"""Derive SkyyMobs/build_skyymobs_0.1.26.py from the GENERATED 0.1.25 (build_skyymobs_0.1.25.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_25_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.25
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_26_patch.py   then   python SkyyMobs/build_skyymobs_0.1.26.py   then   python SkyyMobs/test_skyymobs_0.1.26.py
Edit THIS file, never the generated script (never --deploy).

0.1.26 (2026-11-21) = MOB KILL COINS (round mobcoin1). Skyy 2026-11-21 (docs/answered/economy.md 'MOB COINS'): "but the combat one should
  drop coins from the mobs too. lets make all mobs drop some money so you can get money from xp mob farming too" [default: mob farming earns
  about half the coins / hour of a gathering skill in the same zone (P7 targets), bosses / elites more, no coins from spawner-farm abuse
  beyond the usual kill-XP caps; Server Setup rows]. The Combat shard clicker's own kill coins are a later SkyyShards round - it reuses the
  numbers through the new bridge mob:fn:killCoins.
  1. KILL COINS (new class MobCoin; SpoilsSys calls MobCoin.onDeath ONCE per death - its own once-per-death map, BEFORE the engine's
     drop gate, so a mob with no drop list pays too): a mob a PLAYER kills (the killing blow's Damage$EntitySource has a PlayerRef - a
     projectile's = its shooter; the same killer test SkyySkills' kill XP uses) pays coins.kill.base (25) x the coin curve at the mob's level
     (coins:fn:curve = SkyyCoins' live coins.curve; SkyyCoins absent / older = the built-in copy of its default, asserted = tools/
     balance_model.py p7_curve_text()) x the rank: elite x coins.kill.eliteX (3), mini boss x coins.kill.miniX (10), full boss (Boss roles,
     pack bosses, rank boss) x coins.kill.bossX (20). An UNLEVELLED mob (animals ...) pays coins.kill.animals (50 %) of that at the zone
     level of its spot (mob:fn:levelAt's band, middle of lo..hi); no band there (islands) = nothing. At least 1 coin while on.
     fix (mobcoin1fix): an unlevelled mob pays only when WILD (MobCoin.wild): attitude not FRIENDLY / REVERED / IGNORE (tamed animals,
     villagers, summons), not in "Never level these" (levels.exclude: Tamed_* = every bred / penned animal, Temple_*, *_Merchant*, *NPC*,
     *Trader*, *_Mount*, *_Pet* ...) or the pack helpers, not a baby (*_Calf, *_Chick, *_Kid, *_Lamb, *_Piglet, *_Foal, *_Cub). A boss
     always pays. Closes the bred-pen money loop (critic 1) and the villager / NPC kill (critic note 4).
     Straight into the killer's purse (coins:fn:add = the ACTIVE profile's purse; skipped while profile:busy:<uuid> - a profile switch).
  2. THE COIN MATH (the build prints + asserts it): P7 G = a focused gathering hour (tools/balance_model.py p7_G_mid: Zone 1-5 ~8.2k / 42k /
     300k / 1.06M / 3.8M) at the zone middle levels 10 / 30 / 50 / 70 / 90; kill rate KILLS_H 150 / h (the model's Normal pace, a GUESS
     there too) x (1 + 3 % elites x 2) = 25 x curve x 159 = 3,975 / 20.7k / 146k / 517k / 1.85M per hour = 0.49 G in every zone ("about half").
  3. GUARDS (= no kill XP -> no coins): no player killer (a pet's / summon's own kill, fall / environment deaths: SkyySkills pays no kill XP
     for them either), a killer in Creative, the dead mob a player's pet / summon (pets:fn:ownerOf), paid exactly once per death (first());
     a cancelled hit never adds a DeathComponent, so it never reaches SpoilsSys. coins.kill.capHour (default 5,000,000 = about 2.7 Zone 5
     kill hours; 0 = no limit; fix mobcoin1fix: was 0) caps the coins a player gets per hour (kills + party shares; a failed payment is
     given back to the cap). Spawner mobs: SkyySkills has no spawner rule for kill XP, so none here either (the cap is the brake) - asked.
     The kill XP class-weapon test (SkillClass.killSlot) is NOT mirrored (no bridge; a fist / any-item kill pays coins) - asked.
     Once per death: a corpse still ticking refreshes its DONE entry (MobCoin.seen), so the purge never frees a live corpse (critic 3).
  4. PARTY: SkyySkills shares kill XP (party.combatShare.*) -> mirrored: with coins.kill.party (on) every OTHER member of the killer's
     SkyyParty party (party:fn:members) online in the same world, ready, alive, not in Creative and within SkyySkills' live
     party.combatShare.radius (48) gets party.combatShare.fraction (0.5) of the kill's coins (config:fn:SkyySkills "get", cached 2 s;
     SkyySkills absent or its share off = no coin share). Each member's own purse, own cap.
  5. MESSAGE: "+25 coins  Lv 12 Trork Warrior" through SkyyHud's Coins message kind (msgroute:fn:get "coins": the player's own Chat / Feed /
     Off switch in /settings, else Server Setup > HUD > Messages; tools/skyyroute.py = class MobRoute) - feed card, or a gold chat line,
     or nothing. coins.kill.message off = no line for anyone (coins still paid). Feed cards pass RT.gate (a new card text at most once
     per 400 ms per player; the same text merges): a burst of mixed kills never overflows SkyyHud's 4 cards into chat (coins still paid).
  6. BRIDGE mob:fn:killCoins (put in setup, removed in shutdown; any thread, never throws): apply(Object[] { String roleId or null, Number
     level [, String rank "elite" | "mini" | "boss"] }) -> Long coins of ONE kill at the live rows (a Boss roles role = boss; level < 1 or
     the switch off = 0; bad arguments = null). No cap, no message, nothing paid - SkyyShards' Combat clicker pays it itself later.
  7. SERVER SETUP > Mobs > Kill coins (new tab, 9 rows, live): on / off, coins at Lv 10, elite / mini boss / boss x, animals %, coins per
     hour cap, party share, messages. New keys only: a file without a line = the default (NO one-time update). Ready line: + "kill coins ...".
  SAVED DATA: none (purses are SkyyCoins'; the hour cap is memory only, reset by a restart). Two new classes (MobCoin, MobRoute), one new
  bridge key, no new system / command.
  ROLLBACK to 0.1.25: alone is safe (no saved data; the 9 rows are ignored; coins already paid stay in the purses).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.25.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.26.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.25"') and P.s.startswith('"""SkyyMobs 0.1.25 - build script') and P.has("MobAug") and not P.has("MobCoin"), "not the SET pin 0.1.25"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")
HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.26 (2026-11-21)"):].rstrip() + "\n\n"

P.rep('''"""SkyyMobs 0.1.25 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_25_patch.py from the SET pin 0.1.24 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.25.py -> SkyyMobs/SkyyMobs-0.1.25.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.25.py
''', '''"""SkyyMobs 0.1.26 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_26_patch.py from the SET pin 0.1.25 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.26.py -> SkyyMobs/SkyyMobs-0.1.26.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.26.py
''' + NOTE)
P.rep('VERSION = "0.1.25"', 'VERSION = "0.1.26"')

# ---------- the rows + the coin math (build time; before CFG_LINES)
DEF = '''# 0.1.26 (mobcoin1): the kill coin rows (Server Setup > Mobs > Kill coins; MobCoin, called by SpoilsSys) + the coin math (Skyy 2026-11-21:
# "lets make all mobs drop some money so you can get money from xp mob farming too"; default about half a gathering hour, P7 targets)
COIN_ROW = [("coins.kill.on", "Kill coins", "bool", "true", "", "", "", "", "Every mob a player kills pays coins straight into the killer's purse.", "COIN_ON"),
            ("coins.kill.base", "Coins for a Lv 10 kill", "dec", "25", "0", "1000000", "", "",
             "An ordinary mob at Lv 10. Other levels follow the coin curve (Server Setup > Coins).", "COIN_BASE"),
            ("coins.kill.eliteX", "Elite x", "dec", "3", "1", "1000", "", "x", "An elite pays this many times an ordinary mob of its level.", "COIN_ELITE"),
            ("coins.kill.miniX", "Mini boss x", "dec", "10", "1", "1000", "", "x", "A mini boss pays this many times an ordinary mob of its level.", "COIN_MINI"),
            ("coins.kill.bossX", "Boss x", "dec", "20", "1", "1000", "", "x", "A full boss pays this many times an ordinary mob of its level.", "COIN_BOSS"),
            ("coins.kill.animals", "Animals and unlevelled mobs", "dec", "50", "0", "100", "", "%",
             "Wild mobs without a level pay this share at their zone level. Islands, tamed, babies: none.", "COIN_ANIMAL"),
            ("coins.kill.capHour", "Most kill coins per hour", "int", "5000000", "0", "2000000000", "", "",
             "Per player, kills and party shares together. 0 = no limit.", "COIN_CAP"),
            ("coins.kill.party", "Party share (like kill XP)", "bool", "true", "", "", "", "",
             "Party members near the kill get SkyySkills' party XP share of the coins.", "COIN_PARTY"),
            ("coins.kill.message", "Kill coin messages", "bool", "true", "", "", "", "",
             "Show +25 coins (feed or chat: each player's own Coins message switch).", "COIN_MSG")]
assert all(len(_r[1]) <= 40 and len(_r[8]) <= 100 for _r in COIN_ROW), [(len(_r[1]), len(_r[8])) for _r in COIN_ROW]
COIN_CURVE_TEXT = '1:0.476,8:0.848,10:1,15:1.51,20:2.28,28:4.41,30:5.2,35:8.49,40:13.8,48:30.3,50:36.8,55:50.5,60:69.2,68:115,70:130,75:179,80:246,88:410,90:466,95:641,100:881'          # = SkyyCoins 0.1.10+ coins.curve default
assert BM.p7_curve_text() == COIN_CURVE_TEXT == BM.P7_CURVE_TEXT, "0.1.26: the built-in coin curve = tools/balance_model.py p7_curve_text()"
_CB = float([_r for _r in COIN_ROW if _r[0] == "coins.kill.base"][0][3])
_CE = float([_r for _r in COIN_ROW if _r[0] == "coins.kill.eliteX"][0][3])
_EL_CH = float([_r for _r in P4_RANK_ROWS if _r[0] == "rank.elite.chance"][0][1])          # the Ranks row default (3 %%)
COIN_MATH = []
for _z, _lv in zip(range(1, 6), (10, 30, 50, 70, 90)):
    _amt = max(1, int(round(_CB * BM.p7_curve_from_text(COIN_CURVE_TEXT, _lv))))
    _ph = BM.KILLS_H * (1.0 + _EL_CH / 100.0 * (_CE - 1.0)) * _amt
    _g = BM.p7_G_mid(_z)
    COIN_MATH.append((_z, _lv, _amt, _ph, _g, _ph / _g))
    assert 0.40 <= _ph / _g <= 0.60, "0.1.26: Zone %%d kill coins = about half a gathering hour: %%.2f" %% (_z, _ph / _g)
_CAPD = int([_r for _r in COIN_ROW if _r[0] == "coins.kill.capHour"][0][3])          # mobcoin1fix: a generous default cap, 2-4 Zone 5 kill hours
assert 2.0 <= _CAPD / COIN_MATH[-1][3] <= 4.0, "0.1.26: the default hour cap = 2-4 Zone 5 kill hours: %%.2f" %% (_CAPD / COIN_MATH[-1][3])
print("0.1.26 kill coins (%%g at Lv 10 x the coin curve; %%d kills / h, %%g %%%% elites x%%g) vs P7 G (a focused gathering hour): %%s" %% (_CB, BM.KILLS_H, _EL_CH, _CE,
      "; ".join("Zone %%d Lv %%d %%d a kill = %%.0f / h = %%.2f G (G %%.0f)" %% (_z, _lv, _a, _ph, _r, _g) for _z, _lv, _a, _ph, _g, _r in COIN_MATH)))
'''
P.rep('''# 0.1.24 (gl2): the Trork / Kweebec set drop rows (Server Setup > Mobs > Set drops; MobTheme, rolled by SpoilsSys)
TH_TROW = ''', DEF.replace("%%", "%") + '''# 0.1.24 (gl2): the Trork / Kweebec set drop rows (Server Setup > Mobs > Set drops; MobTheme, rolled by SpoilsSys)
TH_TROW = ''')
# the default file lines (absent in an older file = the default)
P.rep('''              "%s=%s" % (ZMIX_ROW[0], ZMIX_ROW[4])]          # 0.1.25 (absent in an older file = the default)
''', '''              "%s=%s" % (ZMIX_ROW[0], ZMIX_ROW[4])]          # 0.1.25 (absent in an older file = the default)
CFG_LINES += ["# Kill coins (SkyyMobs 0.1.26): a player's kill pays coins.kill.base at Lv 10 x the coin curve x the rank (elite / mini / boss x);",
              "# wild unlevelled mobs (animals; never tamed / babies / NPCs) coins.kill.animals % at the zone level; capHour 0 = no limit; party = SkyySkills' party XP share.",
              ] + ["%s=%s" % (_r[0], _r[3]) for _r in COIN_ROW]          # 0.1.26 (absent in an older file = the default)
''')
# fields
P.rep('''F(cfg, "public static volatile int ELEM_ZMIX = %d;" % ZMIX_DEF)          # aug3fix: ... this % of them (the rest: the 4 other elements)
''', '''F(cfg, "public static volatile int ELEM_ZMIX = %d;" % ZMIX_DEF)          # aug3fix: ... this % of them (the rest: the 4 other elements)
for _r in COIN_ROW:          # 0.1.26 (mobcoin1): the kill coin rows
    if _r[2] == "bool":
        F(cfg, "public static volatile boolean %s = %s;" % (_r[9], _r[3]))
    elif _r[2] == "int":
        F(cfg, "public static volatile int %s = %s;" % (_r[9], _r[3]))
    else:
        F(cfg, "public static volatile double %s = %s;" % (_r[9], repr(float(_r[3]))))
''')
# the tab + rows
P.rep('''CFG_CATS.insert(CFG_CATS.index(("theme", "Set drops")) + 1, ("aug", "Augments"))          # 0.1.25 (aug3)
''', '''CFG_CATS.insert(CFG_CATS.index(("theme", "Set drops")) + 1, ("aug", "Augments"))          # 0.1.25 (aug3)
CFG_CATS.insert(CFG_CATS.index(("aug", "Augments")) + 1, ("coins", "Kill coins"))          # 0.1.26 (mobcoin1)
''')
P.rep('''CFG_ROWS += [ZVAR_ROW, ZMIX_ROW]          # 0.1.25 (aug3): Elements > tougher versions take the zone element + its share (live)
''', '''CFG_ROWS += [ZVAR_ROW, ZMIX_ROW]          # 0.1.25 (aug3): Elements > tougher versions take the zone element + its share (live)
CFG_ROWS += [(_r[0], _r[1], "coins", _r[2], _r[3], _r[4], _r[5], _r[6], _r[7], "live", _r[8], "field:MobCfg.%s" % _r[9]) for _r in COIN_ROW]          # 0.1.26 (mobcoin1): kill coins (live)
''')
# load
LOAD = ""
for _k, _t, _d, _lo, _hi, _f in (("coins.kill.on", "bool", "true", "", "", "COIN_ON"), ("coins.kill.base", "dec", "25", "0", "1000000", "COIN_BASE"),
                                 ("coins.kill.eliteX", "dec", "3", "1", "1000", "COIN_ELITE"), ("coins.kill.miniX", "dec", "10", "1", "1000", "COIN_MINI"),
                                 ("coins.kill.bossX", "dec", "20", "1", "1000", "COIN_BOSS"), ("coins.kill.animals", "dec", "50", "0", "100", "COIN_ANIMAL"),
                                 ("coins.kill.capHour", "int", "5000000", "0", "2000000000", "COIN_CAP"), ("coins.kill.party", "bool", "true", "", "", "COIN_PARTY"),
                                 ("coins.kill.message", "bool", "true", "", "", "COIN_MSG")):
    if _t == "bool":
        LOAD += '''  %s = bool(c.getProperty("%s"), %s);          // 0.1.26 (mobcoin1)
''' % (_f, _k, _d)
    elif _t == "int":
        LOAD += '''  %s = intOf(c.getProperty("%s"), %s, %s, %s);          // 0.1.26
''' % (_f, _k, _d, _lo, _hi)
    else:
        LOAD += '''  %s = dec(c.getProperty("%s"), %s, %s, %s);          // 0.1.26
''' % (_f, _k, repr(float(_d)), repr(float(_lo)), repr(float(_hi)))
P.rep('''  ELEM_ZMIX = intOf(c.getProperty("elem.zoneMix"), 60, 0, 100);          // aug3fix
''', '''  ELEM_ZMIX = intOf(c.getProperty("elem.zoneMix"), 60, 0, 100);          // aug3fix
''' + LOAD)

# ---------- engine types / probes: the killer's game mode (SkyySkills' creative test), a party member's ready state
P.rep('''T.update({"SPPL": "com.hypixel.hytale.server.spawning.SpawningPlugin",          # 0.1.21 (spawn1): the zone densities + /mobs spawns
''', '''T.update({"GM": "com.hypixel.hytale.protocol.GameMode"})          # 0.1.26 (mobcoin1): no kill coins in Creative (SkyySkills' kill XP rule)
T.update({"SPPL": "com.hypixel.hytale.server.spawning.SpawningPlugin",          # 0.1.21 (spawn1): the zone densities + /mobs spawns
''')
P.rep('''B.probe(pool, G["ADDR"], "LOAD")
PROBED.append("AddReason.LOAD")
''', '''B.probe(pool, G["ADDR"], "LOAD")
PROBED.append("AddReason.LOAD")
# 0.1.26 (mobcoin1): the killer's game mode, a party member's ready state + name, the killer's / member's position
SIGS += [(G["PLA"], "getGameMode", G["GM"], []), (G["PLA"], "isWaitingForClientReady", "boolean", []),
         (G["TC"], "getPosition", G["VEC"], []), (G["DENT"], "getRef", G["REF"], []), (G["DMG"], "getSource", G["DMG"] + "$Source", [])]
B.probe(pool, G["GM"], "Creative")
PROBED.append("GameMode.Creative")
''')

# ---------- the classes
P.rep('''maug = pool.makeClass(PKG + ".MobAug")''', '''mcoin = pool.makeClass(PKG + ".MobCoin")     # 0.1.26 (mobcoin1): the kill coins (SpoilsSys calls onDeath) + the bridge mob:fn:killCoins
mrte = pool.makeClass(PKG + ".MobRoute")     # 0.1.26: tools/skyyroute.py's MsgRoute (SkyyHud's Coins message kind: chat / feed / off)
maug = pool.makeClass(PKG + ".MobAug")''')
P.rep('''mlds, mvat, mspw, mspk, mvar, mvsy, mthm, maug]''', '''mlds, mvat, mspw, mspk, mvar, mvsy, mthm, maug, mcoin, mrte]''')

MC = r'''# 0.1.26 (mobcoin1): MobRoute = tools/skyyroute.py's MsgRoute (the same rules as SkyySkills / SkyyClasses / SkyyCollections' copies)
import skyyroute as RT
RT.add_msg_route(mrte, CtField, CtNewMethod, PKG + ".MobLevel.bridge()")
# 0.1.26 (mobcoin1): MobCoin - the kill coins. onDeath (SpoilsSys, the world thread) reads the engine facts of ONE death and hands them to
# once() (first() + core(): pure, executed by the harness); shareAll / memberHere = the party glue; apply() = the bridge mob:fn:killCoins.
mcoin.addInterface(pool.get("java.util.function.Function"))
C(mcoin, "public MobCoin() { }")
for _f in ("public static final int[] CV_LV = new int[] { %s };" % ", ".join(_kv.split(":")[0] for _kv in COIN_CURVE_TEXT.split(",")),
           "public static final double[] CV_F = new double[] { %s };" % ", ".join(repr(float(_kv.split(":")[1])) for _kv in COIN_CURVE_TEXT.split(",")),
           "public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile long PRUNED = 0L;", "public static final long DONE_MS = 600000L;",
           "public static final java.util.concurrent.ConcurrentHashMap HOUR = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile java.util.function.BiConsumer TELL_API = null;",          # HARNESS SEAM ONLY (null in the game)
           "public static volatile double[] PCFG = null;", "public static volatile long PCFG_AT = 0L;",
           "public static final String BABY = \"*_Calf*,*_Chick*,*_Kid,*_Kid_*,*_Lamb*,*_Piglet*,*_Foal*,*_Cub*\";",          # mobcoin1fix: babies never pay
           "public static volatile String[] P_BABY = null;"):
    F(mcoin, _f)
for _n in ("DEATHS", "KILLS", "PAYS", "PAID", "PARTY", "PARTY_PAID", "NOPLAYER", "CREATIVE", "PET", "NOLEVEL", "CAPPED", "BUSY", "FAIL", "TAME", "GATED"):
    F(mcoin, "public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _n)
M(mcoin, "public static boolean on() { return @PKG@.MobCfg.COIN_ON && @PKG@.MobCfg.COIN_BASE > 0.0; }")
# the built-in coin curve (SkyyCoins' coins.curve default; log-linear between the points, the ends extended, the level clamped to 1..100)
M(mcoin, r"""
public static double curveOwn(int level) {
  int x = level < 1 ? 1 : (level > 100 ? 100 : level);
  int i = 0;
  if (x >= CV_LV[CV_LV.length - 1]) i = CV_LV.length - 2;
  else { while (i < CV_LV.length - 2 && x > CV_LV[i + 1]) i++; }
  double a = Math.log(CV_F[i]);
  double b = Math.log(CV_F[i + 1]);
  return Math.exp(a + (b - a) * (double) (x - CV_LV[i]) / (double) (CV_LV[i + 1] - CV_LV[i]));
}""")
# SkyyCoins' LIVE coin curve (coins:fn:curve, Server Setup > Coins > Coin curve), else the built-in copy
M(mcoin, r"""
public static double curve(int level) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object f = b == null ? null : b.get("coins:fn:curve");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(Integer.valueOf(level));
      if (r instanceof Number) {
        double d = ((Number) r).doubleValue();
        if (d > 0.0 && !Double.isNaN(d) && !Double.isInfinite(d)) return d;
      }
    }
  } catch (Throwable t) { }
  return curveOwn(level);
}""")
M(mcoin, r"""
public static double rankX(String rw, boolean boss) {
  if (boss || "boss".equals(rw)) return @PKG@.MobCfg.COIN_BOSS;
  if ("mini".equals(rw)) return @PKG@.MobCfg.COIN_MINI;
  if ("elite".equals(rw)) return @PKG@.MobCfg.COIN_ELITE;
  return 1.0;
}""")
# mobcoin1fix: an UNLEVELLED mob pays only when wild: not tamed / a villager / a summon (attitude), not in Never level these (Tamed_*, Temple_*,
# merchants, NPCs, traders, mounts, pets) or the pack helpers, not a baby. "" (attitude unreadable) = the lists decide.
M(mcoin, r"""
public static boolean wild(String att, String role) {
  String a = att == null ? "" : att.trim().toUpperCase();
  if (a.equals("FRIENDLY") || a.equals("REVERED") || a.equals("IGNORE")) return false;
  if (role == null || role.trim().length() == 0) return false;
  if (@PKG@.MobGlob.any(@PKG@.MobCfg.P_PNEVER, role) || @PKG@.MobGlob.any(@PKG@.MobCfg.P_EXCL, role)) return false;
  String[] b = P_BABY;
  if (b == null) { b = @PKG@.MobGlob.list(BABY); P_BABY = b; }
  return !@PKG@.MobGlob.any(b, role);
}""")
# the coins of ONE kill (no cap, nothing paid): base x curve(level) x rank (x animals % when unlevelled); at least 1 while on; 0 = off / no level
M(mcoin, r"""
public static long amount(int level, String rw, boolean boss, boolean levelled) {
  if (!on() || level < 1) return 0L;
  double v = @PKG@.MobCfg.COIN_BASE * curve(level > 100 ? 100 : level) * rankX(rw, boss);
  if (!levelled) v = v * @PKG@.MobCfg.COIN_ANIMAL / 100.0;
  if (!(v > 0.0)) return 0L;
  if (v > 1.0E15) v = 1.0E15;
  long r = Math.round(v);
  return r < 1L ? 1L : r;
}""")
# once per death (the corpse is ticked a few times; entries older than DONE_MS go when the map passes 512, at most one purge a second)
M(mcoin, r"""
public static boolean first(java.util.UUID mob) {
  if (mob == null) return false;
  long now = System.currentTimeMillis();
  if (DONE.size() > 512 && now - PRUNED > 1000L) {
    PRUNED = now;
    Object[] ks = DONE.keySet().toArray();
    for (int i = 0; i < ks.length; i++) { Object t = DONE.get(ks[i]); if (!(t instanceof Long) || now - ((Long) t).longValue() > DONE_MS) DONE.remove(ks[i]); }
  }
  return DONE.putIfAbsent(mob, Long.valueOf(now)) == null;
}""")
# mobcoin1fix: a corpse ticked again refreshes its entry (true = already paid / judged), so the purge only frees corpses gone > DONE_MS
M(mcoin, r"""
public static boolean seen(java.util.UUID mob, long now) {
  if (mob == null || !DONE.containsKey(mob)) return false;
  DONE.put(mob, Long.valueOf(now));
  return true;
}""")
# the hour cap (memory only; per player UUID; a window starts with the first coins after the last one ended)
M(mcoin, r"""
public static synchronized void prune(long now) {
  Object[] ks = HOUR.keySet().toArray();
  for (int i = 0; i < ks.length; i++) {
    Object o = HOUR.get(ks[i]);
    if (!(o instanceof long[]) || now - ((long[]) o)[0] >= 3600000L || now < ((long[]) o)[0]) HOUR.remove(ks[i]);
  }
}""")
M(mcoin, r"""
public static synchronized long capTake(java.util.UUID u, long want, long now) {
  if (u == null || want <= 0L) return 0L;
  Object o = HOUR.get(u);
  long[] h = null;
  if (o instanceof long[]) h = (long[]) o;
  if (h == null || now - h[0] >= 3600000L || now < h[0]) {
    if (HOUR.size() > 4096) prune(now);
    h = new long[] { now, 0L };
    HOUR.put(u, h);
  }
  long g = want;
  long cap = (long) @PKG@.MobCfg.COIN_CAP;
  if (cap > 0L) {
    long left = cap - h[1];
    if (left <= 0L) return 0L;
    if (g > left) g = left;
  }
  h[1] = h[1] + g;
  return g;
}""")
M(mcoin, r"""
public static synchronized void capGive(java.util.UUID u, long n) {
  Object o = u == null ? null : HOUR.get(u);
  if (!(o instanceof long[]) || n <= 0L) return;
  long[] h = (long[]) o;
  h[1] = h[1] - n;
  if (h[1] < 0L) h[1] = 0L;
}""")
M(mcoin, r"""
public static boolean busy(java.util.UUID u) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    return b != null && u != null && Boolean.TRUE.equals(b.get("profile:busy:" + u));
  } catch (Throwable t) { return false; }
}""")
# SkyyCoins' coins:fn:add (the ACTIVE profile's purse); true only when it answered the new balance (CoinFn answers null on any failure)
M(mcoin, r"""
public static boolean pay(java.util.UUID u, long n) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object f = b == null ? null : b.get("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    return r instanceof Number;
  } catch (Throwable t) { return false; }
}""")
# pay up to want coins to u (busy profile = none; the hour cap; a failed payment gives the cap back); returns the coins paid
M(mcoin, r"""
public static long give(java.util.UUID u, long want, long now) {
  if (u == null || want <= 0L) return 0L;
  if (busy(u)) { BUSY.incrementAndGet(); return 0L; }
  long g = capTake(u, want, now);
  if (g <= 0L) { CAPPED.incrementAndGet(); return 0L; }
  if (!pay(u, g)) {
    capGive(u, g);
    FAIL.incrementAndGet();
    @PKG@.MobLog.warnOnce("coins:pay", "kill coins: coins:fn:add did not pay " + g + " coins to " + u + " (SkyyCoins not running?) - nothing paid (logged once; MobCoin.FAIL counts them)");
    return 0L;
  }
  PAYS.incrementAndGet();
  PAID.addAndGet(g);
  return g;
}""")
M(mcoin, r"""
public static String fmt(long n) {
  try { return java.text.NumberFormat.getIntegerInstance(java.util.Locale.US).format(n); } catch (Throwable t) { return String.valueOf(n); }
}""")
M(mcoin, r"""
public static String name(String role) {
  if (role == null || role.length() == 0) return "mob";
  String s = role;
  int i = s.indexOf("_SkyyArmored");
  if (i < 0) i = s.indexOf("_SkyyVeteran");
  if (i > 0) s = s.substring(0, i);
  return s.replace('_', ' ');
}""")
# the line: SkyyHud's Coins kind (the player's Chat / Feed / Off switch); a feed card SkyyHud refuses becomes the chat line
M(mcoin, r"""
public static String tell(java.util.UUID u, String chat, String feed) {
  if (u == null || !@PKG@.MobCfg.COIN_MSG) return "none";
  String r = @PKG@.MobRoute.route(u, "coins");
  if ("off".equals(r)) { @PKG@.MobRoute.off(); return "off"; }
  if ("feed".equals(r)) {
    if (!@PKG@.MobRoute.gate(u, "coins", feed, 400L, 0L)) { GATED.incrementAndGet(); return "gated"; }          // mobcoin1fix: no burst overflow into chat
    if (@PKG@.MobRoute.feed(u, "coins", null, feed, 0L)) return "feed";
  }
  @PKG@.MobRoute.said(chat);
  java.util.function.BiConsumer f = TELL_API;
  if (f != null) { f.accept(u, chat); return "chat"; }
  try {
    @PR@ pr = @UNIV@.get().getPlayer(u);
    if (pr != null) pr.sendMessage(@MSG@.raw(chat).color(@GOLDC@));
  } catch (Throwable t) { }
  return "chat";
}""".replace("@GOLDC@", jstr(SUI.COLOR["gold"])))
# THE CORE of one death (pure: no engine object). ku = the killer (a player; null = none), cr = in Creative, pet = the dead mob is a player's
# pet / summon, att = its attitude (unlevelled only; "" = unread), lvl / rw = its MobInfo (0 / "" = unlevelled), at = the zone level at its spot (-1 = none). Returns the coins the kill is worth
# (0 = it pays nothing; the killer may still get less - the hour cap / a busy profile); the party share is the caller's (shareAll).
M(mcoin, r"""
public static long core(java.util.UUID ku, boolean cr, boolean pet, String role, String att, int lvl, String rw, int at, long now) {
  DEATHS.incrementAndGet();
  if (ku == null) { NOPLAYER.incrementAndGet(); return 0L; }
  if (cr) { CREATIVE.incrementAndGet(); return 0L; }
  if (pet) { PET.incrementAndGet(); return 0L; }
  boolean boss = @PKG@.MobCfg.isBoss(role) || "boss".equals(rw);
  boolean lv = lvl >= 1;
  if (!lv && !boss && !wild(att, role)) { TAME.incrementAndGet(); return 0L; }          // mobcoin1fix
  int L = lv ? lvl : at;
  if (L < 1) { NOLEVEL.incrementAndGet(); return 0L; }
  long a = amount(L, rw, boss, lv || boss);
  if (a <= 0L) return 0L;
  KILLS.incrementAndGet();
  long g = give(ku, a, now);
  if (g > 0L) tell(ku, "[Mobs] +" + fmt(g) + " coins (Lv " + L + " " + name(role) + ")", "+" + fmt(g) + " coins  Lv " + L + " " + name(role));
  return a;
}""")
M(mcoin, r"""
public static long once(java.util.UUID mob, java.util.UUID ku, boolean cr, boolean pet, String role, String att, int lvl, String rw, int at, long now) {
  if (!on() || !first(mob)) return 0L;
  return core(ku, cr, pet, role, att, lvl, rw, at, now);
}""")
# SkyySkills' LIVE party XP share (config:fn:SkyySkills "get"; cached 2 s): { fraction, radius } or null (no SkyySkills / share off / unreadable)
M(mcoin, r"""
public static double[] partyCfg(long now) {
  double[] c = PCFG;
  if (now - PCFG_AT < 2000L && now >= PCFG_AT) return c;
  double[] n = null;
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object f = b == null ? null : b.get("config:fn:SkyySkills");
    if (f instanceof java.util.function.Function) {
      java.util.function.Function g = (java.util.function.Function) f;
      Object on = g.apply(new Object[] { "get", "party.combatShare.enabled" });
      Object fr = g.apply(new Object[] { "get", "party.combatShare.fraction" });
      Object rd = g.apply(new Object[] { "get", "party.combatShare.radius" });
      if (on instanceof String && "true".equalsIgnoreCase(((String) on).trim()) && fr instanceof String && rd instanceof String) {
        double x = Double.parseDouble(((String) fr).trim());
        double r = Double.parseDouble(((String) rd).trim());
        if (x > 0.0 && x <= 1.0 && r > 0.0 && !Double.isNaN(r) && !Double.isInfinite(r)) n = new double[] { x, r };
      }
    }
  } catch (Throwable t) { n = null; }
  PCFG = n;
  PCFG_AT = now;
  return n;
}""")
# one party member's share (pure): round(amt x fr) into THEIR purse (their own cap) + their line
M(mcoin, r"""
public static long shareOne(java.util.UUID mu, String kn, long amt, double fr, long now) {
  if (mu == null || amt <= 0L || !(fr > 0.0)) return 0L;
  long m = Math.round((double) amt * (fr > 1.0 ? 1.0 : fr));
  if (m <= 0L) return 0L;
  long g = give(mu, m, now);
  if (g <= 0L) return 0L;
  PARTY.incrementAndGet();
  PARTY_PAID.addAndGet(g);
  tell(mu, "[Mobs] +" + fmt(g) + " coins (party kill" + (kn == null ? "" : " by " + kn) + ")", "+" + fmt(g) + " coins  party kill");
  return g;
}""")
M(mcoin, r"""
public static String[] members(java.util.UUID u) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object f = b == null ? null : b.get("party:fn:members");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    String[] out = new String[a.length];
    for (int i = 0; i < a.length; i++) out[i] = a[i] == null ? null : String.valueOf(a[i]);
    return out;
  } catch (Throwable t) { return null; }
}""")
# ---- the engine glue (world thread; SpoilsSys) ----
M(mcoin, r"""
public static boolean creative(@ST@ st, @REF@ r) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p != null && p.getGameMode() == @GM@.Creative;
  } catch (Throwable t) { return false; }
}""")
M(mcoin, r"""
public static @VEC@ pos(@ST@ st, @REF@ r) {
  try {
    @TC@ tc = (@TC@) st.getComponent(r, @TC@.getComponentType());
    return tc == null ? null : tc.getPosition();
  } catch (Throwable t) { return null; }
}""")
# a party member who gets a share: online, in THIS world (store), ready, alive, not Creative, within the radius of the killer
M(mcoin, r"""
public static java.util.UUID memberHere(@ST@ st, @VEC@ kp, String mid, java.util.UUID ku, double r2) {
  if (mid == null || mid.trim().length() == 0 || kp == null) return null;
  java.util.UUID mu = java.util.UUID.fromString(mid.trim());
  if (mu.equals(ku)) return null;
  @PR@ mp = @UNIV@.get().getPlayer(mu);
  if (mp == null || !mp.isValid()) return null;
  @REF@ mr = mp.getReference();
  if (mr == null || !mr.isValid() || mr.getStore() != st) return null;
  @PLA@ pl = (@PLA@) st.getComponent(mr, @PLA@.getComponentType());
  if (pl == null || pl.isWaitingForClientReady()) return null;
  if (creative(st, mr) || st.getComponent(mr, @DTHC@.getComponentType()) != null) return null;
  @VEC@ mp2 = pos(st, mr);
  if (mp2 == null) return null;
  double dx = mp2.x - kp.x;
  double dy = mp2.y - kp.y;
  double dz = mp2.z - kp.z;
  return dx * dx + dy * dy + dz * dz > r2 ? null : mu;
}""")
M(mcoin, r"""
public static int shareAll(@ST@ st, @REF@ kr, java.util.UUID ku, String kn, long amt, long now) {
  if (!@PKG@.MobCfg.COIN_PARTY || amt <= 0L || st == null || kr == null || ku == null) return 0;
  double[] pc = partyCfg(now);
  if (pc == null) return 0;
  String[] ms = members(ku);
  if (ms == null || ms.length < 2) return 0;
  @VEC@ kp = pos(st, kr);
  if (kp == null) return 0;
  double r2 = pc[1] * pc[1];
  int n = 0;
  for (int i = 0; i < ms.length; i++) {
    try {
      java.util.UUID mu = memberHere(st, kp, ms[i], ku, r2);
      if (mu != null && shareOne(mu, kn, amt, pc[0], now) > 0L) n = n + 1;
    } catch (Throwable t) { @PKG@.MobLog.warnOnce("coins:party", "kill coins: a party share failed (logged once): " + t); }
  }
  return n;
}""")
# the killing blow's player (Damage$EntitySource: a projectile's = its shooter) in this store, else null (a pet / summon / the world)
M(mcoin, r"""
public static @REF@ killerRef(Object dco, @ST@ st) {
  try {
    if (!(dco instanceof @DTHC@)) return null;
    @DMG@ d = ((@DTHC@) dco).getDeathInfo();
    if (d == null || !(d.getSource() instanceof @DENT@)) return null;
    @REF@ r = ((@DENT@) d.getSource()).getRef();
    if (r == null || !r.isValid() || r.getStore() != st) return null;
    return r;
  } catch (Throwable t) { return null; }
}""")
M(mcoin, r"""
public static boolean petOf(java.util.UUID mob) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object f = b == null ? null : b.get("pets:fn:ownerOf");
    if (!(f instanceof java.util.function.Function) || mob == null) return false;
    Object o = ((java.util.function.Function) f).apply(mob);
    return o instanceof java.util.UUID || (o instanceof String && ((String) o).trim().length() > 0);
  } catch (Throwable t) { return false; }
}""")
# the zone level at the dead mob's spot (mob:fn:levelAt's band, the middle of lo..hi), -1 = none (islands, no band)
M(mcoin, r"""
public static int levelHere(@ST@ st, @ACH@ chunk, int idx) {
  try {
    @TC@ tc = (@TC@) chunk.getComponent(idx, @TC@.getComponentType());
    @WLD@ w = @PKG@.MobLevel.worldOf(st);
    if (tc == null || w == null || tc.getPosition() == null) return -1;
    @VEC@ p = tc.getPosition();
    Object[] r = @PKG@.MobLevelAtFn.at(w, p.x, p.y, p.z, true);
    if (r == null || !(r[0] instanceof Integer) || !(r[1] instanceof Integer)) return -1;
    return (((Integer) r[0]).intValue() + ((Integer) r[1]).intValue()) / 2;
  } catch (Throwable t) { return -1; }
}""")
# mobcoin1fix: the dead mob's attitude toward players (MobLevel.attitudeOf's read), "" = unreadable
M(mcoin, r"""
public static String attOf(@ACH@ chunk, int idx) {
  try {
    @WSUP@ ws = (@WSUP@) chunk.getComponent(idx, @WSUP@.getComponentType());
    return ws == null || ws.getDefaultPlayerAttitude() == null ? "" : ws.getDefaultPlayerAttitude().name();
  } catch (Throwable t) { return ""; }
}""")
M(mcoin, r"""
public static long onDeath(Object dco, @ST@ st, @ACH@ chunk, int idx, @NPCE@ npc, java.util.UUID mob) {
  if (mob == null || npc == null || st == null || !on()) return 0L;
  if (seen(mob, System.currentTimeMillis())) return 0L;          // mobcoin1fix: a corpse ticked again refreshes its entry
  @REF@ kr = killerRef(dco, st);
  java.util.UUID ku = null;
  String kn = null;
  boolean cr = false;
  if (kr != null) {
    @PR@ pr = (@PR@) st.getComponent(kr, @PR@.getComponentType());
    if (pr != null) {
      ku = pr.getUuid();
      try { kn = pr.getUsername(); } catch (Throwable t) { kn = null; }
      cr = creative(st, kr);
    }
  }
  String role = null;
  try { role = npc.getRoleName(); } catch (Throwable t) { role = null; }
  Object mi = @PKG@.MobLevel.MOBS.get(mob);
  int lvl = mi instanceof @PKG@.MobInfo ? ((@PKG@.MobInfo) mi).level : 0;
  String rw = mi instanceof @PKG@.MobInfo ? @PKG@.MobCfg.rankWord(((@PKG@.MobInfo) mi).rank) : "";
  int at = -1;
  String att = "";
  if (ku != null && !cr && lvl < 1) { at = levelHere(st, chunk, idx); att = attOf(chunk, idx); }
  boolean pet = ku != null && !cr && petOf(mob);
  long now = System.currentTimeMillis();
  long a = once(mob, ku, cr, pet, role, att, lvl, rw, at, now);
  if (a > 0L) shareAll(st, kr, ku, kn, a, now);
  return a;
}""")
M(mcoin, r"""
public static String text() {
  long cap = (long) @PKG@.MobCfg.COIN_CAP;
  return "kill coins " + (on() ? "on" : "OFF") + " (" + @PKG@.MobCfg.COIN_BASE + " at Lv 10 x the coin curve"
      + (@PKG@.MobLevel.bridge() != null && @PKG@.MobLevel.bridge().get("coins:fn:curve") instanceof java.util.function.Function ? " (SkyyCoins)" : " (built-in)")
      + "; elite x" + @PKG@.MobCfg.COIN_ELITE + ", mini x" + @PKG@.MobCfg.COIN_MINI + ", boss x" + @PKG@.MobCfg.COIN_BOSS + "; animals " + @PKG@.MobCfg.COIN_ANIMAL
      + " %; cap " + (cap > 0L ? fmt(cap) + " / h" : "none") + "; party share " + (@PKG@.MobCfg.COIN_PARTY ? "on" : "off") + "; mob:fn:killCoins; paid " + fmt(PAID.get())
      + " on " + KILLS.get() + " kills, party " + fmt(PARTY_PAID.get()) + "; none: no player " + NOPLAYER.get() + ", creative " + CREATIVE.get() + ", pet " + PET.get()
      + ", no level " + NOLEVEL.get() + ", tame / baby / NPC " + TAME.get() + ", capped " + CAPPED.get() + ", busy " + BUSY.get() + ", failed " + FAIL.get() + ", cards held " + GATED.get() + ")";
}""")
# the bridge mob:fn:killCoins: Object[] { String roleId or null, Number level [, String rank] } -> Long (one kill at the live rows) or null
M(mcoin, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[1] instanceof Number)) return null;
    if (a[0] != null && !(a[0] instanceof String)) return null;
    String role = a[0] == null ? null : ((String) a[0]).trim();
    String rk = a.length > 2 && a[2] instanceof String ? ((String) a[2]).trim().toLowerCase(java.util.Locale.ROOT) : "";
    double d = ((Number) a[1]).doubleValue();
    if (Double.isNaN(d) || d < 1.0) return Long.valueOf(0L);
    int lv = d > 1000.0 ? 1000 : (int) d;
    boolean boss = (role != null && @PKG@.MobCfg.isBoss(role)) || "boss".equals(rk);
    return Long.valueOf(amount(lv, rk, boss, true));
  } catch (Throwable t) { return null; }
}""")
'''
P.rep('''# 0.1.25 (aug3): MobAug - the augment drops (Augments-Spec 2.4). ONE roll set per dead mob (SpoilsSys, the world thread): the items go into''',
      MC + '''# 0.1.25 (aug3): MobAug - the augment drops (Augments-Spec 2.4). ONE roll set per dead mob (SpoilsSys, the world thread): the items go into''')
# the ready text
P.rep('''+ "); " + @PKG@.MobTheme.text() + "; " + @PKG@.MobAug.text();          // 0.1.24: + the set drops; 0.1.25: + the augment drops''',
      '''+ "); " + @PKG@.MobTheme.text() + "; " + @PKG@.MobAug.text() + "; " + @PKG@.MobCoin.text();          // 0.1.24: + the set drops; 0.1.25: + the augment drops; 0.1.26: + the kill coins''')
# ---------- SpoilsSys: the gate + the kill coins (once per death, before the engine's drop gate)
P.rep('''&& !@PKG@.MobTheme.on() && !@PKG@.MobAug.on()) return;''', '''&& !@PKG@.MobTheme.on() && !@PKG@.MobAug.on() && !@PKG@.MobCoin.on()) return;''')
P.rep('''    if (npc == null) return;
    @ROLE@ role = npc.getRole();
    if (role == null || !role.hasDroppedDeathItems()) return;''', '''    if (npc == null) return;
    if (@PKG@.MobCoin.on()) {          // 0.1.26 (mobcoin1): the kill coins - once per death, BEFORE the drop gate (a mob with no drops pays too); own catch
      try {
        @UUIDC@ cu = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
        if (cu != null && cu.getUuid() != null) @PKG@.MobCoin.onDeath(chunk.getComponent(idx, @DTHC@.getComponentType()), st, chunk, idx, npc, cu.getUuid());
      } catch (Throwable tcoin) { @PKG@.MobLog.warnOnce("coins", "the kill coins failed (logged once): " + tcoin); }
    }
    @ROLE@ role = npc.getRole();
    if (role == null || !role.hasDroppedDeathItems()) return;''')
# ---------- the bridge
P.rep('''  @PKG@.MobLevel.bridge().put("mob:fn:voidAt", new @PKG@.MobVoidAtFn());   // 0.1.20 (eggs): is this block a Void place (SkyyFishing's Void catches)
''', '''  @PKG@.MobLevel.bridge().put("mob:fn:voidAt", new @PKG@.MobVoidAtFn());   // 0.1.20 (eggs): is this block a Void place (SkyyFishing's Void catches)
  @PKG@.MobLevel.bridge().put("mob:fn:killCoins", new @PKG@.MobCoin());   // 0.1.26 (mobcoin1): the coins of one kill (SkyyShards' Combat clicker)
''')
P.rep('''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10
''', '''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10
  try { @PKG@.MobLevel.bridge().remove("mob:fn:killCoins"); } catch (Throwable t) { }   // 0.1.26
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 2, "0.1.26: two new classes (MobCoin, MobRoute), no system / command"
_i = P.s.index
assert _i("RT.add_msg_route(mrte") < _i("public static String tell(java.util.UUID u, String chat") < _i("public static long core(java.util.UUID ku") < _i("public static long once(")
assert _i("public static long once(") < _i("public static long onDeath(") < _i("@PKG@.MobCoin.text()") < _i("@PKG@.MobCoin.onDeath(chunk.getComponent")
assert _i("public static Object[] at(@WLD@ w, double x") < _i("public static int levelHere(") and _i("COIN_ROW = [") < _i('["%s=%s" % (_r[0], _r[3]) for _r in COIN_ROW]')
assert _i("public static boolean wild(") < _i("public static long core(") and _i("public static boolean seen(") < _i("public static String attOf(") < _i("public static long onDeath(")
assert _i("public static boolean isBoss(String role)") < _i("public static long core(") and _i("public static String rankWord(int r)") < _i("public static long onDeath(")
P.finish()
print("wrote", P.dst)
