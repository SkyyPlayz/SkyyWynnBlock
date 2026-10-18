"""Harness for SkyyGear 0.3.29 (tools/gear_0_3_29_patch.py header = 20 levels per zone, the Bronze Mining set, 15 Foraging / Farming tiers, Vein Mine /
Tree Feller at tool Lv 4, 8, 16, 24, 32, 40, the multitool = both tools with no drawback after rebirth 1)
    python tools/gear_0_3_29_patch.py && python SkyyGear/build_skyygear_0.3.29.py
    python SkyyGear/test_skyygear_0.3.29.py [--keep]          (S329 + H329 on one booted engine)
    python SkyyGear/test_skyygear_0.3.29.py --static [--keep]  (no jar)

  The OLDER chain (H319 .. H328, their engine phases) is NOT re-run on this jar: their literals are the 0.3.28 bands (Copper 10-18, garmor.bands
  7 ranges, Lead 22-30, 85 / 70 % multitools ...) that 0.3.29 changes on purpose everywhere; the 0.3.28 harness library is loaded only for its engine
  boot (the h319 child: stand-in items, bridge stand-ins, the fresh config). The 0.3.28 behaviour this round keeps is re-checked in H329 (F: the T3
  Fortune cap).
  STATIC (--static)
       G  the patch run TWICE in a scratch tree -> byte-identical, = SkyyGear/build_skyygear_0.3.29.py, compiles, line endings kept
       A  anchors: VERSION; no new system / command / class; h29Update / h29Log / migrate0329 after h23Old and migrate0328; abNeed before abilCap /
          pkNeedLv; rbGate only on the merge paths (a made multitool is never gated); the multitool trade-off line gone; tools/test_tier_tags.py PASS
  S329 the jar 0.3.28 -> 0.3.29: removes nothing; adds exactly the 40 new gathering armor items (+ their art / recolours) and the 4 Bronze recipes;
       the 140 gathering armor pieces: ItemLevel = their T's band start, flavour text starts with their tier tag; the Bronze recipes = Iron's amounts
  H329 (the h319 child) - real code:
       A  the bands: GearLevel.band of Copper / Iron / Bronze / Thorium / Lead / Lumen / Onyxium ids + a family (Prisma) + the kits; GearView.tierFor;
          GearSigDrop.zoneOf; the gathering armor bands per family (Foraging F2 = T3 15-23, Crystalwood T15 95-103, Fishing A3 = T4 20-28), 140 ids,
          the old set ids; the zone Mining bands; the fresh file's rows
       B  the Bronze Mining set: GearMine.isPiece / tier 15 / rank between Iron and Thorium / no zone band / its lines (GM_TAB) / setFor
       C  migrate0329: h29Update on a 0.3.28-shaped file (CRLF): every old default rewritten in place, the Bronze rows + marker added at the END,
          one change-log row per change; a second run = null; a hand edit kept + noted; LF stays LF; a hand-set lifelong.abilityLevelStep adds
          lifelong.abilityLevels= (empty) + a note; h29Log = the change-log row
       D  Vein Mine / Tree Feller: pkNeedLv 4, 8, 16, 24, 32, 40 (then + 8); abilCapLv; an empty list = n x step; checkAbLv; a real player (bridge
          skills): Mining 20 + Iron pickaxe (cap Lv 15) = 2 levels; saved levels above the cap stay saved (perkOf), only 2 work (perkEff); free
          points never below 0; a Copper tool tops at Lv 8
       E  the multitool: rows 100 / 100 / gate on; mstats sides = the single tools (eff); the tooltip (Pickaxe [Lv] ... Hatchet [Lv] ..., no trade-off
          line); no "[Lv N]" in its name; rbGate - no SkyyRebirth refused, rebirth 0 refused ("Rebirth 1 : 0"), rebirth 1 allowed
       F  the 0.3.28 Fortune caps still hold (Bronze 33 = 99 %, Thorium 40)
       L  LIVE DATA: a scratch COPY of the test world's config.properties (UserData read only) through h29Update - parses, the bands moved, the run is
          a no-op the second time
Scratch: tools/dev/scratch/g329/h329 (deleted at the end unless --keep). Exit code 1 on any failure (--static: 0 = PASS).
"""
import os, sys, json, shutil, zipfile, re, subprocess, atexit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
STATIC = "--static" in sys.argv
if STATIC:
    sys.dont_write_bytecode = True


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.29"
V328 = "0.3.28"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g329", "h329")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J328 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V328))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_29_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.29.py")
GEN328 = os.path.join(HERE, "build_skyygear_0.3.28.py")
LIVE_DIR = os.path.join(SCR_BASE, "live")
import tier_tags as TT          # noqa: E402

if not STATIC:
    _H328 = os.path.join(HERE, "test_skyygear_0.3.28.py")
    _T328 = open(_H328, encoding="utf-8").read()
    _T328 = _T328[:_T328.rindex('if __name__ == "__main__":')]
    _argv = sys.argv
    sys.argv = [_H328, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H328 = {"__name__": "skyygear_h328", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T328, _H328 + " (library, 0.3.29)", "exec"), H328)
    sys.argv = _argv
    H319, H320, H316 = H328["H319"], H328["H320"], H328["H316"]
    for _h in (H328, H328["H327"], H328["H326"], H328["H325"], H320, H319):
        _h["VERSION"] = VERSION
    FAILS, OKS = H316["FAILS"], H316["OKS"]
else:
    FAILS, OKS = [], [0]


def check(cond, what):
    if STATIC:
        if cond:
            OKS[0] += 1
        else:
            FAILS.append(what)
            print("FAIL", what)
        return
    H316["check"](cond, what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S329 (the parent, no engine)
def run_assets329():
    ea, eb = entries(J328), entries(JAR)
    added, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    ga_new = [i for i in TT.GA_IDS if not re.match(r"^Armor_(Foraging_F|Farming_P|Fishing_A)\d_", i)]
    want_items = sorted("Server/Item/Items/SkyyGear/GArmor/%s.json" % i for i in ga_new)
    want_rec = sorted("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Armor_Bronze_%s.json" % s for s in ("Head", "Chest", "Hands", "Legs"))
    a_items = sorted(n for n in added if n.startswith("Server/Item/Items/"))
    a_rec = sorted(n for n in added if n.startswith("Server/Item/Recipes/"))
    a_rest = [n for n in added if not n.startswith(("Server/Item/Items/", "Server/Item/Recipes/", "Common/"))]
    farm_old = sorted(n for n in gone if re.match(r"^Common/(Items/SkyyGear/GArmor/[A-Za-z]+_(Head|Chest|Hands|Legs)\.png|Icons/ItemsGenerated/Armor_Farming_P\d_(Head|Chest|Hands|Legs)\.png)$", n)
                      and "Angler" not in n)
    check(sorted(gone) == farm_old and len(farm_old) == 56, "S329: 0.3.28 -> 0.3.29 removes only the 7 old Farming placeholder recolours (28 textures + 28 icons): %d, other %s"
          % (len(farm_old), sorted(set(gone) - set(farm_old))[:4]))
    check(len(ga_new) == 72 and a_items == want_items and a_rec == want_rec and not a_rest,
          "S329: adds the 72 new gathering armor pieces (10 Foraging + 8 Farming sets) + the 4 Bronze recipes (+ art): items %d/%d, recipes %s, other %s" % (len(a_items), len(want_items), a_rec, a_rest[:4]))
    a_art = [n for n in added if n.startswith("Common/")]
    check(len(a_art) == 10 * 4 * 3 + 15 * 4 * 3 + 3, "S329: 10 new Foraging sets + Quirk's 15 Farming sets x 4 x (model, texture, icon) + 3 Legendary frames = 303 art files: %d" % len(a_art))
    # every gathering armor piece's model / texture / icon is in the jar (Fishing's vanilla model by path in Assets.zip); Quirk's Farming art
    import tier_tags as TT_
    miss, farm = [], []
    for i in TT_.GA_IDS:
        j = json.loads(eb["Server/Item/Items/SkyyGear/GArmor/%s.json" % i].decode("utf-8"))
        for k_ in ("Model", "Texture", "Icon"):
            pth = "Common/" + j[k_]
            if pth not in eb and not (i.startswith("Armor_Fishing_") and k_ == "Model"):
                miss.append(pth)
        if i.startswith("Armor_Farming_"):
            farm.append((i, j["Model"], j["Icon"], list(j["Armor"].get("CosmeticsToHide") or [])))
    check(not miss, "S329: every gathering armor model / texture / icon is in the jar: missing %s" % miss[:4])
    crop = dict((r[1], r[2]) for r in TT_.FARMING_ARMOR)
    okf = all(m_.startswith("Items/Armors/SkyyFarming/%s/" % crop[i.split("_")[2]]) and ic.endswith("Armor_Farming_%s_%s.png" % (crop[i.split("_")[2]], i.split("_")[3])) for i, m_, ic, ch in farm)
    check(len(farm) == 60 and okf and all(ch for i, m_, ic, ch in farm if i.endswith("_Head")),
          "S329: the 60 Farming pieces (P1 .. P7 ids kept) point at Quirk's crop models / icons; the helmets carry the base's hide flags")
    bad_m = []
    for n in eb:
        if n.startswith("Common/Items/Armors/SkyyFarming/") and n.endswith(".blockymodel"):
            try:
                json.loads(eb[n].decode("utf-8-sig"))
            except Exception as e:
                bad_m.append((n, str(e)[:60]))
    check(not bad_m, "S329: Quirk's Farming models parse: %s" % bad_m[:3])
    gl = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True).stdout.split("\n")
    priv = [f for f in gl if "SkyyFarming" in f or "farming-armor" in f.lower()]
    onrepo = [os.path.relpath(os.path.join(dp, f), ROOT) for dp, dn, fn in os.walk(ROOT) for f in fn
              if "SkyyFarming" in dp and ".git" not in dp]
    check(not priv and not onrepo, "S329: no private Farming art in the repo (git %s, working tree %s)" % (priv[:3], onrepo[:3]))
    # beta bug 21: Legendary's own aqua frames (the vanilla Rare art recoloured), the quality asset points at them
    import skyyart as SA
    qj = json.loads(eb["Server/Item/Qualities/Skyy_Gear_Legendary.json"].decode("utf-8"))
    fr = ["Common/UI/ItemQualities/Tooltips/ItemTooltipSkyyLegendary@2x.png", "Common/UI/ItemQualities/Tooltips/ItemTooltipSkyyLegendaryArrow@2x.png",
          "Common/UI/ItemQualities/Slots/SlotSkyyLegendary@2x.png"]
    def mean(png):
        im = SA.png_decode(png)
        px = [tuple(im.px[i:i + 4]) for i in range(0, len(im.px), 4)]
        op = [p_ for p_ in px if p_[3] > 128]
        return tuple(sum(p_[c] for p_ in op) / float(len(op)) for c in range(3))
    sm = mean(eb[fr[2]]) if fr[2] in eb else (0, 0, 0)
    tm = mean(eb[fr[0]]) if fr[0] in eb else (0, 0, 0)
    check(all(f in eb for f in fr) and qj["SlotTexture"] == "UI/ItemQualities/Slots/SlotSkyyLegendary.png" and qj["ItemTooltipTexture"] == "UI/ItemQualities/Tooltips/ItemTooltipSkyyLegendary.png"
          and qj["TextColor"] == "#55ffff" and sm[1] > sm[0] * 2 and sm[2] > sm[0] * 2 and tm[1] > tm[0] * 2 and tm[2] > tm[0] * 2,
          "S329: Legendary = Wynn aqua text + its own aqua tooltip / slot frames (slot mean RGB %s, tooltip %s)" % ([round(x) for x in sm], [round(x) for x in tm]))
    rq_ = json.loads(eb["Server/Item/Qualities/Skyy_Gear_Rare.json"].decode("utf-8"))
    check(rq_["SlotTexture"].endswith("SlotEpic.png") and json.loads(eb["Server/Item/Qualities/Skyy_Gear_Normal.json"].decode("utf-8"))["SlotTexture"].endswith("SlotCommon.png"),
          "S329: Normal (Common frame) and Rare (Epic frame) unchanged - Legendary now differs from both")
    # alloy armor recipes need knowledge (SkyyCollections grants recipe:<id> when both inputs reach V); the base-metal zone sets do not
    kz = dict((n.split("/")[-1][:-5], json.loads(eb[n].decode("utf-8"))["Recipe"]["KnowledgeRequired"]) for n in eb if n.startswith("Server/Item/Items/SkyyGear/MiningArmor/"))
    check(len(kz) == 32 and all(v == (k.split("_")[2] in ("Dusk", "Azurvane", "Cinder", "Lumen")) for k, v in kz.items()),
          "S329: zone Mining sets - Dusk / Azurvane / Cinder / Lumen KnowledgeRequired, Lead / Chromium / Slag / Titanium not")
    man = eb["manifest.json"].decode("utf-8", "replace")
    check('"0.3.29"' in man and "LEVEL BANDS: 20 levels per zone" in man and "a bit slower and with less Fortune" not in man, "S329: the manifest says 0.3.29 + the round")
    lang = eb["Server/Languages/en-US/server.lang"].decode("utf-8")
    ld = dict(l.split(" = ", 1) for l in lang.splitlines() if " = " in l)
    bad = [i for i in TT.GA_IDS if not ld.get("items.%s.description" % i, "").startswith(TT.tag_for(i) + " - ")]
    check(not bad, "S329: every gathering armor piece's flavour text starts with its tier tag (T3 Bronze - ...): bad %s" % bad[:4])
    check(ld.get("items.Armor_Foraging_F2_Head.description", "").startswith("T3 Bronze - Autumn Bark set") and
          ld.get("items.Armor_Farming_Mushroom_Legs.description", "").startswith("T15 Lumen - Mushroom Harvest set") and
          ld.get("items.Armor_Fishing_A3_Head.description", "").startswith("T4 Thorium - Thorium Angler set"), "S329: sample tags (F2 T3, Mushroom T15, angler A3 T4)")
    lvl_bad = []
    for i in TT.GA_IDS:
        j = json.loads(eb["Server/Item/Items/SkyyGear/GArmor/%s.json" % i].decode("utf-8"))
        if j.get("ItemLevel") != TT.band(TT.noun(TT.tier(i)))[0]:
            lvl_bad.append((i, j.get("ItemLevel")))
    check(not lvl_bad, "S329: every gathering armor piece's ItemLevel = its T's band start: %s" % lvl_bad[:4])
    rq = [json.loads(eb[n].decode("utf-8")) for n in want_rec if n in eb]
    check(len(rq) == 4 and sorted([(x["ItemId"], x["Quantity"]) for x in r["Input"]][0] for r in rq) == [("Ingredient_Bar_Bronze", q) for q in (7, 9, 13, 16)],
          "S329: the Bronze recipes = Iron's amounts with Bronze Ingots (9 / 16 / 7 / 13)")
    check(all(r["BenchRequirement"][0]["Id"] == "Armor_Bench" and r["KnowledgeRequired"] is True and r["PrimaryOutput"]["ItemId"].startswith("Armor_Bronze_")
              for r in rq), "S329: Armor Bench, KnowledgeRequired (SkyyCollections grants it at both inputs V), output Armor_Bronze_<Slot>")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.28 -> 0.3.29: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(["GearCfg", "GearGArm", "GearMine", "GearLL", "GearTool", "GearView", "GearSigDrop", "LifePage"]) <= set(chg),
          "S329: the patched classes changed: %s" % chg)


# ====================================================================================================== H329 (in the h319 child)
def _h329(L, K):
    from jpype import JClass, JString, JInt, JObject, JImplements, JOverride, JArray, JDouble
    P = lambda n: JClass(PKG + n)
    Cfg, apply, FRESH, br, SK, U1 = L["Cfg"], L["apply"], L["FRESH"], L["br"], L["SK"], L["U1"]
    Lvl, View, Sig, Mine, GA, LL, Tool = (P("GearLevel"), P("GearView"), P("GearSigDrop"), P("GearMine"), P("GearGArm"), P("GearLL"), P("GearTool"))
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    Integer = JClass("java.lang.Integer")
    AL = JClass("java.util.ArrayList")

    def kc(cond, what):
        K.check(bool(cond), "H329 " + what)
    apply()
    fresh = str(Cfg.defaultsText())
    pf = Props()
    pf.load(SR(fresh))
    band = lambda i: tuple(int(x) for x in Lvl.band(i))[:2]          # (min, cap); the cap stops at the item level limit 100 (GearLevel.clamp)
    # ============================================================== A: the bands
    bs = dict((i, band(i)) for i in ("Weapon_Sword_Copper", "Tool_Pickaxe_Copper", "Armor_Copper_Head", "Weapon_Sword_Crude", "Weapon_Sword_Iron",
                                     "Armor_Bronze_Head", "Weapon_Sword_Thorium", "Weapon_Sword_Cobalt", "Weapon_Sword_Mithril", "Weapon_Sword_Onyxium",
                                     "Weapon_Sword_Lead_SkyWynn", "Tool_Pickaxe_Lumen_SkyWynn", "Armor_Prisma_Chest", "Weapon_Daggers_Stone_Trork"))
    kc(bs["Weapon_Sword_Copper"] == bs["Tool_Pickaxe_Copper"] == bs["Armor_Copper_Head"] == bs["Weapon_Sword_Crude"] == (1, 8)
       and bs["Weapon_Sword_Iron"] == (8, 15) and bs["Armor_Bronze_Head"] == (15, 23) and bs["Weapon_Sword_Thorium"] == (20, 28)
       and bs["Weapon_Sword_Cobalt"] == (40, 48) and bs["Weapon_Sword_Mithril"] == (80, 88) and bs["Weapon_Sword_Onyxium"] == (100, 100)
       and bs["Weapon_Sword_Lead_SkyWynn"] == (28, 35) and bs["Tool_Pickaxe_Lumen_SkyWynn"] == (95, 100) and bs["Armor_Prisma_Chest"] == (91, 98)
       and bs["Weapon_Daggers_Stone_Trork"] == (3, 10), "A: GearLevel.band on the new table (Lumen 95-103 / Onyxium 100-108 work up to the item level limit 100): %s" % bs)
    kc([int(View.tierFor(JInt(x), "")) for x in (1, 7, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95, 103)] == [1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15]
       and int(View.tierFor(JInt(40), "Armor_Onyxium_Head")) == 16 and int(View.LB_CRUDE) == 5, "A: GearView.tierFor = tools/tier_tags.py LEVEL_BANDS")
    kc([int(Sig.zoneOf(JInt(x))) for x in (1, 20, 21, 40, 41, 60, 61, 100)] == [1, 1, 2, 2, 3, 3, 4, 4], "A: GearSigDrop.zoneOf = ZONE_TOPS 20 / 40 / 60")
    gb = lambda i: tuple(int(x) for x in GA.band(i))
    kc(len(GA.IDS) == 140 and gb("Armor_Foraging_F1_Head") == (1, 8) and gb("Armor_Foraging_F2_Head") == (15, 23) and gb("Armor_Foraging_Beech_Legs") == (8, 15)
       and gb("Armor_Foraging_F5_Chest") == (75, 83) and gb("Armor_Foraging_Crystalwood_Head") == (95, 103) and gb("Armor_Farming_P7_Hands") == (88, 95)
       and gb("Armor_Farming_Mushroom_Head") == (95, 103) and gb("Armor_Fishing_A3_Head") == (20, 28) and gb("Armor_Fishing_A5_Legs") == (60, 68),
       "A: the gathering armor bands by ladder T (F2 = T3, Crystalwood T15, P7 = T14, angler A3 = T4)")
    kc(str(GA.setFor("Armor_Foraging_F2_Head")) == "foraging_f2" and str(GA.setFor("Armor_Farming_P7_Legs")) == "farming_p7"
       and str(GA.setFor("Armor_Foraging_Crystalwood_Legs")) == "foraging_crystalwood" and str(GA.t1Of("Armor_Foraging_F3_Chest")) == "Armor_Foraging_F1_Chest"
       and int(GA.STIER[int(GA.setIdx("foraging_f3"))]) == 5 and list(GA.FN) == [15, 15, 5], "A: the old set ids kept (stored in documents) at their new tier slots")
    kc(str(pf.getProperty("garmor.bands")) == "1-8,8-15,15-23,20-28,28-35,35-43,40-48,48-55,55-63,60-68,68-75,75-83,80-88,88-95,95-103"
       and str(pf.getProperty("garmor.zoneBands")) == "28-35,35-43,48-55,55-63,68-75,75-83,88-95,95-103" and str(pf.getProperty("loot.levelTop")) == "100"
       and str(pf.getProperty("level.material.Copper")) == "1,8" and str(pf.getProperty("level.material.Armor_Copper")) == "1,8"
       and str(pf.getProperty("ut.Hepta_Axe")).startswith("75,83,") and int(Cfg.LOOT_TOP) == 100, "A: the fresh file's rows")
    zb = lambda i: None if Mine.zband(i) is None else tuple(int(x) for x in Mine.zband(i))
    kc(zb("Armor_Mining_Lead_Head") == (28, 35) and zb("Armor_Mining_Lumen_Legs") == (95, 103) and zb("Armor_Bronze_Head") is None,
       "A: the zone Mining bands (Lead 28-35, Lumen 95-103); Bronze keeps level.material")
    kc(GA.checkBands("garmor.bands", "1-18,15-23,20-28,25-38,35-43,40-49,40-49") is not None and GA.checkBands("garmor.bands", str(pf.getProperty("garmor.bands"))) is None,
       "A: an old 7-range garmor.bands is refused by the check, the new one passes")
    # ============================================================== B: the Bronze Mining set
    kc(bool(Mine.isPiece("Armor_Bronze_Head")) and int(Mine.tier("Armor_Bronze_Legs")) == 15 and int(Mine.tier("Armor_Bronze_Ornate_Head")) == -1
       and int(Mine.rank("Armor_Iron_Head")) < int(Mine.rank("Armor_Bronze_Head")) < int(Mine.rank("Armor_Thorium_Head"))
       and str(Mine.setFor("Armor_Bronze_Chest")) == "mining_bronze" and str(Mine.TIER[15]) == "bronze",
       "B: Armor_Bronze_<Slot> = Mining tier 15 (appended), ranked between Iron and Thorium, Ornate Bronze stays combat")
    kc([round(float(Mine.fortune(JInt(60 + s))), 2) for s in range(4)] == [15.75, 22.05, 9.45, 15.75] and int(Mine.lamp(JInt(15))) == 2
       and str(pf.getProperty("set.mining_bronze")) == "Bronze Mining Set,4,mfort+27 mpow+2.5", "B: the Bronze lines (T3: 63 Fortune on the pieces, lamp 2) + set bonus mfort+27 (= 90)")
    # ============================================================== C: migrate0329
    keys = [str(x) for x in Cfg.H29_KEYS]
    old = [str(x) for x in Cfg.H29_OLD]
    new = [str(x) for x in Cfg.H29_NEW]
    fl = fresh.split("\n")
    m = str(Cfg.H29_MARK)
    kc(fl.count(m) == 1 and all(str(pf.getProperty(k)) == n for k, n in zip(keys, new)), "C: the fresh file: marker once, every migrate0329 row at its new default")
    im = fl.index(m)
    j = im + 1
    while j < len(fl) and fl[j].strip():
        j += 1
    o28 = []
    for x in fl[:im - 1] + fl[j:]:
        k_ = x.split("=", 1)[0] if "=" in x and not x.startswith("#") else None
        if k_ in keys:
            x = k_ + "=" + old[keys.index(k_)]
        o28.append(x)
    t28 = "\r\n".join(o28)
    p28 = Props()
    p28.load(SR(t28))
    kc(p28.getProperty("garmor.mining.bronze") is None and p28.getProperty("lifelong.abilityLevels") is None and str(p28.getProperty("level.material.Copper")) == "10,18",
       "C: the 0.3.28-shaped test file (no 0.3.29 block, old values)")
    r = Cfg.h29Update(JString(t28))
    nt = str(r[0]) if r is not None else ""
    rows = [str(x) for x in r[3]] if r is not None else []
    pn = Props()
    pn.load(SR(nt))
    nl = nt.split("\r\n")
    kc(r is not None and all(str(pn.getProperty(k)) == n for k, n in zip(keys, new)) and [x for x in nl if x.strip()][-1] == m
       and str(pn.getProperty("garmor.mining.bronze")) == str(pf.getProperty("garmor.mining.bronze")) and str(pn.getProperty("set.mining_bronze")) == str(pf.getProperty("set.mining_bronze"))
       and pn.getProperty("lifelong.abilityLevels") is None and "\n" not in nt.replace("\r\n", ""),
       "C: h29Update: %d rows rewritten in place, the 2 Bronze rows + marker at the END, CRLF kept: %s" % (len(keys), str(r[1]) if r is not None else None))
    diff = [(a_, b_) for a_, b_ in zip(o28, nl) if a_ != b_ and a_.strip()]          # the block goes in before the file's last (empty) line
    npres = sum(1 for k_ in keys if p28.getProperty(k_) is not None)
    nadd = len([k_ for k_, c_ in zip([str(x) for x in Cfg.H29_ADDK], [str(x) for x in Cfg.H29_ADDIF]) if not c_ and p28.getProperty(k_) is None])
    kc(len(diff) == npres and nadd == 4 and len(nl) == len(o28) + 2 * nadd + 1, "C: only the old-default lines changed (%d of %d rows the file has) + the 4 missing rows (Soul Orb, Shadoweave, Bronze x2: comment + line each) + the marker: extra %s" % (len(diff), npres, [(a_, b_) for a_, b_ in diff if a_.split("=")[0] not in keys or o28.count(a_) > 1][:4]))
    lk = [str(x) for x in Cfg.H29_LK]
    kc(len(rows) == 3 * len(keys) and rows[0:3] == [lk[0], str(Cfg.H29_LO[0]), str(Cfg.H29_LN[0])] and "level.material[Copper]" in rows
       and rows[rows.index("level.material[Copper]") + 1:rows.index("level.material[Copper]") + 3] == ["10|18", "1|8"],
       "C: one change-log row per change (table rows as level.material[<entry>] with | columns)")
    kc(Cfg.h29Update(JString(nt)) is None, "C: a second run = null (run-once marker)")
    o2 = list(o28)
    o2[o2.index("level.material.Iron=15,23")] = "level.material.Iron=12,23"
    o2[o2.index("lifelong.abilityLevelStep=8")] = "lifelong.abilityLevelStep=5"
    r2 = Cfg.h29Update(JString("\n".join(o2)))
    notes = [str(x) for x in r2[2]] if r2 is not None else []
    p2 = Props()
    p2.load(SR(str(r2[0]) if r2 is not None else ""))
    kc(r2 is not None and str(p2.getProperty("level.material.Iron")) == "12,23" and any(n_.startswith("level.material.Iron=12,23 kept") for n_ in notes)
       and str(p2.getProperty("lifelong.abilityLevels")) == "" and any(n_.startswith("lifelong.abilityLevelStep=5 is a hand edit") for n_ in notes)
       and "\r" not in str(r2[0]) and str(p2.getProperty("level.material.Copper")) == "1,8",
       "C: hand edits kept + noted (Iron 12,23; abilityLevelStep 5 -> lifelong.abilityLevels added EMPTY = the old n x 5 rule), LF stays LF: %s" % notes)
    lg = str(Cfg.h29Log(JString("level.material[Copper]"), JString("10|18"), JString("1|8"))).split("\t")
    kc(len(lg) == 8 and lg[1:] == ["SkyyGear 0.3.29", "-", "update", "level.material[Copper]", "10|18", "1|8", "ok"], "C: h29Log = the change-log row: %s" % lg)
    # ============================================================== D: Vein Mine / Tree Feller + spent points
    need = [int(LL.pkNeedLv(JInt(3), JInt(n))) for n in range(1, 9)]
    nfell = [int(LL.pkNeedLv(JInt(4), JInt(n))) for n in range(1, 7)]
    caps = [int(LL.abilCapLv(JInt(x), JInt(6))) for x in (1, 3, 4, 7, 8, 15, 16, 23, 24, 40, 100)]
    kc(need == [4, 8, 16, 24, 32, 40, 48, 56] and nfell == [4, 8, 16, 24, 32, 40] and caps == [0, 0, 1, 1, 2, 2, 3, 3, 4, 6, 6] and int(LL.pkNeedLv(JInt(1), JInt(1))) == 0,
       "D: Vein Mine / Tree Feller need tool Lv 4, 8, 16, 24, 32, 40 (+8 after): %s %s caps %s" % (need, nfell, caps))
    Cfg.LL_ABLV = ""
    e0 = ([int(LL.pkNeedLv(JInt(3), JInt(n))) for n in (1, 2, 3)], int(LL.abilCapLv(JInt(15), JInt(6))))
    Cfg.LL_ABLV = "4,4"
    e1 = int(LL.pkNeedLv(JInt(3), JInt(1)))
    apply()
    kc(e0 == ([8, 16, 24], 1) and e1 == 4 and LL.checkAbLv("k", "4,4") is not None and LL.checkAbLv("k", "") is None and LL.checkAbLv("k", "4,8,16,24,32,40") is None
       and LL.checkAbLv("k", "x") is not None, "D: empty list = n x lifelong.abilityLevelStep (8, 16, 24); a bad list = one WARN + the default; checkAbLv")
    SK[(str(U1), "Mining")] = 20
    PP = Props()
    PP.setProperty(str(LL.KIND[0]) + ".id", "Tool_Pickaxe_Iron")
    PP.setProperty(str(LL.KIND[0]) + ".up." + str(LL.PK[3]), "5")
    PP.setProperty(str(LL.KIND[0]) + ".up." + str(LL.PK[0]), "7")
    ac = int(LL.abilCap(U1, PP, JInt(0)))
    pe = int(LL.perkEff(U1, PP, JInt(0), JInt(3)))
    po = int(LL.perkOf(PP, JInt(0), JInt(3)))
    sp = int(LL.spent(PP, JInt(0)))
    fr = int(LL.free(U1, PP, JInt(0)))
    SK[(str(U1), "Mining")] = 1
    fr1 = int(LL.free(U1, PP, JInt(0)))
    kc(ac == 2 and pe == 2 and po == 5 and sp > 0 and fr >= 0 and fr1 == 0 and int(LL.cap("Tool_Pickaxe_Copper")) == 8 and int(LL.cap("Tool_Pickaxe_Iron")) == 15,
       "D: Mining 20 + an Iron pickaxe (cap Lv 15): 2 Vein Mine levels work; 5 bought stay saved (perkOf 5); spent %d, free %d (Mining 20) / %d (Mining 1, never below 0); Copper tops at 8" % (sp, fr, fr1))
    SK.pop((str(U1), "Mining"), None)
    # ============================================================== E: the multitool
    kc(int(Cfg.MULTI_SPD) == 100 and int(Cfg.MULTI_FORT) == 100 and bool(Cfg.MULTI_RBGATE) and str(pf.getProperty("multi.speedPct")) == "100"
       and str(pf.getProperty("multi.fortunePct")) == "100" and str(pf.getProperty("multi.rebirthGate")) == "true", "E: no multitool drawback (100 / 100), the rebirth gate on")
    mid = "Tool_Hatchet_Pickaxe_Multitool_Iron"
    t = int(Tool.tier(mid))
    m_ = [float(x) for x in Tool.mstats(None, mid, None)]
    g1 = int(m_[2])
    ea_, eb_ = [float(x) for x in Tool.eff(JInt(1), JInt(g1), JInt(t), None)], [float(x) for x in Tool.eff(JInt(3), JInt(g1), JInt(t), None)]
    kc(m_[4] == ea_[0] and m_[9] == eb_[0] and m_[5] == round(ea_[1], 1) and m_[10] == round(eb_[1], 1),
       "E: the multitool's pickaxe side = the pickaxe (power %s, Fortune %s), its hatchet side = the hatchet (power %s, Fortune %s)" % (m_[4], m_[5], m_[9], m_[10]))
    tx, co = AL(), AL()
    Tool.mlines(None, mid, None, JInt(t), tx, co)
    tl = [str(x) for x in tx]
    ip = [i for i, x in enumerate(tl) if x.startswith("Pickaxe [Lv ")]
    ih = [i for i, x in enumerate(tl) if x.startswith("Hatchet [Lv ")]
    kc(len(ip) == 1 and len(ih) == 1 and ip[0] == 0 and ip[0] < [i for i, x in enumerate(tl) if x.startswith("Mining Power")][0] < [i for i, x in enumerate(tl) if x.startswith("Mining Fortune")][0] < ih[0]
       < [i for i, x in enumerate(tl) if x.startswith("Chopping Power")][0] < [i for i, x in enumerate(tl) if x.startswith("Foraging Fortune")][0]
       and not any("slower" in x or "less Fortune" in x for x in tl) and all(len(x) <= 70 for x in tl),
       "E: the tooltip = Pickaxe [Lv N] + its lines, then Hatchet [Lv M] + its lines, no trade-off line, short lines: %s" % tl)
    D0 = P("GearData")
    try:
        doc = D0.base(D0.kindFor(mid), JInt(0), True, "test")
        nm = str(View.lvTag(mid, doc))
        np_ = str(View.lvTag("Tool_Pickaxe_Iron", doc))
        kc(nm == "" and (np_.startswith(" [Lv ") or not bool(Cfg.NAME_LV)), "E: a multitool's name carries no single [Lv N] (%r; a pickaxe: %r)" % (nm, np_))
    except Exception as ex:
        kc(False, "E: lvTag could not be called: %s" % ex)
    br.remove("rebirth:fn:count")
    g0 = LL.rbGate(U1)

    @JImplements("java.util.function.Function")
    class RbFn(object):
        @JOverride
        def apply(self, o):
            return JObject(JInt(0), Integer)
    br.put("rebirth:fn:count", RbFn())
    br.put("rebirth:n:" + str(U1), JObject(JInt(0), Integer))
    gz = LL.rbGate(U1)
    hz = int(LL.rbHave(U1))
    br.put("rebirth:n:" + str(U1), JObject(JInt(1), Integer))
    g1_ = LL.rbGate(U1)
    br.remove("rebirth:fn:count")
    br.remove("rebirth:n:" + str(U1))
    kc(g0 is not None and "SkyyRebirth" in str(g0) and gz is not None and "Rebirth 1 : 0" in str(gz) and hz == 0 and g1_ is None,
       "E: Make multitool: no SkyyRebirth = refused (%r), rebirth 0 = refused (%r), rebirth 1 = allowed" % (str(g0), str(gz)))
    # ============================================================== F: the 0.3.28 Fortune caps still hold
    def lcap(k, iid):
        pp = Props()
        pp.setProperty(str(LL.KIND[k]) + ".id", iid)
        return int(LL.lineCapP(pp, JInt(k), JInt(1)))
    fc = dict((iid, lcap(0, iid)) for iid in ("Tool_Pickaxe_Bronze_SkyWynn", "Tool_Pickaxe_Thorium", "Tool_Pickaxe_Iron", "Tool_Pickaxe_Copper"))
    kc(fc == {"Tool_Pickaxe_Bronze_SkyWynn": 33, "Tool_Pickaxe_Thorium": 40, "Tool_Pickaxe_Iron": 30, "Tool_Pickaxe_Copper": 20} and float(Cfg.LL_PFORTM) == 3.0,
       "F: Fortune line caps by tier, not by band (Bronze 33 = 99 %%, Thorium 40 = over 100 %% from T4): %s" % fc)
    # ============================================================== G: no Enchanted cost below Dusk + the collection gate text (Collections' answer)
    Up = P("GearUp")
    lad = str(Cfg.LL_LADDERS)
    gal = str(Cfg.GARM_LADDERS)
    kc("Armor_Iron_Chest(Ingredient_Bar_Iron*150)" in gal and "Armor_Thorium_Head(Ingredient_Bar_Thorium*75)" in gal and "Armor_Cobalt_Head(Skyy_Ench_Cobalt*1)" in gal
       and "Tool_Pickaxe_Iron(Ingredient_Bar_Iron*75)" in lad and "Tool_Pickaxe_Lead_SkyWynn(Ingredient_Bar_Lead_SkyWynn*75+Ingredient_Stick*300)" in lad
       and "Tool_Pickaxe_Cobalt(Skyy_Ench_Cobalt*2)" in lad and "Armor_Foraging_Beech_Head(Wood_Beech_Trunk*75)" in str(Cfg.GA_LAD0)
       and "Armor_Farming_Lettuce_Chest(Plant_Crop_Lettuce_Item*150)" in str(Cfg.GA_LAD1) and "Armor_Fishing_A2_Chest(Ingredient_Bar_Iron*150)" in str(Cfg.GA_LAD2)
       and "Skyy_Ench_" not in str(Cfg.HARV_LADDERS).split("Dusk")[0],
       "G: below Dusk every tier-up pays plain materials (75 per old Enchanted, sticks too); Dusk and up keep Enchanted")
    bad_l = [str(Up.checkLadders(k_, v_)) for k_, v_ in (("lifelong.ladders", lad), ("garmor.ladders", gal), ("garmor.ladders.foraging", str(Cfg.GA_LAD0)),
                                                         ("garmor.ladders.farming", str(Cfg.GA_LAD1)), ("garmor.ladders.fishing", str(Cfg.GA_LAD2)),
                                                         ("harvester.ladders", str(Cfg.HARV_LADDERS)), ("can.ladders", str(Cfg.CAN_LADDERS)), ("multi.ladders", str(Cfg.MULTI_LADDERS)))
             if Up.checkLadders(k_, v_) is not None and "_SkyWynn" not in str(Up.checkLadders(k_, v_)) and "_Multitool_" not in str(Up.checkLadders(k_, v_))]          # our / WorldGen's _SkyWynn ids are not stand-in items
    kc(not bad_l, "G: every new ladder passes GearUp.checkLadders (the real items): %s" % bad_l[:3])
    kc(int(Up.stickFor("Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium")) == 0 and int(Up.stickFor("Tool_Pickaxe_Thorium", "Tool_Pickaxe_Lead_SkyWynn")) == 0
       and int(Up.stickFor("Tool_Pickaxe_Dusk_SkyWynn", "Tool_Pickaxe_Cobalt")) == 4, "G: no Enchanted Sticks asked below Dusk (they are plain sticks in the step); Cobalt still 4")
    Req = P("GearReq")

    @JImplements("java.util.function.Function")
    class CollFn(object):
        @JOverride
        def apply(self, o):
            tok = str(o[1])
            if tok.startswith("can:"):
                return JString("0|LettuceColl|Lettuce|2|50|10")
            if tok.startswith("harvester:"):
                return JString("1|Wheat|Wheat|2|50|64")
            return JString("0|Copper|Copper Ore|2|50|67")
    br.put("coll:fn:tierup", CollFn())
    rows = AL()
    Req.collRow0(U1, "Tool_WaterCan_Crude", "Tool_WaterCan_Copper", rows, "can")
    Req.collRow0(U1, "Tool_Sickle_Harvester_Crude", "Tool_Sickle_Harvester_Copper", rows, "harvester")
    Req.collRow0(U1, "Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", rows, "pickaxe")
    br.remove("coll:fn:tierup")
    rt = [(str(Req.tx(rows, JInt(i))), int(Req.st(rows, JInt(i)))) for i in range(int(rows.size()))]
    kc(rt == [("Lettuce collection II 50 : 10", 0), ("Wheat collection II 50 : 64", 1), ("Copper Ore collection II 50 : 67", 0)],
       "G: the gate row shows SkyyCollections' tier as asked (can = Lettuce II, Harvester = Wheat II, pickaxe = Copper Ore II - the gates live in Collections): %s" % rt)
    # ============================================================== H: the gathering armor buff (Skyy "buff all the gathering armor ...")
    ia = lambda i: int(GA.index(i))
    fp = lambda i: [round(float(x), 2) for x in GA.piece(JInt(ia(i)))]
    set4 = lambda pre: round(sum(fp(pre + s)[0] for s in ("Head", "Chest", "Hands", "Legs")), 2)
    full = lambda f, t: round(float(GA.col(JInt(f), JInt(2), JInt(t))), 2)
    ft = [set4("Armor_Foraging_F1_") + full(0, 0), set4("Armor_Foraging_F2_") + full(0, 2), set4("Armor_Foraging_Beech_") + full(0, 1),
          set4("Armor_Foraging_Crystalwood_") + full(0, 14), set4("Armor_Farming_P1_") + full(1, 0), set4("Armor_Farming_Mushroom_") + full(1, 14)]
    kc([round(x, 1) for x in ft] == [60.0, 90.0, 75.0, 240.0, 60.0, 240.0] and fp("Armor_Foraging_F1_Chest")[0] == 14.7,
       "H: a full Foraging / Farming set's Fortune = that tier's tool Fortune line (T1 60, T2 75, T3 90 ... T15 240; Oak Bark Cuirass 14.7): %s" % ft)
    mf = [round(sum(float(Mine.fortune(JInt(t * 4 + s))) for s in range(4)), 1) for t in (0, 1, 15, 2, 14)]          # Copper, Iron, Bronze, Thorium, Lumen
    kc(mf == [42.0, 52.5, 63.0, 73.5, 168.0] and float(Cfg.GM_FCAP) == 0.0 and float(Cfg.fcapA()) > 1.0e8,
       "H: the Mining pieces' Fortune (70 %% of the set: Copper 42, Iron 52.5, Bronze 63, Thorium 73.5, Lumen 168) + armor cap none: %s" % mf)
    kc([round(float(GA.tval(JInt(0), JInt(t), JInt(1))), 2) for t in (1, 3, 15, 16)] == [8.75, 15.75, 57.75, 61.25]
       and [round(float(GA.tval(JInt(1), JInt(t), JInt(0))), 2) for t in (1, 15)] == [1.25, 8.25] and round(sum(float(GA.tval(JInt(0), JInt(4), JInt(s))) for s in range(4)), 2) == 55.0,
       "H: Breaking Power / Speed by T (full set T1 25 %% / 5 %% .. T15 165 %% / 33 %%; a Chest = 35 %% of it)")
    tx2, co2 = AL(), AL()
    GA.lines(None, "Armor_Foraging_F1_Chest", None, tx2, co2)
    tm2, cm2 = AL(), AL()
    Mine.lines(None, "Armor_Iron_Chest", None, tm2, cm2)
    t2 = [str(x) for x in tx2]
    m2 = [str(x) for x in tm2]
    kc("Foraging Fortune +14.7" in t2 and "Chopping Power +8.75%" in t2 and "Breaking Speed +1.75%" in t2 and "Mining Power +12.25%" in m2 and "Breaking Speed +2.45%" in m2,
       "H: the tooltips show the new lines: %s / %s" % (t2, m2))
    GA.ARM.put(U1, JArray(JDouble)([0.0] * 11 + [10.0, 20.0, 30.0]))
    sws = [float(GA.swingFor(U1, JInt(f))) for f in (1, 2, 3, 4, 5, 6, 0)]
    GA.ARM.remove(U1)
    kc(sws == [10.0, 10.0, 20.0, 30.0, 30.0, 20.0, 0.0], "H: GearGArm.swingFor by tool family (pickaxe / shovel Mining, hatchet Foraging, hoe / sickle Farming, multitool the higher): %s" % sws)
    kc("Tool_Hatchet_Iron(Ingredient_Bar_Iron*75+Wood_Beech_Trunk*75)" in lad and "Tool_Hatchet_Bronze_SkyWynn(Ingredient_Bar_Bronze*32+Wood_Maple_Trunk*75+Ingredient_Stick*150)" in lad
       and "Tool_Hatchet_Thorium(Ingredient_Bar_Thorium*75+Wood_Dry_Trunk*75" in lad and "Tool_Hatchet_Lead_SkyWynn(Ingredient_Bar_Lead_SkyWynn*75+Wood_Bottletree_Trunk*150" in lad
       and "Tool_Hatchet_Dusk_SkyWynn(Ingredient_Bar_Dusk_SkyWynn*64+Skyy_Ench_Gumboab*2)" in lad, "H: the hatchet ladder's logs follow the new tree tiers (Iron Beech, Bronze Maple, Thorium Dry, Lead Bottletree, Dusk Gumboab ...)")
    # ============================================================== I: crops by tier, the Furnace Charm gate, the Soul Orb band
    kc("Tool_WaterCan_Iron(Ingredient_Bar_Iron*75+Plant_Crop_Lettuce_Item*75)" in str(Cfg.CAN_LADDERS) and "Tool_Sickle_Harvester_Lumen_SkyWynn(Ingredient_Bar_Lumen_SkyWynn*256+Skyy_Ench_Mushroom*3)" in str(Cfg.HARV_LADDERS)
       and "Tool_Sickle_Harvester_Thorium(Ingredient_Bar_Thorium*75+Plant_Crop_Corn_Item*75" in str(Cfg.HARV_LADDERS) and "Tool_Hoe_Iron(Plant_Crop_Lettuce_Item*75)" in lad,
       "I: can / Harvester / hoe steps cost the key crop of their own T (Iron T2 Lettuce, Thorium T4 Corn ... Lumen T15 Mushroom)")
    cn = [int(LL.charmNeed(x)) for x in ("Tool_Pickaxe_Bronze_SkyWynn", "Tool_Hatchet_Dusk_SkyWynn", "Tool_WaterCan_Azurvane_SkyWynn", "Tool_Sickle_Harvester_Cinder_SkyWynn",
                                          "Tool_Hatchet_Pickaxe_Multitool_Lumen_SkyWynn", "Tool_Pickaxe_Thorium", "Tool_Pickaxe_Lead_SkyWynn")]
    pk1 = str(P("Gear").pkey(U1))
    br.remove("acc:smelt:" + str(U1))
    h0, w0 = int(LL.charmHave(U1)), LL.charmWhy(U1, "Tool_Pickaxe_Bronze_SkyWynn")
    rq0 = AL()
    Req.charmRow(U1, "Tool_Pickaxe_Iron", "Tool_Pickaxe_Bronze_SkyWynn", rq0)
    br.put("acc:smelt:" + str(U1), JString("1|10|15|0|" + pk1))
    h1, w1, w1b = int(LL.charmHave(U1)), LL.charmWhy(U1, "Tool_Pickaxe_Bronze_SkyWynn"), LL.charmWhy(U1, "Tool_Pickaxe_Dusk_SkyWynn")
    rq1 = AL()
    Req.charmRow(U1, "Tool_Pickaxe_Iron", "Tool_Pickaxe_Bronze_SkyWynn", rq1)
    br.put("acc:smelt:" + str(U1), JString("5|50|0|1|someone-else"))
    h2 = int(LL.charmHave(U1))
    br.remove("acc:smelt:" + str(U1))
    rt0 = [(str(Req.tx(rq0, JInt(i))), int(Req.st(rq0, JInt(i)))) for i in range(int(rq0.size()))]
    rt1 = [(str(Req.tx(rq1, JInt(i))), int(Req.st(rq1, JInt(i)))) for i in range(int(rq1.size()))]
    kc(cn == [1, 2, 3, 4, 5, 0, 0] and h0 == 0 and w0 is not None and "Furnace Charm I " in str(w0) and h1 == 1 and w1 is None and w1b is not None and "Furnace Charm II" in str(w1b)
       and h2 == 0 and rt0 == [("Furnace Charm I", 0)] and rt1 == [("Furnace Charm I", 1)],
       "I: alloy tool tier-ups need their Furnace Charm (acc:smelt:<uuid> of the active profile): needs %s, rows %s / %s, %r" % (cn, rt0, rt1, str(w0)))
    kc(band("Weapon_Wand_SoulOrb") == (1, 8) and band("Weapon_Fist_Wraps_Shadoweave") == (60, 67), "I: the Soul Orb gets the Crude / Wood band 1-8 (was its exact ItemLevel 3), Shadoweave 60-67")
    Roll = P("GearRoll")
    Cfg.CRAFT_SKILL = "Weapon_Wand_:Divinity"
    SK[(str(U1), "Divinity")] = 14
    c14 = int(Roll.craftLevel("Weapon_Wand_SoulOrb", U1))
    U2_ = L["U2"]
    SK[(str(U2_), "Divinity")] = 5          # another player (the skill read is cached per player for a moment)
    c5 = int(Roll.craftLevel("Weapon_Wand_SoulOrb", U2_))
    SK.pop((str(U2_), "Divinity"), None)
    sk_ = str(Roll.craftSkill("Weapon_Wand_SoulOrb", U1))
    SK.pop((str(U1), "Divinity"), None)
    apply()
    kc(c14 == 8 and c5 == 5 and sk_ == "Divinity", "I: a Soul Orb crafted at Divinity 14 = Lv 8 (the band top), at Divinity 5 = Lv 5 (0.3.28: always 3): %s / %s" % (c14, c5))
    # ============================================================== L: live data (a scratch COPY of the test world's file)
    lf = os.environ.get("SKYY_G329_LIVE")
    if lf and os.path.isfile(lf):
        raw = open(lf, "rb").read()
        txt = raw.decode("ISO-8859-1")
        rl = Cfg.h29Update(JString(txt))
        if rl is None:
            kc(str(Cfg.H29_MARK_ID) in txt, "L: the live copy already carries the 0.3.29 marker")
        else:
            lt = str(rl[0])
            pl = Props()
            pl.load(SR(lt))
            nrows = len(list(rl[3])) // 3
            nnotes = [str(x) for x in rl[2]]
            ol = txt.split("\n")
            nl_ = lt.split("\n")
            kept = sum(1 for a_, b_ in zip(ol, nl_) if a_ == b_)
            CRLF = chr(13) + chr(10)
            kc(Cfg.h29Update(JString(lt)) is None and len(nl_) >= len(ol) and ((CRLF in txt) == (CRLF in lt)) and nrows >= 1
               and str(Cfg.H29_MARK_ID) in lt and pl.getProperty("garmor.mining.bronze") is not None and pl.getProperty("set.mining_bronze") is not None,
               "L: the live copy migrates (%d rows changed, %d notes, %d of %d lines byte-identical) and a second run is a no-op" % (nrows, len(nnotes), kept, len(ol)))
            K.notes.append("H329 live copy: %d rows changed; notes %s; Copper %s, garmor.bands %s, multi.speedPct %s" % (
                nrows, nnotes[:6], pl.getProperty("level.material.Copper"), pl.getProperty("garmor.bands"), pl.getProperty("multi.speedPct")))
    else:
        K.notes.append("H329 L: no live config copy (SKYY_G329_LIVE unset) - skipped")
    print("  note (h329): A-F ran")


if not STATIC:
    def _h319_h329(L, K):
        try:
            _h329(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H329: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_h329          # ONLY H329 on the booted engine (the older phases' literals are the 0.3.28 bands)


# ====================================================================================================== STATIC (no jars)
def run_static():
    base = os.path.join(SCR_BASE, "static")
    shutil.rmtree(base, ignore_errors=True)
    outs = []
    try:
        for k in range(2):
            r = os.path.join(base, "run%d" % k)
            os.makedirs(os.path.join(r, "tools"))
            os.makedirs(os.path.join(r, "SkyyGear"))
            shutil.copyfile(PATCH, os.path.join(r, "tools", os.path.basename(PATCH)))
            shutil.copyfile(os.path.join(TOOLS, "deploy_set.py"), os.path.join(r, "tools", "deploy_set.py"))
            for _m in ("tier_tags.py", "skyyench.py", "skyyeggs.py"):
                shutil.copyfile(os.path.join(TOOLS, _m), os.path.join(r, "tools", _m))
            shutil.copyfile(GEN328, os.path.join(r, "SkyyGear", os.path.basename(GEN328)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.29.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.29.py (the committed file is the patch's output)")
        src = open(GEN328, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.29.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.29"\n' in s and "GENERATED by tools/gear_0_3_29_patch.py" in s, "A: VERSION 0.3.29 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        i = s.index
        check(i("public static boolean h23Old(") < i("public static Object[] h29Update(") < i("public static String h29Log(") < i("public static synchronized String migrate0329()")
              < i("  @PKG@.GearCfg.migrate0329();") and i("  @PKG@.GearCfg.migrate0328();") < i("  @PKG@.GearCfg.migrate0329();"),
              "A: helpers before their callers; migrate0329 runs after migrate0328")
        check(i("public static int abNeed(int n)") < i("public static int abilCap(") < i("public static int pkNeedLv(") and "lv / st;" not in s,
              "A: abNeed before abilCap / pkNeedLv; the old lv / step rule gone")
        rb = [m_.start() for m_ in re.finditer(r"GearLL\.rbGate\(u\)", s)]
        funcs = []
        for p_ in rb:
            h = s.rfind("public ", 0, p_)
            funcs.append(s[h:s.index("(", h)].split()[-1])
        check(set(funcs) == {"mtRow", "makeMt", "llMtRow", "makeLlMt", "mtCheck", "check"},          # GearMerge.check = the crafted pair merge
              "A: rbGate only on the merge paths (a made multitool is never gated): %s" % sorted(set(funcs)))
        check(s.count("@PKG@.GearLL.mtm(P) ? null : @PKG@.GearLL.rbGate(u)") == 2, "A (review F3): the Tools tab tests 'already has the multitool' before the rebirth gate (row + click)")
        check("slightly slower and less Fortune" not in s.split("--- 0.3.28 notes ---")[-1].split("def default_text")[-1], "A: the multitool trade-off line is gone")
        tp = subprocess.run([sys.executable, "-B", os.path.join(TOOLS, "test_tier_tags.py")], capture_output=True, text=True)
        check(tp.returncode == 0 and "PASS" in tp.stdout, "A: tools/test_tier_tags.py PASS: %s" % (tp.stdout + tp.stderr)[-400:])
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def _live_copy():
    """a scratch COPY of the test world's config.properties (UserData is read only)"""
    try:
        import deploy_set
        w = deploy_set.WORLD
    except Exception:
        w = "NewBetaTest"
    src = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", w, "mods", "Skyy_SkyyGear", "config.properties")
    if not os.path.isfile(src):
        print("  note: no live config at %s - H329 L skipped" % src)
        return
    os.makedirs(LIVE_DIR, exist_ok=True)
    dst = os.path.join(LIVE_DIR, "config.properties")
    shutil.copyfile(src, dst)
    os.environ["SKYY_G329_LIVE"] = dst


def main():
    if STATIC:
        sys.exit(run_static())
    if "--h319" in sys.argv:
        H319["run_h319"](arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--keep", "--dir", "--jar", "--root", "--out", "--only") for a in sys.argv[1:]):
        H320["main"]()          # an older child flag (--mkfake ...) - the chain dispatches it; never the full run again
        return
    assert os.path.isfile(J328) and os.path.isfile(JAR), (J328, JAR)
    if "--keep" not in sys.argv:
        atexit.register(lambda: shutil.rmtree(SCR_BASE, ignore_errors=True))
    run_assets329()
    _live_copy()
    H320["run_fallback"](lambda x: x == "h319", [])


if __name__ == "__main__":
    main()
