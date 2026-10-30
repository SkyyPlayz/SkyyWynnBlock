"""Derive SkyyUiProbe/build_skyyuiprobe_0.9.py + test_skyyuiprobe_0.9.py from the 0.8 SET pin (0.8 is left untouched; CRLF kept).
Run:  python tools/uiprobe_0_9_patch.py   then   python SkyyUiProbe/build_skyyuiprobe_0.9.py   (never --deploy)
Check: python SkyyUiProbe/test_skyyuiprobe_0.9.py [--keep] [--old-jar <the 0.8 jar>]

0.9 = the price-tooltip probe R0 (research/Price-Tooltips-Spec.md section 5: R0 row, probes P1-P5, "For the local session") folded into the
combined UI probe (research/UI-Queue-Spec.md). Skyy 2026-10-30: "work through your whole list. always use the best model for the job, to get
the most out of our tokens. you can run in parallel, and use ultracode when it helps." (RESUME NEXT 6: "price tooltips
(research/Price-Tooltips-Spec.md: R0 probe -> Auctions -> Bazaar)"); the spec's [bracket] defaults are taken.

EVERY 0.8 case stays as it is (Skyy has not run /skyprobe tour yet). New, op only (the same skyyuiprobe.admin node, no permission groups):
  /uiprobe tip <item id> <text>       ONE UpdateTranslations(AddOrUpdate) packet to the CALLER only: the item's description key -> <text>
                                       ("\\n" = a new line, surrounding quotes dropped; <text> = reset sends the server's own text back)
  /uiprobe tiplater <item id> <text>  the same, 5 s later from the probe's timer thread (NOT the world thread) - P2: hover with the
                                       inventory open while it lands
  /uiprobe tipgear                    gives you ONE probe item (Weapon_Claws_Tribal - see below) whose ItemDisplayMetadata description has
                                       a Message.translation("server.skyy.probe.tip") child, then sends that key (P3)
  /uiprobe tip gear <text>            sends a new text for that key only (P3 "does it update after a new send?")
No real stack is ever changed: tip / tiplater touch no ItemStack at all; tipgear builds ONE fresh stack (new ItemStack + withMetadata on
that new object, before it is in any inventory) and adds it storage first, then hotbar, counted before and after.

ENGINE FACTS read for this round (HytaleServer.jar bytecode, tools/dev/bcfull.py, 2026-10-30; build-time asserted below):
  KEY FORM: the Init packet (I18nModule.sendTranslations = new UpdateTranslations(Init, getMessages(lang)) via writeNoCache) carries the
    FULL key with the "server." prefix: loadMessagesFrom puts getPrefix(dir, file) + key, getPrefix = <sub dirs with '.'> + <file name
    without .lang> + "." (concat recipe "\\1\\1."), so server.lang's "items.X.description" is "server.items.X.description" in the map
    (the engine's own synthetic keys in the same map are "server.items.\\1.bench.descriptiveLabel"). Item.getDescriptionTranslationKey()
    = TranslationProperties.Description, or "server.items." + id + ".description" when the item JSON names none. So the probe sends the
    item's own getDescriptionTranslationKey() and, when that differs, ALSO "server.items.<id>.description" in the same packet.
  OFF-THREAD: PacketHandler.writeNoCache(p) = writePacket(p, false) = PacketAdapters.__handleOutbound, then the Netty
    ChannelConnection.write / writeAndFlush (no world state). The engine itself calls it off the world thread: I18nModule.start schedules
    flushPendingLanguages (-> sendTranslations -> writeNoCache) on a ScheduledExecutorService, and addDefaultMessages broadcasts AddOrUpdate
    from the asset-load thread (Universe.broadcastPacketNoCache). So it is safe off the world thread; tiplater does exactly that in game.

WHY CLAWS, NOT A SWORD (decision): SkyyGear's GearView stamps every Weapon_* gear id (Weapon_Sword_Iron included) with ITS OWN
ItemDisplayMetadata on the next inventory scan (a /give'd sword "gets the legacy Normal"), which would overwrite the probe's description and
fake a P3 FAIL. Weapon_Claws_Tribal is a vanilla weapon SkyyGear leaves alone (gear.exclude default Weapon_Claws_; SkyyClasses: claws stay
unassigned), so the probe text survives. The client question (a translation child inside an ItemDisplay FormattedMessage) is the same.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "SkyyUiProbe")


def load(name):
    b = open(os.path.join(D, name), "rb").read()
    assert b.count(b"\r\n") == b.count(b"\n"), name + ": expected CRLF only"
    return b.decode("utf-8").replace("\r\n", "\n")


def save(name, s):
    assert "\r" not in s
    with open(os.path.join(D, name), "wb") as f:
        f.write(s.replace("\n", "\r\n").encode("utf-8"))
    print("wrote", os.path.join("SkyyUiProbe", name))


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, "anchor found %d times (want %d): %r" % (c, n, old[:120])
    return s.replace(old, new)


# ===================================================================================================== the build script
S = load("build_skyyuiprobe_0.8.py")
S = rep(S, '"""SkyyUiProbe 0.8 - build script', '"""SkyyUiProbe 0.9 - build script')
S = rep(S, "Run:   python SkyyUiProbe/build_skyyuiprobe_0.8.py    -> SkyyUiProbe/SkyyUiProbe-0.8.jar (no --deploy on purpose)",
        "Run:   python SkyyUiProbe/build_skyyuiprobe_0.9.py    -> SkyyUiProbe/SkyyUiProbe-0.9.jar (no --deploy on purpose)")
S = rep(S, "Check: python SkyyUiProbe/test_skyyuiprobe_0.8.py   (J jar,", "Check: python SkyyUiProbe/test_skyyuiprobe_0.9.py   (J jar,")
S = rep(S, "Skyy's words (docs/answered/ui.md 2026-10-22 UI QUEUE)",
        """0.9 (tools/uiprobe_0_9_patch.py - read its header for the engine facts): + the PRICE-TOOLTIP PROBE R0 of research/Price-Tooltips-Spec.md
section 5, every 0.8 case kept. Op only: /uiprobe tip <item id> <text> (ONE UpdateTranslations AddOrUpdate for the item's description key,
to you only; "\\n" = new line; reset = the server's own text back), /uiprobe tiplater <item id> <text> (the same 5 s later from the timer
thread), /uiprobe tipgear (one probe Weapon_Claws_Tribal whose ItemDisplayMetadata description has a translation child
server.skyy.probe.tip, then that key is sent), /uiprobe tip gear <text> (a new text for that key). No real stack is touched.

Skyy's words (docs/answered/ui.md 2026-10-22 UI QUEUE)""")
S = rep(S, 'VERSION = "0.8"', 'VERSION = "0.9"')
# build-time checks of the vanilla ids the tip probe names (vanilla first: all three exist in Assets.zip)
S = rep(S, """for _ids in list(ICONS.values()) + [list(HUB_ICON.values()), list(FEED_ICONS)]:
    for _i in _ids:
        assert _i in _vanilla_items, "icon %s is not a vanilla item" % _i
""", """for _ids in list(ICONS.values()) + [list(HUB_ICON.values()), list(FEED_ICONS)]:
    for _i in _ids:
        assert _i in _vanilla_items, "icon %s is not a vanilla item" % _i
# 0.9 tip probe (Price-Tooltips-Spec R0): the probe item + the P1 / P5 example ids are vanilla items
TIP_ITEM = "Weapon_Claws_Tribal"          # NOT a sword: SkyyGear GearView re-stamps Weapon_* gear with its own ItemDisplayMetadata
TIP_KEY = "server.skyy.probe.tip"         # the translation child of the probe item (only this jar names it; never in a lang file)
TIP_LATER_MS = 5000
for _i in (TIP_ITEM, "Wood_Oak_Trunk", "Plant_Crop_Wheat_Item"):
    assert _i in _vanilla_items, "tip probe: %s is not a vanilla item" % _i
""")
# tokens
S = rep(S, '''    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
}''', '''    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
    "UTR": "com.hypixel.hytale.protocol.packets.assets.UpdateTranslations",
    "UTY": "com.hypixel.hytale.protocol.UpdateType",
    "IDM": "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "ISTX": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "TIPIT": TIP_ITEM, "TIPKEY": TIP_KEY, "TIPMS": str(TIP_LATER_MS),
}''')
S = rep(S, """TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")
""", """# 0.9 tip probe: every engine member it calls + the two facts the probe stands on (tools/uiprobe_0_9_patch.py header)
for c, m in ((T["ITM"], "getAssetMap"), (T["ITM"], "getDescriptionTranslationKey"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             (T["I18N"], "get"), (T["I18N"], "getMessages"), (T["I18N"], "getMessage"), (T["PR"], "getLanguage"), (T["PH"], "writeNoCache"),
             (T["UTY"], "AddOrUpdate"), (T["IDM"], "KEYED_CODEC"), (T["IS"], "withMetadata"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"),
             (T["IS"], "isEmpty"), (T["PLA"], "getInventory"), (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["IC"], "addItemStack"),
             (T["IC"], "getCapacity"), (T["IC"], "getItemStack"), (T["ISTX"], "succeeded"), (T["ISTX"], "getRemainder"), (T["MSG"], "translation"),
             (T["APC"], "addSubCommand"), (T["APC"], "getName")):
    B.probe(pool, c, m)
_ctors = lambda cls: [str(x.getSignature()) for x in pool.get(cls).getDeclaredConstructors()]
assert "(Lcom/hypixel/hytale/protocol/UpdateType;Ljava/util/Map;)V" in _ctors(T["UTR"]), "UpdateTranslations(UpdateType, Map) changed"
assert "(Lcom/hypixel/hytale/server/core/Message;Lcom/hypixel/hytale/server/core/Message;)V" in _ctors(T["IDM"]), "ItemDisplayMetadata(Message, Message) changed"
assert "(Lcom/hypixel/hytale/protocol/ToClientPacket;)V" in _sig(T["PH"], "writeNoCache"), "PacketHandler.writeNoCache(ToClientPacket) changed"
assert "(Ljava/lang/String;)Ljava/util/Map;" in _sig(T["I18N"], "getMessages"), "I18nModule.getMessages(String) changed"
assert _sig(T["ITM"], "getDescriptionTranslationKey") == ["()Ljava/lang/String;"], "Item.getDescriptionTranslationKey changed"


def _cp_strings(cls):
    cp_ = pool.get(cls).getClassFile().getConstPool()
    out_ = set()
    for i_ in range(1, cp_.getSize()):
        try:
            if int(cp_.getTag(i_)) == 8:
                out_.add(str(cp_.getStringInfo(i_)))
        except Exception:
            pass
    return out_
# the key form: the lang map holds "server."-prefixed keys (getPrefix ends in "<file>." ; the engine's own keys in that map start
# "server.items."), and an item without a Description falls back to "server.items.<id>.description"
assert "\\x01\\x01." in _cp_strings(T["I18N"]) and "server.items.\\x01.bench.descriptiveLabel" in _cp_strings(T["I18N"]), "I18nModule key prefix rule changed"
assert "server.items.\\x01.description" in _cp_strings(T["ITM"]), "Item description key fallback changed"
TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")
""")
S = rep(S, """cmds = mk("ProbeCmds")
""", """cmds = mk("ProbeCmds")
tips = mk("Tips")
tsend = mk("TipSend", None, "java.lang.Runnable")
""")

TIPS_JAVA = r'''
# ---- Tips (0.9, Price-Tooltips-Spec R0): per-player runtime tooltip texts - ONE UpdateTranslations(AddOrUpdate) packet to ONE player.
# Memory only; never a lang file, never an ItemStack already in an inventory. writeNoCache is safe off the world thread (patch header).
F(tips, "public static int SENT = 0;")
F(tips, "public static int GEARS = 0;")
F(tips, "public static int LINE = 0;")
F(tips, "public static String LASTKEYS = \"\";")
F(tips, "public static String LASTTHREAD = \"\";")
M(tips, r"""
public static String stdKey(String id) { return "server.items." + id + ".description"; }""")
M(tips, r"""
public static Object item(String id) {
  try { return @ITM@.getAssetMap().getAsset(id); } catch (Throwable t) { return null; }
}""")
M(tips, r"""
public static String keyOf(String id) {
  Object o = item(id);
  if (o != null) {
    try {
      String k = ((@ITM@) o).getDescriptionTranslationKey();
      if (k != null && k.length() > 0) return k;
    } catch (Throwable t) { }
  }
  return stdKey(id);
}""")
M(tips, r"""
public static String lang(@PR@ pr) {
  String l = null;
  try { if (pr != null) l = pr.getLanguage(); } catch (Throwable t) { l = null; }
  return (l == null || l.length() == 0) ? "en-US" : l;
}""")
M(tips, r"""
public static String base(@PR@ pr, String key) {
  try {
    @I18N@ m = @I18N@.get();
    if (m == null) return null;
    java.util.Map mm = m.getMessages(lang(pr));
    Object v = mm == null ? null : mm.get(key);
    if (v != null) return (String) v;
    return m.getMessage(lang(pr), key);
  } catch (Throwable t) { return null; }
}""")
M(tips, r"""
public static String clean(String t) {
  String s = t == null ? "" : t.trim();
  if (s.length() >= 2 && s.charAt(0) == '"' && s.charAt(s.length() - 1) == '"') s = s.substring(1, s.length() - 1);
  return s.replace("\\n", "\n");
}""")
M(tips, r"""
public static String show(String s) {
  if (s == null) return "(none)";
  if (s.length() == 0) return "(empty)";
  String o = s.replace("\n", " / ");
  return o.length() > 140 ? o.substring(0, 137) + "..." : o;
}""")
M(tips, r"""
public static boolean send(@PR@ pr, java.util.Map m, String why) {
  if (pr == null || m == null || m.isEmpty()) return false;
  try {
    @PH@ ph = pr.getPacketHandler();
    if (ph == null) { @PKG@.ProbeLog.warn("TIP " + why + ": no packet handler"); return false; }
    ph.writeNoCache(new @UTR@(@UTY@.AddOrUpdate, m));
    SENT = SENT + 1;
    StringBuilder sb = new StringBuilder();
    java.util.Iterator it = m.keySet().iterator();
    while (it.hasNext()) { if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }
    LASTKEYS = sb.toString();
    LASTTHREAD = Thread.currentThread().getName();
    @PKG@.ProbeLog.info("TIP " + why + ": ONE UpdateTranslations AddOrUpdate (" + m.size() + " key(s): " + LASTKEYS + ") sent to " + pr.getUsername() + " only, on thread '" + LASTTHREAD + "' - server OK");
    return true;
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn("TIP " + why + " FAIL - the packet could not be sent: " + t);
    return false;
  }
}""")
for _f in ("public @PR@ pr;", "public java.util.Map m;", "public String why;", "public String hint;", "public boolean done;"):
    F(tsend, _f)
C(tsend, "public TipSend(@PR@ pr, java.util.Map m, String why, String hint) { this.pr = pr; this.m = m; this.why = why; this.hint = hint; }")
# the P2 send: runs ON THE PROBE'S TIMER THREAD on purpose (no world hop) - the in-game proof that writeNoCache is fine off the world thread
M(tsend, r"""
public void run() {
  this.done = true;
  try {
    if (this.pr == null || !this.pr.isValid()) { @PKG@.ProbeLog.info("TIP " + this.why + ": the player left - nothing sent"); return; }
    boolean ok = @PKG@.Tips.send(this.pr, this.m, this.why);
    @PKG@.ProbeLog.chat(this.pr, (ok ? "TIP sent now (5 s later, from the timer thread). " : "TIP FAIL - the delayed send failed. ") + this.hint);
  } catch (Throwable t) { @PKG@.ProbeLog.warn("TIP " + this.why + " FAIL: " + t); }
}""")
M(tips, r"""
public static void tip(@PR@ pr, String id0, String text, boolean later) {
  String id = id0 == null ? "" : id0.trim();
  if (id.length() == 0) { @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe tip <item id> <text>  (e.g. /uiprobe tip Wood_Oak_Trunk Test 1)"); return; }
  boolean gear = id.equalsIgnoreCase("gear");
  String t = clean(text);
  boolean reset = t.equalsIgnoreCase("reset");
  String key = gear ? "@TIPKEY@" : keyOf(id);
  boolean known = gear || item(id) != null;
  String was = gear ? null : base(pr, key);
  String v = t;
  if (reset) v = gear ? "Probe line (reset)" : (was == null ? "" : was);
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  m.put(key, v);
  if (!gear && !key.equals(stdKey(id))) {
    String v2 = v;
    if (reset) { String w2 = base(pr, stdKey(id)); v2 = w2 == null ? "" : w2; }   // reset: each key gets ITS OWN server text back
    m.put(stdKey(id), v2);
  }
  String what = gear ? "P3 probe item line" : (reset ? "reset " + id : id);
  String hint = gear ? "Skyy: look - hover the probe claws: does the last line now read '" + show(v) + "'?"
                     : "Skyy: look - hover " + id + ": is its text now '" + show(v) + "' (the server's own text was '" + show(was) + "')?";
  if (!known) hint = hint + " NOTE: no item '" + id + "' is loaded on this server - check the id (case matters).";
  if (later) {
    @PKG@.ProbeTimer.after(new @PKG@.TipSend(pr, m, "P2 " + what + " (later)", hint), @TIPMS@L);
    @PKG@.ProbeLog.tell(pr, "TIP P2: in 5 s you get the new text for " + key + " = '" + show(v) + "'. Open your inventory NOW and keep hovering " + (gear ? "the probe claws" : id) + " - does it change while the inventory stays open?");
    return;
  }
  boolean ok = send(pr, m, what);
  @PKG@.ProbeLog.chat(pr, (ok ? "TIP sent: " : "TIP FAIL - not sent: ") + key + (m.size() > 1 ? " (+ " + stdKey(id) + ")" : "") + " = '" + show(v) + "', to you only (one packet). " + hint);
}""")
M(tips, r"""
public static int count(@IC@ ic, String id) {
  int n = 0;
  if (ic == null) return 0;
  int cap = ic.getCapacity();
  for (int i = 0; i < cap; i++) {
    @IS@ s = ic.getItemStack((short) i);
    if (s != null && !s.isEmpty() && id.equals(s.getItemId())) n = n + s.getQuantity();
  }
  return n;
}""")
M(tips, r"""
public static boolean added(@ISTX@ tx) {
  if (tx == null || !tx.succeeded()) return false;
  @IS@ r = tx.getRemainder();
  return r == null || r.isEmpty();
}""")
M(tips, r"""
public static @IS@ probeStack() {
  @MSG@ name = @MSG@.raw("Probe Claws (price tooltip test P3)").color("@CGOLD@");
  @MSG@ desc = @MSG@.join(new @MSG@[] {
    @MSG@.raw("PROBE item (SkyyUiProbe) - not a real item.\nThe next line comes from a translation key:\n").color("@CDIM@"),
    @MSG@.translation("@TIPKEY@") });
  return new @IS@("@TIPIT@", 1).withMetadata(@IDM@.KEYED_CODEC, new @IDM@(name, desc));
}""")
M(tips, r"""
public static void gear(@REF@ ref, @ST@ store, @PR@ pr) {
  @PLA@ p = null;
  try { p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { @PKG@.ProbeLog.tell(pr, "TIP P3 FAIL - no player component"); return; }
  @INV@ inv = p.getInventory();
  if (inv == null) { @PKG@.ProbeLog.tell(pr, "TIP P3 FAIL - no inventory"); return; }
  int before = count(inv.getStorage(), "@TIPIT@") + count(inv.getHotbar(), "@TIPIT@");
  boolean ok = false;
  try {
    ok = added(inv.getStorage().addItemStack(probeStack()));
    if (!ok) ok = added(inv.getHotbar().addItemStack(probeStack()));
  } catch (Throwable t) { @PKG@.ProbeLog.warn("TIP P3: adding the probe item failed: " + t); ok = false; }
  int after = count(inv.getStorage(), "@TIPIT@") + count(inv.getHotbar(), "@TIPIT@");
  if (!ok || after - before != 1) {
    @PKG@.ProbeLog.tell(pr, "TIP P3 FAIL - the probe item could not be given (inventory full? counted " + before + " -> " + after + "). Make room and run /uiprobe tipgear again.");
    return;
  }
  GEARS = GEARS + 1;
  LINE = LINE + 1;
  String v = "NPC Sell: <color is=\"@CGOLD@\"><b>320</b></color> each <color is=\"@CDIM@\">(probe line #" + LINE + ", " + new java.text.SimpleDateFormat("HH:mm:ss").format(new java.util.Date()) + ")</color>";
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  m.put("@TIPKEY@", v);
  boolean sent = send(pr, m, "P3 probe item line #" + LINE);
  @PKG@.ProbeLog.info("TIP P3: probe item @TIPIT@ given to " + pr.getUsername() + " (counted " + before + " -> " + after + ", storage first) - server OK");
  @PKG@.ProbeLog.chat(pr, "TIP P3: you got 'Probe Claws' (in your inventory). " + (sent ? "" : "FAIL - the key text was not sent. ") + "Skyy: look - hover them: under the grey lines, is there 'NPC Sell: 320 each (probe line #" + LINE + ", time)' with 320 in gold, or a raw key / nothing? Then /uiprobe tip gear Test 3 - does that line change?");
}""")
'''
S = rep(S, """# ---- ProbeCmds: help, tour, next, open a case (the last case seen per player is kept in memory only)
""", TIPS_JAVA + """# ---- ProbeCmds: help, tour, next, open a case (the last case seen per player is kept in memory only)
""")
# help: the tip probe lines
S = rep(S, """  @PKG@.ProbeLog.chat(pr, "Each result prints PASS, FAIL or 'Skyy: look' here and in the server log. Start with /skyprobe tour.");
""", """  @PKG@.ProbeLog.chat(pr, "Each result prints PASS, FAIL or 'Skyy: look' here and in the server log. Start with /skyprobe tour.");
  @PKG@.ProbeLog.chat(pr, "PRICE TOOLTIP PROBE (P1-P5): /uiprobe tip <item id> <text> = a new tooltip text for that item, for you only (\\\\n = new line, reset = the normal text back); /uiprobe tiplater <item id> <text> = the same 5 s later (open your inventory while you wait); /uiprobe tipgear = probe claws with a line from a translation key; /uiprobe tip gear <text> = change that line.");
""")
S = rep(S, """  if (t.equals("tour")) { tour(ref, store, pr); return; }
""", """  if (t.equals("tour")) { tour(ref, store, pr); return; }
  if (t.equals("tipgear")) { @PKG@.Tips.gear(ref, store, pr); return; }
  if (t.equals("tip") || t.equals("tiplater")) { @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe " + t + " <item id> <text>  (e.g. /uiprobe " + t + " Wood_Oak_Trunk Test 1; /uiprobe tip gear <text> for the probe claws)"); return; }
""")
S = rep(S, '''EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
''', '''M(cmds, r"""
public static void tip3(@PR@ pr, String what, String id, String text) {
  String w = what == null ? "" : what.trim().toLowerCase();
  if (w.equals("tip")) { @PKG@.Tips.tip(pr, id, text, false); return; }
  if (w.equals("tiplater")) { @PKG@.Tips.tip(pr, id, text, true); return; }
  @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe tip <item id> <text>, /uiprobe tiplater <item id> <text> (or /uiprobe help)");
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
''')
S = rep(S, '''  this.caseArg = withRequiredArg("what", "tour, next, help, or a case: m4,''', '''  this.caseArg = withRequiredArg("what", "tour, next, help, tipgear, or a case: m4,''')
S = rep(S, '''cmd = mk("SkyProbeCmd", T["APC"])
''', '''cmdT = mk("SkyProbeTipCmd", T["APC"])
# a SUB-command (not a usage variant): the engine picks usage variants by the EXACT token count (AbstractCommand.variantCommands is an
# Int2ObjectMap looked up with the token count), so a multi-word text could never reach a 3-argument variant; a sub-command is found by
# its first word, then GREEDY_STRING takes the rest. Two instances: "tip" and "tiplater" (getName() says which).
F(cmdT, "public @RA@ idArg;")
F(cmdT, "public @RA@ textArg;")
C(cmdT, r"""
public SkyProbeTipCmd(String name) {
  super(name, "(admin) /uiprobe " + name + " <item id> <text> - the price-tooltip probe: a new tooltip text for you only" + (name.equals("tiplater") ? ", 5 s later" : ""));
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.idArg = withRequiredArg("item", "an item id (Wood_Oak_Trunk), or gear for the probe claws' line", @ATY@.STRING);
  this.textArg = withRequiredArg("text", "the tooltip text (\\\\n = new line; reset = the normal text)", @ATY@.GREEDY_STRING);
}""")
M(cmdT, EXEC + r""" {
  try { @PKG@.ProbeCmds.tip3(pr, getName(), String.valueOf(ctx.get(this.idArg)), String.valueOf(ctx.get(this.textArg))); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/uiprobe " + getName() + " failed: " + t); @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe " + getName() + " <item id> <text>"); }
}""")
cmd = mk("SkyProbeCmd", T["APC"])
''')
S = rep(S, '''  super("skyprobe", "(admin) PROBE: the UI queue test pages (15 cases) - /skyprobe tour walks through them, /skyprobe help lists them");''',
        '''  super("skyprobe", "(admin) PROBE: the UI queue test pages (15 cases) + the price-tooltip probe (tip / tiplater / tipgear) - /skyprobe help lists them");''')
S = rep(S, '''  addUsageVariant(new @PKG@.SkyProbeArgCmd());
''', '''  addUsageVariant(new @PKG@.SkyProbeArgCmd());
  addSubCommand(new @PKG@.SkyProbeTipCmd("tip"));
  addSubCommand(new @PKG@.SkyProbeTipCmd("tiplater"));
''')
S = rep(S, '''walks through the @NCASE@ UI queue cases; no data, no HUD, nothing for players");''',
        '''walks through the @NCASE@ UI queue cases + /uiprobe tip / tiplater / tipgear (price-tooltip probe P1-P5); no data, no HUD, nothing for players");''')
S = rep(S, "CLASSES = [log, data, thr, tim, rta, rtp, hres, heads, later, page_c, cmds, cmdA, cmd, pl]",
        "CLASSES = [log, data, thr, tim, rta, rtp, hres, heads, later, page_c, cmds, tips, tsend, cmdA, cmdT, cmd, pl]")
S = rep(S, "ground trail G1) for one test session - no data,",
        "ground trail G1) + the price-tooltip probe (/uiprobe tip, tiplater, tipgear: P1-P5) for one test session - no data,")
save("build_skyyuiprobe_0.9.py", S)

# ===================================================================================================== the harness
H = load("test_skyyuiprobe_0.8.py")
H = rep(H, '"""Harness for SkyyUiProbe 0.8 (the UI queue probe, 15 cases; SkyyUiProbe/build_skyyuiprobe_0.8.py).\nBuild first: python SkyyUiProbe/build_skyyuiprobe_0.8.py',
        '"""Harness for SkyyUiProbe 0.9 (the UI queue probe, 15 cases + the price-tooltip probe R0; SkyyUiProbe/build_skyyuiprobe_0.9.py,\nmade by tools/uiprobe_0_9_patch.py). Build first: python SkyyUiProbe/build_skyyuiprobe_0.9.py')
H = rep(H, "    python SkyyUiProbe/test_skyyuiprobe_0.8.py [--keep]", "    python SkyyUiProbe/test_skyyuiprobe_0.9.py [--keep] [--old-jar <the 0.8 jar>]")
H = rep(H, """       CMDS    the command classes construct""", """       TIP     (0.9) the price-tooltip probe with an I18nModule stand-in (the real server.lang of Assets.zip under the engine's "server."
               prefix) + an Item asset-map stand-in: tip = ONE UpdateTranslations AddOrUpdate to the caller with the item's description
               key, quotes / \\\\n cleaned, reset = the server's own text, a Description-less item and an item whose own key differs
               (both keys in the one packet), an unknown id; tiplater = nothing now, ONE packet when the timer task runs (not on the
               world queue); tipgear = ONE probe stack (claws, ItemDisplayMetadata with the translation child) counted 0 -> 1, the key
               packet; a full inventory = FAIL line, nothing sent; tip gear = only the key; the engine's own parser routes
               /skyprobe tip ... (3+ words, GREEDY text) and /skyprobe tipgear; 2 words / an extra word = refused
       CMDS    the command classes construct""")
H = rep(H, "Scratch: tools/dev/scratch/uiprobe08/harness (deleted unless --keep).", "Scratch: tools/dev/scratch/tip0/harness (deleted unless --keep). C = class compare vs the 0.8 jar.")
H = rep(H, 'VERSION = "0.8"\n', 'VERSION = "0.9"\n')
H = rep(H, '''JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
''', '''JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old-jar", os.path.join(HERE, "SkyyUiProbe-0.8.jar")))
''')
H = rep(H, '"tools", "dev", "scratch", "uiprobe08", "harness"', '"tools", "dev", "scratch", "tip0", "harness"')
H = rep(H, '''CLASSES = ["ProbeLog", "ProbeData", "ProbeThreads", "ProbeTimer", "RtAsset", "RtPic", "HeadResult", "Heads", "Later", "MapPage", "ProbeCmds",
           "SkyProbeArgCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]''', '''CLASSES = ["ProbeLog", "ProbeData", "ProbeThreads", "ProbeTimer", "RtAsset", "RtPic", "HeadResult", "Heads", "Later", "MapPage", "ProbeCmds",
           "Tips", "TipSend", "SkyProbeArgCmd", "SkyProbeTipCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]
# class compare vs 0.8: only these classes / members may differ (everything else byte-identical)
CMP_EXPECT = {"ProbeCmds": ["+m tip3", "~m arg", "~m help"], "SkyProbeArgCmd": ["~c "], "SkyProbeCmd": ["~c "],
              "SkyyUiProbePlugin": ["~m setup"]}
CMP_ADDED = ["Tips", "TipSend", "SkyProbeTipCmd"]''')

TIP_TEST = r'''
    # ---- TIP (0.9): the price-tooltip probe R0 (Price-Tooltips-Spec section 5), every path executed
    TIPS = JV("Tips")
    JMap, JLong = JClass("java.util.HashMap"), JClass("java.util.concurrent.atomic.AtomicLong")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    I18c = JClass(PH + "server.core.modules.i18n.I18nModule")
    i18 = Ucls.allocateInstance(I18c.class_)
    langs, en = CHM(), CHM()
    lang_txt = AZ.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for ln in lang_txt.splitlines():
        if "=" in ln and ln.startswith("items.") and ".description" in ln.split("=", 1)[0]:
            k_, v_ = ln.split("=", 1)
            en.put("server." + k_.strip(), v_.strip())          # the engine's prefix rule (getPrefix: "<file>." = "server.")
    en.put("server.items.Probe_Own_Key_Thing.desc", "Own key text")
    langs.put("en-US", en)
    for fname, val in (("languages", langs), ("cachedLanguages", CHM()), ("messagesVersion", JLong(1)), ("fallbacks", JMap()),
                       ("bundledDefaults", JMap()), ("pendingLanguages", CHM())):
        E.jf(I18c.class_, fname).set(i18, val)
    E.jf(I18c.class_, "instance").set(None, i18)
    oak_base = str(en.get("server.items.Wood_Oak_Trunk.description"))
    K.check(oak_base.startswith("Refines into Hardwood"), "TIP STAND-IN: I18nModule holds the real Oak Log text under server.items.Wood_Oak_Trunk.description")
    K.eq(str(TIPS.base(P.pr, "server.items.Wood_Oak_Trunk.description")), oak_base, "TIP: base() reads the server's own text through I18nModule.getMessages(lang)")
    K.check(TIPS.base(P.pr, "server.items.No_Such_Item.description") is None, "TIP: base() of a key the server lacks = none")
    # Item asset-map stand-in: Oak (own Description key = the standard one), a Description-less item, an item whose JSON key differs
    ITc = JClass(PH + "server.core.asset.type.item.config.Item")
    ITPc = JClass(PH + "server.core.asset.type.item.config.ItemTranslationProperties")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    item_ok = False
    try:
        dam = DAMc()
        AScls = JClass("com.hypixel.hytale.assetstore.AssetStore")
        ast = Ucls.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore").class_)
        E.jf(AScls.class_, "assetMap").set(ast, dam)
        amap = E.jf(DAMc.class_, "assetMap").get(dam)

        def fake_item(iid, desc_key, ms):
            it_ = Ucls.allocateInstance(ITc.class_)
            E.jf(ITc.class_, "id").set(it_, iid)
            tp_ = Ucls.allocateInstance(ITPc.class_)
            if desc_key:
                E.jf(ITPc.class_, "description").set(tp_, desc_key)
            E.jf(ITc.class_, "translationProperties").set(it_, tp_)
            E.jf(ITc.class_, "maxStack").setInt(it_, ms)
            amap.put(iid, it_)
        fake_item("Wood_Oak_Trunk", "server.items.Wood_Oak_Trunk.description", 100)
        fake_item("Plant_Crop_Wheat_Item", None, 100)
        fake_item("Probe_Own_Key_Thing", "server.items.Probe_Own_Key_Thing.desc", 1)
        E.jf(ITc.class_, "ASSET_STORE").set(None, ast)
        item_ok = TIPS.item("Wood_Oak_Trunk") is not None
    except Exception as ex:
        K.notes.append("TIP: the Item asset-map stand-in failed (%s)" % str(ex)[:200])
    K.check(item_ok, "TIP STAND-IN: an Item asset map (Oak, Wheat, an item with its own description key)")
    K.eq(str(TIPS.keyOf("Wood_Oak_Trunk")), "server.items.Wood_Oak_Trunk.description", "TIP: keyOf(Oak) = its JSON Description key")
    K.eq(str(TIPS.keyOf("Plant_Crop_Wheat_Item")), "server.items.Plant_Crop_Wheat_Item.description", "TIP: keyOf(Wheat, no Description) = the engine fallback")
    K.eq(str(TIPS.keyOf("Probe_Own_Key_Thing")), "server.items.Probe_Own_Key_Thing.desc", "TIP: keyOf = the item's own key when it differs")
    K.eq(str(TIPS.keyOf("No_Such_Item")), "server.items.No_Such_Item.description", "TIP: keyOf(unknown) = the standard key")
    K.eq(str(TIPS.clean('  "Test 1"  ')), "Test 1", "TIP: clean drops the surrounding quotes (GREEDY_STRING keeps them)")
    K.eq(str(TIPS.clean("Line A\\nLine B")), "Line A\nLine B", "TIP: clean turns \\n into a new line")
    K.eq(str(TIPS.show("a\nb")), "a / b", "TIP: show() for chat")

    def utr(f0, PP=None):
        return [p for p in E.sent(PP or P)[f0:] if str(p.getClass().getSimpleName()) == "UpdateTranslations"]

    def utmap(p):
        m_ = p.translations
        return dict((str(k), str(m_.get(k))) for k in m_.keySet())
    E.run_world(E.W1)
    if REC.tasks is not None:
        REC.tasks.clear()
        REC.delays.clear()
    # P1: tip = one AddOrUpdate, caller only, the description key
    f0, s0 = len(E.sent(P)), int(TIPS.SENT)
    CMDS.tip3(P.pr, "tip", "Wood_Oak_Trunk", '"Test 1"')
    u = utr(f0)
    K.eq(len(u), 1, "TIP P1: exactly ONE UpdateTranslations packet")
    if u:
        K.eq(str(u[0].type), "AddOrUpdate", "TIP P1: UpdateType AddOrUpdate")
        K.eq(utmap(u[0]), {"server.items.Wood_Oak_Trunk.description": "Test 1"}, "TIP P1: the one key = 'Test 1' (quotes dropped)")
    K.eq(kinds(f0), ["UpdateTranslations"], "TIP P1: no other packet (chat aside)")
    K.check("TIP sent: server.items.Wood_Oak_Trunk.description = 'Test 1'" in chats(f0) and oak_base[:20] in chats(f0),
            "TIP P1: the chat line names the key, the new text and the server's own text")
    K.eq(int(TIPS.SENT) - s0, 1, "TIP P1: SENT counts it")
    # multi-line + reset
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "TIP", "Wood_Oak_Trunk", "Market\\nNPC Sell: 320 each")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Wood_Oak_Trunk.description": "Market\nNPC Sell: 320 each"}, "TIP: \\n = a real new line in the sent text")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Wood_Oak_Trunk", "reset")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Wood_Oak_Trunk.description": oak_base}, "TIP: reset sends the server's own text back")
    # P5: a Description-less item; an item whose own key differs = both keys in ONE packet; an unknown id = sent + a note
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Plant_Crop_Wheat_Item", "Wheat test")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Plant_Crop_Wheat_Item.description": "Wheat test"}, "TIP P5: Wheat (no Description) = the fallback key")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Probe_Own_Key_Thing", "X")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Probe_Own_Key_Thing.desc": "X", "server.items.Probe_Own_Key_Thing.description": "X"},
            "TIP: an item whose key differs = its key + the standard key in the ONE packet")
    K.check("(+ server.items.Probe_Own_Key_Thing.description)" in chats(f0), "TIP: the chat names both keys")
    # fix (critic note 2): reset of an item whose own key differs = each key gets ITS OWN server text (not the own-key text twice)
    en.put("server.items.Probe_Own_Key_Thing.description", "Std key text")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Probe_Own_Key_Thing", "reset")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Probe_Own_Key_Thing.desc": "Own key text", "server.items.Probe_Own_Key_Thing.description": "Std key text"},
            "TIP FIX: reset with two keys = each key its own server text, in ONE packet")
    en.remove("server.items.Probe_Own_Key_Thing.description")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Probe_Own_Key_Thing", "reset")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Probe_Own_Key_Thing.desc": "Own key text", "server.items.Probe_Own_Key_Thing.description": ""},
            "TIP FIX: reset with no server text for the standard key = '' there (never the own-key text)")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "No_Such_Item", "Y")
    K.check(len(utr(f0)) == 1 and "no item 'No_Such_Item' is loaded" in chats(f0), "TIP: an unknown id is still sent, with a check-the-id note")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "nope", "Wood_Oak_Trunk", "Z")
    K.check(len(utr(f0)) == 0 and "Usage: /uiprobe tip" in chats(f0), "TIP: an unknown word = usage, nothing sent")
    for w in ("tip", "tiplater"):
        f0 = len(E.sent(P))
        CMDS.arg(P.ref, P.st, P.pr, w)
        K.check(len(utr(f0)) == 0 and ("Usage: /uiprobe " + w) in chats(f0) and P.pm.getCustomPage() is None, "TIP: /uiprobe %s alone = usage" % w)
    # P2: tiplater = nothing now; ONE packet when the timer task runs - from the timer task itself, not via the world queue
    f0 = len(E.sent(P))
    n_tasks = 0 if REC.tasks is None else int(REC.tasks.size())
    CMDS.tip3(P.pr, "tiplater", "Wood_Oak_Trunk", "Test 2")
    K.eq(len(utr(f0)), 0, "TIP P2: tiplater sends nothing at once")
    K.check("Open your inventory NOW" in chats(f0), "TIP P2: the chat says to open the inventory")
    K.eq(int(REC.tasks.size()) - n_tasks, 1, "TIP P2: one timer task")
    K.eq(int(REC.delays.get(REC.delays.size() - 1)), 5000, "TIP P2: 5000 ms")
    t_ = REC.tasks.get(REC.tasks.size() - 1)
    REC.tasks.clear()
    REC.delays.clear()
    f1 = len(E.sent(P))
    t_.run()
    u = utr(f1)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Wood_Oak_Trunk.description": "Test 2"}, "TIP P2: the timer task sends ONE packet (Test 2) without the world queue")
    K.check("TIP sent now (5 s later, from the timer thread)" in chats(f1), "TIP P2: the chat line after the delayed send")
    # P3: tipgear = ONE probe stack (claws + ItemDisplayMetadata with the translation child), counted, then the key packet
    IDMc = JClass(PH + "server.core.asset.type.item.config.metadata.ItemDisplayMetadata")

    def storage_list(PP):
        ic_ = PP.slots["storage"].getInventory()
        out_ = []
        for i in range(int(ic_.getCapacity())):
            s_ = ic_.getItemStack(JShort(i))
            if s_ is not None and not s_.isEmpty():
                out_.append(str(s_.getItemId()) + "x" + str(s_.getQuantity()))
        return out_
    st0 = storage_list(P)
    K.eq(E.count(P, "Weapon_Claws_Tribal"), 0, "TIP P3: no claws before")
    f0 = len(E.sent(P))
    CMDS.arg(P.ref, P.st, P.pr, "TipGear")
    K.eq(E.count(P, "Weapon_Claws_Tribal"), 1, "TIP P3: ONE probe item given")
    found = None
    sic_ = P.slots["storage"].getInventory()
    for i in range(int(sic_.getCapacity())):
        s_ = sic_.getItemStack(JShort(i))
        if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == "Weapon_Claws_Tribal":
            found = s_
    K.check(found is not None, "TIP P3: the probe item went into STORAGE first")
    if found is not None:
        idm = found.getFromMetadataOrNull(IDMc.KEYED_CODEC)
        K.check(idm is not None, "TIP P3: the stack carries ItemDisplayMetadata")
        if idm is not None:
            K.check("Probe Claws" in str(idm.getName().getRawText()), "TIP P3: the display name")
            ch = [c_ for c_ in idm.getDescription().getChildren()]
            K.check(any(c_.getMessageId() is not None and str(c_.getMessageId()) == "server.skyy.probe.tip" for c_ in ch),
                    "TIP P3: the description has the translation child server.skyy.probe.tip")
            K.check(any(c_.getRawText() is not None and "PROBE item" in str(c_.getRawText()) for c_ in ch), "TIP P3: + the grey explanation lines")
    u = utr(f0)
    K.eq(len(u), 1, "TIP P3: ONE key packet after the item")
    if u:
        mm_ = utmap(u[0])
        K.check(list(mm_) == ["server.skyy.probe.tip"] and 'NPC Sell: <color is="#e8c25a"><b>320</b></color> each' in mm_["server.skyy.probe.tip"]
                and "probe line #1" in mm_["server.skyy.probe.tip"], "TIP P3: the key text (gold 320 + line #1): %s" % mm_)
    K.check("you got 'Probe Claws'" in chats(f0), "TIP P3: the chat line")
    K.eq(sorted(storage_list(P)), sorted(st0 + ["Weapon_Claws_Tribalx1"]), "TIP P3: nothing else in storage changed")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "gear", "Test 3")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.skyy.probe.tip": "Test 3"}, "TIP P3: tip gear Test 3 = only the probe key")
    K.eq(E.count(P, "Weapon_Claws_Tribal"), 1, "TIP P3: tip gear gives no item")
    # P3 with a full inventory: FAIL line, no packet, nothing lost
    PF = E.player(uid=JClass("java.util.UUID")(9, 9), name="SkyyFull")
    ISc = JClass(PH + "server.core.inventory.ItemStack")
    for fld in ("storage", "hotbar"):
        ic_ = PF.slots[fld].getInventory()
        for i in range(int(ic_.getCapacity())):
            ic_.setItemStackForSlot(JShort(i), ISc("Wood_Oak_Trunk", 100))
    n_oak = E.count(PF, "Wood_Oak_Trunk")
    f0 = len(E.sent(PF))
    CMDS.arg(PF.ref, PF.st, PF.pr, "tipgear")
    K.check(len(utr(f0, PF)) == 0 and "TIP P3 FAIL - the probe item could not be given" in E.strs_of(PF, f0), "TIP P3: a full inventory = a FAIL line, no packet")
    K.check(E.count(PF, "Weapon_Claws_Tribal") == 0 and E.count(PF, "Wood_Oak_Trunk") == n_oak, "TIP P3: a full inventory loses nothing, gains nothing (%d oak)" % n_oak)
    # help names the tip probe
    f0 = len(E.sent(P))
    CMDS.arg(P.ref, P.st, P.pr, "help")
    K.check("PRICE TOOLTIP PROBE (P1-P5)" in chats(f0) and "/uiprobe tipgear" in chats(f0), "TIP: help lists the tip probe")
    K.notes.append("TIP: %d UpdateTranslations sent; last keys %s on thread %s" % (int(TIPS.SENT), str(TIPS.LASTKEYS), str(TIPS.LASTTHREAD)))
    # the engine's own parser: /skyprobe tip ... (3+ words) reaches the 3-arg variant; tipgear / tour the 1-arg one; 2 words = refused
    Tok = JClass("com.hypixel.hytale.server.core.command.system.Tokenizer")
    PCx = JClass("com.hypixel.hytale.server.core.command.system.ParserContext")
    PRs = JClass("com.hypixel.hytale.server.core.command.system.ParseResult")
    MSGS = []

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
    class Snd(object):
        @JOverride
        def getUsername(self):
            return "Tester"

        @JOverride
        def getUuid(self):
            return JClass("java.util.UUID")(1, 2)

        @JOverride
        def sendMessage(self, m):
            MSGS.append(str(m.getMessageId() or m.getRawText()))

        @JOverride
        def hasPermission(self, q, *rest):
            return True

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    snd, own = Snd(), Owner()
    rootc = JV("SkyProbeCmd")()
    rootc.setOwner(own)
    try:
        rootc.completeRegistration()
    except Exception as ex:
        K.notes.append("completeRegistration: %s" % str(ex)[:100])

    def parse(line):
        del MSGS[:]
        res = PRs()
        toks = Tok.parseArguments(line, res)
        if res.failed():
            return False, ["tokenizer"]
        ctx = PCx.of(toks, line, res)
        try:
            rootc.acceptCall(snd, ctx, res)
        except Exception as e:
            MSGS.append("EXC " + str(e)[:200])
        if res.failed():
            res.sendMessages(snd)
            return False, list(MSGS)
        return True, list(MSGS)
    for line in ("skyprobe tip Wood_Oak_Trunk Test 1", 'skyprobe tip Wood_Oak_Trunk "Test 1"', "skyprobe tiplater Wood_Oak_Trunk Test 2",
                 "skyprobe tip gear Test 3", "skyprobe tipgear", "skyprobe tour", "skyprobe"):
        ok, ms = parse(line)
        K.check(ok and "server.commands.errors.playerOrArg" in ms, "TIP PARSER: /%s parses and reaches a player command (%s)" % (line, ms[:2]))
    for line in ("skyprobe tip Wood_Oak_Trunk", "skyprobe tip", "skyprobe tiplater Wood_Oak_Trunk", "skyprobe tour extra"):
        ok, ms = parse(line)
        K.check(not ok, "TIP PARSER CONTROL: /%s is refused (%s)" % (line, ms[:1]))
'''
H = rep(H, """    # ---- commands
    for cn in ("SkyProbeCmd", "SkyProbeArgCmd"):""", TIP_TEST.lstrip("\n") + """    # ---- commands
    for cn in ("SkyProbeCmd", "SkyProbeArgCmd"):""")
H = rep(H, """    pgs = root.getPermissionGroups() if hasattr(root, "getPermissionGroups") else None
    K.check(pgs is None or len(list(pgs)) == 0, "CMDS: no permission groups")
""", """    pgs = root.getPermissionGroups() if hasattr(root, "getPermissionGroups") else None
    K.check(pgs is None or len(list(pgs)) == 0, "CMDS: no permission groups")
    subs = dict((str(k), v) for k, v in dict(root.getSubCommands()).items())
    K.eq(sorted(subs), ["tip", "tiplater"], "CMDS: the sub-commands tip + tiplater")
    for nm_, tc_ in sorted(subs.items()):
        K.check(str(tc_.getClass().getSimpleName()) == "SkyProbeTipCmd" and str(tc_.getName()) == nm_, "CMDS: /skyprobe %s = SkyProbeTipCmd" % nm_)
        K.check(str(tc_.getPermission()) == "skyyuiprobe.admin", "CMDS: /skyprobe %s requires skyyuiprobe.admin" % nm_)
        pg2 = tc_.getPermissionGroups() if hasattr(tc_, "getPermissionGroups") else None
        K.check(pg2 is None or len(list(pg2)) == 0, "CMDS: /skyprobe %s has no permission groups" % nm_)
""")
H = rep(H, """    import jpype
    from jpype import JClass, JArray, JByte, JString
""", """    import jpype
    from jpype import JClass, JArray, JByte, JString, JShort, JImplements, JOverride
""")
# the class compare phase (vs the 0.8 jar)
H = rep(H, """    elif ph == "jar":
        run_jar(HK.arg("--out"))
""", """    elif ph == "jar":
        run_jar(HK.arg("--out"))
    elif ph == "compare":
        run_cmp(HK.arg("--out"))
""")
H = rep(H, """    for label in ("jar", "mkfake", "verify", "exec", "audit"):""", """    assert os.path.isfile(OLD_JAR), "the 0.8 jar for the class compare: " + OLD_JAR
    for label in ("jar", "compare", "mkfake", "verify", "exec", "audit"):""")
H = rep(H, '''"--dir", SCRATCH, "--jar", JAR], env=env)''', '''"--dir", SCRATCH, "--jar", JAR, "--old-jar", OLD_JAR], env=env)''')
# the jar check: no Java source writes metadata except the ONE fresh probe stack
H = rep(H, """    K.eq(sorted(n[:-6].split("/")[-1] for n in names if n.endswith(".class")), sorted(CLASSES), "J: classes")
""", """    K.eq(sorted(n[:-6].split("/")[-1] for n in names if n.endswith(".class")), sorted(CLASSES), "J: classes")
    _src = open(os.path.join(HERE, "build_skyyuiprobe_%s.py" % VERSION), encoding="utf-8").read()
    K.eq(len(re.findall(r"\\.withMetadata\\(", _src)), 1, "J: ONE withMetadata in the build (the fresh probe stack only)")
    K.check(re.search(r'return new @IS@\\("@TIPIT@", 1\\)\\.withMetadata\\(', _src) is not None, "J: ... and it is on a NEW ItemStack")
    K.check(".setMetadata(" not in _src and "replaceItemStackInSlot" not in _src and "setItemStackForSlot" not in _src, "J: no setMetadata / slot writes")
""")
H = rep(H, """def run_jar(out):
""", """def run_cmp(out):
    \"\"\"C: HK.run_compare (byte code of every class vs the 0.8 jar) - its non-class rule allows manifest.json only; the 14 case pages
    differ by exactly ONE line each (the title 'SkyyUiProbe 0.8 - ...' -> '0.9 - ...', the VERSION in the text). Checked here, line by line,
    then that one expected FAIL is cleared.\"\"\"
    HK.run_compare(out, JAR, OLD_JAR, PKG, CMP_EXPECT, CMP_ADDED)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    na = [n for n in za.namelist() if not n.endswith(".class")]
    nb = [n for n in zb.namelist() if not n.endswith(".class")]
    ch = sorted(n for n in set(na) | set(nb) if n not in na or n not in nb or za.read(n) != zb.read(n))
    pages = [n for n in ch if n != "manifest.json"]
    good = "manifest.json" in ch and len(pages) == 14 and all(n.startswith("com/skyy/uiprobe/pages/") and n in na and n in nb for n in pages)
    for n in pages if good else []:
        a_, b_ = za.read(n).decode("utf-8").split("\\n"), zb.read(n).decode("utf-8").split("\\n")
        dl = [(x, y) for x, y in zip(a_, b_) if x != y]
        good = good and len(a_) == len(b_) and dl == [("S\\t#SkyyPrTitle.Text\\tSkyyUiProbe 0.8 - UI queue probe", "S\\t#SkyyPrTitle.Text\\tSkyyUiProbe 0.9 - UI queue probe")]
    fl = [f for f in d["fails"] if f.startswith("C: non-class entries changed")]
    if good and len(fl) == 1:
        d["fails"].remove(fl[0])
        d["ok"] += 1
        d["notes"].append("C: non-class entries: manifest.json + the 14 case pages, each ONLY its title line 0.8 -> 0.9 (checked line by line)")
    else:
        d["fails"].append("C: the page data differ by more than the title line: %s" % pages[:4])
    json.dump(d, open(out, "w"), indent=1)


def run_jar(out):
""")
# the 400-line log tail is full by the LATER check now (0.9's help prints one more line per call), so len(tail()) no longer marks
# "new" lines there: empty the tail first (memory only) - the check itself is unchanged
H = rep(H, """    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(P.pr, None)
    n0 = len(tail())
    drain()
""", """    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(P.pr, None)
    LOG.TAIL.clear()
    n0 = 0
    drain()
""")
# LIVE (start twice on a scratch COPY of the live world): setup() twice on fresh plugin objects, a capturing command registry
H = rep(H, """def run_jar(out):
""", """WORLD = "NewBetaTest"          # tools/deploy_set.py WORLD (read only; copied into scratch)


def run_live(out):
    \"\"\"LIVE: the live world's config.json (+ any Skyy_SkyyUiProbe* data folder - none exist: the probe keeps nothing) COPIED into scratch;
    setup() twice on fresh plugin objects (PluginBase fields: logger, dataDirectory inside the copy, a capturing CommandRegistry);
    each start = the '[SkyyUiProbe] 0.9 ready' line + ONE /skyprobe root (alias uiprobe, the 1-word variant, the tip / tiplater
    sub-commands); shutdown() between; the copy is byte + time identical after both starts and no data folder appears.\"\"\"
    import time
    from jpype import JClass
    K = HK.Child(out)
    live = os.path.join(B.USERDATA, "Saves", WORLD)
    home = os.path.join(SCRATCH, "live", WORLD)
    os.makedirs(os.path.join(home, "mods"))
    shutil.copy2(os.path.join(live, "config.json"), os.path.join(home, "config.json"))
    md = os.path.join(live, "mods")
    ours = sorted(d for d in os.listdir(md) if d.startswith("Skyy_SkyyUiProbe")) if os.path.isdir(md) else []
    for d in ours:
        shutil.copytree(os.path.join(md, d), os.path.join(home, "mods", d))
    K.check(os.path.isfile(os.path.join(home, "config.json")), "LIVE: %s config.json copied into scratch (read-only source); probe data folders in the live world: %s" % (WORLD, ours or "none"))
    hcls = os.path.join(SCRATCH, "hcls_live")
    os.makedirs(hcls, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, JAR], verify=True)
    CPj = JClass("javassist.ClassPool").getDefault()
    CPj.appendClassPath(B.SERVER_JAR)
    rc = CPj.makeClass("uiprobeharness.CaptureCmds", CPj.get("com.hypixel.hytale.server.core.command.system.CommandRegistry"))
    rc.addField(JClass("javassist.CtField").make("public static java.util.List CAP = new java.util.ArrayList();", rc))
    rc.addConstructor(JClass("javassist.CtNewConstructor").make("public CaptureCmds() { super((java.util.List) null, (java.util.function.BooleanSupplier) null, "
                                                                 "(String) null, (com.hypixel.hytale.server.core.plugin.PluginBase) null); }", rc))
    rc.addMethod(JClass("javassist.CtNewMethod").make("public com.hypixel.hytale.server.core.command.system.CommandRegistration registerCommand("
                                                       "com.hypixel.hytale.server.core.command.system.AbstractCommand c) { CAP.add(c); return null; }", rc))
    rc.writeFile(hcls)
    CAPC = JClass("uiprobeharness.CaptureCmds")
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    PBc = JClass("com.hypixel.hytale.server.core.plugin.PluginBase")
    PL = JClass(PKG + "SkyyUiProbePlugin")

    def setf(o, name, v):
        f_ = PBc.class_.getDeclaredField(name)
        f_.setAccessible(True)
        f_.set(o, v)
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend").subscribe(CAPLOG)

    def records():
        out_ = []
        for r in list(CAPLOG):
            try:
                out_.append(str(r.getMessage()))
            except Exception:
                pass
        return out_

    def snap():
        d_ = {}
        for dp, _dn, fns in os.walk(home):
            for f_ in fns:
                q = os.path.join(dp, f_)
                d_[os.path.relpath(q, home)] = (open(q, "rb").read(), os.path.getmtime(q))
        return d_
    s0 = snap()
    roots = []
    for n_ in range(2):
        CAPC.CAP.clear()
        p_ = U.allocateInstance(PL.class_)
        setf(p_, "logger", JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyUiProbe"))
        setf(p_, "dataDirectory", JClass("java.nio.file.Paths").get(os.path.join(home, "mods", "Skyy_SkyyUiProbe")))
        setf(p_, "commandRegistry", U.allocateInstance(CAPC.class_))
        setf(p_, "shutdownTasks", JClass("java.util.concurrent.CopyOnWriteArrayList")())
        m_ = PL.class_.getDeclaredMethod("setup")
        m_.setAccessible(True)
        m_.invoke(p_)
        roots.append(list(CAPC.CAP))
        sd_ = PL.class_.getDeclaredMethod("shutdown")
        sd_.setAccessible(True)
        try:
            sd_.invoke(p_)
        except Exception as ex:
            K.notes.append("LIVE: shutdown %d: %s" % (n_ + 1, str(ex)[:120]))
        time.sleep(0.3)
    ready = [m_ for m_ in records() if "[SkyyUiProbe] %s ready" % VERSION in m_]
    K.eq(len(ready), 2, "LIVE: setup() twice = two '[SkyyUiProbe] %s ready' lines" % VERSION)
    K.check(bool(ready) and "/uiprobe tip / tiplater / tipgear" in ready[0], "LIVE: the ready line names the tip probe: %s" % (ready[:1] or [None])[0])
    for n_, rs in enumerate(roots):
        K.eq([str(c_.getName()) for c_ in rs], ["skyprobe"], "LIVE: start %d registers ONE root /skyprobe" % (n_ + 1))
        if len(rs) == 1:
            r_ = rs[0]
            K.check("uiprobe" in [str(a) for a in r_.getAliases()], "LIVE: start %d alias uiprobe" % (n_ + 1))
            K.eq(sorted(str(k) for k in r_.getSubCommands().keySet()), ["tip", "tiplater"], "LIVE: start %d sub-commands" % (n_ + 1))
            K.eq(int(r_.getVariantCommands().size()), 1, "LIVE: start %d the 1-word usage variant" % (n_ + 1))
    s2 = snap()
    K.check(sorted(s2) == sorted(s0) and all(s2[k] == s0[k] for k in s0), "LIVE: the scratch copy is byte + time identical after both starts (%d files)" % len(s0))
    K.check(not os.path.exists(os.path.join(home, "mods", "Skyy_SkyyUiProbe")), "LIVE: no data folder was created (the probe keeps nothing)")
    K.check(not [m_ for m_ in records() if "SEVERE" in m_ or "Exception" in m_], "LIVE: no error logged")
    K.save()


def run_jar(out):
""")
H = rep(H, """    elif ph == "compare":
        run_cmp(HK.arg("--out"))
""", """    elif ph == "compare":
        run_cmp(HK.arg("--out"))
    elif ph == "live":
        run_live(HK.arg("--out"))
""")
H = rep(H, """    for label in ("jar", "compare", "mkfake", "verify", "exec", "audit"):""", """    for label in ("jar", "compare", "mkfake", "verify", "exec", "live", "audit"):""")
# the jar check: the probe writes no file anywhere
H = rep(H, """    K.check(".setMetadata(" not in _src""", """    K.check(not any(w in _src for w in ("FileOutputStream", "Files.write", "Files.newBufferedWriter", "FileWriter", "Files.createDirect")), "J: the build's Java writes no file")
    K.check(".setMetadata(" not in _src""")
H = rep(H, "import os, sys, json, shutil, zipfile, subprocess, importlib.util, struct, math, zlib, hashlib",
        "import os, sys, re, json, shutil, zipfile, subprocess, importlib.util, struct, math, zlib, hashlib")
save("test_skyyuiprobe_0.9.py", H)
