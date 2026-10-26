"""SkyyHud 0.3.37 harness - the PET WIDGET (tools/hud_0_3_37_patch.py; data = SkyyPets 0.4.20's pets:fn:hud). Built on tools/harness_kit.py:
each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.37.py [--jar SkyyHud-0.3.37.jar] [--pets SkyyPets/SkyyPets-0.4.20.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.36 -> 0.3.37: exactly the listed classes / members differ
  S    static   the patch re-generates 0.3.37 byte for byte, 0.3.36's patch still regenerates 0.3.36; no system / command added
  P37  EXECUTED on the real jar classes with a stand-in pets:fn:hud: the model (pet only, both slots, health "-" / "Down" / pips, the
       ability states Ready / Fighting / Riding / cooldown / Down, a bad item id or colour never reaches the markup, a short line skipped,
       null / no function = hidden); the SHAPE stays for XP / health / cooldown changes and moves for a slot / rarity change; the
       markup at 100 % and 2/3 (editor): every text / bar / visibility key the fill sets exists, nothing below the box, the rarity
       frame + portrait; the names cut to fit; HudMain.build + fill of a real layout: the portraits, "Lv 12", a health change = value sets
       only (no re-send), a slot change = a re-send, hidden while both slots are empty; the editor samples (with / without SkyyPets)
  E2E  the REAL SkyyPets 0.4.20 jar + this jar in one JVM: a real pet record + PetHudFn on the bridge -> the widget model
  LIVE twice on a scratch COPY of the live Skyy_SkyyHud (NewBetaTest): nothing written either time, every saved line loads as saved,
       every player gets the Pets widget at its built-in spot
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the look on the real HUD (the ItemIcon portrait inside the HUD, the frame colours, the pips).
Scratch: tools/dev/scratch/petwid/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HK
import skyybuild as B

VERSION, PREV = "0.3.37", "0.3.36"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
PETS = os.path.abspath(HK.arg("--pets", os.path.join(ROOT, "SkyyPets", "SkyyPets-0.4.20.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "petwid", "h")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyHud")
GEN, GEN_OLD = os.path.join(HERE, "build_skyyhud_%s.py" % VERSION), os.path.join(HERE, "build_skyyhud_%s.py" % PREV)
WOLF = "1|p1|Wolf|3|Wolf|12|50|420|1000|Skyy_PetIcon_Wolf_Rare|||||||"
FIRE = "2|p2|DragonFire|5|Fire Dragon|34|50|2100|5200|Skyy_PetIcon_DragonFire_Legendary|84|120|Bite|ok|||#d6e4ee"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.3.37"') == 1 and g.count("registerSystem(") == o.count("registerSystem(") and g.count("registerCommand(") == o.count("registerCommand("),
            "S VERSION; no system / command added")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, os.path.basename(GEN))
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "hud_0_3_37_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S hud_0_3_37_patch.py re-generates its script byte for byte: %s" % p.stderr[-300:])
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.save()


def _setup(out, scratch, cp, tag):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm(cp, verify=True)
    UUID, System, CHM, Paths = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                f.set(obj, val)
                return
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)
    H = lambda n: JClass(PKG + n)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(scratch, tag)
    os.makedirs(os.path.join(work, "cfg"), exist_ok=True)
    os.makedirs(os.path.join(work, "layouts"), exist_ok=True)
    H("HudCfg").FILE = Paths.get(os.path.join(work, "cfg", "config.properties"))
    H("HudCfg").load()
    H("HudThreads").EXEC = None
    H("LayoutStore").DIR = Paths.get(os.path.join(work, "layouts"))
    H("LayoutStore").CACHE.clear()
    pr = U.allocateInstance(PRef.class_)
    u = UUID(0x337, 1)
    setf(pr, PRef, "uuid", u)
    setf(pr, PRef, "username", "Skyy")
    return dict(K=K, JClass=JClass, H=H, bridge=bridge, pr=pr, u=u, work=work)


def run_p37(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JProxy
    S = _setup(out, scratch, [B.SERVER_JAR, jar, B.JAVASSIST], "k")
    K, H, bridge, pr, u = S["K"], S["H"], S["bridge"], S["pr"], S["u"]
    Wid, LS, HM = H("Widgets"), H("LayoutStore"), H("HudMain")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    mFill = HM.class_.getDeclaredMethod("fill", UCB.class_, JClass("boolean"))
    mFill.setAccessible(True)
    allc = lambda b: " ".join(str(c.selector or "") + " " + str(c.text or "") + " " + str(c.data or "") for c in b.getCommands())
    SA = lambda xs: JArray(JString)(xs)
    M = lambda xs: [None if x is None else str(x) for x in Wid.petsModelOf(None if xs is None else SA(xs))]

    # ---- the model
    m = M(None)
    K.check(m[0] == "Y0" and m[1] is None, "MODEL null -> hidden (Y0)")
    K.check(M(["", ""])[0] == "Y0", "MODEL both slots empty -> hidden")
    m = M([WOLF, ""])
    K.check(m[21] == "Yp" and m[1] == "Wolf Lv 12" and m[2:8] == ["Wolf", "Lv 12", "0.420", "420 / 1,000 XP", "Skyy_PetIcon_Wolf_Rare", "#2770b7"]
            and m[0] == "Yp|Skyy_PetIcon_Wolf_Rare|#2770b7", "MODEL pet only: name, Lv, XP bar 0.420, '420 / 1,000 XP', the Rare portrait + the Rare frame colour: %s" % m)
    m = M([WOLF, FIRE])
    K.check(m[21] == "Ypsha" and m[8:14] == ["Fire Dragon", "Lv 34", "0.404", "2,100 / 5,200 XP", "Skyy_PetIcon_DragonFire_Legendary", "#bb8a2c"]
            and m[14] == "84 / 120" and m[15] == "14" and m[16:21] == ["Bite", "Ready", "", "g", "#d6e4ee"],
            "MODEL both: the dragon's XP, health 84 / 120 = 14 of 20 pips, Bite Ready (green), no cooldown bar: %s" % m[8:22])
    sh0 = m[0]
    var = lambda **kw: "|".join(kw.get("f%d" % i, x) for i, x in enumerate(FIRE.split("|")))
    m = M([WOLF, var(f10="30", f7="2500")])
    K.check(m[0] == sh0 and m[14] == "30 / 120" and m[15] == "5" and m[10] == "0.481", "SHAPE the same for health / XP changes (pips 5, bar 0.481)")
    m = M([WOLF, var(f10="1")])
    K.eq(m[15], "1", "MODEL 1 health = at least one pip")
    m = M([WOLF, var(f10="0", f11="0", f13="d23000", f14="0.300", f15="down")])
    K.check(m[0] == sh0 and m[14] == "Down" and m[15] == "0" and m[17] == "Down 23s" and m[19] == "r" and m[18] == "0.300", "MODEL DOWN: 'Down', no pips, 'Down 23s' red, bar 0.300 (same shape)")
    m = M([WOLF, var(f10="-", f11="-")])
    K.check(m[0] == sh0 and m[14] == "-" and m[15] == "0", "MODEL not in the world: health '-'")
    m = M([WOLF, var(f13="c6000", f14="0.400", f12="Radiance", f16="#ffe9a0")])
    K.check(m[17] == "6s" and m[19] == "y" and m[20] == "#ffe9a0" and m[0] != sh0, "MODEL Radiance cooling: '6s' gold, its colour (the ability colour is in the shape)")
    K.check(M([WOLF, var(f13="f")])[17] == "Fighting" and M([WOLF, var(f13="r", f15="riding")])[17:20:2] == ["Riding", "y"], "MODEL Fighting (green) / Riding (gold)")
    # FIX petwidfix: a passive perk = "Passive", no bar; the bar (group AB) only for a real cooldown
    mp = Wid.petsModelOf(SA([WOLF, var(f13="p", f12="Void Strike", f16="#9b6bff")]))
    m = [None if x is None else str(x) for x in mp]
    vp = [str(x) for x in Wid.visPairs("Pets", mp)]
    bp = [str(x) for x in Wid.barPairs("Pets", mp)]
    K.check(m[17] == "Passive" and m[19] == "g" and m[18] == "" and vp[vp.index("AB") + 1] == "0" and "BA" not in bp[0::2],
            "MODEL a passive perk: 'Passive', no cooldown bar (AB hidden, no BA value): %s %s" % (m[16:21], bp))
    mc = Wid.petsModelOf(SA([WOLF, var(f13="c6000", f14="0.400", f12="Radiance", f16="#ffe9a0")]))
    vc = [str(x) for x in Wid.visPairs("Pets", mc)]
    K.check(vc[vc.index("AB") + 1] == "1" and "BA" in [str(x) for x in Wid.barPairs("Pets", mc)][0::2], "MODEL a real cooldown: the bar shown (AB 1) + its BA value")
    vf = [str(x) for x in Wid.visPairs("Pets", Wid.petsModelOf(SA([WOLF, FIRE])))]
    K.eq(vf[vf.index("AB") + 1], "0", "MODEL Bite Ready: no bar")
    m = M([WOLF, var(f9='Bad"Id; } Group', f16="red; } X")])
    K.check(m[12] == "" and m[20] == "#d6e4ee", "MODEL a bad item id / colour never reaches the markup (id '', colour = soft white)")
    m = M(["1|x|Wolf|3", FIRE])
    K.check(m[21] == "Ysha" and m[2] is None and m[1] == "Fire Dragon Lv 34", "MODEL a short (bad) line is skipped; the summon alone shows")
    K.check(M([WOLF, var(f2="DragonFire", f9="Skyy_PetIcon_DragonFire_Mythic", f3="6")])[0] != sh0, "SHAPE moves for a rarity / portrait change (a fuse)")
    m = M([WOLF, "2|p9|Horse|2|Horse|5|50|0|200|Skyy_PetIcon_Horse_Uncommon|||||||"])
    K.check(m[21] == "Yps" and m[14] is None and m[16] is None, "MODEL a Horse summon: no health, no ability rows")
    K.check(M([WOLF.replace("|1000|", "|0|"), ""])[4:6] == ["1.000", "Max level"], "MODEL at the cap: full bar, 'Max level'")

    # ---- the markup (100 % + the editor's 2/3): every key the fill sets exists; nothing below the box
    L = LS.get(u).get("Pets")
    K.check(L is not None and bool(L.en) and str(L.anchor) == "br" and int(L.dx) == 460 and int(L.dy) == 210 and int(L.bw) == 230 and int(L.bh) == 132 and not bool(L.bg),
            "LAYOUT the built-in Pets line: ON, br 460,210 (FIX petwidfix: above Stacks, out of the pickup popups), 230 x 132, no background")
    for sc in (100, 66, 150):
        for lines in ([WOLF, ""], [WOLF, FIRE], ["", FIRE], [WOLF, "2|p9|Horse|2|Horse|5|50|0|200|Skyy_PetIcon_Horse_Uncommon|||||||"]):
            mm = Wid.petsModelOf(SA(lines))
            w = int(Wid.multiW("Pets", L, mm, sc, 6))
            body = str(Wid.multiBody("Pets", "SkyyWPets", L, sc, mm, 6, w))
            hh = int(Wid.bodyH("Pets", mm, sc))
            miss = []
            for k in [str(x) for x in Wid.pairsSc("Pets", mm, sc, True)][0::2]:
                if ("Label #SkyyWPets%sTxt " % k) not in body:
                    miss.append(k)
            for k in [str(x) for x in Wid.barPairs("Pets", mm)][0::2]:
                if ("ProgressBar #SkyyWPets%s " % k) not in body:
                    miss.append(k)
            for k in [str(x) for x in Wid.visPairs("Pets", mm)][0::2]:
                if ("Group #SkyyWPets%s " % k) not in body:
                    miss.append(k)
            bottoms = [int(a) + int(b) for a, b in re.findall(r"Top: (\d+), Width: \d+, Height: (\d+)\)", body)]
            K.check(not miss and max(bottoms) <= hh and w == 230 * sc // 100, "MARKUP %d %% %s: every fill key exists %s, lowest element %d <= height %d, width %d"
                    % (sc, [x.split("|")[2] if x else "-" for x in lines], miss, max(bottoms), hh, w))
    mm = Wid.petsModelOf(SA([WOLF, FIRE]))
    body = str(Wid.multiBody("Pets", "SkyyWPets", L, 100, mm, 6, 230))
    K.check(re.search(r"Group #SkyyWPetsAB [{][^{]*Visible: false; ProgressBar #SkyyWPetsBA ", body) is not None, "MARKUP Bite: the bar group AB built hidden")
    _bc = str(Wid.multiBody("Pets", "SkyyWPets", L, 100, Wid.petsModelOf(SA([WOLF, var(f13="c6000", f14="0.400", f12="Radiance", f16="#ffe9a0")])), 6, 230))
    K.check(re.search(r"Group #SkyyWPetsAB [{][^{]*Visible: true; ProgressBar #SkyyWPetsBA [^}]*Value: 0.400", _bc) is not None, "MARKUP Radiance cooling: the bar group AB shown, Value 0.400")
    K.check('ItemIcon #SkyyWPetsI0 { Anchor: (Left: ' in body and 'ItemId: "Skyy_PetIcon_Wolf_Rare"' in body and 'ItemId: "Skyy_PetIcon_DragonFire_Legendary"' in body
            and "Background: #2770b7(0.9)" in body and "Background: #bb8a2c(0.9)" in body and body.count("Background: #ff6b6b(0.95)") == 20,
            "MARKUP the two portraits (ItemIcon by id) in their rarity frames (Rare blue, Legendary gold) + 20 health pips")
    K.eq(int(Wid.bodyH("Pets", mm, 100)), 132, "MARKUP pet + dragon summon = the 132 px maximum box")
    K.eq(int(Wid.bodyH("Pets", Wid.petsModelOf(SA([WOLF, ""])), 100)), 44, "MARKUP pet only = 44 px")
    lp = Wid.petsModelOf(SA([WOLF.replace("|Wolf|12|", "|Ancient Thunderous Skeleton Knight Overlord|12|"), ""]))
    pp = [str(x) for x in Wid.pairsSc("Pets", lp, 100, True)]
    K.check(pp[1].endswith("...") and int(Wid.textW(pp[1], 13, True)) <= 230 - 8 - (8 + 38 + 6) - int(Wid.textW("Lv 12", 13, True)) - 8 + 8, "TEXT a long name is cut before its Lv: %s" % pp[1])

    # ---- a real HUD: build + the 1 s fill through a stand-in pets:fn:hud
    cur = [[WOLF, FIRE]]
    calls = [0]

    def fn(a):
        calls[0] += 1
        return None if cur[0] is None else SA(cur[0])
    bridge.put("pets:fn:hud", JProxy("java.util.function.Function", dict={"apply": fn}))
    h = HM(pr)
    b = UCB()
    mBuild.invoke(h, b)
    t1 = allc(b)
    b2 = UCB()
    mFill.invoke(h, b2, False)
    t2 = allc(b2)
    K.check('ItemId: "Skyy_PetIcon_Wolf_Rare"' in t1 and "#SkyyWPetsF1" in t1 and "Lv 12" in t1 + t2 and "84 / 120" in t1 + t2 and "Fire Dragon" in t1 + t2 and calls[0] >= 1,
            "HUD build + fill: both portraits, 'Lv 12', the dragon's health; pets:fn:hud asked (%d calls)" % calls[0])
    cur[0] = [WOLF, var(f10="30")]
    b3 = UCB()
    re_ = bool(mFill.invoke(h, b3, False))
    t3 = allc(b3)
    K.check(not re_ and "30 / 120" in t3 and "#SkyyWPetsH6.Visible" in t3 and "ItemIcon" not in t3, "HUD a health change = value + pip sets only, no re-send")
    b4 = UCB()
    re_ = bool(mFill.invoke(h, b4, False))
    K.check(not re_ and "SkyyWPets" not in allc(b4), "HUD nothing changed = nothing sent (no flicker)")
    cur[0] = [WOLF, var(f10="0", f11="0", f13="d23000", f14="0.300", f15="down")]
    b4d = UCB()
    re_ = bool(mFill.invoke(h, b4d, False))
    K.check(not re_ and "#SkyyWPetsAB.Visible" in allc(b4d) and "#SkyyWPetsBA.Value" in allc(b4d) and "Down 23s" in allc(b4d),
            "HUD Bite -> DOWN: the bar group shown + its Value + 'Down 23s', no re-send (FIX petwidfix)")
    cur[0] = [WOLF, var(f10="30")]
    b4e = UCB()
    re_ = bool(mFill.invoke(h, b4e, False))
    K.check(not re_ and "#SkyyWPetsAB.Visible" in allc(b4e) and "#SkyyWPetsBA.Value" not in allc(b4e), "HUD back to Bite Ready: the bar group hidden again, no re-send")
    cur[0] = [WOLF, var(f13="c5000", f14="0.500", f12="Radiance", f16="#ffe9a0")]
    K.check(bool(mFill.invoke(h, UCB(), False)), "HUD the summon changed to another ability colour = a re-send")
    h = HM(pr)
    mBuild.invoke(h, UCB())
    cur[0] = [WOLF, var(f13="c4000", f14="0.600", f12="Radiance", f16="#ffe9a0")]
    b5 = UCB()
    re_ = bool(mFill.invoke(h, b5, False))
    K.check(not re_ and "4s" in allc(b5) and "#SkyyWPetsBA.Value" in allc(b5), "HUD a cooldown tick = the text + the bar Value, no re-send")
    cur[0] = [WOLF, ""]
    K.check(bool(mFill.invoke(h, UCB(), False)), "HUD the summon taken out of its slot = a re-send (the shape)")
    cur[0] = ["", ""]
    h = HM(pr)
    b6 = UCB()
    mBuild.invoke(h, b6)
    K.check("#SkyyWPetsF0" not in allc(b6) and "SkyyWPetsN0" not in allc(b6), "HUD both slots empty: the widget is not drawn")
    cur[0] = None
    K.check(Wid.petsModelU(u)[1] is None, "HUD pets:fn:hud answers null: hidden")
    # ---- the editor / Settings stand-ins
    sm = [None if x is None else str(x) for x in Wid.petsSample()]
    K.check(sm[0] == "S" and sm[2] == "Wolf" and sm[8] == "Light Dragon" and sm[17] == "6s" and sm[14] == "84 / 120", "SAMPLE with SkyyPets: Wolf + Light Dragon (health, Radiance 6s)")
    bridge.remove("pets:fn:hud")
    sm = [None if x is None else str(x) for x in Wid.petsSample()]
    K.check(sm[2] == "Needs SkyyPets 0.4.20" and sm[21] == "Yp" and sm[6] == "", "SAMPLE without SkyyPets: 'Needs SkyyPets 0.4.20' (a grey frame, no picture)")
    vm = [None if x is None else str(x) for x in Wid.viewModel("Pets", pr, L)]
    K.check(vm[1] == "Needs SkyyPets 0.4.20" and str(Wid.label("Pets")) == "Pets", "EDITOR the hidden widget shows its stand-in; label 'Pets'")
    K.check(int(Wid.PETCALLS.get()) >= 3, "the PETCALLS counter (%d)" % int(Wid.PETCALLS.get()))
    K.save()


def run_e2e(out, jar, scratch, _home):
    from jpype import JClass, JProxy
    S = _setup(out, scratch, [B.SERVER_JAR, jar, PETS], "e")
    K, H, u, bridge = S["K"], S["H"], S["u"], S["bridge"]
    P = lambda n: JClass("com.skyy.pets." + n)
    Paths = JClass("java.nio.file.Paths")
    P("PetsLog").LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "e-mods")
    os.makedirs(mods, exist_ok=True)
    P("PetsCfg").load(Paths.get(mods))
    P("PetStore").ROOT = Paths.get(os.path.join(mods, "Skyy_SkyyPets"))
    P("PetStore").DIR = P("PetStore").ROOT.resolve("pets")
    P("PetsEng").API = JProxy("com.skyy.pets.PetsApi", dict={"online": lambda: None, "byName": lambda n: None, "nameOf": lambda x: "Skyy", "tell": lambda a, b, c: None})
    key = str(P("PetStore").pkey(u))
    P("PetStore").KEYOF.put(u, key)
    r = P("PetStore").get(key)
    r.set("starter", "1")
    pid = str(P("PetOps").create(r, None, "Rabbit", 6, 7, 55, "test", "harness", False))
    r.set("active.1", pid)
    bridge.put("pets:fn:hud", P("PetHudFn")())
    m = [None if x is None else str(x) for x in H("Widgets").petsModelU(u)]
    K.check(m[21] == "Yp" and m[2] == "Rabbit" and m[3] == "Lv 7" and m[6] == "Skyy_PetIcon_Rabbit_Mythic" and m[7] == "#CC66CC" and m[5].startswith("55 / "),
            "E2E the real SkyyPets 0.4.20 PetHudFn -> a Mythic Rabbit Lv 7 with 55 XP, its Mythic portrait + the Mythic frame colour: %s" % m[:8])
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
    bad, spot = [], []
    for us in players:
        fl = {}
        for ln in open(os.path.join(lyd, us + ".properties"), encoding="latin-1"):
            if "=" in ln and not ln.startswith("#"):
                k_, v_ = ln.strip().split("=", 1)
                fl[k_] = v_
        r_ = res[0][0][us]
        if not all(r_[w_] == fl[w_] for w_ in r_ if w_ in fl):
            bad.append(us[:8])
        pl = LS.get(UUID.fromString(us)).get("Pets")
        if "Pets" in fl or not (bool(pl.en) and str(pl.anchor) == "br" and int(pl.dx) == 460 and int(pl.dy) == 210):
            spot.append(us[:8])
    K.check(not bad, "LIVE: every saved line of every live layout loads exactly as saved (%d players): %s" % (len(players), bad))
    K.check(not spot, "LIVE: every live player gets the Pets widget ON at br 460,210 (no saved Pets line yet): %s" % spot)
    K.check(len(players) >= 1, "LIVE: the copy has layouts (%d)" % len(players))
    K.save()


EXPECT = {
    "Widgets": ["+f PETCALLS", "+m petsBody", "+m petsCol", "+m petsGlow", "+m petsH", "+m petsHave", "+m petsId", "+m petsModelOf", "+m petsModelU",
                "+m petsPairs", "+m petsRcol", "+m petsRows", "+m petsSample", "+m petsXp", "~<clinit>", "~m barPairs", "~m bodyH", "~m def0", "~m label", "~m linePairs", "~m model",
                "~m multi", "~m multiBody", "~m multiW", "~m pairsSc", "~m sampleU", "~m visPairs"],
    "SettingsPage": ["~m previewText"],      # + "Pets" in the multi-line preview headline list
    # def0 / label: the generated default-layout + label tables (+ the Pets line)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],   # the config kit's version text
    "SkyyHudPlugin": ["~m setup"],                 # the '[SkyyHud] 0.3.37 ready' version text
}
if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD, PKG, SCRATCH, EXPECT, [], [("static", run_static), ("p37", run_p37), ("e2e", run_e2e), ("live", run_live)],
           os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyHud"))
