"""Derive SkyyMobs/build_skyymobs_0.1.18.py from the GENERATED 0.1.17 (build_skyymobs_0.1.17.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_17_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.17
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_18_patch.py   then   python SkyyMobs/build_skyymobs_0.1.18.py   then   python SkyyMobs/test_skyymobs_0.1.18.py
Edit THIS file, never the generated script (never --deploy).

0.1.18 (2026-10-23) = DRAGON EGGS FROM THE DRAGON BOSSES (research/Dragon-Pet-Spec.md section 8 "Elemental egg sources" + section 9 round
  D6; FULL round dragond1 with SkyyPets 0.4.12 = round D1). Skyy (docs/answered/pets.md 2026-10-18 DRAGON PET DESIGN): "... (and we need our
  elemental dragons.)" + 2026-10-20 "just go with the recommended on all of them" (the spec's source default: the elemental eggs drop from
  the Fire / Frost dragon bosses, chance row 1 %) + 2026-10-22 "we already have aures permission for this" (Plain / Tundra eggs stay Aures'
  Nestkeeper nests - we never drop or edit their items).
  1. ROW bosses.dragonEggs "Boss dragon eggs" (Server Setup -> Mobs -> Ranks, text, max 2000): comma separated "Match=Element" or
     "Match=Element/Element" (Match = a role id or MobGlob pattern - any case, exact, Prefix*, *Part*; Element = Fire, Thunder or Air = OUR
     three elemental eggs Skyy_PetEgg_Dragon_Fire / _Thunder / _Air of SkyyPets 0.4.11; several = one of them at random). The most specific
     match wins. Default "Dragon_Fire=Fire/Thunder, Dragon_Frost=Air" (the Storm dragon wears the Fire dragon's body, the Sky dragon the
     Frost dragon's - SkyyPets 0.4.11). Earth / Water are refused (those dragons hatch from Aures' own nest eggs). An admin may add a pack
     boss (e.g. Ancient_Calamity*=Fire).
  2. ROW bosses.dragonEggChance "Dragon egg chance" 1 % (0 - 12): per boss kill, rolled ONCE (the Spoils one-roll-per-death), only when the
     dead mob is a FULL BOSS (the Boss roles row + the pack bosses = mob:fn:boss = the P4 / pack boss rank - the same mobs that roll
     SkyyGear's Mythic bag) and its role is in the egg table. The chance used is capped at SkyyGear's LIVE loot.boss.mythic (read at each
     roll through the config kit's bridge op config:fn:SkyyGear "get", a java.lang call - the SkyyAccessories part.stats pattern) and never
     above 12 % (the row's max = the P5 Mythic boss bag default, tools/balance_model.py P5_MYTHIC): a dragon egg is never more common than a
     Mythic bag, also when an owner lowers the Mythic bag chance (Gear at 0 % = no eggs; Gear not running / unreadable = the 12 % cap).
  3. THE DROP: one egg item (new ItemStack(id, 1), never metadata) at the boss's spot through the Spoils spawn (ItemComponent.generateItemDrops
     + CommandBuffer.addEntities), so SkyySacks' auto-pickup gives it to the drop's owner (the top damager in this world, else the killing
     blow's player / a pet's owner) like the boss's own loot; one gold chat line to that player ("... Hatch it in /pets > Hatchery (one
     dragon per profile)." - the Hatchery refuses a dragon egg while the profile owns a dragon or has a dragon egg in it; the egg stays an
     item to keep or trade). No SkyyPets / an egg item not loaded = no
     drop (one WARN). Independent of the Spoils rows (they may be off).
  4. Ready line: + "dragon eggs: N boss rows, 1.0 % (cap C %, rolled N, dropped N)".
  SAVED DATA: none (two new rows: a file without the line = the default; no migration). One new class MobEgg; no new command / system /
  bridge key (SpoilsSys, 0.1.15, rolls it).
  ROLLBACK to 0.1.17: safe alone (no saved data; the rows are ignored; eggs already dropped stay SkyyPets items).
  FIXER (dragond1fix, 2026-10-23, the lost critic's findings): the cap reads SkyyGear's live Mythic bag chance (was the constant 12); the
  drop line names the one-dragon-per-profile rule (was "Hatch it in /pets > Hatchery." - a player who has a dragon cannot). Review fix: the chat line goes out only after the Spoils spawn put the drop in the world.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.17.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.18.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.17"') and P.s.startswith('"""SkyyMobs 0.1.17 - build script') and not P.has("MobEgg"), "not the SET pin 0.1.17"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("pool.makeClass(")
HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.18 (2026-10-23)"):].rstrip() + "\n\n"

P.rep('''"""SkyyMobs 0.1.17 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_17_patch.py from the SET pin 0.1.16 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.17.py -> SkyyMobs/SkyyMobs-0.1.17.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.17.py
''', '''"""SkyyMobs 0.1.18 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_18_patch.py from the SET pin 0.1.17 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.18.py -> SkyyMobs/SkyyMobs-0.1.18.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.18.py
''' + NOTE)
P.rep('VERSION = "0.1.17"', 'VERSION = "0.1.18"')

# ---------- the defaults (Python, checked against the vanilla roles + the SkyyPets egg table)
P.rep('''print("0.1.17 elements: ''', '''# 0.1.18 (dragond1, Dragon-Pet-Spec 8 + 9 D6): the boss dragon eggs - OUR three elemental eggs (tools/skyyeggs.py DRAGON_EGGS, SkyyPets)
import skyyeggs as EGGS
DEGG = [(_e[0], _e[4].capitalize()) for _e in EGGS.DRAGON_EGGS if _e[3] == "SkyyPets"]          # (item id, element word)
assert [_w for _i, _w in DEGG] == ["Fire", "Thunder", "Air"] and all(_i == "Skyy_PetEgg_Dragon_" + _w for _i, _w in DEGG), DEGG
DEGG_NAMES = dict((_e[0], _e[2]) for _e in EGGS.DRAGON_EGGS)
DEGG_ROWS = [("Dragon_Fire", "Fire/Thunder"), ("Dragon_Frost", "Air")]          # the spec's Fire / Frost dragon bosses (vanilla boss roles)
DEGG_DEF = ", ".join("%s=%s" % _r for _r in DEGG_ROWS)
DEGG_CHANCE = 1.0          # the spec's chance row (1 %)
DEGG_MAX = 12.0            # = SkyyGear loot.boss.mythic, the P5 Mythic boss bag chance (tools/balance_model.py P5_MYTHIC[0])
sys.argv, _av = [sys.argv[0]], sys.argv
import balance_model as _BM
sys.argv = _av
assert DEGG_MAX == _BM.P5_MYTHIC[0] and 0.0 < DEGG_CHANCE <= DEGG_MAX, "0.1.18: a dragon egg is never more common than the Mythic boss bag"
del _BM
for _r in DEGG_ROWS:
    assert any(glob(_r[0].lower(), _n.lower()) for _n in VANILLA), "0.1.18: bosses.dragonEggs pattern %s matches no vanilla role" % _r[0]
    assert matches(BOSS_PATS, _r[0]), "0.1.18: %s is not a Boss roles mob (no egg would ever drop)" % _r[0]
print("0.1.18 dragon eggs: %s at %g %% a boss kill (max %g %% = the Mythic bag)" % (DEGG_DEF, DEGG_CHANCE, DEGG_MAX))
print("0.1.17 elements: ''')
P.rep('''"elem.wheel=" + EL.WHEEL_DEF]          # 0.1.17 (elem1): the element rows (absent in an older file = the default)''',
      '''"elem.wheel=" + EL.WHEEL_DEF]          # 0.1.17 (elem1): the element rows (absent in an older file = the default)
CFG_LINES += ["# Boss dragon eggs (SkyyMobs 0.1.18): bosses.dragonEggs = Match=Fire, Thunder or Air (a / between = one of them), the boss",
              "# drops that SkyyPets dragon egg with bosses.dragonEggChance % a kill (never above SkyyGear's Boss Mythic bag chance, max 12 %).",
              "bosses.dragonEggs=" + DEGG_DEF, "bosses.dragonEggChance=%g" % DEGG_CHANCE]          # 0.1.18 (absent in an older file = the default)''')

# ---------- the rows (Ranks tab)
P.rep('''assert _dp.get("plate.format") == FORMAT_DEF and "{element}" not in FORMAT_DEF, "0.1.17: the default plate format is unchanged (no migration)"''',
      '''assert _dp.get("plate.format") == FORMAT_DEF and "{element}" not in FORMAT_DEF, "0.1.17: the default plate format is unchanged (no migration)"
# 0.1.18 (dragond1): the boss dragon eggs on the Ranks tab
CFG_ROWS += [
    ("bosses.dragonEggs", "Boss dragon eggs", "rank", "text", DEGG_DEF, "", "2000", "", "", "live",
     "Boss role or Prefix*=Fire, Thunder or Air (/ = one of them). Only full bosses drop one.",
     "field:MobCfg.DEGG_TXT;check=MobHooks.checkDragonEggs"),
    ("bosses.dragonEggChance", "Dragon egg chance", "rank", "dec", "%g" % DEGG_CHANCE, "0", "%g" % DEGG_MAX, "", "%", "live",
     "Per boss kill, rolled once. Never above SkyyGear's Boss Mythic bag chance (max 12 %).", "field:MobCfg.DEGG_CHANCE"),
]''')

# ---------- MobCfg fields + apply
P.rep('''          "public static volatile String ELEM_WHEEL = %s;" % jstr(EL.WHEEL_DEF)):
    F(cfg, f)
''', '''          "public static volatile String ELEM_WHEEL = %s;" % jstr(EL.WHEEL_DEF)):
    F(cfg, f)
# 0.1.18 (dragond1): the boss dragon egg rows
for f in ("public static volatile String DEGG_TXT = %s;" % jstr(DEGG_DEF), "public static volatile double DEGG_CHANCE = %s;" % repr(DEGG_CHANCE)):
    F(cfg, f)
''')
P.rep('''  ELEM_WHEEL = c.getProperty("elem.wheel", @ELWH@).trim();''', '''  ELEM_WHEEL = c.getProperty("elem.wheel", @ELWH@).trim();
  DEGG_TXT = c.getProperty("bosses.dragonEggs", @DEGGDEF@).trim();          // 0.1.18: a file without a line = the default
  DEGG_CHANCE = dec(c.getProperty("bosses.dragonEggChance"), @DEGGCH@, 0.0, @DEGGMX@);''')
P.rep('''.replace("@ELWH@", jstr(EL.WHEEL_DEF))''', '''.replace("@ELWH@", jstr(EL.WHEEL_DEF)).replace("@DEGGDEF@", jstr(DEGG_DEF)).replace("@DEGGCH@", repr(DEGG_CHANCE)).replace("@DEGGMX@", repr(DEGG_MAX))''')

# ---------- the class
P.rep('''meo = pool.makeClass(PKG + ".MobElemOfFn")''', '''meo = pool.makeClass(PKG + ".MobElemOfFn")
megg = pool.makeClass(PKG + ".MobEgg")       # 0.1.18 (dragond1): the boss dragon eggs (bosses.dragonEggs; SpoilsSys rolls it)''')
P.rep('''msp, mss, mel, mef, meo]''', '''msp, mss, mel, mef, meo, megg]''')

MEGG = r'''# 0.1.18 (dragond1): MobEgg - the boss dragon egg table (bosses.dragonEggs) + the roll SpoilsSys makes once per boss death. Pure methods
# first (the check= hook below calls err); ITEM_API / TELL_API = harness seams (null in the game).
for _f in ("public static final String[] WORDS = %s;" % ("new String[] { " + ", ".join(jstr(_w) for _i, _w in DEGG) + " }"),
           "public static final String[] IDS = %s;" % ("new String[] { " + ", ".join(jstr(_i) for _i, _w in DEGG) + " }"),
           "public static final String[] NAMES = %s;" % ("new String[] { " + ", ".join(jstr(DEGG_NAMES[_i]) for _i, _w in DEGG) + " }"),
           "public static volatile String TXT = null;",
           "public static volatile Object[] TAB = null;",          # { String[] pattern (lower), int[] spec, String[] egg ids ("a/b") }
           "public static final java.util.Random RNG = new java.util.Random();",
           "public static volatile java.util.function.Predicate ITEM_API = null;",
           "public static volatile java.util.function.BiConsumer TELL_API = null;",
           "public static volatile long ROLLS = 0L;", "public static volatile long DROPS = 0L;", "public static volatile long MISSING = 0L;"):
    F(megg, _f)
M(megg, r"""
public static int word(String w) {
  if (w == null) return -1;
  String t = w.trim();
  for (int i = 0; i < WORDS.length; i++) if (WORDS[i].equalsIgnoreCase(t)) return i;
  return -1;
}""")
# null = fine, else the reason (the check= hook; Earth / Water = Aures' own nest eggs)
M(megg, r"""
public static String err(String v) {
  if (v == null) return null;
  String s = v.trim();
  if (s.length() == 0 || s.equals("-")) return null;
  String[] ps = s.split(",");
  for (int i = 0; i < ps.length; i++) {
    String e = ps[i].trim();
    if (e.length() == 0) continue;
    int q = e.indexOf('=');
    if (q <= 0) return "'" + e + "' needs Role=Element, like Dragon_Fire=Fire.";
    String m = e.substring(0, q).trim();
    if (@PKG@.MobGlob.spec(m) == 0) return "'" + m + "' needs letters, not only *.";
    String[] ws = e.substring(q + 1).split("/");
    for (int k = 0; k < ws.length; k++) {
      String w = ws[k].trim();
      if (w.equalsIgnoreCase("Earth") || w.equalsIgnoreCase("Water")) return "Earth and Water dragons hatch from Aures' own Nestkeeper nest eggs - use Fire, Thunder or Air.";
      if (word(w) < 0) return "'" + w + "' is not Fire, Thunder or Air.";
    }
  }
  return null;
}""")
M(megg, r"""
public static Object[] parse(String v) {
  java.util.ArrayList pat = new java.util.ArrayList();
  java.util.ArrayList eggs = new java.util.ArrayList();
  if (v != null) {
    String[] ps = v.split(",");
    for (int i = 0; i < ps.length; i++) {
      String e = ps[i].trim();
      int q = e.indexOf('=');
      if (q <= 0) continue;
      String m = e.substring(0, q).trim().toLowerCase();
      if (@PKG@.MobGlob.spec(m) == 0) continue;
      String[] ws = e.substring(q + 1).split("/");
      StringBuilder b = new StringBuilder();
      for (int k = 0; k < ws.length; k++) {
        int x = word(ws[k]);
        if (x < 0) continue;
        if (b.length() > 0) b.append('/');
        b.append(IDS[x]);
      }
      if (b.length() == 0) continue;
      pat.add(m);
      eggs.add(b.toString());
    }
  }
  String[] p = new String[pat.size()];
  String[] g = new String[pat.size()];
  int[] sp = new int[pat.size()];
  for (int i = 0; i < p.length; i++) { p[i] = (String) pat.get(i); g[i] = (String) eggs.get(i); sp[i] = @PKG@.MobGlob.spec(p[i]); }
  return new Object[] { p, sp, g };
}""")
M(megg, r"""
public static Object[] tab() {
  String t = @PKG@.MobCfg.DEGG_TXT;
  Object[] tb = TAB;
  if (tb == null || t != TXT) { tb = parse(t); TAB = tb; TXT = t; }
  return tb;
}""")
# the eggs a role may drop ("id/id"), the most specific match (most literal characters, then the first entry); null = none
M(megg, r"""
public static String eggsFor(String role) {
  if (role == null) return null;
  Object[] tb = tab();
  String[] p = (String[]) tb[0];
  int[] sp = (int[]) tb[1];
  String[] g = (String[]) tb[2];
  String k = role.trim().toLowerCase();
  int best = -1;
  for (int i = 0; i < p.length; i++) if (@PKG@.MobGlob.glob(p[i], k) && (best < 0 || sp[i] > sp[best])) best = i;
  return best < 0 ? null : g[best];
}""")
M(megg, r"""
public static boolean itemOk(String id) {
  java.util.function.Predicate p = ITEM_API;
  if (p != null) return p.test(id);
  try { return @ITMA@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return false; }
}""")
M(megg, r"""
public static String nameOf(String id) {
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return NAMES[i];
  return String.valueOf(id);
}""")
# SkyyGear's LIVE Boss Mythic bag chance (loot.boss.mythic) through the config kit's bridge op (CONFIG-CONTRACT: "get" = the value text,
# never throws, never touches the world; the SkyyAccessories part.stats pattern); -1 = Gear not running / unreadable. GEAR_API = harness seam.
F(megg, "public static volatile java.util.function.Function GEAR_API = null;")
M(megg, r"""
public static double gearMythic() {
  try {
    Object f = GEAR_API;
    if (f == null) {
      Object b = System.getProperties().get("skyy.bridge");
      if (!(b instanceof java.util.Map)) return -1.0;
      f = ((java.util.Map) b).get("config:fn:SkyyGear");
    }
    if (!(f instanceof java.util.function.Function)) return -1.0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { "get", "loot.boss.mythic" });
    if (!(r instanceof String)) return -1.0;
    double d = Double.parseDouble(((String) r).trim());
    return (Double.isNaN(d) || Double.isInfinite(d) || d < 0.0) ? -1.0 : d;
  } catch (Throwable t) { return -1.0; }
}""")
# the cap in force: Gear's live Mythic bag chance, never above 12 % (Gear unreadable = 12 %)
M(megg, r"""
public static double cap() {
  double g = gearMythic();
  return (g >= 0.0 && g < @DEGGMX@) ? g : @DEGGMX@;
}""".replace("@DEGGMX@", repr(DEGG_MAX)))
M(megg, r"""
public static double chance() {
  double c = @PKG@.MobCfg.DEGG_CHANCE;
  double k = cap();
  return c > k ? k : c;
}""")
# ONE roll for a dead mob: a FULL boss (Boss roles + pack bosses = mob:fn:boss) whose role is in the table, chance bosses.dragonEggChance %
# (capped by chance() above)
M(megg, r"""
public static String roll(String role, java.util.Random rng) {
  if (role == null || rng == null || !(@PKG@.MobCfg.DEGG_CHANCE > 0.0) || !@PKG@.MobCfg.isBoss(role)) return null;
  String eg = eggsFor(role);
  if (eg == null) return null;
  ROLLS = ROLLS + 1L;
  double ch = chance();
  if (!(ch > 0.0) || !(rng.nextDouble() * 100.0 < ch)) return null;
  String[] ids = eg.split("/");
  String id = ids[ids.length == 1 ? 0 : rng.nextInt(ids.length)];
  if (!itemOk(id)) { MISSING = MISSING + 1L; @PKG@.MobLog.warnOnce("degg:" + id, "a boss rolled a dragon egg but the item " + id + " is not loaded (SkyyPets 0.4.11+ missing?) - nothing dropped"); return null; }
  DROPS = DROPS + 1L;
  return id;
}""")
M(megg, r"""
public static void tell(java.util.UUID u, String text) {
  if (u == null || text == null) return;
  java.util.function.BiConsumer f = TELL_API;
  if (f != null) { f.accept(u, text); return; }
  try {
    @PR@ pr = @UNIV@.get().getPlayer(u);
    if (pr != null) pr.sendMessage(@MSG@.raw(text).color(@GOLDC@));
  } catch (Throwable t) { }
}""".replace("@GOLDC@", jstr(SUI.COLOR["gold"])))          # the kit's gold (the other SkyyMobs chat lines)
# SpoilsSys (once per death): add the egg to the list it spawns at the mob (SkyySacks claims it for the drop's owner); the chat line goes
# out in dropped(), only AFTER the spawn put the drop in the world (review fix)
M(megg, r"""
public static String addTo(java.util.ArrayList l, String role, java.util.UUID owner, java.util.Random rng) {
  if (l == null || owner == null) return null;
  String id = roll(role, rng);
  if (id == null) return null;
  l.add(new Object[] { id, Integer.valueOf(1) });
  return id;
}""")
M(megg, r"""
public static boolean dropped(java.util.UUID owner, String id, int spawned) {
  if (owner == null || id == null || spawned <= 0) return false;
  tell(owner, "[Mobs] The boss dropped a " + nameOf(id) + "! Hatch it in /pets > Hatchery (one dragon per profile).");
  return true;
}""")
M(megg, r"""
public static String text() {
  Object[] tb = tab();
  return "dragon eggs: " + ((String[]) tb[0]).length + " boss rows, " + @PKG@.MobCfg.DEGG_CHANCE + " % (cap " + cap() + " %, rolled " + ROLLS + ", dropped " + DROPS + (MISSING > 0L ? ", item missing " + MISSING : "") + ")";
}""")
M(mh, r"""
public static String checkDragonEggs(String key, String value) {
  if (value == null) return null;
  return @PKG@.MobEgg.err(value);
}""")
'''
P.rep('''# 0.1.17 (elem1): Mob elements + Element wheel in Server Setup (value null = back to the default)''', MEGG + '''# 0.1.17 (elem1): Mob elements + Element wheel in Server Setup (value null = back to the default)''')

# ---------- SpoilsSys: the egg roll, independent of the Spoils rows
P.rep('''    if (!@PKG@.MobSpoils.ON) return;
    @NPCE@ npc''', '''    if (!@PKG@.MobSpoils.ON && !(@PKG@.MobCfg.DEGG_CHANCE > 0.0)) return;          // 0.1.18: + the boss dragon eggs
    @NPCE@ npc''')
P.rep('''    java.util.ArrayList l = @PKG@.MobSpoils.extra(ku, role.getDropListId(), boss, @PKG@.MobSpoils.RNG);
    @PKG@.MobSpoils.coins(ku, lvl, @PKG@.MobSpoils.RNG);''', '''    java.util.ArrayList l = @PKG@.MobSpoils.ON ? @PKG@.MobSpoils.extra(ku, role.getDropListId(), boss, @PKG@.MobSpoils.RNG) : new java.util.ArrayList();
    if (@PKG@.MobSpoils.ON) @PKG@.MobSpoils.coins(ku, lvl, @PKG@.MobSpoils.RNG);
    String egg = @PKG@.MobEgg.addTo(l, npc.getRoleName(), ku, @PKG@.MobEgg.RNG);          // 0.1.18: a full boss's dragon egg (once per death)''')
P.rep('''    if (!l.isEmpty()) @PKG@.MobSpoils.spawn(st, cb, l, new @VEC@(p.x, p.y + 1.0, p.z));
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("spoils",''', '''    int sp = l.isEmpty() ? 0 : @PKG@.MobSpoils.spawn(st, cb, l, new @VEC@(p.x, p.y + 1.0, p.z));
    @PKG@.MobEgg.dropped(ku, egg, sp);          // 0.1.18 review fix: the egg's chat line only once the drop is in the world
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("spoils",''')

# ---------- ready line
P.rep('''+ @PKG@.MobSpoils.text() + " " + spt''', '''+ @PKG@.MobSpoils.text() + " " + spt + "; " + @PKG@.MobEgg.text()''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("pool.makeClass(") == CLS0 + 1, "0.1.18 adds 1 class, no command / system"
_i = P.s.index
assert _i("public static boolean isBoss(String role)") < _i("public static String roll(String role, java.util.Random rng)") < _i("public static String checkDragonEggs(") \
    < _i("@PKG@.MobEgg.addTo(l, npc.getRoleName()"), "0.1.18: methods before callers"
P.finish()
