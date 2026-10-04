"""Derive SkyyAccessories/build_skyyaccessories_0.5.4.py from the GENERATED 0.5.3 script (build_skyyaccessories_0.5.3.py = the
tools/deploy_set.py SET pin, itself written by tools/acc_0_5_3_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.3 script
stays untouched - never re-run acc_0_5_3_patch.py on top of this).
Run:  python tools/acc_0_5_4_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.4.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.4.py   (every 0.5.3 check carried forward + R the Night Vision retirement +
      Q the Lantern on a REAL engine ECS world + Y compare with 0.5.3)

0.5.4 = THE LANTERN LINE REPLACES NIGHT VISION. Skyy 2026-10-03 (OPEN-QUESTIONS, LOCKED), verbatim: "forget night vision, just do the
lantern accessory we talked about. that just makes you glow like the backpack torch mod. (brighter the higher rarity." + picked "Range up,
brightness capped": Common = a normal torch's light, each higher rarity reaches about twice as far (Legendary ~8x a torch's reach) while
the BRIGHTNESS stays at torch level - the extra reach comes from a hidden helper light above the wearer, so nearby particles never glare.
GENERAL RULE (Skyy, same day): "all accessories and bags cost the last rarity/size to craft the next one. so id need a uncommon lantern to
craft a rare lantern."

WHAT PLAYERS GET
 - FOUR items, Skyy_Talisman_Lantern_Common / _Uncommon / _Rare / _Epic = Normal / Unique / Rare / Legendary Lantern Accessory (the folded
   lines' id words, so the shared Workbench tab rank (tools/skyywbtab.py WbRank, unchanged) files each one into its rarity tier after the
   five crafted stat lines - Normal Lantern right after the Normal Speed Accessory, ... - with no change to the shared kit). Looks: four
   vanilla lanterns (Lantern, Kweebec Lantern, Sandswept Lantern, Light Temple Lantern; block model + icon copied at build time, the vanilla
   Slowness Totem pattern of a block model on a plain item). RECIPES at the Workbench "Accessories & Bags" tab, each tier FROM the tier
   below: Normal = 1 Lantern + 4 Crude Torch + 2 Copper Ingot; Unique = Normal Lantern Accessory + 3 Yellow Crystal Shards + 4 Copper Ingot
   + 5 Tree Sap; Rare = Unique + 1 Topaz + 10 Iron Ingot + 5 Essence of Fire; Legendary = Rare + 3 Topaz + 10 Thorium Ingot + 15 Essence of
   Fire (the Stamina line's metal / gem ladder; every input has a vanilla source - Motes of Light have none and are not used).
 - ITS OWN LINE (group T:Lantern): it stacks with every booster line, the bench accessories and the Omni; one per bag, a higher rarity
   swaps a lower one out (the booster rule). Admin give: /accessories givetier <player> Lantern <rarity>, /accessories give, acc:fn:give;
   acc:defs carries 4 records (source word Craft).
 - While it sits in the player's Accessory Bag (the ACTIVE profile's bag, the line switched on, the player alive):
     1. THE GLOW: a DynamicLight COMPONENT on the player - the vanilla torch's own light (#ba9 = levels 11 / 10 / 9, proven from
        Assets.zip at build time and through the engine's parser in the harness). The engine's DynamicLightTracker sends it to EVERY
        viewer (the wearer included), so everyone sees them glow like carrying a torch; DynamicLight has no codec, so it is never saved
        (logout / restart drop it), and DynamicLightSystems$EntityTrackerRemove takes it off every client the moment the component goes.
     2. THE REACH (Unique and up): ONE hidden helper entity per wearer above them carrying its own DynamicLight - the vanilla ambient
        emitter pattern (AmbientEmitterSystems$EntityRefAdded: TransformComponent + NetworkId + Intangible + NonSerialized, spawned
        through the CommandBuffer) + a DespawnComponent dead-man switch (5 s, refreshed every tick) + our marker component. No model, no
        BoundingBox, no Interactable: invisible, never LOD-culled, no collision, nothing to click. NonSerialized: never saved anywhere
        (Archetype.hasSerializableComponents is false - EntityChunk / the RocksDB saver skip it), so nothing survives a restart.
        THE REACH LIGHT IS THE WEARER'S OWN (fix round): AccLanternHide sits in the entity tracker's FIND_VISIBLE_ENTITIES_GROUP after
        CollectVisible - the vanilla SpectatorSystems$HideFromNonSpectators / HideFromPlayer pattern - and takes every OTHER wearer's helper
        out of each viewer's visible set, so the engine never sends a helper (its entity, moves or light) to anyone but its wearer; the glow
        on the player still reaches everyone. Server Setup lantern.shareReach (Advanced, default off) shows the reach light to everyone
        again (then a viewer who /hide's the wearer still never gets it). The light is WHITE (red = green = blue = the level): the client
        fades every colour channel on its own (LightCluster getChannelLightNEW(d, Color.r / .g / .b), zero at 10 x channel / 15 blocks),
        so a torch-tinted far light would reach the ground pure red; the torch tint stays on the glow.
 - BRIGHTNESS ABOUT TORCH LEVEL (research/NightVision-Glare-Research.md: light = 0.8 C (1 - 0.1 d / C)^1.5 with C = level / 15, zero
   past 0.635 x level blocks, lights combine with MAX; particles get 4 x the light with no cap): the helper's light at 3 blocks above the
   wearer's feet (eye-level mining bits) is never above the wearer's own glow at its brightest (the dust at their feet, 0.3 blocks from
   it); higher up it is a little brighter (at 6 blocks up 1.25 - 1.45 x that), which is why the reach light is the wearer's own: nobody
   standing near the hidden light sees it. "Reach" = how far from the wearer the ground
   is still lit (at least 5 % light); a torch reaches ~6 blocks. Per rarity the helper sits as LOW as the reach allows under that cap:
       Normal     glow 11 (the torch)                          reach  5.9 blocks (fully lit  2.3)
       Unique     glow 11 + light level  31 at  14 blocks up  reach 12.3 blocks (2.1x)
       Rare       glow 11 + light level  72 at  38 blocks up  reach 24.7 blocks (4.2x, fully lit 6.7)
       Legendary  glow 11 + light level 208 at 123 blocks up  reach 48.1 blocks (8.1x, fully lit 23.7)
   (the build computes this table from the Server Setup defaults and stops when it changes; the Java solver = the Python one, harness Q.)
   The light shines through blocks (point lights have no occlusion) - only the wearer sees it, so nobody above a caving wearer sees a lit
   patch (unless lantern.shareReach is on).
 - SAFE PLACEMENT (UpdateLocationSystems bytecode): an entity moved into a missing / unloaded section logs a warning and is REMOVED, one
   moved into a non-ticking section is parked out of the world. So the helper only ever goes into a section that is loaded AND ticking
   (checked on the ChunkStore, re-checked every 20 ticks or when the target section changes; a lower good section is used otherwise), never
   above y 318 or below y 1 (ChunkUtil.HEIGHT 320, sections 0-9), never farther up than the wearer's own view radius - 4 blocks
   (EntityViewer.viewRadiusBlocks: CollectVisible only collects entities inside it, so a player with a short view distance still gets
   one); a lower helper gets a dimmer light (the cap holds at any height); below 5 blocks of room there is no helper. Heights are
   compared with a 1e-6 margin ((feet + 123) - feet can be 122.99999999999999). It is moved when it is more than height / 50 blocks
   (0.1 - 1.5) from its spot - at once when it is BELOW its spot (closer to the wearer = brighter) - so a walking wearer does not send a
   move every tick.
 - EVERY EXIT PATH: unequip / profile switch / line switched off -> the bag change pokes the decision (AccStore.LPOKE), glow and helper go
   at once; death -> at once (DeathComponent), back within a second of the respawn; a new entity of the player (join, world change)
   is decided on its first tick (the glow is back at once); logout / world change -> the player's old entity ref
   is invalid or in another store, so the helper system (AccLanternHelp, every tick on our marker) removes the helper in ITS world; a
   helper that was unloaded / despawned / parked is replaced (at most once a second per wearer, backing off after 20 in a minute) and a
   parked one that comes back is not the recorded helper -> removed; plugin stopped -> the 5 s DespawnComponent removes it without us;
   restart -> NonSerialized, nothing saved. Our glow carries radius byte 1 as an owner mark (no visible effect: every channel is >= 1), so
   a light another mod or the builder tool put on the player is never changed or removed (ours comes back when it goes) and our own light is
   still recognised after a plugin reload.
 - SERVER SETUP (new category "Lantern", the config kit tools/skyycfg.py; all live): line.Lantern (on), lantern.glow.<Rarity> (11 each,
   0-15), lantern.reach.<Rarity> (6 / 12 / 24 / 48 blocks, 0-64), lantern.height (128, 8-160 blocks, Advanced), lantern.shareReach (off,
   Advanced). A fresh config.properties carries them; an existing file is NOT rewritten (a missing key = its default; the kit adds a line
   when it is changed in game).

FIX ROUND (the adversarial review of the first 0.5.4 build): 1 the reach light was torch-tinted and reached the ground pure red -> white;
2 the cap held at one height only and bystanders near the hidden light saw strong glare (a player 30 blocks above a Legendary wearer:
particles 8 x) -> the reach light is the wearer's own (AccLanternHide) + honest wording + lantern.shareReach for servers that want it
shared; 3 a move was sent every tick at 0.02 blocks -> height / 50 (0.1 - 1.5), at once when below its spot; 4 floating-point noise
lowered the level and re-sent the light -> a 1e-6 margin; 6 the harness now runs sectionOk / sectionMask on a real World + ChunkStore and
the engine's DespawnSystem, CollectVisible ... SendPackets on a real entity tracker; nits: the reach a rarity shows when the glow alone
lights more than its row, the helper never higher than the wearer's view radius - 4. (5: SkyyMenu 0.3.6's Mods text still names Night
Vision - another mod's file, left for its next build.)

NIGHT VISION RETIRED: Skyy_Talisman_NightVision_Rare stays a valid item (owned copies load, look and read), but it is a retired accessory
like the 0.4.2 bench accessories: no light (AccNv / AccNightVision are gone), Equip refuses it with "Retired - the Lantern Accessory replaced
it", Unequip takes an equipped copy out, it never counts (rarityOf 0, not in acc:tal / acc:fn:has), out of /accessories lines, acc:defs,
givetier, give and acc:fn:give, hidden from the creative library (Variant, no Categories); its tooltip and name say it was replaced by the
Lantern. Its old config keys (line.NightVision, nightVision.*) are ignored when present (the live file never got them).

THE "PREVIOUS TIER" AUDIT (every recipe this mod generates, checked at build time - _ladder_audit): the 5 crafted stat lines (Health,
Stamina, Mana, Regeneration, Speed: each Unique / Rare / Legendary recipe takes the rarity below), the 11 bench accessory ladders (T(n+1) =
T(n) + materials), the Lantern (new) - all follow it; the Omni (all 11 top bench accessories), the Accessory Bag and the Campfire are
single items; the 5 part-2 lines (Brawler, Runic, Stonehide, Razorfang, Feather) have NO recipe at all (Skyy's decision 5: admin give until
the loot pass), retired / legacy ids have none. SkyySacks 0.7.12 (another mod, reported only): every bag type follows it too (Small ->
Medium + Linen -> Rare + Shadoweave -> Large + Cindercloth; Mythic Omni Bag = the five Large bags).

UNCHANGED: every booster line, number, id, rule and migration; the bag page markup (the Lantern row is one more bonus row); AccEffects,
AccGear, MoveSync; tools/skyywbtab.py (its build check is fed the 47 listed recipes, the 4 Lantern recipes are checked against its rank).
UNVERIFIED (in game only): how the glow and the reach look (the shader numbers come from the client exe research); that the client draws
a model-less entity's light (the vanilla ambient emitters are model-less, audio only; fallback idea: the vanilla Empty.blockymodel); how
smoothly the helper follows a sprinting player (the client is expected to glide it between the coarser moves); the hard edge of the
Legendary disc at the client's cut-off (0.635 x level).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.3.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.4.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.3"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.3"\n' in s and "AccNightVision" in s and "Lantern" not in s, "the source must be the generated 0.5.3 script"
REG0 = s.count("registerCommand(")
assert s.count("registerSystem(") == 2

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyAccessories 0.5.3 - build script (derived from the generated build_skyyaccessories_0.5.2.py by tools/acc_0_5_3_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.3.py            -> SkyyAccessories/SkyyAccessories-0.5.3.jar
       python build_skyyaccessories_0.5.3.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.3.py             (bare JVM -Xverify:all: every 0.5.2 check + Night Vision + compare with 0.5.2)
''', '''"""SkyyAccessories 0.5.4 - build script (derived from the generated build_skyyaccessories_0.5.3.py by tools/acc_0_5_4_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.4.py            -> SkyyAccessories/SkyyAccessories-0.5.4.jar
       python build_skyyaccessories_0.5.4.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.4.py             (bare JVM -Xverify:all: every 0.5.3 check + the Night Vision retirement + the
                                                         Lantern on a real engine ECS world + compare with 0.5.3)
0.5.4: THE LANTERN LINE REPLACES NIGHT VISION (Skyy 2026-10-03: "forget night vision, just do the lantern accessory we talked about. that
     just makes you glow like the backpack torch mod. (brighter the higher rarity." + "Range up, brightness capped"; full notes, the tier
     table and the engine proof in tools/acc_0_5_4_patch.py):
     - Lantern Accessory Normal / Unique / Rare / Legendary (Skyy_Talisman_Lantern_Common.._Epic), its own line, crafted at the Workbench
       tab, each tier FROM the tier below. In the Accessory Bag the wearer GLOWS like a torch for everyone (a DynamicLight component on
       the player - the vanilla torch's #ba9 light, never saved); Unique and up add REACH (about 12 / 24 / 48 blocks, a torch ~6) through
       ONE hidden helper entity above the wearer (NonSerialized, Intangible, no model, a 5 s DespawnComponent dead-man switch, our marker)
       with a WHITE light that only its wearer sees (AccLanternHide, the entity tracker's find-visible group; lantern.shareReach shows it
       to everyone), placed as low as the reach allows while eye-level bits stay as bright as torch-lit dust; it only goes into loaded,
       ticking sections between y 1 and 318, within the wearer's view radius. Off at once on unequip / profile switch / death / switch
       off; logout and world change remove it in its own world (AccLanternHelp). Server Setup -> Accessories -> Lantern: on / off, glow
       per rarity, reach per rarity, the highest helper, shared reach. Existing config files are not rewritten (missing keys = defaults).
     - Night Vision is RETIRED: the item stays valid but does nothing, cannot be equipped (Unequip still takes it out), never counts, is
       out of lines / givetier / give / acc:defs and hidden from the creative library; its tooltip says the Lantern replaced it.
     - The "previous tier" rule (Skyy) is checked on every recipe at build time; every line already followed it.
''')
rep('VERSION = "0.5.3"\n', 'VERSION = "0.5.4"\n')

# ---------------------------------------------------------------------------------------------------------------- the classes
rep('''nv   = pool.makeClass(PKG + ".AccNv")                            # 0.5.3: Night Vision - the wearer-only light (state + logic)
nvs  = pool.makeClass(PKG + ".AccNightVision", pool.get(ETS))    # 0.5.3: Night Vision - its system in the entity tracker's update group
''', '''lmk  = pool.makeClass(PKG + ".AccLanternMark")                   # 0.5.4: Lantern - the marker component on our helper entities
lms  = pool.makeClass(PKG + ".AccLanternMarkSup")                # 0.5.4: Lantern - its Supplier (ComponentRegistryProxy.registerComponent)
lan  = pool.makeClass(PKG + ".AccLantern")                       # 0.5.4: Lantern - the glow + the helper (state + logic)
lsys = pool.makeClass(PKG + ".AccLanternSys", pool.get(ETS))     # 0.5.4: Lantern - the system on every player (glow, helper follow)
lhs  = pool.makeClass(PKG + ".AccLanternHelp", pool.get(ETS))    # 0.5.4: Lantern - the system on our helpers (orphans removed)
lhd  = pool.makeClass(PKG + ".AccLanternHide", pool.get(ETS))    # 0.5.4: Lantern - the system on every viewer (others' helpers unseen)
''')

# ---------------------------------------------------------------------------------------------------------------- engine probes + proof
_A = s.index("# 0.5.3 NIGHT VISION - the engine members the light uses (every one B.probe'd)")
_B = s.index("_nv_engine_proof()\n\nPKG = ")
s = s[:_A] + r'''# 0.5.4 LANTERN - the engine members the glow and the helper use (every one B.probe'd) and the facts they rely on (_lantern_engine_proof
# reads them in HytaleServer.jar bytecode and stops the build when one changed; tools/acc_0_5_4_patch.py has the notes)
DLC = "com.hypixel.hytale.server.core.modules.entity.component.DynamicLight"
PDL = "com.hypixel.hytale.server.core.modules.entity.component.PersistentDynamicLight"
CLT = "com.hypixel.hytale.protocol.ColorLight"
TCO = "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"
NID = "com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId"
INT_ = "com.hypixel.hytale.server.core.modules.entity.component.Intangible"
DES = "com.hypixel.hytale.server.core.modules.entity.DespawnComponent"
DTH = "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent"
NSR = "com.hypixel.hytale.component.NonSerialized"
HLD = "com.hypixel.hytale.component.Holder"
CRG = "com.hypixel.hytale.component.ComponentRegistry"
CTY = "com.hypixel.hytale.component.ComponentType"
RTY = "com.hypixel.hytale.component.ResourceType"
ARS = "com.hypixel.hytale.component.AddReason"
RRS = "com.hypixel.hytale.component.RemoveReason"
ESR = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
CSR = "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore"
ARC = "com.hypixel.hytale.component.Archetype"
V3D = "org.joml.Vector3d"
COMP = "com.hypixel.hytale.component.Component"
# the fix round: the reach light is the wearer's own (AccLanternHide edits each viewer's visible set like HideFromNonSpectators)
EVW = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$EntityViewer"
ETR = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems"
CVS = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$CollectVisible"
SGR = "com.hypixel.hytale.component.SystemGroup"
SDP = "com.hypixel.hytale.component.dependency.SystemDependency"
ORD = "com.hypixel.hytale.component.dependency.Order"
HPM = "com.hypixel.hytale.server.core.entity.entities.player.HiddenPlayersManager"
for c, m in ((EVW, "getComponentType"), (EVW, "visible"), (EVW, "viewRadiusBlocks"), (ETR, "FIND_VISIBLE_ENTITIES_GROUP"), (ORD, "AFTER"),
             (HPM, "isPlayerHidden"), (PR, "getHiddenPlayersManager"), (ST, "getEntityCountFor"), (ACH, "getArchetype"), (CB, "getArchetype"),
             ("com.hypixel.hytale.component.system.tick.ArchetypeTickingSystem", "tick"), ("com.hypixel.hytale.component.system.ISystem", "getGroup"),
             ("com.hypixel.hytale.component.system.ISystem", "getDependencies")):
    B.probe(pool, c, m)
for c, m in ((DLC, "getComponentType"), (DLC, "getColorLight"), (DLC, "setColorLight"), (CLT, "radius"), (CLT, "red"), (CLT, "green"),
             (CLT, "blue"), (TCO, "getComponentType"), (TCO, "getPosition"), (TCO, "setPosition"), (NID, "getComponentType"),
             (INT_, "getComponentType"), (DES, "getComponentType"), (DES, "despawnInSeconds"), (DES, "setDespawnTo"),
             (DTH, "getComponentType"), (NSR, "get"), (HLD, "addComponent"), (HLD, "ensureComponent"), (CRG, "newHolder"),
             (CRG, "getNonSerializedComponentType"), (CRG, "getNonTickingComponentType"), (ARS, "SPAWN"), (RRS, "REMOVE"),
             (ESR, "takeNextNetworkId"), (ESR, "getWorld"), (WLD, "getChunkStore"), (CSR, "getChunkSectionReference"), (CSR, "getStore"),
             (ARC, "contains"), (ST, "getArchetype"), (ST, "getRegistry"), (ST, "getExternalData"), (ST, "getResource"),
             (ST, "getComponent"), (CB, "addComponent"), (CB, "tryRemoveComponent"), (CB, "addEntity"), (CB, "tryRemoveEntity"),
             (CB, "getComponent"), (ACH, "getComponent"), (ACH, "getReferenceTo"), (REF, "isValid"), (REF, "getStore"),
             (PR, "getComponentType"), (PR, "getUuid"), (TMR, "getResourceType"), (TMR, "getNow"), (V3D, "x"), (V3D, "y"), (V3D, "z"),
             (CRP, "registerComponent"), (CRP, "registerSystem")):
    B.probe(pool, c, m)


def _lantern_engine_proof():
    """0.5.4: the HytaleServer.jar facts the glow and the helper rely on (read in bytecode - a changed engine stops this build)"""
    import jpype as _jp
    IPc = _jp.JClass("javassist.bytecode.InstructionPrinter")

    def code(cls, name, desc=None):
        cc = pool.get(cls)
        out = []
        for mi in cc.getClassFile().getMethods():
            if str(mi.getName()) != name or (desc is not None and str(mi.getDescriptor()) != desc):
                continue
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            it = ca.iterator()
            while it.hasNext():
                p = it.next()
                out.append(str(IPc.instructionString(it, p, mi.getConstPool())))
        if not out:
            raise SystemExit("0.5.4: %s.%s is gone - re-check the Lantern (tools/acc_0_5_4_patch.py)" % (cls, name))
        return "\n".join(out)

    def need(cond, what):
        if not cond:
            raise SystemExit("0.5.4: the engine changed - %s; re-check the Lantern (tools/acc_0_5_4_patch.py)" % what)
    em = code("com.hypixel.hytale.server.core.modules.entity.EntityModule", "setup").split("\n")
    i_dl = [k for k, l in enumerate(em) if l.endswith("= Class " + DLC)]
    need(len(i_dl) == 1 and any("registerComponent((Ljava/lang/Class;Ljava/util/function/Supplier;)" in l for l in em[i_dl[0]:i_dl[0] + 6]),
         "DynamicLight is no longer registered WITHOUT a codec (registerComponent(Class, Supplier))")
    i_pd = [k for k, l in enumerate(em) if l.endswith("= Class " + PDL)]
    need(len(i_pd) == 1 and any("PersistentDynamicLight.CODEC" in l for l in em[i_pd[0]:i_pd[0] + 6]),
         "PersistentDynamicLight (the SAVED light) is no longer the one with the codec")
    need("CODEC" not in [str(f.getName()) for f in pool.get(DLC).getDeclaredFields()], "DynamicLight now has a CODEC field (it could be saved)")
    ini = code(DLC, "<init>", "(Lcom/hypixel/hytale/protocol/ColorLight;)V")
    need("iconst_1" in ini and "DynamicLight.isNetworkOutdated" in ini, "new DynamicLight(ColorLight) no longer marks itself for sending")
    scl = code(DLC, "setColorLight")
    need("iconst_1" in scl and "DynamicLight.isNetworkOutdated" in scl, "DynamicLight.setColorLight no longer marks the light for sending")
    dt = code("com.hypixel.hytale.server.core.modules.entity.system.EntitySystems$DynamicLightTracker", "tick")
    need("consumeNetworkOutdated" in dt and "Visible.visibleTo" in dt and "Visible.newlyVisibleTo" in dt and "queueUpdatesFor" in dt,
         "DynamicLightTracker no longer sends a light to every viewer (visibleTo) and to new viewers (newlyVisibleTo)")
    tr = code("com.hypixel.hytale.server.core.modules.entity.dynamiclight.DynamicLightSystems$EntityTrackerRemove", "onComponentRemoved",
              "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/modules/entity/component/DynamicLight;"
              "Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V")
    need("Visible.visibleTo" in tr and "EntityViewer.queueRemove" in tr and "ComponentUpdateType.DynamicLight" in tr,
         "a removed DynamicLight is no longer taken off every viewer")
    hs = code(ARC, "hasSerializableComponents")
    need("getNonSerializedComponentType" in hs and "Archetype.contains" in hs, "NonSerialized no longer makes an archetype unsaveable")
    for cn, mn in (("com.hypixel.hytale.server.core.universe.world.chunk.EntityChunk", "cloneSerializable"),
                   ("com.hypixel.hytale.server.core.universe.world.storage.provider.RocksDbChunkStorageProvider$Saver", "snapshotDirtyEntityReferences")):
        need("hasSerializableComponents" in code(cn, mn), "%s.%s no longer skips entities without saveable components" % (cn, mn))
    ae = code("com.hypixel.hytale.builtin.ambience.systems.AmbientEmitterSystems$EntityRefAdded", "onEntityAdded")
    need(all(x in ae for x in ("ComponentRegistry.newHolder", "TransformComponent.clone", "EntityStore.takeNextNetworkId",
                               "NetworkId.<init>", "Holder.ensureComponent", "getNonSerializedComponentType", "NonSerialized.get",
                               "CommandBuffer.addEntity", "AddReason.SPAWN")),
         "the vanilla helper-entity pattern (ambient emitters: Transform + NetworkId + Intangible + NonSerialized via the CommandBuffer) changed")
    ns = code("com.hypixel.hytale.server.core.modules.entity.system.NetworkSendableSpatialSystem", "<clinit>")
    need("TransformComponent.getComponentType" in ns and "NetworkId.getComponentType" in ns and "Archetype.of" in ns,
         "entities sent to clients are no longer exactly those with a TransformComponent and a NetworkId")
    cv = code("com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$CollectVisible", "tick")
    need("EntityViewer.viewRadiusBlocks" in cv and "SpatialStructure.collect" in cv, "visibility is no longer the viewer's radius in blocks")
    # the fix round - THE REACH LIGHT IS THE WEARER'S OWN: each tick ClearEntityViewers empties every viewer's visible set (BEFORE the
    # find-visible group), CollectVisible fills it (in the group), the vanilla HideFromPlayer / HideFromNonSpectators take entries out (in
    # the group, AFTER CollectVisible - AccLanternHide does the same), and only AFTER the group ClearPreviouslyVisible -> EnsureVisibleComponent
    # -> AddToVisible turn what is left into Visible.visibleTo / newlyVisibleTo, the only viewers the light, the moves and the entity go to
    T_ = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$"
    need("EntityViewer.visible" in cv and "Set.addAll" in cv and
         code(T_ + "CollectVisible", "getGroup").count("FIND_VISIBLE_ENTITIES_GROUP") == 1, "CollectVisible no longer fills the visible set in the find-visible group")
    ce = code(T_ + "ClearEntityViewers", "<clinit>")
    need("SystemGroupDependency.<init>" in ce and "Order.BEFORE" in ce and "FIND_VISIBLE_ENTITIES_GROUP" in ce and
         "EntityViewer.visible" in code(T_ + "ClearEntityViewers", "tick") and "Set.clear" in code(T_ + "ClearEntityViewers", "tick"),
         "the visible sets are no longer emptied BEFORE the find-visible group every tick")
    cp_ = code(T_ + "ClearPreviouslyVisible", "<clinit>")
    need("SystemGroupDependency.<init>" in cp_ and "Order.AFTER" in cp_ and "FIND_VISIBLE_ENTITIES_GROUP" in cp_,
         "ClearPreviouslyVisible no longer runs AFTER the find-visible group")
    need("Order.AFTER" in code(T_ + "EnsureVisibleComponent", "<clinit>") and "ClearPreviouslyVisible" in code(T_ + "EnsureVisibleComponent", "<clinit>")
         and "Order.AFTER" in code(T_ + "AddToVisible", "<clinit>") and "EnsureVisibleComponent" in code(T_ + "AddToVisible", "<clinit>"),
         "EnsureVisibleComponent / AddToVisible no longer follow ClearPreviouslyVisible")
    at_ = code(T_ + "AddToVisible", "tick")
    need("EntityViewer.visible" in at_ and "Visible.addViewerParallel" in at_, "AddToVisible no longer turns the visible set into Visible.visibleTo")
    hp_i, hp_t = code(T_ + "HideFromPlayer", "<init>"), code(T_ + "HideFromPlayer", "tick")
    need("Order.AFTER" in hp_i and "EntityTrackerSystems$CollectVisible" in hp_i and "FIND_VISIBLE_ENTITIES_GROUP" in code(T_ + "HideFromPlayer", "getGroup")
         and "EntityViewer.visible" in hp_t and "Iterator.remove" in hp_t and "HiddenPlayersManager.isPlayerHidden" in hp_t,
         "the vanilla HideFromPlayer no longer takes hidden players out of the visible set in the find-visible group after CollectVisible")
    hs_ = code("com.hypixel.hytale.server.core.modules.entity.spectator.SpectatorSystems$HideFromNonSpectators", "tick",
               "(FILcom/hypixel/hytale/component/Store;)V")
    need("Store.getEntityCountFor" in hs_ and "EntityTickingSystem.tick" in hs_,
         "the vanilla HideFromNonSpectators no longer skips a world without spectators (getEntityCountFor, then super.tick)")
    tu_ = code("com.hypixel.hytale.server.core.modules.entity.system.TransformSystems$EntityTrackerUpdate", "tick")
    need("Visible.visibleTo" in tu_ and "Visible.newlyVisibleTo" in tu_ and "PositionUtil.equals" in tu_,
         "a move is no longer sent only to the viewers that see the entity (Visible.visibleTo / newlyVisibleTo)")
    sd_ = code(T_ + "SendPackets", "tick")
    need("EntityViewer.sent" in sd_ and "Set.contains" in sd_ and "EntityUpdates.removed" in sd_,
         "an entity that left a viewer's visible set is no longer removed on that client (SendPackets)")
    need(any(str(k.getSignature()) == "(Lcom/hypixel/hytale/component/dependency/Order;Ljava/lang/Class;)V" for k in pool.get(SDP).getConstructors()),
         "new SystemDependency(Order, Class) is gone")
    lc = code("com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$LODCull", "tick")
    need("BoundingBox" in lc and "getMaximumThickness" in lc, "the LOD cull no longer needs a BoundingBox (a helper could be culled)")
    ts = code("com.hypixel.hytale.server.core.modules.entity.system.TransformSystems$EntityTrackerUpdate", "tick")
    need("getSentTransform" in ts and "PositionUtil.equals" in ts and "queueUpdatesFor" in ts, "a moved entity is no longer re-sent")
    ul = code("com.hypixel.hytale.server.core.modules.entity.system.UpdateLocationSystems", "updateLocation")
    need("-32.0" in ul and "ChunkUtil.chunkCoordinate" in ul and "getChunkSectionReference" in ul and "isn't currently loaded" in ul,
         "entities are no longer put into sections by chunkCoordinate (or the below-the-world / unloaded rules changed)")
    need("can't be loaded! Removing!" in code("com.hypixel.hytale.server.core.modules.entity.system.UpdateLocationSystems", "handleInvalidChunk"),
         "an entity in a section that cannot load is no longer removed")
    ue = code("com.hypixel.hytale.server.core.modules.entity.system.UpdateLocationSystems", "updateEntityInChunk")
    need("getNonTickingComponentType" in ue and "removeEntity" in ue and "addEntityHolder" in ue,
         "an entity moved into a non-ticking section is no longer parked (removeEntity + addEntityHolder)")
    ds = code("com.hypixel.hytale.server.core.modules.entity.DespawnSystem", "tick")
    need("TimeResource.getNow" in ds and "Instant.isAfter" in ds and "removeEntity" in ds, "DespawnSystem no longer removes an entity after its time")
    dq = code("com.hypixel.hytale.server.core.modules.entity.DespawnSystem", "<init>")
    need("Interactable.getComponentType" in dq and "Query.not" in dq, "DespawnSystem's query is no longer Despawn and not Interactable")
    rs = code("com.hypixel.hytale.server.core.modules.entity.damage.RespawnSystems$OnRespawnSystem", "componentType")
    need("DeathComponent.getComponentType" in rs, "a respawn is no longer the DeathComponent going away")
    ad = code(CB, "addEntity", "(Lcom/hypixel/hytale/component/Holder;Lcom/hypixel/hytale/component/AddReason;)Lcom/hypixel/hytale/component/Ref;")
    need("Ref.<init>((Lcom/hypixel/hytale/component/Store;)V)" in ad, "CommandBuffer.addEntity no longer hands back the (pending) Ref it adds")
    rv = code(REF, "isValid", "()Z")
    need("Ref.index" in rv and "-2147483648" in rv, "Ref.isValid is no longer index != MIN_VALUE")
    for cn in (PR, "com.hypixel.hytale.server.core.modules.entity.component.Intangible", NID, DES, DTH):
        need(COMP in [str(i.getName()) for i in pool.get(cn).getInterfaces()], "%s is no longer an entity component" % cn)
    cu = pool.get("com.hypixel.hytale.math.util.ChunkUtil")
    need(int(cu.getField("HEIGHT").getConstantValue()) == 320 and int(cu.getField("SIZE").getConstantValue()) == 32 and
         int(cu.getField("HEIGHT_SECTIONS").getConstantValue()) == 10, "the world is no longer 320 high in 10 sections of 32")
    need(int(pool.get(CLT).getField("FIXED_BLOCK_SIZE").getConstantValue()) == 4, "ColorLight is no longer 4 bytes")
    print("lantern: engine facts read - DynamicLight has no codec (never saved) and reaches every viewer, removal is sent; NonSerialized "
          "entities are never saved; the ambient-emitter helper pattern; Transform + NetworkId = sent; no BoundingBox = never LOD-culled; "
          "moves re-sent; sections 0-9 x 32 (unloaded / non-ticking sections refuse entities); DespawnSystem; respawn = DeathComponent removed; "
          "the visible set is rebuilt every tick and edited in the find-visible group after CollectVisible (HideFromPlayer / "
          "HideFromNonSpectators), then becomes Visible.visibleTo - the only viewers a light, a move or the entity itself is sent to")


_lantern_engine_proof()

PKG = ''' + s[_B + len("_nv_engine_proof()\n\nPKG = "):]

# ---------------------------------------------------------------------------------------------------------------- the Night Vision table -> retired + the Lantern table
_A = s.index("# ---- 0.5.3 NIGHT VISION (tools/acc_0_5_3_patch.py): ONE item of its own line")
_B = s.index("CAP = 60          # 0.5: bag STORAGE slots")
s = s[:_A] + r'''# ---- 0.5.3 NIGHT VISION, RETIRED in 0.5.4 (tools/acc_0_5_4_patch.py; Skyy 2026-10-03: "forget night vision, just do the lantern"):
# the id stays a valid item (owned copies load, look and read), but like the 0.4.2 bench accessories it does nothing, Equip refuses it,
# Unequip takes it out, it never counts, and it is out of lines / givetier / give / acc:defs and the creative library
NV_ID = "Skyy_Talisman_NightVision_Rare"
NV_ADMIN = "NightVision"                    # the old /accessories givetier name (now answered with "retired - use Lantern")
NV_LINE = "Night Vision"
NV_TIER = 3                                 # its id word (Rare): the frame keeps the Rare quality, rarityOf is 0 (retired)
NV_LOOK = "Ingredient_Lightning_Essence"    # the vanilla item whose model, texture and icon it copies (unchanged)
NV_WHY = "Retired - the Lantern Accessory replaced it - craft one at a Workbench"
NV_CHAT = ("The Night Vision Accessory is retired: the Lantern Accessory replaced it (craft one at a Workbench, /accessories lines shows "
           "it). This accessory does nothing any more and cannot be equipped. If one is still in your Accessory Bag, Unequip takes it out.")
NV_ROW = "retired - take it out"            # the bag page row while one is still in the bag (its slot row says "- retired")
NV_GIVE = "Night Vision is retired - the Lantern replaced it: /accessories givetier <player> Lantern <rarity>"
assert all(ord(_c) < 128 for _t in (NV_WHY, NV_CHAT, NV_ROW, NV_GIVE) for _c in _t) and not any(_c in NV_WHY for _c in ",:()")
# ---- 0.5.4 THE LANTERN LINE (tools/acc_0_5_4_patch.py): four rarities of its own line, crafted from the rarity below. Not a booster-table
# row (those carry stat numbers): it gives no stat, it lights the wearer (a DynamicLight component) and, from Unique up, a hidden helper
# entity above them. Word ids (the folded lines' Common / Uncommon / Rare / Epic) so the shared Workbench tab rank files each one into its
# rarity tier; the stat rules give them their rarity (tierOf), group T:Lantern (one per bag, a higher one swaps a lower one out), and
# bestTiers skips them (no booster family).
LAN_FAM = "Lantern"                         # the family key in the ids
LAN_ADMIN = "Lantern"                       # config / commands / acc:defs (/accessories givetier <player> Lantern Rare)
LAN_LINE = "Lantern"                        # what players see: "<Rarity> Lantern Accessory", the bag page row "Lantern"
LAN_IDS = ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Lantern_Uncommon", "Skyy_Talisman_Lantern_Rare", "Skyy_Talisman_Lantern_Epic"]
LAN_SRC = "Craft"                           # acc:defs source word of every rarity
# the look of each rarity: a vanilla lantern's block model + texture + icon (the vanilla Weapon_Deployable_Slowness_Totem carries a block
# model on a plain item the same way); names Lantern / Kweebec Lantern / Sandswept Lantern / Light Temple Lantern
LAN_LOOKS = ["Deco_Lantern", "Furniture_Kweebec_Lantern", "Furniture_Desert_Lantern", "Furniture_Temple_Light_Lantern"]
# the recipes at the Workbench tab: [Normal inputs, Unique extra, Rare extra, Legendary extra] - each upgrade also takes the rarity below
LAN_RECIPES = [
    [("Deco_Lantern", 1), ("Furniture_Crude_Torch", 4), ("Ingredient_Bar_Copper", 2)],
    [("Ingredient_Crystal_Yellow", 3), ("Ingredient_Bar_Copper", 4), ("Ingredient_Tree_Sap", 5)],
    [("Rock_Gem_Topaz", 1), ("Ingredient_Bar_Iron", 10), ("Ingredient_Fire_Essence", 5)],
    [("Rock_Gem_Topaz", 3), ("Ingredient_Bar_Thorium", 10), ("Ingredient_Fire_Essence", 15)],
]
LAN_FLAVOUR = "It never needs oil, and it never goes out."
# THE LIGHT. The vanilla torch players craft (Furniture_Crude_Torch "Crude Torch") and its wall form carry BlockType Light {Radius 0,
# Color "#ba9"}: a "#RGB" colour is one hex digit per channel (0-15, ColorParseUtil.hexStringToColorLightDirect; the harness runs the
# engine's parser on it), so the torch = levels 11 / 10 / 9. _torch_proof below reads both items from Assets.zip.
TORCH_ITEMS = ["Furniture_Crude_Torch", "Wood_Torch_Wall"]
TORCH_HEX = "#ba9"
TORCH_RGB = (11, 10, 9)
LAN_TORCH = 11                              # the torch's level (its brightest channel)
LAN_SIG_R = 1                               # our lights carry radius byte 1: max(channel, 1) = channel for channels >= 1 (no visible change)
LAN_VIS = 0.05                              # "lit" = at least 5% light (walls at 15%): the reach is measured at the wearer's feet level
LAN_PZ = 3.0                                # the wearer's own particles: up to 3 blocks above the feet
LAN_PD = 0.3                                # the glow at its brightest for particles (dust at the feet, 0.3 blocks from the light)
LAN_MINH = 5                                # a helper with less room than this above the feet is not used
LAN_TOP, LAN_BOTTOM = 318.0, 1.0            # inside the world (ChunkUtil.HEIGHT 320, sections 0-9 x 32 - proven in _lantern_engine_proof)
LAN_DESPAWN = 5.0                           # the helper's DespawnComponent: removed 5 s after we last refreshed it (refreshed every tick)
LAN_EPS = 1.0e-6                            # height margin: (feet + 123) - feet can be 122.99999999999999 (review finding 4)
LAN_VIEW_MARGIN = 4                         # the helper stays this far inside the wearer's view radius (CollectVisible's radius)
LAN_MOVE_DIV, LAN_MOVE_MIN, LAN_MOVE_MAX = 50.0, 0.1, 1.5   # moved when off its spot by height / 50 blocks, 0.1 - 1.5 (finding 3)
LAN_RARITIES = ["Normal", "Unique", "Rare", "Legendary"]
LAN_SWITCH = "line.Lantern"
LAN_SHARE_KEY = "lantern.shareReach"        # fix round: off = the reach light is the wearer's own (AccLanternHide); on = everyone sees it
LAN_KEYS = (["lantern.glow.%s" % _r for _r in LAN_RARITIES] + ["lantern.reach.%s" % _r for _r in LAN_RARITIES] + ["lantern.height"])
LAN_FIELDS = ["LAN_GLOW1", "LAN_GLOW2", "LAN_GLOW3", "LAN_GLOW4", "LAN_REACH1", "LAN_REACH2", "LAN_REACH3", "LAN_REACH4", "LAN_HEIGHT"]
LAN_DEF = [11, 11, 11, 11, 6, 12, 24, 48, 128]
LAN_MIN = [0, 0, 0, 0, 0, 0, 0, 0, 8]
LAN_MAX = [15, 15, 15, 15, 64, 64, 64, 64, 160]
assert len(LAN_KEYS) == len(LAN_FIELDS) == len(LAN_DEF) == len(LAN_MIN) == len(LAN_MAX) == 9
assert all(_lo <= _d <= _hi for _lo, _d, _hi in zip(LAN_MIN, LAN_DEF, LAN_MAX)) and LAN_DEF[:4] == [LAN_TORCH] * 4
LAN_ON_OFF = "switched off"
# the default file's Lantern part (a fresh install; an existing file is never rewritten - a missing key = its default). No '=' or key-colon
# in the comments: the config kit uncomments '#key=value' template lines.
LAN_CONFIG_LINES = [
    "# Lantern Accessory (0.5.4): while it sits in a player's Accessory Bag, that player glows like a torch (everyone sees it), and from",
    "# Unique up a hidden light above them that only they see lights farther - around them it stays about as bright as their glow. Set",
    "# line.Lantern to false to switch it off for everyone. lantern.glow.<rarity> is the light level on the wearer, 0-15 (11 is a torch,",
    "# 15 the brightest vanilla light, 0 no glow). lantern.reach.<rarity> is how many blocks around the wearer are lit, 0-64 (a torch",
    "# lights about 6). lantern.height is the highest the hidden light may go above the wearer, 8-160 blocks (it sits as low as the reach",
    "# allows). lantern.shareReach true shows the hidden light to everyone near the wearer too (their bits near it can glow brightly).",
    "%s=true" % LAN_SWITCH] + ["%s=%d" % kv for kv in zip(LAN_KEYS, LAN_DEF)] + ["%s=false" % LAN_SHARE_KEY]
# the Server Setup rows (category "lantern"; tools/CONFIG-CONTRACT.md row tuple)
LAN_ROWS = [
    (LAN_SWITCH, "Lantern line", "lantern", "bool", "true", "", "", "", "", "live",
     "Off = Lanterns light nothing for anyone; every Lantern light goes out within a second.",
     "field:AccDefs.LINE_LANTERN@config.properties:%s" % LAN_SWITCH)] + [
    (LAN_KEYS[_i], "%s: glow" % LAN_RARITIES[_i], "lantern", "int", str(LAN_DEF[_i]), str(LAN_MIN[_i]), str(LAN_MAX[_i]), "step=1", "",
     "live", "Light level on the wearer. 11 = a torch, 15 = the brightest vanilla light, 0 = none.",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[_i], LAN_KEYS[_i])) for _i in range(4)] + [
    (LAN_KEYS[4 + _i], "%s: reach" % LAN_RARITIES[_i], "lantern", "int", str(LAN_DEF[4 + _i]), str(LAN_MIN[4 + _i]), str(LAN_MAX[4 + _i]),
     "step=1", "blocks", "live", "Blocks lit around the wearer (a torch = 6); a hidden light only they see adds the rest.",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[4 + _i], LAN_KEYS[4 + _i])) for _i in range(4)] + [
    (LAN_KEYS[8], "Hidden light: highest", "lantern", "int", str(LAN_DEF[8]), str(LAN_MIN[8]), str(LAN_MAX[8]), "step=1", "blocks",
     "live,adv", "It sits as low as the reach allows, never higher than this (or the wearer's view distance).",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[8], LAN_KEYS[8])),
    (LAN_SHARE_KEY, "Others see the reach light", "lantern", "bool", "false", "", "", "", "", "live,adv",
     "On = players near a wearer see the hidden light too (their bits near it can glow brightly).",
     "field:AccDefs.LAN_SHARE@config.properties:%s" % LAN_SHARE_KEY)]
assert all(ord(_c) < 128 for _t in LAN_CONFIG_LINES + [LAN_FLAVOUR] for _c in _t)
assert not any("=" in _l for _l in LAN_CONFIG_LINES if _l.startswith("#")), "no template-looking comment lines"
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in LAN_ROWS), [_r[0] for _r in LAN_ROWS if len(_r[1]) > 40 or len(_r[10]) > 100]
assert len(LAN_ROWS) == 11 and LAN_CONFIG_LINES[-1] == "lantern.shareReach=false"


# ---- the light model (research/NightVision-Glare-Research.md 1.3 / 1.4; the Java twins in AccDefs: lanLight, lanMaxLevel, lanReach,
# lanSolve - same arithmetic, same iteration counts, so the build table below and the running server agree to the last bit)
def lan_light(level, d):
    """one channel's light at distance d (blocks) from a light of this level: 0.8 C (1 - 0.1 d / C)^1.5, C = level / 15, zero past the
    client's cut-off 0.635 x level and the shader's own zero 10 C"""
    import math as _m
    if level <= 0:
        return 0.0
    c = level / 15.0
    if d < 0.0:
        d = 0.0
    if d >= 0.635 * level or d >= 10.0 * c:
        return 0.0
    x = 1.0 - 0.1 * d / c
    return 0.8 * c * x * _m.sqrt(x)


def lan_maxlevel(dist, cap):
    """the highest level 0-255 whose light at dist is not above cap (the light only grows with the level)"""
    lo, hi = 0, 255
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if lan_light(mid, dist) <= cap:
            lo = mid
        else:
            hi = mid - 1
    return lo


def lan_reach(level, h):
    """how far from the wearer (blocks, at their feet level) a light of this level h blocks above the feet still lights (>= LAN_VIS)"""
    import math as _m
    if lan_light(level, h) < LAN_VIS:
        return 0.0
    lo, hi = 0.0, 400.0
    for _i in range(50):
        m = (lo + hi) * 0.5
        if lan_light(level, _m.sqrt(h * h + m * m)) >= LAN_VIS:
            lo = m
        else:
            hi = m
    return lo


def lan_cap(glow):
    """the brightest the helper may make anything near the wearer: the wearer's own glow at its brightest (a torch when no glow)"""
    return lan_light(glow if glow > 0 else LAN_TORCH, LAN_PD)


def lan_solve(glow, reach, hmax):
    """(height, level, reach reached) of the helper for one rarity: the LOWEST height whose cap-limited level reaches `reach`; the best
    reach under the cap and the height limit when nothing reaches it; (0, 0, the glow's own reach) when the glow alone is enough"""
    own = lan_reach(glow, 0.0)
    if reach <= own + 0.5:
        return 0, 0, own
    cap = lan_cap(glow)
    best = (0, 0, own)
    for h in range(LAN_MINH, hmax + 1):
        lv = lan_maxlevel(h - LAN_PZ, cap)
        if lv <= 0:
            continue
        r = lan_reach(lv, float(h))
        if r > best[2] + 1e-9:
            best = (h, lv, r)
        if r >= reach:
            return h, lv, r
    return best


def lan_key(level):
    """our GLOW as one int: radius byte LAN_SIG_R, then the torch tint at that level (red = level, green / blue = 10 / 11 and 9 / 11 of
    it, rounded) - the Java AccDefs.lanKey (the light ON the player: near the player every channel is fully lit, so the tint is the
    vanilla torch's warm fall-off)"""
    r = 1 if level < 1 else (255 if level > 255 else level)
    g, b = max(1, (r * 10 + 5) // 11), max(1, (r * 9 + 5) // 11)
    return (LAN_SIG_R << 24) | (r << 16) | (g << 8) | b


def lan_hkey(level):
    """the HELPER's light as one int: radius byte LAN_SIG_R, then red = green = blue = the level - the Java AccDefs.lanHKey. White because
    the client fades every channel on its own (LightCluster getChannelLightNEW(distance, Color.r / .g / .b): zero at 10 x channel / 15
    blocks): a torch-tinted helper 123 blocks up would light the ground with red only (review finding 1)"""
    lv = 1 if level < 1 else (255 if level > 255 else level)
    return (LAN_SIG_R << 24) | (lv << 16) | (lv << 8) | lv


def lan_rgb(key, d):
    """the client's light of each channel at d blocks from a light with this key - what the ground under a helper gets: per channel
    E = max(channel, radius byte), the light skipped past 0.635 x the brightest E, then the shader's getChannelLightNEW(0.1 d, E / 15) =
    0.8 C max(0, 1 - 0.1 d / C)^1.5 for EACH channel on its own"""
    rad = (key >> 24) & 255
    chans = [max((key >> s) & 255, rad) for s in (16, 8, 0)]
    if d >= 0.635 * max(chans):
        return (0.0, 0.0, 0.0)
    out = []
    for e in chans:
        c = e / 15.0
        x = 1.0 - 0.1 * d / c if c > 0.0 else 0.0
        out.append(0.8 * c * x * (x ** 0.5) if x > 0.0 else 0.0)
    return tuple(out)


LAN_TABLE = [None] + [lan_solve(LAN_DEF[_t - 1], LAN_DEF[3 + _t], LAN_DEF[8]) for _t in range(1, 5)]
assert [(_h, _l) for _h, _l, _r in LAN_TABLE[1:]] == [(0, 0), (14, 31), (38, 72), (123, 208)], LAN_TABLE
assert [round(_r, 1) for _h, _l, _r in LAN_TABLE[1:]] == [5.9, 12.3, 24.7, 48.1], LAN_TABLE
assert all(lan_light(_l, _h - LAN_PZ) <= lan_cap(LAN_TORCH) for _h, _l, _r in LAN_TABLE[2:]), "the brightness cap holds"
assert lan_key(LAN_TORCH) == (1 << 24) | (11 << 16) | (10 << 8) | 9, "the default glow is the torch's 11 / 10 / 9"
# finding 1: the ground under every default helper (straight below, and at the reach's edge) gets the same light on red, green and blue;
# the old torch tint gave Legendary ground green 0.04 / blue 0 against red 0.42 (a red disc)
for _h, _l, _r in LAN_TABLE[2:]:
    for _d in (float(_h), (_h * _h + (_r * 0.98) ** 2) ** 0.5):
        _w = lan_rgb(lan_hkey(_l), _d)
        assert _w[0] > 0.0 and _w[0] == _w[1] == _w[2], ("the helper light is not white on the ground", _h, _l, _d, _w)
_old = lan_rgb(lan_key(208), 123.0)
assert _old[0] > 0.4 and _old[1] < 0.1 * _old[0] and _old[2] == 0.0, ("the torch-tinted far light would be red", _old)
# the reach a rarity SHOWS: the glow's own reach when there is no helper (the glow alone may light more than a small row), else the
# row when it is reached, else what is reached (the Java AccDefs.lanShown)
LAN_SHOWN = [0] + [int(round(LAN_TABLE[_t][2])) if LAN_TABLE[_t][0] <= 0 else
                   (LAN_DEF[3 + _t] if LAN_TABLE[_t][2] >= LAN_DEF[3 + _t] else int(round(LAN_TABLE[_t][2]))) for _t in range(1, 5)]
assert LAN_SHOWN == [0, 6, 12, 24, 48], LAN_SHOWN
print("lantern: tier table (glow, helper level at height -> reach in blocks, a torch ~%.1f): %s" % (LAN_TABLE[1][2], " | ".join(
    "%s glow %d%s -> %.1f" % (LAN_RARITIES[_t - 1], LAN_DEF[_t - 1], (" + light %d at %d up" % (LAN_TABLE[_t][1], LAN_TABLE[_t][0]))
                              if LAN_TABLE[_t][0] else "", LAN_TABLE[_t][2]) for _t in range(1, 5))))
''' + s[_B:]

# the Python id mirror agrees: the retired Night Vision id keeps its id rules; the Lantern ids are word ids of their own family
rep('''# 0.5.3: the Night Vision id through the booster table's id rules (the Python mirror of AccDefs.tierOf / familyOf / isLegacy / modernOf)
assert NV_ID == "Skyy_Talisman_%s_%s" % (NV_ADMIN, ID_WORD[NV_TIER]) and DISPLAY[NV_TIER] == "Rare", NV_ID
assert py_tier(NV_ID) == NV_TIER and py_family(NV_ID) == NV_ADMIN and py_tail_tier(NV_ID) == -1 and not py_legacy(NV_ID) and py_modern(NV_ID) == NV_ID
assert NV_ADMIN not in [_b[0] for _b in BOOSTERS] + [_b[1] for _b in BOOSTERS] and NV_LINE not in [_b[2] for _b in BOOSTERS]
assert NV_ID not in LINE_IDS + OLD_IDS + LEGACY_IDS and not NV_ID.startswith("Skyy_Accessory_")
''', '''# 0.5.3: the Night Vision id through the booster table's id rules (the Python mirror of AccDefs.tierOf / familyOf / isLegacy / modernOf)
assert NV_ID == "Skyy_Talisman_%s_%s" % (NV_ADMIN, ID_WORD[NV_TIER]) and DISPLAY[NV_TIER] == "Rare", NV_ID
assert py_tier(NV_ID) == NV_TIER and py_family(NV_ID) == NV_ADMIN and py_tail_tier(NV_ID) == -1 and not py_legacy(NV_ID) and py_modern(NV_ID) == NV_ID
assert NV_ADMIN not in [_b[0] for _b in BOOSTERS] + [_b[1] for _b in BOOSTERS] and NV_LINE not in [_b[2] for _b in BOOSTERS]
assert NV_ID not in LINE_IDS + OLD_IDS + LEGACY_IDS and not NV_ID.startswith("Skyy_Accessory_")
# 0.5.4: the Lantern ids = the id words of each rarity, their own family (never a booster family / legacy / bench id)
assert LAN_IDS == ["Skyy_Talisman_%s_%s" % (LAN_FAM, ID_WORD[_t]) for _t in range(1, 5)], LAN_IDS
assert all(py_tier(_i) == _t + 1 and py_family(_i) == LAN_FAM and py_tail_tier(_i) == -1 and not py_legacy(_i) and py_modern(_i) == _i
           for _t, _i in enumerate(LAN_IDS))
assert LAN_FAM not in [_b[0] for _b in BOOSTERS] + [_b[1] for _b in BOOSTERS] + [NV_ADMIN] and LAN_LINE not in [_b[2] for _b in BOOSTERS]
assert not set(LAN_IDS) & set(LINE_IDS + OLD_IDS + LEGACY_IDS + [NV_ID])
''')

# the default file text: the Lantern part instead of the Night Vision part (a fresh install only - an existing file is never appended to)
rep('''] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + NV_CONFIG_LINES + [""])   # 0.5.3: + Night Vision
''', '''] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + LAN_CONFIG_LINES + [""])   # 0.5.4: + the Lantern (0.5.3's Night Vision part is gone)
''')

# ---------------------------------------------------------------------------------------------------------------- AccDefs
_A = s.index("# 0.5.3 NIGHT VISION: its id, names, rarity, acc:defs source word, defaults, the server-wide switch and the light (the kit's field: rows),")
_B = s.index('dfs.addMethod(CtNewMethod.make("""\npublic static boolean isAccessory(String id) {')
s = s[:_A] + r'''# 0.5.3 NIGHT VISION, RETIRED in 0.5.4: its id and texts (isRetired, retiredWhy / retiredChat, pretty, the bag row, the give refusal)
dfs.addField(CtField.make('public static final String NV_ID = "%s";' % NV_ID, dfs))
dfs.addField(CtField.make('public static final String NV_ADMIN = "%s";' % NV_ADMIN, dfs))
dfs.addField(CtField.make('public static final String NV_LINE = "%s";' % NV_LINE, dfs))
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
# the old /accessories givetier names (NightVision, Night_Vision, Night-Vision, NV) - answered with the retirement
JM(dfs, r"""
public static boolean isNvName(String w) {
  if (w == null) return false;
  String x = w.trim();
  return x.equalsIgnoreCase(NV_ADMIN) || x.equalsIgnoreCase("Night_Vision") || x.equalsIgnoreCase("Night-Vision") || x.equalsIgnoreCase("NV");
}""")
# 0.5.4 THE LANTERN: ids, names, the live settings (the kit's field: rows), the tier table (lanTable: rebuilt when a setting changed), the
# light model and our light's int key (radius byte LAN_SIG_R + the torch tint). Compiled before every caller (javassist: method order).
dfs.addField(CtField.make('public static final String LAN_FAM = "%s";' % LAN_FAM, dfs))
dfs.addField(CtField.make('public static final String LAN_ADMIN = "%s";' % LAN_ADMIN, dfs))
dfs.addField(CtField.make('public static final String LAN_LINE = "%s";' % LAN_LINE, dfs))
dfs.addField(CtField.make('public static final String LAN_SRC = "%s";' % LAN_SRC, dfs))
dfs.addField(CtField.make('public static final String[] LAN_IDS = new String[] { %s };' % ", ".join('"%s"' % _i for _i in LAN_IDS), dfs))
dfs.addField(CtField.make('public static final int LAN_TORCH = %d;' % LAN_TORCH, dfs))
dfs.addField(CtField.make('public static final int LAN_SIG_R = %d;' % LAN_SIG_R, dfs))
dfs.addField(CtField.make('public static final double LAN_VIS = %r;' % LAN_VIS, dfs))
dfs.addField(CtField.make('public static final double LAN_PZ = %r;' % LAN_PZ, dfs))
dfs.addField(CtField.make('public static final double LAN_PD = %r;' % LAN_PD, dfs))
dfs.addField(CtField.make('public static final int LAN_MINH = %d;' % LAN_MINH, dfs))
dfs.addField(CtField.make('public static final int[] LAN_DEF = new int[] { %s };' % ", ".join(str(_x) for _x in LAN_DEF), dfs))
dfs.addField(CtField.make('public static volatile boolean LINE_LANTERN = true;', dfs))   # config row line.Lantern
dfs.addField(CtField.make('public static volatile boolean LAN_SHARE = false;', dfs))     # config row lantern.shareReach (fix round)
dfs.addField(CtField.make('public static final double LAN_EPS = %r;' % LAN_EPS, dfs))
dfs.addField(CtField.make('public static final int LAN_VIEW_MARGIN = %d;' % LAN_VIEW_MARGIN, dfs))
dfs.addField(CtField.make('public static final double LAN_MOVE_DIV = %r;' % LAN_MOVE_DIV, dfs))
dfs.addField(CtField.make('public static final double LAN_MOVE_MIN = %r;' % LAN_MOVE_MIN, dfs))
dfs.addField(CtField.make('public static final double LAN_MOVE_MAX = %r;' % LAN_MOVE_MAX, dfs))
for _nf, _nd in zip(LAN_FIELDS, LAN_DEF):
    dfs.addField(CtField.make('public static volatile int %s = %d;' % (_nf, _nd), dfs))      # config rows lantern.*
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_H = new int[5];', dfs))      # per rarity: the helper's height (0 = none)
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_L = new int[5];', dfs))      # per rarity: the helper's light level
dfs.addField(CtField.make('public static volatile float[] LAN_TAB_R = new float[5];', dfs))  # per rarity: the reach it reaches (blocks)
dfs.addField(CtField.make('public static volatile String LAN_SIG = "";', dfs))                # the settings the table was built from
dfs.addField(CtField.make('public static volatile int LAN_EPOCH = 0;', dfs))                  # +1 per rebuild (players decide again)
JM(dfs, r"""
public static double lanLight(int level, double dist) {
  if (level <= 0) return 0.0;
  double c = (double) level / 15.0;
  double d = dist < 0.0 ? 0.0 : dist;
  if (d >= 0.635 * (double) level || d >= 10.0 * c) return 0.0;
  double x = 1.0 - 0.1 * d / c;
  return 0.8 * c * x * Math.sqrt(x);
}""")
JM(dfs, r"""
public static int lanMaxLevel(double dist, double cap) {
  int lo = 0;
  int hi = 255;
  while (lo < hi) {
    int mid = (lo + hi + 1) / 2;
    if (lanLight(mid, dist) <= cap) lo = mid; else hi = mid - 1;
  }
  return lo;
}""")
JM(dfs, r"""
public static double lanReach(int level, double h) {
  if (lanLight(level, h) < LAN_VIS) return 0.0;
  double lo = 0.0;
  double hi = 400.0;
  for (int i = 0; i < 50; i++) {
    double m = (lo + hi) * 0.5;
    if (lanLight(level, Math.sqrt(h * h + m * m)) >= LAN_VIS) lo = m; else hi = m;
  }
  return lo;
}""")
JM(dfs, r"""
public static int lanGlow(int t) {
  switch (t) {
    case 1: return LAN_GLOW1;
    case 2: return LAN_GLOW2;
    case 3: return LAN_GLOW3;
    case 4: return LAN_GLOW4;
    default: return 0;
  }
}""")
JM(dfs, r"""
public static int lanReachOf(int t) {
  switch (t) {
    case 1: return LAN_REACH1;
    case 2: return LAN_REACH2;
    case 3: return LAN_REACH3;
    case 4: return LAN_REACH4;
    default: return 0;
  }
}""")
JM(dfs, r"""
public static double lanCap(int t) {
  int g = lanGlow(t);
  return lanLight(g > 0 ? g : LAN_TORCH, LAN_PD);
}""")
# one rarity's helper: the LOWEST height (5 .. lantern.height) whose cap-limited level reaches the reach row; the best reach when none
# does; none when the glow alone reaches it. out = { height, level } and the reach reached in r[t]
JM(dfs, r"""
public static void lanSolve(int t, int[] hh, int[] ll, float[] rr) {
  int g = lanGlow(t);
  double own = lanReach(g, 0.0);
  int want = lanReachOf(t);
  hh[t] = 0;
  ll[t] = 0;
  rr[t] = (float) own;
  if ((double) want <= own + 0.5) return;
  double cap = lanCap(t);
  int hmax = LAN_HEIGHT;
  double best = own;
  for (int h = LAN_MINH; h <= hmax; h++) {
    int lv = lanMaxLevel((double) h - LAN_PZ, cap);
    if (lv <= 0) continue;
    double r = lanReach(lv, (double) h);
    if (r > best + 0.000000001) { best = r; hh[t] = h; ll[t] = lv; rr[t] = (float) r; }
    if (r >= (double) want) { hh[t] = h; ll[t] = lv; rr[t] = (float) r; return; }
  }
}""")
JM(dfs, r"""
public static synchronized void lanTable() {
  String sig = LAN_GLOW1 + "," + LAN_GLOW2 + "," + LAN_GLOW3 + "," + LAN_GLOW4 + "," + LAN_REACH1 + "," + LAN_REACH2 + "," + LAN_REACH3 + "," + LAN_REACH4 + "," + LAN_HEIGHT;
  if (sig.equals(LAN_SIG)) return;
  int[] hh = new int[5];
  int[] ll = new int[5];
  float[] rr = new float[5];
  for (int t = 1; t <= 4; t++) lanSolve(t, hh, ll, rr);
  LAN_TAB_H = hh;
  LAN_TAB_L = ll;
  LAN_TAB_R = rr;
  LAN_SIG = sig;
  LAN_EPOCH = LAN_EPOCH + 1;
}""")
JM(dfs, r"""
public static int lanKey(int level) {
  int r = level < 1 ? 1 : (level > 255 ? 255 : level);
  int g = (r * 10 + 5) / 11;
  int b = (r * 9 + 5) / 11;
  if (g < 1) g = 1;
  if (b < 1) b = 1;
  return (LAN_SIG_R << 24) | (r << 16) | (g << 8) | b;
}""")
# the helper's light: WHITE (red = green = blue = the level) - the client fades each channel on its own, a torch tint would reach the ground
# red only (review finding 1); the glow on the player keeps the torch tint (lanKey)
JM(dfs, r"""
public static int lanHKey(int level) {
  int l = level < 1 ? 1 : (level > 255 ? 255 : level);
  return (LAN_SIG_R << 24) | (l << 16) | (l << 8) | l;
}""")
JM(dfs, LANJ(r"""
public static @CLT@ lanColor(int k) {
  return new @CLT@((byte) (k >>> 24), (byte) (k >>> 16), (byte) (k >>> 8), (byte) k);
}"""))
JM(dfs, LANJ(r"""
public static int lanKeyOf(@CLT@ c) {
  if (c == null) return 0;
  return ((c.radius & 255) << 24) | ((c.red & 255) << 16) | ((c.green & 255) << 8) | (c.blue & 255);
}"""))
# OUR light (radius byte LAN_SIG_R + the exact torch tint of its red level): another mod's or the builder tool's light never matches
JM(dfs, LANJ(r"""
public static boolean lanOurs(@CLT@ c) {
  if (c == null || (c.radius & 255) != LAN_SIG_R || (c.red & 255) < 1) return false;
  return lanKeyOf(c) == lanKey(c.red & 255);
}"""))
# the reach a rarity shows (bag page, /accessories lines): what the glow alone lights when there is no helper (a reach row below the glow's
# own ~6 blocks no longer reads "about 0 blocks"), else the reach row when it is reached, else what is reached (rounded)
JM(dfs, r"""
public static int lanShown(int t) {
  if (t < 1 || t > 4) return 0;
  lanTable();
  float r = LAN_TAB_R[t];
  if (LAN_TAB_H[t] <= 0) return Math.round(r);
  int want = lanReachOf(t);
  if (r >= (float) want) return want;
  return Math.round(r);
}""")
JM(dfs, r"""
public static String lanGlowText(int t) {
  int g = lanGlow(t);
  if (g <= 0) return "no glow";
  if (g == LAN_TORCH) return "glows like a torch";
  return "glows at light " + g + " (a torch is " + LAN_TORCH + ")";
}""")
JM(dfs, r"""
public static String lanText(int t) {
  if (t < 1 || t > 4) return "";
  lanTable();
  return lanGlowText(t) + ", lights about " + lanShown(t) + " blocks around you";
}""")
# the bag page row (short: one 422 px line at 16 px): "glows like a torch" (no helper) / "torch glow, lights about 48 blocks"
JM(dfs, r"""
public static String lanRow(int t) {
  if (t < 1 || t > 4) return "";
  lanTable();
  int g = lanGlow(t);
  if (LAN_TAB_H[t] <= 0) {
    if (g <= 0) return "no light";
    if (g == LAN_TORCH) return "glows like a torch";
    return "glows at light " + g;
  }
  String gs = "";
  if (g == LAN_TORCH) gs = "torch glow, ";
  else if (g > 0) gs = "glow " + g + ", ";
  return gs + "lights about " + lanShown(t) + " blocks";
}""")
''' + s[_B:]
# the Lantern token resolver (used by the AccDefs methods above and the Lantern classes below)
rep('''def JM(cls, src):
    cls.addMethod(CtNewMethod.make(JT(src), cls))
''', '''def JM(cls, src):
    cls.addMethod(CtNewMethod.make(JT(src), cls))
# 0.5.4: the Lantern class tokens (@DLC@ ...); JT() resolves the others
_LANT = {"DLC": DLC, "CLT": CLT, "TCO": TCO, "NID": NID, "INT": INT_, "DES": DES, "DTH": DTH, "NSR": NSR, "HLD": HLD, "CRG": CRG,
         "CTY": CTY, "RTY": RTY, "ARS": ARS, "RRS": RRS, "ESR": ESR, "CSR": CSR, "ARC": ARC, "V3D": V3D,
         "EVW": EVW, "ETR": ETR, "CVS": CVS, "SGR": SGR, "SDP": SDP, "ORD": ORD, "HPM": HPM}   # + the fix round's AccLanternHide


def LANJ(src):
    for _k, _v in _LANT.items():
        src = src.replace("@%s@" % _k, _v)
    return src
''')

# a retired Night Vision is a retired accessory (rarityOf 0, never counts, Equip refuses it, acc:fn:has never answers true)
rep('''public static boolean isRetired(String id) {
  if (id == null || isTalisman(id) || OMNI.equals(id)) return false;
''', '''public static boolean isRetired(String id) {
  if (NV_ID.equals(id)) return true;   // 0.5.4: Night Vision - replaced by the Lantern
  if (id == null || isTalisman(id) || OMNI.equals(id)) return false;
''')
rep('''public static String retiredWhy(String id) {
  String b = benchOf(id);
''', '''public static String retiredWhy(String id) {
  if (NV_ID.equals(id)) return NV_WHY;   // 0.5.4
  String b = benchOf(id);
''')
rep('''public static String retiredChat(String id) {
  String b = benchOf(id);
''', '''public static String retiredChat(String id) {
  if (NV_ID.equals(id)) return NV_CHAT;   // 0.5.4
  String b = benchOf(id);
''')
# the retirement texts as fields (compiled with the other Night Vision fields above; the methods above read them)
rep('''dfs.addField(CtField.make('public static final String NV_LINE = "%s";' % NV_LINE, dfs))
''', '''dfs.addField(CtField.make('public static final String NV_LINE = "%s";' % NV_LINE, dfs))
dfs.addField(CtField.make("public static final String NV_WHY = %s;" % jlit(NV_WHY), dfs))
dfs.addField(CtField.make("public static final String NV_CHAT = %s;" % jlit(NV_CHAT), dfs))
dfs.addField(CtField.make("public static final String NV_ROW = %s;" % jlit(NV_ROW), dfs))
dfs.addField(CtField.make("public static final String NV_GIVE = %s;" % jlit(NV_GIVE), dfs))
''')
# the Lantern id rules (after groupOf: they need isTalisman / familyOf / isLegacy / tierOf)
rep('''# highest tier per line (index = FAMILIES) among the bag slots - ONLY THE HIGHEST RARITY OF A LINE COUNTS (a duplicate that slipped in
''', '''# 0.5.4 the Lantern: one of its four ids (a word id of family Lantern), the best rarity in a bag (0 = none), the givetier names
JM(dfs, r"""
public static boolean isLantern(String id) {
  return isTalisman(id) && LAN_FAM.equals(familyOf(id)) && !isLegacy(id) && tailTier(id) <= 0;
}""")
JM(dfs, r"""
public static boolean isLanternId(String id) {
  if (id == null) return false;
  for (int i = 0; i < LAN_IDS.length; i++) if (LAN_IDS[i].equals(id)) return true;
  return false;
}""")
JM(dfs, r"""
public static int lanBest(String[] s) {
  int best = 0;
  if (s == null) return 0;
  for (int i = 0; i < s.length; i++) {
    if (!isLantern(s[i])) continue;
    int t = tierOf(s[i]);
    if (t > 4) t = 4;
    if (t > best) best = t;
  }
  return best;
}""")
JM(dfs, r"""
public static boolean isLanName(String w) {
  if (w == null) return false;
  String x = w.trim();
  return x.equalsIgnoreCase(LAN_ADMIN) || x.equalsIgnoreCase("Lanterns");
}""")
# highest tier per line (index = FAMILIES) among the bag slots - ONLY THE HIGHEST RARITY OF A LINE COUNTS (a duplicate that slipped in
''')
# the bag page: the Lantern row after the booster lines, then a note for a retired Night Vision still in the bag
rep('''  if (hasNv(s) && n < BONUS_MAX) {   // 0.5.3: Night Vision - its own line, after the booster lines
    out[n * 2] = NV_LINE;
    out[n * 2 + 1] = LINE_NIGHTVISION ? nvOnText() : "switched off";
    n++;
  }
  return out;
}""")
''', '''  int lt = lanBest(s);   // 0.5.4: the Lantern - its own line, after the booster lines
  if (lt > 0 && n < BONUS_MAX) {
    out[n * 2] = LAN_LINE;
    out[n * 2 + 1] = LINE_LANTERN ? lanRow(lt) : "switched off";
    n++;
  }
  if (hasNv(s) && n < BONUS_MAX) {   // 0.5.4: a retired Night Vision still in the bag
    out[n * 2] = NV_LINE;
    out[n * 2 + 1] = NV_ROW;
    n++;
  }
  return out;
}""")
''')
# names: "<Rarity> Lantern Accessory"; the retired Night Vision says so (the bench accessories' "- retired")
rep('''  if (NV_ID.equals(id)) return NV_LINE + " Accessory";   // 0.5.3: one rarity, so no rarity word in its name
''', '''  if (NV_ID.equals(id)) return NV_LINE + " Accessory - retired";   // 0.5.4: replaced by the Lantern
  if (isLantern(id)) {   // 0.5.4: "<Rarity> Lantern Accessory"
    int lr = rarityOf(id);
    return lr >= 1 && lr < DISPLAY.length ? DISPLAY[lr] + " " + LAN_LINE + " Accessory" : LAN_LINE + " Accessory";
  }
''')
rep('''  if (NV_ID.equals(id)) return NV_LINE + " Accessory";   // 0.5.3
''', '''  if (NV_ID.equals(id)) return NV_LINE + " Accessory";   // 0.5.3 (0.5.4: retired - Equip answers with retiredWhy first)
  if (isLantern(id)) return LAN_LINE + " Accessory";   // 0.5.4
''')
# acc:defs: four Lantern records instead of the Night Vision record
rep('''  if (sb.length() > 0) sb.append(',');   // 0.5.3: Night Vision - the record of its one rarity
  sb.append(NV_ADMIN).append(':').append(NV_ADMIN).append(':').append(NV_TIER).append(':').append(NV_ID);
  sb.append(':').append(DISPLAY[NV_TIER]).append(':').append(AP[NV_TIER]).append(':').append(NV_SRC);
  return sb.toString();
''', '''  for (int t = 1; t <= 4; t++) {   // 0.5.4: the Lantern - one record per rarity (0.5.3's Night Vision record is gone)
    if (sb.length() > 0) sb.append(',');
    sb.append(LAN_ADMIN).append(':').append(LAN_FAM).append(':').append(t).append(':').append(LAN_IDS[t - 1]);
    sb.append(':').append(DISPLAY[t]).append(':').append(AP[t]).append(':').append(LAN_SRC);
  }
  return sb.toString();
''')
# /accessories lines: the Lantern line instead of the Night Vision line
rep('''  StringBuilder nb = new StringBuilder();   // 0.5.3: Night Vision - one rarity, its own line
  nb.append(NV_LINE).append(" Accessory (").append(NV_ADMIN).append(")");
  if (!LINE_NIGHTVISION) nb.append(" - SWITCHED OFF on this server");
  nb.append(": ").append(DISPLAY[NV_TIER]).append(" only - ").append(nvLinesText());
  out.add(nb.toString());
  if (ids) out.add("    ids: " + NV_ID);
''', '''  StringBuilder nb = new StringBuilder();   // 0.5.4: the Lantern - its four rarities (0.5.3's Night Vision line is gone: retired)
  nb.append(LAN_LINE).append(" Accessory (").append(LAN_ADMIN).append(")");
  if (!LINE_LANTERN) nb.append(" - SWITCHED OFF on this server");
  nb.append(": ");
  for (int t = 1; t <= 4; t++) {
    if (t > 1) nb.append(" | ");
    nb.append(DISPLAY[t]).append(' ').append(lanText(t));
  }
  nb.append(LAN_SHARE ? " - everyone sees the glow and the far light" : " - everyone sees your glow, only you see the far light");
  out.add(nb.toString());
  if (ids) {
    StringBuilder lb = new StringBuilder("    ids: ");
    for (int t = 1; t <= 4; t++) { if (t > 1) lb.append(" / "); lb.append(LAN_IDS[t - 1]); }
    out.add(lb.toString());
  }
''')

# ---------------------------------------------------------------------------------------------------------------- AccStore
rep('''# 0.5.3: uuid -> the bag changed since Night Vision last looked (save, join, profile switch): AccNv.step decides on the next world tick
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap NVPOKE = new java.util.concurrent.ConcurrentHashMap();", st_))
''', '''# 0.5.4: uuid -> the bag changed since the Lantern last looked (save, join, profile switch): AccLantern.step decides on the next world tick
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LPOKE = new java.util.concurrent.ConcurrentHashMap();", st_))
''')
rep('''    NVPOKE.put(u, Boolean.TRUE);   // 0.5.3: Night Vision looks at this bag on the next world tick
''', '''    LPOKE.put(u, Boolean.TRUE);   // 0.5.4: the Lantern looks at this bag on the next world tick
''')
# acc:tal lists the accessories that count: a retired one (Night Vision) is left out, like the retired bench accessories in acc:has
rep('''      if (s[i] == null || !{PKG}.AccDefs.isTalisman(s[i])) continue;
''', '''      if (s[i] == null || !{PKG}.AccDefs.isTalisman(s[i]) || {PKG}.AccDefs.isRetired(s[i])) continue;   // 0.5.4: not a retired one
''')

# ---------------------------------------------------------------------------------------------------------------- AccCfg (the loader)
rep('''# 0.5.3 Night Vision: the switch and the light keys, their maximums (minimum 0); defaults in AccDefs.NV_DEF
cfg_.addField(CtField.make('public static final String NV_SWITCH = "%s";' % NV_SWITCH, cfg_))
cfg_.addField(CtField.make("public static final String[] NV_KEYS = new String[] { %s };" % jstrs(NV_KEYS), cfg_))
cfg_.addField(CtField.make("public static final int[] NV_MAX = new int[] { %s };" % ", ".join(str(_x) for _x in NV_MAX), cfg_))
''', '''# 0.5.4 the Lantern: the switch and the keys with their bounds; defaults in AccDefs.LAN_DEF (0.5.3's Night Vision keys are ignored)
cfg_.addField(CtField.make('public static final String LAN_SWITCH = "%s";' % LAN_SWITCH, cfg_))
cfg_.addField(CtField.make('public static final String LAN_SHARE_KEY = "%s";' % LAN_SHARE_KEY, cfg_))   # fix round
cfg_.addField(CtField.make("public static final String[] LAN_KEYS = new String[] { %s };" % jstrs(LAN_KEYS), cfg_))
cfg_.addField(CtField.make("public static final int[] LAN_MIN = new int[] { %s };" % ", ".join(str(_x) for _x in LAN_MIN), cfg_))
cfg_.addField(CtField.make("public static final int[] LAN_MAX = new int[] { %s };" % ", ".join(str(_x) for _x in LAN_MAX), cfg_))
''')
rep('''  boolean nvOn = boolIn(p.getProperty(NV_SWITCH), true, NV_SWITCH);   // 0.5.3: Night Vision - the switch and the light (a missing key = its default)
  int[] nvv = new int[NV_KEYS.length];
  for (int q = 0; q < NV_KEYS.length; q++) nvv[q] = intIn(p.getProperty(NV_KEYS[q]), @PKG@.AccDefs.NV_DEF[q], 0, NV_MAX[q], NV_KEYS[q]);
''', '''  boolean lanOn = boolIn(p.getProperty(LAN_SWITCH), true, LAN_SWITCH);   // 0.5.4: the Lantern - the switch and its numbers (a missing key = its default)
  boolean lanShare = boolIn(p.getProperty(LAN_SHARE_KEY), false, LAN_SHARE_KEY);   // the fix round: the reach light shown to everyone (off)
  int[] lanv = new int[LAN_KEYS.length];
  for (int q = 0; q < LAN_KEYS.length; q++) lanv[q] = intIn(p.getProperty(LAN_KEYS[q]), @PKG@.AccDefs.LAN_DEF[q], LAN_MIN[q], LAN_MAX[q], LAN_KEYS[q]);
''')
rep('''  @PKG@.AccDefs.LINE_NIGHTVISION = nvOn;   // 0.5.3
  @PKG@.AccDefs.NV_RADIUS = nvv[0];
  @PKG@.AccDefs.NV_RED = nvv[1];
  @PKG@.AccDefs.NV_GREEN = nvv[2];
  @PKG@.AccDefs.NV_BLUE = nvv[3];
  @PKG@.AccDefs.NV_REFRESH = nvv[4];
''', '''  @PKG@.AccDefs.LINE_LANTERN = lanOn;   // 0.5.4
  @PKG@.AccDefs.LAN_SHARE = lanShare;
@SETLAN@
''')
rep('''  if (!nvOn) res = res + ", Night Vision switched off";   // 0.5.3
  if (nvv[0] != @PKG@.AccDefs.NV_DEF[0] || nvv[1] != @PKG@.AccDefs.NV_DEF[1] || nvv[2] != @PKG@.AccDefs.NV_DEF[2] || nvv[3] != @PKG@.AccDefs.NV_DEF[3]) res = res + ", Night Vision light " + nvv[0] + "," + nvv[1] + "," + nvv[2] + "," + nvv[3];
  if (nvv[4] != @PKG@.AccDefs.NV_DEF[4]) res = res + (nvv[4] == 0 ? ", Night Vision light sent only when needed" : ", Night Vision light sent again every " + nvv[4] + " s");
''', '''  if (!lanOn) res = res + ", Lantern switched off";   // 0.5.4
  if (lanShare) res = res + ", Lantern reach light shown to everyone";
  StringBuilder lc = new StringBuilder();
  for (int q = 0; q < LAN_KEYS.length; q++) if (lanv[q] != @PKG@.AccDefs.LAN_DEF[q]) lc.append(lc.length() > 0 ? ", " : "").append(LAN_KEYS[q]).append('=').append(lanv[q]);
  if (lc.length() > 0) res = res + ", Lantern numbers custom (" + lc.toString() + ")";
''')
rep('''        .replace("@SETLINES@", "\\n".join("  %s.AccDefs.LINE_%s = on[%d];" % (PKG, b[1].upper(), i) for i, b in enumerate(BOOSTERS)))
''', '''        .replace("@SETLINES@", "\\n".join("  %s.AccDefs.LINE_%s = on[%d];" % (PKG, b[1].upper(), i) for i, b in enumerate(BOOSTERS))) \\
        .replace("@SETLAN@", "\\n".join("  %s.AccDefs.%s = lanv[%d];" % (PKG, f, i) for i, f in enumerate(LAN_FIELDS)))   # 0.5.4
''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup
rep('''CFG_CATS = [("bag", "Accessory Bag"), ("boosters", "Boosters"), ("nightvision", "Night Vision")]   # 0.5.3: + Night Vision
''', '''CFG_CATS = [("bag", "Accessory Bag"), ("boosters", "Boosters"), ("lantern", "Lantern")]   # 0.5.4: Lantern (0.5.3's Night Vision is retired)
''')
rep('''      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS] + NV_ROWS   # 0.5.3: + Night Vision
''', '''      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS] + LAN_ROWS   # 0.5.4: + the Lantern
''')

# ---------------------------------------------------------------------------------------------------------------- the admin give
rep('''  if (@PKG@.AccDefs.NV_ID.equals(id)) return null;   // 0.5.3: Night Vision (admin give only)
''', '''  if (@PKG@.AccDefs.isLanternId(id)) return null;   // 0.5.4: the four Lantern rarities
  if (@PKG@.AccDefs.NV_ID.equals(id)) return @PKG@.AccDefs.NV_GIVE;   // 0.5.4: Night Vision is retired
''')
rep('''    int li = @PKG@.AccDefs.lineOf(tk[1]);
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
''', '''    int li = @PKG@.AccDefs.lineOf(tk[1]);
    boolean lnl = li < 0 && @PKG@.AccDefs.isLanName(tk[1]);   // 0.5.4: the Lantern - its own line, Normal to Legendary
    if (li < 0 && !lnl && @PKG@.AccDefs.isNvName(tk[1])) { msg(pr, @PKG@.AccDefs.NV_GIVE); return; }   // 0.5.4: Night Vision is retired
    if (li < 0 && !lnl) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < @PKG@.AccDefs.LINE_ADMIN.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.LINE_ADMIN[i]); }
      sb.append(", ").append(@PKG@.AccDefs.LAN_ADMIN);   // 0.5.4
      msg(pr, "unknown line - use one of: " + sb.toString());
      return;
    }
    int t = @PKG@.AccDefs.rarityIndex(tk[2]);
    if (t < 1) { msg(pr, "unknown rarity - use Normal, Unique, Rare, Legendary or 1 to 4"); return; }
    id = lnl ? @PKG@.AccDefs.LAN_IDS[t - 1] : @PKG@.AccDefs.idOf(li, t);
''')
rep('''  if (u == null || !(@PKG@.AccDefs.isBoosterId(id) || @PKG@.AccDefs.NV_ID.equals(id)) || n < 1 || n > 64) return 0;   // 0.5.3: + Night Vision
''', '''  if (u == null || !(@PKG@.AccDefs.isBoosterId(id) || @PKG@.AccDefs.isLanternId(id)) || n < 1 || n > 64) return 0;   // 0.5.4: + the Lantern (Night Vision: retired)
''')

# ---------------------------------------------------------------------------------------------------------------- AccNv -> the Lantern (before AccTick)
_A = s.index("# ================= 0.5.3 AccNv: THE NIGHT VISION LIGHT (the logic; AccNightVision.tick only reads the engine components) =================")
_B = s.index('tick.addInterface(pool.get("java.lang.Runnable"))\n')
s = s[:_A] + r'''# ================= 0.5.4 THE LANTERN (tools/acc_0_5_4_patch.py): AccLanternMark (the helper's marker component) + its Supplier, AccLantern
# (state + logic; the systems AccLanternSys / AccLanternHelp / AccLanternHide only read the engine components and call it) =================
# AccLanternMark: our marker on every helper entity = its owner's uuid. Registered without a codec (ComponentRegistryProxy.registerComponent
# (Class, Supplier)), on an entity that is NonSerialized anyway: never saved. AccLanternHelp ticks every entity that carries it.
lmk.addInterface(pool.get(COMP))
JF(lmk, "public java.util.UUID owner;")
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark() { this.owner = null; }", lmk))
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark(java.util.UUID u) { this.owner = u; }", lmk))
JM(lmk, LANJ(r"""
public com.hypixel.hytale.component.Component clone() {
  return new @PKG@.AccLanternMark(this.owner);
}"""))
lms.addInterface(pool.get("java.util.function.Supplier"))
lms.addConstructor(CtNewConstructor.make("public AccLanternMarkSup() { }", lms))
JM(lms, r"""
public Object get() {
  return new @PKG@.AccLanternMark();
}""")
# AccLantern. Component types are bound ONCE in setup() (bind(); T_MARK from registerComponent) and never looked up per tick - so the
# harness runs this exact code on its own engine ComponentRegistry / Store with its own types (section Q).
# State (all uuid keys, world threads write their own players, AccTick prunes players who left, shutdown clears): CLK float[]{seconds
# since the last decision}; WANT int[]{rarity, glow key (0 = none), helper height, helper level, dead 0/1, table epoch} (absent = nothing
# wanted); HELPER the helper's Ref (pending until its CommandBuffer runs); HSTATE int[]{ticks since spawn, seen valid, light key on it};
# OWNER the player's current entity Ref (AccLanternHelp keeps a helper only while this is valid, in the helper's own store, and the helper
# is the recorded one); HY long[]{cx, cz, feet section, target section, chosen section, ticks} the section check; SPAWNT long[]{last
# spawn ms, spawns in the window, window start ms} the spawn limit.
for _f in ("T_PR", "T_TC", "T_DL", "T_NID", "T_INT", "T_DES", "T_DEATH", "T_MARK", "T_EV"):   # T_EV: the EntityViewer (fix round)
    JF(lan, LANJ("public static volatile @CTY@ %s;" % _f))
JF(lan, LANJ("public static volatile @RTY@ R_TIME;"))
for _f in ("CLK", "WANT", "HELPER", "HSTATE", "OWNER", "HY", "SPAWNT"):
    JF(lan, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
# HIDDEN: helpers taken out of other viewers' visible sets (AccLanternHide); CLAMPED: helpers held inside the wearer's view radius
for _f in ("GLOW_ON", "GLOW_SET", "GLOW_OFF", "FOREIGN", "SPAWNS", "HREMOVES", "ORPHANS", "MOVES", "GONE", "LIMITED", "RELIT", "HIDDEN",
           "CLAMPED"):
    JF(lan, "public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _f)
JF(lan, "public static boolean LIMIT_WARNED = false;")
lan.addField(CtField.make("public static final double TOP_Y = %r;" % LAN_TOP, lan))
lan.addField(CtField.make("public static final double BOTTOM_Y = %r;" % LAN_BOTTOM, lan))
lan.addField(CtField.make("public static final float DESPAWN_S = %rf;" % LAN_DESPAWN, lan))
lan.addField(CtField.make("public static final int SECTIONS = 10;", lan))
JM(lan, LANJ(r"""
public static void bind() {
  T_PR = @PR@.getComponentType();
  T_TC = @TCO@.getComponentType();
  T_DL = @DLC@.getComponentType();
  T_NID = @NID@.getComponentType();
  T_INT = @INT@.getComponentType();
  T_DES = @DES@.getComponentType();
  T_DEATH = @DTH@.getComponentType();
  T_EV = @EVW@.getComponentType();
  R_TIME = @TMR@.getResourceType();
}"""))
JM(lan, r"""
public static float[] clk(java.util.UUID u) {
  float[] c = (float[]) CLK.get(u);
  if (c == null) { c = new float[] { 1.0f }; CLK.put(u, c); }
  return c;
}""")
JM(lan, r"""
public static int[] hstate(java.util.UUID u) {
  int[] h = (int[]) HSTATE.get(u);
  if (h == null) { h = new int[] { 0, 0, 0 }; HSTATE.put(u, h); }
  return h;
}""")
# the world of an entity store (null for a store that is not a world's - the harness's own stores: no section checks there)
JM(lan, LANJ(r"""
public static @WLD@ worldOf(@ST@ store) {
  if (store == null) return null;
  Object e = store.getExternalData();
  if (e instanceof @ESR@) return ((@ESR@) e).getWorld();
  return null;
}"""))
JM(lan, LANJ(r"""
public static int netId(@ST@ store) {
  Object e = store.getExternalData();
  if (e instanceof @ESR@) return ((@ESR@) e).takeNextNetworkId();
  return 0;
}"""))
# a section the helper may go into: loaded (the ChunkStore has its ref) AND ticking (no NonTicking component) - UpdateLocationSystems
# removes an entity moved into a missing section and parks one moved into a non-ticking section
JM(lan, LANJ(r"""
public static boolean sectionOk(@WLD@ w, int cx, int cy, int cz) {
  if (cy < 0 || cy >= SECTIONS) return false;
  if (w == null) return true;
  @CSR@ cs = w.getChunkStore();
  if (cs == null) return false;
  @REF@ sec = cs.getChunkSectionReference(cx, cy, cz);
  if (sec == null || !sec.isValid()) return false;
  @ST@ ss = cs.getStore();
  if (ss == null) return false;
  @ARC@ a = ss.getArchetype(sec);
  return a != null && !a.contains(ss.getRegistry().getNonTickingComponentType());
}"""))
# the ok sections from the feet section up to the target section, one bit each (the feet section always counts: the player is in it)
JM(lan, LANJ(r"""
public static long sectionMask(@WLD@ w, int cx, int cz, int sy0, int syt) {
  long m = 0L;
  if (sy0 >= 0 && sy0 < 64) m = m | (1L << sy0);
  for (int sy = sy0 + 1; sy <= syt && sy < 64; sy++) if (sectionOk(w, cx, sy, cz)) m = m | (1L << sy);
  return m;
}"""))
# the highest ok section from syt down to sy0 (pure; the harness feeds it masks)
JM(lan, r"""
public static int walk(int sy0, int syt, long mask) {
  for (int sy = syt; sy > sy0; sy--) if (sy >= 0 && sy < 64 && ((mask >> sy) & 1L) != 0L) return sy;
  return sy0;
}""")
# where the helper goes: want blocks above the feet, inside the world (y 1 .. 318), inside the highest ok section; -1 = no room (< 5).
# Room is compared with the LAN_EPS margin: (feet + want) - feet is not always want in doubles (review finding 4)
JM(lan, LANJ(r"""
public static double pickY(java.util.UUID u, @WLD@ w, double x, double feet, double z, int want) {
  double top = feet + (double) want;
  if (top > TOP_Y) top = TOP_Y;
  if (top < BOTTOM_Y || top - feet < (double) @PKG@.AccDefs.LAN_MINH - @PKG@.AccDefs.LAN_EPS) return -1.0;
  if (w == null) return top;
  int cx = ((int) Math.floor(x)) >> 5;
  int cz = ((int) Math.floor(z)) >> 5;
  int sy0 = ((int) Math.floor(feet)) >> 5;
  int syt = ((int) Math.floor(top)) >> 5;
  if (sy0 < 0) sy0 = 0;
  if (syt > SECTIONS - 1) syt = SECTIONS - 1;
  long[] c = (long[]) HY.get(u);
  int sy;
  if (c != null && c[0] == (long) cx && c[1] == (long) cz && c[2] == (long) sy0 && c[3] == (long) syt && c[5] < 20L) {
    sy = (int) c[4];
    c[5] = c[5] + 1L;
  } else {
    sy = walk(sy0, syt, sectionMask(w, cx, cz, sy0, syt));
    HY.put(u, new long[] { (long) cx, (long) cz, (long) sy0, (long) syt, (long) sy, 0L });
  }
  double lim = (double) (sy * 32) + 31.5;
  double y = top < lim ? top : lim;
  if (y - feet < (double) @PKG@.AccDefs.LAN_MINH - @PKG@.AccDefs.LAN_EPS) return -1.0;
  return y;
}"""))
# at most one spawn per second per wearer; more than 20 in a minute (something keeps removing it) -> one WARN, then one per 10 s
JM(lan, r"""
public static boolean maySpawn(java.util.UUID u, long now) {
  long[] st = (long[]) SPAWNT.get(u);
  if (st == null) { st = new long[] { 0L, 0L, now }; SPAWNT.put(u, st); }
  if (now - st[2] > 60000L) { st[1] = 0L; st[2] = now; }
  long gap = st[1] >= 20L ? 10000L : 1000L;
  if (st[0] != 0L && now - st[0] < gap) { LIMITED.incrementAndGet(); return false; }
  st[0] = now;
  st[1] = st[1] + 1L;
  if (st[1] == 21L && !LIMIT_WARNED) { LIMIT_WARNED = true; @PKG@.AccStore.warn("Lantern: a helper light had to be placed again more than 20 times in a minute for " + u + " - something keeps removing it; trying every 10 s now (logged once)"); }
  return true;
}""")
# THE HELPER: the vanilla ambient-emitter entity (Transform + NetworkId + Intangible + NonSerialized) + its light + a 5 s dead-man
# DespawnComponent + our marker, added through the CommandBuffer (the Ref comes back pending: valid once the buffer ran)
JM(lan, LANJ(r"""
public static @REF@ spawn(java.util.UUID u, @ST@ store, @CB@ cb, double x, double y, double z, int key) {
  @CRG@ reg = store.getRegistry();
  @HLD@ h = reg.newHolder();
  @TCO@ tc = new @TCO@();
  tc.setPosition(new @V3D@(x, y, z));
  h.addComponent(T_TC, tc);
  h.addComponent(T_DL, new @DLC@(@PKG@.AccDefs.lanColor(key)));
  h.addComponent(T_NID, new @NID@(netId(store)));
  h.ensureComponent(T_INT);
  h.addComponent(reg.getNonSerializedComponentType(), @NSR@.get());
  @TMR@ tr = null;
  if (R_TIME != null) tr = (@TMR@) store.getResource(R_TIME);
  if (tr != null) h.addComponent(T_DES, @DES@.despawnInSeconds(tr, DESPAWN_S));
  h.addComponent(T_MARK, new @PKG@.AccLanternMark(u));
  SPAWNS.incrementAndGet();
  return cb.addEntity(h, @ARS@.SPAWN);
}"""))
# the helper goes: removed only from its OWN store (a helper left in another world is removed by that world's AccLanternHelp)
JM(lan, LANJ(r"""
public static int drop(java.util.UUID u, @ST@ store, @CB@ cb) {
  Object o = HELPER.remove(u);
  HSTATE.remove(u);
  HY.remove(u);
  if (o instanceof @REF@) {
    @REF@ r = (@REF@) o;
    if (r.getStore() == store && r.isValid()) {
      cb.tryRemoveEntity(r, @RRS@.REMOVE);
      HREMOVES.incrementAndGet();
      return 128;
    }
  }
  return 0;
}"""))
# THE GLOW on the player: want = our light key (0 = none). Ours is recognised by its mark (AccDefs.lanOurs); another light is never
# changed or removed (16), ours comes back once it is gone. 2 added, 4 changed (a new setting), 8 removed.
JM(lan, LANJ(r"""
public static int glow(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, int want) {
  if (T_DL == null) return 0;
  @DLC@ dl = (@DLC@) store.getComponent(ref, T_DL);
  if (want == 0) {
    if (dl == null || !@PKG@.AccDefs.lanOurs(dl.getColorLight())) return 0;
    cb.tryRemoveComponent(ref, T_DL);
    GLOW_OFF.incrementAndGet();
    return 8;
  }
  if (dl == null) {
    cb.addComponent(ref, T_DL, new @DLC@(@PKG@.AccDefs.lanColor(want)));
    GLOW_ON.incrementAndGet();
    return 2;
  }
  if (!@PKG@.AccDefs.lanOurs(dl.getColorLight())) { FOREIGN.incrementAndGet(); return 16; }
  if (@PKG@.AccDefs.lanKeyOf(dl.getColorLight()) == want) return 0;
  dl.setColorLight(@PKG@.AccDefs.lanColor(want));
  GLOW_SET.incrementAndGet();
  return 4;
}"""))
# THE REACH: w = WANT (null = none). Every tick: the helper above the player (pickY; never farther up than the wearer's own view radius - 4,
# CollectVisible's radius - so a player with a short view distance still gets it), its WHITE light capped for the height it really got,
# placed when missing (32), moved (64) when it is more than height / 50 blocks (0.1 - 1.5) off its spot or at all BELOW it (closer to the
# wearer = brighter), its light changed (256), its dead-man timer refreshed; removed (128) when not wanted or there is no room; 1024 = a
# spawn waits (the limit). A helper left in another store is forgotten here (its world removes it).
JM(lan, LANJ(r"""
public static int helper(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, int[] w) {
  Object hro = HELPER.get(u);
  @REF@ hr = null;
  if (hro instanceof @REF@) hr = (@REF@) hro;
  if (w == null || w[2] <= 0 || w[3] <= 0) return hr == null ? 0 : drop(u, store, cb);
  @TCO@ tc = null;
  if (T_TC != null) tc = (@TCO@) store.getComponent(ref, T_TC);
  if (tc == null) return 0;
  @V3D@ p = tc.getPosition();
  double x = p.x();
  double feet = p.y();
  double z = p.z();
  int want = w[2];
  if (T_EV != null) {
    @EVW@ ev = (@EVW@) store.getComponent(ref, T_EV);
    if (ev != null) {
      int vr = ev.viewRadiusBlocks - @PKG@.AccDefs.LAN_VIEW_MARGIN;
      if (vr < want) { want = vr; CLAMPED.incrementAndGet(); }
    }
  }
  double y = pickY(u, worldOf(store), x, feet, z, want);
  if (y < 0.0) return hr == null ? 0 : drop(u, store, cb);
  int lvl = w[3];
  int hgt = (int) Math.floor(y - feet + @PKG@.AccDefs.LAN_EPS);
  if (hgt < w[2]) {
    int m = @PKG@.AccDefs.lanMaxLevel((double) hgt - @PKG@.AccDefs.LAN_PZ, @PKG@.AccDefs.lanCap(w[0]));
    if (m < lvl) lvl = m;
  }
  if (lvl <= 0) return hr == null ? 0 : drop(u, store, cb);
  int key = @PKG@.AccDefs.lanHKey(lvl);
  int[] hs = hstate(u);
  if (hr != null && hr.getStore() != store) { HELPER.remove(u); hr = null; }
  if (hr != null && !hr.isValid()) {
    if (hs[1] != 0 || hs[0] > 30) { HELPER.remove(u); hr = null; GONE.incrementAndGet(); }
    else { hs[0] = hs[0] + 1; return 0; }
  }
  if (hr == null) {
    if (!maySpawn(u, System.currentTimeMillis())) return 1024;
    hr = spawn(u, store, cb, x, y, z, key);
    HELPER.put(u, hr);
    hs[0] = 0;
    hs[1] = 0;
    hs[2] = key;
    return 32;
  }
  hs[1] = 1;
  hs[0] = hs[0] + 1;
  int code = 0;
  @TCO@ htc = (@TCO@) cb.getComponent(hr, T_TC);
  if (htc != null) {
    @V3D@ hp = htc.getPosition();
    double dx = hp.x() - x;
    double dy = hp.y() - y;
    double dz = hp.z() - z;
    double th = (double) hgt / @PKG@.AccDefs.LAN_MOVE_DIV;
    if (th < @PKG@.AccDefs.LAN_MOVE_MIN) th = @PKG@.AccDefs.LAN_MOVE_MIN;
    if (th > @PKG@.AccDefs.LAN_MOVE_MAX) th = @PKG@.AccDefs.LAN_MOVE_MAX;
    if (dy < -0.02 || dx * dx + dy * dy + dz * dz > th * th) { htc.setPosition(new @V3D@(x, y, z)); MOVES.incrementAndGet(); code = code | 64; }
  }
  if (hs[2] != key) {
    @DLC@ hdl = (@DLC@) cb.getComponent(hr, T_DL);
    if (hdl != null) { hdl.setColorLight(@PKG@.AccDefs.lanColor(key)); hs[2] = key; RELIT.incrementAndGet(); code = code | 256; }
  }
  @DES@ dc = null;
  if (T_DES != null) dc = (@DES@) cb.getComponent(hr, T_DES);
  @TMR@ tr = null;
  if (R_TIME != null) tr = (@TMR@) store.getResource(R_TIME);
  if (dc != null && tr != null) dc.setDespawnTo(tr.getNow(), DESPAWN_S);
  return code;
}"""))
# ONE TICK for one player (AccLanternSys: u, their entity, its store and CommandBuffer, dt). Decides once a second, at once after a bag change
# (AccStore.LPOKE), at once for a new entity of the player (join, world change: their glow is back on the first tick), at once when a wearer
# died, and when a setting changed the tier table; then the glow (decision ticks) and the helper (every tick while wanted). Returns the OR
# of the glow / helper codes + 1 when it decided.
JM(lan, LANJ(r"""
public static int step(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, float dt) {
  if (u == null || ref == null || store == null || cb == null) return 0;
  Object prev = OWNER.put(u, ref);
  boolean moved = prev != ref;
  float[] c = clk(u);
  c[0] = c[0] + dt;
  int[] w = (int[]) WANT.get(u);
  boolean poke = @PKG@.AccStore.LPOKE.remove(u) != null;
  if (w == null && !poke && !moved && c[0] < 1.0f && !HELPER.containsKey(u)) return 0;
  boolean dead = T_DEATH != null && store.getComponent(ref, T_DEATH) != null;
  int code = 0;
  if (poke || moved || c[0] >= 1.0f || (w != null && (dead || w[5] != @PKG@.AccDefs.LAN_EPOCH))) {
    c[0] = 0.0f;
    code = 1;
    @PKG@.AccDefs.lanTable();
    int t = 0;
    if (@PKG@.AccDefs.LINE_LANTERN && !dead) t = @PKG@.AccDefs.lanBest(@PKG@.AccStore.snapshot(u));
    if (t <= 0) {
      WANT.remove(u);
      w = null;
    } else {
      int g = @PKG@.AccDefs.lanGlow(t);
      w = new int[] { t, g > 0 ? @PKG@.AccDefs.lanKey(g) : 0, @PKG@.AccDefs.LAN_TAB_H[t], @PKG@.AccDefs.LAN_TAB_L[t], dead ? 1 : 0, @PKG@.AccDefs.LAN_EPOCH };
      WANT.put(u, w);
    }
    code = code | glow(u, ref, store, cb, w == null ? 0 : w[1]);
  }
  code = code | helper(u, ref, store, cb, w);
  return code;
}"""))
# AccLanternHelp's question for every helper: keep it? Only while its owner's CURRENT entity is valid, in THIS store, and this helper is
# the recorded one (logout / world change: the old entity ref is invalid or in another store; a duplicate or a parked helper coming
# back is not the recorded one)
JM(lan, r"""
public static boolean keep(java.util.UUID u, @REF@ helper, @ST@ store) {
  if (u == null || helper == null) return false;
  Object o = OWNER.get(u);
  if (!(o instanceof @REF@)) return false;
  @REF@ r = (@REF@) o;
  if (!r.isValid() || r.getStore() != store) return false;
  return HELPER.get(u) == helper;
}""")
# THE REACH LIGHT IS THE WEARER'S OWN (the fix round; AccLanternHide runs this on every viewer in the find-visible group after CollectVisible,
# like the vanilla HideFromNonSpectators): every helper in this viewer's visible set that is not the viewer's own goes out of it, so the
# engine never sends it to them (AddToVisible builds Visible.visibleTo from what is left). lantern.shareReach: only a viewer who hid the
# wearer (HiddenPlayersManager, the vanilla /hide) loses it. Returns how many were taken out.
JM(lan, LANJ(r"""
public static int hideFrom(java.util.UUID me, @HPM@ hm, java.util.Set vis, @CB@ cb) {
  if (vis == null || cb == null || T_MARK == null) return 0;
  boolean share = @PKG@.AccDefs.LAN_SHARE;
  int n = 0;
  java.util.Iterator it = vis.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @REF@)) continue;
    @REF@ r = (@REF@) o;
    if (!r.isValid()) continue;
    @ARC@ a = cb.getArchetype(r);
    if (a == null || !a.contains(T_MARK)) continue;
    @PKG@.AccLanternMark m = (@PKG@.AccLanternMark) cb.getComponent(r, T_MARK);
    java.util.UUID ow = null;
    if (m != null) ow = m.owner;
    if (ow != null && ow.equals(me)) continue;
    if (share && ow != null) {
      boolean hid = false;
      if (hm != null) hid = hm.isPlayerHidden(ow);
      if (!hid) continue;
    }
    it.remove();
    n++;
  }
  if (n > 0) HIDDEN.addAndGet((long) n);
  return n;
}"""))
JM(lan, r"""
public static void prune(java.util.Set online) {
  CLK.keySet().retainAll(online);
  WANT.keySet().retainAll(online);
  HELPER.keySet().retainAll(online);
  HSTATE.keySet().retainAll(online);
  OWNER.keySet().retainAll(online);
  HY.keySet().retainAll(online);
  SPAWNT.keySet().retainAll(online);
  @PKG@.AccStore.LPOKE.keySet().retainAll(online);
}""")
JM(lan, r"""
public static void clearAll() {
  CLK.clear();
  WANT.clear();
  HELPER.clear();
  HSTATE.clear();
  OWNER.clear();
  HY.clear();
  SPAWNT.clear();
  @PKG@.AccStore.LPOKE.clear();
}""")

''' + s[_B:]
rep('''  try { @PKG@.AccNv.prune(online); } catch (Throwable t) { }   // 0.5.3: the Night Vision state of players who left
''', '''  try { @PKG@.AccLantern.prune(online); } catch (Throwable t) { }   // 0.5.4: the Lantern state of players who left (their helpers go by themselves)
''')

# ---------------------------------------------------------------------------------------------------------------- the three systems
_A = s.index("# ================= 0.5.3 AccNightVision: the Night Vision system")
_B = s.index("# ================= 0.5.2: the Workbench tab (tools/skyywbtab.py; WB.probe stops the build when an engine fact it relies on changed)")
s = s[:_A] + r'''# ================= 0.5.4 AccLanternSys: the Lantern on every player (EntityTickingSystem, query = PlayerRef, no group: the world thread, one
# player after another - isParallel is not overridden), AccLanternHelp: every helper entity (query = our marker) and (the fix round)
# AccLanternHide: every viewer (query = EntityViewer, the tracker's find-visible group after CollectVisible) =================
# ONE registerSystem per class (setup). All three only read the engine components and call AccLantern (the harness runs the same code).
lsys.addConstructor(CtNewConstructor.make("public AccLanternSys() { super(); }", lsys))
JF(lsys, "public static boolean FAILED = false;")
JM(lsys, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PKG@.AccLantern.T_PR;
}""")
JM(lsys, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PKG@.AccLantern.T_PR);
    if (pr == null) return;
    @PKG@.AccLantern.step(pr.getUuid(), ref, store, cb, dt);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("Lantern failed (logged once): " + t); }
  }
}""")
lhs.addConstructor(CtNewConstructor.make("public AccLanternHelp() { super(); }", lhs))
JF(lhs, "public static boolean FAILED = false;")
JM(lhs, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PKG@.AccLantern.T_MARK;
}""")
JM(lhs, LANJ(r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PKG@.AccLanternMark m = (@PKG@.AccLanternMark) chunk.getComponent(idx, @PKG@.AccLantern.T_MARK);
    java.util.UUID u = null;
    if (m != null) u = m.owner;
    if (@PKG@.AccLantern.keep(u, ref, store)) return;
    cb.tryRemoveEntity(ref, @RRS@.REMOVE);
    @PKG@.AccLantern.ORPHANS.incrementAndGet();
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("Lantern helper clean-up failed (logged once): " + t); }
  }
}"""))
# AccLanternHide (the fix round): THE REACH LIGHT IS THE WEARER'S OWN. Query = the EntityViewer (every viewer), group = the entity tracker's
# FIND_VISIBLE_ENTITIES_GROUP, AFTER CollectVisible - exactly the vanilla SpectatorSystems$HideFromNonSpectators / HideFromPlayer place:
# ClearEntityViewers empties the visible sets BEFORE the group, CollectVisible fills them, we take other wearers' helpers out, and only
# after the group AddToVisible turns what is left into Visible.visibleTo (the viewers DynamicLightTracker / the move tracker / SendPackets
# serve). A world without helpers is skipped (getEntityCountFor, the HideFromNonSpectators short cut). isParallel not overridden (false).
lhd.addConstructor(CtNewConstructor.make("public AccLanternHide() { super(); }", lhd))
JF(lhd, "public static boolean FAILED = false;")
lhd.addField(CtField.make(LANJ("public static final java.util.Set DEPS = java.util.Collections.singleton(new @SDP@(@ORD@.AFTER, @CVS@.class));"), lhd))
JM(lhd, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PKG@.AccLantern.T_EV;
}""")
JM(lhd, LANJ(r"""
public @SGR@ getGroup() {
  return @ETR@.FIND_VISIBLE_ENTITIES_GROUP;
}"""))
JM(lhd, r"""
public java.util.Set getDependencies() {
  return DEPS;
}""")
JM(lhd, r"""
public void tick(float dt, int systemIndex, @ST@ store) {
  if (@PKG@.AccLantern.T_MARK == null || @PKG@.AccLantern.T_EV == null || store == null) return;
  if (store.getEntityCountFor((@QRY@) @PKG@.AccLantern.T_MARK) == 0) return;
  super.tick(dt, systemIndex, store);
}""")
JM(lhd, LANJ(r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @EVW@ v = (@EVW@) chunk.getComponent(idx, @PKG@.AccLantern.T_EV);
    if (v == null) return;
    java.util.UUID me = null;
    @HPM@ hm = null;
    if (@PKG@.AccLantern.T_PR != null) {
      @PR@ pr = (@PR@) chunk.getComponent(idx, @PKG@.AccLantern.T_PR);
      if (pr != null) { me = pr.getUuid(); hm = pr.getHiddenPlayersManager(); }
    }
    @PKG@.AccLantern.hideFrom(me, hm, v.visible, cb);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("Lantern: hiding reach lights from other players failed (logged once): " + t); }
  }
}"""))

''' + s[_B:]

# ---------------------------------------------------------------------------------------------------------------- the plugin
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.AccNightVision());   // 0.5.3: Night Vision (the entity tracker's update group)
''', '''  @PKG@.AccLantern.bind();   // 0.5.4: the Lantern - the engine's component types once, then our marker and the three systems (one each)
  @PKG@.AccLantern.T_MARK = getEntityStoreRegistry().registerComponent(@PKG@.AccLanternMark.class, new @PKG@.AccLanternMarkSup());
  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternHelp());
  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternHide());   // the fix round: the reach light is the wearer's own
''')
rep('''  try { com.skyy.accessories.AccNv.clearAll(); } catch (Throwable t) { }   // 0.5.3: the Night Vision state (the lights go with the clients)
''', '''  try { com.skyy.accessories.AccLantern.clearAll(); } catch (Throwable t) { }   // 0.5.4: the Lantern state (helpers: NonSerialized + a 5 s despawn)
''')
rep('''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear, nv, nvs):   # 0.5.3: + AccNv, AccNightVision
''', '''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear, lmk, lms, lan, lsys, lhs, lhd):   # 0.5.4: the Lantern (AccNv, AccNightVision gone)
''')
rep('''"inventory cooking, a Night Vision accessory (its own line - a light only its wearer sees), %d booster lines in the gear rarities Normal to Legendary (''',
    '''"inventory cooking, the Lantern line (its wearer glows like a torch for everyone; Unique and up light farther for the wearer through a hidden light above them), %d booster lines in the gear rarities Normal to Legendary (''')

# ---------------------------------------------------------------------------------------------------------------- the items + lang
rep('''HIDDEN_IDS = LEGACY_IDS + RETIRED_IDS
assert len(LEGACY_IDS) == 20 and len(RETIRED_IDS) == 5 and len(set(HIDDEN_IDS)) == 25, (len(LEGACY_IDS), RETIRED_IDS)
''', '''HIDDEN_IDS = LEGACY_IDS + RETIRED_IDS + [NV_ID]   # 0.5.4: + the retired Night Vision
assert len(LEGACY_IDS) == 20 and len(RETIRED_IDS) == 5 and len(set(HIDDEN_IDS)) == 26, (len(LEGACY_IDS), RETIRED_IDS)
''')
_A = s.index("# ---- 0.5.3 THE NIGHT VISION ITEM: no recipe (admin give only), the look of the vanilla Lightning Essence (model, texture, icon), Rare,")
_B = s.index('files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"')
s = s[:_A] + r'''# ---- 0.5.3 THE NIGHT VISION ITEM, RETIRED in 0.5.4: still the vanilla Lightning Essence look, Rare frame, no recipe, now hidden from the
# creative library (Variant, no Categories - hide_item) with the retired name and text; its 4 lang lines stay where 0.5.3 had them
_nvnode = item(NV_ID, icon_of(NV_LOOK), QUAL_IDS[NV_TIER], [], WB_REQ, visual=visual_of(NV_LOOK))
del _nvnode["Recipe"]
hide_item(NV_ID, _nvnode)
files["Server/Item/Items/Utility/%s.json" % NV_ID] = json.dumps(_nvnode, indent=2)
NV_NAME = "%s Accessory (retired)" % NV_LINE
NV_DESC = ("Retired. The Lantern Accessory replaced it: craft one at a Workbench. This accessory does nothing and cannot be equipped; if "
           "one is still in your Accessory Bag, Unequip takes it out.")
NV_LANG = ["items.%s.name=%s" % (NV_ID, NV_NAME), "server.items.%s.name=%s" % (NV_ID, NV_NAME),
           "items.%s.description=%s" % (NV_ID, NV_DESC), "server.items.%s.description=%s" % (NV_ID, NV_DESC)]
lang.extend(NV_LANG)


# ---- 0.5.4 THE LANTERN ITEMS: one per rarity, the look of a vanilla lantern (its block model + texture + icon, the Slowness Totem pattern),
# the Workbench tab recipe (Normal from vanilla items, every other rarity from the one below), vanilla-style text. Their 16 lang lines go
# last: server.lang = 0.5.3's (the Night Vision text changed in place) + these lines.
def block_visual_of(iid):
    """a vanilla block item's look for a plain item: its BlockType custom model + first texture (both checked under Common/), a scale for
    a hand-held accessory (0.6 x the block's own CustomModelScale), the item hold animation, the vanilla IconProperties when it has some"""
    need_item(iid)
    d = json.loads(_ASSETS.read(_ITEMS[iid]).decode("utf-8-sig"))
    bt = d.get("BlockType") or {}
    out = {"Model": bt.get("CustomModel"), "Texture": ((bt.get("CustomModelTexture") or [{}])[0]).get("Texture"),
           "Scale": round(0.6 * float(bt.get("CustomModelScale", 1.0)), 3), "PlayerAnimationsId": "Item"}
    assert out["Model"] and out["Texture"] and bt.get("DrawType") == "Model", "0.5.4: %s has no custom block model: %r" % (iid, bt)
    for k in ("Model", "Texture"):
        assert "Common/" + out[k] in _COMMON, "0.5.4: missing %s file for %s: %s" % (k, iid, out[k])
    if "IconProperties" in d:
        out["IconProperties"] = d["IconProperties"]
    return out


TORCH_DATA = {}
for _ti in TORCH_ITEMS:
    need_item(_ti)
    TORCH_DATA[_ti] = (json.loads(_ASSETS.read(_ITEMS[_ti]).decode("utf-8-sig")).get("BlockType") or {}).get("Light")


def _torch_proof():
    """0.5.4: the vanilla torch's light from Assets.zip = the Lantern's default glow (#RGB = one hex digit per channel; the harness runs the
    engine's own ColorParseUtil on it)"""
    for ti, li in TORCH_DATA.items():
        assert li == {"Radius": 0, "Color": TORCH_HEX} or li == {"Color": TORCH_HEX, "Radius": 0}, "0.5.4: %s light changed: %r" % (ti, li)
    assert tuple(int(ch, 16) for ch in TORCH_HEX[1:]) == TORCH_RGB and TORCH_RGB[0] == LAN_TORCH
    assert (lan_key(LAN_TORCH) >> 16) & 255 == 11 and (lan_key(LAN_TORCH) >> 8) & 255 == 10 and lan_key(LAN_TORCH) & 255 == 9
    print("lantern: the vanilla torch light (%s) = %s radius 0 = levels %d / %d / %d - the default glow sends exactly that (+ the radius-1 "
          "owner mark, no visible change)" % (", ".join(TORCH_ITEMS), TORCH_HEX, TORCH_RGB[0], TORCH_RGB[1], TORCH_RGB[2]))


_torch_proof()
LAN_NAMES = ["%s %s Accessory" % (DISPLAY[_t], LAN_LINE) for _t in range(1, 5)]
LAN_DESCS = []
for _t in range(1, 5):
    _first = (_w("Glows like a torch") + " while in your Accessory Bag." if _t == 1 else
              _w("Glows like a torch and lights about %d blocks around you" % LAN_SHOWN[_t]) + " while in your Accessory Bag.")
    _what = ("Everyone around you sees the light - like carrying a torch, with your hands free." if _t == 1 else
             "A hidden light above you reaches about twice as far as the rarity below, while the light around you stays about torch-bright.")
    _rule = "Only your best Lantern Accessory counts. " + ("Next: %s (upgrade it at a Workbench)." % LAN_NAMES[_t] if _t < 4 else
                                                          "Legendary is the top rarity.")
    LAN_DESCS.append(_first + TIP_NL + _what + TIP_NL + _rule + TIP_NL + TIP_NL + "<i>%s</i>" % LAN_FLAVOUR)
LAN_LANG = []
for _t in range(1, 5):
    _iid = LAN_IDS[_t - 1]
    _look = block_visual_of(LAN_LOOKS[_t - 1])
    if _t == 1:
        _rin = [mat(m, q) for m, q in LAN_RECIPES[0]]
    else:
        _rin = [{"ItemId": LAN_IDS[_t - 2], "Quantity": 1}] + [mat(m, q) for m, q in LAN_RECIPES[_t - 1]]
    _node = item(_iid, icon_of(LAN_LOOKS[_t - 1]), QUAL_IDS[_t], _rin, WB_REQ, visual=_look)
    if "IconProperties" not in _look:
        del _node["IconProperties"]   # the backpack's icon framing would not fit (the icon is the vanilla lantern's own PNG)
    files["Server/Item/Items/Utility/%s.json" % _iid] = json.dumps(_node, indent=2)
    LAN_LANG += ["items.%s.name=%s" % (_iid, LAN_NAMES[_t - 1]), "server.items.%s.name=%s" % (_iid, LAN_NAMES[_t - 1]),
                 "items.%s.description=%s" % (_iid, LAN_DESCS[_t - 1]), "server.items.%s.description=%s" % (_iid, LAN_DESCS[_t - 1])]
lang.extend(LAN_LANG)
''' + s[_B:]

# the Workbench tab check: tools/skyywbtab.py lists the 47 recipes it knows (unchanged kit); the 4 Lantern recipes are checked against its
# rank here (each in its rarity tier, after that tier's crafted stat lines and before its bench accessories)
rep('''    got = WB.recipe_checks(files, own, bag_req_id=BAG)
    assert len(got) == 47 and got[BAG][0] == FIELD_REQ[0], len(got)
''', '''    lan_paths = ["Server/Item/Items/Utility/%s.json" % i for i in LAN_IDS]   # 0.5.4: not in the shared kit's table (checked below)
    got = WB.recipe_checks(dict((p, t) for p, t in files.items() if p not in lan_paths), own, bag_req_id=BAG)
    assert len(got) == 47 and got[BAG][0] == FIELD_REQ[0], len(got)
    for t, i in enumerate(LAN_IDS, 1):
        rq = json.loads(files["Server/Item/Items/Utility/%s.json" % i])["Recipe"]["BenchRequirement"]
        assert rq == WB_REQ, "0.5.4: %s must sit in the Workbench tab only: %r" % (i, rq)
        rk = WB.rank_py(i + WB.RECIPE_SUFFIX + "0")
        last_line = WB.rank_py("Skyy_Talisman_Speed_%s" % ID_WORD[t] + WB.RECIPE_SUFFIX + "0")
        first_bench = min(WB.rank_py("Skyy_Accessory_%s_T%d" % (b, n) + WB.RECIPE_SUFFIX + "0") for b in WB.BENCHES
                          for n in range(1, WB.BENCH_TIERS[b] + 1) if min(n, 4) == t)
        assert t * 1000000 <= rk < (t + 1) * 1000000 and last_line < rk < first_bench, (i, rk, last_line, first_bench)
    print("Workbench tab: the 4 Lantern recipes rank into their rarity tiers (after that tier's crafted stat lines, before its bench "
          "accessories) through tools/skyywbtab.py's pattern rule - the shared kit is unchanged")
''')
# the hidden-items check: the retired Night Vision is hidden now, the four Lanterns are listed
rep('''        assert py_legacy(iid) or iid in RETIRED_IDS, iid
''', '''        assert py_legacy(iid) or iid in RETIRED_IDS or iid == NV_ID, iid   # 0.5.4: + the retired Night Vision
''')
rep('''    want = set(LINE_IDS) | set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in ACTIVE for t in range(1, b[3] + 1)) | {OMNI, BAG, NV_ID}   # 0.5.3
''', '''    want = set(LINE_IDS) | set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in ACTIVE for t in range(1, b[3] + 1)) | {OMNI, BAG} | set(LAN_IDS)   # 0.5.4
''')
rep('''    print("creative library: %d old ids hidden (Variant true, no Categories: %d legacy booster ids + %d retired bench accessories), "
          "%d current ids listed" % (len(HIDDEN_IDS), len(LEGACY_IDS), len(RETIRED_IDS), len(current)))
''', '''    print("creative library: %d old ids hidden (Variant true, no Categories: %d legacy booster ids + %d retired bench accessories + the "
          "retired Night Vision), %d current ids listed" % (len(HIDDEN_IDS), len(LEGACY_IDS), len(RETIRED_IDS), len(current)))   # 0.5.4
''')
# the Night Vision asset check -> the retirement check + the Lantern asset check + the previous-tier audit
_A = s.index("def _nv_asset_checks():")
_B = s.index("def _player_literals_check():")
s = s[:_A] + r'''def _nv_retired_checks():
    """0.5.4 build check: the retired Night Vision item - the same look and Rare frame, no recipe, hidden from the creative library, the
    retired name and text (items. + server.items.), still never a booster / bench / Workbench-tab id"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    n = items[NV_ID]
    v = visual_of(NV_LOOK)
    assert n["Quality"] == QUAL_IDS[NV_TIER] == "Skyy_Acc_Rare" and "Recipe" not in n and n.get("Variant") is True and "Categories" not in n, n
    assert n["MaxStack"] == 1 and n["Icon"] == icon_of(NV_LOOK) and "Interactions" not in n and all(n[k] == v[k] for k in v), n
    lt = files["Server/Languages/en-US/server.lang"].split("\n")
    i0 = lt.index(NV_LANG[0])
    assert lt[i0:i0 + 4] == NV_LANG and lt[-17:-1] == LAN_LANG and lt[-1] == "", lt[-20:]
    assert NV_NAME == "Night Vision Accessory (retired)" and "Lantern" in NV_DESC and "replaced" in NV_DESC
    assert NV_ID not in WB.EXPECTED and NV_ID in HIDDEN_IDS and NV_ID not in LINE_IDS
    print("night vision: retired - %s keeps its look, no recipe, hidden from the creative library, text: %s" % (NV_ID, NV_DESC[:60]))


_nv_retired_checks()


def _lantern_asset_checks():
    """0.5.4 build check: the four Lantern items - qualities Normal..Legendary, the Workbench tab recipe ladder (each from the one below),
    four distinct vanilla lantern looks and icons, listed in the creative library, names + vanilla-style tooltips, never a booster / bench /
    legacy / hidden id"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    lmap = dict(l.split("=", 1) for l in files["Server/Languages/en-US/server.lang"].split("\n") if "=" in l)
    for t, i in enumerate(LAN_IDS, 1):
        n = items[i]
        assert n["Quality"] == QUAL_IDS[t] and n["Categories"] == ["Items.Tools"] and "Variant" not in n and n["MaxStack"] == 1, (i, n)
        assert n["Icon"] == icon_of(LAN_LOOKS[t - 1]) and "Interactions" not in n and n["PlayerAnimationsId"] == "Item", (i, n)
        ins = n["Recipe"]["Input"]
        if t == 1:
            assert ins == [mat(m, q) for m, q in LAN_RECIPES[0]] and not any(x.get("ItemId", "").startswith("Skyy_") for x in ins), ins
        else:
            assert ins[0] == {"ItemId": LAN_IDS[t - 2], "Quantity": 1} and ins[1:] == [mat(m, q) for m, q in LAN_RECIPES[t - 1]], ins
        assert lmap["items.%s.name" % i] == lmap["server.items.%s.name" % i] == "%s Lantern Accessory" % DISPLAY[t], i
        d = lmap["items.%s.description" % i]
        assert d == lmap["server.items.%s.description" % i] and d.startswith('<color is="#ffffff">Glows like a torch') and \
            "while in your Accessory Bag." in d.split("\\n")[0] and d.count("\\n") == 4, d
        assert ("Next: %s Lantern Accessory (upgrade it at a Workbench)." % DISPLAY[t + 1] in d) if t < 4 else ("top rarity" in d), d
        if t > 1:
            assert ("about %d blocks" % LAN_SHOWN[t]) in d.split("\\n")[0], d
    assert len(set(items[i]["Icon"] for i in LAN_IDS)) == 4 and len(set(items[i]["Model"] for i in LAN_IDS)) == 4
    assert not set(LAN_IDS) & set(HIDDEN_IDS + LINE_IDS + list(WB.EXPECTED))
    for m, q in [x for r in LAN_RECIPES for x in r]:
        need_item(m)
        assert m != "Ingredient_Motes_Light", "Motes of Light have no vanilla source"
    print("lantern items: %s - recipes at the Workbench tab, each from the one below; looks %s" % (", ".join(LAN_NAMES), ", ".join(LAN_LOOKS)))


_lantern_asset_checks()


def _ladder_audit():
    """0.5.4 build check, Skyy 2026-10-03: "all accessories and bags cost the last rarity/size to craft the next one". Every ladder of this
    mod: an item of rarity / tier n > 1 that HAS a recipe must take the n-1 item of its line exactly once; the first rung takes none of its
    own line. Lines: the crafted stat lines (word ids), the bench accessory ladders (_T<n>), the Lantern. Single items (Omni, Accessory Bag,
    Campfire) and lines without recipes (part 2 lines: admin give until the loot pass; retired / legacy ids) are listed."""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    ladders = {}
    for b in FOLDED:
        ladders["%s line" % b[2]] = [booster_id(b, t) for t in range(1, 5)]
    for b in ACTIVE:
        if b[3] > 1:
            ladders["%s accessory" % b[2]] = ["Skyy_Accessory_%s_T%d" % (b[0], t) for t in range(1, b[3] + 1)]
    ladders["Lantern line"] = list(LAN_IDS)
    for name, ids in ladders.items():
        for k, i in enumerate(ids):
            ins = [x.get("ItemId") for x in items[i]["Recipe"]["Input"]]
            if k == 0:
                assert not any(x in ids for x in ins), "%s: %s takes its own line" % (name, i)
            else:
                assert ins.count(ids[k - 1]) == 1 and not any(x in ids and x != ids[k - 1] for x in ins), \
                    "%s: %s must be crafted from %s (the previous tier rule): %r" % (name, i, ids[k - 1], ins)
    no_recipe = [b[2] for b in BOOSTERS if b[8] is None]
    assert all("Recipe" not in items[i] for b in BOOSTERS if b[8] is None for i in [booster_id(b, t) for t in range(1, 5)])
    singles = [i for i in (OMNI, BAG, "Skyy_Accessory_Campfire_T1") if "Recipe" in items[i]]
    print("previous-tier audit: %d ladders follow it (%s); single items %s; no recipe (admin give): %s"
          % (len(ladders), ", ".join(sorted(ladders)), ", ".join(singles), ", ".join(no_recipe)))


_ladder_audit()


''' + s[_B:]
rep('''the Omni accessory counts as every bench accessory; the admin-given Night Vision accessory (its own line) gives its wearer alone a light that brightens caves and the night; speed stacks''',
    '''the Omni accessory counts as every bench accessory; the Lantern line (Normal to Legendary, each crafted from the rarity below) makes its wearer glow like a torch for everyone and lights farther with each rarity through a hidden light above them; speed stacks''')

# ---------------------------------------------------------------------------------------------------------------- the access audit (before the jar)
rep('''jar = os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)
B.assemble(''', r'''# ================= 0.5.4 ACCESS AUDIT (the SkyyUiProbe 0.3.1 lesson; this repo's SkyyArmory 0.1 audit): what the JVM would refuse at RUN time
# with IllegalAccessError - javassist compiles a call to a protected / package-private member from any class and -Xverify:all does not catch
# it. Every class / member reference in the final class bytes is resolved with the JVM's rules; the build stops on any refused one.
import jpype as _jpa
_JMod = _jpa.JClass("javassist.Modifier")
_JConstPool = _jpa.JClass("javassist.bytecode.ConstPool")
_JClassFile, _JDataIn, _JByteIn = (_jpa.JClass("javassist.bytecode.ClassFile"), _jpa.JClass("java.io.DataInputStream"),
                                   _jpa.JClass("java.io.ByteArrayInputStream"))
_AUDIT_OPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
              0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
              0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}


def _audit_pkg(name):
    return name.rsplit(".", 1)[0] if "." in name else ""


def _audit_elem(name):
    n = name.replace("/", ".").lstrip("[")
    if n.startswith("L") and n.endswith(";"):
        return n[1:-1]
    return None if len(n) == 1 and name.startswith("[") else n


def access_audit(items_):
    refused, used, seen = [], set(), 0
    for D, cf in items_:
        dn = str(D.getName())
        for mi in cf.getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it = mi.getConstPool(), ca.iterator()
            while it.hasNext():
                pos = it.next()
                op = it.byteAt(pos)
                if op not in _AUDIT_OPS:
                    continue
                where = "%s.%s @%d %s" % (dn.rsplit(".", 1)[-1], mi.getName(), pos, _AUDIT_OPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic (javassist never writes one)")
                    continue
                idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != _JConstPool.CONST_Class:
                    continue
                if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                    cname, member = str(cp.getClassInfo(idx)), None
                elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                    cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                elif tag == _JConstPool.CONST_InterfaceMethodref:
                    cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)),
                                                                                  str(cp.getInterfaceMethodrefType(idx)))
                else:
                    cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                seen += 1
                try:
                    en = _audit_elem(cname)
                    if en is not None and _audit_pkg(en) != _audit_pkg(dn) and not _JMod.isPublic(pool.get(en).getModifiers()):
                        refused.append("%s: class %s is not public - the JVM refuses it from %s (IllegalAccessError)" % (where, en, dn))
                    if member is None:
                        continue
                    kind, name, desc = member
                    Cc = pool.get("java.lang.Object" if cname.startswith("[") else cname)
                    if kind == "field":
                        x = Cc.getField(name, desc)
                    elif name == "<init>":
                        x = Cc.getConstructor(desc)
                    else:
                        x = Cc.getMethod(name, desc)
                    md, decl = x.getModifiers(), x.getDeclaringClass()
                    dcn = str(decl.getName())
                    if _JMod.isPublic(md) or (_audit_pkg(dcn) == _audit_pkg(dn) and not _JMod.isPrivate(md)):
                        continue
                    if _JMod.isPrivate(md):
                        ok = dcn == dn
                    elif _JMod.isProtected(md):
                        ok = bool(D.subclassOf(decl))
                    else:
                        ok = False
                    use = "%s %s.%s%s" % (_JMod.toString(md), dcn, name, "" if kind == "field" else desc)
                    if ok:
                        used.add("%s.%s (from %s)" % (dcn.rsplit(".", 1)[-1], name, dn.rsplit(".", 1)[-1]))
                    else:
                        refused.append("%s: %s - the JVM refuses it from %s (IllegalAccessError)" % (where, use, dn))
                except Exception as e:
                    refused.append("%s: %s %s does not resolve: %s" % (where, cname, member, e))
    return refused, sorted(used), seen


def _audit_cf(data):
    return _JClassFile(_JDataIn(_JByteIn(data)))


_st = pool.makeClass(PKG + ".AccessAuditSelfTest")
_st.addMethod(CtNewMethod.make("public static void bad(com.hypixel.hytale.server.core.plugin.JavaPlugin p) { p.setup(); }", _st))
_st_refused, _st_used, _st_n = access_audit([(_st, _audit_cf(_st.toBytecode()))])
_st.detach()
assert len(_st_refused) == 1 and "setup" in _st_refused[0] and "IllegalAccessError" in _st_refused[0], \
    "access audit self-test: a protected JavaPlugin.setup() call from a non-subclass must be refused: %s" % _st_refused
_aitems = []
for _root, _dirs, _fls in os.walk(OUT):
    for _fn in sorted(_fls):
        if _fn.endswith(".class"):
            _cn = os.path.relpath(os.path.join(_root, _fn), OUT)[:-6].replace(os.sep, ".")
            with open(os.path.join(_root, _fn), "rb") as _fh:
                _aitems.append((pool.get(_cn), _audit_cf(_fh.read())))
AUDIT_REFUSED, AUDIT_USED, AUDIT_N = access_audit(_aitems)
if AUDIT_REFUSED:
    raise SystemExit("ACCESS AUDIT: %d reference(s) the JVM would refuse at run time (IllegalAccessError):\n  %s"
                     % (len(AUDIT_REFUSED), "\n  ".join(AUDIT_REFUSED)))
print("access audit: %d class / member references in %d classes, 0 the JVM would refuse; non-public engine members used: %s"
      % (AUDIT_N, len(_aitems), ", ".join(AUDIT_USED) or "none"))

jar = os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)
B.assemble(''')

# ---------------------------------------------------------------------------------------------------------------- final checks
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert s.count("registerSystem(") == 4 and s.count("registerSystem(new @PKG@.AccLanternSys())") == 1 and \
    s.count("registerSystem(new @PKG@.AccLanternHelp())") == 1 and s.count("registerSystem(new @PKG@.AccLanternHide())") == 1 and \
    s.count("registerComponent(@PKG@.AccLanternMark.class") == 1, \
    "one registerSystem per class (AccEffects, AccLanternSys, AccLanternHelp, AccLanternHide) and one marker component"
assert 'VERSION = "0.5.4"' in s and s.count("_lantern_engine_proof()") == 2 and s.count("_lantern_asset_checks()") == 2 and \
    s.count("_ladder_audit()") == 2 and s.count("_nv_retired_checks()") == 2 and s.count("_torch_proof()") == 2
for _gone in ('makeClass(PKG + ".AccNv")', 'makeClass(PKG + ".AccNightVision"', "@PKG@.AccNv.", "new @PKG@.AccNightVision", "NVPOKE",
              "LINE_NIGHTVISION", "NV_RADIUS", "nvOnText", "nvLinesText", ".queueUpdate(", ".queueRemove(", "_nv_engine_proof", "NV_ROWS",
              "NV_CONFIG_LINES", "new @PDL@", "PersistentDynamicLight("):
    assert _gone not in s, "0.5.4: %s is still in the script" % _gone
assert "PersistentDynamicLight" not in s.split("_lantern_engine_proof()")[2], "the Lantern never adds a SAVED light"
assert s.count("cb.addComponent(ref, T_DL,") == 1 and s.count("cb.addEntity(h, @ARS@.SPAWN)") == 1 and \
    s.count("h.addComponent(reg.getNonSerializedComponentType(), @NSR@.get());") == 1, "the glow is added in one place, the helper spawned in one"
for _a, _b in (("LAN_IDS = [", "LAN_CONFIG_LINES + [\"\"]"), ("public static double lanLight(", "public static boolean isAccessory("),
               ("public static boolean isLantern(", "public static String[] bonusRows("), ("LPOKE = new", "LPOKE.put(u, Boolean.TRUE)"),
               ("lmk.addInterface(", "public static " + "@REF@ spawn("), ("public static int step(", "tick.addInterface(pool.get(\"java.lang.Runnable\"))"),
               ("@PKG@.AccLantern.prune(online)", "lsys.addConstructor("), ("lsys.addConstructor(", "public void setup() {"),
               ("public static int hideFrom(", "lhd.addConstructor("), ("lhd.addConstructor(", "public void setup() {"),
               ("public static int lanHKey(", "public static int helper("),
               ("lang.extend(LAN_LANG)", 'files["Server/Languages/en-US/server.lang"] = "\\n".join(lang)'),
               ("def _ladder_audit", "access_audit(_aitems)"), ("access_audit(_aitems)", "B.assemble(jar")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:40], _b[:40])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.5.3
print("wrote", dst, "(%d lines; 0.5.3 had %d)" % (s.count(LF), OLD.count(LF)))
