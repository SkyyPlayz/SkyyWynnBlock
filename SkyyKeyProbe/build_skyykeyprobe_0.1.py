"""SkyyKeyProbe 0.1 - build script (javassist via jpype). A THROWAWAY dev / test pack like SkyyGatherProbe / SkyyMonkProbe: op-only
commands, pinned for ONE test session, then removed from the SET again. It answers ONE question before the class abilities get hotkeys:
which client keys can a server mod catch (no client mods exist)?
Skyy (2026-10-08, docs/answered/ui.md line 66): "a mod that can push to the client side?" ... "yes, add the hotkey probe".
docs/answered/classes.md line 152 (LOCKED 2026-10-08): combos = Ability keys x crouch / sprint / in the air, hotbar ability items,
movement gestures - "probe data from SkyyKeyProbe 0.1 decides what is reliable" -> every key line carries crouching / sprinting / in air.
Run:   python SkyyKeyProbe/build_skyykeyprobe_0.1.py   -> SkyyKeyProbe/SkyyKeyProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyKeyProbe/test_skyykeyprobe_0.1.py    (asset validators, -Xverify:all, every code path executed, permissions, start twice
       on a scratch copy of live data, engine-access audit)

HOW A KEY REACHES THE SERVER (VERIFIED in HytaleServer.jar bytecode, 2026-10-08):
  - The client starts an interaction chain for a key and sends it in a SyncInteractionChains packet (updates[]: interactionType, chainId,
    initial, state, itemInHandId, equipSlot, interactionData[].chargeValue). InteractionManager.syncStart then asks
    InteractionContext.forInteraction(type, equipSlot) which item answers (Equipped -> the ARMOR piece in equipSlot; HeldOffhand -> the
    utility slot; Ability1-3 / Pick / Primary / Secondary -> tool / hotbar by priority; every other type -> the item in hand) and
    getRootInteractionId(type) = the entity's Interactions override, else that item's "Interactions" map entry (no entry = the chain is
    cancelled, "Missing root interaction").
  - PacketAdapters.registerInbound(PlayerPacketWatcher) runs on the network thread BEFORE the packet handler (PlayerChannelHandler
    .channelRead -> __handleInbound; the watcher lambda always returns false = never blocks a packet; the SkyySacks 0.7.12 engine fact).
    Our watcher only READS packets and hands chat lines to the player's world thread (World.execute), like SkyySacks' CraftInFilter.
  - ClientMovement packets carry the client's MovementStates (crouching, sprinting, jumping, rolling, sliding, mantling, gliding, flying,
    onGround) -> the movement edges and the crouch / sprint / air state of each key press, no world-thread component read needed.
  - Server-only chains never come from the client: Death (DeathSystems$RunDeathInteractions), GameModeSwap (GameModeTypeState
    .runInteractionsOnEnter), SwapFrom when an item is moved (InventoryUtils.moveItem). Their roots end in a vanilla SendMessage step
    (Target Owner) so the SERVER says "[KeyProbe] server ran ..." itself - no code of ours involved.

THE PACK (all ids new: SkyyKeyProbe_*; no vanilla / pack-mod id or file is overridden - the harness scans Assets.zip + UserData/Mods):
  SkyyKeyProbe_Tester  "Key Tester": the vanilla stick look (Ingredient_Stick's icon / model / texture only - never its recipe or
                       resource types), MaxStack 1. Its Interactions map EVERY player input type to its own root
                       SkyyKeyProbe_Tester_<Type>: the 8 KEY types (Primary, Secondary, Ability1-3, Use, Pick, Dodge) run a vanilla
                       Charging step (0 / 0.3 / 2 s keys, AllowIndefiniteHold false = the chain always ends by 2 s) whose branches are
                       SendMessage "server ran <Type>: TAP / HOLD / LONG HOLD"; RequireNewClick (one chain per press) and a
                       HudInputBindingEntry (the client may draw the bound key on the HUD - UNVERIFIED for items).
                       SwapTo, SwapFrom, GameModeSwap, Death -> one SendMessage step. Held, HeldOffhand, Wielding, Equipped -> one
                       silent Simple step (they may repeat while held / worn; only our throttled watcher lines report them).
  SkyyKeyProbe_Helmet  "Key Tester Helmet": the vanilla Leather head look, ArmorSlot Head, NO stats. Primary / Secondary = the vanilla
                       armor EquipItem step (click to wear it); every other type -> SkyyKeyProbe_Helmet_<Type> (same shapes). Engine read:
                       only Equipped uses a WORN piece, so the worn helmet should report Equipped only (the probe shows it).
  No Parallel step anywhere (the 2026-10-08 one-entry Parallel lesson); the harness runs the ENGINE ASSET VALIDATORS on every file.

THE COMMAND /keyprobe (alias /kprobe; op only: requirePermission skyykeyprobe.admin + empty permission groups on the root and both
usage variants). Every chat line also goes to the server log as "[SkyyKeyProbe] ...". Memory only, nothing saved, gone at a restart.
  give           the Key Tester + Key Tester Helmet (storage first, nothing dropped) and starts watching you
  on | off       start / stop watching you (off forgets your counts)
  report         which types fired this server run (tap / hold, longest hold, from which item) and which never fired; moves seen
  binds          the client's key names for each input (read from Client/Data at BUILD time); default keys UNVERIFIED (client code)
  moves on|off   movement edge lines while you hold a probe item (crouch, sprint, jump, roll, slide, mantle, glide, fly, land,
                 double-tap crouch). Default off.
  all on|off     also report chains from every OTHER item (vanilla swords, bare hand ...). Default off.
  reset          zero your counts and unmute
  The engine's own 'server ran ...' lines (SendMessage steps) are NOT capped by us: they are bounded by the player - one per
  key press (RequireNewClick) or hotbar swap / item move; SwapTo / SwapFrom keep theirs because a server-run swap never reaches
  the packet watcher.  /keyprobe off also reminds you to trash both probe items before the probe leaves the SET.
  Chat cap: the same type at most once per 0.3 s (hidden ones are counted on the next line); a type firing more than 20 times in 10 s
  is muted with one line (report still counts it). Movement edges: each at most once per 0.3 s.
"""
import sys, os, json, zipfile, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

if "--deploy" in sys.argv:
    raise SystemExit("SkyyKeyProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest")
ASSETS = os.path.join(GAME, "Assets.zip")
CLIENT_LANG = os.path.join(GAME, "Client", "Data", "Shared", "Language", "en-US", "client.lang")
NODE = "skyykeyprobe.admin"
TESTER, HELMET = "SkyyKeyProbe_Tester", "SkyyKeyProbe_Helmet"
TAP_MS, LONG_S = 300, 2.0          # tap < 0.3 s; the Charging chain ends by itself at 2 s
GATE_MS, BURST_N, BURST_MS, STALE_MS, DOUBLE_MS = 300, 20, 10000, 5000, 400

# ================= the input types (every name is checked against the server jar's InteractionType enum below)
KEYS = ["Primary", "Secondary", "Ability1", "Ability2", "Ability3", "Use", "Pick", "Dodge"]        # Charging: tap / hold
LOUD = ["SwapTo", "SwapFrom", "GameModeSwap", "Death"]                                              # one SendMessage step
QUIET = ["Held", "HeldOffhand", "Wielding", "Equipped"]                                             # one silent Simple step
TYPES = KEYS + LOUD + QUIET                                                                         # the 16 mapped types
SERVER_ONLY = ["Death", "GameModeSwap"]           # never sent by the client (SwapFrom: also server-run when an item is moved)
# the client's setting for each key type (client.lang settings.bindings.<Action>); Use / Pick INFERRED from the names
BIND_ACTIONS = [("Primary", "PrimaryItemAction", ""), ("Secondary", "SecondaryItemAction", ""), ("Ability1", "Ability1ItemAction", ""),
                ("Ability2", "Ability2ItemAction", ""), ("Ability3", "Ability3ItemAction", ""),
                ("Use", "BlockInteractAction", " (INFERRED: the setting name says block, the input type says Use)"),
                ("Pick", "PickBlock", " (INFERRED)"), ("Dodge", None, ""),
                ("crouch", "Crouch", ""), ("sprint", "Sprint", ""), ("jump", "Jump", "")]

az = zipfile.ZipFile(ASSETS)
AZ_NAMES = set(az.namelist())
ITEM_PATH = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def vanilla(item_id):
    if item_id not in ITEM_PATH:
        raise SystemExit("vanilla item %s not in Assets.zip" % item_id)
    return json.loads(az.read(ITEM_PATH[item_id]).decode("utf-8-sig"))


def flat(item_id):
    """the item as the engine builds it: Parent fields first, own fields over them (never the recipe)"""
    d = vanilla(item_id)
    out = flat(d["Parent"]) if "Parent" in d else {}
    out.update(d)
    out.pop("Parent", None)
    return out


def look_of(src_id, keys):
    v = flat(src_id)
    out = {}
    for k in keys:
        if k in v:
            out[k] = json.loads(json.dumps(v[k]))
    for k in ("Icon", "Model", "Texture"):
        if k in out and ("Common/" + out[k]) not in AZ_NAMES:
            raise SystemExit("%s of %s (%s) not in Assets.zip" % (k, src_id, out[k]))
    return out


for _i in (TESTER, HELMET):
    if _i in ITEM_PATH:
        raise SystemExit("probe id %s exists in Assets.zip" % _i)

files, lang = {}, []


def lang_line(key, text):
    for pre in ("", "server."):
        lang.append("%s%s=%s" % (pre, key, text))


def say(text):
    return {"Type": "SendMessage", "Target": "Owner", "Message": text}


def root_for(src, label, t):
    if t in KEYS:
        d = {"RequireNewClick": True, "HudInputBindingEntry": "server.hud.inputBinding.SkyyKeyProbe_%s" % t,
             "Interactions": [{"Type": "Charging", "AllowIndefiniteHold": False, "DisplayProgress": False, "Next": {
                 "0": say("[KeyProbe] server ran %s on the %s: TAP (let go before 0.3 s)" % (t, label)),
                 "0.3": say("[KeyProbe] server ran %s on the %s: HOLD (0.3 - 2 s)" % (t, label)),
                 "2": say("[KeyProbe] server ran %s on the %s: LONG HOLD (2 s - the chain stops itself here)" % (t, label))}}]}
    elif t in LOUD:
        d = {"Interactions": [say("[KeyProbe] server ran %s on the %s" % (t, label))]}
    else:
        d = {"Interactions": [{"Type": "Simple"}]}
    rid = "SkyyKeyProbe_%s_%s" % (src, t)
    files["Server/Item/RootInteractions/SkyyKeyProbe/%s.json" % rid] = json.dumps(d, indent=2)
    return rid


tester = {"TranslationProperties": {"Name": "server.items.%s.name" % TESTER, "Description": "server.items.%s.description" % TESTER},
          "MaxStack": 1}
tester.update(look_of("Ingredient_Stick", ("Icon", "IconProperties", "Model", "Texture", "PlayerAnimationsId", "ItemSoundSetId")))
tester["Interactions"] = dict((t, root_for("Tester", "Key Tester", t)) for t in TYPES)
files["Server/Item/Items/SkyyKeyProbe/%s.json" % TESTER] = json.dumps(tester, indent=2)
lang_line("items.%s.name" % TESTER, "Key Tester")
lang_line("items.%s.description" % TESTER, "SkyyKeyProbe: hold it and press every key - chat says which input fired, how long you held it, "
          "and if you were crouching / sprinting / in the air. /keyprobe report afterwards. Throwaway test item.")

_iron = flat("Armor_Iron_Head")
_equip = _iron.get("Interactions") or {}
if sorted(_equip) != ["Primary", "Secondary"] or any(v != {"Interactions": [{"Type": "EquipItem"}]} for v in _equip.values()):
    raise SystemExit("vanilla armor click-to-wear changed: %r" % _equip)
helmet = {"TranslationProperties": {"Name": "server.items.%s.name" % HELMET, "Description": "server.items.%s.description" % HELMET},
          "MaxStack": 1}
helmet.update(look_of("Armor_Leather_Light_Head", ("Icon", "IconProperties", "Model", "Texture", "PlayerAnimationsId", "ItemSoundSetId",
                                                   "Categories")))
_hi = json.loads(json.dumps(_equip))
for _t in TYPES:
    if _t not in ("Primary", "Secondary"):
        _hi[_t] = root_for("Helmet", "Key Tester Helmet (in hand or worn)", _t)
helmet["Interactions"] = _hi
helmet["Armor"] = {"ArmorSlot": "Head", "BaseDamageResistance": 0}
files["Server/Item/Items/SkyyKeyProbe/%s.json" % HELMET] = json.dumps(helmet, indent=2)
lang_line("items.%s.name" % HELMET, "Key Tester Helmet")
lang_line("items.%s.description" % HELMET, "SkyyKeyProbe: wear it and press keys (does armor get Dodge / Equipped / Ability inputs?). "
          "No stats. Throwaway test item.")
for _t in KEYS:
    lang_line("hud.inputBinding.SkyyKeyProbe_%s" % _t, "Key probe: %s" % _t)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"

# ---- asset build checks: new ids / paths only, no Parallel, 16 + 14 roots
for _p in files:
    if _p in AZ_NAMES and not _p.endswith("server.lang"):
        raise SystemExit("asset path %s exists in Assets.zip (override)" % _p)
_roots = sorted(p for p in files if "/RootInteractions/" in p)
assert len(_roots) == len(TYPES) + len(TYPES) - 2, _roots
for _p, _txt in files.items():
    if '"Parallel"' in _txt:
        raise SystemExit("%s uses a Parallel step (the probe needs none)" % _p)

# ---- /keyprobe binds: the client's own setting names (Client/Data, read-only, at build time); default keys live in client code
BIND_LINES = ["Binds - the client's setting names, read from the game's Client/Data files when this probe was built:"]
_cl = {}
if os.path.isfile(CLIENT_LANG):
    for _l in open(CLIENT_LANG, encoding="utf-8-sig", errors="replace"):
        if _l.startswith("settings.bindings.") and "=" in _l:
            _k, _v = _l.split("=", 1)
            _cl[_k.strip()[len("settings.bindings."):]] = _v.strip()
for _t, _a, _note in BIND_ACTIONS:
    if _a is None:
        BIND_LINES.append("%s: no client setting is named Dodge (the Controls list has none) - which key, if any, starts it is UNVERIFIED."
                          % _t)
    elif _a in _cl:
        BIND_LINES.append("%s: Controls setting '%s'%s - default key UNVERIFIED (the client keeps its defaults in code, no data file names them)."
                          % (_t, _cl[_a], _note))
    else:
        BIND_LINES.append("%s: no setting %s found in Client/Data - UNVERIFIED." % (_t, _a))
BIND_LINES.append("Your HUD may show the real key next to 'Key probe: <Type>' while you hold the Key Tester (needs 'Display input bindings on "
                  "HUD'; UNVERIFIED for items). Press each key and read which <Type> line comes back = the true key.")
for _l in BIND_LINES:
    if any(ord(c) > 126 for c in _l):
        raise SystemExit("non-ASCII bind line: %r" % _l)
print("assets: 2 items, %d roots, %d lang lines; binds: %d client setting names read" % (len(_roots), len(lang), len(_cl)))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.keyprobe"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "PAD": "com.hypixel.hytale.server.core.io.adapter.PacketAdapters",
    "PPW": "com.hypixel.hytale.server.core.io.adapter.PlayerPacketWatcher",
    "PF": "com.hypixel.hytale.server.core.io.adapter.PacketFilter",
    "PKT": "com.hypixel.hytale.protocol.Packet",
    "SICS": "com.hypixel.hytale.protocol.packets.interaction.SyncInteractionChains",
    "SIC": "com.hypixel.hytale.protocol.packets.interaction.SyncInteractionChain",
    "ISD": "com.hypixel.hytale.protocol.InteractionSyncData",
    "ITY": "com.hypixel.hytale.protocol.InteractionType",
    "ISTA": "com.hypixel.hytale.protocol.InteractionState",
    "CMV": "com.hypixel.hytale.protocol.packets.player.ClientMovement",
    "MVS": "com.hypixel.hytale.protocol.MovementStates",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
for c, m in ((AC, "requirePermission"), (AC, "setPermissionGroups"), (AC, "addAliases"), (AC, "addUsageVariant"), (AC, "withRequiredArg"),
             (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"), (T["PR"], "getUuid"),
             (T["PR"], "getReference"), (T["PR"], "getWorldUuid"), (T["UNI"], "get"), (T["UNI"], "getWorld"), (T["WLD"], "execute"),
             (T["MSG"], "raw"), (T["INVC"], "getCombined"), (T["INVC"], "STORAGE_HOTBAR_BACKPACK"), (T["INVC"], "getItemInHand"),
             (T["IC"], "addItemStack"), (T["IS"], "getItemId"), (T["IS"], "isEmpty"), (T["IS"], "getQuantity"), (T["IST"], "succeeded"),
             (T["IST"], "getRemainder"), (T["PAD"], "registerInbound"), (T["PAD"], "deregisterInbound"), (T["PPW"], "accept"),
             (T["SICS"], "updates"), (T["SIC"], "interactionType"), (T["SIC"], "chainId"), (T["SIC"], "initial"), (T["SIC"], "state"),
             (T["SIC"], "itemInHandId"), (T["SIC"], "equipSlot"), (T["SIC"], "forkedId"), (T["SIC"], "interactionData"),
             (T["ISD"], "chargeValue"), (T["ISTA"], "NotFinished"), (T["CMV"], "movementStates"), (T["REF"], "getStore"), (T["REF"], "isValid"),
             (PB, "getCommandRegistry"), (PB, "getLogger"), (PB, "shutdown")):
    B.probe(pool, c, m)
for _f in ("crouching", "sprinting", "jumping", "rolling", "sliding", "mantling", "gliding", "flying", "onGround"):
    B.probe(pool, T["MVS"], _f)
for _t in TYPES:
    B.probe(pool, T["ITY"], _t)          # every mapped type is a real InteractionType (the Item codec maps by enum name)
_enum = [str(f.getName()) for f in pool.get(T["ITY"]).getDeclaredFields() if str(f.getType().getName()) == T["ITY"]]
if len(_enum) > 32:
    raise SystemExit("InteractionType grew to %d values - KpState's 32-slot arrays need a bigger size" % len(_enum))
print("InteractionType: %d values, the 16 mapped ones all present; unmapped (collision / projectile / block / pickup): %s"
      % (len(_enum), [x for x in _enum if x not in TYPES]))

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
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


def jl(s):
    return json.dumps(s)          # a Java string literal (ASCII text only here)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


# ---- KpLog: the server log + chat (every chat line is logged too, so the log alone carries the results)
log = mk("KpLog")
F(log, "public static volatile @LOG@ LOG;")
F(log, "public static volatile java.util.List SINK;")          # the harness reads what chat would get
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyKeyProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyKeyProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s) {
  String who = "";
  try { who = pr == null ? "" : "to " + pr.getUsername() + ": "; } catch (Throwable t) { who = ""; }
  info(who + s);
  java.util.List k = SINK;
  if (k != null) { try { k.add(s); } catch (Throwable t) { } }
  try { if (pr != null) pr.sendMessage(@MSG@.raw(s)); } catch (Throwable t) { }
}""")

# ---- KpLogic: pure functions + constants (no engine object except the InteractionType names)
lg = mk("KpLogic")
F(lg, "public static final String TESTER = %s;" % jl(TESTER))
F(lg, "public static final String HELMET = %s;" % jl(HELMET))
F(lg, "public static final String[] EXPECT = %s;" % jarr(TYPES))
F(lg, "public static final String[] SERVER_ONLY = %s;" % jarr(SERVER_ONLY))
F(lg, "public static final String[] BINDS = %s;" % jarr(BIND_LINES))
F(lg, "public static final String[] EDGES = %s;" % jarr(["crouch ON", "crouch off", "sprint ON", "sprint off", "jump", "roll", "slide",
                                                          "mantle (ledge climb)", "glide", "fly ON", "land", "DOUBLE-TAP crouch"]))
F(lg, "public static final String[] EDGE_SHORT = %s;" % jarr(["crouch", "crouch-off", "sprint", "sprint-off", "jump", "roll", "slide",
                                                               "mantle", "glide", "fly", "land", "double-tap crouch"]))
M(lg, r"""
public static String yn(boolean b) { return b ? "y" : "n"; }""")
M(lg, r"""
public static String typeName(int ord) {
  try {
    @ITY@[] v = @ITY@.values();
    if (ord >= 0 && ord < v.length) return v[ord].name();
  } catch (Throwable t) { }
  return "Type#" + ord;
}""")
M(lg, r"""
public static int typeIndex(String name) {
  if (name == null) return -1;
  @ITY@[] v = @ITY@.values();
  for (int i = 0; i < v.length; i++) if (v[i].name().equals(name)) return i;
  return -1;
}""")
# 0 = Key Tester in hand, 1 = Helmet in hand, 2 = any other item / bare hand, 3 = an Equipped chain: the engine always answers it from
# the ARMOR container slot equipSlot (InteractionContext.forInteraction), whatever is in the hand
M(lg, r"""
public static int srcOf(String hand, String type, int slot) {
  if ("Equipped".equals(type) && slot >= 0) return 3;
  if (TESTER.equals(hand)) return 0;
  if (HELMET.equals(hand)) return 1;
  return 2;
}""")
M(lg, r"""
public static String f2(float x) {
  long c = Math.round((double) x * 100.0);
  long w = c / 100L;
  long f = Math.abs(c % 100L);
  return (c < 0L && w == 0L ? "-" : "") + w + "." + (f < 10L ? "0" : "") + f;
}""")
M(lg, r"""
public static String chainLine(String type, long hold, boolean crouch, boolean sprint, boolean air, float charge, int src, String hand,
                               int slot, String end, int hidden) {
  StringBuilder b = new StringBuilder("[KeyProbe] ").append(type).append(" fired (hold ");
  if (hold < 0L) b.append("? - no end seen within @STALE@ s");
  else b.append(hold).append(" ms ").append(hold < @TAP@L ? "tap" : "hold");
  b.append(", crouching ").append(yn(crouch)).append(", sprinting ").append(yn(sprint)).append(", in air ").append(yn(air)).append(")");
  if (charge > 0.0005f) b.append(" client charge ").append(f2(charge)).append(" s");
  if (src == 1) b.append(" - Helmet in hand");
  else if (src == 3) b.append(" - WORN armor, slot ").append(slot);
  else if (src == 2) b.append(" - other item: ").append(hand == null || hand.length() == 0 ? "empty hand" : hand);
  if (end != null && end.length() > 0 && !end.equals("Finished")) b.append(" [ended: ").append(end).append("]");
  if (hidden > 0) b.append(" (+").append(hidden).append(" more hidden)");
  return b.toString();
}""".replace("@STALE@", str(STALE_MS // 1000)).replace("@TAP@", str(TAP_MS)))
M(lg, r"""
public static String muteLine(String type) {
  return "[KeyProbe] " + type + " keeps firing (more than @BN@ times in @BS@ s) - its lines are muted now; /keyprobe report still counts it, /keyprobe reset unmutes.";
}""".replace("@BN@", str(BURST_N)).replace("@BS@", str(BURST_MS // 1000)))
M(lg, r"""
public static String moveLine(int e, long gap, int hidden) {
  String s = "[KeyProbe] move: " + (e >= 0 && e < EDGES.length ? EDGES[e] : "edge " + e);
  if (e == 11) s = s + " (" + gap + " ms between the two presses)";
  if (hidden > 0) s = s + " (+" + hidden + " more hidden)";
  return s;
}""")

# ---- KpState: one watched player (the network thread writes it, commands read it: every method is synchronized)
sta = mk("KpState")
for _f in ("public java.util.UUID uuid;", "public String name;", "public volatile boolean moves;", "public volatile boolean all;",
           "public int[] fired;", "public int[] taps;", "public int[] holds;", "public long[] longest;", "public int[] srcN;",
           "public long[] lastPrint;", "public int[] hidden;", "public long[] burstStart;", "public int[] burstN;", "public boolean[] muted;",
           "public java.util.HashMap pend;", "public java.util.HashMap pendHand;",
           "public boolean crouch;", "public boolean sprint;", "public boolean air;", "public boolean haveMv;", "public boolean[] mv;",
           "public int[] edges;", "public long[] edgePrint;", "public int[] edgeHidden;", "public long lastCrouchOn;",
           "public int others;", "public int chains;", "public int moveTicks;"):
    F(sta, _f)
C(sta, r"""
public KpState(java.util.UUID u, String n) {
  this.uuid = u;
  this.name = n == null ? "?" : n;
  this.moves = false;
  this.all = false;
  this.fired = new int[32];
  this.taps = new int[32];
  this.holds = new int[32];
  this.longest = new long[32];
  this.srcN = new int[128];
  this.lastPrint = new long[32];
  this.hidden = new int[32];
  this.burstStart = new long[32];
  this.burstN = new int[32];
  this.muted = new boolean[32];
  this.pend = new java.util.HashMap();
  this.pendHand = new java.util.HashMap();
  this.mv = new boolean[9];
  this.edges = new int[12];
  this.edgePrint = new long[12];
  this.edgeHidden = new int[12];
  this.lastCrouchOn = 0L;
}""")
# the chat cap: -1 = hide (counted), -2 = muted right now (say it once), else the number of hidden lines to report
M(sta, r"""
public synchronized int gate(int i, long now) {
  if (i < 0 || i >= 32) return -1;
  if (this.muted[i]) { this.hidden[i]++; return -1; }
  if (this.burstN[i] == 0 || now - this.burstStart[i] > @BMS@L) { this.burstStart[i] = now; this.burstN[i] = 0; }
  this.burstN[i]++;
  if (this.burstN[i] > @BN@) { this.muted[i] = true; return -2; }
  if (this.lastPrint[i] != 0L && now - this.lastPrint[i] < @GATE@L) { this.hidden[i]++; return -1; }
  this.lastPrint[i] = now;
  int h = this.hidden[i];
  this.hidden[i] = 0;
  return h;
}""".replace("@BMS@", str(BURST_MS)).replace("@BN@", str(BURST_N)).replace("@GATE@", str(GATE_MS)))
M(sta, r"""
public synchronized String finish(int chainId, String end, boolean timedOut, float charge, long now) {
  Integer k = Integer.valueOf(chainId);
  long[] p = (long[]) this.pend.remove(k);
  String hand = (String) this.pendHand.remove(k);
  if (p == null) return null;
  int ord = (int) p[0];
  long hold = timedOut ? -1L : now - p[1];
  if (hold < 0L && !timedOut) hold = 0L;
  if (hold >= 0L && ord >= 0 && ord < 32) {
    if (hold < @TAP@L) this.taps[ord]++;
    else this.holds[ord]++;
    if (hold > this.longest[ord]) this.longest[ord] = hold;
  }
  int g = gate(ord, now);
  if (g == -1) return null;
  if (g == -2) return @PKG@.KpLogic.muteLine(@PKG@.KpLogic.typeName(ord));
  return @PKG@.KpLogic.chainLine(@PKG@.KpLogic.typeName(ord), hold, p[2] == 1L, p[3] == 1L, p[6] == 1L, charge, (int) p[4], hand,
                                  (int) p[5], end, g);
}""".replace("@TAP@", str(TAP_MS)))
# a chain started (initial packet): counted at once; its line comes at its end (or after @STALE@ s without an end)
M(sta, r"""
public synchronized java.util.ArrayList start(int ord, int chainId, int src, String hand, int slot, long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (this.pend.size() > 0) {
    Object[] ks = this.pend.keySet().toArray();
    for (int i = 0; i < ks.length; i++) {
      long[] q = (long[]) this.pend.get(ks[i]);
      if (q != null && now - q[1] > @STALE@L) {
        String l = finish(((Integer) ks[i]).intValue(), "", true, 0.0f, now);
        if (l != null) out.add(l);
      }
    }
  }
  if (ord >= 0 && ord < 32) {
    this.fired[ord]++;
    if (src >= 0 && src < 4) this.srcN[ord * 4 + src]++;
  }
  this.chains++;
  Integer k = Integer.valueOf(chainId);
  if (this.pend.size() >= 32 && !this.pend.containsKey(k)) { this.pend.clear(); this.pendHand.clear(); }
  this.pend.put(k, new long[] { (long) ord, now, this.crouch ? 1L : 0L, this.sprint ? 1L : 0L, (long) src, (long) slot, this.air ? 1L : 0L });
  this.pendHand.put(k, hand == null ? "" : hand);
  return out;
}""".replace("@STALE@", str(STALE_MS)))
M(sta, r"""
public synchronized void edge(int e, long gap, long now, java.util.ArrayList out) {
  if (e < 0 || e >= 12) return;
  this.edges[e]++;
  if (!this.moves) return;
  if (this.edgePrint[e] != 0L && now - this.edgePrint[e] < @GATE@L) { this.edgeHidden[e]++; return; }
  this.edgePrint[e] = now;
  int h = this.edgeHidden[e];
  this.edgeHidden[e] = 0;
  out.add(@PKG@.KpLogic.moveLine(e, gap, h));
}""".replace("@GATE@", str(GATE_MS)))
# f = crouching, sprinting, jumping, rolling, sliding, mantling, gliding, flying, onGround (the client's MovementStates)
M(sta, r"""
public synchronized java.util.ArrayList move(boolean[] f, long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (f == null || f.length < 9) return out;
  this.moveTicks++;
  this.crouch = f[0];
  this.sprint = f[1];
  this.air = !f[8];
  if (!this.haveMv) {
    for (int i = 0; i < 9; i++) this.mv[i] = f[i];
    this.haveMv = true;
    return out;
  }
  if (f[0] && !this.mv[0]) {
    edge(0, 0L, now, out);
    if (this.lastCrouchOn != 0L && now - this.lastCrouchOn <= @DBL@L) { edge(11, now - this.lastCrouchOn, now, out); this.lastCrouchOn = 0L; }
    else this.lastCrouchOn = now;
  }
  if (!f[0] && this.mv[0]) edge(1, 0L, now, out);
  if (f[1] && !this.mv[1]) edge(2, 0L, now, out);
  if (!f[1] && this.mv[1]) edge(3, 0L, now, out);
  for (int i = 2; i < 8; i++) if (f[i] && !this.mv[i]) edge(i + 2, 0L, now, out);
  if (f[8] && !this.mv[8]) edge(10, 0L, now, out);
  for (int i = 0; i < 9; i++) this.mv[i] = f[i];
  return out;
}""".replace("@DBL@", str(DOUBLE_MS)))
M(sta, r"""
public synchronized void reset() {
  this.fired = new int[32];
  this.taps = new int[32];
  this.holds = new int[32];
  this.longest = new long[32];
  this.srcN = new int[128];
  this.lastPrint = new long[32];
  this.hidden = new int[32];
  this.burstStart = new long[32];
  this.burstN = new int[32];
  this.muted = new boolean[32];
  this.pend.clear();
  this.pendHand.clear();
  this.edges = new int[12];
  this.edgePrint = new long[12];
  this.edgeHidden = new int[12];
  this.lastCrouchOn = 0L;
  this.others = 0;
  this.chains = 0;
}""")
M(sta, r"""
public synchronized void other() { this.others++; }""")
M(sta, r"""
public synchronized java.util.ArrayList report() {
  java.util.ArrayList out = new java.util.ArrayList();
  out.add("[KeyProbe] Report for " + this.name + " (this server run; what your game client SENT; " + this.chains + " chains counted):");
  StringBuilder never = new StringBuilder();
  int n = 0;
  for (int j = 0; j < @PKG@.KpLogic.EXPECT.length; j++) {
    int i = @PKG@.KpLogic.typeIndex(@PKG@.KpLogic.EXPECT[j]);
    if (i < 0 || i >= 32) continue;
    if (this.fired[i] == 0) { never.append(never.length() == 0 ? "" : ", ").append(@PKG@.KpLogic.EXPECT[j]); continue; }
    n++;
    out.add("  " + @PKG@.KpLogic.EXPECT[j] + ": " + this.fired[i] + "x (" + this.taps[i] + " tap, " + this.holds[i] + " hold, longest "
        + this.longest[i] + " ms; Key Tester " + this.srcN[i * 4] + ", Helmet in hand " + this.srcN[i * 4 + 1] + ", worn armor "
        + this.srcN[i * 4 + 3] + ", other items " + this.srcN[i * 4 + 2] + ")" + (this.muted[i] ? " [muted]" : ""));
  }
  for (int i = 0; i < 32; i++) {
    if (this.fired[i] == 0) continue;
    boolean known = false;
    for (int j = 0; j < @PKG@.KpLogic.EXPECT.length; j++) if (@PKG@.KpLogic.EXPECT[j].equals(@PKG@.KpLogic.typeName(i))) known = true;
    if (!known) out.add("  " + @PKG@.KpLogic.typeName(i) + ": " + this.fired[i] + "x (a type the probe items do not map)");
  }
  if (n == 0) out.add("  Nothing fired yet - hold the Key Tester and press keys.");
  out.add("  Never fired: " + (never.length() == 0 ? "none" : never.toString()));
  out.add("  Chains from other items: " + this.others + (this.all ? " (shown: all on)" : " (not shown - /keyprobe all on shows them)"));
  StringBuilder mvs = new StringBuilder("  Moves seen: ");
  for (int e = 0; e < 12; e++) {
    if (e == 1 || e == 3) continue;
    mvs.append(e == 0 ? "" : ", ").append(@PKG@.KpLogic.EDGE_SHORT[e]).append(" ").append(this.edges[e]);
  }
  out.add(mvs.toString() + " (" + this.moveTicks + " movement packets)");
  out.add("  Death and GameModeSwap are run by the server, never sent by the client: look for the server's own '[KeyProbe] server ran ...' line.");
  return out;
}""")

# ---- KpSay: chat lines from the network thread, delivered on the player's world thread (needHand = only while holding a probe item)
say_ = mk("KpSay")
say_.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PR@ pr;", "public java.util.ArrayList lines;", "public boolean needHand;"):
    F(say_, _f)
C(say_, "public KpSay(@PR@ pr, java.util.ArrayList lines, boolean needHand) { this.pr = pr; this.lines = lines; this.needHand = needHand; }")
M(say_, r"""
public static String handId(@PR@ pr) {
  try {
    @REF@ r = pr == null ? null : pr.getReference();
    if (r == null || !r.isValid()) return null;
    @IS@ it = @INVC@.getItemInHand(r.getStore(), r);
    if (it == null || it.isEmpty()) return "";
    return it.getItemId();
  } catch (Throwable t) { return null; }
}""")
M(say_, r"""
public void run() {
  try {
    if (this.lines == null || this.lines.size() == 0) return;
    if (this.needHand) {
      String h = handId(this.pr);
      if (h == null || !(h.equals(@PKG@.KpLogic.TESTER) || h.equals(@PKG@.KpLogic.HELMET))) return;
    }
    for (int i = 0; i < this.lines.size(); i++) @PKG@.KpLog.tell(this.pr, (String) this.lines.get(i));
  } catch (Throwable t) { @PKG@.KpLog.warn("chat delivery failed: " + t); }
}""")

# ---- KpCore: the watched players + the packet reading (network thread: plain reads, no component access)
core = mk("KpCore")
F(core, "public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();")
F(core, "public static volatile @PF@ FILTER;")
F(core, "public static volatile long CLOCK;")                 # the harness sets a clock; 0 = real time
F(core, "public static final java.util.concurrent.atomic.AtomicLong ERRORS = new java.util.concurrent.atomic.AtomicLong();")
F(core, "public static final java.util.concurrent.atomic.AtomicLong UNDELIVERED = new java.util.concurrent.atomic.AtomicLong();")
M(core, r"""
public static long now() { long c = CLOCK; return c != 0L ? c : System.currentTimeMillis(); }""")
M(core, r"""
public static @PKG@.KpState state(java.util.UUID u) {
  if (u == null) return null;
  return (@PKG@.KpState) STATES.get(u);
}""")
M(core, r"""
public static void deliver(@PR@ pr, java.util.ArrayList lines, boolean needHand) {
  if (lines == null || lines.size() == 0) return;
  @WLD@ w = null;
  try {
    java.util.UUID wu = pr.getWorldUuid();
    @UNI@ u = @UNI@.get();
    if (wu != null && u != null) w = u.getWorld(wu);
  } catch (Throwable t) { w = null; }
  if (w == null) {
    UNDELIVERED.addAndGet((long) lines.size());
    for (int i = 0; i < lines.size(); i++) @PKG@.KpLog.info("(no world to deliver) " + lines.get(i));
    return;
  }
  w.execute(new @PKG@.KpSay(pr, lines, needHand));
}""")
M(core, r"""
public static boolean[] flags(@MVS@ m) {
  if (m == null) return null;
  return new boolean[] { m.crouching, m.sprinting, m.jumping, m.rolling, m.sliding, m.mantling, m.gliding, m.flying, m.onGround };
}""")
M(core, r"""
public static float charge(@SIC@ u) {
  float best = 0.0f;
  @ISD@[] d = u.interactionData;
  if (d == null) return 0.0f;
  for (int i = 0; i < d.length; i++) if (d[i] != null && d[i].chargeValue > best) best = d[i].chargeValue;
  return best;
}""")
# one chain update: an initial packet starts it (only probe items unless 'all'); a state other than NotFinished ends it
M(core, r"""
public static void chain(@PKG@.KpState s, @SIC@ u, long now, java.util.ArrayList out) {
  if (u == null || u.forkedId != null) return;
  if (u.initial && u.interactionType != null) {
    String type = u.interactionType.name();
    int src = @PKG@.KpLogic.srcOf(u.itemInHandId, type, u.equipSlot);
    if (src == 2) s.other();
    if (src != 2 || s.all) out.addAll(s.start(u.interactionType.ordinal(), u.chainId, src, u.itemInHandId, u.equipSlot, now));
  }
  if (u.state != null && u.state != @IST@.NotFinished) {
    String l = s.finish(u.chainId, u.state.name(), false, charge(u), now);
    if (l != null) out.add(l);
  }
}""".replace("@IST@", T["ISTA"]))
M(core, r"""
public static void packet(@PR@ pr, @PKT@ p) {
  if (pr == null || p == null || STATES.isEmpty()) return;
  try {
    boolean mv = p instanceof @CMV@;
    boolean ch = p instanceof @SICS@;
    if (!mv && !ch) return;
    @PKG@.KpState s = state(pr.getUuid());
    if (s == null) return;
    long now = now();
    if (mv) {
      boolean[] f = flags(((@CMV@) p).movementStates);
      if (f == null) return;
      java.util.ArrayList l = s.move(f, now);
      if (l.size() > 0) deliver(pr, l, true);
      return;
    }
    @SIC@[] us = ((@SICS@) p).updates;
    if (us == null) return;
    java.util.ArrayList out = new java.util.ArrayList();
    for (int i = 0; i < us.length; i++) chain(s, us[i], now, out);
    if (out.size() > 0) deliver(pr, out, false);
  } catch (Throwable t) {
    if (ERRORS.incrementAndGet() <= 3L) @PKG@.KpLog.warn("packet read failed (logged 3 times at most): " + t);
  }
}""")
M(core, r"""
public static synchronized void stop() {
  @PF@ f = FILTER;
  FILTER = null;
  if (f != null) { try { @PAD@.deregisterInbound(f); } catch (Throwable t) { } }
  STATES.clear();
}""")

# ---- KpWatch: the inbound packet watcher (network thread; never blocks a packet - the engine's watcher lambda returns false)
wat = mk("KpWatch")
wat.addInterface(pool.get(T["PPW"]))
C(wat, "public KpWatch() { }")
M(wat, "public void accept(@PR@ pr, @PKT@ p) { @PKG@.KpCore.packet(pr, p); }")
M(wat, "public void accept(Object a, Object b) { if (a instanceof @PR@ && b instanceof @PKT@) accept((@PR@) a, (@PKT@) b); }")
# KpCore.start names KpWatch: compiled after it (javassist compiles calls against classes that exist)
M(core, r"""
public static synchronized void start() {
  stop();
  try { FILTER = @PAD@.registerInbound((@PPW@) new @PKG@.KpWatch()); }
  catch (Throwable t) { FILTER = null; @PKG@.KpLog.warn("packet watcher NOT registered - the probe sees no keys: " + t); }
}""")

# ---- KpCmds: what each subcommand does (world thread)
cmds = mk("KpCmds")
F(cmds, "public static final String[] GIVE = %s;" % jarr([TESTER, HELMET]))
M(cmds, r"""
public static void tell(@PR@ pr, String s) { @PKG@.KpLog.tell(pr, s); }""")
M(cmds, r"""
public static void help(@PR@ pr) {
  tell(pr, "[KeyProbe] Key probe (op only, memory only). Which keys can a server mod catch?");
  tell(pr, "/keyprobe give - the Key Tester + Key Tester Helmet, and starts watching you | on | off");
  tell(pr, "/keyprobe report - what fired / never fired | binds - the client's key names | reset");
  tell(pr, "/keyprobe moves on|off - movement lines while you hold a probe item | all on|off - also chains from every other item");
}""")
M(cmds, r"""
public static @PKG@.KpState watch(@PR@ pr) {
  @PKG@.KpState s = @PKG@.KpCore.state(pr.getUuid());
  if (s != null) return s;
  s = new @PKG@.KpState(pr.getUuid(), pr.getUsername());
  Object o = @PKG@.KpCore.STATES.putIfAbsent(pr.getUuid(), s);
  return o != null ? (@PKG@.KpState) o : s;
}""")
M(cmds, r"""
public static void give(@PR@ pr, @ST@ st, @REF@ ref) {
  @PKG@.KpState s = watch(pr);
  @IC@ dst = null;
  try { dst = @INVC@.getCombined(st, ref, @INVC@.STORAGE_HOTBAR_BACKPACK); } catch (Throwable t) { dst = null; }
  if (dst == null) { tell(pr, "[KeyProbe] Could not open your inventory - nothing given (watching you anyway)."); return; }
  StringBuilder got = new StringBuilder();
  StringBuilder lost = new StringBuilder();
  for (int i = 0; i < GIVE.length; i++) {
    boolean ok = false;
    try {
      @IST@ tx = dst.addItemStack(new @IS@(GIVE[i], 1));
      @IS@ rem = tx == null ? null : tx.getRemainder();
      ok = tx != null && tx.succeeded() && (rem == null || rem.isEmpty());
    } catch (Throwable t) { @PKG@.KpLog.warn("give " + GIVE[i] + " failed: " + t); ok = false; }
    if (ok) got.append(got.length() == 0 ? "" : " + ").append(GIVE[i].equals(@PKG@.KpLogic.TESTER) ? "Key Tester" : "Key Tester Helmet");
    else lost.append(lost.length() == 0 ? "" : ", ").append(GIVE[i]);
  }
  tell(pr, "[KeyProbe] Given: " + (got.length() == 0 ? "nothing" : got.toString()) + (lost.length() > 0 ? ". No room for " + lost.toString() + " - nothing was dropped." : ".")
      + " Watching you now: hold the Key Tester and press every key, then /keyprobe report.");
}""")
M(cmds, r"""
public static void report(@PR@ pr) {
  @PKG@.KpState s = @PKG@.KpCore.state(pr.getUuid());
  if (s == null) { tell(pr, "[KeyProbe] Not watching you - /keyprobe on (or /keyprobe give) first."); return; }
  java.util.ArrayList l = s.report();
  for (int i = 0; i < l.size(); i++) tell(pr, (String) l.get(i));
  if (@PKG@.KpCore.FILTER == null) tell(pr, "[KeyProbe] WARNING: the packet watcher is not registered - see the server log.");
}""")
M(cmds, r"""
public static void binds(@PR@ pr) {
  for (int i = 0; i < @PKG@.KpLogic.BINDS.length; i++) tell(pr, (i == 0 ? "[KeyProbe] " : "  ") + @PKG@.KpLogic.BINDS[i]);
}""")
M(cmds, r"""
public static void flag(@PR@ pr, String what, String v) {
  String x = v == null ? "" : v.trim().toLowerCase(java.util.Locale.ROOT);
  if (!x.equals("on") && !x.equals("off")) { tell(pr, "[KeyProbe] Usage: /keyprobe " + what + " on|off"); return; }
  @PKG@.KpState s = watch(pr);
  boolean on = x.equals("on");
  if (what.equals("moves")) {
    s.moves = on;
    tell(pr, "[KeyProbe] Movement lines " + (on ? "ON - hold the Key Tester and crouch, sprint, jump, roll, double-tap crouch." : "off (still counted for the report)."));
  } else {
    s.all = on;
    tell(pr, "[KeyProbe] Chains from every item " + (on ? "ON - vanilla items and your bare hand report too." : "off - only the probe items report."));
  }
}""")
M(cmds, r"""
public static void run(@REF@ ref, @ST@ store, @PR@ pr, String what, String arg) {
  String t = what == null ? "" : what.trim().toLowerCase(java.util.Locale.ROOT);
  @PKG@.KpLog.info(pr.getUsername() + " ran /keyprobe " + t + (arg == null ? "" : " " + arg));
  if (t.equals("give")) { give(pr, store, ref); return; }
  if (t.equals("on")) { watch(pr); tell(pr, "[KeyProbe] Watching you (probe items only). /keyprobe off stops."); return; }
  if (t.equals("off") || t.equals("stop")) {
    @PKG@.KpCore.STATES.remove(pr.getUuid());
    tell(pr, "[KeyProbe] Stopped watching you; your counts are gone.");
    tell(pr, "[KeyProbe] Before this probe is removed from the server: take the Key Tester Helmet off and trash both probe items (Key Tester + Key Tester Helmet).");
    return;
  }
  if (t.equals("report")) { report(pr); return; }
  if (t.equals("binds")) { binds(pr); return; }
  if (t.equals("reset")) { watch(pr).reset(); tell(pr, "[KeyProbe] Counts zeroed, every type unmuted."); return; }
  if (t.equals("moves") || t.equals("all")) { flag(pr, t, arg); return; }
  help(pr);
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# ---- /keyprobe <what> <value>  (admin: requirePermission + no permission groups)
cmd2 = mk("KProbeArg2Cmd", T["APC"])
F(cmd2, "public @RA@ whatArg;")
F(cmd2, "public @RA@ valArg;")
C(cmd2, r"""
public KProbeArg2Cmd() {
  super("(admin) /keyprobe moves on|off, /keyprobe all on|off");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("what", "moves or all", @ATY@.STRING);
  this.valArg = withRequiredArg("value", "on or off", @ATY@.STRING);
}""")
M(cmd2, EXEC + r""" {
  String a = null, v = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); v = String.valueOf(ctx.get(this.valArg)); }
  catch (Throwable t) { @PKG@.KpLog.tell(pr, "[KeyProbe] Usage: /keyprobe moves on|off | all on|off"); return; }
  @PKG@.KpCmds.run(ref, store, pr, a, v);
}""")
# ---- /keyprobe <what>
cmd1 = mk("KProbeArgCmd", T["APC"])
F(cmd1, "public @RA@ whatArg;")
C(cmd1, r"""
public KProbeArgCmd() {
  super("(admin) /keyprobe <give, on, off, report, binds, reset>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("what", "give, on, off, report, binds or reset", @ATY@.STRING);
}""")
M(cmd1, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); }
  catch (Throwable t) { @PKG@.KpLog.tell(pr, "[KeyProbe] Usage: /keyprobe <give, on, off, report, binds, reset>"); return; }
  @PKG@.KpCmds.run(ref, store, pr, a, null);
}""")
# ---- /keyprobe (alias /kprobe): the help list
cmd = mk("KProbeCmd", T["APC"])
C(cmd, r"""
public KProbeCmd() {
  super("keyprobe", "(admin) Key probe: which client keys a server mod can catch (throwaway dev pack): /keyprobe lists the commands");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "kprobe" });
  addUsageVariant(new @PKG@.KProbeArgCmd());
  addUsageVariant(new @PKG@.KProbeArg2Cmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.KpCmds.help(pr);
}""")

# ---- the plugin
pl = mk("SkyyKeyProbePlugin", T["JP"])
C(pl, "public SkyyKeyProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.KpLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.KProbeCmd());
  @PKG@.KpCore.start();
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyKeyProbe] @VERSION@ ready - /keyprobe (admin): which client keys reach the server (throwaway dev pack, remove after the test session)");
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.KpCore.stop();
  super.shutdown();
}""")

ALL = [log, lg, sta, say_, core, wat, cmds, cmd2, cmd1, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "SkyyKeyProbe-%s.jar" % VERSION)
man = B.manifest("SkyyKeyProbe", VERSION, "SkyWynn THROWAWAY dev pack: a Key Tester item + helmet that report which client inputs reach the server (Primary, Secondary, Ability1-3, Use, Pick, Dodge, swaps ...) with hold time and crouch / sprint / air state (/keyprobe, admin only). Pinned for one test session, then removed.", PKG + ".SkyyKeyProbePlugin")
B.assemble(jar, man, OUT, files)
