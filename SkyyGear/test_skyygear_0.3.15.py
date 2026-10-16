"""Harness for SkyyGear 0.3.15 (tools/gear_0_3_15_patch.py header) = the 0.3.14 harness's children run on the 0.3.15 jar + S315 + H315:
    python tools/gear_0_3_15_patch.py && python SkyyGear/build_skyygear_0.3.15.py
    python SkyyGear/test_skyygear_0.3.15.py [--keep] [--only assets,h315,h314,live314,h313,live313,h312,live,h311,h310,h39,verify,h38,h37,g36,snd,till,life,audit]

  S315 the jar 0.3.14 -> 0.3.15: new = HubBar, HubHide, GearHub, GearHubOpen, GearHubVis + the 59 kit files + the 8 Crafting-hub tab icons
       (byte-identical to art/hub-tab-icons); nothing gone; only manifest.json changed among the old non-class files
  H315 ONE booted engine (the 0.3.5 life setup) with the REAL pages on a player whose PageManager is FakePM10:
       R  THE REGISTRY: GearHubOpen.register() puts hub:tab:smithing:gear / reforge / upgrade (labels Smithing / Anvil / Upgrade, orders 10 / 30 /
          40, icons) + identify as a MERGED tab of reforge (element 7, HubHide); the strip's tabs = Crafting | Smithing | Anvil | Upgrade (with a
          SkyySacks-like "recipes" tab); removeAll takes only ours
       B  THE BARS on every page (Smithing cards, a set page, Anvil, Anvil > Identify, Upgrade = the tools page, the old Upgrade list): the big
          hub row byte for byte = the kit twin (SUI.hub_big_row_preview) at the Home size (48 px, 32 px icons, 18 px labels), Crafting lit;
          the strip with the page's own tab lit; no old #SkyyGTab row; the page root 1100 x 940 (the Anvil 976); every rendered page validates
       C  THE CLICKS: from each page each strip tab opens the right page (FakePM10.last) - Smithing -> SmithPage, Anvil -> ReforgePage, Upgrade ->
          LifePage; the own tab = a redraw; Anvil <-> Identify in place (strip + sub-row); the merged Identify entry opens the Anvil's Identify
          view (HubBar.openSub); a row-1 hub click / Home / the X are answered; every click answered once
       U  THE TOOLS PAGE = UPGRADE: the button under Reset points reads Upgrade (the old Tier up); /upgrade opens the tools page (lifelong on)
          and the old Upgrade list with lifelong off; the Upgrade tab hides with lifelong + part.upgrade off
       S  THE SET PAGE: a tier-up piece row has an UPGRADE button (tup:<row>:<token>), no "To the Anvil" / "Open the Anvil"; a click without the
          previous piece = refused (nothing changes); from Requip = taken out (wardrobe:fn:fetch) then tiered up; with the piece + the cost +
          the skill = the next tier (GearUp.upgrade), one tier-up for two clicks of the same token
Scratch: tools/dev/scratch/smithhub/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, glob, random

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


VERSION = "0.3.15"
V314 = "0.3.14"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "smithhub")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J314 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V314))                       # read only
PKG = "com.skyy.gear."
NEW_CLASSES = ["HubBar", "HubHide", "GearHub", "GearHubOpen", "GearHubVis"]

# ---- the 0.3.14 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H314 = os.path.join(HERE, "test_skyygear_0.3.14.py")
_T314 = open(_H314, encoding="utf-8").read()
_cut = _T314.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H314, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H314 = {"__name__": "skyygear_h314", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T314[:_cut], _H314 + " (library)", "exec"), H314)
sys.argv = _argv
H313, H312, H311, H310, H39, H38, H37, H36, H35, H = (H314["H313"], H314["H312"], H314["H311"], H314["H310"], H314["H39"], H314["H38"], H314["H37"],
                                                      H314["H36"], H314["H35"], H314["H"])
if not os.path.isfile(H38["AR26"]):          # built jars are tidied; the SET's SkyyArmory (0.1.30) stands in for the 0.1.26 the 0.3.8 children loaded
    H38["AR26"] = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.30.jar")
FAKE_DIR = H314["FAKE_DIR"]
FAKE_PKG = H38["FAKE_PKG"]
FI7_SRC = H314["FI7_SRC"]
CO20 = H314["CO20"]
FAILS, OKS = [], [0]
WAIVE = list(H314["WAIVE"])
WAIVED = []
# 0.3.15 by design (Skyy 2026-10-16): the old inner tab row (#SkyyGTab<n>) is replaced by the Crafting hub bars; the pages are 60 px taller
_WHY_ROW = ("0.3.15 by design (Skyy 2026-10-16 'crafting shows smithing reforge, upgrade, and identify. but in smithing it doesnt' + 'Crafting / "
            "Smithing / Anvil (Reforge + Identify inside) / Upgrade (your tools)'): the old inner SMITHING / ANVIL / IDENTIFY / TOOLS / UPGRADE row "
            "(#SkyyGTab<n>) is gone from these pages - the Crafting hub bars replace it; H315 B / C check the new rows and every route")
_WHY_SET = ("0.3.15 by design (Skyy 2026-10-16 'just change to the anvil to upgrade'): a tier-up piece row reads 'Upgrade your <piece> - it keeps "
            "its rarity' with an UPGRADE button (the Anvil's tier-up right there) and the page has no 'Open the Anvil' (the hub's Anvil tab is the one "
            "way there); H315 S checks the row, the refusal, the Requip take-out and the tier-up")
_WHY_UPG = ("0.3.15 by design (Skyy 2026-10-16 'tools can be rolled into upgrade ... thats 1 less menu'): /upgrade opens the Upgrade tab = the "
            "lifelong tools page while lifelong tools are on (the old Upgrade list with them off); H315 U checks both")
_WHY_H = ("0.3.15 by design: the Smithing pages are 60 px taller (1100 x 940: + the big hub row 56 + the strip 52 - the old row 48), so the old "
          "808 px body budget reads 842 of the new 868; H315 B checks the new root size and that every page validates")
WAIVE_315 = [          # (prefix, why) - each one an explained 0.3.15 change of an older check
    ("T3: the Iron set's piece page: rows 'Tier up a Copper", _WHY_SET),
    ("I1: the tab row Craft | Anvil | Identify | Tools fits", _WHY_ROW),
    ("U the tab row: Craft | Anvil | Identify | Tools | Upgrade", _WHY_ROW),
    ("U the Tools tab shows the Upgrade tab too", _WHY_ROW),
    ("U /upgrade opens the Upgrade tab", _WHY_UPG),
    ("F FIX: the tab row's first tab reads 'Smithing'", _WHY_ROW),
    ("L11: the Tools page renders: unique ids without underscores, the Tools tab,", _WHY_ROW),
    ("L11: the height budget (body 842 <= 808", _WHY_H),
]
_WHY_LIVE = ("not 0.3.15: the live NewBetaTest world already runs 0.3.14 (deployed - its one-time migrate0314 ran and the profiles got their "
             "cans / Harvesters), so these one-time LIVE checks of earlier rounds find nothing left to do; the same checks fail the same way on the "
             "0.3.14 jar today (baseline run 2026-10-16)")
_WHY_BTN = ("0.3.15 by design (Skyy 2026-10-16 'just below reset points add an upgrade button'): the tools page's tier-up button right below "
            "Reset points reads UPGRADE (was Tier up; the same GearUp.upgrade - the tier-up itself passed in this very check) and the help / footer "
            "name the Upgrade button; H315 U checks the button")
WAIVE_315 += [("T2: Tier up = the Anvil's tier-up:", _WHY_BTN), ("T3: the panel shows the new tier; the help + footer name the Tier up button", _WHY_BTN),
              ("M1: no Multitool tab beside Tools (Craft | Anvil | Identify | Tools)", _WHY_ROW + " (no Multitool tab: H315 B checks the strip is exactly Crafting | Smithing | Anvil | Upgrade)")]
WAIVE_315 += [("LIVE no live profile has a can or a Harvester yet", _WHY_LIVE), ("LIVE314 start 1: only the two lines changed", _WHY_LIVE),
              ("LIVE314: two change-log rows with Undo", _WHY_LIVE), ("LIVE314: a History copy holds the live file's bytes", _WHY_LIVE)]
L35_SUM = re.compile(r"\AL35: every 0\.3\.5 life check passes on 0\.3\.7 \((\d+) ok\) except the explained deviations: unexpected \[\]\Z")


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S315
def run_assets315():
    import hashlib
    sys.path.insert(0, TOOLS)
    import skyyui as SUI
    ea, eb = entries(J314), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    kit = SUI.kit_texture_files()
    icons = {}
    man = json.load(open(os.path.join(ROOT, "art", "hub-tab-icons", "manifest.json"), encoding="utf8"))
    for t in ("gear", "reforge", "upgrade", "identify"):
        pp = SUI.hub_tab_icon_paths("smithing", t)
        icons[pp[2]] = "smithing_%s.png" % t
        icons[pp[3]] = "smithing_%s_on.png" % t
    want_add = set("com/skyy/gear/%s.class" % c for c in NEW_CLASSES) | set(kit) | set(icons)
    check(set(added) == want_add and not gone and changed == ["manifest.json"],
          "S315: 0.3.14 -> 0.3.15 adds exactly the 5 classes + 59 kit files + 8 tab icons, removes nothing, changes only manifest.json: extra %s, missing %s, gone %s, changed %s"
          % (sorted(set(added) - want_add)[:4], sorted(want_add - set(added))[:4], gone[:3], changed))
    bad = [p for p, b in kit.items() if eb.get(p) != (b if isinstance(b, bytes) else b.encode("utf-8"))]
    check(not bad, "S315: the kit files are the kit's bytes: %s" % bad[:3])
    bad = []
    for jp, fn in icons.items():
        data = open(os.path.join(ROOT, "art", "hub-tab-icons", fn), "rb").read()
        me = [f for f in man["files"] if f["path"] == fn]
        if eb.get(jp) != data or not me or hashlib.sha256(data).hexdigest() != me[0]["sha256"]:
            bad.append(fn)
    check(not bad, "S315: the 8 tab icons = art/hub-tab-icons (manifest sha256): %s" % bad)
    mj = eb["manifest.json"].decode("utf-8")
    check('"0.3.15"' in mj, "S315: the manifest says 0.3.15")
    menu = os.path.join(ROOT, "SkyyMenu", "SkyyMenu-0.3.34.jar")
    if os.path.isfile(menu):
        em = entries(menu)
        same = [p for p in icons if p in em and em[p] == eb[p]]
        check(len(same) == 8, "S315: the 8 tab icons are byte-identical to SkyyMenu 0.3.34's copies (whichever jar loads last): %d" % len(same))
    ca = set(n for n in ea if n.endswith(".class"))
    cb = set(n for n in eb if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca & cb if ea[n] != eb[n])
    print("  class compare 0.3.14 -> 0.3.15: %d classes, %d changed (%s), new %s" % (len(cb), len(chg), ", ".join(chg), sorted(n.rsplit("/", 1)[1][:-6] for n in cb - ca)))
    want_c = {"SmithPage", "ReforgePage", "LifePage", "UpgPage", "UpCmd", "ToolPtsCmd", "SkyyGearPlugin", "GearUi", "CfgFn", "CfgRows", "GearCfg"}   # Cfg*: the version text
    check(set(chg) <= want_c, "S315: only the expected classes changed: unexpected %s" % sorted(set(chg) - want_c))


# ====================================================================================================== H315
def run_h315(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h315(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H315: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h315(L, K):
    from jpype import JClass, JInt, JShort, JLong, JObject, JArray, JString, JImplements, JOverride
    import skyyui as SUI
    SUI.verify(quiet=True)
    br, Gear, Cfg, LL, Life, Up, Stamp = L["br"], L["Gear"], L["Cfg"], L["LL"], L["Life"], L["Up"], L["Stamp"]
    mkinv, world, PR1, U1, stack, skills, apply, logs, ids, us, jf, ITEM = (L["mkinv"], L["world"], L["PR1"], L["U1"], L["stack"], L["skills"],
                                                                            L["apply"], L["logs"], L["ids"], L["us"], L["jf"], L["ITEM"])
    P = lambda n: JClass(PKG + n)
    HB, GH, GHO, Smith, Ui = P("HubBar"), P("GearHub"), P("GearHubOpen"), P("GearSmith"), P("GearUi")
    Sysm = JClass("java.lang.System")
    HAL = JClass("java.util.ArrayList")

    def kc(cond, what):
        K.check(bool(cond), what)

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))
    apply()
    if Sysm.getProperties().get("skyy.bridge") is None:
        Sysm.getProperties().put("skyy.bridge", br)
    kc(HB.map() is not None, "H315 setup: the kit HubBar sees skyy.bridge")

    # ============================================================== R: the registry
    n_ = int(GHO.register())
    eq(n_, 4, "R register() puts the four tabs")
    def ent(t):
        o = HB.get("hub:tab:smithing:" + t)
        return None if o is None else [o[i] for i in range(len(o))]
    for t, lab, o in (("gear", "Smithing", 10), ("reforge", "Anvil", 30), ("upgrade", "Upgrade", 40), ("identify", "Identify", 60)):
        e = ent(t)
        kc(e is not None and str(e[0]) == "SkyyGear" and str(e[1]) == lab and int(e[2]) == o and str(e[6]) == "smithing_" + t,
           "R hub:tab:smithing:%s = {SkyyGear, %s, %d, icon smithing_%s}: %s" % (t, lab, o, t, [str(x) for x in e] if e else None))
    e = ent("identify")
    kc(e is not None and len(e) >= 8 and str(e[7]) == "reforge" and "HubHide" in str(e[5].getClass().getName()),
       "R identify is a MERGED tab of reforge (element 7 = reforge, element 5 = HubHide)")
    # a SkyySacks-like Crafting tab (order 5), as /craft's jar puts it
    br.put("hub:tab:smithing:recipes", JArray(JObject)([JString("SkyySacks"), JString("Crafting"), JObject(JInt(5), JClass("java.lang.Integer")), JString("craft"), None, None, JString("smithing_recipes")]))          # another jar's array
    tabs = [str(r[0]) for r in HB.tabs("smithing", U1)]
    eq(tabs, ["recipes", "gear", "reforge", "upgrade"], "R the strip's tabs (visible, by order): Crafting | Smithing | Anvil | Upgrade - Identify only inside the Anvil")
    subs = [str(r[0]) for r in HB.subTabs("smithing", U1)]
    eq(subs, ["identify"], "R the merged Identify page is listed by subTabs (Home's + Add keeps it)")

    # ---- row 1 defs (what SkyyMenu publishes): Home + the 7 hubs; the icon = an item the boot has
    TITLES = {"home": "Home", "character": "Character", "storage": "Storage", "market": "Market", "smithing": "Crafting", "world": "World",
              "social": "Social", "settings": "Settings"}
    ICON = "Tool_Pickaxe_Crude"
    for h_ in SUI.HUB_ROW_IDS:
        HB.def4(h_, TITLES[h_], "skymenu" if h_ == "home" else h_, ICON, None)
    ROWHUBS = [(h_, TITLES[h_], ICON) for h_ in SUI.HUB_ROW_IDS]

    # ============================================================== the page rig (FakePM10, render, click) - the H311 way
    FPM = JClass(FAKE_PKG + ".FakePM10")
    PLA = JClass("com.hypixel.hytale.server.entity.entities.Player") if False else JClass("com.hypixel.hytale.server.core.entity.entities.Player")
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
                    probs.append("append into #%s before it exists" % sel)
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
        pg_.build(ref, ub_, ue_, st)
        cl, ev = cmds(ub_), sels(ue_)
        rendered.append((cl, ev))
        txt = chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl)
        return txt, cl, ev, evd(ue_)

    def click(pg_, data):
        p0, c0 = int(FPM.packets), int(FPM.closes)
        pg_.handleDataEvent(ref, st, data)
        return int(FPM.packets) - p0 + int(FPM.closes) - c0

    def appends(cl):
        return [((v["selector"] or "").lstrip("#"), v["text"] if v["text"] and "{" in v["text"] else v["data"]) for v in cl
                if "Set" not in (v["type"] or "") and ((v["text"] and "{" in v["text"]) or (v["data"] and "{" in (v["data"] or "")))]

    TAB_SEL = SUI._tab_btn_style(True, "sky")

    def strip_of(cl):
        """[(label, lit)] of the tab strip #SkyyGHubTabs"""
        ap = appends(cl)
        out_ = []
        for i_, (p_, mk) in enumerate(ap):
            m_ = re.match(r"(?:Text)?Button #SkyyGHubT(\d+) ", mk)
            if p_ == "SkyyGHubTabs" and m_:
                lit = TAB_SEL in mk or SUI.theme_tab_style(True, "sky") in mk
                lab = None
                tm = re.search(r'Text: "([^"]*)"', mk)
                if tm and mk.startswith("TextButton"):
                    lab = tm.group(1)
                else:
                    for p2, mk2 in ap[i_ + 1:i_ + 4]:
                        if p2 == "SkyyGHubT" + m_.group(1) and mk2.startswith("Label"):
                            lab = re.search(r'Text: "([^"]*)"', mk2).group(1)
                out_.append((lab, lit))
        return out_

    def big_ok(cl, what):
        ap = appends(cl)
        mine = [(p_, mk) for p_, mk in ap if p_ == "SkyyGBigRow" or p_.startswith("SkyyGBigR") or (p_ == "SkyyGBody" and "#SkyyGBigRow " in mk)]
        twin = [(p_, mk) for p_, mk in SUI.hub_big_row_preview("SkyyG", ROWHUBS, "smithing", 1066, parent="SkyyGBody")]
        kc(mine == twin, "B %s: the big hub row = the kit twin byte for byte (%d appends): first diff %s" % (
            what, len(twin), next(((a, b) for a, b in zip(mine, twin) if a != b), (len(mine), len(twin)))))
        body = [mk for p_, mk in ap if p_ == "SkyyGBody"]
        kc(body and "#SkyyGBigRow " in body[0] and len(body) > 1 and "#SkyyGHubTabs " in body[1], "B %s: the big row is the body's first child, the strip the second" % what)

    def root_h(cl):
        for p_, mk in appends(cl):
            m_ = re.match(r"Group #SkyyGRoot \{ Anchor: \(Width: (\d+), Height: (\d+)\)", mk)
            if m_:
                return int(m_.group(1)), int(m_.group(2))
        return None

    # the big row's Python constants = SkyyMenu's Home row (BR_*), read from the SET's SkyyMenu build script
    msrc = open(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.34.py"), encoding="utf8").read()
    mm = re.search(r"^BR_H, BR_GAP, BR_BELOW, BR_PAD, BR_PADV, BR_ICON, BR_ICON_GAP, BR_LAB, BR_LAB_MIN, BR_ICON_MIN = ([0-9, ]+)$", msrc, re.M)
    kc(mm and [int(x) for x in mm.group(1).split(",")] == [SUI.BIG_ROW_H, SUI.BIG_ROW_GAP, SUI.BIG_ROW_BELOW, SUI.BIG_ROW_PAD, SUI.BIG_ROW_PADV,
                                                           SUI.BIG_ROW_ICON, SUI.BIG_ROW_ICON_GAP, SUI.BIG_ROW_LABEL, SUI.BIG_ROW_LABEL_MIN, SUI.BIG_ROW_ICON_MIN],
       "B the kit's big row = the SkyWynn Menu Home row's numbers (48 high, 6 apart, 8 under, padding 10 / 6, 32 px icon + 6, 18 px label to 12, icons from 120)")
    kc("BR_LABN = (\"(FontSize: %d, TextColor: %s, RenderBold: true" in msrc and SUI.big_row_label(False).startswith("(FontSize: 18, TextColor: %s, RenderBold: true" % SUI.color("button2Text")),
       "B the big row's label style = Home's (bold, button2Text / buttonText)")

    # ============================================================== B + C: every page
    SP, RP, LP, UP = P("SmithPage"), P("ReforgePage"), P("LifePage"), P("UpgPage")
    skills(Mining=30, Smithing=30, Foraging=30, Farming=30, Fishing=30)
    Life.sweep(PR1, inv, True)
    pages = []
    sp = SP(PR1)
    pages.append(("Smithing", sp, ("Smithing", True), (1100, 940)))
    rp = RP(PR1)
    pages.append(("Anvil", rp, ("Anvil", True), (1100, 976)))
    ri = RP(PR1)
    ri.anIdM = True
    pages.append(("Anvil > Identify", ri, ("Anvil", True), (1100, 976)))
    lp = LP(PR1)
    pages.append(("Upgrade (tools)", lp, ("Upgrade", True), (1100, 940)))
    up = UP(PR1)
    pages.append(("old Upgrade list", up, ("Upgrade", True), (1100, 940)))
    for nm, pg, want, size in pages:
        FPM.cur = pg
        txt, cl, ev, ed = render(pg)
        big_ok(cl, nm)
        sx = strip_of(cl)
        eq([l for l, _x in sx], ["Crafting", "Smithing", "Anvil", "Upgrade"], "B %s: the strip = Crafting | Smithing | Anvil | Upgrade" % nm)
        eq([l for l, x in sx if x], [want[0]], "B %s: its own tab is lit" % nm)
        kc("#SkyyGTab" not in txt and "#SkyyGTabs" not in txt, "B %s: no old inner tab row" % nm)
        eq(root_h(cl), size, "B %s: the page root" % nm)
        kc(any(e_ == '{"a":"hub:h:character"}' or "hub:h:character" in e_ for e_ in ed) and any("hub:upgrade" in e_ for e_ in ed),
           "B %s: the row and the strip are bound (hub:h:<hub>, hub:<tab>)" % nm)
        if nm.startswith("Anvil"):
            idm = nm.endswith("Identify")
            sub = [mk for p_, mk in appends(cl) if p_ == "SkyyGASub"]
            kc(len([m for m in sub if m.startswith("TextButton")]) == 2 and any("mode:5" in e_ for e_ in ed) and any("mode:0" in e_ for e_ in ed),
               "B %s: the Reforge | Identify sub-row under the strip (mode:0 / mode:5)" % nm)
    # the Home row size at the Home page width: 188 px buttons (SkyyMenu Home: 1552 inside)
    eq(SUI.assert_big_row_fits(1552), 188, "B on a Home-wide page the big row's buttons are exactly Home's 188 px")

    # ---- C: the clicks
    def go(pg, data, what, want_cls=None, self_=False):
        FPM.last = None
        FPM.cur = pg
        n0 = int(FPM.opens)
        a = click(pg, data)
        got = FPM.last
        if self_:
            kc(got is None and a == 1, "C %s: %s = this page redrawn once (answered %d)" % (what, data, a))
        else:
            kc(got is not None and str(got.getClass().getName()).endswith(want_cls) and int(FPM.opens) == n0 + 1,
               "C %s: %s opens the %s: %s" % (what, data, want_cls, None if got is None else got.getClass().getName()))
        return got
    for nm, pg, want, size in pages:
        render(pg)
        tok = '{"a":"hub:%s"}'
        if nm != "Smithing":
            go(pg, tok % "gear", nm, "SmithPage")
        else:
            go(pg, tok % "gear", nm, self_=True)
        if not nm.startswith("Anvil"):
            g = go(pg, tok % "reforge", nm, "ReforgePage")
            kc(g is not None and not bool(g.anIdM), "C %s: ... on its Reforge view" % nm)
        if nm not in ("Upgrade (tools)", "old Upgrade list"):
            go(pg, tok % "upgrade", nm, "LifePage")
        else:
            go(pg, tok % "upgrade", nm, self_=True)
        go(pg, '{"a":"hub:h:smithing"}', nm + " (row: Crafting = its own hub)", self_=True)
    # Anvil <-> Identify in place (the strip's Anvil on the Identify view, the sub-row both ways)
    FPM.last = None
    FPM.cur = rp
    rp.anIdM = False
    eq(click(rp, '{"a":"mode:5"}'), 1, "C Anvil: the sub-row's Identify is answered once")
    kc(bool(rp.anIdM) and FPM.last is None, "C Anvil: ... and switches to the Identify view in place (no new page)")
    eq(click(rp, '{"a":"hub:reforge"}'), 1, "C Anvil > Identify: the strip's Anvil is answered once")
    kc(not bool(rp.anIdM) and FPM.last is None, "C Anvil > Identify: ... back on the Reforge view in place")
    click(rp, '{"a":"hub:identify"}')
    kc(bool(rp.anIdM) and FPM.last is None, "C Anvil: a stale hub:identify click switches in place too")
    rp.anIdM = False
    # the merged Identify entry (Home shortcuts, /identify's tab, Right-now rows) = the Anvil's Identify view
    FPM.last = None
    GH.PRS.put(U1, PR1)          # the page's PlayerRef (in the game a Menu page's call finds it through Universe.getPlayer - no Universe in this boot)
    r_ = str(HB.openSub(PR1, U1, "smithing", "identify"))
    GH.PRS.remove(U1)
    got = FPM.last
    kc(r_ == "bridge" and got is not None and str(got.getClass().getName()).endswith("ReforgePage") and bool(got.anIdM),
       "C the merged Identify tab (HubBar.openSub) opens the Anvil on its Identify view: %s" % r_)
    for nm, pg, want, size in pages:
        for d_ in ('{"a":"hub:h:character"}', '{"a":"hub:h:home"}', '{"a":"hub:zzz"}', '{"a":"hub:h:zzz"}'):
            FPM.cur = pg
            a = click(pg, d_)
            kc(a >= 1, "C %s: %s is answered (%d)" % (nm, d_, a))
    c0 = int(FPM.closes)
    FPM.cur = sp
    sp.handleDataEvent(ref, st, '{"a":"hub:close"}')
    kc(int(FPM.closes) >= c0, "C the X (hub:close) is handled")
    kc(int(GH.N[1]) > 10 and int(GHO.N[0]) >= 8, "C the counters: %d hub clicks, %d tab opens" % (int(GH.N[1]), int(GHO.N[0])))

    # ============================================================== U: the tools page = Upgrade
    FPM.cur = lp
    txl, cll, evl, edl = render(lp)
    ap = appends(cll)
    i_re = [i for i, (p_, mk) in enumerate(ap) if "#SkyyGPReRow " in mk]
    i_up = [i for i, (p_, mk) in enumerate(ap) if "#SkyyGPTierRow " in mk]
    kc(i_re and i_up and i_up[0] > i_re[0] and 'TextButton #SkyyGPUp { Anchor: (Width: 160, Height: 44); Text: "Upgrade";' in ap[i_up[0]][1]
       and 'Text: "Tier up"' not in txl, "U the tools page: the UPGRADE button sits right below Reset points (the old Tier up, renamed)")
    UpC = P("UpCmd")
    def upcmd():
        FPM.last = None
        m_ = [m for m in UpC.class_.getDeclaredMethods() if str(m.getName()) == "execute"][0]
        m_.setAccessible(True)
        m_.invoke(UpC(), JArray(JObject)([None, st, ref, PR1, None]))
        return FPM.last
    g = upcmd()
    kc(g is not None and str(g.getClass().getName()).endswith("LifePage"), "U /upgrade opens the Upgrade tab = the tools page")
    apply(part__lifelong="false")
    g = upcmd()
    kc(g is not None and str(g.getClass().getName()).endswith("UpgPage"), "U lifelong tools off: /upgrade opens the 0.3.14 Upgrade list")
    kc(bool(GHO.shows(JInt(2))), "U lifelong off + part.upgrade on: the Upgrade tab still shows (the old list)")
    apply(part__lifelong="false", part__upgrade="false")
    kc(not bool(GHO.shows(JInt(2))) and "upgrade" not in [str(r[0]) for r in HB.tabs("smithing", U1)], "U lifelong + part.upgrade off: no Upgrade tab")
    apply(part__smithing="false")
    kc("gear" not in [str(r[0]) for r in HB.tabs("smithing", U1)], "U part.smithing off: no Smithing tab")
    apply()
    kc([str(r[0]) for r in HB.tabs("smithing", U1)] == ["recipes", "gear", "reforge", "upgrade"], "U the defaults again: the four tabs")

    # ============================================================== S: the set page's Upgrade
    hit = None
    for c_ in [int(x) for x in Smith.SHOW]:
        for g_ in Smith.groups(U1, JInt(c_), True):
            outs, rids = g_[1], g_[2]
            for i_ in range(len(outs)):
                if rids[i_] is None and Smith.prevOf(outs[i_]) is not None and Up.next(Smith.prevOf(outs[i_])) is not None \
                        and str(Up.next(Smith.prevOf(outs[i_]))) == str(outs[i_]):
                    hit = (g_, i_, str(outs[i_]), str(Smith.prevOf(outs[i_])))
                    break
            if hit:
                break
        if hit:
            break
    kc(hit is not None, "S a tier-up set exists (a piece made from its previous tier): %r" % ((hit[2:] if hit else None),))
    if hit:
        g_, i_, out, prev = hit
        sp2 = SP(PR1)
        sp2.grp = g_
        sp2.gkey = g_[0]
        sp2.view = JInt(1)
        sp2.rowPage = JInt(i_ // 6)
        FPM.cur = sp2
        txs, cls_, evs, eds = render(sp2)
        sp2.grp = sp2.findGroup(sp2.gkey) or g_
        tok = int(sp2.token)
        kc(("tup:%d:%d" % (i_, tok)) in " ".join(eds) and "To the Anvil" not in txs and "Open the Anvil" not in txs and '"Upgrade"' in txs,
           "S the piece row's button is UPGRADE (tup:<row>:<token>); no To the Anvil / Open the Anvil")
        for k2, s2 in list(cs.items()):
            for j_ in range(int(s2.getCapacity())):
                s2.setItemStackForSlot(JShort(j_), None)
        n0 = dict(ids(cs))
        Smith_due = None
        a = click(sp2, '{"a":"tup:%d:%d"}' % (i_, tok))
        kc(a == 1 and str(sp2.info).startswith("-") and ids(cs) == n0, "S without the %s: refused, nothing changed, answered once: %s" % (prev, sp2.info))
        # with the piece + the cost + the skill: the next tier (GearUp.upgrade)
        co = Up.cost(prev, out)
        cs["storage"].setItemStackForSlot(JShort(0), stack(prev))
        if co is not None:
            mids, mq = co[0], co[1]
            for j_ in range(len(mids)):
                cs["storage"].setItemStackForSlot(JShort(10 + j_), stack(str(mids[j_]), int(mq[j_]) + 3))
        skills(Mining=100, Smithing=100, Foraging=100, Farming=100, Fishing=100, Combat=100)
        Stamp.scan(PR1, inv)
        render(sp2)
        tok = int(sp2.token)
        JClass("java.lang.Thread").sleep(JLong(1500))
        ans = [click(sp2, '{"a":"tup:%d:%d"}' % (i_, tok)) for _ in range(2)]          # the repeat keeps the first click's answer
        got = ids(cs)
        kc(ans == [1, 1] and str(sp2.info).startswith("+") and got.get(out, 0) == 1 and got.get(prev, 0) == 0,
           "S with the %s + its cost + the skill: it is a %s now (GearUp.upgrade), ONE tier-up for two clicks of the same token: %s %s / %s"
           % (prev, out, ans, sp2.info, dict((k3, v3) for k3, v3 in got.items() if k3 in (out, prev))))
        # from Requip: taken out (wardrobe:fn:fetch), then tiered up
        for k2, s2 in list(cs.items()):
            for j_ in range(int(s2.getCapacity())):
                s2.setItemStackForSlot(JShort(j_), None)
        if co is not None:
            for j_ in range(len(mids)):
                cs["storage"].setItemStackForSlot(JShort(10 + j_), stack(str(mids[j_]), int(mq[j_]) + 3))
        RQ = [["eqA", prev]]
        FETCH = []

        @JImplements("java.util.function.Function")
        class RqList(object):
            @JOverride
            def apply(self, o):
                if str(o[1]) != "armor":
                    return JArray(JObject)([])
                return JArray(JObject)([JArray(JObject)([JString(a_), JString(b_)]) for a_, b_ in RQ])

        @JImplements("java.util.function.Function")
        class RqFetch(object):
            @JOverride
            def apply(self, o):
                FETCH.append(str(o[1]))
                m_ = [x for x in RQ if x[0] == str(o[1])]
                if not m_:
                    return JString("That item is not in your Requip.")
                RQ.remove(m_[0])
                cs["storage"].setItemStackForSlot(JShort(24), stack(m_[0][1]))
                return JString("ok")
        old_l, old_f = br.get("wardrobe:fn:list"), br.get("wardrobe:fn:fetch")
        br.put("wardrobe:fn:list", RqList())
        br.put("wardrobe:fn:fetch", RqFetch())
        try:
            # CRITIC FIX 1: the cost is short -> refused BEFORE anything moves (the piece stays in Requip)
            mats = {}
            for j_ in range(len(mids)) if co is not None else []:
                mats[10 + j_] = cs["storage"].getItemStack(JShort(10 + j_))
                cs["storage"].setItemStackForSlot(JShort(10 + j_), None)
            render(sp2)
            tok = int(sp2.token)
            JClass("java.lang.Thread").sleep(JLong(1500))
            a = click(sp2, '{"a":"tup:%d:%d"}' % (i_, tok))
            kc(a == 1 and FETCH == [] and len(RQ) == 1 and str(sp2.info).startswith("-") and "nothing was taken out of Requip" in str(sp2.info),
               "S (critic fix 1) the %s in Requip but the cost is short: refused, NOTHING taken out: %s %s" % (prev, FETCH, sp2.info))
            for j_, v_ in mats.items():
                cs["storage"].setItemStackForSlot(JShort(j_), v_)
            # CRITIC FIX 2: a FAILING inventory piece (a stack of 2 - 'split it first') does not block the passing one in Requip
            cs["storage"].setItemStackForSlot(JShort(30), stack(prev, 2))
            render(sp2)
            tok = int(sp2.token)
            JClass("java.lang.Thread").sleep(JLong(1500))
            a = click(sp2, '{"a":"tup:%d:%d"}' % (i_, tok))
            got = ids(cs)
            kc(a == 1 and FETCH == ["eqA"] and str(sp2.info).startswith("+") and got.get(out, 0) == 1 and got.get(prev, 0) == 2,
               "S (critic fix 2) a failing %s stack in the inventory + a passing one in Requip: the Requip one is taken out once and tiered up, the stack untouched: %s %s %s"
               % (prev, FETCH, sp2.info, dict((k3, v3) for k3, v3 in got.items() if k3 in (out, prev))))
        finally:
            if old_l is not None:
                br.put("wardrobe:fn:list", old_l)
            else:
                br.remove("wardrobe:fn:list")
            if old_f is not None:
                br.put("wardrobe:fn:fetch", old_f)
            else:
                br.remove("wardrobe:fn:fetch")
        kc(int(GHO.N[2]) >= 1 and int(GHO.N[3]) >= 1, "S the counters: %d set-page upgrades, %d refused" % (int(GHO.N[2]), int(GHO.N[3])))

    # ============================================================== every page rendered validates; removeAll takes only ours
    probs = []
    for cl_, ev_ in rendered:
        probs += validate(cl_, ev_)
    kc(not probs, "B every page rendered (%d) validates: %s" % (len(rendered), probs[:4]))
    HB.removeAll()
    kc(HB.get("hub:tab:smithing:gear") is None and HB.get("hub:tab:smithing:recipes") is not None, "R removeAll takes SkyyGear's tabs only (the Crafting tab stays)")
    K.notes.append("H315 logs: %s" % [x[:160] for x in logs() if "WARN" in x][:6])


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
        w = [why for pre, why in WAIVE + WAIVE_315 if str(f).startswith(pre)]
        if w:
            WAIVED.append("%s: %s (%s)" % (label, str(f)[:140], w[0]))
            continue
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, str(n)[:700]))
    return d


def main():
    H314_FLAGS = (("--mkfake", lambda: H310["run_mkfake10"](arg("--mkfake"))), ("--h314", lambda: H314["run_h314"](arg("--out"))),
                  ("--live314", lambda: H314["run_live314"](arg("--out"))),
                  ("--h313", lambda: H313["run_h313"](arg("--out"))), ("--live313", lambda: H313["run_live313"](arg("--out"))),
                  ("--h312", lambda: H312["run_h312"](arg("--out"))), ("--live312", lambda: H312["run_live312"](arg("--out"))),
                  ("--h311", lambda: H311["run_h311"](arg("--out"))), ("--h310", lambda: H310["run_h310"](arg("--out"))),
                  ("--life", lambda: H35["run_life"](arg("--out"))),
                  ("--verify", lambda: H["run_verify"](arg("--out"))), ("--h39", lambda: H39["run_h39"](arg("--out"))),
                  ("--h38", lambda: H38["run_h38"](arg("--out"))), ("--h37", lambda: H37["run_h37"](arg("--out"))),
                  ("--g36", lambda: H36["run_g36"](arg("--out"))), ("--snd", lambda: H36["run_snd"](arg("--out"))),
                  ("--till", lambda: H35["run_till"](arg("--out"))), ("--audit", lambda: H["run_audit"](arg("--out"))))
    for flag, fn in (("--h315", lambda: run_h315(arg("--out"))),) + H314_FLAGS:
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
    for f_ in (JAR, J314, FI7_SRC, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
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
            run_assets315()
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
            for pre, why in WAIVE_315:
                H37["L37_EXTRA"].append((pre, why))
            n0 = len(H37["FAILS"])
            H37["run_l35"](env_old)
            for f_ in H37["FAILS"][n0:]:
                w = [why for pre, why in WAIVE + WAIVE_315 if str(f_).startswith(pre)]
                if not w and L35_SUM.match(str(f_)):          # every L35 check that ran passed or is explained; only the old >= 300 count is short
                    w = ["every L35 check passed or is an explained deviation (unexpected []); only the old >= 300 count (the explained ones do not count as ok)"]
                if w:
                    WAIVED.append("L35: %s (%s)" % (str(f_)[:140], w[0]))
                else:
                    FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        run_children((("h311", "--h311", env_311), ("h312", "--h312", env_312), ("live", "--live312", env_312), ("h313", "--h313", env_313),
                      ("live313", "--live313", env_313), ("h314", "--h314", env), ("live314", "--live314", env),
                      ("h315", "--h315", env)))          # ours last (the children share the gear home)
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
