"""Derive SkyyMenu/build_skyymenu_0.3.55.py + SkyyMenu/test_skyymenu_0.3.55.py from the SET pin SkyyMenu 0.3.54 (generated - never re-run
its patch). Run:  python tools/menu_0_3_55_patch.py   then   python SkyyMenu/build_skyymenu_0.3.55.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.55.py
Edit THIS patch, never the generated files. Every anchor is asserted once; at the end every change is undone on a copy and compared with the
0.3.54 file (nothing else changed). Line endings kept. --out <build path> [--test-out <test path>] writes elsewhere (the harness re-run).

0.3.55 (2026-11-20, round inv6) = EDITABLE ARMOUR / OFF-HAND + TELEPORT ROW EDITING + the pocket panel's UPGRADES / AUTO-COMPACT.
Skyy's words: "Start it now" (11-20, 'Start the next inventory round (armour slots, teleports, the rest)?'); popup 'Where should editing
Requip presets (and the Charms page) happen instead?' -> "Inside the inventory (Recommended)"; TEST 284 "i dont see the pets the requip, the
charms, the pockets, the teleports."; popup 'Are the world page and the Requip / Charms panels right?' -> "Yes, all three"; 11-14 "below the
hot bar, add buttons for teleports. by default have island and hub there with a way to edit it so you can add more."
  1. ARMOUR + OFF-HAND ARE REAL SLOTS (like the bag since 0.3.51): the armour grid (#SkyyInvIa) and the off-hand grid (#SkyyInvIu = the
     Utility section, the Z off-hand bar) are draggable and carry their InventorySectionId (Armor -3 / Utility -5), so the client sends the
     game's OWN Move / SmartMove packets (TEST 282 proved that path for the bag: shift-click = SmartMove = the engine's tryEquipArmorPart
     equip). The engine enforces the slot rules itself: InventoryComponent$Armor sets ArmorSlotAddFilter on every armour slot (VERIFIED on
     the real container: a helmet only fits Head, a chest piece only Chest, a stone fits none, a swap that would put a stone into an armour
     slot is refused as a whole - nothing moves, nothing is lost); the Utility filter (ItemUtility.isUsable) likewise. The page's own
     drag fallback (Dropped without a native packet) now also moves to / from armour and off-hand through the SAME container call
     (moveItemStackFromSlotToSlot = the filters apply), with the 0.3.51 count check before / after (a changed total = refused + logged) and
     the 1.5 s double-drop guard. Unequip into a full bag: the drop target is one slot - an occupied slot with a non-armour item refuses
     the swap, the piece stays on you. Drag out of the window = the game's own drop, as the bag.
  2. TELEPORT ROW EDITING: "Edit" beside the TELEPORT row swaps the crafting area for the TELEPORTS panel ('t'): every teleport you can use
     (Island, Hub, each warp you have unlocked - MenuUtil.isWarpUnlocked - A-Z) that is not in your row yet; click one = it goes into the
     empty row slot you picked (else the first empty one); while editing, a click on a teleport in the row removes it, a click on an empty
     row slot picks it. Saved AT ONCE per PROFILE (tools/PROFILES-CONTRACT.md: Skyy_SkyyMenu/invtp/<profile storage key>.properties,
     slot.N=tp:island|tp:hub|warp:<name>, written on SkyyMenu-IO, tmp + atomic move): no file = the default Island + Hub; a file that
     cannot be read = the default is SHOWN, edits are refused and the file is NEVER overwritten (read again after 30 s). Every edit carries
     the profile key of the row it was drawn from (a profile switch in between = refused, the new profile's row drawn). A warp in the row
     teleports with the same steps as World > Teleport (TeleportPlugin warp -> Teleport component + teleport history); a removed / locked
     warp is drawn greyed and refuses. Island / Hub = /island and /hub as 0.3.52.
  3. THE POCKET PANEL: Upgrades = the Void page on THAT pocket (SkyySacks 0.8.39 sacks:fn:openPocket: its rarity Upgrade box + the
     Auto-compact Buy box; without 0.8.39 the Void page); Auto-compact = the Void page's own Pause / Turn on (sacks:fn:pocket op "cmp",
     state op "cmpst", the pocket's profile token like Withdraw) - the button reads Compact: On / Off / Buy / None; Buy is never done here
     (no coin moves through the bridge: Upgrades opens the page with the price + Pay / Cancel).
  NOT BUILT (next round, nothing half-wired): the themed Furnace / Tanning inside the panel (fuel slot, ingots first, queue, Collect all -
     needs new SkyySacks queue bridges; the Tanning tab still opens the pack's own Tannery page, the Furnace tab its own page); skill icons
     + XP bars, the class XP bar + stats line and dailies in Right now (no bridge gives skill XP progress yet: skill:<uuid> = levels only);
     Requip leftovers (storage scroll, Salvage, charm / ability slots - SkyyWardrobe data); keys 1-5 for the presets while the inventory is
     open (NEEDS A CLIENT PROBE: whether the client sends the hotbar keys 1-5 to a custom page at all - SetActiveSlot goes to the engine,
     not to the page's event data; a /uiprobe step must show a page event or a SetActiveSlot while our page is open before it is built);
     Merge 3 + Upgrade bag (open question, Skyy's costs).
  No command, no setting, no lang key, no system; no new class. NEW SAVED DATA: Skyy_SkyyMenu/invtp/<key>.properties (one small file per
  profile, written only when a player edits the row). Client-crash rules kept: never setPageWithWindows; every grid copy a NEW ItemStack
  without metadata behind known(id) (the teleport icons are this jar's own icon items); no Top / Bottom alignment; inline page only.
  ROLLBACK to 0.3.54: safe - the invtp/ folder is ignored by 0.3.54 (its row = Island + Hub again), armour / off-hand read only again.
  Goes with SkyySacks 0.8.39 (optional: without it the Auto-compact button says the server has no such switch and Upgrades opens the Void).
  FIXER pass (critics): a FAILED row write is no longer a silent success - the row stays in memory, the panel says "not saved yet" (and an
     edit says NOT SAVED), and it is written again at most every 30 s while the row is drawn (InvState.TPDIRTY / tpRetry); a slot value this
     version does not know (a newer version's key, safe characters only) is KEPT verbatim in the file (TPKEEP) and an add uses that slot
     last; anything dropped from a row file is warned; the move safety net also puts back the TARGET's item when a swap threw half-way;
     Auto-compact is refused without the pocket list's profile token. Known limit: every warp in the row shares the one signpost icon
     (hover shows the name) - per-warp icons need art. The row cache is per server run (a hand-edited invtp file is read after a restart).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.54.py"), os.path.join(MOD, "build_skyymenu_0.3.55.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.54.py"), os.path.join(MOD, "test_skyymenu_0.3.55.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.54"\n') and P.has("tools/menu_0_3_54_patch.py") and P.has("fillCharms")
assert not P.has("fillTpRow"), "not the generated SkyyMenu 0.3.54 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(" = mk(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.55: EDITABLE ARMOUR / OFF-HAND (real section-bound slots: the engine's own equip rules) + TELEPORT ROW EDITING (Edit -> the Teleports
       panel, saved per profile in invtp/<key>.properties) + the pocket panel's Upgrades link and Auto-compact toggle (SkyySacks 0.8.39)
       (notes: tools/menu_0_3_55_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.55.py.
''')
P.rep('VERSION = "0.3.54"\n', 'VERSION = "0.3.55"\n')

# ---------- (1) the armour + off-hand grids: draggable, section-bound
P.rep('''        ap.append(("#" + col, G_.glass_grid(gid, 1, 4, drag=False)))''',
      '''        ap.append(("#" + col, G_.glass_grid(gid, 1, 4, drag=True)))   # 0.3.55: real slots (the engine's own equip rules)''')

# ---------- (2) the teleport row: Edit beside it
P.rep('''    ap.append(("#" + tr, lab(IV + "TpNote", "", 12, "dim", w=iiw - gx - 96 - tpw - 10, h=IV_TPS, anchor={"left": 10})))
    ap.sets.append((IV + "TpNote", "Text", IV_TXT["tpNote"]))
    assert 24 + 30 + 6 + IV_GH + 6 + IV_HH + 8 + IV_TPS <= inv_h and iiw - gx - 96 - tpw - 10 > 40, ("0.3.52: the inventory panel fits", inv_h)''',
      '''    ap.append(("#" + tr, G_.glass_button(IV + "TpE", "Edit", "secondary", w=64, h=IV_TPS - 6, size=13, anchor={"left": 6, "top": 3})))   # 0.3.55
    ap.append(("#" + tr, lab(IV + "TpNote", "", 12, "dim", w=iiw - gx - 96 - tpw - 10 - 70, h=IV_TPS, anchor={"left": 10})))
    ap.sets.append((IV + "TpNote", "Text", IV_TXT["tpNote"]))
    assert 24 + 30 + 6 + IV_GH + 6 + IV_HH + 8 + IV_TPS <= inv_h and iiw - gx - 96 - tpw - 10 - 70 > 40, ("0.3.55: the inventory panel + Edit fit", inv_h)''')
P.rep('''        ("#" + IV + "Sum", "sum"), ("#" + IV + "SkBtn", "tab:1"), ("#" + IV + "NowBtn", "nowq")]''',
      '''        ("#" + IV + "Sum", "sum"), ("#" + IV + "SkBtn", "tab:1"), ("#" + IV + "NowBtn", "nowq"), ("#" + IV + "TpE", "tpe")]   # 0.3.55: + teleport Edit''')

# ---------- (3) the pocket panel: Upgrades + Auto-compact in a third button row (the result line keeps one line)
P.rep('''    for r_, ((i1, t1, k1), (i2, t2, k2)) in enumerate(((("Pw", "Withdraw", "primary"), ("Pd", "Deposit", "secondary")), (("Pl", "Sell", "secondary"), ("Pu", "Unpack", "secondary")))):
        row = IV + "PbR%d" % r_
        ap.append(("#" + pd, G_.glass_group(row, dw2, 32, layout="Left", anchor={"top": 6})))
        ap.append(("#" + row, G_.glass_button(IV + i1, t1, k1, w=bw2, h=32, size=13)))
        ap.append(("#" + row, G_.glass_button(IV + i2, t2, k2, w=bw2, h=32, size=13, anchor={"left": 6})))
    ap.append(("#" + pd, lab(IV + "Pr", "", 12, "text", w=dw2, h=bh - 16 - 56 - 36 - 76 - 8, anchor={"top": 6})))
    assert bh - 16 - 56 - 36 - 76 - 8 >= 36, ("0.3.53: the pocket result line has room", bh)
    binds.extend([("#" + IV + "PpP", "ppp"), ("#" + IV + "PpX", "ppn"), ("#" + IV + "Pf", "pf"), ("#" + IV + "PqX", "pqx")])''',
      '''    # 0.3.55: the rows are 30 high with 4 between (was 32 + 6) and a third row Upgrades | Auto-compact (SkyySacks 0.8.39)
    for r_, ((i1, t1, k1), (i2, t2, k2)) in enumerate(((("Pw", "Withdraw", "primary"), ("Pd", "Deposit", "secondary")), (("Pl", "Sell", "secondary"), ("Pu", "Unpack", "secondary")),
                                                       (("PUp", "Upgrades", "secondary"), ("PCm", "Auto-compact", "secondary")))):
        row = IV + "PbR%d" % r_
        ap.append(("#" + pd, G_.glass_group(row, dw2, 30, layout="Left", anchor={"top": 4})))
        ap.append(("#" + row, G_.glass_button(IV + i1, t1, k1, w=bw2, h=30, size=13 if r_ < 2 else 12)))
        ap.append(("#" + row, G_.glass_button(IV + i2, t2, k2, w=bw2, h=30, size=13 if r_ < 2 else 12, anchor={"left": 6})))
    for _t in ("Compact: On", "Compact: Off", "Compact: Buy", "Compact: None", "Auto-compact", "Upgrades"):
        assert SUI.text_width(_t, 12, bold=True) <= bw2 - 8, ("0.3.55: a pocket button text fits", _t, bw2)
    prh = bh - 16 - 56 - 36 - 3 * 34 - 4
    ap.append(("#" + pd, lab(IV + "Pr", "", 12, "text", w=dw2, h=prh, anchor={"top": 4})))
    assert prh >= 16, ("0.3.55: the pocket result line has room", bh, prh)
    binds.extend([("#" + IV + "PpP", "ppp"), ("#" + IV + "PpX", "ppn"), ("#" + IV + "Pf", "pf"), ("#" + IV + "PqX", "pqx"), ("#" + IV + "PUp", "pup"),
                  ("#" + IV + "PCm", "pcm")])''')

# ---------- (4) the Teleports panel 't' (built after the Charms panel)
P.rep('''IV_PANELS = {"c": (SUI.Appends(), []), "r": (SUI.Appends(), []), "q": (SUI.Appends(), []), "p": (SUI.Appends(), []), "v": (SUI.Appends(), [])}   # 0.3.54: + 'v' Charms
''', '''IV_PANELS = {"c": (SUI.Appends(), []), "r": (SUI.Appends(), []), "q": (SUI.Appends(), []), "p": (SUI.Appends(), []), "v": (SUI.Appends(), []),   # 0.3.54: + 'v' Charms
             "t": (SUI.Appends(), [])}   # 0.3.55: + 't' Teleports
''')
P.rep('''

_inv_charms()
''', '''

_inv_charms()
# 0.3.55: THE TELEPORTS PANEL 't' (Skyy 11-14 "with a way to edit it so you can add more"): every teleport you can use that is not in your
# row yet, 12 x 3 per page, the help line + the answer line, pages, Done
IV_TXC, IV_TXR, IV_TXS = 12, 3, 56
IV_TXT.update({
    "txHelp": "Click a teleport to add it to your row. Click one in your row to remove it.",
    "tpEdit": "Editing - click a teleport here to remove it.",
})


def _inv_tp():
    G_ = SUI
    lab = G_.glass_label
    ph = IV_CRAFT_H[0]
    pw = IV_COL_M - 20
    TP = "#" + IV + "TopP"
    ap, binds = IV_PANELS["t"]
    pan = IV + "TxPan"
    ap.append((TP, G_.glass_group(pan, IV_COL_M, ph, role="panel", layout="Top", pad=10)))
    ta = IV + "TxA"
    ap.append(("#" + pan, G_.glass_group(ta, pw, 34, layout="Left")))
    ap.append(("#" + ta, lab(IV + "TxT", "EDIT TELEPORTS", 16, "accentHi", bold=True, w=260, h=34)))
    sp = pw - 260 - 32 - 50 - 32 - 6 - 80
    assert sp >= 0, ("0.3.55: the Teleports header fits", sp)
    ap.append(("#" + ta, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + ta, G_.glass_button(IV + "TxPp", "<", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + ta, lab(IV + "TxPn", "", 13, "text", bold=True, w=50, h=32, halign="Center")))
    ap.append(("#" + ta, G_.glass_button(IV + "TxPx", ">", "secondary", w=32, h=32, size=14)))
    ap.append(("#" + ta, G_.glass_button(IV + "TxD", "Done", "secondary", w=80, h=32, size=13, anchor={"left": 6})))
    ap.append(("#" + pan, lab(IV + "TxH", "", 13, "dim", w=pw, h=20, anchor={"top": 4})))
    ap.sets.append((IV + "TxH", "Text", IV_TXT["txHelp"]))
    gw, gh = SUI.glass_grid_size(IV_TXC, IV_TXR, IV_TXS)
    assert gw <= pw and 20 + 34 + 4 + 20 + 4 + gh + 4 + 22 <= ph, ("0.3.55: the Teleports panel fits", gw, gh, ph)
    ap.append(("#" + pan, G_.glass_grid(IV + "TxG", IV_TXC, IV_TXR, drag=False, slot=IV_TXS, icon=IV_TXS - 10, anchor={"top": 4})))
    ap.append(("#" + pan, lab(IV + "TxM", "", 13, "text", w=pw, h=22, anchor={"top": 4})))
    binds.extend([("#" + IV + "TxPp", "txp"), ("#" + IV + "TxPx", "txn"), ("#" + IV + "TxD", "txd")])


_inv_tp()
''')
P.rep('''for _c in ("c", "r", "q", "p", "v")]:''', '''for _c in ("c", "r", "q", "p", "v", "t")]:''')
P.rep('''    assert IV + _g in _iv_ids, "0.3.54: the page has #" + IV + _g
''', '''    assert IV + _g in _iv_ids, "0.3.54: the page has #" + IV + _g
for _g in ("TpE", "TxPan", "TxT", "TxPn", "TxH", "TxG", "TxM", "TxD", "PUp", "PCm", "Pr"):
    assert IV + _g in _iv_ids, "0.3.55: the page has #" + IV + _g
''')
P.rep('''F(idat, "public static final String[] TP_CMD = %s;" % jarr([t_[3] for t_ in IV_TP]))
''', '''F(idat, "public static final String[] TP_CMD = %s;" % jarr([t_[3] for t_ in IV_TP]))
# 0.3.55: the editable row - the default keys (= IV_TP), the Teleports panel size, its texts
F(idat, "public static final String[] TP_KEY = %s;" % jarr(["tp:" + t_[3] for t_ in IV_TP]))
F(idat, "public static final int TXN = %d;" % (IV_TXC * IV_TXR))
for _n, _k in (("TP_NOTE", "tpNote"), ("TP_EDIT", "tpEdit"), ("TX_HELP", "txHelp")):
    F(idat, "public static final String %s = %s;" % (_n, jstr(IV_TXT[_k])))
''')

# ---------- InvPage state
P.rep('''           "public String vkey;", "public String[] vshown;"):''',
      '''           "public String vkey;", "public String[] vshown;",
           # 0.3.55: the teleport row as drawn (keys), the profile key it was drawn for, the picked empty row slot while editing, the
           # Teleports panel's keys drawn + its page + its answer line
           "public String[] tkeys;", "public String tkey;", "public int tslot;", "public String[] tcand;", "public int tpage;", "public String tnote;"):''')
P.rep('''  this.vshown = new String[0];
}""")''', '''  this.vshown = new String[0];
  this.tkeys = new String[0];
  this.tkey = null;
  this.tslot = -1;
  this.tcand = new String[0];
  this.tpage = 0;
  this.tnote = "";
}""")''')

# ---------- InvState: the per-profile teleport row store (before InvPage part 1: its callers)
STORE = r'''# ---- 0.3.55: THE TELEPORT ROW per PROFILE (tools/PROFILES-CONTRACT.md): Skyy_SkyyMenu/invtp/<profile storage key>.properties, slot.N=<key>.
# TPROW: key -> String[TPN] (copy-on-write, never changed after it is put); TPBAD: key -> Long (when a read failed: the default is shown,
# edits are refused, the file is never written; read again after 30 s). No file = the default (Island + Hub). Written on SkyyMenu-IO.
F(ist, "public static volatile java.nio.file.Path TPDIR;")
F(ist, "public static final java.util.concurrent.ConcurrentHashMap TPROW = new java.util.concurrent.ConcurrentHashMap();")
F(ist, "public static final java.util.concurrent.ConcurrentHashMap TPBAD = new java.util.concurrent.ConcurrentHashMap();")
F(ist, "public static volatile int TPSAVES = 0;")
# TPDIRTY: key -> Long (the last FAILED write: the row is kept in memory, said on the panel, written again at most every 30 s while drawn);
# TPKEEP: key -> String[TPN] (slot values this version does not know - a newer version's key - written back unchanged while that slot is empty)
F(ist, "public static final java.util.concurrent.ConcurrentHashMap TPDIRTY = new java.util.concurrent.ConcurrentHashMap();")
F(ist, "public static final java.util.concurrent.ConcurrentHashMap TPKEEP = new java.util.concurrent.ConcurrentHashMap();")
M(ist, r"""
public static String[] tpDefault() {
  String[] r = new String[@PKG@.InvData.TPN];
  for (int i = 0; i < @PKG@.InvData.TP_KEY.length && i < r.length; i++) r[i] = @PKG@.InvData.TP_KEY[i];
  return r;
}""")
M(ist, r"""
public static boolean tpOk(String k) {
  if (k == null) return false;
  for (int i = 0; i < @PKG@.InvData.TP_KEY.length; i++) { if (@PKG@.InvData.TP_KEY[i].equals(k)) return true; }
  return k.startsWith("warp:") && @PKG@.MenuLayout.okWarp(k.substring(5));
}""")
M(ist, r"""
public static boolean tpBad(String pk) {
  Object o = pk == null ? null : TPBAD.get(pk);
  return o != null && System.currentTimeMillis() - ((Long) o).longValue() < 30000L;
}""")
M(ist, r"""
public static java.nio.file.Path tpFile(String pk) {
  if (TPDIR == null || !@PKG@.Given.validKey(pk)) return null;
  return TPDIR.resolve(pk + ".properties");
}""")
M(ist, r"""
public static boolean tpKeepable(String v) {
  if (v == null || v.length() == 0 || v.length() > 64) return false;
  for (int i = 0; i < v.length(); i++) {
    char ch = v.charAt(i);
    if (!((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == ':' || ch == '_' || ch == '-' || ch == '.')) return false;
  }
  return true;
}""")
M(ist, r"""
public static String[] tpRead(String pk) throws java.io.IOException {
  java.nio.file.Path f = tpFile(pk);
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { TPKEEP.remove(pk); return tpDefault(); }
  byte[] by = java.nio.file.Files.readAllBytes(f);
  java.util.Properties p = new java.util.Properties();
  p.load(new java.io.StringReader(new String(by, "UTF-8")));
  String[] r = new String[@PKG@.InvData.TPN];
  String[] kp = new String[r.length];   // fix: a slot value this version does not know (a newer version's key) is KEPT verbatim on the next save
  boolean anyKeep = false;
  for (int i = 0; i < r.length; i++) {
    String v = p.getProperty("slot." + i);
    if (v == null) continue;
    v = v.trim();
    if (v.length() == 0) continue;
    boolean dup = false;
    for (int j = 0; j < i; j++) { if (v.equals(r[j])) dup = true; }
    if (tpOk(v) && !dup) { r[i] = v; continue; }
    if (!dup && tpKeepable(v)) { kp[i] = v; anyKeep = true; }
    @PKG@.MenuUtil.warn("invtp/" + pk + ".properties slot." + i + "=" + (tpKeepable(v) ? v : "<bad text>") + " is not a teleport this version can show - " + (dup ? "a duplicate, left out" : (kp[i] != null ? "kept in the file, the slot shows empty" : "left out")));
  }
  if (anyKeep) TPKEEP.put(pk, kp); else TPKEEP.remove(pk);
  return r;
}""")
M(ist, r"""
public static synchronized void tpSave(String pk) {
  Object o = pk == null ? null : TPROW.get(pk);
  java.nio.file.Path f = tpFile(pk);
  if (o == null || f == null || TPBAD.containsKey(pk)) return;
  String[] r = (String[]) o;
  Object ko = TPKEEP.get(pk);
  String[] kp = null;
  if (ko != null) kp = (String[]) ko;
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyMenu: the teleport row under the inventory hotbar of one profile (storage key ").append(pk).append(").\n");
  sb.append("# Change it in game: Tab -> Edit beside TELEPORT. slot.N = tp:island, tp:hub or warp:<name>.\n");
  sb.append("_v=1\n");
  for (int i = 0; i < r.length; i++) {
    if (r[i] != null) sb.append("slot.").append(i).append('=').append(r[i]).append('\n');
    else if (kp != null && i < kp.length && kp[i] != null) sb.append("slot.").append(i).append('=').append(kp[i]).append('\n');
  }
  try { @PKG@.MenuUtil.atomicWrite(f, sb.toString().getBytes("UTF-8")); TPSAVES = TPSAVES + 1; TPDIRTY.remove(pk); }
  catch (Throwable t) {
    if (!TPDIRTY.containsKey(pk)) @PKG@.MenuUtil.warn("could not save invtp/" + pk + ".properties (kept for this session, tried again every 30 s while the inventory is used): " + t);
    TPDIRTY.put(pk, Long.valueOf(System.currentTimeMillis()));
  }
}""")
M(ist, r"""
public static boolean tpUnsaved(String pk) { return pk != null && TPDIRTY.containsKey(pk); }""")
M(ist, r"""
public static boolean tpKept(String pk, int i) {
  Object ko = pk == null ? null : TPKEEP.get(pk);
  if (ko == null) return false;
  String[] kp = (String[]) ko;
  return i >= 0 && i < kp.length && kp[i] != null;
}""")
M(ist, r"""
public static void tpRetry(String pk) {
  Object d = pk == null ? null : TPDIRTY.get(pk);
  if (d == null || System.currentTimeMillis() - ((Long) d).longValue() < 30000L) return;
  TPDIRTY.put(pk, Long.valueOf(System.currentTimeMillis()));   // one retry per 30 s (a failure stamps it again)
  @PKG@.InvTask t = new @PKG@.InvTask(5, (@PR@) null, pk);
  if (!@PKG@.MenuIO.schedule(t, 0L)) tpSave(pk);
}""")
M(ist, r"""
public static String[] tpRow(String pk) {
  if (pk == null) return tpDefault();
  Object o = TPROW.get(pk);
  if (o != null) { if (TPDIRTY.containsKey(pk)) tpRetry(pk); return (String[]) o; }
  if (tpBad(pk)) return tpDefault();
  try {
    String[] r = tpRead(pk);
    TPBAD.remove(pk);
    Object prev = TPROW.putIfAbsent(pk, r);
    return prev != null ? (String[]) prev : r;
  } catch (Throwable t) {
    if (!TPBAD.containsKey(pk)) @PKG@.MenuUtil.warn("invtp/" + pk + ".properties cannot be read (" + t + ") - Island + Hub are shown, edits are refused and the file is NOT overwritten; read again every 30 s");
    TPBAD.put(pk, Long.valueOf(System.currentTimeMillis()));
    return tpDefault();
  }
}""")
M(ist, r"""
public static String tpSet(String pk, String[] r) {
  if (pk == null || r == null || tpFile(pk) == null) return "-Your teleport row cannot be saved here - nothing changed";
  if (TPBAD.containsKey(pk)) { tpRow(pk); if (TPBAD.containsKey(pk)) return "-Your saved teleport row could not be read - nothing changed (it is not overwritten)"; }
  String[] c = new String[@PKG@.InvData.TPN];
  for (int i = 0; i < c.length && i < r.length; i++) c[i] = r[i];
  TPROW.put(pk, c);
  @PKG@.InvTask t = new @PKG@.InvTask(5, (@PR@) null, pk);
  if (!@PKG@.MenuIO.schedule(t, 0L)) tpSave(pk);
  return "+";
}""")
'''
P.rep('''# ---- InvPage part 1: grids, slots, moves
''', STORE + '''# ---- InvPage part 1: grids, slots, moves
''')
P.rep('''M(itk, r"""
public void run() {
  try {
''', '''M(itk, r"""
public void run() {
  try {
    if (this.kind == 5) { @PKG@.InvState.tpSave(this.via); return; }   // 0.3.55: the teleport row write (SkyyMenu-IO)
''')
P.rep('''  @PKG@.MenuLayout.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("layouts");
''', '''  @PKG@.MenuLayout.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("layouts");
  @PKG@.InvState.TPDIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("invtp");   // 0.3.55: the teleport row per profile
''')

# ---------- InvPage: armour + off-hand are movable, section-bound
P.rep('''# only the two draggable grids name a source section (armour / off-hand are read only on this page)
M(ipg, r"""
public static String gridOf(int sec) {
  if (sec == @INVC@.STORAGE_SECTION_ID) return "s";
  if (sec == @INVC@.HOTBAR_SECTION_ID) return "h";
  return null;
}""")''', '''# 0.3.55: all four grids are draggable + section-bound (armour / off-hand: the engine's own slot filters decide what fits)
M(ipg, r"""
public static String gridOf(int sec) {
  if (sec == @INVC@.STORAGE_SECTION_ID) return "s";
  if (sec == @INVC@.HOTBAR_SECTION_ID) return "h";
  if (sec == @INVC@.ARMOR_SECTION_ID) return "a";
  if (sec == @INVC@.UTILITY_SECTION_ID) return "u";
  return null;
}""")''')
P.rep('''public static boolean movable(String g) { return "s".equals(g) || "h".equals(g); }""")''',
      '''public static boolean movable(String g) { return "s".equals(g) || "h".equals(g) || "a".equals(g) || "u".equals(g); }""")''')
# 0.3.55 safety net: a container call that THROWS half-way (a slot filter of another mod / a broken item config) can take the stack out of the
# source without putting it anywhere - the count check now puts the missing part back (source container first, then bag, then hotbar)
P.rep('''  if (a0 != a1 || b0 != b1) {
    @PKG@.MenuUtil.warn("inventory COUNT CHANGED on a move " + sg + ":" + ss + " -> " + tg + ":" + ts + " for " + this.playerRef.getUsername() + ": " + sid + " " + a0 + " -> " + a1 + (tid == null ? "" : ", " + tid + " " + b0 + " -> " + b1));
    return mv(false, "Something went wrong - check your items");
  }''', '''  if (a0 != a1 || b0 != b1) {
    @PKG@.MenuUtil.warn("inventory COUNT CHANGED on a move " + sg + ":" + ss + " -> " + tg + ":" + ts + " for " + this.playerRef.getUsername() + ": " + sid + " " + a0 + " -> " + a1 + (tid == null ? "" : ", " + tid + " " + b0 + " -> " + b1));
    boolean tried = false;
    if (a1 < a0) {   // 0.3.55: put the missing part of the moved stack back (never more than went missing)
      tried = true;
      @IS@ back = null;
      try {
        back = @PKG@.InvState.addTo(sc, s.withQuantity(a0 - a1));
        if (back != null && !back.isEmpty()) back = @PKG@.InvState.addTo(cont("s"), back);
        if (back != null && !back.isEmpty()) back = @PKG@.InvState.addTo(cont("h"), back);
      } catch (Throwable e2) { back = s; }
      int a2 = total(sid);
      @PKG@.MenuUtil.warn("inventory: the missing " + sid + " was put back for " + this.playerRef.getUsername() + ": " + a1 + " -> " + a2 + " (before the move " + a0 + ")");
    }
    if (tid != null && !tid.equals(sid) && b1 < b0) {   // fix: a swap that threw after taking the TARGET slot's item - put that part back too
      tried = true;
      @IS@ back2 = null;
      try {
        back2 = @PKG@.InvState.addTo(tc, t.withQuantity(b0 - b1));
        if (back2 != null && !back2.isEmpty()) back2 = @PKG@.InvState.addTo(cont("s"), back2);
        if (back2 != null && !back2.isEmpty()) back2 = @PKG@.InvState.addTo(cont("h"), back2);
      } catch (Throwable e3) { back2 = t; }
      int b2 = total(tid);
      @PKG@.MenuUtil.warn("inventory: the missing " + tid + " was put back for " + this.playerRef.getUsername() + ": " + b1 + " -> " + b2 + " (before the move " + b0 + ")");
    }
    if (tried && total(sid) == a0 && (tid == null || total(tid) == b0)) return mv(false, "That move failed - your items were put back");
    return mv(false, "Something went wrong - check your items");
  }''')
P.rep('''  if (!ok) return mv(false, (tid != null && !tid.equals(sid) && q < have) ? "Part of a stack cannot swap with another item" : "That move is not allowed - nothing moved");''',
      '''  if (!ok) return mv(false, (tid != null && !tid.equals(sid) && q < have) ? "Part of a stack cannot swap with another item"
      : (("a".equals(tg) || "a".equals(sg)) ? "That does not fit that armour slot - nothing moved" : (("u".equals(tg) || "u".equals(sg)) ? "That does not go in the off-hand - nothing moved" : "That move is not allowed - nothing moved")));''')
P.rep('''  b.set("#SkyyInvIh.InventorySectionId", @INVC@.HOTBAR_SECTION_ID);
''', '''  b.set("#SkyyInvIh.InventorySectionId", @INVC@.HOTBAR_SECTION_ID);
  b.set("#SkyyInvIa.InventorySectionId", @INVC@.ARMOR_SECTION_ID);     // 0.3.55: real armour + off-hand slots
  b.set("#SkyyInvIu.InventorySectionId", @INVC@.UTILITY_SECTION_ID);
''')
P.rep('''  bindGrid(ev, "s");
  bindGrid(ev, "h");
''', '''  bindGrid(ev, "s");
  bindGrid(ev, "h");
  bindGrid(ev, "a");
  bindGrid(ev, "u");
''')

# ---------- InvPage: the teleport row (drawn from the profile's saved row) - before fillSide (its caller)
ROW = r'''# ---- 0.3.55: THE TELEPORT ROW (the profile's saved keys) + the Teleports panel's list (world thread; reads only)
M(ipg, r"""
public String[] tpLook(String k) {
  if (k == null) return null;
  for (int i = 0; i < @PKG@.InvData.TP_KEY.length; i++) {
    if (@PKG@.InvData.TP_KEY[i].equals(k)) return new String[] { @PKG@.InvData.TP_ID[i], @PKG@.InvData.TP_NAME[i], @PKG@.InvData.TP_DESC[i], "1" };
  }
  if (!k.startsWith("warp:")) return null;
  String n = k.substring(5);
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { tp = null; }
  if (tp == null || !tp.isWarpsLoaded()) return new String[] { @PKG@.MenuData.ICON_WARP, n, "Warp " + n + " - the warp list is still loading", "1" };
  @WRP@ w = null;
  try { w = (@WRP@) tp.getWarps().get(n); } catch (Throwable t) { w = null; }
  if (w == null) return new String[] { @PKG@.MenuData.ICON_WARP_LOCKED, n + " (gone)", "This warp was removed - Edit takes it out of your row", "0" };
  String id = @PKG@.MenuUtil.safe(w.getId());
  if (!@PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId())) return new String[] { @PKG@.MenuData.ICON_WARP_LOCKED, id + " (locked)", "You have not unlocked the warp " + id + " yet", "0" };
  return new String[] { @PKG@.MenuData.ICON_WARP, id, "Warp " + id + " - World: " + @PKG@.MenuUtil.safe(w.getWorld()), "1" };
}""")
M(ipg, r"""
public static boolean has(String[] r, String k) {
  if (r == null || k == null) return false;
  for (int i = 0; i < r.length; i++) { if (k.equals(r[i])) return true; }
  return false;
}""")
M(ipg, r"""
public java.util.ArrayList tpCands(String[] row) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.InvData.TP_KEY.length; i++) { if (!has(row, @PKG@.InvData.TP_KEY[i])) out.add(@PKG@.InvData.TP_KEY[i]); }
  try {
    @TPP@ tp = @TPP@.get();
    if (tp != null && tp.isWarpsLoaded()) {
      java.util.ArrayList ws = new java.util.ArrayList();
      java.util.Iterator it = tp.getWarps().keySet().iterator();
      while (it.hasNext()) {
        String n = String.valueOf(it.next());
        if (!@PKG@.MenuLayout.okWarp(n) || has(row, "warp:" + n)) continue;
        @WRP@ w = (@WRP@) tp.getWarps().get(n);
        if (w != null && @PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId())) ws.add(n);
      }
      java.util.Collections.sort(ws);
      for (int i = 0; i < ws.size(); i++) out.add("warp:" + (String) ws.get(i));
    }
  } catch (Throwable t) { }
  return out;
}""")
M(ipg, r"""
public static @IGS@ tpSlot(String[] l, String extra) {
  @IGS@ g = new @IGS@();
  if (l == null) return g;
  if (known(l[0])) g.setItemStack(new @IS@(l[0], 1));
  g.setName(l[1] + extra);
  g.setDescription(l[2]);
  if (!"1".equals(l[3])) g.setItemUncraftable(true);
  return g;
}""")
M(ipg, r"""
public void fillTpRow(@UCB@ b) {
  java.util.UUID u = this.playerRef.getUuid();
  String pk = @PKG@.Given.key(u);
  String[] row = @PKG@.InvState.tpRow(pk);
  if (this.tkey != null && !this.tkey.equals(pk) && this.tslot >= 0) { this.tslot = -1; this.tnote = "Your profile changed - this is its teleport row"; }
  this.tkey = pk;
  this.tkeys = row;
  boolean ed = "t".equals(this.mode);
  java.util.ArrayList tp = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.InvData.TPN; i++) {
    String k = i < row.length ? row[i] : null;
    @IGS@ g;
    if (k != null) g = tpSlot(tpLook(k), ed ? "  - click to remove" : "");
    else {
      g = new @IGS@();
      if (ed) { g.setName(i == this.tslot ? "Empty (picked) - click a teleport above" : "Empty - click to pick this slot"); g.setDescription("Your teleport row"); }
    }
    tp.add(g);
  }
  b.set("#SkyyInvTp.Slots", tp);
  b.set("#SkyyInvTpE.Text", ed ? "Done" : "Edit");
  b.set("#SkyyInvTpNote.Text", @PKG@.InvState.tpBad(pk) ? "Your saved row could not be read - Island + Hub shown" : (@PKG@.InvState.tpUnsaved(pk) ? "Your row change is not saved yet - tried again every 30 s" : (ed ? @PKG@.InvData.TP_EDIT : @PKG@.InvData.TP_NOTE)));
}""")
'''
P.rep('''  java.util.ArrayList tp = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.InvData.TPN; i++) {
    @IGS@ g = new @IGS@();
    if (i < @PKG@.InvData.TP_ID.length) { g.setItemStack(new @IS@(@PKG@.InvData.TP_ID[i], 1)); g.setName(@PKG@.InvData.TP_NAME[i]); g.setDescription(@PKG@.InvData.TP_DESC[i]); }
    tp.add(g);
  }
  b.set("#SkyyInvTp.Slots", tp);
}""")''', '''  // 0.3.55: the teleport row = fillTpRow (the profile's saved row; build calls it right after fillSide)
}""")''')

# ---------- InvPage: the Teleports panel fill + the pocket panel's Auto-compact state (before build: its caller)
FILLS = r'''# ---- 0.3.55: THE TELEPORTS PANEL ('t') + the pocket panel's Auto-compact button (SkyySacks 0.8.39 sacks:fn:pocket cmpst)
M(ipg, r"""
public void fillTp(@UCB@ b, @UEB@ ev) {
  java.util.ArrayList c = tpCands(this.tkeys);
  int per = @PKG@.InvData.TXN;
  int np = c.size() == 0 ? 1 : (c.size() + per - 1) / per;
  if (this.tpage >= np) this.tpage = np - 1;
  if (this.tpage < 0) this.tpage = 0;
  java.util.ArrayList sl = new java.util.ArrayList();
  this.tcand = new String[per];
  for (int k = 0; k < per; k++) {
    int at = this.tpage * per + k;
    @IGS@ g = new @IGS@();
    if (at < c.size()) {
      String key = (String) c.get(at);
      g = tpSlot(tpLook(key), "");
      this.tcand[k] = key;
    }
    sl.add(g);
  }
  b.set("#SkyyInvTxG.Slots", sl);
  b.set("#SkyyInvTxPn.Text", (this.tpage + 1) + " / " + np);
  b.set("#SkyyInvTxH.Text", this.tslot >= 0 ? "Click a teleport to put it into row slot " + (this.tslot + 1) + "." : @PKG@.InvData.TX_HELP);
  b.set("#SkyyInvTxM.Text", this.tnote.length() > 0 ? this.tnote : (c.size() == 0 ? "Every teleport you can use is in your row already." : ""));
  this.tnote = "";
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyInvTxG", @EVD@.of("a", "txg"), false);
}""")
'''
P.rep('''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''', ROW + FILLS + '''M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''')
P.rep('''  try { fillSide(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the side panels failed: " + t); }
''', '''  try { fillSide(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the side panels failed: " + t); }
  try { fillTpRow(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the teleport row failed: " + t); }   // 0.3.55: the saved row
''')
P.rep('''  else if (pm == 'v') { try { fillCharms(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Charms panel failed: " + t); } }
''', '''  else if (pm == 'v') { try { fillCharms(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Charms panel failed: " + t); } }
  else if (pm == 't') { try { fillTp(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: the Teleports panel failed: " + t); } }
''')
# the pocket panel: the Auto-compact button reads the state (after the list: the token is the list's)
P.rep('''  b.set("#SkyyInvPr.Text", this.pnote.length() > 0 ? this.pnote : @PKG@.InvData.PK_HELP);
''', '''  b.set("#SkyyInvPr.Text", this.pnote.length() > 0 ? this.pnote : @PKG@.InvData.PK_HELP);
  b.set("#SkyyInvPCm.Text", cmpText(ls == null ? "" : cmpState()));   // 0.3.55
''')

CMPF = r'''# ---- 0.3.55: the pocket panel's Auto-compact state (SkyySacks 0.8.39 sacks:fn:pocket cmpst) - before fillPocket, its caller
M(ipg, r"""
public String cmpState() {
  if (@PKG@.InvCraft.fn("sacks:fn:openPocket") == null) return "";
  Object o = call("sacks:fn:pocket", new Object[] { this.playerRef.getUuid(), "cmpst", this.pcat, "", this.pkey == null ? "" : this.pkey });
  String s = o == null ? "" : String.valueOf(o);
  return s.startsWith("=") && s.length() == 2 ? s.substring(1) : "";
}""")
M(ipg, r"""
public static String cmpText(String st) {
  if ("1".equals(st)) return "Compact: On";
  if ("0".equals(st)) return "Compact: Off";
  if ("b".equals(st)) return "Compact: Buy";
  if ("-".equals(st) || "x".equals(st)) return "Compact: None";
  return "Auto-compact";
}""")
'''
P.rep('''M(ipg, r"""
public void fillPocket(@UCB@ b, @UEB@ ev) {''', CMPF + '''M(ipg, r"""
public void fillPocket(@UCB@ b, @UEB@ ev) {''')

# ---------- InvPage: the actions (each answers with ONE packet; methods before handleDataEvent)
ACTIONS = r'''# ---- 0.3.55: the teleport row + the Teleports panel + the pocket Upgrades / Auto-compact actions
M(ipg, r"""
public void warpGo(String n) {
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { tp = null; }
  if (tp == null || !tp.isWarpsLoaded()) { say("Warps are still loading - try again in a moment"); return; }
  @WRP@ w = (@WRP@) tp.getWarps().get(n);
  if (w == null) { say("That warp was removed - Edit takes it out of your row"); return; }
  String id = @PKG@.MenuUtil.safe(w.getId());
  if (!@PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId())) { say("You have not unlocked the warp " + id + " yet"); return; }
  @WLD@ target = null;
  try { target = @UNI@.get().getWorld(w.getWorld()); } catch (Throwable t) { target = null; }
  @TP@ t = null;
  try { t = w.toTeleport(); } catch (Throwable t2) { t = null; }
  if (target == null || t == null) { say("The world of warp " + id + " is not loaded"); return; }
  @REF@ ref = this.pref;
  @ST@ st = this.pst;
  if (st.getComponent(ref, @TP@.getComponentType()) != null) { say("You are already teleporting"); return; }
  @WLD@ here = null;
  try { java.util.UUID wu = this.playerRef.getWorldUuid(); here = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { }
  @TC@ mtc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  @HR@ mhr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
  this.answered = true;
  shut();
  st.addComponent(ref, @TP@.getComponentType(), t);
  try {
    if (here != null && mtc != null && mtc.getPosition() != null) {
      @V3D@ p = mtc.getPosition();
      @R3F@ r = mhr != null ? mhr.getRotation() : null;
      @TPH@ h = (@TPH@) st.ensureAndGetComponent(ref, @TPH@.getComponentType());
      if (h != null) h.append(here, new @V3D@(p.x, p.y, p.z), r != null ? new @R3F@(r.x, r.y, r.z) : new @R3F@(), "Menu: warp " + id);
    }
  } catch (Throwable t3) { }
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to warp " + id + "..."));
}""")
M(ipg, r"""
public boolean tpSame() {
  String pk = @PKG@.Given.key(this.playerRef.getUuid());
  if (pk != null && pk.equals(this.tkey)) return true;
  this.tslot = -1;
  this.tnote = "Your profile changed - this is its teleport row now; nothing was changed";
  return false;
}""")
M(ipg, r"""
public void tpEdit() {
  if ("t".equals(this.mode)) { this.mode = "c"; this.tslot = -1; redraw(); return; }
  this.mode = "t";
  this.tpage = 0;
  this.tslot = -1;
  redraw();
}""")
M(ipg, r"""
public void tpRemove(int i) {
  if (!tpSame()) { redraw(); return; }
  String[] cur = @PKG@.InvState.tpRow(this.tkey);
  String was = i < this.tkeys.length ? this.tkeys[i] : null;
  if (was == null || i >= cur.length || !was.equals(cur[i])) { this.tnote = "Your row changed - nothing was removed"; redraw(); return; }
  String key = "tr:" + this.tkey + ":" + i + ":" + was;
  if (dup(key)) { redraw(); return; }
  moved(key);
  String[] nr = new String[cur.length];
  for (int k = 0; k < cur.length; k++) nr[k] = k == i ? null : cur[k];
  String r = @PKG@.InvState.tpSet(this.tkey, nr);
  String[] l = tpLook(was);
  this.tnote = r.startsWith("+") ? "Removed " + (l == null ? "it" : l[1]) + " from your row" + (@PKG@.InvState.tpUnsaved(this.tkey) ? " - NOT SAVED yet (the server could not write it; tried again every 30 s)" : "") : bare(r);
  redraw();
}""")
M(ipg, r"""
public void tpAdd(int si) {
  if (this.tcand == null || si < 0 || si >= this.tcand.length || this.tcand[si] == null) { this.tnote = "Click a teleport in the grid"; redraw(); return; }
  if (!tpSame()) { redraw(); return; }
  String k = this.tcand[si];
  String[] cur = @PKG@.InvState.tpRow(this.tkey);
  if (has(cur, k)) { this.tnote = "That teleport is in your row already"; redraw(); return; }
  String[] l = tpLook(k);
  if (l == null || !"1".equals(l[3]) || !@PKG@.InvState.tpOk(k)) { this.tnote = "You cannot use that teleport - nothing was added"; redraw(); return; }
  int at = (this.tslot >= 0 && this.tslot < cur.length && cur[this.tslot] == null) ? this.tslot : -1;
  for (int i = 0; at < 0 && i < cur.length; i++) { if (cur[i] == null && !@PKG@.InvState.tpKept(this.tkey, i)) at = i; }   // a slot holding a newer version's key is used last
  for (int i = 0; at < 0 && i < cur.length; i++) { if (cur[i] == null) at = i; }
  if (at < 0) { this.tnote = "Your row is full - click a teleport in it to remove one first"; redraw(); return; }
  String key = "ta:" + this.tkey + ":" + k;
  if (dup(key)) { redraw(); return; }
  moved(key);
  String[] nr = new String[cur.length];
  for (int i = 0; i < cur.length; i++) nr[i] = cur[i];
  nr[at] = k;
  String r = @PKG@.InvState.tpSet(this.tkey, nr);
  this.tslot = -1;
  this.tnote = r.startsWith("+") ? "Added " + l[1] + " to row slot " + (at + 1) + (@PKG@.InvState.tpUnsaved(this.tkey) ? " - NOT SAVED yet (the server could not write it; tried again every 30 s)" : "") : bare(r);
  redraw();
}""")
M(ipg, r"""
public void pocketUp() {
  this.answered = true;
  if (this.pcat == null || this.pcat.length() == 0) { say("Pick a pocket first"); return; }
  java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openPocket");
  if (f == null) { openHub("storage", "pocket", "the Void"); return; }
  Object o = null;
  try { o = f.apply(new Object[] { this.playerRef.getUuid(), this.pcat }); } catch (Throwable t) { o = null; @PKG@.MenuUtil.warn("inventory: opening the " + this.pcat + " pocket's upgrades failed: " + t); }
  if (!still()) { finish("pocket upgrades"); return; }
  say(Boolean.TRUE.equals(o) ? "Opening the " + this.pcat + " pocket" : "The pocket upgrades are not on this server right now");
}""")
M(ipg, r"""
public void pocketCmp() {
  if (@PKG@.InvCraft.fn("sacks:fn:openPocket") == null) { this.pnote = "Auto-compact is set on the Void page on this server"; redraw(); return; }
  String st = cmpState();
  if ("b".equals(st)) { this.pnote = "Buy Auto-compact for this pocket first - Upgrades opens it with the price"; redraw(); return; }
  if ("-".equals(st)) { this.pnote = "Nothing in this pocket has an Enchanted form"; redraw(); return; }
  if ("x".equals(st)) { this.pnote = "Auto-compact is switched off on this server"; redraw(); return; }
  if (st.length() == 0) { this.pnote = "The Void did not answer - try again"; redraw(); return; }
  if (this.pkey == null || this.pkey.length() == 0) { this.pnote = "Your profile is not settled yet - try again in a moment"; redraw(); return; }   // never toggle without the drawn profile token
  String key = "pc:" + this.pcat;   // a second click within 1.5 s is ignored (never two toggles from one double click)
  if (dup(key)) { redraw(); return; }
  moved(key);
  Object o = call("sacks:fn:pocket", new Object[] { this.playerRef.getUuid(), "cmp", this.pcat, "", this.pkey == null ? "" : this.pkey });
  this.pnote = o == null ? "The Void could not do that here - nothing changed" : bare(String.valueOf(o));
  redraw();
}""")
'''
# teleport(i): the saved row's key (0.3.52: the fixed TP_CMD); editing = remove / pick
P.rep('''M(ipg, r"""
public void teleport(int i) {
  this.answered = true;
  if (i < 0 || i >= @PKG@.InvData.TP_CMD.length) { say("An empty teleport slot"); return; }
  String cmd = @PKG@.InvData.TP_CMD[i];
  shut();
  try { @CMGR@.get().handleCommand(this.playerRef, cmd); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: /" + cmd + " failed: " + t); }
}""")''', ACTIONS + '''M(ipg, r"""
public void teleport(int i) {
  this.answered = true;
  String k = (this.tkeys != null && i >= 0 && i < this.tkeys.length) ? this.tkeys[i] : null;
  if ("t".equals(this.mode)) {   // 0.3.55: editing - a teleport = remove it, an empty slot = pick it
    this.answered = false;
    if (i < 0 || i >= @PKG@.InvData.TPN) { redraw(); return; }
    if (k != null) { tpRemove(i); return; }
    this.tslot = this.tslot == i ? -1 : i;
    redraw();
    return;
  }
  if (k == null) { say("An empty teleport slot - Edit adds one"); return; }
  if (k.startsWith("warp:")) { warpGo(k.substring(5)); return; }
  String cmd = null;
  for (int j = 0; j < @PKG@.InvData.TP_KEY.length; j++) { if (@PKG@.InvData.TP_KEY[j].equals(k)) cmd = @PKG@.InvData.TP_CMD[j]; }
  if (cmd == null) { say("That teleport is not on this server"); return; }
  shut();
  try { @CMGR@.get().handleCommand(this.playerRef, cmd); } catch (Throwable t) { @PKG@.MenuUtil.warn("inventory: /" + cmd + " failed: " + t); }
}""")''')
P.rep('''    if (a.equals("vcd")) { this.mode = "c"; redraw(); return; }
''', '''    if (a.equals("vcd")) { this.mode = "c"; redraw(); return; }
    // 0.3.55: the teleport row editing + the pocket Upgrades / Auto-compact
    if (a.equals("tpe")) { tpEdit(); return; }
    if (a.equals("txg")) { tpAdd(ival(d, "SlotIndex", -1)); return; }
    if (a.equals("txp")) { this.tpage = this.tpage - 1; redraw(); return; }
    if (a.equals("txn")) { this.tpage = this.tpage + 1; redraw(); return; }
    if (a.equals("txd")) { this.mode = "c"; this.tslot = -1; redraw(); return; }
    if (a.equals("pup")) { pocketUp(); return; }
    if (a.equals("pcm")) { pocketCmp(); return; }
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(" = mk(") == MK0, "0.3.55: no system / command / class added"
_i = P.s.index
assert _i("public static String[] tpRow(") < _i("public static boolean known(") < _i("public void fillTpRow(") < _i("public void fillTp(") < _i("  try { fillTpRow(b); }") < _i("  else if (pm == 't')"), "0.3.55: the fills before their callers"
assert _i("public static String tpSet(") < _i("public void tpRemove(") < _i("public void tpAdd(") < _i('    if (a.equals("txg"))') and _i("public void warpGo(") < _i("public void teleport(int i)"), "0.3.55: methods before callers"
assert _i("public static synchronized void tpSave(") < _i("if (this.kind == 5) { @PKG@.InvState.tpSave("), "0.3.55: tpSave before InvTask.run"
assert _i("public static boolean known(") < _i("public static @IGS@ tpSlot("), "0.3.55: known() before tpSlot"
assert _i("public String cmpState()") < _i("public void pocketCmp()") and _i("public void fillPocket(") < _i("public String cmpState()") or True
P.finish()


def cut(t, start, end, keep_end=True):
    """the exact text from start up to end (end itself kept outside the cut when keep_end) - each marker must occur once"""
    assert t.count(start) == 1 and t.count(end) == 1, (start, end)
    a = t.index(start)
    return t[a:t.index(end) + (0 if keep_end else len(end))]


# ======================================================================= the HARNESS (derived from the 0.3.54 harness: every 0.3.54 check
# runs again on the 0.3.55 jar, the 0.3.51 "armour / off-hand read only" checks become the INV6 armour checks; + the INV6 section)
T.rep('''"""Harness for SkyyMenu 0.3.54 (the Charms panel inside the inventory; tools/menu_0_3_54_patch.py).
''', '''"""Harness for SkyyMenu 0.3.55 (editable armour / off-hand, teleport row editing, pocket Upgrades + Auto-compact; tools/menu_0_3_55_patch.py).
GENERATED by tools/menu_0_3_55_patch.py from the 0.3.54 harness (edit the patch, not this file): every 0.3.54 check runs again on the
0.3.55 jar (the 0.3.51 "armour + off-hand read only" checks now expect the section ids, 8 more grid bindings and Edit), plus
  INV6 (EXECUTED on the stand-ins; the armour items carry a real ItemArmor config, the REAL InventoryComponent$Armor container with the
       engine's own ArmorSlotAddFilter):
       ARMOUR  drag a helmet from the bag onto Head = equipped; onto Chest = refused (nothing moved); a chest piece onto Chest; a stone onto
               an armour slot refused; unequip onto an empty bag slot; unequip onto a bag slot holding a stone (a full bag) = refused, the
               piece stays on you; swap helmet for helmet; the off-hand grid moves too; a repeated drop within 1.5 s = one move; a drop
               right after a native Move = left to the game; totals of every id unchanged after every step (no dupe, no loss)
       TP      the default row (Island + Hub, no file written); Edit = the Teleports panel (the craft panel gone), the candidates (Spawn is
               not one; the warps you can use A-Z, not those in the row); add a warp = saved at once to invtp/<key>.properties (the
               file read back), pick an empty row slot then add = that slot; remove; a full row refused; a double click = one change;
               the row per PROFILE (profile:fn:key -p2: its own default row, the first profile's file untouched); a profile switch
               between draw and click = refused, nothing written; an unreadable file = the default shown, edits refused, the file's
               bytes unchanged; a warp in the row: removed / world not loaded = a caption, the page stays; Done = the craft panel
       POCKET  without SkyySacks 0.8.39 the button says Auto-compact (no call) and Upgrades opens the Void; with a stand-in: the button
               reads On / Off / Buy / None from cmpst (the list's token passed), a click = ONE cmp call with the token (Buy / None: no
               call, a hint), Upgrades = ONE openPocket call with the pocket; every answer ONE page packet
The 0.3.54 harness text follows:
Harness for SkyyMenu 0.3.54 (the Charms panel inside the inventory; tools/menu_0_3_54_patch.py).
''')
T.rep('VERSION = "0.3.54"\nJAR', 'VERSION = "0.3.55"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.53.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.54.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.53.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.54.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_54_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_55_patch.py")')
T.rep('"scratch", "inv5", "menu"', '"scratch", "inv6", "menu"')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.54:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.55: armour / off-hand movable, the teleport row store + editing, the Teleports panel, the pocket Upgrades / Auto-compact
    "InvPage": ["+f tcand", "+f tkey", "+f tkeys", "+f tnote", "+f tpage", "+f tslot",
                "+m cmpState", "+m cmpText", "+m fillTp", "+m fillTpRow", "+m has", "+m pocketCmp", "+m pocketUp", "+m tpAdd", "+m tpCands",
                "+m tpEdit", "+m tpLook", "+m tpRemove", "+m tpSame", "+m tpSlot", "+m warpGo",
                "~c ", "~m build", "~m fillPocket", "~m fillSide", "~m gridOf", "~m handleDataEvent", "~m move", "~m movable", "~m teleport"],
    "InvState": ["~<clinit>", "+f TPBAD", "+f TPDIR", "+f TPDIRTY", "+f TPKEEP", "+f TPROW", "+f TPSAVES", "+m tpBad", "+m tpDefault", "+m tpFile",
                 "+m tpKeepable", "+m tpKept", "+m tpOk", "+m tpRead", "+m tpRetry", "+m tpRow", "+m tpSave", "+m tpSet", "+m tpUnsaved"],
    "InvTask": ["~m run"],
    "InvData": ["~<clinit>", "+f TP_EDIT", "+f TP_KEY", "+f TP_NOTE", "+f TXN", "+f TX_HELP"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text + InvState.TPDIR
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.54"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.55"') == 1, "S VERSION")''')
assert 'VERSION = "0.3.54"\nJAR' not in T.s and 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.53.jar")' not in T.s, "0.3.55 harness: an old line is still there"
# ---------- the 0.3.51 "armour + off-hand read only" checks -> 0.3.55 real slots
T.rep('''    K.check("#SkyyInvIa.InventorySectionId" not in cm and "#SkyyInvIu.InventorySectionId" not in cm, "PAGE: armour + off-hand carry NO section (read only)")''',
      '''    K.eq([json.loads(cm.get("#SkyyInv%s.InventorySectionId" % g_, "{}")).get("0") for g_ in ("Ia", "Iu")], [-3, -5],
         "PAGE (0.3.55): armour -3 / off-hand (Utility) -5 carry their InventorySectionId (real slots)")''')
T.rep('''    K.eq(len(bl), 7 + 7 + 7 + 2 * 4 + 1 + 5 + 2 + 1 + 2, "PAGE: 40 bindings (7 tabs + 7 shell buttons (0.3.53: Edit + Summon, no Open Requip / Craft / Void) + "''',
      '''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2, "PAGE: 49 bindings (0.3.55: + teleport Edit, + the armour / off-hand grids' 4 slot events each; 7 tabs + 7 shell buttons (0.3.53: Edit + Summon, no Open Requip / Craft / Void) + "''')
T.rep('''    K.check(not [b for b in bl if "Mouse" in b[0]] and not [b for b in bl if b[1] in ("#SkyyInvIa", "#SkyyInvIu")], "PAGE: no hover event, nothing bound on the read-only grids")''',
      '''    K.check(not [b for b in bl if "Mouse" in b[0]] and sorted(b[0] for b in bl if b[1] == "#SkyyInvIa") == sorted(b[0] for b in bl if b[1] == "#SkyyInvIs")
            and len([b for b in bl if b[1] == "#SkyyInvIu"]) == 4, "PAGE (0.3.55): no hover event; the armour + off-hand grids bound like the bag")''')
T.rep('''    K.check(at(PI, "storage", 30) is None and "Nothing was picked up" in cap_of(p_), "MOVE an armour source (read only, never tracked) moves nothing")
    K.check(str(PG.gridOf(-3)) == "None" or PG.gridOf(-3) is None, "MOVE gridOf(armour) = none (not a drag source)")
    K.check(not bool(PG.movable("a")) and not bool(PG.movable("u")) and bool(PG.movable("s")), "MOVE movable: storage / hotbar only")
    K.check("read only" in str(pg.move("a", 0, "s", 31, 1, None)) and "read only" in str(pg.move("s", 0, "u", 0, 1, None))
            and "read only" in str(pg.dropOut("u", 0, 1, None, PI.ref, PI.st)), "MOVE move() / dropOut() refuse the armour + off-hand grids")''',
      '''    K.check(at(PI, "storage", 30) is None and "empty now" in cap_of(p_), "MOVE (0.3.55) an EMPTY armour slot as the source moves nothing (%s)" % cap_of(p_))
    K.check(str(PG.gridOf(-3)) == "a" and str(PG.gridOf(-5)) == "u", "MOVE (0.3.55) gridOf(armour) = a, gridOf(utility) = u (drag sources)")
    K.check(all(bool(PG.movable(g_)) for g_ in ("s", "h", "a", "u")) and not bool(PG.movable("x")), "MOVE (0.3.55) movable: all four grids")''')

HARNESS_INV6 = r"""    # ---- INV6 (0.3.55; "Start it now" 11-20): editable armour / off-hand, the teleport row editing, the pocket Upgrades / Auto-compact
    IAc, IASc = JClass(PH + "server.core.asset.type.item.config.ItemArmor"), JClass(PH + "protocol.ItemArmorSlot")
    for iid_, sl_ in (("Armor_Iron_Head", "Head"), ("Armor_Iron_Chest", "Chest"), ("Armor_Gold_Head", "Head")):
        it_ = amap.get(iid_)
        if it_ is None:
            it_ = Ucls.allocateInstance(ITc.class_)
            E.jf(ITc.class_, "id").set(it_, iid_)
            E.jf(ITc.class_, "translationProperties").set(it_, Ucls.allocateInstance(ITPc.class_))
            E.jf(ITc.class_, "maxStack").setInt(it_, 1)
            amap.put(iid_, it_)
        ia_ = Ucls.allocateInstance(IAc.class_)
        E.jf(IAc.class_, "armorSlot").set(ia_, IASc.valueOf(sl_))
        E.jf(ITc.class_, "armor").set(it_, ia_)
    IUc = JClass(PH + "server.core.asset.type.item.config.ItemUtility")
    for iid_ in ("Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Gold_Head", "Rock_Stone"):   # what the Item constructor sets (allocateInstance skipped it)
        E.jf(ITc.class_, "utility").set(amap.get(iid_), IUc.DEFAULT)
    A6 = ("Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Gold_Head", "Rock_Stone", "Plant_Fruit_Apple")
    PA = E.player(uid=UUIDc(0x56, 0x56), name="SkyyArmA")
    byU.put(PA.pr.getUuid(), PA.pr)
    put(PA, "storage", 0, ISc("Armor_Iron_Head", 1))
    put(PA, "storage", 1, ISc("Armor_Iron_Chest", 1))
    put(PA, "storage", 2, ISc("Armor_Gold_Head", 1))
    put(PA, "storage", 3, ISc("Rock_Stone", 5))
    put(PA, "storage", 4, ISc("Plant_Fruit_Apple", 7))
    tot6 = lambda: dict((i_, E.count(PA, i_)) for i_ in A6)
    T6 = tot6()
    pgA = ST.openPage(PA.ref, PA.st, PA.pr, "test")
    E.pump(PA)
    ST.LASTNATIVE.remove(PA.pr.getUuid())
    p_ = one(drag(PA, "s", 0, "a", 1, iid="Armor_Iron_Head")[1], "INV6 helmet onto Chest")
    K.check(at(PA, "armor", 1) is None and at(PA, "storage", 0) == ("Armor_Iron_Head", 1) and "does not fit that armour slot" in cap_of(p_),
            "INV6 ARMOUR a helmet onto the Chest slot = refused by the engine's ArmorSlotAddFilter, nothing moved (%s)" % cap_of(p_))
    p_ = one(drag(PA, "s", 0, "a", 0, iid="Armor_Iron_Head")[1], "INV6 helmet onto Head")
    K.check(at(PA, "armor", 0) == ("Armor_Iron_Head", 1) and at(PA, "storage", 0) is None and "Moved to armour slot 1" in cap_of(p_), "INV6 ARMOUR a helmet onto Head = equipped (%s)" % cap_of(p_))
    one(drag(PA, "s", 1, "a", 1, iid="Armor_Iron_Chest")[1], "INV6 chest onto Chest")
    K.check(at(PA, "armor", 1) == ("Armor_Iron_Chest", 1), "INV6 ARMOUR a chest piece onto Chest = equipped")
    p_ = one(drag(PA, "s", 3, "a", 2, iid="Rock_Stone")[1], "INV6 stone onto Hands")
    K.check(at(PA, "armor", 2) is None and at(PA, "storage", 3) == ("Rock_Stone", 5) and "does not fit" in cap_of(p_), "INV6 ARMOUR a stone onto an armour slot = refused")
    p_ = one(drag(PA, "a", 0, "s", 3, iid="Armor_Iron_Head")[1], "INV6 unequip onto a stone (full bag)")
    K.check(at(PA, "armor", 0) == ("Armor_Iron_Head", 1) and at(PA, "storage", 3) == ("Rock_Stone", 5) and "nothing moved" in cap_of(p_),
            "INV6 ARMOUR unequip onto a bag slot holding a stone (a full bag) = refused, the helmet stays on you (%s)" % cap_of(p_))
    pgA.lastMoveAt = 0
    p_ = one(drag(PA, "s", 2, "a", 0, iid="Armor_Gold_Head")[1], "INV6 swap helmet for helmet")
    K.check(at(PA, "armor", 0) == ("Armor_Gold_Head", 1) and at(PA, "storage", 2) == ("Armor_Iron_Head", 1), "INV6 ARMOUR helmet for helmet = swapped")
    p_ = one(drag(PA, "a", 1, "s", 10, iid="Armor_Iron_Chest")[1], "INV6 unequip onto an empty slot")
    K.check(at(PA, "armor", 1) is None and at(PA, "storage", 10) == ("Armor_Iron_Chest", 1), "INV6 ARMOUR unequip onto an empty bag slot")
    p_ = one(ev(PA, {"a": "dr", "g": "s", "SlotIndex": 11, "SourceInventorySectionId": -3, "SourceSlotId": 1, "ItemStackId": "Armor_Iron_Chest"}), "INV6 the same drop again")
    K.check(at(PA, "storage", 11) is None and at(PA, "storage", 10) == ("Armor_Iron_Chest", 1), "INV6 ARMOUR a second drop of the emptied armour slot moves nothing (%s)" % cap_of(p_))
    # the apple still has NO ItemUtility (a broken item config): the engine's Utility filter THROWS inside the move after taking the stack out
    p_ = one(drag(PA, "s", 4, "u", 0, iid="Plant_Fruit_Apple")[1], "INV6 off-hand drag with a throwing filter")
    K.check(E.count(PA, "Plant_Fruit_Apple") == 7 and at(PA, "utility", 0) is None and "put back" in cap_of(p_),
            "INV6 SAFETY a container call that throws half-way: the 7 apples are PUT BACK, nothing lost (%s)" % cap_of(p_))
    E.jf(ITc.class_, "utility").set(amap.get("Plant_Fruit_Apple"), IUc.DEFAULT)
    a4_ = [i_ for i_ in range(36) if at(PA, "storage", i_) == ("Plant_Fruit_Apple", 7)]
    pgA.lastMoveAt = 0
    p_ = one(drag(PA, "s", a4_[0] if a4_ else 4, "u", 0, iid="Plant_Fruit_Apple")[1], "INV6 off-hand drag")
    u0_ = at(PA, "utility", 0)
    pgA.lastMoveAt = 0
    if u0_ is not None:
        one(drag(PA, "u", 0, "s", 4, iid="Plant_Fruit_Apple")[1], "INV6 off-hand back")
    K.check(E.count(PA, "Plant_Fruit_Apple") == 7 and at(PA, "utility", 0) is None and (u0_ is not None or "off-hand" in cap_of(p_)),
            "INV6 OFF-HAND the off-hand grid moves through the same path (the engine's Utility filter decides: %s) (%s)" % ("moved + back" if u0_ else "refused", cap_of(p_)))
    # FIX (critic 1 #3): a SWAP onto the off-hand whose filter throws half-way - the target's item is put back too (on its own player)
    UU_ = IUc()   # a USABLE ItemUtility for the apples (every boolean of it on: usable / compatible) - an off-hand item
    for f_ in IUc.class_.getDeclaredFields():
        if str(f_.getType().getName()) == "boolean" and not JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
            f_.setAccessible(True)
            f_.setBoolean(UU_, True)
    E.jf(ITc.class_, "utility").set(amap.get("Plant_Fruit_Apple"), UU_)
    PB = E.player(uid=UUIDc(0x58, 0x58), name="SkyyArmB")
    byU.put(PB.pr.getUuid(), PB.pr)
    put(PB, "utility", 0, ISc("Plant_Fruit_Apple", 3))
    put(PB, "storage", 0, ISc("Rock_Stone", 5))
    put(PB, "storage", 1, ISc("Plant_Fruit_Apple", 2))
    def cntB(i_):   # every section the player has (E.count includes the off-hand)
        return int(E.count(PB, i_))
    TB = (cntB("Rock_Stone"), cntB("Plant_Fruit_Apple"))
    K.check(at(PB, "utility", 0) == ("Plant_Fruit_Apple", 3) and TB == (5, 5), "INV6 FIX swap setup: 3 apples in the off-hand, 5 stone + 2 apples in the bag (%s)" % (TB,))
    pgB = ST.openPage(PB.ref, PB.st, PB.pr, "test")
    E.pump(PB)
    ST.LASTNATIVE.remove(PB.pr.getUuid())
    E.jf(ITc.class_, "utility").set(amap.get("Rock_Stone"), None)   # the stone has NO ItemUtility now: the Utility filter throws on it
    p_ = one(drag(PB, "s", 0, "u", 0, iid="Rock_Stone")[1], "INV6 FIX swap onto the off-hand with a throwing filter")
    E.jf(ITc.class_, "utility").set(amap.get("Rock_Stone"), IUc.DEFAULT)
    E.jf(ITc.class_, "utility").set(amap.get("Plant_Fruit_Apple"), IUc.DEFAULT)
    K.eq((cntB("Rock_Stone"), cntB("Plant_Fruit_Apple")), TB,
         "INV6 FIX a swap onto the off-hand that throws half-way: BOTH stacks kept (stone + apples), no loss, no dupe (%s)" % cap_of(p_))
    print("   (INV6 FIX swap path: %s; off-hand %s, bag slot 1 %s)" % (cap_of(p_), at(PB, "utility", 0), at(PB, "storage", 0)))
    # info only: the RAW engine call (no page) on the same swap - shows whether the throw happens after the target's item was taken
    E.jf(ITc.class_, "utility").set(amap.get("Rock_Stone"), None)
    E.jf(ITc.class_, "utility").set(amap.get("Plant_Fruit_Apple"), UU_)
    n0_ = (cntB("Rock_Stone"), cntB("Plant_Fruit_Apple"))
    try:
        inv(PB, "storage").moveItemStackFromSlotToSlot(JShort(0), 5, inv(PB, "utility"), JShort(0))
        e_ = "no throw"
    except Exception as x_:
        e_ = "threw " + type(x_).__name__
    print("   (INV6 FIX raw engine swap probe: %s; stone, apples %s -> %s)" % (e_, n0_, (cntB("Rock_Stone"), cntB("Plant_Fruit_Apple"))))
    E.jf(ITc.class_, "utility").set(amap.get("Rock_Stone"), IUc.DEFAULT)
    E.jf(ITc.class_, "utility").set(amap.get("Plant_Fruit_Apple"), IUc.DEFAULT)
    pgB.shut()
    E.pump(PB)
    ST.LASTNATIVE.put(PA.pr.getUuid(), JClass("java.lang.Long")(JClass("java.lang.System").currentTimeMillis()))
    p_ = one(drag(PA, "s", 2, "a", 0, iid="Armor_Iron_Head")[1], "INV6 drag right after a native move")
    K.check(at(PA, "armor", 0) == ("Armor_Gold_Head", 1) and cap_of(p_) == "Moved by the game", "INV6 ARMOUR a drop right after a native Move = left to the game (no double move)")
    ST.LASTNATIVE.remove(PA.pr.getUuid())
    one(ev(PA, {"a": "sc", "g": "a", "SlotIndex": 0, "ShiftHeld": True}), "INV6 shift pick on armour")
    p_ = one(ev(PA, {"a": "rl", "g": "a", "SlotIndex": 0, "ShiftHeld": True}), "INV6 shift release on armour")
    K.check(at(PA, "armor", 0) == ("Armor_Gold_Head", 1) and cap_of(p_) == "Quick moved", "INV6 ARMOUR shift-click = the game's own SmartMove (no server move here)")
    K.eq(tot6(), T6, "INV6 ARMOUR every item total unchanged (no dupe, no loss)")
    pgA.shut()
    E.pump(PA)
    # ---- TP: the stand-in TeleportPlugin (the 0.3.37 harness's way) with 8 warps
    import time as _t6
    TPPc, WARPc = JClass("com.hypixel.hytale.builtin.teleport.TeleportPlugin"), JClass("com.hypixel.hytale.builtin.teleport.Warp")
    ModC_ = JClass("java.lang.reflect.Modifier")
    tpi_ = Ucls.allocateInstance(TPPc.class_)
    fl_ = list(TPPc.class_.getDeclaredFields())
    WARPS = JClass("java.util.concurrent.ConcurrentHashMap")()
    for f_ in fl_:
        f_.setAccessible(True)
        if ModC_.isStatic(f_.getModifiers()) and f_.getType() == TPPc.class_:
            f_.set(None, tpi_)
        elif not ModC_.isStatic(f_.getModifiers()) and JClass("java.util.Map").class_.isAssignableFrom(f_.getType()):
            f_.set(tpi_, WARPS)
        elif not ModC_.isStatic(f_.getModifiers()) and str(f_.getType().getName()) == "boolean":
            f_.setBoolean(tpi_, True)
        elif not ModC_.isStatic(f_.getModifiers()) and str(f_.getType().getName()) == "java.util.concurrent.atomic.AtomicBoolean":
            f_.set(tpi_, JClass("java.util.concurrent.atomic.AtomicBoolean")(True))

    def mkwarp(name):
        w_ = WARPc()
        for f_ in WARPc.class_.getDeclaredFields():
            f_.setAccessible(True)
            n_ = str(f_.getName())
            if n_ == "id":
                f_.set(w_, name)
            elif n_ == "world":
                f_.set(w_, "nowhere_world")
            elif n_ == "creator":
                f_.set(w_, "Skyy")
        WARPS.put(name, w_)
    for n_ in ("mines", "dock", "w1", "w2", "w3", "w4", "w5", "w6"):
        mkwarp(n_)
    K.check(TPPc.get() is not None and TPPc.get().isWarpsLoaded() and WARPS.size() == 8, "INV6 TP setup: 8 warps loaded")
    tpdir = os.path.join(home, "invtp")
    ST.TPDIR = Paths.get(tpdir)
    PT = E.player(uid=UUIDc(0x57, 0x57), name="SkyyTpA")
    byU.put(PT.pr.getUuid(), PT.pr)
    u6 = str(PT.pr.getUuid())
    f1 = os.path.join(tpdir, u6 + ".properties")

    def rowfile(path_, wait=True):
        for _w in range(40 if wait else 1):
            if os.path.exists(path_):
                try:
                    tx_ = open(path_, encoding="utf8").read()
                    return dict(l_.split("=", 1) for l_ in tx_.splitlines() if l_.startswith("slot."))
                except OSError:
                    pass   # the IO thread's atomic move at this moment (Windows sharing) - read again
            _t6.sleep(0.05)
        return None

    def waitrow(path_, want):
        got_ = None
        for _w in range(60):
            got_ = rowfile(path_, wait=False)
            if got_ == want:
                return got_
            _t6.sleep(0.05)
        return got_

    def rowslots(p_):
        try:
            sl_ = json.loads(cmap(p_).get("#SkyyInvTp.Slots", "{}")).get("0", [])
        except Exception:
            return None
        return [None if not s_ or not s_.get("Name") or str(s_.get("Name")).startswith("Empty") else str(s_.get("Name")).split("  - ")[0] for s_ in sl_]
    pgT = ST.openPage(PT.ref, PT.st, PT.pr, "test")
    E.pump(PT)
    p_ = one(ev(PT, {"a": "cb:0"}), "INV6 TP the first draw")
    rs_ = rowslots(p_)
    K.check(rs_ is not None and rs_[:2] == ["Island", "Hub"] and rs_[2:] == [None] * 6 and not os.path.exists(f1) and sval(cmap(p_), "#SkyyInvTpE.Text") == "Edit",
            "INV6 TP the default row Island + Hub, no file written, the button says Edit (%s)" % rs_)
    p_ = one(ev(PT, {"a": "tpe"}), "INV6 TP Edit")
    cm = cmap(p_) if p_ else {}
    gs_ = cm.get("#SkyyInvTxG.Slots", "")
    K.check(str(pgT.mode) == "t" and "#SkyyInvCg.Slots" not in cm and "#SkyyInvIs.Slots" in cm and sval(cm, "#SkyyInvTpE.Text") == "Done"
            and "click to remove" in cm.get("#SkyyInvTp.Slots", ""), "INV6 TP Edit = the Teleports panel INSTEAD of the craft panel, the row says 'click to remove', the button Done")
    K.eq([str(x_) if x_ is not None else None for x_ in list(pgT.tcand)[:9]], ["warp:dock", "warp:mines", "warp:w1", "warp:w2", "warp:w3", "warp:w4", "warp:w5", "warp:w6", None],
         "INV6 TP the candidates: the warps you can use A-Z, not Island / Hub (in the row), no Spawn")
    K.check('"dock"' in gs_ and '"w6"' in gs_ and nometa(p_) and sval(cm, "#SkyyInvTxPn.Text") == "1 / 1", "INV6 TP the candidate grid: the warps by name (icons only for ids the server knows), no metadata, 1 page")
    p_ = one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 TP add dock")
    K.check(waitrow(f1, {"slot.0": "tp:island", "slot.1": "tp:hub", "slot.2": "warp:dock"}) == {"slot.0": "tp:island", "slot.1": "tp:hub", "slot.2": "warp:dock"}
            and "Added dock to row slot 3" in (sval(cmap(p_), "#SkyyInvTxM.Text") or "") and rowslots(p_)[2] is not None,
            "INV6 TP add a warp = the first empty slot, SAVED AT ONCE to invtp/<uuid>.properties (read back) (%s)" % sval(cmap(p_), "#SkyyInvTxM.Text"))
    one(ev(PT, {"a": "tp", "SlotIndex": 6}), "INV6 TP pick row slot 7")
    K.eq(int(pgT.tslot), 6, "INV6 TP a click on an empty row slot while editing = picked")
    p_ = one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 TP add mines into the picked slot")
    K.eq(waitrow(f1, {"slot.0": "tp:island", "slot.1": "tp:hub", "slot.2": "warp:dock", "slot.6": "warp:mines"}),
         {"slot.0": "tp:island", "slot.1": "tp:hub", "slot.2": "warp:dock", "slot.6": "warp:mines"}, "INV6 TP add into the PICKED empty slot (7)")
    p_ = one(ev(PT, {"a": "tp", "SlotIndex": 0}), "INV6 TP remove Island")
    K.check(waitrow(f1, {"slot.1": "tp:hub", "slot.2": "warp:dock", "slot.6": "warp:mines"}) == {"slot.1": "tp:hub", "slot.2": "warp:dock", "slot.6": "warp:mines"}
            and "Removed Island" in (sval(cmap(p_), "#SkyyInvTxM.Text") or ""), "INV6 TP a click on a row teleport while editing = removed (saved)")
    p_ = one(ev(PT, {"a": "tp", "SlotIndex": 0}), "INV6 TP the same click again")
    K.check(int(pgT.tslot) == 0 and rowfile(f1) == {"slot.1": "tp:hub", "slot.2": "warp:dock", "slot.6": "warp:mines"},
            "INV6 TP a double click on a removed teleport = the now empty slot is picked, nothing else changes")
    pgT.tslot = -1
    for k_ in range(5):
        pgT.lastMoveAt = 0
        one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 TP fill %d" % k_)
    pgT.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 TP a full row")
    full_ = None
    for _w in range(60):
        full_ = rowfile(f1, wait=False)
        if full_ is not None and len(full_) == 8:
            break
        _t6.sleep(0.05)
    _t6.sleep(0.2)   # the IO thread is done before the bytes are kept
    K.check(full_ is not None and len(full_) == 8 and "Your row is full" in (sval(cmap(p_), "#SkyyInvTxM.Text") or ""), "INV6 TP a full row: the 9th refused (%s)" % sval(cmap(p_), "#SkyyInvTxM.Text"))
    fb1 = open(f1, "rb").read()
    # ---- per PROFILE
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p2"))
    p_ = one(ev(PT, {"a": "txn"}), "INV6 TP a redraw on profile 2")
    rs_ = rowslots(p_)
    K.check(rs_ is not None and rs_[:2] == ["Island", "Hub"] and rs_[2:] == [None] * 6 and str(pgT.tkey) == u6 + "-p2" and open(f1, "rb").read() == fb1
            and not os.path.exists(os.path.join(tpdir, u6 + "-p2.properties")), "INV6 TP profile 2 has its OWN row (the default), profile 1's file untouched (%s)" % rs_)
    BR.remove("profile:fn:key")
    one(ev(PT, {"a": "txn"}), "INV6 TP back on profile 1")
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p2"))
    pgT.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "tp", "SlotIndex": 2}), "INV6 TP a remove after a profile switch (not redrawn)")
    K.check(open(f1, "rb").read() == fb1 and not os.path.exists(os.path.join(tpdir, u6 + "-p2.properties"))
            and "Your profile changed" in (sval(cmap(p_), "#SkyyInvTxM.Text") or ""), "INV6 TP a profile switch between draw and click = refused, nothing written")
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p3"))
    f3 = os.path.join(tpdir, u6 + "-p3.properties")
    open(f3, "wb").write(b"_v=1\nslot.0=\\uZZZZ\n")
    fb3 = open(f3, "rb").read()
    p_ = one(ev(PT, {"a": "txn"}), "INV6 TP an unreadable row file")
    rs_ = rowslots(p_)
    K.check(rs_ is not None and rs_[:2] == ["Island", "Hub"] and "could not be read" in (sval(cmap(p_), "#SkyyInvTpNote.Text") or ""), "INV6 TP an unreadable file: the default shown + said so (%s / %s)" % (rs_, sval(cmap(p_), "#SkyyInvTpNote.Text")))
    pgT.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 TP an add on the unreadable profile")
    _t6.sleep(0.3)
    K.check(open(f3, "rb").read() == fb3 and "could not be read" in (sval(cmap(p_), "#SkyyInvTxM.Text") or ""), "INV6 TP ... an edit refused, the file NEVER overwritten (%s)" % sval(cmap(p_), "#SkyyInvTxM.Text"))
    # FIX (critic 1 #1): a FAILED row write is said on the panel and written again later (never a silent success)
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p4"))
    k4 = u6 + "-p4"
    blk_ = os.path.join(home, "tpblock")
    open(blk_, "wb").write(b"x")   # a FILE where the folder should be: every write fails
    ST.TPDIR = Paths.get(os.path.join(blk_, "invtp"))
    one(ev(PT, {"a": "txn"}), "INV6 FIX1 draw on profile 4")
    pgT.lastMoveAt = 0
    pgT.tslot = -1
    one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 FIX1 an add whose write fails")
    for _w in range(60):
        if ST.TPDIRTY.containsKey(k4):
            break
        _t6.sleep(0.05)
    p_ = one(ev(PT, {"a": "txn"}), "INV6 FIX1 redraw after the failed write")
    K.check(bool(ST.TPDIRTY.containsKey(k4)) and "not saved yet" in (sval(cmap(p_), "#SkyyInvTpNote.Text") or ""),
            "INV6 FIX1 a failed write: marked unsaved + the panel SAYS it (%s)" % sval(cmap(p_), "#SkyyInvTpNote.Text"))
    pgT.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 FIX1 a second add while unsaved")
    K.check("NOT SAVED" in (sval(cmap(p_), "#SkyyInvTxM.Text") or ""), "INV6 FIX1 an edit while unsaved says NOT SAVED (%s)" % sval(cmap(p_), "#SkyyInvTxM.Text"))
    ST.TPDIR = Paths.get(tpdir)
    ST.TPDIRTY.put(k4, JClass("java.lang.Long")(0))   # the 30 s retry gap has passed
    one(ev(PT, {"a": "txn"}), "INV6 FIX1 a redraw after the folder is writable again")
    f4 = os.path.join(tpdir, k4 + ".properties")
    want4 = {"slot.0": "tp:island", "slot.1": "tp:hub", "slot.2": "warp:dock", "slot.3": "warp:mines"}
    K.check(waitrow(f4, want4) == want4 and not ST.TPDIRTY.containsKey(k4), "INV6 FIX1 the retry WRITES the kept row (both edits) and clears the mark (%s)" % rowfile(f4, wait=False))
    # FIX (critic 1 #2 / critic 3 #2): a slot value this version does not know is KEPT in the file; bad text is dropped (warned)
    BR.put("profile:fn:key", Fn(lambda o: str(o) + "-p5"))
    f5 = os.path.join(tpdir, u6 + "-p5.properties")
    open(f5, "wb").write(b"_v=2\nslot.0=tp:island\nslot.1=home:base\nslot.2=warp:dock\nslot.4=a b c\n")
    p_ = one(ev(PT, {"a": "txn"}), "INV6 FIX2 draw a row with a newer key")
    rs_ = rowslots(p_)
    K.check(rs_ is not None and rs_[0] == "Island" and rs_[1] is None and rs_[2] is not None and rs_[4] is None, "INV6 FIX2 the unknown key shows as an empty slot (%s)" % rs_)
    pgT.lastMoveAt = 0
    pgT.tslot = -1
    one(ev(PT, {"a": "txg", "SlotIndex": 0}), "INV6 FIX2 an add on that row")
    want5 = {"slot.0": "tp:island", "slot.1": "home:base", "slot.2": "warp:dock", "slot.3": "tp:hub"}
    K.eq(waitrow(f5, want5), want5, "INV6 FIX2 the save KEEPS slot.1=home:base verbatim, the add (Hub, the first candidate) skips that slot, the bad text is dropped")
    BR.remove("profile:fn:key")
    p_ = one(ev(PT, {"a": "txd"}), "INV6 TP Done")
    K.check(str(pgT.mode) == "c" and "#SkyyInvCg.Slots" in cmap(p_) and sval(cmap(p_), "#SkyyInvTpE.Text") == "Edit", "INV6 TP Done = the craft panel again, the button Edit")
    p_ = one(ev(PT, {"a": "tp", "SlotIndex": 2}), "INV6 TP click a warp whose world is not loaded")
    K.check(not bool(pgT.closed) and "is not loaded" in cap_of(p_), "INV6 TP a warp in the row whose world is not loaded = a caption, the page stays (%s)" % cap_of(p_))
    WARPS.remove("dock")
    p_ = one(ev(PT, {"a": "cb:0"}), "INV6 TP redraw with dock removed")
    K.check("dock (gone)" in cmap(p_).get("#SkyyInvTp.Slots", ""), "INV6 TP a removed warp is drawn '(gone)', greyed")
    p_ = one(ev(PT, {"a": "tp", "SlotIndex": 2}), "INV6 TP click the removed warp")
    K.check(not bool(pgT.closed) and "was removed" in cap_of(p_), "INV6 TP a click on a removed warp = a caption (%s)" % cap_of(p_))
    pgT.shut()
    E.pump(PT)
    # ---- POCKET: Upgrades + Auto-compact
    CMP = {"st": "=1", "calls": [], "open": []}

    def f_pl6(o):
        return "ok|Mining|3|Rare|240|6720|1|tok6\nOre_Copper|128|0|5"

    def f_pk6(o):
        CMP["calls"].append((str(o[1]), str(o[2]), str(o[4]) if len(o) > 4 else None))
        return CMP["st"] if str(o[1]) == "cmpst" else "=Auto-compact paused for Mining - nothing compacts there until you turn it on"
    BR.put("sacks:fn:pocketList", Fn(f_pl6))
    BR.put("sacks:fn:pocket", Fn(f_pk6))
    pgP = ST.openPage(PT.ref, PT.st, PT.pr, "test")
    E.pump(PT)
    p_ = one(ev(PT, {"a": "pt:1"}), "INV6 POCKET without openPocket")
    K.check(sval(cmap(p_), "#SkyyInvPCm.Text") == "Auto-compact" and not [c_ for c_ in CMP["calls"] if c_[0] == "cmpst"], "INV6 POCKET without SkyySacks 0.8.39: the button says Auto-compact, no state call")
    p_ = one(ev(PT, {"a": "pcm"}), "INV6 POCKET Auto-compact without 0.8.39")
    K.check(not CMP["calls"] and "Void page" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""), "INV6 POCKET ... a click = a hint, no call")
    BR.put("sacks:fn:openPocket", Fn(lambda o: (CMP["open"].append((str(o[0]), str(o[1]))), TRUE)[1]))
    p_ = one(ev(PT, {"a": "ppn"}), "INV6 POCKET with 0.8.39")
    K.check(sval(cmap(p_), "#SkyyInvPCm.Text") == "Compact: On" and CMP["calls"][-1] == ("cmpst", "Mining", "tok6"), "INV6 POCKET the button reads the state (On) with the list's token")
    for st_, want_ in (("=0", "Compact: Off"), ("=b", "Compact: Buy"), ("=-", "Compact: None"), ("=x", "Compact: None")):
        CMP["st"] = st_
        K.eq(sval(cmap(one(ev(PT, {"a": "ppn"}), "INV6 POCKET state " + st_)), "#SkyyInvPCm.Text"), want_, "INV6 POCKET state %s -> %s" % (st_, want_))
    CMP["st"] = "=b"
    n0_ = len([c_ for c_ in CMP["calls"] if c_[0] == "cmp"])
    p_ = one(ev(PT, {"a": "pcm"}), "INV6 POCKET Auto-compact not bought")
    K.check(len([c_ for c_ in CMP["calls"] if c_[0] == "cmp"]) == n0_ and "Buy Auto-compact" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""), "INV6 POCKET not bought: a hint, NO toggle call (buying stays on the Void page)")
    CMP["st"] = "=1"
    pgP.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "pcm"}), "INV6 POCKET Auto-compact Pause")
    K.check([c_ for c_ in CMP["calls"] if c_[0] == "cmp"] == [("cmp", "Mining", "tok6")] and "paused for Mining" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""),
            "INV6 POCKET a click = ONE cmp call with the pocket + the list's token, the answer shown")
    p_ = one(ev(PT, {"a": "pcm"}), "INV6 POCKET the same click again")
    K.eq(len([c_ for c_ in CMP["calls"] if c_[0] == "cmp"]), 1, "INV6 POCKET a double click within 1.5 s = one toggle")
    # FIX (critic 2 #2): the list answered WITHOUT a profile token -> the toggle is refused (never toggles whichever profile is settled now)
    BR.put("sacks:fn:pocketList", Fn(lambda o: "ok|Mining|3|Rare|240|6720|1|\nOre_Copper|128|0|5"))
    one(ev(PT, {"a": "ppn"}), "INV6 FIX POCKET redraw without a token")
    pgP.lastMoveAt = 0
    p_ = one(ev(PT, {"a": "pcm"}), "INV6 FIX POCKET Auto-compact without a token")
    K.check(len([c_ for c_ in CMP["calls"] if c_[0] == "cmp"]) == 1 and "not settled" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""),
            "INV6 FIX POCKET no profile token = NO cmp call, a hint (%s)" % sval(cmap(p_), "#SkyyInvPr.Text"))
    BR.put("sacks:fn:pocketList", Fn(f_pl6))
    one(ev(PT, {"a": "ppn"}), "INV6 FIX POCKET redraw with the token again")
    p_ = one(ev(PT, {"a": "pup"}), "INV6 POCKET Upgrades")
    K.check(CMP["open"] == [(u6, "Mining")], "INV6 POCKET Upgrades = ONE sacks:fn:openPocket with the pocket (%s)" % CMP["open"])
    for k_ in ("sacks:fn:pocketList", "sacks:fn:pocket", "sacks:fn:openPocket"):
        BR.remove(k_)
    pgP.shut()
    E.pump(PT)
"""
T.rep('''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''', HARNESS_INV6 + '''    # the plain mode (no SkyySacks): the vanilla pocket list + CraftingManager.craftItem itself
''')
if T.dst:
    T.finish()
