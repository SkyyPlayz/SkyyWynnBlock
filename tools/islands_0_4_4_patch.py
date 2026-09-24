"""Derive SkyyIslands/build_skyyislands_0.4.4.py from 0.4.3 (0.4.3 stays untouched).
0.4.4: per-profile storage (tools/PROFILES-CONTRACT.md): one island per profile, islands/<pkey>.properties, new profiles get
skyy-island-<pkey>, protection / membership / visit resolve the ACTIVE profile island, island:<uuid> republished on epoch change.
Identical to 0.4.3 when SkyyProfiles is absent (pkey = uuid = profile 1). Full note in the new script's docstring.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.4.3.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.4.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


def block(start_marker, end_marker, new):
    """Replace s[start_marker .. end_marker) (end marker kept)."""
    global s
    assert s.count(start_marker) == 1, "block start missing or not unique: " + start_marker[:90]
    a = s.index(start_marker)
    b = s.index(end_marker, a)
    s = s[:a] + new + s[b:]


# ---- docstring + version
NOTE = r'''"""SkyyIslands 0.4.4 - build script
0.4.4: per-profile storage (tools/PROFILES-CONTRACT.md). One island per profile (SkyyProfiles). Without SkyyProfiles everything
  behaves exactly like 0.4.3 (pkey(u) = uuid = profile 1).
  - IslandStore.pkey(u) = the contract helper (bridge "profile:fn:key", fallback u.toString()). Island file = islands/<pkey>.properties;
    profile 1 = <uuid>.properties = every existing file, no migration. Profile 1 keeps its current world name; a new profile's island
    is created as skyy-island-<pkey> (e.g. skyy-island-<uuid>-p2) with its own starter kit (the kit flag lives in that profile's file).
  - World -> owner map (WORLD_OWNER) holds the owner's profile KEY (String); the creation guard (CREATING) is keyed by pkey (rule 2).
    IslandBuild captures the key when /island starts, so a switch during creation cannot write the wrong profile's file.
  - /island, /island home and a profile switch (SkyyProfiles dispatches /island) go to the ACTIVE profile's island (created on first
    use). /island visit <player> goes to the target player's ACTIVE profile island. /island invite <player> adds the player (UUID, any
    of their profiles - co-op is social, like Party) to YOUR active profile's island. /island info reads the active profile's file and
    shows "(profile <name>)" only when SkyyProfiles publishes profile:name:<uuid> (no fallback to the numeric profile id).
  - Protection: in an island world the owner is the player whose ACTIVE profile key owns it; members (player UUIDs in that island's
    file) and skyyislands.admin may build. On one of your OTHER profiles your island treats you as a visitor (profiles are separate
    saves, blocks must not carry items between them) and the message says to switch to that profile.
  - Bridge (rule 3, UUID-keyed): island:<uuid> = world name of the active profile's island (removed while it has none). SeenTick now
    runs every 5 s (SEEN pruning still every 10 s) and republishes when profile:epoch:<uuid> changes (last epoch per UUID in
    IslandStore.EPOCH, pruned on logout, so every login publishes once); IslandBuild republishes after creating an island.
  - Never touches the vanilla inventory (rule 5); the starter kit still goes into the new island's chest.

'''
rep('"""SkyyIslands 0.4.3 - build script' + LF, NOTE)
rep('VERSION = "0.4.3"', 'VERSION = "0.4.4"')

# ---- IslandStore: last-seen profile epoch per UUID
rep('st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();", st_))' + LF,
    'st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();", st_))' + LF
    + 'st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", st_))' + LF)

# ---- IslandStore: bridge + contract pkey() + key helpers, added before read() (javassist: no forward references)
PROFILE_HELPERS = r'''st_.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  java.util.Properties sp = System.getProperties();
  Object o = sp.get("skyy.bridge");
  if (o == null) {
    sp.putIfAbsent("skyy.bridge", new java.util.concurrent.ConcurrentHashMap());
    o = sp.get("skyy.bridge");
  }
  return (java.util.Map) o;
}""", st_))
# tools/PROFILES-CONTRACT.md helper, verbatim: storage key of the player's ACTIVE profile (uuid = profile 1 = no SkyyProfiles)
st_.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", st_))
# profile key -> owning player (a key is "<uuid>" or "<uuid>-p<N>"; UUID.toString() is always 36 chars)
st_.addMethod(CtNewMethod.make("""
public static java.util.UUID ownerUuid(String key) {
  if (key == null || key.length() < 36) return null;
  try { return java.util.UUID.fromString(key.substring(0, 36)); } catch (Throwable t) { return null; }
}""", st_))
# /island info label: ONLY the display name SkyyProfiles publishes (profile:name:<uuid>, same as SkyyCoins /balance); no fallback
# to the numeric profile id, control chars stripped, capped at 32 chars. Empty when SkyyProfiles is absent or publishes no name.
st_.addMethod(CtNewMethod.make("""
public static String profileLabel(java.util.UUID u) {
  try {
    Object n = bridge().get("profile:name:" + u);
    if (!(n instanceof String)) return "";
    String raw = ((String) n).trim();
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < raw.length() && sb.length() < 32; i++) {
      char c = raw.charAt(i);
      if (c >= ' ' && c != 127) sb.append(c);
    }
    String nm = sb.toString().trim();
    if (nm.length() > 0) return " (profile " + nm + ")";
  } catch (Throwable t) { }
  return "";
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized java.util.Properties read(String key) {
  java.util.Properties p = new java.util.Properties();
  try {
    java.nio.file.Path f = DIR.resolve(key + ".properties");
'''
rep('''st_.addMethod(CtNewMethod.make("""
public static synchronized java.util.Properties read(java.util.UUID u) {
  java.util.Properties p = new java.util.Properties();
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
''', PROFILE_HELPERS)
rep('  } catch (Throwable t) { warn("could not read island file for " + u + ": " + t); }',
    '  } catch (Throwable t) { warn("could not read island file " + key + ": " + t); }')

# ---- IslandStore.write: by profile key
rep('public static synchronized void write(java.util.UUID u, java.util.Properties p) {',
    'public static synchronized void write(String key, java.util.Properties p) {')
rep('    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");',
    '    java.nio.file.Path tmp = DIR.resolve(key + ".properties.tmp");')
rep('    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"),',
    '    java.nio.file.Files.move(tmp, DIR.resolve(key + ".properties"),')
rep('  } catch (Throwable t) { warn("could not write island file for " + u + ": " + t); }',
    '  } catch (Throwable t) { warn("could not write island file " + key + ": " + t); }')

# ---- IslandStore.loadIslandWorlds: owner = the file's profile key (skip names that do not start with a UUID, as before)
rep('          try { WORLD_OWNER.put(w.trim(), java.util.UUID.fromString(n.substring(0, n.length() - 11))); } catch (Throwable t) { }',
    '          String key = n.substring(0, n.length() - 11);' + LF
    + '          if (ownerUuid(key) != null) WORLD_OWNER.put(w.trim(), key);')

# ---- IslandStore: kit / owner / world name / members by profile key
STORE_TAIL = r'''st_.addMethod(CtNewMethod.make("""
public static synchronized boolean kitGiven(String key) {
  return "1".equals(read(key).getProperty("kit"));
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void setKitGiven(String key) {
  java.util.Properties p = read(key);
  p.setProperty("kit", "1");
  write(key, p);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String ownerOf(String worldName) {
  return worldName == null ? null : (String) WORLD_OWNER.get(worldName);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean isIslandWorld(String name) {
  return name != null && ISLAND_WORLDS.contains(name);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String worldName(String key) {
  String s = read(key).getProperty("world");
  return s == null || s.trim().isEmpty() ? null : s.trim();
}""", st_))
# bridge island:<uuid> = world of the ACTIVE profile's island (UUID-keyed, contract rule 3); called outside the IslandStore lock
st_.addMethod(CtNewMethod.make("""
public static void publish(java.util.UUID u) {
  if (u == null) return;
  try {
    java.util.Map b = bridge();
    String w = worldName(pkey(u));
    if (w == null) b.remove("island:" + u); else b.put("island:" + u, w);
  } catch (Throwable t) { }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void setWorldName(String key, String name) {
  java.util.Properties p = read(key);
  p.setProperty("world", name);
  p.setProperty("created", String.valueOf(System.currentTimeMillis()));
  ISLAND_WORLDS.add(name);
  WORLD_OWNER.put(name, key);
  write(key, p);
}""", st_))
# owner = the player whose ACTIVE profile owns the island; on another of their profiles they are a visitor there.
# members = player UUIDs in the island's file (any of their profiles).
st_.addMethod(CtNewMethod.make("""
public static boolean isMember(String ownerKey, java.util.UUID who) {
  if (ownerKey == null || who == null) return false;
  if (ownerKey.equals(pkey(who))) return true;
  if (who.equals(ownerUuid(ownerKey))) return false;
  String m = read(ownerKey).getProperty("members", "");
  return ("," + m + ",").indexOf("," + who.toString() + ",") >= 0;
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized boolean addMember(String ownerKey, java.util.UUID who) {
  if (who.equals(ownerUuid(ownerKey))) return false;
  java.util.Properties p = read(ownerKey);
  String m = p.getProperty("members", "");
  if (("," + m + ",").indexOf("," + who.toString() + ",") >= 0) return false;
  p.setProperty("members", m.isEmpty() ? who.toString() : m + "," + who.toString());
  write(ownerKey, p);
  return true;
}""", st_))

'''
block('st_.addMethod(CtNewMethod.make("""' + LF + 'public static synchronized boolean kitGiven(java.util.UUID u) {',
      '# ================= FillTask', STORE_TAIL)

# ---- FillTask + RelightNow: the world's owner is a profile key
rep('    java.util.UUID owner = {PKG}.IslandStore.ownerOf(world.getName());',
    '    String owner = {PKG}.IslandStore.ownerOf(world.getName());', count=2)

# ---- IslandBuild: carries the profile key captured when /island started
rep('bld.addField(CtField.make("public java.util.UUID owner;", bld))',
    'bld.addField(CtField.make("public String owner;", bld))')
rep('bld.addConstructor(CtNewConstructor.make("public IslandBuild(java.util.UUID u) { this.owner = u; }", bld))',
    'bld.addConstructor(CtNewConstructor.make("public IslandBuild(String key) { this.owner = key; }", bld))')
rep('    {PKG}.IslandStore.info("island world for " + owner + " = " + world.getName());' + LF,
    '    {PKG}.IslandStore.info("island world for " + owner + " = " + world.getName());' + LF
    + '    {PKG}.IslandStore.publish({PKG}.IslandStore.ownerUuid(owner));' + LF)

# ---- IslandCmd.go: owner = profile key; new islands are skyy-island-<pkey> (profile 1: skyy-island-<uuid>, as before)
rep('public static void go({ST} store, {REF} ref, {PR} pr, {WLD} from, java.util.UUID owner, boolean own) {{',
    'public static void go({ST} store, {REF} ref, {PR} pr, {WLD} from, String owner, boolean own) {{')
rep('    Long since = (Long) {PKG}.IslandStore.CREATING.get(u);',
    '    Long since = (Long) {PKG}.IslandStore.CREATING.get(owner);')
rep('    {PKG}.IslandStore.CREATING.put(u, Long.valueOf(System.currentTimeMillis()));',
    '    {PKG}.IslandStore.CREATING.put(owner, Long.valueOf(System.currentTimeMillis()));')
rep('spawnInstance("SkyyIsland", "skyy-island-" + u.toString(), from, ret);',
    'spawnInstance("SkyyIsland", "skyy-island-" + owner, from, ret);')
rep('    f = f.thenCompose(new {PKG}.IslandBuild(u));',
    '    f = f.thenCompose(new {PKG}.IslandBuild(owner));')

# ---- /island info: the active profile's island
rep('''  java.util.UUID u = pr.getUuid();
  String name = {PKG}.IslandStore.worldName(u);
  String members = {PKG}.IslandStore.read(u).getProperty("members", "");
  pr.sendMessage({MSG}.raw("[Island] " + (name == null ?''',
    '''  java.util.UUID u = pr.getUuid();
  String key = {PKG}.IslandStore.pkey(u);
  String name = {PKG}.IslandStore.worldName(key);
  String members = {PKG}.IslandStore.read(key).getProperty("members", "");
  pr.sendMessage({MSG}.raw("[Island]" + {PKG}.IslandStore.profileLabel(u) + " " + (name == null ?''')

# ---- /island invite: adds the player to YOUR active profile's island
rep('  if ({PKG}.IslandStore.addMember(u, target.getUuid())) {{',
    '  if ({PKG}.IslandStore.addMember({PKG}.IslandStore.pkey(u), target.getUuid())) {{')

# ---- /island visit: the target player's active profile island
rep('''  go(store, ref, pr, world, target.getUuid(), false);
  if (!{PKG}.IslandStore.isMember(target.getUuid(), pr.getUuid())) pr.sendMessage(''',
    '''  String tk = {PKG}.IslandStore.pkey(target.getUuid());
  go(store, ref, pr, world, tk, false);
  if (!{PKG}.IslandStore.isMember(tk, pr.getUuid())) pr.sendMessage(''')

# ---- /island home + root (plain /island, --action home|go): the active profile's island
rep('f"    {PKG}.IslandCmd.go(store, ref, pr, world, pr.getUuid(), true);"',
    'f"    {PKG}.IslandCmd.go(store, ref, pr, world, {PKG}.IslandStore.pkey(pr.getUuid()), true);"')
rep('go(store, ref, pr, world, u, true);', 'go(store, ref, pr, world, {PKG}.IslandStore.pkey(u), true);', count=2)

# ---- GuardSystem: owner = profile key
rep('    java.util.UUID owner = {PKG}.IslandStore.ownerOf(wn);',
    '    String owner = {PKG}.IslandStore.ownerOf(wn);')
rep('      pr.sendMessage({MSG}.raw("[Island] You can only build on islands you are a member of. Ask the owner for /island invite."));',
    '      if (u.equals({PKG}.IslandStore.ownerUuid(owner))) pr.sendMessage({MSG}.raw("[Island] This island belongs to another of your profiles - switch to that profile to build here."));' + LF
    + '      else pr.sendMessage({MSG}.raw("[Island] You can only build on islands you are a member of. Ask the owner for /island invite."));')

# ---- SeenTick: 5 s tick; SEEN pruned every 2nd run (= every 10 s as before) + profile epoch check -> republish island:<uuid>
SEEN_NEW = r'''seen.addInterface(pool.get("java.lang.Runnable"))
seen.addField(CtField.make("public int runs;", seen))
seen.addConstructor(CtNewConstructor.make("public SeenTick() { }", seen))
seen.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{ {PR} pr = ({PR}) it.next(); if (pr != null && pr.isValid()) online.add(pr.getUuid()); }}
    this.runs = this.runs + 1;
    if (this.runs % 2 == 0) {PKG}.IslandStore.SEEN.keySet().retainAll(online);
    {PKG}.IslandStore.EPOCH.keySet().retainAll(online);
    java.util.Map b = {PKG}.IslandStore.bridge();
    java.util.Iterator ou = online.iterator();
    while (ou.hasNext()) {{
      java.util.UUID u = (java.util.UUID) ou.next();
      Object e = b.get("profile:epoch:" + u);
      String es = e == null ? "none" : String.valueOf(e);
      Object last = {PKG}.IslandStore.EPOCH.get(u);
      if (last != null && last.equals(es)) continue;
      {PKG}.IslandStore.EPOCH.put(u, es);
      {PKG}.IslandStore.publish(u);
    }}
  }} catch (Throwable t) {{ }}
}}""", seen))
'''
block('seen.addInterface(pool.get("java.lang.Runnable"))' + LF,
      LF + '# ================= GuardSystem', SEEN_NEW)
rep('scheduleAtFixedRate(new {PKG}.SeenTick(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);',
    'scheduleAtFixedRate(new {PKG}.SeenTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);')

# ---- startup log + manifest
rep('(players: hytale:Adventurer), island protection on (hub "',
    '(players: hytale:Adventurer), island protection on, one island per profile (hub "')
rep('/island invite|visit for co-op. Zero dependencies."',
    '/island invite|visit for co-op, one island per profile (SkyyProfiles). Zero dependencies."')

assert not os.path.exists(dst), "refusing to overwrite " + dst
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "line endings", "CRLF" if NL == CR + LF else "LF")
