"""SkyySkills 0.4.39 - harness for the rebirth wrap-up + sound pass round 2 (tools/skills_0_4_39_patch.py): RbStat (SkyyRebirth's
rebirth:fn:stat -> max Health / Mana / Stamina + Class Wisdom class XP) and SkSnd (level up, Overall level up, perfect dodge).
Build first: python tools/skills_0_4_39_patch.py && python SkyySkills/build_skyyskills_0.4.39.py
             python tools/rebirth_0_3_3_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.3.py   (the REAL rebirth:fn:stat answers)

    python SkyySkills/test_skyyskills_0.4.39.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.38 -> 0.4.39: exactly the planned members differ; SkSnd + RbStat added (SkillRb - the rebirth participant - unchanged)
  G   g39      EXECUTED:
               REBIRTH STATS with the REAL SkyyRebirth 0.3.3 RbFn(6) = rebirth:fn:stat reading real players/<pkey>.properties, on REAL
               EntityStatMaps (Health 100 + 50 armour, Mana 0 + 20 base Mana + 4 SkyyAccessories percent, Stamina 10): RbStat.tick at
               n = 0 (no modifier), 1 / 5 / 10 (+3 / 15 / 30 % of the flat max, skyyacc_ left out), 12 (a hand edit above rebirth.max
               = 30 %), stat.cap 20 (20 %), the Class nodes (Vitality / Greater Vitality / Focus / Void Ascendant / Class Wisdom /
               Might: health 10 %, mana 6 %, stamina 5 %, class XP +10 % through the REAL SkillBonus.xpBonus / boost for a class slot
               only, Might ignored); a still-loading profile (no answer) keeps the last values; rebirth.stats off / no SkyyRebirth
               remove all three; a re-tick changes nothing; RbStat.CUR forgets players who left (Acro.retainOnline)
               SOUNDS on REAL GamePacketHandler players (tools/soundpass_kit.py: the game's own SoundEvent map from Assets.zip, every
               packet the engine writes captured): SkSnd.level / overall / dodge = one PlaySoundEvent2D (UI) each with the default ids;
               the 0.5 s gate; Overall first = the skill sting skipped; muted by settings:sounds:<uuid> FALSE (TRUE / absent play);
               the master / per-sound switches, an empty id, a missing id (one WARN, nothing played); the perfect dodge switch
               skills.perfectDodge through settings:fn:get; the REAL SkillXp.gain3 level-up (one sting per award, none with
               skills.levelUp hidden) and the REAL PDodge.perfect; config read (a file turning them off) + the fresh default block; the
               Server Setup rows (kit header: Sounds category, 7 sound rows + rebirth.stats) and the check= hook through CfgFn.checkHook
  0.4.38's phases on the 0.4.39 jar: G38, F fakes, G37, R3 rebirth participant, RS restart, RB, R route, X exec, D live + DM (start
               twice on a scratch COPY of the live Skyy_SkyySkills) - the checks that pin 0.4.38's row count / default file are
               re-checked here instead (EXPECTED_* below)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SPK

VERSION = "0.4.39"
PKG = "com.skyy.skills."
RPKG = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.38.jar")
RB_JAR = os.path.abspath(HK.arg("--rebirth", os.path.join(ROOT, "SkyyRebirth", "SkyyRebirth-0.3.3.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth6", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))

EXPECT = {
    "SkillCfg": ["~m load"],                                 # the default file (G39 block, header version) + the two reads
    "SkillBonus": ["~m xpBonus"],                            # Class Wisdom
    "SkillXp": ["~m gain4"],                                 # the level-up sound
    "Overall": ["~m levelUp"],                               # the Overall sound
    "PDodge": ["~m perfect"],                                # the perfect dodge sound
    "Perks": ["~m tick"],                                    # RbStat.tick
    "Acro": ["~m retainOnline"],                             # RbStat.CUR of players who left
    "SkyySkillsPlugin": ["~m setup"],                        # the ready line
    # version texts / the kit's rows (+ the Sounds category, the check= hook)
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "CfgFile": ["~<clinit>"],                                # the kit's per-row tables (8 more rows)
}
ADDED = ["RbStat", "SkSnd"]
SOUNDS = [("level", "SFX_Workbench_Upgrade_Complete_Default"), ("overall", "SFX_Memories_Unlock_Local"), ("dodge", "SFX_Ability_Wind_Strike_Imbue_Local")]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T38 = tmod("test_skyyskills_0.4.38.py", "t0438")
path = T38.path
# tools/tidy_local.py archives old jars (backups/archive/old-jars-*.tar.xz): the inherited phases that compare with 0.4.31 - 0.4.35 read an
# extracted copy from SKYY_OLD_JAR_DIR (a folder inside this round's scratch) when the jar is not next to its build script any more
_m, _seen = T38, set()
while _m is not None and id(_m) not in _seen:
    _seen.add(id(_m))
    _oj = getattr(_m, "OLD_JAR", None)
    if _oj and not os.path.isfile(_oj) and os.environ.get("SKYY_OLD_JAR_DIR"):
        _m.OLD_JAR = os.path.join(os.environ["SKYY_OLD_JAR_DIR"], os.path.basename(_oj))
    _m = next((getattr(_m, _n) for _n in ("T37", "T36", "T35", "T34", "T32") if getattr(_m, _n, None) is not None and id(getattr(_m, _n)) not in _seen), None)


def run_g39(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride, JInt, JFloat, JLong, JBoolean, JString, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, RB_JAR], verify=True)
    st = SPK.Stage()
    J = lambda n: JClass(PKG + n)
    R = lambda n: JClass(RPKG + n)
    Cfg, Sto, Defs, Snd, Rbs, Bon = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("SkSnd"), J("RbStat"), J("SkillBonus")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    US, fld = st.us, st.fld
    work = os.path.join(scratch, "g39")
    os.makedirs(os.path.join(work, "players"))
    Cfg.FILE = path(os.path.join(work, "xp.properties"))
    K.notes.append("load: " + str(Cfg.load())[:200])
    fresh = open(os.path.join(work, "xp.properties"), encoding="latin-1").read()
    want_block = ["sounds.enabled=true"] + sum([["sound.%s=true" % k, "sound.%s.id=%s" % (k, d)] for k, d in SOUNDS], []) + ["rebirth.stats=true"]
    lines = [x for x in fresh.split("\n") if x and not x.startswith("#")]
    K.check(lines[-8:] == want_block and "SkyySkills 0.4.39 - XP rules" in fresh, "G config: the fresh xp.properties ends with the 0.4.39 block: %s" % lines[-8:])
    K.check(bool(Snd.ON) and bool(Snd.LEVEL) and str(Snd.LEVEL_ID) == SOUNDS[0][1] and str(Snd.OVL_ID) == SOUNDS[1][1] and str(Snd.DODGE_ID) == SOUNDS[2][1]
            and bool(Rbs.ON), "G config: the defaults read (sounds on, the three ids, rebirth.stats on)")
    Sto.DIR = path(os.path.join(work, "players"))
    br = Sto.bridge()

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v

    # ================================================================ REBIRTH STATS: the stat type store + real EntityStatMaps
    EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")

    def stype(id_, mn, mx):
        t = US.allocateInstance(EST.class_)
        fld(EST.class_, "id").set(t, JString(id_))
        fld(EST.class_, "min").set(t, JFloat(mn))
        fld(EST.class_, "max").set(t, JFloat(mx))
        return t

    @JImplements("java.util.function.IntFunction")
    class Arr(object):
        @JOverride
        def apply(self, n):
            return JClass("java.lang.reflect.Array").newInstance(EST.class_, int(n))
    arrf = Arr()
    amap = ILT(arrf)
    fld(ILT.class_, "array").set(amap, JArray(JAWM)([stype("Health", 0.0, 100.0), stype("Mana", 0.0, 0.0), stype("Stamina", -4.0, 10.0)]))
    FKC = JClass("java.lang.Class").forName("com.hypixel.hytale.assetstore.SkyySoundTestStore", True, AS.class_.getClassLoader())
    sst = US.allocateInstance(FKC)
    fld(AS.class_, "tClass").set(sst, EST.class_)
    fld(AS.class_, "assetMap").set(sst, amap)
    fld(EST.class_, "ASSET_STORE").set(None, sst)
    for nm, ix in (("HEALTH", 0), ("MANA", 1), ("STAMINA", 2)):
        fld(DST.class_, nm).set(None, JInt(ix))
    K.check([int(DST.getHealth()), int(DST.getMana()), int(DST.getStamina())] == [0, 1, 2] and float(J("Overall").typeMax(0)) == 100.0,
            "G stats: the stand-in stat types Health 0 (max 100), Mana 1, Stamina 2")

    def statmap():
        m = ESM()
        vals = []
        for idx, nm, v, mn in ((0, "Health", 100.0, 0.0), (1, "Mana", 0.0, 0.0), (2, "Stamina", 10.0, -4.0)):
            sv = US.allocateInstance(ESV.class_)
            for fn_, val in (("id", JString(nm)), ("index", JInt(idx)), ("value", JFloat(v)), ("min", JFloat(mn)), ("max", JFloat(v))):
                fld(ESV.class_, fn_).set(sv, val)
            vals.append(sv)
        fld(ESM.class_, "values").set(m, JArray(ESV)(vals))
        m.putModifier(0, "armor_test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(50.0)))
        m.putModifier(1, "skyyskill_basemana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(20.0)))
        m.putModifier(1, "skyyacc_mana", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(4.0)))
        return m

    KEYS = ("skyyskill_rebirthhp", "skyyskill_rebirthmana", "skyyskill_rebirthstamina")

    def ours(m):
        out = []
        for i, k in enumerate(KEYS):
            md = m.getModifier(i, k)
            out.append(None if md is None else round(float(md.getAmount()), 4))
        return out

    def maxes(m):
        return [round(float(m.get(i).getMax()), 4) for i in range(3)]

    # the REAL SkyyRebirth 0.3.3: RbStore reads players/<pkey>.properties (no IO thread = read at once), RbFn(6) = rebirth:fn:stat
    RbStore, RbCfg, RbFn = R("RbStore"), R("RbCfg"), R("RbFn")
    rdir = os.path.join(scratch, "rb39", "players")
    os.makedirs(rdir)
    RbStore.DIR = path(rdir)
    fnstat = RbFn(6)
    UUID = JClass("java.util.UUID")
    seq = [0]

    def prof(lines):
        seq[0] += 1
        u = UUID(0x39000 + seq[0], 0x77)
        open(os.path.join(rdir, str(u) + ".properties"), "w").write("".join("%s=%s\n" % kv for kv in lines))
        return u
    K.check(str(RbCfg.keyOf(UUID(1, 2))) == str(UUID(1, 2)) and float(RbCfg.STAT_PER) == 3.0 and float(RbCfg.STAT_CAP) == 30.0 and int(RbCfg.MAX) == 10,
            "G stats: SkyyRebirth's defaults (3 % a rebirth, cap 30, max 10; pkey = UUID without SkyyProfiles)")
    br.put("rebirth:fn:stat", fnstat)
    # no-rebirth baseline flat maxes: Health 150, Mana 24 (20 + 4), Stamina 10
    cases = [("n=0", [("n", 0)], [None, None, None]), ("n=1", [("n", 1)], [4.5, 0.6, 0.3]), ("n=5", [("n", 5)], [22.5, 3.0, 1.5]),
             ("n=10", [("n", 10)], [45.0, 6.0, 3.0]), ("n=12 (hand edit above max)", [("n", 12)], [45.0, 6.0, 3.0])]
    for what, lines_, want in cases:
        u = prof(lines_)
        m = statmap()
        Rbs.tick(u, m)
        K.check(ours(m) == want, "G stats %s: modifiers %s, want %s (flat 150 / 20 - skyyacc_ left out / 10)" % (what, ours(m), want))
        base = [150.0, 24.0, 10.0]
        K.check(maxes(m) == [round(b + (w or 0.0), 4) for b, w in zip(base, want)], "G stats %s: the engine's max %s" % (what, maxes(m)))
        before = ours(m)
        Rbs.tick(u, m)
        K.check(ours(m) == before, "G stats %s: a second tick changes nothing" % what)
        K.check(float(Rbs.classXp(u)) == 0.0 and float(Bon.xpBonus(u, int(Defs.classSlot(0)))) == 0.0, "G stats %s: no class XP without Class Wisdom" % what)
    RbCfg.STAT_CAP = 20.0
    u = prof([("n", 10)])
    m = statmap()
    Rbs.tick(u, m)
    K.check(ours(m) == [30.0, 4.0, 2.0], "G stats: stat.cap 20 -> 20 %% at n = 10: %s" % ours(m))
    RbCfg.STAT_CAP = 30.0
    # the Class nodes: all = 3 + Void Ascendant 2 = 5; health 5 + Vitality 3 + Greater Vitality 2 = 10; mana 5 + Focus 1 = 6; Class Wisdom 5 x 2 = 10 % XP
    u = prof([("n", 1), ("node.Class.hp", 3), ("node.Class.hp2", 2), ("node.Class.mana", 1), ("node.Class.key", 1), ("node.Class.xp", 5), ("node.Class.dmg", 4), ("node.Class.def", 2)])
    K.check([float(fnstat.apply(JArray(JObject)([u, JString(x)]))) for x in ("all", "health", "mana", "classxp", "damage", "defense")] == [5.0, 5.0, 1.0, 10.0, 4.0, 2.0],
            "G stats: the REAL rebirth:fn:stat answers all 5 / health 5 / mana 1 / classxp 10 / damage 4 / defense 2")
    m = statmap()
    Rbs.tick(u, m)
    K.check(ours(m) == [15.0, 1.2, 0.5], "G stats nodes: Health 10 %%, Mana 6 %%, Stamina 5 %% (Might / Guard not here - SkyyGear): %s" % ours(m))
    cs = int(Defs.classSlot(0))
    K.check(abs(float(Rbs.classXp(u)) - 0.10) < 1e-9 and abs(float(Bon.xpBonus(u, cs)) - 0.10) < 1e-9 and float(Bon.xpBonus(u, int(Defs.MINING))) == 0.0
            and int(Bon.boost(u, cs, JLong(1000))) == 1100 and int(Bon.boost(u, int(Defs.MINING), JLong(1000))) == 1000,
            "G stats nodes: Class Wisdom = +10 %% class XP through SkillBonus.xpBonus / boost (class slots only; Mining unchanged)")
    K.check(float(Bon.xpBonus(u, int(Defs.EXPLORATION))) == 0.0, "G stats nodes: Exploration never boosted")
    # a profile SkyyRebirth is still reading (no answer) keeps the last values
    br.put("rebirth:fn:stat", Const(None))
    Rbs.tick(u, m)
    K.check(ours(m) == [15.0, 1.2, 0.5] and abs(float(Rbs.classXp(u)) - 0.10) < 1e-9, "G stats: no answer yet = the last values stay (never a false drop)")
    # no SkyyRebirth: every modifier removed, no class XP
    br.remove("rebirth:fn:stat")
    Rbs.tick(u, m)
    K.check(ours(m) == [None, None, None] and maxes(m) == [150.0, 24.0, 10.0] and float(Rbs.classXp(u)) == 0.0, "G stats: without SkyyRebirth the three modifiers are removed: %s" % ours(m))
    br.put("rebirth:fn:stat", fnstat)
    Rbs.tick(u, m)
    K.check(ours(m) == [15.0, 1.2, 0.5], "G stats: SkyyRebirth back = applied again")
    # rebirth.stats=false through the real config read
    open(os.path.join(work, "xp.properties"), "a").write("rebirth.stats=false\nsounds.enabled=false\nsound.dodge.id=\nsound.level=false\n")
    Cfg.load()
    K.check(not bool(Rbs.ON) and not bool(Snd.ON) and str(Snd.DODGE_ID) == "" and not bool(Snd.LEVEL) and bool(Snd.OVL), "G config: a file turning them off reads off (rebirth.stats, sounds, an empty dodge id, sound.level)")
    Rbs.tick(u, m)
    K.check(ours(m) == [None, None, None] and float(Bon.xpBonus(u, cs)) == 0.0, "G stats: rebirth.stats off removes the modifiers and the class XP")
    open(os.path.join(work, "xp.properties"), "w").write(fresh)
    Cfg.load()
    K.check(bool(Rbs.ON) and bool(Snd.ON) and bool(Snd.LEVEL) and str(Snd.DODGE_ID) == SOUNDS[2][1], "G config: the default file reads on again")
    Rbs.tick(u, m)
    K.check(ours(m) == [15.0, 1.2, 0.5], "G stats: switched on again = applied")
    # a fault inside rebirth:fn:stat: the last values stay, one WARN
    @JImplements("java.util.function.Function")
    class Boom(object):
        @JOverride
        def apply(self, o):
            raise RuntimeError("boom")
    br.put("rebirth:fn:stat", Boom())
    Rbs.tick(u, m)
    K.check(ours(m) == [15.0, 1.2, 0.5] and bool(Rbs.WARNED), "G stats: a failing rebirth:fn:stat keeps the last values (logged once)")
    br.put("rebirth:fn:stat", fnstat)
    # fix round: a PROFILE SWITCH (PROFILES-CONTRACT rules 2 + 4) never carries the old profile's values: profile:fn:key -> <uuid>-p2
    pk2 = str(u) + "-p2"
    open(os.path.join(rdir, pk2 + ".properties"), "w").write("n=1\n")
    br.put("profile:fn:key", Const(JString(pk2)))
    K.check(str(Sto.pkey(u)) == pk2 and str(RbCfg.keyOf(u)) == pk2, "G profiles: the switch resolves to %s in both mods" % pk2)
    br.put("rebirth:fn:stat", Const(None))   # SkyyRebirth still reading profile 2
    Rbs.tick(u, m)
    K.check(ours(m) == [None, None, None] and float(Rbs.classXp(u)) == 0.0 and float(Bon.xpBonus(u, cs)) == 0.0,
            "G profiles: switched + no answer yet = profile 1's boosts removed, no Class Wisdom: %s / %s" % (ours(m), float(Rbs.classXp(u))))
    br.put("rebirth:fn:stat", fnstat)
    Rbs.tick(u, m)
    K.check(ours(m) == [4.5, 0.6, 0.3] and float(Rbs.classXp(u)) == 0.0, "G profiles: profile 2 (n = 1, no nodes) answers -> its own 3 %%: %s" % ours(m))
    br.put("rebirth:fn:stat", Const(None))
    Rbs.tick(u, m)
    K.check(ours(m) == [4.5, 0.6, 0.3], "G profiles: no answer on the SAME profile keeps its last values")
    br.remove("profile:fn:key")
    br.put("rebirth:fn:stat", fnstat)
    Rbs.tick(u, m)
    K.check(ours(m) == [15.0, 1.2, 0.5] and abs(float(Rbs.classXp(u)) - 0.10) < 1e-9, "G profiles: back on profile 1 = its boosts + Class Wisdom again")
    # a fresh login (no cached values) with no answer leaves the saved modifiers alone (never a false drop)
    Rbs.CUR.remove(u)
    br.put("rebirth:fn:stat", Const(None))
    Rbs.tick(u, m)
    K.check(ours(m) == [15.0, 1.2, 0.5] and float(Rbs.classXp(u)) == 0.0, "G profiles: login + no answer = the saved modifiers stay untouched")
    # the REAL SkyyRebirth 0.3.3 on an UNREADABLE profile file (a folder named <pkey>.properties) answers nothing -> nothing dropped
    br.put("rebirth:fn:stat", fnstat)
    Rbs.tick(u, m)
    ubad = UUID(0x39fff, 0x77)
    os.makedirs(os.path.join(rdir, str(ubad) + ".properties"))
    mb = statmap()
    mb.putModifier(0, KEYS[0], SMO(MTG.MAX, CAL.ADDITIVE, JFloat(15.0)))   # saved on the player from an earlier session
    Rbs.tick(ubad, mb)
    K.check(fnstat.apply(JArray(JObject)([ubad, JString("all")])) is None and ours(mb) == [15.0, None, None],
            "G stats: an unreadable SkyyRebirth file = no answer = the saved Health boost stays (no false drop): %s" % ours(mb))
    # players who left: Acro.retainOnline drops their RbStat.CUR entry (the real cleanup; universe with nobody online)
    K.check(Rbs.CUR.containsKey(u), "G stats: CUR holds the player")
    Rbs.CUR.keySet().retainAll(JClass("java.util.HashSet")())
    K.check(not Rbs.CUR.containsKey(u) and float(Rbs.classXp(u)) == 0.0, "G stats: forgetting a player clears the class XP")
    gen = open(os.path.join(HERE, "build_skyyskills_%s.py" % VERSION), encoding="utf8").read()
    K.check("{PKG}.RbStat.CUR.keySet().retainAll(online);" in gen and "{PKG}.RbStat.tick(u, m);" in gen, "G stats: Acro.retainOnline + Perks.tick call RbStat (build script)")

    # ================================================================ SOUNDS (real GamePacketHandler players, the game's SoundEvent map)
    ua, ub, uc = "00000000-0000-4000-8000-0000000039a1", "00000000-0000-4000-8000-0000000039b2", "00000000-0000-4000-8000-0000000039c3"
    pa, pb, pc = st.player("Skyy", ua), st.player("Bee", ub), st.player("Cee", uc)
    st.universe()
    Ua, Ub, Uc = UUID.fromString(ua), UUID.fromString(ub), UUID.fromString(uc)
    st.clear()
    Snd.LAST.clear()
    K.check(bool(Snd.level(pa)) and st.sounds() == [("Skyy", SOUNDS[0][1], "UI", "2d")], "G sound: level up = one PlaySoundEvent2D (UI): %s" % st.sounds())
    st.clear()
    K.check(not bool(Snd.level(pa)) and st.sounds() == [], "G sound: a second level-up sting within 0.5 s is skipped")
    K.check(bool(Snd.overall(pb)) and not bool(Snd.level(pb)) and st.sounds() == [("Bee", SOUNDS[1][1], "UI", "2d")],
            "G sound: Overall level up first = the skill sting skipped: %s" % st.sounds())
    st.clear()
    K.check(bool(Snd.dodge(pc, Uc)) and st.sounds() == [("Cee", SOUNDS[2][1], "UI", "2d")], "G sound: perfect dodge: %s" % st.sounds())
    # muted per player (settings:sounds:<uuid>)
    st.clear()
    Snd.LAST.clear()
    br.put("settings:sounds:" + ua, JBoolean(False))
    m0 = int(Snd.MUTED.get())
    K.check(not bool(Snd.level(pa)) and not bool(Snd.overall(pa)) and not bool(Snd.dodge(pa, Ua)) and st.sounds() == [] and int(Snd.MUTED.get()) == m0 + 3,
            "G sound: settings:sounds:<uuid> FALSE mutes all three")
    br.put("settings:sounds:" + ua, JBoolean(True))
    K.check(bool(Snd.level(pa)), "G sound: settings:sounds:<uuid> TRUE plays")
    br.remove("settings:sounds:" + ua)
    Snd.LAST.clear()
    K.check(bool(Snd.level(pa)) and not bool(Snd.muted(Ub)), "G sound: absent = plays")
    # the perfect dodge chat switch (settings:fn:get answers FALSE for skills.perfectDodge)
    ASK = []

    @JImplements("java.util.function.Function")
    class SetGet(object):
        @JOverride
        def apply(self, o):
            ASK.append(str(o[1]))
            return JBoolean(str(o[1]) not in ("skills.perfectDodge", "skills.levelUp"))
    br.put("settings:fn:get", SetGet())
    st.clear()
    Snd.LAST.clear()
    K.check(not bool(Snd.dodge(pc, Uc)) and st.sounds() == [] and "skills.perfectDodge" in ASK, "G sound: perfect dodge line hidden = no sound")
    br.remove("settings:fn:get")
    # the switches, an empty id, a missing id
    for setup, what in ((lambda: setattr(Snd, "ON", False), "master off"), (lambda: setattr(Snd, "LEVEL", False), "sound.level off"),
                        (lambda: setattr(Snd, "LEVEL_ID", ""), "an empty id"), (lambda: setattr(Snd, "LEVEL_ID", SPK.BAD_ID), "a missing id")):
        Cfg.load()
        Snd.LAST.clear()
        st.clear()
        setup()
        K.check(not bool(Snd.level(pa)) and st.sounds() == [], "G sound: %s = no sound" % what)
    K.check(Snd.WARNED.containsKey(SPK.BAD_ID), "G sound: a missing id is warned once")
    Cfg.load()
    K.check(str(Snd.err("")) == "None" or Snd.err("") is None, "G sound: err('') = fine (no sound)")
    # the REAL callers: SkillXp.gain3 levelling up (one sting per award), PDodge.perfect
    Snd.LAST.clear()
    st.clear()
    J("SkillXp").gain3(pa, int(Defs.MINING), JLong(5000), JBoolean(False), JBoolean(False))
    snds = st.sounds("Skyy")
    K.check(len(snds) == 1 and snds[0][1] in (SOUNDS[0][1], SOUNDS[1][1]), "G sound: the REAL gain3 level-up plays ONE sting: %s" % snds)
    K.notes.append("gain3 level-up sting: %s; chats %s" % (snds, [c[1][:60] for c in st.chats("Skyy")][:4]))
    br.put("settings:fn:get", SetGet())
    Snd.LAST.clear()
    st.clear()
    J("SkillXp").gain3(pa, int(Defs.FORAGING), JLong(5000), JBoolean(False), JBoolean(False))
    K.check(not any(x[1] == SOUNDS[0][1] for x in st.sounds("Skyy")), "G sound: skills.levelUp hidden = no level-up sting: %s" % st.sounds("Skyy"))
    @JImplements("java.util.function.Function")
    class NoOvl(object):
        @JOverride
        def apply(self, o):
            return JBoolean(str(o[1]) != "skills.overallUp")
    br.put("settings:fn:get", NoOvl())
    Snd.LAST.clear()
    st.clear()
    J("SkillXp").gain3(pa, int(Defs.FARMING), JLong(5000), JBoolean(False), JBoolean(False))
    K.check(st.sounds("Skyy") == [("Skyy", SOUNDS[0][1], "UI", "2d")], "G sound: Overall line hidden = the REAL gain3 plays the skill level-up sting: %s" % st.sounds("Skyy"))
    br.remove("settings:fn:get")
    Snd.LAST.clear()
    st.clear()
    PD = J("PDodge")
    PD.STATE.clear()
    paid = int(PD.perfect(pb, None, None, JLong(10 ** 12), JBoolean(False)))
    K.check(paid == 0 and st.sounds("Bee") == [("Bee", SOUNDS[2][1], "UI", "2d")], "G sound: the REAL PDodge.perfect plays the dodge sound once: %s" % st.sounds("Bee"))
    st.clear()
    PD.perfect(pb, None, None, JLong(10 ** 12 + 50), JBoolean(False))
    K.check(st.sounds("Bee") == [], "G sound: the same roll again (PDodge.mark) = no second sound")
    # ================================================================ Server Setup rows + the check= hook (the REAL kit)
    Rows, Fn = J("CfgRows"), J("CfgFn")
    rows = SPK.kit_rows(Rows)
    SPK.sound_rows(K, rows, "sounds.enabled", [("sound.%s" % k, "sound.%s.id" % k, d) for k, d in SOUNDS], prefix="G ")
    r = rows.get("rebirth.stats")
    K.check(r is not None and r[2] == "general" and r[3] == "bool" and r[4] == "true" and "live" in r[9], "G ROW rebirth.stats = a live bool in General, default on: %s" % r)
    K.check(all(rows["sound.%s.id" % k][2] == "sounds" for k, _d in SOUNDS) and len(rows) == 249, "G ROWS: the Sounds category, 249 rows (241 + 8)")
    K.check(SPK.kit_check(Fn, Rows, "sound.level.id", SPK.BAD_ID) is not None and SPK.kit_check(Fn, Rows, "sound.level.id", "a b") is not None
            and SPK.kit_check(Fn, Rows, "sound.overall.id", "SFX_Coins_Land") is None and SPK.kit_check(Fn, Rows, "sound.dodge.id", "") is None,
            "G check= SkSnd.check through CfgFn.checkHook: a missing id / a bad character refused, a real id / empty accepted")
    K.check("sounds on" in str("sounds " + str(Snd.text())) and "rebirth:fn:stat" in str(Rbs.text()), "G texts: SkSnd.text / RbStat.text for the ready line")
    K.save()


# ---- 0.4.38's phases on this jar. Checks that pin 0.4.38's default file / row count are expected to differ by exactly the 0.4.39
# block (re-checked in G39): 0.4.38's "fresh file differs from 0.4.37's ONLY by" and 0.4.37's "241 rows" style checks.
EXPECTED = ("G coin: the fresh file differs from 0.4.37's ONLY", "G coin: load() with no file writes the 0.4.38 default", "G37 rows", "G37 ROWS",
            "G37 config rows", "G37 Server Setup", "G7 Server Setup: 241 rows", "R3 config rows", "R3 rows")


def wrap(fn):
    def run(out, jar, scratch, home):
        tmp = out + ".inner.json"
        fn(tmp, jar, scratch, home)
        d = json.load(open(tmp))
        K = HK.Child(out)
        K.ok, K.notes = d["ok"], d["notes"]
        for f in d["fails"]:
            if any(f.startswith(e) for e in EXPECTED):
                K.ok += 1
                K.notes.append("expected in 0.4.39 (re-checked in G39): " + f[:140])
            else:
                K.fails.append(f)
        K.save()
    return run


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("g39", run_g39), ("g38", wrap(T38.run_g38)), ("fake15", T38.run_fake15), ("fake25", T38.run_fake25), ("g37", wrap(T38.run_g37)),
                   ("r3", wrap(T38.run_r3)), ("restart", T38.run_restart), ("r1", T38.run_r1), ("route", T38.run_route), ("exec", T38.run_exec),
                   ("live", wrap(T38.run_live))],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
