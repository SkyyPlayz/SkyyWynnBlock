"""SkyyClasses 0.1.3 - build script (javassist via jpype). Wynncraft-style classes for SkyWynn.
0.1.4: a POPUP (vanilla notification toast with the weapon's icon) whenever a hit is blocked, next to the chat line - notes in
  tools/classes_0_1_4_patch.py.
0.1.3: per-profile storage (tools/PROFILES-CONTRACT.md). Player files are players/<pkey>.properties - pkey() is the contract helper
  (profile 1 and no SkyyProfiles = <uuid> = the existing files, profile N = <uuid>-pN); the DATA + CLS caches are keyed by the pkey String
  (pkey is always computed outside ClassStore's lock). profile:class:<uuid> (SkyyProfiles) is AUTHORITATIVE when present and a known
  class: it is the player's class for class:<uuid> / class:skill:<uuid> / class:fn:get / the weapon lock, /class is read-only ("locked to
  this profile", no Choose/Switch buttons), /classadmin set|reset refuse, and it is copied into that profile's file (offline reads).
  While SkyyProfiles is loaded (profile:fn:key present) there is no first-join class picker or chat hint - SkyyProfiles runs profile
  creation. ClassTick (every 2 s on HytaleServer.SCHEDULED_EXECUTOR) republishes class:<uuid> + class:skill:<uuid> when
  profile:epoch:<uuid> changes (last epoch seen per UUID, forgotten on disconnect) or the published value drifts from the profile.
  Without SkyyProfiles everything behaves exactly like 0.1.2 (pkey = uuid, the tick returns at once).
  Review fixes: the profile class is copied into a profile file only from a STEADY snapshot - the same (profile:epoch, pkey,
  profile:class) seen for >= SYNC_STEADY_MS across checks AND re-read unchanged right before the write - so a check that lands in the
  middle of a SkyyProfiles switch (pointer and class updated in separate steps) can never write one profile's class into another
  profile's file. A profile:class naming a class that is not ENABLED here (Assassin, Shaman) is not authoritative (logged once, the class
  file decides - never a silent unlock of a coming-soon class's weapons). ensure() is synchronized (load + first publish atomic, as
  0.1.2's load was). /classadmin info reads one pkey and says whether the class comes from the profile or from the profile file.
  Integration fixes (2026-09-23, checked against "Semantics of SkyyProfiles 0.1" in tools/PROFILES-CONTRACT.md; still 0.1.3):
  - a profile:class naming a KNOWN class that is not playable yet (Assassin, Shaman - /profileadmin setclass allows them) is
    authoritative too: the profile is locked to it, class:<uuid> says so (SkyySkills' class check then matches instead of pausing and
    failing open every switch), and that class's own weapons stay blocked like any unassigned weapon (allowed() only lets a class use
    its weapons while the class is ENABLED). Before, the class file decided: an empty profile file meant "no class" = every weapon
    worked (the silent unlock the review wanted to prevent), and /class let the player pick a different class for that profile.
    Unknown names (hand edits) still fall back to the class file (logged once). Only ENABLED classes are ever written into a file.
  - SkyyProfiles loaded but no profile yet (profile:<uuid> absent): /class is read-only and points to /profiles (the class is picked
    when the profile is created - one picker, not two); chooseKey refuses it server-side too. /classadmin set still works.
  - a player file that cannot be READ is no longer cached as an empty file (the next syncKey / choice / prompted flag used to overwrite
    it, losing class, played, switches): the failed read is retried at most every 2 s and saves of an unread key are refused.
    Atomic replace retries 5 x 20 ms on a Windows AccessDeniedException (file briefly held open by a scanner or backup).
  - publishKey is synchronized (reads the class inside ClassStore's lock; only bridge reads + puts, no Function call), so two
    publishes (tick, admin, choice) can no longer interleave into class:<uuid> and class:skill:<uuid> of different classes.
  - the steady-snapshot file sync also needs profile:key:<uuid> == pkey(u): SkyyProfiles flips the key Function at the players-file
    commit and publishes key/class/epoch just after, so a stall in between can never copy the old profile's class into the new file.
  - OpenTask (no-SkyyProfiles first-join page) re-checks on the world thread that the player is still in the world it hopped to.
  Cross-mod timeline pass (2026-09-23, same version): the no-SkyyProfiles first-join page also waits for the player to stay in one
  world for 2 polls, waits up to 8 s while they stand in a skyy-island-* world (SkyyIslands' login routing to the hub would lose the
  page), never replaces an open custom page (SkyyMenu etc.) and never opens over the respawn screen - the same guards as SkyyProfiles'
  Create Profile page. The player-file replace retries on any FileSystemException (a sharing violation from another program is not
  an AccessDeniedException).
  Verified: what first sight does (baseline = one publish, no file write until steady), writes before the key is right (none: pkey is
  right from its first call; ClassStore writes only on a choice, an admin command or the steady sync), epoch change (republish at the
  next 2 s tick; no live effects to recompute - the weapon lock reads profile:class per hit; no dirty data: every write is synchronous),
  lock order (pkey always outside ClassStore's lock; nothing under it calls another mod), disconnect (per-UUID maps dropped, DATA kept by
  pkey, class:<uuid> kept like SkyyProfiles' keys). No item, coin or stat writes happen on the profile path (coins only on a paid switch,
  which is off), so profile:busy needs no check here.
0.1.2 (design lock 2026-09-23 night): roster = Wynn's five - Archer, Warrior, Mage selectable; Assassin + Shaman 'coming later'; Berserker removed
  (axes/battleaxes/maces/clubs are unassigned now). Class switching is OFF (allowSwitch=false): a new class = a new profile (SkyyProfiles).
0.1.1 (Skyy 2026-09-23): Mage ENABLED with staffs (skill Sorcery; wands + spellbooks stay unassigned); /class opened to every player (setPermissionGroups hytale:Adventurer).
Run:   python build_skyyclasses_0.1.3.py            -> SkyyClasses/SkyyClasses-0.1.3.jar
       python build_skyyclasses_0.1.3.py --deploy   -> also copies to Mods/SkyyClasses.jar and enables it in the HUD mod world

Skyy (2026-09-23): "combat will be based on your class. so as an archer your combat skill will be archery, you can only use bows,
and cannot level any kind of combat but archery. the pattern holds the same for all classes."
Roster: Archer=Archery (shortbows, crossbows), Warrior=Swordsmanship (swords, longswords, spears), Assassin=Assassination (daggers,
kunai throwing knife), Berserker=Berserking (axes, battleaxes, maces, clubs), Mage = ENABLED since 0.1.1 (Sorcery, staffs; was 'coming soon' in 0.1;
staves/wands/spellbooks stay locked until Skyy sees where Hytale takes magic).

WEAPON RULES = the CLASSES / FREE_WEAPONS / UNASSIGNED tables right below (edit them, rebuild). Item id PREFIX matching, longest prefix
wins; the build checks every prefix and icon against Assets.zip and prints what each class gets. Why prefixes and not Tags.Family:
the vanilla Family tags are incomplete/wrong (Battleaxe + Kunai have none, Claws say Dagger, Dart says Arrow, Blowgun inherits Sword).
  - class weapons: only that class deals damage with them.
  - FREE_WEAPONS (shields) + anything that matches no rule (tools, fists, blocks, food, torches, modded items with other names): never blocked.
  - UNASSIGNED (bombs, guns, flamethrower, deployables, darts, claws, blowgun, minigame guns, catch-all Weapon_) and the weapons of a
    disabled class (Mage): blocked for every player WITH a class while unassignedBlocked=true (default, config). Decision: nobody gets
    an unowned weapon for free - assign it to a class (or set unassignedBlocked=false) to open it up.
  - Players WITHOUT a class: requireClass=false (default) -> any weapon works (they earn no class XP: SkyySkills sees no class:<uuid>);
    requireClass=true -> weapons deal no damage until they pick a class.
  - Arrows (Weapon_Arrow_*) are Archer weapons: bows fire them from the inventory (never checked), but stabbing with an arrow is Archer-only.

LOCK MECHANISM (research 2026-09-23, verified against HytaleServer.jar bytecode; review fixes 2026-09-23):
  DamageLock extends DamageEventSystem in DamageModule.get().getFilterDamageGroup(), Query.any() - the same hook vanilla PvP-off /
  spawn protection use and TerrariaAddons LavaCharmSystem uses from a mod. The item is never stored on the Damage, so:
  - MELEE: DamageEntityInteraction builds EntitySource(context.getOwningEntity()) = the attacker; we read the attacker's hands at hit
    time: InventoryComponent.getItemInHand(buf, ref) (vanilla DamageAttackerTool does the same) AND the active Utility-slot item (the
    Kunai is Utility.Usable: thrown with right-click from the utility slot while the main hand holds something else).
  - PROJECTILES + BOMBS: ShotTrack (a RefSystem on projectile entities - stolen from SimpleEnchantments' EnchantmentProjectileSpeedSystem:
    Query Transform AND (ProjectileComponent OR StandardPhysicsProvider), AddReason.SPAWN, creator = getCreatorUuid() ->
    EntityStore.getRefFromUUID) records what the shooter held (main hand + utility) when the projectile was LAUNCHED, keyed by the
    projectile's UUIDComponent, dropped in onEntityRemove. Bombs/grenades explode via ExplodeInteraction ->
    Damage$ProjectileSource(owner, projectile) and legacy LaunchProjectile shots (spear/knife throws, guns, staves, wands) hit via
    ProjectileComponent.onProjectileHitEvent -> ProjectileSource(shooter, projectile): both are judged by the launch record, not by the
    hands at detonation (a thrown bomb has left the hand) - and still judged when the shooter is gone (the legacy hit then uses the
    projectile itself as the attacker, which used to skip the check completely).
    Shortbow/crossbow arrows and kunai are new-style projectiles whose hit runs DamageEntity in a proxy context -> plain
    EntitySource(shooter), no projectile on the Damage: judged by the shooter's hands at landing PLUS: while a projectile that player
    launched with a forbidden weapon is still alive (at most SHOT_WINDOW_MS), ALL their damage is blocked - this closes the
    swap-bow-to-sword-mid-flight trick. (New-style projectiles never deal damage once their shooter is gone: the engine removes them.)
  If a weapon the class may not use is involved -> damage.setAmount(0) + setCancelled(true) (LavaCharm does both) + the target's
  KnockbackComponent is removed (DamageEntityInteraction attaches it BEFORE the damage event; vanilla FilterPlayerWorldConfig removes it
  the same way when it cancels) + a throttled chat message ("Only Archers can use bows").
  Weapon USE is NOT blocked (damage only): PlayerInteractEvent is dead code (never constructed anywhere in the server jar) and
  PlayerMouseButtonEvent only fires for the MouseInteraction packet (InteractionModule.doMouseInteraction); real weapon swings/shots are
  client-predicted SyncInteractionChains with no cancellable hook - cancelling them server-side would desync the client.
  KNOWN LIMITS (engine, not fixable from the damage hook):
  - a blocked BOMB still pushes: ExplosionUtils.processTargetEntity attaches the explosion knockback AFTER the damage event and never
    checks cancellation (vanilla's own damage-off filter has the same gap). Blocked melee/arrow/kunai hits do not knock back.
  - DEPLOYABLES (Weapon_Deployable_ turret/totems, the Crystal Flame staff trap) deal damage as the deployable entity, not the player
    (DeployableTurretConfig / DeployableAoeConfig build EntitySource(deployable)) -> the class lock does not judge them.
  - projectiles already flying when the plugin loads, or reloaded from a chunk (AddReason.LOAD), have no launch record -> judged by hands.

/class (alias /classes): inline page, one card per class (weapon icons, name, combat skill, description, Selected state, Choose/Switch).
  First choice is free; switching costs switchCost coins (default 5000, via bridge coins:fn:take; refused with a message if SkyyCoins is
  absent and switchCost > 0) behind a Confirm/Cancel step, and a cooldown (cooldownMinutes, default 60 real minutes since the player's
  last choice). The class is only recorded - per-class combat XP will live in SkyySkills (players/<uuid> keeps "played" = every class used).
First join: PlayerReadyEvent fires on EVERY world switch -> once-per-session set; the player file is then read OFF the world thread
  (ReadyTask on HytaleServer.SCHEDULED_EXECUTOR - no disk I/O in the event handler); if the player has no class: chat hint + the page
  opens ~2 s later on the world thread (SkyyHud AttachTask pattern incl. the WorldMap-channel gate). promptEveryLogin=true (default)
  repeats this every login until a class is chosen; false = only the very first join (persisted flag prompted=1).
Admin (perm skyyclasses.admin): /classadmin set <player|uuid> <class>, /classadmin reset <player|uuid> (next choice free again),
  /classadmin info <player|uuid>, /classadmin reload (config).
Bridge (System.getProperties().get("skyy.bridge")):
  class:<uuid> -> "Archer" (absent = no class; = profile:class:<uuid> when SkyyProfiles sets it)      class:skill:<uuid> -> "Archery"
  class:fn:allowed -> Function apply(Object[]{UUID, String itemId}) -> Boolean (may that player deal damage with that item)
  class:fn:get -> Function apply(UUID) -> "Archer" or null (loads offline players from disk)
  class:list -> "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery" (selectable classes)
  class:weapons:<Class> -> comma list of id prefixes (also class:weapons:free, class:weapons:unassigned)
Data: Skyy_SkyyClasses/players/<pkey>.properties (0.1.3: one file per profile - <uuid> = profile 1 or no SkyyProfiles, <uuid>-pN =
      profile N; class, chosenAt, lastChoiceAt, switches, played, prompted),
      Skyy_SkyyClasses/config.properties (switchCost, cooldownMinutes, requireClass, unassignedBlocked, promptEveryLogin, openDelayMillis).
      Atomic writes (tmp + move).
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.4"
HERE = os.path.dirname(os.path.abspath(__file__))

# =====================================================================================================================
# WEAPON RULES + CLASS DATA (edit here, rebuild). UI text: no , : ; { } " ' _ (the inline UI parser is picky; the build asserts it).
# weapons: (item id prefix, plural noun used in "Only <Class>s can use <noun>")
# =====================================================================================================================
CLASSES = [
    {"name": "Archer", "skill": "Archery", "color": "#8fd67a", "enabled": True,
     "desc": "Fights from range. Charge a shortbow or load a crossbow and strike before the enemy gets close. Arrows are Archer ammo.",
     "icons": ["Weapon_Shortbow_Iron", "Weapon_Crossbow_Iron", "Weapon_Arrow_Crude"],
     "weapons": [("Weapon_Shortbow_", "bows"), ("Weapon_Crossbow_", "crossbows"), ("Weapon_Arrow_", "arrows")],
     "weapon_text": "Shortbows / Crossbows"},
    {"name": "Warrior", "skill": "Swordsmanship", "color": "#e0b060", "enabled": True,
     "desc": "Front line blade fighter. Swords and longswords up close and spears for reach.",
     "icons": ["Weapon_Sword_Iron", "Weapon_Longsword_Iron", "Weapon_Spear_Iron"],
     "weapons": [("Weapon_Sword_", "swords"), ("Weapon_Longsword_", "longswords"), ("Weapon_Spear_", "spears")],
     "weapon_text": "Swords / Longswords / Spears"},
    {"name": "Assassin", "skill": "Assassination", "color": "#b58cff", "enabled": False,
     "desc": "Coming later. Fast and deadly with twin daggers and kunai throwing knives.",
     "icons": ["Weapon_Daggers_Iron", "Weapon_Kunai"],
     "weapons": [("Weapon_Daggers_", "daggers"), ("Weapon_Kunai", "kunai")],
     "weapon_text": "Daggers / Kunai"},
    {"name": "Shaman", "skill": "Shaman skill", "color": "#ff7a5c", "enabled": False,
     "desc": "Coming later. The fifth Wynncraft class - its weapons and skill are designed when that phase starts.",
     "icons": ["Weapon_Wand_Wood"],
     "weapons": [],
     "weapon_text": "Designed later"},
    {"name": "Mage", "skill": "Sorcery", "color": "#7fb0e0", "enabled": True,
     "desc": "Spellcaster. Staves strike up close and cast magic at range.",
     "icons": ["Weapon_Staff_Iron", "Weapon_Staff_Wizard", "Weapon_Staff_Crystal_Ice"],
     "weapons": [("Weapon_Staff_", "staves"), ("Halloween_Broomstick", "broomsticks")],
     "weapon_text": "Staves"},
]
# usable by every class (and by classless players)
FREE_WEAPONS = [("Weapon_Shield_", "shields")]
# weapons no class owns yet (blocked for players with a class while unassignedBlocked=true). "Weapon_" = catch-all for any other Weapon_*.
UNASSIGNED = [
    ("Weapon_Bomb", "bombs"), ("Weapon_Gun", "guns"), ("Flamethrower_", "flamethrowers"), ("Weapon_Deployable_", "deployables"),
    ("Weapon_Dart_", "darts"), ("Weapon_Claws_", "claws"), ("Weapon_Blowgun_", "blowguns"),
    ("Weapon_Assault_Rifle", "guns"), ("Weapon_Handgun", "guns"), ("Weapon_Grenade_", "grenades"), ("Weapon_Test_", "test weapons"),
    ("Weapon_", "that weapon"),
]
# config defaults (written to Skyy_SkyyClasses/config.properties on first start)
DEF_SWITCH_COST = 5000
DEF_COOLDOWN_MIN = 60
DEF_REQUIRE_CLASS = False
DEF_UNASSIGNED_BLOCKED = True
DEF_PROMPT_EVERY_LOGIN = True
DEF_OPEN_DELAY_MS = 2000
MSG_THROTTLE_MS = 3000
SHOT_WINDOW_MS = 10000      # a live projectile launched with a forbidden weapon blocks all of its shooter's damage for at most this long
SHOT_PURGE_MS = 120000      # launch records older than this are purged when the table grows past SHOT_PURGE_AT (safety net)
SHOT_PURGE_AT = 1024
SYNC_STEADY_MS = 1500       # 0.1.3 review fix: the profile class is written into a profile file only after (epoch, pkey, class) held this long

# =====================================================================================================================
# rule table + checks against the vanilla Assets.zip (fail the build on a typo instead of a silent hole in game)
# =====================================================================================================================
FREE, UNASSIGNED_OWNER = -1, -2
RULES = []
for _ci, _c in enumerate(CLASSES):
    for _p, _n in _c["weapons"]:
        RULES.append((_p, _ci, _n))
for _p, _n in FREE_WEAPONS:
    RULES.append((_p, FREE, _n))
for _p, _n in UNASSIGNED:
    RULES.append((_p, UNASSIGNED_OWNER, _n))
assert len(set(r[0] for r in RULES)) == len(RULES), "duplicate weapon prefix in the rule tables"
RULES.sort(key=lambda r: -len(r[0]))   # longest prefix first (stable: equal lengths keep table order)

def classify(iid):
    for p, owner, noun in RULES:
        if iid.startswith(p):
            return owner, noun
    return FREE, None

BAD_UI = set(',:;{}"\'_\\')
for _c in CLASSES:
    for _k in ("name", "skill", "desc", "weapon_text"):
        _bad = BAD_UI & set(_c[_k])
        assert not _bad, "UI text %s.%s contains %r" % (_c["name"], _k, "".join(sorted(_bad)))
    assert re.match(r"^#[0-9a-fA-F]{6}$", _c["color"]), _c["color"]
    assert 1 <= len(_c["icons"]) <= 4, "1-4 icons per class"
assert len(CLASSES) <= 9

_ASSETS = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
_ITEMS = {}
for _n in _ASSETS.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        _ITEMS[os.path.basename(_n)[:-5]] = _n
def _tags(iid, depth=0):
    d = json.loads(_ASSETS.read(_ITEMS[iid]).decode("utf-8-sig"))
    if "Tags" in d or depth > 8 or not d.get("Parent") or d.get("Parent") not in _ITEMS:
        return d.get("Tags") or {}
    return _tags(d["Parent"], depth + 1)
_real = sorted(i for i in _ITEMS if not i.startswith("Template_"))
_by_owner = {}
for _i in _real:
    _o, _ = classify(_i)
    _by_owner.setdefault(_o, []).append(_i)
for _p, _o, _n in RULES:
    assert any(_i.startswith(_p) for _i in _real), "weapon prefix %s matches no item in Assets.zip" % _p
for _ci, _c in enumerate(CLASSES):
    for _ic in _c["icons"]:
        assert _ic in _ITEMS, "icon item %s not in Assets.zip" % _ic
        if _c["weapons"]:  # 0.1.2: a not-yet-designed class (Shaman) has no weapons, its icon is only a picture
            assert classify(_ic)[0] == _ci, "icon %s is not a %s weapon under the rules" % (_ic, _c["name"])
print("weapon rules vs Assets.zip:")
for _ci, _c in enumerate(CLASSES):
    print("  %-10s %-14s %3d items%s" % (_c["name"], _c["skill"], len(_by_owner.get(_ci, [])), "" if _c["enabled"] else "  (class disabled -> treated as unassigned)"))
print("  %-25s %3d items (%s)" % ("free (shields)", len([i for i in _by_owner.get(FREE, []) if i.startswith("Weapon_Shield_")]), "usable by all"))
print("  unassigned: %d items: %s" % (len(_by_owner.get(UNASSIGNED_OWNER, [])), ", ".join(_by_owner.get(UNASSIGNED_OWNER, []))))
_slip = [i for i in _by_owner.get(FREE, []) if "Weapon" in (_tags(i).get("Type") or []) and not i.startswith("Weapon_Shield_")]
print("  note - Weapon-tagged items no rule catches (treated as free):", ", ".join(_slip) or "none")

# =====================================================================================================================
# JVM + engine classes
# =====================================================================================================================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.classes"
T = {
    "PKG": PKG,
    "JP":   "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":  "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "UNI":  "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":  "com.hypixel.hytale.server.core.universe.world.World",
    "APC":  "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":  "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG":  "com.hypixel.hytale.server.core.Message",
    "HSV":  "com.hypixel.hytale.server.core.HytaleServer",
    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG":  "com.hypixel.hytale.logger.HytaleLogger",
    "PLA":  "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "DES":  "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMG":  "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "QRY":  "com.hypixel.hytale.component.query.Query",
    "SG":   "com.hypixel.hytale.component.SystemGroup",
    "ACH":  "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":   "com.hypixel.hytale.component.CommandBuffer",
    "EV":   "com.hypixel.hytale.component.system.EcsEvent",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "UTIL": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility",
    "IS":   "com.hypixel.hytale.server.core.inventory.ItemStack",
    "PRE":  "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE":  "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "DPRJ": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource",
    "KBC":  "com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent",
    "RSYS": "com.hypixel.hytale.component.system.RefSystem",
    "ADDR": "com.hypixel.hytale.component.AddReason",
    "REMR": "com.hypixel.hytale.component.RemoveReason",
    "TC":   "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "SPP":  "com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsProvider",
    "LPC":  "com.hypixel.hytale.server.core.entity.entities.ProjectileComponent",
    "UUIDC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "ES":   "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "NTU":  "com.hypixel.hytale.server.core.util.NotificationUtil",
    "NST":  "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle",
    "IWM":  "com.hypixel.hytale.protocol.ItemWithAllMetadata",
}
def jv(src):
    """Java source with @TOKEN@ placeholders (raw strings: no brace doubling, \\" stays a Java escape)."""
    out = src
    for k, v in T.items():
        out = out.replace("@" + k + "@", v)
    left = re.findall(r"@[A-Z]+@", out)
    assert not left, "unreplaced tokens: %s" % left
    return out
def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }"

AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
for c, m in ((T["DMG"], "setCancelled"), (T["DMG"], "setAmount"), (T["DMG"], "getSource"), (T["DMG"], "isCancelled"),
             (T["DENT"], "getRef"), (T["DMOD"], "get"), (T["DMOD"], "getFilterDamageGroup"), (T["QRY"], "any"),
             (T["INVC"], "getItemInHand"), (T["UTIL"], "getActiveItem"), (T["UTIL"], "getComponentType"), (T["IS"], "getItemId"),
             (T["IS"], "isEmpty"), (T["CB"], "getComponent"), (T["REF"], "isValid"), (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"),
             (T["PLA"], "getPageManager"), (T["PLA"], "getPlayerConnection"), (T["PAGE"], "rebuild"), (T["HSV"], "SCHEDULED_EXECUTOR"),
             (T["UNI"], "getPlayers"), (T["UNI"], "getPlayer"), (T["PR"], "hasPermission"), (T["PR"], "getWorldUuid"), (T["MSG"], "color"),
             (AC, "addSubCommand"), (AC, "addAliases"), (AC, "requirePermission"), (AC, "setPermissionGroups"), (AC, "withRequiredArg"),
             (T["DPRJ"], "getProjectile"), (T["CB"], "tryRemoveComponent"), (T["CB"], "getExternalData"), (T["ACH"], "getReferenceTo"),
             (T["KBC"], "getComponentType"), (T["RSYS"], "onEntityAdded"), (T["RSYS"], "onEntityRemove"), (T["ADDR"], "SPAWN"),
             (T["TC"], "getComponentType"), (T["SPP"], "getComponentType"), (T["SPP"], "getCreatorUuid"), (T["LPC"], "getComponentType"),
             (T["LPC"], "getCreatorUuid"), (T["UUIDC"], "getComponentType"), (T["UUIDC"], "getUuid"), (T["ES"], "getRefFromUUID"),
             (T["QRY"], "and"), (T["QRY"], "or"), (T["PR"], "isValid"),
             (T["NTU"], "sendNotification"), (T["NST"], "Warning"), (T["IS"], "toPacket"), (T["PR"], "getPacketHandler"),
             ("com.hypixel.hytale.component.system.ISystem", "getGroup"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEntityStoreRegistry"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "getCustomPage"),
             ("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent", "getComponentType"), (T["WLD"], "getName"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)
pool.get(T["DES"])

cfg  = pool.makeClass(PKG + ".ClassCfg")
defs = pool.makeClass(PKG + ".ClassDefs")
st_  = pool.makeClass(PKG + ".ClassStore")
rul  = pool.makeClass(PKG + ".ClassRules")
afn  = pool.makeClass(PKG + ".AllowedFn")
gfn  = pool.makeClass(PKG + ".GetFn")
srec = pool.makeClass(PKG + ".ShotRec")
strk = pool.makeClass(PKG + ".ShotTrack", pool.get(T["RSYS"]))
lock = pool.makeClass(PKG + ".DamageLock", pool.get(T["DES"]))
page = pool.makeClass(PKG + ".ClassPage", pool.get(T["PAGE"]))
opn  = pool.makeClass(PKG + ".OpenTask")
rtk  = pool.makeClass(PKG + ".ReadyTask")
rdy  = pool.makeClass(PKG + ".ClassReady")
quit_ = pool.makeClass(PKG + ".ClassQuit")
ctick = pool.makeClass(PKG + ".ClassTick")
cmd  = pool.makeClass(PKG + ".ClassCmd", pool.get(T["APC"]))
aset = pool.makeClass(PKG + ".AdminSetCmd", pool.get(T["APC"]))
ares = pool.makeClass(PKG + ".AdminResetCmd", pool.get(T["APC"]))
ainf = pool.makeClass(PKG + ".AdminInfoCmd", pool.get(T["APC"]))
arel = pool.makeClass(PKG + ".AdminReloadCmd", pool.get(T["APC"]))
adm  = pool.makeClass(PKG + ".ClassAdminCmd", pool.get(T["APC"]))
pl   = pool.makeClass(PKG + ".SkyyClassesPlugin", pool.get(T["JP"]))

def F(cls, src): cls.addField(CtField.make(jv(src), cls))
def M(cls, src): cls.addMethod(CtNewMethod.make(jv(src), cls))
def C(cls, src): cls.addConstructor(CtNewConstructor.make(jv(src), cls))

# ================= ClassCfg: logger, bridge, config =================
CFG_LINES = [
    "# SkyyClasses config - edit, then /classadmin reload (or restart the server)",
    "# switchCost = coins to switch class (the first choice is always free). Uses SkyyCoins; 0 = free switching.",
    "switchCost=%d" % DEF_SWITCH_COST,
    "# cooldownMinutes = real minutes after a player chooses a class before they may switch again",
    "cooldownMinutes=%d" % DEF_COOLDOWN_MIN,
    "# requireClass = true: players without a class deal no weapon damage. false: they may use any weapon (but earn no class XP)",
    "requireClass=%s" % str(DEF_REQUIRE_CLASS).lower(),
    "# unassignedBlocked = true: weapons no class owns yet (staves, wands, spellbooks, bombs, guns...) deal no damage for players with a class",
    "unassignedBlocked=%s" % str(DEF_UNASSIGNED_BLOCKED).lower(),
    "# promptEveryLogin = true: open the class page on every login until a class is chosen. false: only on the very first join",
    "promptEveryLogin=%s" % str(DEF_PROMPT_EVERY_LOGIN).lower(),
    "# openDelayMillis = how long after joining the class page opens",
    "openDelayMillis=%d" % DEF_OPEN_DELAY_MS,
]
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static @LOG@ LOG;")
F(cfg, "public static int FAILS = 0;")
F(cfg, "public static volatile long SWITCH_COST = %dL;" % DEF_SWITCH_COST)
F(cfg, "public static volatile long COOLDOWN_MIN = %dL;" % DEF_COOLDOWN_MIN)
F(cfg, "public static volatile boolean REQUIRE_CLASS = %s;" % str(DEF_REQUIRE_CLASS).lower())
F(cfg, "public static volatile boolean ALLOW_SWITCH = false;")  # 0.1.2: class is locked (profiles pick the class)
F(cfg, "public static volatile boolean UNASSIGNED_BLOCKED = %s;" % str(DEF_UNASSIGNED_BLOCKED).lower())
F(cfg, "public static volatile boolean PROMPT_EVERY_LOGIN = %s;" % str(DEF_PROMPT_EVERY_LOGIN).lower())
F(cfg, "public static volatile long OPEN_DELAY_MS = %dL;" % DEF_OPEN_DELAY_MS)
F(cfg, "public static final String[] DEFAULT_LINES = %s;" % jarr(CFG_LINES))
M(cfg, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# 0.1.3: the profile contract helper, verbatim (tools/PROFILES-CONTRACT.md)
M(cfg, r"""
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
M(cfg, r"""
public static boolean profilesOn() {
  return bridge().get("profile:fn:key") instanceof java.util.function.Function;
}""")
# integration fix: SkyyProfiles is loaded but this player has no profile yet (profile:<uuid> absent: no profile, or SkyyProfiles could
# not read their players file) -> the class is picked on SkyyProfiles' create page, not in /class
M(cfg, r"""
public static boolean needsProfile(java.util.UUID u) {
  if (u == null || !profilesOn()) return false;
  return bridge().get("profile:" + u.toString()) == null;
}""")
M(cfg, r"""
public static String profileClass(java.util.UUID u) {
  if (u == null) return null;
  Object o = bridge().get("profile:class:" + u.toString());
  if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  return null;
}""")
M(cfg, r"""
public static String clean(String s, int max) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < max; i++) {
    char c = s.charAt(i);
    if (c >= ' ' && c != 127) sb.append(c);
  }
  return sb.toString();
}""")
M(cfg, r"""
public static long profileEpoch(java.util.UUID u) {
  Object o = bridge().get("profile:epoch:" + u.toString());
  return o instanceof Number ? ((Number) o).longValue() : -1L;
}""")
# display text of the active profile ("Name (profile 2)"), control characters dropped, max 32 chars of name (the page runs safe() on it)
M(cfg, r"""
public static String profileText(java.util.UUID u) {
  if (u == null) return "";
  java.util.Map b = bridge();
  Object id = b.get("profile:" + u.toString());
  Object nm = b.get("profile:name:" + u.toString());
  String raw = "";
  if (nm instanceof String) raw = (String) nm;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < raw.length() && sb.length() < 32; i++) {
    char c = raw.charAt(i);
    if (c >= ' ' && c != 127) sb.append(c);
  }
  String s = sb.toString().trim();
  if (id != null) {
    String ids = String.valueOf(id);
    if (s.length() == 0) s = "profile " + ids;
    else if (!s.equalsIgnoreCase("profile " + ids)) s = s + " (profile " + ids + ")";
  }
  return s;
}""")
M(cfg, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyClasses] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyClasses] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warnLimited(String msg) {
  if (FAILS >= 20) return;
  FAILS++;
  warn(msg + (FAILS == 20 ? " (further errors of this kind are not logged)" : ""));
}""")
M(cfg, r"""
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim().toLowerCase();
  if (v.equals("true") || v.equals("yes") || v.equals("on") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("no") || v.equals("off") || v.equals("0")) return false;
  return d;
}""")
M(cfg, r"""
public static synchronized String load() {
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < DEFAULT_LINES.length; i++) sb.append(DEFAULT_LINES[i]).append("\n");
      java.nio.file.Path tmp = FILE.resolveSibling("config.properties.tmp");
      java.nio.file.Files.write(tmp, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    long cost = lng(p, "switchCost", SWITCH_COST);
    long cd = lng(p, "cooldownMinutes", COOLDOWN_MIN);
    long delay = lng(p, "openDelayMillis", OPEN_DELAY_MS);
    if (cost < 0L) cost = 0L;
    if (cd < 0L) cd = 0L;
    if (delay < 250L) delay = 250L;
    if (delay > 60000L) delay = 60000L;
    SWITCH_COST = cost;
    COOLDOWN_MIN = cd;
    OPEN_DELAY_MS = delay;
    REQUIRE_CLASS = bool(p, "requireClass", REQUIRE_CLASS);
    UNASSIGNED_BLOCKED = bool(p, "unassignedBlocked", UNASSIGNED_BLOCKED);
    PROMPT_EVERY_LOGIN = bool(p, "promptEveryLogin", PROMPT_EVERY_LOGIN);
    return "switchCost=" + SWITCH_COST + " cooldownMinutes=" + COOLDOWN_MIN + " requireClass=" + REQUIRE_CLASS
      + " unassignedBlocked=" + UNASSIGNED_BLOCKED + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS;
  } catch (Throwable t) { warn("could not load config: " + t); return "config load failed: " + t; }
}""")

# ================= ClassDefs: generated from the Python tables =================
F(defs, "public static final int FREE = %d;" % FREE)
F(defs, "public static final int UNASSIGNED = %d;" % UNASSIGNED_OWNER)
F(defs, "public static final String[] NAMES = %s;" % jarr([c["name"] for c in CLASSES]))
F(defs, "public static final String[] SKILLS = %s;" % jarr([c["skill"] for c in CLASSES]))
F(defs, "public static final String[] DESCS = %s;" % jarr([c["desc"] for c in CLASSES]))
F(defs, "public static final String[] COLORS = %s;" % jarr([c["color"] for c in CLASSES]))
F(defs, "public static final String[] WTEXT = %s;" % jarr([c["weapon_text"] for c in CLASSES]))
F(defs, "public static final String[] ICONS = %s;" % jarr([",".join(c["icons"]) for c in CLASSES]))
F(defs, "public static final boolean[] ENABLED = new boolean[] { %s };" % ", ".join("true" if c["enabled"] else "false" for c in CLASSES))
F(defs, "public static final String[] R_PREFIX = %s;" % jarr([r[0] for r in RULES]))
F(defs, "public static final int[] R_OWNER = new int[] { %s };" % ", ".join(str(r[1]) for r in RULES))
F(defs, "public static final String[] R_NOUN = %s;" % jarr([r[2] for r in RULES]))
M(defs, r"""
public static int indexOf(String s) {
  if (s == null) return -1;
  s = s.trim();
  if (s.length() == 0) return -1;
  for (int i = 0; i < NAMES.length; i++) {
    if (NAMES[i].equalsIgnoreCase(s) || SKILLS[i].equalsIgnoreCase(s) || (NAMES[i] + "s").equalsIgnoreCase(s)) return i;
  }
  return -1;
}""")
M(defs, r"""
public static int rule(String id) {
  if (id == null) return -1;
  for (int i = 0; i < R_PREFIX.length; i++) {
    if (id.startsWith(R_PREFIX[i])) return i;
  }
  return -1;
}""")
M(defs, r"""
public static int ownerOf(String id) {
  int r = rule(id);
  return r < 0 ? FREE : R_OWNER[r];
}""")
M(defs, r"""
public static String nounOf(String id) {
  int r = rule(id);
  return r < 0 ? "that item" : R_NOUN[r];
}""")
M(defs, r"""
public static String prefixesOf(int owner) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < R_PREFIX.length; i++) {
    if (R_OWNER[i] != owner) continue;
    if (sb.length() > 0) sb.append(",");
    sb.append(R_PREFIX[i]);
  }
  return sb.toString();
}""")
M(defs, r"""
public static String listText() {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < NAMES.length; i++) {
    if (!ENABLED[i]) continue;
    if (sb.length() > 0) sb.append(",");
    sb.append(NAMES[i]).append(":").append(SKILLS[i]);
  }
  return sb.toString();
}""")
M(defs, r"""
public static String choiceText() {
  StringBuilder sb = new StringBuilder();
  int n = 0;
  for (int i = 0; i < NAMES.length; i++) if (ENABLED[i]) n++;
  int k = 0;
  for (int i = 0; i < NAMES.length; i++) {
    if (!ENABLED[i]) continue;
    k++;
    if (k > 1) sb.append(k == n ? " or " : ", ");
    sb.append(NAMES[i]);
  }
  return sb.toString();
}""")
M(defs, r"""
public static String article(String name) {
  if (name == null || name.length() == 0) return "";
  char c = Character.toUpperCase(name.charAt(0));
  return ("AEIOU".indexOf(c) >= 0 ? "an " : "a ") + name;
}""")

# ================= ClassStore: per-player data, bridge publishing, coins, the choose transaction =================
F(st_, "public static java.nio.file.Path DIR;")
# 0.1.3: DATA (pkey -> Properties) and CLS (pkey -> class name) are keyed by the pkey String (contract rule 2); SESSION stays per UUID
F(st_, "public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();")
F(st_, "public static final java.util.concurrent.ConcurrentHashMap CLS = new java.util.concurrent.ConcurrentHashMap();")
F(st_, "public static final java.util.concurrent.ConcurrentHashMap SESSION = new java.util.concurrent.ConcurrentHashMap();")
F(st_, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();")  # UUID -> last profile:epoch seen
F(st_, "public static volatile boolean BADPROF = false;")
F(st_, "public static volatile boolean BADOFF = false;")
# integration fix: pkey -> Long ms of the last failed read of that player file (not cached; retried at most every 2 s)
F(st_, "public static final java.util.concurrent.ConcurrentHashMap FAILAT = new java.util.concurrent.ConcurrentHashMap();")
# review fix: UUID -> last (epoch|pkey|profile class) snapshot seen by check() and when it was first seen (syncKey only on a steady one)
F(st_, "public static final java.util.concurrent.ConcurrentHashMap SNAP = new java.util.concurrent.ConcurrentHashMap();")
F(st_, "public static final java.util.concurrent.ConcurrentHashMap SNAPAT = new java.util.concurrent.ConcurrentHashMap();")
F(st_, "public static final long SYNC_STEADY_MS = %dL;" % SYNC_STEADY_MS)
M(st_, r"""
public static int fileIndex(String k) {
  if (k == null) return -1;
  Object c = CLS.get(k);
  return c == null ? -1 : @PKG@.ClassDefs.indexOf((String) c);
}""")
# 0.1.3: profile:class:<uuid> is AUTHORITATIVE when present and a known class name; -1 = absent or unknown -> the class file decides.
# Integration fix: a known class that is not playable yet (Assassin, Shaman - /profileadmin setclass allows them) is authoritative
# too: the profile is locked to it and ClassRules.allowed keeps its weapons blocked (never a silent unlock - before, an empty class
# file made the player classless = every weapon allowed, and /class let them pick another class for that profile)
M(st_, r"""
public static int profileIndex(java.util.UUID u) {
  if (u == null) return -1;
  String s = @PKG@.ClassCfg.profileClass(u);
  if (s == null) return -1;
  int i = @PKG@.ClassDefs.indexOf(s);
  if (i >= 0) {
    if (!@PKG@.ClassDefs.ENABLED[i] && !BADOFF) {
      BADOFF = true;
      @PKG@.ClassCfg.warn("profile:class:" + u + " = " + @PKG@.ClassDefs.NAMES[i] + " is not playable yet in SkyyClasses (coming soon) - the profile stays locked to it and its weapons deal no damage (logged once)");
    }
    return i;
  }
  if (!BADPROF) {
    BADPROF = true;
    @PKG@.ClassCfg.warn("profile:class:" + u + " = " + @PKG@.ClassCfg.clean(s, 32) + " is not a SkyyClasses class - using the class file instead (logged once)");
  }
  return -1;
}""")
M(st_, r"""
public static boolean locked(java.util.UUID u) {
  return profileIndex(u) >= 0;
}""")
# bridge values stay keyed by UUID and describe the ACTIVE profile (contract rule 3); k = pkey(u)
# integration fix: synchronized - the class is read and both keys are written in one step, so concurrent publishes (ClassTick, an
# admin command, a choice) never leave class:<uuid> and class:skill:<uuid> describing different classes. Safe under the lock: only
# bridge reads and puts (no profile:fn:key call, no other mod called).
M(st_, r"""
public static synchronized void publishKey(java.util.UUID u, String k) {
  java.util.Map b = @PKG@.ClassCfg.bridge();
  int i = profileIndex(u);
  if (i < 0) i = fileIndex(k);
  if (i < 0) {
    b.remove("class:" + u.toString());
    b.remove("class:skill:" + u.toString());
    return;
  }
  b.put("class:" + u.toString(), @PKG@.ClassDefs.NAMES[i]);
  b.put("class:skill:" + u.toString(), @PKG@.ClassDefs.SKILLS[i]);
}""")
M(st_, r"""
public static long num(java.util.Properties p, String k) {
  try { String v = p.getProperty(k); return v == null ? 0L : Long.parseLong(v.trim()); } catch (Throwable t) { return 0L; }
}""")
# integration fix: a file that exists but cannot be read is NOT cached (0.1.3 cached an empty copy, which the next syncKey / choice /
# prompted flag wrote over the real file). The caller gets an uncached empty Properties (= no class for now), the read is retried at
# most every 2 s, and every save checks DATA.get(k) == its copy, so an unread file is never overwritten. A missing file = empty, cached.
M(st_, r"""
public static synchronized java.util.Properties loadKey(String k) {
  java.util.Properties p = (java.util.Properties) DATA.get(k);
  if (p != null) return p;
  p = new java.util.Properties();
  Long failed = (Long) FAILAT.get(k);
  if (failed != null && System.currentTimeMillis() - failed.longValue() < 2000L) return p;
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) {
    FAILAT.put(k, Long.valueOf(System.currentTimeMillis()));
    @PKG@.ClassCfg.warnLimited("could not read player file " + k + " (not cached, retried every 2 s, never overwritten meanwhile): " + t);
    return new java.util.Properties();
  }
  FAILAT.remove(k);
  DATA.put(k, p);
  int i = @PKG@.ClassDefs.indexOf(p.getProperty("class", ""));
  if (i >= 0) CLS.put(k, @PKG@.ClassDefs.NAMES[i]);
  else CLS.remove(k);
  return p;
}""")
# first load of the active profile's file publishes (0.1.2 load() did the same). synchronized (review fix): the fresh test, the load and
# the publish are one step, so two threads loading the same new pkey publish once. Safe under the lock: publishKey only reads bridge
# values (no profile:fn:key call), and k is computed by the caller outside the lock.
M(st_, r"""
public static synchronized java.util.Properties ensure(java.util.UUID u, String k) {
  boolean fresh = !DATA.containsKey(k);
  java.util.Properties p = loadKey(k);
  if (fresh) publishKey(u, k);
  return p;
}""")
M(st_, r"""
public static java.util.Properties load(java.util.UUID u) {
  return ensure(u, @PKG@.ClassCfg.pkey(u));
}""")
M(st_, r"""
public static int classIndex(java.util.UUID u) {
  if (u == null) return -1;
  int pi = profileIndex(u);
  if (pi >= 0) return pi;
  String k = @PKG@.ClassCfg.pkey(u);
  if (!DATA.containsKey(k)) ensure(u, k);
  return fileIndex(k);
}""")
# integration fix: returns whether the file was written; nothing is written for a key whose file could not be read (not in DATA);
# the atomic replace retries 5 x 20 ms on any FileSystemException (AccessDeniedException, or a sharing violation from a scanner / backup)
M(st_, r"""
public static synchronized boolean saveKey(String k) {
  java.util.Properties p = (java.util.Properties) DATA.get(k);
  if (p == null) { @PKG@.ClassCfg.warnLimited("not saving player " + k + " - its file could not be read yet"); return false; }
  boolean ok = false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyClasses player"); } finally { out.close(); }
    java.nio.file.Path dst = DIR.resolve(k + ".properties");
    int tries = 0;
    while (!ok) {
      try {
        java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
        ok = true;
      } catch (java.nio.file.FileSystemException ade) {
        tries++;
        if (tries >= 5) throw ade;
        Thread.sleep(20L);
      }
    }
  } catch (Throwable t) { @PKG@.ClassCfg.warn("could not save player " + k + ": " + t); }
  return ok;
}""")
# idx < 0 = remove the class. byPlayer = a player's own choice (starts the switch cooldown); paid = counts as a switch
# 0.1.3: k = pkey of the profile being changed, computed by the caller OUTSIDE this lock (pkey may call into SkyyProfiles)
# integration fix: returns false (nothing changed) when the file could not be read or written
M(st_, r"""
public static synchronized boolean setClassKey(String k, int idx, boolean byPlayer, boolean paid) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return false;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  long now = System.currentTimeMillis();
  String n = null;
  if (idx < 0) {
    p.remove("class");
  } else {
    n = @PKG@.ClassDefs.NAMES[idx];
    p.setProperty("class", n);
    String played = p.getProperty("played", "");
    if (("," + played + ",").indexOf("," + n + ",") < 0) p.setProperty("played", played.length() == 0 ? n : played + "," + n);
  }
  p.setProperty("chosenAt", String.valueOf(now));
  p.setProperty("lastChoiceAt", byPlayer ? String.valueOf(now) : "0");
  if (paid) p.setProperty("switches", String.valueOf(num(p, "switches") + 1L));
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return false; }
  if (n == null) CLS.remove(k); else CLS.put(k, n);
  return true;
}""")
M(st_, r"""
public static boolean setClass(java.util.UUID u, int idx, boolean byPlayer, boolean paid) {
  String k = @PKG@.ClassCfg.pkey(u);
  if (!DATA.containsKey(k)) ensure(u, k);
  boolean ok = setClassKey(k, idx, byPlayer, paid);
  publishKey(u, k);
  return ok;
}""")
# 0.1.3: copy the authoritative profile class into that profile's file (offline class:fn:get, /classadmin info, a start without SkyyProfiles)
# integration fix: only a file that was read is changed, and DATA / CLS only take the new class once the file is written (a failed save
# is retried by the next steady check instead of being hidden by the cache)
M(st_, r"""
public static synchronized void syncKey(String k, int pi) {
  if (pi < 0 || pi >= @PKG@.ClassDefs.NAMES.length || !@PKG@.ClassDefs.ENABLED[pi]) return;
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return;
  String n = @PKG@.ClassDefs.NAMES[pi];
  if (n.equals(old.getProperty("class"))) { CLS.put(k, n); return; }
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.setProperty("class", n);
  String played = p.getProperty("played", "");
  if (("," + played + ",").indexOf("," + n + ",") < 0) p.setProperty("played", played.length() == 0 ? n : played + "," + n);
  if (p.getProperty("chosenAt") == null) p.setProperty("chosenAt", String.valueOf(System.currentTimeMillis()));
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return; }
  CLS.put(k, n);
}""")
# review fix: how long (ms) check() has seen exactly this (epoch|pkey|profile class) snapshot for u; 0 = new or changed. Map work only
# (no bridge Function calls) -> safe under ClassStore's lock, and one atomic step for the two maps.
M(st_, r"""
public static synchronized long steadyFor(java.util.UUID u, String snap) {
  long now = System.currentTimeMillis();
  Object prev = SNAP.put(u, snap);
  Long at = (Long) SNAPAT.get(u);
  if (prev == null || at == null || !snap.equals(prev)) {
    SNAPAT.put(u, Long.valueOf(now));
    return 0L;
  }
  return now - at.longValue();
}""")
# 0.1.3 contract rule 3: republish class:<uuid> / class:skill:<uuid> when profile:epoch:<uuid> changed (or the published value drifted)
# review fix: pkey and profile:class are two separate reads and SkyyProfiles may update them in separate steps during a switch. The
# bridge publish self-heals on the next tick, a file write does not -> syncKey only runs when the snapshot (epoch, pkey, class) has held
# for >= SYNC_STEADY_MS across checks AND a re-read right before the write still matches it (a mid-switch pair never reaches the disk;
# a re-read that differs restarts the steady clock).
# Integration fix: the write also needs profile:key:<uuid> == pkey. SkyyProfiles flips the Function when the players file is committed
# and publishes key, class, epoch a moment later, so "new key + old class + old epoch" is the mid-switch view; the bridge key still
# shows the old key there, so even a long stall between commit and publish can never write the old profile's class into the new file.
M(st_, r"""
public static void check(java.util.UUID u) {
  if (u == null) return;
  long e = @PKG@.ClassCfg.profileEpoch(u);
  Long last = (Long) EPOCH.get(u);
  boolean changed = last == null || last.longValue() != e;
  String k = @PKG@.ClassCfg.pkey(u);
  loadKey(k);
  int pi = profileIndex(u);
  long steady = steadyFor(u, e + "|" + k + "|" + pi);
  if (pi >= 0 && @PKG@.ClassDefs.ENABLED[pi] && fileIndex(k) != pi && steady >= SYNC_STEADY_MS) {
    long e2 = @PKG@.ClassCfg.profileEpoch(u);
    String k2 = @PKG@.ClassCfg.pkey(u);
    int pi2 = profileIndex(u);
    Object kk = @PKG@.ClassCfg.bridge().get("profile:key:" + u.toString());
    if (e2 == e && pi2 == pi && k.equals(k2) && k.equals(kk)) syncKey(k, pi);
    else steadyFor(u, e2 + "|" + k2 + "|" + pi2);   // a switch is under way: restart the steady clock from the newer snapshot
  }
  int i = pi >= 0 ? pi : fileIndex(k);
  String want = null;
  if (i >= 0) want = @PKG@.ClassDefs.NAMES[i];
  Object pub = @PKG@.ClassCfg.bridge().get("class:" + u.toString());
  boolean same = false;
  if (want == null) same = pub == null;
  else same = want.equals(pub);
  if (changed || !same) publishKey(u, k);
  if (changed) EPOCH.put(u, Long.valueOf(e));
}""")
M(st_, r"""
public static long cooldownLeftKey(String k) {
  java.util.Properties p = loadKey(k);
  long last = num(p, "lastChoiceAt");
  if (last <= 0L) return 0L;
  long left = last + @PKG@.ClassCfg.COOLDOWN_MIN * 60000L - System.currentTimeMillis();
  return left > 0L ? left : 0L;
}""")
M(st_, r"""
public static long cooldownLeft(java.util.UUID u) {
  java.util.Properties p = load(u);
  long last = num(p, "lastChoiceAt");
  if (last <= 0L) return 0L;
  long left = last + @PKG@.ClassCfg.COOLDOWN_MIN * 60000L - System.currentTimeMillis();
  return left > 0L ? left : 0L;
}""")
M(st_, r"""
public static boolean wasPrompted(java.util.UUID u) {
  return "1".equals(load(u).getProperty("prompted"));
}""")
M(st_, r"""
public static synchronized void markPromptedKey(String k) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old || "1".equals(old.getProperty("prompted"))) return;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.setProperty("prompted", "1");
  DATA.put(k, p);
  if (!saveKey(k)) DATA.put(k, old);
}""")
M(st_, r"""
public static void markPrompted(java.util.UUID u) {
  String k = @PKG@.ClassCfg.pkey(u);
  if (!DATA.containsKey(k)) ensure(u, k);
  markPromptedKey(k);
}""")
M(st_, r"""
public static boolean coinsReady() {
  java.util.Map b = @PKG@.ClassCfg.bridge();
  return b.get("coins:fn:get") instanceof java.util.function.Function && b.get("coins:fn:take") instanceof java.util.function.Function;
}""")
M(st_, r"""
public static long purse(java.util.UUID u) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("coins:fn:get");
    if (!(f instanceof java.util.function.Function)) return 0L;
    Object r = ((java.util.function.Function) f).apply(u);
    return r instanceof Number ? ((Number) r).longValue() : 0L;
  } catch (Throwable t) { return 0L; }
}""")
M(st_, r"""
public static boolean purseTake(java.util.UUID u, long n) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("coins:fn:take");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    return r instanceof Boolean && ((Boolean) r).booleanValue();
  } catch (Throwable t) { @PKG@.ClassCfg.warn("coins:fn:take failed: " + t); return false; }
}""")
M(st_, r"""
public static String fmtTime(long ms) {
  long s = (ms + 999L) / 1000L;
  if (s < 60L) return s + " s";
  long m = (s + 59L) / 60L;
  if (m < 60L) return m + " min";
  if (m % 60L == 0L) return (m / 60L) + " h";
  return (m / 60L) + " h " + (m % 60L) + " min";
}""")
# the player's own choice: null = done, otherwise the reason it was refused. synchronized -> no double charge on double clicks
# 0.1.3: chooseKey works on one profile's file (k from the caller, outside the lock); a profile-locked class (SkyyProfiles) is refused
M(st_, r"""
public static synchronized String chooseKey(java.util.UUID u, String k, int idx) {
  if (idx < 0 || idx >= @PKG@.ClassDefs.NAMES.length) return "Unknown class.";
  String name = @PKG@.ClassDefs.NAMES[idx];
  if (locked(u)) return "Your class is locked to this profile. A new class means a new profile.";
  if (@PKG@.ClassCfg.needsProfile(u)) return "Create your profile with /profiles - you pick your class there and it is locked to that profile.";
  if (!@PKG@.ClassDefs.ENABLED[idx]) return name + "s are coming soon.";
  if (!DATA.containsKey(k)) ensure(u, k);
  if (!DATA.containsKey(k)) return "Your class file could not be read - try again in a moment.";
  int cur = fileIndex(k);
  if (cur == idx) return "You already are " + @PKG@.ClassDefs.article(name) + ".";
  if (cur < 0) {
    if (!setClassKey(k, idx, true, false)) return "Your class could not be saved - try again in a moment.";
    return null;
  }
  if (!@PKG@.ClassCfg.ALLOW_SWITCH) return "Your class is locked. A new class means a new profile (SkyyProfiles).";
  long left = cooldownLeftKey(k);
  if (left > 0L) return "You can switch class again in " + fmtTime(left) + ".";
  long cost = @PKG@.ClassCfg.SWITCH_COST;
  if (cost > 0L) {
    if (!coinsReady()) return "Switching costs " + cost + " coins but SkyyCoins is not loaded - ask an admin.";
    if (!purseTake(u, cost)) return "Switching costs " + cost + " coins - you have " + purse(u) + ".";
  }
  if (!setClassKey(k, idx, true, cost > 0L)) return "Your class could not be saved - try again in a moment.";
  return null;
}""")
M(st_, r"""
public static String choose(java.util.UUID u, int idx) {
  String k = @PKG@.ClassCfg.pkey(u);
  String r = chooseKey(u, k, idx);
  if (r == null) publishKey(u, k);
  return r;
}""")
M(st_, r"""
public static java.util.UUID resolve(String s) {
  if (s == null) return null;
  s = s.trim();
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ p = (@PR@) it.next();
    if (p != null && p.getUsername() != null && p.getUsername().equalsIgnoreCase(s)) return p.getUuid();
  }
  try { return java.util.UUID.fromString(s); } catch (Throwable t) { return null; }
}""")
# review fix: one pkey for the whole line (file, class, cooldown), and the trailing clause says where the class in force comes from
M(st_, r"""
public static String describe(java.util.UUID u) {
  String k = @PKG@.ClassCfg.pkey(u);
  java.util.Properties p = ensure(u, k);
  int pi = profileIndex(u);
  int ci = pi >= 0 ? pi : fileIndex(k);
  long left = cooldownLeftKey(k);
  String prof = "";
  if (@PKG@.ClassCfg.profilesOn()) {
    String pt = @PKG@.ClassCfg.profileText(u);
    String raw = pi >= 0 ? null : @PKG@.ClassCfg.profileClass(u);
    String why = " - the profile has no class";
    if (pi >= 0) why = " - class locked by the profile" + (@PKG@.ClassDefs.ENABLED[pi] ? "" : " (not playable yet - its weapons deal no damage)");
    else if (raw != null) why = " - profile class " + @PKG@.ClassCfg.clean(raw, 32) + " is not playable in SkyyClasses" + (ci >= 0 ? " - using the class chosen for this profile file" : " - no class in this profile file");
    else if (ci >= 0) why = " - class chosen for this profile file, not locked by SkyyProfiles";
    prof = " | " + (pt.length() > 0 ? pt : "no active profile") + " file " + k + why;
  }
  return (ci < 0 ? "no class" : @PKG@.ClassDefs.NAMES[ci] + " (" + @PKG@.ClassDefs.SKILLS[ci] + ")")
    + " | switches " + num(p, "switches") + " | played " + p.getProperty("played", "-")
    + " | switch cooldown " + (left > 0L ? fmtTime(left) : "none") + prof;
}""")

# ================= ClassRules: may this player deal damage with this item =================
F(rul, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")
F(rul, "public static final java.util.concurrent.ConcurrentHashMap POPPED = new java.util.concurrent.ConcurrentHashMap();")
M(rul, r"""
public static boolean allowed(java.util.UUID u, String id) {
  if (id == null || id.length() == 0) return true;
  int owner = @PKG@.ClassDefs.ownerOf(id);
  if (owner == @PKG@.ClassDefs.FREE) return true;
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) return !@PKG@.ClassCfg.REQUIRE_CLASS;
  if (owner == ci && @PKG@.ClassDefs.ENABLED[ci]) return true;
  if (owner == @PKG@.ClassDefs.UNASSIGNED || !@PKG@.ClassDefs.ENABLED[owner]) return !@PKG@.ClassCfg.UNASSIGNED_BLOCKED;
  return false;
}""")
M(rul, r"""
public static String blockText(java.util.UUID u, String id, boolean util) {
  int owner = @PKG@.ClassDefs.ownerOf(id);
  String noun = @PKG@.ClassDefs.nounOf(id);
  String where = util ? " (it is in your utility slot)" : "";
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) return (@PKG@.ClassCfg.profilesOn() ? "Create a profile with /profiles to get a class" : "Choose a class with /class") + " before fighting with weapons" + where + ".";
  if (owner >= 0 && @PKG@.ClassDefs.ENABLED[owner]) return "Only " + @PKG@.ClassDefs.NAMES[owner] + "s can use " + noun + where + ". You are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[ci]) + " - /class shows your weapons.";
  if (owner >= 0) return @PKG@.ClassDefs.NAMES[owner] + "s are coming soon - nobody can fight with " + noun + " yet" + where + ".";
  return "No class can fight with " + noun + " yet" + where + ".";
}""")
M(rul, r"""
public static void tell(@PR@ pr, java.util.UUID u, String text) {
  long now = System.currentTimeMillis();
  Long last = (Long) WARNED.get(u);
  if (last != null && now - last.longValue() < %dL) return;
  WARNED.put(u, Long.valueOf(now));
  pr.sendMessage(@MSG@.raw("[Classes] " + text).color("#ff9d6b"));
}""" % MSG_THROTTLE_MS)

M(rul, r"""
public static void popup(@PR@ pr, java.util.UUID u, String id, String text) {
  try {
    long now = System.currentTimeMillis();
    Long last = (Long) POPPED.get(u);
    if (last != null && now - last.longValue() < 1500L) return;
    POPPED.put(u, Long.valueOf(now));
    String head = @PKG@.ClassStore.classIndex(u) < 0 ? (@PKG@.ClassCfg.profilesOn() ? "Create a profile first" : "Choose a class first") : "You can't use this weapon";
    @MSG@ title = @MSG@.raw(head).color("#ff9d6b");
    @MSG@ body = @MSG@.raw(text);
    @IWM@ icon = null;
    try { if (id != null && id.length() > 0) icon = (@IWM@) new @IS@(id, 1).toPacket(); } catch (Throwable t0) { icon = null; }
    if (icon != null) @NTU@.sendNotification(pr.getPacketHandler(), title, body, icon, @NST@.Warning);
    else @NTU@.sendNotification(pr.getPacketHandler(), title, body, @NST@.Warning);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("popup failed: " + t); }
}""")

# ================= bridge functions =================
afn.addInterface(pool.get("java.util.function.Function"))
C(afn, "public AllowedFn() { }")
M(afn, r"""
public Object apply(Object o) {
  try {
    Object[] a = (Object[]) o;
    return Boolean.valueOf(@PKG@.ClassRules.allowed((java.util.UUID) a[0], a[1] == null ? null : String.valueOf(a[1])));
  } catch (Throwable t) { return Boolean.TRUE; }
}""")
gfn.addInterface(pool.get("java.util.function.Function"))
C(gfn, "public GetFn() { }")
M(gfn, r"""
public Object apply(Object o) {
  try {
    int i = @PKG@.ClassStore.classIndex((java.util.UUID) o);
    return i < 0 ? null : @PKG@.ClassDefs.NAMES[i];
  } catch (Throwable t) { return null; }
}""")

# ================= ShotRec + ShotTrack: what the shooter held when a projectile / bomb was LAUNCHED =================
# SimpleEnchantments EnchantmentProjectileSpeedSystem pattern (RefSystem, AddReason.SPAWN, creator uuid -> EntityStore.getRefFromUUID,
# record keyed by the projectile's UUIDComponent, removed in onEntityRemove). bad = the forbidden item id (null = the launch was allowed).
F(srec, "public java.util.UUID shooter;")
F(srec, "public String bad;")
F(srec, "public boolean util;")
F(srec, "public long at;")
C(srec, r"""
public ShotRec(java.util.UUID shooter, String bad, boolean util) {
  this.shooter = shooter;
  this.bad = bad;
  this.util = util;
  this.at = System.currentTimeMillis();
}""")
F(strk, "public static final java.util.concurrent.ConcurrentHashMap SHOTS = new java.util.concurrent.ConcurrentHashMap();")
F(strk, "public @QRY@ query;")
C(strk, "public ShotTrack() { super(); this.query = null; }")
M(strk, r"""
public static String badOf(java.util.UUID u, @IS@ it) {
  if (it == null || it.isEmpty()) return null;
  String id = it.getItemId();
  return @PKG@.ClassRules.allowed(u, id) ? null : id;
}""")
M(strk, r"""
public static void purge() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = SHOTS.values().iterator();
  while (it.hasNext()) {
    @PKG@.ShotRec r = (@PKG@.ShotRec) it.next();
    if (r == null || now - r.at > %dL) it.remove();
  }
}""" % SHOT_PURGE_MS)
M(strk, r"""
public static @PKG@.ShotRec find(@CB@ buf, @REF@ pj) {
  if (pj == null || !pj.isValid() || SHOTS.isEmpty()) return null;
  @UUIDC@ idc = (@UUIDC@) buf.getComponent(pj, @UUIDC@.getComponentType());
  if (idc == null || idc.getUuid() == null) return null;
  return (@PKG@.ShotRec) SHOTS.get(idc.getUuid());
}""")
M(strk, r"""
public static @PKG@.ShotRec liveBad(java.util.UUID u) {
  if (u == null || SHOTS.isEmpty()) return null;
  long now = System.currentTimeMillis();
  java.util.Iterator it = SHOTS.values().iterator();
  while (it.hasNext()) {
    @PKG@.ShotRec r = (@PKG@.ShotRec) it.next();
    if (r != null && r.bad != null && u.equals(r.shooter) && now - r.at < %dL) return r;
  }
  return null;
}""" % SHOT_WINDOW_MS)
M(strk, r"""
public @QRY@ getQuery() {
  if (this.query == null) {
    this.query = @QRY@.and(new @QRY@[] { @TC@.getComponentType(), @QRY@.or(new @QRY@[] { @LPC@.getComponentType(), @SPP@.getComponentType() }) });
  }
  return this.query;
}""")
M(strk, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (reason != @ADDR@.SPAWN) return;
    java.util.UUID creator = null;
    @SPP@ sp = (@SPP@) buf.getComponent(ref, @SPP@.getComponentType());
    if (sp != null) creator = sp.getCreatorUuid();
    if (creator == null) {
      @LPC@ lp = (@LPC@) buf.getComponent(ref, @LPC@.getComponentType());
      if (lp != null) creator = lp.getCreatorUuid();
    }
    if (creator == null) return;
    @UUIDC@ idc = (@UUIDC@) buf.getComponent(ref, @UUIDC@.getComponentType());
    if (idc == null || idc.getUuid() == null) return;
    @REF@ sh = ((@ES@) buf.getExternalData()).getRefFromUUID(creator);
    if (sh == null || !sh.isValid()) return;
    @PR@ pr = (@PR@) buf.getComponent(sh, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    String bad = badOf(u, @INVC@.getItemInHand(buf, sh));
    boolean util = false;
    if (bad == null) {
      @UTIL@ ut = (@UTIL@) buf.getComponent(sh, @UTIL@.getComponentType());
      bad = badOf(u, ut == null ? null : ut.getActiveItem());
      util = bad != null;
    }
    if (SHOTS.size() > %d) purge();
    SHOTS.put(idc.getUuid(), new @PKG@.ShotRec(u, bad, util));
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("shot tracker failed: " + t); }
}""" % SHOT_PURGE_AT)
M(strk, r"""
public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (SHOTS.isEmpty()) return;
    @UUIDC@ idc = (@UUIDC@) buf.getComponent(ref, @UUIDC@.getComponentType());
    if (idc != null && idc.getUuid() != null) SHOTS.remove(idc.getUuid());
  } catch (Throwable t) { }
}""")

# ================= DamageLock: cancel damage dealt with a weapon the attacker's class may not use =================
C(lock, "public DamageLock() { super(); }")
M(lock, r"""
public @QRY@ getQuery() {
  return @QRY@.any();
}""")
M(lock, r"""
public @SG@ getGroup() {
  return @DMOD@.get().getFilterDamageGroup();
}""")
M(lock, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    java.util.UUID u = null;
    @PR@ pr = null;
    String bad = null;
    boolean util = false;
    @PKG@.ShotRec rec = null;
    if (src instanceof @DPRJ@) rec = @PKG@.ShotTrack.find(buf, ((@DPRJ@) src).getProjectile());
    if (rec != null) {
      u = rec.shooter;
      bad = rec.bad;
      util = rec.util;
      pr = @UNI@.get().getPlayer(u);
    } else {
      @REF@ att = ((@DENT@) src).getRef();
      if (att == null || !att.isValid()) return;
      pr = (@PR@) buf.getComponent(att, @PR@.getComponentType());
      if (pr == null) return;
      u = pr.getUuid();
      @IS@ main = @INVC@.getItemInHand(buf, att);
      if (main != null && !main.isEmpty()) {
        String id = main.getItemId();
        if (!@PKG@.ClassRules.allowed(u, id)) bad = id;
      }
      if (bad == null) {
        @UTIL@ ut = (@UTIL@) buf.getComponent(att, @UTIL@.getComponentType());
        @IS@ ui = ut == null ? null : ut.getActiveItem();
        if (ui != null && !ui.isEmpty()) {
          String id2 = ui.getItemId();
          if (!@PKG@.ClassRules.allowed(u, id2)) { bad = id2; util = true; }
        }
      }
      if (bad == null) {
        @PKG@.ShotRec lb = @PKG@.ShotTrack.liveBad(u);
        if (lb != null) { bad = lb.bad; util = lb.util; }
      }
    }
    if (bad == null) return;
    d.setAmount(0.0f);
    d.setCancelled(true);
    buf.tryRemoveComponent(chunk.getReferenceTo(idx), @KBC@.getComponentType());
    if (pr != null && pr.isValid()) {
      String bt = @PKG@.ClassRules.blockText(u, bad, util);
      @PKG@.ClassRules.tell(pr, u, bt);
      @PKG@.ClassRules.popup(pr, u, bad, bt);
    }
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("damage lock failed: " + t); }
}""")

# ================= ClassPage: /class =================
BTN = ("Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 12, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
       "Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
       "Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
BTN_GO = ("Style: TextButtonStyle(Default: (Background: #2f6a3a, LabelStyle: (FontSize: 12, TextColor: #e9ffe9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
          "Hovered: (Background: #3f8a4a, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
          "Pressed: (Background: #1f4a2a, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
PAGE_W, PAGE_H = 780, 616
F(page, "public int pending;")
F(page, "public String info;")
C(page, r"""
public ClassPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.pending = -1;
  this.info = "";
}""")
M(page, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\'', ' ').replace('\\', ' ');
}""")
M(page, (r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int pi = @PKG@.ClassStore.profileIndex(u);
  boolean lockp = pi >= 0;
  boolean np = !lockp && @PKG@.ClassCfg.needsProfile(u);
  int cur = lockp ? pi : @PKG@.ClassStore.classIndex(u);
  String bs = "__BTN__";
  String go = "__BTNGO__";
  b.appendInline((String) null, "Group #SkyyCls { Anchor: (Width: __W__, Height: __H__); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }");
  b.appendInline("#SkyyCls", "Group { Anchor: (Height: 2); Background: #d08a4a; }");
  b.appendInline("#SkyyCls", "Label { Anchor: (Height: 30); Text: \"Classes\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  String sub = cur < 0 ? "You have no class yet - your first choice is free. Your class decides your weapons and your combat skill."
    : "You are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[cur]) + " - combat skill " + @PKG@.ClassDefs.SKILLS[cur] + ". Only " + @PKG@.ClassDefs.NAMES[cur] + " weapons deal damage for you.";
  if (lockp) sub = "Your class is locked to this profile - you are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[cur]) + " with combat skill " + @PKG@.ClassDefs.SKILLS[cur] + ". A new class means a new profile.";
  if (lockp && !@PKG@.ClassDefs.ENABLED[cur]) sub = "This profile is locked to " + @PKG@.ClassDefs.NAMES[cur] + " - not playable yet. Its weapons deal no damage until it is released.";
  if (np) sub = "You have no profile yet. Type /profiles to create one - you pick your class there and it is locked to that profile.";
  b.appendInline("#SkyyCls", "Label #SkyyClsSub { Anchor: (Height: 20); Text: \"" + safe(sub) + "\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  for (int i = 0; i < @PKG@.ClassDefs.NAMES.length; i++) {
    boolean on = @PKG@.ClassDefs.ENABLED[i];
    boolean sel = i == cur;
    boolean pend = i == this.pending;
    String bg = sel ? "#173524(0.95)" : (pend ? "#3a2f1a(0.95)" : (on ? "#142030(0.9)" : "#0d1219(0.85)"));
    String nameColor = on ? @PKG@.ClassDefs.COLORS[i] : "#5f6b78";
    String textColor = on ? "#c9d6e2" : "#5f6b78";
    b.appendInline("#SkyyCls", "Label { Anchor: (Height: 6); Text: \"\"; }");
    b.appendInline("#SkyyCls", "Group #SkyyClsCard" + i + " { Anchor: (Height: 86); LayoutMode: Left; Background: " + bg + "; }");
    b.appendInline("#SkyyClsCard" + i, "Label { Anchor: (Width: 10, Height: 86); Text: \"\"; }");
    b.appendInline("#SkyyClsCard" + i, "Group #SkyyClsIco" + i + " { Anchor: (Width: 190, Height: 86); LayoutMode: Left; }");
    String[] ic = @PKG@.ClassDefs.ICONS[i].split(",");
    for (int k = 0; k < ic.length && k < 4; k++) {
      b.appendInline("#SkyyClsIco" + i, "Group { Anchor: (Width: 47, Height: 86); ItemIcon { Anchor: (Width: 40, Height: 40, Left: 3, Top: 23); ItemId: \"" + safe(ic[k]) + "\"; } }");
    }
    b.appendInline("#SkyyClsCard" + i, "Group #SkyyClsTxt" + i + " { Anchor: (Width: 390, Height: 86); LayoutMode: Top; Padding: (Top: 4); }");
    String title = @PKG@.ClassDefs.NAMES[i] + (sel ? " - your class" : (on ? "" : " - coming soon"));
    b.appendInline("#SkyyClsTxt" + i, "Label { Anchor: (Height: 24); Text: \"" + safe(title) + "\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + nameColor + ", VerticalAlignment: Center); }");
    b.appendInline("#SkyyClsTxt" + i, "Label { Anchor: (Height: 18); Text: \"" + safe("Combat skill " + @PKG@.ClassDefs.SKILLS[i] + " - " + @PKG@.ClassDefs.WTEXT[i]) + "\"; Style: (FontSize: 11, RenderBold: true, TextColor: " + (on ? "#9fd8a2" : "#5f6b78") + ", VerticalAlignment: Center); }");
    b.appendInline("#SkyyClsTxt" + i, "Label { Anchor: (Height: 38); Text: \"" + safe(@PKG@.ClassDefs.DESCS[i]) + "\"; Style: (FontSize: 11, TextColor: " + textColor + ", VerticalAlignment: Center, Wrap: true); }");
    b.appendInline("#SkyyClsCard" + i, "Group #SkyyClsAct" + i + " { Anchor: (Width: 136, Height: 86); LayoutMode: Top; Padding: (Top: 27); }");
    if (lockp && sel) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 130, Height: 30); Text: \"Selected\"; Style: (FontSize: 13, RenderBold: true, TextColor: #8fe39a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else if (!on) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 130, Height: 30); Text: \"Coming soon\"; Style: (FontSize: 12, RenderBold: true, TextColor: #5f6b78, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else if (sel) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 130, Height: 30); Text: \"Selected\"; Style: (FontSize: 13, RenderBold: true, TextColor: #8fe39a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else if (lockp || np) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 130, Height: 30); Text: \"Locked\"; Style: (FontSize: 12, RenderBold: true, TextColor: #5f6b78, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else {
      b.appendInline("#SkyyClsAct" + i, "TextButton #SkyyClsPick" + i + " { Anchor: (Width: 130, Height: 30); Text: \"" + (cur < 0 ? "Choose" : "Switch") + "\"; " + (pend ? go : bs) + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyClsPick" + i, @EVD@.of("a", "clspick" + i));
    }
  }
  b.appendInline("#SkyyCls", "Label { Anchor: (Height: 8); Text: \"\"; }");
  b.appendInline("#SkyyCls", "Label #SkyyClsInfo { Anchor: (Height: 22); Text: \"" + safe(this.info) + "\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffd27a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  long cost = @PKG@.ClassCfg.SWITCH_COST;
  if (!lockp && !np && this.pending >= 0 && this.pending < @PKG@.ClassDefs.NAMES.length) {
    String pn = @PKG@.ClassDefs.NAMES[this.pending];
    String q = cur < 0 ? "Become " + @PKG@.ClassDefs.article(pn) + "? Your first choice is free."
      : "Switch to " + pn + " for " + cost + " coins? Your " + @PKG@.ClassDefs.NAMES[cur] + " progress is kept.";
    b.appendInline("#SkyyCls", "Group #SkyyClsConfirm { Anchor: (Height: 34); LayoutMode: Left; Padding: (Top: 2); }");
    b.appendInline("#SkyyClsConfirm", "Label { Anchor: (Width: 470, Height: 30); Text: \"" + safe(q) + "\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }");
    b.appendInline("#SkyyClsConfirm", "TextButton #SkyyClsYes { Anchor: (Width: 120, Height: 28); Text: \"Confirm\"; " + go + " }");
    b.appendInline("#SkyyClsConfirm", "Label { Anchor: (Width: 10, Height: 28); Text: \"\"; }");
    b.appendInline("#SkyyClsConfirm", "TextButton #SkyyClsNo { Anchor: (Width: 120, Height: 28); Text: \"Cancel\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyClsYes", @EVD@.of("a", "clsyes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyClsNo", @EVD@.of("a", "clsno"));
  } else if (np) {
    String nf = "Your class comes from your profile - type /profiles to create it. Shields and tools work for every class.";
    b.appendInline("#SkyyCls", "Label #SkyyClsFoot { Anchor: (Height: 30); Text: \"" + safe(nf) + "\"; Style: (FontSize: 11, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  } else if (lockp) {
    String pt = @PKG@.ClassCfg.profileText(u);
    String lf = "Class locked to " + (pt.length() > 0 ? pt : "this profile") + ". To play another class create a new profile. Shields and tools work for every class.";
    b.appendInline("#SkyyCls", "Label #SkyyClsFoot { Anchor: (Height: 30); Text: \"" + safe(lf) + "\"; Style: (FontSize: 11, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  } else {
    String foot = "Switching costs " + cost + " coins (first choice free) - cooldown " + @PKG@.ClassCfg.COOLDOWN_MIN + " min"
      + (@PKG@.ClassStore.coinsReady() ? " - purse " + @PKG@.ClassStore.purse(u) + " coins" : "") + ". Shields and tools work for every class.";
    b.appendInline("#SkyyCls", "Label #SkyyClsFoot { Anchor: (Height: 30); Text: \"" + safe(foot) + "\"; Style: (FontSize: 11, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  }
}""").replace("__BTN__", BTN.replace('"', '\\"')).replace("__BTNGO__", BTN_GO.replace('"', '\\"')).replace("__W__", str(PAGE_W)).replace("__H__", str(PAGE_H)))
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    if (@PKG@.ClassStore.locked(u)) {
      this.pending = -1;
      this.info = "Your class is locked to this profile - a new class means a new profile.";
      rebuild(); return;
    }
    if (@PKG@.ClassCfg.needsProfile(u)) {
      this.pending = -1;
      this.info = "Create your profile with /profiles - you pick your class there.";
      rebuild(); return;
    }
    for (int i = 0; i < @PKG@.ClassDefs.NAMES.length; i++) {
      if (data.indexOf("clspick" + i + "\"") < 0) continue;
      this.pending = -1;
      if (!@PKG@.ClassDefs.ENABLED[i]) { this.info = @PKG@.ClassDefs.NAMES[i] + "s are coming soon."; rebuild(); return; }
      int cur = @PKG@.ClassStore.classIndex(u);
      if (cur == i) { this.info = "That is already your class."; rebuild(); return; }
      if (cur >= 0) {
        long left = @PKG@.ClassStore.cooldownLeft(u);
        if (left > 0L) { this.info = "You can switch class again in " + @PKG@.ClassStore.fmtTime(left) + "."; rebuild(); return; }
        long cost = @PKG@.ClassCfg.SWITCH_COST;
        if (cost > 0L && !@PKG@.ClassStore.coinsReady()) { this.info = "Switching costs " + cost + " coins but SkyyCoins is not loaded - ask an admin."; rebuild(); return; }
        if (cost > 0L && @PKG@.ClassStore.purse(u) < cost) { this.info = "Switching costs " + cost + " coins - you have " + @PKG@.ClassStore.purse(u) + "."; rebuild(); return; }
      }
      this.pending = i;
      this.info = "";
      rebuild(); return;
    }
    if (data.indexOf("clsyes\"") >= 0) {
      if (this.pending < 0) return;
      int p = this.pending;
      this.pending = -1;
      String err = @PKG@.ClassStore.choose(u, p);
      if (err != null) { this.info = err; rebuild(); return; }
      String n = @PKG@.ClassDefs.NAMES[p];
      this.info = "You are now " + @PKG@.ClassDefs.article(n) + "! Combat skill " + @PKG@.ClassDefs.SKILLS[p] + ".";
      this.playerRef.sendMessage(@MSG@.raw("[Classes] You are now " + @PKG@.ClassDefs.article(n) + "! Your weapons: " + @PKG@.ClassDefs.WTEXT[p] + ". Your combat skill: " + @PKG@.ClassDefs.SKILLS[p] + ".").color("#8fe39a"));
      rebuild(); return;
    }
    if (data.indexOf("clsno\"") >= 0) { this.pending = -1; this.info = ""; rebuild(); return; }
  } catch (Throwable t) { @PKG@.ClassCfg.warn("class page event failed: " + t); }
}""")

# ================= OpenTask: first-join page open (SkyyHud AttachTask pattern: delay, world-thread hop, WorldMap channel gate) =================
# Only without SkyyProfiles. Cross-mod timeline pass (same guards as SkyyProfiles' Create Profile page): calm resets when the player's
# world changes between polls (opens only after 2 polls in one world); waits up to ISLAND_WAIT_MS while the player stands in a
# skyy-island-* world (SkyyIslands routes island logins to the hub 1.5 s after the first PlayerReadyEvent - a page opened just before
# that teleport is lost); never replaces an open custom page (our own ClassPage opened with /class -> done; any other, e.g. the
# SkyyMenu page -> wait until it is closed); never opens over the respawn screen. Gives up after 240 polls (2 min).
opn.addInterface(pool.get("java.lang.Runnable"))
F(opn, "public static final long ISLAND_WAIT_MS = 8000L;")
F(opn, "public @PR@ pr;")
F(opn, "public boolean onWorld;")
F(opn, "public int calm;")
F(opn, "public int tries;")
F(opn, "public java.util.UUID wu;")
F(opn, "public java.util.UUID lastWorld;")
F(opn, "public long born;")
C(opn, "public OpenTask(@PR@ pr) { this.pr = pr; this.onWorld = false; this.calm = 0; this.tries = 0; this.wu = null; this.lastWorld = null; this.born = System.currentTimeMillis(); }")
M(opn, r"""
public void later(long ms) {
  this.onWorld = false;
  @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
M(opn, r"""
public void again(boolean unsettled) {
  if (unsettled) this.calm = 0;
  if (++this.tries < 240) later(500L);
}""")
M(opn, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    if (!this.onWorld) {
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) { again(true); return; }
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null) { again(true); return; }
      this.wu = wu;
      this.onWorld = true;
      w.execute(this);
      return;
    }
    java.util.UUID now = pr.getWorldUuid();
    if (now == null || !now.equals(this.wu)) { again(true); return; }
    if (@PKG@.ClassCfg.profilesOn()) return;
    if (@PKG@.ClassStore.classIndex(pr.getUuid()) >= 0) return;
    if (this.lastWorld == null || !this.lastWorld.equals(now)) { this.lastWorld = now; this.calm = 0; }
    @WLD@ here = @UNI@.get().getWorld(now);
    String wn = here == null ? null : here.getName();
    if (wn != null && wn.startsWith("skyy-island-") && System.currentTimeMillis() - this.born < ISLAND_WAIT_MS) { again(true); return; }
    @REF@ r = pr.getReference();
    if (r == null) { again(true); return; }
    @ST@ st = r.getStore();
    if (st == null) { again(true); return; }
    @PLA@ player = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (player == null) { again(true); return; }
    if (st.getComponent(r, com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent.getComponentType()) != null) { again(true); return; }
    Object cp = player.getPageManager().getCustomPage();
    if (cp instanceof @PKG@.ClassPage) return;
    if (cp != null) { again(true); return; }
    boolean writable = true;
    try {
      com.hypixel.hytale.server.core.io.PacketHandler ph = player.getPlayerConnection();
      com.hypixel.hytale.protocol.io.ChannelConnection ch = ph == null ? null : ph.getChannel(com.hypixel.hytale.protocol.NetworkChannel.WorldMap);
      writable = ch == null || ch.isWritable();
    } catch (Throwable t) { writable = true; }
    if (writable) this.calm++; else this.calm = 0;
    if (this.calm < 2) { again(false); return; }
    player.getPageManager().openCustomPage(r, st, new @PKG@.ClassPage(pr));
    @PKG@.ClassStore.markPrompted(pr.getUuid());
  } catch (Throwable t) { @PKG@.ClassCfg.warn("could not open the class page on join: " + t); }
}""")

# ================= ReadyTask: first-join work OFF the world thread (player file read = disk I/O) =================
rtk.addInterface(pool.get("java.lang.Runnable"))
F(rtk, "public @PR@ pr;")
C(rtk, "public ReadyTask(@PR@ pr) { this.pr = pr; }")
M(rtk, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.ClassStore.load(u);
    if (@PKG@.ClassCfg.profilesOn()) { @PKG@.ClassStore.check(u); return; }
    if (@PKG@.ClassStore.classIndex(u) >= 0) return;
    pr.sendMessage(@MSG@.raw("[Classes] You have no class yet. Type /class to choose " + @PKG@.ClassDefs.choiceText() + " - your class decides your weapons and your combat skill.").color("#ffc800"));
    if (@PKG@.ClassCfg.PROMPT_EVERY_LOGIN || !@PKG@.ClassStore.wasPrompted(u)) new @PKG@.OpenTask(pr).later(@PKG@.ClassCfg.OPEN_DELAY_MS);
  } catch (Throwable t) { @PKG@.ClassCfg.warn("ready task failed: " + t); }
}""")

# ================= PlayerReadyEvent (fires on EVERY world switch -> once per session) =================
rdy.addInterface(pool.get("java.util.function.Consumer"))
C(rdy, "public ClassReady() { }")
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
    java.util.UUID u = pr.getUuid();
    if (@PKG@.ClassStore.SESSION.putIfAbsent(u, Boolean.TRUE) != null) return;
    @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.ReadyTask(pr));
  } catch (Throwable t) { @PKG@.ClassCfg.warn("ready handler failed: " + t); }
}""")
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public ClassQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.ClassStore.SESSION.remove(u);
    @PKG@.ClassRules.WARNED.remove(u);
    @PKG@.ClassRules.POPPED.remove(u);
    @PKG@.ClassStore.EPOCH.remove(u);
    @PKG@.ClassStore.SNAP.remove(u);
    @PKG@.ClassStore.SNAPAT.remove(u);
  } catch (Throwable t) { }
}""")

# ================= ClassTick (0.1.3): profile epoch check every 2 s -> republish class:<uuid> (contract rule 3). No SkyyProfiles = no-op =================
ctick.addInterface(pool.get("java.lang.Runnable"))
F(ctick, "public static int FAILS = 0;")
C(ctick, "public ClassTick() { }")
M(ctick, r"""
public void run() {
  try {
    if (!@PKG@.ClassCfg.profilesOn()) return;
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p == null || !p.isValid()) continue;
      java.util.UUID u = p.getUuid();
      if (u == null) continue;
      try { @PKG@.ClassStore.check(u); } catch (Throwable t1) {
        if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("profile epoch check failed for " + u + ": " + t1); }
      }
    }
  } catch (Throwable t) {
    if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("profile epoch tick failed: " + t); }
  }
}""")

# ================= /class =================
C(cmd, r"""
public ClassCmd() {
  super("class", "Open the class page (Archer, Warrior, Mage - Assassin and Shaman later)");
  addAliases(new String[] { "classes" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(cmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new @PKG@.ClassPage(pr));
  } catch (Throwable t) {
    @PKG@.ClassCfg.warn("/class failed: " + t);
    pr.sendMessage(@MSG@.raw("[Classes] Could not open the page. Your class: " + @PKG@.ClassStore.describe(pr.getUuid())));
  }
}""")

# ================= /classadmin set|reset|info|reload (perm skyyclasses.admin) =================
F(aset, "public @RA@ playerArg;")
F(aset, "public @RA@ classArg;")
C(aset, r"""
public AdminSetCmd() {
  super("set", "(admin) Give a player a class: /classadmin set <player|uuid> <class> (free, no cooldown)");
  this.playerArg = withRequiredArg("player", "online player name or uuid", @ATY@.STRING);
  this.classArg = withRequiredArg("class", "archer | warrior | mage", @ATY@.STRING);
}""")
M(aset, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyclasses.admin")) { pr.sendMessage(@MSG@.raw("[Classes] no permission (skyyclasses.admin)")); return; }
    java.util.UUID t = @PKG@.ClassStore.resolve(String.valueOf(ctx.get(this.playerArg)));
    if (t == null) { pr.sendMessage(@MSG@.raw("[Classes] Unknown player - use an online name or a uuid.")); return; }
    int lk = @PKG@.ClassStore.profileIndex(t);
    if (lk >= 0) { pr.sendMessage(@MSG@.raw("[Classes] " + t + " is locked to " + @PKG@.ClassDefs.NAMES[lk] + " by their active profile (SkyyProfiles). A new class means a new profile.")); return; }
    int i = @PKG@.ClassDefs.indexOf(String.valueOf(ctx.get(this.classArg)));
    if (i < 0) { pr.sendMessage(@MSG@.raw("[Classes] Unknown class. Classes: " + @PKG@.ClassDefs.listText())); return; }
    if (!@PKG@.ClassDefs.ENABLED[i]) { pr.sendMessage(@MSG@.raw("[Classes] " + @PKG@.ClassDefs.NAMES[i] + " is not available yet (coming soon).")); return; }
    if (!@PKG@.ClassStore.setClass(t, i, false, false)) { pr.sendMessage(@MSG@.raw("[Classes] Could not read or write the class file of " + t + " - nothing changed (see the server log).")); return; }
    pr.sendMessage(@MSG@.raw("[Classes] " + t + " is now " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[i]) + ". " + @PKG@.ClassStore.describe(t)));
    @PR@ tp = @UNI@.get().getPlayer(t);
    if (tp != null && tp.isValid()) tp.sendMessage(@MSG@.raw("[Classes] An admin made you " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[i]) + ". Your weapons: " + @PKG@.ClassDefs.WTEXT[i] + ".").color("#8fe39a"));
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin set <player|uuid> <class>")); }
}""")
F(ares, "public @RA@ playerArg;")
C(ares, r"""
public AdminResetCmd() {
  super("reset", "(admin) Remove a player's class: /classadmin reset <player|uuid> (their next choice is free)");
  this.playerArg = withRequiredArg("player", "online player name or uuid", @ATY@.STRING);
}""")
M(ares, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyclasses.admin")) { pr.sendMessage(@MSG@.raw("[Classes] no permission (skyyclasses.admin)")); return; }
    java.util.UUID t = @PKG@.ClassStore.resolve(String.valueOf(ctx.get(this.playerArg)));
    if (t == null) { pr.sendMessage(@MSG@.raw("[Classes] Unknown player - use an online name or a uuid.")); return; }
    int lk = @PKG@.ClassStore.profileIndex(t);
    if (lk >= 0) { pr.sendMessage(@MSG@.raw("[Classes] " + t + " is locked to " + @PKG@.ClassDefs.NAMES[lk] + " by their active profile (SkyyProfiles). A new class means a new profile.")); return; }
    if (!@PKG@.ClassStore.setClass(t, -1, false, false)) { pr.sendMessage(@MSG@.raw("[Classes] Could not read or write the class file of " + t + " - nothing changed (see the server log).")); return; }
    pr.sendMessage(@MSG@.raw("[Classes] Class of " + t + " removed - their next choice is free."));
    @PR@ tp = @UNI@.get().getPlayer(t);
    if (tp != null && tp.isValid()) tp.sendMessage(@MSG@.raw("[Classes] An admin reset your class. Type /class to choose again (free).").color("#ffc800"));
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin reset <player|uuid>")); }
}""")
F(ainf, "public @RA@ playerArg;")
C(ainf, r"""
public AdminInfoCmd() {
  super("info", "(admin) Show a player's class data: /classadmin info <player|uuid>");
  this.playerArg = withRequiredArg("player", "online player name or uuid", @ATY@.STRING);
}""")
M(ainf, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyclasses.admin")) { pr.sendMessage(@MSG@.raw("[Classes] no permission (skyyclasses.admin)")); return; }
    java.util.UUID t = @PKG@.ClassStore.resolve(String.valueOf(ctx.get(this.playerArg)));
    if (t == null) { pr.sendMessage(@MSG@.raw("[Classes] Unknown player - use an online name or a uuid.")); return; }
    pr.sendMessage(@MSG@.raw("[Classes] " + t + ": " + @PKG@.ClassStore.describe(t)));
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin info <player|uuid>")); }
}""")
C(arel, 'public AdminReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyyClasses/config.properties"); }')
M(arel, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (!pr.hasPermission("skyyclasses.admin")) { pr.sendMessage(@MSG@.raw("[Classes] no permission (skyyclasses.admin)")); return; }
  pr.sendMessage(@MSG@.raw("[Classes] config reloaded: " + @PKG@.ClassCfg.load()));
}""")
C(adm, r"""
public ClassAdminCmd() {
  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | reload");
  requirePermission("skyyclasses.admin");
  addSubCommand(new @PKG@.AdminSetCmd());
  addSubCommand(new @PKG@.AdminResetCmd());
  addSubCommand(new @PKG@.AdminInfoCmd());
  addSubCommand(new @PKG@.AdminReloadCmd());
}""")
M(adm, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | reload"));
  pr.sendMessage(@MSG@.raw("[Classes] classes: " + @PKG@.ClassDefs.listText() + " | config: " + @PKG@.ClassCfg.load()));
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyClassesPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ClassCfg.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyyClasses");
  @PKG@.ClassCfg.FILE = base.resolve("config.properties");
  @PKG@.ClassStore.DIR = base.resolve("players");
  String cfgText = @PKG@.ClassCfg.load();
  java.util.Map b = @PKG@.ClassCfg.bridge();
  b.put("class:list", @PKG@.ClassDefs.listText());
  for (int i = 0; i < @PKG@.ClassDefs.NAMES.length; i++) b.put("class:weapons:" + @PKG@.ClassDefs.NAMES[i], @PKG@.ClassDefs.prefixesOf(i));
  b.put("class:weapons:free", @PKG@.ClassDefs.prefixesOf(@PKG@.ClassDefs.FREE));
  b.put("class:weapons:unassigned", @PKG@.ClassDefs.prefixesOf(@PKG@.ClassDefs.UNASSIGNED));
  b.put("class:fn:allowed", new @PKG@.AllowedFn());
  b.put("class:fn:get", new @PKG@.GetFn());
  getCommandRegistry().registerCommand(new @PKG@.ClassCmd());
  getCommandRegistry().registerCommand(new @PKG@.ClassAdminCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.ClassReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.ClassQuit());
  getEntityStoreRegistry().registerSystem(new @PKG@.ShotTrack());
  getEntityStoreRegistry().registerSystem(new @PKG@.DamageLock());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ClassTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyClasses] __VER__ ready - /class, /classadmin; classes " + @PKG@.ClassDefs.listText() + "; " + cfgText + " (coins bridge " + (@PKG@.ClassStore.coinsReady() ? "found" : "not found yet") + "; profiles " + (@PKG@.ClassCfg.profilesOn() ? "SkyyProfiles found - class per profile" : "SkyyProfiles not loaded yet - class per player") + ")");
}""".replace("__VER__", VERSION))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in (cfg, defs, st_, rul, afn, gfn, srec, strk, lock, page, opn, rtk, rdy, quit_, ctick, cmd, aset, ares, ainf, arel, adm, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
m = B.manifest("SkyyClasses", VERSION, "SkyWynn classes (Wynncraft style): Archer, Warrior, Mage (Assassin and Shaman later). Your class decides your weapons and your combat skill; /class to choose, locked per profile with SkyyProfiles. Zero dependencies (SkyyProfiles and SkyyCoins optional).", PKG + ".SkyyClassesPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyClasses.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyClasses" % VERSION, disable_prefix="Skyy:")
