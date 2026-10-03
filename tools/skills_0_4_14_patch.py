"""Derive SkyySkills/build_skyyskills_0.4.14.py from the LIVE generated SkyySkills/build_skyyskills_0.4.13.py (= the tools/deploy_set.py SET
pin; 0.4.13 came from 0.4.12 by tools/skills_0_4_13_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_13_patch.py: rep(old, new) with asserted single anchors, newline-agnostic;
0.4.13 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_14_patch.py   then   python SkyySkills/build_skyyskills_0.4.14.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.14.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0414/, deleted afterwards)

0.4.14 = SKYY'S FOUR LOCKS OF 2026-10-02 (OPEN-QUESTIONS.md, Q&A with Skyy 2026-10-02) + two small fixes:

(1) KILL XP BY MOB LEVEL ("level bonus + gap rule max +250%"). KillSys now calls MobXp.kill: kill XP = round(max health x combat.perHealth)
    kept between combat.min and combat.max (or the combat.role entry), x the class skill XP multiplier (as before) x (1 + combat.levelBonus
    x (L - 1)) x gap(L, S), L = the mob's level from SkyyMobs (bridge mob:fn:level, Object[]{world name, the NPC's UUIDComponent uuid};
    missing bridge / no level / -1 = both factors 1 = EXACTLY the 0.4.13 path through SkillCfg.classXp), S = the killer's class skill
    level before the kill. gap: d = L - S; d > combat.gap.free -> 1 + combat.gap.above x (d - free), at most combat.gap.max; d < -free ->
    1 - combat.gap.below x (-d - free), at least combat.gap.min; else 1. One chance rounding at the end (MobXp.pay = classXp's rule with
    the factor: a product within 1e-9 of a whole number counts as that number). The party share uses EACH member's own class skill:
    PartyXp.share2 / one2 pay amount(pay(killer slot, raw kill XP, levelFactor x gap(L, member's class skill)), fraction) - with no
    level the 0.4.13 share of the killer's cx exactly (share / one keep their old signatures and delegate). Skyy's example: a Lv 33
    Skeleton_Scout (178 HP) at Divinity 11 = 36 x 3 x 2.6 x 1.85 = 519.48 (519 or 520, mean 519.48; 0.4.13 paid 108). Rows (Server
    Setup): Parts "Kill XP by mob level" (combat.levelXp.enabled) + Combat combat.levelBonus 0.05 / combat.gap.free 5 / .above 0.05 /
    .max 3.5 / .below 0.05 / .min 0.1.
(2) ROLL LANDINGS (+50% Acrobatics XP). PROVEN from HytaleServer.jar (bytecode asserted by the build): DamageSystems$FallDamagePlayers.tick
    (gather damage group, DEPENDENCIES = BEFORE PlayerSystems$ProcessPlayerInput) walks PlayerInput.getMovementUpdateQueue(): a
    SetClientVelocity sets speed = |velocity.y|, the first SetMovementStates with onGround while LivingEntity.getCurrentFallDistance() > 0
    is the landing: speed > MovementConfig.MinFallSpeedToEngageRoll (vanilla 21) and not inFluid -> damage = floor(maxHealth / 100 x
    ((0.58f x (speed - min))^2 + 10)); IF that update's MovementStates.rolling (the client sets it when you crouch as you land): speed <=
    MaxFallSpeedRollFullMitigation (25) -> 0, else speed <= MaxFallSpeedToEngageRoll (31) -> x (1 - FallDamagePartialMitigationPercent
    (33) / 100); then Damage(FALL) unless 0, and the fall distance is reset. So a full roll makes NO damage event and 0.4.13 paid it
    nothing (a partial roll paid the reduced damage). NEW RollSys (EntityTickingSystem, ONE registerSystem, dependency BEFORE
    FallDamagePlayers, query Player + PlayerRef + PlayerInput + EntityStatMap, not parallel) reads the same queue read-only on the world
    thread before the engine consumes it and replays exactly that rule (RollSys.damage, compared with the REAL FallDamagePlayers in the
    harness); a landing whose roll ENGAGED (rolling and speed <= MaxFallSpeedToEngageRoll) notes the UNREDUCED damage normalised to 100
    max health (Acro.noteRoll, STATE 288-290). Acro.falls pays it 400 ms later like a hurt landing (alive, not in water, not creative):
    that x acro.fallDamageXp x (1 + acro.rollBonus), capped by acro.fallXpMax, then acro.fallMaxXpPerMinute (the existing caps). The
    damage note of the same landing (a partial roll still hurts) is skipped (noteFall: a roll note younger than 1 s). Non-rolled landings
    are untouched (AcroFallSeenSys as before). acro.rollBonus 0 = off = the 0.4.13 rule. Row Acrobatics "Extra XP for a rolled landing".
    Fix round F2: only in a world with fall damage on (RollSys.fallDamageOn = World.getWorldConfig().isFallDamageEnabled(), the switch the
    engine's FallDamagePlayers.tick(F, I, Store) tests before it looks at any landing - bytecode asserted).
(3) GATHERING PACE ("Bigger boost for all 3"): GatherPace.apply = earned XP x mult(level), mult = gather.boost.early (3) up to
    gather.boost.earlyUntil (10), a straight line to gather.boost.late (1.5) at gather.boost.lateFrom (20), late after (chance rounding,
    1e-9 rule) for the skills of gather.boost.skills (Mining, Foraging, Farming; the check hook refuses others). Applied in SkillXp.gain4's
    bonus path BEFORE the skill-tree Wisdom bonus (blocks, F-harvests, sickle swings) and in FellCredit.one (felled logs); grants from
    other mods (BridgeTask, Collections rewards) and the admin /skills xp stay exact, like Wisdom. Stats page: "Gathering XP x3 up to
    level 10, then easing to x1.5 by level 20" under "Boosts right now". The new keys reach an existing xp.properties through ONE
    appended block (SkillCfg.ensure14: only the key lines the file lacks, the file's own line ending; hand values are never rewritten).
(4) SICKLE SWINGS (research/Tool-Levels-Spec.md question 3, default yes): a sickle swing harvest (Sickle_Swing_*_Selector HitBlock ->
    HarvestCrop -> FarmingUtil.harvest0 -> giveDrops -> ItemUtils.interactivelyPickupItem, bytecode asserted) fires no break event, only
    InteractivelyPickupItemEvent per drop stack (the ItemStack only). NEW SickleSys (EntityEventSystem on it) skips: an F-pickup of a
    loose block (performPickupByInteraction builds BreakBlockEvent(NULL item) first - BreakSys records that context per player: same
    thread, < 250 ms, cleared by its BreakTask), an F-harvest window (HarvestSys records UseBlockEvent$Post on a ripe harvestable block -
    2 s, the SkyyCollections rule; HarvestTask pays those), creative, and anything not held in a sickle (farming.sickle.items, default
    Tool_Sickle_). The stacks of one tick go to SickleTask (world thread, after every other system: a cancelled pickup - SkyyIslands -
    pays nothing). ONE AWARD PER CROP: Sickle.keys() maps each crop's FIRST harvest drop (its produce: Plant_Crop_Wheat_Item,
    Plant_Fruit_Berries_Red ...) to the crop's Farming rule (the StageFinal BlockTypes - fix round F1 - of the live asset map with a Harvest
    drop whose block rule pays Farming XP); a produce stack starts a crop, the stacks after it that the crop can drop (essence, seeds) belong to it -
    anything else the same swing harvested (sap, a flower) is left out; a produce the crop can drop twice in one harvest (berry bushes:
    3% a second berry) merges with a directly preceding stack of the same produce. Each crop pays its rule XP once (SkillXp.gain: pace
    + Wisdom, chat, level ups) and rolls the Farming double drop once (Perks.chanceU / matches / doubled: a copy of that crop's own
    stacks; a failing double drop is logged once and never stops the XP of the next crop). Rows Gathering "Sickle swings pay Farming
    XP" (farming.sickle.enabled) + "Sickle item ids".
(5) The stale xp.properties comment: MREG_L's "Never above max Mana, never while charging, ..." line is fixed in the default text and,
    once, in an existing file (DocMig, before SkillCfg.load: only that EXACT comment line; the "(SkyySkills 0.4.12)" block header is kept;
    a values check (Properties equal), a verified config-history copy first, the kit's atomicWrite, the file's bytes / line endings kept;
    the new line is its own marker - no value changes, so there is nothing to Undo; History restores the old file).
(6) /skills stats: the summed skill:bonus line "Skill tree: ..." is now "Bonuses (trees + tools): ..." (SkyyGear 0.2.2 posts the held
    tool as source "gear"); the Acrobatics tree line keeps "Skill tree:" (its parts are tree nodes only).
NOT in this build: the SkyyTrees 0.3 reader flags (a later SkyySkills). Sickle swings do not call skill:on:gather (the listeners need the
crop block and its position, which the pickup event does not carry).

FIX ROUND (the numbers + exploits reviews of 2026-10-03):
 F1 (HIGH, both reviews) sickle swings paid ANY block with a Harvest drop whose rule pays Farming XP. FarmingUtil.harvest0 has no ripeness
    or placed check (a block without growth stages: giveDrops + setBlock EMPTY, bytecode 82-205), and the stateless Health / Mana / Stamina
    plants and cactus flowers hand back their own item (Assets.zip Harvest drop lists), so place -> swing -> place paid Farming XP forever
    and the double drop copied the plant (the break path never pays a placed one: ignorePlaced, rule[2] = 1). A pickup carries no position,
    so Sickle.addCrop now takes ONLY the StageFinal state of a crop with growth states - what HarvestSys pays for an F-harvest and what
    classifyBreak never place-checks: 16 produce keys (14 crops + apples + berries). Stateless plants, boomshrooms, burnt wheat and wild
    grass pay through breaking only, with ignorePlaced on or off (off: the break path pays them but never doubles them - no sickle path).
 F2 (MEDIUM, both reviews) RollSys paid rolls in a world with fall damage off, where the engine's FallDamagePlayers.tick(F, I, Store)
    returns before any landing (bytecode 12-23): RollSys.fallDamageOn(store) asks the same WorldConfig switch (0.4.13 paid nothing there).
 F3 (LOW) with a mob level each party member's share is worked out with THEIR class skill level: PartyXp.howText says so while mob levels
    are on, the party.combatShare.fraction row help and the 0.4.14 block's comment too (the 0.4.2 party comment stays: PartyCfg untouched).
 F4 (LOW) gather.boost.early / late accepted 0 (a skill that can never earn XP): the rows and GatherPace.read keep them at 0.1 or more.
 NOT changed: a clamp of the client's landing speed by the fall distance (the client's fall physics are not in the server jar -
    MovementConfig VariableJumpFallForce 35, air drag - and this tick's queued moves are not in the fall distance yet, so it would cut
    honest rolls; the engine trusts the same speed for fall damage; acro.fallMaxXpPerMinute stays the bound, as for 0.4.13's hurt
    landings). The party share of a low member (Skyy's lock: each member's own class skill) is Skyy's design call, flagged, not changed.
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.13.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.14.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.13"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
# the source must be the generated 0.4.13 of the edited lineage
assert 'VERSION = "0.4.13"' in s and "derived from the generated 0.4.12 by tools/skills_0_4_13_patch.py" in s, "not the live generated 0.4.13"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
for _x in ('".MobXp"', '".RollSys"', '".GatherPace"', '".Sickle"', '".SickleSys"', '".SickleTask"', '".DocMig"', "MobXp.", "GatherPace.",
           "Sickle.", "combat.levelXp", "acro.rollBonus", "gather.boost", "farming.sickle", "J14(", "Bonuses (trees + tools)", "noteRoll"):
    assert _x not in s, "0.4.13 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
OLDS = []   # every 0.4.13 text a rep() replaced (the whole-diff check below allows exactly their lines to change)


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])   # the WHOLE lines the anchor touches
    s = s.replace(old, new)


def after(anchor, add):
    """insert add right after the (single) anchor"""
    rep(anchor, anchor + add)


def before(anchor, add):
    """insert add right before the (single) anchor"""
    rep(anchor, add + anchor)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical (each still occurs exactly once afterwards)
KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= ManaRegen (0.4.12)", "# AcroSys: EntityTickingSystem on Player entities"),
        block("# ================= SkillDefs: names, icons, level table", "# ================= SkillCfg: xp.properties"),
        block("# ================= Xbow part 1 (0.4.5)", "# ================= ClassCurve (0.4.12)"),
        block("# ================= ClassCurve (0.4.12)", "# ================= SkillXp: award + level-up (world thread)"),
        block("# ================= 0.4.2 FELLED TREES", "# FellCredit (spec 2.6)"),
        block("# ================= skill:fn:addxp (0.4)", "# ================= /skills page (inline"),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ================= 0.4.8 ManaCost / ManaMig / ManaGuard", "# ---- HealMig (0.4.11 point 5)"),
        block("# ================= SkillKit (0.4.3)", "# ================= commands ================="),
        block("# ================= commands =================", "# ================= 1s ticker"),
        block("# ---- 0.4.5 Xbow part 2", "# ================= ManaRegen (0.4.12)"),
        block("# ================= CombatDmgSys (0.3)", "# ================= PlacedStore"),
        block("# ================= PlacedStore", "# ================= 0.4.2 FELLED TREES"),
        block("# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4)", "# ================= trees bridge Functions"),
        block("# ================= SKILLS PAGES LOOK (0.4.7)", "# ================= StatsPage (0.3)")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.13 - build script (derived from the generated 0.4.12 by tools/skills_0_4_13_patch.py - edit the patch, not this file;
0.4.12 was derived''', '''"""SkyySkills 0.4.14 - build script (derived from the generated 0.4.13 by tools/skills_0_4_14_patch.py - edit the patch, not this file;
0.4.13 was derived from the generated 0.4.12 by tools/skills_0_4_13_patch.py; 0.4.12 was derived''')
HEAD_0414 = '''0.4.14: SKYY'S LOCKS OF 2026-10-02 (OPEN-QUESTIONS Q&A; full notes in tools/skills_0_4_14_patch.py).
  KILL XP BY MOB LEVEL: kill XP (max health x combat.perHealth, kept between combat.min / combat.max, x the class skill XP multiplier) x
     (1 + combat.levelBonus x (mob level - 1)) x the level gap against your class skill (more than combat.gap.free levels above: +gap.above
     a level, at most x gap.max = +250%; below: -gap.below a level, at least x gap.min). Mob level = SkyyMobs mob:fn:level; no level = the
     0.4.13 XP exactly. Party members use their own class skill for the gap. Lv 33 Skeleton_Scout (178 HP) at Divinity 11 = ~520 XP.
  ROLL LANDINGS: RollSys (before the engine's FallDamagePlayers, reading the same PlayerInput queue) notes a landing whose roll engaged
     (MovementStates.rolling, speed between MinFallSpeedToEngageRoll and MaxFallSpeedToEngageRoll); it pays the UNREDUCED fall XP x (1 +
     acro.rollBonus) 0.4 s later (alive, not in water), inside acro.fallXpMax / acro.fallMaxXpPerMinute. A full roll paid 0 before.
     Only in a world with fall damage on (WorldConfig.isFallDamageEnabled - the engine skips every landing of the others).
  GATHERING PACE: earned Mining / Foraging / Farming XP x gather.boost.early (3) up to level gather.boost.earlyUntil (10), easing in a
     straight line to x gather.boost.late (1.5) at gather.boost.lateFrom (20), x1.5 after - before the tree Wisdom bonus; grants from
     other mods stay exact. Shown on the Stats page.
  SICKLE SWINGS: InteractivelyPickupItemEvent (SickleSys) with a sickle in hand, outside an F-harvest window and an F-pickup: one Farming
     award + one double-drop roll per RIPE crop - the StageFinal state of a crop with growth states, like an F-harvest (each crop's produce
     item starts it; a pickup has no position, so plants without growth states pay through breaking only). SickleTask pays on the world
     thread. No skill:on:gather for sickle swings (its listeners need the crop block and position).
  FIXES: the stale "never while charging" xp.properties comment (DocMig, once, History first); the Stats line "Bonuses (trees + tools)".
  FIX ROUND (reviews 2026-10-03): sickle swings pay StageFinal crops only (a placed stateless plant that hands back its own item looped XP
     and double drops); RollSys only where fall damage is on; the party texts (each member's own class skill level); gather.boost.early /
     late at least 0.1.
  New keys reach an existing xp.properties through one appended block (only the lines it lacks). CHECKED in a bare JVM
  (SkyySkills/test_skyyskills_0.4.14.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
rep('''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.13: THE COMBAT''', '''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
''' + HEAD_0414 + '''0.4.13: THE COMBAT''')
rep('VERSION = "0.4.13"\n', 'VERSION = "0.4.14"\n')

# ---------------------------------------------------------------------------------------------------------------- engine names + probes
after('CHG = "com.hypixel.hytale.server.core.modules.entity.condition.ChargingCondition"   # 0.4.13 fix: Mana keeps regenerating while charging\n',
      '''# 0.4.14 (tools/skills_0_4_14_patch.py): roll landings, kill XP by mob level, sickle swings
PIN  = "com.hypixel.hytale.server.core.modules.entity.player.PlayerInput"
PISM = "com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetMovementStates"
PISV = "com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetClientVelocity"
FDP  = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FallDamagePlayers"
SDEP = "com.hypixel.hytale.component.dependency.SystemDependency"
DORD = "com.hypixel.hytale.component.dependency.Order"
UUC  = "com.hypixel.hytale.server.core.entity.UUIDComponent"
IPE  = "com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent"
IDL  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemDropList"
IDR  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemDrop"
IDC  = "com.hypixel.hytale.server.core.asset.type.item.config.container.ItemDropContainer"
FUT  = "com.hypixel.hytale.builtin.adventure.farming.FarmingUtil"
WCFG = "com.hypixel.hytale.server.core.universe.world.WorldConfig"   # fix round F2: the per-world fall damage switch (World.getWorldConfig)
''')
PROBES_0414 = r'''# 0.4.14 (tools/skills_0_4_14_patch.py): the engine facts the four new features rest on - HytaleServer.jar bytecode, read 2026-10-03; any
# drift stops the build instead of a feature going quiet. Every engine member the new code calls must be public (the engine-access rule).
for c, m in ((PIN, "getComponentType"), (PIN, "getMovementUpdateQueue"), (PISM, "movementStates"), (PISV, "getVelocity"), (MVT, "rolling"),
             (MVT, "onGround"), (MVT, "inFluid"), (MCF, "getMinFallSpeedToEngageRoll"), (MCF, "getMaxFallSpeedRollFullMitigation"),
             (MCF, "getMaxFallSpeedToEngageRoll"), (MCF, "getFallDamagePartialMitigationPercent"), (MCF, "getAssetMap"), (PLA, "getCurrentFallDistance"),
             (SDEP, "getSystemClass"), (DORD, "BEFORE"), (UUC, "getComponentType"), (UUC, "getUuid"), (IPE, "getItemStack"), (IPE, "isCancelled"),
             (IDL, "getAssetMap"), (IDL, "getContainer"), (IDR, "getItemId"), (IDC, "getAllDrops"), (BTM, "getNextIndex"), (BTM, "getAsset"),
             (HDT, "getDropListId"), (HDT, "getItemId"), (BBE, "getItemInHand"), (INVC, "getItemInHand"), (QRY, "and"), (WLD, "getGameplayConfig"),
             (GPC, "getPlayerConfig"), (PCF, "getMovementConfigIndex"), (WLD, "getWorldConfig"), (WCFG, "isFallDamageEnabled")):
    B.probe(pool, c, m)
_JM14 = _jp.JClass("javassist.Modifier")
for c, m, d in ((PIN, "getMovementUpdateQueue", "()Ljava/util/List;"), (PIN, "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (PISM, "movementStates", "()L" + MVT.replace(".", "/") + ";"), (PISV, "getVelocity", "()L" + V3D.replace(".", "/") + ";"),
                (PLA, "getCurrentFallDistance", "()D"), (MCF, "getMinFallSpeedToEngageRoll", "()F"), (MCF, "getMaxFallSpeedRollFullMitigation", "()F"),
                (MCF, "getMaxFallSpeedToEngageRoll", "()F"), (MCF, "getFallDamagePartialMitigationPercent", "()F"),
                (UUC, "getUuid", "()Ljava/util/UUID;"), (UUC, "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (IPE, "getItemStack", "()L" + IS.replace(".", "/") + ";"), (IPE, "isCancelled", "()Z"),
                (IDL, "getContainer", "()L" + IDC.replace(".", "/") + ";"), (IDC, "getAllDrops", "(Ljava/util/List;)Ljava/util/List;"),
                (IDR, "getItemId", "()Ljava/lang/String;"), (BTM, "getNextIndex", "()I"), (BBE, "getItemInHand", "()L" + IS.replace(".", "/") + ";"),
                (INVC, "getItemInHand", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";)L" + IS.replace(".", "/") + ";"),
                (QRY, "and", "([L" + QRY.replace(".", "/") + ";)Lcom/hypixel/hytale/component/query/AndQuery;"),
                (WLD, "getWorldConfig", "()L" + WCFG.replace(".", "/") + ";"), (WCFG, "isFallDamageEnabled", "()Z")):
    try:
        _mm = pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
    assert _JM14.isPublic(_mm.getModifiers()) and _JM14.isPublic(pool.get(c).getModifiers()), "%s.%s is no longer public" % (c, m)
for c, f in ((MVT, "rolling"), (MVT, "onGround"), (MVT, "inFluid"), (DORD, "BEFORE")):
    assert _JM14.isPublic(pool.get(c).getField(f).getModifiers()), "%s.%s is no longer a public field" % (c, f)
assert _JM14.isPublic(pool.get(SDEP).getConstructor("(L" + DORD.replace(".", "/") + ";Ljava/lang/Class;)V").getModifiers()), "SystemDependency(Order, Class) is not public"
assert pool.get("com.hypixel.hytale.component.ComponentType").subtypeOf(pool.get(QRY)), "ComponentType is no longer a Query"
def _ci_lines(cls):
    """the instructions of the class initializer of cls"""
    _ip, _out = _jp.JClass("javassist.bytecode.InstructionPrinter"), []
    _ci = pool.get(cls).getClassInitializer()
    if _ci is None:
        return _out
    _it, _cp = _ci.getMethodInfo().getCodeAttribute().iterator(), _ci.getMethodInfo().getConstPool()
    while _it.hasNext():
        _out.append(str(_ip.instructionString(_it, _it.next(), _cp)))
    return _out
# (2) ROLL LANDINGS: FallDamagePlayers.tick = the queue walk RollSys replays (speed from SetClientVelocity, the first onGround landing while
# falling, min speed, not in fluid, floor(maxHealth / 100 x ((0.58f x (speed - min))^2 + 10)), the rolling mitigation, the fall distance reset)
_fdp = _bc_lines(FDP, "tick")
for _need in (PIN + ".getMovementUpdateQueue", PISV + ".getVelocity", PISM + ".movementStates", MVT + ".onGround", MVT + ".inFluid", MVT + ".rolling",
              PLA + ".getCurrentFallDistance", PLA + ".setCurrentFallDistance", MCF + ".getMinFallSpeedToEngageRoll",
              MCF + ".getMaxFallSpeedRollFullMitigation", MCF + ".getMaxFallSpeedToEngageRoll", MCF + ".getFallDamagePartialMitigationPercent",
              "double 0.5799999833106995", "double 2.0", "double 10.0", "double 100.0", "java.lang.Math.pow", "java.lang.Math.floor",
              "DamageSystems.executeDamage", "Velocity.getClientVelocity", "EntityStatValue.getMax"):
    assert any(_need in x for x in _fdp), "DamageSystems$FallDamagePlayers.tick no longer has %s - re-check RollSys (roll landings)" % _need
_fdc = _ci_lines(FDP)
assert (any(DORD + ".BEFORE" in x for x in _fdc) and any("PlayerSystems$ProcessPlayerInput" in x for x in _fdc)
        and any(SDEP + ".<init>" in x for x in _fdc) and any(PIN + ".getComponentType" in x for x in _fdc)), \
    "FallDamagePlayers no longer runs BEFORE ProcessPlayerInput on PlayerInput - RollSys could see a consumed queue"
assert any("getGatherDamageGroup" in x for x in _bc_lines(FDP, "getGroup")), "FallDamagePlayers left the gather damage group"
# fix round F2: the store-level FallDamagePlayers.tick(F, I, Store) = World.getWorldConfig().isFallDamageEnabled() first, return when it is off,
# else the per-entity ticks - a world with fall damage off processes NO landing; RollSys.fallDamageOn asks the same switch
_fds = [_mm for _mm in pool.get(FDP).getDeclaredMethods() if str(_mm.getName()) == "tick" and str(_mm.getSignature()) == "(FILcom/hypixel/hytale/component/Store;)V"]
assert len(_fds) == 1 and _fds[0].getMethodInfo().getCodeAttribute() is not None, "FallDamagePlayers no longer declares tick(float, int, Store)"
_fdsi, _fdsc, _fdsl = _fds[0].getMethodInfo().getCodeAttribute().iterator(), _fds[0].getMethodInfo().getConstPool(), []
while _fdsi.hasNext():
    _fdsl.append(str(_jp.JClass("javassist.bytecode.InstructionPrinter").instructionString(_fdsi, _fdsi.next(), _fdsc)))
_fdsw = [i for i, x in enumerate(_fdsl) if WCFG + ".isFallDamageEnabled" in x]
assert (len(_fdsw) == 1 and any(WLD + ".getWorldConfig" in x for x in _fdsl[:_fdsw[0]]) and _fdsl[_fdsw[0] + 1].split(":")[-1].strip().startswith("ifne")
        and _fdsl[_fdsw[0] + 2].split(":")[-1].strip() == "return" and any("EntityTickingSystem.tick" in x for x in _fdsl[_fdsw[0]:])), \
    "FallDamagePlayers.tick(float, int, Store) no longer returns at once in a world with fall damage off - re-check RollSys.fallDamageOn (roll landings)"
# (4) SICKLE SWINGS: the only paths that hand drops over through InteractivelyPickupItemEvent: ItemUtils.interactivelyPickupItem (new event,
# invoke on the player, isCancelled, getItemStack), FarmingUtil.giveDrops (HarvestCrop: F-harvest AND the sickle selector) and the F pickup of
# a loose block (BlockHarvestUtils.performPickupByInteraction: a BreakBlockEvent with a NULL item first, then the drops)
_iup = _bc_lines("com.hypixel.hytale.server.core.entity.ItemUtils", "interactivelyPickupItem")
assert (any(IPE + ".<init>" in x for x in _iup) and any(IPE + ".isCancelled" in x for x in _iup) and any(IPE + ".getItemStack" in x for x in _iup)
        and any("ComponentAccessor.invoke" in x for x in _iup)), "ItemUtils.interactivelyPickupItem changed - re-check SickleSys"
_gdr = _bc_lines(FUT, "giveDrops")
assert any("ItemUtils.interactivelyPickupItem" in x for x in _gdr) and any(BHU + ".getDrops" in x for x in _gdr), "FarmingUtil.giveDrops changed"
assert any(FUT + ".giveDrops" in x for x in _bc_lines(FUT, "harvest0")), "FarmingUtil.harvest0 no longer gives the drops"
assert any(FUT + ".harvest" in x for x in _bc_lines("com.hypixel.hytale.builtin.adventure.farming.interactions.HarvestCropInteraction", "interactWithBlock")), \
    "HarvestCropInteraction.interactWithBlock no longer calls FarmingUtil.harvest"
_ppi = _bc_lines(BHU, "performPickupByInteraction")
_bbi = [i for i, x in enumerate(_ppi) if BBE + ".<init>" in x]
assert len(_bbi) == 1 and any(x.strip() == "aconst_null" for x in _ppi[max(0, _bbi[0] - 3):_bbi[0]]) and \
    any("ItemUtils.interactivelyPickupItem" in x for x in _ppi[_bbi[0]:]), \
    "BlockHarvestUtils.performPickupByInteraction no longer fires BreakBlockEvent(null item) before its pickups - re-check the F-pickup context"
print("0.4.14 engine checks: FallDamagePlayers (BEFORE ProcessPlayerInput, rolling mitigation, 0.58 / 10 / 100, no landing in a world with fall "
      "damage off), InteractivelyPickupItemEvent from ItemUtils <- FarmingUtil.giveDrops <- harvest0 <- HarvestCropInteraction and the F pickup "
      "(BreakBlockEvent(null) first)")
'''
before("# 0.4.8 (Skyy 2026-09-30): every vanilla spell's Mana cost / SPELL_DIVISOR (the SPELL GEN block builds the item overrides)\n", PROBES_0414)

# ---------------------------------------------------------------------------------------------------------------- default xp.properties
rep('''MREG_L.append("# Never above max Mana, never while charging, nothing for a player without Mana (max Mana 0).")
''', '''# 0.4.14 (fix (5)): Mana keeps regenerating while charging since 0.4.13 - the old line is the text DocMig rewrites once in an existing file
MREG_DOC_OLD = "# Never above max Mana, never while charging, nothing for a player without Mana (max Mana 0)."
MREG_DOC_NEW = "# Never above max Mana, nothing for a player without Mana (max Mana 0). Charging no longer pauses it (SkyySkills 0.4.13+)."
MREG_L.append(MREG_DOC_NEW)
''')
N14_BLOCK = r'''# 0.4.14 (Skyy 2026-10-02 locks): kill XP by mob level, roll landings, the gathering pace, sickle swings - ONE block at the end of a fresh file;
# SkillCfg.ensure14 appends it to an existing file (only the key lines the file lacks, its own line ending). The code defaults (MobXp,
# AcroCfg.ROLL, GatherPace, Sickle) are the same numbers. No comment line may look like a "#key=value" template line.
N14_L = []
N14_L.append("# ---------- Kill XP by mob level, roll landings, gathering pace, sickle swings (SkyySkills 0.4.14) ----------")
N14_L.append("# Comments must stay on their own lines.")
N14_L.append("# KILL XP BY MOB LEVEL (Skyy 2026-10-02, needs SkyyMobs levels): kill XP (max health x combat.perHealth, kept between combat.min and")
N14_L.append("# combat.max, times the class skill XP multiplier) x (1 + combat.levelBonus x (mob level - 1)) x the level gap. A mob more than")
N14_L.append("# combat.gap.free levels ABOVE your class skill adds combat.gap.above per extra level (at most combat.gap.max times, 3.5 = +250 percent);")
N14_L.append("# more than combat.gap.free levels BELOW takes combat.gap.below per level away (at least combat.gap.min, 0.1 = 10 percent). A mob")
N14_L.append("# without a level (no SkyyMobs, an animal it does not level) pays as before. Party members get party.combatShare.fraction of what")
N14_L.append("# the kill pays THEM: the gap uses each member's own class skill level.")
N14_L.append("# A Lv 33 Skeleton Scout (178 HP) at Divinity 11 pays 36 x 3 x 2.6 x 1.85 = about 520 XP.")
N14_L.append("combat.levelXp.enabled=true")
N14_L.append("combat.levelBonus=0.05")
N14_L.append("combat.gap.free=5")
N14_L.append("combat.gap.above=0.05")
N14_L.append("combat.gap.max=3.5")
N14_L.append("combat.gap.below=0.05")
N14_L.append("combat.gap.min=0.1")
N14_L.append("# ROLL LANDINGS (Skyy 2026-10-02): crouch as you land and Hytale rolls - less or no fall damage. A rolled landing pays the")
N14_L.append("# Acrobatics XP the fall would have paid without the roll plus acro.rollBonus of it (0.5 = +50 percent; 0 = rolls pay as before).")
N14_L.append("# acro.fallXpMax and acro.fallMaxXpPerMinute still cap it.")
N14_L.append("acro.rollBonus=0.5")
N14_L.append("# GATHERING PACE (Skyy 2026-10-02): XP you earn in these skills (blocks, felled logs, F-harvests, sickle swings) times early up")
N14_L.append("# to level earlyUntil, easing in a straight line to times late at level lateFrom, times late after. Rewards other mods grant")
N14_L.append("# (SkyyCollections tiers) stay exact. The skill-tree Wisdom bonus comes on top.")
N14_L.append("gather.boost.skills=Mining,Foraging,Farming")
N14_L.append("gather.boost.early=3")
N14_L.append("gather.boost.earlyUntil=10")
N14_L.append("gather.boost.late=1.5")
N14_L.append("gather.boost.lateFrom=20")
N14_L.append("# SICKLE SWINGS (Skyy 2026-10-02): a ripe crop a sickle swing harvests pays its Farming XP and rolls the Farming double drop like a")
N14_L.append("# broken ripe crop, once per crop. Hytale only says which items you picked up, so the crop is found from its produce item. An F")
N14_L.append("# on a ripe crop (paid by the F-harvest) and an F pickup of a loose block are never paid twice. Items = id starts of sickles.")
N14_L.append("# A ripe crop is the final growth stage of a crop that grows (like an F-harvest); plants without growth stages (Health,")
N14_L.append("# Mana and Stamina plants, cactus flowers, boomshrooms) pay only when broken - a sickle swing cannot tell a placed one.")
N14_L.append("farming.sickle.enabled=true")
N14_L.append("farming.sickle.items=Tool_Sickle_")
L.append("")
L.extend(N14_L)
N14_DEFAULTS = "\n".join(N14_L) + "\n"
assert all(ord(ch) < 128 for ch in N14_DEFAULTS) and '"' not in N14_DEFAULTS and "\\" not in N14_DEFAULTS
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in N14_L), "a comment looks like a template line"
N14_KEYS = [_ln.split("=", 1)[0] for _ln in N14_L if not _ln.startswith("#")]
assert len(N14_KEYS) == len(set(N14_KEYS)) == 15, N14_KEYS
N14_LIT = json.dumps(N14_DEFAULTS)
assert MREG_DOC_OLD != MREG_DOC_NEW and MREG_DOC_NEW in MREG_L and MREG_DOC_OLD not in MREG_L and "charging" not in MREG_DOC_OLD.replace("never while charging", "")
# the sickle items and the selectors whose HitBlock harvests (Assets.zip, read in memory); vanilla's roll numbers for the log
must_prefix("Tool_Sickle_")
with zipfile.ZipFile(ASSETS) as _sz:
    _szn = _sz.namelist()
    for _sel in ("Sickle_Swing_Left_Selector.json", "Sickle_Swing_Right_Selector.json"):
        _sh = [n for n in _szn if n.startswith("Server/Item/Interactions/") and n.endswith("/" + _sel)]
        assert len(_sh) == 1, "Assets.zip: %d x %s" % (len(_sh), _sel)
        _sj = json.loads(_sz.read(_sh[0]).decode("utf-8-sig"))
        assert any(isinstance(_x, dict) and _x.get("Type") == "HarvestCrop" for _x in ((_sj.get("HitBlock") or {}).get("Interactions") or [])), \
            "%s: HitBlock no longer runs HarvestCrop - sickle swings would not harvest" % _sel
    _smc = [n for n in _szn if n.startswith("Server/Entity/MovementConfig/") and n.endswith("/Default.json")]
    _smd = json.loads(_sz.read(_smc[0]).decode("utf-8-sig")) if len(_smc) == 1 else {}
print("sickle swings (0.4.14): %d Tool_Sickle_ items, both swing selectors harvest; roll landings: vanilla MovementConfig Default roll from %s, "
      "no damage to %s, -%s%% to %s blocks a second" % (len([i for i in ITEM_IDS if i.startswith("Tool_Sickle_")]), _smd.get("MinFallSpeedToEngageRoll"),
                                                      _smd.get("MaxFallSpeedRollFullMitigation"), _smd.get("FallDamagePartialMitigationPercent"),
                                                      _smd.get("MaxFallSpeedToEngageRoll")))
import re as _re14
def J14(src_):
    """0.4.14: Java source with @NAME@ tokens = module constants (PKG, BTY, IS, ...) - single braces, no f-string brace doubling"""
    def _tok(m_):
        v_ = globals().get(m_.group(1))
        if not isinstance(v_, str):
            raise SystemExit("J14: unknown token @%s@" % m_.group(1))
        return v_
    return _re14.sub(r"@([A-Z][A-Z0-9_]*)@", _tok, src_)
'''
after("MREG_LIT = json.dumps(MREG_DEFAULTS)\n", N14_BLOCK)

# ---------------------------------------------------------------------------------------------------------------- the new classes
after('cmbf = pool.makeClass(PKG + ".CombatFn")\n', '''# 0.4.14: kill XP by mob level (MobXp), roll landings (RollSys, before the engine's FallDamagePlayers), the gathering pace (GatherPace),
# sickle swings (Sickle + SickleSys on InteractivelyPickupItemEvent + SickleTask on the world thread), the Mana comment fix (DocMig)
mxp  = pool.makeClass(PKG + ".MobXp")
rsy  = pool.makeClass(PKG + ".RollSys", pool.get(ETS))
gpc  = pool.makeClass(PKG + ".GatherPace")
skl  = pool.makeClass(PKG + ".Sickle")
sksy = pool.makeClass(PKG + ".SickleSys", pool.get(EES))
sktk = pool.makeClass(PKG + ".SickleTask")
dmig = pool.makeClass(PKG + ".DocMig")
''')

# ---------------------------------------------------------------------------------------------------------------- early: the config readers (before SkillCfg.load)
EARLY_CFG = r'''# ================= 0.4.14 config readers (before SkillCfg.load, which calls them): AcroCfg.ROLL, MobXp, GatherPace, Sickle =================
# acro.rollBonus (Skyy 2026-10-02: "if you crouch as you land you take less fall damage ... make that roll give extra acrobatic xp too")
acfg.addField(CtField.make("public static volatile double ROLL = 0.5;", acfg))
acfg.addMethod(CtNewMethod.make(J14(r"""
public static void readRoll(java.util.Properties p) {
  ROLL = clampD(@PKG@.SkillCfg.dbl(p, "acro.rollBonus", 0.5), 0.0, 10.0);
}"""), acfg))
acfg.addMethod(CtNewMethod.make(J14(r"""
public static String rollText() {
  if (!ENABLED) return "off (acro.enabled=false)";
  if (!(ROLL > 0.0)) return "off (rolls pay as before)";
  return "+" + @PKG@.DivCfg.num(ROLL * 100.0) + "% Acrobatics XP for a rolled landing";
}"""), acfg))
# MobXp (Skyy 2026-10-02 KILL XP = "level bonus + gap rule max +250%"): combat.levelXp.enabled / combat.levelBonus / combat.gap.*
for _d in ("public static volatile boolean ON = true;", "public static volatile double BONUS = 0.05;", "public static volatile int FREE = 5;",
           "public static volatile double ABOVE = 0.05;", "public static volatile double MAX = 3.5;", "public static volatile double BELOW = 0.05;",
           "public static volatile double MIN = 0.1;", "public static boolean FAILED_ONCE = false;"):
    mxp.addField(CtField.make(_d, mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "combat.levelXp.enabled", true);
  BONUS = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.levelBonus", 0.05), 0.0, 10.0);
  FREE = (int) @PKG@.AcroCfg.clampD((double) @PKG@.SkillCfg.lng(p, "combat.gap.free", 5L), 0.0, 100.0);
  ABOVE = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.above", 0.05), 0.0, 10.0);
  MAX = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.max", 3.5), 1.0, 100.0);
  BELOW = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.below", 0.05), 0.0, 10.0);
  MIN = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.min", 0.1), 0.0, 1.0);
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (!ON) return "off";
  return "on (+" + @PKG@.DivCfg.num(BONUS * 100.0) + "% a mob level; more than " + FREE + " levels above your class skill +" + @PKG@.DivCfg.num(ABOVE * 100.0) + "% a level up to x" + @PKG@.DivCfg.num(MAX) + ", below -" + @PKG@.DivCfg.num(BELOW * 100.0) + "% a level down to x" + @PKG@.DivCfg.num(MIN) + "; SkyyMobs levels)";
}"""), mxp))
# GatherPace (Skyy 2026-10-02 tool levels answer (4): "Bigger boost for all 3") - gather.boost.*; SLOTS indexed by storage slot
gpc.addField(CtField.make('public static final String DEFAULT_SKILLS = "Mining,Foraging,Farming";', gpc))
# fix round F4: early / late are never below this (0 = a skill that can never earn XP from gathering; the rows' min is the same)
gpc.addField(CtField.make("public static final double MIN_MULT = 0.1;", gpc))
for _d in ("public static volatile boolean[] SLOTS = new boolean[] { true, true, true };", 'public static volatile String TEXT = "Mining,Foraging,Farming";',
           "public static volatile double EARLY = 3.0;", "public static volatile int UNTIL = 10;", "public static volatile double LATE = 1.5;",
           "public static volatile int FROM = 20;"):
    gpc.addField(CtField.make(_d, gpc))
# a gathering skill name -> its slot (Mining / Foraging / Farming), -1 = blank, -2 = anything else
gpc.addMethod(CtNewMethod.make(J14(r"""
public static int slotOf(String t) {
  if (t == null) return -1;
  String x = t.trim();
  if (x.length() == 0) return -1;
  for (int s = 0; s <= @PKG@.SkillDefs.FARMING; s++) if (@PKG@.SkillDefs.NAMES[s].equalsIgnoreCase(x) || @PKG@.SkillDefs.LABELS[s].equalsIgnoreCase(x)) return s;
  return -2;
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  String v = p.getProperty("gather.boost.skills", DEFAULT_SKILLS);
  boolean[] on = new boolean[@PKG@.SkillDefs.N];
  StringBuilder sb = new StringBuilder();
  String[] ps = (v == null ? "" : v).split(",");
  for (int i = 0; i < ps.length; i++) {
    int s = slotOf(ps[i]);
    if (s == -1) continue;
    if (s < 0) { @PKG@.SkillCfg.warn("gather.boost.skills: '" + ps[i].trim() + "' is not Mining, Foraging or Farming - ignored"); continue; }
    if (on[s]) continue;
    on[s] = true;
    if (sb.length() > 0) sb.append(',');
    sb.append(@PKG@.SkillDefs.LABELS[s]);
  }
  SLOTS = on;
  TEXT = sb.toString();
  EARLY = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "gather.boost.early", 3.0), MIN_MULT, 100.0);
  UNTIL = (int) @PKG@.AcroCfg.clampD((double) @PKG@.SkillCfg.lng(p, "gather.boost.earlyUntil", 10L), 0.0, 100.0);
  LATE = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "gather.boost.late", 1.5), MIN_MULT, 100.0);
  FROM = (int) @PKG@.AcroCfg.clampD((double) @PKG@.SkillCfg.lng(p, "gather.boost.lateFrom", 20L), 0.0, 100.0);
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static boolean on(int slot) {
  boolean[] s = SLOTS;
  return slot >= 0 && slot < s.length && s[slot];
}"""), gpc))
# the multiplier at a level: EARLY through UNTIL, LATE from FROM, a straight line between
gpc.addMethod(CtNewMethod.make(J14(r"""
public static double mult(int lv) {
  if (lv <= UNTIL) return EARLY;
  if (lv >= FROM) return LATE;
  return EARLY + (LATE - EARLY) * (double) (lv - UNTIL) / (double) (FROM - UNTIL);
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (TEXT.length() == 0) return "off (no skill listed)";
  return "x" + @PKG@.DivCfg.num(EARLY) + " to level " + UNTIL + ", x" + @PKG@.DivCfg.num(LATE) + " from level " + FROM + " (" + TEXT + ")";
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static String checkSkills(String key, String v) {
  if (v == null) return null;
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) {
    if (slotOf(ps[i]) == -2) return "Only Mining, Foraging and Farming have a gathering pace (" + ps[i].trim() + " is not one).";
  }
  return null;
}"""), gpc))
# Sickle (research/Tool-Levels-Spec.md question 3): farming.sickle.*; the per-player contexts (BRK: an F pickup's BreakBlockEvent, USE: an
# F-harvest, PEND: this tick's pickups) are pruned by Acro.retainOnline; KEYS (produce item -> {Long xp, Boolean multi, String family}) is
# built on first use on a world thread and dropped by every load (the rules may have changed)
skl.addField(CtField.make('public static final String DEFAULT_ITEMS = "Tool_Sickle_";', skl))
for _d in ("public static volatile boolean ON = true;", 'public static volatile String[] ITEMS = new String[] { "Tool_Sickle_" };',
           'public static volatile String ITEMS_TEXT = "Tool_Sickle_";', "public static volatile java.util.HashMap KEYS = null;",
           "public static final java.util.concurrent.ConcurrentHashMap BRK = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap USE = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile boolean SEEN = false;", "public static boolean FAILED_ONCE = false;",
           "public static final long BREAK_NS = 250000000L;", "public static final long WINDOW_MS = 2000L;"):
    skl.addField(CtField.make(_d, skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static String[] parse(String v) {
  java.util.ArrayList l = new java.util.ArrayList();
  String[] ps = (v == null ? "" : v).split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    if (t.length() > 0 && !l.contains(t)) l.add(t);
  }
  return (String[]) l.toArray(new String[0]);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "farming.sickle.enabled", true);
  String[] it = parse(p.getProperty("farming.sickle.items", DEFAULT_ITEMS));
  if (it.length == 0) { @PKG@.SkillCfg.warn("farming.sickle.items is empty - using " + DEFAULT_ITEMS); it = new String[] { DEFAULT_ITEMS }; }
  ITEMS = it;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < it.length; i++) { if (i > 0) sb.append(','); sb.append(it[i]); }
  ITEMS_TEXT = sb.toString();
  KEYS = null;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return ON ? "on (" + ITEMS_TEXT + ", one award per crop)" : "off";
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static String checkItems(String key, String v) {
  if (v == null) return null;
  if (parse(v).length == 0) return "Write at least one item id start, like Tool_Sickle_.";
  return null;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  BRK.keySet().retainAll(online);
  USE.keySet().retainAll(online);
  PEND.keySet().retainAll(online);
}"""), skl))
'''
before("# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================\n", EARLY_CFG)

# ---------------------------------------------------------------------------------------------------------------- SkillCfg: the appended block + the loader
after('''cfg.addMethod(CtNewMethod.make(f"""
public static void ensureManaRegen(java.util.Properties p) {{
  if (p.getProperty("mana.regen.inCombat") != null) return;
  appendBlock("mana.regen.inCombat", MREG_DEFAULTS, "Mana regen in combat");
}}""", cfg))
''', r'''# 0.4.14: the kill XP / roll / gathering pace / sickle block, appended once: its comment lines + only the key lines the file does not have yet
# (an admin's line is never duplicated or rewritten; nothing to add = nothing written), in the file's own line ending (appendBlock)
cfg.addField(CtField.make("public static final String N14_DEFAULTS = " + N14_LIT + ";", cfg))
cfg.addMethod(CtNewMethod.make(J14(r"""
public static String block14(java.util.Properties p) {
  String[] ls = N14_DEFAULTS.split("\n");
  StringBuilder sb = new StringBuilder();
  boolean any = false;
  for (int i = 0; i < ls.length; i++) {
    String ln = ls[i];
    if (ln.length() == 0) continue;
    if (ln.startsWith("#")) { sb.append(ln).append("\n"); continue; }
    int eq = ln.indexOf('=');
    String k = eq > 0 ? ln.substring(0, eq) : ln;
    if (p != null && p.getProperty(k) != null) continue;
    any = true;
    sb.append(ln).append("\n");
  }
  return any ? sb.toString() : null;
}"""), cfg))
cfg.addMethod(CtNewMethod.make(J14(r"""
public static void ensure14(java.util.Properties p) {
  String b = block14(p);
  if (b == null) return;
  appendBlock("combat.levelXp.enabled, acro.rollBonus, gather.boost.*, farming.sickle.*", b, "kill XP by mob level / roll landings / gathering pace / sickle swings");
}"""), cfg))
''')
after("    ensureManaRegen(p);   // 0.4.12: the Mana regen in combat block, once\n",
      "    ensure14(p);          // 0.4.14: the kill XP / roll / gathering pace / sickle block, once (only the keys the file lacks)\n")
after("    {PKG}.ManaRegen.IN_COMBAT = (int) (mrc < 0L ? 0L : (mrc > 100L ? 100L : mrc));\n",
      "    {PKG}.MobXp.read(p);        // 0.4.14: kill XP by mob level\n"
      "    {PKG}.AcroCfg.readRoll(p);  // 0.4.14: roll landings\n"
      "    {PKG}.GatherPace.read(p);   // 0.4.14: the gathering pace\n"
      "    {PKG}.Sickle.read(p);       // 0.4.14: sickle swings\n")
rep('''", in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "%" + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''',
    '''", in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "%" + ", kill XP by mob level " + {PKG}.MobXp.text() + ", roll landings " + {PKG}.AcroCfg.rollText() + ", gathering pace " + {PKG}.GatherPace.text() + ", sickle swings " + {PKG}.Sickle.text() + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''')

# ---------------------------------------------------------------------------------------------------------------- GatherPace.apply (+ the Stats line) before SkillXp
PACE = r'''# ================= GatherPace.apply (0.4.14): earned gathering XP x the pace multiplier of the skill's CURRENT level (world thread: SkillXp.gain4's
# bonus path - blocks, F-harvests, sickle swings - and FellCredit.one - felled logs), BEFORE the tree Wisdom bonus. Any other slot, or a
# multiplier of exactly 1, returns amt unchanged (no rounding); the fraction is paid by chance (a product within 1e-9 of a whole number
# counts as that number: 2.55 x 20 = 51, never 52)
gpc.addMethod(CtNewMethod.make(J14(r"""
public static long apply(java.util.UUID u, int slot, long amt) {
  if (amt <= 0L || u == null || !on(slot)) return amt;
  double m = mult(@PKG@.SkillStore.level(u, slot));
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
gpc.addMethod(CtNewMethod.make(J14(r"""
public static String statsLine(int slot, int lv) {
  if (!on(slot)) return null;
  double m = mult(lv);
  if (m == 1.0) return null;
  String x = @PKG@.DivCfg.num(m);
  if (lv <= UNTIL) {
    if (LATE == EARLY) return "Gathering XP x" + x;
    if (FROM > UNTIL + 1) return "Gathering XP x" + x + " up to level " + UNTIL + ", then easing to x" + @PKG@.DivCfg.num(LATE) + " by level " + FROM;
    return "Gathering XP x" + x + " up to level " + UNTIL + ", then x" + @PKG@.DivCfg.num(LATE);
  }
  if (lv < FROM) return "Gathering XP x" + x + " now - easing to x" + @PKG@.DivCfg.num(LATE) + " by level " + FROM;
  return "Gathering XP x" + x + " (gathering pace)";
}"""), gpc))

'''
before("# ================= SkillXp: award + level-up (world thread) =================\n", PACE)
rep("  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, amount);\n",
    "  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, {PKG}.GatherPace.apply(u, skill, amount));   // 0.4.14: the gathering pace, then the tree Wisdom\n"
    "  if (amount <= 0L) return;\n")
rep("        long amt = {PKG}.SkillBonus.boost(W.u, row, xp);\n",
    "        long amt = {PKG}.SkillBonus.boost(W.u, row, {PKG}.GatherPace.apply(W.u, row, xp));   // 0.4.14: the gathering pace first\n")

# ---------------------------------------------------------------------------------------------------------------- Sickle: the crop map, the contexts, the award
SICKLE = r'''# ================= Sickle (0.4.14, research/Tool-Levels-Spec.md question 3): sickle swing harvests pay Farming XP + roll double drops =================
# A sickle swing's HitBlock runs HarvestCrop -> FarmingUtil.harvest0 -> giveDrops -> ItemUtils.interactivelyPickupItem: one
# InteractivelyPickupItemEvent per drop stack, no break event, no position (bytecode asserted above). SickleSys collects the stacks of one tick
# (PEND) unless they belong to an F pickup (BRK) or an F-harvest (USE); SickleTask pays them on the world thread after every other system.
skl.addMethod(CtNewMethod.make(J14(r"""
public static boolean isSickle(String id) {
  if (id == null) return false;
  String[] it = ITEMS;
  for (int i = 0; i < it.length; i++) if (id.startsWith(it[i])) return true;
  return false;
}"""), skl))
# BreakSys, synchronously: a BreakBlockEvent with a NULL item = BlockHarvestUtils.performPickupByInteraction (the F pickup of a loose block), whose
# drops arrive as pickups right after it on the same thread; its BreakTask closes the context (breakDone) after the dispatch
skl.addMethod(CtNewMethod.make(J14(r"""
public static void breakOpen(java.util.UUID u, Object ev) {
  if (u == null) return;
  BRK.put(u, new Object[] { Thread.currentThread(), Long.valueOf(System.nanoTime()), ev });
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void breakDone(java.util.UUID u, Object ev) {
  if (u == null || BRK.isEmpty()) return;
  Object o = BRK.get(u);
  if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] == ev) BRK.remove(u, o);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static boolean inBreak(java.util.UUID u, long nanos) {
  Object o = BRK.get(u);
  if (!(o instanceof Object[])) return false;
  Object[] a = (Object[]) o;
  if (a.length < 2 || a[0] != Thread.currentThread() || !(a[1] instanceof Long)) return false;
  long d = nanos - ((Long) a[1]).longValue();
  return d >= 0L && d < BREAK_NS;
}"""), skl))
# HarvestSys, synchronously: UseBlockEvent$Post on a ripe harvestable block = an F-harvest (HarvestTask pays it); its drops come later, within
# WINDOW_MS (the SkyyCollections rule) - never paid as sickle swings
skl.addMethod(CtNewMethod.make(J14(r"""
public static void useOpen(@ACH@ chunk, int idx, @ST@ st) {
  try {
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    USE.put(pr.getUuid(), Long.valueOf(System.currentTimeMillis()));
  } catch (Throwable t) { }
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static boolean inUse(java.util.UUID u, long now) {
  Object o = USE.get(u);
  return o instanceof Long && now - ((Long) o).longValue() <= WINDOW_MS;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void failed(Throwable t) {
  if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("sickle swing harvest XP failed (logged once): " + t); }
}"""), skl))
# the crop map: produce item -> {Long the LOWEST Farming XP of its crops, Boolean a crop can drop it twice in one harvest, String the
# alphabetically first crop family (Perks.matches), HashSet every item id those crops' harvests can drop (the produce included)}
skl.addMethod(CtNewMethod.make(J14(r"""
public static void put(java.util.HashMap m, String key, long xp, boolean multi, String fam, java.util.Set ids) {
  Object o = m.get(key);
  if (o instanceof Object[]) {
    Object[] e = (Object[]) o;
    if (xp < ((Long) e[0]).longValue()) e[0] = Long.valueOf(xp);
    if (multi) e[1] = Boolean.TRUE;
    if (fam != null && (e[2] == null || fam.compareTo((String) e[2]) < 0)) e[2] = fam;
    if (ids != null) ((java.util.HashSet) e[3]).addAll(ids);
    return;
  }
  java.util.HashSet s = new java.util.HashSet();
  if (ids != null) s.addAll(ids);
  s.add(key);
  m.put(key, new Object[] { Long.valueOf(xp), Boolean.valueOf(multi), fam, s });
}"""), skl))
# one block type: a RIPE crop (the StageFinal state of a block with growth states) with a Harvest drop whose block rule pays Farming XP ->
# its produce = the first item its harvest drops emit (giveDrops -> BlockHarvestUtils.getDrops: the drop list's items in container order,
# then the Harvest ItemId); multi = that item can be emitted twice by one harvest (berry bushes).
# FIX ROUND F1 (reviews 2026-10-03): ONLY StageFinal. FarmingUtil.harvest0 harvests any block with a Harvest drop at once (no ripeness, no
# placed check), and a pickup carries no position, so a sickle swing cannot tell a placed block: a stateless Health / Mana / Stamina plant
# or cactus flower hands back its own item -> place, swing, place paid Farming XP forever and the double drop copied the plant. StageFinal =
# what HarvestSys pays for an F-harvest and what classifyBreak never place-checks (a crop only gets there by growing); everything else pays
# through breaking only (BreakTask: placed blocks pay nothing under ignorePlaced; with it off they pay but never double)
skl.addMethod(CtNewMethod.make(J14(r"""
public static void addCrop(java.util.HashMap m, @BTY@ bt) {
  if (bt == null) return;
  @BGA@ g = bt.getGathering();
  if (g == null) return;
  @HDT@ h = g.getHarvest();
  if (h == null) return;
  if (!@PKG@.SkillCfg.hasFinalStage(bt) || !"StageFinal".equals(@PKG@.SkillCfg.stateOf(bt))) return;
  String fam = @PKG@.SkillCfg.familyId(bt);
  long[] r = @PKG@.SkillCfg.resolve(fam);
  if (r == null || r[0] != (long) @PKG@.SkillDefs.FARMING || r[1] <= 0L) return;
  String key = null;
  int cnt = 0;
  java.util.HashSet ids = new java.util.HashSet();
  String dl = h.getDropListId();
  if (dl != null) {
    @IDL@ l = (@IDL@) @IDL@.getAssetMap().getAsset(dl);
    if (l != null && l.getContainer() != null) {
      java.util.List ds = l.getContainer().getAllDrops(new java.util.ArrayList());
      for (int j = 0; ds != null && j < ds.size(); j++) {
        Object o = ds.get(j);
        if (!(o instanceof @IDR@)) continue;
        String id = ((@IDR@) o).getItemId();
        if (id == null) continue;
        ids.add(id);
        if (key == null) key = id;
        if (key.equals(id)) cnt++;
      }
    }
  }
  String iid = h.getItemId();
  if (iid != null) {
    ids.add(iid);
    if (key == null) key = iid;
    if (key.equals(iid)) cnt++;
  }
  if (key == null) return;
  put(m, key, r[1], cnt > 1, fam, ids);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static java.util.HashMap keys() {
  java.util.HashMap k = KEYS;
  if (k != null) return k;
  java.util.HashMap m = new java.util.HashMap();
  try {
    @BTM@ am = @BTY@.getAssetMap();
    int n = am.getNextIndex();
    for (int i = 0; i < n; i++) {
      try { addCrop(m, (@BTY@) am.getAsset(i)); } catch (Throwable t) { }
    }
  } catch (Throwable t) { failed(t); }
  KEYS = m;
  return m;
}"""), skl))
# PURE: one tick's stacks (in pickup order) -> crops Object[]{String produce, ArrayList its stacks}: a produce stack starts a crop (its harvest
# emits the produce first), the stacks after it belong to it when that crop can drop them (anything else the same swing harvested - sap, a
# flower - is left out, so the double drop copies only the crop's own items); a multi-source produce directly after a stack of the same
# produce joins it
skl.addMethod(CtNewMethod.make(J14(r"""
public static java.util.ArrayList segments(java.util.List stacks, java.util.Map keys) {
  java.util.ArrayList segs = new java.util.ArrayList();
  Object[] cur = null;
  java.util.Set own = null;
  String prev = null;
  for (int i = 0; stacks != null && i < stacks.size(); i++) {
    Object o = stacks.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ is = (@IS@) o;
    String id = is.getItemId();
    if (id == null) continue;
    Object info = keys == null ? null : keys.get(id);
    if (info instanceof Object[]) {
      Object[] in = (Object[]) info;
      boolean multi = Boolean.TRUE.equals(in[1]);
      if (!(multi && cur != null && id.equals(prev) && id.equals(cur[0]))) {
        cur = new Object[] { id, new java.util.ArrayList() };
        segs.add(cur);
        own = in.length > 3 && in[3] instanceof java.util.Set ? (java.util.Set) in[3] : null;
      }
    } else if (cur != null && own != null && !own.contains(id)) {
      prev = id;
      continue;
    }
    if (cur != null) ((java.util.ArrayList) cur[1]).add(is);
    prev = id;
  }
  return segs;
}"""), skl))
# metadata-free copies (the double drop gives the crop's items once more)
skl.addMethod(CtNewMethod.make(J14(r"""
public static java.util.ArrayList copies(java.util.List l) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; l != null && i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ is = (@IS@) o;
    if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
    out.add(new @IS@(is.getItemId(), is.getQuantity()));
  }
  return out;
}"""), skl))
# world thread (SickleTask): the final stacks of the not-cancelled pickups -> crops; each crop: its Farming XP once (SkillXp.gain = the pace +
# Wisdom, the chat line, level ups) and one Farming double-drop roll (the level after the award, like BreakTask). Returns the crops paid.
skl.addMethod(CtNewMethod.make(J14(r"""
public static int award(@PR@ pr, java.util.List evs, String wn) {
  if (pr == null || evs == null) return 0;
  java.util.ArrayList st = new java.util.ArrayList();
  for (int i = 0; i < evs.size(); i++) {
    Object o = evs.get(i);
    if (!(o instanceof @IPE@)) continue;
    @IPE@ e = (@IPE@) o;
    if (e.isCancelled()) continue;
    @IS@ is = e.getItemStack();
    if (is == null || is.isEmpty() || is.getItemId() == null) continue;
    st.add(is);
  }
  if (st.isEmpty()) return 0;
  java.util.HashMap ks = keys();
  if (ks == null || ks.isEmpty()) return 0;
  java.util.ArrayList segs = segments(st, ks);
  java.util.UUID u = pr.getUuid();
  int n = 0;
  for (int i = 0; i < segs.size(); i++) {
    Object[] sg = (Object[]) segs.get(i);
    Object io = ks.get(sg[0]);
    if (!(io instanceof Object[])) continue;
    Object[] info = (Object[]) io;
    long amt = @PKG@.SkillCfg.scaled(((Long) info[0]).longValue());
    if (amt > 0L) @PKG@.SkillXp.gain(pr, @PKG@.SkillDefs.FARMING, amt);
    try {
      double c = @PKG@.Perks.chanceU(u, @PKG@.SkillDefs.FARMING, @PKG@.SkillStore.level(u, @PKG@.SkillDefs.FARMING));
      if (c > 0.0 && @PKG@.Perks.matches(@PKG@.SkillDefs.FARMING, (String) info[2]) && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < c)
        @PKG@.Perks.doubled(pr, copies((java.util.List) sg[1]), @PKG@.SkillDefs.FARMING, wn);
    } catch (Throwable t) {
      if (!@PKG@.Perks.DD_FAILED_ONCE) { @PKG@.Perks.DD_FAILED_ONCE = true; @PKG@.SkillCfg.warn("double drop failed (logged once): " + t); }
    }
    n++;
  }
  if (n > 0 && !SEEN) { SEEN = true; @PKG@.SkillCfg.info("sickle swing harvests reach SkyySkills - they pay Farming XP and roll double drops (one award per crop)"); }
  return n;
}"""), skl))
# SickleTask: this tick's pickups of one player, on the world thread after every system saw them (a cancelled pickup pays nothing)
sktk.addInterface(pool.get("java.lang.Runnable"))
sktk.addField(CtField.make("public java.util.UUID u;", sktk))
sktk.addField(CtField.make("public String wn;", sktk))
sktk.addConstructor(CtNewConstructor.make("public SickleTask(java.util.UUID u, String wn) { this.u = u; this.wn = wn; }", sktk))
sktk.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  try {
    Object o = @PKG@.Sickle.PEND.remove(this.u);
    if (!(o instanceof java.util.List)) return;
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (@PKG@.SkillStore.bridge().get("profile:busy:" + this.u.toString()) != null) return;
    @PKG@.Sickle.award(pr, (java.util.List) o, this.wn);
  } catch (Throwable t) { @PKG@.Sickle.failed(t); }
}"""), sktk))
# SickleSys (world thread): one pickup into this tick's burst; the first of a burst queues the SickleTask
skl.addMethod(CtNewMethod.make(J14(r"""
public static void add(java.util.UUID u, Object e, @WLD@ w) {
  if (u == null || e == null || w == null) return;
  Object o = PEND.get(u);
  if (o instanceof java.util.ArrayList) { ((java.util.ArrayList) o).add(e); return; }
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(e);
  PEND.put(u, l);
  try { w.execute(new @PKG@.SickleTask(u, w.getName())); } catch (Throwable t) { PEND.remove(u); }
}"""), skl))

'''
before("# ================= Brew.extraPotion (0.4): the brewer's extra-potion perk (world thread) =================\n", SICKLE)

# ---------------------------------------------------------------------------------------------------------------- Acro: the rolled landing note + its payout
rep("#  287 prev extraJumpsUsed, 288-291 spare. reset (world change) and profileReset also zero 281, 282, 284 and 285.\n",
    "#  287 prev extraJumpsUsed, 288-291 spare. reset (world change) and profileReset also zero 281, 282, 284 and 285.\n"
    "# 0.4.14 (roll landings): 288 rolled landing ms (RollSys.land, 0 = none pending), 289 its fall damage WITHOUT the roll normalised to 100 max\n"
    "#  health, 290 resolved; falls() pays it 400 ms later x (1 + acro.rollBonus); profileReset zeroes them; 291 spare.\n")
after("  s[15] = 0.0; s[16] = 0.0; s[17] = 0.0; s[18] = 0.0; s[21] = 0.0; s[152] = 0.0;\n",
      "  s[288] = 0.0; s[289] = 0.0; s[290] = 0.0;   // 0.4.14: a rolled landing not paid yet\n")
after("    {PKG}.ManaRegen.CARRY.keySet().retainAll(online);   // 0.4.13 fix F1's per-player record\n",
      "    {PKG}.Sickle.retain(online);   // 0.4.14: the sickle swing contexts and this tick's pickups\n")
after("public static void noteFall(java.util.UUID u, float amount) {\n  double[] s = state(u);\n",
      "  if (s[288] > 0.0 && (double) System.currentTimeMillis() - s[288] < 1000.0) return;   // 0.4.14: this landing was a roll (RollSys noted it unreduced)\n")
after('''  s[16] = (double) amount;
  s[17] = 0.0;
}""", acro))
''', r'''# 0.4.14 (roll landings): RollSys.land (world thread, before the engine's FallDamagePlayers) - a landing whose roll engaged; amount = the fall
# damage WITHOUT the roll normalised to 100 max health (AcroFallSeenSys' scale); falls() pays it 400 ms later
acro.addMethod(CtNewMethod.make("""
public static void noteRoll(java.util.UUID u, float amount) {
  double[] s = state(u);
  s[288] = (double) System.currentTimeMillis();
  s[289] = (double) amount;
  s[290] = 0.0;
}""", acro))
''')
rep('''  if (s[18] > 0.0 && t - s[18] >= 700.0) s[18] = 0.0;
}}""", acro))''', '''  // 0.4.14: a rolled landing pays the fall's UNREDUCED XP + acro.rollBonus of it (alive, not in water, not creative; acro.fallXpMax per landing,
  // acro.fallMaxXpPerMinute through takeFall in flush - the existing caps)
  if (s[288] > 0.0 && s[290] < 0.5 && t - s[288] >= 400.0) {{
    s[290] = 1.0;
    if (!creative && alive(store, ref) && !inWater(store, ref)) {{
      double x = s[289] * {PKG}.AcroCfg.FALL_DMG_XP * (1.0 + {PKG}.AcroCfg.ROLL);
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;
      if (x > 0.0) s[152] = s[152] + x;
    }}
    s[288] = 0.0;
  }}
  if (s[18] > 0.0 && t - s[18] >= 700.0) s[18] = 0.0;
}}""", acro))''')

# ---------------------------------------------------------------------------------------------------------------- RollSys
ROLLSYS = r'''# ================= RollSys (0.4.14): roll landings (Skyy 2026-10-02) - an EntityTickingSystem BEFORE the engine's DamageSystems$FallDamagePlayers
# (SystemDependency BEFORE: the engine sorts every system of the store in one dependency graph; FallDamagePlayers itself runs BEFORE
# ProcessPlayerInput, which consumes the queue). It reads the player's PlayerInput movement update queue READ-ONLY and replays the engine's
# landing rule (bytecode asserted above): speed = |the client velocity y| (each SetClientVelocity updates it), the first SetMovementStates
# with onGround while the fall distance is > 0 is the landing; speed > MinFallSpeedToEngageRoll and not inFluid -> damage; rolling + speed
# <= MaxFallSpeedToEngageRoll = the roll engaged (full or partial mitigation) -> Acro.noteRoll(the UNREDUCED damage x 100 / max health).
# Non-rolled landings are left to AcroFallSeenSys (as before). Never writes a component, never throws (logged once).
rsy.addConstructor(CtNewConstructor.make("public RollSys() { super(); }", rsy))
rsy.addField(CtField.make("public static boolean FAILED_ONCE = false;", rsy))
rsy.addField(CtField.make("public static volatile java.util.Set DEPS = null;", rsy))
rsy.addField(CtField.make("public static volatile long NOTED = 0L;", rsy))   # rolled landings noted since the start (diagnostics)
rsy.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return @QRY@.and(new @QRY@[] { (@QRY@) @PLA@.getComponentType(), (@QRY@) @PR@.getComponentType(), (@QRY@) @PIN@.getComponentType(), (@QRY@) @ESM@.getComponentType() });
}"""), rsy))
rsy.addMethod(CtNewMethod.make(J14(r"""
public java.util.Set getDependencies() {
  java.util.Set d = DEPS;
  if (d == null) {
    d = java.util.Collections.singleton(new @SDEP@(@DORD@.BEFORE, @FDP@.class));
    DEPS = d;
  }
  return d;
}"""), rsy))
# PURE = FallDamagePlayers' arithmetic: {damage without the roll, the engine's damage, 1 = the roll engaged (mitigated)}; 0 / 0 / 0 when the
# landing makes no fall damage (not faster than min, or in fluid)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static int[] damage(double sp, float min, float full, float eng, float pct, float mx, boolean rolling, boolean fluid) {
  if (!(sp > (double) min) || fluid) return new int[] { 0, 0, 0 };
  double base = Math.pow(0.5799999833106995 * (sp - (double) min), 2.0) + 10.0;
  int d0 = (int) Math.floor((double) mx / 100.0 * base);
  int d1 = d0;
  int rolled = 0;
  if (rolling) {
    if (sp <= (double) full) { d1 = 0; rolled = 1; }
    else if (sp <= (double) eng) { d1 = (int) ((double) d0 * (1.0 - (double) pct / 100.0)); rolled = 1; }
  }
  return new int[] { d0, d1, rolled };
}"""), rsy))
# the world's MovementConfig asset (the lookup FallDamagePlayers and Acro.djMaxFall make)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static @MCF@ movementConfig(@ST@ store) {
  try {
    @WLD@ w = ((@EST@) store.getExternalData()).getWorld();
    int mi = w.getGameplayConfig().getPlayerConfig().getMovementConfigIndex();
    return (@MCF@) @MCF@.getAssetMap().getAsset(mi);
  } catch (Throwable t) { return null; }
}"""), rsy))
# FIX ROUND F2 (reviews 2026-10-03): the store's world has fall damage on - the switch the engine's FallDamagePlayers.tick(F, I, Store) tests
# before it looks at ANY landing (bytecode asserted above); off (or no world / config) = no roll note, like 0.4.13 (no Damage, no fall XP)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static boolean fallDamageOn(@ST@ store) {
  try {
    if (store == null) return false;
    Object ext = store.getExternalData();
    if (!(ext instanceof @EST@)) return false;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return false;
    @WCFG@ wc = w.getWorldConfig();
    return wc != null && wc.isFallDamageEnabled();
  } catch (Throwable t) { return false; }
}"""), rsy))
# one landing: the roll's note, or nothing; returns the unreduced damage noted (0 = nothing noted)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static int land(@ACH@ chunk, int idx, @ST@ store, @MVT@ ms, double sp) {
  if (ms == null || !ms.rolling) return 0;
  @MCF@ mc = movementConfig(store);
  if (mc == null) return 0;
  float mx = 100.0f;
  @ESM@ m = (@ESM@) chunk.getComponent(idx, @ESM@.getComponentType());
  if (m != null) {
    @ESV@ hv = m.get(@DST@.getHealth());
    if (hv != null && hv.getMax() > 0.0f) mx = hv.getMax();
  }
  int[] d = damage(sp, mc.getMinFallSpeedToEngageRoll(), mc.getMaxFallSpeedRollFullMitigation(), mc.getMaxFallSpeedToEngageRoll(), mc.getFallDamagePartialMitigationPercent(), mx, true, ms.inFluid);
  if (d[2] == 0 || d[0] <= 0) return 0;
  @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
  if (pr == null) return 0;
  @PKG@.Acro.noteRoll(pr.getUuid(), (float) d[0] * 100.0f / mx);
  NOTED = NOTED + 1L;
  return d[0];
}"""), rsy))
rsy.addMethod(CtNewMethod.make(J14(r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (!@PKG@.AcroCfg.ENABLED || !(@PKG@.AcroCfg.ROLL > 0.0)) return;
    @PIN@ in = (@PIN@) chunk.getComponent(idx, @PIN@.getComponentType());
    if (in == null) return;
    java.util.List q = in.getMovementUpdateQueue();
    if (q == null || q.isEmpty()) return;
    @PLA@ p = (@PLA@) chunk.getComponent(idx, @PLA@.getComponentType());
    if (p == null || !(p.getCurrentFallDistance() > 0.0)) return;
    if (!fallDamageOn(store)) return;   // fix round F2: a world with fall damage off - the engine skips every landing there
    double sp = 0.0;
    @VEL@ v = (@VEL@) chunk.getComponent(idx, @VEL@.getComponentType());
    if (v != null && v.getClientVelocity() != null) sp = Math.abs(v.getClientVelocity().y());
    for (int i = 0; i < q.size(); i++) {
      Object o = q.get(i);
      if (o instanceof @PISV@) {
        @V3D@ cv = ((@PISV@) o).getVelocity();
        if (cv != null) sp = Math.abs(cv.y());
        continue;
      }
      if (!(o instanceof @PISM@)) continue;
      @MVT@ ms = ((@PISM@) o).movementStates();
      if (ms == null || !ms.onGround) continue;
      land(chunk, idx, store, ms, sp);
      return;
    }
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("roll landing check failed (logged once): " + t); }
  }
}"""), rsy))

'''
before("# ================= CombatDmgSys (0.3): combat perk = more damage with your class weapons =================\n", ROLLSYS)

# ---------------------------------------------------------------------------------------------------------------- MobXp maths (before PartyXp)
MOBXP = r'''# ================= MobXp maths (0.4.14) - compiled before PartyXp (one2 uses them) =================
# levelFactor = 1 + BONUS x (L - 1) (1 without a level or with the part off); gapFactor(L, S): d = L - S, above FREE +ABOVE a level up to MAX,
# below -FREE -BELOW a level down to MIN; factor = both; pay = SkillCfg.classXp's rule with the factor (one chance rounding, the 1e-9 rule)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double levelFactor(int L) {
  if (!ON || L < 1) return 1.0;
  double f = 1.0 + BONUS * (double) (L - 1);
  return f > 0.0 ? f : 0.0;
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double gapFactor(int L, int S) {
  if (!ON || L < 1) return 1.0;
  int d = L - (S < 0 ? 0 : S);
  if (d > FREE) {
    double g = 1.0 + ABOVE * (double) (d - FREE);
    return g > MAX ? MAX : g;
  }
  if (d < -FREE) {
    double g = 1.0 - BELOW * (double) (-d - FREE);
    return g < MIN ? MIN : g;
  }
  return 1.0;
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double factor(int L, int S) {
  return levelFactor(L) * gapFactor(L, S);
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static long pay(int slot, long base, double factor) {
  if (base <= 0L || !(factor > 0.0)) return 0L;
  double m = @PKG@.SkillDefs.isClass(slot) ? @PKG@.SkillCfg.CLASS_MULT : 1.0;
  if (!(m > 0.0)) return 0L;
  double x = (double) base * m * factor;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}"""), mxp))
# the dead mob's level from SkyyMobs (bridge mob:fn:level, Object[]{world name, the entity's UUIDComponent uuid} -> Integer, -1 = none); its
# MOBS entry is removed only when the entity leaves the store, so it still answers at the DeathComponent. -1 = no level (any failure too)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static int levelOf(@ST@ s, @REF@ r) {
  try {
    if (s == null || r == null) return -1;
    Object f = @PKG@.SkillStore.bridge().get("mob:fn:level");
    if (!(f instanceof java.util.function.Function)) return -1;
    @UUC@ uc = (@UUC@) s.getComponent(r, @UUC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return -1;
    String wn = null;
    Object ext = s.getExternalData();
    if (ext instanceof @EST@) {
      @WLD@ w = ((@EST@) ext).getWorld();
      if (w != null) wn = w.getName();
    }
    Object o = ((java.util.function.Function) f).apply(new Object[] { wn, uc.getUuid() });
    if (!(o instanceof Number)) return -1;
    int L = ((Number) o).intValue();
    return L >= 1 ? L : -1;
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("mob level lookup (mob:fn:level) failed (logged once): " + t); }
    return -1;
  }
}"""), mxp))

'''
before('# ================= PartyXp (0.4.2 stage 2, beta backlog 6: "party should share combat XP") =================\n', MOBXP)

# ---------------------------------------------------------------------------------------------------------------- PartyXp: each member's own gap
rep('''# one member: every rule of the header comment; returns the XP paid (0 = skipped)
pxp.addMethod(CtNewMethod.make(f"""
public static long one(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2) {{''',
    '''# one member: every rule of the header comment; returns the XP paid (0 = skipped). 0.4.14: with a mob level (ml >= 1) the member's base is
# MobXp.pay(the killer's slot, the raw kill XP, levelFactor x the gap against THIS member's class skill) - Skyy: "the party share uses each
# member's own skill"; without one (ml -1) the killer's base, exactly 0.4.13
pxp.addMethod(CtNewMethod.make(f"""
public static long one2(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2, int ks, long raw, int ml) {{''')
rep('''  int slot = slotFor(mu);
  if (slot < 0) return 0L;
  long amt = amount(base, fr);
''', '''  int slot = slotFor(mu);
  if (slot < 0) return 0L;
  long b = base;
  if (ml >= 1) b = {PKG}.MobXp.pay(ks, raw, {PKG}.MobXp.factor(ml, {PKG}.SkillStore.level(mu, slot)));   // 0.4.14
  long amt = amount(b, fr);
''')
rep('''  {PKG}.SkillXp.gain4(mp, slot, amt, false, false, kn == null ? "" : kn);
  return amt;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void share({PR} kp, {REF} kr, {ST} s, long base) {{
  if (!{PKG}.PartyCfg.on() || base <= 0L || kp == null || kr == null || s == null) return;''', '''  {PKG}.SkillXp.gain4(mp, slot, amt, false, false, kn == null ? "" : kn);
  return amt;
}}""", pxp))
# 0.4.13's one (no mob level), kept for any caller of the old signature
pxp.addMethod(CtNewMethod.make(f"""
public static long one(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2) {{
  return one2(ku, kn, kpos, s, mid, base, fr, r2, -1, 0L, -1);
}}""", pxp))
# 0.4.14: share2 = 0.4.13's share + the mob level (ks = the killer's class slot, raw = the kill XP before the class multiplier, ml = the mob level
# or -1); members are skipped only when nothing could be shared (no level: the killer's cx is 0; with a level: the raw kill XP is 0)
pxp.addMethod(CtNewMethod.make(f"""
public static void share2({PR} kp, {REF} kr, {ST} s, long base, int ks, long raw, int ml) {{
  if (!{PKG}.PartyCfg.on() || (ml >= 1 ? raw <= 0L : base <= 0L) || kp == null || kr == null || s == null) return;''')
rep('''  for (int i = 0; i < ms.length; i++) {{
    try {{
      one(ku, kn, kpos, s, ms[i], base, fr, r2);
    }} catch (Throwable t) {{''', '''  for (int i = 0; i < ms.length; i++) {{
    try {{
      one2(ku, kn, kpos, s, ms[i], base, fr, r2, ks, raw, ml);
    }} catch (Throwable t) {{''')
after('''      if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("party combat XP share failed (logged once): " + t); }}
    }}
  }}
}}""", pxp))
''', '''# 0.4.13's share (no mob level), kept for any caller of the old signature
pxp.addMethod(CtNewMethod.make(f"""
public static void share({PR} kp, {REF} kr, {ST} s, long base) {{
  share2(kp, kr, s, base, -1, 0L, -1);
}}""", pxp))
''')
# FIX ROUND F3 (numbers review): with a mob level each member's share is worked out with THEIR class skill level (one2), so "of your kill XP"
# is only exact without one - the Stats how-to line says which, and the row help no longer says "the killer's class XP"
rep('''  return ". Party members within " + {PKG}.PartyCfg.blocks() + " blocks get " + {PKG}.PartyCfg.pct() + " of your kill XP (in their own class skill)";
''', '''  boolean lv = false;
  try {{ lv = {PKG}.MobXp.ON && ({PKG}.SkillStore.bridge().get("mob:fn:level") instanceof java.util.function.Function); }} catch (Throwable t) {{ lv = false; }}
  if (lv) return ". Party members within " + {PKG}.PartyCfg.blocks() + " blocks get " + {PKG}.PartyCfg.pct() + " of the kill XP at their own class skill level";   // 0.4.14 fix round
  return ". Party members within " + {PKG}.PartyCfg.blocks() + " blocks get " + {PKG}.PartyCfg.pct() + " of your kill XP (in their own class skill)";
''')
rep('''     "Share of the killer's class XP each nearby party member gets (0.5 = half). The killer keeps all.", "reload"),''',
    '''     "Share of the kill XP each nearby party member gets (0.5 = half), at their own class skill level.", "reload"),''')

# ---------------------------------------------------------------------------------------------------------------- BreakSys / BreakTask / HarvestSys / SickleSys
rep('''    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    Object fs = null;''', '''    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    if (e.getItemInHand() == null) {PKG}.Sickle.breakOpen(pr.getUuid(), e);   // 0.4.14: an F pickup of a loose block - its pickups are no sickle swing
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    Object fs = null;''')
rep('''public void run() {{
  try {{
    if (this.ev.isCancelled()) {{
      try {{ {PKG}.Fell.restore(this.world, this.ev, this.unclaimed); }}''', '''public void run() {{
  try {{
    {PKG}.Sickle.breakDone(this.u, this.ev);   // 0.4.14: the F-pickup context ends with its break's task
    if (this.ev.isCancelled()) {{
      try {{ {PKG}.Fell.restore(this.world, this.ev, this.unclaimed); }}''')
rep('''    {BGA} g = bt.getGathering();
    if (g == null || g.getHarvest() == null) return;
    long[] rr = ''', '''    {BGA} g = bt.getGathering();
    if (g == null || g.getHarvest() == null) return;
    {PKG}.Sickle.useOpen(chunk, idx, st);   // 0.4.14: an F-harvest - its pickups are no sickle swing (HarvestTask pays it)
    long[] rr = ''')
SICKLESYS = r'''# 0.4.14: sickle swing harvests (Tool-Levels-Spec question 3) - InteractivelyPickupItemEvent on the player (ItemUtils.interactivelyPickupItem:
# F pickups, F-harvests and sickle swings; ground pickups never fire it). Not an F pickup (BRK), not an F-harvest (USE), not creative, the main
# hand holds a sickle (farming.sickle.items) -> this tick's burst (Sickle.add); SickleTask pays it on the world thread after the dispatch.
event_system(sksy, "SickleSys", IPE, f"""
    {IPE} e = ({IPE}) ev;
    if (!{PKG}.Sickle.ON) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if ({PKG}.Sickle.inBreak(u, System.nanoTime())) return;
    if ({PKG}.Sickle.inUse(u, System.currentTimeMillis())) return;
    if ({PKG}.SkillXp.creative(st, r)) return;
    {IS} h = {INVC}.getItemInHand(st, r);
    if (h == null || h.isEmpty() || !{PKG}.Sickle.isSickle(h.getItemId())) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    {PKG}.Sickle.add(u, e, w);""")

# 0.4.14 kill XP by mob level (world thread, KillSys): x levelFactor x the gap against the killer's class skill (before this kill) when SkyyMobs
# knows the mob's level, else EXACTLY 0.4.13 (SkillCfg.classXp); then the award and the party share (each member's own gap)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static long kill(@PR@ pr, @REF@ k, @ST@ s, int slot, long base, @REF@ npc) {
  int L = levelOf(s, npc);
  long cx;
  if (ON && L >= 1) cx = pay(slot, base, factor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
  else cx = @PKG@.SkillCfg.classXp(slot, base);
  @PKG@.SkillXp.gain(pr, slot, cx);
  @PKG@.PartyXp.share2(pr, k, s, cx, slot, base, ON ? L : -1);
  return cx;
}"""), mxp))

'''
before("# Combat: DeathComponent added to an NPC killed by a player\n", SICKLESYS)
rep('''    long cx = {PKG}.SkillCfg.classXp(slot, {PKG}.SkillCfg.combatXp(role, maxHp));
    {PKG}.SkillXp.gain(pr, slot, cx);
    {PKG}.PartyXp.share(pr, k, s, cx);
''', '''    {PKG}.MobXp.kill(pr, k, s, slot, {PKG}.SkillCfg.combatXp(role, maxHp), r);   // 0.4.14: x the mob level bonus and the level gap (SkyyMobs)
''')

# ---------------------------------------------------------------------------------------------------------------- the Stats page
rep('''  StringBuilder sb = new StringBuilder("Skill tree: ");
  if (dd > 0.00001) sb.append''', '''  StringBuilder sb = new StringBuilder("Bonuses (trees + tools): ");   // 0.4.14: SkyyGear 0.2.2 posts the held tool as source "gear"
  if (dd > 0.00001) sb.append''')
rep('''    if (c > 0.00001) out.add((next ? "+" : "") + pc(c) + " chance to double the drops of " + what[row]);
  }}
''', '''    if (c > 0.00001) out.add((next ? "+" : "") + pc(c) + " chance to double the drops of " + what[row]);
  }}
  if (!next) {{ String gp = {PKG}.GatherPace.statsLine(s, lv); if (gp != null) out.add(gp); }}   // 0.4.14: the gathering pace
''')
rep('''  if (s == {PKG}.SkillDefs.FARMING) return "Earn XP by harvesting fully grown crops - break them or press F on eternal crops and bushes";''',
    '''  if (s == {PKG}.SkillDefs.FARMING) return "Earn XP by harvesting fully grown crops - break them or press F on eternal crops and bushes" + ({PKG}.Sickle.ON ? " - or swing a sickle through them" : "");''')
rep('''  if (s == {PKG}.SkillDefs.ACROBATICS) return "Earn XP by running - jumping - dodging - and surviving falls that hurt (higher falls pay more - safe drops and water pay 0)";''',
    '''  if (s == {PKG}.SkillDefs.ACROBATICS) return "Earn XP by running - jumping - dodging - and surviving falls that hurt (higher falls pay more - safe drops and water pay 0)" + ({PKG}.AcroCfg.ENABLED && {PKG}.AcroCfg.ROLL > 0.0 ? " - crouch as you land to roll: +" + Math.round({PKG}.AcroCfg.ROLL * 100.0) + "%" : "");''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup rows
after('''    ("divinity.healXp.enabled", "Divinity XP from healing", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: Priest heals pay no Divinity XP (kills still do). Levels are kept.", "reload"),
''', '''    # 0.4.14 (Skyy 2026-10-02 "level bonus + gap rule max +250%"): needs SkyyMobs levels; off = 0.4.13's kill XP
    ("combat.levelXp.enabled", "Kill XP by mob level", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: kills pay no mob level bonus or level gap (needs SkyyMobs levels). Levels are kept.", "reload"),
''')
before('''    ("block", "XP by exact block id", "gathering", "table", "", "", "", "text;type;Skill:XP or none", "", "live",
''', '''    # 0.4.14 (Skyy 2026-10-02 tool levels answer (4): "Bigger boost for all 3") - the gathering pace; sickle swings (Tool-Levels-Spec question 3)
    ("gather.boost.skills", "Gathering pace skills", "gathering", "text", "Mining,Foraging,Farming", "", "300", "", "", "live",
     "Skills whose earned XP gets the early boost below (Mining, Foraging, Farming), comma separated.", "reload;check=GatherPace.checkSkills"),
    ("gather.boost.early", "Early gathering XP boost", "gathering", "dec", "3", "0.1", "100", "", "x", "live",
     "Earned XP x this up to the level below (Skyy: x3 to level 10). At least 0.1.", "reload"),
    ("gather.boost.earlyUntil", "Full boost up to level", "gathering", "int", "10", "0", "100", "", "", "live",
     "The early boost holds through this level, then eases off in a straight line.", "reload"),
    ("gather.boost.late", "Later gathering XP boost", "gathering", "dec", "1.5", "0.1", "100", "", "x", "live",
     "Earned XP x this from the level below on (Skyy: x1.5 from level 20). At least 0.1.", "reload"),
    ("gather.boost.lateFrom", "Later boost from level", "gathering", "int", "20", "0", "100", "", "", "live",
     "From this level on the later boost holds. Granted XP (Collections rewards) never gets a boost.", "reload"),
    ("farming.sickle.enabled", "Sickle swings pay Farming XP", "gathering", "bool", "true", "", "", "", "", "live",
     "A crop in its final growth stage that a sickle harvests pays Farming XP + a double-drop roll, once.", "reload"),
    ("farming.sickle.items", "Sickle item ids", "gathering", "text", "Tool_Sickle_", "", "500", "", "", "live,adv",
     "Item id starts that count as sickles, comma separated.", "reload;check=Sickle.checkItems"),
''')
after('''    ("combat.classWeaponOnly", "Only class weapons earn XP", "combat", "bool", "true", "", "", "", "", "live",
     "On: only the class's own weapons earn combat XP. Off: anything SkyyClasses lets the class use.", "reload"),
''', '''    # 0.4.14 kill XP by mob level (SkyyMobs mob:fn:level): x (1 + levelBonus x (level - 1)) x the gap against your class skill
    ("combat.levelBonus", "Kill XP per mob level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Kill XP x (1 + this x (mob level - 1)) with SkyyMobs levels. 0.05 = +5% a level.", "reload"),
    ("combat.gap.free", "Level gap with no change", "combat", "int", "5", "0", "100", "", "", "live",
     "A mob up to this many levels above or below your class skill pays no gap change.", "reload"),
    ("combat.gap.above", "Higher mob: extra XP a level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Each level a mob is past that gap above you adds this (0.05 = +5%).", "reload"),
    ("combat.gap.max", "Higher mob: XP cap", "combat", "dec", "3.5", "1", "100", "", "x", "live",
     "The gap never pays more than this times (3.5 = +250%).", "reload"),
    ("combat.gap.below", "Lower mob: XP lost a level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Each level a mob is past that gap below you takes this away (0.05 = -5%).", "reload"),
    ("combat.gap.min", "Lower mob: least XP", "combat", "dec", "0.1", "0", "1", "", "x", "live",
     "The gap never pays less than this share (0.1 = 10%).", "reload"),
''')
after('''    ("acro.fallMaxXpPerMinute", "Fall XP per minute cap", "acrobatics", "dec", "3000", "0", "1000000000", "", "", "live",
     "All fall XP in any 60 seconds (0 = no fall XP). Its own cap.", "reload"),
''', '''    # 0.4.14 roll landings (Skyy 2026-10-02): the fall's unreduced XP + this share; 0 = 0.4.13 (a full roll paid nothing)
    ("acro.rollBonus", "Extra XP for a rolled landing", "acrobatics", "dec", "0.5", "0", "10", "", "", "live",
     "Crouch to roll as you land: the fall's XP + this share (0.5 = +50%). 0 = rolls pay as before.", "reload"),
''')
rep('''assert len(CFG_ROWS) == 180, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier; 0.4.12: + the 4 class curve "
                              "rows + mana.regen.inCombat + the mana.regen.show action, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10 / 0.4.12''',
    '''assert len(CFG_ROWS) == 195, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier; 0.4.12: + the 4 class curve "
                              "rows + mana.regen.inCombat + the mana.regen.show action; 0.4.14: + the 15 rows of N14_L, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10 / 0.4.12 / 0.4.14
# 0.4.14: every N14_L key is a row once, its default = the default file = the appended block; their categories / places
_r14 = dict((_r[0], _r) for _r in CFG_ROWS)
for _k in N14_KEYS:
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _dp.get(_k) is not None and ("\\n" + _k + "=" + _dp[_k] + "\\n") in ("\\n" + N14_DEFAULTS), _k
    assert _r14[_k][4] == _dp[_k] or _Dec(_r14[_k][4]) == _Dec(_dp[_k]), _k
assert [_r14[_k][2] for _k in N14_KEYS] == ["parts", "combat", "combat", "combat", "combat", "combat", "combat", "acrobatics"] + ["gathering"] * 7
_kk14 = [_r[0] for _r in CFG_ROWS]
assert _kk14[_kk14.index("combat.classWeaponOnly") + 1:_kk14.index("combat.classWeaponOnly") + 7] == N14_KEYS[1:7]
assert _kk14[_kk14.index("acro.fallMaxXpPerMinute") + 1] == "acro.rollBonus" and _kk14[_kk14.index("divinity.healXp.enabled") + 1] == "combat.levelXp.enabled"
assert _kk14[_kk14.index("block") - 7:_kk14.index("block")] == N14_KEYS[8:]''')
rep('''for _nm, _txt in (("DIV", DIV_DEFAULTS), ("DIVS", DIVS_DEFAULTS), ("XBOW", XBOW_DEFAULTS), ("XBOWX", XBOWX_DEFAULTS), ("OVL", OVL_DEFAULTS),
                  ("CLS", CLS_DEFAULTS)):''', '''for _nm, _txt in (("DIV", DIV_DEFAULTS), ("DIVS", DIVS_DEFAULTS), ("XBOW", XBOW_DEFAULTS), ("XBOWX", XBOWX_DEFAULTS), ("OVL", OVL_DEFAULTS),
                  ("CLS", CLS_DEFAULTS), ("CURVE", CURVE_DEFAULTS), ("MREG", MREG_DEFAULTS), ("N14", N14_DEFAULTS)):''')

# ---------------------------------------------------------------------------------------------------------------- DocMig (after HealMig: it reuses its helpers)
DOCMIG = r'''# ---- DocMig (0.4.14, fix (5)): the stale Mana regen comment of an existing xp.properties ("Never above max Mana, never while charging, ..."),
# rewritten ONCE: setup() after HealMig.run, BEFORE SkillCfg.load and CfgPub.start. Only that EXACT comment line (CR kept; a hand-edited one is
# left alone); lines are scanned per logical line (a continued entry's tail is never taken for a comment); the "(SkyySkills 0.4.12)" block
# header stays. HealMig's machinery: the values must stay equal (sameAfter), config-history must hold the old bytes first (mgKit + snapshot
# + mgSaved), the kit's atomicWrite (ISO-8859-1 bytes, line endings kept). The new line is its own marker (no old line = nothing to do); no
# value changes, so there is no change-log line to undo - Server Setup -> History restores the old file.
dmig.addField(CtField.make("public static final String OLD = %s;" % json.dumps(MREG_DOC_OLD), dmig))
dmig.addField(CtField.make("public static final String NEW = %s;" % json.dumps(MREG_DOC_NEW), dmig))
dmig.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.14";', dmig))
dmig.addMethod(CtNewMethod.make(J14(r"""
public static Object[] docUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  java.util.ArrayList out = new java.util.ArrayList();
  int n = 0;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.equals(OLD)) { out.add(NEW + (raw[k].endsWith("\r") ? "\r" : "")); n++; }
      else out.add(raw[k]);
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    for (int q = k; q <= e; q++) out.add(raw[q]);
    k = e + 1;
  }
  if (n == 0) return null;
  StringBuilder sb = new StringBuilder(text.length() + 64);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), Integer.valueOf(n) };
}"""), dmig))
dmig.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = docUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    if (!@PKG@.HealMig.sameAfter(old, data, new String[0])) {
      @PKG@.SkillCfg.warn("xp.properties: the Mana regen comment was NOT updated (the update would change a value; the file is used as it is)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.14 Mana regen comment fix");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties: the Mana regen comment was NOT updated - the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String msg = "xp.properties: the outdated Mana regen comment ('never while charging') now says charging no longer pauses it (SkyySkills 0.4.13+) - " + ((Integer) r[1]).intValue() + " line, no setting changed (the old file is in config-history)";
    @PKG@.SkillCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update the Mana regen comment of xp.properties (the file is used as it is): " + t);
    return "";
  }
}"""), dmig))
'''
after('''for _src in HMIG_JAVA:
    hmig.addMethod(CtNewMethod.make(_src.replace("@PKG@", PKG), hmig))
''', "\n" + DOCMIG)

# ---------------------------------------------------------------------------------------------------------------- the plugin
after("  {PKG}.HealMig.run();   // 0.4.11: untouched heal XP lines 0.2 / 0.25 / 300 -> 1 / 1.25 / 900 (final heal XP), once; History first\n",
      "  {PKG}.DocMig.run();    // 0.4.14: the stale Mana regen comment ('never while charging'), once; History first\n")
after("  getEntityStoreRegistry().registerSystem(new {PKG}.XbowSlotSys());\n",
      '''  getEntityStoreRegistry().registerSystem(new {PKG}.SickleSys());   // 0.4.14: sickle swing harvests (InteractivelyPickupItemEvent)
  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.RollSys());   // 0.4.14: roll landings, BEFORE the engine's FallDamagePlayers
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not register RollSys (roll landings): " + t + " - rolled landings pay as before until the next restart");
  }}
''')
rep('''"; in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "% of (vanilla + Mana Regen boosts)" + "; bridge''',
    '''"; in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "% of (vanilla + Mana Regen boosts)" + "; kill XP by mob level " + {PKG}.MobXp.text() + "; roll landings " + {PKG}.AcroCfg.rollText() + "; gathering pace " + {PKG}.GatherPace.text() + "; sickle swings " + {PKG}.Sickle.text() + "; bridge''')
rep('''          mcost, mmig, mgd, hmig, ccv, mrg, mrfn, mcmd, cmbf):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; 0.4.13: + CombatFn''',
    '''          mcost, mmig, mgd, hmig, ccv, mrg, mrfn, mcmd, cmbf,
          mxp, rsy, gpc, skl, sksy, sktk, dmig):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; 0.4.13: + CombatFn; 0.4.14: + MobXp, RollSys, GatherPace, Sickle, SickleSys, SickleTask, DocMig''')
rep('''Uninstall / downgrade: switch Base Mana and Overall Level off in Server Setup first.''',
    '''Kill XP grows with the SkyyMobs level and the level gap to your class skill (up to +250%; party members use their own class skill); a crouch-roll landing pays +50% Acrobatics XP; Mining, Foraging and Farming XP x3 to level 10, easing to x1.5 by level 20; sickle swings pay Farming XP and roll double drops (Server Setup). Uninstall / downgrade: switch Base Mana and Overall Level off in Server Setup first.''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 + 2 and s.count("registerCommand(") == CMD0, "systems / commands: want exactly SickleSys + RollSys more"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
# methods before callers (javassist compiles each method body when it is added)
assert _ix("public static void readRoll(") < _ix("public static synchronized String load()") and _ix("public static void ensure14(") < _ix("public static synchronized String load()")
assert _ix("public static void read(java.util.Properties p) {\n  ON = @PKG@.SkillCfg.bool(p, \"combat.levelXp.enabled\"") < _ix("public static synchronized String load()")
assert _ix("public static long apply(java.util.UUID u, int slot, long amt)") < _ix("public static void gain4(") < _ix("public static void one({PKG}.FellWatch W, int i)")
assert _ix("public static String statsLine(int slot, int lv)") < _ix("public static java.util.ArrayList lines(")
assert (_ix("public static int award(@PR@ pr") < _ix("public SickleTask(java.util.UUID u, String wn)") < _ix("public static void add(java.util.UUID u, Object e, @WLD@ w)")
        < _ix('event_system(sksy, "SickleSys", IPE') and _ix("public static void breakOpen(") < _ix('event_system(bsy, "BreakSys", BBE')
        and _ix("public static void breakDone(") < _ix("public BreakTask(") and _ix("public static void useOpen(") < _ix('event_system(usy, "HarvestSys", UBP'))
assert _ix("public static void noteRoll(") < _ix("public static int land(") < _ix("public void tick(float dt, int idx, @ACH@ chunk")
# fix round: F1 the StageFinal-only crop map, F2 the fall damage switch (before tick), F3 the party how-to line, F4 the pace floor (before read)
assert s.count('if (!@PKG@.SkillCfg.hasFinalStage(bt) || !"StageFinal".equals(@PKG@.SkillCfg.stateOf(bt))) return;') == 1
assert '@PKG@.SkillCfg.hasFinalStage(bt) && !"StageFinal"' not in s
assert s.count("if (!fallDamageOn(store)) return;") == 1 and _ix("public static boolean fallDamageOn(") < _ix("public void tick(float dt, int idx, @ACH@ chunk")
assert _ix("if (p == null || !(p.getCurrentFallDistance() > 0.0)) return;") < _ix("if (!fallDamageOn(store)) return;") < _ix("land(chunk, idx, store, ms, sp);")
assert s.count(" of the kill XP at their own class skill level") == 1 and s.count(" of your kill XP (in their own class skill)") == 1
assert s.count("public static final double MIN_MULT = 0.1;") == 1 and _ix("public static final double MIN_MULT = 0.1;") < _ix('"gather.boost.early", 3.0), MIN_MULT, 100.0)')
assert s.count('"dec", "3", "0.1", "100", "", "x", "live"') == 1 and s.count('"dec", "1.5", "0.1", "100", "", "x", "live"') == 1
assert (_ix("public static long pay(int slot") < _ix("public static long one2(") < _ix("public static long one(java.util.UUID ku, String kn")
        < _ix("public static void share2(") < _ix("public static void share({PR} kp") < _ix("public static long kill(@PR@ pr") < _ix('ksy.addConstructor('))
assert _ix("public static void retain(java.util.Set online)") < _ix("public static void retainOnline() {{\n  try {{\n    java.util.HashSet online")
assert _ix("public static Object[] docUpdate(") < _ix('@PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.14 Mana regen comment fix");')
assert s.count("{PKG}.MobXp.kill(pr, k, s, slot,") == 1 and "{PKG}.PartyXp.share(pr, k, s, cx);" not in s
assert s.count("{PKG}.GatherPace.apply(") == 2 and s.count("{PKG}.Sickle.breakOpen(") == 1 and s.count("{PKG}.Sickle.useOpen(") == 1
assert s.count("{PKG}.DocMig.run();") == 1 and s.index("{PKG}.HealMig.run();") < s.index("{PKG}.DocMig.run();") < s.index("String rules = {PKG}.SkillCfg.load();")
assert s.count('"Bonuses (trees + tools): "') == 1 and s.count('new StringBuilder("Skill tree: ")') == 1   # the Acrobatics line keeps "Skill tree:"
assert s.count("MREG_L.append(MREG_DOC_NEW)") == 1 and 'MREG_L.append("# Never above max Mana, never while charging' not in s
assert s.count("L.extend(N14_L)") == 1 and s.index("L.extend(MREG_L)") < s.index("L.extend(N14_L)") < s.index('DEFAULTS = "\\n".join(L) + "\\n"')
# the WHOLE diff against 0.4.13: every 0.4.13 line that changed belongs to one of the replaced anchors above
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.13 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.13,", len(_gone), "0.4.13 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
