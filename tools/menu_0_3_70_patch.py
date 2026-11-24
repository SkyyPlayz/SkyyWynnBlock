"""Derive SkyyMenu/build_skyymenu_0.3.70.py + SkyyMenu/test_skyymenu_0.3.70.py from the SET pin SkyyMenu 0.3.69 (generated - never re-run
its patch). Run:  python tools/menu_0_3_70_patch.py   then   python SkyyMenu/build_skyymenu_0.3.70.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.70.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). Needs SkyyPets 0.4.29 (tools/pets_0_4_29_patch.py: pets:fn:tab st| lines + pets:fn:tabact start / efuse)
for the first-pet choice and egg fusing; with SkyyPets 0.4.28 the Pets tab still works (no st| lines = the /pets hint; Fuse eggs = SkyyPets'
own "-Unknown pet action." answer).

0.3.70 (2026-11-24, round oldmenu2) = OLD MENU FOLLOW-UPS F1 + F2 + F3 (round oldmenu1's OLD_LEFT list). Skyy's words (docs/answered/ui.md
2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when everything is in the new system id like to disable the old menu compleatly, so instead of adding
things like the full tree button, just build it all into the new system and remove the old "Full tree""; 2026-11-23 "looks better. go head and
build everything on your list." Each part calls the SAME server code as the old page (no duplicated rule, no new number):
  F1 SETTINGS TAB = THE OLD MODS PAGE. The Mods card's 12 names are buttons (a mod's help); "All mods" (was "Mods page") turns the big left list
     into ALL MODS (every installed mod: name + live version, its first line; Help, and for admins Set up = Server Setup on that mod - the old
     list's modcfg path, AdminPage "mod"); Help shows that mod's text = MenuUtil.modBodyFor(k, admin) (the old Mods page's tooltip, admin-only
     lines for admins) as rows: "What it does" (the description in 100-character lines), COMMANDS, ADMIN ONLY, each "/cmd - what it does" line
     as command | help. 9 rows a page (< >). A category on the left / a search = back to the settings. Who sees it = the old Mods tab's rule
     (MenuHub.visible "mods"). The settings ON / OFF rows never show in the mods views (a forged on / off = "No setting there").
  F2 PETS TAB = THE OLD PETS PAGE. No Full page. The FIRST-PET CHOICE (SkyyPets 0.4.29 st| lines): while a profile waits for its choice, the
     empty pets grid shows the 4 starter pets (Common portrait, Style Guide 15 tooltip: name in the Common colour, FIRST PET - <type>, its
     buffs in green, the yellow click line); a click = pets:fn:tabact start (SkyyPets asks, the same pet again chooses = PetOps.chooseStarter).
     EVERY HATCHERY SLOT: the Hatchery pages 6 slots at a time (< > under it; "Slots 7-12 of 14"), the rows' Hatch / Take out / Place carry the
     real slot number. EGG FUSING: "Fuse eggs" on the Eggs card = tabact efuse <the selected egg> (SkyyPets asks, the same egg again fuses =
     PetHatchery.efuse). The read failing no longer points at the Full page.
     F2 SURVEY (the old SkyyPets PetsPage clicks -> where each one is in the Pets tab; every one = the same SkyyPets door through
     pets:fn:tab / pets:fn:tabact):
       grid mode 0 'g' (put a pet in a slot)   -> tabact slot (PetOps)        | 'out' (take a slot out)       -> tabact out
       grid mode 1 (summon Mount / Fighter)    -> tabact ride                 | grid mode 2 (fuse pets)       -> tabact fuse
       grid mode 3 (rebirth a max-level pet)   -> tabact reb                  | 'role' / 'area' filters       -> the read's role + area args
       'more' (Show more)                      -> the read's page arg (< >)   | 'pick' (first pet, 2 presses) -> tabact start (0.4.29)
       'later' (starter view's Later)          -> not needed: the 4 starters sit in the empty grid, the rest of the tab stays usable
       Eggs 'craft'                            -> tabact craft                | Eggs emode 1 'eg' (fuse eggs)  -> tabact efuse (0.4.29)
       Eggs emode 0 'eg' (egg -> Hatchery)     -> tabact place                | Eggs emode 2 (pets owned 2+)  -> the pets grid's fuse (tabact fuse)
       Hatchery 'slot' Hatch / Take out        -> tabact hatch / take, every slot (6 a page)  | the hatch reel + its skip-animation toggle
                                                  stay SkyyPets' own PetHatchPage (opened over the tab, "^"), as on the old page.
     Nothing the old page did is left out, so character:pets leaves OLD_LEFT.
  F3 MARKET TAB: the BANK card takes a TYPED AMOUNT (the old Bank page's box: 500, 2k, 1.5m or all) - Deposit / Withdraw use it before the chip
     (bank:fn:move deposit / withdraw / depall / wdall, the panel's profile key + epoch, as before). That was the last thing the Bank page did
     that the card did not (levels, the level line, Upgrade (two presses, the shown level) and the 5 chips are since 0.3.59). Its 'Bank page'
     button opened HubBar storage:bank = with SkyyVault the VAULT (item pages): it is now labelled "Vault" and STAYS until the Vault round
     (OLD_LEFT keeps storage:bank for the Vault).
  STILL OLD (OLD_LEFT, follow-up rounds - too big for one round, never half-wired): market:bazaar (the Bazaar page: buy orders / sell offers with a
  typed price, cancelling orders - needs SkyyBazaar bazaar:fn:tabact ops 'bid' / 'ask' / 'cancel' + an order id in the o| lines), market:merchants
  (SkyyMerchants has no bridge yet: merchants:fn:tab read + buy), market:auctions (the Auction House card's buttons: ah:fn:view browse / create /
  manage and the ah:fn:find rows (ah:fn:open) open SkyyAuctions' own pages through opener(..., "market", "auctions"); fix round: the OLD1 scan
  now counts opener(...) links too, so this row is TRACKED until a browse / sell / my auctions / bids sub-tab (ah:fn read + act ops) replaces
  them), storage:bank (= the Vault). F3 STATUS: of the task's Market parts only the Bank page's typed amount is in; Bazaar Full page, Open
  Merchants, the Auction House links (and the Vault) still open their own pages - they need new ops in SkyyBazaar / a SkyyMerchants bridge /
  ah:fn read + act ops (coins + items: one round each, not a fixer patch). Question for Skyy in the round report.
No saved data, no new class / command / system / picture / lang key / setting. OLD_LEFT: settings:mods + character:pets out, market:auctions
now tracked (20 -> 19 rows).
ROLLBACK to 0.3.69: safe alone (nothing saved; the old links come back). SkyyPets 0.4.29 rolls back alone to 0.4.28 (Menu then shows the /pets hint).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.69.py"), os.path.join(MOD, "build_skyymenu_0.3.70.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.69.py"), os.path.join(MOD, "test_skyymenu_0.3.70.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.69"\n') and P.has("OLD_LEFT = sorted(set([") and not P.has("fillModRows"), "not the generated SkyyMenu 0.3.69 script"
SYS0, CMD0, MK0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count(' = mk("')

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.69: THE OLD MENU SWITCH''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.70: OLD MENU FOLLOW-UPS: the Settings tab holds the old Mods page (each mod's help + commands, Set up for admins); the Pets tab holds the old
       Pets page (the first-pet choice, every Hatchery slot, egg fusing - SkyyPets 0.4.29); the Market tab's bank takes a typed amount (its
       'Bank page' button = the Vault); OLD_LEFT lost 2 rows and now tracks the Auction House links (notes: tools/menu_0_3_70_patch.py). CHECKED: SkyyMenu/test_skyymenu_0.3.70.py.
0.3.69: THE OLD MENU SWITCH''')
P.rep('VERSION = "0.3.69"\n', 'VERSION = "0.3.70"\n')

# ======================================================================= F1: THE SETTINGS TAB = THE OLD MODS PAGE
P.rep('''    "modson": "Each mod's help and commands: the Mods page.",''', '''    "modson": "Pick a mod for its help and commands, or All mods.",   # 0.3.70 (F1): the old Mods page is in this screen''')
P.rep('''    "noaccess": "You no longer have access to Server Setup.",
}''', '''    "noaccess": "You no longer have access to Server Setup.",
    # 0.3.70 (F1): the always line under the mods views of the big list
    "modsal": "Help = that mod's commands. Set up (admins) = its Server Setup. A category on the left = your settings.",
    "modhal": "All mods (right) lists every mod again. A category on the left = back to your settings.",
}''')
P.rep('''for _l in SG_CH:
    assert SUI.text_width(_l, 13, bold=True) <= SG_CHW - 12, ("0.3.64: a choice label fits", _l)''', '''for _l in SG_CH:
    assert SUI.text_width(_l, 13, bold=True) <= SG_CHW - 12, ("0.3.64: a choice label fits", _l)
# 0.3.70 (F1): the old Mods page's text in the big list - THE SAME split SettingsTab.fillModRows makes at run time (chunks of the description,
# "X:" headers, "/cmd - help" = command | help when the command part is at most 44 characters): every piece fits its label, nothing is cut
for _k in ("modsal", "modhal"):
    assert SUI.text_width(SG_TXT[_k], 12) <= SG_LW, ("0.3.70: a mods view's always line fits", _k)
for _l in ("Help", "Set up"):
    assert SUI.text_width(_l, 13, bold=True) <= SG_CHW - 12, ("0.3.70: a mod row's button fits", _l)
SG_MCUT = 44                                                # a command part longer than this goes whole onto the help line


def _sg_chunks(s, mx):
    """= SettingsTab.chunks (Java lastIndexOf(' ', mx) = the last space at or before mx)"""
    out, t = [], s.strip()
    while len(t) > mx:
        c = t.rfind(" ", 0, mx + 1)
        if c <= 0:
            c = mx
        out.append(t[:c].strip())
        t = t[c:].strip()
    if t:
        out.append(t)
    return out


def _sg_mod_rows(body):
    ls = body.split("\\n")
    rows = [("What it does" if i_ == 0 else "", c_) for i_, c_ in enumerate(_sg_chunks(ls[0] if ls else "", SG_DCLIP))]
    for l_ in ls[1:]:
        if not l_:
            continue
        if l_.endswith(":"):
            rows.append((l_[:-1].upper(), ""))
            continue
        j_ = l_.find(" - ")
        rows.append((l_[:j_], l_[j_ + 3:]) if 0 < j_ <= SG_MCUT else ("", l_))
    return rows


_sg_mrows = 0
for _b in MOD_BODY + MOD_ABODY + [b_ for b_ in MOD_OLD_BODY if b_]:
    for _n, _d in _sg_mod_rows(_b):
        assert SUI.text_width(_n, 15, bold=True) <= SG_TW and SUI.text_width(_d, 12) <= SG_DW, ("0.3.70: a mods help row fits", _n, _d)
        _sg_mrows += 1
for _i, _m in enumerate(MODS):
    assert SUI.text_width("%s %s" % (_m["mod"], "0.12.345"), 15, bold=True) <= SG_TW, ("0.3.70: a mod name + version fits", _m["mod"])
print("0.3.70 mods views: %d mods, %d help rows in all (9 a page)" % (len(MODS), _sg_mrows))''')
# the Mods card: its 12 names are buttons (that mod's help); the old 'Mods page' button = All mods (the list view of the big list)
P.rep('''            ap.append(("#" + col_, lab("%sM%d" % (SG, c_ * rows_ + r_), "", 13, "row", w=SG_MCW, h=24)))''',
      '''            ap.append(("#" + col_, G_.glass_button("%sM%d" % (SG, c_ * rows_ + r_), "", "secondary", w=SG_MCW, h=22, size=12, anchor={"bottom": 2})))   # 0.3.70''')
P.rep('''    ap.append(("#" + mo, G_.glass_button(SG + "Mpage", "Mods page", "secondary", w=160, h=34, size=14, anchor={"top": 8})))''',
      '''    ap.append(("#" + mo, G_.glass_button(SG + "Mpage", "All mods", "secondary", w=160, h=34, size=14, anchor={"top": 8})))   # 0.3.70: the list view''')
P.rep('''for _n, _v in (("RN", SG_RN), ("MON", SG_MON), ("SN", SG_SN), ("ONW", SG_ONW), ("CHW", SG_CHW), ("SPW", SG_SPW), ("DCLIP", SG_DCLIP)):
    F(sgd, "public static final int %s = %d;" % (_n, _v))''', '''for _n, _v in (("RN", SG_RN), ("MON", SG_MON), ("SN", SG_SN), ("ONW", SG_ONW), ("CHW", SG_CHW), ("SPW", SG_SPW), ("DCLIP", SG_DCLIP),
               ("BW", SG_BW), ("MCUT", SG_MCUT)):   # 0.3.70: + the row button strip, the command cut
    F(sgd, "public static final int %s = %d;" % (_n, _v))''')
P.rep('''               ("SETUPNONE", SG_TXT["setupnone"]), ("NOACCESS", SG_TXT["noaccess"])):
    F(sgd, "public static final String %s = %s;" % (_n, jstr(_v)))''', '''               ("SETUPNONE", SG_TXT["setupnone"]), ("NOACCESS", SG_TXT["noaccess"]), ("MODSAL", SG_TXT["modsal"]), ("MODHAL", SG_TXT["modhal"])):
    F(sgd, "public static final String %s = %s;" % (_n, jstr(_v)))''')
P.rep('''C(sgt, r"""
public SettingsTab(@PR@ pr, String via) {''', '''for _f in ("public int mview;", "public int modk;", "public int[] mrow;", "public int[] mcard;"):   # 0.3.70 (F1): 0 settings / 1 all mods / 2 one mod
    F(sgt, _f)
C(sgt, r"""
public SettingsTab(@PR@ pr, String via) {''')
P.rep('''  this.drained = false;
  this.mods = new String[0];''', '''  this.drained = false;
  this.mods = new String[0];
  this.mview = 0;
  this.modk = -1;
  this.mrow = new int[0];
  this.mcard = new int[0];''')
# the new methods (before fillSettings, their first caller): chunks, fillTail (the list's footer + search, shared by every view), fillModRows
P.rep('''# SETTINGS: the old page's rows (SetReg.visible per category = only what this player may change), its search (every word in key, tab name,''',
      '''# 0.3.70 (oldmenu2 F1): the description in lines of at most mx characters (cut at the last space; = _sg_chunks at build time)
M(sgt, r"""
public static String[] chunks(String s, int mx) {
  java.util.ArrayList out = new java.util.ArrayList();
  String t = s == null ? "" : s.trim();
  while (t.length() > mx) {
    int c = t.lastIndexOf(' ', mx);
    if (c <= 0) c = mx;
    out.add(t.substring(0, c).trim());
    t = t.substring(c).trim();
  }
  if (t.length() > 0) out.add(t);
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
# the list's footer + the search box (the old page's Reset all, its hint, Find / Enter) - every view of the big list
M(sgt, r"""
public void fillTail(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  boolean armed = this.armedAt > 0L && System.currentTimeMillis() - this.armedAt <= 10000L;
  b.set("#SkyyGtabSt.Text", @PKG@.SetStore.isBroken(u) ? @PKG@.MenuData.SET_TXT_BROKEN : @PKG@.MenuData.SET_TXT_HINT);
  b.set("#SkyyGtabReset.Text", armed ? "Click again" : "Reset all");
  ev.addEventBinding(@BT@.Activating, "#SkyyGtabReset", evd("reset"));
  String dr = this.draft == null ? "" : this.draft;
  if (dr.length() > 0) b.set("#SkyyGtabQ.Value", dr);
  ev.addEventBinding(@BT@.Validating, "#SkyyGtabQ", evd("find"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyGtabFind", evd("find"));
}""")
# 0.3.70 (F1) THE OLD MODS PAGE in the big list: mview 1 = ALL MODS (the old list's installed test AdminPage.installed, name + live version, the
# first line of MenuUtil.modBody; Help, Set up for admins when the mod has a Server Setup page), mview 2 = ONE MOD (MenuUtil.modBodyFor(k, admin) =
# the old Mods page's text, admin-only lines for admins). 9 rows a page; rowKeys stay empty (no setting row can be switched from here).
M(sgt, r"""
public void fillModRows(@UCB@ b, @UEB@ ev) {
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  boolean vis = @PKG@.MenuHub.visible("mods", this.playerRef);
  int rn = @PKG@.SettingsTabData.RN;
  this.rowKeys = new String[rn];
  this.mrow = new int[rn];
  for (int r = 0; r < rn; r++) this.mrow[r] = -1;
  java.util.ArrayList ns = new java.util.ArrayList();
  java.util.ArrayList ds = new java.util.ArrayList();
  java.util.ArrayList ks = new java.util.ArrayList();
  String head = "MODS";
  String al = @PKG@.SettingsTabData.MODSOFF;
  int nm = @PKG@.MenuData.MOD_NAME.length;
  if (vis && this.mview == 2 && this.modk >= 0 && this.modk < nm && @PKG@.AdminPage.installed(this.modk)) {
    int k = this.modk;
    String lv = @PKG@.MenuUtil.liveVersion(@PKG@.MenuData.MOD_NAME[k]);
    head = @PKG@.MenuData.MOD_NAME[k] + " " + (lv != null ? lv : @PKG@.MenuData.MOD_VER[k]) + "   -   help and commands";
    String[] ls = @PKG@.MenuUtil.modBodyFor(k, admin).split(String.valueOf((char) 10));
    String[] dc = chunks(ls.length > 0 ? ls[0] : "", @PKG@.SettingsTabData.DCLIP);
    for (int i = 0; i < dc.length; i++) { ns.add(i == 0 ? "What it does" : ""); ds.add(dc[i]); ks.add(Integer.valueOf(-1)); }
    for (int i = 1; i < ls.length; i++) {
      String l = ls[i];
      if (l.length() == 0) continue;
      if (l.endsWith(":")) { ns.add(l.substring(0, l.length() - 1).toUpperCase()); ds.add(""); ks.add(Integer.valueOf(-1)); continue; }
      int j = l.indexOf(" - ");
      if (j > 0 && j <= @PKG@.SettingsTabData.MCUT) { ns.add(l.substring(0, j)); ds.add(l.substring(j + 3)); }
      else { ns.add(""); ds.add(l); }
      ks.add(Integer.valueOf(-1));
    }
    al = @PKG@.SettingsTabData.MODHAL;
  } else if (vis) {
    this.mview = 1;
    for (int k = 0; k < nm; k++) {
      if (!@PKG@.AdminPage.installed(k)) continue;
      String lv = @PKG@.MenuUtil.liveVersion(@PKG@.MenuData.MOD_NAME[k]);
      ns.add(@PKG@.MenuData.MOD_NAME[k] + " " + (lv != null ? lv : @PKG@.MenuData.MOD_VER[k]));
      String[] ls = @PKG@.MenuUtil.modBody(k).split(String.valueOf((char) 10));
      ds.add(@PKG@.MenuUtil.clip(ls.length > 0 ? ls[0] : "", @PKG@.SettingsTabData.DCLIP));
      ks.add(Integer.valueOf(k));
    }
    head = "ALL MODS   -   " + ks.size() + " installed";
    al = @PKG@.SettingsTabData.MODSAL;
  }
  int n = ns.size();
  this.pages = n == 0 ? 1 : (n + rn - 1) / rn;
  if (this.page >= this.pages) this.page = this.pages - 1;
  if (this.page < 0) this.page = 0;
  int from = this.page * rn;
  b.set("#SkyyGtabLh.Text", @PKG@.MenuUtil.clip(head, 70));
  b.set("#SkyyGtabPg.Text", "Page " + (this.page + 1) + " / " + this.pages);
  for (int r = 0; r < rn; r++) {
    String rw = "SkyyGtabR" + r;
    int j = from + r;
    if (j >= n) {
      boolean none = n == 0 && r == 0;
      b.set("#" + rw + ".Visible", none);
      if (none) { b.set("#" + rw + "N.Text", "No mods to show"); b.set("#" + rw + "D.Text", @PKG@.SettingsTabData.MODSOFF); }
      continue;
    }
    b.set("#" + rw + ".Visible", true);
    b.set("#" + rw + "N.Text", @PKG@.MenuUtil.clip((String) ns.get(j), 48));
    b.set("#" + rw + "D.Text", @PKG@.MenuUtil.clip((String) ds.get(j), 110));
    int k = ((Integer) ks.get(j)).intValue();
    if (k < 0) continue;
    this.mrow[r] = k;
    boolean su = admin && @PKG@.AdminPage.hdr(@PKG@.MenuData.MOD_NAME[k]) != null;
    int nb = su ? 2 : 1;
    String bx = "#" + rw + "B";
    String w = String.valueOf(@PKG@.SettingsTabData.CHW);
    b.appendInline(bx, @PKG@.SettingsTabData.SPC.replace("{W}", String.valueOf(@PKG@.SettingsTabData.BW - nb * (@PKG@.SettingsTabData.CHW + 6))));
    b.appendInline(bx, @PKG@.SettingsTabData.BTN.replace("{I}", "R" + r + "h").replace("{W}", w).replace("{S}", @PKG@.SettingsTabData.ST_SEL));
    b.set("#SkyyGtabR" + r + "h.Text", "Help");
    ev.addEventBinding(@BT@.Activating, "#SkyyGtabR" + r + "h", evd("mh:" + r));
    if (su) {
      b.appendInline(bx, @PKG@.SettingsTabData.BTN.replace("{I}", "R" + r + "s").replace("{W}", w).replace("{S}", @PKG@.SettingsTabData.ST_TAB));
      b.set("#SkyyGtabR" + r + "s.Text", "Set up");
      ev.addEventBinding(@BT@.Activating, "#SkyyGtabR" + r + "s", evd("ms:" + r));
    }
  }
  b.set("#SkyyGtabAl.Text", @PKG@.MenuUtil.clip(al, 125));
}""")
# SETTINGS: the old page's rows (SetReg.visible per category = only what this player may change), its search (every word in key, tab name,''')
P.rep('''    boolean on = !find && i == this.cat;''', '''    boolean on = !find && this.mview == 0 && i == this.cat;   // 0.3.70: no category chosen in the mods views''')
P.rep('''  int rn = @PKG@.SettingsTabData.RN;
  this.pages = n == 0 ? 1 : (n + rn - 1) / rn;
  if (this.page >= this.pages) this.page = this.pages - 1;
  if (this.page < 0) this.page = 0;
  int from = this.page * rn;
  b.set("#SkyyGtabLh.Text", (find ?''', '''  if (this.mview != 0) { fillModRows(b, ev); fillTail(b, ev); return; }   // 0.3.70 (F1): the old Mods page in the big list
  int rn = @PKG@.SettingsTabData.RN;
  this.pages = n == 0 ? 1 : (n + rn - 1) / rn;
  if (this.page >= this.pages) this.page = this.pages - 1;
  if (this.page < 0) this.page = 0;
  int from = this.page * rn;
  b.set("#SkyyGtabLh.Text", (find ?''')
P.rep('''  b.set("#SkyyGtabAl.Text", @PKG@.MenuUtil.clip(find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat], 125));
  boolean armed = this.armedAt > 0L && System.currentTimeMillis() - this.armedAt <= 10000L;
  b.set("#SkyyGtabSt.Text", @PKG@.SetStore.isBroken(u) ? @PKG@.MenuData.SET_TXT_BROKEN : @PKG@.MenuData.SET_TXT_HINT);
  b.set("#SkyyGtabReset.Text", armed ? "Click again" : "Reset all");
  ev.addEventBinding(@BT@.Activating, "#SkyyGtabReset", evd("reset"));
  String dr = this.draft == null ? "" : this.draft;
  if (dr.length() > 0) b.set("#SkyyGtabQ.Value", dr);
  ev.addEventBinding(@BT@.Validating, "#SkyyGtabQ", evd("find"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyGtabFind", evd("find"));
}""")''', '''  b.set("#SkyyGtabAl.Text", @PKG@.MenuUtil.clip(find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat], 125));
  fillTail(b, ev);   // 0.3.70: the footer + search (the same lines, shared with the mods views)
}""")''')
# the Mods card: the installed mods as buttons (mq:<slot> = that mod's help; the last slot when more = All mods)
P.rep('''public void fillMods(@UCB@ b) {
  boolean vis = @PKG@.MenuHub.visible("mods", this.playerRef);
  java.util.ArrayList ls = new java.util.ArrayList();
  if (vis) {
    for (int k = 0; k < @PKG@.MenuData.MOD_NAME.length; k++) {
      if (!@PKG@.AdminPage.installed(k)) continue;
      String lv = @PKG@.MenuUtil.liveVersion(@PKG@.MenuData.MOD_NAME[k]);
      ls.add(@PKG@.MenuData.MOD_NAME[k] + " " + (lv != null ? lv : @PKG@.MenuData.MOD_VER[k]));
    }
  }
  int n = ls.size();
  int m = @PKG@.SettingsTabData.MON;
  b.set("#SkyyGtabMc.Text", vis ? n + " installed" : "");
  for (int k = 0; k < m; k++) {
    String e = "#SkyyGtabM" + k;
    if (k >= n) { b.set(e + ".Visible", false); continue; }
    b.set(e + ".Visible", true);
    b.set(e + ".Text", k == m - 1 && n > m ? "+" + (n - m + 1) + " more on the Mods page" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe((String) ls.get(k)), 30));
  }''', '''public void fillMods(@UCB@ b, @UEB@ ev) {
  boolean vis = @PKG@.MenuHub.visible("mods", this.playerRef);
  java.util.ArrayList ls = new java.util.ArrayList();
  java.util.ArrayList ix = new java.util.ArrayList();
  if (vis) {
    for (int k = 0; k < @PKG@.MenuData.MOD_NAME.length; k++) {
      if (!@PKG@.AdminPage.installed(k)) continue;
      String lv = @PKG@.MenuUtil.liveVersion(@PKG@.MenuData.MOD_NAME[k]);
      ls.add(@PKG@.MenuData.MOD_NAME[k] + " " + (lv != null ? lv : @PKG@.MenuData.MOD_VER[k]));
      ix.add(Integer.valueOf(k));
    }
  }
  int n = ls.size();
  int m = @PKG@.SettingsTabData.MON;
  this.mcard = new int[m];
  b.set("#SkyyGtabMc.Text", vis ? n + " installed" : "");
  for (int k = 0; k < m; k++) {
    String e = "#SkyyGtabM" + k;
    this.mcard[k] = -1;
    if (k >= n) { b.set(e + ".Visible", false); continue; }
    boolean more = k == m - 1 && n > m;
    this.mcard[k] = more ? -2 : ((Integer) ix.get(k)).intValue();   // 0.3.70 (F1): -2 = All mods
    b.set(e + ".Visible", true);
    b.set(e + ".Text", more ? "+" + (n - m + 1) + " more - All mods" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe((String) ls.get(k)), 30));
    ev.addEventBinding(@BT@.Activating, e, evd("mq:" + k));
  }''')
P.rep('''  try { fillMods(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen: the mods card failed: " + t); }''',
      '''  try { fillMods(b, ev); } catch (Throwable t) { this.mcard = new int[0]; @PKG@.MenuUtil.warn("settings screen: the mods card failed: " + t); }''')
# Server Setup on ONE mod by name (setupMod(k) of the Server Setup card and the mods list's Set up share it) + the mods clicks
P.rep('''public void setupMod(int k) {
  this.answered = true;
  if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.tcap = @PKG@.SettingsTabData.NOACCESS; redraw(); return; }
  if (k < 0 || this.mods == null || k >= this.mods.length || this.mods[k] == null) { say("No mod there"); return; }
  String m = this.mods[k];
  if (@PKG@.AdminPage.hdr(m) == null)''', '''public void setupOf(String m) {
  this.answered = true;
  if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.tcap = @PKG@.SettingsTabData.NOACCESS; redraw(); return; }
  if (m == null) { say("No mod there"); return; }
  if (@PKG@.AdminPage.hdr(m) == null)''')
P.rep('''  if (!still()) finish("server setup");
}""")
M(sgt, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''', '''  if (!still()) finish("server setup");
}""")
M(sgt, r"""
public void setupMod(int k) {
  this.answered = true;
  if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.tcap = @PKG@.SettingsTabData.NOACCESS; redraw(); return; }
  if (k < 0 || this.mods == null || k >= this.mods.length || this.mods[k] == null) { say("No mod there"); return; }
  setupOf(this.mods[k]);   // 0.3.70: the same door as the mods list's Set up
}""")
# 0.3.70 (F1): mq:<card slot> (the Mods card) / mh:<row> (Help) / ms:<row> (Set up, admins) - the old Mods tab's rule re-checked at every click
M(sgt, r"""
public void modClick(String kind, int i) {
  this.answered = true;
  if (!@PKG@.MenuHub.visible("mods", this.playerRef)) { this.mview = 0; this.tcap = @PKG@.SettingsTabData.MODSOFF; redraw(); return; }
  int k = -1;
  if (kind.equals("mq")) {
    if (i < 0 || this.mcard == null || i >= this.mcard.length) { say("No mod there"); return; }
    k = this.mcard[i];
    if (k == -2) { this.mview = 1; this.page = 0; this.query = ""; this.tcap = ""; redraw(); return; }
  } else {
    if (this.mview != 1 || i < 0 || this.mrow == null || i >= this.mrow.length) { say("No mod there"); return; }
    k = this.mrow[i];
  }
  if (k < 0 || k >= @PKG@.MenuData.MOD_NAME.length || !@PKG@.AdminPage.installed(k)) { say("No mod there"); return; }
  if (kind.equals("ms")) { setupOf(@PKG@.MenuData.MOD_NAME[k]); return; }
  this.mview = 2;
  this.modk = k;
  this.page = 0;
  this.query = "";
  this.tcap = "";
  redraw();
}""")
M(sgt, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {''')
P.rep('''      if (!@PKG@.MenuHub.visible("mods", this.playerRef)) { this.tcap = @PKG@.SettingsTabData.MODSOFF; redraw(); return; }
      hub("settings", "mods", "the Mods page");
      return;''', '''      if (!@PKG@.MenuHub.visible("mods", this.playerRef)) { this.tcap = @PKG@.SettingsTabData.MODSOFF; redraw(); return; }
      this.mview = 1;                                   // 0.3.70 (F1): ALL MODS in the big list (was the old Mods page)
      this.page = 0;
      this.query = "";
      this.tcap = "";
      redraw();
      return;''')
P.rep('''      this.query = q;
      this.page = 0;
      this.tcap = q.length() == 0 ? "Type a word, then Find" : "";''', '''      this.query = q;
      this.page = 0;
      this.mview = 0;                                   // 0.3.70: a search = the settings
      this.tcap = q.length() == 0 ? "Type a word, then Find" : "";''')
P.rep('''    if (a.equals("fclear")) { this.query = ""; this.draft = ""; this.page = 0; this.tcap = ""; redraw(); return; }''',
      '''    if (a.equals("fclear")) { this.query = ""; this.draft = ""; this.page = 0; this.mview = 0; this.tcap = ""; redraw(); return; }   // 0.3.70: + the settings''')
P.rep('''      if (k < 0 || k >= @PKG@.MenuData.SET_CAT_ID.length) { say("No such category"); return; }
      this.cat = k;''', '''      if (k < 0 || k >= @PKG@.MenuData.SET_CAT_ID.length) { say("No such category"); return; }
      this.mview = 0;                                   // 0.3.70: a category = back to the settings
      this.cat = k;''')
P.rep('''    if (a.startsWith("on:")) { toggle(@PKG@.InvPage.toInt(a.substring(3), -1), true); return; }''',
      '''    if (a.startsWith("mq:") || a.startsWith("mh:") || a.startsWith("ms:")) { modClick(a.substring(0, 2), @PKG@.InvPage.toInt(a.substring(3), -1)); return; }   // 0.3.70
    if (a.startsWith("on:")) { toggle(@PKG@.InvPage.toInt(a.substring(3), -1), true); return; }''')

# ======================================================================= F2: THE PETS TAB = THE OLD PETS PAGE
P.rep('''    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - IV_COIN_W - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(PT + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))''',
      '''    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - IV_COIN_W - IV_X - 8   # 0.3.70 (F2): no Full page (+ its 128 px)
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))''')
P.rep('''    ap.append(("#" + ha, lab(PT + "Hf", "", 11, "dim", w=PT_RI, h=18, anchor={"top": 4})))''',
      '''    hfr = PT + "Hfr"   # 0.3.70 (F2): every Hatchery slot - 6 a page, < > around the footer line (the same 22 px as the old line)
    ap.append(("#" + ha, G_.glass_group(hfr, PT_RI, 20, layout="Left", anchor={"top": 2})))
    ap.append(("#" + hfr, G_.glass_button(PT + "Hp", "<", "secondary", w=30, h=20, size=12, anchor={"right": 4})))
    ap.append(("#" + hfr, lab(PT + "Hf", "", 11, "dim", w=PT_RI - 68, h=20)))
    ap.append(("#" + hfr, G_.glass_button(PT + "Hn", ">", "secondary", w=30, h=20, size=12, anchor={"left": 4})))
    assert SUI.text_width(PT_TXT["hfoot"], 11) <= PT_RI - 68 and SUI.text_width("Slots 13-18 of 18  -  < > for more", 11) <= PT_RI - 68, "0.3.70: the Hatchery footer fits"''')
P.rep('''    ap.append(("#" + egh, lab(PT + "En", "", 12, "dim", w=PT_RI - 120, h=24, halign="End")))''',
      '''    ap.append(("#" + egh, lab(PT + "En", "", 12, "dim", w=PT_RI - 120 - 116, h=24, halign="End", anchor={"right": 6})))
    ap.append(("#" + egh, G_.glass_button(PT + "Ef", "Fuse eggs", "secondary", w=110, h=24, size=12)))   # 0.3.70 (F2): egg fusing (the old Eggs tab)
    assert SUI.text_width(PT_TXT["eggsNote"], 12) <= PT_RI - 236 and SUI.text_width("Fuse eggs", 12, bold=True) <= 98, "0.3.70: the eggs header fits"''')
P.rep('''    binds = [("#%sT%d" % (PT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + PT + "Close", "close"), ("#" + PT + "Full", "full"),
                                                                                  ("#" + PT + "Pp", "pg:-1"), ("#" + PT + "Pnx", "pg:1")]''',
      '''    binds = [("#%sT%d" % (PT, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + PT + "Close", "close"),
                                                                                  ("#" + PT + "Pp", "pg:-1"), ("#" + PT + "Pnx", "pg:1"),
                                                                                  ("#" + PT + "Hp", "hp:-1"), ("#" + PT + "Hn", "hp:1")]   # 0.3.70''')
P.rep('''PT_DYN = (["Coins", "Close", "Full", "Cap", "Pn",''', '''assert PT + "Full" not in _pt_ids and not [b_ for b_ in PT_BINDS if b_[1] == "full"], "0.3.70: the pets screen has no Full page (no old Pets page link)"
PT_DYN = (["Coins", "Close", "Hp", "Hn", "Ef", "Cap", "Pn",''')
P.rep('''               ("FILL6", PT_FILL6), ("FILL6G", PT_FILL6G), ("HFOOT", PT_TXT["hfoot"])):
    F(ptd, "public static final String %s = %s;" % (_n, jstr(_v)))''', '''               ("FILL6", PT_FILL6), ("FILL6G", PT_FILL6G), ("HFOOT", PT_TXT["hfoot"]),
               # 0.3.70 (F2): the first-pet choice (Style Guide 15: the name in the Common colour, the tag gold, the buffs green, the click line yellow)
               ("STNOTE", "Choose your first pet: click one on the left, then click it again."), ("STOLD", "No pet yet - choose your first pet with /pets."),
               ("STFOOT", "Click: choose it (click it again to confirm)"), ("STOFF", "Not on this server - pick another one"),
               ("C_COMMON", PT_RCOL[1]), ("C_TAG", SUI.glass_col("xp")), ("C_HEAD", SUI.glass_col("dim")), ("C_GREEN", SUI.glass_col("green")),
               ("C_RED", SUI.glass_col("red")), ("C_FOOT", SUI.glass_col("action"))):
    F(ptd, "public static final String %s = %s;" % (_n, jstr(_v)))''')
P.rep('''C(ptab, r"""
public PetsTab(@PR@ pr, String via) {''', '''for _f in ("public int hpage;", "public int hpages;", "public String[] starts;"):   # 0.3.70 (F2): the Hatchery page, the starter cells
    F(ptab, _f)
C(ptab, r"""
public PetsTab(@PR@ pr, String via) {''')
P.rep('''  this.calls = 0;
}""")
# 0.3.59: THE MARKET SCREEN DATA''', '''  this.calls = 0;
  this.hpage = 0;
  this.hpages = 1;
  this.starts = new String[0];
}""")
# 0.3.59: THE MARKET SCREEN DATA''')
P.rep('''# the pets grid (p|id|rar|name|lv|icon|slot|tip) - pages of PER, nothing scrolls
M(ptab, r"""
public void fillGrid(@UCB@ b, @UEB@ ev, java.util.ArrayList ps, String[] hd) {
  int per = @PKG@.PetsTabData.PER;
  int n = ps.size() < per ? ps.size() : per;
  this.pageIds = new String[n];
  java.util.ArrayList sl = new java.util.ArrayList();
  for (int i = 0; i < per; i++) {
    if (i < n) {''', '''# 0.3.70 (F2): a starter cell's tooltip (st|i|type|name|icon|perk|on) in the Style Guide 15 layout
M(ptab, r"""
public static String scol(String hex, String t) { return "<color is=" + String.valueOf((char) 34) + hex + String.valueOf((char) 34) + ">" + t + "</color>"; }""")
M(ptab, r"""
public static String stTip(String[] f) {
  String nl = String.valueOf((char) 10);
  boolean on = "1".equals(f[6]);
  return scol(@PKG@.PetsTabData.C_COMMON, f[3]) + nl + scol(@PKG@.PetsTabData.C_TAG, "FIRST PET - " + f[2].toUpperCase()) + nl + nl
      + scol(@PKG@.PetsTabData.C_HEAD, "BONUS") + nl + scol(@PKG@.PetsTabData.C_GREEN, f[5].length() > 0 ? f[5] : "No buffs") + nl + nl
      + scol(on ? @PKG@.PetsTabData.C_FOOT : @PKG@.PetsTabData.C_RED, on ? @PKG@.PetsTabData.STFOOT : @PKG@.PetsTabData.STOFF);
}""")
# the pets grid (p|id|rar|name|lv|icon|slot|tip) - pages of PER, nothing scrolls; 0.3.70: an empty grid + a pending first-pet choice = the starters
M(ptab, r"""
public void fillGrid(@UCB@ b, @UEB@ ev, java.util.ArrayList ps, String[] hd, java.util.ArrayList stl) {
  int per = @PKG@.PetsTabData.PER;
  int n = ps.size() < per ? ps.size() : per;
  this.pageIds = new String[n];
  int sn = n == 0 && stl != null ? (stl.size() < per ? stl.size() : per) : 0;
  this.starts = new String[sn];
  java.util.ArrayList sl = new java.util.ArrayList();
  for (int i = 0; i < per; i++) {
    if (i < sn) {
      String[] f = (String[]) stl.get(i);
      boolean good = f.length >= 7;
      this.starts[i] = good ? f[1] : "";
      sl.add(good ? cell(f[4], 1, f[3] + " (" + f[2] + ")", stTip(f)) : new @IGS@());
    } else if (i < n) {''')
P.rep('''  else if (cnt == 0 && "1".equals(hd.length > 14 ? hd[14] : "0")) note = "No pet yet - choose your first pet on the Full page.";''',
      '''  else if (cnt == 0 && "1".equals(hd.length > 14 ? hd[14] : "0")) note = this.starts.length > 0 ? @PKG@.PetsTabData.STNOTE : @PKG@.PetsTabData.STOLD;   // 0.3.70''')
P.rep('''  int n = @PKG@.PetsTabData.HRN;
  this.hRows = new String[n];
  b.set("#SkyyPtabHc.Text", used + " / " + slots + " slots" + (cut > 0 ? "   -" + cut + "% time" : ""));
  for (int i = 0; i < n; i++) {
    String r = "SkyyPtabH" + i;
    String[] f = null;
    for (int j = 0; j < hl.size(); j++) { String[] x = (String[]) hl.get(j); if (x.length >= 10 && ni(x[1], -1) == i + 1) f = x; }
    String st = f == null ? (i + 1 > slots ? "lock" : "none") : f[2];
    if ("empty".equals(st)) st = "none";
    this.hRows[i] = st + "|" + (i + 1) + "|" + (f == null ? "" : f[8]);''', '''  int n = @PKG@.PetsTabData.HRN;
  this.hRows = new String[n];
  this.hpages = shown <= n ? 1 : (shown + n - 1) / n;   // 0.3.70 (F2): every slot SkyyPets sends, 6 a page
  if (this.hpage >= this.hpages) this.hpage = this.hpages - 1;
  if (this.hpage < 0) this.hpage = 0;
  int base = this.hpage * n;
  b.set("#SkyyPtabHc.Text", used + " / " + slots + " slots" + (cut > 0 ? "   -" + cut + "% time" : ""));
  for (int i = 0; i < n; i++) {
    String r = "SkyyPtabH" + i;
    int sn = base + i + 1;
    boolean past = this.hpage > 0 && sn > shown;
    b.set("#" + r + ".Visible", !past);
    if (past) { this.hRows[i] = null; continue; }
    String[] f = null;
    for (int j = 0; j < hl.size(); j++) { String[] x = (String[]) hl.get(j); if (x.length >= 10 && ni(x[1], -1) == sn) f = x; }
    String st = f == null ? (sn > slots ? "lock" : "none") : f[2];
    if ("empty".equals(st)) st = "none";
    this.hRows[i] = st + "|" + sn + "|" + (f == null ? "" : f[8]);''')
P.rep('''  b.set("#SkyyPtabHf.Text", shown > n ? (shown - n) + " more slots on the Full page" : @PKG@.PetsTabData.HFOOT);''',
      '''  int last = base + n < shown ? base + n : shown;
  b.set("#SkyyPtabHf.Text", this.hpages > 1 ? "Slots " + (base + 1) + "-" + last + " of " + shown + "  -  < > for more" : @PKG@.PetsTabData.HFOOT);   // 0.3.70
  b.set("#SkyyPtabHp.Visible", this.hpages > 1);
  b.set("#SkyyPtabHn.Visible", this.hpages > 1);''')
P.rep('''  ev.addEventBinding(@BT@.Activating, "#SkyyPtabEp", @EVD@.of("a", "place").append("t", this.tok));''',
      '''  ev.addEventBinding(@BT@.Activating, "#SkyyPtabEp", @EVD@.of("a", "place").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyPtabEf", @EVD@.of("a", "efuse").append("t", this.tok));   // 0.3.70 (F2): egg fusing''')
P.rep('''    b.set("#SkyyPtabPe2.Text", "Your pets could not be read right now - try again in a moment, or open the Full page.");''',
      '''    this.starts = new String[0];
    b.set("#SkyyPtabPe2.Text", "Your pets could not be read right now - try again in a moment.");   // 0.3.70: no Full page''')
P.rep('''  java.util.ArrayList cl = new java.util.ArrayList(), hl = new java.util.ArrayList();
  String[] d = null, tl = null, fu = null, fr = null;''', '''  java.util.ArrayList cl = new java.util.ArrayList(), hl = new java.util.ArrayList(), stl = new java.util.ArrayList();   // 0.3.70: + st| (SkyyPets 0.4.29)
  String[] d = null, tl = null, fu = null, fr = null;''')
P.rep('''    else if (l.startsWith("h|")) hl.add(sp(l, 10));
  }''', '''    else if (l.startsWith("h|")) hl.add(sp(l, 10));
    else if (l.startsWith("st|")) stl.add(sp(l, 7));
  }''')
P.rep('''  try { fillGrid(b, ev, ps, hd); } catch (Throwable t) { @PKG@.MenuUtil.warn("pets screen: the pets grid failed: " + t); }''',
      '''  try { fillGrid(b, ev, ps, hd, stl); } catch (Throwable t) { this.starts = new String[0]; @PKG@.MenuUtil.warn("pets screen: the pets grid failed: " + t); }''')
P.rep('''    if (a.equals("full")) { hub("character", "pets", "the Pets page"); return; }
''', '''    // 0.3.70 (oldmenu2 F2): no Full page here - this screen covers the old Pets page (a forged 'full' falls through)
''')
P.rep('''    if (a.startsWith("ar:")) { int r = @PKG@.InvPage.toInt(a.substring(3), 0); this.area = r < 0 || r > 7 ? 0 : r; this.page = 0; this.tcap = ""; redraw(); return; }''',
      '''    if (a.startsWith("ar:")) { int r = @PKG@.InvPage.toInt(a.substring(3), 0); this.area = r < 0 || r > 7 ? 0 : r; this.page = 0; this.tcap = ""; redraw(); return; }
    if (a.startsWith("hp:")) {                          // 0.3.70 (F2): the Hatchery's next / previous 6 slots (view only)
      int dp = @PKG@.InvPage.toInt(a.substring(3), 0);
      int np = this.hpage + (dp < 0 ? -1 : 1);
      if (np < 0 || np >= this.hpages) { say(np < 0 ? "These are the first Hatchery slots" : "These are the last Hatchery slots"); return; }
      this.hpage = np;
      this.tcap = "";
      redraw();
      return;
    }''')
P.rep('''    if (a.equals("g")) {
      int si = @PKG@.InvPage.ival(d, "SlotIndex", -1);
      if (si < 0 || si >= this.pageIds.length) { say("Nothing there"); return; }''', '''    if (a.equals("g")) {
      int si = @PKG@.InvPage.ival(d, "SlotIndex", -1);
      if (this.pageIds.length == 0 && si >= 0 && this.starts != null && si < this.starts.length && this.starts[si].length() > 0) {
        act("start", this.starts[si]);                  // 0.3.70 (F2): the first-pet choice (SkyyPets asks; the same pet again chooses)
        return;
      }
      if (si < 0 || si >= this.pageIds.length) { say("Nothing there"); return; }''')
P.rep('''    if (a.startsWith("hr:")) { hatchRow(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }''', '''    if (a.startsWith("hr:")) { hatchRow(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    if (a.equals("efuse")) {                            // 0.3.70 (F2): Fuse eggs = SkyyPets' egg fusing on the selected egg (it asks first)
      if (this.esel.length() == 0) { say("Select an egg in Your eggs first"); return; }
      act("efuse", this.esel);
      return;
    }''')

# ======================================================================= F3: THE MARKET TAB'S BANK = THE OLD BANK PAGE (a typed amount)
P.rep('''    ap.append(("#" + bkh, G_.glass_button(MT + "Bpg", "Bank page", "secondary", w=104, h=24, size=12)))''',
      '''    ap.append(("#" + bkh, G_.glass_button(MT + "Bpg", "Vault", "secondary", w=104, h=24, size=12)))   # 0.3.70: HubBar storage:bank = the Vault (items)''')
P.rep('''    ap.append(("#" + bar_, G_.glass_group(MT + "Ba", MT_BI - 76, 28, layout="Left")))''',
      '''    ap.append(("#" + bar_, G_.glass_group(MT + "Ba", len(MT_BAMT) * (MT_BCW + 4), 28, layout="Left")))   # 0.3.70: the chips, then the typed amount
    ap.append(("#" + bar_, G_.text_field(MT + "BqBox", MT + "Bq", w=MT_BI - 76 - len(MT_BAMT) * (MT_BCW + 4), h=28, placeholder="or type an amount", max_length=16, size=12)))
    assert MT_BI - 76 - len(MT_BAMT) * (MT_BCW + 4) >= 140, "0.3.70: the typed amount box is wide enough"''')
P.rep('''           "Am", "Oh", "Cl", "Claim", "Ac", "As", "Mgo", "Mn", "Bl", "Bpg", "Bv", "Bs", "Bb", "Bi", "Bn", "Ba", "Dep", "Wd", "Upg", "L1", "L2"]''',
      '''           "Am", "Oh", "Cl", "Claim", "Ac", "As", "Mgo", "Mn", "Bl", "Bpg", "Bv", "Bs", "Bb", "Bi", "Bn", "Ba", "Dep", "Wd", "Upg", "L1", "L2", "Bq", "BqBox"]''')
P.rep('''           "public long upUntil;", "public String bup;", "public long taxBp;",''', '''           "public long upUntil;", "public String bup;", "public long taxBp;", "public String btyped;",''')
P.rep('''  this.taxBp = -1L;
''', '''  this.taxBp = -1L;
  this.btyped = "";
''')
P.rep('''  ev.addEventBinding(@BT@.Activating, "#SkyyMtabDep", @EVD@.of("a", "dep").append("t", this.tok));
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabWd", @EVD@.of("a", "wd").append("t", this.tok));''', '''  String bk = String.valueOf((char) 64) + "B";   // 0.3.70 (F3): the typed amount rides on Deposit / Withdraw (the old Bank page's box)
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabDep", @EVD@.of("a", "dep").append("t", this.tok).append(bk, "#SkyyMtabBq.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyMtabWd", @EVD@.of("a", "wd").append("t", this.tok).append(bk, "#SkyyMtabBq.Value"));
  b.set("#SkyyMtabBqBox.Visible", this.bok);
  if (this.bok && this.btyped != null && this.btyped.length() > 0) b.set("#SkyyMtabBq.Value", this.btyped);''')
P.rep('''# one bank move through bank:fn:move with the panel's profile key + epoch''', '''# 0.3.70 (F3): a typed amount = what the old Bank page's box takes (500, 2k, 1.5m, all): letters, digits, . and , only, 16 at most; SkyyBank parses it
M(mtab, r"""
public static String amtClean(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 16; i++) {
    char c = s.charAt(i);
    if ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '.' || c == ',') sb.append(c);
  }
  return sb.toString().toLowerCase();
}""")
# one bank move through bank:fn:move with the panel's profile key + epoch''')
P.rep('''    if (a.equals("bank")) { hub("storage", "bank", "the Bank page"); return; }''',
      '''    if (a.equals("bank")) { hub("storage", "bank", "the Vault"); return; }   // 0.3.70: the bank itself is all on this card; this = the Vault''')
P.rep('''    if (a.startsWith("bamt:")) { int k = @PKG@.InvPage.toInt(a.substring(5), 0); this.bamt = k < 0 || k > 4 ? 0 : k; this.tcap = ""; redraw(); return; }''',
      '''    if (a.startsWith("bamt:")) { int k = @PKG@.InvPage.toInt(a.substring(5), 0); this.bamt = k < 0 || k > 4 ? 0 : k; this.btyped = ""; this.tcap = ""; redraw(); return; }   // 0.3.70: a chip clears the typed amount''')
P.rep('''    if (a.equals("dep") || a.equals("wd")) {
      String am = @PKG@.MarketTabData.BAMT[this.bamt];
      boolean all = am.equals("all");''', '''    if (a.equals("dep") || a.equals("wd")) {
      String ty = amtClean(@PKG@.InvPage.val(d, String.valueOf((char) 64) + "B"));   // 0.3.70 (F3): a typed amount wins over the chip
      this.btyped = ty;
      String am = ty.length() > 0 ? ty : @PKG@.MarketTabData.BAMT[this.bamt];
      boolean all = am.equals("all");''')

# ======================================================================= the ratchet: OLD_LEFT shrinks by the two rows this round brought in
P.rep('''OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"), ("character", "pets"), ("character", "stats"),
    ("character", "profiles"), ("market", "bazaar"), ("market", "merchants"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"), ("social", "players"), ("social", "party"), ("social", "guild"),
    ("settings", "mods"), ("settings", "setup"), ("smithing", "recipes")]))''', '''# 0.3.70 (oldmenu2): settings:mods (the Settings tab = the old Mods page) and character:pets (the Pets tab = the old Pets page) are gone.
# Still here: market:bazaar (buy orders / sell offers / cancel - needs SkyyBazaar ops), market:merchants (needs a SkyyMerchants bridge), storage:bank
# (= the Vault's item pages; the bank itself is all on the Market tab), market:auctions (the Auction House card's buttons open SkyyAuctions' own
# pages through opener(ah:fn:view / ah:fn:open, ..., "market", "auctions"); the scan counts opener(...) links too, so the ratchet tracks them until
# a browse / sell / my auctions / bids sub-tab - ah:fn read + act ops - replaces them).
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"), ("character", "stats"),
    ("character", "profiles"), ("market", "auctions"), ("market", "bazaar"), ("market", "merchants"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"), ("social", "players"), ("social", "party"), ("social", "guild"),
    ("settings", "setup"), ("smithing", "recipes")]))''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count(' = mk("') == MK0, "0.3.70: no system / command / class"
_i = P.s.index
assert _i("public static String[] chunks(String s, int mx)") < _i("public void fillModRows(") < _i("public void fillSettings(") \
    and _i("public void fillTail(") < _i("public void fillSettings(") and _i("public void setupOf(String m)") < _i("public void setupMod(int k)") \
    < _i("public void modClick(String kind, int i)") < _i("public void handleDataEvent(@REF@ ref, @ST@ st, String d) {\n  String a = @PKG@.InvPage.val(d, \"a\");\n  if (a == null) a = \"\";\n  this.answered = false;\n  try {\n    if (this.closed) { this.answered = true; return; }\n    this.pref = ref;\n    this.pst = st;\n    String dq") \
    and _i("public static String stTip(String[] f)") < _i("public void fillGrid(@UCB@ b, @UEB@ ev, java.util.ArrayList ps, String[] hd, java.util.ArrayList stl)") \
    and _i("public static String amtClean(String s)") < _i('      String ty = amtClean('), "0.3.70: methods before their callers"
P.finish()


# ======================================================================= the HARNESS (every 0.3.69 check runs again on the 0.3.70 jar, plus OLD2)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


EXPECT_70 = '''EXPECT = {   # 0.3.70: the Settings tab's mods views, the Pets tab's starters / Hatchery pages / egg fusing, the bank's typed amount, the version strings
@@EXPECT@@
}
'''
HARNESS_OLD2_STATIC = r'''    # ---- OLD2 (0.3.70; Skyy 11-22 "build it all into the new system"): the ratchet shrank by exactly the rows this round brought in
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left2_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1))) if m_left_ else set()
    m_lo_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", o, re.S)
    lefto_ = set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_lo_.group(1))) if m_lo_ else set()
    op_re_ = r'opener\("[a-z:]+", new Object\[\] \{[^}]*\}, "([a-z]+)", "([a-z]+)"'
    ops_o_ = set(re.findall(op_re_, o[o.index("# ================= 0.3.50 THE INVENTORY SCREEN"):o.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")]))
    K.check(lefto_ - left2_ == set([("settings", "mods"), ("character", "pets")]) and left2_ - lefto_ == set([("market", "auctions")])
            and ("market", "auctions") in ops_o_ and len(left2_) == len(lefto_) - 1,
            "OLD2 RATCHET OLD_LEFT lost settings:mods + character:pets; the one row added = market:auctions, an opener link 0.3.69 already had, now tracked (%d -> %d; still: %s)" % (len(lefto_), len(left2_), sorted(left2_)))
    K.check('hub("settings", "mods"' not in g and 'hub("character", "pets"' not in g and '("#" + PT + "Full", "full")' not in g
            and "0.3.70: the pets screen has no Full page (no old Pets page link)" in g and "on the Full page" not in g
            and "Your pets could not be read right now - try again in a moment, or open the Full page." not in g and "more on the Mods page" not in g,
            "OLD2 STATIC no Mods page / Pets page link, no Pets Full button, no Pets / Mods text pointing at an old page (the Bazaar's Full page stays: OLD_LEFT)")
    K.check('hub("storage", "bank", "the Vault")' in g and 'G_.glass_button(MT + "Bpg", "Vault"' in g and 'act("start", this.starts[si]);' in g
            and 'act("efuse", this.esel);' in g and 'setupOf(@PKG@.MenuData.MOD_NAME[k]);' in g and 'setupOf(this.mods[k]);' in g,
            "OLD2 STATIC the Vault button keeps storage:bank; starters / egg fusing go through pets:fn:tabact; Set up + the Server Setup card share setupOf")
'''
HARNESS_OLD2 = r'''    # ---- OLD2 F2 (0.3.70): THE PETS TAB = THE OLD PETS PAGE - the first-pet choice, every Hatchery slot, egg fusing (on the TAB2 stand-ins)
    PW["start"] = None
    PW["chosen"] = None
    PW["efuse"] = None
    PW["hslots"] = 6
    PW["stOn"] = False

    def f_tab70(o):
        s_ = f_tab(o)
        if s_ is None:
            return None
        ls_ = s_.split("\n")
        hd_ = ls_[0].split("|")
        if PW["stOn"]:
            ls_ = [l_ for l_ in ls_ if not l_.startswith("p|")]
            hd_[2], hd_[6], hd_[14] = "0", "0", "1"
            for i_, (ty_, nm_) in enumerate((("Mining", "Mouse"), ("Farming", "Rabbit"), ("Foraging", "Squirrel"), ("Combat", "Dog"))):
                ls_.append("st|%d|%s|%s|Skyy_PetIcon_%s_Common|Up to +44 %s Fortune at Lv 50|%d" % (i_, ty_, nm_, nm_, ty_, 0 if i_ == 3 else 1))
        if PW["hslots"] > 6:
            hd_[9], hd_[10] = str(PW["hslots"]), str(PW["hslots"])
            ls_ = [l_ for l_ in ls_ if not l_.startswith("h|")]
            for n_ in range(1, PW["hslots"] + 1):
                ls_.append("h|%d|wait|Egg_U|Uncommon Farming Egg|2|4320000|7200000|hid%d|Hatching" % (n_, n_) if n_ in (2, 8, 13)
                           else "h|%d|empty|||0|0|0||Empty" % n_)
        ls_[0] = "|".join(hd_)
        return "\n".join(ls_)

    def f_act70(o):
        a_ = [str(x) for x in list(o)]
        if a_[2] == "start" and a_[1] == PW["tok"]:
            PW["acts"].append(a_)
            if PW["start"] == a_[3]:
                PW["chosen"], PW["start"], PW["stOn"] = a_[3], None, False
                return "+Your first pet is a Common Squirrel (Foraging)! It is in your pet slot."
            PW["start"] = a_[3]
            return "=Make the Squirrel (Foraging) your first pet? Press Choose on it again - this cannot be changed."
        if a_[2] == "efuse" and a_[1] == PW["tok"]:
            PW["acts"].append(a_)
            if PW["efuse"] == a_[3]:
                PW["efuse"] = None
                PW["inv"]["Egg_C"] -= 2
                PW["inv"]["Egg_U"] += 1
                return "+Fused 2 Common Mining Eggs into 1 Uncommon Mining Egg."
            PW["efuse"] = a_[3]
            return "=Fuse 2 Common Mining Eggs into 1 Uncommon Mining Egg? Click it again."
        return f_act(o)
    BR.put("pets:fn:tab", Fn(f_tab70))
    BR.put("pets:fn:tabact", Fn(f_act70))
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    E.pump(PK)
    PW["stOn"] = True
    PW["tok"] = "prof-A"
    f0_ = len(E.sent(PK))
    PS = PTB.open(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    pk_ = pages(PK, f0_)
    cm = cmap(pk_[0]) if pk_ else {}
    g_ = str(sval(cm, "#SkyyPtabG.Slots"))
    K.check(len(pk_) == 1 and [str(x) for x in PS.starts] == ["0", "1", "2", "3"] and "Mouse (Mining)" in g_ and "Dog (Combat)" in g_
            and "FIRST PET - FORAGING" in g_ and str(PTD.STFOOT) in g_ and str(PTD.STOFF) in g_ and str(PTD.C_COMMON) in g_ and str(PTD.C_GREEN) in g_
            and str(sval(cm, "#SkyyPtabPe2.Text")) == str(PTD.STNOTE),
            "OLD2 F2 START no pets + a pending choice = the 4 starters in the grid (Common colour, FIRST PET - type, buffs green, click line; an off kind red), the note")
    K.notes.append("OLD2 the starter grid: %s" % g_[:600])
    n0 = len(PW["acts"])
    p_ = pt_ev({"a": "g", "SlotIndex": 2, "t": str(PS.tok)}, "OLD2 F2 START click the Squirrel")
    K.check(PW["acts"][-1][1:] == ["prof-A", "start", "2"] and "Press Choose on it again" in str(sval(cmap(p_), "#SkyyPtabCap.Text")) and PW["chosen"] is None,
            "OLD2 F2 START a starter click = tabact start <type> with the profile token; SkyyPets' ask shown, nothing chosen")
    p_ = pt_ev({"a": "g", "SlotIndex": 2, "t": str(PS.tok)}, "OLD2 F2 START click it again")
    K.check(PW["chosen"] == "2" and "Your first pet is a Common Squirrel" in str(sval(cmap(p_), "#SkyyPtabCap.Text")) and len(PS.starts) == 0 and len(PS.pageIds) > 0,
            "OLD2 F2 START the same pet again = chosen (SkyyPets' chooseStarter); the redraw shows the pets, no starters")
    old_ = str(PS.tok)
    n1 = len(PW["acts"])
    p_ = pt_ev({"a": "g", "SlotIndex": 2, "t": "nope"}, "OLD2 SAFE a forged token on a starter click")
    K.check(len(PW["acts"]) == n1, "OLD2 SAFE a forged / old page token never reaches SkyyPets")
    p_ = pt_ev({"a": "g", "SlotIndex": 40, "t": str(PS.tok)}, "OLD2 SAFE an empty cell")
    K.check(len(PW["acts"]) == n1, "OLD2 SAFE an empty cell = a caption, no call")
    # an older SkyyPets (no st| lines): the note points at /pets, never at a Full page
    PW["stOn"] = True
    BR.put("pets:fn:tab", Fn(lambda o: "\n".join(l_ for l_ in f_tab70(o).split("\n") if not l_.startswith("st|"))))
    p_ = pt_ev({"a": "ro:0"}, "OLD2 F2 START SkyyPets 0.4.28 (no starter lines)")
    K.check(str(sval(cmap(p_), "#SkyyPtabPe2.Text")) == str(PTD.STOLD) and len(PS.starts) == 0, "OLD2 F2 FALL no starter lines = the /pets hint, no starter cells")
    PW["stOn"] = False
    BR.put("pets:fn:tab", Fn(f_tab70))
    # EVERY HATCHERY SLOT: 14 slots = 3 pages of 6
    PW["hslots"] = 14
    p_ = pt_ev({"a": "ro:0"}, "OLD2 F2 HATCH 14 slots")
    cm = cmap(p_)
    K.check(int(PS.hpages) == 3 and int(PS.hpage) == 0 and str(sval(cm, "#SkyyPtabHf.Text")).startswith("Slots 1-6 of 14") and sval(cm, "#SkyyPtabHp.Visible") in (True, "true")
            and str(PS.hRows[1]).startswith("wait|2|hid2"), "OLD2 F2 HATCH 14 slots = 3 pages, page 1 shows slots 1-6, the arrows show")
    p_ = pt_ev({"a": "hp:1"}, "OLD2 F2 HATCH next 6")
    cm = cmap(p_)
    K.check(int(PS.hpage) == 1 and str(sval(cm, "#SkyyPtabHf.Text")).startswith("Slots 7-12 of 14") and str(PS.hRows[1]).startswith("wait|8|hid8")
            and str(PS.hRows[0]).startswith("none|7|"), "OLD2 F2 HATCH > = slots 7-12 (row 2 = slot 8, its hid)")
    p_ = pt_ev({"a": "hr:1", "t": str(PS.tok)}, "OLD2 F2 HATCH Take out slot 8")
    K.check(PW["acts"][-1][2:] == ["take", "8|hid8"], "OLD2 F2 HATCH a row's button carries the REAL slot number (take 8|hid8)")
    p_ = pt_ev({"a": "hp:1"}, "OLD2 F2 HATCH the last 2")
    cm = cmap(p_)
    K.check(int(PS.hpage) == 2 and str(sval(cm, "#SkyyPtabHf.Text")).startswith("Slots 13-14 of 14") and sval(cm, "#SkyyPtabH2.Visible") in (False, "false")
            and sval(cm, "#SkyyPtabH1.Visible") in (True, "true") and PS.hRows[2] is None, "OLD2 F2 HATCH the last page shows only slots 13-14 (rows past it hidden)")
    n1 = len(PW["acts"])
    p_ = pt_ev({"a": "hr:4", "t": str(PS.tok)}, "OLD2 SAFE a hidden row")
    K.check(len(PW["acts"]) == n1 and "Nothing there" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "OLD2 SAFE a forged click on a hidden row = a caption, no call")
    p_ = pt_ev({"a": "hp:1"}, "OLD2 F2 HATCH past the last")
    K.check("last Hatchery" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "OLD2 F2 HATCH past the last page = a caption")
    PW["hslots"] = 6
    p_ = pt_ev({"a": "ro:0"}, "OLD2 F2 HATCH back to 6 slots")
    cm = cmap(p_)
    K.check(int(PS.hpages) == 1 and int(PS.hpage) == 0 and str(sval(cm, "#SkyyPtabHf.Text")) == str(PTD.HFOOT) and sval(cm, "#SkyyPtabHp.Visible") in (False, "false"),
            "OLD2 F2 HATCH 6 slots or fewer = one page, the old footer, no arrows (a stale page number snaps back)")
    # EGG FUSING
    PW["inv"]["Egg_C"], PW["inv"]["Egg_U"] = 2, 0
    p_ = pt_ev({"a": "ro:0"}, "OLD2 F2 EFUSE redraw")
    K.check(len([b_ for b_ in binds_of(p_) if '"efuse"' in b_[2] and "SkyyPtabEf" in b_[1]]) == 1, "OLD2 F2 EFUSE Fuse eggs bound with the page token")
    p_ = pt_ev({"a": "efuse", "t": str(PS.tok)}, "OLD2 F2 EFUSE first press")
    K.check(PW["acts"][-1][2:] == ["efuse", str(PS.esel)] and PW["inv"]["Egg_C"] == 2 and "Click it again" in str(sval(cmap(p_), "#SkyyPtabCap.Text")),
            "OLD2 F2 EFUSE Fuse eggs = tabact efuse <the selected egg>; SkyyPets asks, nothing moves")
    p_ = pt_ev({"a": "efuse", "t": str(PS.tok)}, "OLD2 F2 EFUSE second press")
    K.check(PW["inv"]["Egg_C"] == 0 and PW["inv"]["Egg_U"] == 1 and "Fused" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "OLD2 F2 EFUSE the second press fuses (SkyyPets' door), once")
    n1 = len(PW["acts"])
    p_ = pt_ev({"a": "efuse", "t": old_}, "OLD2 SAFE an old drawing's Fuse eggs")
    K.check(len(PW["acts"]) == n1, "OLD2 SAFE Fuse eggs from an older drawing = no call")
    PS.esel = ""
    PW["inv"]["Egg_C"], PW["inv"]["Egg_U"] = 0, 0
    p_ = pt_ev({"a": "ro:0"}, "OLD2 F2 EFUSE no eggs")
    p_ = pt_ev({"a": "efuse", "t": str(PS.tok)}, "OLD2 F2 EFUSE with no egg selected")
    K.check(len(PW["acts"]) == n1 and "Select an egg" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "OLD2 F2 EFUSE no egg selected = a caption, no call")
    PW["inv"]["Egg_C"], PW["inv"]["Egg_U"] = 2, 0
    p_ = pt_ev({"a": "full"}, "OLD2 F2 a forged Full page")
    K.check(PK.pm.getCustomPage() == PS and "The page changed" in str(sval(cmap(p_), "#SkyyPtabCap.Text")), "OLD2 F2 a forged 'full' opens no old page (the screen stays)")
    BR.put("pets:fn:tab", Fn(f_tab))
    BR.put("pets:fn:tabact", Fn(f_act))
'''
HARNESS_OLD2_BANK = r'''    # ---- OLD2 F3 (0.3.70): THE BANK CARD TAKES A TYPED AMOUNT (the old Bank page's box); the Bank page button = the Vault
    if PK.pm.getCustomPage() is not MS:
        MS = MTB.open(PK.ref, PK.st, PK.pr, "test")
        E.pump(PK)
    p_ = mt_ev({"a": "bamt:0"}, "OLD2 F3 redraw")
    cm = cmap(p_)
    K.check(sval(cm, "#SkyyMtabBqBox.Visible") in (True, "true") and len([b_ for b_ in binds_of(p_) if '"dep"' in b_[2] and "SkyyMtabBq.Value" in b_[2]]) == 1
            and len([b_ for b_ in binds_of(p_) if '"wd"' in b_[2] and "SkyyMtabBq.Value" in b_[2]]) == 1, "OLD2 F3 the typed box shows; Deposit / Withdraw carry its value")
    nb0 = len(MW["bmoves"])
    p_ = mt_ev({"a": "dep", "t": str(MS.tok), "@B": "2.5K"}, "OLD2 F3 Deposit a typed 2.5k")
    K.check(len(MW["bmoves"]) == nb0 + 1 and MW["bmoves"][-1][1:3] == ["deposit", "2.5k"] and str(MS.btyped) == "2.5k",
            "OLD2 F3 a typed amount = bank:fn:move deposit <typed> (cleaned, lower case), kept in the box (%s)" % MW["bmoves"][-1:])
    p_ = mt_ev({"a": "wd", "t": str(MS.tok), "@B": "all"}, "OLD2 F3 Withdraw typed all")
    K.check(MW["bmoves"][-1][1:3] == ["wdall", ""], "OLD2 F3 typed 'all' = wdall (the exact Withdraw all door)")
    p_ = mt_ev({"a": "dep", "t": str(MS.tok), "@B": "1|0\"0<b>"}, "OLD2 F3 a junk typed amount")
    K.check(MW["bmoves"][-1][1:3] == ["deposit", "100b"], "OLD2 F3 junk characters are dropped before SkyyBank parses it (%s)" % MW["bmoves"][-1:])
    p_ = mt_ev({"a": "dep", "t": str(MS.tok), "@B": "3k"}, "OLD2 F3 Deposit a typed 3k (fix check)")
    K.check(str(sval(cmap(p_), "#SkyyMtabBq.Value")) == "3k", "OLD2 FIX the redraw after a typed Deposit puts the typed amount back in the box (%s)" % sval(cmap(p_), "#SkyyMtabBq.Value"))
    p_ = mt_ev({"a": "bamt:2"}, "OLD2 F3 a chip clears the typed amount")
    K.check(sval(cmap(p_), "#SkyyMtabBq.Value") is None and sval(cmap(p_), "#SkyyMtabBqBox.Visible") in (True, "true") and bool(getattr(p_, "clear", True))
            and str(MS.btyped) == "",
            "OLD2 FIX a chip click = a full page rebuild that never puts the old typed amount back (the box comes back empty; clear=%s)" % getattr(p_, "clear", "?"))
    p_ = mt_ev({"a": "dep", "t": str(MS.tok), "@B": ""}, "OLD2 F3 Deposit with the chip")
    K.check(str(MS.btyped) == "" and MW["bmoves"][-1][1:3] == ["deposit", "100k"], "OLD2 F3 an empty box = the chip (100k), as before")
    n2 = len(MW["bmoves"])
    p_ = mt_ev({"a": "dep", "t": "old", "@B": "5k"}, "OLD2 SAFE an old drawing's Deposit")
    K.check(len(MW["bmoves"]) == n2, "OLD2 SAFE Deposit from an older drawing = nothing moved")
    K.check("Vault" in str(sval(cmap(p_), "#SkyyMtabBpg.Text")) or 'G_.glass_button(MT + "Bpg", "Vault"' in open(GEN, encoding="utf8").read(), "OLD2 F3 the old Bank page button reads Vault")
'''
HARNESS_OLD2_MODS = r'''    # ---- OLD2 F1 (0.3.70): THE SETTINGS TAB = THE OLD MODS PAGE (the card's mod buttons, All mods, one mod's help + commands, Set up for admins)
    GS, p_ = g_open("OLD2 F1 open")
    cm = cmap(p_)
    mods7_ = [i_ for i_ in range(len(MDc6.MOD_NAME)) if bool(JV("AdminPage").installed(i_))]
    vis7_ = bool(MH.visible("mods", PK.pr))
    lbj_ = " ".join(str(x_) for x_ in SGD.LB)
    K.check(len(mods7_) >= 1 and 'Text: "All mods"' in lbj_ and 'Text: "Mods page"' not in lbj_ and "TextButton #SkyyGtabM0 " in lbj_
            and (not vis7_ or (vis6(cm, "M0") and len([b_ for b_ in binds_of(p_) if '"mq:0"' in b_[2]]) == 1)),
            "OLD2 F1 the Mods card: its mod names are buttons (mq:<slot>), the old 'Mods page' button = All mods (%d installed, visible %s)" % (len(mods7_), vis7_))
    MC0_ = JV("MenuCfg")
    mh0_ = bool(MC0_.MODS_HELP)
    MC0_.MODS_HELP = True
    p_ = g_ev({"a": "mods"}, "OLD2 F1 All mods")
    cm = cmap(p_)
    K.check(int(GS.mview) == 1 and str(PK.pm.getCustomPage().getClass().getSimpleName()) == "SettingsTab" and txt6(cm, "Lh").startswith("ALL MODS")
            and txt6(cm, "R0N").startswith(str(MDc6.MOD_NAME[mods7_[0]]) + " ") and len([b_ for b_ in binds_of(p_) if '"mh:0"' in b_[2]]) == 1
            and txt6(cm, "Al") == str(SGD.MODSAL) and not [b_ for b_ in binds_of(p_) if '"on:' in b_[2] or '"ms:' in b_[2]] and not cats6(p_) == [] ,
            "OLD2 F1 All mods = the list view in the big list (name + version, Help; no ON / OFF, no Set up for a plain player), the screen stays")
    p_ = g_ev({"a": "on:0", "t": str(GS.tok)}, "OLD2 SAFE a forged ON in the mods list")
    K.check("No setting there" in cap6(p_), "OLD2 SAFE a forged ON on a mods row = 'No setting there', nothing written")
    p_ = g_ev({"a": "mh:0", "t": str(GS.tok)}, "OLD2 F1 Help on the first mod")
    cm = cmap(p_)
    k0_ = mods7_[0]
    body_ = str(JV("MenuUtil").modBodyFor(k0_, False))
    K.check(int(GS.mview) == 2 and int(GS.modk) == k0_ and "help and commands" in txt6(cm, "Lh") and txt6(cm, "R0N") == "What it does"
            and body_.split("\n")[0].startswith(txt6(cm, "R0D")) and "COMMANDS" in [txt6(cm, "R%dN" % r_) for r_ in range(int(SGD.RN))]
            and txt6(cm, "Al") == str(SGD.MODHAL), "OLD2 F1 Help = that mod's text (MenuUtil.modBodyFor, the old Mods page's): What it does, COMMANDS, each command row")
    rows_ = []
    for pg_ in range(int(GS.pages)):
        if pg_ > 0:
            p_ = g_ev({"a": "pg:1"}, "OLD2 F1 help page %d" % (pg_ + 1))
            cm = cmap(p_)
        rows_ += [(txt6(cm, "R%dN" % r_), txt6(cm, "R%dD" % r_)) for r_ in range(int(SGD.RN)) if vis6(cm, "R%d" % r_)]
    lines_ = body_.split("\n")[1:]
    cmd_ok_ = all(any((n_ + " - " + d_) == l_ or (n_ == "" and d_ == l_) or (l_.endswith(":") and n_ == l_[:-1].upper()) for n_, d_ in rows_) for l_ in lines_ if l_)
    K.check(cmd_ok_ and len(rows_) >= len([l_ for l_ in lines_ if l_]), "OLD2 F1 every line of the old Mods text is a row, nothing lost (%d rows over %d page(s))" % (len(rows_), int(GS.pages)))
    p_ = g_ev({"a": "mh:0", "t": str(GS.tok)}, "OLD2 SAFE Help in the one-mod view")
    K.check("No mod there" in cap6(p_), "OLD2 SAFE a forged Help outside the list = a caption")
    p_ = g_ev({"a": "ms:0", "t": str(GS.tok)}, "OLD2 SAFE Set up, plain player")
    K.check(str(PK.pm.getCustomPage().getClass().getSimpleName()) == "SettingsTab", "OLD2 SAFE a plain player's Set up opens nothing")
    p_ = g_ev({"a": "mq:0", "t": str(GS.tok)}, "OLD2 F1 the card's first mod")
    K.check(int(GS.mview) == 2 and int(GS.modk) == int(GS.mcard[0]), "OLD2 F1 a mod button on the card = that mod's help")
    p_ = g_ev({"a": "mq:11", "t": "stale"}, "OLD2 SAFE a stale card click")
    K.check("The page changed" in cap6(p_), "OLD2 SAFE a card click from an older drawing = said, redrawn")
    p_ = g_ev({"a": "cat:%d" % cook_, "t": str(GS.tok)}, "OLD2 F1 a category = back to the settings")
    K.check(int(GS.mview) == 0 and len([b_ for b_ in binds_of(p_) if '"on:0"' in b_[2]]) == 1, "OLD2 F1 a category = the settings again (ON / OFF rows)")
    p_ = g_ev({"a": "mods"}, "OLD2 F1 All mods again")
    p_ = g_ev({"a": "find", "t": str(GS.tok), "@Q": "harness"}, "OLD2 F1 a search from the mods list")
    K.check(int(GS.mview) == 0 and "Search" in txt6(cmap(p_), "Lh"), "OLD2 F1 a search = the settings search (the mods view left)")
    MC0_.MODS_HELP = False
    if not bool(MH.visible("mods", PK.pr)):
        p_ = g_ev({"a": "mods"}, "OLD2 SAFE All mods, hidden")
        K.check(int(GS.mview) == 0 and cap6(p_) == str(SGD.MODSOFF), "OLD2 SAFE the mods list hidden for a plain player (menu.modsHelp off) = the old rule's text, no list")
        p_ = g_ev({"a": "mq:0", "t": str(GS.tok)}, "OLD2 SAFE a card click, hidden")
        K.check(int(GS.mview) == 0 and cap6(p_) == str(SGD.MODSOFF), "OLD2 SAFE a card click while hidden = the rule's text")
    MC0_.MODS_HELP = mh0_
'''
HARNESS_OLD2_ADMIN = r'''    # OLD2 F1 admin: Set up on a mod with a Server Setup page = AdminPage on that mod (the old Mods list's modcfg path)
    had_ = BR.get("config:def:SkyyIslands")
    BR.put("config:def:SkyyIslands", _JA(OBJ6)(["x", "", "Islands", "1.0", "", _JA(JS)([]), _JA(JS)([]), _JA(OBJ6)([]), "", ""]))
    JV("MenuIdx").scan()
    GO, p_ = g_open("OLD2 F1 admin", P_=PO6)
    p_ = g_ev({"a": "mods"}, "OLD2 F1 admin All mods", P_=PO6)
    cm = cmap(p_)
    names_ = [txt6(cm, "R%dN" % r_) if vis6(cm, "R%d" % r_) else "" for r_ in range(int(SGD.RN))]
    hrow_ = [r_ for r_, n_ in enumerate(names_) if n_.startswith("SkyyIslands ")]
    adm_ok_ = [b_ for b_ in binds_of(p_) if '"ms:' in b_[2]]
    want_ = [r_ for r_, n_ in enumerate(names_) if n_ and JV("AdminPage").hdr(n_.split(" ")[0]) is not None]
    K.notes.append("OLD2 admin list rows: %s, Set up buttons %d" % (names_, len(adm_ok_)))
    K.check(hrow_ and len(adm_ok_) == len(want_) and hrow_[0] in want_ and len([b_ for b_ in binds_of(p_) if '"ms:%d"' % hrow_[0] in b_[2]]) == 1,
            "OLD2 F1 admin: a Set up button exactly on the rows whose mod has a Server Setup page (SkyyIslands here; %d)" % len(adm_ok_))
    f0_ = len(E.sent(PO6))
    GO.handleDataEvent(PO6.ref, PO6.st, json.dumps({"a": "ms:%d" % (hrow_[0] if hrow_ else 0), "t": str(GO.tok)}))
    E.pump(PO6)
    cur_ = PO6.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "AdminPage" and str(cur_.view) == "mod" and str(cur_.mod) == "SkyyIslands"
            and bool(GO.closed) and len(pages(PO6, f0_)) == 1,
            "OLD2 F1 admin Set up = Server Setup on that mod (AdminPage view mod, ONE packet) - the old Mods list's modcfg path (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    if had_ is None:
        BR.remove("config:def:SkyyIslands")
    else:
        BR.put("config:def:SkyyIslands", had_)
    JV("MenuIdx").scan()
'''
T.rep('''"""Harness for SkyyMenu 0.3.69 (the old menu switch; tools/menu_0_3_69_patch.py, round oldmenu1).''',
      '''"""Harness for SkyyMenu 0.3.70 (old menu follow-ups F1 + F2 + F3; tools/menu_0_3_70_patch.py, round oldmenu2).
GENERATED by tools/menu_0_3_70_patch.py from the 0.3.69 harness (edit the patch, not this file): every 0.3.69 check runs again on the
0.3.70 jar (TAB6: the Mods page link is now the All mods view; TAB2: a forged Full page stays on the screen; OLD1: compared with 0.3.69), plus
  OLD2 STATIC   the ratchet: OLD_LEFT lost settings:mods + character:pets, tracks market:auctions (the scan counts opener links); no Mods /
                Pets page link, no Pets Full button,
                no text pointing at a Full page; the Vault button keeps storage:bank
       F1       (the real SettingsTab) the Mods card's mod buttons, All mods (list), Help (one mod's text = MenuUtil.modBodyFor, every line a
                row, nothing lost, pages), a category / a search = back to the settings, forged ON / Help / Set up / stale clicks, the old
                rule (menu.modsHelp off = hidden for players); admin Set up = AdminPage on that mod
       F2       (the TAB2 stand-ins + st| lines) the 4 starters in the empty grid (Style Guide 15 tooltip), click = tabact start, twice =
                chosen; an older SkyyPets = the /pets hint; 14 Hatchery slots in 3 pages (real slot numbers on the buttons, hidden rows
                refused); Fuse eggs = tabact efuse (ask, then fuse once; old drawing / no egg = no call); a forged Full page opens nothing
       F3       (the TAB3 stand-ins) the bank's typed amount: Deposit / Withdraw carry it, cleaned + lower case, 'all' = wdall / depall, a chip
                clears it, an old drawing moves nothing; the Bank page button reads Vault
The 0.3.69 harness text follows:
Harness for SkyyMenu 0.3.69 (the old menu switch; tools/menu_0_3_69_patch.py, round oldmenu1).''')
T.rep(r'''    links_ = sorted(set(re.findall(r'(?:openHub|hub)\("([a-z]+)", "([a-z]+)"', g[i_new_:i_end_])))''',
      r'''    links_ = sorted(set(re.findall(r'(?:openHub|hub)\("([a-z]+)", "([a-z]+)"', g[i_new_:i_end_])
                        + re.findall(r'opener\("[a-z:]+", new Object\[\] \{[^}]*\}, "([a-z]+)", "([a-z]+)"', g[i_new_:i_end_])))   # 0.3.70: + opener links (the AH)''')
T.rep('VERSION = "0.3.69"\nJAR', 'VERSION = "0.3.70"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.68.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.69.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.68.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.69.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_69_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_70_patch.py")')
T.rep('"scratch", "oldmenu1", "menu"', '"scratch", "oldmenu2", "menu"')
T.rep('ADDED = []   # 0.3.69: no new class\n', 'ADDED = []   # 0.3.70: no new class\n')
EXPECT_BODY = '''    "SettingsTab": ["+f mcard", "+f modk", "+f mrow", "+f mview", "+m chunks", "+m fillModRows", "+m fillMods", "+m fillTail", "+m modClick", "+m setupOf",
                    "-m fillMods", "~c ", "~m build", "~m fillSettings", "~m handleDataEvent", "~m setupMod"],   # F1 (fillMods takes the event builder now)
    "SettingsTabData": ["+f BW", "+f MCUT", "+f MODHAL", "+f MODSAL", "~<clinit>"],
    "PetsTab": ["+f hpage", "+f hpages", "+f starts", "+m fillGrid", "+m scol", "+m stTip", "-m fillGrid", "~c ", "~m build", "~m fillEggs", "~m fillHatch",
                "~m handleDataEvent"],   # F2 (fillGrid takes the starter lines now)
    "PetsTabData": ["+f C_COMMON", "+f C_FOOT", "+f C_GREEN", "+f C_HEAD", "+f C_RED", "+f C_TAG", "+f STFOOT", "+f STNOTE", "+f STOFF", "+f STOLD", "~<clinit>"],
    "MarketTab": ["+f btyped", "+m amtClean", "~c ", "~m build", "~m fillBank", "~m handleDataEvent"],   # F3
    "MarketTabData": ["~<clinit>"], "MenuData": ["~<clinit>"], "OpsPage": ["~<clinit>"],   # the page data / version strings
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyMenuPlugin": ["~m setup"],'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.69:', 'if "--expect-dump" in sys.argv:'), EXPECT_70.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.69"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.70"') == 1, "S VERSION")
''' + HARNESS_OLD2_STATIC.rstrip("\n"))
# OLD1 STATIC compared 0.3.69 with 0.3.68 (7 'main' opens went through MenuHub.home): against 0.3.69 the count is unchanged
T.rep('''g.count('new @PKG@.MenuPage(') == o.count('new @PKG@.MenuPage(') - 7,''', '''g.count('new @PKG@.MenuPage(') == o.count('new @PKG@.MenuPage('),   # 0.3.70: vs 0.3.69 (that round removed 7)''')
# TAB6: the Mods page link is now the All mods view (the screen stays)
T.rep('''    for a_, what, want_ in (("mods", "Mods page", None),):   # 0.3.69: no Full page on the Settings tab (OLD1)''',
      '''    for a_, what, want_ in (("mods", "All mods (0.3.70: the old Mods page in this screen)", "SettingsTab"),):   # 0.3.70 (OLD2 F1)''')
# TAB2: a forged Full page stays on the pets screen
T.rep('''    K.check(len(pages(PK, f0_)) == 1, "TAB2 TABS Full page = today's Pets page route, ONE packet (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))''',
      '''    K.check(len(pages(PK, f0_)) == 1 and cur_ is not None and str(cur_.getClass().getSimpleName()) == "PetsTab",
            "TAB2 TABS a forged Full page (0.3.70: gone) = the pets screen redrawn, ONE packet, no old page (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))''')
T.rep('''    K.notes.append("TAB2 counters: opens %d, stale %d, reads %d, acts %d" % (int(PTB.OPENS), int(PTB.STALE), len(PW["reads"]), len(PW["acts"])))''',
      HARNESS_OLD2.rstrip("\n") + '''
    K.notes.append("TAB2 counters: opens %d, stale %d, reads %d, acts %d" % (int(PTB.OPENS), int(PTB.STALE), len(PW["reads"]), len(PW["acts"])))''')
T.rep('''    # links to the old pages (each ONE packet)
    for a_, what, want_ in''', HARNESS_OLD2_MODS.rstrip("\n") + '''
    # links to the old pages (each ONE packet)
    for a_, what, want_ in''')
T.rep('''    K.check(len(MW["bmoves"]) == nb, "TAB3 SAFE any other click between the two presses cancels the upgrade ask")
''', '''    K.check(len(MW["bmoves"]) == nb, "TAB3 SAFE any other click between the two presses cancels the upgrade ask")
''' + HARNESS_OLD2_BANK)
T.rep('''    GO, p_ = g_open("TAB6 reopen as the admin for a gone mod", P_=PO6)
''', HARNESS_OLD2_ADMIN + '''    GO, p_ = g_open("TAB6 reopen as the admin for a gone mod", P_=PO6)
''')
if T.dst:
    T.finish()
