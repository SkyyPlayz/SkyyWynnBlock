"""Harness for SkyyFishing 0.1.8 (THE LINE OVER WATER = beads, REAL MODELS for the 23 tackle items, THE FISH BRIDGE for SkyySacks 0.8.10;
tools/fishing_0_1_8_patch.py) = the 0.1.7 harness's phases on the 0.1.8 jar + F18 + ENG.
Build first: python tools/fishing_0_1_8_patch.py && python SkyyFishing/build_skyyfishing_0.1.8.py

    python SkyyFishing/test_skyyfishing_0.1.8.py [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.1.7 -> 0.1.8 (exactly the planned members), engine-access audit
  F18 EVERY NEW CODE PATH (one child JVM):
      ASSET AUDIT  every item JSON in the jar names a Model + Texture (a block item: CustomModel + its textures) that exists in the jar
                   or in Assets.zip (= no "Missing model for item"); the 23 tackle items have exactly the planned vanilla looks; the
                   bead particle system + spawner are ours, the texture is in Assets.zip; the non-class entries that changed vs 0.1.7
                   are exactly the 23 tackle JSONs, the 2 bead files and the manifest
      BEADS        beadPts on a real 9-point sagging line: first bead 0.25 down the line, every bead ON the line, sizes grow with the
                   distance and are never thinner than the line, the gap = size x beadGap (min 0.06); a too-small gap is capped at
                   120 beads with the FAR END still covered (the gap widens); beadPackets = SpawnParticleSystem(our id, the bead's
                   position, no rotation, scale = size / 0.1, no colour, 0.45 s); sendBeads: the near stand-in player gets ONE batch,
                   the far one nothing, a non-player entry skipped; beadDue (fish.line.beadSec); lineTo = the line + the beads, beads
                   off = the line only; drawLine through FishEngApi on a stand-in world
      BRIDGE       questInit puts fishing:fn:fishOf / fishDoc / pond; a caught fish (makeFish) -> its metadata JSON -> fishOf =
                   "grams,mm,catcher" -> fishDoc = the same metadata (BsonDocument equal) for every species; no metadata = "";
                   foreign metadata / an extra field in our document / not a fish / bad entries = null; a catcher name with , ; | =
                   is cleaned; pond(UUID) = the Pond Fish count of the active profile (FishStore on a scratch folder); wrong
                   argument types = null
  ENG THE ENGINE ASSET VALIDATORS (the 0.1.2 harness's engine_boot: the vanilla pack loaded store by store, then THE JAR as its own
      pack): no failed store, no SEVERE / WARNING line; the 23 tackle items are in the Item store with their model (toPacket), the bead
      particle system is in the ParticleSystem store (toPacket); NEGATIVE CONTROL: an item whose Model file is missing is refused
  R / X / Q / ST  the 0.1.7 harness's phases on this jar (reel, exec, quest = Marlow's starter + gear:fn:pole, live = start twice on a
      scratch COPY of the live Skyy_SkyyFishing); 0.1.7's static cast check reads its own generated script (unchanged in 0.1.8)
Not testable without the game (UNVERIFIED): that the client draws the beads OVER water (particles are drawn after the water; the vanilla
splash shows there), the bead size the packet's scale gives, how the tackle looks in hand / on the ground.
Scratch: tools/dev/scratch/fish018/fishing (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.8"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fish018", "fishing")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_1_7", os.path.join(HERE, "test_skyyfishing_0.1.7.py"))
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)
T15 = T17.T15
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
EXPECT = {
    "FishEngApi": ["+m beadSize", "+m beadWalk", "+m beadPts", "+m beadPackets", "+m sendBeads", "+m beadDue", "+m lineTo", "~m drawLine",
                   "+f BEAD_PKTS", "+f BEADAT", "~<clinit>"],
    "FishRig": ["+m fishOf", "+m fishDoc"],
    "FishQuestFn": ["~m apply"],
    "FishBridge": ["~m questInit"],
    "FishCfg": ["+f BEADS", "+f BEAD_SEC", "+f BEAD_SIZE", "+f BEAD_GAP", "~<clinit>", "~m applyScalars", "~m applyAll", "~m seed"],
    "FishDefs": ["+f BEAD", "+f BEAD_BASE", "+f BEAD_LIFE", "+f BEAD_MAX", "+f BEAD_ANG", "+f BEAD_START", "+f BEAD_MINSTEP"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
    "FishCmds": ["~m admin"], "SkyyFishingPlugin": ["~m setup"],          # the version text (as in every round)
}
ADDED = []
TACKLE = {"Reel": "Ingredient_Gadget_Assembly", "Barbed": "Ingredient_Stud_Iron", "LostProperty": "Ingredient_Scraps", "Lure": "Tool_Trap_Bait",
          "Braided": "Ingredient_Bolt_Linen", "Steady": "Ingredient_Bolt_Cotton", "Twin": "Ingredient_Spider_Silk", "Scholars": "Ingredient_Bolt_Silk",
          "Weighted": "Ingredient_Bar_Iron", "Clean": "Ingredient_Bar_Silver", "Deep": "Ingredient_Bar_Cobalt"}
TACKLE_IDS = (["SkyyFishing_Reel_%s" % t for t in ("Bamboo", "Copper", "Iron")]
              + ["SkyyFishing_%s_%s_%s" % (k, n, r) for k, ns in (("Hook", ("Barbed", "LostProperty", "Lure")),
                                                                   ("Line", ("Braided", "Steady", "Twin", "Scholars")),
                                                                   ("Sinker", ("Weighted", "Clean", "Deep"))) for n in ns for r in ("I", "II")])
BEAD = "SkyyFishing_Line_Bead"
# the 0.1.7 harness's checks that test what 0.1.8 changes ON PURPOSE
T17.WAIVE = T17.WAIVE + (
    ("C: non-class entries changed", "0.1.8 by design: the 23 tackle item JSONs (+ Model / Texture) and the 2 bead particle files - F18 checks the exact list"),
)


def _vanilla_items(az):
    idx = {}
    for n in az.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            idx[n.rsplit("/", 1)[1][:-5]] = n
    return idx


def _vlook(az, idx, iid):
    v = json.loads(az.read(idx[iid]).decode("utf-8-sig"))
    vp = json.loads(az.read(idx[v["Parent"]]).decode("utf-8-sig")) if "Parent" in v else {}
    return v.get("Model") or vp.get("Model"), v.get("Texture") or vp.get("Texture")


def asset_audit(K, jar):
    az = zipfile.ZipFile(AZ_PATH)
    azn = set(az.namelist())
    jz = zipfile.ZipFile(jar)
    jn = set(jz.namelist())
    have = lambda p: ("Common/" + p) in jn or ("Common/" + p) in azn
    bad, n = [], 0
    for nm in sorted(jn):
        if not (nm.startswith("Server/Item/Items/") and nm.endswith(".json")):
            continue
        n += 1
        d = json.loads(jz.read(nm).decode("utf-8-sig"))
        if "BlockType" in d:
            bt = d["BlockType"]
            texs = [t.get("Texture") for t in bt.get("CustomModelTexture", [])]
            if not bt.get("CustomModel") or not have(bt["CustomModel"]) or not texs or not all(t and have(t) for t in texs):
                bad.append((nm, "block", bt.get("CustomModel"), texs))
            continue
        if not d.get("Model") or not d.get("Texture") or not have(d["Model"]) or not have(d["Texture"]):
            bad.append((nm, d.get("Model"), d.get("Texture")))
        for c in (d.get("ItemAppearanceConditions") or {}).values():
            for cc in c:
                if not have(cc["Model"]) or not have(cc["Texture"]):
                    bad.append((nm, "look", cc["Model"]))
    K.check(n == 42 and not bad, "F18 ASSET AUDIT: every one of the %d item JSONs names a Model + Texture (blocks: CustomModel + textures) found in "
            "the jar or Assets.zip - no 'Missing model for item': %s" % (n, bad[:4]))
    idx = _vanilla_items(az)
    wrong = []
    for iid in TACKLE_IDS:
        nm = [x for x in jn if x.endswith("/%s.json" % iid) and x.startswith("Server/Item/Items/")]
        d = json.loads(jz.read(nm[0]).decode("utf-8-sig")) if len(nm) == 1 else {}
        kind = "Reel" if iid.startswith("SkyyFishing_Reel_") else iid.split("_")[2]
        want = _vlook(az, idx, TACKLE[kind])
        if (d.get("Model"), d.get("Texture")) != want or not d.get("Icon", "").startswith("Icons/ItemsGenerated/" + iid):
            wrong.append((iid, d.get("Model"), want))
        if any(("Common/" + p) in jn for p in want):
            wrong.append((iid, "vanilla file copied into the jar"))
    K.check(len(TACKLE_IDS) == 23 and not wrong, "F18: the 23 tackle items carry the planned vanilla looks BY PATH (nothing copied), their own icons stay: %s" % wrong[:3])
    sysp, spw = "Server/Particles/SkyyFishing/%s.particlesystem" % BEAD, "Server/Particles/SkyyFishing/Spawners/%s.particlespawner" % BEAD
    ps, sw = json.loads(jz.read(sysp)), json.loads(jz.read(spw))
    K.check(ps["Spawners"] == [{"SpawnerId": BEAD}] and sw["TotalParticles"] == {"Min": 1, "Max": 1} and ("Common/" + sw["Particle"]["Texture"]) in azn
            and sysp not in azn and spw not in azn and sw["ParticleRotationInfluence"] == "Billboard" and "InitialVelocity" not in sw
            and abs(sw["ParticleLifeSpan"]["Max"] - 0.45) < 1e-9,
            "F18: the bead particle system + spawner are ours (new paths): one still billboard dot, 0.45 s, a vanilla texture by path")
    za = zipfile.ZipFile(OLD_JAR)
    ea = [x for x in za.namelist() if not x.endswith(".class")]
    eb = [x for x in jn if not x.endswith(".class")]
    ed = sorted(x for x in set(ea) | set(eb) if x not in ea or x not in eb or za.read(x) != jz.read(x))
    want_ed = sorted(["manifest.json", sysp, spw] + ["Server/Item/Items/SkyyFishing/%s/%s.json" % ("Parts" if not i.startswith("SkyyFishing_Reel_") else "Parts", i)
                                                    for i in TACKLE_IDS])
    K.eq(ed, want_ed, "F18: the non-class entries that changed vs 0.1.7 = the 23 tackle JSONs + the 2 bead files + the manifest")


def run_f18(out, jar, scratch, _home):
    from jpype import JClass, JArray, JFloat, JString, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    asset_audit(K, jar)
    P = lambda n: JClass(PKG + n)
    EA, Cfg, Defs, Rig, Brg, Store, QFN, Log = (P("FishEngApi"), P("FishCfg"), P("FishDefs"), P("FishRig"), P("FishBridge"), P("FishStore"),
                                               P("FishQuestFn"), P("FishLog"))
    Log.SINK = JClass("java.util.ArrayList")()
    D = JArray(JClass("double"))
    # ---------------- BEADS: a real sagging line (FishCore.linePts' shape: tip high on the shore, bobber 12 blocks out on the water)
    tip, bob = (0.5, 66.6, 0.0), (12.5, 63.9, 0.0)
    n = 9
    pts = []
    for i in range(n):
        u = i / (n - 1.0)
        pts += [tip[0] + (bob[0] - tip[0]) * u, tip[1] + (bob[1] - tip[1]) * u - 0.72 * 4 * u * (1 - u), 0.0]
    Cfg.LINE_THICK = 0.03
    b = list(EA.beadPts(D(pts), n, 1.5, 1.0, 3.0, 120))
    k = len(b) // 4
    segs = [(pts[3 * i:3 * i + 3], pts[3 * i + 3:3 * i + 6]) for i in range(n - 1)]

    def dist_to_line(q):
        best = 9e9
        for a, c in segs:
            ab = [c[j] - a[j] for j in range(3)]
            L2 = sum(x * x for x in ab)
            t = max(0.0, min(1.0, sum((q[j] - a[j]) * ab[j] for j in range(3)) / L2))
            best = min(best, sum((q[j] - a[j] - ab[j] * t) ** 2 for j in range(3)) ** 0.5)
        return best
    beads = [b[4 * i:4 * i + 4] for i in range(k)]
    on = max(dist_to_line(x[:3]) for x in beads)
    first = sum((beads[0][j] - pts[j]) ** 2 for j in range(3)) ** 0.5
    sizes = [x[3] for x in beads]
    gaps = [sum((beads[i + 1][j] - beads[i][j]) ** 2 for j in range(3)) ** 0.5 for i in range(k - 1)]
    gap_ok = all(g_ <= max(0.06, sizes[i] * 3.0) + 1e-6 for i, g_ in enumerate(gaps))
    last = sum((beads[-1][j] - pts[-3 + j]) ** 2 for j in range(3)) ** 0.5
    K.check(20 <= k <= 120 and on < 1e-9 and abs(first - 0.25) < 1e-6 and min(sizes) >= 0.03 - 1e-12 and sizes[-1] > sizes[0]
            and all(sizes[i + 1] >= sizes[i] - 1e-12 for i in range(k - 1)) and gap_ok and last < 0.5,
            "F18 BEADS: %d beads on a 12-block sagging line: all ON the line (max off %.2g), the first 0.25 from the tip, sizes %.3f..%.3f grow "
            "with distance (never under the line's 0.03), gaps <= size x 3 (min 0.06), the last %.2f from the bobber" % (k, on, sizes[0], sizes[-1], last))
    b2 = list(EA.beadPts(D(pts), n, 1.5, 1.0, 1.0, 40))
    k2 = len(b2) // 4
    last2 = sum((b2[-4 + j] - pts[-3 + j]) ** 2 for j in range(3)) ** 0.5
    K.check(k2 <= 40 and k2 >= 25 and last2 < 1.0, "F18 BEADS: a too-small gap is capped (%d <= 40) by WIDENING the gap - the far end (over the water) "
            "is still covered (last bead %.2f from the bobber)" % (k2, last2))
    b3 = list(EA.beadPts(D(pts), n, 1.5, 2.0, 3.0, 120))
    K.check(abs(b3[3] - 2.0 * b[3]) < 1e-9, "F18 BEADS: fish.line.beadSize doubles the size")
    K.check(len(list(EA.beadPts(D(pts), 1, 1.5, 1.0, 3.0, 120))) == 0 and len(list(EA.beadPts(None, 0, 1.5, 1.0, 3.0, 120))) == 0
            and len(list(EA.beadPts(D(pts), n, 1.5, 1.0, 3.0, 0))) == 0, "F18 BEADS: one point / no points / max 0 = no beads")
    pk = list(EA.beadPackets(D(b), JFloat(0.45)))
    SPS = JClass("com.hypixel.hytale.protocol.packets.world.SpawnParticleSystem")
    okp = len(pk) == k and all(SPS.class_.isInstance(p_) and str(p_.particleSystemId) == BEAD and p_.rotation is None and p_.color is None
                                and abs(float(p_.maxDuration) - 0.45) < 1e-6 and abs(float(p_.scale) - beads[i][3] / 0.1) < 1e-4
                                and abs(float(p_.position.x) - beads[i][0]) < 1e-9 and abs(float(p_.position.y) - beads[i][1]) < 1e-9
                                for i, p_ in enumerate(pk))
    K.check(okp, "F18 BEADS: beadPackets = one SpawnParticleSystem per bead (our id, its position, no rotation / colour, scale = size / 0.1, 0.45 s)")
    # stand-in players (the 0.1.2 harness's pattern): a fake PacketHandler records the batches
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fh = jp.makeClass("com.hypixel.hytale.server.core.io.SkyyTestFakeHandler18")
    fh.setSuperclass(jp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    CtF, CtM = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")
    fh.addField(CtF.make("public java.util.ArrayList got;", fh))
    fh.addMethod(CtM.make("public void write(com.hypixel.hytale.protocol.ToClientPacket[] p) { if (this.got == null) this.got = new java.util.ArrayList(); this.got.add(p); }", fh))
    fh.addMethod(CtM.make("public void write(com.hypixel.hytale.protocol.ToClientPacket p) { if (this.got == null) this.got = new java.util.ArrayList(); this.got.add(new com.hypixel.hytale.protocol.ToClientPacket[] { p }); }", fh))
    FH = JClass(fh.toClass(JClass("com.hypixel.hytale.server.core.io.PacketHandler").class_))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, nm):
        kk = c.class_ if hasattr(c, "class_") else c
        while kk is not None:
            try:
                f = kk.getDeclaredField(nm)
                f.setAccessible(True)
                return f
            except Exception:
                kk = kk.getSuperclass()
        raise KeyError(nm)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TRc, V3, R3 = JClass("com.hypixel.hytale.math.vector.Transform"), JClass("org.joml.Vector3d"), JClass("com.hypixel.hytale.math.vector.Rotation3f")
    AL = JClass("java.util.ArrayList")

    def fake_player(x, y, z):
        p_ = us.allocateInstance(PRc.class_)
        h_ = us.allocateInstance(FH.class_)
        h_.got = AL()
        jf(PRc, "transform").set(p_, TRc(V3(x, y, z), R3()))
        jf(PRc, "packetHandler").set(p_, h_)
        return p_, h_
    near, hn = fake_player(3.0, 65.0, 1.0)
    far, hf = fake_player(300.0, 65.0, 1.0)
    plist = AL()
    plist.add(near)
    plist.add(far)
    plist.add(JString("not a player"))
    c0 = int(EA.BEAD_PKTS)
    sent = int(EA.sendBeads(plist, D(b)))
    got = [list(x) for x in hn.got]
    K.check(sent == 1 and len(got) == 1 and len(got[0]) == k and all(SPS.class_.isInstance(p_) for p_ in got[0]) and hf.got.size() == 0
            and int(EA.BEAD_PKTS) == c0 + k and int(EA.sendBeads(plist, D([]))) == 0 and int(EA.sendBeads(None, D(b))) == 0,
            "F18 BEADS: sendBeads - the near player gets ONE batch of %d beads, the far one (300 blocks) nothing, a non-player skipped, nothing "
            "to send = 0" % k)
    U = JClass("java.util.UUID").fromString("00000000-0000-4000-8000-0000000f0180")
    EA.BEADAT.clear()
    Cfg.BEAD_SEC = 0.33
    Cfg.LINE_EVERY = 1          # a fast line: beadSec alone decides (the cadence rule below is checked on its own)
    K.check(bool(EA.beadDue(U, 1000000)) and not bool(EA.beadDue(U, 1000100)) and not bool(EA.beadDue(U, 1000300)) and bool(EA.beadDue(U, 1000320))
            and not bool(EA.beadDue(None, 1000400)) and bool(EA.beadDue(U, 999000)),
            "F18 BEADS: beadDue = every fish.line.beadSec (0.33 s, 20 ms slack) per caster; a clock step back sends at once; no uuid = never")
    # review fix (fish018fix): the bead refresh follows the line refresh - simulate FishCore.line's calls every everyTicks for 3 s and
    # measure how long the line has NO live bead (a bead batch lives BEAD_LIFE s from its send)
    life = int(round(float(Defs.BEAD_LIFE) * 1000))
    dark = {}
    for every in range(1, 31):
        for bs in (0.1, 0.33, 0.4):
            Cfg.LINE_EVERY, Cfg.BEAD_SEC = every, bs
            EA.BEADAT.clear()
            step = every * 1000.0 / 30.0
            sends = [int(round(i * step)) for i in range(int(3000 / step) + 2) if bool(EA.beadDue(U, 7000000 + int(round(i * step))))]
            gap = max([b_ - a_ - life for a_, b_ in zip(sends, sends[1:])] + [0])
            dark[(every, bs)] = gap
    bad_d = dict((k_, v_) for k_, v_ in dark.items() if k_[0] <= 13 and v_ > 0)
    K.check(not bad_d, "F18 FIX: no dark gap between bead batches for every line refresh 1-13 ticks x bead refresh 0.1 / 0.33 / 0.4 s: %s" % bad_d)
    K.check(all(dark[(e_, 0.33)] <= (e_ * 1000.0 / 30.0) - life + 1 for e_ in range(14, 31)),
            "F18 FIX: above 13 ticks the beads are re-sent on EVERY line redraw (the gap is only the redraw interval minus the bead life)")
    Cfg.LINE_EVERY, Cfg.BEAD_SEC = 5, 0.33
    EA.BEADAT.clear()
    s5 = [t_ for t_ in range(0, 2000, 167) if bool(EA.beadDue(U, 8000000 + t_))]
    K.check(s5 == list(range(0, 2000, 334)), "F18 FIX: at the defaults (5 ticks, 0.33 s) beads go out every 2nd redraw as before: %s" % s5)
    hn.got.clear()
    EA.BEADAT.clear()
    Cfg.BEADS = True
    s1 = int(EA.lineTo(plist, U, D(pts), n, JFloat(0.2), 5000000))
    g1 = [list(x) for x in hn.got]
    DDc = JClass("com.hypixel.hytale.protocol.packets.player.DisplayDebug")
    K.check(s1 == 1 and len(g1) == 2 and all(DDc.class_.isInstance(p_) for p_ in g1[0]) and len(g1[0]) == n - 1
            and all(SPS.class_.isInstance(p_) for p_ in g1[1]) and len(g1[1]) == k,
            "F18 BEADS: lineTo = the engine line (8 pieces) AND the beads (%d) to the near player: %s" % (k, [len(x) for x in g1]))
    hn.got.clear()
    s2 = int(EA.lineTo(plist, U, D(pts), n, JFloat(0.2), 5000100))
    K.check(s2 == 1 and hn.got.size() == 1, "F18 BEADS: the next line refresh within beadSec = the line only (the beads still live)")
    hn.got.clear()
    Cfg.BEADS = False
    EA.BEADAT.clear()
    EA.lineTo(plist, U, D(pts), n, JFloat(0.2), 6000000)
    K.check(hn.got.size() == 1 and DDc.class_.isInstance(list(hn.got.get(0))[0]), "F18 BEADS: fish.line.beads off = the line only (0.1.7 exactly)")
    Cfg.BEADS = True
    # drawLine through the real FishEngApi on a stand-in world (its playerRefs = our list)
    WLc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    wl = us.allocateInstance(WLc.class_)
    jf(WLc, "playerRefs").set(wl, plist)
    Ctx = P("FishCtx")
    hn.got.clear()
    EA.BEADAT.clear()
    api = EA()
    api.drawLine(Ctx(U, "Skyy", None, None, None, wl, None), D(pts), n, JFloat(0.2))
    K.check(hn.got.size() == 2, "F18 BEADS: FishEngApi.drawLine (what FishCore.line calls) sends the line + the beads: %d batches" % hn.got.size())
    api.drawLine(Ctx(U, "Skyy", None, None, None, None, None), D(pts), n, JFloat(0.2))
    K.check(hn.got.size() == 2, "F18 BEADS: drawLine without a world sends nothing and never throws")
    # ---------------- BRIDGE
    br = Brg.bridge()
    Brg.questInit()
    fo, fd, fp = br.get("fishing:fn:fishOf"), br.get("fishing:fn:fishDoc"), br.get("fishing:fn:pond")
    K.check(all(f_ is not None and QFN.class_.isInstance(f_) for f_ in (fo, fd, fp)), "F18 BRIDGE: questInit puts fishing:fn:fishOf / fishDoc / pond")
    T15.item_store([str(x) for x in Defs.FISH] + [str(x) for x in Defs.RODS])
    OA = JArray(JClass("java.lang.Object"))
    BD = JClass("org.bson.BsonDocument")
    bad = []
    for sp in range(len(list(Defs.FISH))):
        fid = str(Defs.FISH[sp])
        s_ = Rig.makeFish(sp, 1234 + sp, 456 + sp, "SkyLordPlayz")
        js = str(s_.getMetadata().toJson())
        e = fo.apply(OA([JString(fid), JString(js)]))
        back = fd.apply(OA([JString(fid), e])) if e is not None else None
        if str(e) != "%d,%d,SkyLordPlayz" % (1234 + sp, 456 + sp) or back is None or not BD.parse(back).equals(s_.getMetadata()):
            bad.append((fid, e))
    K.check(not bad, "F18 BRIDGE: every species: makeFish -> metadata JSON -> fishOf 'grams,mm,catcher' -> fishDoc = the SAME metadata (document "
            "+ tooltip): %s" % bad[:3])
    f0 = str(Defs.FISH[0])
    s0 = Rig.makeFish(0, 2000, 500, "A,b;c|d=e")
    e0 = str(fo.apply(OA([JString(f0), s0.getMetadata().toJson()])))
    md = s0.getMetadata().clone()
    md.put("SkyyGear", BD())
    our = s0.getMetadata().get("SkyyFishing").asDocument().clone()
    our.put("x", JClass("org.bson.BsonInt32")(1))
    md2 = s0.getMetadata().clone()
    md2.put("SkyyFishing", our)
    names_bad = [str(fo.apply(OA([JString(f0), Rig.makeFish(0, 2000, 500, nm).getMetadata().toJson()])))
                 for nm in ("A,b", "a;b", "a|b", "a=b", "a" + chr(10) + "b", " Skyy", "Skyy ")]
    K.check(all(x == "None" for x in names_bad), "F18 FIX: a catcher name that cannot round-trip (, ; | = line break, edge spaces) = null "
            "(the fish stays in the inventory): %s" % names_bad)
    K.check(e0 == "None" and str(fo.apply(OA([JString(f0), None]))) == "" and str(fo.apply(OA([JString(f0), JString("{}")]))) == ""
            and fo.apply(OA([JString(f0), md.toJson()])) is None and fo.apply(OA([JString(f0), md2.toJson()])) is None
            and fo.apply(OA([JString("Fish_Bluegill_Item"), s0.getMetadata().toJson()])) is None
            and fo.apply(OA([JString(f0), JString("not json")])) is None,
            "F18 BRIDGE: a catcher with , ; | = is refused (null); no metadata / {} = '' (a plain fish); other metadata, an extra field in our document, "
            "not our fish, broken JSON = null (the Void leaves such a stack alone)")
    K.check(all(fd.apply(OA([JString(f0), JString(x)])) is None for x in ("", "1,2", "0,5,x", "-1,5,x", "a,b,c", "5,-1,x"))
            and fd.apply(OA([JString("Rock_Stone"), JString("100,10,x")])) is None and fd.apply(JString("x")) is None
            and fo.apply(JString("x")) is None and fp.apply(JString("x")) is None,
            "F18 BRIDGE: broken entries / not a fish / wrong argument types = null")
    mods = os.path.join(scratch, "f18-mods")
    os.makedirs(mods, exist_ok=True)
    Store.start(JClass("java.nio.file.Paths").get(mods))
    Store.setPond(str(U), 37)
    pv = fp.apply(U)
    K.check(pv is not None and int(pv) == 37 and JClass("java.lang.Long").class_.isInstance(pv),
            "F18 BRIDGE: fishing:fn:pond(UUID) = the active profile's Pond Fish count as a Long (%s)" % pv)
    K.save()


def run_eng(out, jar, scratch, _home):
    """the 0.1.2 harness's engine_boot (the real asset stores + validators) on the 0.1.8 jar"""
    from jpype import JClass
    K = HK.Child(out)
    sp = importlib.util.spec_from_file_location("t012", os.path.join(HERE, "test_skyyfishing_0.1.2.py"))
    T12 = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(T12)
    T12.JAR, T12.SCRATCH, T12.VERSION = jar, os.path.join(scratch, "eng"), VERSION
    os.makedirs(T12.SCRATCH, exist_ok=True)
    T12._jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)
    E = T12.engine_boot(K)
    bad = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING")]
    for r in bad[:8]:
        print("   ENG:", r[0], r[1][:400].replace("\n", " / "))
    K.check(not E["fail"] and not bad, "ENG: the 0.1.8 jar loads into the real stores as its own pack: no failed store (%s), no SEVERE / WARNING (%d)"
            % (E["fail"], len(bad)))
    ITEM = E["ITEM"]
    miss = []
    for iid in TACKLE_IDS:
        it = ITEM.getAssetMap().getAsset(iid)
        try:
            pk = it.toPacket() if it is not None else None
            mdl = str(pk.model) if pk is not None and pk.model is not None else None
        except Exception as e:
            mdl = "EXC %s" % str(e)[:100]
        if it is None or mdl is None or not mdl.endswith(".blockymodel"):
            miss.append((iid, mdl))
    K.check(not miss, "ENG: the 23 tackle items are in the Item store and their packets carry a model (no 'Missing model'): %s" % miss[:3])
    PSY = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem")
    ps = PSY.getAssetMap().getAsset(BEAD)
    try:
        ps.toPacket()
        pok = True
    except Exception as e:
        pok = str(e)[:150]
    K.check(ps is not None and pok is True, "ENG: the bead particle system is in the ParticleSystem store, toPacket ok: %s" % pok)
    # NEGATIVE CONTROL: an item whose model file is missing is refused (the validators really run)
    zp = os.path.join(scratch, "eng", "ctl.jar")
    base = json.loads(zipfile.ZipFile(jar).read("Server/Item/Items/SkyyFishing/Parts/SkyyFishing_Hook_Barbed_I.json"))
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("Server/Item/Items/SkyyFishCtl/SkyyFishCtl_Model.json", json.dumps(dict(base, Model="Items/SkyyFishCtl_NoSuch.blockymodel")))
    f_, r2 = E["loadpack"](zp, "Skyy:test ctl18", False)
    K.check(bool([r for r in r2 if r[0] == "SEVERE" and "SkyyFishCtl_NoSuch.blockymodel" in r[1]]), "ENG CONTROL: a missing model file is refused (SEVERE)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("f18", run_f18), ("eng", run_eng), ("reel", T17.run_reel), ("exec", T15.run_exec), ("quest", T15.run_quest),
                   ("live", T15.run_live)], script=__file__, live=(T15.LIVE_DIR, "Skyy_SkyyFishing"))
