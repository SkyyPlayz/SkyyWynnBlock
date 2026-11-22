"""Harness for SkyyGear 0.3.58 (round shield1: SHIELDS = Warrior off-hand gear - tools/gear_0_3_58_patch.py header).
Build first (the build needs Quirk's private art; in a worktree: SKYWYNN_PRIVATE_ART=<path to SkyWynn-PRIVATE-art>):
    python tools/gear_0_3_58_patch.py && python SkyyGear/build_skyygear_0.3.58.py
    python SkyyGear/test_skyygear_0.3.58.py [--keep] [--expect-dump]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.57 jar is the compare base):
  S  static    the patch re-runs to identical bytes, ONE new class (GearOff), no command / system; GearHandSys feeds GearOff, totals0 reads it, GearSnap keys
               on it, the chat forget drops it; the three rows in CFG_ROWS + the fresh text
  A  verify    every class loads + initialises with -Xverify:all
  C  compare   0.3.57 -> 0.3.58 (EXPECT below)
  E  engine    the 0.2.11 harness's bare server boot (vanilla pack + THIS jar) - every new path EXECUTED:
               C  the fresh config (shield.gear=true, shield.def=6, shield.power=19.5); the loader: absent = the defaults, clamped
               G  isGear / slotOf: the 16 vanilla shields + SkyyArmory's 8 + a pack recolour = gear, slot 5; GreatShield stays a weapon; shield.gear off = not gear
               B  the level bands of every vanilla shield (material rows, Doomed / Praetorian, Hytale's ItemLevel for Rusty / Orbis Knight)
               R  rolls: GearRoll.pool(5) = the armor pool, rollMods / newDoc on REAL shields only roll armor stats (300 rolls), never Damage %
               T  the tooltip of REAL documents: tier line, Class / Off-hand Shield / RARE SHIELD header, base Defense, the vanilla guard, the off-hand hint,
                  unidentified text, describe(), slot power x shield.power
               O  totals: GearOff (seen / get / forget) + GearStats.totals0 / totals (the snapshot) - an ACTIVE off-hand shield adds base Defense + its lines
                  x shield.power, an unidentified one / a main-hand one / shield.gear off nothing; a new off-hand stack invalidates the snapshot
               H  the REAL GearHandSys.tick on a fake chunk + command buffer with a REAL Utility component: the off-hand stack lands in GearOff
               P  bags: the Weapon_Shield type ("Shield"), candidates at Zone 1-5 levels, pickZ opens shield bags into shields (armor rolls), Unid.roll with the
                  type forced, fromItem (a vanilla shield drop -> a shield bag), the Warrior class lean (leanHit / pickType)
               M  Smithing: cat 2 (Weapons), combatId / combatGear, the Armor Bench refusal text (benchWhy), the Shields card on the REAL recipe store
               F  first sight: GearStamp.stampStack on a bare shield = a Normal document at its band, GearOff.N[0] + gear.log SHIELD-FIRST; again = no change
  E57 / E56 / E55 / E54  the 0.3.57, 0.3.56, 0.3.55 and 0.3.54 harnesses' engine phases against THIS jar (every 0.3.5x check still passes)
  D  live      start twice on a scratch COPY of Skyy's live Skyy_SkyyGear: no one-time update of this round, the second start changes nothing, the shield.*
               rows not written (new keys) and read as their defaults
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client drawing the tooltip; a real block with a shield (the vanilla guard is untouched); the Smithing page craft click
(GearSmith commit is unchanged code - combatId already covered metal shields); a real mob drop of a shield bag (GearLoot's roll is unchanged code).
Scratch: tools/dev/scratch/shield1/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.58"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shield1", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.57.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_58_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.57.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
T57 = {"__file__": os.path.join(HERE, "test_skyygear_0.3.57.py"), "__name__": "t57"}
_s = open(T57["__file__"], encoding="utf8").read()
exec(compile(_s[:_s.rindex(chr(10) + 'HK.run_compare = T54["run_compare54"]')], T57["__file__"], "exec"), T57)
T56 = T57["T56"]
T55 = T57["T55"]
T54 = T57["T54"]
for _t in (T54, T55, T56, T57):
    _t["SCRATCH"] = SCRATCH
ADDED = ["GearOff"]
EXPECT = None if "--expect-dump" in sys.argv else {          # the first run's dump, reviewed: the 3 rows (Cfg*, GearCfg), shieldId / isGearMs / slotOf 5 / the
    # SkyyRolls migration (GearData), I_DEF (GearDefs), shieldDef + describe (GearBase), the armor pool for slot 5 (GearRoll, GearChg.canRoll), GearOff.forget
    # (GearCharged.forget), the Utility read (GearHandSys), the snapshot key (GearSnap), totals0, the tooltip (GearView, IdentifyPage, ReforgePage),
    # Smithing / bench (GearSmith.cat, GearPack.combatGear + its LOOT_IDS table), the bag pool tables (GearPool / GearPackId / GearUt initialisers),
    # the first-sight journal (GearStamp), the plugin's setup (the row table)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'GearBase': ['+m shieldDef', '~m describe'],
    'GearCfg': ['+f SHIELD_ON', '+f SH_DEF', '+f SH_PW', '~<clinit>', '~m apply', '~m defaultsText'],
    'GearCharged': ['~m forget'],
    'GearChg': ['~m canRoll'],
    'GearData': ['+m shieldId', '~m isGearMs', '~m migrate', '~m migrateRarity', '~m slotOf'],
    'GearDefs': ['+f I_DEF'],
    'GearHandSys': ['~m tick'],
    'GearPack': ['~<clinit>', '~m combatGear'],
    'GearPackId': ['~<clinit>'],
    'GearPool': ['~<clinit>', '~m candM', '~m idIdx', '~m levelsM', '~m liveType', '~m matchM', '~m packText', '~m pickItemM', '~m table', '~m typeOfId', '~m w'],
    'GearRoll': ['~m allowed', '~m pool', '~m rollMods'],
    'GearSmith': ['~m cat'],
    'GearSnap': ['~m make', '~m valid'],
    'GearStamp': ['~m stampStack'],
    'GearStats': ['~m totals0'],
    'GearUt': ['~<clinit>'],
    'GearView': ['+f SG_ID', '+f SG_V', '+m guardText', '+m shieldRows', '~<clinit>', '~m baseRows', '~m lines', '~m slotPw', '~m slotWord', '~m topTag'],
    'IdentifyPage': ['~m detail'],
    'ReforgePage': ['~m anLines'],
    'SkyyGearPlugin': ['~m setup'],
}
LIVE_DIR = T54["LIVE_DIR"]
U = "00000000-0000-0000-0000-000000000358"
VAN = ["Weapon_Shield_" + _w for _w in ("Adamantite", "Cobalt", "Copper", "Doomed", "Iron", "Mithril", "Onyxium", "Orbis_Incandescent", "Orbis_Knight",
                                       "Praetorian", "Ruined_Giant", "Rusty", "Scrap", "Scrap_Spiked", "Thorium", "Wood")]
ARM = ["Weapon_Shield_%s_SkyWynn" % _m for _m in ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")]
BANDS = {"Wood": (1, 8), "Copper": (1, 8), "Iron": (8, 15), "Thorium": (20, 28), "Cobalt": (40, 48), "Adamantite": (60, 68), "Mithril": (80, 88),
         "Onyxium": (100, 100), "Doomed": (40, 47), "Praetorian": (40, 47), "Rusty": (15, 15), "Orbis_Knight": (40, 40)}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.58 - build script') and g.count('VERSION = "0.3.58"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')), (0, 0, 1),
         "S one new class (GearOff), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    e_ = g.index("@PKG@.GearOff.seen(pr.getUuid(), shu == null ? null : shu.getActiveItem());")
    tk = g[g.rindex("public void tick(", 0, e_):e_]
    K.check("@PKG@.GearHand.seen(pr.getUuid(), held);" in tk and "@UTIL@ shu = (@UTIL@) cb.getComponent(r, @UTIL@.getComponentType());" in tk,
            "S GearHandSys.tick feeds GearOff from the Utility component (right after GearHand.seen)")
    t0 = g[g.index("public static int[] totals0("):g.index("public static int[] totals(java.util.UUID u")]
    K.check("@PKG@.GearOff.get(u)" in t0 and "@PKG@.GearBase.shieldDef(shid, shd)" in t0 and "if (active(u, shid, shd) && @PKG@.GearOff.classOk(u, shid))" in t0 and "addModsE(acc, shid, shd, true);" in t0,
            "S totals0 adds an ACTIVE off-hand shield the class may use (armor-filtered lines + base Defense)")
    K.check("if (e[18] != (Object) @PKG@.GearOff.get(u)) return false;" in g and "e[18] = @PKG@.GearOff.get(u);" in g, "S GearSnap keys on the off-hand stack")
    K.check("@PKG@.GearOff.forget(u);          // 0.3.58" in g, "S GearChg.forget (the disconnect cleanup) drops the off-hand entry")
    for k_ in ('("shield.gear", "Shields are gear", "combat", "bool", "true"', '("shield.def", "Shield base Defense", "combat", "int", "6", "0", "100"',
               '("shield.power", "Shield slot power", "combat", "dec", "19.5", "0", "200"'):
        K.check(k_ in g, "S the row %s" % k_[:30])
    K.check("SH58_ROWS + [" in g and "set(SH58_KEYS)" in g and "for k in SH58_KEYS:" in g, "S the rows are in CFG_ROWS, the danger set and the fresh text")
    K.save()


# ====================================================================================================== E: engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JObject, JArray, JLong, JDouble, JBoolean, JFloat, JShort, JByte
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng58")
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
    us = E["us"]
    P = lambda n: JClass(PKG + n)
    Cfg, Data, Roll, View, Defs, Pool, Unid, Pack, Stats, Off, Snap, Base, Lvl, Smith, Stamp = (
        P("GearCfg"), P("GearData"), P("GearRoll"), P("GearView"), P("GearDefs"), P("GearPool"), P("GearUnid"), P("GearPack"), P("GearStats"), P("GearOff"),
        P("GearSnap"), P("GearBase"), P("GearLevel"), P("GearSmith"), P("GearStamp"))
    Props = JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BS = JClass("org.bson.BsonString")
    BB = JClass("org.bson.BsonBoolean")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    AL = JClass("java.util.ArrayList")
    SysJ = JClass("java.lang.System")
    u = UUID.fromString(U)
    sysp = SysJ.getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    data = os.path.join(scratch, "data58")
    os.makedirs(data, exist_ok=True)
    Cfg.DIR = Paths.get(data)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    BASE = {"part__gate": "false"}
    apply(**BASE)

    def fld(cls, name):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)

    RID = [str(x) for x in Defs.R_ID]
    R = dict((n_, RID.index(n_)) for n_ in RID)

    def doc(iid, r, lv=20, src="admin"):
        d_ = Roll.newDoc(JString(iid), JInt(r), True, JString(src), JInt(lv))
        d_.put("r", BS(Defs.R_ID[r]))
        return d_

    def stack(iid, d_):
        return Data.put(IS(JString(iid), JInt(1)), d_, u)

    def mods(d_):
        a_ = Data.mods(d_)
        return [(str(a_.get(i).asDocument().get("s").asString().getValue()), int(a_.get(i).asDocument().get("v").asNumber().intValue())) for i in range(a_.size())]
    S_KEY = [str(x) for x in Defs.S_KEY]
    S_SLOT = [str(x) for x in Defs.S_SLOT]
    I_DEF = S_KEY.index("def")
    K.eq(int(Defs.I_DEF), I_DEF, "E GearDefs.I_DEF = the Defense index")

    # ================================================================================== C the fresh config + the loader
    K.check("\nshield.gear=true\n" in fresh and "\nshield.def=6\n" in fresh and "\nshield.power=19.5\n" in fresh and "# ---- shields = Warrior off-hand gear" in fresh,
            "C the fresh config carries shield.gear=true, shield.def=6, shield.power=19.5 under its own heading")
    K.eq((bool(Cfg.SHIELD_ON), int(Cfg.SH_DEF), float(Cfg.SH_PW)), (True, 6, 19.5), "C the loader reads the fresh defaults")
    pr0 = Props()
    pr0.load(JClass("java.io.StringReader")("\n".join(l for l in fresh.split("\n") if not l.startswith("shield."))))
    Cfg.apply(pr0, False)
    a0 = (bool(Cfg.SHIELD_ON), int(Cfg.SH_DEF), float(Cfg.SH_PW))
    apply(shield__gear="false", shield__def="999", shield__power="-5", **BASE)
    a1 = (bool(Cfg.SHIELD_ON), int(Cfg.SH_DEF), float(Cfg.SH_PW))
    apply(shield__def="-3", shield__power="900", **BASE)
    a2 = (int(Cfg.SH_DEF), float(Cfg.SH_PW))
    apply(**BASE)
    K.eq((a0, a1, a2), ((True, 6, 19.5), (False, 100, 0.0), (0, 200.0)), "C absent = the defaults; false / 999 / -5 / -3 / 900 clamped into 0..100 and 0..200")

    # ================================================================================== G isGear / slotOf
    gb = []
    for iid in VAN + ARM + ["Weapon_Shield_Iron_Red", "Weapon_Shield_Cobalt_Black_Pat"]:
        if not bool(Data.shieldId(JString(iid))) or not bool(Data.isGear(JString(iid))) or int(Data.slotOf(JString(iid))) != 5:
            gb.append((iid, bool(Data.isGear(JString(iid))), int(Data.slotOf(JString(iid)))))
    for iid, want in (("Weapon_GreatShield_Iron", 0), ("Weapon_Sword_Iron", 0), ("Armor_Iron_Chest", 2), ("AntiqueShieldBlue", -1)):
        if int(Data.slotOf(JString(iid))) != want:
            gb.append(("not a shield", iid, int(Data.slotOf(JString(iid))), want))
    if bool(Data.shieldId(None)) or bool(Data.shieldId(JString("Weapon_Shield"))) or bool(Data.shieldId(JString("Weapon_GreatShield_Iron"))):
        gb.append("shieldId: null / Weapon_Shield / Weapon_GreatShield_ are no shield ids")
    if not str(Cfg.EXCLUDE).startswith("Weapon_Shield_"):
        gb.append(("gear.exclude keeps its Weapon_Shield_ entry", str(Cfg.EXCLUDE)[:40]))
    apply(shield__gear="false", **BASE)
    off = [(iid, bool(Data.isGear(JString(iid))), int(Data.slotOf(JString(iid)))) for iid in ("Weapon_Shield_Iron", "Weapon_Shield_Wood", ARM[0])]
    if [x for x in off if x[1] or x[2] != -1]:
        gb.append(("shield.gear off = 0.3.57: no shield is gear", off))
    apply(**BASE)
    K.notes.append("G GearData.isGearMs(Weapon_Shield_Iron, 5 stacks) = %s" % bool(Data.isGearMs(JString("Weapon_Shield_Iron"), JInt(5))))
    if bool(Data.isGearMs(JString("Weapon_Shield_Iron"), JInt(5))) or not bool(Data.isGearMs(JString("Weapon_Shield_Iron"), JInt(1))):
        gb.append("isGearMs: a stacking shield is never gear, a single one is")
    K.check(not gb, "G every vanilla (16) / SkyyArmory (8) / pack-recolour shield is gear in slot 5; GreatShield / sword / armor unchanged; shield.gear off = plain: %s" % gb)

    # ================================================================================== B the level bands
    bd = []
    for iid in VAN:
        w = iid[len("Weapon_Shield_"):]
        if w in BANDS:
            b_ = Lvl.band(JString(iid))
            if (int(b_[0]), int(b_[1])) != BANDS[w]:
                bd.append((iid, int(b_[0]), int(b_[1]), BANDS[w]))
    K.notes.append("B bands: %s" % ", ".join("%s %d-%d" % (i[14:], int(Lvl.band(JString(i))[0]), int(Lvl.band(JString(i))[1])) for i in VAN))
    K.check(not bd, "B the shield bands (Wood / Copper 1-8, Iron 8-15, Thorium 20-28, Cobalt 40-48, Adamantite 60-68, Mithril 80-88, Onyxium 100 (the level cap), "
            "Doomed / Praetorian 40-47, Rusty 15, Orbis Knight 40): %s" % bd)

    # ================================================================================== R rolls = the armor pool
    rb = []
    p5 = sorted(S_KEY[int(i)] for i in Roll.pool(JInt(5), JString("Weapon_Shield_Iron")))
    p2 = sorted(S_KEY[int(i)] for i in Roll.pool(JInt(2), JString("Armor_Leather_Light_Chest")))
    if p5 != p2 or "dmg" in p5 or "def" not in p5 or "hpp" not in p5:
        rb.append(("pool(5) = pool(2) (the armor pool)", p5, p2))
    seen_k = set()
    for n_ in range(300):
        iid = VAN[n_ % len(VAN)]
        ms = mods(doc(iid, R["legendary"], 40))
        for k_, v_ in ms:
            seen_k.add(k_)
            if "a" not in S_SLOT[S_KEY.index(k_)] or v_ <= 0:
                rb.append((iid, k_, v_))
                break
        if not ms:
            rb.append((iid, "a Legendary shield rolled no line"))
    if "dmg" in seen_k or "def" not in seen_k or "hpp" not in seen_k:
        rb.append(("seen", sorted(seen_k)))
    K.notes.append("R rolled keys on 300 Legendary shields: %s" % sorted(seen_k))
    K.check(not rb[:6], "R a shield rolls the ARMOR pool only (pool.armor weights, never Damage %%), 300 REAL documents: %s" % rb[:6])

    # ================================================================================== T the tooltip on REAL documents
    tb = []
    apply(**BASE)
    dI = doc("Weapon_Shield_Iron", R["rare"], 12)
    txt, col = AL(), AL()
    View.lines(JString("Weapon_Shield_Iron"), dI, None, txt, col)
    tl = [str(x).replace(chr(2), "") for x in txt]
    cl = [None if x is None else str(x) for x in col]
    defv = int(Base.shieldDef(JString("Weapon_Shield_Iron"), dI))
    exp = int(round(6 * float(Base.curveR(JInt(12))) * float(Base.bonus(JInt(8)))))
    if defv != exp or defv < 6:
        tb.append(("shieldDef Lv 12 Iron = 6 x R(12) x bonus(8)", defv, exp))
    for want in ("Off-hand Shield", "RARE SHIELD", "Defense +%d" % defv, "Guard: 1 Stamina per 14 damage blocked", "Counts in your off-hand (utility) slot", "STATS"):
        if not [x for x in tl if want in x]:
            tb.append(("missing", want))
    tg = str(View.topTag(JString("Weapon_Shield_Iron"), JInt(5), View.descText(JString("Weapon_Shield_Iron"))))
    if tg != "T2 Iron" or not [x for x in tl if x.startswith("T2 Iron")]:
        tb.append(("the tier line", tg, tl[:3]))
    try:
        di = tl.index("Defense +%d" % defv)
        if cl[di] != str(View.rollCol(JString("def"), JInt(defv), False)):
            tb.append(("the base Defense in the Defense colour", cl[di]))
    except ValueError:
        pass
    if str(View.slotWord(JString("Weapon_Shield_Iron"))) != "SHIELD" or str(View.typeWord(JString("Weapon_Shield_Iron"))) != "SHIELD":
        tb.append(("slotWord / typeWord", str(View.slotWord(JString("Weapon_Shield_Iron"))), str(View.typeWord(JString("Weapon_Shield_Iron")))))
    if abs(float(View.slotPw(JString("Weapon_Shield_Iron"))) - 0.195) > 1e-9:
        tb.append(("slot power = shield.power 19.5 %", float(View.slotPw(JString("Weapon_Shield_Iron")))))
    if View.guardText(JString(ARM[7])) is None or "33.1" not in str(View.guardText(JString(ARM[7]))) or View.guardText(JString("Weapon_Shield_Iron_Red")) is not None:
        tb.append(("guardText: SkyyArmory Lumen 33.1, a pack recolour none", View.guardText(JString(ARM[7]))))
    dU = doc("Weapon_Shield_Iron", R["rare"], 12)
    dU.put("id", BB(False))
    tu, cu = AL(), AL()
    View.lines(JString("Weapon_Shield_Iron"), dU, None, tu, cu)
    if not [x for x in tu if "Gives no stats until identified." in str(x)]:
        tb.append(("an unidentified shield says 'Gives no stats until identified.'", [str(x) for x in tu][:8]))
    ds = str(Base.describe(JString("Weapon_Shield_Iron"), dI))
    if "base stats: shield Lv 12 - Defense %d" % defv not in ds or "off-hand" not in ds:
        tb.append(("describe", ds))
    # the Warrior: SkyyClasses' bridge keys (0.1.53 shape: class:list, class:weapons:<Name> prefix lists, class:<uuid>) -> "Class: Warrior" + the Smithing filter
    cls_keys = {"class:list": "Warrior:Combat,Spellblade:Battlemagic", "class:weapons:Warrior": "Weapon_Sword_,Weapon_Spear_,Weapon_Shield_,Weapon_Longsword_Katana",
                "class:weapons:Spellblade": "Weapon_Longsword_,Weapon_GreatShield_", "class:" + U: "Warrior"}
    for k_, v_ in cls_keys.items():
        br.put(k_, JString(v_))
    tw, cw = AL(), AL()
    View.lines(JString("Weapon_Shield_Iron"), dI, None, tw, cw)
    twl = [str(x).replace(chr(2), "") for x in tw]
    shW = bool(Smith.shows(u, JString("Weapon_Shield_Iron"), False))
    br.put("class:" + U, JString("Spellblade"))
    shS = bool(Smith.shows(u, JString("Weapon_Shield_Iron"), False))
    gsS = bool(Smith.shows(u, JString("Weapon_GreatShield_Iron"), False))
    for k_ in cls_keys:
        br.remove(k_)
    K.notes.append("T with SkyyClasses' keys: %s; Smithing shows the Iron shield to a Warrior %s / a Spellblade %s (great shield %s)" % (twl[:4], shW, shS, gsS))
    if "Class: Warrior" not in twl or not shW or shS or not gsS:
        tb.append(("Class: Warrior + the Smithing class filter", twl[:4], shW, shS, gsS))
    K.notes.append("T tooltip (Rare Iron shield Lv 12): %s" % tl)
    K.notes.append("T describe: %s" % ds)
    K.check(not tb, "T the shield tooltip (tier / Class / Off-hand Shield / RARE SHIELD / base Defense in its colour / guard / hint / unidentified) + describe: %s" % tb)

    # ================================================================================== O totals: GearOff + the snapshot
    ob = []
    Off.CUR.clear()
    armor = SIC(JShort(4))
    t0 = [int(x) for x in Stats.totals0(u, None, armor, None, False)]
    dO = doc("Weapon_Shield_Cobalt", R["rare"], 44)
    dO.put("mods", JClass("org.bson.BsonArray")())
    dO.get("mods").add(Data.mod(JString("def"), JInt(20)))
    dO.get("mods").add(Data.mod(JString("str"), JInt(10)))
    sO = stack("Weapon_Shield_Cobalt", dO)
    Off.seen(u, sO)
    if Off.get(u) is None or SysJ.identityHashCode(Off.get(u)) != SysJ.identityHashCode(sO):
        ob.append("GearOff.seen / get keep the stack")
    t1 = [int(x) for x in Stats.totals0(u, None, armor, None, False)]
    bdef = int(Base.shieldDef(JString("Weapon_Shield_Cobalt"), dO))
    want_def = t0[I_DEF] + bdef + int(round(20 * 0.195))
    want_str = t0[S_KEY.index("str")] + int(round(10 * 0.195))
    if t1[I_DEF] != want_def or t1[S_KEY.index("str")] != want_str:
        ob.append(("an active off-hand shield: base Defense + lines x 19.5 %", t1[I_DEF], want_def, t1[S_KEY.index("str")], want_str, bdef))
    K.notes.append("O Cobalt shield Lv 44: base Defense %d, totals Defense %d -> %d, Strength %d -> %d" % (bdef, t0[I_DEF], t1[I_DEF], t0[S_KEY.index("str")], t1[S_KEY.index("str")]))
    # the snapshot (GearStats.totals): a new off-hand stack = a new entry
    tA = [int(x) for x in Stats.totals(u, None, armor, None, False)]
    e1 = Snap.peek(u)
    dO2 = doc("Weapon_Shield_Cobalt", R["rare"], 44)
    dO2.put("mods", JClass("org.bson.BsonArray")())
    dO2.get("mods").add(Data.mod(JString("def"), JInt(40)))
    sO2 = stack("Weapon_Shield_Cobalt", dO2)
    v_before = bool(Snap.valid(e1, u, JLong(SysJ.currentTimeMillis()))) if e1 is not None else None
    Off.seen(u, sO2)
    v_after = bool(Snap.valid(e1, u, JLong(SysJ.currentTimeMillis()))) if e1 is not None else None
    tB = [int(x) for x in Stats.totals(u, None, armor, None, False)]
    if tA[I_DEF] != t1[I_DEF] or v_before is not True or v_after is not False or tB[I_DEF] != t0[I_DEF] + bdef + int(round(40 * 0.195)):
        ob.append(("the snapshot keys on the off-hand stack", tA[I_DEF], t1[I_DEF], v_before, v_after, tB[I_DEF]))
    # inactive: unidentified -> nothing; held in the MAIN hand -> nothing; shield.gear off -> nothing; an empty off-hand -> forgotten
    dN = doc("Weapon_Shield_Cobalt", R["rare"], 44)
    dN.put("id", BB(False))
    Off.seen(u, stack("Weapon_Shield_Cobalt", dN))
    tN = [int(x) for x in Stats.totals0(u, None, armor, None, False)]
    Off.CUR.clear()
    okm = JArray(JBoolean)(1)
    tM = [int(x) for x in Stats.totals0(u, sO, armor, okm, False)]
    if tN[I_DEF] != t0[I_DEF] or tM[I_DEF] != t0[I_DEF] or bool(okm[0]):
        ob.append(("unidentified off-hand / a main-hand shield count nothing (main hand: offence off)", tN[I_DEF], tM[I_DEF], bool(okm[0])))
    Off.seen(u, sO)
    apply(shield__gear="false", **BASE)
    tX = [int(x) for x in Stats.totals0(u, None, armor, None, False)]
    apply(shield__def="0", **BASE)
    tZ = [int(x) for x in Stats.totals0(u, None, armor, None, False)]
    apply(**BASE)
    if tX[I_DEF] != t0[I_DEF] or tZ[I_DEF] != t0[I_DEF] + int(round(20 * 0.195)):
        ob.append(("shield.gear off = nothing; shield.def 0 = the lines only", tX[I_DEF], tZ[I_DEF]))
    # "shields warrior only": SkyyClasses' class:fn:allowed says no (another class) = nothing; yes = counted; a throwing fn = counted (Gear's level gate)
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Allow(object):
        def __init__(self, ans):
            self.ans = ans
            self.asked = []

        @JOverride
        def apply(self, o):
            self.asked.append((str(o[0]), str(o[1])))
            if self.ans is None:
                raise RuntimeError("boom")
            return JClass("java.lang.Boolean").valueOf(self.ans)
    cl0 = int(Off.N[3])
    res = {}
    for ans in (False, True, None):
        fn_ = Allow(ans)
        br.put("class:fn:allowed", fn_)
        res[ans] = ([int(x) for x in Stats.totals0(u, None, armor, None, False)][I_DEF], fn_.asked[:1])
    br.remove("class:fn:allowed")
    K.notes.append("O class:fn:allowed no / yes / throws -> Defense %s" % dict((str(k), v[0]) for k, v in res.items()))
    if res[False][0] != t0[I_DEF] or res[True][0] != t1[I_DEF] or res[None][0] != t1[I_DEF] or res[True][1] != [(U, "Weapon_Shield_Cobalt")] or int(Off.N[3]) != cl0 + 1:
        ob.append(("class:fn:allowed: another class = nothing, the Warrior = counted, a failing fn = counted", res, int(Off.N[3]) - cl0))
    Off.seen(u, None)
    if Off.get(u) is not None or Off.CUR.containsKey(u):
        ob.append("an empty off-hand = no entry")
    Off.seen(u, sO)
    Off.forget(u)
    if Off.get(u) is not None:
        ob.append("forget drops the entry")
    if Off.get(None) is not None:
        ob.append("get(null) = null")
    Off.seen(None, sO)
    # UNDER-LEVEL = inactive (part.gate on, no skills + level.noSkills=block = the level floor): a Lv 84 Mithril shield counts nothing and its tooltip
    # says so in red; a Lv 1 Wood shield still counts
    apply(part__gate="true", level__noSkills="block")
    dHi = doc("Weapon_Shield_Mithril", R["rare"], 84)
    dLo = doc("Weapon_Shield_Wood", R["rare"], 1)
    aHi, aLo = bool(Stats.active(u, JString("Weapon_Shield_Mithril"), dHi)), bool(Stats.active(u, JString("Weapon_Shield_Wood"), dLo))
    Off.seen(u, stack("Weapon_Shield_Mithril", dHi))
    tHi = [int(x) for x in Stats.totals0(u, None, armor, None, False)]
    Off.seen(u, stack("Weapon_Shield_Wood", dLo))
    tLo = [int(x) for x in Stats.totals0(u, None, armor, None, False)]
    th, ch_ = AL(), AL()
    View.lines(JString("Weapon_Shield_Mithril"), dHi, u, th, ch_)
    thl = [str(x).replace(chr(2), "") for x in th]
    red = [str(ch_.get(i)) for i in range(len(thl)) if thl[i].startswith("Gives no stats until")]
    apply(**BASE)
    K.notes.append("O under-level tooltip head: %s" % thl[:6])
    if aHi or not aLo or tHi[I_DEF] != t0[I_DEF] or tLo[I_DEF] <= t0[I_DEF] or not red or red[0] != str(Defs.C_BAD):
        ob.append(("under-level = inactive (no Defense) + the red line; a Lv 1 shield active", aHi, aLo, tHi[I_DEF], tLo[I_DEF], red))
    Off.seen(u, sO)
    K.notes.append("O status: %s" % str(Off.statusText()))
    K.check(not ob, "O totals: an ACTIVE off-hand shield adds base Defense + lines x shield.power; snapshot keyed; unidentified / main hand / off = nothing: %s" % ob)

    # ================================================================================== H the REAL GearHandSys.tick (fake chunk + command buffer, a REAL Utility)
    hb = []
    try:
        fk = os.path.join(esc, "fake58")
        os.makedirs(fk, exist_ok=True)
        cpz = JClass("javassist.ClassPool")(False)
        cpz.appendSystemPath()
        cpz.appendClassPath(JString(B.SERVER_JAR))
        cpz.appendClassPath(JString(jar))
        CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
        CTn, CMPn, REFn = "com.hypixel.hytale.component.ComponentType", "com.hypixel.hytale.component.Component", "com.hypixel.hytale.component.Ref"
        fc = cpz.makeClass("skyygear58t.FakeChunk58")
        fc.setSuperclass(cpz.get("com.hypixel.hytale.component.ArchetypeChunk"))
        fc.addField(CtF.make("public java.util.Map comps;", fc))
        fc.addField(CtF.make("public %s ref;" % REFn, fc))
        fc.addConstructor(CtC.make("public FakeChunk58() { super(null, null); }", fc))          # never run (Unsafe)
        fc.addMethod(CtM.make("public %s getComponent(int i, %s t) { if (this.comps == null) return null; return (%s) this.comps.get(t); }" % (CMPn, CTn, CMPn), fc))
        fc.addMethod(CtM.make("public %s getReferenceTo(int i) { return this.ref; }" % REFn, fc))
        fc.writeFile(JString(fk))
        fb_ = cpz.makeClass("skyygear58t.FakeBuf58")
        fb_.setSuperclass(cpz.get("com.hypixel.hytale.component.CommandBuffer"))
        fb_.addField(CtF.make("public java.util.Map comps;", fb_))
        fb_.addConstructor(CtC.make("public FakeBuf58() { super(null); }", fb_))          # never run (Unsafe)
        fb_.addMethod(CtM.make("public %s getComponent(%s r, %s t) { if (this.comps == null) return null; return (%s) this.comps.get(t); }" % (CMPn, REFn, CTn, CMPn), fb_))
        fb_.writeFile(JString(fk))
        ldr = JClass("java.net.URLClassLoader")(JArray(JClass("java.net.URL"))([JClass("java.io.File")(JString(fk)).toURI().toURL()]), IS.class_.getClassLoader())
        FCh, FBuf = JClass("skyygear58t.FakeChunk58", loader=ldr), JClass("skyygear58t.FakeBuf58", loader=ldr)
        EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        if EM.get() is None:
            em = us.allocateInstance(EM.class_)
            fld(EM, "instance").set(None, em)
        em = EM.get()
        CT = JClass(CTn)
        kk = EM.class_
        while kk is not None and str(kk.getName()) != "java.lang.Object":
            for f_ in kk.getDeclaredFields():
                if f_.getType() == CT.class_ and not JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                    f_.setAccessible(True)
                    if f_.get(em) is None:
                        f_.set(em, us.allocateInstance(CT.class_))
            kk = kk.getSuperclass()
        UTIL = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility")
        uc = SIC(JShort(4))
        ut = UTIL(uc, JByte(0))
        uc.setItemStackForSlot(JShort(0), sO)
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        prf = us.allocateInstance(PRc.class_)
        fld(PRc, "uuid").set(prf, u)
        ref = us.allocateInstance(JClass(REFn).class_)
        ch = us.allocateInstance(FCh.class_)
        m1 = JClass("java.util.IdentityHashMap")()
        m1.put(PRc.getComponentType(), prf)
        fld(FCh, "comps").set(ch, m1)
        fld(FCh, "ref").set(ch, ref)
        cb = us.allocateInstance(FBuf.class_)
        m2 = JClass("java.util.IdentityHashMap")()
        m2.put(UTIL.getComponentType(), ut)
        fld(FBuf, "comps").set(cb, m2)
        Off.CUR.clear()
        n0 = int(Off.N[1])
        if ut.getActiveItem() is None or SysJ.identityHashCode(ut.getActiveItem()) != SysJ.identityHashCode(sO):
            hb.append(("the REAL Utility component's active item = slot 0", ut.getActiveItem()))
        P("GearHandSys")().tick(JFloat(0.05), JInt(0), ch, None, cb)
        g1 = Off.get(u)
        if g1 is None or SysJ.identityHashCode(g1) != SysJ.identityHashCode(sO) or int(Off.N[1]) != n0 + 1:
            hb.append(("tick 1: the off-hand stack lands in GearOff", g1, int(Off.N[1]) - n0))
        P("GearHandSys")().tick(JFloat(0.05), JInt(0), ch, None, cb)
        if int(Off.N[1]) != n0 + 1:
            hb.append("tick 2 (nothing changed): no new entry")
        uc.setItemStackForSlot(JShort(0), None)
        P("GearHandSys")().tick(JFloat(0.05), JInt(0), ch, None, cb)
        if Off.get(u) is not None or int(Off.N[1]) != n0 + 2:
            hb.append(("tick 3 (off-hand emptied): the entry goes", Off.get(u)))
        m2.clear()
        uc.setItemStackForSlot(JShort(0), sO)
        P("GearHandSys")().tick(JFloat(0.05), JInt(0), ch, None, cb)
        if Off.get(u) is not None:
            hb.append("no Utility component = no entry")
    except Exception as ex_:
        hb.append(("the GearHandSys.tick rig", str(ex_)[:400]))
    K.check(not hb, "H the REAL GearHandSys.tick reads the REAL Utility component into GearOff (set, unchanged, emptied, no component): %s" % hb)
    Off.CUR.clear()

    # ================================================================================== P the bags
    pb = []
    ty = int(Pool.typeIdx(JString("Weapon_Shield")))
    if ty < 0 or str(Pool.T_NAME[ty]) != "Shield" or bool(Pool.T_ARM[ty]) or int(Pool.typeOfId(JString("Weapon_Shield_Iron"))) != ty or int(Pool.typeOfId(JString(ARM[0]))) != ty:
        pb.append(("the Weapon_Shield bag type", ty))
    else:
        ids_ = [str(Pool.P_ID[i]) for i in range(len(Pool.P_ID)) if int(Pool.P_T[i]) == ty]
        if sorted(ids_) != sorted([i for i in VAN if i != "Weapon_Shield_Ruined_Giant"] + ARM):
            pb.append(("the pool rows of the type", sorted(ids_)))
        cnt = dict((L, int(Pool.candidates(JInt(ty), JInt(0), JInt(L)))) for L in (1, 5, 12, 15, 25, 42, 64, 84, 100))
        K.notes.append("P shield candidates by level (vanilla loaded; SkyyArmory's 8 not in this boot): %s" % cnt)
        if [L for L in (1, 5, 12, 15, 25, 42, 64, 84, 100) if cnt[L] < 1]:
            pb.append(("a shield candidate at every vanilla band", cnt))
        got = set()
        for n_ in range(60):
            L = (1, 12, 25, 42, 64, 84, 100)[n_ % 7]
            g_ = Unid.pickZ(JInt(ty), JInt(0), JInt(R["rare"]), JInt(L), JInt(L), JInt(0), u, JInt(0))
            if g_ is None:
                pb.append(("pickZ found no shield at", L))
                break
            iid = str(g_[0])
            got.add(iid)
            ms = mods(g_[2])
            if not iid.startswith("Weapon_Shield_") or int(Data.slotOf(JString(iid))) != 5 or [k_ for k_, v_ in ms if "a" not in S_SLOT[S_KEY.index(k_)]] \
                    or str(g_[3].getItemId()) != iid or int(Lvl.level(JString(iid), g_[2])) != L:
                pb.append(("pickZ result", iid, ms, L))
                break
        K.notes.append("P pickZ opened shield bags into: %s" % sorted(got))
        bx = Unid.roll(JInt(30), JInt(ty), JString("mob"), JString("test"), JInt(1), None, JInt(1), JInt(1))
        if bx is None or int(Unid.type(Unid.doc(bx))) != ty:
            pb.append(("Unid.roll with the shield type forced", bx))
        fi = Unid.fromItem(IS(JString("Weapon_Shield_Rusty"), JInt(1)), JInt(1), JInt(-1), JString("test"))
        if fi is None or int(Unid.type(Unid.doc(fi))) != ty:
            pb.append(("fromItem: a dropped vanilla shield -> a shield bag", fi))
        if Unid.why(Unid.doc(bx)) is not None:
            pb.append(("the shield bag can be opened", str(Unid.why(Unid.doc(bx)))))
        lean = JArray(JString)(["Weapon_Sword_", "Weapon_Spear_", "Weapon_Shield_", "Weapon_Longsword_Katana"])
        if not bool(Pool.leanHit(JString("Weapon_Shield"), lean)) or bool(Pool.leanHit(JString("Weapon_GreatShield"), lean)):
            pb.append("the Warrior lean hits Weapon_Shield (not Weapon_GreatShield)")
        apply(loot__classLean="100", **BASE)
        picks = [int(Pool.pickType(False, JInt(25), lean)) for _ in range(300)]
        apply(**BASE)
        share = picks.count(ty) / 300.0
        K.notes.append("P pickType with the Warrior lean at 100 %%: shield share %.2f" % share)
        if share < 0.15:
            pb.append(("the Warrior lean picks shield bags", share))
        apply(shield__gear="false", **BASE)
        cOff = int(Pool.candidates(JInt(ty), JInt(0), JInt(12)))
        apply(**BASE)
        if cOff != 0:
            pb.append(("shield.gear off = no shield candidate", cOff))
    K.check(not pb, "P the Weapon_Shield bags: type, pool rows, candidates by zone, pickZ into REAL shields with armor rolls, roll / fromItem, Warrior lean, off: %s" % pb)

    # ================================================================================== M Smithing + the bench refusal
    mb = []
    sb = []          # FIX critic 3: the Shields card's tier order (its own check)
    sb_ok = [False]
    for iid in ("Weapon_Shield_Copper", "Weapon_Shield_Iron", "Weapon_Shield_Mithril", ARM[0]):
        if int(Smith.cat(JString(iid))) != 2 or not bool(Pack.combatId(JString(iid))) or not bool(Pack.combatGear(JString(iid))):
            mb.append(("Smithing Weapons + combat gear", iid, int(Smith.cat(JString(iid)))))
    if bool(Pack.combatId(JString("Weapon_Shield_Doomed"))) or not bool(Pack.combatGear(JString("Weapon_Shield_Doomed"))) or not bool(Pack.inLoot(JString("Weapon_Shield_Doomed"))):
        mb.append("a named shield = loot only (combat gear, no plain piece, in the bag pool)")
    Fn = JClass("java.util.function.Function")
    from jpype import JImplements, JOverride

    @JImplements(Fn)
    class Dummy(object):
        @JOverride
        def apply(self, o):
            return None
    for k_ in ("sacks:fn:craftList", "sacks:fn:craftPay", "sacks:fn:craftRefund", "sacks:fn:craftCommit"):
        br.put(k_, Dummy())
    w1 = Pack.benchWhy(None, JString("Weapon_Shield_Iron"))
    w2 = Pack.benchWhy(None, JString("Weapon_Shield_Doomed"))
    for k_ in ("sacks:fn:craftList", "sacks:fn:craftPay", "sacks:fn:craftRefund", "sacks:fn:craftCommit"):
        br.remove(k_)
    if w1 is None or "crafted on the Smithing tab now (/smithing - Weapons)" not in str(w1) or w2 is None or "loot only" not in str(w2):
        mb.append(("benchWhy: a plain shield -> Smithing Weapons, a named one -> loot only", w1, w2))
    # the bare boot's recipe store holds only the stand-alone recipe files (item-embedded vanilla recipes are made by a plugin it does not run), so the
    # shield recipe is built here exactly like vanilla's (Armor_Bench, Crafting, category Weapon_Shield) and the Smithing filter is asked about it
    try:
        CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
        MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
        BRQ = JClass("com.hypixel.hytale.protocol.BenchRequirement")
        BT = JClass("com.hypixel.hytale.protocol.BenchType")

        def recipe(out_id, bench, inp="Ingredient_Bar_Iron"):
            mq = MQ(JString(inp), None, None, JInt(4), None)
            brq = BRQ(BT.Crafting, JString(bench), JArray(JString)(["Weapon_Shield"]), JInt(0), None)
            po = MQ(JString(out_id), None, None, JInt(1), None)
            try:
                return CRR(JArray(MQ)([mq]), po, JArray(MQ)([po]), JInt(1), JArray(BRQ)([brq]), JFloat(3.5), False, JInt(0))
            except Exception as ex_:
                K.notes.append("M CraftingRecipe ctor: %s - fields set" % str(ex_)[:160])
                r_ = us.allocateInstance(CRR.class_)
                fld(CRR, "input").set(r_, JArray(MQ)([mq]))
                fld(CRR, "primaryOutput").set(r_, po)
                fld(CRR, "outputs").set(r_, JArray(MQ)([po]))
                fld(CRR, "benchRequirement").set(r_, JArray(BRQ)([brq]))
                return r_
        uz = [(iid, bool(Smith.usable(recipe(iid, "Armor_Bench")))) for iid in ("Weapon_Shield_Copper", "Weapon_Shield_Iron", "Weapon_Shield_Mithril", ARM[0])]
        K.notes.append("M Smithing.usable on vanilla-shaped shield recipes (Armor_Bench): %s" % uz)
        if [x for x in uz if not x[1]]:
            mb.append(("a plain shield recipe at the Armor Bench is a Smithing recipe (usable)", uz))
        if bool(Smith.usable(recipe("Weapon_Shield_Iron", "Armor_Bench", "Weapon_Shield_Copper"))):
            mb.append("a recipe with a gear input (an alteration) is never a Smithing recipe")
        apply(shield__gear="false", **BASE)
        uo = bool(Smith.usable(recipe("Weapon_Shield_Iron", "Armor_Bench")))
        apply(**BASE)
        if uo:
            mb.append("shield.gear off = not a Smithing recipe (the bench crafts it as before)")
        rs_ = Smith.recipes()
        outs_ = [str(rs_.get(i)[1]) for i in range(rs_.size())]
        K.notes.append("M the boot's recipe store: %d shown recipes (shields %s)" % (len(outs_), sorted(x for x in outs_ if x.startswith("Weapon_Shield_"))))
        if bool(Smith.shows(u, JString("Weapon_Shield_Iron"), True)) is not True:
            mb.append("Show all lists the Iron shield")
        # FIX (critic 3, "sort by tier everywhere"): the REAL GearSmith.groups on a recipe list holding every plain shield (vanilla metals + the 8 zone
        # shields, fed in reverse order) + an Iron sword = ONE "Weapon_Shield" card in tier order (band low, then id), Copper .. Mithril in ladder order
        rec0 = Smith.REC
        sb_ok[0] = True
        try:
            plain = ["Weapon_Shield_" + w_ for w_ in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril")] + ARM
            rows_ = JClass("java.util.ArrayList")()
            for iid in list(reversed(plain)) + ["Weapon_Sword_Iron"]:
                rows_.add(JArray(JObject)([JString("T_" + iid), JString(iid), recipe(iid, "Armor_Bench")]))
            Smith.REC = JArray(JObject)([rec0[0], rec0[1], rows_]) if rec0 is not None else None
            if rec0 is None:
                sb.append("Smithing cache REC not filled by recipes()")
            else:
                gs_ = Smith.groups(u, JInt(2), True)
                card = [gs_.get(i) for i in range(gs_.size()) if str(gs_.get(i)[0]) == "Weapon_Shield"]
                got = [str(x) for x in card[0][1]] if card else []
                want = sorted(plain, key=lambda i_: (int(Lvl.band(JString(i_))[0]), i_))
                van_ord = [x for x in got if not x.endswith("_SkyWynn")]
                K.notes.append("M Shields card order: %s" % ", ".join("%s %d" % (x[14:], int(Lvl.band(JString(x))[0])) for x in got))
                if len(card) != 1 or got != want or van_ord != plain[:6] or "Weapon_Sword_Iron" in got:
                    sb.append(("the Shields card = one card, every plain shield, in tier order", got, want))
        finally:
            Smith.REC = rec0
    except Exception as ex_:
        mb.append(("Smithing usable on a REAL recipe", str(ex_)[:300]))
    K.check(sb_ok[0] and not sb, "M2 the REAL GearSmith.groups: one Shields card, Copper .. Mithril + the 8 zone shields in tier order (band low, then id), no sword: %s" % sb)
    K.check(not mb, "M Smithing: plain shields are Smithing > Weapons recipes (usable on a REAL recipe, not with a gear input / shield.gear off), benches refuse them, named = loot only: %s" % mb)

    # ================================================================================== F first sight (the legacy stamp, journaled)
    fb = []
    n0 = int(Off.N[0])
    cnt = JArray(JInt)(4)
    s0 = IS(JString("Weapon_Shield_Wood"), JInt(1))
    s1 = Stamp.stampStack(s0, u, cnt)
    d1 = Data.gearDoc(s1.getMetadata()) if s1 is not None else None
    if d1 is None or SysJ.identityHashCode(s1) == SysJ.identityHashCode(s0) or int(Data.rarity(d1)) != 0 or int(Lvl.level(JString("Weapon_Shield_Wood"), d1)) != 1 \
            or str(s1.getItemId()) != "Weapon_Shield_Wood" or int(s1.getQuantity()) != 1 or int(Off.N[0]) != n0 + 1 or int(cnt[0]) != 1:
        fb.append(("a bare Wood shield -> a Normal Lv 1 document, counted", d1, int(Off.N[0]) - n0, int(cnt[0])))
    s2 = Stamp.stampStack(s1, u, cnt)
    if int(Off.N[0]) != n0 + 1:
        fb.append("a stamped shield is never journaled again")
    s3 = Stamp.stampStack(IS(JString("Weapon_Sword_Iron"), JInt(1)), u, cnt)
    if int(Off.N[0]) != n0 + 1:
        fb.append("a sword is not a shield")
    try:
        P("GearLog").flush() if hasattr(P("GearLog"), "flush") else None
    except Exception:
        pass
    K.check(not fb, "F first sight: a bare shield = a Normal document at its band (nothing else changes), journaled once: %s" % fb)
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
    K.check(c0 is not None, "D the live copy has a config.properties")
    Paths = JClass("java.nio.file.Paths")
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(home)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28", "migrateCan2", "migrateAs51",
           "migrateUt53", "migrateMy53", "migrateSig56"]
    m0 = "\n".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    m1 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    K.notes.append("D start 1: one-time updates said %r" % m0[-400:])
    K.check(open(fc, "rb").read() == c1 and m1 == "", "D start 2 changes nothing")
    for k_ in (b"shield.gear", b"shield.def", b"shield.power"):
        K.check((k_ in c1) == (k_ in c0), "D %s is a new key: not written by this round" % k_.decode())
    if b"shield." not in c0:
        K.eq((bool(Cfg.SHIELD_ON), int(Cfg.SH_DEF), float(Cfg.SH_PW)), (True, 6, 19.5), "D the shield rows absent in the live file = the defaults")
    K.check(str(Cfg.EXCLUDE).find("Weapon_Shield_") >= 0 or b"gear.exclude=" in c0, "D the live gear.exclude is untouched")
    dl, dn = c0.decode("latin-1").splitlines(), c1.decode("latin-1").splitlines()
    extra = [l for l in dn if l not in dl]
    allowed = lambda l: (l.strip() == "" or l.startswith(("ut.", "utfx.", "utpow.", "gear.mythicItems=", "stats.as=", "sig.ut.", "# ---- ")) or "SkyyGear 0.3.5" in l)
    K.check(all(allowed(l) for l in extra), "D only the earlier 0.3.5x one-time updates may touch the file: %s" % [l for l in extra if not allowed(l)][:5])
    K.check(not [l for l in dl if l not in dn], "D no old line removed")
    K.save()


HK.run_compare = T54["run_compare54"]
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("engine57", T57["run_engine"]), ("engine56", T56["run_engine"]), ("engine55", T55["run_engine"]), ("engine54", T54["run_engine"]),
        ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
