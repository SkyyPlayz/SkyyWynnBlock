"""Derive SkyyClasses/build_skyyclasses_0.1.7.py from the EDITED 0.1.6 script (run: python tools/classes_0_1_7_patch.py, then build the
0.1.7 script). EDITED-SCRIPTS RULE (commit ab75b6c): Skyy edited build_skyyclasses_0.1.6.py by hand (priestHeal.feedbackMs 10000, locked
comments); that edited file is the source here and tools/classes_0_1_6_patch.py is NEVER re-run (it would throw Skyy's edits away).
The edited 0.1.6 compiled as-is and passed SkyyClasses/test_skyyclasses_0.1.6.py (282 checks) - no kit-limit fix was needed.

Skyy's locks (OPEN-QUESTIONS.md "Berserker, Priest, class kits" + "In-game server setup" 3 and 13; research/Classes-Berserker-Priest-Spec.md):
 1. CLASS KITS straight into the HOTBAR, immediately (was: storage, ~31 s after a new profile arrived):
    - Kit.consider (2 s ClassTick) no longer waits 31 s after a profile:epoch change nor 3 s in one world; the maps KITEP / KITARR and
      the EPOCH_WAIT_MS / SAME_WORLD_MS fields are gone. KitNewFn (SkyyProfiles Create Profile) and /classadmin set schedule KitSoon
      ~0.3 s later (KIT_SOON_MS): by then SkyyProfiles' createAndSwitch has finished its switch on the same world thread, and the KitTask
      is queued BEHIND it on that thread. The "on its way" chat line is gone (the kit arrives before it would matter).
    - Kit.put / Kit.room take a 'where': 0 = the hotbar only (automatic kits, /classadmin kit and - review fix - the quiet arrival
      retry of owed items, KitTask mode 2 ~3 s after every world arrival), 1 = hotbar then storage (Inventory.getCombinedHotbarFirst =
      hotbar + storage, verified in InventoryComponent.setupCombined; used by an explicit /class kit claim and the arrows). What does
      not fit the hotbar becomes the claim (kit=owed) and only /class kit puts it into storage = "overflow waits on /class kit". Texts
      say hotbar.
    - Unchanged: only a pending flag gives automatically (never a duplicate: kit= per profile, kitBegin writes kit=given + the in-flight
      list BEFORE any item moves), /profileadmin setclass never marks a kit (syncKey), busy / pkey / ready / alive re-checked on the
      world thread, Archer kit 64 arrows.
    - Known limit (the price of "immediately", accepted by the lock): SkyyProfiles keeps its crash marker 30 s after a switch; a server
      CRASH inside that window rolls the new profile back to its empty snapshot, so a kit handed out in those seconds is lost (never
      doubled). /classadmin info still says "kit given"; an admin re-gives it with /classadmin kit.
 2. Weapon_Deployable_Healing_Totem = PRIEST weapon (rule table + 4th Priest icon + weapon text). The weapon lock only judges damage and
    a totem heals, so a new DeployGuard (RefSystem on the engine's DeployableComponent, AddReason.SPAWN) looks up the deployable's config
    id (build-time table from Assets.zip: item -> Projectile config -> SpawnDeployable* Config.Id = "Healing_Totem"), resolves the
    thrower (DeployableComponent.getOwner -> PlayerRef, else getOwnerUUID -> ShotTrack launch record -> shooter), and when
    thrower is not the item's owner class (review fix: judged STRICTLY by DeployGuard.judge - Priest and Priest playable; NOT
    ClassRules.allowed, which lets a classless player through while requireClass is off; a class file that cannot be read = keep + one
    log line, never a removal on a guess) it removes the deployable (CommandBuffer.removeEntity, the engine's own remove-on-add pattern)
    and sends the weapon-lock chat line + popup ("Only Priests can use healing totems..."; classless: "... - create a Priest profile with
    /profiles." / "choose Priest with /class."). The totem item is never consumed (10 s cooldown, MaxStack 1, no consume step in its
    JSON), so nothing is lost. Slowness Totem + Turret stay unassigned and unjudged (unchanged).
 3. Heal chat lines at most every 10 s: Skyy's edited default (DEF_HEAL_MSG_MS = 10000) - kept as is.
 4. Self-heal HP to SkyySkills: HealTask.xpSelf = the exact round-9 call apply(new Object[] { u, Double.valueOf(hpOnSelf),
    "classes:heal:self", ClassCfg.pkey(u), Boolean.TRUE }). Heals on others keep the 4-element call. Deploy with SkyySkills 0.4.6+
    (0.4.5 ignores the flag and pays the others rate).
 5. DAILY ARCHER ARROWS: /class arrows (player sub-command, hytale:Adventurer). An Archer profile claims arrows.amount x arrows.item
    (default 64 Weapon_Arrow_Crude) once per arrows.cooldownHours (24) - rolling, per profile, on disk in players/<pkey>.properties
    (arrowsAt, arrowsN, arrowsFly = in-flight record, arrowsOwed = what did not fit). Order: every check -> synchronized arrowsBegin
    (re-checks owed + cooldown under ClassStore's lock, writes arrowsAt + arrowsFly BEFORE items move) -> put (hotbar then storage) ->
    arrowsEnd (drops arrowsFly, the remainder becomes arrowsOwed). Owed arrows are collected by the next /class arrows (no class /
    cooldown / on-off check: they are the player's). Relog / profile switch / double command cannot claim twice (disk + one pkey per
    command on the world thread + the lock); a crash between begin and end loses rather than doubles. Nothing fits at all -> refused
    before anything is written (the refill waits). Config rows (new category 'Archer arrows'): arrows.enabled (part switch),
    arrows.item (items, exactly 1; check= asks when it is not a Weapon_Arrow_), arrows.amount (1-9999), arrows.cooldownHours (1-168 h).
    /classadmin info shows the arrow state. The Archer kit message mentions /class arrows.
 6. Server Setup: switchCost + cooldownMinutes shown GREYED OUT = kit 1.1 read-only rows ('ro', custom:ClassHooks with no file key - the
    SkyyCollections 0.2.3 Magic Bags pattern), live values from ClassCfg (still read by load / loadInert), never writable, never
    exported. Config history KEEP=10 (was 20).
Build + lint + python SkyyClasses/test_skyyclasses_0.1.7.py (bare JVM).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.6.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.7.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
# the source must be Skyy's EDITED 0.1.6 (commit ab75b6c), never a regenerated one
assert "DEF_HEAL_MSG_MS = 10000   # LOCKED Skyy 2026-09-25" in s, "build_skyyclasses_0.1.6.py is not the edited script (ab75b6c)"


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


# ================================================================================================================ docstring + version
rep('''"""SkyyClasses 0.1.6 - build script (javassist via jpype; derived from 0.1.5 by tools/classes_0_1_6_patch.py - edit the patch, not this
file). Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.7 - build script (javassist via jpype; derived from the EDITED 0.1.6 script by tools/classes_0_1_7_patch.py - edit the
patch, not this file; classes_0_1_6_patch.py is never re-run). Wynncraft-style classes for SkyWynn.
0.1.7 (Skyy's 2026-09-25 locks, commit ab75b6c; OPEN-QUESTIONS.md + research/Classes-Berserker-Priest-Spec.md). Notes in the patch.
  - CLASS KITS straight into the HOTBAR, immediately: a class pick (SkyyProfiles Create Profile -> class:fn:kitnew, the own picker,
    /classadmin set on a classless file) tries the kit ~0.3 s later, then every 2 s - no 31 s epoch wait, no 3 s same-world wait. The
    automatic kit (and /classadmin kit) fills the 9 hotbar slots only; what does not fit waits as a claim for /class kit (hotbar first,
    then storage; the automatic retry at each world arrival fills the hotbar only). /profileadmin setclass still hands out nothing; one
    kit per profile (kit= flag, written first).
  - Weapon_Deployable_Healing_Totem is a PRIEST weapon: DeployGuard removes the totem of anyone who is not a Priest (players without a
    class too) the moment it lands and sends the weapon-lock chat line + popup (the totem item is never used up).
  - Priest heal: HP a Priest heals on themself goes to SkyySkills too (skill:fn:healxp with a trailing Boolean.TRUE = the self rate,
    SkyySkills 0.4.6+). Heals on others unchanged. Heal chat lines every 10 s (Skyy's edited default).
  - DAILY ARCHER ARROWS: /class arrows - an Archer profile claims 64 Crude Arrows once every 24 h (Server Setup -> Classes -> Archer
    arrows: on/off, item, amount, hours); hotbar then storage, the rest waits for the next /class arrows. Never twice (per profile on
    disk, written before the arrows move).
  - Server Setup: switchCost + cooldownMinutes shown greyed out (read-only) while class switching is off; config history keeps 10.
''')
rep("Run:   python build_skyyclasses_0.1.6.py            -> SkyyClasses/SkyyClasses-0.1.6.jar",
    "Run:   python build_skyyclasses_0.1.7.py            -> SkyyClasses/SkyyClasses-0.1.7.jar")
rep("Player: /class, 0.1.6 /class kit (collect kit items that did not fit).",
    "Player: /class, 0.1.6 /class kit (collect kit items that did not fit), 0.1.7 /class arrows (the daily Archer arrow refill).")
rep('''      kitClaimAt), Skyy_SkyyClasses/kits.properties (0.1.6: written once by the 'picked before kits' migration),''',
    '''      kitClaimAt; 0.1.7 arrowsAt, arrowsN, arrowsFly, arrowsOwed), Skyy_SkyyClasses/kits.properties (0.1.6: written once by the
      'picked before kits' migration),''')
rep('''    (DeployableTurretConfig / DeployableAoeConfig build EntitySource(deployable)) -> the class lock does not judge them.''',
    '''    (DeployableTurretConfig / DeployableAoeConfig build EntitySource(deployable)) -> the class lock does not judge them.
    0.1.7: a CLASS-owned deployable (the Healing Totem = Priest) is judged when it spawns instead (DeployGuard: removed + the lock line).''')
rep('''    mark its kit pending (SkyyProfiles 0.1.2 Create Profile). Reads party:fn:members, skill:fn:healxp (0.1.6).''',
    '''    mark its kit pending (SkyyProfiles 0.1.2 Create Profile). Reads party:fn:members, skill:fn:healxp (0.1.6; 0.1.7 also sends the
    Priest's self-heal HP with a trailing Boolean.TRUE).''')
rep('VERSION = "0.1.6"', 'VERSION = "0.1.7"')

# ================================================================================================================ roster: Healing Totem = Priest
rep('''     "icons": ["Weapon_Wand_Wood", "Weapon_Spellbook_Grimoire_Brown", "Weapon_Spellbook_Frost"],
     "weapons": [("Weapon_Wand_", "wands"), ("Weapon_Spellbook_", "spellbooks")],
     "weapon_text": "Wands / Spellbooks", "kit": "Weapon_Wand_Wood:1"},''',
    '''     "icons": ["Weapon_Wand_Wood", "Weapon_Spellbook_Grimoire_Brown", "Weapon_Spellbook_Frost", "Weapon_Deployable_Healing_Totem"],
     # 0.1.7 (LOCKED Skyy 2026-09-25): the vanilla Healing Totem is Priest only (DeployGuard judges the thrown totem when it lands)
     "weapons": [("Weapon_Wand_", "wands"), ("Weapon_Spellbook_", "spellbooks"), ("Weapon_Deployable_Healing_Totem", "healing totems")],
     "weapon_text": "Wands / Spellbooks / Healing Totem", "kit": "Weapon_Wand_Wood:1"},''')
rep('''    # LOCKED Skyy 2026-09-25: Weapon_Deployable_Healing_Totem is Priest only. This build still leaves every deployable unassigned.''',
    '''    # 0.1.7: Weapon_Deployable_Healing_Totem is a Priest weapon (CLASSES above, the longer prefix wins). The other deployables stay here.''')

# ================================================================================================================ constants
rep('''KIT_EPOCH_WAIT_MS = 31000   # with SkyyProfiles: at least this long after the last profile:epoch change (its crash marker lives 30 s)
KIT_SAME_WORLD_MS = 3000    # ... and the player stayed this long in one world (the /island transfer after a switch is over)
''', '''KIT_SOON_MS = 300           # 0.1.7 (LOCKED Skyy 2026-09-25): a kit is tried this soon after the pick, then every 2 s - no 31 s / 3 s waits
''')
rep('''KIT_HOTBAR_ASK_MS = 60000   # "Use my hotbar": a second click this soon (same kit, same hotbar) answers the kit check's question
''', '''KIT_HOTBAR_ASK_MS = 60000   # "Use my hotbar": a second click this soon (same kit, same hotbar) answers the kit check's question
# 0.1.7 daily Archer arrow refill (LOCKED Skyy 2026-09-25: arrows only, once a day per profile) - /class arrows
DEF_ARROWS_ON = True
DEF_ARROWS_ITEM = "Weapon_Arrow_Crude"
DEF_ARROWS_AMOUNT = 64
DEF_ARROWS_HOURS = 24
ARROWS_AMOUNT_MAX = 9999
ARROWS_HOURS_MIN, ARROWS_HOURS_MAX = 1, 168
ALLOW_SWITCH = False        # design lock: no class switching -> switchCost / cooldownMinutes are greyed-out (read-only) rows
CFG_KEEP = 10               # LOCKED Skyy 2026-09-25: the config kit keeps 10 old file versions (was 20)
''')

# ================================================================================================================ build checks (totem, arrows)
rep('''    print("  %-10s %s" % (_c["name"], _c["kit"] or "(empty)"))
''', '''    print("  %-10s %s" % (_c["name"], _c["kit"] or "(empty)"))

# 0.1.7: the Healing Totem is Priest-owned, the other deployables stay unassigned
ARCHER_I = [i for i, c in enumerate(CLASSES) if c["name"] == "Archer"][0]
assert classify("Weapon_Deployable_Healing_Totem")[0] == PRIEST_I, "the Healing Totem must be a Priest weapon (LOCKED 2026-09-25)"
assert classify("Weapon_Deployable_Slowness_Totem")[0] == UNASSIGNED_OWNER and classify("Weapon_Deployable_Turret")[0] == UNASSIGNED_OWNER
# DeployGuard table: every CLASS-owned Weapon_Deployable_ item -> the deployable config id(s) its throw spawns (item Interactions ->
# "Projectile" Config -> Server/ProjectileConfigs/**/<Config>.json -> SpawnDeployable* Config.Id), read from Assets.zip
_PCFG = {}
for _n in _ASSETS.namelist():
    if _n.startswith("Server/ProjectileConfigs/") and _n.endswith(".json"):
        _PCFG[os.path.basename(_n)[:-5]] = _n
def _deploy_ids(node, seen):
    out = set()
    if isinstance(node, dict):
        _t, _cf = node.get("Type"), node.get("Config")
        if isinstance(_t, str) and _t.startswith("SpawnDeployable") and isinstance(_cf, dict) and isinstance(_cf.get("Id"), str):
            out.add(_cf["Id"])
        if _t == "Projectile" and isinstance(_cf, str) and _cf in _PCFG and _cf not in seen:
            seen.add(_cf)
            out |= _deploy_ids(json.loads(_ASSETS.read(_PCFG[_cf]).decode("utf-8-sig")), seen)
        for _v in node.values():
            out |= _deploy_ids(_v, seen)
    elif isinstance(node, list):
        for _v in node:
            out |= _deploy_ids(_v, seen)
    return out
DEPLOY_GUARD = []   # (deployable config id, item id)
for _i in _real:
    if _i.startswith("Weapon_Deployable_") and classify(_i)[0] >= 0:
        _ids = _deploy_ids(json.loads(_ASSETS.read(_ITEMS[_i]).decode("utf-8-sig")), set())
        assert _ids, "class weapon %s spawns no deployable id DeployGuard could judge" % _i
        for _d in sorted(_ids):
            DEPLOY_GUARD.append((_d, _i))
assert ("Healing_Totem", "Weapon_Deployable_Healing_Totem") in DEPLOY_GUARD, "Healing Totem deployable id changed in Assets.zip: %s" % DEPLOY_GUARD
assert len(set(d for d, _ in DEPLOY_GUARD)) == len(DEPLOY_GUARD), "one owner item per deployable id"
print("deployables judged when they land (DeployGuard): %s" % ", ".join("%s <- %s" % x for x in DEPLOY_GUARD))
# daily arrows: the default item exists, is an arrow and an Archer weapon
assert DEF_ARROWS_ITEM in _ITEMS and DEF_ARROWS_ITEM.startswith("Weapon_Arrow_") and classify(DEF_ARROWS_ITEM)[0] == ARCHER_I
assert 1 <= DEF_ARROWS_AMOUNT <= ARROWS_AMOUNT_MAX and ARROWS_HOURS_MIN <= DEF_ARROWS_HOURS <= ARROWS_HOURS_MAX
print("daily Archer arrows (default): %d x %s every %d h per profile (/class arrows)" % (DEF_ARROWS_AMOUNT, DEF_ARROWS_ITEM, DEF_ARROWS_HOURS))
''')

# ================================================================================================================ engine classes + probes
rep('''    "ITM":  "com.hypixel.hytale.server.core.asset.type.item.config.Item",
}''', '''    "ITM":  "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    # 0.1.7: DeployGuard (the built-in Deployables plugin's component + config)
    "DEPC": "com.hypixel.hytale.builtin.deployables.component.DeployableComponent",
    "DEPCFG": "com.hypixel.hytale.builtin.deployables.config.DeployableConfig",
}''')
rep('''             (T["WLD"], "execute"), (T["IS"], "getQuantity"), (T["PR"], "getReference"), (T["PR"], "getUsername")):
    B.probe(pool, c, m)
''', '''             (T["WLD"], "execute"), (T["IS"], "getQuantity"), (T["PR"], "getReference"), (T["PR"], "getUsername")):
    B.probe(pool, c, m)
# 0.1.7: hotbar-first container, DeployGuard
for c, m in ((T["INV"], "getCombinedHotbarFirst"), (T["DEPC"], "getComponentType"), (T["DEPC"], "getOwner"), (T["DEPC"], "getOwnerUUID"),
             (T["DEPC"], "getConfig"), (T["DEPCFG"], "getId"), (T["CB"], "removeEntity"), (T["REMR"], "REMOVE")):
    B.probe(pool, c, m)
''')
rep('''akit  = pool.makeClass(PKG + ".AdminKitCmd", pool.get(T["APC"]))
''', '''akit  = pool.makeClass(PKG + ".AdminKitCmd", pool.get(T["APC"]))
# 0.1.7
ksoon = pool.makeClass(PKG + ".KitSoon")                              # Runnable: one kit try right after a pick
dgd   = pool.makeClass(PKG + ".DeployGuard", pool.get(T["RSYS"]))     # Priest-only Healing Totem (judged when it lands)
arw   = pool.makeClass(PKG + ".Arrows")                               # the daily Archer arrow refill
acmd  = pool.makeClass(PKG + ".ClassArrowsCmd", pool.get(T["APC"]))   # /class arrows
''')

# ================================================================================================================ config file text
rep('''    "# switchCost and cooldownMinutes are unused while class switching is off (design lock: a new class means a new profile)",''',
    '''    "# switchCost and cooldownMinutes are unused while class switching is off (design lock: a new class means a new profile);",
    "# Server Setup shows them greyed out (read only) until class changes unlock (a quest item later)",''')
rep('''    "# LOCKED Skyy 2026-09-25: the kit drops straight into the hotbar the moment the player selects or changes class.",
    "# This build still puts it in storage about 31 s after a new profile arrives. Daily Archer arrow refill is not in this build.",''',
    '''    "# LOCKED Skyy 2026-09-25 (0.1.7): the kit drops straight into the hotbar the moment the player selects or changes class;",
    "# what does not fit the hotbar waits for /class kit. /profileadmin setclass never hands out a kit (admins use /classadmin kit).",''')
rep('''    "priestHeal.feedbackMs=%d" % DEF_HEAL_MSG_MS,
]''', '''    "priestHeal.feedbackMs=%d" % DEF_HEAL_MSG_MS,
    "# ---------- Daily Archer arrows (0.1.7, LOCKED Skyy 2026-09-25: arrows only, once a day) - Archers type /class arrows ----------",
    "# arrows.enabled = false: nobody can claim a refill (arrows still owed from an earlier refill can always be collected)",
    "arrows.enabled=%s" % str(DEF_ARROWS_ON).lower(),
    "# arrows.item = the arrow item; arrows.amount = arrows per refill (1-%d); what does not fit waits for the next /class arrows" % ARROWS_AMOUNT_MAX,
    "arrows.item=%s" % DEF_ARROWS_ITEM,
    "arrows.amount=%d" % DEF_ARROWS_AMOUNT,
    "# arrows.cooldownHours = hours between two refills of one profile (%d-%d; 24 = once a day)" % (ARROWS_HOURS_MIN, ARROWS_HOURS_MAX),
    "arrows.cooldownHours=%d" % DEF_ARROWS_HOURS,
]''')

# ================================================================================================================ ClassCfg: arrow fields + loader
rep('''F(cfg, "public static volatile long HEAL_MSG_MS = %dL;" % DEF_HEAL_MSG_MS)
''', '''F(cfg, "public static volatile long HEAL_MSG_MS = %dL;" % DEF_HEAL_MSG_MS)
# 0.1.7: daily Archer arrows (Server Setup -> Classes -> Archer arrows; arrows.* in config.properties)
F(cfg, "public static volatile boolean ARROWS_ON = %s;" % str(DEF_ARROWS_ON).lower())
F(cfg, "public static volatile String ARROWS_ITEM = %s;" % jstr(DEF_ARROWS_ITEM))
F(cfg, "public static volatile long ARROWS_AMOUNT = %dL;" % DEF_ARROWS_AMOUNT)
F(cfg, "public static volatile long ARROWS_HOURS = %dL;" % DEF_ARROWS_HOURS)
''')
rep('''M(cfg, r"""
public static String fmtNum(double x) {''', '''# 0.1.7: one plain item id (letters, digits, _ . -; no amount) - a bad hand-typed arrows.item falls back to the default
M(cfg, r"""
public static boolean itemIdOk(String id) {
  if (id == null || id.length() == 0 || id.length() > 120) return false;
  for (int i = 0; i < id.length(); i++) {
    char c = id.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '-')) return false;
  }
  return true;
}""")
M(cfg, r"""
public static String fmtNum(double x) {''')
rep('''# the 0.1.6 part of load() / summary(): "kits=on priestHeal=on healShare=25% self=50% radius=16"
M(cfg, r"""
public static String extraText() {
  return " kits=" + (@PKG@.KitCfg.ON ? "on" : "off") + " priestHeal=" + (HEAL_ON ? "on" : "off") + " healShare=" + HEAL_SHARE_PCT
    + "% self=" + HEAL_SELF_PCT + "% radius=" + fmtNum(HEAL_RADIUS);
}""")''', '''# the 0.1.6 + 0.1.7 part of load() / summary(): "kits=on priestHeal=on healShare=25% self=50% radius=16 arrows=on 64xWeapon_Arrow_Crude/24h"
M(cfg, r"""
public static String extraText() {
  return " kits=" + (@PKG@.KitCfg.ON ? "on" : "off") + " priestHeal=" + (HEAL_ON ? "on" : "off") + " healShare=" + HEAL_SHARE_PCT
    + "% self=" + HEAL_SELF_PCT + "% radius=" + fmtNum(HEAL_RADIUS)
    + " arrows=" + (ARROWS_ON ? "on" : "off") + " " + ARROWS_AMOUNT + "x" + ARROWS_ITEM + "/" + ARROWS_HOURS + "h";
}""")''')
rep('''    "__HMS__": "%dL" % DEF_HEAL_MSG_MS, "__HMSMIN__": "%dL" % HEAL_MSG_MS_MIN, "__HMSMAX__": "%dL" % HEAL_MSG_MS_MAX,
}''', '''    "__HMS__": "%dL" % DEF_HEAL_MSG_MS, "__HMSMIN__": "%dL" % HEAL_MSG_MS_MIN, "__HMSMAX__": "%dL" % HEAL_MSG_MS_MAX,
    # 0.1.7 daily arrows
    "__ARON__": str(DEF_ARROWS_ON).lower(), "__ARIT__": jstr(DEF_ARROWS_ITEM), "__ARAM__": "%dL" % DEF_ARROWS_AMOUNT,
    "__ARAMMAX__": "%dL" % ARROWS_AMOUNT_MAX, "__ARH__": "%dL" % DEF_ARROWS_HOURS, "__ARHMIN__": "%dL" % ARROWS_HOURS_MIN,
    "__ARHMAX__": "%dL" % ARROWS_HOURS_MAX,
}''')
rep('''    HEAL_MSG_MS = hms;
    return "switchCost="''', '''    HEAL_MSG_MS = hms;
    ARROWS_ON = bool(p, "arrows.enabled", __ARON__);
    String ai = txt(p, "arrows.item", __ARIT__);
    if (!itemIdOk(ai)) ai = __ARIT__;
    ARROWS_ITEM = ai;
    long aa = lng(p, "arrows.amount", __ARAM__);
    if (aa < 1L) aa = 1L;
    if (aa > __ARAMMAX__) aa = __ARAMMAX__;
    ARROWS_AMOUNT = aa;
    long ah = lng(p, "arrows.cooldownHours", __ARH__);
    if (ah < __ARHMIN__) ah = __ARHMIN__;
    if (ah > __ARHMAX__) ah = __ARHMAX__;
    ARROWS_HOURS = ah;
    return "switchCost="''')

# ================================================================================================================ Server Setup rows
rep('''# ClassHooks = the read-only 'Class switching' row (custom:, no file key: it shows ALLOW_SWITCH and can never be set, so a hand-typed
# allowSwitch line in the file can never turn paid switching back on). switchCost / cooldownMinutes are deliberately not rows.
hooks = pool.makeClass(PKG + ".ClassHooks")
M(hooks, r"""
public static String customGet(String key) {
  if ("classSwitching".equals(key)) return @PKG@.ClassCfg.ALLOW_SWITCH ? "true" : "false";
  return null;
}""")''', '''# ClassHooks = the read-only 'Class switching' row (custom:, no file key: it shows ALLOW_SWITCH and can never be set, so a hand-typed
# allowSwitch line in the file can never turn paid switching back on). 0.1.7 (LOCKED Skyy 2026-09-25): switchCost / cooldownMinutes are
# shown GREYED OUT the same way (kit 1.1 'ro' rows, custom: with no file key - the SkyyCollections 0.2.3 Magic Bags pattern): the live
# ClassCfg values (still read by load / loadInert from the file), never set, exported or restored by the kit.
hooks = pool.makeClass(PKG + ".ClassHooks")
M(hooks, r"""
public static String customGet(String key) {
  if ("classSwitching".equals(key)) return @PKG@.ClassCfg.ALLOW_SWITCH ? "true" : "false";
  if ("switchCost".equals(key)) return String.valueOf(@PKG@.ClassCfg.SWITCH_COST);
  if ("cooldownMinutes".equals(key)) return String.valueOf(@PKG@.ClassCfg.COOLDOWN_MIN);
  return null;
}""")''')
rep('''CFG_CATS = [("lock", "Weapon lock"), ("picker", "Class picker"), ("kits", "Class kits"), ("priest", "Priest heal")]   # 0.1.6: + kits, priest''',
    '''CFG_CATS = [("lock", "Weapon lock"), ("picker", "Class picker"), ("kits", "Class kits"), ("priest", "Priest heal"),   # 0.1.6: + kits, priest
            ("arrows", "Archer arrows")]                                                                                 # 0.1.7: + arrows''')
rep('''    ("classSwitching", "Class switching", "picker", "bool", "false", "", "", "", "", "ro",
     "Off (design lock): a new class means a new profile. switchCost and cooldownMinutes do nothing.",
     "custom:ClassHooks"),
]''', '''    ("classSwitching", "Class switching", "picker", "bool", "false", "", "", "", "", "ro",
     "Off (design lock): a new class means a new profile. The two switch rows below are greyed out.",
     "custom:ClassHooks"),
]
# 0.1.7 (LOCKED Skyy 2026-09-25): visible but not usable while switching is locked off. Should switching ever unlock, bind them as field rows.
assert not ALLOW_SWITCH, "switchCost / cooldownMinutes are read-only rows only while class switching is off"
CFG_ROWS += [
    ("switchCost", "Class switch cost", "picker", "int", str(DEF_SWITCH_COST), "0", "", "", "coins", "ro",
     "Greyed out while class switching is off. Class changes unlock later (a quest item).",
     "custom:ClassHooks"),
    ("cooldownMinutes", "Class switch cooldown", "picker", "int", str(DEF_COOLDOWN_MIN), "0", "", "", "min", "ro",
     "Greyed out while class switching is off. The wait between two class switches.",
     "custom:ClassHooks"),
]''')
rep('''# build check: every row bound to a config.properties key has the default the default file writes (the file and the kit agree)''',
    '''# 0.1.7 daily Archer arrows (LOCKED Skyy 2026-09-25: arrows only, once a day per profile) - /class arrows
CFG_ROWS += [
    ("arrows.enabled", "Daily arrows for Archers", "arrows", "bool", str(DEF_ARROWS_ON).lower(), "", "", "", "", "live,part,danger",
     "Archers claim free arrows with /class arrows. Off: no refills (owed arrows can still be taken).",
     "field:ClassCfg.ARROWS_ON@config.properties:arrows.enabled"),
    ("arrows.item", "Arrow item", "arrows", "items", DEF_ARROWS_ITEM, "1", "1", "", "", "live",
     "The arrow one refill gives (arrows only).",
     "field:ClassCfg.ARROWS_ITEM@config.properties:arrows.item;check=KitHooks.checkArrow"),
    ("arrows.amount", "Arrows per refill", "arrows", "int", str(DEF_ARROWS_AMOUNT), "1", str(ARROWS_AMOUNT_MAX), "", "", "live",
     "Hotbar first, then storage. What does not fit waits for the next /class arrows.",
     "field:ClassCfg.ARROWS_AMOUNT@config.properties:arrows.amount"),
    ("arrows.cooldownHours", "Hours between refills", "arrows", "int", str(DEF_ARROWS_HOURS), str(ARROWS_HOURS_MIN), str(ARROWS_HOURS_MAX),
     "", "h", "live", "Each profile can claim once in this many hours (24 = once a day).",
     "field:ClassCfg.ARROWS_HOURS@config.properties:arrows.cooldownHours"),
]
# build check: every row bound to a config.properties key has the default the default file writes (the file and the kit agree)''')
rep('''assert len(CFG_ROWS) == 5 + 1 + 2 * len(CLASSES) + 8, "row count"''',
    '''assert len(CFG_ROWS) == 5 + 2 + 1 + 2 * len(CLASSES) + 8 + 4, "row count"   # 0.1.7: + 2 greyed-out switch rows, + 4 arrow rows''')
rep('''               RELOAD="ClassCfg.load", KEEP=20, DEFAULTS=''', '''               RELOAD="ClassCfg.load", KEEP=CFG_KEEP, DEFAULTS=''')

# ================================================================================================================ ClassDefs: Archer index, deployables
rep('''F(defs, "public static final int PRIEST = %d;" % PRIEST_I)                                # 0.1.6: the heal class
''', '''F(defs, "public static final int PRIEST = %d;" % PRIEST_I)                                # 0.1.6: the heal class
F(defs, "public static final int ARCHER = %d;" % ARCHER_I)                                # 0.1.7: the daily-arrows class
F(defs, "public static final String[] D_IDS = %s;" % jarr([d for d, _ in DEPLOY_GUARD]))    # 0.1.7: deployable config ids judged at spawn
F(defs, "public static final String[] D_ITEMS = %s;" % jarr([i for _, i in DEPLOY_GUARD]))  # ... and the item (weapon rule) that throws each
''')
rep('''# ================= 0.1.6 KitCfg: kit.<Class> texts (fields next to ClassCfg), parsed at use time like SkyyIslands' IslandCfg.kitOf =================''',
    '''# 0.1.7: the class weapon whose throw spawns this deployable config id (null = not judged)
M(defs, r"""
public static String deployItem(String id) {
  if (id == null) return null;
  for (int i = 0; i < D_IDS.length && i < D_ITEMS.length; i++) if (D_IDS[i].equals(id)) return D_ITEMS[i];
  return null;
}""")

# ================= 0.1.6 KitCfg: kit.<Class> texts (fields next to ClassCfg), parsed at use time like SkyyIslands' IslandCfg.kitOf =================''')

# ================================================================================================================ ClassStore: arrow state (per profile)
rep('''# the player's own choice: null = done, otherwise the reason it was refused. synchronized -> no double charge on double clicks''',
    '''# ================= 0.1.7 daily Archer arrows, per profile (players/<pkey>.properties): arrowsAt = last refill start, arrowsN = refills,
# arrowsFly = in-flight record (written BEFORE the arrows move, dropped after: a crash loses rather than doubles), arrowsOwed = what did not
# fit. Every write: loadKey + saveKey under ClassStore's lock; an unread file is never written.
# ms until the next refill (0 = ready). A clock that went back by more than one cooldown counts as ready; less = the rest of the cooldown.
M(st_, r"""
public static long arrowsLeft(long last, long now, long cdMs) {
  if (last <= 0L || cdMs <= 0L) return 0L;
  if (now < last) {
    long back = last - now;
    return back >= cdMs ? 0L : cdMs - back;
  }
  long left = last + cdMs - now;
  return left > 0L ? left : 0L;
}""")
# 0 = started (arrowsAt + arrowsFly saved), 1 = cooldown not over, 2 = arrows still owed (collect first), -1 = file not readable / writable
M(st_, r"""
public static synchronized int arrowsBegin(String k, String list, long now, long cdMs) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return -1;
  if (old.getProperty("arrowsOwed", "").length() > 0) return 2;
  if (arrowsLeft(num(old, "arrowsAt"), now, cdMs) > 0L) return 1;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.setProperty("arrowsAt", String.valueOf(now));
  p.setProperty("arrowsN", String.valueOf(num(old, "arrowsN") + 1L));
  p.setProperty("arrowsFly", list == null ? "" : list);
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return -1; }
  return 0;
}""")
# the give (or claim) is over: the in-flight record goes; a remainder joins arrowsOwed
M(st_, r"""
public static synchronized boolean arrowsEnd(String k, String rem) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return false;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.remove("arrowsFly");
  if (rem != null && rem.length() > 0) {
    String had = old.getProperty("arrowsOwed", "");
    p.setProperty("arrowsOwed", had.length() == 0 ? rem : had + "," + rem);
  }
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return false; }
  return true;
}""")
# a claim of owed arrows starts: arrowsOwed -> arrowsFly (in flight until arrowsEnd); returns the list, null = nothing owed / not saved
M(st_, r"""
public static synchronized String arrowsClaimBegin(String k) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return null;
  String owed = old.getProperty("arrowsOwed", "");
  if (owed.length() == 0) return null;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  p.remove("arrowsOwed");
  p.setProperty("arrowsFly", owed);
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return null; }
  return owed;
}""")
# /classadmin info
M(st_, r"""
public static String arrowsText(java.util.Properties p, long now, long cdMs) {
  long at = num(p, "arrowsAt");
  String owed = p.getProperty("arrowsOwed", "");
  String fly = p.getProperty("arrowsFly", "");
  StringBuilder sb = new StringBuilder("arrows ");
  if (at <= 0L) sb.append("never claimed");
  else {
    long left = arrowsLeft(at, now, cdMs);
    sb.append(num(p, "arrowsN")).append(" refills, last ").append(@PKG@.KitCfg.day(at)).append(left > 0L ? " (next in " + fmtTime(left) + ")" : " (ready)");
  }
  if (owed.length() > 0) sb.append(" - owed ").append(@PKG@.KitCfg.rawText(owed));
  if (fly.length() > 0) sb.append(" - interrupted while giving ").append(@PKG@.KitCfg.rawText(fly)).append(" (the server stopped mid-give - it may or may not have landed)");
  return sb.toString();
}""")
# the player's own choice: null = done, otherwise the reason it was refused. synchronized -> no double charge on double clicks''')

# ================================================================================================================ KitSoon (constructor first: KitNewFn uses it)
rep('''# ================= 0.1.6 class:fn:kitnew (spec 2.3): apply(Object[]{UUID player, String pkey, String class}) -> Boolean =================''',
    '''# ================= 0.1.7 KitSoon: one kit try ~KIT_SOON_MS after a pick (run() is added after Kit.consider) =================
ksoon.addInterface(pool.get("java.lang.Runnable"))
F(ksoon, "public java.util.UUID u;")
C(ksoon, "public KitSoon(java.util.UUID u) { this.u = u; }")

# ================= 0.1.6 class:fn:kitnew (spec 2.3): apply(Object[]{UUID player, String pkey, String class}) -> Boolean =================''')
rep('''# cannot be read / written. Runs on the caller's thread (SkyyProfiles' world thread): one synchronized ClassStore write, no call into
# another mod (the pkey comes in as an argument), then one chat line to the player if online. Never throws.''',
    '''# cannot be read / written. Runs on the caller's thread (SkyyProfiles' world thread): one synchronized ClassStore write, no call into
# another mod (the pkey comes in as an argument). 0.1.7: then a kit try ~KIT_SOON_MS later (KitSoon on the scheduler; its KitTask queues
# on the player's world thread BEHIND SkyyProfiles' create + switch) instead of the "on its way" chat line. Never throws.''')
rep('''M(knew, r"""
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
}""")''', '''# 0.1.7 (LOCKED Skyy 2026-09-25: the kit lands immediately): schedule one kit try; the 2 s ClassTick is the fallback. Also /classadmin set.
M(knew, r"""
public static void soon(java.util.UUID u) {
  try {
    if (u == null) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.KitSoon(u), __SOON__L, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { }
}""".replace("__SOON__", str(KIT_SOON_MS)))''')
rep('''    if (r == 0) note(u, k, ci);''', '''    if (r == 0) soon(u);   // 0.1.7: tried right away (then every 2 s) - no 31 s wait''')

# ================================================================================================================ DeployGuard (after DamageLock)
rep('''# ================= 0.1.6 HealBudget: per target, a fixed 1 s window shared by ALL Priests (priestHeal.maxPerSecond) =================''',
    '''# ================= 0.1.7 DeployGuard: a class-owned deployable (the Healing Totem = Priest, LOCKED Skyy 2026-09-25) is judged when it SPAWNS =================
# The weapon lock only judges damage and a totem heals, so the thrown totem's deployable entity is checked instead: RefSystem on the
# engine's DeployableComponent (DeployablesUtils.spawnDeployable calls DeployableComponent.init(owner, ...) BEFORE addEntity(SPAWN), so the
# owner is known here), config id -> ClassDefs.deployItem, thrower = the owner Ref's PlayerRef, else the owner UUID's ShotTrack launch
# record (the totem is thrown as a projectile), else that UUID as a player. Not the owner class (judge below) -> CommandBuffer.removeEntity
# (the engine's own remove-on-add pattern, e.g. FailedSpawnSystem) + the lock chat line + popup. The item is not used up (10 s cooldown only).
# The component type comes from the built-in Deployables plugin: resolved lazily (at most every 5 s while missing); without it the
# query falls back to Query.any() and nothing is judged until the type exists.
F(dgd, "public @QRY@ query;")
F(dgd, "public static volatile Object TYPE = null;")
F(dgd, "public static volatile long TRIED = 0L;")
C(dgd, "public DeployGuard() { super(); this.query = null; }")
M(dgd, r"""
public static Object type() {
  Object t = TYPE;
  if (t != null) return t;
  long now = System.currentTimeMillis();
  if (now - TRIED < 5000L && now >= TRIED) return null;
  TRIED = now;
  try { t = @DEPC@.getComponentType(); } catch (Throwable x) { t = null; }
  if (t != null) TYPE = t;
  return t;
}""")
M(dgd, r"""
public @QRY@ getQuery() {
  if (this.query == null) {
    Object t = type();
    if (t instanceof @QRY@) this.query = @QRY@.and(new @QRY@[] { (@QRY@) t });   // = the engine's own DeployableRegisterer query
    else this.query = @QRY@.any();
  }
  return this.query;
}""")
# review fix: the totem is judged STRICTLY - only its owner class (Priest), and only while that class is playable, may throw it. The
# weapon lock's ClassRules.allowed lets a CLASSLESS player through while requireClass is off (the default), which would make the
# Priest-only totem free for anyone without a class. 0 = keep (the owner class), 1 = remove, 2 = keep: the class is unknown right now
# (no class from SkyyProfiles and the class file could not be read -> DATA has no copy); never removed on a guess, logged once.
F(dgd, "public static volatile boolean UNREAD = false;")
M(dgd, r"""
public static int judge(java.util.UUID u, String item) {
  if (u == null || item == null) return 0;
  int owner = @PKG@.ClassDefs.ownerOf(item);
  int ci = @PKG@.ClassStore.classIndex(u);
  if (owner >= 0 && ci == owner && @PKG@.ClassDefs.ENABLED[ci]) return 0;
  if (ci < 0 && @PKG@.ClassStore.DATA.get(@PKG@.ClassCfg.pkey(u)) == null) {
    if (!UNREAD) {
      UNREAD = true;
      @PKG@.ClassCfg.warn("deployable guard: the class file of " + u + " could not be read - their " + item + " was left standing rather than removed on a guess (logged once)");
    }
    return 2;
  }
  return 1;
}""")
# the lock line: a player with a class gets the weapon lock's own text; a classless one is told which class owns the item (the weapon
# lock's classless text says 'before fighting with weapons', which is wrong while requireClass is off)
M(dgd, r"""
public static String text(java.util.UUID u, String item) {
  if (@PKG@.ClassStore.classIndex(u) >= 0) return @PKG@.ClassRules.blockText(u, item, false);
  int owner = @PKG@.ClassDefs.ownerOf(item);
  String noun = @PKG@.ClassDefs.nounOf(item);
  if (owner < 0) return "No class can use " + noun + " yet.";
  String cn = @PKG@.ClassDefs.NAMES[owner];
  if (!@PKG@.ClassDefs.ENABLED[owner]) return cn + "s are coming soon - nobody can use " + noun + " yet.";
  return "Only " + cn + "s can use " + noun + " - " + (@PKG@.ClassCfg.profilesOn() ? "create a " + cn + " profile with /profiles." : "choose " + cn + " with /class.");
}""")
M(dgd, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (reason != @ADDR@.SPAWN || @PKG@.ClassDefs.D_IDS.length == 0) return;
    Object ty = type();
    if (ty == null) return;
    @DEPC@ dc = (@DEPC@) buf.getComponent(ref, (com.hypixel.hytale.component.ComponentType) ty);
    if (dc == null) return;
    @DEPCFG@ cf = dc.getConfig();
    String item = @PKG@.ClassDefs.deployItem(cf == null ? null : cf.getId());
    if (item == null) return;
    java.util.UUID u = null;
    @PR@ pr = null;
    @REF@ own = dc.getOwner();
    if (own != null && own.isValid()) {
      try { pr = (@PR@) buf.getComponent(own, @PR@.getComponentType()); } catch (Throwable t0) { pr = null; }
    }
    if (pr != null) u = pr.getUuid();
    if (u == null) {
      java.util.UUID ou = dc.getOwnerUUID();
      if (ou == null) return;
      @PKG@.ShotRec rec = (@PKG@.ShotRec) @PKG@.ShotTrack.SHOTS.get(ou);
      u = rec != null ? rec.shooter : ou;
      pr = @UNI@.get().getPlayer(u);
    }
    if (pr == null || u == null) return;     // not a player's deployable: never judged
    if (judge(u, item) != 1) return;         // review fix: strictly the owner class; an unreadable class file never removes
    buf.removeEntity(ref, @REMR@.REMOVE);
    String bt = text(u, item);
    @PKG@.ClassRules.tell(pr, u, bt);
    @PKG@.ClassRules.popup(pr, u, item, bt);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("deployable guard failed: " + t); }
}""")
M(dgd, r"""
public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ st, @CB@ buf) {
}""")

# ================= 0.1.6 HealBudget: per target, a fixed 1 s window shared by ALL Priests (priestHeal.maxPerSecond) =================''')

# ================================================================================================================ Kit: hotbar delivery, no waits
rep('''F(kit_, "public static final java.util.concurrent.ConcurrentHashMap KITEP = new java.util.concurrent.ConcurrentHashMap();")     # UUID -> long[]{epoch, seenAt}
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap KITARR = new java.util.concurrent.ConcurrentHashMap();")    # UUID -> Object[]{world UUID, Long since}
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap INFLIGHT = new java.util.concurrent.ConcurrentHashMap();")  # pkey -> Long handed to a world
F(kit_, "public static final long EPOCH_WAIT_MS = %dL;" % KIT_EPOCH_WAIT_MS)
F(kit_, "public static final long SAME_WORLD_MS = %dL;" % KIT_SAME_WORLD_MS)
''', '''# 0.1.7: no epoch / same-world wait maps any more (the kit lands immediately, LOCKED Skyy 2026-09-25)
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap INFLIGHT = new java.util.concurrent.ConcurrentHashMap();")  # pkey -> Long handed to a world
''')
rep('''# storage first (SkyySacks 0.6.5 / SkyyProfiles rule); what really landed is counted (added = after - before), so a failed add can
# never be mistaken for a full one. Amounts above an item's stack size fill several slots (the engine splits them).
M(kit_, r"""
public static int[] put(@PLA@ p, String[] ids, int[] qs) {
  int[] got = new int[ids.length];
  @INV@ inv = p.getInventory();
  @IC@ c = inv == null ? null : inv.getCombinedStorageHotbarBackpack();
  if (c == null) return got;''', '''# 0.1.7 where the items go: 0 = the 9 hotbar slots only (class kits and the quiet arrival retry of owed kit items, LOCKED Skyy 2026-09-25 -
# what does not fit stays the /class kit claim), 1 = hotbar first, then storage (an explicit /class kit claim, daily arrows;
# Inventory.getCombinedHotbarFirst = hotbar + storage)
M(kit_, r"""
public static @IC@ box(@PLA@ p, int where) {
  if (p == null) return null;
  @INV@ inv = p.getInventory();
  if (inv == null) return null;
  if (where == 0) return inv.getHotbar();
  return inv.getCombinedHotbarFirst();
}""")
# what really landed is counted (added = after - before, in the same container), so a failed add can never be mistaken for a full one.
# Amounts above an item's stack size fill several slots (the engine splits them).
M(kit_, r"""
public static int[] put(@PLA@ p, int where, String[] ids, int[] qs) {
  int[] got = new int[ids.length];
  @IC@ c = box(p, where);
  if (c == null) return got;''')
rep('''public static boolean room(@PLA@ p, String[] ids) {
  try {
    @INV@ inv = p.getInventory();
    @IC@ c = inv == null ? null : inv.getCombinedStorageHotbarBackpack();
    if (c == null) return false;''', '''public static boolean room(@PLA@ p, int where, String[] ids) {
  try {
    @IC@ c = box(p, where);
    if (c == null) return false;''')
rep('''    tell(pr, "Your " + cls + " kit is in your inventory: " + @PKG@.KitCfg.listText(ids, got) + ".", false);
  }
  if (left > 0) tell(pr, left + (left == 1 ? " item" : " items") + " of your " + cls + " kit did not fit - make room, then type /class kit to collect " + (left == 1 ? "it." : "them."), true);''',
    '''    tell(pr, "Your " + cls + " kit is in your hotbar: " + @PKG@.KitCfg.listText(ids, got) + ".", false);
    if ("Archer".equals(cls) && @PKG@.ClassCfg.ARROWS_ON) tell(pr, "Archers also get free arrows once a day - type /class arrows.", false);   // 0.1.7
  }
  if (left > 0) tell(pr, left + (left == 1 ? " item" : " items") + " of your " + cls + " kit did not fit your hotbar - make room, then type /class kit to collect " + (left == 1 ? "it." : "them."), true);''')
rep('''  int[] got = put(p, ids, qs);
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  if (full) @PKG@.ClassStore.kitEnd(k, rem);''', '''  int[] got = put(p, 0, ids, qs);   // 0.1.7: the hotbar only (LOCKED Skyy 2026-09-25); the rest = the /class kit claim
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  if (full) @PKG@.ClassStore.kitEnd(k, rem);''')
# review fix (LOCKED Skyy 2026-09-25 "overflow that does not fit still waits on /class kit"): the quiet claim = the automatic retry
# ~3 s after every world arrival (KitTask mode 2, e.g. the /island teleport right after a new profile) fills the HOTBAR only; only an
# explicit /class kit goes hotbar first, then storage.
rep('''  if (!room(p, ids)) {
    if (!quiet) tell(pr, "Your inventory is full - make room for your kit items (" + @PKG@.KitCfg.listText(ids, qs) + "), then type /class kit again.", true);''',
    '''  int where = quiet ? 0 : 1;   // 0.1.7 review fix: automatic (arrival) claims = the hotbar only; /class kit = hotbar, then storage
  if (!room(p, where, ids)) {
    if (!quiet) tell(pr, "Your hotbar and storage are full - make room for your kit items (" + @PKG@.KitCfg.listText(ids, qs) + "), then type /class kit again.", true);''')
rep('''  int[] got = put(p, ids, qs);
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  @PKG@.ClassStore.kitEnd(k, rem);''', '''  int[] got = put(p, where, ids, qs);
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  @PKG@.ClassStore.kitEnd(k, rem);''')
rep('''  if (left > 0 && (!quiet || g > 0)) tell(pr, left + (left == 1 ? " item" : " items") + " still did not fit - make room, then type /class kit again.", true);''',
    '''  if (left > 0 && (!quiet || g > 0)) tell(pr, left + (left == 1 ? " item" : " items") + (quiet ? " did not fit your hotbar - type /class kit to collect " + (left == 1 ? "it" : "them") + " (hotbar, then storage)." : " still did not fit - make room, then type /class kit again."), true);''')
rep('''  if ("pending".equals(s)) return "Your " + cls + " kit is on its way - it lands in your inventory shortly.";''',
    '''  if ("pending".equals(s)) return "Your " + cls + " kit is on its way - it lands in your hotbar in a moment.";''')
rep('''M(kit_, r"""
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
  Long fl = (Long) INFLIGHT.get(k);''', '''# 0.1.7 (LOCKED Skyy 2026-09-25): the kit lands IMMEDIATELY - no 31 s wait after a profile:epoch change and no 3 s in one world any more.
# Still: pending flag of the ACTIVE key, profile:busy absent (a switch or a crash recovery at join is not over), class known + playable,
# one task in flight per profile; KitTask re-checks all of it plus ready / alive on the player's world thread. prof is kept for the
# callers (unused). Crash window: SkyyProfiles rolls a crash in the 30 s after a switch back to the empty snapshot -> that kit is lost
# (never doubled; kit=given stays, an admin re-gives with /classadmin kit).
M(kit_, r"""
public static void consider(@PR@ pr, boolean prof, long now) {
  java.util.UUID u = pr.getUuid();
  if (u == null) return;
  String k = @PKG@.ClassCfg.pkey(u);
  if (!"pending".equals(@PKG@.ClassStore.KITQ.get(k))) return;
  if (busy(u)) return;
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !@PKG@.ClassDefs.ENABLED[ci]) return;
  java.util.UUID wu = pr.getWorldUuid();
  if (wu == null) return;
  Long fl = (Long) INFLIGHT.get(k);''')
rep('''public static void forget(java.util.UUID u) {
  if (u == null) return;
  KITEP.remove(u);
  KITARR.remove(u);
}""")''', '''public static void forget(java.util.UUID u) {
  if (u == null) return;
  String us = u.toString();
  java.util.Iterator it = INFLIGHT.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); if (k != null && k.startsWith(us)) it.remove(); }
}""")''')

# ================================================================================================================ KitSoon.run + Arrows (after Kit)
rep('''# ================= 0.1.6 HealTask: the Priest placeholder heal, on the world thread right after the hit (spec 2.4) =================''',
    '''# ================= 0.1.7 KitSoon.run: the kit try right after a pick (scheduler thread; Kit.consider hands the give to the world thread) =================
M(ksoon, r"""
public void run() {
  try {
    if (this.u == null || !@PKG@.KitCfg.ON || @PKG@.ClassStore.KITQ.isEmpty()) return;
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    @PKG@.Kit.consider(pr, @PKG@.ClassCfg.profilesOn(), System.currentTimeMillis());
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class kit (right after the pick) failed: " + t + " - the 2 s tick retries"); }
}""")

# ================= 0.1.7 Arrows: the daily Archer arrow refill, /class arrows (LOCKED Skyy 2026-09-25: arrows only, once a day per profile) =================
# World thread (the command). One pkey for the whole command; items only while profile:busy is absent. Owed arrows first (always the
# player's: no class / cooldown / on-off check); then Archer + arrows.enabled + cooldown + a known item + some room; then the synchronized
# arrowsBegin (re-checks owed + cooldown under ClassStore's lock and writes arrowsAt + arrowsFly BEFORE anything moves), the give (hotbar
# first, then storage) and arrowsEnd (the rest becomes arrowsOwed). Relog, a profile switch or a double command can never claim twice.
M(arw, r"""
public static int amount() {
  long n = @PKG@.ClassCfg.ARROWS_AMOUNT;
  if (n < 1L) n = 1L;
  if (n > __AMAX__L) n = __AMAX__L;
  return (int) n;
}""".replace("__AMAX__", str(ARROWS_AMOUNT_MAX)))
M(arw, r"""
public static long cooldownMs() {
  long h = @PKG@.ClassCfg.ARROWS_HOURS;
  if (h < 1L) h = 1L;
  return h * 3600000L;
}""")
M(arw, r"""
public static void collect(@PR@ pr, @PLA@ pl, String k, String owed) {
  Object[] ow = @PKG@.KitCfg.parse(owed, null, 1000);
  String[] ids = (String[]) ow[0];
  int[] qs = (int[]) ow[1];
  if (ids.length == 0) {
    if (@PKG@.ClassStore.arrowsClaimBegin(k) != null) @PKG@.ClassStore.arrowsEnd(k, "");
    @PKG@.Kit.tell(pr, "Nothing is waiting.", false);
    return;
  }
  if (!@PKG@.Kit.room(pl, 1, ids)) {
    @PKG@.Kit.tell(pr, "Your hotbar and storage are full - make room for your arrows (" + @PKG@.KitCfg.listText(ids, qs) + "), then type /class arrows again.", true);
    return;
  }
  String fly = @PKG@.ClassStore.arrowsClaimBegin(k);
  if (fly == null) { @PKG@.Kit.tell(pr, "Your class file could not be saved - try again in a moment.", true); return; }
  Object[] fw = @PKG@.KitCfg.parse(fly, "arrowsOwed of " + k, 1000);
  ids = (String[]) fw[0];
  qs = (int[]) fw[1];
  int[] got = @PKG@.Kit.put(pl, 1, ids, qs);
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  @PKG@.ClassStore.arrowsEnd(k, rem);
  int g = @PKG@.KitCfg.total(got);
  int left = @PKG@.KitCfg.total(qs) - g;
  if (g > 0) @PKG@.Kit.tell(pr, "Collected your arrows: " + @PKG@.KitCfg.listText(ids, got) + ".", false);
  if (left > 0) @PKG@.Kit.tell(pr, left + " still did not fit - make room, then type /class arrows again.", true);
  @PKG@.ClassCfg.info("daily arrows claim: " + pr.getUsername() + " (" + k + ") collected " + (g > 0 ? @PKG@.KitCfg.join(ids, got) : "nothing") + (left > 0 ? ", still owed " + rem : ""));
}""")
M(arw, r"""
public static void use(@PR@ pr, @PLA@ pl) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.ClassCfg.pkey(u);
  if (@PKG@.Kit.busy(u)) { @PKG@.Kit.tell(pr, "Your profile is still loading - try again in a moment.", true); return; }
  java.util.Properties p = @PKG@.ClassStore.loadKey(k);
  if (@PKG@.ClassStore.DATA.get(k) != p) { @PKG@.Kit.tell(pr, "Your class file could not be read - try again in a moment.", true); return; }
  String owed = p.getProperty("arrowsOwed", "");
  if (owed.length() > 0) { collect(pr, pl, k, owed); return; }
  if (!@PKG@.ClassCfg.ARROWS_ON) { @PKG@.Kit.tell(pr, "The daily arrow refill is off on this server.", true); return; }
  int ci = @PKG@.ClassStore.classIndex(u);
  int ar = @PKG@.ClassDefs.ARCHER;
  if (ci != ar || !@PKG@.ClassDefs.ENABLED[ar]) {
    @PKG@.Kit.tell(pr, ci < 0 ? "Only Archers get daily arrows - you have no class yet." : "Only Archers get daily arrows. You are " + @PKG@.ClassDefs.article(@PKG@.ClassDefs.NAMES[ci]) + ".", true);
    return;
  }
  long now = System.currentTimeMillis();
  long cd = cooldownMs();
  long left = @PKG@.ClassStore.arrowsLeft(@PKG@.ClassStore.num(p, "arrowsAt"), now, cd);
  if (left > 0L) {
    String fly = p.getProperty("arrowsFly", "");
    @PKG@.Kit.tell(pr, "Your next arrow refill is ready in " + @PKG@.ClassStore.fmtTime(left) + "." + (fly.length() > 0 ? " (The server stopped while your last refill was handed out - if those arrows are missing, ask an admin.)" : ""), true);
    return;
  }
  String id = @PKG@.ClassCfg.ARROWS_ITEM;
  if (id == null || !@PKG@.KitCfg.known(id)) {
    @PKG@.ClassCfg.warnLimited("daily arrows: arrows.item " + @PKG@.ClassCfg.clean(String.valueOf(id), 60) + " is not an item - nothing given");
    @PKG@.Kit.tell(pr, "The daily arrows are not set up right on this server - ask an admin (Server Setup -> Classes -> Archer arrows).", true);
    return;
  }
  String[] ids = new String[] { id };
  int[] qs = new int[] { amount() };
  if (!@PKG@.Kit.room(pl, 1, ids)) { @PKG@.Kit.tell(pr, "Your hotbar and storage are full - make room, then type /class arrows again. Your refill waits for you.", true); return; }
  int r = @PKG@.ClassStore.arrowsBegin(k, @PKG@.KitCfg.join(ids, qs), now, cd);
  if (r == 1) { @PKG@.Kit.tell(pr, "Your next arrow refill is not ready yet.", true); return; }
  if (r == 2) { @PKG@.Kit.tell(pr, "You still have arrows waiting - type /class arrows again to collect them.", true); return; }
  if (r != 0) { @PKG@.Kit.tell(pr, "Your class file could not be saved - nothing was given. Try again in a moment.", true); return; }
  int[] got = @PKG@.Kit.put(pl, 1, ids, qs);
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  @PKG@.ClassStore.arrowsEnd(k, rem);
  int g = @PKG@.KitCfg.total(got);
  int lf = @PKG@.KitCfg.total(qs) - g;
  if (g > 0) {
    @PKG@.Kit.popup(pr, "Daily arrows", "+" + g + " " + @PKG@.KitCfg.name(id), id);
    @PKG@.Kit.tell(pr, "Daily arrows: " + @PKG@.KitCfg.listText(ids, got) + " (hotbar first, then storage). Next refill in " + @PKG@.ClassStore.fmtTime(cd) + ".", false);
  }
  if (lf > 0) @PKG@.Kit.tell(pr, lf + " arrows did not fit - make room, then type /class arrows to collect them.", true);
  @PKG@.ClassCfg.info("daily arrows: " + pr.getUsername() + " (" + k + ") got " + (g > 0 ? @PKG@.KitCfg.join(ids, got) : "nothing") + (lf > 0 ? ", owed " + rem : ""));
}""")

# ================= 0.1.6 HealTask: the Priest placeholder heal, on the world thread right after the hit (spec 2.4) =================''')

# ================================================================================================================ HealTask: self-heal XP
rep('''# one party member (never the Priest): online, same world (their Ref lives in this store = this thread), ready, alive, not creative, in range''',
    '''# 0.1.7 (LOCKED Skyy 2026-09-25): HP the Priest heals on THEMSELF goes to SkyySkills too - the exact round-9 call; the trailing Boolean.TRUE
# = the self rate (0.25 Divinity XP per HP in SkyySkills 0.4.6+; 0.4.5 ignores the flag and pays the others rate -> deploy with 0.4.6+)
M(htask, r"""
public static void xpSelf(java.util.UUID u, double hpOnSelf) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("skill:fn:healxp");
    if (!(f instanceof java.util.function.Function)) return;
    ((java.util.function.Function) f).apply(new Object[] { u, Double.valueOf(hpOnSelf), "classes:heal:self", @PKG@.ClassCfg.pkey(u), Boolean.TRUE });
  } catch (Throwable t) { }
}""")
# one party member (never the Priest): online, same world (their Ref lives in this store = this thread), ready, alive, not creative, in range''')
rep('''    if (others > 0.0) xp(this.u, others);''', '''    if (others > 0.0) xp(this.u, others);
    if (self > 0.0) xpSelf(this.u, self);   // 0.1.7''')

# ================================================================================================================ KitHooks.checkArrow
rep('''kht.addInterface(pool.get("java.lang.Runnable"))''', '''# 0.1.7 check= of arrows.item: an arrow is fine; anything else asks first (the refill is meant for arrows only, LOCKED 2026-09-25)
M(khooks, r"""
public static String checkArrow(String key, String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.startsWith("Weapon_Arrow_")) return null;
  return "?" + @PKG@.ClassCfg.clean(v, 80) + " is not an arrow (Weapon_Arrow_...) - the daily refill is meant for arrows only. Save anyway?";
}""")
kht.addInterface(pool.get("java.lang.Runnable"))''')

# ================================================================================================================ commands
rep('''  super("kit", "Collect class kit items that did not fit your inventory (or see your kit)");''',
    '''  super("kit", "Collect class kit items that did not fit your hotbar (or see your kit)");''')
rep('''# ================= /class =================
C(cmd, r"""''', '''# ================= 0.1.7 /class arrows (player sub-command: the daily Archer arrow refill, or collect arrows that did not fit) =================
C(acmd, r"""
public ClassArrowsCmd() {
  super("arrows", "Archers: claim your free daily arrows (once a day per profile), or collect arrows that did not fit");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(acmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ pl = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (pl == null) return;
    @PKG@.Arrows.use(pr, pl);
  } catch (Throwable t) {
    @PKG@.ClassCfg.warn("/class arrows failed: " + t);
    pr.sendMessage(@MSG@.raw("[Classes] Could not hand out your arrows - the server log has the details."));
  }
}""")

# ================= /class =================
C(cmd, r"""''')
rep('''  addSubCommand(new @PKG@.ClassKitCmd());
}""")''', '''  addSubCommand(new @PKG@.ClassKitCmd());
  addSubCommand(new @PKG@.ClassArrowsCmd());   // 0.1.7
}""")''')
rep('''    if (!@PKG@.ClassStore.setClass(t, i, false, false)) { pr.sendMessage(@MSG@.raw("[Classes] Could not read or write the class file of " + t + " - nothing changed (see the server log).")); return; }
''', '''    if (!@PKG@.ClassStore.setClass(t, i, false, false)) { pr.sendMessage(@MSG@.raw("[Classes] Could not read or write the class file of " + t + " - nothing changed (see the server log).")); return; }
    @PKG@.KitNewFn.soon(t);   // 0.1.7: a first class on a classless file made its kit pending - it lands right away
''')
rep('''    pr.sendMessage(@MSG@.raw("[Classes] " + t + ": " + @PKG@.ClassStore.describe(t)
      + " | " + @PKG@.ClassStore.kitText(@PKG@.ClassStore.loadKey(@PKG@.ClassCfg.pkey(t)))));   // 0.1.6: + the kit state''',
    '''    java.util.Properties kp = @PKG@.ClassStore.loadKey(@PKG@.ClassCfg.pkey(t));
    pr.sendMessage(@MSG@.raw("[Classes] " + t + ": " + @PKG@.ClassStore.describe(t)
      + " | " + @PKG@.ClassStore.kitText(kp) + " | " + @PKG@.ClassStore.arrowsText(kp, System.currentTimeMillis(), @PKG@.Arrows.cooldownMs())));   // 0.1.6 kit + 0.1.7 arrows''')

# ================================================================================================================ setup / write / manifest
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.PriestHealSys());   // 0.1.6: Inspect group, after the damage landed
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.PriestHealSys());   // 0.1.6: Inspect group, after the damage landed
  getEntityStoreRegistry().registerSystem(new @PKG@.DeployGuard());     // 0.1.7: Priest-only Healing Totem, judged when it lands
''')
rep('''log("[SkyyClasses] __VER__ ready - /class, /class kit, /classadmin; classes "''',
    '''log("[SkyyClasses] __VER__ ready - /class, /class kit, /class arrows, /classadmin; classes "''')
rep('''for c in (cfg, kcfg, hooks, defs, st_, rul, afn, gfn, knew, srec, strk, lock, hbud, hmsg, kit_, ktask, htask, phs, khooks, kht, kmig,
          page, opn, rtk, rdy, quit_, ctick, kcmd, cmd, aset, ares, ainf, akit2, akit, arel, adm, pl):''',
    '''for c in (cfg, kcfg, hooks, defs, st_, rul, afn, gfn, ksoon, knew, srec, strk, lock, dgd, hbud, hmsg, kit_, ktask, arw, htask, phs, khooks,
          kht, kmig, page, opn, rtk, rdy, quit_, ctick, kcmd, acmd, cmd, aset, ares, ainf, akit2, akit, arel, adm, pl):''')
rep('''every class gets a kit with its basic weapon; Priests heal their party.''',
    '''every class gets a kit with its basic weapon, straight into the hotbar; Archers claim free arrows once a day; Priests heal their party and own the Healing Totem.''')

assert "KITEP" not in s and "KITARR" not in s and "EPOCH_WAIT_MS" not in s and "SAME_WORLD_MS" not in s, "0.1.7: the kit waits are gone"
assert "getCombinedStorageHotbarBackpack()" not in s.split("# ================= 0.1.6 Kit, part 1")[1].split("# ================= 0.1.6 KitTask")[0], \
    "0.1.7: no storage-first give left in Kit"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
