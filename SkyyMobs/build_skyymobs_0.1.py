"""SkyyMobs 0.1 - build script (javassist via jpype). NEW MOD: stage 1 of research/Mob-Levels-Plan.md (section 13), with the zone bands
re-fitted in research/cloud/Mob-Levels-Refit.md and Skyy's decisions in OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02" round 5 + the
LOCKED 2026-10-01 zone bands (those win over the plan).
Run:   python SkyyMobs/build_skyymobs_0.1.py          -> SkyyMobs/SkyyMobs-0.1.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Test:  python SkyyMobs/test_skyymobs_0.1.py           (bare JVM, -Xverify:all; scratch under tools/dev/scratch/mobs01/)

WHAT IT DOES
  Every hostile mob and every neutral fighter that spawns (or loads from a saved chunk) gets a level from WHERE it spawned. The level
  raises its max health and the damage it deals, and the vanilla nameplate shows "[Lv 9] Trork Warrior". No ticking system, no UI page.
  Zone bands (LOCKED 2026-10-01): Zone 1 = Lv 1-20 (the blue forest Forest_Azure, Autumn and Moss at the top: 18-20), Zone 2 = 20-30,
  Zone 3 = 30-45, Zone 4 = 45-60. Biome bands inside each zone = the refit's tables (rarer biomes higher). Random level inside the band.

WHO GETS A LEVEL (Skyy R5: hostile mobs AND neutral fighters; animals / passive never; never players, pets of other mods, NPC traders,
bosses). Engine finding that changes the plan's rule: WorldSupport.getDefaultPlayerAttitude() is HOSTILE for every role that does not
set an attitude (SupportConfigBuilder.readConfig default = Attitude.HOSTILE, bytecode 2026-10-02) - every bird, fish, frog, mouse,
snail and other mods' pets (FPets Floating_Pet_*, Kazzy mounts) would be "hostile". So the attitude alone is not the test:
  1. players never (the hook only sees NPCEntity + EntityStatMap holders);
  2. attitude HOSTILE or NEUTRAL only (FRIENDLY / REVERED = tamed animals, IGNORE = summons and lantern pets: never);
  3. the role id must be in the BUILT-IN list (the jar constant MobCfg.VANILLA) or match "Extra mobs that get levels" (levels.roles,
     empty by default). The built-in list = the EXACT vanilla role ids, generated HERE from Assets.zip: every vanilla role whose attitude
     is hostile and whose template is a fighter (Template_Predator / Intelligent / Flying_Aggressive / Swimming_Aggressive / Goblin* /
     Trork* / Cactee ...) + the neutral fighters Boar, Warthog, every Scarak, the Feran warriors (Sharptooth, Longtooth, Burrower,
     Windwalker) - 244 ids, proven equal to the role set at build time. Exact ids, not Prefix* patterns (review F1): other mods reuse
     vanilla prefixes for their own mounts, pets, NPCs and bosses (Bear_Grizzly_Mount, Wolf_Pet, Spider_Mount, Wraith_Trader,
     Dungeon_*NPCRole, Dungeon_*_Boss: 193 roles in Skyy's Mods folder matched the old patterns). ~5 KB = over the kit's 2000-character
     row, so the list is not a row; an admin removes a vanilla mob with levels.exclude and adds other mods' mobs with levels.roles;
  4. NEUTRAL roles also need "Neutral fighters get levels" (levels.neutral, default on);
  5. never a role in "Never level these" (levels.exclude): tests, tamed animals, temple NPCs, traders, summons, the bosses (Goblin_Duke,
     Trork_Chieftain, Dragon_*, the 0.7 Skeleton_Elite) - bosses get fixed levels in stage 3 - and other mods' mounts / pets / NPCs /
     bosses under an extra pattern (*_Mount*, *_Pet*, *_Boss*, *NPC*, *_Hub*, *Blacksmith*, *Trader*; not *_Sentry*: Trork_Sentry).
  Unknown roles from other mods get no level until an admin adds them (degrades safely); so do the roles new in the 0.7 pre-release
  (Coffer_Goblin_*, Goblin_Burner / Feastmaster / Guardian, Void_Spectre, Void_Spawn_* ...: the next build after 0.7 ships, or the
  extra row). A mob that stops qualifying (tamed: the role change re-adds it as Tamed_* REVERED, or an admin edits the lists) loses its
  level + plate the next time it is added.

WHERE THE LEVEL COMES FROM (first match wins; MobLevel.resolve, pure Java, the harness drives it with strings)
  0 saved   the level saved on the mob (see PERSISTENCE) - kept after chunk reloads and restarts
  2 world   bands.world: world name or its start (dungeon_ = dungeon_1 ...; 0,0 = no levels there) - instances, hub, admin pins
  3 island  SkyyIslands private island worlds (bridge island:owner:fn) -> bands.islands (default 0 = no level)
  4 lava    Skyy R5: vanilla's deep lava caves (Env_Zone1-3_Caves_Volcanic_T1..T3, Env_Zone4_Caves_Volcanic - ids checked in Assets.zip)
            = the band of the HARDEST biome row of that zone (Zone 1 18-20, Zone 2 28-30, Zone 3 43-45, Zone 4 58-60), any world type
  4 biome   classic worldgen (ChunkGenerator): region + biome at the spawn point -> bands.biome (exact Region.Biome, else the region
            row Region). Overlay biomes in bands.passThrough (rivers, lakes, dunes, valleys, villages ...) use the tile biome underneath.
            Caves = the ground above (the 2D lookup). The environment's Bonus column is added on top. The refit's pattern rows
            (Zone1_Tier1.*_Trork, Plateau_*, Mountain_*, Env_Zone1_Caves* ...) ship EXPANDED into one row per Assets.zip biome /
            environment, because the config kit refuses * in a table entry (only entry=itemprefix tables take one) - so every
            number is editable in Server Setup. A * key typed into the file by hand still works (MobBands.find: most specific wins).
  5 env     bands.env band (worlds without classic zone data: the hand-built island chain painted with /setenvironment, World Gen 2)
  6 zone    bands.zone from the region name (Zone2_Tier1 -> Zone2) or the env id (Env_Zone2_... -> Zone2)
  7 default bands.default (default 0 = no level). Oceans (Skyy R5: skip) have no rows - whatever the lookup gives (normally no level).
  Spawn point = NPCEntity.getLeashPoint() (saved LeashPos), else the current position. Spawn environment = NPCEntity.getEnvironment()
  (world spawns), else the block environment at the spawn point (3D, so caves get their cave environment). Level = roll inside the
  band (seeded: world seed + mob UUID + role) + bonus, capped at levels.max.

STRENGTH (Skyy R5: +4% health / +2% damage per level by default + a DIFFICULTY setting): Easy 3% / 1.5%, Normal 4% / 2% (default),
  Hard 6% / 3%, Custom = strength.hp / strength.dmg. Max health x (1 + hp% x (L - 1)), damage x (1 + dmg% x (L - 1)), capped by
  strength.hpCap (x5) / strength.dmgCap (x3) - caps chosen so no preset is clipped at Lv 60 (Hard Lv 60 = x4.54 health, x2.77 damage).
  Health: ONE StaticModifier(MAX, MULTIPLICATIVE) on Health. The engine sums every MULTIPLICATIVE amount of a stat and multiplies the
  max (after the additive NPC_Max modifier) by that sum (EntityStatValue.computeModifiers bytecode), so there is exactly one modifier.
  Because the engine SUMS multiplicative amounts, another mod's MULTIPLICATIVE Health modifier adds to ours instead of multiplying
  (x1.2 next to a Lv 1 x1.0 = x2.2) - only when mods are combined (review F9, info; MobScanTask warns about known scaling mods).
  SPAWN = full health; LOAD with a changed multiplier = the health share is kept (strength.healOnLoad = full instead).
  Damage: LevelDamage (DamageEventSystem, Filter group, BEFORE DamageSystems$ArmorDamageReduction = before armour, SkyyGear's slot):
  a hit whose source entity is a levelled mob (Damage$EntitySource.getRef; projectiles are a ProjectileSource whose ref is the
  shooter) x the damage multiplier of its level, computed live (a difficulty change applies to damage at once, to health on reload).
  Only the ATTACKER is checked: a levelled mob's hits on players, pets and other mobs are all scaled; players' hits never (review F8).

PERSISTENCE (task: component or UUID map - what this version uses: NEITHER, the engine's own stat save): the level is saved IN THE
  KEY of the health modifier "skyymobs_lv<N>" (one modifier, its amount = the health multiplier). EntityStatMap is an entity component
  with a codec (codecVersion 5, legacyVersioned: "Stats" -> EntityStatValue Id / Value / Modifiers; EntityStatsModule.setup registers
  StaticModifier.ENTITY_CODEC as "Static"), EntityStatsSystems$Setup keeps a loaded map and BalancingInitialisationSystem only re-puts
  NPC_Max, so on LOAD the hook reads its own key back (step 0). HARNESS-VERIFIED with the real codecs: the versioned entity path keeps
  the key, CalculationType MULTIPLICATIVE and the Amount through BSON; ENTITY_CODEC stores no Target (it decodes as MAX, the default,
  which is ours). No new ECS component and no codec code (nothing unknown left in saves after an uninstall - only the modifier, plan
  risk 2). Layer 2: KEPT, a session map uuid -> level filled on UNLOAD (bounded 50,000). Layer 3: the roll is deterministic (world
  seed + UUID + role), so a mob with neither re-rolls the same level while its band is unchanged. MOBS (uuid -> MobInfo, loaded levelled
  mobs only) feeds the damage filter, /mobs and the bridge. A real chunk save + restart is still UNVERIFIED in game (test 9).
  PRUNE (review F6): a removed world's store may never call onEntityRemoved, so MobPruneTask (every 5 min, scheduler thread) forgets the
  MOBS entries whose world is gone (MobInfo.wref = a WEAK World reference, compared by identity with Universe.getWorlds()), and each
  loaded world with levelled mobs drops, on its own world thread, the entries whose entity is gone. Entries younger than 60 s are kept.
UNINSTALL (review F5): the modifier and the plate stay in the save until the mob dies - 0.1 ships no strip command. Before removing the
  jar: Server Setup > Mobs > Never level these = * (no mob gets a level), then restart the server or let the chunks reload - every
  levelled mob loses its modifier + plate the next time it is added (health share kept). Mobs in chunks nobody loads keep them.
  tools/deploy_set.py needs a rollback note for this (main session: the builder may not edit it).

NAMEPLATE "[Lv 9] Trork Warrior" (plate.format) on every levelled mob (plate.mode all / off). Name = server.lang through
  I18nModule.getMessage("en-US", Role.getNameTranslationKey()) (variants point at their base name), else the role id without
  plate.strip endings, underscores -> spaces. COLOURS: UNVERIFIED client feature (plan stage 0) - OFF by default (plate.colorOn);
  plate.markup picks one of the three markups to try: tag = <color=#rrggbb>text</color>, section = the section sign + a legacy colour
  code (nearest of the 16), brace = {#rrggbb}text. Ladder plate.colors (lowest level -> colour; kit colours): 1 row-name white,
  20 warning yellow, 30 gold, 45 error red, 61 Mythic purple (refit 4.4). /mobs platetest shows all three on the mob you look at.

COMMANDS  /mobs and /mobs info (every player, hytale:Adventurer): the band where you stand + region / biome, compared with your class
  weapon skill (class:skill:<uuid> + skill:fn:level when SkyyClasses / SkyySkills run). Admin (requirePermission skyymobs.admin +
  setPermissionGroups(new String[0])): /mobs inspect (the mob you look at, else the nearest levelled mob within 8 blocks: level, how it
  was saved, the lookup step + key + band now, multipliers, plate, attitude, region / biome / env), /mobs set <level> (0 = remove),
  /mobs platetest (3 s per markup, then the plate comes back), /mobs reload (the config kit's reload op).
BRIDGE    mob:fn:level = java.util.function.Function: Object[]{String world, java.util.UUID npc} (or a bare UUID) -> Integer level,
  -1 = no level / unknown / wrong world. Any thread (reads the ConcurrentHashMap MOBS), never throws.
SETTINGS  Server Setup > Mobs (tools/skyycfg.py kit 1.1, node skyymobs.admin): Skyy_SkyyMobs/config.properties (who, strength,
  nameplate) + Skyy_SkyyMobs/bands.properties (biome / env / world / zone tables). Every number is a row.

DECISIONS where the plan left room (all editable rows unless noted):
  - the who-gets-a-level allow list above (the plan's attitude test would level birds, fish, critters and other mods' pets);
    neutral fighters = Boar, Warthog, Scarak_*, Feran warriors; NOT cows / horses / deer / moose / goats (they kick back when
    startled but are animals - Skyy R5), not Kweebecs (plan: Kweebec villages friendly), not Feran civilians / cubs, not Klops.
    QUESTION FOR SKYY (review F2): the neutral line is by name, not behaviour - Boar / Warthog use the same startle-kick setup as Cow /
    Moose, and Mosshorn (bites for 12, fights back only when hit) fits "fight back when hit" literally. Left out by default (the safe
    option: "animals never"): Mosshorn, Mosshorn_Plain, Cow, Horse, Moose_Bull, Moose_Cow, Bison, Ram, Camel, Antelope, Goat, Deer_Stag,
    Horse_Skeleton, Horse_Skeleton_Armored, Kweebec_Razorleaf(_Patrol). Typing any of them into "Extra mobs that get levels" levels them.
  - caps x5 health / x3 damage (no preset clipped at Lv 60).
  - bands.islands and bands.default = 0 (task: island worlds / instances get per-world rows, else no level).
  - shores take the lowest band of their land region (plan 4.1); shallow ocean regions have no rows (Skyy R5: oceans skip).
  - Zone 3 / 4 overlays the plan did not name: lakes, valleys, canyons, calderas, hills, volcanoes, villages and towns pass through to
    the tile biome underneath (the village env Bonus +2 then applies); Zone 3 mountains Mountain_* = the refit's overlay rows 32-34 /
    37-39 / 43-45; Zone 4 mountains use the region rows 45-50 / 53-60.
  - the lava-cave rule applies on every world type; "hardest biome" = the zone's biome row with the highest max (then min), region
    fallback rows (Region.*) left out; the volcanic env rows stay as data (used when bands.volcanicTop is off).
  - env Bonus only on top of a biome band (and the lava band); the env band itself never adds its own bonus.
  - a nameplate set to colours colours the whole plate text; the platetest uses error red #ff6b6b for all three markups.
  - KEEP 10 config history versions (RESUME follow-up direction).
NOT IN 0.1 (later stages): elites, rewards (XP gap rule, bonus drops, gear rarity), mob:fn:band, mob:fn:setLevel, scale.role / boss
  levels, /mobs survey, relevel / strip actions, bands.area, night bonus (Skyy R5: none), mob armour (Skyy R5: none).
REVIEW FIXES (2026-10-02, same version - never deployed): F1 exact built-in role ids + levels.roles = extra mobs (empty) + guard
  patterns in levels.exclude; F3 the worldgen cache keys the exact block column and never keeps a failed lookup or a missing generator;
  F4 no unordered fallback hook (an ERROR + MobLevel.HOOK, shown by /mobs inspect and /mobs info); F5 UNINSTALL note; F6 MobPruneTask;
  F7 isOurs also knows the default format and every format used this run (plate.format runs derive); F11 /mobs platetest claims the
  mob (one test at a time per mob) and puts back the mob's current level plate. F2 = a question for Skyy (above), F8-F10 info (F10:
  blanking levels.roles no longer switches levelling off - it only holds the extras now).
UNVERIFIED (needs the game): the modifier key surviving a real chunk save / restart (the codec round trip is verified); nameplate
  colour markup (the reason colours are off + /mobs platetest); the client drawing a plate on hostile mobs exactly like /entity
  nameplate; I18n key form "server.npcRoles.X.name" (fallback = id); projectile damage carrying the shooter (Damage$ProjectileSource
  ref); marker / beacon spawns' environment = Integer.MIN_VALUE; SkyySkills' getMax() including the multiplier (combat XP); a role
  change (taming) re-adding the mob with the new attitude; painted /setenvironment environments on the island chain; ordering against
  BalancingInitialisationSystem at runtime (a refused registration = no levels that start + one ERROR, no fallback); the prune's
  world-thread pass (Universe.getWorlds() + World.execute, bytecode-probed only).

CHECKED 2026-10-02 after the review fixes (re-run before a deploy - the harness is the source of truth, not this text):
  build: 113 engine members probed (exact descriptors), 29 classes (7 kit), 244 built-in role ids, "assembled ...SkyyMobs-0.1.jar".
  python tools/ci/lint.py: 0 fails for SkyyMobs (repo: 0 fails, 26 warnings, all SkyySacks 0.7.12); lint --perm: 0 fails.
  python tools/skyycfg_test.py: 273 checks + phase 1 (29 refused, 3 built) PASS. tools/skyyui_test.py not re-run (no UI in this mod;
  first build: 10060 ok, 1 known stale fail - base-gated WrapMaxLines, RESUME follow-up).
  python SkyyMobs/test_skyymobs_0.1.py: 9544 ok, 0 fail - A 29 classes -Xverify:all; B the tables = the refit (52 exact + 19 patterns
  expanded + 10 documented additions = 93 biome rows, 81 env rows, 4 zone rows, zone tops 18-20 / 28-30 / 43-45 / 58-60); R 3365
  lookups = a Python mirror + 20 named cases (blue forest 18-20, lava caves, rivers, villages, oceans, islands, world rows, a hand *
  key); C presets; D 1208 multipliers float32-exact (Normal Lv 20 x1.76 / x1.38 ... Lv 60 x3.36 / x2.18, Hard Lv 60 x4.54 / x2.77);
  E 445 vanilla roles = the classification + 26 named cases + review F1 (12 other-mod roles sharing vanilla prefixes, the built-in
  list = the classification, extras + guards), F10, F2 (16 neutral animals left out), F5 (exclude *); X every role of the installed
  mods (read-only scan: 1526 non-vanilla roles in 253 archives) gets no level; G plates (off, 3 markups, ladder, names, F7 old
  formats); F persistence (key, KEPT, 4000 rolls = mirror, a stand-in stat map driving setMult / apply / strip, the real codec); I
  bridge (24,000 threaded calls); W the worldgen cache through a stand-in World (F3); N the prune (F6); T platetest claims (F11); H
  permissions with the engine's own code; K the real config kit (25 rows, set / refuse / confirm, table ops, reload routine, hand
  edit, the extra row, exclude *, plate.format -> derive); S two starts byte-identical; L link check release + 0.7 pre-release: 168
  refs, 0 missing; P ordering + one registerSystem per class, no hook fallback (F4), the prune scheduled (F6), the cache key (F3).
  The same harness run against the pre-fix jar FAILS every review check above (E/X/K F1, W F3, M/P F4, N F6, G/K F7, K F10, T F11).
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
assert tuple(int(x) for x in getattr(CFG, "KIT_VERSION", "1.0").split(".")) >= (1, 1), "SkyyMobs needs config kit 1.1+"
import skyyui as SUI       # chat status colours + the nameplate ladder defaults come from the vanilla UI kit (no pages in 0.1)
SUI.verify(quiet=True)
KIT_ID = SUI.kit_id()

VERSION = "0.1"
MOD = "SkyyMobs"
HERE = os.path.dirname(os.path.abspath(__file__))
NODE = "skyymobs.admin"
KEY_PREFIX = "skyymobs_lv"          # health modifier key = KEY_PREFIX + level (the save slot)

# ================================================================= Assets.zip (read-only): roles, zones, environments
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
AZ = zipfile.ZipFile(AZ_PATH)
AZ_NAMES = AZ.namelist()


def lenient(t):
    t = re.sub(r"//[^\n]*", "", t)
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r",\s*([}\]])", r"\1", t)
    return json.loads(t)


ROLES, ROLE_PATH = {}, {}
for _n in AZ_NAMES:
    if _n.startswith("Server/NPC/Roles/") and _n.endswith(".json"):
        _nm = _n.rsplit("/", 1)[1][:-5]
        ROLES[_nm] = lenient(AZ.read(_n).decode("utf-8-sig", "replace"))
        ROLE_PATH[_nm] = _n[len("Server/NPC/Roles/"):]


def role_params(name, depth=0):
    r = ROLES.get(name)
    if r is None or depth > 12:
        return {}, None
    if r.get("Type") == "Variant":
        base, root = role_params(r.get("Reference"), depth + 1)
        p = dict(base)
        p.update(r.get("Modify") or {})
        return p, root
    p = {}
    for k, v in (r.get("Parameters") or {}).items():
        if isinstance(v, dict) and "Value" in v:
            p[k] = v["Value"]
    return p, name


def role_attitude(name):
    """the attitude the engine gives the role: DefaultPlayerAttitude of its root (Compute = a parameter), HOSTILE when it sets none"""
    p, root = role_params(name)
    rr = ROLES.get(root) if root else None
    a = rr.get("DefaultPlayerAttitude") if rr else None
    if isinstance(a, dict) and "Compute" in a:
        a = p.get(a["Compute"])
    if isinstance(a, dict):
        a = a.get("Value")
    if "DefaultPlayerAttitude" in p and isinstance(p["DefaultPlayerAttitude"], str):
        a = p["DefaultPlayerAttitude"]
    return (a or "Hostile").upper(), root


# a role is a mob that can be levelled (vanilla): not abstract / component, not a test, its root template is not a passive template
PASSIVE_ROOTS = {"Template_Birds_Passive", "Template_Swimming_Passive", "Template_Beasts_Passive_Critter", "Template_Edible_Critter",
                 "Template_Placeholder", "Template_Livestock", "Template_Temple", "Template_Summoned_Ally", "Template_Animal_Neutral"}
NEUTRAL_FIGHTERS = {"Boar", "Warthog", "Feran_Sharptooth", "Feran_Longtooth", "Feran_Burrower", "Feran_Windwalker"}
NEUTRAL_PREFIXES = ("Scarak_", "Dungeon_Scarak_")
BOSSES = ["Goblin_Duke*", "Trork_Chieftain", "Dragon_*", "Skeleton_Elite*"]
VANILLA = []          # every spawnable vanilla role name (the universe the lists are checked against)
FIGHTERS = set()      # hostile fighters + neutral fighters (before the boss exclusion)
ATT = {}
for _nm, _r in ROLES.items():
    if _r.get("Type") in ("Abstract", "Component") or ROLE_PATH[_nm].startswith("_Core/") or _nm == "Empty_Role":
        continue
    VANILLA.append(_nm)
    _a, _root = role_attitude(_nm)
    ATT[_nm] = _a
    if _a == "HOSTILE" and _root not in PASSIVE_ROOTS:
        FIGHTERS.add(_nm)
    if _a == "NEUTRAL" and (_nm in NEUTRAL_FIGHTERS or _nm.startswith(NEUTRAL_PREFIXES)):
        FIGHTERS.add(_nm)
VANILLA.sort()


def glob(p, s):
    return re.fullmatch(re.escape(p.lower()).replace(r"\*", ".*"), s.lower()) is not None


def matches(pats, s):
    return any(glob(p, s) for p in pats)


# Review F1: the built-in list is the EXACT vanilla role ids (no Prefix* patterns): other mods reuse vanilla prefixes for their own
# mounts, pets, NPCs and bosses (Bear_Grizzly_Mount, Wolf_Pet, Spider_Mount, Wraith_Trader, Dungeon_*NPCRole, Dungeon_*_Boss - 193 roles
# in Skyy's Mods folder matched the old patterns). 244 names = ~5 KB, over the kit's 2000-character text row, so they ship as the jar
# constant MobCfg.VANILLA; the row levels.roles is now "Extra mobs that get levels" (other mods' roles), empty by default.
_boss_roles = set(n for n in VANILLA if matches(BOSSES, n))
LEVELLED = sorted(FIGHTERS - _boss_roles)
LEVELLED_TEXT = ",".join(LEVELLED)
_lev_low = set(n.lower() for n in LEVELLED)
ROLES_DEF = ""
# other mods' mounts / pets / NPCs / bosses never get a level, even when an admin adds an extra pattern that matches them (review F1 (b);
# *_Sentry* is left out on purpose: it would remove the vanilla Trork_Sentry / Trork_Sentry_Patrol)
GUARDS = ["*_Mount*", "*_Pet*", "*_Boss*", "*NPC*", "*_Hub*", "*Blacksmith*", "*Trader*"]
EXCLUDE_DEF = ",".join(["Test_*", "Tamed_*", "Temple_*", "*_Merchant*", "Risen_*"] + BOSSES + GUARDS)
_excl = EXCLUDE_DEF.split(",")


def levelled(n, extra=()):
    """the Python mirror of MobCfg.whyNot's list part: built in (exact, any case) or an extra pattern, and not excluded"""
    return (n.lower() in _lev_low or matches(extra, n)) and not matches(_excl, n)


for _n in LEVELLED:
    assert re.fullmatch(r"[A-Za-z0-9_]+", _n), "role id with a separator in it: " + _n
for _n in VANILLA:      # build check: (built in and not exclude) == the role set, for every vanilla role
    assert levelled(_n) == (_n in FIGHTERS and _n not in _boss_roles), "the built-in list / levels.exclude disagree with the classification on " + _n
assert len(EXCLUDE_DEF) <= 2000, "levels.exclude longer than the kit's 2000-character text row"
assert len(LEVELLED_TEXT) < 60000, "the built-in role list must stay one Java string constant"
OLD_PREFIXES = ["Bear_*", "Wolf_*", "Spider*", "Wraith*", "Dungeon_*", "Skeleton*", "Zombie*", "Goblin_*", "Trork_*"]
OTHER_MOD_ROLES = ("Bear_Grizzly_Mount", "Wolf_Pet", "Spider_Mount", "Wraith_Trader", "Dungeon_BlacksmithNPCRole", "Dungeon_Hub_NPC_Role",
                   "Dungeon_ArcaneNPCRole", "Dungeon_Crypt_Boss", "Skeleton_Pet_Knight", "Zombie_Mount", "Goblin_Trader", "Trork_Boss_Warlord",
                   "KazzyPets_Mount_Cow_Undead", "KazzyPets_Mount_Crawler_Void", "KazzyPets_Mount_Bear_Grizzly", "Floating_Pet_Blue",
                   "Spark_Pet_Blue", "Pet_White_Wolf")
for _o in OTHER_MOD_ROLES:
    assert _o not in ROLES, "the other-mod sample %s is a vanilla role" % _o
    assert not levelled(_o), "another mod's mount / pet / NPC / boss would get a level: " + _o
    assert not levelled(_o, OLD_PREFIXES), "the guard patterns miss another mod's mount / pet / NPC / boss under an extra pattern: " + _o
for _yes in ("Skeleton_Fighter", "Skeleton_Fighter_Wander", "Trork_Warrior", "Trork_Sentry", "Boar", "Warthog", "Scarak_Louse",
             "Scarak_Fighter", "Feran_Sharptooth", "Bear_Grizzly", "Spectre_Void", "Golem_Firesteel", "Cactee", "Piranha"):
    assert levelled(_yes), "should get a level: " + _yes
for _no in ("Cow", "Sheep", "Horse", "Deer_Stag", "Bluebird", "Frog_Green", "Mouse", "Kweebec_Razorleaf", "Kweebec_Merchant",
            "Klops_Merchant", "Feran_Civilian", "Feran_Cub", "Tamed_Boar", "Goblin_Duke", "Trork_Chieftain", "Dragon_Fire",
            "Risen_Knight", "Temple_Kweebec", "Snail_Magma", "Shark_Hammerhead", "Mosshorn", "Moose_Bull", "Bison"):
    assert not levelled(_no), "should NOT get a level: " + _no
# review F2 (a question for Skyy, default kept = the safe option): neutral ANIMALS with an attack stay unlevelled (Skyy R5 "animals
# never"; Boar / Warthog are in because Skyy named boars). Listed in the header so Skyy can add them to "Extra mobs that get levels".
NEUTRAL_LEFT_OUT = ["Mosshorn", "Mosshorn_Plain", "Cow", "Horse", "Moose_Bull", "Moose_Cow", "Bison", "Ram", "Camel", "Antelope", "Goat",
                    "Deer_Stag", "Horse_Skeleton", "Horse_Skeleton_Armored", "Kweebec_Razorleaf", "Kweebec_Razorleaf_Patrol"]
for _n in NEUTRAL_LEFT_OUT:
    assert ATT.get(_n) == "NEUTRAL" and not levelled(_n) and levelled(_n, [_n]), "neutral left-out list: " + _n

# zone folders (classic worldgen): region -> biome names (Tile./Custom. prefix and .json stripped = Biome.getName(), bytecode-checked)
REGION_BIOMES = {}
for _n in AZ_NAMES:
    _m = re.match(r"^Server/World/Default/Zones/([^/]+)/(Tile|Custom)\.([^/]+)\.json$", _n)
    if _m:
        REGION_BIOMES.setdefault(_m.group(1), set()).add(_m.group(3))
ENV_IDS = set(_n.rsplit("/", 1)[1][:-5] for _n in AZ_NAMES if _n.startswith("Server/Environments/") and _n.endswith(".json"))
VOLCANIC_ENVS = ["Env_Zone1_Caves_Volcanic_T1", "Env_Zone1_Caves_Volcanic_T2", "Env_Zone1_Caves_Volcanic_T3",
                 "Env_Zone2_Caves_Volcanic_T1", "Env_Zone2_Caves_Volcanic_T2", "Env_Zone2_Caves_Volcanic_T3",
                 "Env_Zone3_Caves_Volcanic_T1", "Env_Zone3_Caves_Volcanic_T2", "Env_Zone3_Caves_Volcanic_T3", "Env_Zone4_Caves_Volcanic"]
for _e in VOLCANIC_ENVS:
    assert _e in ENV_IDS, "volcanic cave environment %s is not in Assets.zip" % _e
assert not [e for e in ENV_IDS if "Volcanic" in e and e not in VOLCANIC_ENVS], "an unlisted volcanic environment exists"

# ================================================================= the default tables (refit section 3 + 4.2; plan 4.5 / 4.6 for Zone 4)
# (key, min, max). Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60.
BIOME_ROWS = [
    # ---- Zone 1 Emerald Wilds 1-20 (refit 3, Zone 1)
    ("Zone1_Spawn.*", 1, 3), ("Zone1_Temple.*", 1, 3),
    ("Zone1_Tier1.Plains_Smooth", 1, 3), ("Zone1_Tier1.Plains_Birch", 3, 5),
    ("Zone1_Tier1.Forest_Birch", 5, 7), ("Zone1_Tier1.Forest_Flower", 5, 7),
    ("Zone1_Tier1.Mountain_Tier1", 5, 7), ("Zone1_Tier1.*_Trork", 5, 7), ("Zone1_Tier1.*", 1, 7),
    ("Zone1_Tier2.Plains_Gorge", 7, 9), ("Zone1_Tier2.Plains_Tallgrass", 9, 11),
    ("Zone1_Tier2.Forest_Aspen", 10, 12), ("Zone1_Tier2.Forest_Gully", 10, 12),
    ("Zone1_Tier2.Mountain_Tier2", 10, 12), ("Zone1_Tier2.*_Trork", 10, 12), ("Zone1_Tier2.*", 7, 12),
    ("Zone1_Tier3.Plains_Gorge", 12, 14), ("Zone1_Tier3.Forest_Swamp", 16, 18),
    ("Zone1_Tier3.Mountain_Tier3", 16, 18), ("Zone1_Tier3.*_Trork", 16, 18),
    ("Zone1_Tier3.Forest_Autumn", 18, 20), ("Zone1_Tier3.Forest_Moss", 18, 20), ("Zone1_Tier3.Forest_Azure", 18, 20),
    ("Zone1_Tier3.*", 12, 20),
    ("Zone1_Shore.*", 1, 3),
    # ---- Zone 2 Howling Sands 20-30
    ("Zone2_Tier1.Savannah_Forest", 20, 22), ("Zone2_Tier1.Savannah_Plains", 20, 22), ("Zone2_Tier1.Savannah_Boab", 20, 22),
    ("Zone2_Tier1.Savannah_Rock", 20, 22), ("Zone2_Tier1.Savannah_Mudflats", 20, 22),
    ("Zone2_Tier1.Plateau_*", 21, 23), ("Zone2_Tier1.Scrub_Bushland", 22, 24), ("Zone2_Tier1.*", 20, 24),
    ("Zone2_Tier2.Desert_Oasis", 25, 27), ("Zone2_Tier2.Desert_Rock", 25, 27), ("Zone2_Tier2.Desert_Springs", 25, 27),
    ("Zone2_Tier2.Desert_Red", 25, 27), ("Zone2_Tier2.*", 25, 27),
    ("Zone2_Tier3.Desert_Barren", 27, 29), ("Zone2_Tier3.Desert_Mushroom", 27, 29),
    ("Zone2_Tier3.Plateau_Desert_*", 28, 30), ("Zone2_Tier3.Desert_Oasis_Hidden*", 28, 30),
    ("Zone2_Tier3.Scrub_Tar_Pits", 28, 30), ("Zone2_Tier3.Desert_Mushroom_Foot", 28, 30), ("Zone2_Tier3.*", 27, 30),
    ("Zone2_Shore.*", 20, 22),
    # ---- Zone 3 Whisperfrost Frontiers 30-45
    ("Zone3_Tier1.Forest_Redwood", 30, 32), ("Zone3_Tier1.Plains_Shire", 30, 32),
    ("Zone3_Tier1.Forest_Fir", 32, 34), ("Zone3_Tier1.Forest_Tundra", 32, 34), ("Zone3_Tier1.Plains_Hotsprings", 32, 34),
    ("Zone3_Tier1.Mountain_*", 32, 34), ("Zone3_Tier1.*", 30, 34),
    ("Zone3_Tier2.Forest_Cedar", 36, 38),
    ("Zone3_Tier2.Plains_Frozen", 37, 39), ("Zone3_Tier2.Forest_Cedar_Mixed", 37, 39), ("Zone3_Tier2.Plains_Tundra", 37, 39),
    ("Zone3_Tier2.Mountain_*", 37, 39), ("Zone3_Tier2.*", 36, 39),
    ("Zone3_Tier3.Forest_Frozen", 41, 43), ("Zone3_Tier3.Forest_Frozen_Light", 41, 43), ("Zone3_Tier3.Plains_Frozen_Frost", 41, 43),
    ("Zone3_Tier3.Mountain_*", 43, 45), ("Zone3_Tier3.*", 41, 45),
    ("Zone3_Shore_Tier1.*", 30, 32), ("Zone3_Shore_Tier2.*", 36, 38), ("Zone3_Shore_Tier3.*", 41, 43),
    # ---- Zone 4 Devastated Lands 45-60 (plan 4.5, unchanged by the refit)
    ("Zone4_Tier4.Wastes_Grasslands", 45, 47), ("Zone4_Tier4.Wastes_Geysers", 48, 50), ("Zone4_Tier4.Forest_Ghost", 48, 50),
    ("Zone4_Tier4.Desert_Dunes", 48, 50), ("Zone4_Tier4.Forest_Swamp", 48, 50), ("Zone4_Tier4.*", 45, 50),
    ("Zone4_Tier5.Desert_Ash", 53, 55), ("Zone4_Tier5.Wastes_Ash", 53, 55), ("Zone4_Tier5.Wastes_Lava", 55, 57),
    ("Zone4_Tier5.Forest_Burned", 58, 60), ("Zone4_Tier5.Forest_Roots", 58, 60), ("Zone4_Tier5.*", 53, 60),
    ("Zone4_Shore_Tier4.*", 45, 47), ("Zone4_Shore_Tier5.*", 53, 55),
]
# (key, min, max, bonus): refit 4.2 for Zones 1-3, plan 4.6 for Zone 4 and the 0.7 portal shards (unchanged)
ENV_ROWS = [
    ("Env_Zone1_Plains", 1, 3, 0), ("Env_Zone1_Shores", 1, 3, 0), ("Env_Zone1_Kweebec", 1, 3, 0),
    ("Env_Zone1_Forests", 5, 9, 0), ("Env_Zone1_Mountains", 5, 14, 0), ("Env_Zone1_Trork", 5, 16, 0),
    ("Env_Zone1_Swamps", 14, 20, 0), ("Env_Zone1_Autumn", 16, 20, 0), ("Env_Zone1_Azure", 16, 20, 0),
    ("Env_Zone1_Caves*", 5, 14, 0),
    ("Env_Zone1_Caves_Volcanic_T1", 5, 9, 0), ("Env_Zone1_Caves_Volcanic_T2", 9, 14, 0), ("Env_Zone1_Caves_Volcanic_T3", 14, 18, 0),
    ("Env_Zone1_Caves_Goblins", 5, 16, 1), ("Env_Zone1_Mineshafts", 5, 16, 1),
    ("Env_Zone1_Encounters", 9, 18, 2), ("Env_Zone1_Graveyard", 9, 18, 2), ("Env_Zone1_Mage_Towers", 9, 18, 2),
    ("Env_Zone1_Dungeons", 14, 20, 2),
    ("Env_Zone2_Savanna", 20, 22, 0), ("Env_Zone2_Shores", 20, 22, 0), ("Env_Zone2_Scrub", 22, 24, 0),
    ("Env_Zone2_Plateaus", 21, 27, 0), ("Env_Zone2_Deserts", 25, 29, 0), ("Env_Zone2_Oasis", 25, 30, 0),
    ("Env_Zone2_Feran", 23, 28, 1), ("Env_Zone2_Scarak", 23, 28, 1),
    ("Env_Zone2_Caves*", 21, 27, 0),
    ("Env_Zone2_Caves_Volcanic_T1", 21, 23, 0), ("Env_Zone2_Caves_Volcanic_T2", 25, 27, 0), ("Env_Zone2_Caves_Volcanic_T3", 28, 30, 0),
    ("Env_Zone2_Mineshafts", 23, 27, 1), ("Env_Zone2_Caves_Goblins", 23, 27, 1),
    ("Env_Zone2_Encounters", 25, 29, 2), ("Env_Zone2_Mage_Towers", 25, 29, 2), ("Env_Zone2_Dungeons", 27, 30, 2),
    ("Env_Zone3_Tundra", 30, 35, 0), ("Env_Zone3_Shores", 30, 33, 0), ("Env_Zone3_Forests", 30, 38, 0),
    ("Env_Zone3_Mountains", 35, 41, 0), ("Env_Zone3_Glacial", 38, 45, 0), ("Env_Zone3_Caves*", 32, 41, 0),
    ("Env_Zone3_Trork", 35, 42, 1), ("Env_Zone3_Outlander*", 39, 45, 2), ("Env_Zone3_Encounters", 39, 45, 2),
    ("Env_Zone4_Wastes", 45, 50, 0), ("Env_Zone4_Shores", 45, 47, 0), ("Env_Zone4_Crucible", 48, 50, 0),
    ("Env_Zone4_Volcanoes", 48, 57, 0), ("Env_Zone4_Forests", 48, 60, 0), ("Env_Zone4_Jungles", 50, 58, 0),
    ("Env_Zone4_Encounters*", 53, 60, 2), ("Env_Zone4_Villages*", 55, 60, 2),
    ("Env_Portal_Goblin_Surface", 5, 8, 0), ("Env_Portal_Goblin_Cave", 7, 10, 0), ("Env_Portal_Goblin_Cave_Deep", 9, 11, 0),
    ("Env_Portal_Goblin_Cave_Void", 10, 12, 0),
]
ZONE_ROWS = [("Zone1", 1, 7), ("Zone2", 20, 24), ("Zone3", 30, 34), ("Zone4", 45, 50)]
# The config kit refuses * in a table entry (CfgRows.entryErr: only entry=itemprefix tables take a trailing *), so the shipped tables
# hold NO pattern keys - every number stays editable in Server Setup: "Region.*" becomes the plain region key "Region" (its fallback
# row) and every other pattern is expanded HERE into one explicit row per matching biome / environment of Assets.zip (exact rows win).
# The runtime still understands * keys (MobBands.find) for hand-edited files.
BIOME_PATTERNS = list(BIOME_ROWS)
ENV_PATTERNS = list(ENV_ROWS)
ZONE_TOPS = {1: 20, 2: 30, 3: 45, 4: 60}
ZONE_FLOORS = {1: 1, 2: 20, 3: 30, 4: 45}
PASS_DEF = "River_*,Lake*,Dunes_*,*_Mudflats,*_Kweebec,Valley_*,Canyon_*,Caldera_*,Hills_*,Volcano_*,Village_*,*_Village,*_Town,Town_*"
COLOR_ROWS = [("1", SUI.COLOR["rowName"]), ("20", SUI.COLOR["warning"]), ("30", SUI.COLOR["gold"]), ("45", SUI.COLOR["error"]),
              ("61", SUI.RARITY["Mythic"])]
TEST_RED = SUI.COLOR["error"]
STRIP_DEF = "_Wander,_Patrol,_Surge,_Static,_Sleep"
FORMAT_DEF = "[Lv {level}] {name}"

# build checks on the pattern tables: every key names a real region / biome / environment of Assets.zip
for _k, _a, _b in BIOME_PATTERNS:
    _reg, _, _bio = _k.partition(".")
    assert _reg in REGION_BIOMES, "biome row %s: no region folder %s" % (_k, _reg)
    assert 0 < _a <= _b, _k
    if "*" in _bio:
        assert _bio == "*" or any(glob(_bio, x) for x in REGION_BIOMES[_reg]), "biome row %s matches no biome of %s" % (_k, _reg)
    else:
        assert _bio in REGION_BIOMES[_reg], "biome row %s: %s has no biome %s" % (_k, _reg, _bio)
    _z = int(_k[4])
    assert ZONE_FLOORS[_z] <= _a and _b <= ZONE_TOPS[_z], "biome row %s outside the Zone %d band" % (_k, _z)


def expand_biomes(rows):
    exact = set(k for k, _a, _b in rows if "*" not in k)
    out = []
    for k, a, b in rows:
        reg, _, bio = k.partition(".")
        if bio == "*":
            out.append((reg, a, b))
        elif "*" in bio:
            for x in sorted(REGION_BIOMES[reg]):
                if glob(bio, x) and "%s.%s" % (reg, x) not in exact:
                    out.append(("%s.%s" % (reg, x), a, b))
        else:
            out.append((k, a, b))
    return out


def expand_envs(rows):
    exact = set(k for k, _a, _b, _c in rows if "*" not in k)
    out = []
    for k, a, b, c in rows:
        if "*" in k:
            for e in sorted(ENV_IDS):
                if glob(k, e) and e not in exact:
                    out.append((e, a, b, c))
        else:
            out.append((k, a, b, c))
    return out


BIOME_ROWS = expand_biomes(BIOME_PATTERNS)
for _z in ZONE_TOPS:
    _rows = [r for r in BIOME_ROWS if r[0].startswith("Zone%d_" % _z)]
    assert min(r[1] for r in _rows) == ZONE_FLOORS[_z] and max(r[2] for r in _rows) == ZONE_TOPS[_z], "Zone %d band" % _z
assert len(set(r[0].lower() for r in BIOME_ROWS)) == len(BIOME_ROWS)
for _k, _a, _b, _c in ENV_PATTERNS:
    assert 0 < _a <= _b and 0 <= _c <= 10, _k
    if _k.startswith("Env_Portal_"):
        continue        # the 0.7 pre-release goblin shard environments (plan 4.6): not in the release Assets.zip
    if "*" in _k:
        assert any(glob(_k, e) for e in ENV_IDS), "env row %s matches no environment" % _k
    else:
        assert _k in ENV_IDS, "env row %s: no such environment" % _k
ENV_ROWS = expand_envs(ENV_PATTERNS)
assert len(set(r[0].lower() for r in ENV_ROWS)) == len(ENV_ROWS)
assert not [r for r in BIOME_ROWS + ENV_ROWS if "*" in r[0]], "a * key left in the shipped tables"


def _band_lines():
    L = ["# SkyyMobs %s level bands. In game: SkyWynn Menu > Server Setup > Mobs > Level bands; /mobs reload re-reads this file." % VERSION,
         "# Every line: <table>.<key>=<lowest level>,<highest level> (environment lines add a third number: the bonus).",
         "# A mob rolls a random level inside its band when it spawns. A band change only reaches new spawns (mobs keep their level).",
         "# Lookup (first match wins): world > private island > lava cave > biome > environment > zone > default (config.properties).",
         "# Biome keys: <Region>.<Biome> for one biome, or <Region> alone for every other biome of that region (its fallback).",
         "",
         "# ---- biome.<Region>.<Biome> / biome.<Region>: classic Hytale worlds (the worldgen zone folder + its tile or overlay biome) ----"]
    zname = {1: "Zone 1 Emerald Wilds: Lv 1-20 (the blue forest Forest_Azure, Autumn and Moss at the top)",
             2: "Zone 2 Howling Sands: Lv 20-30", 3: "Zone 3 Whisperfrost Frontiers: Lv 30-45", 4: "Zone 4 Devastated Lands: Lv 45-60"}
    last = None
    for k, a, b in BIOME_ROWS:
        z = int(k[4])
        if z != last:
            L.append("# " + zname[z])
            last = z
        L.append("biome.%s=%d,%d" % (k, a, b))
    L += ["", "# ---- env.<Environment>=<min>,<max>,<bonus>: the band where no biome is known (islands, World Gen 2); the bonus is added",
          "# on top of a biome band (encounters, dungeons, camps). Lava caves (Env_ZoneN_Caves_Volcanic*) use the zone's hardest biome. ----"]
    for k, a, b, c in ENV_ROWS:
        L.append("env.%s=%d,%d,%d" % (k, a, b, c))
    L += ["", "# ---- zone.<ZoneN>: fallback when only the zone is known (region ZoneN_..., environment Env_ZoneN_...) ----"]
    for k, a, b in ZONE_ROWS:
        L.append("zone.%s=%d,%d" % (k, a, b))
    L += ["", "# ---- world.<world name or its start>=<min>,<max>: one band for a whole world (dungeon_ = every world named dungeon_...;",
          "# 0,0 = no levels there). None by default. ----"]
    return L


BANDS_TEXT = "\n".join(_band_lines()) + "\n"
CFG_LINES = [
    "# SkyyMobs %s settings (mob levels). In game: SkyWynn Menu > Server Setup > Mobs; /mobs reload re-reads this file." % VERSION,
    "# The level bands are in bands.properties next to this file.",
    "# Mob levels (false = new mobs get no level; mobs that have one keep it).",
    "part.levels=true",
    "# Neutral mobs that fight back when hit (boars, Scaraks, Feran warriors) get levels too.",
    "levels.neutral=true",
    "# Extra mobs that get levels (other mods' mobs): role ids or Prefix* patterns, comma separated. Vanilla hostile mobs and the",
    "# neutral fighters (boars, warthogs, Scaraks, Feran warriors) are built in; vanilla animals only get a level when listed here.",
    "levels.roles=" + ROLES_DEF,
    "# Never level these, even when built in or listed above: tests, tamed animals, temple NPCs, traders, summons, bosses and",
    "# other mods' mounts / pets / NPCs. * = no mob gets a level: every levelled mob loses its level + plate the next time it loads.",
    "levels.exclude=" + EXCLUDE_DEF,
    "# Highest mob level (band + bonus never goes above this).",
    "levels.max=100",
    "# Difficulty: easy (3% health / 1.5% damage per level), normal (4% / 2%), hard (6% / 3%) or custom (the two values below).",
    "strength.difficulty=normal",
    "# Custom difficulty only: health and damage added per level above 1, in percent.",
    "strength.hp=4",
    "strength.dmg=2",
    "# Highest health and damage multipliers.",
    "strength.hpCap=5",
    "strength.dmgCap=3",
    "# Heal a mob to full when its chunk reloads (false = a wounded mob keeps its health share).",
    "strength.healOnLoad=false",
    "# Overlay biomes that use the land biome underneath them (rivers, lakes, dunes, valleys, villages ...).",
    "bands.passThrough=" + PASS_DEF,
    "# Vanilla's deep lava caves (Env_ZoneN_Caves_Volcanic*) use the band of the zone's hardest biome.",
    "bands.volcanicTop=true",
    "# SkyyIslands private islands: a level range like 1-3, or 0 for no levels.",
    "bands.islands=0",
    "# Level range when nothing matches (0 = no level).",
    "bands.default=0",
    "# Nameplates: all (every levelled mob) or off.",
    "plate.mode=all",
    "# Nameplate text: {level} = the level, {name} = the mob's name.",
    "plate.format=" + FORMAT_DEF,
    "# Role id endings dropped when a mob has no translated name.",
    "plate.strip=" + STRIP_DEF,
    "# TRIAL (the client may not draw colours): colour the nameplate by level. Run /mobs platetest first and pick the markup that works.",
    "plate.colorOn=false",
    "# Colour markup: tag (<color=#rrggbb>), section (section sign colour codes) or brace ({#rrggbb}).",
    "plate.markup=tag",
    "# Level colours: plate.colors.<lowest level of the band>=#rrggbb",
] + ["plate.colors.%s=%s" % (k, v) for k, v in COLOR_ROWS]
CFG_TEXT = "\n".join(CFG_LINES) + "\n"
for _t in (CFG_TEXT, BANDS_TEXT):
    assert all(ord(c) < 127 for c in _t), "default files must be plain ASCII"

# ================================================================= JVM + engine classes (every member probed: a missing one fails the build)
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.mobs"
T = {
    "PKG": PKG, "VERSION": VERSION,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "HOLD": "com.hypixel.hytale.component.Holder",
    "CTYPE": "com.hypixel.hytale.component.ComponentType",
    "COMP": "com.hypixel.hytale.component.Component",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "WCFG": "com.hypixel.hytale.server.core.universe.world.WorldConfig",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BCH": "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "ENVA": "com.hypixel.hytale.server.core.asset.type.environment.config.Environment",
    "ILT": "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap",
    "CGEN": "com.hypixel.hytale.server.worldgen.chunk.ChunkGenerator",
    "ZBR": "com.hypixel.hytale.server.worldgen.chunk.ZoneBiomeResult",
    "ZGR": "com.hypixel.hytale.server.worldgen.zone.ZoneGeneratorResult",
    "ZONE": "com.hypixel.hytale.server.worldgen.zone.Zone",
    "ZDC": "com.hypixel.hytale.server.worldgen.zone.ZoneDiscoveryConfig",
    "BIOME": "com.hypixel.hytale.server.worldgen.biome.Biome",
    "BPG": "com.hypixel.hytale.server.worldgen.biome.BiomePatternGenerator",
    "NPCE": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ROLE": "com.hypixel.hytale.server.npc.role.Role",
    "WSUP": "com.hypixel.hytale.server.npc.role.support.WorldSupport",
    "ATT": "com.hypixel.hytale.server.core.asset.type.attitude.Attitude",
    "NPL": "com.hypixel.hytale.server.core.entity.nameplate.Nameplate",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "SMO": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier",
    "MODF": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier",
    "MTG": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget",
    "CAL": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "UUIDC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "VEC": "org.joml.Vector3d",
    "HSYS": "com.hypixel.hytale.component.system.HolderSystem",
    "ADDR": "com.hypixel.hytale.component.AddReason",
    "REMR": "com.hypixel.hytale.component.RemoveReason",
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD": "com.hypixel.hytale.component.dependency.Order",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "SG": "com.hypixel.hytale.component.SystemGroup",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "INTL": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
    "TGT": "com.hypixel.hytale.server.core.util.TargetUtil",
    "PMGR": "com.hypixel.hytale.server.core.plugin.PluginManager",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "UNIV": "com.hypixel.hytale.server.core.universe.Universe",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    # every player command: its auto permission node goes to the default player group (vanilla /help /who pattern)
    "ADV": 'setPermissionGroups(new String[] { "hytale:Adventurer" });',
    # admin sub-commands under a player command: own node AND no groups (lint perm_group_leaks; SkyyIslands 0.5 lesson)
    "ADMIN": 'requirePermission("%s"); setPermissionGroups(new String[0]);' % NODE,
    "KEYP": KEY_PREFIX,
    "KITID": KIT_ID,
}
AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
CRP = "com.hypixel.hytale.component.ComponentRegistryProxy"
ROLEB = "com.hypixel.hytale.server.npc.systems.RoleBuilderSystem"
SETUPS = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Setup"
BALS = "com.hypixel.hytale.server.npc.systems.BalancingInitialisationSystem"
ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"


def jdesc(t):
    if t.endswith("[]"):
        return "[" + jdesc(t[:-2])
    prim = {"int": "I", "long": "J", "float": "F", "double": "D", "boolean": "Z", "void": "V", "char": "C", "byte": "B", "short": "S"}
    return prim[t] if t in prim else "L" + t.replace(".", "/") + ";"


def probe_sig(cls, name, ret, args):
    """the exact member: cls.name(args) -> ret (own or inherited); a missing one stops the build (UNVERIFIED engine members)"""
    desc = "(" + "".join(jdesc(a) for a in args) + ")" + jdesc(ret)
    c = pool.get(cls)
    try:
        if name == "<init>":
            c.getConstructor(desc)
        else:
            c.getMethod(name, desc)
    except Exception:
        raise SystemExit("API probe failed: %s.%s%s not found" % (cls, name, desc))
    PROBED.append("%s.%s%s" % (cls.rsplit(".", 1)[1], name, desc))


PROBED = []
G = T
SIGS = [
    # spawn point / spawn environment / role (plan section 12)
    (G["NPCE"], "getComponentType", G["CTYPE"], []), (G["NPCE"], "getEnvironment", "int", []),
    (G["NPCE"], "getLeashPoint", G["VEC"], []), (G["NPCE"], "getRoleName", "java.lang.String", []),
    (G["NPCE"], "getRole", G["ROLE"], []), (G["ROLE"], "getNameTranslationKey", "java.lang.String", []),
    (G["WSUP"], "getComponentType", G["CTYPE"], []), (G["WSUP"], "getDefaultPlayerAttitude", G["ATT"], []),
    # nameplate
    (G["NPL"], "getComponentType", G["CTYPE"], []), (G["NPL"], "setText", "void", ["java.lang.String"]),
    (G["NPL"], "getText", "java.lang.String", []),
    # health modifier (the save slot)
    (G["ESM"], "getComponentType", G["CTYPE"], []), (G["ESM"], "get", G["ESV"], ["int"]),
    (G["ESM"], "putModifier", G["MODF"], ["int", "java.lang.String", G["MODF"]]),
    (G["ESM"], "getModifier", G["MODF"], ["int", "java.lang.String"]),
    (G["ESM"], "removeModifier", G["MODF"], ["int", "java.lang.String"]),
    (G["ESM"], "maximizeStatValue", "float", ["int"]), (G["ESM"], "setStatValue", "float", ["int", "float"]),
    (G["ESV"], "get", "float", []), (G["ESV"], "getMax", "float", []), (G["ESV"], "getModifiers", "java.util.Map", []),
    (G["SMO"], "<init>", "void", [G["MTG"], G["CAL"], "float"]), (G["SMO"], "getAmount", "float", []),
    (G["DST"], "getHealth", "int", []),
    # classic worldgen lookup (NPCMemory$GatherMemoriesSystem.findLocationZoneName recipe, seed = (int) WorldConfig.getSeed())
    (G["CHS"], "getGenerator", "com.hypixel.hytale.server.core.universe.world.worldgen.IWorldGen", []),
    (G["CHS"], "getChunkComponent", G["COMP"], ["long", G["CTYPE"]]),
    (G["CGEN"], "getZoneBiomeResultAt", G["ZBR"], ["int", "int", "int"]),
    (G["ZBR"], "getBiome", G["BIOME"], []), (G["ZBR"], "getZoneResult", G["ZGR"], []), (G["ZGR"], "getZone", G["ZONE"], []),
    (G["ZONE"], "name", "java.lang.String", []), (G["ZONE"], "biomePatternGenerator", G["BPG"], []),
    (G["ZONE"], "discoveryConfig", G["ZDC"], []), (G["ZDC"], "zone", "java.lang.String", []),
    (G["BPG"], "getBiome", "com.hypixel.hytale.server.worldgen.biome.TileBiome", ["int", "int", "int"]),
    (G["BIOME"], "getName", "java.lang.String", []),
    # block environment (3D: BlockChunk.getEnvironment(int, int, int) - the Vector3d form is gone in 0.7)
    (G["BCH"], "getComponentType", G["CTYPE"], []), (G["BCH"], "getEnvironment", "int", ["int", "int", "int"]),
    (G["CHU"], "indexChunkFromBlock", "long", ["int", "int"]),
    (G["ENVA"], "getAssetMap", G["ILT"], []), (G["ENVA"], "getId", "java.lang.String", []),
    (G["ILT"], "getAsset", "com.hypixel.hytale.assetstore.map.JsonAssetWithMap", ["int"]),
    (G["WLD"], "getName", "java.lang.String", []), (G["WLD"], "getChunkStore", G["CHS"], []),
    (G["WLD"], "getWorldConfig", G["WCFG"], []), (G["WLD"], "getEntityStore", G["EST"], []),
    (G["WLD"], "execute", "void", ["java.lang.Runnable"]), (G["WCFG"], "getSeed", "long", []),
    (G["UNIV"], "get", G["UNIV"], []), (G["UNIV"], "getWorlds", "java.util.Map", []),     # the prune of removed worlds (review F6)
    (G["EST"], "getWorld", G["WLD"], []), (G["EST"], "getRefFromUUID", G["REF"], ["java.util.UUID"]), (G["EST"], "getStore", G["ST"], []),
    (G["ST"], "getExternalData", "java.lang.Object", []), (G["ST"], "getComponent", G["COMP"], [G["REF"], G["CTYPE"]]),
    (G["ST"], "ensureAndGetComponent", G["COMP"], [G["REF"], G["CTYPE"]]), (G["ST"], "tryRemoveComponent", "void", [G["REF"], G["CTYPE"]]),
    (G["HOLD"], "getComponent", G["COMP"], [G["CTYPE"]]), (G["HOLD"], "ensureAndGetComponent", G["COMP"], [G["CTYPE"]]),
    (G["HOLD"], "tryRemoveComponent", "boolean", [G["CTYPE"]]),
    (G["UUIDC"], "getComponentType", G["CTYPE"], []), (G["UUIDC"], "getUuid", "java.util.UUID", []),
    (G["TC"], "getComponentType", G["CTYPE"], []), (G["TC"], "getPosition", G["VEC"], []),
    (G["REF"], "isValid", "boolean", []),
    # the systems
    (G["HSYS"], "onEntityAdd", "void", [G["HOLD"], G["ADDR"], G["ST"]]),
    (G["HSYS"], "onEntityRemoved", "void", [G["HOLD"], G["REMR"], G["ST"]]),
    (G["SDEP"], "<init>", "void", [G["ORD"], "java.lang.Class"]),
    (G["QRY"], "and", "com.hypixel.hytale.component.query.AndQuery", [G["QRY"] + "[]"]),
    (G["QRY"], "any", "com.hypixel.hytale.component.query.AnyQuery", []),
    (G["DMOD"], "get", G["DMOD"], []), (G["DMOD"], "getFilterDamageGroup", G["SG"], []),
    (G["DMG"], "getAmount", "float", []), (G["DMG"], "setAmount", "void", ["float"]), (G["DMG"], "getSource", G["DSRC"], []),
    (G["DMG"], "isCancelled", "boolean", []), (G["DENT"], "getRef", G["REF"], []),
    (G["CB"], "getComponent", G["COMP"], [G["REF"], G["CTYPE"]]),
    (CRP, "registerSystem", "void", ["com.hypixel.hytale.component.system.ISystem"]),
    (PB, "getEntityStoreRegistry", CRP, []), (PB, "getCommandRegistry", "com.hypixel.hytale.server.core.command.system.CommandRegistry", []),
    (PB, "getDataDirectory", "java.nio.file.Path", []), (PB, "getLogger", G["LOG"], []), (PB, "shutdown", "void", []),
    # names, commands, look target, plugins
    (G["INTL"], "get", G["INTL"], []), (G["INTL"], "getMessage", "java.lang.String", ["java.lang.String", "java.lang.String"]),
    (G["TGT"], "getTargetEntity", G["REF"], [G["REF"], "com.hypixel.hytale.component.ComponentAccessor"]),
    (G["PMGR"], "get", G["PMGR"], []), (G["PMGR"], "getPlugins", "java.util.List", []),
    (AC, "setPermissionGroups", "void", ["java.lang.String[]"]), (AC, "requirePermission", "void", ["java.lang.String"]),
    (AC, "addSubCommand", "void", [AC]),
    (G["CTX"], "get", "java.lang.Object", ["com.hypixel.hytale.server.core.command.system.arguments.system.Argument"]),
    (G["PR"], "getUuid", "java.util.UUID", []), (G["PR"], "getUsername", "java.lang.String", []),
    (G["PR"], "sendMessage", "void", [G["MSG"]]), (G["MSG"], "raw", G["MSG"], ["java.lang.String"]),
    (G["MSG"], "color", G["MSG"], ["java.lang.String"]),
]
for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)
for _c, _m in ((G["MTG"], "MAX"), (G["CAL"], "MULTIPLICATIVE"), (G["ADDR"], "SPAWN"), (G["REMR"], "UNLOAD"), (G["REMR"], "REMOVE"),
               (G["ORD"], "AFTER"), (G["ORD"], "BEFORE"), (G["ATT"], "HOSTILE"), (G["ATT"], "NEUTRAL"), (G["VEC"], "x"),
               (G["VEC"], "y"), (G["VEC"], "z"), (G["HSV"], "SCHEDULED_EXECUTOR"), (G["ATY"], "STRING"), (AC, "withRequiredArg")):
    B.probe(pool, _c, _m)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _m))
for _c in (ROLEB, SETUPS, BALS, ADRS):
    pool.get(_c)          # the classes our systems order against (looked up again at runtime with Class.forName)
print("engine members probed: %d" % len(PROBED))

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def jstr(s):
    assert all(32 <= ord(c) < 127 for c in s), repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jtext(s):
    """a multi-line Java string literal (\\n escapes) of a plain ASCII text"""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


# ================================================================= classes (all top-level; methods before callers)
lg = pool.makeClass(PKG + ".MobLog")
gb = pool.makeClass(PKG + ".MobGlob")
bd = pool.makeClass(PKG + ".MobBands")
mi = pool.makeClass(PKG + ".MobInfo")
cfg = pool.makeClass(PKG + ".MobCfg")
lv = pool.makeClass(PKG + ".MobLevel")
hk = pool.makeClass(PKG + ".LevelHook", pool.get(G["HSYS"]))
dm = pool.makeClass(PKG + ".LevelDamage", pool.get(G["DES"]))
dmu = pool.makeClass(PKG + ".LevelDamageU", dm)
fn = pool.makeClass(PKG + ".MobLevelFn")
ps = pool.makeClass(PKG + ".MobPlateStep")
sc = pool.makeClass(PKG + ".MobScanTask")
pt = pool.makeClass(PKG + ".MobPruneTask")
mh = pool.makeClass(PKG + ".MobHooks")
mc = pool.makeClass(PKG + ".MobCmds")
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, mh, mc]

# ---------------------------------------------------------------- MobLog: the server log (every class may call it)
F(lg, "public static @LOG@ LOG;")
F(lg, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(lg, r"""
public static void info(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyMobs] " + msg);
    else System.out.println("[SkyyMobs] " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void warn(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyMobs] " + msg);
    else System.out.println("[SkyyMobs] WARN " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void error(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.SEVERE).log("[SkyyMobs] " + msg);
    else System.out.println("[SkyyMobs] ERROR " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void warnOnce(String key, String msg) {
  if (key == null || ONCE.putIfAbsent(key, Boolean.TRUE) != null) return;
  warn(msg);
}""")

# ---------------------------------------------------------------- MobGlob: * patterns (lower case), comma lists
M(gb, r"""
public static boolean glob(String p, String s) {
  if (p == null || s == null) return false;
  int pi = 0, si = 0, star = -1, mark = 0;
  int pn = p.length(), sn = s.length();
  while (si < sn) {
    if (pi < pn && p.charAt(pi) != '*' && p.charAt(pi) == s.charAt(si)) { pi++; si++; }
    else if (pi < pn && p.charAt(pi) == '*') { star = pi; mark = si; pi++; }
    else if (star >= 0) { pi = star + 1; mark++; si = mark; }
    else return false;
  }
  while (pi < pn && p.charAt(pi) == '*') pi++;
  return pi == pn;
}""")
M(gb, r"""
public static int spec(String p) {
  int n = 0;
  for (int i = 0; p != null && i < p.length(); i++) if (p.charAt(i) != '*') n++;
  return n;
}""")
M(gb, r"""
public static String[] list(String csv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (csv != null) {
    String[] parts = csv.split(",");
    for (int i = 0; i < parts.length; i++) {
      String t = parts[i].trim().toLowerCase();
      if (t.length() > 0 && !out.contains(t)) out.add(t);
    }
  }
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")
M(gb, r"""
public static boolean any(String[] pats, String s) {
  if (pats == null || s == null) return false;
  String k = s.toLowerCase();
  for (int i = 0; i < pats.length; i++) if (glob(pats[i], k)) return true;
  return false;
}""")

# ---------------------------------------------------------------- MobBands: one band table (keys sorted, most specific match wins)
for f in ("public String name;", "public String[] raw;", "public String[] low;", "public int[] a;", "public int[] b;", "public int[] c;",
          "public int[] spec;", "public boolean[] wild;", "public java.util.HashMap exact;", "public int n;"):
    F(bd, f)
C(bd, r"""
public MobBands(String name, String[] raw, int[] a, int[] b, int[] c) {
  this.name = name;
  this.raw = raw; this.a = a; this.b = b; this.c = c;
  this.n = raw.length;
  this.low = new String[this.n];
  this.spec = new int[this.n];
  this.wild = new boolean[this.n];
  this.exact = new java.util.HashMap();
  for (int i = 0; i < this.n; i++) {
    this.low[i] = raw[i].toLowerCase();
    this.spec[i] = @PKG@.MobGlob.spec(this.low[i]);
    this.wild[i] = this.low[i].indexOf('*') >= 0;
    if (!this.wild[i] && !this.exact.containsKey(this.low[i])) this.exact.put(this.low[i], Integer.valueOf(i));
  }
}""")
M(bd, r"""
public int find(String key) {
  if (key == null || this.n == 0) return -1;
  String k = key.toLowerCase();
  Object o = this.exact.get(k);
  if (o instanceof Integer) return ((Integer) o).intValue();
  int best = -1, bs = -1;
  for (int i = 0; i < this.n; i++) {
    if (!this.wild[i] || this.spec[i] <= bs) continue;
    if (@PKG@.MobGlob.glob(this.low[i], k)) { best = i; bs = this.spec[i]; }
  }
  return best;
}""")

# world rows: the exact name, else the longest key the name starts with (or a * pattern from a hand edit)
M(bd, r"""
public int findPrefix(String key) {
  int i = find(key);
  if (i >= 0 || key == null) return i;
  String k = key.toLowerCase();
  int best = -1, bl = 0;
  for (int j = 0; j < this.n; j++) {
    if (this.wild[j]) continue;
    if (this.low[j].length() > bl && k.startsWith(this.low[j])) { best = j; bl = this.low[j].length(); }
  }
  return best;
}""")

# ---------------------------------------------------------------- MobInfo: one loaded levelled mob
# wref = a WEAK reference to the World the mob lives in (the prune forgets mobs of removed worlds - review F6 - and never keeps a
# removed World alive)
for f in ("public String world;", "public java.util.UUID uuid;", "public String role;", "public String name;", "public int level;",
          "public String step;", "public String key;", "public int a;", "public int b;", "public int bonus;", "public long at;",
          "public java.lang.ref.WeakReference wref;"):
    F(mi, f)
C(mi, "public MobInfo() { }")

# MobLevel's maps first (MobCfg.derive clears the name cache)
F(lv, "public static final java.util.concurrent.ConcurrentHashMap MOBS = new java.util.concurrent.ConcurrentHashMap();")
F(lv, "public static final java.util.concurrent.ConcurrentHashMap KEPT = new java.util.concurrent.ConcurrentHashMap();")
F(lv, "public static final java.util.concurrent.ConcurrentHashMap WG = new java.util.concurrent.ConcurrentHashMap();")
F(lv, "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();")
F(lv, 'public static final String KEY_PREFIX = "@KEYP@";')
F(lv, "public static final int KEPT_MAX = 50000;")
F(lv, "public static final int WG_MAX = 10000;")
# true once the level hook is registered (review F4: no unordered fallback - without the hook no mob gets a level this run)
F(lv, "public static volatile boolean HOOK = false;")
# the prune (review F6): a mob added less than PRUNE_GRACE ms ago is never pruned (a world that is still being added to the universe)
F(lv, "public static final long PRUNE_GRACE = 60000L;")
F(lv, "public static volatile java.util.concurrent.ScheduledFuture PRUNE;")

# ---------------------------------------------------------------- MobCfg: fields first (the config kit binds them), methods after emit
DIFF_OPTS = "easy|Easy 3% / 1.5%,normal|Normal 4% / 2%,hard|Hard 6% / 3%,custom|Custom"
PRESETS = {"easy": (3.0, 1.5), "normal": (4.0, 2.0), "hard": (6.0, 3.0)}
for f in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path FILE;", "public static java.nio.file.Path BANDS;",
          "public static volatile boolean ON = true;",
          "public static volatile boolean NEUTRAL = true;",
          "public static volatile String ROLES = %s;" % jstr(ROLES_DEF),
          "public static volatile String EXCLUDE = %s;" % jstr(EXCLUDE_DEF),
          "public static volatile int MAX_LEVEL = 100;",
          "public static volatile String DIFFICULTY = \"normal\";",
          "public static volatile double HP_PCT = 4.0;",
          "public static volatile double DMG_PCT = 2.0;",
          "public static volatile double HP_CAP = 5.0;",
          "public static volatile double DMG_CAP = 3.0;",
          "public static volatile boolean HEAL_ON_LOAD = false;",
          "public static volatile String PASS = %s;" % jstr(PASS_DEF),
          "public static volatile boolean VOLCANIC = true;",
          "public static volatile String ISLANDS = \"0\";",
          "public static volatile String DEFAULT_BAND = \"0\";",
          "public static volatile String PLATE_MODE = \"all\";",
          "public static volatile String FORMAT = %s;" % jstr(FORMAT_DEF),
          "public static volatile String STRIP = %s;" % jstr(STRIP_DEF),
          "public static volatile boolean COLOR_ON = false;",
          "public static volatile String MARKUP = \"tag\";",
          # derived (new arrays / objects are swapped in whole, never edited in place)
          "public static volatile String[] P_ROLES;", "public static volatile String[] P_EXCL;",
          "public static volatile String[] P_PASS;", "public static volatile String[] P_STRIP;",
          "public static volatile double HP_STEP = 0.04;", "public static volatile double DMG_STEP = 0.02;",
          "public static volatile int ISL_A = 0;", "public static volatile int ISL_B = 0;",
          "public static volatile int DEF_A = 0;", "public static volatile int DEF_B = 0;",
          "public static volatile @PKG@.MobBands BIOME;", "public static volatile @PKG@.MobBands ENV;",
          "public static volatile @PKG@.MobBands WORLD;", "public static volatile @PKG@.MobBands ZONE;",
          "public static volatile int[] COL_LV;", "public static volatile String[] COL_HEX;",
          "public static volatile int[] ZTOP_A;", "public static volatile int[] ZTOP_B;", "public static volatile String[] ZTOP_KEY;",
          "public static volatile long EPOCH = 0L;", "public static volatile String LOADED = \"\";",
          # review F1: the built-in list = the exact vanilla role ids (lower-cased into VAN on first use)
          "public static final String VANILLA = %s;" % jstr(LEVELLED_TEXT),
          "public static volatile java.util.HashSet VAN;",
          # review F7: every plate format used this run (+ the default) still counts as our plate when a mob is stripped
          "public static final String FORMAT_DEFAULT = %s;" % jstr(FORMAT_DEF),
          "public static final java.util.concurrent.ConcurrentHashMap FORMATS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String DEF_CFG = %s;" % jtext(CFG_TEXT),
          "public static final String DEF_BANDS = %s;" % jtext(BANDS_TEXT)):
    F(cfg, f)

# ================================================================= the config kit (Server Setup > Mobs)
CFG_FILE = "Skyy_SkyyMobs/config.properties"
BANDS_FILE = "Skyy_SkyyMobs/bands.properties"
CFG_CATS = [("levels", "Who gets levels"), ("strength", "Strength"), ("bands", "Level bands"), ("plate", "Nameplate")]
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("part.levels", "Mob levels", "levels", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = new mobs get no level. Mobs that already have one keep it.", "field:MobCfg.ON;after=MobCfg.derive"),
    ("levels.neutral", "Neutral fighters get levels", "levels", "bool", "true", "", "", "", "", "new",
     "Neutral mobs that fight back when hit (boars, Scaraks, Feran warriors). Animals never.",
     "field:MobCfg.NEUTRAL;after=MobCfg.derive"),
    ("levels.roles", "Extra mobs that get levels", "levels", "text", ROLES_DEF, "", "2000", "", "", "new",
     "Other mods' role ids or Prefix* patterns. Vanilla hostile mobs + neutral fighters are built in.",
     "field:MobCfg.ROLES;after=MobCfg.derive"),
    ("levels.exclude", "Never level these", "levels", "text", EXCLUDE_DEF, "", "2000", "", "", "new",
     "Never levelled: tests, tamed, traders, bosses, mounts, pets. * = strip every level as mobs load.",
     "field:MobCfg.EXCLUDE;after=MobCfg.derive"),
    ("levels.max", "Highest mob level", "levels", "int", "100", "1", "1000", "", "", "new,adv",
     "Band + bonus never goes above this.", "field:MobCfg.MAX_LEVEL"),
    ("strength.difficulty", "Difficulty", "strength", "choice", "normal", "", "", DIFF_OPTS, "", "live",
     "Health and damage added per mob level. Custom = the two rows below.", "field:MobCfg.DIFFICULTY;after=MobCfg.derive"),
    ("strength.hp", "Custom: health per level", "strength", "dec", "4", "0", "100", "", "%", "live",
     "Difficulty Custom only: max health +this % per level above 1 (mobs that spawn or reload).",
     "field:MobCfg.HP_PCT;after=MobCfg.derive"),
    ("strength.dmg", "Custom: damage per level", "strength", "dec", "2", "0", "100", "", "%", "live",
     "Difficulty Custom only: damage +this % per level above 1, before armour. Applies at once.",
     "field:MobCfg.DMG_PCT;after=MobCfg.derive"),
    ("strength.hpCap", "Health multiplier cap", "strength", "dec", "5", "1", "100", "", "x", "live",
     "Max health never goes above this multiple (x5 never clips Hard at Lv 60).", "field:MobCfg.HP_CAP"),
    ("strength.dmgCap", "Damage multiplier cap", "strength", "dec", "3", "1", "100", "", "x", "live",
     "Damage never goes above this multiple (x3 never clips Hard at Lv 60).", "field:MobCfg.DMG_CAP"),
    ("strength.healOnLoad", "Heal mobs on chunk reload", "strength", "bool", "false", "", "", "", "", "live,adv",
     "Off = a wounded mob keeps its health share when it reloads with a new multiplier.", "field:MobCfg.HEAL_ON_LOAD"),
    ("bands.biome", "Level by biome", "bands", "table", "", "0", "1000", "int|int;type;Min|Max", "", "new",
     "Region.Biome (Zone1_Tier3.Forest_Azure), or a Region alone = its other biomes (Zone1_Tier3).",
     "reload@%s:biome.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.env", "Level by environment", "bands", "table", "", "0", "1000", "int|int|int;type;Min|Max|Bonus", "", "new",
     "Band where no biome is known (islands, World Gen 2); Bonus is added on top of a biome band.",
     "reload@%s:env.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.world", "Level by world", "bands", "table", "", "0", "1000", "int|int;type;Min|Max", "", "new",
     "World name or its start (dungeon_ = dungeon_1, dungeon_2) - wins over all. 0-0 = no levels.",
     "reload@%s:world.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.zone", "Zone fallback", "bands", "table", "", "0", "1000", "int|int;type;Min|Max", "", "new",
     "Zone1-Zone4: used when only the zone is known (region or environment name).",
     "reload@%s:zone.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.volcanicTop", "Lava caves use the zone top", "bands", "bool", "true", "", "", "", "", "new",
     "Vanilla's deep lava caves get the band of the zone's hardest biome.", "field:MobCfg.VOLCANIC"),
    ("bands.islands", "Private islands", "bands", "range", "0", "0", "1000", "", "", "new",
     "SkyyIslands island worlds: a range like 1-3, or 0 for no levels.", "field:MobCfg.ISLANDS;after=MobCfg.derive"),
    ("bands.default", "When nothing matches", "bands", "range", "0", "0", "1000", "", "", "new",
     "Level range when no row matches (oceans, unknown worlds). 0 = no level.", "field:MobCfg.DEFAULT_BAND;after=MobCfg.derive"),
    ("bands.passThrough", "Use the land underneath", "bands", "text", PASS_DEF, "", "2000", "", "", "new,adv",
     "Overlay biomes (rivers, lakes, dunes, valleys, villages) that take the biome below them.",
     "field:MobCfg.PASS;after=MobCfg.derive"),
    ("plate.mode", "Level nameplates", "plate", "choice", "all", "", "", "all|All levelled mobs,off|Off", "", "new",
     "Show [Lv 9] Name over every levelled mob, or no plates.", "field:MobCfg.PLATE_MODE"),
    ("plate.format", "Nameplate text", "plate", "text", FORMAT_DEF, "", "60", "", "", "new",
     "{level} = the level, {name} = the mob's name. Must hold {level}.",
     "field:MobCfg.FORMAT;after=MobCfg.derive;check=MobHooks.checkFormat"),
    ("plate.colorOn", "Colour by level (trial)", "plate", "bool", "false", "", "", "", "", "new",
     "UNVERIFIED client support: try /mobs platetest, pick the markup that shows colour, then switch on.",
     "field:MobCfg.COLOR_ON"),
    ("plate.markup", "Colour markup", "plate", "choice", "tag", "", "",
     "tag|1 color tag,section|2 section sign,brace|3 brace token", "", "new",
     "1 = <color=#..> tag, 2 = section sign codes, 3 = {#..} token. Use the one /mobs platetest colours.",
     "field:MobCfg.MARKUP"),
    ("plate.colors", "Level colours", "plate", "table", "", "", "7", "text;type;Colour", "", "new",
     "Entry = lowest level of the band, value #rrggbb. Default white / yellow / gold / red / purple.",
     "reload@%s:plate.colors.;check=MobHooks.checkColor" % CFG_FILE),
    ("plate.strip", "Name endings to drop", "plate", "text", STRIP_DEF, "", "200", "", "", "new,adv",
     "Used when a mob has no translated name: Skeleton_Fighter_Wander -> Skeleton Fighter.",
     "field:MobCfg.STRIP;after=MobCfg.derive"),
]
_bad = ["%s help %d" % (r[0], len(r[10])) for r in CFG_ROWS if len(r[10]) > 100] + \
       ["%s label %d" % (r[0], len(r[1])) for r in CFG_ROWS if len(r[1]) > 40]
assert not _bad, "config row text too long: %s" % _bad
_dp, _db = CFG.parse_props(CFG_TEXT), CFG.parse_props(BANDS_TEXT)
for _r in CFG_ROWS:
    if _r[3] != "table":
        assert _dp.get(_r[0]) == _r[4], "default file and row default differ: " + _r[0]
assert sum(1 for k in _db if k.startswith("biome.")) == len(BIOME_ROWS) and sum(1 for k in _db if k.startswith("env.")) == len(ENV_ROWS)
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Mobs", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE, BANDS_FILE], NOTE="Chat: /mobs (players); /mobs inspect, set <level>, platetest, reload (admins).",
               RELOAD="MobCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": CFG_TEXT, "bands.properties": BANDS_TEXT})

# ---------------------------------------------------------------- MobCfg methods
M(cfg, r"""
public static int[] range(String s) {
  int[] r = new int[] { 0, 0 };
  if (s == null) return r;
  String t = s.trim().replace(" ", "");
  if (t.length() == 0) return r;
  try {
    int i = t.indexOf('-', 1);
    int a = Integer.parseInt(i < 0 ? t : t.substring(0, i));
    int b = i < 0 ? a : Integer.parseInt(t.substring(i + 1));
    if (a < 0 || b < 0) return r;
    if (a > b) { int x = a; a = b; b = x; }
    if (b > 1000) b = 1000;
    if (a > 1000) a = 1000;
    r[0] = a; r[1] = b;
  } catch (Throwable e) { }
  return r;
}""")
M(cfg, r"""
public static double dec(String s, double def, double lo, double hi) {
  if (s == null) return def;
  try {
    double d = Double.parseDouble(s.trim());
    if (Double.isNaN(d) || Double.isInfinite(d)) return def;
    if (d < lo) d = lo;
    if (d > hi) d = hi;
    return d;
  } catch (Throwable t) { return def; }
}""")
M(cfg, r"""
public static int intOf(String s, int def, int lo, int hi) {
  if (s == null) return def;
  try {
    long v = Long.parseLong(s.trim());
    if (v < lo) v = lo;
    if (v > hi) v = hi;
    return (int) v;
  } catch (Throwable t) { return def; }
}""")
M(cfg, r"""
public static boolean bool(String s, boolean def) {
  if (s == null) return def;
  String t = s.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return false;
  return def;
}""")
M(cfg, r"""
public static String choice(String s, String def, String[] allowed) {
  if (s == null) return def;
  String t = s.trim().toLowerCase();
  for (int i = 0; i < allowed.length; i++) if (allowed[i].equals(t)) return t;
  return def;
}""")
M(cfg, r"""
public static java.util.Properties props(String text) {
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { }
  return p;
}""")
M(cfg, r"""
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
    @PKG@.MobLog.warn("could not read " + f + ": " + t + " - using the built-in defaults for it");
    return null;
  } finally {
    try { if (in != null) in.close(); } catch (Throwable t2) { }
  }
}""")
M(cfg, r"""
public static void seed(java.nio.file.Path f, String text) {
  if (f == null) return;
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Path dir = f.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, text.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    @PKG@.MobLog.info("wrote the default " + f.getFileName());
  } catch (Throwable t) { @PKG@.MobLog.warn("could not write the default " + f + ": " + t); }
}""")
# a table from a properties map: every <prefix><key>=<n>[,<n>[,<n>]] line, keys sorted (deterministic ties), bad lines skipped + warned
M(cfg, r"""
public static @PKG@.MobBands table(java.util.Properties p, String prefix, int cols, String name) {
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith(prefix) && k.length() > prefix.length()) keys.add(k);
  }
  String[] ks = new String[keys.size()];
  for (int i = 0; i < ks.length; i++) ks[i] = (String) keys.get(i);
  java.util.Arrays.sort(ks);
  java.util.ArrayList raw = new java.util.ArrayList();
  int[] a = new int[ks.length], b = new int[ks.length], c = new int[ks.length];
  int n = 0;
  for (int i = 0; i < ks.length; i++) {
    String v = p.getProperty(ks[i], "").trim();
    String[] parts = v.split("[,|]");
    try {
      int x = Integer.parseInt(parts[0].trim());
      int y = parts.length > 1 ? Integer.parseInt(parts[1].trim()) : x;
      int z = (cols > 2 && parts.length > 2) ? Integer.parseInt(parts[2].trim()) : 0;
      if (x < 0 || y < 0 || z < 0 || x > 1000 || y > 1000 || z > 1000) throw new IllegalArgumentException("out of 0-1000");
      if (x > y) { int s = x; x = y; y = s; }
      raw.add(ks[i].substring(prefix.length()));
      a[n] = x; b[n] = y; c[n] = z; n++;
    } catch (Throwable t) {
      @PKG@.MobLog.warnOnce("line:" + ks[i] + "=" + v, name + ": skipped the line " + ks[i] + "=" + v + " (needs whole numbers 0-1000)");
    }
  }
  String[] rk = new String[n];
  int[] ra = new int[n], rb = new int[n], rc = new int[n];
  for (int i = 0; i < n; i++) { rk[i] = (String) raw.get(i); ra[i] = a[i]; rb[i] = b[i]; rc[i] = c[i]; }
  return new @PKG@.MobBands(name, rk, ra, rb, rc);
}""")
M(cfg, r"""
public static void colors(java.util.Properties p) {
  java.util.TreeMap m = new java.util.TreeMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith("plate.colors.")) continue;
    String v = p.getProperty(k, "").trim().toLowerCase();
    try {
      int lvl = Integer.parseInt(k.substring(13).trim());
      if (lvl < 1 || lvl > 1000 || !v.matches("#[0-9a-f]{6}")) throw new IllegalArgumentException("bad");
      m.put(Integer.valueOf(lvl), v);
    } catch (Throwable t) {
      @PKG@.MobLog.warnOnce("col:" + k + "=" + v, "plate.colors: skipped the line " + k + "=" + v + " (needs <level 1-1000>=#rrggbb)");
    }
  }
  int[] lv = new int[m.size()];
  String[] hx = new String[m.size()];
  int i = 0;
  java.util.Iterator e = m.entrySet().iterator();
  while (e.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) e.next();
    lv[i] = ((Integer) en.getKey()).intValue();
    hx[i] = (String) en.getValue();
    i++;
  }
  COL_LV = lv;
  COL_HEX = hx;
}""")
# the band of the hardest biome row of each zone (Skyy R5 lava caves): highest max, then highest min; Region.* fallback rows left out
M(cfg, r"""
public static void zoneTops() {
  int[] za = new int[10], zb = new int[10];
  String[] zk = new String[10];
  @PKG@.MobBands t = BIOME;
  for (int i = 0; t != null && i < t.n; i++) {
    String k = t.raw[i];
    if (k.length() < 6 || !k.startsWith("Zone") || k.indexOf('.') < 0 || k.endsWith(".*")) continue;
    char d = k.charAt(4);
    if (d < '0' || d > '9' || k.charAt(5) != '_') continue;
    int z = d - '0';
    if (t.b[i] > zb[z] || (t.b[i] == zb[z] && t.a[i] > za[z])) { za[z] = t.a[i]; zb[z] = t.b[i]; zk[z] = k; }
  }
  ZTOP_A = za; ZTOP_B = zb; ZTOP_KEY = zk;
}""")
M(cfg, r"""
public static void derive(String key) {
  P_ROLES = @PKG@.MobGlob.list(ROLES);
  P_EXCL = @PKG@.MobGlob.list(EXCLUDE);
  P_PASS = @PKG@.MobGlob.list(PASS);
  P_STRIP = @PKG@.MobGlob.list(STRIP);
  String d = DIFFICULTY == null ? "normal" : DIFFICULTY.trim().toLowerCase();
  double hp = 4.0, dm = 2.0;
  if (d.equals("easy")) { hp = 3.0; dm = 1.5; }
  else if (d.equals("hard")) { hp = 6.0; dm = 3.0; }
  else if (d.equals("custom")) { hp = HP_PCT; dm = DMG_PCT; }
  HP_STEP = hp / 100.0;
  DMG_STEP = dm / 100.0;
  int[] i = range(ISLANDS);
  ISL_A = i[0]; ISL_B = i[1];
  int[] f = range(DEFAULT_BAND);
  DEF_A = f[0]; DEF_B = f[1];
  String fm = FORMAT;
  if (fm != null) {
    if (FORMATS.size() >= 16 && !FORMATS.containsKey(fm)) FORMATS.clear();
    FORMATS.put(fm, Boolean.TRUE);
  }
  EPOCH = EPOCH + 1L;
  try { @PKG@.MobLevel.NAMES.clear(); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c, java.util.Properties b) {
  ON = bool(c.getProperty("part.levels"), true);
  NEUTRAL = bool(c.getProperty("levels.neutral"), true);
  ROLES = c.getProperty("levels.roles", "").trim();
  EXCLUDE = c.getProperty("levels.exclude", @PKG@.MobCfg.EXCL_DEFAULT()).trim();
  MAX_LEVEL = intOf(c.getProperty("levels.max"), 100, 1, 1000);
  DIFFICULTY = choice(c.getProperty("strength.difficulty"), "normal", new String[] { "easy", "normal", "hard", "custom" });
  HP_PCT = dec(c.getProperty("strength.hp"), 4.0, 0.0, 100.0);
  DMG_PCT = dec(c.getProperty("strength.dmg"), 2.0, 0.0, 100.0);
  HP_CAP = dec(c.getProperty("strength.hpCap"), 5.0, 1.0, 100.0);
  DMG_CAP = dec(c.getProperty("strength.dmgCap"), 3.0, 1.0, 100.0);
  HEAL_ON_LOAD = bool(c.getProperty("strength.healOnLoad"), false);
  PASS = c.getProperty("bands.passThrough", @PKG@.MobCfg.PASS_DEFAULT()).trim();
  VOLCANIC = bool(c.getProperty("bands.volcanicTop"), true);
  int[] r1 = range(c.getProperty("bands.islands", "0"));
  ISLANDS = r1[0] == r1[1] ? String.valueOf(r1[0]) : r1[0] + "-" + r1[1];
  int[] r2 = range(c.getProperty("bands.default", "0"));
  DEFAULT_BAND = r2[0] == r2[1] ? String.valueOf(r2[0]) : r2[0] + "-" + r2[1];
  PLATE_MODE = choice(c.getProperty("plate.mode"), "all", new String[] { "all", "off" });
  String fm = c.getProperty("plate.format", "").trim();
  if (fm.indexOf("{level}") < 0 || fm.length() > 60) fm = "[Lv {level}] {name}";
  FORMAT = fm;
  STRIP = c.getProperty("plate.strip", @PKG@.MobCfg.STRIP_DEFAULT()).trim();
  COLOR_ON = bool(c.getProperty("plate.colorOn"), false);
  MARKUP = choice(c.getProperty("plate.markup"), "tag", new String[] { "tag", "section", "brace" });
  colors(c);
  BIOME = table(b, "biome.", 2, "bands.biome");
  ENV = table(b, "env.", 3, "bands.env");
  WORLD = table(b, "world.", 2, "bands.world");
  ZONE = table(b, "zone.", 2, "bands.zone");
  zoneTops();
  derive(null);
  LOADED = BIOME.n + " biome rows, " + ENV.n + " environment rows, " + WORLD.n + " world rows, " + ZONE.n + " zone rows";
}""".replace("@PKG@.MobCfg.EXCL_DEFAULT()", jstr(EXCLUDE_DEF))
   .replace("@PKG@.MobCfg.PASS_DEFAULT()", jstr(PASS_DEF)).replace("@PKG@.MobCfg.STRIP_DEFAULT()", jstr(STRIP_DEF)))
M(cfg, r"""
public static void reloadAll() {
  java.util.Properties c = read(FILE);
  if (c == null) c = props(DEF_CFG);
  java.util.Properties b = read(BANDS);
  if (b == null) b = props(DEF_BANDS);
  apply(c, b);
}""")
M(cfg, r"""
public static void load() {
  seed(FILE, DEF_CFG);
  seed(BANDS, DEF_BANDS);
  reloadAll();
}""")
M(cfg, "public static void useDefaults() { apply(props(DEF_CFG), props(DEF_BANDS)); }")
# the built-in list (review F1): the exact vanilla role ids, lower case, built once (a whole new set is published, never edited)
M(cfg, r"""
public static java.util.HashSet van() {
  java.util.HashSet s = VAN;
  if (s != null) return s;
  s = new java.util.HashSet();
  String[] p = VANILLA.split(",");
  for (int i = 0; i < p.length; i++) {
    String t = p[i].trim().toLowerCase();
    if (t.length() > 0) s.add(t);
  }
  VAN = s;
  return s;
}""")
M(cfg, "public static boolean builtIn(String role) { return role != null && van().contains(role.toLowerCase()); }")
# who gets a level (null = yes, else the reason): attitude, the exclude list, the built-in list or the extra list, the neutral switch
M(cfg, r"""
public static String whyNot(String att, String role) {
  if (role == null || role.length() == 0) return "not an NPC with a role";
  String a = att == null ? "" : att.trim().toUpperCase();
  boolean hostile = a.equals("HOSTILE"), neutral = a.equals("NEUTRAL");
  if (!hostile && !neutral) return "attitude " + (a.length() == 0 ? "unknown" : a) + " (only hostile mobs and neutral fighters)";
  if (@PKG@.MobGlob.any(P_EXCL, role)) return "in Never level these";
  if (!builtIn(role) && !@PKG@.MobGlob.any(P_ROLES, role)) return "not a built-in vanilla fighter and not in Extra mobs that get levels";
  if (neutral && !NEUTRAL) return "neutral fighters are switched off";
  return null;
}""")
M(cfg, "public static boolean passes(String biome) { return biome != null && @PKG@.MobGlob.any(P_PASS, biome); }")
M(cfg, r"""
public static float hpMult(int level) {
  if (level <= 1) return 1.0f;
  double m = 1.0 + HP_STEP * (double) (level - 1);
  if (m > HP_CAP) m = HP_CAP;
  if (m < 1.0) m = 1.0;
  return (float) m;
}""")
M(cfg, r"""
public static float dmgMult(int level) {
  if (level <= 1) return 1.0f;
  double m = 1.0 + DMG_STEP * (double) (level - 1);
  if (m > DMG_CAP) m = DMG_CAP;
  if (m < 1.0) m = 1.0;
  return (float) m;
}""")
M(cfg, r"""
public static String pct(double d) {
  String s = String.valueOf(Math.round(d * 1000.0) / 10.0);
  if (s.endsWith(".0")) s = s.substring(0, s.length() - 2);
  return s;
}""")
M(cfg, r"""
public static String difficultyText() {
  String d = DIFFICULTY == null ? "normal" : DIFFICULTY;
  String n = d.equals("easy") ? "Easy" : d.equals("hard") ? "Hard" : d.equals("custom") ? "Custom" : "Normal";
  return n + " " + pct(HP_STEP) + "% / " + pct(DMG_STEP) + "%";
}""")

# ---------------------------------------------------------------- MobLevel: the level core (pure parts first, engine glue after)
M(lv, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# SplitMix64 finalizer (constants as signed decimals: 0xBF58476D1CE4E5B9, 0x94D049BB133111EB, 0x9E3779B97F4A7C15)
M(lv, r"""
public static long mix(long z) {
  z = (z ^ (z >>> 30)) * -4658895280553007687L;
  z = (z ^ (z >>> 27)) * -7723592293110705685L;
  return z ^ (z >>> 31);
}""")
M(lv, r"""
public static int roll(long worldSeed, java.util.UUID u, String role, int a, int b) {
  if (b <= a) return a;
  long h = mix(worldSeed + -7046029254386353131L);
  if (u != null) { h = mix(h ^ u.getMostSignificantBits()); h = mix(h ^ u.getLeastSignificantBits()); }
  h = mix(h ^ (long) (role == null ? 0 : role.hashCode()));
  long span = (long) (b - a + 1);
  return a + (int) Long.remainderUnsigned(h, span);
}""")
# res = Object[]{ Integer min, Integer max, Integer bonus, String step, String key } -> the final level (0 = none)
M(lv, r"""
public static int levelFor(Object[] res, long worldSeed, java.util.UUID u, String role) {
  if (res == null) return 0;
  int a = ((Integer) res[0]).intValue(), b = ((Integer) res[1]).intValue(), bonus = ((Integer) res[2]).intValue();
  if (a <= 0 && b <= 0) return 0;
  if (a <= 0) a = 1;
  int l = roll(worldSeed, u, role, a, b) + bonus;
  if (l > @PKG@.MobCfg.MAX_LEVEL) l = @PKG@.MobCfg.MAX_LEVEL;
  if (l < 1) l = 1;
  return l;
}""")
M(lv, 'public static String keyOf(int level) { return KEY_PREFIX + level; }')
M(lv, r"""
public static int levelOfKey(Object k) {
  if (!(k instanceof String)) return -1;
  String s = (String) k;
  if (!s.startsWith(KEY_PREFIX) || s.length() == KEY_PREFIX.length() || s.length() > KEY_PREFIX.length() + 4) return -1;
  int v = 0;
  for (int i = KEY_PREFIX.length(); i < s.length(); i++) {
    char c = s.charAt(i);
    if (c < '0' || c > '9') return -1;
    v = v * 10 + (c - '0');
  }
  return v >= 1 ? v : -1;
}""")
M(lv, r"""
public static int savedFromKeys(Object[] keys) {
  int best = -1;
  for (int i = 0; keys != null && i < keys.length; i++) {
    int v = levelOfKey(keys[i]);
    if (v > best) best = v;
  }
  return best;
}""")
# which kept level wins on an add: the save slot on the mob, else this session's memory (null = roll a new one)
M(lv, r"""
public static Object[] pick(int saved, Object kept) {
  if (saved > 0) return new Object[] { Integer.valueOf(saved), "saved" };
  if (kept instanceof Integer && ((Integer) kept).intValue() > 0) return new Object[] { kept, "kept" };
  return null;
}""")
# health after a max change: the same share of the new max (clamped 0..1)
M(lv, r"""
public static float share(float oldVal, float oldMax, float newMax) {
  if (oldMax <= 0.0f) return newMax;
  float s = oldVal / oldMax;
  if (s > 1.0f) s = 1.0f;
  if (s < 0.0f) s = 0.0f;
  return s * newMax;
}""")
# ---- names
M(lv, r"""
public static String stripRole(String role) {
  if (role == null) return "";
  String s = role;
  String[] ends = @PKG@.MobCfg.P_STRIP;
  boolean cut = true;
  for (int guard = 0; cut && guard < 8; guard++) {
    cut = false;
    String low = s.toLowerCase();
    for (int i = 0; ends != null && i < ends.length; i++) {
      String e = ends[i];
      if (e.length() > 0 && low.endsWith(e) && low.length() > e.length()) { s = s.substring(0, s.length() - e.length()); cut = true; break; }
    }
  }
  return s;
}""")
M(lv, r"""
public static String i18n(String key) {
  if (key == null || key.length() == 0) return null;
  try {
    @INTL@ m = @INTL@.get();
    if (m == null) return null;
    String s = m.getMessage("en-US", key);
    if ((s == null || s.length() == 0) && key.startsWith("server.")) s = m.getMessage("en-US", key.substring(7));
    return s == null || s.trim().length() == 0 ? null : s.trim();
  } catch (Throwable t) { return null; }
}""")
M(lv, r"""
public static String nameOf(String role, String tkey) {
  String r = role == null ? "" : role;
  String ck = r + "|" + (tkey == null ? "" : tkey);
  Object c = NAMES.get(ck);
  if (c instanceof String) return (String) c;
  String n = i18n(tkey);
  String base = stripRole(r);
  if (n == null) n = i18n("server.npcRoles." + base + ".name");
  if (n == null) n = base.replace('_', ' ').trim();
  if (n.length() == 0) n = r;
  if (NAMES.size() > 2000) NAMES.clear();
  NAMES.put(ck, n);
  return n;
}""")
# ---- nameplate text + markups (UNVERIFIED client support: colours off by default)
M(lv, r"""
public static String hexFor(int level) {
  int[] lv = @PKG@.MobCfg.COL_LV;
  String[] hx = @PKG@.MobCfg.COL_HEX;
  String h = "#ffffff";
  for (int i = 0; lv != null && hx != null && i < lv.length && i < hx.length; i++) if (lv[i] <= level) h = hx[i];
  return h;
}""")
# nearest of the 16 legacy colour codes (0-9, a-f) to a #rrggbb colour
M(lv, r"""
public static char legacy(String hex) {
  String codes = "0123456789abcdef";
  int[] pal = new int[] { 0x000000, 0x0000AA, 0x00AA00, 0x00AAAA, 0xAA0000, 0xAA00AA, 0xFFAA00, 0xAAAAAA, 0x555555, 0x5555FF, 0x55FF55, 0x55FFFF, 0xFF5555, 0xFF55FF, 0xFFFF55, 0xFFFFFF };
  int v = 0xFFFFFF;
  try { v = Integer.parseInt(hex.substring(1, 7), 16); } catch (Throwable t) { }
  int r = (v >> 16) & 255, g = (v >> 8) & 255, b = v & 255;
  int best = 15;
  long bd = Long.MAX_VALUE;
  for (int i = 0; i < 16; i++) {
    int pr = (pal[i] >> 16) & 255, pg = (pal[i] >> 8) & 255, pb = pal[i] & 255;
    long d = (long) (r - pr) * (r - pr) + (long) (g - pg) * (g - pg) + (long) (b - pb) * (b - pb);
    if (d < bd) { bd = d; best = i; }
  }
  return codes.charAt(best);
}""")
M(lv, r"""
public static String markup(String text, String hex, String mode) {
  if (text == null) return "";
  String m = mode == null ? "tag" : mode;
  if (m.equals("section")) return String.valueOf((char) 167) + legacy(hex) + text + String.valueOf((char) 167) + "r";
  if (m.equals("brace")) return "{" + hex + "}" + text;
  return "<color=" + hex + ">" + text + "</color>";
}""")
M(lv, r"""
public static String plateText(int level, String name) {
  String f = @PKG@.MobCfg.FORMAT;
  if (f == null || f.indexOf("{level}") < 0) f = "[Lv {level}] {name}";
  String t = f.replace("{level}", String.valueOf(level)).replace("{name}", name == null ? "" : name).trim();
  if (!@PKG@.MobCfg.COLOR_ON) return t;
  return markup(t, hexFor(level), @PKG@.MobCfg.MARKUP);
}""")
# the plate text without any of the three markups (and without a "1: " platetest prefix)
M(lv, r"""
public static String plain(String text) {
  if (text == null) return "";
  String s = text.replaceAll("</?color(=#[0-9A-Fa-f]{6})?>", "").replaceAll("\\{#[0-9A-Fa-f]{6}\\}", "");
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == (char) 167) { i++; continue; }
    sb.append(c);
  }
  String r = sb.toString().trim();
  if (r.length() > 3 && r.charAt(0) >= '1' && r.charAt(0) <= '3' && r.charAt(1) == ':' && r.charAt(2) == ' ') r = r.substring(3);
  return r;
}""")
# a plate made with format f = the format's literal parts in order (the first one at the start when the format starts with it)
M(lv, r"""
public static boolean isOursFor(String text, String f) {
  if (text == null || f == null || f.indexOf("{level}") < 0) return false;
  String p = plain(text);
  String[] parts = f.replace("{name}", "{level}").split(java.util.regex.Pattern.quote("{level}"), -1);
  int pos = 0, hits = 0;
  for (int i = 0; i < parts.length; i++) {
    String s = parts[i];
    if (s.length() == 0) continue;
    int at = p.indexOf(s, pos);
    if (at < 0 || (i == 0 && at != 0)) return false;
    pos = at + s.length();
    hits++;
  }
  if (hits > 0) return true;
  return p.length() > 0 && p.charAt(0) >= '0' && p.charAt(0) <= '9';
}""")
# our plate (review F7): made with the current format, the default format or any format used this run - a mob that stops qualifying
# after an admin changed plate.format still loses its old plate
M(lv, r"""
public static boolean isOurs(String text) {
  if (text == null) return false;
  if (isOursFor(text, @PKG@.MobCfg.FORMAT) || isOursFor(text, @PKG@.MobCfg.FORMAT_DEFAULT)) return true;
  Object[] fs = @PKG@.MobCfg.FORMATS.keySet().toArray();
  for (int i = 0; i < fs.length; i++) if (fs[i] instanceof String && isOursFor(text, (String) fs[i])) return true;
  return false;
}""")
# ---- the lookup chain (pure: strings in, Object[]{Integer min, Integer max, Integer bonus, String step, String key} out)
M(lv, r"""
public static Object[] res(int a, int b, int bonus, String step, String key) {
  return new Object[] { Integer.valueOf(a), Integer.valueOf(b), Integer.valueOf(bonus), step, key };
}""")
M(lv, r"""
public static String zoneOfRegion(String region) {
  if (region == null || region.length() < 5 || !region.startsWith("Zone")) return null;
  int i = 4;
  while (i < region.length() && region.charAt(i) >= '0' && region.charAt(i) <= '9') i++;
  if (i == 4) return null;
  if (i < region.length() && region.charAt(i) != '_') return null;
  return region.substring(0, i);
}""")
M(lv, r"""
public static String zoneOfEnv(String env) {
  if (env == null || !env.startsWith("Env_Zone")) return null;
  return zoneOfRegion(env.substring(4));
}""")
M(lv, r"""
public static int volcanicZone(String env) {
  if (env == null || env.indexOf("_Caves_Volcanic") < 0) return 0;
  String z = zoneOfEnv(env);
  if (z == null || !env.startsWith("Env_" + z + "_Caves_Volcanic")) return 0;
  try { return Integer.parseInt(z.substring(4)); } catch (Throwable t) { return 0; }
}""")
M(lv, r"""
public static Object[] resolve(String wn, boolean island, boolean classic, String region, String biome, String tile, String env) {
  @PKG@.MobBands W = @PKG@.MobCfg.WORLD, E = @PKG@.MobCfg.ENV, BI = @PKG@.MobCfg.BIOME, Z = @PKG@.MobCfg.ZONE;
  int wi = W == null ? -1 : W.findPrefix(wn);
  if (wi >= 0) return res(W.a[wi], W.b[wi], 0, "world", W.raw[wi]);
  if (island) return res(@PKG@.MobCfg.ISL_A, @PKG@.MobCfg.ISL_B, 0, "island", "bands.islands");
  int ei = (E == null || env == null) ? -1 : E.find(env);
  int ebonus = ei >= 0 ? E.c[ei] : 0;
  int vz = volcanicZone(env);
  int[] ta = @PKG@.MobCfg.ZTOP_A, tb = @PKG@.MobCfg.ZTOP_B;
  if (@PKG@.MobCfg.VOLCANIC && vz > 0 && ta != null && vz < ta.length && tb[vz] > 0)
    return res(ta[vz], tb[vz], ebonus, "lava", "Zone" + vz + " top " + @PKG@.MobCfg.ZTOP_KEY[vz]);
  if (classic && region != null && BI != null) {
    String used = biome;
    if (biome != null && tile != null && @PKG@.MobCfg.passes(biome)) used = tile;
    int bi = used == null ? -1 : BI.find(region + "." + used);
    if (bi < 0 && used != biome && biome != null) bi = BI.find(region + "." + biome);
    if (bi < 0) bi = BI.find(region);
    if (bi < 0) bi = BI.find(region + ".*");
    if (bi >= 0) return res(BI.a[bi], BI.b[bi], ebonus, "biome", BI.raw[bi]);
  }
  if (ei >= 0) return res(E.a[ei], E.b[ei], 0, "env", E.raw[ei]);
  String z = zoneOfRegion(region);
  if (z == null) z = zoneOfEnv(env);
  int zi = (Z == null || z == null) ? -1 : Z.find(z);
  if (zi >= 0) return res(Z.a[zi], Z.b[zi], 0, "zone", Z.raw[zi]);
  return res(@PKG@.MobCfg.DEF_A, @PKG@.MobCfg.DEF_B, 0, "default", "bands.default");
}""")
# ---- engine glue: environment, worldgen, island
M(lv, r"""
public static String envId(int idx) {
  if (idx == Integer.MIN_VALUE || idx < 0) return null;
  try {
    Object a = @ENVA@.getAssetMap().getAsset(idx);
    if (a instanceof @ENVA@) return ((@ENVA@) a).getId();
  } catch (Throwable t) { }
  return null;
}""")
M(lv, r"""
public static int blockEnv(@WLD@ w, int x, int y, int z) {
  if (w == null) return Integer.MIN_VALUE;
  try {
    Object c = w.getChunkStore().getChunkComponent(@CHU@.indexChunkFromBlock(x, z), @BCH@.getComponentType());
    if (c instanceof @BCH@) return ((@BCH@) c).getEnvironment(x, y, z);
  } catch (Throwable t) { }
  return Integer.MIN_VALUE;
}""")
M(lv, r"""
public static boolean islandOf(String wn) {
  if (wn == null) return false;
  try {
    Object f = bridge().get("island:owner:fn");
    if (f instanceof java.util.function.Function) return ((java.util.function.Function) f).apply(wn) != null;
  } catch (Throwable t) { }
  return false;
}""")
# String[]{ region, biome, tile, zoneName, classic "1"/"0" } for a column of a world, cached per exact block column (review F3: an 8x8
# cell reused the first spawn's biome for its neighbours across a biome border; the engine caches the lookup itself, ChunkGeneratorCache).
# A failed lookup or a world whose generator is not attached yet is NOT cached: the next spawn there asks again.
M(lv, r"""
public static String[] worldgen(@WLD@ w, int x, int z) {
  if (w == null) return null;
  String wn = w.getName();
  String ck = wn + ":" + x + ":" + z;
  Object c = WG.get(ck);
  if (c instanceof String[]) return (String[]) c;
  String[] r = null;
  boolean keep = true;
  try {
    Object g = w.getChunkStore().getGenerator();
    if (g instanceof @CGEN@) {
      int seed = (int) w.getWorldConfig().getSeed();
      @ZBR@ zr = ((@CGEN@) g).getZoneBiomeResultAt(seed, x, z);
      @ZONE@ zone = zr.getZoneResult().getZone();
      String biome = zr.getBiome() == null ? null : zr.getBiome().getName();
      String tile = null;
      try { tile = zone.biomePatternGenerator().getBiome(seed, x, z).getName(); } catch (Throwable t1) { tile = null; }
      String zn = null;
      try { zn = zone.discoveryConfig() == null ? null : zone.discoveryConfig().zone(); } catch (Throwable t2) { zn = null; }
      r = new String[] { zone.name(), biome, tile, zn, "1" };
    } else {
      r = new String[] { null, null, null, null, "0" };
      keep = g != null;
    }
  } catch (Throwable t) {
    @PKG@.MobLog.warnOnce("worldgen:" + wn, "could not read the worldgen zone / biome in world " + wn + ": " + t + " - mobs spawned there meanwhile use the environment / zone / default rows (asked again on the next spawn)");
    r = new String[] { null, null, null, null, "0" };
    keep = false;
  }
  if (keep) {
    if (WG.size() >= WG_MAX) WG.clear();
    WG.put(ck, r);
  }
  return r;
}""")
# Object[]{ min, max, bonus, step, key, region, biome, tile, env, zoneName, classic, island } at a position (envIdx = the spawn env or MIN)
M(lv, r"""
public static Object[] lookupAt(@WLD@ w, double x, double y, double z, int envIdx) {
  int bx = (int) Math.floor(x), by = (int) Math.floor(y), bz = (int) Math.floor(z);
  String wn = w == null ? "" : w.getName();
  int ei = envIdx;
  if (ei == Integer.MIN_VALUE) ei = blockEnv(w, bx, by, bz);
  String env = envId(ei);
  String[] g = worldgen(w, bx, bz);
  boolean classic = g != null && "1".equals(g[4]);
  boolean island = islandOf(wn);
  Object[] r = resolve(wn, island, classic, classic ? g[0] : null, classic ? g[1] : null, classic ? g[2] : null, env);
  return new Object[] { r[0], r[1], r[2], r[3], r[4], classic ? g[0] : null, classic ? g[1] : null, classic ? g[2] : null, env,
                        classic ? g[3] : null, classic ? "1" : "0", island ? "1" : "0" };
}""")
# ---- the health modifier (save slot)
M(lv, r"""
public static Object[] modKeys(@ESM@ m, int hi) {
  try {
    @ESV@ v = m.get(hi);
    java.util.Map mods = v == null ? null : v.getModifiers();
    if (mods == null || mods.isEmpty()) return new Object[0];
    return mods.keySet().toArray();
  } catch (Throwable t) { return new Object[0]; }
}""")
M(lv, "public static int savedLevel(@ESM@ m, int hi) { return m == null ? -1 : savedFromKeys(modKeys(m, hi)); }")
# remove every save-slot key except keep; true when one was removed
M(lv, r"""
public static boolean removeOurs(@ESM@ m, int hi, String keep) {
  boolean any = false;
  Object[] ks = modKeys(m, hi);
  for (int i = 0; i < ks.length; i++) {
    if (levelOfKey(ks[i]) > 0 && (keep == null || !keep.equals(ks[i]))) { m.removeModifier(hi, (String) ks[i]); any = true; }
  }
  return any;
}""")
# put the level's multiplier; health: full = maximize, else keep the health share when the max changed
M(lv, r"""
public static float setMult(@ESM@ m, int hi, int level, boolean full) {
  float mult = @PKG@.MobCfg.hpMult(level);
  String key = keyOf(level);
  @ESV@ v = m.get(hi);
  if (v == null) return mult;
  float oldMax = v.getMax(), oldVal = v.get();
  boolean changed = removeOurs(m, hi, key);
  Object cur = m.getModifier(hi, key);
  if (!(cur instanceof @SMO@) || Math.abs(((@SMO@) cur).getAmount() - mult) > 0.000001f) {
    m.putModifier(hi, key, new @SMO@(@MTG@.MAX, @CAL@.MULTIPLICATIVE, mult));
    changed = true;
  }
  if (full || @PKG@.MobCfg.HEAL_ON_LOAD) { m.maximizeStatValue(hi); return mult; }
  if (changed && oldMax > 0.0f) {
    @ESV@ v2 = m.get(hi);
    m.setStatValue(hi, share(oldVal, oldMax, v2 == null ? oldMax : v2.getMax()));
  }
  return mult;
}""")
M(lv, r"""
public static void stripStats(@ESM@ m, int hi) {
  @ESV@ v = m.get(hi);
  if (v == null) return;
  float oldMax = v.getMax(), oldVal = v.get();
  if (!removeOurs(m, hi, null)) return;
  @ESV@ v2 = m.get(hi);
  if (v2 != null && oldMax > 0.0f) m.setStatValue(hi, share(oldVal, oldMax, v2.getMax()));
}""")
# ---- components through a Holder (the hook) or a Store + Ref (commands)
M(lv, r"""
public static @COMP@ comp(@HOLD@ h, @ST@ st, @REF@ r, @CTYPE@ t) {
  if (t == null) return null;
  if (h != null) return h.getComponent(t);
  if (st == null || r == null || !r.isValid()) return null;
  return st.getComponent(r, t);
}""")
M(lv, r"""
public static void setPlate(@HOLD@ h, @ST@ st, @REF@ r, String text) {
  @NPL@ p = null;
  if (h != null) p = (@NPL@) h.ensureAndGetComponent(@NPL@.getComponentType());
  else if (st != null && r != null && r.isValid()) p = (@NPL@) st.ensureAndGetComponent(r, @NPL@.getComponentType());
  if (p != null && !text.equals(p.getText())) p.setText(text);
}""")
M(lv, r"""
public static void dropPlate(@HOLD@ h, @ST@ st, @REF@ r, boolean onlyOurs) {
  if (h == null && (st == null || r == null)) return;
  @NPL@ p = (@NPL@) comp(h, st, r, @NPL@.getComponentType());
  if (p == null) return;
  if (onlyOurs && !isOurs(p.getText())) return;
  if (h != null) h.tryRemoveComponent(@NPL@.getComponentType());
  else if (st != null && r != null && r.isValid()) st.tryRemoveComponent(r, @NPL@.getComponentType());
}""")
M(lv, r"""
public static String plateOf(@HOLD@ h, @ST@ st, @REF@ r) {
  if (h == null && (st == null || r == null)) return null;
  @NPL@ p = (@NPL@) comp(h, st, r, @NPL@.getComponentType());
  return p == null ? null : p.getText();
}""")
M(lv, r"""
public static String tkeyOf(@NPCE@ npc) {
  try { return npc.getRole() == null ? null : npc.getRole().getNameTranslationKey(); } catch (Throwable t) { return null; }
}""")
M(lv, r"""
public static @PKG@.MobInfo apply(@HOLD@ h, @ST@ st, @REF@ r, @NPCE@ npc, @ESM@ m, java.util.UUID u, @WLD@ w, String wn, String role,
                                   int level, boolean full, String step, Object[] res) {
  int hi = @DST@.getHealth();
  setMult(m, hi, level, full);
  String name = nameOf(role, tkeyOf(npc));
  if ("off".equals(@PKG@.MobCfg.PLATE_MODE)) dropPlate(h, st, r, true);
  else setPlate(h, st, r, plateText(level, name));
  @PKG@.MobInfo i = new @PKG@.MobInfo();
  i.world = wn; i.uuid = u; i.role = role; i.name = name; i.level = level; i.step = step; i.at = System.currentTimeMillis();
  if (w != null) i.wref = new java.lang.ref.WeakReference(w);
  if (res != null) {
    i.a = ((Integer) res[0]).intValue(); i.b = ((Integer) res[1]).intValue(); i.bonus = ((Integer) res[2]).intValue();
    i.key = (String) res[4];
  }
  if (u != null) { MOBS.put(u, i); KEPT.remove(u); }
  return i;
}""")
M(lv, r"""
public static void strip(@HOLD@ h, @ST@ st, @REF@ r, @ESM@ m, java.util.UUID u) {
  if (m != null) stripStats(m, @DST@.getHealth());
  dropPlate(h, st, r, true);
  if (u != null) { MOBS.remove(u); KEPT.remove(u); }
}""")
M(lv, r"""
public static @WLD@ worldOf(@ST@ st) {
  try { Object e = st.getExternalData(); return e instanceof @EST@ ? ((@EST@) e).getWorld() : null; } catch (Throwable t) { return null; }
}""")
# the spawn point: the leash point (saved LeashPos) when set, else the current position
M(lv, r"""
public static double[] spawnPos(@NPCE@ npc, @HOLD@ h, @ST@ st, @REF@ r) {
  try {
    @VEC@ lp = npc.getLeashPoint();
    if (lp != null && (lp.x != 0.0 || lp.y != 0.0 || lp.z != 0.0)) return new double[] { lp.x, lp.y, lp.z };
  } catch (Throwable t) { }
  @TC@ tc = (@TC@) comp(h, st, r, @TC@.getComponentType());
  if (tc == null || tc.getPosition() == null) return null;
  @VEC@ p = tc.getPosition();
  return new double[] { p.x, p.y, p.z };
}""")
M(lv, r"""
public static String attitudeOf(@HOLD@ h, @ST@ st, @REF@ r) {
  try {
    @WSUP@ ws = (@WSUP@) comp(h, st, r, @WSUP@.getComponentType());
    return ws == null || ws.getDefaultPlayerAttitude() == null ? "" : ws.getDefaultPlayerAttitude().name();
  } catch (Throwable t) { return ""; }
}""")
# Object[] lookup result (lookupAt) for a mob: its spawn point + its spawn environment
M(lv, r"""
public static Object[] lookupMob(@WLD@ w, @NPCE@ npc, @HOLD@ h, @ST@ st, @REF@ r) {
  double[] p = spawnPos(npc, h, st, r);
  if (p == null) return null;
  int ei = Integer.MIN_VALUE;
  try { ei = npc.getEnvironment(); } catch (Throwable t) { ei = Integer.MIN_VALUE; }
  return lookupAt(w, p[0], p[1], p[2], ei);
}""")
M(lv, r"""
public static void onAdd(@HOLD@ h, boolean spawn, @ST@ st) {
  @NPCE@ npc = (@NPCE@) h.getComponent(@NPCE@.getComponentType());
  if (npc == null) return;
  @ESM@ m = (@ESM@) h.getComponent(@ESM@.getComponentType());
  if (m == null) return;
  @UUIDC@ uc = (@UUIDC@) h.getComponent(@UUIDC@.getComponentType());
  java.util.UUID u = uc == null ? null : uc.getUuid();
  if (u == null) return;
  String role = npc.getRoleName();
  int hi = @DST@.getHealth();
  int saved = savedLevel(m, hi);
  Object kept = KEPT.remove(u);
  String no = @PKG@.MobCfg.whyNot(attitudeOf(h, null, null), role);
  if (no != null) {
    if (saved > 0 || isOurs(plateOf(h, null, null))) strip(h, null, null, m, u);
    return;
  }
  @WLD@ w = worldOf(st);
  String wn = w == null ? "" : w.getName();
  Object[] pk = pick(saved, kept);
  int level = pk == null ? 0 : ((Integer) pk[0]).intValue();
  String step = pk == null ? null : (String) pk[1];
  Object[] res = null;
  if (level <= 0) {
    if (!@PKG@.MobCfg.ON) return;
    res = lookupMob(w, npc, h, null, null);
    long seed = 0L;
    try { seed = w == null ? 0L : w.getWorldConfig().getSeed(); } catch (Throwable t) { seed = 0L; }
    level = levelFor(res, seed, u, role);
    if (level <= 0) return;
    step = (String) res[3];
  }
  apply(h, null, null, npc, m, u, w, wn, role, level, spawn, step, res);
}""")
M(lv, r"""
public static void forget(java.util.UUID u, boolean unload) {
  if (u == null) return;
  Object o = MOBS.remove(u);
  if (unload && o instanceof @PKG@.MobInfo) {
    if (KEPT.size() >= KEPT_MAX) KEPT.clear();
    KEPT.put(u, Integer.valueOf(((@PKG@.MobInfo) o).level));
  } else KEPT.remove(u);
}""")
M(lv, r"""
public static void onRemove(@HOLD@ h, boolean unload) {
  @UUIDC@ uc = (@UUIDC@) h.getComponent(@UUIDC@.getComponentType());
  forget(uc == null ? null : uc.getUuid(), unload);
}""")
M(lv, r"""
public static void clearAll() { MOBS.clear(); KEPT.clear(); WG.clear(); NAMES.clear(); }""")
# ---- the prune (review F6: a removed world's store may never call onEntityRemoved, so MOBS could keep its mobs forever).
# MobPruneTask runs every 5 minutes on the scheduler: pruneWith forgets mobs whose world is gone, then each loaded world with levelled
# mobs checks its own on its world thread (pruneWorld). KEPT needs no prune: it is bounded (KEPT_MAX, cleared when full).
M(lv, r"""
public static java.util.ArrayList liveWorlds() {
  try {
    @UNIV@ u = @UNIV@.get();
    if (u == null) return null;
    java.util.Map m = u.getWorlds();
    return m == null ? null : new java.util.ArrayList(m.values());
  } catch (Throwable t) { return null; }
}""")
M(lv, r"""
public static java.util.ArrayList namesOf(java.util.Collection worlds) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = worlds == null ? null : worlds.iterator();
  while (it != null && it.hasNext()) {
    Object o = it.next();
    try { if (o instanceof @WLD@) out.add(((@WLD@) o).getName()); } catch (Throwable t) { }
  }
  return out;
}""")
# forget every mob (older than PRUNE_GRACE) whose world is not one of `worlds` (by identity; its weak reference cleared = gone too);
# a mob without a world reference goes by its world name (names == null: kept). Removes only the exact entry it looked at.
M(lv, r"""
public static int pruneWith(java.util.Collection worlds, java.util.Collection names, long now) {
  java.util.IdentityHashMap live = new java.util.IdentityHashMap();
  java.util.Iterator wi = worlds == null ? null : worlds.iterator();
  while (wi != null && wi.hasNext()) {
    Object o = wi.next();
    if (o != null) live.put(o, Boolean.TRUE);
  }
  int n = 0;
  java.util.Iterator it = MOBS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    boolean gone = false;
    if (!(v instanceof @PKG@.MobInfo)) gone = true;
    else {
      @PKG@.MobInfo i = (@PKG@.MobInfo) v;
      if (now - i.at >= PRUNE_GRACE) {
        if (i.wref != null) { Object w = i.wref.get(); gone = w == null || !live.containsKey(w); }
        else gone = names != null && (i.world == null || !names.contains(i.world));
      }
    }
    if (gone && MOBS.remove(e.getKey(), v)) n++;
  }
  return n;
}""")
M(lv, r"""
public static boolean hasMobsIn(Object w) {
  if (w == null) return false;
  java.util.Iterator it = MOBS.values().iterator();
  while (it.hasNext()) {
    Object v = it.next();
    if (v instanceof @PKG@.MobInfo && ((@PKG@.MobInfo) v).wref != null && ((@PKG@.MobInfo) v).wref.get() == w) return true;
  }
  return false;
}""")
# on the world thread of w: forget its levelled mobs whose entity is gone (a removal that skipped the hook)
M(lv, r"""
public static int pruneWorld(@WLD@ w, long now) {
  if (w == null) return 0;
  @EST@ es = w.getEntityStore();
  if (es == null) return 0;
  int n = 0;
  java.util.Iterator it = MOBS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (!(v instanceof @PKG@.MobInfo)) continue;
    @PKG@.MobInfo i = (@PKG@.MobInfo) v;
    if (i.wref == null || i.wref.get() != w || now - i.at < PRUNE_GRACE || i.uuid == null) continue;
    @REF@ r = es.getRefFromUUID(i.uuid);
    if ((r == null || !r.isValid()) && MOBS.remove(e.getKey(), v)) n++;
  }
  return n;
}""")

# ---------------------------------------------------------------- LevelHook (HolderSystem; ordered AFTER the NPC setup systems)
for f in ("public static Class RBS;", "public static Class SETUP;", "public static Class BAL;", "public java.util.Set deps;",
          "public boolean ordered;", "public @QRY@ query;"):
    F(hk, f)
C(hk, r"""
public LevelHook(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered;
  if (ordered) {
    if (RBS != null) this.deps.add(new @SDEP@(@ORD@.AFTER, RBS));
    if (SETUP != null) this.deps.add(new @SDEP@(@ORD@.AFTER, SETUP));
    if (BAL != null) this.deps.add(new @SDEP@(@ORD@.AFTER, BAL));
  }
}""")
M(hk, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @NPCE@.getComponentType(), (@QRY@) @ESM@.getComponentType() });
  return this.query;
}""")
M(hk, "public java.util.Set getDependencies() { return this.deps; }")
M(hk, r"""
public void onEntityAdd(@HOLD@ h, @ADDR@ why, @ST@ st) {
  try { @PKG@.MobLevel.onAdd(h, why == @ADDR@.SPAWN, st); }
  catch (Throwable t) { @PKG@.MobLog.warnOnce("hook:" + t.getClass().getName(), "level hook failed (" + t + ") - that mob keeps vanilla stats"); }
}""")
M(hk, r"""
public void onEntityRemoved(@HOLD@ h, @REMR@ why, @ST@ st) {
  try { @PKG@.MobLevel.onRemove(h, why == @REMR@.UNLOAD); } catch (Throwable t) { }
}""")
# (no unordered fallback class any more - review F4: unordered, the hook could run before the role / stat map exist and level nothing,
# or read the attitude as unknown and strip saved levels on load; SkyyMobsPlugin.systems logs an ERROR instead)

# ---------------------------------------------------------------- LevelDamage (Filter group, BEFORE ArmorDamageReduction)
for f in ("public static Class ADR;", "public java.util.Set deps;", "public boolean ordered;"):
    F(dm, f)
C(dm, r"""
public LevelDamage(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered && ADR != null;
  if (this.ordered) this.deps.add(new @SDEP@(@ORD@.BEFORE, ADR));
}""")
M(dm, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(dm, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(dm, "public java.util.Set getDependencies() { return this.deps; }")
M(dm, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (@PKG@.MobLevel.MOBS.isEmpty() || !(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ att = ((@DENT@) src).getRef();
    if (att == null || !att.isValid()) return;
    @UUIDC@ uc = (@UUIDC@) buf.getComponent(att, @UUIDC@.getComponentType());
    if (uc == null) return;
    @PKG@.MobInfo i = (@PKG@.MobInfo) @PKG@.MobLevel.MOBS.get(uc.getUuid());
    if (i == null || i.level <= 1) return;
    float mult = @PKG@.MobCfg.dmgMult(i.level);
    if (mult != 1.0f) d.setAmount(d.getAmount() * mult);
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("dmg", "level damage failed: " + t); }
}""")
C(dmu, "public LevelDamageU() { super(false); }")

# ---------------------------------------------------------------- mob:fn:level (bridge, any thread, never throws)
fn.addInterface(pool.get("java.util.function.Function"))
C(fn, "public MobLevelFn() { }")
M(fn, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = null;
    String w = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o instanceof Object[]) {
      Object[] a = (Object[]) o;
      if (a.length >= 2 && a[1] instanceof java.util.UUID) { u = (java.util.UUID) a[1]; w = a[0] == null ? null : String.valueOf(a[0]); }
      else if (a.length == 1 && a[0] instanceof java.util.UUID) u = (java.util.UUID) a[0];
    }
    if (u == null) return Integer.valueOf(-1);
    Object i = @PKG@.MobLevel.MOBS.get(u);
    if (!(i instanceof @PKG@.MobInfo)) return Integer.valueOf(-1);
    @PKG@.MobInfo m = (@PKG@.MobInfo) i;
    if (w != null && m.world != null && !w.equals(m.world)) return Integer.valueOf(-1);
    return Integer.valueOf(m.level);
  } catch (Throwable t) { return Integer.valueOf(-1); }
}""")

# ---------------------------------------------------------------- MobPlateStep: /mobs platetest (scheduler thread -> world thread, 3 s steps)
ps.addInterface(pool.get("java.lang.Runnable"))
# RUNNING: uuid -> Long start time of the plate test running on that mob (review F11: two tests at once on one mob could restore a test
# text as its plate); a claim older than 30 s is stale (the world stopped mid-test) and may be taken over
F(ps, "public static final java.util.concurrent.ConcurrentHashMap RUNNING = new java.util.concurrent.ConcurrentHashMap();")
for f in ("public @WLD@ world;", "public java.util.UUID uuid;", "public String[] texts;", "public int idx;", "public boolean onWorld;",
          "public @PR@ pr;", "public String orig;", "public String label;"):
    F(ps, f)
C(ps, r"""
public MobPlateStep(@WLD@ world, java.util.UUID uuid, String[] texts, @PR@ pr, String orig, String label) {
  this.world = world; this.uuid = uuid; this.texts = texts; this.pr = pr; this.orig = orig; this.label = label;
  this.idx = 0; this.onWorld = false;
}""")
M(ps, r"""
public static boolean claim(java.util.UUID u, long now) {
  if (u == null) return false;
  Long mine = Long.valueOf(now);
  Object prev = RUNNING.putIfAbsent(u, mine);
  if (prev == null) return true;
  if (prev instanceof Long && now - ((Long) prev).longValue() < 30000L) return false;
  return RUNNING.replace(u, prev, mine);
}""")
M(ps, r"""
public void say(String text) {
  try { if (this.pr != null) this.pr.sendMessage(@MSG@.raw(text).color("%s")); } catch (Throwable t) { }
}""" % SUI.STATUS["="])
# the plate put back: a levelled mob gets its CURRENT level plate (a /mobs set or a format change during the test), else the old plate
M(ps, r"""
public void run() {
  boolean done = true;
  try {
    if (!this.onWorld) { this.onWorld = true; this.world.execute(this); done = false; return; }
    this.onWorld = false;
    @EST@ es = this.world.getEntityStore();
    @REF@ r = es == null ? null : es.getRefFromUUID(this.uuid);
    @ST@ st = es == null ? null : es.getStore();
    if (r == null || !r.isValid() || st == null) { say("[Mobs] Plate test stopped: the mob is gone (died or unloaded)."); return; }
    if (this.idx < this.texts.length) {
      @PKG@.MobLevel.setPlate(null, st, r, this.texts[this.idx]);
      this.idx++;
      @HSV@.SCHEDULED_EXECUTOR.schedule(this, 3L, java.util.concurrent.TimeUnit.SECONDS);
      done = false;
      return;
    }
    Object o = @PKG@.MobLevel.MOBS.get(this.uuid);
    if (o instanceof @PKG@.MobInfo && !"off".equals(@PKG@.MobCfg.PLATE_MODE))
      @PKG@.MobLevel.setPlate(null, st, r, @PKG@.MobLevel.plateText(((@PKG@.MobInfo) o).level, ((@PKG@.MobInfo) o).name));
    else if (this.orig != null) @PKG@.MobLevel.setPlate(null, st, r, this.orig);
    else @PKG@.MobLevel.dropPlate(null, st, r, false);
    say("[Mobs] Plate test done on " + this.label + " - its nameplate is back.");
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("platetest", "plate test failed: " + t); }
  finally { if (done && this.uuid != null) RUNNING.remove(this.uuid); }
}""")

# ---------------------------------------------------------------- MobScanTask: one WARN when another mob-scaling plugin runs (plan risk 3)
SCALERS = ["com.ziggfreed.mmomobscaling.MobScalingPlugin", "com.airijko.endlessleveling.EndlessLeveling",
           "org.zuxaw.plugin.RPGLevelingPlugin", "com.zbeve.endlesselitemobs.EndlessEliteMobs", "com.pedrijoe.difficulty.Difficulty"]
sc.addInterface(pool.get("java.lang.Runnable"))
C(sc, "public MobScanTask() { }")
M(sc, r"""
public void run() {
  try {
    String[] known = new String[] { %s };
    java.util.List ps = @PMGR@.get().getPlugins();
    for (int i = 0; ps != null && i < ps.size(); i++) {
      Object p = ps.get(i);
      String cn = p == null ? "" : p.getClass().getName();
      for (int k = 0; k < known.length; k++) {
        if (known[k].equals(cn)) @PKG@.MobLog.warn("another mob scaling mod is running (" + cn + "): mob health / damage multipliers stack and nameplates fight - keep one of them");
      }
    }
  } catch (Throwable t) { }
}""" % ", ".join(jstr(s) for s in SCALERS))

# ---------------------------------------------------------------- MobPruneTask (review F6): every 5 minutes on the scheduler thread
# world == null: forget the mobs of removed worlds, then hand each loaded world with levelled mobs a world-thread check (world set)
pt.addInterface(pool.get("java.lang.Runnable"))
F(pt, "public @WLD@ world;")
C(pt, "public MobPruneTask(@WLD@ world) { this.world = world; }")
M(pt, r"""
public void run() {
  try {
    long now = System.currentTimeMillis();
    if (this.world != null) {
      int k = @PKG@.MobLevel.pruneWorld(this.world, now);
      if (k > 0) @PKG@.MobLog.info("forgot " + k + " levelled mobs that are gone from world " + this.world.getName());
      return;
    }
    java.util.ArrayList live = @PKG@.MobLevel.liveWorlds();
    if (live == null) return;
    int n = @PKG@.MobLevel.pruneWith(live, @PKG@.MobLevel.namesOf(live), now);
    if (n > 0) @PKG@.MobLog.info("forgot " + n + " levelled mobs of worlds that were removed");
    for (int i = 0; i < live.size(); i++) {
      Object o = live.get(i);
      if (o instanceof @WLD@ && @PKG@.MobLevel.hasMobsIn(o)) ((@WLD@) o).execute(new @PKG@.MobPruneTask((@WLD@) o));
    }
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("prune", "the prune of gone mobs failed: " + t); }
}""")

# ---------------------------------------------------------------- MobHooks: config kit check= hooks
M(mh, r"""
public static String checkFormat(String key, String value) {
  if (value == null) return null;
  if (value.indexOf("{level}") < 0) return "The nameplate text must hold {level}.";
  if (value.trim().length() == 0) return "The nameplate text cannot be empty.";
  return null;
}""")
M(mh, r"""
public static String checkColor(String key, String value) {
  int i = key == null ? -1 : key.indexOf('[');
  String e = (i >= 0 && key.endsWith("]")) ? key.substring(i + 1, key.length() - 1) : "";
  try { int lvl = Integer.parseInt(e.trim()); if (lvl < 1 || lvl > 1000) return "The entry must be a level from 1 to 1000."; }
  catch (Throwable t) { return "The entry must be the lowest level of the band, like 20."; }
  if (value == null) return null;
  if (!value.trim().toLowerCase().matches("#[0-9a-f]{6}")) return "The colour must look like #ff6b6b.";
  return null;
}""")
M(mh, r"""
public static String checkBand(String key, String value) {
  if (value == null) return null;
  String[] p = value.split("\\|");
  try {
    int a = Integer.parseInt(p[0].trim()), b = p.length > 1 ? Integer.parseInt(p[1].trim()) : a;
    if (a > b) return "Min must not be above Max.";
    if (a == 0 && b != 0) return "Use 0-0 for no levels, or a Min of 1 or more.";
  } catch (Throwable t) { return "Type whole numbers."; }
  return null;
}""")

# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)
for _s in SUI.java_status_methods():
    M(mc, _s)
M(mc, r"""
public static void tell(@PR@ p, String res) {
  if (p == null || res == null || res.length() == 0) return;
  try { p.sendMessage(@MSG@.raw(textOf(res)).color(colorOf(res))); } catch (Throwable t) { }
}""")
M(mc, r"""
public static void tellAll(@PR@ p, String[] lines) {
  for (int i = 0; lines != null && i < lines.length; i++) tell(p, lines[i]);
}""")
M(mc, r"""
public static String spaced(String s) { return s == null ? "" : s.replace('_', ' '); }""")
M(mc, r"""
public static String bandText(int a, int b, int bonus) {
  int max = @PKG@.MobCfg.MAX_LEVEL;
  int x = Math.min(a + bonus, max), y = Math.min(b + bonus, max);
  return x == y ? "Lv " + x : "Lv " + x + "-" + y;
}""")
M(mc, r"""
public static String zoneText(String region, String env, String zn) {
  String z = @PKG@.MobLevel.zoneOfRegion(region);
  if (z == null) z = @PKG@.MobLevel.zoneOfEnv(env);
  if (z == null) return null;
  String t = "Zone " + z.substring(4);
  String n = zn == null ? null : @PKG@.MobLevel.i18n("server.map.zone." + zn);
  if (n == null && zn != null) n = spaced(zn);
  return n == null ? t : t + " " + n;
}""")
# where the band comes from, for players
M(mc, r"""
public static String whereText(Object[] r, String wn) {
  String step = (String) r[3];
  if ("world".equals(step)) return "this world's band";
  if ("island".equals(step)) return "private island";
  String region = (String) r[5], biome = (String) r[6], env = (String) r[8], zn = (String) r[9];
  String zt = zoneText(region, env, zn);
  StringBuilder sb = new StringBuilder();
  if (zt != null) sb.append(zt);
  if (region != null) {
    String rn = @PKG@.MobLevel.i18n("server.map.region." + region);
    if (sb.length() > 0) sb.append(" - ");
    sb.append(rn == null ? spaced(region) : rn);
  }
  if ("lava".equals(step)) { if (sb.length() > 0) sb.append(" - "); sb.append("lava cave: the zone's hardest band"); }
  else if (biome != null && region != null) sb.append(" - ").append(spaced(biome));
  if ("env".equals(step) && env != null) { if (sb.length() > 0) sb.append(" - "); sb.append(spaced(env.startsWith("Env_") ? env.substring(4) : env)); }
  int bonus = ((Integer) r[2]).intValue();
  if (bonus != 0 && env != null) sb.append(" - ").append(spaced(env.startsWith("Env_") ? env.substring(4) : env)).append(" +").append(bonus);
  return sb.length() == 0 ? step : sb.toString();
}""")
M(mc, r"""
public static String skillLine(java.util.UUID u, int lo, int hi) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object cs = b.get("class:skill:" + u);
    Object f = b.get("skill:fn:level");
    if (!(cs instanceof String) || ((String) cs).length() == 0 || !(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, cs });
    if (!(r instanceof Number)) return null;
    int l = ((Number) r).intValue();
    if (l < 0) l = 0;
    String s = "=Your " + cs + " is " + l + ": ";
    if (hi < l) { int x = l - hi, y = l - lo; return s + "these mobs are " + (x == y ? x + "" : x + " to " + y) + " levels below you."; }
    if (lo > l) { int x = lo - l, y = hi - l; return s + "these mobs are " + (x == y ? x + "" : x + " to " + y) + " levels above you."; }
    return s + "your level is inside this range.";
  } catch (Throwable t) { return null; }
}""")
M(mc, r"""
public static String[] infoLines(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world) {
  @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
  if (tc == null || tc.getPosition() == null) return new String[] { "-[Mobs] Could not read where you stand." };
  if (!@PKG@.MobCfg.ON || !@PKG@.MobLevel.HOOK) return new String[] { "=[Mobs] Mob levels are switched off on this server." };
  @VEC@ p = tc.getPosition();
  Object[] r = @PKG@.MobLevel.lookupAt(world, p.x, p.y, p.z, Integer.MIN_VALUE);
  int a = ((Integer) r[0]).intValue(), b = ((Integer) r[1]).intValue(), bonus = ((Integer) r[2]).intValue();
  String wn = world == null ? "" : world.getName();
  if (a <= 0 && b <= 0) return new String[] { "=[Mobs] Mobs here get no level (" + ("world".equals(r[3]) ? "this world has no levels" : "no band for this place") + ")." };
  if (a <= 0) a = 1;
  String first = "=[Mobs] Mobs here: " + bandText(a, b, bonus) + " (" + whereText(r, wn) + ").";
  String second = skillLine(pr.getUuid(), Math.min(a + bonus, @PKG@.MobCfg.MAX_LEVEL), Math.min(b + bonus, @PKG@.MobCfg.MAX_LEVEL));
  return second == null ? new String[] { first } : new String[] { first, second };
}""")
# the mob an admin means: the entity they look at, else the nearest levelled mob within 8 blocks
M(mc, r"""
public static @REF@ target(@ST@ store, @REF@ ref, @WLD@ world) {
  try {
    @REF@ t = @TGT@.getTargetEntity(ref, store);
    if (t != null && t.isValid() && store.getComponent(t, @NPCE@.getComponentType()) != null) return t;
  } catch (Throwable e) { }
  @TC@ me = (@TC@) store.getComponent(ref, @TC@.getComponentType());
  if (me == null || me.getPosition() == null || world == null) return null;
  @VEC@ mp = me.getPosition();
  String wn = world.getName();
  @EST@ es = (@EST@) store.getExternalData();
  @REF@ best = null;
  double bd = 64.0;
  java.util.Iterator it = @PKG@.MobLevel.MOBS.values().iterator();
  while (it.hasNext()) {
    @PKG@.MobInfo i = (@PKG@.MobInfo) it.next();
    if (i == null || !wn.equals(i.world)) continue;
    @REF@ r = es.getRefFromUUID(i.uuid);
    if (r == null || !r.isValid()) continue;
    @TC@ tc = (@TC@) store.getComponent(r, @TC@.getComponentType());
    if (tc == null || tc.getPosition() == null) continue;
    @VEC@ q = tc.getPosition();
    double dx = q.x - mp.x, dy = q.y - mp.y, dz = q.z - mp.z;
    double d = dx * dx + dy * dy + dz * dz;
    if (d <= bd) { bd = d; best = r; }
  }
  return best;
}""")
M(mc, r"""
public static String f2(float v) {
  String s = String.valueOf(Math.round(v * 100.0f) / 100.0);
  if (s.endsWith(".0")) s = s.substring(0, s.length() - 2);
  return s;
}""")
M(mc, r"""
public static String[] inspect(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world) {
  @REF@ t = target(store, ref, world);
  if (t == null) return new String[] { "-[Mobs] Look at a mob (or stand within 8 blocks of a levelled one), then try again." };
  @NPCE@ npc = (@NPCE@) store.getComponent(t, @NPCE@.getComponentType());
  if (npc == null) return new String[] { "-[Mobs] That is not a mob." };
  @UUIDC@ uc = (@UUIDC@) store.getComponent(t, @UUIDC@.getComponentType());
  java.util.UUID u = uc == null ? null : uc.getUuid();
  @ESM@ m = (@ESM@) store.getComponent(t, @ESM@.getComponentType());
  int hi = @DST@.getHealth();
  String role = npc.getRoleName();
  String name = @PKG@.MobLevel.nameOf(role, @PKG@.MobLevel.tkeyOf(npc));
  int saved = @PKG@.MobLevel.savedLevel(m, hi);
  @PKG@.MobInfo info = u == null ? null : (@PKG@.MobInfo) @PKG@.MobLevel.MOBS.get(u);
  String att = @PKG@.MobLevel.attitudeOf(null, store, t);
  String no = @PKG@.MobCfg.whyNot(att, role);
  java.util.ArrayList L = new java.util.ArrayList();
  int level = info != null ? info.level : saved;
  L.add("=[Mobs] " + name + " (" + role + ") - " + (level > 0 ? "Lv " + level : "no level") + (no == null ? "" : " - gets no level: " + no));
  if (level > 0) L.add("=Saved: " + (saved > 0 ? "on the mob (health modifier " + @PKG@.MobLevel.keyOf(saved) + ")" : "NOT on the mob")
      + (info != null ? "; this run: step " + info.step + (info.key == null ? "" : " " + info.key) : ""));
  Object[] r = @PKG@.MobLevel.lookupMob(world, npc, null, store, t);
  if (r != null) {
    int a = ((Integer) r[0]).intValue(), b = ((Integer) r[1]).intValue(), bonus = ((Integer) r[2]).intValue();
    String band = (a <= 0 && b <= 0) ? "no level" : bandText(Math.max(a, 1), b, bonus) + (bonus != 0 ? " (band " + a + "-" + b + " +" + bonus + ")" : "");
    L.add("=Lookup now: step " + r[3] + " " + r[4] + " -> " + band);
    L.add("=Place: region " + r[5] + ", biome " + r[6] + (r[7] != null && !String.valueOf(r[7]).equals(String.valueOf(r[6])) ? " (land " + r[7] + ")" : "") + ", env " + r[8] + (("1".equals(r[11])) ? ", private island" : "") + ("1".equals(r[10]) ? "" : ", no classic worldgen"));
  }
  @ESV@ hv = m == null ? null : m.get(hi);
  if (level > 0) L.add("=Health x" + f2(@PKG@.MobCfg.hpMult(level)) + (hv == null ? "" : " (" + Math.round(hv.get()) + " / " + Math.round(hv.getMax()) + " HP)") + ", damage x" + f2(@PKG@.MobCfg.dmgMult(level)) + " - " + @PKG@.MobCfg.difficultyText() + ", caps x" + f2((float) @PKG@.MobCfg.HP_CAP) + " / x" + f2((float) @PKG@.MobCfg.DMG_CAP));
  String plate = @PKG@.MobLevel.plateOf(null, store, t);
  L.add("=Plate: " + (plate == null ? "none" : plate) + " - attitude " + (att.length() == 0 ? "unknown" : att));
  if (!@PKG@.MobLevel.HOOK) L.add("-The level hook is NOT running this start (see the ERROR in the server log): no mob gets a level.");
  String[] out = new String[L.size()];
  for (int i = 0; i < out.length; i++) out[i] = (String) L.get(i);
  return out;
}""")
M(mc, r"""
public static String set(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world, String typed) {
  int lvl;
  try { lvl = Integer.parseInt(typed == null ? "" : typed.trim()); } catch (Throwable e) { lvl = -1; }
  if (lvl < 0 || lvl > @PKG@.MobCfg.MAX_LEVEL) return "-[Mobs] Type a level from 0 to " + @PKG@.MobCfg.MAX_LEVEL + " (0 removes the level).";
  @REF@ t = target(store, ref, world);
  if (t == null) return "-[Mobs] Look at a mob (or stand within 8 blocks of a levelled one), then try again.";
  @NPCE@ npc = (@NPCE@) store.getComponent(t, @NPCE@.getComponentType());
  @ESM@ m = (@ESM@) store.getComponent(t, @ESM@.getComponentType());
  @UUIDC@ uc = (@UUIDC@) store.getComponent(t, @UUIDC@.getComponentType());
  if (npc == null || m == null || uc == null) return "-[Mobs] That is not a mob with health.";
  String role = npc.getRoleName();
  String name = @PKG@.MobLevel.nameOf(role, @PKG@.MobLevel.tkeyOf(npc));
  if (lvl == 0) {
    @PKG@.MobLevel.strip(null, store, t, m, uc.getUuid());
    return "+[Mobs] Removed the level from " + name + ".";
  }
  @PKG@.MobLevel.apply(null, store, t, npc, m, uc.getUuid(), world, world == null ? "" : world.getName(), role, lvl, false, "set", null);
  String no = @PKG@.MobCfg.whyNot(@PKG@.MobLevel.attitudeOf(null, store, t), role);
  return "+[Mobs] " + name + " is now Lv " + lvl + " (health x" + f2(@PKG@.MobCfg.hpMult(lvl)) + ", damage x" + f2(@PKG@.MobCfg.dmgMult(lvl)) + ")."
      + (no == null ? "" : " It is not in the level lists (" + no + "), so it loses the level when it reloads.");
}""")
M(mc, r"""
public static String[] plateTest(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world) {
  @REF@ t = target(store, ref, world);
  if (t == null) return new String[] { "-[Mobs] Look at a mob first, then run /mobs platetest." };
  @NPCE@ npc = (@NPCE@) store.getComponent(t, @NPCE@.getComponentType());
  @UUIDC@ uc = (@UUIDC@) store.getComponent(t, @UUIDC@.getComponentType());
  if (npc == null || uc == null) return new String[] { "-[Mobs] That is not a mob." };
  String role = npc.getRoleName();
  String name = @PKG@.MobLevel.nameOf(role, @PKG@.MobLevel.tkeyOf(npc));
  @PKG@.MobInfo info = (@PKG@.MobInfo) @PKG@.MobLevel.MOBS.get(uc.getUuid());
  int lvl = info == null ? 9 : info.level;
  String f = @PKG@.MobCfg.FORMAT == null ? "[Lv {level}] {name}" : @PKG@.MobCfg.FORMAT;
  String base = f.replace("{level}", String.valueOf(lvl)).replace("{name}", name).trim();
  String red = "%s";
  String[] steps = new String[] { "1: " + @PKG@.MobLevel.markup(base, red, "tag"), "2: " + @PKG@.MobLevel.markup(base, red, "section"),
                                  "3: " + @PKG@.MobLevel.markup(base, red, "brace") };
  if (!@PKG@.MobPlateStep.claim(uc.getUuid(), System.currentTimeMillis()))
    return new String[] { "-[Mobs] A plate test is already running on this mob - wait for it to finish (9 s)." };
  String orig = @PKG@.MobLevel.plateOf(null, store, t);
  @PKG@.MobPlateStep s = new @PKG@.MobPlateStep(world, uc.getUuid(), steps, pr, orig, name);
  s.onWorld = true;
  s.run();
  return new String[] { "=[Mobs] Plate test on " + name + ": watch its nameplate, 3 s each - 1 = color tag, 2 = section sign code, 3 = brace token.",
                        "=The step whose text turns RED with no code letters is the markup the client draws. Then Server Setup > Mobs > Nameplate: Colour markup = that number, Colour by level ON." };
}""" % TEST_RED)
M(mc, r"""
public static String reload(java.util.UUID who, String name) {
  if (who == null) return "-[Mobs] Could not tell who sent this command - nothing was changed.";
  Object o = null;
  try { o = new @PKG@.CfgFn().apply(new Object[] { "reload", who, name, "command" }); } catch (Throwable t) { o = null; }
  if (!(o instanceof Object[]) || ((Object[]) o).length < 3) return "-[Mobs] The settings could not be re-read - see the server log.";
  Object[] r = (Object[]) o;
  if ("ok".equals(r[0])) return "+[Mobs] config.properties + bands.properties: " + r[2] + " New spawns use the new values.";
  return "-[Mobs] " + r[2];
}""")

# ================================================================= commands
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []


def cmd(clsname, name, desc, args, body, perm="@ADV@", subs=()):
    """One AbstractPlayerCommand. args = [(field, argName, argDesc, "STRING")], read into a0, a1, ..."""
    c = pool.makeClass(PKG + "." + clsname, pool.get(T["APC"]))
    for (fld, _an, _ad, _ty) in args:
        F(c, "public @RA@ %s;" % fld)
    lines = ['super("%s", "%s");' % (name, desc), perm]
    for (fld, an, ad, ty) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.%s);' % (fld, an, ad, ty))
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    C(c, "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines)))
    reads = "".join('    String a%d = String.valueOf(ctx.get(this.%s));\n' % (i, a[0]) for i, a in enumerate(args))
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.MobLog.warn(\"/mobs " + name + " failed: \" + t);\n"
      "    @PKG@.MobCmds.tell(pr, \"-[Mobs] Something went wrong - the server log has the details.\");\n  }\n}")
    CMDS.append(c)
    return c


X = "@PKG@.MobCmds."
A = "@ADMIN@"
cmd("MobsInfoCmd", "info", "The mob level band where you stand", [], X + "tellAll(pr, " + X + "infoLines(pr, store, ref, world));")
cmd("MobsInspectCmd", "inspect", "Admin: level, lookup step and band of the mob you look at", [],
    X + "tellAll(pr, " + X + "inspect(pr, store, ref, world));", perm=A)
cmd("MobsSetCmd", "set", "Admin: set the level of the mob you look at (0 removes it)",
    [("levelArg", "level", "Level (0 = remove)", "STRING")], X + "tell(pr, " + X + "set(pr, store, ref, world, a0));", perm=A)
cmd("MobsPlateCmd", "platetest", "Admin: show the three nameplate colour markups on the mob you look at", [],
    X + "tellAll(pr, " + X + "plateTest(pr, store, ref, world));", perm=A)
cmd("MobsReloadCmd", "reload", "Admin: re-read config.properties and bands.properties", [],
    X + "tell(pr, " + X + "reload(pr.getUuid(), pr.getUsername()));", perm=A)
cmd("MobsCmd", "mobs", "Mob levels: /mobs shows the level band where you stand", [],
    X + "tellAll(pr, " + X + "infoLines(pr, store, ref, world));",
    subs=("MobsInfoCmd", "MobsInspectCmd", "MobsSetCmd", "MobsPlateCmd", "MobsReloadCmd"))

# ================================================================= plugin
C(pl, "public SkyyMobsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public static Class cls(String n) {
  try { return Class.forName(n); } catch (Throwable t) { return null; }
}""")
M(pl, r"""
public void systems() {
  @PKG@.LevelHook.RBS = cls("%s");
  @PKG@.LevelHook.SETUP = cls("%s");
  @PKG@.LevelHook.BAL = cls("%s");
  @PKG@.LevelDamage.ADR = cls("%s");
  try { getEntityStoreRegistry().registerSystem(new @PKG@.LevelHook(true)); @PKG@.MobLevel.HOOK = true; }
  catch (Throwable t1) {
    @PKG@.MobLevel.HOOK = false;
    @PKG@.MobLog.error("the level hook could not be ordered after the NPC setup systems (" + t1 + ") - NO mob gets a level this start. "
        + "There is no unordered fallback on purpose: it could run before a mob's role and stats exist and strip saved levels. "
        + "Mobs keep the levels saved on them; /mobs inspect shows this too. Please report it with this log.");
  }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.LevelDamage(true)); }
  catch (Throwable t3) {
    @PKG@.MobLog.warn("could not order the level damage before armour (" + t3 + ") - unordered fallback: this start a levelled mob's damage may be scaled after armour instead of before");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.LevelDamageU()); } catch (Throwable t4) { @PKG@.MobLog.warn("the level damage could not be registered: " + t4 + " - mobs deal vanilla damage this start"); }
  }
}""" % (ROLEB, SETUPS, BALS, ADRS))
M(pl, r"""
public void setup() {
  @PKG@.MobLog.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyMobs");
  @PKG@.MobCfg.DIR = dir;
  @PKG@.MobCfg.FILE = dir.resolve("config.properties");
  @PKG@.MobCfg.BANDS = dir.resolve("bands.properties");
  @PKG@.MobCfg.load();
  systems();
  getCommandRegistry().registerCommand(new @PKG@.MobsCmd());
  @PKG@.MobLevel.bridge().put("mob:fn:level", new @PKG@.MobLevelFn());
  @PKG@.MobLog.info("@VERSION@ ready (@KITID@) - levels " + (!@PKG@.MobLevel.HOOK ? "NOT RUNNING (level hook missing, see the error above)" : @PKG@.MobCfg.ON ? "on" : "OFF") + ", " + @PKG@.MobCfg.difficultyText() + ", " + @PKG@.MobCfg.LOADED + "; plates " + @PKG@.MobCfg.PLATE_MODE + " '" + @PKG@.MobCfg.FORMAT + "' (colours " + (@PKG@.MobCfg.COLOR_ON ? @PKG@.MobCfg.MARKUP : "off") + "); /mobs; settings in Server Setup > Mobs; data in " + dir);
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.MobScanTask(), 15L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { }
  try { @PKG@.MobLevel.PRUNE = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.MobPruneTask(null), 300L, 300L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.MobLog.warn("could not schedule the prune of gone mobs: " + t); }
}""")
M(pl, r"""
protected void shutdown() {
  try { java.util.concurrent.ScheduledFuture f = @PKG@.MobLevel.PRUNE; if (f != null) f.cancel(false); @PKG@.MobLevel.PRUNE = null; } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.MobLevel.bridge().remove("mob:fn:level"); } catch (Throwable t) { }
  try { @PKG@.MobLevel.clearAll(); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in ALL + CMDS + [pl]:
    c.writeFile(OUT)
kit.write(OUT)
print("classes written:", len(ALL + CMDS) + 1 + len(kit.classes), "(%d kit)" % len(kit.classes))
print("built-in roles: %d exact vanilla ids (%d chars); levels.roles (extra) default %r; levels.exclude: %d chars; %d biome rows, %d env rows, "
      "%d zone rows" % (len(LEVELLED), len(LEVELLED_TEXT), ROLES_DEF, len(EXCLUDE_DEF), len(BIOME_ROWS), len(ENV_ROWS), len(ZONE_ROWS)))

jar = os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)
man = B.manifest(MOD, VERSION, "SkyWynn mob levels: every hostile mob and neutral fighter gets a level from the zone / biome it spawns in "
                 "(Zone 1 Lv 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60), more health and damage per level with a difficulty "
                 "setting, a [Lv 9] nameplate, /mobs, mob:fn:level bridge. Settings in game (Server Setup > Mobs). Zero dependencies.",
                 PKG + ".SkyyMobsPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
