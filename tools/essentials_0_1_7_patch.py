"""Derive SkyyEssentials/build_skyyessentials_0.1.7.py from the LIVE 0.1.6 (build_skyyessentials_0.1.6.py = the tools/deploy_set.py SET pin).
Run:  python tools/essentials_0_1_7_patch.py   then   python SkyyEssentials/build_skyyessentials_0.1.7.py   (never --deploy: coordinated deploy)
Check: python SkyyEssentials/test_skyyessentials_0.1.7.py   (bare JVM, -Xverify:all; nothing is deployed)
SkyyEssentials uses patch scripts since 0.1.4: edit THIS file, never the generated build script.

0.1.7 = Skyy 2026-10-02 (OPEN-QUESTIONS "Q&A with Skyy 2026-10-02", R2 LOCKED: "Magic Bags are blocked in /trade too (same rule as the AH)";
R9 build order: "SkyyEssentials: bags blocked in /trade"). The Auction House rule copied: SkyyAuctions 0.1.2 AhCfg.applyBuiltin blocks the
keys Skyy_Sack_* (every Magic Bag) and Skyy_Accessory_Bag; its blocked.txt format is "ItemId or Prefix*", exact and case-sensitive, a lone *
ignored. Here:
 1. Server Setup -> Essentials -> Trade: row tradeBlockedItems "Items that can't be traded" (kit type items, opts prefix = ids or Prefix*,
    0-200 entries, live), default "Skyy_Sack_*,Skyy_Accessory_Bag" (= the AH's built-in list; asserted against the SkyyAuctions 0.1.2
    script below). Bound to TCfg.BLOCKED (String); file key tradeBlockedItems in config.properties (appended to an older file with its
    default by TCfg.appendMissing; a new file lists it at the end of the /trade block). The loader (TCfg ROWS type "items") checks the
    format only (id characters, Prefix*, no lone *, no duplicates, max 200) - mod assets may not be loaded at setup; typed values go
    through the kit, which also checks exact ids against the live item map plus the default's cross-mod id (emit ITEM_FN = TBlock.itemOk,
    the SkyyIslands 0.5.2 pattern: reset / Undo / restore of the default work without SkyyAccessories). Not on /tradeadmin config (its
    boxes hold 18 characters); Server Setup (SkyyMenu's items list editor: type an id or Prefix*, or add the held item) and the file are
    the editors. The ready line names the list (TCfg.summary0).
 2. TBlock: the list (parsed once per text - a volatile cache, no lock), blocked(id), firstIn(stacks), the texts.
 3. TBlockF: a SlotFilter (FilterActionType.ADD) on EVERY offer slot of both escrow containers (TStore.armBox, called by newSession).
    The engine asks it inside SimpleItemContainer.cantAddToSlot before any add with filter=true (drag, shift-click, Put all, Quick stack,
    a swap onto an offer slot, sort), so a listed item is refused before anything moves. It touches no container and takes no lock; its
    first refusal of a gesture queues ONE TTask 9 (TStore.blockedTask, the player's world thread): chat + trade page line, the offer window
    and the six inventory sections re-sent (TWindow.resend = its own Window.invalidate, InventoryComponent.markDirty: the SkyyVault 0.1.5
    resync), trade.log BLOCKED-OFFER. REMOVE / DROP are not filtered (a listed item that got in can always be taken out).
 4. TStore.clickReady refuses Ready while either offer holds a listed item; TStore.startCountdown checks the locked offers again and stops
    the countdown (BLOCKED-READY).
 5. TStore.execute (the swap, trade thread): after the drain + agreed-signature check and BEFORE the PAYING marker, the coin takes and the
    swap, a listed item in either drained offer cancels the trade (reason "blocked", BLOCKED-SWAP): finishCancel returns each player's OWN
    offer through the usual owed delivery, no coin moves - a bag that got in by ANY path (another mod adding with filter=false, a list
    change during the countdown) ends here.
 6. Version 0.1.7. Everything else (commands, permission nodes, the other rows, files, bridge keys, deliveries, the durability switch,
    /r, warps, tpa, player switches) stays 0.1.6's.
REVIEW FIXES (the 2026-10-02 review of 0.1.7: PASS, no item creation / loss / duplication; hardening findings 1-3 applied):
 R1. (finding 1) The refusal notice is rate limited: at most ONE notice per side every 1.5 s (TBlockF.NOTICE_MS, lastNotice set by
     TStore.blockedTask). A refusal inside that window is not dropped: its notice waits for the end of the window (TBlockF.delay, 150 ms
     to 1.5 s), so the last refusal of any burst still re-syncs the client; chat, the trade page line and the trade.log BLOCKED-OFFER
     line come once per window (was about one every 150 ms for a client spamming bag moves).
 R2. (finding 2) An emptied or mistyped list is no longer silent. TBlock.audit WARNs once per list text: an empty list, a list that no
     longer blocks Skyy_Sack_* / Skyy_Accessory_Bag (a broader Prefix* covering them counts), an exact id that is not an item on this
     server, a Prefix* that matches no item (with "did you mean ..." for a case typo). It runs at plugin start() (every asset pack is
     loaded; audits before it are skipped), after a hand edit (TCfg.reloadKit) and after an in-game change (kit after=TBlock.changed:
     menu, command, import, restore, undo). The default list's own entries are never called typos (without SkySacks / SkyyAccessories
     they simply have nothing to block). The kit row gets check=TBlock.check: it never refuses, it ASKS (SkyyMenu's confirm step) before
     a save that stops blocking Magic Bags / the Accessory Bag the running list still blocks, or that adds a Prefix* matching no item.
     No danger flag / confirm= (every other save of the row stays one click); the published row is unchanged.
 R3. (finding 3) The trade page's red refusal line is dropped at the next rebuild once either offer (items or coins) changed or it is
     older than 10 s (TradePage.dropStaleNote, the page's own world thread); a click still replaces it as before.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.6.py")
dst = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.7.py")
AH = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.2.py")      # the SET pin of SkyyAuctions (read only)
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")

# the default list = the Auction House's built-in list (SkyyAuctions 0.1.2 AhCfg.applyBuiltin), read from its build script
_ah = open(AH, encoding="utf8").read()
_m = re.search(r'String\[\] keys = new String\[\] \{ ("[^}]*") \};', _ah)
assert _m, "SkyyAuctions 0.1.2: the built-in blocked keys line was not found"
AH_KEYS = re.findall(r'"([^"]+)"', _m.group(1))
DEFAULT_BLOCKED = "Skyy_Sack_*,Skyy_Accessory_Bag"
assert AH_KEYS == DEFAULT_BLOCKED.split(","), "the default no-trade list must be the AH's built-in list %s" % AH_KEYS


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


# ================================================================================================ docstring + version
DOC = '''SkyyEssentials 0.1.7 - build script (javassist via jpype). GENERATED by tools/essentials_0_1_7_patch.py from the LIVE 0.1.6
(build_skyyessentials_0.1.6.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyyessentials_0.1.7.py            -> SkyyEssentials/SkyyEssentials-0.1.7.jar   (never --deploy: tools/deploy_set.py)
Check: python test_skyyessentials_0.1.7.py            (bare JVM, -Xverify:all: the no-trade list end to end on real engine containers, the
                                                        0.1.6 durability checks, two starts on a copy of the live data, byte-compare)

0.1.7 (2026-10-02, Skyy - OPEN-QUESTIONS "Q&A with Skyy 2026-10-02" R2 LOCKED: "Magic Bags are blocked in /trade too (same rule as the
AH)"; R9 build order: SkyyEssentials bags blocked in /trade):
  THE NO-TRADE LIST (Server Setup -> Essentials -> Trade -> "Items that can't be traded", key tradeBlockedItems, an items row: item ids
    or Prefix* entries, comma separated - the Auction House's format; default Skyy_Sack_*,Skyy_Accessory_Bag = SkyyAuctions 0.1.2's
    built-in list (AhCfg.applyBuiltin): every Magic Bag (Skyy_Sack_<type>_<tier>, Skyy_Sack_Omni) and the Accessory Bag). Live: TBlock
    reads TCfg.BLOCKED every time (the parsed list is cached until the text changes). Empty = everything tradeable (an admin's choice).
    Matching = the AH's: exact and case-sensitive, Prefix* = starts with, a lone * is refused.
  1. REFUSED WHEN OFFERED: TBlockF, a SlotFilter (FilterActionType.ADD) on every offer slot of both escrow containers (TStore.armBox in
     newSession). The engine asks it inside SimpleItemContainer.cantAddToSlot before ANY add with filter=true - a drag, a shift-click,
     Put all, Quick stack, a swap onto an offer slot - so a listed item is refused before anything moves: it stays where it was, the
     offers and Ready marks are untouched, no change event fires. The filter touches no container and takes no lock (it runs inside the
     container's write lock); its first refusal of a gesture queues ONE TTask 9 on the player's world thread (TStore.blockedTask): the
     chat line "[Trade] A Magic Bag can't go in a trade - Magic Bags and the Accessory Bag open their owner's own storage. It stays in
     your inventory." (the Accessory Bag and other listed ids get their own words), the same line on the trade page, the offer window
     and the six inventory sections re-sent (TWindow.resend = Window.invalidate, InventoryComponent.markDirty - the SkyyVault 0.1.5
     resync, so a client that drew the move early is corrected), trade.log BLOCKED-OFFER. Taking items out (REMOVE / DROP) is never
     filtered: a listed item that got in can always be taken out.
  2. NEVER READY WITH ONE IN: TStore.clickReady refuses Ready while either offer holds a listed item ("Take a Magic Bag out of your offer
     first - ..." / "<name>'s offer holds a Magic Bag - ... They have to take it out first (or Cancel trade).") - e.g. an item that went
     in before an admin listed it.
  3. COUNTDOWN START: TStore.startCountdown checks the locked offers again; a listed item stops the countdown at once (both are told,
     trade.log BLOCKED-READY).
  4. THE SWAP CHECK (TStore.execute, the trade thread): after both escrows are drained and compared with what was agreed, a listed item in
     EITHER drained offer cancels the whole trade (reason "blocked") BEFORE any coin or item moves - the PAYING marker, the coin takes
     and the swap all come after it - so a bag that got in by ANY path (another mod adding with filter=false, a list change during the
     countdown) ends here: finishCancel gives each player back their OWN offer through the usual owed delivery (storage first, counted
     before and after), coins untouched; both read "<name>'s offer held a Magic Bag - ... Trade cancelled. Everything you put in comes
     back to you."; trade.log BLOCKED-SWAP + CANCEL reason=blocked.
  Deliveries are never blocked: what a trade owes (a player's own items back, or a pre-0.1.7 completed trade) is always handed out.
  CONFIG: TCfg loader row tradeBlockedItems (type items: entries checked like the AH's blocked.txt - id characters, Prefix*, no lone *, no
    duplicates, at most 200; an invalid hand edit keeps the running list and warns); appended to an older config.properties with its
    default (TCfg.appendMissing); new files list it at the end of the /trade block. The kit row (items, opts prefix, 0-200 entries,
    live): SkyyMenu's list editor (type an id or Prefix*, or add the held item, then Save list); the kit checks exact ids against the
    live item map plus the default's cross-mod id Skyy_Accessory_Bag (emit ITEM_FN TBlock.itemOk - the SkyyIslands 0.5.2 pattern, so
    reset / Undo / restore of the default work without SkyyAccessories). Not on /tradeadmin config (that page's boxes hold 18
    characters): Server Setup and the file are the editors. The ready line names the list (TCfg.summary0).
  REVIEW FIXES (2026-10-02 review: PASS, hardening only):
  R1. At most ONE refusal notice per player every 1.5 s (TBlockF.NOTICE_MS): a refusal inside that window waits for its end
      (TBlockF.delay), so a burst still ends with one re-sync of the client, and chat / the page line / trade.log BLOCKED-OFFER come once
      per window instead of about every 150 ms.
  R2. WARN lines in the server log (TBlock.audit, once per list text): an empty list, a list that no longer blocks Skyy_Sack_* or
      Skyy_Accessory_Bag, an exact id that is not an item here, a Prefix* that matches no item ("did you mean Skyy_Sack_*?" for a case
      typo). At plugin start() (assets loaded), after a hand edit (TCfg.reloadKit) and after an in-game change (kit after=TBlock.changed).
      The kit row's check=TBlock.check ASKS before a save that drops Magic Bags / the Accessory Bag or adds a Prefix* matching no item
      (SkyyMenu's confirm step; it never refuses).
  R3. The red refusal line on the trade page goes away at the next rebuild once either offer changed or after 10 s
      (TradePage.dropStaleNote).
  Nothing else changes: commands, permission nodes, the other rows and files, bridge keys, deliveries, the durability switch, /r, warps.

'''
first = s.index('"""') + 3
s = s[:first] + DOC + s[first:]
rep('\nVERSION = "0.1.6"\n', '\nVERSION = "0.1.7"\n')

# ================================================================================================ probes (0.1.7 no-trade list)
rep('''PKG = "com.skyy.essentials"
ES = PKG + ".EssStore"
# 0.1.6: the switch class exists''', '''# 0.1.7: the no-trade list (Skyy 2026-10-02: Magic Bags are blocked in /trade too, the same rule as the Auction House). Every engine member
# TBlockF / TStore.armBox / TStore.resync / TBlock.itemOk touch. The filter mechanics (bytecode 2026-10-02): SimpleItemContainer
# .cantAddToSlot = the global filter allows input AND testFilter(ADD, slot, stack) (the per-slot SlotFilter map setSlotFilter fills), and
# every add with filter=true asks it (InternalContainerUtilItemStack add / set paths, the move paths, sort): client drags
# (InventoryUtils.moveItem -> moveItemStackFromSlotToSlot(..) = filter true), shift-clicks (smartMoveItem -> moveItemStackFromSlot(slot,
# qty, container) = filter true), Put all (moveAllItemStacksTo), Quick stack (CombinedItemContainer.quickStackTo).
BSIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
BFAT = "com.hypixel.hytale.server.core.inventory.container.filter.FilterActionType"
BSFL = "com.hypixel.hytale.server.core.inventory.container.filter.SlotFilter"
BINV = "com.hypixel.hytale.server.core.inventory.InventoryComponent"
for c, m in ((BSIC, "setSlotFilter"), (BSIC, "getCapacity"), (BFAT, "ADD"), (BSFL, "test"), (BINV, "markDirty"),
             (BINV + "$Hotbar", "getComponentType"), (BINV + "$Storage", "getComponentType"), (BINV + "$Backpack", "getComponentType"),
             (BINV + "$Armor", "getComponentType"), (BINV + "$Utility", "getComponentType"), (BINV + "$Tool", "getComponentType"),
             ("com.hypixel.hytale.server.core.entity.entities.player.windows.Window", "invalidate"),
             ("com.hypixel.hytale.server.core.inventory.ItemStack", "getItemId"),
             ("com.hypixel.hytale.server.core.asset.type.item.config.Item", "getAssetMap"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset")):
    B.probe(pool, c, m)
assert any(str(x.getSignature()) == "(Lcom/hypixel/hytale/server/core/inventory/container/filter/FilterActionType;Lcom/hypixel/hytale/server/"
           "core/inventory/container/ItemContainer;SLcom/hypixel/hytale/server/core/inventory/ItemStack;)Z"
           for x in pool.get(BSFL).getDeclaredMethods("test")), "SlotFilter.test(FilterActionType, ItemContainer, short, ItemStack) changed"
assert any(str(x.getSignature()) == "(Lcom/hypixel/hytale/server/core/inventory/container/filter/FilterActionType;SLcom/hypixel/hytale/server/"
           "core/inventory/container/filter/SlotFilter;)V"
           for x in pool.get(BSIC).getDeclaredMethods("setSlotFilter")), "SimpleItemContainer.setSlotFilter(FilterActionType, short, SlotFilter) changed"
# cantAddToSlot must still ask the ADD slot filters (else the early refusal would be gone silently - the swap check would still hold)
import jpype as _jp
_bo = _jp.JClass("java.io.ByteArrayOutputStream")()
_jp.JClass("javassist.bytecode.InstructionPrinter")(_jp.JClass("java.io.PrintStream")(_bo)).print_(pool.get(BSIC).getDeclaredMethod("cantAddToSlot"))
_ca = str(_bo.toString())
assert "testFilter" in _ca and "FilterActionType.ADD" in _ca, "SimpleItemContainer.cantAddToSlot no longer asks the ADD slot filters"

PKG = "com.skyy.essentials"
ES = PKG + ".EssStore"
# 0.1.6: the switch class exists''')

# ================================================================================================ the two new classes
rep('''TRADE_ALL = [tcfg, tcod, trec, tses, tchg, twin, tthr, tjob, ttask, tcd, tpage, tcpg, tst, tfn, trl, tql, ttk]''',
    '''TRADE_ALL = [tcfg, tcod, trec, tses, tchg, twin, tthr, tjob, ttask, tcd, tpage, tcpg, tst, tfn, trl, tql, ttk]
# 0.1.7: the no-trade list - TBlock (the list: parse, match, texts, the kit's item check) and TBlockF (the SlotFilter on every offer slot)
tblk  = pool.makeClass(PKG + ".TBlock")
tbf   = pool.makeClass(PKG + ".TBlockF")
tbf.addInterface(pool.get(BSFL))
BLOCK_ALL = [tblk, tbf]''')

# ================================================================================================ TCfg loader row + default file
ROW_COMMENT = ("tradeBlockedItems: items that can never go in a trade offer - item ids, or Prefix* for every id that starts with Prefix, "
               "separated by commas (exact, case-sensitive). Default = the Auction House's list: Magic Bags (Skyy_Sack_*) and the "
               "Accessory Bag (Skyy_Accessory_Bag). Empty = every item can be traded.")
rep('''    ("gameplay.durability", "Item durability", "bool", "@PKG@.EssDur.ON", 0, 1, "false", "",
     "gameplay.durability: false (the default) = tools, weapons and armor never lose durability, so they never break; items that are already worn keep their value. true = vanilla wear and breaking. Applies at once."),
]''', '''    ("gameplay.durability", "Item durability", "bool", "@PKG@.EssDur.ON", 0, 1, "false", "",
     "gameplay.durability: false (the default) = tools, weapons and armor never lose durability, so they never break; items that are already worn keep their value. true = vanilla wear and breaking. Applies at once."),
    # 0.1.7 (field in TCfg, a String list; lo / hi = entry count): the no-trade list - Magic Bags and the Accessory Bag (Skyy 2026-10-02)
    ("tradeBlockedItems", "Items that can't be traded", "items", "BLOCKED", 0, 200, "%s", "",
     "%s"),
]''' % (DEFAULT_BLOCKED, ROW_COMMENT))
rep('''FILE_ORDER = [REPLY_IDX, IDX["part.tpa"], IDX["part.msg"], IDX["tpa.expireSeconds"], IDX["tpa.cooldownSeconds"],
              IDX["privacy.staffBypass"]] + list(range(0, 13)) + [IDX["gameplay.durability"]]
FILE_BLOCKS = {1: "# ---- teleports and private messages (SkyyEssentials 0.1.3) ----", 6: "# ---- /trade (SkyyEssentials 0.1.2) ----",
               19: "# ---- gameplay (SkyyEssentials 0.1.6) ----"}''',
    '''FILE_ORDER = [REPLY_IDX, IDX["part.tpa"], IDX["part.msg"], IDX["tpa.expireSeconds"], IDX["tpa.cooldownSeconds"],
              IDX["privacy.staffBypass"]] + list(range(0, 13)) + [IDX["tradeBlockedItems"], IDX["gameplay.durability"]]
# 0.1.7: tradeBlockedItems closes the /trade block of a NEW file (an existing file gets it appended by TCfg.appendMissing)
FILE_BLOCKS = {1: "# ---- teleports and private messages (SkyyEssentials 0.1.3) ----", 6: "# ---- /trade (SkyyEssentials 0.1.2) ----",
               20: "# ---- gameplay (SkyyEssentials 0.1.6) ----"}''')
rep('''    if typ in ("bool",):
        F(tcfg, "public static volatile boolean %s = %s;" % (fld, dflt))''', '''    if typ == "items":
        F(tcfg, "public static volatile String %s = %s;" % (fld, jstr(dflt)))      # 0.1.7: the no-trade list (canonical "a,b" text)
    elif typ in ("bool",):
        F(tcfg, "public static volatile boolean %s = %s;" % (fld, dflt))''')
rep('''for i, r in enumerate(ROWS):
    typ, fld = r[2], r[3]
    if typ == "bool":
        get_lines.append''', '''for i, r in enumerate(ROWS):
    typ, fld = r[2], r[3]
    if typ == "items":           # 0.1.7: the no-trade list (the value is the canonical text itself)
        get_lines.append('  if (i == %d) return %s == null ? "" : %s;' % (i, fld, fld))
        put_lines.append('    if (i == %d) { %s = v; return true; }' % (i, fld))
        continue
    if typ == "bool":
        get_lines.append''')

# ================================================================================================ TBlock (compiled after the TCfg fields, before
# TCfg.canon calls TBlock.canonList and before the config kit compiles CfgRows.itemOk -> TBlock.itemOk)
TBLOCK = r'''
# =====================================================================================================================================
# 0.1.7 the no-trade list (Skyy 2026-10-02: Magic Bags are blocked in /trade too - the same rule as the Auction House). TBlock = the list
# (TCfg.BLOCKED, the kit row tradeBlockedItems): parse once per text, match like SkyyAuctions 0.1.2 AhItem.blockedReason (exact entry or
# "Prefix*" = starts with, case-sensitive, a lone * ignored - the loader and the kit refuse one anyway), the texts, the kit's item check.
# No lock anywhere: TBlockF calls blocked() inside the engine's container write lock.
# =====================================================================================================================================
BLOCK_OWN_EXTRA = ["Skyy_Accessory_Bag"]      # the default list's cross-mod exact id (SkyyAccessories' item, not a vanilla asset)
for _x in BLOCK_OWN_EXTRA:
    assert _x in ROWS[IDX["tradeBlockedItems"]][6].split(","), "BLOCK_OWN_EXTRA %s is not in the default list" % _x
T.update({
    "FAT": BFAT, "SFL": BSFL, "CTY": "com.hypixel.hytale.component.ComponentType",
    "IHOT": BINV + "$Hotbar", "ISTO": BINV + "$Storage", "IBAK": BINV + "$Backpack",
    "IARM": BINV + "$Armor", "IUTI": BINV + "$Utility", "ITOO": BINV + "$Tool",
})
# CACHE = { String text, java.util.HashSet exact ids, String[] prefixes } for the text it was built from (swapped in one write)
F(tblk, "public static volatile Object[] CACHE = null;")
M(tblk, r"""
public static boolean idChars(String id) {
  if (id == null || id.length() == 0 || id.length() > 120) return false;
  for (int k = 0; k < id.length(); k++) {
    char c = id.charAt(k);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.')) return false;
  }
  return true;
}""")
# the config kit's item check (emit ITEM_FN, compiled into CfgRows.itemOk after its own idChars test): the live item map, plus the
# default list's own cross-mod id, so the row's default stays valid without SkyyAccessories (reset, Undo, History restore). The kit
# catches a throw (false).
M(tblk, r"""
public static boolean itemOk(String id) {
  if (id == null) return false;
  if (@OWNX@) return true;
  return @ITEM@.getAssetMap().getAsset(id) != null;
}""".replace("@OWNX@", " || ".join('id.equals("%s")' % _x for _x in BLOCK_OWN_EXTRA)))
# a list as the LOADER reads it (config.properties at start, TCfg.reloadKit after a hand edit): entries trimmed, empty ones skipped, each
# an item id or Prefix* (id characters; a lone * has an empty prefix and is refused), no duplicates, at most max entries. Canonical "a,b"
# (the kit's items format) or null = not valid (the loader keeps the running list and warns). Exact ids are NOT checked against the item
# map here (mod assets may not be loaded at setup); typed values go through the kit, which checks them.
M(tblk, r"""
public static String canonList(String raw, int max) {
  if (raw == null) return null;
  String[] parts = raw.split(",");
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  for (int k = 0; k < parts.length; k++) {
    String e = parts[k].trim();
    if (e.length() == 0) continue;
    String base = e.endsWith("*") ? e.substring(0, e.length() - 1) : e;
    if (!idChars(base)) return null;
    if (!seen.add(e)) return null;
    out.add(e);
  }
  if (out.size() > max) return null;
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < out.size(); k++) {
    if (k > 0) sb.append(',');
    sb.append((String) out.get(k));
  }
  return sb.toString();
}""")
# the parsed list, rebuilt only when TCfg.BLOCKED changes (the kit, the loader and reloadKit swap the whole String in one write; a
# reader sees the old or the new list, never half of one)
M(tblk, r"""
public static Object[] rules() {
  String src = @PKG@.TCfg.BLOCKED;
  if (src == null) src = "";
  Object[] c = CACHE;
  if (c != null && src.equals(c[0])) return c;
  java.util.HashSet ex = new java.util.HashSet();
  java.util.ArrayList pre = new java.util.ArrayList();
  String[] parts = src.split(",");
  for (int k = 0; k < parts.length; k++) {
    String e = parts[k].trim();
    if (e.length() == 0) continue;
    if (e.endsWith("*")) {
      String b = e.substring(0, e.length() - 1);
      if (b.length() > 0) pre.add(b);
    } else ex.add(e);
  }
  String[] pa = new String[pre.size()];
  for (int k = 0; k < pa.length; k++) pa[k] = (String) pre.get(k);
  c = new Object[] { src, ex, pa };
  CACHE = c;
  return c;
}""")
M(tblk, r"""
public static boolean blocked(String id) {
  if (id == null || id.length() == 0) return false;
  Object[] c = rules();
  if (((java.util.HashSet) c[1]).contains(id)) return true;
  String[] pa = (String[]) c[2];
  for (int k = 0; k < pa.length; k++) if (id.startsWith(pa[k])) return true;
  return false;
}""")
# the first listed item id in a set of stacks (an offer snapshot or a drained escrow), or null
M(tblk, r"""
public static String firstIn(@IS@[] a) {
  if (a == null) return null;
  for (int k = 0; k < a.length; k++) {
    if (a[k] == null || a[k].isEmpty()) continue;
    String id = a[k].getItemId();
    if (blocked(id)) return id;
  }
  return null;
}""")
M(tblk, r"""
public static boolean bag(String id) { return id != null && (id.startsWith("Skyy_Sack_") || id.equals("Skyy_Accessory_Bag")); }""")
M(tblk, r"""
public static String what(String id) {
  if (id == null) return "an item";
  if (id.equals("Skyy_Accessory_Bag")) return "the Accessory Bag";
  if (id.startsWith("Skyy_Sack_")) return "a Magic Bag";
  return id;
}""")
M(tblk, r"""
public static String why(String id) {
  if (bag(id)) return "Magic Bags and the Accessory Bag open their owner's own storage, so they can't be traded";
  return "it is on this server's no-trade list";
}""")
# the refusal when an item is dragged / shift-clicked / put into an offer (TBlockF said no: nothing moved)
M(tblk, r"""
public static String refused(String id) {
  String w = what(id);
  if (w.length() > 0) w = w.substring(0, 1).toUpperCase() + w.substring(1);
  if (bag(id)) return "-" + w + " can't go in a trade - Magic Bags and the Accessory Bag open their owner's own storage. It stays in your inventory.";
  return "-" + w + " can't go in a trade - it is on this server's no-trade list. It stays in your inventory.";
}""")
M(tblk, r"""
public static String takeOut(String id) { return "-Take " + what(id) + " out of your offer first - " + why(id) + "."; }""")
M(tblk, r"""
public static String theirs(String name, String id) {
  return "-" + name + "'s offer holds " + what(id) + " - " + why(id) + ". They have to take it out first (or Cancel trade).";
}""")
M(tblk, r"""
public static String stopped(String name, String id) {
  return "-" + name + "'s offer holds " + what(id) + " - " + why(id) + ". Take it out, then both click Ready again.";
}""")
M(tblk, r"""
public static String swap(String name, String id) {
  return "-" + name + "'s offer held " + what(id) + " - " + why(id) + ". Trade cancelled. Everything you put in comes back to you.";
}""")
# ---- 0.1.7 review (finding 2): an emptied or mistyped list is no longer silent. The default list's entries (generated from the loader
# row, so they can never drift from it), a list read as entries, "does this list still block everything entry X blocks", this server's
# item ids, the WARN lines (audit) and the kit's check= hook (a question before a save that drops a default entry). None of it runs in
# the slot filter's path (it reads the item map and logs).
F(tblk, "public static volatile String AUDITED = null;")      # the list text the last audit read (one audit per text)
F(tblk, "public static volatile boolean READY = false;")      # plugin start() ran: every asset pack is loaded (audits before it skip)
M(tblk, r"""
public static String[] defs() { return new String[] { @DEFS@ }; }""".replace("@DEFS@", ", ".join('"%s"' % _x for _x in ROWS[IDX["tradeBlockedItems"]][6].split(","))))
M(tblk, r"""
public static java.util.ArrayList entries(String src) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (src == null) return out;
  String[] parts = src.split(",");
  for (int k = 0; k < parts.length; k++) {
    String e = parts[k].trim();
    if (e.length() > 0) out.add(e);
  }
  return out;
}""")
# does the list es block everything the entry want blocks? want = an exact id (an equal entry or a Prefix* it starts with) or a Prefix*
# (only a Prefix* whose prefix starts that prefix: Skyy_* covers Skyy_Sack_*, Skyy_Sack_Mining_* does not; exact ids never cover one)
M(tblk, r"""
public static boolean covers(java.util.ArrayList es, String want) {
  if (es == null || want == null || want.length() == 0) return false;
  boolean wp = want.endsWith("*");
  String wb = wp ? want.substring(0, want.length() - 1) : want;
  for (int k = 0; k < es.size(); k++) {
    String e = (String) es.get(k);
    if (e.endsWith("*")) {
      String b = e.substring(0, e.length() - 1);
      if (b.length() > 0 && wb.startsWith(b)) return true;
    } else if (!wp && e.equals(wb)) return true;
  }
  return false;
}""")
M(tblk, r"""
public static boolean isDef(String e) {
  String[] d = defs();
  for (int k = 0; k < d.length; k++) if (d[k].equals(e)) return true;
  return false;
}""")
M(tblk, r"""
public static String whatAll(String e) {
  if (e == null) return "items";
  if (e.startsWith("Skyy_Sack_")) return "Magic Bags";
  if (e.equals("Skyy_Accessory_Bag")) return "the Accessory Bag";
  return e;
}""")
# this server's item ids (a copy of the live item map's keys), or null when the map can't be read (an empty map = not loaded)
M(tblk, r"""
public static java.util.HashSet itemIds() {
  try {
    java.util.Map m = @ITEM@.getAssetMap().getAssetMap();
    if (m == null) return null;
    return new java.util.HashSet(m.keySet());
  } catch (Throwable t) { return null; }
}""")
M(tblk, r"""
public static boolean anyStarts(java.util.Set ids, String b) {
  java.util.Iterator it = ids.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof String && ((String) o).startsWith(b)) return true;
  }
  return false;
}""")
M(tblk, r"""
public static String clip(String s, int n) {
  if (s == null) return "";
  return s.length() <= n ? s : s.substring(0, n) + "...";
}""")
# "; did you mean Skyy_Sack_*?" for a case typo (skyy_sack_*): an item id that starts with the prefix when case is ignored, else ""
M(tblk, r"""
public static String hintPre(java.util.Set ids, String b) {
  String lb = b.toLowerCase(java.util.Locale.ROOT);
  java.util.Iterator it = ids.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof String)) continue;
    String id = (String) o;
    if (id.length() >= b.length() && id.toLowerCase(java.util.Locale.ROOT).startsWith(lb)) return "; did you mean " + clip(id.substring(0, b.length()), 40) + "*?";
  }
  return "";
}""")
M(tblk, r"""
public static String hintId(java.util.Set ids, String e) {
  java.util.Iterator it = ids.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof String && ((String) o).equalsIgnoreCase(e)) return "; did you mean " + clip((String) o, 40) + "?";
  }
  return "";
}""")
# the same for a default entry typed in the wrong case on a server whose items don't show it (no SkySacks / SkyyAccessories)
M(tblk, r"""
public static String hintDef(String e) {
  String[] d = defs();
  for (int k = 0; k < d.length; k++) if (d[k].equalsIgnoreCase(e)) return "; did you mean " + d[k] + "?";
  return "";
}""")
# the WARN lines for a list (src) read against this server's item ids (ids null / empty = the item map can't be read: only the default
# entry lines). The default list's own entries are never reported as typos (a server without SkySacks / SkyyAccessories simply has
# nothing for them to block).
M(tblk, r"""
public static java.util.ArrayList auditLines(String src, java.util.Set ids) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList es = entries(src);
  String row = " (Server Setup > Essentials > Trade > Items that can't be traded)";
  if (es.size() == 0) {
    out.add("the no-trade list is EMPTY - Magic Bags and the Accessory Bag CAN be traded" + row + ". Reset that row for the default list @DEFT@.");
    return out;
  }
  String[] d = defs();
  for (int k = 0; k < d.length; k++) {
    if (!covers(es, d[k])) out.add("the no-trade list does not block " + d[k] + " - " + whatAll(d[k]) + " CAN be traded" + row + ". The default list is @DEFT@.");
  }
  if (ids == null || ids.size() == 0) return out;
  for (int k = 0; k < es.size(); k++) {
    String e = (String) es.get(k);
    if (isDef(e)) continue;
    if (e.endsWith("*")) {
      String b = e.substring(0, e.length() - 1);
      if (b.length() == 0 || anyStarts(ids, b)) continue;
      String h = hintPre(ids, b);
      if (h.length() == 0) h = hintDef(e);
      out.add("the no-trade list entry " + clip(e, 60) + " matches no item on this server, so it blocks nothing (ids are case-sensitive" + h + ")" + row + ".");
    } else if (!ids.contains(e)) {
      String h = hintId(ids, e);
      if (h.length() == 0) h = hintDef(e);
      out.add("the no-trade list entry " + clip(e, 60) + " is not an item on this server, so it blocks nothing (ids are case-sensitive" + h + ")" + row + ".");
    }
  }
  return out;
}""".replace("@DEFT@", ROWS[IDX["tradeBlockedItems"]][6]))
# the audit of the running list: its WARN lines, once per list text, from plugin start() on (before it the item map is not complete).
# Returns the lines it logged (null = skipped: before start(), or the same text as the last audit). Callers: auditStart (plugin
# start()), TCfg.reloadKit (a hand edit), changed (the kit's after= hook: menu, command, import, restore, undo).
M(tblk, r"""
public static java.util.ArrayList audit(String when) {
  try {
    if (!READY) return null;
    String src = @PKG@.TCfg.BLOCKED;
    if (src == null) src = "";
    if (src.equals(AUDITED)) return null;
    AUDITED = src;
    java.util.ArrayList ls = auditLines(src, itemIds());
    for (int k = 0; k < ls.size(); k++) @ES@.warn((String) ls.get(k) + " [" + when + "]");
    return ls;
  } catch (Throwable t) { return null; }
}""")
M(tblk, r"""
public static java.util.ArrayList auditStart() {
  READY = true;
  AUDITED = null;
  return audit("start");
}""")
M(tblk, r"""
public static void changed(String key) { audit("Server Setup change"); }""")
# the kit's check= hook of tradeBlockedItems (value = the canonical list the kit already validated: exact ids are known items, Prefix*
# well formed). It never refuses. It ASKS ("?question": SkyyMenu's confirm step, then the same save with confirm yes) before a save that
# (a) stops blocking Magic Bags / the Accessory Bag that the running list still blocks (a broader Prefix* that still covers them is
# fine; a list that already lacks them is not asked about again) or (b) adds a Prefix* that matches no item on this server. Import and
# restore treat a question as passed (SkyyMenu confirms those itself); Undo sends confirm yes.
M(tblk, r"""
public static String check(String key, String value) {
  java.util.ArrayList now = entries(value);
  java.util.ArrayList had = entries(@PKG@.TCfg.BLOCKED);
  String[] d = defs();
  String le = "";
  String lw = "";
  for (int k = 0; k < d.length; k++) {
    if (!covers(had, d[k]) || covers(now, d[k])) continue;
    if (le.length() > 0) { le = le + " and "; lw = lw + " and "; }
    le = le + d[k];
    lw = lw + whatAll(d[k]);
  }
  String miss = null;
  String hint = "";
  java.util.HashSet ids = itemIds();
  if (ids != null && ids.size() > 0) {
    for (int k = 0; k < now.size() && miss == null; k++) {
      String e = (String) now.get(k);
      if (!e.endsWith("*") || had.contains(e) || isDef(e)) continue;
      String b = e.substring(0, e.length() - 1);
      if (b.length() == 0 || anyStarts(ids, b)) continue;
      miss = e;
      hint = hintPre(ids, b);
      if (hint.length() == 0) hint = hintDef(e);
    }
  }
  if (le.length() == 0 && miss == null) return null;
  String q = "";
  if (le.length() > 0) q = "Without " + le + ", " + lw + " can be traded again.";
  if (miss != null) {
    String m = "Nothing on this server matches " + clip(miss, 40) + " (ids are case-sensitive" + hint + ").";
    if (q.length() == 0) q = m;
    else if (q.length() + 1 + m.length() + 13 <= 200) q = q + " " + m;
  }
  return "?" + q + " Save anyway?";
}""")

'''
rep(r'''F(tcfg, "public static final String DEFAULT_TEXT = %s;" % jstr(DEFAULT_TEXT).replace("\n", "\\n"))''',
    r'''F(tcfg, "public static final String DEFAULT_TEXT = %s;" % jstr(DEFAULT_TEXT).replace("\n", "\\n"))''' + TBLOCK)

# ================================================================================================ TCfg: canon / canonFile / rule / summary
rep('''public static String canon(int i, String raw) {
  if (raw == null) return null;
  String v = raw.trim().toLowerCase();''', '''public static String canon(int i, String raw) {
  if (raw == null) return null;
  // 0.1.7: the no-trade list keeps its case (item ids are case-sensitive): checked and joined by TBlock.canonList (hi = max entries)
  if (TYPES[i].equals("items")) return @PKG@.TBlock.canonList(raw, (int) HI[i]);
  String v = raw.trim().toLowerCase();''')
rep('''  if (t.equals("bool") || t.equals("mode")) return canon(i, raw);
  long n = parseAmount(raw == null ? "" : raw.trim());''', '''  if (t.equals("bool") || t.equals("mode") || t.equals("items")) return canon(i, raw);
  long n = parseAmount(raw == null ? "" : raw.trim());''')
rep('''  if (t.equals("mode")) return "use page or chest";
  return "use a whole number from " + LO[i] + " to " + HI[i];''', '''  if (t.equals("mode")) return "use page or chest";
  if (t.equals("items")) return "use item ids or Prefix* entries separated by commas, each once, at most " + HI[i] + " (a lone * is not allowed)";
  return "use a whole number from " + LO[i] + " to " + HI[i];''')
rep('''    + ", staff bypass " + (@ES@.STAFF_BYPASS ? "on" : "off");
}""")''', '''    + ", staff bypass " + (@ES@.STAFF_BYPASS ? "on" : "off")
    + ", not tradeable: " + (BLOCKED == null || BLOCKED.length() == 0 ? "nothing (empty list)" : BLOCKED);
}""")''')

# ================================================================================================ config kit row
KIT_HELP = "Ids or Prefix* that never go in a trade. Default: Magic Bags + the Accessory Bag (as on the AH)."
rep('''    ("tradeMaxCoins", "Max coins per trade", "trade", "int", "0", "0", "1000000000000000", "", "coins", "live",
     "The most coins one player can put in one trade. 0 = no cap.", "field:TCfg.MAX_COINS" + CF + "tradeMaxCoins"),''',
    '''    ("tradeMaxCoins", "Max coins per trade", "trade", "int", "0", "0", "1000000000000000", "", "coins", "live",
     "The most coins one player can put in one trade. 0 = no cap.", "field:TCfg.MAX_COINS" + CF + "tradeMaxCoins"),
    # 0.1.7: the no-trade list (Skyy 2026-10-02: Magic Bags are blocked in /trade too - the same rule as the Auction House). An items row
    # (ids or Prefix*; SkyyMenu's list editor with "add the held item"); default = the AH's built-in list. live: the slot filter, Ready
    # and the swap check read TCfg.BLOCKED every time (TBlock caches the parsed text until it changes). Review fix: check=TBlock.check
    # asks before a save that drops Magic Bags / the Accessory Bag or adds a Prefix* matching no item (never refuses); after=TBlock.changed
    # writes the audit's WARN lines for the new list (menu, command, import, restore, undo).
    ("tradeBlockedItems", "Items that can't be traded", "trade", "items", "%s", "0", "200", "prefix", "", "live",
     "%s", "field:TCfg.BLOCKED" + CF + "tradeBlockedItems;after=TBlock.changed;check=TBlock.check"),''' % (DEFAULT_BLOCKED, KIT_HELP))
rep('''kit = CFG.emit(pool, PKG, MOD="SkyyEssentials", TITLE="Essentials", VERSION=VERSION, NODE="skyyessentials.admin", CATS=KIT_CATS,
               ROWS=KIT_ROWS, FILES=["Skyy_SkyyEssentials/config.properties"],
               NOTE="Warps editor: /warpadmin. World spawn: vanilla /spawn set. Trade keys also on /tradeadmin config.",
               RELOAD="TCfg.reloadKit", KEEP=10, DEFAULTS={"config.properties": DEFAULT_TEXT}, PERM_FN="EssPerm.has")''',
    '''# 0.1.7: the kit's item check for the items row tradeBlockedItems (emit ITEM_FN, compiled straight into CfgRows.itemOk; TBlock.itemOk is
# compiled above): the live item map plus the default list's cross-mod id Skyy_Accessory_Bag, so the row's own default stays valid
# without SkyyAccessories (reset / Undo / History restore - the SkyyIslands 0.5.2 lesson). ITEMS = the same for the build-time default
# check (Assets.zip ids + that id; None = Assets.zip not found = no id check, as before).
_ess_assets = CFG._items_from_assets()
ESS_ITEMS = None if _ess_assets is None else (set(_ess_assets) | set(BLOCK_OWN_EXTRA))
kit = CFG.emit(pool, PKG, MOD="SkyyEssentials", TITLE="Essentials", VERSION=VERSION, NODE="skyyessentials.admin", CATS=KIT_CATS,
               ROWS=KIT_ROWS, FILES=["Skyy_SkyyEssentials/config.properties"],
               NOTE="Warps editor: /warpadmin. World spawn: vanilla /spawn set. Trade keys also on /tradeadmin config.",
               RELOAD="TCfg.reloadKit", KEEP=10, DEFAULTS={"config.properties": DEFAULT_TEXT}, PERM_FN="EssPerm.has",
               ITEMS=ESS_ITEMS, ITEM_FN="TBlock.itemOk")''')

# ================================================================================================ TWindow.resend (the SkyyVault 0.1.5 fix)
rep('''C(twin, r"""
public TWindow(@IC@ c, @PKG@.TSession s, int side, int mode) { super(c); this.sess = s; this.side = side; this.mode = mode; this.dead = false; this.page = null; }""")''',
    '''C(twin, r"""
public TWindow(@IC@ c, @PKG@.TSession s, int side, int mode) { super(c); this.sess = s; this.side = side; this.mode = mode; this.dead = false; this.page = null; }""")
# 0.1.7: Window.invalidate() is PROTECTED - only the window itself may call it (SkyyVault 0.1.5: calling it from another class was an
# IllegalAccessError). The engine then sends one UpdateWindow on its next window tick (WindowManager.updateWindows -> consumeIsDirty),
# exactly what it does after every successful container change. Used after a refused offer (TStore.resync).
M(twin, "public void resend() { invalidate(); }")''')

# ================================================================================================ TBlockF (after TTask's constructor)
TBLOCKF = r'''
# ---- 0.1.7 TBlockF: the no-trade SlotFilter on every offer slot of one side (FilterActionType.ADD; TStore.armBox). The engine calls test()
# inside SimpleItemContainer.cantAddToSlot, inside the container's write lock, for every add with filter=true (drags, shift-clicks, Put
# all, Quick stack, swaps, sort). A listed item is refused BEFORE anything moves; everything else passes. It touches no container and
# takes no lock (no TSession method, no monitor): it reads the list (TBlock, lock-free) and notes the refusal, and the first refusal of a
# gesture queues ONE notice task (TTask 9 -> TStore.blockedTask on the player's world thread; queued is cleared there or in taskDone).
# An error while DECIDING passes the item (the Ready check and the swap check in TStore.execute still refuse a trade that holds one); a
# failing notice never changes the decision (its own try).
# Review fix (finding 1): at most ONE notice per side every NOTICE_MS (1.5 s): lastNotice = when this side's last notice ran
# (TStore.blockedTask); a refusal inside the window queues its notice for the END of the window (delay), so a burst of refused moves
# still ends with one client re-sync, and chat / the page line / the trade.log line come once per window.
for _f in ("public @PKG@.TSession sess;", "public int side;", "public volatile String last;",
           "public java.util.concurrent.atomic.AtomicBoolean queued;", "public java.util.concurrent.atomic.AtomicInteger hits;",
           "public volatile long lastNotice;", "public static final long NOTICE_MS = 1500L;"):
    F(tbf, _f)
C(tbf, r"""
public TBlockF(@PKG@.TSession s, int side) {
  this.sess = s;
  this.side = side;
  this.last = null;
  this.queued = new java.util.concurrent.atomic.AtomicBoolean(false);
  this.hits = new java.util.concurrent.atomic.AtomicInteger(0);
  this.lastNotice = 0L;
}""")
# how long a queued notice waits: at least 150 ms (a gesture's refusals coalesce and the engine finishes its move first), and until
# NOTICE_MS after this side's last notice; never longer than NOTICE_MS (a clock set back can't hold a notice longer)
M(tbf, r"""
public static long delay(long last, long now) {
  long w = last + NOTICE_MS - now;
  if (w < 150L) w = 150L;
  if (w > NOTICE_MS) w = NOTICE_MS;
  return w;
}""")
M(tbf, r"""
public boolean test(@FAT@ a, @IC@ c, short slot, @IS@ st) {
  String id = null;
  try {
    if (a != @FAT@.ADD || st == null || st.isEmpty()) return true;
    id = st.getItemId();
    if (!@PKG@.TBlock.blocked(id)) return true;
  } catch (Throwable x) { return true; }
  // refused from here on, whatever the notice does (its own try: a failure there never lets the item in)
  try {
    this.last = id;
    this.hits.incrementAndGet();
    if (this.queued.compareAndSet(false, true)) {
      @PKG@.TSession s = this.sess;
      java.util.UUID u = s == null ? null : s.u[this.side];
      @PKG@.TTask t = new @PKG@.TTask(9, s, this.side, u, (String) null);
      t.obj = this;
      @HSV@.SCHEDULED_EXECUTOR.schedule(t, delay(this.lastNotice, System.currentTimeMillis()), java.util.concurrent.TimeUnit.MILLISECONDS);
    }
  } catch (Throwable e) { this.queued.set(false); }
  return false;
}""")
'''
rep('''C(ttk, "public TTick() { this.n = 0; }")''', '''C(ttk, "public TTick() { this.n = 0; }")''' + TBLOCKF)

# ================================================================================================ TStore: taskDone, armBox / resync, newSession
rep('''public static void taskDone(@PKG@.TTask t) {
  if (t.kind == 4 && t.uuid != null) DELIVERING.remove(t.uuid);
  if (t.kind == 5 && t.sess != null && t.side >= 0) t.sess.clearRefresh(t.side);
}""")''', '''public static void taskDone(@PKG@.TTask t) {
  if (t.kind == 4 && t.uuid != null) DELIVERING.remove(t.uuid);
  if (t.kind == 5 && t.sess != null && t.side >= 0) t.sess.clearRefresh(t.side);
  // 0.1.7: a no-trade notice that could not run (player gone, no world) - the next refusal may queue one again
  if (t.kind == 9 && t.obj instanceof @PKG@.TBlockF) ((@PKG@.TBlockF) t.obj).queued.set(false);
}""")''')
rep('''M(tst, r"""
public static @PKG@.TSession newSession(@PR@ a, @PR@ b) {''', '''# 0.1.7: the no-trade filter on every offer slot of one side (TBlockF, FilterActionType.ADD). A failure (a game update changed the filter API)
# costs only the early refusal: clickReady, startCountdown and the swap check in execute still refuse a trade that holds a listed item.
M(tst, r"""
public static void armBox(@PKG@.TSession s, int side) {
  try {
    @PKG@.TBlockF f = new @PKG@.TBlockF(s, side);
    @SIC@ b = s.box[side];
    int cap = b.getCapacity();
    for (int k = 0; k < cap; k++) b.setSlotFilter(@FAT@.ADD, (short) k, f);
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("blockf", "could not put the no-trade filter on the trade offer slots (" + t + ") - listed items are still refused at Ready and at the swap"); }
}""")
# 0.1.7: the six inventory sections (the engine re-sends only the dirty ones: PlayerSendInventorySystem)
M(tst, r"""
public static @CTY@ invType(int i) {
  if (i == 0) return @IHOT@.getComponentType();
  if (i == 1) return @ISTO@.getComponentType();
  if (i == 2) return @IBAK@.getComponentType();
  if (i == 3) return @IARM@.getComponentType();
  if (i == 4) return @IUTI@.getComponentType();
  if (i == 5) return @ITOO@.getComponentType();
  return null;
}""")
# 0.1.7: after a refused offer, the truth to this player's client on the next tick: the offer window (TWindow.resend -> UpdateWindow) and
# the whole inventory (markDirty on all six sections) - the SkyyVault 0.1.5 resync, so a client that drew the refused move early is
# corrected. World thread (TStore.blockedTask).
M(tst, r"""
public static void resync(@PKG@.TSession s, int side, @REF@ ref, @ST@ st) {
  try {
    @PKG@.TWindow w = s.win[side];
    if (w != null && !w.dead) w.resend();
  } catch (Throwable t) { }
  for (int i = 0; i < 6; i++) {
    try {
      @CTY@ ct = invType(i);
      if (ct == null) continue;
      @INVC@ c = (@INVC@) st.getComponent(ref, ct);
      if (c != null) c.markDirty();
    } catch (Throwable t) { }
  }
}""")
M(tst, r"""
public static @PKG@.TSession newSession(@PR@ a, @PR@ b) {''')
rep('''    s.box[i].setGlobalFilter(@FT@.ALLOW_ALL);
    s.epoch[i] = @PKG@.TCfg.bridge().get("profile:epoch:" + s.u[i]);''', '''    s.box[i].setGlobalFilter(@FT@.ALLOW_ALL);
    armBox(s, i);         // 0.1.7: the no-trade filter on every offer slot
    s.epoch[i] = @PKG@.TCfg.bridge().get("profile:epoch:" + s.u[i]);''')

# ================================================================================================ TStore: cancel texts, the swap check
rep('''  else if (reason.equals("admin")) a = "An admin cancelled this trade.";''', '''  else if (reason.equals("admin")) a = "An admin cancelled this trade.";
  else if (reason.equals("blocked")) a = w + "'s offer held an item that can't be traded - trade cancelled.";''')
rep('''# CANCELLED: each player's own escrow goes back to that player (never swapped); the record is written before anything is delivered.''',
    '''# 0.1.7: the swap check's words (execute names the listed item): the same line for both players
M(tst, r"""
public static String[] blockedMsg(@PKG@.TSession s, int by, String id) {
  String n = (by >= 0 && by <= 1) ? s.name[by] : "Someone";
  String m = @PKG@.TBlock.swap(n, id);
  return new String[] { m, m };
}""")
# CANCELLED: each player's own escrow goes back to that player (never swapped); the record is written before anything is delivered.''')
rep('''  if (bad) why = "offer-changed";
  else if (!sig(ia).equals(s.agreed[0]) || !sig(ib).equals(s.agreed[1])) why = "offer-changed";
  if (why == null && @ES@.online(ua) == null) { why = "disconnect"; by = 0; }''', '''  if (bad) why = "offer-changed";
  else if (!sig(ia).equals(s.agreed[0]) || !sig(ib).equals(s.agreed[1])) why = "offer-changed";
  // 0.1.7 THE SWAP CHECK: an item on the no-trade list in either drained offer cancels the whole trade here, BEFORE the PAYING marker, any
  // coin take or the swap - each player gets their own offer back (finishCancel). Catches a bag that got past the slot filter by ANY path
  // (another mod adding with filter=false, a list change during the countdown).
  String blk = null;
  if (why == null) {
    blk = @PKG@.TBlock.firstIn(ia);
    if (blk != null) { why = "blocked"; by = 0; }
    else {
      blk = @PKG@.TBlock.firstIn(ib);
      if (blk != null) { why = "blocked"; by = 1; }
    }
  }
  if (why == null && @ES@.online(ua) == null) { why = "disconnect"; by = 0; }''')
rep('''  if (why != null) {
    long owA = tookA ? refund(s, 0, ca) : 0L;
    long owB = tookB ? refund(s, 1, cb) : 0L;
    finishCancel(s, ia, ib, why, cancelMsg(s, why, by, by >= 0 ? s.name[by] : (String) null), owA, owB);
    return;
  }''', '''  if (why != null) {
    long owA = tookA ? refund(s, 0, ca) : 0L;
    long owB = tookB ? refund(s, 1, cb) : 0L;
    String[] cm = null;
    if ("blocked".equals(why) && blk != null) {
      cm = blockedMsg(s, by, blk);
      log("BLOCKED-SWAP " + ids(s) + " " + s.name[by] + "'s offer held " + blk + " (no-trade list) - cancelled before any coin or item moved");
    } else cm = cancelMsg(s, why, by, by >= 0 ? s.name[by] : (String) null);
    finishCancel(s, ia, ib, why, cm, owA, owB);
    return;
  }''')

# ================================================================================================ TStore: countdown start + Ready
rep('''public static String startCountdown(@PKG@.TSession s, int tok, int by) {
  String sa = sig(snapshot(s.box[0]));
  String sb = sig(snapshot(s.box[1]));
  if (!s.setAgreed(tok, sa, sb)) return "=The offers just changed - click Ready again.";''', '''public static String startCountdown(@PKG@.TSession s, int tok, int by) {
  @IS@[] xa = snapshot(s.box[0]);
  @IS@[] xb = snapshot(s.box[1]);
  String sa = sig(xa);
  String sb = sig(xb);
  if (!s.setAgreed(tok, sa, sb)) return "=The offers just changed - click Ready again.";
  // 0.1.7: the locked offers once more - a listed item (in before an admin listed it, or past the slot filter) stops the countdown now
  String ba = @PKG@.TBlock.firstIn(xa);
  String bb = @PKG@.TBlock.firstIn(xb);
  if (ba != null || bb != null) {
    int w = ba != null ? 0 : 1;
    String id = ba != null ? ba : bb;
    s.stopCountdown(tok);
    // the record follows the cleared Ready marks (syncOffers' body: that method is compiled after this one)
    s.rec.setOffer(0, s.coins[0], s.ready[0]);
    s.rec.setOffer(1, s.coins[1], s.ready[1]);
    saveSoon(s.rec, (long) @PKG@.TCfg.SAVE_MS);
    String m = @PKG@.TBlock.stopped(s.name[w], id);
    sayBoth(s, m);
    log("BLOCKED-READY " + ids(s) + " " + s.name[w] + " offers " + id + " (no-trade list) - countdown not started");
    requestRefresh(s, 0);
    requestRefresh(s, 1);
    return m;
  }''')
rep('''  int r = s.toggleReady(me);
  if (r < 0) return "-This trade has ended.";
  syncOffers(s);''', '''  // 0.1.7: never Ready while either offer holds an item on the no-trade list (past the slot filter, or listed after it went in)
  if (!s.ready[me] && s.state == 0) {
    String mb = @PKG@.TBlock.firstIn(snapshot(s.box[me]));
    if (mb != null) return @PKG@.TBlock.takeOut(mb);
    String ob = @PKG@.TBlock.firstIn(snapshot(s.box[1 - me]));
    if (ob != null) return @PKG@.TBlock.theirs(s.name[1 - me], ob);
  }
  int r = s.toggleReady(me);
  if (r < 0) return "-This trade has ended.";
  syncOffers(s);''')

# ================================================================================================ TStore: the notice task (TTask 9)
rep('''M(tst, r"""
public static void taskRun(@PKG@.TTask t) {''', '''# 0.1.7: TTask 9 - a refused offer (TBlockF): the player's world thread. The window + inventory re-sent (resync), the chat line, the trade
# page's info line (its rebuild coalesced like every other refresh), trade.log BLOCKED-OFFER. Nothing moves here.
M(tst, r"""
public static void blockedTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  @PKG@.TBlockF f = null;
  if (t.obj instanceof @PKG@.TBlockF) f = (@PKG@.TBlockF) t.obj;
  if (f != null) {
    f.lastNotice = System.currentTimeMillis();      // review fix: this side's next notice waits TBlockF.NOTICE_MS from now (TBlockF.delay)
    f.queued.set(false);
  }
  String id = f == null ? null : f.last;
  @PKG@.TSession s = t.sess;
  if (s == null || !s.live() || t.side < 0 || t.side > 1) return;
  resync(s, t.side, ref, st);
  String m = @PKG@.TBlock.refused(id);
  tellPr(pr, m);
  log("BLOCKED-OFFER " + ids(s) + " " + s.name[t.side] + " tried to offer " + id + " (no-trade list: refused, nothing moved)");
  @PKG@.TradePage pg = s.page[t.side];
  if (pg != null) {
    pg.info = m;
    // review fix (finding 3): the line is a NOTE - TradePage.dropStaleNote drops it at a rebuild once the offers changed or after 10 s
    pg.note = m;
    pg.noteAt = System.currentTimeMillis();
    pg.noteSig = @PKG@.TradePage.offerSig(s);
    requestRefresh(s, t.side);
  }
}""")
M(tst, r"""
public static void taskRun(@PKG@.TTask t) {''')
rep('''    else if (k == 8) cfgResultTask(t, pr, ref, st, p);''', '''    else if (k == 8) cfgResultTask(t, pr, ref, st, p);
    else if (k == 9) blockedTask(t, pr, ref, st, p);''')

# ================================================================================================ review fix 3: the trade page's notice line
rep('''for f in ("public @PKG@.TSession sess;", "public int side;", "public int mode;", "public String info;", "public String keepCoin;",
          "public @PKG@.TWindow win;", "public volatile boolean dismissed;", "public volatile boolean replacing;", "public boolean cleared;"):
    F(tpage, f)''', '''for f in ("public @PKG@.TSession sess;", "public int side;", "public int mode;", "public String info;", "public String keepCoin;",
          "public @PKG@.TWindow win;", "public volatile boolean dismissed;", "public volatile boolean replacing;", "public boolean cleared;"):
    F(tpage, f)
# 0.1.7 review fix (finding 3): the no-trade notice line (TStore.blockedTask sets info AND note): when it was set and the offers it was
# set for. Written and read only on this player's world thread (the notice task and the page build).
for f in ("public String note;", "public long noteAt;", "public String noteSig;"):
    F(tpage, f)''')
rep('''M(tpage, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  this.cleared = false;''', '''# 0.1.7 review fix (finding 3): both offers (items + coins) as one text - the notice line goes away once it changes
M(tpage, r"""
public static String offerSig(@PKG@.TSession s) {
  if (s == null) return "";
  try {
    return @PKG@.TStore.sig(@PKG@.TStore.snapshot(s.box[0])) + "|" + @PKG@.TStore.sig(@PKG@.TStore.snapshot(s.box[1])) + "|" + s.coins[0] + "|" + s.coins[1];
  } catch (Throwable t) { return ""; }
}""")
# at every build: the notice line is dropped once a click replaced it, either offer changed, the trade ended, or it is older than 10 s
# (never on a timer - the next rebuild for any reason clears it; a click still replaces it as before)
M(tpage, r"""
public void dropStaleNote(long now) {
  String n = this.note;
  if (n == null) return;
  boolean shown = this.info != null && this.info.equals(n);
  boolean stale = !shown || now - this.noteAt > 10000L;
  if (!stale) {
    @PKG@.TSession s = this.sess;
    if (s == null || !s.live() || !offerSig(s).equals(this.noteSig)) stale = true;
  }
  if (!stale) return;
  if (shown) this.info = "";
  this.note = null;
  this.noteSig = null;
}""")
M(tpage, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  this.cleared = false;
  dropStaleNote(System.currentTimeMillis());''')

# ================================================================================================ review fix 2: when the audit runs
rep('''  // 0.1.6: gameplay.durability may have changed by hand - apply it now (idempotent; EssDurTick checks every second too)
  try { @PKG@.EssDur.sync(); } catch (Throwable t2) { }
}""")''', '''  // 0.1.6: gameplay.durability may have changed by hand - apply it now (idempotent; EssDurTick checks every second too)
  try { @PKG@.EssDur.sync(); } catch (Throwable t2) { }
  // 0.1.7 review fix: a hand-edited no-trade list is read against the items (WARN lines; once per list text; skipped before start())
  try { @PKG@.TBlock.audit("hand edit"); } catch (Throwable t3) { }
}""")''')
rep('''protected void start() {
  @ES@.claimR();
  // 0.1.6: every asset pack (mods included) is loaded now: apply the item durability switch + start its 1 s re-check
  try { @PKG@.EssDur.start(); } catch (Throwable t) { @ES@.warn("the item durability switch could not start: " + t); }
}""")''', '''protected void start() {
  @ES@.claimR();
  // 0.1.6: every asset pack (mods included) is loaded now: apply the item durability switch + start its 1 s re-check
  try { @PKG@.EssDur.start(); } catch (Throwable t) { @ES@.warn("the item durability switch could not start: " + t); }
  // 0.1.7 review fix: the no-trade list read against the loaded items - WARN lines for an empty list, missing Magic Bags / Accessory
  // Bag entries and entries that match no item (case typos)
  try { @PKG@.TBlock.auditStart(); } catch (Throwable t2) { }
}""")''')

# ================================================================================================ classes written, manifest
rep('''MINE = [rq, es, hop, mv, rd, fly, tick] + OLD_CMDS + TRADE_ALL + TCMDS + [eperm, EWARP, wpage] + DUR_ALL + [pl]''',
    '''MINE = [rq, es, hop, mv, rd, fly, tick] + OLD_CMDS + TRADE_ALL + TCMDS + [eperm, EWARP, wpage] + DUR_ALL + BLOCK_ALL + [pl]''')
rep('''an item durability switch (off by default: tools, weapons and armor never break), every setting in game''',
    '''an item durability switch (off by default: tools, weapons and armor never break), Magic Bags and the Accessory Bag never trade (no-trade list), every setting in game''')

# ================================================================================================ checks on the result
code = s[s.index('\nimport sys, os\n'):]              # everything after the docstring
code_nc = "\n".join(l for l in code.split("\n") if not l.lstrip().startswith("#"))
assert s.count('"0.1.6"') == 0, "a 0.1.6 version string is left"
assert s.count("registerCommand(") == REG0, "no command added or removed"
assert s.count("registerSystem(") == SYS0, "no system added or removed"
_rs = re.findall(r"registerSystem\(new ([\w@.]+)\(", code_nc)
assert len(_rs) == len(set(_rs)), "a class is registered twice: %s" % _rs
# javassist: every method before its first caller
_order = [
    "public static volatile String %s = %s;\" % (fld, jstr(dflt))",                  # the TCfg BLOCKED field exists ...
    "public static boolean idChars(String id) {\n  if (id == null || id.length() == 0 || id.length() > 120)",   # ... before TBlock
    "public static boolean itemOk(String id) {\n  if (id == null) return false;\n  if (@OWNX@) return true;",
    "public static String canonList(String raw, int max) {", "public static Object[] rules() {", "public static boolean blocked(String id) {",
    "public static String firstIn(@IS@[] a) {", "public static boolean bag(String id)", "public static String what(String id) {",
    "public static String why(String id) {", "public static String refused(String id) {", "public static String takeOut(String id)",
    "public static String theirs(String name, String id)", "public static String stopped(String name, String id)",
    "public static String swap(String name, String id)",
    # review fix 2 (TBlock): the helpers before audit / check, audit before its callers (auditStart, changed, TCfg.reloadKit, start())
    "public static String[] defs() {", "public static java.util.ArrayList entries(String src) {",
    "public static boolean covers(java.util.ArrayList es, String want) {", "public static boolean isDef(String e) {",
    "public static String whatAll(String e) {", "public static java.util.HashSet itemIds() {",
    "public static boolean anyStarts(java.util.Set ids, String b) {", "public static String clip(String s, int n) {",
    "public static String hintPre(java.util.Set ids, String b) {", "public static String hintId(java.util.Set ids, String e) {",
    "public static String hintDef(String e) {", "public static java.util.ArrayList auditLines(String src, java.util.Set ids) {",
    "public static java.util.ArrayList audit(String when) {", "public static java.util.ArrayList auditStart() {",
    "public static void changed(String key) { audit(", "public static String check(String key, String value) {\n  java.util.ArrayList now = entries(value);",
    "public static String canon(int i, String raw) {",                                  # TCfg.canon calls TBlock.canonList
    "public static void reloadKit() {",                                                 # TCfg.reloadKit calls TBlock.audit
    "kit = CFG.emit(",                                                                  # CfgRows.itemOk calls TBlock.itemOk
    "M(twin, \"public void resend() { invalidate(); }\")",
    "public TBlockF(@PKG@.TSession s, int side) {", "public static long delay(long last, long now) {",
    "public boolean test(@FAT@ a, @IC@ c, short slot, @IS@ st) {",
    # review fix 3 (TradePage): offerSig uses TStore.snapshot / sig; build calls dropStaleNote first
    "public static @IS@[] snapshot(@IC@ c) {", "public static String sig(@IS@[] a) {", "public static String offerSig(@PKG@.TSession s) {",
    "public void dropStaleNote(long now) {",
    "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {\n  this.cleared = false;\n  dropStaleNote(System.currentTimeMillis());",
    "public static void taskDone(@PKG@.TTask t) {", "public static void armBox(@PKG@.TSession s, int side) {",
    "public static @CTY@ invType(int i) {", "public static void resync(@PKG@.TSession s, int side, @REF@ ref, @ST@ st) {",
    "public static @PKG@.TSession newSession(@PR@ a, @PR@ b) {", "public static String[] cancelMsg(",
    "public static String[] blockedMsg(@PKG@.TSession s, int by, String id) {", "public static void finishCancel(",
    "public static void execute(@PKG@.TSession s, int tok) {", "public static String startCountdown(@PKG@.TSession s, int tok, int by) {",
    "public static String clickReady(@PKG@.TradePage page) {",
    "public static void blockedTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {", "public static void taskRun(@PKG@.TTask t) {",
]
_ix = [code.index(x) for x in _order]
assert _ix == sorted(_ix), "out of order: %s" % [x[:50] for x, i in zip(_order, _ix) if i != sorted(_ix)[_order.index(x)]]
assert code.index("tbf.addInterface(pool.get(BSFL))") < code.index("public TBlockF(@PKG@.TSession s, int side) {")
assert code.index("BSFL = ") < code.index("tbf.addInterface(pool.get(BSFL))")
# the rows: the loader row and the kit row agree (key, default, bounds), the default is the AH's list, label / help widths
assert ('("tradeBlockedItems", "Items that can\'t be traded", "items", "BLOCKED", 0, 200, "%s", "",' % DEFAULT_BLOCKED) in code
assert ('("tradeBlockedItems", "Items that can\'t be traded", "trade", "items", "%s", "0", "200", "prefix", "", "live",' % DEFAULT_BLOCKED) in code
assert '"field:TCfg.BLOCKED" + CF + "tradeBlockedItems;after=TBlock.changed;check=TBlock.check"' in code
assert len("Items that can't be traded") <= 40 and len(KIT_HELP) <= 100 and code.count('"%s"' % KIT_HELP) == 1
assert 'ITEMS=ESS_ITEMS, ITEM_FN="TBlock.itemOk")' in code
# the swap check runs before every coin step and the swap; the drained offers are the ones checked
_ex = code[code.index("public static void execute(@PKG@.TSession s, int tok) {"):]
_ex = _ex[:_ex.index('}""")')]
_bk = _ex.index("blk = @PKG@.TBlock.firstIn(ia);")
assert _ex.index("try { ia = drain(s.box[0]); }") < _bk < _ex.index("@ES@.online(ua) == null") < _ex.index("markPaying(") < _ex.index("takeFor(s, 0, ca)") \
    < _ex.index('s.rec.settle("COMPLETED"'), "the swap check must come after the drain and before the coins and the swap"
assert _ex.index("blk = @PKG@.TBlock.firstIn(ib);") > _bk and "cm = blockedMsg(s, by, blk);" in _ex and "finishCancel(s, ia, ib, why, cm, owA, owB);" in _ex
# Ready: refused before toggleReady; the countdown start: checked after setAgreed, stopped through stopCountdown
_cr = code[code.index("public static String clickReady(@PKG@.TradePage page) {"):]
_cr = _cr[:_cr.index('}""")')]
assert _cr.index("@PKG@.TBlock.firstIn(snapshot(s.box[me]))") < _cr.index("@PKG@.TBlock.firstIn(snapshot(s.box[1 - me]))") < _cr.index("int r = s.toggleReady(me);")
_sc = code[code.index("public static String startCountdown(@PKG@.TSession s, int tok, int by) {"):]
_sc = _sc[:_sc.index('}""")')]
assert _sc.index("s.setAgreed(tok, sa, sb)") < _sc.index("@PKG@.TBlock.firstIn(xa)") < _sc.index("s.stopCountdown(tok);") < _sc.index("sayBoth(s, m);")
# the filter: ADD only, no container call, no lock, no TSession method; refuses with false, passes with true, errors pass
_tf = code[code.index("public boolean test(@FAT@ a, @IC@ c, short slot, @IS@ st) {"):]
_tf = _tf[:_tf.index('}""")')]
assert "a != @FAT@.ADD" in _tf and "synchronized" not in _tf and "s.box" not in _tf and "c." not in _tf.replace("catch", "")
for _bad in ("ItemStack(", "setItemStack", "addItemStack", "removeItemStack", "moveItemStack", ".clear(", "toggleReady", "onChange(", "setCoins("):
    assert _bad not in _tf, "the slot filter must not " + _bad
assert _tf.count("return false;") == 1 and "catch (Throwable x) { return true; }" in _tf and "catch (Throwable e) { this.queued.set(false); }" in _tf
# the refusal does not depend on the notice: the decision's try ends before the notice's try starts, and "return false" comes after both
assert _tf.index("if (!@PKG@.TBlock.blocked(id)) return true;") < _tf.index("catch (Throwable x) { return true; }") < _tf.index("this.last = id;") \
    < _tf.index("catch (Throwable e) { this.queued.set(false); }") < _tf.index("return false;")
# newSession arms both boxes right after they are made (before the change listeners and before claim() makes the trade visible)
_ns = code[code.index("public static @PKG@.TSession newSession(@PR@ a, @PR@ b) {"):]
_ns = _ns[:_ns.index('}""")')]
assert _ns.index("s.box[i].setGlobalFilter(@FT@.ALLOW_ALL);") < _ns.index("armBox(s, i);") < _ns.index("if (!claim(s)) return null;") \
    < _ns.index("registerChangeEvent(")
assert "b.setSlotFilter(@FAT@.ADD, (short) k, f);" in code
# deliveries are untouched (never blocked): the delivery task has no TBlock call
_dt = code[code.index("public static void deliverTask(@PKG@.TTask t,"):]
_dt = _dt[:_dt.index('}""")')]
assert "TBlock" not in _dt
assert "B.deploy(" not in code and "enable_in_world(" not in code
for ident in re.findall(r"#(Skyy[A-Za-z0-9_]*)", code):
    assert "_" not in ident, "UI id with an underscore: " + ident
for _t in ("A Magic Bag", "Magic Bags and the Accessory Bag open their owner's own storage"):
    assert all(32 <= ord(_c) < 127 for _c in _t)
# ---- review fixes
def _body(sig_):
    b_ = code[code.index(sig_):]
    return b_[:b_.index('}""")')]
# R1: the filter schedules its notice through delay(lastNotice, now) (no fixed 150 ms any more); the notice task stamps lastNotice
# BEFORE it clears queued (a refusal that sees queued == false also sees the new stamp)
assert "schedule(t, delay(this.lastNotice, System.currentTimeMillis()), java.util.concurrent.TimeUnit.MILLISECONDS);" in _tf and "150L" not in _tf
_dl = _body("public static long delay(long last, long now) {")
assert "if (w < 150L) w = 150L;" in _dl and "if (w > NOTICE_MS) w = NOTICE_MS;" in _dl and '"public static final long NOTICE_MS = 1500L;"' in code
_btk = _body("public static void blockedTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {")
assert _btk.index("f.lastNotice = System.currentTimeMillis();") < _btk.index("f.queued.set(false);") < _btk.index("resync(s, t.side, ref, st);")
# R3: the notice line is a note (text + time + the offers it was shown for); build drops a stale one before anything else
assert _btk.index("pg.info = m;") < _btk.index("pg.note = m;") < _btk.index("pg.noteSig = @PKG@.TradePage.offerSig(s);") < _btk.index("requestRefresh(s, t.side);")
_dn = _body("public void dropStaleNote(long now) {")
assert "now - this.noteAt > 10000L" in _dn and "!offerSig(s).equals(this.noteSig)" in _dn and "!s.live()" in _dn and "if (shown) this.info = \"\";" in _dn
# R2: the audit is skipped before start(), once per text, and only reads (no file write, no container); start() runs it after the
# durability switch; a hand edit (reloadKit) and an in-game change (kit after=) run it; check= only ever asks (a "?" answer) or passes
_au = _body("public static java.util.ArrayList audit(String when) {")
assert _au.index("if (!READY) return null;") < _au.index("if (src.equals(AUDITED)) return null;") < _au.index("AUDITED = src;") < _au.index("auditLines(src, itemIds())")
for _bad in ("atomicWrite", "Files.", "setItemStack", "TStore", "TSession", "synchronized"):
    assert _bad not in _au and _bad not in _body("public static java.util.ArrayList auditLines(String src, java.util.Set ids) {"), "the audit must not " + _bad
_st = _body("protected void start() {")
assert _st.index("@PKG@.EssDur.start();") < _st.index("try { @PKG@.TBlock.auditStart(); } catch (Throwable t2) { }")
assert 'try { @PKG@.TBlock.audit("hand edit"); } catch (Throwable t3) { }' in _body("public static void reloadKit() {")
_ck = _body("public static String check(String key, String value) {\n  java.util.ArrayList now = entries(value);")    # (EssDur.check comes first)
assert _ck.count("return ") == 2 and "if (le.length() == 0 && miss == null) return null;" in _ck and 'return "?" + q + " Save anyway?";' in _ck
# the default entries in defs() / the audit texts come from the loader row's default (filled in by the build script, never typed twice)
assert code.count('.replace("@DEFS@", ", ".join(\'"%s"\' % _x for _x in ROWS[IDX["tradeBlockedItems"]][6].split(",")))') == 1
assert code.count('.replace("@DEFT@", ROWS[IDX["tradeBlockedItems"]][6])') == 1
for _t in ("Save anyway?", "the no-trade list is EMPTY - Magic Bags and the Accessory Bag CAN be traded", "can be traded again."):
    assert all(32 <= ord(_c) < 127 for _c in _t) and _t in code

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == CR + LF else "LF"))
