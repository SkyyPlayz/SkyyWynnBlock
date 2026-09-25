"""SkyyAuctions 0.1 - build script (javassist via jpype). A Hypixel-style Auction House for SkyWynn, BUY IT NOW listings only.
Run:   python build_skyyauctions_0.1.py            -> SkyyAuctions/SkyyAuctions-0.1.jar   (build only; deploys go through tools/deploy_set.py)
Spec:  research/Auction-House-Spec.md (the spec wins over this docstring). Research: research/Auction-House-Research.md.

WHAT 0.1 DOES
 - /ah (aliases /auction, /auctionhouse) opens ONE inline page (1120 x 880, fits a 1080-high screen) with four views switched by rebuild():
     Browse  - 7 categories (All, Weapons, Armor, Accessories, Consumables, Blocks, Tools & Misc), a search TextField, 4 sorts, a rarity
               filter (the engine's own quality tiers 1..5), 8 rows per page, pager, time left worked out when the page is built.
     Item    - a 1-slot ItemGrid with the REAL restored stack (InfoDisplay: None, so no hover tooltip can stick after Esc), the item's own
               name + description as TextSpans (rolls included), 8 facts + a cheaper-listing / bag line, Buy with a confirm step at or
               above confirmAbove, Cancel for your own listing, grace countdown.
     Create  - our own inventory picker (hotbar, storage, backpack; 36 cells per page), price TextField (#SkyyAhPrice, Enter or Preview),
               duration buttons, a live fee preview; Create BIN only lists when the typed price equals the previewed price.
     Manage  - claims first, then active listings; Cancel (confirm), Claim coins, Claim item, Claim all (confirm at claimAllConfirmAbove),
               the other profiles' claims line.
   /ah sell <price> [<duration>] (usage variant), /ah claim, /ah manage (alias mine), /ah search <words>.
   /ahadmin [list [<player>] | info <id> | remove <id> [<reason...>] | reload | pause | resume | regrant <id> <seller|buyer> [confirm]].
   Every player command / subcommand / variant: setPermissionGroups(hytale:Adventurer). Every admin form: requirePermission
   ("skyyauctions.admin").
 - Data <world>/mods/Skyy_SkyyAuctions/: config.properties (commented template), state.properties (nextId, written BEFORE an id is
   used), listings/<id>.json (one record per open listing, BSON Extended JSON, atomic tmp + fsync + ATOMIC_MOVE writes),
   archive/<yyyy-MM>/<id>.json (closed records, never overwritten), listings/bad/ (unreadable files, never deleted), auctions.log
   (every append fsynced; BOOT / STOP lines; rotated at 5 MB). Shared block list <world>/mods/Skyy_Market/blocked.txt (empty by default).
 - Items: the listed stack is snapshotted with ItemStack.CODEC plus readable fields (SkyyProfiles ProfInv shape) and restored exactly;
   a listing is refused unless the snapshot survives an in-memory AND a JSON round trip (id, quantity, metadata, durability, quality),
   so SkyyRolls metadata always survives. Deliveries never build a plain new ItemStack.
 - Money: listing fee tiers + duration fee on Create (never refunded by cancel), 1% claim tax above 1,000,000 fixed at sale time,
   coins only through the SkyyCoins bridge (coins:fn:get / take / add), claimed into the profile that owns them.
 - Safety (spec section 6): one JVM-wide lock (synchronized (AhStore.class), one call per block), copy-write-swap records, START lines
   synced before the first durable effect, count-before-and-after for every item move, profile:busy refusal, the page key check,
   a forced player save queued after the lock when the inventory changed. A write that fails after an item or coin moved keeps the
   new version in memory (DIRTY; a closed one also in ARCH until its closed version is on disk) and a copy on its WRITE-FAILED /
   PAY-FAILED log line; setup() writes that copy back when the loaded file is older (restoreFromLog, spec 6.10).
 - Bridge: auction:fn:lowestBin, auction:count, auction:claims:<uuid>, auction:version; shared market:blocked (own "file" entries only),
   reads market:veto, market:deny:<uuid>, bazaar:products (whole-id match), profile:* keys, bank:<uuid>.

DEVIATIONS FROM THE SPEC (each is noted where it happens in the code)
 - Forced save (R8) uses Store.copyEntity(ref), not copySerializableEntity(ref): Player.saveConfig reads MovementStatesComponent from the
   holder (bytecode), and that component has no codec, so a serializable-only copy would make the save throw. It also skips worlds
   that do not save players (WorldConfig.isSavingPlayers / World.isSavingLocked, the engine tick's own guard).
 - A coin claim whose coins:fn:add THREW (-1, outcome unknown) keeps the claim CLAIMED and logs PAY-ERROR for an admin (regrant after a
   purse check) instead of rolling back: a roll back after a pay that did land would create coins (spec section 0 / R4). A refused
   add (0) rolls back as the spec says.
 - /ahadmin remove <id> <reason...> and /ah search <words>: the text is also read from the command's input string, because a usage
   variant is chosen by the raw token count (AbstractCommand.checkForExecutingSubcommands) and a reason with spaces would miss it.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = "com.skyy.auctions"

T = {
    "JP":    "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":   "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":    "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":   "com.hypixel.hytale.component.Ref",
    "ST":    "com.hypixel.hytale.component.Store",
    "HOLDER": "com.hypixel.hytale.component.Holder",
    "WLD":   "com.hypixel.hytale.server.core.universe.world.World",
    "ES":    "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC":   "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":   "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ACM":   "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "MSG":   "com.hypixel.hytale.server.core.Message",
    "HSV":   "com.hypixel.hytale.server.core.HytaleServer",
    "ATY":   "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":    "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG":   "com.hypixel.hytale.logger.HytaleLogger",
    "PAGE":  "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PGM":   "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "LIFE":  "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "PGE":   "com.hypixel.hytale.protocol.packets.interface_.Page",
    "UCB":   "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":   "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":   "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":    "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "IGS":   "com.hypixel.hytale.server.core.ui.ItemGridSlot",
    "PLA":   "com.hypixel.hytale.server.core.entity.entities.Player",
    "INV":   "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC":    "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "SIC":   "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "IS":    "com.hypixel.hytale.server.core.inventory.ItemStack",
    "ITM":   "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "IQ":    "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality",
    "CODEC": "com.hypixel.hytale.codec.Codec",
    "PCOL":  "com.hypixel.hytale.protocol.Color",
    "I18N":  "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
    "GM":    "com.hypixel.hytale.protocol.GameMode",
    "OCU":   "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction",
    "PLB":   "com.hypixel.hytale.server.core.plugin.PluginBase",
    "UNI":   "com.hypixel.hytale.server.core.universe.Universe",
    "PRE":   "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE":   "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "BD":    "org.bson.BsonDocument",
    "BV":    "org.bson.BsonValue",
    "PKG":   PKG,
    "RES":   PKG + ".AhResult",
    "VERSION": VERSION,
    "ADV":   'setPermissionGroups(new String[] { "hytale:Adventurer" });',
    "ADMIN": 'requirePermission("skyyauctions.admin");',
}


def jv(src):
    """Java source with @TOKEN@ placeholders (raw strings: no brace doubling, \\" stays a Java escape)."""
    out = src
    for k, v in T.items():
        out = out.replace("@" + k + "@", v)
    left = re.findall(r"@[A-Z][A-Z0-9]*@", out)
    assert not left, "unreplaced tokens: %s" % left
    return out


def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


# ================= javassist =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

for c, m in ((T["PLA"], "getInventory"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["PLA"], "getGameMode"),
             (T["PLA"], "markNeedsSave"), (T["GM"], "Creative"),
             (T["PGM"], "openCustomPage"), (T["PGM"], "setPage"), (T["PGE"], "None"),
             (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"), (T["INV"], "getActiveHotbarSlot"),
             (T["INV"], "getCombinedStorageHotbarBackpack"),
             (T["IC"], "getItemStack"), (T["IC"], "removeItemStackFromSlot"), (T["IC"], "addItemStack"), (T["IC"], "addItemStackToSlot"),
             (T["IC"], "getCapacity"), (T["SIC"], "addOrDropItemStack"),
             (T["IS"], "CODEC"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"), (T["IS"], "getMetadata"),
             (T["IS"], "getDisplayName"), (T["IS"], "getDisplayDescription"), (T["IS"], "withQuantity"), (T["IS"], "isStackableWith"),
             (T["IS"], "getQualityIndex"), (T["IS"], "getDurability"), (T["IS"], "getMaxDurability"), (T["IS"], "getItem"),
             (T["CODEC"], "encode"), (T["CODEC"], "decode"),
             (T["ITM"], "getWeapon"), (T["ITM"], "getArmor"), (T["ITM"], "getTool"), (T["ITM"], "getGlider"), (T["ITM"], "getUtility"),
             (T["ITM"], "isConsumable"), (T["ITM"], "hasBlockType"), (T["ITM"], "getMaxStack"), (T["ITM"], "getTranslationKey"),
             (T["IQ"], "getAssetMap"), (T["IQ"], "getQualityValue"), (T["IQ"], "getTextColor"),
             (T["IGS"], "setName"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"),
             (T["EVD"], "of"), (T["EVD"], "append"), (T["BT"], "Activating"), (T["BT"], "Validating"), (T["LIFE"], "CanDismiss"),
             (T["PAGE"], "rebuild"), (T["PAGE"], "build"), (T["PAGE"], "handleDataEvent"),
             (T["PR"], "getUuid"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"), (T["PR"], "isValid"),
             (T["UNI"], "getPlayer"), (T["UNI"], "getPlayers"), (T["I18N"], "getMessage"),
             (T["MSG"], "raw"), (T["MSG"], "getRawText"), (T["MSG"], "getMessageId"), (T["MSG"], "getChildren"),
             ("org.bson.BsonDocument", "parse"), ("org.bson.BsonDocument", "toJson"), ("org.bson.json.JsonWriterSettings", "builder"),
             ("org.bson.json.JsonMode", "EXTENDED"),
             (T["HSV"], "SCHEDULED_EXECUTOR"), (T["OCU"], "registerSimple"),
             (T["ACM"], "setPermissionGroups"), (T["ACM"], "requirePermission"), (T["ACM"], "addUsageVariant"), (T["ACM"], "addSubCommand"),
             (T["ACM"], "addAliases"), (T["ACM"], "withRequiredArg"), (T["ACM"], "setAllowsExtraArguments"),
             (T["ATY"], "GREEDY_STRING"), (T["ATY"], "STRING"), (T["CTX"], "get"), (T["CTX"], "getInputString"),
             (T["PLB"], "shutdown"), (T["PLB"], "getDataDirectory"), (T["PLB"], "getCommandRegistry"), (T["PLB"], "getEventRegistry"),
             (T["PLB"], "getLogger"), ("com.hypixel.hytale.event.EventRegistry", "registerGlobal")):
    B.probe(pool, c, m)
# ItemGridSlot(ItemStack) and UICommandBuilder.set(String, Message) (TextSpans): signature probes
_igs = pool.get(T["IGS"])
assert any(str(k.getSignature()) == "(L%s;)V" % T["IS"].replace(".", "/") for k in _igs.getDeclaredConstructors()), "ItemGridSlot(ItemStack) missing"
assert any(str(m.getName()) == "set" and str(m.getSignature()).startswith("(Ljava/lang/String;L%s;)" % T["MSG"].replace(".", "/"))
           for m in pool.get(T["UCB"]).getDeclaredMethods()), "UICommandBuilder.set(String, Message) missing"


# R8 soft probes: Player.saveConfig(World, Holder, boolean), Store.copyEntity(Ref), World.isSavingLocked, WorldConfig.isSavingPlayers.
# Missing -> the forced save compiles as a no-op (markNeedsSave only) with a warning instead of failing the build.
def _has(cls, name, sig_prefix=None):
    try:
        for mm in pool.get(cls).getMethods():
            if str(mm.getName()) == name and (sig_prefix is None or str(mm.getSignature()).startswith(sig_prefix)):
                return True
    except Exception:
        return False
    return False


SAVE_OK = (_has(T["PLA"], "saveConfig", "(L%s;L%s;Z)" % (T["WLD"].replace(".", "/"), T["HOLDER"].replace(".", "/")))
           and _has(T["ST"], "copyEntity", "(L%s;)" % T["REF"].replace(".", "/"))
           and _has(T["WLD"], "isSavingLocked") and _has(T["WLD"], "getWorldConfig")
           and _has("com.hypixel.hytale.server.core.universe.world.WorldConfig", "isSavingPlayers"))
if not SAVE_OK:
    print("WARNING: forced player save probes failed - R8 compiles as markNeedsSave only")

utl  = pool.makeClass(PKG + ".AhUtil")
cfg  = pool.makeClass(PKG + ".AhCfg")
lg   = pool.makeClass(PKG + ".AhLog")
coin = pool.makeClass(PKG + ".Coins")
rec  = pool.makeClass(PKG + ".AhRec")
itm  = pool.makeClass(PKG + ".AhItem")
res  = pool.makeClass(PKG + ".AhResult")
srt  = pool.makeClass(PKG + ".AhSort")
sto  = pool.makeClass(PKG + ".AhStore")
lfn  = pool.makeClass(PKG + ".AhLowestBinFn")
page = pool.makeClass(PKG + ".AhPage", pool.get(T["PAGE"]))
fac  = pool.makeClass(PKG + ".AhPageFactory")
cmds = pool.makeClass(PKG + ".AhCmds")
tick = pool.makeClass(PKG + ".AhTick")
note = pool.makeClass(PKG + ".AhNoticeTask")
rdy  = pool.makeClass(PKG + ".AhReady")
quit_ = pool.makeClass(PKG + ".AhQuit")
pl   = pool.makeClass(PKG + ".SkyyAuctionsPlugin", pool.get(T["JP"]))


def F(cls, src): cls.addField(CtField.make(jv(src), cls))
def M(cls, src): cls.addMethod(CtNewMethod.make(jv(src), cls))
def C(cls, src): cls.addConstructor(CtNewConstructor.make(jv(src), cls))


# ================= AhUtil: logger, bridge, pkey, parsing, formatting, text =================
F(utl, "public static @LOG@ LOG;")
M(utl, r"""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyAuctions] " + m); } catch (Throwable t) { }
}""")
M(utl, r"""
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyAuctions] " + m); } catch (Throwable t) { }
}""")
M(utl, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
M(utl, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) { return bridge0(); }
}""")
# PROFILES-CONTRACT helper (javassist-safe copy)
M(utl, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(utl, r"""
public static boolean busy(java.util.UUID u) {
  if (u == null) return false;
  try { return bridge().get("profile:busy:" + u) != null; } catch (Throwable t) { return false; }
}""")
M(utl, r"""
public static String deny(java.util.UUID u) {
  if (u == null) return null;
  try {
    Object o = bridge().get("market:deny:" + u);
    if (o == null) return null;
    String s = String.valueOf(o).trim();
    return s.length() == 0 ? "your profile cannot use the Auction House" : s;
  } catch (Throwable t) { return null; }
}""")
M(utl, r"""
public static String profName(java.util.UUID u) {
  try { Object o = bridge().get("profile:name:" + u); if (o instanceof String) return (String) o; } catch (Throwable t) { }
  return "";
}""")
# the CURRENT name of one profile (storage key) of a player, from SkyyProfiles' profile:list:<uuid> = "1:Apple:Archer,2:Banana:Mage"
# (id 1 = key uuid, id N = uuid-pN; SkyyProfiles strips ':' and ',' from names). null = unknown (no SkyyProfiles, or not listed).
M(utl, r"""
public static String profListName(java.util.UUID u, String key) {
  if (u == null || key == null) return null;
  try {
    Object o = bridge().get("profile:list:" + u);
    if (!(o instanceof String)) return null;
    String us = u.toString();
    String[] parts = ((String) o).split(",");
    for (int i = 0; i < parts.length; i++) {
      String x = parts[i].trim();
      int a = x.indexOf(':');
      if (a <= 0) continue;
      String pid = x.substring(0, a).trim();
      String k = pid.equals("1") ? us : us + "-p" + pid;
      if (!k.equals(key)) continue;
      String rest = x.substring(a + 1);
      int b = rest.lastIndexOf(':');
      String nm = (b >= 0 ? rest.substring(0, b) : rest).trim();
      return nm.length() > 0 ? nm : null;
    }
  } catch (Throwable t) { }
  return null;
}""")
# one string value out of the page event JSON (SkyySacks CraftPage / SkyyBazaar 0.1.2 jsonStr); quote = char 34, backslash = char 92
M(utl, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(utl, r"""
public static boolean isId(String t) {
  if (t == null || t.length() == 0 || t.length() > 96) return false;
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return false;
  }
  return true;
}""")
# a log token: no spaces, never empty
M(utl, r"""
public static String tok(String s) {
  if (s == null || s.length() == 0) return "-";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && i < 80; i++) {
    char c = s.charAt(i);
    if (Character.isWhitespace(c) || c == '#') sb.append('_'); else sb.append(c);
  }
  return sb.toString();
}""")
# price text -> whole coins. -1 = not a price. 500, 2k, 1.5m, 2b; commas, spaces, underscores ignored; a fraction needs a suffix
M(utl, r"""
public static long parsePrice(String raw) {
  if (raw == null) return -1L;
  String t = raw.trim().toLowerCase();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (c != ' ' && c != ',' && c != '_') sb.append(c);
  }
  String s = sb.toString();
  if (s.length() == 0) return -1L;
  double mul = 1.0;
  char last = s.charAt(s.length() - 1);
  if (last == 'k') { mul = 1000.0; s = s.substring(0, s.length() - 1); }
  else if (last == 'm') { mul = 1000000.0; s = s.substring(0, s.length() - 1); }
  else if (last == 'b') { mul = 1000000000.0; s = s.substring(0, s.length() - 1); }
  if (s.length() == 0 || s.length() > 15) return -1L;
  int dots = 0;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == '.') { dots++; continue; }
    if (c < '0' || c > '9') return -1L;
  }
  if (dots > 1 || s.equals(".")) return -1L;
  if (dots == 1 && mul == 1.0) return -1L;
  double v;
  try { v = Double.parseDouble(s) * mul; } catch (Throwable x) { return -1L; }
  if (!(v >= 0.0) || v > 1.0E15) return -1L;
  double r = Math.floor(v + 1.0E-9);
  if (Math.abs(v - r) > 1.0E-6) return -1L;
  return (long) r;
}""")
# duration text -> millis. 24 (= hours), 24h, 30m, 2d. -1 = not a duration
M(utl, r"""
public static long parseDurMs(String raw) {
  if (raw == null) return -1L;
  String s = raw.trim().toLowerCase();
  if (s.length() == 0 || s.length() > 8) return -1L;
  long mul = 3600000L;
  char last = s.charAt(s.length() - 1);
  if (last == 'h') s = s.substring(0, s.length() - 1);
  else if (last == 'm') { mul = 60000L; s = s.substring(0, s.length() - 1); }
  else if (last == 'd') { mul = 86400000L; s = s.substring(0, s.length() - 1); }
  if (s.length() == 0 || s.length() > 6) return -1L;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c < '0' || c > '9') return -1L;
  }
  long n = Long.parseLong(s);
  if (n <= 0L) return -1L;
  return n * mul;
}""")
M(utl, r"""
public static String durLabel(long ms) {
  if (ms % 86400000L == 0L) return (ms / 86400000L) + "d";
  if (ms % 3600000L == 0L) return (ms / 3600000L) + "h";
  return (ms / 60000L) + "m";
}""")
M(utl, r"""
public static String fmt(long v) {
  boolean neg = v < 0L;
  String s = String.valueOf(neg ? -v : v);
  StringBuilder sb = new StringBuilder();
  int n = s.length();
  for (int i = 0; i < n; i++) {
    if (i > 0 && (n - i) % 3 == 0) sb.append(',');
    sb.append(s.charAt(i));
  }
  return (neg ? "-" : "") + sb.toString();
}""")
M(utl, r"""
public static long ceilDiv(long a, long b) {
  if (b <= 0L) return a;
  if (a <= 0L) return 0L;
  return (a + b - 1L) / b;
}""")
M(utl, r"""
public static String timeLeft(long ms) {
  if (ms <= 0L) return "ended";
  long s = (ms + 999L) / 1000L;
  if (s < 60L) return s + "s";
  long m = s / 60L;
  if (m < 60L) return m + "m " + (s % 60L) + "s";
  long h = m / 60L;
  if (h < 24L) return h + "h " + (m % 60L) + "m";
  long d = h / 24L;
  return d + "d " + (h % 24L) + "h";
}""")
M(utl, r"""
public static String ago(long ms) {
  if (ms < 60000L) return "just now";
  long m = ms / 60000L;
  if (m < 60L) return m + "m ago";
  long h = m / 60L;
  if (h < 48L) return h + "h ago";
  return (h / 24L) + "d ago";
}""")
# en-US text of a translation key, null when missing (SkyyRolls tr)
M(utl, r"""
public static String tr(String key) {
  if (key == null) return null;
  try {
    @I18N@ m = @I18N@.get();
    if (m == null) return null;
    String s = m.getMessage("en-US", key);
    if (s == null || s.trim().length() == 0 || s.equals(key)) return null;
    return s;
  } catch (Throwable t) { return null; }
}""")
# plain text of a Message tree (raw text, else the en-US translation), children in order; iterative (javassist: no self-recursion)
M(utl, r"""
public static String plain(@MSG@ m) {
  if (m == null) return "";
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList stack = new java.util.ArrayList();
  stack.add(m);
  int guard = 0;
  while (!stack.isEmpty() && guard < 400) {
    guard++;
    @MSG@ x = (@MSG@) stack.remove(stack.size() - 1);
    if (x == null) continue;
    String r = null;
    try { r = x.getRawText(); } catch (Throwable t) { r = null; }
    if (r != null) sb.append(r);
    else {
      String id = null;
      try { id = x.getMessageId(); } catch (Throwable t) { id = null; }
      if (id != null) { String tt = tr(id); if (tt != null) sb.append(tt); }
    }
    java.util.List ch = null;
    try { ch = x.getChildren(); } catch (Throwable t) { ch = null; }
    if (ch != null) for (int i = ch.size() - 1; i >= 0; i--) stack.add(ch.get(i));
  }
  return sb.toString();
}""")
M(utl, r"""
public static String hex(@PCOL@ c) {
  if (c == null) return null;
  return "#" + Integer.toHexString(256 | (c.red & 255)).substring(1) + Integer.toHexString(256 | (c.green & 255)).substring(1)
    + Integer.toHexString(256 | (c.blue & 255)).substring(1);
}""")
# the words after <word> in a command input string (skip = tokens to drop right after it); "" when absent
M(utl, r"""
public static String rest(String input, String word, int skip) {
  if (input == null || word == null) return "";
  String[] t = input.trim().split("\\s+");
  int at = -1;
  for (int i = 0; i < t.length; i++) { if (t[i].equalsIgnoreCase(word) || t[i].equalsIgnoreCase("/" + word)) { at = i; break; } }
  if (at < 0) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = at + 1 + skip; i < t.length; i++) { if (sb.length() > 0) sb.append(' '); sb.append(t[i]); }
  return sb.toString();
}""")

# ================= AhCfg: config.properties, atomic writes, fee / duration tables, the shared block list =================
CFG_LINES = [
    "# SkyyAuctions config - edit, then /ahadmin reload (or restart). A bad value falls back to its default with a warning in the log.",
    "# listingFee = fee tiers fromPrice:percent (the highest tier at or below the price is used). Paid on Create, never refunded by a cancel.",
    "listingFee=0:1.0,10000000:2.0,100000000:2.5",
    "# durations = up to 8 presets length:fee (m, h or d; a bare number means hours; 14 days at most). The fee is added to the listing fee.",
    "durations=1h:20,6h:45,12h:100,24h:350,48h:1200",
    "# minDurationFee = a preset whose fee is below this is a TEST preset (like 2m:0). It is dropped unless allowTestDurations=true,",
    "# and while test presets are on every start, reload and /ahadmin status says so.",
    "minDurationFee=1",
    "allowTestDurations=false",
    "# defaultDuration = the preset picked when the Create page opens (must be one of the durations; falls back to 24h)",
    "defaultDuration=24h",
    "# claimTaxPercent / claimTaxFrom = tax on a sale above claimTaxFrom coins, fixed when it sells; the seller always keeps claimTaxFrom",
    "claimTaxPercent=1.0",
    "claimTaxFrom=1000000",
    "# minPrice / maxPrice = whole coins for the whole stack",
    "minPrice=1",
    "maxPrice=50000000000",
    "# maxListings = listing slots per PROFILE (a slot frees when that listing's coins or item are claimed)",
    "# maxListingsServer = open records server-wide (keeps loading and page filtering fast)",
    "maxListings=14",
    "maxListingsServer=5000",
    "# graceSeconds = nobody can buy a new listing for this long (the seller can still cancel a mistyped price)",
    "graceSeconds=20",
    "# confirmAbove / confirmSeconds = a buy at or above this price needs a Confirm click within confirmSeconds",
    "confirmAbove=10000",
    "confirmSeconds=10",
    "# claimAllConfirmAbove = Claim all asks first when this many coins or more are owed (purse coins can be lost on death). 0 = never ask",
    "claimAllConfirmAbove=100000",
    "# cancelRefundsFee / adminRemoveRefundsFee = give the listing fee back on a cancel / an admin removal (Hypixel keeps it)",
    "cancelRefundsFee=false",
    "adminRemoveRefundsFee=false",
    "# sameAccountBuy = true lets another profile of the SAME account buy a listing. SOLO TESTING ONLY: it moves coins between profiles.",
    "sameAccountBuy=false",
    "# blockCreative = Creative mode players can browse and claim, but not list or buy",
    "blockCreative=true",
    "# paused = no new listings or buys (cancel and claims still work). /ahadmin pause and /ahadmin resume change it.",
    "paused=false",
    "# bazaarItemsAllowed = false: items the Bazaar sells (bridge bazaar:products) cannot be listed here (Hypixel keeps them apart)",
    "bazaarItemsAllowed=false",
    "# sellCommandOpensPage = true: /ah sell <price> opens the Create page ready for one click. false: it lists straight from chat.",
    "sellCommandOpensPage=true",
    "# detailTextSpans = true: the item view shows the item's own coloured tooltip text. false: plain text (use it if that view looks broken).",
    "detailTextSpans=true",
    "# forceSaveAfterTrade = true: queue a save of the player right after a trade moved items (shortens the crash window)",
    "forceSaveAfterTrade=true",
]
BLOCK_LINES = [
    "# Skyy_Market/blocked.txt - items that are OFF THE MARKET. Shared by the Skyy market mods (Auction House now, the Bazaar later).",
    "# One entry per line:  ItemId   or   Prefix*   optionally followed by   = reason shown to players",
    "# Examples (remove the # to use them):",
    "#   Ore_Mithril = reach Mithril tier VI",
    "#   Skyy_Sack_* = a bag only opens its owner's own storage",
    "#   Skyy_Accessory_Bag = a bag only opens its owner's own storage",
    "# Matching is exact and case-sensitive; a lone * is ignored (use /ahadmin pause to close the market). After editing: /ahadmin reload",
]
for _l in CFG_LINES + BLOCK_LINES:
    assert '"' not in _l and "\\" not in _l, _l

F(cfg, "public static java.nio.file.Path DIR;")
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static java.nio.file.Path BLOCKED;")
F(cfg, "public static final String TEMPLATE = %s;" % jstr("\n".join(CFG_LINES) + "\n"))
F(cfg, "public static final String BLOCK_TEMPLATE = %s;" % jstr("\n".join(BLOCK_LINES) + "\n"))
# every tunable is volatile (read on world threads and the tick, written by /ahadmin reload); a reload runs inside the AhStore lock
# (AhStore.reloadCfg), so a trade never sees half of a new duration or fee table
F(cfg, "public static volatile long[] FEE_FROM = new long[] { 0L, 10000000L, 100000000L };")
F(cfg, "public static volatile double[] FEE_PCT = new double[] { 1.0, 2.0, 2.5 };")
F(cfg, "public static volatile String FEE_TEXT = \"0:1.0,10000000:2.0,100000000:2.5\";")
F(cfg, "public static volatile String[] DUR_LABEL = new String[] { \"1h\", \"6h\", \"12h\", \"24h\", \"48h\" };")
F(cfg, "public static volatile long[] DUR_MS = new long[] { 3600000L, 21600000L, 43200000L, 86400000L, 172800000L };")
F(cfg, "public static volatile long[] DUR_FEE = new long[] { 20L, 45L, 100L, 350L, 1200L };")
F(cfg, "public static volatile int DEF_DUR = 3;")
F(cfg, "public static volatile String TEST_ON = \"\";")
F(cfg, "public static volatile long MIN_DUR_FEE = 1L;")
F(cfg, "public static volatile boolean ALLOW_TEST = false;")
F(cfg, "public static volatile double TAX_PCT = 1.0;")
F(cfg, "public static volatile long TAX_FROM = 1000000L;")
F(cfg, "public static volatile long MIN_PRICE = 1L;")
F(cfg, "public static volatile long MAX_PRICE = 50000000000L;")
F(cfg, "public static volatile int MAX_LISTINGS = 14;")
F(cfg, "public static volatile int MAX_SERVER = 5000;")
F(cfg, "public static volatile long GRACE_MS = 20000L;")
F(cfg, "public static volatile long CONFIRM_ABOVE = 10000L;")
F(cfg, "public static volatile long CONFIRM_MS = 10000L;")
F(cfg, "public static volatile long CLAIMALL_ABOVE = 100000L;")
F(cfg, "public static volatile boolean CANCEL_REFUND = false;")
F(cfg, "public static volatile boolean ADMIN_REFUND = false;")
F(cfg, "public static volatile boolean SAME_ACCOUNT = false;")
F(cfg, "public static volatile boolean BLOCK_CREATIVE = true;")
F(cfg, "public static volatile boolean PAUSED = false;")
F(cfg, "public static volatile boolean BAZAAR_OK = false;")
F(cfg, "public static volatile boolean SELL_PAGE = true;")
F(cfg, "public static volatile boolean SPANS = true;")
F(cfg, "public static volatile boolean FORCE_SAVE = true;")
F(cfg, "public static volatile boolean WARNED_STAR = false;")
# tmp file + fsync + atomic rename, 5 x 20 ms retries on any FileSystemException (copy of SkyyProfiles ProfCfg.atomicWrite)
M(cfg, r"""
public static void atomicWrite(java.nio.file.Path f, byte[] data) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(data);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(cfg, r"""
public static String readText(java.nio.file.Path f) throws java.io.IOException {
  return new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
}""")
M(cfg, r"""
public static long lngP(java.util.Properties p, String k, long d, long lo, long hi) {
  String v = p.getProperty(k);
  if (v == null) return d;
  long r = d;
  try { r = Long.parseLong(v.trim()); } catch (Throwable t) { @PKG@.AhUtil.warn("config " + k + "=" + v + " is not a whole number - using " + d); return d; }
  if (r < lo) { @PKG@.AhUtil.warn("config " + k + "=" + r + " is below " + lo + " - using " + lo); return lo; }
  if (r > hi) { @PKG@.AhUtil.warn("config " + k + "=" + r + " is above " + hi + " - using " + hi); return hi; }
  return r;
}""")
M(cfg, r"""
public static double dblP(java.util.Properties p, String k, double d, double lo, double hi) {
  String v = p.getProperty(k);
  if (v == null) return d;
  double r = d;
  try { r = Double.parseDouble(v.trim()); } catch (Throwable t) { @PKG@.AhUtil.warn("config " + k + "=" + v + " is not a number - using " + d); return d; }
  if (!(r >= lo) || r > hi) { @PKG@.AhUtil.warn("config " + k + "=" + v + " must be " + lo + " to " + hi + " - using " + d); return d; }
  return r;
}""")
M(cfg, r"""
public static boolean boolP(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim().toLowerCase();
  if (v.equals("true") || v.equals("yes") || v.equals("on") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("no") || v.equals("off") || v.equals("0")) return false;
  @PKG@.AhUtil.warn("config " + k + "=" + v + " is not true/false - using " + d);
  return d;
}""")
# "0:1.0,10000000:2.0,..." -> FEE_FROM / FEE_PCT sorted by fromPrice; false = keep the old table
M(cfg, r"""
public static boolean parseFees(String s) {
  if (s == null) return false;
  String[] parts = s.split(",");
  java.util.ArrayList from = new java.util.ArrayList();
  java.util.ArrayList pct = new java.util.ArrayList();
  for (int i = 0; i < parts.length; i++) {
    String x = parts[i].trim();
    if (x.length() == 0) continue;
    int c = x.indexOf(':');
    if (c <= 0) return false;
    long f;
    double pc;
    try { f = Long.parseLong(x.substring(0, c).trim()); pc = Double.parseDouble(x.substring(c + 1).trim()); } catch (Throwable t) { return false; }
    if (f < 0L || !(pc >= 0.0) || pc > 100.0) return false;
    int at = from.size();
    for (int k = 0; k < from.size(); k++) { if (((Long) from.get(k)).longValue() > f) { at = k; break; } }
    from.add(at, Long.valueOf(f));
    pct.add(at, Double.valueOf(pc));
  }
  if (from.isEmpty()) return false;
  long[] a = new long[from.size()];
  double[] b = new double[from.size()];
  for (int i = 0; i < a.length; i++) { a[i] = ((Long) from.get(i)).longValue(); b[i] = ((Double) pct.get(i)).doubleValue(); }
  FEE_FROM = a;
  FEE_PCT = b;
  FEE_TEXT = s.trim();
  return true;
}""")
# "1h:20,6h:45,..." -> DUR_*; test presets (fee < minDurationFee) dropped unless allowTestDurations; false = keep the defaults
M(cfg, r"""
public static boolean parseDurs(String s) {
  if (s == null) return false;
  String[] parts = s.split(",");
  java.util.ArrayList lab = new java.util.ArrayList();
  java.util.ArrayList ms = new java.util.ArrayList();
  java.util.ArrayList fee = new java.util.ArrayList();
  StringBuilder test = new StringBuilder();
  for (int i = 0; i < parts.length; i++) {
    String x = parts[i].trim();
    if (x.length() == 0) continue;
    int c = x.indexOf(':');
    if (c <= 0) { @PKG@.AhUtil.warn("config durations: bad entry " + x + " (use length:fee, like 24h:350)"); continue; }
    long m = @PKG@.AhUtil.parseDurMs(x.substring(0, c));
    long f = -1L;
    try { f = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable t) { f = -1L; }
    if (m <= 0L || f < 0L) { @PKG@.AhUtil.warn("config durations: bad entry " + x + " (use length:fee, like 24h:350)"); continue; }
    String l = x.substring(0, c).trim().toLowerCase();
    if (l.length() > 0 && Character.isDigit(l.charAt(l.length() - 1))) l = l + "h";
    if (m > 1209600000L) { @PKG@.AhUtil.warn("config durations: " + x + " is longer than 14 days - capped at 14d"); m = 1209600000L; l = "14d"; }
    boolean dup = false;
    for (int k = 0; k < ms.size(); k++) { if (((Long) ms.get(k)).longValue() == m) dup = true; }
    if (dup) { @PKG@.AhUtil.warn("config durations: " + x + " repeats a length - ignored"); continue; }
    if (f < MIN_DUR_FEE) {
      if (!ALLOW_TEST) { @PKG@.AhUtil.warn("dropped test duration " + l + ":" + f + " - set allowTestDurations=true to use it"); continue; }
      if (test.length() > 0) test.append(' ');
      test.append(l).append(':').append(f);
    }
    if (lab.size() >= 8) { @PKG@.AhUtil.warn("config durations: at most 8 presets - " + x + " ignored"); continue; }
    lab.add(l);
    ms.add(Long.valueOf(m));
    fee.add(Long.valueOf(f));
  }
  if (lab.isEmpty()) return false;
  String[] a = new String[lab.size()];
  long[] b = new long[lab.size()];
  long[] d = new long[lab.size()];
  for (int i = 0; i < a.length; i++) { a[i] = (String) lab.get(i); b[i] = ((Long) ms.get(i)).longValue(); d[i] = ((Long) fee.get(i)).longValue(); }
  DUR_LABEL = a;
  DUR_MS = b;
  DUR_FEE = d;
  TEST_ON = test.toString();
  return true;
}""")
M(cfg, r"""
public static int durIndexMs(long ms) {
  long[] m = DUR_MS;
  for (int i = 0; i < m.length; i++) if (m[i] == ms) return i;
  return -1;
}""")
M(cfg, r"""
public static String durList() {
  StringBuilder sb = new StringBuilder();
  String[] l = DUR_LABEL;
  for (int i = 0; i < l.length; i++) { if (i > 0) sb.append(' '); sb.append(l[i]); }
  return sb.toString();
}""")
M(cfg, r"""
public static synchronized String load() {
  java.util.Properties p = new java.util.Properties();
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) atomicWrite(FILE, TEMPLATE.getBytes("UTF-8"));
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not read " + FILE + " - using defaults: " + t); }
  MIN_DUR_FEE = lngP(p, "minDurationFee", 1L, 0L, 1000000000L);
  ALLOW_TEST = boolP(p, "allowTestDurations", false);
  if (!parseFees(p.getProperty("listingFee", "0:1.0,10000000:2.0,100000000:2.5"))) {
    @PKG@.AhUtil.warn("config listingFee is not fromPrice:percent,... - using 0:1.0,10000000:2.0,100000000:2.5");
    parseFees("0:1.0,10000000:2.0,100000000:2.5");
  }
  if (!parseDurs(p.getProperty("durations", "1h:20,6h:45,12h:100,24h:350,48h:1200"))) {
    @PKG@.AhUtil.warn("config durations has no usable preset - using 1h:20,6h:45,12h:100,24h:350,48h:1200");
    parseDurs("1h:20,6h:45,12h:100,24h:350,48h:1200");
  }
  long dm = @PKG@.AhUtil.parseDurMs(p.getProperty("defaultDuration", "24h"));
  int di = dm > 0L ? durIndexMs(dm) : -1;
  if (di < 0) {
    di = durIndexMs(86400000L);
    if (di < 0) di = 0;
    @PKG@.AhUtil.warn("config defaultDuration " + p.getProperty("defaultDuration", "24h") + " is not one of the durations - using " + DUR_LABEL[di]);
  }
  DEF_DUR = di;
  TAX_PCT = dblP(p, "claimTaxPercent", 1.0, 0.0, 50.0);
  TAX_FROM = lngP(p, "claimTaxFrom", 1000000L, 0L, 1000000000000000L);
  MIN_PRICE = lngP(p, "minPrice", 1L, 1L, 1000000000000000L);
  MAX_PRICE = lngP(p, "maxPrice", 50000000000L, 1L, 1000000000000000L);
  if (MAX_PRICE < MIN_PRICE) { @PKG@.AhUtil.warn("config maxPrice is below minPrice - using minPrice for both"); MAX_PRICE = MIN_PRICE; }
  MAX_LISTINGS = (int) lngP(p, "maxListings", 14L, 1L, 1000L);
  MAX_SERVER = (int) lngP(p, "maxListingsServer", 5000L, 1L, 100000L);
  GRACE_MS = lngP(p, "graceSeconds", 20L, 0L, 3600L) * 1000L;
  CONFIRM_ABOVE = lngP(p, "confirmAbove", 10000L, 0L, 1000000000000000L);
  CONFIRM_MS = lngP(p, "confirmSeconds", 10L, 3L, 120L) * 1000L;
  CLAIMALL_ABOVE = lngP(p, "claimAllConfirmAbove", 100000L, 0L, 1000000000000000L);
  CANCEL_REFUND = boolP(p, "cancelRefundsFee", false);
  ADMIN_REFUND = boolP(p, "adminRemoveRefundsFee", false);
  SAME_ACCOUNT = boolP(p, "sameAccountBuy", false);
  BLOCK_CREATIVE = boolP(p, "blockCreative", true);
  PAUSED = boolP(p, "paused", false);
  BAZAAR_OK = boolP(p, "bazaarItemsAllowed", false);
  SELL_PAGE = boolP(p, "sellCommandOpensPage", true);
  SPANS = boolP(p, "detailTextSpans", true);
  FORCE_SAVE = boolP(p, "forceSaveAfterTrade", true);
  if (TEST_ON.length() > 0) @PKG@.AhUtil.warn("TEST DURATIONS ARE ON: " + TEST_ON + " (allowTestDurations=true - set it back to false after testing)");
  if (SAME_ACCOUNT) @PKG@.AhUtil.warn("sameAccountBuy=true - profiles of one account can buy each other's listings (solo testing only)");
  return TEST_ON;
}""")
M(cfg, r"""
public static double pctFor(long price) {
  double pc = 0.0;
  long[] f = FEE_FROM;
  double[] q = FEE_PCT;
  for (int i = 0; i < f.length; i++) if (price >= f[i]) pc = q[i];
  return pc;
}""")
M(cfg, r"""
public static long listingFee(long price) {
  if (price <= 0L) return 0L;
  double pc = pctFor(price);
  long fee = (long) Math.ceil((double) price * pc / 100.0 - 1.0E-9);
  return fee < 0L ? 0L : fee;
}""")
# tax fixed at sale time: only above TAX_FROM, never taking the net below TAX_FROM
M(cfg, r"""
public static long tax(long gross) {
  if (gross <= TAX_FROM || TAX_PCT <= 0.0) return 0L;
  long t = (long) Math.ceil((double) gross * TAX_PCT / 100.0 - 1.0E-9);
  long cap = gross - TAX_FROM;
  if (t > cap) t = cap;
  return t < 0L ? 0L : t;
}""")
M(cfg, r"""
public static String pctText(double pc) {
  String s = String.valueOf(pc);
  if (s.endsWith(".0")) s = s.substring(0, s.length() - 2);
  return s;
}""")
# /ahadmin pause | resume: rewrite only the paused= line of config.properties
M(cfg, r"""
public static synchronized boolean setPaused(boolean on) {
  PAUSED = on;
  try {
    String txt = java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]) ? readText(FILE) : TEMPLATE;
    String[] lines = txt.split("\n", -1);
    StringBuilder sb = new StringBuilder();
    boolean done = false;
    for (int i = 0; i < lines.length; i++) {
      String l = lines[i];
      String t = l.trim();
      if (!done && (t.startsWith("paused=") || t.startsWith("paused =") || t.startsWith("paused:"))) { sb.append("paused=").append(on); done = true; }
      else sb.append(l);
      if (i < lines.length - 1) sb.append('\n');
    }
    if (!done) sb.append("\npaused=").append(on).append('\n');
    atomicWrite(FILE, sb.toString().getBytes("UTF-8"));
    return true;
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not write paused to config.properties: " + t); return false; }
}""")
M(cfg, r"""
public static String summary() {
  StringBuilder sb = new StringBuilder();
  sb.append("fees ").append(FEE_TEXT).append(" | durations ");
  for (int i = 0; i < DUR_LABEL.length; i++) { if (i > 0) sb.append(','); sb.append(DUR_LABEL[i]).append(':').append(DUR_FEE[i]); }
  sb.append(" (default ").append(DUR_LABEL[DEF_DUR < DUR_LABEL.length ? DEF_DUR : 0]).append(")");
  sb.append(" | tax ").append(pctText(TAX_PCT)).append("% above ").append(@PKG@.AhUtil.fmt(TAX_FROM));
  sb.append(" | price ").append(@PKG@.AhUtil.fmt(MIN_PRICE)).append("-").append(@PKG@.AhUtil.fmt(MAX_PRICE));
  sb.append(" | ").append(MAX_LISTINGS).append(" per profile, ").append(MAX_SERVER).append(" server");
  sb.append(" | grace ").append(GRACE_MS / 1000L).append("s | confirm >= ").append(@PKG@.AhUtil.fmt(CONFIRM_ABOVE));
  sb.append(" | claim-all confirm >= ").append(@PKG@.AhUtil.fmt(CLAIMALL_ABOVE));
  sb.append(" | sameAccountBuy ").append(SAME_ACCOUNT).append(" | blockCreative ").append(BLOCK_CREATIVE).append(" | bazaarItemsAllowed ").append(BAZAAR_OK);
  return sb.toString();
}""")
M(cfg, r"""
public static java.util.Map blockedMap() {
  java.util.Map b = @PKG@.AhUtil.bridge();
  Object o = b.get("market:blocked");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  b.putIfAbsent("market:blocked", new java.util.concurrent.ConcurrentHashMap());
  o = b.get("market:blocked");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  return new java.util.concurrent.ConcurrentHashMap();
}""")
M(cfg, r"""
public static void removeFileEntries() {
  try {
    java.util.Map m = blockedMap();
    java.util.Iterator it = new java.util.ArrayList(m.keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      Object v = m.get(k);
      if (v instanceof String && ((String) v).startsWith("file|")) m.remove(k);
    }
  } catch (Throwable t) { }
}""")
# Skyy_Market/blocked.txt -> market:blocked entries with owner "file" (other mods' entries are never touched)
M(cfg, r"""
public static synchronized int loadBlocked() {
  removeFileEntries();
  java.util.Map m = blockedMap();
  int n = 0;
  try {
    if (!java.nio.file.Files.exists(BLOCKED, new java.nio.file.LinkOption[0])) atomicWrite(BLOCKED, BLOCK_TEMPLATE.getBytes("UTF-8"));
    String[] lines = readText(BLOCKED).split("\n");
    for (int i = 0; i < lines.length; i++) {
      String l = lines[i];
      int h = l.indexOf('#');
      if (h >= 0) l = l.substring(0, h);
      l = l.trim();
      if (l.length() == 0) continue;
      String entry = l;
      String why = "late-game item";
      int eq = l.indexOf('=');
      if (eq >= 0) { entry = l.substring(0, eq).trim(); String w = l.substring(eq + 1).trim(); if (w.length() > 0) why = w; }
      if (entry.equals("*")) { @PKG@.AhUtil.warn("blocked.txt: a lone * is ignored (it would block everything) - use /ahadmin pause"); continue; }
      String idp = entry.endsWith("*") ? entry.substring(0, entry.length() - 1) : entry;
      if (!@PKG@.AhUtil.isId(idp)) { @PKG@.AhUtil.warn("blocked.txt: not an item id or Prefix* entry: " + entry); continue; }
      if (why.length() > 80) why = why.substring(0, 80);
      m.put(entry, "file|" + why);
      n++;
    }
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not read " + BLOCKED + ": " + t); }
  return n;
}""")

# ================= AhLog: synced auctions.log, BOOT / STOP, START scan, regrant evidence, rotation =================
F(lg, "public static java.nio.file.Path FILE;")
F(lg, "public static final java.util.ArrayList UNMATCHED = new java.util.ArrayList();")
M(lg, r"""
public static String line(String ev, String id, String rest) {
  return java.time.Instant.now().toString() + " " + ev + (id != null ? " #" + id : "") + (rest != null && rest.length() > 0 ? " " + rest : "");
}""")
# every append is written and fsynced before it returns (the log is the only evidence of an interrupted trade)
M(lg, r"""
public static synchronized boolean append(String text) {
  if (text == null || text.length() == 0 || FILE == null) return false;
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(FILE.toFile(), true);
    try {
      out.write(text.getBytes("UTF-8"));
      out.flush();
      out.getFD().sync();
    } finally { out.close(); }
    return true;
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not append auctions.log (" + text.length() + " chars): " + t); return false; }
}""")
M(lg, r"""
public static boolean log(String ev, String id, String rest) {
  return append(line(ev, id, rest) + "\n");
}""")
M(lg, r"""
public static java.util.List readLines(java.nio.file.Path f) {
  try {
    if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return new java.util.ArrayList();
    return java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
  } catch (Throwable t) { return new java.util.ArrayList(); }
}""")
# the newest ROTATED_KEEP rotated logs of ANY month (oldest first, by modified time), then auctions.log. Not "this month only":
# evidence from just before a month boundary must stay visible to regrant and to the start-up restore. Capped so a busy server's
# many 5 MB files are never all read on a world thread.
F(lg, "public static final int ROTATED_KEEP = 3;")
M(lg, r"""
public static java.util.ArrayList logFiles() {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.ArrayList ps = new java.util.ArrayList();
    java.util.ArrayList ts = new java.util.ArrayList();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(FILE.getParent());
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        java.nio.file.Path p = (java.nio.file.Path) it.next();
        String n = p.getFileName().toString();
        if (!n.startsWith("auctions-") || !n.endsWith(".log")) continue;
        long t = 0L;
        try { t = java.nio.file.Files.getLastModifiedTime(p, new java.nio.file.LinkOption[0]).toMillis(); } catch (Throwable x) { t = 0L; }
        int at = ts.size();
        for (int k = 0; k < ts.size(); k++) {
          long tk = ((Long) ts.get(k)).longValue();
          if (tk > t || (tk == t && ((java.nio.file.Path) ps.get(k)).getFileName().toString().compareTo(n) > 0)) { at = k; break; }
        }
        ts.add(at, Long.valueOf(t));
        ps.add(at, p);
      }
    } finally { ds.close(); }
    int from = ps.size() > ROTATED_KEEP ? ps.size() - ROTATED_KEEP : 0;
    for (int i = from; i < ps.size(); i++) out.add(ps.get(i));
  } catch (Throwable t) { }
  out.add(FILE);
  return out;
}""")
# a log line for display: the record copy a WRITE-FAILED / PAY-FAILED line carries is cut off (it can be thousands of characters)
M(lg, r"""
public static String shortDoc(String l) {
  if (l == null) return "";
  int i = l.indexOf(" doc=");
  return i < 0 ? l : l.substring(0, i) + " doc=(record copy)";
}""")
# startup: every LIST-START / BUY-START / CLAIM-COINS-START in the last 2000 lines without its commit or abort -> UNMATCHED + WARN
M(lg, r"""
public static synchronized int scanStarts() {
  UNMATCHED.clear();
  java.util.List all = readLines(FILE);
  int from = all.size() > 2000 ? all.size() - 2000 : 0;
  java.util.LinkedHashMap open = new java.util.LinkedHashMap();
  for (int i = from; i < all.size(); i++) {
    String l = (String) all.get(i);
    String[] t = l.split(" ");
    if (t.length < 3 || !t[2].startsWith("#")) continue;
    String ev = t[1];
    String base = null;
    boolean start = false;
    if (ev.endsWith("-START")) { base = ev.substring(0, ev.length() - 6); start = true; }
    else if (ev.endsWith("-ABORT")) base = ev.substring(0, ev.length() - 6);
    else if (ev.equals("PAY-FAILED") || ev.equals("PAY-ERROR")) base = "CLAIM-COINS";
    else if (ev.equals("LIST") || ev.equals("BUY") || ev.equals("CLAIM-COINS")) base = ev;
    if (base == null) continue;
    String k = base + " " + t[2];
    if (start) open.put(k, l); else open.remove(k);
  }
  java.util.Iterator it = open.values().iterator();
  while (it.hasNext()) {
    String l = (String) it.next();
    UNMATCHED.add(l);
    @PKG@.AhUtil.warn("possible lost coins - a trade started but never finished (check the purse and the record): " + l);
  }
  return UNMATCHED.size();
}""")
M(lg, r"""
public static java.util.ArrayList linesFor(String id, int max) {
  java.util.ArrayList out = new java.util.ArrayList();
  String want = "#" + id;
  java.util.ArrayList files = logFiles();
  for (int f = 0; f < files.size(); f++) {
    java.util.List all = readLines((java.nio.file.Path) files.get(f));
    for (int i = 0; i < all.size(); i++) {
      String l = (String) all.get(i);
      String[] t = l.split(" ");
      if (t.length >= 3 && t[2].equals(want)) out.add(shortDoc(l));
    }
  }
  while (out.size() > max) out.remove(0);
  return out;
}""")
# the first BOOT or STOP after an ISO time: "BOOT <time>" / "STOP <time>" / null
M(lg, r"""
public static String bootOrStopAfter(String iso) {
  java.time.Instant at;
  try { at = java.time.Instant.parse(iso); } catch (Throwable t) { return null; }
  java.time.Instant best = null;
  String bestEv = null;
  java.util.ArrayList files = logFiles();
  for (int f = 0; f < files.size(); f++) {
    java.util.List all = readLines((java.nio.file.Path) files.get(f));
    for (int i = 0; i < all.size(); i++) {
      String[] t = ((String) all.get(i)).split(" ");
      if (t.length < 2 || !(t[1].equals("BOOT") || t[1].equals("STOP"))) continue;
      java.time.Instant w;
      try { w = java.time.Instant.parse(t[0]); } catch (Throwable x) { continue; }
      if (!w.isAfter(at)) continue;
      if (best == null || w.isBefore(best)) { best = w; bestEv = t[1] + " " + t[0]; }
    }
  }
  return bestEv;
}""")
M(lg, r"""
public static synchronized void rotate() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    if (java.nio.file.Files.size(FILE) < 5242880L) return;
    String day = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd").withZone(java.time.ZoneOffset.UTC).format(java.time.Instant.now());
    java.nio.file.Path t = FILE.resolveSibling("auctions-" + day + ".log");
    int n = 1;
    while (java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0]) && n < 1000) { t = FILE.resolveSibling("auctions-" + day + "-" + n + ".log"); n++; }
    java.nio.file.Files.move(FILE, t, new java.nio.file.CopyOption[0]);
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not rotate auctions.log: " + t); }
}""")

# ================= Coins (SkyyCoins bridge; the SkyyBazaar wrapper) =================
M(coin, r"""
public static boolean ready() {
  java.util.Map b = @PKG@.AhUtil.bridge();
  return b.get("coins:fn:get") instanceof java.util.function.Function
      && b.get("coins:fn:add") instanceof java.util.function.Function
      && b.get("coins:fn:take") instanceof java.util.function.Function;
}""")
# get: balance, or -1 = no answer (the bridge is missing, threw or answered garbage). take / add: 1 = done, 0 = refused or missing,
# -1 = threw (outcome unknown)
M(coin, r"""
public static long get(java.util.UUID u) {
  Object f = @PKG@.AhUtil.bridge().get("coins:fn:get");
  if (!(f instanceof java.util.function.Function)) return -1L;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(u); }
  catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:get threw for " + u + ": " + t); return -1L; }
  return r instanceof Number ? ((Number) r).longValue() : -1L;
}""")
M(coin, r"""
public static int take(java.util.UUID u, long n) {
  if (n <= 0L) return 0;
  Object f = @PKG@.AhUtil.bridge().get("coins:fn:take");
  if (!(f instanceof java.util.function.Function)) return 0;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) }); }
  catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:take threw for " + u + " (" + n + " coins): " + t); return -1; }
  return (r instanceof Boolean && ((Boolean) r).booleanValue()) ? 1 : 0;
}""")
M(coin, r"""
public static int add(java.util.UUID u, long n) {
  if (n <= 0L) return 0;
  Object f = @PKG@.AhUtil.bridge().get("coins:fn:add");
  if (!(f instanceof java.util.function.Function)) return 0;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) }); }
  catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:add threw for " + u + " (" + n + " coins): " + t); return -1; }
  return r instanceof Number ? 1 : 0;
}""")

# ================= AhRec: the listing record (BsonDocument) =================
M(rec, r"""
public static String str(@BD@ d, String k, String def) {
  if (d == null) return def;
  try { @BV@ v = (@BV@) d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return def;
}""")
M(rec, r"""
public static long lng(@BD@ d, String k, long def) {
  if (d == null) return def;
  try { @BV@ v = (@BV@) d.get(k); if (v != null && v.isNumber()) return v.asNumber().longValue(); } catch (Throwable t) { }
  return def;
}""")
M(rec, r"""
public static double dbl(@BD@ d, String k, double def) {
  if (d == null) return def;
  try { @BV@ v = (@BV@) d.get(k); if (v != null && v.isNumber()) return v.asNumber().doubleValue(); } catch (Throwable t) { }
  return def;
}""")
M(rec, r"""
public static boolean bool(@BD@ d, String k, boolean def) {
  if (d == null) return def;
  try { @BV@ v = (@BV@) d.get(k); if (v != null && v.isBoolean()) return v.asBoolean().getValue(); } catch (Throwable t) { }
  return def;
}""")
M(rec, r"""
public static @BD@ sub(@BD@ d, String k) {
  if (d == null) return null;
  try { @BV@ v = (@BV@) d.get(k); if (v != null && v.isDocument()) return v.asDocument(); } catch (Throwable t) { }
  return null;
}""")
# for writes on a clone: the existing sub-document, or a new one put in place
M(rec, r"""
public static @BD@ subw(@BD@ d, String k) {
  @BD@ s = sub(d, k);
  if (s != null) return s;
  s = new @BD@();
  d.put(k, s);
  return s;
}""")
M(rec, r"""
public static String subStr(@BD@ d, String k, String f, String def) { return str(sub(d, k), f, def); }""")
M(rec, r"""
public static long subLng(@BD@ d, String k, String f, long def) { return lng(sub(d, k), f, def); }""")
M(rec, r"""
public static boolean subBool(@BD@ d, String k, String f, boolean def) { return bool(sub(d, k), f, def); }""")
M(rec, r"""
public static String id(@BD@ d) { return str(d, "id", ""); }""")
M(rec, r"""
public static String state(@BD@ d) { return str(d, "state", ""); }""")
M(rec, r"""
public static long numId(@BD@ d) {
  try { return Long.parseLong(id(d)); } catch (Throwable t) { return -1L; }
}""")
M(rec, r"""
public static String claim(@BD@ d, String f) { return subStr(d, "claims", f, "NONE"); }""")
M(rec, r"""
public static void setClaim(@BD@ d, String f, String v) { subw(d, "claims").put(f, new org.bson.BsonString(v)); }""")
M(rec, r"""
public static void putStr(@BD@ d, String k, String v) {
  if (v == null) d.put(k, org.bson.BsonNull.VALUE); else d.put(k, new org.bson.BsonString(v));
}""")
M(rec, r"""
public static void putLng(@BD@ d, String k, long v) { d.put(k, new org.bson.BsonInt64(v)); }""")
M(rec, r"""
public static void putBool(@BD@ d, String k, boolean v) { d.put(k, org.bson.BsonBoolean.valueOf(v)); }""")
# the next version of a record: a deep clone (unknown fields of newer versions survive) with rev + 1
M(rec, r"""
public static @BD@ next(@BD@ d) {
  @BD@ c = (@BD@) d.clone();
  c.put("rev", new org.bson.BsonInt64(lng(d, "rev", 0L) + 1L));
  return c;
}""")
M(rec, r"""
public static String toJson(@BD@ d) {
  org.bson.json.JsonWriterSettings s = org.bson.json.JsonWriterSettings.builder().outputMode(org.bson.json.JsonMode.EXTENDED).indent(true).build();
  return d.toJson(s);
}""")
M(rec, r"""
public static String oneLine(@BD@ d) {
  if (d == null) return "null";
  org.bson.json.JsonWriterSettings s = org.bson.json.JsonWriterSettings.builder().outputMode(org.bson.json.JsonMode.EXTENDED).build();
  return d.toJson(s);
}""")
M(rec, r"""
public static @BD@ parse(String s) { return org.bson.BsonDocument.parse(s); }""")
M(rec, r"""
public static boolean knownState(String s) {
  return s.equals("ACTIVE") || s.equals("SOLD") || s.equals("EXPIRED") || s.equals("CANCELLED") || s.equals("REMOVED");
}""")
# a record 0.1 must never act on: newer schema, unknown type or state (shown read-only)
M(rec, r"""
public static boolean readOnly(@BD@ d) {
  if (d == null) return true;
  if (lng(d, "v", 1L) > 1L) return true;
  if (!"BIN".equals(str(d, "type", "BIN"))) return true;
  return !knownState(state(d));
}""")
M(rec, r"""
public static boolean done(String c) { return "NONE".equals(c) || "CLAIMED".equals(c); }""")
M(rec, r"""
public static boolean closable(@BD@ d) {
  String s = state(d);
  if (!(s.equals("SOLD") || s.equals("EXPIRED") || s.equals("CANCELLED") || s.equals("REMOVED"))) return false;
  return done(claim(d, "sellerCoins")) && done(claim(d, "sellerItem")) && done(claim(d, "buyerItem"));
}""")
M(rec, r"""
public static String claimField(@BD@ d, String side) {
  if ("buyer".equals(side)) return "buyerItem";
  return "SOLD".equals(state(d)) ? "sellerCoins" : "sellerItem";
}""")

# ================= AhItem: snapshot / restore, category, rarity, names, inventory helpers, market rules =================
F(itm, 'public static final String[] CAT = new String[] { "ALL", "WEAPONS", "ARMOR", "ACCESSORIES", "CONSUMABLES", "BLOCKS", "MISC" };')
F(itm, 'public static final String[] CAT_LABEL = new String[] { "All", "Weapons", "Armor", "Accessories", "Consumables", "Blocks", "Tools & Misc" };')
F(itm, "public static String[] TIER_NAME;")
F(itm, "public static int[] TIER_VAL;")
F(itm, "public static String BZ_LAST = null;")
F(itm, "public static java.util.HashSet BZ_SET = new java.util.HashSet();")
F(itm, "public static final java.util.Set VETO_WARNED = java.util.concurrent.ConcurrentHashMap.newKeySet();")
M(itm, r"""
public static @BD@ snap(@IS@ s) {
  @BD@ d = new @BD@();
  d.put("id", new org.bson.BsonString(s.getItemId()));
  d.put("qty", new org.bson.BsonInt32(s.getQuantity()));
  d.put("durability", new org.bson.BsonDouble(s.getDurability()));
  d.put("maxDurability", new org.bson.BsonDouble(s.getMaxDurability()));
  d.put("quality", new org.bson.BsonInt32(s.getQualityIndex()));
  @BD@ m = s.getMetadata();
  if (m != null) d.put("meta", (@BD@) m.clone());
  try {
    @BV@ enc = ((@CODEC@) @IS@.CODEC).encode(s);
    if (enc != null) d.put("stack", enc);
  } catch (Throwable t) { @PKG@.AhUtil.warn("ItemStack.CODEC could not encode " + s.getItemId() + " (readable fields kept): " + t); }
  return d;
}""")
# engine codec first (exact), readable fields as the fallback; qty <= 0 = the snapshot's own quantity. Never a plain new ItemStack(id, n).
M(itm, r"""
public static @IS@ restore(@BD@ d, int qty) {
  if (d == null) return null;
  String id = @PKG@.AhRec.str(d, "id", null);
  if (qty <= 0) qty = (int) @PKG@.AhRec.lng(d, "qty", 0L);
  if (id == null || id.length() == 0 || qty <= 0) return null;
  @IS@ s = null;
  try {
    @BV@ enc = (@BV@) d.get("stack");
    if (enc != null && enc.isDocument()) {
      Object o = ((@CODEC@) @IS@.CODEC).decode((@BD@) enc.asDocument().clone());
      if (o instanceof @IS@) {
        @IS@ x = (@IS@) o;
        if (!x.isEmpty() && id.equals(x.getItemId())) s = x;
      }
    }
  } catch (Throwable t) { s = null; }
  if (s == null) {
    @BD@ meta = @PKG@.AhRec.sub(d, "meta");
    try {
      s = new @IS@(id, qty, @PKG@.AhRec.dbl(d, "durability", 0.0), @PKG@.AhRec.dbl(d, "maxDurability", 0.0), (int) @PKG@.AhRec.lng(d, "quality", 0L), meta == null ? null : (@BD@) meta.clone());
    } catch (Throwable t) { @PKG@.AhUtil.warn("listed item " + id + " x" + qty + " cannot be rebuilt (unknown item?): " + t); return null; }
  }
  if (s.getQuantity() != qty) {
    try { s = s.withQuantity(qty); } catch (Throwable t) { return null; }
  }
  return s;
}""")
M(itm, r"""
public static boolean metaEq(@BD@ a, @BD@ b) {
  boolean ea = a == null || a.isEmpty();
  boolean eb = b == null || b.isEmpty();
  if (ea || eb) return ea && eb;
  return a.equals(b);
}""")
M(itm, r"""
public static boolean sameStack(@IS@ a, @IS@ b) {
  if (a == null || b == null || a.isEmpty() || b.isEmpty()) return false;
  if (!a.getItemId().equals(b.getItemId())) return false;
  if (a.getQuantity() != b.getQuantity()) return false;
  if (a.getQualityIndex() != b.getQualityIndex()) return false;
  if (Math.abs(a.getDurability() - b.getDurability()) > 1.0E-9) return false;
  if (Math.abs(a.getMaxDurability() - b.getMaxDurability()) > 1.0E-9) return false;
  return metaEq(a.getMetadata(), b.getMetadata());
}""")
# spec 6.4 e: the snapshot must restore exactly, in memory AND through the JSON the record is stored as
M(itm, r"""
public static boolean roundTripOk(@IS@ orig, @BD@ snap) {
  try {
    @IS@ r = restore(snap, orig.getQuantity());
    if (!sameStack(orig, r)) return false;
    @BD@ wrap = new @BD@();
    wrap.put("item", snap);
    @BD@ back = @PKG@.AhRec.parse(@PKG@.AhRec.toJson(wrap));
    @IS@ r2 = restore(@PKG@.AhRec.sub(back, "item"), orig.getQuantity());
    return sameStack(orig, r2);
  } catch (Throwable t) { @PKG@.AhUtil.warn("snapshot round trip failed for " + orig.getItemId() + ": " + t); return false; }
}""")
# identity of a picked stack (Create click checks the slot still holds exactly this)
M(itm, r"""
public static String sig(@IS@ s) {
  if (s == null || s.isEmpty()) return "";
  @BD@ m = s.getMetadata();
  String mh = (m == null || m.isEmpty()) ? "0" : Integer.toHexString(m.toJson().hashCode());
  return s.getItemId() + "|" + s.getQuantity() + "|" + s.getDurability() + "|" + s.getQualityIndex() + "|" + mh;
}""")
M(itm, r"""
public static @IQ@ quality(int idx) {
  try { Object q = @IQ@.getAssetMap().getAsset(idx); if (q instanceof @IQ@) return (@IQ@) q; } catch (Throwable t) { }
  return null;
}""")
M(itm, r"""
public static int qValue(int idx) {
  @IQ@ q = quality(idx);
  if (q == null) return 1;
  try { return q.getQualityValue(); } catch (Throwable t) { return 1; }
}""")
M(itm, r"""
public static String qName(int idx) {
  @IQ@ q = quality(idx);
  if (q == null) return "Common";
  try { return String.valueOf(q.getId()); } catch (Throwable t) { return "Common"; }
}""")
M(itm, r"""
public static String qColor(int idx) {
  @IQ@ q = quality(idx);
  if (q != null) { try { String h = @PKG@.AhUtil.hex(q.getTextColor()); if (h != null) return h; } catch (Throwable t) { } }
  return "#c9d2dd";
}""")
# rarity filter tiers = the quality assets with QualityValue 1..5, sorted by value, named by asset id (SkyyGear tiers flow in later)
M(itm, r"""
public static synchronized void tiers() {
  if (TIER_NAME != null) return;
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList vals = new java.util.ArrayList();
  try {
    java.util.Map m = @IQ@.getAssetMap().getAssetMap();
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @IQ@)) continue;
      @IQ@ q = (@IQ@) o;
      int v = q.getQualityValue();
      if (v < 1 || v > 5) continue;
      int at = vals.size();
      for (int k = 0; k < vals.size(); k++) { if (((Integer) vals.get(k)).intValue() > v) { at = k; break; } }
      vals.add(at, Integer.valueOf(v));
      names.add(at, String.valueOf(q.getId()));
    }
  } catch (Throwable t) { }
  if (names.isEmpty()) {
    String[] dn = new String[] { "Common", "Uncommon", "Rare", "Epic", "Legendary" };
    for (int i = 0; i < dn.length; i++) { names.add(dn[i]); vals.add(Integer.valueOf(i + 1)); }
  }
  String[] n = new String[names.size()];
  int[] v = new int[names.size()];
  for (int i = 0; i < n.length; i++) { n[i] = (String) names.get(i); v[i] = ((Integer) vals.get(i)).intValue(); }
  TIER_VAL = v;
  TIER_NAME = n;
}""")
M(itm, r"""
public static String category(@IS@ s) {
  String id = s.getItemId();
  if (id.startsWith("Skyy_Talisman_") || (id.startsWith("Skyy_Accessory_") && !id.equals("Skyy_Accessory_Bag"))) return "ACCESSORIES";
  @ITM@ it = null;
  try { it = s.getItem(); } catch (Throwable t) { it = null; }
  if (it != null) {
    try { if (it.getWeapon() != null) return "WEAPONS"; } catch (Throwable t) { }
    try { if (it.getArmor() != null) return "ARMOR"; } catch (Throwable t) { }
    try { if (it.isConsumable()) return "CONSUMABLES"; } catch (Throwable t) { }
  }
  if (id.startsWith("Food_") || id.startsWith("Potion_") || id.startsWith("Skyy_Cook_")) return "CONSUMABLES";
  if (it != null) {
    try { if (it.getTool() != null || it.getGlider() != null || it.getUtility() != null) return "MISC"; } catch (Throwable t) { }
    try { if (it.hasBlockType()) return "BLOCKS"; } catch (Throwable t) { }
  }
  return "MISC";
}""")
M(itm, r"""
public static String reforge(@BD@ meta) {
  if (meta == null) return null;
  try {
    @BV@ v = (@BV@) meta.get("SkyyRolls");
    if (v != null && v.isDocument()) { String r = @PKG@.AhRec.str(v.asDocument(), "reforge", null); if (r != null && r.length() > 0) return r; }
  } catch (Throwable t) { }
  return null;
}""")
M(itm, r"""
public static boolean hasRolls(@BD@ meta) {
  if (meta == null) return false;
  try { @BV@ v = (@BV@) meta.get("SkyyRolls"); return v != null && v.isDocument(); } catch (Throwable t) { return false; }
}""")
# plain-text fallback of the SkyyRolls fields (detailTextSpans=false). Every numeric key of the SkyyRolls document is a rolled stat
# except the fixed keys reforge / quality / rolledAt (SkyyRolls' own STATS convention), so a stat SkyyRolls adds later shows up
# here without a SkyyAuctions change. Known stats get SkyyRolls' labels; an unknown key is shown by its capitalised name.
M(itm, r"""
public static String statLabel(String k) {
  if ("dmg".equals(k)) return "Damage";
  if ("str".equals(k)) return "Strength";
  if ("crit".equals(k)) return "Crit";
  if (k == null || k.length() == 0) return "?";
  return String.valueOf(Character.toUpperCase(k.charAt(0))) + k.substring(1);
}""")
M(itm, r"""
public static String rollsLine(@BD@ meta) {
  if (!hasRolls(meta)) return "";
  @BD@ d = ((@BV@) meta.get("SkyyRolls")).asDocument();
  StringBuilder sb = new StringBuilder();
  String r = @PKG@.AhRec.str(d, "reforge", null);
  if (r != null) sb.append("Reforge ").append(r);
  java.util.Iterator it = d.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if ("reforge".equals(k) || "quality".equals(k) || "rolledAt".equals(k)) continue;
    @BV@ v = (@BV@) d.get(k);
    if (v == null || !v.isNumber()) continue;
    long n = v.asNumber().longValue();
    if (sb.length() > 0) sb.append(" - ");
    sb.append(statLabel(k)).append(' ').append(n >= 0L ? "+" : "").append(n).append("dmg".equals(k) ? "%" : "");
  }
  if (d.containsKey("quality")) sb.append(sb.length() > 0 ? " - " : "").append("Roll quality ").append(@PKG@.AhRec.lng(d, "quality", 0L)).append("%");
  return sb.toString();
}""")
M(itm, r"""
public static String plainName(@IS@ s) {
  String n = null;
  try { n = @PKG@.AhUtil.plain(s.getDisplayName()); } catch (Throwable t) { n = null; }
  if (n == null || n.trim().length() == 0) { try { n = @PKG@.AhUtil.tr(s.getItem().getTranslationKey()); } catch (Throwable t) { n = null; } }
  if (n == null || n.trim().length() == 0) n = s.getItemId().replace('_', ' ');
  n = n.replace('\n', ' ').trim();
  if (n.length() > 64) n = n.substring(0, 64);
  return n;
}""")
M(itm, r"""
public static boolean isBag(String id) {
  return id != null && (id.startsWith("Skyy_Sack_") || id.equals("Skyy_Accessory_Bag"));
}""")
M(itm, r"""
public static boolean technical(@IS@ s) {
  return s != null && qValue(s.getQualityIndex()) >= 8;
}""")
# inventory sections the AH lists from / delivers to: 0 hotbar, 1 storage, 2 backpack (worn armor, utility and tools are never touched)
M(itm, r"""
public static @IC@ section(@PLA@ p, int sec) {
  if (p == null) return null;
  @INV@ inv = p.getInventory();
  if (inv == null) return null;
  if (sec == 0) return inv.getHotbar();
  if (sec == 1) return inv.getStorage();
  if (sec == 2) return inv.getBackpack();
  return null;
}""")
M(itm, r"""
public static String secName(int sec) {
  if (sec == 0) return "hotbar";
  if (sec == 1) return "storage";
  return "backpack";
}""")
M(itm, r"""
public static int count(@PLA@ p, String id) {
  int n = 0;
  for (int sec = 0; sec < 3; sec++) {
    @IC@ c = section(p, sec);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int k = 0; k < cap; k++) {
      @IS@ x = c.getItemStack((short) k);
      if (x == null || x.isEmpty() || !id.equals(x.getItemId())) continue;
      n += x.getQuantity();
    }
  }
  return n;
}""")
# units of this exact stack that fit: empty slot = max stack, a partial stack it can merge with = the rest of it
M(itm, r"""
public static int room(@PLA@ p, @IS@ stack) {
  if (p == null || stack == null) return 0;
  int max = 0;
  try { max = stack.getItem().getMaxStack(); } catch (Throwable t) { max = 0; }
  if (max <= 0) max = 1;
  long room = 0L;
  for (int sec = 0; sec < 3; sec++) {
    @IC@ c = section(p, sec);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int k = 0; k < cap; k++) {
      @IS@ x = c.getItemStack((short) k);
      if (x == null || x.isEmpty()) room += (long) max;
      else {
        boolean st = false;
        try { st = x.isStackableWith(stack); } catch (Throwable t) { st = false; }
        if (st && x.getQuantity() < max) room += (long) (max - x.getQuantity());
      }
    }
  }
  return room > 1000000L ? 1000000 : (int) room;
}""")
# bazaar:products is ONE comma-joined String (SkyyBazaar publishAll): whole-id tokens, cached until the String changes
M(itm, r"""
public static synchronized boolean isBazaarItem(String id) {
  if (id == null) return false;
  Object o = @PKG@.AhUtil.bridge().get("bazaar:products");
  if (!(o instanceof String)) return false;
  String s = (String) o;
  if (!s.equals(BZ_LAST)) {
    java.util.HashSet set = new java.util.HashSet();
    String[] parts = s.split(",");
    for (int i = 0; i < parts.length; i++) { String x = parts[i].trim(); if (x.length() > 0) set.add(x); }
    BZ_SET = set;
    BZ_LAST = s;
  }
  return BZ_SET.contains(id);
}""")
# market:blocked lookup: exact entry first, then every "Prefix*" key; a lone "*" is ignored. Reason = text after the first "|".
M(itm, r"""
public static String blockedReason(String id) {
  if (id == null) return null;
  Object o = @PKG@.AhUtil.bridge().get("market:blocked");
  if (!(o instanceof java.util.Map)) return null;
  java.util.Map m = (java.util.Map) o;
  Object v = m.get(id);
  if (v == null) {
    java.util.Iterator it = m.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      if (!(k instanceof String)) continue;
      String ks = (String) k;
      if (!ks.endsWith("*")) continue;
      if (ks.length() < 2) {
        if (!@PKG@.AhCfg.WARNED_STAR) { @PKG@.AhCfg.WARNED_STAR = true; @PKG@.AhUtil.warn("market:blocked holds a lone * entry - ignored (it would block everything)"); }
        continue;
      }
      if (id.startsWith(ks.substring(0, ks.length() - 1))) { v = m.get(k); if (v == null) v = ""; break; }
    }
  }
  if (v == null) return null;
  String s = String.valueOf(v);
  int bar = s.indexOf('|');
  String r = bar >= 0 ? s.substring(bar + 1).trim() : s.trim();
  return r.length() == 0 ? "late-game item" : r;
}""")
# market:veto: owner -> Function(ItemStack) -> null or a reason; a veto that throws refuses ("could not check this item"), logged once
M(itm, r"""
public static String vetoReason(@IS@ s) {
  Object o = @PKG@.AhUtil.bridge().get("market:veto");
  if (!(o instanceof java.util.Map)) return null;
  java.util.Iterator it = new java.util.ArrayList(((java.util.Map) o).entrySet()).iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object f = e.getValue();
    if (!(f instanceof java.util.function.Function)) continue;
    try {
      Object r = ((java.util.function.Function) f).apply(s);
      if (r != null) return String.valueOf(r);
    } catch (Throwable t) {
      if (VETO_WARNED.add(String.valueOf(e.getKey()))) @PKG@.AhUtil.warn("market:veto of " + e.getKey() + " threw - counted as a refusal: " + t);
      return "could not check this item";
    }
  }
  return null;
}""")
# spec 4.3 rules 1-4 + vetoes (null = can be listed)
M(itm, r"""
public static String tradeable(@IS@ s) {
  if (s == null || s.isEmpty() || s.getQuantity() < 1) return "Pick an item first.";
  String id = s.getItemId();
  if ("Skyy_Menu".equals(id)) return "The SkyWynn Menu item cannot be sold.";
  if (technical(s)) return "This is a technical item - it cannot be traded.";
  String b = blockedReason(id);
  if (b != null) return "This item is off the market (" + b + ").";
  if (!@PKG@.AhCfg.BAZAAR_OK && isBazaarItem(id)) return "Sell this on the Bazaar: /bz";
  String v = vetoReason(s);
  if (v != null) return v;
  return null;
}""")

# ================= AhResult =================
F(res, "public boolean ok;")
F(res, "public String msg;")
F(res, "public String id;")
F(res, "public long coins;")
F(res, "public int code;")
F(res, "public int items;")
F(res, "public boolean kept;")
F(res, "public boolean alert;")
F(res, "public boolean saveNeeded;")
F(res, "public java.util.UUID notifyUuid;")
F(res, "public String notifyMsg;")
F(res, "public java.util.UUID otherUuid;")
C(res, r"""
public AhResult(boolean ok, String msg) {
  this.ok = ok; this.msg = msg; this.code = 0;
}""")

# ================= AhSort (0 lowest price, 1 highest price, 2 ending soon, 3 newest, 4 oldest; ties by end time, then id) =================
srt.addInterface(pool.get("java.util.Comparator"))
F(srt, "public int mode;")
C(srt, "public AhSort(int mode) { this.mode = mode; }")
M(srt, r"""
public int compare(Object a, Object b) {
  @BD@ x = (@BD@) a;
  @BD@ y = (@BD@) b;
  int c = 0;
  if (mode == 0) c = Long.compare(@PKG@.AhRec.lng(x, "price", 0L), @PKG@.AhRec.lng(y, "price", 0L));
  else if (mode == 1) c = Long.compare(@PKG@.AhRec.lng(y, "price", 0L), @PKG@.AhRec.lng(x, "price", 0L));
  else if (mode == 3) c = Long.compare(@PKG@.AhRec.lng(y, "createdAt", 0L), @PKG@.AhRec.lng(x, "createdAt", 0L));
  else if (mode == 4) c = Long.compare(@PKG@.AhRec.lng(x, "createdAt", 0L), @PKG@.AhRec.lng(y, "createdAt", 0L));
  if (c != 0) return c;
  c = Long.compare(@PKG@.AhRec.lng(x, "endsAt", 0L), @PKG@.AhRec.lng(y, "endsAt", 0L));
  if (c != 0) return c;
  return Long.compare(@PKG@.AhRec.numId(x), @PKG@.AhRec.numId(y));
}""")

# ================= AhStore: records, the one lock, operations =================
F(sto, "public static java.nio.file.Path DIR;")
F(sto, "public static java.nio.file.Path LDIR;")
F(sto, "public static java.nio.file.Path ADIR;")
F(sto, "public static java.nio.file.Path BADDIR;")
F(sto, "public static java.nio.file.Path STATE;")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap LIVE = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap STACKS = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap ARCH = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap PREVIEW = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap SESSION = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static long NEXT = 1L;")
F(sto, "public static volatile boolean SAVE_BROKEN = false;")
F(sto, "public static final java.util.ArrayList RESTORED = new java.util.ArrayList();")
M(sto, r"""
public static java.nio.file.Path recFile(String id) { return LDIR.resolve(id + ".json"); }""")
M(sto, r"""
public static boolean write(@BD@ r) {
  String id = @PKG@.AhRec.id(r);
  if (id.length() == 0) return false;
  try {
    @PKG@.AhCfg.atomicWrite(recFile(id), @PKG@.AhRec.toJson(r).getBytes("UTF-8"));
    return true;
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not write listing #" + id + ": " + t); return false; }
}""")
M(sto, r"""
public static String month(long t) {
  return java.time.format.DateTimeFormatter.ofPattern("yyyy-MM").withZone(java.time.ZoneOffset.UTC).format(java.time.Instant.ofEpochMilli(t));
}""")
# never overwrite in archive/: <id>.json, else <id>.r<rev>.json, else with a time suffix
M(sto, r"""
public static java.nio.file.Path freeName(java.nio.file.Path dir, String id, long rev) {
  java.nio.file.Path t = dir.resolve(id + ".json");
  if (!java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) return t;
  t = dir.resolve(id + ".r" + rev + ".json");
  if (!java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) return t;
  return dir.resolve(id + ".r" + rev + "-" + System.currentTimeMillis() + ".json");
}""")
M(sto, r"""
public static void moveFile(java.nio.file.Path a, java.nio.file.Path b) throws java.io.IOException {
  try { java.nio.file.Files.move(a, b, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
  catch (java.nio.file.AtomicMoveNotSupportedException e) { java.nio.file.Files.move(a, b, new java.nio.file.CopyOption[0]); }
}""")
M(sto, r"""
public static boolean archiveMove(@BD@ r) {
  String id = @PKG@.AhRec.id(r);
  java.nio.file.Path src = recFile(id);
  try {
    if (!java.nio.file.Files.exists(src, new java.nio.file.LinkOption[0])) return true;
    long t = @PKG@.AhRec.lng(r, "closedAt", 0L);
    if (t <= 0L) t = System.currentTimeMillis();
    java.nio.file.Path dir = ADIR.resolve(month(t));
    java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    moveFile(src, freeName(dir, id, @PKG@.AhRec.lng(r, "rev", 0L)));
    return true;
  } catch (Throwable x) { @PKG@.AhUtil.warn("could not archive #" + id + " (the tick retries): " + x); return false; }
}""")
# a log line that carries the full record version memory kept although its write failed (one line of JSON after " doc="): the
# start-up restore writes it back if the listing file is older (restoreFromLog), so a crash before the tick's retry can never
# bring back a claim that was already handed over
M(sto, r"""
public static boolean logKept(String ev, String id, String rest, @BD@ d) {
  return @PKG@.AhLog.log(ev, id, rest + " doc=" + @PKG@.AhRec.oneLine(d));
}""")
# swap the new version into memory. A closed record leaves LIVE and waits in ARCH until it is archived: archived now when its closed
# version is on disk, else it stays in ARCH (and DIRTY) so /ahadmin info and regrant still find it; the tick archives it only after
# the closed version was written (retryDirty0 skips ARCH entries that are still DIRTY, so the stale file is never archived)
M(sto, r"""
public static void swap0(@BD@ r, boolean onDisk) {
  String id = @PKG@.AhRec.id(r);
  STACKS.remove(id);
  if (@PKG@.AhRec.bool(r, "closed", false)) {
    LIVE.remove(id);
    if (onDisk) { if (archiveMove(r)) ARCH.remove(id); else ARCH.put(id, r); }
    else ARCH.put(id, r);
  } else LIVE.put(id, r);
}""")
# R2 copy, write, swap: nothing in memory changes when the write fails
M(sto, r"""
public static boolean commit(@BD@ next) {
  if (!write(next)) return false;
  DIRTY.remove(@PKG@.AhRec.id(next));
  swap0(next, true);
  return true;
}""")
# R2 exception: after an effect that cannot be undone memory follows it even if the write failed (DIRTY, the tick retries)
M(sto, r"""
public static boolean commitForced(@BD@ next) {
  String id = @PKG@.AhRec.id(next);
  boolean ok = write(next);
  if (ok) DIRTY.remove(id);
  else {
    DIRTY.put(id, next);
    logKept("WRITE-FAILED", id, "rev=" + @PKG@.AhRec.lng(next, "rev", 0L) + " state=" + @PKG@.AhRec.state(next) + " closed=" + @PKG@.AhRec.bool(next, "closed", false) + " kept-in-memory", next);
    @PKG@.AhUtil.warn("WRITE FAILED for listing #" + id + " after an item or coin moved - memory follows it, the tick retries the write (auctions.log keeps a copy for the next start)");
  }
  swap0(next, ok);
  return ok;
}""")
M(sto, r"""
public static void closeIfDone(@BD@ next, long now) {
  if (@PKG@.AhRec.closable(next)) { next.put("closed", org.bson.BsonBoolean.TRUE); next.put("closedAt", new org.bson.BsonInt64(now)); }
}""")
M(sto, r"""
public static @BD@ get(String id) { if (id == null) return null; return (@BD@) LIVE.get(id); }""")
M(sto, r"""
public static boolean buyable(@BD@ r, long now) {
  return r != null && !@PKG@.AhRec.readOnly(r) && "ACTIVE".equals(@PKG@.AhRec.state(r)) && now < @PKG@.AhRec.lng(r, "endsAt", 0L);
}""")
M(sto, r"""
public static java.util.ArrayList active(long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = LIVE.values().iterator();
  while (it.hasNext()) { @BD@ r = (@BD@) it.next(); if (buyable(r, now)) out.add(r); }
  return out;
}""")
M(sto, r"""
public static int countActive(long now) { return active(now).size(); }""")
M(sto, r"""
public static boolean online(String uuid) {
  try { return @UNI@.get().getPlayer(java.util.UUID.fromString(uuid)) != null; } catch (Throwable t) { return false; }
}""")
# a slot counts from Create until the seller has claimed that listing's coins or item
M(sto, r"""
public static int slotsUsed(String key) {
  int n = 0;
  java.util.Iterator it = LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if (@PKG@.AhRec.bool(r, "closed", false)) continue;
    if (!key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) continue;
    if ("ACTIVE".equals(@PKG@.AhRec.state(r)) || "OWED".equals(@PKG@.AhRec.claim(r, "sellerCoins")) || "OWED".equals(@PKG@.AhRec.claim(r, "sellerItem"))) n++;
  }
  return n;
}""")
# Manage rows of one profile key, in order: coins owed, items owed (oldest first), active (ending soon first), read-only.
# String[] { id, kind }  kind = coins | sitem | bitem | active | ro
M(sto, r"""
public static java.util.ArrayList rowsFor(String key) {
  java.util.ArrayList coins = new java.util.ArrayList();
  java.util.ArrayList items = new java.util.ArrayList();
  java.util.ArrayList act = new java.util.ArrayList();
  java.util.ArrayList ro = new java.util.ArrayList();
  java.util.Iterator it = LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if (@PKG@.AhRec.bool(r, "closed", false)) continue;
    boolean isS = key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""));
    boolean isB = key.equals(@PKG@.AhRec.subStr(r, "buyer", "key", ""));
    if (!isS && !isB) continue;
    if (@PKG@.AhRec.readOnly(r)) { ro.add(r); continue; }
    String st = @PKG@.AhRec.state(r);
    if (isS && "SOLD".equals(st) && "OWED".equals(@PKG@.AhRec.claim(r, "sellerCoins"))) coins.add(r);
    else if (isS && "OWED".equals(@PKG@.AhRec.claim(r, "sellerItem"))) items.add(r);
    else if (isB && "OWED".equals(@PKG@.AhRec.claim(r, "buyerItem"))) items.add(r);
    else if (isS && "ACTIVE".equals(st)) act.add(r);
  }
  java.util.Collections.sort(coins, new @PKG@.AhSort(4));
  java.util.Collections.sort(items, new @PKG@.AhSort(4));
  java.util.Collections.sort(act, new @PKG@.AhSort(2));
  java.util.Collections.sort(ro, new @PKG@.AhSort(4));
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < coins.size(); i++) out.add(new String[] { @PKG@.AhRec.id((@BD@) coins.get(i)), "coins" });
  for (int i = 0; i < items.size(); i++) {
    @BD@ r = (@BD@) items.get(i);
    boolean s = key.equals(@PKG@.AhRec.subStr(r, "seller", "key", "")) && "OWED".equals(@PKG@.AhRec.claim(r, "sellerItem"));
    out.add(new String[] { @PKG@.AhRec.id(r), s ? "sitem" : "bitem" });
  }
  for (int i = 0; i < act.size(); i++) out.add(new String[] { @PKG@.AhRec.id((@BD@) act.get(i)), "active" });
  for (int i = 0; i < ro.size(); i++) out.add(new String[] { @PKG@.AhRec.id((@BD@) ro.get(i)), "ro" });
  return out;
}""")
# { claims owed, coins owed, items owed } for one profile key
M(sto, r"""
public static long[] owedFor(String key) {
  java.util.ArrayList rows = rowsFor(key);
  long n = 0L, coins = 0L, items = 0L;
  for (int i = 0; i < rows.size(); i++) {
    String[] x = (String[]) rows.get(i);
    if (x[1].equals("coins")) { n++; coins += @PKG@.AhRec.subLng(get(x[0]), "sale", "net", 0L); }
    else if (x[1].equals("sitem") || x[1].equals("bitem")) { n++; items++; }
  }
  return new long[] { n, coins, items };
}""")
M(sto, r"""
public static String otherProfiles(java.util.UUID u, String key) {
  // names: SkyyProfiles' current profile:list name first, the name stored on the record at trade time as the fallback
  String us = u.toString();
  java.util.LinkedHashMap cnt = new java.util.LinkedHashMap();
  java.util.HashMap names = new java.util.HashMap();
  java.util.Iterator it = LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if (@PKG@.AhRec.bool(r, "closed", false) || @PKG@.AhRec.readOnly(r)) continue;
    String sk = @PKG@.AhRec.subStr(r, "seller", "key", "");
    if (us.equals(@PKG@.AhRec.subStr(r, "seller", "uuid", "")) && !key.equals(sk)
        && (("SOLD".equals(@PKG@.AhRec.state(r)) && "OWED".equals(@PKG@.AhRec.claim(r, "sellerCoins"))) || "OWED".equals(@PKG@.AhRec.claim(r, "sellerItem")))) {
      Long v = (Long) cnt.get(sk);
      cnt.put(sk, Long.valueOf(v == null ? 1L : v.longValue() + 1L));
      names.put(sk, @PKG@.AhRec.subStr(r, "seller", "profile", ""));
    }
    String bk = @PKG@.AhRec.subStr(r, "buyer", "key", "");
    if (us.equals(@PKG@.AhRec.subStr(r, "buyer", "uuid", "")) && !key.equals(bk) && "OWED".equals(@PKG@.AhRec.claim(r, "buyerItem"))) {
      Long v = (Long) cnt.get(bk);
      cnt.put(bk, Long.valueOf(v == null ? 1L : v.longValue() + 1L));
      names.put(bk, @PKG@.AhRec.subStr(r, "buyer", "profile", ""));
    }
  }
  if (cnt.isEmpty()) return "";
  StringBuilder sb = new StringBuilder();
  java.util.Iterator ki = cnt.keySet().iterator();
  while (ki.hasNext()) {
    String k = (String) ki.next();
    long n = ((Long) cnt.get(k)).longValue();
    String nm = @PKG@.AhUtil.profListName(u, k);
    if (nm == null) nm = (String) names.get(k);
    if (sb.length() > 0) sb.append("; ");
    sb.append("Your profile ").append(nm == null || nm.length() == 0 ? "(another profile)" : nm).append(" has ").append(n).append(n == 1L ? " thing" : " things").append(" to claim");
  }
  sb.append(" - switch to it to claim.");
  return sb.toString();
}""")
# { lowest price EACH (ceil(price / qty)) or -1, how many are listed } among buyable BINs of that item id; skipId leaves one out of
# the lowest (the count still includes it). Lock-free read of LIVE.
M(sto, r"""
public static long[] lowestBin(String itemId, String skipId, long now) {
  if (itemId == null || @PKG@.AhItem.blockedReason(itemId) != null) return new long[] { -1L, 0L };
  long best = -1L;
  long n = 0L;
  java.util.Iterator it = LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if (!buyable(r, now) || !itemId.equals(@PKG@.AhRec.subStr(r, "item", "id", ""))) continue;
    n++;
    if (skipId != null && skipId.equals(@PKG@.AhRec.id(r))) continue;
    long q = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
    if (q < 1L) q = 1L;
    long each = @PKG@.AhUtil.ceilDiv(@PKG@.AhRec.lng(r, "price", 0L), q);
    if (best < 0L || each < best) best = each;
  }
  return new long[] { best, n };
}""")
# display cache (deliveries always restore fresh from the record)
M(sto, r"""
public static @IS@ stackOf(@BD@ r) {
  if (r == null) return null;
  String id = @PKG@.AhRec.id(r);
  long rev = @PKG@.AhRec.lng(r, "rev", 0L);
  Object o = STACKS.get(id);
  if (o instanceof Object[]) {
    Object[] a = (Object[]) o;
    if (((Long) a[0]).longValue() == rev) return (@IS@) a[1];
  }
  @IS@ s = @PKG@.AhItem.restore(@PKG@.AhRec.sub(r, "item"), 0);
  if (s != null) STACKS.put(id, new Object[] { Long.valueOf(rev), s });
  return s;
}""")
# state.properties is written BEFORE the id is used, so an id is never reused (inside the lock)
M(sto, r"""
public static long allocId() {
  long id = NEXT;
  try {
    @PKG@.AhCfg.atomicWrite(STATE, ("# SkyyAuctions - the next listing number (never reused)\nnextId=" + (id + 1L) + "\n").getBytes("UTF-8"));
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not write state.properties: " + t); return -1L; }
  NEXT = id + 1L;
  return id;
}""")
M(sto, r"""
public static void moveBad(java.nio.file.Path f) {
  try {
    java.nio.file.Files.createDirectories(BADDIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path t = BADDIR.resolve(f.getFileName().toString());
    if (java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) t = BADDIR.resolve(f.getFileName().toString() + "." + System.currentTimeMillis());
    moveFile(f, t);
    @PKG@.AhUtil.warn("unreadable listing file moved to listings/bad/" + t.getFileName() + " (never deleted - the snapshot is inside)");
  } catch (Throwable x) { @PKG@.AhUtil.warn("could not move the unreadable listing file " + f + ": " + x); }
}""")
M(sto, r"""
public static int load() {
  LIVE.clear(); STACKS.clear(); DIRTY.clear(); ARCH.clear();
  long next = 1L;
  try {
    java.nio.file.Files.createDirectories(LDIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.createDirectories(ADIR, new java.nio.file.attribute.FileAttribute[0]);
    if (java.nio.file.Files.exists(STATE, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(STATE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      next = Long.parseLong(p.getProperty("nextId", "1").trim());
    }
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not read state.properties (the ids continue after the highest record): " + t); }
  long maxId = 0L;
  try {
    java.util.ArrayList files = new java.util.ArrayList();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(LDIR);
    try { java.util.Iterator it = ds.iterator(); while (it.hasNext()) files.add(it.next()); } finally { ds.close(); }
    for (int i = 0; i < files.size(); i++) {
      java.nio.file.Path f = (java.nio.file.Path) files.get(i);
      if (java.nio.file.Files.isDirectory(f, new java.nio.file.LinkOption[0])) continue;
      String fn = f.getFileName().toString();
      if (fn.endsWith(".tmp")) { try { java.nio.file.Files.deleteIfExists(f); } catch (Throwable t) { } continue; }
      if (!fn.endsWith(".json")) continue;
      @BD@ r = null;
      try { r = @PKG@.AhRec.parse(@PKG@.AhCfg.readText(f)); } catch (Throwable t) { r = null; }
      String id = r == null ? "" : @PKG@.AhRec.id(r);
      if (r == null || id.length() == 0 || !(id + ".json").equals(fn)) { moveBad(f); continue; }
      long nid = @PKG@.AhRec.numId(r);
      if (nid > maxId) maxId = nid;
      if (@PKG@.AhRec.bool(r, "closed", false)) { if (!archiveMove(r)) ARCH.put(id, r); continue; }
      LIVE.put(id, r);
    }
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not read the listings folder: " + t); }
  if (next <= maxId) next = maxId + 1L;
  if (next < 1L) next = 1L;
  NEXT = next;
  return LIVE.size();
}""")
M(sto, r"""
public static boolean creative(@PLA@ p) {
  try { return p != null && p.getGameMode() == @GM@.Creative; } catch (Throwable t) { return false; }
}""")
# null = allowed. trade = list or buy (paused, deny, Creative, coins); every item move refuses while profile:busy is set
M(sto, r"""
public static String refuse(java.util.UUID u, @PLA@ p, boolean trade) {
  if (@PKG@.AhUtil.busy(u)) return "Your profile is still loading - try again in a moment.";
  if (!trade) return null;
  if (@PKG@.AhCfg.PAUSED) return "The Auction House is paused by an admin.";
  String d = @PKG@.AhUtil.deny(u);
  if (d != null) return "You cannot trade on the Auction House: " + d + ".";
  if (@PKG@.AhCfg.BLOCK_CREATIVE && creative(p)) return "Creative mode players can browse and claim, but not list or buy.";
  if (!@PKG@.Coins.ready()) return "Trading needs SkyyCoins - it is not loaded.";
  return null;
}""")
M(sto, r"""
public static @BD@ newRecord(String id, java.util.UUID u, String key, String name, String prof, @BD@ snap, @IS@ orig, long price, int durIdx, long feeL, long feeD, long now) {
  @BD@ r = new @BD@();
  r.put("v", new org.bson.BsonInt32(1));
  r.put("id", new org.bson.BsonString(id));
  r.put("type", new org.bson.BsonString("BIN"));
  r.put("state", new org.bson.BsonString("ACTIVE"));
  r.put("closed", org.bson.BsonBoolean.FALSE);
  r.put("rev", new org.bson.BsonInt64(1L));
  @BD@ s = new @BD@();
  s.put("uuid", new org.bson.BsonString(u.toString()));
  s.put("key", new org.bson.BsonString(key));
  s.put("name", new org.bson.BsonString(name == null ? "?" : name));
  s.put("profile", new org.bson.BsonString(prof == null ? "" : prof));
  r.put("seller", s);
  r.put("item", snap);
  String nm = @PKG@.AhItem.plainName(orig);
  r.put("name", new org.bson.BsonString(nm));
  r.put("search", new org.bson.BsonString((nm + " " + orig.getItemId() + " " + (name == null ? "" : name)).toLowerCase()));
  r.put("category", new org.bson.BsonString(@PKG@.AhItem.category(orig)));
  r.put("price", new org.bson.BsonInt64(price));
  r.put("startBid", new org.bson.BsonInt64(price));
  r.put("topBid", new org.bson.BsonInt64(0L));
  r.put("topBidder", org.bson.BsonNull.VALUE);
  r.put("bids", new org.bson.BsonArray());
  r.put("createdAt", new org.bson.BsonInt64(now));
  r.put("graceUntil", new org.bson.BsonInt64(now + @PKG@.AhCfg.GRACE_MS));
  r.put("endsAt", new org.bson.BsonInt64(now + @PKG@.AhCfg.DUR_MS[durIdx]));
  r.put("duration", new org.bson.BsonString(@PKG@.AhCfg.DUR_LABEL[durIdx]));
  @BD@ fee = new @BD@();
  fee.put("listing", new org.bson.BsonInt64(feeL));
  fee.put("duration", new org.bson.BsonInt64(feeD));
  fee.put("refunded", org.bson.BsonBoolean.FALSE);
  r.put("fee", fee);
  r.put("buyer", org.bson.BsonNull.VALUE);
  r.put("sale", org.bson.BsonNull.VALUE);
  @BD@ c = new @BD@();
  c.put("sellerCoins", new org.bson.BsonString("NONE"));
  c.put("sellerItem", new org.bson.BsonString("NONE"));
  c.put("buyerItem", new org.bson.BsonString("NONE"));
  c.put("sellerItemQty", new org.bson.BsonInt64(0L));
  c.put("buyerItemQty", new org.bson.BsonInt64(0L));
  r.put("claims", c);
  @BD@ nt = new @BD@();
  nt.put("seller", org.bson.BsonBoolean.FALSE);
  r.put("noticed", nt);
  r.put("removed", org.bson.BsonNull.VALUE);
  r.put("regrants", new org.bson.BsonArray());
  r.put("closedAt", new org.bson.BsonInt64(0L));
  return r;
}""")
# ---- LIST (spec 6.4), world thread, inside the lock ----
M(sto, r"""
public static @RES@ list0(@PLA@ p, @REF@ ref, @ST@ st, java.util.UUID u, String key, String name, String prof, int sec, int slot, String sig, long price, int durIdx) {
  long now = System.currentTimeMillis();
  String why = refuse(u, p, true);
  if (why != null) return new @RES@(false, why);
  if (p == null) return new @RES@(false, "Player not found.");
  if (!key.equals(@PKG@.AhUtil.pkey(u))) return new @RES@(false, "Your profile changed - pick the item again.");
  @IC@ c = @PKG@.AhItem.section(p, sec);
  if (c == null || slot < 0 || slot >= c.getCapacity()) return new @RES@(false, "That item moved or changed - pick it again.");
  @IS@ orig = c.getItemStack((short) slot);
  if (orig == null || orig.isEmpty() || !@PKG@.AhItem.sig(orig).equals(sig)) return new @RES@(false, "That item moved or changed - pick it again.");
  String iid = orig.getItemId();
  int qty = orig.getQuantity();
  if (qty < 1) return new @RES@(false, "That slot is empty.");
  String tw = @PKG@.AhItem.tradeable(orig);
  if (tw != null) return new @RES@(false, tw);
  if (price < @PKG@.AhCfg.MIN_PRICE || price > @PKG@.AhCfg.MAX_PRICE) return new @RES@(false, "The price must be " + @PKG@.AhUtil.fmt(@PKG@.AhCfg.MIN_PRICE) + " to " + @PKG@.AhUtil.fmt(@PKG@.AhCfg.MAX_PRICE) + " coins.");
  if (durIdx < 0 || durIdx >= @PKG@.AhCfg.DUR_MS.length) return new @RES@(false, "Pick a duration.");
  int used = slotsUsed(key);
  if (used >= @PKG@.AhCfg.MAX_LISTINGS) return new @RES@(false, "All your listing slots are used (" + used + " / " + @PKG@.AhCfg.MAX_LISTINGS + ") - claim or cancel one first.");
  if (LIVE.size() >= @PKG@.AhCfg.MAX_SERVER) return new @RES@(false, "The Auction House is full right now - try again later.");
  @BD@ snap = @PKG@.AhItem.snap(orig);
  if (!@PKG@.AhItem.roundTripOk(orig, snap)) return new @RES@(false, "This item cannot be listed (its data could not be saved).");
  long feeL = @PKG@.AhCfg.listingFee(price);
  long feeD = @PKG@.AhCfg.DUR_FEE[durIdx];
  long fee = feeL + feeD;
  long bal = @PKG@.Coins.get(u);
  if (bal < 0L) return new @RES@(false, "The coin bank did not answer - nothing listed. Try again.");
  if (bal < fee) return new @RES@(false, "You need " + @PKG@.AhUtil.fmt(fee - bal) + " more coins for the " + @PKG@.AhUtil.fmt(fee) + " coin fee.");
  long idn = allocId();
  if (idn < 0L) return new @RES@(false, "Could not save the listing number - nothing listed. Tell an admin.");
  String id = String.valueOf(idn);
  String it = "item=" + iid + "x" + qty;
  @PKG@.AhLog.log("LIST-START", id, "seller=" + @PKG@.AhUtil.tok(name) + " uuid=" + u + " key=" + key + " " + it + " price=" + price + " fee=" + fee);
  int tk = @PKG@.Coins.take(u, fee);
  if (tk != 1) {
    if (tk < 0) @PKG@.AhLog.log("TAKE-ERROR", id, "uuid=" + u + " fee=" + fee);
    @PKG@.AhLog.log("LIST-ABORT", id, "reason=" + (tk < 0 ? "take-error" : "take-refused"));
    @RES@ r0 = new @RES@(false, tk < 0 ? "The coin bank failed while taking the fee - nothing listed. If your purse dropped, tell an admin (it is logged)." : "Not enough coins for the fee.");
    r0.alert = tk < 0;
    return r0;
  }
  int before = @PKG@.AhItem.count(p, iid);
  try { c.removeItemStackFromSlot((short) slot, qty); } catch (Throwable t) { @PKG@.AhUtil.warn("removeItemStackFromSlot failed for #" + id + ": " + t); }
  int after = @PKG@.AhItem.count(p, iid);
  int removed = before - after;
  if (removed < 0) removed = 0;
  if (removed > qty) removed = qty;
  @IS@ left = c.getItemStack((short) slot);
  boolean empty = left == null || left.isEmpty();
  if (!empty || removed != qty) {
    String put = "none";
    if (removed > 0) {
      try { c.addItemStack(orig.withQuantity(removed)); } catch (Throwable t) { @PKG@.AhUtil.warn("put-back failed for #" + id + ": " + t); }
      int now2 = @PKG@.AhItem.count(p, iid);
      put = now2 >= before ? "ok" : "short=" + (before - now2);
      if (now2 < before) @PKG@.AhLog.log("ITEM-LOST", id, "uuid=" + u + " before=" + before + " after=" + after + " short=" + (before - now2) + " snap=" + @PKG@.AhRec.oneLine(snap));
    }
    int ad = @PKG@.Coins.add(u, fee);
    if (ad != 1) @PKG@.AhLog.log("REFUND-FAILED", id, "uuid=" + u + " owed=" + fee);
    @PKG@.AhLog.log("LIST-ABORT", id, "reason=item-moved removed=" + removed + " putback=" + put);
    @RES@ r1 = new @RES@(false, ad == 1 ? "The item moved - nothing listed and your fee was refunded." : "The item moved - nothing listed, but the fee refund of " + @PKG@.AhUtil.fmt(fee) + " coins FAILED. You are owed it - tell an admin (it is logged).");
    r1.alert = ad != 1 || put.startsWith("short");
    try { p.markNeedsSave(); } catch (Throwable t) { }
    return r1;
  }
  @BD@ r = newRecord(id, u, key, name, prof, snap, orig, price, durIdx, feeL, feeD, now);
  if (!write(r)) {
    try { c.addItemStackToSlot((short) slot, orig); } catch (Throwable t) { }
    int n2 = @PKG@.AhItem.count(p, iid);
    if (n2 < before) {
      try { @SIC@.addOrDropItemStack(st, ref, c, (short) slot, orig.withQuantity(before - n2)); } catch (Throwable t) { @PKG@.AhUtil.warn("addOrDropItemStack failed for #" + id + ": " + t); }
      n2 = @PKG@.AhItem.count(p, iid);
    }
    if (n2 < before) @PKG@.AhLog.log("ITEM-LOST", id, "uuid=" + u + " short=" + (before - n2) + " (the put-back may have dropped it at the player's feet) snap=" + @PKG@.AhRec.oneLine(snap));
    int ad2 = @PKG@.Coins.add(u, fee);
    if (ad2 != 1) @PKG@.AhLog.log("REFUND-FAILED", id, "uuid=" + u + " owed=" + fee);
    @PKG@.AhLog.log("LIST-ABORT", id, "reason=write-failed");
    try { p.markNeedsSave(); } catch (Throwable t) { }
    @RES@ r2 = new @RES@(false, ad2 == 1 ? "Could not save the listing - nothing listed, your item and fee are back." : "Could not save the listing - your item is back, but the fee refund of " + @PKG@.AhUtil.fmt(fee) + " coins FAILED. Tell an admin (it is logged).");
    r2.alert = ad2 != 1;
    return r2;
  }
  LIVE.put(id, r);
  @PKG@.AhLog.log("LIST", id, "seller=" + @PKG@.AhUtil.tok(name) + " key=" + key + " " + it + " price=" + price + " fee=" + fee + " ends=" + @PKG@.AhCfg.DUR_LABEL[durIdx]);
  try { p.markNeedsSave(); } catch (Throwable t) { }
  @RES@ ok = new @RES@(true, "Listed #" + id + " - " + @PKG@.AhRec.str(r, "name", iid) + (qty > 1 ? " x" + qty : "") + " for " + @PKG@.AhUtil.fmt(price) + " coins (fee " + @PKG@.AhUtil.fmt(fee) + " paid).");
  ok.id = id;
  ok.coins = fee;
  ok.saveNeeded = true;
  ok.code = 2;
  return ok;
}""")
# ---- the delivery routine (spec 6.3), inside the lock. { code 2 all / 1 part / 0 full or nothing / -1 not owed / -2 unreadable, added, left }
M(sto, r"""
public static int[] deliver0(@PLA@ p, @BD@ r, String key, boolean seller) {
  String f = seller ? "sellerItem" : "buyerItem";
  String qf = seller ? "sellerItemQty" : "buyerItemQty";
  String side = seller ? "seller" : "buyer";
  if (!"OWED".equals(@PKG@.AhRec.claim(r, f))) return new int[] { -1, 0, 0 };
  String owner = @PKG@.AhRec.subStr(r, seller ? "seller" : "buyer", "key", "");
  if (!owner.equals(key)) return new int[] { -1, 0, 0 };
  int qty = (int) @PKG@.AhRec.subLng(r, "claims", qf, 0L);
  if (qty <= 0) qty = (int) @PKG@.AhRec.subLng(r, "item", "qty", 1L);
  if (p == null) return new int[] { 0, 0, qty };
  @IS@ stack = @PKG@.AhItem.restore(@PKG@.AhRec.sub(r, "item"), qty);
  if (stack == null) return new int[] { -2, 0, qty };
  String iid = stack.getItemId();
  if (@PKG@.AhItem.room(p, stack) < qty) return new int[] { 0, 0, qty };
  int before = @PKG@.AhItem.count(p, iid);
  try { p.getInventory().getCombinedStorageHotbarBackpack().addItemStack(stack); } catch (Throwable t) { @PKG@.AhUtil.warn("addItemStack failed for #" + @PKG@.AhRec.id(r) + ": " + t); }
  int after = @PKG@.AhItem.count(p, iid);
  int added = after - before;
  if (added < 0) added = 0;
  if (added > qty) { @PKG@.AhUtil.warn("delivery of #" + @PKG@.AhRec.id(r) + " counted " + added + " > " + qty); added = qty; }
  if (added <= 0) return new int[] { 0, 0, qty };
  String id = @PKG@.AhRec.id(r);
  @BD@ next = @PKG@.AhRec.next(r);
  long now = System.currentTimeMillis();
  if (added >= qty) {
    @PKG@.AhRec.setClaim(next, f, "CLAIMED");
    @PKG@.AhRec.subw(next, "claims").put(qf, new org.bson.BsonInt64(0L));
    closeIfDone(next, now);
    commitForced(next);
    @PKG@.AhLog.log("CLAIM-ITEM", id, "side=" + side + " qty=" + added + " key=" + key + " item=" + iid);
  } else {
    @PKG@.AhRec.subw(next, "claims").put(qf, new org.bson.BsonInt64((long) (qty - added)));
    commitForced(next);
    @PKG@.AhLog.log("CLAIM-ITEM-PART", id, "side=" + side + " qty=" + added + " left=" + (qty - added) + " key=" + key + " item=" + iid);
  }
  try { p.markNeedsSave(); } catch (Throwable t) { }
  return new int[] { added >= qty ? 2 : 1, added, qty - added };
}""")
M(sto, r"""
public static @BD@ expiredClone(@BD@ r) {
  @BD@ next = @PKG@.AhRec.next(r);
  next.put("state", new org.bson.BsonString("EXPIRED"));
  @PKG@.AhRec.setClaim(next, "sellerItem", "OWED");
  @PKG@.AhRec.subw(next, "claims").put("sellerItemQty", new org.bson.BsonInt64(@PKG@.AhRec.subLng(r, "item", "qty", 1L)));
  @PKG@.AhRec.subw(next, "noticed").put("seller", org.bson.BsonBoolean.valueOf(online(@PKG@.AhRec.subStr(r, "seller", "uuid", ""))));
  return next;
}""")
M(sto, r"""
public static String itemTok(@BD@ r) {
  return "item=" + @PKG@.AhRec.subStr(r, "item", "id", "?") + "x" + @PKG@.AhRec.subLng(r, "item", "qty", 1L);
}""")
# ---- BUY (spec 6.5), buyer's world thread, inside the lock. p == null only in the offline harness (no delivery, item owed)
M(sto, r"""
public static @RES@ buy0(@PLA@ p, java.util.UUID u, String key, String name, String prof, String id, long shownPrice) {
  long now = System.currentTimeMillis();
  String why = refuse(u, p, true);
  if (why != null) return new @RES@(false, why);
  if (!key.equals(@PKG@.AhUtil.pkey(u))) return new @RES@(false, "Your profile changed - look at the listing again.");
  @BD@ r = get(id);
  if (r == null) return new @RES@(false, "That listing is no longer for sale.");
  if (@PKG@.AhRec.readOnly(r)) return new @RES@(false, "That listing needs a newer SkyyAuctions.");
  String state = @PKG@.AhRec.state(r);
  if ("SOLD".equals(state)) return new @RES@(false, "Someone bought it first.");
  if (!"ACTIVE".equals(state)) return new @RES@(false, "That listing is no longer for sale.");
  if (now >= @PKG@.AhRec.lng(r, "endsAt", 0L)) {
    @BD@ ex = expiredClone(r);
    if (commit(ex)) @PKG@.AhLog.log("EXPIRE", id, "seller=" + @PKG@.AhUtil.tok(@PKG@.AhRec.subStr(r, "seller", "name", "")) + " " + itemTok(r) + " (seen at buy)");
    @RES@ rx = new @RES@(false, "It just expired.");
    if (@PKG@.AhRec.subBool(ex, "noticed", "seller", false)) {
      try { rx.notifyUuid = java.util.UUID.fromString(@PKG@.AhRec.subStr(r, "seller", "uuid", "")); rx.notifyMsg = "[Auction House] Your listing of " + @PKG@.AhRec.str(r, "name", "an item") + " expired - /ah claim to get it back."; } catch (Throwable t) { }
    }
    return rx;
  }
  long grace = @PKG@.AhRec.lng(r, "graceUntil", 0L);
  if (now < grace) return new @RES@(false, "New listings can be bought " + (@PKG@.AhCfg.GRACE_MS / 1000L) + " s after they are listed - " + ((grace - now + 999L) / 1000L) + " s left.");
  long price = @PKG@.AhRec.lng(r, "price", 0L);
  if (price != shownPrice) return new @RES@(false, "The price is not the one you saw - look again.");
  String iid = @PKG@.AhRec.subStr(r, "item", "id", "");
  String b = @PKG@.AhItem.blockedReason(iid);
  if (b != null) return new @RES@(false, "That item is off the market (" + b + ") - it cannot be bought.");
  int qty = (int) @PKG@.AhRec.subLng(r, "item", "qty", 1L);
  @IS@ stack = @PKG@.AhItem.restore(@PKG@.AhRec.sub(r, "item"), qty);
  if (stack == null && p != null) return new @RES@(false, "That item could not be read - tell an admin.");
  if (stack != null) { String v = @PKG@.AhItem.vetoReason(stack); if (v != null) return new @RES@(false, v); }
  String sUuid = @PKG@.AhRec.subStr(r, "seller", "uuid", "");
  if (key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) return new @RES@(false, "That is your own listing.");
  if (sUuid.equals(u.toString()) && !@PKG@.AhCfg.SAME_ACCOUNT) return new @RES@(false, "You cannot buy from your own account (another of your profiles listed it).");
  long bal = @PKG@.Coins.get(u);
  if (bal < 0L) return new @RES@(false, "The coin bank did not answer - nothing bought. Try again.");
  if (bal < price) return new @RES@(false, "You need " + @PKG@.AhUtil.fmt(price - bal) + " more coins.");
  boolean fits = p != null && stack != null && @PKG@.AhItem.room(p, stack) >= qty;
  @PKG@.AhLog.log("BUY-START", id, "buyer=" + @PKG@.AhUtil.tok(name) + " uuid=" + u + " key=" + key + " price=" + price);
  int tk = @PKG@.Coins.take(u, price);
  if (tk != 1) {
    if (tk < 0) @PKG@.AhLog.log("TAKE-ERROR", id, "uuid=" + u + " price=" + price);
    @PKG@.AhLog.log("BUY-ABORT", id, "reason=" + (tk < 0 ? "take-error" : "take-refused"));
    @RES@ r0 = new @RES@(false, tk < 0 ? "The coin bank failed while taking " + @PKG@.AhUtil.fmt(price) + " coins - nothing bought. If your purse dropped, tell an admin (it is logged)." : "Not enough coins.");
    r0.alert = tk < 0;
    return r0;
  }
  long tax = @PKG@.AhCfg.tax(price);
  long net = price - tax;
  @BD@ next = @PKG@.AhRec.next(r);
  next.put("state", new org.bson.BsonString("SOLD"));
  @BD@ by = new @BD@();
  by.put("uuid", new org.bson.BsonString(u.toString()));
  by.put("key", new org.bson.BsonString(key));
  by.put("name", new org.bson.BsonString(name == null ? "?" : name));
  by.put("profile", new org.bson.BsonString(prof == null ? "" : prof));
  by.put("at", new org.bson.BsonInt64(now));
  next.put("buyer", by);
  @BD@ sale = new @BD@();
  sale.put("gross", new org.bson.BsonInt64(price));
  sale.put("tax", new org.bson.BsonInt64(tax));
  sale.put("net", new org.bson.BsonInt64(net));
  next.put("sale", sale);
  @PKG@.AhRec.setClaim(next, "sellerCoins", "OWED");
  @PKG@.AhRec.setClaim(next, "buyerItem", "OWED");
  @PKG@.AhRec.subw(next, "claims").put("buyerItemQty", new org.bson.BsonInt64((long) qty));
  boolean sOn = online(sUuid);
  @PKG@.AhRec.subw(next, "noticed").put("seller", org.bson.BsonBoolean.valueOf(sOn));
  if (!write(next)) {
    int ad = @PKG@.Coins.add(u, price);
    if (ad != 1) @PKG@.AhLog.log("REFUND-FAILED", id, "uuid=" + u + " owed=" + price);
    @PKG@.AhLog.log("BUY-ABORT", id, "reason=write-failed refund=" + (ad == 1 ? "ok" : "FAILED"));
    @RES@ rw = new @RES@(false, ad == 1 ? "Could not save the sale - nothing bought, your coins were refunded." : "Could not save the sale and the refund of " + @PKG@.AhUtil.fmt(price) + " coins FAILED - you are owed it, tell an admin (it is logged).");
    rw.alert = ad != 1;
    return rw;
  }
  swap0(next, true);
  @PKG@.AhLog.log("BUY", id, "buyer=" + @PKG@.AhUtil.tok(name) + " key=" + key + " seller=" + @PKG@.AhUtil.tok(@PKG@.AhRec.subStr(r, "seller", "name", "")) + " " + itemTok(r) + " price=" + price + " tax=" + tax + " net=" + net);
  String nm = @PKG@.AhRec.str(r, "name", iid);
  @RES@ ok = new @RES@(true, "");
  ok.id = id;
  ok.coins = price;
  ok.code = 0;
  if (fits) {
    int[] d = deliver0(p, next, key, false);
    ok.code = d[0];
    if (d[0] == 2) { ok.saveNeeded = true; ok.msg = "Bought " + nm + " for " + @PKG@.AhUtil.fmt(price) + " coins."; }
    else if (d[0] == 1) { ok.saveNeeded = true; ok.kept = true; ok.msg = "Bought " + nm + " for " + @PKG@.AhUtil.fmt(price) + " coins - " + d[2] + " did not fit and wait in Manage."; }
    else { ok.kept = true; ok.msg = "Bought " + nm + " for " + @PKG@.AhUtil.fmt(price) + " coins - your inventory is full, it waits in Manage (Claim item)."; }
  } else {
    ok.kept = true;
    ok.msg = "Bought " + nm + " for " + @PKG@.AhUtil.fmt(price) + " coins - your inventory is full, it waits in Manage (Claim item).";
  }
  try { ok.otherUuid = java.util.UUID.fromString(sUuid); } catch (Throwable t) { ok.otherUuid = null; }
  if (sOn && ok.otherUuid != null) {
    ok.notifyUuid = ok.otherUuid;
    ok.notifyMsg = "[Auction House] Your " + nm + " sold to " + name + " for " + @PKG@.AhUtil.fmt(price) + " coins. /ah claim";
  }
  return ok;
}""")
# ---- CANCEL (spec 6.7), seller's world thread, inside the lock
M(sto, r"""
public static @RES@ cancel0(@PLA@ p, java.util.UUID u, String key, String id) {
  String why = refuse(u, p, false);
  if (why != null) return new @RES@(false, why);
  if (!key.equals(@PKG@.AhUtil.pkey(u))) return new @RES@(false, "Your profile changed - look again.");
  @BD@ r = get(id);
  if (r == null) return new @RES@(false, "That listing is gone.");
  if (@PKG@.AhRec.readOnly(r)) return new @RES@(false, "That listing needs a newer SkyyAuctions.");
  if (!key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) return new @RES@(false, "Only the profile that listed it can cancel it.");
  String state = @PKG@.AhRec.state(r);
  if ("SOLD".equals(state)) return new @RES@(false, "It already sold - claim the coins in Manage.");
  if (!"ACTIVE".equals(state)) return new @RES@(false, "It is no longer active.");
  long now = System.currentTimeMillis();
  boolean expired = now >= @PKG@.AhRec.lng(r, "endsAt", 0L);
  @BD@ next = @PKG@.AhRec.next(r);
  next.put("state", new org.bson.BsonString(expired ? "EXPIRED" : "CANCELLED"));
  @PKG@.AhRec.setClaim(next, "sellerItem", "OWED");
  @PKG@.AhRec.subw(next, "claims").put("sellerItemQty", new org.bson.BsonInt64(@PKG@.AhRec.subLng(r, "item", "qty", 1L)));
  @PKG@.AhRec.subw(next, "noticed").put("seller", org.bson.BsonBoolean.TRUE);
  boolean refund = !expired && @PKG@.AhCfg.CANCEL_REFUND;
  long fee = @PKG@.AhRec.subLng(r, "fee", "listing", 0L) + @PKG@.AhRec.subLng(r, "fee", "duration", 0L);
  if (refund) @PKG@.AhRec.subw(next, "fee").put("refunded", org.bson.BsonBoolean.TRUE);
  if (!commit(next)) return new @RES@(false, "Could not save - try again.");
  @PKG@.AhLog.log(expired ? "EXPIRE" : "CANCEL", id, "seller=" + @PKG@.AhUtil.tok(@PKG@.AhRec.subStr(r, "seller", "name", "")) + " " + itemTok(r) + (refund ? " fee-refund=" + fee : ""));
  String nm = @PKG@.AhRec.str(r, "name", "the item");
  @RES@ ok = new @RES@(true, "");
  ok.id = id;
  if (refund && fee > 0L) {
    int ad = @PKG@.Coins.add(u, fee);
    if (ad != 1) { @PKG@.AhLog.log("REFUND-FAILED", id, "uuid=" + u + " owed=" + fee); ok.alert = true; }
  }
  int[] d = deliver0(p, get(id), key, true);
  ok.code = d[0];
  ok.saveNeeded = d[0] >= 1;
  String feeTxt = refund ? " Your fee was refunded." : (fee > 0L ? " (The " + @PKG@.AhUtil.fmt(fee) + " coin fee is not refunded.)" : "");
  String head = expired ? "It had already expired - " : "Cancelled - ";
  if (d[0] == 2) ok.msg = head + nm + " is back in your inventory." + feeTxt;
  else if (d[0] == 1) ok.msg = head + d[1] + " came back, " + d[2] + " wait in Manage - make room." + feeTxt;
  else { ok.kept = true; ok.msg = head + "your inventory is full, it waits in Manage (Claim item)." + feeTxt; }
  if (ok.alert) ok.msg = ok.msg + " The fee refund FAILED - tell an admin (it is logged).";
  return ok;
}""")
# ---- CLAIM COINS (spec 6.6): write CLAIMED first, then pay; a refused pay rolls back, a pay that THREW stays CLAIMED (logged)
M(sto, r"""
public static @RES@ claimCoins0(java.util.UUID u, String key, String id) {
  String why = refuse(u, null, false);
  if (why != null) return new @RES@(false, why);
  if (!@PKG@.Coins.ready()) return new @RES@(false, "Claiming coins needs SkyyCoins - it is not loaded.");
  if (!key.equals(@PKG@.AhUtil.pkey(u))) return new @RES@(false, "Your profile changed - look again.");
  @BD@ r = get(id);
  if (r == null || @PKG@.AhRec.readOnly(r)) return new @RES@(false, "Nothing to claim there.");
  if (!"SOLD".equals(@PKG@.AhRec.state(r)) || !"OWED".equals(@PKG@.AhRec.claim(r, "sellerCoins"))) return new @RES@(false, "Nothing to claim there.");
  if (!key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) return new @RES@(false, "Switch to the profile that listed it to claim these coins.");
  long net = @PKG@.AhRec.subLng(r, "sale", "net", 0L);
  long now = System.currentTimeMillis();
  @PKG@.AhLog.log("CLAIM-COINS-START", id, "uuid=" + u + " key=" + key + " net=" + net);
  @BD@ next = @PKG@.AhRec.next(r);
  @PKG@.AhRec.setClaim(next, "sellerCoins", "CLAIMED");
  closeIfDone(next, now);
  if (!write(next)) { @PKG@.AhLog.log("CLAIM-COINS-ABORT", id, "reason=write-failed"); return new @RES@(false, "Could not save - nothing paid, try again."); }
  int ad = net > 0L ? @PKG@.Coins.add(u, net) : 1;
  if (ad == 1) {
    DIRTY.remove(id);
    swap0(next, true);
    @PKG@.AhLog.log("CLAIM-COINS", id, "uuid=" + u + " key=" + key + " net=" + net);
    @RES@ ok = new @RES@(true, "Claimed " + @PKG@.AhUtil.fmt(net) + " coins for " + @PKG@.AhRec.str(r, "name", "your item") + ".");
    ok.coins = net;
    ok.id = id;
    ok.code = 2;
    return ok;
  }
  if (ad < 0) {
    DIRTY.remove(id);
    swap0(next, true);
    @PKG@.AhLog.log("PAY-ERROR", id, "uuid=" + u + " key=" + key + " net=" + net + " coins:fn:add threw - it may or may not have paid; check the purse, /ahadmin regrant " + id + " seller if unpaid");
    @RES@ re = new @RES@(false, "The coin bank failed while paying " + @PKG@.AhUtil.fmt(net) + " coins. If your purse did not go up, tell an admin (it is logged).");
    re.alert = true;
    return re;
  }
  @BD@ back = @PKG@.AhRec.next(next);
  @PKG@.AhRec.setClaim(back, "sellerCoins", "OWED");
  back.put("closed", org.bson.BsonBoolean.FALSE);
  back.put("closedAt", new org.bson.BsonInt64(0L));
  if (write(back)) { DIRTY.remove(id); swap0(back, true); @PKG@.AhLog.log("CLAIM-COINS-ABORT", id, "reason=pay-refused"); }
  else { DIRTY.put(id, back); swap0(back, false); logKept("PAY-FAILED", id, "uuid=" + u + " net=" + net + " rev=" + @PKG@.AhRec.lng(back, "rev", 0L) + " roll-back write failed - memory keeps OWED, the tick retries", back); }
  @RES@ rf = new @RES@(false, "Could not pay the coins - try again.");
  rf.alert = true;
  return rf;
}""")
# ---- CLAIM ITEM (one row)
M(sto, r"""
public static @RES@ claimItem0(@PLA@ p, java.util.UUID u, String key, String id, boolean seller) {
  String why = refuse(u, p, false);
  if (why != null) return new @RES@(false, why);
  if (!key.equals(@PKG@.AhUtil.pkey(u))) return new @RES@(false, "Your profile changed - look again.");
  @BD@ r = get(id);
  if (r == null || @PKG@.AhRec.readOnly(r)) return new @RES@(false, "Nothing to claim there.");
  if (p == null) return new @RES@(false, "Player not found.");
  String nm = @PKG@.AhRec.str(r, "name", "the item");
  int[] d = deliver0(p, r, key, seller);
  @RES@ o = new @RES@(d[0] >= 1, "");
  o.code = d[0];
  o.items = d[1];
  o.id = id;
  o.saveNeeded = d[0] >= 1;
  if (d[0] == -1) o.msg = "Nothing to claim there.";
  else if (d[0] == -2) { o.msg = "That item could not be read - tell an admin (#" + id + ")."; o.alert = true; }
  else if (d[0] == 0) { o.kept = true; o.msg = "Your inventory is full - make room and claim again."; }
  else if (d[0] == 1) { o.kept = true; o.msg = "Claimed " + d[1] + " of " + nm + " - " + d[2] + " more wait, make room."; }
  else o.msg = "Claimed " + nm + ".";
  return o;
}""")
# ---- EXPIRE pass (tick, scheduler thread; never touches an inventory). Returns Object[] { UUID, message } for online sellers.
M(sto, r"""
public static java.util.ArrayList expireDue0(long now) {
  java.util.ArrayList notes = new java.util.ArrayList();
  StringBuilder lines = new StringBuilder();
  java.util.ArrayList docs = new java.util.ArrayList(LIVE.values());
  for (int i = 0; i < docs.size(); i++) {
    @BD@ r = (@BD@) docs.get(i);
    if (@PKG@.AhRec.readOnly(r) || !"ACTIVE".equals(@PKG@.AhRec.state(r)) || now < @PKG@.AhRec.lng(r, "endsAt", 0L)) continue;
    @BD@ next = expiredClone(r);
    if (!commit(next)) continue;
    String id = @PKG@.AhRec.id(r);
    lines.append(@PKG@.AhLog.line("EXPIRE", id, "seller=" + @PKG@.AhUtil.tok(@PKG@.AhRec.subStr(r, "seller", "name", "")) + " " + itemTok(r) + " price=" + @PKG@.AhRec.lng(r, "price", 0L))).append('\n');
    if (@PKG@.AhRec.subBool(next, "noticed", "seller", false)) {
      try { notes.add(new Object[] { java.util.UUID.fromString(@PKG@.AhRec.subStr(r, "seller", "uuid", "")), "[Auction House] Your listing of " + @PKG@.AhRec.str(r, "name", "an item") + " expired - /ah claim to get it back." }); } catch (Throwable t) { }
    }
  }
  if (lines.length() > 0) @PKG@.AhLog.append(lines.toString());
  return notes;
}""")
# ---- ADMIN REMOVE (ACTIVE only; SOLD is refused - the buyer already paid)
M(sto, r"""
public static @RES@ adminRemove0(String by, String id, String reason) {
  @BD@ r = get(id);
  if (r == null) return new @RES@(false, "No open listing #" + id + ".");
  if (@PKG@.AhRec.readOnly(r)) return new @RES@(false, "#" + id + " needs a newer SkyyAuctions - not touched.");
  String state = @PKG@.AhRec.state(r);
  if ("SOLD".equals(state)) return new @RES@(false, "#" + id + " already sold - the buyer paid. Fix it with coin commands instead.");
  if (!"ACTIVE".equals(state)) return new @RES@(false, "#" + id + " is not active (" + state + ").");
  long now = System.currentTimeMillis();
  String su = @PKG@.AhRec.subStr(r, "seller", "uuid", "");
  @BD@ next = @PKG@.AhRec.next(r);
  next.put("state", new org.bson.BsonString("REMOVED"));
  @BD@ rm = new @BD@();
  rm.put("by", new org.bson.BsonString(by == null ? "admin" : by));
  rm.put("reason", new org.bson.BsonString(reason));
  rm.put("at", new org.bson.BsonInt64(now));
  next.put("removed", rm);
  @PKG@.AhRec.setClaim(next, "sellerItem", "OWED");
  @PKG@.AhRec.subw(next, "claims").put("sellerItemQty", new org.bson.BsonInt64(@PKG@.AhRec.subLng(r, "item", "qty", 1L)));
  boolean on = online(su);
  @PKG@.AhRec.subw(next, "noticed").put("seller", org.bson.BsonBoolean.valueOf(on));
  long fee = @PKG@.AhRec.subLng(r, "fee", "listing", 0L) + @PKG@.AhRec.subLng(r, "fee", "duration", 0L);
  if (@PKG@.AhCfg.ADMIN_REFUND) @PKG@.AhRec.subw(next, "fee").put("refunded", org.bson.BsonBoolean.TRUE);
  if (!commit(next)) return new @RES@(false, "Could not write #" + id + " - nothing changed.");
  @PKG@.AhLog.log("REMOVE", id, "by=" + @PKG@.AhUtil.tok(by) + " reason=" + @PKG@.AhUtil.tok(reason) + " " + itemTok(r));
  String nm = @PKG@.AhRec.str(r, "name", "an item");
  @RES@ ok = new @RES@(true, "Removed #" + id + " (" + nm + "). The item waits in the seller's claims.");
  try { ok.otherUuid = java.util.UUID.fromString(su); } catch (Throwable t) { ok.otherUuid = null; }
  if (@PKG@.AhCfg.ADMIN_REFUND && fee > 0L) {
    boolean paid = false;
    if (on && ok.otherUuid != null && @PKG@.AhUtil.pkey(ok.otherUuid).equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) paid = @PKG@.Coins.add(ok.otherUuid, fee) == 1;
    if (!paid) { @PKG@.AhLog.log("REFUND-FAILED", id, "uuid=" + su + " owed=" + fee + " seller offline or on another profile - pay with /coinsgive"); ok.msg = ok.msg + " The fee refund of " + @PKG@.AhUtil.fmt(fee) + " could not be paid now (seller offline or on another profile) - use /coinsgive."; }
    else ok.msg = ok.msg + " Fee refunded.";
  }
  if (on && ok.otherUuid != null) {
    ok.notifyUuid = ok.otherUuid;
    ok.notifyMsg = "[Auction House] An admin removed your listing of " + nm + ": " + reason + ". /ah claim to get it back.";
  }
  return ok;
}""")
M(sto, r"""
public static java.nio.file.Path findArchived(String id) {
  try {
    if (ADIR == null || !java.nio.file.Files.isDirectory(ADIR, new java.nio.file.LinkOption[0])) return null;
    java.util.ArrayList months = new java.util.ArrayList();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(ADIR);
    try { java.util.Iterator it = ds.iterator(); while (it.hasNext()) months.add(it.next()); } finally { ds.close(); }
    java.util.Collections.sort(months);
    for (int i = months.size() - 1; i >= 0; i--) {
      java.nio.file.Path f = ((java.nio.file.Path) months.get(i)).resolve(id + ".json");
      if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return f;
    }
  } catch (Throwable t) { }
  return null;
}""")
M(sto, r"""
public static @BD@ readAny(String id) {
  @BD@ r = get(id);
  if (r != null) return r;
  Object pend = ARCH.get(id);
  if (pend instanceof @BD@) return (@BD@) pend;
  java.nio.file.Path f = findArchived(id);
  if (f == null) return null;
  try { return @PKG@.AhRec.parse(@PKG@.AhCfg.readText(f)); } catch (Throwable t) { return null; }
}""")
M(sto, r"""
public static String qtyToken(String line) {
  String[] t = line.split(" ");
  for (int i = 0; i < t.length; i++) if (t[i].startsWith("qty=")) return t[i].substring(4);
  return null;
}""")
# ---- REGRANT preview (read-only; remembers admin, id, side, rev and the owed quantity for 60 s)
M(sto, r"""
public static java.util.ArrayList regrantPreview(java.util.UUID admin, String id, String side) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (!"seller".equals(side) && !"buyer".equals(side)) { out.add("The side must be seller or buyer."); return out; }
  @BD@ r = get(id);
  boolean arch = false;
  if (r == null) { r = readAny(id); arch = r != null; }
  if (r == null) { out.add("No record #" + id + " (live or archived)."); return out; }
  if (@PKG@.AhRec.readOnly(r)) { out.add("#" + id + " needs a newer SkyyAuctions - regrant refused."); return out; }
  String f = @PKG@.AhRec.claimField(r, side);
  String cur = @PKG@.AhRec.claim(r, f);
  long rev = @PKG@.AhRec.lng(r, "rev", 0L);
  long full = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
  String nm = @PKG@.AhRec.str(r, "name", "?");
  out.add("#" + id + " " + @PKG@.AhRec.state(r) + (arch ? " (archived)" : "") + " rev " + rev + " - " + nm + " x" + full + " - price " + @PKG@.AhUtil.fmt(@PKG@.AhRec.lng(r, "price", 0L)));
  out.add("Claims: sellerCoins " + @PKG@.AhRec.claim(r, "sellerCoins") + ", sellerItem " + @PKG@.AhRec.claim(r, "sellerItem") + ", buyerItem " + @PKG@.AhRec.claim(r, "buyerItem") + " - this regrant touches " + f + " (now " + cur + ")");
  try {
    @BV@ rv = (@BV@) r.get("regrants");
    if (rv != null && rv.isArray()) {
      org.bson.BsonArray a = rv.asArray();
      for (int i = 0; i < a.size(); i++) {
        @BV@ e = (@BV@) a.get(i);
        if (e == null || !e.isDocument()) continue;
        @BD@ ed = e.asDocument();
        String when = java.time.Instant.ofEpochMilli(@PKG@.AhRec.lng(ed, "at", 0L)).toString();
        String es = @PKG@.AhRec.str(ed, "side", "?");
        out.add((side.equals(es) ? "ALREADY REGRANTED (" : "Earlier regrant (") + es + ") on " + when + " by " + @PKG@.AhRec.str(ed, "by", "?") + ", qty " + @PKG@.AhRec.lng(ed, "qty", 0L));
      }
    }
  } catch (Throwable t) { }
  java.util.ArrayList lines = @PKG@.AhLog.linesFor(id, 12);
  for (int i = 0; i < lines.size(); i++) out.add("log: " + lines.get(i));
  long qty = full;
  String verdict;
  if (f.equals("sellerCoins")) {
    String last = null;
    for (int i = 0; i < lines.size(); i++) {
      String[] t = ((String) lines.get(i)).split(" ");
      if (t.length < 2) continue;
      if (t[1].equals("CLAIM-COINS-START") || t[1].equals("CLAIM-COINS") || t[1].equals("CLAIM-COINS-ABORT") || t[1].equals("PAY-FAILED") || t[1].equals("PAY-ERROR")) last = t[1];
    }
    if ("CLAIM-COINS".equals(last)) verdict = "CLAIM-COINS commit found - the coins were paid; a regrant would duplicate them";
    else if ("CLAIM-COINS-START".equals(last)) verdict = "CLAIM-COINS-START with no CLAIM-COINS or ABORT - looks like a real interrupted payout";
    else if ("PAY-ERROR".equals(last)) verdict = "PAY-ERROR - the coin bank threw while paying; check the seller's purse before regranting";
    else verdict = "no payout line found - check the seller's purse before regranting";
  } else {
    String lastTime = null;
    long lastQty = -1L;
    for (int i = 0; i < lines.size(); i++) {
      String l = (String) lines.get(i);
      String[] t = l.split(" ");
      if (t.length < 2 || !(t[1].equals("CLAIM-ITEM") || t[1].equals("CLAIM-ITEM-PART"))) continue;
      if (l.indexOf(" side=" + side + " ") < 0) continue;
      lastTime = t[0];
      String q = qtyToken(l);
      try { lastQty = q == null ? -1L : Long.parseLong(q); } catch (Throwable x) { lastQty = -1L; }
    }
    if (lastQty > 0L) qty = lastQty;
    else out.add("No delivery line found for this side - the regrant would owe the full stack (" + full + ").");
    if (lastTime != null) {
      String bs = @PKG@.AhLog.bootOrStopAfter(lastTime);
      if (bs != null && bs.startsWith("BOOT")) verdict = "CLAIM-ITEM at " + lastTime + ", then BOOT at " + bs.substring(5) + " with no STOP in between - a crash followed this delivery";
      else if (bs != null) verdict = "CLAIM-ITEM at " + lastTime + ", then a clean STOP - no crash after the last delivery - check the player's inventory before regranting";
      else verdict = "no crash after the last delivery (" + lastTime + ") - check the player's inventory before regranting";
    } else verdict = "no delivery found in the log - check the player's inventory before regranting";
  }
  out.add("Verdict: " + verdict);
  if (!"CLAIMED".equals(cur)) { out.add("A regrant is REFUSED: the claim is " + cur + ", not CLAIMED."); PREVIEW.remove(admin); return out; }
  String owner = @PKG@.AhRec.subStr(r, side, "name", "?");
  String what = f.equals("sellerCoins") ? @PKG@.AhUtil.fmt(@PKG@.AhRec.subLng(r, "sale", "net", 0L)) + " coins" : qty + " x " + nm;
  out.add("Would owe " + what + " to " + owner + " (profile " + @PKG@.AhRec.subStr(r, side, "profile", "?") + ").");
  out.add("To apply: /ahadmin regrant " + id + " " + side + " confirm   (within 60 s)");
  PREVIEW.put(admin, new String[] { id, side, String.valueOf(rev), String.valueOf(System.currentTimeMillis() + 60000L), String.valueOf(qty) });
  return out;
}""")
# ---- REGRANT apply, inside the lock: exactly CLAIMED -> OWED, same path as every other change (write, then LIVE), no restart needed
M(sto, r"""
public static @RES@ regrant0(java.util.UUID admin, String by, String id, String side) {
  String[] pv = (String[]) PREVIEW.get(admin);
  long now = System.currentTimeMillis();
  if (pv == null || !pv[0].equals(id) || !pv[1].equals(side) || now > Long.parseLong(pv[3])) return new @RES@(false, "Run /ahadmin regrant " + id + " " + side + " first (the preview), then confirm within 60 s.");
  @BD@ r = get(id);
  java.nio.file.Path arch = null;
  if (r == null && ARCH.get(id) instanceof @BD@) r = (@BD@) ARCH.get(id);
  if (r == null) {
    arch = findArchived(id);
    if (arch != null) { try { r = @PKG@.AhRec.parse(@PKG@.AhCfg.readText(arch)); } catch (Throwable t) { r = null; } }
  }
  if (r == null) return new @RES@(false, "No record #" + id + ".");
  if (@PKG@.AhRec.readOnly(r)) return new @RES@(false, "#" + id + " needs a newer SkyyAuctions - regrant refused.");
  long rev = @PKG@.AhRec.lng(r, "rev", 0L);
  if (!String.valueOf(rev).equals(pv[2])) return new @RES@(false, "#" + id + " changed since your preview - run the preview again.");
  String f = @PKG@.AhRec.claimField(r, side);
  String cur = @PKG@.AhRec.claim(r, f);
  if (!"CLAIMED".equals(cur)) return new @RES@(false, "The " + side + " claim of #" + id + " is " + cur + ", not CLAIMED - nothing to regrant.");
  long qty = Long.parseLong(pv[4]);
  @BD@ next = @PKG@.AhRec.next(r);
  @PKG@.AhRec.setClaim(next, f, "OWED");
  boolean item = !f.equals("sellerCoins");
  if (item) @PKG@.AhRec.subw(next, "claims").put(side + "ItemQty", new org.bson.BsonInt64(qty));
  next.put("closed", org.bson.BsonBoolean.FALSE);
  next.put("closedAt", new org.bson.BsonInt64(0L));
  org.bson.BsonArray rg = new org.bson.BsonArray();
  try { @BV@ rv = (@BV@) r.get("regrants"); if (rv != null && rv.isArray()) rg = rv.asArray().clone(); } catch (Throwable t) { }
  @BD@ e = new @BD@();
  e.put("side", new org.bson.BsonString(side));
  e.put("by", new org.bson.BsonString(by == null ? "admin" : by));
  e.put("at", new org.bson.BsonInt64(now));
  e.put("qty", new org.bson.BsonInt64(item ? qty : 0L));
  rg.add(e);
  next.put("regrants", rg);
  if (!write(next)) return new @RES@(false, "Could not write #" + id + " - nothing changed.");
  LIVE.put(id, next);
  STACKS.remove(id);
  DIRTY.remove(id);
  ARCH.remove(id);
  PREVIEW.remove(admin);
  if (arch != null) {
    try { moveFile(arch, freeName(arch.getParent(), id, rev)); }
    catch (Throwable t) { @PKG@.AhUtil.warn("regrant #" + id + ": could not rename the archived copy (only listings/ is loaded, so this is harmless): " + t); }
  }
  @PKG@.AhLog.log("REGRANT", id, "side=" + side + " claim=" + f + " qty=" + (item ? qty : 0L) + " by=" + @PKG@.AhUtil.tok(by));
  String nm = @PKG@.AhRec.str(r, "name", "an item");
  @RES@ ok = new @RES@(true, "Regranted #" + id + " " + side + ": " + f + " is OWED again" + (item ? " (qty " + qty + ")" : " (" + @PKG@.AhUtil.fmt(@PKG@.AhRec.subLng(r, "sale", "net", 0L)) + " coins)") + ".");
  try { ok.otherUuid = java.util.UUID.fromString(@PKG@.AhRec.subStr(r, side, "uuid", "")); } catch (Throwable t) { ok.otherUuid = null; }
  if (ok.otherUuid != null) { ok.notifyUuid = ok.otherUuid; ok.notifyMsg = "[Auction House] An admin restored a claim for you: " + nm + " - /ah claim (profile " + @PKG@.AhRec.subStr(r, side, "profile", "?") + ")."; }
  return ok;
}""")
# ---- join notices: mark every unnoticed sale / expiry / removal of any of the player's profiles
M(sto, r"""
public static java.util.ArrayList notices0(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  StringBuilder lines = new StringBuilder();
  String us = u.toString();
  java.util.ArrayList docs = new java.util.ArrayList(LIVE.values());
  java.util.Collections.sort(docs, new @PKG@.AhSort(4));
  for (int i = 0; i < docs.size(); i++) {
    @BD@ r = (@BD@) docs.get(i);
    if (!us.equals(@PKG@.AhRec.subStr(r, "seller", "uuid", "")) || @PKG@.AhRec.readOnly(r)) continue;
    String s = @PKG@.AhRec.state(r);
    if (!("SOLD".equals(s) || "EXPIRED".equals(s) || "REMOVED".equals(s))) continue;
    if (@PKG@.AhRec.subBool(r, "noticed", "seller", false)) continue;
    String id = @PKG@.AhRec.id(r);
    @BD@ next = @PKG@.AhRec.next(r);
    @PKG@.AhRec.subw(next, "noticed").put("seller", org.bson.BsonBoolean.TRUE);
    if (commit(next)) lines.append(@PKG@.AhLog.line("NOTICE", id, "uuid=" + us + " state=" + s)).append('\n');
    String prof = @PKG@.AhRec.subStr(r, "seller", "profile", "");
    String pp = prof.length() > 0 ? " (profile " + prof + ")" : "";
    String nm = @PKG@.AhRec.str(r, "name", "an item");
    if ("SOLD".equals(s)) out.add(nm + " sold to " + @PKG@.AhRec.subStr(r, "buyer", "name", "someone") + " for " + @PKG@.AhUtil.fmt(@PKG@.AhRec.lng(r, "price", 0L)) + " coins" + pp + ". /ah claim to collect.");
    else if ("EXPIRED".equals(s)) out.add("Your listing of " + nm + " expired" + pp + ". /ah claim to get it back.");
    else out.add("An admin removed your listing of " + nm + ": " + @PKG@.AhRec.subStr(r, "removed", "reason", "no reason given") + pp + ". /ah claim to get it back.");
  }
  if (lines.length() > 0) @PKG@.AhLog.append(lines.toString());
  return out;
}""")
M(sto, r"""
public static boolean retryDirty0() {
  boolean all = true;
  java.util.Iterator it = new java.util.ArrayList(DIRTY.keySet()).iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    @BD@ d = (@BD@) DIRTY.get(id);
    if (d == null) continue;
    if (write(d)) {
      DIRTY.remove(id);
      @PKG@.AhLog.log("WRITE-RETRY-OK", id, "rev=" + @PKG@.AhRec.lng(d, "rev", 0L));
      if (@PKG@.AhRec.bool(d, "closed", false)) { if (archiveMove(d)) ARCH.remove(id); else ARCH.put(id, d); }
    } else all = false;
  }
  it = new java.util.ArrayList(ARCH.keySet()).iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    if (LIVE.containsKey(id)) { ARCH.remove(id); continue; }
    if (DIRTY.containsKey(id)) continue;
    @BD@ d = (@BD@) ARCH.get(id);
    if (d != null && archiveMove(d)) ARCH.remove(id);
  }
  return all;
}""")
# ---- start-up restore (inside the lock, right after load): a WRITE-FAILED / PAY-FAILED line carries the record version memory kept.
# If that copy is NEWER (higher rev) than the listing file that was loaded, the write never landed before the server stopped (a crash,
# or a stop while the write kept failing): the copy is written back, exactly as the tick's retry would have done. Revs only go up and
# ids are never reused, so an older copy (a later write landed) is ignored; a listing already closed and archived is not in LIVE and
# is left alone - except a NOT closed copy newer than an archived one (PAY-FAILED after the closing CLAIMED write landed: the refused
# pay's roll-back to OWED had not been saved), which reopens it the way regrant does (the archived file is renamed, never overwritten).
# Returns how many were restored (listed in RESTORED for /ahadmin).
M(sto, r"""
public static int restoreFromLog0() {
  RESTORED.clear();
  java.util.HashMap best = new java.util.HashMap();
  java.util.ArrayList files = @PKG@.AhLog.logFiles();
  for (int f = 0; f < files.size(); f++) {
    java.util.List all = @PKG@.AhLog.readLines((java.nio.file.Path) files.get(f));
    for (int i = 0; i < all.size(); i++) {
      String l = (String) all.get(i);
      int at = l.indexOf(" doc=");
      if (at < 0) continue;
      String[] t = l.substring(0, at).split(" ");
      if (t.length < 3 || !(t[1].equals("WRITE-FAILED") || t[1].equals("PAY-FAILED")) || !t[2].startsWith("#")) continue;
      @BD@ d = null;
      try { d = @PKG@.AhRec.parse(l.substring(at + 5)); } catch (Throwable x) { d = null; }
      if (d == null) { @PKG@.AhUtil.warn("auctions.log: unreadable record copy on a " + t[1] + " line of " + t[2] + " - check that listing by hand"); continue; }
      String id = @PKG@.AhRec.id(d);
      if (id.length() == 0 || !t[2].equals("#" + id)) continue;
      @BD@ o = (@BD@) best.get(id);
      if (o == null || @PKG@.AhRec.lng(d, "rev", 0L) > @PKG@.AhRec.lng(o, "rev", 0L)) best.put(id, d);
    }
  }
  int n = 0;
  java.util.Iterator it = best.values().iterator();
  while (it.hasNext()) {
    @BD@ d = (@BD@) it.next();
    String id = @PKG@.AhRec.id(d);
    @BD@ cur = get(id);
    boolean fromArch = false;
    java.nio.file.Path af = null;
    if (cur == null && ARCH.get(id) instanceof @BD@) { cur = (@BD@) ARCH.get(id); fromArch = true; }
    if (cur == null) {
      af = findArchived(id);
      if (af != null) { try { cur = @PKG@.AhRec.parse(@PKG@.AhCfg.readText(af)); } catch (Throwable x) { cur = null; } }
      fromArch = cur != null;
    }
    if (cur == null) continue;
    long rv = @PKG@.AhRec.lng(d, "rev", 0L);
    long rc = @PKG@.AhRec.lng(cur, "rev", 0L);
    if (rv <= rc) continue;
    if (fromArch && @PKG@.AhRec.bool(d, "closed", false)) continue;
    if (@PKG@.AhRec.readOnly(cur) || @PKG@.AhRec.readOnly(d)) { @PKG@.AhUtil.warn("listing #" + id + " has a newer copy in auctions.log (rev " + rv + " > " + rc + ") but is read-only here - not restored, check it by hand"); continue; }
    boolean ok = commitForced(d);
    if (fromArch) {
      ARCH.remove(id);
      if (ok && af != null) {
        try { moveFile(af, freeName(af.getParent(), id, rc)); }
        catch (Throwable x) { @PKG@.AhUtil.warn("restore #" + id + ": could not rename the archived copy (only listings/ is loaded, so this is harmless): " + x); }
      }
    }
    String what = "#" + id + " rev " + rc + " -> " + rv + " (" + @PKG@.AhRec.state(d) + ", claims sc " + @PKG@.AhRec.claim(d, "sellerCoins") + " si " + @PKG@.AhRec.claim(d, "sellerItem") + " bi " + @PKG@.AhRec.claim(d, "buyerItem") + (@PKG@.AhRec.bool(d, "closed", false) ? ", closed" : "") + ")" + (ok ? "" : " - still not saved, the tick retries");
    @PKG@.AhLog.log("WRITE-RESTORED", id, "rev=" + rv + " was=" + rc + " state=" + @PKG@.AhRec.state(d) + " saved=" + ok);
    @PKG@.AhUtil.warn("restored listing " + what + " from the auctions.log copy of a write that had not landed before the last stop");
    RESTORED.add(what);
    n++;
  }
  return n;
}""")
# ---- synchronized wrappers: the ONE lock (javassist: one call per synchronized block)
M(sto, r"""
public static @RES@ list(@PLA@ p, @REF@ ref, @ST@ st, java.util.UUID u, String key, String name, String prof, int sec, int slot, String sig, long price, int durIdx) {
  synchronized (@PKG@.AhStore.class) { return list0(p, ref, st, u, key, name, prof, sec, slot, sig, price, durIdx); }
}""")
M(sto, r"""
public static @RES@ buy(@PLA@ p, java.util.UUID u, String key, String name, String prof, String id, long shownPrice) {
  synchronized (@PKG@.AhStore.class) { return buy0(p, u, key, name, prof, id, shownPrice); }
}""")
M(sto, r"""
public static @RES@ cancel(@PLA@ p, java.util.UUID u, String key, String id) {
  synchronized (@PKG@.AhStore.class) { return cancel0(p, u, key, id); }
}""")
M(sto, r"""
public static @RES@ claimCoins(java.util.UUID u, String key, String id) {
  synchronized (@PKG@.AhStore.class) { return claimCoins0(u, key, id); }
}""")
M(sto, r"""
public static @RES@ claimItem(@PLA@ p, java.util.UUID u, String key, String id, boolean seller) {
  synchronized (@PKG@.AhStore.class) { return claimItem0(p, u, key, id, seller); }
}""")
M(sto, r"""
public static java.util.ArrayList expireDue(long now) {
  synchronized (@PKG@.AhStore.class) { return expireDue0(now); }
}""")
M(sto, r"""
public static @RES@ adminRemove(String by, String id, String reason) {
  synchronized (@PKG@.AhStore.class) { return adminRemove0(by, id, reason); }
}""")
M(sto, r"""
public static @RES@ regrant(java.util.UUID admin, String by, String id, String side) {
  synchronized (@PKG@.AhStore.class) { return regrant0(admin, by, id, side); }
}""")
M(sto, r"""
public static java.util.ArrayList notices(java.util.UUID u) {
  synchronized (@PKG@.AhStore.class) { return notices0(u); }
}""")
M(sto, r"""
public static boolean retryDirty() {
  synchronized (@PKG@.AhStore.class) { return retryDirty0(); }
}""")
M(sto, r"""
public static int restoreFromLog() {
  synchronized (@PKG@.AhStore.class) { return restoreFromLog0(); }
}""")
# /ahadmin reload inside the one lock: every trade (also inside it) sees the whole old or the whole new config, never a mix
M(sto, r"""
public static String reloadCfg() {
  synchronized (@PKG@.AhStore.class) { return @PKG@.AhCfg.load(); }
}""")
# ---- claim all (spec 6.6): every coin claim, then items oldest first until the first FULL; each claim is its own locked step
M(sto, r"""
public static @RES@ claimAll(@PLA@ p, java.util.UUID u, String key) {
  if (@PKG@.AhUtil.busy(u)) return new @RES@(false, "Your profile is still loading - try again in a moment.");
  java.util.ArrayList rows = rowsFor(key);
  long coins = 0L;
  int items = 0, waiting = 0;
  boolean full = false, save = false, alert = false;
  String err = null;
  for (int i = 0; i < rows.size(); i++) {
    String[] x = (String[]) rows.get(i);
    if (!x[1].equals("coins")) continue;
    if (!@PKG@.Coins.ready()) { err = "coins need SkyyCoins, which is not loaded"; continue; }
    @RES@ r = claimCoins(u, key, x[0]);
    if (r.ok) coins += r.coins; else { err = r.msg; if (r.alert) alert = true; }
  }
  for (int i = 0; i < rows.size(); i++) {
    String[] x = (String[]) rows.get(i);
    if (!x[1].equals("sitem") && !x[1].equals("bitem")) continue;
    if (full) { waiting++; continue; }
    @RES@ r = claimItem(p, u, key, x[0], x[1].equals("sitem"));
    if (r.saveNeeded) save = true;
    if (r.code == 2) items++;
    else if (r.code == 1) { items++; waiting++; full = true; }
    else if (r.code == 0) { waiting++; full = true; }
    else { err = r.msg; if (r.alert) alert = true; }
  }
  @RES@ o = new @RES@(coins > 0L || items > 0, "");
  o.coins = coins;
  o.items = items;
  o.saveNeeded = save;
  o.alert = alert;
  o.kept = waiting > 0;
  if (coins == 0L && items == 0 && waiting == 0 && err == null) { o.msg = "Nothing to claim on this profile."; return o; }
  StringBuilder sb = new StringBuilder();
  if (coins > 0L || items > 0) {
    sb.append("Claimed ");
    if (coins > 0L) sb.append(@PKG@.AhUtil.fmt(coins)).append(" coins");
    if (coins > 0L && items > 0) sb.append(" and ");
    if (items > 0) sb.append(items).append(items == 1 ? " item" : " items");
    sb.append(".");
  }
  if (waiting > 0) sb.append(sb.length() > 0 ? " " : "").append(waiting).append(waiting == 1 ? " item waits" : " items wait").append(" - your inventory is full.");
  if (err != null) sb.append(sb.length() > 0 ? " " : "").append("Not claimed: ").append(err);
  o.msg = sb.toString();
  return o;
}""")
# ---- R8: after the lock, queue a save of the player (see the module docstring for why copyEntity and the world guard)
if SAVE_OK:
    M(sto, r"""
public static void forceSave(@PLA@ p, @REF@ ref, @ST@ st) {
  if (p == null) return;
  try { p.markNeedsSave(); } catch (Throwable t) { }
  if (!@PKG@.AhCfg.FORCE_SAVE || SAVE_BROKEN || ref == null || st == null) return;
  try {
    @WLD@ w = ((@ES@) st.getExternalData()).getWorld();
    if (w == null || w.isSavingLocked() || !w.getWorldConfig().isSavingPlayers()) return;
    @HOLDER@ h = st.copyEntity(ref);
    if (h == null) return;
    p.saveConfig(w, h, true);
  } catch (Throwable t) {
    SAVE_BROKEN = true;
    @PKG@.AhUtil.warn("forced save skipped from now on (markNeedsSave stays; set forceSaveAfterTrade=false to silence this): " + t);
  }
}""")
else:
    M(sto, r"""
public static void forceSave(@PLA@ p, @REF@ ref, @ST@ st) {
  if (p == null) return;
  try { p.markNeedsSave(); } catch (Throwable t) { }
}""")
M(sto, r"""
public static void publishCount() {
  try { @PKG@.AhUtil.bridge().put("auction:count", Long.valueOf((long) countActive(System.currentTimeMillis()))); } catch (Throwable t) { }
}""")
M(sto, r"""
public static void publishClaims(java.util.UUID u) {
  if (u == null) return;
  try { long[] o = owedFor(@PKG@.AhUtil.pkey(u)); @PKG@.AhUtil.bridge().put("auction:claims:" + u, Integer.valueOf((int) o[0])); } catch (Throwable t) { }
}""")
M(sto, r"""
public static void tell(java.util.UUID u, String msg) {
  if (u == null || msg == null) return;
  try { @PR@ o = @UNI@.get().getPlayer(u); if (o != null) o.sendMessage(@MSG@.raw(msg)); } catch (Throwable t) { }
}""")
# everything a trade does AFTER the lock (R1): forced save, chat to the other player, bridge republishes
M(sto, r"""
public static void afterTrade(@RES@ r, @PR@ pr, @PLA@ p, @REF@ ref, @ST@ st) {
  if (r == null) return;
  if (r.saveNeeded) forceSave(p, ref, st);
  if (r.notifyUuid != null && r.notifyMsg != null) tell(r.notifyUuid, r.notifyMsg);
  publishCount();
  if (pr != null) publishClaims(pr.getUuid());
  if (r.otherUuid != null) publishClaims(r.otherUuid);
}""")

# ================= AhLowestBinFn: bridge auction:fn:lowestBin =================
lfn.addInterface(pool.get("java.util.function.Function"))
C(lfn, "public AhLowestBinFn() { }")
M(lfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof String)) return null;
    long[] r = @PKG@.AhStore.lowestBin((String) o, null, System.currentTimeMillis());
    return r[0] > 0L ? Long.valueOf(r[0]) : null;
  } catch (Throwable t) { return null; }
}""")

# ================= AhPage: the one inline page (Browse / Item / Create / Manage) =================
def _bs(bg, hov, prs, fg, size=15):
    lab = "LabelStyle: (FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)"
    return ("Style: TextButtonStyle(Default: (Background: %s, %s), Hovered: (Background: %s, %s), Pressed: (Background: %s, %s));"
            % (bg, lab % (size, fg), hov, lab % (size, "#ffffff"), prs, lab % (size, "#ffffff")))


BS       = _bs("#5a4420", "#8a6a30", "#3a2a10", "#ffe9c9")
BS_ON    = _bs("#e0b060", "#f0c878", "#b08040", "#1a1000").replace("TextColor: #ffffff", "TextColor: #1a1000")
BS_GREEN = _bs("#2f5a34", "#3f7a46", "#1f3a22", "#dfffe0", 16)
BS_RED   = _bs("#6a2e2e", "#8a4040", "#4a1e1e", "#ffe0e0")
BS_BLUE  = _bs("#1d3a5f", "#2f5a8f", "#10243c", "#dfeeff")
for _s in (BS, BS_ON, BS_GREEN, BS_RED, BS_BLUE):
    assert '"' not in _s and "{" not in _s and "\\" not in _s

F(page, "public static final String BS = %s;" % jstr(BS))
F(page, "public static final String BS_ON = %s;" % jstr(BS_ON))
F(page, "public static final String BS_GREEN = %s;" % jstr(BS_GREEN))
F(page, "public static final String BS_RED = %s;" % jstr(BS_RED))
F(page, "public static final String BS_BLUE = %s;" % jstr(BS_BLUE))
F(page, 'public static final String[] SORT_NAME = new String[] { "Lowest price", "Highest price", "Ending soon", "Newest" };')
for fld in ("public String view;", "public String key;", "public int cat;", "public int sort;", "public int rar;", "public String query;",
            "public int browsePage;", "public String[] rowIds;", "public String detailId;", "public long detailPrice;",
            "public String armAct;", "public String armId;", "public long armPrice;", "public long armUntil;",
            "public int invPage;", "public int pickSec;", "public int pickSlot;", "public String pickSig;",
            "public int[] cellSec;", "public int[] cellSlot;", "public String[] cellSig;",
            "public String priceText;", "public long previewPrice;", "public int durIdx;",
            "public int managePage;", "public String[] mIds;", "public String[] mKinds;",
            "public String status;", "public int statusKind;"):
    F(page, fld)
C(page, r"""
public AhPage(@PR@ pr, String view) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view == null ? "browse" : view;
  this.key = @PKG@.AhUtil.pkey(pr.getUuid());
  this.cat = 0; this.sort = 0; this.rar = 0; this.query = ""; this.browsePage = 0;
  this.rowIds = new String[8];
  this.detailId = null; this.detailPrice = -1L;
  this.armAct = null; this.armId = null; this.armPrice = 0L; this.armUntil = 0L;
  this.invPage = 0; this.pickSec = -1; this.pickSlot = -1; this.pickSig = "";
  this.cellSec = new int[36]; this.cellSlot = new int[36]; this.cellSig = new String[36];
  this.priceText = ""; this.previewPrice = -1L; this.durIdx = @PKG@.AhCfg.DEF_DUR;
  this.managePage = 0; this.mIds = new String[8]; this.mKinds = new String[8];
  this.status = ""; this.statusKind = 0;
}""")
# every binding of the Browse view carries the search text, every binding of the Create view the price text
M(page, r"""
public @EVD@ evd(String a) {
  @EVD@ d = @EVD@.of("a", a);
  if ("browse".equals(this.view)) d = d.append("@AhSearch", "#SkyyAhSearch.Value");
  else if ("create".equals(this.view)) d = d.append("@AhPrice", "#SkyyAhPrice.Value");
  return d;
}""")
M(page, r"""
public static void sp(@UCB@ b, String parent, int w, int h) {
  if (w > 0) b.appendInline(parent, "Label { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; }");
  else b.appendInline(parent, "Label { Anchor: (Height: " + h + "); Text: \"\"; }");
}""")
# a label shell (text always through set) - w <= 0 = full width of a Top layout
M(page, r"""
public static String lab(String id, int w, int h, int size, boolean bold, String color, String align, boolean wrap) {
  String a = w > 0 ? "Width: " + w + ", Height: " + h : "Height: " + h;
  return "Label" + (id != null ? " #" + id : "") + " { Anchor: (" + a + "); Text: \"\"; Style: (FontSize: " + size + (bold ? ", RenderBold: true" : "") + ", TextColor: " + color + (align != null ? ", HorizontalAlignment: " + align : "") + ", VerticalAlignment: Center" + (wrap ? ", Wrap: true" : "") + "); }";
}""")
M(page, r"""
public static void txt(@UCB@ b, String parent, String id, int w, int h, int size, boolean bold, String color, String align, boolean wrap, String text) {
  b.appendInline(parent, lab(id, w, h, size, bold, color, align, wrap));
  if (id != null) b.set("#" + id + ".Text", text == null ? "" : text);
}""")
M(page, r"""
public void btn(@UCB@ b, @UEB@ ev, String parent, String id, int w, int h, String text, String style, String action) {
  b.appendInline(parent, "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; " + style + " }");
  b.set("#" + id + ".Text", text == null ? "" : text);
  ev.addEventBinding(@BT@.Activating, "#" + id, evd(action));
}""")
M(page, r"""
public static String icon(String itemId, int box, int h, int size) {
  if (!@PKG@.AhUtil.isId(itemId)) return "Group { Anchor: (Width: " + box + ", Height: " + h + "); }";
  int l = (box - size) / 2;
  int t = (h - size) / 2;
  return "Group { Anchor: (Width: " + box + ", Height: " + h + "); ItemIcon { Anchor: (Width: " + size + ", Height: " + size + ", Left: " + l + ", Top: " + t + "); ItemId: \"" + itemId + "\"; } }";
}""")
# spec 7.1: a Confirm acts only for the action, listing and price it was armed for, before its deadline
M(page, r"""
public static boolean armOk(String act, String id, long price, long until, String wantAct, String wantId, long wantPrice, long now) {
  if (act == null || id == null || wantAct == null || wantId == null) return false;
  return act.equals(wantAct) && id.equals(wantId) && price == wantPrice && now < until;
}""")
M(page, r"""
public void arm(String act, String id, long price, long now) {
  this.armAct = act; this.armId = id; this.armPrice = price; this.armUntil = now + @PKG@.AhCfg.CONFIRM_MS;
}""")
M(page, r"""
public void say(String s, int kind) { this.status = s == null ? "" : s; this.statusKind = kind; }""")
M(page, r"""
public boolean armedFor(String act, String id, long price) {
  return armOk(this.armAct, this.armId, this.armPrice, this.armUntil, act, id, price, System.currentTimeMillis());
}""")
# ---- shared top (50 + 50 + 26 = 126)
M(page, r"""
public void renderTop(@UCB@ b, @UEB@ ev, java.util.UUID u, @PLA@ p) {
  b.appendInline("#SkyyAh", "Group #SkyyAhTop { Anchor: (Height: 50); LayoutMode: Left; }");
  b.appendInline("#SkyyAhTop", "Label #SkyyAhTitle { Anchor: (Width: 420, Height: 50); Text: \"Auction House\"; Style: (FontSize: 26, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }");
  sp(b, "#SkyyAhTop", 260, 50);
  String purse;
  if (!@PKG@.Coins.ready()) purse = "Purse: SkyyCoins not loaded";
  else { long pv = @PKG@.Coins.get(u); purse = pv >= 0L ? "Purse: " + @PKG@.AhUtil.fmt(pv) + " coins" : "Purse: coin bank error"; }
  String pn = @PKG@.AhUtil.profName(u);
  if (pn.length() > 0) purse = purse + " - profile " + pn;
  txt(b, "#SkyyAhTop", "SkyyAhPurse", 400, 50, 17, true, "#ffd766", "End", false, purse);
  b.appendInline("#SkyyAh", "Group #SkyyAhNav { Anchor: (Height: 50); LayoutMode: Left; }");
  boolean br = "browse".equals(this.view) || "item".equals(this.view);
  btn(b, ev, "#SkyyAhNav", "SkyyAhNavBrowse", 200, 42, "Browse", br ? BS_ON : BS, "nav:browse");
  sp(b, "#SkyyAhNav", 10, 42);
  btn(b, ev, "#SkyyAhNav", "SkyyAhNavCreate", 200, 42, "Create BIN", "create".equals(this.view) ? BS_ON : BS, "nav:create");
  sp(b, "#SkyyAhNav", 10, 42);
  long[] ow = @PKG@.AhStore.owedFor(this.key);
  btn(b, ev, "#SkyyAhNav", "SkyyAhNavManage", 200, 42, ow[0] > 0L ? "Manage (" + ow[0] + ")" : "Manage", "manage".equals(this.view) ? BS_ON : BS, "nav:manage");
  sp(b, "#SkyyAhNav", 260, 42);
  btn(b, ev, "#SkyyAhNav", "SkyyAhNavClose", 200, 42, "Close", BS_RED, "close");
  String ban = "";
  if (@PKG@.AhCfg.PAUSED) ban = "The Auction House is paused by an admin - no new listings or buys. Cancel and claims still work.";
  else if (!@PKG@.Coins.ready()) ban = "Trading needs SkyyCoins - you can look, but not list or buy.";
  else if (@PKG@.AhUtil.busy(u)) ban = "Your profile is still loading - try again in a moment.";
  else if (@PKG@.AhUtil.deny(u) != null) ban = "You cannot trade on the Auction House: " + @PKG@.AhUtil.deny(u);
  else if (@PKG@.AhCfg.BLOCK_CREATIVE && @PKG@.AhStore.creative(p)) ban = "Creative mode: you can browse and claim, but not list or buy.";
  txt(b, "#SkyyAh", "SkyyAhBanner", 0, 26, 15, true, "#ffb070", "Center", false, ban);
}""")
# ---- Browse (46 + 46 + 22 + 8 x 62 + 46 = 656, + top 126 + status 30 = 812)
M(page, r"""
public java.util.ArrayList results(long now) {
  java.util.ArrayList all = @PKG@.AhStore.active(now);
  java.util.ArrayList out = new java.util.ArrayList();
  @PKG@.AhItem.tiers();
  String cat = @PKG@.AhItem.CAT[this.cat < 0 || this.cat > 6 ? 0 : this.cat];
  int tv = -1;
  if (this.rar > 0 && this.rar <= @PKG@.AhItem.TIER_VAL.length) tv = @PKG@.AhItem.TIER_VAL[this.rar - 1];
  String q = this.query == null ? "" : this.query.trim().toLowerCase();
  for (int i = 0; i < all.size(); i++) {
    @BD@ r = (@BD@) all.get(i);
    if (!"ALL".equals(cat) && !cat.equals(@PKG@.AhRec.str(r, "category", "MISC"))) continue;
    if (tv >= 0 && @PKG@.AhItem.qValue((int) @PKG@.AhRec.subLng(r, "item", "quality", 0L)) != tv) continue;
    if (q.length() > 0 && @PKG@.AhRec.str(r, "search", "").indexOf(q) < 0) continue;
    out.add(r);
  }
  java.util.Collections.sort(out, new @PKG@.AhSort(this.sort));
  return out;
}""")
M(page, r"""
public void renderBrowse(@UCB@ b, @UEB@ ev, java.util.UUID u, long now) {
  b.appendInline("#SkyyAh", "Group #SkyyAhCats { Anchor: (Height: 46); LayoutMode: Left; }");
  for (int i = 0; i < 7; i++) {
    if (i > 0) sp(b, "#SkyyAhCats", 5, 40);
    btn(b, ev, "#SkyyAhCats", "SkyyAhCat" + i, 148, 40, @PKG@.AhItem.CAT_LABEL[i], i == this.cat ? BS_ON : BS, "cat:" + i);
  }
  b.appendInline("#SkyyAh", "Group #SkyyAhFilt { Anchor: (Height: 46); LayoutMode: Left; }");
  b.appendInline("#SkyyAhFilt", "Group #SkyyAhSearchBox { Anchor: (Width: 330, Height: 40); Background: #16263a; }");
  b.appendInline("#SkyyAhSearchBox", "TextField #SkyyAhSearch { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 40; PlaceholderText: \"Search items or sellers...\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
  if (this.query != null && this.query.length() > 0) b.set("#SkyyAhSearch.Value", this.query);
  ev.addEventBinding(@BT@.Validating, "#SkyyAhSearch", evd("search"), false);
  sp(b, "#SkyyAhFilt", 6, 40);
  btn(b, ev, "#SkyyAhFilt", "SkyyAhSearchGo", 100, 40, "Search", BS_BLUE, "search");
  sp(b, "#SkyyAhFilt", 6, 40);
  btn(b, ev, "#SkyyAhFilt", "SkyyAhSearchClr", 90, 40, "Clear", BS, "clear");
  sp(b, "#SkyyAhFilt", 6, 40);
  btn(b, ev, "#SkyyAhFilt", "SkyyAhSort", 220, 40, "Sort: " + SORT_NAME[this.sort < 0 || this.sort > 3 ? 0 : this.sort], BS, "sort");
  sp(b, "#SkyyAhFilt", 6, 40);
  @PKG@.AhItem.tiers();
  if (this.rar > @PKG@.AhItem.TIER_NAME.length) this.rar = 0;
  btn(b, ev, "#SkyyAhFilt", "SkyyAhRar", 190, 40, "Rarity: " + (this.rar == 0 ? "Any" : @PKG@.AhItem.TIER_NAME[this.rar - 1]), BS, "rar");
  sp(b, "#SkyyAhFilt", 6, 40);
  btn(b, ev, "#SkyyAhFilt", "SkyyAhRefresh", 100, 40, "Refresh", BS_BLUE, "refresh");
  b.appendInline("#SkyyAh", "Group #SkyyAhHead { Anchor: (Height: 22); LayoutMode: Left; }");
  txt(b, "#SkyyAhHead", "SkyyAhHeadItem", 448, 22, 13, true, "#8fa4b8", null, false, "Item");
  txt(b, "#SkyyAhHead", "SkyyAhHeadSeller", 170, 22, 13, true, "#8fa4b8", null, false, "Seller");
  txt(b, "#SkyyAhHead", "SkyyAhHeadPrice", 170, 22, 13, true, "#8fa4b8", null, false, "Price");
  txt(b, "#SkyyAhHead", "SkyyAhHeadTime", 110, 22, 13, true, "#8fa4b8", null, false, "Ends in");
  java.util.ArrayList list = results(now);
  int total = list.size();
  int pages = (total + 7) / 8;
  if (pages < 1) pages = 1;
  if (this.browsePage >= pages) this.browsePage = pages - 1;
  if (this.browsePage < 0) this.browsePage = 0;
  for (int i = 0; i < 8; i++) this.rowIds[i] = null;
  if (total == 0) {
    String e = (this.query != null && this.query.length() > 0) ? "No match for '" + this.query + "'" : "Nothing listed here yet - be the first: Create BIN";
    txt(b, "#SkyyAh", "SkyyAhEmpty", 0, 496, 20, true, "#9fb8cc", "Center", false, e);
  } else {
    String us = u.toString();
    for (int i = 0; i < 8; i++) {
      int idx = this.browsePage * 8 + i;
      if (idx >= total) { sp(b, "#SkyyAh", 0, 62); continue; }
      @BD@ r = (@BD@) list.get(idx);
      String rid = @PKG@.AhRec.id(r);
      this.rowIds[i] = rid;
      String iid = @PKG@.AhRec.subStr(r, "item", "id", "");
      long qty = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
      int qi = (int) @PKG@.AhRec.subLng(r, "item", "quality", 0L);
      String row = "#SkyyAhRow" + i;
      b.appendInline("#SkyyAh", "Group #SkyyAhRow" + i + " { Anchor: (Height: 58); LayoutMode: Left; Background: #142030(0.9); }");
      b.appendInline(row, icon(iid, 60, 58, 50));
      sp(b, row, 8, 58);
      b.appendInline(row, "Group #SkyyAhRowTxt" + i + " { Anchor: (Width: 380, Height: 58); LayoutMode: Top; }");
      txt(b, "#SkyyAhRowTxt" + i, "SkyyAhRowName" + i, 0, 32, 17, true, @PKG@.AhItem.qColor(qi), null, false, @PKG@.AhRec.str(r, "name", iid));
      String rf = @PKG@.AhItem.reforge(@PKG@.AhRec.sub(@PKG@.AhRec.sub(r, "item"), "meta"));
      String blk = @PKG@.AhItem.blockedReason(iid);
      String sub = "x" + qty + " - " + @PKG@.AhItem.qName(qi) + (rf != null ? " - " + rf : "") + (blk != null ? " - OFF THE MARKET" : "");
      txt(b, "#SkyyAhRowTxt" + i, "SkyyAhRowSub" + i, 0, 24, 13, false, blk != null ? "#ff7070" : "#9fb8cc", null, false, sub);
      String sn = @PKG@.AhRec.subStr(r, "seller", "name", "?");
      String tag = "";
      String tc = "#dfe9f5";
      if (this.key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) { tag = " (yours)"; tc = "#9fe8a2"; }
      else if (us.equals(@PKG@.AhRec.subStr(r, "seller", "uuid", ""))) { tag = " (your other profile)"; tc = "#ffd070"; }
      if (blk != null) tc = "#ff7070";
      txt(b, row, "SkyyAhRowSeller" + i, 170, 58, 14, false, tc, null, true, sn + tag);
      long price = @PKG@.AhRec.lng(r, "price", 0L);
      String pt = @PKG@.AhUtil.fmt(price) + (qty > 1L ? " (" + @PKG@.AhUtil.fmt(@PKG@.AhUtil.ceilDiv(price, qty)) + " each)" : "");
      txt(b, row, "SkyyAhRowPrice" + i, 170, 58, 15, true, "#ffd36a", null, true, pt);
      txt(b, row, "SkyyAhRowTime" + i, 110, 58, 14, false, "#cfe3ff", null, false, @PKG@.AhUtil.timeLeft(@PKG@.AhRec.lng(r, "endsAt", 0L) - now));
      b.appendInline(row, "Group #SkyyAhRowBtn" + i + " { Anchor: (Width: 110, Height: 58); }");
      b.appendInline("#SkyyAhRowBtn" + i, "TextButton #SkyyAhRowView" + i + " { Anchor: (Left: 6, Top: 7, Width: 100, Height: 44); Text: \"View\"; " + BS_BLUE + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyAhRowView" + i, evd("view:" + i));
      sp(b, "#SkyyAh", 0, 4);
    }
  }
  b.appendInline("#SkyyAh", "Group #SkyyAhPager { Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 4); }");
  btn(b, ev, "#SkyyAhPager", "SkyyAhPrev", 180, 40, "< Prev", BS, "prev");
  txt(b, "#SkyyAhPager", "SkyyAhPageTxt", 700, 40, 16, true, "#cfe3ff", "Center", false, "Page " + (this.browsePage + 1) + " / " + pages + " - " + total + (total == 1 ? " listing" : " listings"));
  btn(b, ev, "#SkyyAhPager", "SkyyAhNext", 180, 40, "Next >", BS, "next");
}""")
# ---- Item view (560 + 60, + top 126 + status 30 = 776)
M(page, r"""
public void renderItem(@UCB@ b, @UEB@ ev, java.util.UUID u, long now) {
  @BD@ r = @PKG@.AhStore.get(this.detailId);
  boolean live = @PKG@.AhStore.buyable(r, now);
  b.appendInline("#SkyyAh", "Group #SkyyAhDBody { Anchor: (Height: 560); LayoutMode: Left; }");
  b.appendInline("#SkyyAhDBody", "Group #SkyyAhDLeft { Anchor: (Width: 220, Height: 560); }");
  b.appendInline("#SkyyAhDLeft", "ItemGrid #SkyyAhDGrid { Anchor: (Left: 20, Top: 10, Width: 180, Height: 180); SlotsPerRow: 1; AreItemsDraggable: false; InfoDisplay: None; Style: (SlotSize: 180, SlotIconSize: 140, SlotSpacing: 0); }");
  b.appendInline("#SkyyAhDBody", "Group #SkyyAhDRight { Anchor: (Width: 840, Height: 560); LayoutMode: Top; }");
  int qi = r == null ? 0 : (int) @PKG@.AhRec.subLng(r, "item", "quality", 0L);
  b.appendInline("#SkyyAhDRight", lab("SkyyAhDName", 0, 40, 22, true, @PKG@.AhItem.qColor(qi), null, false));
  b.appendInline("#SkyyAhDRight", "Label #SkyyAhDDesc { Anchor: (Height: 230); Text: \"\"; Style: (FontSize: 15, TextColor: #c9dff0, Wrap: true); }");
  for (int i = 0; i < 9; i++) b.appendInline("#SkyyAhDRight", lab("SkyyAhDFact" + i, 0, 28, 16, i == 4, i == 8 ? "#ffb070" : (i == 4 ? "#ffd36a" : "#dfe9f5"), null, false));
  String[] facts = new String[9];
  for (int i = 0; i < 9; i++) facts[i] = "";
  String cheaper = null;
  String nm = "";
  long price = -1L;
  if (r == null) {
    b.set("#SkyyAhDName.Text", "This listing is gone");
    b.set("#SkyyAhDDesc.Text", "It was bought, cancelled or it expired. Go back to the results.");
    this.detailPrice = -1L;
  } else {
    price = @PKG@.AhRec.lng(r, "price", 0L);
    this.detailPrice = price;
    nm = @PKG@.AhRec.str(r, "name", "?");
    @IS@ st = @PKG@.AhStore.stackOf(r);
    @BD@ meta = @PKG@.AhRec.sub(@PKG@.AhRec.sub(r, "item"), "meta");
    if (st != null) {
      java.util.ArrayList slots = new java.util.ArrayList();
      slots.add(new @IGS@(st));
      b.set("#SkyyAhDGrid.Slots", slots);
    }
    boolean named = false;
    if (st != null && @PKG@.AhCfg.SPANS) {
      try {
        @MSG@ dn = st.getDisplayName();
        if (dn != null && @PKG@.AhUtil.plain(dn).trim().length() > 0) { b.set("#SkyyAhDName.TextSpans", dn); named = true; }
        @MSG@ dd = st.getDisplayDescription();
        if (dd != null && @PKG@.AhUtil.plain(dd).trim().length() > 0) b.set("#SkyyAhDDesc.TextSpans", dd);
        else b.set("#SkyyAhDDesc.Text", "");
      } catch (Throwable t) { named = false; }
    }
    if (!named) {
      b.set("#SkyyAhDName.Text", nm);
      String d = "";
      if (st != null) { try { d = @PKG@.AhUtil.plain(st.getDisplayDescription()); } catch (Throwable t) { d = ""; } }
      String rl = @PKG@.AhItem.rollsLine(meta);
      if (rl.length() > 0 && d.indexOf("Reforge") < 0) d = (d.length() > 0 ? d + "\n\n" : "") + rl;
      b.set("#SkyyAhDDesc.Text", d);
    }
    long qty = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
    @BD@ it = @PKG@.AhRec.sub(r, "item");
    double cd = @PKG@.AhRec.dbl(it, "durability", 0.0);
    double md = @PKG@.AhRec.dbl(it, "maxDurability", 0.0);
    String sk = @PKG@.AhRec.subStr(r, "seller", "key", "");
    facts[0] = "Rarity: " + @PKG@.AhItem.qName(qi);
    facts[1] = "Quantity: " + qty;
    facts[2] = md > 0.0 ? "Durability: " + Math.round(cd) + " / " + Math.round(md) : "Durability: -";
    facts[3] = "Seller: " + @PKG@.AhRec.subStr(r, "seller", "name", "?") + (this.key.equals(sk) ? " (you)" : "");
    facts[4] = "Price: " + @PKG@.AhUtil.fmt(price) + " coins" + (qty > 1L ? " - " + @PKG@.AhUtil.fmt(@PKG@.AhUtil.ceilDiv(price, qty)) + " each" : "");
    facts[5] = live ? "Ends in: " + @PKG@.AhUtil.timeLeft(@PKG@.AhRec.lng(r, "endsAt", 0L) - now) : "Ends in: ended";
    facts[6] = "Listed: " + @PKG@.AhUtil.ago(now - @PKG@.AhRec.lng(r, "createdAt", now));
    facts[7] = "Listing #" + @PKG@.AhRec.id(r);
    String iid = @PKG@.AhRec.subStr(r, "item", "id", "");
    long[] lo = @PKG@.AhStore.lowestBin(iid, @PKG@.AhRec.id(r), now);
    long each = @PKG@.AhUtil.ceilDiv(price, qty < 1L ? 1L : qty);
    String w = "";
    if (lo[0] > 0L && lo[0] < each) {
      cheaper = @PKG@.AhUtil.fmt(lo[0]);
      w = "A cheaper one is listed: " + cheaper + " each (" + lo[1] + " listed)" + (@PKG@.AhItem.hasRolls(meta) ? " - rolls are not compared" : "");
    }
    if (@PKG@.AhItem.isBag(iid)) w = w + (w.length() > 0 ? " - " : "") + "Contents not included.";
    facts[8] = w;
  }
  for (int i = 0; i < 9; i++) b.set("#SkyyAhDFact" + i + ".Text", facts[i]);
  b.appendInline("#SkyyAh", "Group #SkyyAhDAct { Anchor: (Height: 60); LayoutMode: Left; Padding: (Top: 5); }");
  String note = null;
  if (r == null) note = "This listing is no longer for sale.";
  else if (@PKG@.AhRec.readOnly(r)) note = "This listing needs a newer SkyyAuctions.";
  else if (!live) note = "This listing is no longer for sale.";
  boolean own = r != null && this.key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""));
  if (note == null && own) {
    if (armedFor("cancel", this.detailId, this.detailPrice)) {
      long fee = @PKG@.AhRec.subLng(r, "fee", "listing", 0L) + @PKG@.AhRec.subLng(r, "fee", "duration", 0L);
      txt(b, "#SkyyAhDAct", "SkyyAhDAsk", 420, 50, 15, true, "#ffd36a", null, true, @PKG@.AhCfg.CANCEL_REFUND ? "Cancel this listing? The fee is refunded." : "Cancel? The " + @PKG@.AhUtil.fmt(fee) + " coin fee is not refunded.");
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDConfirm", 180, 50, "Yes, cancel", BS_RED, "confirm");
      sp(b, "#SkyyAhDAct", 10, 50);
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDNo", 180, 50, "No", BS, "no");
      sp(b, "#SkyyAhDAct", 20, 50);
    } else {
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDCancel", 360, 50, "Cancel listing", BS_RED, "dcancel");
      sp(b, "#SkyyAhDAct", 450, 50);
    }
  } else if (note == null && u.toString().equals(@PKG@.AhRec.subStr(r, "seller", "uuid", "")) && !@PKG@.AhCfg.SAME_ACCOUNT) {
    note = "Listed by your profile " + @PKG@.AhRec.subStr(r, "seller", "profile", "") + " - you cannot buy from yourself.";
  } else if (note == null && @PKG@.AhItem.blockedReason(@PKG@.AhRec.subStr(r, "item", "id", "")) != null) {
    note = "Off the market (" + @PKG@.AhItem.blockedReason(@PKG@.AhRec.subStr(r, "item", "id", "")) + ") - it cannot be bought.";
  } else if (note == null) {
    long grace = @PKG@.AhRec.lng(r, "graceUntil", 0L);
    if (now < grace) {
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDBuy", 360, 50, "Buy (opens in " + ((grace - now + 999L) / 1000L) + " s)", BS, "buy");
      sp(b, "#SkyyAhDAct", 450, 50);
    } else if (armedFor("buy", this.detailId, this.detailPrice)) {
      String q = "Pay " + @PKG@.AhUtil.fmt(price) + " coins for " + nm + "?" + (cheaper != null ? " A cheaper one is listed at " + cheaper + " each." : "");
      txt(b, "#SkyyAhDAct", "SkyyAhDAsk", 420, 50, 15, true, "#ffd36a", null, true, q);
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDConfirm", 180, 50, "Confirm", BS_GREEN, "confirm");
      sp(b, "#SkyyAhDAct", 10, 50);
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDNo", 180, 50, "Cancel", BS, "no");
      sp(b, "#SkyyAhDAct", 20, 50);
    } else {
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDBuy", 360, 50, "Buy now - " + @PKG@.AhUtil.fmt(price) + " coins", BS_GREEN, "buy");
      sp(b, "#SkyyAhDAct", 450, 50);
    }
  }
  if (note != null) {
    txt(b, "#SkyyAhDAct", "SkyyAhDNote", 810, 50, 16, true, "#ffb070", null, true, note);
  }
  btn(b, ev, "#SkyyAhDAct", "SkyyAhDBack", 240, 50, "< Back to results", BS_BLUE, "back");
}""")
# ---- Create view (26 + 312 + 40 + 76 + 50 + 50 + 72 + 58 = 684, + top 126 + status 30 = 840)
M(page, r"""
public void renderCreate(@UCB@ b, @UEB@ ev, java.util.UUID u, @PLA@ p, long now) {
  txt(b, "#SkyyAh", "SkyyAhInvHead", 0, 26, 15, true, "#cfe3ff", null, false, "Pick an item from your inventory (hotbar, storage, backpack). The whole stack is listed - split stacks first.");
  java.util.ArrayList cells = new java.util.ArrayList();
  if (p != null) {
    for (int sec = 0; sec < 3; sec++) {
      @IC@ c = @PKG@.AhItem.section(p, sec);
      if (c == null) continue;
      int cap = c.getCapacity();
      for (int k = 0; k < cap; k++) {
        @IS@ x = c.getItemStack((short) k);
        if (x == null || x.isEmpty()) continue;
        if (@PKG@.AhItem.technical(x) || "Skyy_Menu".equals(x.getItemId())) continue;
        cells.add(new int[] { sec, k });
      }
    }
  }
  int n = cells.size();
  int pages = (n + 35) / 36;
  if (pages < 1) pages = 1;
  if (this.invPage >= pages) this.invPage = pages - 1;
  if (this.invPage < 0) this.invPage = 0;
  @IS@ picked = null;
  if (this.pickSec >= 0 && p != null) {
    @IC@ pc = @PKG@.AhItem.section(p, this.pickSec);
    if (pc != null && this.pickSlot >= 0 && this.pickSlot < pc.getCapacity()) {
      @IS@ x = pc.getItemStack((short) this.pickSlot);
      if (x != null && !x.isEmpty() && @PKG@.AhItem.sig(x).equals(this.pickSig)) picked = x;
    }
    if (picked == null) { this.pickSec = -1; this.pickSlot = -1; this.pickSig = ""; if (this.status.length() == 0) say("The picked item moved or changed - pick it again.", 2); }
  }
  b.appendInline("#SkyyAh", "Group #SkyyAhInvGrid { Anchor: (Height: 312); LayoutMode: Top; }");
  for (int rr = 0; rr < 4; rr++) {
    String row = "#SkyyAhInvRow" + rr;
    b.appendInline("#SkyyAhInvGrid", "Group #SkyyAhInvRow" + rr + " { Anchor: (Height: 78); LayoutMode: Left; }");
    sp(b, row, 172, 76);
    for (int cc = 0; cc < 9; cc++) {
      int i = rr * 9 + cc;
      int idx = this.invPage * 36 + i;
      if (cc > 0) sp(b, row, 4, 76);
      if (idx >= n) {
        this.cellSec[i] = -1;
        b.appendInline(row, "Group { Anchor: (Width: 76, Height: 76); Background: #142030(0.9); }");
        continue;
      }
      int[] cs = (int[]) cells.get(idx);
      @IS@ x = @PKG@.AhItem.section(p, cs[0]).getItemStack((short) cs[1]);
      this.cellSec[i] = cs[0];
      this.cellSlot[i] = cs[1];
      this.cellSig[i] = @PKG@.AhItem.sig(x);
      String iid = x.getItemId();
      boolean sel = picked != null && cs[0] == this.pickSec && cs[1] == this.pickSlot;
      boolean blk = @PKG@.AhItem.blockedReason(iid) != null;
      String bg = sel ? "#4f7fb0" : (blk ? "#3a2020" : "#1d3a5f");
      String ic = @PKG@.AhUtil.isId(iid) ? "ItemIcon { Anchor: (Width: 56, Height: 56, Left: 10, Top: 5); ItemId: \"" + iid + "\"; } " : "";
      b.appendInline(row, "Button #SkyyAhInv" + i + " { Anchor: (Width: 76, Height: 76); Style: ButtonStyle( Default: ( Background: " + bg + " ), Hovered: ( Background: #2f5a8f ), Disabled: ( Background: #1a2c3c ) ); " + ic + "Label #SkyyAhInvQty" + i + " { Anchor: (Width: 70, Height: 18, Right: 4, Bottom: 2); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); } }");
      if (x.getQuantity() > 1) b.set("#SkyyAhInvQty" + i + ".Text", String.valueOf(x.getQuantity()));
      ev.addEventBinding(@BT@.Activating, "#SkyyAhInv" + i, evd("pick:" + i));
    }
  }
  b.appendInline("#SkyyAh", "Group #SkyyAhInvPager { Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 2); }");
  btn(b, ev, "#SkyyAhInvPager", "SkyyAhInvPrev", 160, 36, "< Prev", BS, "invprev");
  txt(b, "#SkyyAhInvPager", "SkyyAhInvTxt", 740, 36, 14, false, "#9fb8cc", "Center", false, p == null ? "" : "Page " + (this.invPage + 1) + " / " + pages + " - " + n + (n == 1 ? " stack" : " stacks"));
  btn(b, ev, "#SkyyAhInvPager", "SkyyAhInvNext", 160, 36, "Next >", BS, "invnext");
  b.appendInline("#SkyyAh", "Group #SkyyAhSel { Anchor: (Height: 76); LayoutMode: Left; Background: #10233a(0.9); }");
  String pid = picked == null ? "" : picked.getItemId();
  b.appendInline("#SkyyAhSel", icon(pid, 76, 76, 60));
  b.appendInline("#SkyyAhSel", "Group #SkyyAhSelTxt { Anchor: (Width: 980, Height: 76); LayoutMode: Top; }");
  int pq = picked == null ? 1 : picked.getQuantity();
  if (picked == null) {
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelName", 0, 30, 18, true, "#cfe3ff", null, false, "No item picked");
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelInfo", 0, 22, 14, false, "#9fb8cc", null, false, "Click an item above to sell it.");
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelHint", 0, 24, 14, false, "#ffd36a", null, false, "");
  } else {
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelName", 0, 30, 18, true, @PKG@.AhItem.qColor(picked.getQualityIndex()), null, false, @PKG@.AhItem.plainName(picked));
    String rf = @PKG@.AhItem.reforge(picked.getMetadata());
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelInfo", 0, 22, 14, false, "#9fb8cc", null, false, "x" + pq + " - " + @PKG@.AhItem.qName(picked.getQualityIndex()) + (rf != null ? " - " + rf : "") + " - " + @PKG@.AhItem.secName(this.pickSec) + " slot " + (this.pickSlot + 1));
    long[] lo = @PKG@.AhStore.lowestBin(pid, null, now);
    String h = lo[0] > 0L ? "Lowest BIN for this item now: " + @PKG@.AhUtil.fmt(lo[0]) + " each (" + lo[1] + " listed)" : "None listed right now.";
    if (@PKG@.AhItem.isBag(pid)) h = h + " Contents not included - a bag opens its owner's own storage.";
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelHint", 0, 24, 14, false, "#ffd36a", null, false, h);
  }
  b.appendInline("#SkyyAh", "Group #SkyyAhPriceRow { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 4); }");
  txt(b, "#SkyyAhPriceRow", "SkyyAhPriceLab", 110, 42, 17, true, "#ffe9c9", null, false, "Price");
  b.appendInline("#SkyyAhPriceRow", "Group #SkyyAhPriceBox { Anchor: (Width: 300, Height: 42); Background: #16263a; }");
  b.appendInline("#SkyyAhPriceBox", "TextField #SkyyAhPrice { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 16; PlaceholderText: \"e.g. 12000 or 12k\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 18); Style: (TextColor: #ffffff, FontSize: 18); }");
  if (this.priceText != null && this.priceText.length() > 0) b.set("#SkyyAhPrice.Value", this.priceText);
  ev.addEventBinding(@BT@.Validating, "#SkyyAhPrice", evd("preview"), false);
  sp(b, "#SkyyAhPriceRow", 10, 42);
  btn(b, ev, "#SkyyAhPriceRow", "SkyyAhPricePreview", 150, 42, "Preview", BS_BLUE, "preview");
  sp(b, "#SkyyAhPriceRow", 14, 42);
  txt(b, "#SkyyAhPriceRow", "SkyyAhPriceHint", 470, 42, 14, false, "#9fb8cc", null, true, "Enter or Preview shows the fee - then click Create BIN.");
  b.appendInline("#SkyyAh", "Group #SkyyAhDurRow { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 4); }");
  txt(b, "#SkyyAhDurRow", "SkyyAhDurLab", 110, 42, 17, true, "#ffe9c9", null, false, "Duration");
  String[] dl = @PKG@.AhCfg.DUR_LABEL;
  if (this.durIdx < 0 || this.durIdx >= dl.length) this.durIdx = @PKG@.AhCfg.DEF_DUR < dl.length ? @PKG@.AhCfg.DEF_DUR : 0;
  for (int i = 0; i < dl.length && i < 8; i++) {
    if (i > 0) sp(b, "#SkyyAhDurRow", 8, 42);
    btn(b, ev, "#SkyyAhDurRow", "SkyyAhDur" + i, 100, 42, dl[i], i == this.durIdx ? BS_ON : BS, "dur:" + i);
  }
  String f0, f1, f2 = "";
  long pp = this.previewPrice;
  if (pp > 0L) {
    long lf = @PKG@.AhCfg.listingFee(pp);
    long df = @PKG@.AhCfg.DUR_FEE[this.durIdx];
    f0 = "Listing fee " + @PKG@.AhCfg.pctText(@PKG@.AhCfg.pctFor(pp)) + "% = " + @PKG@.AhUtil.fmt(lf) + " + duration fee (" + dl[this.durIdx] + ") = " + @PKG@.AhUtil.fmt(df) + " -> you pay " + @PKG@.AhUtil.fmt(lf + df) + " coins now (" + (@PKG@.AhCfg.CANCEL_REFUND ? "refunded" : "not refunded") + " if you cancel).";
    long tx = @PKG@.AhCfg.tax(pp);
    f1 = "If it sells you get " + @PKG@.AhUtil.fmt(pp - tx) + " coins" + (tx > 0L ? " (" + @PKG@.AhCfg.pctText(@PKG@.AhCfg.TAX_PCT) + "% tax " + @PKG@.AhUtil.fmt(tx) + ")." : " (no tax under " + @PKG@.AhUtil.fmt(@PKG@.AhCfg.TAX_FROM) + ").");
    if (picked != null) {
      long[] lo2 = @PKG@.AhStore.lowestBin(pid, null, now);
      long each = @PKG@.AhUtil.ceilDiv(pp, (long) pq);
      if (lo2[0] > 0L && each * 2L < lo2[0]) f2 = "That is less than half the lowest BIN (" + @PKG@.AhUtil.fmt(lo2[0]) + " each) - check the price.";
    }
  } else {
    f0 = "Type a price, press Enter or Preview to see the fee, then click Create BIN.";
    f1 = "Prices like 500, 12k, 1.5m or 2b - from " + @PKG@.AhUtil.fmt(@PKG@.AhCfg.MIN_PRICE) + " to " + @PKG@.AhUtil.fmt(@PKG@.AhCfg.MAX_PRICE) + " coins for the whole stack.";
  }
  txt(b, "#SkyyAh", "SkyyAhFee0", 0, 24, 15, true, "#ffe9c9", null, false, f0);
  txt(b, "#SkyyAh", "SkyyAhFee1", 0, 24, 15, false, "#9fe8a2", null, false, f1);
  txt(b, "#SkyyAh", "SkyyAhFee2", 0, 24, 15, true, "#ffb070", null, false, f2);
  b.appendInline("#SkyyAh", "Group #SkyyAhCreateRow { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }");
  sp(b, "#SkyyAhCreateRow", 350, 52);
  btn(b, ev, "#SkyyAhCreateRow", "SkyyAhCreate", 360, 52, "Create BIN", BS_GREEN, "create");
}""")
# ---- Manage view (50 + 8 x 62 + 46 + 26 = 618, + top 126 + status 30 = 774)
M(page, r"""
public void renderManage(@UCB@ b, @UEB@ ev, java.util.UUID u, long now) {
  java.util.ArrayList rows = @PKG@.AhStore.rowsFor(this.key);
  long[] ow = @PKG@.AhStore.owedFor(this.key);
  int used = @PKG@.AhStore.slotsUsed(this.key);
  b.appendInline("#SkyyAh", "Group #SkyyAhMSum { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 4); }");
  boolean armedAll = armedFor("claimall", String.valueOf(ow[1]), ow[1]);
  String sum = "Listings " + used + " / " + @PKG@.AhCfg.MAX_LISTINGS + " used - to claim: " + ow[2] + (ow[2] == 1L ? " item, " : " items, ") + @PKG@.AhUtil.fmt(ow[1]) + " coins";
  if (armedAll) sum = "Claim " + @PKG@.AhUtil.fmt(ow[1]) + " coins into your purse? Purse coins can be lost on death.";
  txt(b, "#SkyyAhMSum", "SkyyAhMSumTxt", 640, 42, 16, true, armedAll ? "#ffd36a" : "#ffe9c9", null, true, sum);
  sp(b, "#SkyyAhMSum", 10, 42);
  if (armedAll) {
    btn(b, ev, "#SkyyAhMSum", "SkyyAhMClaimAll", 200, 42, "Yes, claim all", BS_GREEN, "claimyes");
    sp(b, "#SkyyAhMSum", 10, 42);
    btn(b, ev, "#SkyyAhMSum", "SkyyAhMClaimNo", 200, 42, "No", BS, "claimno");
  } else {
    btn(b, ev, "#SkyyAhMSum", "SkyyAhMClaimAll", 200, 42, "Claim all", ow[0] > 0L ? BS_GREEN : BS, "claimall");
    sp(b, "#SkyyAhMSum", 10, 42);
    btn(b, ev, "#SkyyAhMSum", "SkyyAhMCreate", 200, 42, "Create BIN", BS_BLUE, "mcreate");
  }
  int total = rows.size();
  int pages = (total + 7) / 8;
  if (pages < 1) pages = 1;
  if (this.managePage >= pages) this.managePage = pages - 1;
  if (this.managePage < 0) this.managePage = 0;
  for (int i = 0; i < 8; i++) { this.mIds[i] = null; this.mKinds[i] = null; }
  if (total == 0) {
    b.appendInline("#SkyyAh", "Group #SkyyAhMEmpty { Anchor: (Height: 496); LayoutMode: Top; }");
    sp(b, "#SkyyAhMEmpty", 0, 140);
    txt(b, "#SkyyAhMEmpty", "SkyyAhMEmptyTxt", 0, 60, 22, true, "#cfe3ff", "Center", false, "You have no listings");
    b.appendInline("#SkyyAhMEmpty", "Group #SkyyAhMEmptyRow { Anchor: (Height: 70); LayoutMode: Left; }");
    sp(b, "#SkyyAhMEmptyRow", 350, 60);
    btn(b, ev, "#SkyyAhMEmptyRow", "SkyyAhMCreateBig", 360, 60, "Create BIN", BS_GREEN, "mcreate");
  } else {
    for (int i = 0; i < 8; i++) {
      int idx = this.managePage * 8 + i;
      if (idx >= total) { sp(b, "#SkyyAh", 0, 62); continue; }
      String[] x = (String[]) rows.get(idx);
      @BD@ r = @PKG@.AhStore.get(x[0]);
      if (r == null) { sp(b, "#SkyyAh", 0, 62); continue; }
      this.mIds[i] = x[0];
      this.mKinds[i] = x[1];
      String iid = @PKG@.AhRec.subStr(r, "item", "id", "");
      long qty = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
      int qi = (int) @PKG@.AhRec.subLng(r, "item", "quality", 0L);
      long price = @PKG@.AhRec.lng(r, "price", 0L);
      String row = "#SkyyAhMRow" + i;
      b.appendInline("#SkyyAh", "Group #SkyyAhMRow" + i + " { Anchor: (Height: 58); LayoutMode: Left; Background: #142030(0.9); }");
      b.appendInline(row, icon(iid, 60, 58, 50));
      sp(b, row, 8, 58);
      b.appendInline(row, "Group #SkyyAhMTxt" + i + " { Anchor: (Width: 380, Height: 58); LayoutMode: Top; }");
      txt(b, "#SkyyAhMTxt" + i, "SkyyAhMName" + i, 0, 32, 17, true, @PKG@.AhItem.qColor(qi), null, false, @PKG@.AhRec.str(r, "name", iid));
      txt(b, "#SkyyAhMTxt" + i, "SkyyAhMSub" + i, 0, 24, 13, false, "#9fb8cc", null, false, "x" + qty + " - " + @PKG@.AhUtil.fmt(price) + " coins - #" + x[0]);
      String state;
      String act = null;
      String style = BS;
      String k = x[1];
      if (k.equals("coins")) {
        state = "Sold to " + @PKG@.AhRec.subStr(r, "buyer", "name", "?") + " - " + @PKG@.AhUtil.fmt(@PKG@.AhRec.subLng(r, "sale", "net", 0L)) + " coins (tax " + @PKG@.AhUtil.fmt(@PKG@.AhRec.subLng(r, "sale", "tax", 0L)) + ")";
        act = "Claim coins"; style = BS_GREEN;
      } else if (k.equals("sitem")) {
        String s = @PKG@.AhRec.state(r);
        long left = @PKG@.AhRec.subLng(r, "claims", "sellerItemQty", qty);
        if ("REMOVED".equals(s)) state = "Removed by an admin: " + @PKG@.AhRec.subStr(r, "removed", "reason", "no reason given");
        else if ("CANCELLED".equals(s)) state = "Cancelled";
        else state = "Expired";
        if (left > 0L && left < qty) state = state + " - " + left + " left to claim";
        act = "Claim item"; style = BS_GREEN;
      } else if (k.equals("bitem")) {
        state = "Bought from " + @PKG@.AhRec.subStr(r, "seller", "name", "?") + " - waiting for inventory room";
        act = "Claim item"; style = BS_GREEN;
      } else if (k.equals("active")) {
        long grace = @PKG@.AhRec.lng(r, "graceUntil", 0L);
        long ends = @PKG@.AhRec.lng(r, "endsAt", 0L);
        state = now < grace ? "In grace " + ((grace - now + 999L) / 1000L) + " s - nobody can buy it yet" : (now < ends ? "Ends in " + @PKG@.AhUtil.timeLeft(ends - now) : "Ended - expires on the next tick");
        if (@PKG@.AhItem.blockedReason(iid) != null) state = state + " - off the market";
        act = "Cancel"; style = BS_RED;
      } else {
        state = "Needs a newer SkyyAuctions - left untouched";
      }
      txt(b, row, "SkyyAhMState" + i, 380, 58, 15, false, "#dfe9f5", null, true, state);
      b.appendInline(row, "Group #SkyyAhMBtn" + i + " { Anchor: (Width: 232, Height: 58); LayoutMode: Left; Padding: (Top: 7); }");
      String bp = "#SkyyAhMBtn" + i;
      if (k.equals("active") && armedFor("mcancel:" + i, x[0], 0L)) {
        btn(b, ev, bp, "SkyyAhMAct" + i, 130, 44, "Yes, cancel", BS_RED, "myes:" + i);
        sp(b, bp, 6, 44);
        btn(b, ev, bp, "SkyyAhMNo" + i, 90, 44, "No", BS, "mno");
      } else if (act != null) {
        btn(b, ev, bp, "SkyyAhMAct" + i, 220, 44, act, style, "mact:" + i);
      }
      sp(b, "#SkyyAh", 0, 4);
    }
  }
  b.appendInline("#SkyyAh", "Group #SkyyAhMPager { Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 4); }");
  btn(b, ev, "#SkyyAhMPager", "SkyyAhMPrev", 180, 40, "< Prev", BS, "mprev");
  txt(b, "#SkyyAhMPager", "SkyyAhMPageTxt", 700, 40, 16, true, "#cfe3ff", "Center", false, "Page " + (this.managePage + 1) + " / " + pages);
  btn(b, ev, "#SkyyAhMPager", "SkyyAhMNext", 180, 40, "Next >", BS, "mnext");
  txt(b, "#SkyyAh", "SkyyAhMOther", 0, 26, 14, true, "#ffd070", "Center", false, @PKG@.AhStore.otherProfiles(u, this.key));
}""")
# the whole page; also what the offline markup check calls (player may be null there)
M(page, r"""
public void render(@UCB@ b, @UEB@ ev, java.util.UUID u, @PLA@ p) {
  long now = System.currentTimeMillis();
  b.appendInline((String) null, "Group #SkyyAh { Anchor: (Width: 1120, Height: 880); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }");
  renderTop(b, ev, u, p);
  if ("item".equals(this.view)) renderItem(b, ev, u, now);
  else if ("create".equals(this.view)) renderCreate(b, ev, u, p, now);
  else if ("manage".equals(this.view)) renderManage(b, ev, u, now);
  else renderBrowse(b, ev, u, now);
  String col = this.statusKind == 1 ? "#9fe8a2" : (this.statusKind == 2 ? "#ffb070" : "#cfe3ff");
  txt(b, "#SkyyAh", "SkyyAhStatus", 0, 30, 15, true, col, "Center", false, this.status);
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  render(b, ev, this.playerRef.getUuid(), p);
}""")
M(page, r"""
public static int argInt(String a, String prefix) {
  try { return Integer.parseInt(a.substring(prefix.length())); } catch (Throwable t) { return -1; }
}""")
M(page, r"""
public void finish(@RES@ r, @REF@ ref, @ST@ st, @PLA@ p) {
  @PKG@.AhStore.afterTrade(r, this.playerRef, p, ref, st);
  if (r != null && r.alert) this.playerRef.sendMessage(@MSG@.raw("[Auction House] " + r.msg));
}""")
M(page, r"""
public void doPreview() {
  long v = @PKG@.AhUtil.parsePrice(this.priceText);
  if (v <= 0L) {
    this.previewPrice = -1L;
    say(this.priceText == null || this.priceText.trim().length() == 0 ? "Type a price first - like 12000, 12k or 1.5m." : "That is not a price - type a whole number like 12000, 12k or 1.5m.", 2);
    return;
  }
  if (v < @PKG@.AhCfg.MIN_PRICE || v > @PKG@.AhCfg.MAX_PRICE) {
    this.previewPrice = -1L;
    say("The price must be " + @PKG@.AhUtil.fmt(@PKG@.AhCfg.MIN_PRICE) + " to " + @PKG@.AhUtil.fmt(@PKG@.AhCfg.MAX_PRICE) + " coins.", 2);
    return;
  }
  this.previewPrice = v;
  say("Check the fee above, then click Create BIN.", 0);
}""")
M(page, r"""
public void doCreate(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u) {
  if (this.pickSec < 0) { say("Pick an item from your inventory first.", 2); return; }
  long v = @PKG@.AhUtil.parsePrice(this.priceText);
  if (v <= 0L || v != this.previewPrice) {
    doPreview();
    if (this.previewPrice > 0L) say("Check the fee above, then click Create BIN again.", 0);
    return;
  }
  @RES@ r = @PKG@.AhStore.list(p, ref, st, u, this.key, this.playerRef.getUsername(), @PKG@.AhUtil.profName(u), this.pickSec, this.pickSlot, this.pickSig, v, this.durIdx);
  finish(r, ref, st, p);
  if (r.ok) {
    this.view = "manage"; this.managePage = 0;
    this.pickSec = -1; this.pickSlot = -1; this.pickSig = "";
    this.previewPrice = -1L; this.priceText = "";
    say(r.msg, 1);
  } else say(r.msg, 2);
}""")
M(page, r"""
public void doBuy(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, long now, boolean confirmed) {
  @BD@ r = @PKG@.AhStore.get(this.detailId);
  if (r == null || !@PKG@.AhStore.buyable(r, now)) { say("That listing is no longer for sale.", 2); return; }
  long grace = @PKG@.AhRec.lng(r, "graceUntil", 0L);
  if (now < grace) { say("New listings can be bought " + (@PKG@.AhCfg.GRACE_MS / 1000L) + " s after they are listed - " + ((grace - now + 999L) / 1000L) + " s left.", 2); return; }
  if (!confirmed && this.detailPrice >= @PKG@.AhCfg.CONFIRM_ABOVE) {
    arm("buy", this.detailId, this.detailPrice, now);
    say("Confirm the purchase within " + (@PKG@.AhCfg.CONFIRM_MS / 1000L) + " s.", 0);
    return;
  }
  @RES@ res = @PKG@.AhStore.buy(p, u, this.key, this.playerRef.getUsername(), @PKG@.AhUtil.profName(u), this.detailId, this.detailPrice);
  finish(res, ref, st, p);
  if (res.ok) {
    this.playerRef.sendMessage(@MSG@.raw("[Auction House] " + res.msg));
    this.view = "browse";
    say(res.msg, 1);
  } else say(res.msg, 2);
}""")
M(page, r"""
public void doCancel(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String id) {
  @RES@ r = @PKG@.AhStore.cancel(p, u, this.key, id);
  finish(r, ref, st, p);
  if (r.ok && "item".equals(this.view)) this.view = "manage";
  say(r.msg, r.ok ? 1 : 2);
}""")
M(page, r"""
public void doClaimAll(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u) {
  @RES@ r = @PKG@.AhStore.claimAll(p, u, this.key);
  finish(r, ref, st, p);
  say(r.msg, r.ok ? 1 : 2);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.AhUtil.jsonStr(data, "a");
    if (a.length() == 0) return;
    java.util.UUID u = this.playerRef.getUuid();
    long now = System.currentTimeMillis();
    String wAct = this.armAct;
    String wId = this.armId;
    long wPrice = this.armPrice;
    long wUntil = this.armUntil;
    this.armAct = null; this.armId = null; this.armPrice = 0L; this.armUntil = 0L;
    if (data.indexOf("\"@AhSearch\"") >= 0) {
      String q = @PKG@.AhUtil.jsonStr(data, "@AhSearch").trim();
      if (q.length() > 40) q = q.substring(0, 40);
      if (!q.equals(this.query)) { this.query = q; this.browsePage = 0; }
    }
    if (data.indexOf("\"@AhPrice\"") >= 0) {
      String v = @PKG@.AhUtil.jsonStr(data, "@AhPrice").trim();
      if (v.length() > 16) v = v.substring(0, 16);
      this.priceText = v;
    }
    @PLA@ p = null;
    try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
    if (a.equals("close")) { if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None); return; }
    String k = @PKG@.AhUtil.pkey(u);
    if (!k.equals(this.key)) {
      this.key = k;
      this.pickSec = -1; this.pickSlot = -1; this.pickSig = ""; this.previewPrice = -1L; this.managePage = 0;
      String pn = @PKG@.AhUtil.profName(u);
      say("Your profile changed - this is now profile " + (pn.length() > 0 ? pn : "(current)") + "'s view.", 2);
      rebuild();
      return;
    }
    this.status = ""; this.statusKind = 0;
    if (a.equals("nav:browse")) { this.view = "browse"; }
    else if (a.equals("nav:create") || a.equals("mcreate")) { this.view = "create"; }
    else if (a.equals("nav:manage")) { this.view = "manage"; }
    else if (a.startsWith("cat:")) { int i = argInt(a, "cat:"); if (i >= 0 && i < 7) { this.cat = i; this.browsePage = 0; } }
    else if (a.equals("sort")) { this.sort = (this.sort + 1) % 4; this.browsePage = 0; }
    else if (a.equals("rar")) { @PKG@.AhItem.tiers(); this.rar = (this.rar + 1) % (@PKG@.AhItem.TIER_NAME.length + 1); this.browsePage = 0; }
    else if (a.equals("refresh") || a.equals("search")) { }
    else if (a.equals("clear")) { this.query = ""; this.browsePage = 0; }
    else if (a.equals("prev")) { if (this.browsePage > 0) this.browsePage--; }
    else if (a.equals("next")) { this.browsePage++; }
    else if (a.startsWith("view:")) {
      int i = argInt(a, "view:");
      if (i >= 0 && i < 8 && this.rowIds[i] != null) { this.detailId = this.rowIds[i]; this.detailPrice = -1L; this.view = "item"; }
    }
    else if (a.equals("back")) { this.view = "browse"; }
    else if (a.equals("buy")) { doBuy(ref, st, p, u, now, false); }
    else if (a.equals("confirm")) {
      if (armOk(wAct, wId, wPrice, wUntil, "buy", this.detailId, this.detailPrice, now)) doBuy(ref, st, p, u, now, true);
      else if (armOk(wAct, wId, wPrice, wUntil, "cancel", this.detailId, this.detailPrice, now)) doCancel(ref, st, p, u, this.detailId);
      else say("The confirm ran out - click again.", 2);
    }
    else if (a.equals("no")) { say("Nothing done.", 0); }
    else if (a.equals("dcancel")) {
      @BD@ r = @PKG@.AhStore.get(this.detailId);
      if (r != null && this.key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) { arm("cancel", this.detailId, this.detailPrice, now); say("Confirm the cancel within " + (@PKG@.AhCfg.CONFIRM_MS / 1000L) + " s.", 0); }
      else say("That listing is not yours or is gone.", 2);
    }
    else if (a.startsWith("pick:")) {
      int i = argInt(a, "pick:");
      if (i >= 0 && i < 36 && this.cellSec[i] >= 0 && p != null) {
        @IC@ c = @PKG@.AhItem.section(p, this.cellSec[i]);
        @IS@ x = c == null ? null : c.getItemStack((short) this.cellSlot[i]);
        if (x == null || x.isEmpty() || !@PKG@.AhItem.sig(x).equals(this.cellSig[i])) say("That slot changed - pick again.", 2);
        else {
          String why = @PKG@.AhItem.tradeable(x);
          if (why != null) say(why, 2);
          else { this.pickSec = this.cellSec[i]; this.pickSlot = this.cellSlot[i]; this.pickSig = this.cellSig[i]; say("Picked " + @PKG@.AhItem.plainName(x) + " - type a price.", 0); }
        }
      }
    }
    else if (a.equals("invprev")) { if (this.invPage > 0) this.invPage--; }
    else if (a.equals("invnext")) { this.invPage++; }
    else if (a.equals("preview")) { doPreview(); }
    else if (a.startsWith("dur:")) { int i = argInt(a, "dur:"); if (i >= 0 && i < @PKG@.AhCfg.DUR_LABEL.length) this.durIdx = i; doPreview(); }
    else if (a.equals("create")) { doCreate(ref, st, p, u); }
    else if (a.startsWith("mact:")) {
      int i = argInt(a, "mact:");
      if (i >= 0 && i < 8 && this.mIds[i] != null) {
        String kind = this.mKinds[i];
        if (kind.equals("active")) { arm("mcancel:" + i, this.mIds[i], 0L, now); say("Cancel it? The fee is " + (@PKG@.AhCfg.CANCEL_REFUND ? "refunded" : "not refunded") + " - click Yes, cancel within " + (@PKG@.AhCfg.CONFIRM_MS / 1000L) + " s.", 0); }
        else if (kind.equals("coins")) { @RES@ r = @PKG@.AhStore.claimCoins(u, this.key, this.mIds[i]); finish(r, ref, st, p); say(r.msg, r.ok ? 1 : 2); }
        else if (kind.equals("sitem") || kind.equals("bitem")) { @RES@ r = @PKG@.AhStore.claimItem(p, u, this.key, this.mIds[i], kind.equals("sitem")); finish(r, ref, st, p); say(r.msg, r.ok ? 1 : 2); }
      }
    }
    else if (a.startsWith("myes:")) {
      int i = argInt(a, "myes:");
      if (i >= 0 && i < 8 && this.mIds[i] != null && armOk(wAct, wId, wPrice, wUntil, "mcancel:" + i, this.mIds[i], 0L, now)) doCancel(ref, st, p, u, this.mIds[i]);
      else say("The confirm ran out - click Cancel again.", 2);
    }
    else if (a.equals("mno") || a.equals("claimno")) { say("Nothing done.", 0); }
    else if (a.equals("mprev")) { if (this.managePage > 0) this.managePage--; }
    else if (a.equals("mnext")) { this.managePage++; }
    else if (a.equals("claimall")) {
      long[] ow = @PKG@.AhStore.owedFor(this.key);
      if (@PKG@.AhCfg.CLAIMALL_ABOVE > 0L && ow[1] >= @PKG@.AhCfg.CLAIMALL_ABOVE) { arm("claimall", String.valueOf(ow[1]), ow[1], now); say("Purse coins can be lost on death - coins waiting here are safe.", 0); }
      else doClaimAll(ref, st, p, u);
    }
    else if (a.equals("claimyes")) {
      long[] ow = @PKG@.AhStore.owedFor(this.key);
      if (armOk(wAct, wId, wPrice, wUntil, "claimall", String.valueOf(ow[1]), ow[1], now)) doClaimAll(ref, st, p, u);
      else say("The confirm ran out or the amount changed - click Claim all again.", 2);
    }
    rebuild();
  } catch (Throwable t) { @PKG@.AhUtil.warn("auction page click failed: " + t); }
}""")

fac.addInterface(pool.get("java.util.function.Function"))
C(fac, "public AhPageFactory() { }")
M(fac, r"""
public Object apply(Object o) { return new @PKG@.AhPage((@PR@) o, "browse"); }""")

# ================= AhCmds: shared bodies of the player and admin commands =================
M(cmds, r"""
public static void tell(@PR@ pr, String m) { pr.sendMessage(@MSG@.raw("[Auction House] " + m)); }""")
M(cmds, r"""
public static void atell(@PR@ pr, String m) { pr.sendMessage(@MSG@.raw("[AH admin] " + m)); }""")
M(cmds, r"""
public static void open(@PR@ pr, @REF@ ref, @ST@ store, @PKG@.AhPage page) {
  @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  if (!@PKG@.Coins.ready()) tell(pr, "SkyyCoins is not loaded - you can look, but not list or buy.");
  p.getPageManager().openCustomPage(ref, store, page);
}""")
M(cmds, r"""
public static void sell(@PR@ pr, @REF@ ref, @ST@ store, String priceRaw, String durRaw) {
  @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  java.util.UUID u = pr.getUuid();
  @INV@ inv = p.getInventory();
  int slot = inv.getActiveHotbarSlot();
  @IC@ hb = inv.getHotbar();
  @IS@ st = (hb != null && slot >= 0 && slot < hb.getCapacity()) ? hb.getItemStack((short) slot) : null;
  if (st == null || st.isEmpty()) { tell(pr, "Hold the item you want to sell (your selected hotbar slot), then /ah sell <price>."); return; }
  int di = @PKG@.AhCfg.DEF_DUR;
  if (durRaw != null) {
    long ms = @PKG@.AhUtil.parseDurMs(durRaw);
    int d2 = ms > 0L ? @PKG@.AhCfg.durIndexMs(ms) : -1;
    if (d2 < 0) { tell(pr, "Pick one of: " + @PKG@.AhCfg.durList()); return; }
    di = d2;
  }
  String raw = priceRaw == null ? "" : priceRaw.trim();
  if (raw.length() > 16) raw = raw.substring(0, 16);
  long price = @PKG@.AhUtil.parsePrice(raw);
  String why = @PKG@.AhItem.tradeable(st);
  if (@PKG@.AhCfg.SELL_PAGE) {
    @PKG@.AhPage pg = new @PKG@.AhPage(pr, "create");
    pg.priceText = raw;
    pg.durIdx = di;
    if (why == null) { pg.pickSec = 0; pg.pickSlot = slot; pg.pickSig = @PKG@.AhItem.sig(st); }
    if (price > 0L && price >= @PKG@.AhCfg.MIN_PRICE && price <= @PKG@.AhCfg.MAX_PRICE) {
      pg.previewPrice = price;
      if (why == null) pg.say("Check the fee, then click Create BIN.", 0); else pg.say(why, 2);
    } else pg.say(why != null ? why : "That is not a price in range - type one like 12000, 12k or 1.5m, then Preview.", 2);
    open(pr, ref, store, pg);
    return;
  }
  if (why != null) { tell(pr, why); return; }
  if (price <= 0L) { tell(pr, "That is not a price - try 12000, 12k or 1.5m."); return; }
  @RES@ r = @PKG@.AhStore.list(p, ref, store, u, @PKG@.AhUtil.pkey(u), pr.getUsername(), @PKG@.AhUtil.profName(u), 0, slot, @PKG@.AhItem.sig(st), price, di);
  @PKG@.AhStore.afterTrade(r, pr, p, ref, store);
  tell(pr, r.msg);
}""")
M(cmds, r"""
public static void claim(@PR@ pr, @REF@ ref, @ST@ store) {
  @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  java.util.UUID u = pr.getUuid();
  String key = @PKG@.AhUtil.pkey(u);
  @RES@ r = @PKG@.AhStore.claimAll(p, u, key);
  @PKG@.AhStore.afterTrade(r, pr, p, ref, store);
  tell(pr, r.msg);
  if (@PKG@.AhCfg.CLAIMALL_ABOVE > 0L && r.coins >= @PKG@.AhCfg.CLAIMALL_ABOVE) {
    boolean bank = @PKG@.AhUtil.bridge().get("bank:" + u) != null;
    tell(pr, "Tip: purse coins can be lost on death" + (bank ? " - /bank deposit keeps them safe." : "."));
  }
  String other = @PKG@.AhStore.otherProfiles(u, key);
  if (other.length() > 0) tell(pr, other);
}""")
M(cmds, r"""
public static void search(@PR@ pr, @REF@ ref, @ST@ store, String words) {
  @PKG@.AhPage pg = new @PKG@.AhPage(pr, "browse");
  String q = words == null ? "" : words.trim();
  if (q.length() > 40) q = q.substring(0, 40);
  pg.query = q;
  open(pr, ref, store, pg);
}""")
M(cmds, r"""
public static String recLine(@BD@ r, long now) {
  String st = @PKG@.AhRec.state(r);
  String s = "#" + @PKG@.AhRec.id(r) + " " + st + " " + @PKG@.AhRec.str(r, "name", "?") + " x" + @PKG@.AhRec.subLng(r, "item", "qty", 1L) + " " + @PKG@.AhUtil.fmt(@PKG@.AhRec.lng(r, "price", 0L)) + " by " + @PKG@.AhRec.subStr(r, "seller", "name", "?");
  if ("ACTIVE".equals(st)) s = s + " ends " + @PKG@.AhUtil.timeLeft(@PKG@.AhRec.lng(r, "endsAt", 0L) - now);
  if (@PKG@.AhRec.sub(r, "buyer") != null) s = s + " -> " + @PKG@.AhRec.subStr(r, "buyer", "name", "?");
  s = s + " [sc " + @PKG@.AhRec.claim(r, "sellerCoins") + ", si " + @PKG@.AhRec.claim(r, "sellerItem") + ", bi " + @PKG@.AhRec.claim(r, "buyerItem") + "]";
  if (@PKG@.AhRec.readOnly(r)) s = s + " (read-only: needs a newer SkyyAuctions)";
  return s;
}""")
M(cmds, r"""
public static void status(@PR@ pr) {
  long now = System.currentTimeMillis();
  int act = @PKG@.AhStore.countActive(now);
  int owed = 0;
  java.util.Iterator it = @PKG@.AhStore.LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if ("OWED".equals(@PKG@.AhRec.claim(r, "sellerCoins"))) owed++;
    if ("OWED".equals(@PKG@.AhRec.claim(r, "sellerItem"))) owed++;
    if ("OWED".equals(@PKG@.AhRec.claim(r, "buyerItem"))) owed++;
  }
  atell(pr, "SkyyAuctions @VERSION@ - " + act + " active, " + @PKG@.AhStore.LIVE.size() + " open records, " + owed + " claims owed, " + @PKG@.AhStore.DIRTY.size() + " unsaved (DIRTY), " + @PKG@.AhStore.ARCH.size() + " waiting to archive, paused " + @PKG@.AhCfg.PAUSED + ", coins bridge " + (@PKG@.Coins.ready() ? "found" : "MISSING") + ", forced save " + (@PKG@.AhCfg.FORCE_SAVE ? (@PKG@.AhStore.SAVE_BROKEN ? "BROKEN (skipped)" : "on") : "off"));
  atell(pr, @PKG@.AhCfg.summary());
  if (@PKG@.AhCfg.TEST_ON.length() > 0) atell(pr, "TEST DURATIONS ARE ON: " + @PKG@.AhCfg.TEST_ON + " - set allowTestDurations=false after testing");
  if (@PKG@.AhCfg.SAME_ACCOUNT) atell(pr, "sameAccountBuy=true - solo testing only");
  for (int i = 0; i < @PKG@.AhLog.UNMATCHED.size(); i++) atell(pr, "possible lost coins: " + @PKG@.AhLog.UNMATCHED.get(i));
  for (int i = 0; i < @PKG@.AhStore.RESTORED.size(); i++) atell(pr, "restored at start from auctions.log (a write had not landed): " + @PKG@.AhStore.RESTORED.get(i));
  atell(pr, "/ahadmin list [player] | info <id> | remove <id> [reason] | reload | pause | resume | regrant <id> <seller|buyer> [confirm]");
}""")
M(cmds, r"""
public static void list(@PR@ pr, String who) {
  long now = System.currentTimeMillis();
  java.util.ArrayList out = new java.util.ArrayList();
  if (who == null) {
    out = @PKG@.AhStore.active(now);
    java.util.Collections.sort(out, new @PKG@.AhSort(3));
    if (out.isEmpty()) { atell(pr, "No active listings."); return; }
    for (int i = 0; i < out.size() && i < 10; i++) atell(pr, recLine((@BD@) out.get(i), now));
    if (out.size() > 10) atell(pr, "... and " + (out.size() - 10) + " more.");
    return;
  }
  java.util.Iterator it = @PKG@.AhStore.LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if (who.equalsIgnoreCase(@PKG@.AhRec.subStr(r, "seller", "name", "")) || who.equalsIgnoreCase(@PKG@.AhRec.subStr(r, "buyer", "name", ""))) out.add(r);
  }
  java.util.Collections.sort(out, new @PKG@.AhSort(3));
  if (out.isEmpty()) { atell(pr, "No open records for " + who + "."); return; }
  for (int i = 0; i < out.size() && i < 20; i++) atell(pr, recLine((@BD@) out.get(i), now));
  if (out.size() > 20) atell(pr, "... and " + (out.size() - 20) + " more.");
}""")
M(cmds, r"""
public static void info(@PR@ pr, String id) {
  @BD@ r = @PKG@.AhStore.readAny(id == null ? "" : id.trim().replace("#", ""));
  if (r == null) { atell(pr, "No record #" + id + " (live or archived)."); return; }
  long now = System.currentTimeMillis();
  String rid = @PKG@.AhRec.id(r);
  String where = @PKG@.AhStore.DIRTY.containsKey(rid) ? " (NOT SAVED YET - its write failed, the tick retries; auctions.log has a copy)" : (@PKG@.AhStore.get(rid) == null ? (@PKG@.AhStore.ARCH.containsKey(rid) ? " (closed, waiting to archive)" : " (archived)") : "");
  atell(pr, recLine(r, now) + where);
  atell(pr, "type " + @PKG@.AhRec.str(r, "type", "?") + ", v " + @PKG@.AhRec.lng(r, "v", 1L) + ", rev " + @PKG@.AhRec.lng(r, "rev", 0L) + ", closed " + @PKG@.AhRec.bool(r, "closed", false) + ", category " + @PKG@.AhRec.str(r, "category", "?") + ", duration " + @PKG@.AhRec.str(r, "duration", "?"));
  atell(pr, "seller " + @PKG@.AhRec.subStr(r, "seller", "name", "?") + " " + @PKG@.AhRec.subStr(r, "seller", "uuid", "?") + " key " + @PKG@.AhRec.subStr(r, "seller", "key", "?") + " profile " + @PKG@.AhRec.subStr(r, "seller", "profile", ""));
  if (@PKG@.AhRec.sub(r, "buyer") != null) atell(pr, "buyer " + @PKG@.AhRec.subStr(r, "buyer", "name", "?") + " " + @PKG@.AhRec.subStr(r, "buyer", "uuid", "?") + " key " + @PKG@.AhRec.subStr(r, "buyer", "key", "?") + " profile " + @PKG@.AhRec.subStr(r, "buyer", "profile", ""));
  atell(pr, "fee listing " + @PKG@.AhRec.subLng(r, "fee", "listing", 0L) + " + duration " + @PKG@.AhRec.subLng(r, "fee", "duration", 0L) + " refunded " + @PKG@.AhRec.subBool(r, "fee", "refunded", false) + (@PKG@.AhRec.sub(r, "sale") != null ? " | sale gross " + @PKG@.AhRec.subLng(r, "sale", "gross", 0L) + " tax " + @PKG@.AhRec.subLng(r, "sale", "tax", 0L) + " net " + @PKG@.AhRec.subLng(r, "sale", "net", 0L) : ""));
  atell(pr, "claims sellerCoins " + @PKG@.AhRec.claim(r, "sellerCoins") + ", sellerItem " + @PKG@.AhRec.claim(r, "sellerItem") + " (qty " + @PKG@.AhRec.subLng(r, "claims", "sellerItemQty", 0L) + "), buyerItem " + @PKG@.AhRec.claim(r, "buyerItem") + " (qty " + @PKG@.AhRec.subLng(r, "claims", "buyerItemQty", 0L) + ")");
  @BD@ it = @PKG@.AhRec.sub(r, "item");
  @BD@ meta = @PKG@.AhRec.sub(it, "meta");
  String keys = meta == null ? "none" : String.valueOf(meta.keySet());
  atell(pr, "item " + @PKG@.AhRec.str(it, "id", "?") + " x" + @PKG@.AhRec.lng(it, "qty", 0L) + " quality " + @PKG@.AhRec.lng(it, "quality", 0L) + " durability " + @PKG@.AhRec.dbl(it, "durability", 0.0) + " / " + @PKG@.AhRec.dbl(it, "maxDurability", 0.0) + " metadata keys " + keys + (it != null && it.containsKey("stack") ? " (codec snapshot present)" : " (NO codec snapshot)"));
}""")
M(cmds, r"""
public static void remove(@PR@ pr, String id, String reason) {
  String rs = reason == null || reason.trim().length() == 0 ? "removed by an admin" : reason.trim();
  if (rs.length() > 100) rs = rs.substring(0, 100);
  @RES@ r = @PKG@.AhStore.adminRemove(pr.getUsername(), id == null ? "" : id.trim().replace("#", ""), rs);
  @PKG@.AhStore.afterTrade(r, null, null, null, null);
  atell(pr, r.msg);
}""")
M(cmds, r"""
public static void reload(@PR@ pr) {
  @PKG@.AhStore.reloadCfg();
  int n = @PKG@.AhCfg.loadBlocked();
  atell(pr, "config.properties and Skyy_Market/blocked.txt re-read (" + n + " blocked entries from the file). Listings are not re-read.");
  atell(pr, @PKG@.AhCfg.summary());
  if (@PKG@.AhCfg.TEST_ON.length() > 0) atell(pr, "TEST DURATIONS ARE ON: " + @PKG@.AhCfg.TEST_ON);
  @PKG@.AhStore.publishCount();
}""")
M(cmds, r"""
public static void pause(@PR@ pr, boolean on) {
  boolean ok = @PKG@.AhCfg.setPaused(on);
  @PKG@.AhLog.log(on ? "PAUSE" : "RESUME", null, "by=" + @PKG@.AhUtil.tok(pr.getUsername()));
  atell(pr, (on ? "Paused: no new listings or buys (cancel and claims still work)." : "Resumed: listing and buying are open again.") + (ok ? "" : " (Could not write config.properties - it lasts until a restart.)"));
}""")
M(cmds, r"""
public static void regrant(@PR@ pr, String id, String side, boolean confirm) {
  String i = id == null ? "" : id.trim().replace("#", "");
  String s = side == null ? "" : side.trim().toLowerCase();
  if (!confirm) {
    java.util.ArrayList lines = @PKG@.AhStore.regrantPreview(pr.getUuid(), i, s);
    for (int k = 0; k < lines.size(); k++) atell(pr, (String) lines.get(k));
    return;
  }
  @RES@ r = @PKG@.AhStore.regrant(pr.getUuid(), pr.getUsername(), i, s);
  @PKG@.AhStore.afterTrade(r, null, null, null, null);
  atell(pr, r.msg);
}""")

# ================= commands =================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []


def exe(cls, body, what):
    M(cls, EXEC + " {\n  try {\n    " + body + "\n  } catch (Throwable t) {\n    @PKG@.AhUtil.warn(\"" + what + " failed: \" + t);\n"
      "    pr.sendMessage(@MSG@.raw(\"[Auction House] Something went wrong - the server log has the details.\"));\n  }\n}")


def mk(name):
    c = pool.makeClass(PKG + "." + name, pool.get(T["APC"]))
    CMDS.append(c)
    return c


# ---- player commands (each constructor has setPermissionGroups; subcommands / variants BEFORE the class that adds them)
c_selld = mk("AhSellDurCmd")
F(c_selld, "public @RA@ priceArg;")
F(c_selld, "public @RA@ durArg;")
C(c_selld, r"""
public AhSellDurCmd() {
  super("Sell the item in your hand for a price and a duration: /ah sell <price> <duration>");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  this.priceArg = withRequiredArg("price", "500, 12k, 1.5m or 2b", @ATY@.STRING);
  this.durArg = withRequiredArg("duration", "a preset like 1h, 6h, 12h, 24h or 48h", @ATY@.STRING);
}""")
exe(c_selld, "@PKG@.AhCmds.sell(pr, ref, store, String.valueOf(ctx.get(this.priceArg)), String.valueOf(ctx.get(this.durArg)));", "/ah sell")

c_sell = mk("AhSellCmd")
F(c_sell, "public @RA@ priceArg;")
C(c_sell, r"""
public AhSellCmd() {
  super("sell", "Sell the item in your hand: /ah sell <price> [duration]");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  this.priceArg = withRequiredArg("price", "500, 12k, 1.5m or 2b", @ATY@.STRING);
  addUsageVariant(new @PKG@.AhSellDurCmd());
}""")
exe(c_sell, "@PKG@.AhCmds.sell(pr, ref, store, String.valueOf(ctx.get(this.priceArg)), (String) null);", "/ah sell")

c_claim = mk("AhClaimCmd")
C(c_claim, r"""
public AhClaimCmd() {
  super("claim", "Claim everything the Auction House owes this profile");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
exe(c_claim, "@PKG@.AhCmds.claim(pr, ref, store);", "/ah claim")

c_man = mk("AhManageCmd")
C(c_man, r"""
public AhManageCmd() {
  super("manage", "Open your Auction House listings and claims");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addAliases(new String[] { "mine" });
}""")
exe(c_man, "@PKG@.AhCmds.open(pr, ref, store, new @PKG@.AhPage(pr, \"manage\"));", "/ah manage")

c_srch = mk("AhSearchCmd")
F(c_srch, "public @RA@ wordsArg;")
C(c_srch, r"""
public AhSearchCmd() {
  super("search", "Search the Auction House: /ah search <words>");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  this.wordsArg = withRequiredArg("words", "item or seller name", @ATY@.GREEDY_STRING);
  setAllowsExtraArguments(true);
}""")
exe(c_srch, r"""String w = @PKG@.AhUtil.rest(ctx.getInputString(), "search", 0);
    if (w.length() == 0) w = String.valueOf(ctx.get(this.wordsArg));
    @PKG@.AhCmds.search(pr, ref, store, w);""", "/ah search")

c_ah = mk("AhCmd")
C(c_ah, r"""
public AhCmd() {
  super("ah", "Open the Auction House (Buy It Now) - /ah sell, /ah claim, /ah manage, /ah search");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addAliases(new String[] { "auction", "auctionhouse" });
  addSubCommand(new @PKG@.AhSellCmd());
  addSubCommand(new @PKG@.AhClaimCmd());
  addSubCommand(new @PKG@.AhManageCmd());
  addSubCommand(new @PKG@.AhSearchCmd());
}""")
exe(c_ah, "@PKG@.AhCmds.open(pr, ref, store, new @PKG@.AhPage(pr, \"browse\"));", "/ah")

# ---- admin commands (every constructor calls requirePermission; a subcommand is dispatched before the root's permission check)
c_alp = mk("AhAdminListPlayerCmd")
F(c_alp, "public @RA@ whoArg;")
C(c_alp, r"""
public AhAdminListPlayerCmd() {
  super("(admin) a player's open records, any profile: /ahadmin list <player>");
  requirePermission("skyyauctions.admin");
  this.whoArg = withRequiredArg("player", "seller or buyer name as stored on the records", @ATY@.STRING);
}""")
exe(c_alp, "@PKG@.AhCmds.list(pr, String.valueOf(ctx.get(this.whoArg)));", "/ahadmin list")

c_al = mk("AhAdminListCmd")
C(c_al, r"""
public AhAdminListCmd() {
  super("list", "(admin) the 10 newest active listings, or /ahadmin list <player>");
  requirePermission("skyyauctions.admin");
  addUsageVariant(new @PKG@.AhAdminListPlayerCmd());
}""")
exe(c_al, "@PKG@.AhCmds.list(pr, (String) null);", "/ahadmin list")

c_ai = mk("AhAdminInfoCmd")
F(c_ai, "public @RA@ idArg;")
C(c_ai, r"""
public AhAdminInfoCmd() {
  super("info", "(admin) every field of one record, live or archived: /ahadmin info <id>");
  requirePermission("skyyauctions.admin");
  this.idArg = withRequiredArg("id", "listing number", @ATY@.STRING);
}""")
exe(c_ai, "@PKG@.AhCmds.info(pr, String.valueOf(ctx.get(this.idArg)));", "/ahadmin info")

c_arw = mk("AhAdminRemoveWhyCmd")
F(c_arw, "public @RA@ idArg;")
F(c_arw, "public @RA@ whyArg;")
C(c_arw, r"""
public AhAdminRemoveWhyCmd() {
  super("(admin) remove an active listing with a reason shown to the seller: /ahadmin remove <id> <reason...>");
  requirePermission("skyyauctions.admin");
  this.idArg = withRequiredArg("id", "listing number", @ATY@.STRING);
  this.whyArg = withRequiredArg("reason", "shown to the seller", @ATY@.GREEDY_STRING);
}""")
exe(c_arw, r"""String why = @PKG@.AhUtil.rest(ctx.getInputString(), "remove", 1);
    if (why.length() == 0) why = String.valueOf(ctx.get(this.whyArg));
    @PKG@.AhCmds.remove(pr, String.valueOf(ctx.get(this.idArg)), why);""", "/ahadmin remove")

c_ar = mk("AhAdminRemoveCmd")
F(c_ar, "public @RA@ idArg;")
C(c_ar, r"""
public AhAdminRemoveCmd() {
  super("remove", "(admin) remove an active listing, the item goes back to the seller's claims: /ahadmin remove <id> [reason]");
  requirePermission("skyyauctions.admin");
  this.idArg = withRequiredArg("id", "listing number", @ATY@.STRING);
  setAllowsExtraArguments(true);
  addUsageVariant(new @PKG@.AhAdminRemoveWhyCmd());
}""")
exe(c_ar, r"""String why = @PKG@.AhUtil.rest(ctx.getInputString(), "remove", 1);
    @PKG@.AhCmds.remove(pr, String.valueOf(ctx.get(this.idArg)), why);""", "/ahadmin remove")

c_arl = mk("AhAdminReloadCmd")
C(c_arl, r"""
public AhAdminReloadCmd() {
  super("reload", "(admin) re-read config.properties and Skyy_Market/blocked.txt");
  requirePermission("skyyauctions.admin");
}""")
exe(c_arl, "@PKG@.AhCmds.reload(pr);", "/ahadmin reload")

c_ap = mk("AhAdminPauseCmd")
C(c_ap, r"""
public AhAdminPauseCmd() {
  super("pause", "(admin) stop new listings and buys (cancel and claims still work)");
  requirePermission("skyyauctions.admin");
}""")
exe(c_ap, "@PKG@.AhCmds.pause(pr, true);", "/ahadmin pause")

c_aru = mk("AhAdminResumeCmd")
C(c_aru, r"""
public AhAdminResumeCmd() {
  super("resume", "(admin) open listing and buying again");
  requirePermission("skyyauctions.admin");
}""")
exe(c_aru, "@PKG@.AhCmds.pause(pr, false);", "/ahadmin resume")

c_rgo = mk("AhAdminRegrantOkCmd")
F(c_rgo, "public @RA@ idArg;")
F(c_rgo, "public @RA@ sideArg;")
F(c_rgo, "public @RA@ okArg;")
C(c_rgo, r"""
public AhAdminRegrantOkCmd() {
  super("(admin) apply a previewed regrant: /ahadmin regrant <id> <seller|buyer> confirm");
  requirePermission("skyyauctions.admin");
  this.idArg = withRequiredArg("id", "listing number", @ATY@.STRING);
  this.sideArg = withRequiredArg("side", "seller or buyer", @ATY@.STRING);
  this.okArg = withRequiredArg("confirm", "the word confirm", @ATY@.STRING);
}""")
exe(c_rgo, r"""String ok = String.valueOf(ctx.get(this.okArg)).trim();
    if (!ok.equalsIgnoreCase("confirm")) { @PKG@.AhCmds.atell(pr, "The third word must be confirm: /ahadmin regrant <id> <seller|buyer> confirm"); return; }
    @PKG@.AhCmds.regrant(pr, String.valueOf(ctx.get(this.idArg)), String.valueOf(ctx.get(this.sideArg)), true);""", "/ahadmin regrant")

c_rg = mk("AhAdminRegrantCmd")
F(c_rg, "public @RA@ idArg;")
F(c_rg, "public @RA@ sideArg;")
C(c_rg, r"""
public AhAdminRegrantCmd() {
  super("regrant", "(admin) PREVIEW a claim repair after a crash: /ahadmin regrant <id> <seller|buyer> [confirm]");
  requirePermission("skyyauctions.admin");
  this.idArg = withRequiredArg("id", "listing number", @ATY@.STRING);
  this.sideArg = withRequiredArg("side", "seller or buyer", @ATY@.STRING);
  addUsageVariant(new @PKG@.AhAdminRegrantOkCmd());
}""")
exe(c_rg, "@PKG@.AhCmds.regrant(pr, String.valueOf(ctx.get(this.idArg)), String.valueOf(ctx.get(this.sideArg)), false);", "/ahadmin regrant")

c_adm = mk("AhAdminCmd")
C(c_adm, r"""
public AhAdminCmd() {
  super("ahadmin", "(admin) Auction House status and tools: list, info, remove, reload, pause, resume, regrant");
  requirePermission("skyyauctions.admin");
  addSubCommand(new @PKG@.AhAdminListCmd());
  addSubCommand(new @PKG@.AhAdminInfoCmd());
  addSubCommand(new @PKG@.AhAdminRemoveCmd());
  addSubCommand(new @PKG@.AhAdminReloadCmd());
  addSubCommand(new @PKG@.AhAdminPauseCmd());
  addSubCommand(new @PKG@.AhAdminResumeCmd());
  addSubCommand(new @PKG@.AhAdminRegrantCmd());
}""")
exe(c_adm, "@PKG@.AhCmds.status(pr);", "/ahadmin")

# ================= tick, join notices, session guard =================
tick.addInterface(pool.get("java.lang.Runnable"))
C(tick, "public AhTick() { }")
M(tick, r"""
public void run() {
  try {
    long now = System.currentTimeMillis();
    java.util.ArrayList notes = @PKG@.AhStore.expireDue(now);
    for (int i = 0; i < notes.size(); i++) {
      Object[] n = (Object[]) notes.get(i);
      @PKG@.AhStore.tell((java.util.UUID) n[0], (String) n[1]);
    }
    if (!@PKG@.AhStore.DIRTY.isEmpty() || !@PKG@.AhStore.ARCH.isEmpty()) @PKG@.AhStore.retryDirty();
    @PKG@.AhStore.publishCount();
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null) @PKG@.AhStore.publishClaims(p.getUuid());
    }
    @PKG@.AhLog.rotate();
  } catch (Throwable t) { @PKG@.AhUtil.warn("tick failed: " + t); }
}""")
note.addInterface(pool.get("java.lang.Runnable"))
F(note, "public @PR@ pr;")
C(note, "public AhNoticeTask(@PR@ pr) { this.pr = pr; }")
M(note, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID u = pr.getUuid();
    java.util.ArrayList lines = @PKG@.AhStore.notices(u);
    for (int i = 0; i < lines.size() && i < 5; i++) pr.sendMessage(@MSG@.raw("[Auction House] While you were away: " + lines.get(i)));
    if (lines.size() > 5) pr.sendMessage(@MSG@.raw("[Auction House] ...and " + (lines.size() - 5) + " more."));
    long[] ow = @PKG@.AhStore.owedFor(@PKG@.AhUtil.pkey(u));
    if (ow[0] > 0L) pr.sendMessage(@MSG@.raw("[Auction House] You have " + ow[0] + (ow[0] == 1L ? " thing" : " things") + " to claim - /ah claim."));
    @PKG@.AhStore.publishClaims(u);
  } catch (Throwable t) { @PKG@.AhUtil.warn("join notice failed: " + t); }
}""")
# PlayerReadyEvent fires on EVERY world switch -> once per session (cleared on disconnect)
rdy.addInterface(pool.get("java.util.function.Consumer"))
C(rdy, "public AhReady() { }")
M(rdy, r"""
public void accept(Object ev) {
  try {
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    if (@PKG@.AhStore.SESSION.putIfAbsent(pr.getUuid(), Boolean.TRUE) != null) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.AhNoticeTask(pr), 3L, java.util.concurrent.TimeUnit.SECONDS);
  } catch (Throwable t) { @PKG@.AhUtil.warn("ready handler failed: " + t); }
}""")
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public AhQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr != null) @PKG@.AhStore.SESSION.remove(pr.getUuid());
  } catch (Throwable t) { }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyAuctionsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.AhUtil.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyAuctions");
  @PKG@.AhCfg.DIR = dir;
  @PKG@.AhCfg.FILE = dir.resolve("config.properties");
  @PKG@.AhCfg.BLOCKED = dir.resolveSibling("Skyy_Market").resolve("blocked.txt");
  @PKG@.AhLog.FILE = dir.resolve("auctions.log");
  @PKG@.AhStore.DIR = dir;
  @PKG@.AhStore.LDIR = dir.resolve("listings");
  @PKG@.AhStore.ADIR = dir.resolve("archive");
  @PKG@.AhStore.BADDIR = dir.resolve("listings").resolve("bad");
  @PKG@.AhStore.STATE = dir.resolve("state.properties");
  @PKG@.AhCfg.load();
  int nb = @PKG@.AhCfg.loadBlocked();
  int n = @PKG@.AhStore.load();
  int rs = @PKG@.AhStore.restoreFromLog();
  int un = @PKG@.AhLog.scanStarts();
  getCommandRegistry().registerCommand(new @PKG@.AhCmd());
  getCommandRegistry().registerCommand(new @PKG@.AhAdminCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.AhReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.AhQuit());
  @OCU@.registerSimple(this, @PKG@.SkyyAuctionsPlugin.class, "SkyyAuctions", new @PKG@.AhPageFactory());
  java.util.Map b = @PKG@.AhUtil.bridge();
  b.put("auction:fn:lowestBin", new @PKG@.AhLowestBinFn());
  b.put("auction:version", "@VERSION@");
  @PKG@.AhStore.publishCount();
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.AhTick(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  @PKG@.AhLog.log("BOOT", null, "version=@VERSION@ open=" + n + " next=" + @PKG@.AhStore.NEXT);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyAuctions] @VERSION@ ready - /ah (/auction, /auctionhouse), /ahadmin; " + n + " open records, next #" + @PKG@.AhStore.NEXT + ", " + nb + " blocked entries from Skyy_Market/blocked.txt, coins bridge " + (@PKG@.Coins.ready() ? "found" : "NOT found yet") + (un > 0 ? ", " + un + " unfinished trades in the log (see /ahadmin)" : "") + (rs > 0 ? ", " + rs + " listings restored from auctions.log (see /ahadmin)" : "") + "; data in " + dir);
  if (@PKG@.AhCfg.TEST_ON.length() > 0) getLogger().at(java.util.logging.Level.WARNING).log("[SkyyAuctions] TEST DURATIONS ARE ON: " + @PKG@.AhCfg.TEST_ON);
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  boolean clean = true;
  try { clean = @PKG@.AhStore.retryDirty() && @PKG@.AhStore.DIRTY.isEmpty(); } catch (Throwable t) { clean = false; }
  try {
    java.util.Map b = @PKG@.AhUtil.bridge();
    java.util.Iterator it = new java.util.ArrayList(b.keySet()).iterator();
    while (it.hasNext()) { Object k = it.next(); if (k instanceof String && ((String) k).startsWith("auction:")) b.remove(k); }
  } catch (Throwable t) { }
  try { @PKG@.AhCfg.removeFileEntries(); } catch (Throwable t) { }
  if (clean) @PKG@.AhLog.log("STOP", null, "clean");
  else @PKG@.AhUtil.warn("shutdown: " + @PKG@.AhStore.DIRTY.size() + " listing records could not be saved - no STOP line written (see auctions.log WRITE-FAILED)");
  super.shutdown();
}""")

ALL = [utl, cfg, lg, coin, rec, itm, res, srt, sto, lfn, page, fac, cmds] + CMDS + [tick, note, rdy, quit_, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written:", len(ALL))

jar = os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)
m = B.manifest("SkyyAuctions", VERSION, "SkyWynn Auction House: /ah Buy It Now listings with claims, fees, a synced log and admin repair tools. Uses the SkyyCoins bridge, zero dependencies.", PKG + ".SkyyAuctionsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    raise SystemExit("SkyyAuctions: --deploy is not supported here - deploys go through tools/deploy_set.py")
