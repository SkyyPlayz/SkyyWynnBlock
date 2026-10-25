"""Harness for SkyyGear 0.3.47 (round ut28: the first 28 Zone 1-5 Untiered items - 55 SkyyGear copies of vanilla models, 64 ut / utfx / utpow rows,
the one-time pure addition migrateUt28, 6 new trick words, the held weapon's damage taken, the alloy tag in the header - tools/gear_0_3_47_patch.py
header; the table tools/ut28.py).
Build first:
    python tools/gear_0_3_47_patch.py && python SkyyGear/build_skyygear_0.3.47.py
    python SkyyGear/test_skyygear_0.3.47.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.46 jar is the compare base):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the jar adds exactly the 55 copies + their
              110 recoloured textures / icons; the only other non-class changes are the manifest + server.lang (+ 110 lines, nothing else); each
              copy = its vanilla base's JSON + our keys (no recipe, Untiered quality, the band start, the vanilla model by path); no vanilla path
              shadowed; tools/ut28.py + tools/test_tier_tags.py pass
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.46 -> 0.3.47 (EXPECT below)
  X  exec     (bare JVM) the trick words (TK, parseRow, checkRow accepts all 64 rows and refuses typos), tgtMult / bossMult / bossRank / takenPct,
              trickText / trickBad, hitMult unchanged, the fresh file (64 x ut / utfx / utpow + the 3 rows + marker) read by GearCfg.apply (bands,
              rows, utpow), the 3 rows live, gear:fn:utfx answers mcost / aura / pierce / tgtlow, the header tag (topTag / headTag), u28Update on an
              older file (a pure addition at the end, second run null, a key there in any case kept + noted, an admin utline.power = no utpow rows,
              CRLF kept), migrateUt28 on a scratch file twice (History copy, change-log rows, run once)
  E  engine   (the 0.2.11 harness's bare server boot: vanilla pack store by store with every codec validator, then THIS jar as its own pack)
              no failed store / SEVERE / WARNING of ours about the new files; the 55 copies in the Item store (toPacket), the 9 SkyyArmory ids absent;
              armor weight by sound set; GearUt.ok true for the 55 / false for the 9; bag type + band pick (GearUt.match / pickItem); the REAL
              tooltips (alloy tag, weight, trade-off note + trick lines in green / red); GearUtFx.sum0 on real stacks (worn Caldera Guard set + a
              held Raptorfang: lowtaken / tgtlow summed; a held weapon's taken counts now, 0.3.46's armor-only taken() would not); the Azure Arc's
              fixed slow tier (GearSpeed.ensure)
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: start 1 = migrateUt28 adds only the missing ut28 rows at
              the end (every other byte kept, History copy, change-log rows), GearCfg.load reads them; start 2 changes nothing
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the hit path end to end (GearHitSys -> onHit's tgtMult / isBoss with a live SkyyMobs mob:fn:info), GearArmorSys
calling taken2 on a real hit, the copies' looks on a player / in hand, the 9 SkyyArmory weapons (not built - SkyyArmory's round).
Scratch: tools/dev/scratch/ut28fix2/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.47"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ut28fix2", "harness")]
import skyybuild as B
import harness_kit as HK
import tier_tags as TT
import ut28 as UT28

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.46.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_47_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.46.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = []
EXPECT = {
    "GearCfg": ["+f U28_GC", "+f U28_GK", "+f U28_GL", "+f U28_GS", "+f U28_HEAD", "+f U28_LK", "+f U28_LV", "+f U28_MARK", "+f U28_MARK_ID", "+f U28_WHO",
                "+f UT_AURA", "+f UT_FULLT", "+f UT_LOWT", "+m migrateUt28", "+m u28Log", "+m u28Update", "~<clinit>", "~m apply", "~m defaultsText"],          # the rows, the 3 fields, the one-time update
    "GearUtFx": ["+f T_AURA", "+f T_BOSS", "+f T_LOWTAKEN", "+f T_MCOST", "+f T_TGTFULL", "+f T_TGTLOW", "+m bossMult", "+m bossRank", "+m isBoss", "+m taken2",
                 "+m takenPct", "+m tgtMult", "~<clinit>", "~m checkRow", "~m onHit", "~m trickText"],          # TK + BASE_FROM / BASE_TO in <clinit>
    "GearArmorSys": ["~m handle"],          # taken2 (the held weapon + lowtaken)
    "GearView": ["~m topTag", "~m trickBad"],
    "GearFn": ["~m utfx"],          # fix round ut28fix: "cfg:auraReach" -> utline.auraReach
    "GearPack": ["~<clinit>"],          # fix round ut28fix2: LOOT_IDS without the 4 UT looks
    "GearPool": ["~<clinit>", "~m candM", "~m idIdx", "~m levelsM", "~m liveType", "~m matchM", "~m packText", "~m pickItemM", "~m table", "~m typeOfId", "~m w"],          # ut28fix2: P_ID - 4, the inlined P_N0 constant
    "SkyyGearPlugin": ["~m setup"],          # migrateUt28
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],          # the version + the 3 rows
}
ROWS = UT28.rows()
COPY = [r for r in ROWS if r[4] == "gear"]
ARM = [r for r in ROWS if r[4] == "armory"]
NEW_FILES = sorted(["Server/Item/Items/SkyyGear/UT/%s.json" % r[0] for r in COPY] + ["Common/Items/SkyyGear/UT/%s.png" % r[0] for r in COPY]
                   + ["Common/Icons/ItemsGenerated/%s.png" % r[0] for r in COPY])
U = "00000000-0000-0000-0000-000000000347"
WEIGHT = {"cloth armor": 3, "light armor": 2, "heavy armor": 1}
TAGS = {1: "T3 Bronze", 2: "T6 Dusk", 3: "T9 Azurvane", 4: "T12 Cinder", 5: "T15 Lumen"}


def az_json(z, iid):
    p = [n for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith("/" + iid + ".json")]
    return json.loads(z.read(p[0]).decode("utf-8-sig")) if p else None


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.47 - build script') and g.count('VERSION = "0.3.47"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.check(not UT28.check(), "S tools/ut28.py check: %s" % UT28.check())
    p2 = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "test_tier_tags.py")], capture_output=True, text=True)
    K.check(p2.returncode == 0 and "PASS" in p2.stdout, "S tools/test_tier_tags.py passes: %s" % (p2.stdout + p2.stderr)[-300:])
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (NEW_FILES, []), "S the jar adds exactly the 55 copies + 110 textures / icons, removes nothing")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["Server/Languages/en-US/server.lang", "manifest.json"], "S the only other non-class changes: manifest + server.lang")
    la = za.read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n")
    lb = zb.read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n")
    added = [x for x in lb if x not in set(la)]
    K.check(not [x for x in la if x not in set(lb)] and len(added) == 110 and [x for x in lb if x in set(la)] == la, "S server.lang: every old line kept in order, 110 new lines (%d)" % len(added))
    want = []
    for r in COPY:
        want += ["items.%s.name = %s" % (r[0], r[1]), "items.%s.description = %s - Untiered %s." % (r[0], TAGS[r[3]], r[2])]
    K.eq(sorted(added), sorted(want), "S the 110 lines = name + 'T6 Dusk - Untiered cloth armor.' per copy (the tag first)")
    K.check(not [x for x in lb if any(("items.%s." % r[0]) in x for r in ARM)], "S no lang line for the 9 SkyyArmory ids (its round writes them)")
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    azn = set(az.namelist())
    K.check(not [n for n in NEW_FILES if n in azn], "S no new file shadows a vanilla path")
    pw = json.loads(zb.read("Server/Item/Items/SkyyGear/UT/Weapon_Sword_UT_Paperweight.json"))
    ours = ("TranslationProperties", "Quality", "Variant", "ItemLevel", "Texture", "Icon")
    for r in COPY:
        j = json.loads(zb.read("Server/Item/Items/SkyyGear/UT/%s.json" % r[0]))
        b = az_json(az, r[5])
        rest_j = dict((k, v) for k, v in j.items() if k not in ours)
        rest_b = dict((k, v) for k, v in b.items() if k not in ours + ("Recipe", "$Comment"))
        K.check(rest_j == rest_b and "Recipe" not in j and j["Quality"] == pw["Quality"] and j["Variant"] is True and j["ItemLevel"] == UT28.ZONE_BAND[r[3]][0]
                and j["TranslationProperties"] == {"Name": "server.items.%s.name" % r[0], "Description": "server.items.%s.description" % r[0]}
                and j["Texture"] == "Items/SkyyGear/UT/%s.png" % r[0] and j["Icon"] == "Icons/ItemsGenerated/%s.png" % r[0],
                "S %s = %s's JSON (model %s by path) + our keys, no recipe, quality %s, Lv %d" % (r[0], r[5], j.get("Model") or "(its Parent's)", j.get("Quality"), j.get("ItemLevel", -1)))
        bt = b.get("Texture") or az_json(az, b["Parent"]).get("Texture")
        K.check(zb.read("Common/" + j["Texture"]) != az.read("Common/" + bt), "S %s texture is a recolour of %s (not a vanilla copy)" % (r[0], bt))
    K.check(zb.read("Common/Items/SkyyGear/UT/Armor_UT_FossilSeer_Head.png") != zb.read("Common/Items/SkyyGear/UT/Armor_UT_OasisWarden_Head.png"),
            "S the Z5 cloth (Fossil Seer) looks different from the Z2 one on the same Silk model")
    gsrc = g
    K.check("Weapon_Daggers_UT_DeepcaveShadow" in [r[0] for r in COPY] and [r for r in COPY if r[0] == "Weapon_Daggers_UT_DeepcaveShadow"][0][6] == "Weapon_Daggers_Bronze_Ancient",
            "S Skyy's Ancient Bronze Daggers = the model of Deepcave Shadow (the Z5 Assassin UT)")
    K.check("pierce" not in [r for r in ROWS if r[0] == "Weapon_Spear_UT_MagmaLance"][0][8] and "pierce" not in [r for r in ROWS if r[0] == "Weapon_Crossbow_UT_Stormvent"][0][8],
            "S Magma Lance / Stormvent carry no pierce word (no reader for spear thrusts / bolts)")
    K.check(gsrc.count("@PKG@.GearCfg.migrateUt28();") == 1 and gsrc.index("@PKG@.GearCfg.migrateWc15(") < gsrc.index("@PKG@.GearCfg.migrateUt28();") < gsrc.index("@PKG@.GearCfg.load();", gsrc.index("@PKG@.GearCfg.migrateUt28();")) < gsrc.index("@PKG@.GearBox.ON = @PKG@.GearCfg.HIDE_BOX;"),
            "S setup: migrateUt28 runs once, after migrateWc15, before load()")
    K.save()


# ====================================================================================================== X: the bare JVM
def run_exec(out, jar, scratch, home):
    from jpype import JClass, JString, JArray, JObject, JDouble
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    Cfg, Fx, Ut, GV, Fn = P("GearCfg"), P("GearUtFx"), P("GearUt"), P("GearView"), P("GearFn")
    Props = JClass("java.util.Properties")
    fresh = str(Cfg.defaultsText())
    D = lambda xs: JArray(JDouble)([float(x) for x in xs])

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()
    # ---- the words
    TK = [str(x) for x in Fx.TK]
    K.eq(TK, ["lowhp", "back", "front", "taken", "hp", "mregen", "range", "pierce", "heal", "kb", "tgtlow", "tgtfull", "boss", "lowtaken", "mcost", "aura"], "X TK = the 10 old words + 6")
    K.eq([int(getattr(Fx, "T_" + n)) for n in ("TGTLOW", "TGTFULL", "BOSS", "LOWTAKEN", "MCOST", "AURA", "KB", "LOWHP")], [10, 11, 12, 13, 14, 15, 9, 0], "X T_ indices (old ones unchanged)")
    SB = JClass("java.lang.StringBuilder")
    for r in ROWS:
        b = SB()
        row = Fx.parseRow(JString("%s,%s" % (r[7], r[8])), b)
        K.check(row is not None and b.length() == 0 and Fx.checkRow(JString("utfx[%s]" % r[0]), JString("%s,%s" % (r[7], r[8]))) is None,
                "X %s: parseRow + checkRow accept '%s,%s' (bad: %r)" % (r[0], r[7], r[8], str(b)))
    for bad in ("str cc,tgtlo+5", "mp cc,mcost", "mp hpr,aura+x", "str cc,boss-30x"):
        K.check(Fx.checkRow(JString("utfx[Weapon_Sword_UT_Raptorfang]"), JString(bad)) is not None, "X checkRow refuses %r" % bad)
    tk = [0.0] * 16
    tk[10], tk[11] = 50.0, -25.0
    K.eq([round(float(Fx.tgtMult(D(tk), x)), 4) for x in (0.3, 0.49, 0.5, 0.6, 0.9, 1.0, -1.0)], [1.5, 1.5, 1.0, 1.0, 0.75, 0.75, 1.0],
         "X tgtMult: +50 % under 50 % Health, -25 % at 90 %+, nothing in between / unknown")
    apply(utline__lowTarget="30", utline__fullTarget="100")
    K.eq([int(Cfg.UT_LOWT), int(Cfg.UT_FULLT), round(float(Fx.tgtMult(D(tk), 0.4)), 4), round(float(Fx.tgtMult(D(tk), 0.99)), 4), round(float(Fx.tgtMult(D(tk), 1.0)), 4)],
         [30, 100, 1.0, 1.0, 0.75], "X utline.lowTarget / fullTarget are read live (30 / 100)")
    # ---- fix round ut28fix2 (critic 3): fullTarget is kept above lowTarget at read time - a mob is never both low and full
    apply(utline__lowTarget="99", utline__fullTarget="50")
    K.eq([int(Cfg.UT_LOWT), int(Cfg.UT_FULLT), round(float(Fx.tgtMult(D(tk), 0.6)), 4), round(float(Fx.tgtMult(D(tk), 1.0)), 4)],
         [99, 100, 1.5, 0.75], "X fix: low 99 / full 50 -> full read as 100 (60 % Health = low only, never both)")
    apply(utline__lowTarget="70", utline__fullTarget="70")
    K.eq([int(Cfg.UT_LOWT), int(Cfg.UT_FULLT)], [70, 71], "X fix: full = low -> low + 1")
    apply()
    K.eq([int(Cfg.UT_LOWT), int(Cfg.UT_FULLT), int(Cfg.UT_AURA)], [50, 90, 8], "X the 3 rows' defaults")
    # ---- fix round ut28fix2 (critic 1): the 4 unique vanilla looks used as UT models are out of the random bags; the other 3 bases stay
    Pool = P("GearPool")
    pid = set(str(x) for x in Pool.P_ID)
    out4 = ["Weapon_Daggers_Bronze_Ancient", "Weapon_Sword_Silversteel", "Weapon_Shortbow_Doomed", "Weapon_Spear_Adamantite_Saurian"]
    K.check(not [i for i in out4 if i in pid] and all(i in pid for i in ("Weapon_Longsword_Katana", "Weapon_Axe_Bone", "Weapon_Crossbow_Ancient_Steel")),
            "X fix: the 4 UT looks are not in the bag pool (Katana / Axe_Bone / Crossbow_Ancient_Steel stay)")
    K.check(all(int(Pool.typeOfId(JString(i))) >= 0 for i in out4)
            and [str(Pool.T_KEY[int(Pool.typeOfId(JString(i)))]) for i in out4] == ["Weapon_Daggers", "Weapon_Sword", "Weapon_Shortbow", "Weapon_Spear"],
            "X fix: an owned UT-look base still has its bag type by name (identify / reforge keep working)")
    tb = [0.0] * 16
    tb[12] = -30.0
    K.eq([round(float(Fx.bossMult(D(tb), True)), 4), float(Fx.bossMult(D(tb), False)), float(Fx.bossMult(D(tk), True))], [0.7, 1.0, 1.0], "X bossMult: -30 % on a boss only")
    K.eq([bool(Fx.bossRank(JString(a), JString(b) if b else None)) for a, b in (("boss", "Dragon_Fire"), ("mini", "X"), ("elite", "X"), ("boss", "Skeleton_Elite"), ("", None))]
         + [bool(Fx.bossRank(None, JString("X")))], [True, True, False, False, False, False], "X bossRank: boss / mini count; an elite or a loot.notBosses role or no rank does not")
    tl = [0.0] * 16
    tl[3], tl[13] = 2.0, 10.0
    K.eq([float(Fx.takenPct(D(tl), x)) for x in (0.4, 0.5, 0.9, -1.0)] + [float(Fx.takenPct(None, 0.1))], [12.0, 2.0, 2.0, 2.0, 0.0], "X takenPct: taken + lowtaken while under half Health")
    th = [0.0] * 16
    th[0], th[1] = 30.0, 50.0
    K.eq([round(float(Fx.hitMult(D(th), 0.4, 1, 3.0, False)), 4), round(float(Fx.hitMult(D(th), 0.8, 0, 3.0, False)), 4)], [1.95, 1.0], "X hitMult unchanged (lowhp x back)")
    tt = [(k, v) for k, v in ((10, 50.0), (11, -25.0), (12, -30.0), (13, 6.0), (14, -25.0), (15, 50.0))]
    K.eq([str(Fx.trickText(k, v)) for k, v in tt], ["Damage +50% to enemies under 50% Health", "Damage -25% to enemies at 90%+ Health", "Damage -30% to bosses and mini bosses",
                                                     "Damage taken +6% while under half Health", "Spell Mana cost -25%", "Heal orb also heals party members within 8 blocks at 50%"],
         "X trickText of the 6 words")
    K.eq([bool(GV.trickBad(k, v)) for k, v in ((13, 6.0), (13, -6.0), (14, 30.0), (14, -25.0), (11, -25.0), (10, 50.0), (15, 50.0), (3, 2.0))],
         [True, False, True, False, True, False, False, True], "X trickBad: more taken / dearer spells / a minus = red")
    # ---- the fresh file + the table
    fl = fresh.split("\n")
    for pre in ("ut.", "utfx.", "utpow."):
        K.eq(sorted(x.split("=", 1)[0][len(pre):] for x in fl if x.startswith(pre) and x.split("=", 1)[0][len(pre):] in set(UT28.IDS)), sorted(UT28.IDS),
             "X the fresh file has a %s row for each of the 64 ids" % pre)
    K.check(fresh.count("SkyyGear 0.3.47 ut28 untiered") == 1 and "utline.lowTarget=50" in fresh and "utline.fullTarget=90" in fresh and "utline.auraReach=8" in fresh,
            "X ... the marker once + the 3 rows")
    pw = dict((x.split("=", 1)[0][6:], int(x.split("=", 1)[1])) for x in fl if x.startswith("utpow."))
    for r in ROWS:
        bd = Ut.band(JString(r[0]))
        K.check(bd is not None and list(bd) == list(UT28.ZONE_BAND[r[3]]) and Fx.row(JString(r[0])) is not None and int(Fx.utPow(JString(r[0]))) == pw[r[0]]
                and str(Ut.note(JString(r[0]))) == r[9], "X GearCfg reads %s: band %s, lines, utpow %d, the trade-off line" % (r[0], None if bd is None else list(bd), pw.get(r[0], -1)))
    K.check(all(70 <= v <= 600 for k, v in pw.items() if k in set(UT28.IDS)), "X every new utpow in 70-600")
    K.notes.append("X utpow: %s" % ", ".join("%s %d" % (i, pw[i]) for i in UT28.IDS))
    OA = JArray(JClass("java.lang.Object"))
    ufx = lambda i, w: float(Fn.utfx(OA([JString(i), JString(w)])))
    K.eq([ufx("Weapon_Spellbook_UT_SandscriptCodex", "mcost"), ufx("Weapon_Spellbook_UT_AshfallGrimoire", "mcost"), ufx("Weapon_Wand_UT_HotspringBlessing", "aura"),
          ufx("Weapon_Staff_UT_Stormfossil", "pierce"), ufx("Weapon_Sword_UT_Raptorfang", "tgtlow"), ufx("Weapon_Sword_UT_Raptorfang", "dmg"), ufx("Weapon_Wand_UT_Cavewind", "heal")],
         [-25.0, 30.0, 50.0, 1.0, 50.0, 0.0, -100.0], "X gear:fn:utfx answers SkyyArmory's words by id (mcost / aura / pierce / heal) + tgtlow")
    # ---- fix round ut28fix (critic 2.1): SkyyArmory can read utline.auraReach through the bridge (any id, live)
    a0 = [ufx("Weapon_Wand_UT_HotspringBlessing", "cfg:auraReach"), ufx("", "cfg:auraReach")]
    apply(utline__auraReach="12")
    a1 = ufx("Weapon_Wand_UT_HotspringBlessing", "cfg:auraReach")
    apply()
    K.eq(a0 + [a1, ufx("Weapon_Wand_UT_HotspringBlessing", "auraReach")], [8.0, 8.0, 12.0, 0.0], "X fix: gear:fn:utfx 'cfg:auraReach' = utline.auraReach (8, live 12; the bare word is no trick = 0)")
    # ---- fix round ut28fix (critic 3.4): no trade-off text names a Server Setup threshold (the trick lines carry the live value)
    tn = [(r[0], r[9]) for r in ROWS if any(w.startswith(("tgtlow", "tgtfull", "aura")) for w in r[8].split())]
    K.check(len(tn) == 3 and not [i for i, n in tn if "half Health" in n or "full Health" in n or "blocks" in n]
            and str(Ut.note(JString("Weapon_Sword_UT_Raptorfang"))) == "50% more damage to enemies at low Health. 25% less to enemies at high Health.",
            "X fix: Raptorfang / Bonewhistle / Hotspring texts say low / high Health and nearby: %s" % tn)
    # ---- fix round ut28fix (critic 2.2): the topTag branch only acts on an Untiered description WITH a leading tag - no live one has it
    live_ut = []
    for jp in (jar, os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.47.jar")):
        zj = zipfile.ZipFile(jp)
        for n in zj.namelist():
            if n.endswith(".lang"):
                for ln in zj.read(n).decode("utf-8", "replace").split(chr(10)):
                    m = re.match(r"^items\.(\w*_UT_\w*)\.description = (.*)$", ln.rstrip(chr(13)))
                    if m and m.group(1) not in set(UT28.IDS):
                        live_ut.append((os.path.basename(jp), m.group(1), m.group(2)))
    tagged = [x for x in live_ut if GV.descTag(JString(x[2])) is not None]
    K.check(len(live_ut) >= 19 and not tagged, "X fix: the %d live Untiered descriptions (SkyyGear + SkyyArmory 0.1.47) carry no leading tag, so topTag's new branch changes none of them: %s" % (len(live_ut), tagged[:3]))
    K.eq([str(GV.topTag(JString(x[1]), 0, JString(x[2]))) == str(GV.topTag(JString(x[1]), 0, None)) for x in live_ut], [True] * len(live_ut),
         "X fix: ... each live Untiered id's header tag with its real description = the pre-0.3.47 path (no description)")
    # ---- the header tag
    K.eq(str(GV.headTag(JString("Armor_UT_OasisWarden_Head"), 2, JString("T6 Dusk - Untiered cloth armor."))), "T6 Dusk", "X headTag of a new UT piece = its lang tag (the zone's alloy)")
    K.check(str(GV.topTag(JString("Armor_UT_OasisWarden_Head"), 2, JString("T6 Dusk - Untiered cloth armor."))).startswith("T6 Dusk "), "X topTag keeps the weight word for the flavour sig")
    K.eq(str(GV.topTag(JString("Weapon_Sword_UT_Raptorfang"), 0, JString("T15 Lumen - Untiered sword."))), "T15 Lumen", "X topTag of a new UT weapon = T15 Lumen")
    K.eq(str(GV.topTag(JString("Weapon_Sword_UT_Paperweight"), 0, JString("Untiered sword."))), str(GV.bandTag(JString("Weapon_Sword_UT_Paperweight"))),
         "X a live Z1 UT without a lang tag keeps its band tag (unchanged)")
    # ---- u28Update (pure text)
    blk0 = fl.index("# ---- Untiered trick thresholds (SkyyGear 0.3.47) ----")
    hd = [i for i, x in enumerate(fl) if x.startswith("# ---- The first 28 Zone 1-5 Untiered items (SkyyGear 0.3.47")][0]
    end = hd + 2 + 3 + 3 * 64
    old = "\n".join(fl[:blk0 - 1] + fl[end:])
    K.check("ut28 untiered" not in old and "utline.lowTarget" not in old, "X an older file built from the fresh one minus the 0.3.47 lines")
    r1 = Cfg.u28Update(JString(old))
    t1 = str(r1[0])
    K.check(t1.startswith(old.rstrip("\n")) and t1.count("SkyyGear 0.3.47 ut28 untiered") == 1 and len(list(r1[3])) == 2 * 192 and len(list(r1[1])) == 0,
            "X u28Update: a pure addition at the end (192 rows, no notes)")
    p1 = Props()
    p1.load(JClass("java.io.StringReader")(t1))
    K.check(all(str(p1.getProperty("ut." + r[0])) == "%d,%d,%s" % (UT28.ZONE_BAND[r[3]] + (r[9],)) and str(p1.getProperty("utpow." + r[0])) == str(pw[r[0]]) for r in ROWS),
            "X ... the added rows = the fresh file's")
    lk = [str(x) for x in r1[3]]
    K.check(lk[0] == "ut[Armor_UT_OasisWarden_Head]" and lk[1].startswith("32|40|") and "utpow[Weapon_Bo_UT_CrushingTail]" in lk, "X ... change-log rows key[entry] / columns joined by |")
    K.check(Cfg.u28Update(JString(t1)) is None and Cfg.u28Update(JString(fresh)) is None, "X a second run (marker there) = null; a fresh file = null")
    r2 = Cfg.u28Update(JString(old + "ut.armor_ut_oasiswarden_head=1,5,mine\n"))
    t2 = str(r2[0])
    K.check(t2.count("ut.Armor_UT_OasisWarden_Head=") == 0 and "ut.armor_ut_oasiswarden_head=1,5,mine" in t2 and len(list(r2[3])) == 2 * 191
            and [str(x) for x in r2[1]] == ["ut.Armor_UT_OasisWarden_Head is already in the file - kept"], "X a key already there (any case) is kept + noted, never doubled: %s" % [str(x) for x in r2[1]])
    r3 = Cfg.u28Update(JString(old.replace("utline.power=70", "utline.power=90")))
    K.check("utline.power=90" in old.replace("utline.power=70", "utline.power=90") and len(list(r3[3])) == 2 * 128 and "utpow.Armor_UT_OasisWarden_Head" not in str(r3[0])
            and len(list(r3[1])) == 1 and "kept (an admin's value)" in str(r3[1][0]) and "built-in fit" in str(r3[1][0]), "X an admin utline.power: no utpow rows, one note (they use the built-in fit)")
    pnp = Props()
    pnp.load(JClass("java.io.StringReader")(chr(10).join(x for x in fl if not x.startswith("utpow.Armor_UT_OasisWarden_Head="))))
    Cfg.apply(pnp, False)
    K.check(int(Fx.utPow(JString("Armor_UT_OasisWarden_Head"))) == pw["Armor_UT_OasisWarden_Head"] and "utpow.Armor_UT_OasisWarden_Head" not in str(pnp),
            "X fix: ... and the built-in fit (UTP_ID / UTP_PC) answers a new id without its utpow row (%d)" % int(Fx.utPow(JString("Armor_UT_OasisWarden_Head"))))
    apply()
    crlf = old.replace("\n", "\r\n")
    r4 = str(Cfg.u28Update(JString(crlf))[0])
    K.check(r4.startswith(crlf.rstrip("\r\n")) and "\n" not in r4.replace("\r\n", ""), "X a CRLF file stays CRLF")
    # ---- migrateUt28 on a scratch file twice
    md = os.path.join(scratch, "mig")
    os.makedirs(md, exist_ok=True)
    fp = os.path.join(md, "config.properties")
    open(fp, "wb").write(old.encode("latin-1"))
    Cfg.FILE = JClass("java.nio.file.Paths").get(fp)
    m1 = str(Cfg.migrateUt28())
    b1 = open(fp, "rb").read()
    K.check("192 rows" in m1 and b1.decode("latin-1") == t1, "X migrateUt28 start 1: the file = u28Update's text: %s" % m1[:160])
    hist = [os.path.join(dp, f) for dp, dn, fs in os.walk(md) for f in fs if f != "config.properties"]
    K.check([h for h in hist if open(h, "rb").read() == old.encode("latin-1")], "X ... the old file kept in History: %s" % [os.path.relpath(h, md) for h in hist][:6])
    logt = "".join(open(h, encoding="latin-1").read() for h in hist if open(h, "rb").read() != old.encode("latin-1"))
    K.check(logt.count("SkyyGear 0.3.47\t-\tupdate\t") == 192, "X ... 192 change-log rows (Undo): %d" % logt.count("SkyyGear 0.3.47\t-\tupdate\t"))
    m2 = str(Cfg.migrateUt28())
    K.check(m2 == "" and open(fp, "rb").read() == b1, "X migrateUt28 start 2 changes nothing")
    K.save()


# ====================================================================================================== E: the booted engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JArray, JImplements, JOverride, JObject, JShort
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
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    ITEM = E["ITEM"]
    mine = set(UT28.IDS)
    # this bare boot's Interaction store misses some vanilla parents: a copy's message is fine only when its vanilla base gets the SAME one
    bmsg = set(r[1] for r in list(E["rec"]) + list(E["vrec"]) if r[0] in ("SEVERE", "WARNING"))          # vrec = the vanilla pack's own load
    base_of = dict((r[0], r[5]) for r in COPY)

    def same_as_base(m):
        hit = [i for i in mine if i in m]
        return len(hit) == 1 and hit[0] in base_of and m.replace("**" + hit[0] + "_", "**" + base_of[hit[0]] + "_") in bmsg and ("**" + hit[0] + "_") in m
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and [i for i in mine if i in r[1]] and not same_as_base(r[1])]
    K.notes.append("E V: %d messages about the new copies are the bare boot's own (their vanilla base gets the same one)" % len(
        [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and [i for i in mine if i in r[1]] and same_as_base(r[1])]))
    old_ut = [r[1][:120] for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and "_UT_" in r[1] and r not in ours]
    K.notes.append("E V: messages about the LIVE 0.3.46 Untiered copies in this bare boot (vanilla parents the bare store lacks, not this round): %s" % old_ut[:4])
    K.check(not ours and set(E["fail"]) <= set(E["vfail"]), "E V: no failure about the 55 new copies (failed stores %s, vanilla's %s): %s" % (E["fail"], E["vfail"], [r[1][:200] for r in ours[:3]]))
    for r in COPY:
        it = ITEM.getAssetMap().getAsset(r[0])
        try:
            pk = it.toPacket() if it is not None else None
            K.check(it is not None and pk is not None and (it.getArmor() is not None) == r[0].startswith("Armor_"), "E %s in the Item store (toPacket%s)" % (r[0], ", Armor block" if r[0].startswith("Armor_") else ""))
        except Exception as ex:
            K.check(False, "E %s packet: %s" % (r[0], str(ex)[:200]))
    K.check(not [r[0] for r in ARM if ITEM.getAssetMap().getAsset(r[0]) is not None], "E the 9 SkyyArmory ids are not items yet (its round builds them)")
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Data, Roll, Defs, View, Ut, Fx, Pool, Spd = (P("GearCfg"), P("Gear"), P("GearData"), P("GearRoll"), P("GearDefs"), P("GearView"), P("GearUt"),
                                                            P("GearUtFx"), P("GearPool"), P("GearSpeed"))
    Props = JClass("java.util.Properties")
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()
    K.eq(dict((r[0], int(View.weightOf(JString(r[0])))) for r in COPY if r[0].startswith("Armor_")), dict((r[0], WEIGHT[r[2]]) for r in COPY if r[0].startswith("Armor_")),
         "E every armor copy's weight by its sound set = its kind (Cloth 3 / Light 2 / Heavy 1)")
    tab = Cfg.UTAB
    okd = dict((r[0], bool(Ut.ok(tab, int(Ut.idx(tab, JString(r[0])))))) for r in ROWS)
    K.eq(okd, dict((r[0], r[4] == "gear") for r in ROWS), "E GearUt.ok: the 55 copies usable, the 9 SkyyArmory rows wait for their items")
    K.check(all(int(Pool.typeOfId(JString(r[0]))) >= 0 and bool(Data.isGear(JString(r[0]))) and not bool(Ut.crafted(JString(r[0]))) for r in ROWS),
            "E every id: a bag type, gear, no recipe makes it")
    for r in COPY:
        ty = int(Pool.typeOfId(JString(r[0])))
        lo, hi = UT28.ZONE_BAND[r[3]]
        K.check(bool(Ut.match(tab, int(Ut.idx(tab, JString(r[0]))), ty, lo)) and bool(Ut.match(tab, int(Ut.idx(tab, JString(r[0]))), ty, hi))
                and not bool(Ut.match(tab, int(Ut.idx(tab, JString(r[0]))), ty, hi + 1)), "E %s: an orange %s bag at Lv %d-%d may pick it" % (r[0], str(Pool.T_NAME[ty]), lo, hi))
    seen = set()
    for _n in range(400):
        x = Ut.pickItem(int(Pool.typeOfId(JString("Weapon_Sword_UT_Raptorfang"))), 96)
        if x is not None:
            seen.add(str(x))
    K.check("Weapon_Sword_UT_Raptorfang" in seen and not [s for s in seen if s.startswith("Weapon_Sword_UT_Paperweight")], "E pickItem(Sword, Lv 96) draws Raptorfang, never the Zone 1 Paperweight: %s" % sorted(seen))
    br = Gear.bridge()
    lv = {}

    @JImplements("java.util.function.Function")
    class Skill(object):
        @JOverride
        def apply(self, a):
            return JInt(lv.get(str(a[1]), 200))
    br.put("skill:fn:level", Skill())
    br.put("class:list", "Warrior:Swordsmanship,Mage:Arcana,Archer:Archery,Assassin:Stealth,Berserker:Fury")
    br.put("class:skill:" + U, "Swordsmanship")
    br.put("class:weapons:Warrior", "Weapon_Sword_,Weapon_Spear_")
    U1 = JClass("java.util.UUID").fromString(U)
    RUT = int(Defs.R_UT)
    HAL = JClass("java.util.ArrayList")

    def tip(iid, lvl):
        d = Roll.newDoc(JString(iid), JInt(RUT), True, JString("ut"), JInt(lvl))
        txt, col = HAL(), HAL()
        View.lines(JString(iid), d, U1, txt, col)
        return [(str(txt.get(k)).replace(chr(2), ""), None if col.get(k) is None else str(col.get(k))) for k in range(txt.size())]
    ta = tip("Armor_UT_OasisWarden_Chest", 36)
    K.notes.append("E Oasis Warden's Robe tooltip: %s" % ta)
    tx = [a for a, b in ta]
    dsc = View.descText(JString("Armor_UT_OasisWarden_Chest"))          # this bare boot loads no lang: the header falls back to the band tag (X checks the lang tag path)
    K.check(tx[0] == str(View.headTag(JString("Armor_UT_OasisWarden_Chest"), 2, dsc)) and "Cloth Armor" in tx[:4] and [x for x in tx[:6] if x.startswith("UNTIERED ")],
            "E the Robe's header: the tier line (%r, lang %r), Cloth Armor, the UNTIERED rarity line: %s" % (tx[0], None if dsc is None else str(dsc), tx[:6]))
    K.check("Ability: Trade-off" in tx and [x for x in tx if x == [r for r in ROWS if r[0] == "Armor_UT_OasisWarden_Chest"][0][9]], "E ... the trade-off section + its orange line")
    good, bad = str(Defs.C_GRAY), None
    tw = tip("Weapon_Sword_UT_Raptorfang", 96)
    K.notes.append("E Raptorfang tooltip: %s" % tw)
    lo_ = [c for a, c in tw if a == "Damage +50% to enemies under 50% Health"]
    hi_ = [c for a, c in tw if a == "Damage -25% to enemies at 90%+ Health"]
    K.check(lo_ and hi_ and lo_[0] == str(Defs.C_GRAY) and hi_[0] != lo_[0], "E Raptorfang: the tgtlow line (an upside, grey) and the tgtfull line in the downside colour (%s / %s)" % (lo_, hi_))
    # ---- the tricks of real stacks: a worn Caldera Guard set + a held Raptorfang
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")

    def stack(iid, lvl):
        return Data.put(IS(JString(iid), JInt(1)), Roll.newDoc(JString(iid), JInt(RUT), True, JString("ut"), JInt(lvl)), None)
    arm = SIC(JShort(4))
    for k, sl in enumerate(("Head", "Chest", "Hands", "Legs")):
        arm.setItemStackForSlot(JShort(k), stack("Armor_UT_CalderaGuard_" + sl, 76))
    main = stack("Weapon_Sword_UT_Raptorfang", 96)
    s0 = Fx.sum0(U1, main, arm)
    K.check(s0 is not None and float(s0[13]) == 32.0 and float(s0[10]) == 50.0 and float(s0[11]) == -25.0,
            "E sum0: the worn Caldera Guard set's lowtaken 6+10+6+10 = 32, the held Raptorfang's tgtlow 50 / tgtfull -25: %s" % (None if s0 is None else [float(x) for x in s0]))
    K.eq([float(Fx.takenPct(s0, 0.3)), float(Fx.takenPct(s0, 0.7))], [32.0, 0.0], "E takenPct on it: +32 % under half Health, 0 above")
    apply(**{"utfx__Weapon_Sword_UT_Raptorfang": "str cd,tgtlow+50 tgtfull-25 taken+8"})
    emp = SIC(JShort(4))
    K.eq([float(Fx.taken2(U1, main, emp, None, None)), float(Fx.taken(U1, emp))], [8.0, 0.0],
         "E fix: a held weapon's taken+8 counts in taken2 (0.3.46's taken() read the armor only = 0)")
    apply()
    az = stack("Weapon_Longsword_UT_AzureArc", 15)
    dz = Spd.ensure(JString("Weapon_Longsword_UT_AzureArc"), Data.effective(JString("Weapon_Longsword_UT_AzureArc"), az.getMetadata()))
    K.eq(int(Fx.swingOf(JString("Weapon_Longsword_UT_AzureArc"))), 0, "E the Azure Arc's fixed tier = slow (0)")
    K.check(dz is not None and int(Spd.tierOf(dz)) == 0, "E GearSpeed.ensure gives the Azure Arc's document the slow tier")
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, Ut = JClass(PKG + "GearCfg"), JClass(PKG + "GearUt")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    K.check(c0 is not None, "D the live copy has a config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39"]
    t0 = c0.decode("latin-1")
    admin = re.search(r"(?m)^utline\.power\s*[=:]\s*(\S+)", t0)
    have = [i for i in UT28.IDS if re.search(r"(?mi)^ut\." + re.escape(i) + r"\s*[=:]", t0)]
    m0 = "".join(str(getattr(Cfg, x)()) for x in MIG)
    K.check(m0 == "", "D the older one-time updates do nothing on the live copy (%r)" % m0[:80])
    m1 = str(Cfg.migrateUt28())
    Cfg.load()
    c1 = open(fc, "rb").read()
    n_pow = 0 if admin and admin.group(1) != "70" else 64
    K.notes.append("D start 1: %s (utline.power %s, ut28 keys already there %d)" % (m1[:240], admin.group(1) if admin else "absent", len(have)))
    K.check(("%d rows" % (128 + n_pow - 3 * len(have))) in m1 or (have and "kept" in m1), "D start 1: migrateUt28 added the missing rows: %s" % m1[:200])
    K.check(c1.startswith(c0.rstrip(b"\r\n")) and c1.count(b"SkyyGear 0.3.47 ut28 untiered") == 1 and (b"\r\n" in c0) == (b"\r\n" in c1), "D start 1: a pure addition at the end, the marker once, line endings kept")
    K.check(all(Ut.band(r[0]) is not None and list(Ut.band(r[0])) == list(UT28.ZONE_BAND[r[3]]) for r in ROWS), "D GearCfg.load reads the 64 new rows from the live copy")
    K.check(Ut.size() >= 64 + 40, "D the Untiered table holds the old + the new rows (%d)" % int(Ut.size()))
    m2 = str(Cfg.migrateUt28())
    Cfg.load()
    K.check(m2 == "" and open(fc, "rb").read() == c1, "D start 2 changes nothing (%r)" % m2[:80])
    hist = [os.path.join(dp, f) for dp, dn, fs in os.walk(home) for f in fs if open(os.path.join(dp, f), "rb").read() == c0 and os.path.join(dp, f) != fc]
    K.check(hist, "D the live file's old bytes are kept in History")
    K.save()


# the compare phase: harness_kit's own with this round's 165 new files + server.lang (both checked in S) hidden from its non-class check
_RC0 = HK.run_compare


def run_compare47(out, jar, old_jar, pkg, expect, added, removed=()):
    import zipfile as _z
    _orig = _z.ZipFile
    hide = set(NEW_FILES) | {"Server/Languages/en-US/server.lang"}

    class _ZF(_orig):
        def namelist(self):
            n = _orig.namelist(self)
            return [x for x in n if x not in hide] if os.path.abspath(self.filename) in (os.path.abspath(jar), os.path.abspath(old_jar)) else n
    _z.ZipFile = _ZF
    try:
        _RC0(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        _z.ZipFile = _orig


HK.run_compare = run_compare47
if "--expect-dump" in sys.argv:
    EXPECT = {}
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
