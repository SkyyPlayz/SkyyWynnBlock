"""Harness for SkyyShards 0.4.32 (Hytale-look clicker art - tools/shards_0_4_32_patch.py, on top of 0.4.31).
Build first:
    python tools/shards_0_4_32_patch.py && python SkyyShards/build_skyyshards_0.4.32.py
    python SkyyShards/test_skyyshards_0.4.32.py [--keep] [--only label,label] [--dir <scratch>] [--sheet <folder>]

  S32  static   the patch re-runs to identical bytes; header / VERSION / ready line / rollback note; no new registerSystem / registerCommand; line
                endings kept; the renderer has no clock / randomness
  P32  pictures every Clk picture the jar's classes / data name exists in the jar (path or @2x) and decodes, none blank; the zone islands (15, their
                sizes), the per-role monster cards (= the distinct T_ROLE), the 1x spot (110 x 140) + map card (210 x 140) sizes, the totems; the
                retired Isl / QIsl / TIsl / Totem / Spirit gone; NO PNG of the jar is a file in git (byte compare against every tracked .png);
                re-rendered in this process from the generated script's CLK_HY_SRC = the jar's bytes (a zone island + a monster card + a tree)
  G32  page     EXECUTED for all 6 shards x 5 zones x 3 sizes: the page shows the zone's base island (ClkZIsl<zone><size>), Mining its quarry
                terraces, Combat its houses + tower, the shard's own totem (Root / Ember / Thunder), its spot pictures; nothing retired; every picture
                the markup names is in the jar; the page walks clean; T_PIC = the row's role card. Writes the review sheet (--sheet) of the real pages
  then 0.4.31's phases (minus static / livemig31) on THIS jar, A verify, C compare, AA audit, live32 = 0.4.31's start-twice on a scratch copy of the
                live data (unchanged rules: this round changes no saved data)
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, struct, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.32"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "clkart1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.31.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.31.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_32_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
SHEET = os.path.abspath(HK.arg("--sheet")) if "--sheet" in sys.argv else os.path.join(ROOT, "tools", "dev", "scratch", "clkart1", "review")
PKG = "com.skyy.shards."
MAPP = "Common/UI/Custom/SkyyShards/Map/"

# the 0.4.31 harness (it loads 0.4.30 -> ... older): its version moves to this one in memory
_T31 = open(os.path.join(HERE, "test_skyyshards_0.4.31.py"), encoding="utf8").read()
assert _T31.count('VERSION = "0.4.31"\n') == 1, "the 0.4.31 harness changed"
_T31 = _T31.replace('VERSION = "0.4.31"\n', 'VERSION = "%s"\n' % VERSION)
_argv = list(sys.argv)
T431 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_31", loader=None))
T431.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.31.py")
exec(compile(_T31, T431.__file__, "exec"), T431.__dict__)
sys.argv[:] = _argv
T430, T429, T428, T427 = T431.T430, T431.T429, T431.T428, T431.T427
T426, T425, T424, T423, T410, T49 = T431.T426, T431.T425, T431.T424, T431.T423, T431.T410, T431.T49
for _m in (T431, T430, T429, T428):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
OWNER = T428.OWNER
T0 = T428.T0
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
KN = ["mining", "foraging", "farming", "ranching", "orchard", "combat"]
TOT = {MI: "TotemEmber", CK: "TotemThunder"}
RETIRED_PICS = ("Isl1", "Isl2", "Isl3", "QIsl1", "QIsl2", "QIsl3", "TIsl1", "TIsl2", "TIsl3", "Totem", "Spirit")


def _hy():
    """the generated script's renderer (exec'd here, as the build does)"""
    g = open(GEN, encoding="utf8").read()
    a = g.index("CLK_HY_SRC = r'''") + len("CLK_HY_SRC = r'''")
    ns = {}
    exec(compile(g[a:g.index("'''", a)], "clkhy", "exec"), ns)
    return ns


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.32 - build script') and 'VERSION = "0.4.32"\n' in g, "S32 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S32 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.32:" in g, "S32 the ready line names the round")
    K.check("ROLLBACK 0.4.32 -> 0.4.31 alone" in g and "SAVED DATA: none" in g, "S32 the rollback + saved-data notes")
    hs = g[g.index("CLK_HY_SRC = r'''"):]
    hs = hs[:hs.index("'''", 20)]
    K.check(not any(w in hs for w in ("import random", "import time", "time.time", "datetime", "os.urandom", "hash(")), "S32 the renderer has no clock / randomness / salted hash")
    K.check("SA.assets()" in g and "_hy_zf.close()" in g and "open(" not in hs, "S32 Assets.zip is opened read only (skyyart.assets) and closed; the renderer writes no file")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S32 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S32 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S32 jar newer than the script, the script newer than the patch")
    K.save()


def _git_pngs():
    """every tracked .png of the repo: {sha256: path}"""
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "-z", "--", "*.png"], capture_output=True)
    out = {}
    for p in r.stdout.decode("utf8", "replace").split("\0"):
        if p and os.path.isfile(os.path.join(ROOT, p)):
            out[hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()] = p
    return out


def run_pictures(out, jar, scratch, _home):
    import skyyart as SA
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    refs = set()
    for n in names:
        if n.endswith(".class") or (n.startswith("com/skyy/shards/map/") and not n.endswith(".png")):
            refs |= set(m.decode("ascii") for m in re.findall(rb"SkyyShards/Map/[A-Za-z0-9/]+\.png", z.read(n)))
    clk = sorted(r for r in refs if "/Clk" in r)
    missing, bad, blank = [], [], []
    for r in sorted(refs):
        p = "Common/UI/Custom/" + r
        cand = [c for c in (p, p[:-4] + "@2x.png") if c in names]
        if not cand:
            missing.append(r)
            continue
        for c in cand:
            try:
                im = SA.png_decode(z.read(c))
            except Exception as e:   # noqa
                bad.append("%s %s" % (c, e))
                continue
            if not any(im.px[3::4]):
                blank.append(c)
    with zipfile.ZipFile(OLD_JAR) as zo:   # the old menu's Map tab bases (dropped in 0.4.27, the menu never opens) are named but absent since 0.4.27
        on = set(zo.namelist())
        old_missing = set(r for r in missing if "Common/UI/Custom/" + r not in on and "Common/UI/Custom/" + r[:-4] + "@2x.png" not in on)
    K.check(not [r for r in missing if "/Clk" in r] and set(missing) <= old_missing and not bad and not blank and len(clk) >= 200,
            "P32 every clicker picture the classes / page data name is in the jar, decodes, not blank (%d named, %d clicker; missing %s = 0.4.31's too) bad %s blank %s"
            % (len(refs), len(clk), sorted(missing)[:6], bad[:3], blank[:5]))
    size = {}
    for n in names:
        if n.startswith(MAPP + "Clk") and n.endswith(".png"):
            size[n[len(MAPP) + 3:-4]] = struct.unpack(">II", z.read(n)[16:24])
    K.check(not any(k.endswith("@2x") and k[:-3] in size for k in size), "P32 no picture ships twice (1x + @2x)")
    isl = dict((k, v) for k, v in size.items() if re.fullmatch(r"ZIsl[1-5][1-3]", k))
    K.check(len(isl) == 15 and all(v == {"1": (520, 300), "2": (700, 400), "3": (880, 500)}[k[-1]] for k, v in isl.items()), "P32 15 zone islands at their drawn sizes: %s" % sorted(isl.items())[:3])
    spot = dict((k, v) for k, v in size.items() if re.fullmatch(r"(Tree|Stump|QNode|QRub|FCrop|TMon|RAni|OTree|OPick)\d+|FHarv|TSlain|RRest", k))
    nmon = len([k for k in spot if k.startswith("TMon")])
    K.check(len(spot) - nmon == 15 + 15 + 11 + 11 + 15 + 8 + 8 + 8 + 3 and nmon >= 40 and all(v == (110, 140) for v in spot.values()),
            "P32 the spot pictures are 1x 110 x 140 (%d, %d monster cards)" % (len(spot), nmon))
    cards = dict((k, v) for k, v in size.items() if re.fullmatch(r"(Map|FMap|QMap|TMap)\d+", k))
    K.check(len(cards) == 46 and all(v == (210, 140) for v in cards.values()), "P32 the 46 map cards are 1x 210 x 140")
    K.check(all(size.get(k) == (64, 128) for k in ("TotemRoot", "TotemEmber", "TotemThunder")) and size.get("Weather") == (34, 73)
            and all(k in size for k in ("QTerr1", "QTerr2", "QTerr3", "THouse", "TTower")), "P32 the totems (64 x 128, fix3), the weather totem, the quarry terraces, the town parts")
    # fix3: the spirit fills the top of the totem picture (not a blob): opaque pixels in the top 40% of each totem
    for k in ("TotemRoot", "TotemEmber", "TotemThunder"):
        im = SA.png_decode(z.read(MAPP + "Clk%s.png" % k))
        top = sum(1 for y in range(int(im.h * 0.4)) if any(im.px[(y * im.w + x) * 4 + 3] > 128 for x in range(im.w)))
        K.check(top >= int(im.h * 0.4) * 0.8, "FX3 %s: the spirit fills the top of the picture (%d of the top %d rows drawn)" % (k, top, int(im.h * 0.4)))
    # fix1: the Zone 5 islands glow (lava cracks + pools on the top), the other zones do not
    def _lava(n):
        im = SA.png_decode(z.read(MAPP + "Clk%s.png" % n))
        return sum(1 for i in range(0, len(im.px), 4) if im.px[i + 3] > 200 and im.px[i] > 200 and 50 < im.px[i + 1] < 190 and im.px[i + 2] < 90)
    lv = dict(("ZIsl%d%d" % (zz, s2), _lava("ZIsl%d%d" % (zz, s2))) for zz in (1, 4, 5) for s2 in (1, 2, 3))
    K.check(all(lv["ZIsl5%d" % s2] > 800 and lv["ZIsl5%d" % s2] > 20 * max(1, lv["ZIsl4%d" % s2]) for s2 in (1, 2, 3)),
            "FX1 Zone 5 islands show glowing lava (bright orange px per size vs Zone 4 / Zone 1): %s" % sorted(lv.items()))
    # fix2: every monster card has a light rim (light pixels on its soft outline) so it reads on dark ground
    def _rimmed(n):
        im = SA.png_decode(z.read(n))
        w, h, px = im.w, im.h, im.px
        edge = light = 0
        for y in range(1, h - 16):
            for x in range(1, w - 1):
                i = (y * w + x) * 4
                if px[i + 3] < 60 or px[i + 3] > 220:
                    continue
                edge += 1
                if px[i] > 200 and px[i + 1] > 190 and px[i + 2] > 160:
                    light += 1
        return edge > 0 and light > edge * 0.5, (edge, light)
    mons = sorted(n for n in names if n.startswith(MAPP + "ClkTMon") and n.endswith(".png"))
    rr_ = [(n, _rimmed(n)) for n in mons]
    norim = [(n[len(MAPP):], v[1]) for n, v in rr_ if not v[0]]
    K.check(len(mons) >= 40 and not norim, "FX2 every monster card (%d) has the light rim: without %s" % (len(mons), norim[:4]))
    K.check(not any(k in size or (k + "@2x") in size for k in RETIRED_PICS) and not any(("/Clk%s.png" % k) in r for k in RETIRED_PICS for r in refs),
            "P32 the retired Isl / QIsl / TIsl / Totem / Spirit pictures are gone and named nowhere")
    gp = _git_pngs()
    inj = [n for n in names if n.endswith(".png") and hashlib.sha256(z.read(n)).hexdigest() in gp]
    K.check(len(gp) > 10 and not [n for n in inj if n.startswith(MAPP + "Clk")], "P32 no clicker picture of the jar is a file in git (%d tracked PNGs compared): %s" % (len(gp), inj[:4]))
    K.notes.append("P32 jar PNGs equal to a tracked file (not clicker art; the kit / portal art made by older rounds): %s" % ", ".join(inj[:20]))
    total = sum(w * h for k, (w, h) in size.items())
    K.notes.append("P32 clicker pictures: %d files, %.2f Mpx" % (len(size), total / 1e6))
    # determinism: the generated renderer, run again here, gives the jar's bytes
    ns = _hy()
    S = ns["Src"](SA.assets(), SA.png_decode)
    big = ns["Vox"](ns["A1"] * ns["SS"], ns["B1"] * ns["SS"], ns["H1"] * ns["SS"])
    zi, _ = ns["zone_island"](S, big, 3, 520, 300, 31)
    K.check(zi.png() == z.read(MAPP + "ClkZIsl31.png"), "P32 re-rendered Zone 3 Small island = the jar's bytes (deterministic)")
    small = ns["Vox"](9 * ns["SS"], 9 * ns["SS"] // 2, 9 * ns["SS"], bevel=("log",))
    K.check(ns["tree_pic"](S, small, "Oak", 21, []).png() == z.read(MAPP + "ClkTree1.png"), "P32 re-rendered Tree1 (Oak) = the jar's bytes")
    K.check(ns["card"](ns["crop_alpha"](S.model("Rat")), 110, 140, mh=124, lit=True).png() in [z.read(n) for n in names if n.startswith(MAPP + "ClkTMon")],
            "P32 re-rendered Rat card = one of the jar's monster cards")
    K.save()


_GRX = re.compile(r'Group #(\w+) \{ Anchor: \(Left: (-?\d+), Top: (-?\d+), Width: (\d+), Height: (\d+)\); Background: "(SkyyShards/Map/[A-Za-z0-9/]+\.png)"; \}')


def _compose(ns, SA, z, mk):
    """the scene of a built page, drawn from its markup (the island scene's pictures in markup order) with the jar's pictures"""
    W, H = 1000, 600
    sc = ns["Pic"](W, H)
    for y in range(H):
        t = y / float(H)
        c = bytes((int(79 + 135 * t), int(159 + 78 * t), int(234 + 21 * t), 255))
        sc.px[y * W * 4:(y + 1) * W * 4] = c * W
    cache = {}
    for (ident, l, t, w, h, tex) in _GRX.findall(mk):
        if not tex.split("/")[-1].startswith("Clk") or tex.endswith("ClkSky.png"):
            continue
        p = "Common/UI/Custom/" + tex
        if p not in cache:
            data = z.read(p) if p in z.namelist() else z.read(p[:-4] + "@2x.png")
            cache[p] = ns["of_img"](SA.png_decode(data))
        im = cache[p]
        w, h = int(w), int(h)
        if (im.w, im.h) != (w, h):
            im = ns["resize"](im, w, h)
        sc.paste(im, int(l), int(t))
    return sc


def _set_one(L, p, kd, ty, sz):
    St = L["ShStore"]
    if kd == FO:
        T423._foraging(L, p, size=sz, amt=5, irr=5, deco=5)
    elif kd == MI:
        T424._mining(L, p, size=sz, irr=5, deco=5, iron=False)
    elif kd == FK:
        T425._farm(L, p, size=sz, irr=5, deco=5)
    elif kd == CK:
        T426._town(L, p, size=sz, amt=5)
    else:
        T428._isl(L, p, KN[kd], [(0, ty, sz)], irr=5, deco=5)
    St.LOCK.lock()
    try:
        p.setProperty("%s.i0.type" % KN[kd], ty)
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def run_page(out, jar, scratch, _home):
    import skyyart as SA
    K = HK.Child(out)
    L, ou, W_, p, lv, got = T431._env(scratch, K, "g32")
    for k_ in ("Ranching", "Orchard", "Mining", "Foraging", "Farming"):
        lv[k_] = 100
    Isl, Ck, Cmb, Page = L["ShIsl"], L["ShClk"], L["ShCombat"], L["ShPage"]
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    roles = [str(r) for r in Ck.T_ROLE]
    rr = sorted(set(roles))
    tm = [str(x) for x in Page.T_MON]
    K.check(len(tm) == len(rr) and all(tm[int(Ck.T_PIC[i])].endswith("ClkTMon%d.png" % rr.index(roles[i])) for i in range(len(roles))),
            "P32 T_PIC = each town row's own role card (%d rows, %d roles)" % (len(roles), len(rr)))
    ns = _hy()
    os.makedirs(SHEET, exist_ok=True)
    shots = []
    seen = 0
    for kd in (FO, MI, FK, RA, OR, CK):
        L0, LN = int(Isl.LAD0[kd]), int(Isl.LADN[kd])
        for zone in range(1, 6):
            if kd == CK:
                ty = L0 + zone - 1
            else:
                tys = [L0 + i for i in range(LN) if int(Isl.zoneOf(L0 + i)) == zone]
                if not tys:
                    continue
                ty = tys[0]
            key = str(Isl.KEY[ty])
            for sz in (1, 2, 3):
                _set_one(L, p, kd, key, sz)
                pg = T427._page(L, ou, W_, kd)
                bd = T49._build(pg)
                mk = bd["mk"]
                seen += 1
                tex = set(re.findall(r'"(SkyyShards/Map/[A-Za-z0-9/]+\.png)"', mk)) | set(str(x) for x in (pg.ckTexA or []) if x is not None)
                miss = [t for t in tex if "Common/UI/Custom/" + t not in names and "Common/UI/Custom/" + t[:-4] + "@2x.png" not in names]
                want = ["ClkZIsl%d%d.png" % (zone, sz), "Clk%s.png" % TOT.get(kd, "TotemRoot")] + (["ClkQTerr%d.png" % sz] if kd == MI else []) + \
                       (["ClkTHouse.png", "ClkTTower.png"] if kd == CK else [])
                other = [t for t in ("ClkZIsl%d%d.png" % (z2, s2) for z2 in range(1, 6) for s2 in (1, 2, 3)) if t != want[0] and t in mk]
                wrong_tot = [t for t in ("ClkTotemRoot.png", "ClkTotemEmber.png", "ClkTotemThunder.png") if t != want[1] and t in mk]
                spot = {FO: "ClkTree", MI: "ClkQNode", FK: "ClkFCrop", RA: "ClkRAni", OR: "ClkOTree", CK: "ClkTMon"}[kd]
                r_ = T410.full(pg)
                extra_ok = ("#SkyyShKWx" not in mk and "#SkyyShKD4" not in mk) if kd == CK else ("#SkyyShKWx" in mk and "#SkyyShKD4" in mk and "#SkyyShKTo0" in mk)
                tos = [(int(t_), int(i_)) for i_, t_ in re.findall(r"#SkyyShKTo(\d) \{ Anchor: \(Left: -?\d+, Top: (-?\d+)", mk)]
                if kd != CK:   # fix3: the totems are drawn back to front (a lower Top first)
                    extra_ok = extra_ok and len(tos) >= 1 and tos == sorted(tos) and len(tos) == len(set(i_ for t_, i_ in tos))
                ok = (extra_ok and all(w in mk for w in want) and not other and not wrong_tot and not miss and spot in mk and int(pg.ckSz) == sz
                      and not any(("/Clk%s.png" % k) in mk for k in RETIRED_PICS) and not r_["miss"] and not r_["unbound"])
                K.check(ok, "G32 %s Zone %d size %d: the zone island, %s, the %s totem, the spot pictures, walks clean (want %s, other %s, totem %s, missing %s, %s)"
                        % (KN[kd], zone, sz, "terraces" if kd == MI else ("town" if kd == CK else "no overlay"), want[1][3:-4], [w for w in want if w not in mk], other, wrong_tot, miss[:3], r_["miss"][:2]))
                if sz == 2 or (sz == 3 and zone in (1, 5)):
                    shots.append(("%s Z%d S%d" % (KN[kd], zone, sz), _compose(ns, SA, z, mk)))
    K.check(seen == 3 * (5 + 5 + 5 + 3 + 3 + 5), "G32 every shard x zone x size page built (%d)" % seen)
    # the review sheet: the real pages' island scenes at half size, 4 a row
    Pic = ns["Pic"]
    cw, ch = 500, 300
    cols = 4
    sheet = Pic(cols * cw, ((len(shots) + cols - 1) // cols) * ch, (30, 34, 44, 255))
    for i, (lab, sc) in enumerate(shots):
        sheet.paste(ns["down2"](sc), (i % cols) * cw, (i // cols) * ch)
    open(os.path.join(SHEET, "scenes.png"), "wb").write(sheet.png())
    allp = sorted(n for n in names if n.startswith(MAPP + "Clk") and n.endswith(".png"))
    cw, ch, cols = 120, 150, 18
    sh2 = Pic(cols * cw, ((len(allp) + cols - 1) // cols) * ch, (60, 70, 92, 255))
    for i, n in enumerate(allp):
        im = ns["of_img"](SA.png_decode(z.read(n)))
        im = ns["fit"](im, cw - 4, ch - 4)
        sh2.paste(im, (i % cols) * cw + 2, (i // cols) * ch + 2)
    open(os.path.join(SHEET, "pictures.png"), "wb").write(sh2.png())
    K.notes.append("G32 review sheet: %s (%d scenes) + %s (%d pictures)" % (os.path.join(SHEET, "scenes.png"), len(shots), os.path.join(SHEET, "pictures.png"), len(allp)))
    K.save()


def _compare32(out, jar, old_jar, pkg, expect, added, removed=()):
    """non-class files: only the clicker pictures (Common/UI/Custom/SkyyShards/Map/Clk*.png) + manifest.json change; then the class compare"""
    rx = re.compile(r"^Common/UI/Custom/SkyyShards/Map/Clk[A-Za-z0-9]+(@2x)?\.png$")
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
        new = sorted(n for n in na - nb if not n.endswith(".class"))
        gone = sorted(n for n in nb - na if not n.endswith(".class"))
        chg = sorted(n for n in na & nb if not n.endswith(".class") and a.read(n) != b.read(n))
        assert all(rx.match(n) for n in new + gone) and all(rx.match(n) or n == "manifest.json" for n in chg),             "C non-class files other than the clicker pictures: %s / %s / %s" % ([n for n in new if not rx.match(n)][:5], [n for n in gone if not rx.match(n)][:5],
                                                                                   [n for n in chg if not rx.match(n) and n != "manifest.json"][:5])
    print("C. non-class files: only clicker pictures (%d new, %d gone, %d changed) + manifest.json" % (len(new), len(gone), len(chg)))
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    os.makedirs(SCRATCH, exist_ok=True)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(old_jar) as zo0, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if n.endswith(".class") or n == "manifest.json":
                zo.writestr(n, zi.read(n))
        for n in zo0.namelist():
            if not n.endswith(".class") and n != "manifest.json":
                zo.writestr(n, zo0.read(n))
    T431.T419._compare(out, cp, old_jar, pkg, expect, added, removed)


EXPECT = {   # 0.4.31 -> 0.4.32: the art round touches only the page (zone base / overlays / totems) + the per-role T_PIC; the rest = the @VERSION@ string
    'SkyyShardsPlugin': ['~m setup'], 'ShClk': ['~<clinit>'], 'ShPage': ['~<clinit>', '~m buildClick'],
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'], 'ShFill': ['~m markFixed'],
    'ShStore': ['~m migrate', '~m migrate2', '~m migrate3', '~m migrate4', '~m migrate5', '~m migrate6', '~m save'],
}

# 0.4.2x phases that pin the OLD drawings (picture names / counts / @2x, the island picture per kind) - replaced on purpose by this round's SPEC (P32 / G32
# check the new pictures). A failing check whose text matches is counted as a note "retired ..." instead.
T427.RETIRED += [
    (r"^PG23 \.\.\. the island picture, the 5 decorations, the weather totem, a spirit totem", "SPEC 1/4: ClkIsl<size> is retired - the zone island ClkZIsl<zone><size> + the shard's own totem (G32 checks them + the decorations / weather totem)"),
    (r"^MP \.\.\. the quarry picture, Copper \+ Iron nodes, the springs", "SPEC 1/2: ClkQIsl<size> is retired - the zone island + the quarry terraces ClkQTerr<size> (G32, with the springs)"),
    (r"^FP \.\.\. the Wheat plots, the island, the rain totem \(Irrigation\), the decorations", "SPEC 1: ClkIsl<size> is retired - the zone island (G32 checks it + the rain totem + the decorations)"),
    (r"^TP \.\.\. the monsters, the town island, the spirit warriors \(totems\), no weather totem / decorations", "SPEC 1/2: ClkTIsl<size> is retired - the zone island + THouse / TTower (G32, no weather totem / decorations)"),
]

PHASES = [("static", run_static), ("pictures32", run_pictures), ("page32", run_page)] + \
         [x for x in T431.PHASES if x[0] not in ("static", "livemig31")] + [("livemig32", T431.run_live)]


if __name__ == "__main__":
    HK.run_compare = _compare32
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=ph, script=__file__, live=(T431.T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
