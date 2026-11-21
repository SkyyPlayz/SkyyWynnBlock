"""SkyyHud 0.3.39 harness - HUD v5: the pet card left of the hotbar, the NEW Mount card right of it (tools/hud_0_3_39_patch.py; data =
SkyyPets 0.4.27's pets:fn:hud). Built on tools/harness_kit.py and on 0.3.38's harness (its P38 model / markup / HUD phase and its E2E run
again on this jar, unchanged: the Pets widget code underneath is 0.3.38's).

    python SkyyHud/test_skyyhud_0.3.39.py [--jar SkyyHud-0.3.39.jar] [--pets SkyyPets/SkyyPets-0.4.27.jar] [--dir <scratch>] [--keep]

  A / C / AA  verify (-Xverify:all), compare 0.3.38 -> 0.3.39, the engine-access audit
  S     static   the patch re-generates 0.3.39 byte for byte; no system / command added
  P38   0.3.38's phase on this jar (petsModelOf / markup / a real HUD with the block moving cards)
  P39   EXECUTED: the ids + built-in spots; one card per widget (pet slot / mount slot of ONE answer, the old 0.4.26 line shape too, an empty
        slot hides only its card); the Mount markup (every fill key, nothing below the box); a real HUD build + fill: Pets draws F0 only,
        Mount F1 only, a health tick = values only, a mount change = a re-send, the mount slot emptied = the Mount card gone; the stand-ins
        (with / without SkyyPets); FIRST SPOT (cardPlace) for a new player + a crowded layout; THE ONE-TIME MOVE: an old-spot Pets line moves
        once (verified history copy, the file untouched, scale / style kept), a second load after a save never moves again, hand-moved kept,
        Pets OFF -> Mount OFF, a file with a Mount line never moves, no history copy = no move, an older different copy = a stamped sibling;
        the server default code + /skyyhud import of an old code follow the same rule
  E2E   0.3.38's: the REAL SkyyPets 0.4.27 jar + this jar in one JVM
  LIVE  twice on a scratch COPY of the live Skyy_SkyyHud: nothing written, every saved line loads as saved, where the two cards land
Not testable without the game (UNVERIFIED): the look on the real HUD, the real hotbar / chat / pickup sizes (Layout-Spec estimates).
Scratch: tools/dev/scratch/hud5/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "hud5", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyHud-0.3.39.jar")]
if "--pets" not in sys.argv:
    sys.argv += ["--pets", os.path.join(ROOT, "SkyyPets", "SkyyPets-0.4.27.jar")]
import harness_kit as HK
import skyybuild as B

_s = importlib.util.spec_from_file_location("test_skyyhud_0_3_38", os.path.join(HERE, "test_skyyhud_0.3.38.py"))
T338 = importlib.util.module_from_spec(_s)
_a = list(sys.argv)
_s.loader.exec_module(T338)
sys.argv[:] = _a
T337 = T338.T337

VERSION, PREV = "0.3.39", "0.3.38"
JAR, PETS, SCRATCH = T337.JAR, T337.PETS, T337.SCRATCH
OLD = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
PKG = T337.PKG
GEN, GEN_OLD = os.path.join(HERE, "build_skyyhud_%s.py" % VERSION), os.path.join(HERE, "build_skyyhud_%s.py" % PREV)
WOLF, FIRE, PFIRE, HORSE = T337.WOLF, T337.FIRE, T338.PFIRE, T338.HORSE
OLD_PETS = "1,br,460,210,100,0"          # the 0.3.37 / 0.3.38 built-in Pets line (Background OFF)


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.3.39"') == 1 and g.count("registerSystem(") == o.count("registerSystem(") and g.count("registerCommand(") == o.count("registerCommand("),
            "S VERSION; no system / command added")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, os.path.basename(GEN))
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "hud_0_3_39_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S hud_0_3_39_patch.py re-generates its script byte for byte: %s" % p.stderr[-300:])
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.save()


def _file(work, u, lines):
    """a layout file the way LayoutStore.save writes one (java.util.Properties: header, date, key=value)"""
    p = os.path.join(work, "layouts", str(u) + ".properties")
    with open(p, "wb") as f:
        f.write(("#SkyyHud layout\n#Sat Nov 21 10:00:00 MST 2026\n" + "".join("%s=%s\n" % kv for kv in lines)).encode("latin-1"))
    return p


def run_p39(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JProxy
    S = T337._setup(out, scratch, [B.SERVER_JAR, jar, B.JAVASSIST], "k39")
    K, H, bridge, pr, u, work = S["K"], S["H"], S["bridge"], S["pr"], S["u"], S["work"]
    Wid, LS, HM, Cfg = H("Widgets"), H("LayoutStore"), H("HudMain"), H("HudCfg")
    UUID = JClass("java.util.UUID")
    SA = lambda xs: JArray(JString)(xs)
    L_ = lambda m: [None if x is None else str(x) for x in m]
    ids = [str(x) for x in Wid.IDS]

    # ---- ids, labels, built-in spots
    K.check(ids[-2:] == ["Pets", "Mount"] and str(Wid.label("Mount")) == "Mount" and bool(Wid.multi("Mount")), "P39 Mount APPENDED to IDS, label 'Mount', a multi-line widget: %s" % ids[-3:])
    dp, dm = Wid.def_("Pets") if hasattr(Wid, "def_") else Wid.start("Pets"), Wid.start("Mount")
    K.check((bool(dp.en), str(dp.anchor), int(dp.dx), int(dp.dy), int(dp.bw), int(dp.bh), bool(dp.bg)) == (True, "b", -483, 8, 230, 88, False),
            "P39 built-in pet card: ON, b -483,8, 230 x 88, no background")
    K.check((bool(dm.en), str(dm.anchor), int(dm.dx), int(dm.dy), int(dm.bw), int(dm.bh), bool(dm.bg)) == (True, "br", 224, 8, 230, 88, False),
            "P39 built-in mount card: ON, br 224,8, 230 x 88, no background")
    K.eq([int(x) for x in Wid.screenPosWH(dp, 230, 88)] + [int(x) for x in Wid.screenPosWH(dm, 230, 88)], [362, 984, 1466, 984], "P39 1080p: pet card x 362, mount card x 1466, both y 984")

    # ---- one card per widget from ONE pets:fn:hud answer
    cur = [[PFIRE, HORSE]]
    calls = [0]

    def hud(a):
        calls[0] += 1
        return None if cur[0] is None else SA(cur[0])
    bridge.put("pets:fn:hud", JProxy("java.util.function.Function", dict={"apply": hud}))
    mp, mm = L_(Wid.model("Pets", pr, True)), L_(Wid.model("Mount", pr, True))
    K.check(mp[21] == "Ypqha" and mp[2] == "Fire Dragon" and mp[14] == "84 / 120" and mp[16] == "Bite" and mp[8] is None,
            "P39 the pet card = the pet slot only, with the fighting dragon's health + Bite: %s" % mp[21])
    K.check(mm[21] == "Ys" and mm[8] == "Horse" and mm[9] == "Lv 5" and mm[1] == "Horse Lv 5" and mm[2] is None and mm[14] is None,
            "P39 the mount card = the mount slot only (Horse Lv 5, no block): %s" % mm[21])
    K.eq(calls[0], 2, "P39 one pets:fn:hud call per card")
    cur[0] = [WOLF, FIRE]          # the 0.4.20 - 0.4.26 shape: the fields on the second line
    mp, mm = L_(Wid.model("Pets", pr, True)), L_(Wid.model("Mount", pr, True))
    K.check(mp[21] == "Yp" and mm[21] == "Ysha" and mm[14] == "84 / 120", "P39 an older SkyyPets: pet card Wolf, the block on the mount card: %s %s" % (mp[21], mm[21]))
    cur[0] = ["", HORSE]
    K.check(L_(Wid.model("Pets", pr, True))[0] == "Y0" and L_(Wid.model("Mount", pr, True))[21] == "Ys", "P39 an empty pet slot hides only the pet card")
    cur[0] = [WOLF, ""]
    K.check(L_(Wid.model("Mount", pr, True))[0] == "Y0" and L_(Wid.model("Pets", pr, True))[21] == "Yp", "P39 an empty mount slot hides only the mount card")
    cur[0] = None
    K.check(L_(Wid.model("Pets", pr, True))[0] == "Y0" and L_(Wid.model("Mount", pr, True))[0] == "Y0", "P39 no answer = both hidden")
    K.check(Wid.petsPick(None, 0) is None and [str(x) for x in Wid.petsPick(SA([WOLF]), 1)] == ["", ""], "P39 petsPick: null / a short answer = an empty slot")

    # ---- the Mount markup
    L = LS.get(u).get("Mount")
    for sc in (100, 66, 150):
        for lines in (["", HORSE], ["", FIRE], ["", FIRE.replace("|84|120|Bite|ok||", "|||Radiance|r|1.000|riding")]):
            m = Wid.petsModelOf(SA(lines))
            w = int(Wid.multiW("Mount", L, m, sc, 6))
            body = str(Wid.multiBody("Mount", "SkyyWMount", L, sc, m, 6, w))
            hh = int(Wid.bodyH("Mount", m, sc))
            miss = []
            for k in [str(x) for x in Wid.pairsSc("Mount", m, sc, True)][0::2]:
                if ("Label #SkyyWMount%sTxt " % k) not in body:
                    miss.append(k)
            for k in [str(x) for x in Wid.barPairs("Mount", m)][0::2]:
                if ("ProgressBar #SkyyWMount%s " % k) not in body:
                    miss.append(k)
            for k in [str(x) for x in Wid.visPairs("Mount", m)][0::2]:
                if ("Group #SkyyWMount%s " % k) not in body:
                    miss.append(k)
            bottoms = [int(a) + int(b) for a, b in re.findall(r"Top: (\d+), Width: \d+, Height: (\d+)\)", body)]
            K.check(not miss and max(bottoms) <= hh and w == 230 * sc // 100, "P39 MOUNT MARKUP %d %% %s: every fill key exists %s, lowest %d <= height %d, width %d"
                    % (sc, lines[1].split("|")[2], miss, max(bottoms), hh, w))
    K.eq(int(Wid.bodyH("Mount", Wid.petsModelOf(SA(["", HORSE])), 100)), 44, "P39 a plain mount card = 44 px")
    K.eq(int(Wid.bodyH("Mount", Wid.petsModelOf(SA(["", FIRE])), 100)), 88, "P39 a mount card with health + ability = 88 px (the box maximum)")
    K.eq(int(Wid.bodyH("Pets", Wid.petsModelOf(SA([PFIRE, ""])), 100)), 88, "P39 the pet card with health + ability = 88 px (the box maximum)")

    # ---- a real HUD: two cards, each its own slot
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    mFill = HM.class_.getDeclaredMethod("fill", UCB.class_, JClass("boolean"))
    mFill.setAccessible(True)
    allc = lambda b: " ".join(str(c.selector or "") + " " + str(c.text or "") + " " + str(c.data or "") for c in b.getCommands())
    cur[0] = [PFIRE, HORSE]
    h = HM(pr)
    b1, b2 = UCB(), UCB()
    mBuild.invoke(h, b1)
    mFill.invoke(h, b2, False)
    t = allc(b1) + " " + allc(b2)
    K.check("#SkyyWPetsF0" in t and "#SkyyWMountF1" in t and "#SkyyWPetsF1" not in t and "#SkyyWMountF0" not in t and "Fire Dragon" in t and "Horse" in t and "84 / 120" in t,
            "HUD the pet card draws the pet slot (F0, Fire Dragon, health), the mount card the mount slot (F1, Horse)")
    cur[0] = [PFIRE.replace("|84|", "|30|"), HORSE]
    b3 = UCB()
    re_ = bool(mFill.invoke(h, b3, False))
    K.check(not re_ and "30 / 120" in allc(b3) and "ItemIcon" not in allc(b3), "HUD a health tick = values only, no re-send")
    b4 = UCB()
    K.check(not bool(mFill.invoke(h, b4, False)) and "SkyyWPets" not in allc(b4) and "SkyyWMount" not in allc(b4), "HUD nothing changed = nothing sent")
    cur[0] = [PFIRE.replace("|84|", "|30|"), WOLF.replace("1|p1|", "2|p1|")]
    K.check(bool(mFill.invoke(h, UCB(), False)), "HUD another mount = a re-send (its shape: portrait / rarity)")
    cur[0] = [PFIRE, ""]
    h = HM(pr)
    b5, b6 = UCB(), UCB()
    mBuild.invoke(h, b5)
    mFill.invoke(h, b6, False)
    K.check("#SkyyWMountF1" not in allc(b5) + allc(b6) and "#SkyyWPetsF0" in allc(b5) + allc(b6), "HUD the mount slot empty: no mount card, the pet card stays")

    # ---- the stand-ins
    sp, sm = L_(Wid.sampleU("Pets", "Skyy", True)), L_(Wid.sampleU("Mount", "Skyy", True))
    K.check(sp[0] == "S" and sp[2] == "Light Dragon" and sp[14] == "84 / 120" and sp[17] == "6s" and "q" in sp[21] and sm[0] == "S" and sm[8] == "Horse" and sm[9] == "Lv 18" and sm[21] == "Ys",
            "SAMPLE with SkyyPets: pet card = the fighting Light Dragon (health, Radiance 6s), mount card = Horse Lv 18: %s %s" % (sp[21], sm[21]))
    bridge.remove("pets:fn:hud")
    sp, sm = L_(Wid.sampleU("Pets", "Skyy", True)), L_(Wid.sampleU("Mount", "Skyy", True))
    K.check(sp[2] == "Needs SkyyPets 0.4.20" and sp[21] == "Yp" and sm[8] == "Needs SkyyPets 0.4.20" and sm[21] == "Ys" and sm[13] == "#7f93a6",
            "SAMPLE without SkyyPets: 'Needs SkyyPets 0.4.20' on both cards (grey frame)")
    vm = L_(Wid.viewModel("Mount", pr, LS.get(u).get("Mount")))
    K.check(vm[1] == "Needs SkyyPets 0.4.20", "EDITOR the hidden Mount card shows its stand-in")
    hb = int(Wid.multiW("Mount", LS.get(u).get("Mount"), Wid.petsSampleS(1), 100, 6))
    K.eq(hb, 230, "EDITOR the mount card's box is 230 wide")

    # ---- FIRST SPOT + THE ONE-TIME MOVE (LayoutStore.get on real files in the scratch layouts folder)
    hist = os.path.join(work, "layout-history")
    LS.CACHE.clear()
    n0 = int(LS.V5MOVED.get())
    u1 = UUID(0x39, 1)
    m1 = LS.get(u1)
    g = lambda m, i: (bool(m.get(i).en), str(m.get(i).anchor), int(m.get(i).dx), int(m.get(i).dy), int(m.get(i).scale))
    K.check(g(m1, "Pets") == (True, "b", -483, 8, 100) and g(m1, "Mount") == (True, "br", 224, 8, 100) and g(m1, "Keys")[1:4] == ("b", -330, 14),
            "PLACE a new player: pet card b -483,8, mount card br 224,8, Key hints b -330,14 between the pet card and the hotbar: %s" % (g(m1, "Keys"),))
    K.check(not os.path.exists(os.path.join(work, "layouts", str(u1) + ".properties")) and not os.path.exists(hist), "PLACE a new player: nothing written")
    # (b) a 0.3.38 file: Pets at the old spot (scale 120 + a style kept), no Mount line
    u2 = UUID(0x39, 2)
    pets_line = "1,br,460,210,120,0,gold,1,0,1,black"
    f2 = _file(work, u2, [("Abilities", "1,br,460,21,100,0"), ("Keys", "1,b,-330,14,100,0"), ("Pets", pets_line)])
    raw2 = open(f2, "rb").read()
    m2 = LS.get(u2)
    p2 = m2.get("Pets")
    hf = os.path.join(hist, str(u2) + ".v038.properties")
    # at scale 120 the card is 276 x 105: b -483,8 would touch their Key hints (b -330,14) -> cardPlace's next free spot b -513,8
    K.check(g(m2, "Pets") == (True, "b", -513, 8, 120) and str(p2.col) == "gold" and bool(p2.glow) and str(p2.gcol) == "black" and int(LS.V5MOVED.get()) == n0 + 1,
            "MOVE an old-spot Pets line -> the pet side (b -513,8: the 120 %% card clears their Key hints), scale 120 + style kept, counted: %s" % (g(m2, "Pets"),))
    K.check(os.path.isfile(hf) and open(hf, "rb").read() == raw2 and open(f2, "rb").read() == raw2, "MOVE a verified history copy (same bytes); the layout file itself untouched")
    K.check(g(m2, "Mount") == (True, "br", 224, 8, 100), "MOVE the mount card at its built-in spot")
    LS.save(u2)
    import time
    for _ in range(50):
        if b"Mount=" in open(f2, "rb").read():
            break
        time.sleep(0.05)
    sv = open(f2, "rb").read().decode("latin-1")
    K.check("Mount=1,br,224,8,100,0" in sv and "Pets=1,b,-513,8,120,0,gold,1,0,1,black" in sv, "MOVE the next save writes the new Pets spot + the Mount line (the run-once marker)")
    LS.CACHE.clear()
    m2b = LS.get(u2)
    K.check(g(m2b, "Pets") == (True, "b", -513, 8, 120) and int(LS.V5MOVED.get()) == n0 + 1, "MOVE a second load after the save: no move again, same spot")
    # the same file loaded twice WITHOUT a save in between (a restart before any layout change): the same result, the one history copy kept
    u3 = UUID(0x39, 3)
    f3 = _file(work, u3, [("Pets", OLD_PETS)])
    LS.CACHE.clear()
    a3 = g(LS.get(u3), "Pets")
    LS.CACHE.clear()
    b3_ = g(LS.get(u3), "Pets")
    K.check(a3 == b3_ == (True, "b", -483, 8, 100) and sorted(x for x in os.listdir(hist) if x.startswith(str(u3))) == [str(u3) + ".v038.properties"],
            "MOVE a restart before any save: the same spot, one history copy (not a second one)")
    # (c) hand-moved Pets kept exactly; its mount card at the free built-in spot; no copy
    u4 = UUID(0x39, 4)
    _file(work, u4, [("Pets", "1,tl,100,500,100,0")])
    m4 = LS.get(u4)
    K.check(g(m4, "Pets") == (True, "tl", 100, 500, 100) and g(m4, "Mount") == (True, "br", 224, 8, 100) and not os.path.exists(os.path.join(hist, str(u4) + ".v038.properties")),
            "KEEP a hand-moved Pets line is kept exactly (no copy); the mount card gets its spot")
    # (d) Pets OFF at the old spot -> moved, still OFF; Mount starts OFF
    u5 = UUID(0x39, 5)
    _file(work, u5, [("Pets", "0,br,460,210,100,0")])
    m5 = LS.get(u5)
    K.check(g(m5, "Pets") == (False, "b", -483, 8, 100) and g(m5, "Mount")[0] is False, "OFF a switched-off Pets line stays off; the Mount card starts OFF too")
    u5b = UUID(0x39, 15)
    _file(work, u5b, [("Pets", "0,tr,30,30,100,0")])
    K.check(g(LS.get(u5b), "Mount")[0] is False and g(LS.get(u5b), "Pets") == (False, "tr", 30, 30, 100), "OFF a hand-moved OFF Pets line: kept, the Mount card OFF")
    # (e) a file WITH a Mount line never moves (the marker)
    u6 = UUID(0x39, 6)
    _file(work, u6, [("Pets", OLD_PETS), ("Mount", "1,br,224,8,100,0")])
    K.check(g(LS.get(u6), "Pets") == (True, "br", 460, 210, 100) and not os.path.exists(os.path.join(hist, str(u6) + ".v038.properties")),
            "MARKER a file with a Mount line: Pets kept at br 460,210 (moved back by hand after 0.3.39), no copy")
    # (f) a crowded layout: the mount card's built-in spot touches their Party box -> the first free spot of its side
    u7 = UUID(0x39, 7)
    _file(work, u7, [("Party", "1,br,387,15,130,0"), ("Combat", "1,bl,433,23,130,0"), ("Feed", "1,bl,10,23,125,0"), ("Coins", "1,tr,8,336,150,0"),
                     ("Abilities", "1,br,10,231,110,0"), ("Stacks", "1,br,810,146,125,0")])
    m7 = LS.get(u7)
    mg = g(m7, "Mount")
    K.check(mg[1:4] == ("br", 134, 8), "PLACE a crowded layout: the mount card takes a free spot right of the hotbar: %s" % (mg,))
    q = [int(x) for x in Wid.screenPosWH(m7.get("Mount"), 230, 88)]
    pq = [int(x) for x in Wid.screenPosWH(m7.get("Party"), 442, int(Wid.hMax(m7.get("Party"))))]
    K.check(q[0] >= 1236 and (q[0] >= pq[0] + 442 + 4 or q[1] >= pq[1] + int(Wid.hMax(m7.get("Party"))) + 4 or q[1] + 88 + 4 <= pq[1]), "PLACE ... and clear of their Party box: %s vs %s" % (q, pq))
    pp = [int(x) for x in Wid.screenPosWH(m7.get("Pets"), 230, 88)]
    K.check(g(m7, "Pets")[1:4] == ("b", -393, 100) and pp == [452, 892],
            "PLACE ... their Combat / Feed boxes fill the bottom row left of the hotbar and the next rows touch the vanilla chat estimate: the widget-clear spot covering the least chat -> b -393,100 (x 452-682): %s" % (g(m7, "Pets"),))
    # FIX hud5 #1: the least-covered spot, measured: x 452-682 covers 116 x 68 px of the chat estimate (8,600,560,360); the old pick b -453,100 covered 176 x 68
    _ch = (8, 600, 560, 360)
    _cov = lambda x, y: max(0, min(x + 230, _ch[0] + _ch[2]) - max(x, _ch[0])) * max(0, min(y + 88, _ch[1] + _ch[3]) - max(y, _ch[1]))
    K.check(_cov(pp[0], pp[1]) == 116 * 68 and _cov(392, 892) == 176 * 68, "FIX1 the crowded pet card covers less of the chat than before: %d < %d px" % (_cov(pp[0], pp[1]), _cov(392, 892)))
    K.check(pp[0] + 230 + 4 <= 690, "FIX1 ... still left of the vanilla vitals / hotbar (x 690): right edge %d" % (pp[0] + 230))
    # FIX hud5 #1: the new far-left bottom-row candidates (b -633 .. -813 = x 212 .. 32): a box from x 450 on the bottom row -> the pet card at x 212 (right of the default Game Clock x 8-188), still bottom row, off the chat
    u7c = UUID(0x39, 27)
    _file(work, u7c, [("Combat", "1,bl,450,10,130,0")])
    m7c = LS.get(u7c)
    pc = [int(x) for x in Wid.screenPosWH(m7c.get("Pets"), 230, 88)]
    cb = [int(x) for x in Wid.screenPosWH(m7c.get("Combat"), 234, int(Wid.hMax(m7c.get("Combat"))))]
    K.check(g(m7c, "Pets")[1:4] == ("b", -633, 8) and pc == [212, 984] and pc[0] + 230 + 4 <= cb[0] and _cov(pc[0], pc[1]) == 0,
            "FIX1 a box across the left bottom row (x %d+): the pet card takes a far-left bottom-row spot clear of the chat: %s %s" % (cb[0], g(m7c, "Pets"), pc))
    # FIX hud5 #4: /skyyhud Reset puts both cards back at their built-in spots
    LS.reset(u7)
    K.check(g(LS.get(u7), "Pets")[1:4] == ("b", -483, 8) and g(LS.get(u7), "Mount")[1:4] == ("br", 224, 8), "FIX4 Reset restores the pet card b -483,8 and the mount card br 224,8: %s %s" % (g(LS.get(u7), "Pets"), g(LS.get(u7), "Mount")))
    u7b = UUID(0x39, 17)          # the same, with the old Pets line of a 0.3.38 save: moved, then placed the same way
    _file(work, u7b, [("Party", "1,br,387,15,130,0"), ("Combat", "1,bl,433,23,130,0"), ("Feed", "1,bl,10,23,125,0"), ("Coins", "1,tr,8,336,150,0"),
                      ("Abilities", "1,br,10,231,110,0"), ("Stacks", "1,br,810,146,125,0"), ("Pets", OLD_PETS)])
    K.check(g(LS.get(u7b), "Pets")[1:4] == ("b", -393, 100) and g(LS.get(u7b), "Mount")[1:4] == ("br", 134, 8), "PLACE a moved old-spot Pets line is placed like a new one")
    # (g) no history copy possible -> no move
    LS.CACHE.clear()
    import shutil
    shutil.rmtree(hist)
    open(hist, "w").write("a file where the folder should be")
    u8 = UUID(0x39, 8)
    _file(work, u8, [("Pets", OLD_PETS)])
    n8 = int(LS.V5MOVED.get())
    K.check(g(LS.get(u8), "Pets") == (True, "br", 460, 210, 100) and int(LS.V5MOVED.get()) == n8, "SAFE no history copy possible: the Pets line stays where it was saved")
    os.remove(hist)
    # (h) an older history copy with other bytes -> a time-stamped sibling, then the move
    os.makedirs(hist)
    u9 = UUID(0x39, 9)
    open(os.path.join(hist, str(u9) + ".v038.properties"), "wb").write(b"older bytes")
    f9 = _file(work, u9, [("Pets", OLD_PETS)])
    LS.CACHE.clear()
    K.check(g(LS.get(u9), "Pets")[1:4] == ("b", -483, 8), "SAFE an older copy with other bytes: moved")
    sib = [x for x in os.listdir(hist) if x.startswith(str(u9) + ".v038.") and x != str(u9) + ".v038.properties"]
    K.check(len(sib) == 1 and open(os.path.join(hist, sib[0]), "rb").read() == open(f9, "rb").read() and open(os.path.join(hist, str(u9) + ".v038.properties"), "rb").read() == b"older bytes",
            "SAFE ... a time-stamped sibling copy holds this file, the older copy untouched: %s" % sib)
    # (i) the server default layout code (Server Setup -> HUD), in memory only
    Cfg.DEFAULT_LAYOUT = "Pets=1:br:460:210:100:0;Coins=1:br:8:8:100:1"
    Cfg.PARSED = None
    sp_ = Wid.start("Pets")
    K.check((str(sp_.anchor), int(sp_.dx), int(sp_.dy)) == ("b", -483, 8) and bool(Wid.start("Mount").en), "DEFAULT an older default code's old-spot Pets -> the pet spot; Mount ON")
    Cfg.DEFAULT_LAYOUT = "Pets=0:br:460:210:100:0"
    Cfg.PARSED = None
    K.check(not bool(Wid.start("Mount").en) and not bool(Wid.start("Pets").en), "DEFAULT an older default code with Pets OFF: Mount OFF too")
    Cfg.DEFAULT_LAYOUT = "Pets=1:br:460:210:100:0;Mount=1:br:30:300:100:0"
    Cfg.PARSED = None
    K.check((str(Wid.start("Pets").anchor), int(Wid.start("Pets").dx)) == ("br", 460) and int(Wid.start("Mount").dx) == 30, "DEFAULT a 0.3.39 code (Mount entry) is used as written")
    Cfg.DEFAULT_LAYOUT = ""
    Cfg.PARSED = None
    # (j) /skyyhud import / profile load of an older code
    u10 = UUID(0x39, 10)
    LS.CACHE.clear()
    n = int(LS.importCode(u10, "Pets=1:br:460:210:100:0;Coins=1:tl:8:8:100:1"))
    K.check(n == 2 and g(LS.get(u10), "Pets")[1:4] == ("b", -483, 8), "IMPORT an older code's old-spot Pets -> the pet spot")
    n = int(LS.importCode(u10, "Pets=0:br:460:210:100:0"))
    K.check(g(LS.get(u10), "Mount")[0] is False and g(LS.get(u10), "Pets")[0] is False, "IMPORT an older code with Pets OFF: Mount OFF")
    n = int(LS.importCode(u10, "Pets=1:br:460:210:100:0;Mount=1:br:224:8:100:0"))
    K.check(g(LS.get(u10), "Pets")[1:4] == ("br", 460, 210), "IMPORT a 0.3.39 code: used as written")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    LS, Cfg, Pub, Wid = P("LayoutStore"), P("HudCfg"), P("CfgPub"), P("Widgets")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    lyd = os.path.join(home, "layouts")
    players = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []
    res = []
    for _n in range(2):
        b0 = HK.tree_hash(mods)
        LS.CACHE.clear()
        LS.DIR = Paths.get(lyd)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Wid.HUBFILE = Paths.get(os.path.join(mods, "Skyy_SkyyIslands", "hub.properties"))
        Cfg.load()
        Pub.start(Paths.get(mods), None)
        r_ = {}
        for us in players:
            mp = LS.get(UUID.fromString(us))
            r_[us] = dict((str(w_), str(mp.get(w_).ser())) for w_ in Wid.IDS)
        Pub.flush()
        a0 = HK.tree_hash(mods)
        res.append((r_, sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k))))
    K.check(res[0][1] == [] and res[1][1] == [] and res[0][0] == res[1][0],
            "LIVE: two starts on a COPY of the live Skyy_SkyyHud (%d layouts): nothing written, the same layouts: %s" % (len(players), [r[1] for r in res]))
    bad, spots = [], []
    for us in players:
        fl = {}
        for ln in open(os.path.join(lyd, us + ".properties"), encoding="latin-1"):
            if "=" in ln and not ln.startswith("#"):
                k_, v_ = ln.strip().split("=", 1)
                fl[k_] = v_
        r_ = res[0][0][us]
        if not all(r_[w_] == fl[w_] for w_ in r_ if w_ in fl):
            bad.append(us[:8])
        spots.append((us[:8], r_["Pets"], r_["Mount"], "Pets" in fl, "Mount" in fl))
    K.notes.append("LIVE where the cards land: %s" % [(s[0], s[1], s[2]) for s in spots])
    K.check(not bad, "LIVE: every saved line of every live layout loads exactly as saved (%d players): %s" % (len(players), bad))
    K.check(all(not s[3] and not s[4] for s in spots), "LIVE: no live layout has a Pets / Mount line yet (nothing for the one-time move): %s" % spots)
    K.check(all(s[1].startswith("1,b,") and s[2].startswith("1,br,") for s in spots), "LIVE: every player gets the pet card (b) + the mount card (br): %s" % spots)
    K.check(len(players) >= 1, "LIVE: the copy has layouts (%d)" % len(players))
    K.save()


EXPECT = {
    "Widgets": ["+m cardPlace", "+m petsModelUS", "+m petsOld", "+m petsPick", "+m petsSampleS", "~<clinit>", "~m barPairs", "~m bodyH", "~m def0", "~m label",
                "~m linePairs", "~m model", "~m multi", "~m multiBody", "~m multiW", "~m pairsSc", "~m sampleU", "~m start", "~m visPairs"],
    "LayoutStore": ["+f V5MOVED", "+m v5Copy", "+m v5Mig", "~<clinit>", "~m get", "~m importCode"],
    "SettingsPage": ["~m previewText"],      # + "Mount" in the multi-line preview headline list
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],   # the config kit's version text
    "SkyyHudPlugin": ["~m setup"],                 # the '[SkyyHud] 0.3.39 ready' version text
}
if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD, PKG, SCRATCH, EXPECT, [], [("static", run_static), ("p38", T338.run_p38), ("p39", run_p39), ("e2e", T338.run_e2e), ("live", run_live)],
           os.path.abspath(__file__), live=(T337.LIVE_DIR, "Skyy_SkyyHud"))
