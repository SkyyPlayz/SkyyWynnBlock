"""Derive SkyyClasses/build_skyyclasses_0.1.6.py from 0.1.5 (run: python tools/classes_0_1_6_patch.py, then build the 0.1.6 script).
Spec: research/Classes-Berserker-Priest-Spec.md section 2 (Skyy's decisions of 2026-09-25: Berserker + Priest + class kits).
0.1.6:
 - ROSTER: Archer, Warrior, Mage, Berserker, Priest playable; Assassin, Shaman 'coming later'. Display order = list order (indices are
   never persisted: files store class=<Name> / played=<names>, ClassDefs.indexOf matches names, the page payload clspick<i> is transient).
   Berserker = Fury: Weapon_Axe_ axes, Weapon_Battleaxe_ battleaxes, Weapon_Mace_ maces, Weapon_Club_ clubs (Tool_Hatchet_* match no rule =
   free gathering tools). Priest = Divinity: Weapon_Wand_ wands, Weapon_Spellbook_ spellbooks. Shaman's placeholder icon is the Slowness
   Totem (the wand is a Priest weapon now). New ClassDefs.ROLES (one line per class, shown on /class; SkyyProfiles 0.1.2 has its own copy).
   The longest prefix wins, so the new class prefixes beat the Weapon_ catch-all; FREE_WEAPONS / UNASSIGNED are unchanged.
 - CLASS KITS (spec 2.3): kit.<Class>=id:amount,... in Skyy_SkyyClasses/config.properties (Server Setup -> Classes -> Class kits, one items
   row + one "Use my hotbar" action per class; kits.enabled part switch). Kit state per profile in players/<pkey>.properties (kit =
   pending | given | owed | old | off, kitClass, kitAt, kitGivenAt, kitItems, kitOwed, kitClaimAt) written through ClassStore's atomic
   saveKey. A kit becomes pending only from an ABSENT flag: SkyyProfiles 0.1.2's Create Profile calls the new bridge function
   class:fn:kitnew, SkyyClasses' own picker marks it in the same write as the first class (setClassKey on a file with no class and no
   flag; also /classadmin set on such a file). Never on syncKey, /profileadmin setclass, or a new choice after a reset of an old/given
   profile. KitMigrate (first start, kits.properties marker) marks every existing file with a class and no flag 'old' = no surprise kit.
   Delivery (Kit.tick in the 2 s ClassTick -> KitTask on the player's world thread, everything re-checked there): kits on, player online,
   pkey = the pending key, profile:busy absent, class known + playable, with SkyyProfiles >= 31 s since the last profile:epoch change
   SkyyClasses saw (first sight after a join counts as a change: SkyyProfiles' 30 s crash marker), >= 3 s in one world, Player ready, alive.
   Own picker (no SkyyProfiles): ClassPage gives it at once after Confirm. Give order is crash-safe (kitBegin writes kit=given + the
   in-flight list first; a lost kit is admin-recoverable, a duplicate is not), items go storage first
   (getCombinedStorageHotbarBackpack), what did not fit becomes a claim (kit=owed) - retried 3 s after every world arrival and by
   /class kit, never dropped on the ground. Popup (Success) + chat line, not toggleable (onboarding).
   Commands: /class kit (player, hytale:Adventurer), /classadmin kit <player|uuid> [class] (requirePermission skyyclasses.admin +
   setPermissionGroups(new String[0])); /classadmin info shows the kit state.
 - PRIEST PLACEHOLDER HEAL (spec 2.4): PriestHealSys (DamageEventSystem, INSPECT group = after ApplyDamage, Query.any): an uncancelled hit of
   >= 1 on an NPC (never a player) by a Priest holding a Priest weapon (melee: main hand at the hit; orbs: the ShotTrack launch record's new
   ShotRec.item), not in creative (the dispatch skips a creative melee hit early; HealTask.run re-checks the Priest's own game mode for
   EVERY hit, orbs included, before anything heals) -> HealTask on the same world thread: every SkyyParty member (party:fn:members)
   online, same world,
   ready, alive, not creative, within priestHeal.radius of the Priest heals min(damage x sharePercent %, maxPerHit), the Priest themself
   selfPercent % of that; per target at most maxPerSecond in a fixed 1 s window for all Priests together (HealBudget); never above max
   Health (overheal is clamped BEFORE the budget is taken, so it never uses up the per-second cap). HP healed on OTHER members is offered to
   SkyySkills 0.4.4 as Divinity XP through skill:fn:healxp (absent = no XP, no error). Chat aggregated (HealMsg, flushed by ClassTick):
   Priest "Heals: +23 HP to your party (2 players) and +6 HP to you", member "Skyy healed you +12 HP" - admin master switch
   priestHeal.messages AND the player Settings switches classes.healGiven / classes.healTaken, checked before the line's own timestamp.
 - SERVER SETUP (spec 2.5): 23 new rows (kits.enabled, 7 kit items rows each followed by its "Use my hotbar" action, 8 Priest heal rows),
   categories Weapon lock / Class picker / Class kits / Priest heal; all new keys read their code defaults while missing from the file.
   ClassCfg.load (the kit's RELOAD) parses and clamps them. "Use my hotbar" (review fix): the kit check's question (another class's
   weapon, or an unowned weapon while unassignedBlocked is on) is NOT pre-answered - the first click saves nothing and asks in chat; a
   second click on the same kit within 60 s with the same hotbar is the "Save anyway" (the action already answered the menu before the
   hotbar could be read, so the question cannot appear in the menu itself).
 - Interrupted gives (review fix): an admin /classadmin kit of the same class on a profile whose give was interrupted clears the
   in-flight record (the admin checked and re-gave); /classadmin info and /class kit say plainly that such a kit may or may not have landed.
 - /class page: 7 cards on a 1000 x 900 root (fits 1080), role in the card title, "Hatchets are tools." in the footer.
 - setup order: ClassCfg.load -> KitMigrate.runOnce -> bridge puts (class:fn:kitnew) -> commands -> events -> systems ShotTrack, DamageLock,
   PriestHealSys -> ClassTick -> regSetting x4 -> CfgPub.start last. shutdown unchanged.
Defaults of the 0.1.5 keys are unchanged.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.5.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.6.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


def rep_span(start, end, new):
    """replace from the unique start marker through the unique end marker (inclusive)"""
    global s
    assert s.count(start) == 1, "start anchor count %d: %s" % (s.count(start), start[:80])
    a = s.index(start)
    b = s.index(end, a)
    assert s.count(end) >= 1
    s = s[:a] + new + s[b + len(end):]


# ================================================================================================================ docstring + version
rep('"""SkyyClasses 0.1.3 - build script (javassist via jpype). Wynncraft-style classes for SkyWynn.',
    '"""SkyyClasses 0.1.6 - build script (javassist via jpype; derived from 0.1.5 by tools/classes_0_1_6_patch.py - edit the patch, not this\n'
    'file). Wynncraft-style classes for SkyWynn.\n'
    '0.1.6 (Skyy 2026-09-25, research/Classes-Berserker-Priest-Spec.md section 2): roster Archer, Warrior, Mage, BERSERKER (Fury: axes,\n'
    '  battleaxes, maces, clubs; hatchets stay free tools), PRIEST (Divinity: wands, spellbooks; AoE healing support) - Assassin + Shaman later.\n'
    '  CLASS KITS: every class has a kit with its basic weapon (Server Setup -> Classes -> Class kits), given once per profile when the class\n'
    '  is picked (SkyyProfiles 0.1.2 calls class:fn:kitnew; the own picker marks it itself); storage first, overflow waits as a claim\n'
    '  (/class kit). PRIEST PLACEHOLDER HEAL: a Priest weapon hit on a monster heals party members near the Priest (numbers in Server Setup),\n'
    '  Divinity XP for healing others via SkyySkills 0.4.4 skill:fn:healxp. Notes in tools/classes_0_1_6_patch.py.')
rep('VERSION = "0.1.5"', 'VERSION = "0.1.6"')
rep("Run:   python build_skyyclasses_0.1.5.py            -> SkyyClasses/SkyyClasses-0.1.5.jar",
    "Run:   python build_skyyclasses_0.1.6.py            -> SkyyClasses/SkyyClasses-0.1.6.jar")
rep("  /classadmin info <player|uuid>, /classadmin reload (config).",
    "  /classadmin info <player|uuid>, /classadmin reload (config); 0.1.6: /classadmin kit <player|uuid> [class] (give a kit now).\n"
    "Player: /class, 0.1.6 /class kit (collect kit items that did not fit).")
rep('  class:list -> "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery" (selectable classes)',
    '  class:list -> "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity" (selectable classes)\n'
    '  class:fn:kitnew (0.1.6) -> Function apply(Object[]{UUID player, String pkey, String class}) -> Boolean: a profile just got its class,\n'
    '    mark its kit pending (SkyyProfiles 0.1.2 Create Profile). Reads party:fn:members, skill:fn:healxp (0.1.6).')
rep("      profile N; class, chosenAt, lastChoiceAt, switches, played, prompted),",
    "      profile N; class, chosenAt, lastChoiceAt, switches, played, prompted; 0.1.6 kit, kitClass, kitAt, kitGivenAt, kitItems, kitOwed,\n"
    "      kitClaimAt), Skyy_SkyyClasses/kits.properties (0.1.6: written once by the 'picked before kits' migration),")

# ================================================================================================================ roster (spec 2.1)
rep_span("CLASSES = [\n", "\n]\n# usable by every class", r'''CLASSES = [
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
# usable by every class''')

rep("SYNC_STEADY_MS = 1500", r'''# 0.1.6 class kits + Priest heal (research/Classes-Berserker-Priest-Spec.md 2.3-2.5). Defaults also in CFG_LINES and the kit rows.
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
DEF_HEAL_MSG_MS = 5000
HEAL_SHARE_MAX, HEAL_SELF_MAX = 500, 100
HEAL_RADIUS_MIN, HEAL_RADIUS_MAX = 1.0, 64.0
HEAL_CAP_MIN, HEAL_CAP_MAX = 0.5, 1000.0
HEAL_MSG_MS_MIN, HEAL_MSG_MS_MAX = 1000, 60000


def dnum(x):
    """a decimal as the config kit's canonical text (16.0 -> 16, 0.5 -> 0.5)"""
    return str(int(x)) if float(x) == int(x) else repr(float(x))


def jdbl(x):
    return repr(float(x))


SYNC_STEADY_MS = 1500''')

rep('    for _k in ("name", "skill", "desc", "weapon_text"):',
    '    assert isinstance(_c.get("kit"), str) and _c.get("role"), "0.1.6: every class needs a role and a kit (may be empty)"\n'
    '    for _k in ("name", "skill", "desc", "weapon_text", "role"):')
rep('print("  note - Weapon-tagged items no rule catches (treated as free):", ", ".join(_slip) or "none")',
    r'''print("  note - Weapon-tagged items no rule catches (treated as free):", ", ".join(_slip) or "none")
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
    print("  %-10s %s" % (_c["name"], _c["kit"] or "(empty)"))''')

# ================================================================================================================ tokens + probes + classes
rep('    "IWM":  "com.hypixel.hytale.protocol.ItemWithAllMetadata",\n}',
    '    "IWM":  "com.hypixel.hytale.protocol.ItemWithAllMetadata",\n'
    '    # 0.1.6: kits + Priest heal\n'
    '    "NPC":  "com.hypixel.hytale.server.npc.entities.NPCEntity",\n'
    '    "ESM":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",\n'
    '    "ESV":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",\n'
    '    "DST":  "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",\n'
    '    "INV":  "com.hypixel.hytale.server.core.inventory.Inventory",\n'
    '    "IC":   "com.hypixel.hytale.server.core.inventory.container.ItemContainer",\n'
    '    "VEC":  "org.joml.Vector3d",\n'
    '    "GM":   "com.hypixel.hytale.protocol.GameMode",\n'
    '    "ITM":  "com.hypixel.hytale.server.core.asset.type.item.config.Item",\n'
    '}')
rep('    B.probe(pool, c, m)\npool.get(T["DES"])',
    '    B.probe(pool, c, m)\n'
    '# 0.1.6: every new engine call (spec 2.9)\n'
    'for c, m in ((T["DMOD"], "getInspectDamageGroup"), (T["ESM"], "addStatValue"), (T["ESM"], "getComponentType"), (T["ESM"], "get"),\n'
    '             (T["DST"], "getHealth"), (T["ESV"], "get"), (T["ESV"], "getMax"), (T["INV"], "getCombinedStorageHotbarBackpack"),\n'
    '             (T["INV"], "getHotbar"), (T["IC"], "addItemStack"), (T["IC"], "getCapacity"), (T["IC"], "getItemStack"),\n'
    '             (T["IC"], "canAddItemStack"), ("com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction", "getRemainder"),\n'
    '             (T["PLA"], "isWaitingForClientReady"), (T["PLA"], "getGameMode"), (T["PLA"], "getInventory"), (T["PLA"], "markNeedsSave"),\n'
    '             (T["NPC"], "getComponentType"), (T["NST"], "Success"), (T["GM"], "Creative"), (T["ITM"], "getAssetMap"),\n'
    '             (T["ES"], "getWorld"), (T["TC"], "getPosition"), (T["VEC"], "x"), (AC, "addUsageVariant"), (T["CTX"], "provided"),\n'
    '             (T["WLD"], "execute"), (T["IS"], "getQuantity"), (T["PR"], "getReference"), (T["PR"], "getUsername")):\n'
    '    B.probe(pool, c, m)\n'
    'pool.get(T["DES"])')
rep('pl   = pool.makeClass(PKG + ".SkyyClassesPlugin", pool.get(T["JP"]))',
    'pl   = pool.makeClass(PKG + ".SkyyClassesPlugin", pool.get(T["JP"]))\n'
    '# 0.1.6: class kits + Priest heal (all top-level classes; KitCfg is made next to ClassCfg, KitHooks after the config kit)\n'
    'knew  = pool.makeClass(PKG + ".KitNewFn")\n'
    'kit_  = pool.makeClass(PKG + ".Kit")\n'
    'ktask = pool.makeClass(PKG + ".KitTask")\n'
    'kmig  = pool.makeClass(PKG + ".KitMigrate")\n'
    'kht   = pool.makeClass(PKG + ".KitHotbarTask")\n'
    'khooks = pool.makeClass(PKG + ".KitHooks")\n'
    'hbud  = pool.makeClass(PKG + ".HealBudget")\n'
    'hmsg  = pool.makeClass(PKG + ".HealMsg")\n'
    'htask = pool.makeClass(PKG + ".HealTask")\n'
    'phs   = pool.makeClass(PKG + ".PriestHealSys", pool.get(T["DES"]))\n'
    'kcmd  = pool.makeClass(PKG + ".ClassKitCmd", pool.get(T["APC"]))\n'
    'akit  = pool.makeClass(PKG + ".AdminKitCmd", pool.get(T["APC"]))')

# ================================================================================================================ default file text
rep('    "# unassignedBlocked = true: weapons no class owns yet (axes, maces, wands, spellbooks, bombs, guns...) deal no damage for players with a class",',
    '    "# unassignedBlocked = true: weapons no class owns yet (bombs, guns, darts, claws, deployables...) deal no damage for players with a class",')
rep('    "openDelayMillis=%d" % DEF_OPEN_DELAY_MS,\n]',
    r'''    "openDelayMillis=%d" % DEF_OPEN_DELAY_MS,
    "# ---------- Class kits (0.1.6) - every class gets its basic weapon once, when a profile picks the class ----------",
    "# kits.enabled = false: new classes get no kit (kits still pending or owed wait until it is on again)",
    "kits.enabled=%s" % str(DEF_KITS_ON).lower(),
    "# kit.<Class> = item:amount,item:amount (at most %d stacks). In game: Server Setup -> Classes -> Class kits (also 'Use my hotbar')" % KIT_MAX_STACKS,
] + ["kit.%s=%s" % (_c["name"], _c["kit"]) for _c in CLASSES] + [
    "# ---------- Priest heal (placeholder until spells exist) ----------",
    "# a Priest's wand or spellbook hit on a monster heals party members within priestHeal.radius blocks of the Priest by sharePercent of",
    "# the damage (the Priest themself selfPercent of that), at most maxPerHit per hit and maxPerSecond per second for each player",
    "priestHeal.enabled=%s" % str(DEF_HEAL_ON).lower(),
    "priestHeal.sharePercent=%d" % DEF_HEAL_SHARE_PCT,
    "priestHeal.selfPercent=%d" % DEF_HEAL_SELF_PCT,
    "priestHeal.radius=%s" % dnum(DEF_HEAL_RADIUS),
    "priestHeal.maxPerHit=%s" % dnum(DEF_HEAL_MAX_HIT),
    "priestHeal.maxPerSecond=%s" % dnum(DEF_HEAL_MAX_SEC),
    "# messages = heal chat lines (players can also hide theirs in /settings); feedbackMs = at most one line per player this often",
    "priestHeal.messages=%s" % str(DEF_HEAL_MSG).lower(),
    "priestHeal.feedbackMs=%d" % DEF_HEAL_MSG_MS,
]''')

# ================================================================================================================ ClassCfg fields + KitCfg fields
rep('F(cfg, "public static final String[] DEFAULT_LINES = %s;" % jarr(CFG_LINES))',
    r'''F(cfg, "public static final String[] DEFAULT_LINES = %s;" % jarr(CFG_LINES))
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
    F(kcfg, "public static volatile String K_%s = %s;" % (_c["name"].upper(), jstr(_c["kit"])))''')

# ---------------------------------------------------------------- ClassCfg helpers before load(), load() reads the new keys
rep('M(cfg, r"""\npublic static synchronized String load() {',
    r'''# 0.1.6 loader helpers
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
public static synchronized String load() {''')
rep('    PROMPT_EVERY_LOGIN = bool(p, "promptEveryLogin", PROMPT_EVERY_LOGIN);\n'
    '    return "switchCost=" + SWITCH_COST + " cooldownMinutes=" + COOLDOWN_MIN + " requireClass=" + REQUIRE_CLASS\n'
    '      + " unassignedBlocked=" + UNASSIGNED_BLOCKED + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS;\n'
    '  } catch (Throwable t) { warn("could not load config: " + t); return "config load failed: " + t; }\n'
    '}""")',
    r'''    PROMPT_EVERY_LOGIN = bool(p, "promptEveryLogin", PROMPT_EVERY_LOGIN);
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
M(cfg, _LOAD)''')
rep('public static String summary() {\n'
    '  return "switchCost=" + SWITCH_COST + " cooldownMinutes=" + COOLDOWN_MIN + " requireClass=" + REQUIRE_CLASS\n'
    '    + " unassignedBlocked=" + UNASSIGNED_BLOCKED + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS;',
    'public static String summary() {\n'
    '  return "switchCost=" + SWITCH_COST + " cooldownMinutes=" + COOLDOWN_MIN + " requireClass=" + REQUIRE_CLASS\n'
    '    + " unassignedBlocked=" + UNASSIGNED_BLOCKED + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS + extraText();')

# ================================================================================================================ Server Setup rows (spec 2.5)
rep('CFG_CATS = [("lock", "Weapon lock"), ("picker", "Class picker")]',
    'CFG_CATS = [("lock", "Weapon lock"), ("picker", "Class picker"), ("kits", "Class kits"), ("priest", "Priest heal")]   # 0.1.6: + kits, priest')
rep('     "ON: weapons no class owns (axes, maces, bombs, guns, wands...) do no damage for anyone with a class.",',
    '     "ON: unowned weapons (bombs, guns, darts, claws, deployables...) do no damage for class players.",')
rep('     "custom:ClassHooks"),\n]\n',
    r'''     "custom:ClassHooks"),
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
''')
rep('NOTE="Player classes: /classadmin set, reset, info <player>. Weapon rules are code (rebuild).",',
    'NOTE="Players: /classadmin set, reset, info, kit <player>. Weapon rules are code (rebuild).",')

# ================================================================================================================ ClassDefs: roles + Priest index
rep('F(defs, "public static final String[] WTEXT = %s;" % jarr([c["weapon_text"] for c in CLASSES]))',
    'F(defs, "public static final String[] WTEXT = %s;" % jarr([c["weapon_text"] for c in CLASSES]))\n'
    'F(defs, "public static final String[] ROLES = %s;" % jarr([c["role"] for c in CLASSES]))   # 0.1.6\n'
    'F(defs, "public static final int PRIEST = %d;" % PRIEST_I)                                # 0.1.6: the heal class')

# ================================================================================================================ KitCfg methods (after ClassDefs, before ClassStore)
rep("# ================= ClassStore: per-player data, bridge publishing, coins, the choose transaction =================",
    r'''# 0.1.6: every class name, lower case (command help / refusals)
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

# ================= ClassStore: per-player data, bridge publishing, coins, the choose transaction =================''')

# ================================================================================================================ ClassStore: KITQ, loadKey, setClassKey, kit state
rep('F(st_, "public static final java.util.concurrent.ConcurrentHashMap FAILAT = new java.util.concurrent.ConcurrentHashMap();")',
    'F(st_, "public static final java.util.concurrent.ConcurrentHashMap FAILAT = new java.util.concurrent.ConcurrentHashMap();")\n'
    '# 0.1.6: pkey -> "pending" | "owed" for every class file read (loadKey) or written (kitnew, setClassKey, give) with that kit state, so the\n'
    '# 2 s kit tick and the arrival retry never read files. The owner UUID is the first 36 characters of the pkey.\n'
    'F(st_, "public static final java.util.concurrent.ConcurrentHashMap KITQ = new java.util.concurrent.ConcurrentHashMap();")')
rep('  FAILAT.remove(k);\n  DATA.put(k, p);\n',
    '  FAILAT.remove(k);\n  DATA.put(k, p);\n'
    '  String ks = p.getProperty("kit");\n'
    '  if ("pending".equals(ks) || "owed".equals(ks)) KITQ.put(k, ks);\n')
rep('  String n = null;\n  if (idx < 0) {\n    p.remove("class");',
    '  String n = null;\n'
    '  // 0.1.6: the first class of a file with no kit flag makes its kit pending in the SAME write (own picker / /classadmin set on a classless\n'
    '  // file). A file that had a class or any kit flag (old, given, owed, off, pending) is left alone: one automatic kit per profile at most.\n'
    '  String kit0 = null;\n'
    '  if (idx >= 0 && old.getProperty("class", "").trim().length() == 0 && old.getProperty("kit") == null) kit0 = @PKG@.KitCfg.ON ? "pending" : "off";\n'
    '  if (idx < 0) {\n    p.remove("class");')
rep('  if (paid) p.setProperty("switches", String.valueOf(num(p, "switches") + 1L));\n  DATA.put(k, p);',
    '  if (paid) p.setProperty("switches", String.valueOf(num(p, "switches") + 1L));\n'
    '  if (kit0 != null) {\n'
    '    p.setProperty("kit", kit0);\n'
    '    p.setProperty("kitClass", n);\n'
    '    p.setProperty("kitAt", String.valueOf(now));\n'
    '  }\n'
    '  DATA.put(k, p);')
rep('  if (n == null) CLS.remove(k); else CLS.put(k, n);\n  return true;',
    '  if (n == null) CLS.remove(k); else CLS.put(k, n);\n'
    '  if ("pending".equals(kit0)) KITQ.put(k, "pending");\n'
    '  return true;')
rep("# 0.1.3: copy the authoritative profile class into that profile's file (offline class:fn:get, /classadmin info, a start without SkyyProfiles)",
    r'''# ================= 0.1.6 kit state per profile (spec 2.3). Every write goes through loadKey + saveKey under ClassStore's lock (all other keys
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

# 0.1.3: copy the authoritative profile class into that profile's file (offline class:fn:get, /classadmin info, a start without SkyyProfiles)''')

# ================================================================================================================ class:fn:kitnew
rep("# ================= ShotRec + ShotTrack: what the shooter held when a projectile / bomb was LAUNCHED =================",
    r'''# ================= 0.1.6 class:fn:kitnew (spec 2.3): apply(Object[]{UUID player, String pkey, String class}) -> Boolean =================
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

# ================= ShotRec + ShotTrack: what the shooter held when a projectile / bomb was LAUNCHED =================''')

# ---------------------------------------------------------------- ShotRec.item (0.1.6: the Priest heal needs the launching item, not only a forbidden one)
rep('F(srec, "public boolean util;")\nF(srec, "public long at;")\nC(srec, r"""\n'
    'public ShotRec(java.util.UUID shooter, String bad, boolean util) {\n'
    '  this.shooter = shooter;\n  this.bad = bad;\n  this.util = util;\n',
    'F(srec, "public boolean util;")\n'
    'F(srec, "public String item;")   # 0.1.6: the main-hand item id at launch (null = empty hand), for every tracked shot\n'
    'F(srec, "public long at;")\nC(srec, r"""\n'
    'public ShotRec(java.util.UUID shooter, String bad, boolean util, String item) {\n'
    '  this.shooter = shooter;\n  this.bad = bad;\n  this.util = util;\n  this.item = item;\n')
rep('    String bad = badOf(u, @INVC@.getItemInHand(buf, sh));',
    '    @IS@ mh = @INVC@.getItemInHand(buf, sh);\n'
    '    String item = (mh == null || mh.isEmpty()) ? null : mh.getItemId();\n'
    '    String bad = badOf(u, mh);')
rep('    SHOTS.put(idc.getUuid(), new @PKG@.ShotRec(u, bad, util));',
    '    SHOTS.put(idc.getUuid(), new @PKG@.ShotRec(u, bad, util, item));')

# ================================================================================================================ heal + kit machinery (after DamageLock)
rep("# ================= ClassPage: /class =================",
    r'''# ================= 0.1.6 HealBudget: per target, a fixed 1 s window shared by ALL Priests (priestHeal.maxPerSecond) =================
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

# ================= ClassPage: /class =================''')

# ================================================================================================================ ClassPage (spec 2.6: 7 cards, 1000 x 900)
rep('BTN = ("Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 12, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '       "Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '       "Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")\n'
    'BTN_GO = ("Style: TextButtonStyle(Default: (Background: #2f6a3a, LabelStyle: (FontSize: 12, TextColor: #e9ffe9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '          "Hovered: (Background: #3f8a4a, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '          "Pressed: (Background: #1f4a2a, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")\n'
    'PAGE_W, PAGE_H = 780, 616',
    '# 0.1.6: 15 pt buttons, 1000 x 900 root (7 cards, fits 1080): 3 + 40 + 28 + 7 x (6 + 96) + 8 + 26 + 40 = 859 + 28 padding = 887\n'
    'BTN = ("Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 15, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '       "Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '       "Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")\n'
    'BTN_GO = ("Style: TextButtonStyle(Default: (Background: #2f6a3a, LabelStyle: (FontSize: 15, TextColor: #e9ffe9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '          "Hovered: (Background: #3f8a4a, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "\n'
    '          "Pressed: (Background: #1f4a2a, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")\n'
    'PAGE_W, PAGE_H = 1000, 900\n'
    'assert 3 + 40 + 28 + len(CLASSES) * (6 + 96) + 8 + 26 + 40 + 28 <= PAGE_H <= 1080, "the /class page must fit its root and 1080"')
rep_span('M(page, (r"""\npublic void build(', '.replace("__W__", str(PAGE_W)).replace("__H__", str(PAGE_H)))\n', r'''M(page, (r"""
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
''')
rep('      this.playerRef.sendMessage(@MSG@.raw("[Classes] You are now " + @PKG@.ClassDefs.article(n) + "! Your weapons: " + @PKG@.ClassDefs.WTEXT[p] + ". Your combat skill: " + @PKG@.ClassDefs.SKILLS[p] + ".").color("#8fe39a"));',
    '      this.playerRef.sendMessage(@MSG@.raw("[Classes] You are now " + @PKG@.ClassDefs.article(n) + "! Your weapons: " + @PKG@.ClassDefs.WTEXT[p] + ". Your combat skill: " + @PKG@.ClassDefs.SKILLS[p] + ".").color("#8fe39a"));\n'
    '      if (!@PKG@.ClassCfg.profilesOn()) @PKG@.Kit.now(this.playerRef, ref, st);   // 0.1.6: own picker = the kit lands at once')

# ================================================================================================================ ready / quit / tick
rep('    @PKG@.ClassStore.load(u);\n    if (@PKG@.ClassCfg.profilesOn()) { @PKG@.ClassStore.check(u); return; }',
    '    @PKG@.ClassStore.load(u);\n'
    '    @PKG@.Kit.owedLater(pr);   // 0.1.6: owed kit items of this profile (the load above just filled KITQ at a join)\n'
    '    if (@PKG@.ClassCfg.profilesOn()) { @PKG@.ClassStore.check(u); return; }')
rep('    java.util.UUID u = pr.getUuid();\n    if (@PKG@.ClassStore.SESSION.putIfAbsent(u, Boolean.TRUE) != null) return;',
    '    java.util.UUID u = pr.getUuid();\n'
    '    @PKG@.Kit.owedLater(pr);   // 0.1.6: every world arrival retries owed kit items, before the once-per-session check\n'
    '    if (@PKG@.ClassStore.SESSION.putIfAbsent(u, Boolean.TRUE) != null) return;')
rep('    @PKG@.ClassStore.SNAPAT.remove(u);\n  } catch (Throwable t) { }',
    '    @PKG@.ClassStore.SNAPAT.remove(u);\n'
    '    @PKG@.Kit.forget(u);\n'
    '    @PKG@.HealBudget.forget(u);\n'
    '    @PKG@.HealMsg.forget(u);\n'
    '  } catch (Throwable t) { }')
rep("# ================= ClassTick (0.1.3): profile epoch check every 2 s -> republish class:<uuid> (contract rule 3). No SkyyProfiles = no-op =================",
    "# ================= ClassTick (0.1.3): profile epoch check every 2 s -> republish class:<uuid> (contract rule 3). No SkyyProfiles = no-op =================\n"
    "# 0.1.6: first the class kit rules (Kit.tick, returns at once while nothing is pending) and the heal chat lines, with or without SkyyProfiles")
rep('public void run() {\n  try {\n    if (!@PKG@.ClassCfg.profilesOn()) return;\n    java.util.Iterator it = @UNI@.get().getPlayers().iterator();',
    'public void run() {\n'
    '  try { @PKG@.Kit.tick(); } catch (Throwable t0) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("class kit tick failed: " + t0); } }\n'
    '  try { @PKG@.HealMsg.flushDue(); } catch (Throwable t2) { }\n'
    '  try {\n    if (!@PKG@.ClassCfg.profilesOn()) return;\n    java.util.Iterator it = @UNI@.get().getPlayers().iterator();')

# ================================================================================================================ commands
rep("# ================= /class =================",
    r'''# ================= 0.1.6 /class kit (player sub-command: collect owed kit items of the active profile, or see the kit state) =================
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

# ================= /class =================''')
rep('  super("class", "Open the class page (Archer, Warrior, Mage - Assassin and Shaman later)");\n'
    '  addAliases(new String[] { "classes" });\n'
    '  setPermissionGroups(new String[] { "hytale:Adventurer" });\n',
    '  super("class", "Open the class page - Archer, Warrior, Mage, Berserker, Priest (Assassin and Shaman later)");\n'
    '  addAliases(new String[] { "classes" });\n'
    '  setPermissionGroups(new String[] { "hytale:Adventurer" });\n'
    '  addSubCommand(new @PKG@.ClassKitCmd());\n')
rep('  this.classArg = withRequiredArg("class", "archer | warrior | mage", @ATY@.STRING);',
    '  this.classArg = withRequiredArg("class", "archer | warrior | mage | berserker | priest", @ATY@.STRING);')
rep('    pr.sendMessage(@MSG@.raw("[Classes] " + t + ": " + @PKG@.ClassStore.describe(t)));\n'
    '  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin info <player|uuid>")); }',
    '    pr.sendMessage(@MSG@.raw("[Classes] " + t + ": " + @PKG@.ClassStore.describe(t)\n'
    '      + " | " + @PKG@.ClassStore.kitText(@PKG@.ClassStore.loadKey(@PKG@.ClassCfg.pkey(t)))));   // 0.1.6: + the kit state\n'
    '  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin info <player|uuid>")); }')
rep('C(adm, r"""\npublic ClassAdminCmd() {',
    r'''# 0.1.6: /classadmin kit <player|uuid> [<class>] - give a kit NOW to an online player (ignores the flag; disabled classes allowed for
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
public ClassAdminCmd() {''')
rep('  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | reload");\n'
    '  requirePermission("skyyclasses.admin");\n'
    '  addSubCommand(new @PKG@.AdminSetCmd());\n'
    '  addSubCommand(new @PKG@.AdminResetCmd());\n'
    '  addSubCommand(new @PKG@.AdminInfoCmd());\n',
    '  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | kit <player> [class] | reload");\n'
    '  requirePermission("skyyclasses.admin");\n'
    '  addSubCommand(new @PKG@.AdminSetCmd());\n'
    '  addSubCommand(new @PKG@.AdminResetCmd());\n'
    '  addSubCommand(new @PKG@.AdminInfoCmd());\n'
    '  addSubCommand(new @PKG@.AdminKitCmd());\n')
rep('  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | reload"));',
    '  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | kit <player|uuid> [class] | reload"));')

# ================================================================================================================ setup() (spec 2.8)
rep('  String cfgText = @PKG@.ClassCfg.load();\n',
    '  String cfgText = @PKG@.ClassCfg.load();\n'
    '  @PKG@.KitMigrate.runOnce();   // 0.1.6: existing profiles with a class -> kit=old (once; before kitnew can be called)\n')
rep('  b.put("class:fn:get", new @PKG@.GetFn());\n',
    '  b.put("class:fn:get", new @PKG@.GetFn());\n'
    '  b.put("class:fn:kitnew", new @PKG@.KitNewFn());   // 0.1.6 (SkyyProfiles 0.1.2 Create Profile)\n')
rep('  getEntityStoreRegistry().registerSystem(new @PKG@.DamageLock());\n',
    '  getEntityStoreRegistry().registerSystem(new @PKG@.DamageLock());\n'
    '  getEntityStoreRegistry().registerSystem(new @PKG@.PriestHealSys());   // 0.1.6: Inspect group, after the damage landed\n')
rep('''  @PKG@.ClassCfg.regSetting("classes.blockedPopup", "Blocked weapon - popup", "combat", true, "The popup with the weapon's icon - at most every 1.5 s");\n''',
    '''  @PKG@.ClassCfg.regSetting("classes.blockedPopup", "Blocked weapon - popup", "combat", true, "The popup with the weapon's icon - at most every 1.5 s");\n'''
    '''  @PKG@.ClassCfg.regSetting("classes.healGiven", "Priest heals - your heals", "combat", true, "Your heals: +23 HP to 2 party members and +6 HP to you - one line every 5 s at most");\n'''
    '''  @PKG@.ClassCfg.regSetting("classes.healTaken", "Priest heals - healed by others", "combat", true, "Skyy healed you +12 HP - one line every 5 s at most. The heal happens either way");\n''')
rep('getLogger().at(java.util.logging.Level.INFO).log("[SkyyClasses] __VER__ ready - /class, /classadmin; classes "',
    'getLogger().at(java.util.logging.Level.INFO).log("[SkyyClasses] __VER__ ready - /class, /class kit, /classadmin; classes "')

# ================================================================================================================ write + manifest
rep("for c in (cfg, hooks, defs, st_, rul, afn, gfn, srec, strk, lock, page, opn, rtk, rdy, quit_, ctick, cmd, aset, ares, ainf, arel, adm, pl):",
    "for c in (cfg, kcfg, hooks, defs, st_, rul, afn, gfn, knew, srec, strk, lock, hbud, hmsg, kit_, ktask, htask, phs, khooks, kht, kmig,\n"
    "          page, opn, rtk, rdy, quit_, ctick, kcmd, cmd, aset, ares, ainf, akit2, akit, arel, adm, pl):")
rep('"SkyWynn classes (Wynncraft style): Archer, Warrior, Mage (Assassin and Shaman later). Your class decides your weapons and your combat skill; /class to choose, locked per profile with SkyyProfiles. Zero dependencies (SkyyProfiles and SkyyCoins optional)."',
    '"SkyWynn classes (Wynncraft style): Archer, Warrior, Mage, Berserker, Priest (Assassin and Shaman later). Your class decides your weapons and your combat skill; every class gets a kit with its basic weapon; Priests heal their party. /class to choose, locked per profile with SkyyProfiles. Zero dependencies (SkyyProfiles, SkyyParty, SkyySkills and SkyyCoins optional)."')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
