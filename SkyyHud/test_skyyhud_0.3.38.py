"""SkyyHud 0.3.38 harness - the pet card shows the FIGHTING pet's health + ability under the card that carries it (tools/hud_0_3_38_patch.py;
data = SkyyPets 0.4.27's pets:fn:hud: the health / Bite fields on the PET slot line). Built on tools/harness_kit.py and on 0.3.37's harness
(every 0.3.37 phase runs again on this jar, unchanged: the old pets:fn:hud shape - fields on the second line - shows exactly as before).

    python SkyyHud/test_skyyhud_0.3.38.py [--jar SkyyHud-0.3.38.jar] [--pets SkyyPets/SkyyPets-0.4.27.jar] [--dir <scratch>] [--keep]

  A / C / AA  verify (-Xverify:all), compare 0.3.37 -> 0.3.38, the engine-access audit
  S     static   the patch re-generates 0.3.38 byte for byte; no system / command added
  P37   0.3.37's model / markup / HUD phase on this jar (the old line shape)
  P38   EXECUTED: the block from the PET line (shape letter q): health / pips / Bite / DOWN; the box height = the 0.3.37 sum; under the pet card
        (above the mount card's frame); pet line alone; the first line wins when both carry it; a real HUD build + fill + a re-send when the
        block moves from one card to the other
  E2E   the REAL SkyyPets 0.4.27 jar + this jar in one JVM: a dragon in the PET slot -> PetHudFn -> the block under the pet card
  LIVE  twice on a scratch COPY of the live Skyy_SkyyHud: nothing written, every saved line loads as saved
Not testable without the game (UNVERIFIED): the look on the real HUD.
Scratch: tools/dev/scratch/pets1fix/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "pets1fix", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyHud-0.3.38.jar")]
if "--pets" not in sys.argv:
    sys.argv += ["--pets", os.path.join(ROOT, "SkyyPets", "SkyyPets-0.4.27.jar")]
import harness_kit as HK
import skyybuild as B

_s = importlib.util.spec_from_file_location("test_skyyhud_0_3_37", os.path.join(HERE, "test_skyyhud_0.3.37.py"))
T337 = importlib.util.module_from_spec(_s)
_a = list(sys.argv)
_s.loader.exec_module(T337)
sys.argv[:] = _a

VERSION, PREV = "0.3.38", "0.3.37"
JAR, PETS, SCRATCH = T337.JAR, T337.PETS, T337.SCRATCH
OLD = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
PKG = T337.PKG
GEN, GEN_OLD = os.path.join(HERE, "build_skyyhud_%s.py" % VERSION), os.path.join(HERE, "build_skyyhud_%s.py" % PREV)
WOLF, FIRE = T337.WOLF, T337.FIRE
# SkyyPets 0.4.27's lines: the fighting dragon in the PET slot (fields 10-16), a Horse in the mount slot (no fields)
PFIRE = "1|p2|DragonFire|5|Fire Dragon|34|50|2100|5200|Skyy_PetIcon_DragonFire_Legendary|84|120|Bite|ok|||#d6e4ee"
HORSE = "2|p9|Horse|2|Horse|5|50|0|200|Skyy_PetIcon_Horse_Uncommon|||||||"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.3.38"') == 1 and g.count("registerSystem(") == o.count("registerSystem(") and g.count("registerCommand(") == o.count("registerCommand("),
            "S VERSION; no system / command added")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, os.path.basename(GEN))
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "hud_0_3_38_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S hud_0_3_38_patch.py re-generates its script byte for byte: %s" % p.stderr[-300:])
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.save()


def run_p38(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JProxy
    S = T337._setup(out, scratch, [B.SERVER_JAR, jar, B.JAVASSIST], "k38")
    K, H, bridge, pr, u = S["K"], S["H"], S["bridge"], S["pr"], S["u"]
    Wid, LS, HM = H("Widgets"), H("LayoutStore"), H("HudMain")
    SA = lambda xs: JArray(JString)(xs)
    M = lambda xs: [None if x is None else str(x) for x in Wid.petsModelOf(SA(xs))]
    m = M([PFIRE, HORSE])
    K.check("q" in m[21] and "h" in m[21] and "a" in m[21] and "s" in m[21] and m[14] == "84 / 120" and m[15] == "14" and m[16:21] == ["Bite", "Ready", "", "g", "#d6e4ee"],
            "P38 the PET line's fields: health 84 / 120 (14 pips), Bite Ready, q = under the pet card: %s %s" % (m[21], m[14:21]))
    K.check(m[2] == "Fire Dragon" and m[8] == "Horse", "P38 the pet card = the dragon, the mount card = the Horse")
    m0 = M([WOLF, FIRE])
    K.check("q" not in m0[21] and m0[21] == "Ypsha", "P38 the 0.3.37 shape (fields on the mount line) is unchanged: %s" % m0[21])
    md = M([PFIRE.replace("|84|120|Bite|ok||", "|0|0|Bite|d23000|0.300|down"), HORSE])
    K.check(md[14] == "Down" and md[17] == "Down 23s" and md[19] == "r", "P38 the pet-slot dragon DOWN: 'Down', 'Down 23s' red")
    mb = M([PFIRE, FIRE])
    K.check("q" in mb[21] and mb[14] == "84 / 120", "P38 both lines carry fields: the first (the pet slot) wins")
    ma = M([PFIRE, ""])
    K.check(ma[21] == "Ypqha" and ma[2] == "Fire Dragon", "P38 the pet line alone with its block: %s" % ma[21])
    L = LS.get(u).get("Pets")
    K.eq(int(Wid.bodyH("Pets", Wid.petsModelOf(SA([PFIRE, HORSE])), 100)), 132, "P38 pet dragon + Horse = the same 132 px maximum box")
    K.eq(int(Wid.bodyH("Pets", Wid.petsModelOf(SA([PFIRE, ""])), 100)), 3 + 38 + 22 + 22 + 3, "P38 pet dragon alone = card + health + ability")
    for sc in (100, 66, 150):
        for lines in ([PFIRE, HORSE], [PFIRE, ""], [PFIRE, FIRE]):
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
            K.check(not miss and max(bottoms) <= hh, "P38 MARKUP %d %% %s: every fill key exists %s, lowest %d <= height %d" % (sc, [x.split("|")[2] if x else "-" for x in lines], miss, max(bottoms), hh))
    body = str(Wid.multiBody("Pets", "SkyyWPets", L, 100, Wid.petsModelOf(SA([PFIRE, HORSE])), 6, 230))
    th = int(re.search(r"Label #SkyyWPetsHLTxt [{][^}]*?Top: (\d+)", body).group(1)) if re.search(r"Label #SkyyWPetsHLTxt [{][^}]*?Top: (\d+)", body) else -1
    tf1 = int(re.search(r"Group #SkyyWPetsF1 [{] Anchor: [(]Left: \d+, Top: (\d+)", body).group(1))
    tf0 = int(re.search(r"Group #SkyyWPetsF0 [{] Anchor: [(]Left: \d+, Top: (\d+)", body).group(1))
    K.check(tf0 < th < tf1 and body.count("Background: #ff6b6b(0.95)") == 20, "P38 the health row sits under the pet card, above the mount card (F0 %d < health %d < F1 %d), 20 pips" % (tf0, th, tf1))
    # a real HUD: the block moving from the mount card to the pet card = a re-send; a health tick = values only
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    mFill = HM.class_.getDeclaredMethod("fill", UCB.class_, JClass("boolean"))
    mFill.setAccessible(True)
    allc = lambda b: " ".join(str(c.selector or "") + " " + str(c.text or "") + " " + str(c.data or "") for c in b.getCommands())
    cur = [[WOLF, FIRE]]
    bridge.put("pets:fn:hud", JProxy("java.util.function.Function", dict={"apply": lambda a: SA(cur[0])}))
    h = HM(pr)
    mBuild.invoke(h, UCB())
    mFill.invoke(h, UCB(), False)
    cur[0] = [PFIRE, HORSE]
    K.check(bool(mFill.invoke(h, UCB(), False)), "P38 HUD the block moves to the pet card = a re-send (the shape)")
    h = HM(pr)          # a re-send = the HUD is built again (as HudMain's caller does)
    mBuild.invoke(h, UCB())
    mFill.invoke(h, UCB(), False)
    cur[0] = [PFIRE.replace("|84|", "|30|"), HORSE]
    b = UCB()
    re_ = bool(mFill.invoke(h, b, False))
    K.check(not re_ and "30 / 120" in allc(b), "P38 HUD a health change of the pet-slot dragon = values only, no re-send")
    K.save()


def run_e2e(out, jar, scratch, _home):
    from jpype import JClass, JProxy
    S = T337._setup(out, scratch, [B.SERVER_JAR, jar, PETS], "e38")
    K, H, u, bridge = S["K"], S["H"], S["u"], S["bridge"]
    P = lambda n: JClass("com.skyy.pets." + n)
    Paths = JClass("java.nio.file.Paths")
    P("PetsLog").LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "e38-mods")
    os.makedirs(mods, exist_ok=True)
    P("PetsCfg").load(Paths.get(mods))
    P("PetStore").ROOT = Paths.get(os.path.join(mods, "Skyy_SkyyPets"))
    P("PetStore").DIR = P("PetStore").ROOT.resolve("pets")
    P("PetsEng").API = JProxy("com.skyy.pets.PetsApi", dict={"online": lambda: None, "byName": lambda n: None, "nameOf": lambda x: "Skyy", "tell": lambda a, b, c: None})
    key = str(P("PetStore").pkey(u))
    P("PetStore").KEYOF.put(u, key)
    r = P("PetStore").get(key)
    r.set("starter", "1")
    pid = str(P("PetOps").create(r, None, "DragonFire", 4, 34, 55, "test", "harness", False))
    r.set("active.1", pid)
    bridge.put("pets:fn:hud", P("PetHudFn")())
    raw = [str(x) for x in bridge.get("pets:fn:hud").apply(u)]
    m = [None if x is None else str(x) for x in H("Widgets").petsModelU(u)]
    K.check(raw[0].split("|")[10] == "-" and raw[0].split("|")[12] == "Bite", "E2E the real SkyyPets 0.4.27 sends health '-' (not out) + Bite on the PET slot line: %s" % raw[0])
    K.check("q" in m[21] and m[2] == "Fire Dragon" and m[14] == "-" and m[16] == "Bite", "E2E ... the widget shows it under the pet card: %s %s" % (m[21], m[14:18]))
    K.save()


EXPECT = {"Widgets": ["~m petsBody", "~m petsH", "~m petsModelOf"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"]}
if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD, PKG, SCRATCH, EXPECT, [], [("static", run_static), ("p37", T337.run_p37), ("p38", run_p38), ("e2e", run_e2e), ("live", T337.run_live)],
           os.path.abspath(__file__), live=(T337.LIVE_DIR, "Skyy_SkyyHud"))
