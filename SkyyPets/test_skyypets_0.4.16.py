"""Harness for SkyyPets 0.4.16 (the hatch reels always finish + rendered Dog / Corgi portraits; tools/pets_0_4_16_patch.py). Build first:
    python tools/pets_0_4_16_patch.py && python SkyyPets/build_skyypets_0.4.16.py
    python SkyyPets/test_skyypets_0.4.16.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; no class / system / command added; line endings kept; the jar: no entry added or
                 removed except the two new portrait PNGs; the changed non-class entries = manifest.json + the two portrait item JSONs; the row
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.15 -> 0.4.16, engine-access audit
  RL    EXECUTED the full roll through the REAL chain (HytaleServer.SCHEDULED_EXECUTOR -> PetWorld.execute -> the stage world's task queue
                 drained like a world thread -> tick -> the next task), opened the way the Hatchery opens it (PetHatchery.OPENER): every
                 rarity 1-6 (Mythic incl.) at 14 frames, the boundaries 8 / 24 frames, the default 3 s speed: reel 1 then reel 2 then the
                 result card, exactly f1 + f2 - 1 frame updates + ONE result packet, ONE reveal line, the strips stop on the pet / its
                 rarity, the watchdog afterwards = a no-op; reel 2 shows pictures (not empty cells) while reel 1 spins; THE SCREENSHOT
                 STALL (every frame task lost at the last pet-reel frame) and a stall from frame 0 -> the watchdog shows the result after
                 the roll length + pets.hatch.stallSeconds (one WARN); a late frame; a frame that throws; a world switch mid-roll (the
                 frames follow the player's current world); Skip mid-roll = ONE packet, then silence; Esc (another page) mid-roll = the
                 reveal, no more frames; the hatch record (pet, hatch.unseen) untouched by the animation
  PT    the jar: every pet kind (44, dragons incl.) has Skyy_PetIcon_<kind> whose icon is its OWN PNG in the jar (Icons/ItemsGenerated),
                 unique, never a vanilla item icon (no tool / sword stand-in); Dog + Corgi are the new renders (64 x 64, mostly opaque body);
                 the 6 rarity tokens (Mythic incl.) have their gem icons + quality; EXECUTED PetsPage.iconOf / PetHatchPage.portraitOf for
                 every kind; the starter page reads the portrait
  sl/mig/dr/t/r/m/f/dg/vw/st/el410/live  0.4.15's phases EXECUTED on this jar
NOT COVERED (UNVERIFIED in game): the real client's look of the frames and of the rendered portraits; a world hop that fails on a live
server (the code path is the same as before plus the warn; the page then finishes on the next click).
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util, subprocess, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "pets0416", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s415 = importlib.util.spec_from_file_location("test_skyypets_0_4_15", os.path.join(HERE, "test_skyypets_0.4.15.py"))
T415 = importlib.util.module_from_spec(_s415)
_s415.loader.exec_module(T415)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T414, T413, T412, T411, T410, T44, T41 = T415.T414, T415.T413, T415.T412, T415.T411, T415.T410, T415.T44, T415.T41

VERSION = "0.4.16"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.15.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.15.py")
PATCH = os.path.join(TOOLS, "pets_0_4_16_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T415, T414, T413, T412, T411, T410, T44):
    _m.PKG = PKG
for _m in (T415, T414, T413, T412, T411):
    _m.JAR, _m.OLD_JAR = JAR, OLD_JAR
T414.GEN = GEN
T415.GEN = GEN
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # the kit's row tables (+ the stall row)
    "PetsCfg": ["+f STALL_S", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"],
    "PetsMigP5": ["~m mgLog", "~m run"], "PetsMigS2": ["~m run"],                                     # VERSION strings
    "PetHatchPage": ["+f STALLS", "+f due", "+m armDog", "+m expectMs", "+m finish", "+m hop", "+m step", "+m watch", "+m worldNow",
                     "~<clinit>", "~m begin", "~m build", "~m go", "~m handleDataEvent", "~m tick"],
    "PetReel": ["+f dog", "~m run"],
    "PetsPage": ["~m build"],
    "SkyyPetsPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
NEW_PNG = ["Common/Icons/ItemsGenerated/Skyy_PetIcon_Corgi.png", "Common/Icons/ItemsGenerated/Skyy_PetIcon_Dog.png"]
PORT_JSON = ["Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_Corgi.json", "Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_Dog.json"]


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + the two new portraits (PNG + item JSON)"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == sorted(["manifest.json"] + NEW_PNG + PORT_JSON), "C: non-class entries changed = manifest.json + the Dog / Corgi portraits: %s" % sorted(got))
    return _eq00(self, got, want, what)


HK.Child.eq = _eq


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.16 - build script') and g.count('VERSION = "0.4.16"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls("),
            "S no class, system or command added")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(z.namelist()) - set(oz.namelist())), NEW_PNG, "S the only new entries = the Dog + Corgi portraits")
    K.eq(sorted(set(oz.namelist()) - set(z.namelist())), [], "S no entry removed")
    ch = sorted(n for n in set(z.namelist()) & set(oz.namelist()) if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(ch, ["Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_Corgi.json", "Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_Dog.json", "manifest.json"],
         "S the changed non-class entries = the 2 portrait items + manifest.json")
    K.check('("pets.hatch.stallSeconds", "Reel stall fallback", "eggs", "int", "5", "1", "60", "", "s", "live,adv"' in g, "S the stall row (int 1-60 s, default 5, adv)")
    hatch_core = ("public static Object[] hatch(", "public static boolean reveal(java.util.UUID u", "public static int unseen(java.util.UUID u")
    for hc in hatch_core:
        if hc in o:
            a0 = o.index(hc)
            a1 = g.index(hc)
            K.check(g[a1:a1 + 3000] == o[a0:a0 + 3000], "S the hatch itself untouched: %s" % hc)
    K.save()


# ======================================================================================================== RL: the roll, EXECUTED
def run_rl(out, jar, scratch, _home):
    from jpype import JClass, JProxy
    import hub_tab_kit as HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Egg, Page, HPage, Reel, Hy, Eng, Defs, PK = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetEgg"), P_("PetsPage"),
                                                                     P_("PetHatchPage"), P_("PetReel"), P_("PetHatchery"), P_("PetsEng"), P_("PetEggDefs"), P_("PetKind"))
    Paths, UUID, Integer = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Integer")
    OA = JClass("java.lang.Object[]")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "stage-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    Hy.OPENER = P_("PetHatchOpen")()
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000616"), "Roller")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "123")
    told = []
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, [str(u1)]), "byName": lambda n: u1 if str(n) == "Roller" else None,
                                            "nameOf": lambda u: "Roller", "tell": lambda u, t, c: told.append(str(t))})
    K.check(str(Cfg.HATCH_ANIM) == "reel" and int(Cfg.STALL_S) == 5, "RL defaults: reels on, pets.hatch.stallSeconds 5 (%s, %s)" % (Cfg.HATCH_ANIM, Cfg.STALL_S))
    W1 = Eng.worldObj(P1.st)
    K.check(W1 is not None, "RL the stage player has a world")
    ids = [str(x) for x in Defs.IDS]
    CATS = [str(x) for x in Defs.CATS]

    def egg_of(cat, rar):
        for i in ids:
            if int(Defs.catOfId(i)) >= 0 and CATS[int(Defs.catOfId(i))] == cat and int(Defs.rarOfId(i)) == rar:
                return i
        raise KeyError((cat, rar))
    seq = [0]

    def cpk():
        return len([p for p in E.sent(P1) if str(p.getClass().getSimpleName()) == "CustomPage"])

    def start(kind, cat, rar, egg_rar=6):
        """a hatch result as PetHatchery.hatch hands it over (the pet + hatch.unseen saved first) -> the OPENER (the real Hatchery path)"""
        seq[0] += 1
        hid = "h%04d" % seq[0]
        pid = str(Ops.createR(r1, None, kind, rar, 1, 0, 0, "egg", "harness", False))
        egg = egg_of(cat, egg_rar)
        r1.set("hatch.unseen." + hid, "%s|%s|%d" % (egg, kind, rar))
        res = OA(["+You hatched a %s %s!" % (PK.rarityName(rar), kind), hid, pid, kind, Integer(rar)])
        ok = bool(Hy.OPENER.apply(OA([P1.pr, P1.ref, P1.st, egg, res])))
        E.pump(P1)
        pg = E.pg(P1)
        return ok, pg, hid, pid

    def drive(pg, secs, drop=None, world=None, stop=True, hook=None):
        """drain the world's task queue like its thread does until the roll ends (or secs); drop(task) = lose that task (a stall)"""
        w = world or W1
        t0 = time.time()
        ran = 0
        while time.time() - t0 < secs:
            if hook is not None:
                hook(pg)
            tk = None if w.tasks is None else w.tasks.poll()
            if tk is None:
                if stop and int(pg.view) != 1:
                    break
                time.sleep(0.002)
                continue
            if drop is not None and drop(tk):
                continue
            tk.run()
            ran += 1
            E.pump(P1)
        return time.time() - t0, ran

    def is_frame(tk):
        return str(tk.getClass().getSimpleName()) == "PetReel" and not bool(tk.dog)

    def unseen_left(hid):
        return r1.get("hatch.unseen." + hid) is not None

    # ---------------------------------------------------------------- every rarity + the boundaries, through the real chain
    Cfg.REEL_S = 1.0
    runs = [("Warthog", "Mining", r, 14) for r in range(1, 7)] + [("Rabbit", "Farming", 6, 8), ("Warthog", "Mining", 6, 24)]
    for kind, cat, rar, fr in runs:
        Cfg.REEL_FRAMES = fr
        told.clear()
        f0, st0, c0 = int(HPage.FRAMES), int(HPage.STALLS), cpk()
        ok, pg, hid, pid = start(kind, cat, rar)
        tag = "%s %s @%d frames" % (PK.rarityName(rar), kind, fr)
        if not K.check(ok and pg is not None and str(pg.getClass().getName()) == PKG + "PetHatchPage" and int(pg.view) == 1 and int(pg.due) > 0,
                       "RL %s: the reel page opens spinning, the watchdog armed" % tag):
            continue
        f1, f2 = int(pg.f1), int(pg.f2)
        K.check(f1 == fr and f2 == fr - 2, "RL %s: %d + %d frames" % (tag, f1, f2))
        if rar == 6 and fr == 14:
            cm, _ev = HT.build(pg, P1)
            s = dict((s_, d) for ty, s_, t, d in cm if ty == "Set")
            K.check(all("Skyy_PetRarity_" in str(s.get("#SkyyHtB%d.Slots" % c)) for c in range(5)) and "?" in str(s.get("#SkyyHtBN.Text")),
                    "RL while reel 1 spins, reel 2 shows rarity PICTURES (not empty cells) + '?': %s" % [str(s.get("#SkyyHtB%d.Slots" % c))[:60] for c in range(2)])
        exp = int(pg.expectMs()) / 1000.0
        el, ran = drive(pg, exp + 6.0)
        K.check(int(pg.view) == 2 and int(pg.gen) > 0, "RL %s: reel 1 -> reel 2 -> the result card (%.2f s, expected %.2f s)" % (tag, el, exp))
        K.eq(int(HPage.FRAMES) - f0, f1 + f2 - 1, "RL %s: every frame drawn once (f1 + f2 - 1)" % tag)
        K.eq(cpk() - c0, 1 + f1 + f2 - 1 + 1, "RL %s: the page + the frames + ONE result packet" % tag)
        K.check(0.5 * exp <= el <= exp + 2.0, "RL %s: the roll took its own length (%.2f s / %.2f s)" % (tag, el, exp))
        K.check(str(pg.s1[f1 + 1]) == str(HPage.portraitOf(kind)) and str(pg.s2[f2 + 1]) == str(Defs.token(rar)), "RL %s: the strips stop on the pet + its rarity" % tag)
        cm, _ev = HT.build(pg, P1)
        s = dict((s_, d) for ty, s_, t, d in cm if ty == "Set")
        K.check(str(Defs.token(rar)) in str(s.get("#SkyyHtT.Slots")) and str(HPage.portraitOf(kind)) in str(s.get("#SkyyHtR.Slots"))
                and ('"%s %s"' % (PK.rarityName(rar), Egg.kindName(kind))) in str(s.get("#SkyyHtResN.Text")) and "You hatched a" in str(s.get("#SkyyHtStatus.Text")),
                "RL %s: the result card (portrait, rarity picture, name, status): %s" % (tag, [str(s.get(x))[:80] for x in ("#SkyyHtT.Slots", "#SkyyHtR.Slots", "#SkyyHtResN.Text", "#SkyyHtStatus.Text")]))
        K.check(len([t for t in told if "You hatched a" in t]) == 1 and not unseen_left(hid) and bool(r1.has(pid)), "RL %s: ONE reveal line; the pet stays saved" % tag)
        # the watchdog after a normal end: a no-op
        c1 = cpk()
        Cfg.STALL_S = 1
        drive(pg, 1.4, stop=False)
        Cfg.STALL_S = 5
        K.check(int(HPage.STALLS) == st0 and cpk() == c1 and len([t for t in told if "You hatched a" in t]) == 1 and int(pg.view) == 2,
                "RL %s: the watchdog after a finished roll does nothing" % tag)
    # the default speed (3 s per reel), Mythic
    Cfg.REEL_S, Cfg.REEL_FRAMES = 3.0, 14
    told.clear()
    ok, pg, hid, pid = start("Warthog", "Mining", 6)
    exp = int(pg.expectMs()) / 1000.0
    el, _r = drive(pg, exp + 6.0)
    K.check(int(pg.view) == 2 and 5.0 <= exp <= 7.0 and el <= exp + 2.0 and len([t for t in told if "You hatched a Mythic" in t]) == 1,
            "RL the default 3 s reels: a Mythic roll ends on its own (%.2f s, expected %.2f s)" % (el, exp))
    Cfg.REEL_S = 1.0
    # ---------------------------------------------------------------- THE SCREENSHOT: frames lost at the last pet-reel frame
    for where, cond in (("at the last pet-reel frame (Skyy's screenshot)", lambda p: int(p.phase) == 1 and int(p.frame) == int(p.f1) - 1),
                        ("from frame 0", lambda p: True)):
        told.clear()
        Log.LINES.clear()
        st0 = int(HPage.STALLS)
        Cfg.STALL_S = 1
        ok, pg, hid, pid = start("Warthog", "Mining", 6)
        exp = int(pg.expectMs()) / 1000.0
        el, _r = drive(pg, exp + 5.0, drop=lambda tk, p=pg, c=cond: is_frame(tk) and c(p))
        Cfg.STALL_S = 5
        K.check(int(pg.view) == 2 and int(HPage.STALLS) == st0 + 1 and exp + 0.8 <= el <= exp + 3.0,
                "RL a stall %s: the watchdog shows the result after the roll + 1 s (%.2f s, roll %.2f s)" % (where, el, exp))
        K.check(len([t for t in told if "You hatched a Mythic Warthog" in t]) == 1 and not unseen_left(hid) and bool(r1.has(pid)), "RL ... ONE reveal line, the pet saved")
        K.check(where != "from frame 0" or int(pg.phase) == 1, "RL (the frame-0 stall really stopped in reel 1)")
        cm, _ev = HT.build(pg, P1)
        s = dict((s_, d) for ty, s_, t, d in cm if ty == "Set")
        K.check('"Mythic Warthog"' in str(s.get("#SkyyHtResN.Text")), "RL ... the result card")
    K.check(len([l for l in Log.LINES if "stopped before its end" in str(l)]) <= 1, "RL the stall WARN is written once per server run")
    # a late frame (past the deadline) -> the result
    told.clear()
    st0 = int(HPage.STALLS)
    ok, pg, hid, pid = start("Warthog", "Mining", 5)
    drive(pg, 0.3, stop=True)
    pg.due = 1
    el, _r = drive(pg, 3.0)
    K.check(int(pg.view) == 2 and int(HPage.STALLS) == st0 + 1 and len([t for t in told if "You hatched a Legendary" in t]) == 1, "RL a frame after the deadline -> the result + ONE line")
    # a frame that throws -> the result
    told.clear()
    ok, pg, hid, pid = start("Warthog", "Mining", 4)
    el, _r = drive(pg, 5.0, hook=lambda p: setattr(p, "s2", None) if int(p.phase) == 2 and int(p.frame) == 2 else None)
    K.check(int(pg.view) == 2 and len([t for t in told if "You hatched a Epic" in t]) == 1, "RL a frame that throws (reel 2 strip gone) -> the result + ONE line")
    # a world switch mid-roll: the frames follow the player's CURRENT world
    told.clear()
    ok, pg, hid, pid = start("Warthog", "Mining", 3)
    drive(pg, 0.25, stop=True)
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    es = P1.st.getExternalData()
    fw = HT.jf(ESc.class_, "world")
    fw.set(es, E.W2)
    n2 = [0]

    def drop_w1(tk):
        return False
    el, ran2 = drive(pg, 5.0, world=E.W2)
    fw.set(es, E.W1)
    drive(pg, 0.2, stop=False)
    K.check(int(pg.view) == 2 and ran2 > 3 and len([t for t in told if "You hatched a Rare" in t]) == 1, "RL a world switch mid-roll: the frames run on the new world and end (%d tasks there)" % ran2)
    # Skip mid-roll = ONE packet, then silence
    told.clear()
    ok, pg, hid, pid = start("Warthog", "Mining", 6)
    drive(pg, 0.3, stop=True)
    c0, f0 = cpk(), int(HPage.FRAMES)
    pg.handleDataEvent(P1.ref, P1.st, '{"a":"skip"}')
    E.pump(P1)
    c1 = cpk()
    drive(pg, 1.5, stop=False)
    K.check(int(pg.view) == 2 and c1 - c0 == 1 and cpk() == c1 and int(HPage.FRAMES) == f0 and len([t for t in told if "You hatched a Mythic" in t]) == 1,
            "RL Skip mid-roll: ONE packet (the result), no frame after it, ONE line (%d packets)" % (c1 - c0))
    # Esc / another page mid-roll: the reveal, no more frames
    told.clear()
    ok, pg, hid, pid = start("Warthog", "Mining", 2)
    drive(pg, 0.3, stop=True)
    P1.pm.openCustomPage(P1.ref, P1.st, Page(P1.pr))
    E.pump(P1)
    f0 = int(HPage.FRAMES)
    drive(pg, 2.5, stop=False)
    K.check(int(HPage.FRAMES) == f0 and len([t for t in told if "You hatched a Uncommon" in t]) == 1 and not unseen_left(hid),
            "RL another page mid-roll (Esc): the reveal line at once, no more frames")
    # the quick mode / the skip toggle still bypass the reels (the result at once)
    Cfg.HATCH_ANIM = "quick"
    told.clear()
    ok, pg, hid, pid = start("Warthog", "Mining", 6)
    K.check(int(pg.view) == 2 and int(pg.due) == 0 and len([t for t in told if "You hatched a Mythic" in t]) == 1, "RL quick mode: the result at once, no watchdog")
    Cfg.HATCH_ANIM = "reel"
    sev = [str(l) for l in Log.LINES if "SEVERE" in str(l)]
    K.check(int(HPage.STALLS) >= 3 and not sev, "RL no SEVERE: %s" % sev[:3])
    K.save()


# ======================================================================================================== PT: the portraits
def run_pt(out, jar, scratch, _home):
    from jpype import JClass
    import skyyart as SA
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Defs, HPage = P_("PetsCfg"), P_("PetEggDefs"), P_("PetHatchPage")
    _m = os.path.join(scratch, "pt-mods")
    os.makedirs(_m, exist_ok=True)
    Cfg.load(JClass("java.nio.file.Paths").get(_m))
    z = zipfile.ZipFile(jar)
    az = SA.assets()
    vanilla_item_icons = set()
    for n in az.namelist():
        if n.startswith("Common/Icons/Items") and n.endswith(".png"):
            vanilla_item_icons.add(hashlib.sha256(az.read(n)).hexdigest())
    kinds = [str(k.id) for k in Cfg.KINDS]
    K.check(len(kinds) == 44, "PT 44 pet kinds (dragons incl.): %d" % len(kinds))
    seen = {}
    bad = []
    for k in kinds:
        iid = str(Defs.portrait(k))
        if iid != "Skyy_PetIcon_" + k or str(HPage.portraitOf(k)) != iid:
            bad.append((k, iid, "id"))
            continue
        js = json.loads(z.read("Server/Item/Items/SkyyPets/Icons/%s.json" % iid).decode("utf-8"))
        ic = js.get("Icon", "")
        if ic != "Icons/ItemsGenerated/%s.png" % iid or ("Common/" + ic) not in z.namelist():
            bad.append((k, ic, "icon path"))
            continue
        h = hashlib.sha256(z.read("Common/" + ic)).hexdigest()
        if h in vanilla_item_icons:
            bad.append((k, ic, "a vanilla item icon"))
        if h in seen:
            bad.append((k, ic, "same picture as " + seen[h]))
        seen[h] = k
    K.eq(bad, [], "PT every kind's portrait = its own creature picture in the jar (no tool / sword stand-in, no shared picture)")
    ok = []
    for k in ("Dog", "Corgi"):
        im = SA.png_decode(z.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k))
        cov = sum(1 for y in range(im.h) for x in range(im.w) if im.get(x, y)[3] > 200)
        ok.append((k, im.w, im.h, cov))
    K.check(all(w == 64 and h == 64 and 900 < c < 3000 for _k, w, h, c in ok), "PT Dog + Corgi: rendered 64 x 64 creature pictures: %s" % ok)
    oz = zipfile.ZipFile(OLD_JAR)
    o_dog = json.loads(oz.read("Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_Dog.json").decode("utf-8"))["Icon"]
    K.check("ItemsGenerated/Skyy_PetIcon_Dog" not in o_dog, "PT (0.4.15's Dog portrait was a stand-in item icon: %s)" % o_dog)
    toks = [str(t) for t in Defs.TOKENS]
    tb = []
    for i, t in enumerate(toks):
        js = json.loads(z.read("Server/Item/Items/SkyyPets/Icons/%s.json" % t).decode("utf-8"))
        ic = js.get("Icon", "")
        if not ic or (("Common/" + ic) not in az.namelist() and ("Common/" + ic) not in z.namelist()) or not js.get("Quality"):
            tb.append((t, ic, js.get("Quality")))
    K.check(len(toks) == 6 and toks[5] == "Skyy_PetRarity_Mythic" and not tb, "PT the 6 rarity tokens (Mythic incl.) have their gem icon + quality: %s" % tb)
    g = open(GEN, encoding="utf8").read()
    K.check('String ic = pk == null ? "@ICON@" : (@PKG@.PetEggDefs.portrait(pk.id) != null ? @PKG@.PetEggDefs.portrait(pk.id) : pk.icon);' in g,
            "PT the starter choice page shows the pet portrait")
    K.save()


def run_mig(out, jar, scratch, home):
    f = T414._swap(T415.run_mig, T415, [(r"SkyyPets 0.4.15\t-\tupdate", r"SkyyPets 0.4.16\t-\tupdate")])     # the Changes line names this jar
    f(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("rl", run_rl), ("pt", run_pt), ("sl", T415.run_sl), ("mig", run_mig), ("dr", T415.run_dr), ("t", T415.run_t),
                   ("r", T414.run_r), ("m", T412.run_m), ("f", T414.run_f), ("dg", T414.run_dg), ("vw", T411.run_vw), ("st", T414.run_st),
                   ("el410", T414.run_el), ("live", T415.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
