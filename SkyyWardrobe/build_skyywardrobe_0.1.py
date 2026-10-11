"""SkyyWardrobe 0.1 - build script (javassist via jpype, tools/skyybuild.py). NEW MOD (no older version; the next version copies this
file or gets a patch script). Owner: Skyy (they/them).
Run:   python SkyyWardrobe/build_skyywardrobe_0.1.py   -> SkyyWardrobe/SkyyWardrobe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Test:  python SkyyWardrobe/test_skyywardrobe_0.1.py --dir tools/dev/scratch/<task>/test   (bare-JVM harness)

WHY (Skyy's own words; docs/answered/gear.md LOCKED 2026-10-10 "WARDROBE = LOADOUTS - build it now"):
  "build the wardrobe/ loadout system too. (in the loadouts i want to be able to setup Armor, (hot bar if its not too hard.) Pets, and
  active abilities and their modifiers. so you can setup several combat sets with different pets and ability's. different foraging
  sets for mining/farming with different pets armor, tools in the hot bar, and ability's. (we might add ability's to the foraging trees
  later. but they will be the same across every class, and pretty simple.)"
  "Oh yeah, and the wardrobe thing for quick swapping armor should be a full loadout swapper, so you make a loadout with the armor, and
  pets you want. (later maybe even hot bar)"
Spec: research/cloud/Wardrobe-Spec.md W1 + its 'Scope change' line (section 11 questions take their [defaults]); Looks (W2) are NOT here.

WHAT A LOADOUT IS (per PROFILE, tools/PROFILES-CONTRACT.md: one file per storage key, profile:busy respected):
  name (16 characters, Server Setup nameMax) + ARMOR (the 4 worn pieces) + HOTBAR (the 9 hotbar slots; an item listed in swap.keepIds -
  default the SkyWynn Menu item Skyy_Menu and the vault arrows Skyy_Vault_* - is never moved and never stored) + the PET slot + SUMMON slot
  pet ids (references only: pets are SkyyPets records, never items) + the ACTIVE ABILITIES and their modifiers (one SkyyClasses snapshot
  String, class:fn:loadoutGet / loadoutSet - SkyyClasses 0.1.19).
THE MODEL (SkyBlock wardrobe, made a loadout swapper; decisions in the build report):
  - At most ONE loadout per profile is EQUIPPED (the card says so): what you wear IS that loadout. Its stored spots are normally empty -
    the gear is on you, and its card shows your live armor + hotbar.
  - EQUIP n: one world-thread task. For each armor spot and hotbar slot: the stored piece of n goes on; what you wear in that spot goes
    HOME to the equipped loadout (its spot is free) - else into n (the spot n's piece just left: always free). Where n stores nothing the
    worn piece STAYS ON (LOCKED gear.md 2026-10-08 "partial sets keep the worn piece", spec Q3; Server Setup swap.strict ON = it goes
    home too and you wear exactly loadout n). An EMPTY loadout (no items at all) is the put-away: everything you wear goes home. The
    pets + abilities you have now are kept with the loadout you leave (same file write); n becomes the equipped loadout; then the pets
    (pets:fn:loadoutSet) and abilities (class:fn:loadoutSet) of n are applied. Items first, under the write-ahead journal (spec 5.2), then
    the bridge calls; a bridge part that fails is reported, nothing is half-lost.
  - SAVE CURRENT n: n becomes the equipped loadout (nothing moves - what you wear now belongs to n) and stores the pet / summon ids and the
    ability snapshot you have now. On the equipped loadout itself it just updates pets + abilities. Refused while ANOTHER loadout is
    equipped (it would steal that loadout's gear - Equip the empty loadout first: your gear goes home, then put on the new gear) and on a
    loadout that still stores gear (Equip it or Clear it first).
  - CLEAR n (asks twice on the page): its stored gear goes to your inventory, storage first (a stack that does not fit WHOLE stays stored,
    "Inventory full"), its pets / abilities / name are forgotten; clearing the equipped loadout only unlinks it (your gear stays on you).
    Clear (and the crash repair) still work while wardrobe.enabled is off, so players can always take their gear out.
  - RENAME n: the name typed in the page's name box (letters, digits, space, - and ').
  - Refused while dead, in combat (combatSeconds 10, DamageDataComponent), within swap.gapSeconds (1 s) of the last change, while
    profile:busy, within afterSwitchSeconds (30 s) after a profile switch / a busy crash recovery (SkyyProfiles' rollback window), and one
    change at a time per player (a double click is refused; the page token makes a click from a stale page rebuild the page).
  - Slots: slots.free (4) + slots.byLevel (6:10, 10:20, 14:30, 18:40 = slots : Overall Level, skill:fn:overall) + the admin floor
    (/wardrobeadmin slots), at most slots.max (18). A locked slot that still holds gear can still be equipped or cleared ("locked but full").
DUPE / LOSS SAFETY:
  - Files: Skyy_SkyyWardrobe/loadouts/<pkey>.json - the SkyyVault / SkyyProfiles lossless slot format (explicit fields + the engine's
    ItemStack.CODEC, EXTENDED JSON), tmp + fsync + ATOMIC_MOVE (5 x 20 ms retries), read back and the stack count compared, a rev number.
    An unreadable / newer-format file keeps that wardrobe SHUT (nothing ever written over it). Undecodable stacks go to "orphans" (kept,
    retried at every load, never dropped). wardrobe.log = one line per EQUIP / SAVE / CLEAR / RENAME / REPAIR / ADMIN.
  - The journal (loadouts/<pkey>.journal.json, format 2) is written BEFORE any item moves. It is a CHAIN of steps: a change made while
    an earlier saved change is still inside its keep window JOINS that journal (never overwrites it). Each step = every move (which spot,
    the piece going on, the piece coming off and where it goes; for a Clear: every stack and the live count of its kind before) + "pre",
    the wardrobe document as it was before the step; the journal carries the profile epoch. A failure inside the task is rolled back in
    the same task (verified slot by slot) and the journal goes back to its earlier saved steps; a failed rollback marks the journal
    "failed" and shuts that wardrobe until /wardrobeadmin repair. After the save the journal stays journalKeepSeconds (30 s - the engine
    saves players every 10 s) from its NEWEST step, then the 1 s timer deletes it (only while the file says "saved"). A server CRASH
    inside that time is repaired at the next join (world thread, after profile:busy clears): newest step first, a step with no trace in
    the LIVE inventory is undone exactly (its "pre"), the first step that did reach the inventory is reconciled spot by spot, so every
    piece exists exactly once. A journal is reconciled whenever its key is active again (no epoch rule: a profile switched away from was
    saved by SkyyProfiles after the change, so its moves read "happened"; the epoch also moves WITHOUT a save). Evidence is loose where use
    changes a piece: a swapped-in stack eaten from / used / moved still counts (same kind; per-kind counts from before the swap). A
    stored piece a repair displaces is parked in a free spot of another loadout (else an orphan with its loadout origin, retried at every
    load) - never lost, always reachable. A repair that cannot be saved stops the change that triggered it.
ENGINE CHECKS (spec section 9; desk / bytecode, HytaleServer.jar of 2026-10-10 - details in the build report):
  E1 ItemContainer.setItemStackForSlot(s, stack, false) / removeItemStackFromSlot(s, false) -> sendUpdate -> ItemContainerChangeEvent ->
     InventoryComponent.markChanged + its change queue -> InventorySystems$LegacyArmorChangeStatSystem sets OutdatedEquipment and
     schedules the stat recalculation (the worn model + stats refresh; SkyyProfiles 0.1.6 does the same writes in game).
  E2 the same queue feeds InventorySystems$ArmorChangeEventSystem / HotbarChangeEventSystem -> InventoryChangeEvent (SkyyGear's
     GearFxInvSys sees every swap - no extra call needed).
  E5 death opens the engine's RespawnPage (DeathSystems$PlayerDeathScreen), which replaces any open custom page; every change refuses
     while dead anyway.
  E6 the page is rebuilt only after a click (never on a timer); swap.gapSeconds + the per-player busy flag + the page token.
BRIDGE: publishes wardrobe:fn:open (Function apply(UUID) -> Boolean: TRUE = the Wardrobe page will open on that player's world thread)
  for SkyyMenu's tile. Reads profile:fn:key / profile:busy:<uuid> / profile:epoch:<uuid>, skill:fn:overall (skill:overall:<uuid>),
  pets:fn:loadoutGet / pets:fn:loadoutSet / pets:fn:petName (SkyyPets 0.2.3+, contract in the build report), class:fn:loadoutGet /
  class:fn:loadoutSet (SkyyClasses 0.1.19+). Missing keys = that part is greyed with a short note, nothing else changes.
KNOWN LIMIT: the rest of the inventory is the engine's own (the ~10 s player-save window every Skyy storage mod has); the journal covers
  the wardrobe's own moves within journalKeepSeconds.
"""
import sys, os, re, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
import skyyui as SUI       # the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md)
SUI.verify()               # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only)
KIT_ID = SUI.kit_id()

VERSION = "0.1"
MOD = "SkyyWardrobe"
NODE = "skyywardrobe.admin"
PKG = "com.skyy.wardrobe"
HERE = os.path.dirname(os.path.abspath(__file__))
CFG_FILE = "Skyy_SkyyWardrobe/config.properties"
COL = SUI.COLOR
COL_OK, COL_ERR, COL_INFO, COL_GOLD = COL["success"], COL["error"], COL["info"], COL["gold"]
MAX_SLOTS = 18            # 2 pages of 9 in SkyBlock; the hard cap of slots.max
ARMOR_N, HOT_N = 4, 9     # Head, Chest, Hands, Legs; the 9 hotbar slots
SPOT_NAMES = ["head", "chest", "hands", "legs"]

J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "KITID": KIT_ID,
    "COLOK": COL_OK, "COLERR": COL_ERR, "COLINF": COL_INFO, "COLGLD": COL_GOLD,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CT": "com.hypixel.hytale.component.ComponentType",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "ARM": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor",
    "HOT": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "STO": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage",
    "BAK": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack",
    "STX": "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction",
    "ISX": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "CODEC": "com.hypixel.hytale.codec.Codec",
    "ITEM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "DDC": "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent",
    "DEATH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "TR": "com.hypixel.hytale.server.core.modules.time.TimeResource",
    "PRE": "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
}
AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PB_ = "com.hypixel.hytale.server.core.plugin.PluginBase"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
# API probes: every engine member this mod calls (catches API drift at build time)
for c, m in ((T["PR"], "getUuid"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"), (T["PR"], "getComponentType"), (T["PR"], "getReference"),
             (T["PR"], "getWorldUuid"), (T["UNI"], "get"), (T["UNI"], "getPlayers"), (T["UNI"], "getPlayer"), (T["UNI"], "getWorld"),
             (T["WLD"], "execute"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["PLA"], "getComponentType"),
             (T["PLA"], "getPageManager"), (PGM, "openCustomPage"), (T["REF"], "getStore"), (T["REF"], "isValid"), (T["ST"], "getComponent"),
             (T["ST"], "getResource"), (T["PAGE"], "rebuild"), (T["PAGE"], "close"), (T["PAGE"], "handleDataEvent"), (T["EVD"], "of"),
             (T["EVD"], "append"), (T["UEB"], "addEventBinding"), (T["UCB"], "set"), (T["UCB"], "appendInline"), (T["BT"], "Activating"),
             (T["LIFE"], "CanDismiss"), (T["IS"], "CODEC"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "getDurability"),
             (T["IS"], "getMaxDurability"), (T["IS"], "getQualityIndex"), (T["IS"], "getMetadata"), (T["IS"], "isEmpty"),
             (T["IS"], "getOverrideDroppedItemAnimation"), (T["IS"], "setOverrideDroppedItemAnimation"), (T["CODEC"], "encode"),
             (T["CODEC"], "decode"), (T["IC"], "getItemStack"), (T["IC"], "getCapacity"), (T["IC"], "setItemStackForSlot"),
             (T["IC"], "removeItemStackFromSlot"), (T["IC"], "addItemStack"), (T["IC"], "canAddItemStack"), (T["IC"], "removeItemStack"), (T["IS"], "withQuantity"),
             (T["STX"], "succeeded"), (T["ISX"], "getRemainder"), (T["ISX"], "succeeded"), (T["INVC"], "getInventory"),
             (T["ARM"], "getComponentType"), (T["HOT"], "getComponentType"), (T["STO"], "getComponentType"), (T["BAK"], "getComponentType"),
             (T["ITEM"], "getAssetMap"), (T["DDC"], "getComponentType"), (T["DDC"], "getLastDamageTime"), (T["DDC"], "getLastCombatAction"),
             (T["DEATH"], "getComponentType"), (T["TR"], "getResourceType"), (T["TR"], "getNow"), (T["PRE"], "getPlayerRef"),
             (T["PDE"], "getPlayerRef"), ("org.bson.BsonDocument", "parse"), ("org.bson.BsonDocument", "toJson"),
             ("org.bson.json.JsonWriterSettings", "builder"), ("org.bson.json.JsonMode", "EXTENDED"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             (AC, "requirePermission"), (AC, "setPermissionGroups"), (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "addAliases"),
             (T["CTX"], "get"), (T["ATY"], "STRING"), (PB_, "getCommandRegistry"), (PB_, "getEventRegistry"), (PB_, "getLogger"),
             (PB_, "getDataDirectory"), (PB_, "shutdown"), ("com.hypixel.hytale.event.EventRegistry", "registerGlobal")):
    B.probe(pool, c, m)
_sig = lambda cls, name: [str(mm.getSignature()) for mm in pool.get(cls).getDeclaredMethods() if str(mm.getName()) == name]
# the exact overloads the swap uses (E1): set / remove WITHOUT the slot filters (a piece only ever goes back to the slot type it came from)
assert "(SLcom/hypixel/hytale/server/core/inventory/ItemStack;Z)Lcom/hypixel/hytale/server/core/inventory/transaction/ItemStackSlotTransaction;" in _sig(T["IC"], "setItemStackForSlot")
assert "(SZ)Lcom/hypixel/hytale/server/core/inventory/transaction/SlotTransaction;" in _sig(T["IC"], "removeItemStackFromSlot")
assert "(Lcom/hypixel/hytale/server/core/inventory/ItemStack;)Z" in _sig(T["IC"], "canAddItemStack")
assert "(Lcom/hypixel/hytale/server/core/inventory/ItemStack;)Lcom/hypixel/hytale/server/core/inventory/transaction/ItemStackTransaction;" in _sig(T["IC"], "addItemStack")
assert "(Lcom/hypixel/hytale/server/core/inventory/ItemStack;)Lcom/hypixel/hytale/server/core/inventory/transaction/ItemStackTransaction;" in _sig(T["IC"], "removeItemStack")

TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:4000]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2000]))


def jstr(s):
    return json.dumps(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs) if xs else "new String[0]"


ALL = []


def cls(name, sup=None):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    ALL.append(c)
    return c


def iface(name):
    c = pool.makeInterface(PKG + "." + name)
    ALL.append(c)
    return c


# every class first (javassist resolves a call only to a class that exists; methods are added callee-first below)
log = cls("WdLog")
api = iface("WdApi")
inv = iface("WdInvApi")
eng = cls("WdEng")
cfgc = cls("WdCfg")
cod = cls("WdCodec")
lo = cls("WdLoad")
dat = cls("WdData")
sto = cls("WdStore")
jr = cls("WdJournal")
slt = cls("WdSlots")
brg = cls("WdBridge")
tx = cls("WdTx")
gate = cls("WdGate")
ops = cls("WdOps")
page = cls("WdPage", T["PAGE"])
rtask = cls("WdRepairTask")
hop = cls("WdHop")
otask = cls("WdOpenTask")
ftask = cls("WdFloorTask")
ofn = cls("WdOpenFn")
timer = cls("WdTimer")
ready = cls("WdReady")
quit_ = cls("WdQuit")
cmds = cls("WdCmds")

# =====================================================================================================================
# WdLog: server log (+ LINES, a harness hook) + the bridge helpers
# =====================================================================================================================
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List LINES;")
F(log, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(log, r"""
public static void info(String msg) {
  try { if (LINES != null) LINES.add("INFO " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyWardrobe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LINES != null) LINES.add("WARN " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyWardrobe] " + msg); } catch (Throwable t) { }
}""")
# at most once a minute per key (spec 5.1: an unreadable wardrobe is warned once a minute)
M(log, r"""
public static void warnOnce(String key, String msg) {
  long now = System.currentTimeMillis();
  Object last = ONCE.get(key);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L && now >= ((Long) last).longValue()) return;
  if (ONCE.size() > 2000) ONCE.clear();
  ONCE.put(key, Long.valueOf(now));
  warn(msg);
}""")
M(log, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(log, r"""
public static java.util.function.Function fn(String key) {
  try { Object o = bridge().get(key); return o instanceof java.util.function.Function ? (java.util.function.Function) o : null; } catch (Throwable t) { return null; }
}""")
M(log, r"""
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
}""")
M(log, r"""
public static String body(String res) {
  if (res == null) return "";
  if (res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-' || res.charAt(0) == '=')) return res.substring(1);
  return res;
}""")

# =====================================================================================================================
# WdApi (online players, names, chat) + WdInvApi (the inventory sections) = the harness seams; null in game = the real engine calls
# =====================================================================================================================
for sig in ("public abstract java.util.UUID[] online();",
            "public abstract java.util.UUID byName(String name);",
            "public abstract String nameOf(java.util.UUID u);",
            "public abstract void tell(java.util.UUID u, String text, String color);"):
    M(api, sig)
M(inv, "public abstract @IC@ section(@ST@ st, @REF@ ref, int which);")
F(eng, "public static volatile @PKG@.WdApi API = null;")
M(eng, r"""
public static void say(@PR@ pr, String text, String color) {
  if (pr == null) return;
  try { @MSG@ m = @MSG@.raw(text); if (color != null) m = m.color(color); pr.sendMessage(m); } catch (Throwable t) { }
}""")
M(eng, r"""
public static java.util.UUID[] online() {
  if (API != null) return API.online();
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUuid() != null) out.add(((@PR@) o).getUuid());
    }
  } catch (Throwable t) { }
  java.util.UUID[] a = new java.util.UUID[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (java.util.UUID) out.get(i);
  return a;
}""")
M(eng, r"""
public static java.util.UUID byName(String name) {
  if (name == null || name.trim().length() == 0) return null;
  if (API != null) return API.byName(name.trim());
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && name.trim().equalsIgnoreCase(((@PR@) o).getUsername())) return ((@PR@) o).getUuid();
    }
  } catch (Throwable t) { }
  return null;
}""")
M(eng, r"""
public static String nameOf(java.util.UUID u) {
  if (u == null) return "?";
  if (API != null) return API.nameOf(u);
  try { @PR@ pr = @UNI@.get().getPlayer(u); if (pr != null) return pr.getUsername(); } catch (Throwable t) { }
  return u.toString();
}""")
M(eng, r"""
public static void tell(java.util.UUID u, String text, String color) {
  if (u == null) return;
  if (API != null) { API.tell(u, text, color); return; }
  try { @PR@ pr = @UNI@.get().getPlayer(u); if (pr != null) say(pr, text, color); } catch (Throwable t) { }
}""")
M(eng, r"""
public static void reply(@PR@ pr, String res) {
  if (res == null || res.length() == 0 || pr == null) return;
  char c = res.charAt(0);
  String col = c == '+' ? "@COLOK@" : (c == '-' ? "@COLERR@" : "@COLINF@");
  say(pr, "[Wardrobe] " + @PKG@.WdLog.body(res), col);
}""")
M(eng, r"""
public static boolean open(@REF@ ref, @ST@ st, @PAGE@ pg) {
  if (ref == null || st == null || pg == null) return false;
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return false;
    p.getPageManager().openCustomPage(ref, st, pg);
    return true;
  } catch (Throwable t) { @PKG@.WdLog.warn("the Wardrobe page could not open: " + t); return false; }
}""")
# the world of an online player (null = offline / unknown)
M(eng, r"""
public static @WLD@ worldOf(java.util.UUID u) {
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || pr.getWorldUuid() == null) return null;
    return @UNI@.get().getWorld(pr.getWorldUuid());
  } catch (Throwable t) { return null; }
}""")

# =====================================================================================================================
# WdCfg (Server Setup > Wardrobe through tools/skyycfg.py)
# =====================================================================================================================
SCALARS = [
    # key, label, cat, type, default, min, max, opts, unit, flags, help, FIELD, java type
    ("wardrobe.enabled", "Wardrobe", "wd", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = no Equip / Save current / Rename. Clear still works, so players can take their gear out.", "ON", "boolean"),
    ("slots.free", "Free loadout slots", "wd", "int", "4", "1", str(MAX_SLOTS), "step=1", "", "live",
     "Loadouts every profile has without levels (SkyBlock gives 4).", "FREE", "int"),
    ("slots.max", "Most loadout slots", "wd", "int", str(MAX_SLOTS), "1", str(MAX_SLOTS), "step=1", "", "live",
     "Lowering it never deletes a loadout: one above it is locked but can still be equipped or cleared.", "MAX", "int"),
    ("slots.byLevel", "Slots by Overall Level", "wd", "text", "6:10,10:20,14:30,18:40", "1", "200", "", "", "live",
     "slots:level pairs, comma separated (6:10 = 6 slots from Overall Level 10). - = none.", "BYLEVEL", "java.lang.String"),
    ("swap.hotbar", "Hotbar in loadouts", "wd", "bool", "true", "", "", "", "", "live",
     "Off = Equip and Save current leave the hotbar alone (hotbar items a loadout stores stay stored).", "HOTBAR", "boolean"),
    ("swap.strict", "Strict swap (wear exactly the loadout)", "wd", "bool", "false", "", "", "", "", "live",
     "Off = a spot the loadout leaves empty keeps your worn piece (SkyBlock). On = it goes back home.", "STRICT", "boolean"),
    ("swap.keepIds", "Hotbar items never moved", "wd", "text", "Skyy_Menu,Skyy_Vault_*", "1", "400", "", "", "live,adv",
     "Item ids (a trailing * = any id starting so) that stay in the hotbar, never stored. - = none.", "KEEP_IDS", "java.lang.String"),
    ("swap.gapSeconds", "Time between two changes", "wd", "int", "1", "0", "30", "step=1", "s", "live",
     "Another Equip / Save current / Clear this soon is refused (double clicks).", "GAP_S", "int"),
    ("combatSeconds", "No change after combat", "wd", "int", "10", "0", "600", "step=1", "s", "live",
     "No loadout change this long after taking or dealing damage.", "COMBAT_S", "int"),
    ("afterSwitchSeconds", "Wait after a profile switch", "wd", "int", "30", "0", "120", "step=5", "s", "live,adv",
     "Loadouts stay shut this long after a profile switch. Under 30 s a server crash can dupe items.", "SETTLE_S", "int"),
    ("journalKeepSeconds", "Keep the swap journal", "wd", "int", "30", "5", "600", "step=5", "s", "live,adv",
     "A server crash this soon after a change is repaired at the next join (players save every 10 s).", "JKEEP_S", "int"),
    ("nameMax", "Loadout name length", "wd", "int", "16", "4", "32", "step=1", "", "live",
     "Most characters in a loadout name.", "NAME_MAX", "int"),
]
for _r in SCALARS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, (_r[0], len(_r[1]), len(_r[10]))
_chk = {"slots.byLevel": "WdCfg.checkLevels", "swap.keepIds": "WdCfg.checkIds"}
CFG_ROWS = [r[:11] + ("field:WdCfg.%s" % r[11] + (";check=%s" % _chk[r[0]] if r[0] in _chk else ""),) for r in SCALARS]
CFG_CATS = [("wd", "Wardrobe")]
CFG_NOTE = "Players: /wardrobe (alias /loadout). Admins: /wardrobeadmin info | slots | repair | reload."
assert len(CFG_NOTE) <= 100
_d = ["# SkyyWardrobe %s - loadouts (armor + hotbar + pets + abilities). Also in game: SkyWynn Menu > Server Setup > Wardrobe." % VERSION,
      "# Hand edits: /wardrobeadmin reload (or Server Setup > Wardrobe > Reload, or a restart). Times in seconds.", ""]
for _r in SCALARS:
    _d.append("# %s - %s" % (_r[1], _r[10]))
    _d.append("%s=%s" % (_r[0], _r[4]))
_d.append("")
DEFAULT_TEXT = "\n".join(_d)
_dp = CFG.parse_props(DEFAULT_TEXT)
for _r in SCALARS:
    assert _dp.get(_r[0]) == _r[4], _r[0]

for r in SCALARS:
    jt, fld, dv = r[12], r[11], r[4]
    if jt == "boolean":
        F(cfgc, "public static volatile boolean %s = %s;" % (fld, dv))
    elif jt == "int":
        F(cfgc, "public static volatile int %s = %d;" % (fld, int(dv)))
    else:
        F(cfgc, "public static volatile String %s = %s;" % (fld, jstr(dv)))
F(cfgc, "public static volatile int[] LEVELS = new int[0];")      # slots, level, slots, level ... (parsed slots.byLevel)
F(cfgc, "public static volatile String[] KEEP = new String[0];")  # parsed swap.keepIds
# the text each parse came from: Server Setup sets BYLEVEL / KEEP_IDS directly (field: rows), so levels() / keepList() re-parse on a change
F(cfgc, "public static volatile String LEVELS_SRC = null;")
F(cfgc, "public static volatile String KEEP_SRC = null;")
F(cfgc, "public static java.nio.file.Path FILE;")
F(cfgc, "public static volatile long LOADS = 0L;")
F(cfgc, "public static final String DEFAULT_TEXT = %s;" % jstr(DEFAULT_TEXT))
M(cfgc, r"""
public static boolean bv(java.util.Properties p, String k, boolean d) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null) return d;
  s = s.trim().toLowerCase();
  if (s.equals("true") || s.equals("on") || s.equals("yes") || s.equals("1")) return true;
  if (s.equals("false") || s.equals("off") || s.equals("no") || s.equals("0")) return false;
  return d;
}""")
M(cfgc, r"""
public static int iv(java.util.Properties p, String k, int d, int lo, int hi) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null) return d;
  try { int v = Integer.parseInt(s.trim()); return v < lo ? lo : (v > hi ? hi : v); } catch (Throwable t) { return d; }
}""")
M(cfgc, r"""
public static String sv(java.util.Properties p, String k, String d) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null || s.trim().length() == 0) return d;
  return s.trim();
}""")
# "6:10,10:20" -> { 6, 10, 10, 20 } (sorted by level); "-" / "" -> {}; null = not valid
M(cfgc, r"""
public static int[] parseLevels(String s) {
  if (s == null) return null;
  String t = s.trim();
  if (t.length() == 0 || t.equals("-")) return new int[0];
  String[] parts = t.split(",");
  int[] out = new int[parts.length * 2];
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int c = p.indexOf(':');
    if (c <= 0 || c >= p.length() - 1) return null;
    int sl = -1;
    int lv = -1;
    try { sl = Integer.parseInt(p.substring(0, c).trim()); lv = Integer.parseInt(p.substring(c + 1).trim()); } catch (Throwable e) { return null; }
    if (sl < 1 || sl > 18 || lv < 0 || lv > 100000) return null;
    out[i * 2] = sl;
    out[i * 2 + 1] = lv;
  }
  for (int i = 0; i < parts.length; i++) {
    for (int j = i + 1; j < parts.length; j++) {
      if (out[j * 2 + 1] < out[i * 2 + 1]) {
        int a = out[i * 2]; int b = out[i * 2 + 1];
        out[i * 2] = out[j * 2]; out[i * 2 + 1] = out[j * 2 + 1];
        out[j * 2] = a; out[j * 2 + 1] = b;
      }
    }
  }
  return out;
}""")
M(cfgc, r"""
public static String[] parseIds(String s) {
  if (s == null) return null;
  String t = s.trim();
  if (t.length() == 0 || t.equals("-")) return new String[0];
  String[] parts = t.split(",");
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    if (p.length() == 0) continue;
    for (int k = 0; k < p.length(); k++) {
      char ch = p.charAt(k);
      boolean ok = (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '_' || (ch == '*' && k == p.length() - 1);
      if (!ok) return null;
    }
    if (p.equals("*")) return null;
    out.add(p);
  }
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
M(cfgc, r"""
public static int[] levels() {
  String src = BYLEVEL;
  if (src != null && src.equals(LEVELS_SRC)) return LEVELS;
  int[] lv = parseLevels(src);
  if (lv == null) { @PKG@.WdLog.warnOnce("cfg:byLevel", "slots.byLevel=" + src + " is not slots:level pairs - no level slots until it is fixed"); lv = new int[0]; }
  LEVELS = lv;
  LEVELS_SRC = src;
  return lv;
}""")
M(cfgc, r"""
public static String[] keepList() {
  String src = KEEP_IDS;
  if (src != null && src.equals(KEEP_SRC)) return KEEP;
  String[] ks = parseIds(src);
  if (ks == null) { @PKG@.WdLog.warnOnce("cfg:keep", "swap.keepIds=" + src + " is not a list of item ids - the SkyWynn Menu item stays protected"); ks = new String[] { "Skyy_Menu" }; }
  KEEP = ks;
  KEEP_SRC = src;
  return ks;
}""")
_ap = ["public static void applyScalars(java.util.Properties p) {"]
for r in SCALARS:
    k, jt, fld, dv = r[0], r[12], r[11], r[4]
    if jt == "boolean":
        _ap.append('  %s = bv(p, %s, %s);' % (fld, jstr(k), dv))
    elif jt == "int":
        _ap.append('  %s = iv(p, %s, %d, %d, %d);' % (fld, jstr(k), int(dv), int(r[5]), int(r[6])))
    else:
        _ap.append('  %s = sv(p, %s, %s);' % (fld, jstr(k), jstr(dv)))
_ap += ['  levels();', '  keepList();', "}"]
M(cfgc, "\n".join(_ap))
M(cfgc, r"""
public static java.util.Properties props(String text) {
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { }
  return p;
}""")
M(cfgc, r"""
public static java.util.Properties read(java.nio.file.Path f) {
  if (f == null) return null;
  java.io.InputStream in = null;
  try {
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return null;
    in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    java.util.Properties p = new java.util.Properties();
    p.load(in);
    return p;
  } catch (Throwable t) {
    @PKG@.WdLog.warn("could not read " + f + ": " + t + " - using the built-in defaults");
    return null;
  } finally {
    try { if (in != null) in.close(); } catch (Throwable t2) { }
  }
}""")
M(cfgc, r"""
public static void seed(java.nio.file.Path f) {
  if (f == null) return;
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Path dir = f.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, DEFAULT_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    @PKG@.WdLog.info("wrote the default " + f.getFileName());
  } catch (Throwable t) { @PKG@.WdLog.warn("could not write the default " + f + ": " + t); }
}""")
M(cfgc, r"""
public static void reloadAll() {
  java.util.Properties p = read(FILE);
  applyScalars(p != null ? p : props(DEFAULT_TEXT));
  LOADS = LOADS + 1L;
}""")
M(cfgc, r"""
public static void load(java.nio.file.Path modsDir) {
  FILE = modsDir == null ? null : modsDir.resolve("Skyy_SkyyWardrobe").resolve("config.properties");
  seed(FILE);
  reloadAll();
}""")
# an item id that is never moved / stored (swap.keepIds; a trailing * = prefix)
M(cfgc, r"""
public static boolean keep(String id) {
  if (id == null) return false;
  String[] a = keepList();
  for (int i = 0; i < a.length; i++) {
    String k = a[i];
    if (k.endsWith("*")) { if (id.startsWith(k.substring(0, k.length() - 1))) return true; }
    else if (k.equals(id)) return true;
  }
  return false;
}""")
M(cfgc, r"""
public static String checkLevels(String key, String value) {
  if (value == null) return null;
  if (parseLevels(value) == null) return "Use slots:level pairs, e.g. 6:10,10:20 (slots 1-18), or - for none.";
  return null;
}""")
M(cfgc, r"""
public static String checkIds(String key, String value) {
  if (value == null) return null;
  if (parseIds(value) == null) return "Item ids separated by commas (letters, digits, _; a trailing * = prefix), or - for none.";
  return null;
}""")
M(cfgc, r"""
public static String summary() {
  return (ON ? "on" : "OFF") + ", " + FREE + " free slots (max " + MAX + ", by level " + BYLEVEL + "), hotbar " + (HOTBAR ? "on" : "off") + ", strict swap " + (STRICT ? "on" : "off") + ", kept " + KEEP_IDS + ", gap " + GAP_S + " s, combat " + COMBAT_S + " s, after a switch " + SETTLE_S + " s, journal " + JKEEP_S + " s";
}""")
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Wardrobe", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS, FILES=[CFG_FILE], NOTE=CFG_NOTE,
               RELOAD="WdCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": DEFAULT_TEXT})

# =====================================================================================================================
# WdCodec: the SkyyProfiles 0.1 lossless slot format (the SkyyVault 0.1.5 VCodec) + stack comparisons
# =====================================================================================================================
F(cod, "public static volatile java.util.Set UNKNOWN_IDS = null;")   # HARNESS SEAM ONLY (null in game): ids that count as gone
M(cod, r"""
public static int intOf(org.bson.BsonDocument d, String k, int def) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); } catch (Throwable t) { }
  return def;
}""")
M(cod, r"""
public static long lngOf(org.bson.BsonDocument d, String k, long def) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().longValue(); } catch (Throwable t) { }
  return def;
}""")
M(cod, r"""
public static double dblOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().doubleValue(); } catch (Throwable t) { }
  return 0.0;
}""")
M(cod, r"""
public static String strOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return null;
}""")
M(cod, r"""
public static org.bson.BsonDocument docOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isDocument()) return v.asDocument(); } catch (Throwable t) { }
  return null;
}""")
M(cod, r"""
public static boolean empty(@IS@ s) {
  return s == null || s.isEmpty();
}""")
M(cod, r"""
public static String desc(@IS@ s) {
  return empty(s) ? "-" : s.getItemId() + " x" + s.getQuantity();
}""")
# the same piece: id + quantity + metadata (durability and the rest may change by use; empty == empty)
M(cod, r"""
public static boolean same(@IS@ a, @IS@ b) {
  boolean ea = empty(a);
  boolean eb = empty(b);
  if (ea || eb) return ea && eb;
  if (!a.getItemId().equals(b.getItemId()) || a.getQuantity() != b.getQuantity()) return false;
  org.bson.BsonDocument ma = a.getMetadata();
  org.bson.BsonDocument mb = b.getMetadata();
  boolean xa = ma == null || ma.isEmpty();
  boolean xb = mb == null || mb.isEmpty();
  if (xa || xb) return xa && xb;
  return ma.equals(mb);
}""")
# the same KIND of stack (id + metadata, any quantity) - for counting a Clear's stacks in the live inventory
M(cod, r"""
public static boolean kind(@IS@ a, @IS@ b) {
  if (empty(a) || empty(b) || !a.getItemId().equals(b.getItemId())) return false;
  org.bson.BsonDocument ma = a.getMetadata();
  org.bson.BsonDocument mb = b.getMetadata();
  boolean xa = ma == null || ma.isEmpty();
  boolean xb = mb == null || mb.isEmpty();
  if (xa || xb) return xa && xb;
  return ma.equals(mb);
}""")
# the item still exists in the game (an item removed with its pack stays STORED, never put on a player)
M(cod, r"""
public static boolean known(String id) {
  if (id == null || id.length() == 0) return false;
  java.util.Set u = UNKNOWN_IDS;
  if (u != null) return !u.contains(id);
  try { return @ITEM@.getAssetMap().getAsset(id) != null; }
  catch (Throwable t) { @PKG@.WdLog.warnOnce("known", "the item asset map could not be read (" + t + ") - stored items are treated as existing"); return true; }
}""")
M(cod, r"""
public static org.bson.BsonDocument slotDoc(int slot, @IS@ s) {
  org.bson.BsonDocument d = new org.bson.BsonDocument();
  d.put("slot", new org.bson.BsonInt32(slot));
  d.put("id", new org.bson.BsonString(s.getItemId()));
  d.put("qty", new org.bson.BsonInt32(s.getQuantity()));
  d.put("durability", new org.bson.BsonDouble(s.getDurability()));
  d.put("maxDurability", new org.bson.BsonDouble(s.getMaxDurability()));
  d.put("quality", new org.bson.BsonInt32(s.getQualityIndex()));
  d.put("overrideAnim", new org.bson.BsonBoolean(s.getOverrideDroppedItemAnimation()));
  org.bson.BsonDocument m = s.getMetadata();
  if (m != null) d.put("meta", (org.bson.BsonDocument) m.clone());
  try {
    org.bson.BsonValue enc = ((@CODEC@) @IS@.CODEC).encode(s);
    if (enc != null) d.put("stack", enc);
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("enc-" + s.getItemId(), "ItemStack.CODEC could not encode " + s.getItemId() + " (explicit fields kept): " + t); }
  return d;
}""")
# engine codec first (exact engine persistence), explicit fields as the fallback; null = cannot be rebuilt (kept as an orphan)
M(cod, r"""
public static @IS@ stackOf(org.bson.BsonDocument d) {
  if (d == null) return null;
  String id = strOf(d, "id");
  int qty = intOf(d, "qty", 0);
  if (id == null || id.length() == 0 || qty <= 0) return null;
  try {
    org.bson.BsonValue enc = (org.bson.BsonValue) d.get("stack");
    if (enc != null && enc.isDocument()) {
      Object o = ((@CODEC@) @IS@.CODEC).decode(enc);
      if (o instanceof @IS@) {
        @IS@ s = (@IS@) o;
        if (!s.isEmpty() && id.equals(s.getItemId()) && s.getQuantity() == qty) return s;
      }
    }
  } catch (Throwable t) { }
  org.bson.BsonDocument meta = docOf(d, "meta");
  @IS@ s2 = null;
  try { s2 = new @IS@(id, qty, dblOf(d, "durability"), dblOf(d, "maxDurability"), intOf(d, "quality", 0), meta); }
  catch (Throwable t) { return null; }
  try {
    org.bson.BsonValue a = (org.bson.BsonValue) d.get("overrideAnim");
    if (a != null && a.isBoolean() && a.asBoolean().getValue()) s2.setOverrideDroppedItemAnimation(true);
  } catch (Throwable t) { }
  return s2;
}""")
M(cod, r"""
public static String toJson(org.bson.BsonDocument d) {
  org.bson.json.JsonWriterSettings s = org.bson.json.JsonWriterSettings.builder().outputMode(org.bson.json.JsonMode.EXTENDED).indent(true).build();
  return d.toJson(s);
}""")

# =====================================================================================================================
# WdLoad (one loadout) + WdData (one profile's wardrobe)
# =====================================================================================================================
for _f in ("public int n;", "public String name;", "public @IS@[] armor;", "public @IS@[] hot;", "public boolean hasPets;", "public String pet;",
           "public String summon;", "public String abil;"):
    F(lo, _f)
C(lo, r"""
public WdLoad(int n) {
  this.n = n; this.name = ""; this.armor = new @IS@[%d]; this.hot = new @IS@[%d];
  this.hasPets = false; this.pet = ""; this.summon = ""; this.abil = null;
}""" % (ARMOR_N, HOT_N))
M(lo, r"""
public @IS@[] arr(int part) {
  return part == 0 ? this.armor : this.hot;
}""")
M(lo, r"""
public int countPart(int part) {
  @IS@[] a = arr(part);
  int c = 0;
  for (int i = 0; i < a.length; i++) if (!@PKG@.WdCodec.empty(a[i])) c++;
  return c;
}""")
M(lo, r"""
public int count() {
  return countPart(0) + countPart(1);
}""")
M(lo, r"""
public boolean blank() {
  return count() == 0 && !this.hasPets && this.abil == null && this.name.length() == 0;
}""")
M(lo, r"""
public String title() {
  return this.name.length() > 0 ? this.name : "Loadout " + (this.n + 1);
}""")
M(lo, r"""
public void setFrom(@PKG@.WdLoad o) {
  this.name = o.name;
  for (int i = 0; i < this.armor.length && i < o.armor.length; i++) this.armor[i] = o.armor[i];
  for (int i = 0; i < this.hot.length && i < o.hot.length; i++) this.hot[i] = o.hot[i];
  this.hasPets = o.hasPets; this.pet = o.pet; this.summon = o.summon; this.abil = o.abil;
}""")
M(lo, r"""
public @PKG@.WdLoad copy() {
  @PKG@.WdLoad c = new @PKG@.WdLoad(this.n);
  c.setFrom(this);
  return c;
}""")
F(dat, "public static final int MAX = %d;" % MAX_SLOTS)
for _f in ("public String key;", "public String uuid;", "public long rev;", "public int floor;", "public int worn;", "public @PKG@.WdLoad[] slots;",
           "public org.bson.BsonArray orphans;", "public boolean bad;", "public String why;", "public long savedAt;", "public Object ioLock;"):
    F(dat, _f)
C(dat, r"""
public WdData(String key, String uuid) {
  this.key = key; this.uuid = uuid; this.rev = 0L; this.floor = 0; this.worn = -1; this.slots = new @PKG@.WdLoad[%d];
  for (int i = 0; i < this.slots.length; i++) this.slots[i] = new @PKG@.WdLoad(i);
  this.orphans = new org.bson.BsonArray(); this.bad = false; this.why = ""; this.savedAt = 0L; this.ioLock = new Object();
}""" % MAX_SLOTS)
M(dat, r"""
public int items() {
  int c = 0;
  for (int i = 0; i < this.slots.length; i++) c = c + this.slots[i].count();
  return c + this.orphans.size();
}""")
M(dat, r"""
public int highestUsed() {
  for (int i = this.slots.length - 1; i >= 0; i--) if (!this.slots[i].blank()) return i;
  return -1;
}""")
M(dat, r"""
public void orphan(String from, @IS@ s) {
  if (@PKG@.WdCodec.empty(s)) return;
  org.bson.BsonDocument d = @PKG@.WdCodec.slotDoc(-1, s);
  d.put("from", new org.bson.BsonString(from));
  this.orphans.add(d);
}""")
# a free spot for a displaced stack: the same part + slot of another loadout (blank loadouts first; never avoid / avoid2 / the equipped
# one); -1 = none free
M(dat, r"""
public int parkFree(int part, int slot, @IS@ s, int avoid, int avoid2) {
  if (@PKG@.WdCodec.empty(s) || part < 0 || part > 1 || slot < 0) return -1;
  for (int pass = 0; pass < 2; pass++) {
    for (int i = 0; i < this.slots.length; i++) {
      if (i == avoid || i == avoid2 || i == this.worn) continue;
      if (pass == 0 && !this.slots[i].blank()) continue;
      @IS@[] a = this.slots[i].arr(part);
      if (slot < a.length && @PKG@.WdCodec.empty(a[slot])) { a[slot] = s; return i; }
    }
  }
  return -1;
}""")
# a displaced stack (crash repair): a free spot elsewhere, else an orphan whose origin is retried at every load (never lost)
M(dat, r"""
public int park(int part, int slot, @IS@ s, int avoid, int avoid2, String why) {
  int i = parkFree(part, slot, s, avoid, avoid2);
  if (i < 0) orphan("loadout" + avoid + ":" + (part == 0 ? "armor" : "hotbar") + ":" + slot + ":" + why, s);
  return i;
}""")

# =====================================================================================================================
# WdStore: pkey, the per-profile files (load, save + read back), wardrobe.log, the start scan
# =====================================================================================================================
for _f in ("public static java.nio.file.Path ROOT;", "public static java.nio.file.Path DIR;", "public static java.nio.file.Path LOGF;",
           "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile long SAVES = 0L;", "public static volatile long SAVE_FAILS = 0L;",
           "public static volatile int FAIL_NEXT = 0;"):   # FAIL_NEXT: HARNESS SEAM ONLY (0 in game) - the next n saves fail
    F(sto, _f)
M(sto, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = @PKG@.WdLog.bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(sto, r"""
public static java.nio.file.Path fileOf(String k) {
  return DIR.resolve(k + ".json");
}""")
M(sto, r"""
public static void log(String line) {
  try {
    if (LOGF == null) return;
    java.nio.file.Files.createDirectories(LOGF.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(LOGF, (java.time.Instant.now().toString() + " " + @PKG@.WdLog.clean(line) + "\n").getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("logf", "could not append to wardrobe.log: " + t); }
}""")
# tmp file + fsync + atomic rename, 5 x 20 ms retries on a Windows FileSystemException (SkyyProfiles ProfCfg.atomicWrite)
M(sto, r"""
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
M(sto, r"""
public static org.bson.BsonArray slotsDoc(@IS@[] a) {
  org.bson.BsonArray arr = new org.bson.BsonArray();
  for (int i = 0; i < a.length; i++) if (!@PKG@.WdCodec.empty(a[i])) arr.add(@PKG@.WdCodec.slotDoc(i, a[i]));
  return arr;
}""")
M(sto, r"""
public static org.bson.BsonDocument docOf(@PKG@.WdData d) {
  org.bson.BsonDocument doc = new org.bson.BsonDocument();
  doc.put("format", new org.bson.BsonInt32(1));
  doc.put("mod", new org.bson.BsonString("SkyyWardrobe"));
  doc.put("version", new org.bson.BsonString("@VERSION@"));
  doc.put("uuid", new org.bson.BsonString(d.uuid == null ? "" : d.uuid));
  doc.put("key", new org.bson.BsonString(d.key));
  doc.put("savedAt", new org.bson.BsonInt64(System.currentTimeMillis()));
  doc.put("rev", new org.bson.BsonInt64(d.rev));
  doc.put("floor", new org.bson.BsonInt32(d.floor));
  doc.put("worn", new org.bson.BsonInt32(d.worn));
  org.bson.BsonArray ls = new org.bson.BsonArray();
  for (int i = 0; i < d.slots.length; i++) {
    @PKG@.WdLoad L = d.slots[i];
    if (L.blank()) continue;
    org.bson.BsonDocument x = new org.bson.BsonDocument();
    x.put("n", new org.bson.BsonInt32(i));
    x.put("name", new org.bson.BsonString(L.name));
    x.put("armor", slotsDoc(L.armor));
    x.put("hotbar", slotsDoc(L.hot));
    if (L.hasPets) {
      org.bson.BsonDocument p = new org.bson.BsonDocument();
      p.put("pet", new org.bson.BsonString(L.pet == null ? "" : L.pet));
      p.put("summon", new org.bson.BsonString(L.summon == null ? "" : L.summon));
      x.put("pets", p);
    }
    if (L.abil != null) x.put("abil", new org.bson.BsonString(L.abil));
    ls.add(x);
  }
  doc.put("loadouts", ls);
  doc.put("orphans", d.orphans.clone());
  return doc;
}""")
# the stacks a file document holds (loadout slots + orphans) - the read-back compare
M(sto, r"""
public static int countDoc(org.bson.BsonDocument doc) {
  if (doc == null) return -1;
  int c = 0;
  org.bson.BsonArray ls = doc.getArray("loadouts", new org.bson.BsonArray());
  for (int i = 0; i < ls.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) ls.get(i);
    if (v == null || !v.isDocument()) continue;
    c = c + v.asDocument().getArray("armor", new org.bson.BsonArray()).size() + v.asDocument().getArray("hotbar", new org.bson.BsonArray()).size();
  }
  return c + doc.getArray("orphans", new org.bson.BsonArray()).size();
}""")
M(sto, r"""
public static void fill(@PKG@.WdData d, @PKG@.WdLoad L, org.bson.BsonArray arr, int part, String from) {
  @IS@[] a = L.arr(part);
  for (int i = 0; i < arr.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) arr.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument sd = v.asDocument();
    int slot = @PKG@.WdCodec.intOf(sd, "slot", -1);
    @IS@ s = @PKG@.WdCodec.stackOf(sd);
    if (s == null) {
      org.bson.BsonDocument o = (org.bson.BsonDocument) sd.clone();
      o.put("from", new org.bson.BsonString(from + ":" + (part == 0 ? "armor" : "hotbar") + ":" + slot));
      d.orphans.add(o);
      @PKG@.WdLog.warnOnce("orphan:" + d.key, "a stored stack of " + d.key + " could not be rebuilt (" + @PKG@.WdCodec.strOf(sd, "id") + ") - kept as an orphan, retried at every load");
      continue;
    }
    if (slot < 0 || slot >= a.length || !@PKG@.WdCodec.empty(a[slot])) { d.orphan(from + ":" + (part == 0 ? "armor" : "hotbar") + ":" + slot, s); continue; }
    a[slot] = s;
  }
}""")
M(sto, r"""
public static @PKG@.WdData fromDoc(org.bson.BsonDocument doc, String k, String u) {
  @PKG@.WdData d = new @PKG@.WdData(k, u);
  int fmt = @PKG@.WdCodec.intOf(doc, "format", 0);
  if (fmt != 1) { d.bad = true; d.why = "Your wardrobe file has format " + fmt + " (this version reads 1) - nothing is changed until an admin updates the mod."; return d; }
  d.rev = @PKG@.WdCodec.lngOf(doc, "rev", 0L);
  d.floor = @PKG@.WdCodec.intOf(doc, "floor", 0);
  d.worn = @PKG@.WdCodec.intOf(doc, "worn", -1);
  if (d.worn < -1 || d.worn >= d.slots.length) d.worn = -1;
  d.savedAt = @PKG@.WdCodec.lngOf(doc, "savedAt", 0L);
  // orphans first (retried: a stack that can be rebuilt now goes back where it came from when that spot is free)
  org.bson.BsonArray old = doc.getArray("orphans", new org.bson.BsonArray());
  java.util.ArrayList retry = new java.util.ArrayList();
  for (int i = 0; i < old.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) old.get(i);
    if (v != null && v.isDocument()) retry.add(v.asDocument());
  }
  org.bson.BsonArray ls = doc.getArray("loadouts", new org.bson.BsonArray());
  for (int i = 0; i < ls.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) ls.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument x = v.asDocument();
    int n = @PKG@.WdCodec.intOf(x, "n", -1);
    String from = "loadout" + n;
    if (n < 0 || n >= d.slots.length) {
      @PKG@.WdLoad tmp = new @PKG@.WdLoad(0);
      fill(d, tmp, x.getArray("armor", new org.bson.BsonArray()), 0, from);
      fill(d, tmp, x.getArray("hotbar", new org.bson.BsonArray()), 1, from);
      for (int p = 0; p < 2; p++) for (int s = 0; s < tmp.arr(p).length; s++) d.orphan(from + ":" + p + ":" + s, tmp.arr(p)[s]);
      continue;
    }
    @PKG@.WdLoad L = d.slots[n];
    String nm = @PKG@.WdCodec.strOf(x, "name");
    L.name = nm == null ? "" : nm;
    fill(d, L, x.getArray("armor", new org.bson.BsonArray()), 0, from);
    fill(d, L, x.getArray("hotbar", new org.bson.BsonArray()), 1, from);
    org.bson.BsonDocument p = @PKG@.WdCodec.docOf(x, "pets");
    if (p != null) {
      L.hasPets = true;
      String pt = @PKG@.WdCodec.strOf(p, "pet");
      String sm = @PKG@.WdCodec.strOf(p, "summon");
      L.pet = pt == null ? "" : pt;
      L.summon = sm == null ? "" : sm;
    }
    L.abil = @PKG@.WdCodec.strOf(x, "abil");
  }
  for (int i = 0; i < retry.size(); i++) {
    org.bson.BsonDocument o = (org.bson.BsonDocument) retry.get(i);
    @IS@ s = @PKG@.WdCodec.stackOf(o);
    if (s == null) { d.orphans.add(o); continue; }
    String from = @PKG@.WdCodec.strOf(o, "from");
    boolean placed = false;
    if (from != null && from.startsWith("loadout")) {
      try {
        String[] a = from.substring(7).split(":");
        int n = Integer.parseInt(a[0]);
        int part = a[1].equals("armor") || a[1].equals("0") ? 0 : (a[1].equals("hotbar") || a[1].equals("1") ? 1 : -1);
        int slot = Integer.parseInt(a[2]);
        if (n >= 0 && n < d.slots.length && part >= 0 && slot >= 0 && slot < d.slots[n].arr(part).length && @PKG@.WdCodec.empty(d.slots[n].arr(part)[slot])) {
          d.slots[n].arr(part)[slot] = s;
          placed = true;
        } else if (part >= 0 && d.parkFree(part, slot, s, n, -1) >= 0) placed = true;   // its own spot is taken: a free spot elsewhere
      } catch (Throwable t) { placed = false; }
    }
    if (!placed) d.orphans.add(o);
  }
  return d;
}""")
# the file of one key; an unreadable file -> bad (cached: never written; /wardrobeadmin reload retries)
M(sto, r"""
public static @PKG@.WdData readFile(String k, String u) {
  java.nio.file.Path f = fileOf(k);
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return new @PKG@.WdData(k, u);
  try {
    org.bson.BsonDocument doc = org.bson.BsonDocument.parse(new String(java.nio.file.Files.readAllBytes(f), "UTF-8"));
    return fromDoc(doc, k, u);
  } catch (Throwable t) {
    @PKG@.WdData d = new @PKG@.WdData(k, u);
    d.bad = true;
    d.why = "Your wardrobe file could not be read - an admin has been told. Nothing is moved or written until it is fixed.";
    @PKG@.WdLog.warnOnce("unreadable:" + k, "wardrobe file " + f + " could not be read (" + t + ") - that wardrobe stays SHUT and is never written over; fix the file, then /wardrobeadmin reload");
    return d;
  }
}""")
# synchronous: the transaction must know the result (SkyyVault buy pattern). false = NOT saved (the file keeps its old content)
M(sto, r"""
public static boolean save(@PKG@.WdData d) {
  if (d == null || d.bad || DIR == null) return false;
  synchronized (d.ioLock) {
    try {
      if (FAIL_NEXT > 0) { FAIL_NEXT = FAIL_NEXT - 1; throw new java.io.IOException("harness: this save fails"); }
      org.bson.BsonDocument doc = docOf(d);
      int want = countDoc(doc);
      if (want != d.items()) throw new java.io.IOException("the document holds " + want + " stacks, memory " + d.items());
      java.nio.file.Path f = fileOf(d.key);
      atomicWrite(f, @PKG@.WdCodec.toJson(doc).getBytes("UTF-8"));
      org.bson.BsonDocument back = org.bson.BsonDocument.parse(new String(java.nio.file.Files.readAllBytes(f), "UTF-8"));
      if (countDoc(back) != want || @PKG@.WdCodec.lngOf(back, "rev", -1L) != d.rev) throw new java.io.IOException("read back " + countDoc(back) + " stacks rev " + @PKG@.WdCodec.lngOf(back, "rev", -1L) + ", wrote " + want + " rev " + d.rev);
      d.savedAt = System.currentTimeMillis();
      SAVES = SAVES + 1L;
      return true;
    } catch (Throwable t) {
      SAVE_FAILS = SAVE_FAILS + 1L;
      @PKG@.WdLog.warn("could not save wardrobe " + d.key + ": " + t);
      return false;
    }
  }
}""")
# the start scan: { files, unreadable, journals, stacks } - reads only, creates nothing
M(sto, r"""
public static int[] scanAll() {
  int[] r = new int[4];
  try {
    if (DIR == null || !java.nio.file.Files.isDirectory(DIR, new java.nio.file.LinkOption[0])) return r;
    java.io.File[] fs = DIR.toFile().listFiles();
    if (fs == null) return r;
    for (int i = 0; i < fs.length; i++) {
      String n = fs[i].getName();
      if (n.endsWith(".journal.json")) { r[2]++; continue; }
      if (!n.endsWith(".json")) continue;
      r[0]++;
      try {
        org.bson.BsonDocument doc = org.bson.BsonDocument.parse(new String(java.nio.file.Files.readAllBytes(fs[i].toPath()), "UTF-8"));
        r[3] = r[3] + countDoc(doc);
      } catch (Throwable t) { r[1]++; @PKG@.WdLog.warn("wardrobe file " + n + " could not be read: " + t + " - that wardrobe stays shut until it is fixed"); }
    }
  } catch (Throwable t) { @PKG@.WdLog.warn("the wardrobe scan failed: " + t); }
  return r;
}""")

# =====================================================================================================================
# WdJournal: the write-ahead journal (one per storage key) + its keep window
# =====================================================================================================================
F(jr, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")  # key -> Long at
M(jr, r"""
public static java.nio.file.Path fileOf(String k) {
  return @PKG@.WdStore.DIR.resolve(k + ".journal.json");
}""")
M(jr, r"""
public static synchronized boolean write(String k, org.bson.BsonDocument j) {
  try {
    @PKG@.WdStore.atomicWrite(fileOf(k), @PKG@.WdCodec.toJson(j).getBytes("UTF-8"));
    return true;
  } catch (Throwable t) { @PKG@.WdLog.warn("could not write the wardrobe journal of " + k + ": " + t); return false; }
}""")
M(jr, r"""
public static synchronized org.bson.BsonDocument read(String k) {
  try {
    if (@PKG@.WdStore.DIR == null) return null;
    java.nio.file.Path f = fileOf(k);
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    return org.bson.BsonDocument.parse(new String(java.nio.file.Files.readAllBytes(f), "UTF-8"));
  } catch (Throwable t) {
    @PKG@.WdLog.warnOnce("journal:" + k, "the wardrobe journal of " + k + " could not be read (" + t + ") - left in place for an admin");
    return null;
  }
}""")
M(jr, r"""
public static synchronized void delete(String k) {
  PENDING.remove(k);
  try { if (@PKG@.WdStore.DIR != null) java.nio.file.Files.deleteIfExists(fileOf(k)); } catch (Throwable t) { @PKG@.WdLog.warn("could not delete the wardrobe journal of " + k + ": " + t); }
}""")
M(jr, r"""
public static long epochOf(String uuid) {
  if (uuid == null || uuid.length() == 0) return -1L;
  try { Object e = @PKG@.WdLog.bridge().get("profile:epoch:" + uuid); if (e instanceof Number) return ((Number) e).longValue(); } catch (Throwable t) { }
  return -1L;
}""")
# the steps of a journal, oldest first (a journal without "steps" is one step)
M(jr, r"""
public static org.bson.BsonArray stepsOf(org.bson.BsonDocument j) {
  if (j == null) return new org.bson.BsonArray();
  org.bson.BsonValue v = (org.bson.BsonValue) j.get("steps");
  if (v != null && v.isArray()) return v.asArray();
  org.bson.BsonArray a = new org.bson.BsonArray();
  a.add(j);
  return a;
}""")
# a change starts: its step (+ "pre" = the wardrobe as it is now) JOINS a saved journal still inside its keep window, so a crash undoes the
# newest steps first (one journal per key, never overwritten); steps saved longer ago than the keep window are dropped (the engine has
# saved the player since). Stage "moving" is never in PENDING, so the timer never deletes it. null = not written (nothing may move)
M(jr, r"""
public static synchronized org.bson.BsonDocument begin(@PKG@.WdData d, org.bson.BsonDocument step, long now) {
  String k = d.key;
  Object prevAt = PENDING.get(k);
  org.bson.BsonArray steps = new org.bson.BsonArray();
  long keepMs = (long) @PKG@.WdCfg.JKEEP_S * 1000L;
  if (prevAt instanceof Long) {
    org.bson.BsonDocument prev = read(k);
    if (prev != null && "saved".equals(@PKG@.WdCodec.strOf(prev, "stage"))) {
      org.bson.BsonArray ps = stepsOf(prev);
      for (int i = 0; i < ps.size(); i++) {
        org.bson.BsonValue v = (org.bson.BsonValue) ps.get(i);
        if (v == null || !v.isDocument()) continue;
        long sa = @PKG@.WdCodec.lngOf(v.asDocument(), "savedAt", 0L);
        if (sa > 0L && now - sa >= keepMs) continue;
        steps.add(v);
      }
    }
  }
  int prevN = steps.size();
  step.put("pre", @PKG@.WdStore.docOf(d));
  steps.add(step);
  org.bson.BsonDocument j = new org.bson.BsonDocument();
  j.put("format", new org.bson.BsonInt32(2));
  j.put("key", new org.bson.BsonString(k));
  j.put("uuid", new org.bson.BsonString(d.uuid == null ? "" : d.uuid));
  j.put("epoch", new org.bson.BsonInt64(epochOf(d.uuid)));
  j.put("stage", new org.bson.BsonString("moving"));
  j.put("at", new org.bson.BsonInt64(now));
  j.put("prevSteps", new org.bson.BsonInt32(prevN));
  j.put("prevSavedAt", new org.bson.BsonInt64(prevAt instanceof Long ? ((Long) prevAt).longValue() : 0L));
  j.put("steps", steps);
  PENDING.remove(k);
  if (write(k, j)) return j;
  if (prevAt instanceof Long) PENDING.put(k, prevAt);
  return null;
}""")
# after the file was saved: stage "saved", kept journalKeepSeconds from the NEWEST step (a crash inside it = the next join repairs)
M(jr, r"""
public static synchronized void saved(String k, org.bson.BsonDocument j, long now) {
  j.put("stage", new org.bson.BsonString("saved"));
  j.put("savedAt", new org.bson.BsonInt64(now));
  org.bson.BsonArray st = stepsOf(j);
  if (st.size() > 0) { org.bson.BsonValue v = (org.bson.BsonValue) st.get(st.size() - 1); if (v != null && v.isDocument()) v.asDocument().put("savedAt", new org.bson.BsonInt64(now)); }
  if (write(k, j)) PENDING.put(k, Long.valueOf(now));
}""")
# the change was rolled back cleanly: the journal goes back to its earlier saved steps (or goes)
M(jr, r"""
public static synchronized void abort(String k, org.bson.BsonDocument j) {
  if (j == null) return;
  int prevN = @PKG@.WdCodec.intOf(j, "prevSteps", 0);
  long at = @PKG@.WdCodec.lngOf(j, "prevSavedAt", 0L);
  if (prevN <= 0) { delete(k); return; }
  org.bson.BsonArray all = stepsOf(j);
  org.bson.BsonArray keep = new org.bson.BsonArray();
  for (int i = 0; i < prevN && i < all.size(); i++) keep.add((org.bson.BsonValue) all.get(i));
  j.put("steps", keep);
  j.put("stage", new org.bson.BsonString("saved"));
  j.put("prevSteps", new org.bson.BsonInt32(0));
  if (write(k, j)) PENDING.put(k, Long.valueOf(at > 0L ? at : System.currentTimeMillis()));
}""")
# could not be undone: stage "failed" (the lock), never swept
M(jr, r"""
public static synchronized void failed(String k, org.bson.BsonDocument j, String why) {
  PENDING.remove(k);
  if (j == null) return;
  j.put("stage", new org.bson.BsonString("failed"));
  j.put("why", new org.bson.BsonString(why));
  write(k, j);
}""")
# the timer: a journal whose keep time is over goes - only while the FILE still says "saved" (a moving / failed / unreadable one stays)
M(jr, r"""
public static synchronized void sweep(long now) {
  java.util.Iterator it = new java.util.ArrayList(PENDING.keySet()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    Object at = PENDING.get(k);
    if (!(at instanceof Long) || now - ((Long) at).longValue() < (long) @PKG@.WdCfg.JKEEP_S * 1000L) continue;
    org.bson.BsonDocument j = read(k);
    if (j != null && "saved".equals(@PKG@.WdCodec.strOf(j, "stage"))) delete(k);
    else PENDING.remove(k);
  }
}""")
# graceful stop: the engine saves every online player, so the live inventory and the files agree - the journals go
M(jr, r"""
public static synchronized int dropAll() {
  int n = 0;
  java.util.Iterator it = new java.util.ArrayList(PENDING.keySet()).iterator();
  while (it.hasNext()) { delete((String) it.next()); n++; }
  return n;
}""")

M(sto, r"""
public static @PKG@.WdData get(String k, java.util.UUID u) {
  Object o = CACHE.get(k);
  if (o instanceof @PKG@.WdData) return (@PKG@.WdData) o;
  @PKG@.WdData d = readFile(k, u == null ? "" : u.toString());
  if (!d.bad) {
    org.bson.BsonDocument j = @PKG@.WdJournal.read(k);
    if (j != null && "failed".equals(@PKG@.WdCodec.strOf(j, "stage"))) {
      d.bad = true;
      d.why = "A loadout change failed and could not be undone - your wardrobe is locked until an admin runs /wardrobeadmin repair. Nothing is lost.";
    }
  }
  Object prev = CACHE.putIfAbsent(k, d);
  return prev instanceof @PKG@.WdData ? (@PKG@.WdData) prev : d;
}""")
# =====================================================================================================================
# WdSlots: how many loadout slots a profile has (free + Overall Level + admin floor, at most slots.max)
# =====================================================================================================================
M(slt, r"""
public static int overall(java.util.UUID u) {
  try {
    java.util.function.Function f = @PKG@.WdLog.fn("skill:fn:overall");
    if (f != null) {
      Object r = f.apply(u);
      if (r instanceof Object[] && ((Object[]) r).length > 0 && ((Object[]) r)[0] instanceof Number) return ((Number) ((Object[]) r)[0]).intValue();
      if (r instanceof Number) return ((Number) r).intValue();
    }
    Object v = @PKG@.WdLog.bridge().get("skill:overall:" + u.toString());
    if (v instanceof Number) return ((Number) v).intValue();
  } catch (Throwable t) { }
  return -1;
}""")
M(slt, r"""
public static int byLevel(int level) {
  int[] a = @PKG@.WdCfg.levels();
  int best = 0;
  for (int i = 0; i + 1 < a.length; i += 2) if (level >= a[i + 1] && a[i] > best) best = a[i];
  return best;
}""")
M(slt, r"""
public static int unlocked(java.util.UUID u, @PKG@.WdData d) {
  int lv = u == null ? -1 : overall(u);
  int n = @PKG@.WdCfg.FREE;
  int b = byLevel(lv);
  if (b > n) n = b;
  if (d != null && d.floor > n) n = d.floor;
  int mx = @PKG@.WdCfg.MAX;
  if (n > mx) n = mx;
  if (n > @PKG@.WdData.MAX) n = @PKG@.WdData.MAX;
  if (n < 1) n = 1;
  return n;
}""")
# the Overall Level that opens slot index i (0-based), -1 = no level rule opens it
M(slt, r"""
public static int levelFor(int i) {
  int[] a = @PKG@.WdCfg.levels();
  int best = -1;
  for (int k = 0; k + 1 < a.length; k += 2) if (a[k] >= i + 1 && (best < 0 || a[k + 1] < best)) best = a[k + 1];
  return best;
}""")
M(slt, r"""
public static String lockText(int i) {
  if (i >= @PKG@.WdCfg.MAX) return "locked by the server (Most loadout slots)";
  int lv = levelFor(i);
  return lv < 0 ? "locked - an admin can open it" : "unlocks at Overall Level " + lv;
}""")
# cards on the page: every unlocked slot, every slot that still holds something, and the next locked one (so the player sees the goal)
M(slt, r"""
public static int shown(@PKG@.WdData d, int unl) {
  int n = unl;
  int h = d == null ? -1 : d.highestUsed();
  if (d != null && d.worn + 1 > n) n = d.worn + 1;
  if (h + 1 > n) n = h + 1;
  if (n < @PKG@.WdData.MAX && n < @PKG@.WdCfg.MAX + 1) n = n + 1;
  if (n > @PKG@.WdData.MAX) n = @PKG@.WdData.MAX;
  return n;
}""")

# =====================================================================================================================
# WdBridge: SkyyPets (pets:fn:loadoutGet / loadoutSet / petName) + SkyyClasses (class:fn:loadoutGet / loadoutSet)
# =====================================================================================================================
F(brg, 'public static final String PETS_NEED = "Pets in loadouts need SkyyPets 0.2.3";')
F(brg, 'public static final String ABIL_NEED = "Abilities in loadouts need SkyyClasses 0.1.19";')
M(brg, "public static boolean petsHas() { return @PKG@.WdLog.fn(\"pets:fn:loadoutGet\") != null && @PKG@.WdLog.fn(\"pets:fn:loadoutSet\") != null; }")
M(brg, "public static boolean abilHas() { return @PKG@.WdLog.fn(\"class:fn:loadoutGet\") != null && @PKG@.WdLog.fn(\"class:fn:loadoutSet\") != null; }")
# { pet id, summon id } ("" = that slot is empty); null = SkyyPets cannot answer (missing key, null, an error)
M(brg, r"""
public static String[] petsGet(java.util.UUID u) {
  java.util.function.Function f = @PKG@.WdLog.fn("pets:fn:loadoutGet");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(u);
    if (!(r instanceof String)) return null;
    String s = (String) r;
    int bar = s.indexOf('|');
    if (bar < 0) return new String[] { s.trim(), "" };
    return new String[] { s.substring(0, bar).trim(), s.substring(bar + 1).trim() };
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("petsget", "pets:fn:loadoutGet failed: " + t); return null; }
}""")
# the pets result ("+..." / "=..." / "-..."); null = the key is missing
M(brg, r"""
public static String petsSet(java.util.UUID u, String pet, String summon) {
  java.util.function.Function f = @PKG@.WdLog.fn("pets:fn:loadoutSet");
  if (f == null) return null;
  try {
    Object r = f.apply(new Object[] { u, pet == null ? "" : pet, summon == null ? "" : summon });
    if (r instanceof String && ((String) r).length() > 0) return (String) r;
    return "-SkyyPets gave no answer - your pets were not changed.";
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("petsset", "pets:fn:loadoutSet failed: " + t); return "-SkyyPets failed - your pets were not changed (see the server log)."; }
}""")
M(brg, r"""
public static String petName(java.util.UUID u, String id) {
  if (id == null || id.length() == 0) return "none";
  java.util.function.Function f = @PKG@.WdLog.fn("pets:fn:petName");
  if (f != null) {
    try {
      Object r = f.apply(new Object[] { u, id });
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
      return id + " (gone)";
    } catch (Throwable t) { }
  }
  return id;
}""")
M(brg, r"""
public static String abilGet(java.util.UUID u) {
  java.util.function.Function f = @PKG@.WdLog.fn("class:fn:loadoutGet");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(u);
    return r instanceof String && ((String) r).length() > 0 ? (String) r : null;
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("abilget", "class:fn:loadoutGet failed: " + t); return null; }
}""")
M(brg, r"""
public static String abilSet(java.util.UUID u, String snap) {
  java.util.function.Function f = @PKG@.WdLog.fn("class:fn:loadoutSet");
  if (f == null) return null;
  try {
    Object r = f.apply(new Object[] { u, snap });
    if (r instanceof String && ((String) r).length() > 0) return (String) r;
    return "-SkyyClasses gave no answer - your abilities were not changed.";
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("abilset", "class:fn:loadoutSet failed: " + t); return "-SkyyClasses failed - your abilities were not changed (see the server log)."; }
}""")
M(brg, r"""
public static String val(String snap, String key) {
  if (snap == null || key == null) return null;
  String[] parts = snap.split(";");
  for (int i = 0; i < parts.length; i++) {
    int e = parts[i].indexOf('=');
    if (e > 0 && parts[i].substring(0, e).trim().equals(key)) return parts[i].substring(e + 1).trim();
  }
  return null;
}""")
M(brg, r"""
public static String nm(String snap, String n, String id) {
  String v = val(snap, n);
  if (v != null && v.length() > 0) return v;
  v = val(snap, id);
  return v == null || v.length() == 0 ? "-" : v;
}""")
M(brg, r"""
public static String abilText(String snap) {
  if (snap == null) return "Abilities: not saved in this loadout";
  String c = val(snap, "class");
  return "Abilities" + (c == null ? "" : " (" + c + ")") + ": " + nm(snap, "n1", "p1") + ", " + nm(snap, "n2", "p2") + " - alts " + nm(snap, "n3", "a1") + ", " + nm(snap, "n4", "a2");
}""")
M(brg, r"""
public static String petsText(java.util.UUID u, @PKG@.WdLoad L) {
  if (!L.hasPets) return "Pets: not saved in this loadout";
  return "Pet: " + petName(u, L.pet) + "    Summon: " + petName(u, L.summon);
}""")

# =====================================================================================================================
# WdTx: THE TRANSACTIONS on the live containers (world thread; harness-executed with real engine containers)
# =====================================================================================================================
F(tx, "public static volatile int CRASH_AT = -1;")              # HARNESS SEAM ONLY (-1 in game): "the JVM dies" after this many moves
F(tx, "public static volatile boolean CRASH_AFTER_SAVE = false;")   # HARNESS SEAM ONLY: "the JVM dies" after the file was saved
F(tx, "public static volatile long EQUIPS = 0L;")
F(tx, "public static volatile long ROLLBACKS = 0L;")
F(tx, "public static volatile long REPAIRS = 0L;")
F(tx, 'public static final String LOCKED_MSG = "-The change failed and could not be undone - your wardrobe is locked until an admin runs /wardrobeadmin repair. Nothing is lost: the journal lists every piece.";')
# take the whole stack off slot s (no slot filter: the piece goes back only where it came from); true = the slot is empty now
M(tx, r"""
public static boolean takeOff(@IC@ c, short s) {
  try {
    @STX@ t = c.removeItemStackFromSlot(s, false);
    if (t == null || !t.succeeded()) return @PKG@.WdCodec.empty(c.getItemStack(s));
  } catch (Throwable e) { @PKG@.WdLog.warnOnce("takeoff", "could not take a stack off a slot: " + e); }
  return @PKG@.WdCodec.empty(c.getItemStack(s));
}""")
# make slot s hold exactly `want` (null = empty) and read it back
M(tx, r"""
public static boolean put(@IC@ c, short s, @IS@ want) {
  try {
    @IS@ cur = c.getItemStack(s);
    if (@PKG@.WdCodec.empty(want)) return @PKG@.WdCodec.empty(cur) || takeOff(c, s);
    if (cur == want) return true;
    if (!@PKG@.WdCodec.empty(cur) && !takeOff(c, s)) return false;
    c.setItemStackForSlot(s, want, false);
  } catch (Throwable e) { @PKG@.WdLog.warnOnce("put", "could not set a slot: " + e); }
  return @PKG@.WdCodec.same(c.getItemStack(s), want);
}""")
# undo the done moves in reverse: the spot holds its old live piece again; true = every spot verified
M(tx, r"""
public static boolean rollback(java.util.ArrayList done, @IC@ arm, @IC@ hot) {
  boolean ok = true;
  for (int i = done.size() - 1; i >= 0; i--) {
    Object[] m = (Object[]) done.get(i);
    int part = ((Integer) m[0]).intValue();
    short s = (short) ((Integer) m[1]).intValue();
    @IC@ c = part == 0 ? arm : hot;
    if (c == null || !put(c, s, (@IS@) m[4])) ok = false;
  }
  ROLLBACKS = ROLLBACKS + 1L;
  return ok;
}""")
M(tx, r"""
public static org.bson.BsonDocument moveDoc(int part, int slot, int dest, @IS@ on, @IS@ off) {
  org.bson.BsonDocument m = new org.bson.BsonDocument();
  m.put("part", new org.bson.BsonInt32(part));
  m.put("slot", new org.bson.BsonInt32(slot));
  m.put("dest", new org.bson.BsonInt32(dest));
  if (!@PKG@.WdCodec.empty(on)) m.put("on", @PKG@.WdCodec.slotDoc(slot, on));
  if (!@PKG@.WdCodec.empty(off)) m.put("off", @PKG@.WdCodec.slotDoc(slot, off));
  return m;
}""")
M(tx, r"""
public static void lock(@PKG@.WdData d, org.bson.BsonDocument j, String why) {
  d.bad = true;
  d.why = @PKG@.WdLog.body(LOCKED_MSG);
  @PKG@.WdJournal.failed(d.key, j, why);
  @PKG@.WdStore.log("LOCKED " + d.key + " " + why);
  @PKG@.WdLog.warn("wardrobe " + d.key + " locked: " + why + " - /wardrobeadmin repair <player> once the player is online");
}""")
M(tx, r"""
public static String join(java.util.ArrayList notes) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < notes.size(); i++) { if (i > 0) sb.append("; "); sb.append(String.valueOf(notes.get(i))); }
  return sb.toString();
}""")
# how many of this stack's KIND (id + metadata) the live inventory holds (Clear's journal, Equip's kind counts)
M(tx, r"""
public static int countKind(@IC@[] cs, @IS@ k) {
  int c = 0;
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    int cap = cs[i].getCapacity();
    for (int s = 0; s < cap; s++) {
      @IS@ x = cs[i].getItemStack((short) s);
      if (@PKG@.WdCodec.kind(x, k)) c = c + x.getQuantity();
    }
  }
  return c;
}""")
M(tx, r"""
public static boolean findAny(@IC@[] cs, @IS@ k) {
  if (@PKG@.WdCodec.empty(k)) return false;
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    int cap = cs[i].getCapacity();
    for (int s = 0; s < cap; s++) if (@PKG@.WdCodec.same(cs[i].getItemStack((short) s), k)) return true;
  }
  return false;
}""")
# how many pieces of an equip step (pieces going on [3] and coming off [4]) are of k's kind - the kind counts are only used for a kind
# that appears ONCE in the step (else the counts of two pieces mix and the exact match decides, as before)
M(tx, r"""
public static int kindsIn(java.util.ArrayList mv, @IS@ k) {
  int c = 0;
  for (int i = 0; i < mv.size(); i++) {
    Object[] m = (Object[]) mv.get(i);
    if (m[3] != null && @PKG@.WdCodec.kind((@IS@) m[3], k)) c++;
    if (m[4] != null && @PKG@.WdCodec.kind((@IS@) m[4], k)) c++;
  }
  return c;
}""")
# the swapped-in piece slot holds a piece of the same KIND (eaten from, used, more picked up) while the piece taken off is another kind:
# the move reached the inventory
M(tx, r"""
public static boolean onLike(@IS@ live, @IS@ on, @IS@ off) {
  if (@PKG@.WdCodec.empty(on) || @PKG@.WdCodec.empty(live)) return false;
  if (@PKG@.WdCodec.same(live, on)) return true;
  return @PKG@.WdCodec.kind(live, on) && !@PKG@.WdCodec.kind(on, off);
}""")
# an UNCLEAR move (neither piece in its spot): is the piece that went ON somewhere in the live inventory? With its kind count from before
# the swap ("onB"): more of that kind than before = (some of) it is here - eaten from, moved, stacked. Else the exact match.
M(tx, r"""
public static boolean onHere(@IC@[] all, @IS@ on, org.bson.BsonDocument m) {
  if (@PKG@.WdCodec.empty(on)) return false;
  int b = @PKG@.WdCodec.intOf(m, "onB", -1);
  if (b < 0) return findAny(all, on);
  return countKind(all, on) > b;
}""")
# ... and the piece that came OFF (it left the inventory at the swap): more than "offB" minus its own quantity = it is still here
M(tx, r"""
public static boolean offHere(@IC@[] all, @IS@ off, org.bson.BsonDocument m) {
  if (@PKG@.WdCodec.empty(off)) return false;
  int b = @PKG@.WdCodec.intOf(m, "offB", -1);
  if (b < 0) return findAny(all, off);
  return countKind(all, off) > b - off.getQuantity();
}""")
# did this move reach the live inventory? The piece that went on sits in its spot (same kind, used or not) - or the spot was EMPTY before
# and is empty again while more of the piece's kind is in the inventory than before the swap (eaten from / moved away); a move that only
# took a piece off: the spot is empty
M(tx, r"""
public static boolean moved(@IS@ live, @IS@ on, @IS@ off, @IC@[] all, org.bson.BsonDocument m) {
  if (on == null) return @PKG@.WdCodec.empty(live) && off != null;
  if (onLike(live, on, off)) return true;
  return off == null && @PKG@.WdCodec.empty(live) && @PKG@.WdCodec.intOf(m, "onB", -1) >= 0 && onHere(all, on, m);
}""")
# EQUIP loadout n (the items part). Spec 5.2 + the build docstring. notes = what stayed where it was (shown to the player)
M(tx, r"""
public static String equip(@PKG@.WdData d, int n, @IC@ arm, @IC@ hot, @IC@ sto, @IC@ bak, java.util.ArrayList notes) {
  if (d == null) return "-No wardrobe.";
  if (d.bad) return "-" + d.why;
  if (n < 0 || n >= d.slots.length) return "-There is no loadout " + (n + 1) + ".";
  @PKG@.WdLoad L = d.slots[n];
  int w = d.worn;
  @PKG@.WdLoad W = w >= 0 && w < d.slots.length && w != n ? d.slots[w] : null;
  java.util.ArrayList mv = new java.util.ArrayList();
  // swap.strict off (the LOCKED default, gear.md 2026-10-08 "partial sets keep the worn piece"): a spot this loadout leaves empty keeps
  // the worn piece ON. An EMPTY loadout (no items at all) is the put-away: what you wear goes home to the equipped loadout (as strict)
  boolean strict = @PKG@.WdCfg.STRICT || L.count() == 0;
  for (int part = 0; part < 2; part++) {
    @IS@[] src = L.arr(part);
    if (part == 1 && !@PKG@.WdCfg.HOTBAR) { if (L.countPart(1) > 0) notes.add("hotbar loadouts are switched off on this server - its stored hotbar items stay stored"); continue; }
    @IC@ c = part == 0 ? arm : hot;
    if (c == null) { if (L.countPart(part) > 0) notes.add("your " + (part == 0 ? "armor" : "hotbar") + " could not be read - that part stays stored"); continue; }
    int cap = c.getCapacity();
    for (int s = 0; s < src.length; s++) {
      @IS@ S = src[s];
      if (@PKG@.WdCodec.empty(S)) S = null;
      if (S != null && !@PKG@.WdCodec.known(S.getItemId())) { notes.add("a stored " + S.getItemId() + " no longer exists in the game - it stays stored"); S = null; }
      if (s >= cap) { if (S != null) notes.add("slot " + (s + 1) + " is missing - its stored item stays stored"); continue; }
      @IS@ live = c.getItemStack((short) s);
      if (@PKG@.WdCodec.empty(live)) live = null;
      if (part == 1 && live != null && @PKG@.WdCfg.keep(live.getItemId())) { if (S != null) notes.add("hotbar slot " + (s + 1) + " keeps your " + live.getItemId() + " - the item stored there stays stored"); continue; }
      if (S == null && !strict) continue;
      int dest = n;
      if (live != null && W != null && @PKG@.WdCodec.empty(W.arr(part)[s])) dest = w;
      if (S == null && (live == null || dest == n)) continue;
      mv.add(new Object[] { Integer.valueOf(part), Integer.valueOf(s), Integer.valueOf(dest), S, live });
    }
  }
  long now = System.currentTimeMillis();
  @PKG@.WdLoad nOld = L.copy();
  @PKG@.WdLoad wOld = W == null ? null : W.copy();
  int wornOld = d.worn;
  long revOld = d.rev;
  org.bson.BsonDocument j = null;
  if (mv.size() > 0) {
    org.bson.BsonDocument st = new org.bson.BsonDocument();
    st.put("op", new org.bson.BsonString("equip"));
    st.put("n", new org.bson.BsonInt32(n));
    st.put("from", new org.bson.BsonInt32(w));
    st.put("rev", new org.bson.BsonInt64(d.rev));
    st.put("at", new org.bson.BsonInt64(now));
    org.bson.BsonArray ms = new org.bson.BsonArray();
    @IC@[] allL = new @IC@[] { arm, hot, sto, bak };
    for (int i = 0; i < mv.size(); i++) {
      Object[] m = (Object[]) mv.get(i);
      org.bson.BsonDocument md = moveDoc(((Integer) m[0]).intValue(), ((Integer) m[1]).intValue(), ((Integer) m[2]).intValue(), (@IS@) m[3], (@IS@) m[4]);
      // the live count of each piece's kind before the swap (a kind that appears once in this step): the crash repair's evidence for a
      // piece eaten from / used / moved inside the keep window
      if (m[3] != null && kindsIn(mv, (@IS@) m[3]) == 1) md.put("onB", new org.bson.BsonInt32(countKind(allL, (@IS@) m[3])));
      if (m[4] != null && kindsIn(mv, (@IS@) m[4]) == 1) md.put("offB", new org.bson.BsonInt32(countKind(allL, (@IS@) m[4])));
      ms.add(md);
    }
    st.put("moves", ms);
    j = @PKG@.WdJournal.begin(d, st, now);
    if (j == null) return "-Could not write the swap journal - nothing was moved (see the server log).";
  }
  java.util.ArrayList done = new java.util.ArrayList();
  String fail = null;
  boolean broken = false;   // a failed move whose OWN spot could not be restored (the piece is only in the journal now): never "put back"
  for (int i = 0; i < mv.size() && fail == null; i++) {
    if (CRASH_AT == i) throw new IllegalStateException("harness crash after " + i + " moves");
    Object[] m = (Object[]) mv.get(i);
    int part = ((Integer) m[0]).intValue();
    short s = (short) ((Integer) m[1]).intValue();
    @IC@ c = part == 0 ? arm : hot;
    @IS@ S = (@IS@) m[3];
    @IS@ live = (@IS@) m[4];
    if (!@PKG@.WdCodec.same(c.getItemStack(s), live)) { fail = "a slot changed during the swap"; continue; }
    if (live != null && !takeOff(c, s)) { if (!put(c, s, live)) broken = true; fail = "could not take off " + live.getItemId(); continue; }
    if (S != null && !put(c, s, S)) { if (!put(c, s, live)) broken = true; fail = "could not put on " + S.getItemId(); continue; }
    done.add(m);
  }
  if (fail == null && CRASH_AT >= 0 && CRASH_AT >= mv.size()) throw new IllegalStateException("harness crash after every move");
  if (fail != null) {
    boolean back = rollback(done, arm, hot);
    if (back && !broken) { @PKG@.WdJournal.abort(d.key, j); return "-Equip stopped (" + fail + ") - everything was put back."; }
    lock(d, j, "equip " + (n + 1) + ": " + fail + (broken ? ", and that slot could not be restored" : "") + (back ? "" : ", and the rollback failed"));
    return LOCKED_MSG;
  }
  for (int i = 0; i < done.size(); i++) {
    Object[] m = (Object[]) done.get(i);
    int part = ((Integer) m[0]).intValue();
    int s = ((Integer) m[1]).intValue();
    int dest = ((Integer) m[2]).intValue();
    if (m[3] != null) L.arr(part)[s] = null;   // a spot whose stored piece was skipped (a gone item) keeps it
    if (m[4] != null || dest == n) d.slots[dest].arr(part)[s] = (@IS@) m[4];
  }
  d.worn = n;
  d.rev = d.rev + 1L;
  if (!@PKG@.WdStore.save(d)) {
    L.setFrom(nOld);
    if (W != null) W.setFrom(wOld);
    d.worn = wornOld;
    d.rev = revOld;
    if (rollback(done, arm, hot)) { @PKG@.WdJournal.abort(d.key, j); return "-Could not save your wardrobe - everything was put back (see the server log)."; }
    lock(d, j, "equip " + (n + 1) + ": the save failed, and the rollback failed");
    return LOCKED_MSG;
  }
  if (CRASH_AFTER_SAVE) throw new IllegalStateException("harness crash after the save");
  if (j != null) @PKG@.WdJournal.saved(d.key, j, now);
  EQUIPS = EQUIPS + 1L;
  StringBuilder lg = new StringBuilder();
  for (int i = 0; i < done.size(); i++) {
    Object[] m = (Object[]) done.get(i);
    lg.append(' ').append(((Integer) m[0]).intValue() == 0 ? "A" : "H").append(m[1]).append(':').append(@PKG@.WdCodec.desc((@IS@) m[3])).append("<-").append(@PKG@.WdCodec.desc((@IS@) m[4])).append("@").append(((Integer) m[2]).intValue() + 1);
  }
  @PKG@.WdStore.log("EQUIP " + d.uuid + " " + d.key + " loadout=" + (n + 1) + " from=" + (wornOld + 1) + " rev=" + d.rev + lg.toString());
  return "+Equipped " + L.title() + " (" + done.size() + " " + (done.size() == 1 ? "piece" : "pieces") + " moved).";
}""")
# SAVE CURRENT (the items part): n becomes the equipped loadout - nothing moves. null = fine
M(tx, r"""
public static String link(@PKG@.WdData d, int n) {
  if (d.bad) return "-" + d.why;
  @PKG@.WdLoad L = d.slots[n];
  int w = d.worn;
  if (w == n) return null;
  if (w >= 0 && w < d.slots.length) return "-You are wearing " + d.slots[w].title() + ". Press Save current on it to update it - or Equip " + L.title() + " first (your gear goes back to " + d.slots[w].title() + "), put on the new gear, then Save current.";
  if (L.count() > 0) return "-" + L.title() + " still stores gear - Equip it, or Clear it first.";
  d.worn = n;
  return null;
}""")
# CLEAR loadout n: its stored stacks go to the inventory (storage, hotbar, backpack - a stack only where it fits WHOLE), refs + name go
M(tx, r"""
public static String clear(@PKG@.WdData d, int n, @IC@ arm, @IC@ hot, @IC@ sto, @IC@ bak, java.util.ArrayList notes) {
  if (d.bad) return "-" + d.why;
  @PKG@.WdLoad L = d.slots[n];
  @IC@[] all = new @IC@[] { sto, hot, bak, arm };
  @IC@[] dst = new @IC@[] { sto, hot, bak };
  java.util.ArrayList mv = new java.util.ArrayList();
  for (int part = 0; part < 2; part++) {
    @IS@[] a = L.arr(part);
    for (int s = 0; s < a.length; s++) {
      if (@PKG@.WdCodec.empty(a[s])) continue;
      @IC@ to = null;
      for (int k = 0; k < dst.length && to == null; k++) {
        try { if (dst[k] != null && dst[k].canAddItemStack(a[s])) to = dst[k]; } catch (Throwable t) { }
      }
      if (to == null) { notes.add("no room for " + @PKG@.WdCodec.desc(a[s]) + " - it stays stored"); continue; }
      int before = countKind(all, a[s]);
      for (int q = 0; q < mv.size(); q++) {
        @IS@ e = (@IS@) ((Object[]) mv.get(q))[2];
        if (@PKG@.WdCodec.kind(e, a[s])) before = before + e.getQuantity();
      }
      mv.add(new Object[] { Integer.valueOf(part), Integer.valueOf(s), a[s], to, Integer.valueOf(before) });
    }
  }
  long now = System.currentTimeMillis();
  org.bson.BsonDocument j = null;
  @PKG@.WdLoad old = L.copy();
  int wornOld = d.worn;
  long revOld = d.rev;
  if (mv.size() > 0) {
    org.bson.BsonDocument st = new org.bson.BsonDocument();
    st.put("op", new org.bson.BsonString("clear"));
    st.put("n", new org.bson.BsonInt32(n));
    st.put("rev", new org.bson.BsonInt64(d.rev));
    st.put("at", new org.bson.BsonInt64(now));
    org.bson.BsonArray it = new org.bson.BsonArray();
    for (int i = 0; i < mv.size(); i++) {
      Object[] m = (Object[]) mv.get(i);
      org.bson.BsonDocument x = new org.bson.BsonDocument();
      x.put("part", new org.bson.BsonInt32(((Integer) m[0]).intValue()));
      x.put("slot", new org.bson.BsonInt32(((Integer) m[1]).intValue()));
      x.put("before", new org.bson.BsonInt32(((Integer) m[4]).intValue()));
      x.put("item", @PKG@.WdCodec.slotDoc(((Integer) m[1]).intValue(), (@IS@) m[2]));
      it.add(x);
    }
    st.put("items", it);
    j = @PKG@.WdJournal.begin(d, st, now);
    if (j == null) return "-Could not write the journal - nothing was moved (see the server log).";
  }
  java.util.ArrayList done = new java.util.ArrayList();
  for (int i = 0; i < mv.size(); i++) {
    if (CRASH_AT == i) throw new IllegalStateException("harness crash after " + i + " moves");
    Object[] m = (Object[]) mv.get(i);
    @IS@ S = (@IS@) m[2];
    @IC@ to = (@IC@) m[3];
    int before = countKind(all, S);
    @IS@ rest = null;
    try {
      @ISX@ t = to.addItemStack(S);
      rest = t == null ? S : t.getRemainder();
    } catch (Throwable e) { rest = S; }
    int got = countKind(all, S) - before;
    if (@PKG@.WdCodec.empty(rest) && got == S.getQuantity()) { done.add(m); continue; }
    // only part of it (or nothing) arrived: take back what arrived, keep the stack stored
    if (got > 0) { try { to.removeItemStack(S.withQuantity(got)); } catch (Throwable e) { } }
    if (countKind(all, S) != before) { notes.add("could not move " + @PKG@.WdCodec.desc(S) + " cleanly"); lock(d, j, "clear " + (n + 1) + ": a stack only half arrived and could not be taken back"); return LOCKED_MSG; }
    notes.add("no room for " + @PKG@.WdCodec.desc(S) + " - it stays stored");
  }
  if (CRASH_AT >= 0 && CRASH_AT >= mv.size()) throw new IllegalStateException("harness crash after every move");
  for (int i = 0; i < done.size(); i++) {
    Object[] m = (Object[]) done.get(i);
    L.arr(((Integer) m[0]).intValue())[((Integer) m[1]).intValue()] = null;
  }
  boolean emptied = L.count() == 0;
  L.hasPets = false; L.pet = ""; L.summon = ""; L.abil = null;
  if (emptied) L.name = "";
  if (d.worn == n) d.worn = -1;
  d.rev = d.rev + 1L;
  if (!@PKG@.WdStore.save(d)) {
    L.setFrom(old);
    d.worn = wornOld;
    d.rev = revOld;
    boolean back = true;
    for (int i = done.size() - 1; i >= 0; i--) {
      Object[] m = (Object[]) done.get(i);
      @IS@ S = (@IS@) m[2];
      int before = countKind(all, S);
      try { ((@IC@) m[3]).removeItemStack(S); } catch (Throwable e) { }
      if (countKind(all, S) != before - S.getQuantity()) back = false;
    }
    if (back) { @PKG@.WdJournal.abort(d.key, j); return "-Could not save your wardrobe - nothing was moved (see the server log)."; }
    lock(d, j, "clear " + (n + 1) + ": the save failed, and the items could not be taken back");
    return LOCKED_MSG;
  }
  if (CRASH_AFTER_SAVE) throw new IllegalStateException("harness crash after the save");
  if (j != null) @PKG@.WdJournal.saved(d.key, j, now);
  StringBuilder lg = new StringBuilder();
  for (int i = 0; i < done.size(); i++) lg.append(' ').append(@PKG@.WdCodec.desc((@IS@) ((Object[]) done.get(i))[2]));
  @PKG@.WdStore.log("CLEAR " + d.uuid + " " + d.key + " loadout=" + (n + 1) + " rev=" + d.rev + " to-inventory:" + lg.toString() + (notes.size() > 0 ? " kept: " + join(notes) : ""));
  return "+Cleared " + old.title() + ": " + done.size() + " " + (done.size() == 1 ? "stack" : "stacks") + " moved to your inventory" + (wornOld == n ? ", your gear stays on you" : "") + ".";
}""")
# THE CRASH REPAIR: a journal left by a previous run (or a failed one, force) is reconciled with the LIVE inventory, spot by spot
M(tx, r"""
public static boolean setSpot(@PKG@.WdData d, int n, int part, int slot, @IS@ want, String why, int other) {
  @IS@[] a = d.slots[n].arr(part);
  if (@PKG@.WdCodec.same(a[slot], want)) return false;
  @IS@ old = a[slot];
  a[slot] = want;
  if (!@PKG@.WdCodec.empty(old)) {
    int at = d.park(part, slot, old, n, other, "repair-" + why);
    @PKG@.WdStore.log("PARK " + d.key + " " + @PKG@.WdCodec.desc(old) + " displaced from loadout " + (n + 1) + " -> " + (at < 0 ? "orphans (retried at every load)" : "loadout " + (at + 1)));
  }
  return true;
}""")
M(tx, r"""
public static String repairEquip(@PKG@.WdData d, org.bson.BsonDocument j, @IC@ arm, @IC@ hot, @IC@[] all, java.util.ArrayList notes) {
  int n = @PKG@.WdCodec.intOf(j, "n", -1);
  int from = @PKG@.WdCodec.intOf(j, "from", -1);
  if (n < 0 || n >= d.slots.length) return "-bad journal";
  org.bson.BsonArray ms = j.getArray("moves", new org.bson.BsonArray());
  int hap = 0;
  int not = 0;
  int odd = 0;
  boolean ch = false;
  for (int i = 0; i < ms.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) ms.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument m = v.asDocument();
    int part = @PKG@.WdCodec.intOf(m, "part", -1);
    int slot = @PKG@.WdCodec.intOf(m, "slot", -1);
    int dest = @PKG@.WdCodec.intOf(m, "dest", -1);
    @IS@ on = @PKG@.WdCodec.stackOf(@PKG@.WdCodec.docOf(m, "on"));
    @IS@ off = @PKG@.WdCodec.stackOf(@PKG@.WdCodec.docOf(m, "off"));
    @IC@ c = part == 0 ? arm : (part == 1 ? hot : null);
    if (c == null || slot < 0 || slot >= c.getCapacity() || dest < 0 || dest >= d.slots.length || slot >= d.slots[n].arr(part).length) { odd++; continue; }
    @IS@ live = c.getItemStack((short) slot);
    boolean happened = moved(live, on, off, all, m);
    boolean notYet = !happened && @PKG@.WdCodec.same(live, off);
    if (happened) {
      hap++;
      if (on != null && @PKG@.WdCodec.same(d.slots[n].arr(part)[slot], on)) { d.slots[n].arr(part)[slot] = null; ch = true; }
      if (off != null && setSpot(d, dest, part, slot, off, "happened", n)) ch = true;
    } else if (notYet) {
      not++;
      if (off != null && @PKG@.WdCodec.same(d.slots[dest].arr(part)[slot], off)) { d.slots[dest].arr(part)[slot] = null; ch = true; }
      if (on != null && setSpot(d, n, part, slot, on, "undone", dest)) ch = true;
    } else {
      // neither piece sits in that spot (a half-done move, or the player moved things before the crash): each piece must exist exactly
      // once - one found anywhere in the inventory leaves the wardrobe, one found nowhere goes (back) into it
      odd++;
      boolean onL = onHere(all, on, m);
      boolean offL = offHere(all, off, m);
      if (on != null) {
        if (onL) { if (@PKG@.WdCodec.same(d.slots[n].arr(part)[slot], on)) { d.slots[n].arr(part)[slot] = null; ch = true; } }
        else if (setSpot(d, n, part, slot, on, "unclear-on", dest)) ch = true;
      }
      if (off != null) {
        if (offL) { if (@PKG@.WdCodec.same(d.slots[dest].arr(part)[slot], off)) { d.slots[dest].arr(part)[slot] = null; ch = true; } }
        else if (setSpot(d, dest, part, slot, off, "unclear-off", n)) ch = true;
      }
      notes.add((part == 0 ? "armor " : "hotbar ") + (slot + 1) + ": " + (on == null ? "-" : on.getItemId() + (onL ? " is in your inventory" : " back in the wardrobe")) + ", " + (off == null ? "-" : off.getItemId() + (offL ? " is in your inventory" : " back in the wardrobe")));
    }
  }
  int nw = not == 0 && hap > 0 ? n : (hap == 0 ? from : n);
  if (nw < -1 || nw >= d.slots.length) nw = -1;
  if (d.worn != nw) { d.worn = nw; ch = true; }
  return (ch ? "changed" : "same") + " equip " + (n + 1) + ": " + hap + " done, " + not + " not done, " + odd + " unclear";
}""")
M(tx, r"""
public static String repairClear(@PKG@.WdData d, org.bson.BsonDocument j, @IC@[] all, java.util.ArrayList notes) {
  int n = @PKG@.WdCodec.intOf(j, "n", -1);
  if (n < 0 || n >= d.slots.length) return "-bad journal";
  org.bson.BsonArray it = j.getArray("items", new org.bson.BsonArray());
  int dup = 0;
  int lost = 0;
  boolean ch = false;
  for (int i = 0; i < it.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) it.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument x = v.asDocument();
    int part = @PKG@.WdCodec.intOf(x, "part", -1);
    int slot = @PKG@.WdCodec.intOf(x, "slot", -1);
    int before = @PKG@.WdCodec.intOf(x, "before", 0);
    @IS@ S = @PKG@.WdCodec.stackOf(@PKG@.WdCodec.docOf(x, "item"));
    if (S == null || part < 0 || part > 1 || slot < 0 || slot >= d.slots[n].arr(part).length) continue;
    boolean inLive = countKind(all, S) > before;   // (some of) it arrived - eaten from / used since counts too, never re-stored
    boolean inFile = @PKG@.WdCodec.same(d.slots[n].arr(part)[slot], S);
    if (inLive && inFile) { d.slots[n].arr(part)[slot] = null; dup++; ch = true; }
    else if (!inLive && !inFile) { setSpot(d, n, part, slot, S, "clear-undone", -1); lost++; ch = true; }
  }
  return (ch ? "changed" : "same") + " clear " + (n + 1) + ": " + dup + " stored twice fixed, " + lost + " brought back";
}""")
# EVIDENCE (pure, nothing changes): { happened, not happened, unclear } moves of equip step i against the LIVE inventory. A spot that
# holds the piece an OLDER step of the chain took off counts as "not happened" (that older step did not reach the inventory either)
M(tx, r"""
public static int[] evEquip(org.bson.BsonArray steps, int i, @IC@ arm, @IC@ hot, @IC@[] all) {
  int hap = 0;
  int not = 0;
  int odd = 0;
  org.bson.BsonValue sv = (org.bson.BsonValue) steps.get(i);
  if (sv == null || !sv.isDocument()) return new int[] { 0, 0, 1 };
  org.bson.BsonArray ms = sv.asDocument().getArray("moves", new org.bson.BsonArray());
  for (int k = 0; k < ms.size(); k++) {
    org.bson.BsonValue v = (org.bson.BsonValue) ms.get(k);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument m = v.asDocument();
    int part = @PKG@.WdCodec.intOf(m, "part", -1);
    int slot = @PKG@.WdCodec.intOf(m, "slot", -1);
    @IC@ c = part == 0 ? arm : (part == 1 ? hot : null);
    if (c == null || slot < 0 || slot >= c.getCapacity()) { odd++; continue; }
    @IS@ on = @PKG@.WdCodec.stackOf(@PKG@.WdCodec.docOf(m, "on"));
    @IS@ off = @PKG@.WdCodec.stackOf(@PKG@.WdCodec.docOf(m, "off"));
    @IS@ live = c.getItemStack((short) slot);
    if (moved(live, on, off, all, m)) { hap++; continue; }
    if (@PKG@.WdCodec.same(live, off)) { not++; continue; }
    boolean older = false;
    for (int q = i - 1; q >= 0 && !older; q--) {
      org.bson.BsonValue qv = (org.bson.BsonValue) steps.get(q);
      if (qv == null || !qv.isDocument() || !"equip".equals(@PKG@.WdCodec.strOf(qv.asDocument(), "op"))) continue;
      org.bson.BsonArray qm = qv.asDocument().getArray("moves", new org.bson.BsonArray());
      for (int r = 0; r < qm.size() && !older; r++) {
        org.bson.BsonValue rv = (org.bson.BsonValue) qm.get(r);
        if (rv == null || !rv.isDocument()) continue;
        org.bson.BsonDocument x = rv.asDocument();
        if (@PKG@.WdCodec.intOf(x, "part", -1) == part && @PKG@.WdCodec.intOf(x, "slot", -1) == slot && @PKG@.WdCodec.same(live, @PKG@.WdCodec.stackOf(@PKG@.WdCodec.docOf(x, "off")))) older = true;
      }
    }
    if (older) not++; else odd++;
  }
  return new int[] { hap, not, odd };
}""")
M(tx, r"""
public static int[] evClear(org.bson.BsonDocument st, @IC@[] all) {
  int hap = 0;
  int not = 0;
  org.bson.BsonArray it = st.getArray("items", new org.bson.BsonArray());
  for (int i = 0; i < it.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) it.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument x = v.asDocument();
    @IS@ S = @PKG@.WdCodec.stackOf(@PKG@.WdCodec.docOf(x, "item"));
    if (S == null) continue;
    if (countKind(all, S) > @PKG@.WdCodec.intOf(x, "before", 0)) hap++; else not++;
  }
  return new int[] { hap, not, 0 };
}""")
# a step that never reached the inventory: the wardrobe's items + the equipped mark go back exactly to its "pre" copy (names / pets /
# abilities stay as they are now, except a Clear's own loadout, whose Clear never happened). false = no usable copy
M(tx, r"""
public static boolean restorePre(@PKG@.WdData d, org.bson.BsonDocument st, String op) {
  org.bson.BsonDocument pre = @PKG@.WdCodec.docOf(st, "pre");
  if (pre == null) return false;
  @PKG@.WdData p = @PKG@.WdStore.fromDoc(pre, d.key, d.uuid);
  if (p.bad) return false;
  for (int i = 0; i < d.slots.length && i < p.slots.length; i++) {
    for (int x = 0; x < d.slots[i].armor.length; x++) d.slots[i].armor[x] = p.slots[i].armor[x];
    for (int x = 0; x < d.slots[i].hot.length; x++) d.slots[i].hot[x] = p.slots[i].hot[x];
  }
  d.worn = p.worn;
  d.orphans = p.orphans;
  if ("clear".equals(op)) {
    int n = @PKG@.WdCodec.intOf(st, "n", -1);
    if (n >= 0 && n < d.slots.length) {
      @PKG@.WdLoad L = d.slots[n];
      @PKG@.WdLoad P = p.slots[n];
      L.name = P.name; L.hasPets = P.hasPets; L.pet = P.pet; L.summon = P.summon; L.abil = P.abil;
    }
  }
  return true;
}""")
# returns null when there was nothing to repair, else a line for the player / admin. force = a journal of this run or a failed one too.
# THE CHAIN: newest step first - a step with no evidence in the inventory is undone exactly (its "pre" copy) and the next older one is
# checked; the first step that did reach the inventory (or is unclear) is reconciled spot by spot and older steps are left alone (they
# reached the inventory before it). NO epoch rule (fixer 2): profile:epoch also moves without an inventory save (first profile, admin
# setclass, join repair), so a journal is ALWAYS reconciled when its key is active again - a key switched away from was saved by
# SkyyProfiles after the change, so replaying it then finds every move "happened" (nothing changes). Unreadable sections keep the journal.
M(tx, r"""
public static String repair(@PKG@.WdData d, @IC@ arm, @IC@ hot, @IC@ sto, @IC@ bak, boolean force, java.util.ArrayList notes) {
  if (d == null) return null;
  org.bson.BsonDocument j = @PKG@.WdJournal.read(d.key);
  if (j == null) return null;
  // a saved change of THIS run inside its keep window: memory, file and inventory agree - nothing to reconcile (an admin repair too)
  if (@PKG@.WdJournal.PENDING.containsKey(d.key)) return null;
  String stage = @PKG@.WdCodec.strOf(j, "stage");
  if (!force && "failed".equals(stage)) return null;
  // the evidence needs the live armor, hotbar and storage: unreadable = the journal is kept and nothing may change on top of it
  if (arm == null || hot == null || sto == null) {
    @PKG@.WdLog.warnOnce("repairsec:" + d.key, "the wardrobe repair of " + d.key + " could not read the inventory - the journal is kept for the next try");
    return "-Your inventory could not be read just now - the interrupted loadout change is kept for the next try.";
  }
  if (force && d.bad && "failed".equals(stage)) {
    @PKG@.WdData fresh = @PKG@.WdStore.readFile(d.key, d.uuid);
    if (fresh.bad) return "-The wardrobe file itself cannot be read - fix the file first.";
    d.rev = fresh.rev; d.floor = fresh.floor; d.worn = fresh.worn; d.orphans = fresh.orphans;
    for (int i = 0; i < d.slots.length; i++) d.slots[i].setFrom(fresh.slots[i]);
    d.bad = false; d.why = "";
  }
  if (d.bad) return null;
  org.bson.BsonArray steps = @PKG@.WdJournal.stepsOf(j);
  @IC@[] allE = new @IC@[] { arm, hot, sto, bak };
  @IC@[] allC = new @IC@[] { sto, hot, bak, arm };
  boolean ch = false;
  int undone = 0;
  String r = null;
  for (int i = steps.size() - 1; i >= 0 && r == null; i--) {
    org.bson.BsonValue v = (org.bson.BsonValue) steps.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument st = v.asDocument();
    String op = @PKG@.WdCodec.strOf(st, "op");
    int[] ev = "equip".equals(op) ? evEquip(steps, i, arm, hot, allE) : ("clear".equals(op) ? evClear(st, allC) : new int[] { 0, 0, 1 });
    if (ev[0] == 0 && ev[2] == 0 && restorePre(d, st, op)) { ch = true; undone++; continue; }
    if ("equip".equals(op)) r = repairEquip(d, st, arm, hot, allE, notes);
    else if ("clear".equals(op)) r = repairClear(d, st, allC, notes);
    else r = "same unknown journal op " + op;
  }
  if (r == null) r = "same";
  if (r.startsWith("changed")) ch = true;
  String what = (undone > 0 ? undone + (undone == 1 ? " change" : " changes") + " that never reached your inventory undone" : "") + (r.indexOf(' ') > 0 ? (undone > 0 ? ", " : "") + r.substring(r.indexOf(' ') + 1) : "");
  if (ch) {
    d.rev = d.rev + 1L;
    if (!@PKG@.WdStore.save(d)) {
      @PKG@.WdData fresh = @PKG@.WdStore.readFile(d.key, d.uuid);
      if (!fresh.bad) { d.rev = fresh.rev; d.worn = fresh.worn; d.orphans = fresh.orphans; for (int i = 0; i < d.slots.length; i++) d.slots[i].setFrom(fresh.slots[i]); }
      return "-The repair could not be saved - the journal is kept for the next try.";
    }
  }
  @PKG@.WdJournal.delete(d.key);
  REPAIRS = REPAIRS + 1L;
  @PKG@.WdStore.log("REPAIR " + d.uuid + " " + d.key + " stage=" + stage + " steps=" + steps.size() + " undone=" + undone + " " + r + (notes.size() > 0 ? " notes: " + join(notes) : ""));
  @PKG@.WdLog.info("repaired an interrupted wardrobe change of " + d.key + ": " + what);
  return "=An interrupted loadout change was checked against what you carry: " + (what.length() == 0 ? "nothing to fix" : what) + ".";
}""")

# =====================================================================================================================
# WdGate: the refusals (dead, combat, busy, after a switch, the gap) - pure rule + the engine reads
# =====================================================================================================================
for _f in ("EPOCH", "EPOCHAT", "BUSYAT", "LAST", "BUSY"):
    F(gate, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
M(gate, r"""
public static String why(boolean dead, long combatAgo, boolean busy, long settleLeft, long gapLeft) {
  if (dead) return "-You cannot change loadouts while dead.";
  if (busy) return "-Your profile is still loading - try again in a moment.";
  if (settleLeft > 0L) return "-Loadouts open again " + ((settleLeft + 999L) / 1000L) + " s after a profile switch (crash safety).";
  long cm = (long) @PKG@.WdCfg.COMBAT_S * 1000L;
  if (combatAgo >= 0L && cm > 0L && combatAgo < cm) return "-You are in combat - wait " + ((cm - combatAgo + 999L) / 1000L) + " s.";
  if (gapLeft > 0L) return "-One loadout change at a time - wait a moment.";
  return null;
}""")
M(gate, r"""
public static boolean busy(java.util.UUID u) {
  try { return Boolean.TRUE.equals(@PKG@.WdLog.bridge().get("profile:busy:" + u.toString())); } catch (Throwable t) { return false; }
}""")
# remember the profile epoch (first sight = baseline, a later change = the settle window) and when profile:busy was last seen
M(gate, r"""
public static void observe(java.util.UUID u, long now) {
  if (u == null) return;
  try {
    Object e = @PKG@.WdLog.bridge().get("profile:epoch:" + u.toString());
    if (e instanceof Number) {
      Object old = EPOCH.put(u, Long.valueOf(((Number) e).longValue()));
      if (old instanceof Long && ((Long) old).longValue() != ((Number) e).longValue()) EPOCHAT.put(u, Long.valueOf(now));
    }
    if (busy(u)) BUSYAT.put(u, Long.valueOf(now));
  } catch (Throwable t) { }
}""")
M(gate, r"""
public static long settleLeft(java.util.UUID u, long now) {
  long w = (long) @PKG@.WdCfg.SETTLE_S * 1000L;
  if (w <= 0L) return 0L;
  long last = 0L;
  Object a = EPOCHAT.get(u);
  Object b = BUSYAT.get(u);
  if (a instanceof Long && ((Long) a).longValue() > last) last = ((Long) a).longValue();
  if (b instanceof Long && ((Long) b).longValue() > last) last = ((Long) b).longValue();
  if (last <= 0L) return 0L;
  long left = last + w - now;
  return left > 0L ? left : 0L;
}""")
M(gate, r"""
public static long gapLeft(java.util.UUID u, long now) {
  Object o = LAST.get(u);
  if (!(o instanceof Long)) return 0L;
  long left = ((Long) o).longValue() + (long) @PKG@.WdCfg.GAP_S * 1000L - now;
  return left > 0L ? left : 0L;
}""")
M(gate, r"""
public static long agoMs(java.time.Instant then, java.time.Instant now) {
  if (then == null || now == null) return -1L;
  try {
    long ms = java.time.Duration.between(then, now).toMillis();
    return ms < 0L ? -1L : ms;
  } catch (Throwable t) { return -1L; }
}""")
# { dead 1 / 0, ms since the last damage taken or dealt (-1 = never) } (the SkyyProfiles 0.1 refuse() reads)
M(gate, r"""
public static long[] read(@ST@ st, @REF@ ref) {
  long[] r = new long[] { 0L, -1L };
  if (st == null || ref == null) return r;
  try { if (st.getComponent(ref, @DEATH@.getComponentType()) != null) r[0] = 1L; } catch (Throwable t) { }
  try {
    @DDC@ dc = (@DDC@) st.getComponent(ref, @DDC@.getComponentType());
    if (dc != null) {
      @TR@ tr = (@TR@) st.getResource(@TR@.getResourceType());
      java.time.Instant now = tr == null ? null : tr.getNow();
      long a = agoMs(dc.getLastDamageTime(), now);
      long b = agoMs(dc.getLastCombatAction(), now);
      long m = -1L;
      if (a >= 0L) m = a;
      if (b >= 0L && (m < 0L || b < m)) m = b;
      r[1] = m;
    }
  } catch (Throwable t) { }
  return r;
}""")
M(gate, r"""
public static String check(java.util.UUID u, @ST@ st, @REF@ ref, long now) {
  observe(u, now);
  long[] r = read(st, ref);
  return why(r[0] != 0L, r[1], busy(u), settleLeft(u, now), gapLeft(u, now));
}""")

# =====================================================================================================================
# WdOps: what a click / command does (the player's world thread): one key per operation, the gate, the busy flag, repair-first
# =====================================================================================================================
F(ops, "public static volatile @PKG@.WdInvApi INV = null;")   # HARNESS SEAM ONLY (null in game): the inventory sections
M(ops, r"""
public static @IC@ section(@ST@ st, @REF@ ref, int which) {
  if (INV != null) return INV.section(st, ref, which);
  if (st == null || ref == null) return null;
  try {
    @CT@ t = which == 0 ? @ARM@.getComponentType() : (which == 1 ? @HOT@.getComponentType() : (which == 2 ? @STO@.getComponentType() : @BAK@.getComponentType()));
    @INVC@ c = (@INVC@) st.getComponent(ref, t);
    return c == null ? null : c.getInventory();
  } catch (Throwable e) { @PKG@.WdLog.warnOnce("section" + which, "could not read an inventory section (" + which + "): " + e); return null; }
}""")
M(ops, r"""
public static String sanitize(String s) {
  if (s == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < s.length() && b.length() < @PKG@.WdCfg.NAME_MAX; i++) {
    char c = s.charAt(i);
    boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == ' ' || c == '-' || c == '\'';
    if (ok && !(c == ' ' && (b.length() == 0 || b.charAt(b.length() - 1) == ' '))) b.append(c);
  }
  return b.toString().trim();
}""")
# the pets + abilities of loadout n onto the player (after the items); notes collect what was not applied
M(ops, r"""
public static void applyRefs(java.util.UUID u, @PKG@.WdLoad L, java.util.ArrayList notes) {
  if (L.hasPets) {
    String r = @PKG@.WdBridge.petsSet(u, L.pet, L.summon);
    if (r == null) notes.add(@PKG@.WdBridge.PETS_NEED + " - your pets were not changed");
    else if (r.charAt(0) != '+') notes.add("pets: " + @PKG@.WdLog.body(r));
  }
  if (L.abil != null) {
    String r = @PKG@.WdBridge.abilSet(u, L.abil);
    if (r == null) notes.add(@PKG@.WdBridge.ABIL_NEED + " - your abilities were not changed");
    else if (r.charAt(0) != '+') notes.add("abilities: " + @PKG@.WdLog.body(r));
  }
}""")
M(ops, r"""
public static String withNotes(String res, java.util.ArrayList notes) {
  if (notes.size() == 0 || res == null || res.length() == 0) return res;
  char c = res.charAt(0);
  if (c == '-') return res;
  return "=" + @PKG@.WdLog.body(res) + " Note: " + @PKG@.WdTx.join(notes) + ".";
}""")
# op 1 equip, 2 save current, 3 clear, 4 rename (arg = the name), 5 repair only
M(ops, r"""
public static String run(@PR@ pr, @REF@ ref, @ST@ st, int op, int n, String arg) {
  if (pr == null || pr.getUuid() == null) return "-No player.";
  if (!@PKG@.WdCfg.ON && op != 3 && op != 5) return "-Loadouts are switched off on this server - Clear still works to take your gear out.";
  java.util.UUID u = pr.getUuid();
  long now = System.currentTimeMillis();
  String k = @PKG@.WdStore.pkey(u);
  @PKG@.WdData d = @PKG@.WdStore.get(k, u);
  if (d.uuid == null || d.uuid.length() == 0) d.uuid = u.toString();
  if (op != 4 && op != 5) { String g = @PKG@.WdGate.check(u, st, ref, now); if (g != null) return g; }
  if (@PKG@.WdGate.BUSY.putIfAbsent(u, Boolean.TRUE) != null) return "-One loadout change at a time - wait a moment.";
  try {
    java.util.ArrayList notes = new java.util.ArrayList();
    @IC@ arm = section(st, ref, 0);
    @IC@ hot = section(st, ref, 1);
    String rep = null;
    if (!d.bad && !@PKG@.WdGate.busy(u)) rep = @PKG@.WdTx.repair(d, arm, hot, section(st, ref, 2), section(st, ref, 3), false, notes);
    if (op == 5) return rep == null ? "=Nothing to repair." : rep;
    if (rep != null && rep.charAt(0) == '-') return rep;   // the repair could not be saved: no new change on top of it
    if (d.bad) return "-" + d.why;
    if (n < 0 || n >= @PKG@.WdData.MAX) return "-There is no loadout " + (n + 1) + " (1 - " + @PKG@.WdData.MAX + ").";
    int unl = @PKG@.WdSlots.unlocked(u, d);
    boolean locked = n >= unl;
    @PKG@.WdLoad L = d.slots[n];
    String res;
    if (op == 1) {
      if (locked && L.count() == 0) return "-" + L.title() + " is " + @PKG@.WdSlots.lockText(n) + ".";
      // what you have now belongs to the loadout you leave: its pets + abilities are kept with it (saved with the same file write)
      int wo = d.worn;
      @PKG@.WdLoad Wl = !d.bad && wo >= 0 && wo < d.slots.length && wo != n ? d.slots[wo] : null;
      @PKG@.WdLoad wKeep = Wl == null ? null : Wl.copy();
      if (Wl != null) {
        String[] pets = @PKG@.WdBridge.petsGet(u);
        if (pets != null) { Wl.hasPets = true; Wl.pet = pets[0]; Wl.summon = pets[1]; }
        String ab = @PKG@.WdBridge.abilGet(u);
        if (ab != null) Wl.abil = ab;
      }
      res = @PKG@.WdTx.equip(d, n, arm, hot, section(st, ref, 2), section(st, ref, 3), notes);
      if (res.charAt(0) == '-' && Wl != null) { Wl.hasPets = wKeep.hasPets; Wl.pet = wKeep.pet; Wl.summon = wKeep.summon; Wl.abil = wKeep.abil; }
      if (res.charAt(0) != '-') applyRefs(u, L, notes);
      @PKG@.WdGate.LAST.put(u, Long.valueOf(now));
    } else if (op == 2) {
      if (locked) return "-" + L.title() + " is " + @PKG@.WdSlots.lockText(n) + ".";
      String no = @PKG@.WdTx.link(d, n);
      if (no != null) return no;
      String[] pets = @PKG@.WdBridge.petsGet(u);
      if (pets != null) { L.hasPets = true; L.pet = pets[0]; L.summon = pets[1]; }
      else notes.add(@PKG@.WdBridge.petsHas() ? "SkyyPets could not tell your pets - they were not saved" : @PKG@.WdBridge.PETS_NEED);
      String ab = @PKG@.WdBridge.abilGet(u);
      if (ab != null) L.abil = ab;
      else notes.add(@PKG@.WdBridge.abilHas() ? "your class has no abilities to save" : @PKG@.WdBridge.ABIL_NEED);
      d.rev = d.rev + 1L;
      if (!@PKG@.WdStore.save(d)) {
        @PKG@.WdData fresh = @PKG@.WdStore.readFile(k, u.toString());
        if (!fresh.bad) { d.rev = fresh.rev; d.worn = fresh.worn; for (int i = 0; i < d.slots.length; i++) d.slots[i].setFrom(fresh.slots[i]); }
        return "-Could not save your wardrobe - nothing changed (see the server log).";
      }
      @PKG@.WdStore.log("SAVE " + u + " " + k + " loadout=" + (n + 1) + " rev=" + d.rev + " pets=" + (L.hasPets ? L.pet + "|" + L.summon : "-") + " abil=" + (L.abil == null ? "-" : L.abil));
      @PKG@.WdGate.LAST.put(u, Long.valueOf(now));
      res = "+Saved " + L.title() + ": what you wear and your hotbar are this loadout now" + (L.hasPets ? ", with your pets" : "") + (L.abil != null ? " and your abilities" : "") + ".";
    } else if (op == 3) {
      res = withNotes(@PKG@.WdTx.clear(d, n, arm, hot, section(st, ref, 2), section(st, ref, 3), notes), notes);
      @PKG@.WdGate.LAST.put(u, Long.valueOf(now));
      return rep != null && res.charAt(0) != '-' ? res + " " + @PKG@.WdLog.body(rep) : res;
    } else if (op == 4) {
      if (locked && L.blank()) return "-" + L.title() + " is " + @PKG@.WdSlots.lockText(n) + ".";
      String nm = sanitize(arg);
      String old = L.name;
      L.name = nm;
      d.rev = d.rev + 1L;
      if (!@PKG@.WdStore.save(d)) { L.name = old; d.rev = d.rev - 1L; return "-Could not save your wardrobe - the name did not change."; }
      @PKG@.WdStore.log("RENAME " + u + " " + k + " loadout=" + (n + 1) + " name=" + nm);
      res = nm.length() == 0 ? "+Loadout " + (n + 1) + " has its plain name again." : "+Loadout " + (n + 1) + " is now called " + nm + ".";
    } else return "-Unknown action.";
    res = withNotes(res, notes);
    return rep != null && res.charAt(0) != '-' ? res + " " + @PKG@.WdLog.body(rep) : res;
  } catch (IllegalStateException e) {
    if (String.valueOf(e.getMessage()).startsWith("harness crash")) throw e;
    @PKG@.WdLog.warn("wardrobe op " + op + " failed: " + e);
    return "-Something went wrong - the server log has the details.";
  } catch (Throwable t) {
    @PKG@.WdLog.warn("wardrobe op " + op + " failed: " + t);
    return "-Something went wrong - the server log has the details.";
  } finally { @PKG@.WdGate.BUSY.remove(u); }
}""")
# one-line summary per loadout (admin info, the chat list)
M(ops, r"""
public static String info(java.util.UUID u, String k) {
  @PKG@.WdData d = @PKG@.WdStore.get(k, u);
  StringBuilder sb = new StringBuilder();
  int unl = @PKG@.WdSlots.unlocked(u, d);
  sb.append(k).append(": ").append(unl).append(" slots (floor ").append(d.floor).append("), rev ").append(d.rev).append(", equipped ").append(d.worn < 0 ? "none" : String.valueOf(d.worn + 1)).append(", orphans ").append(d.orphans.size());
  if (d.bad) sb.append(", SHUT: ").append(d.why);
  for (int i = 0; i < d.slots.length; i++) {
    @PKG@.WdLoad L = d.slots[i];
    if (L.blank()) continue;
    sb.append("\n  ").append(i + 1).append(' ').append(L.title()).append(": ").append(L.countPart(0)).append(" armor, ").append(L.countPart(1)).append(" hotbar, pets ").append(L.hasPets ? L.pet + "|" + L.summon : "-").append(", abilities ").append(L.abil == null ? "-" : "saved");
  }
  return sb.toString();
}""")

# =====================================================================================================================
# WdPage: the Wardrobe page (vanilla look through tools/skyyui.py; inline; rebuilt only after a click)
# =====================================================================================================================
J_ = SUI.J
PW, PH = 1120, 900
SH = SUI.page_shell("SkyyWd", PW, PH, "Wardrobe", body_id="SkyyWdBody")
IW = SH.inner_w
HEAD_H = 30
STATUS_H, STATUS_M = 30, 6
FOOT_H = SUI.BTN_H + 8
LIST_H = SH.inner_h - HEAD_H - (STATUS_H + STATUS_M) - FOOT_H
assert SH.fit([HEAD_H, LIST_H, STATUS_H + STATUS_M, FOOT_H]) == 0, "the Wardrobe page body must be filled exactly"
CARD_W = IW - 2 * SUI.WELL_LIST_PAD - 2 * SUI.SCROLL_SPACING - SUI.SCROLL_SIZE   # the well padding + the scrollbar
CARD_H, CARD_GAP = 158, 6
BAR_W, BAR_GAP = 4, 8
ACT_W = 300
COL_W = CARD_W - BAR_W - BAR_GAP - ACT_W
FR = 46                    # an item frame (the vanilla slot border, 2 px padding): 42 px icons
FR_GAP = 4
ARM_GAP = 16               # between the 4 armor frames and the 9 hotbar frames
assert ARMOR_N * (FR + FR_GAP) + ARM_GAP + HOT_N * (FR + FR_GAP) <= COL_W, "the icon row must fit the text column"
assert LIST_H >= 4 * (CARD_H + CARD_GAP), "at least 4 cards visible without scrolling"
BTN_W = 144
assert 2 * BTN_W + 8 <= ACT_W
LINES = [("Pt", 24, "default"), ("Ab", 24, "default"), ("Nt", 22, "caption")]
TOP_PAD = 8
assert TOP_PAD + 26 + (FR + 4) + sum(h for _i, h, _k in LINES) <= CARD_H, "card text must fit"
NAME_W = 520
FIELD_W = 360
CLOSE_GAP = 12
HINT_W = IW - FIELD_W - SUI.BTN_MIN_W - 2 * CLOSE_GAP


def jl(parent, mk, root=False):
    return SUI.java_append(parent, mk, page_root=root)


def ind(s, n):
    return "\n".join((" " * n) + l for l in s.split("\n"))


CID = "SkyyWdC" + J_("i", "0")
FRAME_ID = CID + "F" + J_("k", "0")
P = {}
P["SHELL"] = SH.java("b")
_ap = SUI.Appends()
_ap.text(SH.body, "SkyyWdHead", J_("head", "Profile Fox"), "bold", h=HEAD_H, w=IW)
P["HEAD"] = _ap.java("b")
P["LIST"] = jl(SH.body, SUI.scroll_list("SkyyWdList", h=LIST_H, well=True), True)
P["CARD"] = "\n".join([
    jl("SkyyWdList", SUI.group(CID, "Left", w=CARD_W, h=CARD_H, anchor={"bottom": CARD_GAP}, bg=J_("cbg", COL["row"]))),
    jl(CID, SUI.status_bar(CID + "Bar", on=J_("worn"), col="selected", w=BAR_W, gap=BAR_GAP)),
    jl(CID, SUI.group(CID + "Tx", "Top", w=COL_W, h=CARD_H, pad={"top": TOP_PAD})),
    jl(CID + "Tx", SUI.group(CID + "R1", "Left", w=COL_W, h=26)),
    jl(CID + "R1", SUI.label(CID + "Nm", "", "strong", w=NAME_W, h=26, fit=False)),
    jl(CID + "R1", SUI.label(CID + "Tg", "", "bold", w=COL_W - NAME_W, h=26, align="End", col=J_("tgc", COL["gold"]), fit=False)),
    jl(CID + "Tx", SUI.group(CID + "Ic", "Left", w=COL_W, h=FR, anchor={"top": 2, "bottom": 2})),
] + [jl(CID + "Tx", SUI.label(CID + lid, "", kind, w=COL_W, h=h, fit=False)) for lid, h, kind in LINES]
    + [jl(CID, SUI.group(CID + "Act", "Top", w=ACT_W, h=CARD_H, pad={"top": 30}))])
P["FRAMEON"] = jl(CID + "Ic", SUI.item_frame(FRAME_ID, FR, item=J_("ic", "Weapon_Sword_Iron"), anchor={"right": FR_GAP}))
P["FRAMEOFF"] = jl(CID + "Ic", SUI.item_frame(FRAME_ID, FR, anchor={"right": FR_GAP}))
P["ARMGAP"] = jl(CID + "Ic", SUI.spacer(w=ARM_GAP - FR_GAP, h=FR))
P["BUTTONS"] = "\n".join([
    jl(CID + "Act", SUI.group(CID + "A1", "Left", w=ACT_W, h=SUI.BTN_SMALL_H)),
    jl(CID + "A1", SUI.button(CID + "Eq", "Equip", "primary", "small", w=BTN_W)),
    jl(CID + "A1", SUI.button(CID + "Sv", "Save current", "secondary", "small", w=BTN_W, anchor={"left": 8})),
    jl(CID + "Act", SUI.group(CID + "A2", "Left", w=ACT_W, h=SUI.BTN_SMALL_H, anchor={"top": 8})),
    jl(CID + "A2", SUI.button(CID + "Rn", "Rename", "secondary", "small", w=BTN_W)),
    jl(CID + "A2", SUI.button(CID + "Cl", "Clear", "destructive", "small", w=BTN_W, anchor={"left": 8})),
])
P["BUTTONSNOSV"] = "\n".join([
    jl(CID + "Act", SUI.group(CID + "A1", "Left", w=ACT_W, h=SUI.BTN_SMALL_H)),
    jl(CID + "A1", SUI.button(CID + "Eq", "Equip", "primary", "small", w=BTN_W)),
    jl(CID + "A1", SUI.button(CID + "Sv", "Save current", "secondary", "small", w=BTN_W, disabled=True, anchor={"left": 8})),
    jl(CID + "Act", SUI.group(CID + "A2", "Left", w=ACT_W, h=SUI.BTN_SMALL_H, anchor={"top": 8})),
    jl(CID + "A2", SUI.button(CID + "Rn", "Rename", "secondary", "small", w=BTN_W)),
    jl(CID + "A2", SUI.button(CID + "Cl", "Clear", "destructive", "small", w=BTN_W, anchor={"left": 8})),
])
P["LOCKWORD"] = jl(CID + "Act", SUI.state_word(None, "Locked", "disabled", w=2 * BTN_W + 8, h=SUI.BTN_SMALL_H))
P["STATUS"] = jl(SH.body, SUI.status_line("SkyyWdStatus", anchor={"top": STATUS_M}), True)
P["FOOT"] = "\n".join([
    jl(SH.body, SUI.group("SkyyWdFoot", "Left", w=IW, h=SUI.BTN_H, anchor={"top": 8}), True),
    jl("SkyyWdFoot", SUI.text_field("SkyyWdNameBox", "SkyyWdName", w=FIELD_W, h=SUI.FIELD_H, placeholder="Type a name then press Rename",
                                    max_length=32, anchor={"top": (SUI.BTN_H - SUI.FIELD_H) // 2})),
    jl("SkyyWdFoot", SUI.label("SkyyWdHint", "", "caption", w=HINT_W, h=SUI.BTN_H, anchor={"left": CLOSE_GAP}, wrap=True, fit=False)),
    jl("SkyyWdFoot", SUI.button("SkyyWdClose", "Close", "secondary", sound="cancel", anchor={"left": CLOSE_GAP})),
])

for _f in ("public String tok;", "public long base;", "public long seq;", "public String info;", "public int pend;", "public long pendAt;",
           "public static volatile long BUILDS = 0L;", "public static volatile long CLICKS = 0L;", "public static volatile long STALE = 0L;"):
    F(page, _f)
C(page, r"""
public WdPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.tok = "0"; this.base = System.nanoTime() & 0xffffffL; this.seq = 0L; this.info = ""; this.pend = -1; this.pendAt = 0L;
}""")
for _l in SUI.java_status_methods():
    M(page, _l)
M(page, r"""
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
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(page, r"""
public static int toInt(String s) {
  try { return Integer.parseInt(s.trim()); } catch (Throwable t) { return -1; }
}""")
# a plain item id for an ItemIcon (anything else -> "": no icon)
M(page, r"""
public static String safe(String id) {
  if (id == null) return "";
  for (int i = 0; i < id.length(); i++) {
    char c = id.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "";
  }
  return id;
}""")
M(page, r"""
public static String iconOf(@IS@ s) {
  if (@PKG@.WdCodec.empty(s) || !@PKG@.WdCodec.known(s.getItemId())) return "";   // a gone item: an empty frame (no client warning)
  return safe(s.getItemId());
}""")
BUILD_SRC = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  BUILDS = BUILDS + 1L;
  this.seq = this.seq + 1L;
  this.tok = Long.toHexString(this.base + this.seq);
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.WdStore.pkey(u);
  @PKG@.WdData d = @PKG@.WdStore.get(k, u);
  int unl = @PKG@.WdSlots.unlocked(u, d);
  int shown = @PKG@.WdSlots.shown(d, unl);
  int used = 0;
  for (int q = 0; q < unl && q < d.slots.length; q++) if (!d.slots[q].blank()) used++;
  int lv = @PKG@.WdSlots.overall(u);
  Object pn = @PKG@.WdLog.bridge().get("profile:name:" + u.toString());
  String head = (pn instanceof String && ((String) pn).length() > 0 ? "Profile " + pn + "  -  " : "") + used + " of " + unl + " loadouts used" + (lv >= 0 ? "  -  Overall Level " + lv : "");
  if (unl < d.slots.length && unl < @PKG@.WdCfg.MAX) head = head + "  -  next slot: " + @PKG@.WdSlots.lockText(unl);
{{SHELL}}
{{HEAD}}
{{LIST}}
  @IC@ arm = @PKG@.WdOps.section(st, ref, 0);
  @IC@ hot = @PKG@.WdOps.section(st, ref, 1);
  for (int i = 0; i < shown; i++) {
    @PKG@.WdLoad L = d.slots[i];
    boolean worn = d.worn == i;
    boolean locked = i >= unl;
    String cbg = worn ? "{{ROWPRESSED}}" : "{{ROW}}";
    String tgc = worn ? "{{OKCOL}}" : (locked ? "{{OFFCOL}}" : "{{GOLDCOL}}");
{{CARD}}
    for (int k = 0; k < 13; k++) {
      @IS@ s = null;
      if (k < 4) s = L.armor[k];
      else s = L.hot[k - 4];
      if (worn && @PKG@.WdCodec.empty(s)) {
        @IC@ c = k < 4 ? arm : hot;
        int sl = k < 4 ? k : k - 4;
        if (c != null && sl < c.getCapacity()) { @IS@ live = c.getItemStack((short) sl); if (!@PKG@.WdCodec.empty(live) && !(k >= 4 && @PKG@.WdCfg.keep(live.getItemId()))) s = live; }
      }
      String ic = iconOf(s);
      if (ic.length() > 0) {
{{FRAMEON}}
      } else {
{{FRAMEOFF}}
      }
      if (k == 3) {
{{ARMGAP}}
      }
    }
    String tag = worn ? "EQUIPPED - you wear it" : (locked ? (L.blank() ? "Locked" : "Locked - still holds gear") : (L.blank() ? "Empty" : ""));
    String nt;
    if (locked) nt = "Loadout " + (i + 1) + " " + @PKG@.WdSlots.lockText(i) + (L.count() > 0 ? " - Equip and Clear still work." : ".");
    else if (worn) nt = "The icons show what you wear now. Equip another loadout and it all comes back here.";
    else if (L.blank()) nt = "Wear the gear you want, then press Save current (or Equip this empty loadout first to put your current gear away).";
    else nt = L.countPart(0) + " armor pieces and " + L.countPart(1) + " hotbar items stored here." + (d.worn >= 0 || L.count() > 0 ? " Equip it to change its pets, abilities or hotbar." : "");
    boolean canSave = worn || (d.worn < 0 && L.count() == 0);
    b.set("#SkyyWdC" + i + "Nm.Text", (i + 1) + ".  " + L.title());
    b.set("#SkyyWdC" + i + "Tg.Text", tag);
    b.set("#SkyyWdC" + i + "Pt.Text", @PKG@.WdBridge.petsText(u, L) + (L.hasPets || @PKG@.WdBridge.petsHas() ? "" : "  (" + @PKG@.WdBridge.PETS_NEED + ")"));
    b.set("#SkyyWdC" + i + "Ab.Text", @PKG@.WdBridge.abilText(L.abil) + (L.abil != null || @PKG@.WdBridge.abilHas() ? "" : "  (" + @PKG@.WdBridge.ABIL_NEED + ")"));
    b.set("#SkyyWdC" + i + "Nt.Text", nt);
    if (locked && L.count() == 0) {
{{LOCKWORD}}
    } else {
      if (canSave) {
{{BUTTONS}}
        ev.addEventBinding(@BT@.Activating, "#SkyyWdC" + i + "Sv", @EVD@.of("a", "sv").append("i", String.valueOf(i)).append("t", this.tok));
      } else {
{{BUTTONSNOSV}}
      }
      ev.addEventBinding(@BT@.Activating, "#SkyyWdC" + i + "Eq", @EVD@.of("a", "eq").append("i", String.valueOf(i)).append("t", this.tok));
      ev.addEventBinding(@BT@.Activating, "#SkyyWdC" + i + "Rn", @EVD@.of("a", "rn").append("i", String.valueOf(i)).append("t", this.tok).append("@WdName", "#SkyyWdName.Value"));
      ev.addEventBinding(@BT@.Activating, "#SkyyWdC" + i + "Cl", @EVD@.of("a", "cl").append("i", String.valueOf(i)).append("t", this.tok));
    }
  }
{{STATUS}}
  String note = this.info;
  if (note.length() == 0 && !@PKG@.WdCfg.ON) note = "-Loadouts are switched off on this server - Clear still works to take your gear out.";
  if (note.length() == 0 && d.bad) note = "-" + d.why;
  if (note.length() == 0) note = "=Equip swaps your armor, hotbar, pets and abilities in one click. Ability modifiers join once SkyyClasses has them.";
  b.set("#SkyyWdStatus.Text", textOf(note));
{{FOOT}}
  String kl = @PKG@.WdCfg.KEEP_IDS == null ? "" : @PKG@.WdCfg.KEEP_IDS.trim();
  b.set("#SkyyWdHint.Text", "Rename uses this name. " + (@PKG@.WdCfg.keep("Skyy_Menu") ? "The SkyWynn Menu item never moves." : (kl.length() == 0 || kl.equals("-") ? "Every hotbar slot swaps." : "Never moved: " + kl)));
  ev.addEventBinding(@BT@.Activating, "#SkyyWdClose", @EVD@.of("a", "close"));
}"""
P["ROWPRESSED"] = COL["rowPressed"]
P["ROW"] = COL["row"]
P["OKCOL"] = COL["success"]
P["OFFCOL"] = COL["disabled"]
P["GOLDCOL"] = COL["gold"]
_indent = {"SHELL": 2, "HEAD": 2, "LIST": 2, "CARD": 4, "FRAMEON": 8, "FRAMEOFF": 8, "ARMGAP": 8, "LOCKWORD": 6, "BUTTONS": 8, "BUTTONSNOSV": 8, "STATUS": 2,
           "FOOT": 2}
for _k, _v in P.items():
    _tag = "{{%s}}" % _k
    assert BUILD_SRC.count(_tag) == 1, _tag
    BUILD_SRC = BUILD_SRC.replace(_tag, ind(_v, _indent[_k]) if _k in _indent else _v)
assert "{{" not in BUILD_SRC
for _id in ("SkyyWdHead", "SkyyWdList", "SkyyWdStatus", "SkyyWdFoot", "SkyyWdName", "SkyyWdClose", "SkyyWdHint"):
    assert ("#%s {" % _id) in BUILD_SRC or ("#%s {" % _id) in BUILD_SRC.replace("\\", ""), "the page lost #" + _id
assert "_" not in "".join(re.findall(r"#(SkyyWd\w*)", BUILD_SRC)), "no underscores in element ids (HANDOFF section 2)"
M(page, BUILD_SRC)
PAGE_ID = hashlib.sha256(BUILD_SRC.encode("utf-8")).hexdigest()[:12]
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  CLICKS = CLICKS + 1L;
  String a = jsonStr(data, "a");
  if (a.equals("close")) { close(); return; }
  if (!jsonStr(data, "t").equals(this.tok)) { STALE = STALE + 1L; this.info = "=The page changed - here it is again."; rebuild(); return; }
  int i = toInt(jsonStr(data, "i"));
  long now = System.currentTimeMillis();
  String r = "";
  try {
    if (a.equals("eq")) { this.pend = -1; r = @PKG@.WdOps.run(this.playerRef, ref, st, 1, i, null); }
    else if (a.equals("sv")) { this.pend = -1; r = @PKG@.WdOps.run(this.playerRef, ref, st, 2, i, null); }
    else if (a.equals("rn")) { this.pend = -1; r = @PKG@.WdOps.run(this.playerRef, ref, st, 4, i, jsonStr(data, "@WdName")); }
    else if (a.equals("cl")) {
      if (this.pend == i && now - this.pendAt < 10000L && now >= this.pendAt) { this.pend = -1; r = @PKG@.WdOps.run(this.playerRef, ref, st, 3, i, null); }
      else { this.pend = i; this.pendAt = now; r = "=Press Clear again to empty loadout " + (i + 1) + ": its stored gear goes to your inventory, its pets and abilities are forgotten."; }
    }
  } catch (Throwable t) {
    @PKG@.WdLog.warn("wardrobe page click " + a + " failed: " + t);
    r = "-Something went wrong - the server log has the details.";
  }
  this.info = r == null ? "" : r;
  rebuild();
}""")

# =====================================================================================================================
# The world-thread tasks: repair at join (after profile:busy), open (wardrobe:fn:open); WdHop hops a task onto the player's world
# =====================================================================================================================
rtask.addInterface(pool.get("java.lang.Runnable"))
hop.addInterface(pool.get("java.lang.Runnable"))
otask.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public java.util.UUID u;", "public int tries;", "public boolean force;", "public java.util.UUID by;"):
    F(rtask, _f)
F(rtask, "public static volatile long RUNS = 0L;")
F(hop, "public java.util.UUID u;")
F(hop, "public Runnable task;")
F(otask, "public java.util.UUID u;")
C(rtask, "public WdRepairTask(java.util.UUID u, int tries, boolean force, java.util.UUID by) { this.u = u; this.tries = tries; this.force = force; this.by = by; }")
C(hop, "public WdHop(java.util.UUID u, Runnable task) { this.u = u; this.task = task; }")
C(otask, "public WdOpenTask(java.util.UUID u) { this.u = u; }")
M(hop, r"""
public void run() {
  try {
    @WLD@ w = @PKG@.WdEng.worldOf(this.u);
    if (w != null) w.execute(this.task);
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("hop", "could not hand a wardrobe task to a world thread: " + t); }
}""")
M(hop, r"""
public static void later(java.util.UUID u, Runnable task, long ms) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.WdHop(u, task), ms, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { @PKG@.WdLog.warnOnce("later", "could not schedule a wardrobe task: " + t); }
}""")
# the player's world thread: wait for profile:busy to clear (SkyyProfiles' crash recovery), then repair the active profile's journal
M(rtask, r"""
public void run() {
  RUNS = RUNS + 1L;
  try {
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null) return;
    if (@PKG@.WdGate.busy(this.u)) {
      if (this.tries < 60) @PKG@.WdHop.later(this.u, new @PKG@.WdRepairTask(this.u, this.tries + 1, this.force, this.by), 1000L);
      return;
    }
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) return;
    @ST@ st = ref.getStore();
    String r;
    if (this.force) {
      String k = @PKG@.WdStore.pkey(this.u);
      @PKG@.WdData d = @PKG@.WdStore.get(k, this.u);
      java.util.ArrayList notes = new java.util.ArrayList();
      r = @PKG@.WdTx.repair(d, @PKG@.WdOps.section(st, ref, 0), @PKG@.WdOps.section(st, ref, 1), @PKG@.WdOps.section(st, ref, 2), @PKG@.WdOps.section(st, ref, 3), true, notes);
      if (r == null) r = "=Nothing to repair for " + pr.getUsername() + (d.bad ? " (the wardrobe is shut: " + d.why + ")" : "") + ".";
      if (this.by != null) @PKG@.WdEng.tell(this.by, "[Wardrobe] " + @PKG@.WdLog.body(r), r.charAt(0) == '-' ? "@COLERR@" : "@COLINF@");
    } else r = @PKG@.WdOps.run(pr, ref, st, 5, 0, null);
    if (r != null && !r.startsWith("=Nothing")) @PKG@.WdEng.reply(pr, r);
  } catch (Throwable t) { @PKG@.WdLog.warn("the wardrobe repair task failed: " + t); }
}""")
M(otask, r"""
public void run() {
  try {
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null) return;
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) return;
    if (!@PKG@.WdEng.open(ref, ref.getStore(), new @PKG@.WdPage(pr))) @PKG@.WdEng.say(pr, "[Wardrobe] The Wardrobe page could not open right now.", "@COLERR@");
  } catch (Throwable t) { @PKG@.WdLog.warn("wardrobe:fn:open failed: " + t); }
}""")
ftask.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public java.util.UUID u;", "public int n;", "public java.util.UUID by;", "public String byName;", "public String name;"):
    F(ftask, _f)
C(ftask, "public WdFloorTask(java.util.UUID u, int n, java.util.UUID by, String byName, String name) { this.u = u; this.n = n; this.by = by; this.byName = byName; this.name = name; }")
M(ftask, r"""
public void run() {
  String r;
  try {
    String k = @PKG@.WdStore.pkey(this.u);
    @PKG@.WdData d = @PKG@.WdStore.get(k, this.u);
    if (d.bad) r = "-" + this.name + "'s wardrobe is shut: " + d.why;
    else if (@PKG@.WdGate.BUSY.putIfAbsent(this.u, Boolean.TRUE) != null) r = "-" + this.name + " is changing a loadout right now - try again.";
    else {
      try {
        int old = d.floor;
        d.floor = this.n;
        d.rev = d.rev + 1L;
        if (!@PKG@.WdStore.save(d)) { d.floor = old; d.rev = d.rev - 1L; r = "-Could not save - nothing changed."; }
        else {
          @PKG@.WdStore.log("ADMIN " + this.byName + " slots " + this.u + " " + k + " floor " + old + " -> " + this.n);
          r = "+" + this.name + " now has at least " + this.n + " loadout slots on this profile (" + @PKG@.WdSlots.unlocked(this.u, d) + " open).";
        }
      } finally { @PKG@.WdGate.BUSY.remove(this.u); }
    }
  } catch (Throwable t) { r = "-The slots change failed: " + t; }
  @PKG@.WdLog.info("/wardrobeadmin slots by " + this.byName + ": " + @PKG@.WdLog.body(r));
  if (this.by != null) @PKG@.WdEng.tell(this.by, "[Wardrobe] " + @PKG@.WdLog.body(r), r.charAt(0) == '-' ? "@COLERR@" : (r.charAt(0) == '+' ? "@COLOK@" : "@COLINF@"));
}""")
# wardrobe:fn:open apply(UUID) -> Boolean (TRUE = the page will open on the player's world thread) - SkyyMenu's tile
ofn.addInterface(pool.get("java.util.function.Function"))
C(ofn, "public WdOpenFn() { }")
M(ofn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
    java.util.UUID u = (java.util.UUID) o;
    @WLD@ w = @PKG@.WdEng.worldOf(u);
    if (w == null) return Boolean.FALSE;
    w.execute(new @PKG@.WdOpenTask(u));
    return Boolean.TRUE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
# the 1 s timer: profile epochs / busy (the settle window) + the journals whose keep time is over
timer.addInterface(pool.get("java.lang.Runnable"))
F(timer, "public static final java.util.concurrent.atomic.AtomicLong RUNS = new java.util.concurrent.atomic.AtomicLong();")
C(timer, "public WdTimer() { }")
M(timer, r"""
public void run() {
  try {
    RUNS.incrementAndGet();
    long now = System.currentTimeMillis();
    java.util.UUID[] on = @PKG@.WdEng.online();
    for (int i = 0; i < on.length; i++) @PKG@.WdGate.observe(on[i], now);
    @PKG@.WdJournal.sweep(now);
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("timer", "the wardrobe timer failed: " + t); }
}""")
# PlayerReadyEvent (every world switch): once per session, the repair task on the player's world thread
ready.addInterface(pool.get("java.util.function.Consumer"))
F(ready, "public static final java.util.concurrent.ConcurrentHashMap SESSION = new java.util.concurrent.ConcurrentHashMap();")
C(ready, "public WdReady() { }")
M(ready, r"""
public void accept(Object ev) {
  try {
    @REF@ r = ((@PRE@) ev).getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null || pr.getUuid() == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.WdGate.observe(u, System.currentTimeMillis());
    if (SESSION.putIfAbsent(u, Boolean.TRUE) != null) return;
    @PKG@.WdHop.later(u, new @PKG@.WdRepairTask(u, 0, false, null), 2000L);
  } catch (Throwable t) { @PKG@.WdLog.warnOnce("ready", "the wardrobe join handler failed: " + t); }
}""")
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public WdQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null || pr.getUuid() == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.WdReady.SESSION.remove(u);
    @PKG@.WdGate.BUSY.remove(u);
    @PKG@.WdGate.LAST.remove(u);
    @PKG@.WdGate.EPOCH.remove(u);
    @PKG@.WdGate.EPOCHAT.remove(u);
    @PKG@.WdGate.BUSYAT.remove(u);
  } catch (Throwable t) { }
}""")

# =====================================================================================================================
# Commands: /wardrobe (aliases /loadout /loadouts /wd; every player; every usage variant hytale:Adventurer) + /wardrobeadmin (op only)
# =====================================================================================================================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
M(cmds, r"""
public static int num(String s) {
  try { return Integer.parseInt(s.trim()) - 1; } catch (Throwable t) { return -1; }
}""")
M(cmds, r"""
public static String help() {
  return "=/wardrobe opens the page. /wardrobe <n> equips loadout n. /wardrobe equip | save | clear <n>. /wardrobe name <n> <name>.";
}""")
# a = the typed words (player variants)
M(cmds, r"""
public static void player(@PR@ pr, @REF@ ref, @ST@ st, String[] a) {
  String v = a.length > 0 && a[0] != null ? a[0].trim().toLowerCase() : "";
  String res;
  if (a.length == 1) {
    if (v.equals("help")) res = help();
    else if (num(v) >= 0) res = @PKG@.WdOps.run(pr, ref, st, 1, num(v), null);
    else res = help();
  } else if (a.length == 2) {
    int n = num(a[1]);
    if (v.equals("equip")) res = @PKG@.WdOps.run(pr, ref, st, 1, n, null);
    else if (v.equals("save")) res = @PKG@.WdOps.run(pr, ref, st, 2, n, null);
    else if (v.equals("clear")) res = @PKG@.WdOps.run(pr, ref, st, 3, n, null);
    else res = help();
  } else if (a.length == 3 && (v.equals("name") || v.equals("rename"))) res = @PKG@.WdOps.run(pr, ref, st, 4, num(a[1]), a[2]);
  else res = help();
  @PKG@.WdEng.reply(pr, res);
}""")
M(cmds, r"""
public static String admin(@PR@ pr, String[] a) {
  String v = a.length > 0 && a[0] != null ? a[0].trim().toLowerCase() : "help";
  String by = pr == null ? "console" : pr.getUsername();
  if (v.equals("reload")) {
    @PKG@.WdCfg.reloadAll();
    int bad = 0;
    java.util.Iterator it = new java.util.ArrayList(@PKG@.WdStore.CACHE.keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      Object d = @PKG@.WdStore.CACHE.get(k);
      if (d instanceof @PKG@.WdData && ((@PKG@.WdData) d).bad) { @PKG@.WdStore.CACHE.remove(k, d); bad++; }
    }
    @PKG@.WdStore.log("ADMIN " + by + " reload");
    return "+Reloaded: " + @PKG@.WdCfg.summary() + (bad > 0 ? " (" + bad + " shut wardrobes will be read again)" : "");
  }
  if (a.length < 2 || v.equals("help")) return "=/wardrobeadmin info <player> | slots <player> <n> | repair <player> | reload";
  java.util.UUID u = @PKG@.WdEng.byName(a[1]);
  if (u == null) return "-" + a[1] + " is not online.";
  String k = @PKG@.WdStore.pkey(u);
  if (v.equals("info")) return "=" + @PKG@.WdOps.info(u, k);
  if (v.equals("repair")) {
    @PKG@.WdHop.later(u, new @PKG@.WdRepairTask(u, 0, true, pr == null ? null : pr.getUuid()), 1L);
    @PKG@.WdStore.log("ADMIN " + by + " repair " + u + " " + k);
    return "=Repair queued on " + a[1] + "'s world - the answer follows in chat.";
  }
  if (v.equals("slots") && a.length >= 3) {
    int n = -1;
    try { n = Integer.parseInt(a[2].trim()); } catch (Throwable t) { n = -1; }
    if (n < 0 || n > @PKG@.WdData.MAX) return "-Slots is 0 - " + @PKG@.WdData.MAX + " (0 = no admin floor).";
    // the player's own world thread (their swaps write the same file there): never two writers at once
    @PKG@.WdHop.later(u, new @PKG@.WdFloorTask(u, n, pr == null ? null : pr.getUuid(), by, a[1]), 1L);
    return "=Slots change queued on " + a[1] + "'s world - the answer follows in chat.";
  }
  return "=/wardrobeadmin info <player> | slots <player> <n> | repair <player> | reload";
}""")
PLAYER_FORMS = [  # class, description, arg names
    ("WdArg1Cmd", "/wardrobe <n> - equip loadout n (or /wardrobe help)", ["what"]),
    ("WdArg2Cmd", "/wardrobe equip | save | clear <n>", ["action", "n"]),
    ("WdArg3Cmd", "/wardrobe name <n> <name>", ["action", "n", "name"]),
]
ARG_HELP = {"what": "a loadout number or help", "action": "equip, save, clear or name", "n": "the loadout number", "name": "the new name (one word)",
            "option": "info, slots, repair, reload or help", "player": "an online player", "count": "slots 0-18"}
for _cn, _desc, _args in PLAYER_FORMS:
    _c = cls(_cn, T["APC"])
    for _a in _args:
        F(_c, "public @RA@ %sArg;" % _a)
    _ctor = ["public %s() {" % _cn, '  super(%s);' % jstr(_desc), '  setPermissionGroups(new String[] { "hytale:Adventurer" });']
    for _a in _args:
        _ctor.append('  this.%sArg = withRequiredArg(%s, %s, @ATY@.STRING);' % (_a, jstr(_a), jstr(ARG_HELP[_a])))
    _ctor.append("}")
    C(_c, "\n".join(_ctor))
    _body = [EXEC + " {", "  String[] a = new String[%d];" % len(_args)]
    for _i, _a in enumerate(_args):
        _body.append("  try { a[%d] = String.valueOf(ctx.get(this.%sArg)); } catch (Throwable t%d) { a[%d] = \"\"; }" % (_i, _a, _i, _i))
    _body.append("  @PKG@.WdCmds.player(pr, ref, store, a);")
    _body.append("}")
    M(_c, "\n".join(_body))
_wc = ["public WdCmd() {", '  super("wardrobe", "Your loadouts: armor, hotbar, pets and abilities - one click swaps them all");',
       '  setPermissionGroups(new String[] { "hytale:Adventurer" });', '  addAliases(new String[] { "loadout", "loadouts", "wd", "wardrobes" });']
for _cn, _d, _a in PLAYER_FORMS:
    _wc.append("  addUsageVariant(new @PKG@.%s());" % _cn)
_wc.append("}")
cmd = cls("WdCmd", T["APC"])
C(cmd, "\n".join(_wc))
M(cmd, EXEC + r""" {
  if (!@PKG@.WdEng.open(ref, store, new @PKG@.WdPage(pr))) @PKG@.WdEng.reply(pr, "-The Wardrobe page could not open right now.");
}""")
ADMIN_FORMS = [
    ("WdAdminArg1Cmd", "(admin) /wardrobeadmin reload | help", ["option"]),
    ("WdAdminArg2Cmd", "(admin) /wardrobeadmin info | repair <player>", ["option", "player"]),
    ("WdAdminArg3Cmd", "(admin) /wardrobeadmin slots <player> <n>", ["option", "player", "count"]),
]
for _cn, _desc, _args in ADMIN_FORMS:
    _c = cls(_cn, T["APC"])
    for _a in _args:
        F(_c, "public @RA@ %sArg;" % _a)
    _ctor = ["public %s() {" % _cn, '  super(%s);' % jstr(_desc), '  requirePermission("@NODE@");', "  setPermissionGroups(new String[0]);"]
    for _a in _args:
        _ctor.append('  this.%sArg = withRequiredArg(%s, %s, @ATY@.STRING);' % (_a, jstr(_a), jstr(ARG_HELP[_a])))
    _ctor.append("}")
    C(_c, "\n".join(_ctor))
    _body = [EXEC + " {", "  String[] a = new String[%d];" % len(_args)]
    for _i, _a in enumerate(_args):
        _body.append("  try { a[%d] = String.valueOf(ctx.get(this.%sArg)); } catch (Throwable t%d) { a[%d] = \"\"; }" % (_i, _a, _i, _i))
    _body.append("  @PKG@.WdEng.reply(pr, @PKG@.WdCmds.admin(pr, a));")
    _body.append("}")
    M(_c, "\n".join(_body))
acmd = cls("WdAdminCmd", T["APC"])
_ac = ["public WdAdminCmd() {", '  super("wardrobeadmin", "(admin) Wardrobe: /wardrobeadmin info | slots | repair | reload");',
       '  requirePermission("@NODE@");', "  setPermissionGroups(new String[0]);"]
for _cn, _d, _a in ADMIN_FORMS:
    _ac.append("  addUsageVariant(new @PKG@.%s());" % _cn)
_ac.append("}")
C(acmd, "\n".join(_ac))
M(acmd, EXEC + " { @PKG@.WdEng.reply(pr, @PKG@.WdCmds.admin(pr, new String[] { \"help\" })); }")

# =====================================================================================================================
# the plugin
# =====================================================================================================================
plug = cls("SkyyWardrobePlugin", T["JP"])
F(plug, "public static volatile Object TIMER = null;")
C(plug, "public SkyyWardrobePlugin(@JPI@ init) { super(init); }")
M(plug, r"""
public void setup() {
  @PKG@.WdLog.LOG = getLogger();
  java.nio.file.Path mods = getDataDirectory().getParent();
  @PKG@.WdCfg.load(mods);
  @PKG@.WdStore.ROOT = mods.resolve("Skyy_SkyyWardrobe");
  @PKG@.WdStore.DIR = @PKG@.WdStore.ROOT.resolve("loadouts");
  @PKG@.WdStore.LOGF = @PKG@.WdStore.ROOT.resolve("wardrobe.log");
  int[] sc = @PKG@.WdStore.scanAll();
  @PKG@.CfgPub.start(mods, getLogger());
  @PKG@.WdLog.bridge().put("wardrobe:fn:open", new @PKG@.WdOpenFn());
  getCommandRegistry().registerCommand(new @PKG@.WdCmd());
  getCommandRegistry().registerCommand(new @PKG@.WdAdminCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.WdReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.WdQuit());
  try { TIMER = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.WdTimer(), 2L, 1L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.WdLog.warn("the wardrobe timer could not start: " + t + " - journals stay until the next start, the profile-switch wait uses the page's own reads"); }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyWardrobe] @VERSION@ ready - " + sc[0] + " wardrobe files (" + sc[3] + " stored stacks, " + sc[1] + " unreadable, " + sc[2] + " journals to repair at join); " + @PKG@.WdCfg.summary() + "; pets " + (@PKG@.WdBridge.petsHas() ? "found" : "not loaded yet (SkyyPets 0.2.3+)") + ", abilities " + (@PKG@.WdBridge.abilHas() ? "found" : "not loaded yet (SkyyClasses 0.1.19+)") + "; bridge wardrobe:fn:open; /wardrobe (/loadout), /wardrobeadmin; kit @KITID@, page @PAGEID@");
}""".replace("@PAGEID@", PAGE_ID))
M(plug, r"""
protected void shutdown() {
  try { if (TIMER instanceof java.util.concurrent.Future) ((java.util.concurrent.Future) TIMER).cancel(false); } catch (Throwable t) { }
  try { int n = @PKG@.WdJournal.dropAll(); if (n > 0) @PKG@.WdLog.info("stop: " + n + " swap journals closed (the engine saves every online player on a normal stop)"); } catch (Throwable t2) { }
  try {
    java.util.Map br = @PKG@.WdLog.bridge();
    Object f = br.get("wardrobe:fn:open");
    if (f instanceof @PKG@.WdOpenFn) br.remove("wardrobe:fn:open", f);
  } catch (Throwable t3) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t4) { }
  super.shutdown();
}""")

# ================================================================= write + assemble
kit.write(OUT)
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d (+ the config kit's 7); wardrobe page %dx%d (body %dx%d, cards %dx%d, %d visible), page id %s, kit %s"
      % (len(ALL), PW, PH, IW, SH.inner_h, CARD_W, CARD_H, LIST_H // (CARD_H + CARD_GAP), PAGE_ID, KIT_ID))
jar = os.path.join(HERE, "SkyyWardrobe-%s.jar" % VERSION)
man = B.manifest(MOD, VERSION, "SkyWynn loadouts (the SkyBlock-style wardrobe made a full loadout swapper): per-profile loadouts of armor, "
                 "hotbar, pet + summon and class abilities; one click (Equip) swaps them all under a write-ahead journal; /wardrobe "
                 "(/loadout), /wardrobeadmin; Server Setup > Wardrobe.", PKG + ".SkyyWardrobePlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
if "--deploy" in sys.argv:
    raise SystemExit("SkyyWardrobe: --deploy is not supported here - deploys go through tools/deploy_set.py")
