"""SkyyAbilityProbe 0.1 - build script (javassist via jpype). A THROWAWAY op-only dev pack like SkyyKeyProbe / SkyyMonkProbe / SkyyUiProbe:
pinned for ONE ~8 minute Skyy test session on Hytale 0.7, then removed from the SET again. No patch-script chain (a probe mod is hand-written;
this file is the source). Phase B1 of research/Ability-Framework-Mage-Spec.md (section 7) - it answers the section 10 UNVERIFIED items the
real-keys round (SkyyClasses 0.1.20, phase B2) depends on, BEFORE that round is written.

Skyy (docs/answered/classes.md 2026-10-13, word for word): "Should we build the abilitys all in one go? Or start with one class, refine it,
then move on to the next?" -> "Mage (Recommended)"; "work through your whole list, so everything is ready to play when i get off work."
Skyy 2026-10-08 (research/cloud/Ability-Probe-Plan.md): "3. wait till 0.7" -> this probe runs on the 0.7.0 release only.

Derived from the cloud draft (git 0c19d9d, research/cloud/Ability-Probe-Plan.md, UNTESTED there), REWRITTEN for the 0.7.0 release jar and
cut to the B1 set the newer spec names: P1, P3, P4, P13, P14, P15 + info / stats / stop. The draft's 0.6.8 fallbacks and P2 / P5-P12
(damage filters, attack speed, Mana spends, stun, dome particles, projectile bubble, banner block, NPC targeting) are LEFT OUT: the spec's
B1 row does not list them, several are answered by live code already (section 7 of the plan), and every extra hook is risk in a jar whose
only job is the rune keys. Every 0.7 class is now named DIRECTLY in the Java (the build compiles against the release jar, so a renamed
method stops the build instead of a test session); only the two PRIVATE engine fields (InteractionManager.cooldownHandler,
CooldownHandler.cooldowns / Cooldown.remainingCooldown) are read by reflection - the engine has no getter for them.

Run:   python SkyyAbilityProbe/build_skyyabilityprobe_0.1.py   -> SkyyAbilityProbe/SkyyAbilityProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyAbilityProbe/test_skyyabilityprobe_0.1.py    (-Xverify:all, every code path executed on real engine objects, the
       state-reset rule, permissions, start twice on a scratch copy of live data, the engine-access audit)

NO ASSETS (manifest IncludesAssetPack false): no item / rune / keyword / language file, so nothing vanilla or pack-owned is overridden. Our OWN
rune ("Cost 0 / None Core rune with a 1-step marker root", spec U1 / U2) needs a rune ITEM = an asset, so it is NOT here - it is the B2
round's first in-game step (the build-time desk below already answers the codec half of U1).

THE PROBES (/aprobe, alias /abilityprobe - never /abilities: vanilla 0.7 owns it; op only: requirePermission skyyabilityprobe.admin + empty
permission groups on the root and every usage variant). Every chat line also goes to the server log as "[SkyyAbilityProbe] to <name>: ..."
(tools/chat_tail.py --grep AbilityProbe reads them; SkyyEssentials mirrors the chat too). Memory only, per player, ONE timed probe at a time
(arming a probe ends the running one with its summary, then resets every probe field - AbCmds.clear() is GENERATED from the field list).
  p1 [cancel]   60 s: every InteractionChainStartEvent of yours. Ability2 / Ability3 lines: root id, the item that answered (a rune in the
                ability section -11 slot 0 / 3, or your weapon when the rune cannot be used with it), the rune's Ability data (slot, cost,
                cooldown, keywords, cast root), whether the hand item passes CoreItemAbility.canUseWith, and crouch / sprint / roll / air at
                the press. "cancel" cancels every Ability2 / 3 chain (the engine then sends the client a cancel packet) and 1 s later checks
                your Mana and the server cooldown of the held rune's Cast root id: PASS = nothing spent, no cooldown armed.  (U1 U3 U4)
  p3 | p3 set <id> <secs> | p3 clear <id>    the player's server-side CooldownHandler (InteractionManager's private field): every
                cooldown it holds (id, max, remaining, charges); "set" arms <id> (a rune's Cast root, e.g. Root_Ability_Fireball) for secs;
                "clear" ends it. Then press the rune key: does the HUD slot fill / does the cast go off?                       (U6)
  p4 read | watch | put <slot> <itemId> | take <slot> | bad <slot>   the AbilitySlots section (-11, 6 slots, lines of 3: slot 0 = Use
                Ability 2, slot 3 = Use Ability 3): read (with each rune's data + canUseWith for your hand item), 60 s
                InventoryChangeEvent watch (AbilitySlots / RuneBag / other), write a RUNE (Core / Support only) by code into an EMPTY slot,
                take back ONLY the exact ItemStack copy the probe put there (identity, never one of yours; /aprobe stop takes them all
                back too), and try your held NON-rune into an empty slot (removed again). (U8)
  p13 [zones] [secs]   getAllEntitiesInSphere cost: zones x 4 Hz scans (radius 8, ring of 10 around you) + world ticks per second
                (default 48 zones, 10 s; budget 1 ms per tick - spec 3.9).                                                      (U10)
  p14           your rune sections -11 / -12 + your SkyyProfiles profile key: run, /profiles switch, run again.               (U5)
  p15           Mana: your value / max, the Mana stat type's own max (Mana.json; 0.7 = 100), compare with /skills mana.       (U9)
  info          the chain-event hook, the section ids, and the BUILD-TIME desk reads (U1 codec, U7 ids, runes, keywords, Mana).
  stats | stop  (stop also takes back every probe-made rune that is still the probe's exact copy)
  p3 ends a running p1 cancel first (otherwise the rune key press of the U6 test would be cancelled).

DESK READS AT BUILD TIME (printed + shipped as /aprobe info lines; ids and numbers only, nothing vanilla is copied):
  - every rune item of the release Assets.zip (Core: Slot / Cost / CostType / Cooldown / AbilityKeywords / Weapons / Cast; Support:
    RequiresAny / RequiresAll / ExcludesAny), the keyword assets (Server/Abilities/Keywords), Mana.json Max;
  - the release codec: CoreItemAbility HAS a "Weapons" key (weapon TAG list) and canUseWith = held item has an ItemWeapon block AND (no
    Weapons tags, or one matching tag) - read from the jar's bytecode, so the spec's "no Weapons field" (U1) is corrected here;
  - TriggerCooldownInteraction uses the rune's Cast root id as the cooldown id (bytecode) = the id P3 must use;
  - InteractionManager.syncStart / executeChain0 fire InteractionChainStartEvent and on a cancel send the client a cancel packet (bytecode);
  - the SkyyArmory SET jar's Mage / Priest weapons that carry a Weapon block (a rune is usable with them only then);
  - U7: the Fireball impact / frost effect ids the B2 round wants exist under those names.

ENGINE PATHS: every member is probed at build time (B.probe + exact descriptors below). Systems: AbTick (EntityTickingSystem on Player,
not parallel, returns at once while no probe is armed), AbChainSys (EntityEventSystem<InteractionChainStartEvent> - the vanilla
CheckInteractionChainStartSystem / AbilityChargeMeleeAttackSystem shape), AbInvSys (EntityEventSystem<InventoryChangeEvent> - SkyyGear's
GearInvSys shape). Every hook returns at once while STATES is empty. World thread only; no disk I/O at all; no saved data.
"""
import sys, os, json, zipfile, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

if "--deploy" in sys.argv:
    raise SystemExit("SkyyAbilityProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyyabilityprobe.admin"
PKG = "com.skyy.abilprobe"
N = {"P13_R": 8.0, "P13_HZ": 4.0, "P13_RING": 10.0, "P13_LIMIT_US": 1000.0}

az = zipfile.ZipFile(ASSETS)
NAMES = az.namelist()
NAMESET = set(NAMES)


def vanilla_json(path):
    return json.loads(az.read(path).decode("utf-8-sig"))


def ascii_line(s, n=600):
    return re.sub(r"[^\x20-\x7e]", "?", str(s))[:n]


def lst(v):
    return ",".join(str(x) for x in v) if isinstance(v, list) and v else "-"


# ---------------- desk reads (Assets.zip, read-only)
DESK = []
MANA_MAX = vanilla_json("Server/Entity/Stats/Mana.json").get("Max") if "Server/Entity/Stats/Mana.json" in NAMESET else None
DESK.append("P15 desk: Server/Entity/Stats/Mana.json Max = %s (vanilla 0.7 pool; SkyySkills 0.4.31 overrides it)" % MANA_MAX)
CORE, SUPP = [], []
for _n in sorted(NAMES):
    if not (_n.startswith("Server/Item/Items/") and _n.endswith(".json")):
        continue
    try:
        _d = vanilla_json(_n)
    except Exception:
        continue
    _ab = _d.get("Ability") if isinstance(_d, dict) else None
    if not isinstance(_ab, dict):
        continue
    _id = _n.rsplit("/", 1)[1][:-5]
    if _ab.get("Slot") == "Core":
        CORE.append("%s (cost %s %s, cooldown %s s, keywords %s, weapons %s, cast %s)" % (
            _id, _ab.get("Cost"), _ab.get("CostType"), _ab.get("Cooldown"), lst(_ab.get("AbilityKeywords")), lst(_ab.get("Weapons")),
            _ab.get("Cast")))
    else:
        SUPP.append("%s (requires any %s, all %s, excludes %s)" % (_id, lst(_ab.get("RequiresAnyAbilityKeyword")),
                                                                  lst(_ab.get("RequiresAllAbilityKeywords")),
                                                                  lst(_ab.get("ExcludesAnyAbilityKeyword"))))
if not CORE:
    raise SystemExit("no Core rune in Assets.zip - this is not the Hytale 0.7 release (the probe is 0.7-only)")
KEYWORDS = sorted(n.rsplit("/", 1)[1][:-5] for n in NAMES if n.startswith("Server/Abilities/Keywords/") and n.endswith(".json"))
for i in range(0, len(CORE), 3):
    DESK.append("P1 desk: Core runes %d-%d of %d: %s" % (i + 1, min(i + 3, len(CORE)), len(CORE), "; ".join(CORE[i:i + 3])))
for i in range(0, len(SUPP), 5):
    DESK.append("P1 desk: Support runes %d-%d of %d: %s" % (i + 1, min(i + 5, len(SUPP)), len(SUPP), "; ".join(SUPP[i:i + 5])))
DESK.append("P1 desk: %d ability keywords are ASSETS (Server/Abilities/Keywords/<id>.json): %s - a class keyword like SkyyMage needs its "
            "own keyword file in the B2 asset pack" % (len(KEYWORDS), ", ".join(KEYWORDS)))
# U7: the ids the B2 round wants to reuse
U7 = []
for label, needle in (("Fireball impact", "Ability_Fireball_Impact"), ("Fireball cast", "Ability_Fireball_Cast"),
                      ("Fireball projectile config", "Projectile_Config_Ability_Fireball"), ("cast particle", "Fireball_Cast_Charge"),
                      ("camera shake", "Ability_Cast_Generic")):
    hits = sorted(n for n in NAMES if n.rsplit("/", 1)[-1].split(".")[0] == needle)
    if not hits:      # spec section 10 U7: a missing id = the build stops
        raise SystemExit("U7: the %s id %s is MISSING from the release Assets.zip - the B2 round cannot reuse it" % (label, needle))
    U7.append("%s %s: %s" % (label, needle, hits[0]))
_frost = sorted(n.rsplit("/", 1)[1].split(".")[0] for n in NAMES if n.startswith("Server/Entity/Effects/") and
                re.search(r"(?i)freez|frost|chill|slow", n.rsplit("/", 1)[1]))
if not _frost:
    raise SystemExit("U7: no frost / chill / freeze / slow effect under Server/Entity/Effects/ in the release Assets.zip")
DESK.append("U7 desk: " + "; ".join(U7))
DESK.append("U7 desk: frost / slow effects: %s" % ", ".join(_frost[:10]))      # own line: the ids line alone is near the 600-char cap
# the SkyyArmory SET jar's magic weapons (read-only project file): a Core rune is usable only with a held item that has a Weapon block
_set = {}
for _l in open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8"):
    for _m in re.finditer(r'\("(Skyy\w+)", "([\d.]+)"\)', _l):
        _set.setdefault(_m.group(1), _m.group(2))
_arm = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-%s.jar" % _set.get("SkyyArmory", "?"))
if os.path.isfile(_arm):
    _az = zipfile.ZipFile(_arm)
    _fam = {}
    for _n in _az.namelist():
        if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
            _id = _n.rsplit("/", 1)[1][:-5]
            _k = "staff" if "_Staff_" in _id and "_Bo_" not in _id else "spellbook" if "_Spellbook_" in _id else "wand" if "_Wand_" in _id else None
            if _k:
                _d = json.loads(_az.read(_n).decode("utf-8-sig"))
                _a, _b = _fam.get(_k, (0, 0))
                _fam[_k] = (_a + (1 if "Weapon" in _d else 0), _b + 1)
    DESK.append("U1 desk: SkyyArmory %s magic weapons WITH a Weapon block (canUseWith needs one): %s" % (
        _set.get("SkyyArmory"), ", ".join("%s %d of %d" % (k, v[0], v[1]) for k, v in sorted(_fam.items()))))
else:
    DESK.append("U1 desk: SkyyArmory SET jar not found (%s) - hold a staff and read the p1 / p4 canUseWith line instead" % _arm)

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE,
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
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "ABS": "com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots",
    "RNB": "com.hypixel.hytale.server.core.inventory.InventoryComponent$RuneBag",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "TXN": "com.hypixel.hytale.server.core.inventory.transaction.Transaction",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "IAB": "com.hypixel.hytale.server.core.asset.type.item.config.ItemAbility",
    "CIA": "com.hypixel.hytale.server.core.asset.type.item.config.CoreItemAbility",
    "SIA": "com.hypixel.hytale.server.core.asset.type.item.config.SupportItemAbility",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "ESTT": "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "V3D": "org.joml.Vector3d",
    "TU": "com.hypixel.hytale.server.core.util.TargetUtil",
    "ICE": "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent",
    "ICSE": "com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent",
    "ICTX": "com.hypixel.hytale.server.core.entity.InteractionContext",
    "IMGR": "com.hypixel.hytale.server.core.entity.InteractionManager",
    "IMOD": "com.hypixel.hytale.server.core.modules.interaction.InteractionModule",
    "CDH": "com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler",
    "CDN": "com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler$Cooldown",
    "MSC": "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "MST": "com.hypixel.hytale.protocol.MovementStates",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "getComponentType"), (T["MSG"], "raw"), (T["PLA"], "getComponentType"),
             (T["INVC"], "getItemInHand"), (T["INVC"], "getInventory"), (T["INVC"], "ABILITIES_SECTION_ID"), (T["INVC"], "RUNE_BAG_SECTION_ID"),
             (T["ABS"], "getComponentType"), (T["RNB"], "getComponentType"),
             (T["IC"], "getCapacity"), (T["IC"], "getItemStack"), (T["IC"], "addItemStackToSlot"), (T["IC"], "removeItemStackFromSlot"),
             (T["IS"], "getItemId"), (T["IS"], "isEmpty"), (T["IS"], "getQuantity"), (T["IS"], "getItem"), (T["TXN"], "succeeded"),
             (T["ITM"], "getAbility"), (T["ITM"], "getWeapon"), (T["ITM"], "getAssetMap"),
             (T["CIA"], "getCost"), (T["CIA"], "getCostType"), (T["CIA"], "getCooldownS"), (T["CIA"], "getAbilityKeywords"),
             (T["CIA"], "getCastRootId"), (T["CIA"], "canUseWith"), (T["SIA"], "getRequiresAnyAbilityKeyword"),
             (T["SIA"], "getRequiresAllAbilityKeywords"), (T["SIA"], "getExcludesAnyAbilityKeyword"),
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESV"], "get"), (T["ESV"], "getMax"), (T["DST"], "getMana"),
             (T["ESTT"], "getAssetMap"), (T["ESTT"], "getMax"), (T["ETS"], "tick"), (T["ETS"], "isParallel"), (T["ACH"], "getReferenceTo"),
             (T["TC"], "getComponentType"), (T["TC"], "getPosition"), (T["TU"], "getAllEntitiesInSphere"),
             (T["ICE"], "getComponentType"), (T["ICSE"], "getType"), (T["ICSE"], "getContext"), (T["ICSE"], "getRootInteractionId"),
             (T["ICSE"], "setCancelled"), (T["ICSE"], "isCancelled"), (T["ICTX"], "getHeldItem"), (T["ICTX"], "getHeldItemSectionId"),
             (T["ICTX"], "getHeldItemSlot"), (T["IMOD"], "get"), (T["IMOD"], "getInteractionManagerComponent"),
             (T["IMGR"], "DEFAULT_CHARGE_TIMES"), (T["CDH"], "getCooldown"), (T["CDN"], "getCooldown"), (T["CDN"], "setCooldownMax"),
             (T["CDN"], "resetCooldown"), (T["CDN"], "getCharges"), (T["MSC"], "getComponentType"), (T["MSC"], "getMovementStates"),
             ("com.hypixel.hytale.component.Ref", "isValid"),
             (PB, "getCommandRegistry"), (PB, "getEntityStoreRegistry"), (PB, "getLogger"), (PB, "shutdown")):
    B.probe(pool, c, m)


def _d(cn):
    return "L" + cn.replace(".", "/") + ";"


_V = _d(T["V3D"])
for c, m, d in ((T["TU"], "getAllEntitiesInSphere", "(" + _V + "D" + _d(T["CAC"]) + ")Ljava/util/List;"),
                (T["CDH"], "getCooldown", "(Ljava/lang/String;F[FZZ)" + _d(T["CDN"])),
                (T["CDH"], "getCooldown", "(Ljava/lang/String;)" + _d(T["CDN"])),
                (T["CDN"], "setCooldownMax", "(F)V"), (T["CDN"], "resetCooldown", "()V"), (T["CDN"], "getCooldown", "()F"),
                (T["CIA"], "canUseWith", "(" + _d(T["IS"]) + ")Z"), (T["CIA"], "getAbilityKeywords", "()[Ljava/lang/String;"),
                (T["ICSE"], "getRootInteractionId", "()Ljava/lang/String;"), (T["ICSE"], "setCancelled", "(Z)V"),
                (T["ICTX"], "getHeldItemSectionId", "()I"), (T["ICTX"], "getHeldItemSlot", "()B"),
                (T["INVC"], "getItemInHand", "(" + _d(T["CAC"]) + _d(T["REF"]) + ")" + _d(T["IS"])),
                (T["IC"], "addItemStackToSlot", "(S" + _d(T["IS"]) + ")Lcom/hypixel/hytale/server/core/inventory/transaction/ItemStackSlotTransaction;"),
                (T["IC"], "removeItemStackFromSlot", "(S)Lcom/hypixel/hytale/server/core/inventory/transaction/SlotTransaction;"),
                (T["IS"], "<init>", "(Ljava/lang/String;I)V"), (T["ABS"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;")):
    try:
        if m == "<init>":
            pool.get(c).getConstructor(d)
        else:
            pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
for c, f in ((T["IMGR"], "cooldownHandler"), (T["CDH"], "cooldowns"), (T["CDN"], "remainingCooldown")):
    try:
        pool.get(c).getDeclaredField(f)
    except Exception as _e:
        raise SystemExit("private engine field %s.%s is gone (P3 reads it by reflection): %s" % (c, f, _e))
for c in (T["ICSE"], T["ICE"]):
    if not pool.get(c).subtypeOf(pool.get(T["EV"])):
        raise SystemExit("%s is no EcsEvent" % c)
if not pool.get(T["ICSE"]).subtypeOf(pool.get("com.hypixel.hytale.component.system.CancellableEcsEvent")):
    raise SystemExit("InteractionChainStartEvent is no longer cancellable - P1 cancel would mean nothing")


# ---- bytecode desk reads (the release jar, read-only): what the engine does with the chain event and the cooldown id
def calls(cls, meth):
    cc = pool.get(cls)
    out = []
    for mi in cc.getClassFile2().getMethods():
        if str(mi.getName()) != meth or mi.getCodeAttribute() is None:
            continue
        cp, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
        while it.hasNext():
            p = it.next()
            op = it.byteAt(p)
            if op in (0xb6, 0xb7, 0xb8, 0xb9):
                i = it.u16bitAt(p + 1)
                if op == 0xb9:
                    out.append(str(cp.getInterfaceMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cp.getInterfaceMethodrefName(i)))
                else:
                    out.append(str(cp.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cp.getMethodrefName(i)))
    return out


_sync = calls(T["IMGR"], "syncStart")
_i = _sync.index("InteractionChainStartEvent.isCancelled") if "InteractionChainStartEvent.isCancelled" in _sync else -1
if _i < 0 or "InteractionManager.sendCancelPacket" not in _sync[_i:_i + 8]:
    raise SystemExit("InteractionManager.syncStart no longer sends a cancel packet after a cancelled InteractionChainStartEvent")
_trig = calls("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.TriggerCooldownInteraction", "firstRun")
if "CoreItemAbility.getCastRootId" not in _trig or "CoreItemAbility.getCooldownS" not in _trig:
    raise SystemExit("TriggerCooldownInteraction no longer keys the rune cooldown by its Cast root id")
_use = calls(T["CIA"], "canUseWith")
if "Item.getWeapon" not in _use:
    raise SystemExit("CoreItemAbility.canUseWith no longer checks the held item's Weapon block")
_fields = sorted(str(f.getName()) for f in pool.get(T["CIA"]).getDeclaredFields())
DESK.append("U1 desk (release jar): CoreItemAbility fields %s; canUseWith = the hand item has a Weapon block AND (no Weapons tags or one "
            "matching tag) - so a rune with no Weapons works with ANY weapon, never with food / tools / an empty hand (then the key falls "
            "through to the hand item's own Ability2 / 3)" % ", ".join(f for f in _fields if not f.isupper()))
DESK.append("U3 / U6 desk (release jar): a cancelled InteractionChainStartEvent -> syncStart sends the client a cancel packet; the rune "
            "cooldown is armed by TriggerCooldownInteraction inside the cast chain, keyed by the rune's Cast root id (cooldown = the "
            "rune's Cooldown x the cast's Cooldown attribute) - a chain cancelled at its start never reaches it on the server")
for _l in DESK:
    print(_l)
for _l in DESK:
    if len(_l) >= 600:      # ascii_line would cut it: an info line must never lose its tail silently (the U7 frost list once did)
        raise SystemExit("desk line too long (%d chars) - split it: %s" % (len(_l), _l[:120]))
DESK = [ascii_line(x) for x in DESK]

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
    return json.dumps(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


def jd(v):
    return repr(float(v))


# ---- AbLog: server log + chat. SINK (harness hook, null in game) also receives every chat line.
log = mk("AbLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List SINK;")
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyAbilityProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyAbilityProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s) {
  String who = "";
  try { if (pr != null) who = "to " + pr.getUsername() + ": "; } catch (Throwable t) { who = ""; }
  info(who + s);
  try { if (SINK != null) SINK.add(s); } catch (Throwable t) { }
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[AbilityProbe] " + s)); } catch (Throwable t) { }
}""")

# ---- AbLogic: pure functions (no engine objects) - the harness calls each directly
lg = mk("AbLogic")
M(lg, r"""
public static String f1(double v) {
  if (v != v) return "?";
  long t = Math.round(v * 10.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = 0L - t;
  return sign + (t / 10L) + "." + (t % 10L);
}""")
M(lg, r"""
public static int number(String s, int dflt, int lo, int hi) {
  int n = dflt;
  try { n = Integer.parseInt(s == null ? "" : s.trim()); } catch (Throwable t) { n = dflt; }
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
M(lg, r"""
public static double dnum(String s, double dflt, double lo, double hi) {
  double n = dflt;
  try { n = Double.parseDouble(s == null ? "" : s.trim()); } catch (Throwable t) { n = dflt; }
  if (n != n) n = dflt;
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
M(lg, r"""
public static String word(String[] w, int i) {
  if (w == null || i < 0 || i >= w.length || w[i] == null) return null;
  String t = w[i].trim();
  return t.length() == 0 ? null : t;
}""")
M(lg, r"""
public static String low(String s) {
  return s == null ? null : s.toLowerCase(java.util.Locale.ROOT);
}""")
M(lg, r"""
public static double perSec(long count, long ms) {
  if (ms <= 0L) return 0.0;
  return (double) count * 1000.0 / (double) ms;
}""")
M(lg, r"""
public static double[] ring(double cx, double cz, double r, int i, int n) {
  if (n < 1) n = 1;
  double a = 2.0 * Math.PI * (double) i / (double) n;
  return new double[] { cx + r * Math.cos(a), cz + r * Math.sin(a) };
}""")
M(lg, r"""
public static String budget(double usPerTick, double limitUs) {
  return (usPerTick < limitUs ? "PASS" : "OVER") + " (" + f1(usPerTick) + " us per tick, budget " + f1(limitUs) + ")";
}""")
M(lg, r"""
public static boolean slotOk(int s, int cap) {
  return s >= 0 && s < cap;
}""")
# chain type text -> 1 = a rune key (Ability2 / Ability3), 0 = anything else
M(lg, r"""
public static int kind(String type) {
  if ("Ability2".equals(type) || "Ability3".equals(type)) return 1;
  return 0;
}""")
M(lg, r"""
public static String yn(boolean b) {
  return b ? "y" : "n";
}""")
M(lg, r"""
public static String join(String[] a) {
  if (a == null || a.length == 0) return "-";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < a.length; i++) {
    if (i > 0) b.append(",");
    b.append(a[i]);
  }
  return b.toString();
}""")
M(lg, r"""
public static String moveText(boolean known, boolean crouch, boolean sprint, boolean roll, boolean ground) {
  if (!known) return "movement unknown";
  return "crouch " + yn(crouch) + ", sprint " + yn(sprint) + ", roll " + yn(roll) + ", in air " + yn(!ground);
}""")
# the 1 s cancel check: Mana must not have dropped and the server must hold no running cooldown for the cancelled root
M(lg, r"""
public static String cancelVerdict(double before, double after, double cdLeft) {
  boolean spent = after + 0.01 < before;
  boolean cd = cdLeft > 0.0;
  String h = (!spent && !cd) ? "PASS: nothing spent, no server cooldown" : "FAIL:" + (spent ? " Mana went DOWN (the cancelled cast was paid)" : "") + (cd ? " a server cooldown is running (" + f1(cdLeft) + " s left)" : "");
  return h + " - Mana " + f1(before) + " -> " + f1(after) + " 1 s later. Did you see a cast animation or a cooldown fill on the HUD slot?";
}""")
M(lg, r"""
public static String p15Text(double value, double max, double typeMax) {
  String a = "P15: your Mana " + f1(value) + " / " + f1(max) + "; the Mana stat type's own max (Mana.json) " + f1(typeMax) + ".";
  String b = (typeMax > 0.0 && max >= typeMax) ? " Compare: your max is at least the vanilla max - see if /skills mana shows the same (U9)." : " Expect: /skills mana shows the same max (the vanilla " + f1(typeMax) + " is not added on top - U9).";
  return a + b;
}""")
# one cooldown row: id, max, remaining (-1 = unreadable), charge count (-1 = none)
M(lg, r"""
public static String cdRow(String id, double max, double left, int charges) {
  return id + ": max " + f1(max) + " s, " + (left < 0.0 ? "remaining unreadable" : left > 0.0 ? f1(left) + " s left" : "ready") + (charges >= 0 ? ", " + charges + " charge slot(s)" : "");
}""")

# ---- AbState: one player's probe state (world thread; one per player in AbCmds.STATES). EVERY probe field is reset by AbCmds.clear
STATE_FIELDS = [
    # the running timed probe: mode 0 none, else 1 (p1), 4 (p4 watch), 13 (p13); every hook also checks now < modeUntil
    ("int", "mode"), ("long", "modeUntil"), ("long", "armedAt"), ("int", "lines"), ("int", "logOnly"),
    # P1
    ("boolean", "cancel"), ("int", "chains"), ("int", "chainAb"), ("int", "chainOther"), ("int", "cancelled"), ("int", "cancelFail"),
    ("long", "p1CheckAt"), ("double", "p1Mana"), ("String", "p1Root"),
    # P4 watch
    ("int", "invSlots"), ("int", "invBag"), ("int", "invOther"),
    # P13
    ("int", "zones"), ("double", "p13Acc"), ("int", "p13Idx"), ("long", "p13Ticks"), ("long", "p13Scans"), ("long", "p13Ents"),
    ("long", "p13Ns"), ("long", "p13Max"),
]
KEEP_FIELDS = [("java.util.UUID", "u"), ("@REF@", "ref"), ("Object", "st"), ("long", "ns"), ("long", "nsMax"), ("long", "ticks")]
sta = mk("AbState")
for t, n in KEEP_FIELDS + STATE_FIELDS:
    F(sta, "public %s %s;" % (t, n))
C(sta, r"""
public AbState(java.util.UUID u, @REF@ r, Object st) {
  this.u = u;
  this.ref = r;
  this.st = st;
  this.p1Root = "";
}""")


def _reset(t, n):
    if t == "String":
        return '  s.%s = "";' % n
    if t == "boolean":
        return "  s.%s = false;" % n
    if t == "double":
        return "  s.%s = 0.0;" % n
    if t == "long":
        return "  s.%s = 0L;" % n
    return "  s.%s = 0;" % n


# ---- AbCmds: engine glue + every probe (world thread: AbstractPlayerCommand.execute, the tick, the event systems)
cmds = mk("AbCmds")
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          # P4: the runes the probe itself put ("<uuid> <slot>" -> item id) - only those may be taken back
          "public static final java.util.concurrent.ConcurrentHashMap PUT = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile boolean CHAIN_ON = false;",
          "public static volatile String CHAIN_WHY = \"not registered\";",
          "public static final String[] DESK = %s;" % jarr(DESK)):
    F(cmds, f)
for k, v in sorted(N.items()):
    F(cmds, "public static final double %s = %s;" % (k, jd(v)))
M(cmds, r"""
public static void tell(@PR@ pr, String s) { @PKG@.AbLog.tell(pr, s); }""")
M(cmds, r"""
public static String f1(double v) { return @PKG@.AbLogic.f1(v); }""")
M(cmds, r"""
public static java.util.Map bridge() {
  Object b = System.getProperties().get("skyy.bridge");
  if (b instanceof java.util.Map) return (java.util.Map) b;
  return java.util.Collections.EMPTY_MAP;
}""")
M(cmds, r"""
public static @PR@ prOf(@CAC@ acc, @REF@ r) {
  try { if (acc == null || r == null || !r.isValid()) return null; return (@PR@) acc.getComponent(r, @PR@.getComponentType()); } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @V3D@ pos(@CAC@ acc, @REF@ r) {
  try {
    @TC@ tc = (@TC@) acc.getComponent(r, @TC@.getComponentType());
    return tc == null ? null : tc.getPosition();
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static java.util.List near(@CAC@ acc, double x, double y, double z, double r) {
  try {
    java.util.List l = @TU@.getAllEntitiesInSphere(new @V3D@(x, y, z), r, acc);
    return l == null ? new java.util.ArrayList() : l;
  } catch (Throwable t) { @PKG@.AbLog.warn("area query failed: " + t); return new java.util.ArrayList(); }
}""")
# {value, max} of one stat (null = unreadable)
M(cmds, r"""
public static double[] stat(@CAC@ acc, @REF@ r, int idx) {
  try {
    if (idx < 0 || r == null) return null;
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return null;
    @ESV@ v = m.get(idx);
    if (v == null) return null;
    return new double[] { (double) v.get(), (double) v.getMax() };
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @IC@ slotsOf(@CAC@ acc, @REF@ r) {
  try {
    @ABS@ a = (@ABS@) acc.getComponent(r, @ABS@.getComponentType());
    return a == null ? null : a.getInventory();
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @IC@ bagOf(@CAC@ acc, @REF@ r) {
  try {
    @RNB@ a = (@RNB@) acc.getComponent(r, @RNB@.getComponentType());
    return a == null ? null : a.getInventory();
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @IS@ stackAt(@IC@ c, int i) {
  try {
    @IS@ s = c.getItemStack((short) i);
    return s == null || s.isEmpty() ? null : s;
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static String slotText(@IC@ c, int i) {
  try {
    @IS@ s = c.getItemStack((short) i);
    return s == null || s.isEmpty() ? "-" : s.getItemId() + (s.getQuantity() > 1 ? " x" + s.getQuantity() : "");
  } catch (Throwable t) { return "?"; }
}""")
M(cmds, r"""
public static int cap(@IC@ c) {
  try { return c == null ? 0 : (int) c.getCapacity(); } catch (Throwable t) { return 0; }
}""")
M(cmds, r"""
public static String slots(@IC@ c, boolean onlyFilled, int max) {
  if (c == null) return "none";
  int n0 = cap(c);
  StringBuilder b = new StringBuilder();
  int n = 0;
  for (int i = 0; i < n0 && n < max; i++) {
    String one = slotText(c, i);
    if (onlyFilled && "-".equals(one)) continue;
    if (b.length() > 0) b.append(", ");
    b.append(i).append(" ").append(one);
    n++;
  }
  return "(" + n0 + " slots) " + (b.length() == 0 ? "all empty" : b.toString());
}""")
M(cmds, r"""
public static String txText(Object tx) {
  if (tx == null) return "no transaction";
  String ok = "";
  try { if (tx instanceof @TXN@) ok = " succeeded=" + ((@TXN@) tx).succeeded(); } catch (Throwable t) { ok = " succeeded=?"; }
  return tx.getClass().getSimpleName() + ok;
}""")
M(cmds, r"""
public static @IAB@ abilOf(@IS@ s) {
  try {
    if (s == null) return null;
    @ITM@ it = s.getItem();
    return it == null ? null : it.getAbility();
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static boolean hasWeapon(@IS@ s) {
  try { return s != null && s.getItem() != null && s.getItem().getWeapon() != null; } catch (Throwable t) { return false; }
}""")
# a rune's Ability data as text (Core / Support), or why there is none
M(cmds, r"""
public static String abilText(@IS@ s) {
  if (s == null) return "empty";
  @IAB@ a = abilOf(s);
  if (a instanceof @CIA@) {
    @CIA@ c = (@CIA@) a;
    return "Core rune: cost " + f1((double) c.getCost()) + " " + c.getCostType() + ", cooldown " + f1((double) c.getCooldownS()) + " s, keywords " + @PKG@.AbLogic.join(c.getAbilityKeywords()) + ", cast " + c.getCastRootId();
  }
  if (a instanceof @SIA@) {
    @SIA@ p = (@SIA@) a;
    return "Support rune: requires any " + @PKG@.AbLogic.join(p.getRequiresAnyAbilityKeyword()) + ", all " + @PKG@.AbLogic.join(p.getRequiresAllAbilityKeywords()) + ", excludes " + @PKG@.AbLogic.join(p.getExcludesAnyAbilityKeyword());
  }
  return "not a rune (" + s.getItemId() + ")";
}""")
# can this Core rune be cast with the hand item (the engine's own rule)?
M(cmds, r"""
public static String useText(@IS@ rune, @IS@ hand) {
  @IAB@ a = abilOf(rune);
  if (!(a instanceof @CIA@)) return "";
  String hid = hand == null ? "empty hand" : hand.getItemId();
  boolean ok = false;
  try { ok = ((@CIA@) a).canUseWith(hand); } catch (Throwable t) { ok = false; }
  return "; with " + hid + " (Weapon block " + @PKG@.AbLogic.yn(hasWeapon(hand)) + "): canUseWith " + (ok ? "YES" : "NO - the key falls through to the hand item");
}""")
M(cmds, r"""
public static @IS@ hand(@CAC@ acc, @REF@ r) {
  try { return @INVC@.getItemInHand(acc, r); } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static String moveText(@CAC@ acc, @REF@ r) {
  try {
    @MSC@ c = (@MSC@) acc.getComponent(r, @MSC@.getComponentType());
    @MST@ m = c == null ? null : c.getMovementStates();
    if (m == null) return @PKG@.AbLogic.moveText(false, false, false, false, true);
    return @PKG@.AbLogic.moveText(true, m.crouching, m.sprinting, m.rolling, m.onGround);
  } catch (Throwable t) { return @PKG@.AbLogic.moveText(false, false, false, false, true); }
}""")
# ---- the CooldownHandler (P3 + the P1 cancel check): private fields, read by reflection (no engine getter exists)
M(cmds, r"""
public static Object field(Object o, String cls, String name) {
  if (o == null) return null;
  try {
    java.lang.reflect.Field f = Class.forName(cls).getDeclaredField(name);
    f.setAccessible(true);
    return f.get(o);
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static @CDH@ handler(@CAC@ acc, @REF@ r) {
  try {
    Object im = acc.getComponent(r, @IMOD@.get().getInteractionManagerComponent());
    Object h = field(im, "@IMGR@", "cooldownHandler");
    return h instanceof @CDH@ ? (@CDH@) h : null;
  } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static double left(@CDN@ c) {
  Object v = field(c, "@CDN@", "remainingCooldown");
  return v instanceof Float ? (double) ((Float) v).floatValue() : -1.0;
}""")
M(cmds, r"""
public static String cdLine(String id, @CDN@ c) {
  if (c == null) return id + ": no cooldown";
  int ch = -1;
  try { float[] a = c.getCharges(); ch = a == null ? -1 : a.length; } catch (Throwable t) { ch = -1; }
  return @PKG@.AbLogic.cdRow(id, (double) c.getCooldown(), left(c), ch);
}""")
M(cmds, r"""
public static double cdLeft(@CDH@ h, String id) {
  if (h == null || id == null || id.length() == 0) return 0.0;
  try {
    @CDN@ c = h.getCooldown(id);
    if (c == null) return 0.0;
    double l = left(c);
    return l < 0.0 ? 0.0 : l;
  } catch (Throwable t) { return 0.0; }
}""")
M(cmds, r"""
public static @PKG@.AbState state(@PR@ pr, @REF@ r, Object st) {
  java.util.UUID u = pr.getUuid();
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(u);
  if (s == null || s.st != st) {
    s = new @PKG@.AbState(u, r, st);
    STATES.put(u, s);
  }
  s.ref = r;
  return s;
}""")
# the running probe of that player, or null. EVERY hook goes through this: no window, no action.
M(cmds, r"""
public static @PKG@.AbState active(@PR@ pr, int mode, long now) {
  if (pr == null) return null;
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(pr.getUuid());
  if (s == null || s.mode == 0 || now >= s.modeUntil) return null;
  if (mode >= 0 && s.mode != mode) return null;
  return s;
}""")
# ---- THE RESET RULE: every probe field back to rest (generated from the AbState field list - nothing can be forgotten)
M(cmds, "public static void clear(@PKG@.AbState s) {\n  if (s == null) return;\n" + "\n".join(_reset(t, n) for t, n in STATE_FIELDS) + "\n}")
# ---- arming a timed probe (pure: the harness runs it): clear() FIRST, then the probe's own fields. null = armed.
M(cmds, r"""
public static String plan(@PKG@.AbState s, String[] w, long now) {
  clear(s);
  String t = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 0));
  String a1 = @PKG@.AbLogic.word(w, 1);
  String a2 = @PKG@.AbLogic.word(w, 2);
  String l1 = @PKG@.AbLogic.low(a1);
  s.armedAt = now;
  int secs = 0;
  if ("p1".equals(t)) { s.mode = 1; secs = 60; s.cancel = "cancel".equals(l1); }
  else if ("p4".equals(t) && "watch".equals(l1)) { s.mode = 4; secs = 60; }
  else if ("p13".equals(t)) { s.mode = 13; s.zones = @PKG@.AbLogic.number(a1, 48, 1, 256); secs = @PKG@.AbLogic.number(a2, 10, 3, 60); }
  else { clear(s); return "Unknown probe - /aprobe lists them."; }
  s.modeUntil = now + (long) secs * 1000L;
  return null;
}""")
# ---- the summary of the running probe (numbers only - safe after a world change)
M(cmds, r"""
public static void summary(@PKG@.AbState s, @PR@ pr, String why) {
  if (s == null || s.mode == 0) return;
  long ms = System.currentTimeMillis() - s.armedAt;
  if (ms < 1L) ms = 1L;
  String h = "P" + s.mode + " " + (why == null ? "done" : why) + ": ";
  int m = s.mode;
  if (m == 1) tell(pr, h + s.chains + " chain starts (" + s.chainAb + " Ability2/3, " + s.chainOther + " other; " + s.logOnly + " lines in the log only)" + (s.cancel ? ", " + s.cancelled + " cancelled, " + s.cancelFail + " cancel failures" : "") + ". Expect: each rune key printed an Ability2 / Ability3 line" + (s.cancel ? " and the cancelled casts showed no animation, no cooldown fill, no Mana spent." : "."));
  else if (m == 4) tell(pr, h + s.invSlots + " InventoryChangeEvents on the AbilitySlots, " + s.invBag + " on the RuneBag, " + s.invOther + " on other sections. Expect: your drag in the Runebinder's Lattice printed an AbilitySlots line.");
  else if (m == 13) {
    double tps = @PKG@.AbLogic.perSec(s.p13Ticks, ms);
    double us = s.p13Ticks == 0L ? 0.0 : (double) s.p13Ns / (double) s.p13Ticks / 1000.0;
    tell(pr, h + s.zones + " zones x " + f1(P13_HZ) + " Hz: " + s.p13Scans + " scans (" + f1(@PKG@.AbLogic.perSec(s.p13Scans, ms)) + " per s), " + f1(s.p13Scans == 0L ? 0.0 : (double) s.p13Ents / (double) s.p13Scans) + " entities per scan, max " + s.p13Max / 1000L + " us in one tick; world ticks per second " + f1(tps) + " (spec assumes 30). " + @PKG@.AbLogic.budget(us, P13_LIMIT_US));
  }
}""")
M(cmds, r"""
public static void finish(@PKG@.AbState s, @PR@ pr, String why) {
  summary(s, pr, why);
  clear(s);
}""")
M(cmds, r"""
public static void help(@PR@ pr) {
  tell(pr, "Ability probe for Hytale 0.7 (op only, throwaway). One timed probe at a time; results also go to the server log.");
  tell(pr, "/aprobe p1 [cancel] | p3 [set <id> <secs> | clear <id>] | p4 read | p4 watch | p4 put <slot> <itemId> | p4 take <slot> | p4 bad <slot>");
  tell(pr, "/aprobe p13 [zones] [secs] | p14 | p15 | info | stats | stop");
}""")
M(cmds, r"""
public static void info(@PR@ pr) {
  tell(pr, "Info: InteractionChainStartEvent hook " + (CHAIN_ON ? "LISTENING" : "OFF (" + CHAIN_WHY + ")") + "; ability section " + @INVC@.ABILITIES_SECTION_ID + ", rune bag section " + @INVC@.RUNE_BAG_SECTION_ID + "; " + DESK.length + " desk lines follow (build time, release Assets.zip + jar).");
  for (int i = 0; i < DESK.length; i++) tell(pr, DESK[i]);
}""")
M(cmds, r"""
public static void stats(@PR@ pr) {
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(pr.getUuid());
  if (s == null) tell(pr, "No probe state.");
  else tell(pr, "Stats: running P" + s.mode + ", " + s.ticks + " ticks, avg " + (s.ticks == 0L ? 0L : s.ns / s.ticks / 1000L) + " us, max " + s.nsMax / 1000L + " us per tick; " + PUT.size() + " probe-put runes still tracked.");
}""")
# ---- P3: the CooldownHandler (list / set / clear)
M(cmds, r"""
public static void p3(@PR@ pr, @CAC@ st, @REF@ ref, String[] w) {
  @CDH@ h = handler(st, ref);
  if (h == null) { tell(pr, "P3: FAIL - no CooldownHandler on your InteractionManager (private field cooldownHandler unreadable). The SkyyHud widget stays the cooldown display (spec 3.5)."); return; }
  String l1 = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 1));
  String id = @PKG@.AbLogic.word(w, 2);
  if (l1 == null || "list".equals(l1)) {
    Object mo = field(h, "@CDH@", "cooldowns");
    if (!(mo instanceof java.util.Map)) { tell(pr, "P3: the handler's cooldown map is unreadable."); return; }
    java.util.Map map = (java.util.Map) mo;
    tell(pr, "P3: your server CooldownHandler holds " + map.size() + " cooldown(s)" + (map.isEmpty() ? " - cast a vanilla rune, then /aprobe p3 again." : ":"));
    java.util.Iterator it = new java.util.ArrayList(map.entrySet()).iterator();
    int n = 0;
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      Object c = e.getValue();
      String line = "P3 " + cdLine(String.valueOf(e.getKey()), c instanceof @CDN@ ? (@CDN@) c : null);
      n++;
      if (n <= 12) tell(pr, line); else @PKG@.AbLog.info(line);
    }
    return;
  }
  if (id == null) { tell(pr, "Usage: /aprobe p3 set <id> <secs> | /aprobe p3 clear <id> (id = a rune's cast root, e.g. Root_Ability_Fireball)"); return; }
  try {
    if ("set".equals(l1)) {
      double secs = @PKG@.AbLogic.dnum(@PKG@.AbLogic.word(w, 3), 8.0, 0.5, 120.0);
      @CDN@ c = h.getCooldown(id, (float) secs, @IMGR@.DEFAULT_CHARGE_TIMES, true, false);
      c.setCooldownMax((float) secs);
      c.resetCooldown();
      tell(pr, "P3 set: " + cdLine(id, c) + ". Now press that rune's key: does the HUD slot show a fill (U6)? Does the cast go off at once, not at all, or late when the time runs out?");
      return;
    }
    if ("clear".equals(l1)) {
      @CDN@ c = h.getCooldown(id);
      if (c == null) { tell(pr, "P3 clear: " + id + " has no cooldown."); return; }
      c.setCooldownMax(0.0f);
      tell(pr, "P3 clear: " + cdLine(id, c) + ".");
      return;
    }
  } catch (Throwable t) { tell(pr, "P3 " + l1 + " failed: " + t); return; }
  tell(pr, "Usage: /aprobe p3 | p3 set <id> <secs> | p3 clear <id>");
}""")
# ---- P4: the AbilitySlots section -11
M(cmds, r"""
public static void p4(@PR@ pr, @CAC@ st, @REF@ ref, String[] w) {
  @IC@ c = slotsOf(st, ref);
  if (c == null) { tell(pr, "P4: no AbilitySlots on you."); return; }
  int n0 = cap(c);
  String l1 = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 1));
  @IS@ hd = hand(st, ref);
  if (l1 == null || "read".equals(l1)) {
    tell(pr, "P4 AbilitySlots " + slots(c, false, 12) + ". Slot 0 = Use Ability 2, slot 3 = Use Ability 3; 1-2 / 4-5 = their modifiers.");
    for (int i = 0; i < n0 && i < 12; i++) {
      @IS@ s = stackAt(c, i);
      if (s != null) tell(pr, "P4 slot " + i + " " + s.getItemId() + ": " + abilText(s) + useText(s, hd));
    }
    return;
  }
  int slot = @PKG@.AbLogic.number(@PKG@.AbLogic.word(w, 2), -1, -1, 99);
  if (!@PKG@.AbLogic.slotOk(slot, n0)) { tell(pr, "Usage: /aprobe p4 put <slot 0-" + (n0 - 1) + "> <itemId> | take <slot> | bad <slot>"); return; }
  String key = pr.getUuid() + " " + slot;
  try {
    if ("put".equals(l1)) {
      String id = @PKG@.AbLogic.word(w, 3);
      if (id == null) { tell(pr, "Usage: /aprobe p4 put <slot> <itemId> (e.g. Rune_Fireball)"); return; }
      if (@ITM@.getAssetMap().getAsset(id) == null) { tell(pr, "P4 put: no item '" + id + "' is loaded (ids are case-sensitive)."); return; }
      @IS@ made = new @IS@(id, 1);
      @IAB@ ab = abilOf(made);
      if (!(ab instanceof @CIA@) && !(ab instanceof @SIA@)) { tell(pr, "P4 put: " + id + " is not a rune (no Core / Support Ability) - only runes can be put."); return; }
      if (stackAt(c, slot) != null) { tell(pr, "P4 put: slot " + slot + " is not empty (" + slotText(c, slot) + ") - drag it out in the Runebinder's Lattice first."); return; }
      Object tx = c.addItemStackToSlot((short) slot, made);
      @IS@ now = stackAt(c, slot);
      if (now != null && id.equals(now.getItemId())) PUT.put(key, new Object[] { id, now });
      tell(pr, "P4 put " + id + " -> slot " + slot + ": " + txText(tx) + "; slot now " + slotText(c, slot) + ". Next: look at the HUD slot, then die / change world / relog and /aprobe p4 read after each (U8).");
      if (now != null) tell(pr, "P4 put: this is a REAL rune in your saved slots. /aprobe p4 take " + slot + " (or /aprobe stop) takes back ONLY this exact copy; after a relog or profile switch it is a new copy the probe cannot prove is its own - then drag it to your rune bag by hand.");
      return;
    }
    if ("take".equals(l1)) {
      Object[] mine = (Object[]) PUT.get(key);
      @IS@ s = stackAt(c, slot);
      if (s == null) { PUT.remove(key); tell(pr, "P4 take: slot " + slot + " is empty."); return; }
      if (mine == null || mine[1] != s) { tell(pr, "P4 take: slot " + slot + " holds " + s.getItemId() + ", which is not the exact copy the probe put there (never put, moved, relogged or another profile) - it stays; drag it out in the bench if it is the probe's."); return; }
      Object tx = c.removeItemStackFromSlot((short) slot);
      PUT.remove(key);
      tell(pr, "P4 take slot " + slot + " (" + mine[0] + ", probe-made): " + txText(tx) + "; slot now " + slotText(c, slot) + ".");
      return;
    }
    if ("bad".equals(l1)) {
      if (hd == null || hd.isEmpty()) { tell(pr, "P4 bad: hold any NON-rune item (a sword) first."); return; }
      if (abilOf(hd) != null) { tell(pr, "P4 bad: you hold a rune - hold a NON-rune item (a sword)."); return; }
      if (stackAt(c, slot) != null) { tell(pr, "P4 bad: slot " + slot + " is not empty - pick an empty slot."); return; }
      String id = hd.getItemId();
      Object tx = c.addItemStackToSlot((short) slot, new @IS@(id, 1));
      if (stackAt(c, slot) != null) {
        c.removeItemStackFromSlot((short) slot);
        tell(pr, "P4 bad: FAIL - a non-rune (" + id + ") went into slot " + slot + " from code (the slot filter does not guard code writes: the B2 mirror must check items itself). Removed again: " + (stackAt(c, slot) == null ? "yes" : "NO - take it out by hand") + ".");
      } else tell(pr, "P4 bad: PASS - slot " + slot + " refused " + id + " (" + txText(tx) + ").");
      return;
    }
  } catch (Throwable t) { tell(pr, "P4 " + l1 + " failed: " + t); return; }
  tell(pr, "Usage: /aprobe p4 read | watch | put <slot> <itemId> | take <slot> | bad <slot>");
}""")
# ---- /aprobe stop: take back every rune the probe put for this player that is STILL the exact copy it made; forget the rest (they
# are plain vanilla runes now - the player drags them to the rune bag). Returns the result line, or null when nothing was tracked.
M(cmds, r"""
public static String takeBack(@PR@ pr, @CAC@ st, @REF@ ref) {
  String pre = pr.getUuid() + " ";
  java.util.Iterator it = new java.util.ArrayList(PUT.keySet()).iterator();
  @IC@ c = slotsOf(st, ref);
  int taken = 0;
  StringBuilder left = new StringBuilder();
  int tracked = 0;
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(pre)) continue;
    Object[] e = (Object[]) PUT.remove(k);
    if (e == null) continue;
    tracked++;
    int slot = @PKG@.AbLogic.number(k.substring(pre.length()), -1, -1, 99);
    @IS@ s = c == null ? null : stackAt(c, slot);
    boolean ok = false;
    if (s != null && s == e[1]) {
      try { c.removeItemStackFromSlot((short) slot); ok = stackAt(c, slot) == null; } catch (Throwable t) { ok = false; }
    }
    if (ok) taken++;
    else if (s != null && String.valueOf(e[0]).equals(s.getItemId())) { if (left.length() > 0) left.append(", "); left.append("slot ").append(slot).append(" ").append(e[0]); }
  }
  if (tracked == 0) return null;
  return "P4 stop: took back " + taken + " probe-made rune(s)" + (left.length() == 0 ? "." : "; NOT provably the probe's copy, left in place (drag to your rune bag by hand if it is): " + left.toString() + ".");
}""")
# ---- P14: the rune sections across SkyyProfiles profiles
M(cmds, r"""
public static void p14(@PR@ pr, @CAC@ st, @REF@ ref) {
  @IC@ a = slotsOf(st, ref);
  @IC@ b = bagOf(st, ref);
  Object key = bridge().get("profile:key:" + pr.getUuid().toString());
  tell(pr, "P14 profile " + (key == null ? "(no SkyyProfiles key)" : String.valueOf(key)) + ": ability slots -11 " + slots(a, true, 6) + "; rune bag -12 " + slots(b, true, 20) + ".");
  tell(pr, "Now switch to another profile (/profiles) and run /aprobe p14 again: the SAME runes there = the leak (U5; SkyyProfiles 0.1.10 saves 6 sections).");
}""")
# ---- P15: Mana numbers
M(cmds, r"""
public static void p15(@PR@ pr, @CAC@ st, @REF@ ref) {
  int mi = -1;
  try { mi = @DST@.getMana(); } catch (Throwable t) { mi = -1; }
  double[] mv = stat(st, ref, mi);
  double tmax = -1.0;
  try {
    @ESTT@ t = (@ESTT@) @ESTT@.getAssetMap().getAsset(mi);
    if (t != null) tmax = (double) t.getMax();
  } catch (Throwable x) { tmax = -1.0; }
  if (mv == null) { tell(pr, "P15: your Mana is unreadable (stat index " + mi + ")."); return; }
  tell(pr, @PKG@.AbLogic.p15Text(mv[0], mv[1], tmax));
}""")
# ---- engine setup of an armed probe (after plan); a text = refused (the caller clears the state)
M(cmds, r"""
public static String start(@PKG@.AbState s, @CAC@ st, @REF@ ref) {
  if (s.mode == 1 && !CHAIN_ON) return "P1: the InteractionChainStartEvent hook is off (" + CHAIN_WHY + ") - the rune keys cannot be watched.";
  if (s.mode == 4 && slotsOf(st, ref) == null) return "P4 watch: no AbilitySlots on you.";
  return null;
}""")
M(cmds, r"""
public static String armedText(@PKG@.AbState s) {
  long secs = (s.modeUntil - s.armedAt) / 1000L;
  int m = s.mode;
  String h = "P" + m + " armed for " + secs + " s: ";
  if (m == 1) return h + "press Use Ability 2 and Use Ability 3 (with a weapon, with food, with an empty hand; also while sprinting / rolling / crouching / jumping)" + (s.cancel ? " - your Ability2 / 3 chains are CANCELLED: watch for a stuck animation or a cooldown fill." : ".");
  if (m == 4) return h + "open the Runebinder's Lattice and drag a rune in and out.";
  if (m == 13) return h + s.zones + " zones scanning at " + f1(P13_HZ) + " Hz each - stand among some mobs.";
  return h;
}""")
M(cmds, r"""
public static void p13Tick(@PKG@.AbState s, @CAC@ cb, @V3D@ p, float dt) {
  s.p13Ticks = s.p13Ticks + 1L;
  double d = (double) dt;
  if (!(d > 0.0)) d = 0.0;
  if (d > 0.2) d = 0.2;
  s.p13Acc = s.p13Acc + (double) s.zones * P13_HZ * d;
  long t0 = System.nanoTime();
  int n = 0;
  while (s.p13Acc >= 1.0 && n < 400) {
    s.p13Acc = s.p13Acc - 1.0;
    int i = s.p13Idx % (s.zones < 1 ? 1 : s.zones);
    s.p13Idx = s.p13Idx + 1;
    double[] xz = @PKG@.AbLogic.ring(p.x, p.z, P13_RING, i, s.zones);
    java.util.List l = near(cb, xz[0], p.y + 1.0, xz[1], P13_R);
    s.p13Ents = s.p13Ents + (long) l.size();
    n++;
  }
  long ns = System.nanoTime() - t0;
  s.p13Scans = s.p13Scans + (long) n;
  s.p13Ns = s.p13Ns + ns;
  if (ns > s.p13Max) s.p13Max = ns;
}""")
# the P1 cancel check, 1 s after the first cancelled chain: Mana + the server cooldown of that root
M(cmds, r"""
public static void p1Check(@PKG@.AbState s, @PR@ pr, @CAC@ acc, @REF@ r) {
  s.p1CheckAt = 0L;
  double[] mv = stat(acc, r, @DST@.getMana());
  if (mv == null) { tell(pr, "P1 cancel check: your Mana is unreadable."); return; }
  tell(pr, "P1 cancel check (" + s.p1Root + "): " + @PKG@.AbLogic.cancelVerdict(s.p1Mana, mv[0], cdLeft(handler(acc, r), s.p1Root)));
}""")
# ---- the per-player tick (AbTick, world thread, every tick; returns at once while nobody is probing)
M(cmds, r"""
public static void tickPlayer(@REF@ r, Object store, @CAC@ cb, float dt) {
  if (r == null || STATES.isEmpty()) return;
  @PR@ pr = prOf(cb, r);
  if (pr == null) return;
  @PKG@.AbState s = (@PKG@.AbState) STATES.get(pr.getUuid());
  if (s == null) return;
  if (s.st != store) { finish(s, pr, "ended: you changed world"); STATES.remove(pr.getUuid(), s); return; }
  long now = System.currentTimeMillis();
  if (s.p1CheckAt > 0L && now >= s.p1CheckAt) p1Check(s, pr, cb, r);
  if (s.mode == 0) return;
  if (now >= s.modeUntil) { finish(s, pr, null); return; }
  if (s.mode != 13) return;
  long t0 = System.nanoTime();
  @V3D@ p = pos(cb, r);
  if (p != null) p13Tick(s, cb, p, dt);
  long ns = System.nanoTime() - t0;
  s.ns = s.ns + ns;
  if (ns > s.nsMax) s.nsMax = ns;
  s.ticks = s.ticks + 1L;
}""")
# the cooldown id the 1 s cancel check reads: the held Core rune's Cast root (TriggerCooldownInteraction keys the rune cooldown by it -
# the desk read above), NOT the chain's root interaction id; the chain root only when the held item is no Core rune
M(cmds, r"""
public static String cdId(@IS@ held, String chainRoot) {
  try {
    @IAB@ a = abilOf(held);
    if (a instanceof @CIA@) {
      String c = ((@CIA@) a).getCastRootId();
      if (c != null && c.length() > 0) return c;
    }
  } catch (Throwable t) { }
  return chainRoot == null ? "" : chainRoot;
}""")
# ---- P1 hook: InteractionChainStartEvent on the player
M(cmds, r"""
public static void onChain(@ICSE@ ev, @REF@ r, @CAC@ acc) {
  if (ev == null) return;
  @PR@ pr = prOf(acc, r);
  long now = System.currentTimeMillis();
  @PKG@.AbState s = active(pr, 1, now);
  if (s == null) return;
  String type = String.valueOf(ev.getType());
  int k = @PKG@.AbLogic.kind(type);
  s.chains = s.chains + 1;
  if (k == 1) s.chainAb = s.chainAb + 1; else s.chainOther = s.chainOther + 1;
  String root = "?";
  try { root = ev.getRootInteractionId(); } catch (Throwable t) { root = "? (" + t.getClass().getSimpleName() + ")"; }
  @ICTX@ ctx = ev.getContext();
  @IS@ held = null;
  int sec = 0;
  int slot = -1;
  if (ctx != null) {
    held = ctx.getHeldItem();
    sec = ctx.getHeldItemSectionId();
    slot = (int) ctx.getHeldItemSlot();
  }
  String hid = held == null || held.isEmpty() ? "nothing" : held.getItemId();
  String line = "P1 " + type + " root " + root + ", item " + hid + " (section " + sec + " slot " + slot + ")";
  if (k == 1) {
    @IS@ hd = hand(acc, r);
    line = line + " | " + abilText(held) + useText(held, hd) + " | " + moveText(acc, r);
  }
  line = line + " (+" + (now - s.armedAt) + " ms)";
  if (s.cancel && k == 1) {
    ev.setCancelled(true);
    boolean ok = ev.isCancelled();
    if (ok) s.cancelled = s.cancelled + 1; else s.cancelFail = s.cancelFail + 1;
    line = line + (ok ? " -> CANCELLED" : " -> cancel FAILED");
    double[] mv = stat(acc, r, @DST@.getMana());
    if (ok && mv != null && s.p1CheckAt == 0L) { s.p1Mana = mv[0]; s.p1Root = cdId(held, root); s.p1CheckAt = now + 1000L; }
  }
  if (s.lines < 40 && (k == 1 || s.chainOther <= 6)) { s.lines = s.lines + 1; tell(pr, line); }
  else { s.logOnly = s.logOnly + 1; @PKG@.AbLog.info(line); }
}""")
# ---- P4 watch hook: InventoryChangeEvent on the player - which section changed
M(cmds, r"""
public static void onInv(@ICE@ ev, @REF@ r, @CAC@ acc) {
  if (ev == null) return;
  @PR@ pr = prOf(acc, r);
  @PKG@.AbState s = active(pr, 4, System.currentTimeMillis());
  if (s == null) return;
  Object t = ev.getComponentType();
  String where = null;
  if (t != null && t == @ABS@.getComponentType()) { s.invSlots = s.invSlots + 1; where = "the AbilitySlots (-11)"; }
  else if (t != null && t == @RNB@.getComponentType()) { s.invBag = s.invBag + 1; where = "the RuneBag (-12)"; }
  else s.invOther = s.invOther + 1;
  if (where != null && s.lines < 20) { s.lines = s.lines + 1; tell(pr, "P4 watch: InventoryChangeEvent on " + where + "; slots now " + slots(ev.getItemContainer(), true, 20)); }
}""")
# ---- one entry point for every usage variant: w = the words after /aprobe
M(cmds, r"""
public static void run(@REF@ ref, @CAC@ st, @PR@ pr, String[] w) {
  String t = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 0));
  String l1 = @PKG@.AbLogic.low(@PKG@.AbLogic.word(w, 1));
  StringBuilder all = new StringBuilder();
  for (int i = 0; w != null && i < w.length; i++) { if (w[i] != null) all.append(" ").append(w[i]); }
  @PKG@.AbLog.info(pr.getUsername() + " ran /aprobe" + all.toString());
  if (t == null || "help".equals(t)) { help(pr); return; }
  if ("info".equals(t)) { info(pr); return; }
  if ("stats".equals(t)) { stats(pr); return; }
  if ("stop".equals(t)) {
    @PKG@.AbState s0 = (@PKG@.AbState) STATES.remove(pr.getUuid());
    if (s0 != null) finish(s0, pr, "stopped");
    String tb = takeBack(pr, st, ref);
    if (tb != null) tell(pr, tb);
    tell(pr, "Probe state cleared.");
    return;
  }
  if ("p3".equals(t)) {
    @PKG@.AbState c0 = (@PKG@.AbState) STATES.get(pr.getUuid());
    if (c0 != null && c0.mode == 1 && c0.cancel) finish(c0, pr, "cancel ended early (p3 needs your rune key uncancelled)");
    p3(pr, st, ref, w);
    return;
  }
  if ("p4".equals(t) && !"watch".equals(l1)) { p4(pr, st, ref, w); return; }
  if ("p14".equals(t)) { p14(pr, st, ref); return; }
  if ("p15".equals(t)) { p15(pr, st, ref); return; }
  @PKG@.AbState s = state(pr, ref, st);
  if (s.mode != 0) finish(s, pr, "ended early (a new probe was armed)");
  long now = System.currentTimeMillis();
  String err = plan(s, w, now);
  if (err != null) { tell(pr, err); return; }
  String err2 = start(s, st, ref);
  if (err2 != null) { clear(s); tell(pr, err2); return; }
  tell(pr, armedText(s));
}""")

# ---- AbTick: EntityTickingSystem on Player (one registerSystem per class), world thread
tick = mk("AbTick", T["ETS"])
F(tick, "public static boolean FAILED_ONCE = false;")
C(tick, "public AbTick() { super(); }")
M(tick, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(tick, "public boolean isParallel(int a, int b) { return false; }")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (chunk == null || @PKG@.AbCmds.STATES.isEmpty()) return;
    @PKG@.AbCmds.tickPlayer(chunk.getReferenceTo(idx), store, cb, dt);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("tick failed (logged once): " + t); }
  }
}""")

# ---- AbChainSys: EntityEventSystem<InteractionChainStartEvent> on players (P1)
chain = mk("AbChainSys", T["EES"])
F(chain, "public static boolean FAILED_ONCE = false;")
C(chain, "public AbChainSys() { super(@ICSE@.class); }")
M(chain, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(chain, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || !(ev instanceof @ICSE@) || @PKG@.AbCmds.STATES.isEmpty()) return;
    @PKG@.AbCmds.onChain((@ICSE@) ev, chunk.getReferenceTo(idx), buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("chain hook failed (logged once): " + t); }
  }
}""")

# ---- AbInvSys: EntityEventSystem<InventoryChangeEvent> on players (P4 watch)
inv = mk("AbInvSys", T["EES"])
F(inv, "public static boolean FAILED_ONCE = false;")
C(inv, "public AbInvSys() { super(@ICE@.class); }")
M(inv, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(inv, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || !(ev instanceof @ICE@) || @PKG@.AbCmds.STATES.isEmpty()) return;
    @PKG@.AbCmds.onInv((@ICE@) ev, chunk.getReferenceTo(idx), buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AbLog.warn("inventory hook failed (logged once): " + t); }
  }
}""")

# ---- /aprobe and its usage variants (admin: requirePermission + no permission groups on each)
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
ARG_DESCS = ["probe", "first value", "second value", "third value"]


def variant(n):
    cname = "AProbeArg%dCmd" % n
    vc = mk(cname, T["APC"])
    for i in range(n):
        F(vc, "public @RA@ a%d;" % i)
    usage = "(admin) /aprobe " + " ".join("<%s>" % d for d in ARG_DESCS[:n])
    args = "\n".join('  this.a%d = withRequiredArg("%s", "%s", @ATY@.STRING);' % (i, ARG_DESCS[i].replace(" ", ""),
                     "p1 p3 p4 p13 p14 p15 info stats stop" if i == 0 else "a word or a number") for i in range(n))
    C(vc, r"""
public %s() {
  super("%s");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
%s
}""" % (cname, usage, args))
    reads = "\n".join("    w[%d] = String.valueOf(ctx.get(this.a%d));" % (i, i) for i in range(n))
    M(vc, EXEC + r""" {
  String[] w = new String[%d];
  try {
%s
  } catch (Throwable t) { @PKG@.AbLog.tell(pr, "Usage: /aprobe <probe> [values]"); return; }
  @PKG@.AbCmds.run(ref, store, pr, w);
}""" % (n, reads))
    return vc


VARIANTS = [variant(1), variant(2), variant(3), variant(4)]
cmd = mk("AProbeCmd", T["APC"])
C(cmd, r"""
public AProbeCmd() {
  super("aprobe", "(admin) Hytale 0.7 ability-key probes (throwaway dev pack): /aprobe lists them");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "abilityprobe" });
  addUsageVariant(new @PKG@.AProbeArg1Cmd());
  addUsageVariant(new @PKG@.AProbeArg2Cmd());
  addUsageVariant(new @PKG@.AProbeArg3Cmd());
  addUsageVariant(new @PKG@.AProbeArg4Cmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.AbCmds.help(pr);
}""")

# ---- the plugin
pl = mk("SkyyAbilityProbePlugin", T["JP"])
C(pl, "public SkyyAbilityProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.AbLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.AProbeCmd());
  getEntityStoreRegistry().registerSystem(new @PKG@.AbTick());
  getEntityStoreRegistry().registerSystem(new @PKG@.AbInvSys());
  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbChainSys()); @PKG@.AbCmds.CHAIN_ON = true; @PKG@.AbCmds.CHAIN_WHY = "listening"; }
  catch (Throwable t) { @PKG@.AbCmds.CHAIN_WHY = "registration failed: " + t; @PKG@.AbLog.warn("InteractionChainStartEvent hook failed: " + t); }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyAbilityProbe] @VERSION@ ready - /aprobe (admin): Hytale 0.7 ability-key probes P1 P3 P4 P13 P14 P15 (throwaway dev pack, remove after the test session); chain event " + @PKG@.AbCmds.CHAIN_WHY);
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.AbCmds.STATES.clear();
  @PKG@.AbCmds.PUT.clear();
  super.shutdown();
}""")

ALL = [log, lg, sta, cmds, tick, chain, inv] + VARIANTS + [cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "SkyyAbilityProbe-%s.jar" % VERSION)
man = B.manifest("SkyyAbilityProbe", VERSION, "SkyWynn THROWAWAY dev pack for Hytale 0.7: ability-key probes (/aprobe, admin only) - rune keys "
                 "+ chain start event + cancel, the server cooldown handler, the ability slots, scan cost, the profile leak, the Mana scale. "
                 "Pinned for one test session, then removed.", PKG + ".SkyyAbilityProbePlugin")
man["IncludesAssetPack"] = False   # class-only jar (the harness asserts it): nothing vanilla or pack-owned is overridden
B.assemble(jar, man, OUT, {})
