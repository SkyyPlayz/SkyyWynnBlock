"""Harness for SkyyGear 0.3.9 (tools/gear_0_3_9_patch.py header) = the 0.3.8 harness's children run on the 0.3.9 jar + H39 (one booted engine):
    python tools/gear_0_3_9_patch.py && python SkyyGear/build_skyygear_0.3.9.py
    python SkyyGear/test_skyygear_0.3.9.py [--keep] [--only assets,h39,verify,h38,h37,g36,snd,till,life,audit]

  S39  non-class entries 0.3.8 -> 0.3.9: the same entries, only manifest.json changes
  H39  ONE booted engine (the 0.3.5 life setup) + the vanilla Armor / Weapon items of the cached Assets.zip and their generated recipes:
       V  THE ROOT CAUSE + THE VALIDATOR: the 0.3.8 piece page parts with VerticalAlignment Top are refused by GearUi.bad (the 0.3.9 ones pass);
          bad parts (unbalanced, a { without an element, an underscore id, @ / %, an unknown ItemId, LayoutMode / alignment values the client
          does not know, a negative size) are refused; good ones (every kit card / row) pass. GearUi.ap skips a bad part AND everything
          appended into it / set on it / bound to it later in the same build (one WARN), a good build sends exactly what it was given
       P  EVERY PAGE THE CRAFT TAB CAN SHOW: each category (Mining / Foraging / Farming / Fishing), each card's piece page (every row page),
          at skill 2 and 45, every inline document checked the way the client parses it (the kit's check_markup + alignment / LayoutMode values,
          ItemId = a loaded item, no negative size), every parent created before use, no element id twice, every b.set / event on an element
          that exists; GearUi.bad agrees (no part skipped); the 0.3.5 figure output (same cells) as the control
       C  THE CATEGORIES: the left list = Mining / Foraging / Farming / Fishing armor only (no Combat armor, Weapons, Tools, Multitools, no class
          filter); GearSmith.cat: Farming P1 = 6, Foraging F1 = 5, Fishing A1 = 7, Copper = 1; the Farming P1 set is under Farming armor; the
          left column fits 656
       T  FIRST TIER ONLY: Copper / F1 / P1 / A1 sets craftable; Iron .. Adamantite + F2.. / P2.. / A2.. = "Tier up on the Anvil" cards (also
          without a recipe), their rows name the piece below + the materials + the skill; Mithril (no ladder step) stays craftable;
          GearSmith.craft refuses a tier-up piece; the REAL GearCraftPreSys on a REAL CraftRecipeEvent$Pre: Armor_Iron_Head cancelled with a
          chat line, Armor_Copper_Head / a combat piece / Creative not; garmor.ladders cleared = craftable again
       I  THE IDENTIFY TAB: the tab row Craft | Anvil | Identify | Tools (| Multitool) fits 1066; /reforge = the Anvil lists identified gear only
          (no Identify all, no re-identify strip); mode:5 = the Identify tab lists only bags / unidentified gear with Identify all + Select all +
          Identify picked; tick / Select all / Clear; Identify picked identifies exactly the ticked bags (coins each, one reveal card each), a
          ticked bag that left is skipped with a line, coins running out stops cleanly; /identify opens the Identify tab; stale clicks of the
          other tab do nothing; every Anvil / Identify page validated as in P
  VERIFY / H38 / H37 / G36 / SND / TILL / L35 / AA  the 0.3.8 harness's children on the 0.3.9 jar
Scratch: tools/dev/scratch/gear039/harness (deleted at the end unless --keep). Exit code 1 on any failure.
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


VERSION = "0.3.9"
V38 = "0.3.8"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear039")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J38 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V38))                       # read only
PKG = "com.skyy.gear."

# ---- the 0.3.8 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H38 = os.path.join(HERE, "test_skyygear_0.3.8.py")
_T38 = open(_H38, encoding="utf-8").read()
_cut = _T38.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H38, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H38 = {"__name__": "skyygear_h38", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T38[:_cut], _H38 + " (library)", "exec"), H38)
sys.argv = _argv
H37, H36, H35, H = H38["H37"], H38["H36"], H38["H35"], H38["H"]
Child, _jvm, jar_classes = H38["Child"], H38["_jvm"], H38["jar_classes"]
FAKE_DIR = H38["FAKE_DIR"]
FAKE_PKG = H38["FAKE_PKG"]
FAILS, OKS = [], [0]

ALIGN = {"Start", "Center", "End"}
LAYOUTS = {"Top", "Left", "Middle", "Center", "TopScrolling", "Full", "CenterMiddle", "MiddleCenter", "Right", "Bottom", "LeftWrap", "LeftCenterWrap"}
ELEM_RE = re.compile(r"(?:^|(?<=[;{}]))\s*([A-Z][A-Za-z]*)(?:\s+#([A-Za-z0-9_]+))?\s*\{")
# the 0.3.8 piece page parts (verbatim) - the control the client refused
OLD_BONUS = 'Label #SkyyGPBonus { Anchor: (Height: 66); Text: ""; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Top, Wrap: true); }'
OLD_ROLL = 'Label #SkyyGPRoll { Anchor: (Height: 88); Text: ""; Style: (FontSize: 14, TextColor: #878e9c, VerticalAlignment: Top, Wrap: true); }'


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


def strip_q(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == '"':
            j = i + 1
            while j < len(s) and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            out.append('""')
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


# ====================================================================================================== S39
def run_assets39():
    ea, eb = entries(J38), entries(JAR)
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(sorted(ea) == sorted(eb) and changed == ["manifest.json"],
          "S39: 0.3.8 -> 0.3.9: the same entries, only manifest.json changed among non-class files: %s / added %s gone %s"
          % (changed, sorted(set(eb) - set(ea))[:3], sorted(set(ea) - set(eb))[:3]))
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.9"' in man and "Identify (unidentified gear and mystery bags" in man and "the first tier is crafted" in man, "S39: the manifest names the round")


# ====================================================================================================== F: + FakeSmithPage
def run_mkfake9(out_dir):
    H35["run_mkfake5"](out_dir)
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fp = cp.makeClass(FAKE_PKG + ".FakeSmithPage")
    fp.setSuperclass(cp.get(PKG + "SmithPage"))
    fp.addField(CtField.make("public int rebuilds;", fp))
    fp.addField(CtField.make("public int closes;", fp))
    fp.addConstructor(CtNewConstructor.make("public FakeSmithPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.writeFile(out_dir)
    print("F+. FakeSmithPage written")


# ====================================================================================================== H39
def run_h39(out):
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h39(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H39: the phase raised: %s" % traceback.format_exc()[-1200:])
    K.save()


def _h39(L, K):
    from jpype import JClass, JInt, JShort, JLong, JObject, JArray, JString, JImplements, JOverride
    import skyyui as SUI
    ITEM, CRR, HAL, afs, AZP, gen_recipes = L["ITEM"], L["CRR"], L["HAL"], L["afs"], L["AZP"], L["gen_recipes"]
    br, Gear, Cfg, Data, Roll, Smith = L["br"], L["Gear"], L["Cfg"], L["Data"], L["Roll"], L["Smith"]
    mkinv, world, PR1, U1, stack, doc, skills, apply, logs, COINS, said, ids = (L["mkinv"], L["world"], L["PR1"], L["U1"], L["stack"], L["doc"],
                                                                                 L["skills"], L["apply"], L["logs"], L["COINS"], L["said"], L["ids"])
    us, jf, FCh, IHM = L["us"], L["jf"], L["FCh"], L["IHM"]
    P = lambda n: JClass(PKG + n)
    Ui, GA, Mine, Up, Unid, Ident, LLc = P("GearUi"), P("GearGArm"), P("GearMine"), P("GearUp"), P("GearUnid"), P("GearIdent"), P("GearLL")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Bool_ = JClass("java.lang.Boolean")

    # ---- the vanilla armor + weapon items (the life setup loads the tools only) and their recipes
    with zipfile.ZipFile(AZP) as az_:
        names = [n for n in az_.namelist() if (n.startswith("Server/Item/Items/Armor/") or n.startswith("Server/Item/Items/Weapon/")) and n.endswith(".json")]
    tl_ = HAL()
    for n in names:
        tl_.add(afs.getPath("/" + n))
    ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl_)
    newi = [ITEM.getAssetMap().getAsset(os.path.basename(n)[:-5]) for n in names]
    n_rc = gen_recipes([x for x in newi if x is not None])
    K.notes.append("H39: %d armor / weapon items loaded (%d missing), %d recipes generated" % (sum(1 for x in newi if x is not None), sum(1 for x in newi if x is None), n_rc))
    Smith.NAV_MS = JLong(0)
    Smith.RQ_MS = JLong(0)
    Smith.REC = None

    def item_ok(i_):
        return ITEM.getAssetMap().getAsset(i_) is not None

    # ---- the page reader + the client-side check
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

    def evs(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            v_ = None
            for f_ in ("selector",):
                try:
                    v_ = str(getattr(e_, f_))
                except Exception:
                    v_ = None
            out_.append(v_)
        return out_

    def pybad(d):
        try:
            SUI.check_markup(d, kit_paths=False)
        except ValueError as e_:
            return "kit: " + str(e_)[:200]
        bare = strip_q(d)
        for m_ in re.finditer(r"(Horizontal|Vertical)Alignment:\s*(\w+)", bare):
            if m_.group(2) not in ALIGN:
                return "%sAlignment %s" % (m_.group(1), m_.group(2))
        for m_ in re.finditer(r"LayoutMode:\s*(\w+)", bare):
            if m_.group(1) not in LAYOUTS:
                return "LayoutMode " + m_.group(1)
        for m_ in re.finditer(r'ItemId: "([^"]*)"', d):
            if not item_ok(m_.group(1)):
                return "ItemId %s is no item" % m_.group(1)
        if re.search(r"(Width|Height):\s*-", bare):
            return "negative size"
        return None

    def validate(cl, ev, what):
        """problems of one rendered page (the client's view): parse, parents, duplicate ids, sets / events on existing elements"""
        probs, known, made = [], set(), []
        for v in cl:
            t_ = v["text"] if v["text"] and "{" in v["text"] else (v["data"] if v["data"] and "{" in v["data"] else None)
            ty = (v["type"] or "")
            if t_ is not None and "Set" not in ty:
                sel = v["selector"]
                if sel not in (None, "None", "") and sel.lstrip("#") not in known:
                    probs.append("append into #%s before it exists" % sel)
                why = pybad(t_)
                jwhy = Ui.bad(t_)
                if why:
                    probs.append("%s: %s | %s" % (sel, why, t_[:140]))
                if (jwhy is None) != (why is None):
                    probs.append("validator disagree (java %s / py %s): %s" % (jwhy, why, t_[:140]))
                for m_ in ELEM_RE.finditer(strip_q(t_)):
                    if m_.group(2):
                        if m_.group(2) in known:
                            probs.append("#%s created twice" % m_.group(2))
                        known.add(m_.group(2))
                        made.append(m_.group(2))
            elif v["selector"] and "." in v["selector"]:
                tid = v["selector"].lstrip("#").split(".")[0]
                if tid not in known:
                    probs.append("set on #%s which does not exist" % tid)
        for e_ in ev:
            if e_ and e_.lstrip("#") not in known:
                probs.append("event on %s which does not exist" % e_)
        return probs

    def render(pg_, ref_, st_):
        ub_, ue_ = UCB(), UEB()
        n0 = int(Ui.UIN[1])
        pg_.build(ref_, ub_, ue_, st_)
        cl = cmds(ub_)
        ev = evs(ue_)
        txt = chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl)
        return txt, cl, ev, int(Ui.UIN[1]) - n0

    def child_sum(cl, parent, key="Height"):
        tot = 0
        for v in cl:
            t_ = v["text"] if v["text"] and "{" in v["text"] else None
            if t_ is None or v["selector"] != parent:
                continue
            m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", t_)
            if m_:
                h_ = re.search(key + r": (\d+)", m_.group(1))
                tot += int(h_.group(1)) if h_ else 0
        return tot

    # ============================================================================ V: the root cause + the validator
    fixed_b, fixed_r = OLD_BONUS.replace("Top", "Start"), OLD_ROLL.replace("Top", "Start")
    bads = {"unbalanced": "Group #SkyyGX { Anchor: (Height: 4); ", "no element": "Group { Anchor: (Height: 4); { } }", "underscore": "Group #Skyy_X { }",
            "variable": "Label { Style: (TextColor: @Gold); }", "placeholder": "Group { Anchor: (Height: %d); }", "item": 'ItemIcon { ItemId: "Nope_Not_An_Item"; }',
            "layout": "Group { LayoutMode: Sideways; }", "align": "Label { Style: (HorizontalAlignment: Left); }", "negative": "Group { Anchor: (Width: -4); }",
            "cross": "Group { Anchor: (Height: 4}; )", ";;": "Group { Anchor: (Height: 4);; }"}
    jb = dict((k_, Ui.bad(v_)) for k_, v_ in bads.items())
    K.check(Ui.bad(OLD_BONUS) is not None and "VerticalAlignment: Top is not" in str(Ui.bad(OLD_BONUS)) and Ui.bad(OLD_ROLL) is not None
            and pybad(OLD_BONUS) is not None and Ui.bad(fixed_b) is None and Ui.bad(fixed_r) is None and pybad(fixed_b) is None,
            "V1 ROOT CAUSE: the 0.3.8 #SkyyGPFig labels (VerticalAlignment Top) are refused by GearUi.bad and the client-side check (%s); 'Start' passes"
            % Ui.bad(OLD_BONUS))
    K.check(all(v_ is not None for v_ in jb.values()), "V2: GearUi.bad refuses every broken part: %s" % dict((k_, v_) for k_, v_ in jb.items() if v_ is None))
    goods = ['Group #SkyyGRoot { Anchor: (Width: 1100, Height: 880); }', 'Group #SkyyGTitle { Anchor: (Height: 38, Top: 0); Padding: (Top: 7); Background: (TexturePath: "Common/ContainerHeader.png", HorizontalBorder: 50, VerticalBorder: 0); Label #SkyyGTitleTxt { Padding: (Horizontal: 19); Text: ""; Style: (FontSize: 15, VerticalAlignment: Center, HorizontalAlignment: Center, RenderUppercase: true, TextColor: #b4c8c9, FontName: "Secondary", RenderBold: true); } }',
             'Group { Anchor: (Width: 80, Height: 80); Background: #000000(0.3); ItemIcon { Anchor: (Width: 72, Height: 72, Left: 4, Top: 4); ItemId: "Armor_Copper_Head"; } }',
             str(Ui.cell(JInt(64), "Armor_Farming_P1_Head")), str(P("GearAnvil").card("SkyyGCardI", JInt(562))), str(P("GearAnvil").head("SkyyGCardIT"))]
    K.check(all(Ui.bad(g_) is None for g_ in goods), "V3: good parts pass (frame, cells, the kit card / head): %s" % [(g_[:60], Ui.bad(g_)) for g_ in goods if Ui.bad(g_) is not None])
    ub = UCB()
    ue = UEB()
    BT = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType")
    EVD = JClass("com.hypixel.hytale.server.core.ui.builder.EventData")
    logs()
    Ui.ap(ub, None, "Group #SkyyGRoot { Anchor: (Width: 600, Height: 400); }")
    Ui.ap(ub, "#SkyyGRoot", "Group #SkyyGBad { Anchor: (Height: 40); LayoutMode: Top; Label #SkyyGBadL { Style: (VerticalAlignment: Top); } }")
    Ui.ap(ub, "#SkyyGBad", "Label #SkyyGKid { Anchor: (Height: 20); }")
    Ui.ap(ub, "#SkyyGKid", "Label #SkyyGKid2 { Anchor: (Height: 20); }")
    Ui.st(ub, "#SkyyGBadL.Text", "x")
    Ui.st(ub, "#SkyyGKid.Text", "x")
    Ui.on(ub, ue, BT.Activating, "#SkyyGKid", EVD.of("a", "x"))
    Ui.ap(ub, "#SkyyGRoot", "Label #SkyyGOk { Anchor: (Height: 20); }")
    Ui.st(ub, "#SkyyGOk.Text", "fine")
    Ui.on(ub, ue, BT.Activating, "#SkyyGOk", EVD.of("a", "ok"))
    clv, evv = cmds(ub), evs(ue)
    lg = logs()
    K.check(len(clv) == 3 and [v["selector"] for v in clv] == [None, "#SkyyGRoot", "#SkyyGOk.Text"] and evv == ["#SkyyGOk"]
            and len([x for x in lg if "was NOT sent" in x and "VerticalAlignment: Top" in x]) == 1 and not validate(clv, evv, "v"),
            "V4: GearUi.ap skips the bad part, everything appended into it (2 levels), its b.set and its event; the good parts go out; one WARN: %s / %s / %s"
            % ([v["selector"] for v in clv], evv, [x[:120] for x in lg if "NOT sent" in x]))

    # ============================================================================ P + C + T: every page of the Craft tab
    FSP = JClass(FAKE_PKG + ".FakeSmithPage")
    inv, cs = mkinv()
    ref, st, ch, pl = world(inv, cs, PR1)
    allp, n_pages, n_docs, skipped_total, cards_seen = [], 0, 0, 0, {}
    left_h, figs = [], {}
    for lvl_ in (2, 45):
        skills(Mining=lvl_, Foraging=lvl_, Farming=lvl_, Fishing=lvl_, Smithing=lvl_)
        pg = FSP(PR1)
        txt, cl, ev, sk = render(pg, ref, st)
        n_pages += 1
        allp += ["L%d overview: %s" % (lvl_, p_) for p_ in validate(cl, ev, "overview")]
        skipped_total += sk
        left_h.append(child_sum(cl, "#SkyyGLeft"))
        if lvl_ == 2:
            cats_btn = sorted(int(x) for x in re.findall(r"TextButton #SkyyGCat(\d+) ", txt))
            K.check(cats_btn == [1, 5, 6, 7] and "#SkyyGFltMine" not in txt and "#SkyyGFltAll" not in txt and "Class:" not in txt and "Show all" not in txt
                    and all(('Text: "%s"' % n_) in txt for n_ in ("Mining armor", "Foraging armor", "Farming armor", "Fishing armor"))
                    and not any(('Text: "%s"' % n_) in txt for n_ in ("Combat armor", "Weapons", "Multitools", "My class", "Show all")),
                    "C1: the Craft tab's left list = Mining / Foraging / Farming / Fishing armor (#SkyyGCat%s), no Combat armor / Weapons / Tools / "
                    "Multitools, no class filter" % cats_btn)
        for c_ in (1, 5, 6, 7):
            pg.handleDataEvent(ref, st, '{"a":"cat:%d"}' % c_)
            txt, cl, ev, sk = render(pg, ref, st)
            n_pages += 1
            skipped_total += sk
            allp += ["L%d cat %d: %s" % (lvl_, c_, p_) for p_ in validate(cl, ev, "cat")]
            if "click Show all" in txt:
                allp.append("L%d cat %d: the stale 'click Show all' line (review F5)" % (lvl_, c_))
            grp = list(Smith.groups(U1, JInt(c_), True))
            for pn_ in range(8):
                for i_ in range(len(grp)):
                    if i_ // 6 != pn_:
                        continue
                    pg.handleDataEvent(ref, st, '{"a":"card:%d"}' % i_)
                    for rp_ in range(3):
                        txt2, cl2, ev2, sk2 = render(pg, ref, st)
                        n_pages += 1
                        n_docs += sum(1 for v in cl2 if v["text"] and "{" in v["text"])
                        skipped_total += sk2
                        g_ = grp[i_]
                        key_ = str(g_[0])
                        cards_seen[(c_, key_)] = (bool(Smith.tierUp(g_)), txt2)
                        allp += ["L%d cat %d %s rows %d: %s" % (lvl_, c_, key_, rp_, p_) for p_ in validate(cl2, ev2, key_)]
                        figs.setdefault(key_, [v["text"] for v in cl2 if v["selector"] == "#SkyyGPFig"])
                        if "#SkyyGBtnRNext" not in txt2:
                            break
                        pg.handleDataEvent(ref, st, '{"a":"rnext"}')
                    pg.handleDataEvent(ref, st, '{"a":"pback"}')
                if (pn_ + 1) * 6 >= len(grp):
                    break
                pg.handleDataEvent(ref, st, '{"a":"next"}')
            pg.pageNo = 0
    K.check(not allp and skipped_total == 0 and n_pages > 30,
            "P1: EVERY Craft tab page (%d pages, %d piece-page documents: 4 categories x every card x every row page, skill 2 and 45) parses the way "
            "the client does, parents first, no id twice, sets / events on existing elements, no part skipped (%d): %s" % (n_pages, n_docs, skipped_total, allp[:6]))
    fig_docs = [d_ for v_ in figs.values() for d_ in v_]
    K.check(fig_docs and not [d_ for d_ in fig_docs if "VerticalAlignment: Top" in d_] and any("#SkyyGPBonus" in d_ and "VerticalAlignment: Start" in d_ for d_ in fig_docs),
            "P2: the #SkyyGPFig parts (figure rows + the 3 labels) of %d piece pages: no VerticalAlignment Top, the labels use Start" % len(figs))
    # control: the 0.3.5 figure output for the same cells (figure() is unchanged since 0.2.23): only the 2 labels differ
    ctl = [d_ for d_ in fig_docs if "ItemIcon" in d_]
    K.check(ctl and all(Ui.bad(d_) is None for d_ in ctl), "P3 (control): the figure rows (ItemIcon cells, identical to 0.3.5's) were always valid - %d checked" % len(ctl))
    K.check(max(left_h) <= 656, "C2: the left column fits (%s <= 656)" % left_h)
    K.check(int(Smith.cat("Armor_Farming_P1_Head")) == 6 and int(Smith.cat("Armor_Foraging_F1_Head")) == 5 and int(Smith.cat("Armor_Fishing_A1_Legs")) == 7
            and int(Smith.cat("Armor_Copper_Head")) == 1 and int(Smith.cat("Weapon_Sword_Iron")) == 2,
            "C3: GearSmith.cat: Farming P1 = 6, Foraging F1 = 5, Fishing A1 = 7, Copper = 1, a sword = 2 (not shown): %s"
            % [int(Smith.cat(x)) for x in ("Armor_Farming_P1_Head", "Armor_Foraging_F1_Head", "Armor_Fishing_A1_Legs", "Armor_Copper_Head", "Weapon_Sword_Iron")])
    keys_by = dict((c_, [str(g_[0]) for g_ in Smith.groups(U1, JInt(c_), True)]) for c_ in (0, 1, 5, 6, 7))
    K.check("Armor_Farming_P1" in keys_by[6] and "Armor_Farming_P1" not in keys_by[0] and "Armor_Foraging_F1" in keys_by[5] and "Armor_Fishing_A1" in keys_by[7]
            and "Armor_Copper" in keys_by[1], "C4: the Farming P1 set is a Farming armor card (not Combat armor); F1 / A1 / Copper in theirs: %s" % keys_by)
    # T: first tier only
    tu = dict(((c_, k_), v_[0]) for (c_, k_), v_ in cards_seen.items())
    want_tu = [(1, "Armor_%s" % t_) for t_ in ("Iron", "Thorium", "Cobalt", "Adamantite")] + [(5, "Armor_Foraging_F%d" % n_) for n_ in range(2, 6)] \
        + [(6, "Armor_Farming_P%d" % n_) for n_ in range(2, 8)] + [(7, "Armor_Fishing_A%d" % n_) for n_ in range(2, 6)]
    want_cr = [(1, "Armor_Copper"), (5, "Armor_Foraging_F1"), (6, "Armor_Farming_P1"), (7, "Armor_Fishing_A1")]
    K.check(all(tu.get(k_) is True for k_ in want_tu) and all(tu.get(k_) is False for k_ in want_cr),
            "T1: FIRST TIER ONLY: Copper / F1 / P1 / A1 craftable cards; Iron..Adamantite, F2-F5, P2-P7, A2-A5 'Tier up on the Anvil' cards (also without a recipe): "
            "missing / wrong %s" % ([k_ for k_ in want_tu if tu.get(k_) is not True] + [k_ for k_ in want_cr if tu.get(k_) is not False]))
    K.check(tu.get((1, "Armor_Mithril")) is False if (1, "Armor_Mithril") in tu else True,
            "T2: Mithril (no garmor.ladders step leads to it) stays craftable: %s" % tu.get((1, "Armor_Mithril")))
    ti_ = cards_seen.get((1, "Armor_Iron"), (None, ""))[1]
    K.check("Tier up a " in ti_ and "on the Anvil" in ti_ and "needs Mining" in ti_ and "To the Anvil" in ti_ and "#SkyyGBtnAnv" in ti_ and "craft:" not in ti_
            and "Craft every missing piece" not in ti_,
            "T3: the Iron set's piece page: rows 'Tier up a Copper ... on the Anvil' + materials + 'needs Mining N', To the Anvil / Open the Anvil, no Craft button")
    av = str(Smith.anvilOnly("Armor_Iron_Head"))
    rIron = [r_ for r_ in Smith.recipes() if str(r_[1]) == "Armor_Iron_Head"]
    crI = Smith.craft(inv, U1, "Tester", rIron[0][0], False) if rIron else None
    K.check(av.startswith("Not crafted: tier up a") and Smith.anvilOnly("Armor_Copper_Head") is None and Smith.anvilOnly("Armor_Cloth_Wool_Head") is None
            and crI is not None and int(crI[0]) == 0 and str(crI[1]) == av,
            "T4: GearSmith.anvilOnly + craft refuse Armor_Iron_Head (%s), never Copper or combat armor: %s" % (av, None if crI is None else str(crI[1])))
    # the REAL GearCraftPreSys on a REAL CraftRecipeEvent$Pre
    PreE = JClass("com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre")
    Pre = P("GearCraftPreSys")()

    def recipe_of(out_id):
        for rc_ in CRR.getAssetMap().getAssetMap().values():
            try:
                po = rc_.getPrimaryOutput()
                if po is not None and str(po.getItemId()) == out_id and int(po.getQuantity()) == 1:
                    return rc_
            except Exception:
                pass
        return None
    chC = us.allocateInstance(FCh.class_)
    chC.comps = IHM()
    chC.ref = ref
    PR1.said = None
    res_ = {}
    for oid in ("Armor_Iron_Head", "Armor_Copper_Head", "Armor_Cloth_Wool_Head", "Armor_Thorium_Legs"):
        rc_ = recipe_of(oid)
        if rc_ is None:
            res_[oid] = "no recipe"
            continue
        e_ = PreE(rc_, JInt(1))
        Pre.handle(JInt(0), chC, st, None, e_)
        res_[oid] = bool(e_.isCancelled())
    sd = said(PR1)
    gmf = None
    try:
        gmf = jf(JClass("com.hypixel.hytale.server.core.entity.entities.Player"), "gameMode")
        gmf.set(pl, JClass("com.hypixel.hytale.protocol.GameMode").Creative)
        e_ = PreE(recipe_of("Armor_Iron_Head"), JInt(1))
        Pre.handle(JInt(0), chC, st, None, e_)
        res_["creative"] = bool(e_.isCancelled())
        gmf.set(pl, None)
    except KeyError:
        K.notes.append("T5: Player has no gameMode field - the Creative case is not run")
    apply(garmor__ladders="")
    e_ = PreE(recipe_of("Armor_Iron_Head"), JInt(1))
    Pre.handle(JInt(0), chC, st, None, e_)
    res_["no ladders"] = bool(e_.isCancelled())
    keys_off = [str(g_[0]) for g_ in Smith.groups(U1, JInt(1), True) if not bool(Smith.tierUp(g_))]
    apply()
    K.check(res_.get("Armor_Iron_Head") is True and res_.get("Armor_Thorium_Legs") is True and res_.get("Armor_Copper_Head") is False
            and res_.get("Armor_Cloth_Wool_Head") in (False, "no recipe") and res_.get("creative", False) is False and res_.get("no ladders") is False
            and any("Gathering armor is crafted once at its first tier" in x for x in sd) and "Armor_Iron" in keys_off,
            "T5: CraftRecipeEvent$Pre (bench / pocket / SkyySacks 0.8.6 /craft): Iron / Thorium pieces cancelled with a chat line, Copper / combat cloth / "
            "Creative not; garmor.ladders cleared = craftable again (card too): %s | %s" % (res_, sd[-1:]))
    # review F1 / F2: gear.gatherAnvilOnly off = benches craft every tier, the Craft tab keeps the tier-up cards; part.upgrade off = nothing refused
    FRESH = L["FRESH"]
    K.check("\ngear.gatherAnvilOnly=true\n" in "\n" + str(P("GearCfg").defaultsText()) + "\n" and bool(P("GearCfg").GARM_ANVIL),
            "T6: the fresh config has the row gear.gatherAnvilOnly=true (default ON)")
    apply(gear__gatherAnvilOnly="false")
    e_ = PreE(recipe_of("Armor_Iron_Head"), JInt(1))
    Pre.handle(JInt(0), chC, st, None, e_)
    off_c = bool(e_.isCancelled())
    off_a = Smith.anvilOnly("Armor_Iron_Head")
    off_cards = [str(g_[0]) for g_ in Smith.groups(U1, JInt(1), True) if bool(Smith.tierUp(g_))]
    apply(part__upgrade="false")
    e_ = PreE(recipe_of("Armor_Iron_Head"), JInt(1))
    Pre.handle(JInt(0), chC, st, None, e_)
    up_c = bool(e_.isCancelled())
    up_cards = [str(g_[0]) for g_ in Smith.groups(U1, JInt(1), True) if bool(Smith.tierUp(g_))]
    apply()
    K.check(not off_c and off_a is None and "Armor_Iron" in off_cards and not up_c and Smith.anvilOnly("Armor_Iron_Head") is not None and not up_cards,
            "T7 (review F1/F2): gear.gatherAnvilOnly=false -> the bench crafts Iron (not cancelled), the Craft tab still shows the Iron tier-up card; "
            "part.upgrade=false -> nothing refused, no tier-up cards: %s / %s / %s" % (off_c, off_cards[:3], up_cards[:3]))

    # ---- why a Mage saw no combat cloth set (0.3.8): the facts for the report
    cloth = [str(r_[1]) for r_ in Smith.recipes() if str(r_[1]).startswith("Armor_Cloth_")]
    K.notes.append("H39 cloth: %d Armor_Cloth_* recipes on the 0.3.8 Craft-tab list (%s), armorType of Armor_Cloth_Wool_Head = %s, cat = %s"
                   % (len(cloth), cloth[:4], int(Smith.armorType("Armor_Cloth_Wool_Head")) if item_ok("Armor_Cloth_Wool_Head") else "no item",
                      int(Smith.cat("Armor_Cloth_Wool_Head"))))

    # ============================================================================ I: the Identify tab
    FRP = JClass(FAKE_PKG + ".FakeReforgePage")
    REV = []

    @JImplements("java.util.function.Function")
    class RevFn(object):
        @JOverride
        def apply(self, o):
            REV.append(o)
            return JObject(True, Bool_)
    br.put("explore:fn:reveal", RevFn())
    inv2, cs2 = mkinv()
    ref2, st2, ch2, pl2 = world(inv2, cs2, PR1)
    skills(Mining=20, Foraging=20, Farming=20, Fishing=20, Smithing=20)

    def bag(wid, lv=10):
        b_ = Unid.fromItem(stack(wid), JInt(1), JInt(lv), "drop")
        return b_
    sw = Data.put(stack("Weapon_Sword_Iron"), Roll.newDoc("Weapon_Sword_Iron", JInt(1), True, "craft", JInt(12)), None)
    b1, b2, b3 = bag("Weapon_Sword_Iron"), bag("Weapon_Axe_Iron"), bag("Weapon_Sword_Copper", 5)
    K.check(b1 is not None and b2 is not None and b3 is not None and bool(Unid.isBox(b1.getItemId())), "I0: three mystery bags made (GearUnid.fromItem)")
    cs2["hotbar"].setItemStackForSlot(JShort(0), sw)
    cs2["storage"].setItemStackForSlot(JShort(0), b1)
    cs2["storage"].setItemStackForSlot(JShort(1), b2)
    cs2["storage"].setItemStackForSlot(JShort(2), b3)
    rp = FRP(PR1)
    rp.anPreselect(inv2, False)
    txa, cla, eva, ska = render(rp, ref2, st2)
    tabs_ = re.findall(r'TextButton #SkyyGTab(\d+) \{ Anchor: \(Width: (\d+)', txa)
    tw_ = sum(int(w_) for _m, w_ in tabs_) + 5 * (len(tabs_) - 1)
    K.check([m_ for m_, _w in tabs_][:4] == ["3", "0", "5", "4"] and '"Identify"' in txa.replace('\\"', '"') and tw_ <= 1066
            and not validate(cla, eva, "anvil") and ska == 0,
            "I1: the tab row Craft | Anvil | Identify | Tools%s fits (%d <= 1066); the Anvil page validates: %s"
            % (" | Multitool" if len(tabs_) > 4 else "", tw_, validate(cla, eva, "anvil")[:4]))
    K.check("Your gear (1)" in txa and "#SkyyGBtnAll" not in txa and "#SkyyGTick" not in txa and "#SkyyGBtnRr" not in txa and "Mystery" not in txa.split("Your gear")[1][:4000].split("#SkyyGAnvil")[0],
            "I2: /reforge = the Anvil lists only the identified sword (no bags, no Identify all, no ticks, no re-identify)")
    rp.handleDataEvent(ref2, st2, '{"a":"mode:5"}')
    txi, cli, evi, ski = render(rp, ref2, st2)
    K.check(bool(rp.anIdM) and "Unidentified (3)" in txi and "#SkyyGBtnAll" in txi and "#SkyyGBtnTickAll" in txi and "#SkyyGBtnIdSel" in txi
            and txi.count("TextButton #SkyyGTick") == 3 and "Tick items below" in txi and not validate(cli, evi, "identify") and ski == 0
            and child_sum(cli, "#SkyyGListBox") <= 656,
            "I3: mode:5 = the Identify tab: only the 3 bags, Identify all + Select all + Identify picked, a tick box per row, list %d <= 656, validates: %s"
            % (child_sum(cli, "#SkyyGListBox"), validate(cli, evi, "identify")[:4]))
    rp.handleDataEvent(ref2, st2, '{"a":"forge"}')
    rp.handleDataEvent(ref2, st2, '{"a":"tick:0"}')
    rp.handleDataEvent(ref2, st2, '{"a":"tick:2"}')
    txk, clk, evk, _s = render(rp, ref2, st2)
    K.check(len(rp.anTick) == 2 and "2 picked - " in txk and not validate(clk, evk, "ticked"), "I4: tick rows 0 + 2 -> '2 picked - N coins' (a stale Anvil click did nothing)")
    rp.handleDataEvent(ref2, st2, '{"a":"tickall"}')
    n_all = len(rp.anTick)
    txc, _c, _e, _s = render(rp, ref2, st2)
    rp.handleDataEvent(ref2, st2, '{"a":"tickall"}')
    n_clr = len(rp.anTick)
    K.check(n_all == 3 and '"Clear"' in txc.replace('\\"', '"') and n_clr == 0, "I5: Select all ticks all 3 (the button says Clear), Clear unticks them")
    rp.handleDataEvent(ref2, st2, '{"a":"tick:0"}')
    rp.handleDataEvent(ref2, st2, '{"a":"tick:1"}')
    c0 = COINS[0]
    REV[:] = []
    cs2["storage"].setItemStackForSlot(JShort(1), None)          # bag 2 leaves after it was ticked
    rp.lastForge = JLong(0)
    rp.handleDataEvent(ref2, st2, '{"a":"idsel"}')
    left_ = [str(cs2["storage"].getItemStack(JShort(i_)).getItemId()) if cs2["storage"].getItemStack(JShort(i_)) is not None and not cs2["storage"].getItemStack(JShort(i_)).isEmpty() else None for i_ in range(3)]
    K.check(left_[0] is not None and not bool(Unid.isBox(left_[0])) and left_[2] is not None and bool(Unid.isBox(left_[2])) and COINS[0] < c0
            and "had left your inventory" in str(rp.info) and "Identified 1 of 1" in str(rp.info) and len(REV) == 1 and len(rp.anTick) == 0,
            "I6: Identify picked identifies exactly the ticked bag still there (coins %d -> %d), the bag that left is skipped with a line, the untouched bag "
            "stays a bag, one reveal page: %s | %s" % (c0, COINS[0], rp.info, left_))
    txr, clr, evr, skr = render(rp, ref2, st2)
    K.check(not validate(clr, evr, "after") and skr == 0, "I7: the Identify tab after the reveal validates: %s" % validate(clr, evr, "after")[:3])
    # review F3: Back from the reveal page = the Identify tab; review F4: the item that came out of the bag is in the Re-identify list
    K.check(str(Ident.backFor(rp)) == "identify" and "Unidentified (1)" in txr and "#SkyyGReHead" in txr and "Re-id " in txr
            and txr.count("TextButton #SkyyGTick") == 1 and int(rp.anNUn) == 1 and int(rp.rows.size()) == 2,
            "I7b (review F3/F4): backFor = identify on the Identify tab; the identified bag item sits in a 'Re-identify' list under the 1 bag left "
            "(cost shown, no tick box): %s" % [str(Ident.backFor(rp)), int(rp.anNUn), int(rp.rows.size())])
    rp.handleDataEvent(ref2, st2, '{"a":"tick:1"}')
    rp.handleDataEvent(ref2, st2, '{"a":"sel:1"}')
    txq, clq, evq, skq = render(rp, ref2, st2)
    K.check(len(rp.anTick) == 0 and "#SkyyGBtnRr" in txq and not validate(clq, evq, "reid") and skq == 0,
            "I7c (review F4): a Re-identify row cannot be ticked; picking it shows the re-identify strip (same action as before), the page validates")
    # coins run out: tick the last bag, no coins
    rp.handleDataEvent(ref2, st2, '{"a":"tickall"}')
    COINS[0] = 0
    rp.lastForge = JLong(0)
    rp.handleDataEvent(ref2, st2, '{"a":"idsel"}')
    still = cs2["storage"].getItemStack(JShort(2))
    K.check(still is not None and bool(Unid.isBox(still.getItemId())) and str(rp.info).startswith("-"), "I8: no coins = stops cleanly, the bag stays: %s" % rp.info)
    COINS[0] = 10 ** 7
    rp.handleDataEvent(ref2, st2, '{"a":"mode:0"}')
    txb, clb, evb, _s = render(rp, ref2, st2)
    rp.handleDataEvent(ref2, st2, '{"a":"idall"}')
    K.check(not bool(rp.anIdM) and "Your gear" in txb and not validate(clb, evb, "back") and cs2["storage"].getItemStack(JShort(2)) is not None
            and bool(Unid.isBox(cs2["storage"].getItemStack(JShort(2)).getItemId())),
            "I9: mode:0 = back on the Anvil (identified gear), a stale Identify all there does nothing")
    # every row of both tabs on the anvil: the Reforge / Upgrade / Sigil cards, the Identify card, the re-identify strip - no part skipped
    cs2["hotbar"].setItemStackForSlot(JShort(1), Data.put(stack("Armor_Copper_Head"), Roll.newDoc("Armor_Copper_Head", JInt(2), True, "craft", JInt(10)), None))
    cs2["hotbar"].setItemStackForSlot(JShort(2), Data.put(stack("Tool_Pickaxe_Iron"), Roll.newDoc("Tool_Pickaxe_Iron", JInt(1), True, "craft", JInt(20)), None))
    cs2["storage"].setItemStackForSlot(JShort(3), bag("Weapon_Axe_Iron"))
    rowp, nrow = [], 0
    for m_ in ("mode:0", "mode:5"):
        rp.handleDataEvent(ref2, st2, '{"a":"%s"}' % m_)
        render(rp, ref2, st2)
        for i_ in range(int(rp.rows.size())):
            rp.handleDataEvent(ref2, st2, '{"a":"sel:%d"}' % i_)
            txs, cls_, evs_, sks = render(rp, ref2, st2)
            nrow += 1
            rowp += ["%s row %d: %s" % (m_, i_, p_) for p_ in validate(cls_, evs_, "row")] + (["%s row %d: %d part(s) skipped" % (m_, i_, sks)] if sks else [])
    K.check(nrow >= 5 and not rowp, "I12: every row on the Anvil (Reforge / Level up / Upgrade cards, a Copper piece's tier-up) and on the Identify tab (the "
            "Identify card) renders and validates, nothing skipped (%d pages): %s" % (nrow, rowp[:4]))
    # /identify opens the Identify tab
    FPM = JClass(FAKE_PKG + ".FakePM")
    cmd = P("IdentifyCmd")()
    exe = [m_ for m_ in P("IdentifyCmd").class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
    exe.setAccessible(True)
    FPM.last = None
    exe.invoke(cmd, None, st2, ref2, PR1, None)
    op = FPM.last
    K.check(op is not None and str(op.getClass().getName()).endswith("ReforgePage") and bool(op.anIdM), "I10: /identify opens the Identify tab (ReforgePage anIdM)")
    K.check("page parts checked" in str(Ui.uiText()), "I11: %s" % Ui.uiText())
    K.notes.append("H39 logs: %s" % [x[:160] for x in logs() if "WARN" in x][:6])


# ====================================================================================================== main
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--root", SCR_ROOT], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, str(n)[:500]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: run_mkfake9(arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--h39", lambda: run_h39(arg("--out"))), ("--h38", lambda: H38["run_h38"](arg("--out"))),
                     ("--h37", lambda: H37["run_h37"](arg("--out"))), ("--g36", lambda: H36["run_g36"](arg("--out"))),
                     ("--snd", lambda: H36["run_snd"](arg("--out"))), ("--till", lambda: H35["run_till"](arg("--out"))),
                     ("--audit", lambda: H["run_audit"](arg("--out")))):
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
    for f_ in (JAR, J38, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
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
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets39()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("h39", "--h39"), ("verify", "--verify"), ("h38", "--h38"), ("h37", "--h37"), ("g36", "--g36"), ("snd", "--snd"), ("till", "--till")):
            if not want(label):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if want("life"):
            n0 = len(H37["FAILS"])
            H37["run_l35"](env)
            for f_ in H37["FAILS"][n0:]:
                FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        if want("audit"):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
