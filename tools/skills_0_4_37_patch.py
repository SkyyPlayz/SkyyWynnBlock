"""Derive SkyySkills/build_skyyskills_0.4.37.py from the LIVE generated SkyySkills/build_skyyskills_0.4.36.py (= the tools/deploy_set.py SET
pin; 0.4.36 came from 0.4.35 by tools/skills_0_4_36_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.36 stays untouched, its line endings are kept; the 0.4.36
rebirth participant (SkillRb) is kept as it is (one tolerance line for a rebirth staged by 0.4.36, see (5)).
Run:  python tools/skills_0_4_37_patch.py   then   python SkyySkills/build_skyyskills_0.4.37.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.37.py --dir tools/dev/scratch/<yours>/sk   (bare JVM, -Xverify:all)

0.4.37 (2026-10-14) = PERFECT DODGE in our roll + GATHERING PHASE 2, the SkyySkills side (Skyy 2026-10-11 popup "Add perfect-dodge to ours
(Recommended)" - docs/answered/skills.md 2026-10-11 PERFECT DODGES; research/Gathering-Shards-Spec.md 5.3 / 5.4 / 11 phase 2):
  (1) PERFECT DODGE (learned from narwhals' Perfect Dodges - ARR, nothing copied; it stays OFF): a hit from a monster or a player (an entity
      source; never fall / fire / poison / drowning, never a cause that bypasses resistances) that lands at most acro.perfectDodge.windowMs
      (50) after one of OUR roll effects began (Dodge_Left / Right / Forward / Back - the 8-way roll, sprint press or dodge key) = a PERFECT
      DODGE: the hit does no damage (PDodgeSys, Filter group, BEFORE the engine's DamageSystems$FilterUnkillable - the vanilla 0.25 s roll
      i-frames would otherwise cancel the event before any later system sees it), +acro.perfectDodge.xp (5) Acrobatics XP once per roll
      (into the Acrobatics XP the 1 s tick pays: acro.enabled, not creative, not during a Monk move), and the player's NEXT hit within
      acro.perfectDodge.counterMs (750) deals x acro.perfectDodge.counterMultiplier (1.25) - "the counter-hit" (PCounterSys, Filter group,
      any target, used up by that hit). Roll age = the roll effect's initial minus remaining duration (the engine ticks it per world tick,
      so 50 ms = the hit in the roll's own tick or the next one at 30 TPS); a roll effect EXTENDED by a chained roll (remaining above its
      initial) counts as "cannot tell" = no perfect dodge (the vanilla i-frames still block). Chat line "Perfect dodge! ..." at most every
      1.5 s, player switch skills.perfectDodge in /settings. Server Setup -> Skills -> Acrobatics: 6 rows (acro.perfectDodge*).
      FIX ROUND (critics): a hit with no damage, or one another engine filter would block anyway (dead / Invulnerable / Intangible,
      spawn protection, player damage off, a player's hit with PvP off - PDodge.vetoAt mirrors FilterUnkillable, PlayerDamageFilterSystem,
      FilterPlayerWorldConfig; build-checked) is never a perfect dodge; the XP only for a MONSTER's hit (a PvP dodge still blocks + gives the
      counter-hit, no XP) and at most acro.perfectDodge.maxXpPerMinute (50) a minute; the chat line names only the XP really paid; the
      hit's knockback is removed like the engine's own filters do.
  (2) THREE NEW SKILLS (spec 5.3 / 5.4): Fishing, Ranching, Orchard = storage slots 16, 17, 18 (append-only; saved keys Fishing / Ranching /
      Orchard + .paid in players/<pkey>.properties, written with every save from now on). A profile file WITHOUT them loads them as 0 XP,
      level 0, nothing owed (no retroactive coins). They level on the general table (Server Setup -> Levels -> own list per skill works for
      them too), are not on the /skills page rows yet (the page budget is 9 rows - a later UI round), open with /skills stats fishing |
      ranching | orchard, have /skills top lists, level-up chat lines and coins like every skill.
      - FISHING XP: SkyyFishing already sends every catch through skill:fn:addxp {uuid, "Fishing", xp, "fishing", pkey} (0.1.x answers FALSE
        today) - Fishing, Ranching and Orchard are now ALWAYS grantable through skill:fn:addxp (like Exploration; bridge.addxp.skills is not
        rewritten - no migration), so catches pay from this version on.
      - RANCHING XP = pickups only (spec 13 "Ranching XP from pickups only until proven"). Desk probe R1 (0.7 jar + Assets.zip, scratch
        deleted): InteractivelyPickupItemEvent fires ONLY for F-pickups of loose blocks and crop harvests (ItemUtils.interactivelyPickupItem's
        callers: BlockHarvestUtils.performPickupByInteraction, FarmingUtil.giveDrops) - never for animal products; EVERY player pickup
        (ground items AND F-pickups) spawns a "picked up" item entity (ItemComponent.generatePickedUpItem: ItemComponent + PickupItemComponent
        whose target is the player) - RanchPickSys (a RefSystem on PickupItemComponent) sees it as it is added. Coops hand their produce
        straight into the inventory (UseCoopInteraction.gatherProduceFromContainer - no pickup, not counted); shearing / milking (NPC
        Harvest*: Drop_Sheep_Harvest wool, Drop_Chicken_Harvest feathers, the cow fills a held bucket) are UNVERIFIED in game. Paid per item
        id from ranching.items (eggs, wool, feathers, chicken / pork / beef / wild meat, light / medium hide), x the xp multiplier, x
        Farming's gathering pace (at the Ranching level) + the Farming tree Wisdom, THEN at most ranching.maxXpPerMinute (200) per player
        (fix round: the cap counts the final XP). A PARTIAL ground pickup (inventory nearly full) or an F-pickup counts as 1 item (the
        picked-up entity then holds the REMAINDER / a new 1-item stack; only a full pickup is flagged removedByPlayerPickup). ANTI-FARM: items a PLAYER dropped (DropItemEvent$Drop on a player - RanchDropSys) go into a
        per-world ledger and the next pickups of that id in that world pay nothing (10 min memory) - drop / pick-up loops pay 0.
      - ORCHARD XP: Farming XP of the blocks in orchard.ids (default Plant_Crop_Apple, Plant_Crop_Berry - apples and berry bushes; spec 7.3
        M1 "Apple, Wild Berries") is paid to Orchard instead (broken ripe, F-harvested, sickle swings). Ripe checks, the harvest gate, the
        Farming double drops / tool Fortune and the trees' gather hooks stay exactly Farming's (one shared Farming tree, spec 5.3). FIX
        ROUND: Orchard (and Ranching) awards keep Farming's gathering pace switch (gather.boost.skills "Farming", at their own level) and
        the xp.farming tree Wisdom (Farm3.paceSlot -> GatherPace.applyAt in SkillXp.gain4) - no silent XP cut for apple harvesters.
      - FARMING AVERAGE (spec 5.3): skill:farmavg:<uuid> (Integer) = floor((Farming + Ranching + Orchard) / 3) at the profile's levels,
        published with skill:<uuid>; skill:fn:level answers "farmingavg". A SEPARATE key on purpose: SkyyGuilds sums every level in
        skill:<uuid> and SkyyMenu prints every pair, so a "FarmingAvg" pair there would count Farming twice. skill:<uuid> gains
        Fishing:<n>,Ranching:<n>,Orchard:<n> (always listed). The Overall Level counts Farming as that average ONLY with Server Setup ->
        Overall "Farming counts as the average" (overall.farmingAverage, default OFF - on today it would drop every farmer's Overall Level,
        Ranching / Orchard start at 0; Skyy decides). Fishing may be added to overall.skills by an admin.
      - REBIRTH (R1 / R3 rules, Exploration excluded only): the three reset like every slot but Exploration (x.Fishing / x.Ranching /
        x.Orchard facts); arm.fishing now appears in the facts (SkyyRebirth 0.2 already reads it - the Fishing arm earns points). A
        rebirth STAGED by 0.4.36 and committed by 0.4.37 has no x.<new> line: those three slots are left as they are (not an error).
  FIX ROUND 2 (critics): the Ranching drop ledger takes a player's drop only AFTER every system saw the event (RanchDropSys queues a
    RanchTask(drop, world) on the world; Ranch.dropDone skips a drop that was cancelled before or after us - SkyyIslands' guard, SkyyVault,
    CarryChest and other mods handle DropItemEvent$Drop too); no stacking with Perfect Parries (pack mod, by runtime id): a hit made while
    the attacker carries PP_Counterattack_Ready keeps only the parry's own counter multiplier and uses our counter-hit up (PDodge.hasFx,
    PARRY_SKIP); the Acrobatics "Perfect dodge" line and a new Farming-page line "Farming level (average of Farming - Ranching - Orchard)"
    come LAST on the Stats "now" list and only while it has room (ST_LINES 7) - they never push the skill-tree line or a hook line off.
    Not changed: drops that reach the ground without a player's drop (a broken chest, a death drop) still pay Ranching XP up to
    ranching.maxXpPerMinute (known gap, question for Skyy); a rebirth staged by 0.4.36 skips the new slots (the test world has no staged
    rebirth - no rebirth folder in Skyy_SkyySkills on 2026-10-14).
  ROLLBACK to 0.4.36: safe for everything but the new skills' XP - 0.4.36 drops the Fishing / Ranching / Orchard lines at the next save of
    each profile (their XP is lost; nothing else). Server Setup keys of 0.4.37 are ignored by 0.4.36. No migration, no command change.
  NEXT ROUNDS (not here): SkyyTrees - the Fishing tree + the Farming tree's level = skill:farmavg:<uuid>; SkyyHud - Fishing / Ranching /
    Orchard lines + "Farming 12 (F 15 / R 9 / O 12)"; SkyyCollections - fish / animal / fruit collection XP rewards routed to Fishing /
    Ranching / Orchard (grants work already); SkyyRebirth - arm.farming fed by all three pools (spec 5.3 "one Farming branch"); SkyyGear -
    hoe / sickle cap + farm armor from the average; SkyySkills - /skills page rows for the three; SkyyMenu - a SET_KNOWN row for the new
    player switch skills.perfectDodge (tab combat, "Perfect dodge line", same help text) - its menu_check WARNs until then - and the
    Skills tab row budget (StatsCalc.ROWS 14: 3 more skill pairs may push the last class row off).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.36.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.37.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.36"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.36"' in s and "derived from the generated 0.4.35 by tools/skills_0_4_36_patch.py" in s, "not the live generated 0.4.36"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert 'srb = pool.makeClass(PKG + ".SkillRb")' in s, "not 0.4.36 (SkillRb missing)"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.37 (2026-10-14)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.36 - build script (derived from the generated 0.4.35 by tools/skills_0_4_36_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.37 - build script (derived from the generated 0.4.36 by tools/skills_0_4_37_patch.py - edit the patch, not this file;
0.4.36 was derived from the generated 0.4.35 by tools/skills_0_4_36_patch.py;
''')
rep('''0.4.36 (2026-10-14) = REBIRTH ROUND R3''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.37.py.
0.4.36 (2026-10-14) = REBIRTH ROUND R3''')
rep('VERSION = "0.4.36"', 'VERSION = "0.4.37"')

# ---------------------------------------------------------------- (2) the three new storage slots 16-18 (append-only)
rep('''SLOT_NAMES = [_x[0] for _x in _SL]
''', '''# 0.4.37 (research/Gathering-Shards-Spec.md 5.3 / 5.4): Fishing, Ranching, Orchard = storage slots 16, 17, 18 (APPENDED; saved keys = names)
GATHER37_ROWS = [("Fishing", "Fishing", "Fish_Trout_Rainbow_Item", "#6fc0e8"), ("Ranching", "Ranching", "Tool_Shears_Basic", "#d8a070"),
                 ("Orchard", "Orchard", "Plant_Fruit_Apple", "#e8786f")]
for _c in GATHER37_ROWS: must(_c[2])
_SL = _SL + [tuple(_c) for _c in GATHER37_ROWS]
SLOT_NAMES = [_x[0] for _x in _SL]
''')
rep('''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 16''',
    '''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 19   # 0.4.37: + Fishing, Ranching, Orchard''')
rep('''assert SLOT_NAMES[10:14] == ["Alchemy", "Smithing", "Cooking", "Exploration"] and SLOT_NAMES[14:] == ["Combat.Berserker", "Combat.Priest"]
assert SLOT_LABELS[14:] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Zen" and SLOT_NAMES[8] == "Combat.Shaman"   # 0.4.21: renamed, key kept; 0.4.27 Zen''',
    '''assert SLOT_NAMES[10:14] == ["Alchemy", "Smithing", "Cooking", "Exploration"] and SLOT_NAMES[14:16] == ["Combat.Berserker", "Combat.Priest"]
assert SLOT_NAMES[16:] == ["Fishing", "Ranching", "Orchard"] == SLOT_LABELS[16:]   # 0.4.37
assert SLOT_LABELS[14:16] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Zen" and SLOT_NAMES[8] == "Combat.Shaman"   # 0.4.21: renamed, key kept; 0.4.27 Zen''')
rep('''defs.addField(CtField.make("public static final int DIVINITY = %d;" % DIVINITY_SLOT, defs))   # 0.4.4 Priest
''', '''defs.addField(CtField.make("public static final int DIVINITY = %d;" % DIVINITY_SLOT, defs))   # 0.4.4 Priest
# 0.4.37: the Gathering phase 2 slots (spec 5.3 / 5.4)
for _nm37, _ix37 in (("FISHING", 16), ("RANCHING", 17), ("ORCHARD", 18)):
    assert SLOT_NAMES[_ix37] == _nm37.capitalize()
    defs.addField(CtField.make("public static final int %s = %d;" % (_nm37, _ix37), defs))
''')

# ---------------------------------------------------------------- the new classes
rep('''pmig = pool.makeClass(PKG + ".PerkMig")
''', '''pmig = pool.makeClass(PKG + ".PerkMig")
# 0.4.37: perfect dodge (PDodge + PDodgeSys / PDodgeSysU before FilterUnkillable + PCounterSys), Ranching pickups (Ranch + RanchPickSys on the
# picked-up item entity + RanchDropSys on a player's drop + RanchTask), Orchard routing + the Farming average (Farm3)
REFS37 = "com.hypixel.hytale.component.system.RefSystem"
PIC37 = "com.hypixel.hytale.server.core.modules.entity.item.PickupItemComponent"
ICO37 = "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent"
ADR37 = "com.hypixel.hytale.component.AddReason"
RMR37 = "com.hypixel.hytale.component.RemoveReason"
DIE37 = "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent.Drop"    # javassist source name (cast)
DIE37C = "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop"  # class literal
FU37 = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FilterUnkillable"
# fix round: the other damage filters PDodgeSys mirrors (PDodge.vetoAt) + the knockback a perfect dodge removes
PDF37 = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$PlayerDamageFilterSystem"
FPW37 = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FilterPlayerWorldConfig"
INVU37 = "com.hypixel.hytale.server.core.modules.entity.component.Invulnerable"
INTG37 = "com.hypixel.hytale.server.core.modules.entity.component.Intangible"
KBC37 = "com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent"
ARC37 = "com.hypixel.hytale.component.Archetype"
CBC37 = "com.hypixel.hytale.server.core.asset.type.gameplay.CombatConfig"
pdg  = pool.makeClass(PKG + ".PDodge")
pds  = pool.makeClass(PKG + ".PDodgeSys", pool.get(DEVS))
pdsu = pool.makeClass(PKG + ".PDodgeSysU", pds)
pcs  = pool.makeClass(PKG + ".PCounterSys", pool.get(DEVS))
rch  = pool.makeClass(PKG + ".Ranch")
rps  = pool.makeClass(PKG + ".RanchPickSys", pool.get(REFS37))
rds  = pool.makeClass(PKG + ".RanchDropSys", pool.get(EES))
rtk  = pool.makeClass(PKG + ".RanchTask")
fm3  = pool.makeClass(PKG + ".Farm3")
''')

# ---------------------------------------------------------------- the default file block (fresh xp.properties; an old file reads the code defaults)
rep('''
DEFAULTS = "\\n".join(L) + "\\n"
''', r'''
# 0.4.37: perfect dodge + Ranching / Orchard / Farming average - ONE block at the end of a FRESH file. An existing file is NOT changed: a
# missing key reads the same code default (PDodge / Ranch / Farm3.read), so no migration.
PD_ON_DEF, PD_WIN_DEF, PD_CTR_DEF, PD_MULT_DEF, PD_XP_DEF, PD_PM_DEF = "true", "50", "750", "1.25", "5", "50"
RANCH_ITEMS = [("Food_Egg", 3), ("Ingredient_Fabric_Scrap_Wool", 3), ("Ingredient_Feathers_Light", 1), ("Food_Chicken_Raw", 2),
               ("Food_Pork_Raw", 2), ("Food_Beef_Raw", 3), ("Food_Wildmeat_Raw", 2), ("Ingredient_Hide_Light", 1), ("Ingredient_Hide_Medium", 2)]
for _i37, _x37 in RANCH_ITEMS: must(_i37)
RANCH_DEF = ",".join("%s:%d" % _r for _r in RANCH_ITEMS)
RANCH_PM_DEF = "200"
ORCH_DEF = ",".join([must_prefix("Plant_Crop_Apple"), must_prefix("Plant_Crop_Berry")])
G37_L = ["# ---------- Perfect dodge, Ranching, Orchard (SkyySkills 0.4.37) ----------",
         "# Comments must stay on their own lines.",
         "# PERFECT DODGE: a roll that starts at most acro.perfectDodge.windowMs before a monster's or player's hit takes no damage,",
         "# pays acro.perfectDodge.xp Acrobatics XP once per roll, and your next hit within acro.perfectDodge.counterMs deals",
         "# x acro.perfectDodge.counterMultiplier damage (1 = no counter-hit). The XP comes only from monsters' hits, at most",
         "# acro.perfectDodge.maxXpPerMinute a minute per player (0 = no cap); a hit the server would block anyway never counts.",
         "acro.perfectDodge=" + PD_ON_DEF,
         "acro.perfectDodge.windowMs=" + PD_WIN_DEF,
         "acro.perfectDodge.counterMs=" + PD_CTR_DEF,
         "acro.perfectDodge.counterMultiplier=" + PD_MULT_DEF,
         "acro.perfectDodge.xp=" + PD_XP_DEF,
         "acro.perfectDodge.maxXpPerMinute=" + PD_PM_DEF,
         "# RANCHING: animal products you pick up pay Ranching XP (item id and XP per item). Items a player dropped pay nothing when",
         "# they are picked up again in that world. At most ranching.maxXpPerMinute Ranching XP per player per minute (0 = no cap).",
         "ranching.pickupXp=true",
         "ranching.items=" + RANCH_DEF,
         "ranching.maxXpPerMinute=" + RANCH_PM_DEF,
         "# ORCHARD: the Farming XP of blocks whose id starts with one of these goes to Orchard instead (apples and berry bushes).",
         "orchard.ids=" + ORCH_DEF,
         "# FARMING AVERAGE: true = the Overall Level counts Farming as the average of Farming, Ranching and Orchard.",
         "overall.farmingAverage=false"]
L.append("")
L.extend(G37_L)
G37_DEFAULTS = "\n".join(G37_L) + "\n"
assert all(ord(ch) < 128 for ch in G37_DEFAULTS) and '"' not in G37_DEFAULTS and "\\" not in G37_DEFAULTS and all(len(_ln) <= 140 for _ln in G37_L if _ln.startswith("#"))
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in G37_L), "a comment looks like a template line"
G37_KEYS = [_ln.split("=", 1)[0] for _ln in G37_L if not _ln.startswith("#")]
assert len(G37_KEYS) == len(set(G37_KEYS)) == 11
DEFAULTS = "\n".join(L) + "\n"
''')

# ---------------------------------------------------------------- region (b): config readers + pure maths, before SkillLv / SkillCfg.load
R37B = r'''# ================= 0.4.37 PERFECT DODGE + GATHERING PHASE 2 part 1: config readers + pure maths (before SkillCfg.load, which calls the
# readers; Overall.sums / BreakTask / HarvestTask / Sickle call Farm3). Engine facts the new code rests on (HytaleServer.jar, read at every
# build; any drift stops it):
#   F1 DamageSystems$FilterUnkillable (Filter group) cancels the damage of an entity whose EffectControllerComponent isInvulnerable (the
#      roll's Dodge_Invulnerability) - a cancelled Damage reaches no later system (EventSystem.shouldProcessEvent), so PDodgeSys runs BEFORE it
#   F2 every player pickup (ground items via PlayerItemEntityPickupSystem, F-pickups via ItemUtils.interactivelyPickupItem) adds a picked-up
#      item entity (ItemComponent.generatePickedUpItem) with a PickupItemComponent whose target is the player
#   F3 ItemUtils.throwItem (a player's drop) fires DropItemEvent$Drop on the thrower first
for _c37, _m37 in ((PIC37, "getTargetRef"), (PIC37, "getComponentType"), (ICO37, "getItemStack"), (ICO37, "getComponentType"),
                   (AEE, "getInitialDuration"), (AEE, "getRemainingDuration"), (AEE, "getEntityEffectIndex"), (ECC, "getAllActiveEntityEffects"),
                   (DCS, "doesBypassResistances"), (DMG, "getCause"), (DIE37C, "getItemStack"), (REFS37, "onEntityAdded"), (REFS37, "onEntityRemove"),
                   (ADR37, "LOAD"),
                   # fix round: the veto (PDodge.vetoAt), the knockback removal, the partial-pickup flag
                   (INVU37, "getComponentType"), (INTG37, "getComponentType"), (DTH, "getComponentType"), (KBC37, "getComponentType"),
                   (ARC37, "contains"), (ST, "getArchetype"), (PLA, "hasSpawnProtection"), (WLD, "getWorldConfig"), (WCFG, "isPvpEnabled"),
                   (WLD, "getGameplayConfig"), (CBC37, "isPlayerIncomingDamageDisabled"), (DMG, "getIfPresentMetaObject"), (DMG, "KNOCKBACK_COMPONENT"),
                   (CB, "tryRemoveComponent"), (ICO37, "isRemovedByPlayerPickup")):
    B.probe(pool, _c37, _m37)
import jpype as _jpy37
_JM37 = _jpy37.JClass("javassist.Modifier")
def _bc37(cls, meth):
    """_bc_lines with its own jpype handle (the module-level _jp name is reused further up the script)"""
    _ip37, _out37 = _jpy37.JClass("javassist.bytecode.InstructionPrinter"), []
    for _mm in pool.get(cls).getDeclaredMethods():
        if str(_mm.getName()) != meth or _mm.getMethodInfo().getCodeAttribute() is None:
            continue
        _it, _cp = _mm.getMethodInfo().getCodeAttribute().iterator(), _mm.getMethodInfo().getConstPool()
        while _it.hasNext():
            _out37.append(str(_ip37.instructionString(_it, _it.next(), _cp)))
    return _out37
for _c37, _m37, _d37 in ((PIC37, "getTargetRef", "()L" + REF.replace(".", "/") + ";"), (ICO37, "getItemStack", "()L" + IS.replace(".", "/") + ";"),
                         (AEE, "getInitialDuration", "()F"), (AEE, "getRemainingDuration", "()F"), (AEE, "getEntityEffectIndex", "()I"),
                         (ECC, "getAllActiveEntityEffects", "()[L" + AEE.replace(".", "/") + ";"), (DCS, "doesBypassResistances", "()Z"),
                         (DIE37C, "getItemStack", "()L" + IS.replace(".", "/") + ";"),
                         (REFS37, "onEntityAdded", "(L" + REF.replace(".", "/") + ";L" + ADR37.replace(".", "/") + ";L" + ST.replace(".", "/") + ";L" + CB.replace(".", "/") + ";)V"),
                         (REFS37, "onEntityRemove", "(L" + REF.replace(".", "/") + ";L" + RMR37.replace(".", "/") + ";L" + ST.replace(".", "/") + ";L" + CB.replace(".", "/") + ";)V")):
    try:
        _mm37 = pool.get(_c37).getMethod(_m37, _d37)
    except Exception as _e37:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (_c37, _m37, _d37, _e37))
    assert _JM37.isPublic(_mm37.getModifiers()) and _JM37.isPublic(pool.get(_c37).getModifiers()), "%s.%s is no longer public" % (_c37, _m37)
_fu37 = _bc37(FU37, "handle")
assert (any(ECC + ".isInvulnerable" in x for x in _fu37) and any(DMG + ".setCancelled" in x for x in _fu37)
        and "getFilterDamageGroup" in " ".join(_bc37(FU37, "getGroup"))), \
    "DamageSystems$FilterUnkillable no longer cancels invulnerable entities' damage in the Filter group - re-check PDodgeSys (perfect dodge)"
_spe37 = _bc37("com.hypixel.hytale.component.system.EventSystem", "shouldProcessEvent")
assert any("ICancellableEcsEvent.isCancelled" in x for x in _spe37), "event systems may see cancelled events now - re-check PDodgeSys's order"
_pk37 = _bc37("com.hypixel.hytale.server.core.modules.entity.player.PlayerItemEntityPickupSystem", "tick")
_iu37 = _bc37("com.hypixel.hytale.server.core.entity.ItemUtils", "interactivelyPickupItem")
_gp37 = _bc37(ICO37, "generatePickedUpItem")
assert (any(ICO37 + ".generatePickedUpItem" in x for x in _pk37) and any(ICO37 + ".generatePickedUpItem" in x for x in _iu37)
        and any(PIC37 + ".<init>" in x for x in _gp37)), \
    "player pickups no longer add a picked-up item entity with a PickupItemComponent - re-check RanchPickSys (Ranching XP)"
# fix round: a FULL ground pickup marks the ground item removedByPlayerPickup BEFORE generatePickedUpItem clones it (the clone keeps the flag
# and the picked quantity); a PARTIAL pickup sets the ground stack to the REMAINDER first and never sets the flag - RanchPickSys pays 1 item then
_pkj37 = " ".join(_pk37)
assert (ICO37 + ".setRemovedByPlayerPickup" in _pkj37 and _pkj37.index(ICO37 + ".setRemovedByPlayerPickup") < _pkj37.index(ICO37 + ".generatePickedUpItem")
        and ICO37 + ".setItemStack" in _pkj37 and any("removedByPlayerPickup" in x for x in _bc37(ICO37, "clone"))),     "the pickup flag facts changed (setRemovedByPlayerPickup / setItemStack / clone) - re-check RanchPickSys's quantity"
# fix round: the vanilla filters PDodge.vetoAt mirrors still test exactly these facts (a new rule there = re-check the veto)
_pdf37, _fpw37 = " ".join(_bc37(PDF37, "handle")), " ".join(_bc37(FPW37, "handle"))
assert (PLA + ".hasSpawnProtection" in _pdf37 and WCFG + ".isPvpEnabled" in _pdf37 and CBC37 + ".isPlayerIncomingDamageDisabled" in _fpw37
        and INVU37 + ".getComponentType" in " ".join(_fu37) and INTG37 + ".getComponentType" in " ".join(_fu37)),     "the engine's damage filters changed - re-check PDodge.vetoAt (perfect dodge)"
_ti37 = _bc37("com.hypixel.hytale.server.core.entity.ItemUtils", "throwItem")
assert any(DIE37C + ".<init>" in x for x in _ti37) and any("ComponentAccessor.invoke" in x for x in _ti37), \
    "ItemUtils.throwItem no longer fires DropItemEvent$Drop - re-check RanchDropSys (the drop ledger)"
print("0.4.37 engine checks: FilterUnkillable cancels invulnerable damage (Filter group), pickups add a PickupItemComponent entity, throwItem "
      "fires DropItemEvent$Drop, effect durations readable")

# ---- Farm3: Orchard routing + the Farming average (pure; any thread)
fm3.addField(CtField.make('public static final String ORCH_DEFAULT = "%s";' % ORCH_DEF, fm3))
for _d37 in ("boolean AVG = false", "String[] ORCH = new String[] { %s }" % ", ".join('"%s"' % _x for _x in ORCH_DEF.split(",")),
             'String ORCH_TEXT = "%s"' % ORCH_DEF.replace(",", ", ")):
    fm3.addField(CtField.make("public static volatile %s;" % _d37, fm3))
fm3.addMethod(CtNewMethod.make(J14(r"""
public static String bare(String id) {
  if (id == null) return "";
  String t = id.trim();
  while (t.startsWith("*")) t = t.substring(1);
  return t;
}"""), fm3))
fm3.addMethod(CtNewMethod.make(J14(r"""
public static String[] parseIds(String v) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (v != null) {
    String[] ps = v.split(",");
    for (int i = 0; i < ps.length; i++) {
      String t = bare(ps[i]);
      if (t.length() > 0 && !out.contains(t)) out.add(t);
    }
  }
  String[] r = new String[out.size()];
  for (int j = 0; j < r.length; j++) r[j] = (String) out.get(j);
  return r;
}"""), fm3))
fm3.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  AVG = @PKG@.SkillCfg.bool(p, "overall.farmingAverage", false);
  String[] o = parseIds(p.getProperty("orchard.ids", ORCH_DEFAULT));
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < o.length; i++) {
    if (i > 0) sb.append(", ");
    sb.append(o[i]);
  }
  ORCH = o;
  ORCH_TEXT = sb.toString();
}"""), fm3))
fm3.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return "Orchard from " + (ORCH.length == 0 ? "nothing (orchard.ids is empty)" : ORCH_TEXT) + ", Farming in the Overall Level " + (AVG ? "= the average of Farming / Ranching / Orchard" : "= Farming alone");
}"""), fm3))
# a Farming award -> Orchard when the block id starts with an orchard.ids entry (a leading '*' of a state id ignored); any other slot unchanged
fm3.addMethod(CtNewMethod.make(J14(r"""
public static int route(int slot, String id) {
  if (slot != @PKG@.SkillDefs.FARMING || id == null) return slot;
  String[] o = ORCH;
  if (o == null || o.length == 0) return slot;
  String b = bare(id);
  for (int i = 0; i < o.length; i++) if (b.startsWith(o[i])) return @PKG@.SkillDefs.ORCHARD;
  return slot;
}"""), fm3))
fm3.addMethod(CtNewMethod.make(J14(r"""
public static boolean isFarm(int s) {
  return s == @PKG@.SkillDefs.FARMING || s == @PKG@.SkillDefs.RANCHING || s == @PKG@.SkillDefs.ORCHARD;
}"""), fm3))
# fix round: whose gathering pace + tree Wisdom an earned award uses - Ranching and Orchard share Farming's (one shared Farming tree, spec
# 5.3: gather.boost.skills "Farming" and the xp.farming Wisdom bonus cover them); any other slot its own
fm3.addMethod(CtNewMethod.make(J14(r"""
public static int paceSlot(int s) {
  return (s == @PKG@.SkillDefs.RANCHING || s == @PKG@.SkillDefs.ORCHARD) ? @PKG@.SkillDefs.FARMING : s;
}"""), fm3))
fm3.addMethod(CtNewMethod.make(J14(r"""
public static int avg3(int f, int r, int o) {
  int t = (f < 0 ? 0 : f) + (r < 0 ? 0 : r) + (o < 0 ? 0 : o);
  return t / 3;
}"""), fm3))
fm3.addMethod(CtNewMethod.make(J14(r"""
public static int lvIn(long[] d, int s) {
  if (d == null || s < 0 || s >= d.length) return 0;
  return @PKG@.SkillDefs.levelOf(s, d[s]);
}"""), fm3))
# the TABLE-level average (the Overall Level side, like Overall.sums: levels above 100 never count)
fm3.addMethod(CtNewMethod.make(J14(r"""
public static int avgOf(long[] d) {
  return avg3(lvIn(d, @PKG@.SkillDefs.FARMING), lvIn(d, @PKG@.SkillDefs.RANCHING), lvIn(d, @PKG@.SkillDefs.ORCHARD));
}"""), fm3))
# how much the average moved when slot s went from oldLv to its level in d (the other two from d); 0 for any other slot
fm3.addMethod(CtNewMethod.make(J14(r"""
public static int avgDelta(long[] d, int s, int oldLv, int newLv) {
  int f = lvIn(d, @PKG@.SkillDefs.FARMING);
  int r = lvIn(d, @PKG@.SkillDefs.RANCHING);
  int o = lvIn(d, @PKG@.SkillDefs.ORCHARD);
  int now = avg3(f, r, o);
  if (s == @PKG@.SkillDefs.FARMING) f = oldLv;
  else if (s == @PKG@.SkillDefs.RANCHING) r = oldLv;
  else if (s == @PKG@.SkillDefs.ORCHARD) o = oldLv;
  else return 0;
  return now - avg3(f, r, o);
}"""), fm3))

# ---- PDodge part 1: the acro.perfectDodge rows, the window maths, the per-player state (counter-hit until, last rewarded roll, last chat line)
for _d37 in ("boolean ON = true", "long WINDOW_MS = 50L", "long COUNTER_MS = 750L", "double MULT = 1.25", "long XP = 5L", "long MAX_PM = 50L"):
    pdg.addField(CtField.make("public static volatile %s;" % _d37, pdg))
for _d37 in ("java.util.concurrent.ConcurrentHashMap STATE = new java.util.concurrent.ConcurrentHashMap()",
             "java.util.concurrent.atomic.AtomicLong PERFECT = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong BLOCKED = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong COUNTERS = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong VETOED = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong PARRY_SKIP = new java.util.concurrent.atomic.AtomicLong()",   # fix round 2
             'String PARRY_FX = "PP_Counterattack_Ready"',   # fix round 2: Perfect Parries' (pack mod, by runtime id) counter-ready effect
             "java.util.HashMap XPWIN = new java.util.HashMap()",
             "long ONE_PER_ROLL_MS = 300L", "long LINE_MS = 1500L"):
    pdg.addField(CtField.make("public static final %s;" % _d37, pdg))
pdg.addMethod(CtNewMethod.make(J14(r"""
public static long clampL(long v, long lo, long hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}"""), pdg))
pdg.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "acro.perfectDodge", true);
  WINDOW_MS = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.windowMs", 50L), 0L, 250L);
  COUNTER_MS = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.counterMs", 750L), 0L, 10000L);
  double m = @PKG@.SkillCfg.dbl(p, "acro.perfectDodge.counterMultiplier", 1.25);
  MULT = (Double.isNaN(m) || Double.isInfinite(m)) ? 1.25 : (m < 1.0 ? 1.0 : (m > 5.0 ? 5.0 : m));
  XP = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.xp", 5L), 0L, 100000L);
  MAX_PM = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.maxXpPerMinute", 50L), 0L, 1000000000L);   // fix round: the XP cap
}"""), pdg))
pdg.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (!ON) return "off";
  return "on (a roll at most " + WINDOW_MS + " ms before a hit: no damage, +" + XP + " Acrobatics XP from monsters' hits" + (MAX_PM > 0L ? " (at most " + MAX_PM + " a minute)" : "") + (COUNTER_MS > 0L && MULT > 1.0 ? ", the next hit within " + COUNTER_MS + " ms x" + MULT : "") + ")";
}"""), pdg))
# the perfect-dodge window: age = ms since the roll began, -1 = no roll / cannot tell
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean inWindow(long age, long win) {
  return age >= 0L && age <= win;
}"""), pdg))
# ms since a roll effect began, from its durations in seconds (the engine counts remaining down by each tick's dt); -1 = cannot tell: no
# initial, a negative remaining, or remaining ABOVE the initial (OverlapBehavior Extend - a chained roll added time; its start is unknown)
pdg.addMethod(CtNewMethod.make(J14(r"""
public static long ageOf(float initial, float remaining) {
  if (!(initial > 0.0f) || remaining < 0.0f || remaining > initial + 0.0005f) return -1L;
  return (long) Math.floor((double) (initial - remaining) * 1000.0 + 0.5);
}"""), pdg))
pdg.addMethod(CtNewMethod.make(J14(r"""
public static long[] pst(java.util.UUID u) {
  long[] s = (long[]) STATE.get(u);
  if (s != null) return s;
  long[] n = new long[3];
  Object o = STATE.putIfAbsent(u, n);
  return o == null ? n : (long[]) o;
}"""), pdg))
# a blocked hit: true = a NEW perfect dodge (rewarded: the counter-hit window opens), false = this roll was rewarded already
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean mark(java.util.UUID u, long now) {
  long[] s = pst(u);
  BLOCKED.incrementAndGet();
  if (s[1] > 0L && now >= s[1] && now - s[1] < ONE_PER_ROLL_MS) return false;
  s[1] = now;
  PERFECT.incrementAndGet();
  if (COUNTER_MS > 0L && MULT > 1.0) s[0] = now + COUNTER_MS;
  return true;
}"""), pdg))
# the attacker's damage factor now: MULT inside an open counter-hit window (the window is used up), else 1.0
pdg.addMethod(CtNewMethod.make(J14(r"""
public static double counter(java.util.UUID u, long now) {
  if (u == null || !ON) return 1.0;
  long[] s = (long[]) STATE.get(u);
  if (s == null || s[0] <= 0L) return 1.0;
  long until = s[0];
  s[0] = 0L;
  if (now > until || !(MULT > 1.0)) return 1.0;
  COUNTERS.incrementAndGet();
  return MULT;
}"""), pdg))
# fix round: the per-player Acrobatics XP minute cap (acro.perfectDodge.maxXpPerMinute; 0 = no cap) - how much of amt may be paid now
pdg.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long allowXp(java.util.UUID u, long amt, long now) {
  if (u == null || amt <= 0L) return 0L;
  long cap = MAX_PM;
  if (cap <= 0L) return amt;
  long[] w = (long[]) XPWIN.get(u);
  if (w == null || now - w[0] >= 60000L) {
    w = new long[] { now, 0L };
    XPWIN.put(u, w);
  }
  long left = cap - w[1];
  if (left <= 0L) return 0L;
  long ok = amt < left ? amt : left;
  w[1] = w[1] + ok;
  return ok;
}"""), pdg))
pdg.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void retainXp(java.util.Set online) {
  XPWIN.keySet().retainAll(online);
}"""), pdg))
# fix round: would one of the engine's OTHER damage filters cancel this hit anyway? (mirrors DamageSystems$FilterUnkillable's dead /
# Invulnerable / Intangible part, $PlayerDamageFilterSystem's spawn protection + PvP-off and $FilterPlayerWorldConfig's player damage off).
# 0 = no, 1 dead / Invulnerable / Intangible, 2 spawn protection, 3 player damage off in this world, 4 a player's hit with PvP off.
# Such a hit is never a perfect dodge (no reward, no counter-hit, no chat line) - the engine blocks it on its own.
pdg.addMethod(CtNewMethod.make(J14(r"""
public static int veto(boolean deadOrInvul, boolean spawnProt, boolean noDamage, boolean byPlayer, boolean pvpOn) {
  if (deadOrInvul) return 1;
  if (spawnProt) return 2;
  if (noDamage) return 3;
  if (byPlayer && !pvpOn) return 4;
  return 0;
}"""), pdg))
pdg.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  STATE.keySet().retainAll(online);
  retainXp(online);
}"""), pdg))

# ---- Ranch part 1: ranching.* rows, the item table, the per-world drop ledger, the per-player minute cap
rch.addField(CtField.make('public static final String DEFAULT_ITEMS = "%s";' % RANCH_DEF, rch))
for _d37 in ("boolean ON = true", "java.util.HashMap XP = new java.util.HashMap()", 'String TEXT = ""', "long PER_MIN = %sL" % RANCH_PM_DEF,
             "boolean SEEN = false", "boolean FAILED = false"):
    rch.addField(CtField.make("public static volatile %s;" % _d37, rch))
for _d37 in ("long LEDGER_MS = 600000L", "java.util.HashMap LEDGER = new java.util.HashMap()", "java.util.HashMap WIN = new java.util.HashMap()",
             "java.util.concurrent.atomic.AtomicLong PAID = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong SKIPPED = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong CAPPED = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong DROP_CANCELLED = new java.util.concurrent.atomic.AtomicLong()"):   # fix round 2
    rch.addField(CtField.make("public static final %s;" % _d37, rch))
rch.addMethod(CtNewMethod.make(J14(r"""
public static long num(String v) {
  try { return Long.parseLong(v.trim()); } catch (Throwable t) { return -1L; }
}"""), rch))
rch.addMethod(CtNewMethod.make(J14(r"""
public static java.util.HashMap parse(String v) {
  java.util.HashMap m = new java.util.HashMap();
  if (v == null) return m;
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    int c = t.lastIndexOf(':');
    if (c <= 0) continue;
    String id = t.substring(0, c).trim();
    long x = num(t.substring(c + 1));
    if (id.length() == 0 || x <= 0L) continue;
    m.put(id, Long.valueOf(x > 1000000L ? 1000000L : x));
  }
  return m;
}"""), rch))
rch.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "ranching.pickupXp", true);
  java.util.HashMap m = parse(p.getProperty("ranching.items", DEFAULT_ITEMS));
  XP = m;
  TEXT = m.size() + " item ids";
  long pm = @PKG@.SkillCfg.lng(p, "ranching.maxXpPerMinute", 200L);
  PER_MIN = pm < 0L ? 0L : (pm > 1000000000L ? 1000000000L : pm);
}"""), rch))
rch.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return ON ? "Ranching XP from pickups on (" + TEXT + ", at most " + (PER_MIN > 0L ? PER_MIN + " a minute" : "no cap") + ")" : "Ranching XP from pickups off";
}"""), rch))
rch.addMethod(CtNewMethod.make(J14(r"""
public static long xpOf(String id) {
  if (id == null) return 0L;
  Object o = XP.get(id);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}"""), rch))
# a player dropped n of id in world w: the next n pickups of id in w pay nothing (kept LEDGER_MS after the last drop)
rch.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void dropped(String w, String id, long n, long now) {
  if (id == null || n <= 0L || xpOf(id) <= 0L) return;
  String k = String.valueOf(w) + "|" + id;
  long[] e = (long[]) LEDGER.get(k);
  if (e == null || now - e[1] > LEDGER_MS) {
    e = new long[] { 0L, now };
    LEDGER.put(k, e);
  }
  e[0] = e[0] + n > 1000000000L ? 1000000000L : e[0] + n;
  e[1] = now;
}"""), rch))
# of n picked-up items of id in world w: how many no player dropped there (the ledger takes the rest)
rch.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long fresh(String w, String id, long n, long now) {
  if (id == null || n <= 0L) return 0L;
  String k = String.valueOf(w) + "|" + id;
  long[] e = (long[]) LEDGER.get(k);
  if (e == null) return n;
  if (now - e[1] > LEDGER_MS) {
    LEDGER.remove(k);
    return n;
  }
  long take = e[0] < n ? e[0] : n;
  e[0] = e[0] - take;
  if (e[0] <= 0L) LEDGER.remove(k);
  return n - take;
}"""), rch))
# the per-player minute cap: how much of amt may be paid now (0 = none); ranching.maxXpPerMinute 0 = no cap
rch.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long allow(java.util.UUID u, long amt, long now) {
  if (u == null || amt <= 0L) return 0L;
  long cap = PER_MIN;
  if (cap <= 0L) return amt;
  long[] w = (long[]) WIN.get(u);
  if (w == null || now - w[0] >= 60000L) {
    w = new long[] { now, 0L };
    WIN.put(u, w);
  }
  long left = cap - w[1];
  if (left <= 0L) return 0L;
  long ok = amt < left ? amt : left;
  w[1] = w[1] + ok;
  return ok;
}"""), rch))
rch.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void retain(java.util.Set online) {
  WIN.keySet().retainAll(online);
}"""), rch))
# the base Ranching XP for n picked-up items of id in world w (before the xp multiplier and the cap); 0 = nothing to pay
rch.addMethod(CtNewMethod.make(J14(r"""
public static long base(String w, String id, long n, long now) {
  if (!ON || n <= 0L) return 0L;
  long x = xpOf(id);
  if (x <= 0L) return 0L;
  long f = fresh(w, id, n, now);
  if (f <= 0L) {
    SKIPPED.incrementAndGet();
    return 0L;
  }
  if (f > 1000000L) f = 1000000L;
  return x * f;
}"""), rch))

'''
rep('''# ================= SkillLv (0.4.16): the levels.skill table - own XP-per-level lists per non-class skill (before SkillCfg.load) =================
''', R37B + '''# ================= SkillLv (0.4.16): the levels.skill table - own XP-per-level lists per non-class skill (before SkillCfg.load) =================
''')
rep('''    {PKG}.SkillLv.read(p);      // 0.4.16: own XP-per-level lists (the levels.skill table; Mining by default)
''', '''    {PKG}.SkillLv.read(p);      // 0.4.16: own XP-per-level lists (the levels.skill table; Mining by default)
    {PKG}.PDodge.read(p);       // 0.4.37: perfect dodge (acro.perfectDodge*)
    {PKG}.Ranch.read(p);        // 0.4.37: Ranching XP from pickups (ranching.*)
    {PKG}.Farm3.read(p);        // 0.4.37: Orchard routing + the Farming average (orchard.ids, overall.farmingAverage)
''')

# ---------------------------------------------------------------- region (c): the world-thread parts + the systems (after Acro / SkillXp / event_system)
R37C = r'''# ================= 0.4.37 PERFECT DODGE + RANCHING part 2: world-thread logic and the ECS systems =================
# PDodge.rollAge: ms since the newest of OUR roll effects began on this entity (the 4 effects Acro.dodge counts), -1 = none / cannot tell
pdg.addMethod(CtNewMethod.make(J14(r"""
public static long rollAge(@ECC@ ecc) {
  if (ecc == null) return -1L;
  @AEE@[] all = ecc.getAllActiveEntityEffects();
  if (all == null) return -1L;
  int li = @EFX@.getAssetMap().getIndex("Dodge_Left");
  int ri = @EFX@.getAssetMap().getIndex("Dodge_Right");
  int fi = @EFX@.getAssetMap().getIndex("Dodge_Forward");
  int bi = @EFX@.getAssetMap().getIndex("Dodge_Back");
  long best = -1L;
  for (int i = 0; i < all.length; i++) {
    @AEE@ a = all[i];
    if (a == null) continue;
    int x = a.getEntityEffectIndex();
    if (x == Integer.MIN_VALUE || (x != li && x != ri && x != fi && x != bi)) continue;
    long g = ageOf(a.getInitialDuration(), a.getRemainingDuration());
    if (g >= 0L && (best < 0L || g < best)) best = g;
  }
  return best;
}"""), pdg))
# the chat line; xp = the Acrobatics XP this dodge really pays (fix round: the line never promises XP that is not paid)
pdg.addMethod(CtNewMethod.make(J14(r"""
public static String line(long xp) {
  String t = "Perfect dodge!";
  if (COUNTER_MS > 0L && MULT > 1.0) t = t + " Your next hit within " + @PKG@.DivCfg.num((double) COUNTER_MS / 1000.0) + " s deals x" + @PKG@.DivCfg.num(MULT) + " damage.";
  if (xp > 0L) t = t + "  +" + xp + " Acrobatics XP";
  return t;
}"""), pdg))
# fix round: is the attacker a player (a Player or PlayerRef component)? Unreadable = not a player
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean isPlayer(@ST@ st, @REF@ att) {
  try {
    if (att == null || !att.isValid()) return false;
    return st.getComponent(att, @PLA@.getComponentType()) != null || st.getComponent(att, @PR@.getComponentType()) != null;
  } catch (Throwable t) { return false; }
}"""), pdg))
# fix round: the engine facts for veto() read on the world thread; each unreadable fact counts as "not blocked"
pdg.addMethod(CtNewMethod.make(J14(r"""
public static int vetoAt(@ST@ st, @REF@ r, boolean byPlayer) {
  boolean dead = false;
  boolean sp = false;
  boolean nd = false;
  boolean pvp = true;
  try {
    @ARC37@ a = st.getArchetype(r);
    dead = a != null && (a.contains(@DTH@.getComponentType()) || a.contains(@INVU37@.getComponentType()) || a.contains(@INTG37@.getComponentType()));
  } catch (Throwable t) { dead = false; }
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    sp = p != null && p.hasSpawnProtection();
  } catch (Throwable t) { sp = false; }
  @WLD@ w = null;
  try {
    Object ext = st.getExternalData();
    if (ext instanceof @EST@) w = ((@EST@) ext).getWorld();
  } catch (Throwable t) { w = null; }
  if (w != null) {
    try { nd = w.getGameplayConfig().getCombatConfig().isPlayerIncomingDamageDisabled(); } catch (Throwable t) { nd = false; }
    if (byPlayer) {
      try { pvp = w.getWorldConfig().isPvpEnabled(); } catch (Throwable t) { pvp = true; }
    }
  }
  return veto(dead, sp, nd, byPlayer, pvp);
}"""), pdg))
# fix round: a perfect dodge also removes the hit's knockback (as the engine's own filters do when they cancel: PlayerDamageFilterSystem
# .cancelKnockback). true = the hit carried knockback and its removal was queued
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean dropKnockback(@DMG@ d, @REF@ r, @CB@ buf) {
  if (d == null || r == null || buf == null) return false;
  Object kb = d.getIfPresentMetaObject(@DMG@.KNOCKBACK_COMPONENT);
  if (kb == null) return false;
  try { buf.tryRemoveComponent(r, @KBC37@.getComponentType()); } catch (Throwable t) { return false; }
  return true;
}"""), pdg))
# fix round 2: does this entity carry the active effect with asset id fx? (no such asset = false - e.g. Perfect Parries not installed)
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean hasFx(@ECC@ ecc, String fx) {
  if (ecc == null || fx == null) return false;
  int want = @EFX@.getAssetMap().getIndex(fx);
  if (want == Integer.MIN_VALUE || want < 0) return false;
  @AEE@[] all = ecc.getAllActiveEntityEffects();
  if (all == null) return false;
  for (int i = 0; i < all.length; i++) {
    if (all[i] != null && all[i].getEntityEffectIndex() == want) return true;
  }
  return false;
}"""), pdg))
# a perfect dodge of player pr (world thread, from PDodgeSys - the hit is already cancelled): one reward per roll - the counter-hit window,
# the Acrobatics XP (into Acro's pending XP, paid by its 1 s tick: acro.enabled, not creative, not during a Monk move; fix round: only for a
# MONSTER's hit (mob = true) and at most acro.perfectDodge.maxXpPerMinute a minute), a throttled chat line naming the XP really paid.
# Returns the XP paid.
pdg.addMethod(CtNewMethod.make(J14(r"""
public static long perfect(@PR@ pr, @ST@ st, @REF@ r, long now, boolean mob) {
  java.util.UUID u = pr.getUuid();
  if (!mark(u, now)) return 0L;
  long paid = 0L;
  if (mob && XP > 0L && @PKG@.AcroCfg.ENABLED && !@PKG@.SkillXp.creative(st, r) && !@PKG@.Acro.monkMove(u, now)) {
    paid = allowXp(u, XP, now);
    if (paid > 0L) {
      double[] a = @PKG@.Acro.state(u);
      a[11] = a[11] + (double) paid;
    }
  }
  long[] s = pst(u);
  if (now - s[2] >= LINE_MS && @PKG@.SkillStore.notifyOn(u, "skills.perfectDodge")) {
    s[2] = now;
    pr.sendMessage(@MSG@.raw(line(paid)).color("#9fd8ff"));
  }
  return paid;
}"""), pdg))
# PDodgeSys: DamageEventSystem in the FILTER group, players only, BEFORE DamageSystems$FilterUnkillable (fact F1); PDodgeSysU = the
# unordered fallback (one registerSystem per class) - it may run after the i-frames' cancel and then sees no hit inside a roll
pds.addField(CtField.make("public java.util.Set deps;", pds))
pds.addField(CtField.make("public static boolean FAILED_ONCE = false;", pds))
pds.addField(CtField.make('public static final String FU = "%s";' % FU37, pds))
pds.addConstructor(CtNewConstructor.make(J14(r"""
public PDodgeSys(boolean ordered) {
  super();
  if (ordered) this.deps = java.util.Collections.singleton(new @SDEP@(@DORD@.BEFORE, Class.forName(FU)));
  else this.deps = java.util.Collections.EMPTY_SET;
}"""), pds))
pds.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}"""), pds))
pds.addMethod(CtNewMethod.make(J14(r"""
public @SYG@ getGroup() {
  return @DMM@.get().getFilterDamageGroup();
}"""), pds))
pds.addMethod(CtNewMethod.make(J14(r"""
public java.util.Set getDependencies() {
  return this.deps;
}"""), pds))
pds.addMethod(CtNewMethod.make(J14(r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled() || !@PKG@.PDodge.ON) return;
    if (!(d.getAmount() > 0.0f)) return;   // fix round: a hit that does no damage is nothing to dodge
    Object src = d.getSource();
    if (!(src instanceof @DES@)) return;
    @REF@ att = ((@DES@) src).getRef();
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null || att == null || r.equals(att)) return;
    @DCS@ c = d.getCause();
    if (c != null && c.doesBypassResistances()) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @ECC@ ecc = (@ECC@) st.getComponent(r, @ECC@.getComponentType());
    long age = @PKG@.PDodge.rollAge(ecc);
    if (!@PKG@.PDodge.inWindow(age, @PKG@.PDodge.WINDOW_MS)) return;
    boolean byPlayer = @PKG@.PDodge.isPlayer(st, att);
    if (@PKG@.PDodge.vetoAt(st, r, byPlayer) != 0) {   // fix round: the engine blocks this hit anyway - not a perfect dodge
      @PKG@.PDodge.VETOED.incrementAndGet();
      return;
    }
    d.setCancelled(true);
    @PKG@.PDodge.dropKnockback(d, r, buf);
    @PKG@.PDodge.perfect(pr, st, r, System.currentTimeMillis(), !byPlayer);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("perfect dodge failed (logged once): " + t); }
  }
}"""), pds))
pdsu.addConstructor(CtNewConstructor.make("public PDodgeSysU() { super(false); }", pdsu))
# PCounterSys: the counter-hit - DamageEventSystem in the FILTER group, any target (CombatDmgSys's shape): the attacker (EntitySource ref,
# projectiles: their shooter) with a PlayerRef and an open counter-hit window deals x MULT; the window is used up
pcs.addConstructor(CtNewConstructor.make("public PCounterSys() { super(); }", pcs))
pcs.addField(CtField.make("public static boolean FAILED_ONCE = false;", pcs))
pcs.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return @QRY@.any();
}"""), pcs))
pcs.addMethod(CtNewMethod.make(J14(r"""
public @SYG@ getGroup() {
  return @DMM@.get().getFilterDamageGroup();
}"""), pcs))
pcs.addMethod(CtNewMethod.make(J14(r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled() || !@PKG@.PDodge.ON) return;
    Object src = d.getSource();
    if (!(src instanceof @DES@)) return;
    @REF@ att = ((@DES@) src).getRef();
    if (att == null || !att.isValid()) return;
    @REF@ tr = chunk.getReferenceTo(idx);
    if (tr != null && tr.equals(att)) return;
    @PR@ pr = (@PR@) buf.getComponent(att, @PR@.getComponentType());
    if (pr == null) return;
    float a = d.getAmount();
    if (!(a > 0.0f)) return;
    double m = @PKG@.PDodge.counter(pr.getUuid(), System.currentTimeMillis());
    if (!(m > 1.0)) return;
    // fix round 2: no stacking with Perfect Parries (pack mod) - a hit that is its counterattack (PP_Counterattack_Ready on the attacker)
    // keeps only the parry's own multiplier; our counter-hit is used up by it
    try {
      if (@PKG@.PDodge.hasFx((@ECC@) buf.getComponent(att, @ECC@.getComponentType()), @PKG@.PDodge.PARRY_FX)) {
        @PKG@.PDodge.PARRY_SKIP.incrementAndGet();
        return;
      }
    } catch (Throwable pt) { }
    d.setAmount((float) (a * m));
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("perfect dodge counter-hit failed (logged once): " + t); }
  }
}"""), pcs))

# RanchTask: the Ranching award on the player's world thread (after every system saw the pickup): the same profile, not creative, the minute cap
rtk.addInterface(pool.get("java.lang.Runnable"))
for _d37 in ("java.util.UUID u", "long base", "String key", "Object drop", "String world"):
    rtk.addField(CtField.make("public %s;" % _d37, rtk))
rtk.addConstructor(CtNewConstructor.make("public RanchTask(java.util.UUID u, long base, String key) { this.u = u; this.base = base; this.key = key; }", rtk))
# fix round 2: the DROP mode - a player's DropItemEvent$Drop goes into the ledger only once every system has seen the event (a later
# system - SkyyIslands' guard, SkyyVault, a pack mod - may still cancel or change it after RanchDropSys); run on the world queue
rtk.addConstructor(CtNewConstructor.make("public RanchTask(Object drop, String world) { this.drop = drop; this.world = world; this.base = 0L; }", rtk))
# Ranch.dropDone: the deferred ledger entry of a player's drop event - nothing for a cancelled drop; the stack the event ends with
rch.addMethod(CtNewMethod.make(J14(r"""
public static boolean dropDone(Object ev, String w) {
  if (!(ev instanceof @DIE37@)) return false;
  @DIE37@ e = (@DIE37@) ev;
  if (e.isCancelled()) {
    DROP_CANCELLED.incrementAndGet();
    return false;
  }
  @IS@ is = e.getItemStack();
  if (is == null || is.isEmpty()) return false;
  dropped(w, is.getItemId(), (long) is.getQuantity(), System.currentTimeMillis());
  return true;
}"""), rch))
rtk.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  try {
    if (this.drop != null) {   // fix round 2: the deferred drop ledger entry
      @PKG@.Ranch.dropDone(this.drop, this.world);
      return;
    }
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (this.key == null || !this.key.equals(@PKG@.SkillStore.pkey(this.u))) return;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return;
    if (@PKG@.SkillXp.creative(r.getStore(), r)) return;
    // fix round: the xp multiplier, Farming's gathering pace (at the Ranching level) and the Farming tree Wisdom FIRST, then the minute cap
    // on that final number - ranching.maxXpPerMinute is what really lands - paid exactly (gain3 without a second bonus)
    long full = @PKG@.SkillBonus.boost(this.u, @PKG@.SkillDefs.FARMING, @PKG@.GatherPace.applyAt(this.u, @PKG@.SkillDefs.FARMING, @PKG@.SkillDefs.RANCHING, @PKG@.SkillCfg.scaled(this.base)));
    long amt = @PKG@.Ranch.allow(this.u, full, System.currentTimeMillis());
    if (amt <= 0L) { @PKG@.Ranch.CAPPED.incrementAndGet(); return; }
    @PKG@.SkillXp.gain3(pr, @PKG@.SkillDefs.RANCHING, amt, true, false);
    @PKG@.Ranch.PAID.addAndGet(amt);
    if (!@PKG@.Ranch.SEEN) { @PKG@.Ranch.SEEN = true; @PKG@.SkillCfg.info("Ranching XP from pickups reaches SkyySkills (the first one was paid: " + amt + " XP)"); }
  } catch (Throwable t) { @PKG@.SkillCfg.warn("Ranching award failed: " + t); }
}"""), rtk))
# fix round: the quantity a picked-up item entity stands for: its stack's quantity after a full pickup, else 1
rch.addMethod(CtNewMethod.make(J14(r"""
public static int qtyOf(boolean full, int q) {
  if (q <= 0) return 0;
  return full ? q : 1;
}"""), rch))
# Ranch.picked (world thread, RanchPickSys): a picked-up item entity for player pr -> the base XP (the ledger first) -> a RanchTask
rch.addMethod(CtNewMethod.make(J14(r"""
public static boolean picked(@ST@ st, @PR@ pr, String id, int qty) {
  if (!ON || st == null || pr == null || id == null || qty <= 0 || xpOf(id) <= 0L) return false;
  Object ext = st.getExternalData();
  if (!(ext instanceof @EST@)) return false;
  @WLD@ w = ((@EST@) ext).getWorld();
  if (w == null) return false;
  long b = base(w.getName(), id, (long) qty, System.currentTimeMillis());
  if (b <= 0L) return false;
  java.util.UUID u = pr.getUuid();
  w.execute(new @PKG@.RanchTask(u, b, @PKG@.SkillStore.pkey(u)));
  return true;
}"""), rch))
# RanchPickSys: a RefSystem on PickupItemComponent (fact F2) - the picked-up item entity as it is added (never on a chunk LOAD)
rps.addConstructor(CtNewConstructor.make("public RanchPickSys() { super(); }", rps))
rps.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return (@QRY@) @PIC37@.getComponentType();
}"""), rps))
rps.addMethod(CtNewMethod.make(J14(r"""
public void onEntityAdded(@REF@ ref, @ADR37@ why, @ST@ st, @CB@ cb) {
  try {
    if (!@PKG@.Ranch.ON || why == @ADR37@.LOAD || ref == null) return;
    @PIC37@ pc = (@PIC37@) st.getComponent(ref, @PIC37@.getComponentType());
    @ICO37@ ic = (@ICO37@) st.getComponent(ref, @ICO37@.getComponentType());
    if (pc == null || ic == null) return;
    @REF@ t = pc.getTargetRef();
    if (t == null || !t.isValid()) return;
    @PR@ pr = (@PR@) st.getComponent(t, @PR@.getComponentType());
    if (pr == null) return;
    @IS@ is = ic.getItemStack();
    if (is == null || is.isEmpty()) return;
    // fix round: only a FULL ground pickup (removedByPlayerPickup, copied by the clone) carries the picked quantity; a PARTIAL one carries
    // what is LEFT on the ground and an F-pickup a new 1-item stack - both count as 1 item (never more than was picked)
    @PKG@.Ranch.picked(st, pr, is.getItemId(), @PKG@.Ranch.qtyOf(ic.isRemovedByPlayerPickup(), is.getQuantity()));
  } catch (Throwable e) {
    if (!@PKG@.Ranch.FAILED) { @PKG@.Ranch.FAILED = true; @PKG@.SkillCfg.warn("Ranching pickup check failed (logged once): " + e); }
  }
}"""), rps))
rps.addMethod(CtNewMethod.make(J14(r"""
public void onEntityRemove(@REF@ ref, @RMR37@ why, @ST@ st, @CB@ cb) {
}"""), rps))
# RanchDropSys: DropItemEvent$Drop on a PLAYER (fact F3) -> the drop ledger of that world
event_system(rds, "RanchDropSys", DIE37C, f"""
    {DIE37} e = ({DIE37}) ev;
    if (!{PKG}.Ranch.ON) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {IS} is = e.getItemStack();
    if (is == null || is.isEmpty()) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    if (e.isCancelled()) return;   // fix round 2: a cancelled drop leaves the item in the inventory - no ledger entry
    w.execute(new {PKG}.RanchTask(e, w.getName()));   // fix round 2: the ledger entry after every system saw the drop (a later cancel = none)""")

'''
rep('''# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4): explosions + fire fire EnvironmentBreakBlockEvent on the ENTITY store =================
''', R37C + '''# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4): explosions + fire fire EnvironmentBreakBlockEvent on the ENTITY store =================
''')

# ---------------------------------------------------------------- Acro prune: the new per-player maps
rep('''    {PKG}.BridgeXp.retain(online);
''', '''    {PKG}.BridgeXp.retain(online);
    {PKG}.PDodge.retain(online);   // 0.4.37: perfect dodge state of players who left
    {PKG}.Ranch.retain(online);    // 0.4.37: the Ranching minute windows
''')

# ---------------------------------------------------------------- Orchard routing at the three Farming award points
rep('''    {PKG}.SkillXp.gain(pr, (int) this.rule[0], bamt);
''', '''    {BTY} rbt = this.ev.getBlockType();   // 0.4.37: Orchard routing (orchard.ids) - the XP only; the drops below stay Farming's
    {PKG}.SkillXp.gain(pr, {PKG}.Farm3.route((int) this.rule[0], rbt == null ? null : rbt.getId()), bamt);
''')
rep('''      {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.FARMING, this.amount);
''', '''      {PKG}.SkillXp.gain(pr, {PKG}.Farm3.route({PKG}.SkillDefs.FARMING, this.ripe), this.amount);   // 0.4.37: Orchard routing
''')
rep('''    if (amt > 0L) @PKG@.SkillXp.gain(pr, @PKG@.SkillDefs.FARMING, amt);
''', '''    if (amt > 0L) @PKG@.SkillXp.gain(pr, @PKG@.Farm3.route(@PKG@.SkillDefs.FARMING, (String) info[2]), amt);   // 0.4.37: Orchard routing
''')

# ---------------------------------------------------------------- fix round: Orchard / Ranching XP keep Farming's gathering pace + Wisdom
rep('''# the Stats page's "Boosts right now" line of a paced skill (null = no line: not listed, or x1 at this level)
''', '''# fix round (0.4.37): applyAt = apply with the pace switch of cfgSlot (gather.boost.skills) at the level of lvSlot - Orchard / Ranching awards
# use Farming's switch at their OWN level (Farm3.paceSlot); apply(u, s, amt) == applyAt(u, s, s, amt)
gpc.addMethod(CtNewMethod.make(J14(r"""
public static long applyAt(java.util.UUID u, int cfgSlot, int lvSlot, long amt) {
  if (amt <= 0L || u == null || !on(cfgSlot)) return amt;
  double m = mult(@PKG@.SkillStore.level(u, lvSlot));
  if (m == 1.0) return amt;
  if (!(m > 0.0)) return 0L;
  double x = (double) amt * m;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}"""), gpc))
# the Stats page's "Boosts right now" line of a paced skill (null = no line: not listed, or x1 at this level)
''')
rep('''  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, {PKG}.GatherPace.apply(u, skill, amount));   // 0.4.14: the gathering pace, then the tree Wisdom
''', '''  int bsl = {PKG}.Farm3.paceSlot(skill);   // 0.4.37 fix round: Orchard / Ranching use Farming's pace switch + Wisdom (one shared Farming tree)
  if (bonus) amount = {PKG}.SkillBonus.boost(u, bsl, {PKG}.GatherPace.applyAt(u, bsl, skill, amount));   // 0.4.14: the gathering pace, then the tree Wisdom
''')

# ---------------------------------------------------------------- bridge: skill:<uuid> + skill:farmavg:<uuid>, skill:fn:level farmingavg, grants
rep('''  int[] order = new int[] {{ {PKG}.SkillDefs.MINING, {PKG}.SkillDefs.FORAGING, {PKG}.SkillDefs.FARMING, {PKG}.SkillDefs.ACROBATICS, {PKG}.SkillDefs.ALCHEMY, {PKG}.SkillDefs.SMITHING, {PKG}.SkillDefs.COOKING, {PKG}.SkillDefs.EXPLORATION }};''',
    '''  int[] order = new int[] {{ {PKG}.SkillDefs.MINING, {PKG}.SkillDefs.FORAGING, {PKG}.SkillDefs.FARMING, {PKG}.SkillDefs.ACROBATICS, {PKG}.SkillDefs.ALCHEMY, {PKG}.SkillDefs.SMITHING, {PKG}.SkillDefs.COOKING, {PKG}.SkillDefs.EXPLORATION, {PKG}.SkillDefs.FISHING, {PKG}.SkillDefs.RANCHING, {PKG}.SkillDefs.ORCHARD }};   // 0.4.37: + Fishing, Ranching, Orchard''')
rep('''    bridge().put("skill:" + u.toString(), levelsOf(u, d));
''', '''    bridge().put("skill:" + u.toString(), levelsOf(u, d));
    String fk = pkey(u);   // 0.4.37: skill:farmavg:<uuid> = floor((Farming + Ranching + Orchard) / 3) at the profile's levels (its own key)
    int fa = (com.skyy.skills.SkillCap.level(fk, com.skyy.skills.SkillDefs.FARMING, d[com.skyy.skills.SkillDefs.FARMING]) + com.skyy.skills.SkillCap.level(fk, com.skyy.skills.SkillDefs.RANCHING, d[com.skyy.skills.SkillDefs.RANCHING]) + com.skyy.skills.SkillCap.level(fk, com.skyy.skills.SkillDefs.ORCHARD, d[com.skyy.skills.SkillDefs.ORCHARD])) / 3;
    bridge().put("skill:farmavg:" + u.toString(), Integer.valueOf(fa));
''')
assert 'PKG = "com.skyy.skills"' in s
rep('''    if ("overall".equalsIgnoreCase(String.valueOf(a[1]).trim())) return Integer.valueOf({PKG}.Overall.levelOf((java.util.UUID) a[0]));
''', '''    if ("overall".equalsIgnoreCase(String.valueOf(a[1]).trim())) return Integer.valueOf({PKG}.Overall.levelOf((java.util.UUID) a[0]));
    if ("farmingavg".equalsIgnoreCase(String.valueOf(a[1]).trim())) {{   // 0.4.37: the Farming average (spec 5.3)
      java.util.UUID fu = (java.util.UUID) a[0];
      return Integer.valueOf(({PKG}.SkillStore.level(fu, {PKG}.SkillDefs.FARMING) + {PKG}.SkillStore.level(fu, {PKG}.SkillDefs.RANCHING) + {PKG}.SkillStore.level(fu, {PKG}.SkillDefs.ORCHARD)) / 3);
    }}
''')
rep('''    sb.append({PKG}.SkillDefs.LABELS[{PKG}.SkillDefs.EXPLORATION]);
  }}
  GRANT = g;
''', '''    sb.append({PKG}.SkillDefs.LABELS[{PKG}.SkillDefs.EXPLORATION]);
  }}
  int[] g37 = new int[] {{ {PKG}.SkillDefs.FISHING, {PKG}.SkillDefs.RANCHING, {PKG}.SkillDefs.ORCHARD }};   // 0.4.37: always grantable (SkyyFishing catches; shards later)
  for (int g37i = 0; g37i < g37.length; g37i++) {{
    if (g[g37[g37i]]) continue;
    g[g37[g37i]] = true;
    if (sb.length() > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[g37[g37i]]);
  }}
  GRANT = g;
''')

# ---------------------------------------------------------------- Overall: the Farming average (overall.farmingAverage), Fishing allowed in overall.skills
rep('''    if (s < 0 || s >= {PKG}.SkillDefs.N) continue;
    sum += {PKG}.SkillDefs.levelOf(s, d[s]);
''', '''    if (s < 0 || s >= {PKG}.SkillDefs.N) continue;
    sum += (s == {PKG}.SkillDefs.FARMING && {PKG}.Farm3.AVG) ? {PKG}.Farm3.avgOf(d) : {PKG}.SkillDefs.levelOf(s, d[s]);   // 0.4.37
''')
rep('''  for (int i = 0; i < sl.length; i++) if (sl[i] == skill) return true;
''', '''  for (int i = 0; i < sl.length; i++) if (sl[i] == skill || ({PKG}.Farm3.AVG && sl[i] == {PKG}.SkillDefs.FARMING && {PKG}.Farm3.isFarm(skill))) return true;   // 0.4.37
''')
rep('''    int[] sc = sums(u, {PKG}.SkillStore.data(u));
    int after = level(sc);
    int before = sc[1] <= 0 ? 0 : (sc[0] - (int) (newLv - oldLv)) / sc[1];
''', '''    long[] ld = {PKG}.SkillStore.data(u);
    int[] sc = sums(u, ld);
    int after = level(sc);
    int dl = ({PKG}.Farm3.AVG && {PKG}.Farm3.isFarm(skill)) ? {PKG}.Farm3.avgDelta(ld, skill, (int) oldLv, (int) newLv) : (int) (newLv - oldLv);   // 0.4.37
    int before = sc[1] <= 0 ? 0 : (sc[0] - dl) / sc[1];
''')
rep('''    sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillDefs.levelOf(s, d[s]));
''', '''    if (s == {PKG}.SkillDefs.FARMING && {PKG}.Farm3.AVG) sb.append("Farming (avg of 3) ").append({PKG}.Farm3.avgOf(d));   // 0.4.37
    else sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillDefs.levelOf(s, d[s]));
''')
rep('''      || s == {PKG}.SkillDefs.ALCHEMY || s == {PKG}.SkillDefs.SMITHING || s == {PKG}.SkillDefs.COOKING || s == {PKG}.SkillDefs.EXPLORATION;
}}""", ovc))''', '''      || s == {PKG}.SkillDefs.ALCHEMY || s == {PKG}.SkillDefs.SMITHING || s == {PKG}.SkillDefs.COOKING || s == {PKG}.SkillDefs.EXPLORATION
      || s == {PKG}.SkillDefs.FISHING;   // 0.4.37: an admin may add Fishing (Ranching / Orchard count through Farming's average)
}}""", ovc))''')

# ---------------------------------------------------------------- (5) rebirth: a rebirth staged by 0.4.36 (no x.<new slot>) leaves those three as they are
rep('''    if (v == null) return "err:the staged file has no x." + @PKG@.SkillDefs.NAMES[s];
''', '''    if (v == null && s >= @PKG@.SkillDefs.FISHING) continue;   // 0.4.37: staged by 0.4.36 (no Fishing / Ranching / Orchard yet) - left as they are
    if (v == null) return "err:the staged file has no x." + @PKG@.SkillDefs.NAMES[s];
''')

# ---------------------------------------------------------------- StatsPage + command texts
rep('''  int row = {PKG}.SkillDefs.perkRow(s);
  if (row < 0) return out;
''', '''  if (s == {PKG}.SkillDefs.FISHING || s == {PKG}.SkillDefs.RANCHING || s == {PKG}.SkillDefs.ORCHARD) {{   // 0.4.37: no perks yet
    if (next) {{
      if ({PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillStore.rbCoins({PKG}.SkillCfg.COINS_PER_LEVEL * (long) (lv + 1), {PKG}.SkillStore.rbN({PKG}.SkillStore.pkey(u)))) + " coins when you reach level " + (lv + 1));
      return out;
    }}
    if (s == {PKG}.SkillDefs.RANCHING && !{PKG}.Ranch.ON) out.add("Ranching XP from pickups is turned off on this server");
    if (s != {PKG}.SkillDefs.FISHING) {{
      out.add("Farming level (average of Farming - Ranching - Orchard) " + {PKG}.Farm3.avgOf({PKG}.SkillStore.data(u)));
      if ({PKG}.GatherPace.on({PKG}.SkillDefs.FARMING)) {{ String gp = {PKG}.GatherPace.statsLine({PKG}.SkillDefs.FARMING, lv); if (gp != null) out.add(gp); }}   // fix round: Farming's pace
      out.add("Shares the Farming tree - its Wisdom raises this XP too");
    }} else out.add("No boosts yet - the Fishing tree comes in a later update");
    return out;
  }}
  int row = {PKG}.SkillDefs.perkRow(s);
  if (row < 0) return out;
''')
rep('''      if (!next) {{
        String dj = {PKG}.Acro.djLine(u);
        if (dj != null) out.add(dj);
      }}
''', '''      if (!next) {{
        String dj = {PKG}.Acro.djLine(u);
        if (dj != null) out.add(dj);
      }}
''')
# fix round 2: the Acrobatics perfect-dodge line and the Farming page's "Farming level (average ...)" line come LAST and only while the list
# has room (ST_LINES) - they never push a 0.4.36 line (the skill-tree line, a hook line) off the page
rep('''  if (!next && out.isEmpty()) out.add(lv <= 0 ? "Nothing yet - level up to unlock boosts" : "This skill gives no boosts on this server");
  return out;
''', '''  if (!next && out.isEmpty()) out.add(lv <= 0 ? "Nothing yet - level up to unlock boosts" : "This skill gives no boosts on this server");
  if (!next && out.size() < {ST_LINES}) {{   // 0.4.37 fix round 2: lowest priority, only while the list has room
    if (s == {PKG}.SkillDefs.ACROBATICS && {PKG}.AcroCfg.ENABLED && {PKG}.PDodge.ON) out.add("Perfect dodge - roll at most " + {PKG}.PDodge.WINDOW_MS + " ms before a hit: no damage" + ({PKG}.PDodge.MULT > 1.0 && {PKG}.PDodge.COUNTER_MS > 0L ? " and x" + {PKG}.DivCfg.num({PKG}.PDodge.MULT) + " on your next hit" : ""));
    else if (s == {PKG}.SkillDefs.FARMING) out.add("Farming level (average of Farming - Ranching - Orchard) " + {PKG}.Farm3.avgOf({PKG}.SkillStore.data(u)) + ({PKG}.Farm3.AVG ? " - counts in your Overall Level" : ""));
  }}
  return out;
''')
rep('''Math.round({PKG}.AcroCfg.ROLL * 100.0) + "%" : "");''',
    '''Math.round({PKG}.AcroCfg.ROLL * 100.0) + "%" : "") + ({PKG}.PDodge.ON ? " - roll right before a hit for a perfect dodge" : "");   // 0.4.37''')
rep('''  if (s == {PKG}.SkillDefs.COMBAT) return "Your combat skill is your class skill''',
    '''  if (s == {PKG}.SkillDefs.FISHING) return "Earn XP by catching fish with a SkyyFishing rod - bigger and rarer fish pay more";   // 0.4.37
  if (s == {PKG}.SkillDefs.RANCHING) return "Earn XP by picking up animal products - eggs - wool - feathers - meat and hides (items a player dropped pay nothing)";
  if (s == {PKG}.SkillDefs.ORCHARD) return "Earn XP by harvesting fruit - apples and berry bushes - when they are ripe (break them or press F)";
  if (s == {PKG}.SkillDefs.COMBAT) return "Your combat skill is your class skill''')
rep('''mining | foraging | farming | alchemy''', '''mining | foraging | farming | fishing | ranching | orchard | alchemy''', count=3)
rep('''Use mining, foraging, farming, alchemy,''', '''Use mining, foraging, farming, fishing, ranching, orchard, alchemy,''')
rep('''use Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking or Exploration''',
    '''use Mining, Foraging, Farming, Fishing, Ranching, Orchard, Acrobatics, Alchemy, Smithing, Cooking or Exploration''')

# ---------------------------------------------------------------- Server Setup rows (appended at the end: no other row moves) + the bridge row's help
rep('''     "Skills skill:fn:addxp may pay (Collections rewards, Cooking). Exploration is always allowed.", "reload;check=SkillKit.checkSkills"),''',
    '''     "Skills skill:fn:addxp may pay. Exploration, Fishing, Ranching and Orchard are always allowed.", "reload;check=SkillKit.checkSkills"),''')
rep('''     "Smithing XP per item for every other Furnace output (0 = none).", "reload"),
]
''', '''     "Smithing XP per item for every other Furnace output (0 = none).", "reload"),
    # 0.4.37 (Skyy 2026-10-11 "Add perfect-dodge to ours"; Gathering-Shards-Spec 5.3 phase 2): perfect dodge, Ranching, Orchard, the Farming average
    ("acro.perfectDodge", "Perfect dodge", "acrobatics", "bool", PD_ON_DEF, "", "", "", "", "live",
     "A roll right before a hit: no damage, Acrobatics XP (monsters' hits) and a stronger next hit.", "reload"),
    ("acro.perfectDodge.windowMs", "Perfect dodge window", "acrobatics", "int", PD_WIN_DEF, "0", "250", "", "ms", "live",
     "The hit must land at most this long after the roll starts (the server runs 30 ticks a second).", "reload"),
    ("acro.perfectDodge.counterMs", "Counter-hit time", "acrobatics", "int", PD_CTR_DEF, "0", "10000", "", "ms", "live",
     "After a perfect dodge your next hit within this time deals more damage (0 = no counter-hit).", "reload"),
    ("acro.perfectDodge.counterMultiplier", "Counter-hit damage", "acrobatics", "dec", PD_MULT_DEF, "1", "5", "", "x", "live",
     "The counter-hit's damage times this (1 = no bonus).", "reload"),
    ("acro.perfectDodge.xp", "Perfect dodge Acrobatics XP", "acrobatics", "int", PD_XP_DEF, "0", "100000", "", "", "live",
     "Acrobatics XP for each perfect dodge of a monster's hit (once per roll).", "reload"),
    ("acro.perfectDodge.maxXpPerMinute", "Perfect dodge XP per minute", "acrobatics", "int", PD_PM_DEF, "0", "1000000000", "", "", "live",
     "At most this much perfect-dodge Acrobatics XP per player per minute (0 = no cap).", "reload"),
    ("ranching.pickupXp", "Ranching XP from pickups", "gathering", "bool", "true", "", "", "", "", "live",
     "Animal products you pick up pay Ranching XP. Items a player dropped pay nothing again.", "reload"),
    ("ranching.items", "Ranching XP per item", "gathering", "text", RANCH_DEF, "", "2000", "", "", "live",
     "Item id and Ranching XP per item picked up, like Food_Egg:3, comma separated.", "reload"),
    ("ranching.maxXpPerMinute", "Ranching XP per player per minute", "gathering", "int", RANCH_PM_DEF, "0", "1000000000", "", "", "live",
     "At most this much Ranching XP from pickups per player per minute (0 = no cap).", "reload"),
    ("orchard.ids", "Orchard blocks (Farming XP to Orchard)", "gathering", "text", ORCH_DEF, "", "2000", "", "", "live",
     "Block id starts whose Farming XP goes to Orchard instead (fruit), comma separated.", "reload"),
    ("overall.farmingAverage", "Farming counts as the average", "overall", "bool", "false", "", "", "", "", "live",
     "On: the Overall Level counts Farming as the average of Farming, Ranching and Orchard.", "reload"),
]
''')
rep('''assert len(CFG_ROWS) == 230, ("0.4.36: + rebirth.coinFactor;''', '''assert len(CFG_ROWS) == 241, ("0.4.37: + 11 rows (perfect dodge 6, ranching 3, orchard.ids, overall.farmingAverage); 0.4.36: + rebirth.coinFactor;''')
rep('''print("config rows: %d (%d tables), %d not in the default file (zero perk stats, adv)"''',
    '''for _k37 in G37_KEYS:   # 0.4.37: every new key a row once, row default = the default file (= the code default)
    _r37 = [_r for _r in CFG_ROWS if _r[0] == _k37]
    assert len(_r37) == 1 and _dp.get(_k37) is not None and ("\\n" + _k37 + "=" + _dp[_k37] + "\\n") in ("\\n" + G37_DEFAULTS), _k37
assert [_r[0] for _r in CFG_ROWS][-11:] == G37_KEYS
print("config rows: %d (%d tables), %d not in the default file (zero perk stats, adv)"''')

# ---------------------------------------------------------------- the page colour list: the three new skill colours (lint + the page check)
rep('''UI_PAGE_COLORS = _B5C + CLASS_ROWS + EXTRA_ROWS   # the 16 skill / class colours''',
    '''UI_PAGE_COLORS = _B5C + CLASS_ROWS + EXTRA_ROWS + GATHER37_ROWS   # 0.4.37: + Fishing / Ranching / Orchard; the 19 skill / class colours''')
rep('''assert sorted(_B5C + [_x[3] for _x in CLASS_ROWS + EXTRA_ROWS]) == sorted(SLOT_COLORS), "UI_PAGE_COLORS != SkillDefs.COLORS"''',
    '''assert sorted(_B5C + [_x[3] for _x in CLASS_ROWS + EXTRA_ROWS + GATHER37_ROWS]) == sorted(SLOT_COLORS), "UI_PAGE_COLORS != SkillDefs.COLORS"''')

rep(r'''assert DEFAULTS.endswith("\n" + SKL_DEFAULTS + "\n" + KXP_DEFAULTS + "\n" + P25_DEFAULTS)   # 0.4.17: the KXP block follows the 0.4.16 block; 0.4.25: + P25''',
    r'''assert DEFAULTS.endswith("\n" + SKL_DEFAULTS + "\n" + KXP_DEFAULTS + "\n" + P25_DEFAULTS + "\n" + G37_DEFAULTS)   # 0.4.17: the KXP block follows the 0.4.16 block; 0.4.25: + P25; 0.4.37: + G37''')

# ---------------------------------------------------------------- plugin: systems, setting, ready line, manifest, class list
rep('''  {PKG}.MoveSync.checkProto({PKG}.Acro.MOD);
''', '''  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.PDodgeSys(true));   // 0.4.37: perfect dodge, BEFORE the roll i-frames' FilterUnkillable
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not order PDodgeSys before FilterUnkillable (" + t + ") - unordered fallback: perfect dodges may not be seen inside the roll i-frames");
    try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PDodgeSysU()); }} catch (Throwable t2) {{ {PKG}.SkillCfg.warn("could not register PDodgeSysU - no perfect dodge this start: " + t2); }}
  }}
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PCounterSys()); }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not register PCounterSys - no counter-hit this start: " + t); }}
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.RanchPickSys()); }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not register RanchPickSys - no Ranching XP from pickups this start: " + t); }}
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.RanchDropSys()); }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not register RanchDropSys - dropped items are not remembered this start: " + t); }}
  {PKG}.MoveSync.checkProto({PKG}.Acro.MOD);
''')
rep('''+ "; Farming one or two tiers above your hoe / sickle pays x" + ''',
    '''+ "; perfect dodge " + {PKG}.PDodge.text() + "; Fishing (skill:fn:addxp from SkyyFishing), Ranching (" + {PKG}.Ranch.text() + "), Orchard (" + {PKG}.Farm3.text() + "), bridge skill:farmavg:<uuid>" + "; Farming one or two tiers above your hoe / sickle pays x" + ''')
rep('''  {PKG}.SkillStore.regSetting("skills.overallUp",''',
    '''  {PKG}.SkillStore.regSetting("skills.perfectDodge", "Perfect dodge line", "combat", true, "Perfect dodge! when a roll right before a hit blocks it - your next hit hits harder");   // 0.4.37
  {PKG}.SkillStore.regSetting("skills.overallUp",''')
rep('''Per profile with SkyyProfiles (optional). Zero dependencies.", PKG + ".SkyySkillsPlugin")''',
    '''Per profile with SkyyProfiles (optional). Fishing (catches from SkyyFishing), Ranching (animal products you pick up - eggs, wool, feathers, meat, hides; items a player dropped pay nothing again) and Orchard (apples and berry bushes) skills; the Farming average of the three on the bridge (skill:farmavg:<uuid>, optional for the Overall Level). Perfect dodge: roll right before a monster's or player's hit for no damage, Acrobatics XP and a stronger next hit (Server Setup). Zero dependencies.", PKG + ".SkyySkillsPlugin")''')
rep('''          rbf, pset, sio, polm, mrt, scap, ftr, srun, srb):   # 0.4.36: + SkillRb;''',
    '''          rbf, pset, sio, polm, mrt, scap, ftr, srun, srb,
          pdg, pds, pdsu, pcs, rch, rps, rds, rtk, fm3):   # 0.4.37: + PDodge, PDodgeSys, PDodgeSysU, PCounterSys, Ranch, RanchPickSys, RanchDropSys, RanchTask, Farm3; 0.4.36: + SkillRb;''')

# ---------------------------------------------------------------- checks
assert s.index("public static int route(int slot, String id)") < s.index("public BreakTask(")
assert s.index("public static int avgOf(long[] d)") < s.index("public static int[] sums(java.util.UUID u, long[] d)")
assert s.index("public static void read(java.util.Properties p) {\n  ON = @PKG@.SkillCfg.bool(p, \"acro.perfectDodge\"") < s.index("{PKG}.PDodge.read(p);")
assert s.index("def event_system(") < s.index('event_system(rds, "RanchDropSys"')
assert s.index("public static double[] state(java.util.UUID u)") < s.index("public static long perfect(@PR@ pr")
assert s.index("public static long applyAt(") < s.index("public static void gain4(") and s.index("public static int paceSlot(int s)") < s.index("public static void gain4(")
assert s.index("public static long applyAt(") < s.index("public RanchTask(")
assert s.index("public static void gain4(") < s.index("public RanchTask(")
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.36 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.36,", len(_gone), "0.4.36 lines replaced;", len(OLDS), "anchors")
