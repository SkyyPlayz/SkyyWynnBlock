"""Derive SkyySkills/build_skyyskills_0.4.py from 0.3.2 (same style as skills_0_3_2_patch.py: rep(old, new) with asserted anchors,
newline-agnostic; 0.3.2 stays untouched, the CRLF/LF line endings of 0.3.2 are preserved). Edit THIS file, not the generated script.
0.4 = research/Alchemy-Skill-Spec.md (all of it) + the SkyySkills parts of research/Smithing-Smelting-Spec.md + the Cooking ROW
      + the orchestrator decisions of the 0.4 round (they win over both specs):
 - Slots 10 Alchemy, 11 Smithing, 12 Cooking (N = 13, CLASS_END = 10; every class loop bounded to CLASS_END). Slot 3 "Combat" stays
   in storage only (no /skills row; old saves keep it, moveLegacy still moves it to the first class).
 - Alchemy: vanilla Alchemy Bench crafts via CraftRecipeEvent$Post (CraftSys -> CraftTask, 1 unit per Post on the queued path), XP
   table by primary output id, perks (potion duration via EffectControllerComponent.addEffect EXTEND, +0.2 max Mana per level,
   extra potion chance), build-time loop check, anti-exploit rules.
 - Smithing: vanilla Furnace = InventoryChangeEvent MOVE_TO_SELF from the output part of an open Furnace window (SmeltSys ->
   SmeltTask), smithing.* table (bar = 1.0 x the ore's Mining XP, charcoal 0, rule 2.3 for unknown bars), the craft-XP bridge entry
   (skill:fn:craftxp) SkyySacks' Furnace tab calls.
 - Cooking: the row only; XP only through skill:fn:addxp (SkyyCooking owns Cooking). The craft hook IGNORES Cookingbench and
   Campfire recipes (RecipeXp.classify returns null for them - on the bench path AND through craftxp).
 - Bridge: skill:fn:addxp grants Mining, Foraging, Farming, Alchemy, Smithing, Cooking by default (bridge.addxp.skills);
   skill:fn:craftxp returns Long (accepted, 0 = the recipe pays nothing) or null (refused for now - the caller keeps its ledger).
   Optional stats hook skill:stats:<SkillName> (Function) lets another mod add lines to that skill's Stats page (SkyyCooking).
 - Acrobatics falls (Skyy): only a fall that really hurt (Damage survived the whole pipeline: not cancelled, amount >= 1 after
   ApplyDamage, seen in the INSPECT damage group) and that you survived pays; XP per point of unreduced fall damage normalised to
   100 max health (vanilla fall damage is a percent of max health); safe drops, water landings and negated damage pay 0; its own
   per-minute cap outside the 240/min movement cap; the old default acro.* fall lines of an existing xp.properties are migrated.
 - Admin /skills xp <skill> <amount>; /skills page with 8 rows; Stats pages for the new rows.
 - Part 2 (SkyyTrees bridge, research/Skill-Trees-Spec.md 9.3 / 10): skill:fn:xp, the skill:bonus:<uuid> reader (xp.<skill> for
   Mining / Foraging / Farming / Cooking, dd.<skill> in the double-drop roll), skill:on:gather listeners, skill:fn:drops,
   skill:fn:placed, Tree buttons on /skills + the Stats pages (only with SkyyTrees). The section is near the end of this file.
Run:  python tools/skills_0_4_patch.py   then   python SkyySkills/build_skyyskills_0.4.py   (NO --deploy: coordinated deploy)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.3.2.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.3.2"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def rep_block(start, end, new):
    """replace from the unique `start` through the first `end` after it (inclusive)"""
    global s
    assert s.count(start) == 1, "block start count %d: %s" % (s.count(start), start[:100])
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + new + s[b:]


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyySkills 0.3.2 - build script (derived from 0.3.1 by tools/skills_0_3_2_patch.py - edit the patch, not this file;
0.3 was derived from 0.2 by tools/skills_0_3_patch.py)
0.3.2: per-profile storage''', '''"""SkyySkills 0.4 - build script (derived from 0.3.2 by tools/skills_0_4_patch.py - edit the patch, not this file;
0.3.2 was derived from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4 (research/Alchemy-Skill-Spec.md, research/Smithing-Smelting-Spec.md SkyySkills parts, orchestrator decisions of the 0.4 round):
  SLOTS: 10 Alchemy, 11 Smithing, 12 Cooking (N = 13, append-only; CLASS_END = 10 bounds every class loop - slots 10-12 are >= CLASS0
  but are not classes). Slot 3 "Combat" is kept in NAMES (snap() drops unknown keys, so removing it would delete unmigrated legacy
  XP) but has no /skills row any more: the class row shows the class weapon skill by name, or "Class skill - choose a class with
  /class" (+ the old Combat XP line). /skills = 8 rows: Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, class
  skill (ROW_SLOTS); perk rows = mining, foraging, farming, combat (= current class), acrobatics, alchemy, smithing, cooking
  (PERK_SLOT; Perks.rowLevel reads through it). Bridge skill:<uuid> drops the Combat entry and gains Alchemy / Smithing / Cooking.
  ALCHEMY: the vanilla Alchemy Bench fires CraftRecipeEvent$Post on the crafter for every finished unit (queued path: one Post per
  unit but getQuantity() = the whole batch, so 1 unit per Post when TimeSeconds > 0; instant path: quantity). CraftSys (Archetype.empty
  query, like BreakSys) defers to CraftTask on the world thread: dropped when the event was cancelled, the player left, or the profile
  key changed between craft and award; creative pays nothing. XP per craft by primary output id (alchemy.xp.<id>, unlisted
  Alchemybench recipes -> alchemy.tierXp by bench tier, logged once). Perks: potion effects you DRINK last +1%/level (cap +100%) -
  Brew.tick (every tick from AcroSys) extends each fresh application of a whitelisted effect ONCE by base x bonus with
  EffectControllerComponent.addEffect(..., OverlapBehavior.EXTEND, ...) (no restart, no extra pulse); +0.2 max Mana per level
  (skyyskill_mana); 0.2%/level (cap 25%) chance to brew one extra potion (Potion_* / Weapon_Bomb_*, never Potion_Empty*). The build
  fails if an Alchemybench output worth more than 10 XP feeds a recipe that returns one of its own inputs (craft/uncraft loop).
  SMITHING: vanilla Furnace = SmeltSys (InventoryChangeEvent, Player query): a MOVE_TO_SELF move whose other container is the
  combined container of a Furnace ProcessingBenchWindow the player has open, removed from its OUTPUT part (container 2), pays the
  items that landed in the player's inventory (add side, once per container) x SmithCfg.forOutput(id) -> SmeltTask on the world
  thread (pkey re-check; offline -> silent addK). smithing.xp.<id> table (bars = 1.0 x the ore's Mining XP, glass vial 2, charcoal 0),
  unknown Ingredient_Bar_* = the Mining XP of its Furnace recipe's ore x smithing.oreFactor (min 1), else smithing.smeltDefault.
  Salvagebench / Tannery / Campfire windows pay nothing here.
  COOKING: row + Stats page only. Cooking XP arrives ONLY through skill:fn:addxp from SkyyCooking; the craft hook IGNORES Cookingbench
  and Campfire recipes (RecipeXp.classify -> null), so SkyyCooking's crafts are never double counted.
  BRIDGE (plain java.util.function.Function objects, published in setup, removed in shutdown):
    skill:fn:addxp  apply(Object[]{UUID, String skill, Number baseXp, String source [, String expectKey]}) -> Boolean. skill = an exact
                    NAMES/LABELS entry listed in bridge.addxp.skills (default Mining,Foraging,Farming,Alchemy,Smithing,Cooking);
                    TRUE = accepted and queued on the player's world thread (creative / profile re-check there can still drop it),
                    FALSE = refused (unknown or not grantable skill, bad amount, over bridge.maxXpPerCall, per-minute cap, offline,
                    expectKey differs). Never blocks, never does file I/O, any thread.
    skill:fn:craftxp apply(Object[]{UUID, String recipeId, Number crafts, String source [, String expectKey]}) -> Long or null. For crafts
                    the caller completed WITHOUT CraftingManager (SkyySacks /craft + Furnace tab). Skill and XP come from the same
                    RecipeXp.classify table as the vanilla bench (Alchemybench -> Alchemy, Furnace -> Smithing, Cookingbench /
                    Campfire / everything else -> 0). Long = accepted (0 = this recipe pays nothing, OR the call can never be
                    paid because recipe XP x crafts is over bridge.maxXpPerCall - drop it from your ledger either way; so send
                    big ledgers in parts: SkyySacks 0.7.3 sends at most 1,000 units per call); null = refused for now (offline,
                    per-minute cap, profile key differs) - keep the ledger and retry later.
    skill:stats:<SkillName> (OPTIONAL, published by other mods, e.g. SkyyCooking for "Cooking"): Function apply(Object[]{UUID,
                    Integer level, Boolean next}) -> java.util.List of String; up to 5 lines are shown on that skill's Stats page
                    ("Boosts right now" when next=false, "Level L+1 adds" when next=true).
    Caps: bridge.maxXpPerCall = the caller's base XP, checked BEFORE the multiplier and the skill-tree bonus on purpose (a guard
    against a broken caller: a Wisdom node must never turn a valid grant into a permanent refusal); bridge.maxXpPerMinute = the XP
    actually queued (after the multiplier and the tree bonus), per player, all bridge sources together, not reset by a profile
    switch - it is the real bound. The vanilla bench / furnace paths are not capped (every event is a real, paid, non-creative craft).
  ACROBATICS FALLS (Skyy): the further you fall WITHOUT dying the more XP. Only a fall whose damage really applied pays: AcroFallSeenSys
  (DamageEventSystem in the INSPECT group = after ApplyDamage) notes FALL damage that is not cancelled and still >= 1 after
  ApplyDamage's rounding, and not while in fluid/swimming; falls() pays it 0.4 s later if the player is alive, not in creative and
  not in water: XP = unreduced fall damage (Damage.getInitialAmount, before armor and the Acrobatics reduction) x 100 / max health
  (vanilla fall damage = percent of max health, so extra max health changes nothing) x acro.fallDamageXp (10), capped per landing
  (acro.fallXpMax 2000) and per 60 s (acro.fallMaxXpPerMinute 3000, its own ring, outside acro.maxXpPerMinute which now only
  covers running, jumping and dodging). Safe no-damage drops pay 0 (acro.fallXpPerBlock / acro.fallMinBlocks are gone). An existing
  xp.properties without acro.fallMaxXpPerMinute is migrated once: the old default fall lines are rewritten (custom values kept).
  COMMANDS: /skills xp <skill> <amount> (admin test helper, requirePermission skyyskills.admin + no groups; raw XP, no multiplier);
  skill args gain alchemy, smithing, cooking. CONFIG: alchemy.*, perk.alchemy.*, smithing.*, bridge.* blocks appended once to an
  existing xp.properties (AlchCfg / SmithCfg / BridgeCfg.ensureDefaults); /skills reload re-reads them.
  TREES BRIDGE (research/Skill-Trees-Spec.md 9.3 / 10; built for SkyyTrees 0.1, generic): skill:fn:xp apply(Object[]{UUID, skill})
  -> Long (total XP, active profile). skill:bonus:<uuid> is read on every award: xp.<skill> (summed over sources, clamped 0..5, the
  fraction paid by chance) raises the XP of bridge.bonus.xpSkills (default Mining, Foraging, Farming, Cooking) that the player EARNS:
  blocks, F-harvest, vanilla bench / furnace crafts, skill:fn:craftxp. XP another mod GRANTS through skill:fn:addxp gets it only for
  bridge.bonus.addxpSkills (default Cooking = SkyyCooking's per-dish XP, which the Cooking tree's Wisdom node boosts); SkyyCollections'
  Mining / Foraging / Farming tier rewards stay exact (Skill-Trees-Spec 9.3 item 2: Wisdom = gathering XP). Never the admin /skills
  xp. Bridge XP gets the bonus in BridgeXp.offer, so bridge.maxXpPerMinute counts it. dd.<skill> adds to the Mining / Foraging
  / Farming double-drop chance (Perks.chanceU, still capped by perk.doubleDropMax). skill:on:gather (ConcurrentHashMap name ->
  Function, created here with putIfAbsent) is called on the world thread after a gathering block / F-harvest paid XP and rolled its
  double drop: Object[]{PlayerRef, Integer row, BlockType, String world, Boolean harvest, Integer x, Integer y, Integer z}.
  skill:fn:drops apply(Object[]{BlockType, Boolean harvest}) -> List (a fresh roll = Perks.breakDrops / harvestDrops; null = cannot be
  reproduced). skill:fn:placed apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Boolean (PlacedStore.contains; null
  = unknown, tracker off). UI: while tree:fn:level is on the bridge, a "Tree" button on the Mining / Foraging / Farming / Cooking rows
  of /skills and "Skill tree" on their Stats pages run /tree <skill> as the player (the tree page replaces ours); Stats line "Skill
  tree: +X% double drops, +Y% XP". Config: bridge.bonus.enabled, bridge.bonus.xpSkills, bridge.bonus.addxpSkills (bridge block of
  xp.properties).
  NOT in 0.4 (on purpose): Cooking grades / graded dishes / cook:fn:* and the Cooking tree's grade bonuses (SkyyCooking reads
  tree:fn:level / tree:fn:bonus itself; SkyyTrees 0.1 publishes no tree:cook:<uuid> map).
0.3.2: per-profile storage''')
rep('''Run:   python build_skyyskills_0.3.2.py            -> SkyySkills/SkyySkills-0.3.2.jar
       python build_skyyskills_0.3.2.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.4.py            -> SkyySkills/SkyySkills-0.4.jar
       python build_skyyskills_0.4.py --deploy   -> also copies''')
rep('VERSION = "0.3.2"', 'VERSION = "0.4"')

# ================================================================ engine constants + probes (all verified with tools/dev reflect/bcfull)
after('AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"\n', r'''# 0.4 Alchemy / Smithing API (verified with tools/dev reflect.py + bcfull.py against HytaleServer.jar, 2026-09-24)
CRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
CREP= "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"   # '$' form for the class literal, like UBP
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
BRQ = "com.hypixel.hytale.protocol.BenchRequirement"          # public fields id, requiredTierLevel, type
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
AEE = "com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect"
OVB = "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior"
ICE = "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent"
MVTX= "com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction"   # (MVT is MovementStates)
MVY = "com.hypixel.hytale.server.core.inventory.transaction.MoveType"
LTX = "com.hypixel.hytale.server.core.inventory.transaction.ListTransaction"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
SLT = "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction"
CIC = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
PBW = "com.hypixel.hytale.builtin.crafting.window.ProcessingBenchWindow"
BWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow"
WMG = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"
BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
CRPL= "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
BTP = "com.hypixel.hytale.protocol.BenchType"
''')
before('\n# ================= default xp.properties (generated here, every id checked against Assets.zip) =================', r'''
for c, m in ((CRE, "getCraftedRecipe"), (CRE, "getQuantity"), (CRE, "isCancelled"), (CRR, "getTimeSeconds"), (CRR, "getPrimaryOutput"),
             (CRR, "getBenchRequirement"), (CRR, "getId"), (CRR, "getAssetMap"), (CRR, "getInput"), (MQ, "getItemId"), (MQ, "getQuantity"),
             (BRQ, "id"), (BRQ, "requiredTierLevel"), (ECC, "getActiveEffects"), (ECC, "addEffect"), (AEE, "getRemainingDuration"),
             (AEE, "isInfinite"), (EFX, "getDuration"), (EFX, "isDebuff"), (EFX, "getAssetMap"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset"), (OVB, "EXTEND"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"), (ICE, "getTransaction"), (MVTX, "getMoveType"),
             (MVTX, "getOtherContainer"), (MVTX, "getRemoveTransaction"), (MVTX, "getAddTransaction"), (MVTX, "succeeded"),
             (MVY, "MOVE_TO_SELF"), (LTX, "getList"), (IST, "getSlotTransactions"), (SLT, "getSlot"), (SLT, "getSlotBefore"),
             (SLT, "getSlotAfter"), (CIC, "getContainer"), (CIC, "getContainerForSlot"), (CIC, "getContainersSize"),
             (PBW, "getItemContainer"), (BWN, "getBlockType"), (WMG, "getWindows"), (PLA, "getWindowManager"), (BTY, "getBench"),
             (BEN, "getId"), (CRPL, "getBenchRecipes"), (BTP, "Processing"), (DMM, "getInspectDamageGroup"), (IS, "isEmpty")):
    B.probe(pool, c, m)''')

# ================================================================ xp.properties: Acrobatics fall lines (Skyy's fall rule)
rep('''ACRO_L.append("# Falls: landing after a drop of at least acro.fallMinBlocks pays acro.fallXpPerBlock per block from there on; a fall that hurt")
ACRO_L.append("# pays acro.fallDamageXp per point of fall damage (before the Acrobatics reduction) instead, only if you survived it.")
ACRO_L.append("# One landing pays at most acro.fallXpMax. Landing in water pays nothing.")
ACRO_L.append("acro.fallMinBlocks=4")
ACRO_L.append("acro.fallXpPerBlock=2")
ACRO_L.append("acro.fallDamageXp=2")
ACRO_L.append("acro.fallXpMax=50")''', r'''# 0.4 (Skyy): only a fall that really hurt you and that you survived pays - the higher the fall, the more XP. The pre-0.4 lines below
# (ACRO_FALL_OLD) are what 0.2 / 0.3 wrote; AcroCfg.migrateFall rewrites them once in an existing xp.properties.
ACRO_FALL_OLD = ["# Falls: landing after a drop of at least acro.fallMinBlocks pays acro.fallXpPerBlock per block from there on; a fall that hurt",
                 "# pays acro.fallDamageXp per point of fall damage (before the Acrobatics reduction) instead, only if you survived it.",
                 "# One landing pays at most acro.fallXpMax. Landing in water pays nothing."]
ACRO_FALL_NEW = ["# Falls (SkyySkills 0.4): only a fall that really HURT you and that you SURVIVED pays - the higher the fall, the more XP.",
                 "# Safe drops (no fall damage), water landings and falls whose damage was cancelled or fully negated pay nothing.",
                 "# acro.fallDamageXp = XP per point of fall damage BEFORE armor and the Acrobatics reduction, counted as if you had 100 max",
                 "# health (vanilla fall damage is a percent of max health, so extra max health does not change the XP). One landing pays",
                 "# at most acro.fallXpMax; all fall XP together at most acro.fallMaxXpPerMinute in any 60 seconds (0 = no fall XP), a cap",
                 "# of its own outside acro.maxXpPerMinute."]
ACRO_CAP_OLD = "# All Acrobatics XP together pays at most this much in ANY 60 seconds (sliding window; movement is easy to macro)."
ACRO_CAP_NEW = "# Running, jumping and dodging XP together pays at most this much in ANY 60 seconds (sliding window; movement is easy to macro)."
FALL_DMG_DEF, FALL_MAX_DEF, FALL_PM_DEF = "10", "2000", "3000"
ACRO_L.extend(ACRO_FALL_NEW)
ACRO_L.append("acro.fallDamageXp=" + FALL_DMG_DEF)
ACRO_L.append("acro.fallXpMax=" + FALL_MAX_DEF)
ACRO_L.append("acro.fallMaxXpPerMinute=" + FALL_PM_DEF)''')
rep('''ACRO_L.append("# All Acrobatics XP together pays at most this much in ANY 60 seconds (sliding window; movement is easy to macro).")''',
    '''ACRO_L.append(ACRO_CAP_NEW)''')

# ================================================================ xp.properties: Alchemy, Smithing, bridge blocks + build-time checks
after('PERK_LIT = json.dumps(PERK_DEFAULTS)\n', r'''# 0.4: Alchemy + Smithing + cross-mod XP. Each block is also appended once to an existing xp.properties that has none of its keys
# (AlchCfg / SmithCfg / BridgeCfg.ensureDefaults, the AcroCfg pattern); the code defaults below are the same numbers, so a file that
# lacks a key still gets them. Every item id goes through must(), every effect id through must_effect().
ALCH_XP = [("Potion_Health_Lesser", 50), ("Potion_Signature_Lesser", 50), ("Potion_Stamina_Lesser", 50), ("Potion_Antidote", 80),
           ("Weapon_Bomb_Popberry", 10), ("Potion_Morph_Dog", 800), ("Potion_Morph_Frog", 800), ("Potion_Morph_Mouse", 800),
           ("Potion_Morph_Pigeon", 800), ("Potion_Empty_Small", 0), ("Potion_Empty_Large", 0), ("Plant_Seeds_Health1", 60),
           ("Plant_Seeds_Mana1", 60), ("Plant_Seeds_Stamina1", 60), ("Tool_Fertilizer_Crystal", 300), ("Potion_Health_Small", 850),
           ("Potion_Signature_Small", 850), ("Potion_Stamina_Small", 850), ("Potion_Health", 8000), ("Potion_Signature", 8000),
           ("Potion_Stamina", 8000), ("Plant_Seeds_Health2", 300), ("Plant_Seeds_Mana2", 300), ("Plant_Seeds_Stamina2", 300),
           ("Potion_Health_Greater", 18000), ("Potion_Signature_Greater", 18000), ("Potion_Stamina_Greater", 18000),
           ("Plant_Seeds_Health3", 1200), ("Plant_Seeds_Mana3", 1200), ("Plant_Seeds_Stamina3", 1200)]
ALCH_TIER = [50, 850, 8000, 18000, 18000]
ALCH_EXTEND = ["Potion_Health_Regen", "Potion_Health_Regen_Lesser", "Potion_Health_Regen_Small", "Potion_Health_Regen_Large",
               "Potion_Health_Regen_Greater", "Potion_Signature_Regen", "Potion_Signature_Regen_Lesser", "Potion_Signature_Regen_Small",
               "Potion_Signature_Regen_Large", "Potion_Signature_Regen_Greater", "Potion_Morph_Dog", "Potion_Morph_Frog",
               "Potion_Morph_Mouse", "Potion_Morph_Pigeon", "Antidote"]
SMITH_XP = [("Ingredient_Bar_Copper", 5), ("Ingredient_Bar_Iron", 8), ("Ingredient_Bar_Silver", 10), ("Ingredient_Bar_Gold", 12),
            ("Ingredient_Bar_Cobalt", 15), ("Ingredient_Bar_Thorium", 18), ("Ingredient_Bar_Mithril", 25), ("Ingredient_Bar_Adamantite", 30),
            ("Ingredient_Bar_Onyxium", 40), ("Ingredient_Bar_Prisma", 50), ("Potion_Empty", 2), ("Ingredient_Charcoal", 0)]
BRIDGE_SKILLS = "Mining,Foraging,Farming,Alchemy,Smithing,Cooking"
EFFECTS = {}
RECIPES = []   # (source file, primary output id, set of input item ids, set of output item ids, [bench ids])
def _mat_ids(v):
    out = set()
    if isinstance(v, dict): v = [v]
    if isinstance(v, list):
        for x in v:
            if isinstance(x, dict) and isinstance(x.get("ItemId"), str): out.add(x["ItemId"])
    return out
def _benches(r):
    br = r.get("BenchRequirement") or []
    if isinstance(br, dict): br = [br]
    return [b.get("Id") for b in br if isinstance(b, dict)]
with zipfile.ZipFile(ASSETS) as z:
    for n in z.namelist():
        if not n.endswith(".json"): continue
        if n.startswith("Server/Entity/Effects/"):
            try: d = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception: d = {}
            EFFECTS[os.path.basename(n)[:-5]] = d if isinstance(d, dict) else {}
        elif n.startswith("Server/Item/Items/"):
            try: d = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception: continue
            r = d.get("Recipe") if isinstance(d, dict) else None
            if isinstance(r, dict):
                iid = os.path.basename(n)[:-5]
                RECIPES.append((n, iid, _mat_ids(r.get("Input")), {iid} | _mat_ids(r.get("Output")), _benches(r)))
        elif n.startswith("Server/Item/Recipes/"):
            try: d = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception: continue
            if not isinstance(d, dict): continue
            po = _mat_ids(d.get("PrimaryOutput"))
            outs = po | _mat_ids(d.get("Output"))
            prim = sorted(po)[0] if po else (sorted(outs)[0] if outs else None)
            RECIPES.append((n, prim, _mat_ids(d.get("Input")), outs, _benches(d)))
def must_effect(e):
    if e not in EFFECTS: raise SystemExit("unknown effect id in defaults: " + e)
    return e
for _i, _x in ALCH_XP: must(_i)
for _i, _x in SMITH_XP: must(_i)
for _e in ALCH_EXTEND: must_effect(_e)
_alch = [r for r in RECIPES if "Alchemybench" in r[4]]
assert len(_alch) >= 30, "expected the 30 vanilla Alchemybench recipes, found %d" % len(_alch)
_axp = dict(ALCH_XP)
for _r in _alch:
    if _r[1] not in _axp: print("note: Alchemybench recipe %s (%s) is not in alchemy.xp.* - it pays alchemy.tierXp" % (_r[1], _r[0]))
# craft / uncraft loop check (Alchemy spec 6.4): an Alchemybench output worth more than 10 XP must not be the input of any recipe
# that gives back one of the inputs it was made from (the bomb -> salvage loop is why the bomb pays 10). Reruns on every build.
for _r in _alch:
    if _axp.get(_r[1], ALCH_TIER[-1]) <= 10: continue
    for _q in RECIPES:
        if _r[1] in _q[2] and (_q[3] & _r[2]):
            raise SystemExit("craft loop: %s (%d Alchemy XP) -> %s gives back %s" % (_r[1], _axp.get(_r[1], 0), _q[0], sorted(_q[3] & _r[2])))
# base durations for the Stats page pulse text (floor(duration x (1 + bonus) / pulse cooldown))
def _eff(e, k, d):
    v = EFFECTS[must_effect(e)].get(k)
    return float(v) if isinstance(v, (int, float)) else float(d)
SIG_DUR, SIG_CD = _eff("Potion_Signature_Regen_Lesser", "Duration", 30.05), _eff("Potion_Signature_Regen_Lesser", "DamageCalculatorCooldown", 5)
HPR_DUR, HPR_CD = _eff("Potion_Health_Regen_Lesser", "Duration", 5.05), _eff("Potion_Health_Regen_Lesser", "DamageCalculatorCooldown", 5)
MORPH_DUR, ANTI_DUR = _eff("Potion_Morph_Dog", "Duration", 60), _eff("Antidote", "Duration", 120)
ALCH_L = []
ALCH_L.append("# ---------- Alchemy (SkyySkills 0.4) ----------")
ALCH_L.append("# Comments must stay on their own lines.")
ALCH_L.append("alchemy.enabled=true")
ALCH_L.append("# Base XP per finished craft at the vanilla Alchemy Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). Alchemy")
ALCH_L.append("# Bench recipes another Skyy mod crafts itself (bridge skill:fn:craftxp) use the same table. Unlisted Alchemy Bench recipes pay")
ALCH_L.append("# alchemy.tierXp by the recipe's bench tier I..V (the server log names each one once).")
for _i, _x in ALCH_XP:
    ALCH_L.append("alchemy.xp.%s=%d" % (_i, _x))
ALCH_L.append("alchemy.tierXp=" + ",".join(str(x) for x in ALCH_TIER))
ALCH_L.append("# Brewer perks (Alchemy level of your active profile). Potion effects you DRINK last longer: durationPerLevel 0.01 = +1 percent per")
ALCH_L.append("# level (x2 at level 100), capped at durationMax; only the effect ids in perk.alchemy.extend grow (instant heals cannot).")
ALCH_L.append("perk.alchemy.durationPerLevel=0.01")
ALCH_L.append("perk.alchemy.durationMax=1.0")
ALCH_L.append("perk.alchemy.extend=" + ",".join(ALCH_EXTEND))
ALCH_L.append("perk.alchemy.manaPerLevel=0.2")
ALCH_L.append("# Chance per level to brew one extra potion (only outputs starting with an extraPotionOnly part, never an extraPotionNever part).")
ALCH_L.append("perk.alchemy.extraPotionPerLevel=0.002")
ALCH_L.append("perk.alchemy.extraPotionMax=0.25")
ALCH_L.append("perk.alchemy.extraPotionOnly=Potion_,Weapon_Bomb_")
ALCH_L.append("perk.alchemy.extraPotionNever=Potion_Empty")
ALCH_L.append("# perk.smithing.* and perk.cooking.* accept healthPerLevel / staminaPerLevel / manaPerLevel like every other skill (default 0).")
SMITH_L = []
SMITH_L.append("# ---------- Smithing (SkyySkills 0.4) ----------")
SMITH_L.append("# Comments must stay on their own lines.")
SMITH_L.append("# Smithing XP per finished smelted item. Placed vanilla Furnace: paid when YOU take items out of its output slots into your")
SMITH_L.append("# inventory (drag, shift-click or double-click; whoever collects gets the XP). SkyySacks /craft Furnace tab: paid when a unit")
SMITH_L.append("# finishes (bridge skill:fn:craftxp). Reforging / powders will add Smithing XP later (bridge skill:fn:addxp).")
SMITH_L.append("smithing.smelt.enabled=true")
SMITH_L.append("smithing.vanillaFurnace=true")
for _i, _x in SMITH_XP:
    SMITH_L.append("smithing.xp.%s=%d" % (_i, _x))
SMITH_L.append("# an Ingredient_Bar_* not listed: Mining XP of the ore its Furnace recipe uses x this (at least 1)")
SMITH_L.append("smithing.oreFactor=1.0")
SMITH_L.append("# every other Furnace output (smoothed rock, bricks, clay): this much per item (0 = none)")
SMITH_L.append("smithing.smeltDefault=1")
BRIDGE_L = []
BRIDGE_L.append("# ---------- Cross-mod XP (SkyySkills 0.4) ----------")
BRIDGE_L.append("# Comments must stay on their own lines.")
BRIDGE_L.append("# Skills other Skyy mods may grant through skill:fn:addxp (SkyyCollections tier rewards, SkyyCooking, later reforging / powders).")
BRIDGE_L.append("# Exact skill names; Acrobatics, the class skills and the old Combat slot are not in the default list.")
BRIDGE_L.append("bridge.addxp.skills=" + BRIDGE_SKILLS)
BRIDGE_L.append("# One call may ask for at most maxXpPerCall XP: the caller's base XP, before the xp multiplier and skill-tree bonuses (a guard")
BRIDGE_L.append("# against a broken caller). All bridge XP of one player: at most maxXpPerMinute per minute, counted as actually paid (after")
BRIDGE_L.append("# the multiplier and tree bonuses; 0 = no per-minute cap). The vanilla Alchemy Bench and Furnace paths are not capped.")
BRIDGE_L.append("bridge.maxXpPerCall=500000")
BRIDGE_L.append("bridge.maxXpPerMinute=3000000")
for _blk in (ALCH_L, SMITH_L, BRIDGE_L):
    L.append("")
    L.extend(_blk)
ALCH_DEFAULTS = "\n".join(ALCH_L) + "\n"
SMITH_DEFAULTS = "\n".join(SMITH_L) + "\n"
BRIDGE_DEFAULTS = "\n".join(BRIDGE_L) + "\n"
for _t in (ALCH_DEFAULTS, SMITH_DEFAULTS, BRIDGE_DEFAULTS): assert all(ord(ch) < 128 for ch in _t)
ALCH_LIT, SMITH_LIT, BRIDGE_LIT = json.dumps(ALCH_DEFAULTS), json.dumps(SMITH_DEFAULTS), json.dumps(BRIDGE_DEFAULTS)
ALCH_PUTS = "\n".join('  m.put("%s", Long.valueOf(%dL));' % (i, x) for i, x in ALCH_XP)
SMITH_PUTS = "\n".join('  m.put("%s", Long.valueOf(%dL));' % (i, x) for i, x in SMITH_XP)
''')

# ================================================================ new classes
after('scmd = pool.makeClass(PKG + ".StatsCmd", pool.get(APC))\n', r'''# 0.4
alc  = pool.makeClass(PKG + ".AlchCfg")
smc  = pool.makeClass(PKG + ".SmithCfg")
bgc  = pool.makeClass(PKG + ".BridgeCfg")
rxp  = pool.makeClass(PKG + ".RecipeXp")
brew = pool.makeClass(PKG + ".Brew")
bxp  = pool.makeClass(PKG + ".BridgeXp")
ctk  = pool.makeClass(PKG + ".CraftTask")
stk  = pool.makeClass(PKG + ".SmeltTask")
btsk = pool.makeClass(PKG + ".BridgeTask")
csy  = pool.makeClass(PKG + ".CraftSys", pool.get(EES))
sxu  = pool.makeClass(PKG + ".SmeltXp")
ssy  = pool.makeClass(PKG + ".SmeltSys", pool.get(EES))
afss = pool.makeClass(PKG + ".AcroFallSeenSys", pool.get(DEVS))
afn  = pool.makeClass(PKG + ".SkillAddFn")
cfn  = pool.makeClass(PKG + ".SkillCraftFn")
xcmd = pool.makeClass(PKG + ".XpCmd", pool.get(APC))
''')

# ================================================================ SkillDefs: slots 10-12, CLASS_END, rows
rep('''SLOT_NAMES = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + ["Combat." + c[0] for c in CLASS_ROWS]
SLOT_LABELS = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + [c[1] for c in CLASS_ROWS]
SLOT_ICONS = ICONS + [c[2] for c in CLASS_ROWS]
SLOT_COLORS = ["#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff"] + [c[3] for c in CLASS_ROWS]
assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 10''', r'''# 0.4: slots 10-12 (append-only; they are >= CLASS0 but NOT classes - class loops stop at CLASS_END = 10)
EXTRA_ROWS = [("Alchemy", "Alchemy", "Potion_Health", "#7fe0d0"), ("Smithing", "Smithing", "Ingredient_Bar_Iron", "#c0c8d0"),
              ("Cooking", "Cooking", "Food_Pie_Apple", "#ffb070")]
for _c in EXTRA_ROWS: must(_c[2])
SLOT_NAMES = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + ["Combat." + c[0] for c in CLASS_ROWS] + [c[0] for c in EXTRA_ROWS]
SLOT_LABELS = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + [c[1] for c in CLASS_ROWS] + [c[1] for c in EXTRA_ROWS]
SLOT_ICONS = ICONS + [c[2] for c in CLASS_ROWS] + [c[2] for c in EXTRA_ROWS]
SLOT_COLORS = ["#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff"] + [c[3] for c in CLASS_ROWS] + [c[3] for c in EXTRA_ROWS]
assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 13
assert SLOT_NAMES[10:] == ["Alchemy", "Smithing", "Cooking"] and SLOT_NAMES[5 + len(CLASS_ROWS) - 1] == "Combat.Mage"''')
after('defs.addField(CtField.make("public static final int ACROBATICS = 4;", defs))\n', r'''defs.addField(CtField.make("public static final int CLASS_END = %d;" % (5 + len(CLASS_ROWS)), defs))
defs.addField(CtField.make("public static final int ALCHEMY = 10;", defs))
defs.addField(CtField.make("public static final int SMITHING = 11;", defs))
defs.addField(CtField.make("public static final int COOKING = 12;", defs))
# /skills rows (3 = the class row: the current class's weapon skill, or the "choose a class" row)
defs.addField(CtField.make("public static final int[] ROW_SLOTS = new int[] { 0, 1, 2, 10, 11, 12, 4, 3 };", defs))
# perk row -> storage slot (row 3 = the current class, see Perks.rowLevel); PerkCfg.KEYS has the same order
defs.addField(CtField.make("public static final int[] PERK_SLOT = new int[] { 0, 1, 2, 3, 4, 10, 11, 12 };", defs))
defs.addMethod(CtNewMethod.make("""
public static boolean isClass(int s) {
  return s >= CLASS0 && s < CLASS_END;
}""", defs))
# storage slot -> perk row (class slots and the legacy Combat slot -> the combat row 3), -1 = none
defs.addMethod(CtNewMethod.make("""
public static int perkRow(int s) {
  if (s >= 0 && s <= 2) return s;
  if (s == COMBAT || isClass(s)) return COMBAT;
  if (s == ACROBATICS) return ACROBATICS;
  if (s == ALCHEMY) return 5;
  if (s == SMITHING) return 6;
  if (s == COOKING) return 7;
  return -1;
}""", defs))
''')

# ================================================================ AcroCfg: fall keys
rep('''"double FALL_XP = 2.0", "double FALL_DMG_XP = 2.0", "double FALL_MAX = 50.0",''',
    '''"double FALL_DMG_XP = 10.0", "double FALL_MAX = 2000.0", "double FALL_PER_MIN = 3000.0",''')
rep('''  FALL_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpPerBlock", 2.0));
  FALL_DMG_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallDamageXp", 2.0));
  FALL_MAX = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpMax", 50.0));''', '''  FALL_DMG_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallDamageXp", 10.0));
  FALL_MAX = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpMax", 2000.0));
  FALL_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.fallMaxXpPerMinute", 3000.0));''')

# ================================================================ PerkCfg: 8 perk rows (alchemy, smithing, cooking)
rep('''pcfg.addField(CtField.make('public static final String[] KEYS = new String[] { "mining", "foraging", "farming", "combat", "acrobatics" };', pcfg))''',
    '''pcfg.addField(CtField.make('public static final String[] KEYS = new String[] { "mining", "foraging", "farming", "combat", "acrobatics", "alchemy", "smithing", "cooking" };', pcfg))''')
rep('''              "boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.1, 0.25, 0.1, 0.0 }",
              "double[] STA = new double[] { 0.05, 0.0, 0.0, 0.0, 0.0 }", "double[] MANA = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0 }",
              "double[] DD = new double[] { 0.005, 0.005, 0.005, 0.0, 0.0 }", 'String[] ONLY = new String[] { "", "_Trunk", "", "", "" }'):''',
    '''              "boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0 }",
              "double[] STA = new double[] { 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }", "double[] MANA = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0 }",
              "double[] DD = new double[] { 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0 }", 'String[] ONLY = new String[] { "", "_Trunk", "", "", "", "", "", "" }'):''')
rep('''  double[] dhp = new double[] {{ 0.0, 0.1, 0.25, 0.1, 0.0 }};
  double[] dsta = new double[] {{ 0.05, 0.0, 0.0, 0.0, 0.0 }};
  double[] ddd = new double[] {{ 0.005, 0.005, 0.005, 0.0, 0.0 }};
  String[] donly = new String[] {{ "", "_Trunk", "", "", "" }};
  double[] hp = new double[5];
  double[] sta = new double[5];
  double[] mana = new double[5];
  double[] dd = new double[5];
  String[] only = new String[5];
  for (int i = 0; i < 5; i++) {{
    String k = "perk." + KEYS[i] + ".";
    hp[i] = rate(p, k + "healthPerLevel", dhp[i]);
    sta[i] = rate(p, k + "staminaPerLevel", dsta[i]);
    mana[i] = rate(p, k + "manaPerLevel", 0.0);''', '''  double[] dhp = new double[] {{ 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0 }};
  double[] dsta = new double[] {{ 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }};
  double[] dmana = new double[] {{ 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0 }};
  double[] ddd = new double[] {{ 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0 }};
  String[] donly = new String[] {{ "", "_Trunk", "", "", "", "", "", "" }};
  int nk = KEYS.length;
  double[] hp = new double[nk];
  double[] sta = new double[nk];
  double[] mana = new double[nk];
  double[] dd = new double[nk];
  String[] only = new String[nk];
  for (int i = 0; i < nk; i++) {{
    String k = "perk." + KEYS[i] + ".";
    hp[i] = rate(p, k + "healthPerLevel", dhp[i]);
    sta[i] = rate(p, k + "staminaPerLevel", dsta[i]);
    mana[i] = rate(p, k + "manaPerLevel", dmana[i]);''')

# ================================================================ AlchCfg / SmithCfg / BridgeCfg (config part; before SkillCfg.load)
before('# 0.3: the 0.1/0.2 default levels= line (50 levels) -> the 100-level table, in memory AND in the file (custom tables are kept)\n', r'''# ================= AlchCfg (0.4): alchemy.* + perk.alchemy.* keys of xp.properties =================
alc.addField(CtField.make("public static final String DEFAULTS = " + ALCH_LIT + ";", alc))
alc.addField(CtField.make('public static final String DEFAULT_EXTEND = "%s";' % ",".join(ALCH_EXTEND), alc))
for _decl in ("boolean ENABLED = true", "java.util.HashMap XP = new java.util.HashMap()",
              "long[] TIER = new long[] { %s }" % ", ".join("%dL" % x for x in ALCH_TIER),
              "double DUR_PER = 0.01", "double DUR_MAX = 1.0", "String[] EXTEND = new String[0]", "double EXTRA_PER = 0.002",
              "double EXTRA_MAX = 0.25", 'String[] EXTRA_ONLY = new String[] { "Potion_", "Weapon_Bomb_" }',
              'String[] EXTRA_NEVER = new String[] { "Potion_Empty" }', "int[] EXT_IDX = null", "long EXT_NEXT = 0L",
              "boolean EXT_WARNED = false"):
    alc.addField(CtField.make("public static volatile %s;" % _decl, alc))
alc.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap UNLISTED = new java.util.concurrent.ConcurrentHashMap();", alc))
alc.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap defaultsMap() {{
  java.util.HashMap m = new java.util.HashMap();
{ALCH_PUTS}
  return m;
}}""", alc))
# "a, b,,c" -> {"a", "b", "c"}
alc.addMethod(CtNewMethod.make("""
public static String[] split(String v) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (v != null) {
    String[] ps = v.split(",");
    for (int i = 0; i < ps.length; i++) { String t = ps[i].trim(); if (t.length() > 0) l.add(t); }
  }
  return (String[]) l.toArray(new String[0]);
}""", alc))
alc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "alchemy.enabled", true);
  java.util.HashMap m = defaultsMap();
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    String k = String.valueOf(en.nextElement()).trim();
    if (!k.startsWith("alchemy.xp.") || k.length() <= 11) continue;
    try {{
      long v = Long.parseLong(p.getProperty(k).trim());
      m.put(k.substring(11), Long.valueOf(v < 0L ? 0L : v));
    }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("bad line " + k + "=" + p.getProperty(k) + " (want a whole number)"); }}
  }}
  XP = m;
  long[] tier = new long[] {{ {", ".join("%dL" % x for x in ALCH_TIER)} }};
  String tv = p.getProperty("alchemy.tierXp");
  if (tv != null) {{
    String[] ps = tv.split(",");
    for (int i = 0; i < ps.length && i < tier.length; i++) {{
      try {{ long v = Long.parseLong(ps[i].trim()); tier[i] = v < 0L ? 0L : v; }} catch (Throwable t) {{ }}
    }}
  }}
  TIER = tier;
  DUR_PER = {PKG}.PerkCfg.rate(p, "perk.alchemy.durationPerLevel", 0.01);
  DUR_MAX = Math.min(10.0, {PKG}.PerkCfg.rate(p, "perk.alchemy.durationMax", 1.0));
  EXTEND = split(p.getProperty("perk.alchemy.extend", DEFAULT_EXTEND));
  EXT_IDX = null;
  EXT_NEXT = 0L;
  EXT_WARNED = false;
  EXTRA_PER = {PKG}.PerkCfg.rate(p, "perk.alchemy.extraPotionPerLevel", 0.002);
  EXTRA_MAX = Math.min(1.0, {PKG}.PerkCfg.rate(p, "perk.alchemy.extraPotionMax", 0.25));
  EXTRA_ONLY = split(p.getProperty("perk.alchemy.extraPotionOnly", "Potion_,Weapon_Bomb_"));
  EXTRA_NEVER = split(p.getProperty("perk.alchemy.extraPotionNever", "Potion_Empty"));
  UNLISTED.clear();
}}""", alc))
alc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("alchemy.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Alchemy section (alchemy.* + perk.alchemy.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the alchemy.* section to xp.properties: " + t); }}
}}""", alc))
# base XP of one finished Alchemy Bench craft (table by output id, else alchemy.tierXp by bench tier - named once in the log)
alc.addMethod(CtNewMethod.make(f"""
public static long xpFor(String id, int tier) {{
  if (id == null) return 0L;
  Object x = XP.get(id);
  if (x instanceof Long) return ((Long) x).longValue();
  long[] tt = TIER;
  int t = tier < 1 ? 1 : (tier > tt.length ? tt.length : tier);
  long v = tt[t - 1];
  if (UNLISTED.putIfAbsent(id, Boolean.TRUE) == null) {PKG}.SkillCfg.info("alchemy: " + id + " (bench tier " + t + ") is not in alchemy.xp.* - it pays alchemy.tierXp " + v + " per craft; add alchemy.xp." + id + "=<xp> to change that");
  return v;
}}""", alc))
alc.addMethod(CtNewMethod.make("""
public static boolean extraOk(String id) {
  if (id == null) return false;
  String[] nv = EXTRA_NEVER;
  for (int i = 0; i < nv.length; i++) if (id.startsWith(nv[i])) return false;
  String[] on = EXTRA_ONLY;
  if (on.length == 0) return true;
  for (int i = 0; i < on.length; i++) if (id.startsWith(on[i])) return true;
  return false;
}""", alc))
# effect ids of perk.alchemy.extend -> asset indexes (lazy: the asset map is ready once players are in; retried every 10 s while none
# resolves; reset by read())
alc.addMethod(CtNewMethod.make(f"""
public static int[] extIdx() {{
  int[] c = EXT_IDX;
  if (c != null) return c;
  long now = System.currentTimeMillis();
  if (now < EXT_NEXT) return null;
  EXT_NEXT = now + 10000L;
  String[] ids = EXTEND;
  int[] tmp = new int[ids.length];
  int n = 0;
  StringBuilder miss = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {{
    int x = Integer.MIN_VALUE;
    try {{ x = {EFX}.getAssetMap().getIndex(ids[i]); }} catch (Throwable t) {{ }}
    if (x == Integer.MIN_VALUE || x < 0) {{ miss.append(' ').append(ids[i]); continue; }}
    tmp[n] = x;
    n++;
  }}
  int[] r = new int[n];
  for (int i = 0; i < n; i++) r[i] = tmp[i];
  if (miss.length() > 0 && !EXT_WARNED) {{ EXT_WARNED = true; {PKG}.SkillCfg.warn("perk.alchemy.extend: unknown effect id(s)" + miss + " - ignored"); }}
  if (n > 0 || ids.length == 0) EXT_IDX = r;
  return r;
}}""", alc))

# ================= SmithCfg (0.4): smithing.* keys (Smithing-Smelting spec 2.6; forOutput is added after SkillCfg.resolve) =================
smc.addField(CtField.make("public static final String DEFAULTS = " + SMITH_LIT + ";", smc))
for _decl in ("boolean ENABLED = true", "boolean VANILLA = true", "double ORE_FACTOR = 1.0", "long DEFAULT = 1L",
              "java.util.HashMap XP = new java.util.HashMap()"):
    smc.addField(CtField.make("public static volatile %s;" % _decl, smc))
smc.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();", smc))
smc.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap defaultsMap() {{
  java.util.HashMap m = new java.util.HashMap();
{SMITH_PUTS}
  return m;
}}""", smc))
smc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "smithing.smelt.enabled", true);
  VANILLA = {PKG}.SkillCfg.bool(p, "smithing.vanillaFurnace", true);
  double f = {PKG}.SkillCfg.dbl(p, "smithing.oreFactor", 1.0);
  ORE_FACTOR = (Double.isNaN(f) || f < 0.0) ? 0.0 : f;
  long d = {PKG}.SkillCfg.lng(p, "smithing.smeltDefault", 1L);
  DEFAULT = d < 0L ? 0L : d;
  java.util.HashMap m = defaultsMap();
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    String k = String.valueOf(en.nextElement()).trim();
    if (!k.startsWith("smithing.xp.") || k.length() <= 12) continue;
    try {{
      long v = Long.parseLong(p.getProperty(k).trim());
      m.put(k.substring(12), Long.valueOf(v < 0L ? 0L : v));
    }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("bad line " + k + "=" + p.getProperty(k) + " (want a whole number)"); }}
  }}
  XP = m;
  CACHE.clear();
}}""", smc))
smc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("smithing.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Smithing section (smithing.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the smithing.* section to xp.properties: " + t); }}
}}""", smc))

# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
bgc.addField(CtField.make("public static final String DEFAULTS = " + BRIDGE_LIT + ";", bgc))
bgc.addField(CtField.make('public static final String DEFAULT_SKILLS = "%s";' % BRIDGE_SKILLS, bgc))
for _decl in ("boolean[] GRANT = new boolean[0]", 'String GRANT_TEXT = ""', "long PER_CALL = 500000L", "long PER_MIN = 3000000L"):
    bgc.addField(CtField.make("public static volatile %s;" % _decl, bgc))
bgc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  boolean[] g = new boolean[{PKG}.SkillDefs.N];
  StringBuilder sb = new StringBuilder();
  String[] ps = p.getProperty("bridge.addxp.skills", DEFAULT_SKILLS).split(",");
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    int hit = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(t) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(t)) hit = s;
    if (hit < 0 || hit == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.addxp.skills: unknown or not grantable skill '" + t + "' - ignored"); continue; }}
    g[hit] = true;
    if (sb.length() > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[hit]);
  }}
  GRANT = g;
  GRANT_TEXT = sb.toString();
  long c = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerCall", 500000L);
  PER_CALL = c < 1L ? 1L : c;
  long m = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerMinute", 3000000L);
  PER_MIN = m < 0L ? 0L : m;
}}""", bgc))
bgc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("bridge.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the cross-mod XP section (bridge.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the bridge.* section to xp.properties: " + t); }}
}}""", bgc))
''')

# AcroCfg.migrateFall: after SkillCfg.squash exists (it is added right before load)
before('''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''', r'''# 0.4 (Skyy's fall rule): an xp.properties written by 0.2 / 0.3 carries the old fall lines (safe drops paid per block, 2 XP per damage
# point, 50 per landing, falls inside the 240/min cap). Rewritten ONCE (marker: acro.fallMaxXpPerMinute missing while acro.* keys exist):
# the old comments -> the new ones, acro.fallMinBlocks / acro.fallXpPerBlock removed (a custom value leaves a comment line), the DEFAULT
# acro.fallDamageXp=2 / acro.fallXpMax=50 -> the 0.4 defaults (custom values are kept), acro.fallMaxXpPerMinute added after
# acro.fallXpMax. The loaded Properties get the same changes, so this load already uses them.
acfg.addField(CtField.make("public static final String[] FALL_OLD = new String[] { %s };" % ", ".join(json.dumps(x) for x in ACRO_FALL_OLD), acfg))
acfg.addField(CtField.make("public static final String[] FALL_NEW = new String[] { %s };" % ", ".join(json.dumps(x) for x in ACRO_FALL_NEW), acfg))
acfg.addField(CtField.make("public static final String CAP_OLD = %s;" % json.dumps(ACRO_CAP_OLD), acfg))
acfg.addField(CtField.make("public static final String CAP_NEW = %s;" % json.dumps(ACRO_CAP_NEW), acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void migrateFall(java.util.Properties p) {{
  if (p.getProperty("acro.fallMaxXpPerMinute") != null) return;
  boolean any = false;
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("acro.")) any = true;
  }}
  if (!any) return;
  boolean hadPer = p.getProperty("acro.fallXpPerBlock") != null;
  p.remove("acro.fallXpPerBlock");
  p.remove("acro.fallMinBlocks");
  if ("2".equals({PKG}.SkillCfg.squash(p.getProperty("acro.fallDamageXp")))) p.setProperty("acro.fallDamageXp", "{FALL_DMG_DEF}");
  if ("50".equals({PKG}.SkillCfg.squash(p.getProperty("acro.fallXpMax")))) p.setProperty("acro.fallXpMax", "{FALL_MAX_DEF}");
  p.setProperty("acro.fallMaxXpPerMinute", "{FALL_PM_DEF}");
  try {{
    java.util.List lines = java.nio.file.Files.readAllLines({PKG}.SkillCfg.FILE, java.nio.charset.StandardCharsets.UTF_8);
    StringBuilder sb = new StringBuilder();
    boolean wroteNew = false;
    boolean perMin = false;
    for (int i = 0; i < lines.size(); i++) {{
      String ln = (String) lines.get(i);
      String t = ln.trim();
      String q = {PKG}.SkillCfg.squash(t);
      boolean oldComment = false;
      for (int k = 0; k < FALL_OLD.length; k++) if (t.equals(FALL_OLD[k])) oldComment = true;
      if (oldComment) {{
        if (!wroteNew) {{
          for (int k = 0; k < FALL_NEW.length; k++) sb.append(FALL_NEW[k]).append("\\n");
          wroteNew = true;
        }}
        continue;
      }}
      if (q.startsWith("acro.fallMinBlocks=") || q.startsWith("acro.fallXpPerBlock=")) {{
        if (!q.equals("acro.fallMinBlocks=4") && !q.equals("acro.fallXpPerBlock=2")) sb.append("# SkyySkills 0.4 removed: ").append(t).append(" (safe drops pay no Acrobatics XP any more)\\n");
        continue;
      }}
      if (q.equals("acro.fallDamageXp=2")) {{ sb.append("acro.fallDamageXp={FALL_DMG_DEF}\\n"); continue; }}
      if (q.startsWith("acro.fallXpMax=")) {{
        if (q.equals("acro.fallXpMax=50")) sb.append("acro.fallXpMax={FALL_MAX_DEF}\\n"); else sb.append(ln).append("\\n");
        if (!perMin) {{ sb.append("acro.fallMaxXpPerMinute={FALL_PM_DEF}\\n"); perMin = true; }}
        continue;
      }}
      if (t.equals(CAP_OLD)) {{ sb.append(CAP_NEW).append("\\n"); continue; }}
      sb.append(ln).append("\\n");
    }}
    if (!perMin) {{
      sb.append("# SkyySkills 0.4: all fall XP together pays at most this much in any 60 seconds (its own cap, outside acro.maxXpPerMinute)\\n");
      sb.append("acro.fallMaxXpPerMinute={FALL_PM_DEF}\\n");
    }}
    java.nio.file.Path tmp = {PKG}.SkillCfg.FILE.resolveSibling("xp.properties.tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, {PKG}.SkillCfg.FILE, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
    {PKG}.SkillCfg.info("xp.properties: Acrobatics falls moved to the 0.4 rules - only survived falls that hurt pay (acro.fallDamageXp=" + p.getProperty("acro.fallDamageXp") + ", acro.fallXpMax=" + p.getProperty("acro.fallXpMax") + ", acro.fallMaxXpPerMinute=" + p.getProperty("acro.fallMaxXpPerMinute") + ")" + (hadPer ? "; acro.fallXpPerBlock removed" : ""));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not rewrite the Acrobatics fall lines of xp.properties (the 0.4 fall rules apply anyway): " + t); }}
}}""", acfg))
''')

# SkillCfg.load: migrate + append + read the 0.4 blocks
rep('''    upgradeLevels(p);
    {PKG}.AcroCfg.ensureDefaults(p);
    {PKG}.PerkCfg.ensureDefaults(p);
''', '''    upgradeLevels(p);
    {PKG}.AcroCfg.migrateFall(p);
    {PKG}.AcroCfg.ensureDefaults(p);
    {PKG}.PerkCfg.ensureDefaults(p);
    {PKG}.AlchCfg.ensureDefaults(p);
    {PKG}.SmithCfg.ensureDefaults(p);
    {PKG}.BridgeCfg.ensureDefaults(p);
''')
rep('''    {PKG}.AcroCfg.read(p);
    {PKG}.PerkCfg.read(p);
''', '''    {PKG}.AcroCfg.read(p);
    {PKG}.PerkCfg.read(p);
    {PKG}.AlchCfg.read(p);
    {PKG}.SmithCfg.read(p);
    {PKG}.BridgeCfg.read(p);
''')
rep('''    CACHE.clear();
    return ex.size()''', '''    CACHE.clear();
    {PKG}.SmithCfg.CACHE.clear();
    return ex.size()''')
rep('''", perks " + ({PKG}.PerkCfg.ENABLED ? "on" : "off") + ", max level "''',
    '''", perks " + ({PKG}.PerkCfg.ENABLED ? "on" : "off") + ", alchemy " + ({PKG}.AlchCfg.ENABLED ? "on" : "off") + ", smithing " + ({PKG}.SmithCfg.ENABLED ? ({PKG}.SmithCfg.VANILLA ? "on" : "on (Furnace tab only)") : "off") + ", bridge skills " + {PKG}.BridgeCfg.GRANT_TEXT + ", max level "''')

# ================================================================ SmithCfg.forOutput + RecipeXp (after SkillCfg.resolve)
before('# ================= SkillStore: per-player XP, persistence, bridge =================\n', r'''# ================= SmithCfg.forOutput (0.4): Smithing XP per smelted item (Smithing-Smelting spec 2.3) =================
# 1. smithing.xp.<exact id> (0 = none; code defaults include Ingredient_Charcoal=0)  2. Ingredient_Bar_*: the Mining XP of the ore its
# Furnace recipe uses (CraftingPlugin.getBenchRecipes(Processing, "Furnace"), input 0 -> SkillCfg.resolve) x oreFactor, at least 1
# 3. smithing.smeltDefault. Cached per id; cleared by SmithCfg.read and SkillCfg.load (the ore rules may have changed).
smc.addMethod(CtNewMethod.make(f"""
public static long fromOre(String id) {{
  try {{
    java.util.List l = {CRPL}.getBenchRecipes({BTP}.Processing, "Furnace");
    for (int i = 0; l != null && i < l.size(); i++) {{
      Object o = l.get(i);
      if (!(o instanceof {CRR})) continue;
      {CRR} r = ({CRR}) o;
      {MQ} po = r.getPrimaryOutput();
      if (po == null || !id.equals(po.getItemId())) continue;
      {MQ}[] in = r.getInput();
      if (in == null || in.length == 0 || in[0] == null || in[0].getItemId() == null) continue;
      long[] rule = {PKG}.SkillCfg.resolve(in[0].getItemId());
      if (rule != null && rule[0] == (long) {PKG}.SkillDefs.MINING && rule[1] > 0L) return Math.max(1L, Math.round(rule[1] * ORE_FACTOR));
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("smithing: could not look up the Furnace recipe of " + id + ": " + t); }}
  return -1L;
}}""", smc))
smc.addMethod(CtNewMethod.make("""
public static long forOutput(String id) {
  if (id == null) return 0L;
  Object c = CACHE.get(id);
  if (c instanceof Long) return ((Long) c).longValue();
  long v;
  Object x = XP.get(id);
  if (x instanceof Long) v = ((Long) x).longValue();
  else {
    v = -1L;
    if (id.startsWith("Ingredient_Bar_")) v = fromOre(id);
    if (v < 0L) v = DEFAULT;
  }
  CACHE.put(id, Long.valueOf(v));
  return v;
}""", smc))
# ================= RecipeXp (0.4): which skill a finished craft pays and how much (one table for the bench, the furnace tab and the bridge) =====
# -> {slot, base XP per craft} or null. Cookingbench / Campfire recipes -> null (SkyyCooking owns Cooking and pays it through
# skill:fn:addxp; 0.4 decision), Alchemybench -> Alchemy, Furnace -> Smithing (only while smithing.smelt.enabled), anything else null.
# No cache of its own (SmithCfg.CACHE is the only one, so /skills reload takes effect at once).
rxp.addMethod(CtNewMethod.make(f"""
public static long[] classify({CRR} rc) {{
  if (rc == null) return null;
  {BRQ}[] br = rc.getBenchRequirement();
  if (br == null || br.length == 0) return null;
  for (int i = 0; i < br.length; i++) {{
    if (br[i] == null || br[i].id == null) continue;
    if (br[i].id.equalsIgnoreCase("Cookingbench") || br[i].id.equalsIgnoreCase("Campfire")) return null;
  }}
  for (int i = 0; i < br.length; i++) {{
    if (br[i] == null || br[i].id == null) continue;
    String b = br[i].id;
    if (b.equalsIgnoreCase("Alchemybench")) {{
      if (!{PKG}.AlchCfg.ENABLED) return null;
      {MQ} po = rc.getPrimaryOutput();
      if (po == null || po.getItemId() == null) return null;
      long xp = {PKG}.AlchCfg.xpFor(po.getItemId(), br[i].requiredTierLevel);
      if (xp <= 0L) return null;
      return new long[] {{ (long) {PKG}.SkillDefs.ALCHEMY, xp }};
    }}
    if (b.equalsIgnoreCase("Furnace")) {{
      if (!{PKG}.SmithCfg.ENABLED) return null;
      {MQ} po = rc.getPrimaryOutput();
      if (po == null || po.getItemId() == null) return null;
      long per = {PKG}.SmithCfg.forOutput(po.getItemId());
      long xp = per * (long) Math.max(1, po.getQuantity());
      if (xp <= 0L) return null;
      return new long[] {{ (long) {PKG}.SkillDefs.SMITHING, xp }};
    }}
  }}
  return null;
}}""", rxp))
''')

# ================================================================ SkillClass: class loops bounded to CLASS_END, skill args
rep('''  if (slot < {PKG}.SkillDefs.CLASS0 || slot >= {PKG}.SkillDefs.N) return false;''',
    '''  if (!{PKG}.SkillDefs.isClass(slot)) return false;''')
rep('''pr.sendMessage({MSG}.raw("[Skills] Unknown skill. Use mining, foraging, farming, acrobatics, combat (your class skill) or a class skill: archery, swordsmanship, assassination, shaman, sorcery."));''',
    '''pr.sendMessage({MSG}.raw("[Skills] Unknown skill. Use mining, foraging, farming, alchemy, smithing, cooking, acrobatics, combat (your class skill) or a class skill: archery, swordsmanship, assassination, shaman, sorcery."));''')

# ================================================================ SkillStore: bridge string without Combat, legacy move bounded
rep_block('''sto.addMethod(CtNewMethod.make(f"""
public static String levelsOf(java.util.UUID u, long[] d) {{''', '''}}""", sto))''', r'''sto.addMethod(CtNewMethod.make(f"""
public static String levelsOf(java.util.UUID u, long[] d) {{
  int cs = {PKG}.SkillClass.slot(u);
  int[] order = new int[] {{ {PKG}.SkillDefs.MINING, {PKG}.SkillDefs.FORAGING, {PKG}.SkillDefs.FARMING, {PKG}.SkillDefs.ACROBATICS, {PKG}.SkillDefs.ALCHEMY, {PKG}.SkillDefs.SMITHING, {PKG}.SkillDefs.COOKING }};
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < order.length; i++) {{
    if (i > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[order[i]]).append(':').append({PKG}.SkillDefs.levelOf(d[order[i]]));
  }}
  for (int s = {PKG}.SkillDefs.CLASS0; s < {PKG}.SkillDefs.CLASS_END; s++) {{
    if (s != cs && d[s] <= 0L) continue;
    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillDefs.levelOf(d[s]));
  }}
  return sb.toString();
}}""", sto))''')
rep('''  if (slot < {PKG}.SkillDefs.CLASS0 || slot >= n || d[c] <= 0L) return -1L;
  for (int k = {PKG}.SkillDefs.CLASS0; k < n; k++) if (d[k] > 0L) return -1L;''',
    '''  if (!{PKG}.SkillDefs.isClass(slot) || d[c] <= 0L) return -1L;
  for (int k = {PKG}.SkillDefs.CLASS0; k < {PKG}.SkillDefs.CLASS_END; k++) if (d[k] > 0L) return -1L;''')

# ================================================================ Brew part 1 + BridgeXp part 1 (before Perks: Perks.tick / switched and Acro use them)
before('# ================= Perks (0.3): flat stat perks, legacy combat migration, double drops =================\n', r'''# ================= Brew (0.4): Alchemy perks - longer potion effects for the DRINKER, extra potion for the BREWER =================
# BONUS: UUID -> Float duration bonus of the active profile's Alchemy level (set once per second by Perks.tick). SEEN: UUID ->
# Object[2k] last ActiveEntityEffect seen for whitelist effect k, [2k+1] its remaining duration after our last look. Each application
# is extended ONCE by base x bonus (EXTEND adds to remainingDuration without a restart or an extra pulse - bytecode), so drinking again
# can never stack past base x (1 + bonus). Cleared on a profile switch (Perks.switched) and on disconnect (Acro.retainOnline).
brew.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BONUS = new java.util.concurrent.ConcurrentHashMap();", brew))
brew.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();", brew))
brew.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MSGT = new java.util.concurrent.ConcurrentHashMap();", brew))
brew.addField(CtField.make("public static boolean FAILED_ONCE = false;", brew))
brew.addField(CtField.make("public static final double SIG_DUR = %r;" % SIG_DUR, brew))
brew.addField(CtField.make("public static final double SIG_CD = %r;" % SIG_CD, brew))
brew.addField(CtField.make("public static final double HPR_DUR = %r;" % HPR_DUR, brew))
brew.addField(CtField.make("public static final double HPR_CD = %r;" % HPR_CD, brew))
brew.addField(CtField.make("public static final double MORPH_DUR = %r;" % MORPH_DUR, brew))
brew.addField(CtField.make("public static final double ANTI_DUR = %r;" % ANTI_DUR, brew))
brew.addMethod(CtNewMethod.make(f"""
public static double bonusFor(int lvl) {{
  if (!{PKG}.AlchCfg.ENABLED || !{PKG}.PerkCfg.ENABLED || lvl <= 0) return 0.0;
  double v = lvl * {PKG}.AlchCfg.DUR_PER;
  return v > {PKG}.AlchCfg.DUR_MAX ? {PKG}.AlchCfg.DUR_MAX : v;
}}""", brew))
brew.addMethod(CtNewMethod.make(f"""
public static double extraChance(int lvl) {{
  if (!{PKG}.AlchCfg.ENABLED || !{PKG}.PerkCfg.ENABLED || lvl <= 0) return 0.0;
  double v = lvl * {PKG}.AlchCfg.EXTRA_PER;
  return v > {PKG}.AlchCfg.EXTRA_MAX ? {PKG}.AlchCfg.EXTRA_MAX : v;
}}""", brew))
brew.addMethod(CtNewMethod.make("""
public static void setBonus(java.util.UUID u, int lvl) {
  float b = (float) bonusFor(lvl);
  if (b <= 0.0f) { BONUS.remove(u); SEEN.remove(u); return; }
  BONUS.put(u, Float.valueOf(b));
}""", brew))
brew.addMethod(CtNewMethod.make("""
public static void forget(java.util.UUID u) {
  BONUS.remove(u);
  SEEN.remove(u);
  MSGT.remove(u);
}""", brew))
brew.addMethod(CtNewMethod.make("""
public static int pulses(double dur, double cd, double b) {
  if (cd <= 0.0) return 1;
  return (int) Math.floor(dur * (1.0 + b) / cd);
}""", brew))
# "Signature potions 7 pulses instead of 6 - morphs 75s" (+ " - Health regen 2 pulses" from +98%); its own Stats line (length)
brew.addMethod(CtNewMethod.make("""
public static String pulseText(int lvl) {
  double b = bonusFor(lvl);
  String t = "Signature potions " + pulses(SIG_DUR, SIG_CD, b) + " pulses instead of " + pulses(SIG_DUR, SIG_CD, 0.0) + " - morphs " + Math.round(MORPH_DUR * (1.0 + b)) + "s";
  int hp = pulses(HPR_DUR, HPR_CD, b);
  if (hp > pulses(HPR_DUR, HPR_CD, 0.0)) t = t + " - Health regen " + hp + " pulses";
  return t;
}""", brew))
# every tick per player from AcroSys (world thread, before its 1 s gate): extend each fresh application of a whitelisted effect once
brew.addMethod(CtNewMethod.make(f"""
public static void tick(java.util.UUID u, {ST} store, {CB} cb, {REF} ref, float dt) {{
  try {{
    Object bo = BONUS.get(u);
    if (bo == null) return;
    float b = ((Float) bo).floatValue();
    if (b <= 0.0f) return;
    int[] ids = {PKG}.AlchCfg.extIdx();
    if (ids == null || ids.length == 0) return;
    {ECC} ecc = ({ECC}) store.getComponent(ref, {ECC}.getComponentType());
    if (ecc == null) return;
    Object[] seen = (Object[]) SEEN.get(u);
    if (seen == null || seen.length != 2 * ids.length) {{ seen = new Object[2 * ids.length]; SEEN.put(u, seen); }}
    it.unimi.dsi.fastutil.ints.Int2ObjectMap m = ecc.getActiveEffects();
    for (int k = 0; k < ids.length; k++) {{
      Object o = null;
      if (m != null) o = m.get(ids[k]);
      if (!(o instanceof {AEE})) {{ seen[2 * k] = null; seen[2 * k + 1] = null; continue; }}
      {AEE} a = ({AEE}) o;
      if (a.isInfinite()) continue;
      {EFX} fx = ({EFX}) {EFX}.getAssetMap().getAsset(ids[k]);
      if (fx == null || fx.isDebuff()) continue;
      float rem = a.getRemainingDuration();
      boolean fresh = seen[2 * k] != a;
      if (!fresh && seen[2 * k + 1] instanceof Float) {{
        float last = ((Float) seen[2 * k + 1]).floatValue();
        if (rem > last + 0.01f) fresh = true;
        else if (rem < last - dt - 0.25f && Math.abs(rem - fx.getDuration()) < 0.5f) fresh = true;
      }}
      if (fresh) {{
        float extra = fx.getDuration() * b;
        if (extra >= 0.05f && ecc.addEffect(ref, ids[k], fx, extra, {OVB}.EXTEND, cb)) rem = rem + extra;
      }}
      seen[2 * k] = a;
      seen[2 * k + 1] = Float.valueOf(rem);
    }}
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("alchemy potion duration perk failed (logged once): " + t); }}
  }}
}}""", brew))

# ================= BridgeXp part 1 (0.4): per-minute cap of cross-mod XP, grantable skills =================
# WIN: UUID -> long[]{window start ms, XP accepted in it} (after the multiplier). Per physical player, NOT reset by a profile switch
# (a switch must not reset a rate cap). WARN: UUID -> Long last warning ms (one server-log line per player per minute).
bxp.addField(CtField.make("public static final java.util.HashMap WIN = new java.util.HashMap();", bxp))
bxp.addField(CtField.make("public static final java.util.HashMap WARN = new java.util.HashMap();", bxp))
bxp.addMethod(CtNewMethod.make(f"""
public static synchronized void warnLimited(java.util.UUID u, String text) {{
  long now = System.currentTimeMillis();
  Object last = WARN.get(u);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L) return;
  WARN.put(u, Long.valueOf(now));
  {PKG}.SkillCfg.warn("bridge XP for " + u + ": " + text);
}}""", bxp))
bxp.addMethod(CtNewMethod.make(f"""
public static synchronized boolean allow(java.util.UUID u, long amt) {{
  long cap = {PKG}.BridgeCfg.PER_MIN;
  if (cap <= 0L) return true;
  long now = System.currentTimeMillis();
  long[] w = (long[]) WIN.get(u);
  if (w == null || now - w[0] >= 60000L) {{ w = new long[] {{ now, 0L }}; WIN.put(u, w); }}
  if (w[1] + amt > cap) return false;
  w[1] = w[1] + amt;
  return true;
}}""", bxp))
bxp.addMethod(CtNewMethod.make("""
public static synchronized void retain(java.util.Set online) {
  WIN.keySet().retainAll(online);
  WARN.keySet().retainAll(online);
}""", bxp))
# exact NAMES / LABELS entry (no prefix match) that bridge.addxp.skills allows, else -1 (never the legacy Combat slot)
bxp.addMethod(CtNewMethod.make(f"""
public static int grantSlot(String skill) {{
  if (skill == null) return -1;
  String t = skill.trim();
  boolean[] g = {PKG}.BridgeCfg.GRANT;
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    if ({PKG}.SkillDefs.NAMES[i].equalsIgnoreCase(t) || {PKG}.SkillDefs.LABELS[i].equalsIgnoreCase(t)) {{
      if (i == {PKG}.SkillDefs.COMBAT || g == null || i >= g.length || !g[i]) return -1;
      return i;
    }}
  }}
  return -1;
}}""", bxp))
''')

# ================================================================ Perks: 8 perk rows, Brew bonus, switch
rep('''  return {PKG}.SkillStore.level(u, row);
}}""", perk))''', '''  if (row < 0 || row >= {PKG}.SkillDefs.PERK_SLOT.length) return 0;
  return {PKG}.SkillStore.level(u, {PKG}.SkillDefs.PERK_SLOT[row]);
}}""", perk))''')
rep('''  int[] lv = new int[{PKG}.SkillDefs.ROWS];''', '''  int[] lv = new int[{PKG}.PerkCfg.KEYS.length];''')
rep('''  {PKG}.SkillClass.resync(u);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("profile switch: "''', '''  {PKG}.SkillClass.resync(u);
  {PKG}.Brew.forget(u);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("profile switch: "''')
rep('''    int[] lv = levels(u);
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());''', '''    int[] lv = levels(u);
    {PKG}.Brew.setBonus(u, lv[5]);
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());''')

# ================================================================ Brew.extraPotion (after Perks.give)
before('# ================= 0.2 ACROBATICS =================\n', r'''# ================= Brew.extraPotion (0.4): the brewer's extra-potion perk (world thread) =================
# one roll per finished unit (vanilla bench) or per reported craft (bridge); a hit gives the recipe's primary output once more through
# Perks.give (storage > hotbar > backpack, dropped at the feet when full). "Extra potion!" line throttled like "Double drop!".
brew.addMethod(CtNewMethod.make(f"""
public static void extraPotion({PR} pr, {CRR} rc, int units, String world) {{
  try {{
    if (pr == null || rc == null || units <= 0) return;
    java.util.UUID u = pr.getUuid();
    double c = extraChance({PKG}.SkillStore.level(u, {PKG}.SkillDefs.ALCHEMY));
    if (c <= 0.0) return;
    {MQ} po = rc.getPrimaryOutput();
    if (po == null) return;
    String id = po.getItemId();
    if (!{PKG}.AlchCfg.extraOk(id)) return;
    int n = units > 10000 ? 10000 : units;
    int hits = 0;
    java.util.concurrent.ThreadLocalRandom rnd = java.util.concurrent.ThreadLocalRandom.current();
    for (int i = 0; i < n; i++) {{ if (rnd.nextDouble() < c) hits++; }}
    if (hits <= 0) return;
    int q = po.getQuantity() > 0 ? po.getQuantity() : 1;
    java.util.ArrayList l = new java.util.ArrayList();
    l.add(new {IS}(id, q * hits));
    if ({PKG}.SkillStore.bridge().get("profile:busy:" + u.toString()) != null) return;
    String what = {PKG}.Perks.give(pr, l, world);
    if (what == null || {PKG}.SkillStore.quiet(u)) return;
    long now = System.currentTimeMillis();
    long[] tm = (long[]) MSGT.get(u);
    if (tm == null) {{ tm = new long[2]; MSGT.put(u, tm); }}
    tm[0] = tm[0] + (long) hits;
    if (now - tm[1] < {PKG}.SkillCfg.FEEDBACK_MS) return;
    pr.sendMessage({MSG}.raw("Extra potion" + (tm[0] > 1L ? " x" + tm[0] : "") + "!" + what + "  (Alchemy perk)").color("#a0f0e0"));
    tm[0] = 0L;
    tm[1] = now;
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("extra potion perk failed: " + t); }}
}}""", brew))
''')

# ================================================================ Acrobatics: falls (Skyy's rule), own cap ring, retain, Brew tick
rep('''  double[] n = new double[152];''', '''  double[] n = new double[281];''')
rep('''  s[15] = 0.0; s[16] = 0.0; s[17] = 0.0; s[18] = 0.0; s[21] = 0.0;
}""", acro))''', '''  s[15] = 0.0; s[16] = 0.0; s[17] = 0.0; s[18] = 0.0; s[21] = 0.0; s[152] = 0.0;
}""", acro))''')
rep('''    {PKG}.SkillClass.GAVEUP.keySet().retainAll(online);
''', '''    {PKG}.SkillClass.GAVEUP.keySet().retainAll(online);
    {PKG}.Brew.BONUS.keySet().retainAll(online);
    {PKG}.Brew.SEEN.keySet().retainAll(online);
    {PKG}.Brew.MSGT.keySet().retainAll(online);
    {PKG}.BridgeXp.retain(online);
''')
rep('''#  23 pending dodge boost ms (the push is sent 100 ms after the Dodge effect appears so it lands AFTER the dodge's own ApplyForce "Set"''',
    '''#  (0.4: 16 = the noted fall damage normalised to 100 max health; 18/19 landing bookkeeping only - safe drops pay nothing; 152 pending
#  fall XP; 153-216 fall XP paid per wall-clock second (ring, own cap acro.fallMaxXpPerMinute), 217-280 the second each slot holds)
#  23 pending dodge boost ms (the push is sent 100 ms after the Dodge effect appears so it lands AFTER the dodge's own ApplyForce "Set"''')
before('# the ONE anti-exploit movement-state set (review fix: move() AND dodge() use it - the 0.2 draft only checked it in move())\n', r'''# 0.4: in water / swimming (no fall XP there - the engine applies no fall damage in fluid either)
acro.addMethod(CtNewMethod.make(f"""
public static boolean inWater({ST} store, {REF} ref) {{
  try {{
    {MSC} msc = ({MSC}) store.getComponent(ref, {MSC}.getComponentType());
    if (msc == null) return false;
    {MVT} ms = msc.getMovementStates();
    return ms != null && (ms.inFluid || ms.swimming);
  }} catch (Throwable t) {{ return false; }}
}}""", acro))
''')
rep_block('''acro.addMethod(CtNewMethod.make(f"""
public static void falls(''', '''}}""", acro))''', r'''acro.addMethod(CtNewMethod.make(f"""
public static void falls(double[] s, {ST} store, {REF} ref, long now, boolean creative) {{
  double t = (double) now;
  if (s[15] > 0.0 && s[17] < 0.5 && t - s[15] >= 400.0) {{
    s[17] = 1.0;
    if (!creative && alive(store, ref) && !inWater(store, ref)) {{
      double x = s[16] * {PKG}.AcroCfg.FALL_DMG_XP;
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;
      if (x > 0.0) s[152] = s[152] + x;
    }}
    s[15] = 0.0;
  }}
  if (s[18] > 0.0 && t - s[18] >= 700.0) s[18] = 0.0;
}}""", acro))''')
# the old falls() comment described the safe-drop payout
rep('''# pay landings: a FALL damage event near the landing pays by damage (if alive), otherwise the drop pays per block.''',
    '''# 0.4 pay landings: ONLY a FALL damage that really applied (noted by AcroFallSeenSys in the Inspect damage group) pays, by its unreduced
# amount normalised to 100 max health, 0.4 s later if the player is alive and not in water; safe drops (no damage) pay nothing.
# (pre-0.4: a FALL damage event near the landing paid by damage (if alive), otherwise the drop paid per block.)''')
before('# once per second: pay whole XP (sliding per-minute cap, global multiplier), throttled chat line\n', r'''# 0.4: the fall XP ring (153-216 amounts, 217-280 seconds) - same sliding 61-second rule as the movement ring, own cap
acro.addMethod(CtNewMethod.make("""
public static double ringSum(double[] s, long sec, int a, int b) {
  double sum = 0.0;
  double lo = (double) (sec - 60L);
  double hi = (double) sec;
  for (int k = 0; k < 64; k++) {
    double at = s[b + k];
    if (at >= lo && at <= hi) sum = sum + s[a + k];
  }
  return sum;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static void ringAdd(double[] s, long sec, double amt, int a, int b) {
  int k = (int) (sec % 64L);
  if (s[b + k] != (double) sec) { s[b + k] = (double) sec; s[a + k] = 0.0; }
  s[a + k] = s[a + k] + amt;
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double takeFall(double[] s, long now, double whole) {{
  long sec = now / 1000L;
  double room = {PKG}.AcroCfg.FALL_PER_MIN - ringSum(s, sec, 153, 217);
  if (whole > room) whole = Math.floor(room);
  if (whole < 1.0) return 0.0;
  ringAdd(s, sec, whole, 153, 217);
  return whole;
}}""", acro))
''')
rep('''  if (s[21] >= 1.0 && t - s[22] >= (double) {PKG}.AcroCfg.FEEDBACK_MS) {{
''', '''  double fw = Math.floor(s[152]);
  if (fw >= 1.0) {{
    s[152] = s[152] - fw;
    fw = takeFall(s, now, fw);
    if (fw >= 1.0) {{
      long famt = {PKG}.SkillCfg.scaled((long) fw);
      if (famt > 0L) {PKG}.SkillXp.gain2(pr, {PKG}.SkillDefs.ACROBATICS, famt, true);
    }}
  }}
  if (s[21] >= 1.0 && t - s[22] >= (double) {PKG}.AcroCfg.FEEDBACK_MS) {{
''')
rep('''      {PKG}.Acro.falls(s, store, ref, now, creative);
    }}
    s[14] = s[14] + (double) dt;
''', '''      {PKG}.Acro.falls(s, store, ref, now, creative);
    }}
    {PKG}.Brew.tick(u, store, cb, ref, dt);
    s[14] = s[14] + (double) dt;
''')
# fall XP is noted AFTER ApplyDamage now (AcroFallSeenSys), not in the Filter group
rep('''    {PKG}.Acro.noteFall(u, d.getInitialAmount());
''', '')
before('# ================= CombatDmgSys (0.3): combat perk = more damage with your class weapons =================\n', r'''# AcroFallSeenSys (0.4): DamageEventSystem in the INSPECT group (after ApplyDamage - vanilla DamageSystems$ApplyParticles uses the same
# group). ApplyDamage rounds the amount, subtracts it and cancels when the entity is already dead, so a FALL Damage that reaches this
# group uncancelled with amount >= 1 was really applied (not negated by armor / our reduction / another mod). Noted as the unreduced
# amount (getInitialAmount, before the Filter group) normalised to 100 max health; falls() pays it 0.4 s later if still alive.
afss.addConstructor(CtNewConstructor.make("public AcroFallSeenSys() { super(); }", afss))
afss.addField(CtField.make("public static boolean FAILED_ONCE = false;", afss))
afss.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", afss))
afss.addMethod(CtNewMethod.make(f"""
public {SYG} getGroup() {{
  return {DMM}.get().getInspectDamageGroup();
}}""", afss))
afss.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    if (!(ev instanceof {DMG})) return;
    {DMG} d = ({DMG}) ev;
    if (d.isCancelled()) return;
    if (!{PKG}.Acro.isFall(d.getCause())) return;
    if (d.getAmount() < 0.5f) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    if ({PKG}.Acro.inWater(st, r)) return;
    float mx = 100.0f;
    {ESM} m = ({ESM}) st.getComponent(r, {ESM}.getComponentType());
    if (m != null) {{
      {ESV} hv = m.get({DST}.getHealth());
      if (hv != null && hv.getMax() > 0.0f) mx = hv.getMax();
    }}
    float init = d.getInitialAmount();
    if (init <= 0.0f) return;
    {PKG}.Acro.noteFall(pr.getUuid(), init * 100.0f / mx);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("acrobatics fall XP handler failed (logged once): " + t); }}
  }}
}}""", afss))

''')

# ================================================================ CraftTask + SmeltTask (world thread; before the ECS systems)
before('# ================= ECS systems =================\n', r'''# ================= CraftTask (0.4): vanilla Alchemy Bench award, after every other system saw the Post event =================
ctk.addInterface(pool.get("java.lang.Runnable"))
ctk.addField(CtField.make(f"public {CRE} ev;", ctk))
ctk.addField(CtField.make("public java.util.UUID u;", ctk))
ctk.addField(CtField.make("public String world;", ctk))
ctk.addField(CtField.make(f"public {CRR} rc;", ctk))
ctk.addField(CtField.make("public long[] rule;", ctk))
ctk.addField(CtField.make("public int units;", ctk))
ctk.addField(CtField.make("public String key;", ctk))
ctk.addConstructor(CtNewConstructor.make(f"""
public CraftTask({CRE} ev, java.util.UUID u, String world, {CRR} rc, long[] rule, int units, String key) {{
  this.ev = ev; this.u = u; this.world = world; this.rc = rc; this.rule = rule; this.units = units; this.key = key;
}}""", ctk))
ctk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.ev.isCancelled()) return;
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (!this.key.equals({PKG}.SkillStore.pkey(this.u))) return;
    long amt = {PKG}.SkillCfg.scaled(this.rule[1] * (long) this.units);
    if (amt > 0L) {PKG}.SkillXp.gain(pr, (int) this.rule[0], amt);
    if (this.rule[0] == (long) {PKG}.SkillDefs.ALCHEMY) {PKG}.Brew.extraPotion(pr, this.rc, this.units, this.world);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("craft award failed: " + t); }}
}}""", ctk))
# ================= SmeltTask (0.4): vanilla Furnace award (world thread); offline -> silent write, owed coins paid on the next gain =====
stk.addInterface(pool.get("java.lang.Runnable"))
stk.addField(CtField.make("public java.util.UUID u;", stk))
stk.addField(CtField.make("public int slot;", stk))
stk.addField(CtField.make("public long amt;", stk))
stk.addField(CtField.make("public String key;", stk))
stk.addConstructor(CtNewConstructor.make("""
public SmeltTask(java.util.UUID u, int slot, long amt, String key) {
  this.u = u; this.slot = slot; this.amt = amt; this.key = key;
}""", stk))
stk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.amt <= 0L) return;
    if (!this.key.equals({PKG}.SkillStore.pkey(this.u))) return;
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr != null && pr.isValid()) {PKG}.SkillXp.gain(pr, this.slot, this.amt);
    else {PKG}.SkillStore.addK(this.key, this.u, null, this.slot, this.amt);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("smelt award failed: " + t); }}
}}""", stk))
# ================= BridgeTask (0.4): cross-mod XP award on the player's world thread =================
btsk.addInterface(pool.get("java.lang.Runnable"))
btsk.addField(CtField.make("public java.util.UUID u;", btsk))
btsk.addField(CtField.make("public int slot;", btsk))
btsk.addField(CtField.make("public long amt;", btsk))
btsk.addField(CtField.make("public String key;", btsk))
btsk.addField(CtField.make("public String source;", btsk))
btsk.addField(CtField.make(f"public {CRR} rc;", btsk))
btsk.addField(CtField.make("public int units;", btsk))
btsk.addConstructor(CtNewConstructor.make(f"""
public BridgeTask(java.util.UUID u, int slot, long amt, String key, String source, {CRR} rc, int units) {{
  this.u = u; this.slot = slot; this.amt = amt; this.key = key; this.source = source; this.rc = rc; this.units = units;
}}""", btsk))
btsk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (!this.key.equals({PKG}.SkillStore.pkey(this.u))) return;
    String wn = null;
    {REF} r = pr.getReference();
    if (r != null && r.isValid()) {{
      {ST} st = r.getStore();
      if ({PKG}.SkillXp.creative(st, r)) return;
      Object ext = st.getExternalData();
      if (ext instanceof {EST}) {{
        {WLD} w = (({EST}) ext).getWorld();
        if (w != null) wn = w.getName();
      }}
    }}
    {PKG}.SkillXp.gain(pr, this.slot, this.amt);
    if (this.rc != null && this.slot == {PKG}.SkillDefs.ALCHEMY && wn != null) {PKG}.Brew.extraPotion(pr, this.rc, this.units, wn);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("bridge XP award (" + this.source + ") failed: " + t); }}
}}""", btsk))
# BridgeXp.offer (0.4): >= 0 = accepted (scaled XP queued; 0 = nothing to pay), -1 = refused for now (offline, profile key differs,
# per-minute cap), -2 = refused for good (bad slot, over bridge.maxXpPerCall = the caller's base XP, before multiplier and tree bonus).
# Any thread; no I/O; never blocks.
bxp.addMethod(CtNewMethod.make(f"""
public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units) {{
  if (u == null || slot < 0 || slot >= {PKG}.SkillDefs.N || slot == {PKG}.SkillDefs.COMBAT) return -2L;
  if (base <= 0L) return 0L;
  if (base > {PKG}.BridgeCfg.PER_CALL) {{ warnLimited(u, "refused " + base + " XP from " + source + " (over bridge.maxXpPerCall " + {PKG}.BridgeCfg.PER_CALL + ")"); return -2L; }}
  {PR} pr = {UNI}.get().getPlayer(u);
  if (pr == null || !pr.isValid()) return -1L;
  String k = {PKG}.SkillStore.pkey(u);
  if (expect != null && expect.length() > 0 && !expect.equals(k)) return -1L;
  {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
  if (w == null) return -1L;
  long amt = {PKG}.SkillCfg.scaled(base);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt)) {{ warnLimited(u, "bridge.maxXpPerMinute " + {PKG}.BridgeCfg.PER_MIN + " reached - refused " + amt + " XP from " + source); return -1L; }}
  w.execute(new {PKG}.BridgeTask(u, slot, amt, k, source == null ? "?" : source, rc, units));
  return amt;
}}""", bxp))
''')

# ================================================================ CraftSys, SmeltXp, SmeltSys, the two bridge Functions (after the ECS helper)
before('# ================= leaderboard =================\n', r'''# ================= CraftSys (0.4): CraftRecipeEvent$Post = one finished craft unit at a vanilla crafting bench (Alchemy spec 3.1) ======
# Queued path (TimeSeconds > 0): one Post per unit but getQuantity() = the whole batch -> count 1. Instant path: quantity.
# RecipeXp.classify ignores Cookingbench / Campfire recipes (SkyyCooking owns them) and everything that is not Alchemybench / Furnace.
event_system(csy, "CraftSys", CREP, f"""
    {CRE} e = ({CRE}) ev;
    if (e.isCancelled()) return;
    {CRR} rc = e.getCraftedRecipe();
    if (rc == null) return;
    long[] rule = {PKG}.RecipeXp.classify(rc);
    if (rule == null) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null || {PKG}.SkillXp.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    int units = rc.getTimeSeconds() > 0.0f ? 1 : Math.max(1, e.getQuantity());
    if (units > 10000) units = 10000;
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.CraftTask(e, u, w.getName(), rc, rule, units, {PKG}.SkillStore.pkey(u)));""")

# ================= SmeltXp (0.4): helpers for the vanilla Furnace hook (Smithing-Smelting spec 3.3) =================
# MOVE_TO_SELF moves whose source is a combined container (a bench window); ListTransaction recursed
sxu.addMethod(CtNewMethod.make(f"""
public static void moves(Object tx, java.util.ArrayList out) {{
  if (tx instanceof {LTX}) {{
    java.util.List l = (({LTX}) tx).getList();
    for (int i = 0; l != null && i < l.size(); i++) moves(l.get(i), out);
    return;
  }}
  if (!(tx instanceof {MVTX})) return;
  {MVTX} mt = ({MVTX}) tx;
  if (!mt.succeeded() || mt.getMoveType() != {MVY}.MOVE_TO_SELF) return;
  if (!(mt.getOtherContainer() instanceof {CIC})) return;
  out.add(mt);
}}""", sxu))
sxu.addMethod(CtNewMethod.make(f"""
public static int qty({IS} s, String id) {{
  if (s == null || s.isEmpty() || id == null || !id.equals(s.getItemId())) return 0;
  return s.getQuantity();
}}""", sxu))
# items of `id` that landed in THIS container (a move split over hotbar + storage arrives once per container, each with the full
# remove transaction - so only the add side counts)
sxu.addMethod(CtNewMethod.make(f"""
public static int added(Object at, String id) {{
  if (at == null) return 0;
  if (at instanceof {LTX}) {{
    int n = 0;
    java.util.List l = (({LTX}) at).getList();
    for (int i = 0; l != null && i < l.size(); i++) n += added(l.get(i), id);
    return n;
  }}
  if (at instanceof {IST}) {{
    int n = 0;
    java.util.List l = (({IST}) at).getSlotTransactions();
    for (int i = 0; l != null && i < l.size(); i++) n += added(l.get(i), id);
    return n;
  }}
  if (at instanceof {SLT}) {{
    {SLT} s = ({SLT}) at;
    int d = qty(s.getSlotAfter(), id) - qty(s.getSlotBefore(), id);
    return d > 0 ? d : 0;
  }}
  return 0;
}}""", sxu))
# bench id of the player's open processing window whose container is `src`, else null
sxu.addMethod(CtNewMethod.make(f"""
public static String benchOf(java.util.List wins, Object src) {{
  for (int i = 0; wins != null && i < wins.size(); i++) {{
    Object w = wins.get(i);
    if (!(w instanceof {PBW})) continue;
    Object ic = (({PBW}) w).getItemContainer();
    if (ic != src) continue;
    {BTY} bt = (({BWN}) w).getBlockType();
    if (bt == null) return null;
    {BEN} b = bt.getBench();
    if (b == null) return null;
    return b.getId();
  }}
  return null;
}}""", sxu))
# ================= SmeltSys (0.4): InventoryChangeEvent on the player (vanilla ObjectiveInventoryChangeSystem pattern, Player query) =====
ssy.addConstructor(CtNewConstructor.make(f"public SmeltSys() {{ super({ICE}.class); }}", ssy))
ssy.addField(CtField.make("public static boolean FAILED_ONCE = false;", ssy))
ssy.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", ssy))
ssy.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {ICE} e = ({ICE}) ev;
    Object tx = e.getTransaction();
    if (!(tx instanceof {MVTX}) && !(tx instanceof {LTX})) return;
    if (!{PKG}.SmithCfg.ENABLED || !{PKG}.SmithCfg.VANILLA) return;
    java.util.ArrayList mv = new java.util.ArrayList();
    {PKG}.SmeltXp.moves(tx, mv);
    if (mv.isEmpty()) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (pr == null || p == null || p.getWindowManager() == null) return;
    if ({PKG}.SkillXp.creative(st, r)) return;
    java.util.List wins = p.getWindowManager().getWindows();
    long smith = 0L;
    for (int m = 0; m < mv.size(); m++) {{
      {MVTX} mt = ({MVTX}) mv.get(m);
      {CIC} src = ({CIC}) mt.getOtherContainer();
      String bench = {PKG}.SmeltXp.benchOf(wins, src);
      if (bench == null || !"Furnace".equalsIgnoreCase(bench) || src.getContainersSize() < 3) continue;
      {SLT} rt = mt.getRemoveTransaction();
      if (rt == null || src.getContainerForSlot(rt.getSlot()) != src.getContainer(2)) continue;
      {IS} before = rt.getSlotBefore();
      if (before == null || before.isEmpty()) continue;
      String id = before.getItemId();
      int got = {PKG}.SmeltXp.added(mt.getAddTransaction(), id);
      if (got <= 0) continue;
      long per = {PKG}.SmithCfg.forOutput(id);
      if (per > 0L) smith = smith + per * (long) got;
    }}
    if (smith <= 0L) return;
    if (smith > 1000000L) smith = 1000000L;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.SmeltTask(u, {PKG}.SkillDefs.SMITHING, {PKG}.SkillCfg.scaled(smith), {PKG}.SkillStore.pkey(u)));
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("vanilla furnace Smithing hook failed (logged once): " + t); }}
  }}
}}""", ssy))

# ================= skill:fn:addxp (0.4): apply(Object[]{UUID, String skill, Number baseXp, String source [, String expectKey]}) -> Boolean =====
afn.addInterface(pool.get("java.util.function.Function"))
afn.addConstructor(CtNewConstructor.make("public SkillAddFn() { }", afn))
afn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[2] instanceof Number)) return Boolean.FALSE;
    int slot = {PKG}.BridgeXp.grantSlot(String.valueOf(a[1]));
    if (slot < 0) return Boolean.FALSE;
    long base = ((Number) a[2]).longValue();
    if (base <= 0L) return Boolean.FALSE;
    String src = a.length > 3 && a[3] != null ? String.valueOf(a[3]) : "?";
    String expect = a.length > 4 && a[4] instanceof String ? (String) a[4] : null;
    return {PKG}.BridgeXp.offer((java.util.UUID) a[0], slot, base, src, expect, null, 0) >= 0L ? Boolean.TRUE : Boolean.FALSE;
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", afn))
# ================= skill:fn:craftxp (0.4): apply(Object[]{UUID, String recipeId, Number crafts, String source [, String expectKey]}) -> Long | null
cfn.addInterface(pool.get("java.util.function.Function"))
cfn.addConstructor(CtNewConstructor.make("public SkillCraftFn() { }", cfn))
cfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return Long.valueOf(0L);
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || a[1] == null || !(a[2] instanceof Number)) return Long.valueOf(0L);
    {CRR} rc = ({CRR}) {CRR}.getAssetMap().getAsset(String.valueOf(a[1]));
    if (rc == null) return Long.valueOf(0L);
    long[] rule = {PKG}.RecipeXp.classify(rc);
    if (rule == null) return Long.valueOf(0L);
    int crafts = ((Number) a[2]).intValue();
    if (crafts < 1) crafts = 1;
    if (crafts > 10000) crafts = 10000;
    String src = a.length > 3 && a[3] != null ? String.valueOf(a[3]) : "?";
    String expect = a.length > 4 && a[4] instanceof String ? (String) a[4] : null;
    int slot = (int) rule[0];
    long got = {PKG}.BridgeXp.offer((java.util.UUID) a[0], slot, rule[1] * (long) crafts, src, expect, slot == {PKG}.SkillDefs.ALCHEMY ? rc : null, crafts);
    if (got == -1L) return null;
    return Long.valueOf(got < 0L ? 0L : got);
  }} catch (Throwable t) {{ return Long.valueOf(0L); }}
}}""", cfn))

''')

# ================================================================ /skills page: 8 rows (ROW_SLOTS), no Combat row
rep_block('''page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{''', '''}}""", page))''', r'''page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  String bs = "Style: TextButtonStyle(Default: (Background: #27463a, LabelStyle: (FontSize: 12, TextColor: #dcffe8, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3b6b54, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #172a22, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySkills {{ Anchor: (Width: 640, Height: 624); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySkills", "Group {{ Anchor: (Height: 2); Background: #9fe0a0; }}");
  if (this.view < 0 || this.view >= {PKG}.SkillDefs.N) {{
    int cs = {PKG}.SkillClass.slot(u);
    int[] rows = {PKG}.SkillDefs.ROW_SLOTS;
    int sum = 0;
    int shown = 0;
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      if (sl == {PKG}.SkillDefs.COMBAT) {{
        if (cs < 0) continue;
        sl = cs;
      }}
      sum += {PKG}.SkillDefs.levelOf(d[sl]);
      shown++;
    }}
    long avg10 = shown > 0 ? Math.round(sum * 10.0 / shown) : 0L;
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\"Skills\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #e6fff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 18); Text: \\"" + safe("Skill average " + (avg10 / 10L) + "." + (avg10 % 10L) + " - every level up pays coins") + "\\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 6); Text: \\"\\"; }}");
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      boolean classRow = sl == {PKG}.SkillDefs.COMBAT;
      if (classRow && cs >= 0) sl = cs;
      long total = d[sl];
      int lv = {PKG}.SkillDefs.levelOf(total);
      long cur = {PKG}.SkillDefs.intoLevel(total);
      long need = {PKG}.SkillDefs.needFor(total);
      int fill = need > 0L ? (int) ({BARW}L * cur / need) : {BARW};
      if (fill < 0) fill = 0;
      if (fill > {BARW}) fill = {BARW};
      String prog = need > 0L ? ({PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1)) : ("MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP");
      String col = {PKG}.SkillDefs.COLORS[sl];
      String title = {PKG}.SkillDefs.LABELS[sl] + "  " + lv;
      if (classRow) {{
        if (cs >= 0) title = {PKG}.SkillClass.skillName(u, cs) + "  " + lv;
        else {{
          title = "Class skill - choose a class with /class";
          prog = total > 0L ? "Old Combat XP (level " + lv + ") moves to the first class you choose" : "Your combat skill is your class skill";
          fill = 0;
        }}
      }}
      boolean acroRow = sl == {PKG}.SkillDefs.ACROBATICS;
      int rh = acroRow ? 72 : 58;
      b.appendInline("#SkyySkills", "Group #SkyySkRow" + i + " {{ Anchor: (Height: " + rh + "); LayoutMode: Left; Padding: (Top: 4); Background: #142030(0.9); }}");
      b.appendInline("#SkyySkRow" + i, "Group {{ Anchor: (Width: 60, Height: 50); ItemIcon {{ Anchor: (Width: 44, Height: 44, Left: 8, Top: 3); ItemId: \\"" + {PKG}.SkillDefs.ICONS[sl] + "\\"; }} }}");
      b.appendInline("#SkyySkRow" + i, "Group #SkyySkTxt" + i + " {{ Anchor: (Width: 430, Height: " + (rh - 8) + "); LayoutMode: Top; }}");
      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 20); Text: \\"" + safe(title) + "\\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }}");
      b.appendInline("#SkyySkTxt" + i, "Group #SkyySkBar" + i + " {{ Anchor: (Width: {BARW}, Height: 10); Background: #22324a; }}");
      if (fill > 0) b.appendInline("#SkyySkBar" + i, "Group {{ Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 10); Background: " + col + "; }}");
      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 18); Text: \\"" + safe(prog) + "\\"; Style: (FontSize: 11, TextColor: #b8c8d8, VerticalAlignment: Center); }}");
      if (acroRow) {{
        b.appendInline("#SkyySkTxt" + i, "Label #SkyySkBonus {{ Anchor: (Height: 14); Text: \\"\\"; Style: (FontSize: 10, RenderBold: true, TextColor: #d8c0ff, VerticalAlignment: Center); }}");
        b.set("#SkyySkBonus.Text", {PKG}.Acro.bonusText(lv));
      }}
      b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkStat" + i + " {{ Anchor: (Width: 100, Height: 28); Text: \\"Stats\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyySkStat" + i, {EVD}.of("a", "skstat" + sl));
      b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 4); Text: \\"\\"; }}");
    }}
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 18); Text: \\"Gather - brew - smelt - cook - fight with your class weapons - run jump fall dodge.  Stats shows every boost\\"; Style: (FontSize: 10, TextColor: #7f94a8, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    return;
  }}
  int s = this.view;
  java.util.ArrayList rows = {PKG}.SkillTop.all(s);
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\"" + safe("Top 10 - " + {PKG}.SkillDefs.LABELS[s]) + "\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + {PKG}.SkillDefs.COLORS[s] + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  int n = rows.size() < 10 ? rows.size() : 10;
  if (n == 0) b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 24); Text: \\"Nobody has any XP yet.\\"; Style: (FontSize: 12, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int i = 0; i < n; i++) {{
    Object[] e = (Object[]) rows.get(i);
    long x = ((Long) e[1]).longValue();
    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);
    String line = (i + 1) + ".   " + e[0] + "     Level " + {PKG}.SkillDefs.levelOf(x) + "     " + {PKG}.SkillDefs.fmt(x) + " XP";
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 26); Text: \\"" + safe(line) + "\\"; Style: (FontSize: 13, " + (me ? "RenderBold: true, TextColor: #ffe08a" : "TextColor: #e6f0ff") + ", VerticalAlignment: Center); }}");
  }}
  int rank = {PKG}.SkillTop.rankOf(rows, u);
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 20); Text: \\"" + safe(rank > 0 ? "Your rank #" + rank + " of " + rows.size() + " - level " + {PKG}.SkillDefs.levelOf(d[s]) + " - " + {PKG}.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet") + "\\"; Style: (FontSize: 12, TextColor: #c9dff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySkills", "Group #SkyySkNav {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 8); }}");
  b.appendInline("#SkyySkNav", "Label {{ Anchor: (Width: 250, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyySkNav", "TextButton #SkyySkBack {{ Anchor: (Width: 106, Height: 30); Text: \\"Back\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySkBack", {EVD}.of("a", "skback"));
}}""", page))''')

# ================================================================ Stats page: Alchemy / Smithing / Cooking lines, how, class-only guards
rep_block('''spg.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList lines(''', '''}}""", spg))''', r'''# 0.4: optional lines from another mod (bridge skill:stats:<SkillName>, e.g. SkyyCooking for "Cooking"): Function apply(Object[]{UUID,
# Integer level, Boolean next}) -> java.util.List of String; at most 5 lines; -1 = no hook
spg.addMethod(CtNewMethod.make(f"""
public static int hook(java.util.UUID u, int s, int lv, boolean next, java.util.ArrayList out) {{
  try {{
    Object f = {PKG}.SkillStore.bridge().get("skill:stats:" + {PKG}.SkillDefs.NAMES[s]);
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] {{ u, Integer.valueOf(lv), Boolean.valueOf(next) }});
    if (!(r instanceof java.util.List)) return 0;
    java.util.List l = (java.util.List) r;
    int n = 0;
    for (int i = 0; i < l.size() && n < 5; i++) {{
      Object o = l.get(i);
      if (o == null) continue;
      String t = String.valueOf(o).trim();
      if (t.length() == 0) continue;
      out.add(t);
      n++;
    }}
    return n;
  }} catch (Throwable t) {{ return -1; }}
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == {PKG}.SkillDefs.COMBAT) {{
    if (!next) {{
      out.add("No class yet - choose one with /class to start leveling combat");
      if ({PKG}.SkillStore.data(u)[s] > 0L) out.add("Old Combat XP - level " + lv + " - moves to the first class you choose");
    }}
    return out;
  }}
  int row = {PKG}.SkillDefs.perkRow(s);
  if (row < 0) return out;
  int b = next ? lv + 1 : lv;
  if (row == {PKG}.SkillDefs.ACROBATICS) {{
    if (!{PKG}.AcroCfg.ENABLED) {{
      if (!next) out.add("Acrobatics bonuses are turned off on this server");
    }} else {{
      double sp = {PKG}.Acro.speedBonus(b) - (next ? {PKG}.Acro.speedBonus(lv) : 0.0);
      double jp = {PKG}.Acro.jumpBonus(b) - (next ? {PKG}.Acro.jumpBonus(lv) : 0.0);
      double fb = {PKG}.Acro.fallBonus(b) - (next ? {PKG}.Acro.fallBonus(lv) : 0.0);
      double db = {PKG}.Acro.dodgeBonus(b) - (next ? {PKG}.Acro.dodgeBonus(lv) : 0.0);
      if (sp > 0.00001) out.add("+" + pc(sp) + " movement speed (of vanilla speed)");
      if (jp > 0.00001) out.add("+" + num(jp) + " blocks jump height");
      if (fb > 0.00001) out.add("-" + pc(fb) + " fall damage");
      if (db > 0.00001) out.add("+" + pc(db) + " dodge push");
    }}
  }}
  if (s == {PKG}.SkillDefs.ALCHEMY) {{
    if (!{PKG}.AlchCfg.ENABLED) {{
      if (!next) out.add("Alchemy is turned off on this server");
    }} else {{
      double du = {PKG}.Brew.bonusFor(b) - (next ? {PKG}.Brew.bonusFor(lv) : 0.0);
      if (du > 0.00001) {{
        out.add("+" + pc(du) + " longer potion effects");
        if (!next) out.add("   " + {PKG}.Brew.pulseText(b));
      }}
    }}
  }}
  stat(out, {PKG}.PerkCfg.HP[row], lv, next, "max Health");
  stat(out, {PKG}.PerkCfg.STA[row], lv, next, "max Stamina");
  stat(out, {PKG}.PerkCfg.MANA[row], lv, next, "max Mana");
  if (s == {PKG}.SkillDefs.ALCHEMY && {PKG}.AlchCfg.ENABLED) {{
    double ex = {PKG}.Brew.extraChance(b) - (next ? {PKG}.Brew.extraChance(lv) : 0.0);
    if (ex > 0.00001) out.add((next ? "+" : "") + pc(ex) + " chance to brew an extra potion");
  }}
  if (row <= {PKG}.SkillDefs.FARMING) {{
    String[] what = new String[] {{ "mined blocks", "chopped logs", "harvested crops" }};
    double c = {PKG}.Perks.chance(row, b) - (next ? {PKG}.Perks.chance(row, lv) : 0.0);
    if (c > 0.00001) out.add((next ? "+" : "") + pc(c) + " chance to double the drops of " + what[row]);
  }}
  if (row == {PKG}.SkillDefs.COMBAT && {PKG}.SkillDefs.isClass(s) && {PKG}.PerkCfg.ENABLED && {PKG}.PerkCfg.DMG > 0.0) {{
    double dm = next ? {PKG}.PerkCfg.DMG : {PKG}.Perks.damage(lv);
    if (dm > 0.0) out.add("+" + pc(dm) + " damage with " + {PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0] + " weapons" + ({PKG}.PerkCfg.DMG_PVP ? "" : " (against monsters)"));
  }}
  int hooked = hook(u, s, lv, next, out);
  if (s == {PKG}.SkillDefs.COOKING && !next && hooked < 0) out.add("Food you cook gets stronger with your Cooking level (shown here when SkyyCooking is installed)");
  if (s == {PKG}.SkillDefs.SMITHING && !next && out.isEmpty()) out.add("No boosts yet - they arrive with reforging and powders");
  if (next && {PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillCfg.COINS_PER_LEVEL * (long) b) + " coins when you reach level " + b);
  if (!next && out.isEmpty()) out.add(lv <= 0 ? "Nothing yet - level up to unlock boosts" : "This skill gives no boosts on this server");
  return out;
}}""", spg))''')
rep_block('''spg.addMethod(CtNewMethod.make(f"""
public static String how(int s) {{''', '''}}""", spg))''', r'''spg.addMethod(CtNewMethod.make(f"""
public static String how(int s) {{
  if (s == {PKG}.SkillDefs.MINING) return "Earn XP by mining stone and ores - rarer ores pay more";
  if (s == {PKG}.SkillDefs.FORAGING) return "Earn XP by chopping trees - rare woods pay more";
  if (s == {PKG}.SkillDefs.FARMING) return "Earn XP by harvesting fully grown crops - break them or press F on eternal crops and bushes";
  if (s == {PKG}.SkillDefs.ACROBATICS) return "Earn XP by running - jumping - dodging - and surviving falls that hurt (higher falls pay more - safe drops and water pay 0)";
  if (s == {PKG}.SkillDefs.ALCHEMY) return "Earn XP by brewing at the Alchemy Bench - stronger potions and higher bench tiers pay more (Greater potions pay the most)";
  if (s == {PKG}.SkillDefs.SMITHING) return "Earn XP by smelting - take the bars out of a Furnace yourself or use the Furnace tab of /craft (reforging and powders later)";
  if (s == {PKG}.SkillDefs.COOKING) return "Cook at a Cooking Bench - food you cook gets stronger with your level";
  if (s == {PKG}.SkillDefs.COMBAT) return "Your combat skill is your class skill - Archer Archery / Warrior Swordsmanship / Mage Sorcery (Assassin and Shaman later)";
  if (!{PKG}.SkillDefs.isClass(s)) return "";
  String c = {PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0];
  String w = {PKG}.SkillClass.weaponsText(c);
  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w);
}}""", spg))''')
rep('''  if (s >= {PKG}.SkillDefs.CLASS0 && s != cs) {{''', '''  if ({PKG}.SkillDefs.isClass(s) && s != cs) {{''')

# ================================================================ commands: skill args, admin /skills xp
rep('''"mining | foraging | farming | acrobatics | combat (your class skill) | archery | swordsmanship | assassination | shaman | sorcery"''',
    '''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | combat (your class skill) | archery | swordsmanship | assassination | shaman | sorcery"''', count=2)
before('''cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{''', r'''# /skills xp <skill> <amount> (0.4 admin test helper): gives yourself RAW XP (no multiplier, no cap, creative allowed) through the normal
# award path (chat line, level ups, coins, publish). Two required args (optional args are not positional - HANDOFF command rules).
xcmd.addField(CtField.make(f"public {RA} skillArg;", xcmd))
xcmd.addField(CtField.make(f"public {RA} amountArg;", xcmd))
xcmd.addConstructor(CtNewConstructor.make(f"""
public XpCmd() {{
  super("xp", "(admin) Give yourself skill XP for testing: /skills xp alchemy 3100000 (also 500k, 3.1m)");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | alchemy | smithing | cooking | acrobatics | combat (your class skill) | archery | swordsmanship | sorcery", {ATY}.STRING);
  this.amountArg = withRequiredArg("amount", "raw XP, e.g. 3100000 or 3.1m", {ATY}.STRING);
  requirePermission("skyyskills.admin");
  setPermissionGroups(new String[0]);
}}""", xcmd))
xcmd.addMethod(CtNewMethod.make("""
public static long parseAmount(String v) {
  if (v == null) return -1L;
  String t = v.trim().toLowerCase().replace(",", "").replace("_", "");
  double mul = 1.0;
  if (t.endsWith("k")) { mul = 1000.0; t = t.substring(0, t.length() - 1); }
  else if (t.endsWith("m")) { mul = 1000000.0; t = t.substring(0, t.length() - 1); }
  else if (t.endsWith("b")) { mul = 1000000000.0; t = t.substring(0, t.length() - 1); }
  try {
    double x = Double.parseDouble(t) * mul;
    if (Double.isNaN(x) || x < 1.0 || x > 1000000000.0) return -1L;
    return Math.round(x);
  } catch (Throwable e) { return -1L; }
}""", xcmd))
xcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (!pr.hasPermission("skyyskills.admin")) {{ pr.sendMessage({MSG}.raw("[Skills] no permission (skyyskills.admin)")); return; }}
    int s = {PKG}.SkillClass.argSlot(pr, String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) return;
    if (s == {PKG}.SkillDefs.COMBAT) {{ pr.sendMessage({MSG}.raw("[Skills] You have no class - choose one with /class, or name a class skill (archery, swordsmanship, sorcery).")); return; }}
    long amt = parseAmount(String.valueOf(ctx.get(this.amountArg)));
    if (amt <= 0L) {{ pr.sendMessage({MSG}.raw("[Skills] amount must be 1 .. 1000000000 (e.g. 3100000, 500k, 3.1m)")); return; }}
    {PKG}.SkillXp.gain(pr, s, amt);
    {PKG}.SkillCfg.info("admin /skills xp: " + pr.getUsername() + " gave themself " + amt + " " + {PKG}.SkillDefs.NAMES[s] + " XP (" + {PKG}.SkillStore.pkey(pr.getUuid()) + ")");
    pr.sendMessage({MSG}.raw("[Skills] +" + amt + " " + {PKG}.SkillClass.skillName(pr.getUuid(), s) + " XP (admin test, raw - no multiplier). Level now " + {PKG}.SkillStore.level(pr.getUuid(), s) + ".").color("#ffc800"));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills xp failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not give the XP"));
  }}
}}""", xcmd))
''')
rep('''  addSubCommand(new {PKG}.ReloadCmd());
''', '''  addSubCommand(new {PKG}.ReloadCmd());
  addSubCommand(new {PKG}.XpCmd());
''')

# ================================================================ plugin: systems + bridge functions
rep('''  getEntityStoreRegistry().registerSystem(new {PKG}.CombatDmgSys());
''', '''  getEntityStoreRegistry().registerSystem(new {PKG}.CombatDmgSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.AcroFallSeenSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.CraftSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.SmeltSys());
''')
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:level", new {PKG}.SkillFn());
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:level", new {PKG}.SkillFn());
  {PKG}.SkillStore.bridge().put("skill:fn:addxp", new {PKG}.SkillAddFn());
  {PKG}.SkillStore.bridge().put("skill:fn:craftxp", new {PKG}.SkillCraftFn());
''')
rep('''"[SkyySkills] {VERSION} ready - /skills; xp rules: " + rules + "; combat''',
    '''"[SkyySkills] {VERSION} ready - /skills; rows Alchemy (Alchemy Bench) / Smithing (Furnace) / Cooking (via SkyyCooking); bridge skill:fn:addxp + skill:fn:craftxp; xp rules: " + rules + "; combat''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:addxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:craftxp"); }} catch (Throwable t) {{ }}
''')
rep('''          pcfg, scls, perk, cds, spg, scmd):''', '''          pcfg, scls, perk, cds, spg, scmd, alc, smc, bgc, rxp, brew, bxp, ctk, stk, btsk, csy, sxu, ssy, afss, afn, cfn, xcmd):''')

# ================================================================ manifest
rep('''"SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Acrobatics and your class combat skill (SkyyClasses) to level 100. XP from breaking blocks, ripe crops, kills with class weapons and running / jumping / falling / dodging.''',
    '''"SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics and your class combat skill (SkyyClasses) to level 100. XP from breaking blocks, ripe crops, brewing at the Alchemy Bench, smelting at a Furnace, cooking (SkyyCooking), kills with class weapons and running / jumping / big survived falls / dodging. Alchemy makes potion effects last longer and adds max Mana.''')

# ================================================================ 0.4 part 2: SkyyTrees bridge (research/Skill-Trees-Spec.md 9.3 + 10)
# Everything below is additive and generic (SkyyTrees 0.1 is the first user; other mods may use the same keys):
#   skill:fn:xp      Function apply(Object[]{UUID, String skill}) -> Long   total XP of the ACTIVE profile (SkillXpFn)
#   skill:bonus:<uuid>  read only: ConcurrentHashMap source -> immutable Map; xp.<skill> multiplies XP of bridge.bonus.xpSkills
#                    (default Mining, Foraging, Farming, Cooking), clamped 0..5 (at most x6), on XP the player EARNS (gain2 = blocks,
#                    F-harvest, vanilla bench / furnace; skill:fn:craftxp); XP GRANTED through skill:fn:addxp only for
#                    bridge.bonus.addxpSkills (default Cooking = SkyyTrees' Cooking Wisdom on the XP SkyyCooking grants per dish;
#                    SkyyCollections' tier rewards stay exact - Skill-Trees-Spec 9.3 item 2 scopes Wisdom to gathering XP);
#                    dd.<skill> adds to the Mining / Foraging / Farming double-drop chance (Perks.chanceU), total still capped by
#                    perk.doubleDropMax (SkillBonus)
#   skill:on:gather  ConcurrentHashMap name -> Function, created here with putIfAbsent; called on the world thread right after a
#                    gathering block / F-harvest PAID XP (BreakTask / HarvestTask, after the XP and the double-drop roll):
#                    Object[]{PlayerRef, Integer row, BlockType, String world, Boolean harvest, Integer x, Integer y, Integer z}
#   skill:fn:drops   Function apply(Object[]{BlockType, Boolean harvest}) -> java.util.List (fresh roll, Perks.breakDrops/harvestDrops)
#   skill:fn:placed  Function apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Boolean (PlacedStore.contains; null =
#                    unknown because the tracker is off - callers treat that as placed)
#   UI               "Tree" button on the Mining / Foraging / Farming / Cooking rows of /skills and "Skill tree" on their Stats pages,
#                    only while tree:fn:level is on the bridge (SkyyTrees installed); runs /tree <skill> as the player
#                    (CommandManager.handleCommand, the SkyyMenu / SkyyTrees pattern - the tree page replaces ours, nothing is closed
#                    first). Stats page line "Skill tree: +X% double drops, +Y% XP" while a bonus is above 0.
# The Cooking tree's grade / batch bonuses are SkyyCooking's job (it reads tree:fn:level / tree:fn:bonus itself), not ours.
rep('''BTP = "com.hypixel.hytale.protocol.BenchType"
''', '''BTP = "com.hypixel.hytale.protocol.BenchType"
CMGR= "com.hypixel.hytale.server.core.command.system.CommandManager"      # 0.4 trees bridge: the Tree buttons run /tree <skill>
''')
after('''             (BEN, "getId"), (CRPL, "getBenchRecipes"), (BTP, "Processing"), (DMM, "getInspectDamageGroup"), (IS, "isEmpty")):
    B.probe(pool, c, m)
''', '''# 0.4 trees bridge (CommandManager.handleCommand(CommandSender, String) - PlayerRef is a CommandSender, reflect.py)
for c, m in ((CMGR, "get"), (CMGR, "handleCommand"), ("java.util.Map", "putIfAbsent"), ("java.lang.Double", "isNaN")):
    B.probe(pool, c, m)
''')

# ---- config: bridge.bonus.* (inside the bridge block, so a file without any bridge.* key gets them appended with it)
after('''BRIDGE_SKILLS = "Mining,Foraging,Farming,Alchemy,Smithing,Cooking"
''', '''BONUS_XP_SKILLS = "Mining,Foraging,Farming,Cooking"   # 0.4 trees bridge: skills whose XP the skill:bonus xp.<skill> entries raise
BONUS_ADDXP_SKILLS = "Cooking"   # ... and whose skill:fn:addxp GRANTS (XP other mods grant) get it too; SkyyCollections rewards stay exact
''')
after('''BRIDGE_L.append("bridge.maxXpPerMinute=3000000")
''', '''BRIDGE_L.append("# Skill tree bonuses (SkyyTrees posts them in skill:bonus:<uuid>). Wisdom nodes raise the XP you earn yourself in the skills")
BRIDGE_L.append("# of bridge.bonus.xpSkills (blocks, crops, crafts; at most x6). XP another mod grants through skill:fn:addxp gets the Wisdom")
BRIDGE_L.append("# bonus only for the skills in bridge.bonus.addxpSkills (Cooking: SkyyCooking pays your cooking XP that way); rewards such")
BRIDGE_L.append("# as the SkyyCollections tier XP stay exact. The admin /skills xp never gets it. Fortune nodes add to the double-drop chance")
BRIDGE_L.append("# of Mining / Foraging / Farming (the total stays capped at perk.doubleDropMax). bridge.bonus.enabled=false ignores them all.")
BRIDGE_L.append("bridge.bonus.enabled=true")
BRIDGE_L.append("bridge.bonus.xpSkills=" + BONUS_XP_SKILLS)
BRIDGE_L.append("bridge.bonus.addxpSkills=" + BONUS_ADDXP_SKILLS)
''')
rep('''for _decl in ("boolean[] GRANT = new boolean[0]", 'String GRANT_TEXT = ""', "long PER_CALL = 500000L", "long PER_MIN = 3000000L"):''',
    '''bgc.addField(CtField.make('public static final String DEFAULT_BONUS_XP = "%s";' % BONUS_XP_SKILLS, bgc))
bgc.addField(CtField.make('public static final String DEFAULT_BONUS_ADDXP = "%s";' % BONUS_ADDXP_SKILLS, bgc))
for _decl in ("boolean[] GRANT = new boolean[0]", 'String GRANT_TEXT = ""', "long PER_CALL = 500000L", "long PER_MIN = 3000000L",
              "boolean BONUS = true", "boolean[] BONUS_XP = new boolean[0]", 'String BONUS_TEXT = ""',
              "boolean[] BONUS_ADDXP = new boolean[0]", 'String BONUS_ADDXP_TEXT = ""'):''')
rep('''  long m = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerMinute", 3000000L);
  PER_MIN = m < 0L ? 0L : m;
}}""", bgc))''', '''  long m = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerMinute", 3000000L);
  PER_MIN = m < 0L ? 0L : m;
  BONUS = {PKG}.SkillCfg.bool(p, "bridge.bonus.enabled", true);
  boolean[] bx = new boolean[{PKG}.SkillDefs.N];
  StringBuilder bsb = new StringBuilder();
  String[] bps = p.getProperty("bridge.bonus.xpSkills", DEFAULT_BONUS_XP).split(",");
  for (int j = 0; j < bps.length; j++) {{
    String bt = bps[j].trim();
    if (bt.length() == 0) continue;
    int bh = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(bt) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(bt)) bh = s;
    if (bh < 0 || bh == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.bonus.xpSkills: unknown skill '" + bt + "' - ignored"); continue; }}
    bx[bh] = true;
    if (bsb.length() > 0) bsb.append(',');
    bsb.append({PKG}.SkillDefs.LABELS[bh]);
  }}
  BONUS_XP = bx;
  BONUS_TEXT = bsb.toString();
  boolean[] gx = new boolean[{PKG}.SkillDefs.N];
  StringBuilder gsb = new StringBuilder();
  String[] gps = p.getProperty("bridge.bonus.addxpSkills", DEFAULT_BONUS_ADDXP).split(",");
  for (int k = 0; k < gps.length; k++) {{
    String gt = gps[k].trim();
    if (gt.length() == 0) continue;
    int gh = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(gt) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(gt)) gh = s;
    if (gh < 0 || gh == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.bonus.addxpSkills: unknown skill '" + gt + "' - ignored"); continue; }}
    if (!bx[gh]) {PKG}.SkillCfg.warn("bridge.bonus.addxpSkills: " + {PKG}.SkillDefs.LABELS[gh] + " is not in bridge.bonus.xpSkills, so it gets no tree XP bonus anyway");
    gx[gh] = true;
    if (gsb.length() > 0) gsb.append(',');
    gsb.append({PKG}.SkillDefs.LABELS[gh]);
  }}
  BONUS_ADDXP = gx;
  BONUS_ADDXP_TEXT = gsb.toString();
}}""", bgc))''')

# ---- new classes
after('''xcmd = pool.makeClass(PKG + ".XpCmd", pool.get(APC))
''', '''# 0.4 trees bridge
sbn  = pool.makeClass(PKG + ".SkillBonus")
xfn  = pool.makeClass(PKG + ".SkillXpFn")
dfn  = pool.makeClass(PKG + ".SkillDropsFn")
pfn  = pool.makeClass(PKG + ".SkillPlacedFn")
''')

# ---- SkillBonus (before SkillXp: gain3 uses boost; before Perks: chanceU uses dd; before the tasks: gather)
before('''# ================= SkillXp: award + level-up (world thread) =================''', r'''# ================= SkillBonus (0.4 trees bridge, Skill-Trees-Spec 9.3): skill:bonus:<uuid>, skill:on:gather, the Tree buttons =================
# skill:bonus:<uuid> = ConcurrentHashMap source -> immutable Map{"xp.mining": 0.15, "dd.farming": 0.2, ...} (fractions). Read live on every
# award (UUID-keyed = the ACTIVE profile, PROFILES-CONTRACT rule 3; SkyyTrees republishes it within 1 s of a switch). Non-numbers, NaN
# and infinities are skipped; the key is xp. / dd. + the slot NAME in lower case (mining, foraging, farming, cooking, alchemy, ...).
sbn.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FAILED = new java.util.concurrent.ConcurrentHashMap();", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static java.util.Map sources(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("skill:bonus:" + u.toString());
    if (o instanceof java.util.Map) return (java.util.Map) o;
  }} catch (Throwable t) {{ }}
  return null;
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static double sum(java.util.UUID u, String key) {{
  if (u == null || !{PKG}.BridgeCfg.BONUS) return 0.0;
  java.util.Map m = sources(u);
  if (m == null) return 0.0;
  double s = 0.0;
  try {{
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {{
      Object v = it.next();
      if (!(v instanceof java.util.Map)) continue;
      Object n = ((java.util.Map) v).get(key);
      if (!(n instanceof Number)) continue;
      double d = ((Number) n).doubleValue();
      if (Double.isNaN(d) || Double.isInfinite(d)) continue;
      s = s + d;
    }}
  }} catch (Throwable t) {{ return 0.0; }}
  return s;
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static String key(int slot) {{
  return {PKG}.SkillDefs.NAMES[slot].toLowerCase(java.util.Locale.ROOT);
}}""", sbn))
# XP bonus fraction of one slot: only slots listed in bridge.bonus.xpSkills, sum over all sources clamped 0..5 (spec 9.3)
sbn.addMethod(CtNewMethod.make(f"""
public static double xpBonus(java.util.UUID u, int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return 0.0;
  boolean[] on = {PKG}.BridgeCfg.BONUS_XP;
  if (slot >= on.length || !on[slot]) return 0.0;
  double s = sum(u, "xp." + key(slot));
  if (s <= 0.0) return 0.0;
  return s > 5.0 ? 5.0 : s;
}}""", sbn))
# amount x (1 + bonus); the fraction is paid by chance (stone pays 1 XP: +15% must still add 0.15 XP per block on average)
sbn.addMethod(CtNewMethod.make(f"""
public static long boost(java.util.UUID u, int slot, long amt) {{
  if (amt <= 0L) return amt;
  double b = xpBonus(u, slot);
  if (b <= 0.0) return amt;
  double x = (double) amt * (1.0 + b);
  if (x >= 9.0E15) return amt;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w < amt ? amt : w;
}}""", sbn))
# skill:fn:addxp = XP another mod GRANTS (SkyyCollections tier rewards, SkyyCooking dishes): the tree XP bonus only for the skills in
# bridge.bonus.addxpSkills (default Cooking). XP the player earns (gain2, skill:fn:craftxp) follows bridge.bonus.xpSkills alone.
sbn.addMethod(CtNewMethod.make(f"""
public static boolean grantBonus(int slot) {{
  boolean[] g = {PKG}.BridgeCfg.BONUS_ADDXP;
  return slot >= 0 && slot < g.length && g[slot];
}}""", sbn))
# double-drop fraction the trees add for a gathering row (0 = Mining, 1 = Foraging, 2 = Farming), clamped 0..1
sbn.addMethod(CtNewMethod.make(f"""
public static double dd(java.util.UUID u, int row) {{
  if (row < 0 || row > {PKG}.SkillDefs.FARMING) return 0.0;
  double s = sum(u, "dd." + key(row));
  if (s <= 0.0) return 0.0;
  return s > 1.0 ? 1.0 : s;
}}""", sbn))
# SkyyTrees publishes tree:fn:level in its setup and removes it in its shutdown: its presence = the trees are installed
sbn.addMethod(CtNewMethod.make(f"""
public static boolean treesOn() {{
  try {{ return {PKG}.SkillStore.bridge().get("tree:fn:level") instanceof java.util.function.Function; }} catch (Throwable t) {{ return false; }}
}}""", sbn))
# /tree argument of a slot (SkyyTrees 0.1 trees: mining, foraging, farming, cooking); null = no tree for that skill
sbn.addMethod(CtNewMethod.make(f"""
public static String treeName(int slot) {{
  if (slot == {PKG}.SkillDefs.MINING) return "mining";
  if (slot == {PKG}.SkillDefs.FORAGING) return "foraging";
  if (slot == {PKG}.SkillDefs.FARMING) return "farming";
  if (slot == {PKG}.SkillDefs.COOKING) return "cooking";
  return null;
}}""", sbn))
# page click (world thread): run /tree <skill> as the player; the tree page replaces this page (never close a page first)
sbn.addMethod(CtNewMethod.make(f"""
public static void openTree({PR} pr, String tree) {{
  if (pr == null || tree == null) return;
  if (!treesOn()) {{ pr.sendMessage({MSG}.raw("[Skills] Skill trees need SkyyTrees - it is not running on this server").color("#ffb080")); return; }}
  try {{
    {CMGR}.get().handleCommand(pr, "tree " + tree);
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not run /tree " + tree + ": " + t);
    pr.sendMessage({MSG}.raw("[Skills] Could not open the skill tree - try /tree " + tree).color("#ffb080"));
  }}
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static void failed(Object name, Throwable t) {{
  String n = String.valueOf(name);
  if (FAILED.putIfAbsent(n, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("skill:on:gather listener '" + n + "' failed (logged once per listener): " + t);
}}""", sbn))
# world thread, right after a gathering block (row 0-2) or an F-harvest (harvest = true) PAID XP; every listener gets its own argument
# array and its own try/catch, so one broken listener never stops the others or the award
sbn.addMethod(CtNewMethod.make(f"""
public static void gather({PR} pr, int row, {BTY} bt, String world, boolean harvest, int x, int y, int z) {{
  if (pr == null || row < 0 || row > {PKG}.SkillDefs.FARMING) return;
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList fns = new java.util.ArrayList();
  try {{
    Object o = {PKG}.SkillStore.bridge().get("skill:on:gather");
    if (!(o instanceof java.util.Map)) return;
    java.util.Iterator it = ((java.util.Map) o).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (e.getValue() instanceof java.util.function.Function) {{ names.add(e.getKey()); fns.add(e.getValue()); }}
    }}
  }} catch (Throwable t) {{ return; }}
  for (int i = 0; i < fns.size(); i++) {{
    try {{
      ((java.util.function.Function) fns.get(i)).apply(new Object[] {{ pr, Integer.valueOf(row), bt, world, Boolean.valueOf(harvest), Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) }});
    }} catch (Throwable t) {{ failed(names.get(i), t); }}
  }}
}}""", sbn))

''')

# ---- SkillXp: gain3 = the award with or without the tree XP bonus; gain2 / gain keep their meaning (+ the bonus)
rep('''public static void gain2({PR} pr, int skill, long amount, boolean note) {{
  if (pr == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
  java.util.UUID u = pr.getUuid();
''', '''public static void gain3({PR} pr, int skill, long amount, boolean note, boolean bonus) {{
  if (pr == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
  java.util.UUID u = pr.getUuid();
  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, amount);
''')
before('''xp.addMethod(CtNewMethod.make(f"""
public static void gain({PR} pr, int skill, long amount) {{''', '''# 0.4 trees bridge: gain2 = gain3 WITH the skill-tree XP bonus (every normal award). gain3(..., false) pays exactly the amount: the
# admin /skills xp (raw) and BridgeTask (BridgeXp.offer already added the bonus, so the per-minute bridge cap counts it)
xp.addMethod(CtNewMethod.make(f"""
public static void gain2({PR} pr, int skill, long amount, boolean note) {{
  gain3(pr, skill, amount, note, true);
}}""", xp))
''')

# ---- Perks: double-drop chance with the trees' dd.<skill> (both the break and the F-harvest roll)
after('''public static double chance(int row, int lvl) {{
  if (!{PKG}.PerkCfg.ENABLED || row < 0 || row > {PKG}.SkillDefs.FARMING || lvl <= 0) return 0.0;
  double c = lvl * {PKG}.PerkCfg.DD[row];
  return c > {PKG}.PerkCfg.DD_MAX ? {PKG}.PerkCfg.DD_MAX : c;
}}""", perk))
''', '''# 0.4 trees bridge: the level perk + the summed dd.<skill> of skill:bonus:<uuid> (SkyyTrees Fortune nodes); the total is still capped at
# perk.doubleDropMax. perk.enabled=false only turns off SkyySkills' own level perk, not the tree bonus (bridge.bonus.enabled does that).
perk.addMethod(CtNewMethod.make(f"""
public static double chanceU(java.util.UUID u, int row, int lvl) {{
  if (row < 0 || row > {PKG}.SkillDefs.FARMING) return 0.0;
  double c = chance(row, lvl) + {PKG}.SkillBonus.dd(u, row);
  if (c > {PKG}.PerkCfg.DD_MAX) c = {PKG}.PerkCfg.DD_MAX;
  return c < 0.0 ? 0.0 : c;
}}""", perk))
''')
rep('''    double c = chance(row, {PKG}.SkillStore.level(pr.getUuid(), row));
''', '''    double c = chanceU(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row));
''', 2)

# ---- PlacedStore.contains (skill:fn:placed)
after('''public static synchronized boolean remove(String w, long k) {
  boolean r = set(w).remove(Long.valueOf(k));
  if (r) DIRTY.add(w);
  return r;
}""", plc))
''', '''# 0.4 trees bridge (skill:fn:placed): was this position placed by a player? LRU-capped at CAP per world, so a very old placement can be
# forgotten (Skill-Trees-Spec 9.3 accepts that). The first call for a world loads its file, like remove() in BreakTask.
plc.addMethod(CtNewMethod.make("""
public static synchronized boolean contains(String w, long k) {
  return set(w).contains(Long.valueOf(k));
}""", plc))
''')

# ---- gather listeners: after the XP + the double-drop roll, only where that roll may run (a player-placed block never gets here)
rep('''    {PKG}.SkillXp.gain(pr, (int) this.rule[0], this.rule[1]);
    {PKG}.Perks.breakDouble(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED);
''', '''    {PKG}.SkillXp.gain(pr, (int) this.rule[0], this.rule[1]);
    {PKG}.Perks.breakDouble(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED);
    if (this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED) {{
      {V3I} g = this.ev.getTargetBlock();
      if (g != null) {PKG}.SkillBonus.gather(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, false, g.x(), g.y(), g.z());
    }}
''')
rep('''      {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.FARMING, this.amount);
      {PKG}.Perks.harvestDouble(pr, this.bt, this.wn);
''', '''      {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.FARMING, this.amount);
      {PKG}.Perks.harvestDouble(pr, this.bt, this.wn);
      {PKG}.SkillBonus.gather(pr, {PKG}.SkillDefs.FARMING, this.bt, this.wn, true, this.x, this.y, this.z);
''')

# ---- bridge XP: the tree bonus is added in BridgeXp.offer (counted by bridge.maxXpPerMinute), so BridgeTask pays it as it is
rep('''  long amt = {PKG}.SkillCfg.scaled(base);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt))''', '''  long amt = {PKG}.SkillCfg.scaled(base);
  if (!grant || {PKG}.SkillBonus.grantBonus(slot)) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt))''')
# grant = true: skill:fn:addxp (XP another mod grants); false: skill:fn:craftxp (a craft the player finished through another mod's page)
rep('''public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units) {{''',
    '''public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant) {{''')
rep('''offer((java.util.UUID) a[0], slot, base, src, expect, null, 0) >= 0L''', '''offer((java.util.UUID) a[0], slot, base, src, expect, null, 0, true) >= 0L''')
rep('''slot == {PKG}.SkillDefs.ALCHEMY ? rc : null, crafts);''', '''slot == {PKG}.SkillDefs.ALCHEMY ? rc : null, crafts, false);''')
rep('''# Any thread; no I/O; never blocks.
''', '''# grant = true for skill:fn:addxp (tree XP bonus only for bridge.bonus.addxpSkills), false for skill:fn:craftxp (bridge.bonus.xpSkills).
# Any thread; no I/O; never blocks.
''')
rep('''    {PKG}.SkillXp.gain(pr, this.slot, this.amt);
    if (this.rc != null && this.slot == {PKG}.SkillDefs.ALCHEMY''', '''    {PKG}.SkillXp.gain3(pr, this.slot, this.amt, true, false);
    if (this.rc != null && this.slot == {PKG}.SkillDefs.ALCHEMY''')
# admin /skills xp stays raw (no multiplier, no tree bonus)
rep('''    {PKG}.SkillXp.gain(pr, s, amt);
    {PKG}.SkillCfg.info("admin /skills xp: ''', '''    {PKG}.SkillXp.gain3(pr, s, amt, true, false);
    {PKG}.SkillCfg.info("admin /skills xp: ''')
rep('''(admin test, raw - no multiplier)''', '''(admin test, raw - no multiplier, no tree bonus)''')

# ---- the three bridge Functions (after Perks + PlacedStore, before the 0.4 XP Functions)
before('''# ================= skill:fn:addxp (0.4): apply(Object[]{UUID, String skill, Number baseXp, String source [, String expectKey]}) -> Boolean =====''', r'''# ================= trees bridge Functions (0.4, Skill-Trees-Spec 9.3 / 10): skill:fn:xp, skill:fn:drops, skill:fn:placed =================
# skill:fn:xp  apply(Object[]{UUID, String skill}) -> Long = total XP of that skill on the ACTIVE profile (SkillFn's rules: exact or
# 3+ letter prefix names, "Combat" = the current class skill; unknown -> 0). SkyyTrees computes Dust from it. Any thread.
xfn.addInterface(pool.get("java.util.function.Function"))
xfn.addConstructor(CtNewConstructor.make("public SkillXpFn() { }", xfn))
xfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    int i = {PKG}.SkillDefs.indexOf(String.valueOf(a[1]));
    if (i < 0) return Long.valueOf(0L);
    java.util.UUID u = (java.util.UUID) a[0];
    if (i == {PKG}.SkillDefs.COMBAT) i = {PKG}.SkillClass.rowSlot(u, i);
    long x = {PKG}.SkillStore.rd({PKG}.SkillStore.data(u), i);
    return Long.valueOf(x < 0L ? 0L : x);
  }} catch (Throwable t) {{ return Long.valueOf(0L); }}
}}""", xfn))
# skill:fn:drops  apply(Object[]{BlockType, Boolean harvest}) -> java.util.List = a FRESH roll of the block's own drops, the same
# reproduction as the double drop (break: Perks.breakDrops; F-harvest: Perks.harvestDrops); null when it cannot be reproduced
# (tool-dependent drops, blocks with both Soft and Breaking drops, no harvest data). World thread (BlockHarvestUtils.getDrops).
dfn.addInterface(pool.get("java.util.function.Function"))
dfn.addConstructor(CtNewConstructor.make("public SkillDropsFn() { }", dfn))
dfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    if (a.length < 1 || !(a[0] instanceof {BTY})) return null;
    {BTY} bt = ({BTY}) a[0];
    boolean h = a.length > 1 && Boolean.TRUE.equals(a[1]);
    if (h) return {PKG}.Perks.harvestDrops(bt);
    return {PKG}.Perks.breakDrops(bt);
  }} catch (Throwable t) {{ return null; }}
}}""", dfn))
# skill:fn:placed  apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Boolean: TRUE = a player placed the block there,
# FALSE = not placed (as far as the LRU tracker knows); null = unknown (ignorePlaced=false: the tracker records nothing) - SkyyTrees
# treats anything but FALSE as placed and skips that position.
pfn.addInterface(pool.get("java.util.function.Function"))
pfn.addConstructor(CtNewConstructor.make("public SkillPlacedFn() { }", pfn))
pfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!{PKG}.SkillCfg.IGNORE_PLACED) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 4 || a[0] == null) return null;
    int x = ((Number) a[1]).intValue();
    int y = ((Number) a[2]).intValue();
    int z = ((Number) a[3]).intValue();
    return Boolean.valueOf({PKG}.PlacedStore.contains(String.valueOf(a[0]), {PKG}.PlacedStore.key(x, y, z)));
  }} catch (Throwable t) {{ return null; }}
}}""", pfn))
''')

# ---- /skills page: Tree buttons (only while SkyyTrees is installed; the rows keep their layout otherwise)
rep(r'''    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 6); Text: \\"\\"; }}");
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      boolean classRow = sl == {PKG}.SkillDefs.COMBAT;''', r'''    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 6); Text: \\"\\"; }}");
    boolean trees = {PKG}.SkillBonus.treesOn();
    int tw = trees ? 356 : 430;
    int bw = trees ? 330 : {BARW};
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      boolean classRow = sl == {PKG}.SkillDefs.COMBAT;''')
rep('''      int fill = need > 0L ? (int) ({BARW}L * cur / need) : {BARW};
      if (fill < 0) fill = 0;
      if (fill > {BARW}) fill = {BARW};
      String prog = need > 0L''', '''      int fill = need > 0L ? (int) ((long) bw * cur / need) : bw;
      if (fill < 0) fill = 0;
      if (fill > bw) fill = bw;
      String prog = need > 0L''')
rep(r'''"Group #SkyySkTxt" + i + " {{ Anchor: (Width: 430, Height: " + (rh - 8) + "); LayoutMode: Top; }}"''',
    r'''"Group #SkyySkTxt" + i + " {{ Anchor: (Width: " + tw + ", Height: " + (rh - 8) + "); LayoutMode: Top; }}"''')
rep(r'''"Group #SkyySkBar" + i + " {{ Anchor: (Width: {BARW}, Height: 10); Background: #22324a; }}"''',
    r'''"Group #SkyySkBar" + i + " {{ Anchor: (Width: " + bw + ", Height: 10); Background: #22324a; }}"''')
before(r'''      b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkStat" + i + " {{ Anchor: (Width: 100, Height: 28); Text: \\"Stats\\"; " + bs + " }}");''', r'''      if (trees) {{
        if ({PKG}.SkillBonus.treeName(sl) != null) {{
          b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkTree" + i + " {{ Anchor: (Width: 70, Height: 28); Text: \\"Tree\\"; " + bs + " }}");
          ev.addEventBinding({BT}.Activating, "#SkyySkTree" + i, {EVD}.of("a", "sktree" + sl));
        }} else {{
          b.appendInline("#SkyySkRow" + i, "Label {{ Anchor: (Width: 70, Height: 28); Text: \\"\\"; }}");
        }}
        b.appendInline("#SkyySkRow" + i, "Label {{ Anchor: (Width: 4, Height: 28); Text: \\"\\"; }}");
      }}
''')
before(r'''    if (data.indexOf("skback\\"") >= 0) {{ this.view = -1; rebuild(); return; }}''', r'''    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("sktree" + i + "\\"") >= 0) {{ {PKG}.SkillBonus.openTree(this.playerRef, {PKG}.SkillBonus.treeName(i)); return; }}
    }}
''')

# ---- Stats page: "Skill tree: ..." line + "Skill tree" button
before('''spg.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList lines(''', r'''# 0.4 trees bridge: "Skill tree: +X% double drops, +Y% XP" from skill:bonus:<uuid> (SkyyTrees); null when both are 0
spg.addMethod(CtNewMethod.make(f"""
public static String treeLine(java.util.UUID u, int s) {{
  double dd = {PKG}.SkillBonus.dd(u, s);
  double xb = {PKG}.SkillBonus.xpBonus(u, s);
  if (dd <= 0.00001 && xb <= 0.00001) return null;
  StringBuilder sb = new StringBuilder("Skill tree: ");
  if (dd > 0.00001) sb.append("+").append(pc(dd)).append(" double drops");
  if (xb > 0.00001) {{
    if (dd > 0.00001) sb.append(", ");
    sb.append("+").append(pc(xb)).append(" XP");
  }}
  return sb.toString();
}}""", spg))
''')
before('''  int hooked = hook(u, s, lv, next, out);
''', '''  if (!next) {{
    String tl = treeLine(u, s);
    if (tl != null) out.add(tl);
  }}
''')
rep(r'''  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 164, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStBack {{ Anchor: (Width: 130, Height: 30); Text: \\"< Back\\"; " + bs + " }}");
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 20, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStTop {{ Anchor: (Width: 130, Height: 30); Text: \\"Top 10\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
''', r'''  String tree = {PKG}.SkillBonus.treesOn() ? {PKG}.SkillBonus.treeName(s) : null;
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: " + (tree != null ? 89 : 164) + ", Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStBack {{ Anchor: (Width: 130, Height: 30); Text: \\"< Back\\"; " + bs + " }}");
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 20, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStTop {{ Anchor: (Width: 130, Height: 30); Text: \\"Top 10\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
  if (tree != null) {{
    b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 20, Height: 30); Text: \\"\\"; }}");
    b.appendInline("#SkyyStNav", "TextButton #SkyyStTree {{ Anchor: (Width: 130, Height: 30); Text: \\"Skill tree\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyStTree", {EVD}.of("a", "sttree"));
  }}
''')
after(r'''    if (data.indexOf("stback\\"") >= 0) {{ p.getPageManager().openCustomPage(ref, st, new {PKG}.SkillsPage(this.playerRef)); return; }}
''', r'''    if (data.indexOf("sttree\\"") >= 0) {{ {PKG}.SkillBonus.openTree(this.playerRef, {PKG}.SkillBonus.treeName(this.slot)); return; }}
''')

# ---- plugin: publish / remove the Functions, create the listener map, log line, class list
after('''  {PKG}.SkillStore.bridge().put("skill:fn:craftxp", new {PKG}.SkillCraftFn());
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:xp", new {PKG}.SkillXpFn());
  {PKG}.SkillStore.bridge().put("skill:fn:drops", new {PKG}.SkillDropsFn());
  {PKG}.SkillStore.bridge().put("skill:fn:placed", new {PKG}.SkillPlacedFn());
  {PKG}.SkillStore.bridge().putIfAbsent("skill:on:gather", new java.util.concurrent.ConcurrentHashMap());
''')
after('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:craftxp"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:xp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:drops"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:placed"); }} catch (Throwable t) {{ }}
''')
rep('''bridge skill:fn:addxp + skill:fn:craftxp; xp rules: " + rules''',
    '''bridge skill:fn:addxp + skill:fn:craftxp; trees bridge on (tree bonuses " + ({PKG}.BridgeCfg.BONUS ? "XP for " + {PKG}.BridgeCfg.BONUS_TEXT + " (grants from other mods: " + ({PKG}.BridgeCfg.BONUS_ADDXP_TEXT.length() > 0 ? {PKG}.BridgeCfg.BONUS_ADDXP_TEXT : "none") + ") + double drops" : "off") + ", SkyyTrees " + ({PKG}.SkillBonus.treesOn() ? "found" : "not loaded yet") + "); xp rules: " + rules''')
rep('''afss, afn, cfn, xcmd):''', '''afss, afn, cfn, xcmd, sbn, xfn, dfn, pfn):''')
rep('''Stats page per skill. Level ups pay SkyyCoins.''',
    '''Stats page per skill. Skill tree bonuses and Tree buttons with SkyyTrees (optional). Level ups pay SkyyCoins.''')

# ---- part 2 sanity
assert s.count('bridge().put("skill:fn:xp"') == 1 and s.count('bridge().put("skill:fn:drops"') == 1 and s.count('bridge().put("skill:fn:placed"') == 1
assert s.count('bridge().remove("skill:fn:xp")') == 1 and s.count('bridge().remove("skill:fn:drops")') == 1 and s.count('bridge().remove("skill:fn:placed")') == 1
assert s.count('putIfAbsent("skill:on:gather"') == 1 and 'remove("skill:on:gather"' not in s
assert s.count("{PKG}.SkillBonus.gather(") == 2 and s.count("chanceU(pr.getUuid(), row,") == 2 and "double c = chance(row, {PKG}.SkillStore.level" not in s
assert s.count("SkillXp.gain3(") == 2 and s.count("SkillBonus.boost(") == 2
assert "SkyySkTree" in s and "sktree" in s and "sttree" in s and "SkyyStTree" in s
assert s.count("SkillBonus.grantBonus(slot)) amt = {PKG}.SkillBonus.boost(u, slot, amt);") == 1 and s.count("int units, boolean grant) {{") == 1
assert s.count("null, 0, true) >= 0L") == 1 and s.count("? rc : null, crafts, false);") == 1 and s.count("BridgeXp.offer(") == 2
assert s.count('"bridge.bonus.addxpSkills", DEFAULT_BONUS_ADDXP') == 1 and 'BRIDGE_L.append("bridge.bonus.addxpSkills=" + BONUS_ADDXP_SKILLS)' in s

# ================================================================ sanity
assert 'VERSION = "0.4"' in s and "0.4 (research/Alchemy-Skill-Spec.md" in s
assert "SkillDefs.ROWS" not in s, "a /skills or perk loop still uses the 5-row ROWS constant"
assert s.count("registerSystem(new {PKG}.CraftSys())") == 1 and s.count("registerSystem(new {PKG}.SmeltSys())") == 1
assert s.count("registerSystem(new {PKG}.AcroFallSeenSys())") == 1 and s.count("registerSystem(new {PKG}.AcroFallSys())") == 1
assert "Acro.noteFall(u, d.getInitialAmount())" not in s and s.count("Acro.noteFall(") == 1
assert '"acro.fallXpPerBlock", 2.0' not in s and "FALL_XP " not in s
assert s.count('bridge().put("skill:fn:addxp"') == 1 and s.count('bridge().put("skill:fn:craftxp"') == 1
assert s.count('bridge().remove("skill:fn:addxp")') == 1 and s.count('bridge().remove("skill:fn:craftxp")') == 1
assert 'equalsIgnoreCase("Cookingbench")' in s and 'equalsIgnoreCase("Campfire")' in s
assert "slot >= {PKG}.SkillDefs.N) return false;" not in s and "k < n; k++) if (d[k] > 0L)" not in s
assert "{PKG}.Brew.tick(u, store, cb, ref, dt);" in s and "{PKG}.Brew.setBonus(u, lv[5]);" in s and "{PKG}.Brew.forget(u);" in s
assert "Combat:" not in s.split("public static String levelsOf", 1)[1].split("}}\"\"\", sto))", 1)[0]
assert "--deploy" in s   # the script keeps its optional deploy switch; this workflow never passes it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.3.2
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
