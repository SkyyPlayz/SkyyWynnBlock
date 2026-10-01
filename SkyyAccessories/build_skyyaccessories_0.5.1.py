"""SkyyAccessories 0.5.1 - build script (derived from the generated build_skyyaccessories_0.5.py by tools/acc_0_5_1_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.1.py            -> SkyyAccessories/SkyyAccessories-0.5.1.jar
       python build_skyyaccessories_0.5.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.1.py             (bare JVM -Xverify:all: every 0.5 check + the hidden flags + the 0.5.1 update)
0.5.1: TWO CHANGES (full notes, engine proof and the hidden id list in tools/acc_0_5_1_patch.py):
     - THE STAMINA LINE (Skyy: "double the amount of stamina the stamina accessory gives you, but half the stamina regen boost it
       gives you"; OPEN-QUESTIONS LOCKED 2026-10-01): max Stamina +3 / +6 / +9 / +12 (was +1.5 / +3 / +4.5 / +6) and Stamina Regen
       +2.5 / +5 / +7.5 / +10 % (was +5 / +10 / +15 / +20), Normal..Legendary; tooltips, /accessories lines, the bag page and the
       Server Setup defaults follow the booster table. ONE-TIME UPDATE of a 0.5 config.properties (AccCfg.migrate051, setup() before
       the loader and CfgPub.start; the SkyyGear 0.1.1 migrateStat011 pattern): a boost.Stamina.flat / boost.Stamina.regenPct line that
       still holds the 0.5 numbers gets the 0.5.1 numbers, any other value is kept (INFO line); the old file is first kept as a
       History version (verified before the rewrite - else WARN, untouched, retried next start), one config-changes.log line per
       changed entry (Server Setup -> Changes can undo it); the marker comment "SkyyAccessories 0.5.1 Stamina defaults" makes it
       run once (the 0.5.1 default text carries it).
     - OLD IDS OUT OF THE CREATIVE LIBRARY (Skyy: "this one appears twice in creative"): the 20 legacy booster ids (_Talisman, _Ring,
       _Artifact, the old _Legendary) and the 5 retired bench accessories get "Variant": true and no "Categories" (the engine's item
       library filter, documented in the Item codec - proven at build time); they still load, look, show their tooltip and convert
       as in 0.5. The current items stay listed. No new quality (SkyyVault's HideFromSearch is a quality flag: it would need hidden
       twin qualities and shift every quality index once more).
     - (forced by the 0.4.3 build gate) the Campfire Accessory item text follows SkyyCooking 0.1.3 (Skyy, LOCKED 2026-10-01: campfire
       cooking pays half the Cooking XP): "25% Cooking XP and 75% of your cooking bonus by default" (was 50%); deploy with SkyyCooking 0.1.3.
0.5 notes:
0.5: BOOSTER ACCESSORIES, PARTS 1 AND 2 (Skyy's decisions, OPEN-QUESTIONS LOCKED 2026-09-30; research/Booster-Accessories-Spec.md 6.1
     and 6.2; full notes in tools/acc_0_5_patch.py):
     - ONE booster table (BOOSTERS -> flat 1-D arrays in AccDefs): line, stats, four numbers per stat (Normal..Legendary), item ids,
       looks, source words. Five folded lines: Health, Stamina, Mana, Regeneration, Speed. Part 2: five new lines (admin give only,
       ids Skyy_Talisman_<Key>_T1..T4): Brawler (Strength), Runic (Magical Power), Stonehide (Defense), Razorfang (Crit Chance and
       Crit Damage), Feather (less fall damage, higher jumps).
     - combat stats go to SkyyGear as ONE text per player in gear:extra:<uuid> (SkyyAccessories owns the key: whole numbers, keys
       str mp def cc cd, written only on change, a second writer = back off for that player, removed on leave / shutdown); Feather's
       jump and fall ride the accessories.talismans movement post (fall damage is applied by SkyySkills).
     - the 25 talismans FOLD into those lines: same ids, names "<Rarity> <Line> Accessory", new numbers (Health / Stamina flat, Mana %
       with a floor, Regeneration lower, Speed 2.5..10 %), _Epic = Legendary, the old _Legendary = a legacy id (no recipe, counts as
       Legendary, stored as _Epic); only the best rarity of a line counts; "+stamina" = max Stamina AND a Stamina Regen top-up that
       only flows while vanilla's own refill flows (never while sprinting, gliding or blocking).
     - GEAR RARITIES for every accessory: six Skyy_Acc_* qualities (Fabled / Mythic shipped unused), bench I Normal, II Unique,
       III Rare, IV+ Legendary, the Omni Legendary, the bag item Unique; a world-thread restamp fixes saved stacks.
     - config migration (one atomic write, config.properties.pre-0.5.bak, config-changes.log lines, slots 9 -> 18), a one-time chat
       notice per player (notices.properties), Server Setup rows for every number (boost table, 5 line switches, notice switch).
     - the bag: 60 storage slots (slot0..8 in bags/<key>.properties as before, slot9..59 in bags/<key>.more.properties, so a rollback
       to 0.4.5 hides them instead of deleting them), 18 by default; the page shows 9 rows per page with pagers.
     - /accessories lines (players), /accessories give | givetier (admins), bridges acc:defs + acc:fn:give; the bag page lists the
       active bonus of each line and says when SkyyGear / its combat stats / SkyySkills are missing for a line.
     DO NOT ROLL BACK BELOW 0.5: restamped stacks point at Skyy_Acc_* qualities that 0.4.5 does not ship (stale look, UNVERIFIED).
0.4.5 notes:
0.4.5: THE VANILLA LOOK for the Accessory Bag page (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them
     to look and feel vanilla"; research/Vanilla-UI-Style-Guide.md; full notes in tools/acc_0_4_5_patch.py). ONLY THE LOOK CHANGED:
     - the page is built from the shared kit tools/skyyui.py when this script runs (SUI.verify() first proves every style value,
       texture and sound against Assets.zip, read-only); the kit id is in the ready log line.
     - the vanilla decorated window (title bar with runes, the gold ornaments, ACCESSORY BAG in the title font), 1210 x 780 (was
       640 x 630): a well with the hint and the live Bonuses line (left-aligned, the vanilla value colour), then two vanilla list
       wells - BAG SLOTS (the slot rows) and the inventory list (up to 6 rows) - with vanilla list rows (row panel, blue status bar,
       40 px item icon, 18 px name + 15 px rarity word in the item's quality colour) and small Secondary UNEQUIP / EQUIP buttons,
       then the result line (the kit's status line: green done, red refused, info blue notes / the Campfire line; AccPage.infoColor
       reads 0.4.4's unchanged result texts).
     - every element id of 0.4.4 (#SkyyAcc is now the window body), the un:<i> / eq:<i> bindings, every text (the same Java
       expressions; b.set, so commas show again - safe() only guards the item ids inside the markup), invIds and the profile-key
       check are 0.4.4's; handleDataEvent and every other class are unchanged. This rebuild compiles the current admin config kit
       tools/skyycfg.py 1.1 (the live 0.4.4 jar was built on 1.0): CfgFile / CfgFn / CfgRows / CfgSaveTask carry 1.1's
       hand-edit table-line checks, reload order and monitor changes (the Talisman bonuses rows + /accessories reload use them).
0.4.4 notes:
0.4.4: ADMIN CONFIG IN GAME (research/Server-Setup-Spec.md 4.14, tools/CONFIG-CONTRACT.md; full notes in tools/acc_0_4_4_patch.py):
     - FIRST config file Skyy_SkyyAccessories/config.properties, written on the first start with today's values: slots=9,
       regenEverySeconds=2, bonus.<Family>=<Common..Legendary percents> (the numbers the talisman tooltips print).
     - SkyWynn Menu -> Server Setup -> Accessories (SkyyMenu 0.3) edits them through the kit (tools/skyycfg.py): validated, logged in
       config-changes.log, versioned in config-history/, written back line by line. config:def/fn:SkyyAccessories published LAST in setup().
     - slots limits NEW equips only: accessories already in a higher slot stay, keep counting and can be unequipped (the page hides only
       empty slots above the limit). The bonus table and the regeneration interval apply at once.
     - /accessories reload (skyyaccessories.admin only, groups cleared) re-reads the file after hand edits (logged via=command).
     - Item tooltips keep the built-in numbers (assets); the bag page's Bonuses line shows the live ones.
0.4.3 notes:
0.4.3: the CAMPFIRE accessory is BACK (Skyy 2026-09-24: quick inventory cooking, an emergency cook). Full notes in
     tools/acc_0_4_3_patch.py:
     - Skyy_Accessory_Campfire_T1: recipe back (Bench_Campfire + 4 Copper Bars at a Workbench), equippable, Common, in acc:has:<uuid> and
       acc:fn:has again. Description "Quick inventory cooking: campfire dishes in /craft at 50% Cooking XP and 75% of your cooking
       bonus" (SkyyCooking 0.1.1 cook:fn:campfire does the reduction; SkyySacks 0.7.4's /craft Campfire tab shows + calls it - with
       0.7.3, which still treats it as retired, it unlocks nothing).
     - Omni: covers the Campfire again; recipe = the 11 active top-tier bench accessories (0.4.2: 10).
     - Review fixes: the item text calls 50% / 75% the defaults; the bag page status line shows SkyyCooking's LIVE campfire factors
       while the Campfire accessory or the Omni is equipped (AccStore.campFactors / campLine); the 5 s tick logs one warning per
       distinct live pair that differs from the item text (AccStore.campCheck); the build fails if the SkyyCooking defaults line
       cannot be read.
     - Alchemy Bench T1-T4 and Cooking Bench stay retired exactly as in 0.4.2; every other 0.4.2 behaviour is unchanged.
0.4.2 notes:
0.4.2: RETIRED bench accessories (Skyy: Alchemy + Cooking are table-only; research/Smithing-Smelting-Spec.md section 6; the Campfire
     goes too - its 3 recipes are all cooked food). Full notes in tools/acc_0_4_2_patch.py:
     - Skyy_Accessory_Alchemybench_T1..T4, Skyy_Accessory_Cookingbench_T1, Skyy_Accessory_Campfire_T1 keep their item assets (owned
       copies stay valid items) but have NO recipe, say "(retired)" and why in name + description, and do nothing.
     - Equip refuses them (page line + chat line, the item stays in the inventory); Unequip still takes an equipped copy out.
     - An equipped copy is filtered out of acc:has:<uuid> (AccDefs.benchList) and acc:fn:has (AccStore.has), so it unlocks no /craft
       recipes; rarityOf = 0 (never counts toward accessory power); the page shows it grey as "- retired" / "DOES NOTHING".
     - Omni: recipe = the 10 active top-tier bench accessories (was 13) and it no longer covers the retired three.
     - Every 0.4.1 per-profile behaviour is unchanged.
0.4.1 notes:
0.4.1: per-profile storage (tools/PROFILES-CONTRACT.md) - one accessory bag per SkyyProfiles profile (full notes in
     tools/acc_0_4_1_patch.py):
     - AccStore.pkey(UUID) = the contract helper (bridge "profile:fn:key"; falls back to uuid = profile 1). Bag files
       bags/<pkey>.properties (profile 1 = the existing <uuid>.properties, no migration), BAGS cache keyed by the pkey String,
       each store method resolves the key once (slotsK / saveK), locks stay per player.
     - acc:has:<uuid> / acc:tal:<uuid> stay UUID keys for the ACTIVE profile and are republished when profile:epoch:<uuid> (or the
       active key) changes - checked in the 5 s AccTick and the 1 s AccEffects sync; talisman stats, regen and the Speed movement
       source follow the new profile's bag through the same per-second sync (it reads through pkey).
     - The bag page rebuilds instead of acting when the profile changed since it was drawn. Vanilla inventory untouched.
     - Integration pass: Equip/Unequip refused while profile:busy:<uuid> is set (pending crash recovery) or the player's profile
       state is unknown (SkyyProfiles installed, no profile:epoch:<uuid>); one pkey per click for every store call of that click.
     - Without SkyyProfiles every key is the UUID: behaviour identical to 0.4.
0.4 notes:
0.4: RARITY TIERS + PERCENT LAYER + OMNI (full notes in tools/acc_0_4_patch.py):
     - Talismans Skyy_Talisman_<Family>_<Common|Uncommon|Rare|Epic|Legendary> (Quality = vanilla quality of that name), upgrade recipe =
       previous rarity + materials at a Workbench. Legacy 0.2/0.3 ids <Talisman|Ring|Artifact> keep their assets (no recipe) and count
       as Uncommon/Rare/Epic; Equip stores the modern id, Unequip returns the modern (upgradable) item. Bench accessory rarity by tier
       (T1 Common .. T5+ Legendary). One talisman per family counts (best rarity).
     - Vitality/Endurance/Intelligence = % of the FLAT max Health/Stamina/Mana, Regeneration = % of the FULL current max Health
       every 2 s (deliberate: the Health bar the item text names; a heal is not a max bonus), Speed = %
       through the movement protocol's pct layer. StaticModifier MULTIPLICATIVE was checked in bytecode: it applies after ADDITIVE but
       all multiplicative amounts are SUMMED into one factor (vanilla Meat_Buff 1.05 + ours 1.10 = x2.15), so the % is computed here
       from type max + every other ADDITIVE MAX modifier and posted as ADDITIVE (keys skyyacc_health/stamina/mana, as in 0.2/0.3).
     - Skyy_Accessory_Omni (Legendary, Workbench, all 13 max-tier bench accessories) counts as every bench accessory at max tier:
       acc:has expands it into Skyy_Accessory_<BenchId>_T<maxTier> entries, exactly one entry per bench at the best tier of real +
       Omni (SkyySacks needs no change). Own group "Omni".
     - /accessories (acc, accbag): setPermissionGroups hytale:Adventurer. Bag page shows rarity names in the quality colours.
0.3 notes:
0.3: Speed talismans use the SHARED SKYY MOVEMENT PROTOCOL v1 (tools/skyymove.py has the full spec; SkyySkills 0.2 Acrobatics runs the
     identical MoveSync code): bridge "move:<uuid>" -> ConcurrentHashMap source -> Map{layer "flat"|"pct", speed, jump, fallDamage}.
     This mod posts ONLY its own source "accessories.talismans" (layer pct, speed = best Speed talisman, removed at 0) and then applies
     the total of ALL sources: baseSpeed = default x clamp((1 + sum flat speed) x (1 + sum pct speed), 0.3, 5); jump height =
     (h0 + sum flat blocks) x (1 + sum pct), jumpForce = sqrt(2 g h), h0 = default jumpForce^2 / 2g, g = 32. Idempotent: two appliers
     agree, so talismans and Acrobatics never fight. The 5-strike back-off only triggers against writers outside the protocol (a new
     target resets it; logged once per player); defaults are restored only for a field that still holds the value the protocol wrote;
     nothing is written while mounted. fallDamage is applied only by the owner of bridge "stat:owner:fallDamage" (SkyySkills) -
     talismans post no fall stat. Non-Skyy mods that write MovementSettings directly are NOT coordinated (they win for the player
     they reset): keep them out of SkyWynn worlds; the known ones are named in the log on the first sync (skyymove.KNOWN_WRITERS).
0.2 notes:
SkyyAccessories 0.2 - build script (derived from 0.1 by tools/acc_0_2_patch.py - edit the patch, not this file)
0.2: STAT TALISMANS (Hypixel SkyBlock style) that work while they sit in the Accessory Bag, bag capacity 6 -> 9 (old bags keep their
     slots), "Talisman bonuses" summary line on the bag page. Items Skyy_Talisman_<Family>_<Talisman|Ring|Artifact>; one per family
     counts (same swap rule as the bench accessories). Effects: AccEffects (EntityTickingSystem on Player, world thread, 1 s per player):
     StaticModifier(MAX, ADDITIVE) keys skyyacc_health / skyyacc_stamina / skyyacc_mana, Regeneration = addStatValue(Health) every 2 s,
     Speed = MovementSettings.baseSpeed = default * (1 + bonus) + update(packetHandler) (EndgameAndQoL AccessoryPassiveSystem /
     RPGLeveling MovementSpeedHelper pattern: baseSpeed only) with a back-off when another mod keeps resetting it. Modifiers are removed
     as soon as the talisman leaves the bag. Bridge: acc:has:<uuid> = bench accessories in the bag (0.1 meaning, SkyySacks reads it),
     acc:tal:<uuid> = talismans in the bag, acc:fn:has = both.
     Review fixes: baseSpeed-only speed (no f*f compounding), unequip undoes exactly the baseSpeed we wrote, equip pre-checks the bag and
     hand-backs fall back to a free bag slot then a logged loss, per-player locks, talismans use the vanilla crystal fragment model.
0.1 notes:
SkyyAccessories 0.1 - build script (javassist via jpype). Accessory bag + bench accessories (Skyy's design 2026-09-23).
Run:   python build_skyyaccessories_0.1.py            -> SkyyAccessories/SkyyAccessories-0.1.jar
       python build_skyyaccessories_0.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Design (pattern copied from TerrariaAddons' AccessoryPouchSharedContainer: per-player container persisted to a file, opened from the
item's Secondary interaction; effects are checked, never "applied"):
 - Item Skyy_Accessory_Bag (Fieldcraft recipe): right-click -> page "SkyyAccBag" (/accessories or /acc also opens it).
   6 slots stored in Skyy_SkyyAccessories/bags/<uuid>.properties (slot0..slot5 = item id). Equip moves the item out of your
   inventory into the bag; Unequip gives it back (if your storage is full the item stays in the bag).
 - Bench accessories Skyy_Accessory_<BenchId>_T<n>: one per bench tier. T1 = the bench item + 4 copper bars at a Workbench;
   T(n+1) = T(n) + exactly the materials the real bench needs to upgrade to that tier (from the bench's TierLevels).
   Only one accessory per bench fits in the bag; equipping a higher tier hands the lower one back.
 - Bridge: "acc:has:<uuid>" -> "id,id" (what is in the bag) republished on every change and for every online player (5s tick);
   "acc:fn:has" -> java.util.function.Function apply(Object[]{UUID, String itemId}) -> Boolean. SkyySacks 0.6.1 reads acc:has to
   add a craft-page tab per bench accessory (recipes filtered by BenchRequirement.requiredTierLevel <= accessory tier).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyySkills 0.2)
import skyycfg as CFG   # 0.4.4: the admin config kit (research/Server-Setup-Spec.md 1.3-1.4, tools/CONFIG-CONTRACT.md)
import skyyui as SUI    # 0.4.5: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()            # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()   # "skyyui <version> <blob12>" - in the ready log line

VERSION = "0.5.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
ISS = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction"
OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"
# 0.2 stat / movement API (verified with reflect.py + TerrariaAddons bytecode, see tools/acc_0_2_patch.py)
ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
DST = "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes"
MOD = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
MTG = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
MMG = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager"
MVS = "com.hypixel.hytale.protocol.MovementSettings"
ETS = "com.hypixel.hytale.component.system.tick.EntityTickingSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
QRY = "com.hypixel.hytale.component.query.Query"
CRP = "com.hypixel.hytale.component.ComponentRegistryProxy"

for c, m in ((PLA, "getInventory"), (INV, "getStorage"), (INV, "getHotbar"), (INV, "getBackpack"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"),
             (IC, "addItemStack"), (IC, "getCapacity"), (OCU, "registerSimple"), (HSV, "SCHEDULED_EXECUTOR"), (UNI, "getPlayers"),
             (PAGE, "rebuild"), ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)
for c, m in ((ESM, "getComponentType"), (ESM, "putModifier"), (ESM, "removeModifier"), (ESM, "getModifier"), (ESM, "addStatValue"), (ESM, "get"),
             (ESV, "get"), (ESV, "getMax"), (DST, "getHealth"), (DST, "getStamina"), (DST, "getMana"), (SMO, "getAmount"), (MTG, "MAX"),
             (CAL, "ADDITIVE"), (MMG, "getComponentType"), (MMG, "getSettings"), (MMG, "getDefaultSettings"), (MMG, "update"),
             (MVS, "baseSpeed"), (PR, "getPacketHandler"), (PLA, "isWaitingForClientReady"),
             (ETS, "tick"), (ACH, "getReferenceTo"), (CB, "getComponent"), (REF, "isValid"), (CRP, "registerSystem"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEntityStoreRegistry")):
    B.probe(pool, c, m)
MV.probe(B, pool)   # 0.3: MovementStates.mounting, MovementSettings.jumpForce, PhysicsConstants.GRAVITY_ACCELERATION, ...
# 0.4: percent layer reads the stat type's base max + the other MAX modifiers; /accessories gets the Adventurer permission group
EST = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
ILT = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
ACM = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
for c, m in ((EST, "getAssetMap"), (EST, "getMax"), (ILT, "getAsset"), (ESV, "getModifiers"), (SMO, "getCalculationType"),
             (MOD, "getTarget"), (MTG, "MAX"), (CAL, "ADDITIVE"), (ACM, "setPermissionGroups"), (ACM, "addAliases")):
    B.probe(pool, c, m)
# 0.4.4: /accessories reload (admin sub-command, groups cleared) + the kit's reload op with the admin's name
for c, m in ((ACM, "requirePermission"), (ACM, "addSubCommand"), (ACM, "setPermissionGroups"), (PR, "getUsername"), (PR, "getUuid"),
             (PR, "sendMessage")):
    B.probe(pool, c, m)
# 0.5: the Stamina Regen top-up (research/Booster-Accessories-Spec.md 5.4.1 - every call read in HytaleServer.jar bytecode), the quality
# restamp (the SkyySacks 0.7.7 calls), the admin give (addOrDropItemStack, the SkyyCooking / SkyyExploration call; the target's world
# thread: Store.isInThread + World.execute), /accessories lines (PlayerRef.hasPermission) and the raw command text (SkyyGear /gear give)
RGV = "com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue"
RGN = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating"
RGT = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating$RegenType"
CND = "com.hypixel.hytale.server.core.modules.entity.condition.Condition"
TMR = "com.hypixel.hytale.server.core.modules.time.TimeResource"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
for c, m in ((ESV, "getRegeneratingValues"), (RGV, "getRegenerating"), (RGN, "getRegenType"), (RGN, "getAmount"), (RGN, "getInterval"),
             (RGT, "ADDITIVE"), (CND, "allConditionsMet"), (TMR, "getResourceType"), (TMR, "getNow"), (ST, "getResource"),
             (ESV, "get"), (ESV, "getMax"), (ESM, "addStatValue"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItem"),
             (IS, "getQuantity"), (ITM, "getQualityIndex"), (IC, "setItemStackForSlot"), (SIC, "addOrDropItemStack"),
             (INV, "getCombinedStorageHotbarBackpack"), (ST, "isInThread"), (REF, "getStore"), (PR, "getReference"),
             (PR, "getWorldUuid"), (PR, "hasPermission"), (PR, "isValid"), (UNI, "getPlayer"), (UNI, "getWorld"), (WLD, "execute"),
             (ACM, "setAllowsExtraArguments"), (CTX, "getInputString"), (MSG, "raw"), (MSG, "color")):
    B.probe(pool, c, m)
# 0.5.1: old ids out of the creative library - the ITEM flag Variant (tools/acc_0_5_1_patch.py B): the asset field, its packet field and
# the categories packet field exist, and the Item codec's own documentation still says what the flags do in the item library
IBASE = "com.hypixel.hytale.protocol.ItemBase"
for c, m in ((ITM, "isVariant"), (ITM, "getCategories"), (IBASE, "variant"), (IBASE, "categories")):
    B.probe(pool, c, m)


def _variant_proof():
    import zipfile as _zf
    cls = _zf.ZipFile(B.SERVER_JAR).read("com/hypixel/hytale/server/core/asset/type/item/config/Item.class")
    for needle in (b"Variant", b"Categories",
                   b"If this item is marked as a variant, then we filter it out of the item library menu by default, unless the player "
                   b"chooses to display variants.",
                   b"A list of categories this item will be shown in on the creative library menu."):
        if needle not in cls:
            raise SystemExit("0.5.1: the Item codec no longer says %r - check how old ids are hidden from the creative library" % needle[:60])
    print("creative library: the Item codec documents Variant (filtered out of the item library by default) and Categories")


_variant_proof()

PKG = "com.skyy.accessories"
dfs  = pool.makeClass(PKG + ".AccDefs")
st_  = pool.makeClass(PKG + ".AccStore")
fn   = pool.makeClass(PKG + ".AccFn")
page = pool.makeClass(PKG + ".AccPage", pool.get(PAGE))
fac  = pool.makeClass(PKG + ".AccPageFactory")
cmd  = pool.makeClass(PKG + ".AccCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".AccTick")
eff  = pool.makeClass(PKG + ".AccEffects", pool.get(ETS))
mvs_ = pool.makeClass(PKG + ".MoveSync")   # 0.3: shared movement protocol
pl   = pool.makeClass(PKG + ".SkyyAccessoriesPlugin", pool.get(JP))
cfg_ = pool.makeClass(PKG + ".AccCfg")                         # 0.4.4: config.properties loader + the kit's hooks
rcmd = pool.makeClass(PKG + ".AccReloadCmd", pool.get(APC))    # 0.4.4: /accessories reload (server admins only)
lcmd = pool.makeClass(PKG + ".AccLinesCmd", pool.get(APC))     # 0.5: /accessories lines (every player)
gcmd = pool.makeClass(PKG + ".AccGiveCmd", pool.get(APC))      # 0.5: /accessories give (server admins only)
tcmd = pool.makeClass(PKG + ".AccGiveTierCmd", pool.get(APC))  # 0.5: /accessories givetier (server admins only)
adm  = pool.makeClass(PKG + ".AccAdmin")                         # 0.5: the give helpers (argument text, player lookup, acc:fn:give)
gtk  = pool.makeClass(PKG + ".AccGiveTask")                      # 0.5: one give, run on the TARGET player's world thread
gfn  = pool.makeClass(PKG + ".AccGiveFn")                        # 0.5: bridge acc:fn:give
rtk  = pool.makeClass(PKG + ".AccRestampTask")                   # 0.5: the quality restamp on a player's world thread
note = pool.makeClass(PKG + ".AccNotice")                        # 0.5: the one-time chat notice per player
gear = pool.makeClass(PKG + ".AccGear")                          # 0.5 part 2: gear:extra publisher, bag page notes, bridge clean-up

# (benchId, bench item id, display name, tiers, [upgrade materials to reach T2, T3, ...])
BENCHES = [
    ("Workbench",      "Bench_WorkBench", "Workbench",      3, [[("Ingredient_Bar_Copper", 30), ("Ingredient_Bar_Iron", 20), ("Ingredient_Fabric_Scrap_Linen", 20)],
                                                               [("Ingredient_Bar_Thorium", 30), ("Ingredient_Bar_Cobalt", 20), ("Ingredient_Leather_Heavy", 30), ("Ingredient_Fabric_Scrap_Shadoweave", 50), ("Ingredient_Fire_Essence", 25)]]),
    ("Armor_Bench",    "Bench_Armour",    "Armor Bench",    3, [[("Ingredient_Bar_Copper", 20), ("Ingredient_Bone_Fragment", 20), ("Ingredient_Leather_Medium", 20), ("Wood_Azure_Trunk", 100)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fabric_Scrap_Shadoweave", 40), ("Ingredient_Chitin_Sturdy", 40), ("Ingredient_Voidheart", 3)]]),
    ("Weapon_Bench",   "Bench_Weapon",    "Weapon Bench",   3, [[("Ingredient_Bar_Iron", 20), ("Ingredient_Leather_Light", 30), ("Ingredient_Fabric_Scrap_Linen", 30), ("Ingredient_Sac_Venom", 15)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fire_Essence", 20), ("Ingredient_Ice_Essence", 40), ("Ingredient_Void_Essence", 100)]]),
    ("Alchemybench",   "Bench_Alchemy",   "Alchemy Bench",  4, [[("Ingredient_Bar_Silver", 5), ("Ingredient_Bar_Gold", 10), ("Ingredient_Sac_Venom", 10), ("Rock_Gem_Emerald", 1)],
                                                               [("Ingredient_Bar_Silver", 10), ("Ingredient_Bar_Gold", 20), ("Ingredient_Chitin_Sturdy", 20), ("Rock_Gem_Zephyr", 1)],
                                                               [("Ingredient_Bar_Silver", 20), ("Ingredient_Bar_Gold", 40), ("Ingredient_Fabric_Scrap_Shadoweave", 30), ("Rock_Gem_Sapphire", 1)]]),
    ("Farmingbench",   "Bench_Farming",   "Farming Bench",  7, [[("Ingredient_Life_Essence", 50), ("Plant_Crop_Wheat_Item", 5), ("Plant_Crop_Lettuce_Item", 5), ("Wood_Softwood_Trunk", 5)],
                                                               [("Ingredient_Life_Essence_Concentrated", 1), ("Plant_Crop_Carrot_Item", 10), ("Plant_Crop_Corn_Item", 10), ("Wood_Lightwood_Trunk", 10)],
                                                               [("Ingredient_Life_Essence_Concentrated", 2), ("Plant_Crop_Cauliflower_Item", 20), ("Plant_Crop_Turnip_Item", 20), ("Wood_Hardwood_Trunk", 20)],
                                                               [("Ingredient_Life_Essence_Concentrated", 3), ("Plant_Crop_Aubergine_Item", 30), ("Plant_Crop_Pumpkin_Item", 30), ("Wood_Drywood_Trunk", 30)],
                                                               [("Ingredient_Life_Essence_Concentrated", 4), ("Plant_Crop_Tomato_Item", 40), ("Plant_Crop_Chilli_Item", 40), ("Wood_Darkwood_Trunk", 40)],
                                                               [("Ingredient_Life_Essence_Concentrated", 5), ("Plant_Crop_Cotton_Item", 50), ("Plant_Crop_Rice_Item", 50), ("Wood_Redwood_Trunk", 50)]]),
    ("Furnace",        "Bench_Furnace",   "Furnace",        2, [[("Ingredient_Bar_Copper", 5), ("Ingredient_Bar_Iron", 5), ("Ingredient_Bar_Thorium", 5), ("Ingredient_Bar_Cobalt", 5)]]),
    ("Tannery",        "Bench_Tannery",   "Tannery",        2, [[("Ingredient_Leather_Light", 5), ("Ingredient_Leather_Medium", 5), ("Ingredient_Leather_Heavy", 5), ("Ingredient_Chitin_Sturdy", 5)]]),
    ("Arcanebench",    "Bench_Arcane",    "Arcane Bench",   1, []),
    ("Cookingbench",   "Bench_Cooking",   "Cooking Bench",  1, []),
    ("Furniture_Bench","Bench_Furniture", "Furniture Bench",1, []),
    ("Loombench",      "Bench_Loom",      "Loom",           1, []),
    ("Salvagebench",   "Bench_Salvage",   "Salvage Bench",  1, []),
    ("Campfire",       "Bench_Campfire",  "Campfire",       1, []),
]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
# 0.4.2 RETIRED bench accessories (Smithing-Smelting spec section 6). Their rows stay in BENCHES so the item assets are still generated
# (owned copies stay valid items), but they get no recipe, Equip refuses them, acc:has / acc:fn:has leave them out, the Omni does not
# cover them and they never count for rarity/power. AccDefs.retiredWhy / retiredChat name these two ids literally - keep them in sync.
# 0.4.3: the Campfire is NOT retired any more (Skyy 2026-09-24: quick inventory cooking at 50% Cooking XP and 75% of the cooking
# bonus - SkyyCooking 0.1.1 cook:fn:campfire, called by SkyySacks' /craft page). It is an ordinary ACTIVE bench accessory again.
RETIRED = ["Alchemybench", "Cookingbench"]
assert RETIRED == ["Alchemybench", "Cookingbench"], "AccDefs.retiredWhy / retiredChat and RETIRED_DESC name these literally"
ACTIVE = [b for b in BENCHES if b[0] not in RETIRED]
assert all(any(b[0] == r for b in BENCHES) for r in RETIRED), RETIRED
assert len(ACTIVE) == len(BENCHES) - len(RETIRED) == 11, [b[0] for b in ACTIVE]
assert [b[3] for b in ACTIVE if b[0] == "Campfire"] == [1], "0.4.3: the Campfire must be an active single-tier bench"
RETIRED_NAMES = [[b[2] for b in BENCHES if b[0] == r][0] for r in RETIRED]
RETIRED_MAX = [[b[3] for b in BENCHES if b[0] == r][0] for r in RETIRED]   # tier count per retired bench (pretty: numeral only if > 1)
assert RETIRED_MAX == [4, 1], RETIRED_MAX
# 0.4.3 Campfire accessory description (Skyy's call, orchestrator wording). The two numbers are SkyyCooking's defaults
# campfire.xpFactor / campfire.buffFactor (cook:fn:campfire applies the real, configurable factors) - checked against the newest
# SkyyCooking build script when it is present, so the tooltip cannot drift from those defaults.
# 0.4.3 review fix: a server can change the real factors in cooking.properties, so the text calls them the defaults and points at the
# Accessory Bag page, whose status line shows the LIVE factors (AccStore.campLine); AccStore.campCheck logs a mismatch once.
CAMP_XP_PCT, CAMP_BUFF_PCT = 25, 75   # 0.5.1: SkyyCooking 0.1.3 halves the campfire XP share (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01)
CAMPFIRE_DESC = ("Quick inventory cooking: campfire dishes in /craft at %d%% Cooking XP and %d%% of your cooking bonus by default (your "
                 "Accessory Bag page shows this server's numbers). Put it in your Accessory Bag and /craft cooks the Campfire recipes "
                 "straight from your inventory - an emergency cook; a Cooking Bench gives the full bonus and XP.") % (CAMP_XP_PCT, CAMP_BUFF_PCT)
assert CAMPFIRE_DESC.startswith("Quick inventory cooking: campfire dishes in /craft at 25% Cooking XP and 75% of your cooking bonus by default"), CAMPFIRE_DESC
def _camp_defaults_check():
    import re, glob
    def _v(p):
        m = re.search(r"_(\d+(?:\.\d+)*)\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(glob.glob(os.path.join(HERE, "..", "SkyyCooking", "build_skyycooking_*.py")), key=_v)
    if not found:
        print("note: no SkyyCooking build script next to this mod - Campfire description numbers not cross-checked")
        return
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    m = re.search(r"^CAMP_BUFF_DEF, CAMP_XP_DEF = ([0-9.]+), ([0-9.]+)", txt, re.M)
    if not m:   # 0.4.3 review fix: SkyyCooking IS here but changed shape - fail instead of silently skipping the check
        raise SystemExit("0.4.3: %s has no 'CAMP_BUFF_DEF, CAMP_XP_DEF = <buff>, <xp>' line any more - find SkyyCooking's campfire "
                         "defaults, update CAMP_*_PCT and this check (tools/acc_0_4_3_patch.py)" % os.path.basename(found[-1]))
    # 0.4.3 review fix: the bag page / log read the LIVE factors from cook:fn:campfactors - the SkyyCooking build must still publish it
    if 'b.put("cook:fn:campfactors"' not in txt or "Double buffFactor, Double xpFactor, Boolean enabled" not in txt:
        raise SystemExit("0.4.3: %s no longer publishes cook:fn:campfactors -> Object[]{Double buffFactor, Double xpFactor, Boolean "
                         "enabled} - update AccStore.campFactors and this check (tools/acc_0_4_3_patch.py)" % os.path.basename(found[-1]))
    buff, xp = int(round(float(m.group(1)) * 100)), int(round(float(m.group(2)) * 100))
    if (buff, xp) != (CAMP_BUFF_PCT, CAMP_XP_PCT):
        raise SystemExit("0.4.3: %s defaults are buff %d%% / XP %d%% but the Campfire accessory text says %d%% / %d%% - update CAMP_*_PCT"
                         % (os.path.basename(found[-1]), buff, xp, CAMP_BUFF_PCT, CAMP_XP_PCT))
    print("campfire accessory text matches %s defaults (XP %d%%, bonus %d%%)" % (os.path.basename(found[-1]), xp, buff))
_camp_defaults_check()
BAG = "Skyy_Accessory_Bag"
OMNI = "Skyy_Accessory_Omni"   # 0.4: counts as every bench accessory at max tier (own group "Omni"); 0.5: Legendary (crafted, never Mythic)
CAP = 60          # 0.5: bag STORAGE slots (Skyy 2026-09-30: "bag 18 slots to start, up to 60"); AccStore.CAP, the page, un:<i>
MAIN_SLOTS = 9    # 0.5: slot0..slot8 stay in bags/<key>.properties - the file 0.4.x reads and rewrites whole - and slot9..slot59 go
                  # into bags/<key>.more.properties, which 0.4.x never opens: a rollback hides the extra slots, it cannot delete them
SLOTS_DEF = 18    # 0.5: config row slots default (1..CAP); it limits NEW equips only, as in 0.4.4
PAGE_ROWS = 9     # 0.5: bag page rows per page - the bag slots and the accessories in the inventory, each with the kit pager
BONUS_MAX = 12    # 0.5: the Bonuses well: two columns of 6 short lines
REGEN_EVERY = 2
REGEN_MAX = 30
assert MAIN_SLOTS == 9 and 1 <= SLOTS_DEF <= CAP == 60 and PAGE_ROWS == 9 and BONUS_MAX == 12

# ---- BOOSTER TABLE START (SkyyAccessories/test_skyyaccessories_0.5.py execs this block: plain Python - no kit, no JVM, no files)
# 0.5 rarity (Skyy 2026-09-30: "they are all accessories. but they come in the same rarity tiers as weapons and armor"; spec 1.2 / 5.2).
# ID words and display rarities are SEPARATE: the id word "Epic" means Legendary on screen, and "Legendary" ending an id is a legacy word.
ID_WORD = ["", "Common", "Uncommon", "Rare", "Epic"]            # tier 1..4: parse and build ids ONLY (the Workbench ladder)
LEGACY_WORDS = [("Talisman", 2), ("Ring", 3), ("Artifact", 4), ("Legendary", 4)]   # old id tails -> tier; modernOf -> the ID_WORD id
DISPLAY = ["", "Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic"]         # rarity 1..6 = everything players see
ACC_AP = [0, 10, 13, 16, 19, 22, 25]   # Accessory Power by rarity (spec 1.3): a build constant in acc:defs only - no setting, not shown
MAX_LINE_RARITY = 4                    # a line stops at Legendary; Fabled / Mythic are rare finds for later (spec 4.1)
SOURCE_WORDS = ("Craft", "Drop", "Chest", "Combine", "Boss")   # placeholder source words for the later loot pass (spec 2.3)
# THE BOOSTER TABLE (spec 2, 5.4): one row per line. Everything else - the AccDefs arrays, config entries, Server Setup rows, the
# effect tick, tooltips, item assets, /accessories lines, acc:defs and the harness - comes from it.
# (family key = item ids, admin name = config / commands / acc:defs, line name = what players see,
#  look: crystal colour + Legendary icon item (every rarity the colour's crystal fragment model; icons fragments / small cluster /
#        large cluster / that item) OR None + [4 items] (each rarity copies that vanilla item's model and icon, spec 5.6),
#  stats [(stat, kind, [Normal, Unique, Rare, Legendary])], source words per rarity, flavour line,
#  recipes [Normal inputs, Unique extra, Rare extra, Legendary extra] - each upgrade also takes the rarity below, at a Workbench -
#        or None (no recipe: admin give only until the loot pass, Skyy's decision 5),
#  id style "word" = Skyy_Talisman_<Key>_<Common|Uncommon|Rare|Epic> (the folded lines, their legacy ids kept) or "T" =
#        Skyy_Talisman_<Key>_T1..T4 (the new lines, spec 5.3))
SRC_FOLDED = ["Craft", "Craft+Drop", "Craft+Chest", "Craft+Boss"]
BOOSTERS = [
    ("Vitality", "Health", "Health", "Red", "Rock_Gem_Ruby",
     [("flat", "maxHealth", [6, 12, 18, 24])], SRC_FOLDED, "A warm pulse that steadies the heart.", [
        [("Ingredient_Crystal_Red", 2), ("Ingredient_Life_Essence", 5), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Red", 3), ("Ingredient_Life_Essence", 10), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Ruby", 1), ("Ingredient_Bar_Iron", 10), ("Ingredient_Life_Essence", 30)],
        [("Rock_Gem_Ruby", 3), ("Ingredient_Bar_Thorium", 10), ("Ingredient_Life_Essence_Concentrated", 2)],
     ], "word"),
    ("Endurance", "Stamina", "Stamina", "Yellow", "Rock_Gem_Topaz",
     [("flat", "maxStamina", [3, 6, 9, 12]), ("regenPct", "staminaRegen", [2.5, 5, 7.5, 10])], SRC_FOLDED,   # 0.5.1: Skyy
     "It hums faster the harder you breathe.", [
        [("Ingredient_Crystal_Yellow", 2), ("Ingredient_Leather_Light", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Yellow", 3), ("Ingredient_Leather_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Topaz", 1), ("Ingredient_Leather_Medium", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Topaz", 3), ("Ingredient_Leather_Heavy", 15), ("Ingredient_Bar_Thorium", 10)],
     ], "word"),
    ("Intelligence", "Mana", "Mana", "Blue", "Rock_Gem_Sapphire",
     [("pct", "manaPct", [6, 12, 18, 24]), ("floor", "manaFloor", [1, 2, 3, 4])], SRC_FOLDED,
     "Cold to the touch, and full of quiet thoughts.", [
        [("Ingredient_Crystal_Blue", 2), ("Ingredient_Fabric_Scrap_Linen", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Blue", 3), ("Ingredient_Fabric_Scrap_Linen", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Sapphire", 1), ("Ingredient_Fabric_Scrap_Silk", 10), ("Ingredient_Bar_Silver", 5)],
        [("Rock_Gem_Sapphire", 3), ("Ingredient_Bolt_Cindercloth", 5), ("Ingredient_Bar_Cobalt", 10)],
     ], "word"),
    ("Regeneration", "Regeneration", "Regeneration", "Green", "Rock_Gem_Emerald",
     [("pct", "healPct", [0.25, 0.5, 0.75, 1.0])], SRC_FOLDED, "Moss grows back on it overnight.", [
        [("Ingredient_Crystal_Green", 2), ("Ingredient_Life_Essence", 10), ("Ingredient_Tree_Sap", 3)],
        [("Ingredient_Crystal_Green", 3), ("Ingredient_Life_Essence", 20), ("Ingredient_Tree_Sap", 5)],
        [("Rock_Gem_Emerald", 1), ("Ingredient_Life_Essence", 50), ("Ingredient_Bar_Gold", 5)],
        [("Rock_Gem_Emerald", 3), ("Ingredient_Life_Essence_Concentrated", 3), ("Ingredient_Bar_Cobalt", 10)],
     ], "word"),
    ("Speed", "Speed", "Speed", "Cyan", "Rock_Gem_Zephyr",
     [("pct", "speedPct", [2.5, 5, 7.5, 10])], SRC_FOLDED, "The wind always seems to be at your back.", [
        [("Ingredient_Crystal_Cyan", 2), ("Ingredient_Feathers_Light", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Cyan", 3), ("Ingredient_Feathers_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Zephyr", 1), ("Ingredient_Feathers_Blue", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Zephyr", 3), ("Ingredient_Lightning_Essence", 10), ("Ingredient_Bar_Cobalt", 10)],
     ], "word"),
    # ---- part 2 (spec 2.3, 2.4): no recipes, ids _T1.._T4
    ("Strength", "Strength", "Brawler", None,
     ["Ingredient_Bone_Fragment", "Ingredient_Sinue_Cindersinue", "Ingredient_Fire_Essence", "Ingredient_Voidheart"],
     [("flat", "str", [3, 6, 9, 12])], ["Drop", "Combine", "Craft", "Boss"], "Scuffed wraps from a hundred fights.", None, "T"),
    ("MagicPower", "MagicPower", "Runic", "Purple", "Rock_Gem_Voidstone",
     [("flat", "mp", [3, 6, 9, 12])], ["Chest", "Combine", "Craft", "Boss"], "Faint runes crawl across it when you cast.", None, "T"),
    ("Defense", "Defense", "Stonehide", "White", "Rock_Crystal_Iridescent_Large",
     [("flat", "def", [3, 6, 9, 12])], ["Drop", "Combine", "Craft", "Boss"], "Heavy as a boulder, and just as stubborn.", None, "T"),
    ("Crit", "Crit", "Razorfang", "Pink", "Rock_Crystal_Iridescent_Medium",
     [("chancePct", "cc", [2, 4, 6, 8]), ("damagePct", "cd", [4, 8, 12, 16])], ["Chest", "Combine", "Craft", "Boss"],
     "Its edge always finds the gap in the armor.", None, "T"),
    ("Feather", "Feather", "Feather", None,
     ["Ingredient_Feathers_Light", "Ingredient_Feathers_Blue", "Ingredient_Ice_Essence", "Ingredient_Motes_Light"],
     [("fallPct", "fallPct", [10, 20, 30, 40]), ("jumpPct", "jumpPct", [5, 10, 15, 20])], ["Craft", "Craft", "Chest", "Chest"],
     "Lighter than it has any right to be.", None, "T"),
]
# THE STAT ALLOWLIST (spec 1.4; Skyy's decision 6: "stats that do nothing yet must NEVER be on a booster"): kind -> (config unit,
# whole numbers only, cap, what applies it in game). A row using any other kind stops the build. Never dmg, element damage, tdmg,
# spd or stam through gear:extra, or a key SkyyGear marks "later" (it accepts them and does nothing - a booster would lie).
STAT_KINDS = {
    "maxHealth":    ("flat", False, 1000, "stat map key skyyacc_health (StaticModifier MAX, ADDITIVE)"),
    "maxStamina":   ("flat", False, 1000, "stat map key skyyacc_stamina (StaticModifier MAX, ADDITIVE)"),
    "staminaRegen": ("pct",  False, 100,  "the Stamina Regen top-up: addStatValue(Stamina) while vanilla's own refill runs (AccEffects.staminaRegen)"),
    "manaPct":      ("pct",  False, 100,  "stat map key skyyacc_mana (MAX, ADDITIVE): percent of the flat Mana, never less than manaFloor"),
    "manaFloor":    ("flat", False, 1000, "the least the Mana line adds (with manaPct in the same line)"),
    "healPct":      ("pct",  False, 100,  "addStatValue(Health) every regenEverySeconds, percent of max Health"),
    "speedPct":     ("pct",  False, 100,  "movement protocol source accessories.talismans, layer pct, speed"),
    # part 2: SkyyGear 0.1 (live) reads gear:extra:<uuid> on every hit (VERIFIED: GearStats.totals(..., withExtra = true) in the
    # offence and Defense handlers); SkyyGear floors each part, so these take whole numbers only
    "str":          ("flat", True,  1000, "gear:extra key str - SkyyGear: +1% damage per point (melee, arrows, thrown weapons, staff melee)"),
    "mp":           ("flat", True,  1000, "gear:extra key mp - SkyyGear: +1% spell damage per point"),
    "def":          ("flat", True,  1000, "gear:extra key def - SkyyGear: mob and player hits x 100 / (100 + Defense)"),
    "cc":           ("pct",  True,  100,  "gear:extra key cc - SkyyGear: Crit Chance in percent (base 0)"),
    "cd":           ("pct",  True,  100,  "gear:extra key cd - SkyyGear: Crit Damage in percent (rides with cc on one line)"),
    "fallPct":      ("pct",  False, 100,  "movement protocol source accessories.talismans, fallDamage (pct layer, negated) - applied by SkyySkills"),
    "jumpPct":      ("pct",  False, 100,  "movement protocol source accessories.talismans, jump (pct layer) - applied by MoveSync.sync"),
}
# the gear:extra keys (spec 5.4): kind -> SkyyGear stat key; the ONLY keys SkyyAccessories may write (lsteal joins in wave 2)
GEAR_ALLOW = ("str", "mp", "def", "cc", "cd")
GEAR_KEYS = sorted(GEAR_ALLOW)                  # the text lists them in this order: "cc:8,cd:16,def:12,mp:12,str:12"
STAT_GEAR = {"str": "str", "mp": "mp", "def": "def", "cc": "cc", "cd": "cd"}
GEAR_NEVER = ("dmg", "tdmg", "spd", "stam", "fEarth", "fFire", "fWater", "fAir", "fThunder", "lsteal")
# kinds that only ride along with another kind of the same line (one tooltip template, one bag-page part with it)
RIDERS = {"manaFloor": "manaPct", "cd": "cc", "jumpPct": "fallPct", "staminaRegen": "maxStamina"}
ENTRIES = []      # config entries "<Admin>.<stat>" in table order: (key, line index, kind, [Normal, Unique, Rare, Legendary])
for _li, _b in enumerate(BOOSTERS):
    for _st, _kind, _vals in _b[5]:
        ENTRIES.append(("%s.%s" % (_b[1], _st), _li, _kind, list(_vals)))
E = dict((_e[0], _i) for _i, _e in enumerate(ENTRIES))
KIND_E = dict((_e[2], _i) for _i, _e in enumerate(ENTRIES))
LI = dict((_b[1], _i) for _i, _b in enumerate(BOOSTERS))


def booster_id(b, t):
    """the item id of rarity t (1..4) of table row b (its id style)"""
    return "Skyy_Talisman_%s_%s" % (b[0], ID_WORD[t]) if b[9] == "word" else "Skyy_Talisman_%s_T%d" % (b[0], t)


LINE_IDS = [booster_id(_b, _t) for _b in BOOSTERS for _t in range(1, 5)]   # [line * 4 + tier - 1]
LINE_SRC = [_b[6][_t - 1] for _b in BOOSTERS for _t in range(1, 5)]
BOOST_DEF = [",".join("%g" % _v for _v in _e[3]) for _e in ENTRIES]
FOLDED = [_b for _b in BOOSTERS if _b[9] == "word"]      # the 0.4.x lines: word ids, legacy ids, Workbench recipes
E_GEAR = [STAT_GEAR.get(_e[2], "") for _e in ENTRIES]    # per entry: its gear:extra key or ""
COMBAT_LINES = [_b[2] for _li, _b in enumerate(BOOSTERS) if any(E_GEAR[_i] for _i, _e in enumerate(ENTRIES) if _e[1] == _li)]


def _table_checks():
    """the table rules (spec 6.1 / 6.2 build checks); the harness runs them again"""
    import re as _re
    fams, admins, names, kinds = [b[0] for b in BOOSTERS], [b[1] for b in BOOSTERS], [b[2] for b in BOOSTERS], []
    for lst, what in ((fams, "family key"), (admins, "admin name"), (names, "line name")):
        assert len(set(lst)) == len(lst), "duplicate %s: %s" % (what, lst)
    words = [w for w in ID_WORD[1:]] + [w for w, _t in LEGACY_WORDS]
    for b in BOOSTERS:
        fam, adm, line, crystal, gem, stats, src, flavour, recipes, style = b
        assert _re.match(r"^[A-Z][A-Za-z]+$", fam) and not any(fam.endswith(w) for w in words), "family key %r: CamelCase, no _, " \
            "not ending in an id word or legacy word" % fam
        assert _re.match(r"^[A-Z][A-Za-z]+$", adm) and _re.match(r"^[A-Z][A-Za-z]+$", line), (adm, line)
        assert len(src) == MAX_LINE_RARITY and all(all(w in SOURCE_WORDS for w in x.split("+")) for x in src), (fam, src)
        assert style in ("word", "T"), (fam, style)
        if style == "word":
            assert recipes is not None and len(recipes) == MAX_LINE_RARITY, (fam, "a folded line keeps its 4 Workbench steps")
        else:
            assert recipes is None, (fam, "new lines have no recipe (Skyy: acquisition later - admin give only)")
        if crystal is None:
            assert isinstance(gem, list) and len(gem) == MAX_LINE_RARITY and len(set(gem)) == 4, (fam, "4 look items, one per rarity")
        else:
            assert _re.match(r"^[A-Z][a-z]+$", crystal) and isinstance(gem, str), (fam, crystal, gem)
        assert flavour and "." in flavour and all(ord(ch) < 128 for ch in flavour), flavour
        for st, kind, vals in stats:
            assert kind in STAT_KINDS, "%s uses the stat kind %r, which is not in the allowlist STAT_KINDS (spec 1.4)" % (fam, kind)
            unit, whole, cap, _how = STAT_KINDS[kind]
            assert _re.match(r"^[a-z][A-Za-z]*$", st), st
            assert len(vals) == MAX_LINE_RARITY, "%s.%s needs exactly 4 numbers (Normal..Legendary): %r" % (adm, st, vals)
            for v in vals:
                assert 0 <= v <= cap and round(v, 2) == v and (not whole or v == int(v)), (adm, st, v)
            assert list(vals) == sorted(vals) and vals[0] > 0, "%s.%s must grow with the rarity: %r" % (adm, st, vals)
            kinds.append(kind)
        ks = [k for _s, k, _v in stats]
        for rider, main in RIDERS.items():
            assert (rider in ks) <= (main in ks), "%s goes with %s in one line" % (rider, main)
        assert len([k for k in ks if k not in RIDERS]) == 1, "%s: exactly one main stat (the rest ride along): %s" % (adm, ks)
    assert len(set(kinds)) == len(kinds), "one line per stat kind (spec 1.1: one line per stat)"
    assert len(set(LINE_IDS)) == len(LINE_IDS) == 4 * len(BOOSTERS), "two rarities share an id"
    assert len(set(e[0] for e in ENTRIES)) == len(ENTRIES)
    assert ACC_AP[1:5] == [10, 13, 16, 19] and all(10 <= a <= 25 for a in ACC_AP[1:]), ACC_AP   # locked +10 to +25 (locks 111-113)
    assert DISPLAY[1:5] == ["Normal", "Unique", "Rare", "Legendary"] and MAX_LINE_RARITY == 4
    # part 2: gear:extra - only the allowlist, whole numbers, never a key SkyyGear keeps for weapons / armor or "later"
    for k, g in STAT_GEAR.items():
        assert g in GEAR_ALLOW and g not in GEAR_NEVER and STAT_KINDS[k][1], "gear:extra key %r is outside str mp def cc cd" % g
    assert set(GEAR_ALLOW) == set(STAT_GEAR.values()) and not set(GEAR_ALLOW) & set(GEAR_NEVER)
    assert all(g == "" or g in GEAR_ALLOW for g in E_GEAR)
    # part 2 ids: _T1.._T4, never the bench prefix, never ending in a legacy word (modernOf would rebuild them)
    for b in BOOSTERS:
        if b[9] != "T":
            continue
        for t in range(1, 5):
            i = booster_id(b, t)
            assert i.startswith("Skyy_Talisman_") and not i.startswith("Skyy_Accessory_") and i.endswith("_T%d" % t), i
            assert not any(i.endswith("_" + w) for w, _t in LEGACY_WORDS), i
    assert len(BOOSTERS) + 2 <= BONUS_MAX, "the Bonuses well holds one row per line + 2 notes (%d lines)" % len(BOOSTERS)


_table_checks()
# ---- BOOSTER TABLE END
assert [_b[0] for _b in BOOSTERS] == ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed", "Strength", "MagicPower",
                                     "Defense", "Crit", "Feather"], "the five folded lines + the five part 2 lines"
assert [_b[0] for _b in FOLDED] == ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed"]
assert BOOST_DEF == ["6,12,18,24", "3,6,9,12", "2.5,5,7.5,10", "6,12,18,24", "1,2,3,4", "0.25,0.5,0.75,1", "2.5,5,7.5,10",
                     "3,6,9,12", "3,6,9,12", "3,6,9,12", "2,4,6,8", "4,8,12,16", "10,20,30,40", "5,10,15,20"], BOOST_DEF
assert [_e[0] for _e in ENTRIES][7:] == ["Strength.flat", "MagicPower.flat", "Defense.flat", "Crit.chancePct", "Crit.damagePct",
                                         "Feather.fallPct", "Feather.jumpPct"], "the spec 5.8 part 2 entry names"
assert COMBAT_LINES == ["Brawler", "Runic", "Stonehide", "Razorfang"], COMBAT_LINES
# the numbers are exact float32 values (the loader computes (float) of the parsed text; the jar literals are "%.4ff")
import struct as _struct
def _f32(x):
    return _struct.unpack("<f", _struct.pack("<f", x))[0]
assert all(_f32(v) == v for _e in ENTRIES for v in _e[3]), "a booster default is not exact in float32"
# the rarity look: frame art = SkyyGear's Skyy_Gear_* table (tooltip + arrow texture quality, slot texture quality, drop particle);
# colours = the kit's rarity palette (the same hexes as SkyyGear / SkyySacks); the six quality assets Skyy_Acc_<Rarity>
QUAL_IDS = [""] + ["Skyy_Acc_" + _r for _r in DISPLAY[1:]]
QUAL_ART = {"Normal": ("Common", "Common", "Drop_Common"), "Unique": ("Legendary", "Legendary", "Drop_Legendary"),
            "Rare": ("Epic", "Epic", "Drop_Epic"), "Legendary": ("Rare", "Rare", "Drop_Rare"),
            "Fabled": ("Common", "Developer", "Drop_Legendary"), "Mythic": ("Epic", "Epic", "Drop_Epic")}
RARITY_COLORS = ["#ffffff"] + [SUI.RARITY[_r] for _r in DISPLAY[1:]]
BENCH_RARITY = [0, 1, 2, 3, 4, 4, 4, 4]   # bench tier I Normal, II Unique, III Rare, IV and up Legendary (crafted: stops at Legendary)


def _gear_art_check():
    """SkyyAccessories ships its own qualities (every Skyy mod works alone), but the look must match SkyyGear's ladder"""
    import re as _re, glob as _glob
    def _v(p):
        m = _re.search(r"_(\d+(?:\.\d+)*)\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(_glob.glob(os.path.join(HERE, "..", "SkyyGear", "build_skyygear_*.py")), key=_v)
    if not found:
        print("note: no SkyyGear build script next to this mod - the Skyy_Acc_* frame art is not cross-checked")
        return
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    rows = _re.findall(r'^\s*\("(\w+)", "(\w+)", "(#[0-9A-Fa-f]{6})", "#[0-9A-Fa-f]{6}", "(\w+)", "(\w+)", "(\w+)"\),', txt, _re.M)
    got = dict((nm, (col.lower(), (tt, sl, pt))) for _rid, nm, col, tt, sl, pt in rows)
    for r in DISPLAY[1:]:
        if r not in got:
            raise SystemExit("0.5: %s has no %s row in its RARITIES table - update _gear_art_check" % (os.path.basename(found[-1]), r))
        if got[r][1] != QUAL_ART[r] or got[r][0] != SUI.RARITY[r].lower():
            raise SystemExit("0.5: the %s look differs from %s (%r vs %r) - update QUAL_ART" % (r, os.path.basename(found[-1]), got[r], (SUI.RARITY[r], QUAL_ART[r])))
    print("rarity look matches %s (%s)" % (os.path.basename(found[-1]), ", ".join(DISPLAY[1:])))


_gear_art_check()

# ---- the Python mirror of the Java id rules (AccDefs.tailTier / tierOf / familyOf / isLegacy / modernOf / rarityOf) + the fold checks
def py_family(iid):
    tail = iid[len("Skyy_Talisman_"):]
    k = tail.rfind("_")
    return tail[:k] if k > 0 else tail
def py_tail_tier(iid):
    w = iid[iid.rfind("_") + 1:]
    return int(w[1:]) if len(w) >= 2 and w[0] == "T" and w[1:].isdigit() else -1
def py_tier(iid):
    if py_tail_tier(iid) > 0:
        return py_tail_tier(iid)
    for r in range(len(ID_WORD) - 1, 0, -1):
        if iid.endswith("_" + ID_WORD[r]):
            return r
    for w, t in LEGACY_WORDS:
        if iid.endswith("_" + w):
            return t
    return 1
def py_legacy(iid):
    return py_tail_tier(iid) <= 0 and any(iid.endswith("_" + w) for w, _t in LEGACY_WORDS)
def py_modern(iid):
    return "Skyy_Talisman_%s_%s" % (py_family(iid), ID_WORD[py_tier(iid)]) if py_legacy(iid) else iid
def old_tier(iid):   # SkyyAccessories 0.4.5 AccDefs.tierOf on talisman ids (Common 1 .. Legendary 5; Talisman 2, Ring 3, Artifact 4)
    for r, w in ((5, "Legendary"), (4, "Epic"), (3, "Rare"), (2, "Uncommon"), (1, "Common")):
        if iid.endswith("_" + w):
            return r
    return {"Artifact": 4, "Ring": 3, "Talisman": 2}.get(iid[iid.rfind("_") + 1:], 1)
OLD_IDS = ["Skyy_Talisman_%s_%s" % (_b[0], _w) for _b in FOLDED for _w in ("Common", "Uncommon", "Rare", "Epic", "Legendary")]
LEGACY_IDS = ["Skyy_Talisman_%s_%s" % (_b[0], _w) for _b in FOLDED for _w, _t in LEGACY_WORDS]
FOLDED_IDS = [booster_id(_b, _t) for _b in FOLDED for _t in range(1, 5)]
NEW_IDS = [booster_id(_b, _t) for _b in BOOSTERS if _b[9] == "T" for _t in range(1, 5)]
assert len(OLD_IDS) == 25 and len(LEGACY_IDS) == 20 and set(FOLDED_IDS) < set(OLD_IDS) and len(NEW_IDS) == 20
assert not set(NEW_IDS) & set(OLD_IDS + LEGACY_IDS) and sorted(FOLDED_IDS + NEW_IDS) == sorted(LINE_IDS)
for _li, _b in enumerate(BOOSTERS):
    for _t in range(1, 5):
        _i = LINE_IDS[_li * 4 + _t - 1]
        assert py_tier(_i) == _t and py_family(_i) == _b[0] and not py_legacy(_i) and py_modern(_i) == _i, _i
        assert (py_tail_tier(_i) == _t) == (_b[9] == "T"), _i       # part 2: the _T<n> tail parses first
    if _b[9] != "word":
        continue
    for _w, _t in LEGACY_WORDS:
        _i = "Skyy_Talisman_%s_%s" % (_b[0], _w)
        assert py_legacy(_i) and py_tier(_i) == _t and py_family(_i) == _b[0] and py_modern(_i) == LINE_IDS[_li * 4 + _t - 1], _i
assert py_modern("Skyy_Talisman_Vitality_Legendary") == "Skyy_Talisman_Vitality_Epic"
assert py_tier("Skyy_Talisman_Crit_T4") == 4 and py_family("Skyy_Talisman_MagicPower_T2") == "MagicPower"
# the equip swap order (AccStore.equipK: a higher tier of the same line swaps in, equal or lower is refused) is 0.4.5's for every pair
# of the 40 old ids of a line, except that the old fifth id (_Legendary) now TIES with the other tier-4 ids (_Epic and _Artifact)
_sgn = lambda x: (x > 0) - (x < 0)
for _b in FOLDED:
    _ids = sorted(set(i for i in OLD_IDS + LEGACY_IDS if py_family(i) == _b[0]))   # the 5 + 3 ids 0.4.5 knew (_Legendary is in both lists)

    assert len(_ids) == 8, _ids
    for _a in _ids:
        for _c in _ids:
            _o, _n = _sgn(old_tier(_a) - old_tier(_c)), _sgn(py_tier(_a) - py_tier(_c))
            if _o != _n:
                assert _n == 0 and "_Legendary" in (_a[-10:], _c[-10:]) and 4 in (old_tier(_a), old_tier(_c)), (_a, _c, _o, _n)

# ---- 0.5 CONFIG (the defaults file = the kit's DEFAULTS; AccCfg.migrate appends the lines from "notice.boosters" on to a 0.4.x file)
# groups of new keys: (comment lines, [(key, value), ...]) - the migration writes a group's comments before its first missing key
# 0.5.1 STAMINA (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01: double the max Stamina, half the Stamina Regen). AccCfg.migrate051 rewrites a
# boost.Stamina.flat / boost.Stamina.regenPct line that still holds these 0.5 numbers (the SkyyGear 0.1.1 migrateStat011 rules)
M51_OLD = [("Stamina.flat", "1.5,3,4.5,6"), ("Stamina.regenPct", "5,10,15,20")]
M51_KEYS = [_k for _k, _o in M51_OLD]
M51_NEW = [BOOST_DEF[E[_k]] for _k in M51_KEYS]
assert M51_NEW == ["3,6,9,12", "2.5,5,7.5,10"] and all(_k in E for _k in M51_KEYS), M51_NEW
# the marker (in the 0.5.1 default text and in every updated file): a doc comment with spaces and no '=', so the kit never takes it for
# a "#key=value" template line; migrate051 looks for M51_MARK_ID in comment lines only
M51_MARK_ID = "SkyyAccessories 0.5.1 Stamina defaults"
M51_MARK = ("# %s (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01): max Stamina doubled to 3,6,9,12 and Stamina Regen halved "
            "to 2.5,5,7.5,10 (0.5: 1.5,3,4.5,6 and 5,10,15,20)." % M51_MARK_ID)
# the name on the update's config-changes.log lines and its History version: a fixed literal (SkyyGear 0.1.1 review finding 5)
M51_WHO = "SkyyAccessories 0.5.1"
assert all(32 <= ord(_c) < 127 for _c in M51_MARK) and "=" not in M51_MARK and M51_MARK.startswith("# ")
ADD_GROUPS = [
    (["# Tell players once, in chat, about the 0.5 accessory change (only players who had accessories before 0.5): true or false."],
     [("notice.boosters", "true")]),
    (["# Line switches: false = the line stays in the bag, counts for nothing and the Accessory Bag page says it is switched off."],
     [("line.%s" % _b[1], "true") for _b in BOOSTERS]),
    (["# Send the combat stats of the %s accessories to SkyyGear (true or false; false = they add nothing)." % ", ".join(COMBAT_LINES)],
     [("combatToGear", "true")]),
    (["# Booster numbers: four numbers for Normal,Unique,Rare,Legendary (no minus sign, up to 2 decimals). The entry name gives the",
      "# unit: flat = added to your maximum (Strength, MagicPower, Defense: whole points), pct = percent (Mana: of your Mana;",
      "# Regeneration: of max Health healed every regenEverySeconds; Speed: faster movement), chancePct / damagePct = whole percent",
      "# Crit Chance / Crit Damage, regenPct = percent faster Stamina refill, floor = the least the Mana line adds, fallPct = percent",
      "# less fall damage (written without a minus), jumpPct = percent higher jumps. The item tooltips print the built-in numbers;",
      "# the Accessory Bag page and /accessories lines show the ones below.", M51_MARK],
     [("boost." + _e[0], BOOST_DEF[_i]) for _i, _e in enumerate(ENTRIES)]),
]
CONFIG_TEXT = "\n".join([
    "# SkyyAccessories settings. Change them in game: SkyWynn Menu -> Server Setup -> Accessories, or edit this file",
    "# and run /accessories reload (server admins: skyyaccessories.admin). Every change is logged in config-changes.log.",
    "#",
    "# Accessory bag slots every player can fill, 1-%d. Lowering it deletes nothing: accessories already in a higher slot stay," % CAP,
    "# keep counting and can still be unequipped - only a newly equipped accessory needs a free slot within the limit.",
    "slots=%d" % SLOTS_DEF,
    "# How often the Regeneration Accessory heals, in seconds (1-%d)." % REGEN_MAX,
    "regenEverySeconds=%d" % REGEN_EVERY,
] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + [""])
assert all(ord(ch) < 128 for ch in CONFIG_TEXT), "config text must stay ASCII"
# the 0.4.x lines the migration handles (spec 5.1): bonus.<family> with its untouched default and where an EDITED list goes ("" = its
# unit changed, it is dropped and logged); the 0.4.4 / 0.4.5 default comment lines it rewrites ("" = removed)
OLD_BONUS = [("Vitality", "2,4,6,8,10", "", "its unit changed from percent to flat - set boost.Health.flat by hand"),
             ("Endurance", "2,4,6,8,10", "", "its unit changed from percent to flat - set boost.Stamina.flat by hand"),
             ("Intelligence", "2,4,6,8,10", "Mana.pct", ""),
             ("Regeneration", "0.5,1,1.5,2,3", "Regeneration.pct", ""),
             ("Speed", "2,4,6,8,10", "Speed.pct", "")]
assert all(c == "" or c in E for _f, _d, c, _n in OLD_BONUS)
OLD_COMMENTS = [
    ("# Accessory bag slots every player can fill, 1-9. Lowering it deletes nothing: accessories already in a higher slot stay,",
     "# Accessory bag slots every player can fill, 1-%d. Lowering it deletes nothing: accessories already in a higher slot stay," % CAP),
    ("# How often the Regeneration talisman heals, in seconds (1-30).", "# How often the Regeneration Accessory heals, in seconds (1-%d)." % REGEN_MAX),
    ("# Talisman bonuses in percent for Common,Uncommon,Rare,Epic,Legendary (0-100 each, up to 2 decimals), one line per family.", ""),
    ("# Vitality / Endurance / Intelligence = percent of your flat max Health / Stamina / Mana, Regeneration = percent of max Health", ""),
    ("# healed every regenEverySeconds, Speed = percent movement speed. The item tooltips keep printing the built-in numbers", ""),
    ("# (2,4,6,8,10, Regeneration 0.5,1,1.5,2,3); the Accessory Bag page shows the ones below.", ""),
]
ADD_KEY = [k for _g, (_n, _ks) in enumerate(ADD_GROUPS) for k, _v in _ks]
ADD_VAL = [v for _g, (_n, _ks) in enumerate(ADD_GROUPS) for _k, v in _ks]
ADD_GROUP = [_g for _g, (_n, _ks) in enumerate(ADD_GROUPS) for _k, _v in _ks]
GROUP_NOTE = ["\n".join(_n) for _n, _ks in ADD_GROUPS]
MIG_NOTICE = ("[Accessories] Your talismans are now accessories: Health, Stamina, Mana, Regeneration and Speed Accessory, in the gear "
              "rarities Normal, Unique, Rare and Legendary, with new numbers. Stamina now also refills faster. /accessories lines "
              "shows every line.")   # spec 5.1 (the one place where the old word "talismans" reaches a player: it names what they had)


def jlit(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
def jstrs(xs):
    return ", ".join(jlit(x) for x in xs)
def JX(src):
    return src.replace("@PKG@", PKG)
def jfloats(vals, scale=1.0):
    return ", ".join("%.4ff" % (v * scale) for v in [0] + list(vals))
# 0.5: Java written with @TOKEN@ class names (no f-string brace doubling in the new code)
_TOK = {"PKG": PKG, "PR": PR, "REF": REF, "ST": ST, "UNI": UNI, "WLD": WLD, "MSG": MSG, "PLA": PLA, "INV": INV, "IC": IC, "IS": IS,
        "IST": IST, "ISS": ISS, "ESM": ESM, "ESV": ESV, "DST": DST, "MOD": MOD, "SMO": SMO, "MTG": MTG, "CAL": CAL, "CB": CB,
        "ACH": ACH, "QRY": QRY, "CTX": CTX, "EVD": EVD, "BT": BT, "UCB": UCB, "UEB": UEB, "RGV": RGV, "RGN": RGN, "RGT": RGT,
        "CND": CND, "TMR": TMR, "SIC": SIC, "ITM": ITM, "EST": EST}
def JT(src):
    out = src
    for _k, _v in _TOK.items():
        out = out.replace("@%s@" % _k, _v)
    assert "@" not in out, "unresolved @TOKEN@ in: " + out[:160]
    return out
def JM(cls, src):
    cls.addMethod(CtNewMethod.make(JT(src), cls))
def JF(cls, src):
    cls.addField(CtField.make(JT(src), cls))

# ================= AccDefs =================
bench_ids = ", ".join('"%s"' % b[0] for b in ACTIVE)     # 0.4.2: ACTIVE benches only (the Omni's synthetic grants)
bench_names = ", ".join('"%s"' % b[2] for b in ACTIVE)
assert '"Campfire"' in bench_ids and '"Alchemybench"' not in bench_ids and '"Cookingbench"' not in bench_ids, bench_ids   # 0.4.3
dfs.addField(CtField.make('public static final String BAG = "%s";' % BAG, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_IDS = new String[] { %s };' % bench_ids, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_NAMES = new String[] { %s };' % bench_names, dfs))
# 0.5: THE BOOSTER TABLE as flat 1-D arrays (javassist compiles no [][]): per line (FAMILIES order), per line x 4 + tier - 1, per entry
dfs.addField(CtField.make('public static final String[] FAMILIES = new String[] { %s };' % jstrs(b[0] for b in BOOSTERS), dfs))   # family keys (item ids only)
dfs.addField(CtField.make('public static final String[] LINE_ADMIN = new String[] { %s };' % jstrs(b[1] for b in BOOSTERS), dfs))   # config, commands, acc:defs
dfs.addField(CtField.make('public static final String[] LINE_NAME = new String[] { %s };' % jstrs(b[2] for b in BOOSTERS), dfs))    # "<Rarity> <Line> Accessory"
dfs.addField(CtField.make('public static final String[] LINE_IDS = new String[] { %s };' % jstrs(LINE_IDS), dfs))
dfs.addField(CtField.make('public static final String[] LINE_SRC = new String[] { %s };' % jstrs(LINE_SRC), dfs))
dfs.addField(CtField.make('public static final String[] ID_WORD = new String[] { %s };' % jstrs(ID_WORD), dfs))   # ids only (tier 1..4)
dfs.addField(CtField.make('public static final String[] LEGACY_WORD = new String[] { %s };' % jstrs(w for w, t in LEGACY_WORDS), dfs))
dfs.addField(CtField.make('public static final int[] LEGACY_TIER = new int[] { %s };' % ", ".join(str(t) for w, t in LEGACY_WORDS), dfs))
dfs.addField(CtField.make('public static final String[] DISPLAY = new String[] { %s };' % jstrs(DISPLAY), dfs))   # rarity 1..6
dfs.addField(CtField.make('public static final String[] RARITY_COLOR = new String[] { %s };' % jstrs(RARITY_COLORS), dfs))   # kit colours
dfs.addField(CtField.make('public static final int[] AP = new int[] { %s };' % ", ".join(str(a) for a in ACC_AP), dfs))
dfs.addField(CtField.make('public static final String[] E_KEYS = new String[] { %s };' % jstrs(e[0] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int[] E_LINE = new int[] { %s };' % ", ".join(str(e[1]) for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final String[] E_UNIT = new String[] { %s };' % jstrs(STAT_KINDS[e[2]][0] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int[] E_WHOLE = new int[] { %s };' % ", ".join("1" if STAT_KINDS[e[2]][1] else "0" for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final float[] E_CAP = new float[] { %s };' % ", ".join("%d.0f" % STAT_KINDS[e[2]][2] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int BONUS_MAX = %d;' % BONUS_MAX, dfs))
# the live numbers [entry * 5 + tier] (tier 0 = no accessory = 0), in the config unit (Speed / Regeneration in percent); AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile float[] BOOST = new float[] { %s };' % ", ".join(jfloats(e[3]) for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static volatile int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))   # 0.4.4: config row regenEverySeconds (kit field:)
for _b in BOOSTERS:   # 0.5: the line switches (kit field: rows line.<Admin>, live kill switches, on by default - Skyy's decision 6)
    dfs.addField(CtField.make('public static volatile boolean LINE_%s = true;' % _b[1].upper(), dfs))
dfs.addField(CtField.make('public static volatile boolean NOTICE = true;', dfs))   # 0.5: config row notice.boosters
# 0.5 part 2: the gear:extra key of each entry ("" = not a combat stat), the allowlist in text order, config row combatToGear, and the
# entries of the movement parts (-1 = no such entry)
dfs.addField(CtField.make('public static final String[] E_GEAR = new String[] { %s };' % jstrs(E_GEAR), dfs))
dfs.addField(CtField.make('public static final String[] GEAR_KEYS = new String[] { %s };' % jstrs(GEAR_KEYS), dfs))
dfs.addField(CtField.make('public static volatile boolean COMBAT_TO_GEAR = true;', dfs))
dfs.addField(CtField.make('public static final int E_SPEED = %d;' % KIND_E.get("speedPct", -1), dfs))
dfs.addField(CtField.make('public static final int E_JUMP = %d;' % KIND_E.get("jumpPct", -1), dfs))
dfs.addField(CtField.make('public static final int E_FALL = %d;' % KIND_E.get("fallPct", -1), dfs))
dfs.addField(CtField.make('public static final String OMNI = "%s";' % OMNI, dfs))
dfs.addField(CtField.make('public static final int[] BENCH_MAX = new int[] { %s };' % ", ".join(str(b[3]) for b in ACTIVE), dfs))
# 0.4.2: retired bench ids + display names (same index) and the grey used for them on the bag page
dfs.addField(CtField.make('public static final String[] RETIRED = new String[] { %s };' % ", ".join('"%s"' % r for r in RETIRED), dfs))
dfs.addField(CtField.make('public static final String[] RETIRED_NAMES = new String[] { %s };' % ", ".join('"%s"' % n for n in RETIRED_NAMES), dfs))
dfs.addField(CtField.make('public static final int[] RETIRED_MAX = new int[] { %s };' % ", ".join(str(m) for m in RETIRED_MAX), dfs))
dfs.addField(CtField.make('public static final String RETIRED_COLOR = "#8a97a3";', dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean isAccessory(String id) {
  if (id == null) return false;
  if (id.startsWith("Skyy_Talisman_")) return true;
  return id.startsWith("Skyy_Accessory_") && !id.equals(BAG);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean isTalisman(String id) {
  return id != null && id.startsWith("Skyy_Talisman_") && id.length() > "Skyy_Talisman_".length();
}""", dfs))
# "Skyy_Talisman_Vitality_Ring" -> "Vitality"
dfs.addMethod(CtNewMethod.make("""
public static String familyOf(String id) {
  if (!isTalisman(id)) return null;
  String tail = id.substring("Skyy_Talisman_".length());
  int k = tail.lastIndexOf('_');
  return k > 0 ? tail.substring(0, k) : tail;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static int familyIndex(String fam) {
  if (fam == null) return -1;
  for (int i = 0; i < FAMILIES.length; i++) if (FAMILIES[i].equals(fam)) return i;
  return -1;
}""", dfs))
# "Skyy_Accessory_Workbench_T2" -> "Workbench" ; ids without _T<n> -> whole tail
dfs.addMethod(CtNewMethod.make("""
public static String benchOf(String id) {
  if (!isAccessory(id) || isTalisman(id)) return null;
  String tail = id.substring("Skyy_Accessory_".length());
  int t = tail.lastIndexOf("_T");
  if (t > 0) {
    boolean digits = t + 2 < tail.length();
    for (int i = t + 2; i < tail.length(); i++) if (!Character.isDigit(tail.charAt(i))) digits = false;
    if (digits) return tail.substring(0, t);
  }
  return tail;
}""", dfs))
# 0.4.2: a retired bench accessory (Alchemy Bench T1-T4, Cooking Bench; 0.4.3: no longer the Campfire): kept as an item, does nothing
dfs.addMethod(CtNewMethod.make("""
public static boolean isRetired(String id) {
  if (id == null || isTalisman(id) || OMNI.equals(id)) return false;
  String b = benchOf(id);
  if (b == null) return false;
  for (int i = 0; i < RETIRED.length; i++) if (RETIRED[i].equalsIgnoreCase(b)) return true;
  return false;
}""", dfs))
# 0.4.2: Equip refusal on the page (one line, no commas / colons / parentheses) and the longer chat explanation
dfs.addMethod(CtNewMethod.make("""
public static String retiredWhy(String id) {
  String b = benchOf(id);
  if ("Alchemybench".equalsIgnoreCase(b)) return "Retired - brew at a real Alchemy Bench now - it takes ingredients from your Magic Bags";
  if ("Cookingbench".equalsIgnoreCase(b)) return "Retired - cook at a real Cooking Bench now - it takes ingredients from your Magic Bags";
  return "Retired - this accessory does nothing any more";   // 0.4.3: the Campfire is active again - no retired id reaches this
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String retiredChat(String id) {
  String b = benchOf(id);
  String tail = " This accessory does nothing any more and cannot be equipped. If one is still in your Accessory Bag, Unequip takes it out.";
  if ("Alchemybench".equalsIgnoreCase(b)) return "The Alchemy Bench accessory is retired: Alchemy is a skill now. Brew at a real Alchemy Bench - it takes ingredients straight from your Magic Bags." + tail;
  if ("Cookingbench".equalsIgnoreCase(b)) return "The Cooking Bench accessory is retired: Cooking is a skill now. Cook at a real Cooking Bench - it takes ingredients straight from your Magic Bags." + tail;
  return "This accessory is retired." + tail;   // 0.4.3: the Campfire is active again - no retired id reaches this
}""", dfs))
# 0.5: the tier of a "_T<digits>" tail (the part 2 line ids Skyy_Talisman_<Key>_T1..T4), else -1
JM(dfs, r"""
public static int tailTier(String id) {
  if (!isTalisman(id)) return -1;
  int k = id.lastIndexOf('_');
  if (k < 0 || k + 2 >= id.length() + 1) return -1;
  String w = id.substring(k + 1);
  if (w.length() < 2 || w.charAt(0) != 'T') return -1;
  for (int i = 1; i < w.length(); i++) if (!Character.isDigit(w.charAt(i))) return -1;
  try { return Integer.parseInt(w.substring(1)); } catch (Throwable e) { return -1; }
}""")
# 0.5 tier 1..4 of a stat accessory: a _T<n> tail, then the id words Common..Epic, then the legacy words (Talisman 2, Ring 3, Artifact 4,
# Legendary 4 - the old fifth id folds into Legendary); bench accessories keep their _T<n>
JM(dfs, r"""
public static int tierOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isTalisman(id)) {
    int tt = tailTier(id);
    if (tt > 0) return tt;
    for (int r = ID_WORD.length - 1; r >= 1; r--) if (id.endsWith("_" + ID_WORD[r])) return r;
    for (int j = 0; j < LEGACY_WORD.length; j++) if (id.endsWith("_" + LEGACY_WORD[j])) return LEGACY_TIER[j];
    return 1;
  }
  int t = id.lastIndexOf("_T");
  if (t < 0 || t + 2 >= id.length()) return 1;
  try { return Integer.parseInt(id.substring(t + 2)); } catch (Throwable e) { return 1; }
}""")
# 0.4 / 0.5: an old stat accessory id (0.2/0.3 Talisman / Ring / Artifact, and 0.4's fifth id _Legendary): asset kept, no recipe
JM(dfs, r"""
public static boolean isLegacy(String id) {
  if (!isTalisman(id) || tailTier(id) > 0) return false;
  for (int j = 0; j < LEGACY_WORD.length; j++) if (id.endsWith("_" + LEGACY_WORD[j])) return true;
  return false;
}""")
# "Skyy_Talisman_Vitality_Ring" -> "..._Rare", "Skyy_Talisman_Vitality_Legendary" -> "..._Epic" (Legendary); every other id unchanged
JM(dfs, r"""
public static String modernOf(String id) {
  if (!isLegacy(id)) return id;
  String f = familyOf(id);
  int t = tierOf(id);
  if (f == null || t < 1 || t >= ID_WORD.length) return id;
  return "Skyy_Talisman_" + f + "_" + ID_WORD[t];
}""")
# 0.5 rarity 1..4 (Normal..Legendary, the gear ladder) of every accessory: stat accessories by tier, bench I Normal, II Unique,
# III Rare, IV and up Legendary, the Omni Legendary (crafted: never above Legendary); 5 / 6 (Fabled / Mythic) are for the rare finds
JM(dfs, r"""
public static int rarityOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isRetired(id)) return 0;   // 0.4.2: retired - never counts (future accessory power reads rarityOf)
  if (OMNI.equals(id)) return 4;
  int t = tierOf(id);
  if (t < 1) t = 1;
  if (t > 4) t = 4;
  return t;
}""")
JM(dfs, r"""
public static String rarityName(String id) {
  if (isRetired(id)) return "Does nothing";   // 0.4.2: the page's rarity column for a retired accessory
  return DISPLAY[rarityOf(id)];
}""")
dfs.addMethod(CtNewMethod.make("""
public static String rarityColor(String id) {
  if (isRetired(id)) return RETIRED_COLOR;   // 0.4.2
  return RARITY_COLOR[rarityOf(id)];
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean hasOmni(String[] s) {
  if (s == null) return false;
  for (int i = 0; i < s.length; i++) if (OMNI.equals(s[i])) return true;
  return false;
}""", dfs))
# one-per-group key used by AccStore.equip: bench id for bench accessories, "T:<family>" for talismans
dfs.addMethod(CtNewMethod.make("""
public static String groupOf(String id) {
  if (isTalisman(id)) return "T:" + familyOf(id);
  return benchOf(id);
}""", dfs))
# highest tier per line (index = FAMILIES) among the bag slots - ONLY THE HIGHEST RARITY OF A LINE COUNTS (a duplicate that slipped in
# through stashK changes nothing: the maximum is taken)
dfs.addMethod(CtNewMethod.make("""
public static int[] bestTiers(String[] s) {
  int[] out = new int[FAMILIES.length];
  if (s == null) return out;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (!isTalisman(id)) continue;
    int f = familyIndex(familyOf(id));
    if (f < 0) continue;
    int t = tierOf(id);
    if (t > 4) t = 4;   // 0.5: Normal..Legendary
    if (t > out[f]) out[f] = t;
  }
  return out;
}""", dfs))
# 0.5: the Java of AccDefs.statParts (per line, the short texts of its stats at one tier, live numbers) and AccDefs.lineOn, generated
# from the booster table when this script runs (a new stat kind needs its text here and a tooltip in TIPS)
def _stat_code():
    TXT = {   # kind -> Java expression of one part ((v) = the number); manaFloor rides along with manaPct
        "maxHealth": '"+" + numText(v) + " max Health"',
        "maxStamina": '"+" + numText(v) + " max Stamina"',
        "staminaRegen": '"+" + numText(v) + "% Stamina Regen"',
        "healPct": '"Heals " + numText(v) + "% max Health every " + REGEN_EVERY + " s"',
        "speedPct": '"+" + numText(v) + "% Speed"',
        "str": '"+" + numText(v) + " Strength"',                  # part 2
        "mp": '"+" + numText(v) + " Magical Power"',
        "def": '"+" + numText(v) + " Defense"',
    }
    PAIRS = {   # part 2: two stats of one line on ONE part (the rider is left out when its number is 0)
        "cc": ("cd", '"+" + numText(a) + "% Crit Chance"', '"+" + numText(r) + "% Crit Damage"'),
        "fallPct": ("jumpPct", '"-" + numText(a) + "% fall damage"', '"+" + numText(r) + "% jump height"'),
    }
    lines = []
    for li, bo in enumerate(BOOSTERS):
        body = []
        ks = dict((kd, E[bo[1] + "." + st]) for st, kd, _v in bo[5])
        for st, kd, _v in bo[5]:
            e = str(E[bo[1] + "." + st])
            if kd in ("manaFloor", "cd", "jumpPct"):
                continue
            if kd in PAIRS:
                rk, ta, tr = PAIRS[kd]
                rx = ("b[" + str(ks[rk]) + " * 5 + t]") if rk in ks else "0.0f"
                body.append("    float a" + e + " = b[" + e + " * 5 + t];\n    float r" + e + " = " + rx + ";\n    String p" + e + " = \"\";\n"
                            "    if (a" + e + " > 0.0f) p" + e + " = " + ta.replace("(a)", "(a" + e + ")") + ";\n"
                            "    if (r" + e + " > 0.0f) p" + e + " = p" + e + " + (p" + e + ".length() > 0 ? \", \" : \"\") + " +
                            tr.replace("(r)", "(r" + e + ")") + ";\n    if (p" + e + ".length() > 0) out.add(p" + e + ");")
                continue
            if kd == "manaPct":
                fl = ks.get("manaFloor")
                fx = ("b[" + str(fl) + " * 5 + t]") if fl is not None else "0.0f"
                body.append("    float v" + e + " = b[" + e + " * 5 + t];\n    float f" + e + " = " + fx + ";\n    if (v" + e + " > 0.0f || f" + e +
                            " > 0.0f) out.add(\"+\" + numText(v" + e + ") + \"% max Mana\" + (f" + e + " > 0.0f ? \" (at least +\" + numText(f" + e +
                            ") + \")\" : \"\"));")
                continue
            assert kd in TXT, "0.5: no text for the stat kind %s - add it to _stat_code (and to TIPS)" % kd
            body.append("    float v" + e + " = b[" + e + " * 5 + t];\n    if (v" + e + " > 0.0f) out.add(" + TXT[kd].replace("(v)", "(v" + e + ")") + ");")
        lines.append("  if (li == " + str(li) + ") {\n" + "\n".join(body) + "\n  }")
    return ("public static String[] statParts(int li, int t) {\n  java.util.ArrayList out = new java.util.ArrayList();\n"
            "  float[] b = BOOST;\n  if (t < 1 || t > 4) return new String[0];\n" + "\n".join(lines) +
            "\n  return (String[]) out.toArray(new String[0]);\n}")
STAT_JAVA = _stat_code()
LINEON_JAVA = ("public static boolean lineOn(int li) {\n  switch (li) {\n" +
               "".join("    case %d: return LINE_%s;\n" % (i, b[1].upper()) for i, b in enumerate(BOOSTERS)) +
               "    default: return false;\n  }\n}")
# 0.5: 24.0 -> "24", 1.5 -> "1.5", 0.25 -> "0.25" (up to 2 decimals, values are >= 0)
JM(dfs, r"""
public static String numText(float v) {
  long c = Math.round((double) v * 100.0);
  if (c % 100L == 0L) return String.valueOf(c / 100L);
  if (c % 10L == 0L) return String.valueOf(c / 100L) + "." + String.valueOf((c % 100L) / 10L);
  String f = String.valueOf(c % 100L);
  if (f.length() < 2) f = "0" + f;
  return String.valueOf(c / 100L) + "." + f;
}""")
# 0.5: is a line switched on (config rows line.<Admin>; generated from the table)
JM(dfs, LINEON_JAVA)
# 0.5: line index of an admin name, a family key (the old names Vitality / Endurance / Intelligence as aliases) or a line name; -1 = none
JM(dfs, r"""
public static int lineOf(String name) {
  if (name == null) return -1;
  String n = name.trim();
  for (int i = 0; i < FAMILIES.length; i++) {
    if (LINE_ADMIN[i].equalsIgnoreCase(n) || FAMILIES[i].equalsIgnoreCase(n) || LINE_NAME[i].equalsIgnoreCase(n)) return i;
  }
  return -1;
}""")
# 0.5: rarity word or number -> tier 1..4 (Normal, Unique, Rare, Legendary or 1-4); -1 = not a line rarity
JM(dfs, r"""
public static int rarityIndex(String w) {
  if (w == null) return -1;
  String x = w.trim();
  for (int t = 1; t <= 4; t++) if (DISPLAY[t].equalsIgnoreCase(x) || String.valueOf(t).equals(x)) return t;
  return -1;
}""")
JM(dfs, r"""
public static String idOf(int li, int t) {
  if (li < 0 || li >= FAMILIES.length || t < 1 || t > 4) return null;
  return LINE_IDS[li * 4 + t - 1];
}""")
JM(dfs, r"""
public static boolean isBoosterId(String id) {
  if (id == null) return false;
  for (int i = 0; i < LINE_IDS.length; i++) if (LINE_IDS[i].equals(id)) return true;
  return false;
}""")
# 0.5: the short texts of one line's stats at one tier, with the live numbers (generated from the booster table)
JM(dfs, STAT_JAVA)
# 0.5: the Bonuses well - one key / value row per line with its best accessory in the bag (key = the line name, value = its stats at
# that rarity with the live numbers, or "switched off"), up to BONUS_MAX rows: [key0, value0, key1, value1, ...], "" = an empty row.
# (AccGear.pageRows adds the SkyyGear / SkyySkills notes in the free rows.)
JM(dfs, r"""
public static String[] bonusRows(String[] s) {
  String[] out = new String[BONUS_MAX * 2];
  for (int i = 0; i < out.length; i++) out[i] = "";
  int[] best = bestTiers(s);
  int n = 0;
  for (int li = 0; li < FAMILIES.length; li++) {
    if (best[li] <= 0 || n >= BONUS_MAX) continue;
    out[n * 2] = LINE_NAME[li];
    if (!lineOn(li)) { out[n * 2 + 1] = "switched off"; n++; continue; }
    String[] p = statParts(li, best[li]);
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < p.length; k++) { if (k > 0) sb.append(", "); sb.append(p[k]); }
    out[n * 2 + 1] = sb.length() > 0 ? sb.toString() : "nothing (its numbers are 0 on this server)";
    n++;
  }
  return out;
}""")
JM(dfs, r"""
public static String bonusText(String[] s) {
  String[] l = bonusRows(s);
  if (l[0].length() > 0) return "Bonuses - your best accessory of each line counts";
  return hasOmni(s) ? "Bonuses - no stat accessories yet - the Omni counts as every bench accessory" : "Bonuses - none yet - put accessories in this bag";
}""")
# 0.5 part 2: the tiers that COUNT right now (bestTiers with the switched-off lines at 0) - the effect tick, the gear:extra text, the notes
JM(dfs, r"""
public static int[] activeTiers(String[] s) {
  int[] best = bestTiers(s);
  for (int li = 0; li < best.length; li++) if (!lineOn(li)) best[li] = 0;
  return best;
}""")
# 0.5 part 2: does line li at tier t send anything to SkyyGear (a gear:extra entry above 0) / have a fall-damage part above 0?
JM(dfs, r"""
public static boolean sendsGear(int li, int t) {
  if (t < 1 || t > 4) return false;
  for (int e = 0; e < E_GEAR.length; e++) if (E_LINE[e] == li && E_GEAR[e].length() > 0 && BOOST[e * 5 + t] >= 1.0f) return true;
  return false;
}""")
JM(dfs, r"""
public static boolean hasFall(int li, int t) {
  return E_FALL >= 0 && E_LINE[E_FALL] == li && t >= 1 && t <= 4 && BOOST[E_FALL * 5 + t] > 0.0f;
}""")
dfs.addMethod(CtNewMethod.make("""
public static String roman(int t) {
  String[] r = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII" };
  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  if (isTalisman(id)) {   // 0.5: "<Rarity> <Line> Accessory" - never the family key or the old word (a legacy id shows its rarity's name)
    int r = rarityOf(id);
    int li = familyIndex(familyOf(id));
    String ln = li >= 0 ? LINE_NAME[li] + " Accessory" : "Accessory";
    return r >= 1 && r < DISPLAY.length ? DISPLAY[r] + " " + ln : ln;
  }
  if (OMNI.equals(id)) return "Omni Accessory";
  String b = benchOf(id);
  if (b == null) return id == null ? "?" : id;
  if (isRetired(id)) {   // 0.4.2 (BENCH_NAMES holds only the active benches); no parentheses in inline page text; numeral only for multi-tier benches
    for (int j = 0; j < RETIRED.length; j++) if (RETIRED[j].equalsIgnoreCase(b)) return RETIRED_NAMES[j] + (RETIRED_MAX[j] > 1 ? " " + roman(tierOf(id)) : "") + " - retired";
  }
  for (int i = 0; i < BENCH_IDS.length; i++) if (BENCH_IDS[i].equals(b)) return BENCH_MAX[i] > 1 ? BENCH_NAMES[i] + " " + roman(tierOf(id)) : BENCH_NAMES[i];
  return b.replace('_', ' ') + " " + roman(tierOf(id));
}""", dfs))

# 0.5: what the bag's "same or better ... already equipped" refusal names
JM(dfs, r"""
public static String lineLabel(String id) {
  if (isTalisman(id)) {
    int li = familyIndex(familyOf(id));
    return li >= 0 ? LINE_NAME[li] + " Accessory" : "accessory of that line";
  }
  return OMNI.equals(id) ? "Omni accessory" : "bench accessory";
}""")
# 0.5 bridge acc:defs (spec 5.9): every rarity of every line as name:key:tier:itemId:rarity:ap:sources, records joined by ","
JM(dfs, r"""
public static String defsText() {
  StringBuilder sb = new StringBuilder();
  for (int li = 0; li < FAMILIES.length; li++) {
    for (int t = 1; t <= 4; t++) {
      if (sb.length() > 0) sb.append(',');
      sb.append(LINE_ADMIN[li]).append(':').append(FAMILIES[li]).append(':').append(t).append(':').append(LINE_IDS[li * 4 + t - 1]);
      sb.append(':').append(DISPLAY[t]).append(':').append(AP[t]).append(':').append(LINE_SRC[li * 4 + t - 1]);
    }
  }
  return sb.toString();
}""")
# 0.5 /accessories lines: one chat line per line (its four rarities with the live numbers); ids = the admin's extra id line
JM(dfs, r"""
public static String[] linesText(boolean ids) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int li = 0; li < FAMILIES.length; li++) {
    StringBuilder sb = new StringBuilder();
    sb.append(LINE_NAME[li]).append(" Accessory (").append(LINE_ADMIN[li]).append(")");
    if (!lineOn(li)) sb.append(" - SWITCHED OFF on this server");
    sb.append(": ");
    for (int t = 1; t <= 4; t++) {
      if (t > 1) sb.append(" | ");
      sb.append(DISPLAY[t]).append(' ');
      String[] p = statParts(li, t);
      if (p.length == 0) sb.append("nothing");
      for (int k = 0; k < p.length; k++) { if (k > 0) sb.append(" and "); sb.append(p[k]); }
    }
    out.add(sb.toString());
    if (ids) {
      StringBuilder ib = new StringBuilder("    ids: ");
      for (int t = 1; t <= 4; t++) { if (t > 1) ib.append(" / "); ib.append(LINE_IDS[li * 4 + t - 1]); }
      out.add(ib.toString());
    }
  }
  return (String[]) out.toArray(new String[0]);
}""")
# 0.4: bench accessory ids for the acc:has bridge value = EXACTLY ONE entry per bench id, at the best tier (a bench id -> max tier
# reduction, the same one SkyySacks' accessories() parser does). Real bench accessories first (slot order; the stored id of the best
# tier is kept as-is), then - when the Omni is in the bag - every bench at BENCH_MAX: a bench not listed yet is appended as the
# synthetic "Skyy_Accessory_<BenchId>_T<maxTier>", a listed bench whose real tier is lower is replaced IN PLACE by that synthetic id
# (review fix: a plain string-containment dedupe published a real Workbench_T2 AND the synthetic Workbench_T3, so SkyyMenu's
# "N bench accessories" count read 14 instead of 13). The Omni id itself is not listed, so acc:has keeps its 0.1 meaning.
# keys = bench id of out[k] (same index), best[k] = its tier; at most s.length + BENCH_IDS.length entries.
# 0.4.2: a retired bench accessory is skipped (an equipped old copy unlocks nothing), and BENCH_IDS holds only the ACTIVE benches, so
# the Omni does not grant the retired ones either.
dfs.addMethod(CtNewMethod.make("""
public static java.util.ArrayList benchList(String[] s) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == null) return out;
  java.util.ArrayList keys = new java.util.ArrayList();
  int[] best = new int[s.length + BENCH_IDS.length];
  boolean omni = false;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (id == null || isTalisman(id) || !isAccessory(id)) continue;
    if (OMNI.equals(id)) { omni = true; continue; }
    String bn = benchOf(id);
    if (bn == null) continue;
    if (isRetired(id)) continue;   // 0.4.2
    int t = tierOf(id);
    int k = keys.indexOf(bn);
    if (k < 0) { keys.add(bn); out.add(id); best[out.size() - 1] = t; }
    else if (t > best[k]) { out.set(k, id); best[k] = t; }
  }
  if (omni) {
    for (int j = 0; j < BENCH_IDS.length; j++) {
      String syn = "Skyy_Accessory_" + BENCH_IDS[j] + "_T" + BENCH_MAX[j];
      int k2 = keys.indexOf(BENCH_IDS[j]);
      if (k2 < 0) { keys.add(BENCH_IDS[j]); out.add(syn); best[out.size() - 1] = BENCH_MAX[j]; }
      else if (BENCH_MAX[j] > best[k2]) { out.set(k2, syn); best[k2] = BENCH_MAX[j]; }
    }
  }
  return out;
}""", dfs))

# ================= AccStore =================
st_.addField(CtField.make("public static java.nio.file.Path DIR;", st_))
st_.addField(CtField.make(f"public static {LOG} LOG;", st_))
st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
st_.addField(CtField.make("public static final int MAIN = %d;" % MAIN_SLOTS, st_))   # 0.5: slot0..MAIN-1 in <key>.properties, the rest in <key>.more.properties
# 0.4.4: CAP stays the STORAGE size (0.5: 60 - the page, the un:<i> buttons); SLOTS = this server's limit for NEW equips (config row
# slots, kit field:, default 18). Accessories already in a slot >= SLOTS stay, keep counting and can be unequipped.
st_.addField(CtField.make("public static volatile int SLOTS = %d;" % SLOTS_DEF, st_))
# 0.5: bag files that could not be READ at load (path text -> reason): never overwritten afterwards, so a read error cannot wipe a bag
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADFILE = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static boolean RESTAMP_WARNED = false;", st_))
# 0.4.1: BAGS is keyed by the profile storage key (pkey String, PROFILES-CONTRACT rule 2), not the UUID
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAGS = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", st_))
# 0.2 effect state (world thread writes, 5 s tick prunes offline players): CLOCK uuid -> float[]{secondsSinceSync, regenSeconds},
# SPEED uuid -> 0.3: MoveSync applier state float[]{lastWrittenSpeed, lastWrittenJump, strikes, targetSpeed, targetJump, warned} (0.2: own speed state)
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SPEED = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", st_))
# 0.4.1 PROFILES-CONTRACT storage key helper (verbatim from tools/PROFILES-CONTRACT.md): active profile's key, uuid = profile 1
st_.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", st_))
# 0.4.1 rule 3: EPOCH uuid -> profile:epoch:<uuid> seen at the last publish, PUBKEY uuid -> pkey the last publish used (pruned like PUBLISHED)
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBKEY = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static Object epochOf(java.util.UUID u) {
  try { return bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { return null; }
}""", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static Object lock(java.util.UUID u) {
  Object o = LOCKS.get(u);
  if (o != null) return o;
  Object n = new Object();
  o = LOCKS.putIfAbsent(u, n);
  return o == null ? n : o;
}""", st_))
# 0.5: slots from..to-1 of one bag file (a missing file = empty slots); a file that cannot be read is remembered in BADFILE
JM(st_, r"""
public static void readInto(String[] s, java.nio.file.Path f, int from, int to) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    for (int i = from; i < to && i < s.length; i++) {
      String v = p.getProperty("slot" + i);
      if (v != null && v.trim().length() > 0) s[i] = v.trim();
    }
  } catch (Throwable t) {
    BADFILE.put(f.toString(), String.valueOf(t));
    warn("could not load bag file " + f + " - it is left as it is and not overwritten until the server restarts: " + t);
  }
}""")
# 0.4.1: the bag of storage key k; 0.5: slot0..8 from bags/<k>.properties (0.4.x's file, same format), slot9..59 from bags/<k>.more.properties
JM(st_, r"""
public static String[] slotsK(java.util.UUID u, String k) {
  String[] s = (String[]) BAGS.get(k);
  if (s != null) return s;
  synchronized (lock(u)) {
    s = (String[]) BAGS.get(k);
    if (s != null) return s;
    s = new String[CAP];
    readInto(s, DIR.resolve(k + ".properties"), 0, MAIN);
    readInto(s, DIR.resolve(k + ".more.properties"), MAIN, CAP);
    BAGS.put(k, s);
    return s;
  }
}""")
# 0.5: true when a file of bag k could not be read at load: the page then moves nothing into or out of that bag (a move could not be
# saved, and an item put in would be lost at the next restart)
JM(st_, r"""
public static boolean isBad(String k) {
  if (DIR == null || k == null) return false;
  return BADFILE.containsKey(DIR.resolve(k + ".properties").toString()) || BADFILE.containsKey(DIR.resolve(k + ".more.properties").toString());
}""")
# 0.5: writes slots from..to-1 into one bag file (tmp + move). The main file is always written (0.4.5's format and comment); the second
# file only when it holds something or already exists (then it may become empty - it is never deleted). A BADFILE is never written.
JM(st_, r"""
public static void writeSlots(String[] s, String name, int from, int to, boolean always) throws java.io.IOException {
  java.nio.file.Path f = DIR.resolve(name);
  if (BADFILE.containsKey(f.toString())) { warn("bag file " + f + " could not be read at load, so it is not overwritten (restart after fixing or removing it)"); return; }
  java.util.Properties p = new java.util.Properties();
  boolean any = false;
  for (int i = from; i < to && i < s.length; i++) if (s[i] != null) { p.setProperty("slot" + i, s[i]); any = true; }
  if (!any && !always && !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  java.nio.file.Path tmp = DIR.resolve(name + ".tmp");
  java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
  try { p.store(out, from == 0 ? "SkyyAccessories bag" : "SkyyAccessories bag - slots 10 to 60 (0.5 and later)"); } finally { out.close(); }
  java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
}""")
# 0.4.1: the bag of the player's ACTIVE profile
st_.addMethod(CtNewMethod.make("""
public static String[] slots(java.util.UUID u) {
  return slotsK(u, pkey(u));
}""", st_))
# copy of the bag for readers (talisman tick, page build) - never the live array
st_.addMethod(CtNewMethod.make("""
public static String[] snapshot(java.util.UUID u) {
  String[] s = slots(u);
  String[] c = new String[s.length];
  synchronized (lock(u)) { System.arraycopy(s, 0, c, 0, s.length); }
  return c;
}""", st_))
# acc:has keeps its 0.1 meaning (bench accessories only - SkyySacks 0.6.1 parses every id there as Skyy_Accessory_<Bench>_T<n>, so a
# talisman id made a bogus "itality Talisman I" craft tab); talismans go to acc:tal:<uuid>; acc:fn:has still answers for both.
# 0.4: acc:has = AccDefs.benchList (one entry per bench at its best tier, the Omni counting as every bench at max tier); acc:tal lists modern ids (legacy
# Talisman/Ring/Artifact published as their Uncommon/Rare/Epic id)
st_.addMethod(CtNewMethod.make(f"""
public static void publish(java.util.UUID u) {{
  Object ep = epochOf(u);   // 0.4.1: read BEFORE the key, so a later switch always looks newer
  synchronized (lock(u)) {{
    String k = pkey(u);
    String[] s = slotsK(u, k);
    StringBuilder acc = new StringBuilder();
    StringBuilder tal = new StringBuilder();
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || !{PKG}.AccDefs.isTalisman(s[i])) continue;
      if (tal.length() > 0) tal.append(',');
      tal.append({PKG}.AccDefs.modernOf(s[i]));
    }}
    java.util.ArrayList bl = {PKG}.AccDefs.benchList(s);
    for (int i = 0; i < bl.size(); i++) {{
      if (acc.length() > 0) acc.append(',');
      acc.append((String) bl.get(i));
    }}
    bridge().put("acc:has:" + u.toString(), acc.toString());
    bridge().put("acc:tal:" + u.toString(), tal.toString());
    PUBLISHED.put(u, Boolean.TRUE);
    if (ep == null) EPOCH.remove(u); else EPOCH.put(u, ep);
    PUBKEY.put(u, k);
  }}
}}""", st_))
# 0.4.1: saves the bag of storage key k (the key the caller resolved once), then republishes the active profile; 0.5: two files
st_.addMethod(CtNewMethod.make("""
public static void saveK(java.util.UUID u, String k) {
  synchronized (lock(u)) {
    try {
      String[] s = slotsK(u, k);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      writeSlots(s, k + ".properties", 0, MAIN, true);
      writeSlots(s, k + ".more.properties", MAIN, CAP, false);
    } catch (Throwable t) { warn("could not save bag " + k + " for " + u + ": " + t); }
    publish(u);
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  saveK(u, pkey(u));
}""", st_))
st_.addMethod(CtNewMethod.make(f"""
public static boolean has(java.util.UUID u, String id) {{
  if (u == null || id == null) return false;
  if ({PKG}.AccDefs.isRetired(id)) return false;   // 0.4.2: acc:fn:has never answers true for a retired accessory
  synchronized (lock(u)) {{
    String[] s = slots(u);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (id.equals(s[i]) || id.equals({PKG}.AccDefs.modernOf(s[i]))) return true;
    }}
    if (id.startsWith("Skyy_Accessory_") && {PKG}.AccDefs.benchList(s).contains(id)) return true;   // 0.4: Omni = every bench at max tier
    return false;
  }}
}}""", st_))
# 0.4.4: the number of slots a NEW accessory may go into (SLOTS clamped to 1..the bag's length); = s.length with the default 9
st_.addMethod(CtNewMethod.make("""
public static int capOf(String[] s) {
  int c = SLOTS;
  if (c < 1) c = 1;
  if (s != null && c > s.length) c = s.length;
  return c;
}""", st_))
# would equip(u, id) take the item? same rule as equip - asked BEFORE the item leaves the inventory
st_.addMethod(CtNewMethod.make(f"""
public static boolean canEquipK(java.util.UUID u, String k, String id) {{
  if ({PKG}.AccDefs.isRetired(id)) return false;   // 0.4.2: never equipped (the page refuses first, with the reason)
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);
    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    boolean same = false;
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || g == null || !g.equals({PKG}.AccDefs.groupOf(s[i]))) continue;
      if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return false;   // 0.5: an equal or better one anywhere in the line = refused
      same = true;
    }}
    if (same) return true;   // 0.5: every slot of the line is lower - the lowest is swapped out
    int cap = capOf(s);   // 0.4.4: a free slot below this server's limit (an in-place upgrade above is still fine)
    for (int i = 0; i < cap; i++) if (s[i] == null) return true;
    return false;
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean canEquip(java.util.UUID u, String id) {
  return canEquipK(u, pkey(u), id);
}""", st_))
# equips id; returns the item id that was displaced (same group, lower tier) or "" when a free slot was used, or null when the bag is full / an equal or better one is in
st_.addMethod(CtNewMethod.make(f"""
public static String equipK(java.util.UUID u, String k, String id) {{
  if ({PKG}.AccDefs.isRetired(id)) return null;   // 0.4.2
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);
    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    int low = -1;
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || g == null || !g.equals({PKG}.AccDefs.groupOf(s[i]))) continue;
      if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return null;   // 0.5: an equal or better one anywhere in the line = refused
      if (low < 0 || {PKG}.AccDefs.tierOf(s[i]) < {PKG}.AccDefs.tierOf(s[low])) low = i;
    }}
    if (low >= 0) {{ String old = s[low]; s[low] = id; saveK(u, k); return old; }}   // 0.5: the lowest slot of the line
    int cap = capOf(s);   // 0.4.4: new accessories only go below this server's limit (canEquipK asks the same)
    for (int i = 0; i < cap; i++) if (s[i] == null) {{ s[i] = id; saveK(u, k); return ""; }}
    return null;
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String equip(java.util.UUID u, String id) {
  return equipK(u, pkey(u), id);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String unequipK(java.util.UUID u, String k, int idx) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    if (idx < 0 || idx >= s.length || s[idx] == null) return null;
    String id = s[idx]; s[idx] = null; saveK(u, k); return id;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String unequip(java.util.UUID u, int idx) {
  return unequipK(u, pkey(u), idx);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void putK(java.util.UUID u, String k, int idx, String id) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    if (idx < 0 || idx >= s.length) return;
    s[idx] = id; saveK(u, k);
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void put(java.util.UUID u, int idx, String id) {
  putK(u, pkey(u), idx, id);
}""", st_))
# last resort so an item can never vanish: first free slot, ignoring the one-per-group rule (bestTiers and SkyySacks use the best tier)
st_.addMethod(CtNewMethod.make("""
public static boolean stashK(java.util.UUID u, String k, String id) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    for (int i = 0; i < s.length; i++) if (s[i] == null) { s[i] = id; saveK(u, k); return true; }
    return false;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean stash(java.util.UUID u, String id) {
  return stashK(u, pkey(u), id);
}""", st_))
# Integration pass (semantics rule 5): null = item moves between the live inventory and this player's bag are safe right now, else the
# reason shown on the page. profile:busy:<uuid> = the live inventory may not belong to the active profile (pending crash recovery at
# join; a switch runs inside one world-thread task, so the page handler never sees that one). SkyyProfiles installed but no
# profile:epoch:<uuid> for an online player = its players file is unreadable and pkey fell back to profile 1's key (or the join work
# has not run yet): moving items now could carry them from one profile to another. Without SkyyProfiles both keys are absent -> null.
st_.addMethod(CtNewMethod.make("""
public static String moveBlock(java.util.UUID u) {
  try {
    java.util.Map b = bridge();
    String us = u.toString();
    if (b.get("profile:busy:" + us) != null) return "your profile is still loading - try again in a moment";
    if (b.get("profile:fn:key") != null && b.get("profile:epoch:" + us) == null) return "your profile is not loaded - try again in a moment - tell an admin if this stays";
  } catch (Throwable t) { }
  return null;
}""", st_))
# 0.4.1 PROFILES-CONTRACT rule 3: republish acc:has / acc:tal when profile:epoch:<uuid> changed since the last publish, or the active
# key is not the one published (either write order inside SkyyProfiles). Only after the first publish (0.4 timing kept). Without
# SkyyProfiles the epoch is absent on both sides -> false after one lookup. Called by publishOnline (5 s) and AccEffects (1 s).
st_.addMethod(CtNewMethod.make("""
public static boolean checkEpoch(java.util.UUID u) {
  if (u == null || !PUBLISHED.containsKey(u)) return false;
  Object ep = epochOf(u);
  Object last = EPOCH.get(u);
  boolean changed = (ep == null) ? (last != null) : !ep.equals(last);
  if (!changed) {
    if (ep == null) return false;
    Object pk = PUBKEY.get(u);
    if (pk == null || pk.equals(pkey(u))) return false;
  }
  publish(u);
  return true;
}""", st_))
st_.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (!PUBLISHED.containsKey(u)) publish(u);
      else checkEpoch(u);   // 0.4.1: profile switch -> republish
    }}
    PUBLISHED.keySet().retainAll(online);
    EPOCH.keySet().retainAll(online);
    PUBKEY.keySet().retainAll(online);
    CLOCK.keySet().retainAll(online);
    SPEED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", st_))

# 0.5: the accessories (Skyy_Talisman_* / Skyy_Accessory_*, the bag item too) in storage + hotbar + backpack, by count
JM(st_, r"""
public static int accCount(@IC@[] conts) {
  int n = 0;
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id != null && (id.startsWith("Skyy_Talisman_") || id.startsWith("Skyy_Accessory_"))) n = n + it.getQuantity();
    }
  }
  return n;
}""")
# 0.5 RESTAMP (spec 5.2, the SkyySacks 0.7.7 pattern): a saved stack keeps the quality index it was saved with, so every accessory stack
# (and the bag item) whose index differs from its item's gets withQuality(item index) - id and count unchanged (asserted per stack, and
# the accessory count before and after is compared). World thread only (AccRestampTask); returns the stacks changed.
JM(st_, r"""
public static int restamp(@INV@ inv) {
  if (inv == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  int before = accCount(conts);
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id == null || !(id.startsWith("Skyy_Talisman_") || id.startsWith("Skyy_Accessory_"))) continue;
      @ITM@ item = it.getItem();
      if (item == null) continue;
      int want = item.getQualityIndex();
      if (it.getQualityIndex() == want) continue;
      @IS@ nw = it.withQuality(want);
      if (nw == null || !id.equals(nw.getItemId()) || nw.getQuantity() != it.getQuantity()) {
        if (!RESTAMP_WARNED) { RESTAMP_WARNED = true; warn("restamp skipped " + id + ": withQuality changed the id or the count (logged once)"); }
        continue;
      }
      cont.setItemStackForSlot(s, nw);
      n++;
    }
  }
  int after = accCount(conts);
  if (after != before && !RESTAMP_WARNED) { RESTAMP_WARNED = true; warn("restamp: the accessory count changed from " + before + " to " + after + " (logged once)"); }
  return n;
}""")
# 0.5: how many of item id are in storage + hotbar + backpack (the give counts before and after)
JM(st_, r"""
public static int countOf(@INV@ inv, String id) {
  if (inv == null || id == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n = n + it.getQuantity();
    }
  }
  return n;
}""")
# 0.5 (part 1 review finding 1): the give arithmetic - got = the count after minus before (never below 0), handed out = got + dropped;
# c[3] = 1 when that is not the n asked for (a stack merged elsewhere, a full inventory that could not drop, ...)
JM(st_, r"""
public static int[] giveCount(int before, int after, int dropped, int n) {
  int got = after - before;
  if (got < 0) got = 0;
  int d = dropped < 0 ? 0 : dropped;
  int ok = got + d;
  return new int[] { ok, got, d, ok != n ? 1 : 0 };
}""")
# 0.5 give (spec 5.9): n copies of id, one at a time (MaxStack 1), storage first and the rest dropped at the player's feet
# (addOrDropItemStack, vanilla's giveOutput call), counted before and after. ONLY on that player's world thread (Store.isInThread);
# returns { handed out, now in the inventory, dropped } or null when the player / store / thread is not right.
JM(st_, r"""
public static int[] deliver(@PR@ pr, String id, int n) {
  if (pr == null || id == null || n < 1) return null;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  @ST@ st = r.getStore();
  if (st == null || !st.isInThread()) return null;
  @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  if (p == null || p.getInventory() == null) return null;
  @INV@ inv = p.getInventory();
  int before = countOf(inv, id);
  int dropped = 0;
  for (int i = 0; i < n; i++) {
    if (@SIC@.addOrDropItemStack(st, r, inv.getCombinedStorageHotbarBackpack(), new @IS@(id, 1))) dropped++;   // true = dropped
  }
  int[] c = giveCount(before, countOf(inv, id), dropped, n);
  if (c[3] != 0) warn("give of " + n + " x " + id + " to " + pr.getUsername() + ": " + c[1] + " arrived in the inventory and " + c[2] + " were dropped at their feet (" + c[0] + " handed out)");
  return new int[] { c[0], c[1], c[2] };
}""")
# 0.4.3 review fix: SkyyCooking's LIVE Campfire accessory factors. The item text can only carry the defaults (CAMP_*_PCT), but a server
# can change campfire.xpFactor / campfire.buffFactor in cooking.properties (+ /cookadmin reload). SkyyCooking 0.1.1 publishes them as
# cook:fn:campfactors = Function, apply(anything) -> Object[]{ Double buffFactor, Double xpFactor, Boolean enabled } (live, any thread,
# no I/O). campFactors() -> {xpFactor, buffFactor, enabled 1/0} or null (SkyyCooking absent, or the key missing / changed shape).
st_.addField(CtField.make('public static volatile String CF_SEEN = "";', st_))   # campCheck: last state logged (tick thread only)
st_.addField(CtField.make("public static final double CAMP_XP_TEXT = %s;" % repr(CAMP_XP_PCT / 100.0), st_))
st_.addField(CtField.make("public static final double CAMP_BUFF_TEXT = %s;" % repr(CAMP_BUFF_PCT / 100.0), st_))
st_.addField(CtField.make('public static final String CAMPFIRE_ID = "Skyy_Accessory_Campfire_T1";', st_))
st_.addMethod(CtNewMethod.make("""
public static double[] campFactors() {
  try {
    Object f = bridge().get("cook:fn:campfactors");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply((Object) null);
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    if (a.length < 3 || !(a[0] instanceof Number) || !(a[1] instanceof Number) || !(a[2] instanceof Boolean)) return null;
    double bv = ((Number) a[0]).doubleValue();
    double xv = ((Number) a[1]).doubleValue();
    if (!(xv >= 0.0 && xv <= 1.0 && bv >= 0.0 && bv <= 1.0)) return null;
    return new double[] { xv, bv, ((Boolean) a[2]).booleanValue() ? 1.0 : 0.0 };
  } catch (Throwable t) { return null; }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String campPct(double v) {
  long c = Math.round(v * 1000.0);
  if (c % 10L == 0L) return String.valueOf(c / 10L) + "%";
  return String.valueOf(c / 10L) + "." + String.valueOf(c % 10L) + "%";
}""", st_))
# 5 s tick (AccTick, scheduler thread): one WARNING per distinct state - live factors that differ from the item text, graded cooking
# turned off, or SkyyCooking running (cook:fn:campfire) without a readable cook:fn:campfactors. Silent while the live factors match
# the text or SkyyCooking (0.1.1+) is absent. Checking every 5 s also catches /cookadmin reload.
st_.addMethod(CtNewMethod.make("""
public static void campCheck() {
  try {
    if (bridge().get("cook:fn:campfire") == null) return;
    double[] f = campFactors();
    String seen = "unreadable";
    if (f != null && f[2] < 0.5) seen = "off";
    else if (f != null) seen = (Math.abs(f[0] - CAMP_XP_TEXT) < 0.0005 && Math.abs(f[1] - CAMP_BUFF_TEXT) < 0.0005) ? "default" : campPct(f[0]) + " " + campPct(f[1]);
    if (seen.equals(CF_SEEN)) return;
    CF_SEEN = seen;
    if (seen.equals("default")) return;
    if (f == null) warn("SkyyCooking runs (cook:fn:campfire), but its live Campfire accessory factors could not be read (cook:fn:campfactors missing or changed shape - expected Object[]{Double buffFactor, Double xpFactor, Boolean enabled}). The Campfire Accessory item text shows the defaults " + campPct(CAMP_XP_TEXT) + " Cooking XP / " + campPct(CAMP_BUFF_TEXT) + " of the cooking bonus and the Accessory Bag page cannot show this server's numbers.");
    else if (seen.equals("off")) warn("graded cooking is off in cooking.properties (enabled=false): the Campfire accessory cooks plain dishes with no Cooking XP, but its item text says " + campPct(CAMP_XP_TEXT) + " Cooking XP / " + campPct(CAMP_BUFF_TEXT) + " of the cooking bonus. The Accessory Bag page says it is off.");
    else warn("cooking.properties sets the Campfire accessory to " + campPct(f[0]) + " Cooking XP and " + campPct(f[1]) + " of the cooking bonus (campfire.xpFactor / campfire.buffFactor), but the Campfire Accessory item text says the defaults " + campPct(CAMP_XP_TEXT) + " / " + campPct(CAMP_BUFF_TEXT) + ". The Accessory Bag page shows the live numbers; the item text only changes with a SkyyAccessories rebuild (CAMP_XP_PCT / CAMP_BUFF_PCT).");
  } catch (Throwable t) { }
}""", st_))
# Accessory Bag page status line while the Campfire accessory or the Omni is equipped ("" otherwise, or when the factors cannot be read)
st_.addMethod(CtNewMethod.make("""
public static String campLine(String[] s) {
  try {
    boolean on = false;
    if (s != null) for (int i = 0; i < s.length; i++) if (CAMPFIRE_ID.equals(s[i]) || com.skyy.accessories.AccDefs.OMNI.equals(s[i])) on = true;
    if (!on) return "";
    if (bridge().get("cook:fn:campfire") == null) return "Campfire quick cook - SkyyCooking is not running - plain dishes and no Cooking XP";
    double[] f = campFactors();
    if (f == null) return "";
    if (f[2] < 0.5) return "Campfire quick cook - graded cooking is off on this server - plain dishes and no Cooking XP";
    return "Campfire quick cook on this server - " + campPct(f[0]) + " Cooking XP and " + campPct(f[1]) + " of your cooking bonus";
  } catch (Throwable t) { return ""; }
}""", st_))

# ================= AccCfg (0.4.4; 0.5: booster entries, line switches, notice switch, the one-time 0.5 migration) =================
cfg_.addField(CtField.make("public static java.nio.file.Path FILE;", cfg_))
cfg_.addField(CtField.make("public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT), cfg_))
cfg_.addField(CtField.make("public static final String[] BOOST_DEF = new String[] { %s };" % jstrs(BOOST_DEF), cfg_))   # index = AccDefs.E_KEYS
cfg_.addField(CtField.make('public static volatile String TIP_SEEN = "";', cfg_))   # the last "differs from the tooltips" text logged
# 0.5 migration data (spec 5.1)
cfg_.addField(CtField.make("public static final String[] OLD_FAM = new String[] { %s };" % jstrs(o[0] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_DEF = new String[] { %s };" % jstrs(o[1] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_CARRY = new String[] { %s };" % jstrs(o[2] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_WHY = new String[] { %s };" % jstrs(o[3] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] ADD_KEY = new String[] { %s };" % jstrs(ADD_KEY), cfg_))
cfg_.addField(CtField.make("public static final String[] ADD_VAL = new String[] { %s };" % jstrs(ADD_VAL), cfg_))
cfg_.addField(CtField.make("public static final int[] ADD_GROUP = new int[] { %s };" % ", ".join(str(g) for g in ADD_GROUP), cfg_))
cfg_.addField(CtField.make("public static final String[] GROUP_NOTE = new String[] { %s };" % jstrs(GROUP_NOTE), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_COMMENT = new String[] { %s };" % jstrs(o for o, n in OLD_COMMENTS), cfg_))
cfg_.addField(CtField.make("public static final String[] NEW_COMMENT = new String[] { %s };" % jstrs(n for o, n in OLD_COMMENTS), cfg_))
for _src in [
r"""
public static void info(String msg) {
  try { if (@PKG@.AccStore.LOG != null) @PKG@.AccStore.LOG.at(java.util.logging.Level.INFO).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""",
r"""
public static void writeDefaults() {
  try {
    if (FILE == null || java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(FILE, DEFAULT_TEXT.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
    info("wrote the first config.properties with the built-in settings: " + FILE);
  } catch (Throwable t) { @PKG@.AccStore.warn("could not write the default config.properties: " + t); }
}""",
r"""
public static double num(String t) {
  if (t == null) return -1.0;
  String x = t.trim();
  if (x.length() == 0 || x.length() > 12) return -1.0;
  int dot = -1;
  for (int i = 0; i < x.length(); i++) {
    char c = x.charAt(i);
    if (c == '.') {
      if (dot >= 0 || i == 0 || i == x.length() - 1) return -1.0;
      dot = i;
    } else if (c < '0' || c > '9') return -1.0;
  }
  if (dot >= 0 && x.length() - dot - 1 > 2) return -1.0;
  try { return Double.parseDouble(x); } catch (Throwable e) { return -1.0; }
}""",
# "6,12,18,24" -> n numbers (n = 4 for a booster entry, 5 for a 0.4.x bonus list), or null when it is not exactly n numbers >= 0
r"""
public static double[] parseN(String v, int n) {
  if (v == null) return null;
  String[] p = v.split(",", -1);
  if (p.length != n) return null;
  double[] out = new double[n];
  for (int i = 0; i < n; i++) {
    double x = num(p[i]);
    if (x < 0.0) return null;
    out[i] = x;
  }
  return out;
}""",
r"""
public static boolean sameRow(double[] a, double[] b) {
  if (a == null || b == null || a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) if (Math.abs(a[i] - b[i]) > 0.0000001) return false;
  return true;
}""",
r"""
public static String dtext(double v) {
  long c = Math.round(v * 100.0);
  if (c % 100L == 0L) return String.valueOf(c / 100L);
  if (c % 10L == 0L) return String.valueOf(c / 100L) + "." + String.valueOf((c % 100L) / 10L);
  String f = String.valueOf(c % 100L);
  if (f.length() < 2) f = "0" + f;
  return String.valueOf(c / 100L) + "." + f;
}""",
r"""
public static String rowText(double[] r) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < r.length; i++) { if (i > 0) sb.append(','); sb.append(dtext(r[i])); }
  return sb.toString();
}""",
r"""
public static int intIn(String v, int def, int lo, int hi, String key) {
  if (v == null) return def;
  int n = def;
  try { n = Integer.parseInt(v.trim()); }
  catch (Throwable t) { @PKG@.AccStore.warn("config.properties: " + key + "=" + v.trim() + " is not a whole number - " + def + " is used"); return def; }
  if (n < lo) { @PKG@.AccStore.warn("config.properties: " + key + "=" + n + " is below " + lo + " - " + lo + " is used"); return lo; }
  if (n > hi) { @PKG@.AccStore.warn("config.properties: " + key + "=" + n + " is above " + hi + " - " + hi + " is used"); return hi; }
  return n;
}""",
r"""
public static boolean boolIn(String v, boolean def, String key) {
  if (v == null) return def;
  String x = v.trim().toLowerCase();
  if (x.equals("true") || x.equals("on") || x.equals("yes") || x.equals("1")) return true;
  if (x.equals("false") || x.equals("off") || x.equals("no") || x.equals("0")) return false;
  @PKG@.AccStore.warn("config.properties: " + key + "=" + v.trim() + " is not true or false - " + (def ? "true" : "false") + " is used");
  return def;
}""",
r"""
public static int entryIndex(String en) {
  if (en == null) return -1;
  for (int i = 0; i < @PKG@.AccDefs.E_KEYS.length; i++) if (@PKG@.AccDefs.E_KEYS[i].equals(en)) return i;
  return -1;
}""",
# one booster entry from the file: 4 numbers, capped at the entry's cap, whole numbers where the entry needs them (the loader clamps like
# the kit validates; a line that is not 4 numbers falls back to the built-in numbers)
r"""
public static double[] boostIn(String v, int e) {
  double[] d = parseN(BOOST_DEF[e], 4);
  if (v == null) return d;
  String k = "boost." + @PKG@.AccDefs.E_KEYS[e];
  double[] r = parseN(v, 4);
  if (r == null) {
    @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " is not 4 numbers like " + BOOST_DEF[e] + " (Normal,Unique,Rare,Legendary; 0 or more, at most 2 decimals, no minus sign) - the built-in numbers are used");
    return d;
  }
  double cap = (double) @PKG@.AccDefs.E_CAP[e];
  boolean cl = false;
  boolean wh = false;
  for (int t = 0; t < 4; t++) {
    if (r[t] > cap) { r[t] = cap; cl = true; }
    if (@PKG@.AccDefs.E_WHOLE[e] == 1 && r[t] != Math.floor(r[t])) { r[t] = Math.floor(r[t]); wh = true; }
  }
  if (cl) @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " has a number above " + dtext(cap) + " - " + dtext(cap) + " is used there");
  if (wh) @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " takes whole numbers only - the decimals are dropped");
  return r;
}""",
r"""
public static String oneLine(String t) {
  if (t == null) return "";
  return t.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ');
}""",
# the key of one physical .properties line (null for a comment or a blank line)
r"""
public static String keyOf(String ln) {
  if (ln == null) return null;
  int i = 0;
  while (i < ln.length() && (ln.charAt(i) == ' ' || ln.charAt(i) == '\t' || ln.charAt(i) == '\f')) i++;
  if (i >= ln.length()) return null;
  char c0 = ln.charAt(i);
  if (c0 == '#' || c0 == '!') return null;
  int j = i;
  while (j < ln.length()) {
    char c = ln.charAt(j);
    if (c == '=' || c == ':' || c == ' ' || c == '\t' || c == '\f') break;
    j++;
  }
  return ln.substring(i, j);
}""",
# a value line that continues on the next physical line (an odd number of backslashes at the end)
r"""
public static boolean contLine(String ln) {
  int n = 0;
  for (int i = ln.length() - 1; i >= 0 && ln.charAt(i) == '\\'; i--) n++;
  return n % 2 == 1;
}""",
# the migration's change-log lines, in the kit's config-changes.log format (who migration-0.5, uuid -, via migrate) + one INFO line each
r"""
public static void logMig(java.util.ArrayList logs) {
  StringBuilder sb = new StringBuilder();
  String now = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss").format(java.time.LocalDateTime.now());
  for (int i = 0; i < logs.size(); i++) {
    String[] e = (String[]) logs.get(i);
    sb.append(now).append('\t').append("migration-0.5").append('\t').append('-').append('\t').append("migrate").append('\t');
    sb.append(oneLine(e[0])).append('\t').append(oneLine(e[1])).append('\t').append(oneLine(e[2])).append('\t').append(oneLine(e[3])).append('\n');
    info("config " + oneLine(e[0]) + " " + oneLine(e[1]) + " -> " + oneLine(e[2]) + " by migration-0.5 (migrate)" + ("ok".equals(e[3]) ? "" : " [" + e[3] + "]"));
  }
  try {
    java.nio.file.Path lf = FILE.resolveSibling("config-changes.log");
    java.nio.file.Files.write(lf, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { @PKG@.AccStore.warn("could not write config-changes.log for the 0.5 update: " + t); }
}""",
# THE ONE-TIME 0.5 MIGRATION (spec 5.1). setup() -> load(true) -> here, BEFORE CfgPub.start. Runs only when the file has a bonus. line
# and no boost. line (a file with neither just gets the missing 0.5 keys); afterwards there is no bonus. line, so it never runs again.
# One atomic write; the old file is copied once to config.properties.pre-0.5.bak; every changed / carried / dropped / added value is
# logged. Returns "" when nothing was done, else the summary for the ready log line.
r"""
public static String migrate() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return "";
    byte[] raw = java.nio.file.Files.readAllBytes(FILE);
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.ByteArrayInputStream(raw));
    boolean hasBonus = false;
    boolean hasBoost = false;
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String pk = (String) it.next();
      if (pk.startsWith("bonus.")) hasBonus = true;
      if (pk.startsWith("boost.")) hasBoost = true;
    }
    // 0.5 part 2: mig = the 0.4.x -> 0.5 update (bonus. lines and no boost. line). A file that already has boost. lines (a server
    // that ran part 1) only gets the 0.5 keys it misses appended: no slots change, no removal, no .bak (nothing is lost).
    boolean mig = hasBonus && !hasBoost;
    String text = new String(raw, "ISO-8859-1");
    String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    String body = text;
    if (body.endsWith("\r\n")) body = body.substring(0, body.length() - 2);
    else if (body.endsWith("\n")) body = body.substring(0, body.length() - 1);
    String[] lines = body.length() == 0 ? new String[0] : body.split("\r?\n", -1);
    java.util.ArrayList logs = new java.util.ArrayList();
    java.util.HashMap carried = new java.util.HashMap();
    for (int f = 0; mig && f < OLD_FAM.length; f++) {
      String key = "bonus." + OLD_FAM[f];
      String ov = p.getProperty(key);
      if (ov == null) continue;
      String o = ov.trim();
      double[] r = parseN(o, 5);
      if (r != null && sameRow(r, parseN(OLD_DEF[f], 5))) { logs.add(new String[] { key, o, "(removed - the 0.5 default applies)", "done" }); continue; }
      if (OLD_CARRY[f].length() == 0) { logs.add(new String[] { key, o, "(dropped - " + OLD_WHY[f] + ")", "invalid" }); continue; }
      if (r == null) { logs.add(new String[] { key, o, "(dropped - not 5 numbers, so the 0.5 default applies)", "invalid" }); continue; }
      int e = entryIndex(OLD_CARRY[f]);
      double[] c = new double[] { r[0], r[1], r[2], r[4] };
      String note = "";
      for (int t = 0; t < 4; t++) {
        if (e >= 0 && c[t] > (double) @PKG@.AccDefs.E_CAP[e]) { c[t] = (double) @PKG@.AccDefs.E_CAP[e]; note = ", capped at " + dtext(c[t]); }
      }
      String cv = rowText(c);
      carried.put(OLD_CARRY[f], cv);
      logs.add(new String[] { key, o, "boost." + OLD_CARRY[f] + "=" + cv + " (the 1st, 2nd, 3rd and 5th number - the 4th, " + dtext(r[3]) + ", is dropped" + note + ")", "done" });
    }
    String sv = p.getProperty("slots");
    boolean bump = mig && sv != null && sv.trim().equals("9");
    boolean bumped = false;
    StringBuilder out = new StringBuilder();
    boolean contDrop = false;
    boolean contKeep = false;
    for (int i = 0; i < lines.length; i++) {
      String ln = lines[i];
      if (contDrop) { contDrop = contLine(ln); continue; }
      if (contKeep) { contKeep = contLine(ln); out.append(ln).append(nl); continue; }
      String k = keyOf(ln);
      if (mig && k != null && k.startsWith("bonus.")) { contDrop = contLine(ln); continue; }
      if (bump && "slots".equals(k) && !contLine(ln)) { out.append("slots=@SLOTS@").append(nl); bumped = true; continue; }
      if (mig && k == null) {
        int oc = -1;
        for (int j = 0; j < OLD_COMMENT.length; j++) if (OLD_COMMENT[j].equals(ln)) oc = j;
        if (oc >= 0) { if (NEW_COMMENT[oc].length() > 0) out.append(NEW_COMMENT[oc]).append(nl); continue; }
      }
      if (k != null) contKeep = contLine(ln);
      out.append(ln).append(nl);
    }
    if (bumped) logs.add(0, new String[] { "slots", "9", "@SLOTS@", "ok" });
    StringBuilder add = new StringBuilder();
    int lastGroup = -1;
    for (int a = 0; a < ADD_KEY.length; a++) {
      if (p.getProperty(ADD_KEY[a]) != null) continue;
      String v = ADD_VAL[a];
      if (ADD_KEY[a].startsWith("boost.")) {
        String cv2 = (String) carried.get(ADD_KEY[a].substring(6));
        if (cv2 != null) v = cv2;
        logs.add(new String[] { "boost[" + ADD_KEY[a].substring(6) + "]", "(none)", v, "done" });
      } else logs.add(new String[] { ADD_KEY[a], "(none)", v, "done" });
      if (ADD_GROUP[a] != lastGroup) {
        lastGroup = ADD_GROUP[a];
        String[] nt = GROUP_NOTE[lastGroup].split("\n");
        for (int j = 0; j < nt.length; j++) add.append(nt[j]).append(nl);
      }
      add.append(ADD_KEY[a]).append('=').append(v).append(nl);
    }
    if (logs.size() == 0) return "";
    String result = out.toString();
    if (add.length() > 0) result = result + "# ---- added by SkyyAccessories 0.5 (booster accessories) ----" + nl + add.toString();
    java.nio.file.Path bak = FILE.resolveSibling(FILE.getFileName().toString() + ".pre-0.5.bak");
    if (!hasBoost && !java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0])) java.nio.file.Files.copy(FILE, bak, new java.nio.file.CopyOption[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp-0.5");
    java.io.FileOutputStream fo = new java.io.FileOutputStream(tmp.toFile());
    try { fo.write(result.getBytes("ISO-8859-1")); fo.flush(); fo.getFD().sync(); } finally { fo.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    logMig(logs);
    if (hasBoost) return "config.properties: " + logs.size() + " missing 0.5 settings added (config-changes.log)";
    return "config.properties updated to 0.5 (" + logs.size() + " changes in config-changes.log, the old file kept as config.properties.pre-0.5.bak)";
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to 0.5 - it stays as it is, and the built-in 0.5 numbers apply where it has none: " + t);
    return "config.properties could not be updated to 0.5 (see the warning)";
  }
}""",
# the mod's loader: setup() (first = true: writes the 0.5 default file or migrates a 0.4.x one, first) and the kit's RELOAD after every
# save / hand edit
r"""
public static String load(boolean first) {
  String mig = "";
  if (first) { writeDefaults(); mig = migrate(); }
  java.util.Properties p = new java.util.Properties();
  try {
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) {
    if (!first) {
      @PKG@.AccStore.warn("config.properties could not be read - the current settings stay: " + t);
      return "config.properties could not be read - the current settings stay";
    }
    @PKG@.AccStore.warn("config.properties could not be read - the built-in settings are used: " + t);
    p = new java.util.Properties();
  }
  int sl = intIn(p.getProperty("slots"), @SLOTS@, 1, @CAP@, "slots");
  int rg = intIn(p.getProperty("regenEverySeconds"), @REGEN@, 1, @RMAX@, "regenEverySeconds");
  float[] bo = new float[@NE@ * 5];
  StringBuilder bt = new StringBuilder();
  for (int e = 0; e < @NE@; e++) {
    double[] r = boostIn(p.getProperty("boost." + @PKG@.AccDefs.E_KEYS[e]), e);
    bo[e * 5] = 0.0f;
    for (int t = 0; t < 4; t++) bo[e * 5 + t + 1] = (float) r[t];
    if (!sameRow(r, parseN(BOOST_DEF[e], 4))) bt.append(", ").append(@PKG@.AccDefs.E_KEYS[e]).append(' ').append(rowText(r));
  }
  boolean[] on = new boolean[@NL@];
  StringBuilder off = new StringBuilder();
  for (int li = 0; li < @NL@; li++) {
    on[li] = boolIn(p.getProperty("line." + @PKG@.AccDefs.LINE_ADMIN[li]), true, "line." + @PKG@.AccDefs.LINE_ADMIN[li]);
    if (!on[li]) off.append(", ").append(@PKG@.AccDefs.LINE_ADMIN[li]);
  }
  boolean nt = boolIn(p.getProperty("notice.boosters"), true, "notice.boosters");
  boolean cg = boolIn(p.getProperty("combatToGear"), true, "combatToGear");   // 0.5 part 2
  @PKG@.AccStore.SLOTS = sl;
  @PKG@.AccDefs.REGEN_EVERY = rg;
  @PKG@.AccDefs.BOOST = bo;
@SETLINES@
  @PKG@.AccDefs.NOTICE = nt;
  @PKG@.AccDefs.COMBAT_TO_GEAR = cg;
  StringBuilder tip = new StringBuilder();
  if (rg != @REGEN@) tip.append(", Regeneration every ").append(rg).append(" s");
  tip.append(bt.toString());
  String ts = "";
  if (tip.length() > 0) ts = tip.substring(2);
  if (!ts.equals(TIP_SEEN)) {
    TIP_SEEN = ts;
    if (ts.length() > 0) info("this server's booster numbers differ from what the item tooltips print (built-in numbers - the Accessory Bag page and /accessories lines show the live ones): " + ts);
  }
  String bs = "built-in";
  if (bt.length() > 0) bs = "custom (" + bt.substring(2) + ")";
  String res = "config " + sl + " bag slots, Regeneration every " + rg + " s, booster numbers " + bs;
  if (off.length() > 0) res = res + ", lines switched off: " + off.substring(2);
  if (!nt) res = res + ", the 0.5 notice is off";
  if (!cg) res = res + ", combat stats are not sent to SkyyGear (combatToGear=false)";
  if (mig.length() > 0) res = res + "; " + mig;
  return res;
}""",
r"""
public static String reload() {
  String r = load(false);
  info("config.properties applied: " + r);
  return r;
}""",
# check= hook of the boost table: key = boost[<entry>], value = the canonical text, null = a removal
r"""
public static String checkBoost(String key, String value) {
  String en = key == null ? "" : key;
  int a = en.indexOf('[');
  int b = en.lastIndexOf(']');
  if (a >= 0 && b > a) en = en.substring(a + 1, b);
  int e = entryIndex(en);
  if (e < 0) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < @PKG@.AccDefs.E_KEYS.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.E_KEYS[i]); }
    return "Unknown entry. The booster entries are: " + sb.toString() + ".";
  }
  if (value == null) return "The " + en + " line stays - set it to " + BOOST_DEF[e] + " to go back to the built-in numbers.";
  double[] r = parseN(value, 4);
  if (r == null) return "Needs 4 numbers for Normal,Unique,Rare,Legendary like " + BOOST_DEF[e] + " (no minus sign, up to 2 decimals).";
  double cap = (double) @PKG@.AccDefs.E_CAP[e];
  for (int t = 0; t < 4; t++) if (r[t] > cap) return "Each number must be from 0 to " + dtext(cap) + " - " + @PKG@.AccDefs.DISPLAY[t + 1] + " is " + dtext(r[t]) + ".";
  if (@PKG@.AccDefs.E_WHOLE[e] == 1) {
    for (int t = 0; t < 4; t++) if (r[t] != Math.floor(r[t])) return "Whole numbers only for " + en + " - " + @PKG@.AccDefs.DISPLAY[t + 1] + " is " + dtext(r[t]) + ".";
  }
  return null;
}""",
]:
    _src = JX(_src).replace("@CAP@", str(CAP)).replace("@SLOTS@", str(SLOTS_DEF)).replace("@REGEN@", str(REGEN_EVERY)) \
        .replace("@RMAX@", str(REGEN_MAX)).replace("@NE@", str(len(ENTRIES))).replace("@NL@", str(len(BOOSTERS))) \
        .replace("@SETLINES@", "\n".join("  %s.AccDefs.LINE_%s = on[%d];" % (PKG, b[1].upper(), i) for i, b in enumerate(BOOSTERS)))
    assert "@" not in _src.replace("@PKG@", ""), _src[:80]
    cfg_.addMethod(CtNewMethod.make(_src, cfg_))

# ================= the admin config kit (0.4.4; research/Server-Setup-Spec.md 4.14, tools/CONFIG-CONTRACT.md; 0.5 rows: spec 5.8) =================
# (key, label, cat, type, default, min, max, opts, unit, flags, help, bind) - row key = file key (spec 7: the file key never changes)
CFG_CATS = [("bag", "Accessory Bag"), ("boosters", "Boosters")]
CFG_ROWS = [
    ("slots", "Accessory slots", "bag", "int", str(SLOTS_DEF), "1", str(CAP), "step=1", "", "new,danger",
     "Lowering it deletes nothing: accessories already in higher slots stay and count until taken out.",
     "field:AccStore.SLOTS@config.properties:slots;confirm=down"),
    ("notice.boosters", "Tell players about the accessory change", "bag", "bool", "true", "", "", "", "", "live",
     "One chat line, once, for each player who had accessories before 0.5.",
     "field:AccDefs.NOTICE@config.properties:notice.boosters"),
    ("regenEverySeconds", "Regeneration heals every", "boosters", "int", str(REGEN_EVERY), "1", str(REGEN_MAX), "step=1", "s", "live,adv",
     "How often the Regeneration Accessory heals. Its item tooltip keeps saying %d seconds." % REGEN_EVERY,
     "field:AccDefs.REGEN_EVERY@config.properties:regenEverySeconds"),
    ("boost", "Booster numbers", "boosters", "table", "", "", "60", "text;type;Normal..Legendary", "", "live,danger",
     "Four numbers, Normal to Legendary. The entry name gives the unit. Fall is written without a minus.",
     "reload@config.properties:boost.;check=AccCfg.checkBoost"),
    ("combatToGear", "Send combat stats to SkyyGear", "boosters", "bool", "true", "", "", "", "", "live",
     "Off = %s add nothing (SkyyGear applies their stats)." % " and ".join(
         [", ".join(COMBAT_LINES[:-1]), COMBAT_LINES[-1]] if len(COMBAT_LINES) > 1 else COMBAT_LINES),
     "field:AccDefs.COMBAT_TO_GEAR@config.properties:combatToGear"),
] + [("line.%s" % _b[1], "%s line" % _b[2], "boosters", "bool", "true", "", "", "", "", "live",
      "Off = the line stays in the bag, counts for nothing and the bag page says switched off.",
      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS]
assert all(len(_r[10]) <= 100 for _r in CFG_ROWS), [_r[0] for _r in CFG_ROWS if len(_r[10]) > 100]
CFG_NOTE = "Item tooltips show the built-in numbers - the Accessory Bag page shows this server's."
kit = CFG.emit(pool, PKG, MOD="SkyyAccessories", TITLE="Accessories", VERSION=VERSION, NODE="skyyaccessories.admin", CATS=CFG_CATS,
               ROWS=CFG_ROWS, FILES=["Skyy_SkyyAccessories/config.properties"], NOTE=CFG_NOTE, RELOAD="AccCfg.reload", KEEP=20,
               DEFAULTS={"config.properties": CONFIG_TEXT})

# ================= 0.5.1: the one-time Stamina defaults update (AccCfg.migrate051; the SkyyGear 0.1.1 migrateStat011 pattern) =================
# compiled after CFG.emit: it uses the kit's own parser (CfgFile), History (CfgHist), change log (CfgLog) and atomic write (CfgRows)
cfg_.addField(CtField.make("public static final String[] M51_KEY = new String[] { %s };" % jstrs(M51_KEYS), cfg_))
cfg_.addField(CtField.make("public static final String[] M51_OLD = new String[] { %s };" % jstrs(_o for _k, _o in M51_OLD), cfg_))
cfg_.addField(CtField.make("public static final String[] M51_NEW = new String[] { %s };" % jstrs(M51_NEW), cfg_))
cfg_.addField(CtField.make("public static final String M51_MARK = %s;" % jlit(M51_MARK), cfg_))
cfg_.addField(CtField.make("public static final String M51_MARK_ID = %s;" % jlit(M51_MARK_ID), cfg_))
cfg_.addField(CtField.make("public static final String M51_WHO = %s;" % jlit(M51_WHO), cfg_))
for _src in [
# a key exactly as java.util.Properties / the loader read it (case-sensitive) -> the M51_KEY index, -1 = none
r"""
public static int m51Idx(String k) {
  if (k == null || !k.startsWith("boost.")) return -1;
  for (int i = 0; i < M51_KEY.length; i++) if (("boost." + M51_KEY[i]).equals(k)) return i;
  return -1;
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile.key / value / end). null = the 0.5.1 marker
# is already in a comment line (nothing to do); an empty array = no boost. line at all (a 0.4.x file: the 0.5 migration appends the
# 0.5.1 numbers with the marker). Else { new text, "boost.Stamina.flat 1.5,3,4.5,6 -> 3,6,9,12, ...", String[] kept notes,
# String[] { entry, old, new }* }. A key whose LAST live entry (the one Properties keeps) is a one-line entry holding the 0.5 numbers
# (as 4 numbers) is updated: every one-line entry of it that holds them gets the 0.5.1 text (value text only: key, separator and CR
# stay). Anything else is kept: a custom value (noted unless it already is the 0.5.1 default), a continued entry (noted), a missing
# line (silent). The marker goes on its own line right above the first boost.Stamina entry, else above the first boost. entry - the
# start of a logical line, so nothing continues into it. Every line is scanned from the start of a logical line.
r"""
public static Object[] m51Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = M51_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int firstStam = -1;
  int firstBoost = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M51_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    if (firstBoost < 0 && key != null && key.startsWith("boost.")) firstBoost = k;
    int m = m51Idx(key);
    if (m >= 0) {
      if (firstStam < 0) firstStam = k;
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    k = e + 1;
  }
  if (firstBoost < 0) return new Object[0];
  int at = firstStam >= 0 ? firstStam : firstBoost;
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && sameRow(parseN(eff[i], 4), parseN(M51_OLD[i], 4))) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append("boost.").append(M51_KEY[i]).append(' ').append(oneLine(eff[i])).append(" -> ").append(M51_NEW[i]);
      rows.add(M51_KEY[i]);
      rows.add(eff[i]);
      rows.add(M51_NEW[i]);
    } else if (multi[i] || !sameRow(parseN(eff[i], 4), parseN(M51_NEW[i], 4))) {
      kept.add("boost." + M51_KEY[i] + "=" + oneLine(eff[i]) + " kept (custom) - the 0.5.1 default is " + M51_NEW[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == at) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M51_MARK + (crm ? "\r" : ""));
    }
    int m2 = m51Idx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && sameRow(parseN(@PKG@.CfgFile.value(l, k).trim(), 4), parseN(M51_OLD[m2], 4))) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M51_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M51_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""",
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): History + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyyAccessories)
r"""
public static void m51Kit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.AccStore.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""",
# CfgHist.snapshot swallows its own errors, so the update checks that config-history really holds a copy with exactly these bytes (the
# new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log (SkyyGear review finding 3)
r"""
public static boolean m51Saved(byte[] old) {
  String[] have = @PKG@.CfgHist.list(0);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(0, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""",
# one config-changes.log line in the kit's table format (CfgLog.add without its per-line INFO): time, name, uuid, via, key, old, new,
# status - the key is the table row key + [entry], so Server Setup -> Changes undoes it with a tset back to the old value
r"""
public static String m51Log(String e, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M51_WHO + "\t-\tupdate\tboost[" + @PKG@.CfgRows.oneLine(e) + "]\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""",
# setup(), BEFORE load(true) (the loader, the 0.5 migration) and CfgPub.start: the file before this update becomes a History version
# (KEEP 20, verified by m51Saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one
# change-log line per updated entry, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by "; " ("" = nothing
# done: no file, no boost. line yet, marker already there, or a failure - WARN, file untouched, the next start tries again)
r"""
public static synchronized String migrate051() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m51Update(new String(old, "ISO-8859-1"));
    if (r == null || r.length == 0) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m51Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M51_WHO, "before the 0.5.1 Stamina defaults update");
    if (!m51Saved(old)) {
      @PKG@.AccStore.warn("config.properties NOT updated to the 0.5.1 Stamina defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(m51Log(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.5.1 Stamina defaults: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no Stamina line still had its 0.5 numbers - nothing changed (0.5.1 Stamina marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append("; ").append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to the 0.5.1 Stamina defaults (the file is used as it is): " + t);
    return "";
  }
}""",
]:
    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))

# ================= 0.5 part 2: AccGear - combat stats to SkyyGear (gear:extra:<uuid>), the bag page notes, bridge clean-up =================
# SkyyGear 0.1 (live) / 0.1.1 / 0.1.2 read gear:extra:<uuid> as ONE String ("str:40,cc:10": GearStats.extra -> parseExtra, whole numbers,
# unknown keys skipped) and add it to the totals of every hit (GearStats.totals(..., withExtra = true) in the offence and Defense
# handlers). No other mod writes the key (every build script in this repo checked), so SkyyAccessories OWNS it (spec 5.4, "one
# gear:extra writer" in 4.2): the text is written only when it changes; removed when it becomes empty, for every player who left
# (AccTick, every 5 s) and on shutdown - always with Map.remove(key, ourText), so a text another mod wrote is never removed. A text we
# did not write is overwritten with one WARN per player; when it changes again within 5 s after that overwrite (a second writer) or
# is not a String at all (another format), writing stops for that player until they rejoin or switch profile (profile:epoch changes),
# with one more WARN - two writers never fight every second. Bridge values are java.lang types only.
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> our text in the bridge
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap AT = new java.util.concurrent.ConcurrentHashMap();")      # uuid -> Long ms of our overwrite of a foreign text
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap STOP = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> the profile epoch we stopped at
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> the overwrite WARN was logged
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap MOVED = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> we have a movement entry
JF(gear, 'public static final String SOURCE = "accessories.talismans";')   # our movement protocol source (tools/skyymove.py)
JF(gear, 'public static final String OWNER_FALL = "stat:owner:fallDamage";')   # SkyySkills claims it: it applies every source's fall damage
JM(gear, r"""
public static String keyOf(java.util.UUID u) {
  return "gear:extra:" + u.toString();
}""")
JM(gear, r"""
public static String clip(Object o) {
  String t = String.valueOf(o);
  return t.length() > 80 ? t.substring(0, 80) + "..." : t;
}""")
JM(gear, r"""
public static Object epochMark(java.util.UUID u) {
  Object ep = @PKG@.AccStore.epochOf(u);
  if (ep == null) return "-";
  return ep;
}""")
# the text for one bag: best = AccDefs.activeTiers (switched-off lines 0); every gear:extra entry of the line's best rarity, floored to a
# whole number (SkyyGear floors each part anyway), summed per key, keys in GEAR_KEYS order, zero parts left out; "" = nothing to send
JM(gear, r"""
public static String textOf(int[] best) {
  if (!@PKG@.AccDefs.COMBAT_TO_GEAR || best == null) return "";
  String[] gk = @PKG@.AccDefs.GEAR_KEYS;
  long[] sum = new long[gk.length];
  float[] bo = @PKG@.AccDefs.BOOST;
  for (int e = 0; e < @PKG@.AccDefs.E_GEAR.length; e++) {
    String g = @PKG@.AccDefs.E_GEAR[e];
    if (g.length() == 0) continue;
    int li = @PKG@.AccDefs.E_LINE[e];
    int t = li >= 0 && li < best.length ? best[li] : 0;
    if (t < 1 || t > 4) continue;
    int gi = -1;
    for (int k = 0; k < gk.length; k++) if (gk[k].equals(g)) gi = k;
    if (gi < 0) continue;
    double v = Math.floor((double) bo[e * 5 + t]);
    if (v > 0.0) sum[gi] = sum[gi] + (long) v;
  }
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < gk.length; k++) {
    if (sum[k] <= 0L) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(gk[k]).append(':').append(sum[k]);
  }
  return sb.toString();
}""")
# publish one player's text (any thread: the bridge is a ConcurrentHashMap; the tick calls it on the world thread once a second).
# Returns 0 nothing written, 1 written, 2 removed, 3 a foreign text overwritten, 4 writing stopped for this player.
JM(gear, r"""
public static int publish(java.util.UUID u, String name, String text, long now) {
  if (u == null) return 0;
  String key = keyOf(u);
  java.util.Map b = @PKG@.AccStore.bridge();
  Object st = STOP.get(u);
  if (st != null) {
    if (st.equals(epochMark(u))) return 0;
    STOP.remove(u);
    AT.remove(u);
    WARNED.remove(u);
    @PKG@.AccCfg.info("gear:extra for " + name + ": the profile switched - SkyyAccessories writes it again");
  }
  String tx = text == null ? "" : text;
  Object cur = b.get(key);
  String last = (String) LAST.get(u);
  if (cur != null && !(cur instanceof String)) {
    STOP.put(u, epochMark(u));
    LAST.remove(u);
    @PKG@.AccStore.warn(key + " (" + name + ") holds a " + cur.getClass().getName() + ", not a text - another mod's format, so SkyyAccessories leaves it alone and sends no accessory combat stats for this player until they rejoin or switch profile");
    return 4;
  }
  boolean foreign = cur != null && (last == null || !last.equals(cur));
  if (foreign) {
    Long at = (Long) AT.get(u);
    if (at != null && now - at.longValue() < 5000L) {
      STOP.put(u, epochMark(u));
      LAST.remove(u);
      AT.remove(u);
      @PKG@.AccStore.warn(key + " (" + name + ") changed again within 5 s after SkyyAccessories wrote it (now: " + clip(cur) + ") - a second writer; SkyyAccessories stops writing it for this player until they rejoin or switch profile");
      return 4;
    }
    if (tx.length() == 0) { LAST.remove(u); return 0; }   // nothing of ours to send: the other text stays
    if (!WARNED.containsKey(u)) {
      WARNED.put(u, Boolean.TRUE);
      @PKG@.AccStore.warn(key + " (" + name + ") held a text SkyyAccessories did not write (" + clip(cur) + ") - SkyyAccessories is the only writer of this key and replaces it");
    }
    b.put(key, tx);
    LAST.put(u, tx);
    AT.put(u, Long.valueOf(now));
    return 3;
  }
  if (tx.length() == 0) {
    LAST.remove(u);
    if (cur != null) { b.remove(key, cur); return 2; }
    return 0;
  }
  if (tx.equals(cur)) { LAST.put(u, tx); return 0; }
  b.put(key, tx);
  LAST.put(u, tx);
  return 1;
}""")
# our movement entry for one player (the protocol's own remove: MoveSync.post with all zeros does exactly this)
JM(gear, r"""
public static void dropMove(java.util.UUID u) {
  try {
    Object o = @PKG@.AccStore.bridge().get("move:" + u.toString());
    if (o instanceof java.util.Map) ((java.util.Map) o).remove(SOURCE);
  } catch (Throwable t) { }
}""")
# every player who left (AccTick, every 5 s, any thread): our gear:extra text and movement entry go, the per-player state is forgotten
JM(gear, r"""
public static void prune(java.util.Set online) {
  java.util.Map b = @PKG@.AccStore.bridge();
  java.util.Iterator it = LAST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (online.contains(e.getKey())) continue;
    b.remove(keyOf((java.util.UUID) e.getKey()), e.getValue());
    it.remove();
  }
  java.util.Iterator mi = MOVED.keySet().iterator();
  while (mi.hasNext()) {
    java.util.UUID mu = (java.util.UUID) mi.next();
    if (online.contains(mu)) continue;
    dropMove(mu);
    mi.remove();
  }
  AT.keySet().retainAll(online);
  STOP.keySet().retainAll(online);
  WARNED.keySet().retainAll(online);
}""")
# plugin shutdown: every text we wrote and every movement entry of ours leaves the bridge (the bridge outlives a plugin reload)
JM(gear, r"""
public static void shutdownAll() {
  java.util.Map b = @PKG@.AccStore.bridge();
  java.util.Iterator it = LAST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    b.remove(keyOf((java.util.UUID) e.getKey()), e.getValue());
  }
  java.util.Iterator mi = MOVED.keySet().iterator();
  while (mi.hasNext()) dropMove((java.util.UUID) mi.next());
  LAST.clear();
  MOVED.clear();
  AT.clear();
  STOP.clear();
  WARNED.clear();
}""")
# SkyyGear running = its bridge functions are there (gear:fn:stats, gear:gates - SkyyGear 0.1 setup); its combat stats switch = the
# kit's config:fn:SkyyGear "get" of part.stats (a java.lang call; tools/CONFIG-CONTRACT.md: never throws, never touches the world).
# Unknown (no config function, an odd answer) counts as on.
JM(gear, r"""
public static boolean gearRunning() {
  java.util.Map b = @PKG@.AccStore.bridge();
  return b.get("gear:fn:stats") instanceof java.util.function.Function || b.get("gear:gates") != null;
}""")
JM(gear, r"""
public static boolean gearStatsOn() {
  try {
    Object f = @PKG@.AccStore.bridge().get("config:fn:SkyyGear");
    if (!(f instanceof java.util.function.Function)) return true;
    Object r = ((java.util.function.Function) f).apply(new Object[] { "get", "part.stats" });
    if (!(r instanceof String)) return true;
    String x = ((String) r).trim().toLowerCase();
    return !(x.equals("false") || x.equals("off") || x.equals("no") || x.equals("0"));
  } catch (Throwable t) { return true; }
}""")
JM(gear, r"""
public static boolean fallOwned() {
  return @PKG@.AccStore.bridge().get(OWNER_FALL) != null;
}""")
# why the combat lines do nothing for this player right now ("" = they work): the bag page's "Combat stats" note
JM(gear, r"""
public static String combatNote(java.util.UUID u) {
  if (!@PKG@.AccDefs.COMBAT_TO_GEAR) return "not sent - switched off in Server Setup";
  if (!gearRunning()) return "need SkyyGear, which is not running";
  if (!gearStatsOn()) return "off in SkyyGear (Gear stats in combat)";
  if (u != null && STOP.containsKey(u)) return "paused - another mod writes them (server log)";
  return "";
}""")
# the Bonuses well of the bag page: AccDefs.bonusRows + the notes in the free rows (a combat line that sends nothing, Feather's fall part
# without a fall-damage owner) - [key0, value0, ...], BONUS_MAX rows
JM(gear, r"""
public static String[] pageRows(String[] s, java.util.UUID u) {
  String[] r = @PKG@.AccDefs.bonusRows(s);
  int max = @PKG@.AccDefs.BONUS_MAX;
  int n = 0;
  while (n < max && r[n * 2].length() > 0) n++;
  int[] best = @PKG@.AccDefs.activeTiers(s);
  boolean gear = false;
  boolean fall = false;
  for (int li = 0; li < best.length; li++) {
    if (best[li] <= 0) continue;
    if (@PKG@.AccDefs.sendsGear(li, best[li])) gear = true;
    if (@PKG@.AccDefs.hasFall(li, best[li])) fall = true;
  }
  if (gear && n < max) {
    String cn = combatNote(u);
    if (cn.length() > 0) { r[n * 2] = "Combat stats"; r[n * 2 + 1] = cn; n++; }
  }
  if (fall && n < max && !fallOwned()) { r[n * 2] = "Fall damage"; r[n * 2 + 1] = "needs SkyySkills, which is not running"; n++; }
  return r;
}""")

# ================= AccFn (bridge function acc:fn:has) =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addConstructor(CtNewConstructor.make("public AccFn() { }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    return Boolean.valueOf({PKG}.AccStore.has((java.util.UUID) a[0], String.valueOf(a[1])));
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", fn))

# ================= AccPage =================
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public String[] invIds;", page))
page.addField(CtField.make("public String key;", page))   # 0.4.1: profile storage key the page was built for
page.addField(CtField.make("public int slotPage;", page))   # 0.5: the bag slot pager (clamped in build())
page.addField(CtField.make("public int invPage;", page))    # 0.5: the inventory list pager (clamped in build())
page.addConstructor(CtNewConstructor.make(f"""
public AccPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
  this.info = "";
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
# accessory item ids carried in storage/hotbar/backpack (distinct)
page.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList carried({PLA} p) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList old = new java.util.ArrayList();   // 0.4.2: retired accessories, appended after the usable ones
  {INV} inv = p.getInventory();
  if (inv == null) return out;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (!{PKG}.AccDefs.isAccessory(id)) continue;
      if ({PKG}.AccDefs.isRetired(id)) {{ if (!old.contains(id)) old.add(id); }}
      else if (!out.contains(id)) out.add(id);
    }}
  }}
  out.addAll(old);   // 0.4.2: so they never push a usable accessory out of the Equip rows
  return out;
}}""", page))
# remove one of item id from any inventory section; true when removed
page.addMethod(CtNewMethod.make(f"""
public static boolean takeOne({PLA} p, String id) {{
  {INV} inv = p.getInventory();
  if (inv == null) return false;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      {ISS} tx = cont.removeItemStackFromSlot(s, 1);
      if (tx != null && tx.succeeded()) return true;
    }}
  }}
  return false;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public static boolean giveOne({PLA} p, String id) {{
  try {{
    {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    tx = p.getInventory().getHotbar().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    {IC} bp = p.getInventory().getBackpack();
    if (bp == null) return false;
    tx = bp.addItemStack(new {IS}(id, 1));
    return tx != null && tx.succeeded();
  }} catch (Throwable t) {{ return false; }}
}}""", page))
# ================= AccPage look (0.4.5; 0.5: bonus columns + pagers): the vanilla UI kit tools/skyyui.py, called when THIS script runs =================
# research/Vanilla-UI-Style-Guide.md sections 3, 7, 8c. acc_page_*() build the markup from kit calls (every value proven by SUI.verify() at
# the top of this script). The Java the kit emits gets a name here (ACC_*_JAVA) and is interpolated into the build() f-string below as
# {ACC_..._JAVA}: interpolated text is never re-parsed by Python, so the kit's Java string literals reach javassist exactly as written.
# ---- ACC PAGE BLOCK START (SkyyAccessories/test_skyyaccessories_0.5.py execs this block and ACC_BUILD_SRC below, with SUI verified,
# PKG, CAP, PAGE_ROWS, BONUS_MAX and the class-name constants defined, and compares the compiled build() with acc_page_state())
ACC_PREFIX = "SkyyAcc"                 # every element id starts with it; 0.4.4's root #SkyyAcc = the body
ACC_COL_W, ACC_COL_GAP = 580, 16       # two list wells: the bag slots | the accessories in the inventory
ACC_LIST_PAD = SUI.WELL_LIST_PAD       # 4: the vanilla list well's padding (WorldEventPanelPage #ListContainer)
ACC_COL_IN = ACC_COL_W - 2 * ACC_LIST_PAD                                       # 572: the width of a row inside a well
ACC_W = 2 * ACC_COL_W + ACC_COL_GAP + 2 * SUI.CONTENT_PAD                     # 1210
ACC_ROW_H, ACC_ROW_GAP = SUI.ROW_H_READABLE, SUI.ROW_GAP                       # 56 + 3: two readable lines (18 px name, 15 px rarity)
ACC_ACT_W = 112                        # UNEQUIP / EQUIP: a small Secondary row action (vanilla 92; 112 keeps UNEQUIP at 14 px)
ACC_PANEL_W = ACC_COL_IN - 4 - ACC_ACT_W                                       # the row panel; the action sits 4 px right of it
ACC_BAR = 4 + 8                        # the status bar (4 px + 8 px gap, WorldEventListRow)
ACC_ICON, ACC_ICON_BOX = 40, 52        # 40 px item icon in a 52 px box (12 px to the text)
ACC_ROW_PAD = 8                        # row panel padding left / right (WorldEventListRow)
ACC_TEXT_W = ACC_PANEL_W - 2 * ACC_ROW_PAD - ACC_BAR - ACC_ICON_BOX            # 376
ACC_NAME_H, ACC_SUB_H = SUI.fs(14) + 6, SUI.fs(12) + 5                          # 24 + 20 (the kit's row_text heights)
ACC_TEXT_TOP = (ACC_ROW_H - ACC_NAME_H - ACC_SUB_H) // 2                       # 6
ACC_LINE_H = 26                        # hint / bonus summary lines
ACC_TOP_PAD = 8
ACC_BON_ROWS, ACC_BON_H = BONUS_MAX // 2, 22                                    # 0.5: two columns of 6 bonus rows (16 px, one line)
ACC_BON_W = (ACC_W - 2 * SUI.CONTENT_PAD - 2 * 8) // 2                          # 580: half the top well's inner width
ACC_BON_KEY_W = SUI.PROP_KEY_W                                                  # 0.5 part 2: 150, the WorldEventPropertyRow key column
ACC_BON_VAL_W = ACC_BON_W - ACC_BON_KEY_W - 8                                   # 422: the value (the key's right margin is 8)
ACC_TOP_H = 2 * ACC_TOP_PAD + 2 * ACC_LINE_H + ACC_BON_ROWS * ACC_BON_H         # 200: the well on top
ACC_SEC_H = SUI.fs(13) + 10 + 10 + 4   # section head 26 + its margins 10 / 4 (WorldEventSectionLabel)
ACC_ROWS_H = PAGE_ROWS * (ACC_ROW_H + ACC_ROW_GAP)                              # 531: one page of rows (a fixed group)
ACC_PG_BTN_W, ACC_PG_CAP_W, ACC_PG_GAP = 120, 260, 12                           # 0.5: the kit pager in a 572 px well (524 px wide)
ACC_PG_H = SUI.BTN_SMALL_H + 8                                                  # 40: the pager's .h (32 + its top margin 8)
ACC_COLS_H = 2 * ACC_LIST_PAD + ACC_SEC_H + ACC_ROWS_H + ACC_PG_H              # 619: a list well = head + one page of rows + pager
ACC_SEP_H = 1 + 2 * SUI.SEP_MARGIN     # content separator 1 px, 8 px above and below
ACC_INFO_H = 44                        # the result line: 16 px bold, wraps to two lines
ACC_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + ACC_TOP_H + ACC_COLS_H + ACC_SEP_H + ACC_INFO_H     # 952 (fits 1080)
ACC_HINT = "Bench accessories unlock /craft recipes. Stat accessories add their bonus while they sit here - only your best of each line counts."
ACC_EMPTY = "Empty slot"
ACC_NONE = "None - craft accessories at a Workbench"
ACC_INFO_COLOR = "infoColor(this.info)"   # the Java colour expression of the result line (AccPage.infoColor below)
UI_DATA_COLORS = ["#8a97a3"]           # AccDefs.RETIRED_COLOR (0.4.2): a retired accessory's name + rarity word - data, like the rarity colours
assert (ACC_W, ACC_H) == (1210, 952) and ACC_COL_IN == 572 and ACC_TEXT_W == 376 and ACC_TEXT_TOP == 6, (ACC_W, ACC_H, ACC_TEXT_W)
assert ACC_ACT_W - 2 * SUI.BTN_SMALL_PAD >= 64 + 8, "UNEQUIP (64 px at 14 px bold) fits the small button without shrinking"
assert 2 * ACC_PG_BTN_W + 2 * ACC_PG_GAP + ACC_PG_CAP_W <= ACC_COL_IN, "the pager fits a list well"
SUI.assert_page_size(ACC_W, ACC_H)
# AccPage.infoColor: the result line's colour from the result text (no +/-/= marks in the texts): vanilla success green = done, error
# red = refused (nothing moved, or an item could not be given back), info blue = a note (the profile switched) and the Campfire line
# shown while no result is set. The patch (tools/acc_0_5_patch.py) asserts the full list of texts handleDataEvent sets; the harness
# runs this method on the real texts.
ACC_INFO_COLOR_SRC = """
public static String infoColor(String t) {
  if (t == null || t.length() == 0) return "%(eq)s";
  if (t.startsWith("upgraded to ")) return t.indexOf(" could not be returned") >= 0 ? "%(no)s" : "%(ok)s";
  if (t.startsWith("equipped ") || t.startsWith("unequipped ")) return "%(ok)s";
  if (t.startsWith("your profile changed")) return "%(eq)s";
  return "%(no)s";
}""" % {"ok": SUI.STATUS["+"], "no": SUI.STATUS["-"], "eq": SUI.STATUS["="]}


def acc_pager(parent, prefix, st):
    """The kit pager (Prev / caption / Next, small Secondary buttons, the Disabled look at the ends) under a list well's rows:
    st = (caption, prev_on, next_on) - J() values in the build, plain values in checks. Ids #<prefix>Prev / Page / Next."""
    cap, prev_on, next_on = st
    p = SUI.pager(parent, prefix, ACC_COL_IN, text=cap, prev_on=prev_on, next_on=next_on, btn_w=ACC_PG_BTN_W, caption_w=ACC_PG_CAP_W,
                  gap=ACC_PG_GAP)
    assert p.h == ACC_PG_H and (p.prev, p.page, p.next) == (prefix + "Prev", prefix + "Page", prefix + "Next"), (p.h, p.prev)
    return p


def acc_page_shell(bonus, bon, info, head, sp, ip):
    """The window + everything that is not a row: the top well (hint, #SkyyAccBonus, the bonus rows #SkyyAccBr0..11 in two columns:
    key #SkyyAccBk<k> + value #SkyyAccBon<k>), the two list wells with their section heads, their fixed row groups #SkyyAccSlotRows /
    #SkyyAccInvRows and pagers #SkyyAccSp / #SkyyAccIp, the separator and #SkyyAccInfo (colour = ACC_INFO_COLOR, a J() in the markup).
    bonus / bon (12 (key, value) pairs) / info / head (the slot head) = the b.set values; sp / ip = the pager states (see acc_pager).
    The bonus rows are the kit's property-row look (Pages/WorldEvent/WorldEventPropertyRow: the propKey label 150 px + 8, the
    propValue label, LayoutMode Left) with fixed widths and one line each: skyyui.property_row itself writes FlexWeight and
    WrapMaxLines, which skyyui.PROBED does not list yet (assert_proven). Returns the Shell."""
    sh = SUI.page_shell(ACC_PREFIX + "F", ACC_W, ACC_H, "Accessory Bag", body_id=ACC_PREFIX)
    ap, body = sh.appends, sh.body
    ap.append((body, SUI.panel("SkyyAccTop", "well", h=ACC_TOP_H, pad={"horizontal": 8, "vertical": ACC_TOP_PAD})))
    sh.text("SkyyAccTop", "SkyyAccHint", ACC_HINT, "default", h=ACC_LINE_H)             # left-aligned like the vanilla #Summary text
    ap.append(("SkyyAccTop", SUI.label("SkyyAccBonus", "", "propValue", h=ACC_LINE_H, wrap=False)))   # a value, not a result line
    ap.append(("SkyyAccTop", SUI.group("SkyyAccBonCols", "Left", h=ACC_BON_ROWS * ACC_BON_H)))
    for c in range(2):
        col = "SkyyAccBonC%d" % c
        ap.append(("SkyyAccBonCols", SUI.group(col, "Top", w=ACC_BON_W, h=ACC_BON_ROWS * ACC_BON_H)))
        for r in range(ACC_BON_ROWS):
            k = c * ACC_BON_ROWS + r
            ap.append((col, SUI.group("SkyyAccBr%d" % k, "Left", w=ACC_BON_W, h=ACC_BON_H)))
            ap.append(("SkyyAccBr%d" % k, SUI.label("SkyyAccBk%d" % k, "", "propKey", w=ACC_BON_KEY_W, h=ACC_BON_H, wrap=False,
                                                    anchor={"right": 8})))
            ap.append(("SkyyAccBr%d" % k, SUI.label("SkyyAccBon%d" % k, "", "propValue", w=ACC_BON_VAL_W, h=ACC_BON_H, wrap=False)))
    ap.append((body, SUI.group("SkyyAccCols", "Left", h=ACC_COLS_H)))
    ap.append(("SkyyAccCols", SUI.panel("SkyyAccLeft", "well", w=ACC_COL_W, h=ACC_COLS_H, pad=ACC_LIST_PAD)))
    ap.append(("SkyyAccCols", SUI.panel("SkyyAccRight", "well", w=ACC_COL_W, h=ACC_COLS_H, pad=ACC_LIST_PAD, anchor={"left": ACC_COL_GAP})))
    ap.append(("SkyyAccLeft", SUI.section("SkyyAccSlotsH", "")))                      # "Bag slots - 3 of 18 used" (b.set)
    ap.append(("SkyyAccLeft", SUI.group("SkyyAccSlotRows", "Top", h=ACC_ROWS_H)))
    ap.extend(acc_pager("SkyyAccLeft", "SkyyAccSp", sp))
    ap.append(("SkyyAccRight", SUI.section("SkyyAccInvH", "Accessories in your inventory")))
    ap.append(("SkyyAccRight", SUI.group("SkyyAccInvRows", "Top", h=ACC_ROWS_H)))
    ap.extend(acc_pager("SkyyAccRight", "SkyyAccIp", ip))
    ap.append((body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})))
    ap.append((body, SUI.status_line("SkyyAccInfo", ACC_INFO_COLOR, h=ACC_INFO_H, wrap=True)))
    ap.sets.append(("SkyyAccSlotsH", "Text", head))
    ap.sets.append(("SkyyAccBonus", "Text", bonus))
    assert len(bon) == BONUS_MAX and all(len(kv) == 2 for kv in bon), "bon = %d (key, value) pairs" % BONUS_MAX
    for k in range(BONUS_MAX):
        ap.sets.append(("SkyyAccBk%d" % k, "Text", bon[k][0]))
        ap.sets.append(("SkyyAccBon%d" % k, "Text", bon[k][1]))
    ap.sets.append(("SkyyAccInfo", "Text", info))
    SUI.fit([ACC_LINE_H, ACC_LINE_H, ACC_BON_ROWS * ACC_BON_H], ACC_TOP_H - 2 * ACC_TOP_PAD, "top well")
    SUI.fit([ACC_BON_W, ACC_BON_W], sh.inner_w - 2 * 8, "bonus columns")
    SUI.fit([ACC_BON_KEY_W, 8, ACC_BON_VAL_W], ACC_BON_W, "bonus row")
    SUI.fit([ACC_COL_W, ACC_COL_GAP, ACC_COL_W], sh.inner_w, "columns")
    SUI.fit([ACC_SEC_H, ACC_ROWS_H, ACC_PG_H], ACC_COLS_H - 2 * ACC_LIST_PAD, "list well")
    SUI.fit([ACC_ROW_H + ACC_ROW_GAP] * PAGE_ROWS, ACC_ROWS_H, "one page of rows")
    SUI.fit([ACC_PANEL_W, 4, ACC_ACT_W], ACC_COL_IN, "row in the well")
    SUI.fit([ACC_ROW_PAD, ACC_BAR, ACC_ICON_BOX, ACC_TEXT_W, ACC_ROW_PAD], ACC_PANEL_W, "row panel")
    left = sh.fit([ACC_TOP_H, ACC_COLS_H, ACC_SEP_H, ACC_INFO_H], "accessory page body")
    assert left == 0 and sh.inner_w == 2 * ACC_COL_W + ACC_COL_GAP, "the body must be filled exactly (no FlexWeight filler): %d px left" % left
    return sh


def acc_page_row_box(ap, col, rid):
    """The row container #<rid> (a bag slot or an inventory row: LayoutMode Left, 56 + 3) in the row group col."""
    ap.append((col, SUI.group(rid, "Left", h=ACC_ROW_H, anchor={"bottom": ACC_ROW_GAP})))


def acc_page_row_full(ap, rid, act_id, act_text, item, name, rarity, colr):
    """A filled row inside #<rid>: the WorldEventListRow look with fixed widths - the row panel #<rid>P (#101925(0.55), padding 8) with
    the status bar, the item icon #<rid>Ic (ItemIcon: the item id only, metadata-free), the name #<rid>Nm (18 px bold) + the rarity
    word #<rid>Rr (15 px), both in the rarity colour colr and b.set - then the small Secondary action button act_id."""
    ap.append((rid, SUI.panel(rid + "P", "row", w=ACC_PANEL_W, h=ACC_ROW_H, layout="Left", pad={"left": ACC_ROW_PAD, "right": ACC_ROW_PAD})))
    ap.append((rid + "P", SUI.group(rid + "Bar", None, w=4, anchor={"right": 8}, extra="Background: " + SUI.COLOR["selected"])))
    ap.append((rid + "P", SUI.group(rid + "Ib", None, w=ACC_ICON_BOX, h=ACC_ROW_H)))
    ap.append((rid + "Ib", SUI.item_icon(rid + "Ic", item, ACC_ICON, anchor={"left": 0, "top": (ACC_ROW_H - ACC_ICON) // 2})))
    ap.append((rid + "P", SUI.group(rid + "T", "Top", w=ACC_TEXT_W, h=ACC_ROW_H, pad={"top": ACC_TEXT_TOP})))
    ap.text(rid + "T", rid + "Nm", name, "rowName", h=ACC_NAME_H, col=colr)
    ap.text(rid + "T", rid + "Rr", rarity, "rowSub", h=ACC_SUB_H, col=colr)
    ap.append((rid, SUI.row_action(act_id, act_text, w=ACC_ACT_W)))


def acc_page_row_empty(ap, rid):
    """An empty bag slot inside #<rid>: a static row panel across the well with the grey caption "Empty slot" at the name position."""
    ap.append((rid, SUI.panel(rid + "P", "row", w=ACC_COL_IN, h=ACC_ROW_H, layout="Left", pad={"left": ACC_ROW_PAD, "right": ACC_ROW_PAD})))
    ap.append((rid + "P", SUI.spacer(w=ACC_BAR + ACC_ICON_BOX)))
    ap.append((rid + "P", SUI.label(None, ACC_EMPTY, "caption", w=ACC_COL_IN - 2 * ACC_ROW_PAD - ACC_BAR - ACC_ICON_BOX, h=ACC_ROW_H)))


def acc_page_none():
    """The line in the inventory list when no accessory is carried."""
    return SUI.label(None, ACC_NONE, "caption", h=30, anchor={"left": 2})


def acc_page_state(bonus, bon, info, head, sp, ip, slots, inv, inv_total):
    """The whole page for ONE state, as the chunks build() emits in order (each an Appends: its appends, then its b.set lines):
    slots = the rows of the CURRENT slot page [(slot index, None for an empty slot | (item, name, rarity, colour))], inv = the rows of
    the current inventory page [(index into invIds, (item, name, rarity, colour))], inv_total = how many accessories are carried (0 =
    the "none" line). Values are plain strings or J(expr, sample); the result line's colour stays the J(ACC_INFO_COLOR). Used by the
    build-time check of sample states below and by the harness, which compares these chunks with what the compiled build() sends."""
    sh = acc_page_shell(bonus, bon, info, head, sp, ip)
    chunks = [sh.appends]
    for i, v in slots:
        rid = "SkyyAccSlot" + str(i)
        box = SUI.Appends()
        acc_page_row_box(box, "SkyyAccSlotRows", rid)
        chunks.append(box)
        ap = SUI.Appends()
        if v is None:
            acc_page_row_empty(ap, rid)
        else:
            acc_page_row_full(ap, rid, "SkyyAccUn" + str(i), "Unequip", v[0], v[1], v[2], v[3])
        chunks.append(ap)
    if inv_total == 0:
        chunks.append(SUI.Appends([("SkyyAccInvRows", acc_page_none())]))
    for i, v in inv:
        ap = SUI.Appends()
        acc_page_row_box(ap, "SkyyAccInvRows", "SkyyAccInv" + str(i))
        acc_page_row_full(ap, "SkyyAccInv" + str(i), "SkyyAccEq" + str(i), "Equip", v[0], v[1], v[2], v[3])
        chunks.append(ap)
    return chunks


def acc_page_check(chunks):
    """check_page on a whole state (ids, prefix, no duplicates, every parent created first, every b.set target exists) and the proven
    property table (kit 1.4 assert_proven: only what deployed pages use)"""
    whole = SUI.Appends()
    for c in chunks:
        whole += c
    SUI.assert_proven(whole, what="accessory page")
    return SUI.check_page(whole, ACC_PREFIX)


def _acc_java(ap, indent, known=()):
    """The Java statements of one Appends (appends, then b.set lines), checked first, indented for the build() source."""
    SUI.check_page(ap, ACC_PREFIX, known_parents=[SUI.render(k) for k in known])
    return LF.join(indent + ln for ln in ap.java("b").split(LF))


LF = chr(10)
_I = SUI.J("i", "0")                   # the row's index in build() (slot index / index into invIds); ids like "SkyyAccSlot" + (i) + "Nm"
_SLOT, _INV = "SkyyAccSlot" + _I, "SkyyAccInv" + _I
_Q = SUI.RARITY["Legendary"]           # colour sample of the runtime rarity colour (AccDefs.rarityColor)
# the texts: the Java expressions of build() (b.set never parses markup); safe() stays on the ItemIds (inline markup)
ACC_SH = acc_page_shell(SUI.J(PKG + ".AccDefs.bonusText(s)", "Bonuses - none yet - put accessories in this bag"),
                        [(SUI.J("bl[%d]" % (2 * k), "Stamina"), SUI.J("bl[%d]" % (2 * k + 1), "+12 max Stamina, +10% Stamina Regen"))
                         for k in range(BONUS_MAX)],
                        SUI.J("this.info != null && this.info.length() > 0 ? this.info : " + PKG + ".AccStore.campLine(s)",
                              "equipped Legendary Health Accessory"),
                        SUI.J("slotsHead", "Bag slots - 3 of 18 used"),
                        (SUI.J("slotCaption", "Page 1 / 2"), SUI.J("this.slotPage > 0", "true"), SUI.J("this.slotPage < slotPages - 1", "true")),
                        (SUI.J("invCaption", "Page 1 / 1"), SUI.J("this.invPage > 0", "true"), SUI.J("this.invPage < invPages - 1", "true")))
SUI.check_page(ACC_SH.appends, ACC_PREFIX)
SUI.assert_proven(ACC_SH.appends, what="accessory page shell")
ACC_TOP_JAVA = LF.join("  " + ln for ln in ACC_SH.java("b").split(LF))
_ap = SUI.Appends()
acc_page_row_box(_ap, "SkyyAccSlotRows", _SLOT)
ACC_SLOT_JAVA = _acc_java(_ap, "    ", known=["SkyyAccSlotRows"])
_ap = SUI.Appends()
acc_page_row_full(_ap, _SLOT, "SkyyAccUn" + _I, "Unequip", SUI.J("safe(s[i])", "Skyy_Talisman_Vitality_Epic"),
                  SUI.J(PKG + ".AccDefs.pretty(s[i])", "Legendary Health Accessory"),
                  SUI.J(PKG + ".AccDefs.rarityName(s[i]).toUpperCase()", "LEGENDARY"),
                  SUI.J(PKG + ".AccDefs.rarityColor(s[i])", _Q))
ACC_FULL_JAVA = _acc_java(_ap, "      ", known=[_SLOT])
_ap = SUI.Appends()
acc_page_row_empty(_ap, _SLOT)
ACC_EMPTY_JAVA = _acc_java(_ap, "      ", known=[_SLOT])
ACC_NONE_JAVA = SUI.java_append("SkyyAccInvRows", acc_page_none())
_ap = SUI.Appends()
acc_page_row_box(_ap, "SkyyAccInvRows", _INV)
acc_page_row_full(_ap, _INV, "SkyyAccEq" + _I, "Equip", SUI.J("safe(id)", "Skyy_Accessory_Workbench_T2"),
                  SUI.J(PKG + ".AccDefs.pretty(id)", "Workbench II"),
                  SUI.J(PKG + ".AccDefs.rarityName(id).toUpperCase()", "UNIQUE"),
                  SUI.J(PKG + ".AccDefs.rarityColor(id)", SUI.RARITY["Unique"]))
ACC_INV_JAVA = _acc_java(_ap, "    ", known=["SkyyAccInvRows"])
# build-time check of whole sample states: a full page of slots + 9 inventory rows, an empty bag with nothing carried, a middle page
_full = ("Skyy_Talisman_Speed_Epic", "Legendary Speed Accessory", "LEGENDARY", SUI.RARITY["Legendary"])
_invr = ("Skyy_Accessory_Furnace_T1", "Furnace", "NORMAL", SUI.RARITY["Normal"])
_bon = [("Health", "+24 max Health"), ("Stamina", "+12 max Stamina, +10% Stamina Regen"), ("Mana", "+24% max Mana (at least +4)"),
        ("Regeneration", "Heals 1% max Health every 2 s"), ("Speed", "+10% Speed"), ("Brawler", "+12 Strength"),
        ("Runic", "+12 Magical Power"), ("Stonehide", "switched off"), ("Razorfang", "+8% Crit Chance, +16% Crit Damage"),
        ("Feather", "-40% fall damage, +20% jump height"), ("Combat stats", "need SkyyGear, which is not running"),
        ("Fall damage", "needs SkyySkills, which is not running")]
_nobon = [("", "")] * BONUS_MAX
assert len(_bon) == BONUS_MAX
for _acc_st in (acc_page_state("Bonuses - your best accessory of each line counts", _bon, "", "Bag slots - 9 of 18 used",
                               ("Page 1 / 2", False, True), ("Page 1 / 2", False, True),
                               [(i, _full) for i in range(PAGE_ROWS)], [(i, _invr) for i in range(PAGE_ROWS)], 12),
                acc_page_state("Bonuses - none yet - put accessories in this bag", _nobon, "", "Bag slots - 0 of 18 used",
                               ("Page 1 / 2", False, True), ("Page 1 / 1", False, False), [(i, None) for i in range(PAGE_ROWS)], [], 0),
                acc_page_state("Bonuses - none yet", _nobon, "bag is full, or the same or a better Speed Accessory is already equipped",
                               "Bag slots - 3 of 60 used", ("Page 4 / 7", True, True), ("Page 2 / 2", True, False),
                               [(27, _full), (28, None), (35, _full)], [(9, _invr)], 10)):
    acc_page_check(_acc_st)
print("accessory page: %d x %d on %s, %d static appends + row templates checked (%d rows a page, pagers under both lists)" % (
    ACC_W, ACC_H, KIT_ID, len(ACC_SH.appends), PAGE_ROWS))
# ---- ACC PAGE BLOCK END
ACC_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  this.key = {PKG}.AccStore.pkey(u);   // 0.4.1
  String[] s = {PKG}.AccStore.snapshot(u);
  int cap = {PKG}.AccStore.capOf(s);   // 0.4.4
  // 0.5: the slots this page lists (a slot above this server's limit only while something is still in it), {PAGE_ROWS} a page
  int[] shown = new int[s.length];
  int ns = 0;
  int used = 0;
  for (int i = 0; i < s.length; i++) {{
    if (s[i] != null) used++;
    if (i >= cap && s[i] == null) continue;
    shown[ns] = i;
    ns++;
  }}
  int slotPages = (ns + {PAGE_ROWS} - 1) / {PAGE_ROWS};
  if (slotPages < 1) slotPages = 1;
  if (this.slotPage >= slotPages) this.slotPage = slotPages - 1;
  if (this.slotPage < 0) this.slotPage = 0;
  String slotsHead = "Bag slots - " + used + " of " + cap + " used";
  String slotCaption = "Page " + (this.slotPage + 1) + " / " + slotPages;
  java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);
  this.invIds = new String[inv.size()];
  for (int i = 0; i < inv.size(); i++) this.invIds[i] = (String) inv.get(i);
  int invPages = (inv.size() + {PAGE_ROWS} - 1) / {PAGE_ROWS};
  if (invPages < 1) invPages = 1;
  if (this.invPage >= invPages) this.invPage = invPages - 1;
  if (this.invPage < 0) this.invPage = 0;
  String invCaption = "Page " + (this.invPage + 1) + " / " + invPages;
  String[] bl = {PKG}.AccGear.pageRows(s, u);   // 0.5 part 2: one key / value row per line + the SkyyGear / SkyySkills notes
  // the window, the top well (hint, bonuses), the two list wells (heads, row groups, pagers), the separator and the result line
{ACC_TOP_JAVA}
  for (int q = 0; q < {PAGE_ROWS}; q++) {{
    int k = this.slotPage * {PAGE_ROWS} + q;
    if (k >= ns) break;
    int i = shown[k];
{ACC_SLOT_JAVA}
    if (s[i] != null) {{
{ACC_FULL_JAVA}
      ev.addEventBinding({BT}.Activating, "#SkyyAccUn" + i, {EVD}.of("a", "un:" + i));
    }} else {{
{ACC_EMPTY_JAVA}
    }}
  }}
  if (inv.isEmpty()) {ACC_NONE_JAVA}
  for (int q = 0; q < {PAGE_ROWS}; q++) {{
    int i = this.invPage * {PAGE_ROWS} + q;
    if (i >= inv.size()) break;
    String id = (String) inv.get(i);
{ACC_INV_JAVA}
    ev.addEventBinding({BT}.Activating, "#SkyyAccEq" + i, {EVD}.of("a", "eq:" + i));
  }}
  ev.addEventBinding({BT}.Activating, "#SkyyAccSpPrev", {EVD}.of("a", "sp:prev"));
  ev.addEventBinding({BT}.Activating, "#SkyyAccSpNext", {EVD}.of("a", "sp:next"));
  ev.addEventBinding({BT}.Activating, "#SkyyAccIpPrev", {EVD}.of("a", "ip:prev"));
  ev.addEventBinding({BT}.Activating, "#SkyyAccIpNext", {EVD}.of("a", "ip:next"));
}}"""
for _piece in (ACC_TOP_JAVA, ACC_SLOT_JAVA, ACC_FULL_JAVA, ACC_EMPTY_JAVA, ACC_NONE_JAVA, ACC_INV_JAVA):
    assert _piece in ACC_BUILD_SRC, "kit Java changed on its way into the build() source"   # the f-string pilot: verbatim
assert ACC_BUILD_SRC.count("infoColor(this.info)") == 1 and ACC_BUILD_SRC.count("safe(") == 2, "infoColor once; safe() on the 2 ItemIds only"
page.addMethod(CtNewMethod.make(ACC_INFO_COLOR_SRC, page))   # before build() (javassist: methods before their callers)
page.addMethod(CtNewMethod.make(ACC_BUILD_SRC, page))
# giveBack: 0 = back in the inventory, 1 = kept in a free bag slot, 2 = lost (logged with the player's uuid so an admin can give it back)
page.addMethod(CtNewMethod.make(f"""
public static int giveBack({PLA} p, java.util.UUID u, String k, String id) {{
  if (giveOne(p, id)) return 0;
  if ({PKG}.AccStore.stashK(u, k, id)) return 1;   // integration pass: the bag of the click's key k
  {PKG}.AccStore.warn("ITEM LOST - could not return " + id + " to player " + u + " (inventory and accessory bag full), give it back by hand");
  return 2;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    // 0.5: the two pagers move nothing (build() clamps the page numbers)
    if (data.indexOf("sp:prev\\"") >= 0) {{ if (this.slotPage > 0) this.slotPage = this.slotPage - 1; rebuild(); return; }}
    if (data.indexOf("sp:next\\"") >= 0) {{ this.slotPage = this.slotPage + 1; rebuild(); return; }}
    if (data.indexOf("ip:prev\\"") >= 0) {{ if (this.invPage > 0) this.invPage = this.invPage - 1; rebuild(); return; }}
    if (data.indexOf("ip:next\\"") >= 0) {{ this.invPage = this.invPage + 1; rebuild(); return; }}
    String k = {PKG}.AccStore.pkey(u);   // integration pass: ONE storage key for everything this click does (semantics rule 1)
    if (this.key != null && !this.key.equals(k)) {{   // 0.4.1: profile switched since this page was drawn
      this.info = "your profile changed - this is the bag of your current profile now";
      this.slotPage = 0;
      this.invPage = 0;
      rebuild(); return;
    }}
    String blk = {PKG}.AccStore.moveBlock(u);   // integration pass: profile:busy / unknown profile state -> move nothing
    if (blk != null) {{ this.info = blk; rebuild(); return; }}
    {PKG}.AccStore.slotsK(u, k);   // 0.5: load the bag first, so a file that cannot be read is known before anything moves
    if ({PKG}.AccStore.isBad(k)) {{ this.info = "your accessory bag file could not be read - nothing was moved, tell an admin (server log)"; rebuild(); return; }}
    for (int i = 0; i < {PKG}.AccStore.CAP; i++) {{
      if (data.indexOf("un:" + i + "\\"") < 0) continue;
      String id = {PKG}.AccStore.unequipK(u, k, i);
      if (id == null) return;
      String give = {PKG}.AccDefs.modernOf(id);   // 0.4 / 0.5: an old id comes back as the current (upgradable) item
      if (!giveOne(player, give)) {{ {PKG}.AccStore.putK(u, k, i, id); this.info = "your inventory is full"; }}
      else this.info = "unequipped " + {PKG}.AccDefs.pretty(give) + (give.equals(id) ? "" : " - your older copy came back as the current item");
      rebuild(); return;
    }}
    int ni = this.invIds == null ? 0 : this.invIds.length;
    for (int i = 0; i < ni; i++) {{
      if (data.indexOf("eq:" + i + "\\"") < 0) continue;
      if (this.invIds[i] == null) return;
      String id = this.invIds[i];
      if ({PKG}.AccDefs.isRetired(id)) {{   // 0.4.2: retired - refused with the reason, nothing is moved
        this.info = {PKG}.AccDefs.retiredWhy(id);
        try {{ this.playerRef.sendMessage({MSG}.raw("[Accessories] " + {PKG}.AccDefs.retiredChat(id))); }} catch (Throwable t2) {{ }}
        rebuild(); return;
      }}
      String put = {PKG}.AccDefs.modernOf(id);   // 0.4 / 0.5: an old id is stored as its current id
      String why = "bag is full, or the same or a better " + {PKG}.AccDefs.lineLabel(id) + " is already equipped";
      if (!{PKG}.AccStore.canEquipK(u, k, put)) {{ this.info = why; rebuild(); return; }}
      if (!takeOne(player, id)) {{ this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }}
      String res = {PKG}.AccStore.equipK(u, k, put);
      if (res == null) {{
        int g = giveBack(player, u, k, id);
        this.info = g == 0 ? why : (g == 1 ? why + " - it was kept in a free bag slot" : "could not give " + {PKG}.AccDefs.pretty(id) + " back - inventory and bag full, reported to the server log");
        rebuild(); return;
      }}
      if (res.length() > 0) {{
        res = {PKG}.AccDefs.modernOf(res);
        int g = giveBack(player, u, k, res);
        String old = {PKG}.AccDefs.pretty(res);
        this.info = "upgraded to " + {PKG}.AccDefs.pretty(id) + " - " + (g == 0 ? old + " returned" : (g == 1 ? old + " kept in the bag - inventory full" : old + " could not be returned - reported to the server log"));
      }}
      else this.info = "equipped " + {PKG}.AccDefs.pretty(put) + (put.equals(id) ? "" : " - converted from an older copy");
      rebuild(); return;
    }}
  }} catch (Throwable t) {{ {PKG}.AccStore.warn("bag page event failed: " + t); }}
}}""", page))

fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public AccPageFactory() { }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.AccPage(({PR}) o);
}}""", fac))

# ================= 0.5 admin give helpers (AccAdmin), the delivery task (AccGiveTask), acc:fn:give (AccGiveFn) =================
JM(adm, r"""
public static void msg(@PR@ pr, String t) {
  if (pr == null) return;
  try { pr.sendMessage(@MSG@.raw("[Accessories] " + t)); } catch (Throwable e) { }
}""")
# the words after the sub-command word ("accessories give Skyy Skyy_Talisman_Speed_Epic 2" -> "Skyy Skyy_Talisman_Speed_Epic 2"; SkyyGear's rest)
JM(adm, r"""
public static String rest(@CTX@ ctx, String word) {
  String line = "";
  try { line = ctx.getInputString(); } catch (Throwable t) { line = ""; }
  if (line == null) return "";
  String[] tk = line.trim().split("\\s+");
  StringBuilder sb = new StringBuilder();
  boolean seen = false;
  for (int i = 0; i < tk.length; i++) {
    if (!seen) { if (tk[i].equalsIgnoreCase(word) || tk[i].equalsIgnoreCase("/" + word)) seen = true; continue; }
    if (sb.length() > 0) sb.append(' ');
    sb.append(tk[i]);
  }
  return sb.toString().trim();
}""")
JM(adm, r"""
public static @PR@ findPlayer(String name) {
  if (name == null) return null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(name.trim())) return (@PR@) o;
    }
  } catch (Throwable t) { }
  return null;
}""")
JM(adm, r"""
public static int amountOf(String t) {
  try {
    int n = Integer.parseInt(t.trim());
    return n >= 1 && n <= 64 ? n : -1;
  } catch (Throwable e) { return -1; }
}""")
# which ids /accessories give takes: the booster table ids, the active bench accessories (up to their top tier), the Omni and the bag
# item; never an old (legacy) id or a retired accessory. null = fine, else the reason (no ids in it: admins see ids via /accessories lines)
JM(adm, r"""
public static String giveable(String id) {
  if (id == null || id.length() == 0) return "no item id given";
  if (@PKG@.AccDefs.isBoosterId(id)) return null;
  if (@PKG@.AccDefs.BAG.equals(id) || @PKG@.AccDefs.OMNI.equals(id)) return null;
  if (@PKG@.AccDefs.isLegacy(id)) return "that is an old id - give its current id instead (/accessories lines shows them)";
  if (@PKG@.AccDefs.isRetired(id)) return "that accessory is retired and does nothing";
  String bn = @PKG@.AccDefs.benchOf(id);
  if (bn != null && !@PKG@.AccDefs.isTalisman(id)) {
    int t = @PKG@.AccDefs.tierOf(id);
    for (int i = 0; i < @PKG@.AccDefs.BENCH_IDS.length; i++) {
      if (@PKG@.AccDefs.BENCH_IDS[i].equals(bn) && t >= 1 && t <= @PKG@.AccDefs.BENCH_MAX[i] && id.equals("Skyy_Accessory_" + bn + "_T" + t)) return null;
    }
  }
  return "not an accessory of this mod - /accessories lines lists the stat accessory ids";
}""")
gtk.addInterface(pool.get("java.lang.Runnable"))
JF(gtk, "public @PR@ admin;")
JF(gtk, "public @PR@ target;")
JF(gtk, "public String id;")
JF(gtk, "public int n;")
JF(gtk, "public boolean onWorld;")
JF(gtk, "public boolean queued;")
gtk.addConstructor(CtNewConstructor.make(JT("public AccGiveTask(@PR@ admin, @PR@ target, String id, int n) { this.admin = admin; this.target = target; this.id = id; this.n = n; this.onWorld = false; this.queued = false; }"), gtk))
# first run: hop to the TARGET player's world (any thread); second run, on that world thread: refuse while the profile loads, deliver,
# tell the admin (and the player), log one INFO line. admin == null = acc:fn:give called off the world thread. queued = true once
# world.execute accepted the second run (acc:fn:give then returns -1, part 2 review finding 2).
JM(gtk, r"""
public void run() {
  try {
    if (this.target == null || !this.target.isValid()) { @PKG@.AccAdmin.msg(this.admin, "that player left"); return; }
    if (!this.onWorld) {
      java.util.UUID wu = this.target.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.AccAdmin.msg(this.admin, "that player's world is not loaded - try again"); return; }
      this.onWorld = true;
      w.execute(this);
      this.queued = true;
      return;
    }
    String nm = this.target.getUsername();
    if (@PKG@.AccStore.moveBlock(this.target.getUuid()) != null) { @PKG@.AccAdmin.msg(this.admin, nm + "'s profile is loading - nothing was given, try again in a moment"); return; }
    int[] g = @PKG@.AccStore.deliver(this.target, this.id, this.n);
    if (g == null) { @PKG@.AccAdmin.msg(this.admin, "could not reach " + nm + "'s inventory - nothing was given, try again"); return; }
    String item = @PKG@.AccDefs.pretty(this.id);
    @PKG@.AccAdmin.msg(this.admin, "Gave " + g[0] + " x " + item + " to " + nm + (g[2] > 0 ? " (" + g[2] + " dropped at their feet - inventory full)" : ""));
    if (this.admin == null || !this.admin.getUuid().equals(this.target.getUuid())) @PKG@.AccAdmin.msg(this.target, "You got " + g[0] + " x " + item + (g[2] > 0 ? " (" + g[2] + " dropped at your feet - inventory full)" : ""));
    @PKG@.AccCfg.info("give: " + (this.admin == null ? "acc:fn:give" : this.admin.getUsername()) + " gave " + g[0] + " x " + this.id + " to " + nm + " (" + g[1] + " in the inventory, " + g[2] + " dropped)");
  } catch (Throwable t) {
    @PKG@.AccStore.warn("give failed: " + t);
    @PKG@.AccAdmin.msg(this.admin, "give failed - see the server log");
  }
}""")
JM(adm, r"""
public static void giveCmd(@PR@ pr, String rest, boolean byTier) {
  String[] tk = rest == null || rest.trim().length() == 0 ? new String[0] : rest.trim().split("\\s+");
  String id = null;
  int n = 1;
  if (!byTier) {
    if (tk.length < 2 || tk.length > 3) { msg(pr, "usage: /accessories give <player> <item id> [amount 1-64]"); return; }
    id = tk[1];
    if (tk.length == 3) n = amountOf(tk[2]);
  } else {
    if (tk.length < 3 || tk.length > 4) { msg(pr, "usage: /accessories givetier <player> <line> <rarity> [amount 1-64]"); return; }
    int li = @PKG@.AccDefs.lineOf(tk[1]);
    if (li < 0) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < @PKG@.AccDefs.LINE_ADMIN.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.LINE_ADMIN[i]); }
      msg(pr, "unknown line - use one of: " + sb.toString());
      return;
    }
    int t = @PKG@.AccDefs.rarityIndex(tk[2]);
    if (t < 1) { msg(pr, "unknown rarity - use Normal, Unique, Rare, Legendary or 1 to 4"); return; }
    id = @PKG@.AccDefs.idOf(li, t);
    if (tk.length == 4) n = amountOf(tk[3]);
  }
  if (n < 1) { msg(pr, "the amount must be a whole number from 1 to 64"); return; }
  String why = giveable(id);
  if (why != null) { msg(pr, why); return; }
  @PR@ target = findPlayer(tk[0]);
  if (target == null) { msg(pr, "no online player called " + tk[0]); return; }
  new @PKG@.AccGiveTask(pr, target, id, n).run();
}""")
# acc:fn:give (spec 5.9) for the later loot pass: booster table ids only; on the player's world thread it delivers at once and returns how
# many were handed out (counted before and after); from any other thread it hops to that world and logs one line.
# THE RESULT (part 2 review finding 2 - the spec's "returns 0" off the thread made a retry-on-0 caller give twice):
#   n > 0 = given now (counted), 0 = NOTHING given and nothing queued (bad id / amount, player offline, profile loading, inventory not
#   reachable, the player's world not loaded), -1 = QUEUED: the give runs later on the player's world thread and its outcome is only
#   logged (it can still give nothing if the player leaves first). A caller must never retry on -1.
JM(adm, r"""
public static int giveFn(java.util.UUID u, String id, int n) {
  if (u == null || !@PKG@.AccDefs.isBoosterId(id) || n < 1 || n > 64) return 0;
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t) { pr = null; }
  if (pr == null || !pr.isValid()) return 0;
  @REF@ r = pr.getReference();
  @ST@ st = r == null ? null : r.getStore();
  if (st != null && st.isInThread()) {
    if (@PKG@.AccStore.moveBlock(u) != null) return 0;
    int[] g = @PKG@.AccStore.deliver(pr, id, n);
    if (g == null) return 0;
    @PKG@.AccCfg.info("give: acc:fn:give gave " + g[0] + " x " + id + " to " + pr.getUsername() + " (" + g[1] + " in the inventory, " + g[2] + " dropped)");
    return g[0];
  }
  @PKG@.AccGiveTask gt = new @PKG@.AccGiveTask(null, pr, id, n);
  gt.run();
  if (!gt.queued) { @PKG@.AccStore.warn("acc:fn:give was called off " + pr.getUsername() + "'s world thread and could not reach that world - nothing was given, the call returns 0"); return 0; }
  @PKG@.AccStore.warn("acc:fn:give was called off " + pr.getUsername() + "'s world thread - the give runs later on that thread and the call returns -1 (queued: do not retry)");
  return -1;
}""")
gfn.addInterface(pool.get("java.util.function.Function"))
gfn.addConstructor(CtNewConstructor.make("public AccGiveFn() { }", gfn))
JM(gfn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return Integer.valueOf(0);
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String) || !(a[2] instanceof Number)) return Integer.valueOf(0);
    return Integer.valueOf(@PKG@.AccAdmin.giveFn((java.util.UUID) a[0], (String) a[1], ((Number) a[2]).intValue()));
  } catch (Throwable t) { @PKG@.AccStore.warn("acc:fn:give failed: " + t); return Integer.valueOf(0); }
}""")

# ================= 0.5 AccNotice: the one-time chat line (spec 5.1) =================
# Checked by the effect tick (world thread, the player is ready) once per player per session (ASKED, forgotten when they leave): a
# player with a bag file from before (bags/<uuid>.properties or bags/<uuid>-p<N>.properties) gets MIG_NOTICE once, ever (unless
# notice.boosters is off: then nothing is looked at or recorded - no directory scan - so switching it on later still tells them); a
# player without one is recorded as new and never gets it. Seen players live in
# Skyy_SkyyAccessories/notices.properties, saved by AccTick (never the world thread), tmp + fsync + move. An unreadable file is left
# alone and the notice is remembered for this session only.
JF(note, "public static java.nio.file.Path FILE;")
JF(note, "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();")
JF(note, "public static final java.util.concurrent.ConcurrentHashMap ASKED = new java.util.concurrent.ConcurrentHashMap();")
JF(note, "public static volatile boolean DIRTY = false;")
JF(note, "public static boolean BROKEN = false;")
JF(note, "public static boolean SAVEWARNED = false;")
note.addField(CtField.make("public static final String TEXT = %s;" % jlit(MIG_NOTICE), note))
JM(note, r"""
public static void load() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); SEEN.put(k, p.getProperty(k)); }
  } catch (Throwable t) {
    BROKEN = true;
    @PKG@.AccStore.warn("could not read " + FILE + " - the 0.5 notice is remembered for this session only (the file is left untouched): " + t);
  }
}""")
JM(note, r"""
public static boolean hasOldBag(java.util.UUID u) {
  try {
    java.nio.file.Path d = @PKG@.AccStore.DIR;
    if (d == null || !java.nio.file.Files.exists(d, new java.nio.file.LinkOption[0])) return false;
    if (java.nio.file.Files.exists(d.resolve(u.toString() + ".properties"), new java.nio.file.LinkOption[0])) return true;
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(d, u.toString() + "-p*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        String nm = String.valueOf(((java.nio.file.Path) it.next()).getFileName());
        if (!nm.endsWith(".more.properties")) return true;
      }
    } finally { ds.close(); }
  } catch (Throwable t) { }
  return false;
}""")
JM(note, r"""
public static void check(@PR@ pr, java.util.UUID u) {
  if (u == null || pr == null) return;
  String us = u.toString();
  if (SEEN.containsKey(us) || ASKED.containsKey(u)) return;
  if (!@PKG@.AccDefs.NOTICE) return;   // part 1 review finding 3: switched off = nothing looked at or remembered, so switching it on still tells them
  ASKED.put(u, Boolean.TRUE);          // (forgotten when the player leaves: AccTick)
  if (!hasOldBag(u)) { SEEN.put(us, "new"); if (!BROKEN) DIRTY = true; return; }
  SEEN.put(us, "boosters-0.5");
  if (!BROKEN) DIRTY = true;
  pr.sendMessage(@MSG@.raw(TEXT).color("@INFOCOL@"));
}""".replace("@INFOCOL@", SUI.STATUS["="]))
JM(note, r"""
public static synchronized void save() {
  if (!DIRTY || BROKEN || FILE == null) return;
  DIRTY = false;
  try {
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = SEEN.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty((String) e.getKey(), String.valueOf(e.getValue())); }
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyyAccessories one-time notices per player (uuid=boosters-0.5 told / new = joined without accessories)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  } catch (Throwable t) {
    DIRTY = true;
    if (!SAVEWARNED) { SAVEWARNED = true; @PKG@.AccStore.warn("could not save " + FILE + " (retried by the next save): " + t); }
  }
}""")

# ================= 0.5 AccRestampTask: the quality restamp on one player's world thread (dispatched by AccTick every 5 s) =================
rtk.addInterface(pool.get("java.lang.Runnable"))
JF(rtk, "public @PR@ pr;")
JF(rtk, "public java.util.UUID expectedWorld;")
JF(rtk, "public static boolean FAILED = false;")
JF(rtk, "public static volatile long STAMPED = 0L;")
rtk.addConstructor(CtNewConstructor.make(JT("public AccRestampTask(@PR@ pr, java.util.UUID w) { this.pr = pr; this.expectedWorld = w; }"), rtk))
JM(rtk, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID nowWorld = this.pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    if (@PKG@.AccStore.moveBlock(this.pr.getUuid()) != null) return;   // the live inventory may not be the active profile's yet
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    int n = @PKG@.AccStore.restamp(p.getInventory());
    if (n > 0) {   // part 1 review note: admins can see that the restamp ran (one line per player per restamp that changed stacks)
      STAMPED = STAMPED + (long) n;
      @PKG@.AccCfg.info("restamp: " + n + " accessory stack(s) of " + this.pr.getUsername() + " moved to the 0.5 rarity look (" + STAMPED + " since the start)");
    }
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("accessory rarity restamp failed (logged once): " + t); }
  }
}""")

# ================= /accessories reload (0.4.4, server admins only) =================
# COMMAND RULES: an admin sub-command under a player command needs requirePermission AND setPermissionGroups(new String[0]) - otherwise
# the engine copies skyyaccessories.admin into /accessories' hytale:Adventurer group (the SkyyIslands 0.5 leak; lint perm_group_leaks).
# The kit's reload op re-checks the node too (denied), reads the file on this thread and the save task runs AccCfg.reload.
rcmd.addConstructor(CtNewConstructor.make("""
public AccReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyAccessories/config.properties after hand edits");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
}""", rcmd))
rcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "reload", pr.getUuid(), pr.getUsername(), "command" }});
    String m = "could not reload - see the server log";
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) m = String.valueOf(((Object[]) o)[2]);
    pr.sendMessage({MSG}.raw("[Accessories] " + m));
  }} catch (Throwable t) {{
    {PKG}.AccStore.warn("/accessories reload failed: " + t);
    pr.sendMessage({MSG}.raw("[Accessories] could not reload - see the server log"));
  }}
}}""", rcmd))

# ================= /accessories lines (0.5, every player) =================
lcmd.addConstructor(CtNewConstructor.make("""
public AccLinesCmd() {
  super("lines", "Show every accessory line, its rarities and this server's numbers");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""", lcmd))
JM(lcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    boolean admin = false;
    try { admin = pr.hasPermission("skyyaccessories.admin"); } catch (Throwable t0) { admin = false; }
    pr.sendMessage(@MSG@.raw("[Accessories] Accessory lines on this server - only your best accessory of each line counts, and every line stops at Legendary:"));
    String[] ls = @PKG@.AccDefs.linesText(admin);
    for (int i = 0; i < ls.length; i++) pr.sendMessage(@MSG@.raw("  " + ls[i]));
  } catch (Throwable t) {
    @PKG@.AccStore.warn("/accessories lines failed: " + t);
    pr.sendMessage(@MSG@.raw("[Accessories] could not list the lines - see the server log"));
  }
}""")
# ================= /accessories give | givetier (0.5, server admins only) =================
# COMMAND RULES: an admin sub-command under a player command needs requirePermission AND setPermissionGroups(new String[0]) (lint
# perm_group_leaks). The arguments are read from the raw command text (setAllowsExtraArguments, SkyyGear's /gear give way), so there is
# no usage variant and [amount] is simply an optional last word.
gcmd.addConstructor(CtNewConstructor.make("""
public AccGiveCmd() {
  super("give", "(admin) Give an accessory: /accessories give <player> <item id> [amount]");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""", gcmd))
JM(gcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.AccAdmin.giveCmd(pr, @PKG@.AccAdmin.rest(ctx, "give"), false); }
  catch (Throwable t) { @PKG@.AccStore.warn("/accessories give failed: " + t); @PKG@.AccAdmin.msg(pr, "give failed - see the server log"); }
}""")
tcmd.addConstructor(CtNewConstructor.make("""
public AccGiveTierCmd() {
  super("givetier", "(admin) Give by line and rarity: /accessories givetier <player> <line> <rarity> [amount]");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""", tcmd))
JM(tcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.AccAdmin.giveCmd(pr, @PKG@.AccAdmin.rest(ctx, "givetier"), true); }
  catch (Throwable t) { @PKG@.AccStore.warn("/accessories givetier failed: " + t); @PKG@.AccAdmin.msg(pr, "give failed - see the server log"); }
}""")

# ================= /accessories =================
cmd.addConstructor(CtNewConstructor.make("""
public AccCmd() {
  super("accessories", "Open your accessory bag");
  addAliases(new String[] { "acc", "accbag" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });   // 0.4: COMMAND RULES - ordinary players lack the auto node
  addSubCommand(new com.skyy.accessories.AccReloadCmd());   // 0.4.4: server admins only (its own groups are cleared)
  addSubCommand(new com.skyy.accessories.AccLinesCmd());    // 0.5: every player (its own hytale:Adventurer group)
  addSubCommand(new com.skyy.accessories.AccGiveCmd());     // 0.5: server admins only (its own groups are cleared)
  addSubCommand(new com.skyy.accessories.AccGiveTierCmd()); // 0.5: server admins only (its own groups are cleared)
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.AccPage(pr));
  }} catch (Throwable t) {{
    {PKG}.AccStore.warn("/accessories failed: " + t);
    pr.sendMessage({MSG}.raw("[Accessories] could not open the bag"));
  }}
}}""", cmd))

tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public AccTick() { }", tick))
# 0.4.3 review fix: campCheck; 0.5: the notices file (never saved on a world thread) and one AccRestampTask per online player on its world;
# 0.5 part 2: every player who left loses our gear:extra text and movement entry (AccGear.prune) and the notice's once-a-session mark
JF(tick, "public static boolean PRUNE_WARNED = false;")
JM(tick, r"""
public void run() {
  @PKG@.AccStore.publishOnline();
  @PKG@.AccStore.campCheck();
  try { @PKG@.AccNotice.save(); } catch (Throwable t) { }
  java.util.HashSet online = new java.util.HashSet();
  boolean listed = false;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      online.add(pr.getUuid());
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new @PKG@.AccRestampTask(pr, wu));
    }
    listed = true;
  } catch (Throwable t) { }
  if (!listed) return;   // never prune from a player list that could not be read
  try {
    @PKG@.AccGear.prune(online);
    @PKG@.AccNotice.ASKED.keySet().retainAll(online);
  } catch (Throwable t) {
    if (!PRUNE_WARNED) { PRUNE_WARNED = true; @PKG@.AccStore.warn("removing the bridge keys of players who left failed (logged once): " + t); }
  }
}""")

# ================= MoveSync: the shared Skyy movement protocol (tools/skyymove.py; identical code in SkyySkills 0.2) =================
MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".AccStore.warn")

# ================= AccEffects: accessory stats (EntityTickingSystem on Player entities, runs on each world's thread) =================
# Pattern copied from TerrariaAddons 1.7.4 (DivingHelmetSystem: putModifier/removeModifier with a StaticModifier under a fixed key;
# BandOfRegenerationSystem: addStatValue(DefaultEntityStatTypes.getHealth(), n); speed through the Skyy movement protocol). Work is
# throttled to once per second per player. 0.5: the numbers come from the booster table (AccDefs.BOOST, live config), a switched-off
# line counts for nothing, and every publisher has its own try + log-once flag (spec 5.4), so one failing part never stops the others.
eff.addConstructor(CtNewConstructor.make("public AccEffects() { super(); }", eff))
eff.addField(CtField.make("public static boolean FAILED_ONCE = false;", eff))
eff.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", eff))
# 0.4 PERCENT LAYER. Verified in HytaleServer.jar bytecode (EntityStatValue.computeModifiers): max = EntityStatType.max, then
# max + SUM(ADDITIVE MAX amounts), then max * SUM(MULTIPLICATIVE MAX amounts). MULTIPLICATIVE amounts are summed, so ours (1.10) next
# to vanilla's Meat_Buff (1.05) would give x2.15 - not usable. Instead: flat = type max + every OTHER additive MAX modifier (armour,
# SkyySkills, food boosts), ours = ADDITIVE round(flat x pct / 100, 2 decimals) under the 0.2/0.3 key (overwrites the flat value
# those versions saved with the player). A vanilla multiplicative buff then scales flat + ours = flat x (1 + pct) x buff.
eff.addMethod(CtNewMethod.make(f"""
public static float flatMax({ESV} v, int idx, String key) {{
  float base = 0.0f;
  try {{
    {EST} t = ({EST}) {EST}.getAssetMap().getAsset(idx);
    if (t != null) base = t.getMax();
  }} catch (Throwable e) {{ }}
  java.util.Map mods = v.getModifiers();
  if (mods == null) return base;
  java.util.Iterator it = mods.keySet().iterator();
  while (it.hasNext()) {{
    Object k = it.next();
    if (key.equals(k)) continue;
    Object o = mods.get(k);
    if (!(o instanceof {SMO})) continue;
    {SMO} sm = ({SMO}) o;
    if (sm.getTarget() != {MTG}.MAX || sm.getCalculationType() != {CAL}.ADDITIVE) continue;
    base = base + sm.getAmount();
  }}
  return base;
}}""", eff))
# 0.5: set (amt > 0) or remove (amt <= 0) our MAX modifier on one stat, ADDITIVE (never MULTIPLICATIVE: the engine sums every
# multiplicative amount into one factor); only writes when something changes. Throws to the caller's publisher try.
# Never removed on leave or shutdown (as in 0.4.5 and SkyySkills): the modifier is saved with the character, a relog keeps it and the
# next tick corrects it. DEPLOY NOTE (part 2 review finding 3): removing or disabling the mod leaves the last flat bonus on saved
# characters until a later admin cleanup command removes skyyacc_health / skyyacc_stamina / skyyacc_mana.
JM(eff, r"""
public static void modAmt(@ESM@ m, int idx, String key, float amt) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;   // getModifier/putModifier would log "No EntityStatValue found" every second
  @MOD@ cur = m.getModifier(idx, key);
  if (amt <= 0.0f) { if (cur != null) m.removeModifier(idx, key); return; }
  @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, amt);
  if (cur != null && cur.equals(want)) return;
  m.putModifier(idx, key, want);
}""")
# 0.5 Mana: pct of the FLAT max Mana (flatMax: the type max + every other ADDITIVE MAX modifier, ours left out), never less than floor
JM(eff, r"""
public static void manaMod(@ESM@ m, int idx, String key, float pct, float floor) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;
  float amt = 0.0f;
  if (pct > 0.0f) amt = Math.round(flatMax(v, idx, key) * pct) / 100.0f;
  if (floor > amt) amt = floor;
  modAmt(m, idx, key, amt);
}""")
# 0.5 STAMINA REGEN (spec 5.4.1; every call read in HytaleServer.jar bytecode and B.probe'd): the rate vanilla is refilling at RIGHT NOW
# = the sum of amount / interval over the Stamina value's positive ADDITIVE regen entries whose conditions pass
# Condition.allConditionsMet(cb, ref, now, rg) - exactly the check RegeneratingValue.shouldRegenerate makes after its timer step (we
# never call shouldRegenerate / regenerate: they advance the engine's own regen timer); the clock is the store's TimeResource, like
# EntityStatsSystems$Regenerate. The top-up = rate x pct / 100 x the seconds since the last 1 s tick (clamped 0..2), capped at max,
# skipped for a dead player or a full bar, added with addStatValue like the engine. Sprinting / gliding / blocking / the empty-bar pause
# fail those conditions, so the bonus never flows then (sampled once a second: at most one second's bonus either way).
# The rate is the Stamina asset's own ADDITIVE regen entries only (part 2 review finding 4): RegeneratingModifier multipliers and
# armor regen entries are not in it, so "X% faster" and any quoted refill time hold for the vanilla numbers.
JM(eff, r"""
public static void staminaRegen(@ST@ store, @CB@ cb, @REF@ ref, @ESM@ m, float pct, float secs) {
  if (pct <= 0.0f) return;
  int si = @DST@.getStamina();
  if (si < 0) return;
  @ESV@ v = m.get(si);
  if (v == null) return;
  int hi = @DST@.getHealth();
  @ESV@ hv = hi < 0 ? null : m.get(hi);
  if (hv != null && hv.get() <= 0.0f) return;
  float cur = v.get();
  float max = v.getMax();
  if (cur >= max) return;
  @RGV@[] rv = v.getRegeneratingValues();
  if (rv == null || rv.length == 0) return;
  java.time.Instant now = ((@TMR@) store.getResource(@TMR@.getResourceType())).getNow();
  float rate = 0.0f;
  for (int i = 0; i < rv.length; i++) {
    if (rv[i] == null) continue;
    @RGN@ rg = rv[i].getRegenerating();
    if (rg == null || rg.getRegenType() != @RGT@.ADDITIVE) continue;
    float a = rg.getAmount();
    float iv = rg.getInterval();
    if (a <= 0.0f || iv <= 0.0f) continue;
    if (@CND@.allConditionsMet(cb, ref, now, rg)) rate = rate + a / iv;
  }
  if (rate <= 0.0f) return;
  float sec = secs;
  if (sec < 0.0f) sec = 0.0f;
  if (sec > 2.0f) sec = 2.0f;
  float amt = rate * pct / 100.0f * sec;
  if (cur + amt > max) amt = max - cur;
  if (amt > 0.0f) m.addStatValue(si, amt);
}""")
# Movement (0.3 Speed; 0.5 part 2 + Feather): the whole bag is ONE source "accessories.talismans" (layer pct) in the shared movement
# protocol (tools/skyymove.py) - speed 0.10 = +10 %, jump 0.20 = jump HEIGHT x 1.20, fallDamage -0.40 = 40 % less fall damage (the
# config stores the magnitude, the tick adds the minus); all zero removes the entry. MoveSync.sync applies the total of every source:
# baseSpeed = default x clamp((1 + sum flat) x (1 + sum pct), 0.3, 5), jumpForce from the summed jump height (clamped to h0 + 20
# blocks); fall damage is applied ONCE, by the mod holding stat:owner:fallDamage (SkyySkills 0.4.8: its fall filter multiplies by
# MoveSync.fallMultiplier(sums of every source)). Still baseSpeed only for speed (the direction multipliers are factors ON baseSpeed).
# The 0.2 back-off lives on in MoveSync; an unequip restores defaults only for a field still holding the value written. AccGear.MOVED
# remembers who has an entry, so AccTick removes it when they leave (AccGear.prune) and shutdown removes every one.
JM(eff, r"""
public static void move(java.util.UUID u, @PR@ pr, @CB@ cb, @REF@ ref, float speed, float jump, float fall) {
  @PKG@.MoveSync.post(u, @PKG@.AccGear.SOURCE, "pct", speed, jump, fall);
  if (speed != 0.0f || jump != 0.0f || fall != 0.0f) @PKG@.AccGear.MOVED.put(u, Boolean.TRUE);
  else @PKG@.AccGear.MOVED.remove(u);
  @PKG@.MoveSync.sync(u, pr, cb, ref, @PKG@.AccStore.SPEED, "SkyyAccessories");
}""")
# one log-once flag per publisher (spec 5.4; part 2 review finding 1: Health, Stamina and Mana had shared one pools flag, so a
# Health failure hid a later Stamina or Mana failure). F_STAM = the Stamina Regen top-up, F_STAMINA = the max Stamina modifier.
JF(eff, "public static boolean F_HEALTH = false;")
JF(eff, "public static boolean F_STAMINA = false;")
JF(eff, "public static boolean F_MANA = false;")
JF(eff, "public static boolean F_STAM = false;")
JF(eff, "public static boolean F_HEAL = false;")
JF(eff, "public static boolean F_MOVE = false;")
JF(eff, "public static boolean F_GEAR = false;")
JF(eff, "public static boolean F_NOTE = false;")
JM(eff, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  @REF@ ref = null;
  @PR@ pr = null;
  java.util.UUID u = null;
  float[] c = null;
  float secs = 0.0f;
  int[] best = null;
  @ESM@ m = null;
  try {
    ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    u = pr.getUuid();
    c = (float[]) @PKG@.AccStore.CLOCK.get(u);
    if (c == null) { c = new float[] { 1.0f, 0.0f }; @PKG@.AccStore.CLOCK.put(u, c); }
    c[0] = c[0] + dt;
    if (c[0] < 1.0f) return;
    secs = c[0];
    c[0] = 0.0f;
    @PKG@.AccStore.checkEpoch(u);   // 0.4.1: republish acc:has / acc:tal within a second of a profile switch
    best = @PKG@.AccDefs.bestTiers(@PKG@.AccStore.snapshot(u));   // 0.4.1: the ACTIVE profile's bag; only the best rarity of a line
    for (int li = 0; li < best.length; li++) if (!@PKG@.AccDefs.lineOn(li)) best[li] = 0;   // 0.5: a switched-off line counts for nothing
    m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AccStore.warn("accessory effects failed (logged once): " + t); }
    return;
  }
  float[] bo = @PKG@.AccDefs.BOOST;
  // 1. stat pools: max Health and max Stamina flat, max Mana a percent of the flat Mana with a floor (removed at 0)
  if (m != null) {
    try { modAmt(m, @DST@.getHealth(), "skyyacc_health", bo[@E_HF@ * 5 + best[@L_H@]]); }
    catch (Throwable t) { if (!F_HEALTH) { F_HEALTH = true; @PKG@.AccStore.warn("max Health from accessories failed (logged once): " + t); } }
    try { modAmt(m, @DST@.getStamina(), "skyyacc_stamina", bo[@E_SF@ * 5 + best[@L_S@]]); }
    catch (Throwable t) { if (!F_STAMINA) { F_STAMINA = true; @PKG@.AccStore.warn("max Stamina from accessories failed (logged once): " + t); } }
    try { manaMod(m, @DST@.getMana(), "skyyacc_mana", bo[@E_MP@ * 5 + best[@L_M@]], bo[@E_MF@ * 5 + best[@L_M@]]); }
    catch (Throwable t) { if (!F_MANA) { F_MANA = true; @PKG@.AccStore.warn("max Mana from accessories failed (logged once): " + t); } }
  }
  // 2. Stamina Regen top-up (only while vanilla's own refill flows)
  try { if (m != null && best[@L_S@] > 0) staminaRegen(store, cb, ref, m, bo[@E_SR@ * 5 + best[@L_S@]], secs); }
  catch (Throwable t) { if (!F_STAM) { F_STAM = true; @PKG@.AccStore.warn("Stamina Regen from accessories failed (logged once): " + t); } }
  // 3. Regeneration: a percent of the FULL current max Health every regenEverySeconds (the Health bar the item text names)
  try {
    int rt = best[@L_R@];
    if (m != null && rt > 0) {
      c[1] = c[1] + 1.0f;
      if (c[1] >= (float) @PKG@.AccDefs.REGEN_EVERY) {
        c[1] = 0.0f;
        int hi = @DST@.getHealth();
        @ESV@ hv = hi < 0 ? null : m.get(hi);
        if (hv != null) {
          float hnow = hv.get();
          float hmax = hv.getMax();
          float amt = hmax * bo[@E_RP@ * 5 + rt] / 100.0f;
          if (hnow > 0.0f && hnow < hmax) {
            if (hnow + amt > hmax) amt = hmax - hnow;
            m.addStatValue(hi, amt);
          }
        }
      }
    } else c[1] = 0.0f;
  } catch (Throwable t) { if (!F_HEAL) { F_HEAL = true; @PKG@.AccStore.warn("Regeneration from accessories failed (logged once): " + t); } }
  // 4. movement: Speed + Feather (jump height, less fall damage) through the shared protocol (source accessories.talismans, layer
  //    pct, fractions: 0.10 = +10%, fall -0.40 = 40% less)
  try { move(u, pr, cb, ref, bo[@E_SP@ * 5 + best[@L_SP@]] / 100.0f, bo[@E_JU@ * 5 + best[@L_FE@]] / 100.0f, 0.0f - bo[@E_FA@ * 5 + best[@L_FE@]] / 100.0f); }
  catch (Throwable t) { if (!F_MOVE) { F_MOVE = true; @PKG@.AccStore.warn("accessory Speed / Feather failed (logged once): " + t); } }
  // 5. combat stats to SkyyGear: ONE text per player in gear:extra:<uuid> (written only when it changes; AccGear's back-off rules)
  try { @PKG@.AccGear.publish(u, pr.getUsername(), @PKG@.AccGear.textOf(best), System.currentTimeMillis()); }
  catch (Throwable t) { if (!F_GEAR) { F_GEAR = true; @PKG@.AccStore.warn("accessory combat stats for SkyyGear failed (logged once): " + t); } }
  // 6. the one-time 0.5 notice
  try { @PKG@.AccNotice.check(pr, u); }
  catch (Throwable t) { if (!F_NOTE) { F_NOTE = true; @PKG@.AccStore.warn("the 0.5 notice failed (logged once): " + t); } }
}""".replace("@E_HF@", str(KIND_E["maxHealth"])).replace("@E_SF@", str(KIND_E["maxStamina"])).replace("@E_SR@", str(KIND_E["staminaRegen"]))
     .replace("@E_MP@", str(KIND_E["manaPct"])).replace("@E_MF@", str(KIND_E["manaFloor"])).replace("@E_RP@", str(KIND_E["healPct"]))
     .replace("@E_SP@", str(KIND_E["speedPct"])).replace("@L_H@", str(ENTRIES[KIND_E["maxHealth"]][1]))
     .replace("@L_S@", str(ENTRIES[KIND_E["maxStamina"]][1])).replace("@L_M@", str(ENTRIES[KIND_E["manaPct"]][1]))
     .replace("@L_R@", str(ENTRIES[KIND_E["healPct"]][1])).replace("@L_SP@", str(ENTRIES[KIND_E["speedPct"]][1]))
     .replace("@E_JU@", str(KIND_E["jumpPct"])).replace("@E_FA@", str(KIND_E["fallPct"])).replace("@L_FE@", str(ENTRIES[KIND_E["fallPct"]][1])))
assert ENTRIES[KIND_E["staminaRegen"]][1] == ENTRIES[KIND_E["maxStamina"]][1] and ENTRIES[KIND_E["manaFloor"]][1] == ENTRIES[KIND_E["manaPct"]][1]
assert ENTRIES[KIND_E["jumpPct"]][1] == ENTRIES[KIND_E["fallPct"]][1], "Feather's jump and fall are one line"

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyAccessoriesPlugin({JPI} init) {{ super(init); }}", pl))
_READY = ("[SkyyAccessories] %s ready (%s) - /accessories (lines; admins: give, givetier, reload), right-click the Accessory Bag; %d bench "
          "accessories + Omni (%d retired kept as items that do nothing - Alchemy Bench, Cooking Bench), Campfire accessory for quick "
          "inventory cooking, %d booster lines in the gear rarities Normal to Legendary (%d items + %d old ids, hidden from the creative library; combat stats to SkyyGear "
          "through gear:extra, Feather's jump and fall through the movement protocol), bag up to %d slots, one "
          "bag per profile when SkyyProfiles runs; ") % (VERSION, KIT_ID, sum(b[3] for b in ACTIVE),
                                                       sum(b[3] for b in BENCHES if b[0] in RETIRED), len(BOOSTERS), len(LINE_IDS),
                                                       len(FOLDED) * len(LEGACY_WORDS), CAP)
JM(pl, r"""
public void setup() {
  @PKG@.AccStore.LOG = getLogger();
  @PKG@.AccStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("bags");
  @PKG@.AccCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("config.properties");   // 0.4.4
  String m51 = @PKG@.AccCfg.migrate051();   // 0.5.1: a 0.5 file gets the Stamina numbers ONCE (History copy first), before the loader
  String cs = @PKG@.AccCfg.load(true);   // 0.5: a first start writes the 0.5 file; an existing 0.4.x file is updated ONCE (before CfgPub.start)
  if (m51.length() > 0) cs = cs + "; " + m51;
  @PKG@.AccNotice.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("notices.properties");   // 0.5
  @PKG@.AccNotice.load();
  com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction.registerSimple(this, @PKG@.SkyyAccessoriesPlugin.class, "SkyyAccBag", new @PKG@.AccPageFactory());
  getCommandRegistry().registerCommand(new @PKG@.AccCmd());
  @PKG@.AccStore.bridge().put("acc:fn:has", new @PKG@.AccFn());
  @PKG@.AccStore.bridge().put("acc:defs", @PKG@.AccDefs.defsText());     // 0.5: every rarity of every line (the later loot pass)
  @PKG@.AccStore.bridge().put("acc:fn:give", new @PKG@.AccGiveFn());     // 0.5: give a booster to an online player (n given now, 0 none, -1 queued: never retry)
  getEntityStoreRegistry().registerSystem(new @PKG@.AccEffects());
  @PKG@.MoveSync.checkProto("SkyyAccessories");
  this.ticker = com.hypixel.hytale.server.core.HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.AccTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log(@READY@ + cs + "; admin settings: SkyWynn Menu -> Server Setup -> Accessories or /accessories reload");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());   // 0.4.4: config:def / config:fn:SkyyAccessories - LAST, after the config load
}""".replace("@READY@", jlit(_READY)))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:has"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:give"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:defs"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccGear.shutdownAll(); } catch (Throwable t) { }   // 0.5 part 2: our gear:extra texts + movement entries
  try { com.skyy.accessories.AccNotice.save(); } catch (Throwable t) { }
  try { com.skyy.accessories.CfgPub.shutdown(); } catch (Throwable t) { }   // 0.4.4: pending config saves + change-log lines now
  super.shutdown();
}""", pl))

for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear):
    c.writeFile(OUT)
kit.write(OUT)   # 0.4.4: deferred kit checks (0.5: AccCfg.reload / checkBoost exist with the right signatures), then the 7 kit classes
print("classes written (+%d config kit)" % len(kit.classes))

# ================= assets: items + lang =================
def item(iid, icon, quality, recipe_in, bench_req, page_id=None, visual=None):
    node = {
      "TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
      "Categories": ["Items.Tools"],
      "Icon": icon,
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": bench_req},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
    }
    if visual:
        node.update(visual)   # 0.2 review fix: talismans look like the vanilla crystal they are made from (0.1 placeholder: backpack)
    if page_id:
        node["Interactions"] = {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    return node

WB_REQ = [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]
# 0.2: every recipe input / icon is checked against the vanilla Assets.zip (build fails on a typo instead of a broken recipe in game)
import zipfile
_ASSETS = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
_ITEMS = {}
for _n in _ASSETS.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        _ITEMS[os.path.basename(_n)[:-5]] = _n
_COMMON = set(n for n in _ASSETS.namelist() if n.startswith("Common/"))
_RTYPES = set(os.path.basename(n)[:-5] for n in _ASSETS.namelist() if n.startswith("Server/Item/ResourceTypes/") and n.endswith(".json"))
_VNAMES = {}
for _l in _ASSETS.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
    if _l.startswith("items.") and ".name" in _l and "=" in _l:
        _k, _v = _l.split("=", 1)
        _VNAMES[_k.strip()[len("items."):-len(".name")]] = _v.strip()
def vname(iid):
    """vanilla display name (en-US server.lang), e.g. Ingredient_Bar_Iron -> Iron Ingot"""
    return _VNAMES.get(iid) or iid.replace("Ingredient_", "").replace("Rock_Gem_", "").replace("_", " ")
def need_item(iid):
    assert iid in _ITEMS, "unknown vanilla item id: " + iid
def mat(m, q):
    """recipe input: ItemId for items, ResourceTypeId for resource types (0.1 bug: the Farming Bench upgrades used
    ItemId Wood_Softwood_Trunk etc. - those are ResourceTypes in vanilla Bench_Farming TierLevels, so the recipes could not resolve)"""
    if m in _ITEMS: return {"ItemId": m, "Quantity": q}
    assert m in _RTYPES, "unknown vanilla item / resource type: " + m
    return {"ResourceTypeId": m, "Quantity": q}
def icon_of(iid):
    """the vanilla item's own Icon (follows Parent), checked to exist under Common/"""
    seen = 0
    cur = iid
    while cur and seen < 8:
        need_item(cur)
        d = json.loads(_ASSETS.read(_ITEMS[cur]).decode("utf-8-sig"))
        if d.get("Icon"):
            assert "Common/" + d["Icon"] in _COMMON, "missing icon file for %s: %s" % (iid, d["Icon"])
            return d["Icon"]
        cur = d.get("Parent"); seen += 1
    raise SystemExit("no icon for " + iid)
VISUAL_KEYS = ("Model", "Texture", "IconProperties", "Scale", "PlayerAnimationsId", "ItemSoundSetId")
def visual_of(iid):
    """held / dropped look of a vanilla item (follows Parent, the child's value wins); Model and Texture checked to exist under Common/"""
    out = {}
    cur = iid
    seen = 0
    while cur and seen < 8:
        need_item(cur)
        d = json.loads(_ASSETS.read(_ITEMS[cur]).decode("utf-8-sig"))
        for k in VISUAL_KEYS:
            if k in d and k not in out: out[k] = d[k]
        cur = d.get("Parent"); seen += 1
    assert "Model" in out and "Texture" in out, "no model for " + iid
    for k in ("Model", "Texture"):
        assert "Common/" + out[k] in _COMMON, "missing %s file for %s: %s" % (k, iid, out[k])
    return out
FIELD_REQ = [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}]
QUAL = [QUAL_IDS[BENCH_RARITY[min(_t, 7)]] for _t in range(8)]   # 0.5: bench tier -> Skyy_Acc_* (I Normal .. IV+ Legendary; = AccDefs.rarityOf)
# 0.5.1: OLD IDS OUT OF THE CREATIVE LIBRARY (Skyy: "this one appears twice in creative"). The legacy booster ids and the retired bench
# accessories stay real items (owned copies load, render, show their tooltip and convert in the bag as before) but get the engine's
# item library filter: "Variant": true (filtered out of the library by default) and no "Categories" (no library tab even with the
# library's Show Variants toggle on). The current items keep Categories ["Items.Tools"] and no Variant (_hidden_checks below).
RETIRED_IDS = ["Skyy_Accessory_%s_T%d" % (_b[0], _t) for _b in BENCHES if _b[0] in RETIRED for _t in range(1, _b[3] + 1)]
HIDDEN_IDS = LEGACY_IDS + RETIRED_IDS
assert len(LEGACY_IDS) == 20 and len(RETIRED_IDS) == 5 and len(set(HIDDEN_IDS)) == 25, (len(LEGACY_IDS), RETIRED_IDS)
assert all(py_legacy(_i) for _i in LEGACY_IDS) and not set(HIDDEN_IDS) & set(LINE_IDS)


def hide_item(iid, node):
    """0.5.1: keep an old id out of the creative item library (the Item codec's Variant + Categories, proven by _variant_proof)"""
    assert iid in HIDDEN_IDS, "0.5.1: only the old ids are hidden: " + iid
    del node["Categories"]
    node["Variant"] = True
    return node


files = {}
lang = []
# ---- 0.5 the six quality assets (spec 5.2): the vanilla Common.json field set, SkyyGear's frame art, the kit's rarity colours, the
# label under general.qualities.<id> AND server.general.qualities.<id> (the SkyySacks pattern). Fabled and Mythic ship unused (spec 4.1).
_VQF = set(json.loads(_ASSETS.read("Server/Item/Qualities/Common.json").decode("utf-8-sig")).keys())
_PARTS = set(os.path.basename(n)[:-len(".particlesystem")] for n in _ASSETS.namelist() if n.endswith(".particlesystem"))
def _tex(p):
    q = "Common/" + p
    return q in _COMMON or (q.endswith(".png") and q[:-4] + "@2x.png" in _COMMON)
for _r in range(1, len(DISPLAY)):
    _nm = DISPLAY[_r]
    _tt, _slot, _part = QUAL_ART[_nm]
    _q = {"QualityValue": _r,
          "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % _tt,
          "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltip%sArrow.png" % _tt,
          "SlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "BlockSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "SpecialSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "TextColor": SUI.RARITY[_nm].lower(),
          "LocalizationKey": "server.general.qualities." + QUAL_IDS[_r],
          "VisibleQualityLabel": True,
          "RenderSpecialSlot": True,
          "ItemEntityConfig": {"ParticleSystemId": _part}}
    assert set(_q) == _VQF, "0.5: quality field set differs from vanilla Common.json: %s" % (set(_q) ^ _VQF)
    assert _q["QualityValue"] < 8, "0.5: a quality at 8 or more is 'technical' for SkyyAuctions"
    for _k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        assert _tex(_q[_k]), "0.5: quality texture missing in Assets.zip: " + _q[_k]
    assert _part in _PARTS, "0.5: drop particle missing in Assets.zip: " + _part
    files["Server/Item/Qualities/%s.json" % QUAL_IDS[_r]] = json.dumps(_q, indent=2)
    lang.append("general.qualities.%s=%s" % (QUAL_IDS[_r], _nm))
    lang.append("server.general.qualities.%s=%s" % (QUAL_IDS[_r], _nm))
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, "Icons/ItemsGenerated/Utility_Bag_Seed.png", QUAL_IDS[2],
    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], FIELD_REQ, "SkyyAccBag"), indent=2)
lang.append("items.%s.name=Accessory Bag" % BAG); lang.append("server.items.%s.name=Accessory Bag" % BAG)
d = ("Right-click to open. Holds your accessories. Bench accessories in it let /craft make that bench's recipes straight from your "
     "inventory; stat accessories in it add their bonus (only your best of each line counts); the Omni accessory counts as every bench "
     "accessory.")
lang.append("items.%s.description=%s" % (BAG, d)); lang.append("server.items.%s.description=%s" % (BAG, d))
count = 0
retired_count = 0
# 0.4.2: descriptions of the retired bench accessories (asset kept, no recipe)
RETIRED_TAIL = " This accessory does nothing and cannot be equipped; if one is still in your Accessory Bag, Unequip takes it out."
RETIRED_DESC = {
    "Alchemybench": "Retired. Alchemy is a skill now: brew at a real Alchemy Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
    "Cookingbench": "Retired. Cooking is a skill now: cook at a real Cooking Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
}
assert sorted(RETIRED_DESC) == sorted(RETIRED)
for bench_id, bench_item, name, tiers, ups in BENCHES:
    for t in range(1, tiers + 1):
        iid = "Skyy_Accessory_%s_T%d" % (bench_id, t)
        if t == 1:
            need_item(bench_item)
            rin = [{"ItemId": bench_item, "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}]
        else:
            rin = [{"ItemId": "Skyy_Accessory_%s_T%d" % (bench_id, t - 1), "Quantity": 1}] + [mat(m, q) for m, q in ups[t - 2]]   # 0.2: mat() fixes resource types
        icon = "Icons/ItemsGenerated/%s.png" % ("Bench_Architects" if bench_item == "Bench_Builders" else bench_item)
        node = item(iid, icon, QUAL[min(t, 7)], rin, WB_REQ)
        disp = "%s Accessory %s" % (name, ROMAN[t]) if tiers > 1 else "%s Accessory" % name
        d = "Put it in your Accessory Bag to craft %s recipes%s from your inventory with /craft.%s" % (
            name, (" up to tier %s" % ROMAN[t]) if tiers > 1 else "",
            (" Upgrade it with the same materials the bench needs for tier %s." % ROMAN[t + 1]) if t < tiers else "")
        if bench_id == "Campfire":   # 0.4.3: back as quick inventory cooking (SkyyCooking cook:fn:campfire through SkyySacks /craft)
            d = CAMPFIRE_DESC
        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)
            del node["Recipe"]
            hide_item(iid, node)  # 0.5.1: not in the creative library
            disp += " (retired)"
            d = RETIRED_DESC[bench_id]
            retired_count += 1
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        count += 1
need_item("Ingredient_Bar_Copper"); need_item("Ingredient_Fabric_Scrap_Cotton"); assert "Wood_Trunk" in _RTYPES

# ---- 0.5 THE BOOSTER ITEMS (spec 2.2, 5.6, 5.7): one item per rarity of every line, generated from the booster table.
# Look: the line's crystal fragment MODEL for every rarity; icons Normal crystal fragments, Unique small cluster, Rare large cluster,
# Legendary the gem (each rarity its own icon). Names "<Rarity> <Line> Accessory". Tooltip = vanilla item-text markup: the stat line
# first (<color is="#ffffff">), what it does, the one-per-line rule with the next rarity, an italic flavour line; a line break is the
# two characters \n inside one lang line (a real newline would break the file).
TIP_NL = "\\n"
def _w(t):
    return '<color is="#ffffff">%s</color>' % t
def _n(v):
    return "%g" % v
TIPS = {   # kind -> (stat line, what it does) at one rarity; vals = {kind: number}; kinds without an entry ride along (manaFloor)
    "maxHealth": lambda v: (_w("+%s max Health" % _n(v["maxHealth"])) + " while in your Accessory Bag.",
                            "Raises your maximum Health; the bar fills up by normal means."),
    "maxStamina": lambda v: (_w("+%s max Stamina" % _n(v["maxStamina"])) + " and " + _w("+%s%% Stamina Regen" % _n(v["staminaRegen"])) +
                             " while in your Accessory Bag.",
                             "Your Stamina refills %s%% faster whenever it refills (not while you sprint, glide or block)." % _n(v["staminaRegen"])),
    "manaPct": lambda v: (_w("+%s%% max Mana" % _n(v["manaPct"])) + " (at least +%s) while in your Accessory Bag." % _n(v["manaFloor"]),
                          "A percent of the Mana your level, skills and gear give."),
    "healPct": lambda v: (_w("Heals %s%% of your max Health" % _n(v["healPct"])) + " every %d seconds while in your Accessory Bag." % REGEN_EVERY,
                          "Works in combat too."),
    "speedPct": lambda v: (_w("+%s%% movement speed" % _n(v["speedPct"])) + " while in your Accessory Bag.", "Adds on top of Acrobatics."),
    # part 2 (spec 5.7): the stat line first, what it affects, the requirement (no mod names - players do not know "SkyyGear")
    "str": lambda v: (_w("+%s Strength" % _n(v["str"])) + " while in your Accessory Bag.",
                      "More damage with melee, arrows, thrown weapons and staff melee." + TIP_NL + "Works with gear weapons or bare hands."),
    "mp": lambda v: (_w("+%s Magical Power" % _n(v["mp"])) + " while in your Accessory Bag.",
                     "More damage with spells." + TIP_NL + "Spell shots only (wand, staff, spellbook)."),
    "def": lambda v: (_w("+%s Defense" % _n(v["def"])) + " while in your Accessory Bag.",
                      "Takes a little off every hit." + TIP_NL + "Against hits from mobs and players."),
    "cc": lambda v: (_w("+%s%% Crit Chance" % _n(v["cc"])) + " and " + _w("+%s%% Crit Damage" % _n(v["cd"])) + " while in your Accessory Bag.",
                     "A critical hit does double damage, and Crit Damage makes it hit even harder." + TIP_NL +
                     "Works with gear weapons or bare hands."),
    "fallPct": lambda v: (_w("-%s%% fall damage" % _n(v["fallPct"])) + " and " + _w("+%s%% jump height" % _n(v["jumpPct"])) +
                          " while in your Accessory Bag.", "Softer landings and higher jumps, on top of Acrobatics."),
}
def booster_name(li, t):
    return "%s %s Accessory" % (DISPLAY[t], BOOSTERS[li][2])
def booster_desc(li, t, legacy=False):
    b = BOOSTERS[li]
    vals = dict((kind, v[t - 1]) for _st, kind, v in b[5])
    main = [k for k in vals if k in TIPS]
    assert len(main) == 1, "0.5: line %s needs exactly one tooltip template among %s" % (b[1], list(vals))
    first, what = TIPS[main[0]](vals)
    nxt = ("Next: %s (upgrade it at a Workbench)." if b[8] is not None else "Next: %s.") % booster_name(li, t + 1) if t < 4 else ""
    rule = "Only your best %s Accessory counts. " % b[2] + (nxt if t < 4 else "Legendary is the top rarity.")
    # part 1 review finding 4: an old copy can be refused as a tie (an equal or better one already equipped) and never converted
    old = ""
    if legacy:
        old = TIP_NL + "An older copy: put it in your Accessory Bag once and it becomes the current one" + (
            " (only that one can be upgraded)" if t < 4 else "") + ". If it is refused, an equal or better one is already equipped."
    return first + TIP_NL + what + TIP_NL + rule + old + TIP_NL + TIP_NL + "<i>%s</i>" % b[7]
tal_count = 0
legacy_count = 0
ICONS = {}
for li, b in enumerate(BOOSTERS):
    fam, adm, line, crystal, gem, stats, src, flavour, recipes, style = b
    if crystal is not None:   # crystal style: the crystal fragment model in the line's colour for every rarity (clusters / gems are blocks)
        _v = visual_of("Ingredient_Crystal_" + crystal)
        visuals = [None, _v, _v, _v, _v]
        icons = [None, icon_of("Ingredient_Crystal_" + crystal), icon_of("Rock_Crystal_%s_Small" % crystal),
                 icon_of("Rock_Crystal_%s_Large" % crystal), icon_of(gem)]
    else:                     # part 2 item style (spec 5.6): each rarity copies the model and icon of its own vanilla item
        visuals = [None] + [visual_of(x) for x in gem]
        icons = [None] + [icon_of(x) for x in gem]
    assert len(set(icons[1:])) == 4, "0.5: two rarities of the %s line share an icon: %s" % (adm, icons)
    ICONS[adm] = icons
    for t in range(1, 5):
        iid = LINE_IDS[li * 4 + t - 1]
        if recipes is None:
            rin = []                  # part 2: no recipe (admin give only until the loot pass)
        elif t == 1:
            rin = [mat(m, q) for m, q in recipes[0]]
        else:
            rin = [{"ItemId": LINE_IDS[li * 4 + t - 2], "Quantity": 1}] + [mat(m, q) for m, q in recipes[t - 1]]
        node = item(iid, icons[t], QUAL_IDS[t], rin, WB_REQ, visual=visuals[t])
        if recipes is None:
            del node["Recipe"]
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, booster_name(li, t))); lang.append("server.items.%s.name=%s" % (iid, booster_name(li, t)))
        lang.append("items.%s.description=%s" % (iid, booster_desc(li, t))); lang.append("server.items.%s.description=%s" % (iid, booster_desc(li, t)))
        tal_count += 1
    if style != "word":
        continue              # the new lines have no old ids
    # the old ids (0.2/0.3 Talisman / Ring / Artifact and 0.4's fifth id Legendary): asset kept so owned copies still load and render,
    # NO recipe; the look, name and text of the rarity they count as (players never see ids); equip / unequip turns them into that id
    vis = visuals[1]
    for word, lt in LEGACY_WORDS:
        iid = "Skyy_Talisman_%s_%s" % (fam, word)
        node = item(iid, icons[lt], QUAL_IDS[lt], [], WB_REQ, visual=vis)
        del node["Recipe"]
        hide_item(iid, node)      # 0.5.1: not in the creative library (Skyy saw the old Artifact next to the Legendary)
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, booster_name(li, lt))); lang.append("server.items.%s.name=%s" % (iid, booster_name(li, lt)))
        lang.append("items.%s.description=%s" % (iid, booster_desc(li, lt, True))); lang.append("server.items.%s.description=%s" % (iid, booster_desc(li, lt, True)))

        legacy_count += 1
print("booster items:", tal_count, "old ids kept (no recipe):", legacy_count)

# 0.4 OMNI accessory: Workbench recipe = the max-tier accessory of every bench; counts as all of them (AccDefs.benchList); 0.5 Legendary
omni_in = []
for bench_id, bench_item, name, tiers, ups in ACTIVE:   # 0.4.2: retired benches are no inputs (13 -> 10); 0.4.3: the Campfire is again (11)
    top = "Skyy_Accessory_%s_T%d" % (bench_id, tiers)
    assert "Server/Item/Items/Utility/%s.json" % top in files, top
    omni_in.append({"ItemId": top, "Quantity": 1})
assert len(omni_in) == len(ACTIVE) == 11
assert {"ItemId": "Skyy_Accessory_Campfire_T1", "Quantity": 1} in omni_in   # 0.4.3
files["Server/Item/Items/Utility/%s.json" % OMNI] = json.dumps(item(OMNI, icon_of("Rock_Gem_Diamond"), QUAL_IDS[4], omni_in, WB_REQ), indent=2)
lang.append("items.%s.name=Omni Accessory" % OMNI); lang.append("server.items.%s.name=Omni Accessory" % OMNI)
d = ("Legendary accessory. Keep it in your Accessory Bag and it counts as EVERY bench accessory at its highest tier (%s), so /craft shows "
     "all of their recipes. It has its own slot rule, so it can sit next to other bench accessories. Crafted at a Workbench from all %d "
     "top-tier bench accessories. Campfire dishes made through it are quick inventory cooking, like the Campfire accessory. Alchemy "
     "and Cooking are table-only, so the retired Alchemy Bench and Cooking Bench accessories are not part of it and are not covered.") % (", ".join(("%s %s" % (b[2], ROMAN[b[3]])) if b[3] > 1 else b[2] for b in ACTIVE), len(ACTIVE))
lang.append("items.%s.description=%s" % (OMNI, d)); lang.append("server.items.%s.description=%s" % (OMNI, d))
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
print("accessory items:", count, "retired (no recipe):", retired_count)
# 0.4.2 build check: no generated recipe takes a retired bench accessory, and no retired accessory has a recipe
_RET_IDS = set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in BENCHES if b[0] in RETIRED for t in range(1, b[3] + 1))
assert retired_count == len(_RET_IDS) == 5, (retired_count, sorted(_RET_IDS))   # 0.4.3: Alchemy Bench T1-T4 + Cooking Bench
for _fn, _body in files.items():
    if not _fn.endswith(".json") or not _fn.startswith("Server/Item/Items/"):
        continue
    _node = json.loads(_body)
    _iid = os.path.basename(_fn)[:-5]
    if _iid in _RET_IDS:
        assert "Recipe" not in _node, "retired accessory still has a recipe: " + _iid
    for _inp in (_node.get("Recipe") or {}).get("Input", []):
        assert _inp.get("ItemId") not in _RET_IDS, "%s still takes the retired %s" % (_iid, _inp.get("ItemId"))
# 0.4.3 build check: the Campfire accessory is back - the 0.4.1 Workbench recipe, its own name + description, an Omni input; 0.5 Normal
_CF = "Skyy_Accessory_Campfire_T1"
assert _CF not in _RET_IDS
_cfn = json.loads(files["Server/Item/Items/Utility/%s.json" % _CF])
assert (_cfn.get("Recipe") or {}).get("Input") == [{"ItemId": "Bench_Campfire", "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}], _cfn.get("Recipe")
assert _cfn["Recipe"]["BenchRequirement"] == WB_REQ and _cfn["Quality"] == QUAL_IDS[1], _cfn
for _pre in ("items.", "server.items."):
    assert (_pre + _CF + ".name=Campfire Accessory") in lang, _pre
    assert (_pre + _CF + ".description=" + CAMPFIRE_DESC) in lang, _pre
assert not any(l.startswith(("items." + _CF + ".", "server.items." + _CF + ".")) and "etired" in l for l in lang), "Campfire text still says retired"
_omn = json.loads(files["Server/Item/Items/Utility/%s.json" % OMNI])["Recipe"]["Input"]
assert sorted(i["ItemId"] for i in _omn) == sorted("Skyy_Accessory_%s_T%d" % (b[0], b[3]) for b in ACTIVE) and len(_omn) == 11, _omn
print("campfire accessory: recipe back, Omni input %d of %d, retired ids: %s" % (_omn.index({"ItemId": _CF, "Quantity": 1}) + 1, len(_omn), ", ".join(sorted(_RET_IDS))))


def _booster_asset_checks():
    """0.5 part 1 build checks on the generated assets (research/Booster-Accessories-Spec.md 6.1)"""
    import re as _re
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    assert sorted(quals) == sorted(QUAL_IDS[1:]) and len(quals) == 6, sorted(quals)
    lt = files["Server/Languages/en-US/server.lang"]
    lmap = dict(l.split("=", 1) for l in lt.split("\n") if "=" in l)
    for qid in quals:
        assert lmap.get("general.qualities." + qid) == lmap.get("server.general.qualities." + qid) == qid[len("Skyy_Acc_"):], qid
    # every item's quality is shipped here; an item with a recipe (booster, bench, Omni, bag) is never above Legendary
    for iid, node in items.items():
        assert node["Quality"] in quals, "%s uses quality %s that is not shipped" % (iid, node["Quality"])
        if "Recipe" in node:
            assert QUAL_IDS.index(node["Quality"]) <= MAX_LINE_RARITY, "crafted %s is above Legendary (%s)" % (iid, node["Quality"])
    assert items[OMNI]["Quality"] == QUAL_IDS[4] and items[BAG]["Quality"] == QUAL_IDS[2]
    for b in BENCHES:
        for t in range(1, b[3] + 1):
            assert items["Skyy_Accessory_%s_T%d" % (b[0], t)]["Quality"] == QUAL_IDS[BENCH_RARITY[min(t, 7)]], (b[0], t)
    # the booster ids: exactly 4 rarities Normal..Legendary per line, the Workbench ladder (folded lines), no recipe (part 2 lines),
    # the old ids without a recipe
    for li, b in enumerate(BOOSTERS):
        ids = LINE_IDS[li * 4:li * 4 + 4]
        assert [items[i]["Quality"] for i in ids] == QUAL_IDS[1:5], (b[1], [items[i]["Quality"] for i in ids])
        assert len(set(items[i]["Icon"] for i in ids)) == 4, "%s: two rarities share an icon" % b[1]
        if b[9] != "word":
            assert all("Recipe" not in items[i] for i in ids), "%s: a part 2 line has a recipe (admin give only)" % b[1]
            assert all(i.endswith("_T%d" % (t + 1)) and not i.startswith("Skyy_Accessory_") for t, i in enumerate(ids)), ids
            assert not any(("Skyy_Talisman_%s_%s" % (b[0], w)) in items for w, _t in LEGACY_WORDS), "%s: no old ids" % b[1]
            continue
        for t in range(2, 5):
            assert {"ItemId": ids[t - 2], "Quantity": 1} in items[ids[t - 1]]["Recipe"]["Input"], "%s: the ladder is broken at %s" % (b[1], ids[t - 1])
        for w, t in LEGACY_WORDS:
            lid = "Skyy_Talisman_%s_%s" % (b[0], w)
            assert "Recipe" not in items[lid] and items[lid]["Quality"] == QUAL_IDS[t] and items[lid]["Icon"] == items[ids[t - 1]]["Icon"], lid
            assert lmap["server.items.%s.name" % lid] == lmap["server.items.%s.name" % ids[t - 1]], lid
    assert not any(i.endswith("_Legendary") and i.startswith("Skyy_Talisman_") and "Recipe" in n for i, n in items.items())
    assert not any(inp.get("ItemId", "").startswith("Skyy_Talisman_") and inp.get("ItemId", "").endswith("_Legendary")
                   for n in items.values() for inp in (n.get("Recipe") or {}).get("Input", [])), "a recipe still takes an old _Legendary id"
    # names: exactly "<Rarity> <Line> Accessory" for all 60 stat accessory ids (40 modern + 20 old); lang lines are one line each
    for li, b in enumerate(BOOSTERS):
        for t in range(1, 5):
            assert lmap["items.%s.name" % LINE_IDS[li * 4 + t - 1]] == "%s %s Accessory" % (DISPLAY[t], b[2])
            d = lmap["items.%s.description" % LINE_IDS[li * 4 + t - 1]]
            assert d.startswith('<color is="#ffffff">') and "while in your Accessory Bag." in d.split("\\n")[0], "stat line first: " + d[:80]
            if b[8] is None:
                assert "Workbench" not in d, "a part 2 tooltip promises a Workbench upgrade: " + d
    assert all("\r" not in l for l in lang) and len(lt.split("\n")) == len(lang) + 1, "a lang value holds a real line break"
    # no scrapped name or the old item word in anything a player reads: lang values, Server Setup labels + help (admins), config text
    bad = ("Vitality", "Endurance", "Intelligence", "Talisman")
    for k, v in lmap.items():
        assert not any(w in v for w in bad) and "talisman" not in v.lower(), "a player text says %r: %s=%s" % ([w for w in bad if w in v], k, v)
    for r in CFG_ROWS:
        assert not any(w in r[1] + r[10] for w in bad) and "talisman" not in (r[1] + r[10]).lower(), r[0]
    assert not any(w in CONFIG_TEXT for w in bad) and "talisman" not in CONFIG_TEXT.lower()
    print("booster assets: %d lines x 4 rarities (%d with a Workbench ladder, %d admin give only), %d old ids, 6 qualities (%s), "
          "names and texts checked" % (len(BOOSTERS), len(FOLDED), len(BOOSTERS) - len(FOLDED), len(LEGACY_IDS), ", ".join(DISPLAY[1:])))


_booster_asset_checks()


def _hidden_checks():
    """0.5.1 build check: exactly the old ids are hidden from the creative library, every current id stays listed"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    lt = files["Server/Languages/en-US/server.lang"]
    lmap = dict(l.split("=", 1) for l in lt.split("\n") if "=" in l)
    hidden = sorted(i for i, n in items.items() if "Variant" in n)
    assert hidden == sorted(HIDDEN_IDS), "0.5.1: the hidden items differ from HIDDEN_IDS: %s" % sorted(set(hidden) ^ set(HIDDEN_IDS))
    for iid in HIDDEN_IDS:
        n = items[iid]
        assert n["Variant"] is True and "Categories" not in n and "Recipe" not in n, "0.5.1: %s is not hidden right: %r" % (iid, n)
        assert py_legacy(iid) or iid in RETIRED_IDS, iid
        assert n["Quality"] in quals and n["MaxStack"] == 1 and n.get("Icon") and lmap.get("server.items.%s.name" % iid) and \
            lmap.get("server.items.%s.description" % iid), "0.5.1: %s lost its look or text" % iid
        if py_legacy(iid):   # it still looks and reads like the rarity it counts as (0.5's rule, re-checked on the hidden item)
            cur = items[py_modern(iid)]
            assert n["Quality"] == cur["Quality"] and n["Icon"] == cur["Icon"] and n["Model"] == cur["Model"], iid
            assert lmap["server.items.%s.name" % iid] == lmap["server.items.%s.name" % py_modern(iid)], iid
    current = sorted(i for i in items if i not in HIDDEN_IDS)
    want = set(LINE_IDS) | set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in ACTIVE for t in range(1, b[3] + 1)) | {OMNI, BAG}
    assert set(current) == want, "0.5.1: current items differ: %s" % sorted(set(current) ^ want)
    for iid in current:
        assert "Variant" not in items[iid] and items[iid].get("Categories") == ["Items.Tools"], "0.5.1: %s must stay listed" % iid
    for iid, n in items.items():
        for inp in (n.get("Recipe") or {}).get("Input", []):
            assert inp.get("ItemId") not in HIDDEN_IDS, "0.5.1: %s takes the hidden %s" % (iid, inp.get("ItemId"))
    assert not any(q.get("HideFromSearch") for q in quals.values()), "0.5.1: a quality hides items (the qualities are shared)"
    print("creative library: %d old ids hidden (Variant true, no Categories: %d legacy booster ids + %d retired bench accessories), "
          "%d current ids listed" % (len(HIDDEN_IDS), len(LEGACY_IDS), len(RETIRED_IDS), len(current)))


_hidden_checks()


def _player_literals_check():
    """0.5 build check: no Java string literal of this script says Vitality / Endurance / Intelligence / Talisman / talisman, except
    item ids and id words (the id rules need them), the movement source name and the one notice text (MIG_NOTICE, spec 5.1). Scans every
    string constant / f-string of this script that holds Java (a "public " member) - chat, page, refusal and command texts included."""
    import ast as _ast, re
    tree = _ast.parse(
open(os.path.abspath(__file__), encoding="utf8").read())
    ok_exact = set(["Vitality", "Endurance", "Intelligence", "Talisman", "Ring", "Artifact", "Legendary", "accessories.talismans",
                    "_Talisman", "_Ring", "_Artifact", "Skyy_Talisman_", "T:"])
    id_re = re.compile(r"^Skyy_[A-Za-z0-9_]*$")
    lit_re = re.compile(r'"((?:[^"\\\n]|\\.)*)"')
    n = 0
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Constant) and isinstance(node.value, str):
            txt = node.value
        elif isinstance(node, _ast.JoinedStr):
            txt = "".join(v.value for v in node.values if isinstance(v, _ast.Constant) and isinstance(v.value, str))
        else:
            continue
        if not re.search(r"(^|\n)\s*(public|protected)\s", txt):
            continue
        txt = re.sub(r"//[^\n]*", "", txt)
        for m in lit_re.finditer(txt):
            lit = m.group(1)
            n += 1
            if lit in ok_exact or id_re.match(lit) or lit == jlit(MIG_NOTICE)[1:-1]:
                continue
            if any(w in lit for w in ("Vitality", "Endurance", "Intelligence", "Talisman")) or "talisman" in lit.lower():
                raise SystemExit("0.5: a Java string literal says an old name (players must only see line names): %r" % lit)
    page = [ACC_HINT, ACC_NONE, ACC_EMPTY] + [SUI.render(v) for _p, mk in ACC_SH.appends for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,))] + \
        [SUI.render(v) for _i, _p, v in ACC_SH.all_sets()]

    for t in page:
        if any(w in t for w in ("Vitality", "Endurance", "Intelligence", "Talisman")) or "talisman" in t.lower():
            raise SystemExit("0.5: a page text says an old name: %r" % t[:200])
    print("player texts: %d Java string literals and %d page texts scanned, no old names" % (n, len(page)))


_player_literals_check()

jar = os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyAccessories", VERSION, "SkyWynn accessory bag: bench accessories unlock /craft (SkyySacks) recipes; stat accessories in ten lines (Health, Stamina with Stamina Regen, Mana, Regeneration, Speed, and admin-given Brawler, Runic, Stonehide, Razorfang and Feather - combat stats through SkyyGear, fall damage through SkyySkills) in the gear rarities Normal to Legendary add their bonus while they sit in the bag, only the best of each line counts; the Omni accessory counts as every bench accessory; speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol; up to 60 bag slots (18 by default); one bag per SkyyProfiles profile when that mod is installed; the Campfire accessory is quick inventory cooking (campfire dishes in /craft at reduced Cooking XP and bonus with SkyyCooking); the Alchemy Bench and Cooking Bench accessories are retired; bag slots, every booster number and the line switches are server settings (config.properties, editable in game through SkyWynn Menu -> Server Setup); /accessories lines lists every line. Zero dependencies.", PKG + ".SkyyAccessoriesPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyAccessories.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyAccessories" % VERSION, disable_prefix="Skyy:")
