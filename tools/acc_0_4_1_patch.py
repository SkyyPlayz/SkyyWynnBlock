"""Derive SkyyAccessories/build_skyyaccessories_0.4.1.py from 0.4 (same style as acc_0_4_patch.py: rep(old, new) with asserted anchors,
newline-agnostic; 0.4 stays untouched, the line endings of 0.4 are preserved).
0.4.1 (Skyy 2026-09-23): PER-PROFILE STORAGE following tools/PROFILES-CONTRACT.md v1 (SkyyProfiles owns profiles; this mod keeps
working without it, zero dependencies):
 1. pkey(UUID) helper embedded in AccStore, byte-for-byte the contract's code (bridge "profile:fn:key" Function, falls back to
    uuid.toString() = profile 1). Without SkyyProfiles pkey = uuid, so every file name, cache key and bridge value is what 0.4 used.
 2. Rule 1: bag files are bags/<pkey>.properties (+ .properties.tmp for the atomic save). Profile 1 = the existing <uuid>.properties
    files, no migration.
 3. Rule 2: the in-memory BAGS cache is keyed by the pkey String (was the UUID), so a profile switch simply resolves another entry.
    Every store method resolves the key ONCE (slotsK(u, k) / saveK(u, k)), so a switch in the middle of an equip can never write one
    profile's slots into another profile's file. Locks stay per PLAYER (UUID): all bag operations of one player still serialize.
 4. Rule 3: acc:has:<uuid> / acc:tal:<uuid> stay keyed by UUID (they describe the ACTIVE profile). publish(u) remembers the
    profile:epoch:<uuid> it saw (EPOCH) and the key it published (PUBKEY); checkEpoch(u) republishes when the epoch changed or the
    active key differs from the published one (covers either write order inside SkyyProfiles). It runs in the existing 5 s AccTick
    (publishOnline) AND in the existing 1 s AccEffects per-player sync, so SkyySacks' craft tabs follow a switch within a second.
    Without SkyyProfiles the epoch is absent: checkEpoch returns false after one map lookup (no behaviour change).
 5. Rule 4: talisman stat modifiers, regen and the Speed movement source are recomputed from the new profile's bag by the existing
    per-second AccEffects sync (it reads AccStore.snapshot(u), which reads through pkey) - nothing else is kept per profile.
 6. Rule 5: the vanilla inventory is never touched for a switch (SkyyProfiles swaps it). The bag page remembers the key it was built
    for; a click after a profile switch only rebuilds the page on the current profile's bag (no equip/unequip on a stale page).
 7. Rule 6: nothing else here is per player data.
INTEGRATION PASS (2026-09-23, still 0.4.1 - checked against "Semantics of SkyyProfiles 0.1" at the end of PROFILES-CONTRACT.md):
 8. Semantics rule 5: bag Equip / Unequip move items between the live vanilla inventory and per-profile storage, so they are refused
    (page message, nothing moved) while profile:busy:<uuid> is present (a pending crash recovery at join: the recovery reloads the
    snapshot afterwards, so an equip would duplicate the item and an unequip would lose it). Also refused while SkyyProfiles is
    installed (profile:fn:key present) but profile:epoch:<uuid> is absent for this online player: per the semantics that means the
    players file is unreadable and the key function fell back to profile 1's key, so an equip/unequip would move items between
    profiles. AccStore.moveBlock(u) answers both (null = go).
 9. Semantics rule 1 (one key per operation): the page resolves pkey ONCE per click (checked against the key it was drawn for) and
    passes it to every store call of that click (canEquipK / equipK / unequipK / putK / stashK via giveBack), so the check, the move,
    the hand-back and the undo of one click can never land in two different profiles' bags. The UUID-only store methods remain as
    wrappers (pkey resolved once inside each).
Run:  python tools/acc_0_4_1_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.4.1.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.1.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


# ---------------------------------------------------------------- header / version
rep('''"""SkyyAccessories 0.4 - build script (derived from 0.3 by tools/acc_0_4_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.py            -> SkyyAccessories/SkyyAccessories-0.4.jar
       python build_skyyaccessories_0.4.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4: RARITY TIERS''', '''"""SkyyAccessories 0.4.1 - build script (derived from 0.4 by tools/acc_0_4_1_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.1.py            -> SkyyAccessories/SkyyAccessories-0.4.1.jar
       python build_skyyaccessories_0.4.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.1: per-profile storage (tools/PROFILES-CONTRACT.md) - one accessory bag per SkyyProfiles profile (full notes in
     tools/acc_0_4_1_patch.py):
     - AccStore.pkey(UUID) = the contract helper (bridge "profile:fn:key"; falls back to uuid = profile 1). Bag files
       bags/<pkey>.properties (profile 1 = the existing <uuid>.properties, no migration), BAGS cache keyed by the pkey String,
       each store method resolves the key once (slotsK / saveK), locks stay per player.
     - acc:has:<uuid> / acc:tal:<uuid> stay UUID keys for the ACTIVE profile and are republished when profile:epoch:<uuid> (or the
       active key) changes - checked in the 5 s AccTick and the 1 s AccEffects sync; talisman stats, regen and the Speed movement
       source follow the new profile's bag through the same per-second sync (it reads through pkey).
     - The bag page rebuilds instead of acting when the profile changed since it was drawn. Vanilla inventory untouched.
     - Integration pass: Equip/Unequip refused while profile:busy:<uuid> is set (pending crash recovery) or the player's profile
       state is unknown (SkyyProfiles installed, no profile:epoch:<uuid>); one pkey per click for every store call of that click.
     - Without SkyyProfiles every key is the UUID: behaviour identical to 0.4.
0.4 notes:
0.4: RARITY TIERS''')
rep('VERSION = "0.4"\n', 'VERSION = "0.4.1"\n')

# ---------------------------------------------------------------- AccStore: pkey helper + epoch state
rep('''st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAGS = new java.util.concurrent.ConcurrentHashMap();", st_))''',
    '''# 0.4.1: BAGS is keyed by the profile storage key (pkey String, PROFILES-CONTRACT rule 2), not the UUID
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAGS = new java.util.concurrent.ConcurrentHashMap();", st_))''')
rep('''st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();", st_))''',
    '''# 0.4.1 PROFILES-CONTRACT storage key helper (verbatim from tools/PROFILES-CONTRACT.md): active profile's key, uuid = profile 1
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
# 0.4.1 rule 3: EPOCH uuid -> profile:epoch:<uuid> seen at the last publish, PUBKEY uuid -> pkey the last publish used (pruned like PUBLISHED)
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBKEY = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static Object epochOf(java.util.UUID u) {
  try { return bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { return null; }
}""", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();", st_))''')

# ---------------------------------------------------------------- AccStore.slots -> slotsK(u, key) + slots(u) wrapper
rep('''st_.addMethod(CtNewMethod.make("""
public static String[] slots(java.util.UUID u) {
  String[] s = (String[]) BAGS.get(u);
  if (s != null) return s;
  synchronized (lock(u)) {
    s = (String[]) BAGS.get(u);
    if (s != null) return s;
    s = new String[CAP];
    try {
      java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");''', '''# 0.4.1: the bag of storage key k (bags/<k>.properties); lock stays per player
st_.addMethod(CtNewMethod.make("""
public static String[] slotsK(java.util.UUID u, String k) {
  String[] s = (String[]) BAGS.get(k);
  if (s != null) return s;
  synchronized (lock(u)) {
    s = (String[]) BAGS.get(k);
    if (s != null) return s;
    s = new String[CAP];
    try {
      java.nio.file.Path f = DIR.resolve(k + ".properties");''')
rep('''    } catch (Throwable t) { warn("could not load bag for " + u + ": " + t); }
    BAGS.put(u, s);
    return s;
  }
}""", st_))''', '''    } catch (Throwable t) { warn("could not load bag " + k + " for " + u + ": " + t); }
    BAGS.put(k, s);
    return s;
  }
}""", st_))
# 0.4.1: the bag of the player's ACTIVE profile
st_.addMethod(CtNewMethod.make("""
public static String[] slots(java.util.UUID u) {
  return slotsK(u, pkey(u));
}""", st_))''')

# ---------------------------------------------------------------- publish: active profile, remember epoch + key
rep('''public static void publish(java.util.UUID u) {{
  synchronized (lock(u)) {{
    String[] s = slots(u);''', '''public static void publish(java.util.UUID u) {{
  Object ep = epochOf(u);   // 0.4.1: read BEFORE the key, so a later switch always looks newer
  synchronized (lock(u)) {{
    String k = pkey(u);
    String[] s = slotsK(u, k);''')
rep('''    PUBLISHED.put(u, Boolean.TRUE);
  }}
}}""", st_))''', '''    PUBLISHED.put(u, Boolean.TRUE);
    if (ep == null) EPOCH.remove(u); else EPOCH.put(u, ep);
    PUBKEY.put(u, k);
  }}
}}""", st_))''')

# ---------------------------------------------------------------- save -> saveK(u, key) + save(u) wrapper
rep('''st_.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  synchronized (lock(u)) {
    try {
      String[] s = slots(u);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.util.Properties p = new java.util.Properties();
      for (int i = 0; i < s.length; i++) if (s[i] != null) p.setProperty("slot" + i, s[i]);
      java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
      java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
      try { p.store(out, "SkyyAccessories bag"); } finally { out.close(); }
      java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable t) { warn("could not save bag for " + u + ": " + t); }
    publish(u);
  }
}""", st_))''', '''# 0.4.1: saves the bag of storage key k (the key the caller resolved once), then republishes the active profile
st_.addMethod(CtNewMethod.make("""
public static void saveK(java.util.UUID u, String k) {
  synchronized (lock(u)) {
    try {
      String[] s = slotsK(u, k);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.util.Properties p = new java.util.Properties();
      for (int i = 0; i < s.length; i++) if (s[i] != null) p.setProperty("slot" + i, s[i]);
      java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
      java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
      try { p.store(out, "SkyyAccessories bag"); } finally { out.close(); }
      java.nio.file.Files.move(tmp, DIR.resolve(k + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable t) { warn("could not save bag " + k + " for " + u + ": " + t); }
    publish(u);
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  saveK(u, pkey(u));
}""", st_))''')

# ---------------------------------------------------------------- canEquip / equip / unequip / put / stash: one key per operation
# Integration pass: each is a K variant taking the storage key the CALLER resolved (the bag page resolves it once per click, semantics
# rule 1), plus the UUID-only wrapper (pkey resolved once) added right after it (javassist: callee before caller).
rep('''public static boolean canEquip(java.util.UUID u, String id) {{
  synchronized (lock(u)) {{
    String[] s = slots(u);''', '''public static boolean canEquipK(java.util.UUID u, String k, String id) {{
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);''')
rep('''    for (int i = 0; i < s.length; i++) if (s[i] == null) return true;
    return false;
  }}
}}""", st_))''', '''    for (int i = 0; i < s.length; i++) if (s[i] == null) return true;
    return false;
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean canEquip(java.util.UUID u, String id) {
  return canEquipK(u, pkey(u), id);
}""", st_))''')
rep('''public static String equip(java.util.UUID u, String id) {{
  synchronized (lock(u)) {{
    String[] s = slots(u);''', '''public static String equipK(java.util.UUID u, String k, String id) {{
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);''')
rep('''        String old = s[i]; s[i] = id; save(u); return old;''', '''        String old = s[i]; s[i] = id; saveK(u, k); return old;''')
rep('''    for (int i = 0; i < s.length; i++) if (s[i] == null) {{ s[i] = id; save(u); return ""; }}
    return null;
  }}
}}""", st_))''',
    '''    for (int i = 0; i < s.length; i++) if (s[i] == null) {{ s[i] = id; saveK(u, k); return ""; }}
    return null;
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String equip(java.util.UUID u, String id) {
  return equipK(u, pkey(u), id);
}""", st_))''')
rep('''public static String unequip(java.util.UUID u, int idx) {
  synchronized (lock(u)) {
    String[] s = slots(u);
    if (idx < 0 || idx >= s.length || s[idx] == null) return null;
    String id = s[idx]; s[idx] = null; save(u); return id;
  }
}""", st_))''', '''public static String unequipK(java.util.UUID u, String k, int idx) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    if (idx < 0 || idx >= s.length || s[idx] == null) return null;
    String id = s[idx]; s[idx] = null; saveK(u, k); return id;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String unequip(java.util.UUID u, int idx) {
  return unequipK(u, pkey(u), idx);
}""", st_))''')
rep('''public static void put(java.util.UUID u, int idx, String id) {
  synchronized (lock(u)) {
    String[] s = slots(u);
    if (idx < 0 || idx >= s.length) return;
    s[idx] = id; save(u);
  }
}""", st_))''', '''public static void putK(java.util.UUID u, String k, int idx, String id) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    if (idx < 0 || idx >= s.length) return;
    s[idx] = id; saveK(u, k);
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void put(java.util.UUID u, int idx, String id) {
  putK(u, pkey(u), idx, id);
}""", st_))''')
rep('''public static boolean stash(java.util.UUID u, String id) {
  synchronized (lock(u)) {
    String[] s = slots(u);
    for (int i = 0; i < s.length; i++) if (s[i] == null) { s[i] = id; save(u); return true; }
    return false;
  }
}""", st_))''', '''public static boolean stashK(java.util.UUID u, String k, String id) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    for (int i = 0; i < s.length; i++) if (s[i] == null) { s[i] = id; saveK(u, k); return true; }
    return false;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean stash(java.util.UUID u, String id) {
  return stashK(u, pkey(u), id);
}""", st_))
# Integration pass (semantics rule 5): null = item moves between the live inventory and this player's bag are safe right now, else the
# reason shown on the page. profile:busy:<uuid> = the live inventory may not belong to the active profile (pending crash recovery at
# join; a switch runs inside one world-thread task, so the page handler never sees that one). SkyyProfiles installed but no
# profile:epoch:<uuid> for an online player = its players file is unreadable and pkey fell back to profile 1's key (or the join work
# has not run yet): moving items now could carry them from one profile to another. Without SkyyProfiles both keys are absent -> null.
st_.addMethod(CtNewMethod.make("""
public static String moveBlock(java.util.UUID u) {
  try {
    java.util.Map b = bridge();
    String us = u.toString();
    if (b.get("profile:busy:" + us) != null) return "your profile is still loading - try again in a moment";
    if (b.get("profile:fn:key") != null && b.get("profile:epoch:" + us) == null) return "your profile is not loaded - try again in a moment - tell an admin if this stays";
  } catch (Throwable t) { }
  return null;
}""", st_))''')

# ---------------------------------------------------------------- epoch check (rule 3) in the existing 5 s tick
rep('''st_.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{''', '''# 0.4.1 PROFILES-CONTRACT rule 3: republish acc:has / acc:tal when profile:epoch:<uuid> changed since the last publish, or the active
# key is not the one published (either write order inside SkyyProfiles). Only after the first publish (0.4 timing kept). Without
# SkyyProfiles the epoch is absent on both sides -> false after one lookup. Called by publishOnline (5 s) and AccEffects (1 s).
st_.addMethod(CtNewMethod.make("""
public static boolean checkEpoch(java.util.UUID u) {
  if (u == null || !PUBLISHED.containsKey(u)) return false;
  Object ep = epochOf(u);
  Object last = EPOCH.get(u);
  boolean changed = (ep == null) ? (last != null) : !ep.equals(last);
  if (!changed) {
    if (ep == null) return false;
    Object pk = PUBKEY.get(u);
    if (pk == null || pk.equals(pkey(u))) return false;
  }
  publish(u);
  return true;
}""", st_))
st_.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{''')
rep('''      if (!PUBLISHED.containsKey(u)) publish(u);
    }}
    PUBLISHED.keySet().retainAll(online);''', '''      if (!PUBLISHED.containsKey(u)) publish(u);
      else checkEpoch(u);   // 0.4.1: profile switch -> republish
    }}
    PUBLISHED.keySet().retainAll(online);
    EPOCH.keySet().retainAll(online);
    PUBKEY.keySet().retainAll(online);''')

# ---------------------------------------------------------------- AccEffects: epoch check in the existing 1 s per-player sync
rep('''    c[0] = 0.0f;
    int[] best = {PKG}.AccDefs.bestTiers({PKG}.AccStore.snapshot(u));''', '''    c[0] = 0.0f;
    {PKG}.AccStore.checkEpoch(u);   // 0.4.1: republish acc:has / acc:tal within a second of a profile switch
    int[] best = {PKG}.AccDefs.bestTiers({PKG}.AccStore.snapshot(u));   // 0.4.1: reads the ACTIVE profile's bag (rule 4)''')

# ---------------------------------------------------------------- AccPage: never act on a page drawn for another profile
rep('''page.addField(CtField.make("public String[] invIds;", page))''', '''page.addField(CtField.make("public String[] invIds;", page))
page.addField(CtField.make("public String key;", page))   # 0.4.1: profile storage key the page was built for''')
rep('''  String[] s = {PKG}.AccStore.snapshot(u);
  String bs = "Style: TextButtonStyle(''', '''  this.key = {PKG}.AccStore.pkey(u);   // 0.4.1
  String[] s = {PKG}.AccStore.snapshot(u);
  String bs = "Style: TextButtonStyle(''')
rep('''    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    for (int i = 0; i < {PKG}.AccStore.CAP; i++) {{''', '''    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    String k = {PKG}.AccStore.pkey(u);   // integration pass: ONE storage key for everything this click does (semantics rule 1)
    if (this.key != null && !this.key.equals(k)) {{   // 0.4.1: profile switched since this page was drawn
      this.info = "your profile changed - this is the bag of your current profile now";
      rebuild(); return;
    }}
    String blk = {PKG}.AccStore.moveBlock(u);   // integration pass: profile:busy / unknown profile state -> move nothing
    if (blk != null) {{ this.info = blk; rebuild(); return; }}
    for (int i = 0; i < {PKG}.AccStore.CAP; i++) {{''')
# integration pass: every store call of the click uses that key k
rep('''      String id = {PKG}.AccStore.unequip(u, i);''', '''      String id = {PKG}.AccStore.unequipK(u, k, i);''')
rep('''{PKG}.AccStore.put(u, i, id);''', '''{PKG}.AccStore.putK(u, k, i, id);''')
rep('''      if (!{PKG}.AccStore.canEquip(u, put)) {{''', '''      if (!{PKG}.AccStore.canEquipK(u, k, put)) {{''')
rep('''      String res = {PKG}.AccStore.equip(u, put);''', '''      String res = {PKG}.AccStore.equipK(u, k, put);''')
rep('''        int g = giveBack(player, u, id);''', '''        int g = giveBack(player, u, k, id);''')
rep('''        int g = giveBack(player, u, res);''', '''        int g = giveBack(player, u, k, res);''')
rep('''public static int giveBack({PLA} p, java.util.UUID u, String id) {{
  if (giveOne(p, id)) return 0;
  if ({PKG}.AccStore.stash(u, id)) return 1;''', '''public static int giveBack({PLA} p, java.util.UUID u, String k, String id) {{
  if (giveOne(p, id)) return 0;
  if ({PKG}.AccStore.stashK(u, k, id)) return 1;   // integration pass: the bag of the click's key k''')

# ---------------------------------------------------------------- log line + manifest
rep('''talismans in 5 rarities (percent layer on)" );''', '''talismans in 5 rarities (percent layer on), one bag per profile when SkyyProfiles runs" );''')
rep('''speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol. Zero dependencies."''',
    '''speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol; one bag per SkyyProfiles profile when that mod is installed. Zero dependencies."''')

assert 'VERSION = "0.4.1"' in s
assert "BAGS.get(u)" not in s and "BAGS.put(u" not in s, "a UUID-keyed bag cache access is left"
assert "u.toString() + \".properties" not in s, "a UUID bag file name is left"
assert s.count("save(u);") == 0, "a save(u) call inside a key-resolving method is left"
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4
print("wrote", dst)
