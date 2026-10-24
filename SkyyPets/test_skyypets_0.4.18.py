"""Harness for SkyyPets 0.4.18 (PET RARITY COLOURS: rarity portrait items with the quality frame in the grids + the hatch result, the
rarity square behind every row icon; tools/pets_0_4_18_patch.py + the kit's static_row(icon_bg=)). Build first:
    python tools/pets_0_4_18_patch.py && python SkyyPets/build_skyypets_0.4.18.py
    python SkyyPets/test_skyypets_0.4.18.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes, 0.4.17's patch still regenerates 0.4.17 byte for byte; no class / system / command
                 added; line endings kept; the jar: the ONLY new entries = the 264 PetFrames item JSONs (each = its kind's portrait JSON +
                 the rarity's Quality, the same picture and name key), no entry removed, changed non-class entries = manifest.json
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.17 -> 0.4.18, engine-access audit
  RC    EXECUTED on the hub stage (real UICommandBuilder pages): PetEggDefs.portraitR / isFramed / eggRar, PetsPage.rbg / cellIcon; the
                 Pets grid cells (rarity portrait, quality background ON; a kind without a portrait = its icon, no frame), the Fuse pets cells,
                 the egg cells (unchanged); the BUILT Pets tab (Pet slot Mythic + Summon slot Epic squares, the grid's items), the starter
                 choice rows (Common), the Eggs tab craft rows (each egg's rarity), the Hatchery rows (a Rare egg, our dragon egg = Legendary,
                 an empty slot = grey), the Fuse pets grid, the hatch result card (rarity portrait + quality frame); every page through
                 the kit checks (T42.menu_page); one page packet per click (a mode click + a tab click)
  hx/w15/rl/pt/sl/mig/dr/t/r/m/f/dg/vw/st/el410   0.4.17's phases EXECUTED on this jar
  live  start twice on a scratch COPY of the live Skyy_SkyyPets folder (no saved-data change in 0.4.18)
NOT COVERED (UNVERIFIED in game): how the client draws a quality frame + popup title for an ItemGridSlot with its own name / description
(the egg grid has done it since 0.4.1); the 40 % square's look at 1080p.
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util, subprocess, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "petcol", "pets")]
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s417 = importlib.util.spec_from_file_location("test_skyypets_0_4_17", os.path.join(HERE, "test_skyypets_0.4.17.py"))
T417 = importlib.util.module_from_spec(_s417)
_s417.loader.exec_module(T417)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T416, T415, T414, T413, T412, T411, T410, T44, T41 = T417.T416, T417.T415, T417.T414, T417.T413, T417.T412, T417.T411, T417.T410, T417.T44, T417.T41
T42 = T411.T42

VERSION = "0.4.18"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.17.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.17.py")
PATCH = os.path.join(TOOLS, "pets_0_4_18_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T417, T416, T415, T414, T413, T412, T411, T410, T44):
    _m.PKG = PKG
for _m in (T417, T416, T415, T414, T413, T412, T411):
    _m.JAR = JAR
for _m in (T414, T415, T416, T417):
    _m.GEN = GEN
RARS = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
RCOL = [SUI.QUALITY["Common"], SUI.QUALITY["Uncommon"], SUI.QUALITY["Rare"], SUI.QUALITY["Epic"], SUI.QUALITY["Legendary"], SUI.RARITY["Mythic"]]
NONE = SUI.COLOR["disabled"] + "(0.15)"
EXPECT = {   # checked 2026-10-24 against the harness's class compare 0.4.17 -> 0.4.18 (every member is a change of tools/pets_0_4_18_patch.py)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "PetsCfg": ["~m applyAll", "~m seed"],     # the VERSION in the kit / default texts
    "PetsMigP5": ["~m mgLog", "~m run"], "PetsMigS2": ["~m run"], "PetsMigW15": ["~m run"], "SkyyPetsPlugin": ["~m setup"],   # VERSION strings
    "PetEggDefs": ["+m eggRar", "+m isFramed", "+m portraitR"],
    "PetsPage": ["+m cellIcon", "+m rbg", "~m build", "~m cell", "~m fillEggGrid"],
    "PetHatchery": ["~m petCell"], "PetHatchPage": ["~m build"],
}
ADDED = []
if "--expect-dump" in sys.argv:
    EXPECT = {}


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + the 264 new PetFrames item JSONs (S checks each one)"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        fr = [g for g in got if g.startswith("Server/Item/Items/SkyyPets/PetFrames/Skyy_PetIcon_") and g.endswith(".json")]
        return self.check(len(fr) == 264 and sorted(got) == sorted(["manifest.json"] + fr), "C: non-class entries changed = manifest.json + 264 PetFrames items (%d)" % len(fr))
    return _eq00(self, got, want, what)


HK.Child.eq = _eq


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.18 - build script') and g.count('VERSION = "0.4.18"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls("),
            "S no class, system or command added")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_17_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    new = sorted(n for n in set(z.namelist()) - set(oz.namelist()) if not n.endswith("/"))
    K.eq(sorted(set(oz.namelist()) - set(z.namelist())), [], "S no entry removed")
    ch = sorted(n for n in set(z.namelist()) & set(oz.namelist()) if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(ch, ["manifest.json"], "S the changed non-class entries = manifest.json")
    want = []
    bad = []
    for n in oz.namelist():
        m = re.fullmatch(r"Server/Item/Items/SkyyPets/Icons/(Skyy_PetIcon_\w+)\.json", n)
        if not m:
            continue
        base = json.loads(oz.read(n).decode("utf-8"))
        for i, r in enumerate(RARS):
            p = "Server/Item/Items/SkyyPets/PetFrames/%s_%s.json" % (m.group(1), r)
            want.append(p)
            if p not in z.namelist():
                bad.append((p, "missing"))
                continue
            js = json.loads(z.read(p).decode("utf-8"))
            q = "Skyy_Pet_Mythic" if r == "Mythic" else r
            if js != dict(base, Quality=q):
                bad.append((p, js))
    K.check(len(want) == 264 and sorted(want) == new and not bad, "S the only new entries = 264 PetFrames items, each = the portrait JSON + its rarity Quality (%d new, bad %s)" % (len(new), bad[:2]))
    lang = z.read("Server/Languages/en-US/server.lang") == oz.read("Server/Languages/en-US/server.lang")
    K.check(lang, "S no lang line added (the frames reuse the portrait's name key)")
    K.save()


# ======================================================================================================== RC: the rarity colours, EXECUTED
def run_rc(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JShort
    import hub_tab_kit as HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Log, Page, HPage, Hy, Eng, Defs, PK = (P_("PetsCfg"), P_("PetStore"), P_("PetsLog"), P_("PetsPage"), P_("PetHatchPage"), P_("PetHatchery"),
                                                       P_("PetsEng"), P_("PetEggDefs"), P_("PetKind"))
    Paths, UUID, IS = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "rc-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    P_("PetsHubOpen").register()
    Hy.OPENER = P_("PetHatchOpen")()
    # ---- the pure helpers
    kinds = [str(k.id) for k in Cfg.KINDS]
    bad = [(k, r) for k in kinds for r in range(1, 7) if str(Defs.portraitR(k, r)) != "Skyy_PetIcon_%s_%s" % (k, RARS[r - 1]) or not bool(Defs.isFramed(Defs.portraitR(k, r)))]
    K.check(len(kinds) == 44 and not bad, "RC portraitR: every kind x rarity = Skyy_PetIcon_<Kind>_<Rarity>, each isFramed (%s)" % bad[:3])
    K.check(Defs.portraitR("Rabbit", 0) is None and Defs.portraitR("Rabbit", 7) is None and Defs.portraitR("NoSuchKind", 3) is None and Defs.portraitR(None, 3) is None,
            "RC portraitR: no rarity / no portrait = null")
    K.check(not any(bool(Defs.isFramed(x)) for x in ("Skyy_PetIcon_Rabbit", "Skyy_PetIcon_Rabbit_3", "Skyy_PetEgg_Mining_Rare", "Tool_Map", None, "Skyy_PetIcon_", "Skyy_PetRarity_Epic")),
            "RC isFramed: the base portrait, a number suffix, eggs, tokens, tool icons = no frame")
    eg = [(str(i), int(Defs.eggRar(str(i)))) for i in Defs.IDS]
    K.check(all(r == RARS.index(i.rsplit("_", 1)[1]) + 1 for i, r in eg) and len(eg) == 30, "RC eggRar: the 30 pet eggs = their rarity")
    K.check(int(Defs.eggRar("Skyy_PetEgg_Dragon_Air")) == 5 and int(Defs.eggRar("Dragon_Egg_Plain")) == 0 and int(Defs.eggRar(None)) == 0 and int(Defs.eggRar("Rock_Stone")) == 0,
            "RC eggRar: our dragon egg = Legendary, Aures' / unknown = none")
    K.eq([str(Page.rbg(r)) for r in range(0, 8)], [NONE] + [c + "(0.4)" for c in RCOL] + [NONE], "RC rbg: the rarity colour at 40 %, none = the faint grey")
    # ---- a player with pets of every rarity
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000009818"), "Colour")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "123")
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, [str(u1)]), "byName": lambda n: u1, "nameOf": lambda u: "Colour",
                                            "tell": lambda u, t, c: None})
    now = int(JClass("java.lang.System").currentTimeMillis())
    for r in range(1, 7):
        r1.create("rc%d" % r, "Rabbit", r, 3, 0, "harness", now)
    r1.create("rc3b", "Rabbit", 3, 2, 0, "harness", now)
    r1.create("rcx", "NoSuchKind", 4, 1, 0, "harness", now)
    r1.set("active.1", "rc6")
    r1.set("active.2", "rc4")

    def item_of(g):
        return str(HT.jf(g.getClass(), "itemStack").get(g).getItemId())
    cells = [(r, Page.cell(r1, "rc%d" % r, 0)) for r in range(1, 7)]
    K.check(all(item_of(g) == "Skyy_PetIcon_Rabbit_%s" % RARS[r - 1] and not bool(g.isSkipItemQualityBackground()) for r, g in cells),
            "RC the Pets grid cells: the rarity portrait, quality background ON (%s)" % [(item_of(g), bool(g.isSkipItemQualityBackground())) for r, g in cells][:2])
    tip6 = str(HT.jf(cells[5][1].getClass(), "description").get(cells[5][1]))
    K.check(('<color is="%s">Mythic Rabbit</color>' % RCOL[5]) in tip6 and "BUFFS NOW" in tip6 and "PROGRESS" in tip6,
            "RC the approved tooltip: name + rarity in the rarity colour, the sections kept")
    gx = Page.cell(r1, "rcx", 0)
    K.check(item_of(gx) == str(Page.iconOf(r1, "rcx")) and bool(gx.isSkipItemQualityBackground()), "RC a kind without a portrait: its icon (%s), no frame" % item_of(gx))
    K.eq(str(Page.iconOf(r1, "rc5")), "Skyy_PetIcon_Rabbit", "RC iconOf stays the base portrait (SkyyWardrobe / the reel)")
    pc = Hy.petCell(r1, "rc3", Page.cellIcon(r1, "rc3"))
    K.check(item_of(pc) == "Skyy_PetIcon_Rabbit_Rare" and not bool(pc.isSkipItemQualityBackground()), "RC the Fuse pets cell: Rare portrait + frame")
    inv = P_("PetInvReal").of(P1.st, P1.ref)
    ec = Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Mining_Epic", 0)
    K.check(item_of(ec) == "Skyy_PetEgg_Mining_Epic" and not bool(ec.isSkipItemQualityBackground()), "RC the egg cells keep the eggs' own quality frames")

    def frame(apps, ident):
        for _p, mk in apps:
            t = SUI.render(mk)
            m = re.search(r"Group #%s \{ Anchor: \(Width: 44, Height: 44, Left: 0, Top: \d+\); Background: ([^;]+); \}" % re.escape(ident), t)
            if m:
                return m.group(1)
        return None
    # ---- the Pets tab
    hb = P1.slots["hotbar"].getInventory()
    hb.addItemStackToSlot(JShort(2), IS("Skyy_PetEgg_Farming_Rare", 2))
    hb.addItemStackToSlot(JShort(3), IS("Skyy_PetEgg_Dragon_Air", 1))
    pg = Page(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, pg)
    E.pump(P1)
    built = HT.build(pg, P1)
    apps, sets, _ev = T42.menu_page(K, built, "RC the Pets tab")
    K.eq((frame(apps, "SkyyPtS1If"), frame(apps, "SkyyPtS2If")), (RCOL[5] + "(0.4)", RCOL[3] + "(0.4)"), "RC Pet slot (Mythic) + Summon slot (Epic): the icon squares")
    gs = str(sets.get("#SkyyPtGrid.Slots"))
    K.check(all(("Skyy_PetIcon_Rabbit_%s" % r) in gs for r in RARS), "RC the built grid carries the six rarity portraits")
    r1.set("active.2", "")
    apps, sets, _ev = T42.menu_page(K, HT.build(pg, P1), "RC the Pets tab, summon slot empty")
    K.eq(frame(apps, "SkyyPtS2If"), NONE, "RC an empty summon slot: the faint grey square")
    # ---- the starter choice (a second player who has not chosen)
    P2 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000009819"), "Starter")
    u2 = P2.pr.getUuid()
    k2 = str(Store.pkey(u2))
    Store.KEYOF.put(u2, k2)
    r2 = Store.get(k2)
    r2.set("starter", "choose")
    pg2 = Page(P2.pr)
    P2.pm.openCustomPage(P2.ref, P2.st, pg2)
    E.pump(P2)
    apps2, _s2, _e2 = T42.menu_page(K, HT.build(pg2, P2), "RC the starter choice")
    K.eq([frame(apps2, "SkyyPtC%dIf" % i) for i in range(4)], [RCOL[0] + "(0.4)"] * 4, "RC the starter rows: Common squares")
    # ---- the Eggs tab
    pg.tab = 1
    apps, sets, _ev = T42.menu_page(K, HT.build(pg, P1), "RC the Eggs tab")
    craft = [str(x) for x in Hy.CRAFT]
    got = [frame(apps, "SkyyPtE%dIf" % i) for i in range(len(craft))]
    K.eq(got, [RCOL[int(Defs.eggRar(c)) - 1] + "(0.4)" for c in craft], "RC the craft rows: each egg's rarity square (%d rows)" % len(craft))
    # ---- the Hatchery tab: a Rare egg, our dragon egg, an empty slot
    pg.tab = 2
    r1.set("hatchery.1", "Skyy_PetEgg_Farming_Rare|%d|rch1|inv" % now)
    apps, sets, _ev = T42.menu_page(K, HT.build(pg, P1), "RC the Hatchery tab")
    K.eq((frame(apps, "SkyyPtH1If"), frame(apps, "SkyyPtH2If")), (RCOL[2] + "(0.4)", NONE), "RC the Hatchery rows: a Rare egg, an empty slot = grey")
    r1.set("hatchery.2", "Skyy_PetEgg_Dragon_Air|%d|rch2|inv" % now)
    apps, sets, _ev = T42.menu_page(K, HT.build(pg, P1), "RC the Hatchery tab with a dragon egg")
    K.eq(frame(apps, "SkyyPtH2If"), RCOL[4] + "(0.4)", "RC the Hatchery row of our dragon egg = Legendary")
    egs = str(sets.get("#SkyyPtEg.Slots"))
    K.check("Skyy_PetEgg_Farming_Rare" in egs, "RC the egg grid holds the eggs")
    pg.emode = 2
    apps, sets, _ev = T42.menu_page(K, HT.build(pg, P1), "RC the Fuse pets grid")
    K.check("Skyy_PetIcon_Rabbit_Rare" in str(sets.get("#SkyyPtEg.Slots")), "RC the Fuse pets grid: the Rare Rabbit group wears the Rare portrait")
    # ---- one page packet per click (unchanged rule): a click-mode click and a tab click
    pg.emode = 0
    pg.tab = 0
    for d in ('{"a":"mode","i":"1"}', '{"a":"tab2"}'):
        c0 = int(Page.PAGE_UPDATES)
        b0 = int(Page.BUILDS)
        pg.handleDataEvent(P1.ref, P1.st, d)
        E.pump(P1)
        K.check(int(Page.BUILDS) - b0 == 1, "RC %s: ONE rebuild (one page packet)" % d)
    # ---- the hatch result card
    hp = HPage(P1.pr)
    hp.egg, hp.kind, hp.prar, hp.pid, hp.view = "Skyy_PetEgg_Farming_Legendary", "Rabbit", 5, "rc5", 2
    cm, ev = HT.build(hp, P1)
    s3 = dict((s_, d) for ty, s_, t, d in cm if ty == "Set")
    K.check("Skyy_PetIcon_Rabbit_Legendary" in str(s3.get("#SkyyHtR.Slots")) and "Skyy_PetRarity_Legendary" in str(s3.get("#SkyyHtT.Slots")),
            "RC the hatch result card: the Legendary portrait (+ the rarity token): %s" % str(s3.get("#SkyyHtR.Slots"))[:120])
    T42.menu_page(K, (cm, ev), "RC the hatch result page")
    sev = [str(l) for l in Log.LINES if "SEVERE" in str(l) or "WARN" in str(l)]
    K.check(not [l for l in sev if "SEVERE" in l], "RC no SEVERE: %s" % sev[:3])
    K.save()


def run_w15(out, jar, scratch, home):
    f = T414._swap(T417.run_w15, T417, [(r'"SkyyPets 0.4.17\t-\tupdate\ttree.Combat.b3.r3a." in l', r'"SkyyPets 0.4.18\t-\tupdate\ttree.Combat.b3.r3a." in l')])
    f(out, jar, scratch, home)


def run_mig(out, jar, scratch, home):
    f = T414._swap(T415.run_mig, T415, [(r"SkyyPets 0.4.15\t-\tupdate", r"SkyyPets 0.4.18\t-\tupdate")])     # the Changes line names this jar
    f(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("rc", run_rc), ("hx", T417.run_hx), ("w15", run_w15), ("rl", T416.run_rl), ("pt", T416.run_pt),
                   ("sl", T415.run_sl), ("mig", run_mig), ("dr", T415.run_dr), ("t", T415.run_t), ("r", T414.run_r), ("m", T412.run_m),
                   ("f", T414.run_f), ("dg", T414.run_dg), ("vw", T411.run_vw), ("st", T414.run_st), ("el410", T414.run_el), ("live", T417.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
