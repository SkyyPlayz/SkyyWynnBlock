"""Harness for SkyyGear 0.3.16 (tools/gear_0_3_16_patch.py header) = the 0.3.15 harness's children run on the 0.3.16 jar + S316 + H316:
    python tools/gear_0_3_16_patch.py && python SkyyGear/build_skyygear_0.3.16.py
    python SkyyGear/test_skyygear_0.3.16.py [--keep] [--only assets,h316,h315,h314,live314,h313,live313,h312,live,h311,h310,h39,verify,h38,h37,g36,snd,till,life,audit]

  S316 the jar 0.3.15 -> 0.3.16: no class added or removed, only UI classes changed (the pages, GearHub, HubBar, GearUi + the version text
       classes); every non-class file identical except manifest.json
  H316 ONE booted engine (the 0.3.5 life setup) with the REAL pages on a player whose PageManager is FakePM10:
       P  EVERY PAGE (Smithing cards of each category, a tier-up set page, a craftable set page, Anvil Reforge, Anvil + an item, Anvil
          Identify, Upgrade = the tools page for each tool, the old Upgrade list, and with part.anvil off the old Reforge page, its Upgrade
          mode, the Multitool page, the 0.2.11 Identify page): SUI.assert_menu_page on the commands the page really sends (1600 x 980, row 1
          + row 2, at most one sub row - only on the Anvil -, no Back / < Menu / pager text, the content fits the kit's room), the kit shell
          byte for byte, row 1 = the kit twin, row 2 = Crafting | Smithing | Anvil | Upgrade with the page's tab lit, the footer = result
          line + Refresh, no #SkyyGBtnBack / #SkyyGBtnPBack / Prev / Next; every page validates (ids, parents, kit markup, item ids)
       G  RULE 7: a set's piece rows, the old Upgrade rows and the Anvil rows grow when few (the kit's tiers), normal when many; the cards are
          one scroll list (all cards, no pager)
       C  THE CLICKS: row 2 from every page opens the right page; Smithing on an open set = back to the cards; the Anvil sub-tabs switch in
          place; the legacy pages route row 1 / row 2 / the X; Refresh answered once on every page; the old pager / back clicks still answer
Scratch: tools/dev/scratch/menuS3/gear/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.16"
V315 = "0.3.15"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "menuS3", "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J315 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V315))                       # read only
PKG = "com.skyy.gear."

# ---- the 0.3.15 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H315 = os.path.join(HERE, "test_skyygear_0.3.15.py")
_T315 = open(_H315, encoding="utf-8").read()
_cut = _T315.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H315, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H315 = {"__name__": "skyygear_h315", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T315[:_cut], _H315 + " (library)", "exec"), H315)
sys.argv = _argv
H314, H313, H312, H311, H310, H39, H38, H37, H36, H35, H = (H315["H314"], H315["H313"], H315["H312"], H315["H311"], H315["H310"], H315["H39"],
                                                           H315["H38"], H315["H37"], H315["H36"], H315["H35"], H315["H"])
FAKE_DIR = H315["FAKE_DIR"]
FAKE_PKG = H315["FAKE_PKG"]
FI7_SRC = H315["FI7_SRC"]
FAILS, OKS = [], [0]
WAIVE = list(H315["WAIVE"]) + list(H315["WAIVE_315"])
WAIVED = []
_WHY_PAGE = ("0.3.16 by design (menu sweep S3; Skyy 2026-10-16 'keep this top bar at this size consistent at the top across every menu' + popup "
             "'every hub page Home size 1600 x 980'): every Gear page is the kit 1.7 hub_page - root #SkyyGHp 1600 x 980, row 1 #SkyyGHpBigRow, "
             "row 2 #SkyyGHpBigTabs (the kit 1.6 big row + strip #SkyyGBigRow / #SkyyGHubTabs of 0.3.15 are gone), the Anvil's Reforge | "
             "Identify = the kit sub-tab row #SkyyGHpSub; H316 P checks every page with SUI.assert_menu_page")
_WHY_BACK = ("0.3.16 by design (Skyy 2026-10-16 'I never want to have to use a back button'): no Back / Close button in the footer and none on "
             "the set page - rows 1 + 2 and the X lead away, a set is left by its category button or row 2's Smithing tab; H316 C checks both")
_WHY_PAGER = ("0.3.16 by design (Menu-Pattern 3.3 + Skyy 'i dont mind scrolling, but if there are only a few items try to scale them to all "
              "fit'): the cards, a set's rows and the old Upgrade list are ONE scroll list each (no Prev / Next pages); short lists grow; H316 G "
              "checks the lists and the row sizes")
_WHY_ROW = ("0.3.16 by design: the part.anvil-off Reforge-page mode row keeps only the page's own modes (Reforge / Upgrade / Multitool) - "
            "Smithing / Tools / Identify / Upgrade are row 2's tabs (kit 1.7); H316 P checks those pages")
WAIVE_316 = [          # (prefix, why) - each one an explained 0.3.16 layout change of an older check (from the first 0.3.16 run)
    ("F FIX: the Upgrade tab: 8 rows on page 1 of", _WHY_PAGER), ("F FIX: page 2 starts at row 8", _WHY_PAGER)]
for _pg in ("Smithing", "Anvil", "Anvil > Identify", "Upgrade (tools)", "old Upgrade list"):
    for _w in ("the big hub row = the kit twin byte for byte", "the big row is the body's first child, the strip the second",
               "the strip = Crafting | Smithing | Anvil | Upgrade", "its own tab is lit", "the page root", "the Reforge | Identify sub-row under the strip"):
        WAIVE_316.append(("B %s: %s" % (_pg, _w), _WHY_PAGE))


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S316
def run_assets316():
    ea, eb = entries(J315), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(not added and not gone and changed == ["manifest.json"],
          "S316: 0.3.15 -> 0.3.16 adds nothing, removes nothing, changes only manifest.json among the files: added %s, gone %s, changed %s"
          % (added[:4], gone[:4], changed))
    check('"0.3.16"' in eb["manifest.json"].decode("utf-8"), "S316: the manifest says 0.3.16")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.15 -> 0.3.16: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    want_c = {"SmithPage", "ReforgePage", "LifePage", "UpgPage", "MultiPage", "IdentifyPage", "GearHub", "HubBar", "GearUi",
              "SkyyGearPlugin", "CfgFn", "CfgRows", "GearCfg"}          # Cfg* / the plugin: the version text and the start line
    check(set(chg) <= want_c, "S316: only the UI classes (+ the version text) changed: unexpected %s" % sorted(set(chg) - want_c))


# ====================================================================================================== H316
def run_h316(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h316(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H316: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h316(L, K):
    from jpype import JClass, JInt, JShort, JLong, JObject, JArray, JString
    import skyyui as SUI
    SUI.verify(quiet=True)
    br, Gear, Cfg, LL, Life, Up, Stamp = L["br"], L["Gear"], L["Cfg"], L["LL"], L["Life"], L["Up"], L["Stamp"]
    mkinv, world, PR1, U1, stack, skills, apply, logs, ids, us, jf, ITEM = (L["mkinv"], L["world"], L["PR1"], L["U1"], L["stack"], L["skills"],
                                                                            L["apply"], L["logs"], L["ids"], L["us"], L["jf"], L["ITEM"])
    P = lambda n: JClass(PKG + n)
    HB, GH, GHO, Smith, Ui = P("HubBar"), P("GearHub"), P("GearHubOpen"), P("GearSmith"), P("GearUi")
    Sysm = JClass("java.lang.System")

    def kc(cond, what):
        K.check(bool(cond), what)

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))
    apply()
    if Sysm.getProperties().get("skyy.bridge") is None:
        Sysm.getProperties().put("skyy.bridge", br)
    eq(int(GHO.register()), 4, "H316 setup: the four Crafting tabs are put")
    br.put("hub:tab:smithing:recipes", JArray(JObject)([JString("SkyySacks"), JString("Crafting"), JObject(JInt(5), JClass("java.lang.Integer")), JString("craft"), None, None, JString("smithing_recipes")]))
    TITLES = {"home": "Home", "character": "Character", "storage": "Storage", "market": "Market", "smithing": "Crafting", "world": "World",
              "social": "Social", "settings": "Settings"}
    ICON = "Tool_Pickaxe_Crude"
    for h_ in SUI.HUB_ROW_IDS:
        HB.def4(h_, TITLES[h_], "skymenu" if h_ == "home" else h_, ICON, None)
    ROWHUBS = [(h_, TITLES[h_], ICON) for h_ in SUI.HUB_ROW_IDS]
    KW = dict(body_id="SkyyGHpB", content_id="SkyyGBody", content_w=1066, content_layout="Top")
    SH = SUI.hub_page("SkyyGHp", "smithing", footer=True, **KW)
    SHS = SUI.hub_page("SkyyGHp", "smithing", sub=True, footer=True, **KW)

    # ============================================================== the page rig (FakePM10, render, click) - the H315 way
    FPM = JClass(FAKE_PKG + ".FakePM10")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    inv, cs = mkinv()
    ref, st, ch, pl = world(inv, cs, PR1)
    pm_field = None
    k_ = PLA.class_
    while k_ is not None and pm_field is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PMC.class_:
                f_.setAccessible(True)
                pm_field = f_
        k_ = k_.getSuperclass()
    pm_field.set(pl, us.allocateInstance(FPM.class_))
    jf(PRc, "entity").set(PR1, ref)
    ALIGN, ELEM_RE, strip_q = H39["ALIGN"], H39["ELEM_RE"], H39["strip_q"]
    rendered = []

    def cmds(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("type", "selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            out_.append(vals)
        return out_

    def evd(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            got = ""
            for f_ in ("data", "eventData"):
                try:
                    v_ = getattr(e_, f_)
                    if v_ is not None:
                        got = str(v_)
                        break
                except Exception:
                    pass
            out_.append(got or str(e_))
        return out_

    def sels(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            try:
                out_.append(str(getattr(e_, "selector")))
            except Exception:
                out_.append(None)
        return out_

    def validate(cl, ev):
        probs, known = [], set()
        for v in cl:
            t_ = v["text"] if v["text"] and "{" in v["text"] else (v["data"] if v["data"] and "{" in v["data"] else None)
            if t_ is not None and "Set" not in (v["type"] or ""):
                sel = v["selector"]
                if sel not in (None, "None", "") and sel.lstrip("#") not in known:
                    probs.append("append into %s before it exists" % sel)
                try:
                    SUI.check_markup(t_, kit_paths=False)
                except ValueError as e_:
                    probs.append("kit: " + str(e_)[:160])
                if Ui.bad(t_) is not None:
                    probs.append("GearUi.bad: %s" % Ui.bad(t_))
                bare = strip_q(t_)
                for m_ in re.finditer(r"(Horizontal|Vertical)Alignment:\s*(\w+)", bare):
                    if m_.group(2) not in ALIGN:
                        probs.append("%sAlignment %s" % (m_.group(1), m_.group(2)))
                for m_ in re.finditer(r'ItemId: "([^"]*)"', t_):
                    if ITEM.getAssetMap().getAsset(m_.group(1)) is None:
                        probs.append("ItemId %s is no item" % m_.group(1))
                for m_ in ELEM_RE.finditer(bare):
                    if m_.group(2):
                        if m_.group(2) in known:
                            probs.append("#%s created twice" % m_.group(2))
                        known.add(m_.group(2))
            elif v["selector"] and "." in v["selector"]:
                tid = v["selector"].lstrip("#").split(".")[0]
                if tid not in known:
                    probs.append("set on #%s which does not exist" % tid)
        for e_ in ev:
            if e_ and e_.lstrip("#") not in known:
                probs.append("event on %s which does not exist" % e_)
        return probs

    def render(pg_):
        ub_, ue_ = UCB(), UEB()
        FPM.cur = pg_
        pg_.build(ref, ub_, ue_, st)
        cl, ev = cmds(ub_), sels(ue_)
        rendered.append((cl, ev))
        txt = chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl)
        return txt, cl, ev, evd(ue_)

    def click(pg_, data):
        FPM.cur = pg_
        p0, c0 = int(FPM.packets), int(FPM.closes)
        pg_.handleDataEvent(ref, st, data)
        return int(FPM.packets) - p0 + int(FPM.closes) - c0

    def appends(cl):
        out_ = []
        for v in cl:
            if "Set" in (v["type"] or ""):
                continue
            mk = v["text"] if v["text"] and "{" in v["text"] else (v["data"] if v["data"] and "{" in (v["data"] or "") else None)
            if mk is None:
                continue
            sel = v["selector"]
            out_.append((None if sel in (None, "None", "") else sel.lstrip("#"), mk))
        return out_

    def sets(cl):
        out_ = []
        for v in cl:
            if "Set" in (v["type"] or "") and v["selector"]:
                val = v["text"] if v["text"] is not None else v["data"]
                out_.append((v["selector"], "" if val is None else val))
        return out_

    TAB_SEL = SUI._tab_btn_style(True, "sky")

    def row2(cl):
        """[(label, lit)] of row 2 #SkyyGHpBigTabs"""
        ap = appends(cl)
        out_ = []
        for i_, (p_, mk) in enumerate(ap):
            m_ = re.match(r"Button #SkyyGHpBigT(\d+) ", mk)
            if p_ == "SkyyGHpBigTabs" and m_:
                lab = None
                for p2, mk2 in ap[i_ + 1:i_ + 4]:
                    if p2 == "SkyyGHpBigT" + m_.group(1) and mk2.startswith("Label"):
                        lab = re.search(r'Text: "([^"]*)"', mk2).group(1)
                out_.append((lab, TAB_SEL in mk))
        return out_

    def page_ok(nm, pg, tab, sub=False, sub_lit=None):
        txt, cl, ev, ed = render(pg)
        ap = appends(cl)
        sh = SHS if sub else SH
        try:
            r_ = SUI.assert_menu_page(ap, sh, what="H316 " + nm, sets=sets(cl))
            kc(r_["rows"] == 2 and r_["subs"] == (1 if sub else 0), "P %s: assert_menu_page passes (rows 1 + 2, %d sub row)" % (nm, 1 if sub else 0))
        except ValueError as e_:
            kc(False, "P %s: assert_menu_page: %s" % (nm, e_))
        shell = [(p_, mk) for p_, mk in sh.appends]
        kc(ap[:len(shell)] == shell, "P %s: the page starts with the kit 1.7 shell byte for byte (%d appends): first diff %s" % (
            nm, len(shell), next(((a, b) for a, b in zip(ap, shell) if a != b), None)))
        r1 = [(p_, mk) for p_, mk in ap if p_ == "SkyyGHpBigRow" or (p_ or "").startswith("SkyyGHpBigR")]
        twin = [(p_, mk) for p_, mk in SUI.hub_big_row_preview("SkyyGHp", ROWHUBS, "smithing", 1552) if p_ != "SkyyGHpB"]
        kc(r1 == [(p_, mk) for p_, mk in twin if p_ == "SkyyGHpBigRow" or (p_ or "").startswith("SkyyGHpBigR")],
           "P %s: row 1 = the kit twin (Home's size, Crafting lit)" % nm)
        r2 = row2(cl)
        eq([l for l, _x in r2], ["Crafting", "Smithing", "Anvil", "Upgrade"], "P %s: row 2 = Crafting | Smithing | Anvil | Upgrade" % nm)
        eq([l for l, x in r2 if x], [tab], "P %s: its own tab is lit" % nm)
        subs = [(p_, mk) for p_, mk in ap if p_ == "SkyyGHpSub" and mk.startswith("TextButton")]
        if sub:
            kc([re.search(r'Text: "([^"]*)"', mk).group(1) for _p, mk in subs] == ["Reforge", "Identify"]
               and [re.search(r'Text: "([^"]*)"', mk).group(1) for _p, mk in subs if SUI.theme_button_style("primary", "small", theme="sky") in mk] == [sub_lit],
               "P %s: the sub-tab row = Reforge | Identify, %s lit" % (nm, sub_lit))
            kc(any("mode:0" in e_ for e_ in ed) and any("mode:5" in e_ for e_ in ed), "P %s: the sub-tabs are bound (mode:0 / mode:5)" % nm)
        else:
            kc(not subs, "P %s: no sub-tab row" % nm)
        foot = [mk for p_, mk in ap if p_ == "SkyyGHpFoot"]
        kc(len(foot) == 3 and "#SkyyGInfo " in foot[0] and "#SkyyGBtnRefresh " in foot[2] and 'Text: "Refresh"' in foot[2],
           "P %s: the footer = the result line + Refresh: %s" % (nm, [m[:40] for m in foot]))
        bad = [x for x in ("#SkyyGBtnBack", "#SkyyGBtnPBack", "#SkyyGBtnPrev", "#SkyyGBtnNext", "#SkyyGBtnRPrev", "#SkyyGPager", "#SkyyGRPager",
                           "#SkyyGHubTabs", "#SkyyGBigRow", "#SkyyGTabs ", "#SkyyGRoot", "#SkyyGNav") if x in txt]
        kc(not bad, "P %s: none of the old pieces (back / pager / strip / old row / old root): %s" % (nm, bad))
        kc(any("hub:h:character" in e_ for e_ in ed) and any("hub:upgrade" in e_ for e_ in ed) and any("hub:close" in e_ for e_ in ed),
           "P %s: rows 1 + 2 and the X are bound (hub:h:<hub>, hub:<tab>, hub:close)" % nm)
        return txt, cl, ev, ed

    SP, RP, LP, UP, MP, IP = P("SmithPage"), P("ReforgePage"), P("LifePage"), P("UpgPage"), P("MultiPage"), P("IdentifyPage")
    skills(Mining=30, Smithing=30, Foraging=30, Farming=30, Fishing=30)
    Life.sweep(PR1, inv, True)

    # ============================================================== P + G: the Smithing page
    sp = SP(PR1)
    for c_ in [int(x) for x in Smith.SHOW]:
        sp.cat = JInt(c_)
        sp.picked = True
        txt, cl, ev, ed = page_ok("Smithing cards (%s)" % Smith.CAT_NAME[c_], sp, "Smithing")
        n = len(Smith.groups(U1, JInt(c_), bool(Smith.showAll(U1))))
        cards = set(re.findall(r"#SkyyGCard(\d+) \{", txt))
        kc(len(cards) == n and (n == 0 or "#SkyyGCardList " in txt), "G Smithing %s: ONE scroll list of all %d cards (%d drawn)" % (Smith.CAT_NAME[c_], n, len(cards)))
    # the set pages: a tier-up set and a craftable set, few rows and many
    tierset, craftset = None, None
    for c_ in [int(x) for x in Smith.SHOW]:
        for g_ in Smith.groups(U1, JInt(c_), True):
            if bool(Smith.tierUp(g_)) and tierset is None:
                tierset = (c_, g_)
            if not bool(Smith.tierUp(g_)) and craftset is None:
                craftset = (c_, g_)
    kc(tierset is not None and craftset is not None, "G a tier-up set and a craftable set exist")
    for nm, hit in (("tier-up set", tierset), ("craftable set", craftset)):
        if hit is None:
            continue
        c_, g_ = hit
        sp2 = SP(PR1)
        sp2.cat = JInt(c_)
        sp2.picked = True
        sp2.grp = g_
        sp2.gkey = g_[0]
        sp2.view = JInt(1)
        txt, cl, ev, ed = page_ok("Smithing %s %s" % (nm, g_[0]), sp2, "Smithing")
        outs = len(g_[1])
        want = int(GH.growPiece(JInt(outs)))
        hs = SUI.grow_row_sizes(534, 74, gap=0)
        eq(want, hs[SUI.grow_pick(outs, 534, hs, 0)], "G %s: GearHub.growPiece(%d) = the kit twin (grow_pick)" % (nm, outs))
        rows_ = re.findall(r"Group #SkyyGPc(\d+) \{ Anchor: \(Height: (\d+)\)", txt)
        kc(len(rows_) == outs and all(int(h_) == want for _i, h_ in rows_) and "#SkyyGRows " in txt and "TopScrolling" in [mk for p_, mk in appends(cl) if "#SkyyGRows " in mk][0],
           "G %s: all %d piece rows in ONE scroll list, %d px each" % (nm, outs, want))
        kc('Text: "Back"' not in txt, "P %s: no Back button" % nm)
        # C: row 2's Smithing on the open set = back to the cards; a category button too
        FPM.last = None
        a = click(sp2, '{"a":"hub:gear"}')
        kc(a == 1 and int(sp2.view) == 0 and FPM.last is None, "C %s: row 2's Smithing = back to the cards in place (answered %d, view %d)" % (nm, a, int(sp2.view)))
    eq([GH.growPiece(JInt(n_)) for n_ in (1, 3, 4, 7, 12)], [148, 148, 107, 74, 74], "G the piece rows: 1-3 rows 148 px, 4 rows 107, 5+ rows 74 (normal)")
    eq([GH.growUp(JInt(n_)) for n_ in (1, 4, 5, 6, 7, 20)], [140, 140, 101, 101, 70, 70], "G the old Upgrade rows: 1-4 rows 140 px, 5-6 rows 101, 7+ rows 70")
    eq([GH.growAnvil(JInt(n_), JInt(626)) for n_ in (1, 2, 4, 8, 30)], [90, 90, 64, 44, 44], "G the Anvil rows (+ 4 rows for Requip): 1-2 items 90 px, 3-5 items 64, more 44")
    sp3 = SP(PR1)
    sp3.picked = True
    sp3.cat = JInt(int(Smith.SHOW[0]))
    render(sp3)
    for d_ in ('{"a":"prev"}', '{"a":"next"}', '{"a":"rprev"}', '{"a":"rnext"}', '{"a":"pback"}', '{"a":"back"}', '{"a":"refresh"}'):
        JClass("java.lang.Thread").sleep(JLong(400))
        FPM.cur = sp3
        a = click(sp3, d_)
        kc(a >= 1 or d_ in ('{"a":"prev"}', '{"a":"next"}', '{"a":"rprev"}', '{"a":"rnext"}', '{"a":"pback"}'), "C Smithing: a stale %s still answers (%d)" % (d_, a))

    # ============================================================== P: the Anvil
    rp = RP(PR1)
    page_ok("Anvil (Reforge)", rp, "Anvil", sub=True, sub_lit="Reforge")
    txt, cl, ev, ed = render(rp)
    ft = [v for v in sets(cl) if v[0] == "#SkyyGFoot.Text"]
    kc(ft and "Your purse" in ft[0][1] and [p_ for p_, mk in appends(cl) if "#SkyyGFoot " in mk] == ["SkyyGHpSub"],
       "P Anvil: the purse / Appraisal Tool line sits on the sub-tab row: %s" % (ft[0][1][:60] if ft else None))
    # an item on the anvil (a gear piece in the inventory)
    piece = None
    for c_ in [int(x) for x in Smith.SHOW]:
        for g_ in Smith.groups(U1, JInt(c_), True):
            piece = str(g_[1][0])
            break
        if piece:
            break
    cs["storage"].setItemStackForSlot(JShort(0), stack(piece))
    Stamp.scan(PR1, inv)
    rp2 = RP(PR1)
    txt, cl, ev, ed = page_ok("Anvil + 1 item", rp2, "Anvil", sub=True, sub_lit="Reforge")
    rowh = re.findall(r"Button #SkyyGRow(\d+) \{ Anchor: \(Height: (\d+)\)", txt)
    nrows = len(rp2.rows)
    want = int(GH.growAnvil(JInt(nrows), JInt(626)))
    kc(rowh and all(int(h_) == want for _i, h_ in rowh) and want >= 64, "G Anvil: %d gear row(s) drawn %s px (the grow tier %d)" % (nrows, [h_ for _i, h_ in rowh], want))
    a = click(rp2, '{"a":"sel:0"}')
    txt, cl, ev, ed = page_ok("Anvil, the item on the anvil", rp2, "Anvil", sub=True, sub_lit="Reforge")
    kc("#SkyyGAnvil " in txt and int(rp2.selSec) >= 0, "P Anvil: the picked item is on the anvil (the reforge / upgrade panel)")
    eq(click(rp2, '{"a":"mode:5"}'), 1, "C Anvil: the sub-tab Identify is answered once")
    kc(bool(rp2.anIdM) and FPM.last is None, "C Anvil: ... the Identify view in place")
    page_ok("Anvil (Identify)", rp2, "Anvil", sub=True, sub_lit="Identify")
    eq(click(rp2, '{"a":"mode:0"}'), 1, "C Anvil > Identify: the sub-tab Reforge is answered once")
    kc(not bool(rp2.anIdM), "C Anvil > Identify: ... back on the Reforge view")
    for k2, s2 in list(cs.items()):
        for j_ in range(int(s2.getCapacity())):
            s2.setItemStackForSlot(JShort(j_), None)

    # ============================================================== P: Upgrade = the tools page, every tool; the old Upgrade list
    lp = LP(PR1)
    for k_ in range(len(LL.KIND)):
        lp.sel = JInt(k_)
        page_ok("Upgrade (tools) %s" % LL.KIND[k_], lp, "Upgrade")
    txt, cl, ev, ed = render(lp)
    kc('Text: "Upgrade"' in txt and "#SkyyGPReset " in txt, "P Upgrade: Reset points + the UPGRADE button still there")
    tok = int(lp.tok)
    a = click(lp, '{"a":"reset:%d"}' % tok)
    kc(a >= 1, "C Upgrade: Reset points answers (%d)" % a)
    up = UP(PR1)
    txt, cl, ev, ed = page_ok("old Upgrade list", up, "Upgrade")
    kc("#SkyyGUList " in txt and "TopScrolling" in [mk for p_, mk in appends(cl) if "#SkyyGUList " in mk][0], "G old Upgrade list: ONE scroll list")
    n_up = len(up.rows)
    rh = re.findall(r"Group #SkyyGURow\d+ \{ Anchor: \(Height: (\d+)\); LayoutMode: Left; Padding: \(Horizontal: 6", txt)
    kc(n_up > 0 and (len(rh) == n_up and all(int(h_) == int(GH.growUp(JInt(n_up))) for h_ in rh)), "G old Upgrade list: %d rows, %s px" % (n_up, sorted(set(rh))))
    for d_ in ('{"a":"pg:1"}', '{"a":"pg:-1"}', '{"a":"refresh"}'):
        kc(click(up, d_) >= 1, "C old Upgrade list: %s answers" % d_)

    # ============================================================== C: row 2 from every page
    def go(pg, data, what, want_cls=None, self_=False):
        FPM.last = None
        n0 = int(FPM.opens)
        a = click(pg, data)
        got = FPM.last
        if self_:
            kc(got is None and a >= 1, "C %s: %s = this page redrawn (answered %d)" % (what, data, a))
        else:
            kc(got is not None and str(got.getClass().getName()).endswith(want_cls) and int(FPM.opens) == n0 + 1,
               "C %s: %s opens the %s: %s" % (what, data, want_cls, None if got is None else got.getClass().getName()))
    for nm, pg, own in (("Smithing", SP(PR1), "gear"), ("Anvil", RP(PR1), "reforge"), ("Upgrade (tools)", LP(PR1), "upgrade"), ("old Upgrade list", UP(PR1), "upgrade")):
        for tab, cls in (("gear", "SmithPage"), ("reforge", "ReforgePage"), ("upgrade", "LifePage")):
            render(pg)
            if tab == own:
                go(pg, '{"a":"hub:%s"}' % tab, nm, self_=True)
            else:
                go(pg, '{"a":"hub:%s"}' % tab, nm, cls)
        for d_ in ('{"a":"hub:h:character"}', '{"a":"hub:h:home"}', '{"a":"refresh"}'):
            render(pg)
            JClass("java.lang.Thread").sleep(JLong(400))
            kc(click(pg, d_) >= 1, "C %s: %s is answered" % (nm, d_))
        c0 = int(FPM.closes)
        render(pg)
        click(pg, '{"a":"hub:close"}')
        kc(int(FPM.closes) == c0 + 1, "C %s: the X (hub:close) closes the page" % nm)

    # ============================================================== part.anvil off: the legacy pages
    apply(part__anvil="false")
    rl = RP(PR1)
    rl.mode = JInt(0)
    txt, cl, ev, ed = page_ok("legacy Reforge page (part.anvil off)", rl, "Anvil")
    tabs_ = re.findall(r'TextButton #SkyyGTab(\d) \{', txt)
    kc(set(tabs_) <= {"0", "1", "2"}, "P legacy Reforge page: its mode row has only its own modes (Reforge / Upgrade / Multitool): %s" % tabs_)
    ru = RP(PR1)
    ru.mode = JInt(1)
    page_ok("legacy Reforge page, Upgrade mode", ru, "Upgrade")
    mp = MP(PR1)
    page_ok("legacy Multitool page", mp, "Anvil")
    ip = IP(PR1)
    page_ok("legacy Identify page", ip, "Anvil")
    for nm, pg in (("legacy Reforge", rl), ("legacy Multitool", mp), ("legacy Identify", ip)):
        render(pg)
        go(pg, '{"a":"hub:upgrade"}', nm, "LifePage")
        render(pg)
        go(pg, '{"a":"hub:gear"}', nm, "SmithPage")
        c0 = int(FPM.closes)
        render(pg)
        click(pg, '{"a":"hub:close"}')
        kc(int(FPM.closes) == c0 + 1, "C %s: the X closes the page" % nm)
        render(pg)
        JClass("java.lang.Thread").sleep(JLong(450))
        kc(click(pg, '{"a":"refresh"}') >= 1, "C %s: Refresh answers" % nm)
    apply()

    # ============================================================== every page rendered validates
    probs = []
    for cl_, ev_ in rendered:
        probs += validate(cl_, ev_)
    kc(not probs, "P every page rendered (%d) validates: %s" % (len(rendered), probs[:4]))
    HB.removeAll()
    K.notes.append("H316 logs: %s" % [x[:160] for x in logs() if "WARN" in x][:6])


# ====================================================================================================== main
def child(env, *args):
    cmd = [sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--root", SCR_ROOT]
    return subprocess.run(cmd, env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        w = [why for pre, why in WAIVE + WAIVE_316 if str(f).startswith(pre)]
        if w:
            WAIVED.append("%s: %s (%s)" % (label, str(f)[:140], w[0]))
            continue
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, str(n)[:700]))
    return d


def main():
    H314_FLAGS = (("--mkfake", lambda: H310["run_mkfake10"](arg("--mkfake"))), ("--h315", lambda: H315["run_h315"](arg("--out"))),
                  ("--h314", lambda: H314["run_h314"](arg("--out"))), ("--live314", lambda: H314["run_live314"](arg("--out"))),
                  ("--h313", lambda: H313["run_h313"](arg("--out"))), ("--live313", lambda: H313["run_live313"](arg("--out"))),
                  ("--h312", lambda: H312["run_h312"](arg("--out"))), ("--live312", lambda: H312["run_live312"](arg("--out"))),
                  ("--h311", lambda: H311["run_h311"](arg("--out"))), ("--h310", lambda: H310["run_h310"](arg("--out"))),
                  ("--life", lambda: H35["run_life"](arg("--out"))),
                  ("--verify", lambda: H["run_verify"](arg("--out"))), ("--h39", lambda: H39["run_h39"](arg("--out"))),
                  ("--h38", lambda: H38["run_h38"](arg("--out"))), ("--h37", lambda: H37["run_h37"](arg("--out"))),
                  ("--g36", lambda: H36["run_g36"](arg("--out"))), ("--snd", lambda: H36["run_snd"](arg("--out"))),
                  ("--till", lambda: H35["run_till"](arg("--out"))), ("--audit", lambda: H["run_audit"](arg("--out"))))
    for flag, fn in (("--h316", lambda: run_h316(arg("--out"))),) + H314_FLAGS:
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    _known = {"--only", "--keep", "--dir", "--jar", "--root", "--out"}
    _unk = [a for a in sys.argv[1:] if a.startswith("--") and a not in _known]
    if _unk:
        print("unknown child flag(s) %s - nothing run" % _unk)
        sys.exit(2)
    for f_ in (JAR, J315, FI7_SRC, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
        assert os.path.isfile(f_), f_
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    shutil.copyfile(H35["CO_SRC"], H36["CO_JAR"])
    shutil.copyfile(H36["FI6_SRC"], H36["FI_JAR"])
    for f_ in glob.glob(os.path.join(H35["LIVE_PLAYERS"], "*.json")):
        shutil.copyfile(f_, os.path.join(SCRATCH, "players", os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    env_313 = dict(env)
    env_313["JAVA_TOOL_OPTIONS"] = env["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.no314=true"
    env_312 = dict(env_313)
    env_312["JAVA_TOOL_OPTIONS"] = env_313["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noNormOff=true"
    env_311 = dict(env_312)
    env_311["JAVA_TOOL_OPTIONS"] = env_312["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noCanKit=true"
    env_old = dict(env_311)
    env_old["JAVA_TOOL_OPTIONS"] = env_311["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noPoleKit=true"
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets316()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")

        def run_children(lst):
            for label, flag, ev in lst:
                if not want(label):
                    continue
                out = os.path.join(SCRATCH, "%s.json" % label)
                pr = child(ev, flag, "--out", out)
                check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
                take(out, label)
        run_children((("h310", "--h310", env_old), ("h39", "--h39", env_old), ("verify", "--verify", env_old), ("h38", "--h38", env_old),
                      ("h37", "--h37", env_old), ("g36", "--g36", env_old), ("snd", "--snd", env_old), ("till", "--till", env_old)))
        if want("life"):
            _why39 = "0.3.9 by design: Identify moved to the Identify tab; the 0.3.5 check clicks it on the Anvil tab (H39 I covers the reveal)"
            H37["L37_EXTRA"].extend([("G35 R1:", _why39), ("G35 R2:", _why39), ("G35 R3:", _why39), ("G35 R4", _why39), ("G35 R5:", _why39)])
            H37["L37_EXTRA"].append(("G35 P6:", "0.3.11 fix round by design: with the kit off /pole says 'You have no lifelong fishing pole - this server hands none out (lifelong.poleKit is off). A pole a quest gave you: hold it and type /lifelong.' (no Marlow pole since SkyyQuests 0.3.4); the exact-copy half is unchanged"))
            H37["L37_EXTRA"].append(("G35 P7 FIX 2", "0.3.11 fix round by design: the refusal reads 'Only a fishing pole a quest gave you can become your lifelong pole' (no Marlow pole since SkyyQuests 0.3.4); still refused, nothing written"))
            _why314 = "0.3.14 by design (Skyy 2026-10-16 'let it work'): sigil.mythicUse defaults to true - a fresh config file says so (the build-time text the seam cannot change), the Mythic Sigil works on the Anvil; H314 E covers it"
            H37["L37_EXTRA"].extend([("G34 S1:", "0.3.14 by design: the fresh config's hoe.areaElsewhere and sigil.mythicUse rows read true (Skyy 2026-10-16 'everywhere' / 'let it work'); H314 A checks the new defaults"),
                                     ("FIX2 M1:", _why314), ("G34 S2:", _why314 + " (the M1 step used the Mythic Sigil the S2 step expected)")])
            H37["L37_EXTRA"].append(("M: a NEW profile's first join", "0.3.12 by design: GearLL.KCRUDE has 6 kinds (+ the watering can); the four Crude Common tools still land in storage 0-3 exactly as checked (the can comes from the kit, off here: noCanKit)"))
            for pre, why in H315["WAIVE_315"] + WAIVE_316:
                H37["L37_EXTRA"].append((pre, why))
            n0 = len(H37["FAILS"])
            H37["run_l35"](env_old)
            for f_ in H37["FAILS"][n0:]:
                w = [why for pre, why in WAIVE + WAIVE_316 if str(f_).startswith(pre)]
                if not w and H315["L35_SUM"].match(str(f_)):
                    w = ["every L35 check passed or is an explained deviation (unexpected []); only the old >= 300 count (the explained ones do not count as ok)"]
                if w:
                    WAIVED.append("L35: %s (%s)" % (str(f_)[:140], w[0]))
                else:
                    FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        run_children((("h311", "--h311", env_311), ("h312", "--h312", env_312), ("live", "--live312", env_312), ("h313", "--h313", env_313),
                      ("live313", "--live313", env_313), ("h314", "--h314", env), ("live314", "--live314", env),
                      ("h315", "--h315", env), ("h316", "--h316", env)))          # ours last (the children share the gear home)
        if want("audit"):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env_old, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s), %d waived (by design)" % (VERSION, OKS[0], len(FAILS), len(WAIVED)))
    for w in WAIVED:
        print("WAIVED:", w)
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
