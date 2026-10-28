"""Derive SkyyMobs/build_skyymobs_0.1.20.py from the GENERATED 0.1.19 (build_skyymobs_0.1.19.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_19_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.19
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_20_patch.py   then   python SkyyMobs/build_skyymobs_0.1.20.py   then   python SkyyMobs/test_skyymobs_0.1.20.py
Edit THIS file, never the generated script (never --deploy).

0.1.20 (2026-10-27) = SECRET DRAGON EGG SOURCES, the SkyyMobs part (round "eggs" D5b-2, research/cloud/Secret-Dragons-Spec.md 3: V1 / B1 /
  L1). Skyy 2026-10-27: "sounds good" (the RESUME queue: secret dragon egg sources, three small rounds in Mobs, Fishing and Collections) +
  "work through your whole que"; docs/answered/pets.md 2026-10-23 SECRET DRAGON EGGS "Yes, those (Recommended)" (every chance a Server
  Setup row). SkyyPets 0.4.19+ owns the eggs, the chances (Server Setup > Pets > Dragons: pets.dragon.secret.rates void=30, blood=20 per
  10,000) and the once-per-profile rule; this mod only finds the moment and knocks on its door (plain java.lang over skyy.bridge):
  pets:fn:secretRoll {UUID, word, sourceTag} (the word's chance first) / pets:fn:giveSecretEgg (no roll). No SkyyPets (or older than
  0.4.19) = no door = nothing happens (counted, no error). The finds say nothing in chat (spec: "players figure them out"); SkyyPets
  gives the egg + its own one line.
  1. VOID (V1): every kill SpoilsSys sees (once per death) whose role matches secret.void.mobs (default "*Void*, -Void_Anomaly_Crystal*,
     -*_Tentacle_Marker": the vanilla Void mobs, not the objective crystals / the tentacle telegraph proxy) OR whose SPAWN environment
     (NPCEntity.getEnvironment) is in secret.void.places (default "Env_Void, Env_Portal_Goblin_Cave_Void, Env_Dungeon_Goblin_Void" - the
     vanilla Void world and the goblin Void portal / dungeon; NOT Env_Default_Void, the environment of every SkyyIslands island) rolls
     pets:fn:secretRoll "void" for the drop's owner (the top damager in this world, else the killer - the Spoils owner). One roll a kill.
  2. BLOOD (B1): an elite / mini boss / boss kill (its rank, or a Boss roles mob) whose LEVEL is in Zone secret.blood.zone (4) or higher
     (MobBossFn's zone tops, bosses.zoneTops), made at NIGHT in that world (WorldTimeResource.getCurrentHour inside secret.blood.night
     "21-5"; no hour = its daylight < 0.25; no clock = not night) while the drop's owner carries a Heart (secret.blood.heart
     "Ingredient_Voidheart" - the vanilla Void Heart, Drop_Voidheart; any one of the listed ids in hotbar / storage / backpack; never
     taken; "-" = no Heart needed) rolls pets:fn:secretRoll "blood".
  3. LIGHT (L1): a FULL boss (Boss roles + pack bosses = mob:fn:boss) of Zone 1..secret.light.zones (4) killed sets that zone's flag on
     the active profile of EVERY player credited on it (MobCredit - party kills count for each) + the drop's owner. All flags set = the
     door pets:fn:giveSecretEgg "light" (no roll): OK / GIVEN = the flags are cleared (run done); any other answer keeps them (the next
     guardian kill asks again). A player DEATH anywhere clears that profile's flags (new system LightDeathSys: Player + DeathComponent).
     Flags are saved per profile in Skyy_SkyyMobs/secret-light.properties (profileKey=bits, atomic write) so a run survives restarts.
  4. BRIDGE mob:fn:voidAt {String world, Number x, y, z} -> Boolean (the block's environment is in secret.void.places) or null (not the
     world's own thread / not loaded / no environment) - SkyyFishing 0.2.1's Void catches use the same list.
  5. SERVER SETUP > Mobs > Secret eggs (new tab): secret.eggs (on), secret.void.mobs, secret.void.places, secret.blood.zone,
     secret.blood.night, secret.blood.heart, secret.light.zones. New keys only (a missing line = its default) - no migration.
  SAVED DATA: Skyy_SkyyMobs/secret-light.properties (new, per-profile Light run flags). Classes MobSecret, LightDeathSys, MobVoidAtFn; one
  new system (LightDeathSys); one new bridge key (mob:fn:voidAt); no new command.
  ROLLBACK to 0.1.19: safe alone (the rows and the flag file are ignored; eggs already owed / given stay SkyyPets'). SkyyFishing 0.2.1's
  Void catches then find no mob:fn:voidAt and roll nothing.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.19.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.20.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.19"') and P.s.startswith('"""SkyyMobs 0.1.19 - build script') and P.has("migrateWc15") and not P.has("MobSecret"), "not the SET pin 0.1.19"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")
HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.20 (2026-10-27)"):].rstrip() + "\n\n"

P.rep('''"""SkyyMobs 0.1.19 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_19_patch.py from the SET pin 0.1.18 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.19.py -> SkyyMobs/SkyyMobs-0.1.19.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.19.py
''', '''"""SkyyMobs 0.1.20 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_20_patch.py from the SET pin 0.1.19 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.20.py -> SkyyMobs/SkyyMobs-0.1.20.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.20.py
''' + NOTE)
P.rep('VERSION = "0.1.19"', 'VERSION = "0.1.20"')

# ---------- 1. the defaults (Python, checked against the vanilla roles / environments / items)
P.rep('''assert not [e for e in ENV_IDS if "Volcanic" in e and e not in VOLCANIC_ENVS], "an unlisted volcanic environment exists"
''', '''assert not [e for e in ENV_IDS if "Volcanic" in e and e not in VOLCANIC_ENVS], "an unlisted volcanic environment exists"
# 0.1.20 (eggs, Secret-Dragons-Spec 3): the secret dragon egg finds - defaults checked against Assets.zip
SEC_VM_DEF = "*Void*, -Void_Anomaly_Crystal*, -*_Tentacle_Marker"
SEC_VP_DEF = "Env_Void, Env_Portal_Goblin_Cave_Void, Env_Dungeon_Goblin_Void"
SEC_BH_DEF = "Ingredient_Voidheart"
SEC_BN_DEF = "21-5"
SEC_BZ_DEF = 4
SEC_LZ_DEF = 4


def sec_hit(txt, s):
    """the Python mirror of MobSecret.hit(pats(txt), s): any plain pattern matches and no -pattern does"""
    inc = [p.strip() for p in txt.split(",") if p.strip() and not p.strip().startswith("-")]
    exc = [p.strip()[1:].strip() for p in txt.split(",") if p.strip().startswith("-")]
    return any(glob(p, s) for p in inc) and not any(glob(p, s) for p in exc)


_SEC_ROLES = [_n.rsplit("/", 1)[1][:-5] for _n in AZ_NAMES if _n.startswith("Server/NPC/Roles/") and _n.endswith(".json")]
_SEC_V = sorted(set(_r for _r in _SEC_ROLES if sec_hit(SEC_VM_DEF, _r) and not _r.startswith(("Template_", "Component_", "Test_", "Cinematic_"))))
for _r in ("Crawler_Void", "Void_Spectre", "Void_Spawn", "Eye_Void", "Larva_Void", "Bear_Voidtaken", "Void_Tentacle", "Golem_Guardian_Void"):
    assert _r in _SEC_V, "0.1.20: %s should roll the Void egg" % _r
for _r in ("Void_Anomaly_Crystal_Small", "Void_Anomaly_Crystal_Keystone", "Bear_Voidtaken_Tentacle_Marker", "Skeleton", "Trork_Warrior"):
    assert not sec_hit(SEC_VM_DEF, _r), "0.1.20: %s must not roll the Void egg" % _r
_SEC_P = [_e.strip() for _e in SEC_VP_DEF.split(",")]
assert all(_e in ENV_IDS for _e in _SEC_P) and "Env_Default_Void" in ENV_IDS and not sec_hit(SEC_VP_DEF, "Env_Default_Void"), \\
    "0.1.20: the Void places are real environments; SkyyIslands' Env_Default_Void (every island) is not one"
assert "Server/Item/Items/Ingredient/" + SEC_BH_DEF + ".json" in AZ_NAMES, "0.1.20: the Heart item is vanilla"
print("0.1.20 secret eggs: Void = %d vanilla roles (%s ...) + places %s; Blood = Zone %d+ elites at night %s with %s; Light = Zone 1-%d bosses"
      % (len(_SEC_V), ", ".join(_SEC_V[:6]), SEC_VP_DEF, SEC_BZ_DEF, SEC_BN_DEF, SEC_BH_DEF, SEC_LZ_DEF))
''')
P.rep('''              "bosses.dragonEggs=" + DEGG_DEF, "bosses.dragonEggChance=%g" % DEGG_CHANCE]          # 0.1.18 (absent in an older file = the default)''',
      '''              "bosses.dragonEggs=" + DEGG_DEF, "bosses.dragonEggChance=%g" % DEGG_CHANCE]          # 0.1.18 (absent in an older file = the default)
CFG_LINES += ["# Secret dragon eggs (SkyyMobs 0.1.20; the eggs, chances and one-per-profile rule are SkyyPets' - Server Setup > Pets > Dragons):",
              "# Void = a kill of a secret.void.mobs role or of a mob born in a secret.void.places environment; Blood = an elite / boss of Zone",
              "# secret.blood.zone+ at night (game hours secret.blood.night) with a secret.blood.heart item in the bag; Light = a boss of every",
              "# Zone 1..secret.light.zones without dying in between. -Pattern leaves a role / environment out.",
              "secret.eggs=true", "secret.void.mobs=" + SEC_VM_DEF, "secret.void.places=" + SEC_VP_DEF, "secret.blood.zone=%d" % SEC_BZ_DEF,
              "secret.blood.night=" + SEC_BN_DEF, "secret.blood.heart=" + SEC_BH_DEF, "secret.light.zones=%d" % SEC_LZ_DEF]          # 0.1.20''')

# ---------- 2. the rows (new tab Secret eggs, after Elements)
P.rep('''CFG_CATS.insert(CFG_CATS.index(("rank", "Ranks")) + 1, ("elem", "Elements"))''',
      '''CFG_CATS.insert(CFG_CATS.index(("rank", "Ranks")) + 1, ("elem", "Elements"))
CFG_CATS.insert(CFG_CATS.index(("elem", "Elements")) + 1, ("secret", "Secret eggs"))          # 0.1.20''')
P.rep('''     "Per boss kill, rolled once. Never above SkyyGear's Boss Mythic bag chance (max 12 %).", "field:MobCfg.DEGG_CHANCE"),
]''', '''     "Per boss kill, rolled once. Never above SkyyGear's Boss Mythic bag chance (max 12 %).", "field:MobCfg.DEGG_CHANCE"),
]
# 0.1.20 (eggs): the secret dragon egg finds (the chances live in SkyyPets: Server Setup > Pets > Dragons)
SEC_ROWS = [
    ("secret.eggs", "Secret dragon egg finds", "secret", "bool", "true", "", "", "", "", "live",
     "Kills may find SkyyPets' secret dragon eggs. Chances: Server Setup > Pets > Dragons.", "field:MobCfg.SEC_ON"),
    ("secret.void.mobs", "Void egg mobs", "secret", "text", SEC_VM_DEF, "", "400", "", "", "live",
     "Roles, *Part* ok, comma separated; -Pattern leaves one out. Each kill rolls the Void egg.", "field:MobCfg.SEC_VMOBS"),
    ("secret.void.places", "Void egg places", "secret", "text", SEC_VP_DEF, "", "400", "", "", "live",
     "Environment ids: mobs born there and fish caught there roll the Void egg. -Pattern = leave out.", "field:MobCfg.SEC_VPLACES"),
    ("secret.blood.zone", "Blood egg lowest zone", "secret", "int", str(SEC_BZ_DEF), "1", "5", "", "", "live",
     "Elite / mini boss / boss kills from this zone up, at night, with a Heart item in the bag.", "field:MobCfg.SEC_BZONE"),
    ("secret.blood.night", "Blood egg night hours", "secret", "text", SEC_BN_DEF, "", "7", "", "", "live",
     "Game hours start-end: 21-5 = from 9 pm to 5 am.", "field:MobCfg.SEC_BNIGHT;check=MobSecret.checkNight"),
    ("secret.blood.heart", "Blood egg Heart items", "secret", "text", SEC_BH_DEF, "", "400", "", "", "live",
     "Item ids, comma separated; one must be in the bag (never taken). - = no Heart needed.", "field:MobCfg.SEC_BHEART"),
    ("secret.light.zones", "Light egg guardian zones", "secret", "int", str(SEC_LZ_DEF), "1", "5", "", "", "live",
     "Beat a boss of every Zone 1 to this one without dying in between = the Light egg.", "field:MobCfg.SEC_LZONES"),
]
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in SEC_ROWS), [(len(_r[1]), len(_r[10])) for _r in SEC_ROWS]
CFG_ROWS += SEC_ROWS''')

# ---------- 3. MobCfg fields + load
P.rep('''for f in ("public static volatile String DEGG_TXT = %s;" % jstr(DEGG_DEF), "public static volatile double DEGG_CHANCE = %s;" % repr(DEGG_CHANCE)):
    F(cfg, f)
''', '''for f in ("public static volatile String DEGG_TXT = %s;" % jstr(DEGG_DEF), "public static volatile double DEGG_CHANCE = %s;" % repr(DEGG_CHANCE)):
    F(cfg, f)
# 0.1.20 (eggs): the secret dragon egg finds
for f in ("public static volatile boolean SEC_ON = true;", "public static volatile String SEC_VMOBS = %s;" % jstr(SEC_VM_DEF),
          "public static volatile String SEC_VPLACES = %s;" % jstr(SEC_VP_DEF), "public static volatile int SEC_BZONE = %d;" % SEC_BZ_DEF,
          "public static volatile String SEC_BNIGHT = %s;" % jstr(SEC_BN_DEF), "public static volatile String SEC_BHEART = %s;" % jstr(SEC_BH_DEF),
          "public static volatile int SEC_LZONES = %d;" % SEC_LZ_DEF):
    F(cfg, f)
''')
P.rep('''  DEGG_CHANCE = dec(c.getProperty("bosses.dragonEggChance"), @DEGGCH@, 0.0, @DEGGMX@);''',
      '''  DEGG_CHANCE = dec(c.getProperty("bosses.dragonEggChance"), @DEGGCH@, 0.0, @DEGGMX@);
  SEC_ON = bool(c.getProperty("secret.eggs"), true);          // 0.1.20: the secret egg finds (a file without a line = the default)
  SEC_VMOBS = c.getProperty("secret.void.mobs", @SECVM@).trim();
  SEC_VPLACES = c.getProperty("secret.void.places", @SECVP@).trim();
  SEC_BZONE = intOf(c.getProperty("secret.blood.zone"), @SECBZ@, 1, 5);
  SEC_BNIGHT = c.getProperty("secret.blood.night", @SECBN@).trim();
  SEC_BHEART = c.getProperty("secret.blood.heart", @SECBH@).trim();
  SEC_LZONES = intOf(c.getProperty("secret.light.zones"), @SECLZ@, 1, 5);''')
P.rep('''.replace("@DEGGCH@", repr(DEGG_CHANCE)).replace("@DEGGMX@", repr(DEGG_MAX))          # 0.1.17''',
      '''.replace("@DEGGCH@", repr(DEGG_CHANCE)).replace("@DEGGMX@", repr(DEGG_MAX)) \\
   .replace("@SECVM@", jstr(SEC_VM_DEF)).replace("@SECVP@", jstr(SEC_VP_DEF)).replace("@SECBZ@", str(SEC_BZ_DEF)).replace("@SECBN@", jstr(SEC_BN_DEF)) \\
   .replace("@SECBH@", jstr(SEC_BH_DEF)).replace("@SECLZ@", str(SEC_LZ_DEF))          # 0.1.17; 0.1.20''')

# ---------- 4. engine classes + probes
P.rep('''          "ITMA": "com.hypixel.hytale.server.core.asset.type.item.config.Item"})''',
      '''          "ITMA": "com.hypixel.hytale.server.core.asset.type.item.config.Item"})
T.update({"PLA": "com.hypixel.hytale.server.core.entity.entities.Player",          # 0.1.20 (eggs): the Blood egg's Heart check + LightDeathSys
          "INVT": "com.hypixel.hytale.server.core.inventory.Inventory",
          "ICON": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
          "WTR": "com.hypixel.hytale.server.core.modules.time.WorldTimeResource"})          # the night check (the SkyyFishing / SkyyShards clock)''')
P.rep('''for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)''', '''# 0.1.20 (eggs): the night (WorldTimeResource), the Heart in the bag (Player inventory), the player death system
SIGS += [(G["ST"], "getResource", "com.hypixel.hytale.component.Resource", ["com.hypixel.hytale.component.ResourceType"]),
         (G["WTR"], "getResourceType", "com.hypixel.hytale.component.ResourceType", []), (G["WTR"], "getCurrentHour", "int", []),
         (G["WTR"], "getSunlightFactor", "double", []), (G["PLA"], "getComponentType", G["CTYPE"], []),
         (G["ST"], "getComponent", G["COMP"], [G["REF"], G["CTYPE"]]), (G["REF"], "isValid", "boolean", []),
         (G["NPCE"], "getEnvironment", "int", [])]
for _c, _m in ((G["PLA"], "getInventory"), (G["INVT"], "getStorage"), (G["INVT"], "getBackpack"), (G["INVT"], "getHotbar"),
               (G["ICON"], "getCapacity"), (G["ICON"], "getItemStack")):
    B.probe(pool, _c, _m)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _m))
for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)''')

# ---------- 5. the classes
P.rep('''megg = pool.makeClass(PKG + ".MobEgg")       # 0.1.18 (dragond1): the boss dragon eggs (bosses.dragonEggs; SpoilsSys rolls it)   # 0.1.17: mob:fn:elemOf''',
      '''megg = pool.makeClass(PKG + ".MobEgg")       # 0.1.18 (dragond1): the boss dragon eggs (bosses.dragonEggs; SpoilsSys rolls it)   # 0.1.17: mob:fn:elemOf
msec = pool.makeClass(PKG + ".MobSecret")    # 0.1.20 (eggs): the secret dragon egg finds (SpoilsSys calls onKill)
mlds = pool.makeClass(PKG + ".LightDeathSys", pool.get(G["ETS"]))   # 0.1.20: a player death clears the Light run flags
mvat = pool.makeClass(PKG + ".MobVoidAtFn")  # 0.1.20: mob:fn:voidAt (SkyyFishing's Void catches)''')
P.rep('''msp, mss, mel, mef, meo, megg]''', '''msp, mss, mel, mef, meo, megg, msec, mlds, mvat]''')

MSEC = r'''# ================================================================= 0.1.20 MobSecret: the secret dragon egg finds (tools/mobs_0_1_20_patch.py
# docstring). SkyyPets owns the eggs, chances and once-per-profile rule; this class finds the moment and asks its door. Harness seams:
# ROLL_API / GIVE_API (the doors), HEART_API (UUID -> Boolean), HOUR_TEST (>= 0 = this hour, -2 = no clock); all null / -1 in the game.
for _f in ("public static volatile String VM_TXT = null;", "public static volatile Object[] VM = null;",
           "public static volatile String VP_TXT = null;", "public static volatile Object[] VP = null;",
           "public static volatile String HT_TXT = null;", "public static volatile String[] HT = null;",
           "public static final java.util.concurrent.ConcurrentHashMap LIGHT = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap DEADAT = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile java.nio.file.Path FILE = null;",
           "public static volatile java.util.function.Function ROLL_API = null;", "public static volatile java.util.function.Function GIVE_API = null;",
           "public static volatile java.util.function.Function HEART_API = null;", "public static volatile int HOUR_TEST = -1;",
           "public static volatile long VOIDS = 0L;", "public static volatile long BLOODS = 0L;", "public static volatile long LIGHTS = 0L;",
           "public static volatile long FLAGS = 0L;", "public static volatile long FOUND = 0L;", "public static volatile long NODOOR = 0L;",
           "public static volatile long CLEARS = 0L;"):
    F(msec, _f)
# "a, -b, *c*" -> { String[] plain (lower), String[] left out (lower) }; a lone * is skipped (it would match everything)
M(msec, r"""
public static Object[] pats(String v) {
  java.util.ArrayList inc = new java.util.ArrayList();
  java.util.ArrayList exc = new java.util.ArrayList();
  if (v != null) {
    String[] ps = v.split(",");
    for (int i = 0; i < ps.length; i++) {
      String t = ps[i].trim().toLowerCase();
      boolean neg = t.startsWith("-");
      if (neg) t = t.substring(1).trim();
      if (t.length() == 0 || @PKG@.MobGlob.spec(t) == 0) continue;
      if (neg) exc.add(t); else inc.add(t);
    }
  }
  String[] a = new String[inc.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) inc.get(i);
  String[] b = new String[exc.size()];
  for (int i = 0; i < b.length; i++) b[i] = (String) exc.get(i);
  return new Object[] { a, b };
}""")
M(msec, r"""
public static boolean hit(Object[] p, String s) {
  if (p == null || s == null || s.length() == 0) return false;
  String k = s.toLowerCase();
  String[] a = (String[]) p[0];
  String[] b = (String[]) p[1];
  boolean in = false;
  for (int i = 0; i < a.length && !in; i++) if (@PKG@.MobGlob.glob(a[i], k)) in = true;
  if (!in) return false;
  for (int i = 0; i < b.length; i++) if (@PKG@.MobGlob.glob(b[i], k)) return false;
  return true;
}""")
M(msec, r"""
public static boolean voidMob(String role) {
  String t = @PKG@.MobCfg.SEC_VMOBS;
  Object[] p = VM;
  if (p == null || t != VM_TXT) { p = pats(t); VM = p; VM_TXT = t; }
  return hit(p, role == null ? null : role.trim());
}""")
M(msec, r"""
public static boolean voidPlace(String env) {
  String t = @PKG@.MobCfg.SEC_VPLACES;
  Object[] p = VP;
  if (p == null || t != VP_TXT) { p = pats(t); VP = p; VP_TXT = t; }
  return hit(p, env);
}""")
# "21-5" -> { 21, 5 } (0-23 each); null = bad
M(msec, r"""
public static int[] night(String v) {
  if (v == null) return null;
  String t = v.trim();
  int q = t.indexOf('-');
  if (q <= 0 || q >= t.length() - 1) return null;
  try {
    int a = Integer.parseInt(t.substring(0, q).trim());
    int b = Integer.parseInt(t.substring(q + 1).trim());
    if (a < 0 || a > 23 || b < 0 || b > 23 || a == b) return null;
    return new int[] { a, b };
  } catch (Throwable x) { return null; }
}""")
M(msec, r"""
public static String checkNight(String key, String value) {
  if (value == null) return null;
  return night(value) == null ? "Type two game hours 0-23 as start-end, like 21-5 (from 9 pm to 5 am)." : null;
}""")
M(msec, r"""
public static boolean isNightHour(int h, String v) {
  int[] n = night(v);
  if (n == null) n = night(@SECBN@);
  if (h < 0 || h > 23 || n == null) return false;
  return n[0] < n[1] ? (h >= n[0] && h < n[1]) : (h >= n[0] || h < n[1]);
}""".replace("@SECBN@", jstr(SEC_BN_DEF)))
# 1 = night, 0 = day, -1 = no clock (never night) - the world's WorldTimeResource hour, else its daylight (< 0.25 = night)
M(msec, r"""
public static int nightAt(@ST@ st) {
  int ht = HOUR_TEST;
  if (ht >= 0) return isNightHour(ht, @PKG@.MobCfg.SEC_BNIGHT) ? 1 : 0;
  if (ht == -2 || st == null) return -1;
  try {
    Object r = st.getResource(@WTR@.getResourceType());
    if (!(r instanceof @WTR@)) return -1;
    @WTR@ c = (@WTR@) r;
    int h = c.getCurrentHour();
    if (h >= 0 && h <= 23) return isNightHour(h, @PKG@.MobCfg.SEC_BNIGHT) ? 1 : 0;
    double s = c.getSunlightFactor();
    if (s >= 0.0) return s < 0.25 ? 1 : 0;
  } catch (Throwable t) { }
  return -1;
}""")
# the Heart ids (secret.blood.heart; "-" / blank = none needed = String[0])
M(msec, r"""
public static String[] hearts() {
  String t = @PKG@.MobCfg.SEC_BHEART;
  String[] h = HT;
  if (h != null && t == HT_TXT) return h;
  java.util.ArrayList l = new java.util.ArrayList();
  if (t != null && !t.trim().equals("-")) {
    String[] ps = t.split(",");
    for (int i = 0; i < ps.length; i++) { String x = ps[i].trim(); if (x.length() > 0 && !x.equals("-")) l.add(x); }
  }
  h = new String[l.size()];
  for (int i = 0; i < h.length; i++) h[i] = (String) l.get(i);
  HT = h;
  HT_TXT = t;
  return h;
}""")
# does this player (in THIS world's store - the world thread) carry one of the Heart ids in hotbar / storage / backpack? Never takes it.
M(msec, r"""
public static boolean heart(java.util.UUID u, @ST@ st) {
  String[] ids = hearts();
  if (ids.length == 0) return true;
  if (u == null) return false;
  java.util.function.Function f = HEART_API;
  if (f != null) return Boolean.TRUE.equals(f.apply(u));
  try {
    @PR@ pr = @UNIV@.get().getPlayer(u);
    if (pr == null) return false;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid() || r.getStore() != st) return false;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return false;
    @INVT@ inv = p.getInventory();
    if (inv == null) return false;
    @ICON@[] cs = new @ICON@[] { inv.getHotbar(), inv.getStorage(), inv.getBackpack() };
    for (int k = 0; k < cs.length; k++) {
      @ICON@ c = cs[k];
      if (c == null) continue;
      int n = c.getCapacity();
      for (int i = 0; i < n; i++) {
        @ISTK@ x = c.getItemStack((short) i);
        if (x == null || x.isEmpty()) continue;
        String id = x.getItemId();
        for (int j = 0; j < ids.length; j++) if (ids[j].equalsIgnoreCase(id)) return true;
      }
    }
  } catch (Throwable t) { }
  return false;
}""")
# SkyyPets' doors (pets:fn:secretRoll / pets:fn:giveSecretEgg, 0.4.19+); null = no SkyyPets / an older one (nothing happens)
M(msec, r"""
public static java.util.function.Function door(boolean roll) {
  Object f = roll ? ROLL_API : GIVE_API;
  if (f == null) {
    try { f = @PKG@.MobLevel.bridge().get(roll ? "pets:fn:secretRoll" : "pets:fn:giveSecretEgg"); } catch (Throwable t) { f = null; }
  }
  return f instanceof java.util.function.Function ? (java.util.function.Function) f : null;
}""")
# the answer code ("OK", "MISS", "GIVEN", "HAS_DRAGON", "HAS_EGG", "OFF", "BUSY" ...) or null = no door; never throws, never tells the player
M(msec, r"""
public static String ask(boolean roll, java.util.UUID u, String word, String src) {
  if (u == null) return null;
  java.util.function.Function f = door(roll);
  if (f == null) { NODOOR = NODOOR + 1L; return null; }
  try {
    Object r = f.apply(new Object[] { u, word, src });
    String c = r == null ? null : String.valueOf(r);
    if ("OK".equals(c)) { FOUND = FOUND + 1L; @PKG@.MobLog.info("secret " + word + " egg found by " + u + " (" + src + ") - SkyyPets delivers it"); }
    return c;
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("secretdoor", "the SkyyPets secret egg door failed (logged once): " + t); return null; }
}""")
M(msec, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = @PKG@.MobLevel.bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(msec, r"""
public static int zoneOf(int lv) {
  int[] tops = @PKG@.MobCfg.BOSS_TOP;
  if (tops == null || tops.length == 0 || lv < 1) return 0;
  for (int i = 0; i < tops.length; i++) if (tops[i] >= lv) return i + 1;
  return tops.length;
}""")
# ---- the Light run flags (per profile key: bit z-1 = a Zone z guardian beaten), Skyy_SkyyMobs/secret-light.properties
M(msec, r"""
public static void load(java.nio.file.Path dir) {
  LIGHT.clear();
  DEADAT.clear();
  if (dir == null) return;
  FILE = dir.resolve("secret-light.properties");
  try {
    if (!java.nio.file.Files.isRegularFile(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.ByteArrayInputStream(java.nio.file.Files.readAllBytes(FILE)));
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      int m = @PKG@.MobCfg.intOf(p.getProperty(k), 0, 0, 31);
      if (m > 0) LIGHT.put(k, Integer.valueOf(m));
    }
  } catch (Throwable t) { @PKG@.MobLog.warn("could not read " + FILE + " - the Light run flags start empty: " + t); }
}""")
M(msec, r"""
public static synchronized boolean save() {
  java.nio.file.Path f = FILE;
  if (f == null) return false;
  try {
    java.util.Properties p = new java.util.Properties();
    Object[] ks = LIGHT.keySet().toArray();
    for (int i = 0; i < ks.length; i++) { Object v = LIGHT.get(ks[i]); if (v != null) p.setProperty(String.valueOf(ks[i]), String.valueOf(v)); }
    java.io.StringWriter sw = new java.io.StringWriter();
    p.store(sw, "SkyyMobs Light run flags per profile (1 = a Zone 1 guardian beaten, 2 = Zone 2, 4 = Zone 3, 8 = Zone 4, 16 = Zone 5); a death clears the line");
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, sw.toString().getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    return true;
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("secretsave", "could not save the Light run flags (logged once): " + t); return false; }
}""")
M(msec, r"""
public static int need() {
  int z = @PKG@.MobCfg.SEC_LZONES;
  if (z < 1) z = 1;
  if (z > 5) z = 5;
  return (1 << z) - 1;
}""")
M(msec, r"""
public static int maskOf(String key) {
  if (key == null) return 0;
  Object o = LIGHT.get(key);
  return o instanceof Integer ? ((Integer) o).intValue() : 0;
}""")
# a Zone z guardian beaten by u (credited): set the flag; all flags = the Light egg's door (no roll); OK / GIVEN = the run is done (cleared)
M(msec, r"""
public static String light(java.util.UUID u, int zone) {
  if (u == null || zone < 1 || zone > 5) return null;
  int nd = need();
  int bit = 1 << (zone - 1);
  if ((bit & nd) == 0) return null;
  String key = pkey(u);
  int m0 = maskOf(key);
  int m = m0 | bit;
  if (m != m0) { LIGHT.put(key, Integer.valueOf(m)); FLAGS = FLAGS + 1L; save(); }
  if ((m & nd) != nd) return "FLAG";
  LIGHTS = LIGHTS + 1L;
  String c = ask(false, u, "light", "SkyyMobs:light-run");
  if ("OK".equals(c) || "GIVEN".equals(c)) { LIGHT.remove(key); save(); }
  return c == null ? "NODOOR" : c;
}""")
# a player death (LightDeathSys, every tick while dead - throttled to once per 3 s a player): clears the active profile's flags
M(msec, r"""
public static boolean died(java.util.UUID u, long now) {
  if (u == null || LIGHT.isEmpty()) return false;
  Object t = DEADAT.get(u);
  if (t instanceof Long && now - ((Long) t).longValue() < 3000L) return false;
  if (DEADAT.size() > 512) DEADAT.clear();
  DEADAT.put(u, Long.valueOf(now));
  if (LIGHT.remove(pkey(u)) == null) return false;
  CLEARS = CLEARS + 1L;
  save();
  return true;
}""")
M(msec, r"""
public static java.util.UUID uuid(String s) {
  if (s == null) return null;
  try { return java.util.UUID.fromString(s.trim()); } catch (Throwable t) { return null; }
}""")
# every player credited on the mob (MobCredit, read only) + the drop's owner, once each
M(msec, r"""
public static java.util.UUID[] credited(java.util.UUID mob, java.util.UUID ku) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (ku != null) l.add(ku);
  Object[] c = null;
  if (mob != null) c = @PKG@.MobCredit.sharesOf(mob.toString());
  if (c != null && c.length >= 1 && c[0] instanceof String[]) {
    String[] w = (String[]) c[0];
    for (int i = 0; i < w.length; i++) { java.util.UUID p = uuid(w[i]); if (p != null && !l.contains(p)) l.add(p); }
  }
  java.util.UUID[] a = new java.util.UUID[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (java.util.UUID) l.get(i);
  return a;
}""")
# ONE dead mob (SpoilsSys, the world thread, once per death): the Void roll, the Blood roll, the Light flags. Returns a short trace (harness).
M(msec, r"""
public static String onKill(@ST@ st, String role, String env, int lvl, String rw, java.util.UUID mob, java.util.UUID ku) {
  if (!@PKG@.MobCfg.SEC_ON || role == null || ku == null) return "";
  StringBuilder b = new StringBuilder();
  if (voidMob(role) || voidPlace(env)) {
    VOIDS = VOIDS + 1L;
    b.append("void=").append(ask(true, ku, "void", "SkyyMobs:void-kill " + role)).append(' ');
  }
  int zone = zoneOf(lvl);
  boolean boss = @PKG@.MobCfg.isBoss(role);
  boolean big = boss || (rw != null && rw.length() > 0);
  if (big && zone >= @PKG@.MobCfg.SEC_BZONE && nightAt(st) == 1 && heart(ku, st)) {
    BLOODS = BLOODS + 1L;
    b.append("blood=").append(ask(true, ku, "blood", "SkyyMobs:blood-night " + role)).append(' ');
  }
  if (boss && zone >= 1) {
    java.util.UUID[] who = credited(mob, ku);
    for (int i = 0; i < who.length; i++) b.append("light=").append(light(who[i], zone)).append(' ');
  }
  return b.toString().trim();
}""")
M(msec, r"""
public static String text() {
  String[] h = hearts();
  return "secret eggs " + (@PKG@.MobCfg.SEC_ON ? "on" : "OFF") + " (SkyyPets' pets:fn:secretRoll / giveSecretEgg " + (door(true) != null ? "found" : "not loaded yet")
      + "; Blood Zone " + @PKG@.MobCfg.SEC_BZONE + "+ at night " + @PKG@.MobCfg.SEC_BNIGHT + (h.length == 0 ? " (no Heart needed)" : " with a Heart")
      + "; Light Zones 1-" + @PKG@.MobCfg.SEC_LZONES + ", " + LIGHT.size() + " runs saved; void " + VOIDS + ", blood " + BLOODS + ", light " + LIGHTS
      + ", found " + FOUND + (NODOOR > 0L ? ", no door " + NODOOR : "") + ", deaths cleared " + CLEARS + "; mob:fn:voidAt)";
}""")

# ================================================================= 0.1.20 mob:fn:voidAt (bridge, the world's own thread only, never throws)
# Object[]{ String world, Number x, Number y, Number z } -> Boolean (the block's environment is in secret.void.places) | null (other
# thread / not loaded / no environment)
mvat.addInterface(pool.get("java.util.function.Function"))
C(mvat, "public MobVoidAtFn() { }")
M(mvat, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 4 || !(a[0] instanceof String) || !(a[1] instanceof Number) || !(a[2] instanceof Number) || !(a[3] instanceof Number)) return null;
    double x = ((Number) a[1]).doubleValue(), y = ((Number) a[2]).doubleValue(), z = ((Number) a[3]).doubleValue();
    if (Double.isNaN(x) || Double.isNaN(y) || Double.isNaN(z) || Math.abs(x) > 1.0E8 || Math.abs(z) > 1.0E8 || Math.abs(y) > 1.0E5) return null;
    @WLD@ w = @PKG@.MobLevelAtFn.world((String) a[0]);
    if (w == null || !@PKG@.MobLevelAtFn.onThread(w)) return null;
    String e = @PKG@.MobLevel.envId(@PKG@.MobLevel.blockEnv(w, (int) Math.floor(x), (int) Math.floor(y), (int) Math.floor(z)));
    if (e == null) return null;
    return @PKG@.MobSecret.voidPlace(e) ? Boolean.TRUE : Boolean.FALSE;
  } catch (Throwable t) { return null; }
}""")

'''
P.rep('''# ================================================================= 0.1.15 MobSpoils + SpoilsSys: the Combat tree's Spoils rows (Balance P8b)''',
      MSEC + '''# ================================================================= 0.1.15 MobSpoils + SpoilsSys: the Combat tree's Spoils rows (Balance P8b)''')

# ---------- 6. SpoilsSys: the secret finds (independent of the Spoils rows and the dragon eggs)
P.rep('''    if (!@PKG@.MobSpoils.ON && !(@PKG@.MobCfg.DEGG_CHANCE > 0.0)) return;          // 0.1.18: + the boss dragon eggs''',
      '''    if (!@PKG@.MobSpoils.ON && !(@PKG@.MobCfg.DEGG_CHANCE > 0.0) && !@PKG@.MobCfg.SEC_ON) return;          // 0.1.18: + the boss dragon eggs; 0.1.20: + the secret finds''')
P.rep('''    @PKG@.MobEgg.dropped(ku, egg, sp);          // 0.1.18 review fix: the egg's chat line only once the drop is in the world
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("spoils",''', '''    @PKG@.MobEgg.dropped(ku, egg, sp);          // 0.1.18 review fix: the egg's chat line only once the drop is in the world
    try {          // 0.1.20 (eggs): the secret dragon egg finds (Void / Blood / Light) - their own failure never stops the Spoils
      int ei = Integer.MIN_VALUE;
      try { ei = npc.getEnvironment(); } catch (Throwable te) { ei = Integer.MIN_VALUE; }
      @PKG@.MobSecret.onKill(st, npc.getRoleName(), @PKG@.MobLevel.envId(ei), lvl, rw, mob, ku);
    } catch (Throwable ts) { @PKG@.MobLog.warnOnce("secret", "the secret egg finds failed (logged once): " + ts); }
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("spoils",''')

# ---------- 7. LightDeathSys (after SpoilsSys): Player + DeathComponent, every tick while dead (MobSecret.died throttles)
P.rep('''# ================================================================= 0.1.7 mob:fn:credit (bridge, any thread, never throws)''',
      '''# ================================================================= 0.1.20 LightDeathSys: a player death clears the Light run flags (MobSecret.died)
F(mlds, "public java.util.Set deps;")
C(mlds, "public LightDeathSys() { super(); this.deps = new java.util.HashSet(); }")
M(mlds, "public @QRY@ getQuery() { return @QRY@.and(new @QRY@[] { (@QRY@) @PLA@.getComponentType(), (@QRY@) @DTHC@.getComponentType() }); }")
M(mlds, "public java.util.Set getDependencies() { return this.deps; }")
M(mlds, "public boolean isParallel(int a, int b) { return false; }")
M(mlds, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ st, @CB@ cb) {
  try {
    if (@PKG@.MobSecret.LIGHT.isEmpty()) return;
    @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return;
    @PKG@.MobSecret.died(uc.getUuid(), System.currentTimeMillis());
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("lightdeath", "the Light run death check failed (logged once): " + t); }
}""")

# ================================================================= 0.1.7 mob:fn:credit (bridge, any thread, never throws)''')

# ---------- 8. plugin: register, load, bridge, ready line, shutdown
P.rep('''    catch (Throwable t8) { @PKG@.MobSpoils.SYS_ON = false; @PKG@.MobLog.warn("the Spoils death system could not be ordered after DropDeathItems (" + t8 + ") - the Combat tree's Spoils rows give nothing this start"); }
  }
}""" % (ROLEB, SETUPS, BALS, ADRS))''', '''    catch (Throwable t8) { @PKG@.MobSpoils.SYS_ON = false; @PKG@.MobLog.warn("the Spoils death system could not be ordered after DropDeathItems (" + t8 + ") - the Combat tree's Spoils rows give nothing this start"); }
  }
  // 0.1.20 (eggs): a player death clears the Light run flags (ONE registerSystem); not registered = deaths do not reset a run this start
  try { getEntityStoreRegistry().registerSystem(new @PKG@.LightDeathSys()); }
  catch (Throwable t9) { @PKG@.MobLog.warn("the Light run death check could not be registered (" + t9 + ") - this start a death does not clear the Light egg flags"); }
}""" % (ROLEB, SETUPS, BALS, ADRS))''')
P.rep('''  String spt = @PKG@.MobSpoils.loadV3(dir);   // 0.1.15 (Balance P8b): the Spoils rows' numbers (trees.properties, seeded when missing)
''', '''  String spt = @PKG@.MobSpoils.loadV3(dir);   // 0.1.15 (Balance P8b): the Spoils rows' numbers (trees.properties, seeded when missing)
  @PKG@.MobSecret.load(dir);   // 0.1.20 (eggs): the Light run flags (secret-light.properties; missing = none)
''')
P.rep('''  @PKG@.MobLevel.bridge().put("mob:fn:elemOf", new @PKG@.MobElemOfFn());   // 0.1.17: a role's own element
''', '''  @PKG@.MobLevel.bridge().put("mob:fn:elemOf", new @PKG@.MobElemOfFn());   // 0.1.17: a role's own element
  @PKG@.MobLevel.bridge().put("mob:fn:voidAt", new @PKG@.MobVoidAtFn());   // 0.1.20 (eggs): is this block a Void place (SkyyFishing's Void catches)
''')
P.rep('''+ "; " + @PKG@.MobEgg.text() + "; /mobs;''', '''+ "; " + @PKG@.MobEgg.text() + "; " + @PKG@.MobSecret.text() + "; /mobs;''')
P.rep('''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10
''', '''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10
  try { @PKG@.MobLevel.bridge().remove("mob:fn:voidAt"); @PKG@.MobSecret.save(); @PKG@.MobSecret.DEADAT.clear(); } catch (Throwable t) { }   // 0.1.20
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 + 1 and P.s.count("makeClass(") == CLS0 + 3, "0.1.20: 3 classes, 1 system, no command"
_i = P.s.index
assert _i("public static Object[] sharesOf(String mob)") < _i("public static java.util.UUID[] credited(") < _i("public static String onKill(@ST@ st") \
    < _i("@PKG@.MobSecret.onKill(st, npc.getRoleName()") < _i("@PKG@.MobSecret.died(uc.getUuid()"), "0.1.20: methods before callers"
assert _i("public static String envId(int idx)") < _i("public static String onKill(") and _i("public static int blockEnv(") < _i("public MobVoidAtFn()")
assert _i("public static boolean onThread(@WLD@ w)") < _i("public MobVoidAtFn()") and _i("public static boolean isBoss(String role)") < _i("public static String onKill(")
P.finish()
print("wrote", P.dst)
