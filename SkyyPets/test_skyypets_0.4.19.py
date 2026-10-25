"""Harness for SkyyPets 0.4.19 (THE SECRET DRAGONS, round D5b-1: research/cloud/Secret-Dragons-Spec.md; tools/pets_0_4_19_patch.py).
Build first:
    python tools/pets_0_4_19_patch.py && python SkyyPets/build_skyypets_0.4.19.py
    python SkyyPets/test_skyypets_0.4.19.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes, 0.4.18's patch still regenerates 0.4.18 byte for byte; 2 classes added (PetSecret,
                 PetSecretFn), no system / command; line endings kept; the jar: the new entries = exactly the 4 secret kinds' files (portrait
                 item + picture, 24 PetFrames, egg item + icon + held texture, child model + texture) + the 2 classes; no entry removed;
                 changed non-class entries = manifest.json + server.lang; the child models' Parent / texture size; Blood / Light / Crystal
                 pictures = recolours of the art/dragons pictures (never the Frost icon), the Void ones byte for byte
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.18 -> 0.4.19, engine-access audit
  SD    EXECUTED the door + the delivery: pets:fn:giveSecretEgg / secretRoll (PetSecretFn) codes OK / GIVEN / HAS_DRAGON / HAS_EGG / OFF /
                 BAD_WORD / BAD_PLAYER / MISS, the chance row (check= hook, fixed rolls), the owed lines SAVED before OK, the per-second
                 delivery (PetHatchery.tick path) into a counted inventory: the message, the eggcredit, dsecret given; full inventory = waits
                 (told once) then arrives; CRASH cases: a stop after the count was saved (egg in / egg not in the player file), a stop after
                 the delivery save (the eggcredit regives only when the player file lacks it); /petadmin secret; the hatch row fallback
                 (an older pets.dragon.eggs text); the Hatchery egg list shows a secret egg only while held; the tooltip ABILITIES lines;
                 placing + hatching a Strange Void Egg -> a Void Dragon (one dragon per profile after)
  PK    EXECUTED on a stand-in world (PetWorld.API / PetFight.API seams, real Damage objects, real PetViews): Void Strike in the bite,
                 Blood Drinker heals 4 % of the bite (capped at the max), Radiance every 10 s only while hurt, Crystal Skin queued from the
                 damage hook and dealt on the dragon's second (never kills, never for a player's hit)
  rc/hx/w15/...   0.4.18's phases EXECUTED on this jar (the counts 44 -> 48 kinds, 264 -> 288 frames swapped in)
  live  start twice on a scratch COPY of the live Skyy_SkyyPets folder (no saved-data change at start)
NOT COVERED (UNVERIFIED in game): the four child models' look in game (recolour quality, Fire / Frost bodies), the seat heights, the heal +
reflect feel in real fights, EntityStatMap.addStatValue on the owner from the dragon's tick (the same call SkyyAccessories' regen uses).
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util, subprocess, hashlib, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "drag5", "pets")]
import skyybuild as B
import harness_kit as HK
import skyyui as SUI
import skyyeggs as EGG

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s418 = importlib.util.spec_from_file_location("test_skyypets_0_4_18", os.path.join(HERE, "test_skyypets_0.4.18.py"))
T418 = importlib.util.module_from_spec(_s418)
_s418.loader.exec_module(T418)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T417, T416, T415, T414, T413, T412, T411, T410, T44, T41 = (T418.T417, T418.T416, T418.T415, T418.T414, T418.T413, T418.T412, T418.T411,
                                                             T418.T410, T418.T44, T418.T41)
T42 = T411.T42

VERSION = "0.4.19"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.18.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.18.py")
PATCH = os.path.join(TOOLS, "pets_0_4_19_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T418, T417, T416, T415, T414, T413, T412, T411, T410, T44):
    _m.PKG = PKG
for _m in (T418, T417, T416, T415, T414, T413, T412, T411):
    _m.JAR = JAR
for _m in (T414, T415, T416, T417):
    _m.GEN = GEN
SECRET = ["DragonVoid", "DragonBlood", "DragonLight", "DragonCrystal"]
WORDS = ["void", "blood", "light", "crystal"]
EGGS = [e[0] for e in EGG.SECRET_EGGS]
NAMES = [e[2] for e in EGG.SECRET_EGGS]
GRAD = {"Void": "Dragon_Fire", "Blood": "Dragon_Fire", "Light": "Dragon_Frost", "Crystal": "Dragon_Frost"}
RARS = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
EXPECT = {   # checked 2026-10-25 against the class compare 0.4.18 -> 0.4.19 (every member is a change of tools/pets_0_4_19_patch.py)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetAdminArg1Cmd': ['~c '],
    'PetAdminArg2Cmd': ['~c '],
    'PetAdminArg3Cmd': ['~c '],
    'PetAdminArg4Cmd': ['~c '],
    'PetAdminArg5Cmd': ['~c '],
    'PetDragon': ['+f FIRST_SECRET', '~<clinit>', '~m rowKind'],
    'PetEgg': ['~m admin'],
    'PetEggDefs': ['~<clinit>'],
    'PetFight': ['+f REFL_MS', '+m healOwner', '+m light', '+m ownerHere', '+m reflect', '+m reflectNow', '+m ridden', '+m steal', '~<clinit>', '~m amount', '~m bite', '~m clear', '~m inspect', '~m second', '~m shareOf'],
    'PetHatchery': ['~m tick', '~m tickRec'],
    'PetKind': ['~<clinit>'],
    'PetOps': ['~m admin'],
    'PetRec': ['+f ow', '+f owMods', '+f owSet', '+m owes'],
    'PetRide': ['~<clinit>', '~m seatRow'],
    'PetViews': ['~m upkeep'],
    'PetsCfg': ['+f DRAGON_ANCHOR_DRAGONBLOOD', '+f DRAGON_ANCHOR_DRAGONCRYSTAL', '+f DRAGON_ANCHOR_DRAGONLIGHT', '+f DRAGON_ANCHOR_DRAGONVOID', '+f DRAGON_BLOOD_STEAL', '+f DRAGON_CRYSTAL_REFLECT', '+f DRAGON_LIGHT_EVERY', '+f DRAGON_LIGHT_HEAL', '+f DRAGON_SECRET', '+f DRAGON_SECRET_RATES', '+f DRAGON_VOID_STRIKE', '~<clinit>', '~m applyAll', '~m applyScalars', '~m seed'],
    'PetsMigP5': ['~m mgLog', '~m run'],
    'PetsMigS2': ['~m run'],
    'PetsMigW15': ['~m run'],
    'PetsPage': ['~m tip'],
    'SkyyPetsPlugin': ['~m setup', '~m shutdown'],
}
ADDED = ["PetSecret", "PetSecretFn"]
if "--expect-dump" in sys.argv:
    EXPECT = {}


def _new_entries():
    """the jar entries 0.4.19 adds (besides the 2 classes)"""
    out = []
    for k, w in zip(SECRET, ("Void", "Blood", "Light", "Crystal")):
        out += ["Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_%s.json" % k, "Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k]
        out += ["Server/Item/Items/SkyyPets/PetFrames/Skyy_PetIcon_%s_%s.json" % (k, r) for r in RARS]
        e = "Skyy_PetEgg_Dragon_" + w
        out += ["Server/Item/Items/SkyyPets/Dragons/%s.json" % e, "Common/Icons/ItemsGenerated/%s.png" % e, "Common/Items/Pets/%s_Texture.png" % e]
        out += ["Server/Models/SkyyPets/Skyy_Dragon_%s.json" % w, "Common/NPC/SkyyPets/Skyy_Dragon_%s/Texture.png" % w]
    return sorted(out)


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + server.lang + the new kinds' files (S checks each one)"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == sorted(["manifest.json", "Server/Languages/en-US/server.lang"] + _new_entries()),
                          "C: non-class entries changed = manifest.json + server.lang + the %d new secret-dragon files: %s" % (len(_new_entries()), sorted(set(got) - set(_new_entries()))))
    return _eq00(self, got, want, what)


HK.Child.eq = _eq


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    import skyyart as SA
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.19 - build script') and g.count('VERSION = "0.4.19"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls(") + 2,
            "S 2 classes added (PetSecret, PetSecretFn), no system or command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_18_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    zn, on = set(z.namelist()), set(oz.namelist())
    new = sorted(n for n in zn - on if not n.endswith("/") and not n.endswith(".class"))
    K.eq(new, _new_entries(), "S the new entries = the 4 secret kinds' files (%d)" % len(_new_entries()))
    K.eq(sorted(n for n in zn - on if n.endswith(".class")), ["com/skyy/pets/PetSecret.class", "com/skyy/pets/PetSecretFn.class"], "S the 2 new classes")
    K.eq(sorted(on - zn), [], "S no entry removed")
    ch = sorted(n for n in zn & on if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(ch, ["Server/Languages/en-US/server.lang", "manifest.json"], "S the changed non-class entries = manifest.json + server.lang")
    # the child models: our Parent, the parent's texture size, the spec gradient (six steps)
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))          # read only
    for w, par in GRAD.items():
        mj = json.loads(z.read("Server/Models/SkyyPets/Skyy_Dragon_%s.json" % w).decode("utf-8"))
        pt = json.loads(az.read("Server/Models/Elemental/%s.json" % par).decode("utf-8-sig"))["Texture"]
        tex = z.read("Common/NPC/SkyyPets/Skyy_Dragon_%s/Texture.png" % w)
        K.check(mj.get("Parent") == par and mj.get("Texture") == "NPC/SkyyPets/Skyy_Dragon_%s/Texture.png" % w and SA.png_size(tex) == SA.png_size(az.read("Common/" + pt))
                and (mj.get("Particles") == [] if par == "Dragon_Fire" else "Particles" not in mj), "S Skyy_Dragon_%s: Parent %s, its texture size, %s" % (w, par, mj))
    # the pictures: Void = art/dragons byte for byte; Blood / Light / Crystal = 64 px recolours of OUR art (never the Frost icon's pixels)
    man = json.load(open(os.path.join(ROOT, "art", "dragons", "manifest.json"), encoding="utf8"))
    sha = dict((f["path"], f.get("sha256")) for f in man["files"])
    for p in ("Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonVoid.png", "Common/Icons/ItemsGenerated/Skyy_PetEgg_Dragon_Void.png"):
        K.check(hashlib.sha256(z.read(p)).hexdigest() == sha[p], "S %s = art/dragons byte for byte" % p)
    pics = [z.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k) for k in SECRET] + [z.read("Common/Icons/ItemsGenerated/%s.png" % e) for e in EGGS]
    K.check(len(set(hashlib.sha256(b).hexdigest() for b in pics)) == 8 and all(SA.png_size(b) == (64, 64) for b in pics), "S 8 different 64 px pictures")
    fro = SA.png_decode(oz.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_DragonFire.png"))
    for k, base in (("DragonBlood", "DragonFire"), ("DragonLight", "DragonSky"), ("DragonCrystal", "DragonTundra")):
        a, b = SA.png_decode(z.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k)), SA.png_decode(z.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % base))
        same_alpha = all(a.get(x, y)[3] == b.get(x, y)[3] for y in range(64) for x in range(64))
        K.check(same_alpha, "S %s = a recolour of the %s art (same shape, alpha kept)" % (k, base))
    # the egg items: Legendary, our egg model, the plain secret names, the flavor tag from tier_tags (no 'Dragon')
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for e, nm in zip(EGGS, NAMES):
        ij = json.loads(z.read("Server/Item/Items/SkyyPets/Dragons/%s.json" % e).decode("utf-8"))
        ds = re.search(r"(?m)^server\.items\.%s\.description=(.*)$" % re.escape(e), lang)
        K.check(ij["Quality"] == "Legendary" and ij["Model"] == EGG.EGG_MODEL and ("server.items.%s.name=%s" % (e, nm)) in lang and ds and ds.group(1).startswith("Legendary Egg - ")
                and "ragon" not in ds.group(1) and "ragon" not in nm, "S %s: Legendary, '%s', flavor '%s'" % (e, nm, ds and ds.group(1)[:60]))
    K.check(all(("server.items.Skyy_PetIcon_%s.name=%s Dragon" % (k, k[6:])) in lang for k in SECRET), "S the 4 portrait names (X Dragon)")
    K.save()


# ======================================================================================================== SD: the door + the delivery, EXECUTED
def run_sd(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "sd")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JArray, JObject, JString
    P_ = lambda n: JClass(PKG + n)
    Sec, Dg, Cfg, Store, Hy, Egg, Ops, Page, Defs, Fn = (P_("PetSecret"), P_("PetDragon"), P_("PetsCfg"), P_("PetStore"), P_("PetHatchery"), P_("PetEgg"),
                                                         P_("PetOps"), P_("PetsPage"), P_("PetEggDefs"), P_("PetSecretFn"))
    Log = P_("PetsLog")
    told = []
    UUID = W["UUID"]
    u1 = UUID.fromString("00000000-0000-0000-0000-000000009901")
    u2 = UUID.fromString("00000000-0000-0000-0000-000000009902")
    W["names"].update({str(u1): "Seeker", str(u2): "Owner"})
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])),
                                                      "byName": lambda n: {"Seeker": u1, "Owner": u2}.get(str(n)),
                                                      "nameOf": lambda u: W["names"].get(str(u), str(u)), "tell": lambda u, t, c: told.append((str(u), str(t)))})
    OA = lambda *a: JArray(JObject)([JString(x) if isinstance(x, str) else x for x in a])
    give = Fn(0)
    roll = Fn(1)
    # ---- the tables
    K.eq([str(x) for x in Dg.KINDS][5:], SECRET, "SD PetDragon.KINDS: the 4 secret dragons after the 5")
    K.eq([str(x) for x in Dg.EGG_IDS][5:], EGGS, "SD PetDragon.EGG_IDS: the 4 secret eggs, same order")
    K.check(int(Dg.FIRST_SECRET) == 5 and [str(x) for x in Sec.WORDS] == WORDS and [str(x) for x in Sec.NAMES] == NAMES, "SD the words + names")
    K.check(int(len(Cfg.KINDS)) == 48 and all(Cfg.kind(k) is not None and str(Cfg.kind(k).skill) == "Combat" and int(Cfg.kind(k).rarity) == 3 for k in SECRET),
            "SD 48 kinds; each secret dragon a Combat kind starting Rare")
    K.check(all(Cfg.elemOf(k) is None for k in SECRET) and str(Cfg.elemOf("DragonFire")) == "Fire", "SD no element for the secret dragons (Fire keeps Fire)")
    K.check(all(bool(Cfg.summonable(k)) for k in SECRET), "SD each is summonable (fighter + mount)")
    K.eq([str(Dg.model(k, 50)) for k in SECRET], ["Skyy_Dragon_Void", "Skyy_Dragon_Blood", "Skyy_Dragon_Light", "Skyy_Dragon_Crystal"], "SD the models")
    K.eq([str(Dg.eggKind(e)) for e in EGGS], SECRET, "SD each secret egg hatches its dragon (the default row)")
    # an older saved pets.dragon.eggs text (0.4.18's default) still hatches them; "-" = none; a remap wins
    old = "Dragon_Egg_Plain=DragonPlain, Dragon_Egg_Tundra=DragonTundra, Skyy_PetEgg_Dragon_Fire=DragonFire, Skyy_PetEgg_Dragon_Thunder=DragonStorm, Skyy_PetEgg_Dragon_Air=DragonSky"
    Cfg.DRAGON_EGGS = old
    K.check([str(Dg.rowKind(e)) for e in EGGS] == SECRET and str(Dg.rowKind("Skyy_PetEgg_Dragon_Fire")) == "DragonFire", "SD the older row text: the secret eggs hatch their own dragon")
    Cfg.DRAGON_EGGS = old + ", Skyy_PetEgg_Dragon_Void=DragonFire"
    K.check(str(Dg.rowKind(EGGS[0])) == "DragonFire", "SD a remap in the row wins")
    Cfg.DRAGON_EGGS = "-"
    K.check(all(Dg.rowKind(e) is None for e in EGGS), "SD '-' = no dragon egg hatches")
    Cfg.DRAGON_EGGS = "Skyy_PetEgg_Dragon_Air=DragonSky"
    K.check(Dg.rowKind("Skyy_PetEgg_Dragon_Fire") is None and str(Dg.rowKind(EGGS[2])) == "DragonLight", "SD an elemental egg not listed = off (0.4.11 rule kept); a secret one = its own")
    Cfg.reloadAll()
    # ---- the chance row
    K.check(Sec.checkRates("k", "void=30, blood=20") is None and Sec.checkRates("k", "") is None and "not a secret" in str(Sec.checkRates("k", "fire=3"))
            and "0 - 10000" in str(Sec.checkRates("k", "void=20000")) and "twice" in str(Sec.checkRates("k", "void=1, VOID=2")) and "needs" in str(Sec.checkRates("k", "void")),
            "SD checkRates (the Server Setup check= hook)")
    K.eq([int(Sec.rate(w)) for w in WORDS + ["nope"]], [30, 20, 10000, 10000, 0], "SD rates: void 30, blood 20, light / crystal always, a bad word 0")
    Cfg.DRAGON_SECRET_RATES = "void=oops"
    K.eq(int(Sec.rate("void")), 30, "SD a broken row = the built-in rates")
    Cfg.reloadAll()
    # ---- the door: refusals first
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "1")
    K.eq(str(give.apply(OA(u1, "fire", "t"))), "BAD_WORD", "SD a word that is no secret egg: BAD_WORD")
    K.eq(str(give.apply(OA(None, "void", "t"))), "BAD_PLAYER", "SD no player: BAD_PLAYER")
    K.eq(str(give.apply(JString("nope"))), "BAD_PLAYER", "SD not an Object[]: BAD_PLAYER (never throws)")
    Cfg.DRAGON_SECRET = False
    K.eq(str(give.apply(OA(u1, "void", "t"))), "OFF", "SD pets.dragon.secret off: OFF")
    Cfg.DRAGON_SECRET = True
    Cfg.KINDS_OFF = "DragonVoid"
    off = str(give.apply(OA(u1, "void", "t")))
    Cfg.reloadAll()
    K.eq(off, "OFF", "SD the Void Dragon switched off (pets.kinds.off): OFF")
    K.check(r1.get("dsecretw.void") is None and r1.get("dsecret.void") is None, "SD nothing written for a refusal")
    # ---- the roll
    Sec.ROLL_FIX = 30
    K.eq(str(roll.apply(OA(u1, "void", "mobs:void"))), "MISS", "SD secretRoll void: a roll of 30 >= 30 per 10,000 = MISS")
    K.check(r1.get("dsecretw.void") is None and int(Sec.MISSES.get()) == 1, "SD a miss writes nothing")
    Sec.ROLL_FIX = 29
    K.eq(str(roll.apply(OA(u1, "void", "mobs:void"))), "OK", "SD secretRoll void: a roll of 29 = OK")
    Sec.ROLL_FIX = -1
    wl = str(r1.get("dsecretw.void"))
    K.check(wl.startswith(EGGS[0] + "|mobs:void|") and wl.endswith("|-1") and str(r1.get("dsecret.void")).startswith("owed|"), "SD OK = the owed line + the marker: %s" % wl)
    disk = open(os.path.join(W["home"], "pets", "%s.properties" % k1), encoding="latin-1").read() if os.path.isfile(os.path.join(W["home"], "pets", "%s.properties" % k1)) else ""
    if not disk:
        for _r, _d, _f in os.walk(os.path.join(W["home"])):
            for f_ in _f:
                if k1 in f_ and f_.endswith(".properties"):
                    disk = open(os.path.join(_r, f_), encoding="latin-1").read()
    K.check("dsecretw.void=" in disk and "dsecret.void=" in disk, "SD ... SAVED to the pet file before the answer")
    K.eq(str(give.apply(OA(u1, "void", "again"))), "GIVEN", "SD the same word again: GIVEN (one per profile per word)")
    K.eq(str(give.apply(OA(u1, "light", "guardians"))), "HAS_EGG", "SD another word while one is on its way: HAS_EGG")
    # ---- the delivery (the per-second tick path: PetHatchery.tickRec) into a counted inventory
    inv = T41.Inv({"Rock_Stone": 5})
    pinv = T41.proxy_inv(inv)
    told[:] = []
    now = int(W["now"]())
    Hy.tickRec(u1, r1, pinv, now)
    K.check(inv.count(EGGS[0]) == 1 and r1.get("dsecretw.void") is None and str(r1.get("dsecret.void")).startswith("given|"), "SD delivered: 1 Strange Void Egg, the owed line gone, the marker = given")
    cr = [str(k) for k in r1.keysWith("eggcredit.")]
    K.check(len(cr) == 1 and str(r1.get(cr[0])).startswith(EGGS[0] + "|0|") and str(r1.get(cr[0])).endswith("|1"), "SD ... as an eggcredit (count before 0, after 1): %s" % [str(r1.get(c)) for c in cr])
    hid = cr[0][10:]
    K.check(Egg.SESSION.containsKey(hid) and str(Egg.FORCE.get(hid)) == k1, "SD ... the forced player save is asked for")
    K.check(any(t == "[Pets] You found a Strange Void Egg." for _u, t in told) and not any("mobs" in t or "ragon" in t for _u, t in told), "SD the message: the item's name only: %s" % told)
    K.check(any("secret dragon egg %s given to %s (source mobs:void)" % (EGGS[0], k1) in str(l) for l in Log.LINES), "SD the server log names the source")
    Hy.tickRec(u1, r1, pinv, now + 1000)
    K.eq(inv.count(EGGS[0]), 1, "SD the next second: nothing more")
    # ---- FIX (critic 1.1 / 3.2) + fix 2: a second word is asked while the first egg is still unhatched in the bag -> it WAITS (never two dragon eggs)
    K.check(not bool(r1.owes()), "FIX owes(): nothing owed after the delivery")
    K.eq(str(give.apply(OA(u1, "light", "guardians"))), "OK", "FIX another word, the Void egg in the bag: OK at the door (the bag is only seen on the world thread)")
    K.check(bool(r1.owes()), "FIX owes(): the owed line is seen after the change")
    told[:] = []
    d0 = int(Sec.DROPS.get())
    h0 = int(Sec.HOLDS.get())
    Hy.tickRec(u1, r1, pinv, now + 2000)
    Hy.tickRec(u1, r1, pinv, now + 3000)
    K.check(inv.count(EGGS[2]) == 0 and str(r1.get("dsecretw.light")).endswith("|-1") and str(r1.get("dsecret.light")).startswith("owed|") and int(Sec.DROPS.get()) == d0
            and int(Sec.HOLDS.get()) == h0 + 2 and not any("found" in t or "room" in t for _u, t in told) and bool(r1.owes()),
            "FIX2 ... at delivery: it WAITS (no second dragon egg, the owed line kept, no message): %s" % told)
    K.eq(len([l for l in Log.LINES if ("waits: a dragon egg is in the inventory: %s" % EGGS[0]) in str(l)]), 1, "FIX2 ... the server log says why, once")
    K.eq(str(give.apply(OA(u1, "blood", "mobs:night"))), "HAS_EGG", "FIX2 ... meanwhile another word: HAS_EGG (one on its way)")
    inv.live.pop(EGGS[0], None)          # the Void egg sold / traded away
    Hy.tickRec(u1, r1, pinv, now + 4000)
    K.check(inv.count(EGGS[2]) == 1 and r1.get("dsecretw.light") is None and str(r1.get("dsecret.light")).startswith("given|")
            and any(t == "[Pets] You found a Radiant Egg." for _u, t in told), "FIX2 ... the Void egg gone: the Radiant Egg arrives: %s" % told)
    inv.live.pop(EGGS[2], None)
    for c_ in [str(x) for x in r1.keysWith("eggcredit.")]:
        r1.set(c_, None)
    # ---- FIX 2 (second critic): a player UUID with no record + no pet file + not online = BAD_PLAYER, no ghost file
    ug = UUID.fromString("00000000-0000-0000-0000-00000000ab01")
    kg = str(Store.pkey(ug))
    K.eq(str(give.apply(OA(ug, "void", "mobs:void"))), "BAD_PLAYER", "FIX2 an offline UUID that never had pets: BAD_PLAYER")
    K.check(not Store.REC.containsKey(kg) and not Store.file(kg).toFile().isFile(), "FIX2 ... no ghost record / pet file (%s)" % kg)
    # ---- FIX (critic 2.3): a profile key that names no profile = BAD_PLAYER, no pet file written
    K.eq(str(give.apply(OA("nosuchprofile42", "void", "t"))), "BAD_PLAYER", "FIX an unknown profile key: BAD_PLAYER")
    K.check(not Store.REC.containsKey("nosuchprofile42") and not Store.file("nosuchprofile42").toFile().isFile(), "FIX ... no ghost record / pet file")
    # ---- a full inventory: waits, told once, then arrives
    k2 = str(Store.pkey(u2))
    Store.KEYOF.put(u2, k2)
    r2 = Store.get(k2)
    r2.set("starter", "1")
    K.eq(str(give.apply(OA(k2, "crystal", "collections:crystal"))), "OK", "SD by profile key (an offline profile): OK")
    full = T41.Inv({"Rock_Stone": 10}, cap=10)
    pf = T41.proxy_inv(full)
    told[:] = []
    for s_ in range(3):
        Hy.tickRec(u2, r2, pf, now + s_ * 1000)
    w2 = str(r2.get("dsecretw.crystal"))
    K.check(full.count(EGGS[3]) == 0 and w2.endswith("|0") and int(Sec.WAITS.get()) == 3 and len([t for _u, t in told if "Make room" in t]) == 1,
            "SD a full inventory: it waits (the count before saved: %s), 'make room' told ONCE" % w2)
    # FIX 2 (critic LOW 1): a Crystal Egg traded in while ours waits for room is never taken for ours; the saved count follows the bag
    full.live[EGGS[3]] = 1
    g0 = int(Sec.GIVEN.get())
    Hy.tickRec(u2, r2, pf, now + 3500)
    w3 = str(r2.get("dsecretw.crystal"))
    K.check(w3.endswith("|1") and str(r2.get("dsecret.crystal")).startswith("owed|") and int(Sec.GIVEN.get()) == g0 and full.count(EGGS[3]) == 1,
            "FIX2 a traded-in Crystal Egg while ours waits: NOT marked given, the count follows (%s), ours waits (a dragon egg in the bag)" % w3)
    full.live.pop(EGGS[3], None)
    Hy.tickRec(u2, r2, pf, now + 4000)
    K.check(str(r2.get("dsecretw.crystal")).endswith("|0") and full.count(EGGS[3]) == 0, "FIX2 ... it left again: the count follows back (%s), still full" % r2.get("dsecretw.crystal"))
    full.cap = 11
    Hy.tickRec(u2, r2, pf, now + 5000)
    K.check(full.count(EGGS[3]) == 1 and r2.get("dsecretw.crystal") is None and str(r2.get("dsecret.crystal")).startswith("given|"), "SD room again: the Crystal Egg arrives")
    # ---- CRASH A: a stop after the count before was saved, the egg NOT in the player file -> given now (exactly one)
    r2.set("dsecret.crystal", None)
    for c in r2.keysWith("eggcredit."):
        r2.set(c, None)
    full.live.pop(EGGS[3], None)
    full.cap = None
    r2.set("dsecretw.crystal", "%s|collections:crystal|%d|0" % (EGGS[3], now))
    Hy.tickRec(u2, r2, pf, now + 6000)
    K.check(full.count(EGGS[3]) == 1 and r2.get("dsecretw.crystal") is None, "SD crash A (count saved, egg never given): given once now")
    # ---- CRASH B: the same line, but the egg DID reach the player file before the stop -> nothing more, marked given
    r2.set("dsecretw.crystal", "%s|collections:crystal|%d|0" % (EGGS[3], now))
    g0 = int(Sec.GIVEN.get())
    Sec.STARTED.clear()          # a server restart (statics fresh)
    Hy.tickRec(u2, r2, pf, now + 7000)
    K.check(full.count(EGGS[3]) == 1 and r2.get("dsecretw.crystal") is None and str(r2.get("dsecret.crystal")).startswith("given|") and int(Sec.GIVEN.get()) == g0 + 1,
            "SD crash B (the egg already in the inventory: 1 > 0): no second egg, marked given")
    # ---- CRASH C: a stop after the delivery save, before the player file saved -> the eggcredit regives once after the restart
    r3k = "secret-c"
    u3 = UUID.fromString("00000000-0000-0000-0000-000000009903")
    W["names"][str(u3)] = "Crash"
    Store.KEYOF.put(u3, r3k)
    W["keys"][str(u3)] = r3k
    r3 = Store.get(r3k)
    r3.set("starter", "1")
    K.eq(str(give.apply(OA(u3, "blood", "mobs:night"))), "OK", "SD crash C: owed")
    i3 = T41.Inv({})
    p3 = T41.proxy_inv(i3)
    Hy.tickRec(u3, r3, p3, now)
    K.eq(i3.count(EGGS[1]), 1, "SD crash C: delivered (live)")
    i3.restart()          # the server stops: the player file never held it
    Egg.SESSION.clear()
    Egg.DONE.clear()
    Hy.credits(u3, r3, p3, now + 1000)
    K.eq(i3.count(EGGS[1]), 1, "SD crash C: after the restart the eggcredit gives it again - ONE egg")
    i3.psave()
    i3.restart()
    Egg.SESSION.clear()
    Hy.credits(u3, r3, p3, now + 2000)
    K.check(i3.count(EGGS[1]) == 1 and len(r3.keysWith("eggcredit.")) == 0, "SD crash C: the player file holds it -> the credit clears, still ONE egg")
    # ---- HAS_DRAGON / HAS_EGG (a dragon egg in the Hatchery)
    pid = str(Ops.create(r2, None, "DragonFire", 3, 10, 0, "test", "harness", False))
    K.eq(str(give.apply(OA(u2, "light", "guardians"))), "HAS_DRAGON", "SD owns a dragon: HAS_DRAGON")
    k4 = "secret-d"
    r4 = Store.get(k4)
    r4.set("hatchery.1", "Skyy_PetEgg_Dragon_Air|%d|h4|inv" % now)
    K.eq(str(give.apply(OA(k4, "light", "guardians"))), "HAS_EGG", "SD a dragon egg in the Hatchery: HAS_EGG")
    r4.set("hatchery.1", None)
    Cfg.KINDS_OFF = ""
    K.eq(str(give.apply(OA(k4, "light", "guardians"))), "OK", "SD ... taken out: OK")
    # ---- FIX (critic 3.2): a dragon hatched while the egg was owed -> dropped at delivery, nothing given
    u4 = UUID.fromString("00000000-0000-0000-0000-000000009904")
    Ops.create(r4, None, "DragonPlain", 3, 10, 0, "test", "harness", False)
    i4 = T41.Inv({})
    p4 = T41.proxy_inv(i4)
    Hy.tickRec(u4, r4, p4, now)
    K.check(i4.count(EGGS[2]) == 0 and r4.get("dsecretw.light") is None and r4.get("dsecret.light") is None, "FIX a dragon hatched meanwhile: the owed Radiant Egg is dropped, not given")
    # ---- FIX (critic 1.2): an unreadable owed line clears its owed marker too
    r4.set("dsecretw.blood", "junk")
    r4.set("dsecret.blood", "owed|1|t")
    Hy.tickRec(u4, r4, p4, now + 1000)
    K.check(r4.get("dsecretw.blood") is None and r4.get("dsecret.blood") is None and i4.count(EGGS[1]) == 0, "FIX an unreadable owed line: both lines cleared (the word may be given again)")
    r4.set("dsecretw.crystal", "junk")
    r4.set("dsecret.crystal", "given|1|t")
    Hy.tickRec(u4, r4, p4, now + 2000)
    K.check(r4.get("dsecretw.crystal") is None and str(r4.get("dsecret.crystal")) == "given|1|t", "FIX ... a 'given' marker stays")
    # ---- /petadmin secret (the same door)
    k5 = str(Store.pkey(u1))
    a1 = str(Egg.admin("Admin", "secret", "Seeker", "void", None, None))
    Sec.ROLL_FIX = 9999
    a5 = str(Egg.admin("Admin", "secretroll", "Seeker", "blood", None, None))
    Sec.ROLL_FIX = -1
    K.check(a5.startswith("-Not given (MISS)") and "blood = 20 per 10,000" in a5 and r1.get("dsecretw.blood") is None, "FIX2 /petadmin secretroll: the chance first (%s)" % a5)
    a2 = str(Egg.admin("Admin", "secret", "Seeker", "blood", None, None))
    K.check("waits while they hold or hatch another dragon egg" in a2 and "dropped if they already own a dragon" in a2, "FIX2 /petadmin secret: OK = owed, says when it waits / drops")
    a3 = str(Egg.admin("Admin", "secret", "Nobody", "blood", None, None))
    a4 = str(Egg.admin("Admin", "secret", "Seeker", "fire", None, None))
    K.check(a1.startswith("-Not given (GIVEN)") and a2.startswith("+Crimson Egg (Skyy_PetEgg_Dragon_Blood) owed to Seeker") and "not online" in a3 and "(BAD_WORD)" in a4,
            "SD /petadmin secret: %s | %s | %s | %s" % (a1[:50], a2[:60], a3, a4[:40]))
    K.check("admin:Admin" in str(r1.get("dsecretw.blood")), "SD ... the source = admin:<name>")
    # ---- the Hatchery egg list + the dragon egg rules for a secret egg
    K.check(Dg.placeWhy(r1, EGGS[1]) is None, "SD placeWhy: a Crimson Egg may go in an empty Hatchery")
    K.check(str(Dg.placeWhy(r2, EGGS[3])).startswith("-One dragon per profile"), "SD placeWhy: not while owning a dragon (R8)")
    K.check(int(Defs.eggRar(EGGS[0])) == 5 and bool(Defs.isDragon(EGGS[0])) and str(Defs.nameOf(EGGS[0])) == NAMES[0], "SD PetEggDefs: Legendary colour, a dragon egg, its plain name")
    K.check("Void Dragon" in str(Dg.eggText(EGGS[0])) and "(" not in str(Dg.eggText(EGGS[0])).split("Void Dragon")[1][:3], "SD the egg text once owned: your Void Dragon (no element): %s" % Dg.eggText(EGGS[0]))
    # ---- the tooltip: ABILITIES
    for k, nm, val in (("DragonBlood", "Blood Drinker", "4 %"), ("DragonVoid", "Void Strike", "+5 %"), ("DragonLight", "Radiance", "3 %"), ("DragonCrystal", "Crystal Skin", "6 %")):
        rr = Store.get("tip-" + k)
        tp = str(Ops.create(rr, None, k, 3, 12, 0, "test", "harness", False))
        tip = str(Page.tip(rr, tp, 0))
        ab = tip.split("ABILITIES</color>")[1] if "ABILITIES</color>" in tip else ""
        col = str(Sec.colOf(k))
        K.check(('<color is="%s">%s</color>' % (col, nm)) in ab and ('<color is="#7ee08a">%s</color>' % val) in ab and "None yet" not in ab and "summon slot" in ab
                and "FIGHTING (SUMMON SLOT)" in tip and "Bites for" in tip, "SD the %s tooltip: ABILITIES %s %s (its colour, the value green)" % (k, nm, val))
    rr = Store.get("tip-fire")
    tf = str(Ops.create(rr, None, "DragonFire", 3, 12, 0, "test", "harness", False))
    K.check("None yet" in str(Page.tip(rr, tf, 0)).split("ABILITIES")[1], "SD a Fire Dragon: ABILITIES None yet (unchanged)")
    K.check(abs(float(P_("PetFight").share("DragonVoid", 100, 3, 0)) - 0.25) < 1e-9 and abs(float(P_("PetFight").share("DragonLight", 100, 3, 0)) - 0.225) < 1e-9,
            "SD the bite shares at Lv 100 Rare: Void 25 %, Light 22.5 % (tools/balance_model.py)")
    K.check(str(Sec.text()).startswith("secret dragons on (pets:fn:giveSecretEgg"), "SD the ready-line part: %s" % Sec.text())
    sev = [str(l) for l in Log.LINES if "SEVERE" in str(l)]
    K.check(not sev, "SD no SEVERE: %s" % sev[:3])
    K.save()


# ======================================================================================================== HT: hatching a secret egg, EXECUTED
def run_ht(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "ht")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    P_ = lambda n: JClass(PKG + n)
    Dg, Cfg, Hy, Store = P_("PetDragon"), P_("PetsCfg"), P_("PetHatchery"), P_("PetStore")
    UUID = W["UUID"]
    u = UUID.fromString("00000000-0000-0000-0000-000000009911")
    W["names"][str(u)] = "Hatcher"
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: u,
                                                      "nameOf": lambda u_: "Hatcher", "tell": lambda u_, t, c: None})
    key = str(Store.pkey(u))
    Store.KEYOF.put(u, key)
    r = Store.get(key)
    r.set("starter", "1")
    empty = T41.proxy_inv(T41.Inv({"Skyy_PetEgg_Mining_Rare": 1}))
    K.check(not [x for x in [str(y) for y in Hy.eggsHeld(u, empty)] if x in EGGS], "HT the Hatchery egg list: no secret egg while you hold none (no hint)")
    inv = T41.Inv({EGGS[0]: 1, EGGS[2]: 1})
    pinv = T41.proxy_inv(inv)
    held = [str(x) for x in Hy.eggsHeld(u, pinv)]
    K.check(EGGS[0] in held and EGGS[2] in held, "HT ... it lists the secret eggs you hold: %s" % held)
    Cfg.DRAGON_HATCH_S = 0
    res = Hy.place(u, pinv, EGGS[0], "test")
    K.check(str(res[0]).startswith("+Strange Void Egg is in Hatchery slot 1") and inv.count(EGGS[0]) == 0, "HT place: %s" % res[0])
    Hy.CLICK.clear()
    res2 = Hy.place(u, pinv, EGGS[2], "test")
    K.check(str(res2[0]).startswith("-One dragon per profile") and inv.count(EGGS[2]) == 1, "HT a second secret egg while one is in the Hatchery: refused, the egg stays: %s" % res2[0])
    Hy.CLOCK_OFF = 10 * 3600 * 1000
    h = Hy.hatch(u, 1, None, "test")
    K.check(str(h[0]).startswith("+You hatched a ") and str(h[0]).endswith(" Void Dragon!") and str(h[3]) == "DragonVoid" and int(h[4]) >= 3, "HT hatch: %s" % h[0])
    pid = str(h[2])
    K.check(str(r.kindOf(pid)) == "DragonVoid" and int(r.levelOf(pid)) == 1 and str(Dg.ownedId(r, None)) == pid, "HT the Void Dragon is in the pets list (one dragon per profile)")
    Hy.CLICK.clear()
    res3 = Hy.place(u, pinv, EGGS[2], "test")
    K.check(str(res3[0]).startswith("-One dragon per profile - you already have your Void Dragon") and inv.count(EGGS[2]) == 1, "HT after the hatch: a Radiant Egg refused (R8): %s" % res3[0])
    K.check(not [str(l) for l in P_("PetsLog").LINES if "SEVERE" in str(l)], "HT no SEVERE")
    K.save()


# ======================================================================================================== PK: the perks, EXECUTED on a stand-in world
def run_pk(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "pk")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JFloat, JObject
    P_ = lambda n: JClass(PKG + n)
    Dg, Cfg, Views, PW, Store, Ops, Fg, Sec = (P_("PetDragon"), P_("PetsCfg"), P_("PetViews"), P_("PetWorld"), P_("PetStore"), P_("PetOps"), P_("PetFight"),
                                               P_("PetSecret"))
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                      "nameOf": lambda u: "Rider", "tell": lambda u, t, c: None})
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.server.core.universe.world.World")
    Dmg, ES = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage"), JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    UUID = W["UUID"]
    st = U.allocateInstance(Store_.class_)
    w = U.allocateInstance(World.class_)
    ents, jobs, calls = {}, [], []
    nxt = [100]

    def new_ref(uuid, role, pos, hp=(100.0, 0.0, 100.0), player=None, inv=False):
        nxt[0] += 1
        r = Ref(st, nxt[0])
        ents[int(r.getIndex())] = {"uuid": uuid, "role": role, "pos": list(pos), "removed": False, "ref": r, "hp": list(hp), "player": player, "inv": inv, "dead": False}
        return r
    ent = lambda r: None if r is None else ents.get(int(r.getIndex()))
    uo = UUID.fromString("00000000-0000-0000-0000-000000009921")
    oref = new_ref(uo, None, [10.0, 70.0, 10.0], player=uo)
    roles = {"Skyy_Pet_Walk": 11, "Skyy_Pet_Fly": 12, "Skyy_Pet_Dragon": 13, "Test_Pet": 7, "Test_Fly": 8}

    def spawn(s, role, x, y, z, yaw, model):
        rn = [k for k, v in roles.items() if v == int(role)][0]
        r = new_ref(UUID.randomUUID(), rn, [float(x), float(y), float(z)])
        ent(r)["model"] = str(model)
        return r

    def pos(acc, r):
        e = ent(r)
        return None if e is None or e["removed"] else JArray(JDouble)(e["pos"])

    def remove(acc, r):
        e = ent(r)
        if e is None or e["removed"]:
            return False
        e["removed"] = True
        return True
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": lambda m, s: JString("%s" % m), "modelPinned": lambda m, s, seed: JString("%s#%s" % (m, seed)),
           "spawn": spawn, "store": lambda w_: st, "ownerRef": lambda u_: oref if str(u_) == str(uo) else None, "refOf": lambda w_, u_: None,
           "execute": lambda w_, r_: (jobs.append(r_), True)[1], "pos": pos, "setPos": lambda *a: None,
           "teleport": lambda acc, r, x, y, z, yaw: ent(r)["pos"].__setitem__(slice(0, 3), [float(x), float(y), float(z)]),
           "dead": lambda acc, r: bool((ent(r) or {}).get("dead")), "uuid": lambda acc, r: (ent(r) or {}).get("uuid"), "roleOf": lambda acc, r: (ent(r) or {}).get("role"),
           "tags": lambda acc, r: JString(""), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None, "clearDebug": lambda acc, r: None,
           "mark": lambda acc, r, o: None, "remove": remove, "hearts": lambda *a: None, "anim": lambda acc, r, a: None, "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: 1.0, "fx": lambda acc, i, x, y, z: calls.append(("fx", str(i))), "passthrough": lambda acc, r, m: JString("all")}
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)
    hits = []

    def hit(cb, t, src, cause, amt):
        hits.append((ent(t)["role"], ent(src)["role"], None if cause is None else str(cause), round(float(amt), 4)))
        return True

    def health(acc, r):
        e = ent(r)
        return None if e is None or e["hp"] is None else JArray(JFloat)(e["hp"])
    Fg.API = JProxy(PKG + "PetFightApi", dict={"hit": hit, "health": health, "playerOf": lambda acc, r: (ent(r) or {}).get("player"),
                                                "guarded": lambda acc, r: bool((ent(r) or {}).get("inv"))})
    heals = []

    def heal(r, amt):
        e = ent(r)
        a = float(amt)
        heals.append(round(a, 4))
        e["hp"][0] = min(e["hp"][2], e["hp"][0] + a)
        return JClass("java.lang.Double").valueOf(a)
    Sec.HEAL_API = JProxy("java.util.function.BiFunction", dict={"apply": heal})

    def reload():
        Cfg.reloadAll()
        Cfg.SPAWN_DELAY = 0
        Cfg.SLOT2_MODE = "always"
    reload()
    W["names"][str(uo)] = "Rider"
    key = str(Store.pkey(uo))
    Store.KEYOF.put(uo, key)
    r = Store.get(key)
    r.set("starter", "1")
    clock = [0]

    def second(plus=1000):
        clock[0] += plus
        Fg.NOW_OFF = clock[0]
        Views.second(uo, oref, st, None, w, "default")
        while jobs:
            jobs.pop(0).run()
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))
    KD = 1000.0 / float(Fg.REF_GAP_MS)
    now = lambda: int(Fg.now())

    def summon(kind, lv=50):
        for pid_ in [str(x) for x in r.ids()]:
            r.set("pet.%s.kind" % pid_, None)
        Views.clearAll() if hasattr(Views, "clearAll") else None
        pid = str(Ops.create(r, None, kind, 3, lv, 0, "test", "harness", False))
        r.set("active.2", pid)
        second(0)
        second(0)
        v = Views.view(uo, 2)
        return pid, v
    # ---- the math helpers
    K.check(abs(float(Sec.strikeMul("DragonVoid")) - 1.05) < 1e-12 and float(Sec.strikeMul("DragonFire")) == 1.0 and float(Sec.strikeMul(None)) == 1.0, "PK strikeMul: Void x1.05 only")
    F3 = lambda a: JArray(JFloat)(a)
    K.check(abs(float(Sec.stealAmt("DragonBlood", 100.0, F3([50.0, 0.0, 100.0]))) - 4.0) < 1e-9 and abs(float(Sec.stealAmt("DragonBlood", 100.0, F3([98.5, 0.0, 100.0]))) - 1.5) < 1e-6
            and float(Sec.stealAmt("DragonBlood", 100.0, F3([100.0, 0.0, 100.0]))) == 0.0 and float(Sec.stealAmt("DragonVoid", 100.0, F3([50.0, 0.0, 100.0]))) == 0.0
            and float(Sec.stealAmt("DragonBlood", 100.0, None)) == 0.0 and float(Sec.stealAmt("DragonBlood", 100.0, F3([0.0, 0.0, 100.0]))) == 0.0,
            "PK stealAmt: 4 % of the bite, never above the max, nothing when full / dead / unknown / not Blood")
    K.check(abs(float(Sec.lightAmt("DragonLight", F3([50.0, 0.0, 200.0]))) - 6.0) < 1e-9 and abs(float(Sec.lightAmt("DragonLight", F3([198.0, 0.0, 200.0]))) - 2.0) < 1e-6
            and float(Sec.lightAmt("DragonLight", F3([200.0, 0.0, 200.0]))) == 0.0, "PK lightAmt: 3 % of the max, capped at the max, 0 at full health")
    K.check(abs(float(Sec.noKill(6.0, F3([50.0, 0.0, 80.0]))) - 6.0) < 1e-9 and abs(float(Sec.noKill(6.0, F3([3.0, 0.0, 80.0]))) - 2.0) < 1e-6
            and float(Sec.noKill(6.0, F3([1.0, 0.0, 80.0]))) == 0.0 and float(Sec.noKill(6.0, None)) == 0.0, "PK noKill: never below 1 health")
    Cfg.DRAGON_VOID_STRIKE = 250.0
    K.check(float(Sec.pct(0)) == 100.0, "PK a perk row above 100 % = 100")
    Cfg.DRAGON_VOID_STRIKE = float("nan")
    K.check(float(Sec.pct(0)) == 0.0, "PK a broken perk row = 0")
    reload()
    # ---- Void Strike in the real bite
    pid, v = summon("DragonVoid")
    K.check(v is not None and str(v.kind) == "DragonVoid" and str(v.model) == "Skyy_Dragon_Void", "PK a summoned Lv 50 Void Dragon (model %s)" % (v and v.model))
    dref = v.ref
    ent(dref)["pos"] = [12.0, 70.0, 10.0]
    mob = new_ref(UUID.randomUUID(), "Trork_Warrior", [13.0, 70.0, 10.0], hp=(500.0, 0.0, 500.0))
    Fg.OWNHIT.clear()
    Fg.ema(uo, 100.0, now())
    a = float(Fg.amount(v, r, mob, None, now()))
    K.check(abs(a - 100.0 * KD * 0.25 * 0.5 * 1.5 * 1.05) < 1e-6, "PK the Void bite: your 100 / 0.45 s x 25 %% x Lv 50 x 1.5 s x 1.05 (strike) = %.3f" % a)
    Fg.inspect(None, mob, Dmg(ES(oref), 0, 100.0))
    hits[:] = []
    second()
    K.check(len(hits) == 1 and hits[0][:3] == ("Trork_Warrior", "Skyy_Pet_Dragon", None) and ("fx", "Impact_Critical") in calls, "PK it bites (no element: the default cause + effect): %s" % hits)
    # ---- Blood Drinker
    pid, v = summon("DragonBlood")
    ent(v.ref)["pos"] = [12.0, 70.0, 10.0]
    ent(oref)["hp"] = [40.0, 0.0, 100.0]
    Fg.OWNHIT.clear()
    Fg.ema(uo, 100.0, now())
    Fg.inspect(None, mob, Dmg(ES(oref), 0, 100.0))
    hits[:] = []
    heals[:] = []
    second()
    second(1500)
    K.check(len(hits) >= 1 and len(heals) == len(hits) and all(abs(h - 0.04 * b[3]) < 1e-3 for h, b in zip(heals, hits)) and int(Sec.STEALS.get()) >= 1,
            "PK Blood Drinker: each bite heals you 4 %% of it: bites %s heals %s" % ([b[3] for b in hits], heals))
    ent(oref)["hp"] = [100.0, 0.0, 100.0]
    heals[:] = []
    second(1500)
    K.check(not heals, "PK ... nothing at full health")
    # ---- Radiance
    pid, v = summon("DragonLight")
    Fg.drop(v, "test")
    ent(oref)["hp"] = [50.0, 0.0, 200.0]
    heals[:] = []
    second()
    K.check(heals == [6.0], "PK Radiance: hurt -> 3 %% of your max 200 = 6: %s" % heals)
    for _i in range(9):
        second()
    K.check(heals == [6.0], "PK ... not again within 10 s: %s" % heals)
    second()
    K.check(heals == [6.0, 6.0], "PK ... again after 10 s: %s" % heals)
    ent(oref)["hp"] = [200.0, 0.0, 200.0]
    for _i in range(11):
        second()
    K.check(heals == [6.0, 6.0], "PK ... nothing at full health")
    ent(oref)["hp"] = [190.0, 0.0, 200.0]
    second()
    K.check(heals == [6.0, 6.0, 6.0], "PK ... the clock waited: hurt again = at once (6 <= 10 missing)")
    Cfg.DRAGON_FIGHT = False
    ent(oref)["hp"] = [100.0, 0.0, 200.0]
    for _i in range(11):
        second()
    K.check(len(heals) == 4, "PK ... also with dragon fighting off")
    reload()
    # FIX 2 (critic MEDIUM 1): Radiance also while ridden (upkeep returns before PetFight.second)
    vr = Views.view(uo, 2)
    vr.landing = True
    ent(oref)["hp"] = [100.0, 0.0, 200.0]
    for _i in range(11):
        second()
    K.check(len(heals) == 5 and bool(Views.view(uo, 2).landing), "FIX2 Radiance while ridden / landing: healed (%s)" % heals)
    Views.view(uo, 2).landing = False
    # ---- Crystal Skin
    pid, v = summon("DragonCrystal")
    ent(v.ref)["pos"] = [12.0, 70.0, 10.0]
    Fg.drop(v, "test")
    mob2 = new_ref(UUID.randomUUID(), "Trork_Brute", [11.0, 70.0, 10.0], hp=(80.0, 0.0, 80.0))
    hits[:] = []
    Fg.inspect(None, oref, Dmg(ES(mob2), 0, 50.0))
    q = Sec.REFL.get(v.uuid)
    K.check(q is not None and abs(float(q[1]) - 3.0) < 1e-9 and not hits, "PK Crystal Skin: a Trork hits you for 50 -> 3 queued, nothing dealt inside the damage hook")
    Fg.inspect(None, oref, Dmg(ES(mob2), 0, 50.0))
    K.check(abs(float(Sec.REFL.get(v.uuid)[1]) - 6.0) < 1e-9, "PK ... two hits in one second add up (6)")
    second()
    rf = [h for h in hits if h[0] == "Trork_Brute"]
    K.check(len(rf) >= 1 and rf[0][1] == "Skyy_Pet_Dragon" and rf[0][2] is None and abs(rf[0][3] - 6.0) < 1e-6 and Sec.REFL.get(v.uuid) is None and int(Sec.REFLECTS.get()) == 1,
            "PK ... dealt on the dragon's second, from the dragon: %s" % rf)
    ent(mob2)["hp"] = [2.0, 0.0, 80.0]
    hits[:] = []
    Fg.inspect(None, oref, Dmg(ES(mob2), 0, 50.0))
    second()
    rf = [h for h in hits if h[0] == "Trork_Brute" and h[2] is None]
    K.check(len(rf) == 1 and abs(rf[0][3] - 1.0) < 1e-6, "PK ... never kills (2 health -> 1 dealt): %s" % rf)
    # ---- FIX (critic 2.1): a queued hit older than 3 s (the owner rode in between) is dropped
    ent(mob2)["hp"] = [80.0, 0.0, 80.0]
    hits[:] = []
    Fg.inspect(None, oref, Dmg(ES(mob2), 0, 50.0))
    q = Sec.REFL.get(v.uuid)
    K.check(q is not None and len(q) == 3 and int(q[2]) == now(), "FIX the queued reflect carries its time")
    second(plus=4000)
    rf = [h for h in hits if h[0] == "Trork_Brute" and h[2] is None]
    K.check(not rf and Sec.REFL.get(v.uuid) is None, "FIX ... 4 s later: dropped, nothing dealt: %s" % rf)
    Fg.inspect(None, oref, Dmg(ES(mob2), 0, 50.0))
    second(plus=2900)
    rf = [h for h in hits if h[0] == "Trork_Brute" and h[2] is None]
    K.check(len(rf) == 1 and abs(rf[0][3] - 3.0) < 1e-6, "FIX ... within 3 s: dealt (3): %s" % rf)
    pl = new_ref(UUID.randomUUID(), None, [11.0, 70.0, 10.0], player=UUID.randomUUID())
    Fg.inspect(None, oref, Dmg(ES(pl), 0, 50.0))
    K.check(Sec.REFL.get(v.uuid) is None, "PK ... never for a player's hit")
    pid, v = summon("DragonFire")
    Fg.inspect(None, oref, Dmg(ES(mob2), 0, 50.0))
    K.check(Sec.REFL.isEmpty(), "PK ... nothing with another dragon")
    K.check(not [str(l) for l in P_("PetsLog").LINES if "SEVERE" in str(l)], "PK no SEVERE")
    K.save()


# ======================================================================================================== 0.4.18 phases with the new counts
def run_rc(out, jar, scratch, home):
    f = T414._swap(T418.run_rc, T418, [("len(kinds) == 44", "len(kinds) == 48")])
    f(out, jar, scratch, home)


def run_w15(out, jar, scratch, home):
    f = T414._swap(T417.run_w15, T417, [(r'"SkyyPets 0.4.17\t-\tupdate\ttree.Combat.b3.r3a." in l', r'"SkyyPets 0.4.19\t-\tupdate\ttree.Combat.b3.r3a." in l')])
    f(out, jar, scratch, home)


def run_dg(out, jar, scratch, home):
    """0.4.14's swap of 0.4.11's dragon phase + the 9 kinds / the void word (now a secret egg)"""
    f = T414._swap(T411.run_dg, T411, [("Page.tip(r, pid, 0)", "Dg.card(r, pid)"),
                                       ('''and "Fighting, riding and flying come in a later version." in tip and "Element: Earth</color>" in tip''',
                                        '''and "Ride it from Lv 10 (F on it in the summon slot)." in tip and "Fights next to you in the summon slot: bites for 0.1 %" in tip and '<color is="#5dbb4a">Earth</color>' in str(Page.tip(r, pid, 0))'''),
                                       ('K.eq([str(x) for x in Dg.KINDS], KINDS, "DG the five dragon kinds")', 'K.eq([str(x) for x in Dg.KINDS], KINDS + %r, "DG the five dragon kinds + the 4 secret ones (0.4.19)")' % SECRET),
                                       ('''"Skyy_PetEgg_Dragon_Air", "Skyy_PetEgg_Dragon_Fire", "Dragon_Egg_Plain", None, None], "DG /petadmin egg dragon <word>")''',
                                        '''"Skyy_PetEgg_Dragon_Air", "Skyy_PetEgg_Dragon_Fire", "Dragon_Egg_Plain", "Skyy_PetEgg_Dragon_Void", None], "DG /petadmin egg dragon <word> (0.4.19: void = the Strange Void Egg)")'''),
                                       ('''a2 = str(Egg.admin("harness", "egg", "Drake", "Dragon", "void", None))''', '''a2 = str(Egg.admin("harness", "egg", "Drake", "Dragon", "nope", None))''')],
                   allow_many=("Page.tip(r, pid, 0)",))
    f(out, jar, scratch, home)


def run_vw(out, jar, scratch, home):
    f = T414._swap(T411.run_vw, T411, [("dragon models 0 / 11 - MISSING", "dragon models 0 / 15 - MISSING")])
    f(out, jar, scratch, home)


def run_pt(out, jar, scratch, home):
    """0.4.16's portrait phase: 48 kinds; the 0.4.15 jar it read (the old Dog stand-in) is archived - that history line is skipped"""
    f = T414._swap(T416.run_pt, T416, [("len(kinds) == 44, \"PT 44 pet kinds", "len(kinds) == 48, \"PT 48 pet kinds"),
                                       ('''    oz = zipfile.ZipFile(OLD_JAR)
    o_dog = json.loads(oz.read("Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_Dog.json").decode("utf-8"))["Icon"]
''', '''    o_dog = "Icons/ItemsGenerated/Skyy_PetIcon_Dog_not_checked" if False else "Icons/Items/archived"
''')])
    f(out, jar, scratch, home)


def run_mig(out, jar, scratch, home):
    f = T414._swap(T415.run_mig, T415, [(r"SkyyPets 0.4.15\t-\tupdate", r"SkyyPets 0.4.19\t-\tupdate")])
    f(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("sd", run_sd), ("ht", run_ht), ("pk", run_pk), ("rc", run_rc), ("hx", T417.run_hx), ("w15", run_w15), ("rl", T416.run_rl),
                   ("pt", run_pt), ("sl", T415.run_sl), ("mig", run_mig), ("dr", T415.run_dr), ("t", T415.run_t), ("r", T414.run_r), ("m", T412.run_m),
                   ("f", T414.run_f), ("dg", run_dg), ("vw", run_vw), ("st", T414.run_st), ("el410", T414.run_el), ("live", T417.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
