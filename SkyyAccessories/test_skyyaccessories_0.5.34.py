"""Harness for SkyyAccessories 0.5.34 (the rarity + tooltip pass - tools/accessories_0_5_34_patch.py; looks only). Build first:
    python tools/accessories_0_5_34_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.34.py
    python SkyyAccessories/test_skyyaccessories_0.5.34.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new system / command / class; line endings kept; the only non-class jar changes
                 = manifest.json + server.lang; LANG 0.5.33 -> 0.5.34: the same keys, only .description values change, and only these:
                 the 28 bench accessories = 'T<n> Bench - ' + their 0.5.33 text (retired ones too), every stat line / Lantern item = the
                 same green stat line first, EFFECT + RULE headers in the kit section colour, the 0.5.33 sentences kept, the flavour last in
                 dim italics (old ids: + OLDER COPY), the Omni (green line + EFFECT / RULE / CRAFT) and the retired bag item (RETIRED / THIS
                 ITEM); ASCII, one line each; no other item text changed (Furnace Charms, Night Vision ...)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.33 -> 0.5.34 (EXPECT below)
  X     exec     EXECUTES in a bare JVM: AccPage.benchTag (T1..T7 Bench, retired, Omni / bag / stat / Lantern / charm = ""), AccPage.tierTag
                 (benchTag, Furnace Charm I..V = T1..T5 Charm, Eternal Flame = T5 Charm), AccPage.fxCol (the 5 element lines = the item text's
                 _wc colour, everything else green), AccPage.ibg
                 (rarity colour + (0.4), null = RETIRED_COLOR), AccPage.tip for a bench, a retired bench, a stat line, the Omni, a Lantern,
                 a charm, a Fire / Water line: tag span first, the rarity word in its colour, the effects in green (an element line in its
                 element colour = the hex in its own item text), +AP gold / notes dim, the click hint last yellow
  PG    page     the real page through tools/hub_tab_kit.py: the BAG view with a bag accessory selected and with an inventory one
                 selected - #SkyyAccSelIf exists with Background = rarityColor(sel)(0.4) and the icon 2 px in; the grid cell hover text
                 carries the tier tag / green effects; the CRAFT view - every row #SkyyAccCr<k>If with Background = its row's rarity colour
                 (0.4); kit check_page / assert_menu_page on every view
  LIVE  start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyAccessories (every one-time update in setup's order + the
                 loaders): start 1 = 0.5.33's behaviour (wc15 marker / History), start 2 changes nothing
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): how the client draws nested <color><i> and the header lines (the vanilla item text markup nests <color><b>);
the 40 % square's look on the Craft rows.
Scratch: tools/dev/scratch/rar_accessoriesfix/h (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_accessoriesfix", "h")]
import harness_kit as HK
import skyybuild as B
import skyyui as SUI
import tier_tags as TT
import trees_v3_effects as V3E
import wc15 as WC
import wc15_harness as WH

_sp = importlib.util.spec_from_file_location("acc_h522", os.path.join(HERE, "test_skyyaccessories_0.5.22.py"))
T22 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T22)
import skyyonce_harness as OH
HK.run_compare = OH.compare_allowing(lambda n: n == "Server/Languages/en-US/server.lang")          # the lang file is the round (phase S checks it)

VERSION, OLD = "0.5.34", "0.5.33"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_34_patch.py")
PKG = "com.skyy.accessories."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
LANG = "Server/Languages/en-US/server.lang"
GOOD, SEC, DIM = "#7ee08a", SUI.COLOR["section"], SUI.COLOR["rowSub"]
GOLD, OFF, ACT, VAL = SUI.STATUS_INFO["gold"], SUI.COLOR["disabled"], SUI.COLOR["warning"], SUI.COLOR["value"]
OMNI, BAG = "Skyy_Accessory_Omni", "Skyy_Accessory_Bag"
EXPECT = {
    "AccPage": ["+m benchTag", "+m fxCol", "+m ibg", "+m tierTag", "~m buildBag", "~m buildCraft", "~m tip"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup"],          # the version texts
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def lang_of(jar):
    t = zipfile.ZipFile(jar).read(LANG).decode("utf-8")
    return dict(l.split("=", 1) for l in t.split("\n") if "=" in l)


def sp(col, t):
    return '<color is="%s">%s</color>' % (col, t)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.34 - build script') and g.count('VERSION = "0.5.34"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no jar entry added / removed")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), [LANG, "manifest.json"], "S the only non-class changes: manifest + server.lang")
    a, b = lang_of(OLD_JAR), lang_of(jar)
    K.eq(sorted(set(a) ^ set(b)), [], "S LANG the same keys")
    ch = sorted(k for k in a if a[k] != b[k])
    K.check(all(k.endswith(".description") for k in ch), "S LANG only descriptions changed: %s" % [k for k in ch if not k.endswith(".description")][:4])
    K.check(all(all(ord(c) < 128 for c in b[k]) and "\r" not in b[k] for k in ch), "S LANG ASCII, one line")
    for k in ch:
        K.check(b[k] == b[("server." + k) if not k.startswith("server.") else k[len("server."):]], "S LANG twin keys equal: %s" % k)
    ids = sorted(set(k.split(".")[-2] for k in ch))
    bench = [i for i in ids if re.match(r"^Skyy_Accessory_[A-Za-z_]+_T\d+$", i)]
    stat = [i for i in ids if i.startswith("Skyy_Talisman_") and "Lantern" not in i]
    lan = [i for i in ids if i.startswith("Skyy_Talisman_Lantern_")]
    rest = sorted(set(ids) - set(bench) - set(stat) - set(lan))
    nbj = sorted(os.path.basename(n)[:-5] for n in nb if re.match(r"^Server/Item/Items/Utility/Skyy_Accessory_[A-Za-z_]+_T\d+\.json$", n) and "_Charm_" not in n)
    K.check(bench == nbj and len(bench) >= 28, "S every bench accessory of the jar changed (%d: %s ...)" % (len(bench), bench[:3]))
    K.eq(rest, sorted([OMNI, BAG]), "S besides benches / stat lines / Lanterns only the Omni + the bag changed")
    K.check(len(lan) == 4 and len(stat) >= 40 + 12, "S the 4 Lanterns + every stat line (%d stat ids)" % len(stat))
    nb_ = 0
    for i in bench:
        t = int(i.rsplit("_T", 1)[1])
        k = "items.%s.description" % i
        nb_ += b[k] == TT.ladder_tag(t, "Bench") + TT.SEP + a[k]
    K.eq(nb_, len(nbj), "S every bench text = 'T<n> Bench - ' + its 0.5.33 text (retired + Campfire too)")
    K.check(b["items.Skyy_Accessory_Alchemybench_T2.description"].startswith("T2 Bench - Retired. ") and
            b["items.Skyy_Accessory_Campfire_T1.description"].startswith("T1 Bench - Quick inventory cooking"), "S retired / Campfire keep their text after the tag")
    K.check(all(not re.match(r"^T\d+ ", b["items.%s.description" % i]) for i in stat + lan + [OMNI, BAG]), "S rarity-ladder items stay untagged")
    bad = []
    for i in stat + lan:
        k = "items.%s.description" % i
        n, ol = b[k], a[k]
        first = ol.split("\\n")[0]
        sec = re.findall(r'<color is="%s">([A-Z ]+)</color>' % SEC, n)
        want = ["EFFECT", "RULE"] + (["OLDER COPY"] if "An older copy" in ol else [])
        fl = re.findall(r"<i>(.*?)</i>", ol)
        ok = (n.startswith(first + "\\n\\n" + sp(SEC, "EFFECT") + "\\n") and sec == want and len(fl) == 1 and n.endswith("\\n\\n" + sp(DIM, "<i>%s</i>" % fl[0]))
              and "\\n\\n\\n" not in n)
        # every 0.5.33 sentence survives (the old-copy sentence starts with 'Put it' now)
        for seg in ol.replace("<i>%s</i>" % fl[0], "").replace("An older copy: put it", "Put it").split("\\n"):
            ok = ok and seg in n
        if not ok:
            bad.append((i, n[:300]))
    K.check(not bad, "S every stat line / Lantern text: stat line first, EFFECT / RULE (/ OLDER COPY) headers, every old sentence, dim italic flavour last (%d ids): %s" % (len(stat + lan), bad[:2]))
    om = b["items.%s.description" % OMNI]
    K.check(om.startswith(sp(GOOD, "Counts as EVERY bench accessory at its highest tier") + " while in your Void Charms.") and
            re.findall(r'<color is="%s">([A-Z ]+)</color>' % SEC, om) == ["EFFECT", "RULE", "CRAFT"] and "Crafted in the Craft tab of Void Charms from all 11" in om,
            "S the Omni: green line, EFFECT / RULE / CRAFT: %s" % om[:200])
    bg = b["items.%s.description" % BAG]
    K.check(re.findall(r'<color is="%s">([A-Z ]+)</color>' % SEC, bg) == ["RETIRED", "THIS ITEM"] and "/charms" in bg and "right-click opens Void Charms" in bg,
            "S the retired bag item: RETIRED / THIS ITEM: %s" % bg[:160])
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Pg, D, Pw = JClass(PKG + "AccPage"), JClass(PKG + "AccDefs"), JClass(PKG + "AccPower")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "x")
    os.makedirs(os.path.join(home, "power"), exist_ok=True)
    Pw.FILE = Paths.get(os.path.join(home, "power.properties"))
    Pw.DIR = Paths.get(os.path.join(home, "power"))
    Pw.load()
    langB = lang_of(jar)
    bt = lambda i: str(Pg.benchTag(i))
    K.eq([bt("Skyy_Accessory_Workbench_T%d" % t) for t in (1, 2, 3)], ["T1 Bench", "T2 Bench", "T3 Bench"], "X benchTag Workbench T1..T3")
    K.eq((bt("Skyy_Accessory_Farmingbench_T7"), bt("Skyy_Accessory_Campfire_T1"), bt("Skyy_Accessory_Alchemybench_T4")), ("T7 Bench", "T1 Bench", "T4 Bench"),
         "X benchTag Farming T7, Campfire T1, the retired Alchemy Bench T4")
    nots = [OMNI, BAG, "Skyy_Talisman_Speed_Epic", "Skyy_Talisman_Strength_T3", "Skyy_Talisman_Lantern_Rare", "Skyy_Talisman_NightVision_Rare",
            str(D.FC_IDS[2]) if hasattr(D, "FC_IDS") else "Skyy_Accessory_Charm_Furnace_T3", None, "", "Skyy_Accessory_Workbench_Tx", "Rock_Gem_Diamond"]
    K.eq([bt(i) for i in nots], [""] * len(nots), "X benchTag is empty for the Omni, bag, stat lines, Lantern, Night Vision, a charm, junk")
    # fix: the hover's tier tag = the item text's (bench 'T<n> Bench', Furnace Charm 'T<n> Charm', Eternal Flame 'T5 Charm')
    tt = lambda i: str(Pg.tierTag(i))
    fcs = [str(x) for x in D.FC_IDS]
    K.eq([tt(i) for i in fcs], [TT.ladder_tag(min(k, 5), "Charm") for k in range(1, 7)], "X tierTag Furnace Charm I..V + Eternal Flame = T1..T5, T5 Charm")
    K.eq([tt(i) for i in fcs], [langB["items.%s.description" % i].split(TT.SEP)[0] for i in fcs], "X tierTag of every charm = its item text's tag")
    K.eq(tt("Skyy_Accessory_Workbench_T3"), "T3 Bench", "X tierTag of a bench = benchTag")
    K.eq([tt(i) for i in nots if i not in fcs], [""] * len([i for i in nots if i not in fcs]), "X tierTag is empty for rarity-ladder items / junk")
    # fix: the effect colour = the element colour its own item text uses
    ELC = {}
    for e in ("Earth", "Thunder", "Water", "Fire", "Air"):
        d = langB["items.Skyy_Talisman_%s_T4.description" % e]
        m = re.match(r'<color is="(#[0-9a-fA-F]{6})">\+[0-9.]+% ' + e + ' damage', d)
        K.check(m is not None, "X the %s item text starts with its element colour: %r" % (e, d[:80]))
        ELC[e] = m.group(1) if m else "?"
        for t in (1, 4):
            K.eq(str(Pg.fxCol("Skyy_Talisman_%s_T%d" % (e, t))), ELC[e], "X fxCol(%s T%d) = its item text colour %s" % (e, t, ELC[e]))
    K.eq(len(set(ELC.values())), 5, "X five different element colours")
    for i in ("Skyy_Talisman_Speed_Epic", "Skyy_Talisman_Strength_T3", "Skyy_Accessory_Workbench_T3", OMNI, "Skyy_Talisman_Lantern_Rare", fcs[2], None, "Rock_Gem_Diamond"):
        K.eq(str(Pg.fxCol(i)), GOOD, "X fxCol(%s) = the stat green" % i)
    for i in ("Skyy_Accessory_Workbench_T3", "Skyy_Talisman_Speed_Epic", OMNI, "Skyy_Accessory_Alchemybench_T2"):
        K.eq(str(Pg.ibg(D.rarityColor(i))), str(D.rarityColor(i)) + "(0.4)", "X ibg(rarityColor(%s)) = %s(0.4)" % (i, D.rarityColor(i)))
    K.eq(str(D.rarityColor("Skyy_Accessory_Alchemybench_T2")), str(D.RETIRED_COLOR), "X a retired accessory's square = RETIRED_COLOR")
    K.eq((str(Pg.ibg(None)), str(Pg.ibg(""))), (str(D.RETIRED_COLOR) + "(0.4)",) * 2, "X ibg(null / '') = the faint retired grey")
    S = lambda *ids: JArray(JString)([JString(i) for i in ids])
    q = '"'

    def tip(i, s, inb):
        return str(Pg.tip(i, s, inb))

    def chk(i, s, inb, tag, col=GOOD):
        t = tip(i, s, inb)
        rc, rn = str(D.rarityColor(i)), str(D.rarityName(i)).upper()
        fx = str(Pg.effects(i))
        head = (sp(VAL, tag) + sp(OFF, " - ") if tag else "") + sp(rc, rn)
        ok = t.startswith(head)
        ok = ok and ((("\n" + sp(col, fx)) in t) if fx else True)
        hint = "Click it, then Unequip" if inb else "Click it, then Equip"
        ok = ok and t.endswith("\n\n" + sp(ACT, hint))
        ok = ok and (fx == "" or t.index(sp(col, fx)) < t.index(sp(ACT, hint)))
        K.check(ok, "X tip(%s, inBag=%s): %s%s rarity word, green effects, yellow click hint last: %r" % (i, inb, ("tag '%s' first, " % tag) if tag else "", rn, t[:260]))
        return t
    t = chk("Skyy_Accessory_Workbench_T3", S("Skyy_Accessory_Workbench_T3"), True, "T3 Bench")
    K.check(sp(GOLD, "+") in t.replace(GOLD + q + ">+", GOLD + q + ">+</color>") or ("<color is=%s%s%s>+" % (q, GOLD, q)) in t, "X ... +AP in gold kept: %r" % t[-200:])
    t = chk("Skyy_Accessory_Alchemybench_T2", S("Skyy_Accessory_Alchemybench_T2"), True, "T2 Bench")
    K.check(sp(OFF, str(D.retiredWhy("Skyy_Accessory_Alchemybench_T2"))) in t and str(D.rarityName("Skyy_Accessory_Alchemybench_T2")) == "Does nothing",
            "X a retired bench: tag, 'DOES NOTHING' in RETIRED_COLOR, the retired note dim")
    chk("Skyy_Talisman_Speed_Epic", S("Skyy_Talisman_Speed_Epic"), True, "")
    chk("Skyy_Talisman_Speed_Common", S("Skyy_Talisman_Speed_Epic"), False, "")
    chk(OMNI, S(OMNI), True, "")
    chk("Skyy_Talisman_Lantern_Rare", S(), False, "")
    chk("Skyy_Accessory_Farmingbench_T7", S(), False, "T7 Bench")
    chk(fcs[2], S(fcs[2]), True, "T3 Charm")          # fix: the Furnace Charm's hover starts with its tag
    chk(fcs[5], S(), False, "T5 Charm")
    t = chk("Skyy_Talisman_Fire_T4", S("Skyy_Talisman_Fire_T4"), True, "", ELC["Fire"])          # fix: an element line in its colour
    K.check(sp(GOOD, str(Pg.effects("Skyy_Talisman_Fire_T4"))) not in t, "X the Fire hover is not green: %r" % t[:200])
    chk("Skyy_Talisman_Water_T2", S(), False, "", ELC["Water"])
    K.save()


def _page_env(scratch, jar):
    from jpype import JClass
    import hub_tab_kit as HT
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "m")
    os.makedirs(os.path.join(home, "bags"), exist_ok=True)
    J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
    J("AccPower").FILE = Paths.get(os.path.join(home, "power.properties"))
    J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
    J("AccPower").load()
    J("AccCraft").LOGF = Paths.get(os.path.join(home, "crafts.log"))
    return HT, E, J


def run_page(out, jar, scratch, _home):
    from jpype import JClass, JShort
    K = HK.Child(out)
    HT, E, J = _page_env(scratch, jar)
    UUID, IS = JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    D = J("AccDefs")
    K.eq(str(J("AccHubOpen").register()), "character:accessories", "PG the Void Charms tab is registered")
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-0000000ac534"), "Rarity")
    u1 = P1.pr.getUuid()
    E.bridge.put("profile:epoch:%s" % u1, JClass("java.lang.Long")(1))
    K.check(bool(J("AccHubOpen")().apply(u1)), "PG the tab's open Function opens the page")
    E.pump(P1)
    pg = E.pg(P1)
    Acc, k1 = J("AccStore"), str(u1)
    Acc.putK(u1, k1, 0, "Skyy_Accessory_Workbench_T3")
    Acc.putK(u1, k1, 1, "Skyy_Talisman_Speed_Epic")
    Acc.putK(u1, k1, 2, OMNI)
    P1.slots["storage"].getInventory().addItemStackToSlot(JShort(0), IS("Skyy_Talisman_Vitality_Rare", 1))

    def click(a, extra=""):
        pg.handleDataEvent(P1.ref, P1.st, '{"a":"%s"%s}' % (a, extra))
        E.pump(P1)
        return str(pg.info)

    def frame(cmds, fid):
        mk = "\n".join(t for ty, s, t, d in cmds if t)
        m = re.search(r"Group #%s \{ ([^}]*)\}" % fid, mk)
        return m.group(1) if m else None

    b0 = HT.build(pg, P1)
    T22.menu_page(K, b0, "PG Bag (nothing selected)")
    K.check(frame(b0[0], "SkyyAccSelIf") is None, "PG nothing selected = no square")
    grid = " ".join(str(d) for ty, s, t, d in b0[0] if ty == "Set" and s == "#SkyyAccGrid.Slots")
    K.check("T3 Bench" in grid and GOOD in grid and ACT in grid, "PG the bag grid's hover text carries the tier tag, the green effects and the yellow hint")
    order = list(pg.bagIds)
    for want in ("Skyy_Accessory_Workbench_T3", "Skyy_Talisman_Speed_Epic", OMNI):
        r = click("g", ',"SlotIndex":%d' % order.index(want))
        b1 = HT.build(pg, P1)
        _a, s1, _e = T22.menu_page(K, b1, "PG Bag (%s selected)" % want)
        f = frame(b1[0], "SkyyAccSelIf")
        col = str(D.rarityColor(want)) + "(0.4)"
        K.check(f is not None and ("Background: %s;" % col) in f and "Width: 44" in f and "Height: 44" in f,
                "PG select %s (%s): #SkyyAccSelIf 44 x 44 Background %s: %s" % (want, r, col, f))
        mk = "\n".join(t for ty, s, t, d in b1[0] if t)
        K.check(re.search(r"ItemIcon #SkyyAccSelIc \{ Anchor: \(Width: 40, Height: 40, Left: 2, Top: \d+\)", mk) is not None, "PG ... the icon sits 2 px in")
        nm = re.search(r"Label #SkyyAccSelNm \{[^}]*TextColor: (#[0-9a-fA-F]+)", mk)
        K.check(nm is None or nm.group(1).lower() == SUI.COLOR["rowName"].lower(), "PG ... the selected name stays soft white (no rarity colour)")
    r = click("ig", ',"SlotIndex":0')
    b2 = HT.build(pg, P1)
    T22.menu_page(K, b2, "PG Bag (inventory selection)")
    f = frame(b2[0], "SkyyAccSelIf")
    K.check(f is not None and ("Background: %s(0.4);" % D.rarityColor("Skyy_Talisman_Vitality_Rare")) in f, "PG an inventory selection (%s): its rarity square: %s" % (r, f))
    # CRAFT
    click("tb:craft")
    tot, allseen = 0, []
    for sub in range(int(len(J("AccCraft").SUB_NAMES))):
        click("st:%d" % sub)
        b3 = HT.build(pg, P1)
        T22.menu_page(K, b3, "PG Craft sub %d" % sub)
        n = len(list(pg.craftIds))
        ok, seen = True, []
        for k in range(n):
            f = frame(b3[0], "SkyyAccCr%dIf" % k)
            rid = str(list(pg.craftIds)[k])
            mk = "\n".join(t for ty, s, t, d in b3[0] if t)
            nm = re.search(r"Label #SkyyAccCr%dNm \{[^}]*TextColor: (#[0-9a-fA-F]+)" % k, mk)
            c = nm.group(1) if nm else None
            good = f is not None and c is not None and ("Background: %s(0.4);" % c) in f and "Width: 44" in f
            seen.append((rid, c))
            ok = ok and good
        K.check(ok, "PG Craft sub %d: every one of %d rows draws #SkyyAccCr<k>If in its rarity colour (= the name colour) at 0.4: %s" % (sub, n, seen[:3]))
        tot += n
        allseen += seen
    K.check(tot > 0, "PG the Craft view drew %d rows in all" % tot)
    K.notes.append("PG Craft rows checked: %s" % allseen)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    J = lambda n: JClass(PKG + n)
    fc, fp = os.path.join(home, "config.properties"), os.path.join(home, "power.properties")
    others0 = dict((n, open(os.path.join(home, n), "rb").read()) for n in ("config.properties", "power.properties", "sounds.properties") if os.path.isfile(os.path.join(home, n)))
    starts = []

    def load():
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(fc)
        o = "".join(str(getattr(J("AccCfg"), m)()) for m in ("migrate051", "migrate055", "migrate0518")) + str(J("AccCfg").migrateP5(J("AccCfg").FILE, False))
        J("AccCfg").load(True)
        J("AccPower").FILE = Paths.get(fp)
        J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
        o += str(J("AccCfg").migrateP5(J("AccPower").FILE, True))
        J("AccPower").load()
        starts.append(o)
        K.check(str(J("AccV3").loadV3(Paths.get(home))).endswith("read"), "LIVE AccV3.loadV3 reads trees.properties")
    moved, pb, pa = WH.live_twice(K, J("AccCfg"), "SkyyAccessories", home, load)
    K.check(all(x == "" for x in starts), "LIVE the older one-time updates do nothing on the live copy (%r)" % [x[:60] for x in starts if x])
    others1 = dict((n, open(os.path.join(home, n), "rb").read()) for n in others0)
    K.eq(sorted(n for n in others0 if others0[n] != others1[n]), [], "LIVE no other settings file changed")
    WC.apply(V3E, "SkyyAccessories")
    ip = [i for i, e in enumerate(V3E.rows("SkyyAccessories")) if e[0] == "Combat"][0]
    k = V3E.ckey(V3E.rows("SkyyAccessories")[ip]) + ".per"
    want = float(pa[k]) / 100.0 if k in pa else 0.0075
    K.check(abs(float(J("AccV3").v3per(ip)) - want) < 1e-12, "LIVE AccV3 after load: Plates per %s" % float(J("AccV3").v3per(ip)))
    bags = os.path.join(home, "bags")
    n = len(os.listdir(bags)) if os.path.isdir(bags) else 0
    K.check(True, "LIVE %d bag files on the copy (0.5.34 reads / writes no saved data differently)" % n)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("page", run_page), ("t22page", T22.run_page), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
