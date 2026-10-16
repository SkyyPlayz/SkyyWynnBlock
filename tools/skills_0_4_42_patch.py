"""Derive SkyySkills/build_skyyskills_0.4.42.py from the GENERATED SkyySkills 0.4.41 (build_skyyskills_0.4.41.py = the tools/deploy_set.py SET
pin; 0.4.41 came from 0.4.40 by tools/skills_0_4_41_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.41 (nothing else changed); 0.4.41 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_42_patch.py   then   python SkyySkills/build_skyyskills_0.4.42.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.42.py

0.4.42 (2026-10-15) = FORTUNE INDICATOR (lean round skills0442; Skyy 2026-10-15, docs/answered/skills.md FORTUNE INDICATOR: "and id like
some sort of small indicator when a gathering fortune works, and gives me more drops").
  Every gathering extra drop goes through Perks.doubled (BreakTask = Mining / Foraging / Farming breaks incl. ripe crops, Fell.one = felled
  tree blocks, HarvestTask = F-harvests, Sickle.award = sickle swings). The drop maths are NOT touched (Perks.fortune / extras / rolls /
  breakDouble / harvestDouble are byte-identical to 0.4.41); doubled() keeps give() + collDouble() and only its message part changes:
  1. "Fortune!" LINE (new class Fortune, its own message kind "fortune"): the extra items of hits within FORTUNE_WIN (1.5 s) of each other
     are GROUPED per player (a group is sent 1.5 s after its last hit, at the latest 4 s after its first - so fast mining / a felled tree
     gives one line, never spam) and delivered by a one-shot task (FortTask, the server scheduler; memory + one feed push or one chat
     packet, no I/O):
       ITEM NAMES = what players see (Item.getTranslationKey -> I18nModule en-US, SkyySacks' PickupView.name: Wood_Oak_Trunk -> "Oak Log",
       Ore_Copper -> "Copper Ore"); the prettified id only when an item has no translation.
       - feed (default): ONE SkyyHud feed card, kind "fortune", the icon of the item with the most extra, "Fortune! Oak Log" with
         count = that item's extra (SkyyHud draws "x5" and merges a following group of the same item into the same card - "x9").
       - chat: "Fortune! +5 Oak Log, +1 Stick" (up to 3 items, "+N more"), the old double-drop colour.
       - off: nothing.
     The player picks it in /settings -> Messages (registered through settings:fn:register in category "messages", exactly like SkyyHud's
     kinds: msg.fortune = shown or not, msg.fortune.feed = feed or chat; both default ON). SkyyHud's msgroute:fn:get only knows its own 11
     kinds (an unknown kind always answers "chat"), so Fortune reads the two switches itself (settings:fn:get; no SkyyMenu = the
     defaults). Feed wanted but no SkyyHud (no feed:fn:push) = SILENT; SkyyHud refuses the card (that player's Feed widget / HUD off) =
     the chat line (SkyyHud's own rule: what a player chose to see never vanishes).
     Still hidden by the old switches first: perk.doubleDropMessage=false (Server Setup, now labelled "Fortune indicator") and the
     player's skills.doubleDrop (/settings Skills, its help text now describes the Fortune line).
     The 0.4.34 route "drop" card / 0.4.33 chat line for double drops is replaced (no duplicate); route "drop" stays for extra potions.
  2. SOUND: SkSnd.fortune - SFX_Crops_Grow_Stage_Complete (research/Sound-Pass-Plan.md: "Tree felled bonus, double drop | soft pop"),
     2D to that player only (SkSnd.playTo: the per-player settings:sounds:<uuid> mute, the 0.5 s gate), once when a group OPENS (not per
     hit). Server Setup -> Skills -> Sounds: "Fortune sound" (sound.fortune) + its id (sound.fortune.id, check= SkSnd.check; empty = none).
     Muted for a player who hides the line (msg.fortune / skills.doubleDrop off) - "a muted message class is a muted sound".
  3. SPARKLE: vanilla particle system Block_Break_Treasure (the treasure / coin block's own break burst: a flash, sparks, 6-8 stars and a
     few gold coins; EVERY spawner has a finite TotalParticles - build-checked in Assets.zip, so it ends by itself, the SkyyArmory 0.1.3
     lesson) at 0.6 scale, centred on the broken block, sent ONLY to that player (ParticleUtil.spawnParticleEffect with a one-element ref
     list - the 0.4.x double-jump feathers' recipe), at most one every 250 ms per player (a felled tree never floods packets). The block
     position comes from Fortune.at(u, x, y, z), set by BreakTask / Fell.one / HarvestTask right before their breakDouble / harvestDouble
     (used only within 100 ms); sickle swings have no block position -> no sparkle (line + sound only). Server Setup -> Skills -> Perks:
     "Fortune sparkle" (fortune.sparkle).
  CONFIG: a fresh xp.properties lists sound.fortune, sound.fortune.id, fortune.sparkle (the 0.4.42 block); an existing file without them
  reads the same defaults (no migration, nothing rewritten). No saved data, no new command, no new bridge key written (two settings keys
  registered). Players who left: Fortune.retain (Acro.retainOnline); shutdown clears the groups.
  ROLLBACK to 0.4.41: safe (memory only; 0.4.41 ignores the three new lines; the double-drop card / chat line come back).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.41.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.42.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.4.41"' in s and s.startswith('"""SkyySkills 0.4.41 - build script') and "Fortune" + ".hit" not in s, "not the generated 0.4.41 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.42 (2026-10-15)"):].rstrip() + "\n"
FORT_SND = "SFX_Crops_Grow_Stage_Complete"
FORT_FX = "Block_Break_Treasure"

# ================================================================================================ docstring + version
rep('''"""SkyySkills 0.4.41 - build script (derived from the generated 0.4.40 by tools/skills_0_4_41_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.42 - build script (derived from the generated 0.4.41 by tools/skills_0_4_42_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.42.py.
0.4.41 was derived from the generated 0.4.40 by tools/skills_0_4_41_patch.py;
''')
rep('VERSION = "0.4.41"', 'VERSION = "0.4.42"')

# ================================================================================================ the two new classes
rep('''hopen = pool.makeClass(PKG + ".SkillsHubOpen")
''', '''hopen = pool.makeClass(PKG + ".SkillsHubOpen")
fort42 = pool.makeClass(PKG + ".Fortune")      # 0.4.42: the Fortune indicator (grouped line, sound, sparkle)
ftask42 = pool.makeClass(PKG + ".FortTask")    # 0.4.42: the one-shot task that sends a player's Fortune group
''')

# ================================================================================================ the default xp.properties block + asset checks
rep('''assert len(G39_KEYS) == len(set(G39_KEYS)) == 8
''', '''assert len(G39_KEYS) == len(set(G39_KEYS)) == 8
# 0.4.42 (tools/skills_0_4_42_patch.py): the Fortune indicator's sound + sparkle; a missing key reads the same code default (no migration)
FORT_SND = %r
FORT_FX = %r
assert FORT_SND in SOUND_IDS, "0.4.42: sound event %%s is not in Assets.zip" %% FORT_SND
with zipfile.ZipFile(ASSETS) as z:
    _fxn = [n for n in z.namelist() if n.startswith("Server/Particles/") and n.endswith("/" + FORT_FX + ".particlesystem")]
    assert len(_fxn) == 1, "0.4.42: particle system %%s is not in Assets.zip" %% FORT_FX
    _fxs = json.loads(z.read(_fxn[0]))
    _sp = dict((os.path.basename(n)[:-len(".particlespawner")], n) for n in z.namelist() if n.startswith("Server/Particles/") and n.endswith(".particlespawner"))
    assert _fxs.get("Spawners"), "0.4.42: %%s has spawners" %% FORT_FX
    for _sx in _fxs["Spawners"]:   # every spawner ends by itself (no endless emitter left in the world - SkyyArmory 0.1.3)
        assert _sx.get("TotalSpawners", 1) != -1 and _sx.get("SpawnerId") in _sp, "0.4.42: spawner %%s" %% _sx
        _tp = json.loads(z.read(_sp[_sx["SpawnerId"]])).get("TotalParticles", {})
        assert isinstance(_tp.get("Max"), (int, float)) and 0 <= _tp["Max"] <= 64, "0.4.42: %%s emits a finite burst (%%s)" %% (_sx["SpawnerId"], _tp)
G42_L = ["# ---------- Fortune indicator (SkyySkills 0.4.42) ----------",
         "# Comments must stay on their own lines.",
         "# When gathering Fortune gives extra drops the player gets a short Fortune line (each player picks feed, chat or off in /settings,",
         "# Messages tab), a soft sound (an empty id = no sound) and a small sparkle at the block that only that player sees.",
         "# perk.doubleDropMessage false turns all three off.",
         "sound.fortune=true", "sound.fortune.id=" + FORT_SND, "fortune.sparkle=true"]
L.append("")
L.extend(G42_L)
G42_DEFAULTS = "\\n".join(G42_L) + "\\n"
assert all(ord(ch) < 128 for ch in G42_DEFAULTS) and '"' not in G42_DEFAULTS and "\\\\" not in G42_DEFAULTS and all(len(_ln) <= 140 for _ln in G42_L if _ln.startswith("#"))
assert not any(_cre.match(r"#\\s*[A-Za-z][A-Za-z0-9._-]*\\s*[=:]\\s*\\S+\\s*$", _ln) for _ln in G42_L), "a comment looks like a template line"
G42_KEYS = [_ln.split("=", 1)[0] for _ln in G42_L if not _ln.startswith("#")]
assert len(G42_KEYS) == len(set(G42_KEYS)) == 3
''' % (FORT_SND, FORT_FX))

# ================================================================================================ SkSnd: the Fortune sound + the sparkle switch
rep('''    snd39.addField(CtField.make("public static final %s;" % _d39, snd39))
''', '''    snd39.addField(CtField.make("public static final %s;" % _d39, snd39))
for _d42 in ("public static volatile boolean FORT = true;", "public static volatile String FORT_ID = %s;" % json.dumps(FORT_SND),
             "public static volatile boolean SPARKLE = true;"):   # 0.4.42: sound.fortune, sound.fortune.id, fortune.sparkle
    snd39.addField(CtField.make(_d42, snd39))
''')
rep('''  DODGE_ID = idOf(p, "sound.dodge.id", "SFX_Ability_Wind_Strike_Imbue_Local");
''', '''  DODGE_ID = idOf(p, "sound.dodge.id", "SFX_Ability_Wind_Strike_Imbue_Local");
  FORT = @PKG@.SkillCfg.bool(p, "sound.fortune", true);                      // 0.4.42: the Fortune indicator
  FORT_ID = idOf(p, "sound.fortune.id", "''' + FORT_SND + '''");
  SPARKLE = @PKG@.SkillCfg.bool(p, "fortune.sparkle", true);
''')
rep('''", perfect dodge " + one(DODGE, DODGE_ID) + "; settings:sounds:<uuid> FALSE mutes a player)";''',
    '''", perfect dodge " + one(DODGE, DODGE_ID) + ", Fortune " + one(FORT, FORT_ID) + "; Fortune sparkle " + (SPARKLE ? "on" : "off") + "; settings:sounds:<uuid> FALSE mutes a player)";''')
rep('''snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean dodge(@PR@ pr, java.util.UUID u) {''', '''# 0.4.42: the Fortune indicator's sound - the caller (Fortune.hit) already checked the player's msg.fortune / skills.doubleDrop switches
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean fortune(@PR@ pr) {
  return playTo(pr, pick(ON, FORT, FORT_ID), "fortune");
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean dodge(@PR@ pr, java.util.UUID u) {''')

# ================================================================================================ Fortune + FortTask (before Perks.doubled)
FORT_JAVA = r'''
# ================= 0.4.42 Fortune: the indicator when gathering Fortune gives extra drops (tools/skills_0_4_42_patch.py) =================
# GRP: UUID -> Object[]{ LinkedHashMap item id -> long[]{extra}, long[]{first hit ms, last hit ms} } - one open group per player; POS: UUID
# -> double[]{x, y, z, set ms} (Fortune.at, the block the next breakDouble / harvestDouble rolls for); SPK: UUID -> Long last sparkle ms.
# hit() on the world thread (Perks.doubled), step() on the scheduler (FortTask) - add / due / take hold the class lock (memory only).
for _d in ("public static final java.util.concurrent.ConcurrentHashMap GRP = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap POS = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap SPK = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();",   # item id -> the name players see
           "public static volatile long WIN = 1500L;", "public static volatile long MAX_AGE = 4000L;", "public static volatile long SPARK_GAP = 250L;",
           "public static volatile boolean MANUAL = false;",      # HARNESS SEAM ONLY (false): no FortTask is scheduled, the harness calls step()
           "public static volatile boolean WARNED = false;",
           "public static final String PARTICLE = %s;" % json.dumps(FORT_FX), "public static final float SCALE = 0.6f;",
           "public static final java.util.concurrent.atomic.AtomicLong HITS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong GROUPS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong FEEDS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong CHATS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong OFFS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong SILENT = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong SOUNDS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong SPARKS = new java.util.concurrent.atomic.AtomicLong();"):
    fort42.addField(CtField.make(_d, fort42))
ftask42.addInterface(pool.get("java.lang.Runnable"))
ftask42.addField(CtField.make("public java.util.UUID u;", ftask42))
ftask42.addConstructor(CtNewConstructor.make("public FortTask(java.util.UUID u) { this.u = u; }", ftask42))
fort42.addMethod(CtNewMethod.make(J14(r"""
public static void warn(String what, Throwable t) {
  if (WARNED) return;
  WARNED = true;
  @PKG@.SkillCfg.warn("Fortune indicator: " + what + " failed (logged once): " + t);
}"""), fort42))
# a player's own switch (settings:fn:get, SkyyMenu); no SkyyMenu / no answer = ON (both Fortune switches default ON)
fort42.addMethod(CtNewMethod.make(J14(r"""
public static boolean setting(java.util.UUID u, String key) {
  if (u == null) return true;
  try {
    Object f = @PKG@.SkillStore.bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}"""), fort42))
# shown at all: the admin master (perk.doubleDropMessage), the old player switch (skills.doubleDrop), the new one (msg.fortune)
fort42.addMethod(CtNewMethod.make(J14(r"""
public static boolean shown(java.util.UUID u) {
  if (u == null || !@PKG@.PerkCfg.DD_MSG) return false;
  if (!@PKG@.SkillStore.notifyOn(u, "skills.doubleDrop")) return false;
  return setting(u, "msg.fortune");
}"""), fort42))
fort42.addMethod(CtNewMethod.make(J14(r"""
public static void at(java.util.UUID u, int x, int y, int z) {
  if (u == null) return;
  POS.put(u, new double[] { (double) x, (double) y, (double) z, (double) System.currentTimeMillis() });
}"""), fort42))
# the block of THIS break: set within the last 100 ms (the caller's breakDouble / harvestDouble runs right after at()), consumed once
fort42.addMethod(CtNewMethod.make(J14(r"""
public static double[] pos(java.util.UUID u, long now) {
  if (u == null) return null;
  double[] p = (double[]) POS.remove(u);
  if (p == null || p.length < 4) return null;
  double age = (double) now - p[3];
  if (age >= 0.0 && age <= 100.0) return p;
  return null;
}"""), fort42))
# add q of item id to the player's group; true = this call OPENED a new group (the caller schedules its FortTask + plays the sound)
fort42.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean add(java.util.UUID u, String id, long q, long now) {
  Object[] g = (Object[]) GRP.get(u);
  boolean opened = false;
  if (g == null) {
    g = new Object[] { new java.util.LinkedHashMap(), new long[] { now, now } };
    GRP.put(u, g);
    opened = true;
  }
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) g[0];
  long[] c = (long[]) m.get(id);
  if (c == null) {
    if (m.size() >= 32) return opened;
    c = new long[1];
    m.put(id, c);
  }
  long t = c[0] + q;
  c[0] = t > 999999999L ? 999999999L : t;
  ((long[]) g[1])[1] = now;
  return opened;
}"""), fort42))
# PURE-ish: the extra stacks of one proc into the group: 1 = a new group opened, 0 = added to the open one, -1 = nothing to add
fort42.addMethod(CtNewMethod.make(J14(r"""
public static int hitU(java.util.UUID u, java.util.List drops, long now) {
  if (u == null || drops == null) return -1;
  int r = -1;
  for (int i = 0; i < drops.size(); i++) {
    Object o = drops.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ is = (@IS@) o;
    if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
    HITS.incrementAndGet();
    if (add(u, is.getItemId(), (long) is.getQuantity(), now)) { r = 1; GROUPS.incrementAndGet(); }
    else if (r < 0) r = 0;
  }
  return r;
}"""), fort42))
# ms until the group is due (> 0), 0 = due now (WIN ms after its last hit, or MAX_AGE after its first), -1 = no group
fort42.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long due(java.util.UUID u, long now) {
  Object[] g = (Object[]) GRP.get(u);
  if (g == null) return -1L;
  long[] t = (long[]) g[1];
  long a = t[1] + WIN - now;
  long b = t[0] + MAX_AGE - now;
  long w = a < b ? a : b;
  return w > 0L ? w : 0L;
}"""), fort42))
# the group off the map: Object[]{ String[] ids, long[] extras } biggest first (equal amounts keep the order they came in), or null
fort42.addMethod(CtNewMethod.make(J14(r"""
public static synchronized Object[] take(java.util.UUID u) {
  Object[] g = (Object[]) GRP.remove(u);
  if (g == null) return null;
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) g[0];
  int n = m.size();
  if (n == 0) return null;
  String[] ids = new String[n];
  long[] qs = new long[n];
  java.util.Iterator it = m.keySet().iterator();
  int i = 0;
  while (it.hasNext() && i < n) {
    Object k = it.next();
    ids[i] = (String) k;
    qs[i] = ((long[]) m.get(k))[0];
    i++;
  }
  for (int a = 1; a < n; a++) {
    String si = ids[a];
    long qi = qs[a];
    int b = a - 1;
    while (b >= 0 && qs[b] < qi) { ids[b + 1] = ids[b]; qs[b + 1] = qs[b]; b--; }
    ids[b + 1] = si;
    qs[b + 1] = qi;
  }
  return new Object[] { ids, qs };
}"""), fort42))
# the item's name as players see it (SkyySacks 0.8.7 PickupView.name, reused): Item.getTranslationKey() -> I18nModule en-US (the
# "server." prefix dropped as a second try); no item / no translation / an untranslated key = the prettified id; cached, at most 4096 ids
B.probe(pool, ITM, "getTranslationKey")
B.probe(pool, "com.hypixel.hytale.server.core.modules.i18n.I18nModule", "getMessage")
fort42.addMethod(CtNewMethod.make(J14(r"""
public static String name(String id) {
  if (id == null) return "";
  Object c = NAMES.get(id);
  if (c instanceof String) return (String) c;
  String n = null;
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    if (o instanceof @ITM@) {
      String tk = ((@ITM@) o).getTranslationKey();
      com.hypixel.hytale.server.core.modules.i18n.I18nModule m = com.hypixel.hytale.server.core.modules.i18n.I18nModule.get();
      if (tk != null && m != null) {
        n = m.getMessage("en-US", tk);
        if ((n == null || n.length() == 0) && tk.startsWith("server.")) n = m.getMessage("en-US", tk.substring(7));
      }
    }
  } catch (Throwable t) { n = null; }
  if (n == null || n.length() == 0 || n.indexOf('.') > 0 && n.indexOf(' ') < 0) n = @PKG@.MsgRoute.pretty(id);
  if (NAMES.size() < 4096) NAMES.put(id, n);
  return n;
}"""), fort42))
# the feed card's text (SkyyHud adds "  x<count>" = the first item's extra) and the chat line - item names via name()
fort42.addMethod(CtNewMethod.make(J14(r"""
public static String cardText(String[] ids) {
  if (ids == null || ids.length == 0) return "";
  return "Fortune! " + name(ids[0]) + (ids.length > 1 ? ", +" + (ids.length - 1) + " more" : "");
}"""), fort42))
fort42.addMethod(CtNewMethod.make(J14(r"""
public static String chatLine(String[] ids, long[] qs) {
  if (ids == null || qs == null || ids.length == 0) return "";
  StringBuilder sb = new StringBuilder("Fortune!");
  int n = ids.length < 4 ? ids.length : 3;
  for (int i = 0; i < n && i < qs.length; i++) sb.append(i == 0 ? " +" : ", +").append(qs[i]).append(' ').append(name(ids[i]));
  if (ids.length > n) sb.append(", +").append(ids.length - n).append(" more");
  return sb.toString();
}"""), fort42))
# deliver one group: "off" (hidden now), "feed" (the card was taken), "none" (feed wanted, no SkyyHud = silent), "chat" (the line;
# pr null = the harness: the line is only counted / recorded through MsgRoute.said)
fort42.addMethod(CtNewMethod.make(J14(r"""
public static String deliver(java.util.UUID u, @PR@ pr, String[] ids, long[] qs) {
  if (u == null || ids == null || qs == null || ids.length == 0 || qs.length == 0) return "none";
  if (!@PKG@.PerkCfg.DD_MSG || !setting(u, "msg.fortune")) { OFFS.incrementAndGet(); return "off"; }
  if (setting(u, "msg.fortune.feed")) {
    if (@PKG@.MsgRoute.fn("feed:fn:push") == null) { SILENT.incrementAndGet(); return "none"; }
    if (@PKG@.MsgRoute.feed(u, "fortune", ids[0], cardText(ids), qs[0])) { FEEDS.incrementAndGet(); return "feed"; }
  }
  String line = chatLine(ids, qs);
  @PKG@.MsgRoute.said(line);
  CHATS.incrementAndGet();
  if (pr != null) pr.sendMessage(@MSG@.raw(line).color("#b8f0a0"));
  return "chat";
}"""), fort42))
# FortTask's step: the wait left (> 0 = run again then), or -1 = done (sent, nothing open, or the player left)
fort42.addMethod(CtNewMethod.make(J14(r"""
public static long step(java.util.UUID u, long now) {
  long w = due(u, now);
  if (w != 0L) return w;
  Object[] t = take(u);
  if (t == null) return -1L;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return -1L;
    deliver(u, pr, (String[]) t[0], (long[]) t[1]);
  } catch (Throwable x) { warn("the line", x); }
  return -1L;
}"""), fort42))
fort42.addMethod(CtNewMethod.make(J14(r"""
public static void sched(java.util.UUID u, long ms) {
  if (MANUAL || u == null) return;
  try {
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.FortTask(u), ms, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    GRP.remove(u);
    warn("scheduling", t);
  }
}"""), fort42))
# the sparkle: Block_Break_Treasure at 0.6 scale on the block centre, ONLY to this player (a one-element ref list), one per SPARK_GAP
fort42.addMethod(CtNewMethod.make(J14(r"""
public static boolean spark(@PR@ pr, double[] p, long now) {
  if (pr == null || p == null || !@PKG@.SkSnd.SPARKLE) return false;
  try {
    java.util.UUID u = pr.getUuid();
    Object last = SPK.get(u);
    if (last instanceof Long) { long d = now - ((Long) last).longValue(); if (d >= 0L && d < SPARK_GAP) return false; }
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return false;
    @ST@ st = r.getStore();
    if (st == null) return false;
    SPK.put(u, Long.valueOf(now));
    java.util.ArrayList l = new java.util.ArrayList();
    l.add(r);
    @PTU@.spawnParticleEffect(PARTICLE, new @V3D@(p[0] + 0.5, p[1] + 0.5, p[2] + 0.5), 0.0f, 0.0f, 0.0f, SCALE, (com.hypixel.hytale.protocol.Color) null, l, st);
    SPARKS.incrementAndGet();
    return true;
  } catch (Throwable t) {
    warn("the sparkle", t);
    return false;
  }
}"""), fort42))
# Perks.doubled (world thread), after give() handed the extra drops over: group them, the sound when a group opens, the sparkle
fort42.addMethod(CtNewMethod.make(J14(r"""
public static void hit(@PR@ pr, java.util.List drops) {
  if (pr == null) return;
  try {
    java.util.UUID u = pr.getUuid();
    long now = System.currentTimeMillis();
    double[] p = pos(u, now);
    if (!shown(u)) return;
    int r = hitU(u, drops, now);
    if (r < 0) return;
    if (r == 1) {
      sched(u, WIN);
      if (@PKG@.SkSnd.fortune(pr)) SOUNDS.incrementAndGet();
    }
    spark(pr, p, now);
  } catch (Throwable t) { warn("hit", t); }
}"""), fort42))
fort42.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  GRP.keySet().retainAll(online);
  POS.keySet().retainAll(online);
  SPK.keySet().retainAll(online);
}"""), fort42))
fort42.addMethod(CtNewMethod.make(J14(r"""
public static String stats() {
  return "hits " + HITS.get() + ", groups " + GROUPS.get() + ", feed " + FEEDS.get() + ", chat " + CHATS.get() + ", off " + OFFS.get() + ", silent " + SILENT.get() + ", sounds " + SOUNDS.get() + ", sparkles " + SPARKS.get();
}"""), fort42))
ftask42.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  try {
    long w = @PKG@.Fortune.step(this.u, System.currentTimeMillis());
    if (w > 0L) @HSV@.SCHEDULED_EXECUTOR.schedule(this, w, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    @PKG@.Fortune.GRP.remove(this.u);
    @PKG@.Fortune.warn("the task", t);
  }
}"""), ftask42))
'''
rep('''# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
''', FORT_JAVA.lstrip("\n") + '''# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
# 0.4.42: replaced by the Fortune indicator (Fortune.hit: grouped "Fortune!" line kind fortune, sound, sparkle); the hide switches stay
''')
rep('''  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.doubleDrop")) return;
  if (ddRoute(u, drops)) return;
  long now = System.currentTimeMillis();
  long[] c = (long[]) DDMSG.get(u);
  if (c == null) {{ c = new long[2]; DDMSG.put(u, c); }}
  c[0] = c[0] + 1L;
  if (now - c[1] < {PKG}.SkillCfg.FEEDBACK_MS) return;
  String dl = "Double drop" + (c[0] > 1L ? " x" + c[0] : "") + "!" + what + "  (" + {PKG}.SkillDefs.LABELS[row] + " perk)";
  {PKG}.MsgRoute.said(dl);
  pr.sendMessage({MSG}.raw(dl).color("#b8f0a0"));
  c[0] = 0L;
  c[1] = now;
}}""", perk))''', '''  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  {PKG}.Fortune.hit(pr, drops);   // 0.4.42: the Fortune indicator (it checks skills.doubleDrop + msg.fortune itself)
}}""", perk))''')

# ================================================================================================ the block positions (sparkle) at the 3 callers
rep('''    {PKG}.Perks.breakDouble(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED);
''', '''    {V3I} fp = this.ev.getTargetBlock();   // 0.4.42: the Fortune sparkle's block
    if (fp != null) {PKG}.Fortune.at(this.u, fp.x(), fp.y(), fp.z());
    {PKG}.Perks.breakDouble(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED);
''')
rep('''    if ({PKG}.FellCfg.DOUBLE_DROPS && rule != null) {PKG}.Perks.breakDouble(pr, row, bt, W.wn, true);
''', '''    if ({PKG}.FellCfg.DOUBLE_DROPS && rule != null) {{
      {PKG}.Fortune.at(W.u, W.x[i], W.y[i], W.z[i]);   // 0.4.42: the Fortune sparkle's block
      {PKG}.Perks.breakDouble(pr, row, bt, W.wn, true);
    }}
''')
rep('''      {PKG}.Perks.harvestDouble(pr, this.bt, this.wn);
''', '''      {PKG}.Fortune.at(this.u, this.x, this.y, this.z);   // 0.4.42: the Fortune sparkle's block
      {PKG}.Perks.harvestDouble(pr, this.bt, this.wn);
''')

# ================================================================================================ players who left / shutdown
rep('''    {PKG}.Perks.DDMSG.keySet().retainAll(online);
''', '''    {PKG}.Perks.DDMSG.keySet().retainAll(online);
    {PKG}.Fortune.retain(online);   // 0.4.42: Fortune groups / block positions / sparkle stamps of players who left
''')
rep('''  {PKG}.SkillsHubOpen.unregister();     // 0.4.41: the Skills tab off the bridge (only while it still holds ours; never throws)
  super.shutdown();''', '''  {PKG}.SkillsHubOpen.unregister();     // 0.4.41: the Skills tab off the bridge (only while it still holds ours; never throws)
  try {{ {PKG}.Fortune.GRP.clear(); }} catch (Throwable t) {{ }}   // 0.4.42: a pending FortTask finds nothing to send
  super.shutdown();''')

# ================================================================================================ /settings switches (setup)
rep('''  {PKG}.SkillStore.regSetting("skills.doubleDrop", "Double drops", "skills", true, "Double drop x3! from the Mining, Foraging and Farming perks");''',
    '''  {PKG}.SkillStore.regSetting("skills.doubleDrop", "Double drops", "skills", true, "Fortune! +3 Oak Log, a soft sound and a sparkle when gathering gives extra drops");   // 0.4.42''')
rep('''  {PKG}.SkillStore.regSetting("skills.xbowHint", "Crossbow reload chat line", "combat", true, "Crossbow reloaded - 6 bolts back in - when your kept bolts return");
''', '''  {PKG}.SkillStore.regSetting("skills.xbowHint", "Crossbow reload chat line", "combat", true, "Crossbow reloaded - 6 bolts back in - when your kept bolts return");
  // 0.4.42: the Fortune indicator's message kind "fortune" - SkyyHud's two-switch pattern in the Messages tab (shown, then feed or chat)
  {PKG}.SkillStore.regSetting("msg.fortune", "Fortune drops", "messages", true, "Off = never shown. On = shown in the feed or in chat (the next switch).");
  {PKG}.SkillStore.regSetting("msg.fortune.feed", "Fortune drops: in the feed (off = chat)", "messages", true, "On = a card in the feed above the chat. Off = a line in chat.");
''')

# ================================================================================================ Server Setup rows
rep('''    ("perk.doubleDropMessage", "Double drop chat line", "perks", "bool", "true", "", "", "", "", "live",
     "'Double drop x3!'. Players can also hide it in /settings.", "reload"),''',
    '''    ("perk.doubleDropMessage", "Fortune indicator", "perks", "bool", "true", "", "", "", "", "live",
     "'Fortune! +3 Oak Log' line, sound and sparkle on extra drops. Players can hide it in /settings.", "reload"),''')
rep('''     "On: SkyyRebirth's stat boosts raise max Health, Mana, Stamina and class XP.", "reload"),
]''', '''     "On: SkyyRebirth's stat boosts raise max Health, Mana, Stamina and class XP.", "reload"),
    # 0.4.42: the Fortune indicator's sound + sparkle - G42_KEYS order
    ("sound.fortune", "Fortune sound", "sounds", "bool", "true", "", "", "", "", "live",
     "Gathering Fortune gives extra drops (once per group). Off for players who hide that line.", "reload"),
    ("sound.fortune.id", "Fortune sound id", "sounds", "text", "''' + FORT_SND + '''", "", "120", "", "", "live",
     "A vanilla sound event id (try it with /soundtest). Empty = no sound.", "reload;check=SkSnd.check"),
    ("fortune.sparkle", "Fortune sparkle", "perks", "bool", "true", "", "", "", "", "live",
     "A small sparkle at the block when Fortune gives extra drops. Only that player sees it.", "reload"),
]''')
rep('''assert [_r[0] for _r in CFG_ROWS][-19:-8] == G37_KEYS   # 0.4.39: the 8 G39 rows follow''',
    '''assert [_r[0] for _r in CFG_ROWS][-22:-11] == G37_KEYS   # 0.4.39: the 8 G39 rows follow; 0.4.42: then the 3 G42 rows''')
rep('''assert [_r[0] for _r in CFG_ROWS][-8:] == G39_KEYS
''', '''assert [_r[0] for _r in CFG_ROWS][-11:-3] == G39_KEYS
for _k42 in G42_KEYS:   # 0.4.42: every new key a row once, row default = the default file (= the code default)
    _r42 = [_r for _r in CFG_ROWS if _r[0] == _k42]
    assert len(_r42) == 1 and _dp.get(_k42) is not None and ("\\n" + _k42 + "=" + _dp[_k42] + "\\n") in ("\\n" + G42_DEFAULTS), _k42
assert [_r[0] for _r in CFG_ROWS][-3:] == G42_KEYS
''')
rep('''assert len(CFG_ROWS) == 249, ("0.4.39: + 8 rows''', '''assert len(CFG_ROWS) == 252, ("0.4.42: + 3 rows (sound.fortune + id, fortune.sparkle); 0.4.39: + 8 rows''')
rep('''"\\n" + G37_DEFAULTS + "\\n" + G39_DEFAULTS)   # 0.4.39: + G39''', '''"\\n" + G37_DEFAULTS + "\\n" + G39_DEFAULTS + "\\n" + G42_DEFAULTS)   # 0.4.42: + G42; 0.4.39: + G39''')

# ================================================================================================ the ready line + the jar's class list
rep('''"; sounds " + {PKG}.SkSnd.text() + "''', '''"; sounds " + {PKG}.SkSnd.text() + "; Fortune indicator (message kind fortune: /settings Messages - feed / chat / off, grouped " + {PKG}.Fortune.WIN + " ms; sparkle " + {PKG}.Fortune.PARTICLE + ")" + "''')
rep('''          hubb, hopen):   # 0.4.41: + HubBar, SkillsHubOpen;''', '''          hubb, hopen, fort42, ftask42):   # 0.4.42: + Fortune, FortTask; 0.4.41: + HubBar, SkillsHubOpen;''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "command / system registrations changed"
_i = s.index
assert _i("snd39.addField") < _i("public static boolean fortune(@PR@ pr)") < _i("fort42.addField") < _i("{PKG}.Fortune.hit(pr, drops);")
assert _i("ftask42.addConstructor") < _i("new @PKG@.FortTask(u)") < _i("@PKG@.Fortune.step(this.u") and _i("public static long step(") < _i("@PKG@.Fortune.step(this.u")
assert _i("public static void at(java.util.UUID u, int x") < _i("{PKG}.Fortune.at(W.u") and _i("public static void at(java.util.UUID u, int x") < _i("{PKG}.Fortune.at(this.u, fp.x()")
assert _i("public static void retain(java.util.Set online) {\n  GRP") < _i("{PKG}.Fortune.retain(online);")
assert s.count("{PKG}.Fortune.at(") == 3 and s.count("{PKG}.Fortune.hit(") == 1 and s.count('"Fortune! " + name(ids[0])') == 1 and s.count(".append(name(ids[i]))") == 1
for _keep in ("public static int rolls(java.util.UUID u, int row, int lvl, String fam) {", "public static int extras(double t, double r) {",
              "public static double fortune(java.util.UUID u, int row, int lvl, String fam) {", "public static void breakDouble({PR} pr, int row, {BTY} bt, String world, boolean tracked) {{",
              "public static void harvestDouble({PR} pr, {BTY} bt, String world) {{"):
    assert OLD.count(_keep) == 1 and s.count(_keep) == 1, "0.4.42: the drop maths stay: " + _keep
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.4.41 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines; 0.4.41 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
