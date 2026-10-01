"""Derive SkyyAccessories/build_skyyaccessories_0.5.1.py from the GENERATED 0.5 script (build_skyyaccessories_0.5.py = the
tools/deploy_set.py SET pin, itself written by tools/acc_0_5_patch.py; same style: rep(old, new) with asserted anchors + KEEP blocks;
the 0.5 script stays untouched - never re-run acc_0_5_patch.py on top of this).
Run:  python tools/acc_0_5_1_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.1.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.1.py   (every 0.5 check + H hidden flags + S the 0.5.1 update + Y compare with 0.5)

0.5.1 = TWO CHANGES (A, B) + the Campfire text the build gate forces (C), nothing else (asserted by the KEEP blocks below):

 A. THE STAMINA LINE. Skyy (verbatim): "id double the amount of stamina the stamina accessory gives you, but half the stamina regen
    boost it gives you." (OPEN-QUESTIONS.md, LOCKED 2026-10-01). Booster table row Endurance / Stamina: max Stamina +3 / +6 / +9 / +12
    (0.5: +1.5 / +3 / +4.5 / +6) and Stamina Regen +2.5 / +5 / +7.5 / +10 % (0.5: +5 / +10 / +15 / +20), Normal..Legendary. Everything
    else follows the table as in 0.5: AccDefs.BOOST + AccCfg.BOOST_DEF (the built-in numbers), the tooltips of the four Stamina items
    and their legacy ids (lang), /accessories lines and the bag page (live config), the Server Setup row defaults (kit DEFAULTS =
    CONFIG_TEXT), the 0.4.x -> 0.5 migration's appended values (ADD_VAL = BOOST_DEF). The page's sample texts (build-time fit checks
    only) say the new Legendary text "+12 max Stamina, +10% Stamina Regen".
    ONE-TIME UPDATE of an existing 0.5 config.properties: AccCfg.migrate051, called from setup() BEFORE AccCfg.load(true) (so before the
    loader, the 0.5 migration and CfgPub.start). The SkyyGear 0.1.1 migrateStat011 machinery, method for method:
      - m51Update = a pure text step on the kit's own parser (CfgFile.isComment / end / key / value / valStart; ISO-8859-1 chars in and
        out, LF or CRLF per line as found, every other byte kept). A boost.Stamina.flat / boost.Stamina.regenPct key whose LAST entry
        (the one java.util.Properties keeps) is a one-line entry holding the 0.5 numbers (compared as 4 numbers like the 0.5 migration's
        sameRow, so "1.5, 3, 4.5, 6" counts) gets the 0.5.1 text on every one-line entry of that key that holds them (value text only:
        key, separator and CR stay). Any other value is KEPT and noted ("boost.Stamina.flat=2,4,6,8 kept (custom) - the 0.5.1 default
        is 3,6,9,12", one INFO line each, also in the ready line); a continued entry is kept and noted; a missing line stays missing
        (the loader's built-in = the 0.5.1 numbers).
      - RUNS ONCE: the marker comment M51_MARK ("# SkyyAccessories 0.5.1 Stamina defaults ...", no '=' so the kit never takes it for a
        template line) is inserted right above the first boost.Stamina entry (else above the first boost. entry - always the start of
        a logical line, so nothing can continue into it and the end-of-file trap of SkyyGear review finding 4 cannot happen). A file
        that carries the marker in any comment line is never touched again, so a value an admin later sets back to the 0.5 numbers
        stays. The 0.5.1 default text carries the marker too (the last comment line of the boost block, ADD_GROUPS / GROUP_NOTE), so a
        fresh file, and a 0.4.x file the 0.5 migration fills with the 0.5.1 numbers, are never updated.
      - A file with NO boost. line at all (a 0.4.x file, or no file) is left alone (m51Update returns an empty array): the 0.5
        migration inside load(true) appends the 0.5.1 numbers together with the marker.
      - Through the config kit's own files (kit 1.1, KEEP 20): m51Kit points CfgRows.HOME / CfgHist / CfgLog at the folder of
        config.properties (CfgPub.start sets the same values again afterwards), CfgHist.snapshot keeps the old file as a History
        version ("before the 0.5.1 Stamina defaults update", restorable in Server Setup -> History), and the update only rewrites the
        file once m51Saved finds a config-history copy holding exactly the old bytes (CfgHist.snapshot swallows its own errors - SkyyGear
        review finding 3) - else WARN, file untouched, the next start tries again. CfgRows.atomicWrite (tmp + fsync + ATOMIC_MOVE,
        retries) writes it; one config-changes.log line per changed entry in the kit's table format
        (time, "SkyyAccessories 0.5.1", -, update, boost[Stamina.flat], 1.5,3,4.5,6, 3,6,9,12, ok) so Server Setup -> Changes offers
        Undo (= the kit's inverse tset with the old value, which checkBoost accepts); one INFO line. Any failure: WARN, file as it was.
 B. OLD IDS OUT OF THE CREATIVE LIBRARY. Skyy (creative, 0.5 live): "this one appears twice in creative" - the library listed the
    Legendary Stamina Accessory twice (Skyy_Talisman_Endurance_Epic and the legacy Skyy_Talisman_Endurance_Artifact). HIDDEN_IDS = the
    20 legacy booster ids (Skyy_Talisman_<Vitality|Endurance|Intelligence|Regeneration|Speed>_<Talisman|Ring|Artifact|Legendary>) + the
    5 retired bench accessories the 0.5 build keeps the same way (asset kept so owned copies load, no recipe, do nothing:
    Skyy_Accessory_Alchemybench_T1..T4, Skyy_Accessory_Cookingbench_T1). Their item JSON gets "Variant": true and loses "Categories";
    nothing else changes (quality, icon, model, name, tooltip, MaxStack), so they still load, render, show their tooltip and convert
    in the bag exactly as in 0.5 (AccDefs / AccStore are untouched). The 67 current items keep "Categories": ["Items.Tools"] and no
    Variant key.
    WHY NOT SkyyVault's quality HideFromSearch: it is a QUALITY flag (ItemQuality.hideFromSearch, "hidden from typical public search,
    like the creative library"), and the legacy ids share the Skyy_Acc_Unique / Rare / Legendary qualities with the current items.
    Hiding them that way needs 4 new hidden twin qualities (the retired benches are Normal..Legendary), which shifts the index of every
    quality loaded after this pack a second time (saved stacks keep their index: Bag-Restructure-Spec 1.4; the 0.5 spec 5.2 shipped six
    qualities at once so the shift happens ONCE) and changes the saved index of every legacy stack. The engine has an ITEM-level flag:
    PROVEN (the build stops if any of it changes):
      - Item codec, HytaleServer.jar constant pool (_variant_proof below): key "Variant" documented "If this item is marked as a
        variant, then we filter it out of the item library menu by default, unless the player chooses to display variants"; key
        "Categories" documented "A list of categories this item will be shown in on the creative library menu".
      - Item.toPacket copies Item.variant to ItemBase.variant and the categories (null when empty) to ItemBase.categories (bytecode);
        B.probe Item.isVariant, ItemBase.variant / categories.
      - Server side nothing else reads them: no invoke of Item.isVariant anywhere in HytaleServer.jar; Item.getCategories only in
        BlockSetLookupTable (blocks) and BlockSpawnerSettingsPage (furniture blocks); no Skyy mod reads either.
      - Vanilla uses the flag on plain items (15, e.g. Ingredient_Life_Essence_Carrot) and blocks (110); items without Categories load
        fine (25 vanilla items, e.g. the spawner eggs).
      - Client (read-only, test harness section H): Item Library has a "Show Variants" toggle (Client/Data/Game/Interface/InGame/Pages/
        Inventory/ItemLibraryPanel.ui #ToggleVariantsButton, client.lang inventory.itemLibrary.options.showVariants).
    So by default the old ids are in no library list or search; with "Show Variants" switched on they are still in no category tab
    (no Categories) - whether a library SEARCH then lists them is client code (UNVERIFIED; vanilla's variant items behave the same).
    Build check (_hidden_checks): the set of items with Variant = HIDDEN_IDS exactly; each hidden id has Variant true, no Categories,
    no Recipe, is a legacy id by the Python id mirror or a retired bench id, and keeps its quality / icon / name; each current id has
    Categories ["Items.Tools"] and no Variant; no recipe takes a hidden id; no quality asset has HideFromSearch (they are shared).

 C. CAMPFIRE ACCESSORY TEXT FOLLOWS SkyyCooking 0.1.3 (forced by 0.4.3's build gate, not a separate design change): Skyy LOCKED
    2026-10-01 "Campfire cooking (in /crafting) pays half the Cooking XP it did - Campfire XP share 0.5 -> 0.25" and the parallel
    SkyyCooking 0.1.3 build (tools/cooking_0_1_3_patch.py: CAMP_XP_DEF 0.25; its notes say "SkyyAccessories ... its next build must set
    CAMP_XP_PCT 50 -> 25"). _camp_defaults_check (0.4.3, unchanged) reads the NEWEST SkyyCooking build script and stops this build when
    the Campfire Accessory item text differs, so CAMP_XP_PCT 50 -> 25: the item text says "25% Cooking XP and 75% of your cooking bonus
    by default" and AccStore.CAMP_XP_TEXT (the campCheck warning baseline) is 0.25. Deploy SkyyCooking 0.1.3 together with this jar: with
    the live SkyyCooking 0.1.2 (0.5 share) the item text says 25%, AccStore.campCheck logs one warning and the bag page shows the live
    share (as 0.4.3 designed for any difference).

Also: VERSION 0.5.1 (jar name, manifest, kit header, ready line); the ready line says the old ids are hidden from the creative library.
Unchanged on purpose: qualities and the restamp, AccDefs id rules, the bag, the page, commands, bridges, the notice, the 0.5 migration
code (only its appended values / note text follow the table), gear:extra, movement, every other number.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.1.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


def block(a, b):
    """the text from anchor a (included) to anchor b (excluded) of the CURRENT source (for unchanged-block asserts)"""
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


assert 'VERSION = "0.5"\n' in s and "def migrate051" not in s and "HIDDEN_IDS" not in s, "the source must be the generated 0.5 script"
REG0 = s.count("registerCommand(")
# blocks that come out of this patch byte-identical (0.5's code the two changes do not touch)
KEEP = [block('JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"', "# 0.5: the Stamina Regen top-up (research/Booster-Accessories-Spec.md"),
        block('PKG = "com.skyy.accessories"', "# 0.4.3 Campfire accessory description (Skyy's call, orchestrator wording)."),
        block("CAMPFIRE_DESC = (", "assert CAMPFIRE_DESC.startswith("),
        block("def _camp_defaults_check():", "# ---- BOOSTER TABLE START"),
        block("# ================= AccDefs =================", "# ================= the admin config kit (0.4.4;"),
        block("# ================= 0.5 part 2: AccGear", "# ---- ACC PAGE BLOCK START"),
        block("# ---- ACC PAGE BLOCK END", "# ================= plugin ================="),
        block("def item(iid, icon, quality, recipe_in, bench_req, page_id=None, visual=None):", "FIELD_REQ = [{"),
        block("def _booster_asset_checks():", "\n\n_booster_asset_checks()\n"),
        block("def _player_literals_check():", "jar = os.path.join(HERE, \"SkyyAccessories-%s.jar\" % VERSION)")]

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyAccessories 0.5 - build script (derived from 0.4.5 by tools/acc_0_5_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.py            -> SkyyAccessories/SkyyAccessories-0.5.jar
       python build_skyyaccessories_0.5.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.py             (bare JVM -Xverify:all, table, fold, config migration on a scratch copy, paging)
0.5: BOOSTER ACCESSORIES''', '''"""SkyyAccessories 0.5.1 - build script (derived from the generated build_skyyaccessories_0.5.py by tools/acc_0_5_1_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.1.py            -> SkyyAccessories/SkyyAccessories-0.5.1.jar
       python build_skyyaccessories_0.5.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.1.py             (bare JVM -Xverify:all: every 0.5 check + the hidden flags + the 0.5.1 update)
0.5.1: TWO CHANGES (full notes, engine proof and the hidden id list in tools/acc_0_5_1_patch.py):
     - THE STAMINA LINE (Skyy: "double the amount of stamina the stamina accessory gives you, but half the stamina regen boost it
       gives you"; OPEN-QUESTIONS LOCKED 2026-10-01): max Stamina +3 / +6 / +9 / +12 (was +1.5 / +3 / +4.5 / +6) and Stamina Regen
       +2.5 / +5 / +7.5 / +10 % (was +5 / +10 / +15 / +20), Normal..Legendary; tooltips, /accessories lines, the bag page and the
       Server Setup defaults follow the booster table. ONE-TIME UPDATE of a 0.5 config.properties (AccCfg.migrate051, setup() before
       the loader and CfgPub.start; the SkyyGear 0.1.1 migrateStat011 pattern): a boost.Stamina.flat / boost.Stamina.regenPct line that
       still holds the 0.5 numbers gets the 0.5.1 numbers, any other value is kept (INFO line); the old file is first kept as a
       History version (verified before the rewrite - else WARN, untouched, retried next start), one config-changes.log line per
       changed entry (Server Setup -> Changes can undo it); the marker comment "SkyyAccessories 0.5.1 Stamina defaults" makes it
       run once (the 0.5.1 default text carries it).
     - OLD IDS OUT OF THE CREATIVE LIBRARY (Skyy: "this one appears twice in creative"): the 20 legacy booster ids (_Talisman, _Ring,
       _Artifact, the old _Legendary) and the 5 retired bench accessories get "Variant": true and no "Categories" (the engine's item
       library filter, documented in the Item codec - proven at build time); they still load, look, show their tooltip and convert
       as in 0.5. The current items stay listed. No new quality (SkyyVault's HideFromSearch is a quality flag: it would need hidden
       twin qualities and shift every quality index once more).
     - (forced by the 0.4.3 build gate) the Campfire Accessory item text follows SkyyCooking 0.1.3 (Skyy, LOCKED 2026-10-01: campfire
       cooking pays half the Cooking XP): "25% Cooking XP and 75% of your cooking bonus by default" (was 50%); deploy with SkyyCooking 0.1.3.
0.5 notes:
0.5: BOOSTER ACCESSORIES''')
rep('VERSION = "0.5"\n', 'VERSION = "0.5.1"\n')

# ---------------------------------------------------------------------------------------------------------------- A. the Stamina line
rep('''     [("flat", "maxStamina", [1.5, 3, 4.5, 6]), ("regenPct", "staminaRegen", [5, 10, 15, 20])], SRC_FOLDED,''',
    '''     [("flat", "maxStamina", [3, 6, 9, 12]), ("regenPct", "staminaRegen", [2.5, 5, 7.5, 10])], SRC_FOLDED,   # 0.5.1: Skyy''')
rep('''assert BOOST_DEF == ["6,12,18,24", "1.5,3,4.5,6", "5,10,15,20", "6,12,18,24",''',
    '''assert BOOST_DEF == ["6,12,18,24", "3,6,9,12", "2.5,5,7.5,10", "6,12,18,24",''')
# the one-time update's data, before ADD_GROUPS (its marker is the last comment line of the boost block)
rep('''ADD_GROUPS = [
''', '''# 0.5.1 STAMINA (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01: double the max Stamina, half the Stamina Regen). AccCfg.migrate051 rewrites a
# boost.Stamina.flat / boost.Stamina.regenPct line that still holds these 0.5 numbers (the SkyyGear 0.1.1 migrateStat011 rules)
M51_OLD = [("Stamina.flat", "1.5,3,4.5,6"), ("Stamina.regenPct", "5,10,15,20")]
M51_KEYS = [_k for _k, _o in M51_OLD]
M51_NEW = [BOOST_DEF[E[_k]] for _k in M51_KEYS]
assert M51_NEW == ["3,6,9,12", "2.5,5,7.5,10"] and all(_k in E for _k in M51_KEYS), M51_NEW
# the marker (in the 0.5.1 default text and in every updated file): a doc comment with spaces and no '=', so the kit never takes it for
# a "#key=value" template line; migrate051 looks for M51_MARK_ID in comment lines only
M51_MARK_ID = "SkyyAccessories 0.5.1 Stamina defaults"
M51_MARK = ("# %s (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01): max Stamina doubled to 3,6,9,12 and Stamina Regen halved "
            "to 2.5,5,7.5,10 (0.5: 1.5,3,4.5,6 and 5,10,15,20)." % M51_MARK_ID)
# the name on the update's config-changes.log lines and its History version: a fixed literal (SkyyGear 0.1.1 review finding 5)
M51_WHO = "SkyyAccessories 0.5.1"
assert all(32 <= ord(_c) < 127 for _c in M51_MARK) and "=" not in M51_MARK and M51_MARK.startswith("# ")
ADD_GROUPS = [
''')
rep('''      "# the Accessory Bag page and /accessories lines show the ones below."],''',
    '''      "# the Accessory Bag page and /accessories lines show the ones below.", M51_MARK],''')
# the page's sample texts (build-time checks only): the new Legendary Stamina text
rep('"+6 max Stamina, +20% Stamina Regen"', '"+12 max Stamina, +10% Stamina Regen"', count=2)

# AccCfg.migrate051 + helpers: compiled AFTER the kit (they call CfgFile / CfgHist / CfgLog / CfgRows), called from setup()
M51_JAVA = r'''
# ================= 0.5.1: the one-time Stamina defaults update (AccCfg.migrate051; the SkyyGear 0.1.1 migrateStat011 pattern) =================
# compiled after CFG.emit: it uses the kit's own parser (CfgFile), History (CfgHist), change log (CfgLog) and atomic write (CfgRows)
cfg_.addField(CtField.make("public static final String[] M51_KEY = new String[] { %s };" % jstrs(M51_KEYS), cfg_))
cfg_.addField(CtField.make("public static final String[] M51_OLD = new String[] { %s };" % jstrs(_o for _k, _o in M51_OLD), cfg_))
cfg_.addField(CtField.make("public static final String[] M51_NEW = new String[] { %s };" % jstrs(M51_NEW), cfg_))
cfg_.addField(CtField.make("public static final String M51_MARK = %s;" % jlit(M51_MARK), cfg_))
cfg_.addField(CtField.make("public static final String M51_MARK_ID = %s;" % jlit(M51_MARK_ID), cfg_))
cfg_.addField(CtField.make("public static final String M51_WHO = %s;" % jlit(M51_WHO), cfg_))
for _src in [
# a key exactly as java.util.Properties / the loader read it (case-sensitive) -> the M51_KEY index, -1 = none
r"""
public static int m51Idx(String k) {
  if (k == null || !k.startsWith("boost.")) return -1;
  for (int i = 0; i < M51_KEY.length; i++) if (("boost." + M51_KEY[i]).equals(k)) return i;
  return -1;
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile.key / value / end). null = the 0.5.1 marker
# is already in a comment line (nothing to do); an empty array = no boost. line at all (a 0.4.x file: the 0.5 migration appends the
# 0.5.1 numbers with the marker). Else { new text, "boost.Stamina.flat 1.5,3,4.5,6 -> 3,6,9,12, ...", String[] kept notes,
# String[] { entry, old, new }* }. A key whose LAST live entry (the one Properties keeps) is a one-line entry holding the 0.5 numbers
# (as 4 numbers) is updated: every one-line entry of it that holds them gets the 0.5.1 text (value text only: key, separator and CR
# stay). Anything else is kept: a custom value (noted unless it already is the 0.5.1 default), a continued entry (noted), a missing
# line (silent). The marker goes on its own line right above the first boost.Stamina entry, else above the first boost. entry - the
# start of a logical line, so nothing continues into it. Every line is scanned from the start of a logical line.
r"""
public static Object[] m51Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = M51_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int firstStam = -1;
  int firstBoost = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M51_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    if (firstBoost < 0 && key != null && key.startsWith("boost.")) firstBoost = k;
    int m = m51Idx(key);
    if (m >= 0) {
      if (firstStam < 0) firstStam = k;
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    k = e + 1;
  }
  if (firstBoost < 0) return new Object[0];
  int at = firstStam >= 0 ? firstStam : firstBoost;
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && sameRow(parseN(eff[i], 4), parseN(M51_OLD[i], 4))) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append("boost.").append(M51_KEY[i]).append(' ').append(oneLine(eff[i])).append(" -> ").append(M51_NEW[i]);
      rows.add(M51_KEY[i]);
      rows.add(eff[i]);
      rows.add(M51_NEW[i]);
    } else if (multi[i] || !sameRow(parseN(eff[i], 4), parseN(M51_NEW[i], 4))) {
      kept.add("boost." + M51_KEY[i] + "=" + oneLine(eff[i]) + " kept (custom) - the 0.5.1 default is " + M51_NEW[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == at) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M51_MARK + (crm ? "\r" : ""));
    }
    int m2 = m51Idx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && sameRow(parseN(@PKG@.CfgFile.value(l, k).trim(), 4), parseN(M51_OLD[m2], 4))) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M51_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M51_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""",
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): History + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyyAccessories)
r"""
public static void m51Kit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.AccStore.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""",
# CfgHist.snapshot swallows its own errors, so the update checks that config-history really holds a copy with exactly these bytes (the
# new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log (SkyyGear review finding 3)
r"""
public static boolean m51Saved(byte[] old) {
  String[] have = @PKG@.CfgHist.list(0);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(0, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""",
# one config-changes.log line in the kit's table format (CfgLog.add without its per-line INFO): time, name, uuid, via, key, old, new,
# status - the key is the table row key + [entry], so Server Setup -> Changes undoes it with a tset back to the old value
r"""
public static String m51Log(String e, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M51_WHO + "\t-\tupdate\tboost[" + @PKG@.CfgRows.oneLine(e) + "]\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""",
# setup(), BEFORE load(true) (the loader, the 0.5 migration) and CfgPub.start: the file before this update becomes a History version
# (KEEP 20, verified by m51Saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one
# change-log line per updated entry, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by "; " ("" = nothing
# done: no file, no boost. line yet, marker already there, or a failure - WARN, file untouched, the next start tries again)
r"""
public static synchronized String migrate051() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m51Update(new String(old, "ISO-8859-1"));
    if (r == null || r.length == 0) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m51Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M51_WHO, "before the 0.5.1 Stamina defaults update");
    if (!m51Saved(old)) {
      @PKG@.AccStore.warn("config.properties NOT updated to the 0.5.1 Stamina defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(m51Log(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.5.1 Stamina defaults: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no Stamina line still had its 0.5 numbers - nothing changed (0.5.1 Stamina marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append("; ").append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to the 0.5.1 Stamina defaults (the file is used as it is): " + t);
    return "";
  }
}""",
]:
    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))
'''
rep('''               DEFAULTS={"config.properties": CONFIG_TEXT})

# ================= 0.5 part 2: AccGear''', '''               DEFAULTS={"config.properties": CONFIG_TEXT})
''' + M51_JAVA + '''
# ================= 0.5 part 2: AccGear''')
rep('''  String cs = @PKG@.AccCfg.load(true);   // 0.5: a first start writes the 0.5 file; an existing 0.4.x file is updated ONCE (before CfgPub.start)
''', '''  String m51 = @PKG@.AccCfg.migrate051();   // 0.5.1: a 0.5 file gets the Stamina numbers ONCE (History copy first), before the loader
  String cs = @PKG@.AccCfg.load(true);   // 0.5: a first start writes the 0.5 file; an existing 0.4.x file is updated ONCE (before CfgPub.start)
  if (m51.length() > 0) cs = cs + "; " + m51;
''')
rep('''(%d items + %d old ids; combat stats to SkyyGear "''', '''(%d items + %d old ids, hidden from the creative library; combat stats to SkyyGear "''')

# ---------------------------------------------------------------------------------------------------------------- C. campfire text
# 0.4.3's _camp_defaults_check reads the newest SkyyCooking build script: 0.1.3 (Skyy LOCKED 2026-10-01) sets CAMP_XP_DEF 0.25
rep('CAMP_XP_PCT, CAMP_BUFF_PCT = 50, 75\n',
    'CAMP_XP_PCT, CAMP_BUFF_PCT = 25, 75   # 0.5.1: SkyyCooking 0.1.3 halves the campfire XP share (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01)\n')
rep('assert CAMPFIRE_DESC.startswith("Quick inventory cooking: campfire dishes in /craft at 50% Cooking XP and 75% of your cooking bonus by '
    'default"), CAMPFIRE_DESC',
    'assert CAMPFIRE_DESC.startswith("Quick inventory cooking: campfire dishes in /craft at 25% Cooking XP and 75% of your cooking bonus by '
    'default"), CAMPFIRE_DESC')

# ---------------------------------------------------------------------------------------------------------------- B. hidden old ids
# engine proof at build time, next to 0.5's probes (the build stops when Hytale changes the flag, its packet field or its meaning)
rep('''             (ACM, "setAllowsExtraArguments"), (CTX, "getInputString"), (MSG, "raw"), (MSG, "color")):
    B.probe(pool, c, m)
''', '''             (ACM, "setAllowsExtraArguments"), (CTX, "getInputString"), (MSG, "raw"), (MSG, "color")):
    B.probe(pool, c, m)
# 0.5.1: old ids out of the creative library - the ITEM flag Variant (tools/acc_0_5_1_patch.py B): the asset field, its packet field and
# the categories packet field exist, and the Item codec's own documentation still says what the flags do in the item library
IBASE = "com.hypixel.hytale.protocol.ItemBase"
for c, m in ((ITM, "isVariant"), (ITM, "getCategories"), (IBASE, "variant"), (IBASE, "categories")):
    B.probe(pool, c, m)


def _variant_proof():
    import zipfile as _zf
    cls = _zf.ZipFile(B.SERVER_JAR).read("com/hypixel/hytale/server/core/asset/type/item/config/Item.class")
    for needle in (b"Variant", b"Categories",
                   b"If this item is marked as a variant, then we filter it out of the item library menu by default, unless the player "
                   b"chooses to display variants.",
                   b"A list of categories this item will be shown in on the creative library menu."):
        if needle not in cls:
            raise SystemExit("0.5.1: the Item codec no longer says %r - check how old ids are hidden from the creative library" % needle[:60])
    print("creative library: the Item codec documents Variant (filtered out of the item library by default) and Categories")


_variant_proof()
''')
# the hidden ids + the one helper that hides an item (only the two flags change; everything else of the item stays 0.5's)
rep('''files = {}
lang = []
''', '''# 0.5.1: OLD IDS OUT OF THE CREATIVE LIBRARY (Skyy: "this one appears twice in creative"). The legacy booster ids and the retired bench
# accessories stay real items (owned copies load, render, show their tooltip and convert in the bag as before) but get the engine's
# item library filter: "Variant": true (filtered out of the library by default) and no "Categories" (no library tab even with the
# library's Show Variants toggle on). The current items keep Categories ["Items.Tools"] and no Variant (_hidden_checks below).
RETIRED_IDS = ["Skyy_Accessory_%s_T%d" % (_b[0], _t) for _b in BENCHES if _b[0] in RETIRED for _t in range(1, _b[3] + 1)]
HIDDEN_IDS = LEGACY_IDS + RETIRED_IDS
assert len(LEGACY_IDS) == 20 and len(RETIRED_IDS) == 5 and len(set(HIDDEN_IDS)) == 25, (len(LEGACY_IDS), RETIRED_IDS)
assert all(py_legacy(_i) for _i in LEGACY_IDS) and not set(HIDDEN_IDS) & set(LINE_IDS)


def hide_item(iid, node):
    """0.5.1: keep an old id out of the creative item library (the Item codec's Variant + Categories, proven by _variant_proof)"""
    assert iid in HIDDEN_IDS, "0.5.1: only the old ids are hidden: " + iid
    del node["Categories"]
    node["Variant"] = True
    return node


files = {}
lang = []
''')
rep('''        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)
            del node["Recipe"]
''', '''        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)
            del node["Recipe"]
            hide_item(iid, node)  # 0.5.1: not in the creative library
''')
rep('''        node = item(iid, icons[lt], QUAL_IDS[lt], [], WB_REQ, visual=vis)
        del node["Recipe"]
''', '''        node = item(iid, icons[lt], QUAL_IDS[lt], [], WB_REQ, visual=vis)
        del node["Recipe"]
        hide_item(iid, node)      # 0.5.1: not in the creative library (Skyy saw the old Artifact next to the Legendary)
''')
rep('''

_booster_asset_checks()
''', '''

_booster_asset_checks()


def _hidden_checks():
    """0.5.1 build check: exactly the old ids are hidden from the creative library, every current id stays listed"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    lt = files["Server/Languages/en-US/server.lang"]
    lmap = dict(l.split("=", 1) for l in lt.split("\\n") if "=" in l)
    hidden = sorted(i for i, n in items.items() if "Variant" in n)
    assert hidden == sorted(HIDDEN_IDS), "0.5.1: the hidden items differ from HIDDEN_IDS: %s" % sorted(set(hidden) ^ set(HIDDEN_IDS))
    for iid in HIDDEN_IDS:
        n = items[iid]
        assert n["Variant"] is True and "Categories" not in n and "Recipe" not in n, "0.5.1: %s is not hidden right: %r" % (iid, n)
        assert py_legacy(iid) or iid in RETIRED_IDS, iid
        assert n["Quality"] in quals and n["MaxStack"] == 1 and n.get("Icon") and lmap.get("server.items.%s.name" % iid) and \\
            lmap.get("server.items.%s.description" % iid), "0.5.1: %s lost its look or text" % iid
        if py_legacy(iid):   # it still looks and reads like the rarity it counts as (0.5's rule, re-checked on the hidden item)
            cur = items[py_modern(iid)]
            assert n["Quality"] == cur["Quality"] and n["Icon"] == cur["Icon"] and n["Model"] == cur["Model"], iid
            assert lmap["server.items.%s.name" % iid] == lmap["server.items.%s.name" % py_modern(iid)], iid
    current = sorted(i for i in items if i not in HIDDEN_IDS)
    want = set(LINE_IDS) | set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in ACTIVE for t in range(1, b[3] + 1)) | {OMNI, BAG}
    assert set(current) == want, "0.5.1: current items differ: %s" % sorted(set(current) ^ want)
    for iid in current:
        assert "Variant" not in items[iid] and items[iid].get("Categories") == ["Items.Tools"], "0.5.1: %s must stay listed" % iid
    for iid, n in items.items():
        for inp in (n.get("Recipe") or {}).get("Input", []):
            assert inp.get("ItemId") not in HIDDEN_IDS, "0.5.1: %s takes the hidden %s" % (iid, inp.get("ItemId"))
    assert not any(q.get("HideFromSearch") for q in quals.values()), "0.5.1: a quality hides items (the qualities are shared)"
    print("creative library: %d old ids hidden (Variant true, no Categories: %d legacy booster ids + %d retired bench accessories), "
          "%d current ids listed" % (len(HIDDEN_IDS), len(LEGACY_IDS), len(RETIRED_IDS), len(current)))


_hidden_checks()
''')

# ---------------------------------------------------------------------------------------------------------------- final checks
for _k in KEEP:
    assert _k in s, "a block that must stay 0.5's changed: " + _k[:100]
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert s.count("registerSystem(") == 1, "one registerSystem per class (AccEffects only)"
# javassist: methods before their callers; the update's methods after the kit (CfgFile / CfgHist / CfgLog / CfgRows), before setup()
for _a, _b in (("kit = CFG.emit(pool, PKG,", "public static int m51Idx(String k)"),
               ("public static double[] parseN(String v, int n)", "public static Object[] m51Update(String text)"),
               ("public static boolean sameRow(double[] a, double[] b)", "public static Object[] m51Update(String text)"),
               ("public static String oneLine(String t)", "public static Object[] m51Update(String text)"),
               ("public static void info(String msg)", "public static synchronized String migrate051()"),
               ("public static int m51Idx(String k)", "public static Object[] m51Update(String text)"),
               ("public static Object[] m51Update(String text)", "public static synchronized String migrate051()"),
               ("public static void m51Kit(java.nio.file.Path home)", "public static synchronized String migrate051()"),
               ("public static boolean m51Saved(byte[] old)", "public static synchronized String migrate051()"),
               ("public static String m51Log(String e, String o, String n)", "public static synchronized String migrate051()"),
               ("public static synchronized String migrate051()", "public void setup() {"),
               ("String m51 = @PKG@.AccCfg.migrate051();", "String cs = @PKG@.AccCfg.load(true);"),
               ("String cs = @PKG@.AccCfg.load(true);", "@PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());"),
               ("def hide_item(iid, node):", "hide_item(iid, node)  # 0.5.1: not in the creative library\n"),
               ("_booster_asset_checks()\n\n\ndef _hidden_checks():", "_player_literals_check()\n")):
    _ia, _ib = s.find(_a), s.find(_b)
    assert 0 <= _ia < _ib, "order: %s must come before %s" % (_a[:50], _b[:50])
assert s.count("hide_item(iid, node)") == 3 and s.count("def hide_item(") == 1 and s.count("M51_MARK]") == 1
assert 'VERSION = "0.5.1"' in s and "@@" not in s
assert "Endurance" not in M51_JAVA and "Talisman" not in M51_JAVA and "talisman" not in M51_JAVA.lower()
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.5
print("wrote", dst, "(%d lines; 0.5 had %d)" % (s.count(LF), OLD.count(LF)))
