"""SkyyReelProbe 0.1 - build script (javassist via jpype). A THROWAWAY dev / test pack (like SkyyGatherProbe / SkyyUiProbe): it proves the
fishing ROD + REEL LOOK in game before the real fishing mod exists. Op-only command, pinned for ONE test session, then removed again.
Run:   python SkyyReelProbe/build_skyyreelprobe_0.1.py   -> SkyyReelProbe/SkyyReelProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyReelProbe/test_skyyreelprobe_0.1.py    (bare JVM, -Xverify:all, engine codecs, every code path executed)

SKYY'S WORDS (2026-10-07, docs/answered/skills.md + gear.md, research/Rod-Reel-Look.md):
  "regarding rods, how does swapping reels work with the item look? can we make it show a cobalt rod with an adamantine reel? or will
   we have to make an item for every combination?"  ->  "do the 8 rods with the reel stat"  ->  rod icon: "second row for the rod".
So: 8 rod items (one per rod tier), ONE new entity stat SkyyFishing_Reel (0 = no reel, 1..8 = reel tier) and, on every rod, 9
ItemAppearanceConditions entries on that stat (the engine swaps the held model / texture while the HOLDER's stat is in the range -
VERIFIED shape: vanilla Template_Glider.json on its own GlidingActive stat, Weapon_Axe_Iron.json on Health).

WHAT IS IN THE JAR
  Server/Entity/Stats/SkyyFishing_Reel.json   modelled on vanilla GlidingActive.json (read from Assets.zip at build time): InitialValue 0,
                                              Min 0, Max 8, Shared true (synced to OTHER players, like GlidingActive), IgnoreInvulnerability
                                              true (as GlidingActive), no Regenerating, no Min/MaxValueEffects, HideFromTooltip true
                                              (the vanilla MagicCharges "hidden" key).
  Server/Item/Items/SkyyReelProbe/SkyyFishing_Rod_<Tier>.json  x 8 (Bamboo, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium):
        no recipe (creative / probe only: Categories Items.Tools = the creative Tools tab, or /reelprobe give). HELD LOOK: the vanilla
        rod model (Common/Items/Tools/Fishing_Rod/FishingRod.blockymodel) has NO vanilla item JSON, so the hold fields come from the
        vanilla one-handed stick that is closest - Weapon_Wand_Wood (PlayerAnimationsId "Wand", DroppedItemAnimation, ItemSoundSetId,
        Quality); its Interactions / Weapon / Particles / Tags are NOT copied (a rod must not cast or count as a wand). MaxStack 1.
        Icon = the rod's own 3D render (make_fishing.reel_looks: the alt/ render, default reel); IconProperties = the shared rod view.
        Model / Texture = the rod model + its DEFAULT texture (the rod's own matching-tier reel; Bamboo = the vanilla reel), so a
        dropped rod, a rod in a chest and the icon show the default reel.
        ItemAppearanceConditions {"SkyyFishing_Reel": [ {"Condition": [K, K], "Model": ..., "Texture": ...} for K = 0..8 ]}
        (no ConditionValueType: the engine default is Absolute - ItemAppearanceCondition.<init> bytecode; GlidingActive uses none).
          K 0     = the rod model WITHOUT its Reel + Crank nodes (make_fishing.strip_reel) + the default texture  ("no reel")
          K 1..8  = the rod model + the texture with reel tier K painted on the Reel + Crank nodes (same UV, same size)
  Common/...  the models, textures and icons from tools/art/make_fishing.py reel_looks() - made at BUILD time from Assets.zip
              (vanilla-derived bytes go only into this jar, never into a tracked file). 84 files.
  Server/Languages/en-US/server.lang  the 8 rod names + descriptions.

THE COMMAND (op only: requirePermission skyyreelprobe.admin + no permission groups, like the other probes; alias /rprobe)
  /reelprobe          prints your SkyyFishing_Reel value, the rod in your hand, auto on / off, and the help lines
  /reelprobe give     gives all 8 rods (storage first; whatever does not fit is reported, never dropped)
  /reelprobe <0-8>    sets YOUR SkyyFishing_Reel stat (EntityStatMap.setStatValue on the index looked up by name - Crossbow-Loaded-
                      Spec 1.1 / 1.8) and turns auto off
  /reelprobe auto     toggles auto mode: on every hotbar change (InventorySetActiveSlotEvent, hotbar section) the stat is set for the
                      new item: rod tier N (Bamboo 1 .. Onyxium 8) -> reel (N mod 8) + 1 = the NEXT tier's reel (Bamboo rod -> Copper
                      reel ... Mithril rod -> Onyxium reel, Onyxium rod -> Bamboo reel), so scrolling shows a different reel on every
                      rod; anything else in hand -> 0. Memory only (per player, gone at restart).
Every chat line is also written to the server log as "[SkyyReelProbe] ...". Chat lines are plain vanilla-style sentences; changes in the
kit's success colour, refusals in the kit's error colour (tools/skyyui.py COLOR).
NO VANILLA / PACK-MOD ID OR PATH IS OVERRIDDEN: the harness checks Assets.zip and every installed mod (read-only) for a clash.

REMOVING THE PROBE (rollback): two things stay in saved data.
  1. the SkyyFishing_Reel stat value - the engine keeps it in EntityStatMap.unknown (harmless; harness D "removed").
  2. any SkyyFishing_Rod_* stack still in a hotbar / storage / backpack, a chest or a SkyyProfiles profile inventory. Harness D "removed"
     (real SimpleItemContainer codec): the stack is KEPT in its slot with its id and saved again; ItemStack.getItem() = Item.UNKNOWN
     server-side; ItemContainer.toProtocolMap still sends it to the client under its old id. What the CLIENT draws / lets you do with it
     is UNVERIFIED. Safest: hand the rods back (or /clear them) before the probe is removed. The way out either way: the real
     SkyyFishing reuses these exact item ids (SkyyFishing_Rod_<Tier>) and stat id, so a stray rod becomes a working rod again.
"""
import sys, os, json, zipfile, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "art"))
import skyybuild as B
import skyyui as SUI
import make_fishing as MF

if "--deploy" in sys.argv:
    raise SystemExit("SkyyReelProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyyreelprobe.admin"
STAT = "SkyyFishing_Reel"
STAT_PATH = "Server/Entity/Stats/%s.json" % STAT
ITEM_DIR = "Server/Item/Items/SkyyReelProbe"
LOOK_SRC = "Weapon_Wand_Wood"               # the vanilla one-handed stick whose hold fields the rods borrow (see the header)
HOLD_KEYS = ("PlayerAnimationsId", "DroppedItemAnimation", "ItemSoundSetId", "Quality")
TIERS = list(MF.TIERS)
assert TIERS == ["Bamboo", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"], TIERS
ROD_IDS = ["SkyyFishing_Rod_%s" % t for t in TIERS]
SUI.verify()
COL_OK, COL_ERR = SUI.COLOR["success"], SUI.COLOR["error"]

az = zipfile.ZipFile(ASSETS)
AZ_NAMES = set(az.namelist())
ITEM_PATH = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def vanilla_json(path):
    return json.loads(az.read(path).decode("utf-8-sig"))


# ================= the stat (GlidingActive's shape) =================
GLIDE = vanilla_json("Server/Entity/Stats/GlidingActive.json")
if [k for k in GLIDE] != ["InitialValue", "Min", "Max", "Shared", "IgnoreInvulnerability", "Regenerating", "MinValueEffects"]:
    raise SystemExit("GlidingActive.json changed shape: %s - re-check the SkyyFishing_Reel model" % list(GLIDE))
if not (GLIDE["InitialValue"] == 0 and GLIDE["Min"] == 0 and GLIDE["Shared"] is True and GLIDE["IgnoreInvulnerability"] is True):
    raise SystemExit("GlidingActive.json values changed: %r" % GLIDE)
if vanilla_json("Server/Entity/Stats/MagicCharges.json").get("HideFromTooltip") is not True:
    raise SystemExit("MagicCharges.json no longer carries HideFromTooltip - re-check the 'hidden' key")
stat = {}
for k in ("InitialValue", "Min", "Max", "Shared", "IgnoreInvulnerability"):     # GlidingActive's keys in GlidingActive's order
    stat[k] = GLIDE[k]
stat["Max"] = 8
stat["HideFromTooltip"] = True                                                   # "hidden" (vanilla MagicCharges)
STAT_TEXT = json.dumps(stat, indent=2) + "\n"

# ================= the art (built now, shipped only in the jar) =================
LOOKS = MF.reel_looks(az)
PROPS = LOOKS["icon_props"]
RODS = LOOKS["rods"]
assert [r["item"] for r in RODS] == ROD_IDS, [r["item"] for r in RODS]
files, lang = {}, []
for r in RODS:
    for p, b in sorted(r["files"].items()):
        if not p.startswith("Common/") or p in AZ_NAMES or p in files:
            raise SystemExit("art path %s is not a new Common/ path" % p)
        files[p] = b
    for lk in r["looks"]:
        for k in ("model", "texture"):
            if lk[k] not in files and lk[k] not in AZ_NAMES:
                raise SystemExit("%s look %d: %s %s is neither shipped nor in Assets.zip" % (r["item"], lk["reel"], k, lk[k]))


def rel(p):
    """item JSON paths are relative to Common/"""
    assert p.startswith("Common/"), p
    return p[len("Common/"):]


# ================= the 8 rod items =================
VLOOK = vanilla_json(ITEM_PATH[LOOK_SRC])
if VLOOK.get("PlayerAnimationsId") != "Wand" or "Parent" in VLOOK:
    raise SystemExit("%s changed (PlayerAnimationsId %r / Parent) - re-check the rod hold" % (LOOK_SRC, VLOOK.get("PlayerAnimationsId")))
HOLD = dict((k, VLOOK[k]) for k in HOLD_KEYS)
GLIDER = vanilla_json(ITEM_PATH["Template_Glider"])
_gc = GLIDER["ItemAppearanceConditions"]["GlidingActive"][0]
if sorted(_gc) != ["Condition", "Model", "Texture"] or _gc["Condition"] != [1, 1] or "ConditionValueType" in _gc:
    raise SystemExit("Template_Glider ItemAppearanceConditions changed: %r" % _gc)
if GLIDER.get("Categories") != ["Items.Tools"]:
    raise SystemExit("Template_Glider Categories changed: %r" % GLIDER.get("Categories"))


def name_lines(iid, name, desc):
    for pre in ("", "server."):
        lang.append("%sitems.%s.name=%s" % (pre, iid, name))
        lang.append("%sitems.%s.description=%s" % (pre, iid, desc))


ITEMS = {}
for r in RODS:
    iid, tier = r["item"], r["tier"]
    d = {"TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
         "Icon": rel(r["icon"]), "IconProperties": json.loads(json.dumps(PROPS)),
         "Model": rel(r["model"]), "Texture": rel(r["texture"])}
    d.update(HOLD)
    d["MaxStack"] = 1
    d["Categories"] = ["Items.Tools"]
    d["ItemAppearanceConditions"] = {STAT: [{"Condition": [lk["reel"], lk["reel"]], "Model": rel(lk["model"]), "Texture": rel(lk["texture"])}
                                            for lk in r["looks"]]}
    ITEMS[iid] = d
    files["%s/%s.json" % (ITEM_DIR, iid)] = json.dumps(d, indent=2)
    name_lines(iid, "%s Fishing Rod (reel probe)" % tier,
               "Reel look probe: the %s rod. /reelprobe 0-8 sets the reel you see on it (0 none, 1 Bamboo .. 8 Onyxium); /reelprobe auto "
               "puts the next tier's reel on every rod as you scroll. Throwaway test item." % tier)
files[STAT_PATH] = STAT_TEXT
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"

# ---- asset build checks
for p in files:
    if p in AZ_NAMES and not p.endswith("server.lang"):
        raise SystemExit("asset path %s exists in Assets.zip (override)" % p)
for iid in ROD_IDS:
    if iid in ITEM_PATH:
        raise SystemExit("rod id %s would override a vanilla id" % iid)
print("assets: %d rods x %d looks, stat %s, %d files (%d bytes of art), %d lang lines"
      % (len(ITEMS), len(RODS[0]["looks"]), STAT, len(files), sum(len(b) for p, b in files.items() if p.startswith("Common/")), len(lang)))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.reelprobe"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "STAT": STAT, "COLOK": COL_OK, "COLERR": COL_ERR,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "HOTB": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "EST": "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ISAS": "com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "getComponentType"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["PLA"], "getComponentType"),
             (T["INVC"], "getCombined"), (T["INVC"], "STORAGE_HOTBAR_BACKPACK"), (T["INVC"], "HOTBAR_SECTION_ID"),
             (T["HOTB"], "getComponentType"), (T["HOTB"], "getActiveItem"), (T["HOTB"], "getActiveSlot"), (T["IC"], "addItemStack"),
             (T["IS"], "getItemId"), (T["IS"], "isEmpty"), (T["IS"], "getQuantity"), (T["IST"], "succeeded"), (T["IST"], "getRemainder"),
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESM"], "setStatValue"), (T["ESV"], "get"), (T["ESV"], "getMax"),
             (T["EST"], "getAssetMap"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             (T["ISAS"], "getInventorySectionId"), (T["ISAS"], "getNewSlot"), (T["ISAS"], "getPreviousSlot"), (T["ACH"], "getReferenceTo"),
             (T["ST"], "getComponent"), (PB, "getCommandRegistry"), (PB, "getEntityStoreRegistry"), (PB, "getLogger"), (PB, "shutdown")):
    B.probe(pool, c, m)

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


def jarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs)


# ---- RpLog: server log + chat. SINK (harness hook, null in game) also receives every chat line as "<colour>|<text>".
log = mk("RpLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List SINK;")
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyReelProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyReelProbe] " + msg); } catch (Throwable t) { }
}""")
# col = null -> the vanilla default chat colour
M(log, r"""
public static void tell(@PR@ pr, String s, String col) {
  info((pr == null ? "" : "to " + pr.getUsername() + ": ") + s);
  try { if (SINK != null) SINK.add((col == null ? "" : col) + "|" + s); } catch (Throwable t) { }
  try {
    if (pr != null) {
      @MSG@ m = @MSG@.raw(s);
      if (col != null) m = m.color(col);
      pr.sendMessage(m);
    }
  } catch (Throwable t) { }
}""")

# ---- RpLogic: pure functions (no engine objects) - the harness calls them directly
lg = mk("RpLogic")
F(lg, "public static final String[] TIERS = %s;" % jarr(TIERS))
F(lg, "public static final String[] RODS = %s;" % jarr(ROD_IDS))
M(lg, r"""
public static int rodIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < RODS.length; i++) if (RODS[i].equals(id)) return i;
  return -1;
}""")
# auto mode: rod tier N (Bamboo 1 .. Onyxium 8) -> reel (N mod 8) + 1 = the next tier's reel; not a rod -> 0
M(lg, r"""
public static int autoReel(int idx) {
  if (idx < 0 || idx >= RODS.length) return 0;
  int n = idx + 1;
  return (n % 8) + 1;
}""")
# "0".."8" -> 0..8, anything else -1
M(lg, r"""
public static int parseReel(String s) {
  if (s == null) return -1;
  String t = s.trim();
  if (t.length() != 1) return -1;
  char c = t.charAt(0);
  if (c < '0' || c > '8') return -1;
  return c - '0';
}""")
M(lg, r"""
public static String reelName(int k) {
  if (k == 0) return "no reel";
  if (k >= 1 && k <= TIERS.length) return TIERS[k - 1] + " reel";
  return "reel " + k;
}""")
M(lg, r"""
public static String rodName(int idx) {
  if (idx < 0 || idx >= TIERS.length) return null;
  return TIERS[idx] + " Fishing Rod";
}""")
M(lg, r"""
public static int toReel(float v) {
  if (v != v) return -1;
  return Math.round(v);
}""")
M(lg, r"""
public static String heldText(String id) {
  if (id == null) return "nothing";
  int i = rodIndex(id);
  return i >= 0 ? "the " + rodName(i) : id + " (not a probe rod)";
}""")

# ---- RpStat: the SkyyFishing_Reel stat on one entity (world thread)
sta = mk("RpStat")
F(sta, "public static final String NAME = \"@STAT@\";")
# the stat index by name; < 0 = the stat asset is not loaded (IndexedLookupTableAssetMap.getIndex answers its missing-key default;
# EntityStatMap.get(int) only range-checks the top, so a negative index must never reach it)
M(sta, r"""
public static int index() {
  try { return @EST@.getAssetMap().getIndex(NAME); } catch (Throwable t) { return -1; }
}""")
M(sta, r"""
public static @ESM@ map(@ST@ st, @REF@ ref) {
  try { return (@ESM@) st.getComponent(ref, @ESM@.getComponentType()); } catch (Throwable t) { return null; }
}""")
M(sta, r"""
public static @ESV@ value(@ESM@ m) {
  int i = index();
  if (m == null || i < 0) return null;
  try { return m.get(i); } catch (Throwable t) { return null; }
}""")
# the current reel 0..8, -1 = no stat (not loaded / no stat map)
M(sta, r"""
public static int get(@ESM@ m) {
  @ESV@ v = value(m);
  if (v == null) return -1;
  return @PKG@.RpLogic.toReel(v.get());
}""")
# set the reel (clamped 0..8 here AND by the engine's [Min, Max]); answers the value read back, -1 = failed
M(sta, r"""
public static int set(@ESM@ m, int k) {
  if (k < 0) k = 0;
  if (k > 8) k = 8;
  @ESV@ v = value(m);
  if (v == null) return -1;
  try { m.setStatValue(index(), (float) k); } catch (Throwable t) { @PKG@.RpLog.warn("setStatValue failed: " + t); return -1; }
  return @PKG@.RpLogic.toReel(v.get());
}""")
M(sta, r"""
public static String heldId(@ST@ st, @REF@ ref) {
  try {
    @HOTB@ hb = (@HOTB@) st.getComponent(ref, @HOTB@.getComponentType());
    @IS@ it = hb == null ? null : hb.getActiveItem();
    if (it == null || it.isEmpty()) return null;
    return it.getItemId();
  } catch (Throwable t) { return null; }
}""")

# ---- RpCmds: what each command does (world thread: AbstractPlayerCommand.execute / the hotbar event)
cmds = mk("RpCmds")
F(cmds, "public static final java.util.concurrent.ConcurrentHashMap AUTO = new java.util.concurrent.ConcurrentHashMap();")
F(cmds, "public static final String OK = \"@COLOK@\";")
F(cmds, "public static final String ERR = \"@COLERR@\";")
M(cmds, r"""
public static boolean autoOn(java.util.UUID u) { return u != null && AUTO.get(u) != null; }""")
M(cmds, r"""
public static void help(@PR@ pr) {
  @PKG@.RpLog.tell(pr, "Reel look probe (op only):", null);
  @PKG@.RpLog.tell(pr, "/reelprobe give - get all 8 test rods", null);
  @PKG@.RpLog.tell(pr, "/reelprobe 0-8 - show that reel on the rod in your hand: 0 none, 1 Bamboo, 2 Copper, 3 Iron, 4 Thorium, 5 Cobalt, 6 Adamantite, 7 Mithril, 8 Onyxium", null);
  @PKG@.RpLog.tell(pr, "/reelprobe auto - turn auto mode on or off: every rod you scroll to gets the next tier's reel", null);
}""")
M(cmds, r"""
public static void status(@PR@ pr, @ST@ st, @REF@ ref) {
  int k = @PKG@.RpStat.get(@PKG@.RpStat.map(st, ref));
  String held = @PKG@.RpLogic.heldText(@PKG@.RpStat.heldId(st, ref));
  if (k < 0) { @PKG@.RpLog.tell(pr, "The SkyyFishing_Reel stat is not loaded on this server - is the SkyyReelProbe asset pack enabled?", ERR); return; }
  @PKG@.RpLog.tell(pr, "Reel look: " + k + " (" + @PKG@.RpLogic.reelName(k) + "). Auto mode: " + (autoOn(pr.getUuid()) ? "on" : "off") + ". In your hand: " + held + ".", null);
}""")
M(cmds, r"""
public static void give(@PR@ pr, @ST@ st, @REF@ ref) {
  @IC@ dst = null;
  try { dst = @INVC@.getCombined(st, ref, @INVC@.STORAGE_HOTBAR_BACKPACK); } catch (Throwable t) { dst = null; }
  if (dst == null) { @PKG@.RpLog.tell(pr, "Could not open your inventory.", ERR); return; }
  int got = 0;
  StringBuilder lost = new StringBuilder();
  for (int i = 0; i < @PKG@.RpLogic.RODS.length; i++) {
    String id = @PKG@.RpLogic.RODS[i];
    boolean ok = false;
    try {
      @IST@ tx = dst.addItemStack(new @IS@(id, 1));
      @IS@ rem = tx == null ? null : tx.getRemainder();
      ok = tx != null && tx.succeeded() && (rem == null || rem.isEmpty());
    } catch (Throwable t) { @PKG@.RpLog.warn("give " + id + " failed: " + t); ok = false; }
    if (ok) got++;
    else lost.append(lost.length() == 0 ? "" : ", ").append(@PKG@.RpLogic.TIERS[i]);
  }
  if (got > 0) @PKG@.RpLog.tell(pr, "You got " + got + " fishing " + (got == 1 ? "rod" : "rods") + ".", OK);
  if (lost.length() > 0) @PKG@.RpLog.tell(pr, "No room for the " + lost.toString() + " " + (got == 7 ? "rod" : "rods") + " - nothing was dropped. Free some space and use /reelprobe give again.", ERR);
}""")
M(cmds, r"""
public static void setReel(@PR@ pr, @ST@ st, @REF@ ref, int k) {
  boolean wasAuto = pr != null && AUTO.remove(pr.getUuid()) != null;
  int now = @PKG@.RpStat.set(@PKG@.RpStat.map(st, ref), k);
  if (now < 0) { @PKG@.RpLog.tell(pr, "Could not set the reel look - the SkyyFishing_Reel stat is not loaded.", ERR); return; }
  String held = @PKG@.RpStat.heldId(st, ref);
  int ri = @PKG@.RpLogic.rodIndex(held);
  String where = ri >= 0 ? "Your " + @PKG@.RpLogic.rodName(ri) + " now shows " : "Any probe rod you hold now shows ";
  @PKG@.RpLog.tell(pr, where + (now == 0 ? "no reel" : "the " + @PKG@.RpLogic.reelName(now)) + " (reel look " + now + ")." + (wasAuto ? " Auto mode is off." : ""), OK);
}""")
# apply auto mode to the item now in hand: answers the reel set, -1 = no stat; tells only when it changes
M(cmds, r"""
public static int applyAuto(@PR@ pr, @ST@ st, @REF@ ref, String held, boolean always) {
  @ESM@ m = @PKG@.RpStat.map(st, ref);
  int before = @PKG@.RpStat.get(m);
  if (before < 0) return -1;
  int ri = @PKG@.RpLogic.rodIndex(held);
  int k = @PKG@.RpLogic.autoReel(ri);
  int now = before;
  if (before != k) now = @PKG@.RpStat.set(m, k);
  if (ri >= 0 && (always || now != before)) @PKG@.RpLog.tell(pr, "Auto: your " + @PKG@.RpLogic.rodName(ri) + " shows the " + @PKG@.RpLogic.reelName(now) + " (reel look " + now + ").", null);
  return now;
}""")
M(cmds, r"""
public static void toggleAuto(@PR@ pr, @ST@ st, @REF@ ref) {
  java.util.UUID u = pr.getUuid();
  if (AUTO.remove(u) != null) {
    @PKG@.RpLog.tell(pr, "Auto mode is off. Your reel look stays where it is - /reelprobe 0-8 sets it.", OK);
    return;
  }
  AUTO.put(u, Boolean.TRUE);
  @PKG@.RpLog.tell(pr, "Auto mode is on: scroll through your rods - each one shows the next tier's reel (Bamboo rod: Copper reel ... Onyxium rod: Bamboo reel).", OK);
  if (applyAuto(pr, st, ref, @PKG@.RpStat.heldId(st, ref), true) < 0)
    @PKG@.RpLog.tell(pr, "The SkyyFishing_Reel stat is not loaded on this server - auto mode cannot change anything.", ERR);
}""")
# one entry point for /reelprobe <what>
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, String what) {
  String t = what == null ? "" : what.trim().toLowerCase(java.util.Locale.ROOT);
  @PKG@.RpLog.info(pr.getUsername() + " ran /reelprobe " + t);
  if (t.equals("give")) { give(pr, st, ref); return; }
  if (t.equals("auto")) { toggleAuto(pr, st, ref); return; }
  int k = @PKG@.RpLogic.parseReel(t);
  if (k >= 0) { setReel(pr, st, ref, k); return; }
  @PKG@.RpLog.tell(pr, "Unknown option '" + (what == null ? "" : what.trim()) + "'.", ERR);
  help(pr);
}""")

# ---- RpSlotSys: auto mode on a hotbar change (InventorySetActiveSlotEvent, hotbar section only; fired inside setActiveSlot after the
# active slot was written - Crossbow-Loaded-Spec 1.3 - so getActiveItem() is already the NEW item). World thread.
sys_ = mk("RpSlotSys", T["EES"])
F(sys_, "public static boolean FAILED_ONCE = false;")
C(sys_, "public RpSlotSys() { super(@ISAS@.class); }")
M(sys_, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(sys_, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    @ISAS@ e = (@ISAS@) ev;
    if (e.getInventorySectionId() != @INVC@.HOTBAR_SECTION_ID) return;
    if (@PKG@.RpCmds.AUTO.isEmpty()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null || !@PKG@.RpCmds.autoOn(pr.getUuid())) return;
    @PKG@.RpCmds.applyAuto(pr, st, r, @PKG@.RpStat.heldId(st, r), false);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.RpLog.warn("hotbar hook failed (logged once): " + t); }
  }
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# ---- /reelprobe <what>  (admin: requirePermission + no permission groups)
cmd1 = mk("ReelProbeArgCmd", T["APC"])
F(cmd1, "public @RA@ whatArg;")
C(cmd1, r"""
public ReelProbeArgCmd() {
  super("(admin) /reelprobe <give, auto, 0-8>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("option", "give, auto, or a reel look 0-8 (0 none, 1 Bamboo .. 8 Onyxium)", @ATY@.STRING);
}""")
M(cmd1, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); }
  catch (Throwable t) { @PKG@.RpLog.tell(pr, "Usage: /reelprobe <give, auto, 0-8>", @PKG@.RpCmds.ERR); return; }
  @PKG@.RpCmds.run(ref, store, pr, a);
}""")
# ---- /reelprobe (alias /rprobe): status + help
cmd = mk("ReelProbeCmd", T["APC"])
C(cmd, r"""
public ReelProbeCmd() {
  super("reelprobe", "(admin) Fishing rod reel look probe (throwaway dev pack): /reelprobe shows your reel look and the options");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "rprobe" });
  addUsageVariant(new @PKG@.ReelProbeArgCmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.RpLog.info(pr.getUsername() + " ran /reelprobe");
  @PKG@.RpCmds.status(pr, store, ref);
  @PKG@.RpCmds.help(pr);
}""")

# ---- the plugin
pl = mk("SkyyReelProbePlugin", T["JP"])
C(pl, "public SkyyReelProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.RpLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.ReelProbeCmd());
  getEntityStoreRegistry().registerSystem(new @PKG@.RpSlotSys());
  int i = @PKG@.RpStat.index();
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyReelProbe] @VERSION@ ready - /reelprobe (admin): 8 rods + the @STAT@ look stat (index " + i + ", throwaway dev pack, remove after the test session)");
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.RpCmds.AUTO.clear();
  super.shutdown();
}""")

ALL = [log, lg, sta, cmds, sys_, cmd1, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "SkyyReelProbe-%s.jar" % VERSION)
man = B.manifest("SkyyReelProbe", VERSION, "SkyWynn THROWAWAY dev pack: the 8 fishing rods + the SkyyFishing_Reel look stat (/reelprobe, admin only) - proves the rod + reel look in game. Pinned for one test session, then removed.", PKG + ".SkyyReelProbePlugin")
B.assemble(jar, man, OUT, files)
