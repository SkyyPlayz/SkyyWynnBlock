"""Derive SkyyMenu/build_skyymenu_0.3.67.py + SkyyMenu/test_skyymenu_0.3.67.py from the SET pin SkyyMenu 0.3.66 (generated - never re-run
its patch). Run:  python tools/menu_0_3_67_patch.py   then   python SkyyMenu/build_skyymenu_0.3.67.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.67.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Pairs with SkyyWardrobe 0.2.16 (tools/wardrobe_0_2_16_patch.py: requip:fn:act cands / pick / pet).

0.3.67 (2026-11-23, round req2) = THE REQUIP SLOT PICKER + AUTO BEST GEAR. Skyy's words (docs/answered/ui.md 2026-11-22, LOCKED 'REQUIP SLOT
PICKER', 'REQUIP PICKER FILTER + AUTO-BEST', 'REQUIP EMPTY HAND'): "clicking a box in the requip should pull up something to select what goes
there. if you click helmet slot, ot shows all your helmets and so on." / "filtered to whatever type it is, so in mine, but ones like mine should
auto add the best mining gear you have." / "i dont see a way to set thew hand to empty"; 2026-11-23 "looks better. go head and build everything
on your list."
  1. THE PICKER (panel 'k', drawn in the inventory's top panel like Requip storage 'q' - no old page): clicking ANY preset slot (Head / Chest /
     Hands / Legs, pet, mount, every hotbar slot) lists what you own that fits it (SkyyWardrobe 0.2.16 cands: on you - armour, hotbar, bag,
     backpack - + Requip storage; your owned pets for pet / mount), 12 x 3 a page, best first (tier, then rarity, then gear level, then name),
     the rarity colour on the slot + title (the 0.3.66 slot(): stacks on you keep their coloured tooltip; stored items / pets: their quality /
     rarity colour; Server Setup menu.inventory.rarity off = plain). Skill presets list only that skill's gear (Combat = combat armour / weapons,
     Mining = the Mining armour sets (Armor_Mining_*, the vanilla metal sets, Bronze) + pickaxes / multitools, Farming = Farming armour + hoes /
     sickles / watering cans, Foraging = Foraging armour + hatchets / multitools, Fishing = Angler armour + rods); "Show <skill>" toggles to
     "Show all" (everything that fits - food, torches ...). Custom presets list everything that fits. A preset's skill = a skill word in its
     name (mine / mining / pick, farm, forag / chop / wood / lumber, fish, combat / fight / pvp), else Requip's unnamed 1-5 order (Combat,
     Mining, Farming, Foraging, Fishing), else custom.
     Click = that item goes in the slot: an item in Requip storage or a stamped item on you = Requip's pick (nothing moves); a plain item on you
     = the SAME call as dragging it onto the slot (Requip's own deposit + pick: it waits in Requip storage until Equip). Pets: Requip's pet
     pick. Every click re-checks: the profile it was drawn for, the preset, the item still in that place (else "moved - nothing changed"), a
     double click within 1.5 s = once. No item is moved by this page itself.
  2. EMPTY + KEEP on top of every list: Empty = Requip's "x" pick (on Equip whatever sits there goes into Requip storage, or a free bag slot
     when Requip refuses it, or stays when there is no room - SkyyWardrobe planEquip, never lost); pet / mount Empty = none. Keep = the old
     Keep (whatever you wear stays). Both mark the slot "set by you".
  3. AUTO BEST GEAR (skill presets): the Requip header's "Auto On / Off" (ON by default) and each slot list's "Auto best". The auto slots
     = the 4 armour slots + one hotbar slot per tool kind (Hotbar 1 = the pickaxe / hatchet / rod / weapon; Farming: Hotbar 1 hoe, 2 sickle,
     3 watering can). An auto slot shows (preview, "auto" under it) the best owned item of the preset's skill; EQUIP (the presets row or the
     panel's Equip) first sets each auto slot to that item through the same Requip calls as a click, then equips. Opening the panel never
     moves anything. A slot you set by hand (a click, Empty, Keep, Keep slot, a drag, Save what I wear, the old /requip page) shows "by you"
     and stays; its list's "Auto best" gives it back (and sets the best at once). Auto Off -> On = every armour / tool slot back on Auto.
     First sight of a preset (FIX after the critics, PROJECT-RULES 4 - only what still holds the old default changes): EVERY pick you
     already saved (that skill's gear too, Empty, a block) counts as set by you and is never replaced; only the slots still on the default
     Keep become Auto's (the server log names them; nothing changes before Equip). Auto Off -> On or a slot's "Auto best" hands a saved
     pick to Auto. A hotbar slot set by you that holds a tool kind = that kind is not placed again. Auto never takes an item another slot
     of the preset already holds. If Requip refuses the Equip after Auto took gear from your bag, the caption says it waits in Requip
     storage. The lists ask SkyyWardrobe for the skill's id prefixes (counted before its 240-row cap; a cut list is said on the picker).
     rqauto values are escaped (backslash-u) so any item id survives a restart.
     Saved: Skyy_SkyyMenu/rqauto/<profile storage key>.properties (NEW file per profile, written only on a change: p.<n>.auto / .hand (slot
     bits) / .seen / .last.<slot> = the item Auto put there; "x" = an Empty Auto reset). No existing file is rewritten (no migration).
  4. The panel's hint row says how (click a slot; Auto fills the 'auto' slots on Equip).
No new command, system, picture or lang key; no new class (InvState / InvPage / InvData members). Needs SkyyWardrobe 0.2.16 for the lists /
Empty / pets / Auto; with 0.2.15 the picker says so (drag + Keep slot + Save what I wear work as 0.3.66) and Auto does nothing.
ROLLBACK to 0.3.66: safe alone (the rqauto files are ignored; every pick made is a normal Requip pick).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.66.py"), os.path.join(MOD, "build_skyymenu_0.3.67.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.66.py"), os.path.join(MOD, "test_skyymenu_0.3.67.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.66"\n') and P.has("benchRow") and not P.has("public void fillPick("), "not the generated SkyyMenu 0.3.66 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.66: SKYY'S 11-22 INVENTORY FIXES''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.67: THE REQUIP SLOT PICKER + AUTO BEST GEAR: clicking a preset slot lists what you own that fits (filtered to the preset's skill, best
       first, rarity colours), Empty / Keep / Auto on top; skill presets fill their armour + tool slots with your best gear of that skill on
       Equip, slots you set by hand stay (notes: tools/menu_0_3_67_patch.py; SkyyWardrobe 0.2.16). CHECKED: SkyyMenu/test_skyymenu_0.3.67.py.
0.3.66: SKYY'S 11-22 INVENTORY FIXES''')
P.rep('VERSION = "0.3.66"\n', 'VERSION = "0.3.67"\n')

# ---------- the picker panel 'k' + sizes + texts
P.rep('''             "f": (SUI.Appends(), [])}   # 0.3.56: + 'f' Furnace / Tanning''',
      '''             "f": (SUI.Appends(), []),   # 0.3.56: + 'f' Furnace / Tanning
             "k": (SUI.Appends(), [])}   # 0.3.67: + 'k' the Requip slot picker''')
P.rep('''IV_RS, IV_RSN, IV_QC, IV_QR, IV_PGC, IV_PGR, IV_RLMAX = 44, 7, 12, 4, 9, 4, 7
''', '''IV_RS, IV_RSN, IV_QC, IV_QR, IV_PGC, IV_PGR, IV_RLMAX = 44, 7, 12, 4, 9, 4, 7
IV_KC, IV_KR, IV_KTW, IV_AUW = 12, 3, 300, 76   # 0.3.67: the slot picker grid, its title width; the Requip header's Auto button
# 0.3.67: the preset skills (Requip's unnamed 1-5 order), the words in a preset name that pick one, the tool kinds (';') of each (prefixes ','),
# the vanilla metal armour sets that are the Mining sets (SkyyGear MINE_IDS + the T3 Bronze set; the zone sets are Armor_Mining_*)
IV_TYN = ["Combat", "Mining", "Farming", "Foraging", "Fishing"]
IV_TYKEY = ["combat,fight,pvp", "mine,mining,pick", "farm", "forag,chop,wood,lumber", "fish"]
IV_TYTOOL = ["Weapon_", "Tool_Pickaxe_,Tool_Hatchet_Pickaxe_Multitool_", "Tool_Hoe_;Tool_Sickle_;Tool_WaterCan_", "Tool_Hatchet_", "SkyyFishing_Rod_"]
IV_MINE_ARM = sorted("Armor_%s_%s" % (_m, _s) for _m in ("Copper", "Iron", "Bronze", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
                     for _s in ("Head", "Chest", "Hands", "Legs"))
assert all(len(_t.split(";")) <= 9 for _t in IV_TYTOOL) and len(IV_TYN) == len(IV_TYKEY) == len(IV_TYTOOL) == 5, "0.3.67: the skill tables"
# fix (req2 critics): the id prefixes each skill's armour list is cut to BEFORE SkyyWardrobe's 240-row cap ("" = no filter: Combat armour
# = everything that is no skill's armour); the hotbar lists use IV_TYTOOL (Combat: Weapon_)
IV_TYPRE = ["", ",".join(["Armor_Mining_"] + IV_MINE_ARM), "Armor_Farming_", "Armor_Foraging_", "Armor_Fishing_"]
assert all(len(_t) < 4000 for _t in IV_TYPRE + IV_TYTOOL), "0.3.67: the cands filters fit SkyyWardrobe's 4000-char limit"
''')
P.rep('''    "rqHelp": "Drag gear from your bag onto a slot to save it into this preset.",''',
      '''    "rqHelp": "Click a slot to choose what goes in it, or drag gear from your bag onto it.",   # 0.3.67: the slot picker
    "rqAuto": "Auto puts your best {T} gear in the 'auto' slots on Equip. Click a slot to choose.",   # 0.3.67
    "rqNoAuto": "Auto is for skill presets (Combat, Mining, Farming, Foraging, Fishing)",
    "kHelp": "Click an item to put it in this slot. Empty = take it off on Equip, Keep = leave what you wear.",
    "kOld": "This list needs SkyyWardrobe 0.2.16 - drag an item onto the slot instead",
    "kNoAuto": "Auto works on the armour and tool slots of skill presets",
    "kMore": "Only the first 240 fit this list",   # fix (req2 critics): SkyyWardrobe cut the list''')
# the Requip header: + the Auto button (the title 30 px narrower)
P.rep('''    tw = 280
    ap.append(("#" + ra, lab(IV + "RqT", "", 16, "accentHi", bold=True, w=tw, h=34)))
    sp = pw - tw - 110 - 6 - 170 - 6 - 80
    assert sp >= 0, ("0.3.53: the Requip header fits", sp)
    ap.append(("#" + ra, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + ra, G_.glass_button(IV + "RqEq", "Equip", "primary", w=110, h=32, size=14)))''',
      '''    tw = 250   # 0.3.67: 280 -> 250 for the Auto button
    ap.append(("#" + ra, lab(IV + "RqT", "", 16, "accentHi", bold=True, w=tw, h=34)))
    sp = pw - tw - IV_AUW - 6 - 110 - 6 - 170 - 6 - 80
    assert sp >= 0, ("0.3.53: the Requip header fits", sp)
    assert SUI.text_width("Auto Off", 13, bold=True) <= IV_AUW - 12 and SUI.text_width("REQUIP - FORAGING  (WORN)", 16, bold=True) <= tw, "0.3.67: the Auto button + title fit"
    ap.append(("#" + ra, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + ra, G_.glass_button(IV + "RqAu", "Auto On", "secondary", w=IV_AUW, h=32, size=13)))
    ap.append(("#" + ra, G_.glass_button(IV + "RqEq", "Equip", "primary", w=110, h=32, size=14, anchor={"left": 6})))''')
P.rep('''    binds.extend([("#" + IV + "RqEq", "rqeq"), ("#" + IV + "RqSv", "rqsv"), ("#" + IV + "RqDn", "rqd"), ("#" + IV + "RqK", "rqk"),''',
      '''    binds.append(("#" + IV + "RqAu", "rqau"))   # 0.3.67: Auto On / Off
    for _t in (IV_TXT["rqAuto"].replace("{T}", "Foraging"), IV_TXT["rqHelp"], IV_TXT["rqNoAuto"]):
        assert SUI.text_width(_t, 12) <= rw, ("0.3.67: a Requip hint fits one line", _t)
    binds.extend([("#" + IV + "RqEq", "rqeq"), ("#" + IV + "RqSv", "rqsv"), ("#" + IV + "RqDn", "rqd"), ("#" + IV + "RqK", "rqk"),''')
P.rep('''    # ======== 'p' ONE POCKET (research/ui-theme-art/inventory-mockup-mining.png)
''', '''    # ======== 'k' 0.3.67 (req2): THE SLOT PICKER - a preset slot's click: what you own that fits it, best first; Empty / Keep / Auto / Show
    ap, binds = IV_PANELS["k"]
    pan = IV + "KPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    ka = IV + "KA"
    ap.append(("#" + pan, G_.glass_group(ka, pw, 34, layout="Left")))
    ap.append(("#" + ka, lab(IV + "KT", "", 16, "accentHi", bold=True, w=IV_KTW, h=34)))
    ap.append(("#" + ka, lab(IV + "KS", "", 13, "text", w=pw - IV_KTW - 6 - 110, h=34)))
    ap.append(("#" + ka, G_.glass_button(IV + "KB", "Done", "primary", w=110, h=32, size=14, anchor={"left": 6})))
    assert SUI.text_width("PICK HOTBAR 9 - FORAGING", 16, bold=True) <= IV_KTW, "0.3.67: the picker title fits"
    kr = IV + "KR"
    ap.append(("#" + pan, G_.glass_group(kr, pw, 32, layout="Left", anchor={"top": 6})))
    ap.append(("#" + kr, G_.glass_button(IV + "KE", "Empty", "secondary", w=96, h=32, size=13)))
    ap.append(("#" + kr, G_.glass_button(IV + "KK", "Keep", "secondary", w=96, h=32, size=13, anchor={"left": 6})))
    ap.append(("#" + kr, G_.glass_button(IV + "KU", "Auto best", "secondary", w=130, h=32, size=13, anchor={"left": 6})))
    ap.append(("#" + kr, G_.glass_button(IV + "KF", "Show all", "secondary", w=150, h=32, size=13, anchor={"left": 6})))
    assert SUI.text_width("Show Foraging", 13, bold=True) <= 150 - 12 and SUI.text_width("Auto best", 13, bold=True) <= 130 - 12, "0.3.67: the picker buttons fit"
    sp = pw - 96 - 6 - 96 - 6 - 130 - 6 - 150 - 32 - 56 - 32
    assert sp >= 0, ("0.3.67: the picker row fits", sp)
    ap.append(("#" + kr, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + kr, G_.glass_button(IV + "KpP", "<", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + kr, lab(IV + "Kn", "", 13, "text", bold=True, w=56, h=32, halign="Center")))
    ap.append(("#" + kr, G_.glass_button(IV + "KpN", ">", "secondary", w=32, h=32, size=14)))
    kgw, kgh = SUI.glass_grid_size(IV_KC, IV_KR, IV_RS)
    assert kgw <= pw and 34 + 6 + 32 + 6 + kgh + 6 + 20 <= ph - 20, ("0.3.67: the picker panel fits", kgw, kgh, ph)
    ap.append(("#" + pan, G_.glass_grid(IV + "Kg", IV_KC, IV_KR, drag=False, slot=IV_RS, icon=IV_RS - 8, anchor={"top": 6, "left": (pw - kgw) // 2})))
    ap.append(("#" + pan, lab(IV + "Ki", "", 12, "text", w=pw, h=20, anchor={"top": 6})))
    for _t in (IV_TXT["kHelp"], IV_TXT["kOld"], IV_TXT["kNoAuto"], "You own no Foraging gear for Hotbar 9 - Show all lists everything that fits", IV_TXT["kMore"] + " - Show Foraging narrows it"):
        assert SUI.text_width(_t, 12) <= pw, ("0.3.67: a picker line fits one line", _t)
    binds.extend([("#" + IV + "KB", "kb"), ("#" + IV + "KE", "ke"), ("#" + IV + "KK", "kk"), ("#" + IV + "KU", "ku"), ("#" + IV + "KF", "kf"),
                  ("#" + IV + "KpP", "kpp"), ("#" + IV + "KpN", "kpn")])
    # ======== 'p' ONE POCKET (research/ui-theme-art/inventory-mockup-mining.png)
''')
P.rep('''for _code, _aps, _bnd in [("-", IV_AP, IV_BINDS)] + [(_c, IV_PANELS[_c][0], IV_PANELS[_c][1]) for _c in ("c", "r", "q", "p", "v", "t", "f", "w")]:   # 0.3.60: + w''',
      '''for _code, _aps, _bnd in [("-", IV_AP, IV_BINDS)] + [(_c, IV_PANELS[_c][0], IV_PANELS[_c][1]) for _c in ("c", "r", "q", "p", "v", "t", "f", "w", "k")]:   # 0.3.60: + w; 0.3.67: + k
    assert _code != "k" or set(["KPan", "Kg", "KT", "KS", "Ki", "Kn", "KE", "KK", "KU", "KF", "KB"]) <= set(i_[len(IV):] for _p, mk_ in _aps for i_ in SUI._static_ids(mk_)), "0.3.67: the picker panel ids"''')
P.rep('''F(idat, "public static final String W_HELP = %s;" % jstr(IV_TXT["wHelp"]))
''', '''F(idat, "public static final String W_HELP = %s;" % jstr(IV_TXT["wHelp"]))
# 0.3.67 (req2): the slot picker + Requip Auto
F(idat, "public static final int KN = %d;" % (IV_KC * IV_KR))
for _n, _v in (("TYN", IV_TYN), ("TYKEY", IV_TYKEY), ("TYTOOL", IV_TYTOOL), ("MINE_ARM", IV_MINE_ARM), ("TYPRE", IV_TYPRE)):
    F(idat, "public static final String[] %s = %s;" % (_n, jarr(_v)))
for _n, _k in (("RQ_AUTO", "rqAuto"), ("RQ_NOAUTO", "rqNoAuto"), ("K_HELP", "kHelp"), ("K_OLD", "kOld"), ("K_NOAUTO", "kNoAuto"), ("K_MORE", "kMore")):
    F(idat, "public static final String %s = %s;" % (_n, jstr(IV_TXT[_k])))
''')

# ---------- InvState: the rqauto file per profile (read once, kept in memory, written on a change; an unreadable file is never written over)
P.rep('''M(ist, r"""
public static boolean tpUnsaved(String pk) { return pk != null && TPDIRTY.containsKey(pk); }""")''', '''M(ist, r"""
public static boolean tpUnsaved(String pk) { return pk != null && TPDIRTY.containsKey(pk); }""")
# 0.3.67 (req2): Requip Auto per profile - Skyy_SkyyMenu/rqauto/<storage key>.properties (p.<n>.auto / .hand / .seen / .last.<slot>)
F(ist, "public static volatile java.nio.file.Path RQDIR;")
F(ist, "public static final java.util.concurrent.ConcurrentHashMap RQA = new java.util.concurrent.ConcurrentHashMap();")
F(ist, "public static final java.util.concurrent.ConcurrentHashMap RQBAD = new java.util.concurrent.ConcurrentHashMap();")
F(ist, "public static volatile int RQSAVES = 0;")
M(ist, r"""
public static java.nio.file.Path rqFile(String pk) {
  if (RQDIR == null || !@PKG@.Given.validKey(pk)) return null;
  return RQDIR.resolve(pk + ".properties");
}""")
M(ist, r"""
public static synchronized java.util.Properties rqProps(String pk) {
  Object o = pk == null ? null : RQA.get(pk);
  if (o != null) return (java.util.Properties) o;
  java.util.Properties p = new java.util.Properties();
  java.nio.file.Path f = rqFile(pk);
  if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
    try { p.load(new java.io.StringReader(new String(java.nio.file.Files.readAllBytes(f), "UTF-8"))); }
    catch (Throwable t) {
      RQBAD.put(pk, Boolean.TRUE);
      @PKG@.MenuUtil.warn("rqauto/" + pk + ".properties could not be read (" + t + ") - Requip Auto uses its defaults for this profile and the file is not written over");
      p = new java.util.Properties();
    }
  }
  if (pk != null) RQA.put(pk, p);
  return p;
}""")
M(ist, r"""
public static synchronized boolean rqSave(String pk) {
  Object o = pk == null ? null : RQA.get(pk);
  java.nio.file.Path f = rqFile(pk);
  if (o == null || f == null || RQBAD.containsKey(pk)) return false;
  java.util.Properties p = (java.util.Properties) o;
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.Iterator it = p.keySet().iterator();
  while (it.hasNext()) { Object k = it.next(); if (k instanceof String && tpKeepable((String) k)) ks.add(k); }
  java.util.Collections.sort(ks);
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyMenu: Requip Auto of one profile (storage key ").append(pk).append("). Change it in game: Tab -> Requip -> Auto, or a slot's list.\\n");
  sb.append("# p.<preset>.auto = 1 on / 0 off; .hand = the slots set by you (bit 0-3 armour, 4-12 hotbar); .last.<slot> = what Auto put there.\\n");
  for (int i = 0; i < ks.size(); i++) {
    String k = (String) ks.get(i);
    String v = p.getProperty(k);
    if (v == null) continue;
    if (v.length() > 512) { @PKG@.MenuUtil.warn("rqauto/" + pk + ".properties " + k + " is " + v.length() + " characters long - not saved (Auto treats that slot as set by you after a restart)"); continue; }
    sb.append(k).append('=');
    // fix (req2 critics): any item id is kept - characters outside [A-Za-z0-9:_.-] are written as a backslash-u hex escape (java.util.Properties reads them back)
    for (int j = 0; j < v.length(); j++) {
      char ch = v.charAt(j);
      if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == ':' || ch == '_' || ch == '-' || ch == '.') sb.append(ch);
      else { String hx = Integer.toHexString((int) ch); sb.append("\\\\u"); for (int z = hx.length(); z < 4; z++) sb.append('0'); sb.append(hx); }
    }
    sb.append('\\n');
  }
  try { @PKG@.MenuUtil.atomicWrite(f, sb.toString().getBytes("UTF-8")); RQSAVES = RQSAVES + 1; return true; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not save rqauto/" + pk + ".properties (kept for this session): " + t); return false; }
}""")''')

# ---------- InvPage: markWord + the helpers (before fillRequip, their first caller)
P.rep('''  if (m.equals("set")) return "set";
  return "keep";''', '''  if (m.equals("set")) return "set";
  if (m.equals("auto")) return "auto";   // 0.3.67: an Auto slot (the best gear Equip puts on)
  return "keep";''')
HELPERS = r'''# ---- 0.3.67 (req2): THE SLOT PICKER + REQUIP AUTO (SkyyWardrobe 0.2.16 requip:fn:act cands / pick / pet; notes: tools/menu_0_3_67_patch.py)
for _f in ("public String[] rlab;", "public int rty;", "public boolean rauto;", "public int kslot;", "public int kpage;", "public boolean kall;",
           "public Object[] kshown;", "public String kkey;", "public int kn;", "public String knote;", "public String kwhy;",
           "public boolean kmore;", "public int adrop;"):   # fix (req2 critics): the list was cut; Auto's deposits before an Equip
    F(ipg, _f)
# a preset's skill: a skill word in its name, else Requip's unnamed 1-5 (Combat, Mining, Farming, Foraging, Fishing), else -1 = custom
M(ipg, r"""
public static int rqType(int n, String name) {
  String nm = name == null ? "" : name.toLowerCase();
  for (int t = 0; t < @PKG@.InvData.TYKEY.length; t++) {
    String[] ks = @PKG@.InvData.TYKEY[t].split(",");
    for (int j = 0; j < ks.length; j++) if (ks[j].length() > 0 && nm.indexOf(ks[j]) >= 0) return t;
  }
  return n >= 0 && n < @PKG@.InvData.TYN.length ? n : -1;
}""")
M(ipg, r"""
public static int armType(String id) {
  if (id == null) return -1;
  if (id.startsWith("Armor_Mining_") || java.util.Arrays.binarySearch(@PKG@.InvData.MINE_ARM, id) >= 0) return 1;
  if (id.startsWith("Armor_Farming_")) return 2;
  if (id.startsWith("Armor_Foraging_")) return 3;
  if (id.startsWith("Armor_Fishing_")) return 4;
  return 0;
}""")
M(ipg, r"""
public static int nfam(int ty) {
  if (ty < 0 || ty >= @PKG@.InvData.TYTOOL.length) return 0;
  return @PKG@.InvData.TYTOOL[ty].split(";").length;
}""")
M(ipg, r"""
public static int famOf(int ty, String id) {
  if (ty < 0 || ty >= @PKG@.InvData.TYTOOL.length || id == null) return -1;
  if (ty == 0 && (id.indexOf("Shield") >= 0 || id.indexOf("Arrow") >= 0)) return -1;
  String[] fs = @PKG@.InvData.TYTOOL[ty].split(";");
  for (int j = 0; j < fs.length; j++) {
    String[] ps = fs[j].split(",");
    for (int i = 0; i < ps.length; i++) if (ps[i].length() > 0 && id.startsWith(ps[i])) return j;
  }
  return -1;
}""")
M(ipg, r"""
public static boolean fitsType(int ty, int k, String id) {
  if (ty < 0) return true;
  if (k < 4) return armType(id) == ty;
  if (ty == 0) return id != null && id.startsWith("Weapon_");
  return famOf(ty, id) >= 0;
}""")
M(ipg, r"""
public static int rarRank(String w) {
  if (w == null) return 0;
  String t = w.trim().toLowerCase();
  if (t.equals("normal") || t.equals("common")) return 1;
  if (t.equals("unique") || t.equals("uncommon")) return 2;
  if (t.equals("rare")) return 3;
  if (t.equals("epic") || t.equals("legendary") || t.equals("set")) return 4;
  if (t.equals("fabled")) return 5;
  if (t.equals("mythic")) return 6;
  return 0;
}""")
# best first: tier, rarity, gear level, name (fixed-width numbers so the text order is the number order)
M(ipg, r"""
public static String rowKey(String[] r) {
  int t = 0;
  try { t = @PKG@.InvCraft.tier(r[2]); } catch (Throwable e) { t = 0; }
  if (t < 0) t = 0;
  if (t > 999) t = 999;
  int lv = toInt(r[5], 0);
  if (lv < 0) lv = 0;
  if (lv > 99999) lv = 99999;
  return String.valueOf(2000 - t) + "." + (9 - rarRank(r[4])) + "." + String.valueOf(200000 - lv) + "." + @PKG@.InvCraft.name(r[2]).toLowerCase() + "." + r[0] + r[1];
}""")
# fix (req2 critics): the id prefixes of skill ty for slot k (SkyyWardrobe cuts the list to them BEFORE its 240-row cap); "" = none
M(ipg, r"""
public static String kPre(int ty, int k) {
  if (ty < 0 || ty >= @PKG@.InvData.TYPRE.length || k >= 13) return "";
  if (k < 4) return @PKG@.InvData.TYPRE[ty];
  if (ty == 0) return "Weapon_";
  return @PKG@.InvData.TYTOOL[ty].replace(';', ',');
}""")
# SkyyWardrobe 0.2.16 cands: { src on|in|pet, ref, item id (pet: icon), eid / "k", rarity, level, quality (pet: colour), count (pet: label) };
# a last line "more|240" = the list was cut (kmore)
M(ipg, r"""
public java.util.ArrayList candRows(int n, int k, String pre) {
  this.kwhy = "";
  this.kmore = false;
  Object o = call("requip:fn:act", new Object[] { this.playerRef.getUuid(), "cands", Integer.valueOf(n), pre == null || pre.length() == 0 ? String.valueOf(k) : k + "|" + pre });
  if (!(o instanceof String)) { this.kwhy = @PKG@.InvCraft.fn("requip:fn:act") == null ? "Requip presets are not on this server right now" : "Requip did not answer"; return null; }
  String s = (String) o;
  if (!s.startsWith("ok|")) { this.kwhy = s.startsWith("off|") ? s.substring(4) : (s.startsWith("-Unknown") ? @PKG@.InvData.K_OLD : bare(s)); return null; }
  String[] ls = s.split("\n");
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 1; i < ls.length; i++) {
    if (ls[i].startsWith("more|")) { this.kmore = true; continue; }
    String[] f = ls[i].split("\\|", -1);
    if (f.length >= 8 && f[2].length() > 0 && f[2].length() < 120) out.add(f);
  }
  return out;
}""")
M(ipg, r"""
public java.util.ArrayList kList(int n, int k, int ty, boolean all) {
  java.util.ArrayList rs = candRows(n, k, all ? "" : kPre(ty, k));
  if (rs == null || k >= 13) return rs;
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList keys = new java.util.ArrayList();
  for (int i = 0; i < rs.size(); i++) {
    String[] r = (String[]) rs.get(i);
    if (!all && !fitsType(ty, k, r[2])) continue;
    String key = rowKey(r);
    int at = out.size();
    while (at > 0 && ((String) keys.get(at - 1)).compareTo(key) > 0) at--;
    out.add(at, r);
    keys.add(at, key);
  }
  return out;
}""")
M(ipg, r"""
public static String rowId(String[] r) {
  if ("in".equals(r[0])) return r[1];
  if (r[3].length() > 0) return r[3];
  return "#" + r[1];
}""")
M(ipg, r"""
public static String[] bestOf(java.util.ArrayList rows, int ty, int k, java.util.HashSet used) {
  if (rows == null) return null;
  for (int i = 0; i < rows.size(); i++) {
    String[] r = (String[]) rows.get(i);
    if (k < 4 ? armType(r[2]) != ty : famOf(ty, r[2]) != k - 4) continue;
    if ("in".equals(r[0]) && "k".equals(r[3])) continue;
    if (used.contains(rowId(r))) continue;
    return r;
  }
  return null;
}""")
M(ipg, r"""
public static void parseSlots(String[] d, String[] marks, String[] ids, String[] codes) {
  for (int i = 1; i < d.length; i++) {
    String[] f = d[i].split("\\|", -1);
    if (f.length < 4) continue;
    int k = toInt(f[0], -1);
    if (k < 0 || k > 12) continue;
    marks[k] = f[1];
    ids[k] = f[2];
    codes[k] = f.length > 4 ? f[4] : null;
  }
}""")
M(ipg, r"""
public static String secWord(int sec) {
  if (sec == 0) return "armor";
  if (sec == 1) return "hotbar";
  if (sec == 2) return "storage";
  if (sec == 3) return "backpack";
  return null;
}""")
M(ipg, r"""
public static String slotTitle(int k) {
  if (k == 0) return "Head";
  if (k == 1) return "Chest";
  if (k == 2) return "Hands";
  if (k == 3) return "Legs";
  if (k == 13) return "Pet";
  if (k == 14) return "Mount";
  return "Hotbar " + (k - 3);
}""")
# the Auto record of preset n (ON unless switched off). FIX (req2 critics, PROJECT-RULES 4 "only rewrite what still holds the old default"):
# first sight = EVERY pick already saved (gear of any skill, Empty, a block) is "set by you" and never changed; only the slots still on
# the default Keep become Auto's (logged with their numbers; a slot's Keep / a click puts it back by hand). Later: a non-Keep pick that is
# not what Auto put there (a click, a drag, Save what I wear, the old page) = set by you
M(ipg, r"""
public static int[] autoState(String pk, int n, int ty, String[] marks, String[] ids) {
  java.util.Properties p = @PKG@.InvState.rqProps(pk);
  String b = "p." + n + ".";
  int hand = toInt(p.getProperty(b + "hand"), 0);
  if ("0".equals(p.getProperty(b + "auto"))) return new int[] { 0, hand };
  boolean seen = "1".equals(p.getProperty(b + "seen"));
  int was = hand;
  int nf = nfam(ty);
  int keepAuto = 0;
  for (int k = 0; k < 4 + nf && k < 13; k++) {
    if ((hand & (1 << k)) != 0) continue;
    String m = marks[k];
    if (m == null || "keep".equals(m)) { if (!seen) keepAuto = keepAuto | (1 << k); continue; }
    String id = ids[k] == null ? "" : ids[k];
    String last = p.getProperty(b + "last." + k, "");
    boolean mine;
    if (!seen) mine = false;
    else if ("empty".equals(m)) mine = "x".equals(last);
    else mine = id.length() > 0 && id.equals(last);
    if (!mine) hand = hand | (1 << k);
  }
  if (!seen) {
    p.setProperty(b + "seen", "1");
    p.setProperty(b + "auto", "1");
    @PKG@.MenuUtil.info("Requip Auto: " + pk + " preset " + (n + 1) + " first seen - your " + Integer.bitCount(hand) + " saved pick(s) stay as set by you (slot bits " + hand
      + "), the " + Integer.bitCount(keepAuto) + " Keep slot(s) (bits " + keepAuto + ") get your best " + @PKG@.InvData.TYN[ty] + " gear on Equip; nothing was changed yet");
  }
  if (hand != was || !seen) { p.setProperty(b + "hand", String.valueOf(hand)); @PKG@.InvState.rqSave(pk); }
  return new int[] { 1, hand };
}""")
# { int[] {auto 1/0, hand bits}, Object[13] best row per Auto slot (null = none owned), boolean[13] the slots Auto fills now }
# (no 5th preset field = SkyyWardrobe < 0.2.16: Auto off, nothing read or written)
M(ipg, r"""
public Object[] autoPlan(int n, int ty, String[] marks, String[] ids, String[] codes) {
  Object[] best = new Object[13];
  boolean[] slot = new boolean[13];
  boolean nw = false;
  for (int k = 0; k < 13; k++) if (codes[k] != null) nw = true;
  if (!nw || ty < 0) return new Object[] { new int[] { 0, 0 }, best, slot };
  int[] st = autoState(@PKG@.Given.key(this.playerRef.getUuid()), n, ty, marks, ids);
  if (st[0] == 0) return new Object[] { st, best, slot };
  int hand = st[1];
  int nf = nfam(ty);
  java.util.HashSet used = new java.util.HashSet();
  boolean[] cov = new boolean[nf];
  for (int k = 0; k < 13; k++) {
    if (k < 4 + nf && (hand & (1 << k)) == 0) continue;
    if (codes[k] != null && (codes[k].startsWith("e:") || codes[k].startsWith("k:"))) {
      String c = codes[k].substring(2);
      int x = c.indexOf(':');
      used.add(x > 0 ? c.substring(0, x) : c);
    }
    if (k >= 4 && ids[k] != null && ids[k].length() > 0 && marks[k] != null && !"keep".equals(marks[k]) && !"empty".equals(marks[k])) {
      int j = famOf(ty, ids[k]);
      if (j >= 0 && j < nf) cov[j] = true;
    }
  }
  java.util.ArrayList hot = null;
  for (int k = 0; k < 4 + nf && k < 13; k++) {
    if ((hand & (1 << k)) != 0) continue;
    if (k >= 4 && cov[k - 4]) continue;
    java.util.ArrayList rows;
    if (k < 4) rows = kList(n, k, ty, false);
    else { if (hot == null) hot = kList(n, 4, ty, false); rows = hot; }
    if (rows == null) return new Object[] { new int[] { 0, hand }, new Object[13], new boolean[13] };
    slot[k] = true;
    String[] r = bestOf(rows, ty, k, used);
    best[k] = r;
    if (r != null) used.add(rowId(r));
  }
  return new Object[] { st, best, slot };
}""")
M(ipg, r"""
public String rqRaw(String op, int n, String arg) {
  Object o = call("requip:fn:act", new Object[] { this.playerRef.getUuid(), op, Integer.valueOf(n), arg == null ? "" : arg });
  return o == null ? null : String.valueOf(o);
}""")
# put row r in slot k of preset n through Requip's own calls: { answer ("=" = already so, no call), the item Auto now owns there }
M(ipg, r"""
public String[] autoSet(int n, int k, String[] r, String mark, String code) {
  boolean keep = mark == null || "keep".equals(mark);
  if (r == null) {
    if (keep) return new String[] { "=", "" };
    String a0 = rqRaw("keep", n, String.valueOf(k));
    return new String[] { a0 == null ? "-Requip did not answer" : a0, "" };
  }
  String want = null;
  if ("in".equals(r[0])) want = ("k".equals(r[3]) ? "k:" : "e:") + r[1];
  else if (r[3].length() > 0) want = "e:" + r[3];
  if (want != null && code != null && (code.equals(want) || code.startsWith(want + ":"))) return new String[] { "=", r[2] };
  if ("on".equals(r[0]) && r[3].length() == 0 && r[1].equals(k < 4 ? "0:" + k : "1:" + (k - 4))) {
    if (keep) return new String[] { "=", "" };
    String a1 = rqRaw("keep", n, String.valueOf(k));
    return new String[] { a1 == null ? "-Requip did not answer" : a1, "" };
  }
  String a = null;
  if (want != null) {
    a = rqRaw("pick", n, k + "|" + want);
    if (a != null && a.startsWith("+")) return new String[] { a, r[2] };
    if (!"on".equals(r[0])) return new String[] { a == null ? "-Requip did not answer" : a, r[2] };
  }
  int c = r[1].indexOf(':');
  int sec = c > 0 ? toInt(r[1].substring(0, c), -1) : -1;
  int sl = c > 0 ? toInt(r[1].substring(c + 1), -1) : -1;
  String w = secWord(sec);
  if (w == null || sl < 0) return new String[] { "-That item moved", r[2] };
  a = rqRaw("drop", n, k + "|" + w + ":" + sl + ":" + r[2]);
  if (a != null && a.startsWith("+")) this.adrop = this.adrop + 1;   // fix (req2 critics): it left your body / bag for Requip storage
  return new String[] { a == null ? "-Requip did not answer" : a, r[2] };
}""")
# EQUIP's first step: every Auto slot of a skill preset gets the best owned gear of its skill (hand-picked slots untouched)
M(ipg, r"""
public String autoFill(int n) {
  java.util.UUID u = this.playerRef.getUuid();
  String[] d = lines("requip:fn:preset", new Object[] { u, Integer.valueOf(n) });
  if (d == null || d.length == 0 || !d[0].startsWith("ok|")) return "";
  String[] h = d[0].split("\\|", -1);
  int ty = rqType(n, h.length > 2 ? h[2] : "");
  if (ty < 0) return "";
  String[] marks = new String[13];
  String[] ids = new String[13];
  String[] codes = new String[13];
  parseSlots(d, marks, ids, codes);
  Object[] pl = autoPlan(n, ty, marks, ids, codes);
  if (((int[]) pl[0])[0] == 0) return "";
  Object[] best = (Object[]) pl[1];
  boolean[] slot = (boolean[]) pl[2];
  String pk = @PKG@.Given.key(u);
  java.util.Properties p = @PKG@.InvState.rqProps(pk);
  String b = "p." + n + ".last.";
  int set = 0;
  int bad = 0;
  boolean ch = false;
  String why = "";
  for (int k = 0; k < 13; k++) {
    if (!slot[k]) continue;
    String[] rr = autoSet(n, k, (String[]) best[k], marks[k], codes[k]);
    if (rr[0].equals("=") || rr[0].startsWith("+")) {
      if (!rr[1].equals(p.getProperty(b + k, ""))) { p.setProperty(b + k, rr[1]); ch = true; }
      if (rr[0].startsWith("+")) set = set + 1;
    } else { bad = bad + 1; if (why.length() == 0) why = bare(rr[0]); }
  }
  if (ch) @PKG@.InvState.rqSave(pk);
  if (set == 0 && bad == 0) return "";
  return "Auto: " + set + (set == 1 ? " slot" : " slots") + " set to your best " + @PKG@.InvData.TYN[ty] + " gear" + (bad > 0 ? " (" + bad + " not: " + why + ")" : "") + ".";
}""")
M(ipg, r"""
public void setHand(int n, int k, boolean on, String last) {
  String pk = @PKG@.Given.key(this.playerRef.getUuid());
  java.util.Properties p = @PKG@.InvState.rqProps(pk);
  String b = "p." + n + ".";
  int h = toInt(p.getProperty(b + "hand"), 0);
  h = on ? (h | (1 << k)) : (h & ~(1 << k));
  p.setProperty(b + "hand", String.valueOf(h));
  p.setProperty(b + "seen", "1");
  if (last != null) p.setProperty(b + "last." + k, last);
  @PKG@.InvState.rqSave(pk);
}""")
M(ipg, r"""
public @IS@ stackAt(int sec, int sl) {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    if (p == null || p.getInventory() == null || sl < 0) return null;
    @IC@ c = null;
    if (sec == 0) c = p.getInventory().getSectionById(@INVC@.ARMOR_SECTION_ID);
    else if (sec == 1) c = p.getInventory().getHotbar();
    else if (sec == 2) c = p.getInventory().getStorage();
    else if (sec == 3) c = p.getInventory().getBackpack();
    if (c == null || sl >= c.getCapacity()) return null;
    return c.getItemStack((short) sl);
  } catch (Throwable t) { return null; }
}""")
M(ipg, r"""
public static String qHex(String id, int q) {
  try {
    if (q < 0) return "";
    @ITEM@ it = @PKG@.InvCraft.item(id);
    if (it != null && q == it.getQualityIndex()) return "";
    return qualHex(@IQL@.getAssetMap().getAsset(q));
  } catch (Throwable t) { return ""; }
}""")
M(ipg, r"""
public static boolean light(String hx) {
  try {
    if (hx == null || hx.length() != 7 || hx.charAt(0) != '#') return true;
    int c = Integer.parseInt(hx.substring(1), 16);
    return ((c >> 16) & 255) >= 192 && ((c >> 8) & 255) >= 192 && (c & 255) >= 192;
  } catch (Throwable t) { return true; }
}""")
# one picker cell: a stack on you = the 0.3.66 slot() (its coloured tooltip + rarity); stored / pet = a NEW stack + name + rarity colour
M(ipg, r"""
public @IGS@ cellOf(String[] r) {
  if ("on".equals(r[0])) {
    int c = r[1].indexOf(':');
    @IS@ s = c > 0 ? stackAt(toInt(r[1].substring(0, c), -1), toInt(r[1].substring(c + 1), -1)) : null;
    if (s != null && !s.isEmpty() && r[2].equals(s.getItemId())) return slot(s);
    return rqSlot(r[2], null, "missing");
  }
  @IGS@ g = new @IGS@();
  if (known(r[2])) g.setItemStack(new @IS@(r[2], 1));
  boolean pet = "pet".equals(r[0]);
  String nm = pet ? r[7].replace("<", "").replace(">", "") : @PKG@.InvCraft.name(r[2]);
  String hx = pet ? (light(r[6]) ? "" : r[6]) : qHex(r[2], toInt(r[6], -1));
  if (!@PKG@.MenuCfg.INV_RARITY) hx = "";
  if (hx.length() > 0) {
    nm = "<color is=" + String.valueOf((char) 34) + hx + String.valueOf((char) 34) + ">" + nm + "</color>";
    try {
      g.setBackground(@UVAL@.of(new @PSTY@().setColor(@UVAL@.of(tint(hx)))));
      g.setSkipItemQualityBackground(true);
      RARS = RARS + 1;
    } catch (Throwable t) { }
  }
  g.setName(nm);
  g.setDescription(pet ? (r[4].length() > 0 ? r[4] + " pet" : "Pet") : ("k".equals(r[3]) ? "In Requip storage - x" + r[7] : "In Requip storage"));
  return g;
}""")
'''
P.rep('''# THE REQUIP PANEL ('r'): the preset list, the picked preset's slots + marks, the hint, the storage strip
''', HELPERS + '''# THE REQUIP PANEL ('r'): the preset list, the picked preset's slots + marks, the hint, the storage strip
''')
# fillRequip: the Auto preview, the labels, the hint, the Auto button
P.rep('''  java.util.ArrayList ra = new java.util.ArrayList();
  java.util.ArrayList rh = new java.util.ArrayList();
  for (int k = 0; k < 4; k++) ra.add(rqSlot(this.rids[k], this.rtit[k], this.rmarks[k]));''', '''  // 0.3.67 (req2): Requip Auto - a skill preset's Auto slots show the best gear Equip puts on ("auto"); slots set by hand say "by you"
  this.rlab = new String[15];
  this.rty = -1;
  this.rauto = false;
  if (d != null && d.length > 0 && d[0].startsWith("ok|")) {
    String[] h2 = d[0].split("\\\\|", -1);
    this.rty = rqType(this.rsel, h2.length > 2 ? h2[2] : "");
    if (this.rty >= 0) {
      String[] mk = new String[13];
      String[] id0 = new String[13];
      String[] cd = new String[13];
      parseSlots(d, mk, id0, cd);
      Object[] pl = autoPlan(this.rsel, this.rty, mk, id0, cd);
      int[] st = (int[]) pl[0];
      this.rauto = st[0] == 1;
      if (this.rauto) {
        Object[] best = (Object[]) pl[1];
        boolean[] sl = (boolean[]) pl[2];
        int nf = nfam(this.rty);
        for (int k = 0; k < 4 + nf && k < 13; k++) {
          if ((st[1] & (1 << k)) != 0) { if (this.rmarks[k] != null) this.rlab[k] = "by you"; continue; }
          if (!sl[k]) continue;
          String[] r = (String[]) best[k];
          this.rlab[k] = "auto";
          this.rmarks[k] = "auto";
          this.rids[k] = r == null ? "" : r[2];
        }
      }
    }
  }
  java.util.ArrayList ra = new java.util.ArrayList();
  java.util.ArrayList rh = new java.util.ArrayList();
  for (int k = 0; k < 4; k++) ra.add(rqSlot(this.rids[k], this.rtit[k], this.rmarks[k]));''')
P.rep('''    String w = this.rmarks[s] == null ? "" : (k < 4 ? markWord(this.rmarks[s]) : (k == 4 ? "pet " : "mount ") + markWord(this.rmarks[s]));''',
      '''    String w = this.rmarks[s] == null ? "" : (k < 4 ? markWord(this.rmarks[s]) : (k == 4 ? "pet " : "mount ") + markWord(this.rmarks[s]));
    if (this.rlab[s] != null) w = this.rlab[s];   // 0.3.67: auto / by you''')
P.rep('''    String w = this.rmarks[4 + k] == null ? "" : markWord(this.rmarks[4 + k]);''',
      '''    String w = this.rmarks[4 + k] == null ? "" : markWord(this.rmarks[4 + k]);
    if (this.rlab[4 + k] != null) w = this.rlab[4 + k];   // 0.3.67: auto / by you''')
P.rep('''          + (this.rslot < 13 ? " - drag an item here to change it, Keep slot = what you wear" : " - set pets on the Pets tab");''',
      '''          + (this.rslot < 13 ? " - click it to choose, Keep slot = what you wear" : " - click it to choose a pet");   // 0.3.67''')
P.rep('''    else hint = @PKG@.InvData.RQ_HELP;''', '''    else hint = this.rauto ? @PKG@.InvData.RQ_AUTO.replace("{T}", @PKG@.InvData.TYN[this.rty]) : @PKG@.InvData.RQ_HELP;   // 0.3.67''')
P.rep('''  b.set("#SkyyInvRqT.Text", title);
  b.set("#SkyyInvRqI.Text", hint);''', '''  b.set("#SkyyInvRqT.Text", title);
  b.set("#SkyyInvRqAu.Text", this.rty < 0 ? "No Auto" : (this.rauto ? "Auto On" : "Auto Off"));   // 0.3.67
  b.set("#SkyyInvRqI.Text", hint);''')
# the picker panel's draw (before build, its caller)
P.rep('''# ONE POCKET ('p'): sacks:fn:pocketList - the real counts on the icons, search, Enchanted only, pages, the picked item; the actions are bound
''', r'''# 0.3.67 (req2): THE SLOT PICKER ('k'): preset rsel, slot kslot (0-12 gear, 13 pet, 14 mount) - what you own that fits, best first
M(ipg, r"""
public void fillPick(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  int n = this.rsel;
  int k = this.kslot;
  String[] d = lines("requip:fn:preset", new Object[] { u, Integer.valueOf(n) });
  String name = "";
  String[] marks = new String[13];
  String[] ids = new String[13];
  String[] codes = new String[13];
  String now = "";
  if (d != null && d.length > 0 && d[0].startsWith("ok|")) {
    String[] h = d[0].split("\\|", -1);
    name = h.length > 2 ? h[2] : "";
    parseSlots(d, marks, ids, codes);
    for (int i = 1; i < d.length && k >= 13; i++) {
      String[] f = d[i].split("\\|", -1);
      if (f.length >= 4 && f[0].equals(k == 13 ? "pet" : "mount")) now = "keep".equals(f[1]) ? "Keep" : ("none".equals(f[1]) ? "Empty" : (f[3].length() > 0 ? f[3] : "a pet"));
    }
  }
  int ty = rqType(n, name);
  String sn = slotTitle(k);
  boolean autoOk = ty >= 0 && k < 13 && k < 4 + nfam(ty);
  if (k < 13) {
    String m = marks[k];
    String id = ids[k] == null ? "" : ids[k];
    now = m == null || "keep".equals(m) ? "Keep" : ("empty".equals(m) ? "Empty" : (id.length() > 0 ? @PKG@.InvCraft.name(id) : markWord(m)));
    if (autoOk) {
      java.util.Properties p = @PKG@.InvState.rqProps(@PKG@.Given.key(u));
      boolean on = !"0".equals(p.getProperty("p." + n + ".auto"));
      boolean hand = (toInt(p.getProperty("p." + n + ".hand"), 0) & (1 << k)) != 0;
      if (on) now = hand ? now + " - set by you" : "Auto (your best " + @PKG@.InvData.TYN[ty] + " gear)";
    }
  }
  java.util.ArrayList rows = k >= 13 ? candRows(n, k, "") : kList(n, k, ty, this.kall || ty < 0);
  int per = @PKG@.InvData.KN;
  int tot = rows == null ? 0 : rows.size();
  int np = tot == 0 ? 1 : (tot + per - 1) / per;
  if (this.kpage >= np) this.kpage = np - 1;
  if (this.kpage < 0) this.kpage = 0;
  this.kshown = new Object[per];
  this.kkey = @PKG@.Given.key(u);
  this.kn = n;
  java.util.ArrayList cells = new java.util.ArrayList();
  for (int i = 0; i < per; i++) {
    int at = this.kpage * per + i;
    String[] r = null;
    if (rows != null && at < tot) r = (String[]) rows.get(at);
    this.kshown[i] = r;
    cells.add(r == null ? new @IGS@() : cellOf(r));
  }
  b.set("#SkyyInvKg.Slots", act(cells));
  b.set("#SkyyInvKT.Text", ("Pick " + sn + " - " + name).toUpperCase());
  b.set("#SkyyInvKS.Text", "Now: " + now);
  b.set("#SkyyInvKU.Text", autoOk ? "Auto best" : "No Auto");
  b.set("#SkyyInvKF.Text", k >= 13 || ty < 0 || this.kall ? "Show all" : "Show " + @PKG@.InvData.TYN[ty]);
  b.set("#SkyyInvKn.Text", (this.kpage + 1) + " / " + np);
  String info;
  if (this.knote != null && this.knote.length() > 0) info = this.knote;
  else if (rows == null) info = this.kwhy != null && this.kwhy.length() > 0 ? this.kwhy : "Requip did not answer";
  else if (tot == 0) info = k >= 13 ? "You own no pets yet" : (ty >= 0 && !this.kall ? "You own no " + @PKG@.InvData.TYN[ty] + " gear for " + sn + " - Show all lists everything that fits" : "You own nothing that fits " + sn);
  else if (this.kmore) info = @PKG@.InvData.K_MORE + (ty >= 0 && this.kall && k < 13 ? " - Show " + @PKG@.InvData.TYN[ty] + " narrows it" : "");   // fix (req2 critics)
  else info = @PKG@.InvData.K_HELP;
  this.knote = "";
  b.set("#SkyyInvKi.Text", info);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvKg", @EVD@.of("a", "kg"), false);
}""")
''' + '''# ONE POCKET ('p'): sacks:fn:pocketList - the real counts on the icons, search, Enchanted only, pages, the picked item; the actions are bound
''')
P.rep('''  else if (pm == 'f') { try { fillFurn(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Furnace panel failed: " + t); } }''',
      '''  else if (pm == 'f') { try { fillFurn(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Furnace panel failed: " + t); } }
  else if (pm == 'k') { try { fillPick(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Requip slot picker failed: " + t); } }   // 0.3.67''')
# Equip = Auto first (presets row + the panel's Equip)
P.rep('''M(ipg, r"""
public void presetEquip(int i) {
  if (this.presetN == null || i < 0 || i >= this.presetN.length) { say("No such preset"); return; }
  int n = this.presetN[i];
  String r = rqAct("equip", n, "");''', '''# 0.3.67 (req2): Equip = Requip Auto first (a skill preset's Auto slots get your best gear of that skill), then Requip's own Equip
M(ipg, r"""
public String equipN(int n) {
  String a = "";
  this.adrop = 0;
  try { a = autoFill(n); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: Requip Auto failed (Equip goes on without it): " + t); a = ""; }
  String raw = rqRaw("equip", n, "");
  String r = raw == null ? (@PKG@.InvCraft.fn("requip:fn:act") == null ? "Requip presets are not on this server right now" : "Requip could not do that here - nothing changed") : bare(raw);
  boolean ok = raw != null && (raw.startsWith("+") || raw.startsWith("="));
  // fix (req2 critics): Auto put gear from your bag into Requip storage, then Equip was refused - say where that gear is
  if (!ok && this.adrop > 0) return r + " Auto had already put " + this.adrop + (this.adrop == 1 ? " item" : " items") + " from your bag into Requip storage - it waits there (Requip tab), nothing is lost.";
  return a.length() > 0 ? r + " " + a : r;
}""")
M(ipg, r"""
public void presetEquip(int i) {
  if (this.presetN == null || i < 0 || i >= this.presetN.length) { say("No such preset"); return; }
  int n = this.presetN[i];
  String r = equipN(n);''')
# a slot click opens the picker (was: select the slot for Keep slot)
P.rep('''  if (k < 0) { say("That slot is not part of the preset"); return; }
  this.rslot = this.rslot == k ? -1 : k;
  redraw();''', '''  if (k < 0) { say("That slot is not part of the preset"); return; }
  this.rslot = k;
  this.kslot = k;   // 0.3.67: the slot picker
  this.kpage = 0;
  this.kall = false;
  this.knote = "";
  this.mode = "k";
  redraw();''')
P.rep('''  if (this.rslot < 0 || this.rslot > 12) { this.rnote = "Pick an armour or hotbar slot of the preset first"; redraw(); return; }
  rqDo("keep", String.valueOf(this.rslot));
}""")''', '''  if (this.rslot < 0 || this.rslot > 12) { this.rnote = "Pick an armour or hotbar slot of the preset first"; redraw(); return; }
  String a = rqRaw("keep", this.rsel, String.valueOf(this.rslot));
  if (a != null && a.startsWith("+") && this.rty >= 0) setHand(this.rsel, this.rslot, true, null);   // 0.3.67: Keep = set by you
  this.rnote = a == null ? (@PKG@.InvCraft.fn("requip:fn:act") == null ? "Requip presets are not on this server right now" : "Requip could not do that here - nothing changed") : bare(a);
  redraw();
}""")''')
PICKACT = r'''# 0.3.67 (req2): the slot picker's clicks - each re-checks the profile + preset it was drawn for; a double click = once
M(ipg, r"""
public boolean kStale() {
  String pk = @PKG@.Given.key(this.playerRef.getUuid());
  if (this.kkey == null || !this.kkey.equals(pk)) { this.knote = "Your profile changed - the list is new, pick again"; redraw(); return true; }
  if (this.kn != this.rsel) { this.knote = "The preset changed - pick again"; redraw(); return true; }
  return false;
}""")
M(ipg, r"""
public void kDone(int k, String raw) {
  if (raw == null) { this.knote = @PKG@.InvCraft.fn("requip:fn:act") == null ? "Requip presets are not on this server right now" : "Requip could not do that here - nothing changed"; redraw(); return; }
  if (!raw.startsWith("+")) { this.knote = raw.startsWith("-Unknown") ? @PKG@.InvData.K_OLD : bare(raw); redraw(); return; }
  if (k < 13 && this.rty >= 0) setHand(this.rsel, k, true, null);
  this.mode = "r";
  this.rslot = k;
  this.rnote = bare(raw);
  redraw();
}""")
M(ipg, r"""
public void kPick(int si) {
  if (this.kshown == null || si < 0 || si >= this.kshown.length || this.kshown[si] == null) { this.knote = "That slot is empty"; redraw(); return; }
  if (kStale()) return;
  String[] r = (String[]) this.kshown[si];
  int n = this.rsel;
  int k = this.kslot;
  String key = "kp:" + n + ":" + k + ":" + r[0] + ":" + r[1];
  if (dup(key)) { this.knote = "Double click ignored - wait a moment to click again"; redraw(); return; }
  moved(key);
  if ("pet".equals(r[0])) { kDone(k, k >= 13 ? rqRaw("pet", n, (k - 13) + "|" + r[1]) : "-Pick an item"); return; }
  if (k >= 13) { this.knote = "Pick a pet"; redraw(); return; }
  if ("in".equals(r[0])) { kDone(k, rqRaw("pick", n, k + "|" + ("k".equals(r[3]) ? "k:" : "e:") + r[1])); return; }
  int c = r[1].indexOf(':');
  int sec = c > 0 ? toInt(r[1].substring(0, c), -1) : -1;
  int sl = c > 0 ? toInt(r[1].substring(c + 1), -1) : -1;
  @IS@ s = stackAt(sec, sl);
  if (s == null || s.isEmpty() || !r[2].equals(s.getItemId()) || secWord(sec) == null) { this.knote = "That item moved since the list was drawn - nothing changed"; redraw(); return; }
  if (r[3].length() > 0) {
    String a = rqRaw("pick", n, k + "|e:" + r[3]);
    if (a != null && a.startsWith("+")) { kDone(k, a); return; }
  }
  kDone(k, rqRaw("drop", n, k + "|" + secWord(sec) + ":" + sl + ":" + r[2]));
}""")
M(ipg, r"""
public void kChoice(boolean empty) {
  if (kStale()) return;
  int n = this.rsel;
  int k = this.kslot;
  String key = "kc:" + n + ":" + k + ":" + empty;
  if (dup(key)) { this.knote = "Double click ignored - wait a moment to click again"; redraw(); return; }
  moved(key);
  if (empty) kDone(k, k >= 13 ? rqRaw("pet", n, (k - 13) + "|") : rqRaw("pick", n, k + "|empty"));
  else kDone(k, k >= 13 ? rqRaw("pet", n, (k - 13) + "|~") : rqRaw("keep", n, String.valueOf(k)));
}""")
M(ipg, r"""
public void kAuto() {
  if (kStale()) return;
  int n = this.rsel;
  int k = this.kslot;
  java.util.UUID u = this.playerRef.getUuid();
  String[] d = lines("requip:fn:preset", new Object[] { u, Integer.valueOf(n) });
  if (d == null || d.length == 0 || !d[0].startsWith("ok|")) { this.knote = "Requip did not answer"; redraw(); return; }
  String[] h = d[0].split("\\|", -1);
  int ty = rqType(n, h.length > 2 ? h[2] : "");
  if (ty < 0 || k >= 13 || k >= 4 + nfam(ty)) { this.knote = @PKG@.InvData.K_NOAUTO; redraw(); return; }
  String[] marks = new String[13];
  String[] ids = new String[13];
  String[] codes = new String[13];
  parseSlots(d, marks, ids, codes);
  boolean nw = false;
  for (int i = 0; i < 13; i++) if (codes[i] != null) nw = true;
  if (!nw) { this.knote = @PKG@.InvData.K_OLD; redraw(); return; }
  String key = "ka:" + n + ":" + k;
  if (dup(key)) { this.knote = "Double click ignored - wait a moment to click again"; redraw(); return; }
  moved(key);
  String pk = @PKG@.Given.key(u);
  java.util.Properties p = @PKG@.InvState.rqProps(pk);
  String b = "p." + n + ".";
  if ("0".equals(p.getProperty(b + "auto"))) p.setProperty(b + "auto", "1");
  setHand(n, k, false, "empty".equals(marks[k]) ? "x" : (ids[k] == null || "keep".equals(marks[k]) ? "" : ids[k]));
  Object[] pl = autoPlan(n, ty, marks, ids, codes);
  boolean[] sl = (boolean[]) pl[2];
  String sn = slotTitle(k);
  String msg;
  if (!sl[k]) msg = sn + " is on Auto - another slot already holds that tool";
  else {
    String[] r = (String[]) ((Object[]) pl[1])[k];
    String[] rr = autoSet(n, k, r, marks[k], codes[k]);
    if (rr[0].equals("=") || rr[0].startsWith("+")) {
      p.setProperty(b + "last." + k, rr[1]);
      @PKG@.InvState.rqSave(pk);
      msg = sn + " is on Auto: " + (r == null ? "you own no " + @PKG@.InvData.TYN[ty] + " gear for it yet" : @PKG@.InvCraft.name(r[2]) + " (your best " + @PKG@.InvData.TYN[ty] + " gear)");
    } else msg = sn + " is on Auto, but: " + bare(rr[0]);
  }
  this.mode = "r";
  this.rslot = k;
  this.rnote = msg;
  redraw();
}""")
# the Requip header's Auto On -> Off; Off -> On = every armour / tool slot back on Auto (their picks now count as Auto's)
M(ipg, r"""
public void rqAutoToggle() {
  if (dup("rqau:" + this.rsel)) { redraw(); return; }
  moved("rqau:" + this.rsel);
  java.util.UUID u = this.playerRef.getUuid();
  String[] d = lines("requip:fn:preset", new Object[] { u, Integer.valueOf(this.rsel) });
  if (d == null || d.length == 0 || !d[0].startsWith("ok|")) { this.rnote = "Requip did not answer"; redraw(); return; }
  String[] h = d[0].split("\\|", -1);
  int ty = rqType(this.rsel, h.length > 2 ? h[2] : "");
  if (ty < 0) { this.rnote = @PKG@.InvData.RQ_NOAUTO; redraw(); return; }
  String pk = @PKG@.Given.key(u);
  java.util.Properties p = @PKG@.InvState.rqProps(pk);
  String b = "p." + this.rsel + ".";
  if (!"0".equals(p.getProperty(b + "auto"))) {
    p.setProperty(b + "auto", "0");
    this.rnote = "Auto OFF: Equip uses exactly what this preset holds";
  } else {
    String[] marks = new String[13];
    String[] ids = new String[13];
    String[] codes = new String[13];
    parseSlots(d, marks, ids, codes);
    p.setProperty(b + "auto", "1");
    p.setProperty(b + "hand", "0");
    p.setProperty(b + "seen", "1");
    for (int k = 0; k < 13; k++) p.setProperty(b + "last." + k, "empty".equals(marks[k]) ? "x" : (ids[k] == null || marks[k] == null || "keep".equals(marks[k]) ? "" : ids[k]));
    this.rnote = "Auto ON: every armour + tool slot is Auto again - Equip puts on your best " + @PKG@.InvData.TYN[ty] + " gear";
  }
  @PKG@.InvState.rqSave(pk);
  redraw();
}""")
'''
P.rep('''M(ipg, r"""
public void rqTake() {''', PICKACT + '''M(ipg, r"""
public void rqTake() {''')
P.rep('''    if (a.equals("rqeq")) { rqDo("equip", ""); return; }''', '''    if (a.equals("rqeq")) { this.rnote = equipN(this.rsel); redraw(); return; }   // 0.3.67: Requip Auto first
    // 0.3.67 (req2): the Auto button + the slot picker
    if (a.equals("rqau")) { rqAutoToggle(); return; }
    if (a.equals("kb")) { this.mode = "r"; redraw(); return; }
    if (a.equals("kg")) { kPick(ival(d, "SlotIndex", -1)); return; }
    if (a.equals("ke")) { kChoice(true); return; }
    if (a.equals("kk")) { kChoice(false); return; }
    if (a.equals("ku")) { kAuto(); return; }
    if (a.equals("kf")) { this.kall = !this.kall; this.kpage = 0; redraw(); return; }
    if (a.equals("kpp")) { this.kpage = this.kpage - 1; redraw(); return; }
    if (a.equals("kpn")) { this.kpage = this.kpage + 1; redraw(); return; }''')
P.rep('''  @PKG@.InvState.TPDIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("invtp");   // 0.3.55: the teleport row per profile''',
      '''  @PKG@.InvState.TPDIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("invtp");   // 0.3.55: the teleport row per profile
  @PKG@.InvState.RQDIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("rqauto");   // 0.3.67: Requip Auto per profile (written on a change only)''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.67: no new system / command"
_i = P.s.index
assert _i("public static int[] autoState(") < _i("public Object[] autoPlan(") < _i("public void fillRequip(") < _i("public void fillPick(") < _i("  String lk = @PKG@.InvData.LK;")
assert _i("public String rqRaw(") < _i("public String[] autoSet(") < _i("public String autoFill(") < _i("public String equipN(") < _i("public void presetEquip(")
assert _i("public String rqAct(") < _i("public String equipN(") and _i("public void setHand(") < _i("public void rqKeep(") and _i("public @IGS@ cellOf(") < _i("public void fillPick(")
assert _i("public static @IGS@ slot(@IS@ s)") < _i("public @IGS@ cellOf(") and _i("public static @IGS@ rqSlot(") < _i("public @IGS@ cellOf(")
assert _i("public static synchronized java.util.Properties rqProps(") < _i("public static int[] autoState(") and _i("public void kDone(") < _i("public void kPick(") < _i("public void rqTake()")
assert _i("public java.util.ArrayList kList(") < _i("public static String[] bestOf(") and _i("public void rqAutoToggle(") < _i('if (a.equals("rqau"))')
P.finish()



# ---- the harness blocks (REQ2)
EXPECT_67 = '''EXPECT = {   # 0.3.67: the slot picker + Requip Auto (InvPage / InvState / InvData), the version strings
    "InvData": ["+f KN", "+f K_HELP", "+f K_MORE", "+f K_NOAUTO", "+f K_OLD", "+f MINE_ARM", "+f RQ_AUTO", "+f RQ_NOAUTO", "+f TYKEY", "+f TYN", "+f TYPRE", "+f TYTOOL", "~<clinit>"],
    "InvPage": ["+f adrop", "+f kall", "+f kkey", "+f kmore", "+f kn", "+f knote", "+f kpage", "+f kshown", "+f kslot", "+f kwhy", "+f rauto", "+f rlab", "+f rty", "+m armType",
                "+m autoFill", "+m autoPlan", "+m autoSet", "+m autoState", "+m bestOf", "+m candRows", "+m cellOf", "+m equipN", "+m famOf", "+m fillPick",
                "+m fitsType", "+m kAuto", "+m kChoice", "+m kDone", "+m kList", "+m kPick", "+m kPre", "+m kStale", "+m light", "+m nfam", "+m parseSlots", "+m qHex",
                "+m rarRank", "+m rowId", "+m rowKey", "+m rqAutoToggle", "+m rqRaw", "+m rqType", "+m secWord", "+m setHand", "+m slotTitle", "+m stackAt",
                "~m build", "~m fillRequip", "~m handleDataEvent", "~m markWord", "~m presetEquip", "~m rqKeep", "~m rqSlotPick"],
    "InvState": ["+f RQA", "+f RQBAD", "+f RQDIR", "+f RQSAVES", "+m rqFile", "+m rqProps", "+m rqSave", "~<clinit>"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the config kit's version text
    "SkyyMenuPlugin": ["~m setup"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],
}
'''
HARNESS_REQ2 = r'''    # ---- REQ2 (0.3.67; Skyy 11-22 "clicking a box in the requip should pull up something to select what goes there" + "ones like mine
    # should auto add the best mining gear you have" + "i dont see a way to set thew hand to empty"): SkyyWardrobe 0.2.16 stand-ins
    rqdir_ = os.path.join(scratch, "rqauto")
    ST.RQDIR = JClass("java.io.File")(rqdir_).toPath()
    ST.RQA.clear()
    for iid_, ms_ in (("Armor_Mining_Lead_Head", 1), ("Armor_Copper_Head", 1), ("Armor_Iron_Hands", 1), ("Armor_Cloth_Head", 1), ("Armor_Cloth_Chest", 1),
                      ("Tool_Pickaxe_Iron", 1), ("Tool_Pickaxe_Lead_SkyWynn", 1), ("Potion_Health", 25), ("Armor_Iron_Head", 1)):
        if amap.get(iid_) is None:
            it_ = Ucls.allocateInstance(ITc.class_)
            E.jf(ITc.class_, "id").set(it_, iid_)
            E.jf(ITc.class_, "translationProperties").set(it_, Ucls.allocateInstance(ITPc.class_))
            E.jf(ITc.class_, "maxStack").setInt(it_, ms_)
            amap.put(iid_, it_)
    R2 = {"names": ["Combat", "Mining", "Farming", "Foraging", "Fishing", "Loadout 6"], "calls": [], "old": False, "four": False,
          "picks": {1: {0: ("on", "Armor_Iron_Head", "e:eH"), 1: ("stored", "Armor_Cloth_Chest", "e:eX"), 3: ("empty", "", "x"),
                        4: ("on", "Tool_Pickaxe_Iron", "e:eP"), 5: ("on", "Weapon_Sword_Iron", "e:eS")}}, "pet": {}}
    C2 = {0: ["on|0:0|Armor_Iron_Head|eH|normal|3|-1|1", "in|eL|Armor_Mining_Lead_Head||rare|20|-1|1", "on|2:7|Armor_Copper_Head||normal|1|-1|1",
              "in|eC|Armor_Cloth_Head||legendary|30|-1|1"],
          1: ["in|eX|Armor_Cloth_Chest||normal|5|-1|1"], 2: ["on|2:3|Armor_Iron_Hands||normal|2|-1|1"], 3: ["on|0:3|Armor_Iron_Legs||normal|2|-1|1"],
          4: ["on|1:0|Tool_Pickaxe_Iron|eP|rare|4|-1|1", "in|eQ|Tool_Pickaxe_Lead_SkyWynn||normal|22|-1|1", "on|1:1|Weapon_Sword_Iron|eS|normal|2|-1|1",
              "in|eK|Potion_Health|k||0|-1|5"],
          13: ["pet|pA|Skyy_PetIcon_Wolf_Legendary||Rare|3|#3c78d8|Rare Wolf Lv 3"]}
    NM2 = ["Head", "Chest", "Hands", "Legs"] + ["Hotbar %d" % (i_ + 1) for i_ in range(9)]
    cl_ = lambda k_: k_ if k_ < 4 or k_ >= 13 else 4

    def f_presets2(o):
        return "\n".join(["ok|1|%d|18" % len(R2["names"])] + ["%d|%s|1|0|0|1" % (i_, n_) for i_, n_ in enumerate(R2["names"])])

    def f_preset2(o):
        n_ = int(o[1])
        pk_ = R2["picks"].setdefault(n_, {})
        ls_ = ["ok|%d|%s|0|0" % (n_, R2["names"][n_])]
        for k_ in range(13):
            m_, i_, c_ = pk_.get(k_, ("keep", "", ""))
            ls_.append("%d|%s|%s|%s" % (k_, m_, i_, NM2[k_]) + ("" if R2["four"] else "|" + c_))
        pv_ = R2["pet"].get(n_)
        return "\n".join(ls_ + ["pet|%s" % ("keep||" if pv_ is None else ("none||" if pv_ == "" else "set|Skyy_PetIcon_Wolf_Legendary|Rare Wolf Lv 3")), "mount|keep||", "abil|keep||"])

    def f_act2(o):
        op_, n_, a_ = str(o[1]), int(o[2]), ("" if o[3] is None else str(o[3]))
        R2["calls"].append((op_, n_, a_))
        nm_ = R2["names"][n_] if 0 <= n_ < len(R2["names"]) else "Requip"
        if R2["old"] and op_ in ("cands", "pick", "pet"):
            return "-Unknown Requip action."
        pk_ = R2["picks"].setdefault(n_, {})
        if op_ == "cands":
            k_ = int(a_.split("|")[0])
            pre_ = [x_ for x_ in a_.split("|", 1)[1].split(",") if x_] if "|" in a_ else []
            rs_ = [r_ for r_ in C2.get(cl_(k_), []) if not pre_ or any(r_.split("|")[2].startswith(x_) for x_ in pre_)]
            return "\n".join(["ok|%d" % k_] + rs_ + (["more|240"] if R2.get("more") else []))
        if op_ == "pick":
            k_, c_ = a_.split("|", 1)
            if c_ == "empty":
                pk_[int(k_)] = ("empty", "", "x")
            else:
                row_ = [r_.split("|") for r_ in C2.get(cl_(int(k_)), []) if r_.split("|")[1] == c_[2:] or r_.split("|")[3] == c_[2:]]
                if not row_:
                    return "-That item is not in Requip any more."
                pk_[int(k_)] = ("stored" if row_[0][0] == "in" else "on", row_[0][2], c_)
            return "+%s: %s takes it." % (nm_, NM2[int(k_)])
        if op_ == "keep":
            pk_.pop(int(a_), None)
            return "+%s: %s keeps what you wear." % (nm_, NM2[int(a_)])
        if op_ == "drop":
            k_, rest_ = a_.split("|", 1)
            w_, sl_, iid_ = rest_.split(":")
            pk_[int(k_)] = ("stored", iid_, "e:d_" + iid_)
            lst_ = C2.setdefault(cl_(int(k_)), [])
            for r_ in list(lst_):
                f_ = r_.split("|")
                if f_[0] == "on" and f_[2] == iid_ and f_[3] == "":
                    lst_.remove(r_)
            lst_.append("in|d_%s|%s||normal|1|-1|1" % (iid_, iid_))
            return "+%s: %s takes %s. It waits in Requip storage until you Equip." % (nm_, NM2[int(k_)], iid_)
        if op_ == "pet":
            rs_, v_ = a_.split("|", 1)
            if v_ == "~":
                R2["pet"].pop(n_, None)
            else:
                R2["pet"][n_] = v_
            return "+%s: the pet slot is set." % nm_
        if op_ == "equip":
            return "-%s is locked." % nm_ if R2.get("eqfail") else "+Equipped %s (1 move)." % nm_
        return "+done"
    for k_, f_ in (("requip:fn:presets", f_presets2), ("requip:fn:preset", f_preset2), ("requip:fn:act", f_act2)):
        BR.put(k_, Fn(f_))
    MUT = lambda: [c_ for c_ in R2["calls"] if c_[0] != "cands"]
    key_ = str(PK.pr.getUuid())
    props_ = lambda: ST.rqProps(key_)
    pv = lambda k_: (None if props_().getProperty(k_) is None else str(props_().getProperty(k_)))
    lab_ = lambda cm_: [(x_ or "").replace("> ", "") for x_ in [sval(cm_, "#SkyyInvMa%d.Text" % k_) for k_ in range(4)] + [sval(cm_, "#SkyyInvMh0.Text"), sval(cm_, "#SkyyInvMh1.Text")]]
    cp0_ = E.count(PK, "Armor_Copper_Head")
    one(ev(PK, {"a": "rqe"}), "REQ2 Edit")
    p_ = one(ev(PK, {"a": "rl:1"}), "REQ2 open Mining")
    cm = cmap(p_) if p_ else {}
    K.eq(MUT(), [], "REQ2 AUTO opening the panel moves / changes nothing (only cands reads)")
    K.eq(lab_(cm), ["by you", "by you", "auto", "by you", "by you", "on you"],
         "REQ2 FIX first sight (PROJECT-RULES 4): EVERY saved pick (even Mining's own Iron head + Iron pickaxe, a combat chest, an Empty slot) = by you; only the default Keep slot (Hands) = auto; Hotbar 2 (no tool kind) as before")
    K.check("Armor_Iron_Head" in cm.get("#SkyyInvRa.Slots", "") and "Armor_Mining_Lead_Head" not in cm.get("#SkyyInvRa.Slots", "") and "Armor_Iron_Hands" in cm.get("#SkyyInvRa.Slots", "")
            and "Tool_Pickaxe_Iron" in cm.get("#SkyyInvRh.Slots", "") and "Tool_Pickaxe_Lead_SkyWynn" not in cm.get("#SkyyInvRh.Slots", "") and nometa(p_),
            "REQ2 FIX preview: your saved Iron helmet + Iron pickaxe stay (no better gear swapped in), the Keep slot Hands = the Iron gloves in your bag; no metadata")
    K.check(sval(cm, "#SkyyInvRqAu.Text") == "Auto On" and ((sval(cm, "#SkyyInvRqI.Text") or "").startswith("Auto puts your best Mining gear") or "waits in Requip storage" in (sval(cm, "#SkyyInvRqI.Text") or "")),
            "REQ2 AUTO the header says Auto On, the hint explains (%s)" % sval(cm, "#SkyyInvRqI.Text"))
    K.check(pv("p.1.hand") == "27" and pv("p.1.last.0") is None and pv("p.1.last.4") is None and pv("p.1.auto") == "1"
            and os.path.isfile(os.path.join(rqdir_, key_ + ".properties")), "REQ2 FIX the record: hand bits 0 1 3 4 (every saved pick), no Auto item yet, the file written (%s)" % dict(props_()))
    m0_ = len(MUT())
    p_ = one(ev(PK, {"a": "rl:1"}), "REQ2 FIX open Mining again")
    K.check(MUT()[m0_:] == [] and lab_(cmap(p_)) == ["by you", "by you", "auto", "by you", "by you", "on you"] and pv("p.1.hand") == "27",
            "REQ2 FIX a second open = the same marks, nothing changed (seen once)")
    # the picker
    p_ = one(ev(PK, {"a": "rs:a", "SlotIndex": 0}), "REQ2 PICK click Head")
    cm = cmap(p_) if p_ else {}
    shown_ = lambda: [None if x_ is None else str(x_[2]) for x_ in pg.kshown][:5]
    K.check(str(pg.mode) == "k" and sval(cm, "#SkyyInvKT.Text") == "PICK HEAD - MINING" and shown_()[:4] == ["Armor_Mining_Lead_Head", "Armor_Iron_Head", "Armor_Copper_Head", None]
            and (sval(cm, "#SkyyInvKS.Text") or "").endswith(" - set by you") and sval(cm, "#SkyyInvKF.Text") == "Show Mining" and sval(cm, "#SkyyInvKU.Text") == "Auto best"
            and "Armor_Cloth_Head" not in cm.get("#SkyyInvKg.Slots", "") and "#SkyyInvRa.Slots" not in cm and nometa(p_),
            "REQ2 PICK a Head click = the picker: Mining helmets only, best first (T5 Lead, T2 Iron, T1 Copper), Now = your helmet, set by you (%s / %s)" % (shown_(), sval(cm, "#SkyyInvKS.Text")))
    cc_ = [c_[2] for c_ in R2["calls"] if c_[0] == "cands" and c_[2].startswith("0")]
    K.check(len(cc_) > 0 and cc_[-1].startswith("0|Armor_Mining_,") and "Armor_Iron_Head" in cc_[-1] and "Armor_Cloth" not in cc_[-1],
            "REQ2 FIX the Mining Head list asks SkyyWardrobe for Mining helmets only (the filter counts before its 240 cap) (%s)" % (cc_[-1:],))
    K.check(("SlotClicking", "#SkyyInvKg") in [(b_[0], b_[1]) for b_ in binds_of(p_)] and all(x_ in [b_[1] for b_ in binds_of(p_)] for x_ in ("#SkyyInvKE", "#SkyyInvKK", "#SkyyInvKU", "#SkyyInvKB")),
            "REQ2 PICK the grid + Empty / Keep / Auto / Back are bound")
    p_ = one(ev(PK, {"a": "kf"}), "REQ2 PICK Show all")
    K.check(shown_()[:5] == ["Armor_Mining_Lead_Head", "Armor_Iron_Head", "Armor_Copper_Head", "Armor_Cloth_Head", None] and sval(cmap(p_), "#SkyyInvKF.Text") == "Show all",
            "REQ2 PICK Show all = every helmet that fits (the combat Cloth helmet last: no tier) (%s)" % shown_())
    K.check([c_[2] for c_ in R2["calls"] if c_[0] == "cands"][-1] == "0", "REQ2 FIX Show all = no filter")
    R2["more"] = True
    p_ = one(ev(PK, {"a": "kpp"}), "REQ2 FIX a cut list")
    K.eq(sval(cmap(p_), "#SkyyInvKi.Text"), str(DATA.K_MORE) + " - Show Mining narrows it", "REQ2 FIX a list SkyyWardrobe cut at 240 = said on the picker")
    R2["more"] = False
    one(ev(PK, {"a": "kf"}), "REQ2 PICK Show Mining again")
    m0_ = len(MUT())
    p_ = one(ev(PK, {"a": "kg", "SlotIndex": 2}), "REQ2 PICK the Copper helmet that is not there")
    K.check(len(MUT()) == m0_ and "moved since the list was drawn" in (sval(cmap(p_), "#SkyyInvKi.Text") or ""), "REQ2 SAFE an item no longer in its place = said, NO call")
    put(PK, "storage", 7, ISc("Armor_Copper_Head", 1))
    one(ev(PK, {"a": "kpp"}), "REQ2 PICK redraw")
    pg.lastMove = ""   # the stale click above armed the double-click guard for this cell
    p_ = one(ev(PK, {"a": "kg", "SlotIndex": 2}), "REQ2 PICK the Copper helmet")
    cm = cmap(p_) if p_ else {}
    K.check(MUT()[m0_:] == [("drop", 1, "0|storage:7:Armor_Copper_Head")] and str(pg.mode) == "r" and lab_(cm)[0] == "by you" and pv("p.1.hand") == "27"
            and "waits in Requip storage" in (sval(cm, "#SkyyInvRqI.Text") or "") and E.count(PK, "Armor_Copper_Head") == cp0_ + 1,
            "REQ2 PICK a plain item in your bag = the SAME call as dragging it (drop 0|storage:7), back on the preset, Head = by you; the page moved nothing (%s)" % MUT()[m0_:])
    m0_ = len(MUT())
    one(ev(PK, {"a": "kg", "SlotIndex": 2}), "REQ2 SAFE the same click again")
    K.eq(len(MUT()), m0_, "REQ2 SAFE a double click = ONE call")
    one(ev(PK, {"a": "rs:a", "SlotIndex": 2}), "REQ2 PICK Hands")
    p_ = one(ev(PK, {"a": "ke"}), "REQ2 EMPTY Hands")
    K.check(MUT()[-1] == ("pick", 1, "2|empty") and lab_(cmap(p_))[2] == "by you" and str(pg.mode) == "r", "REQ2 EMPTY Hands = Requip's Empty pick, set by you (%s %s %s)" % (MUT()[-1], lab_(cmap(p_)), str(pg.mode)))
    one(ev(PK, {"a": "rs:a", "SlotIndex": 1}), "REQ2 PICK Chest")
    p_ = one(ev(PK, {"a": "kk"}), "REQ2 KEEP Chest")
    K.check(MUT()[-1] == ("keep", 1, "1") and lab_(cmap(p_))[1] == "by you" and (int(pv("p.1.hand")) & 2) == 2, "REQ2 KEEP Chest = Requip's Keep, set by you (%s %s %s)" % (MUT()[-1], lab_(cmap(p_)), pv("p.1.hand")))
    one(ev(PK, {"a": "rs:h", "SlotIndex": 3}), "REQ2 PICK Hotbar 4")
    p_ = one(ev(PK, {"a": "kg", "SlotIndex": 0}), "REQ2 PICK the stored Lead pickaxe into Hotbar 4")
    K.check(MUT()[-1] == ("pick", 1, "7|e:eQ") and str(pg.mode) == "r", "REQ2 PICK an item in Requip storage = Requip's pick by its entry, nothing moves (%s)" % (MUT()[-1],))
    one(ev(PK, {"a": "rs:h", "SlotIndex": 3}), "REQ2 PICK Hotbar 4 again")
    one(ev(PK, {"a": "kk"}), "REQ2 KEEP Hotbar 4")
    # Hotbar 1 back on Auto (its list's Auto best): the best pickaxe at once
    one(ev(PK, {"a": "rs:h", "SlotIndex": 0}), "REQ2 PICK Hotbar 1")
    p_ = one(ev(PK, {"a": "ku"}), "REQ2 AUTO Hotbar 1")
    K.check(MUT()[-1] == ("pick", 1, "4|e:eQ") and (int(pv("p.1.hand")) & 16) == 0 and pv("p.1.last.4") == "Tool_Pickaxe_Lead_SkyWynn" and lab_(cmap(p_))[4] == "auto",
            "REQ2 AUTO Hotbar 1's Auto best: back on Auto, the T5 pickaxe set at once (%s %s)" % (MUT()[-1], dict(props_())))
    # Equip: every slot set by you stays; the Auto slot is already the best = Equip only
    m0_ = len(MUT())
    p_ = one(ev(PK, {"a": "rqeq"}), "REQ2 EQUIP Mining")
    K.check(MUT()[m0_:] == [("equip", 1, "")] and "Auto:" not in (sval(cmap(p_), "#SkyyInvRqI.Text") or ""),
            "REQ2 EQUIP every slot set by you stays, Hotbar 1 already the best -> Equip only (%s)" % MUT()[m0_:])
    m0_ = len(MUT())
    one(ev(PK, {"a": "rqeq"}), "REQ2 EQUIP again")
    K.eq(MUT()[m0_:], [("equip", 1, "")], "REQ2 EQUIP again: nothing left to change = only Equip")
    m0_ = len(MUT())
    one(ev(PK, {"a": "rp:1"}), "REQ2 EQUIP from the presets row")
    K.eq(MUT()[m0_:], [("equip", 1, "")], "REQ2 EQUIP the presets row runs Auto too (nothing to change here)")
    # Auto back on Head
    one(ev(PK, {"a": "rs:a", "SlotIndex": 0}), "REQ2 PICK Head")
    p_ = one(ev(PK, {"a": "ku"}), "REQ2 AUTO Head")
    cm = cmap(p_) if p_ else {}
    K.check(MUT()[-1] == ("pick", 1, "0|e:eL") and lab_(cm)[0] == "auto" and (int(pv("p.1.hand")) & 1) == 0 and pv("p.1.last.0") == "Armor_Mining_Lead_Head"
            and (sval(cm, "#SkyyInvRqI.Text") or "").startswith("Head is on Auto"), "REQ2 AUTO a slot's Auto: back on Auto, the best helmet set at once (%s %s %s %s)" % (sval(cm, "#SkyyInvRqI.Text"), MUT()[-3:], lab_(cm), dict(props_())))
    # Auto off / on (reset)
    p_ = one(ev(PK, {"a": "rqau"}), "REQ2 AUTO off")
    cm = cmap(p_) if p_ else {}
    K.check(pv("p.1.auto") == "0" and sval(cm, "#SkyyInvRqAu.Text") == "Auto Off" and "auto" not in lab_(cm) and "by you" not in lab_(cm), "REQ2 AUTO OFF: no auto / by you marks")
    m0_ = len(MUT())
    one(ev(PK, {"a": "rqeq"}), "REQ2 EQUIP with Auto off")
    K.eq(MUT()[m0_:], [("equip", 1, "")], "REQ2 EQUIP with Auto OFF = Equip only")
    pg.lastMove = ""
    p_ = one(ev(PK, {"a": "rqau"}), "REQ2 AUTO on")
    cm = cmap(p_) if p_ else {}
    K.check(pv("p.1.auto") == "1" and pv("p.1.hand") == "0" and lab_(cm)[:5] == ["auto", "auto", "auto", "auto", "auto"], "REQ2 AUTO ON again = every armour + tool slot back on Auto (%s)" % lab_(cm))
    m0_ = len(MUT())
    R2["eqfail"] = True
    p_ = one(ev(PK, {"a": "rqeq"}), "REQ2 EQUIP after the reset (Requip refuses the Equip)")
    R2["eqfail"] = False
    K.check(MUT()[m0_:] == [("drop", 1, "2|storage:3:Armor_Iron_Hands"), ("keep", 1, "3"), ("equip", 1, "")],
            "REQ2 EQUIP after the reset: the gloves from the bag (drop), the worn legs stay where they are (Keep), the rest already best (%s)" % MUT()[m0_:])
    t_ = sval(cmap(p_), "#SkyyInvRqI.Text") or ""
    K.check(t_.startswith("Mining is locked.") and "put 1 item from your bag into Requip storage" in t_ and "nothing is lost" in t_,
            "REQ2 FIX Equip refused after Auto moved gear = says the gear waits in Requip storage (%s)" % t_)
    m0_ = len(MUT())
    one(ev(PK, {"a": "rqeq"}), "REQ2 EQUIP once more")
    K.eq(MUT()[m0_:], [("equip", 1, "")], "REQ2 EQUIP once more: Auto has nothing left to do")
    # pets: the owned list, a pet, None, Keep; Auto refused
    p_ = one(ev(PK, {"a": "rs:a", "SlotIndex": 4}), "REQ2 PET slot")
    cm = cmap(p_) if p_ else {}
    K.check(str(pg.mode) == "k" and sval(cm, "#SkyyInvKT.Text") == "PICK PET - MINING" and "Skyy_PetIcon_Wolf_Legendary" in cm.get("#SkyyInvKg.Slots", "")
            and "Rare Wolf Lv 3" in cm.get("#SkyyInvKg.Slots", "") and sval(cm, "#SkyyInvKU.Text") == "No Auto", "REQ2 PET the pet list (icon, label, rarity colour)")
    one(ev(PK, {"a": "kg", "SlotIndex": 0}), "REQ2 PET pick the wolf")
    K.eq(MUT()[-1], ("pet", 1, "0|pA"), "REQ2 PET a pet = Requip's pet pick")
    one(ev(PK, {"a": "rs:a", "SlotIndex": 4}), "REQ2 PET slot again")
    one(ev(PK, {"a": "ke"}), "REQ2 PET Empty")
    K.eq(MUT()[-1], ("pet", 1, "0|"), "REQ2 PET Empty = none")
    one(ev(PK, {"a": "rs:a", "SlotIndex": 5}), "REQ2 MOUNT slot")
    one(ev(PK, {"a": "kk"}), "REQ2 MOUNT Keep")
    K.eq(MUT()[-1], ("pet", 1, "1|~"), "REQ2 MOUNT Keep = keep")
    one(ev(PK, {"a": "rs:a", "SlotIndex": 5}), "REQ2 MOUNT slot again")
    m0_ = len(MUT())
    p_ = one(ev(PK, {"a": "ku"}), "REQ2 MOUNT Auto")
    K.check(len(MUT()) == m0_ and sval(cmap(p_), "#SkyyInvKi.Text") == str(DATA.K_NOAUTO), "REQ2 MOUNT Auto = said, no call")
    # a profile switch between the draw and the click
    one(ev(PK, {"a": "rs:a", "SlotIndex": 0}), "REQ2 SAFE draw Head")
    BR.put("profile:fn:key", Fn(lambda u_: str(u_) + "-p2"))
    m0_ = len(MUT())
    p_ = one(ev(PK, {"a": "kg", "SlotIndex": 0}), "REQ2 SAFE click after a profile switch")
    K.check(len(MUT()) == m0_ and "profile changed" in (sval(cmap(p_), "#SkyyInvKi.Text") or ""), "REQ2 SAFE a profile switch between draw and click = said, NO call")
    BR.remove("profile:fn:key")
    one(ev(PK, {"a": "kb"}), "REQ2 Back")
    # a custom preset: everything that fits, no Auto
    p_ = one(ev(PK, {"a": "rl:5"}), "REQ2 CUSTOM Loadout 6")
    K.check(sval(cmap(p_), "#SkyyInvRqAu.Text") == "No Auto" and "auto" not in lab_(cmap(p_)), "REQ2 CUSTOM no Auto on a custom preset")
    p_ = one(ev(PK, {"a": "rs:a", "SlotIndex": 0}), "REQ2 CUSTOM Head")
    K.check("Armor_Cloth_Head" in shown_() and "Armor_Mining_Lead_Head" in shown_(), "REQ2 CUSTOM the list = every helmet that fits (%s)" % shown_())
    one(ev(PK, {"a": "kb"}), "REQ2 CUSTOM Back")
    p_ = one(ev(PK, {"a": "rqau"}), "REQ2 CUSTOM Auto")
    K.eq(sval(cmap(p_), "#SkyyInvRqI.Text"), str(DATA.RQ_NOAUTO), "REQ2 CUSTOM Auto = said")
    # SkyyWardrobe 0.2.15 (no cands / pick / pet, 4 preset fields): the picker says so, Auto does nothing
    R2["old"], R2["four"] = True, True
    one(ev(PK, {"a": "rl:1"}), "REQ2 OLD Mining")
    p_ = one(ev(PK, {"a": "rs:a", "SlotIndex": 0}), "REQ2 OLD Head")
    K.eq(sval(cmap(p_), "#SkyyInvKi.Text"), str(DATA.K_OLD), "REQ2 OLD the picker says it needs SkyyWardrobe 0.2.16")
    p_ = one(ev(PK, {"a": "ke"}), "REQ2 OLD Empty")
    K.eq(sval(cmap(p_), "#SkyyInvKi.Text"), str(DATA.K_OLD), "REQ2 OLD Empty = the same line (nothing changed)")
    one(ev(PK, {"a": "kb"}), "REQ2 OLD Back")
    m0_ = len(R2["calls"])
    p_ = one(ev(PK, {"a": "rqeq"}), "REQ2 OLD Equip")
    K.check(R2["calls"][m0_:] == [("equip", 1, "")] and "auto" not in lab_(cmap(p_)), "REQ2 OLD Equip = Equip only (no Auto, no read)")
    R2["old"], R2["four"] = False, False
    # the record survives a restart (read back from the file); FIX: an odd item id is escaped, not dropped
    odd_ = "Some Mod/Item=1 ü#x"
    props_().setProperty("p.1.last.9", odd_)
    K.check(bool(ST.rqSave(key_)), "REQ2 FIX save with an odd item id")
    h0_ = pv("p.1.hand")
    ST.RQA.clear()
    txt_ = open(os.path.join(rqdir_, key_ + ".properties"), encoding="utf8").read()
    K.check(pv("p.1.last.9") == odd_ and "p.1.last.9=Some\\u0020Mod\\u002fItem\\u003d1\\u0020\\u00fc\\u0023x" in txt_,
            "REQ2 FIX an item id outside [A-Za-z0-9:_.-] is kept (escaped) and reads back the same (%s)" % pv("p.1.last.9"))
    K.check(pv("p.1.hand") == h0_ and pv("p.1.auto") == "1" and "p.1.auto=1" in txt_ and txt_.startswith("# SkyyMenu: Requip Auto") and int(ST.RQSAVES) > 0
            and sorted(os.listdir(rqdir_)) == [key_ + ".properties"], "REQ2 FILE read back after a restart = the same record; one file per profile, nothing else")
    K.eq(E.count(PK, "Armor_Copper_Head"), cp0_ + 1, "REQ2 the page itself never moved an item")
    inv(PK, "storage").removeItemStackFromSlot(JShort(7))
    for k_ in ("requip:fn:presets", "requip:fn:preset", "requip:fn:act"):
        BR.put(k_, Fn(NEW[k_]))
    one(ev(PK, {"a": "rqd"}), "REQ2 Done")
    ST.RQA.clear()
    ST.RQDIR = None
'''


# ======================================================================= the HARNESS (derived from the 0.3.66 harness: every 0.3.66 check
# runs again on the 0.3.67 jar, plus REQ2)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.66 (Skyy's 11-22 inventory fixes; tools/menu_0_3_66_patch.py, round furn2).
GENERATED by tools/menu_0_3_66_patch.py from the 0.3.65 harness (edit the patch, not this file): every 0.3.65 check runs again on the
0.3.66 jar''', '''"""Harness for SkyyMenu 0.3.67 (the Requip slot picker + Auto best gear; tools/menu_0_3_67_patch.py, round req2).
GENERATED by tools/menu_0_3_67_patch.py from the 0.3.66 harness (edit the patch, not this file): every 0.3.66 check runs again on the
0.3.67 jar (INV4: a slot click now opens its picker - Back returns with the slot picked), plus
  REQ2 (EXECUTED on the stand-in player with Python stand-ins of SkyyWardrobe 0.2.16 requip:fn:presets / preset (5 fields) / act (cands,
       pick, keep, drop, pet, equip)):
       AUTO    first sight: every saved pick = by you, only Keep slots = auto (fix); opening the panel changes nothing;
               the preview = the best owned gear; the record + file; Auto on a slot sets the best at once; Auto Off / On (reset); Equip:
               Auto first, hand slots untouched, a bag item = drop, an item worn in place = Keep, already best = no call, then Equip; the
               presets row too; Auto OFF = Equip only
       PICK    Head = that skill's helmets best first (tier); Show all adds the rest; a bag item = drop (as a drag); a stored item = pick
               by entry; Empty = pick empty; Keep = keep; pets: the owned list, a pet / None / Keep; Auto on the mount = said
       SAFE    an item no longer in its place, a double click, a profile switch between draw and click = nothing; the page moves no item
       CUSTOM  a custom preset lists everything, no Auto;  OLD  SkyyWardrobe 0.2.15 = the picker says so, Equip only
       FILE    rqauto/<key>.properties read back after a restart, one file per profile; an odd item id escaped + read back (fix)
       FIX     the skill filter sent to cands, a cut list said, a refused Equip after Auto moved gear said
The 0.3.66 harness text follows:
Harness for SkyyMenu 0.3.66 (Skyy's 11-22 inventory fixes; tools/menu_0_3_66_patch.py, round furn2).
GENERATED by tools/menu_0_3_66_patch.py from the 0.3.65 harness (edit the patch, not this file): every 0.3.65 check runs again on the
0.3.66 jar''')
T.rep('VERSION = "0.3.66"\nJAR', 'VERSION = "0.3.67"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.65.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.66.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.65.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.66.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_66_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_67_patch.py")')
T.rep('"scratch", "furn2", "menu"', '"scratch", "req2", "menu"')
T.rep('ADDED = []   # 0.3.66: no new class\n', 'ADDED = []   # 0.3.67: no new class\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.66:', 'if "--expect-dump" in sys.argv:'), EXPECT_67)
T.rep('''    K.check(g.count('VERSION = "0.3.66"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.67"') == 1, "S VERSION")
    K.check("0.3.67: the picker panel fits" in g and "0.3.67: the Auto button + title fit" in g and "0.3.67: a picker line fits one line" in g
            and "0.3.67: a Requip hint fits one line" in g and "0.3.67: the picker panel ids" in g, "REQ2 STATIC the build asserts the picker panel, the Auto button and every line fit")''')
T.rep('''    p_ = one(ev(PK, {"a": "rs:h", "SlotIndex": 2}), "INV4 pick Hotbar 3")
    K.check(int(pg.rslot) == 6''', '''    p_ = one(ev(PK, {"a": "rs:h", "SlotIndex": 2}), "INV4 pick Hotbar 3")
    K.check(int(pg.rslot) == 6 and str(pg.mode) == "k" and "HOTBAR 3" in (sval(cmap(p_), "#SkyyInvKT.Text") or ""), "INV4 (0.3.67) a slot click opens its picker (%s)" % sval(cmap(p_), "#SkyyInvKT.Text"))
    p_ = one(ev(PK, {"a": "kb"}), "INV4 (0.3.67) the picker's Back")
    K.check(int(pg.rslot) == 6''')
T.rep('''    n0_ = len(RQ["calls"])
    one(ev(PK, {"a": "rs:a", "SlotIndex": 4}), "INV4 pick the pet slot")
''', '''    one(ev(PK, {"a": "rs:a", "SlotIndex": 4}), "INV4 pick the pet slot")
    one(ev(PK, {"a": "kb"}), "INV4 (0.3.67) the pet picker's Back")
    n0_ = len(RQ["calls"])
''')
T.rep('''    p_ = one(ev(PK, {"a": "rqd"}), "INV4 Done")
    K.check(str(pg.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_) and "#SkyyInvRa.Slots" not in cmap(p_), "INV4 Done = the craft panel again")
''', '''    p_ = one(ev(PK, {"a": "rqd"}), "INV4 Done")
    K.check(str(pg.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_) and "#SkyyInvRa.Slots" not in cmap(p_), "INV4 Done = the craft panel again")
''' + HARNESS_REQ2)
if T.dst:
    T.finish()
