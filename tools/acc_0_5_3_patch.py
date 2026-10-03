"""Derive SkyyAccessories/build_skyyaccessories_0.5.3.py from the GENERATED 0.5.2 script (build_skyyaccessories_0.5.2.py = the
tools/deploy_set.py SET pin, itself written by tools/acc_0_5_2_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.2 script
stays untouched - never re-run acc_0_5_2_patch.py on top of this).
Run:  python tools/acc_0_5_3_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.3.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.3.py   (every 0.5.2 check + N the Night Vision accessory + Y compare with 0.5.2)

0.5.3 = ONE CHANGE: THE NIGHT VISION ACCESSORY. Skyy 2026-10-02, verbatim: "add a night vision accessory if you can."
(OPEN-QUESTIONS 'ASKED 2026-10-02': its own line so it stacks with the boosters, admin give like the other boosters, only on while it sits in
the Accessory Bag, off at once when removed, a Server Setup switch.)

WHAT PLAYERS GET
 - ONE item, Skyy_Talisman_NightVision_Rare, "Night Vision Accessory", Rare (the Skyy_Acc_Rare quality every Rare accessory uses), the look
   of the vanilla Lightning Essence (model, texture and icon copied from Assets.zip at build time; no other accessory uses it). No recipe:
   admin give only, like the other new lines (/accessories give <player> Skyy_Talisman_NightVision_Rare, /accessories givetier <player>
   NightVision Rare, acc:fn:give). Vanilla-style tooltip: "Night Vision - see in the dark while in your Accessory Bag."
 - ITS OWN LINE: it stacks with every booster line, the bench accessories and the Omni (one copy per bag: a second one is refused like a
   same-rarity booster). The bag page lists it as a "Night Vision" row under the booster lines; /accessories lines lists it (Rare only);
   acc:defs carries one record for it.
 - While it sits in the player's Accessory Bag (the ACTIVE profile's bag), that player - and nobody else - gets a light on their own
   character: it brightens the night and dark caves. Out of the bag (unequip, profile switch, switched off) the light is taken back on the
   next world tick after the bag changes (at the latest within a second); on logout / world change the client drops the entity anyway.

HOW (engine proof: _nv_engine_proof below stops this build when any of these HytaleServer.jar facts changes; research by the night
vision research workflow wf_4726d526-aa2, every fact re-read in bytecode for this build)
 - A DynamicLightUpdate(ColorLight radius, red, green, blue) queued on the player's OWN EntityTrackerSystems$EntityViewer for the player's
   OWN entity: EntityViewer.queueUpdate(ref, update) / queueRemove(ref, ComponentUpdateType.DynamicLight). Only that viewer's client gets
   it (the engine's own DynamicLightTracker sends a lit entity's light the same way, to each viewer in Visible.visibleTo). No component is
   added to the player: nothing is saved, other players never see it, and mods that add or strip DynamicLight components are not touched.
   Two published Night Vision mods for Hytale 0.6.x (NotEnoughPotions 2.3.0, SimpleEnchantments 1.2.0) send exactly this
   ColorLight(-1, 1, 1, 1) - the default here (radius 255, a wide, faint, even glow). Read-only, ideas only.
 - WHERE IT RUNS: its own EntityTickingSystem AccNightVision in EntityTrackerSystems.QUEUE_UPDATE_GROUP - the group the engine's own
   update queuers use. queueUpdate throws "Entity is not visible!" unless the target is in the viewer's visible set, and that set is
   cleared and rebuilt every tick (ClearEntityViewers -> FIND_VISIBLE_ENTITIES_GROUP -> ClearPreviouslyVisible -> EnsureVisibleComponent ->
   AddToVisible -> RemoveEmptyVisibleComponent [BEFORE QUEUE_UPDATE_GROUP] -> QUEUE_UPDATE_GROUP -> SendPackets [AFTER QUEUE_UPDATE_GROUP]).
   A system with no group (AccEffects) lands ANYWHERE in that order (the engine's DependencyGraph, run on the real tracker systems in the
   harness: a group-less system came out first, between and last in different shuffles), so queuing from AccEffects could fail every
   second for good; in the update group the set is complete and the update leaves in the same tick's SendPackets. One registerSystem per
   class: AccEffects and AccNightVision are two classes. isParallel is not overridden (EntityTickingSystem returns false): it runs on
   the world thread, one player after another.
 - WHEN IT SENDS (AccNv.step, the logic; AccNightVision.tick only reads the engine components): a decision once a second per player, at
   once after a bag change (AccStore.publish sets AccStore.NVPOKE: equip / unequip / profile switch / join) and at once when the client
   re-creates the player's entity (the player in their own Visible.newlyVisibleTo - join, world change; the engine's own trackers re-send
   component state on exactly that). Sent: when the light is on a different entity than last time, when the light settings changed, after
   the client re-created the entity, and every nightVision.refreshSeconds (10) as a safety net. Taken back (queueRemove) only from the
   entity it was sent to. Never while the client is still loading (Player.isWaitingForClientReady), never while ANOTHER light owns the
   player (a real DynamicLight component - the engine already sends that one to every viewer, the player too: no fighting; when it goes,
   ours comes back within a second). A failed send ("Entity is not visible!") is retried at the next check.
 - State: AccNv.SENT (uuid -> the entity our light is on), SKEY (the light sent), CLK (seconds since the check / the send) - pruned by
   AccTick for players who left, cleared on shutdown. Nothing on disk, nothing on the bridge.

SERVER SETUP (new category "Night Vision", the config kit tools/skyycfg.py; all live): line.NightVision (on), nightVision.radius /
red / green / blue (255 / 1 / 1 / 1, each 0-255), nightVision.refreshSeconds (10, 0-300, Advanced). A fresh config.properties carries them;
an existing file is NOT rewritten (no migration: a missing key means its default; the kit adds the line when it is changed in game) - so
deploying 0.5.3 changes no file of a running server.

UNCHANGED: every booster line, number, id, rule and migration; the bag page markup; AccEffects, AccGear, MoveSync; the Workbench tab
(the item has no recipe, so tools/skyywbtab.py and its call site are untouched).
UNVERIFIED (in game only): how bright / wide 255,1,1,1 looks on screen (the client turns radius + channels into a point light - not
readable here; the rows let Skyy tune it without a build); whether the client keeps the light through death / respawn on the same
entity (the 10 s refresh covers it).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.2.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.3.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.2"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.2"\n' in s and "skyywbtab" in s and "NightVision" not in s, "the source must be the generated 0.5.2 script"
REG0 = s.count("registerCommand(")
assert s.count("registerSystem(") == 1

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyAccessories 0.5.2 - build script (derived from the generated build_skyyaccessories_0.5.1.py by tools/acc_0_5_2_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.2.py            -> SkyyAccessories/SkyyAccessories-0.5.2.jar
       python build_skyyaccessories_0.5.2.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.2.py             (bare JVM -Xverify:all: every 0.5.1 check + the Workbench tab + compare with 0.5.1)
''', '''"""SkyyAccessories 0.5.3 - build script (derived from the generated build_skyyaccessories_0.5.2.py by tools/acc_0_5_3_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.3.py            -> SkyyAccessories/SkyyAccessories-0.5.3.jar
       python build_skyyaccessories_0.5.3.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.3.py             (bare JVM -Xverify:all: every 0.5.2 check + Night Vision + compare with 0.5.2)
0.5.3: THE NIGHT VISION ACCESSORY (Skyy 2026-10-02: "add a night vision accessory if you can."; full notes and the engine proof in
     tools/acc_0_5_3_patch.py): one item, Skyy_Talisman_NightVision_Rare ("Night Vision Accessory", Rare, admin give only, its own line
     so it stacks with every booster). While it sits in the Accessory Bag, its wearer - and nobody else - gets a light on their own
     character: a DynamicLightUpdate queued on the player's OWN entity viewer (no component, nothing saved), sent by the new system
     AccNightVision in the entity tracker's update group (EntityTrackerSystems.QUEUE_UPDATE_GROUP, after the visible sets are built and
     before SendPackets), decided once a second and at once after a bag change or when the client re-creates the player's entity;
     taken back from that entity when it leaves the bag. Server Setup -> Accessories -> Night Vision: on / off, the light (radius,
     red, green, blue; 255,1,1,1) and a safety re-send (10 s). Existing config files are not rewritten (missing keys = defaults).
''')
rep('VERSION = "0.5.2"\n', 'VERSION = "0.5.3"\n')

# ---------------------------------------------------------------------------------------------------------------- the classes
rep('''gear = pool.makeClass(PKG + ".AccGear")                          # 0.5 part 2: gear:extra publisher, bag page notes, bridge clean-up
''', '''gear = pool.makeClass(PKG + ".AccGear")                          # 0.5 part 2: gear:extra publisher, bag page notes, bridge clean-up
nv   = pool.makeClass(PKG + ".AccNv")                            # 0.5.3: Night Vision - the wearer-only light (state + logic)
nvs  = pool.makeClass(PKG + ".AccNightVision", pool.get(ETS))    # 0.5.3: Night Vision - its system in the entity tracker's update group
''')

# ---------------------------------------------------------------------------------------------------------------- engine probes + proof
rep('''

_variant_proof()
''', r'''

_variant_proof()

# 0.5.3 NIGHT VISION - the engine members the light uses (every one B.probe'd) and the order / visibility facts it relies on
# (_nv_engine_proof reads them in HytaleServer.jar bytecode and stops the build when one changed; tools/acc_0_5_3_patch.py has the notes)
EVW = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$EntityViewer"
VSB = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$Visible"
ETR = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems"
DLC = "com.hypixel.hytale.server.core.modules.entity.component.DynamicLight"
DLU = "com.hypixel.hytale.protocol.DynamicLightUpdate"
CLT = "com.hypixel.hytale.protocol.ColorLight"
CUT = "com.hypixel.hytale.protocol.ComponentUpdateType"
SGR = "com.hypixel.hytale.component.SystemGroup"
ISY = "com.hypixel.hytale.component.system.ISystem"
for c, m in ((EVW, "queueUpdate"), (EVW, "queueRemove"), (EVW, "getComponentType"), (EVW, "visible"), (VSB, "newlyVisibleTo"),
             (VSB, "getComponentType"), (DLC, "getComponentType"), (DLU, "dynamicLight"), (CLT, "radius"), (CLT, "red"), (CLT, "green"),
             (CLT, "blue"), (CUT, "DynamicLight"), (ETR, "QUEUE_UPDATE_GROUP"), (ISY, "getGroup"), (PLA, "isWaitingForClientReady"),
             (PR, "getUuid"), (ST, "getComponent"), (ACH, "getReferenceTo")):
    B.probe(pool, c, m)
_NVT = {"EVW": EVW, "VSB": VSB, "ETR": ETR, "DLC": DLC, "DLU": DLU, "CLT": CLT, "CUT": CUT, "SGR": SGR}


def NVJ(src):
    """0.5.3: the Night Vision class tokens (@EVW@ ...); JT() resolves the others"""
    for _k, _v in _NVT.items():
        src = src.replace("@%s@" % _k, _v)
    return src


def _nv_engine_proof():
    """0.5.3: the HytaleServer.jar facts the Night Vision light relies on (read in bytecode - a changed engine stops this build)"""
    import jpype as _jp
    IPc, PSc, BOSc = _jp.JClass("javassist.bytecode.InstructionPrinter"), _jp.JClass("java.io.PrintStream"), _jp.JClass("java.io.ByteArrayOutputStream")

    def code(cls, name):
        cc = pool.get(cls)
        out = ""
        ms = [x for x in cc.getDeclaredMethods() if str(x.getName()) == name]
        if name == "<clinit>" and cc.getClassInitializer() is not None:
            ms = [cc.getClassInitializer().toMethod("clinit_", cc)]
        for mm in ms:
            bos = BOSc()
            IPc(PSc(bos)).print_(mm)
            out += str(bos.toString())
        if not out:
            raise SystemExit("0.5.3: %s.%s is gone - re-check Night Vision (tools/acc_0_5_3_patch.py)" % (cls, name))
        return out

    def need(cond, what):
        if not cond:
            raise SystemExit("0.5.3: the engine changed - %s; re-check Night Vision (tools/acc_0_5_3_patch.py)" % what)
    T = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$"
    qu = code(EVW, "queueUpdate")
    need("java.util.Set.contains" in qu and '"Entity is not visible!"' in qu and "EntityUpdate.queueUpdate(" in qu,
         "EntityViewer.queueUpdate no longer checks the visible set and queues the update")
    qr = code(EVW, "queueRemove")
    need("java.util.Set.contains" in qr and '"Entity is not visible!"' in qr and "EntityUpdate.queueRemove(" in qr,
         "EntityViewer.queueRemove no longer checks the visible set and queues the removal")
    rv = code(T + "RemoveEmptyVisibleComponent", "<clinit>")
    need("Order.AFTER" in rv and "EntityTrackerSystems$AddToVisible" in rv and "Order.BEFORE" in rv and "QUEUE_UPDATE_GROUP" in rv,
         "RemoveEmptyVisibleComponent is no longer AFTER AddToVisible and BEFORE the update group")
    sp = code(T + "SendPackets", "<clinit>")
    need("Order.AFTER" in sp and "QUEUE_UPDATE_GROUP" in sp, "SendPackets no longer runs AFTER the update group")
    cl = code(T + "ClearPreviouslyVisible", "tick")
    need("Visible.newlyVisibleTo" in cl and "java.util.Map.clear" in cl, "ClearPreviouslyVisible no longer clears newlyVisibleTo every tick")
    av = code(VSB, "addViewerParallel")
    need("Visible.previousVisibleTo" in av and "Visible.newlyVisibleTo" in av and "java.util.Map.containsKey" in av,
         "Visible.addViewerParallel no longer marks a viewer that did not see the entity last tick as newly visible")
    at = code(T + "AddToVisible", "tick")
    need("Visible.addViewerParallel(" in at and "EntityViewer.visible" in at, "AddToVisible no longer adds each viewer to what it sees")
    ip = code("com.hypixel.hytale.component.system.tick.EntityTickingSystem", "isParallel")
    need(ip.split("\n")[0].strip().endswith("iconst_0"), "EntityTickingSystem.isParallel is no longer false by default")
    dt = code("com.hypixel.hytale.server.core.modules.entity.system.EntitySystems$DynamicLightTracker", "queueUpdatesFor")
    need("DynamicLightUpdate.<init>((Lcom/hypixel/hytale/protocol/ColorLight;)V)" in dt and "EntityViewer.queueUpdate(" in dt,
         "the engine's own DynamicLightTracker no longer queues a DynamicLightUpdate(ColorLight) on each viewer")
    for cn in (DLU, CLT):
        f = pool.get(cn).getField("FIXED_BLOCK_SIZE")
        need(int(f.getConstantValue()) == 4, "%s is no longer 4 bytes" % cn)
    print("night vision: engine facts read - queueUpdate / queueRemove need the target in the viewer's visible set, the update group runs "
          "after AddToVisible (RemoveEmptyVisibleComponent) and before SendPackets, newlyVisibleTo is rebuilt every tick, ticking systems "
          "are sequential by default, DynamicLightUpdate = 4 bytes")


_nv_engine_proof()
''')

# ---------------------------------------------------------------------------------------------------------------- the Night Vision table
rep('''OMNI = "Skyy_Accessory_Omni"   # 0.4: counts as every bench accessory at max tier (own group "Omni"); 0.5: Legendary (crafted, never Mythic)
''', r'''OMNI = "Skyy_Accessory_Omni"   # 0.4: counts as every bench accessory at max tier (own group "Omni"); 0.5: Legendary (crafted, never Mythic)
# ---- 0.5.3 NIGHT VISION (tools/acc_0_5_3_patch.py): ONE item of its own line, Rare, admin give only (no recipe). Not a booster-table row
# (those have four rarities and a number per rarity): it gives no stat, it switches a light on. The id is a stat accessory id
# (Skyy_Talisman_<Key>_<Word>), so every bench path (acc:has, the Omni, SkyySacks' /craft tabs) leaves it alone, and the stat rules give
# it the rarity of its word: tierOf 3 = Rare, groupOf "T:NightVision" (one copy per bag), bestTiers skips it (no booster line).
NV_ID = "Skyy_Talisman_NightVision_Rare"
NV_ADMIN = "NightVision"                    # config / commands / acc:defs (/accessories givetier <player> NightVision Rare)
NV_LINE = "Night Vision"                    # what players see: "Night Vision Accessory", the bag page row "Night Vision"
NV_TIER = 3                                 # Rare (Skyy's task: Rare unless the research suggests tiers - it does not: one light, on or off)
NV_LOOK = "Ingredient_Lightning_Essence"    # the vanilla item whose model, texture and icon it copies (no other accessory looks like it)
NV_SRC = "Chest"                            # acc:defs source word (a placeholder for the later loot pass, like the other admin-give lines)
NV_SWITCH = "line.NightVision"              # the server-wide switch (the other lines' line.<Admin> pattern), AccDefs.LINE_NIGHTVISION
NV_FIELDS = ["NV_RADIUS", "NV_RED", "NV_GREEN", "NV_BLUE", "NV_REFRESH"]          # AccDefs fields (the kit's field: rows)
NV_KEYS = ["nightVision.radius", "nightVision.red", "nightVision.green", "nightVision.blue", "nightVision.refreshSeconds"]
NV_DEF = [255, 1, 1, 1, 10]                 # ColorLight(radius, red, green, blue) = the shipped Night Vision mods' (-1, 1, 1, 1); re-send s
NV_MAX = [255, 255, 255, 255, 300]
NV_ON_TEXT = "you see in the dark - only you see the light"      # the bag page row while it counts
NV_LINES_TEXT = "see in the dark while it sits in your Accessory Bag - only you see the light"   # /accessories lines
NV_FLAVOUR = "Your eyes adjust far faster than they should."
# the default file's Night Vision part (a fresh install; an existing file is never rewritten - a missing key = its default). No '=' or
# key-colon in the comments: the config kit uncomments '#key=value' template lines.
NV_CONFIG_LINES = [
    "# Night Vision Accessory (0.5.3): while it sits in a player's Accessory Bag, that player - and nobody else - gets a light on",
    "# their own character that brightens the night and dark caves. Set line.NightVision to false to switch it off for everyone.",
    "# The light is radius, red, green and blue, each 0-255 (%d,%d,%d,%d is a wide, faint, even glow; a much brighter try is 15,255,255,255)."
    % tuple(NV_DEF[:4]),
    "# nightVision.refreshSeconds is how often the light is sent again as a safety net, 0-300 seconds (0 means only when needed).",
    "%s=true" % NV_SWITCH] + ["%s=%d" % kv for kv in zip(NV_KEYS, NV_DEF)]
# the Server Setup rows (category "nightvision"; tools/CONFIG-CONTRACT.md row tuple)
NV_ROWS = [
    (NV_SWITCH, "Night Vision", "nightvision", "bool", "true", "", "", "", "", "live",
     "Off = the Night Vision Accessory does nothing for anyone; lights go out within a second.",
     "field:AccDefs.LINE_NIGHTVISION@config.properties:%s" % NV_SWITCH),
    (NV_KEYS[0], "Light radius", "nightvision", "int", str(NV_DEF[0]), "0", str(NV_MAX[0]), "step=1", "", "live",
     "How far the light reaches, 0-255. 255 = a wide, even glow. Only its wearer sees it.",
     "field:AccDefs.NV_RADIUS@config.properties:%s" % NV_KEYS[0]),
    (NV_KEYS[1], "Light red", "nightvision", "int", str(NV_DEF[1]), "0", str(NV_MAX[1]), "step=1", "", "live",
     "Red part of the light, 0-255. 1 = faint; 15 and up = much brighter (try 15,255,255,255).",
     "field:AccDefs.NV_RED@config.properties:%s" % NV_KEYS[1]),
    (NV_KEYS[2], "Light green", "nightvision", "int", str(NV_DEF[2]), "0", str(NV_MAX[2]), "step=1", "", "live",
     "Green part of the light, 0-255.", "field:AccDefs.NV_GREEN@config.properties:%s" % NV_KEYS[2]),
    (NV_KEYS[3], "Light blue", "nightvision", "int", str(NV_DEF[3]), "0", str(NV_MAX[3]), "step=1", "", "live",
     "Blue part of the light, 0-255.", "field:AccDefs.NV_BLUE@config.properties:%s" % NV_KEYS[3]),
    (NV_KEYS[4], "Send the light again every", "nightvision", "int", str(NV_DEF[4]), "0", str(NV_MAX[4]), "step=1", "s", "live,adv",
     "A safety net if the light ever drops. 0 = only when needed (join, world change, new light).",
     "field:AccDefs.NV_REFRESH@config.properties:%s" % NV_KEYS[4]),
]
assert len(NV_FIELDS) == len(NV_KEYS) == len(NV_DEF) == len(NV_MAX) == 5 and all(0 <= _d <= _m for _d, _m in zip(NV_DEF, NV_MAX))
assert all(ord(_c) < 128 for _t in NV_CONFIG_LINES + [NV_ON_TEXT, NV_LINES_TEXT, NV_FLAVOUR] for _c in _t)
assert not any("=" in _l for _l in NV_CONFIG_LINES if _l.startswith("#")), "no template-looking comment lines"
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in NV_ROWS), [_r[0] for _r in NV_ROWS]
''')

# the Python id mirror agrees: tier 3 (Rare), family NightVision, never a legacy id, no booster line, no bench id. Placed right AFTER the
# booster table block (the 0.5.x harnesses exec that block on its own, without the Night Vision names)
rep('''# ---- 0.5 CONFIG (the defaults file = the kit's DEFAULTS; AccCfg.migrate appends the lines from "notice.boosters" on to a 0.4.x file)
''', '''# ---- 0.5 CONFIG (the defaults file = the kit's DEFAULTS; AccCfg.migrate appends the lines from "notice.boosters" on to a 0.4.x file)
# 0.5.3: the Night Vision id through the booster table's id rules (the Python mirror of AccDefs.tierOf / familyOf / isLegacy / modernOf)
assert NV_ID == "Skyy_Talisman_%s_%s" % (NV_ADMIN, ID_WORD[NV_TIER]) and DISPLAY[NV_TIER] == "Rare", NV_ID
assert py_tier(NV_ID) == NV_TIER and py_family(NV_ID) == NV_ADMIN and py_tail_tier(NV_ID) == -1 and not py_legacy(NV_ID) and py_modern(NV_ID) == NV_ID
assert NV_ADMIN not in [_b[0] for _b in BOOSTERS] + [_b[1] for _b in BOOSTERS] and NV_LINE not in [_b[2] for _b in BOOSTERS]
assert NV_ID not in LINE_IDS + OLD_IDS + LEGACY_IDS and not NV_ID.startswith("Skyy_Accessory_")
''')

# the default file text gets the Night Vision part (a fresh install only - AccCfg.migrate's ADD_KEY list is unchanged, so an existing
# file is never appended to)
rep('''] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + [""])
''', '''] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + NV_CONFIG_LINES + [""])   # 0.5.3: + Night Vision
''')

# ---------------------------------------------------------------------------------------------------------------- AccDefs
rep('''dfs.addField(CtField.make('public static final String RETIRED_COLOR = "#8a97a3";', dfs))
''', r'''dfs.addField(CtField.make('public static final String RETIRED_COLOR = "#8a97a3";', dfs))
# 0.5.3 NIGHT VISION: its id, names, rarity, acc:defs source word, defaults, the server-wide switch and the light (the kit's field: rows),
# and the helpers every other method uses (compiled first: javassist needs a method before its callers)
dfs.addField(CtField.make('public static final String NV_ID = "%s";' % NV_ID, dfs))
dfs.addField(CtField.make('public static final String NV_ADMIN = "%s";' % NV_ADMIN, dfs))
dfs.addField(CtField.make('public static final String NV_LINE = "%s";' % NV_LINE, dfs))
dfs.addField(CtField.make('public static final int NV_TIER = %d;' % NV_TIER, dfs))
dfs.addField(CtField.make('public static final String NV_SRC = "%s";' % NV_SRC, dfs))
dfs.addField(CtField.make('public static final int[] NV_DEF = new int[] { %s };' % ", ".join(str(_x) for _x in NV_DEF), dfs))
dfs.addField(CtField.make('public static volatile boolean LINE_NIGHTVISION = true;', dfs))   # config row line.NightVision
for _nf, _nd in zip(NV_FIELDS, NV_DEF):
    dfs.addField(CtField.make('public static volatile int %s = %d;' % (_nf, _nd), dfs))      # config rows nightVision.*
JM(dfs, r"""
public static boolean isNv(String id) {
  return NV_ID.equals(id);
}""")
JM(dfs, r"""
public static boolean hasNv(String[] s) {
  if (s == null) return false;
  for (int i = 0; i < s.length; i++) if (NV_ID.equals(s[i])) return true;
  return false;
}""")
# /accessories givetier <player> NightVision Rare (also Night_Vision, Night-Vision, NV)
JM(dfs, r"""
public static boolean isNvName(String w) {
  if (w == null) return false;
  String x = w.trim();
  return x.equalsIgnoreCase(NV_ADMIN) || x.equalsIgnoreCase("Night_Vision") || x.equalsIgnoreCase("Night-Vision") || x.equalsIgnoreCase("NV");
}""")
JM(dfs, r"""
public static String nvOnText() {
  return "@ON@";
}""".replace("@ON@", NV_ON_TEXT))
JM(dfs, r"""
public static String nvLinesText() {
  return "@LT@";
}""".replace("@LT@", NV_LINES_TEXT))
''')
# its name has no rarity word (one rarity; the frame and the bag row say Rare) - pretty() and the refusal's line label
rep('''public static String pretty(String id) {
  if (isTalisman(id)) {   // 0.5: "<Rarity> <Line> Accessory" - never the family key or the old word (a legacy id shows its rarity's name)
''', '''public static String pretty(String id) {
  if (NV_ID.equals(id)) return NV_LINE + " Accessory";   // 0.5.3: one rarity, so no rarity word in its name
  if (isTalisman(id)) {   // 0.5: "<Rarity> <Line> Accessory" - never the family key or the old word (a legacy id shows its rarity's name)
''')
rep('''public static String lineLabel(String id) {
  if (isTalisman(id)) {
''', '''public static String lineLabel(String id) {
  if (NV_ID.equals(id)) return NV_LINE + " Accessory";   // 0.5.3
  if (isTalisman(id)) {
''')
# the bag page: one "Night Vision" row after the booster lines (AccGear.pageRows puts its notes in the rows still free)
rep('''    out[n * 2 + 1] = sb.length() > 0 ? sb.toString() : "nothing (its numbers are 0 on this server)";
    n++;
  }
  return out;
}""")
''', '''    out[n * 2 + 1] = sb.length() > 0 ? sb.toString() : "nothing (its numbers are 0 on this server)";
    n++;
  }
  if (hasNv(s) && n < BONUS_MAX) {   // 0.5.3: Night Vision - its own line, after the booster lines
    out[n * 2] = NV_LINE;
    out[n * 2 + 1] = LINE_NIGHTVISION ? nvOnText() : "switched off";
    n++;
  }
  return out;
}""")
''')
# /accessories lines: one more line (Rare only); admins also see its id
rep('''      out.add(ib.toString());
    }
  }
  return (String[]) out.toArray(new String[0]);
}""")
''', '''      out.add(ib.toString());
    }
  }
  StringBuilder nb = new StringBuilder();   // 0.5.3: Night Vision - one rarity, its own line
  nb.append(NV_LINE).append(" Accessory (").append(NV_ADMIN).append(")");
  if (!LINE_NIGHTVISION) nb.append(" - SWITCHED OFF on this server");
  nb.append(": ").append(DISPLAY[NV_TIER]).append(" only - ").append(nvLinesText());
  out.add(nb.toString());
  if (ids) out.add("    ids: " + NV_ID);
  return (String[]) out.toArray(new String[0]);
}""")
''')
# acc:defs: one record for its one rarity
rep('''      sb.append(':').append(DISPLAY[t]).append(':').append(AP[t]).append(':').append(LINE_SRC[li * 4 + t - 1]);
    }
  }
  return sb.toString();
}""")
''', '''      sb.append(':').append(DISPLAY[t]).append(':').append(AP[t]).append(':').append(LINE_SRC[li * 4 + t - 1]);
    }
  }
  if (sb.length() > 0) sb.append(',');   // 0.5.3: Night Vision - the record of its one rarity
  sb.append(NV_ADMIN).append(':').append(NV_ADMIN).append(':').append(NV_TIER).append(':').append(NV_ID);
  sb.append(':').append(DISPLAY[NV_TIER]).append(':').append(AP[NV_TIER]).append(':').append(NV_SRC);
  return sb.toString();
}""")
''')

# ---------------------------------------------------------------------------------------------------------------- AccStore
# a bag change (AccStore.publish runs after every save, on join and on a profile switch) makes Night Vision decide on the next tick
rep('''st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SPEED = new java.util.concurrent.ConcurrentHashMap();", st_))
''', '''st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SPEED = new java.util.concurrent.ConcurrentHashMap();", st_))
# 0.5.3: uuid -> the bag changed since Night Vision last looked (save, join, profile switch): AccNv.step decides on the next world tick
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap NVPOKE = new java.util.concurrent.ConcurrentHashMap();", st_))
''')
rep('''    PUBKEY.put(u, k);
''', '''    PUBKEY.put(u, k);
    NVPOKE.put(u, Boolean.TRUE);   // 0.5.3: Night Vision looks at this bag on the next world tick
''')

# ---------------------------------------------------------------------------------------------------------------- AccCfg (the loader)
rep('''cfg_.addField(CtField.make("public static final String[] NEW_COMMENT = new String[] { %s };" % jstrs(n for o, n in OLD_COMMENTS), cfg_))
''', '''cfg_.addField(CtField.make("public static final String[] NEW_COMMENT = new String[] { %s };" % jstrs(n for o, n in OLD_COMMENTS), cfg_))
# 0.5.3 Night Vision: the switch and the light keys, their maximums (minimum 0); defaults in AccDefs.NV_DEF
cfg_.addField(CtField.make('public static final String NV_SWITCH = "%s";' % NV_SWITCH, cfg_))
cfg_.addField(CtField.make("public static final String[] NV_KEYS = new String[] { %s };" % jstrs(NV_KEYS), cfg_))
cfg_.addField(CtField.make("public static final int[] NV_MAX = new int[] { %s };" % ", ".join(str(_x) for _x in NV_MAX), cfg_))
''')
rep('''  boolean cg = boolIn(p.getProperty("combatToGear"), true, "combatToGear");   // 0.5 part 2
''', '''  boolean cg = boolIn(p.getProperty("combatToGear"), true, "combatToGear");   // 0.5 part 2
  boolean nvOn = boolIn(p.getProperty(NV_SWITCH), true, NV_SWITCH);   // 0.5.3: Night Vision - the switch and the light (a missing key = its default)
  int[] nvv = new int[NV_KEYS.length];
  for (int q = 0; q < NV_KEYS.length; q++) nvv[q] = intIn(p.getProperty(NV_KEYS[q]), @PKG@.AccDefs.NV_DEF[q], 0, NV_MAX[q], NV_KEYS[q]);
''')
rep('''  @PKG@.AccDefs.COMBAT_TO_GEAR = cg;
''', '''  @PKG@.AccDefs.COMBAT_TO_GEAR = cg;
  @PKG@.AccDefs.LINE_NIGHTVISION = nvOn;   // 0.5.3
  @PKG@.AccDefs.NV_RADIUS = nvv[0];
  @PKG@.AccDefs.NV_RED = nvv[1];
  @PKG@.AccDefs.NV_GREEN = nvv[2];
  @PKG@.AccDefs.NV_BLUE = nvv[3];
  @PKG@.AccDefs.NV_REFRESH = nvv[4];
''')
rep('''  if (!cg) res = res + ", combat stats are not sent to SkyyGear (combatToGear=false)";
''', '''  if (!cg) res = res + ", combat stats are not sent to SkyyGear (combatToGear=false)";
  if (!nvOn) res = res + ", Night Vision switched off";   // 0.5.3
  if (nvv[0] != @PKG@.AccDefs.NV_DEF[0] || nvv[1] != @PKG@.AccDefs.NV_DEF[1] || nvv[2] != @PKG@.AccDefs.NV_DEF[2] || nvv[3] != @PKG@.AccDefs.NV_DEF[3]) res = res + ", Night Vision light " + nvv[0] + "," + nvv[1] + "," + nvv[2] + "," + nvv[3];
  if (nvv[4] != @PKG@.AccDefs.NV_DEF[4]) res = res + (nvv[4] == 0 ? ", Night Vision light sent only when needed" : ", Night Vision light sent again every " + nvv[4] + " s");
''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup
rep('''CFG_CATS = [("bag", "Accessory Bag"), ("boosters", "Boosters")]
''', '''CFG_CATS = [("bag", "Accessory Bag"), ("boosters", "Boosters"), ("nightvision", "Night Vision")]   # 0.5.3: + Night Vision
''')
rep('''      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS]
assert all(len(_r[10]) <= 100 for _r in CFG_ROWS), [_r[0] for _r in CFG_ROWS if len(_r[10]) > 100]
''', '''      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS] + NV_ROWS   # 0.5.3: + Night Vision
assert all(len(_r[10]) <= 100 for _r in CFG_ROWS), [_r[0] for _r in CFG_ROWS if len(_r[10]) > 100]
''')

# ---------------------------------------------------------------------------------------------------------------- the admin give
rep('''  if (@PKG@.AccDefs.BAG.equals(id) || @PKG@.AccDefs.OMNI.equals(id)) return null;
''', '''  if (@PKG@.AccDefs.BAG.equals(id) || @PKG@.AccDefs.OMNI.equals(id)) return null;
  if (@PKG@.AccDefs.NV_ID.equals(id)) return null;   // 0.5.3: Night Vision (admin give only)
''')
rep('''    int li = @PKG@.AccDefs.lineOf(tk[1]);
    if (li < 0) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < @PKG@.AccDefs.LINE_ADMIN.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.LINE_ADMIN[i]); }
      msg(pr, "unknown line - use one of: " + sb.toString());
      return;
    }
    int t = @PKG@.AccDefs.rarityIndex(tk[2]);
    if (t < 1) { msg(pr, "unknown rarity - use Normal, Unique, Rare, Legendary or 1 to 4"); return; }
    id = @PKG@.AccDefs.idOf(li, t);
''', '''    int li = @PKG@.AccDefs.lineOf(tk[1]);
    boolean nvl = li < 0 && @PKG@.AccDefs.isNvName(tk[1]);   // 0.5.3: Night Vision - a line of one rarity (Rare)
    if (li < 0 && !nvl) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < @PKG@.AccDefs.LINE_ADMIN.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.LINE_ADMIN[i]); }
      sb.append(", ").append(@PKG@.AccDefs.NV_ADMIN);   // 0.5.3
      msg(pr, "unknown line - use one of: " + sb.toString());
      return;
    }
    int t = @PKG@.AccDefs.rarityIndex(tk[2]);
    if (t < 1) { msg(pr, "unknown rarity - use Normal, Unique, Rare, Legendary or 1 to 4"); return; }
    if (nvl && t != @PKG@.AccDefs.NV_TIER) { msg(pr, "Night Vision comes in Rare only - use Rare or 3"); return; }
    id = nvl ? @PKG@.AccDefs.NV_ID : @PKG@.AccDefs.idOf(li, t);
''')
rep('''  if (u == null || !@PKG@.AccDefs.isBoosterId(id) || n < 1 || n > 64) return 0;
''', '''  if (u == null || !(@PKG@.AccDefs.isBoosterId(id) || @PKG@.AccDefs.NV_ID.equals(id)) || n < 1 || n > 64) return 0;   // 0.5.3: + Night Vision
''')

# ---------------------------------------------------------------------------------------------------------------- AccNv (before AccTick)
rep('''tick.addInterface(pool.get("java.lang.Runnable"))
''', r'''# ================= 0.5.3 AccNv: THE NIGHT VISION LIGHT (the logic; AccNightVision.tick only reads the engine components) =================
# A DynamicLightUpdate(ColorLight radius, red, green, blue) queued on the player's OWN entity viewer for the player's OWN entity: only that
# player's client gets it, nothing is added to the entity (nothing saved, nobody else sees it). World thread only (AccNightVision, the
# entity tracker's update group: the viewer's visible set is complete and the update leaves in this tick's SendPackets).
# SENT uuid -> the entity (Ref) our light is on, SKEY uuid -> the light sent (radius<<24 | red<<16 | green<<8 | blue), CLK uuid ->
# float[]{seconds since the last decision, seconds since the last send}. Pruned by AccTick for players who left, cleared on shutdown.
JF(nv, "public static final java.util.concurrent.ConcurrentHashMap SENT = new java.util.concurrent.ConcurrentHashMap();")
JF(nv, "public static final java.util.concurrent.ConcurrentHashMap SKEY = new java.util.concurrent.ConcurrentHashMap();")
JF(nv, "public static final java.util.concurrent.ConcurrentHashMap CLK = new java.util.concurrent.ConcurrentHashMap();")
JF(nv, "public static final java.util.concurrent.atomic.AtomicLong SENDS = new java.util.concurrent.atomic.AtomicLong();")
JF(nv, "public static final java.util.concurrent.atomic.AtomicLong REMOVES = new java.util.concurrent.atomic.AtomicLong();")
JF(nv, "public static final java.util.concurrent.atomic.AtomicLong MISSES = new java.util.concurrent.atomic.AtomicLong();")
JM(nv, r"""
public static float[] clk(java.util.UUID u) {
  float[] c = (float[]) CLK.get(u);
  if (c == null) { c = new float[] { 1.0f, 0.0f }; CLK.put(u, c); }
  return c;
}""")
# the live light (config rows nightVision.radius / red / green / blue, each 0-255) packed into one int
JM(nv, r"""
public static int key() {
  return ((@PKG@.AccDefs.NV_RADIUS & 255) << 24) | ((@PKG@.AccDefs.NV_RED & 255) << 16) | ((@PKG@.AccDefs.NV_GREEN & 255) << 8) | (@PKG@.AccDefs.NV_BLUE & 255);
}""")
JM(nv, NVJ(r"""
public static @CLT@ light(int k) {
  return new @CLT@((byte) (k >>> 24), (byte) (k >>> 16), (byte) (k >>> 8), (byte) k);
}"""))
# queue the light; "Entity is not visible!" (the client does not see its own entity this tick) = not sent, the next check tries again
JM(nv, NVJ(r"""
public static boolean send(java.util.UUID u, @REF@ ref, @EVW@ v, int k) {
  try {
    v.queueUpdate(ref, new @DLU@(light(k)));
  } catch (IllegalArgumentException e) {
    SENT.remove(u);
    SKEY.remove(u);
    MISSES.incrementAndGet();
    return false;
  }
  SENT.put(u, ref);
  SKEY.put(u, Integer.valueOf(k));
  float[] c = clk(u);
  c[1] = 0.0f;
  SENDS.incrementAndGet();
  return true;
}"""))
# take the light back - only from the entity it was sent to (an entity that is gone - world switch, logout - took it with it)
JM(nv, NVJ(r"""
public static boolean clear(java.util.UUID u, @REF@ ref, @EVW@ v) {
  Object was = SENT.remove(u);
  SKEY.remove(u);
  if (was == null || was != ref || v == null) return false;
  try {
    v.queueRemove(ref, @CUT@.DynamicLight);
  } catch (IllegalArgumentException e) {
    return false;
  }
  REMOVES.incrementAndGet();
  return true;
}"""))
# ONE TICK for one player (u, their own entity ref, their own viewer v, their Visible vis, the client is ready, another light owns the
# player, dt). A decision once a second, at once after a bag change (AccStore.NVPOKE) and at once when the client re-creates the
# entity (the player in their own Visible.newlyVisibleTo: join, world change - whatever it had from us is gone). Returns 0 nothing to do,
# 1 light sent (a new entity or a new light), 2 sent again (the client re-created the entity), 3 the safety re-send, 4 light taken back,
# 5 another light owns the player (ours is not sent; it comes back when that one goes), 6 the client is not ready, 7 forgotten (it was
# on an entity that is gone), -1 not sent (not visible - the next check tries again).
JM(nv, NVJ(r"""
public static int step(java.util.UUID u, @REF@ ref, @EVW@ v, @VSB@ vis, boolean ready, boolean other, float dt) {
  if (u == null || ref == null || v == null) return 0;
  float[] c = clk(u);
  c[0] = c[0] + dt;
  c[1] = c[1] + dt;
  boolean newly = vis != null && vis.newlyVisibleTo != null && vis.newlyVisibleTo.containsKey(ref);
  if (newly && SENT.get(u) == ref) { SENT.remove(u); SKEY.remove(u); }
  boolean poke = @PKG@.AccStore.NVPOKE.remove(u) != null;
  if (c[0] < 1.0f && !poke && !newly) return 0;
  c[0] = 0.0f;
  if (!ready) return 6;
  boolean want = @PKG@.AccDefs.LINE_NIGHTVISION && @PKG@.AccDefs.hasNv(@PKG@.AccStore.snapshot(u));
  Object s = SENT.get(u);
  if (!want) {
    if (s == null) return 0;
    return clear(u, ref, v) ? 4 : 7;
  }
  if (other) {
    if (s != null) { SENT.remove(u); SKEY.remove(u); }
    return 5;
  }
  int k = key();
  Object sk = SKEY.get(u);
  if (s == ref && sk != null && ((Integer) sk).intValue() == k) {
    int rf = @PKG@.AccDefs.NV_REFRESH;
    if (rf <= 0 || c[1] < (float) rf) return 0;
    return send(u, ref, v, k) ? 3 : -1;
  }
  return send(u, ref, v, k) ? (newly ? 2 : 1) : -1;
}"""))
JM(nv, r"""
public static void prune(java.util.Set online) {
  SENT.keySet().retainAll(online);
  SKEY.keySet().retainAll(online);
  CLK.keySet().retainAll(online);
  @PKG@.AccStore.NVPOKE.keySet().retainAll(online);
}""")
JM(nv, r"""
public static void clearAll() {
  SENT.clear();
  SKEY.clear();
  CLK.clear();
  @PKG@.AccStore.NVPOKE.clear();
}""")

tick.addInterface(pool.get("java.lang.Runnable"))
''')
rep('''  try {
    @PKG@.AccGear.prune(online);
''', '''  try { @PKG@.AccNv.prune(online); } catch (Throwable t) { }   // 0.5.3: the Night Vision state of players who left
  try {
    @PKG@.AccGear.prune(online);
''')

# ---------------------------------------------------------------------------------------------------------------- AccNightVision (the system)
rep('''assert ENTRIES[KIND_E["jumpPct"]][1] == ENTRIES[KIND_E["fallPct"]][1], "Feather's jump and fall are one line"
''', r'''assert ENTRIES[KIND_E["jumpPct"]][1] == ENTRIES[KIND_E["fallPct"]][1], "Feather's jump and fall are one line"

# ================= 0.5.3 AccNightVision: the Night Vision system (EntityTickingSystem on Player entities, the entity tracker's UPDATE GROUP) =================
# EntityTrackerSystems.QUEUE_UPDATE_GROUP runs after the visible sets are built (RemoveEmptyVisibleComponent: AFTER AddToVisible, BEFORE the
# group) and before SendPackets (AFTER the group) - the engine's own update queuers live there; a system with no group (AccEffects) can
# land anywhere in that order, so the light is not queued from AccEffects. isParallel is not overridden (false): the world thread, one
# player after another. ONE registerSystem for this class (setup). The logic is AccNv.step; this only reads the engine components.
nvs.addConstructor(CtNewConstructor.make("public AccNightVision() { super(); }", nvs))
JF(nvs, "public static boolean FAILED = false;")
JM(nvs, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
JM(nvs, NVJ(r"""
public @SGR@ getGroup() {
  return @ETR@.QUEUE_UPDATE_GROUP;
}"""))
JM(nvs, NVJ(r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    @EVW@ v = (@EVW@) store.getComponent(ref, @EVW@.getComponentType());
    if (v == null) return;
    @VSB@ vis = (@VSB@) store.getComponent(ref, @VSB@.getComponentType());
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    boolean ready = p != null && !p.isWaitingForClientReady();
    boolean other = store.getComponent(ref, @DLC@.getComponentType()) != null;
    @PKG@.AccNv.step(pr.getUuid(), ref, v, vis, ready, other, dt);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("Night Vision failed (logged once): " + t); }
  }
}"""))
''')

# ---------------------------------------------------------------------------------------------------------------- the plugin
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.AccEffects());
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.AccEffects());
  getEntityStoreRegistry().registerSystem(new @PKG@.AccNightVision());   // 0.5.3: Night Vision (the entity tracker's update group)
''')
rep('''  try { com.skyy.accessories.AccGear.shutdownAll(); } catch (Throwable t) { }   // 0.5 part 2: our gear:extra texts + movement entries
''', '''  try { com.skyy.accessories.AccGear.shutdownAll(); } catch (Throwable t) { }   // 0.5 part 2: our gear:extra texts + movement entries
  try { com.skyy.accessories.AccNv.clearAll(); } catch (Throwable t) { }   // 0.5.3: the Night Vision state (the lights go with the clients)
''')
rep('''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear):
''', '''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear, nv, nvs):   # 0.5.3: + AccNv, AccNightVision
''')
rep('''"inventory cooking, %d booster lines in the gear rarities Normal to Legendary (''',
    '''"inventory cooking, a Night Vision accessory (its own line - a light only its wearer sees), %d booster lines in the gear rarities Normal to Legendary (''')

# ---------------------------------------------------------------------------------------------------------------- the item + lang
rep('''lang.extend(WB.LANG_LINES)   # 0.5.2: the tab name (benchCategories.workbench.skyyaccessories + the server. twin)
''', r'''lang.extend(WB.LANG_LINES)   # 0.5.2: the tab name (benchCategories.workbench.skyyaccessories + the server. twin)
# ---- 0.5.3 THE NIGHT VISION ITEM: no recipe (admin give only), the look of the vanilla Lightning Essence (model, texture, icon), Rare,
# listed in the creative library like every current item. Its 4 lang lines go last: server.lang = 0.5.2's + these lines.
_nvnode = item(NV_ID, icon_of(NV_LOOK), QUAL_IDS[NV_TIER], [], WB_REQ, visual=visual_of(NV_LOOK))
del _nvnode["Recipe"]
files["Server/Item/Items/Utility/%s.json" % NV_ID] = json.dumps(_nvnode, indent=2)
NV_NAME = "%s Accessory" % NV_LINE
NV_DESC = (_w(NV_LINE) + " - see in the dark while in your Accessory Bag." + TIP_NL + "Lights up the night and dark caves around you. "
           "Only you see the light." + TIP_NL + "It is its own line, so it counts next to all your other accessories." + TIP_NL + TIP_NL +
           "<i>%s</i>" % NV_FLAVOUR)
NV_LANG = ["items.%s.name=%s" % (NV_ID, NV_NAME), "server.items.%s.name=%s" % (NV_ID, NV_NAME),
           "items.%s.description=%s" % (NV_ID, NV_DESC), "server.items.%s.description=%s" % (NV_ID, NV_DESC)]
lang.extend(NV_LANG)
''')
rep('''    want = set(LINE_IDS) | set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in ACTIVE for t in range(1, b[3] + 1)) | {OMNI, BAG}
''', '''    want = set(LINE_IDS) | set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in ACTIVE for t in range(1, b[3] + 1)) | {OMNI, BAG, NV_ID}   # 0.5.3
''')
rep('''


_hidden_checks()
''', r'''


_hidden_checks()


def _nv_asset_checks():
    """0.5.3 build check: the Night Vision item - Rare, no recipe, listed in the creative library, the Lightning Essence look (no other
    accessory has it), its name and vanilla-style tooltip (items. + server.items., last in server.lang), never a booster / bench /
    Workbench-tab / hidden id"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    n = items[NV_ID]
    v = visual_of(NV_LOOK)
    assert n["Quality"] == QUAL_IDS[NV_TIER] == "Skyy_Acc_Rare" and "Recipe" not in n and "Variant" not in n, n
    assert n["Categories"] == ["Items.Tools"] and n["MaxStack"] == 1 and n["Icon"] == icon_of(NV_LOOK) and "Interactions" not in n, n
    assert all(n[k] == v[k] for k in v), (n, v)
    lt = files["Server/Languages/en-US/server.lang"].split("\n")
    assert lt[-5:-1] == NV_LANG and lt[-1] == "", lt[-6:]
    assert NV_DESC.startswith('<color is="#ffffff">Night Vision</color> - see in the dark while in your Accessory Bag.') and NV_DESC.count(TIP_NL) == 4
    assert NV_ID not in WB.EXPECTED and NV_ID not in HIDDEN_IDS and NV_ID not in LINE_IDS
    same = [i2 for i2, n2 in items.items() if i2 != NV_ID and n2.get("Icon") == n["Icon"]]
    assert not same, "another accessory already looks like Night Vision: %s" % same
    print("night vision item: %s (%s, %s), no recipe (admin give only), the %s look, listed in the creative library; tooltip: %s"
          % (NV_ID, NV_NAME, DISPLAY[NV_TIER], NV_LOOK, NV_DESC.split(TIP_NL)[0]))


_nv_asset_checks()
''')
rep('''the Omni accessory counts as every bench accessory; speed stacks''',
    '''the Omni accessory counts as every bench accessory; the admin-given Night Vision accessory (its own line) gives its wearer alone a light that brightens caves and the night; speed stacks''')

# ---------------------------------------------------------------------------------------------------------------- final checks
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert s.count("registerSystem(") == 2 and s.count("registerSystem(new @PKG@.AccNightVision())") == 1, "one registerSystem per class (AccEffects, AccNightVision)"
assert 'VERSION = "0.5.3"' in s and "NightVision" in s and s.count("_nv_engine_proof()") == 2 and s.count("_nv_asset_checks()") == 2
assert s.count("v.queueUpdate(ref, ") == 1 and s.count("v.queueRemove(ref, ") == 1 and s.count(".queueUpdate(ref") == 1, "the light is queued in AccNv only"
assert "putComponent" not in s and "PersistentDynamicLight" not in s and "new @DLC@" not in s, "no DynamicLight component is ever added"
for _a, _b in (("NV_ID = \"Skyy_Talisman_NightVision_Rare\"", "NV_CONFIG_LINES + [\"\"]"), ("public static boolean hasNv(", "public static String pretty("),
               ("public static String nvOnText()", "public static String[] bonusRows("), ("NVPOKE = new", "NVPOKE.put(u, Boolean.TRUE)"),
               ("public static int step(", "tick.addInterface(pool.get(\"java.lang.Runnable\"))"), ("@PKG@.AccNv.prune(online)", "nvs.addConstructor("),
               ("nvs.addConstructor(", "public void setup() {"), ("lang.extend(NV_LANG)", 'files["Server/Languages/en-US/server.lang"] = "\\n".join(lang)'),
               ("def _nv_asset_checks", "B.assemble(jar")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:40], _b[:40])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.5.2
print("wrote", dst, "(%d lines; 0.5.2 had %d)" % (s.count(LF), OLD.count(LF)))
