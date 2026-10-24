"""Harness for SkyyGear 0.3.46 (gear046: the fishing pole ladder + bands, gathering armor tiers up in place + bridge steps, Ornate Bronze = a craftable
combat set with our own Legs, the tooltip header order - tools/gear_0_3_46_patch.py header).
Build first:
    python tools/gear_0_3_46_patch.py && python SkyyGear/build_skyygear_0.3.46.py
    python SkyyGear/test_skyygear_0.3.46.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.45 jar is the compare base):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the jar adds exactly the Ornate Legs item,
              its recoloured texture + icon and the 4 Ornate recipes; the only other non-class change is the manifest (no lang file changed)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.45 -> 0.3.46 (EXPECT below)
  X  exec     (bare JVM) THE POLE: KLAD[POLE] = the 7 rods, GearData.parsePB / poleBand (default, a hand edit, a bad text = WARN + default), the
              bands + level caps (GearLevel.band / cap / level), Bamboo / Copper / Iron unchanged, OLDTOP still Iron (isTop / lineCap: no pole
              gets capped), no Enchanted Sticks on any pole step (GearUp.stickFor), the shown metal (tnm, UpgPage.tierTag "T8 Chromium");
              BRIDGES: GearUp.bridges on the live default ladders (Bronze > Thorium at Iron > Thorium's cost, Lead / Dusk > Cobalt, Chromium /
              Azurvane > Adamantite, nothing for Foraging / Farming / Fishing), GearUp.next / prevsOf / prevOwned / upTotal with a bridge piece;
              gk / below / rankOf; TOOLTIP: reqLine "Mining Lv 23 (15-23)" (met green, short red + "(you: N)", no skills), headTag, armorClass,
              GearView.lines = tag, Class, type, speed, rarity, level line, THEN the stats; plain() line 0 = the bare name, the tag leads line 1;
              the mystery bag text (header first)
  E  engine   (the 0.2.11 harness's bare server boot: vanilla pack store by store with every codec validator, then THIS jar as its own pack)
              V: no failed store / SEVERE / WARNING of ours about the new files; the Legs item in the store (toPacket, Armor block, Heavy sound
              set); the 4 recipes in the CraftingRecipe store; GearPack.combatId; the Smithing Combat armor card "Ornate Bronze" (4 pieces, Head ..
              Legs) sorted by tier between the Lv 8 and Lv 20 sets; the REAL tooltip lines of the Ornate Legs ("Heavy Armor" by its sound set)
              THE CONVERSION through GearSmith.craft (contract stand-ins for SkyySacks' craft bridge + SkyyWardrobe's list / fetch on real
              containers): worn Iron Helm -> Bronze Helm in place (rarity, lines, reforge, eid, set field; materials = the recipe; one piece, no
              second; CONVERT-BEGIN / DONE; XP once); the highest of two lower pieces; no lower piece = a normal craft; materials short = refused,
              nothing moves; an unidentified piece = refused before paying; a slot that refuses the write = the old piece kept + the receipt
              refunded (CONVERT-FAILED); a Requip piece checked + counted first, taken out, converted; Requip + no materials = nothing taken out;
              the converted Bronze piece tiers up into Thorium (GearUp.check: the bridge step's cost); the page button reads "Upgrade"
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: config.properties untouched by 0.3.46 (no one-time update;
              lifelong.poleBands = its default), trees.properties = the wc15 update of 0.3.45 (start 1) and nothing on start 2
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client's hover look of the new header (the "Slot:" line is the client's), the Ornate Legs model / colours
on a player, SkyyFishing 0.2.0's bench craft of a T3-T6 rod carrying the lifelong pole (its own harness), the Smithing page drawing (the craft /
tier-up code it calls is executed here).
Scratch: tools/dev/scratch/gear046/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.46"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear046", "harness")]
import skyybuild as B
import harness_kit as HK
import tier_tags as TT
import wc15_harness as WH

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.45.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_46_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.45.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
FAKE46 = os.path.join(SCRATCH, "fake46")
ADDED = []
EXPECT = {
    "GearCfg": ["+f LL_POLEB", "+f POLEB_DEF", "~<clinit>", "~m apply", "~m defaultsText"],          # lifelong.poleBands (field, loader, fresh file)
    "GearData": ["+f PBC", "+m checkPoleBands", "+m parsePB", "+m poleBand", "~<clinit>"],
    "GearLevel": ["~m band", "~m level"],
    "GearLL": ["+f POLE_SHOW", "+f POLE_W", "+m poleWord", "~<clinit>", "~m tnm"],          # the 7-rod ladder + the shown metal
    "UpgPage": ["~m tierTag"],
    "GearUp": ["+m bridges", "~m cost0", "~m tab"],          # fix: cost0 reads a bridge row's source step
    "GearSmith": ["+f CV", "+f LOW_SECS", "+m below", "+m convWhy", "+m convert", "+m gk", "+m inList", "+m lowerAt", "+m lowerName", "+m lowerRq",
                  "+m prevOwned", "+m prevsOf", "+m rankOf", "~<clinit>", "~m craft", "~m upTotal"],
    "GearHubOpen": ["~m plan", "~m upPiece"],
    "SmithPage": ["~m left", "~m pieceRow", "~m tierRow"],          # left = the page note (fix)
    "GearPack": ["~<clinit>"],          # SMC_ASETS + Armor_Bronze_Ornate
    "GearView": ["+m armorClass", "+m headTag", "+m lvRange", "~m lines", "~m plain", "~m reqLine"],
    "GearUnid": ["~m descMsg"],
    "SkyyGearPlugin": ["~m setup"],
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],          # the version + the new row
}
NEW_FILES = sorted(["Common/Icons/ItemsGenerated/Armor_Bronze_Ornate_Legs.png", "Common/Items/SkyyGear/OrnateArmor/Legs_Texture.png",
                    "Server/Item/Items/SkyyGear/OrnateArmor/Armor_Bronze_Ornate_Legs.json"]
                   + ["Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Armor_Bronze_Ornate_%s.json" % s for s in ("Head", "Chest", "Hands", "Legs")])
ORN = ["Armor_Bronze_Ornate_" + s for s in ("Head", "Chest", "Hands", "Legs")]
RODS = ["SkyyFishing_Rod_" + w for w, m in TT.FI_RODS[:7]]
U = "00000000-0000-0000-0000-000000000346"
LABEL = "*#96a9be"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.46 - build script') and g.count('VERSION = "0.3.46"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (NEW_FILES, []), "S the jar adds exactly the Ornate Legs files + the 4 recipes, removes nothing")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only other non-class change is the manifest (no lang file: the Legs name is vanilla's own key)")
    lj = json.loads(zb.read("Server/Item/Items/SkyyGear/OrnateArmor/Armor_Bronze_Ornate_Legs.json"))
    K.check(lj["TranslationProperties"]["Name"] == "server.items.Armor_Bronze_Ornate_Legs.name" and lj["Model"] == "Items/Armors/Bronze/Legs.blockymodel"
            and lj["Texture"] == "Items/SkyyGear/OrnateArmor/Legs_Texture.png" and lj["ItemSoundSetId"] == "ISS_Armor_Heavy" and lj["Armor"]["ArmorSlot"] == "Legs",
            "S the Legs item: vanilla's own name key, the vanilla Bronze Greaves model by path, our recoloured texture, Heavy sounds")
    K.check("Recipe" in lj and [b["Id"] for b in lj["Recipe"]["BenchRequirement"]] == ["TODO"],
            "S fix: the Legs item has its own Recipe key on vanilla's unreachable TODO bench (the Parent Armor_Iron_Legs' Armor Bench recipe is never inherited)")
    gsrc = open(GEN, encoding="utf-8").read()
    pr = gsrc[gsrc.index("public void pieceRow("):gsrc.index("public void reqLine(")]
    K.check(" - upgrades your " not in pr and 'gid + "Cv { Anchor: (Height: 18);' in pr and '"Upgrades your " + cv9' in pr and "Width: 160); LayoutMode: Top; Padding: (Top: 12)" in pr
            and "Height: 40)" in pr and 12 + 40 + 18 <= 74,
            "S fix (1080 fit): the 324 px name label keeps 'Name  [Lv a-b]'; 'Upgrades your X' is an 18 px line under the 40 px button (12 + 40 + 18 <= the 74 px row)")
    K.check("crafted once, then tiered up on the Anvil" not in gsrc and "craft the next tier to upgrade your piece in place" in gsrc, "S fix: the Smithing page note names the in-place upgrade")
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    K.check(not [n for n in NEW_FILES if n in set(az.namelist())], "S no new file shadows a vanilla path")
    K.check(zb.read("Common/Items/SkyyGear/OrnateArmor/Legs_Texture.png") != az.read("Common/Items/Armors/Bronze/Legs_Texture.png"), "S the Legs texture is a recolour (not a vanilla copy)")
    for s in ("Head", "Chest", "Hands", "Legs"):
        r = json.loads(zb.read("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Armor_Bronze_Ornate_%s.json" % s))
        K.check(r["PrimaryOutput"]["ItemId"] == "Armor_Bronze_Ornate_" + s and r["BenchRequirement"][0]["Id"] == "Armor_Bench" and r["KnowledgeRequired"] is False
                and [x.get("ItemId") for x in r["Input"]][0] == "Ingredient_Bar_Bronze" and "Ingredient_Leather_Medium" in [x.get("ItemId") for x in r["Input"]],
                "S recipe %s: Armor Bench, Bronze Ingots + Medium Leather, no knowledge gate" % s)
    K.check(not (set(TT.ROWS) & set(ORN)), "S tools/tier_tags.py has no Ornate row (the combat_tag reads the id's metal word): %s" % [TT.combat_tag(i, 15) for i in ORN])
    K.save()


# ====================================================================================================== F46: stand-ins (javassist)
def run_mkfake46(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    rb = cp.makeClass("skyyg46.RefuseBox")
    rb.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"))
    rb.addField(CtField.make("public String refuseId;", rb))
    rb.addConstructor(CtNewConstructor.make("public RefuseBox(short n) { super(n); }", rb))
    rb.addMethod(CtNewMethod.make(
        "public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction setItemStackForSlot(short s, com.hypixel.hytale.server.core.inventory.ItemStack i) {\n"
        "  if (this.refuseId != null && i != null && this.refuseId.equals(i.getItemId())) throw new java.lang.IllegalStateException(\"test: the slot refuses \" + this.refuseId);\n"
        "  return super.setItemStackForSlot(s, i);\n}", rb))
    os.makedirs(FAKE46, exist_ok=True)
    rb.writeFile(FAKE46)
    K.check(os.path.isfile(os.path.join(FAKE46, "skyyg46", "RefuseBox.class")), "F46 RefuseBox written")
    K.save()


# ====================================================================================================== X: the bare JVM
def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JString, JArray, JImplements, JOverride, JInt
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    Cfg, Data, Lvl, LL, Up, Sm, GV, Defs, Upg, Unid = (P("GearCfg"), P("GearData"), P("GearLevel"), P("GearLL"), P("GearUp"), P("GearSmith"), P("GearView"),
                                                     P("GearDefs"), P("UpgPage"), P("GearUnid"))
    AL = JClass("java.util.ArrayList")
    BD, BS, BI, BB = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonBoolean")
    JA = lambda xs: JArray(JString)([JString(x) for x in xs])
    Props = JClass("java.util.Properties")
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()
    # ================================================================ 1. THE POLE
    K.eq(str(LL.KLAD[int(LL.POLE)]), ",".join(RODS), "X the pole ladder = the 7 SkyyFishing 0.2.0 rods")
    K.eq(str(Cfg.LL_POLEB), "Thorium=20-39,Cobalt=40-47,Adamantite=48-54,Mithril=55-63", "X lifelong.poleBands default")
    K.check("lifelong.poleBands=Thorium=20-39,Cobalt=40-47,Adamantite=48-54,Mithril=55-63" in fresh and fresh.count("(SkyyGear 0.3.46) ----") == 1,
            "X a fresh config.properties carries the row under its 0.3.46 heading")
    bands = dict((r, [int(x) for x in Lvl.band(JString(r))]) for r in RODS)
    want = {"Bamboo": [3, 10, 1], "Copper": [1, 8, 1], "Iron": [8, 15, 1], "Thorium": [20, 39, 1], "Cobalt": [40, 47, 1], "Adamantite": [48, 54, 1], "Mithril": [55, 63, 1]}
    K.eq(bands, dict(("SkyyFishing_Rod_" + k, v) for k, v in want.items()), "X GearLevel.band of every rod (Bamboo / Copper / Iron = 0.3.45's lookup, unchanged)")
    K.eq([int(LL.cap(JString(r))) for r in RODS], [10, 8, 15, 39, 47, 54, 63], "X the level cap = the band top (Thorium 28 -> 39, Cobalt 47, Chromium 54, Azurvane 63)")
    for r in RODS[3:]:
        b = TT.band(dict(TT.FI_RODS)[r[16:]])
        K.check(int(Lvl.band(JString(r))[0]) == b[0], "X %s starts at its shown metal's band start %s (tools/tier_tags.py)" % (r, b))
    K.eq([int(Lvl.level(JString(r), None)) for r in RODS[3:]], [20, 40, 48, 55], "X GearLevel.level (no stamp) = the band start")
    K.eq([str(LL.tnm(JString(r))) for r in RODS], ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Chromium", "Azurvane"], "X tnm = the shown metal")
    K.eq([str(Upg.tierTag(JString(r))) for r in RODS], ["T1 Crude", "T1 Copper", "T2 Iron", "T4 Thorium", "T7 Cobalt", "T8 Chromium", "T9 Azurvane"],
         "X the Upgrade list's tier tag = tools/tier_tags.py FI_RODS: %s" % [TT.tag_text(TT.ROWS[r][0], TT.WORDS.get(r)) for r in RODS])
    K.eq([str(Upg.poleNext(JString(r))) if Upg.poleNext(JString(r)) is not None else None for r in RODS], RODS[1:] + [None], "X poleNext walks the 7 rods")
    K.eq(list(LL.OLDTOP), [5, 5, 3, 2, 2, 5], "X OLDTOP unchanged: the pole's 0.3.22 top stays Iron")
    K.eq([bool(LL.isTop(int(LL.POLE), JString(r))) for r in RODS], [False, False, True, True, True, True, True], "X Iron and every higher pole keep the uncapped line (isTop)")
    K.eq([int(Up.stickFor(JString(a), JString(b))) for a, b in zip(RODS, RODS[1:])], [0] * 6, "X no Enchanted Sticks on any pole step (SkyyFishing charges them)")
    K.check(int(Up.stickFor(JString("Tool_Pickaxe_Lead_SkyWynn"), JString("Tool_Pickaxe_Dusk_SkyWynn"))) > 0 or int(Up.stickFor(JString("Tool_Pickaxe_Cobalt"), JString("Tool_Pickaxe_Chromium_SkyWynn"))) > 0,
            "X ... while a pickaxe step still costs sticks (control)")
    # the row: a hand edit, a bad text (WARN once + the default), the check hook
    apply(lifelong__poleBands="Thorium=21-30,Iron=8-19")
    K.eq([[int(x) for x in Lvl.band(JString("SkyyFishing_Rod_" + w))] for w in ("Thorium", "Iron", "Cobalt")], [[21, 30, 1], [8, 19, 1], [40, 48, 1]],
         "X a hand-edited lifelong.poleBands is read live (an unlisted rod = level.material)")
    apply(lifelong__poleBands="Thorium=30-20")
    K.eq([int(x) for x in Lvl.band(JString("SkyyFishing_Rod_Thorium"))], [20, 39, 1], "X a bad text = the default")
    K.check(Data.checkPoleBands(JString("lifelong.poleBands"), JString("Thorium=30-20")) is not None and Data.checkPoleBands(JString("k"), JString("A=1-2,B=3-4")) is None
            and Data.checkPoleBands(JString("k"), JString("")) is None and Data.checkPoleBands(JString("k"), JString("Th-orium=1-2")) is not None
            and Data.checkPoleBands(JString("k"), JString("A=1-2,A=3-4")) is not None, "X checkPoleBands: Server Setup refuses a bad text")
    apply()
    # the level rule with a fake SkyySkills: Fishing 60 on a Thorium pole = Lv 39; Fishing 10 on it = Lv 20? (floor: min(skill, cap))
    lv = {"Fishing": 60}

    @JImplements("java.util.function.Function")
    class Skill(object):
        @JOverride
        def apply(self, a):
            return JInt(lv.get(str(a[1]), 0))
    br.put("skill:fn:level", Skill())
    uu = JClass("java.util.UUID").fromString(U)
    P("GearGate").forget(uu)
    K.eq([int(LL.levelFor(uu, JString(r))) for r in RODS[3:]], [39, 47, 54, 60], "X levelFor at Fishing 60: Thorium 39, Cobalt 47, Chromium 54, Azurvane 60")
    lv["Fishing"] = 30
    P("GearGate").forget(uu)
    K.eq([int(LL.levelFor(uu, JString(r))) for r in (RODS[2], RODS[3], RODS[6])], [15, 30, 30], "X levelFor at Fishing 30: Iron 15 (as 0.3.45), Thorium 30, Azurvane 30")

    # ================================================================ 2. BRIDGES + the gathering keys
    tb = Up.tab()
    f, t = [str(x) for x in tb[0]], [str(x) for x in tb[1]]
    kd = [str(x) for x in tb[3]]
    rows = list(zip(f, t, kd))
    brg = [(a, b) for a, b, k in rows if k == "bridge"]
    SL = ["Head", "Chest", "Hands", "Legs"]
    exp = []
    for s in SL:
        exp += [("Armor_Bronze_" + s, "Armor_Thorium_" + s), ("Armor_Mining_Lead_" + s, "Armor_Cobalt_" + s), ("Armor_Mining_Dusk_" + s, "Armor_Cobalt_" + s),
                ("Armor_Mining_Chromium_" + s, "Armor_Adamantite_" + s), ("Armor_Mining_Azurvane_" + s, "Armor_Adamantite_" + s)]
    K.eq(sorted(brg), sorted(exp), "X the bridge steps of the default ladders: Bronze > Thorium, Lead / Dusk > Cobalt, Chromium / Azurvane > Adamantite (x 4 slots)")
    K.check(not [a for a, b in brg if not a.startswith(("Armor_Bronze_", "Armor_Mining_"))], "X ... Mining only (Foraging / Farming / Fishing ladders are complete)")
    K.check(len(set(f)) == len(f), "X every piece still has ONE next tier")
    for a, b in brg[:5]:
        src = [x for x, y, k in rows if y == b and k != "bridge"][0]
        ca, cb = Up.cost(JString(a), JString(b)), Up.cost(JString(src), JString(b))
        K.check(ca is not None and [str(x) for x in ca[0]] == [str(x) for x in cb[0]] and list(ca[1]) == list(cb[1]), "X %s > %s costs what %s > %s costs" % (a, b, src, b))
    K.eq(str(Up.next(JString("Armor_Bronze_Head"))), "Armor_Thorium_Head", "X GearUp.next(Bronze Helm) = Thorium Helm (the converted piece tiers on)")
    xb = tb[2][f.index("Armor_Bronze_Head")]
    g0 = str(Cfg.GARM_LADDERS)
    Cfg.GARM_LADDERS = JString(re.sub(r"\([^)]*\)", "", g0))
    tbn = Up.tab()
    fn_ = [str(x) for x in tbn[0]]
    xn = tbn[2][fn_.index("Armor_Bronze_Head")]
    Cfg.GARM_LADDERS = JString(g0)
    Up.tab()
    K.check("(" in g0 and "String" not in type(xb).__name__ and str(xn) == "Armor_Iron_Head",
            "X fix: a bridge row keeps the source's written cost (%s); with the costs taken out of the text it carries the source step's from (%r) for cost0" % (type(xb).__name__, str(xn)))
    K.eq([str(x) for x in Sm.prevsOf(JString("Armor_Thorium_Head"))], ["Armor_Iron_Head", "Armor_Bronze_Head"], "X prevsOf(Thorium Helm): the table's row first, then the bridge")
    K.eq(str(Sm.prevOf(JString("Armor_Thorium_Head"))), "Armor_Iron_Head", "X prevOf unchanged (the Smithing card text / tierUpOnly)")
    K.check(Sm.tierUpOnly(JString("Armor_Bronze_Head")) is None and Sm.tierUpOnly(JString("Armor_Thorium_Head")) is not None, "X Bronze is still crafted, Thorium still tiers up")
    hs = JClass("java.util.HashSet")()
    hs.add("Armor_Bronze_Head")
    K.eq([str(Sm.prevOwned(JString("Armor_Thorium_Head"), hs)), str(Sm.prevOwned(JString("Armor_Thorium_Head"), JClass("java.util.HashSet")()))],
         ["Armor_Bronze_Head", "Armor_Iron_Head"], "X prevOwned: the owned source (a Bronze Helm), else the table's")
    ut = Sm.upTotal(JA(["Armor_Thorium_" + s for s in SL]), hs, None)
    K.eq(([str(x) for x in ut[0]], [str(x) for x in ut[2]]), (["Armor_Thorium_Head"], ["Armor_Thorium_" + s for s in SL[1:]]), "X upTotal: the Bronze Helm counts for the Thorium set")
    gk = lambda i: None if Sm.gk(JString(i)) is None else list(Sm.gk(JString(i)))
    K.eq([gk("Armor_Iron_Head"), gk("Armor_Bronze_Head"), gk("Armor_Bronze_Legs"), gk("Armor_Bronze_Ornate_Head"), gk("Weapon_Sword_Iron")],
         [[0, 0, 1], [0, 0, 2], [0, 3, 2], None, None], "X gk: Mining family 0, slot, rank (Iron 1 < Bronze 2); Ornate / weapons = none")
    kb = Sm.gk(JString("Armor_Bronze_Head"))
    K.eq([bool(Sm.below(JString(x), kb)) for x in ("Armor_Iron_Head", "Armor_Copper_Head", "Armor_Iron_Chest", "Armor_Thorium_Head", "Armor_Bronze_Head", "Armor_Foraging_F1_Head")],
         [True, True, False, False, False, False], "X below: lower tiers of the same slot only")
    gf = gk("Armor_Foraging_F2_Head")
    K.check(gf is not None and gf[0] == 1 and gk("Armor_Foraging_Beech_Head")[2] < gf[2] and bool(Sm.below(JString("Armor_Foraging_F1_Head"), Sm.gk(JString("Armor_Foraging_F2_Head")))),
            "X gk / below for a Foraging set (family 1, by ladder T)")

    # ================================================================ 4. THE TOOLTIP HEADER (bare JVM: no item sound sets = Heavy)
    Roll = P("GearRoll")
    RIX = {"normal": 0, "unique": 1, "rare": 2, "legendary": 3, "fabled": 4, "mythic": 5, "set": 6}

    def doc(r="rare", lvl=10, ident=True, iid="Weapon_Sword_Iron"):
        d = Roll.newDoc(JString(iid), JInt(RIX[r]), ident, JString("craft"), JInt(lvl))
        d.put("mods", JClass("org.bson.BsonArray")())
        return d

    def lines(i, d, owner=None):
        txt, col = AL(), AL()
        GV.lines(JString(i), d, owner, txt, col)
        return [(str(txt.get(k)).replace(chr(2), ""), None if col.get(k) is None else str(col.get(k))) for k in range(txt.size())]
    br.put("class:list", "Warrior:Swordsmanship,Mage:Arcana,Archer:Archery,Monk:Martial")
    br.put("class:skill:" + U, "Swordsmanship")
    lv["Swordsmanship"] = 20
    br.put("class:weapons:Warrior", "Weapon_Sword_,Weapon_Longsword_")
    br.put("class:weapons:Mage", "Weapon_Staff_,Weapon_Wand_")
    K.eq(str(GV.armorClass(JString("Armor_Bronze_Ornate_Legs"))), "Warrior", "X armorClass: the listed classes whose smith.classArmor type is Heavy")
    br.put("class:list", "Warrior:Swordsmanship,Mage:Arcana,Paladin:Faith")
    ac1 = str(GV.armorClass(JString("Armor_Bronze_Ornate_Legs")))
    br.put("class:list", "Paladin:Faith,Druid:Nature")
    ac2 = str(GV.armorClass(JString("Armor_Bronze_Ornate_Legs")))
    br.put("class:list", "Mage:Arcana")
    ac3 = GV.armorClass(JString("Armor_Bronze_Ornate_Legs"))
    K.eq([ac1, ac2, ac3], ["Warrior / Paladin", "Any", None], "X fix: armorClass + a class not in smith.classArmor (= every type: 'Warrior / Paladin'); every class can = 'Any'; none = no line")
    br.put("class:list", "Warrior:Swordsmanship,Mage:Arcana,Archer:Archery,Monk:Martial")
    K.eq(str(GV.headTag(JString("Armor_Bronze_Ornate_Head"), 2, None)), "T3 Bronze", "X headTag = the tier without the weight")
    K.eq(str(GV.topTag(JString("Armor_Bronze_Ornate_Head"), 2, None)), "T3 Bronze Heavy", "X topTag (the sig's flavour tag) keeps the weight")
    lv["Mining"] = 26
    P("GearGate").forget(uu)
    rq = [str(x) for x in GV.reqLine(uu, JString("Armor_Bronze_Head"), doc("set", 23, iid="Armor_Bronze_Head"), 23)][:2]
    K.eq(rq, ["Mining Lv 23 (15-23)", str(Defs.C_OK)], "X the level line: Mining Lv 23 (15-23), green when met (Skyy's example)")
    lv["Mining"] = 10
    P("GearGate").forget(uu)
    rq2 = [str(x) for x in GV.reqLine(uu, JString("Armor_Bronze_Head"), doc("set", 23, iid="Armor_Bronze_Head"), 23)][:2]
    K.eq(rq2, ["Mining Lv 23 (15-23) (you: 10)", str(Defs.C_BAD)], "X ... red + (you: N) when short")
    K.eq(str(GV.reqLine(None, JString("Armor_Bronze_Head"), doc("set", 23, iid="Armor_Bronze_Head"), 23)[0]), "Mining Lv 23 (15-23)", "X ... the neutral text (no owner)")
    K.eq(str(GV.lvRange(JString("Weapon_Sword_Iron"), 10)), " (8-15)", "X lvRange = the item's band")
    sw = lines("Weapon_Sword_Iron", doc("rare", 10), uu)
    tx = [t for t, c in sw]
    K.notes.append("X lines(Weapon_Sword_Iron): %s" % tx)
    hb = tx[:tx.index("")] if "" in tx else tx
    K.eq(sw[0], ("T2 Iron", LABEL), "X sword: line 0 = the tier tag")
    K.check("Class: Warrior" in hb and "RARE SWORD" in hb and [x for x in hb if " Lv 10 (8-15)" in x], "X sword header: class, rarity, level line all above the first blank line: %s" % hb)
    K.check(hb.index("Class: Warrior") < hb.index("RARE SWORD") < [i for i, x in enumerate(hb) if " Lv 10" in x][0] and "Swordsmanship Lv 10 (8-15)" in hb, "X sword header order: class, (speed), rarity, level 'Swordsmanship Lv 10 (8-15)'")
    K.check(not [x for x in tx[len(hb):] if x == "RARE SWORD" or "Lv. Min" in x or x.startswith("Class")], "X nothing of the header below the stats (no old bottom rarity line)")
    st = [i for i, x in enumerate(tx) if x.startswith(("Damage", "Ability 1", "+ ", "- "))]
    K.check(st and st[0] > len(hb), "X the stats / Ability rows come after the header")
    ar = lines("Armor_Bronze_Ornate_Legs", doc("rare", 15, iid="Armor_Bronze_Ornate_Legs"), uu)
    ta = [t for t, c in ar]
    K.notes.append("X lines(Armor_Bronze_Ornate_Legs): %s" % ta)
    K.eq(ta[:4], ["T3 Bronze", "Class: Warrior", "Heavy Armor", "RARE LEGGINGS"], "X armor header: tier, class, type, rarity")
    K.eq(ta[4], "Swordsmanship Lv 15 (15-23)", "X ... then the level line (the class skill)")
    mp = lines("Armor_Bronze_Head", doc("set", 23, iid="Armor_Bronze_Head"), uu)
    tm = [t for t, c in mp]
    K.notes.append("X lines(Armor_Bronze_Head) Mining 10: %s" % tm)
    hm = tm[:tm.index("")]
    K.check("Mining Lv 23 (15-23) (you: 10)" in hm and [x for x in hm if x.startswith("Gives no stats until")] and hm.index("Mining Lv 23 (15-23) (you: 10)") < [i for i, x in enumerate(hm) if x.startswith("Gives no stats")][0]
            and not [x for x in hm if x.startswith("Class:")], "X Mining piece header: level line, then the red note; no Class line (not combat armor): %s" % hm)
    K.check("Heavy Armor" in hm and hm.index("Heavy Armor") <= 1 and hm.index("Heavy Armor") < hm.index("Mining Lv 23 (15-23) (you: 10)"), "X fix (critic 2): the Mining Bronze Helm header shows its type 'Heavy Armor' right under the tier: %s" % hm)
    pk = lines("Tool_Pickaxe_Iron", doc("rare", 10, iid="Tool_Pickaxe_Iron"), uu)
    tp = [t for t, c in pk]
    hp = tp[:tp.index("")]
    K.check(hp[0] == "T2 Iron" and "RARE PICKAXE" in hp and [x for x in hp if x.startswith("Mining Lv 10")], "X tool header: tier, rarity, Mining Lv line: %s" % hp)
    un = lines("Weapon_Sword_Iron", doc("legendary", 12, False), uu)
    tu = [t for t, c in un]
    K.check("LEGENDARY SWORD" in tu[:tu.index("")] and "Unidentified - its modifiers appear when you identify it." in tu[tu.index(""):], "X unidentified: rarity in the header, the grey text below")
    heads = hb + ta[:ta.index("")] + hm + hp + tu[:tu.index("")]
    K.check(max(len(x) for x in heads) <= 70, "X every header line <= 70 characters (longest %d)" % max(len(x) for x in heads))
    pl = [str(x) for x in GV.plain(JString("Weapon_Sword_Iron"), doc("rare", 10), None)]
    K.notes.append("X plain(Weapon_Sword_Iron): %s" % pl)
    K.check(pl[0] == str(GV.nameText(JString("Weapon_Sword_Iron"), doc("rare", 10))) and pl[1].startswith("T2 Iron - ") and sum(1 for x in pl if "T2 Iron" in x) == 1,
            "X plain(): line 0 = the bare name, the tag leads line 1 (Auctions / Wardrobe / Exploration read it)")
    pa = [str(x) for x in GV.plain(JString("Armor_Bronze_Ornate_Legs"), doc("rare", 15, iid="Armor_Bronze_Ornate_Legs"), None)]
    K.check(pa[1] == "T3 Bronze - Heavy Armor" or pa[1].startswith("T3 Bronze - "), "X plain(Ornate Legs) line 1: %r" % pa[1])
    # the mystery bag (a new bag's text): armor type, rarity, Lv range first
    bd = BD()
    for k_, v_ in (("r", "rare"), ("ty", 2), ("at", 1), ("lo", 15), ("hi", 23)):
        bd.put(k_, BS(v_) if isinstance(v_, str) else BI(v_))
    try:
        m = Unid.descMsg(bd)
        kids = [str(c.getRawText()) for c in m.getChildren() if c.getRawText() is not None]
        flat = [x for x in "".join(kids).split("\n")]
        K.notes.append("X bag text: %s" % flat)
        K.check([x for x in flat[:3] if x.startswith("RARE ")] and [x for x in flat[:4] if x in ("Lv 15-23",)] and not [x for x in flat if "Lv. Range" in x], "X the bag text starts with its rarity + Lv 15-23: %s" % flat[:5])
    except Exception as ex:
        K.check(False, "X the bag text ran in the bare JVM: %s" % str(ex)[:200])
    br.remove("skill:fn:level")
    K.save()


# ====================================================================================================== E: the booted engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JShort, JByte, JString, JArray, JImplements, JOverride, JObject
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar, FAKE46], verify=True, big=True)

    class KC(object):          # the helpers' Child API -> ours
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    HAL = JClass("java.util.ArrayList")
    lst = HAL()
    for it in list(ITEM.getAssetMap().getAssetMap().values()):
        if it is not None and it.hasRecipesToGenerate():
            it.collectRecipesToGenerate(lst)
    if lst.size() > 0:
        CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
    # ---- V: our new files through the engine's validators
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("Ornate" in r[1] or "OrnateArmor" in r[1])]
    K.check(not ours and set(E["fail"]) <= set(E["vfail"]), "E V: no failure about the Ornate files (failed stores %s, vanilla's %s): %s" % (E["fail"], E["vfail"], [r[1][:200] for r in ours[:3]]))
    lg = ITEM.getAssetMap().getAsset("Armor_Bronze_Ornate_Legs")
    try:
        pk = lg.toPacket() if lg is not None else None
        K.check(lg is not None and pk is not None and lg.getArmor() is not None and int(lg.getMaxStack()) == 1, "E V: the Legs item is in the Item store (toPacket, Armor block, MaxStack 1)")
    except Exception as ex:
        K.check(False, "E V: the Legs item packet: %s" % str(ex)[:200])
    oth = []
    for rc in list(CRR.getAssetMap().getAssetMap().values()):
        po = rc.getPrimaryOutput() if rc is not None else None
        if po is None or str(po.getItemId()) not in ORN or str(rc.getId()).startswith("SkyyGear_Recipe_"):
            continue
        brq = rc.getBenchRequirement()
        bn = [str(b.id) for b in brq] if brq is not None else []
        oth.append((str(rc.getId()), str(po.getItemId()), bn))
    K.notes.append("E other recipes that make an Ornate piece: %s" % oth)
    K.check(not [o for o in oth if o[2] != ["TODO"]],
            "E fix: no other recipe makes an Ornate piece at a reachable bench (only vanilla's TODO-bench ones; the Legs inherit no Iron recipe): %s" % oth)
    for i in ORN:
        rc = CRR.getAssetMap().getAsset("SkyyGear_Recipe_" + i)
        K.check(rc is not None and str(rc.getPrimaryOutput().getItemId()) == i, "E V: recipe SkyyGear_Recipe_%s in the CraftingRecipe store" % i)
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Up, Data, Roll, Stamp, Defs, Log, View, Sm, Pack, Forge, Lvl, Merge = (P("GearCfg"), P("Gear"), P("GearUp"), P("GearData"), P("GearRoll"),
                                                                                   P("GearStamp"), P("GearDefs"), P("GearLog"), P("GearView"), P("GearSmith"),
                                                                                   P("GearPack"), P("GearForge"), P("GearLevel"), P("GearMerge"))
    Props = JClass("java.util.Properties")
    p = Props()
    p.load(JClass("java.io.StringReader")(str(Cfg.defaultsText())))
    Cfg.apply(p, False)
    K.check(all(bool(Pack.combatId(JString(i))) for i in ORN) and not [i for i in ORN if bool(Pack.inLoot(JString(i)))], "E GearPack.combatId: the 4 Ornate pieces are plain combat pieces, none in the bag pool")
    K.eq([int(View.weightOf(JString(i))) for i in ORN], [1, 1, 1, 1], "E every Ornate piece is Heavy (its sound set)")
    br = Gear.bridge()
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    RB = JClass("skyyg46.RefuseBox")
    BD, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString")
    UUID = JClass("java.util.UUID")
    U1 = UUID.fromString(U)
    Long_, Bool_ = JClass("java.lang.Long"), JClass("java.lang.Boolean")
    OA = JArray(JClass("java.lang.Object"))
    lv = {"Mining": 30, "Swordsmanship": 20, "Smithing": 10}

    @JImplements("java.util.function.Function")
    class Skill(object):
        @JOverride
        def apply(self, a):
            return JInt(lv.get(str(a[1]), 0))
    XP = []

    @JImplements("java.util.function.Function")
    class AddXp(object):
        @JOverride
        def apply(self, o):
            XP.append((str(o[1]), int(o[2].longValue())))
            return JObject(True, Bool_)
    br.put("skill:fn:level", Skill())
    br.put("skill:fn:addxp", AddXp())
    br.put("class:list", "Warrior:Swordsmanship,Mage:Arcana,Archer:Archery")
    br.put("class:skill:" + U, "Swordsmanship")
    # ---- the Smithing Combat armor card (sorted by tier)
    gs = Sm.groups(U1, 0, True)
    cards = [([str(x) for x in g[1]], int(g[3]), str(g[0])) for g in gs]
    oc = [c for c in cards if c[0] and c[0][0].startswith("Armor_Bronze_Ornate_")]
    K.eq([c[0] for c in oc], [ORN], "E Smithing > Combat armor: one Ornate Bronze card with the 4 pieces in slot order")
    los = [c[1] for c in cards]
    K.check(los == sorted(los) and oc and oc[0][1] == 15 and [c for c in cards if c[1] < 15] and [c for c in cards if c[1] > 15], "E the cards are sorted by tier; Ornate (Lv 15) between lower and higher sets: %s" % [(c[2], c[1]) for c in cards])
    K.eq(str(Sm.setWords(JArray(JString)(["Ornate Bronze Helm", "Ornate Bronze Chest", "Ornate Bronze Gauntlets", "Ornate Bronze Greaves"]))), "Ornate Bronze",
         "E the card heading from the pieces' real (vanilla lang) names = Ornate Bronze Set (this boot has no lang: %r)" % (str(Sm.setName(JString(oc[0][2]), JArray(JString)(ORN), 0)) if oc else None))
    # ---- the real tooltip of the Ornate Legs
    dlg = Roll.newDoc(JString("Armor_Bronze_Ornate_Legs"), JInt(2), True, JString("craft"), JInt(15))
    txt, col = HAL(), HAL()
    View.lines(JString("Armor_Bronze_Ornate_Legs"), dlg, U1, txt, col)
    tl = [str(txt.get(k)) for k in range(txt.size())]
    K.notes.append("E Ornate Legs tooltip: %s" % tl)
    K.eq(tl[:4], ["T3 Bronze", "Class: Warrior", "Heavy Armor", "RARE LEGGINGS"], "E the Ornate Legs header: tier, class, type, rarity")
    K.check(tl[4] == "Swordsmanship Lv 15 (15-23)" and tl.index("") == 5, "E ... then the level line (the class skill, met = no red note): %r" % tl[4])

    # ================================================================ THE CONVERSION (GearSmith.craft)
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        jf(Cc, "inventory").set(o_, cont)
        return o_

    def mkinv(refuse=None):
        inv_ = INV()
        sz = {"hotbar": 9, "storage": 36, "backpack": 9, "armor": 4, "utility": 4, "tools": 4}
        cs_ = {}
        for k_, n_ in sz.items():
            if k_ == "armor" and refuse:
                c_ = RB(JShort(n_))
                c_.refuseId = refuse
            else:
                c_ = SIC(JShort(n_))
            cs_[k_] = c_
        for f_, kind in (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool")):
            jf(INV, f_).set(inv_, comp(kind, cs_[f_]))
        return inv_, cs_

    def at(cs_, sec, i):
        s_ = cs_[sec].getItemStack(JShort(i))
        return None if s_ is None or s_.isEmpty() else s_

    def cnt(inv_, ids):
        all_ = Stamp.allOf(inv_)
        return dict((x, int(Stamp.countId(all_, x))) for x in ids)

    class S(object):
        inv = None
        bag = {}
        receipts = {}
        pays = [0]
        fetches = []
        rq = []
        seq = [0]

    def inputs(rid):
        out_ = []
        for q in CRR.getAssetMap().getAsset(rid).getInput():
            if q is None or q.getQuantity() < 1:
                continue
            out_.append((str(q.getItemId()) if q.getItemId() is not None else "res:" + str(q.getResourceTypeId()), int(q.getQuantity())))
        return out_

    def inv_have(iid):
        return int(Up.have(S.inv, iid)) if S.inv is not None and not iid.startswith("res:") else 0

    def inv_take(iid, n):
        left = n
        for c_ in Up.matSecs(S.inv):
            for i_ in range(int(c_.getCapacity())):
                if left <= 0:
                    return n
                x = c_.getItemStack(JShort(i_))
                if not bool(Up.usable(x, iid)):
                    continue
                q = int(x.getQuantity())
                t_ = min(q, left)
                if t_ >= q:
                    c_.removeItemStackFromSlot(JShort(i_))
                else:
                    c_.setItemStackForSlot(JShort(i_), x.withQuantity(JInt(q - t_)))
                left -= t_
        return n - left

    @JImplements("java.util.function.Function")
    class FList(object):
        @JOverride
        def apply(self, o):
            ids = [str(r_[0]) for r_ in Sm.recipes()]
            return JArray(JString)(ids)

    @JImplements("java.util.function.Function")
    class FHave(object):
        @JOverride
        def apply(self, o):
            ins = inputs(str(o[1]))
            ids, hv, nd = JArray(JString)(len(ins)), JArray(Long_)(len(ins)), JArray(Long_)(len(ins))
            times = 10 ** 9
            for i_, (iid, q) in enumerate(ins):
                h_ = inv_have(iid) + S.bag.get(iid, 0)
                ids[i_], hv[i_], nd[i_] = iid, Long_(h_), Long_(q)
                times = min(times, h_ // q)
            return OA([Long_(times if ins else 0), ids, hv, nd])

    @JImplements("java.util.function.Function")
    class FPay(object):
        @JOverride
        def apply(self, o):
            rid = str(o[1])
            S.pays[0] += 1
            ins = inputs(rid)
            for iid, q in ins:
                if inv_have(iid) + S.bag.get(iid, 0) < q:
                    return OA([Long_(0), None, "not enough materials"])
            took_i, took_b = {}, {}
            for iid, q in ins:
                ti = inv_take(iid, min(q, inv_have(iid)))
                S.bag[iid] = S.bag.get(iid, 0) - (q - ti)
                took_i[iid], took_b[iid] = ti, q - ti
            S.seq[0] += 1
            rc = "rc%d" % S.seq[0]
            S.receipts[rc] = {"inv": took_i, "bag": took_b, "state": "open"}
            return OA([Long_(1), rc, None])

    @JImplements("java.util.function.Function")
    class FRefund(object):
        @JOverride
        def apply(self, o):
            e_ = S.receipts.get(None if o[1] is None else str(o[1]))
            if e_ is None or e_["state"] != "open":
                return Long_(0)
            e_["state"] = "refunded"
            tot = 0
            for iid, n_ in e_["inv"].items():
                if n_ > 0:
                    S.inv.getStorage().addItemStack(IS(iid, JInt(n_)))
                    tot += n_
            for iid, n_ in e_["bag"].items():
                S.bag[iid] = S.bag.get(iid, 0) + n_
                tot += n_
            return Long_(tot)

    @JImplements("java.util.function.Function")
    class FCommit(object):
        @JOverride
        def apply(self, o):
            e_ = S.receipts.get(str(o[1]))
            if e_ is None or e_["state"] != "open":
                return JObject(False, Bool_)
            e_["state"] = "committed"
            return JObject(True, Bool_)

    @JImplements("java.util.function.Function")
    class FCount(object):
        @JOverride
        def apply(self, o):
            return Long_(S.bag.get(str(o[1]), 0))

    @JImplements("java.util.function.Function")
    class WList(object):
        @JOverride
        def apply(self, o):
            if str(o[1]) != "armor":
                return OA([])
            return OA([OA([JString(e), JString(s.getItemId()), s.getMetadata().get(str(Defs.DOC_KEY))]) for e, s in S.rq])

    @JImplements("java.util.function.Function")
    class WFetch(object):
        @JOverride
        def apply(self, o):
            eid = str(o[1])
            S.fetches.append(eid)
            hit = [x for x in S.rq if x[0] == eid]
            if not hit:
                return "not in Requip"
            S.rq.remove(hit[0])
            st_ = S.inv.getStorage()
            st_.setItemStackForSlot(JShort(int(Sm.freeSlot(st_))), hit[0][1])
            return "ok"
    for k_, f_ in (("sacks:fn:craftList", FList()), ("sacks:fn:craftHave", FHave()), ("sacks:fn:craftPay", FPay()), ("sacks:fn:craftRefund", FRefund()),
                   ("sacks:fn:craftCommit", FCommit()), ("sacks:fn:count", FCount()), ("wardrobe:fn:list", WList()), ("wardrobe:fn:fetch", WFetch())):
        br.put(k_, f_)
    GLF = os.path.join(esc, "gear.log")
    Log.FILE = JClass("java.nio.file.Paths").get(GLF)

    def logs():
        Log.flush()
        t_ = open(GLF, encoding="utf-8").read() if os.path.isfile(GLF) else ""
        if os.path.isfile(GLF):
            os.remove(GLF)
        return [l_ for l_ in (t_ + "\n" + str(Log.take())).split("\n") if l_.strip()]
    logs()
    # the recipe Smithing uses for the Bronze Helm (in game SkyyGear_Recipe_Armor_Bronze_Head: the vanilla TODO-bench recipe is filtered by
    # GearSmith.accExists once SkyyAccessories' bench items exist - this bare boot has none, so the lowest usable recipe id wins here)
    RBH = [str(r_[0]) for r_ in Sm.recipes() if str(r_[1]) == "Armor_Bronze_Head"][0]
    ins = inputs(RBH)
    K.notes.append("E %s inputs: %s" % (RBH, ins))
    K.check(Sm.byRid(JString(RBH)) is not None and RBH in [str(x) for x in FList().apply(None)], "E the Bronze Helm recipe is a Smithing recipe")

    def stock(cs_, times=1):
        k_ = 0
        for iid, q in ins:
            if iid.startswith("res:"):          # a resource input (Wood_Trunk = any log): the stand-in counts it from the bag map
                S.bag[iid] = S.bag.get(iid, 0) + q * times
                continue
            cs_["storage"].setItemStackForSlot(JShort(20 + k_), IS(iid, JInt(q * times)))
            k_ += 1

    def piece(iid, r=2, lvl=12, rf="Sturdy", eid=None, ident=True):
        d_ = Roll.newDoc(JString(iid), JInt(r), ident, JString("craft"), JInt(lvl))
        if rf:
            d_.put("rf", BS(rf))
        if not ident:          # a Mining piece is always rolled identified (Set) - mark the document unidentified by hand
            d_.put("id", JClass("org.bson.BsonBoolean")(False))
        s_ = Data.put(IS(iid, JInt(1)), d_, None)
        if eid:
            md = s_.getMetadata().clone()
            md.put("SkyyRequip", BD("e", BS(eid)))
            s_ = s_.withMetadata(md)
        return s_

    def docOf(s_):
        return Merge.inDoc(s_)
    mats = [i for i, q in ins if not i.startswith("res:")]
    # C1 worn Iron Helm -> Bronze Helm in place
    inv, cs = mkinv()
    S.inv, S.bag, S.pays[0] = inv, {}, 0
    iron = piece("Armor_Iron_Head", 2, 12, "Sturdy", "e-iron")
    d0 = docOf(iron)
    cs["armor"].setItemStackForSlot(JShort(0), iron)
    stock(cs)
    m0 = cnt(inv, mats)
    XP[:] = []
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    nw = at(cs, "armor", 0)
    d1 = None if nw is None else docOf(nw)
    K.notes.append("E C1: %s / %s" % (str(r[1]), None if d1 is None else str(d1.toJson())[:300]))
    K.check(int(r[0]) == 1 and nw is not None and str(nw.getItemId()) == "Armor_Bronze_Head", "E C1 the worn Iron Helm BECAME a Bronze Helm in its slot: %s" % str(r[1]))
    K.eq(cnt(inv, ["Armor_Iron_Head", "Armor_Bronze_Head"]), {"Armor_Iron_Head": 0, "Armor_Bronze_Head": 1}, "E C1 one piece, no second (Skyy's bug)")
    if d1 is not None:
        K.check(int(Data.rarity(d1)) == int(Data.rarity(d0)) and str(Data.str(d1, "rf", "")) == "Sturdy" and int(Data.mods(d1).size()) == int(Data.mods(d0).size())
                and [str(Data.str(m_.asDocument(), "s", "")) for m_ in Data.mods(d1)] == [str(Data.str(m_.asDocument(), "s", "")) for m_ in Data.mods(d0)],
                "E C1 rarity, reforge name and every line kept (re-levelled like the Anvil)")
        K.eq(str(Data.str(d1, "set", "")), "mining_bronze", "E C1 the set field moved to the Bronze Mining Set")
        K.check(int(Lvl.level(JString("Armor_Bronze_Head"), d1)) == 23, "E C1 the level = Mining 30 capped at the Bronze band top 23 (%d)" % int(Lvl.level(JString("Armor_Bronze_Head"), d1)))
        K.check(nw.getMetadata().containsKey("SkyyRequip") and str(nw.getMetadata().get("SkyyRequip").asDocument().getString("e").getValue()) == "e-iron", "E C1 the Requip eid rides along")
    m1 = cnt(inv, mats)
    K.eq(dict((i, m0[i] - m1[i]) for i in mats), dict((i, q) for i, q in ins if not i.startswith("res:")), "E C1 the materials taken = the recipe")
    K.check([e for e in S.receipts.values() if e["state"] == "committed"] and S.pays[0] == 1, "E C1 one payment, committed")
    lg1 = logs()
    K.check([l for l in lg1 if "CONVERT-BEGIN" in l] and [l for l in lg1 if "CONVERT-DONE" in l and "Armor_Iron_Head -> Armor_Bronze_Head" in l] and not [l for l in lg1 if "CRAFT-BEGIN" in l],
            "E C1 gear.log: CONVERT-BEGIN / CONVERT-DONE (no CRAFT line)")
    K.check(len([x for x in XP if x[0] == "Smithing"]) == 1, "E C1 Smithing XP paid once: %s" % XP)
    # C9 the converted piece tiers on: Bronze > Thorium through the bridge (the Iron > Thorium cost)
    ck = Up.check(nw, U1)
    K.check(ck[1] is not None and str(ck[1]) == "Armor_Thorium_Head" and (ck[0] is None or "Mining" in str(ck[0]) or "need" in str(ck[0]).lower()),
            "E C9 the converted Bronze Helm tiers up into Thorium (GearUp.check: %s)" % str(ck[0]))
    c9 = Up.cost(JString("Armor_Bronze_Head"), JString("Armor_Thorium_Head"))
    c9b = Up.cost(JString("Armor_Iron_Head"), JString("Armor_Thorium_Head"))
    K.check(c9 is not None and list(c9[1]) == list(c9b[1]), "E C9 ... at the Iron > Thorium cost")
    g9 = str(Cfg.GARM_LADDERS)          # fix (critic): the ladders with NO written costs - the bridge pays what the Iron step's recipe costs
    Cfg.GARM_LADDERS = JString(re.sub(r"\([^)]*\)", "", g9))
    Up.tab()
    sig = lambda c: None if c is None else ([str(x) for x in c[0]], list(c[1]))
    n9 = [sig(Up.cost(JString("Armor_Bronze_" + s), JString("Armor_Thorium_" + s))) for s in ("Head", "Chest", "Hands", "Legs")]
    m9 = [sig(Up.cost(JString("Armor_Iron_" + s), JString("Armor_Thorium_" + s))) for s in ("Head", "Chest", "Hands", "Legs")]
    Cfg.GARM_LADDERS = JString(g9)
    Up.tab()
    K.notes.append("E C9b unwritten Iron > Thorium costs (from the recipes): %s" % m9)
    K.eq(n9, m9, "E fix C9b: costs not written - Bronze > Thorium costs exactly what Iron > Thorium costs")
    # C8 the highest of two lower pieces (Copper in storage, Iron in the backpack) -> Iron converts, Copper stays
    inv, cs = mkinv()
    S.inv, S.bag = inv, {}
    cs["storage"].setItemStackForSlot(JShort(0), piece("Armor_Copper_Head", 1, 5, None))
    cs["backpack"].setItemStackForSlot(JShort(2), piece("Armor_Iron_Head", 3, 12, None))
    stock(cs)
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    K.check(int(r[0]) == 1 and str(at(cs, "backpack", 2).getItemId()) == "Armor_Bronze_Head" and str(at(cs, "storage", 0).getItemId()) == "Armor_Copper_Head",
            "E C8 the HIGHEST lower piece (Iron) converts, the Copper Helm stays")
    logs()
    # C2 no lower piece = a normal craft (a new piece)
    inv, cs = mkinv()
    S.inv, S.bag = inv, {}
    stock(cs)
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    K.check(int(r[0]) == 1 and cnt(inv, ["Armor_Bronze_Head"])["Armor_Bronze_Head"] == 1 and str(r[4]) == "inventory", "E C2 no lower piece = a new Bronze Helm (a normal craft): %s" % str(r[1]))
    K.check([l for l in logs() if "CRAFT-DONE" in l], "E C2 ... CRAFT-DONE in gear.log")
    # C3 materials short = refused, nothing moves
    inv, cs = mkinv()
    S.inv, S.bag = inv, {}
    ir = piece("Armor_Iron_Head", 2, 12, None)
    cs["armor"].setItemStackForSlot(JShort(0), ir)
    fp0 = str(Forge.fp(ir))
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    K.check(int(r[0]) == 0 and str(Forge.fp(at(cs, "armor", 0))) == fp0 and "materials" in str(r[1]), "E C3 materials short = refused, the Iron Helm unchanged: %s" % str(r[1]))
    K.check([l for l in logs() if "CONVERT-REFUSED" in l], "E C3 ... CONVERT-REFUSED")
    # C7 an unidentified lower piece = refused before paying
    inv, cs = mkinv()
    S.inv, S.bag, S.pays[0] = inv, {}, 0
    cs["armor"].setItemStackForSlot(JShort(0), piece("Armor_Iron_Head", 2, 12, None, ident=False))
    stock(cs)
    m0 = cnt(inv, mats)
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    K.check(int(r[0]) == 0 and "Identify" in str(r[1]) and S.pays[0] == 0 and cnt(inv, mats) == m0 and str(at(cs, "armor", 0).getItemId()) == "Armor_Iron_Head",
            "E C7 an unidentified Iron Helm: refused before paying (never a second piece): %s" % str(r[1]))
    logs()
    # C4 the slot refuses the write -> the old piece stays, the receipt is refunded
    inv, cs = mkinv(refuse="Armor_Bronze_Head")
    S.inv, S.bag = inv, {}
    ir = piece("Armor_Iron_Head", 2, 12, "Sturdy")
    cs["armor"].setItemStackForSlot(JShort(0), ir)
    fp0 = str(Forge.fp(ir))
    stock(cs)
    m0 = cnt(inv, mats)
    cv0 = [int(x) for x in Sm.CV]
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    K.check(int(r[0]) == -1 and str(Forge.fp(at(cs, "armor", 0))) == fp0 and cnt(inv, mats) == m0 and cnt(inv, ["Armor_Bronze_Head"])["Armor_Bronze_Head"] == 0,
            "E C4 a refused write: the Iron Helm stays exactly, every material back, no Bronze Helm: %s" % str(r[1]))
    K.check([e for e in S.receipts.values() if e["state"] == "refunded"] and int(Sm.CV[2]) == cv0[2] + 1, "E C4 ... the receipt refunded (CV failed +1)")
    K.check([l for l in logs() if "CONVERT-FAILED" in l and "piece kept true" in l], "E C4 ... CONVERT-FAILED, piece kept")
    # C5 the lower piece is in Requip: checked + counted first, taken out, converted
    inv, cs = mkinv()
    S.inv, S.bag, S.fetches[:] = inv, {}, []
    S.rq = [("eid-7", piece("Armor_Iron_Head", 3, 12, "Keen", "eid-7"))]
    stock(cs)
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    hit = [(i, at(cs, "storage", i)) for i in range(36) if at(cs, "storage", i) is not None and str(at(cs, "storage", i).getItemId()) == "Armor_Bronze_Head"]
    K.check(int(r[0]) == 1 and S.fetches == ["eid-7"] and len(hit) == 1 and not S.rq and str(Data.str(docOf(hit[0][1]), "rf", "")) == "Keen",
            "E C5 the Requip Iron Helm was taken out and converted (one piece, its reforge kept): %s" % str(r[1]))
    logs()
    # C6 Requip + no materials = nothing taken out
    inv, cs = mkinv()
    S.inv, S.bag, S.fetches[:] = inv, {}, []
    S.rq = [("eid-8", piece("Armor_Iron_Head", 3, 12, None, "eid-8"))]
    r = Sm.craft(inv, U1, "Tester", RBH, False)
    K.check(int(r[0]) == 0 and S.fetches == [] and len(S.rq) == 1, "E C6 Requip piece + no materials: refused, nothing taken out of Requip: %s" % str(r[1]))
    S.rq = []
    logs()
    # the page words: lowerName -> "Upgrade" + "Upgrades your Iron Helm" under the button
    inv, cs = mkinv()
    cs["hotbar"].setItemStackForSlot(JShort(4), piece("Armor_Iron_Head", 2, 12, None))
    K.eq([str(Sm.lowerName(inv, U1, JString("Armor_Bronze_Head"))), Sm.lowerName(inv, U1, JString("Armor_Bronze_Chest")), Sm.lowerName(inv, U1, JString("Armor_Bronze_Ornate_Head"))],
         [str(Gear.itemName(JString("Armor_Iron_Head"))), None, None], "E lowerName: the Iron Helm for the Bronze Helm row only (never a combat piece)")
    # fix (critic 2): a Requip-only lower piece names itself on the row ("Upgrade" + "Upgrades your Iron Helm (in Requip)"), craft's own pick
    inv, cs = mkinv()
    S.inv, S.bag = inv, {}
    S.rq = [("eid-9", piece("Armor_Iron_Head", 3, 12, None, "eid-9"))]
    K.eq(str(Sm.lowerName(inv, U1, JString("Armor_Bronze_Head"))), str(Gear.itemName(JString("Armor_Iron_Head"))) + " (in Requip)", "E fix lowerName: a Requip-only Iron Helm reads '(in Requip)'")
    cs["hotbar"].setItemStackForSlot(JShort(1), piece("Armor_Copper_Head", 1, 5, None))
    K.eq(str(Sm.lowerName(inv, U1, JString("Armor_Bronze_Head"))), str(Gear.itemName(JString("Armor_Iron_Head"))) + " (in Requip)", "E fix lowerName: Requip Iron outranks an inventory Copper Helm (craft's rank rule)")
    cs["hotbar"].setItemStackForSlot(JShort(2), piece("Armor_Iron_Head", 2, 12, None))
    K.eq(str(Sm.lowerName(inv, U1, JString("Armor_Bronze_Head"))), str(Gear.itemName(JString("Armor_Iron_Head"))), "E fix lowerName: an Iron Helm on you wins a tie (craft converts the one on you)")
    S.rq = []
    # critic 2 (no loss preview before a convert): a synced gathering piece can never buy level ups (lvlInfo code 8), so docI drops no lvU
    li9 = Forge.lvlInfo(U1, JString("Armor_Iron_Head"), docOf(piece("Armor_Iron_Head", 2, 12, None)))
    K.eq(int(li9[0]), 8, "E critic 2: a gathering armor piece cannot be levelled up with coins (no bought level up to lose on a convert): %s" % str(li9[5]))
    K.notes.append("E CV counters: %s" % [int(x) for x in Sm.CV])
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39"]

    def load():
        m = "".join(str(getattr(Cfg, x)()) for x in MIG)
        K.check(m == "", "D the older one-time updates do nothing on the live copy (%r)" % m[:80])
        Cfg.load()
    WH.live_twice(K, Cfg, "SkyyGear", home, load)
    K.check(c0 is not None and open(fc, "rb").read() == c0, "D config.properties untouched by 0.3.46 over both starts (no one-time update)")
    K.eq(str(Cfg.LL_POLEB), "Thorium=20-39,Cobalt=40-47,Adamantite=48-54,Mithril=55-63", "D lifelong.poleBands read = the default (the live file has no such line)")
    K.check(c0 is not None and b"lifelong.poleBands" not in c0, "D ... (the live file holds no lifelong.poleBands line)")
    K.save()


# the compare phase: harness_kit's own (javassist members + resolved bytecode) with this round's 7 new non-class files allowed next to the manifest
_RC0 = HK.run_compare


def run_compare46(out, jar, old_jar, pkg, expect, added, removed=()):
    import zipfile as _z
    _orig = _z.ZipFile

    class _ZF(_orig):          # the kit's last check reads the non-class entries: hide this round's 7 known new files from it (checked in S)
        def namelist(self):
            n = _orig.namelist(self)
            return [x for x in n if x not in NEW_FILES] if os.path.abspath(self.filename) == os.path.abspath(jar) else n
    _z.ZipFile = _ZF
    try:
        _RC0(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        _z.ZipFile = _orig


HK.run_compare = run_compare46
if "--expect-dump" in sys.argv:
    EXPECT = {}
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("mkfake46", run_mkfake46), ("exec", run_exec), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
