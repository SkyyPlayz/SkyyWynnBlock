"""SkyyClasses 0.1.6 - build script (javassist via jpype; derived from 0.1.5 by tools/classes_0_1_6_patch.py - edit the patch, not this
file). Wynncraft-style classes for SkyWynn.
0.1.6 (Skyy 2026-09-25, research/Classes-Berserker-Priest-Spec.md section 2): roster Archer, Warrior, Mage, BERSERKER (Fury: axes,
  battleaxes, maces, clubs; hatchets stay free tools), PRIEST (Divinity: wands, spellbooks; AoE healing support) - Assassin + Shaman later.
  CLASS KITS: every class has a kit with its basic weapon (Server Setup -> Classes -> Class kits), given once per profile when the class
  is picked (SkyyProfiles 0.1.2 calls class:fn:kitnew; the own picker marks it itself); storage first, overflow waits as a claim
  (/class kit). PRIEST PLACEHOLDER HEAL: a Priest weapon hit on a monster heals party members near the Priest (numbers in Server Setup),
  Divinity XP for healing others via SkyySkills 0.4.4 skill:fn:healxp. Notes in tools/classes_0_1_6_patch.py.
0.1.5: in-game server setup - the admin config kit (tools/skyycfg.py; SkyyMenu Server Setup -> Classes: requireClass,
  unassignedBlocked, promptEveryLogin, openDelayMillis, read-only Class switching) and the player Settings switches
  classes.blockedChat / classes.blockedPopup - notes in tools/classes_0_1_5_patch.py.
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
Run:   python build_skyyclasses_0.1.6.py            -> SkyyClasses/SkyyClasses-0.1.6.jar
       (no --deploy: deploys go through tools/deploy_set.py)

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
  /classadmin info <player|uuid>, /classadmin reload (config); 0.1.6: /classadmin kit <player|uuid> [class] (give a kit now).
Player: /class, 0.1.6 /class kit (collect kit items that did not fit).
Bridge (System.getProperties().get("skyy.bridge")):
  class:<uuid> -> "Archer" (absent = no class; = profile:class:<uuid> when SkyyProfiles sets it)      class:skill:<uuid> -> "Archery"
  class:fn:allowed -> Function apply(Object[]{UUID, String itemId}) -> Boolean (may that player deal damage with that item)
  class:fn:get -> Function apply(UUID) -> "Archer" or null (loads offline players from disk)
  class:list -> "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity" (selectable classes)
  class:fn:kitnew (0.1.6) -> Function apply(Object[]{UUID player, String pkey, String class}) -> Boolean: a profile just got its class,
    mark its kit pending (SkyyProfiles 0.1.2 Create Profile). Reads party:fn:members, skill:fn:healxp (0.1.6).
  class:weapons:<Class> -> comma list of id prefixes (also class:weapons:free, class:weapons:unassigned)
Data: Skyy_SkyyClasses/players/<pkey>.properties (0.1.3: one file per profile - <uuid> = profile 1 or no SkyyProfiles, <uuid>-pN =
      profile N; class, chosenAt, lastChoiceAt, switches, played, prompted; 0.1.6 kit, kitClass, kitAt, kitGivenAt, kitItems, kitOwed,
      kitClaimAt), Skyy_SkyyClasses/kits.properties (0.1.6: written once by the 'picked before kits' migration),
      Skyy_SkyyClasses/config.properties (switchCost, cooldownMinutes, requireClass, unassignedBlocked, promptEveryLogin, openDelayMillis;
      0.1.5: also edited in game through the config kit - Skyy_SkyyClasses/config-changes.log + config-history/).
      Atomic writes (tmp + move).
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG

VERSION = "0.1.6"
HERE = os.path.dirname(os.path.abspath(__file__))

# =====================================================================================================================
# WEAPON RULES + CLASS DATA (edit here, rebuild). UI text: no , : ; { } " ' _ (the inline UI parser is picky; the build asserts it).
# weapons: (item id prefix, plural noun used in "Only <Class>s can use <noun>")
# =====================================================================================================================
CLASSES = [
    {"name": "Archer", "skill": "Archery", "color": "#8fd67a", "enabled": True, "role": "Ranged damage",
     "desc": "Fights from range. Charge a shortbow or load a crossbow and strike before the enemy gets close. Arrows are Archer ammo.",
     "icons": ["Weapon_Shortbow_Iron", "Weapon_Crossbow_Iron", "Weapon_Arrow_Crude"],
     "weapons": [("Weapon_Shortbow_", "bows"), ("Weapon_Crossbow_", "crossbows"), ("Weapon_Arrow_", "arrows")],
     "weapon_text": "Shortbows / Crossbows", "kit": "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64"},
    {"name": "Warrior", "skill": "Swordsmanship", "color": "#e0b060", "enabled": True, "role": "Melee fighter",
     "desc": "Front line blade fighter. Swords and longswords up close and spears for reach.",
     "icons": ["Weapon_Sword_Iron", "Weapon_Longsword_Iron", "Weapon_Spear_Iron"],
     "weapons": [("Weapon_Sword_", "swords"), ("Weapon_Longsword_", "longswords"), ("Weapon_Spear_", "spears")],
     "weapon_text": "Swords / Longswords / Spears", "kit": "Weapon_Sword_Crude:1"},
    {"name": "Mage", "skill": "Sorcery", "color": "#7fb0e0", "enabled": True, "role": "Magic damage",
     "desc": "Spellcaster. Staves strike up close and cast magic at range.",
     "icons": ["Weapon_Staff_Iron", "Weapon_Staff_Wizard", "Weapon_Staff_Crystal_Ice"],
     "weapons": [("Weapon_Staff_", "staves"), ("Halloween_Broomstick", "broomsticks")],
     "weapon_text": "Staves", "kit": "Weapon_Staff_Wood:1"},
    # 0.1.6 (Skyy 2026-09-25): Berserker is back. Tool_Hatchet_* match no rule = free gathering tools for every class.
    {"name": "Berserker", "skill": "Fury", "color": "#d9443f", "enabled": True, "role": "Heavy melee damage",
     "desc": "Heavy melee fighter. Axes and battleaxes cleave - maces and clubs crush. Hatchets stay gathering tools for everyone.",
     "icons": ["Weapon_Battleaxe_Iron", "Weapon_Axe_Iron", "Weapon_Mace_Iron", "Weapon_Club_Iron"],
     "weapons": [("Weapon_Axe_", "axes"), ("Weapon_Battleaxe_", "battleaxes"), ("Weapon_Mace_", "maces"), ("Weapon_Club_", "clubs")],
     "weapon_text": "Axes / Battleaxes / Maces / Clubs", "kit": "Weapon_Battleaxe_Crude:1"},
    # 0.1.6: Priest = AoE healing support (placeholder party heal on weapon hits until a spell system exists; custom content later)
    {"name": "Priest", "skill": "Divinity", "color": "#f2e6a0", "enabled": True, "role": "AoE healer / support",
     "desc": "AoE healer and support. Your wand and spellbook hits on monsters heal party members near you. Spells come later.",
     "icons": ["Weapon_Wand_Wood", "Weapon_Spellbook_Grimoire_Brown", "Weapon_Spellbook_Frost"],
     "weapons": [("Weapon_Wand_", "wands"), ("Weapon_Spellbook_", "spellbooks")],
     "weapon_text": "Wands / Spellbooks", "kit": "Weapon_Wand_Wood:1"},
    {"name": "Assassin", "skill": "Assassination", "color": "#b58cff", "enabled": False, "role": "Fast burst damage",
     "desc": "Coming later. Fast and deadly with twin daggers and kunai throwing knives.",
     "icons": ["Weapon_Daggers_Iron", "Weapon_Kunai"],
     "weapons": [("Weapon_Daggers_", "daggers"), ("Weapon_Kunai", "kunai")],
     "weapon_text": "Daggers / Kunai", "kit": "Weapon_Daggers_Crude:1"},
    # 0.1.6: Shaman gets a custom weapon later (change note 4); its icon is only a picture (the wand is a Priest weapon now)
    {"name": "Shaman", "skill": "Shaman skill", "color": "#ff7a5c", "enabled": False, "role": "Designed later",
     "desc": "Coming later. The fifth Wynncraft class - it gets its own custom weapon.",
     "icons": ["Weapon_Deployable_Slowness_Totem"],
     "weapons": [],
     "weapon_text": "Custom weapon later", "kit": ""},
]
# usable by every class (and by classless players)
FREE_WEAPONS = [("Weapon_Shield_", "shields")]
# weapons no class owns yet (blocked for players with a class while unassignedBlocked=true). "Weapon_" = catch-all for any other Weapon_*.
UNASSIGNED = [
    # LOCKED Skyy 2026-09-25: Weapon_Deployable_Healing_Totem is Priest only. This build still leaves every deployable unassigned.
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
# 0.1.6 class kits + Priest heal (research/Classes-Berserker-Priest-Spec.md 2.3-2.5). Defaults also in CFG_LINES and the kit rows.
DEF_KITS_ON = True
KIT_MAX_STACKS = 9          # kit.<Class> holds at most this many stacks (row max, parse cap)
KIT_EPOCH_WAIT_MS = 31000   # with SkyyProfiles: at least this long after the last profile:epoch change (its crash marker lives 30 s)
KIT_SAME_WORLD_MS = 3000    # ... and the player stayed this long in one world (the /island transfer after a switch is over)
KIT_OWED_DELAY_MS = 3000    # owed kit items are retried this long after each world arrival
KIT_INFLIGHT_MS = 10000     # a kit task handed to a world thread blocks a second one for that profile this long
KIT_HOTBAR_ASK_MS = 60000   # "Use my hotbar": a second click this soon (same kit, same hotbar) answers the kit check's question
DEF_HEAL_ON = True
DEF_HEAL_SHARE_PCT = 25
DEF_HEAL_SELF_PCT = 50
DEF_HEAL_RADIUS = 16.0
DEF_HEAL_MAX_HIT = 10.0
DEF_HEAL_MAX_SEC = 10.0
DEF_HEAL_MSG = True
DEF_HEAL_MSG_MS = 10000   # LOCKED Skyy 2026-09-25: one heal chat line every 10 s (was 5 s). A file already on 5000 keeps 5 s.
HEAL_SHARE_MAX, HEAL_SELF_MAX = 500, 100
HEAL_RADIUS_MIN, HEAL_RADIUS_MAX = 1.0, 64.0
HEAL_CAP_MIN, HEAL_CAP_MAX = 0.5, 1000.0
HEAL_MSG_MS_MIN, HEAL_MSG_MS_MAX = 1000, 60000


def dnum(x):
    """a decimal as the config kit's canonical text (16.0 -> 16, 0.5 -> 0.5)"""
    return str(int(x)) if float(x) == int(x) else repr(float(x))


def jdbl(x):
    return repr(float(x))


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
    assert isinstance(_c.get("kit"), str) and _c.get("role"), "0.1.6: every class needs a role and a kit (may be empty)"
    for _k in ("name", "skill", "desc", "weapon_text", "role"):
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
print("  hatchets (Tool_Hatchet_*): %d items, %s" % (len([i for i in _real if i.startswith("Tool_Hatchet_")]),
      "all free" if all(classify(i)[0] == FREE for i in _real if i.startswith("Tool_Hatchet_")) else "NOT ALL FREE"))
assert all(classify(i)[0] == FREE for i in _real if i.startswith("Tool_Hatchet_")), "hatchets must stay free gathering tools"
PRIEST_I = [i for i, c in enumerate(CLASSES) if c["name"] == "Priest"][0]


# 0.1.6 class kits (spec 2.3): every default kit id exists; an enabled class's kit holds only free items or its own weapons
def kit_entries(text):
    out = []
    for e in [x.strip() for x in text.split(",") if x.strip()]:
        iid, _, q = e.rpartition(":")
        assert iid and q.isdigit() and 1 <= int(q) <= 9999, "kit entry %r must be item:amount (amount 1-9999)" % e
        out.append((iid, int(q)))
    assert len(out) <= KIT_MAX_STACKS, "a kit holds at most %d stacks" % KIT_MAX_STACKS
    assert len(set(i for i, _ in out)) == len(out), "kit lists an item twice: %s" % text
    return out


print("class kits (defaults):")
for _ci, _c in enumerate(CLASSES):
    for _iid, _q in kit_entries(_c["kit"]):
        assert _iid in _ITEMS, "kit item %s of %s is not in Assets.zip" % (_iid, _c["name"])
        if _c["enabled"]:
            assert classify(_iid)[0] in (FREE, _ci), "kit item %s of %s is neither free nor a %s weapon" % (_iid, _c["name"], _c["name"])
    print("  %-10s %s" % (_c["name"], _c["kit"] or "(empty)"))

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
    # 0.1.6: kits + Priest heal
    "NPC":  "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ESM":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST":  "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "INV":  "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC":   "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "VEC":  "org.joml.Vector3d",
    "GM":   "com.hypixel.hytale.protocol.GameMode",
    "ITM":  "com.hypixel.hytale.server.core.asset.type.item.config.Item",
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
# 0.1.6: every new engine call (spec 2.9)
for c, m in ((T["DMOD"], "getInspectDamageGroup"), (T["ESM"], "addStatValue"), (T["ESM"], "getComponentType"), (T["ESM"], "get"),
             (T["DST"], "getHealth"), (T["ESV"], "get"), (T["ESV"], "getMax"), (T["INV"], "getCombinedStorageHotbarBackpack"),
             (T["INV"], "getHotbar"), (T["IC"], "addItemStack"), (T["IC"], "getCapacity"), (T["IC"], "getItemStack"),
             (T["IC"], "canAddItemStack"), ("com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction", "getRemainder"),
             (T["PLA"], "isWaitingForClientReady"), (T["PLA"], "getGameMode"), (T["PLA"], "getInventory"), (T["PLA"], "markNeedsSave"),
             (T["NPC"], "getComponentType"), (T["NST"], "Success"), (T["GM"], "Creative"), (T["ITM"], "getAssetMap"),
             (T["ES"], "getWorld"), (T["TC"], "getPosition"), (T["VEC"], "x"), (AC, "addUsageVariant"), (T["CTX"], "provided"),
             (T["WLD"], "execute"), (T["IS"], "getQuantity"), (T["PR"], "getReference"), (T["PR"], "getUsername")):
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
# 0.1.6: class kits + Priest heal (all top-level classes; KitCfg is made next to ClassCfg, KitHooks after the config kit)
knew  = pool.makeClass(PKG + ".KitNewFn")
kit_  = pool.makeClass(PKG + ".Kit")
ktask = pool.makeClass(PKG + ".KitTask")
kmig  = pool.makeClass(PKG + ".KitMigrate")
kht   = pool.makeClass(PKG + ".KitHotbarTask")
khooks = pool.makeClass(PKG + ".KitHooks")
hbud  = pool.makeClass(PKG + ".HealBudget")
hmsg  = pool.makeClass(PKG + ".HealMsg")
htask = pool.makeClass(PKG + ".HealTask")
phs   = pool.makeClass(PKG + ".PriestHealSys", pool.get(T["DES"]))
kcmd  = pool.makeClass(PKG + ".ClassKitCmd", pool.get(T["APC"]))
akit  = pool.makeClass(PKG + ".AdminKitCmd", pool.get(T["APC"]))

def F(cls, src): cls.addField(CtField.make(jv(src), cls))
def M(cls, src): cls.addMethod(CtNewMethod.make(jv(src), cls))
def C(cls, src): cls.addConstructor(CtNewConstructor.make(jv(src), cls))

# ================= ClassCfg: logger, bridge, config =================
CFG_LINES = [
    "# SkyyClasses config - edit, then /classadmin reload (or restart the server). Also in game: SkyWynn Menu -> Server Setup -> Classes",
    "# switchCost and cooldownMinutes are unused while class switching is off (design lock: a new class means a new profile)",
    "# switchCost = coins to switch class (the first choice is always free). Uses SkyyCoins; 0 = free switching.",
    "switchCost=%d" % DEF_SWITCH_COST,
    "# cooldownMinutes = real minutes after a player chooses a class before they may switch again",
    "cooldownMinutes=%d" % DEF_COOLDOWN_MIN,
    "# requireClass = true: players without a class deal no weapon damage. false: they may use any weapon (but earn no class XP)",
    "requireClass=%s" % str(DEF_REQUIRE_CLASS).lower(),
    "# unassignedBlocked = true: weapons no class owns yet (bombs, guns, darts, claws, deployables...) deal no damage for players with a class",
    "unassignedBlocked=%s" % str(DEF_UNASSIGNED_BLOCKED).lower(),
    "# promptEveryLogin = true: open the class page on every login until a class is chosen. false: only on the very first join",
    "promptEveryLogin=%s" % str(DEF_PROMPT_EVERY_LOGIN).lower(),
    "# openDelayMillis = how long after joining the class page opens",
    "openDelayMillis=%d" % DEF_OPEN_DELAY_MS,
    "# ---------- Class kits (0.1.6) - every class gets its basic weapon once, when a profile picks the class ----------",
    "# LOCKED Skyy 2026-09-25: the kit drops straight into the hotbar the moment the player selects or changes class.",
    "# This build still puts it in storage about 31 s after a new profile arrives. Daily Archer arrow refill is not in this build.",
    "# kits.enabled = false: new classes get no kit (kits still pending or owed wait until it is on again)",
    "kits.enabled=%s" % str(DEF_KITS_ON).lower(),
    "# kit.<Class> = item:amount,item:amount (at most %d stacks). In game: Server Setup -> Classes -> Class kits (also 'Use my hotbar')" % KIT_MAX_STACKS,
] + ["kit.%s=%s" % (_c["name"], _c["kit"]) for _c in CLASSES] + [
    "# ---------- Priest heal (LOCKED Skyy 2026-09-25, TEMPORARY until healing spells exist) ----------",
    "# Numbers locked for now: sharePercent 25, selfPercent 50, radius 16, maxPerHit 10, maxPerSecond 10, party only.",
    "# a Priest's wand or spellbook hit on a monster heals party members within priestHeal.radius blocks of the Priest by sharePercent of",
    "# the damage (the Priest themself selfPercent of that), at most maxPerHit per hit and maxPerSecond per second for each player",
    "priestHeal.enabled=%s" % str(DEF_HEAL_ON).lower(),
    "priestHeal.sharePercent=%d" % DEF_HEAL_SHARE_PCT,
    "priestHeal.selfPercent=%d" % DEF_HEAL_SELF_PCT,
    "priestHeal.radius=%s" % dnum(DEF_HEAL_RADIUS),
    "priestHeal.maxPerHit=%s" % dnum(DEF_HEAL_MAX_HIT),
    "priestHeal.maxPerSecond=%s" % dnum(DEF_HEAL_MAX_SEC),
    "# messages = heal chat lines, on by default (players can hide theirs in /settings)",
    "# feedbackMs = LOCKED Skyy 2026-09-25: at most one line per player every 10000 ms (was 5000). A file already on 5000 keeps 5000.",
    "priestHeal.messages=%s" % str(DEF_HEAL_MSG).lower(),
    "priestHeal.feedbackMs=%d" % DEF_HEAL_MSG_MS,
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
# 0.1.6: Priest heal placeholder (Server Setup -> Classes -> Priest heal; priestHeal.* in config.properties)
F(cfg, "public static volatile boolean HEAL_ON = %s;" % str(DEF_HEAL_ON).lower())
F(cfg, "public static volatile long HEAL_SHARE_PCT = %dL;" % DEF_HEAL_SHARE_PCT)
F(cfg, "public static volatile long HEAL_SELF_PCT = %dL;" % DEF_HEAL_SELF_PCT)
F(cfg, "public static volatile double HEAL_RADIUS = %s;" % jdbl(DEF_HEAL_RADIUS))
F(cfg, "public static volatile double HEAL_MAX_HIT = %s;" % jdbl(DEF_HEAL_MAX_HIT))
F(cfg, "public static volatile double HEAL_MAX_SEC = %s;" % jdbl(DEF_HEAL_MAX_SEC))
F(cfg, "public static volatile boolean HEAL_MSG = %s;" % str(DEF_HEAL_MSG).lower())
F(cfg, "public static volatile long HEAL_MSG_MS = %dL;" % DEF_HEAL_MSG_MS)
# 0.1.6: class kits (Server Setup -> Classes -> Class kits; kits.enabled + kit.<Class> in config.properties). The fields exist before
# CFG.emit (field: bindings); the methods come after ClassDefs.
kcfg = pool.makeClass(PKG + ".KitCfg")
F(kcfg, "public static final int MAX = %d;" % KIT_MAX_STACKS)
F(kcfg, "public static volatile boolean ON = %s;" % str(DEF_KITS_ON).lower())
for _c in CLASSES:
    F(kcfg, "public static volatile String K_%s = %s;" % (_c["name"].upper(), jstr(_c["kit"])))
M(cfg, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# 0.1.5: player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.3). No SkyyMenu = no answer = on (0.1.4 behaviour).
M(cfg, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""")
M(cfg, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyClasses", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
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
# 0.1.6 loader helpers
M(cfg, r"""
public static double dbl(java.util.Properties p, String k, double d) {
  try {
    String v = p.getProperty(k);
    if (v == null) return d;
    double x = Double.parseDouble(v.trim());
    if (x != x || Double.isInfinite(x)) return d;
    return x;
  } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static String txt(java.util.Properties p, String k, String d) {
  String v = p.getProperty(k);
  return v == null ? d : v.trim();
}""")
M(cfg, r"""
public static String fmtNum(double x) {
  if (x == Math.floor(x) && Math.abs(x) < 1.0E15) return String.valueOf((long) x);
  return String.valueOf((double) Math.round(x * 100.0) / 100.0);
}""")
# the 0.1.6 part of load() / summary(): "kits=on priestHeal=on healShare=25% self=50% radius=16"
M(cfg, r"""
public static String extraText() {
  return " kits=" + (@PKG@.KitCfg.ON ? "on" : "off") + " priestHeal=" + (HEAL_ON ? "on" : "off") + " healShare=" + HEAL_SHARE_PCT
    + "% self=" + HEAL_SELF_PCT + "% radius=" + fmtNum(HEAL_RADIUS);
}""")
# 0.1.6: the new keys read their CODE defaults while missing (an existing 0.1.5 file keeps working untouched); clamps = the row bounds
LOAD_TOK = {
    "__KITSON__": str(DEF_KITS_ON).lower(),
    "__KITLOAD__": "\n".join('    @PKG@.KitCfg.K_%s = txt(p, "kit.%s", %s);' % (c["name"].upper(), c["name"], jstr(c["kit"])) for c in CLASSES),
    "__HEALON__": str(DEF_HEAL_ON).lower(), "__HM__": str(DEF_HEAL_MSG).lower(),
    "__HSP__": "%dL" % DEF_HEAL_SHARE_PCT, "__HSPMAX__": "%dL" % HEAL_SHARE_MAX,
    "__HSF__": "%dL" % DEF_HEAL_SELF_PCT, "__HSFMAX__": "%dL" % HEAL_SELF_MAX,
    "__HR__": jdbl(DEF_HEAL_RADIUS), "__HRMIN__": jdbl(HEAL_RADIUS_MIN), "__HRMAX__": jdbl(HEAL_RADIUS_MAX),
    "__HH__": jdbl(DEF_HEAL_MAX_HIT), "__HS__": jdbl(DEF_HEAL_MAX_SEC), "__CAPMIN__": jdbl(HEAL_CAP_MIN), "__CAPMAX__": jdbl(HEAL_CAP_MAX),
    "__HMS__": "%dL" % DEF_HEAL_MSG_MS, "__HMSMIN__": "%dL" % HEAL_MSG_MS_MIN, "__HMSMAX__": "%dL" % HEAL_MSG_MS_MAX,
}
_LOAD = r"""
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
    @PKG@.KitCfg.ON = bool(p, "kits.enabled", __KITSON__);
__KITLOAD__
    HEAL_ON = bool(p, "priestHeal.enabled", __HEALON__);
    long hsp = lng(p, "priestHeal.sharePercent", __HSP__);
    if (hsp < 0L) hsp = 0L;
    if (hsp > __HSPMAX__) hsp = __HSPMAX__;
    HEAL_SHARE_PCT = hsp;
    long hsf = lng(p, "priestHeal.selfPercent", __HSF__);
    if (hsf < 0L) hsf = 0L;
    if (hsf > __HSFMAX__) hsf = __HSFMAX__;
    HEAL_SELF_PCT = hsf;
    double hr = dbl(p, "priestHeal.radius", __HR__);
    if (hr < __HRMIN__) hr = __HRMIN__;
    if (hr > __HRMAX__) hr = __HRMAX__;
    HEAL_RADIUS = hr;
    double hh = dbl(p, "priestHeal.maxPerHit", __HH__);
    if (hh < __CAPMIN__) hh = __CAPMIN__;
    if (hh > __CAPMAX__) hh = __CAPMAX__;
    HEAL_MAX_HIT = hh;
    double hs = dbl(p, "priestHeal.maxPerSecond", __HS__);
    if (hs < __CAPMIN__) hs = __CAPMIN__;
    if (hs > __CAPMAX__) hs = __CAPMAX__;
    HEAL_MAX_SEC = hs;
    HEAL_MSG = bool(p, "priestHeal.messages", __HM__);
    long hms = lng(p, "priestHeal.feedbackMs", __HMS__);
    if (hms < __HMSMIN__) hms = __HMSMIN__;
    if (hms > __HMSMAX__) hms = __HMSMAX__;
    HEAL_MSG_MS = hms;
    return "switchCost=" + SWITCH_COST + " cooldownMinutes=" + COOLDOWN_MIN + " requireClass=" + REQUIRE_CLASS
      + " unassignedBlocked=" + UNASSIGNED_BLOCKED + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS + extraText();
  } catch (Throwable t) { warn("could not load config: " + t); return "config load failed: " + t; }
}"""
for _k in LOAD_TOK:
    _LOAD = _LOAD.replace(_k, LOAD_TOK[_k])
assert "__" not in _LOAD.replace("__init__", ""), "unreplaced load() token"
M(cfg, _LOAD)

# 0.1.5: the running values as one line (the same text load() returns) - bare /classadmin prints it instead of re-reading the file
M(cfg, r"""
public static String summary() {
  return "switchCost=" + SWITCH_COST + " cooldownMinutes=" + COOLDOWN_MIN + " requireClass=" + REQUIRE_CLASS
    + " unassignedBlocked=" + UNASSIGNED_BLOCKED + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS + extraText();
}""")
# 0.1.5: /classadmin reload re-reads ONLY the two keys that are not kit rows (switchCost, cooldownMinutes: inert while ALLOW_SWITCH=false,
# spec 4.15). The kit rows are re-read by the kit's reload op (logged, then ClassCfg.load after the kit's own writes); this never
# touches a bound field, so it cannot undo an in-game change still waiting for its 500 ms save. Same clamps as load().
M(cfg, r"""
public static synchronized void loadInert() {
  try {
    if (FILE == null || !java.nio.file.Files.isRegularFile(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    long cost = lng(p, "switchCost", SWITCH_COST);
    long cd = lng(p, "cooldownMinutes", COOLDOWN_MIN);
    if (cost < 0L) cost = 0L;
    if (cd < 0L) cd = 0L;
    SWITCH_COST = cost;
    COOLDOWN_MIN = cd;
  } catch (Throwable t) { warn("could not re-read switchCost / cooldownMinutes: " + t); }
}""")

# ================= 0.1.5: the admin config kit (research/Server-Setup-Spec.md 4.15; tools/CONFIG-CONTRACT.md) =================
# ClassHooks = the read-only 'Class switching' row (custom:, no file key: it shows ALLOW_SWITCH and can never be set, so a hand-typed
# allowSwitch line in the file can never turn paid switching back on). switchCost / cooldownMinutes are deliberately not rows.
hooks = pool.makeClass(PKG + ".ClassHooks")
M(hooks, r"""
public static String customGet(String key) {
  if ("classSwitching".equals(key)) return @PKG@.ClassCfg.ALLOW_SWITCH ? "true" : "false";
  return null;
}""")
M(hooks, r"""
public static Object[] customSet(String key, String value) {
  return new Object[] { "bad", null, "Class switching is off in this version (design lock) - a new class means a new profile." };
}""")
CFG_CATS = [("lock", "Weapon lock"), ("picker", "Class picker"), ("kits", "Class kits"), ("priest", "Priest heal")]   # 0.1.6: + kits, priest
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind) - row key = file key
    ("requireClass", "Require a class for weapons", "lock", "bool", str(DEF_REQUIRE_CLASS).lower(), "", "", "", "", "live,danger",
     "ON: players without a class deal no weapon damage. OFF: any weapon works for them (no class XP).",
     "field:ClassCfg.REQUIRE_CLASS@config.properties:requireClass"),
    ("unassignedBlocked", "Block weapons no class owns", "lock", "bool", str(DEF_UNASSIGNED_BLOCKED).lower(), "", "", "", "", "live",
     "ON: unowned weapons (bombs, guns, darts, claws, deployables...) do no damage for class players.",
     "field:ClassCfg.UNASSIGNED_BLOCKED@config.properties:unassignedBlocked"),
    ("promptEveryLogin", "Class page on every login", "picker", "bool", str(DEF_PROMPT_EVERY_LOGIN).lower(), "", "", "", "", "live",
     "Without SkyyProfiles: ON opens /class at each login until a class is chosen, OFF only at first join.",
     "field:ClassCfg.PROMPT_EVERY_LOGIN@config.properties:promptEveryLogin"),
    ("openDelayMillis", "Class page open delay", "picker", "int", str(DEF_OPEN_DELAY_MS), "250", "60000", "step=250", "ms", "live,adv",
     "How long after joining the class page opens (only without SkyyProfiles).",
     "field:ClassCfg.OPEN_DELAY_MS@config.properties:openDelayMillis"),
    ("classSwitching", "Class switching", "picker", "bool", "false", "", "", "", "", "ro",
     "Off (design lock): a new class means a new profile. switchCost and cooldownMinutes do nothing.",
     "custom:ClassHooks"),
]
# 0.1.6 class kits (spec 2.3 + 2.5): the part switch, then per class its items row followed by its "Use my hotbar" action (the action
# rows sit right under the kit they replace; SkyyMenu 0.3 draws a value-less button, the hook reads the admin's hotbar on their world thread)
CFG_ROWS.append(("kits.enabled", "Class kits", "kits", "bool", str(DEF_KITS_ON).lower(), "", "", "", "", "live,part,danger",
                 "Off: new classes get no kit. Kits still pending or owed wait until it is on again.",
                 "field:KitCfg.ON@config.properties:kits.enabled"))
for _c in CLASSES:
    _n = _c["name"]
    if _c["enabled"]:
        _lab, _fl, _help = _n + " kit", "new", "Given once when a profile picks this class (item:amount, at most %d stacks)." % KIT_MAX_STACKS
    elif _c["kit"]:
        _lab, _fl, _help = _n + " kit (coming later)", "new,adv", "Used once %s is released. /classadmin kit can hand it out for testing." % _n
    else:
        _lab, _fl, _help = _n + " kit (coming later)", "new,adv", "Empty until %s gets its custom weapon." % _n
    CFG_ROWS.append(("kit." + _n, _lab, "kits", "items", _c["kit"], "0", str(KIT_MAX_STACKS), "qty", "", _fl, _help,
                     "field:KitCfg.K_%s@config.properties:kit.%s;check=KitHooks.checkKit" % (_n.upper(), _n)))
    CFG_ROWS.append(("kit.%s.fromHotbar" % _n, _n + " kit from my hotbar", "kits", "action", "", "", "", "Use my hotbar", "",
                     "new,danger" + ("" if _c["enabled"] else ",adv"),
                     "Replaces the %s kit with what is in your 9 hotbar slots now (items and amounts)." % _n,
                     "action:KitHooks.hb%s" % _n))
# 0.1.6 Priest heal placeholder (spec 2.4 + 2.5)
CFG_ROWS += [
    ("priestHeal.enabled", "Priest heal (placeholder)", "priest", "bool", str(DEF_HEAL_ON).lower(), "", "", "", "", "live,part,danger",
     "Off: Priest weapon hits heal nobody (and pay no Divinity heal XP).",
     "field:ClassCfg.HEAL_ON@config.properties:priestHeal.enabled"),
    ("priestHeal.sharePercent", "Heal share of damage", "priest", "int", str(DEF_HEAL_SHARE_PCT), "0", str(HEAL_SHARE_MAX), "", "%", "live",
     "Party members near the Priest heal this % of the damage a Priest weapon hit did to a monster.",
     "field:ClassCfg.HEAL_SHARE_PCT@config.properties:priestHeal.sharePercent"),
    ("priestHeal.selfPercent", "Priest heals self", "priest", "int", str(DEF_HEAL_SELF_PCT), "0", str(HEAL_SELF_MAX), "", "%", "live",
     "The Priest heals this % of what one party member gets. 0 = never heals themself.",
     "field:ClassCfg.HEAL_SELF_PCT@config.properties:priestHeal.selfPercent"),
    ("priestHeal.radius", "Heal range", "priest", "dec", dnum(DEF_HEAL_RADIUS), dnum(HEAL_RADIUS_MIN), dnum(HEAL_RADIUS_MAX), "", "blocks",
     "live", "Party members within this distance of the Priest are healed (same world only).",
     "field:ClassCfg.HEAL_RADIUS@config.properties:priestHeal.radius"),
    ("priestHeal.maxPerHit", "Most HP per hit (each player)", "priest", "dec", dnum(DEF_HEAL_MAX_HIT), dnum(HEAL_CAP_MIN), dnum(HEAL_CAP_MAX),
     "", "", "live", "Cap for one hit and one player, before the per-second cap.",
     "field:ClassCfg.HEAL_MAX_HIT@config.properties:priestHeal.maxPerHit"),
    ("priestHeal.maxPerSecond", "Most HP per second (each player)", "priest", "dec", dnum(DEF_HEAL_MAX_SEC), dnum(HEAL_CAP_MIN),
     dnum(HEAL_CAP_MAX), "", "", "live", "All Priest heals one player gets in one second, added up.",
     "field:ClassCfg.HEAL_MAX_SEC@config.properties:priestHeal.maxPerSecond"),
    ("priestHeal.messages", "Heal chat lines", "priest", "bool", str(DEF_HEAL_MSG).lower(), "", "", "", "", "live",
     "Off: no heal lines for anyone. Players can also hide theirs in /settings.",
     "field:ClassCfg.HEAL_MSG@config.properties:priestHeal.messages"),
    ("priestHeal.feedbackMs", "Heal chat line interval", "priest", "int", str(DEF_HEAL_MSG_MS), str(HEAL_MSG_MS_MIN), str(HEAL_MSG_MS_MAX),
     "", "ms", "live,adv", "At most one heal line per player this often (heals are added up).",
     "field:ClassCfg.HEAL_MSG_MS@config.properties:priestHeal.feedbackMs"),
]
# build check: every row bound to a config.properties key has the default the default file writes (the file and the kit agree)
_DFL = CFG.parse_props("".join(l + "\n" for l in CFG_LINES))
for _r in CFG_ROWS:
    _m = re.match(r"^field:[^@]+@config\.properties:([^;]+)", _r[11])
    if _m:
        assert _DFL.get(_m.group(1)) == _r[4], "row %s default %r != default file %r" % (_r[0], _r[4], _DFL.get(_m.group(1)))
assert len(CFG_ROWS) == 5 + 1 + 2 * len(CLASSES) + 8, "row count"
kit = CFG.emit(pool, PKG, MOD="SkyyClasses", TITLE="Classes", VERSION=VERSION, NODE="skyyclasses.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyyClasses/config.properties"], NOTE="Players: /classadmin set, reset, info, kit <player>. Weapon rules are code (rebuild).",
               RELOAD="ClassCfg.load", KEEP=20, DEFAULTS={"config.properties": "".join(l + "\n" for l in CFG_LINES)})
print("config kit: %d rows, files %s" % (kit.info["rows"], ", ".join(kit.info["files"])))

# ================= ClassDefs: generated from the Python tables =================
F(defs, "public static final int FREE = %d;" % FREE)
F(defs, "public static final int UNASSIGNED = %d;" % UNASSIGNED_OWNER)
F(defs, "public static final String[] NAMES = %s;" % jarr([c["name"] for c in CLASSES]))
F(defs, "public static final String[] SKILLS = %s;" % jarr([c["skill"] for c in CLASSES]))
F(defs, "public static final String[] DESCS = %s;" % jarr([c["desc"] for c in CLASSES]))
F(defs, "public static final String[] COLORS = %s;" % jarr([c["color"] for c in CLASSES]))
F(defs, "public static final String[] WTEXT = %s;" % jarr([c["weapon_text"] for c in CLASSES]))
F(defs, "public static final String[] ROLES = %s;" % jarr([c["role"] for c in CLASSES]))   # 0.1.6
F(defs, "public static final int PRIEST = %d;" % PRIEST_I)                                # 0.1.6: the heal class
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

# 0.1.6: every class name, lower case (command help / refusals)
M(defs, r"""
public static String allText() {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < NAMES.length; i++) {
    if (sb.length() > 0) sb.append(", ");
    sb.append(NAMES[i].toLowerCase());
    if (!ENABLED[i]) sb.append(" (later)");
  }
  return sb.toString();
}""")

# ================= 0.1.6 KitCfg: kit.<Class> texts (fields next to ClassCfg), parsed at use time like SkyyIslands' IslandCfg.kitOf =================
M(kcfg, r"""
public static boolean idOk(String id) {
  if (id == null || id.length() == 0 || id.length() > 120) return false;
  for (int i = 0; i < id.length(); i++) {
    char c = id.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '-')) return false;
  }
  return true;
}""")
# "id:amount,..." -> { String[] ids, int[] amounts }; where = the key named in the one-line warning of a bad entry (null = no warning);
# max = most stacks (the config kit refuses more when typed; a hand edit keeps the first max)
M(kcfg, r"""
public static Object[] parse(String text, String where, int max) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  String[] a = text == null ? new String[0] : text.split(",");
  for (int i = 0; i < a.length; i++) {
    String e = a[i].trim();
    if (e.length() == 0) continue;
    String id = e;
    int q = 1;
    int c = e.lastIndexOf(':');
    if (c >= 0) {
      id = e.substring(0, c).trim();
      try { q = Integer.parseInt(e.substring(c + 1).trim()); } catch (Throwable t) { q = -1; }
    }
    if (!idOk(id) || q < 1 || q > 9999) {
      if (where != null) @PKG@.ClassCfg.warnLimited(where + ": entry '" + @PKG@.ClassCfg.clean(e, 60) + "' skipped (item:amount, amount 1-9999)");
      continue;
    }
    if (ids.size() >= max) {
      if (where != null) @PKG@.ClassCfg.warnLimited(where + ": more than " + max + " stacks - '" + @PKG@.ClassCfg.clean(e, 60) + "' and the rest skipped");
      break;
    }
    ids.add(id);
    qs.add(Integer.valueOf(q));
  }
  String[] ra = new String[ids.size()];
  int[] qa = new int[ids.size()];
  for (int i = 0; i < ra.length; i++) { ra[i] = (String) ids.get(i); qa[i] = ((Integer) qs.get(i)).intValue(); }
  return new Object[] { ra, qa };
}""")
# the live item map knows the id (never true in a bare JVM: no asset map there)
M(kcfg, r"""
public static boolean known(String id) {
  try {
    Object a = @ITM@.getAssetMap().getAsset(id);
    return a instanceof @ITM@;
  } catch (Throwable t) { return false; }
}""")
M(kcfg, r"""
public static Object[] knownOnly(String[] ids, int[] qs, String where) {
  java.util.ArrayList ki = new java.util.ArrayList();
  java.util.ArrayList kq = new java.util.ArrayList();
  for (int i = 0; i < ids.length && i < qs.length; i++) {
    if (known(ids[i])) { ki.add(ids[i]); kq.add(Integer.valueOf(qs[i])); }
    else @PKG@.ClassCfg.warnLimited(where + ": unknown item " + ids[i] + " skipped");
  }
  String[] ra = new String[ki.size()];
  int[] qa = new int[ki.size()];
  for (int i = 0; i < ra.length; i++) { ra[i] = (String) ki.get(i); qa[i] = ((Integer) kq.get(i)).intValue(); }
  return new Object[] { ra, qa };
}""")
# "Weapon_Wand_Wood" -> "Wand Wood" (the SkyySkills weaponsText style)
M(kcfg, r"""
public static String name(String id) {
  if (id == null) return "";
  String n = id.startsWith("Weapon_") ? id.substring(7) : id;
  return n.replace('_', ' ');
}""")
# "Wand Wood x1, Arrow Crude x64" (entries with an amount > 0)
M(kcfg, r"""
public static String listText(String[] ids, int[] qs) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length && i < qs.length; i++) {
    if (qs[i] <= 0) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(name(ids[i])).append(" x").append(qs[i]);
  }
  return sb.toString();
}""")
M(kcfg, r"""
public static String namesText(String[] ids, int[] qs) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length && i < qs.length; i++) {
    if (qs[i] <= 0) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(name(ids[i]));
  }
  return sb.toString();
}""")
# "id:amount,..." (entries with an amount > 0) - the form kitItems / kitOwed are stored in
M(kcfg, r"""
public static String join(String[] ids, int[] qs) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length && i < qs.length; i++) {
    if (qs[i] <= 0) continue;
    if (sb.length() > 0) sb.append(",");
    sb.append(ids[i]).append(":").append(qs[i]);
  }
  return sb.toString();
}""")
# what did not fit: amount - given, per entry
M(kcfg, r"""
public static String rest(String[] ids, int[] qs, int[] got) {
  int[] left = new int[qs.length];
  for (int i = 0; i < qs.length; i++) left[i] = qs[i] - (i < got.length ? got[i] : 0);
  return join(ids, left);
}""")
M(kcfg, r"""
public static int total(int[] qs) {
  int n = 0;
  for (int i = 0; i < qs.length; i++) if (qs[i] > 0) n = n + qs[i];
  return n;
}""")
# a stored list as "Weapon_Arrow_Crude x14, ..." (admin view) / "Arrow Crude x14, ..." (player view)
M(kcfg, r"""
public static String rawText(String text) {
  Object[] k = parse(text, null, 1000);
  String[] ids = (String[]) k[0];
  int[] qs = (int[]) k[1];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {
    if (sb.length() > 0) sb.append(", ");
    sb.append(ids[i]).append(" x").append(qs[i]);
  }
  return sb.length() == 0 ? "-" : sb.toString();
}""")
M(kcfg, r"""
public static String itemsText(String text) {
  Object[] k = parse(text, null, 1000);
  return listText((String[]) k[0], (int[]) k[1]);
}""")
M(kcfg, r"""
public static String day(long ms) {
  try { return new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date(ms)); } catch (Throwable t) { return "?"; }
}""")
M(kcfg, (r"""
public static String textOf(int ci) {
__TEXTOF__
  return "";
}""").replace("__TEXTOF__", "\n".join("  if (ci == %d) return K_%s;" % (i, c["name"].upper()) for i, c in enumerate(CLASSES))))

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
# 0.1.6: pkey -> "pending" | "owed" for every class file read (loadKey) or written (kitnew, setClassKey, give) with that kit state, so the
# 2 s kit tick and the arrival retry never read files. The owner UUID is the first 36 characters of the pkey.
F(st_, "public static final java.util.concurrent.ConcurrentHashMap KITQ = new java.util.concurrent.ConcurrentHashMap();")
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
  String ks = p.getProperty("kit");
  if ("pending".equals(ks) || "owed".equals(ks)) KITQ.put(k, ks);
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
  // 0.1.6: the first class of a file with no kit flag makes its kit pending in the SAME write (own picker / /classadmin set on a classless
  // file). A file that had a class or any kit flag (old, given, owed, off, pending) is left alone: one automatic kit per profile at most.
  String kit0 = null;
  if (idx >= 0 && old.getProperty("class", "").trim().length() == 0 && old.getProperty("kit") == null) kit0 = @PKG@.KitCfg.ON ? "pending" : "off";
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
  if (kit0 != null) {
    p.setProperty("kit", kit0);
    p.setProperty("kitClass", n);
    p.setProperty("kitAt", String.valueOf(now));
  }
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return false; }
  if (n == null) CLS.remove(k); else CLS.put(k, n);
  if ("pending".equals(kit0)) KITQ.put(k, "pending");
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
# ================= 0.1.6 kit state per profile (spec 2.3). Every write goes through loadKey + saveKey under ClassStore's lock (all other keys
# kept); an unread file is never written (-1 / false / null). Nothing here calls another mod.
M(st_, r"""
public static String kitState(String k) {
  return loadKey(k).getProperty("kit");
}""")
# class:fn:kitnew: -1 = the file could not be read / written, 0 = marked pending, 1 = marked off (kits are off), 2 = it already had a state
M(st_, r"""
public static synchronized int markKitKey(String k, String cls) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return -1;
  if (old.getProperty("kit") != null) return 2;
  boolean on = @PKG@.KitCfg.ON;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.setProperty("kit", on ? "pending" : "off");
  if (cls != null && cls.length() > 0) p.setProperty("kitClass", cls);
  p.setProperty("kitAt", String.valueOf(System.currentTimeMillis()));
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return -1; }
  if (on) KITQ.put(k, "pending");
  return on ? 0 : 1;
}""")
# step 1 of a give (crash-safe order): kit=given + the whole list as the in-flight record BEFORE any item moves
M(st_, r"""
public static synchronized boolean kitBegin(String k, String cls, String list) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return false;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.setProperty("kit", "given");
  p.setProperty("kitClass", cls);
  p.setProperty("kitGivenAt", String.valueOf(System.currentTimeMillis()));
  p.setProperty("kitItems", list == null ? "" : list);
  if (list == null || list.length() == 0) p.remove("kitOwed"); else p.setProperty("kitOwed", list);
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return false; }
  return true;
}""")
# step 3: nothing left -> the in-flight record goes; a remainder -> kit=owed, kitOwed=<remainder> (a claim for /class kit)
M(st_, r"""
public static synchronized boolean kitEnd(String k, String rem) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return false;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  if (rem == null || rem.length() == 0) {
    p.remove("kitOwed");
    if ("owed".equals(p.getProperty("kit"))) p.setProperty("kit", "given");
  } else {
    p.setProperty("kit", "owed");
    p.setProperty("kitOwed", rem);
  }
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return false; }
  return true;
}""")
# a claim starts: owed -> given (kitOwed stays as the in-flight record until kitEnd); returns the owed list, null = nothing owed / not saved
M(st_, r"""
public static synchronized String kitClaimBegin(String k) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return null;
  if (!"owed".equals(old.getProperty("kit"))) return null;
  String owed = old.getProperty("kitOwed", "");
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.setProperty("kit", "given");
  p.setProperty("kitClaimAt", String.valueOf(System.currentTimeMillis()));
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return null; }
  return owed;
}""")
# /classadmin kit on a profile whose flag is given / old / off / owed: the flag stays, only a remainder becomes (or joins) the claim.
# Review fix: kit=given with an in-flight kitOwed (a give interrupted by a crash) and an admin kit of that SAME class = the admin checked
# and re-gave it, so the stale in-flight record goes (else /classadmin info kept saying "interrupted" forever). Another class's kit
# leaves it alone.
M(st_, r"""
public static synchronized boolean kitMerge(String k, String cls, String rem) {
  boolean left = rem != null && rem.length() > 0;
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return !left;
  boolean fly = "given".equals(old.getProperty("kit")) && old.getProperty("kitOwed", "").length() > 0 && cls != null && cls.equals(old.getProperty("kitClass"));
  if (!left && !fly) return true;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  if (fly) p.remove("kitOwed");
  if (left) {
    String had = "owed".equals(old.getProperty("kit")) ? old.getProperty("kitOwed", "") : "";
    p.setProperty("kit", "owed");
    p.setProperty("kitOwed", had.length() == 0 ? rem : had + "," + rem);
    if (p.getProperty("kitClass") == null) p.setProperty("kitClass", cls);
  }
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return false; }
  return true;
}""")
# /classadmin info: the kit state of one profile file
M(st_, r"""
public static String kitText(java.util.Properties p) {
  String s = p.getProperty("kit");
  String cls = p.getProperty("kitClass", "?");
  if (s == null) return "no kit yet";
  if (s.equals("pending")) return "kit pending (" + cls + ")";
  if (s.equals("old")) return "kit - class picked before kits";
  if (s.equals("off")) return "kit off - class picked while class kits were off";
  if (s.equals("owed")) return "kit owed: " + @PKG@.KitCfg.rawText(p.getProperty("kitOwed", "")) + " (" + cls + ")";
  if (s.equals("given")) {
    long at = num(p, "kitGivenAt");
    String fly = p.getProperty("kitOwed", "");
    return "kit given " + (at > 0L ? @PKG@.KitCfg.day(at) : "?") + " (" + cls + ")"
      + (fly.length() > 0 ? " - interrupted while giving " + @PKG@.KitCfg.rawText(fly) + " (the server stopped mid-give: it may or may not have landed) - check their inventory before /classadmin kit" : "");
  }
  return "kit " + @PKG@.ClassCfg.clean(s, 20);
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
  if (!@PKG@.ClassCfg.notifyOn(u, "classes.blockedChat")) return;
  long now = System.currentTimeMillis();
  Long last = (Long) WARNED.get(u);
  if (last != null && now - last.longValue() < %dL) return;
  WARNED.put(u, Long.valueOf(now));
  pr.sendMessage(@MSG@.raw("[Classes] " + text).color("#ff9d6b"));
}""" % MSG_THROTTLE_MS)

M(rul, r"""
public static void popup(@PR@ pr, java.util.UUID u, String id, String text) {
  try {
    if (!@PKG@.ClassCfg.notifyOn(u, "classes.blockedPopup")) return;
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

# ================= 0.1.6 class:fn:kitnew (spec 2.3): apply(Object[]{UUID player, String pkey, String class}) -> Boolean =================
# TRUE = recorded (pending, or off while kits are off) or the profile already has a kit state; FALSE = bad arguments or the class file
# cannot be read / written. Runs on the caller's thread (SkyyProfiles' world thread): one synchronized ClassStore write, no call into
# another mod (the pkey comes in as an argument), then one chat line to the player if online. Never throws.
knew.addInterface(pool.get("java.util.function.Function"))
C(knew, "public KitNewFn() { }")
M(knew, r"""
public static boolean keyOk(java.util.UUID u, String k) {
  String us = u.toString();
  if (k.equals(us)) return true;
  if (!k.startsWith(us + "-p")) return false;
  String n = k.substring(us.length() + 2);
  if (n.length() == 0 || n.length() > 4) return false;
  for (int i = 0; i < n.length(); i++) {
    char c = n.charAt(i);
    if (c < '0' || c > '9') return false;
  }
  return true;
}""")
M(knew, r"""
public static void note(java.util.UUID u, String k, int ci) {
  try {
    if (ci < 0) return;
    Object[] kit = @PKG@.KitCfg.parse(@PKG@.KitCfg.textOf(ci), null, @PKG@.KitCfg.MAX);
    if (((String[]) kit[0]).length == 0) return;
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return;
    String when = k.equals(u.toString()) ? "shortly." : "shortly after the switch.";
    pr.sendMessage(@MSG@.raw("[Classes] Your " + @PKG@.ClassDefs.NAMES[ci] + " kit is on its way - it lands in your inventory " + when).color("#8fe39a"));
  } catch (Throwable t) { }
}""")
M(knew, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return Boolean.FALSE;
    java.util.UUID u = (java.util.UUID) a[0];
    String k = ((String) a[1]).trim();
    if (!keyOk(u, k)) return Boolean.FALSE;
    String raw = a[2] == null ? "" : String.valueOf(a[2]);
    int ci = @PKG@.ClassDefs.indexOf(raw);
    String cls = ci >= 0 ? @PKG@.ClassDefs.NAMES[ci] : @PKG@.ClassCfg.clean(raw, 32);
    int r = @PKG@.ClassStore.markKitKey(k, cls);
    if (r < 0) return Boolean.FALSE;
    if (r == 0) note(u, k, ci);
    return Boolean.TRUE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")

# ================= ShotRec + ShotTrack: what the shooter held when a projectile / bomb was LAUNCHED =================
# SimpleEnchantments EnchantmentProjectileSpeedSystem pattern (RefSystem, AddReason.SPAWN, creator uuid -> EntityStore.getRefFromUUID,
# record keyed by the projectile's UUIDComponent, removed in onEntityRemove). bad = the forbidden item id (null = the launch was allowed).
F(srec, "public java.util.UUID shooter;")
F(srec, "public String bad;")
F(srec, "public boolean util;")
F(srec, "public String item;")   # 0.1.6: the main-hand item id at launch (null = empty hand), for every tracked shot
F(srec, "public long at;")
C(srec, r"""
public ShotRec(java.util.UUID shooter, String bad, boolean util, String item) {
  this.shooter = shooter;
  this.bad = bad;
  this.util = util;
  this.item = item;
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
    @IS@ mh = @INVC@.getItemInHand(buf, sh);
    String item = (mh == null || mh.isEmpty()) ? null : mh.getItemId();
    String bad = badOf(u, mh);
    boolean util = false;
    if (bad == null) {
      @UTIL@ ut = (@UTIL@) buf.getComponent(sh, @UTIL@.getComponentType());
      bad = badOf(u, ut == null ? null : ut.getActiveItem());
      util = bad != null;
    }
    if (SHOTS.size() > %d) purge();
    SHOTS.put(idc.getUuid(), new @PKG@.ShotRec(u, bad, util, item));
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

# ================= 0.1.6 HealBudget: per target, a fixed 1 s window shared by ALL Priests (priestHeal.maxPerSecond) =================
F(hbud, "public static final java.util.concurrent.ConcurrentHashMap USED = new java.util.concurrent.ConcurrentHashMap();")  # UUID -> double[]{start, used}
M(hbud, r"""
public static synchronized double take(java.util.UUID u, double want, long now, double perSec) {
  if (u == null || !(want > 0.0) || !(perSec > 0.0)) return 0.0;
  double[] b = (double[]) USED.get(u);
  if (b == null || (double) now - b[0] >= 1000.0 || (double) now < b[0]) { b = new double[] { (double) now, 0.0 }; USED.put(u, b); }
  double left = perSec - b[1];
  if (!(left > 0.0)) return 0.0;
  double got = want < left ? want : left;
  b[1] = b[1] + got;
  return got;
}""")
M(hbud, r"""
public static void forget(java.util.UUID u) {
  if (u != null) USED.remove(u);
}""")

# ================= 0.1.6 HealMsg: heal chat lines, added up and sent at most every priestHeal.feedbackMs by ClassTick (spec 2.4 Feedback) =================
# GIVEN: Priest -> { double[]{party, self}, HashSet healed members }; TAKEN: member -> { double[]{hp}, healer name, HashSet healers }.
# The admin switch + the player's Settings switch are checked before the line's own timestamp (a hidden line uses up nothing).
F(hmsg, "public static final java.util.concurrent.ConcurrentHashMap GIVEN = new java.util.concurrent.ConcurrentHashMap();")
F(hmsg, "public static final java.util.concurrent.ConcurrentHashMap TAKEN = new java.util.concurrent.ConcurrentHashMap();")
F(hmsg, "public static final java.util.concurrent.ConcurrentHashMap LASTG = new java.util.concurrent.ConcurrentHashMap();")
F(hmsg, "public static final java.util.concurrent.ConcurrentHashMap LASTT = new java.util.concurrent.ConcurrentHashMap();")
M(hmsg, r"""
public static synchronized void given(java.util.UUID p, java.util.UUID target, double hp) {
  if (p == null || target == null || !(hp > 0.0)) return;
  Object[] e = (Object[]) GIVEN.get(p);
  if (e == null) { e = new Object[] { new double[] { 0.0, 0.0 }, new java.util.HashSet() }; GIVEN.put(p, e); }
  double[] v = (double[]) e[0];
  if (p.equals(target)) v[1] = v[1] + hp;
  else { v[0] = v[0] + hp; ((java.util.HashSet) e[1]).add(target); }
}""")
M(hmsg, r"""
public static synchronized void taken(java.util.UUID target, java.util.UUID healer, String name, double hp) {
  if (target == null || healer == null || !(hp > 0.0)) return;
  Object[] e = (Object[]) TAKEN.get(target);
  if (e == null) { e = new Object[] { new double[] { 0.0 }, name, new java.util.HashSet() }; TAKEN.put(target, e); }
  double[] v = (double[]) e[0];
  v[0] = v[0] + hp;
  ((java.util.HashSet) e[2]).add(healer);
}""")
M(hmsg, r"""
public static String fmt(double hp) {
  double r = (double) Math.round(hp * 10.0) / 10.0;
  if (r == Math.floor(r)) return String.valueOf((long) r);
  return String.valueOf(r);
}""")
M(hmsg, r"""
public static String givenText(double party, int n, double self) {
  String s = "";
  if (party >= 0.05) s = "+" + fmt(party) + " HP to your party (" + n + (n == 1 ? " player)" : " players)");
  if (self >= 0.05) s = s + (s.length() > 0 ? " and " : "") + "+" + fmt(self) + " HP to you";
  return s.length() == 0 ? null : "Heals: " + s;
}""")
M(hmsg, r"""
public static String takenText(String name, int n, double hp) {
  if (!(hp >= 0.05)) return null;
  return (n > 1 || name == null || name.length() == 0 ? "Priests" : name) + " healed you +" + fmt(hp) + " HP";
}""")
# the due lines (their entries removed): Object[] { UUID, text, settings key, the LAST map to stamp once it is shown }
M(hmsg, r"""
public static synchronized Object[] due(long now, long every) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = new java.util.ArrayList(GIVEN.keySet()).iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    Long last = (Long) LASTG.get(u);
    if (last != null && now - last.longValue() < every) continue;
    Object[] e = (Object[]) GIVEN.remove(u);
    if (e == null) continue;
    double[] v = (double[]) e[0];
    String t = givenText(v[0], ((java.util.HashSet) e[1]).size(), v[1]);
    if (t != null) out.add(new Object[] { u, t, "classes.healGiven", LASTG });
  }
  java.util.Iterator it2 = new java.util.ArrayList(TAKEN.keySet()).iterator();
  while (it2.hasNext()) {
    java.util.UUID u2 = (java.util.UUID) it2.next();
    Long last2 = (Long) LASTT.get(u2);
    if (last2 != null && now - last2.longValue() < every) continue;
    Object[] e2 = (Object[]) TAKEN.remove(u2);
    if (e2 == null) continue;
    double[] v2 = (double[]) e2[0];
    String t2 = takenText((String) e2[1], ((java.util.HashSet) e2[2]).size(), v2[0]);
    if (t2 != null) out.add(new Object[] { u2, t2, "classes.healTaken", LASTT });
  }
  return out.toArray();
}""")
M(hmsg, r"""
public static void flushDue() {
  if (GIVEN.isEmpty() && TAKEN.isEmpty()) return;
  long now = System.currentTimeMillis();
  Object[] d = due(now, @PKG@.ClassCfg.HEAL_MSG_MS);
  for (int i = 0; i < d.length; i++) {
    try {
      Object[] e = (Object[]) d[i];
      java.util.UUID u = (java.util.UUID) e[0];
      String key = (String) e[2];
      if (!@PKG@.ClassCfg.HEAL_MSG || !@PKG@.ClassCfg.notifyOn(u, key)) continue;
      @PR@ pr = @UNI@.get().getPlayer(u);
      if (pr == null || !pr.isValid()) continue;
      ((java.util.concurrent.ConcurrentHashMap) e[3]).put(u, Long.valueOf(now));
      pr.sendMessage(@MSG@.raw("[Classes] " + (String) e[1]).color("#f2e6a0"));
    } catch (Throwable t) { }
  }
}""")
M(hmsg, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  GIVEN.remove(u);
  TAKEN.remove(u);
  LASTG.remove(u);
  LASTT.remove(u);
}""")

# ================= 0.1.6 Kit, part 1: helpers, give, claim (world thread) =================
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap KITEP = new java.util.concurrent.ConcurrentHashMap();")     # UUID -> long[]{epoch, seenAt}
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap KITARR = new java.util.concurrent.ConcurrentHashMap();")    # UUID -> Object[]{world UUID, Long since}
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap INFLIGHT = new java.util.concurrent.ConcurrentHashMap();")  # pkey -> Long handed to a world
F(kit_, "public static final long EPOCH_WAIT_MS = %dL;" % KIT_EPOCH_WAIT_MS)
F(kit_, "public static final long SAME_WORLD_MS = %dL;" % KIT_SAME_WORLD_MS)
F(kit_, "public static final long OWED_DELAY_MS = %dL;" % KIT_OWED_DELAY_MS)
F(kit_, "public static final long INFLIGHT_MS = %dL;" % KIT_INFLIGHT_MS)
M(kit_, r"""
public static void requeue(String k) {
  String s = @PKG@.ClassStore.kitState(k);
  if ("pending".equals(s) || "owed".equals(s)) @PKG@.ClassStore.KITQ.put(k, s);
  else @PKG@.ClassStore.KITQ.remove(k);
}""")
# profile:busy:<uuid> present = the live inventory may not belong to the active profile (PROFILES-CONTRACT rule 5): no item moves
M(kit_, r"""
public static boolean busy(java.util.UUID u) {
  try { return u != null && @PKG@.ClassCfg.bridge().get("profile:busy:" + u.toString()) != null; } catch (Throwable t) { return true; }
}""")
M(kit_, r"""
public static boolean alive(@ST@ st, @REF@ r) {
  try {
    if (r == null || !r.isValid()) return false;
    @ESM@ m = (@ESM@) st.getComponent(r, @ESM@.getComponentType());
    if (m == null) return true;
    int hi = @DST@.getHealth();
    if (hi < 0) return true;
    @ESV@ hv = m.get(hi);
    return hv == null || hv.get() > 0.0f;
  } catch (Throwable t) { return false; }
}""")
M(kit_, r"""
public static boolean creative(@PLA@ p) {
  try { return p != null && p.getGameMode() == @GM@.Creative; } catch (Throwable t) { return false; }
}""")
M(kit_, r"""
public static void tell(@PR@ pr, String text, boolean warn) {
  try { if (pr != null && pr.isValid()) pr.sendMessage(@MSG@.raw("[Classes] " + text).color(warn ? "#ffc800" : "#8fe39a")); } catch (Throwable t) { }
}""")
M(kit_, r"""
public static void popup(@PR@ pr, String title, String body, String id) {
  try {
    @MSG@ ti = @MSG@.raw(title).color("#8fe39a");
    @MSG@ bd = @MSG@.raw(body);
    @IWM@ icon = null;
    try { if (id != null && id.length() > 0) icon = (@IWM@) new @IS@(id, 1).toPacket(); } catch (Throwable t0) { icon = null; }
    if (icon != null) @NTU@.sendNotification(pr.getPacketHandler(), ti, bd, icon, @NST@.Success);
    else @NTU@.sendNotification(pr.getPacketHandler(), ti, bd, @NST@.Success);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("kit popup failed: " + t); }
}""")
M(kit_, r"""
public static int count(@IC@ c, String id) {
  int n = 0;
  if (c == null || id == null) return 0;
  short cap = c.getCapacity();
  for (short sl = 0; sl < cap; sl++) {
    @IS@ it = c.getItemStack(sl);
    if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n = n + it.getQuantity();
  }
  return n;
}""")
# storage first (SkyySacks 0.6.5 / SkyyProfiles rule); what really landed is counted (added = after - before), so a failed add can
# never be mistaken for a full one. Amounts above an item's stack size fill several slots (the engine splits them).
M(kit_, r"""
public static int[] put(@PLA@ p, String[] ids, int[] qs) {
  int[] got = new int[ids.length];
  @INV@ inv = p.getInventory();
  @IC@ c = inv == null ? null : inv.getCombinedStorageHotbarBackpack();
  if (c == null) return got;
  for (int i = 0; i < ids.length && i < qs.length; i++) {
    int q = qs[i];
    if (q <= 0) continue;
    try {
      int before = count(c, ids[i]);
      c.addItemStack(new @IS@(ids[i], q));
      int added = count(c, ids[i]) - before;
      if (added < 0) added = 0;
      if (added > q) added = q;
      got[i] = added;
    } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class kit: could not add " + ids[i] + ": " + t); }
  }
  try { p.markNeedsSave(); } catch (Throwable t2) { }
  return got;
}""")
# some room for at least one of these items (a claim at a world arrival skips the file writes when nothing can fit)
M(kit_, r"""
public static boolean room(@PLA@ p, String[] ids) {
  try {
    @INV@ inv = p.getInventory();
    @IC@ c = inv == null ? null : inv.getCombinedStorageHotbarBackpack();
    if (c == null) return false;
    for (int i = 0; i < ids.length; i++) if (c.canAddItemStack(new @IS@(ids[i], 1))) return true;
  } catch (Throwable t) { return true; }
  return false;
}""")
M(kit_, r"""
public static void tellGiven(@PR@ pr, String cls, String[] ids, int[] qs, int[] got) {
  int g = @PKG@.KitCfg.total(got);
  int left = @PKG@.KitCfg.total(qs) - g;
  if (g > 0) {
    String first = null;
    for (int i = 0; i < ids.length && first == null; i++) if (got[i] > 0) first = ids[i];
    popup(pr, "Class kit", cls + " kit - " + @PKG@.KitCfg.namesText(ids, got), first);
    tell(pr, "Your " + cls + " kit is in your inventory: " + @PKG@.KitCfg.listText(ids, got) + ".", false);
  }
  if (left > 0) tell(pr, left + (left == 1 ? " item" : " items") + " of your " + cls + " kit did not fit - make room, then type /class kit to collect " + (left == 1 ? "it." : "them."), true);
}""")
# give the kit of class ci to the ACTIVE profile k (world thread, Player component in hand). admin = /classadmin kit (ignores the flag).
# Returns null when done (or nothing to give), else a reason nothing was given.
M(kit_, r"""
public static String give(@PR@ pr, @PLA@ p, String k, int ci, boolean admin, @PR@ by) {
  if (ci < 0 || ci >= @PKG@.ClassDefs.NAMES.length) return "no class";
  String cls = @PKG@.ClassDefs.NAMES[ci];
  Object[] kit = @PKG@.KitCfg.parse(@PKG@.KitCfg.textOf(ci), "kit." + cls, @PKG@.KitCfg.MAX);
  Object[] ok = @PKG@.KitCfg.knownOnly((String[]) kit[0], (int[]) kit[1], "kit." + cls);
  String[] ids = (String[]) ok[0];
  int[] qs = (int[]) ok[1];
  String list = @PKG@.KitCfg.join(ids, qs);
  String st0 = @PKG@.ClassStore.kitState(k);
  boolean flag = st0 == null || "pending".equals(st0);
  if (!admin && !"pending".equals(st0)) { requeue(k); return null; }   // automatic kits only ever from a pending flag (never twice)
  if (ids.length == 0) {
    if (admin) return "The " + cls + " kit is empty - set it in Server Setup -> Classes -> Class kits (kit." + cls + " in config.properties).";
    if (@PKG@.ClassStore.kitBegin(k, cls, "")) @PKG@.ClassStore.kitEnd(k, "");
    requeue(k);
    return null;
  }
  boolean full = !admin || flag;
  if (full && !@PKG@.ClassStore.kitBegin(k, cls, list)) return "the kit record of " + k + " could not be saved - nothing was given";
  int[] got = put(p, ids, qs);
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  if (full) @PKG@.ClassStore.kitEnd(k, rem);
  else @PKG@.ClassStore.kitMerge(k, cls, rem);
  requeue(k);
  tellGiven(pr, cls, ids, qs, got);
  int g = @PKG@.KitCfg.total(got);
  int left = @PKG@.KitCfg.total(qs) - g;
  String who = pr.getUsername();
  if (admin && by != null && by.isValid()) {
    String what = g > 0 ? @PKG@.KitCfg.listText(ids, got) : "nothing fit";
    by.sendMessage(@MSG@.raw("[Classes] Gave " + who + " the " + cls + " kit: " + what + (left > 0 ? " - " + left + " items wait for them (/class kit)" : "") + ".").color("#8fe39a"));
  }
  @PKG@.ClassCfg.info("class kit: " + who + " (" + k + ") got the " + cls + " kit" + (admin ? " from " + (by == null ? "an admin" : by.getUsername()) : "")
    + " - given " + (g > 0 ? @PKG@.KitCfg.join(ids, got) : "nothing") + (left > 0 ? ", owed " + rem : ""));
  return null;
}""")
# collect owed kit items of the ACTIVE profile k (world thread). quiet = the retry at a world arrival (only a success is told)
M(kit_, r"""
public static void claim(@PR@ pr, @PLA@ p, String k, boolean quiet) {
  java.util.Properties pp = @PKG@.ClassStore.loadKey(k);
  if (!"owed".equals(pp.getProperty("kit"))) { requeue(k); if (!quiet) tell(pr, "Nothing is waiting.", false); return; }
  Object[] ow = @PKG@.KitCfg.parse(pp.getProperty("kitOwed", ""), "kitOwed of " + k, 1000);
  String[] ids = (String[]) ow[0];
  int[] qs = (int[]) ow[1];
  if (ids.length == 0) { @PKG@.ClassStore.kitEnd(k, ""); requeue(k); if (!quiet) tell(pr, "Nothing is waiting.", false); return; }
  if (!room(p, ids)) {
    if (!quiet) tell(pr, "Your inventory is full - make room for your kit items (" + @PKG@.KitCfg.listText(ids, qs) + "), then type /class kit again.", true);
    return;
  }
  String owed = @PKG@.ClassStore.kitClaimBegin(k);
  if (owed == null) { if (!quiet) tell(pr, "Your kit record could not be saved - try again in a moment.", true); return; }
  int[] got = put(p, ids, qs);
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  @PKG@.ClassStore.kitEnd(k, rem);
  requeue(k);
  int g = @PKG@.KitCfg.total(got);
  int left = @PKG@.KitCfg.total(qs) - g;
  if (g > 0) tell(pr, "Collected " + g + (g == 1 ? " kit item: " : " kit items: ") + @PKG@.KitCfg.listText(ids, got) + ".", false);
  if (left > 0 && (!quiet || g > 0)) tell(pr, left + (left == 1 ? " item" : " items") + " still did not fit - make room, then type /class kit again.", true);
  @PKG@.ClassCfg.info("class kit claim: " + pr.getUsername() + " (" + k + ") collected " + (g > 0 ? @PKG@.KitCfg.join(ids, got) : "nothing") + (left > 0 ? ", still owed " + rem : ""));
}""")
# /class kit with nothing owed
M(kit_, r"""
public static String stateLine(java.util.Properties p) {
  String s = p.getProperty("kit");
  String cls = p.getProperty("kitClass", "class");
  if ("given".equals(s)) {
    if (p.getProperty("kitOwed", "").length() > 0) return "Nothing is waiting. The server stopped while your " + cls + " kit was being handed out - if it is not in your inventory, ask an admin.";
    String items = @PKG@.KitCfg.itemsText(p.getProperty("kitItems", ""));
    long at = @PKG@.ClassStore.num(p, "kitGivenAt");
    return "Nothing is waiting. Your " + cls + " kit" + (items.length() > 0 ? " (" + items + ")" : "") + " was given" + (at > 0L ? " on " + @PKG@.KitCfg.day(at) : "") + ".";
  }
  if ("pending".equals(s)) return "Your " + cls + " kit is on its way - it lands in your inventory shortly.";
  if ("old".equals(s)) return "Nothing is waiting. This profile chose its class before class kits existed - ask an admin if you need one.";
  if ("off".equals(s)) return "Nothing is waiting. Class kits were off when this profile chose its class - ask an admin if you need one.";
  return "Nothing is waiting.";
}""")

# ================= 0.1.6 KitTask: one kit job on the player's world thread; everything is re-checked there =================
# mode 0 = automatic (pending, from Kit.tick), 1 = /classadmin kit, 2 = owed items at a world arrival (hops to the current world first)
ktask.addInterface(pool.get("java.lang.Runnable"))
F(ktask, "public @PR@ pr;")
F(ktask, "public String k;")
F(ktask, "public java.util.UUID wu;")
F(ktask, "public int ci;")
F(ktask, "public int mode;")
F(ktask, "public @PR@ by;")
F(ktask, "public boolean onWorld;")
C(ktask, "public KitTask(@PR@ pr, String k, java.util.UUID wu, int ci, int mode, @PR@ by, boolean onWorld) { this.pr = pr; this.k = k; this.wu = wu; this.ci = ci; this.mode = mode; this.by = by; this.onWorld = onWorld; }")
M(ktask, r"""
public void toAdmin(String msg) {
  try {
    if (this.mode != 1 || this.by == null || !this.by.isValid()) return;
    String n = this.pr == null ? "the player" : this.pr.getUsername();
    this.by.sendMessage(@MSG@.raw("[Classes] No kit given - " + n + " " + msg).color("#ffc800"));
  } catch (Throwable t) { }
}""")
M(ktask, r"""
public boolean work() {
  if (this.pr == null || !this.pr.isValid()) { toAdmin("went offline."); return false; }
  if (!this.onWorld) {
    java.util.UUID w0 = this.pr.getWorldUuid();
    if (w0 == null) return false;
    @WLD@ wo = @UNI@.get().getWorld(w0);
    if (wo == null) return false;
    this.wu = w0;
    this.onWorld = true;
    wo.execute(this);
    return true;
  }
  java.util.UUID nw = this.pr.getWorldUuid();
  if (nw == null || this.wu == null || !nw.equals(this.wu)) { toAdmin("changed worlds - try again."); return false; }
  java.util.UUID u = this.pr.getUuid();
  if (!this.k.equals(@PKG@.ClassCfg.pkey(u))) { toAdmin("switched profiles - try again."); return false; }
  if (@PKG@.Kit.busy(u)) { toAdmin("is still loading their profile - try again in a moment."); return false; }
  @REF@ ref = this.pr.getReference();
  if (ref == null || !ref.isValid()) return false;
  @ST@ st = ref.getStore();
  if (st == null) return false;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null || p.isWaitingForClientReady()) { toAdmin("is still loading - try again in a moment."); return false; }
  if (!@PKG@.Kit.alive(st, ref)) { toAdmin("is dead - try again after they respawn."); return false; }
  if (this.mode == 0) {
    if (!@PKG@.KitCfg.ON) return false;
    if (!"pending".equals(@PKG@.ClassStore.kitState(this.k))) { @PKG@.Kit.requeue(this.k); return false; }
    int c0 = @PKG@.ClassStore.classIndex(u);
    if (c0 < 0 || !@PKG@.ClassDefs.ENABLED[c0]) return false;
    String r0 = @PKG@.Kit.give(this.pr, p, this.k, c0, false, null);
    if (r0 != null) @PKG@.ClassCfg.warnLimited("class kit for " + this.k + ": " + r0 + " (retried)");
  } else if (this.mode == 1) {
    String r1 = @PKG@.Kit.give(this.pr, p, this.k, this.ci, true, this.by);
    if (r1 != null && this.by != null && this.by.isValid()) this.by.sendMessage(@MSG@.raw("[Classes] No kit given - " + r1).color("#ffc800"));
  } else {
    @PKG@.Kit.claim(this.pr, p, this.k, true);
  }
  return false;
}""")
M(ktask, r"""
public void run() {
  boolean hopped = false;
  try { hopped = work(); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class kit task failed: " + t); }
  if (!hopped && this.mode == 0 && this.k != null) @PKG@.Kit.INFLIGHT.remove(this.k);
}""")

# ================= 0.1.6 Kit, part 2: the scheduler-side rules (2 s ClassTick), the own picker, arrivals =================
M(kit_, r"""
public static void consider(@PR@ pr, boolean prof, long now) {
  java.util.UUID u = pr.getUuid();
  if (u == null) return;
  String k = @PKG@.ClassCfg.pkey(u);
  if (!"pending".equals(@PKG@.ClassStore.KITQ.get(k))) return;
  if (busy(u)) return;
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !@PKG@.ClassDefs.ENABLED[ci]) return;
  if (prof) {
    long e = @PKG@.ClassCfg.profileEpoch(u);
    long[] seen = (long[]) KITEP.get(u);
    if (seen == null || seen[0] != e) { KITEP.put(u, new long[] { e, now }); return; }
    if (now - seen[1] < EPOCH_WAIT_MS) return;
  }
  java.util.UUID wu = pr.getWorldUuid();
  if (wu == null) return;
  Object[] arr = (Object[]) KITARR.get(u);
  if (arr == null || !wu.equals(arr[0])) { KITARR.put(u, new Object[] { wu, Long.valueOf(now) }); return; }
  if (now - ((Long) arr[1]).longValue() < SAME_WORLD_MS) return;
  Long fl = (Long) INFLIGHT.get(k);
  if (fl != null && now - fl.longValue() < INFLIGHT_MS) return;
  @WLD@ w = @UNI@.get().getWorld(wu);
  if (w == null) return;
  INFLIGHT.put(k, Long.valueOf(now));
  w.execute(new @PKG@.KitTask(pr, k, wu, ci, 0, null, true));
}""")
M(kit_, r"""
public static void tick() {
  if (@PKG@.ClassStore.KITQ.isEmpty() || !@PKG@.KitCfg.ON) return;
  long now = System.currentTimeMillis();
  boolean prof = @PKG@.ClassCfg.profilesOn();
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ pr = (@PR@) it.next();
    if (pr == null || !pr.isValid()) continue;
    try { consider(pr, prof, now); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class kit check failed: " + t); }
  }
}""")
# own picker without SkyyProfiles (ClassPage "Confirm", world thread): no epoch wait, the kit lands at once
M(kit_, r"""
public static void now(@PR@ pr, @REF@ ref, @ST@ st) {
  try {
    if (!@PKG@.KitCfg.ON || pr == null || ref == null || st == null) return;
    java.util.UUID u = pr.getUuid();
    String k = @PKG@.ClassCfg.pkey(u);
    if (!"pending".equals(@PKG@.ClassStore.KITQ.get(k))) return;
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady() || !alive(st, ref)) return;
    int ci = @PKG@.ClassStore.classIndex(u);
    if (ci < 0 || !@PKG@.ClassDefs.ENABLED[ci]) return;
    String r = give(pr, p, k, ci, false, null);
    if (r != null) @PKG@.ClassCfg.warnLimited("class kit (class page) for " + k + ": " + r + " (retried by the tick)");
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class kit (class page) failed: " + t); }
}""")
# owed items of the active profile: retried OWED_DELAY_MS after every world arrival (never by the 2 s tick)
M(kit_, r"""
public static void owedLater(@PR@ pr) {
  try {
    if (pr == null || !pr.isValid()) return;
    String k = @PKG@.ClassCfg.pkey(pr.getUuid());
    if (!"owed".equals(@PKG@.ClassStore.KITQ.get(k))) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.KitTask(pr, k, null, -1, 2, null, false), OWED_DELAY_MS, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { }
}""")
M(kit_, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  KITEP.remove(u);
  KITARR.remove(u);
}""")
# /classadmin kit <player|uuid> [<class>] (both command forms): checks here, the give itself on the TARGET's world thread (KitTask mode 1)
M(kit_, r"""
public static void adminGive(@PR@ pr, String player, String clsName) {
  try {
    if (!pr.hasPermission("skyyclasses.admin")) { pr.sendMessage(@MSG@.raw("[Classes] no permission (skyyclasses.admin)")); return; }
    java.util.UUID t = @PKG@.ClassStore.resolve(player);
    if (t == null) { pr.sendMessage(@MSG@.raw("[Classes] Unknown player - use an online name or a uuid.")); return; }
    @PR@ tp = @UNI@.get().getPlayer(t);
    if (tp == null || !tp.isValid()) { pr.sendMessage(@MSG@.raw("[Classes] " + t + " is not online - /classadmin kit puts the items into their inventory right away.")); return; }
    int ci = -1;
    if (clsName != null) {
      ci = @PKG@.ClassDefs.indexOf(clsName);
      if (ci < 0) { pr.sendMessage(@MSG@.raw("[Classes] Unknown class. Classes: " + @PKG@.ClassDefs.allText())); return; }
    } else {
      ci = @PKG@.ClassStore.classIndex(t);
      if (ci < 0) { pr.sendMessage(@MSG@.raw("[Classes] " + tp.getUsername() + " has no class - name one: /classadmin kit <player> <class>")); return; }
    }
    String cls = @PKG@.ClassDefs.NAMES[ci];
    Object[] kk = @PKG@.KitCfg.parse(@PKG@.KitCfg.textOf(ci), null, @PKG@.KitCfg.MAX);
    if (((String[]) kk[0]).length == 0) { pr.sendMessage(@MSG@.raw("[Classes] The " + cls + " kit is empty - set it in Server Setup -> Classes -> Class kits (kit." + cls + " in config.properties).")); return; }
    java.util.UUID wu = tp.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null) { pr.sendMessage(@MSG@.raw("[Classes] Could not find the world of " + tp.getUsername() + " - try again in a moment.")); return; }
    w.execute(new @PKG@.KitTask(tp, @PKG@.ClassCfg.pkey(t), wu, ci, 1, pr, true));
    pr.sendMessage(@MSG@.raw("[Classes] Giving " + tp.getUsername() + " the " + cls + " kit..."));
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin kit <player|uuid> [class]")); }
}""")

# ================= 0.1.6 HealTask: the Priest placeholder heal, on the world thread right after the hit (spec 2.4) =================
htask.addInterface(pool.get("java.lang.Runnable"))
F(htask, "public java.util.UUID u;")
F(htask, "public float dealt;")
F(htask, "public String world;")
F(htask, "public static volatile boolean FAILED_ONCE = false;")
C(htask, "public HealTask(java.util.UUID u, float dealt, String world) { this.u = u; this.dealt = dealt; this.world = world; }")
# pure math (bare-JVM tested): one member's heal = min(damage x share %, maxPerHit); the Priest = that x self %; never above max Health
M(htask, r"""
public static double want(double dealt, long sharePct, double maxHit) {
  if (!(dealt > 0.0) || sharePct <= 0L) return 0.0;
  double w = dealt * (double) sharePct / 100.0;
  return w > maxHit ? maxHit : w;
}""")
M(htask, r"""
public static double selfWant(double want, long selfPct) {
  if (!(want > 0.0) || selfPct <= 0L) return 0.0;
  return want * (double) selfPct / 100.0;
}""")
M(htask, r"""
public static double room(double want, float now, float max) {
  if (!(want > 0.0) || now <= 0.0f || now >= max) return 0.0;
  double r = (double) (max - now);
  return want < r ? want : r;
}""")
M(htask, r"""
public static void failOnce(Throwable t) {
  if (FAILED_ONCE) return;
  FAILED_ONCE = true;
  @PKG@.ClassCfg.warn("priest heal failed (logged once): " + t);
}""")
# party:fn:members as String[] (null = SkyyParty missing or no answer; empty = not in a party) - the SkyySkills PartyXp.members pattern
M(htask, r"""
public static String[] members(java.util.UUID u) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("party:fn:members");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    String[] out = new String[a.length];
    for (int i = 0; i < a.length; i++) out[i] = a[i] == null ? null : String.valueOf(a[i]);
    return out;
  } catch (Throwable t) { return null; }
}""")
M(htask, r"""
public static @VEC@ pos(@ST@ s, @REF@ r) {
  try {
    @TC@ tc = (@TC@) s.getComponent(r, @TC@.getComponentType());
    return tc == null ? null : tc.getPosition();
  } catch (Throwable t) { return null; }
}""")
# heal one player: overheal is clamped first, then the per-second budget of that player is taken, then Health goes up
M(htask, r"""
public static double heal(@ST@ st, @REF@ r, java.util.UUID tu, double want, long now) {
  if (!(want > 0.01)) return 0.0;
  @ESM@ m = (@ESM@) st.getComponent(r, @ESM@.getComponentType());
  if (m == null) return 0.0;
  int hi = @DST@.getHealth();
  if (hi < 0) return 0.0;
  @ESV@ hv = m.get(hi);
  if (hv == null) return 0.0;
  double ask = room(want, hv.get(), hv.getMax());
  if (!(ask > 0.01)) return 0.0;
  double got = @PKG@.HealBudget.take(tu, ask, now, @PKG@.ClassCfg.HEAL_MAX_SEC);
  if (!(got > 0.01)) return 0.0;
  m.addStatValue(hi, (float) got);
  return got;
}""")
M(htask, r"""
public static void xp(java.util.UUID u, double hp) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("skill:fn:healxp");
    if (!(f instanceof java.util.function.Function)) return;
    ((java.util.function.Function) f).apply(new Object[] { u, Double.valueOf(hp), "classes:heal", @PKG@.ClassCfg.pkey(u) });
  } catch (Throwable t) { }
}""")
# one party member (never the Priest): online, same world (their Ref lives in this store = this thread), ready, alive, not creative, in range
M(htask, r"""
public double one(@ST@ st, @VEC@ c, String mid, double want, double r2, long now, String healer) {
  if (mid == null || mid.trim().length() == 0) return 0.0;
  java.util.UUID mu = java.util.UUID.fromString(mid.trim());
  if (mu.equals(this.u)) return 0.0;
  @PR@ mp = @UNI@.get().getPlayer(mu);
  if (mp == null || !mp.isValid()) return 0.0;
  @REF@ mr = mp.getReference();
  if (mr == null || !mr.isValid() || mr.getStore() != st) return 0.0;
  @PLA@ pl = (@PLA@) st.getComponent(mr, @PLA@.getComponentType());
  if (pl == null || pl.isWaitingForClientReady() || @PKG@.Kit.creative(pl) || !@PKG@.Kit.alive(st, mr)) return 0.0;
  @VEC@ mpos = pos(st, mr);
  if (mpos == null) return 0.0;
  double dx = mpos.x() - c.x();
  double dy = mpos.y() - c.y();
  double dz = mpos.z() - c.z();
  if (dx * dx + dy * dy + dz * dz > r2) return 0.0;
  double got = heal(st, mr, mu, want, now);
  if (got > 0.0) {
    @PKG@.HealMsg.given(this.u, mu, got);
    @PKG@.HealMsg.taken(mu, this.u, healer, got);
  }
  return got;
}""")
M(htask, r"""
public void run() {
  try {
    if (!@PKG@.ClassCfg.HEAL_ON) return;
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null || this.world == null || !this.world.equals(w.getName())) return;
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady() || @PKG@.Kit.creative(p) || !@PKG@.Kit.alive(st, ref)) return;
    @VEC@ c = pos(st, ref);
    if (c == null) return;
    double want = want((double) this.dealt, @PKG@.ClassCfg.HEAL_SHARE_PCT, @PKG@.ClassCfg.HEAL_MAX_HIT);
    if (!(want > 0.0)) return;
    double rad = @PKG@.ClassCfg.HEAL_RADIUS;
    double r2 = rad * rad;
    long now = System.currentTimeMillis();
    String[] ms = members(this.u);
    String healer = pr.getUsername();
    double others = 0.0;
    for (int i = 0; ms != null && i < ms.length; i++) {
      try { others = others + one(st, c, ms[i], want, r2, now, healer); } catch (Throwable t1) { failOnce(t1); }
    }
    double self = heal(st, ref, this.u, selfWant(want, @PKG@.ClassCfg.HEAL_SELF_PCT), now);
    if (self > 0.0) @PKG@.HealMsg.given(this.u, this.u, self);
    if (others > 0.0) xp(this.u, others);
  } catch (Throwable t) { failOnce(t); }
}""")

# ================= 0.1.6 PriestHealSys: DamageEventSystem in the INSPECT group (after ApplyDamage: only damage that really landed) =================
# Query.any (the target is an NPC; its component type is read inside like SkyySkills KillSys, so registration never depends on the NPC
# module's init order). No PvP: a target with a PlayerRef is skipped. No stat write inside the damage dispatch: HealTask runs next.
C(phs, "public PriestHealSys() { super(); }")
M(phs, r"""
public @QRY@ getQuery() {
  return @QRY@.any();
}""")
M(phs, r"""
public @SG@ getGroup() {
  return @DMOD@.get().getInspectDamageGroup();
}""")
# The creative check here is only an early out for melee (att = the attacker; for an orb att is not reliably the shooter, the reason
# DamageLock resolves orb shooters through Universe). The rule itself lives in HealTask.run: it resolves the Priest by UUID
# (Universe.getPlayer) and returns before any heal, chat line or XP when the Priest is in creative - for every hit, orbs included.
M(phs, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!@PKG@.ClassCfg.HEAL_ON) return;
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    float dealt = d.getAmount();
    if (dealt < 1.0f) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ tg = chunk.getReferenceTo(idx);
    if (tg == null || !tg.isValid()) return;
    if (buf.getComponent(tg, @PR@.getComponentType()) != null) return;
    if (buf.getComponent(tg, @NPC@.getComponentType()) == null) return;
    @PKG@.ShotRec rec = null;
    if (src instanceof @DPRJ@) rec = @PKG@.ShotTrack.find(buf, ((@DPRJ@) src).getProjectile());
    @REF@ att = ((@DENT@) src).getRef();
    @PR@ apr = null;
    if (att != null && att.isValid()) apr = (@PR@) buf.getComponent(att, @PR@.getComponentType());
    java.util.UUID u = null;
    String item = null;
    if (rec != null) {
      u = rec.shooter;
      item = rec.item;
    } else {
      if (apr == null) return;
      u = apr.getUuid();
      @IS@ main = @INVC@.getItemInHand(buf, att);
      if (main != null && !main.isEmpty()) item = main.getItemId();
    }
    if (u == null || item == null) return;
    if (@PKG@.ClassDefs.ownerOf(item) != @PKG@.ClassDefs.PRIEST) return;
    int ci = @PKG@.ClassStore.classIndex(u);
    if (ci != @PKG@.ClassDefs.PRIEST || !@PKG@.ClassDefs.ENABLED[ci]) return;
    if (apr != null && u.equals(apr.getUuid())) {
      @PLA@ pl = (@PLA@) buf.getComponent(att, @PLA@.getComponentType());
      if (@PKG@.Kit.creative(pl)) return;
    }
    @WLD@ w = ((@ES@) buf.getExternalData()).getWorld();
    if (w == null) return;
    w.execute(new @PKG@.HealTask(u, dealt, w.getName()));
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("priest heal failed: " + t); }
}""")

# ================= 0.1.6 KitHooks (config kit hooks: check= of the kit rows, the 7 "Use my hotbar" actions) + KitHotbarTask =================
M(khooks, r"""public static Object[] R(String st, String v, String m) { return new Object[] { st, v, m }; }""")
M(khooks, r"""
public static int classOfKey(String key) {
  if (key == null || !key.startsWith("kit.")) return -1;
  String c = key.substring(4);
  int d = c.indexOf('.');
  if (d >= 0) c = c.substring(0, d);
  for (int i = 0; i < @PKG@.ClassDefs.NAMES.length; i++) if (@PKG@.ClassDefs.NAMES[i].equals(c)) return i;
  return -1;
}""")
# the first item of a kit value that the kit's class cannot fight with (another class's weapon, or an unowned weapon while
# unassignedBlocked is on), as a sentence; null = fine
M(khooks, r"""
public static String warning(int ci, String value) {
  if (ci < 0 || value == null) return null;
  Object[] k = @PKG@.KitCfg.parse(value, null, 1000);
  String[] ids = (String[]) k[0];
  String first = null;
  int more = 0;
  for (int i = 0; i < ids.length; i++) {
    int o = @PKG@.ClassDefs.ownerOf(ids[i]);
    String w = null;
    if (o >= 0 && o != ci) w = ids[i] + " is " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[o]) + " weapon - " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[ci]) + " cannot fight with it";
    else if (o == @PKG@.ClassDefs.UNASSIGNED && @PKG@.ClassCfg.UNASSIGNED_BLOCKED) w = ids[i] + " is a weapon no class owns - nobody with a class can fight with it while Block weapons no class owns is on";
    if (w == null) continue;
    if (first == null) first = w; else more++;
  }
  if (first == null) return null;
  return first + (more > 0 ? " (and " + more + " more)" : "") + ".";
}""")
# check= of kit.<Class> (typed values, restore / import): null = fine, "?question" = the kit's confirm step
M(khooks, r"""
public static String checkKit(String key, String value) {
  if (value == null) return null;
  String w = warning(classOfKey(key), value);
  return w == null ? null : "?" + w + " Save anyway?";
}""")
kht.addInterface(pool.get("java.lang.Runnable"))
F(kht, "public @PR@ pr;")
F(kht, "public String worldName;")
F(kht, "public java.util.UUID who;")
F(kht, "public String name;")
F(kht, "public String cls;")
F(kht, "public static final java.util.concurrent.ConcurrentHashMap ASKED = new java.util.concurrent.ConcurrentHashMap();")  # "<admin>|<Class>" -> Object[]{hotbar text, Long asked at}
F(kht, "public static final long ASK_MS = %dL;" % KIT_HOTBAR_ASK_MS)
C(kht, "public KitHotbarTask(@PR@ p, String wn, java.util.UUID u, String n, String c) { this.pr = p; this.worldName = wn; this.who = u; this.name = n; this.cls = c; }")
# review fix: the kit check's question is answered by a SECOND click (same admin, same kit, same hotbar, within ASK_MS) - pure, bare-JVM tested
M(kht, r"""
public static String askKey(java.util.UUID who, String cls) {
  return String.valueOf(who) + "|" + cls;
}""")
M(kht, r"""
public static boolean again(String key, String text, long now) {
  if (key == null || text == null) return false;
  Object[] a = (Object[]) ASKED.get(key);
  if (a == null) return false;
  long at = ((Long) a[1]).longValue();
  if (now - at > ASK_MS || now < at) { ASKED.remove(key); return false; }
  return text.equals(a[0]);
}""")
M(kht, r"""
public static void asked(String key, String text, long now) {
  if (key == null || text == null) return;
  if (ASKED.size() > 200) ASKED.clear();
  ASKED.put(key, new Object[] { text, Long.valueOf(now) });
}""")
M(kht, r"""
public static String askText(String cls, String question) {
  String q = question == null ? "" : question;
  if (q.endsWith(" Save anyway?")) q = q.substring(0, q.length() - 13);
  return "The " + cls + " kit was NOT changed: " + q + " To save it anyway, click Use my hotbar on the " + cls + " kit again within " + (ASK_MS / 1000L) + " s with the same hotbar.";
}""")
# the 9 hotbar stacks as "id:amount,..." (the same id twice is added up, max 9999; item metadata is not kept), null = empty (SkyyIslands 0.5.2)
M(kht, r"""
public static String hotbarText(@PLA@ p) {
  @INV@ inv = p.getInventory();
  if (inv == null) return null;
  @IC@ hb = inv.getHotbar();
  if (hb == null) return null;
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  short cap = hb.getCapacity();
  for (short sl = 0; sl < cap; sl++) {
    @IS@ it = hb.getItemStack(sl);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    if (id == null || id.length() == 0) continue;
    int q = it.getQuantity();
    Object had = m.get(id);
    if (had instanceof Integer) q = q + ((Integer) had).intValue();
    if (q > 9999) q = 9999;
    if (q < 1) q = 1;
    m.put(id, Integer.valueOf(q));
  }
  if (m.isEmpty()) return null;
  StringBuilder sb = new StringBuilder();
  java.util.Iterator e = m.keySet().iterator();
  while (e.hasNext()) {
    String k = (String) e.next();
    if (sb.length() > 0) sb.append(',');
    sb.append(k).append(':').append(((Integer) m.get(k)).intValue());
  }
  return sb.toString();
}""")
M(kht, r"""
public void say(String text, boolean ok) {
  try { if (this.pr != null && this.pr.isValid()) this.pr.sendMessage(@MSG@.raw("[Classes] " + text).color(ok ? "#8fe39a" : "#ffc800")); } catch (Throwable t) { }
}""")
# review fix: the value is set with confirm="" first, so the kit check's question (another class's weapon in this kit) really stops the
# save; the menu's own danger confirm came before the hotbar was read and cannot show it. The question goes to chat; a second click on
# the same kit within ASK_MS with an unchanged hotbar sets it with confirm=yes ("Save anyway").
M(kht, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID wu = this.pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) { say("You changed worlds before your hotbar was read - the " + this.cls + " kit was not changed. Try again.", false); return; }
    @REF@ ref = this.pr.getReference();
    if (ref == null) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { say("Could not read your hotbar - the " + this.cls + " kit was not changed.", false); return; }
    String text = hotbarText(p);
    if (text == null) { say("Your hotbar is empty - put the " + this.cls + " kit in your 9 hotbar slots, then try again. Nothing was changed.", false); return; }
    String ak = askKey(this.who, this.cls);
    long now = System.currentTimeMillis();
    boolean yes = again(ak, text, now);
    Object[] r = @PKG@.CfgFn.set("kit." + this.cls, text, this.who, this.name, yes ? "yes" : "", "menu");
    String stt = (r == null || r.length < 3) ? "error" : String.valueOf(r[0]);
    String msg = (r == null || r.length < 3) ? "Could not change the " + this.cls + " kit - see the server log." : String.valueOf(r[2]);
    if (stt.equals("confirm")) {
      asked(ak, text, now);
      say(askText(this.cls, msg), false);
      return;
    }
    ASKED.remove(ak);
    boolean ok = stt.equals("ok") || stt.equals("restart");
    say(msg, ok);
  } catch (Throwable t) {
    @PKG@.ClassCfg.warn("class kit from hotbar failed: " + t);
    say("Something went wrong - the server log has the details.", false);
  }
}""")
# actions need the admin's hotbar: schedule on their world thread and answer "working on it" (config contract guarantee 3)
M(khooks, r"""
public static Object[] hotbar(String cls, java.util.UUID who, String name) {
  @PR@ pr = who == null ? null : @UNI@.get().getPlayer(who);
  if (pr == null || !pr.isValid()) return R("bad", null, "Only an admin who is in game can use this: put the kit in your hotbar first.");
  java.util.UUID wu = pr.getWorldUuid();
  @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
  if (w == null) return R("error", null, "Could not find your world - try again in a moment.");
  w.execute(new @PKG@.KitHotbarTask(pr, w.getName(), who, name, cls));
  return R("ok", null, "Reading your hotbar - the new " + cls + " kit is shown in the chat in a moment.");
}""")
for _c in CLASSES:   # one hook per action row (the kit's action contract passes no key)
    M(khooks, "public static Object[] hb%s(java.util.UUID who, String name) { return hotbar(%s, who, name); }" % (_c["name"], jstr(_c["name"])))

# ================= 0.1.6 KitMigrate: at the first start of 0.1.6, every existing profile with a class and no kit flag becomes kit=old =================
# (no surprise kit for anyone - also not after an admin reset + new pick). Files are read and written directly (not through the DATA
# cache). Any failure leaves kits.properties unwritten: the next start retries (marking is idempotent).
M(kmig, r"""
public static int markFile(java.nio.file.Path f) throws Exception {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  String c = p.getProperty("class");
  if (c == null || c.trim().length() == 0 || p.getProperty("kit") != null) return 0;
  p.setProperty("kit", "old");
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
  try { p.store(out, "SkyyClasses player"); } finally { out.close(); }
  java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  return 1;
}""")
M(kmig, (r"""
public static void runOnce() {
  try {
    java.nio.file.Path dir = @PKG@.ClassStore.DIR;
    if (dir == null) return;
    java.nio.file.Path base = dir.getParent();
    java.nio.file.Path marker = base.resolve("kits.properties");
    if (java.nio.file.Files.exists(marker, new java.nio.file.LinkOption[0])) return;
    int marked = 0;
    int files = 0;
    int failed = 0;
    if (java.nio.file.Files.isDirectory(dir, new java.nio.file.LinkOption[0])) {
      java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(dir, "*.properties");
      try {
        java.util.Iterator it = ds.iterator();
        while (it.hasNext()) {
          java.nio.file.Path f = (java.nio.file.Path) it.next();
          files++;
          try { marked = marked + markFile(f); } catch (Throwable t1) { failed++; @PKG@.ClassCfg.warnLimited("class kits: could not mark " + f.getFileName() + ": " + t1); }
        }
      } finally { ds.close(); }
    }
    if (failed > 0) {
      @PKG@.ClassCfg.warn("class kits: " + failed + " player files could not be read or written - the migration runs again at the next start (" + marked + " marked this time)");
      return;
    }
    java.util.Properties m = new java.util.Properties();
    m.setProperty("migratedAt", String.valueOf(System.currentTimeMillis()));
    m.setProperty("marked", String.valueOf(marked));
    m.setProperty("files", String.valueOf(files));
    m.setProperty("version", "__VER__");
    java.nio.file.Files.createDirectories(base, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = base.resolve("kits.properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { m.store(out, "SkyyClasses class kits migration - existing profiles were marked kit=old (no automatic kit). Delete = run again."); } finally { out.close(); }
    java.nio.file.Files.move(tmp, marker, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    @PKG@.ClassCfg.info("class kits: " + marked + " existing profiles marked as picked before kits - they get no automatic kit");
  } catch (Throwable t) { @PKG@.ClassCfg.warn("class kits: migration failed (runs again at the next start): " + t); }
}""").replace("__VER__", VERSION))

# ================= ClassPage: /class =================
# 0.1.6: 15 pt buttons, 1000 x 900 root (7 cards, fits 1080): 3 + 40 + 28 + 7 x (6 + 96) + 8 + 26 + 40 = 859 + 28 padding = 887
BTN = ("Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 15, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
       "Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
       "Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
BTN_GO = ("Style: TextButtonStyle(Default: (Background: #2f6a3a, LabelStyle: (FontSize: 15, TextColor: #e9ffe9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
          "Hovered: (Background: #3f8a4a, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
          "Pressed: (Background: #1f4a2a, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
PAGE_W, PAGE_H = 1000, 900
assert 3 + 40 + 28 + len(CLASSES) * (6 + 96) + 8 + 26 + 40 + 28 <= PAGE_H <= 1080, "the /class page must fit its root and 1080"
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
  b.appendInline((String) null, "Group #SkyyCls { Anchor: (Width: __W__, Height: __H__); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyCls", "Group { Anchor: (Height: 3); Background: #d08a4a; }");
  b.appendInline("#SkyyCls", "Label { Anchor: (Height: 40); Text: \"Classes\"; Style: (FontSize: 22, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  String sub = cur < 0 ? "You have no class yet - your first choice is free. Your class decides your weapons and your combat skill."
    : "You are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[cur]) + " - combat skill " + @PKG@.ClassDefs.SKILLS[cur] + ". Only " + @PKG@.ClassDefs.NAMES[cur] + " weapons deal damage for you.";
  if (lockp) sub = "Your class is locked to this profile - you are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[cur]) + " with combat skill " + @PKG@.ClassDefs.SKILLS[cur] + ". A new class means a new profile.";
  if (lockp && !@PKG@.ClassDefs.ENABLED[cur]) sub = "This profile is locked to " + @PKG@.ClassDefs.NAMES[cur] + " - not playable yet. Its weapons deal no damage until it is released.";
  if (np) sub = "You have no profile yet. Type /profiles to create one - you pick your class there and it is locked to that profile.";
  b.appendInline("#SkyyCls", "Label #SkyyClsSub { Anchor: (Height: 28); Text: \"" + safe(sub) + "\"; Style: (FontSize: 14, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  for (int i = 0; i < @PKG@.ClassDefs.NAMES.length; i++) {
    boolean on = @PKG@.ClassDefs.ENABLED[i];
    boolean sel = i == cur;
    boolean pend = i == this.pending;
    String bg = sel ? "#173524(0.95)" : (pend ? "#3a2f1a(0.95)" : (on ? "#142030(0.9)" : "#0d1219(0.85)"));
    String nameColor = on ? @PKG@.ClassDefs.COLORS[i] : "#5f6b78";
    String textColor = on ? "#c9d6e2" : "#5f6b78";
    b.appendInline("#SkyyCls", "Label { Anchor: (Height: 6); Text: \"\"; }");
    b.appendInline("#SkyyCls", "Group #SkyyClsCard" + i + " { Anchor: (Height: 96); LayoutMode: Left; Background: " + bg + "; }");
    b.appendInline("#SkyyClsCard" + i, "Label { Anchor: (Width: 12, Height: 96); Text: \"\"; }");
    b.appendInline("#SkyyClsCard" + i, "Group #SkyyClsIco" + i + " { Anchor: (Width: 224, Height: 96); LayoutMode: Left; }");
    String[] ic = @PKG@.ClassDefs.ICONS[i].split(",");
    for (int k = 0; k < ic.length && k < 4; k++) {
      b.appendInline("#SkyyClsIco" + i, "Group { Anchor: (Width: 56, Height: 96); ItemIcon { Anchor: (Width: 48, Height: 48, Left: 4, Top: 24); ItemId: \"" + safe(ic[k]) + "\"; } }");
    }
    b.appendInline("#SkyyClsCard" + i, "Group #SkyyClsTxt" + i + " { Anchor: (Width: 548, Height: 96); LayoutMode: Top; Padding: (Top: 2); }");
    String title = @PKG@.ClassDefs.NAMES[i] + (sel ? " - your class" : (on ? " - " + @PKG@.ClassDefs.ROLES[i] : " - coming soon"));
    b.appendInline("#SkyyClsTxt" + i, "Label { Anchor: (Height: 30); Text: \"" + safe(title) + "\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + nameColor + ", VerticalAlignment: Center); }");
    b.appendInline("#SkyyClsTxt" + i, "Label { Anchor: (Height: 22); Text: \"" + safe("Combat skill " + @PKG@.ClassDefs.SKILLS[i] + " - " + @PKG@.ClassDefs.WTEXT[i]) + "\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + (on ? "#9fd8a2" : "#5f6b78") + ", VerticalAlignment: Center); }");
    b.appendInline("#SkyyClsTxt" + i, "Label { Anchor: (Height: 40); Text: \"" + safe(@PKG@.ClassDefs.DESCS[i]) + "\"; Style: (FontSize: 13, TextColor: " + textColor + ", VerticalAlignment: Center, Wrap: true); }");
    b.appendInline("#SkyyClsCard" + i, "Group #SkyyClsAct" + i + " { Anchor: (Width: 168, Height: 96); LayoutMode: Top; Padding: (Top: 28); }");
    if (lockp && sel) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 160, Height: 40); Text: \"Selected\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fe39a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else if (!on) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 160, Height: 40); Text: \"Coming soon\"; Style: (FontSize: 14, RenderBold: true, TextColor: #5f6b78, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else if (sel) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 160, Height: 40); Text: \"Selected\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fe39a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else if (lockp || np) {
      b.appendInline("#SkyyClsAct" + i, "Label { Anchor: (Width: 160, Height: 40); Text: \"Locked\"; Style: (FontSize: 14, RenderBold: true, TextColor: #5f6b78, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else {
      b.appendInline("#SkyyClsAct" + i, "TextButton #SkyyClsPick" + i + " { Anchor: (Width: 160, Height: 40); Text: \"" + (cur < 0 ? "Choose" : "Switch") + "\"; " + (pend ? go : bs) + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyClsPick" + i, @EVD@.of("a", "clspick" + i));
    }
  }
  b.appendInline("#SkyyCls", "Label { Anchor: (Height: 8); Text: \"\"; }");
  b.appendInline("#SkyyCls", "Label #SkyyClsInfo { Anchor: (Height: 26); Text: \"" + safe(this.info) + "\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffd27a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  long cost = @PKG@.ClassCfg.SWITCH_COST;
  if (!lockp && !np && this.pending >= 0 && this.pending < @PKG@.ClassDefs.NAMES.length) {
    String pn = @PKG@.ClassDefs.NAMES[this.pending];
    String q = cur < 0 ? "Become " + @PKG@.ClassDefs.article(pn) + "? Your first choice is free."
      : "Switch to " + pn + " for " + cost + " coins? Your " + @PKG@.ClassDefs.NAMES[cur] + " progress is kept.";
    b.appendInline("#SkyyCls", "Group #SkyyClsConfirm { Anchor: (Height: 40); LayoutMode: Left; }");
    b.appendInline("#SkyyClsConfirm", "Label { Anchor: (Width: 640, Height: 40); Text: \"" + safe(q) + "\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }");
    b.appendInline("#SkyyClsConfirm", "TextButton #SkyyClsYes { Anchor: (Width: 140, Height: 38); Text: \"Confirm\"; " + go + " }");
    b.appendInline("#SkyyClsConfirm", "Label { Anchor: (Width: 12, Height: 38); Text: \"\"; }");
    b.appendInline("#SkyyClsConfirm", "TextButton #SkyyClsNo { Anchor: (Width: 140, Height: 38); Text: \"Cancel\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyClsYes", @EVD@.of("a", "clsyes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyClsNo", @EVD@.of("a", "clsno"));
  } else if (np) {
    String nf = "Your class comes from your profile - type /profiles to create it. Shields and tools work for every class. Hatchets are tools.";
    b.appendInline("#SkyyCls", "Label #SkyyClsFoot { Anchor: (Height: 40); Text: \"" + safe(nf) + "\"; Style: (FontSize: 13, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
  } else if (lockp) {
    String pt = @PKG@.ClassCfg.profileText(u);
    String lf = "Class locked to " + (pt.length() > 0 ? pt : "this profile") + ". To play another class create a new profile. Shields and tools work for every class. Hatchets are tools.";
    b.appendInline("#SkyyCls", "Label #SkyyClsFoot { Anchor: (Height: 40); Text: \"" + safe(lf) + "\"; Style: (FontSize: 13, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
  } else {
    String foot = "Switching costs " + cost + " coins (first choice free) - cooldown " + @PKG@.ClassCfg.COOLDOWN_MIN + " min"
      + (@PKG@.ClassStore.coinsReady() ? " - purse " + @PKG@.ClassStore.purse(u) + " coins" : "") + ". Shields and tools work for every class. Hatchets are tools.";
    b.appendInline("#SkyyCls", "Label #SkyyClsFoot { Anchor: (Height: 40); Text: \"" + safe(foot) + "\"; Style: (FontSize: 13, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
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
      if (!@PKG@.ClassCfg.profilesOn()) @PKG@.Kit.now(this.playerRef, ref, st);   // 0.1.6: own picker = the kit lands at once
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
    @PKG@.Kit.owedLater(pr);   // 0.1.6: owed kit items of this profile (the load above just filled KITQ at a join)
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
    @PKG@.Kit.owedLater(pr);   // 0.1.6: every world arrival retries owed kit items, before the once-per-session check
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
    @PKG@.Kit.forget(u);
    @PKG@.HealBudget.forget(u);
    @PKG@.HealMsg.forget(u);
  } catch (Throwable t) { }
}""")

# ================= ClassTick (0.1.3): profile epoch check every 2 s -> republish class:<uuid> (contract rule 3). No SkyyProfiles = no-op =================
# 0.1.6: first the class kit rules (Kit.tick, returns at once while nothing is pending) and the heal chat lines, with or without SkyyProfiles
ctick.addInterface(pool.get("java.lang.Runnable"))
F(ctick, "public static int FAILS = 0;")
C(ctick, "public ClassTick() { }")
M(ctick, r"""
public void run() {
  try { @PKG@.Kit.tick(); } catch (Throwable t0) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("class kit tick failed: " + t0); } }
  try { @PKG@.HealMsg.flushDue(); } catch (Throwable t2) { }
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

# ================= 0.1.6 /class kit (player sub-command: collect owed kit items of the active profile, or see the kit state) =================
C(kcmd, r"""
public ClassKitCmd() {
  super("kit", "Collect class kit items that did not fit your inventory (or see your kit)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(kcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    java.util.UUID u = pr.getUuid();
    String k = @PKG@.ClassCfg.pkey(u);
    java.util.Properties p = @PKG@.ClassStore.loadKey(k);
    if (!"owed".equals(p.getProperty("kit"))) { @PKG@.Kit.tell(pr, @PKG@.Kit.stateLine(p), false); return; }
    if (@PKG@.Kit.busy(u)) { @PKG@.Kit.tell(pr, "Your profile is still loading - try again in a moment.", true); return; }
    @PLA@ pl = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (pl == null) return;
    @PKG@.Kit.claim(pr, pl, k, false);
  } catch (Throwable t) {
    @PKG@.ClassCfg.warn("/class kit failed: " + t);
    pr.sendMessage(@MSG@.raw("[Classes] Could not check your class kit - the server log has the details."));
  }
}""")

# ================= /class =================
C(cmd, r"""
public ClassCmd() {
  super("class", "Open the class page - Archer, Warrior, Mage, Berserker, Priest (Assassin and Shaman later)");
  addAliases(new String[] { "classes" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.ClassKitCmd());
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
  this.classArg = withRequiredArg("class", "archer | warrior | mage | berserker | priest", @ATY@.STRING);
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
    pr.sendMessage(@MSG@.raw("[Classes] " + t + ": " + @PKG@.ClassStore.describe(t)
      + " | " + @PKG@.ClassStore.kitText(@PKG@.ClassStore.loadKey(@PKG@.ClassCfg.pkey(t)))));   // 0.1.6: + the kit state
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin info <player|uuid>")); }
}""")
C(arel, 'public AdminReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyyClasses/config.properties"); }')
# 0.1.5: the kit's reload op (hand edits logged via=file, ClassCfg.load runs after the kit's pending writes), then flush so the reply
# shows current values, then the two inert keys (never a bound field)
M(arel, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (!pr.hasPermission("skyyclasses.admin")) { pr.sendMessage(@MSG@.raw("[Classes] no permission (skyyclasses.admin)")); return; }
  String k = "not re-read by the config kit";
  try {
    Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", pr.getUuid(), pr.getUsername(), "command" });
    if (o instanceof Object[] && ((Object[]) o).length > 2) k = String.valueOf(((Object[]) o)[2]);
  } catch (Throwable t) { k = "the config kit could not re-read it: " + t; }
  try { @PKG@.CfgPub.flush(); } catch (Throwable t) { @PKG@.ClassCfg.warn("config flush failed: " + t); }
  @PKG@.ClassCfg.loadInert();
  pr.sendMessage(@MSG@.raw("[Classes] config reloaded: " + @PKG@.ClassCfg.summary() + " (" + k + ")"));
}""")
# 0.1.6: /classadmin kit <player|uuid> [<class>] - give a kit NOW to an online player (ignores the flag; disabled classes allowed for
# testing, empty kits refused). Optional args are not positional (HANDOFF COMMAND RULES 2: acceptCall0 needs the token count to equal
# the required-arg count), so "<player> <class>" is a usage variant (SkyyRolls / SkyyVault pattern: description-only constructor +
# withRequiredArg, the sub-command calls addUsageVariant; the engine picks it by the token count). Both call requirePermission AND
# setPermissionGroups(new String[0]): the node never lands in a permission group.
akit2 = pool.makeClass(PKG + ".AdminKitClassCmd", pool.get(T["APC"]))
F(akit2, "public @RA@ playerArg;")
F(akit2, "public @RA@ classArg;")
C(akit2, r"""
public AdminKitClassCmd() {
  super("(admin) Give a player the kit of a class now: /classadmin kit <player|uuid> <class>");
  requirePermission("skyyclasses.admin");
  setPermissionGroups(new String[0]);
  this.playerArg = withRequiredArg("player", "online player name or uuid", @ATY@.STRING);
  this.classArg = withRequiredArg("class", "archer | warrior | mage | berserker | priest (assassin, shaman for testing)", @ATY@.STRING);
}""")
M(akit2, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.Kit.adminGive(pr, String.valueOf(ctx.get(this.playerArg)), String.valueOf(ctx.get(this.classArg)));
}""")
F(akit, "public @RA@ playerArg;")
C(akit, r"""
public AdminKitCmd() {
  super("kit", "(admin) Give a player a class kit now: /classadmin kit <player|uuid> [class] (default: their class)");
  requirePermission("skyyclasses.admin");
  setPermissionGroups(new String[0]);
  this.playerArg = withRequiredArg("player", "online player name or uuid", @ATY@.STRING);
  addUsageVariant(new @PKG@.AdminKitClassCmd());
}""")
M(akit, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.Kit.adminGive(pr, String.valueOf(ctx.get(this.playerArg)), null);
}""")
C(adm, r"""
public ClassAdminCmd() {
  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | kit <player> [class] | reload");
  requirePermission("skyyclasses.admin");
  addSubCommand(new @PKG@.AdminSetCmd());
  addSubCommand(new @PKG@.AdminResetCmd());
  addSubCommand(new @PKG@.AdminInfoCmd());
  addSubCommand(new @PKG@.AdminKitCmd());
  addSubCommand(new @PKG@.AdminReloadCmd());
}""")
M(adm, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | kit <player|uuid> [class] | reload"));
  pr.sendMessage(@MSG@.raw("[Classes] classes: " + @PKG@.ClassDefs.listText() + " | config: " + @PKG@.ClassCfg.summary()));
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
  @PKG@.KitMigrate.runOnce();   // 0.1.6: existing profiles with a class -> kit=old (once; before kitnew can be called)
  java.util.Map b = @PKG@.ClassCfg.bridge();
  b.put("class:list", @PKG@.ClassDefs.listText());
  for (int i = 0; i < @PKG@.ClassDefs.NAMES.length; i++) b.put("class:weapons:" + @PKG@.ClassDefs.NAMES[i], @PKG@.ClassDefs.prefixesOf(i));
  b.put("class:weapons:free", @PKG@.ClassDefs.prefixesOf(@PKG@.ClassDefs.FREE));
  b.put("class:weapons:unassigned", @PKG@.ClassDefs.prefixesOf(@PKG@.ClassDefs.UNASSIGNED));
  b.put("class:fn:allowed", new @PKG@.AllowedFn());
  b.put("class:fn:get", new @PKG@.GetFn());
  b.put("class:fn:kitnew", new @PKG@.KitNewFn());   // 0.1.6 (SkyyProfiles 0.1.2 Create Profile)
  getCommandRegistry().registerCommand(new @PKG@.ClassCmd());
  getCommandRegistry().registerCommand(new @PKG@.ClassAdminCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.ClassReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.ClassQuit());
  getEntityStoreRegistry().registerSystem(new @PKG@.ShotTrack());
  getEntityStoreRegistry().registerSystem(new @PKG@.DamageLock());
  getEntityStoreRegistry().registerSystem(new @PKG@.PriestHealSys());   // 0.1.6: Inspect group, after the damage landed
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ClassTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  @PKG@.ClassCfg.regSetting("classes.blockedChat", "Blocked weapon - chat line", "combat", true, "Only Archers can use bows... - at most every 3 s. The hit is blocked either way");
  @PKG@.ClassCfg.regSetting("classes.blockedPopup", "Blocked weapon - popup", "combat", true, "The popup with the weapon's icon - at most every 1.5 s");
  @PKG@.ClassCfg.regSetting("classes.healGiven", "Priest heals - your heals", "combat", true, "Your heals: +23 HP to 2 party members and +6 HP to you - one line every 10 s at most");
  @PKG@.ClassCfg.regSetting("classes.healTaken", "Priest heals - healed by others", "combat", true, "Skyy healed you +12 HP - one line every 10 s at most. The heal happens either way");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyClasses] __VER__ ready - /class, /class kit, /classadmin; classes " + @PKG@.ClassDefs.listText() + "; " + cfgText + " (coins bridge " + (@PKG@.ClassStore.coinsReady() ? "found" : "not found yet") + "; profiles " + (@PKG@.ClassCfg.profilesOn() ? "SkyyProfiles found - class per profile" : "SkyyProfiles not loaded yet - class per player") + "; config also in game: SkyWynn Menu -> Server Setup -> Classes)");
}""".replace("__VER__", VERSION))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in (cfg, kcfg, hooks, defs, st_, rul, afn, gfn, knew, srec, strk, lock, hbud, hmsg, kit_, ktask, htask, phs, khooks, kht, kmig,
          page, opn, rtk, rdy, quit_, ctick, kcmd, cmd, aset, ares, ainf, akit2, akit, arel, adm, pl):
    c.writeFile(OUT)
kit.write(OUT)
print("classes written (+%d config kit classes)" % len(kit.classes))

jar = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
m = B.manifest("SkyyClasses", VERSION, "SkyWynn classes (Wynncraft style): Archer, Warrior, Mage, Berserker, Priest (Assassin and Shaman later). Your class decides your weapons and your combat skill; every class gets a kit with its basic weapon; Priests heal their party. /class to choose, locked per profile with SkyyProfiles. Zero dependencies (SkyyProfiles, SkyyParty, SkyySkills and SkyyCoins optional).", PKG + ".SkyyClassesPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    raise SystemExit("SkyyClasses: --deploy is not supported here - deploys go through tools/deploy_set.py")
