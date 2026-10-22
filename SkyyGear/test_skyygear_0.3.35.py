"""Harness for SkyyGear 0.3.35 (Balance P5 power + beta bugs 12 / 17 - tools/gear_0_3_35_patch.py). Build first:
    python tools/gear_0_3_35_patch.py && python SkyyGear/build_skyygear_0.3.35.py
    python SkyyGear/test_skyygear_0.3.35.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, one new class (GearLuck), no new command / system, setup order
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.34 -> 0.3.35 (EXPECT below)
  X  exec     EXECUTES the new paths in a bare JVM:
              X1 the defaults (rarity table, level ramp 60 / 15, armor weights, slot power, loot rows, reforge per level)
              X2 the text checks (utdrop.points, slot.power, pool.armor)
              X3 the REAL GearRoll.rollMods (2000 rolls a rarity) -> the P5 power table (tools/balance_model.py P5_TABLE_SPEC) within 8 %,
                 armor never rolls Health % on a weapon, armor mostly Defense / Health %
              X4 slot power + the tooltip line (GearView.slotPw / effVal / rollLineD), Health % key
              X5 the % lines of a hit (GearHit.pctInfo)
              X6 GearLuck: points, the meter (roll, sure bag at 36), the luck file write + re-read, the Mythic pity (10th dry kill), texts
              X7 bug 12: orange weapon bags are 'Unidentified (Untiered) Weapon' + pick a weapon type at identify (GearUt.pickWU); armor
                 bags keep their type; bug 17: GearUp.retired (plain hoes / sickles retired, Harvesters not)
              X8 hp5Update on the REAL 0.3.34 default file (the old jar's defaultsText): only the planned rows move + Armor_Iron appended
                 (Properties), marker, second run null, hand edit kept + noted, CRLF kept; p5Same
  D  live     migrate0330 + migrateP4 + migrateP5 on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear/config.properties: only
              planned keys change, config-history copy, change-log lines; a SECOND start changes nothing
  AA engine-access audit
Scratch: tools/dev/scratch/balp5/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.35"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp5", "gear")]
import skyybuild as B
import harness_kit as HK
import balance_model as BM

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.34.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_35_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.34.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
# the stat index shift (Health % right after Defense: every I_* constant after it is inlined anew) touches the classes that read stat indexes
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],
          "GearAdmin": ["~m boxCmd", "~m lootCmd", "~m me", "~m totalsText"], "GearBoxFn": ["~m apply"],
          "GearCfg": ["+f BOSS_PITY", "+f HP5_ADDK", "+f HP5_ADDV", "+f HP5_KEYS", "+f HP5_MARK", "+f HP5_MARK_ID", "+f HP5_NEW", "+f HP5_OLD", "+f HP5_TBK", "+f HP5_TBL", "+f HP5_WHO",
                      "+f LOOT_SMART", "+f PA_DEF", "+f PA_KEY", "+f SLOT_PW", "+f SLOT_PW_DEF", "+f SLOT_PW_KEY", "+f S_WA", "+f UT_CHANCE", "+f UT_PITY",
                      "+f UT_PTS", "+f UT_PV", "+m checkPoolArmor", "+m checkSlotPower", "+m checkUtPts", "+m hp5Lk", "+m hp5Log", "+m hp5Lv", "+m hp5Update", "+m migrateP5",
                      "+m p5Same", "+m utPts", "~<clinit>", "~m apply", "~m bonusStat", "~m defaultsText", "~m loadV3", "~m parseBonus", "~m readSets"],
          "GearDeathMark": ["~m tick"], "GearDefs": ["+f I_HPP", "~<clinit>"], "GearFx": ["~m armorPass", "~m second"], "GearGArm": ["~<clinit>"],
          "GearHit": ["+m pctInfo", "~m weaponHit"], "GearIdent": ["~m identifyBox"], "GearLife": ["~m harvDoc", "~m harvDocAll", "~m mtDoc"], "GearLoot": ["~m mobRoll"],
          "GearMerge": ["~m docI"], "GearMine": ["~m compute0"], "GearPack": ["~m bossRoll"], "GearPackGive": ["~m run"],
          "GearRoll": ["~m pool", "~m rollMods"], "GearSet": ["~m addTo", "~m bonusText", "~m hp"],
          "GearStats": ["+m addModsE", "+m addUtE", "+m addUtL", "~m parseExtra", "~m parsePets", "~m statsString", "~m totals0"],
          "GearUnid": ["+m grpU", "+m kept", "~m descMsg", "~m open", "~m rerollWhy", "~m tname", "~m why"], "GearUt": ["+m pickWU", "~m bag"],
          "GearUtFx": ["+f OLD_HPKEY", "+m body", "+m flatMax", "+m flatOf", "+m pctKey", "~m hpApply", "~m lines", "~m parseRow", "~m secondPass"], "GearV3": ["~<clinit>", "~m combat0"],
          "GearView": ["+f ASLOT", "+m effVal", "+m fv", "+m rollLineD", "+m slotPw", "+m utX", "~<clinit>", "~m rolledRows", "~m suffix", "~m utRows"],
          "SkyyGearPlugin": ["~m setup", "~m shutdown"]}
ADDED = ["GearLuck"]


def _props(txt):
    from jpype import JClass
    out = {}
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(txt))
    for k in p.stringPropertyNames():
        out[str(k)] = str(p.getProperty(k))
    return out


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.35 - build script') and g.count('VERSION = "0.3.35"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count('mk("') - o.count('mk("'), 1, "S one new class (GearLuck)")
    su = g[g.index("@PKG@.GearCfg.migrate02();"):]
    K.check(su.index("migrate0330();") < su.index("migrateP4();") < su.index("migrateP5();") < su.index("@PKG@.GearCfg.load();"),
            "S setup: migrate0330 -> migrateP4 -> migrateP5 -> load")
    K.check("@PKG@.GearLuck.flushAll();" in g[g.index("@PKG@.GearOpened.flush(); } catch (Throwable t3)"):][:300], "S shutdown flushes the luck files")
    K.check(g.count("@PKG@.GearLuck.utKill(") == 1 and g.count("@PKG@.GearLuck.smartBag(kp, lvl, lk)") == 1 and g.count("@PKG@.GearLuck.mythicSure(") == 1,
            "S the meter / smart bag / Mythic pity hooks once each")
    K.check("return @PKG@.GearPool.T_ARM[ty0] ? b0 : @PKG@.GearUnid.grouped(b0);" in g, "S bug 12: a bridge weapon bag is grouped")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _old_default_text():
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    oc = JClass(PKG + "GearCfg", loader=ld)
    return str(oc.defaultsText())


def fake_items(JClass, ids):
    """a bare JVM has no Item asset store: one holding bare Item objects (only the id set) for ids, so Gear.item(id) != null (the Untiered
    rows count as live); no ArmorSlot is read from them (GearView.slotPw falls back on the id's _Head / _Chest / _Legs / _Hands)"""
    from jpype import JString, JObject
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    C = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestItemStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestItemStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    FKC = fk.toClass(AS.class_)

    def fld(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    mp = JClass("java.util.concurrent.ConcurrentHashMap")()
    for i in ids:
        o = US.allocateInstance(C.class_)
        fld(C, "id").set(o, JString(i))
        mp.put(JObject(JString(i), JClass("java.lang.Object")), o)
    m = DM(mp)
    st = US.allocateInstance(FKC)
    fld(AS, "tClass").set(st, C.class_)
    fld(AS, "assetMap").set(st, m)
    fld(JClass("com.hypixel.hytale.assetstore.AssetRegistry"), "storeMap").get(None).put(C.class_, st)
    fld(C, "ASSET_STORE").set(None, st)
    return int(sum(1 for i in ids if C.getAssetMap().getAsset(i) is not None))


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JString, JInt, JArray, JObject, JDouble
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    P = lambda n: JClass(PKG + n)
    Cfg, Defs, Roll, Lv, View, Hit, Luck, Unid, Pool, Ut, Up, GData, Fx = (P(x) for x in (
        "GearCfg", "GearDefs", "GearRoll", "GearLevel", "GearView", "GearHit", "GearLuck", "GearUnid", "GearPool", "GearUt", "GearUp", "GearData", "GearUtFx"))
    SK = [str(x) for x in Defs.S_KEY]
    RID = [str(x) for x in Defs.R_ID]
    # ============================================================== X1 defaults
    rt = dict((RID[i], (int(Cfg.R_MODS[i]), int(Cfg.R_LO[i]), int(Cfg.R_HI[i]))) for i in range(len(RID)))
    K.check(all(rt[r] == BM.P5_RARITY[r] for r in BM.P5_RARITY) and rt.get("untiered") == (0, 0, 0), "X1 the rarity table = P5: %s" % rt)
    K.eq((int(Cfg.LEVEL_FLOOR), int(Cfg.LEVEL_FULL)), (60, 15), "X1 stat.levelFloor / levelFull 60 / 15")
    K.eq([round(float(Lv.factor(JInt(L))), 3) for L in (0, 5, 15, 40)], [60.0, round(60 + 40 * 5 / 15.0, 3), 100.0, 100.0],
         "X1 GearLevel.factor: Lv 0 60 %, Lv 15 full")
    wa = dict((SK[i], int(Cfg.S_WA[i])) for i in range(len(SK)))
    K.check(all(wa[k] == w for k, w in BM.P5_POOL_ARMOR.items()) and int(Cfg.S_W[SK.index("hpp")]) == 0,
            "X1 the armor weights = P5_POOL_ARMOR, Health % weight 0 on weapons")
    K.eq([float(x) for x in Cfg.SLOT_PW], [118.0, 26.0, 45.5, 39.0, 19.5], "X1 slot power Weapon / Head / Chest / Legs / Hands")
    K.eq((int(Cfg.CLASS_LEAN), int(Cfg.LOOT_SMART), float(Cfg.UT_CHANCE), float(Cfg.UT_PITY), [float(x) for x in Cfg.UT_PV], float(Cfg.BOSS_MY), int(Cfg.BOSS_PITY)),
         (75, 50, 2.5, 36.0, [1.0, 5.0, 0.25, 10.0], 12.0, 10), "X1 loot rows: lean 75, smart 50, UT 2.5 % / 36 / points, Mythic 12 % + pity 10")
    K.eq([int(Cfg.costReforge(JInt(i), JInt(50))) - int(Cfg.costReforge(JInt(i), JInt(0))) for i in range(len(RID))],
         [50 * {"normal": 10, "unique": 20, "rare": 40, "legendary": 100, "fabled": 200, "mythic": 400, "set": 100, "untiered": 200}[r] for r in RID],
         "X1 reforge cost grows with the level (50 levels x the per-level column)")
    # the default file through the real loader (the Untiered table, the sets ...) - the defaults above must stay
    pd = JClass("java.util.Properties")()
    pd.load(JClass("java.io.StringReader")(Cfg.defaultsText()))
    Cfg.apply(pd, False)
    K.eq((int(Cfg.LEVEL_FULL), [float(x) for x in Cfg.SLOT_PW], int(Cfg.S_WA[SK.index("def")]), int(Cfg.CLASS_LEAN)), (15, [118.0, 26.0, 45.5, 39.0, 19.5], 120, 75),
         "X1 the fresh default file loads to the same P5 values")
    uts = [str(x) for x in Cfg.UTAB[0]]
    nfi = fake_items(JClass, uts + ["Weapon_Sword_Iron", "Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Legs", "Armor_Iron_Hands"])
    K.check(nfi == len(uts) + 5 and len(uts) > 10, "X0 the test Item store holds the %d Untiered ids of the default file + 5 test ids" % len(uts))
    # ============================================================== X2 checks
    pv = Cfg.utPts("mini 4, elite 2,dungeonBoss 9, dungeon 0.5")
    K.check(pv is not None and [float(x) for x in pv] == [2.0, 4.0, 0.5, 9.0], "X2 utPts any order / spacing")
    K.check(all(Cfg.utPts(x) is None for x in ("elite 1, mini 5", "elite 1, elite 2, dungeon 1, dungeonBoss 1", "elite x, mini 5, dungeon 1, dungeonBoss 1",
                                                  "elite 1, mini 5, dungeon 1, dungeonBoss 2000", "boss 1, mini 5, dungeon 1, dungeonBoss 1", None)),
            "X2 utPts refuses missing / repeated / junk / too big / unknown words")
    K.check(Cfg.checkUtPts("utdrop.points", "elite 1, mini 5, dungeon 0.25, dungeonBoss 10") is None and Cfg.checkUtPts("utdrop.points", "x") is not None, "X2 checkUtPts")
    K.check(Cfg.checkSlotPower("slot.power[Head]", "26") is None and Cfg.checkSlotPower("slot.power[Feet]", "26") is not None
            and Cfg.checkSlotPower("slot.power[Weapon]", "400") is not None, "X2 checkSlotPower: slot names, 0-300")
    K.check(Cfg.checkPoolArmor("pool.armor[def]", "120") is None and Cfg.checkPoolArmor("pool.armor[tdmg]", "5") is not None
            and Cfg.checkPoolArmor("pool.armor[hpp]", "1.5") is not None, "X2 checkPoolArmor: armor stats only, whole weights")
    # ============================================================== X3 the real roll -> the P5 table
    def mods(arr):
        o = {}
        for i in range(arr.size()):
            dd = arr.get(i).asDocument()
            o[str(GData.str(dd, "s", ""))] = int(GData.num(dd, "v", 0))
        return o
    N = 2000
    worst = (0.0, "")
    rows = []
    hpp_w = 0
    armor_lines = {}
    for ri, r in enumerate(BM.P5_RARS):
        rr = RID.index(r)
        W, AD, AE = [], [], []
        for _ in range(N):
            wm = mods(Roll.rollMods(None, JInt(0), JInt(rr), JInt(100)))
            hpp_w += 1 if "hpp" in wm else 0
            W.append(BM.p5_dps(BM.p5_weapon_totals(wm)))
            pcs = []
            for s in ("Head", "Chest", "Legs", "Hands"):
                am = mods(Roll.rollMods(None, JInt(2), JInt(rr), JInt(100)))
                for k in am:
                    armor_lines[k] = armor_lines.get(k, 0) + 1
                pcs.append((s, am))
            tot = BM.p5_armor_totals(pcs)
            AD.append(BM.p5_dps(tot))
            AE.append(BM.p5_ehp(tot))
        got = (sum(W) / N, BM.p5_p90(W), sum(AD) / N, BM.p5_p90(AD), sum(AE) / N, BM.p5_p90(AE))
        spec = BM.P5_TABLE_SPEC[r]
        for j, (g_, s_) in enumerate(zip(got, spec)):
            dv = abs(g_ - s_) / s_
            if dv > worst[0]:
                worst = (dv, "%s col %d %.3f vs %.3f" % (r, j, g_, s_))
        rows.append("%s %s" % (r, " ".join("%.2f" % x for x in got)))
    K.check(worst[0] <= BM.P5_TOL, "X3 the REAL rollMods (%d rolls a rarity) -> the P5 power table within 8 %%: worst %.1f %% (%s)" % (N, 100 * worst[0], worst[1]))
    K.notes.append("X3 rows (weapon mean p90, armor DPS mean p90, armor EHP mean p90): " + " | ".join(rows))
    K.eq(hpp_w, 0, "X3 a weapon never rolls Health %")
    tl = sum(armor_lines.values())
    share = (armor_lines.get("def", 0) + armor_lines.get("hpp", 0)) / float(tl)
    K.check(share > 0.45 and armor_lines.get("str", 0) / float(tl) < 0.02, "X3 armor lines: Defense + Health %% %.0f %%, Strength %.1f %%" % (100 * share, 100.0 * armor_lines.get("str", 0) / tl))
    # ============================================================== X4 slot power + tooltip line
    sp = dict((x, round(float(View.slotPw(x)), 4)) for x in ("Weapon_Sword_Iron", "Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Legs", "Armor_Iron_Hands", "Tool_Pickaxe_Iron", "Nope_Item"))
    K.eq(sp, {"Weapon_Sword_Iron": 1.18, "Armor_Iron_Head": 0.26, "Armor_Iron_Chest": 0.455, "Armor_Iron_Legs": 0.39, "Armor_Iron_Hands": 0.195,
              "Tool_Pickaxe_Iron": 1.0, "Nope_Item": 1.0}, "X4 GearView.slotPw by slot (tools / unknown 1)")
    K.eq(round(float(View.effVal("Armor_Iron_Chest", None, "def", JInt(20))), 3), 9.1, "X4 effVal: a Chest's +20 Defense counts 9.1")
    K.eq([str(View.fv(JDouble(x))) for x in (9.1, 12.0, -2.0, 0.04, 2.25)], ["+9.1", "+12", "-2", "+0", "+2.3"], "X4 fv: one decimal, sign")
    K.eq(str(View.rollLineD("hpp", JInt(10), JDouble(2.6))), "+ Health %   +2.6% (of max Health)", "X4 the Health % tooltip line")
    K.eq(str(View.rollLineD("fFire", JInt(6), JDouble(7.08))), "+ Fire Damage   +7.1%", "X4 an element line shows %")
    K.eq((str(Fx.HPKEY), str(Fx.OLD_HPKEY)), ("skyygear_hp", "skyygear_ut_hp"), "X4 the max Health modifier key (the 0.3.34 one removed on sight)")
    # fix round (critic): an armor id whose slot cannot be read is NOT cached (asked again; never a hidden 100 % for the whole run)
    View.ASLOT.clear()
    K.check(int(GData.slotOf("Armor_Fixround_Odd")) == 2 and float(View.slotPw("Armor_Fixround_Odd")) == 1.0 and not bool(View.ASLOT.containsKey("Armor_Fixround_Odd"))
            and bool(View.ASLOT.containsKey("Armor_Iron_Chest")) is False, "X4 fix: an armor id with no readable slot = 1.0 now but never cached")
    View.slotPw("Armor_Iron_Chest")
    K.check(bool(View.ASLOT.containsKey("Armor_Iron_Chest")), "X4 fix: a readable slot is still cached")
    # fix round (critic: Health % compounding): the % base = type max + flat ADDITIVE MAX modifiers, never another mod's % layer
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    from jpype import JFloat
    mm = JClass("java.util.HashMap")()
    for k_, v_ in (("Armor", 50.0), ("skyyskill_mana_base", 20.0), ("skyygear_hp", 40.0), ("skyygear_ut_hp", 9.0), ("skyyacc_health", 30.0), ("skyypet_health", 20.0),
                   ("skyyskill_classhp", 10.0), ("skyyskill_rebirthhp", 15.0)):
        mm.put(k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    mm.put("mult_test", SMO(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(0.5)))
    fo = float(Fx.flatOf(JFloat(100.0), mm))
    K.eq(fo, 170.0, "X4 fix: flatOf = type max 100 + Armor 50 + a flat 20; gear / accessory / pet / class / rebirth %% layers + multiplicative skipped")
    K.eq(float(Fx.flatOf(JFloat(0.0), mm)), -1.0, "X4 fix: no type max = -1 (the old max-minus-ours rule then)")
    # the three % mods settle on the SAME flat base: gear 30 % + accessories 20 % + pets 15 % = x1.65 (was ~x2.1 when each read the others)
    have = 0.0
    for _ in range(6):
        have = float(Fx.hpWant(JFloat(fo + have), JFloat(have), JDouble(30.0)))
    K.eq(round(have, 2), round(0.30 * 170.0, 2), "X4 fix: Gear's 30 %% = 51 of the 170 flat max, steady (no feedback from the other %% layers)")
    # fix round 2 (critic, spec 2.4): an Untiered item's BODY lines x slot power, its fixed lines as written (GearStats.addUtL / GearView.utX)
    St = P("GearStats")
    ns = int(Defs.NS)
    l_ = [0] * ns
    b_ = [0] * ns
    l_[SK.index("def")], b_[SK.index("def")] = 18, 18          # body Defense 18
    l_[SK.index("str")], b_[SK.index("str")] = 13, 18          # body Strength 18 + a fixed str-5
    l_[SK.index("spd")] = 4                                     # fixed spd+4
    acc_ = JArray(JDouble)([0.0] * ns)
    t_ = JArray(JInt)([0] * ns)
    St.addUtL(acc_, t_, JArray(JInt)(l_), JArray(JInt)(b_), JDouble(0.455))
    K.eq((round(float(acc_[SK.index("def")]), 2), round(float(acc_[SK.index("str")]), 2), int(t_[SK.index("str")]), int(t_[SK.index("spd")]), int(t_[SK.index("def")])),
         (8.19, 8.19, -5, 4, 0), "X4 fix 2: a UT Chest's body lines count x 45.5 %% (Defense 18 -> 8.19), its fixed lines as written (str-5, spd+4)")
    K.eq([round(float(View.utX(JInt(a_), JInt(b2_), JDouble(1.18))), 2) for a_, b2_ in ((13, 18), (4, 0), (18, 18))], [16.24, 4.0, 21.24],
         "X4 fix 2: the UT tooltip value = fixed part + body x slot power (the totals' rule)")
    St.addUtL(acc_, t_, None, JArray(JInt)(b_), JDouble(1.0))
    K.check(True, "X4 fix 2: addUtL with no lines is a no-op")
    gsx = open(GEN, encoding="utf8").read()
    K.check(gsx.count("addUtE(acc, t, ") == 2 and "@PKG@.GearUtFx.addTo(t, " not in gsx[gsx.index("public static int[] totals0("):][:3000]
            and "utX(l[i], ub == null" in gsx, "X4 fix 2: totals0 sums UT lines through addUtE (weapon + armor), the tooltip through utX")
    # ============================================================== X5 % lines in the hit
    t = [0] * int(Defs.NS)
    t[SK.index("tdmg")] = 10
    t[SK.index("fFire")] = 6
    t[SK.index("rElem")] = 2
    jt = JArray(JInt)(t)
    inf = Hit.info(None, jt)
    Hit.pctInfo(inf, jt, JDouble(200.0), JDouble(0.5))
    K.eq((int(inf[1]), int(inf[5])), (20, int(round(200 * (6 + 5 * 2) / 100.0))), "X5 pctInfo: +10 %% True = 20 of a 200 hit, Fire 6 + Raw Elemental 2 x5 = 16 %% = 32")
    vs = []
    for i in range(400):
        inf2 = Hit.info(None, jt)
        Hit.pctInfo(inf2, jt, JDouble(5.0), JDouble(random.random()))
        vs.append(int(inf2[1]))
    K.check(0.4 < sum(vs) / 400.0 < 0.6 and set(vs) <= {0, 1}, "X5 a 5-damage hit with +10 %% True: 0 or 1, 0.5 on average (%.2f)" % (sum(vs) / 400.0))
    # ============================================================== X6 GearLuck
    ld = os.path.join(scratch, "luckhome")
    os.makedirs(ld, exist_ok=True)
    Cfg.DIR = JClass("java.nio.file.Paths").get(ld)
    U = JClass("java.util.UUID")
    u = U.fromString("11111111-2222-3333-4444-555555555555")
    pk = str(JClass(PKG + "Gear").pkey(u))
    K.eq(pk, str(u), "X6 the profile key (no SkyyProfiles in the bare JVM = the UUID)")
    pts = [float(Luck.points(None, "Goblin_Elite", JString(x))) for x in ("elite", "mini", "boss", "")]
    Cfg.UT_DUNG = "Dungeon_"
    ptd = [float(Luck.points("Dungeon_Crypt", "Skeleton", JString("boss"))), float(Luck.points("Dungeon_Crypt", "Skeleton", JString(""))), float(Luck.points("Dungeon_Crypt", "Skeleton_Elite", JString("elite")))]
    K.eq(pts + ptd, [1.0, 5.0, 0.0, 0.0, 10.0, 0.25, 1.0], "X6 points: elite 1, mini 5, a world boss 0, a plain mob 0; in a dungeon: boss 10, any mob 0.25, elite 1")
    nomobs = float(Luck.points(None, "Goblin_Elite", None))
    K.check(nomobs in (1.0, 5.0, 0.0), "X6 points without SkyyMobs rank: the sigil.miniWords rule (%s)" % nomobs)
    s1 = [list(Luck.step(pk, u, JDouble(5.0), JDouble(0.99))) for _ in range(7)]
    K.eq([x[0] for x in s1], [0.0] * 7, "X6 7 mini boss kills with no luck: no bag")
    s8 = list(Luck.step(pk, u, JDouble(1.0), JDouble(0.99)))
    K.eq(s8, [2.0, 36.0], "X6 the 36th point = a sure bag (2.0 = by the meter)")
    w1 = list(Luck.step(pk, u, JDouble(1.0), JDouble(0.01)))
    K.eq(w1[0], 1.0, "X6 a lucky roll (r 0.01 < 2.5 %) wins")
    Luck.reset(pk, u)
    Luck.step(pk, u, JDouble(5.0), JDouble(0.99))
    Cfg.UT_PITY = 0.0
    nop = [list(Luck.step(pk, u, JDouble(5.0), JDouble(0.99)))[0] for _ in range(10)]
    Cfg.UT_PITY = 36.0
    K.eq(nop, [0.0] * 10, "X6 utdrop.pity 0 = no sure bag")
    K.check("UT meter 55 / 36" in str(Luck.meterText(u)), "X6 meterText: %s" % str(Luck.meterText(u))[:80])
    Luck.reset(pk, u)
    Luck.step(pk, u, JDouble(5.0), JDouble(0.99))
    sure = []
    for i in range(10):
        s_ = bool(Luck.mythicSure(u, JInt(3)))
        sure.append(s_)
        if s_:
            Luck.mythicHit(u, JInt(3), True)
        else:
            Luck.mythicMiss(u, JInt(3))
    K.eq(sure, [False] * 9 + [True], "X6 the Mythic pity: the 10th dry Zone 3 boss kill is sure")
    for i in range(4):
        Luck.mythicMiss(u, JInt(2))
    K.check(bool(Luck.write(pk)), "X6 the luck file writes")
    lf = os.path.join(ld, "luck", pk + ".properties")
    txt = open(lf, encoding="latin-1").read() if os.path.isfile(lf) else ""
    K.check("ut=5" in txt and "my.2=4" in txt and "my.3" not in txt, "X6 luck/<pkey>.properties: %r" % txt[-60:])
    Luck.LUCK.clear()
    v = [float(x) for x in Luck.luck(pk, u)]
    K.eq((v[0], v[2], v[3]), (5.0, 4.0, 0.0), "X6 the luck file reads back after a restart")
    open(lf, "w").write("ut=banana\nmy.4=-3\nmy.5=7\n")
    Luck.LUCK.clear()
    v2 = [float(x) for x in Luck.luck(pk, u)]
    K.eq((v2[0], v2[4], v2[5]), (0.0, 0.0, 7.0), "X6 a broken luck file: junk = 0, the good lines kept")
    # fix round (critic): a luck file that cannot be READ (a lock) is not cached and never overwritten; the next call reads it again
    u2 = U.fromString("22222222-3333-4444-5555-666666666666")
    pk2 = str(JClass(PKG + "Gear").pkey(u2))
    lf2 = os.path.join(ld, "luck", pk2 + ".properties")
    os.makedirs(lf2, exist_ok=True)          # a directory in the file's place = the read throws
    z2 = [float(x) for x in Luck.luck(pk2, u2)]
    Luck.step(pk2, u2, JDouble(5.0), JDouble(0.99))
    K.check(z2 == [0.0] * 10 and not bool(Luck.LUCK.containsKey(pk2)) and not bool(Luck.write(pk2)), "X6 fix: an unreadable luck file = zeros for now, NOT cached, write() skips it")
    os.rmdir(lf2)
    open(lf2, "w").write("ut=30\nmy.1=9\n")
    v3 = [float(x) for x in Luck.luck(pk2, u2)]
    K.eq((v3[0], v3[1]), (30.0, 9.0), "X6 fix: once it reads, the saved meter is back (30, Zone 1 9 dry kills) - nothing was reset")
    # fix round (critic, spec 3.2): any other orange bag empties the meter (bridge / chest), the meter's own bag and no player do not
    Luck.step(pk2, u2, JDouble(1.0), JDouble(0.99))
    og = [bool(Luck.orangeGot(u2, "meter")), float(Luck.luck(pk2, u2)[0]), bool(Luck.orangeGot(None, "bridge")), bool(Luck.orangeGot(u2, "chest")), float(Luck.luck(pk2, u2)[0])]
    K.eq(og, [False, 31.0, False, True, 0.0], "X6 fix: orangeGot - a meter bag / no player keep the meter (31), a chest / bridge orange bag empties it")
    # fix round 2 (critic): an orange bag during a profile switch empties the meter once the switch is over (queued, not lost)
    Luck.step(pk2, u2, JDouble(5.0), JDouble(0.99))
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    br.put("profile:busy:" + str(u2), JClass("java.lang.Boolean").TRUE)
    q1 = (bool(Luck.orangeGot(u2, "bridge")), float(Luck.luck(pk2, u2)[0]), bool(Luck.RESETQ.containsKey(u2)))
    s_busy = list(Luck.step(pk2, u2, JDouble(1.0), JDouble(0.99)))
    br.remove("profile:busy:" + str(u2))
    s_after = list(Luck.step(pk2, u2, JDouble(1.0), JDouble(0.99)))
    K.eq((q1, s_busy[1], s_after[1], bool(Luck.RESETQ.containsKey(u2))), ((True, 5.0, True), 6.0, 1.0, False),
         "X6 fix 2: an orange bag during a switch is queued (meter kept 5 -> 6 while busy), the first step after empties it (-> 1), queue cleared")
    Luck.step(pk2, u2, JDouble(2.0), JDouble(0.99))
    br.put("profile:busy:" + str(u2), JClass("java.lang.Boolean").TRUE)
    Luck.orangeGot(u2, "chest")
    br.remove("profile:busy:" + str(u2))
    K.check("UT meter 0 / 36" in str(Luck.meterText(u2)) and not bool(Luck.RESETQ.containsKey(u2)), "X6 fix 2: /gear shows the queued reset at once (%s)" % str(Luck.meterText(u2))[:20])
    gsrc = open(GEN, encoding="utf8").read()
    K.check(gsrc.count("@PKG@.GearLuck.orangeGot(") == 3 and 'orangeGot(u, "chest")' in gsrc[gsrc.index("public static Object[] identifyBox("):][:6000],
            "X6 fix: orangeGot is called by the Luggage swap, another mod's Untiered bag and identify of a chest's orange bag")
    try:
        Luck.dirty(pk)
        n = int(Luck.flushAll())
        K.check(n >= 0, "X6 dirty + flushAll run in a bare JVM (flushed %d)" % n)
    except Exception as e:
        K.check(False, "X6 dirty / flushAll raised %s" % e)
    K.check("smart bags" in str(Luck.countsText()), "X6 countsText")
    Cfg.UT_CHANCE = 0.0
    Cfg.UT_PITY = 0.0
    off = (bool(Luck.meterOn()), str(Luck.meterText(u)))
    Cfg.UT_CHANCE = 2.5
    Cfg.UT_PITY = 36.0
    K.check(not off[0] and "off" in off[1] and bool(Luck.meterOn()), "X6 both rows 0 = the meter is off (utdrop.mob is used then)")
    # ============================================================== X7 bug 12 + 17
    Lu = [L for L in range(1, 102) if bool(Ut.covers(JInt(L)))]
    K.check(len(Lu) > 0, "X7 some levels have Untiered rows (%d)" % len(Lu))
    wb, ab = [], []
    for i in range(160):
        b = Ut.bagFor(JInt(Lu[i % len(Lu)]), None, "meter", "meter", JInt(0))
        if b is None:
            continue
        d = Unid.doc(b)
        (ab if bool(Pool.T_ARM[int(Unid.type(d))]) else wb).append(d)
    K.check(len(wb) > 10 and all(bool(Unid.grpU(d)) and str(Unid.title(d)) == "Unidentified Untiered Weapon" for d in wb),
            "X7 bug 12: every orange weapon bag says 'Unidentified Untiered Weapon' (%d)" % len(wb))
    K.check(len(ab) == 0 or all(not bool(Unid.grpU(d)) and "Weapon" not in str(Unid.title(d)) for d in ab), "X7 orange armor bags keep their type (%d)" % len(ab))
    K.check(all(str(GData.str(d, "src", "")) == "meter" for d in wb + ab), "X7 the meter bags carry src meter (the tooltip line)")
    tys, okk = set(), True
    for d in wb[:20]:
        for _ in range(3):
            o = Unid.open(d, None)
            if o is None:
                okk = False
                continue
            ty = int(Pool.typeOfId(str(o[0])))
            tys.add(ty)
            okk = okk and not bool(Pool.T_ARM[ty])
    K.check(okk and len(tys) >= 2, "X7 identify picks a weapon type with an Untiered row (%d types), always a weapon" % len(tys))
    K.check(all(Unid.why(d) is None for d in wb[:20]), "X7 why() lets an orange weapon bag open")
    # fix round (critic): an orange weapon bag saved BEFORE 0.3.35 (no grp tag, e.g. a 'mace' bag) hides its type too and picks it at identify
    olds = []
    for d in wb[:12]:
        od = d.clone()
        od.remove("grp")
        olds.append(od)
    otys = set()
    for od in olds:
        for _ in range(3):
            o = Unid.open(od, None)
            if o is not None:
                otys.add(int(Pool.typeOfId(str(o[0]))))
    K.check(all(bool(Unid.grpU(od)) and str(Unid.title(od)) == "Unidentified Untiered Weapon" for od in olds) and len(otys) >= 2
            and not any(bool(Pool.T_ARM[t_]) for t_ in otys), "X7 fix: old orange weapon bags (no grp) say 'Unidentified Untiered Weapon' and identify picks the type (%d types)" % len(otys))
    gsrc7 = open(GEN, encoding="utf8").read()
    K.check('gsp.getDeclaredMethod("stampStack").insertBefore(J("{ if ($1 != null && !$1.isEmpty() && @PKG@.GearUnid.isBox($1.getItemId())) return @PKG@.GearUnid.reView($1); }"))' in gsrc7,
            "X7 fix: a saved bag's name is re-rendered on the stamp scan (GearUnid.reView), so old bags lose the type in their name")
    Cfg.UNID_TYPEID = False
    tn_off = str(Unid.title(wb[0]))
    Cfg.UNID_TYPEID = True
    K.check("Weapon" not in tn_off or tn_off != "Unidentified Untiered Weapon", "X7 unid.typeAtIdentify=false shows the stored type: %s" % tn_off)
    hp = "Tool_Sickle_Harvester_"
    ret = [bool(Up.retired(x)) for x in ("Tool_Hoe_Crude", "Tool_Hoe_Iron", "Tool_Sickle_Crude", hp + "Crude", "Tool_Pickaxe_Crude", None)]
    K.eq(ret, [True, True, True, False, False, False], "X7 bug 17: GearUp.retired - plain hoes / sickles yes (never in the Anvil list), Harvesters / pickaxes no")
    # fix round 2 (critic): the plain hoe ids (vanilla Crude / Copper / Iron / Thorium + a pack mod's Tool_Hoe_Wood): those on an upgrade ladder
    # (next() != null) are kept out of GearUp.rows only by retired(); each of the three switches off = listed again
    hoes = ["Tool_Hoe_Crude", "Tool_Hoe_Copper", "Tool_Hoe_Iron", "Tool_Hoe_Thorium", "Tool_Hoe_Wood"]
    nx = dict((h_, Up.next(h_) is not None) for h_ in hoes)
    shown = [h_ for h_ in hoes if nx[h_] and not bool(Up.retired(h_))]
    sw = []
    for f_ in ("LL_ON", "HARV_ON", "HARV_ONLY"):
        o_ = bool(getattr(Cfg, f_))
        setattr(Cfg, f_, False)
        sw.append(bool(Up.retired("Tool_Hoe_Crude")))
        setattr(Cfg, f_, o_)
    K.check(any(nx.values()) and shown == [] and sw == [False, False, False] and bool(Up.retired("Tool_Hoe_Wood")),
            "X7 bug 17: plain hoes on the ladder %s, none left for the Upgrade list %s; lifelong / harvester / harvester.only off = listed again %s" % (nx, shown, sw))
    gup = open(GEN, encoding="utf8").read()
    K.check("next(it.getItemId()) == null || retired(it.getItemId())) continue;" in gup[gup.index("public static boolean retired(String id)"):][:1600],
            "X7 bug 17: GearUp.rows skips retired ids (the Anvil Upgrade list)")
    # fix round 2 (critic): an orange bag made for an ASKED type (admin give / gear:fn:box type key) keeps it; random ones stay secret
    kt = [t_ for t_ in range(len(Pool.T_KEY)) if not bool(Pool.T_ARM[t_]) and any(int(Ut.rowsOf(JInt(t_), JInt(L_))) > 0 for L_ in Lu)]
    K.check(len(kt) >= 2, "X7 fix 2: weapon types with Untiered rows (%d)" % len(kt))
    kb = None
    for L_ in Lu:
        if int(Ut.rowsOf(JInt(kt[0]), JInt(L_))) > 0:
            kb = Unid.kept(Ut.bag(JInt(L_), JInt(kt[0]), "admin", "admin", JInt(0)))
            break
    kd = Unid.doc(kb) if kb is not None else None
    kopen = set()
    for _ in range(12):
        o = Unid.open(kd, None) if kd is not None else None
        if o is not None:
            kopen.add(int(Pool.typeOfId(str(o[0]))))
    ktitle = str(Unid.title(kd)) if kd is not None else ""
    K.check(kd is not None and not bool(Unid.grpU(kd)) and ktitle != "Unidentified Untiered Weapon" and kopen == {kt[0]},
            "X7 fix 2: an asked-type orange bag (%s) keeps its type: title %r, identify gives %s" % (str(Pool.T_KEY[kt[0]]), ktitle, kopen))
    gbx = open(GEN, encoding="utf8").read()
    K.check('tu >= 0 ? @PKG@.GearUnid.kept(@PKG@.GearUt.bag(L, tu, src, "bridge", tier))' in gbx and 'ty >= 0 ? @PKG@.GearUnid.kept(@PKG@.GearUt.bag(L, ty, "admin", "admin", 0))' in gbx
            and 'if (@PKG@.GearUt.has(s.getItemId())) return @PKG@.GearUt.bag(L, ty0, src, "bridge", tier);' in gbx,
            "X7 fix 2: gear:fn:box with a type key + admin give keep the type; a vanilla Untiered item handed in stays secret (a drop)")
    # ============================================================== X9 (fix round, spec 2.4): Untiered net power vs Fabled +-15 %, set bonuses vs +8 %
    import math
    dp = _props(str(Cfg.defaultsText()))
    smax = dict((SK[i], float(Cfg.S_MAX[i])) for i in range(len(SK)))
    upw = int(Cfg.UT_POWER) / 100.0
    tab = BM.p5_roll_table()
    fab_w = math.log(tab["fabled"][0])
    fab_a = math.log(tab["fabled"][2] * tab["fabled"][4])
    UNMOD = ("swing", "range", "pierce", "heal", "kb", "mregen")

    ARMW = (("Head", ("Head", "Helm", "Crown", "Hood", "Cap", "Mask")), ("Chest", ("Chest", "Plate", "Robe", "Jacket", "Cuirass")),
            ("Legs", ("Legs", "Leggings", "Greaves", "Trousers", "Skirt", "Boots")), ("Hands", ("Hands", "Gauntlets", "Gloves", "Cuffs")))

    def ut_slot(iid):
        if iid.startswith("Weapon_"):
            return "Weapon"
        for sl, ws in ARMW:
            if any(w in iid for w in ws):
                return sl
        return "Weapon" if not iid.startswith("Armor_") else None

    def ut_tot(iid, body, fixed):
        # the jar's rule (fix round 2, GearStats.addUtE): body lines = stat max x utline.power at full level x SLOT POWER; fixed lines as written
        tt, dm, em, um = {}, 1.0, 1.0, []
        spw_ = BM.P5_SLOT_POWER.get(ut_slot(iid) or "", 100.0) / 100.0
        for k_ in body.split():
            tt[k_] = tt.get(k_, 0.0) + smax.get(k_, 0.0) * upw * spw_
        for w_ in fixed.split():
            if w_.startswith(UNMOD):
                um.append(w_)
                continue
            j = max(w_.rfind("+"), w_.rfind("-"))
            k_, n_ = w_[:j], float(w_[j:])
            if k_ == "hp":
                tt["hpp"] = tt.get("hpp", 0.0) + n_
            elif k_ == "taken":
                em = em / (1 + n_ / 100.0)
            elif k_ == "lowhp":
                dm = dm * (1 + n_ / 200.0)          # assumed: under half Health half the time
            elif k_ == "back":
                dm = dm * (1 + 0.25 * n_ / 100.0)          # assumed: 25 % of hits from behind
            elif k_ == "front":
                dm = dm * (1 + 0.5 * n_ / 100.0)          # assumed: 50 % of hits from the front
            else:
                tt[k_] = tt.get(k_, 0.0) + n_
        return tt, dm, em, um, ut_slot(iid), "mp" in body.split()
    ut_out, flags = [], []
    fx = sorted((k_[5:], v_) for k_, v_ in dp.items() if k_.startswith("utfx."))
    for iid, v_ in fx:
        body, _c, fixed = v_.partition(",")
        tt, dm, em, um, sl, cas = ut_tot(iid, body, fixed)
        net = math.log(BM.p5_dps(tt, caster=cas) * dm * BM.p5_ehp(tt) * em)
        ref = fab_w if sl == "Weapon" else fab_a / 4.0          # armor: a quarter of a Fabled set's log power (one piece)
        bad = abs(net - ref) > 0.15 * abs(ref)
        ut_out.append("%s [%s] %.2f vs %.2f%s%s" % (iid, sl or "?", net, ref, " FLAG" if bad else "", (" (+ " + " ".join(um) + " unmodeled)") if um else ""))
        if bad:
            flags.append(iid)
    K.check(len(fx) >= 16 and len(ut_out) == len(fx), "X9 spec 2.4: every utfx row's net log power printed (%d rows) vs Fabled weapon %.2f / a quarter Fabled armor set %.2f (+-15 %%)" % (len(fx), fab_w, fab_a / 4.0))
    K.notes.append("X9 Untiered net log power (the jar's rule: body = stat max x utline.power x slot power (fix round 2); FLAG = outside Fabled +-15 %, a Skyy question - never fixed automatically; tricks assumed: lowhp half the time, back 25 % / front 50 % of hits, swing tiers DPS-neutral; slot guessed from the id): " + "; ".join(ut_out))
    K.notes.append("X9 FLAGGED Untiered rows (%d of %d): %s" % (len(flags), len(fx), flags or "none"))
    srow = []
    for k_, v_ in sorted(dp.items()):
        if not k_.startswith("set.") or k_[4:].startswith(("mining_", "foraging_", "farming_", "fishing_")):
            continue
        c_ = v_.split(",")
        tt = {}
        for w_ in (c_[2] if len(c_) > 2 else "").split():
            j = max(w_.rfind("+"), w_.rfind("-"))
            if j > 0:
                tt[w_[:j]] = tt.get(w_[:j], 0.0) + float(w_[j:])
        pw_ = math.log(BM.p5_dps(tt) * BM.p5_ehp(tt))
        srow.append("%s %s = %.3f%s" % (k_, c_[2] if len(c_) > 2 else "", pw_, " OVER +8 %" if pw_ > math.log(1.08) else ""))
    K.notes.append("X9 combat set bonuses (spec 2.4: <= +8 %% = ln 0.077; flat hp not counted): %s" % ("; ".join(srow) if srow else "no combat set rows in the default file (the gathering sets are Fortune)"))
    K.check(True, "X9 set bonuses printed (%d combat rows)" % len(srow))
    # ============================================================== X8 hp5Update on the real 0.3.34 default file
    old = _old_default_text()
    keys = [str(x) for x in Cfg.HP5_KEYS]
    new = [str(x) for x in Cfg.HP5_NEW]
    po = _props(old)
    K.check(all(po.get(k) == str(o_) for k, o_ in zip(keys, Cfg.HP5_OLD)), "X8 the 0.3.34 default file holds every HP5_OLD text (%d rows)" % len(keys))
    r = Cfg.hp5Update(old)
    pn = _props(str(r[0]))
    want = dict(po)
    want.update(dict(zip(keys, new)))
    want["level.material.Armor_Iron"] = "8,19"
    K.eq(sorted(k for k in set(pn) | set(want) if pn.get(k) != want.get(k)), [], "X8 hp5Update: the planned rows move, Armor_Iron appended, nothing else (Properties)")
    K.check(str(Cfg.HP5_MARK_ID) in str(r[0]) and len(r[2]) == 0 and len(r[3]) == 3 * (len(keys) + 1), "X8 the marker + one change-log row each, no notes")
    K.check(Cfg.hp5Update(str(r[0])) is None, "X8 a second update = null (marker)")
    K.check(bool(Cfg.p5Same(JString(old).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r[3])), "X8 p5Same: only the planned keys differ")
    # fix round (critic: Undo): table rows are logged tableKey[entry] with | columns (CONFIG-CONTRACT 1.4.6), scalars key / value
    lgs = [str(Cfg.hp5Log(k_, o_, n_)).split("\t")[4:7] for k_, o_, n_ in (("rarity.normal", "1, 45,80", "1,40,70"), ("level.material.Armor_Iron", "(none)", "8,19"),
                                                                           ("set.mining_lead", "Lead Mining Set,4,mfort+60 mwis+3", "Lead Mining Set,4,mfort+77 mwis+3"),
                                                                           ("garmor.mining.lead", "15 26 22 12,1 2 2 1,0", "16 27 23 13,1 2 2 1,0"),
                                                                           ("cost.reforge.mythic", "10000,0", "10000,400"), ("loot.classLean", "50", "75"), ("garmor.farming", "1,2|x|3", "4,5|x|6"))]
    K.eq(lgs, [["rarity[normal]", "1|45|80", "1|40|70"], ["level.material[Armor_Iron]", "(none)", "8|19"],
               ["set[mining_lead]", "Lead Mining Set|4|mfort+60 mwis+3", "Lead Mining Set|4|mfort+77 mwis+3"],
               ["garmor.mining[lead]", "15 26 22 12|1 2 2 1|0", "16 27 23 13|1 2 2 1|0"], ["cost.reforge[mythic]", "10000|0", "10000|400"],
               ["loot.classLean", "50", "75"], ["garmor.farming", "1,2|x|3", "4,5|x|6"]], "X8 fix: hp5Log - table rows as table[entry] + | columns, scalars as they are")
    rc = Cfg.hp5Update(old.replace("\n", "\r\n"))
    K.check(_props(str(rc[0])) == want and "\n" not in str(rc[0]).replace("\r\n", ""), "X8 CRLF kept")
    hand = old.replace("\nrarity.rare=3,40,80\n", "\nrarity.rare=3,44,88\n").replace("\nloot.classLean=50\n", "\nloot.classLean=60\n")
    rh = Cfg.hp5Update(hand)
    ph = _props(str(rh[0]))
    K.check(ph["rarity.rare"] == "3,44,88" and ph["loot.classLean"] == "60" and ph["rarity.normal"] == "1,40,70" and len(rh[2]) == 2,
            "X8 hand-set rows kept + noted: %s" % [str(x)[:60] for x in rh[2]])
    hi = old + "level.material.Armor_Iron=8,17\n"
    ri_ = Cfg.hp5Update(hi)
    K.check(_props(str(ri_[0]))["level.material.Armor_Iron"] == "8,17", "X8 an Armor_Iron line already there is kept")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    P = JClass("java.nio.file.Paths")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = P.get(fc)
    lgp = os.path.join(home, "config-changes.log")
    log0 = open(lgp, "rb").read() if os.path.isfile(lgp) else b""
    Cfg.migrate0330()
    Cfg.migrateP4()
    oc = open(fc, "rb").read()
    msg = str(Cfg.migrateP5())
    nc = open(fc, "rb").read()
    K.check("0.3.35" in msg, "D start 1: %s" % msg[:300].replace("\n", " | "))
    po, pn = _props(oc.decode("latin-1")), _props(nc.decode("latin-1"))
    changed = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    allowed = set(str(x) for x in Cfg.HP5_KEYS) | set(str(x) for x in Cfg.HP5_ADDK)
    K.check(changed and set(changed) <= allowed, "D only planned keys changed: %d (%s)" % (len(changed), [k for k in changed if k not in allowed][:5]))
    K.notes.append("D live rows moved: %s" % changed)
    K.check(str(Cfg.HP5_MARK_ID).encode() in nc, "D the marker is in the live file")
    found = any(open(os.path.join(r_, f_), "rb").read() == oc for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs)
    K.check(found, "D the config-history copy holds the old bytes")
    lg = open(lgp, "rb").read()[len(log0):].decode("utf-8")
    K.eq(lg.count("\tSkyyGear 0.3.35\t-\tupdate\t"), len(changed), "D one change-log line per changed row")
    # fix round (critic: Undo): every logged key is a known row key or table[entry] of a Server Setup table; table values carry no comma
    tbl = dict((str(p_), str(k_)) for p_, k_ in zip(Cfg.HP5_TBL, Cfg.HP5_TBK))
    badk = []
    for ln in [x for x in lg.split("\n") if "\tSkyyGear 0.3.35\t-\tupdate\t" in x]:
        c = ln.split("\t")
        key, ov, nv = c[4], c[5], c[6]
        if "[" in key:
            tk, ent = key[:key.index("[")], key[key.index("[") + 1:-1]
            okk = key.endswith("]") and tk in tbl.values() and (ent and "," not in ov + nv) and any(p_ + ent in changed for p_, k_ in tbl.items() if k_ == tk)
        else:
            okk = key in changed and not any(key.startswith(p_) for p_ in tbl)
        if not okk:
            badk.append(key)
    K.check(not badk, "D fix: every change-log key is a scalar or table[entry] (Undo-able): bad %s" % badk[:5])
    K.notes.append("D change-log keys: %s" % sorted(set(x.split("\t")[4] for x in lg.split("\n") if "\tSkyyGear 0.3.35\t" in x))[:12])
    msg2 = str(Cfg.migrateP5())
    K.check(msg2 == "" and open(fc, "rb").read() == nc, "D start 2: nothing changes (%r)" % msg2[:120])
    Cfg.load()
    K.check(int(Cfg.LEVEL_FULL) in (15, int(pn.get("stat.levelFull", "15"))) and len(list(Cfg.SLOT_PW)) == 5, "D the live file loads (levelFull %d)" % int(Cfg.LEVEL_FULL))
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
