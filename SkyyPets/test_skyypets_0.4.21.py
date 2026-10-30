"""Harness for SkyyPets 0.4.21 (THE RARITY + TOOLTIP PASS: the Hatchery egg / Fuse pets tooltips in the Pets tooltip layout, the egg item
flavor texts colour coded, the hatch page titles in the rarity colour; tools/pets_0_4_21_patch.py). Build first:
    python tools/pets_0_4_21_patch.py && python SkyyPets/build_skyypets_0.4.21.py
    python SkyyPets/test_skyypets_0.4.21.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; 0.4.20's patch still regenerates 0.4.20 byte for byte; no class / system / command
                 added; line endings kept; the jar: no entry added / removed, changed non-class entries = manifest.json + server.lang; the
                 lang: the same keys in the same order, ONLY the egg descriptions changed - each one: the tier tag first in the egg's
                 rarity colour, then lang \\n, the spans stripped + the \\n put back to " - " = 0.4.20's text byte for byte, the items. /
                 server. twins equal
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.20 -> 0.4.21, engine-access audit
  RT    EXECUTED on the hub stage (real ItemGridSlots + real UICommandBuilder pages): eggCell for a Rare / Epic / Mythic egg (name in the
                 rarity colour + dim count, HATCHES / PETS / RARITY ODDS in order, gold wait, the footer: Place / all slots in use / Fuse
                 eggs / the fuse cap), with eggs in the Void ("In your Void: " + gold), our dragon egg + Aures' (Legendary); petCell for a
                 fusable Rare group (green state, gold "x<n> owned") and a Mythic one (dim); the hatch page titles #SkyyHtName (no egg =
                 soft white, each rarity, our dragon egg, Aures' egg = Legendary) and #SkyyHtResN (all six rarities) through the kit checks
  rc    0.4.19's RC phase EXECUTED on this jar (the rarity portraits / squares / result card: unchanged)
  ph    0.4.20's PH phase EXECUTED on this jar (pets:fn:hud: unchanged)
  live  0.4.17's start-twice on a scratch COPY of the live Skyy_SkyyPets (no saved-data change)
NOT COVERED (UNVERIFIED in game): how the client draws a lang \\n inside an item's hover description (the server's LangFileParser turns "\\n"
into a line break - read from HytaleServer.jar; vanilla lang never uses it); the colours' look at 1080p.
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "rar_pets", "pets")]
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import skyyeggs as EGG
import tier_tags as TT

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s420 = importlib.util.spec_from_file_location("test_skyypets_0_4_20", os.path.join(HERE, "test_skyypets_0.4.20.py"))
T420 = importlib.util.module_from_spec(_s420)
_s420.loader.exec_module(T420)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T419, T417, T44, T41 = T420.T419, T420.T417, T420.T44, T420.T41
T42 = T417.T411.T42

VERSION = "0.4.21"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.20.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.20.py")
PATCH = os.path.join(TOOLS, "pets_0_4_21_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T420.JAR = T419.JAR = JAR
RARS = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
RCOL = [SUI.QUALITY["Common"], SUI.QUALITY["Uncommon"], SUI.QUALITY["Rare"], SUI.QUALITY["Epic"], SUI.QUALITY["Legendary"], SUI.RARITY["Mythic"]]
SOFT, DIM, GOLD, GREEN, SEC, FOOT, FOOTDIM = "#d6e4ee", "#7f93a6", "#e8c25a", "#7ee08a", "#9aacbc", "#ffcc00", SUI.COLOR["disabled"]
SPAN = re.compile(r"</?color[^>]*>")
EXPECT = {   # the class compare 0.4.20 -> 0.4.21: the four looks + the version texts (the patch's finish() proves nothing else changed)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetsCfg': ['~m applyAll', '~m seed'],
    'PetsMigP5': ['~m mgLog', '~m run'],
    'PetsMigS2': ['~m run'],
    'PetsMigW15': ['~m run'],
    'SkyyPetsPlugin': ['~m setup'],
    'PetHatchery': ['+f RCOL', '+m eggCol', '+m oddsCol', '+m rcolOf', '+m tsec', '~<clinit>', '~m eggCell', '~m petCell'],
    'PetHatchPage': ['+m nameCol', '+m rcolOf', '~m build'],
}
ADDED = []
if "--expect-dump" in sys.argv:
    EXPECT = {}


def tc(c, t):
    return '<color is="%s">%s</color>' % (c, t)


RNAMES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]


def odds(plain):
    """fixer (critic 1): the expected RARITY ODDS line from the plain rarityText - each rarity name in its colour, the % soft, ' - ' dim"""
    out = []
    for part in str(plain).split(" - "):
        nm, pc = part.split(" ", 1)
        out.append(tc(RCOL[RNAMES.index(nm)], nm) + tc(SOFT, " " + pc))
    return tc(DIM, " - ").join(out)


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + server.lang (S checks every lang line)"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == ["Server/Languages/en-US/server.lang", "manifest.json"], "C: non-class entries changed = manifest.json + server.lang (%s)" % got)
    return _eq00(self, got, want, what)


HK.Child.eq = _eq


def lang(z):
    return [l.split("=", 1) for l in z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines() if "=" in l]


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.21 - build script') and g.count('VERSION = "0.4.21"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls("),
            "S no class, system or command added")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_20_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), [], "S the jar adds no entry")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    ch = sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n))
    K.eq(ch, ["Server/Languages/en-US/server.lang", "manifest.json"], "S changed non-class entries = manifest.json + server.lang")
    ln, lo = lang(zn), lang(zo)
    K.eq([k for k, v in ln], [k for k, v in lo], "S the lang: the same keys in the same order (no key name changed)")
    old = dict(lo)
    chg = [k for k, v in ln if old.get(k) != v]
    eggs = sorted(EGG.egg_id(c, r) for c in EGG.CATEGORIES for r in RARS) + sorted(e[0] for e in EGG.ALL_DRAGON_EGGS if e[3] == "SkyyPets")
    want = sorted(p + "items.%s.description" % i for i in eggs for p in ("", "server."))
    K.eq(sorted(chg), want, "S ONLY the %d egg descriptions changed (30 eggs + %d dragon / secret eggs, items. + server.)" % (len(eggs), len(eggs) - 30))
    new = dict(ln)
    bad = []
    for i in eggs:
        v, v0 = new["items.%s.description" % i], old["items.%s.description" % i]
        tag = TT.tag_for(i)
        p = EGG.parse_id(i)
        col = RCOL[RARS.index(p[1])] if p else RCOL[4]
        plain = SPAN.sub("", v)
        ok = (v == new["server.items.%s.description" % i] and v.startswith(tc(col, tag) + "\\n") and plain.startswith(tag + "\\n")
              and plain.replace("\\n", TT.SEP, 1) == v0 and "\\n" not in plain.replace("\\n", "", 1) and tc(DIM, "") [:-8] in v and tc(SOFT, "")[:-8] in v)
        if "Rare to Mythic" in v0:
            ok = ok and (tc(RCOL[2], "Rare") + tc(SOFT, " to ") + tc(RCOL[5], "Mythic")) in v
        if i in EGG.SECRET_EGG_IDS:
            ok = ok and "ragon" not in plain and len(plain) < 300
        if not ok:
            bad.append((i, v[:160], v0[:100]))
    K.check(not bad, "S each egg text: the tier tag first in its rarity colour (span-stripped tag first), lang \\n, the same words as 0.4.20, soft + dim spans, "
            "Rare / Mythic coloured, the secret eggs still say no 'dragon': %s" % bad[:2])
    K.notes.append("S Rare egg text: " + new["items.Skyy_PetEgg_Mining_Rare.description"])
    K.save()


# ======================================================================================================== RT: the tooltips + titles EXECUTED
def run_rt(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JShort
    import hub_tab_kit as HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Log, Page, HPage, Hy, Eng, Defs, Dg, Egg, Ops = (P_("PetsCfg"), P_("PetStore"), P_("PetsLog"), P_("PetsPage"), P_("PetHatchPage"),
                                                                  P_("PetHatchery"), P_("PetsEng"), P_("PetEggDefs"), P_("PetDragon"), P_("PetEgg"), P_("PetOps"))
    Paths, UUID, IS, Long = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack"), JClass("java.lang.Long")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "rt-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    P_("PetsHubOpen").register()
    Hy.OPENER = P_("PetHatchOpen")()
    K.eq([str(x) for x in Hy.RCOL], RCOL, "RT PetHatchery.RCOL = the rarity colours (= PetsPage.RCOL)")
    K.eq([str(Hy.rcolOf(r)) for r in (0, 1, 6, 7)], [RCOL[0], RCOL[0], RCOL[5], RCOL[0]], "RT rcolOf: out of range = Common")
    K.eq(str(Hy.tsec("PETS")), "\n\n" + tc(SEC, "PETS"), "RT tsec = PetsPage.sec (the section head)")
    K.eq(str(Hy.tsec("PETS")), str(Page.sec("PETS")), "RT ... byte for byte")
    K.eq([str(Hy.eggCol(i)) for i in ("Skyy_PetEgg_Mining_Rare", "Skyy_PetEgg_Combat_Mythic", "Skyy_PetEgg_Dragon_Air", "Dragon_Egg_Plain", "Rock_Stone", None)],
         [RCOL[2], RCOL[5], RCOL[4], RCOL[4], RCOL[0], RCOL[0]], "RT eggCol: the egg's rarity; our dragon egg + Aures' = Legendary; not an egg = Common")
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000009821"), "Tips")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "123")
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, [str(u1)]), "byName": lambda n: u1, "nameOf": lambda u: "Tips",
                                            "tell": lambda u, t, c: None})
    void = {}
    br = P_("PetsLog").bridge()
    br.put("sacks:fn:count", JProxy("java.util.function.Function", dict={"apply": lambda a: Long.valueOf(void.get(str(list(a)[1]), 0))}))
    hb = P1.slots["hotbar"].getInventory()
    hb.addItemStackToSlot(JShort(2), IS("Skyy_PetEgg_Mining_Epic", 2))
    hb.addItemStackToSlot(JShort(3), IS("Skyy_PetEgg_Dragon_Air", 1))
    hb.addItemStackToSlot(JShort(4), IS("Skyy_PetEgg_Farming_Rare", 7))
    inv = P_("PetInvReal").of(P1.st, P1.ref)
    desc = lambda g: str(HT.jf(g.getClass(), "description").get(g))

    def foot(d):
        m = re.search(r"\n\n<color is=\"(#[0-9a-fA-F]{6})\">([^<]*)</color>$", d)
        return None if m is None else (m.group(1), m.group(2))

    def order(d, *parts):
        at = [d.find(p) for p in parts]
        return all(a >= 0 for a in at) and at == sorted(at)
    # ---- an Epic egg, 2 held, Place mode
    g = Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Mining_Epic", 0)
    d = desc(g)
    K.check(d.startswith(tc(RCOL[3], "Epic Mining Egg") + "  " + tc(DIM, "x2") + "\n\n" + tc(SEC, "HATCHES")),
            "RT egg cell: the name in the Epic colour + dim x2 first (no Void line with none in the Void): %r" % d[:140])
    K.check(order(d, tc(SEC, "HATCHES"), tc(SOFT, "Hatches in ") + '<color is="%s">' % GOLD, tc(DIM, " in a Hatchery slot"), tc(SEC, "PETS"),
                  tc(SOFT, str(Egg.oddsText("Mining", 4))), tc(SEC, "RARITY ODDS"), odds(Egg.rarityText(4))),
            "RT ... HATCHES (soft 'Hatches in ' + the gold wait) -> PETS (the odds, soft white) -> RARITY ODDS, in that order")
    # fixer (critic 1): RARITY ODDS = each rarity name in its own colour, the same words as rarityText once the spans are stripped
    _ol = d[d.index(tc(SEC, "RARITY ODDS")) + len(tc(SEC, "RARITY ODDS")) + 1:].split("\n")[0]
    K.eq(SPAN.sub("", _ol), str(Egg.rarityText(4)), "FIX1 egg cell: the RARITY ODDS line, spans stripped = PetEgg.rarityText word for word")
    K.check(all(tc(RCOL[RNAMES.index(p.split(" ")[0])], p.split(" ")[0]) in _ol for p in str(Egg.rarityText(4)).split(" - ")),
            "FIX1 ... every rarity name in its own rarity colour: %r" % _ol[:200])
    K.check(tc(SOFT, str(Egg.rarityText(4))) not in d, "FIX1 ... no longer one soft-white line")
    K.check(tc(GOLD, str(Hy.dur(Hy.waitMs("Skyy_PetEgg_Mining_Epic", u1)))) in d, "RT ... the wait = dur(waitMs) in gold")
    K.eq(foot(d), (FOOT, "Click: put it in a free Hatchery slot"), "RT ... the footer unchanged (yellow Click: put it in a free Hatchery slot)")
    K.eq(str(HT.jf(g.getClass(), "name").get(g)), "Epic Mining Egg x2", "RT ... setName kept")
    K.check(not bool(g.isSkipItemQualityBackground()), "RT ... the egg's quality frame kept")
    # ---- Fuse eggs mode (2 < the fuse count -> the grey reason), then 7 Rare eggs (ready, yellow)
    d1 = desc(Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Mining_Epic", 1))
    w1 = str(Hy.efuseWhy(u1, inv, "Skyy_PetEgg_Mining_Epic") or "")
    K.check(w1.startswith("-") and foot(d1) == (FOOTDIM, w1[1:]), "RT Fuse eggs mode, too few: the grey reason footer unchanged: %s" % (foot(d1),))
    d2 = desc(Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Farming_Rare", 1))
    w2 = Hy.efuseWhy(u1, inv, "Skyy_PetEgg_Farming_Rare")
    want2 = (FOOT, "Click twice: fuse %d into 1 Epic Farming Egg" % int(Cfg.EFUSE_COUNT)) if w2 is None else (FOOTDIM, str(w2)[1:])
    K.eq(foot(d2), want2, "RT Fuse eggs mode, a Rare stack of 7: the footer unchanged")
    K.check(d2.startswith(tc(RCOL[2], "Rare Farming Egg") + "  " + tc(DIM, "x7")), "RT ... the name in the Rare colour")
    # ---- eggs in the Void: the dim 'In your Void: ' + the gold count, counted in x<n>
    void["Skyy_PetEgg_Farming_Rare"] = 5
    d3 = desc(Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Farming_Rare", 0))
    K.check(d3.startswith(tc(RCOL[2], "Rare Farming Egg") + "  " + tc(DIM, "x12") + "\n" + tc(DIM, "In your Void: ") + tc(GOLD, "5") + "\n\n" + tc(SEC, "HATCHES")),
            "RT with 5 in the Void: x12 + the Void line (dim label, gold count) before HATCHES: %r" % d3[:200])
    void.clear()
    # ---- a Mythic egg (only in the Void: the cell still shows)
    void["Skyy_PetEgg_Combat_Mythic"] = 1
    d4 = desc(Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Combat_Mythic", 0))
    K.check(d4.startswith(tc(RCOL[5], "Mythic Combat Egg") + "  " + tc(DIM, "x1")) and odds(Egg.rarityText(6)) in d4, "RT a Mythic egg: the Mythic colour")
    void.clear()
    # ---- our dragon egg + Aures' egg (Legendary)
    dd = desc(Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Dragon_Air", 0))
    K.check(dd.startswith(tc(RCOL[4], str(Defs.nameOf("Skyy_PetEgg_Dragon_Air"))) + "  " + tc(DIM, "x1"))
            and order(dd, tc(SEC, "HATCHES"), tc(SEC, "PETS"), tc(SOFT, "Hatches " + str(Dg.eggText("Skyy_PetEgg_Dragon_Air"))), tc(SEC, "RARITY ODDS"), odds(Dg.rarityText()))
            and "Hatches your Sky Dragon (Air)" in dd,
            "RT our dragon egg: the Legendary colour, PETS = 'Hatches your Sky Dragon (Air) ...', the dragon rarity odds: %r" % dd[:220])
    dw = Dg.placeWhy(r1, "Skyy_PetEgg_Dragon_Air")
    K.eq(foot(dd), (FOOTDIM, str(dw)[1:]) if dw is not None else (FOOT, "Click: put it in a free Hatchery slot"), "RT ... its footer unchanged")
    da = desc(Hy.eggCell(u1, r1, inv, "Dragon_Egg_Plain", 0))
    K.check(da.startswith('<color is="%s">' % RCOL[4]) and tc(SOFT, "Hatches " + str(Dg.eggText("Dragon_Egg_Plain"))) in da,
            "RT Aures' Plain Dragon egg: Legendary colour, its dragon line (%s): %r" % (str(Dg.eggText("Dragon_Egg_Plain"))[:60], da[:160]))
    # ---- all Hatchery slots in use: the grey footer unchanged
    now = int(JClass("java.lang.System").currentTimeMillis())
    for s in range(1, int(Cfg.HATCH_SLOTS) + 1):
        r1.set("hatchery.%d" % s, "Skyy_PetEgg_Farming_Rare|%d|rth%d|inv" % (now, s))
    K.eq(foot(desc(Hy.eggCell(u1, r1, inv, "Skyy_PetEgg_Mining_Epic", 0))), (FOOTDIM, "All Hatchery slots are in use"), "RT every slot in use: the grey footer unchanged")
    for s in range(1, int(Cfg.HATCH_SLOTS) + 1):
        r1.set("hatchery.%d" % s, None)
    # ---- the Fuse pets cells: a fusable Rare Rabbit group, a Mythic one
    n = int(Cfg.FUSE_COUNT)
    for i in range(n):
        r1.create("rtR%d" % i, "Rabbit", 3, 2 + i, 0, "harness", now)
    r1.create("rtM", "Rabbit", 6, 3, 0, "harness", now)
    pc = Hy.petCell(r1, "rtR0", Page.cellIcon(r1, "rtR0"))
    p = desc(pc)
    tl = str(Ops.typeLine("Rabbit", int(P_("PetRide").levelOf(r1, "rtR0"))))
    K.check(Ops.fuseWhy(r1, "rtR0") is None, "RT the Rare Rabbit group can fuse (%d)" % n)
    K.check(p.startswith(tl + "\n" + tc(RCOL[2], "Rare Rabbit") + "  " + tc(GOLD, "x%d owned" % n) + "\n\n" + tc(SEC, "FUSING") + "\n" + tc(SOFT, "Fusing: ")
                         + tc(GREEN, str(Ops.fuseInfo(r1, "rtR0"))) + "\n" + tc(DIM, "Mythic pets come only from eggs.")),
            "RT Fuse pets cell (fusable): type line, 'Rare Rabbit' in the Rare colour + gold 'x%d owned', FUSING with the state in green, the dim minor line: %r" % (n, p[:260]))
    K.eq(foot(p), (FOOT, "Click twice: fuse %d into 1 Epic (keeps the most grown)" % n), "RT ... the footer unchanged")
    K.check(not bool(pc.isSkipItemQualityBackground()), "RT ... the Rare portrait frame kept")
    pm = desc(Hy.petCell(r1, "rtM", Page.cellIcon(r1, "rtM")))
    wm = str(Ops.fuseWhy(r1, "rtM"))
    K.check(tc(RCOL[5], "Mythic Rabbit") + "  " + tc(GOLD, "x1 owned") in pm and tc(DIM, str(Ops.fuseInfo(r1, "rtM"))) in pm and foot(pm) == (FOOTDIM, wm[1:]),
            "RT Fuse pets cell (Mythic): the Mythic colour, the state dim, the grey reason footer unchanged: %r" % pm[-200:])
    # ---- the hatch page titles
    def title_cols(hp):
        cm, ev = HT.build(hp, P1)
        cols = {}
        for ty, s_, t, _d in cm:
            if t is None:
                continue
            for ident in ("SkyyHtName", "SkyyHtResN"):
                m = re.search(r"Label #%s \{[^}]*TextColor: (#[0-9a-fA-F]{6})" % ident, str(t))
                if m:
                    cols[ident] = m.group(1)
        T42.menu_page(K, (cm, ev), "RT the hatch page view %d (%s)" % (hp.view, hp.egg or "no egg"))
        return cols
    hp = HPage(P1.pr)
    hp.view = 0
    hp.egg = ""
    got = {}
    for egg_, want in (("", SOFT), ("Skyy_PetEgg_Farming_Common", RCOL[0]), ("Skyy_PetEgg_Farming_Uncommon", RCOL[1]), ("Skyy_PetEgg_Mining_Rare", RCOL[2]),
                       ("Skyy_PetEgg_Mining_Epic", RCOL[3]), ("Skyy_PetEgg_Combat_Legendary", RCOL[4]), ("Skyy_PetEgg_Combat_Mythic", RCOL[5]),
                       ("Skyy_PetEgg_Dragon_Air", RCOL[4]), ("Dragon_Egg_Plain", RCOL[4])):
        hp.egg, hp.view = egg_, 0
        got[egg_ or "-"] = (title_cols(hp).get("SkyyHtName"), want)
    held = str(P_("PetInvReal").of(P1.st, P1.ref).heldId() or "")
    if held and int(Defs.index(held)) >= 0:
        K.notes.append("RT the player holds %s - view 0 takes the held egg (checked as is)" % held)
    bad = [(k, g_, w_) for k, (g_, w_) in got.items() if g_ != w_ and not (held and int(Defs.index(held)) >= 0)]
    K.check(not bad and len(got) == 9, "RT #SkyyHtName: no egg = soft white, each egg its rarity colour, our dragon + Aures' egg = Legendary: %s" % (bad or got))
    gr = []
    for pr_ in range(1, 7):
        hp.egg, hp.kind, hp.prar, hp.pid, hp.view = "Skyy_PetEgg_Farming_Legendary", "Rabbit", pr_, "rtR0", 2
        gr.append(title_cols(hp).get("SkyyHtResN"))
    K.eq(gr, RCOL, "RT #SkyyHtResN (the result 'Rarity Kind'): each rarity's colour")
    K.eq([str(HPage.rcolOf(r)) for r in (0, 3, 7)], [SOFT, RCOL[2], SOFT], "RT PetHatchPage.rcolOf: out of range = the heading's soft white")
    sev = [str(l) for l in Log.LINES if "SEVERE" in str(l)]
    K.check(not sev, "RT no SEVERE: %s" % sev[:3])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("rt", run_rt), ("rc", T419.run_rc), ("ph", T420.run_ph), ("live", T417.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
