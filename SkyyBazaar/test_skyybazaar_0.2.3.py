"""Harness for SkyyBazaar 0.2.3 (the rarity + tooltip pass, LOOKS ONLY; tools/bazaar_0_2_3_patch.py). Build first:
    python tools/bazaar_0_2_3_patch.py && python SkyyBazaar/build_skyybazaar_0.2.3.py --with SkyyCollections/SkyyCollections-0.2.35.jar
    python SkyyBazaar/test_skyybazaar_0.2.3.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py + the 0.1.20 / 0.2.0 page stand-ins):
  S     static   the patch re-runs to identical bytes; line endings kept; no new command / system; the kit icon_cell(icon_bg=None) is
                 byte-identical for every other caller (SkyyAuctions / Accessories / Trees / Menu shapes)
  A     verify   every class loads + initialises
  C     compare  0.2.2 -> 0.2.3 (EXPECT below: BzMarket gains the tables + rar / rarity / tag / specMap, BzPage render / ordEditor, texts)
  K     catalog  every Catalog constant (products, prices, guard edges, caps) = 0.2.2's exactly - nothing priced or traded changes
  R     rarity   EXECUTED: BzMarket.rar / rarity / tag for EVERY product = an independent re-count from Assets.zip + tools/tier_tags.py
                 (+ null / "" / unknown / punctuated ids -> 0 / "" without an exception)
  P     page     EXECUTED on the stand-in engine: the detail of EVERY product renders (no exception) with the name in its rarity colour
                 (or rowName), the icon square in its rarity colour at 0.4 (or the faint grey), the tier line = tag(id); every grid
                 tab: each cell's square = its product's rarity; the element count stays under the kit guard (1000); the Auction House
                 detail (row-name name, grey square, tag line), the order editor (tier line + the two price lines) and MY ORDERS open;
                 the You hold line gold bold, the Demand line minor grey; every text identical in form to 0.2.2's
  D     live     scratch COPIES of the live NewBetaTest Skyy_SkyyBazaar: the 0.2.3 start = the 0.2.2 start byte-for-byte (no data change),
                 and a second 0.2.3 start writes nothing
  AA    audit    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI
import skyyench as EN
import tier_tags as TT

VERSION = "0.2.3"
PKG = "com.skyy.bazaar."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.2.2.jar")
GEN = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybazaar_0.2.2.py")
PATCH = os.path.join(ROOT, "tools", "bazaar_0_2_3_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_bazaar", "bz")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar")
EXPECT = {"BzMarket": ["+f RAR_SPEC", "+f TAG_SPEC", "+f RARS", "+f TAGS", "+m specMap", "+m rar", "+m rarity", "+m tag", "~<clinit>"],
          "BzPage": ["~m render", "~m ordEditor"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyBazaarPlugin": ["~m setup"]}   # + the version texts
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
RAR = ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic")
RCOL = [SUI.QUALITY["Common"], SUI.QUALITY["Uncommon"], SUI.QUALITY["Rare"], SUI.QUALITY["Epic"], SUI.QUALITY["Legendary"], SUI.RARITY["Mythic"]]
RBG_NONE = SUI.COLOR["disabled"] + "(0.15)"
GOLD = EN.TIP_LEVEL


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


_M = {}


def t21():
    if "21" not in _M:
        _M["21"] = tmod(os.path.join(HERE, "test_skyybazaar_0.2.1.py"), "tbz021")
    return _M["21"]


def t200():
    if "200" not in _M:
        _M["200"] = tmod(os.path.join(HERE, "test_skyybazaar_0.2.0.py"), "tbz0200")
    return _M["200"]


def expected_rarity(ids):
    """an independent re-count of the build's rule: tier_tags rarity rows, the Enchanted = Epic, a raw fish grade's id, the asset Quality
    (following Parent); anything else 0"""
    z = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    path = dict((n.rsplit("/", 1)[1][:-5], n) for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))

    def q(i, d=0):
        try:
            j = json.loads(z.read(path[i]).decode("utf-8", "replace"))
        except Exception:
            j = {}
        if "Quality" in j or d > 8 or j.get("Parent") not in path:
            return j.get("Quality")
        return q(j["Parent"], d + 1)
    out = {}
    for i in ids:
        rt = TT.rarity_tag_for(i)
        if rt:
            r = rt.split(" ")[0]
        elif i.startswith(EN.PREFIX):
            r = "Epic"
        elif re.fullmatch(r"Food_Fish_Raw_(Uncommon|Rare|Epic|Legendary)", i):
            r = i.rsplit("_", 1)[1]
        elif i in path:
            r = q(i)
        else:
            r = None
        out[i] = RAR.index(r) + 1 if r in RAR else 0
    z.close()
    return out


# ------------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.3"') == 1 and g.startswith('"""SkyyBazaar 0.2.3'), "S version + header")
    for w in ("registerSystem(", "registerCommand(", "CFG.row(", "Server Setup"):
        K.check(g.count(w) == o.count(w), "S no new %s (%d)" % (w, g.count(w)))
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    # the kit: icon_bg=None = every other caller's markup byte for byte (the shapes SkyyAuctions / Accessories / Trees / Menu use)
    J = SUI.J
    shapes = [("SkyyAhPk" + J("i", "0"), J("ids[i]", "Ore_Copper"), 74, "normal", dict(qty=True)),
              ("SkyyAcRowIc", "Weapon_Sword_Iron", 76, "selected", dict(look="plain")),
              ("SkyyTrN", None, 64, "disabled", dict(sound=None)),
              ("SkyyMnL", "Food_Bread", 87, "static", dict(qty="12")),
              ("SkyyTrW", "Weapon_Sword_Iron", 74, "normal", dict(w=158, h=76, icon=44, icon_left=6)),
              ("SkyyMnE", "Food_Bread", 74, "empty", {})]
    same = all(SUI.icon_cell(a, b, c, st, **kw) == SUI.icon_cell(a, b, c, st, icon_bg=None, **kw) for a, b, c, st, kw in shapes)
    K.check(same, "S kit icon_cell(icon_bg=None) = the old output for every shape (other mods unchanged)")
    fr = SUI.render(SUI.icon_cell("SkyyBzDIcon", "Ore_Copper", state="static", w=96, h=96, icon=80, icon_bg="#2770b7(0.4)"))
    K.check("Group #SkyyBzDIconIf { Anchor: (Width: 84, Height: 84, Left: 6, Top: 6); Background: #2770b7(0.4); } ItemIcon #SkyyBzDIconIc" in fr,
            "S the detail icon square: 84 px, 2 px around the 80 px icon, drawn before it")
    # no saved-data / price code touched: the Catalog / Market / Trader / BzBook / BzOrders sources are unchanged (only the page + BzMarket)
    K.check(g.count("public static int rar(String id)") == 1 and g.count("b.set(\"#SkyyBzDTier.Text\"") == 3, "S rar() + the tier line set in the 3 detail views")
    K.save()


def _consts(J):
    C = J("Catalog")
    from jpype import JClass
    Mod = JClass("java.lang.reflect.Modifier")
    out = {}
    for f in C.class_.getDeclaredFields():
        m = f.getModifiers()
        if not (Mod.isStatic(m) and Mod.isFinal(m)):
            continue
        f.setAccessible(True)
        v = f.get(None)
        t = str(f.getType().getName())
        if t == "[Ljava.lang.String;":
            out[str(f.getName())] = [str(x) for x in v]
        elif t == "[D":
            out[str(f.getName())] = [float(x) for x in v]
        elif t in ("java.lang.String", "int", "long", "double", "boolean"):
            out[str(f.getName())] = str(v)
    return out


def _dump_consts(jar_path, dst):
    from jpype import JClass
    HK.jvm([jar_path, B.SERVER_JAR], verify=True)
    json.dump(_consts(lambda n: JClass(PKG + n)), open(dst, "w"))


def run_catalog(out, jar, scratch, home):
    K = HK.Child(out)
    res = {}
    for tag, jp in (("old", OLD_JAR), ("new", jar)):
        dst = os.path.join(scratch, "consts_%s.json" % tag)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--dump-consts", jp, dst], capture_output=True, text=True)
        K.check(p.returncode == 0 and os.path.isfile(dst), "K constants of %s read: %s" % (os.path.basename(jp), p.stderr[-300:]))
        res[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}
    a, b = res["old"], res["new"]
    diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    K.check(not diff and len(a) > 10, "K every Catalog constant (%d: products, prices, guard edges, caps) = 0.2.2's (differ: %s)" % (len(a), diff))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- R
def run_rarity(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    J = lambda n: JClass(PKG + n)
    t21().bz_prep(J, os.path.join(scratch, "rar", "Skyy_SkyyBazaar"))
    C, BM = J("Catalog"), J("BzMarket")
    ids = sorted(str(p.id) for p in C.all())
    want = expected_rarity(ids)
    got = dict((i, int(BM.rar(i))) for i in ids)
    bad = [(i, got[i], want[i]) for i in ids if got[i] != want[i]]
    K.check(not bad and len(ids) >= 540, "R BzMarket.rar of every product (%d) = the independent re-count: %s" % (len(ids), bad[:5]))
    bad2 = [i for i in ids if str(BM.rarity(i)) != (RAR[got[i] - 1] if got[i] else "")]
    K.check(not bad2, "R rarity(id) names rar(id) for every product: %s" % bad2[:5])
    tb = [(i, str(BM.tag(i)), TT.tag_for(i)) for i in ids if str(BM.tag(i)) != (TT.tag_for(i) or "")]
    K.check(not tb, "R tag(id) = tools/tier_tags.py tag_for(id) for every product (\"\" untiered): %s" % tb[:5])
    from collections import Counter
    K.notes.append("R rarities: %s; tagged %d of %d" % (dict(Counter(RAR[v - 1] if v else "none" for v in got.values())), sum(1 for i in ids if str(BM.tag(i))), len(ids)))
    for i in ("Skyy_Ench_Copper", "Food_Fish_Raw_Uncommon", "Ingredient_Bar_Iron", "Ore_Copper"):
        if i in ids:
            K.notes.append("R %s: rar %d %r tag %r" % (i, got[i], str(BM.rarity(i)), str(BM.tag(i))))
    odd = [None, "", "No_Such_Item_X", "a|b:c", "Skyy_Ench_", "x" * 300]
    r = []
    for o in odd:
        try:
            r.append((int(BM.rar(o)), str(BM.rarity(o)), str(BM.tag(o))))
        except Exception as ex:
            r.append(("EXC", str(ex)[:80]))
    K.check(all(x == (0, "", "") for x in r), "R null / empty / unknown / punctuated / long ids -> 0, \"\", \"\" (never an error): %s" % r)
    K.check(int(BM.rar("Skyy_Ench_Copper")) == 4 and int(BM.rar("Food_Fish_Raw_Uncommon")) == 2, "R Enchanted Copper = Epic, the Uncommon raw fish = Uncommon")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- P
def _decl(apps, ident):
    """the markup that declares #ident (one element)"""
    for _p, mk in apps:
        s = SUI.render(mk)
        k = s.find("#%s {" % ident)
        if k >= 0:
            return s[k:k + 600]
    return None


def _bg(apps, ident):
    d = _decl(apps, ident)
    m = re.search(r"Background: ([^;]+);", d or "")
    return m.group(1).strip() if m else None


def _textcol(apps, ident):
    d = _decl(apps, ident)
    m = re.search(r"TextColor: (#[0-9A-Fa-f]{6,8})", d or "")
    return m.group(1).lower() if m else None


def _elems(apps):
    return sum(len(re.findall(r"(?:^|[ ;{}])(?:Group|Button|TextButton|Label|ItemIcon|TextField|ItemGrid|ItemSlot)\b[^{;]*\{", SUI.render(mk))) for _p, mk in apps)


def run_page(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JInt, JLong, JString
    K = HK.Child(out)
    T200 = t200()
    T20 = T200.T20
    W = T20.boot2(scratch, [jar], "page")
    W.E.br = JClass(PKG + "HubBar").map()
    E = W.E
    J = lambda n: JClass(PKG + n)
    home = os.path.join(scratch, "home_page")
    T200.prep(E, J, home)
    C, BM = J("Catalog"), J("BzMarket")
    ids = [str(p.id) for p in C.all()]
    T20.fake_items(E, ids)
    fx = T200.Fx(E, J)
    A, Bb, Cc = T200.mkplayers(W)
    ua = A.pr.getUuid()
    fx.purse[str(ua)] = 1000000
    E.br.put("hub:last:" + T200.U1, JClass("java.util.concurrent.ConcurrentHashMap")())
    J("BzHubOpen").register()
    J("HubBar").open(A.pr, ua, "market", "bazaar")
    E.pump(A)
    pg = A.pm.getCustomPage()
    K.check(pg is not None and "BzPage" in str(pg.getClass().getName()), "P the Bazaar page opens (%s)" % (None if pg is None else pg.getClass().getName()))
    iid, _ch = T200.pick(J)
    T20.give(A, iid, 7, 2)

    def click(a, **kw):
        pg_ = A.pm.getCustomPage()
        pg_.cfShown = 0
        d = {"a": a, "@BzFind": "", "@BzCf": ""}
        d.update(kw)
        A.pm.handleLegacyCustomPageEvent(A.ref, A.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(A)
        return A.pm.getCustomPage()

    # the product, hub-page checked as a whole (menu pattern, every set / binding names an element)
    pg.sel = iid
    pg.cat = C.get(iid).cat
    pg, cm, ev, ap = H.built(K, E, A, "PAGE product detail (%s)" % iid)
    hold = str(H.set_of(cm, "#SkyyBzDHold.Text"))
    K.check(hold.startswith("You hold 7") and "selling all pays" in hold, "P the You hold text as in 0.2.2: %s" % hold)
    K.check(_textcol(ap, "SkyyBzDHold") == GOLD and "RenderBold: true" in (_decl(ap, "SkyyBzDHold") or ""), "P You hold line: gold %s bold" % GOLD)
    K.check(_textcol(ap, "SkyyBzDDem") == SUI.COLOR["rowSub"] and str(H.set_of(cm, "#SkyyBzDDem.Text")).startswith("Demand "), "P Demand line: minor grey")
    K.check(_textcol(ap, "SkyyBzDBuy") == SUI.COLOR["success"].lower() and _textcol(ap, "SkyyBzDSell") == SUI.COLOR["error"].lower(), "P buy green / sell red kept")
    order = [x for x in re.findall(r"#(SkyyBzD[A-Za-z]+) \{", "\n".join(SUI.render(m) for _p, m in ap)) if x in ("SkyyBzDTier", "SkyyBzDBuy", "SkyyBzDSell", "SkyyBzDHold", "SkyyBzDDem", "SkyyBzDProc")]
    K.eq(order, (["SkyyBzDTier"] if TT.tag_for(iid) else []) + ["SkyyBzDBuy", "SkyyBzDSell", "SkyyBzDHold", "SkyyBzDDem", "SkyyBzDProc"],
         "P the tier line is the first detail line (only when %s has a tag: %r)" % (iid, TT.tag_for(iid)))
    dn = _decl(ap, "SkyyBzDName") or ""
    K.check("FontSize: 21" in dn and "RenderBold: true" in dn, "P the detail name: 21 px bold")
    # EVERY product's detail renders: name colour, icon square, tier line
    bad, nbad, ibad, tbad, maxel = [], [], [], [], (0, None)
    # fix round: the tier line appended only when tagged, in the name's rarity colour; every wrapped detail line measured at 42 vs 44 px
    gbad, gcol, ntag, over42, over44 = [], [], 0, [], []
    LW, LH42, LH44 = 440, 42, 44
    from collections import Counter
    small = min(Counter(str(C.get(i).cat) for i in ids).items(), key=lambda kv: kv[1])[0]     # the detail does not depend on the open tab
    import time as _t
    t0 = _t.time()
    for i in ids:
        p_ = C.get(i)
        pg.sel = i
        pg.cat = small
        pg.oSide = -1
        try:
            _pg, cm_, ev_ = H.build_page(E, A, pg)
        except Exception as ex:
            bad.append((i, str(ex)[:120]))
            continue
        ap_ = H.apps_of(cm_)
        r = int(BM.rar(i))
        wn = (RCOL[r - 1] if r else SUI.COLOR["rowName"]).lower()
        wb = (RCOL[r - 1] + "(0.4)") if r else RBG_NONE
        if _textcol(ap_, "SkyyBzDName") != wn:
            nbad.append((i, r, _textcol(ap_, "SkyyBzDName")))
        if _bg(ap_, "SkyyBzDIconIf") != wb:
            ibad.append((i, r, _bg(ap_, "SkyyBzDIconIf")))
        if str(H.set_of(cm_, "#SkyyBzDTier.Text") or "") != (TT.tag_for(i) or "") or H.set_of(cm_, "#SkyyBzDName.Text") != str(p_.name):
            tbad.append((i, H.set_of(cm_, "#SkyyBzDTier.Text")))
        tg_ = TT.tag_for(i) or ""
        has_ = _decl(ap_, "SkyyBzDTier") is not None
        if has_ != bool(tg_) or (H.set_of(cm_, "#SkyyBzDTier.Text") is not None) != bool(tg_):
            gbad.append((i, tg_, has_))
        if tg_:
            ntag += 1
            if _textcol(ap_, "SkyyBzDTier") != wn:
                gcol.append((i, r, _textcol(ap_, "SkyyBzDTier")))
        for k_, sz_, bd_ in (("DProc", 14, False), ("DHold", 15, True), ("DDem", 14, False)):
            t_ = str(H.set_of(cm_, "#SkyyBzD%s.Text" % k_) or "")
            hh_ = SUI.text_lines(t_, LW, sz_, bold=bd_) * SUI.line_height(sz_, bold=bd_) if t_ else 0
            if hh_ > LH42:
                over42.append((i, k_, round(hh_, 1)))
            if hh_ > LH44:
                over44.append((i, k_, round(hh_, 1)))
        n_ = _elems(ap_)
        if n_ > maxel[0]:
            maxel = (n_, i)
    K.notes.append("P %d detail renders in %.0f s (grid tab %s)" % (len(ids), _t.time() - t0, small))
    K.check(not bad, "P the detail of EVERY product (%d) renders without an exception: %s" % (len(ids), bad[:3]))
    K.check(not nbad, "P every detail name is in its rarity colour (rowName without one): %s" % nbad[:4])
    K.check(not ibad, "P every detail icon square = the rarity colour at 0.4 (faint grey without one): %s" % ibad[:4])
    K.check(not tbad, "P every tier line = tools/tier_tags.py tag_for (\"\" untiered), the name text unchanged: %s" % tbad[:4])
    K.check(not gbad and ntag > 0 and ntag < len(ids), "P fix: the tier line is appended (and set) only for a tagged product (%d of %d tagged; an untiered one has no blank strip): %s" % (ntag, len(ids), gbad[:4]))
    K.check(not gcol, "P fix: every tier line is in its product's rarity colour (rowName without one), not the You hold gold: %s" % gcol[:4])
    K.check(sorted(over42) == sorted(over44), "P fix: the 44 -> 42 px trim clips no detail line that fitted at 44: %s" % sorted(set(over42) - set(over44))[:4])
    K.notes.append("P detail lines taller than 44 px (already so in 0.2.2, not this round): %d %s" % (len(over44), over44[:6]))
    K.check(maxel[0] <= SUI.MAP_MAX_ELEMENTS, "P the most elements on a product page: %d (%s) <= %d" % (maxel[0], maxel[1], SUI.MAP_MAX_ELEMENTS))
    # every grid tab: each cell's square = its product's rarity
    cats = [str(c) for c in C.categories()]
    cbad, ncell = [], 0
    for c in cats:
        pg.cat = c
        pg.sel = None
        _pg, cm_, ev_ = H.build_page(E, A, pg)
        ap_ = H.apps_of(cm_)
        cells = [None if x is None else str(x) for x in list(pg.cells)]
        for k, cid in enumerate(cells):
            if cid is None:
                continue
            ncell += 1
            r = int(BM.rar(cid))
            wb = (RCOL[r - 1] + "(0.4)") if r else RBG_NONE
            if _bg(ap_, "SkyyBzCell%dIf" % k) != wb:
                cbad.append((c, k, cid, _bg(ap_, "SkyyBzCell%dIf" % k)))
        el = _elems(ap_)
        if el > maxel[0]:
            maxel = (el, "tab " + c)
    K.check(not cbad and ncell >= 100, "P every grid cell's square (%d cells in %d tabs) = its product's rarity: %s" % (ncell, len(cats), cbad[:4]))
    # the fullest grid: a search that matches everything (Show more after 180)
    pg.cat = cats[0]
    pg = click("find", **{"@BzFind": "e"})
    _pg, cm_, ev_ = H.build_page(E, A, pg)
    el = _elems(H.apps_of(cm_))
    K.check(el <= SUI.MAP_MAX_ELEMENTS, "P a wide search (%d cells shown) draws %d elements <= %d" % (len([x for x in list(pg.cells) if x is not None]), el, SUI.MAP_MAX_ELEMENTS))
    K.notes.append("P elements: most on a product page %s; the 'e' search %d" % (maxel, el))
    pg = click("fclear")
    # the order editor: the tier line + the two price lines
    pg.sel = iid
    pg.cat = C.get(iid).cat
    pg = click("obid", **{"@BzAmount": ""})
    pg, cm, ev, ap = H.built(K, E, A, "PAGE editor (buy order)")
    K.check(int(pg.oSide) == 0 and str(H.set_of(cm, "#SkyyBzDTier.Text") or "") == (TT.tag_for(iid) or "") and _decl(ap, "SkyyBzDIconIf") is not None
            and str(H.set_of(cm, "#SkyyBzOEh.Text")).startswith("New buy order"), "P the editor opens with the tier line + the rarity square")
    pg = click("odisc", **{"@BzOQ": "1", "@BzOP": "1"})
    # MY ORDERS
    pg = click("tabO")
    pg, cm, ev, ap = H.built(K, E, A, "PAGE MY ORDERS")
    K.check(bool(pg.myTab), "P MY ORDERS opens")
    # the Auction House detail: a stand-in SkyyAuctions (ah:fn:find / ah:fn:open, the 0.1.9 key contract) answers one listing row; a search
    # shows it as an AH cell, the cell click opens its detail
    from jpype import JImplements, JOverride
    ah_id = "Weapon_Sword_Iron"
    Int, Lng = JClass("java.lang.Integer"), JClass("java.lang.Long")

    @JImplements("java.util.function.Function")
    class AhFind:
        @JOverride
        def apply(self, q):
            l = JClass("java.util.ArrayList")()
            l.add(JArray(JObject)([JString(ah_id), JString("Iron Sword"), Int.valueOf(2), Lng.valueOf(50), Lng.valueOf(100), Lng.valueOf(2),
                                   JString("5m"), Int.valueOf(-1), JString("#ffffff")]))
            return l

    @JImplements("java.util.function.Function")
    class AhOpen:
        @JOverride
        def apply(self, o):
            return JClass("java.lang.Boolean").TRUE
    E.br.put("ah:fn:find", AhFind())
    E.br.put("ah:fn:open", AhOpen())
    pg = click("tab:0")
    pg = click("find", **{"@BzFind": "iron sword"})
    ahc = [k for k, x in enumerate(list(pg.ahCells)) if x is not None and str(x) == ah_id]
    K.check(bool(ahc), "P a search shows the stand-in Auction House listing as a cell (%s)" % ahc)
    if ahc:
        pg = click("cell:%d" % ahc[0], **{"@BzFind": "iron sword"})
        _pg, cm, ev = H.build_page(E, A, pg)
        ap = H.apps_of(cm)
        K.check(str(H.set_of(cm, "#SkyyBzDName.Text")) == "Auction House - Iron Sword" and _textcol(ap, "SkyyBzDName") == SUI.COLOR["rowName"].lower()
                and _bg(ap, "SkyyBzDIconIf") == RBG_NONE and str(H.set_of(cm, "#SkyyBzDTier.Text") or "") == str(BM.tag(ah_id))
                and "#SkyyBzAhOpen" in [s_ for s_, _t in ev] and _bg(ap, "SkyyBzCell%dIf" % ahc[0]) == RBG_NONE,
                "P the Auction House detail: row-name name, faint grey square (detail + cell), the tag line, OPEN IN AUCTION HOUSE (%s)"
                % str(H.set_of(cm, "#SkyyBzDName.Text")))
    E.br.remove("ah:fn:find")
    E.br.remove("ah:fn:open")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D
def _start(jar_path, home, dst):
    from jpype import JClass
    HK.jvm([jar_path, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    t21().bz_prep(lambda n: JClass(PKG + n), home)
    json.dump(dict((k, v) for k, v in HK.tree_hash(home).items()), open(dst, "w"))


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    other = home.rstrip("\\/") + "_old"
    shutil.copytree(home, other)
    hs = {}
    for tag, jp, h in (("old", OLD_JAR, other), ("new1", jar, home), ("new2", jar, home)):
        dst = os.path.join(scratch, "live_%s.json" % tag)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--start", jp, h, dst], capture_output=True, text=True)
        K.check(p.returncode == 0, "D %s start ran: %s" % (tag, p.stderr[-300:]))
        hs[tag] = json.load(open(dst)) if os.path.isfile(dst) else {}
    strip = lambda t: dict((k, v) for k, v in t.items() if not k.startswith("config-history") and k != "trades.log")
    da = sorted(k for k in set(strip(hs["old"])) | set(strip(hs["new1"])) if strip(hs["old"]).get(k) != strip(hs["new1"]).get(k))
    K.check(not da, "D the 0.2.3 start = the 0.2.2 start on the live data (files that differ: %s)" % da)
    K.check(hs["new1"] == hs["new2"], "D a second 0.2.3 start writes nothing (%s)" % sorted(k for k in set(hs["new1"]) | set(hs["new2"]) if hs["new1"].get(k) != hs["new2"].get(k))[:5])
    K.save()


if __name__ == "__main__":
    if "--dump-consts" in sys.argv:
        k = sys.argv.index("--dump-consts")
        _dump_consts(sys.argv[k + 1], sys.argv[k + 2])
        sys.exit(0)
    if "--start" in sys.argv:
        k = sys.argv.index("--start")
        _start(sys.argv[k + 1], sys.argv[k + 2], sys.argv[k + 3])
        sys.exit(0)
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("catalog", run_catalog), ("rarity", run_rarity), ("page", run_page), ("live", run_live)],
           live=(LIVE, "Skyy_SkyyBazaar"), script=__file__)
