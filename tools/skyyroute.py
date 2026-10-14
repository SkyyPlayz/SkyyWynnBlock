"""SKYY MESSAGE ROUTE - one source of truth for every sender mod that moves a chat line into SkyyHud's notification feed.
Used at BUILD time by SkyySkills 0.4.34+, SkyyClasses 0.1.20+ and SkyyCollections 0.2.12+ (each jar gets its own copy of the MsgRoute
class in its own package - no runtime dependency between the mods; every copy is generated from THIS file, so they behave the same).

Skyy 2026-10-12 (docs/answered/ui.md, CHAT OVERFLOW): "watch for things i probably wont notice, and figure out ways to reduce the chat
overflow while still giving players the info they need. the chat has top move slow enough people can read it for server use. (unless we
set up a second notification system that uses our widgets or something.)"

THE BRIDGE API (SkyyHud 0.3.20+, read from SkyyHud/build_skyyhud_0.3.21.py - never edited here; java.lang types only):
  msgroute:fn:get  apply(Object[] { UUID, String kind }) -> "chat" | "feed" | "off"   (the player's own Chat / Feed / Off switch, else the
                   Server Setup > Messages default; "feed" already falls back to "chat" when that player's Feed / Skills widget is off)
  feed:fn:push     apply(Object[] { UUID, String kind, String itemId or null, String text, Number count or null }) -> Boolean
                   (TRUE = the player WILL see it; FALSE = send the chat line yourself)
  xpflash:fn:push  apply(Object[] { UUID, String skill, Number amount }) -> Boolean (TRUE = flashes on the Skills widget; FALSE = chat)

RULES every sender follows (MsgRoute):
  - route(u, kind): asks msgroute:fn:get, cached per player + kind for TTL ms (2 s) - a per-pickup / per-hit sender never calls the
    bridge more than once every 2 s per player (lag rules, research/Code-Structure-Audit.md: memory only, no lock held, no I/O).
    No SkyyHud / an old SkyyHud without msgroute:fn:get / anything but "feed" or "off" = "chat" = the old chat line, unchanged.
  - "off" = nothing is sent (the player's choice). "feed" = feed(...) / flash(...); a FALSE answer = the old chat line after all
    (nothing a player chose to see ever vanishes).
  - said(text): every routed chat line is counted (CHAT) and, while the harness seam SAID is set, recorded.
  - The cache is bounded (cleared at 4096 entries) and forget(u) drops a player's entries (called on leave where the mod has a hook).
  - gate(u, kind, key, newMs, sameMs) (review fix 2026-10-13): at most one NEW feed card key per newMs per player + kind (the same key passes, but
    not within sameMs) -
    SkyyHud turns a card pushed out of its 4-card stack before it was drawn into a chat line, so burst senders must not flood it.
  - br() caches the skyy.bridge map once (BR): a mod whose own bridge() still locks System.class (SkyyClasses, SkyyCollections) takes
    that lock only on the first call (research/Code-Structure-Audit.md finding 1).
"""

FIELDS = (
    "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
    "public static final java.util.concurrent.atomic.AtomicLong CHAT = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong FEED = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong FLASH = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong OFF = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong BACK = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong ASKS = new java.util.concurrent.atomic.AtomicLong();",
    "public static volatile long TTL = 2000L;",
    "public static volatile java.util.List SAID = null;",    # HARNESS SEAM ONLY (null): every routed chat line sent
    "public static volatile java.util.Map BR = null;",       # the skyy.bridge map, cached once (never locks after the first call)
    "public static final java.util.concurrent.ConcurrentHashMap GATE = new java.util.concurrent.ConcurrentHashMap();",   # gate(): last card per player + kind
)

# @BR@ = a Java expression giving the skyy.bridge java.util.Map (the mod's own lock-free bridge())
METHODS = (
    r"""
public static java.util.Map br() {
  java.util.Map m = BR;
  if (m != null) return m;
  m = @BR@;
  BR = m;
  return m;
}""",
    r"""
public static java.util.function.Function fn(String k) {
  try {
    java.util.Map m = br();
    Object f = m == null ? null : m.get(k);
    return f instanceof java.util.function.Function ? (java.util.function.Function) f : null;
  } catch (Throwable t) { return null; }
}""",
    r"""
public static String ask(java.util.UUID u, String kind) {
  java.util.function.Function f = fn("msgroute:fn:get");
  if (f == null) return "chat";
  ASKS.incrementAndGet();
  try {
    Object r = f.apply(new Object[] { u, kind });
    if ("feed".equals(r)) return "feed";
    if ("off".equals(r)) return "off";
  } catch (Throwable t) { }
  return "chat";
}""",
    r"""
public static String route(java.util.UUID u, String kind) {
  if (u == null || kind == null) return "chat";
  String k = kind + "|" + u.toString();
  long now = System.currentTimeMillis();
  Object o = CACHE.get(k);
  if (o instanceof Object[]) {
    Object[] e = (Object[]) o;
    if (((Long) e[1]).longValue() > now) return (String) e[0];
  }
  String r = ask(u, kind);
  if (CACHE.size() > 4096) CACHE.clear();
  CACHE.put(k, new Object[] { r, Long.valueOf(now + TTL) });
  return r;
}""",
    r"""
public static boolean feed(java.util.UUID u, String kind, String icon, String text, long n) {
  java.util.function.Function f = fn("feed:fn:push");
  if (f == null || u == null || kind == null || text == null || text.length() == 0) { BACK.incrementAndGet(); return false; }
  try {
    Long c = n > 0L ? Long.valueOf(n) : null;
    Object r = f.apply(new Object[] { u, kind, icon, text, c });
    if (Boolean.TRUE.equals(r)) { FEED.incrementAndGet(); return true; }
  } catch (Throwable t) { }
  BACK.incrementAndGet();
  return false;
}""",
    r"""
public static boolean flash(java.util.UUID u, String skill, long amt) {
  java.util.function.Function f = fn("xpflash:fn:push");
  if (f == null || u == null || skill == null || amt <= 0L) { BACK.incrementAndGet(); return false; }
  try {
    Object r = f.apply(new Object[] { u, skill, Long.valueOf(amt) });
    if (Boolean.TRUE.equals(r)) { FLASH.incrementAndGet(); return true; }
  } catch (Throwable t) { }
  BACK.incrementAndGet();
  return false;
}""",
    # REVIEW FIX (2026-10-13): SkyyHud keeps at most 4 cards and turns a card pushed out before it was ever drawn into a CHAT line
    # (Feed.addCard -> overflow -> flushOver). A sender that can push many DIFFERENT cards in one burst (a sickle over 5 crops, a felled tree
    # with several item types) asks gate() first: a new card key (kind + icon / text) is allowed once per newMs per player + kind; the same
    # key as the last one passes (SkyyHud merges it into that card) but no card of that kind passes within sameMs of the last one passed
    # (0 = no limit). false = skip the card (the caller keeps / merges the amount or drops it - never a chat line).
    r"""
public static boolean gate(java.util.UUID u, String kind, String key, long newMs, long sameMs) {
  if (u == null || kind == null) return true;
  String k = kind + "|" + u.toString();
  long now = System.currentTimeMillis();
  Object o = GATE.get(k);
  if (o instanceof Object[]) {
    Object[] e = (Object[]) o;
    long lastNew = ((Long) e[1]).longValue();
    long lastAny = ((Long) e[2]).longValue();
    if (now >= lastAny && now - lastAny < sameMs) return false;
    if (key != null && key.equals(e[0])) { e[2] = Long.valueOf(now); return true; }
    if (now >= lastNew && now - lastNew < newMs) return false;
  }
  if (GATE.size() > 4096) GATE.clear();
  GATE.put(k, new Object[] { key, Long.valueOf(now), Long.valueOf(now) });
  return true;
}""",
    r"""
public static void said(String s) {
  CHAT.incrementAndGet();
  java.util.List l = SAID;
  if (l != null && s != null) l.add(s);
}""",
    r"""
public static void off() {
  OFF.incrementAndGet();
}""",
    r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String s = "|" + u.toString();
  java.util.Iterator it = CACHE.keySet().iterator();
  while (it.hasNext()) { if (((String) it.next()).endsWith(s)) it.remove(); }
  java.util.Iterator gi = GATE.keySet().iterator();
  while (gi.hasNext()) { if (((String) gi.next()).endsWith(s)) gi.remove(); }
}""",
    # "Wood_Oak_Trunk" -> "Wood Oak Trunk" ("Plant_Crop_Pumpkin_Item" -> "Plant Crop Pumpkin"): the chat lines' own item naming, shorter
    r"""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id.replace('_', ' ').trim();
  if (s.endsWith(" Item")) s = s.substring(0, s.length() - 5);
  return s;
}""",
    r"""
public static String stats() {
  return "chat " + CHAT.get() + ", feed " + FEED.get() + ", flash " + FLASH.get() + ", off " + OFF.get() + ", back to chat " + BACK.get() + ", asks " + ASKS.get();
}""",
)


def add_msg_route(cls, CtField, CtNewMethod, bridge_expr):
    """Adds the MsgRoute fields + methods to the (empty) CtClass cls. bridge_expr = the mod's lock-free bridge() call."""
    for f in FIELDS:
        cls.addField(CtField.make(f, cls))
    for m in METHODS:
        cls.addMethod(CtNewMethod.make(m.replace("@BR@", bridge_expr), cls))
