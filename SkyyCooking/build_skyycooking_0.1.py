"""SkyyCooking 0.1 - build script (javassist via jpype). NEW mod, never deployed: edit this file directly (no patch script yet).
Run:   python build_skyycooking_0.1.py            -> SkyyCooking/SkyyCooking-0.1.jar
       python build_skyycooking_0.1.py --deploy   -> also copies to Mods/SkyyCooking.jar (ONLY with Skyy's OK - HANDOFF deploy rule)

WHAT IT IS - research/Cooking-Skill-Spec.md, adapted to the orchestrator's decisions of 2026-09-24:
 (1) Cooking lives in its OWN mod (this one), so its ~450 generated assets can never break SkyySkills if they fail to load.
     SkyySkills 0.4 owns only the Cooking ROW (slot 12) and receives Cooking XP through its XP-grant bridge skill:fn:addxp;
     SkyySkills' own craft system ignores Cookingbench crafts - this mod owns them.
 (2) XP pace re-scaled so the best route reaches Cooking 50 in about the time Alchemy 50 takes (~27 focused hours, Alchemy spec
     4.3), instead of the spec's draft table (which put level 50 at ~550,000 pies). Model in the XP section below (printed at build).
 (3) Grades 11 and 12 come ONLY from the Cooking skill tree, the 4th tree in SkyyTrees, read through bridge tree:fn:level
     (UUID, "Cooking.<NodeId>") -> Integer (research/Skill-Trees-Spec.md section 10, node ids = Cooking spec 7.2).
 Zero hard dependencies: without SkyySkills every dish comes out plain (Grade 0) and cooking pays no XP.

HOW IT PLAYS: cook at a placed vanilla Cooking Bench (its ingredients can come from Magic Bags through the SkyySacks bench link).
Every finished dish pays Cooking XP (SkyySkills shows the +XP line). From Cooking 10 on dishes come out GRADED: "Meat Pie (Grade 5)".
Grade = floor(Cooking level / 10) (max 10 from levels) + Cooking-tree bonuses (cap 12). Multiplier M = 2^(Grade/5): x2.00 at
Grade 5 (level 50), x4.00 at Grade 10 (level 100), x4.59 / x5.28 at the tree-only Grades 11 / 12. The Grade multiplies BOTH the
strength (heal %, regen per tick, max-Health / max-Stamina bonus, damage resistance) and the duration of everything the dish does.
Whoever eats the dish gets the cook's Grade. Same-Grade dishes stack (they are one item id); different Grades do not.

ENGINE PATH (VERIFIED bytecode 2026-09-24, tools/dev/bcfull.py):
 - Cooking Bench = bench id "Cookingbench", Bench.Type Crafting, no tiers. Every vanilla cooking recipe has TimeSeconds 1/2/5, so it
   takes the QUEUED path: CraftingManager.tick removes one unit's inputs, fires new CraftRecipeEvent$Post(job.recipe, job.quantity)
   through ComponentAccessor.invoke(ref, ev) (= CommandBuffer.invoke -> Store.internal_invoke, synchronous), then calls
   giveOutput(ref, accessor, job, n) -> giveOutput(ref, accessor, recipe, 1) ONLY if the event was not cancelled. So one Post per
   finished dish, but getQuantity() is the whole batch: we count 1 unit per Post when TimeSeconds > 0 (instant path: quantity).
 - CookSys (EntityEventSystem on CraftRecipeEvent$Post, the only system class of this mod) grades SYNCHRONOUSLY in the handler: it
   cancels the Post and hands out the graded stacks exactly the way vanilla giveOutput would (SimpleItemContainer.addOrDropItemStack
   with the handler's CommandBuffer), into getCombinedStorageHotbarBackpack (storage first - SkyySacks 0.6.5 lesson). Grade 0 with
   no tree bonus = nothing cancelled, vanilla gives the plain dish. Tree extras (extra dish / ingredient back / double ingredient)
   are given NEXT TO the normal output, never instead of it.
 - The XP award is deferred with world.execute (runs after every other system saw the event, the SkyySkills BreakTask pattern):
   skipped if someone ELSE cancelled the Post, if the profile switched meanwhile (pkey changed), or past the per-minute cap.
 - Eating needs no Java at all: a graded dish is a normal food item whose eat chain (vanilla Root_Secondary_Consume_Food_T<n>)
   points at PRE-SCALED effect assets; vanilla ApplyEffectInteraction looks them up by id (Cooking spec 5.1, VERIFIED bytecode).

GENERATED ASSETS (asset pack in this jar, all copied from the game's own shapes in Assets.zip, 447 JSON files):
 - Server/Entity/Effects/SkyyCook/Skyy_Cook_<Base>_G<g>.json      13 vanilla food effects x Grades 1-12 = 156
   (Food_Instant_Heal_T1/T2/T3/Bread, HealthRegen_Buff_T1-3, Meat_Buff_T1-3, FruitVeggie_Buff_T1-3; vanilla JSON with ONLY the
   strength fields x S and Duration x D (instant 0.1 s effects keep their duration); caps: instant heal <= 100 %, regen <= 12 %
   per tick, max-stat bonus <= +150 %, resistance <= 50 %, Duration <= 2400 s)
 - Server/Item/Interactions/SkyyCook/Skyy_Cook_<Family>_Check_T<t>_G<g>.json   3 families x 3 tiers x 12 = 108
   (vanilla <Family>_TierCheck_T<t> rule "a weaker buff never replaces a stronger one" extended to all 39 members of a family:
   EffectCondition on every stronger member, Match None -> Serial [ClearEntityEffect every weaker member, ApplyEffect this one];
   rank = (strength, duration). Only vanilla interaction types. doTickChain runs instant operations back to back in ONE tick.)
 - Server/Item/Items/SkyyCook/Skyy_Cook_<Dish>_G<g>.json           15 dishes x 12 = 180 (vanilla dish copy: Parent Template_Food,
   every own key EXCEPT Recipe, own name/description/Quality, InteractionVars.Effect -> the Grade assets)
 - Server/Item/Items/SkyyCook/Recipes/Skyy_Cook_Recipe_<X>.json     3 Cooking Bench recipes for the Campfire dishes (vanilla
   "Variant recipe" shape of Ingredient/Life Essence Recipes: Variant true, Parent = the output item, own Recipe with Output)
 - Server/Languages/en-US/server.lang   name + description of every graded dish (items.* and server.items.*, the SkyyAccessories form)
 BUILD-TIME SELF-CHECK (the build fails if one is false): M(5) = 2, M(10) = 4; every effect / interaction / root interaction id
 referenced by a generated item or interaction exists (generated or Assets.zip); every item Parent, icon, model and texture exists;
 no graded dish has a Recipe; every recipe variant outputs one of the 15 dishes and uses existing inputs; no generated id collides
 with a vanilla id; the 15 dishes, their eat chains and the 13 base effects still have the numbers this build expects (a Hytale
 update stops the build instead of shipping wrong numbers); every graded item has lang lines; XP keys are real Cookingbench outputs;
 no cooking output feeds a recipe that gives its own inputs back (craft/uncraft loop); XP per call and per minute stay under
 SkyySkills' bridge caps.

GRADED DISHES (15): Food_Wildmeat_Cooked, Food_Fish_Grilled, Food_Vegetable_Cooked (T1, via the new Cooking Bench recipes),
 Food_Bread, the 4 kebabs, Food_Salad_Berry, Food_Salad_Mushroom (T2), Food_Popcorn, the 3 pies, Food_Salad_Caesar (T3).
 NOT graded: Food_Cheese (it is an input by id for Caesar Salad and Potion_Morph_Mouse), ingredients (flour, dough, salt, spices,
 raw fish) - they still pay XP. A placed Campfire has no owner and fires no event (VERIFIED): plain food, no XP.

STACKING WHEN EATING: instant heal every bite; same buff again = timer restarts (Overwrite, never adds); a stronger buff of the same
 family replaces the weaker (cleared); a weaker one while a stronger runs does nothing for that family; different families run side
 by side; vanilla (Grade 0) buffs rank inside the families. KNOWN LIMIT (spec 5.4): a PLAIN vanilla dish eaten while a graded buff
 runs may add its own vanilla buff next to it (vanilla chains only know vanilla ids) - worst case one extra vanilla-strength buff.

SKILL TREE (Cooking spec 7.2, read at craft time; per-level values in cooking.properties tree.<Id>.per):
 CGourmet (25) +0.8 %/lvl chance of +1 Grade; CBatch (20) +1 %/lvl one extra dish (same Grade, no XP); CFrugal (10) +2 %/lvl one
 item-id ingredient back (never Fuel / resource-type inputs); CGrill (15) / CPrep (10) / CBaker (10) +2/3/3 %/lvl +1 Grade on
 T1 / T2 / T3 dishes; CIngr (10) +3 %/lvl double output of an ingredient craft (flour, dough, salt, spices); CGourmet2 (20) +1 %/lvl
 +1 Grade (adds to CGourmet); CSig (10) +1 %/lvl +2 Grades; CMaster (5) level 1 = +1 Grade on every dish, levels 2-5 +5 % each
 chance of one more. One roll per dish: g = level/10 (max 10) + (CMaster >= 1), then +1 on the combined chance or +2 on CSig, cap 12.
 CWisdom (XP %) and CFed (max Health) are SkyyTrees / SkyySkills hooks, not read here: SkyyTrees 0.1 posts Cooking Wisdom as
 xp.cooking in skill:bonus:<uuid>, and SkyySkills 0.4 multiplies the XP this mod sends through skill:fn:addxp by it (BridgeXp.offer,
 only while Cooking is in BOTH bridge.bonus.xpSkills and bridge.bonus.addxpSkills of SkyySkills' xp.properties - both list it by
 default; its bridge.maxXpPerMinute counts the boosted XP: legit peak 708k x 1.15 < 3M).

ANTI-EXPLOIT: creative = vanilla output, no Grade, no XP (creativeGrades=false; on the cook:fn:out bridge too, where an unknown game
 mode without the caller's creative flag also means plain and no XP); 1 unit per queued Post (batch trap); no graded dish
 has a recipe; a Post another system cancelled first is neither graded nor paid; profile:busy:<uuid> (pending crash recovery) =
 plain output and no XP; XP dropped if the profile switched before the award; per-player cap maxXpPerMinute (base XP, counted before
 xpMultiplier) - the dish is still given when it trips; an item id is only ever handed out after Item.getAssetMap() confirmed it
 exists (if the asset pack failed to load, food comes out plain - never an "Invalid Item").

STORAGE: nothing per player on disk. Config Skyy_SkyyCooking/cooking.properties (global). Memory only, per UUID: the XP-per-minute
 window, the chat throttle and the "new Grade" hint (a profile switch does not reset the XP window on purpose). The Grade lives in
 the item id, so it survives chests, trades, drops, relogs and Magic Bags; the XP lives in SkyySkills' per-profile files.

BRIDGE (System.getProperties().get("skyy.bridge")):
 reads  skill:fn:level  (Object[]{UUID, "Cooking"}) -> Integer          SkyySkills 0.4 (absent = no SkyySkills: Grade 0, no XP)
        skill:fn:addxp  (Object[]{UUID, "Cooking", Long baseXp, String source}) -> Boolean   SkyySkills 0.4 (Alchemy spec 7.1;
                        must list Cooking in bridge.addxp.skills - orchestrator decision 6); calls are split at 400,000 XP
        (skill:fn:addxp also gets the profile key captured at craft time as its optional 5th element, expectKey)
        tree:fn:level   (Object[]{UUID, "Cooking.<Id>"}) -> Integer     SkyyTrees 0.1 (absent = every node 0)
        tree:fn:bonus   same argument -> Double chance (level x per from SkyyTrees' trees.properties; Master Chef = (level - 1) x per);
                        preferred for the chances so Skyy tunes them in ONE place; absent -> level x tree.<Id>.per of cooking.properties
        profile:fn:key / profile:busy:<uuid>                             SkyyProfiles contract
 writes cook:fn:grade   apply(UUID) -> Integer  guaranteed Grade now (level/10 + Master Chef) - for the HUD / Menu / Skills Stats page
        cook:fn:out     apply(Object[]{UUID, String recipeId, Number crafts [, String expectKey [, Boolean creative]]}) -> java.util.List
                        of ItemStack: graded outputs + tree extras for a Cookingbench craft ANOTHER mod completed without
                        CraftingManager (SkyySacks /craft), and it pays the Cooking XP itself (SkyySkills ignores Cookingbench crafts,
                        so skill:fn:craftxp pays 0 for them). null = not a Cookingbench recipe (or expectKey mismatch; pass null to
                        skip the key check). Call it on the player's world thread and pass creative = the player's
                        GameMode == Creative. The function also reads the game mode itself (PlayerRef -> Ref -> Store, only when
                        Store.isInThread()). Creative (flag TRUE or read as Creative, unless creativeGrades=true), profile:busy,
                        enabled=false, or a game mode that is unknown with no flag passed -> the plain vanilla outputs and NO XP.
                        Nothing calls it yet (SkyySacks 0.7.3 never crafts Cookingbench recipes).
        cook:prefix     "Skyy_Cook_Food_" (SkyySacks catOf -> Farming bag; Bazaar)
        skill:stats:Cooking  apply(Object[]{UUID, Integer level, Boolean next}) -> List of String: the Cooking lines of SkyySkills 0.4's
                        Stats page (your Grade and multiplier, next Grade, tree chances; "Level L+1 adds" shows a new Grade at 10, 20 ...)
 All removed again in shutdown().

XP (defaults written to cooking.properties, base XP per finished craft, keyed by the output id; SkyySkills' multiplier on top):
 Meat Pie 23,900 - Apple Pie 25,250 - Pumpkin Pie 23,200 - Bread 12,900 - Caesar Salad 11,800 - Meat Skewer 5,250 - Fruit / Veg
 Skewer 3,650 - Mushroom Skewer 2,850 - Berry Salad 4,850 - Mushroom Salad 3,250 - Popcorn 3,000 - Grilled Fish 2,000 - Cooked
 Wildmeat 1,600 - Roast Vegetable 1,200 - Flour 1,425 - Spices 855 - Dough 640 - Cheese 430 - Raw Fish 285 - Salt 140 - other 1,000.
 Model (printed by the build): meat-pie route = 23.7 weighted raw items -> ~26,850 XP; at the Alchemy spec's 1,800 items/hour that is
 ~2.04M XP/h -> Cooking 50 in ~27 h (vegetable skewers only: ~38 h). Level 10 comes after half a pie and level 20 after ~20 pies
 (the shared curve is steep late, flat early); decision 2 anchors level 50 only. Legit bench peak (Caesar salad, 1 s) = 708k base
 XP/min, under SkyySkills' addxp caps (500k per call, 3M per minute); our own cap defaults to 1.5M/min.

UNVERIFIED (first in-game test): that the 447 generated assets load from this jar (items + lang are proven for Skyy mods; effects and
 interactions from a Skyy jar are new - NotEnoughPotions ships both the same way); that a mod-shipped Variant recipe item shows on the
 Cooking Bench; that dishes given from the Post handler with its CommandBuffer land in the inventory (vanilla does the same call);
 the pace in hours; long family-check Serials (up to 38 ClearEntityEffect + 1 ApplyEffect; doTickChain runs instant operations in
 one tick - VERIFIED bytecode - but a chain this long is new).
TEST (Skyy, after a deploy with SkyySkills 0.4 and optionally SkyyTrees 0.1): server log "[SkyyCooking] 0.1 ready", no asset errors
 naming Skyy_Cook_; /cookadmin give pie_meat 5 -> "Meat Pie (Grade 5)" (Rare) with the tooltip numbers; /cooking at level 0 -> Grade 0;
 cook bread at a placed Cooking Bench with bag ingredients -> plain Bread + Cooking XP; queue 5 skewers -> 5 skewers, 5 x the XP (not
 25x); set Cooking 50 (/skills admin XP helper) and cook a Meat Pie -> exactly one "Meat Pie (Grade 5)"; eat Grade 5 bread at low
 health -> ~30 % heal; eat a Grade 5 Meat Pie -> regen icon 12:00, max health +30 %; Grade 10 pie then Grade 5 skewer -> the pie's buffs
 stay; Grade 10 pie again -> timer back to 24:00, never added; Grade 5 + Grade 5 stack, Grade 5 + 6 do not; chest + relog keeps the
 Grade; the Cooking Bench lists Cooked Wildmeat / Grilled Fish / Roast Vegetable; placed Campfire -> plain food, no XP; creative ->
 plain, no XP; second player eats your Grade 5 pie -> Grade 5 effects; fresh profile -> plain food; SkyyTrees Master Chef -> +1 Grade.

COMMANDS (HANDOFF command rules): /cooking = your Cooking level, Grade, multiplier, next Grade, tree chances (hytale:Adventurer).
 /cookadmin give <dish> <grade> (5 dishes, grade 0-12, dish = Food_Pie_Meat or pie_meat), /cookadmin reload: requirePermission
 skyycooking.admin + setPermissionGroups(new String[0]). No pages (chat only), so no UI risk.
"""
import sys, os, json, zipfile, copy, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
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
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
MSG = "com.hypixel.hytale.server.core.Message"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
GM  = "com.hypixel.hytale.protocol.GameMode"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
CAC = "com.hypixel.hytale.component.ComponentAccessor"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
CEV = "com.hypixel.hytale.component.system.CancellableEcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
CRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
CRP_= "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"   # '$' form only in the class literal (UBP pattern)
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
CRM = "com.hypixel.hytale.builtin.crafting.component.CraftingManager"
BRQ = "com.hypixel.hytale.protocol.BenchRequirement"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
PB  = "com.hypixel.hytale.server.core.plugin.PluginBase"

# API probes (VERIFIED 2026-09-24 with tools/dev/reflect.py + bcfull.py; a Hytale update that renames one stops the build here)
for c, m in ((CRE, "getCraftedRecipe"), (CRE, "getQuantity"), (CEV, "isCancelled"), (CEV, "setCancelled"),
             (CRR, "getInput"), (CRR, "getPrimaryOutput"), (CRR, "getBenchRequirement"), (CRR, "getTimeSeconds"), (CRR, "getId"),
             (CRR, "getAssetMap"), (CRM, "getOutputItemStacks"), (MQ, "getItemId"), (MQ, "getResourceTypeId"), (MQ, "getQuantity"),
             (BRQ, "id"), (ITM, "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             (IS, "getItemId"), (IS, "getQuantity"), (PLA, "getInventory"), (PLA, "getGameMode"), (GM, "Creative"),
             (INV, "getCombinedStorageHotbarBackpack"), (SIC, "addOrDropItemStack"),
             (UNI, "get"), (UNI, "getPlayer"), (PR, "isValid"), (PR, "getUuid"), (PR, "sendMessage"), (PR, "hasPermission"),
             (PR, "getReference"), (REF, "isValid"), (REF, "getStore"), (ST, "isInThread"),
             (MSG, "raw"), (MSG, "color"), (WLD, "execute"), (EST, "getWorld"), (ST, "getExternalData"), (ST, "getComponent"),
             (ACH, "getReferenceTo"), ("com.hypixel.hytale.component.Archetype", "empty"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "withRequiredArg"), (AC, "addAliases"),
             (ATY, "STRING"), (PB, "shutdown"), (PB, "getEntityStoreRegistry"), (PB, "getCommandRegistry"), (PB, "getDataDirectory"),
             ("com.hypixel.hytale.component.ComponentRegistryProxy", "registerSystem")):
    B.probe(pool, c, m)

PKG = "com.skyy.cooking"
T = {"PKG": PKG, "PR": PR, "REF": REF, "ST": ST, "UNI": UNI, "WLD": WLD, "EST": EST, "CTX": CTX, "ATY": ATY, "RA": RA, "MSG": MSG,
     "PLA": PLA, "GM": GM, "ACH": ACH, "CB": CB, "CAC": CAC, "EV": EV, "QRY": QRY, "CRE": CRE, "CRP": CRP_, "CRR": CRR, "CRM": CRM,
     "BRQ": BRQ, "MQ": MQ, "ITM": ITM, "IS": IS, "IC": IC, "SIC": SIC, "LOG": LOG, "JPI": JPI, "VERSION": VERSION}
def jsrc(s):
    """Java source template: @NAME@ -> constant (keeps Java braces single - no f-string doubling)"""
    def rep(m):
        k = m.group(1)
        if k not in T: raise SystemExit("jsrc: unknown token @%s@" % k)
        return T[k]
    return re.sub(r"@([A-Z_]+)@", rep, s)

# =====================================================================================================================
# ASSET GENERATION (pure Python, before the classes: the Java side bakes in the generated dish list, tiers and factors)
# =====================================================================================================================
AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
ANAMES = AZ.namelist()
def rd(n): return json.loads(AZ.read(n).decode("utf-8-sig"))
def ids_under(prefix):
    out = {}
    for n in ANAMES:
        if n.startswith(prefix) and n.endswith(".json"):
            out[os.path.basename(n)[:-5]] = n
    return out
V_ITEMS = ids_under("Server/Item/Items/")
V_EFFECTS = ids_under("Server/Entity/Effects/")
V_INTER = ids_under("Server/Item/Interactions/")
V_ROOTS = ids_under("Server/Item/RootInteractions/")
V_RTYPES = ids_under("Server/Item/ResourceTypes/")
V_QUAL = ids_under("Server/Item/Qualities/")
V_COMMON = set(n for n in ANAMES if n.startswith("Common/"))
VLANG = {}
for _l in AZ.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
    if "=" in _l and not _l.lstrip().startswith("#"):
        _k, _v = _l.split("=", 1)
        VLANG[_k.strip()] = _v.strip()

GEN_MAX = 12
COOK_STRENGTH_EXP = 1.0   # a: strength factor S = M^a (Skyy asked x4 strength AND x4 duration at 100; 0.5/0.5 = x4 total)
COOK_DURATION_EXP = 1.0   # b: duration factor D = M^b   (baked into the assets - a change needs a rebuild)
def M(g): return 2.0 ** (g / 5.0)
def SF(g): return M(g) ** COOK_STRENGTH_EXP
def DF(g): return M(g) ** COOK_DURATION_EXP
assert M(5) == 2.0 and M(10) == 4.0, "Grade curve must hit x2 at Grade 5 and x4 at Grade 10"   # self-check 1

DISHES = ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked", "Food_Bread", "Food_Kebab_Fruit", "Food_Kebab_Meat",
          "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Salad_Berry", "Food_Salad_Mushroom", "Food_Popcorn", "Food_Pie_Apple",
          "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Salad_Caesar"]
INGREDIENTS = ["Ingredient_Flour", "Ingredient_Dough", "Ingredient_Salt", "Ingredient_Spices"]   # CIngr (Prep Cook) targets
INSTANT = ["Food_Instant_Heal_T1", "Food_Instant_Heal_T2", "Food_Instant_Heal_T3", "Food_Instant_Heal_Bread"]
FAMILIES = ["HealthRegen", "Meat", "FruitVeggie"]
BASES = INSTANT + ["%s_Buff_T%d" % (f, t) for f in FAMILIES for t in (1, 2, 3)]
# the vanilla numbers this build was written for (Cooking spec 4.1, re-read from Assets.zip 2026-09-24) - self-check 4
EXPECT = {
    "Food_Instant_Heal_T1": ("heal", 5.0, None), "Food_Instant_Heal_T2": ("heal", 10.0, None),
    "Food_Instant_Heal_T3": ("heal", 15.0, None), "Food_Instant_Heal_Bread": ("heal", 15.0, None),
    "HealthRegen_Buff_T1": ("regen", 1.0, 45.0), "HealthRegen_Buff_T2": ("regen", 1.5, 150.0), "HealthRegen_Buff_T3": ("regen", 2.0, 360.0),
    "Meat_Buff_T1": ("maxHealth", 1.05, 45.0), "Meat_Buff_T2": ("maxHealth", 1.10, 150.0), "Meat_Buff_T3": ("maxHealth", 1.15, 360.0),
    "FruitVeggie_Buff_T1": ("maxStamina", 1.10, 45.0), "FruitVeggie_Buff_T2": ("maxStamina", 1.20, 150.0),
    "FruitVeggie_Buff_T3": ("maxStamina", 1.30, 360.0),
}
CAP_HEAL, CAP_REGEN, CAP_MULT, CAP_RES, CAP_DUR = 100.0, 12.0, 2.5, 0.5, 2400.0

def r4(v): return float("%.4f" % v)
VBASE = {}
for b in BASES:
    if b not in V_EFFECTS: raise SystemExit("vanilla effect missing: " + b)
    d = rd(V_EFFECTS[b])
    kind, amount, dur = EXPECT[b]
    if kind == "heal":
        ok = d.get("ValueType") == "Percent" and abs(d["StatModifiers"]["Health"] - amount) < 1e-9 and d.get("Duration", 0) <= 0.5
    elif kind == "regen":
        ok = (d.get("ValueType") == "Percent" and abs(d["StatModifiers"]["Health"] - amount) < 1e-9 and abs(d["Duration"] - dur) < 1e-9
              and d.get("DamageCalculatorCooldown", 0) > 0)
    else:
        stat = "Health" if kind == "maxHealth" else "Stamina"
        m = d["RawStatModifiers"][stat][0]
        ok = (m.get("CalculationType") == "Multiplicative" and m.get("Target") == "Max" and abs(m["Amount"] - amount) < 1e-9
              and abs(d["Duration"] - dur) < 1e-9)
    if not ok:
        raise SystemExit("self-check 4: vanilla effect %s no longer matches this build's expectation (%s %s %s): %s" % (b, kind, amount, dur, json.dumps(d)))
    VBASE[b] = d

def scale_effect(b, g):
    """vanilla effect JSON b scaled to Grade g (g = 0 -> the vanilla JSON itself). Only the strength fields and Duration change."""
    d = VBASE[b]
    if g == 0: return d
    S, D = SF(g), DF(g)
    o = copy.deepcopy(d)
    instant = d.get("Duration", 0) <= 0.5
    pct = d.get("ValueType") == "Percent"
    for k, v in list(o.get("StatModifiers", {}).items()):
        nv = v * S
        if pct: nv = min(nv, CAP_HEAL if instant else CAP_REGEN)
        o["StatModifiers"][k] = r4(nv)
    for stat, lst in o.get("RawStatModifiers", {}).items():
        for m in lst:
            a = m["Amount"]
            if m.get("CalculationType") == "Multiplicative":
                m["Amount"] = r4(min(1.0 + (a - 1.0) * S, CAP_MULT))
            else:
                m["Amount"] = r4(a * S)
    for typ, lst in o.get("DamageResistance", {}).items():
        for m in lst:
            m["Amount"] = r4(min(m["Amount"] * S, CAP_RES))
    if not instant:
        o["Duration"] = float("%.2f" % min(d["Duration"] * D, CAP_DUR))
    return o

def eff_id(b, g): return b if g == 0 else "Skyy_Cook_%s_G%d" % (b, g)
def check_id(fam, t, g): return "Skyy_Cook_%s_Check_T%d_G%d" % (fam, t, g)
def dish_id(dish, g): return "Skyy_Cook_%s_G%d" % (dish, g)

files = {}
G_EFFECTS, G_INTER, G_ITEMS = {}, {}, {}
for b in BASES:
    for g in range(1, GEN_MAX + 1):
        i = eff_id(b, g)
        G_EFFECTS[i] = scale_effect(b, g)
        files["Server/Entity/Effects/SkyyCook/%s.json" % i] = json.dumps(G_EFFECTS[i], indent=2)

# ---- family checks: rank = (strength, duration, tier, grade), vanilla Grade 0 members included
def strength(fam, e):
    if fam == "HealthRegen": return e["StatModifiers"]["Health"]
    if fam == "Meat": return e["RawStatModifiers"]["Health"][0]["Amount"]
    return e["RawStatModifiers"]["Stamina"][0]["Amount"]
max_clears = 0
for fam in FAMILIES:
    members = []
    for t in (1, 2, 3):
        for g in range(0, GEN_MAX + 1):
            e = scale_effect("%s_Buff_T%d" % (fam, t), g)
            members.append(((round(strength(fam, e), 6), round(e["Duration"], 4), t, g), eff_id("%s_Buff_T%d" % (fam, t), g), t, g))
    members.sort()
    keys = [m[0] for m in members]
    assert len(set(keys)) == len(keys)
    for idx, (key, eid, t, g) in enumerate(members):
        if g == 0: continue
        above = [m[1] for m in members[idx + 1:]]
        below = [m[1] for m in members[:idx]]
        serial = {"Type": "Serial", "Interactions": [{"Type": "ClearEntityEffect", "EntityEffectId": x} for x in below] +
                  [{"Type": "ApplyEffect", "EffectId": eid}]}
        max_clears = max(max_clears, len(below))
        node = serial if not above else {"Type": "EffectCondition", "EntityEffectIds": above, "Match": "None", "Next": serial,
                                         "Failed": {"Type": "Simple", "RunTime": 0}}
        cid = check_id(fam, t, g)
        G_INTER[cid] = node
        files["Server/Item/Interactions/SkyyCook/%s.json" % cid] = json.dumps(node, indent=2)

# ---- graded dishes
QORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
for q in QORDER: assert q in V_QUAL, "vanilla quality missing: " + q
def grade_quality(g): return "Uncommon" if g <= 2 else ("Rare" if g <= 5 else ("Epic" if g <= 8 else "Legendary"))
ROMAN = {1: "I", 2: "II", 3: "III"}
def pct_s(v): return ("%.1f" % v).rstrip("0").rstrip(".")
def num_s(v): return ("%.3f" % v).rstrip("0").rstrip(".")
def mmss(sec):
    s = int(round(sec)); return "%d:%02d" % (s // 60, s % 60)
DISH_TIER, DISH_NAME, DISH_FX = {}, {}, {}
lang = []
W = '<color is="#ffffff">%s</color>'
for dish in DISHES:
    if dish not in V_ITEMS: raise SystemExit("vanilla dish missing: " + dish)
    v = rd(V_ITEMS[dish])
    sec = (v.get("Interactions") or {}).get("Secondary")
    m = re.match(r"^Root_Secondary_Consume_Food_T([123])$", str(sec))
    if v.get("Parent") != "Template_Food" or not m:
        raise SystemExit("self-check 4: %s is no longer a Template_Food dish with a T1-T3 eat root (%s, %s)" % (dish, v.get("Parent"), sec))
    DISH_TIER[dish] = int(m.group(1))
    DISH_NAME[dish] = VLANG.get("items.%s.name" % dish) or dish
    fx = []
    for e in v["InteractionVars"]["Effect"]["Interactions"]:
        if isinstance(e, dict) and e.get("Type") == "ApplyEffect" and e.get("EffectId") in INSTANT and len(e) == 2:
            fx.append(("I", e["EffectId"]))
            continue
        mm = re.match(r"^(HealthRegen|Meat|FruitVeggie)_TierCheck_T([123])$", str(e)) if isinstance(e, str) else None
        if not mm:
            raise SystemExit("self-check 4: unexpected entry in %s's eat chain: %s" % (dish, json.dumps(e)))
        fx.append(("F", mm.group(1), int(mm.group(2))))
    if not fx or fx[0][0] != "I":
        raise SystemExit("self-check 4: %s's eat chain does not start with an instant heal" % dish)
    DISH_FX[dish] = fx
    for g in range(1, GEN_MAX + 1):
        gid = dish_id(dish, g)
        o = copy.deepcopy(v)
        o.pop("Recipe", None)
        o["TranslationProperties"] = {"Name": "server.items.%s.name" % gid, "Description": "server.items.%s.description" % gid}
        vq = v.get("Quality", "Common")
        o["Quality"] = vq if (vq in QORDER and QORDER.index(vq) >= QORDER.index(grade_quality(g))) else grade_quality(g)
        chain = []
        bullets, dur = [], 0.0
        heal = None
        for f in fx:
            if f[0] == "I":
                chain.append({"Type": "ApplyEffect", "EffectId": eff_id(f[1], g)})
                heal = scale_effect(f[1], g)["StatModifiers"]["Health"]
            else:
                fam, k = f[1], f[2]
                chain.append(check_id(fam, k, g))
                e = scale_effect("%s_Buff_T%d" % (fam, k), g)
                dur = max(dur, e["Duration"])
                if fam == "HealthRegen":
                    bullets.append("• " + W % ("Health Regen " + ROMAN[k]) + " (%s%% health every %s s)" % (pct_s(e["StatModifiers"]["Health"]), pct_s(e["DamageCalculatorCooldown"])))
                elif fam == "Meat":
                    res = e.get("DamageResistance", {}).get("Physical", [{}])[0].get("Amount")
                    bullets.append("• " + W % ("Health Boost " + ROMAN[k]) + " (+%s%% max health%s)" % (
                        pct_s((e["RawStatModifiers"]["Health"][0]["Amount"] - 1.0) * 100.0),
                        (", %s%% less physical and projectile damage" % pct_s(res * 100.0)) if res else ""))
                else:
                    st = e.get("StatModifiers", {}).get("Stamina")
                    bullets.append("• " + W % ("Stamina Boost " + ROMAN[k]) + " (+%s%% max stamina%s)" % (
                        pct_s((e["RawStatModifiers"]["Stamina"][0]["Amount"] - 1.0) * 100.0),
                        (", +%s stamina every %s s" % (num_s(st), pct_s(e["DamageCalculatorCooldown"]))) if st else ""))
        ev = dict(v["InteractionVars"]["Effect"])
        ev["Interactions"] = chain
        o["InteractionVars"]["Effect"] = ev
        G_ITEMS[gid] = o
        files["Server/Item/Items/SkyyCook/%s.json" % gid] = json.dumps(o, indent=2)
        name = "%s (Grade %d)" % (DISH_NAME[dish], g)
        if g <= 10:
            head = "Grade %d food - cooked at Cooking %d or higher." % (g, g * 10)
        else:
            head = "Grade %d food - only a Cooking skill tree bonus reaches it." % g
        head += " Heal and buffs " + W % ("x%.2f" % SF(g)) + " stronger, buffs last " + W % ("x%.2f" % DF(g)) + " longer."
        body = "Instantly restores " + W % (pct_s(heal) + "%") + " health"
        if bullets:
            body += " and grants:\\n\\n" + "\\n".join(bullets) + "\\n\\nDuration: " + W % mmss(dur)
        else:
            body += "."
        desc = head + "\\n\\n" + body
        for pre in ("items.", "server.items."):
            lang.append("%s%s.name=%s" % (pre, gid, name))
            lang.append("%s%s.description=%s" % (pre, gid, desc))

# ---- Cooking Bench recipes for the 3 Campfire dishes (vanilla Variant-recipe shape, Ingredient_Life_Essence_Wheat.json)
BENCH = rd(V_ITEMS["Bench_Cooking"])
BENCH_CATS = [c["Id"] for c in BENCH["BlockType"]["Bench"]["Categories"]]
assert BENCH["BlockType"]["Bench"]["Id"] == "Cookingbench" and BENCH["BlockType"]["Bench"]["Type"] == "Crafting", "Cooking Bench changed"
VARIANTS = [   # (recipe item, output dish, inputs) - Campfire inputs + 1 Fuel (Cooking spec 3.2, [SKYY?] fuel cost)
    ("Skyy_Cook_Recipe_Wildmeat", "Food_Wildmeat_Cooked", [("R", "Meats", 1), ("R", "Fuel", 1)]),
    ("Skyy_Cook_Recipe_Fish", "Food_Fish_Grilled", [("I", "Food_Fish_Raw", 1), ("R", "Fuel", 1)]),
    ("Skyy_Cook_Recipe_Vegetable", "Food_Vegetable_Cooked", [("R", "Vegetables", 1), ("R", "Fuel", 1)]),
]
for rid, outd, ins in VARIANTS:
    v = rd(V_ITEMS[outd])
    camp = v.get("Recipe") or {}
    assert [b.get("Id") for b in camp.get("BenchRequirement", [])] == ["Campfire"], "%s is no longer a Campfire recipe" % outd
    node = {
        "TranslationProperties": {"Name": "server.items.%s.name" % outd, "Description": "server.items.%s.description" % outd},
        "Variant": True,
        "Parent": outd,
        "Icon": v["Icon"],
        "Recipe": {
            "TimeSeconds": camp.get("TimeSeconds", 2),
            "Input": [({"ResourceTypeId": x, "Quantity": q} if k == "R" else {"ItemId": x, "Quantity": q}) for k, x, q in ins],
            "Output": [{"ItemId": outd, "Quantity": 1}],
            "BenchRequirement": [{"Type": "Crafting", "Id": "Cookingbench", "Categories": ["Prepared"]}],
            "OutputQuantity": 1,
        },
    }
    G_ITEMS[rid] = node
    files["Server/Item/Items/SkyyCook/Recipes/%s.json" % rid] = json.dumps(node, indent=2)

# =====================================================================================================================
# BUILD-TIME SELF-CHECK: every generated item / interaction references ids that exist
# =====================================================================================================================
errs = []
def need(kind, i, where):
    pools = {"effect": (V_EFFECTS, G_EFFECTS), "inter": (V_INTER, G_INTER), "root": (V_ROOTS, {}), "item": (V_ITEMS, G_ITEMS)}[kind]
    if not isinstance(i, str) or (i not in pools[0] and i not in pools[1]):
        errs.append("%s: unknown %s id %r" % (where, kind, i))
def walk_inter(node, where):
    """an interaction reference: a string id or an inline interaction object (vanilla item / interaction JSON shape)"""
    if isinstance(node, str):
        need("inter", node, where); return
    if not isinstance(node, dict):
        errs.append("%s: unexpected interaction node %r" % (where, node)); return
    for k, v in node.items():
        if k == "Parent": need("inter", v, where)
        elif k in ("EffectId", "EntityEffectId"): need("effect", v, where)
        elif k == "EntityEffectIds":
            for x in v: need("effect", x, where)
        elif k == "Interactions":
            for x in v: walk_inter(x, where)
        elif k in ("Next", "Failed"):
            if isinstance(v, str): need("inter", v, where)
            elif isinstance(v, dict) and ("Type" in v or "Parent" in v): walk_inter(v, where)
            elif isinstance(v, dict):
                for tk, tv in v.items(): walk_inter(tv, where)   # Charging: {"2.5": {...}}
def need_common(path, where):
    if path and "Common/" + path not in V_COMMON: errs.append("%s: missing file Common/%s" % (where, path))
for cid, node in G_INTER.items():
    walk_inter(node, "interaction " + cid)
for iid, node in G_ITEMS.items():
    need("item", node.get("Parent"), "item " + iid)
    for typ, root in (node.get("Interactions") or {}).items():
        if isinstance(root, str): need("root", root, "item %s Interactions.%s" % (iid, typ))
        else: walk_inter(root, "item %s Interactions.%s" % (iid, typ))
    for var, vv in (node.get("InteractionVars") or {}).items():
        for x in vv.get("Interactions", []): walk_inter(x, "item %s InteractionVars.%s" % (iid, var))
    need_common(node.get("Icon"), "item " + iid)
    bt = node.get("BlockType") or {}
    need_common(bt.get("CustomModel"), "item " + iid)
    for tx in bt.get("CustomModelTexture", []): need_common(tx.get("Texture"), "item " + iid)
    if iid.startswith("Skyy_Cook_Food_"):
        if "Recipe" in node: errs.append("graded dish %s has a Recipe (self-check 3)" % iid)
        for suf in ("name", "description"):
            for pre in ("items.", "server.items."):
                if not any(l.startswith("%s%s.%s=" % (pre, iid, suf)) for l in lang): errs.append("no lang line %s%s.%s" % (pre, iid, suf))
    else:
        rc = node["Recipe"]
        outs = [o["ItemId"] for o in rc["Output"]]
        if len(outs) != 1 or outs[0] not in DISHES: errs.append("recipe variant %s must output one graded dish (self-check 3)" % iid)
        for inp in rc["Input"]:
            if "ItemId" in inp: need("item", inp["ItemId"], "recipe " + iid)
            elif inp.get("ResourceTypeId") not in V_RTYPES: errs.append("recipe %s: unknown resource type %r" % (iid, inp.get("ResourceTypeId")))
        for br in rc["BenchRequirement"]:
            if br["Id"] != "Cookingbench" or any(c not in BENCH_CATS for c in br.get("Categories", [])): errs.append("recipe %s: bad bench %r" % (iid, br))
for kind, gen, van in (("effect", G_EFFECTS, V_EFFECTS), ("interaction", G_INTER, V_INTER), ("item", G_ITEMS, V_ITEMS)):
    for i in gen:
        if not i.startswith("Skyy_Cook_") or i in van: errs.append("generated %s id %s collides with vanilla or lacks the Skyy_Cook_ prefix (self-check 5)" % (kind, i))
if errs:
    raise SystemExit("ASSET SELF-CHECK FAILED (%d):\n  " % len(errs) + "\n  ".join(errs[:60]))
N_EFF, N_INT, N_DISH, N_VAR = len(G_EFFECTS), len(G_INTER), len([i for i in G_ITEMS if i.startswith("Skyy_Cook_Food_")]), len(VARIANTS)
assert (N_EFF, N_INT, N_DISH, N_VAR) == (13 * GEN_MAX, 9 * GEN_MAX, 15 * GEN_MAX, 3), (N_EFF, N_INT, N_DISH, N_VAR)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
print("assets: %d effects + %d family checks + %d graded dishes + %d recipe variants = %d JSON, %d lang lines; longest check clears %d; self-check OK"
      % (N_EFF, N_INT, N_DISH, N_VAR, N_EFF + N_INT + N_DISH + N_VAR, len(lang), max_clears))
print("grade factors: " + ", ".join("G%d x%.2f" % (g, SF(g)) for g in range(0, GEN_MAX + 1)))

# =====================================================================================================================
# XP TABLE (orchestrator decision 2: level 50 in about Alchemy's time, ~27 focused hours on the best route)
# =====================================================================================================================
# Model: a craft's XP follows the raw gathering effort in its whole ingredient chain ("chain raw", in item units weighted by how
# slow they are to get). A finished DISH pays 85 % of its chain's raw value x K (x1.25 for recipes that need recipe knowledge:
# pies, Caesar salad); an INGREDIENT craft (flour, dough, salt, spices, cheese, raw fish) pays 15 % of its own direct raw inputs x K.
# So a whole chain pays ~K per raw unit and no single step is a shortcut (flour spam pays 15 %). Throughput assumption = the Alchemy
# spec's 1,800 gathered items per hour with bags (UNVERIFIED in game). K is chosen so the meat-pie route lands at ~27 h to level 50.
K_XP, DISH_SHARE, ING_SHARE, KNOW_BONUS, ITEMS_PER_HOUR = 950.0, 0.85, 0.15, 1.25, 1800.0
LV50 = 55172425   # SkyySkills table, levels 1-50 (0.3.2 asserts it)
W_ITEM = {"Ingredient_Stick": 0.5, "*Deco_Tankard_State_Filled_Water": 0.5, "Food_Egg": 2.0}
W_RT = {"Fuel": 0.5, "Meats": 1.5, "Milk_Bucket": 3.0, "Fish": 2.0, "Fish_Uncommon": 2.0, "Fish_Rare": 2.0, "Fish_Epic": 2.0, "Fish_Legendary": 2.0}
def recipe_of(item_id):
    r = rd(V_ITEMS[item_id]).get("Recipe")
    return r
def primary(item_id, r):
    po = r.get("PrimaryOutput")   # e.g. Food_Fish_Raw_Uncommon (Variant) -> Food_Fish_Raw x2
    if isinstance(po, dict) and po.get("ItemId"): return po["ItemId"], int(po.get("Quantity", r.get("OutputQuantity", 1)) or 1)
    outs = r.get("Output") or []
    if outs: return outs[0]["ItemId"], int(outs[0].get("Quantity", r.get("OutputQuantity", 1)) or 1)
    return item_id, int(r.get("OutputQuantity", 1) or 1)
COOK = {}   # output id -> (inputs [(kind, id, qty)], out qty, seconds, knowledge)
for iid, path in V_ITEMS.items():
    try: r = rd(path).get("Recipe")
    except Exception: continue
    if not r or not any(b.get("Id") == "Cookingbench" for b in r.get("BenchRequirement") or []): continue
    out, q = primary(iid, r)
    if out in COOK and out != iid: continue      # Food_Fish_Raw_Rare etc. -> keep the base recipe of Food_Fish_Raw
    ins = [(("R", i["ResourceTypeId"]) if i.get("ResourceTypeId") else ("I", i["ItemId"])) + (int(i.get("Quantity", 1) or 1),) for i in r.get("Input", [])]
    COOK[out] = (ins, q, float(r.get("TimeSeconds", 0) or 0), bool(r.get("KnowledgeRequired", False)))
for rid, outd, ins in VARIANTS:
    COOK[outd] = ([(k, x, q) for k, x, q in ins], 1, float(G_ITEMS[rid]["Recipe"]["TimeSeconds"]), False)
for dsh in DISHES: assert dsh in COOK, "no Cookingbench recipe makes " + dsh
def weight(kind, i):
    return W_RT.get(i, 1.0) if kind == "R" else W_ITEM.get(i, 1.0)
_memo = {}
def chain_raw(out, depth=0):
    if out in _memo: return _memo[out]
    assert depth < 8, "recipe cycle at " + out
    ins, q, _, _ = COOK[out]
    tot = 0.0
    for kind, i, n in ins:
        tot += (chain_raw(i, depth + 1) if (kind == "I" and i in COOK and i != out) else weight(kind, i)) * n
    _memo[out] = tot / q
    return _memo[out]
def direct_raw(out):
    ins, q, _, _ = COOK[out]
    return sum(weight(k, i) * n for k, i, n in ins if not (k == "I" and i in COOK))
def rnd_to(v, step): return int(step * round(v / step))
XP = {}
for out in sorted(COOK):
    if out in DISHES:
        XP[out] = rnd_to(K_XP * DISH_SHARE * chain_raw(out) * (KNOW_BONUS if COOK[out][3] else 1.0), 50)
    else:
        XP[out] = rnd_to(K_XP * ING_SHARE * direct_raw(out), 5)
XP_DEFAULT = 1000   # any other Cookingbench output (modded content); the server log names it once
# route estimate: one meat pie with its whole chain (flour, dough, spices, 1/5 of a salt craft)
def chain_xp(out, depth=0):
    ins, q, _, _ = COOK[out]
    x = XP[out] / float(q)
    for kind, i, n in ins:
        if kind == "I" and i in COOK and i != out: x += chain_xp(i, depth + 1) * n
    return x
pie_xp, pie_raw = chain_xp("Food_Pie_Meat"), chain_raw("Food_Pie_Meat")
xph = ITEMS_PER_HOUR / pie_raw * pie_xp
HOURS_50 = LV50 / xph
kebab_h = LV50 / (ITEMS_PER_HOUR / chain_raw("Food_Kebab_Vegetable") * chain_xp("Food_Kebab_Vegetable"))
print("XP table (base XP per finished craft): " + ", ".join("%s=%d" % (k, XP[k]) for k in sorted(XP)))
print("pace: meat pie chain = %.1f raw units -> %d XP (%.0f XP/unit); ~%.0f XP/h at %d items/h -> Cooking 50 in ~%.1f h (veg kebabs only: ~%.1f h)"
      % (pie_raw, pie_xp, pie_xp / pie_raw, xph, ITEMS_PER_HOUR, HOURS_50, kebab_h))
assert 25.0 <= HOURS_50 <= 30.0, "decision 2: level 50 must take 25-30 focused hours on the best route (Alchemy's pace), model says %.1f" % HOURS_50
# bench-limited peak (one CraftingManager queue per player): XP per recipe second x 60 - stays under SkyySkills' addxp caps
PEAK = max(XP[o] / max(COOK[o][2], 1.0) * 60.0 for o in COOK)
MAX_PER_MIN = int(math.ceil(PEAK * 2.0 / 100000.0) * 100000)   # 2x the legit bench peak, rounded up to 100k
assert max(XP.values()) <= 400000 and MAX_PER_MIN <= 3000000, "XP must stay under skill:fn:addxp's 500k/call and 3M/min caps"
print("bench peak %.0f base XP/min -> default maxXpPerMinute=%d" % (PEAK, MAX_PER_MIN))
# self-check: craft/uncraft loop - no recipe anywhere takes a cooking output and gives back one of that output's own inputs
ALLREC = []
for iid, path in V_ITEMS.items():
    try: r = rd(path).get("Recipe")
    except Exception: continue
    if r: ALLREC.append((iid, r))
for n in ANAMES:
    if n.startswith("Server/Item/Recipes/") and n.endswith(".json"):
        try: ALLREC.append((os.path.basename(n)[:-5], rd(n)))
        except Exception: pass
for out, (ins, q, _, _) in COOK.items():
    if XP.get(out, 0) <= 0: continue
    mine = set(i for k, i, n in ins if k == "I")
    for rid, r in ALLREC:
        rin = set(i.get("ItemId") for i in r.get("Input", []) if i.get("ItemId"))
        if out not in rin: continue
        routs = set(o.get("ItemId") for o in (r.get("Output") or []))
        if isinstance(r.get("PrimaryOutput"), dict): routs.add(r["PrimaryOutput"].get("ItemId"))
        if not routs: routs = {rid}
        if routs & mine:
            raise SystemExit("self-check: craft/uncraft loop - %s (pays %d XP) feeds %s which returns %s" % (out, XP[out], rid, sorted(routs & mine)))

# ---- the generated cooking.properties (written on first run; comments must stay on their own lines)
NODES = [("CGourmet", 25, 0.008, "chance of +1 Grade"), ("CBatch", 20, 0.01, "chance of one extra dish (same Grade, no XP)"),
         ("CFrugal", 10, 0.02, "chance to get one item ingredient back (never Fuel or resource-type inputs)"),
         ("CGrill", 15, 0.02, "chance of +1 Grade on T1 dishes (cooked meat, grilled fish, roast vegetable)"),
         ("CPrep", 10, 0.03, "chance of +1 Grade on T2 dishes (bread, skewers, berry and mushroom salad)"),
         ("CBaker", 10, 0.03, "chance of +1 Grade on T3 dishes (popcorn, pies, Caesar salad)"),
         ("CIngr", 10, 0.03, "chance an ingredient craft (flour, dough, salt, spices) gives double output"),
         ("CGourmet2", 20, 0.01, "chance of +1 Grade on any dish (adds to CGourmet)"),
         ("CSig", 10, 0.01, "chance of +2 Grades"), ("CMaster", 5, 0.05, "level 1 = +1 Grade on every dish; levels 2-5 = this chance each of one more")]
DL = ["# SkyyCooking %s - cooking.properties (written on first run; comments must stay on their own lines)" % VERSION,
      "# Cooking Bench crafts give graded dishes and Cooking XP (sent to SkyySkills 0.4 through skill:fn:addxp).",
      "enabled=true",
      "# Grade = floor(Cooking level / 10) (max 10) + Cooking skill tree (SkyyTrees). The x2 at Grade 5 / x4 at Grade 10 numbers are baked",
      "# into the generated assets. maxGrade can only LOWER the cap: the jar has assets for Grades 1-%d; a higher value is read as %d." % (GEN_MAX, GEN_MAX),
      "maxGrade=%d" % GEN_MAX,
      "# true = creative-mode crafts get Grades and XP too (default: creative = plain food, no XP)",
      "creativeGrades=false",
      "# multiplies every Cooking XP award (SkyySkills' own global multiplier applies on top)",
      "xpMultiplier=1.0",
      "# safety net: base Cooking XP per player per minute (counted before xpMultiplier); 0 = off. The dish is always given.",
      "maxXpPerMinute=%d" % MAX_PER_MIN,
      "# chat lines for tree bonuses and a new Grade",
      "messages=true",
      "# dishes that come out graded (must be dishes this jar generated assets for; others always come out plain)",
      "graded=" + ",".join(DISHES),
      "# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). Pace (decision 2):",
      "# the meat-pie route reaches Cooking 50 in about %.0f focused hours, like Alchemy 50. A dish pays %d%% of the raw gathering in its" % (HOURS_50, int(DISH_SHARE * 100)),
      "# whole ingredient chain x %d per item (x%.2f for pies and Caesar salad, which need recipe knowledge); an ingredient craft pays %d%% of its own inputs." % (int(K_XP), KNOW_BONUS, int(ING_SHARE * 100)),
      "xp.default=%d" % XP_DEFAULT]
for k in sorted(XP):
    DL.append("xp.%s=%d" % (k, XP[k]))
DL.append("# Cooking skill tree (SkyyTrees node levels, bridge tree:fn:level): value per node level. Max levels: " +
          ", ".join("%s %d" % (n[0], n[1]) for n in NODES))
for nid, mx, per, what in NODES:
    DL.append("# %s: %s" % (nid, what))
    DL.append("tree.%s.per=%s" % (nid, repr(per)))
DEFAULTS_TEXT = "\n".join(DL) + "\n"

# =====================================================================================================================
# JAVA CLASSES (dependency order: every method exists before any caller is compiled)
# =====================================================================================================================
def jstr_arr(lst): return "new String[] { " + ", ".join(json.dumps(x) for x in lst) + " }"
def jint_arr(lst): return "new int[] { " + ", ".join(str(int(x)) for x in lst) + " }"
def jdbl_arr(lst): return "new double[] { " + ", ".join(repr(float(x)) for x in lst) + " }"
def jlong_arr(lst): return "new long[] { " + ", ".join("%dL" % int(x) for x in lst) + " }"

cfg  = pool.makeClass(PKG + ".CookCfg")
ck   = pool.makeClass(PKG + ".Cook")
xpt  = pool.makeClass(PKG + ".CookXpTask")
csy  = pool.makeClass(PKG + ".CookSys", pool.get(EES))
gfn  = pool.makeClass(PKG + ".CookGradeFn")
ofn  = pool.makeClass(PKG + ".CookOutFn")
sfn  = pool.makeClass(PKG + ".CookStatsFn")
gcmd = pool.makeClass(PKG + ".CookGiveCmd", pool.get(APC))
rcmd = pool.makeClass(PKG + ".CookReloadCmd", pool.get(APC))
acmd = pool.makeClass(PKG + ".CookAdminCmd", pool.get(APC))
ccmd = pool.makeClass(PKG + ".CookingCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyCookingPlugin", pool.get(JP))

def F(cls, decl): cls.addField(CtField.make(decl, cls))
def Mk(cls, src): cls.addMethod(CtNewMethod.make(jsrc(src), cls))
def Ct(cls, src): cls.addConstructor(CtNewConstructor.make(jsrc(src), cls))

# ================= CookCfg: cooking.properties + build-time constants =================
F(cfg, "public static %s LOG;" % LOG)
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static final int GEN_MAX = %d;" % GEN_MAX)
F(cfg, "public static final String[] DISHES = %s;" % jstr_arr(DISHES))
F(cfg, "public static final int[] TIER = %s;" % jint_arr([DISH_TIER[d] for d in DISHES]))
F(cfg, "public static final String[] NAMES = %s;" % jstr_arr([DISH_NAME[d] for d in DISHES]))
F(cfg, "public static final String[] INGR = %s;" % jstr_arr(INGREDIENTS))
F(cfg, "public static final String[] NODES = %s;" % jstr_arr([n[0] for n in NODES]))
F(cfg, "public static final int[] NODE_MAX = %s;" % jint_arr([n[1] for n in NODES]))
F(cfg, "public static final double[] NODE_DEF = %s;" % jdbl_arr([n[2] for n in NODES]))
F(cfg, "public static final double[] SF = %s;" % jdbl_arr([round(SF(g), 4) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final double[] DF = %s;" % jdbl_arr([round(DF(g), 4) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final String[] XP_IDS = %s;" % jstr_arr(sorted(XP)))
F(cfg, "public static final long[] XP_VALS = %s;" % jlong_arr([XP[k] for k in sorted(XP)]))
F(cfg, "public static final long DEF_XP_DEFAULT = %dL;" % XP_DEFAULT)
F(cfg, "public static final long DEF_MAX_PER_MIN = %dL;" % MAX_PER_MIN)
F(cfg, "public static final String DEFAULTS = %s;" % json.dumps(DEFAULTS_TEXT))
F(cfg, "public static volatile boolean ENABLED = true;")
F(cfg, "public static volatile int MAX_GRADE = %d;" % GEN_MAX)
F(cfg, "public static volatile boolean CREATIVE = false;")
F(cfg, "public static volatile double XP_MULT = 1.0;")
F(cfg, "public static volatile long MAX_PER_MIN = %dL;" % MAX_PER_MIN)
F(cfg, "public static volatile boolean MESSAGES = true;")
F(cfg, "public static volatile long XP_DEFAULT = %dL;" % XP_DEFAULT)
F(cfg, "public static volatile java.util.HashMap XP = new java.util.HashMap();")
F(cfg, "public static volatile java.util.HashSet GRADED = new java.util.HashSet();")
F(cfg, "public static volatile double[] PER = %s;" % jdbl_arr([n[2] for n in NODES]))
F(cfg, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
F(cfg, "public static final java.util.concurrent.ConcurrentHashMap EVERY = new java.util.concurrent.ConcurrentHashMap();")
Mk(cfg, """
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCooking] " + msg); } catch (Throwable t) { }
}""")
Mk(cfg, """
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyCooking] " + msg); } catch (Throwable t) { }
}""")
Mk(cfg, """
public static void once(String key, String msg) {
  if (ONCE.putIfAbsent(key, Boolean.TRUE) == null) warn(msg);
}""")
Mk(cfg, """
public static void every(String key, long ms, String msg) {
  long now = System.currentTimeMillis();
  Long l = (Long) EVERY.get(key);
  if (l != null && now - l.longValue() < ms) return;
  EVERY.put(key, Long.valueOf(now));
  warn(msg);
}""")
Mk(cfg, """
public static double dbl(java.util.Properties p, String k, double d) {
  try { String v = p.getProperty(k); if (v == null) return d; double x = Double.parseDouble(v.trim()); if (Double.isNaN(x) || Double.isInfinite(x)) return d; return x; } catch (Throwable t) { return d; }
}""")
Mk(cfg, """
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
Mk(cfg, """
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim();
  if (v.equalsIgnoreCase("true")) return true;
  if (v.equalsIgnoreCase("false")) return false;
  return d;
}""")
Mk(cfg, """
public static int dishIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < DISHES.length; i++) if (DISHES[i].equals(id)) return i;
  return -1;
}""")
# tier of a dish that comes out GRADED right now (0 = never graded: not generated or removed from graded=)
Mk(cfg, """
public static int tierOf(String id) {
  int i = dishIndex(id);
  if (i < 0) return 0;
  if (!GRADED.contains(id)) return 0;
  return TIER[i];
}""")
Mk(cfg, """
public static boolean isIngredient(String id) {
  if (id == null) return false;
  for (int i = 0; i < INGR.length; i++) if (INGR[i].equals(id)) return true;
  return false;
}""")
Mk(cfg, """
public static String nameOf(String id) {
  if (id == null) return "?";
  int i = dishIndex(id);
  if (i >= 0) return NAMES[i];
  String s = id;
  if (s.startsWith("Skyy_Cook_")) s = s.substring(10);
  if (s.startsWith("Ingredient_")) s = s.substring(11);
  if (s.startsWith("Food_")) s = s.substring(5);
  return s.replace('_', ' ');
}""")
Mk(cfg, """
public static void fillDefaults(java.util.HashMap xp, java.util.HashSet gr) {
  for (int i = 0; i < XP_IDS.length; i++) xp.put(XP_IDS[i], Long.valueOf(XP_VALS[i]));
  for (int i = 0; i < DISHES.length; i++) gr.add(DISHES[i]);
}""")
Mk(cfg, """
public static synchronized String load() {
  int bad = 0;
  java.util.HashMap xp = new java.util.HashMap();
  java.util.HashSet gr = new java.util.HashSet();
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    ENABLED = bool(p, "enabled", true);
    long mg = lng(p, "maxGrade", (long) GEN_MAX);
    if (mg < 0L) mg = 0L;
    if (mg > (long) GEN_MAX) { warn("maxGrade=" + mg + " is above the " + GEN_MAX + " Grades this jar has assets for - using " + GEN_MAX); mg = (long) GEN_MAX; }
    MAX_GRADE = (int) mg;
    CREATIVE = bool(p, "creativeGrades", false);
    double m = dbl(p, "xpMultiplier", 1.0);
    XP_MULT = m < 0.0 ? 0.0 : m;
    long cap = lng(p, "maxXpPerMinute", DEF_MAX_PER_MIN);
    MAX_PER_MIN = cap < 0L ? 0L : cap;
    MESSAGES = bool(p, "messages", true);
    long xd = lng(p, "xp.default", DEF_XP_DEFAULT);
    XP_DEFAULT = xd < 0L ? 0L : xd;
    for (int i = 0; i < XP_IDS.length; i++) xp.put(XP_IDS[i], Long.valueOf(XP_VALS[i]));
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {
      String k = String.valueOf(en.nextElement()).trim();
      if (!k.startsWith("xp.") || k.equals("xp.default") || k.length() <= 3) continue;
      try {
        long v = Long.parseLong(p.getProperty(k).trim());
        if (v < 0L) v = 0L;
        xp.put(k.substring(3), Long.valueOf(v));
      } catch (Throwable t) { bad++; warn("bad line " + k + "=" + p.getProperty(k) + " (want a whole number)"); }
    }
    String gl = p.getProperty("graded");
    if (gl == null) { for (int i = 0; i < DISHES.length; i++) gr.add(DISHES[i]); }
    else {
      String[] parts = gl.split(",");
      for (int i = 0; i < parts.length; i++) {
        String id = parts[i].trim();
        if (id.length() == 0) continue;
        if (dishIndex(id) >= 0) gr.add(id);
        else { bad++; warn("graded: " + id + " has no generated Grade assets in this jar - ignored"); }
      }
    }
    double[] per = new double[NODES.length];
    for (int i = 0; i < NODES.length; i++) {
      double v = dbl(p, "tree." + NODES[i] + ".per", NODE_DEF[i]);
      if (v < 0.0) v = 0.0;
      if (v > 1.0) v = 1.0;
      per[i] = v;
    }
    XP = xp; GRADED = gr; PER = per;
    return (ENABLED ? "on" : "OFF") + ", " + gr.size() + " graded dishes, max Grade " + MAX_GRADE + ", " + xp.size() + " XP keys, xpMultiplier " + XP_MULT + ", cap " + MAX_PER_MIN + "/min" + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");
  } catch (Throwable t) {
    warn("could not load cooking.properties (using the built-in defaults): " + t);
    java.util.HashMap dx = new java.util.HashMap();
    java.util.HashSet dg = new java.util.HashSet();
    fillDefaults(dx, dg);
    XP = dx; GRADED = dg;
    return "load failed, defaults in use: " + t;
  }
}""")
Mk(cfg, """
public static long xpFor(String out) {
  if (out == null) return 0L;
  Long v = (Long) XP.get(out);
  if (v != null) return v.longValue();
  if (ONCE.putIfAbsent("xp:" + out, Boolean.TRUE) == null) info("no xp." + out + " line - paying xp.default=" + XP_DEFAULT + " per craft (add the line to cooking.properties to change it)");
  return XP_DEFAULT;
}""")

# ================= Cook: grading, tree, giving, XP =================
F(ck, "public static final long CHUNK = 400000L;")
F(ck, "public static final java.util.concurrent.ConcurrentHashMap EXISTS = new java.util.concurrent.ConcurrentHashMap();")
F(ck, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
F(ck, "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();")
F(ck, "public static final java.util.HashMap RATE = new java.util.HashMap();")
Mk(ck, """
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# the contract helper, verbatim (tools/PROFILES-CONTRACT.md)
Mk(ck, """
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
Mk(ck, """
public static boolean busy(java.util.UUID u) {
  try { return bridge().get("profile:busy:" + u.toString()) != null; } catch (Throwable t) { return false; }
}""")
# Cooking level from SkyySkills 0.4; -1 = no SkyySkills (then: plain food, no XP)
Mk(ck, """
public static int level(java.util.UUID u) {
  try {
    Object f = bridge().get("skill:fn:level");
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking" });
    if (!(r instanceof Number)) return 0;
    int v = ((Number) r).intValue();
    if (v < 0) v = 0;
    if (v > 1000) v = 1000;
    return v;
  } catch (Throwable t) { return 0; }
}""")
Mk(ck, """
public static int baseGrade(int level) {
  if (level <= 0) return 0;
  int g = level / 10;
  if (g > 10) g = 10;
  return g;
}""")
Mk(ck, """
public static int clampGrade(int g) {
  int m = @PKG@.CookCfg.MAX_GRADE;
  if (m > @PKG@.CookCfg.GEN_MAX) m = @PKG@.CookCfg.GEN_MAX;
  if (g > m) g = m;
  if (g < 0) g = 0;
  return g;
}""")
# Cooking tree node levels from SkyyTrees (bridge tree:fn:level (UUID, "Cooking.<Id>") -> Integer), clamped to each node's max
Mk(ck, """
public static int[] tree(java.util.UUID u) {
  int n = @PKG@.CookCfg.NODES.length;
  int[] t = new int[n];
  Object f = null;
  try { f = bridge().get("tree:fn:level"); } catch (Throwable x) { f = null; }
  if (!(f instanceof java.util.function.Function)) return t;
  for (int i = 0; i < n; i++) {
    try {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking." + @PKG@.CookCfg.NODES[i] });
      if (r instanceof Number) {
        int v = ((Number) r).intValue();
        if (v < 0) v = 0;
        if (v > @PKG@.CookCfg.NODE_MAX[i]) v = @PKG@.CookCfg.NODE_MAX[i];
        t[i] = v;
      }
    } catch (Throwable x) { }
  }
  return t;
}""")
Mk(ck, """
public static boolean anyTree(int[] t) {
  for (int i = 0; i < t.length; i++) if (t[i] > 0) return true;
  return false;
}""")
Mk(ck, """
public static int guaranteed(java.util.UUID u) {
  int lv = level(u);
  if (lv < 0) return 0;
  int[] t = tree(u);
  return clampGrade(baseGrade(lv) + (t[9] >= 1 ? 1 : 0));
}""")
Mk(ck, """
public static double rnd() {
  return java.util.concurrent.ThreadLocalRandom.current().nextDouble();
}""")
# per-node chance fractions. SkyyTrees 0.1 publishes tree:fn:bonus (same argument -> Double = level x per from ITS trees.properties;
# Master Chef = (level - 1) x per), so Skyy tunes the numbers in one place; without it: level x tree.<Id>.per of cooking.properties.
Mk(ck, """
public static double[] chances(java.util.UUID u, int[] t) {
  int n = t.length;
  double[] c = new double[n];
  double[] p = @PKG@.CookCfg.PER;
  Object f = null;
  try { f = bridge().get("tree:fn:bonus"); } catch (Throwable x) { f = null; }
  for (int i = 0; i < n; i++) {
    double v = 0.0;
    if (t[i] <= 0) { c[i] = 0.0; continue; }
    boolean got = false;
    if (f instanceof java.util.function.Function) {
      try {
        Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking." + @PKG@.CookCfg.NODES[i] });
        if (r instanceof Number) { v = ((Number) r).doubleValue(); got = true; }
      } catch (Throwable x) { got = false; }
    }
    if (!got) v = (i == 9 ? (t[i] - 1) : t[i]) * p[i];
    if (Double.isNaN(v) || v < 0.0) v = 0.0;
    if (v > 1.0) v = 1.0;
    c[i] = v;
  }
  return c;
}""")
# combined +1 Grade chance for a dish tier: Gourmet + Gourmet II + the tier's mastery + Master Chef levels 2-5 (capped at 100 %)
Mk(ck, """
public static double upChance(int tier, double[] c) {
  double v = c[0] + c[7] + c[9];
  if (tier == 1) v = v + c[3];
  else if (tier == 2) v = v + c[4];
  else if (tier == 3) v = v + c[5];
  if (v > 1.0) v = 1.0;
  return v;
}""")
Mk(ck, """
public static double sigChance(double[] c) {
  if (c[8] > 1.0) return 1.0;
  return c[8];
}""")
# one roll per dish (Cooking spec 7.2): g = level/10 (max 10) + Master Chef; +1 on the combined chance, or +2 on Signature Dish
Mk(ck, """
public static int roll(int level, int tier, int[] t, double[] c, int[] bonus) {
  int g = baseGrade(level) + (t[9] >= 1 ? 1 : 0);
  int b = 0;
  double p1 = upChance(tier, c);
  if (p1 > 0.0 && rnd() < p1) b = 1;
  double p2 = sigChance(c);
  if (p2 > 0.0 && rnd() < p2) b = 2;
  bonus[0] = b;
  return clampGrade(g + b);
}""")
Mk(ck, """
public static String gradedId(String dish, int g) {
  return "Skyy_Cook_" + dish + "_G" + g;
}""")
# an id is only ever handed out once the live item asset map has it (asset pack failed = plain food, never an Invalid Item)
Mk(ck, """
public static boolean exists(String id) {
  if (id == null) return false;
  if (EXISTS.containsKey(id)) return true;
  boolean ok = false;
  try { ok = @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { ok = false; }
  if (ok) EXISTS.put(id, Boolean.TRUE);
  else @PKG@.CookCfg.once("asset:" + id, "item asset " + id + " is not loaded - handing out the plain item instead (did the SkyyCooking asset pack load? check the server log for asset errors)");
  return ok;
}""")
Mk(ck, """
public static boolean isCooking(@CRR@ rc) {
  if (rc == null) return false;
  @BRQ@[] b = rc.getBenchRequirement();
  if (b == null) return false;
  for (int i = 0; i < b.length; i++) if (b[i] != null && "Cookingbench".equals(b[i].id)) return true;
  return false;
}""")
Mk(ck, """
public static String outId(@CRR@ rc) {
  @MQ@ po = rc.getPrimaryOutput();
  if (po == null) return null;
  return po.getItemId();
}""")
Mk(ck, """
public static int outQty(@CRR@ rc) {
  @MQ@ po = rc.getPrimaryOutput();
  if (po == null) return 1;
  int q = po.getQuantity();
  return q < 1 ? 1 : q;
}""")
Mk(ck, """
public static boolean creative(@ST@ st, @REF@ r) {
  if (@PKG@.CookCfg.CREATIVE) return false;
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p != null && p.getGameMode() == @GM@.Creative;
  } catch (Throwable t) { return false; }
}""")
# the same check for a caller that only has the UUID (cook:fn:out): 1 = creative, 0 = not (or creativeGrades=true), -1 = unknown
# (offline, no live entity, or not called on that player's world thread - components are only read on the world thread)
Mk(ck, """
public static int creativeOf(java.util.UUID u) {
  if (@PKG@.CookCfg.CREATIVE) return 0;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return -1;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return -1;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return -1;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return -1;
    return p.getGameMode() == @GM@.Creative ? 1 : 0;
  } catch (Throwable t) { return -1; }
}""")
# Frugal: one random ITEM-id input (never a resource type such as Fuel / Meats, never a '*' state wildcard)
Mk(ck, """
public static String frugalPick(@CRR@ rc) {
  @MQ@[] in = rc.getInput();
  if (in == null) return null;
  java.util.ArrayList c = new java.util.ArrayList();
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null) continue;
    String id = in[i].getItemId();
    if (id == null || id.length() == 0 || id.startsWith("*") || in[i].getResourceTypeId() != null) continue;
    if (exists(id)) c.add(id);
  }
  if (c.isEmpty()) return null;
  int k = (int) (rnd() * c.size());
  if (k >= c.size()) k = c.size() - 1;
  return (String) c.get(k);
}""")
# The plan for `units` finished crafts of rc by u. null = nothing to change (vanilla output, no tree extra).
# [0] = full replacement output List (then the caller cancels the Post) or null, [1] = extra stacks List or null (given NEXT TO the
# output), [2] = chat note or null, [3] = Integer Grade of the last dish.
Mk(ck, """
public static Object[] plan(java.util.UUID u, @CRR@ rc, int units) {
  if (!@PKG@.CookCfg.ENABLED || rc == null) return null;
  int lv = level(u);
  if (lv < 0) return null;
  String out = outId(rc);
  if (out == null) return null;
  int tier = @PKG@.CookCfg.tierOf(out);
  boolean ingr = @PKG@.CookCfg.isIngredient(out);
  int[] t = tree(u);
  boolean tr = anyTree(t);
  if (!tr && (tier == 0 || baseGrade(lv) == 0)) return null;
  double[] ch = new double[t.length];
  if (tr) ch = chances(u, t);
  java.util.ArrayList all = new java.util.ArrayList();
  java.util.ArrayList ex = new java.util.ArrayList();
  boolean changed = false;
  String note = null;
  int lastG = 0;
  int[] bonus = new int[1];
  for (int k = 0; k < units; k++) {
    java.util.List outs = @CRM@.getOutputItemStacks(rc, 1);
    int g = 0;
    bonus[0] = 0;
    if (tier > 0) g = roll(lv, tier, t, ch, bonus);
    lastG = g;
    String dishGiven = null;
    for (int i = 0; outs != null && i < outs.size(); i++) {
      @IS@ s = (@IS@) outs.get(i);
      if (s == null || s.getQuantity() <= 0) continue;
      String id = s.getItemId();
      if (g > 0 && @PKG@.CookCfg.tierOf(id) > 0) {
        String gid = gradedId(id, g);
        if (exists(gid)) { s = new @IS@(gid, s.getQuantity()); changed = true; }
      }
      if (dishGiven == null && id.equals(out)) dishGiven = s.getItemId();
      all.add(s);
    }
    if (bonus[0] > 0 && dishGiven != null && !dishGiven.equals(out)) note = (bonus[0] == 2 ? "Signature Dish! " : "Gourmet! ") + @PKG@.CookCfg.nameOf(out) + " came out Grade " + g;
    if (tier > 0 && ch[1] > 0.0 && dishGiven != null && rnd() < ch[1]) {
      ex.add(new @IS@(dishGiven, outQty(rc)));
      note = "Batch Cook! +" + outQty(rc) + " " + @PKG@.CookCfg.nameOf(out) + (g > 0 ? " (Grade " + g + ")" : "");
    }
    if (ingr && ch[6] > 0.0 && rnd() < ch[6]) {
      ex.add(new @IS@(out, outQty(rc)));
      note = "Prep Cook! double " + @PKG@.CookCfg.nameOf(out);
    }
    if (ch[2] > 0.0 && rnd() < ch[2]) {
      String fid = frugalPick(rc);
      if (fid != null) { ex.add(new @IS@(fid, 1)); note = "Frugal! got 1 " + @PKG@.CookCfg.nameOf(fid) + " back"; }
    }
  }
  if (!changed && ex.isEmpty()) return null;
  Object rep = null;
  if (changed) rep = all;
  Object ext = null;
  if (!ex.isEmpty()) ext = ex;
  return new Object[] { rep, ext, note, Integer.valueOf(lastG) };
}""")
# hand stacks out exactly like vanilla giveOutput (addOrDropItemStack with the caller's accessor), storage first
Mk(ck, """
public static void give(@CAC@ acc, @REF@ r, @IC@ c, java.util.List l) {
  if (l == null) return;
  for (int i = 0; i < l.size(); i++) {
    @IS@ s = (@IS@) l.get(i);
    if (s == null || s.getQuantity() <= 0) continue;
    @SIC@.addOrDropItemStack(acc, r, c, s);
  }
}""")
Mk(ck, """
public static synchronized boolean allowXp(java.util.UUID u, long base) {
  long cap = @PKG@.CookCfg.MAX_PER_MIN;
  if (cap <= 0L) return true;
  long now = System.currentTimeMillis();
  long[] w = (long[]) RATE.get(u);
  if (w == null) { w = new long[] { now, 0L, 0L }; RATE.put(u, w); }
  if (now - w[0] >= 60000L) { w[0] = now; w[1] = 0L; }
  if (w[1] + base > cap) {
    if (now - w[2] >= 60000L) { w[2] = now; @PKG@.CookCfg.warn("Cooking XP cap reached for " + u + " (" + cap + " base XP per minute, maxXpPerMinute) - XP of this craft dropped, the dish was still given"); }
    return false;
  }
  w[1] = w[1] + base;
  return true;
}""")
Mk(ck, """
public static long sendXp(java.util.UUID u, long amt, String src, String key) {
  if (amt <= 0L) return 0L;
  Object f = bridge().get("skill:fn:addxp");
  if (!(f instanceof java.util.function.Function)) {
    @PKG@.CookCfg.once("noaddxp", "SkyySkills' XP bridge skill:fn:addxp is missing - cooking pays no XP (needs SkyySkills 0.4 or newer)");
    return 0L;
  }
  long left = amt;
  long sent = 0L;
  int guard = 0;
  while (left > 0L && guard < 64) {
    guard++;
    long c = left > CHUNK ? CHUNK : left;
    Object ok = null;
    try { ok = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking", Long.valueOf(c), src, key }); } catch (Throwable t) { ok = null; }
    if (!Boolean.TRUE.equals(ok)) {
      @PKG@.CookCfg.every("refused", 60000L, "SkyySkills refused " + c + " Cooking XP for " + u + " (" + src + ") - is Cooking in SkyySkills' bridge.addxp.skills, or was its per-minute bridge cap hit?");
      return sent;
    }
    sent = sent + c;
    left = left - c;
  }
  return sent;
}""")
Mk(ck, """
public static void tell(@PR@ pr, String msg, boolean force) {
  if (pr == null || msg == null || !@PKG@.CookCfg.MESSAGES) return;
  long now = System.currentTimeMillis();
  Long l = (Long) LAST.get(pr.getUuid());
  if (!force && l != null && now - l.longValue() < 2500L) return;
  LAST.put(pr.getUuid(), Long.valueOf(now));
  pr.sendMessage(@MSG@.raw("[Cooking] " + msg).color("#ffb070"));
}""")
Mk(ck, """
public static String x2(double v) {
  long c = Math.round(v * 100.0);
  long f = c % 100L;
  return (c / 100L) + "." + (f < 10L ? "0" : "") + f;
}""")
Mk(ck, """
public static String pc(double v) {
  long c = Math.round(v * 1000.0);
  long f = c % 10L;
  return (c / 10L) + (f == 0L ? "" : "." + f) + "%";
}""")

# ================= CookXpTask: the deferred award (world thread, after every other system saw the Post) =================
xpt.addInterface(pool.get("java.lang.Runnable"))
for _d in ("public %s ev;" % CRE, "public java.util.UUID u;", "public String key;", "public String out;", "public long base;",
           "public boolean gave;", "public String note;", "public int grade;"):
    F(xpt, _d)
Ct(xpt, """
public CookXpTask(@CRE@ ev, java.util.UUID u, String key, String out, long base, boolean gave, String note, int grade) {
  this.ev = ev; this.u = u; this.key = key; this.out = out; this.base = base; this.gave = gave; this.note = note; this.grade = grade;
}""")
Mk(xpt, """
public void run() {
  try {
    if (this.ev != null && this.ev.isCancelled() && !this.gave) return;
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (!this.key.equals(@PKG@.Cook.pkey(this.u))) return;
    Integer told = (Integer) @PKG@.Cook.TOLD.get(this.u);
    if (this.gave && this.grade > 0 && (told == null || told.intValue() < this.grade)) {
      @PKG@.Cook.TOLD.put(this.u, Integer.valueOf(this.grade));
      @PKG@.Cook.tell(pr, "Your food now comes out Grade " + this.grade + " - heal and buffs x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[this.grade]) + " stronger, buffs last x" + @PKG@.Cook.x2(@PKG@.CookCfg.DF[this.grade]) + " longer. /cooking for details.", true);
    } else if (this.note != null) @PKG@.Cook.tell(pr, this.note, false);
    if (this.base <= 0L) return;
    if (!@PKG@.Cook.allowXp(this.u, this.base)) return;
    long amt = Math.round(this.base * @PKG@.CookCfg.XP_MULT);
    @PKG@.Cook.sendXp(this.u, amt, "cook:" + this.out, this.key);
  } catch (Throwable t) { @PKG@.CookCfg.warn("cooking XP task failed: " + t); }
}""")

# ================= CookSys: THE craft hook (EntityEventSystem on CraftRecipeEvent$Post; the mod's only system class) =================
Ct(csy, "public CookSys() { super(@CRP@.class); }")
Mk(csy, """
public @QRY@ getQuery() {
  return com.hypixel.hytale.component.Archetype.empty();
}""")
Mk(csy, """
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!@PKG@.CookCfg.ENABLED) return;
    @CRE@ e = (@CRE@) ev;
    @CRR@ rc = e.getCraftedRecipe();
    if (rc == null || !@PKG@.Cook.isCooking(rc)) return;
    if (e.isCancelled()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    if (@PKG@.Cook.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    if (@PKG@.Cook.busy(u)) return;
    int units = 1;
    if (rc.getTimeSeconds() <= 0.0f) units = Math.max(1, e.getQuantity());
    if (units > 10000) units = 10000;
    String key = @PKG@.Cook.pkey(u);
    String out = @PKG@.Cook.outId(rc);
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    Object[] plan = null;
    if (p != null) plan = @PKG@.Cook.plan(u, rc, units);
    boolean gave = false;
    String note = null;
    int grade = 0;
    if (plan != null) {
      @IC@ c = p.getInventory().getCombinedStorageHotbarBackpack();
      if (plan[0] != null) {
        e.setCancelled(true);
        @PKG@.Cook.give(buf, r, c, (java.util.List) plan[0]);
        gave = true;
      }
      if (plan[1] != null) @PKG@.Cook.give(buf, r, c, (java.util.List) plan[1]);
      note = (String) plan[2];
      grade = ((Integer) plan[3]).intValue();
    }
    long base = @PKG@.CookCfg.xpFor(out) * (long) units;
    w.execute(new @PKG@.CookXpTask(e, u, key, out, base, gave, note, grade));
  } catch (Throwable t) { @PKG@.CookCfg.every("sys", 30000L, "CookSys failed (vanilla output kept unless the Post was already cancelled): " + t); }
}""")

# ================= bridge functions =================
gfn.addInterface(pool.get("java.util.function.Function"))
Ct(gfn, "public CookGradeFn() { }")
Mk(gfn, """
public Object apply(Object arg) {
  try {
    Object a = arg;
    if (a instanceof Object[]) a = ((Object[]) a)[0];
    if (!(a instanceof java.util.UUID)) return Integer.valueOf(0);
    return Integer.valueOf(@PKG@.Cook.guaranteed((java.util.UUID) a));
  } catch (Throwable t) { return Integer.valueOf(0); }
}""")
ofn.addInterface(pool.get("java.util.function.Function"))
Ct(ofn, "public CookOutFn() { }")
Mk(ofn, """
public Object apply(Object arg) {
  try {
    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];
    @CRR@ rc = (@CRR@) @CRR@.getAssetMap().getAsset(String.valueOf(a[1]));
    if (rc == null || !@PKG@.Cook.isCooking(rc)) return null;
    int n = ((Number) a[2]).intValue();
    if (n < 1) n = 1;
    if (n > 10000) n = 10000;
    String key = @PKG@.Cook.pkey(u);
    if (a.length > 3 && a[3] != null && !String.valueOf(a[3]).equals(key)) return null;
    java.util.ArrayList res = new java.util.ArrayList();
    boolean plain = !@PKG@.CookCfg.ENABLED || @PKG@.Cook.busy(u);
    if (!plain && !@PKG@.CookCfg.CREATIVE) {
      boolean declared = a.length > 4 && a[4] instanceof Boolean;
      if (declared && ((Boolean) a[4]).booleanValue()) plain = true;
      else {
        int cm = @PKG@.Cook.creativeOf(u);
        if (cm == 1) plain = true;
        else if (cm < 0 && !declared) {
          plain = true;
          @PKG@.CookCfg.once("outfn:mode", "cook:fn:out: cannot read the game mode of " + u + " (not on that player's world thread?) and the caller passed no creative flag - plain output and no XP. Pass Object[]{UUID, recipeId, crafts, expectKey, Boolean creative}.");
        }
      }
    }
    if (plain) { res.addAll(@CRM@.getOutputItemStacks(rc, n)); return res; }
    Object[] plan = @PKG@.Cook.plan(u, rc, n);
    if (plan != null && plan[0] != null) res.addAll((java.util.List) plan[0]);
    else res.addAll(@CRM@.getOutputItemStacks(rc, n));
    if (plan != null && plan[1] != null) res.addAll((java.util.List) plan[1]);
    String out = @PKG@.Cook.outId(rc);
    long base = @PKG@.CookCfg.xpFor(out) * (long) n;
    if (base > 0L && @PKG@.Cook.allowXp(u, base)) @PKG@.Cook.sendXp(u, Math.round(base * @PKG@.CookCfg.XP_MULT), "cook:" + out + ":bridge", key);
    return res;
  } catch (Throwable t) { @PKG@.CookCfg.every("outfn", 30000L, "cook:fn:out failed: " + t); return null; }
}""")

# skill:stats:Cooking (SkyySkills 0.4 Stats page hook): apply(Object[]{UUID, Integer level, Boolean next}) -> List of String (<= 5 lines,
# dashes instead of commas and colons like the rest of that page)
sfn.addInterface(pool.get("java.util.function.Function"))
Ct(sfn, "public CookStatsFn() { }")
Mk(sfn, """
public Object apply(Object arg) {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];
    int lv = ((Number) a[1]).intValue();
    boolean next = Boolean.TRUE.equals(a[2]);
    if (!@PKG@.CookCfg.ENABLED) { if (!next) out.add("Graded cooking is turned off on this server"); return out; }
    int[] t = @PKG@.Cook.tree(u);
    int m = 0;
    if (t[9] >= 1) m = 1;
    int base = @PKG@.Cook.baseGrade(lv);
    if (next) {
      int nl = lv + 1;
      if (nl % 10 == 0 && nl / 10 <= 10) {
        int ng = @PKG@.Cook.clampGrade(@PKG@.Cook.baseGrade(nl) + m);
        if (ng > @PKG@.Cook.clampGrade(base + m)) out.add("Grade " + ng + " food - heal and buffs x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[ng]) + " stronger and lasting x" + @PKG@.Cook.x2(@PKG@.CookCfg.DF[ng]) + " longer");
      }
      return out;
    }
    int g = @PKG@.Cook.clampGrade(base + m);
    out.add("Food you cook - Grade " + g + " - heal and buffs x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[g]) + " stronger - buffs last x" + @PKG@.Cook.x2(@PKG@.CookCfg.DF[g]) + " longer");
    if (base < 10) {
      int ng = @PKG@.Cook.clampGrade(base + 1 + m);
      if (ng > g) out.add("Next Grade - Grade " + ng + " x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[ng]) + " at Cooking " + ((base + 1) * 10));
    } else out.add("Grades 11 and 12 come only from the Cooking skill tree");
    if (@PKG@.Cook.anyTree(t)) {
      double[] c = @PKG@.Cook.chances(u, t);
      out.add("Skill tree - " + @PKG@.Cook.pc(@PKG@.Cook.upChance(3, c)) + " chance of +1 Grade on pies - " + @PKG@.Cook.pc(@PKG@.Cook.sigChance(c)) + " of +2 - " + @PKG@.Cook.pc(c[1]) + " extra dish - " + @PKG@.Cook.pc(c[2]) + " ingredient back");
    }
    if (!@PKG@.Cook.exists(@PKG@.Cook.gradedId(@PKG@.CookCfg.DISHES[3], 1))) out.add("WARNING - graded dish assets are not loaded - food comes out plain");
  } catch (Throwable t) { }
  return out;
}""")

# ================= commands =================
# /cookadmin give <dish> <grade>
F(gcmd, "public %s dishArg;" % RA)
F(gcmd, "public %s gradeArg;" % RA)
Ct(gcmd, """
public CookGiveCmd() {
  super("give", "(admin) Give 5 dishes of a Grade: /cookadmin give Food_Pie_Meat 5 (grade 0-12, 0 = plain)");
  this.dishArg = withRequiredArg("dish", "Food_Pie_Meat, pie_meat, Food_Bread, ... (the 15 graded dishes)", @ATY@.STRING);
  this.gradeArg = withRequiredArg("grade", "0-12", @ATY@.STRING);
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
}""")
Mk(gcmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyycooking.admin")) { pr.sendMessage(@MSG@.raw("[Cooking] no permission (skyycooking.admin)")); return; }
    String d = String.valueOf(ctx.get(this.dishArg)).trim();
    String dish = null;
    for (int i = 0; i < @PKG@.CookCfg.DISHES.length; i++) {
      String x = @PKG@.CookCfg.DISHES[i];
      if (x.equalsIgnoreCase(d) || x.equalsIgnoreCase("Food_" + d)) dish = x;
    }
    if (dish == null) {
      String all = "";
      for (int i = 0; i < @PKG@.CookCfg.DISHES.length; i++) all = all + (i > 0 ? ", " : "") + @PKG@.CookCfg.DISHES[i].substring(5);
      pr.sendMessage(@MSG@.raw("[Cooking] unknown dish '" + d + "'. Dishes: " + all));
      return;
    }
    int g = -1;
    try { g = Integer.parseInt(String.valueOf(ctx.get(this.gradeArg)).trim()); } catch (Throwable t) { g = -1; }
    if (g < 0 || g > @PKG@.CookCfg.GEN_MAX) { pr.sendMessage(@MSG@.raw("[Cooking] grade must be 0-" + @PKG@.CookCfg.GEN_MAX)); return; }
    String id = g == 0 ? dish : @PKG@.Cook.gradedId(dish, g);
    if (!@PKG@.Cook.exists(id)) { pr.sendMessage(@MSG@.raw("[Cooking] item " + id + " is not loaded (asset pack problem - see the server log)")); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    @SIC@.addOrDropItemStack(store, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, 5));
    pr.sendMessage(@MSG@.raw("[Cooking] gave 5 x " + id));
  } catch (Throwable t) { @PKG@.CookCfg.warn("/cookadmin give failed: " + t); pr.sendMessage(@MSG@.raw("[Cooking] give failed: " + t)); }
}""")
Ct(rcmd, """
public CookReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyCooking/cooking.properties");
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
}""")
Mk(rcmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (!pr.hasPermission("skyycooking.admin")) { pr.sendMessage(@MSG@.raw("[Cooking] no permission (skyycooking.admin)")); return; }
  @PKG@.Cook.EXISTS.clear();
  @PKG@.CookCfg.ONCE.clear();
  pr.sendMessage(@MSG@.raw("[Cooking] cooking.properties reloaded: " + @PKG@.CookCfg.load()));
}""")
Ct(acmd, """
public CookAdminCmd() {
  super("cookadmin", "(admin) SkyyCooking: /cookadmin give <dish> <grade>, /cookadmin reload");
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
  addSubCommand(new @PKG@.CookGiveCmd());
  addSubCommand(new @PKG@.CookReloadCmd());
}""")
Mk(acmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Cooking] /cookadmin give <dish> <grade>  (e.g. /cookadmin give pie_meat 5)  |  /cookadmin reload"));
}""")
Ct(ccmd, """
public CookingCmd() {
  super("cooking", "Your Cooking level, the Grade of the food you cook and your skill tree chances");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
Mk(ccmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    java.util.UUID u = pr.getUuid();
    if (!@PKG@.CookCfg.ENABLED) { pr.sendMessage(@MSG@.raw("[Cooking] graded cooking is turned off on this server (enabled=false).")); return; }
    int lv = @PKG@.Cook.level(u);
    if (lv < 0) { pr.sendMessage(@MSG@.raw("[Cooking] SkyySkills is not installed - food comes out plain (Grade 0) and cooking gives no XP.")); return; }
    int[] t = @PKG@.Cook.tree(u);
    int base = @PKG@.Cook.baseGrade(lv);
    int g = @PKG@.Cook.clampGrade(base + (t[9] >= 1 ? 1 : 0));
    pr.sendMessage(@MSG@.raw("[Cooking] Cooking " + lv + " - your food comes out Grade " + g + ": heal and buffs x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[g]) + " stronger, buffs last x" + @PKG@.Cook.x2(@PKG@.CookCfg.DF[g]) + " longer.").color("#ffb070"));
    if (base < 10 && base + 1 <= @PKG@.Cook.clampGrade(99)) {
      int ng = @PKG@.Cook.clampGrade(base + 1 + (t[9] >= 1 ? 1 : 0));
      pr.sendMessage(@MSG@.raw("[Cooking] Next: Grade " + ng + " (x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[ng]) + ") at Cooking " + ((base + 1) * 10) + "."));
    } else if (base >= 10) pr.sendMessage(@MSG@.raw("[Cooking] Grades 11 and 12 come only from the Cooking skill tree (SkyyTrees)."));
    if (@PKG@.Cook.anyTree(t)) {
      double[] c = @PKG@.Cook.chances(u, t);
      String s = "[Cooking] Skill tree - +1 Grade: T1 " + @PKG@.Cook.pc(@PKG@.Cook.upChance(1, c)) + " T2 " + @PKG@.Cook.pc(@PKG@.Cook.upChance(2, c)) + " T3 " + @PKG@.Cook.pc(@PKG@.Cook.upChance(3, c));
      s = s + " - +2 Grades " + @PKG@.Cook.pc(@PKG@.Cook.sigChance(c)) + " - extra dish " + @PKG@.Cook.pc(c[1]) + " - ingredient back " + @PKG@.Cook.pc(c[2]) + " - double ingredients " + @PKG@.Cook.pc(c[6]);
      if (t[9] >= 1) s = s + " - Master Chef +1 Grade";
      pr.sendMessage(@MSG@.raw(s));
    }
    pr.sendMessage(@MSG@.raw("[Cooking] Earn XP at a Cooking Bench (ingredients can come from your bags) - pies and Caesar salad pay the most. A placed Campfire gives plain food and no XP; its dishes are on the Cooking Bench too."));
    if (!@PKG@.Cook.exists(@PKG@.Cook.gradedId(@PKG@.CookCfg.DISHES[3], 1))) pr.sendMessage(@MSG@.raw("[Cooking] WARNING: the graded dish assets are not loaded - food comes out plain. Tell an admin (server log)."));
  } catch (Throwable t) { @PKG@.CookCfg.warn("/cooking failed: " + t); pr.sendMessage(@MSG@.raw("[Cooking] something went wrong - see the server log")); }
}""")

# ================= plugin =================
Ct(pl, "public SkyyCookingPlugin(@JPI@ init) { super(init); }")
Mk(pl, """
public void setup() {
  @PKG@.CookCfg.LOG = getLogger();
  @PKG@.CookCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCooking").resolve("cooking.properties");
  String s = @PKG@.CookCfg.load();
  getEntityStoreRegistry().registerSystem(new @PKG@.CookSys());
  getCommandRegistry().registerCommand(new @PKG@.CookingCmd());
  getCommandRegistry().registerCommand(new @PKG@.CookAdminCmd());
  java.util.Map b = @PKG@.Cook.bridge();
  b.put("cook:fn:grade", new @PKG@.CookGradeFn());
  b.put("cook:fn:out", new @PKG@.CookOutFn());
  b.put("cook:prefix", "Skyy_Cook_Food_");
  b.put("skill:stats:Cooking", new @PKG@.CookStatsFn());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCooking] @VERSION@ ready - Cooking Bench crafts give graded dishes (Grade = Cooking level / 10, x2 at 50, x4 at 100, Grades 11-12 from the SkyyTrees Cooking tree) and Cooking XP through SkyySkills; /cooking; config: " + s + "; SkyySkills " + (b.get("skill:fn:level") != null ? "found" : "not loaded yet (plain food and no XP without it)"));
}""")
Mk(pl, """
protected void shutdown() {
  try { java.util.Map b = @PKG@.Cook.bridge(); b.remove("cook:fn:grade"); b.remove("cook:fn:out"); b.remove("cook:prefix"); b.remove("skill:stats:Cooking"); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in (cfg, ck, xpt, csy, gfn, ofn, sfn, gcmd, rcmd, acmd, ccmd, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyCooking", VERSION, "SkyWynn Cooking: dishes cooked at the Cooking Bench come out graded by your Cooking level (SkyySkills) - Grade = level / 10, heal and buffs x2 stronger and longer at level 50, x4 at 100, Grades 11-12 from the SkyyTrees Cooking tree; the Campfire dishes can be cooked at the Cooking Bench too; Cooking XP goes to SkyySkills. /cooking. Zero dependencies (without SkyySkills food stays plain).", PKG + ".SkyyCookingPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCooking.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCooking" % VERSION, disable_prefix="Skyy:")
