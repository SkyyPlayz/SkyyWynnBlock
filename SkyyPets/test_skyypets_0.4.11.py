"""Harness for SkyyPets 0.4.11 (THE DRAGON PET: five dragon kinds, dragon eggs in the Hatchery, one dragon per profile, the stage looks in
the summon slot, DOWN after the void; tools/pets_0_4_11_patch.py, research/Dragon-Pet-Spec.md).
Build first:
    python tools/pets_0_4_11_patch.py && python SkyyPets/build_skyypets_0.4.11.py
    python SkyyPets/test_skyypets_0.4.11.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; one new class (PetDragon), no new system / command; line endings kept; the jar: our
                 dragon role (= the walk role, MaxWalkSpeed 8), the two child models (Parent by id + our texture, same size as the
                 vanilla one), 3 egg items (Legendary, no Recipe, the right-click line), 5 portraits (all OUR recolours - fixer B1: never
                 a path of Aures' pack; nothing of Aures in the jar), the lang lines; tools/skyyeggs.py untouched for the 30 eggs
  FX2   (fixer 2) EXECUTED: the Eggs grid skips an unloaded egg id; a take-out of Aures' egg without the pack is refused; open credit /
        check lines wait for the pack, then give; lookOk needs all four stage models; the vanilla sizes x0.3 -> x1.0; the tier tag first
  FX    (fixer round) EXECUTED: Aures' egg / stage models NOT loaded (PetDragon.ASSET_API) -> place / hatch / admin egg / summon refuse
                 with the Nestkeeper reason; the egg give line counts what arrived; a dragon is never a starter pet; DOWN only with the
                 owner online, alive and in the dragon's world; a logout forgets the unsent line; DOWN prunes ran-out cooldowns
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.10 -> 0.4.11, engine-access audit
  DG    EXECUTED (fake inventory / clock, real records): the stage + size maths at every level and every row edit, the look (summon slot
                 only), the elements (pets.dragon.element; pets.element wins), the dragon egg ids (index / catOf / rarOf / names), the
                 rows' check= hooks, the rarity roll (never below Rare, 20,000 seeded rolls), dragons never from a category egg, the
                 HATCHERY: place (inventory + Void), a second dragon egg refused, 1 h wait, hatch = the fixed kind + a dragon rarity, a
                 second dragon refused on EVERY path (place, hatch with an egg already waiting, /petadmin give, restore), egg fusing
                 refused, the grid cell / slot texts, /petadmin egg <player> dragon <word>, the card lines, pets:stats with the element
  VW    EXECUTED on a stand-in world (PetWorld.API): want() (pet slot = nothing, summon slot = the stage model), spawnNow (our dragon
                 role, the PINNED look through modelPinned(seed = pet id), x the model's own size), a level-up = a new stage model, the
                 game removing it (the void) = DOWN + one chat line + nothing spawned until the cooldown ends + back after it; the pin
                 maths on real Java maps (every set but the saddle, the same pick every time, another pet = its own); the REAL
                 PetWorld.modelPinned never throws without assets; the census line
  ST    EXECUTED in the hub stage (REAL PageManager): Aures' egg in a real hotbar -> the Hatchery grid -> a click places it -> the slot
                 row ("dragon eggs take 1h 00m") -> a second dragon egg refused -> the clock -> Hatch -> the reel page opens straight on the
                 result (no reels) -> the Pets tab card shows the stage lines
  EL410 0.4.10's element phase EXECUTED on this jar (unchanged behaviour)
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets: nothing written, every pet file reads, the dragons known with the live
                 config file (no kind.<Dragon> line = the built-in one), their elements from pets.dragon.element
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "dragonpet", "pets")]
import skyybuild as B
import harness_kit as HK
import skyyeggs as EGG
import skyyui as SUI

_cmp0 = HK.run_compare
_s410 = importlib.util.spec_from_file_location("test_skyypets_0_4_10", os.path.join(HERE, "test_skyypets_0.4.10.py"))
T410 = importlib.util.module_from_spec(_s410)
_s410.loader.exec_module(T410)
T44 = T410.T44
T41 = T44.T41
_s42 = importlib.util.spec_from_file_location("test_skyypets_0_4_2", os.path.join(HERE, "test_skyypets_0.4.2.py"))
T42 = importlib.util.module_from_spec(_s42)
_s42.loader.exec_module(T42)
HK.run_compare = _cmp0

VERSION = "0.4.11"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.10.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.10.py")
PATCH = os.path.join(TOOLS, "pets_0_4_11_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T44.PKG = T410.PKG = PKG
KINDS = ["DragonPlain", "DragonTundra", "DragonFire", "DragonStorm", "DragonSky"]
AURES = ["Dragon_Egg_Plain", "Dragon_Egg_Tundra"]
OURS = ["Skyy_PetEgg_Dragon_Fire", "Skyy_PetEgg_Dragon_Thunder", "Skyy_PetEgg_Dragon_Air"]
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # the kit: the Dragons rows + the version text
    "PetEgg": ["~m adminEgg", "~m order"], "PetEggGive": ["+m gotText", "~m run"], "PetEggDefs": ["+m isDragon", "~<clinit>", "~m catOfId", "~m index", "~m nameOf", "~m rarOfId"],
    "PetHatchPage": ["~m begin", "~m build"],
    "PetHatchery": ["~m checks", "~m credits", "~m efuseWhy", "~m eggCell", "~m eggsHeld", "~m hatchLocked", "~m placeLocked", "~m removeLocked", "~m slotSub", "~m waitMs"],     # fixer 2: + checks / credits / removeLocked
    "PetKind": ["~<clinit>"], "PetLook": ["~m resolve"], "PetOps": ["~m chooseLocked", "~m createR", "~m starter"],
    "PetViews": ["~m census", "~m leave", "~m onRemoved", "~m second", "~m spawnNow", "~m want"],
    "PetWorld": ["+m modelPinned", "+m pinMap", "+m pinPick"], "PetWorldApi": ["+m modelPinned"],
    "PetsCfg": ["+f DELEM_MAP", "+f DELEM_TXT", "+f DRAGON_DOWN_MAX", "+f DRAGON_DOWN_MIN", "+f DRAGON_EGGS", "+f DRAGON_ELEMS", "+f DRAGON_GROW",
                "+f DRAGON_HATCH_S", "+f DRAGON_MAX", "+f DRAGON_S2", "+f DRAGON_S3", "+f DRAGON_S4", "+f DRAGON_VADULT", "+f DRAGON_VYOUNG", "+f DRAGON_W",
                "~<clinit>", "~m applyAll", "~m applyScalars", "~m checkEggOrder", "~m checkStarter", "~m checkStarterKind", "~m elemOf", "~m seed"],          # applyAll / seed: the fresh file text
    "PetsMigP5": ["~m mgLog", "~m run"], "SkyyPetsPlugin": ["~m setup"],          # the version text
    "PetsPage": ["~m build", "~m tip"],          # fixer B2: the slot icon
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["PetDragon"]
NEW_ENTRIES = sorted(["Server/NPC/Roles/SkyyPets/Skyy_Pet_Dragon.json", "Server/Models/SkyyPets/Skyy_Dragon_Storm.json", "Server/Models/SkyyPets/Skyy_Dragon_Sky.json",
                      "Common/NPC/SkyyPets/Skyy_Dragon_Storm/Texture.png", "Common/NPC/SkyyPets/Skyy_Dragon_Sky/Texture.png"]
                     + ["Server/Item/Items/SkyyPets/Dragons/%s.json" % i for i in OURS] + ["Common/Icons/ItemsGenerated/%s.png" % i for i in OURS]
                     + ["Common/Items/Pets/%s_Texture.png" % i for i in OURS] + ["Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_%s.json" % k for k in KINDS]
                     + ["Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k for k in KINDS])          # fixer B1: all five portraits are ours
_eq0 = HK.Child.eq


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + the lang file (the dragon egg lines) + the new dragon files"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == sorted(["manifest.json", "Server/Languages/en-US/server.lang"] + NEW_ENTRIES),
                          "C: non-class entries changed = manifest.json + server.lang + the %d new dragon files: %s" % (len(NEW_ENTRIES), sorted(set(got) ^ set(["manifest.json", "Server/Languages/en-US/server.lang"] + NEW_ENTRIES))))
    return _eq0(self, got, want, what)


HK.Child.eq = _eq


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.11 - build script') and g.count('VERSION = "0.4.11"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(g.count("= cls(") == o.count("= cls(") + 1 and 'dgc = cls("PetDragon")' in g, "S exactly one new class: PetDragon")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z = zipfile.ZipFile(jar)
    n = set(z.namelist())
    oz = set(zipfile.ZipFile(OLD_JAR).namelist())
    new = sorted(x for x in n - oz if not x.endswith(".class"))
    K.eq(new, NEW_ENTRIES, "S the jar's new non-class entries (nothing else)")
    K.check(not any("Nestkeeper" in x or "Plain_Dragon" in x or "Tundra_Dragon" in x or "Dragon_Egg_" in x for x in n),
            "S nothing of Aures' Nestkeeper in the jar (their models / icons / eggs are used by id / path only)")
    rd = json.loads(z.read("Server/NPC/Roles/SkyyPets/Skyy_Pet_Dragon.json"))
    rw = json.loads(z.read("Server/NPC/Roles/SkyyPets/Skyy_Pet_Walk.json"))
    rw2 = json.loads(json.dumps(rw))
    rw2["MotionControllerList"][0]["MaxWalkSpeed"] = 8
    K.check(rd == rw2 and rd["Invulnerable"] is True and rd["DefaultPlayerAttitude"] == "Ignore", "S the dragon role = the walk role (follow the owner, invulnerable, ignores players), MaxWalkSpeed 8")
    import skyyart as SA
    az = zipfile.ZipFile(B.ASSETS if hasattr(B, "ASSETS") else os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    for cid, par, parts in (("Skyy_Dragon_Storm", "Dragon_Fire", True), ("Skyy_Dragon_Sky", "Dragon_Frost", False)):
        mj = json.loads(z.read("Server/Models/SkyyPets/%s.json" % cid))
        vp = [x for x in az.namelist() if x.endswith("/%s.json" % par) and x.startswith("Server/Models/")][0]
        vt = json.loads(az.read(vp).decode("utf-8-sig"))["Texture"]
        K.check(mj.get("Parent") == par and mj.get("Texture") == "NPC/SkyyPets/%s/Texture.png" % cid and (("Particles" in mj) == parts)
                and set(mj) <= {"Parent", "Texture", "Particles"}, "S %s = Parent %s + our texture only (no vanilla data copied): %s" % (cid, par, mj))
        K.check(SA.png_size(z.read("Common/NPC/SkyyPets/%s/Texture.png" % cid)) == SA.png_size(az.read("Common/" + vt))
                and z.read("Common/NPC/SkyyPets/%s/Texture.png" % cid) != az.read("Common/" + vt), "S %s texture: the vanilla size, recoloured" % cid)
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for e in EGG.DRAGON_EGGS:
        if e[3] != "SkyyPets":
            K.check(("server.items.%s.name" % e[0]) not in lang, "S %s: Aures' egg keeps its own name (we never write their lang key)" % e[0])
            continue
        it = json.loads(z.read("Server/Item/Items/SkyyPets/Dragons/%s.json" % e[0]))
        K.check(it["Quality"] == "Legendary" and "Recipe" not in it and it["Icon"] == "Icons/ItemsGenerated/%s.png" % e[0]
                and it["Interactions"]["Secondary"]["Interactions"][0]["Page"]["Id"] == "SkyyPetsHatch" and it["MaxStack"] == EGG.MAX_STACK,
                "S %s: Legendary, never craftable, right-click = the Hatchery line" % e[0])
        K.check(("server.items.%s.name=%s\n" % (e[0], e[2])) in lang and ("server.items.%s.description=Legendary Dragon Egg - Hatch it in the Hatchery" % e[0]) in lang,
                "S %s: name + flavor in the lang file, the tier tag first (fixer 2: tools/tier_tags.py)" % e[0])
    for k in KINDS:
        pj = json.loads(z.read("Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_%s.json" % k))
        K.check(pj["Icon"] == "Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k and ("Common/" + pj["Icon"]) in n
                and pj.get("Variant") is True and "Recipe" not in pj, "S portrait %s -> %s (in OUR jar - fixer B1)" % (k, pj["Icon"]))
    pics = [z.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k) for k in KINDS]
    K.check(len(set(pics)) == 5 and all(SA.png_size(x) == (64, 64) for x in pics), "S five different 64 px dragon portraits")
    K.check(not any(("Plain_Dragon_Item" in x or "Tundra_Dragon_Item" in x) for x in lang.splitlines()) and
            not any(b"_Dragon_Item.png" in z.read(x) for x in n if x.startswith("Server/Item/Items/SkyyPets/")),
            "S fixer B1: no item of ours names an icon of Aures' pack")
    K.check("The egg can be traded or sold; the dragon that hatches is yours." in lang and "the dragon is bound to you" not in lang, "S fixer: the egg flavor wording")
    K.check(len(EGG.IDS) == 30 and not set(EGG.DRAGON_EGG_IDS) & set(EGG.IDS) and all(EGG.parse_id(i) is None for i in EGG.DRAGON_EGG_IDS),
            "S tools/skyyeggs.py: the 30 category eggs unchanged, the dragon eggs apart (Bazaar / Merchants / Collections never see them)")
    K.save()


# ======================================================================================================== DG: the dragon logic
def run_dg(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "dg")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    P_ = lambda n: JClass(PKG + n)
    Dg, Cfg, Look, Defs, Egg, Hy, Ops, Page, Buff, Kind, Store = (P_("PetDragon"), P_("PetsCfg"), P_("PetLook"), P_("PetEggDefs"), P_("PetEgg"),
                                                                 P_("PetHatchery"), P_("PetOps"), P_("PetsPage"), P_("PetBuff"), P_("PetKind"), P_("PetStore"))
    Random = JClass("java.util.Random")
    told = []
    W["names"]["00000000-0000-0000-0000-000000009401"] = "Drake"
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])),
                                                      "byName": lambda n: W["UUID"].fromString("00000000-0000-0000-0000-000000009401") if str(n) == "Drake" else None,
                                                      "nameOf": lambda u: W["names"].get(str(u), str(u)), "tell": lambda u, t, c: told.append(str(t))})
    # ---- the kinds
    K.eq([str(x) for x in Dg.KINDS], KINDS, "DG the five dragon kinds")
    for k in KINDS:
        pk = Cfg.kind(k)
        K.check(pk is not None and str(pk.skill) == "Combat" and int(pk.rarity) == 3 and bool(Cfg.summonable(k)) and not bool(Cfg.isMount(k)),
                "DG %s: a Combat kind starting Rare, summonable (fighter), not a mount yet" % k)
    K.eq([str(Kind.display(k)) for k in KINDS], ["Plain Dragon", "Tundra Dragon", "Fire Dragon", "Storm Dragon", "Sky Dragon"], "DG display names")
    K.check(Dg.isDragon("dragonplain") and not Dg.isDragon("Wolf") and not Dg.isDragon(None) and Dg.kindIndex("DragonSky") == 4, "DG isDragon (any case)")
    # ---- stages + sizes (rows 4 / 7 / 10, grow 0.6 %, max x1.3; vanilla 0.3 -> 1.0 = the spec section 8 default, fixer 2)
    st = [int(Dg.stage(lv)) for lv in (1, 3, 4, 6, 7, 9, 10, 50, 100)]
    K.eq(st, [1, 1, 2, 2, 3, 3, 4, 4, 4], "DG stages: Weakling 1-3, Smalling 4-6, Biteling 7-9, Flyling 10+")
    K.eq([str(Dg.stageName(s)) for s in (1, 2, 3, 4, 0, 9)], ["Weakling", "Smalling", "Biteling", "Flyling", "Weakling", "Weakling"], "DG stage names")
    sz = [round(float(Dg.size("DragonPlain", lv)), 4) for lv in (1, 9, 10, 11, 50, 60, 100)]
    K.eq(sz, [1.0, 1.0, 1.0, 1.006, 1.24, 1.3, 1.3], "DG Nestkeeper size: x1 to Lv 10, +0.6 % a level, x1.24 at Lv 50 (no rebirth), cap x1.3 from Lv 60")
    vz = [round(float(Dg.size("DragonFire", lv)), 4) for lv in (1, 4, 10, 11, 60, 100)]
    K.eq(vz, [0.3, round(0.3 + 0.7 * 3 / 9, 4), 1.0, 1.006, 1.3, 1.3], "DG vanilla size: x0.3 at Lv 1 -> x1.0 at Lv 10, then the growth (x1.3 max)")
    K.eq([str(Dg.model("DragonPlain", lv)) for lv in (1, 4, 7, 10)], ["Nestkeeper_Dragon_Plain_%d" % i for i in (1, 2, 3, 4)], "DG Plain stage models _1.._4")
    K.eq([str(Dg.model("DragonTundra", 8)), str(Dg.model("DragonFire", 1)), str(Dg.model("DragonStorm", 50)), str(Dg.model("DragonSky", 50))],
         ["Nestkeeper_Dragon_Tundra_3", "Dragon_Fire", "Skyy_Dragon_Storm", "Skyy_Dragon_Sky"], "DG the other models")
    K.check(Dg.model("Wolf", 5) is None and abs(float(Dg.size("Wolf", 5)) - 1.0) < 1e-9, "DG not a dragon: no model")

    def lk(k, lv, sl):
        r = Look.resolve(k, lv, sl)
        return None if r is None else [str(r[0]), round(float(r[1]), 4), int(r[2]), bool(r[3])]
    K.eq([lk("DragonPlain", 5, 1), lk("DragonPlain", 5, 2), lk("DragonFire", 10, 2)],
         [None, ["Nestkeeper_Dragon_Plain_2", -1.0, 0, False], ["Dragon_Fire", -1.0, 0, False]],
         "DG PetLook.resolve: a dragon in the PET slot shows nothing; in the summon slot the stage model x its own size (negative), walking")
    K.check(lk("Fox", 5, 1) is not None and lk("Fox", 5, 1)[0] == "Fox", "DG other kinds unchanged")
    Cfg.DRAGON_S2, Cfg.DRAGON_S3, Cfg.DRAGON_S4 = 9, 5, 3
    K.eq(list(Dg.stageLv()), [9, 9, 9], "DG stage rows out of order -> put in order (never a stage that shrinks)")
    Cfg.DRAGON_S2, Cfg.DRAGON_S3, Cfg.DRAGON_S4 = 2, 3, 5
    K.eq([int(Dg.stage(lv)) for lv in (1, 2, 3, 5)], [1, 2, 3, 4], "DG stage rows 2 / 3 / 5 live")
    Cfg.DRAGON_GROW, Cfg.DRAGON_MAX = 0.0, 1.3
    K.check(abs(float(Dg.size("DragonPlain", 90)) - 1.0) < 1e-9, "DG growth 0 = no growth")
    Cfg.DRAGON_GROW, Cfg.DRAGON_MAX = 10.0, 0.5
    K.check(abs(float(Dg.size("DragonPlain", 90)) - 1.0) < 1e-9, "DG a max size below 1 = x1")
    Cfg.DRAGON_VYOUNG, Cfg.DRAGON_VADULT = 0.0, 99.0
    K.check(abs(float(Dg.size("DragonFire", 1)) - 0.05) < 1e-9 and abs(float(Dg.size("DragonFire", 5)) - 3.0) < 1e-9, "DG vanilla sizes clamped 0.05 .. 3")
    Cfg.reloadAll()
    K.check(int(Cfg.DRAGON_S4) == 10 and abs(float(Cfg.DRAGON_GROW) - 0.6) < 1e-9 and abs(float(Cfg.DRAGON_VADULT) - 1.0) < 1e-9 and abs(float(Cfg.DRAGON_VYOUNG) - 0.3) < 1e-9, "DG reload = the defaults again")
    # ---- elements
    K.eq([str(Cfg.elemOf(k)) for k in KINDS], ["Earth", "Water", "Fire", "Thunder", "Air"], "DG dragon elements (pets.dragon.element defaults)")
    Cfg.ELEMS = str(Cfg.ELEMS) + ", DragonFire=Water"
    K.check(str(Cfg.elemOf("DragonFire")) == "Water", "DG pets.element listing a dragon wins")
    Cfg.DRAGON_ELEMS = "DragonPlain=Thunder, DragonSky=none"
    K.check(str(Cfg.elemOf("DragonPlain")) == "Thunder" and Cfg.elemOf("DragonSky") is None and Cfg.elemOf("DragonTundra") is None and str(Cfg.elemOf("Fox")) == "Fire",
            "DG a live edit of pets.dragon.element (none / unlisted = no element; other kinds unchanged)")
    K.check(Cfg.checkElem("pets.dragon.element", "DragonPlain=Ice") is not None, "DG pets.dragon.element check= hook")
    Cfg.reloadAll()
    # ---- egg ids
    nE = len(list(Defs.IDS))
    K.eq([int(Defs.index(i)) for i in EGG.DRAGON_EGG_IDS], list(range(nE, nE + 5)), "DG the dragon eggs are pet eggs after the 30")
    K.check(all(Defs.isDragon(i) and int(Defs.catOfId(i)) == -1 and int(Defs.rarOfId(i)) == 0 for i in EGG.DRAGON_EGG_IDS)
            and not Defs.isDragon("Skyy_PetEgg_Combat_Rare") and int(Defs.catOfId("Skyy_PetEgg_Combat_Rare")) == 3 and int(Defs.rarOfId("Skyy_PetEgg_Combat_Rare")) == 3
            and int(Defs.index("Food_Egg")) == -1 and not Defs.isDragon("Food_Egg"), "DG no category / rarity for a dragon egg; the 30 unchanged")
    K.eq([str(Defs.nameOf(i)) for i in EGG.DRAGON_EGG_IDS], [e[2] for e in EGG.DRAGON_EGGS], "DG dragon egg names")
    K.eq([str(Dg.eggKind(i)) for i in EGG.DRAGON_EGG_IDS], KINDS, "DG pets.dragon.eggs default: each egg its dragon")
    K.eq([str(Dg.eggFor(w)) if Dg.eggFor(w) is not None else None for w in ("plain", "TUNDRA", "fire", "thunder", "Storm", "sky", "air", "DragonFire", "Dragon_Egg_Plain", "void", None)],
         ["Dragon_Egg_Plain", "Dragon_Egg_Tundra", "Skyy_PetEgg_Dragon_Fire", "Skyy_PetEgg_Dragon_Thunder", "Skyy_PetEgg_Dragon_Thunder", "Skyy_PetEgg_Dragon_Air",
          "Skyy_PetEgg_Dragon_Air", "Skyy_PetEgg_Dragon_Fire", "Dragon_Egg_Plain", None, None], "DG /petadmin egg dragon <word>")
    K.check(Dg.checkEggs("k", "Dragon_Egg_Plain=DragonFire, Skyy_PetEgg_Dragon_Air=DragonSky") is None and Dg.checkEggs("k", "-") is None
            and "not a dragon egg" in str(Dg.checkEggs("k", "Food_Egg=DragonFire")) and "not a dragon" in str(Dg.checkEggs("k", "Dragon_Egg_Plain=Wolf"))
            and "twice" in str(Dg.checkEggs("k", "Dragon_Egg_Plain=DragonFire,Dragon_Egg_Plain=DragonSky")) and "needs" in str(Dg.checkEggs("k", "Dragon_Egg_Plain")),
            "DG pets.dragon.eggs check= hook")
    Cfg.DRAGON_EGGS = "Dragon_Egg_Plain=DragonFire, Dragon_Egg_Tundra=Wolf"
    K.check(str(Dg.eggKind("Dragon_Egg_Plain")) == "DragonFire" and Dg.eggKind("Dragon_Egg_Tundra") is None and Dg.eggKind("Skyy_PetEgg_Dragon_Fire") is None
            and Dg.eggKind("Food_Egg") is None, "DG a remapped / unlisted / non-dragon entry")
    Cfg.DRAGON_EGGS = "-"
    K.check(all(Dg.eggKind(i) is None for i in EGG.DRAGON_EGG_IDS), "DG - = no dragon hatches")
    Cfg.reloadAll()
    # ---- the rarity row + roll
    K.eq(list(Dg.weights()), [0, 0, 6000, 3000, 900, 100], "DG pets.dragon.rarity default")
    K.check(Dg.checkW("k", "0/0/6000/3000/900/100") is None and "never below Rare" in str(Dg.checkW("k", "10/0/6000/3000/900/100"))
            and Dg.checkW("k", "1/2/3") is not None and Dg.checkW("k", "0/0/0/0/0/0") is not None, "DG pets.dragon.rarity check= hook")
    Cfg.DRAGON_W = "5000/5000/0/0/0/1"
    K.eq(list(Dg.weights()), [0, 0, 0, 0, 0, 1], "DG a hand-edited Common / Uncommon weight is dropped (never below Rare)")
    Cfg.DRAGON_W = "9000/1000/0/0/0/0"
    K.eq(list(Dg.weights()), [0, 0, 6000, 3000, 900, 100], "DG nothing left -> the built-in odds")
    Cfg.reloadAll()
    rn = Random(4242)
    cnt = [0] * 7
    for _ in range(20000):
        cnt[int(Dg.rollRarity(rn))] += 1
    K.check(cnt[1] == 0 and cnt[2] == 0 and 0.57 < cnt[3] / 20000.0 < 0.63 and 0.27 < cnt[4] / 20000.0 < 0.33 and 0.07 < cnt[5] / 20000.0 < 0.11 and 0.004 < cnt[6] / 20000.0 < 0.017,
            "DG 20,000 rolls: Rare ~60 %%, Epic ~30 %%, Legendary ~9 %%, Mythic ~1 %%, never Common / Uncommon: %s" % cnt[1:])
    K.eq(str(Dg.rarityText()), "Rare 60% - Epic 30% - Legendary 9.0% - Mythic 1.0%", "DG rarity text")
    # ---- dragons never from a category egg
    K.check(not any(Dg.isDragon(x) for x in Egg.order("Combat")) and len(list(Egg.order("Combat"))) == 14, "DG Combat eggs never roll a dragon (14 combat kinds)")
    K.check("dragon" in str(Cfg.checkEggOrder("pets.egg.order.combat", "Wolf, DragonFire")), "DG pets.egg.order refuses a dragon")
    Cfg.EGG_O_COMBAT = "DragonFire, Wolf"
    o_ = [str(x) for x in Egg.order("Combat")]
    K.check("Wolf" in o_ and not any(x.startswith("Dragon") for x in o_), "DG a hand-edited order naming a dragon: the dragon is left out: %s" % o_)
    Cfg.reloadAll()
    # ---- the Hatchery
    u, k, r = T44._mk(W, 9401)
    inv = T41.Inv({"Dragon_Egg_Plain": 2, "Skyy_PetEgg_Dragon_Fire": 1, "Skyy_PetEgg_Combat_Common": 1})
    held = [str(x) for x in Hy.eggsHeld(u, T41.proxy_inv(inv))]
    K.eq(held, ["Skyy_PetEgg_Combat_Common", "Dragon_Egg_Plain", "Skyy_PetEgg_Dragon_Fire"], "DG the Hatchery grid: the dragon eggs after the others (top tier last)")
    K.check("cannot be fused" in str(Hy.efuseWhy(u, T41.proxy_inv(inv), "Dragon_Egg_Plain")) and "cannot be fused" in str(Hy.efuseAsk(u, T41.proxy_inv(inv), "Dragon_Egg_Plain")),
            "DG Fuse eggs: dragon eggs refused (the grid cells: ST)")
    K.check("Hatches: your Plain Dragon (Earth) - one dragon per profile. Using it in your hand hatches a wild dragon instead." == "Hatches: " + str(Dg.eggText("Dragon_Egg_Plain"))
            and str(Dg.eggText("Skyy_PetEgg_Dragon_Fire")) == "your Fire Dragon (Fire) - one dragon per profile.", "DG the egg texts")
    p1 = T44._place(W, u, inv, "Dragon_Egg_Plain")
    K.check(p1[0].startswith("+Plain Dragon Egg is in Hatchery slot 1 - it hatches in 1h 00m") and inv.count("Dragon_Egg_Plain") == 1
            and str(r.get("hatchery.1")).startswith("Dragon_Egg_Plain|"), "DG place Aures' egg (taken from the inventory, counted): %s" % p1)
    W["PetEgg"].NOFORCE.clear()
    T44._tick(W, u, r, inv, plus=61000)
    p2 = T44._place(W, u, inv, "Skyy_PetEgg_Dragon_Fire")
    K.check(p2[0].startswith("-One dragon per profile - your Plain Dragon Egg is already in the Hatchery") and inv.count("Skyy_PetEgg_Dragon_Fire") == 1
            and r.get("hatchery.2") is None, "DG a second dragon egg refused while one waits: %s" % p2)
    K.check("already in the Hatchery" in str(Dg.placeWhy(r, "Skyy_PetEgg_Dragon_Fire")), "DG ... placeWhy says why (the cell footer)")
    ln = Hy.line(r, 1)
    K.check(int(Hy.waitMs("Dragon_Egg_Plain")) == 3600000 and "dragon eggs take 1h 00m" in str(Hy.slotSub(ln, Hy.now())), "DG 1 h wait: %s" % Hy.slotSub(ln, Hy.now()))
    h0 = [str(x) for x in Hy.hatch(u, 1, str(ln[2]), "harness")]
    K.check(h0[0].startswith("-Still hatching") and r.count() == 0, "DG not ready yet: %s" % h0[0])
    Hy.CLOCK_OFF = 3601 * 1000
    W["PetEgg"].HATCHING.clear()
    Egg.RNG = Random(7)
    h1 = [str(x) if x is not None else None for x in Hy.hatch(u, 1, str(ln[2]), "harness")]
    Egg.RNG = None
    pid = h1[2]
    K.check(h1[0].startswith("+You hatched a ") and h1[0].endswith(" Plain Dragon!") and str(r.kindOf(pid)) == "DragonPlain" and int(r.rarityOf(pid)) >= 3
            and r.get("hatchery.1") is None and int(r.levelOf(pid)) == 1 and str(r.get("pet.%s.src" % pid)).startswith("egg:Dragon_Egg_Plain:"),
            "DG READY -> hatched the egg's own dragon at Rare+ (no reel 1), Lv 1, the slot empty: %s" % h1[0])
    K.check(str(r.get("hatch.unseen." + h1[1])) == "Dragon_Egg_Plain|DragonPlain|%d" % int(r.rarityOf(pid)) and int(Dg.HATCHED.get()) == 1, "DG the reveal line waits (hatch.unseen)")
    p3 = T44._place(W, u, inv, "Skyy_PetEgg_Dragon_Fire")
    K.check(p3[0].startswith("-One dragon per profile - you already have your Plain Dragon") and inv.count("Skyy_PetEgg_Dragon_Fire") == 1, "DG owning a dragon: no dragon egg goes in: %s" % p3)
    # an egg already waiting when a dragon arrives another way (an admin give): the hatch refuses, the egg waits in its slot
    u2, k2, r2 = T44._mk(W, 9402)
    inv2 = T41.Inv({"Skyy_PetEgg_Dragon_Thunder": 1})
    T44._place(W, u2, inv2, "Skyy_PetEgg_Dragon_Thunder")
    g1 = str(Ops.create(r2, None, "DragonSky", 4, 5, 0, "admin give", "harness", True))
    K.check(not g1.startswith("-") and str(r2.kindOf(g1)) == "DragonSky", "DG /petadmin give of a first dragon works: %s" % g1)
    g2 = str(Ops.create(r2, None, "DragonFire", 3, 1, 0, "admin give", "harness", True))
    K.check(g2.startswith("-One dragon per profile - you already have your Sky Dragon") and r2.count() == 1, "DG a second dragon by /petadmin give refused: %s" % g2)
    g3 = str(Ops.createR(r2, g1, "DragonSky", 4, 5, 0, 0, "restore", "harness", False))
    K.check(g3.startswith("-Pet ") or g3 == g1 or g3.startswith("-One dragon"), "DG restoring the same dragon id never makes a second dragon: %s" % g3)
    g4 = str(Ops.createR(r2, "zz00restore", "DragonPlain", 4, 5, 0, 0, "restore", "harness", False))
    K.check(g4.startswith("-One dragon per profile") and r2.count() == 1, "DG restoring ANOTHER dragon refused: %s" % g4)
    ln2 = Hy.line(r2, 1)
    Hy.CLOCK_OFF = 2 * 3601 * 1000          # (placed under the first offset)
    W["PetEgg"].HATCHING.clear()
    h2 = [str(x) if x is not None else None for x in Hy.hatch(u2, 1, str(ln2[2]), "harness")]
    K.check(h2[0].startswith("-One dragon per profile - you already have your Sky Dragon. The egg waits in its slot.") and r2.get("hatchery.1") is not None and r2.count() == 1,
            "DG a waiting dragon egg of a profile that got a dragon meanwhile: refused, the egg stays: %s" % h2[0])
    K.check(int(Dg.REFUSED.get()) >= 3, "DG refusals counted (%d)" % int(Dg.REFUSED.get()))
    Hy.CLOCK_OFF = 0
    # the egg row off -> placing refused with the reason
    Cfg.DRAGON_EGGS = "-"
    u3, k3, r3 = T44._mk(W, 9403)
    inv3 = T41.Inv({"Dragon_Egg_Tundra": 1})
    p4 = T44._place(W, u3, inv3, "Dragon_Egg_Tundra")
    K.check(p4[0].startswith("-This dragon egg does not hatch on this server") and inv3.count("Dragon_Egg_Tundra") == 1, "DG pets.dragon.eggs - : refused, the egg kept: %s" % p4)
    Cfg.reloadAll()
    Cfg.KINDS_OFF = "DragonTundra"
    p5 = T44._place(W, u3, inv3, "Dragon_Egg_Tundra")
    K.check(p5[0].startswith("-The Tundra Dragon is switched off"), "DG a dragon kind switched off: refused: %s" % p5)
    Cfg.reloadAll()
    # from the Void (SkyySacks) too
    W["V"].live["Dragon_Egg_Tundra"] = 1
    inv4 = T41.Inv({})
    u4, k4, r4 = T44._mk(W, 9404)
    p6 = T44._place(W, u4, inv4, "Dragon_Egg_Tundra")
    K.check(p6[0].startswith("+Tundra Dragon Egg is in Hatchery slot 1") and W["V"].live["Dragon_Egg_Tundra"] == 0 and p6[2] == "void", "DG a dragon egg from the Void: %s" % p6)
    # ---- the card, the buffs
    tip = str(Page.tip(r, pid, 0))
    K.check("Dragon: Weakling (size x1) - Smalling at Lv 4" in tip and "Shows only in the summon slot. One dragon per profile." in tip
            and "Fighting, riding and flying come in a later version." in tip and "Element: Earth</color>" in tip, "DG the card: %s" % [l for l in tip.split("\n") if "Dragon" in l or "Shows" in l])
    r.set("pet.%s.level" % pid, "60")
    tip60 = str(Page.tip(r, pid, 0))
    K.check("Dragon: Flyling (size x1.3)" in tip60 and "still growing" not in tip60, "DG Lv 60: Flyling x1.3, done growing")
    r.set("pet.%s.level" % pid, "20")
    t20 = [l for l in str(Page.tip(r, pid, 0)).split(chr(10)) if l.startswith("Dragon:")]
    K.check(t20 == ["Dragon: Flyling (size x1.06) - still growing"], "DG Lv 20: x1.06, still growing: %s" % t20)
    K.check(str(Dg.card(r, "nope")) == "" and str(Dg.card(None, pid)) == "", "DG not a dragon: no card lines")
    r.set("active.1", pid)
    keys = [str(x) for x in Kind.STAT_KEYS]
    t = list(Buff.compute2(u, r, "w"))
    s = dict((keys[i], float(t[i])) for i in range(len(t)) if abs(float(t[i])) > 1e-9)
    f = float(Cfg.factor(int(r.rarityOf(pid)))) * 20 / 100.0
    K.check(abs(s.get("str", 0) - 28 * f) < 1e-6 and abs(s.get("cd", 0) - 21 * f) < 1e-6 and abs(s.get("def", 0) - 11 * f) < 1e-6
            and abs(s.get("fEarth", 0) - 1.0 * f) < 1e-6 and abs(s.get("dEarth", 0) - 15.0 * f) < 1e-6, "DG a pet-slot Plain Dragon Lv 20 gives its stats + Earth (pets:stats): %s" % s)
    # ---- /petadmin egg <player> dragon <word>
    q = []
    P_("PetEggGive").QUEUE_API = JProxy("java.util.function.Function", dict={"apply": lambda a: (q.append([str(x) for x in a]), JClass("java.lang.Boolean").TRUE)[1]})
    a1 = str(Egg.admin("harness", "egg", "Drake", "dragon", "thunder", "2"))
    a2 = str(Egg.admin("harness", "egg", "Drake", "Dragon", "void", None))
    a3 = str(Egg.admin("harness", "egg", "Drake", "dragon", "plain", "0"))
    a4 = str(Egg.admin("harness", "egg", "Drake", "Mining", "Rare", None))
    K.check(a1.startswith("+Sent 2 x Storm Dragon Egg (Skyy_PetEgg_Dragon_Thunder) to ") and a1.endswith("it hatches in the Hatchery (/pets).") and q[0][1:3] == ["Skyy_PetEgg_Dragon_Thunder", "2"]
            and a2.startswith("-Which dragon egg? plain, tundra, fire, thunder, air") and a3.startswith("-How many") and a4.startswith("+Sent 1 x Rare Mining Egg"),
            "DG /petadmin egg dragon: %s / %s / %s / %s" % (a1, a2, a3, a4))
    # ---- FX fixer B2: Aures' Dragon Nestkeeper NOT loaded (their egg item / stage models missing) -> refused with the reason, never a broken item
    miss = set(["Dragon_Egg_Plain", "Nestkeeper_Dragon_Tundra_1"])
    u6, k6, r6 = T44._mk(W, 9406)
    inv6 = T41.Inv({"Dragon_Egg_Tundra": 1})
    W["PetEgg"].NOFORCE.clear()
    T44._place(W, u6, inv6, "Dragon_Egg_Tundra")          # placed while the pack was there
    W["PetEgg"].NOFORCE.clear()
    u8, k8, r8 = T44._mk(W, 9408)
    inv8 = T41.Inv({"Dragon_Egg_Plain": 1})
    p8a = T44._place(W, u8, inv8, "Dragon_Egg_Plain")          # fixer 2: Aures' Plain egg in a slot, then the pack goes
    W["PetEgg"].NOFORCE.clear()
    K.check(p8a[0].startswith("+") and inv8.count("Dragon_Egg_Plain") == 0, "FX2 setup: Plain egg placed while the pack was there: %s" % p8a[0])
    T44._tick(W, u8, r8, inv8, plus=61000)
    Dg.ASSET_API = JProxy("java.util.function.Predicate", dict={"test": lambda x: str(x) not in miss})
    K.check(not Dg.itemOk("Dragon_Egg_Plain") and Dg.itemOk("Dragon_Egg_Tundra") and Dg.itemOk("Skyy_PetEgg_Dragon_Fire") and not Dg.itemOk(None)
            and Dg.lookOk(0) and not Dg.lookOk(1) and Dg.lookOk(2) and Dg.lookOk(4) and not Dg.lookOk(-1), "FX itemOk / lookOk (only Aures' ids are looked up)")
    K.check(Dg.eggKind("Dragon_Egg_Plain") is None and Dg.eggKind("Dragon_Egg_Tundra") is None and str(Dg.eggKind("Skyy_PetEgg_Dragon_Fire")) == "DragonFire"
            and str(Dg.rowKind("Dragon_Egg_Plain")) == "DragonPlain", "FX eggKind: Aures' egg without its item / its dragon's models = nothing hatches; ours unchanged")
    u5, k5, r5 = T44._mk(W, 9405)
    inv5 = T41.Inv({"Dragon_Egg_Plain": 1, "Dragon_Egg_Tundra": 1})
    p7 = T44._place(W, u5, inv5, "Dragon_Egg_Plain")
    p8 = T44._place(W, u5, inv5, "Dragon_Egg_Tundra")
    K.check(p7[0].startswith("-This dragon egg needs the Dragon Nestkeeper mod") and p8[0].startswith("-This dragon egg needs the Dragon Nestkeeper mod")
            and inv5.count("Dragon_Egg_Plain") == 1 and inv5.count("Dragon_Egg_Tundra") == 1 and r5.get("hatchery.1") is None, "FX place refused, eggs kept: %s / %s" % (p7[0], p8[0]))
    K.check("needs the Dragon Nestkeeper mod" in str(Dg.eggText("Dragon_Egg_Plain")), "FX the cell text says why: %s" % Dg.eggText("Dragon_Egg_Plain"))
    # ---- FX2 (second review): the Eggs grid, the take-out, the credit / check lines, every stage model
    inv9 = T41.Inv({"Dragon_Egg_Plain": 1, "Dragon_Egg_Tundra": 1, "Skyy_PetEgg_Dragon_Fire": 1})
    K.eq([str(x) for x in Hy.eggsHeld(u5, T41.proxy_inv(inv9))], ["Dragon_Egg_Tundra", "Skyy_PetEgg_Dragon_Fire"],
         "FX2 the Eggs grid never lists an egg id the server has not loaded (Aures' Plain egg here)")
    t8 = T44._takeout(W, u8, inv8, 1)
    K.check(t8[0] == "-The Plain Dragon Egg comes with the Dragon Nestkeeper mod, which is not loaded on this server - it stays in its slot."
            and inv8.count("Dragon_Egg_Plain") == 0 and str(r8.get("hatchery.1")).startswith("Dragon_Egg_Plain|") and len(r8.keysWith("eggcredit.")) == 0,
            "FX2 take-out of Aures' egg without the pack: refused, the egg stays in its slot, nothing given: %s" % t8[0])
    r8.set("eggcredit.fx2credit", "Dragon_Egg_Plain|1|1|2")          # a take-out credit open from before a stop
    r8.set("eggcheck.fx2check", "Dragon_Egg_Plain|1|place|inv")      # a place cut off before its save (the player was saved without it)
    told[:] = []
    Hy.checks(u8, r8, T41.proxy_inv(inv8))
    T44._tick(W, u8, r8, inv8)
    K.check(inv8.count("Dragon_Egg_Plain") == 0 and r8.get("eggcredit.fx2credit") is not None and r8.get("eggcheck.fx2check") is not None
            and not any("Make room" in x for x in told), "FX2 the credit + check lines wait for the pack (no unknown item, no 'make room' loop): %s" % told)
    pm = JProxy("java.util.function.Predicate", dict={"test": lambda x: str(x) != "Nestkeeper_Dragon_Plain_4"})
    Dg.ASSET_API = pm
    K.check(not Dg.lookOk(0) and Dg.lookOk(1) and Dg.eggKind("Dragon_Egg_Plain") is None and Look.resolve("DragonPlain", 2, 2) is None,
            "FX2 lookOk needs all four stage models (a partial Nestkeeper without _4: no hatch, nothing shown - never a Flyling that cannot spawn)")
    Dg.ASSET_API = JProxy("java.util.function.Predicate", dict={"test": lambda x: str(x) not in miss})
    ln6 = Hy.line(r6, 1)
    Hy.CLOCK_OFF = 3601 * 1000
    W["PetEgg"].HATCHING.clear()
    h6 = [str(x) if x is not None else None for x in Hy.hatch(u6, 1, str(ln6[2]), "harness")]
    Hy.CLOCK_OFF = 0
    K.check(h6[0] == "-This dragon egg needs the Dragon Nestkeeper mod, which is not loaded on this server. The egg waits in its slot." and r6.get("hatchery.1") is not None
            and r6.count() == 0, "FX an egg already in a slot when the pack goes: no hatch, the egg waits: %s" % h6[0])
    K.check(Look.resolve("DragonTundra", 5, 2) is None and Look.resolve("DragonPlain", 5, 2) is not None and Look.resolve("DragonFire", 5, 2) is not None,
            "FX a dragon whose models are missing shows nothing in the summon slot (no spawn attempt every second)")
    q[:] = []
    P_("PetEggGive").QUEUE_API = JProxy("java.util.function.Function", dict={"apply": lambda a: (q.append([str(x) for x in a]), JClass("java.lang.Boolean").TRUE)[1]})
    a5 = str(Egg.admin("harness", "egg", "Drake", "dragon", "plain", None))
    a6 = str(Egg.admin("harness", "egg", "Drake", "dragon", "fire", None))
    K.check(a5 == "-Plain Dragon Egg (Dragon_Egg_Plain) is not loaded on this server - it comes with the Dragon Nestkeeper mod." and len(q) == 1 and q[0][1] == "Skyy_PetEgg_Dragon_Fire"
            and a6.startswith("+Sent 1 x Fire Dragon Egg"), "FX /petadmin egg dragon plain without the pack: refused, nothing queued: %s / %s" % (a5, a6))
    P_("PetEggGive").QUEUE_API = None
    Dg.ASSET_API = None
    K.check(Dg.eggKind("Dragon_Egg_Plain") is not None and Dg.itemOk("Dragon_Egg_Plain"), "FX no seam + no asset store (the harness) = loaded (in game the store is always there)")
    Hy.checks(u8, r8, T41.proxy_inv(inv8))          # the check first: count 0 = before - 1 -> given back (1)
    T44._tick(W, u8, r8, inv8)                     # then the credit: count 1 = before 1 -> given again (2), the line re-armed for this session
    K.check(inv8.count("Dragon_Egg_Plain") == 2 and str(r8.get("eggcredit.fx2credit")).startswith("Dragon_Egg_Plain|1|") and str(r8.get("eggcredit.fx2credit")) != "Dragon_Egg_Plain|1|1|2"
            and r8.get("eggcheck.fx2check") is None,
            "FX2 the pack back: the waiting credit + check lines give their eggs (%d)" % inv8.count("Dragon_Egg_Plain"))
    r8.set("eggcredit.fx2credit", None)          # (the re-armed credit settles on its own; cleared here so the next move is not held back)
    t8b = T44._takeout(W, u8, inv8, 1)
    K.check(t8b[0].startswith("+The Plain Dragon Egg is back in your inventory") and inv8.count("Dragon_Egg_Plain") == 3, "FX2 ... and the take-out works again: %s" % t8b[0])
    # ---- FX fixer A1: the give line counts what arrived
    Gv = P_("PetEggGive")
    K.eq([str(Gv.gotText("Plain Dragon Egg", 0)), str(Gv.gotText("Fire Dragon Egg", 2))],
         ["[Pets] The Plain Dragon Egg could not be given (it is not loaded on this server) - an admin can check the server log.",
          "[Pets] You got 2 x Fire Dragon Egg - hatch it in /pets > Hatchery."], "FX the egg give line")
    # ---- FX fixer A2: a dragon is never a starter pet
    K.check("is a dragon" in str(Cfg.checkStarter("pets.starter", "DragonFire")) and Cfg.checkStarter("pets.starter", "Rabbit") is None
            and Cfg.checkStarter("pets.starter", "none") is None and "is a dragon" in str(Cfg.checkStarterKind("pets.starter.combat", " DragonSky "))
            and Cfg.checkStarterKind("pets.starter.combat", "Dog") is None, "FX the starter rows refuse a dragon")
    Cfg.STARTER, Cfg.STARTER_CHOOSE = "DragonFire", False
    u7, k7, r7 = T44._mk(W, 9407)
    r7.set("starter", None)
    K.check(not bool(Ops.starter(u7, r7)) and int(r7.count()) == 0 and r7.get("starter") is None, "FX a hand-edited dragon starter gives nothing")
    Cfg.STARTER = "Rabbit"
    K.check(bool(Ops.starter(u7, r7)) and int(r7.count()) == 1, "FX ... the normal starter still works")
    Cfg.reloadAll()
    Cfg.STARTER_COMBAT = "DragonFire"
    r7.set("starter", "choose")
    K.check(str(Ops.chooseLocked(r7, 3, "harness")).startswith("-The Combat starter pet is not available") and int(r7.count()) == 1, "FX the starter choice never makes a dragon")
    Cfg.reloadAll()
    P_("PetEggGive").QUEUE_API = None
    K.save()


# ======================================================================================================== VW: the views on a stand-in world
def run_vw(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "vw")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JObject
    P_ = lambda n: JClass(PKG + n)
    Dg, Cfg, Views, PW, Store, Ops, Log = P_("PetDragon"), P_("PetsCfg"), P_("PetViews"), P_("PetWorld"), P_("PetStore"), P_("PetOps"), P_("PetsLog")
    told = []
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                      "nameOf": lambda u: "Rider", "tell": lambda u, t, c: told.append(str(t))})
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.server.core.universe.world.World")
    RR = JClass("com.hypixel.hytale.component.RemoveReason")
    UUID = W["UUID"]
    st = U.allocateInstance(Store_.class_)
    w = U.allocateInstance(World.class_)
    ents, jobs, calls = {}, [], []
    nxt = [100]

    def new_ref(uuid, role, pos):
        nxt[0] += 1
        r = Ref(st, nxt[0])
        ents[int(r.getIndex())] = {"uuid": uuid, "role": role, "pos": list(pos), "model": None, "removed": False, "ref": r}
        return r
    ent = lambda r: None if r is None else ents.get(int(r.getIndex()))
    uo = UUID.fromString("00000000-0000-0000-0000-000000009501")
    oref = new_ref(uo, "player", [10.0, 70.0, 10.0])
    roles = {"Skyy_Pet_Walk": 11, "Skyy_Pet_Fly": 12, "Skyy_Pet_Dragon": 13, "Test_Pet": 7, "Test_Fly": 8}
    vs = {"Nestkeeper_Dragon_Plain_1": 0.325, "Nestkeeper_Dragon_Plain_2": 0.55, "Nestkeeper_Dragon_Plain_4": 1.55, "Dragon_Fire": 1.25}

    def spawn(s, role, x, y, z, yaw, model):
        rn = [k for k, v in roles.items() if v == int(role)][0]
        r = new_ref(UUID.randomUUID(), rn, [float(x), float(y), float(z)])
        ent(r)["model"] = str(model)
        calls.append(("spawn", rn, str(model)))
        return r

    def model(mid, sc):
        calls.append(("model", str(mid), round(float(sc), 4)))
        return JString("%s@%s" % (mid, round(float(sc), 4)))

    def pinned(mid, sc, seed):
        calls.append(("pinned", str(mid), round(float(sc), 4), str(seed)))
        return JString("%s@%s#%s" % (mid, round(float(sc), 4), seed))

    def remove(acc, r):
        e = ent(r)
        if e is None or e["removed"]:
            return False
        e["removed"] = True
        calls.append(("remove", e["role"]))
        return True

    def pos(acc, r):
        e = ent(r)
        return None if e is None or e["removed"] else JArray(JDouble)(e["pos"])
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": model, "modelPinned": pinned, "spawn": spawn, "store": lambda w_: st,
           "ownerRef": lambda u_: oref if str(u_) == str(uo) else None, "refOf": lambda w_, u_: None,
           "execute": lambda w_, r_: (jobs.append(r_), True)[1], "pos": pos, "setPos": lambda *a: None, "teleport": lambda *a: None,
           "dead": lambda acc, r: False, "uuid": lambda acc, r: (ent(r) or {}).get("uuid"), "roleOf": lambda acc, r: (ent(r) or {}).get("role"),
           "tags": lambda acc, r: JString(""), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None, "clearDebug": lambda acc, r: None,
           "mark": lambda acc, r, o: None, "remove": remove, "hearts": lambda *a: None, "anim": lambda *a: None, "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: float(vs.get(str(mid), 1.0)), "fx": lambda *a: None, "passthrough": lambda acc, r, m: JString("all")}
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)
    Cfg.SPAWN_DELAY = 0
    Cfg.SLOT2_MODE = "always"
    W["names"][str(uo)] = "Rider"
    key = str(Store.pkey(uo))
    Store.KEYOF.put(uo, key)
    r = Store.get(key)
    r.set("starter", "1")
    pid = str(Ops.create(r, None, "DragonPlain", 3, 5, 0, "test", "harness", False))

    def second():
        Views.second(uo, oref, st, None, w, "default")
        n = 0
        while jobs:
            jobs.pop(0).run()
            n += 1
        return n
    # in the PET slot: buffs only, no creature
    r.set("active.1", pid)
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))
    second()
    K.check(not [c for c in calls if c[0] == "spawn"] and Views.want(uo, r, key, 1, "default", False) is None, "VW a dragon in the PET slot: nothing appears (Skyy: only in the summon slot)")
    # the summon slot
    r.set("active.1", "")
    r.set("active.2", pid)
    wt = str(Views.want(uo, r, key, 2, "default", False))
    K.eq(wt, "%s|2|%s|Nestkeeper_Dragon_Plain_2|-1.0|0" % (key, pid), "VW want: the Smalling model (Lv 5), x1 of its own size, walking")
    second()
    sp = [c for c in calls if c[0] in ("spawn", "pinned", "model")]
    K.check(sp == [("pinned", "Nestkeeper_Dragon_Plain_2", 0.55, pid), ("spawn", "Skyy_Pet_Dragon", "Nestkeeper_Dragon_Plain_2@0.55#" + pid)],
            "VW spawnNow: OUR dragon role, the PINNED look (seed = the pet id), x its vanilla size 0.55: %s" % sp)
    v = Views.view(uo, 2)
    K.check(v is not None and str(v.kind) == "DragonPlain" and str(v.role) == "Skyy_Pet_Dragon", "VW tracked as the summon")
    # a level-up into the next stage = a new look
    calls[:] = []
    r.set("pet.%s.level" % pid, "10")
    second()
    second()
    sp = [c for c in calls if c[0] in ("spawn", "pinned", "remove")]
    K.check(sp[:1] == [("remove", "Skyy_Pet_Dragon")] and ("pinned", "Nestkeeper_Dragon_Plain_4", 1.55, pid) in sp and ("spawn", "Skyy_Pet_Dragon", "Nestkeeper_Dragon_Plain_4@1.55#" + pid) in sp,
            "VW Lv 10: the Smalling goes, the Flyling (x1.55) comes: %s" % sp)
    # the game removes it (the void): DOWN + one line, nothing spawns until the cooldown ends
    v = Views.view(uo, 2)
    calls[:] = []
    told[:] = []
    ent(v.ref)["removed"] = True
    Views.onRemoved(v.ref, RR.REMOVE, st)
    left = int(Dg.downLeft(pid))
    K.check(int(Dg.DOWNS.get()) == 1 and 50000 < left <= int(Dg.downMs(10)) and Views.view(uo, 2) is None, "VW removed by the game at Lv 10 = DOWN for %d ms (%d)" % (left, int(Dg.downMs(10))))
    second()
    second()
    K.check(not [c for c in calls if c[0] == "spawn"] and Views.want(uo, r, key, 2, "default", False) is None, "VW while DOWN: nothing appears")
    K.check(told == ["[Pets] Your dragon flew back to its summon slot - it comes back in 56 s."], "VW one chat line on the owner's tick: %s" % told)
    K.check("Down - back in" in str(P_("PetsPage").tip(r, pid, 0)), "VW the card says DOWN")
    Dg.DOWN.put(pid, JClass("java.lang.Long").valueOf(1))
    second()
    K.check([c for c in calls if c[0] == "spawn"] == [("spawn", "Skyy_Pet_Dragon", "Nestkeeper_Dragon_Plain_4@1.55#" + pid)] and int(Dg.downLeft(pid)) == 0,
            "VW after the cooldown: back in the summon slot")
    K.eq([int(Dg.downMs(lv)) for lv in (1, 50, 100, 200)], [60000, round((60 - 45 * 49 / 99.0) * 1000), 15000, 15000], "VW the cooldown: 60 s at Lv 1 -> 15 s at Lv 100")
    Cfg.DRAGON_DOWN_MAX, Cfg.DRAGON_DOWN_MIN = 0, 30
    K.check(int(Dg.downMs(1)) == 0, "VW down rows 0 = at once (min clamped to max)")
    v = Views.view(uo, 2)
    ent(v.ref)["removed"] = True
    Views.onRemoved(v.ref, RR.REMOVE, st)
    K.check(int(Dg.downLeft(pid)) == 0 and Views.want(uo, r, key, 2, "default", False) is not None, "VW ... a removal then never blocks")
    Cfg.reloadAll()
    Cfg.SPAWN_DELAY, Cfg.SLOT2_MODE = 0, "always"
    second()
    v = Views.view(uo, 2)
    n0 = int(Dg.DOWNS.get())
    Views.onRemoved(v.ref, RR.UNLOAD, st)
    K.check(int(Dg.DOWNS.get()) == n0 and int(Dg.downLeft(pid)) == 0, "VW a chunk UNLOAD is not DOWN")
    # ---- FX fixer C2 / B4: DOWN only while the owner is online, alive and in the dragon's world; B5: a logout forgets the line, DOWN prunes
    st2 = U.allocateInstance(Store_.class_)
    oref2 = Ref(st2, 999)

    def removed_with(owner_ref, dead):
        PW.API = JProxy(PKG + "PetWorldApi", dict=api)
        second()
        v_ = Views.view(uo, 2)
        if v_ is None:
            return None
        n_ = int(Dg.DOWNS.get())
        a2 = dict(api)
        a2["ownerRef"] = owner_ref
        a2["dead"] = lambda acc, r_: dead
        PW.API = JProxy(PKG + "PetWorldApi", dict=a2)
        ent(v_.ref)["removed"] = True
        Views.onRemoved(v_.ref, RR.REMOVE, st)
        PW.API = JProxy(PKG + "PetWorldApi", dict=api)
        return (int(Dg.DOWNS.get()) - n_, int(Dg.downLeft(pid)) > 0, Views.view(uo, 2) is None)
    K.eq(removed_with(lambda u_: None, False), (0, False, True), "FX the owner logged out when the game removed it: not DOWN, the view dropped")
    K.eq(removed_with(lambda u_: oref2, False), (0, False, True), "FX the owner in another world: not DOWN")
    K.eq(removed_with(lambda u_: oref if str(u_) == str(uo) else None, True), (0, False, True), "FX the owner dead: not DOWN")
    told[:] = []
    for i in range(70):
        Dg.DOWN.put("old%d" % i, JClass("java.lang.Long").valueOf(1))
    K.eq(removed_with(lambda u_: oref if str(u_) == str(uo) else None, False), (1, True, True), "FX the owner there (/entity remove while looking at it): DOWN")
    K.check(int(Dg.DOWN.size()) == 1 and Dg.TELL.containsKey(uo), "FX DOWN prunes the ran-out cooldowns (70 -> %d); the line waits for the owner's tick" % int(Dg.DOWN.size()))
    Views.leave(uo, "logout")
    K.check(not Dg.TELL.containsKey(uo), "FX a logout forgets the unsent line (never stale at the next join)")
    Dg.DOWN.clear()
    # a vanilla dragon: the plain fox path unchanged, the Fire dragon young
    calls[:] = []
    uf2 = UUID.fromString("00000000-0000-0000-0000-000000009502")
    k2 = str(Store.pkey(uf2))
    r2 = Store.get(k2)
    fd = str(Ops.create(r2, None, "DragonFire", 3, 1, 0, "test", "harness", False))
    r2.set("active.2", fd)
    K.eq(str(Views.want(uf2, r2, k2, 2, "default", False)), "%s|2|%s|Dragon_Fire|-0.3|0" % (k2, fd), "VW a Lv 1 Fire dragon: x0.3 of the vanilla boss")
    r2.set("pet.%s.rebirth" % fd, "1")
    K.eq(str(Views.want(uf2, r2, k2, 2, "default", False)).split("|")[3:5], ["Dragon_Fire", "-1.3"], "VW a pet rebirth keeps it grown (0.3.0 rule): x1.3")
    # ---- the pin maths on real Java maps
    HM = JClass("java.util.HashMap")
    sets = HM()
    for sn, ks in (("Base", ["0", "1", "2", "3", "4", "5", "6"]), ("1_Head_Horns", ["1", "2", "3", "4", "5", "6", "7", "8"]), ("Dragon_Saddle", ["Saddle"]), ("4_Teeth", ["0", "1", "2", "3", "4"])):
        m = HM()
        for k_ in ks:
            m.put(k_, JObject(None))
        sets.put(sn, m)
    a = dict((str(k_), str(v_)) for k_, v_ in PW.pinMap(sets, "abc123").entrySet())
    b = dict((str(k_), str(v_)) for k_, v_ in PW.pinMap(sets, "abc123").entrySet())
    others = set(tuple(sorted(dict((str(k_), str(v_)) for k_, v_ in PW.pinMap(sets, "pet%d" % i).entrySet()).items())) for i in range(40))
    K.check(a == b and sorted(a) == ["1_Head_Horns", "4_Teeth", "Base"] and a["Base"] in [str(i) for i in range(7)] and len(others) > 20,
            "VW the pinned look: every set but the saddle, the same pick every time, other pets differ (%d looks of 40): %s" % (len(others), a))
    K.check(PW.pinPick(None, "x") is None and PW.pinPick(JClass("java.util.HashSet")(), "x") is None and len(dict(PW.pinMap(None, "x"))) == 0, "VW pin maths: empty / null")
    PW.API = None
    K.check(PW.modelPinned("Nestkeeper_Dragon_Plain_4", 1.0, "x") is None and PW.modelPinned(None, 1.0, None) is None, "VW the REAL modelPinned never throws without assets (null)")
    cen = str(Dg.census())
    K.check(cen.startswith("dragon role Skyy_Pet_Dragon = -1, dragon models 0 / 11 - MISSING Nestkeeper_Dragon_Plain_1") and "is Dragon Nestkeeper installed?" in cen,
            "VW the census line (no assets here): %s" % cen[:160])
    K.save()


# ======================================================================================================== ST: the hub stage (real pages)
def run_st(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JShort, JByte
    import hub_tab_kit as HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Egg, Page, Reel, Hy, Eng = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetEgg"), P_("PetsPage"),
                                                      P_("PetReel"), P_("PetHatchery"), P_("PetsEng"))
    Paths, UUID, IS = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "st-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    P_("PetsHubOpen").register()
    Hy.OPENER = P_("PetHatchOpen")()
    # fixer B2 on the stage's asset stores (no Dragon Nestkeeper here): the REAL ModelAsset map has no Nestkeeper stage model = not loaded;
    # the stage's Item map is a stand-in that answers every id (the missing-item path: DG FX with the seam)
    Dg = P_("PetDragon")
    K.check(not Dg.lookOk(0) and not Dg.lookOk(1) and Dg.lookOk(4) and Dg.itemOk("Skyy_PetEgg_Dragon_Air") and Dg.eggKind("Dragon_Egg_Tundra") is None
            and "needs the Dragon Nestkeeper mod" in str(Dg.placeWhy(None, "Dragon_Egg_Plain")),
            "ST the REAL ModelAsset map: Aures' stage models missing = their dragons do not hatch here (the Nestkeeper reason), ours do")
    Dg.ASSET_API = JProxy("java.util.function.Predicate", dict={"test": lambda x: True})          # from here: as with Dragon Nestkeeper installed
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000009611"), "Keeper")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "123")
    told = []
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, [str(u1)]), "byName": lambda n: u1, "nameOf": lambda u: "Keeper",
                                            "tell": lambda u, t, c: told.append(str(t))})

    def click(page, a, i=None, extra=None, tok=True):
        Hy.CLICK.clear()
        d = '{"a":"%s"' % a + (',"i":"%s"' % i if i is not None else "") + (',"t":"%s"' % page.tok if tok else "") + (extra or "") + "}"
        page.handleDataEvent(P1.ref, P1.st, d)
        E.pump(P1)
        return str(page.info)
    hb = P1.slots["hotbar"].getInventory()
    hb.addItemStackToSlot(JShort(2), IS("Dragon_Egg_Plain", 1))
    hb.addItemStackToSlot(JShort(3), IS("Skyy_PetEgg_Dragon_Air", 1))
    pg = Page(P1.pr)
    pg.tab = 2
    P1.pm.openCustomPage(P1.ref, P1.st, pg)
    E.pump(P1)
    built = HT.build(pg, P1)
    T42.menu_page(K, built, "ST the Hatchery tab with two dragon eggs")

    def desc(g):
        return str(HT.jf(g.getClass(), "description").get(g))
    cells = [desc(Hy.eggCell(u1, r1, P_("PetInvReal").of(P1.st, P1.ref), i, 0)) for i in ("Dragon_Egg_Plain", "Skyy_PetEgg_Dragon_Air")]
    K.check("Hatches in 1h 00m" in cells[0] and "Hatches: your Plain Dragon (Earth) - one dragon per profile. Using it in your hand hatches a wild dragon instead." in cells[0]
            and "Rarity: Rare 60%" in cells[0] and "Click: put it in a free Hatchery slot" in cells[0] and "Hatches: your Sky Dragon (Air)" in cells[1],
            "ST the dragon egg cells: %s" % cells[0].replace(chr(10), " | "))
    K.check("cannot be fused" in desc(Hy.eggCell(u1, r1, P_("PetInvReal").of(P1.st, P1.ref), "Dragon_Egg_Plain", 1)), "ST the Fuse eggs mode: dragon eggs greyed out")
    K.eq([str(x) for x in pg.eids], ["Dragon_Egg_Plain", "Skyy_PetEgg_Dragon_Air"], "ST the grid holds the two dragon eggs")
    g0 = click(pg, "eg", extra=',"SlotIndex":0')
    K.check(g0.startswith("+Plain Dragon Egg is in Hatchery slot 1 - it hatches in 1h 00m") and r1.get("hatchery.1") is not None, "ST a grid click places Aures' egg: %s" % g0)
    Egg.NOFORCE.clear()
    built = HT.build(pg, P1)
    s2 = dict((s_, d) for ty, s_, t, d in built[0] if ty == "Set")
    T42.menu_page(K, built, "ST the Hatchery with a dragon egg in slot 1")
    K.check("One dragon per profile" in desc(Hy.eggCell(u1, r1, P_("PetInvReal").of(P1.st, P1.ref), "Skyy_PetEgg_Dragon_Air", 0)), "ST the second dragon egg's cell says why")
    K.check("dragon eggs take 1h 00m" in str(s2.get("#SkyyPtH1Sb.Text")) and "Plain Dragon Egg" in str(s2.get("#SkyyPtH1Nm.Text")), "ST slot 1 row: %s / %s" % (s2.get("#SkyyPtH1Nm.Text"), s2.get("#SkyyPtH1Sb.Text")))
    ix = [str(x) for x in pg.eids].index("Skyy_PetEgg_Dragon_Air")
    g1 = click(pg, "eg", extra=',"SlotIndex":%d' % ix)
    K.check(g1.startswith("-One dragon per profile") and r1.get("hatchery.2") is None, "ST the second dragon egg refused: %s" % g1)
    Hy.CLOCK_OFF = 3601 * 1000
    HT.build(pg, P1)
    n0 = int(r1.count())
    pg.confirm = ""
    click(pg, "slot", 1, extra=',"m":"h"')
    cur = E.pg(P1)
    K.check(int(r1.count()) == n0 + 1 and cur is not None and str(cur.getClass().getName()) == PKG + "PetHatchPage" and int(cur.view) == 2,
            "ST Hatch: the dragon saved, the reel page opens straight on the RESULT (no reels for a fixed dragon): view %s" % (cur.view if cur is not None else None))
    Hy.CLOCK_OFF = 0
    cm, ev = HT.build(cur, P1)
    T42.menu_page(K, (cm, ev), "ST the hatch result page of a dragon")
    s3 = dict((s_, d) for ty, s_, t, d in cm if ty == "Set")
    K.check("Plain Dragon" in str(s3.get("#SkyyHtResN.Text")) and "Plain Dragon Egg" in str(s3.get("#SkyyHtName.Text"))
            and "Your dragon - one dragon per profile." in str(s3.get("#SkyyHtSub.Text")) and len([t for t in told if "You hatched a" in t]) == 1,
            "ST the result view: %s / %s / %s; one reveal line" % (s3.get("#SkyyHtName.Text"), s3.get("#SkyyHtSub.Text"), s3.get("#SkyyHtResN.Text")))
    cur.handleDataEvent(P1.ref, P1.st, '{"a":"pets"}')
    E.pump(P1)
    back = E.pg(P1)
    built = HT.build(back, P1)
    T42.menu_page(K, built, "ST the Pets tab after the hatch")
    did = [i for i in r1.ids() if str(r1.kindOf(i)) == "DragonPlain"][0]
    cell = Page.cell(r1, did, 0)
    K.check("Dragon: Weakling" in desc(cell) and "Plain Dragon" in str(HT.jf(cell.getClass(), "name").get(cell)), "ST the dragon's cell: %s" % str(HT.jf(cell.getClass(), "name").get(cell)))
    K.check(str(Page.iconOf(r1, did)) == "Skyy_PetIcon_DragonPlain", "ST its icon item = the portrait (our recolour - fixer B1)")
    K.save()


# ======================================================================================================== LIVE: start twice on a copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, MgP5, Log = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsMigP5"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = T41.tree(home)

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        r = str(MgP5.run(Paths.get(home)))
        Cfg.load(Paths.get(mods))
        v = str(Cfg.loadV3(Paths.get(home)))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return r, v, [int(x) for x in Store.scanAll()]
    r1, v1, sc1 = start()
    t1 = T41.tree(home)
    K.check(r1 == "" or "Balance P5 power (SkyyPets 0.4.8)" in r1, "LIVE start 1: only 0.4.8's own P5 update may run (%s)" % ("ran" if r1 else "already done"))
    K.check(sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k) and not k.startswith(("config-history", "migrations", "config.properties", "config-changes"))) == []
            or r1 != "", "LIVE 0.4.11 writes nothing of its own")
    K.check(sc1[2] == 0 and sc1[3] == 0, "LIVE every pet file reads (%s)" % sc1)
    txt = open(os.path.join(home, "config.properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(home, "config.properties")) else ""
    K.check(all(P_("PetsCfg").kind(k) is not None for k in KINDS), "LIVE the five dragons are known with the live config file (%s kind.Dragon lines)" % ("no" if "kind.Dragon" not in txt else "some"))
    if "pets.dragon.element" not in txt:
        K.eq([str(Cfg.elemOf(k)) for k in KINDS], ["Earth", "Water", "Fire", "Thunder", "Air"], "LIVE dragon elements from pets.dragon.element (the live pets.element names no dragon)")
    if "pets.dragon.eggs" not in txt:
        K.check(str(P_("PetDragon").eggKind("Dragon_Egg_Plain")) == "DragonPlain" and int(Cfg.DRAGON_HATCH_S) == 3600, "LIVE the dragon rows at their defaults")
    r2, v2, sc2 = start()
    K.check(r2 == "" and T41.tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("dg", run_dg), ("vw", run_vw), ("st", run_st), ("el410", T410.run_el), ("live", run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
