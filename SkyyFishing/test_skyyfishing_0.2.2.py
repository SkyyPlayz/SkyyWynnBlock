"""Harness for SkyyFishing 0.2.2 (rarity + tooltip pass, looks only; tools/fishing_0_2_2_patch.py).
Build first: python tools/fishing_0_2_2_patch.py && python SkyyFishing/build_skyyfishing_0.2.2.py

    python SkyyFishing/test_skyyfishing_0.2.2.py [--keep]

  S       static: the patch re-runs to identical bytes, line endings kept, no class / command / system; jar: no file added or removed, the
          only non-class change is the manifest (no item, lang or asset change)
  A / C / AA  verify (-Xverify:all), class compare 0.2.1 -> 0.2.2 (EXPECT), engine-access audit
  R       EXECUTES: FishDefs.RAR_BG (6 = the RAR_QUALITY hues at 0.4 = every fish item's own Quality frame), qualityBg for every rod / reel /
          part (= its item JSON Quality hue), unknown / null = RBG_NONE; FishRig.fishTip / makeFish: the sectioned lines (rarity word in its
          colour, Zone / Weight / Length name + value colours, Caught by + hint dim, no Caught by when empty), the title colour, the
          metadata document unchanged (v / g / mm / by), fishOf(makeFish json) = "g,mm,by", fishDoc round trip; THE REAL WINDOW
          (FishPage.build on each tab with fish of every rarity, rods, reels, parts I-III, an empty slot): every row icon square #<row>If
          carries the expected colour, the 0.1.9 window checks (check_page, assert_proven, fits, one tab row)
  X210    0.2.1's EXEC phase on this jar (Void catch roll, cast / land)
  L200    0.2.0's LOGIC phase on this jar; its one fish-tooltip text check ("Rare fish from Zone 3 - 30 kg, 160 cm", the 0.2.0 one-line
          body) is superseded by R and recorded as a note, every other check must pass
  LIVE    start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyFishing (0.2.1's live phase: config bytes untouched)
Not testable without the game (UNVERIFIED): how the 40 % squares and the tooltip spans look in the client.
Exit code 1 on any failure.
"""
import os, sys, json, re, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.2.2"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_fishing", "h022")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_cmp0 = HK.run_compare
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_2_1", os.path.join(HERE, "test_skyyfishing_0.2.1.py"))
T210 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T210)
HK.run_compare = _cmp0
T200 = T210.T200
T19 = T200.T19
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.2.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
T200.JAR = JAR
T210.JAR = JAR
if not os.path.isfile(T200.OLD_JAR):          # built jars are git-ignored: a worktree reads the main checkout's 0.1.12 jar (read only)
    _main = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(ROOT))), "SkyyFishing", os.path.basename(T200.OLD_JAR))
    if os.path.basename(os.path.dirname(ROOT)) == "worktrees" and os.path.isfile(_main):
        T200.OLD_JAR = _main
GEN = os.path.join(HERE, "build_skyyfishing_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyfishing_0.2.1.py")
PATCH = os.path.join(ROOT, "tools", "fishing_0_2_2_patch.py")
LIVE_DIR = T200.LIVE_DIR
ADDED = []
VONLY = ["CfgFn", "CfgRows", "FishCfg", "FishCmds"]          # the version text only (run_static checks the bytes)
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "FishCfg": ["~m applyAll", "~m seed"], "FishCmds": ["~m admin"],
    "FishDefs": ["+f QB_BG", "+f QB_IDS", "+f RAR_BG", "+f RBG_NONE", "+m qualityBg", "~<clinit>"],
    "FishRig": ["+m fishTip", "+m tipPair", "~m makeFish"],
    "FishPage": ["~m build"],
    "SkyyFishingPlugin": ["~m setup"],          # the ready line: version + the bench page id (run_static checks the bytes)
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U1S = "00000000-0000-4000-8000-0000000022f2"
RAR_QUALITY = ["Common", "Legendary", "Epic", "Rare", "Epic", "Epic"]
TIP_GOOD, TIP_NAME, TIP_DIM, COL_TEXT = "#7ee08a", "#d6e4ee", "#7f93a6", "#96a9be"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyFishing 0.2.2 - build script') and g.count('VERSION = "0.2.2"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count(' = mk("') - o.count(' = mk("')), (0, 0, 0), "S no class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no file added or removed")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest (lang / items / art identical)")
    for c in VONLY:
        n = "com/skyy/fishing/%s.class" % c
        K.check(za.read(n).replace(b"0.2.1", b"0.2.2") == zb.read(n), "S %s differs only by the version text" % c)
    n = "com/skyy/fishing/SkyyFishingPlugin.class"
    pa, pb = za.read(n), zb.read(n)
    K.check(len(pa) == len(pb) and re.sub(rb"\[SkyyFishing\] 0\.2\.[12] ready|page [0-9a-f]{12}", b"", pa) == re.sub(rb"\[SkyyFishing\] 0\.2\.[12] ready|page [0-9a-f]{12}", b"", pb),
            "S SkyyFishingPlugin differs only by the ready line's version + bench page id")
    lang = zb.read("Server/Languages/en-US/server.lang").decode("utf8")
    fl = [l_ for l_ in lang.splitlines() if l_.startswith("items.SkyyFishing_Fish_") and ".description=" in l_]
    K.check(len(fl) == 27 and all(re.match(r'[^=]+=T\d+ Fish - <color is="#[0-9A-Fa-f]{6}">[A-Za-z]+</color> fish from Zone \d \([A-Za-z ]+\)\. Sell it whole or fillet', l_) for l_ in fl),
            "S the fish lang text keeps the tooltip's order (tag, rarity in colour, zone, then the bench hint): %s" % fl[:1])
    K.save()


def parts_of(msg_json):
    """[(text, colour, bold)] of a Message JSON (its RawText + its Children, in order)"""
    o = []

    def walk(m):
        if not isinstance(m, dict):
            return
        t = m.get("RawText", m.get("rawText"))
        if t is not None:
            o.append((t, m.get("Color", m.get("color")), bool(m.get("Bold", m.get("bold", False)))))
        for c in m.get("Children", m.get("children", [])) or []:
            walk(c)
    walk(msg_json)
    return o


def lines_of(parts):
    """the parts split into lines at the "\\n" parts"""
    ls, cur = [], []
    for p in parts:
        if p[0] == "\n":
            ls.append(cur)
            cur = []
        else:
            cur.append(p)
    ls.append(cur)
    return ls


def run_rar(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    P, mods = T200.setup(K, scratch, "r")
    Defs, Rig, Pg, Eng, Bench = P("FishDefs"), P("FishRig"), P("FishPage"), P("FishEng"), P("FishBench")
    z = zipfile.ZipFile(jar)
    Q = lambda iid, sub: json.loads(z.read("Server/Item/Items/SkyyFishing/%s/%s.json" % (sub, iid)))["Quality"]
    # ---- 1. RAR_BG / RBG_NONE / qualityBg
    rbg = [str(x) for x in Defs.RAR_BG]
    K.eq(rbg, [SUI.QUALITY[q] + "(0.4)" for q in RAR_QUALITY], "R RAR_BG = the 6 RAR_QUALITY hues at 0.4")
    K.eq(str(Defs.RBG_NONE), SUI.COLOR["disabled"] + "(0.15)", "R RBG_NONE = the kit's disabled grey at 0.15")
    fish = [str(x) for x in Defs.FISH]
    bad = [f for i, f in enumerate(fish) if SUI.QUALITY[Q(f, "Fish")] + "(0.4)" != rbg[int(Defs.SP_RAR[i])]]
    K.check(len(fish) == 27 and not bad, "R every fish's row square = its item frame's Quality hue (27 fish): %s" % bad)
    qb = {}
    for iid in [str(x) for x in Defs.RODS]:
        qb[iid] = Q(iid, "Rods")
    for iid in [str(x) for x in Defs.REELS] + [str(x) for x in Defs.PART_IDS]:
        qb[iid] = Q(iid, "Parts")
    badq = [i for i, q in qb.items() if str(Defs.qualityBg(i)) != SUI.QUALITY[q] + "(0.4)"]
    K.check(len(qb) == 8 + 7 + 30 and not badq, "R qualityBg of every rod / reel / part = its item JSON Quality hue (%d): %s" % (len(qb), badq))
    K.eq(sorted(set(qb[str(p)] for p in Defs.PART_IDS)), ["Common", "Rare", "Uncommon"], "R parts I / II / III = Common / Uncommon / Rare")
    K.eq([str(Defs.qualityBg("Ingredient_Stick")), str(Defs.qualityBg(None)), str(Defs.qualityBg(""))], [str(Defs.RBG_NONE)] * 3, "R qualityBg of anything else = RBG_NONE")
    K.eq(sorted(str(x) for x in Defs.R_OUT if str(Defs.qualityBg(x)) == str(Defs.RBG_NONE)), [], "R every Parts tab craft output has a Quality square")
    # ---- 2. the fish tooltip
    sp = dict((str(k), i) for i, k in enumerate(Defs.SP_KEY))
    ex = []
    for key, g, mm, by in (("GlassPike", 30000, 1600, "Skyy"), (str(Defs.SP_KEY[0]), 2410, 523, ""), (str(Defs.SP_KEY[26]), 812, 299, "Tester")):
        s = sp[key]
        r = int(Defs.SP_RAR[s])
        zn = int(Defs.zoneOf(s))
        f = Rig.makeFish(s, g, mm, by)
        mj = json.loads(str(f.getMetadata().toJson()))
        dk = [k for k in mj if k != "SkyyFishing"]
        K.eq(sorted(mj["SkyyFishing"].keys()), ["by", "g", "mm", "v"], "R %s: the metadata document is still v / g / mm / by" % key)
        disp = mj[dk[0]] if dk else {}
        if not ex:
            K.notes.append("R display metadata keys: %s" % sorted(disp.keys()))
        name_k = [k for k in disp if "name" in k.lower()]
        desc_k = [k for k in disp if "desc" in k.lower()]
        title = parts_of(disp[name_k[0]]) if name_k else []
        body = lines_of(parts_of(disp[desc_k[0]])) if desc_k else []
        tag = str(Defs.SP_TAG[s])
        rn, rh = str(Defs.RAR_NAME[r]), str(Defs.RAR_HEX[r])
        want = [[(tag + " - ", COL_TEXT, True), (rn, rh, True), (" fish", str(Defs.COL_VALUE), False)],
                [("Zone: ", TIP_NAME, False), ("%d (%s)" % (zn, str(Defs.ZONE_COLL[zn - 1])), TIP_GOOD, True)],
                [("Weight: ", TIP_NAME, False), (str(P("FishMath").kg(g)), TIP_GOOD, True)],
                [("Length: ", TIP_NAME, False), (str(P("FishMath").cm(mm)), TIP_GOOD, True)]]
        if by:
            want.append([("Caught by: " + by, TIP_DIM, False)])
        want.append([("Sell it or fillet it at a Fishing Bench.", TIP_DIM, False)])
        norm = lambda ls: [[(t, (c or "").lower(), b) for t, c, b in l_ if t != ""] for l_ in ls]
        K.eq(norm(body), norm(want), "R %s: the sectioned tooltip (%d lines, the rarity word in %s)" % (key, len(want), rh))
        K.eq([(t, (c or "").lower()) for t, c, _b in title if t], [(str(Defs.SP_NAME[s]), rh.lower())], "R %s: the title = the name in its rarity colour" % key)
        K.eq(str(Rig.fishOf(fish[s], str(f.getMetadata().toJson()))), "%d,%d,%s" % (g, mm, by), "R %s: fishOf(makeFish json) = g,mm,by" % key)
        K.eq(str(Rig.fishDoc(fish[s], "%d,%d,%s" % (g, mm, by))), str(f.getMetadata().toJson()), "R %s: fishDoc rebuilds the same metadata" % key)
        # fishTip itself (wrapped in a display document the same way) = the body makeFish carries
        IDM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata")
        MSG = JClass("com.hypixel.hytale.server.core.Message")
        tj = json.loads(str(JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("Rock_Stone", 1).withMetadata(IDM.KEYED_CODEC, IDM(MSG.raw("t"), Rig.fishTip(s, g, mm, by))).getMetadata().toJson()))
        td = tj[dk[0]] if dk and dk[0] in tj else {}
        K.eq(norm(lines_of(parts_of(td.get(desc_k[0], {}) if desc_k else {}))), norm(want), "R %s: fishTip returns the %d lines directly" % (key, len(want)))
        ex.append(key)
    # ---- 3. THE REAL WINDOW: the row icon squares carry the expected colours
    IS, SIC, SH, UUID = (JClass("com.hypixel.hytale.server.core.inventory.ItemStack"), JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"),
                         JClass("java.lang.Short"), JClass("java.util.UUID"))
    u = UUID.fromString(U1S)
    W = {"inv": SIC(SH(36).shortValue()), "t": 1000000}
    Eng.API = T19._api(W)
    inv = W["inv"]
    rar = [int(x) for x in Defs.SP_RAR]
    for rr in range(6):
        cand = [i for i in range(len(rar)) if rar[i] == rr]
        if cand:
            inv.addItemStack(Rig.makeFish(cand[0], 2000 + rr, 450, "Skyy"))
    rod = Rig.withRig(IS("SkyyFishing_Rod_Thorium", 1), ["4", "SkyyFishing_Hook_Barbed_III", "", ""])
    inv.addItemStack(rod)
    for iid in ("SkyyFishing_Hook_Barbed_I", "SkyyFishing_Line_Braided_II", "SkyyFishing_Sinker_Weighted_III", "SkyyFishing_Reel_Cobalt"):
        inv.addItemStack(IS(iid, 1))
    FPT = T19.fake_page_class()
    pg = FPT(T19.player_ref(u))
    H = T19.H

    def squares(cmds):
        o = {}
        for ty, s, t, d in cmds:
            for mm_ in re.finditer(r"Group #(SkyyFb[A-Za-z]+\d+)If \{[^{}]*Background: ([^;]+);", t or ""):
                o[mm_.group(1)] = mm_.group(2).strip()
        return o

    def icons(cmds):
        o = {}
        for ty, s, t, d in cmds:
            for mm_ in re.finditer(r'ItemIcon #(SkyyFb[A-Za-z]+\d+)Ic \{[^{}]*ItemId: "([^"]+)"', t or ""):
                o[mm_.group(1)] = mm_.group(2)
        return o
    win = []
    for tab in (0, 1, 2):
        pg.tab = tab
        pg.rebuild()
        cmds = H.cmds_of(pg.lastB)
        win.append(("tab %d" % tab, cmds, H.events_of(pg.lastEv), str(pg.info)))
        sq, ic = squares(cmds), icons(cmds)
        K.check(len(sq) > 0 and sorted(sq) == sorted(ic), "R tab %d: every row icon has its square (%d squares, %d icons)" % (tab, len(sq), len(ic)))
        wrong = []
        for row, iid in ic.items():
            if row.startswith("SkyyFbF"):
                want_c = rbg[rar[fish.index(iid)]]
            elif row.startswith("SkyyFbK") and int(row[7:]) >= 0 and iid in ("SkyyFishing_Reel_Bamboo", "SkyyFishing_Hook_Barbed_I", "SkyyFishing_Line_Braided_I", "SkyyFishing_Sinker_Weighted_I") \
                    and not (int(row[7:]) == 1 and iid == "SkyyFishing_Hook_Barbed_I"):
                want_c = str(Defs.RBG_NONE)          # an empty slot (the placeholder icon)
            else:
                want_c = str(Defs.qualityBg(iid))
            if sq.get(row) != want_c:
                wrong.append((row, iid, sq.get(row), want_c))
        K.check(not wrong, "R tab %d: each square = the item's hue (fish RAR_BG, rods / reels / parts qualityBg, empty slot RBG_NONE): %s" % (tab, wrong[:4]))
        if tab == 1:
            K.check(any(r_.startswith("SkyyFbK") and v == str(Defs.RBG_NONE) for r_, v in sq.items()), "R Rig tab: an empty slot shows the faint grey")
            K.check(any(r_.startswith("SkyyFbP") and v == SUI.QUALITY["Rare"] + "(0.4)" for r_, v in sq.items())
                    and any(r_.startswith("SkyyFbP") and v == SUI.QUALITY["Common"] + "(0.4)" for r_, v in sq.items())
                    and any(r_.startswith("SkyyFbP") and v == SUI.QUALITY["Uncommon"] + "(0.4)" for r_, v in sq.items()), "R Rig tab: parts I / II / III squares Common / Uncommon / Rare")
            K.check(sq.get("SkyyFbK0") == SUI.QUALITY[qb["SkyyFishing_Reel_Thorium"]] + "(0.4)" and sq.get("SkyyFbK1") == SUI.QUALITY["Rare"] + "(0.4)", "R Rig tab: the fitted Thorium reel + Barbed Hook III squares: %s" % sq)
        if tab == 2:
            K.eq(sorted(set(sq.values())), sorted(set(rbg[rr] for rr in range(6) if rr in rar)), "R Fillet and Sell: one square per rarity hue")
        K.notes.append("R tab %d squares: %s" % (tab, sorted(sq.items())[:12]))
    T19.window_checks(K, win, [int(x) for x in Pg.RHS])
    Eng.API = None
    P("FishStore").stopIO()
    K.save()


def run_l200(out, jar, scratch, home):
    """0.2.0's logic phase; its one 0.2.0 fish-tooltip-text check is superseded by R (noted, not failed)"""
    sup = "H10 the fish tooltip starts with its tag"
    _chk = HK.Child.check

    def check(self, cond, what):
        if not cond and str(what).startswith(sup):
            self.notes.append("superseded by 0.2.2 fishTip (R checks the new sections): %s" % what)
            return True
        return _chk(self, cond, what)
    HK.Child.check = check
    T200.run_logic(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("rar", run_rar), ("x210", T210.run_exec), ("l200", run_l200), ("live", T210.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyFishing"))
