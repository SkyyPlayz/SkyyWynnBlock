"""Derive SkyyEssentials/build_skyyessentials_0.1.9.py from 0.1.8 (build_skyyessentials_0.1.8.py = the tools/deploy_set.py SET pin).
Run:  python tools/essentials_0_1_9_patch.py   then   python SkyyEssentials/build_skyyessentials_0.1.9.py   (never --deploy: coordinated deploy)
Check: python SkyyEssentials/test_skyyessentials_0.1.9.py   (bare JVM, -Xverify:all; nothing is deployed)
SkyyEssentials uses patch scripts since 0.1.4: edit THIS file, never the generated build script.

0.1.9 = THE CHAT MIRROR (docs/answered/project.md LOCKED 2026-10-08, Skyy: "the chat mirror sounds good. just be sure to delete logs when
you are done with them, so they dont take up my storage space on my pc."): every chat / system message the server sends a player is ALSO
written to the server log as ONE INFO line
    [Chat] to <player name>: <plain text>
(formatting / colour codes stripped; translation keys resolved with the server's own en-US table the way the engine's
MessageUtil.formatMessageToPlainString does, else the key + its params), so Claude reads test output without screenshots.
WHERE (one place for every mod - vanilla, other mods, ours): an OUTBOUND PACKET FILTER on the chat packet. The engine facts (read from the
server jar's bytecode at build time, the build stops when one changes):
  - PlayerRef.sendMessage(Message) is the ONLY place the engine builds a ServerMessage (protocol.packets.interface_.ServerMessage, the
    one chat packet; ChatType has one value, Chat): new ServerMessage(ChatType.Chat, message.getFormattedMessage()) -> writeNoCache.
  - writeNoCache -> writePacket(p, false); writePacket runs PacketAdapters.__handleOutbound FIRST, on the CALLER's thread (the world
    thread, a scheduler thread, ...), before anything is queued or flushed.
  - PacketAdapters.registerOutbound(PlayerPacketFilter) wraps it in a lambda that hands over GamePacketHandler.getPlayerRef() (the
    SkyySacks 0.7.12 CraftPacketFilter pattern; SkyySacks itself is not touched).
  - EVERY outbound write path runs __handleOutbound (writePacket for one packet, handleOutboundAndCachePackets for an array).
  ChatMirrorF.test ALWAYS returns false (true would DROP the packet) and catches everything: it never throws on any thread. Cost per
  packet: one volatile read + up to three instanceof; per chat line: a ThreadLocal read, one short synchronized rate check, the text walk.
TOASTS AND TITLES (fix round, critic finding): the Notification packet (NotificationUtil.sendNotification - SkyyClasses / SkyyGear gate
  and level-up toasts) and the ShowEventTitle packet (EventTitleUtil) carry text a player sees too, so the same filter mirrors them:
    [Chat] to <name>: [Toast] <message> | <secondary message>
    [Chat] to <name>: [Title] <primary title> | <secondary title>
  (same text rules, maxLen, rate cap). Kill feed lines and HUD / page text are NOT mirrored.
SERVER SETUP (category "Chat log", tools/skyycfg.py rows; all live):
  chat.mirror          bool, default ON   - off = nothing is written (the filter stays registered: one volatile read per packet)
  chat.mirror.maxLen   int 40-4000, default 300 - a longer text is cut to maxLen characters ending in "..."
  chat.mirror.rateCap  int 10-10000, default 600 - lines a minute per player; over it lines are left out and ONE line
                       "[Chat] to <name>: (N lines skipped - over <cap> a minute)" is written when that minute ends (at the next line for
                       that player or by EssTick within ~2 s). Logs stay small (Skyy cares about disk space; worst case ~180 KB a minute
                       per player at 300 chars) but a move's debug toggle printing every hit (Skyy 2026-10-08: "all i have to do is run
                       the probe command for the data to appear in chat") fits under it (fix round: 200 was too low for that).
  chat.mirror.private  bool, default OFF (danger, asks when turned ON) - private messages between two players (/msg /tell /w /whisper,
                       /reply, /r <text>: SkyyEssentials' own pm(), the only 1:1 player message on the server - vanilla has none, no other
                       Skyy mod sends one) are NEVER logged unless this is on. NOT covered (fix round, critic finding): GROUP chat -
                       SkyyParty /pc lines and SkyyGuilds [Guild] lines go through plain PlayerRef.sendMessage and ARE logged once per
                       member (marking them needs SkyyParty / SkyyGuilds changes: a later round if Skyy wants it). The row help says so.
                       pm() sends its two text lines through EssStore.sayPm, which
                       marks the sending thread (ChatMirror.PM_SEND) around PlayerRef.sendMessage; the filter runs inside that call on the
                       same thread (writePacket -> __handleOutbound is synchronous) and skips the line. The refusal / usage lines of /msg
                       carry no message text and are logged like any system line.
No saved data (the rate book is in memory, swept every 2 s; nothing on disk but the 4 config lines). No assets.
Version 0.1.9. Nothing else changes: commands, bridge keys, the other rows, files, /trade, /tpa, warps, durability, the no-trade list.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.8.py")
dst = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.9.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


# ================================================================================================ docstring + version
DOC = '''SkyyEssentials 0.1.9 - build script (javassist via jpype). GENERATED by tools/essentials_0_1_9_patch.py from 0.1.8
(build_skyyessentials_0.1.8.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyyessentials_0.1.9.py            -> SkyyEssentials/SkyyEssentials-0.1.9.jar   (never --deploy: tools/deploy_set.py)
Check: python test_skyyessentials_0.1.9.py            (bare JVM, -Xverify:all: the 0.1.8 checks + the chat mirror through the engine path)

0.1.9 (2026-10-08, Skyy: "the chat mirror sounds good. just be sure to delete logs when you are done with them"; docs/answered/project.md):
  THE CHAT MIRROR: every chat / system line the server sends a player is also ONE server-log INFO line "[Chat] to <name>: <plain text>".
  One outbound PlayerPacketFilter (ChatMirrorF, always returns false) on the ServerMessage packet - PlayerRef.sendMessage is the only
  place the engine builds one, and writePacket runs the filters first on the caller's thread (engine facts checked at build time).
  Text = the engine's own plain-text rules (rawText; messageId through I18nModule en-US + MessageUtil.formatText, else the key + params;
  children), colour / markup / control characters stripped, cut to chat.mirror.maxLen with "...". Rate cap chat.mirror.rateCap lines a
  minute per player, then one "N lines skipped" line. Private messages (pm(): /msg /reply /r) never logged unless chat.mirror.private
  (party / guild GROUP chat is logged). Toasts (Notification) and event titles (ShowEventTitle) are mirrored too: "[Toast] ..." /
  "[Title] ...", main | secondary text.
  Rows (category "Chat log"): chat.mirror (ON), chat.mirror.maxLen (300), chat.mirror.rateCap (600), chat.mirror.private (OFF).
  setup() registers the filter after the tpa bridge (own try), shutdown() removes it; EssTick sweeps the rate book. No saved data.

'''
first = s.index('"""') + 3
s = s[:first] + DOC + s[first:]
rep('\nVERSION = "0.1.8"\n', '\nVERSION = "0.1.9"\n')

# ================================================================================================ engine facts + probes
FACTS = '''
# ================= 0.1.9: the chat mirror's ENGINE FACTS (read from the server jar's bytecode; a game update that changes one stops the build)
CM_SMSG = "com.hypixel.hytale.protocol.packets.interface_.ServerMessage"
CM_FMSG = "com.hypixel.hytale.protocol.FormattedMessage"
CM_PKT = "com.hypixel.hytale.protocol.Packet"
CM_PAD = "com.hypixel.hytale.server.core.io.adapter.PacketAdapters"
CM_PPF = "com.hypixel.hytale.server.core.io.adapter.PlayerPacketFilter"
CM_PFI = "com.hypixel.hytale.server.core.io.adapter.PacketFilter"
CM_I18 = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"
CM_MUT = "com.hypixel.hytale.server.core.util.MessageUtil"
CM_PV = "com.hypixel.hytale.protocol."
CM_NOTE = "com.hypixel.hytale.protocol.packets.interface_.Notification"       # fix round: toasts
CM_TITLE = "com.hypixel.hytale.protocol.packets.interface_.ShowEventTitle"    # fix round: event titles
for _c, _m in ((CM_NOTE, "message"), (CM_NOTE, "secondaryMessage"), (CM_TITLE, "primaryTitle"), (CM_TITLE, "secondaryTitle"),
               (CM_PAD, "registerOutbound"), (CM_PAD, "deregisterOutbound"), (CM_PPF, "test"), (CM_SMSG, "message"),
               (CM_FMSG, "rawText"), (CM_FMSG, "messageId"), (CM_FMSG, "children"), (CM_FMSG, "params"), (CM_FMSG, "messageParams"),
               (CM_FMSG, "markupEnabled"), (CM_I18, "get"), (CM_I18, "getMessage"), (CM_MUT, "formatText"),
               (CM_PV + "StringParamValue", "value"), (CM_PV + "IntParamValue", "value"), (CM_PV + "LongParamValue", "value"),
               (CM_PV + "DoubleParamValue", "value"), (CM_PV + "BoolParamValue", "value"), (PR, "sendMessage"), (PR, "getUsername")):
    B.probe(pool, _c, _m)


def _cm_code(cls, meth, sig=None):
    for mm in pool.get(cls).getDeclaredMethods():
        if str(mm.getName()) == meth and (sig is None or sig in str(mm.getSignature())):
            bo = _jp.JClass("java.io.ByteArrayOutputStream")()
            _jp.JClass("javassist.bytecode.InstructionPrinter")(_jp.JClass("java.io.PrintStream")(bo)).print_(mm)
            return str(bo.toString())
    raise SystemExit("0.1.9 chat mirror engine check: %s.%s not found in the server jar" % (cls, meth))


def _cm_in_order(txt, needles):
    i = 0
    for nd in needles:
        j = txt.find(nd, i)
        if j < 0:
            return nd
        i = j + len(nd)
    return None


CM_FACTS = [
    ("PlayerRef.sendMessage builds a ServerMessage(ChatType.Chat, message.getFormattedMessage()) and sends it with writeNoCache",
     PR, "sendMessage", "(Lcom/hypixel/hytale/server/core/Message;)V",
     ["new", "ServerMessage", "ChatType.Chat", "getFormattedMessage", "ServerMessage.<init>", "PacketHandler.writeNoCache"]),
    ("PacketHandler.writeNoCache = writePacket(p, false)", "com.hypixel.hytale.server.core.io.PacketHandler", "writeNoCache", None,
     ["iconst_0", "PacketHandler.writePacket"]),
    ("PacketHandler.writePacket runs the outbound filters FIRST (before the channel write), on the caller's thread",
     "com.hypixel.hytale.server.core.io.PacketHandler", "writePacket", None, ["PacketAdapters.__handleOutbound", "ifeq", "getChannel", "write"]),
    ("a PlayerPacketFilter is called with the GamePacketHandler's PlayerRef",
     CM_PAD, "lambda$registerOutbound$1", None, ["GamePacketHandler", "getPlayerRef", "PlayerPacketFilter.test"]),
    ("PacketHandler.handleOutboundAndCachePackets (the array write path) runs the outbound filters too",
     "com.hypixel.hytale.server.core.io.PacketHandler", "handleOutboundAndCachePackets", None, ["PacketAdapters.__handleOutbound"]),
    ("NotificationUtil.sendNotification (toasts) builds a Notification from Message.getFormattedMessage and sends it with writeNoCache",
     "com.hypixel.hytale.server.core.util.NotificationUtil", "sendNotification", "NotificationStyle;Ljava/lang/String;)V",
     ["new", "interface_.Notification", "getFormattedMessage", "PacketHandler.writeNoCache"]),
    ("EventTitleUtil.showEventTitleToPlayer builds a ShowEventTitle and sends it with writeNoCache",
     "com.hypixel.hytale.server.core.util.EventTitleUtil", "showEventTitleToPlayer", "FFF)V",
     ["new", "ShowEventTitle", "getFormattedMessage", "ShowEventTitle.<init>", "PacketHandler.writeNoCache"]),
    ("the engine's plain text: rawText, else messageId through I18nModule en-US + MessageUtil.formatText, then the children",
     CM_MUT, "appendFormattedMessage", None, ["FormattedMessage.rawText", "FormattedMessage.messageId", "I18nModule.get", "en-US",
                                              "I18nModule.getMessage", "MessageUtil.formatText", "FormattedMessage.children"]),
]
_cm_bad = []
for (_what, _cls, _meth, _sig, _needles) in CM_FACTS:
    _miss = _cm_in_order(_cm_code(_cls, _meth, _sig), _needles)
    if _miss is not None:
        _cm_bad.append("%s (%s.%s: no %r in order)" % (_what, _cls.rsplit(".", 1)[1], _meth, _miss))
if _cm_bad:
    raise SystemExit("0.1.9 chat mirror engine check FAILED - the mirror would not see every chat line:\\n  " + "\\n  ".join(_cm_bad))
# the ONLY engine class that builds a ServerMessage is PlayerRef (its clone / toObject aside): scanned in the server jar
import zipfile as _cmz
from jpype import JClass as _cmJ
_cm_builders = set()
with _cmz.ZipFile(J["server_jar"]) as _z:
    for _n in _z.namelist():
        if _n.endswith(".class") and _n.startswith("com/hypixel/") and b"interface_/ServerMessage" in _z.read(_n):
            _cn = _n[:-6].replace("/", ".")
            if _cn == CM_SMSG:
                continue
            try:
                _cc = pool.get(_cn)
            except Exception:
                continue
            for _mm in list(_cc.getDeclaredMethods()) + list(_cc.getDeclaredConstructors()):
                try:
                    _bo = _jp.JClass("java.io.ByteArrayOutputStream")()
                    _jp.JClass("javassist.bytecode.InstructionPrinter")(_jp.JClass("java.io.PrintStream")(_bo)).print_(_mm)
                except Exception:
                    continue
                if "ServerMessage.<init>" in str(_bo.toString()):
                    _cm_builders.add(_cn)
if _cm_builders != {PR}:
    raise SystemExit("0.1.9 chat mirror engine check FAILED - ServerMessage is built outside PlayerRef.sendMessage: %s" % sorted(_cm_builders))
print("chat mirror engine facts: %d verified + ServerMessage built only by PlayerRef" % len(CM_FACTS))
'''
rep('''assert "testFilter" in _ca and "FilterActionType.ADD" in _ca, "SimpleItemContainer.cantAddToSlot no longer asks the ADD slot filters"
''', '''assert "testFilter" in _ca and "FilterActionType.ADD" in _ca, "SimpleItemContainer.cantAddToSlot no longer asks the ADD slot filters"
''' + FACTS)

# ================================================================================================ the classes (kit fields exist before TCfg / the kit)
rep('''edur.addField(CtField.make("public static volatile boolean ON = false;", edur))
''', '''edur.addField(CtField.make("public static volatile boolean ON = false;", edur))
# 0.1.9: the chat mirror (ChatMirror = the text + rate book + log line; ChatMirrorF = the outbound packet filter). The four kit fields
# exist before TCfg compiles its get / put and before the config kit is emitted.
cm   = pool.makeClass(PKG + ".ChatMirror")
cmf  = pool.makeClass(PKG + ".ChatMirrorF")
cm.addField(CtField.make("public static volatile boolean ON = true;", cm))
cm.addField(CtField.make("public static volatile int MAX_LEN = 300;", cm))
cm.addField(CtField.make("public static volatile int RATE_CAP = 600;", cm))
cm.addField(CtField.make("public static volatile boolean PRIV = false;", cm))
# set by EssStore.sayPm around the PlayerRef.sendMessage of a private message's text (the filter runs inside that call, same thread)
cm.addField(CtField.make("public static final ThreadLocal PM_SEND = new ThreadLocal();", cm))
''')

CM_CODE = r'''# ================= 0.1.9: THE CHAT MIRROR (docs/answered/project.md 2026-10-08) =================
# every ServerMessage a player is sent -> one INFO line "[Chat] to <name>: <plain text>" in the server log. Nothing here may throw on the
# caller's thread (any thread that sends chat): every entry point catches everything.
_CMT = {"@PR@": PR, "@PKG@": PKG, "@ES@": ES, "@SMSG@": CM_SMSG, "@FMSG@": CM_FMSG, "@PKT@": CM_PKT, "@PAD@": CM_PAD, "@PPF@": CM_PPF,
        "@PFI@": CM_PFI, "@I18@": CM_I18, "@MUT@": CM_MUT, "@PV@": CM_PV, "@NOTE@": CM_NOTE, "@TITLE@": CM_TITLE}


def _cmj(src):
    for k_, v_ in _CMT.items():
        src = src.replace(k_, v_)
    assert "@" not in src.replace("@Override", ""), src[:200]
    return src


def _cmm(cls, src):
    cls.addMethod(CtNewMethod.make(_cmj(src), cls))


cm.addField(CtField.make(_cmj("public static volatile @PFI@ FILTER;"), cm))
cm.addField(CtField.make("public static final long WINDOW_MS = 60000L;", cm))
cm.addField(CtField.make("public static final java.util.HashMap RATE = new java.util.HashMap();", cm))     # UUID -> long[] { window start, lines, skipped }
cm.addField(CtField.make("public static final java.util.HashMap NAMES = new java.util.HashMap();", cm))    # UUID -> the last name seen
cm.addField(CtField.make("public static volatile boolean FAILED = false;", cm))
cm.addField(CtField.make("public static volatile long LINES = 0L;", cm))       # lines written (the ready line / the harness)
cm.addField(CtField.make("public static volatile long DROPPED = 0L;", cm))     # lines left out by the rate cap
cm.addField(CtField.make("public static volatile long HIDDEN = 0L;", cm))      # private-message lines not written
# one log line, literal (flogger log(String) does no % formatting, so chat text with % is safe)
_cmm(cm, r"""
public static void emit(String line) {
  try {
    if (@ES@.LOG != null) @ES@.LOG.at(java.util.logging.Level.INFO).log(line);
    LINES = LINES + 1L;
  } catch (Throwable t) { }
}""")
# a piece of text as ONE plain line: section-sign colour codes (2 chars) dropped, <...> tags dropped when the node has markup on, line
# breaks / tabs -> one space, other control characters dropped
_cmm(cm, r"""
public static String clean(String s, boolean markup) {
  if (s == null) return "";
  int n = s.length();
  StringBuilder b = new StringBuilder(n);
  for (int i = 0; i < n; i++) {
    char c = s.charAt(i);
    if (c == 167) { i++; continue; }
    if (markup && c == '<') {
      int j = s.indexOf('>', i);
      if (j > i && j - i <= 80) { i = j; continue; }
    }
    if (c == 10 || c == 13 || c == 9) { b.append(' '); continue; }
    if (c < 32 || c == 127 || (c >= 128 && c < 160)) continue;
    b.append(c);
  }
  return b.toString();
}""")
_cmm(cm, r"""
public static String param(Object v) {
  if (v == null) return "null";
  if (v instanceof @PV@StringParamValue) return String.valueOf(((@PV@StringParamValue) v).value);
  if (v instanceof @PV@IntParamValue) return String.valueOf(((@PV@IntParamValue) v).value);
  if (v instanceof @PV@LongParamValue) return String.valueOf(((@PV@LongParamValue) v).value);
  if (v instanceof @PV@DoubleParamValue) return String.valueOf(((@PV@DoubleParamValue) v).value);
  if (v instanceof @PV@BoolParamValue) return String.valueOf(((@PV@BoolParamValue) v).value);
  return String.valueOf(v);
}""")
# the translation of a key (en-US, the engine's own plain-text language), or null when the server has none
_cmm(cm, r"""
public static String tr(String key) {
  try {
    @I18@ i = @I18@.get();
    if (i == null) return null;
    return i.getMessage("en-US", key);
  } catch (Throwable t) { return null; }
}""")
# walk(b, m, depth, cap): the engine's MessageUtil.appendFormattedMessage rules (rawText, else the key's translation formatted with the
# params, then the children), plus: an unknown key is written as "key {name=value, ...}" (params and message params, by name), text is
# cleaned, depth <= 12, stops once b is past cap. Recursive, so the body is set after the method exists.
_cm_walk = CtNewMethod.make(_cmj("public static void walk(StringBuilder b, @FMSG@ m, int depth, int cap) { }"), cm)
cm.addMethod(_cm_walk)
_cm_walk.setBody(_cmj(r"""{
  StringBuilder b = $1;
  @FMSG@ m = $2;
  int depth = $3;
  int cap = $4;
  if (b == null || m == null || depth > 12 || b.length() > cap) return;
  boolean mk = m.markupEnabled;
  if (m.rawText != null) b.append(clean(m.rawText, mk));
  else if (m.messageId != null) {
    String t = tr(m.messageId);
    if (t != null) {
      String f = t;
      try { f = @MUT@.formatText(t, m.params, m.messageParams); } catch (Throwable e) { f = t; }
      b.append(clean(f, mk));
    } else {
      b.append(clean(m.messageId, false));
      boolean any = false;
      if (m.params != null && !m.params.isEmpty()) {
        java.util.Iterator it = new java.util.TreeMap(m.params).entrySet().iterator();
        while (it.hasNext()) {
          java.util.Map.Entry e = (java.util.Map.Entry) it.next();
          b.append(any ? ", " : " {").append(String.valueOf(e.getKey())).append('=').append(clean(param(e.getValue()), false));
          any = true;
        }
      }
      if (m.messageParams != null && !m.messageParams.isEmpty()) {
        java.util.Iterator it2 = new java.util.TreeMap(m.messageParams).entrySet().iterator();
        while (it2.hasNext()) {
          java.util.Map.Entry e2 = (java.util.Map.Entry) it2.next();
          b.append(any ? ", " : " {").append(String.valueOf(e2.getKey())).append('=');
          any = true;
          Object v = e2.getValue();
          if (v instanceof @FMSG@) walk(b, (@FMSG@) v, depth + 1, cap);
          else b.append(clean(String.valueOf(v), false));
        }
      }
      if (any) b.append('}');
    }
  }
  if (m.children != null) {
    for (int i = 0; i < m.children.length; i++) walk(b, m.children[i], depth + 1, cap);
  }
}"""))
# the whole line text: trimmed, cut to max characters ending in "..." (never splits a surrogate pair)
_cmm(cm, r"""
public static String cut(String s, int max) {
  if (max < 4) max = 4;
  if (s.length() <= max) return s;
  int cut = max - 3;
  if (cut > 0 && Character.isHighSurrogate(s.charAt(cut - 1))) cut--;
  return s.substring(0, cut).trim() + "...";
}""")
_cmm(cm, r"""
public static String textOf(@FMSG@ m, int max) {
  if (max < 4) max = 4;
  StringBuilder b = new StringBuilder();
  walk(b, m, 0, max + 64);
  return cut(b.toString().trim(), max);
}""")
# fix round: a toast / title = main text " | " secondary text (either may be missing), cut to max as ONE text
_cmm(cm, r"""
public static String textOf2(@FMSG@ a, @FMSG@ b, int max) {
  if (max < 4) max = 4;
  String s1 = a == null ? "" : textOf(a, max);
  String s2 = b == null ? "" : textOf(b, max);
  if (s1.length() == 0) return s2;
  if (s2.length() == 0) return s1;
  return cut(s1 + " | " + s2, max);
}""")
_cmm(cm, r"""
public static String skipLine(String name, long n, int cap) {
  return "[Chat] to " + name + ": (" + n + " line" + (n == 1L ? "" : "s") + " skipped - over " + cap + " a minute)";
}""")
# the rate book (one short lock): -1 = over the cap (left out, counted), else the number of lines a FINISHED minute skipped (0 = none)
_cmm(cm, r"""
public static synchronized long admit(java.util.UUID u, String name, long now) {
  long[] st = (long[]) RATE.get(u);
  long flushed = 0L;
  if (st == null) {
    st = new long[3];
    st[0] = now;
    RATE.put(u, st);
  } else if (now - st[0] >= WINDOW_MS || now < st[0]) {
    flushed = st[2];
    st[0] = now;
    st[1] = 0L;
    st[2] = 0L;
  }
  NAMES.put(u, name);
  int cap = RATE_CAP;
  if (cap > 0 && st[1] >= (long) cap) {
    st[2] = st[2] + 1L;
    DROPPED = DROPPED + 1L;
    return -1L;
  }
  st[1] = st[1] + 1L;
  return flushed;
}""")
# every finished minute leaves the book (no growth for players who left); one skipped line each for those that skipped any
_cmm(cm, r"""
public static synchronized java.util.ArrayList sweep(long now) {
  java.util.ArrayList out = null;
  java.util.Iterator it = RATE.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    long[] st = (long[]) e.getValue();
    if (now - st[0] < WINDOW_MS && now >= st[0]) continue;
    if (st[2] > 0L) {
      if (out == null) out = new java.util.ArrayList();
      out.add(skipLine(String.valueOf(NAMES.get(e.getKey())), st[2], RATE_CAP));
    }
    NAMES.remove(e.getKey());
    it.remove();
  }
  return out;
}""")
_cmm(cm, r"""
public static synchronized void clear() {
  RATE.clear();
  NAMES.clear();
}""")
# EssTick (every 2 s, the scheduler thread)
_cmm(cm, r"""
public static void tick() {
  try {
    java.util.ArrayList l = sweep(System.currentTimeMillis());
    if (l == null) return;
    for (int i = 0; i < l.size(); i++) emit((String) l.get(i));
  } catch (Throwable t) { }
}""")
# THE ENTRY (ChatMirrorF.test, on whatever thread sends the line): never throws; logs nothing while chat.mirror is off
_cmm(cm, r"""
public static void outbound(@PR@ pr, Object pkt) {
  try {
    if (!ON || pkt == null || pr == null) return;
    @FMSG@ fm = null;
    @FMSG@ f2 = null;
    String tag = "";
    if (pkt instanceof @SMSG@) {
      if (PM_SEND.get() != null && !PRIV) { HIDDEN = HIDDEN + 1L; return; }
      fm = ((@SMSG@) pkt).message;
    } else if (pkt instanceof @NOTE@) {
      fm = ((@NOTE@) pkt).message;
      f2 = ((@NOTE@) pkt).secondaryMessage;
      tag = "[Toast] ";
    } else if (pkt instanceof @TITLE@) {
      fm = ((@TITLE@) pkt).primaryTitle;
      f2 = ((@TITLE@) pkt).secondaryTitle;
      tag = "[Title] ";
    } else return;
    if (fm == null && f2 == null) return;
    String name = String.valueOf(pr.getUsername());
    long f = admit(pr.getUuid(), name, System.currentTimeMillis());
    if (f < 0L) return;
    if (f > 0L) emit(skipLine(name, f, RATE_CAP));
    String t = f2 == null ? textOf(fm, MAX_LEN) : textOf2(fm, f2, MAX_LEN);
    if (t.length() == 0) return;
    emit("[Chat] to " + name + ": " + tag + t);
  } catch (Throwable t) {
    if (!FAILED) {
      FAILED = true;
      @ES@.warn("chat mirror: a chat line could not be written to the log (warned once): " + t);
    }
  }
}""")
_cmm(cm, r"""
public static String note() {
  return "chat mirror " + (FILTER == null ? "NOT registered" : (ON ? "ON" : "off")) + " ([Chat] lines in the server log: chat, toasts, titles; max " + MAX_LEN
    + " chars, " + RATE_CAP + " lines a minute per player, private messages " + (PRIV ? "LOGGED" : "never logged") + ")";
}""")
_cmm(cm, r"""
public static synchronized void stop() {
  @PFI@ f = FILTER;
  FILTER = null;
  if (f != null) {
    try { @PAD@.deregisterOutbound(f); } catch (Throwable t) { }
  }
  RATE.clear();
  NAMES.clear();
}""")
# ChatMirrorF: the outbound PlayerPacketFilter (chat, toasts, titles). ALWAYS false (true would drop the packet); never throws
cmf.addInterface(pool.get(CM_PPF))
cmf.addConstructor(CtNewConstructor.make("public ChatMirrorF() { }", cmf))
_cmm(cmf, r"""
public boolean test(@PR@ pr, @PKT@ pkt) {
  try {
    if (@PKG@.ChatMirror.ON && (pkt instanceof @SMSG@ || pkt instanceof @NOTE@ || pkt instanceof @TITLE@)) @PKG@.ChatMirror.outbound(pr, pkt);
  } catch (Throwable t) { }
  return false;
}""")
# setup(): a second start first removes the first filter (two filters = every line twice)
_cmm(cm, r"""
public static synchronized String start() {
  stop();
  FAILED = false;
  try {
    FILTER = @PAD@.registerOutbound((@PPF@) new @PKG@.ChatMirrorF());
  } catch (Throwable t) {
    FILTER = null;
    @ES@.warn("chat mirror: the outbound filter could not be registered - chat is not written to the log: " + t);
  }
  return note();
}""")
# a private message's text line (pm(): /msg /reply /r): marked for the filter, which skips it unless chat.mirror.private is on
es.addMethod(CtNewMethod.make(f"""
public static void sayPm({PR} p, String text, String color) {{
  {PKG}.ChatMirror.PM_SEND.set(Boolean.TRUE);
  say(p, text, color);
  {PKG}.ChatMirror.PM_SEND.remove();
}}""", es))

'''
PM_ANCHOR = '''es.addMethod(CtNewMethod.make(f"""
public static void pm({PR} pr, {PR} target, String text) {{'''
rep(PM_ANCHOR, CM_CODE + PM_ANCHOR)
rep('''  say(pr, "[you -> " + target.getUsername() + "] " + text, PM);
''', '''  sayPm(pr, "[you -> " + target.getUsername() + "] " + text, PM);
''')
rep('''  say(target, "[" + pr.getUsername() + (g == 2 ? " (staff)" : "") + " -> you] " + text, PM);
''', '''  sayPm(target, "[" + pr.getUsername() + (g == 2 ? " (staff)" : "") + " -> you] " + text, PM);
''')
# EssTick: the rate book sweep (every 2 s)
rep('''    if (this.n % 5 == 0) {ES}.prune();
  }} catch (Throwable t) {{ {ES}.warn("tick failed: " + t); }}''', '''    if (this.n % 5 == 0) {ES}.prune();
    {PKG}.ChatMirror.tick();
  }} catch (Throwable t) {{ {ES}.warn("tick failed: " + t); }}''')

# ================================================================================================ config: loader rows + file + kit rows
rep('''Empty = every item can be traded."),
]
IDX = dict(''', '''Empty = every item can be traded."),
    # 0.1.9 (fields in ChatMirror): the chat mirror (Skyy 2026-10-08)
    ("chat.mirror", "Chat mirror on", "bool", "@PKG@.ChatMirror.ON", 0, 1, "true", "",
     "chat.mirror: true (the default) = every chat / system line, toast and event title the server sends a player is also written to the server log as one line: [Chat] to <name>: <text> (colours stripped; toasts start [Toast], titles [Title]). false = nothing is written."),
    ("chat.mirror.maxLen", "Longest logged line (characters)", "int", "@PKG@.ChatMirror.MAX_LEN", 40, 4000, "300", "",
     "chat.mirror.maxLen: a logged chat line longer than this many characters is cut and ends with ... (40-4000)."),
    ("chat.mirror.rateCap", "Most logged lines a minute", "int", "@PKG@.ChatMirror.RATE_CAP", 10, 10000, "600", "",
     "chat.mirror.rateCap: at most this many chat lines a minute per player go to the log; the rest are left out and one 'N lines skipped' line is written (10-10000). Keeps the log small."),
    ("chat.mirror.private", "Log private messages", "bool", "@PKG@.ChatMirror.PRIV", 0, 1, "false", "",
     "chat.mirror.private: false (the default) = private messages between two players (/msg, /reply, /r) are never written to the log. true = they are logged like any chat line. Party and guild chat (/pc, [Guild] lines) are group chat and are always logged while chat.mirror is on."),
]
IDX = dict(''')
rep('''IDX["privacy.staffBypass"]] + list(range(0, 13)) + [IDX["tradeBlockedItems"], IDX["gameplay.durability"]]''',
    '''IDX["privacy.staffBypass"]] + list(range(0, 13)) + [IDX["tradeBlockedItems"], IDX["gameplay.durability"]] \\
    + [IDX["chat.mirror"], IDX["chat.mirror.maxLen"], IDX["chat.mirror.rateCap"], IDX["chat.mirror.private"]]''')
rep('''               20: "# ---- gameplay (SkyyEssentials 0.1.6) ----"}''', '''               20: "# ---- gameplay (SkyyEssentials 0.1.6) ----", 21: "# ---- chat mirror: chat lines in the server log (SkyyEssentials 0.1.9) ----"}''')
rep('''            ("trade", "Trade")]
CF = "@config.properties:"''', '''            ("trade", "Trade"), ("chat", "Chat log")]
CF = "@config.properties:"''')
rep('''     "field:TCfg.SAVE_MS" + CF + "tradeSaveDelayMillis"),
]''', '''     "field:TCfg.SAVE_MS" + CF + "tradeSaveDelayMillis"),
    # 0.1.9: the chat mirror (Skyy 2026-10-08: "the chat mirror sounds good"). live: ChatMirror reads the fields on every line.
    # chat.mirror.private is danger + confirm=on: turning it ON asks (it puts players' private texts into the log); off never asks.
    ("chat.mirror", "Chat mirror (server log)", "chat", "bool", "true", "", "", "", "", "live",
     "On: every chat line, toast and title a player gets is also logged as [Chat] to Name: text.",
     "field:ChatMirror.ON" + CF + "chat.mirror"),
    ("chat.mirror.maxLen", "Longest logged line (characters)", "chat", "int", "300", "40", "4000", "step=10", "", "live",
     "Longer chat lines are cut to this many characters and end with ... in the log.",
     "field:ChatMirror.MAX_LEN" + CF + "chat.mirror.maxLen"),
    ("chat.mirror.rateCap", "Most logged lines a minute", "chat", "int", "600", "10", "10000", "step=10", "", "live",
     "Per player. Over it, lines are left out and one N lines skipped line is logged instead.",
     "field:ChatMirror.RATE_CAP" + CF + "chat.mirror.rateCap"),
    ("chat.mirror.private", "Log private messages", "chat", "bool", "false", "", "", "", "", "live,danger",
     "On: /msg, /reply, /r texts are logged too (default off). Party and guild chat are always logged.",
     "field:ChatMirror.PRIV" + CF + "chat.mirror.private;confirm=on"),
]''')

# ================================================================================================ setup / shutdown / class list / manifest
rep('''  try { @ES@.publishFns(); } catch (Throwable tf) { fNote = "tpa bridge off (error)"; @ES@.warn("could not publish the tpa bridge (SkyyParty's TPA buttons): " + tf); }
''', '''  try { @ES@.publishFns(); } catch (Throwable tf) { fNote = "tpa bridge off (error)"; @ES@.warn("could not publish the tpa bridge (SkyyParty's TPA buttons): " + tf); }
  // 0.1.9: the chat mirror's outbound packet filter (own try: a problem costs only the [Chat] log lines)
  String cNote = "chat mirror off (error)";
  try { cNote = @PKG@.ChatMirror.start(); } catch (Throwable tc) { @ES@.warn("could not start the chat mirror: " + tc); }
''')
rep('''+ fNote + "; " + rNote''', '''+ fNote + "; " + cNote + "; " + rNote''')
rep('''  @ES@.unpublishFns();
''', '''  @ES@.unpublishFns();
  // 0.1.9: the chat mirror's filter goes
  try { @PKG@.ChatMirror.stop(); } catch (Throwable tc) { }
''')
rep('''MINE = [rq, es, hop, mv, rd, fly, tick, efn] + OLD_CMDS''', '''MINE = [rq, es, hop, mv, rd, fly, tick, efn, cm, cmf] + OLD_CMDS''')
rep('''Magic Bags and the Accessory Bag never trade (no-trade list), every setting''',
    '''Magic Bags and the Accessory Bag never trade (no-trade list), a chat mirror (every chat line, toast and title a player gets is also one [Chat] line in the server log; private messages only when switched on), every setting''')

# ================================================================================================ checks on the generated text
code = s
assert code.count("registerCommand(") == REG0 and code.count("registerSystem(") == SYS0
assert code.count("sayPm(") == 3                                   # the method + pm's two text lines
_pm = code[code.index("public static void pm({PR} pr, {PR} target, String text) {{"):]
_pm = _pm[:_pm.index('}}""", es))')]
assert "+ text, PM)" in _pm and _pm.count("+ text, PM)") == 2 and "say(pr, \"[you" not in _pm and "say(target, \"[" not in _pm
assert code.index("public static void sayPm(") < code.index("public static void pm(") < code.index("tick.addMethod(")
assert code.index('cm   = pool.makeClass(PKG + ".ChatMirror")') < code.index('tcfg  = pool.makeClass(PKG + ".TCfg")')
_su = code[code.index("public void setup() {"):]
assert _su.index("@ES@.publishFns();") < _su.index("@PKG@.ChatMirror.start();") < _su.index("@PKG@.CfgPub.start(")
assert "B.deploy(" not in code and "enable_in_world(" not in code
for _t in ("[Chat] to ", " skipped - over ", "chat mirror: ", "[Toast] ", "[Title] ", "RATE_CAP = 600;"):
    assert _t in code

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == CR + LF else "LF"))
