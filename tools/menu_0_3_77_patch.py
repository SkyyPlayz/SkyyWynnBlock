"""Derive SkyyMenu/build_skyymenu_0.3.77.py + SkyyMenu/test_skyymenu_0.3.77.py from the SET pin SkyyMenu 0.3.76 (generated - never re-run
its patch). Run:  python tools/menu_0_3_77_patch.py   then   python SkyyMenu/build_skyymenu_0.3.77.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.77.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyyAccessories 0.5.39 (tools/accessories_0_5_39_patch.py: acc:fn:charms vc:power / vc:pick) for the
Power tab; with 0.5.38 the tab says it needs 0.5.39 (the Bag grid, the craft rows and everything else work as 0.3.76).

0.3.77 (2026-11-24, round oldmenu9) = THE LAST OLD-MENU ROWS. Skyy's words (docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when
everything is in the new system id like to disable the old menu compleatly, so instead of adding things like the full tree button, just build it
all into the new system and remove the old "Full tree""; 2026-11-24 "keep building". OLD_LEFT held character:trees, character:accessories,
storage:pocket, smithing:recipes and settings:setup (Server Setup, kept on purpose). Every new-screen link to the first four is gone:
  character:accessories  THE CHARM ROWS' 'Bag' (vbag = the full Void Charms page) is now the BAG GRID inside the inventory (the 0.3.54 'v' panel:
      vc:list / tier / take / put - the old page's Bag tab), its Done = back to the rows; the rows got a fourth sub-tab POWER (the old page's Power
      tab) = SkyyAccessories 0.5.39 vc:power (AP, the Power that works now, every visible Power: group, lock, what it gives at your AP) + Pick =
      ONE vc:pick "<id>|<the Power the tab showed as yours>" with the rows' profile key (SkyyAccessories refuses with '=' when your Power changed
      since the drawing - the redraw shows the new one, the same press again runs; '-' locked / the wait / off; a null = 'could not do that here').
      Only buttons the drawing showed run (vpow[k], else 'Nothing to pick on that row', no call); a double click = no second call. Without
      acc:fn:charms (SkyyAccessories older than 0.5.37) the Void Charms buttons (inventory + skill page) say so - no old page.
  storage:pocket  the Void tab without SkyySacks 0.8.38's pocket bridge, Upgrades without 0.8.39's sacks:fn:openPocket = a caption naming the
      version (pure fallbacks); the dead 'pkv' handler is gone. (Upgrades WITH 0.8.39 still opens SkyySacks' own Void page on that pocket - a
      SkyySacks page, not a SkyyMenu link: the pocket upgrade shop in the screen needs a SkyySacks buy op - follow-up.)
  smithing:recipes  the Tanning tab / Full page without sacks:fn:openTannery = a caption naming SkyySacks 0.8.38 (pure fallback).
  character:trees  the skill page's Open tree without SkyyTrees (no tree:<uuid> key or no /tree) = a caption naming SkyyTrees 0.6.10; a skill
      without a tree = said; the Right now tree row when the skill page cannot open = a caption (pure fallbacks; the inline tree is 0.3.61's).
New: no class / command / system / picture / lang key / setting / saved data. 3 fields on InvPage (vbag, vpow, vpowCur). The charm tabs 104 -> 84 px
and the count label 110 -> 92 px (four tabs fit the header).
OLD_LEFT: 5 -> 3 (fix pass): character:accessories + character:trees gone; storage:pocket (Upgrades = sacks:fn:openPocket, SkyySacks' Void page)
and smithing:recipes (the Tanning panel's Full page = sacks:fn:openTannery, SkyySacks' Tannery page) stay as tracked live doors with a follow-up
note at OLD_LEFT; settings:setup = Server Setup for admins, on purpose. Fix pass also: Open tree without the inline tree never runs /tree (a
caption); the Power tab names 0.5.39 on the real 0.5.38 answer ('-Your profile changed', its key gate); a Pick refused with '=' re-arms at once.
ROLLBACK to 0.3.76: safe alone (nothing saved; the Bag / Trees / Void / Tannery links come back). SkyyAccessories 0.5.39 rolls back alone (the Power
tab then names 0.5.39).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.76.py"), os.path.join(MOD, "build_skyymenu_0.3.77.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.76.py"), os.path.join(MOD, "test_skyymenu_0.3.77.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.76"\n') and P.has("OLD_LEFT = sorted(set([") and P.has('MT + "Kv"') and not P.has('"vc:power"'), "not the generated SkyyMenu 0.3.76 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.76: OLD MENU FOLLOW-UP - THE BANK VIEW''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.77: THE LAST OLD-MENU ROWS: the charm rows' Bag = the bag grid in the inventory (Done = back to the rows), a fourth sub-tab POWER
       (SkyyAccessories 0.5.39 vc:power / vc:pick: AP, your Power, every Power with its lock + stats, Pick with the shown Power checked); the Void /
       Upgrades / Tannery / Trees / Void Charms fallbacks (an older or missing bridge mod) = a caption naming the version, no old page; the pkv
       handler gone; Open tree never /tree. OLD_LEFT 5 -> 3 (Upgrades + the Tanning Full page = tracked SkyySacks doors, Server Setup stays; notes: tools/menu_0_3_77_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.77.py.
0.3.76: OLD MENU FOLLOW-UP - THE BANK VIEW''')
P.rep('VERSION = "0.3.76"\n', 'VERSION = "0.3.77"\n')

# ======================================================================= the charm rows: four tabs (+ Power); the Bag text
P.rep('''IV_WRN, IV_WRH, IV_WIS = 5, 40, 36     # 0.3.60: the charm rows - rows a page, row height, icon cell
IV_WF_BTN = "TextButton #SkyyInvWf{I} { Anchor: (Width: 104, Height: 30, Right: 4); {S} }"
IV_TXT["wHelp"] = "Craft or upgrade a charm here - it goes straight into Void Charms. Bag = the full Void Charms page."''',
      '''IV_WRN, IV_WRH, IV_WIS = 5, 40, 36     # 0.3.60: the charm rows - rows a page, row height, icon cell
IV_WF_W, IV_WF_SLOT, IV_WXI_W = 84, 88, 92   # 0.3.77: four sub-tabs (+ Power): a tab 104 -> 84 (+ 4 gap), the count label 110 -> 92
IV_WF_BTN = "TextButton #SkyyInvWf{I} { Anchor: (Width: %d, Height: 30, Right: 4); {S} }" % IV_WF_W
IV_TXT["wHelp"] = "Craft or upgrade a charm - it goes into Void Charms. Bag = the charms you have in, Power = your Accessory Power."
for _n in ("Benches", "Combat", "Gathering", "Power"):
    assert SUI.text_width(_n, 14, bold=True) <= IV_WF_W - 10, ("0.3.77: a charm tab fits", _n)
assert SUI.text_width("AP 99999", 12) <= IV_WXI_W and SUI.text_width("99 charms", 12) <= IV_WXI_W, "0.3.77: the count label fits"
assert IV_WF_SLOT == IV_WF_W + 4 and SUI.text_width(IV_TXT["wHelp"], 11) <= IV_COL_M - 20, "0.3.77: the tab slot + the help line fit"''')
P.rep('''    ap.append(("#" + wa, G_.glass_group(IV + "WfB", 3 * 108, 32, layout="Left")))
    ap.append(("#" + wa, lab(IV + "WxI", "", 12, "gold", w=110, h=30, anchor={"left": 4})))
    sp = pw - 3 * 108 - 4 - 110 - 32 - 50 - 32 - 6 - 60 - 6 - 64''', '''    ap.append(("#" + wa, G_.glass_group(IV + "WfB", 4 * IV_WF_SLOT, 32, layout="Left")))   # 0.3.77: + the Power tab
    ap.append(("#" + wa, lab(IV + "WxI", "", 12, "gold", w=IV_WXI_W, h=30, anchor={"left": 4})))
    sp = pw - 4 * IV_WF_SLOT - 4 - IV_WXI_W - 32 - 50 - 32 - 6 - 60 - 6 - 64''')
P.rep('''    assert sp >= 0, ("0.3.60: the charm rows header fits", sp)''', '''    assert sp >= 0, ("0.3.60: the charm rows header fits", sp)
    assert sp >= 0, ("0.3.77: the charm rows header fits four tabs", sp)''')

# ======================================================================= the Java: fields, the probe, the tabs, THE POWER TAB, the rows
P.rep('''# ---- 0.3.60: THE CHARM ROWS ('w'): acc:fn:charms vc:rows (SkyyAccessories 0.5.38) = the Craft tab's rows; vc:craft = its button (before build)
M(ipg, r"""
public boolean charmRowsOk() {
  if (this.vsub < 0 || this.vsub > 2) this.vsub = 0;
  Object o = call("acc:fn:charms", new Object[] { "vc:rows", this.playerRef.getUuid(), "", String.valueOf(this.vsub) });
  boolean ok = o instanceof String && !((String) o).startsWith("-");
  this.vprobe = ok ? (String) o : null;   // the panel's first fill reuses this answer (one vc:rows read per open, not two)
  return ok;
}""")''', '''# 0.3.77 (oldmenu9): vbag = the Bag grid ('v') was asked for from the rows (no switch to the rows); vpow = the Power ids the drawing showed a
# Pick button for (per row); vpowCur = the Power the drawing showed as yours (vc:pick sends it - never a value the player did not see)
F(ipg, "public boolean vbag;")
F(ipg, "public String[] vpow;")
F(ipg, "public String vpowCur;")
# ---- 0.3.60: THE CHARM ROWS ('w'): acc:fn:charms vc:rows (SkyyAccessories 0.5.38) = the Craft tab's rows; vc:craft = its button (before build)
M(ipg, r"""
public boolean charmRowsOk() {
  if (this.vsub < 0 || this.vsub > 3) this.vsub = 0;   // 0.3.77: 3 = the Power tab (the probe asks the Benches rows; its answer is not reused there)
  int sb = this.vsub == 3 ? 0 : this.vsub;
  Object o = call("acc:fn:charms", new Object[] { "vc:rows", this.playerRef.getUuid(), "", String.valueOf(sb) });
  boolean ok = o instanceof String && !((String) o).startsWith("-");
  this.vprobe = ok && this.vsub != 3 ? (String) o : null;   // the panel's first fill reuses this answer (one vc:rows read per open, not two)
  return ok;
}""")
# 0.3.77: the four sub-tabs (Benches | Combat | Gathering = SkyyAccessories' Craft tabs, Power = its Power tab), the open one selected
M(ipg, r"""
public void charmTabs(@UCB@ b, @UEB@ ev, String[] names) {
  for (int i = 0; i < 4; i++) {
    b.appendInline("#SkyyInvWfB", @PKG@.InvData.WF_BTN.replace("{I}", String.valueOf(i)).replace("{S}", i == this.vsub ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvWf" + i + ".Text", @PKG@.MenuUtil.clip(i == 3 ? "Power" : names[i], 12));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvWf" + i, @EVD@.of("a", "vf:" + i));
  }
}""")
# 0.3.77 (oldmenu9): THE POWER TAB (the old Void Charms page's Power tab) = SkyyAccessories 0.5.39 vc:power, drawn on the rows panel's own
# elements: the name (+ YOURS / LOCKED), the group + what it gives at your AP (green = yours), Pick only on a free Power that is not yours
M(ipg, r"""
public void fillPower(@UCB@ b, @UEB@ ev) {
  String[] ls = lines("acc:fn:charms", new Object[] { "vc:power", this.playerRef.getUuid(), "", "" });
  String err = null;
  String head = "";
  String help = "";
  boolean on = false;
  java.util.ArrayList rows = new java.util.ArrayList();
  this.vpowCur = null;
  if (ls == null) err = "Void Charms is not on this server right now";
  else if (ls[0].indexOf("does not know") >= 0 || ls[0].startsWith("-Your profile changed")) err = "Power here needs SkyyAccessories 0.5.39 - /charms power works on this server";   // fix: 0.5.38 answers a keyless vc:power with its key gate ('-Your profile changed') - 0.5.39 reads vc:power keyless, so that answer = an older SkyyAccessories
  else if (!ls[0].startsWith("ok|")) err = ls[0].startsWith("off|") ? ls[0].substring(4) : bare(ls[0]);
  else {
    String[] h = ls[0].split("\\\\|", -1);
    if (h.length < 9) err = "Void Charms did not answer";
    else {
      if (this.vkey != null && !h[6].equals(this.vkey) && this.vnote.length() == 0) this.vnote = "Your profile changed - this is its Power now";
      this.vkey = h[6];
      this.vpowCur = h[3];
      on = "1".equals(h[5]);
      head = "AP " + h[1];
      int wl = toInt(h[4], 0);
      if (!on) help = "Accessory Powers are switched off on this server";
      else if (wl > 0) help = "You can switch your Power again in " + wl + " s";
      else help = "Pick a Power - your Accessory Power (AP " + h[1] + ", x" + h[2] + ") becomes its stats. " + h[8] + " s between switches.";
      for (int i = 1; i < ls.length; i++) {
        String[] f = ls[i].split("\\\\|", -1);
        if (f.length >= 8 && f[0].equals("p")) rows.add(f);
      }
    }
  }
  charmTabs(b, ev, new String[] { "Benches", "Combat", "Gathering" });
  int per = @PKG@.InvData.WRN;
  int np = rows.size() == 0 ? 1 : (rows.size() + per - 1) / per;
  if (this.vpage >= np) this.vpage = np - 1;
  if (this.vpage < 0) this.vpage = 0;
  this.vpow = new String[per];
  this.vrows = new String[per];   // no craft row on the Power tab
  int nr = @PKG@.InvData.VRAR.length;
  String[] grp = new String[] { "Combat", "Combat 15", "Gathering" };
  for (int k = 0; k < per; k++) {
    int at = this.vpage * per + k;
    if (at >= rows.size()) { b.set("#SkyyInvWr" + k + ".Visible", false); continue; }
    String[] f = (String[]) rows.get(at);
    boolean mine = "1".equals(f[7]);
    boolean locked = f[5].length() > 0;
    int g = toInt(f[4], 0);
    String gn = g >= 0 && g < 3 ? grp[g] : "Power";
    String nm = f[3] + (mine ? "  -  YOURS" : (locked ? "  -  LOCKED" : ""));
    String st = gn + "  -  " + (locked ? "Locked: " + f[5] : f[6]);
    java.util.ArrayList one = new java.util.ArrayList();
    @IGS@ gs = new @IGS@();
    gs.setName(f[3]);
    gs.setDescription(gn + " Power" + String.valueOf((char) 10) + f[6] + (locked ? String.valueOf((char) 10) + "Locked: " + f[5] : ""));
    one.add(gs);
    b.set("#SkyyInvWi" + k + ".Slots", act(one));
    for (int j = 0; j <= nr; j++) {
      b.set("#SkyyInvWn" + k + "v" + j + ".Text", @PKG@.MenuUtil.clip(nm, 60));
      b.set("#SkyyInvWn" + k + "v" + j + ".Visible", j == 0);
    }
    for (int j = 0; j < 2; j++) {
      b.set("#SkyyInvWs" + k + "v" + j + ".Text", @PKG@.MenuUtil.clip(st, 96));
      b.set("#SkyyInvWs" + k + "v" + j + ".Visible", (j == 1) == mine);
    }
    boolean btn = on && !mine && !locked && f[2].length() > 0 && f[2].length() <= 40;
    b.set("#SkyyInvWb" + k + ".Visible", btn);
    if (btn) b.set("#SkyyInvWb" + k + ".Text", "Pick");
    this.vpow[k] = btn ? f[2] : null;
  }
  b.set("#SkyyInvWxI.Text", head);
  b.set("#SkyyInvWxPn.Text", (this.vpage + 1) + " / " + np);
  b.set("#SkyyInvWxM.Text", @PKG@.MenuUtil.clip(this.vnote.length() > 0 ? this.vnote : (err != null ? err : help), 110));
  this.vnote = "";
}""")''')
P.rep('''public void fillCharmRows(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  if (this.vsub < 0 || this.vsub > 2) this.vsub = 0;''', '''public void fillCharmRows(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  if (this.vsub < 0 || this.vsub > 3) this.vsub = 0;
  if (this.vsub == 3) { this.vprobe = null; fillPower(b, ev); return; }   // 0.3.77 (oldmenu9): the Power tab''')
P.rep('''  for (int i = 0; i < 3; i++) {
    b.appendInline("#SkyyInvWfB", @PKG@.InvData.WF_BTN.replace("{I}", String.valueOf(i)).replace("{S}", i == this.vsub ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvWf" + i + ".Text", @PKG@.MenuUtil.clip(names[i], 12));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvWf" + i, @EVD@.of("a", "vf:" + i));
  }
  int per = @PKG@.InvData.WRN;''', '''  charmTabs(b, ev, names);   // 0.3.77: + the Power tab
  int per = @PKG@.InvData.WRN;''')
P.rep('''  if ("v".equals(this.mode) && charmRowsOk()) this.mode = "w";   // 0.3.60: the charm ROWS (SkyyAccessories 0.5.38), else the 0.3.59 grid''',
      '''  if ("v".equals(this.mode) && !this.vbag && charmRowsOk()) this.mode = "w";   // 0.3.60: the charm ROWS (SkyyAccessories 0.5.38), else the 0.3.59 grid; 0.3.77: Bag = the grid''')

# ======================================================================= the skill page: Void Charms + Open tree fallbacks (no old hub)
P.rep('''      if (@PKG@.InvCraft.fn("acc:fn:charms") == null) { hub("character", "accessories", "Void Charms"); return; }
      toInv("v", -1);''', '''      if (@PKG@.InvCraft.fn("acc:fn:charms") == null) { say("Void Charms needs SkyyAccessories 0.5.37 - it is not on this server right now"); return; }   // 0.3.77: no old page
      toInv("v", -1);''')
P.rep('''public void openTree() {
  int si = idx(this.skill);
  String tn = si >= 0 ? @PKG@.SkillData.TREE[si] : this.skill;
  Object o = null;
  try { o = @PKG@.MenuUtil.bridge().get("tree:" + this.playerRef.getUuid().toString()); } catch (Throwable t) { o = null; }
  boolean has = false;
  if (o instanceof String) {
    String[] es = ((String) o).split(",");
    for (int i = 0; i < es.length; i++) { int c = es[i].indexOf(':'); if (c > 0 && es[i].substring(0, c).trim().equalsIgnoreCase(tn)) has = true; }
  }
  if (!has || @PKG@.MenuUtil.cmd("tree") == null) { hub("character", "trees", "Trees"); return; }
  this.answered = true;
  try { @CMGR@.get().handleCommand(this.playerRef, "tree " + tn.toLowerCase()); } catch (Throwable t) { @PKG@.MenuUtil.warn("skill page: /tree " + tn + " failed: " + t); }
  if (!still()) { finish("tree"); return; }
  say("Opening the " + tn + " tree");
}''', '''public void openTree() {
  // 0.3.77 (oldmenu9 + fix): reached only WITHOUT the inline tree (SkyyTrees 0.6.10 tree:fn:map) - a caption, never the old Trees hub and never
  // /tree (SkyyTrees' own page = the old Trees page; Skyy 11-22 "remove the old Full tree")
  int si = idx(this.skill);
  String tn = si >= 0 ? @PKG@.SkillData.TREE[si] : this.skill;
  if (@PKG@.InvCraft.fn("tree:fn:map") == null || @PKG@.InvCraft.fn("tree:fn:act") == null) { say("Skill trees need SkyyTrees 0.6.10 - they are not on this server right now"); return; }
  say("Your " + tn + " tree could not be drawn here right now - try again");
}''')

# ======================================================================= the inventory: Tannery / pockets / Right now tree fallbacks
P.rep('''  openHub("smithing", "recipes", "the Crafting page - pick its Tannery tab");
}""")''', '''  say(f == null ? "The Tannery needs SkyySacks 0.8.38 - it is not on this server right now" : "The Tannery could not open right now - try again");   // 0.3.77: no old Crafting page
}""")''')
P.rep('''  if (f == null) { openHub("storage", "pocket", "the Void"); return; }''',
      '''  if (f == null) { say("Pocket upgrades need SkyySacks 0.8.39 - they are not on this server right now"); return; }   // 0.3.77: no old Void page''')
P.rep('''  if (@PKG@.InvCraft.fn("sacks:fn:openPocket") == null) { this.pnote = "Auto-compact is set on the Void page on this server"; redraw(); return; }''',
      '''  if (@PKG@.InvCraft.fn("sacks:fn:openPocket") == null) { this.pnote = "Auto-compact here needs SkyySacks 0.8.39 - it is not on this server right now"; redraw(); return; }''')
P.rep('''    openHub("character", "trees", "your trees");
    return;''', '''    say("Your " + tab + " tree could not open here - pick its skill on the Skills tab");   // 0.3.77: no old Trees hub
    return;''')
P.rep('''  if (!this.pkOn) { openHub("storage", "pocket", "the Void"); return; }''',
      '''  if (!this.pkOn) { say("The Void pockets need SkyySacks 0.8.38 - they are not on this server right now"); return; }   // 0.3.77: no old Void page''')
P.rep('''public void openCharms() {
  if (@PKG@.InvCraft.fn("acc:fn:charms") == null) { openHub("character", "accessories", "Void Charms"); return; }
  this.mode = "v";''', '''public void openCharms() {
  if (@PKG@.InvCraft.fn("acc:fn:charms") == null) { say("Void Charms needs SkyyAccessories 0.5.37 - it is not on this server right now"); return; }   // 0.3.77: no old page
  this.vbag = false;   // 0.3.77: Void Charms opens the rows (Bag = the grid)
  this.mode = "v";''')
# ======================================================================= Pick on the Power tab (a row's button; the same vr:<k> binding)
P.rep('''# a row's Craft / Upgrade = vc:craft with the drawn recipe id and the list's profile key (SkyyAccessories re-checks the line's next step,
# the lock, the materials and a free slot - an old row / a double click uses nothing); the same row within 1.5 s = no second call
M(ipg, r"""
public void charmRow(int k) {
''', '''# 0.3.77 (oldmenu9): Pick on the Power tab = ONE vc:pick "<the row's Power id>|<the Power the drawing showed as yours>" with the rows' profile
# key; only a row the drawing gave a Pick button (vpow); the same Power within 1.5 s = no second call; '=' (your Power changed since the drawing)
# / '-' / '+' = the answer line + ONE redraw (a new read: the next press carries the new Power)
M(ipg, r"""
public void powerPick(int k) {
  if (this.vpow == null || k < 0 || k >= this.vpow.length || this.vpow[k] == null) { this.vnote = "Nothing to pick on that row"; redraw(); return; }
  if (this.vkey == null || this.vkey.length() == 0) { this.vnote = "Your profile is not settled yet - try again in a moment"; redraw(); return; }
  String key = "vp:" + this.vpow[k];
  if (dup(key)) { this.vnote = this.vlast.length() > 0 ? this.vlast : "Double click ignored - wait a moment to click again"; redraw(); return; }
  moved(key);
  String r = vcAct("vc:pick", this.vpow[k] + "|" + (this.vpowCur == null ? "" : this.vpowCur));
  if (r != null && r.startsWith("=")) this.lastMove = null;   // fix: '=' (changed since the drawing) did nothing - the same press again (now with the redrawn Power) runs at once
  this.vlast = bare(r);
  this.vnote = this.vlast;
  redraw();
}""")
# a row's Craft / Upgrade = vc:craft with the drawn recipe id and the list's profile key (SkyyAccessories re-checks the line's next step,
# the lock, the materials and a free slot - an old row / a double click uses nothing); the same row within 1.5 s = no second call
M(ipg, r"""
public void charmRow(int k) {
  if (this.vsub == 3) { powerPick(k); return; }   // 0.3.77: the Power tab
''')
P.rep('''    if (a.equals("pkc")) { say("You are on Craft"); return; }
    if (a.equals("pkv")) { openHub("storage", "pocket", "the Void"); return; }
''', '''    if (a.equals("pkc")) { say("You are on Craft"); return; }   // 0.3.77 (oldmenu9): the dead 'pkv' (the old Void page) is gone
''')
P.rep('''    if (a.startsWith("vf:")) { int k = toInt(a.substring(3), 0); this.vsub = k < 0 || k > 2 ? 0 : k; this.vpage = 0; this.vnote = ""; redraw(); return; }   // 0.3.60''',
      '''    if (a.startsWith("vf:")) { int k = toInt(a.substring(3), 0); this.vsub = k < 0 || k > 3 ? 0 : k; this.vpage = 0; this.vnote = ""; redraw(); return; }   // 0.3.60; 0.3.77: 3 = Power''')
P.rep('''    if (a.equals("vbag")) { openHub("character", "accessories", "Void Charms"); return; }   // 0.3.60: the full Void Charms page''',
      '''    if (a.equals("vbag")) { this.vbag = true; this.mode = "v"; this.vpage = 0; this.vsel = null; this.vnote = ""; redraw(); return; }   // 0.3.77: Bag = the bag grid here (was the old Void Charms page)''')
P.rep('''    if (a.equals("vcd")) { this.mode = "c"; redraw(); return; }''',
      '''    if (a.equals("vcd")) {   // 0.3.77: Done in the Bag grid (opened from the rows) = back to the rows; else the craft panel
      if (this.vbag && "v".equals(this.mode)) { this.vbag = false; this.vpage = 0; this.vnote = ""; redraw(); return; }
      this.vbag = false;
      this.mode = "c";
      redraw();
      return;
    }''')

# ======================================================================= the ratchet: OLD_LEFT shrinks by the rows this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"),
    ("storage", "pocket"),
    ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.77 (oldmenu9): character:accessories (the charm rows' Bag = the bag grid in the inventory; + the Power tab = SkyyAccessories 0.5.39 vc:power /
# vc:pick) and character:trees (Open tree without the inline tree = a caption, never /tree) are gone. Their pure fallbacks for an older SkyySacks
# (the Void tab, Upgrades, the Tanning tab) are captions now, but TWO LIVE DOORS still open the same old pages through SkyySacks' bridge (the
# OLD1 SCAN counts them): storage:pocket = the pocket panel's Upgrades (sacks:fn:openPocket = SkyySacks' Void page on that pocket) - FOLLOW-UP: a
# SkyySacks op 'sacks:fn:pocket' (view: upgrade tiers + prices + Auto-compact state; buy / buy-compact with page token + profile key, '=' when
# the price or tier changed since the drawing, a coin-conservation harness) and the upgrade shop as a pocket-panel view; smithing:recipes = the
# Tanning panel's Full page (sacks:fn:openTannery = SkyySacks' Crafting > Tannery page) - FOLLOW-UP: whatever that page does beyond the
# 0.3.56 Tanning panel (sacks:fn:furn) as a panel view, then drop Full page. Server Setup (admins) stays on purpose.
OLD_LEFT = sorted(set([
    ("storage", "pocket"),
    ("settings", "setup"), ("smithing", "recipes")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.77: no system / command / class"
_i = P.s.index
assert _i("public String[] lines(String key, Object arg) {\n  Object o = call(key, arg);") < _i("public void charmTabs(@UCB@ b, @UEB@ ev, String[] names)") \
    < _i("public void fillPower(@UCB@ b, @UEB@ ev)") < _i("public void fillCharmRows(@UCB@ b, @UEB@ ev)"), "0.3.77: the tabs + the Power tab before fillCharmRows"
assert _i('F(ipg, "public String vpowCur;")') < _i("public void fillPower(@UCB@ b, @UEB@ ev)"), "0.3.77: the fields before their users"
assert _i("public String vcAct(String op, String arg)") < _i("public void powerPick(int k)") < _i("public void charmRow(int k)"), "0.3.77: powerPick before charmRow"
_new = P.s[P.s.index("# ================= 0.3.50 THE INVENTORY SCREEN"):P.s.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")]
for _old in ('hub("character", "trees"', 'hub("character", "accessories"', 'hub("storage", "pocket"', 'hub("smithing", "recipes"', 'a.equals("pkv")',
             "the Crafting page - pick its Tannery tab", "the full Void Charms page", "on the Void page", 'handleCommand(this.playerRef, "tree "'):
    assert _old not in _new, "0.3.77: no old link left: " + _old
# fix: the two live SkyySacks doors to old pages (Upgrades, the Tanning Full page) stay tracked in OLD_LEFT (the OLD1 SCAN counts them)
assert _new.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openPocket");') == 1 \
    and _new.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openTannery");') == 1, "0.3.77: one Upgrades door, one Tannery door"
P.finish()

# ======================================================================= the HARNESS (every 0.3.76 check runs again on the 0.3.77 jar, plus OLD9)
HARNESS_OLD9_STATIC = r'''    # ---- OLD9 (0.3.77; Skyy 11-22 "build it all into the new system", 11-24 "keep building"): the ratchet lost the last four rows
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    K.check(lefto_ - left2_ == set([("character", "trees"), ("character", "accessories")])
            and left2_ == set([("settings", "setup"), ("storage", "pocket"), ("smithing", "recipes")]),
            "OLD9 RATCHET OLD_LEFT lost character:trees + character:accessories; left = Server Setup (on purpose) + the tracked SkyySacks doors storage:pocket / smithing:recipes (%d -> %d: %s)"
            % (len(lefto_), len(left2_), sorted(left2_)))
    nwd_ = g[g.index("# ================= 0.3.50 THE INVENTORY SCREEN"):g.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")]
    K.check(nwd_.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openPocket");') == 1 and nwd_.count('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openTannery");') == 1
            and 'handleCommand(this.playerRef, "tree "' not in nwd_ and "FOLLOW-UP: a" in g and "SkyySacks op 'sacks:fn:pocket'" in g,
            "OLD9 FIX RATCHET the live old-page doors (Upgrades = openPocket, the Tanning Full page = openTannery) are one each and tracked with a follow-up; no /tree left in the new screens")
    nw9_ = g[g.index("# ================= 0.3.50 THE INVENTORY SCREEN"):g.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")]
    K.check(all(x_ not in nw9_ for x_ in ('hub("character", "trees"', 'hub("character", "accessories"', 'hub("storage", "pocket"', 'hub("smithing", "recipes"',
                                          'a.equals("pkv")', "the Crafting page - pick its Tannery tab", "the full Void Charms page", "on the Void page")),
            "OLD9 STATIC no Trees / Void Charms / Void / Crafting page link or text left in the new screens; the dead 'pkv' handler is gone")
    K.check('if (a.equals("vbag")) { this.vbag = true; this.mode = "v";' in g and 'if ("v".equals(this.mode) && !this.vbag && charmRowsOk()) this.mode = "w";' in g
            and '"vc:power", this.playerRef.getUuid(), "", ""' in g and 'vcAct("vc:pick", this.vpow[k] + "|" + (this.vpowCur == null ? "" : this.vpowCur))' in g
            and "ScheduledFuture vp" not in g,
            "OLD9 STATIC Bag = the bag grid in the inventory; the Power tab reads vc:power and picks with vc:pick <id>|<the shown Power> (no timer)")
    K.check(all(("0.3.77: %s" % t_) in g for t_ in ("a charm tab fits", "the count label fits", "the tab slot + the help line fit", "the charm rows header fits four tabs")),
            "OLD9 STATIC the build asserts the four charm tabs, the count label and the help line fit")
'''

SCAN_OLD = r'''    links_ = sorted(set(re.findall(r'(?:openHub|hub)\("([a-z]+)", "([a-z]+)"', g[i_new_:i_end_])
                        + re.findall(r'opener\("[a-z:]+", new Object\[\] \{[^}]*\}, "([a-z]+)", "([a-z]+)"', g[i_new_:i_end_])))   # 0.3.70: + opener links (the AH)
'''
SCAN_ADD = r'''    # 0.3.77 fix: + the live SkyySacks doors to the same old pages (Upgrades = SkyySacks' Void page, the Tanning Full page = its Crafting > Tannery page)
    links_ = sorted(set(links_ + [hk_ for dk_, hk_ in (('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openPocket");', ("storage", "pocket")),
                                                       ('java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:openTannery");', ("smithing", "recipes")))
                                  if dk_ in g[i_new_:i_end_]]))
'''

HARNESS_OLD9_FALL = r'''    # ---- OLD9 (0.3.77): the old-page fallbacks are captions (no old Void page)
    p_ = one(ev(PK, {"a": "pt:1"}), "OLD9 FALL the Void tab without SkyySacks 0.8.38")
    K.check("need SkyySacks 0.8.38" in cap_of(p_) and PK.pm.getCustomPage() == pg and str(pg.mode) == "c",
            "OLD9 FALL the Void tab without the pocket bridge = a caption naming SkyySacks 0.8.38, the page stays (%s)" % cap_of(p_))
    p_ = one(ev(PK, {"a": "pkv"}), "OLD9 FALL a forged pkv")
    K.check(PK.pm.getCustomPage() == pg and "Opening" not in cap_of(p_), "OLD9 FALL the old 'pkv' click opens nothing (the handler is gone) (%s)" % cap_of(p_))
'''

HARNESS_OLD9_POCKET = r'''    p_ = one(ev(PT, {"a": "pup"}), "OLD9 FALL Upgrades without SkyySacks 0.8.39")
    K.check(not CMP["open"] and "need SkyySacks 0.8.39" in cap_of(p_) and PT.pm.getCustomPage() == pgP,
            "OLD9 FALL Upgrades without sacks:fn:openPocket = a caption naming SkyySacks 0.8.39, the page stays (%s)" % cap_of(p_))
'''

HARNESS_OLD9_SKILL = r'''    K.check(cur_ == SP and "need SkyyTrees 0.6.10" in str(sval(cmap(p_), "#SkyySkpCap.Text")),
            "TAB1 ACT Open tree without /tree = (0.3.77) a caption naming SkyyTrees 0.6.10, the page stays - never the old Trees hub (%s)" % sval(cmap(p_), "#SkyySkpCap.Text"))
    if BR.get("acc:fn:charms") is None:
        p9_ = sk_ev({"a": "vc"}, "OLD9 FALL the skill page's Void Charms without SkyyAccessories 0.5.37")
        K.check(PK.pm.getCustomPage() == SP and "needs SkyyAccessories 0.5.37" in str(sval(cmap(p9_), "#SkyySkpCap.Text")),
                "OLD9 FALL the skill page's Void Charms without acc:fn:charms = a caption naming SkyyAccessories 0.5.37, the page stays (%s)" % sval(cmap(p9_), "#SkyySkpCap.Text"))
    else:
        K.check(False, "OLD9 FALL the skill page test expected no acc:fn:charms here")
'''

HARNESS_OLD9 = r'''    # ---- OLD9 (0.3.77): Bag = the bag grid INSIDE the inventory (was the old Void Charms page); Done = back to the rows
    n9_ = len(CRW["calls"])
    p_ = one(ev(PK, {"a": "vbag"}), "OLD9 BAG Bag")
    cm = cmap(p_) if p_ else {}
    K.check(PK.pm.getCustomPage() == pg and str(pg.mode) == "v" and bool(pg.vbag) and "#SkyyInvVxG.Slots" in cm and "#SkyyInvWxM.Text" not in cm
            and len(CRW["calls"]) == n9_ and nometa(p_),
            "OLD9 BAG Bag = the charms grid inside the inventory (vc:list - the old page's Bag tab), the page stays, no old Void Charms page, no act")
    p_ = one(ev(PK, {"a": "vcd"}), "OLD9 BAG Done in the grid")
    K.check(str(pg.mode) == "w" and not bool(pg.vbag) and "#SkyyInvWxM.Text" in cmap(p_), "OLD9 BAG Done in the grid = back to the charm rows (not the craft panel)")
    # ---- OLD9 POWER: the fourth sub-tab = SkyyAccessories 0.5.39 vc:power / vc:pick (stand-in = tools/accessories_0_5_39_patch.py's contract)
    POW9 = [("Tank", "Tank", 0, ""), ("Balance", "Balance", 0, ""), ("Slayer", "Slayer", 0, ""), ("Lucky", "Lucky", 0, ""), ("Magical", "Magical", 0, ""),
            ("Fortress", "Fortress", 1, "unlocks at Combat 15 (you are Combat 3)"), ("Mining", "Mining", 2, "")]
    PW9 = {"cur": "Balance", "on": "1", "wait": "0", "picks": [], "ans": None, "old": None, "reads": 0, "null": False}

    def f_pow9(o):
        op_ = str(o[0])
        if op_ == "vc:power":
            PW9["reads"] += 1
            if PW9["old"]:
                return PW9["old"]   # the real SkyyAccessories 0.5.38: a keyless vc:power hits its key gate ('-Your profile changed ...')
            L = ["ok|120|1.10|%s|%s|%s|%s|15|5" % (PW9["cur"], PW9["wait"], PW9["on"], CRW["tok"])]
            for i_, (id_, nm_, g_, lk_) in enumerate(POW9):
                L.append("p|%d|%s|%s|%d|%s|+%d Str, +%d Def|%s" % (i_, id_, nm_, g_, lk_, i_ + 1, i_ + 1, "1" if id_ == PW9["cur"] else "0"))
            return "\n".join(L)
        if op_ == "vc:pick":
            PW9["picks"].append((str(o[2]), str(o[3])))
            if PW9["null"]:
                return None
            if PW9["ans"] is not None:
                return PW9["ans"]
            id_, shown_ = str(o[3]).split("|")
            if shown_ != PW9["cur"]:
                return "=Your Power changed since you looked (it is %s now) - look again, nothing changed" % PW9["cur"]
            PW9["cur"] = id_
            return "+Power is now %s - your stats follow within a second" % id_
        return f_rows(o)
    BR.put("acc:fn:charms", Fn(f_pow9))
    r9_ = PW9["reads"]
    p_ = one(ev(PK, {"a": "vf:3"}), "OLD9 POWER the Power tab")
    cm = cmap(p_) if p_ else {}
    K.check(int(pg.vsub) == 3 and str(pg.mode) == "w" and PW9["reads"] - r9_ == 1 and TS_ in mk_of(p_, "SkyyInvWf3") and TS_ not in mk_of(p_, "SkyyInvWf0")
            and [sval(cm, "#SkyyInvWf%d.Text" % k_) for k_ in range(4)] == ["Benches", "Combat", "Gathering", "Power"] and "#SkyyInvIs.Slots" in cm,
            "OLD9 POWER the Power tab = ONE vc:power read, the fourth sub-tab selected (Benches / Combat / Gathering / Power), the bag stays")
    K.check(sval(cm, "#SkyyInvWxI.Text") == "AP 120" and sval(cm, "#SkyyInvWxPn.Text") == "1 / 2" and "x1.10" in str(sval(cm, "#SkyyInvWxM.Text"))
            and str(sval(cm, "#SkyyInvWn1v0.Text")) == "Balance  -  YOURS" and vis(cm, "Wn1v0") and not vis(cm, "Wn1v1") and vis(cm, "Ws1v1") and not vis(cm, "Ws1v0")
            and not vis(cm, "Wb1") and vis(cm, "Wb0") and sval(cm, "#SkyyInvWb0.Text") == "Pick" and vis(cm, "Ws0v0")
            and str(sval(cm, "#SkyyInvWs0v0.Text")) == "Combat  -  +1 Str, +1 Def" and "Tank" in cm.get("#SkyyInvWi0.Slots", "") and nometa(p_),
            "OLD9 POWER the rows: AP, pages, the help with the multiplier; yours = '- YOURS' + its stats green, no Pick; the others = group + stats, Pick")
    K.check([None if x_ is None else str(x_) for x_ in pg.vpow] == ["Tank", None, "Slayer", "Lucky", "Magical"],
            "OLD9 POWER only the drawn Pick buttons can pick (%s)" % [None if x_ is None else str(x_) for x_ in pg.vpow])
    p_ = one(ev(PK, {"a": "vr:0"}), "OLD9 POWER Pick Tank")
    cm = cmap(p_) if p_ else {}
    K.check(PW9["picks"] == [(CRW["tok"], "Tank|Balance")] and str(sval(cm, "#SkyyInvWxM.Text")).startswith("Power is now Tank") and str(sval(cm, "#SkyyInvWn0v0.Text")) == "Tank  -  YOURS"
            and not vis(cm, "Wb0") and vis(cm, "Wb1"),
            "OLD9 POWER Pick = ONE vc:pick '<id>|<the Power the drawing showed>' with the rows' profile key; the answer + ONE redraw (Tank is yours now) (%s)" % PW9["picks"])
    one(ev(PK, {"a": "vr:0"}), "OLD9 POWER a forged Pick on your own Power")
    K.eq(len(PW9["picks"]), 1, "OLD9 POWER no Pick button on your own Power = no call")
    PW9["cur"] = "Lucky"   # another place (/charms power) switched it after the drawing
    p_ = one(ev(PK, {"a": "vr:2"}), "OLD9 POWER Pick Slayer from an older drawing")
    cm = cmap(p_) if p_ else {}
    K.check(PW9["picks"][-1] == (CRW["tok"], "Slayer|Tank") and str(sval(cm, "#SkyyInvWxM.Text")).startswith("Your Power changed since you looked (it is Lucky now)")
            and str(sval(cm, "#SkyyInvWn3v0.Text")) == "Lucky  -  YOURS" and PW9["cur"] == "Lucky",
            "OLD9 POWER '=' (your Power changed since the drawing) = the answer line, nothing changed, the redraw shows Lucky")
    p_ = one(ev(PK, {"a": "vr:2"}), "OLD9 POWER the same press again at once")
    K.check(len(PW9["picks"]) == 3 and PW9["picks"][-1] == (CRW["tok"], "Slayer|Lucky") and PW9["cur"] == "Slayer" and str(sval(cmap(p_), "#SkyyInvWxM.Text")).startswith("Power is now Slayer"),
            "OLD9 FIX POWER after '=' the same press again AT ONCE (no 1.5 s wait) carries the newly drawn Power and runs (%s)" % PW9["picks"])
    PW9["ans"] = "-wait 4 s before you switch your Power again"
    time.sleep(1.6)
    p_ = one(ev(PK, {"a": "vr:0"}), "OLD9 POWER a refused Pick")
    K.check(PW9["picks"][-1] == (CRW["tok"], "Tank|Slayer") and str(sval(cmap(p_), "#SkyyInvWxM.Text")) == "wait 4 s before you switch your Power again" and PW9["cur"] == "Slayer",
            "OLD9 POWER a '-' answer (the wait) = shown, nothing else")
    n9d_ = len(PW9["picks"])
    one(ev(PK, {"a": "vr:0"}), "OLD9 POWER the same press within 1.5 s")
    K.eq(len(PW9["picks"]), n9d_, "OLD9 POWER a double click (after a '-' answer) = no second call")
    PW9["ans"] = None
    PW9["null"] = True
    time.sleep(1.6)
    p_ = one(ev(PK, {"a": "vr:0"}), "OLD9 POWER a null answer")
    K.check("could not do that here - nothing changed" in str(sval(cmap(p_), "#SkyyInvWxM.Text")) and PW9["cur"] == "Slayer", "OLD9 POWER a null answer = 'could not do that here - nothing changed'")
    PW9["null"] = False
    p_ = one(ev(PK, {"a": "vpn"}), "OLD9 POWER page 2")
    cm = cmap(p_) if p_ else {}
    n9_ = len(PW9["picks"])
    K.check(sval(cm, "#SkyyInvWxPn.Text") == "2 / 2" and str(sval(cm, "#SkyyInvWn0v0.Text")) == "Fortress  -  LOCKED" and not vis(cm, "Wb0")
            and str(sval(cm, "#SkyyInvWs0v0.Text")) == "Combat 15  -  Locked: unlocks at Combat 15 (you are Combat 3)" and vis(cm, "Wb1")
            and str(sval(cm, "#SkyyInvWs1v0.Text")).startswith("Gathering  -  ") and sval(cm, "#SkyyInvWr2.Visible") in (False, "false"),
            "OLD9 POWER page 2: a locked Power says why, no Pick; the Gathering group; rows 3-5 hidden")
    for a_, why_ in (("vr:0", "a locked Power (no button)"), ("vr:4", "an empty row"), ("vr:x", "bad")):
        p_ = one(ev(PK, {"a": a_}), "OLD9 POWER " + why_)
        K.check(len(PW9["picks"]) == n9_ and "Nothing to pick" in str(sval(cmap(p_), "#SkyyInvWxM.Text")), "OLD9 POWER %s: no call, said" % why_)
    one(ev(PK, {"a": "vpp"}), "OLD9 POWER page 1")
    PW9["on"] = "0"
    p_ = one(ev(PK, {"a": "vf:3"}), "OLD9 POWER Powers off")
    cm = cmap(p_) if p_ else {}
    K.check(not any(vis(cm, "Wb%d" % k_) for k_ in range(5)) and "switched off" in str(sval(cm, "#SkyyInvWxM.Text")) and all(x_ is None for x_ in pg.vpow),
            "OLD9 POWER Powers off on the server = said, no Pick button")
    PW9["on"], PW9["wait"] = "1", "3"
    p_ = one(ev(PK, {"a": "vf:3"}), "OLD9 POWER the switch wait")
    K.check("again in 3 s" in str(sval(cmap(p_), "#SkyyInvWxM.Text")), "OLD9 POWER the switch wait is said")
    PW9["wait"] = "0"
    CRW["tok"] = "ck3"
    p_ = one(ev(PK, {"a": "vf:3"}), "OLD9 POWER a profile switch")
    K.check("Your profile changed" in str(sval(cmap(p_), "#SkyyInvWxM.Text")), "OLD9 POWER a profile switch seen on a redraw is said")
    time.sleep(1.6)
    one(ev(PK, {"a": "vr:0"}), "OLD9 POWER Pick on the new profile")
    K.eq(PW9["picks"][-1], ("ck3", "Tank|Slayer"), "OLD9 POWER the next Pick carries the new profile's key")
    n9_ = len(PW9["picks"])
    for old_ in ("-Your profile changed - pick the charm again (nothing changed)", "-Void Charms does not know that - nothing changed"):
        PW9["old"] = old_
        p_ = one(ev(PK, {"a": "vf:3"}), "OLD9 POWER SkyyAccessories 0.5.38")
        cm = cmap(p_) if p_ else {}
        K.check("needs SkyyAccessories 0.5.39" in str(sval(cm, "#SkyyInvWxM.Text")) and "profile changed" not in str(sval(cm, "#SkyyInvWxM.Text"))
                and not any(vis(cm, "Wb%d" % k_) for k_ in range(5)) and sval(cm, "#SkyyInvWr0.Visible") in (False, "false") and sval(cm, "#SkyyInvWf3.Text") == "Power",
                "OLD9 FIX POWER with SkyyAccessories 0.5.38 (%r - its real keyless answer first) = the tab says it needs 0.5.39, no rows, no button" % old_)
    p_ = one(ev(PK, {"a": "vr:0"}), "OLD9 POWER a forged Pick with 0.5.38")
    K.check(len(PW9["picks"]) == n9_, "OLD9 POWER a forged Pick there = no call")
    PW9["old"] = None
    p_ = one(ev(PK, {"a": "vf:1"}), "OLD9 POWER back to Combat")
    K.check(int(pg.vsub) == 1 and sval(cmap(p_), "#SkyyInvWb0.Text") == "Craft", "OLD9 POWER a Craft tab again = the craft rows")
    n0_ = len(CRW["calls"])
    time.sleep(1.6)
    one(ev(PK, {"a": "vr:1"}), "OLD9 POWER Craft after the Power tab")
    K.check(CRW["calls"][n0_:] == [("vc:craft", "ck3", "Rec_1")], "OLD9 POWER Craft on a craft tab still = vc:craft (never vc:pick) (%s)" % CRW["calls"][n0_:])
    K.notes.append("OLD9 ran: vc:power reads %d, picks %d" % (PW9["reads"], len(PW9["picks"])))
    BR.put("acc:fn:charms", Fn(f_rows))
'''

EXPECT_BODY = '''    "InvPage": ["+f vbag", "+f vpow", "+f vpowCur", "+m charmTabs", "+m fillPower", "+m powerPick", "~m build", "~m charmRow", "~m charmRowsOk",
                "~m fillCharmRows", "~m handleDataEvent", "~m nowGo", "~m openCharms", "~m pocketCmp", "~m pocketTab", "~m pocketUp", "~m tanning"],
    "SkillPage": ["~m handleDataEvent", "~m openTree"],
    "InvData": ["~<clinit>"],   # WF_BTN (the charm tab width) + W_HELP (the help line)
    "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''


def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.76 (old menu follow-up - the Market tab's Bank view = the old Storage > Bank link; tools/menu_0_3_76_patch.py,''',
      '''"""Harness for SkyyMenu 0.3.77 (the last old-menu rows - the charm rows' Bag + Power tab, the Void / Tannery / Trees fallbacks;
tools/menu_0_3_77_patch.py, round oldmenu9). GENERATED by tools/menu_0_3_77_patch.py from the 0.3.76 harness (edit the patch, not this file):
every 0.3.76 check runs again on the 0.3.77 jar (MENUFIX1: Bag = the bag grid; CRAFT: the Tanning tab caption names SkyySacks 0.8.38; INV6:
Auto-compact without 0.8.39 names it; TAB1: Open tree without /tree = a caption naming SkyyTrees 0.6.10; OLD8's ratchet = 'stays gone'), plus
  OLD9 STATIC   the ratchet: OLD_LEFT 5 -> 3 (Server Setup + the tracked SkyySacks doors Upgrades / Tanning Full page; the OLD1 SCAN counts
                them); no /tree; no Trees / Void Charms / Void / Crafting page link or text in the new screens; the
                pkv handler gone; Bag = the grid; the Power tab reads vc:power + picks with vc:pick <id>|<shown Power>; the build asserts the
                four tabs, the count label and the help line fit
       FALL     the Void tab without SkyySacks 0.8.38 / Upgrades without 0.8.39 / the skill page's Void Charms without SkyyAccessories 0.5.37
                = a caption naming the version, the page stays; a forged pkv opens nothing
       BAG      Bag = the charms grid inside the inventory (vc:list), no act; Done there = back to the rows
       POWER    the fourth sub-tab = ONE vc:power read: AP, pages, the help (multiplier), yours green + '- YOURS' without Pick, the others Pick,
                locked = why, no Pick; Pick = ONE vc:pick '<id>|<shown Power>' with the rows' profile key, the answer + ONE redraw; a forged Pick
                (own / locked / empty / bad row) = no call; '=' (changed since the drawing) then the same press again runs with the new Power;
                a double click = no second call; '-' shown; null = said; Powers off = no Pick; the wait said; a profile switch said and the
                new key sent; SkyyAccessories 0.5.38 = the tab names 0.5.39, no rows; a Craft tab again = vc:craft
The 0.3.76 harness text follows:
Harness for SkyyMenu 0.3.76 (old menu follow-up - the Market tab's Bank view = the old Storage > Bank link; tools/menu_0_3_76_patch.py,''')
T.rep('VERSION = "0.3.76"\nJAR', 'VERSION = "0.3.77"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.75.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.76.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.75.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.76.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_76_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_77_patch.py")')
T.rep('"scratch", "oldmenu8", "menu"', '"scratch", "oldmenu9", "menu"')
T.rep('ADDED = []   # 0.3.76: no new class\n', 'ADDED = []   # 0.3.77: no new class\n')
EXPECT_77 = '''EXPECT = {   # 0.3.77: the charm rows' Bag + Power tab, the fallbacks, the version strings
@@EXPECT@@
}
'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.76:', 'if "--expect-dump" in sys.argv:'), EXPECT_77.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.76"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.77"') == 1, "S VERSION")
''' + HARNESS_OLD9_STATIC.rstrip("\n"))
# OLD8's ratchet compared 0.3.76 with 0.3.75: against 0.3.76 it is OLD9's (above) - its row stays gone
T.rep('''    K.check(lefto_ - left2_ == set([("storage", "bank")]) and not (left2_ - lefto_) and len(left2_) == len(lefto_) - 1,
            "OLD8 RATCHET OLD_LEFT lost storage:bank, nothing added (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))''',
      '''    K.check(("storage", "bank") not in left2_, "OLD8 RATCHET (0.3.77: vs 0.3.76) storage:bank stays gone")''')
# CRAFT: the Tanning tab without sacks:fn:openTannery (0.3.53's caption pointed at the old Crafting page)
T.rep('''    K.check("Tannery tab" in cap_of(p_), "CRAFT Tanning tab: the caption tells the player to pick the Tannery tab (%s)" % cap_of(p_))''',
      '''    K.check("needs SkyySacks 0.8.38" in cap_of(p_) and "Crafting page" not in cap_of(p_), "CRAFT Tanning tab without openTannery: (0.3.77) a caption naming SkyySacks 0.8.38, no old Crafting page (%s)" % cap_of(p_))''')
T.rep('''    K.check("not on this server" in cap_of(p_), "INV4 Summon without pets:fn:ride: a caption (%s)" % cap_of(p_))
''', '''    K.check("not on this server" in cap_of(p_), "INV4 Summon without pets:fn:ride: a caption (%s)" % cap_of(p_))
''' + HARNESS_OLD9_FALL)
T.rep('''    K.check(not CMP["calls"] and "Void page" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""), "INV6 POCKET ... a click = a hint, no call")
''', '''    K.check(not CMP["calls"] and "needs SkyySacks 0.8.39" in (sval(cmap(p_), "#SkyyInvPr.Text") or ""), "INV6 POCKET ... a click = a hint naming SkyySacks 0.8.39 (0.3.77), no call")
''' + HARNESS_OLD9_POCKET)
T.rep('''    K.check(cur_ == SP or (cur_ is not None and bool(SP.closed)), "TAB1 ACT Open tree without /tree = the Character hub's Trees route (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
''', HARNESS_OLD9_SKILL)
T.rep(r'''    K.check([str(E.CM.lines.get(i_)) for i_ in range(l0_, int(E.CM.lines.size()))] == ["tree mining"] and sval(cmap(p_), "#SkyySkpCap.Text") == "Opening the Mining tree",
            "TAB1 ACT Open tree = /tree mining as the player")''',
      r'''    K.check([str(E.CM.lines.get(i_)) for i_ in range(l0_, int(E.CM.lines.size()))] == [] and "need SkyyTrees 0.6.10" in str(sval(cmap(p_), "#SkyySkpCap.Text"))
            and PK.pm.getCustomPage() == SP,
            "TAB1 ACT Open tree WITH /tree but no inline tree = (0.3.77 fix) a caption naming SkyyTrees 0.6.10, never /tree (SkyyTrees' own page) (%s)" % sval(cmap(p_), "#SkyySkpCap.Text"))''')
T.rep(SCAN_OLD, SCAN_OLD + SCAN_ADD)
T.rep('''    p_ = one(ev(PK, {"a": "vbag"}), "MENUFIX1 ROWS Bag")
    cur_ = PK.pm.getCustomPage()
    K.check(p_ is not None, "MENUFIX1 ROWS Bag = the Void Charms page route, ONE packet (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    if PK.pm.getCustomPage() is not None and PK.pm.getCustomPage() != pg:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    pg = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
''', HARNESS_OLD9)
if T.dst:
    T.finish()
