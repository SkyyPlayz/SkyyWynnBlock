"""Derive SkyySkills/build_skyyskills_0.4.66.py from the GENERATED SkyySkills 0.4.65 (build_skyyskills_0.4.65.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_65_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.65 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_66_patch.py   then   python SkyySkills/build_skyyskills_0.4.66.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.66.py
Round ranch6 = starter archipelago R6 (research/Starter-Archipelago-Spec.md section 16 row R6 + section 11; docs/answered/world.md 2026-10-23
ARCHIPELAGO LAYOUT APPROVED: "Ranching XP from eggs / wool / milk / taming yes").
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.66 (2026-10-25) = RANCHING XP FOR TAMING, CAPTURE CRATES AND MILKING (starter archipelago R6, research/Starter-Archipelago-Spec.md
  16 row R6 + 11; Skyy's default 2026-10-23 "Ranching XP from eggs / wool / milk / taming yes"; Skyy: "(tbh i have no clue how the animal
  taming or farming works in Hytale yet. so have the quests walk you through it.)").
  EGGS + WOOL (+ feathers): ALREADY PAID since 0.4.37 - chickens lay Food_Egg as a ground item (Template ProduceItem = an NPC DropItem) and
    shears drop 1-3 Ingredient_Fabric_Scrap_Wool / 1-2 Ingredient_Feathers_Light on the ground (HarvestDropList, NPC DropItem): the
    pickup pays ranching.items (egg 30, wool 30, feathers 10) through RanchPickSys, with the drop ledger (items a player dropped pay 0).
    Unchanged. Eggs a Coop_Chicken collects go straight into the inventory (UseCoopInteraction - no pickup, no event): still not paid.
  ENGINE FACTS (HytaleServer.jar + Assets.zip, read at EVERY build - any drift stops the build):
    T1 taming = the NPC action Role (Template_Animal_Neutral: fed the AttractiveItemSet food -> RemoveHeldItem 1 + Role TameRoleChange):
       RoleChangeSystem.tick REMOVES the NPC with RemoveReason.UNLOAD and re-adds the SAME holder (UUIDComponent kept) with AddReason.LOAD
       under the new role (Cow -> Tamed_Cow). No event names the player.
    T2 a Capture Crate (UseCaptureCrateInteraction.tick0) replaces the held crate with one carrying metadata CapturedEntity
       (CapturedNPCMetadata, npcNameKey = the NPC's role name) and THEN CommandBuffer.removeEntity(npc, RemoveReason.REMOVE); a dead NPC
       cannot be crated. Group Capture_Crate (IncludeRoles, "*X" = any role ending in X) = the roles a crate takes.
    T3 milking = the Tamed_Cow / Tamed_Mosshorn Harvest state (Template_Livestock, context Milk, needs Container_Bucket / Deco_Bucket in
       the main hand): Inventory RemoveHeldItem (InventoryHelper.removeItemInHand -> the hotbar's removeItemStackFromSlot on the ACTIVE
       slot) then Inventory Add of the filled bucket (CombinedItemContainer.addItemStack). Both changes reach the player as
       InventoryChangeEvents (InventoryChangeEventSystem.tick -> CommandBuffer.invoke); no pickup, no other event. The cow's own
       Harvest_Ready alarm (11-14 game hours, kept in a Capture Crate) is the per-animal cooldown.
  NEW (all Ranching XP goes through RanchTask = the pickup award: xp multiplier, P3, Farming's gathering pace + tree Wisdom, THEN
  ranching.maxXpPerMinute; same profile, never in creative):
    1 TAMING (RanchNpcSys, a RefSystem on NPCEntity): an UNLOAD of a tameable wild role (TAME table, from Assets.zip) remembers the UUID
      for 3 s; a LOAD of that UUID as exactly its TameRoleChange role = a tame -> on the world thread (RanchActTask) the NEAREST player
      (not creative) within ranching.actRange blocks gets ranching.tameXp. A chunk unload + load never changes a role (no false tame); a pen
      animal SkyyIslands spawns as Tamed_X is a SPAWN, not a role change (no XP).
    2 CAPTURE CRATE = a PAIR (fix round): the catcher's ACTIVE hotbar slot turning an EMPTY Tool_Capture_Crate into one carrying
      CapturedEntity of role X (RanchInvSys, the slot transaction of T2's replaceItemStackInSlot) AND a REMOVE of a live (no
      DeathComponent) Capture_Crate role X in the same world (RanchNpcSys) within 1 s, either order -> THAT player (never a bystander;
      a despawn / cull / command removal has no crate change = nothing) gets ranching.captureXp if within ranching.actRange.
      RELEASED ANIMALS NEVER PAY (like items a player dropped): a crate of role X turning EMPTY in the active slot (the release, T2b:
      UseCaptureCrateInteraction.interactWithBlock spawns a NEW NPC then empties the crate) paired within 1 s with a non-LOAD add of role X in
      that world marks the new animal's UUID; catching it later pays nothing (memory only - a server restart forgets the mark).
    3 MILKING (RanchInvSys, InventoryChangeEvent on the player): an empty bucket leaving the ACTIVE hotbar slot (a slot change, never a
      move) and a filled milk bucket arriving (any slot) within 250 ms (one ActionInventory = the same tick) = one milking, and only with a
      milkable animal (Tamed_Cow / Tamed_Mosshorn*, a registry RanchNpcSys keeps from NPC adds / removes) within range. The decision runs one
      world task LATER (RanchActTask kind 2), so a drop or milk-bucket pickup noted in the same tick (RanchDropSys / RanchPickSys, after the
      inventory event) still refuses it; never for moves (chests, drag) - a bought / stored / dropped milk bucket pays nothing. The cow's
      own Harvest wait (11-14 game hours) is the real per-cow limit.
    NO XP COOLDOWNS BY DEFAULT (docs/answered/skills.md 2026-10-18 NO XP CAPS: "remove all caps", XP-only cooldowns too): the per-player
    crate / milk waits, the same-cow and same-animal times default to 0 = off; the rows stay so an admin can switch them on. Per-player
    stamps are pruned by AGE (a relog never resets them).
    XP 0 = that source off. Server Setup -> Skills -> gathering: 8 new rows (tame / capture / milk XP, capture + milk cooldowns, the
    same-cow and same-animal times, the range). Defaults (base XP before the multipliers, like ranching.items): tame 250, capture 100, milk 100
    (Lv 1-5 of Ranching = 6,300 XP; a fed + crated + milked starter pen of 4 wild animals topped up every 10 min ~ 6-9k Ranching XP an hour,
    under Farming's ~20k model hour - research/balance/targets.md 2 - because animals are slow; catch / release pays only for animals
    nobody released, so wild supply sets the pace).
  SAVED DATA: none (memory only). SETTINGS: 8 new keys in a block at the end of a FRESH xp.properties; an existing file reads the code
  defaults while a line is missing - no setting migration. No command added. ROLLBACK to 0.4.65: just the jar (0.4.65 ignores the new
  keys; taming / crates / milking pay nothing again).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.65.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.66.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.65"') and P.has("tools/skills_0_4_65_patch.py") and not P.has("0.4.66 (2026-10-25)"), "not the generated SkyySkills 0.4.65 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyySkills 0.4.65 - GENERATED by tools/skills_0_4_65_patch.py from build_skyyskills_0.4.64.py (the SET pin) - edit the patch, not this file.
''', '''"""SkyySkills 0.4.66 - GENERATED by tools/skills_0_4_66_patch.py from build_skyyskills_0.4.65.py (the SET pin) - edit the patch, not this file.
''' + NOTE + '''
SkyySkills 0.4.65 - GENERATED by tools/skills_0_4_65_patch.py from build_skyyskills_0.4.64.py (the SET pin at that time).
''')
P.rep('VERSION = "0.4.65"', 'VERSION = "0.4.66"')

# ---- the classes (made with the other 0.4.37 Ranching classes)
P.rep('''fm3  = pool.makeClass(PKG + ".Farm3")
''', '''fm3  = pool.makeClass(PKG + ".Farm3")
# 0.4.66 (R6): taming / Capture Crate / milking Ranching XP - RanchAct (tables, rules, memory), RanchNpcSys (RefSystem on NPCEntity: tame +
# crate), RanchInvSys (InventoryChangeEvent on the player: milking), RanchActTask (the nearest player on the world thread)
rac  = pool.makeClass(PKG + ".RanchAct")
rns  = pool.makeClass(PKG + ".RanchNpcSys", pool.get(REFS37))
ris  = pool.makeClass(PKG + ".RanchInvSys", pool.get(EES))
rat  = pool.makeClass(PKG + ".RanchActTask")
''')

# ---- build-time tables from Assets.zip + the default lines (a block at the end of a FRESH file; no migration)
P.rep('''DEFAULTS = DEFAULTS_063 + ("" if DEFAULTS_063.endswith(chr(10)) else chr(10)) + G64_BLOCK
''', '''DEFAULTS = DEFAULTS_063 + ("" if DEFAULTS_063.endswith(chr(10)) else chr(10)) + G64_BLOCK
# 0.4.66 (R6): the animal tables, read from Assets.zip at build time (never committed): TAME = wild role -> its TameRoleChange role
# (IsTameable), CRATE = the Capture_Crate group's IncludeRoles ("*X" = any role ending in X), MILK = the filled buckets a Milk harvest adds,
# MILK_EMPTY = the items a Milk harvest needs in the hand
_r66_tame, _r66_milk, _r66_empty, _r66_cows = {}, set(), set(), set()
with zipfile.ZipFile(ASSETS) as _z66:
    for _n66 in _z66.namelist():
        if not (_n66.startswith("Server/NPC/Roles/") and _n66.endswith(".json")):
            continue
        try:
            _d66 = json.loads(_z66.read(_n66).decode("utf-8-sig"))
        except Exception:
            continue
        _m66 = _d66.get("Modify") if isinstance(_d66, dict) else None
        if not isinstance(_m66, dict):
            continue
        _role66 = os.path.basename(_n66)[:-5]
        if _m66.get("IsTameable") is True and isinstance(_m66.get("TameRoleChange"), str):
            _r66_tame[_role66] = _m66["TameRoleChange"]
        if _m66.get("HarvestInteractionContext") == "Milk":
            _r66_cows.add(_role66)
            for _k66 in ("HarvestAddItemBucket", "HarvestAddItemDecoBucket"):
                if isinstance(_m66.get(_k66), str): _r66_milk.add(_m66[_k66].lstrip("*"))
            for _i66 in (_m66.get("HarvestInteractionRequiredItems") or []):
                _r66_empty.add(_i66.lstrip("*"))
    _cc66 = json.loads(_z66.read("Server/NPC/Groups/Capture_Crate.json").decode("utf-8-sig"))
    _tn66 = json.loads(_z66.read("Server/NPC/Roles/_Core/Templates/Template_Animal_Neutral.json").decode("utf-8-sig"))
    _tl66 = json.loads(_z66.read("Server/NPC/Roles/_Core/Templates/Template_Livestock.json").decode("utf-8-sig"))
R66_CRATE = [str(_x) for _x in _cc66.get("IncludeRoles", [])]
def _r66_types(o, out):
    if isinstance(o, dict):
        if isinstance(o.get("Type"), str): out.append((o["Type"], o.get("Operation"), o.get("Role"), o.get("Item")))
        for _v in o.values(): _r66_types(_v, out)
    elif isinstance(o, list):
        for _v in o: _r66_types(_v, out)
    return out
_tt66, _lt66 = _r66_types(_tn66, []), _r66_types(_tl66, [])
assert ("Role", None, {"Compute": "TameRoleChange"}, None) in _tt66 and ("Inventory", "RemoveHeldItem", None, None) in _tt66, \\
    "0.4.66: Template_Animal_Neutral no longer tames with RemoveHeldItem + a Role change - re-check RanchNpcSys (taming XP)"
assert ("Inventory", "RemoveHeldItem", None, None) in _lt66 and ("Inventory", "Add", None, {"Compute": "HarvestAddItemBucket"}) in _lt66, \\
    "0.4.66: Template_Livestock no longer milks with RemoveHeldItem + Add of the filled bucket - re-check RanchInvSys (milking XP)"
assert _r66_tame.get("Cow") == "Tamed_Cow" and _r66_tame.get("Sheep") == "Tamed_Sheep" and _r66_tame.get("Chicken") == "Tamed_Chicken" and len(_r66_tame) >= 20, _r66_tame
assert "Container_Bucket_State_Filled_Milk" in _r66_milk and {"Container_Bucket", "Deco_Bucket"} <= _r66_empty and not (_r66_milk & _r66_empty), (_r66_milk, _r66_empty)
assert "*Chicken" in R66_CRATE and "*Cow_Calf" in R66_CRATE and "*Sheep_Lamb" in R66_CRATE and all("," not in _x and "=" not in _x for _x in R66_CRATE)
assert all(_k.replace("_", "").isalnum() and _v.replace("_", "").isalnum() for _k, _v in _r66_tame.items())
must("Tool_Capture_Crate")
for _i66 in sorted(_r66_empty): must(_i66)
R66_TAME = ",".join("%s=%s" % (_k, _r66_tame[_k]) for _k in sorted(_r66_tame))
R66_CRATE_TEXT = ",".join(R66_CRATE)
R66_MILK = ",".join(sorted(_r66_milk))
R66_EMPTY = ",".join(sorted(_r66_empty))
assert "Tamed_Cow" in _r66_cows and all(_c.replace("_", "").isalnum() for _c in _r66_cows), _r66_cows
R66_COWS = ",".join(sorted(_r66_cows))   # the roles that can be milked (a milking needs one of them near the player)
# the defaults (base Ranching XP before the multipliers, like ranching.items; research/balance targets: Farming ~20k model XP an hour)
R66_KEYS = [("ranching.tameXp", "250"), ("ranching.captureXp", "100"), ("ranching.milkXp", "100"), ("ranching.captureCooldownSec", "0"),
            ("ranching.milkCooldownSec", "0"), ("ranching.cowCooldownSec", "0"), ("ranching.animalCooldownSec", "0"), ("ranching.actRange", "8")]
# fix round: the four XP-only waits default 0 = off (docs/answered/skills.md 2026-10-18 NO XP CAPS - "XP cooldowns that only gate XP too")
R66_DEF = dict(R66_KEYS)
G66_L = ["# 0.4.66: Ranching XP for taming an animal (feed it its food), catching one in a Capture Crate and milking a tamed cow (0 = off).",
         "# Taming pays the nearest player within ranching.actRange blocks; a catch pays the player whose crate filled; an animal released",
         "# from a crate never pays a catch again; a milking needs a tamed cow or mosshorn within range. The waits (captureCooldownSec,",
         "# milkCooldownSec, cowCooldownSec, animalCooldownSec) are 0 = off. Eggs and wool pay on pickup (ranching.items)."]
G66_L += ["%s=%s" % _kv for _kv in R66_KEYS]
G66_BLOCK = chr(10).join(G66_L) + chr(10)
DEFAULTS_065 = DEFAULTS   # 0.4.66: the 0.4.65 default file
DEFAULTS = DEFAULTS_065 + ("" if DEFAULTS_065.endswith(chr(10)) else chr(10)) + G66_BLOCK
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000 and all(("\\n%s=" % _k) not in ("\\n" + DEFAULTS_065) for _k, _v in R66_KEYS)
print("0.4.66: %d tameable roles, %d Capture Crate entries, milk %s from %s; default file %d bytes" % (len(_r66_tame), len(R66_CRATE), R66_MILK, R66_EMPTY, len(DEFAULTS)))
''')

# ---- the CFG assertions that pinned the end of the default file / the moved keys
P.rep('''assert sorted(_k for _k in set(_dp) | set(_dp61) if _dp.get(_k) != _dp61.get(_k) and _k != "tree.rally") == sorted(_e[0] for _e in P9_KEYS), "0.4.62: only the P9 keys moved (0.4.64: + the new Rally line)"
assert all(_dp.get(_k) == _n and _dp61.get(_k) == _o for _k, _o, _n, _r in P9_KEYS) and DEFAULTS_063.endswith(P9_BLOCK) and DEFAULTS.endswith(G64_BLOCK)   # 0.4.62; 0.4.64: + the Rally block''',
      '''assert sorted(_k for _k in set(_dp) | set(_dp61) if _dp.get(_k) != _dp61.get(_k) and _k != "tree.rally" and _k not in R66_DEF) == sorted(_e[0] for _e in P9_KEYS), "0.4.62: only the P9 keys moved (0.4.64: + the new Rally line; 0.4.66: + the R6 lines)"
assert all(_dp.get(_k) == _n and _dp61.get(_k) == _o for _k, _o, _n, _r in P9_KEYS) and DEFAULTS_063.endswith(P9_BLOCK) and DEFAULTS_065.endswith(G64_BLOCK) and DEFAULTS.endswith(G66_BLOCK)   # 0.4.62; 0.4.64: + the Rally block; 0.4.66: + the R6 block
assert all(_dp.get(_k) == _v for _k, _v in R66_KEYS)   # 0.4.66''')

# ---- the Server Setup rows (after the Rally row)
P.rep('''assert [_r[0] for _r in CFG_ROWS].count("tree.rally") == 1 and ("tree.rally=" + RALLY_DEF) in DEFAULTS.split(chr(10))
''', '''assert [_r[0] for _r in CFG_ROWS].count("tree.rally") == 1 and ("tree.rally=" + RALLY_DEF) in DEFAULTS.split(chr(10))
# 0.4.66 (R6): taming / Capture Crate / milking Ranching XP
CFG_ROWS.append(("ranching.tameXp", "Ranching XP for taming", "gathering", "int", R66_DEF["ranching.tameXp"], "0", "1000000", "", "", "live",
                 "Ranching XP when you tame an animal by feeding it its food (0 = none).", "reload"))
CFG_ROWS.append(("ranching.captureXp", "Ranching XP for a Capture Crate catch", "gathering", "int", R66_DEF["ranching.captureXp"], "0", "1000000", "", "", "live",
                 "Ranching XP when you catch an animal in a Capture Crate (0 = none).", "reload"))
CFG_ROWS.append(("ranching.milkXp", "Ranching XP for milking", "gathering", "int", R66_DEF["ranching.milkXp"], "0", "1000000", "", "", "live",
                 "Ranching XP when you milk a tamed cow or mosshorn with an empty bucket (0 = none).", "reload"))
CFG_ROWS.append(("ranching.captureCooldownSec", "Time between paid crate catches", "gathering", "int", R66_DEF["ranching.captureCooldownSec"], "0", "86400", "", "s", "live",
                 "Crate catches pay at most once in this many seconds per player (0 = no wait, the default).", "reload"))
CFG_ROWS.append(("ranching.milkCooldownSec", "Time between paid milkings", "gathering", "int", R66_DEF["ranching.milkCooldownSec"], "0", "86400", "", "s", "live",
                 "Milkings pay at most once in this many seconds per player (0 = no wait, the default).", "reload"))
CFG_ROWS.append(("ranching.cowCooldownSec", "Same cow pays milk again after", "gathering", "int", R66_DEF["ranching.cowCooldownSec"], "0", "604800", "", "s", "live",
                 "A milking needs a tamed cow or mosshorn near you; each pays milk XP once per this many s (0 = off).", "reload"))
CFG_ROWS.append(("ranching.animalCooldownSec", "Same animal pays again after", "gathering", "int", R66_DEF["ranching.animalCooldownSec"], "0", "604800", "", "s", "live",
                 "A tamed or crated animal pays that again only after this long (0 = off; released animals never pay).", "reload"))
CFG_ROWS.append(("ranching.actRange", "Ranching XP range", "gathering", "int", R66_DEF["ranching.actRange"], "1", "64", "", "blocks", "live",
                 "Taming pays the nearest player this close; a catcher and a milked cow must be this close too.", "reload"))
assert all([_r[0] for _r in CFG_ROWS].count(_k) == 1 and ("%s=%s" % (_k, _v)) in DEFAULTS.split(chr(10)) for _k, _v in R66_KEYS)
''')

# ---- the two 0.4.65 Ranching rows that now read wrongly: pickupXp covers pickups only, the minute cap covers every Ranching source
P.rep('''     "Animal products you pick up pay Ranching XP. Items a player dropped pay nothing again.", "reload"),''',
      '''     "Animal products you pick up pay Ranching XP (pickups only). Items a player dropped pay nothing.", "reload"),''')
P.rep('''     "At most this much Ranching XP from pickups per player per minute (0 = no cap).", "reload"),''',
      '''     "At most this much Ranching XP per player per minute: pickups, taming, crates, milking (0 = no cap).", "reload"),''')

# ---- RanchAct part 1 (config + pure rules + memory): compiled right after Ranch part 1, before SkillCfg.load calls RanchAct.read
P.rep('''# ================= SkillLv (0.4.16): the levels.skill table''', '''# ---- 0.4.66 RanchAct part 1 (R6): the tables, the settings, the tame / crate / milk rules and their memory (no engine calls but the
# transaction readers; world thread or any thread - every map is behind a synchronized method)
CNM66 = "com.hypixel.hytale.server.npc.metadata.CapturedNPCMetadata"
MVTX66 = MVTX
for _c66, _m66 in ((CNM66, "getNpcNameKey"), (CNM66, "KEYED_CODEC"), (IS, "getFromMetadataOrNull"), (SLT, "getSlot"), (SLT, "getSlotBefore"),
                   (SLT, "getSlotAfter"), (SLT, "succeeded"), (IST, "getSlotTransactions"), (LTX, "getList"), (ICE, "getComponentType"),
                   (ICE, "getTransaction"), (HOTB, "getComponentType"), (HOTB, "getActiveSlot"), (HOTB, "getActiveItem"), (NPC, "getRoleName"),
                   (UUC, "getUuid"), (UUC, "getComponentType"), (DTH, "getComponentType"), (RMR37, "UNLOAD"), (RMR37, "REMOVE"), (ADR37, "LOAD")):
    B.probe(pool, _c66, _m66)
# engine facts T1-T3 (the NOTE): any change = stop the build and re-check RanchNpcSys / RanchInvSys
_rc66 = " ".join(_bc37("com.hypixel.hytale.server.npc.systems.RoleChangeSystem", "tick"))
assert ("RemoveReason.UNLOAD" in _rc66 and "AddReason.LOAD" in _rc66 and _rc66.index("Store.removeEntity") < _rc66.index("NPCEntity.setRoleName") < _rc66.index("Store.addEntity")
        and "UUIDComponent" not in _rc66), "0.4.66 T1: RoleChangeSystem no longer re-adds the same holder UNLOAD -> LOAD under the new role - re-check taming XP"
assert any("RoleChangeSystem.requestRoleChange" in _x for _x in _bc37("com.hypixel.hytale.server.npc.corecomponents.lifecycle.ActionRole", "execute")), "0.4.66 T1: ActionRole"
_uc66 = " ".join(_bc37("com.hypixel.hytale.builtin.adventure.farming.interactions.UseCaptureCrateInteraction", "tick0"))
assert ("DeathComponent.getComponentType" in _uc66 and "CapturedNPCMetadata.setNpcNameKey" in _uc66 and "NPCPlugin.getName" in _uc66 and "RemoveReason.REMOVE" in _uc66
        and _uc66.index("ItemContainer.replaceItemStackInSlot") < _uc66.index("CommandBuffer.removeEntity")), "0.4.66 T2: the Capture Crate facts changed - re-check crate XP"
# T2b (fix round): a release reads the held crate's CapturedEntity, queues the NPC spawn (CommandBuffer.run) and empties the crate in the
# active hotbar slot (replaceItemStackInSlot); a coop put (CoopBlock.tryPutResident) empties it with no spawn
_ub66 = " ".join(_bc37("com.hypixel.hytale.builtin.adventure.farming.interactions.UseCaptureCrateInteraction", "interactWithBlock"))
assert ("CapturedNPCMetadata.getNpcNameKey" in _ub66 and "Hotbar.getActiveSlot" in _ub66 and "CoopBlock.tryPutResident" in _ub66
        and _ub66.rindex("CommandBuffer.run") < _ub66.rindex("ItemContainer.replaceItemStackInSlot")), "0.4.66 T2b: the crate release facts changed - re-check the released-animal ledger"
_ai66 = " ".join(_bc37("com.hypixel.hytale.server.npc.corecomponents.items.ActionInventory", "execute"))
_rh66 = " ".join(_bc37("com.hypixel.hytale.server.npc.util.InventoryHelper", "removeItemInHand"))
_ie66 = " ".join(_bc37("com.hypixel.hytale.server.core.inventory.InventorySystems$InventoryChangeEventSystem", "tick"))
assert ("InventoryHelper.removeItemInHand" in _ai66 and "CombinedItemContainer.addItemStack" in _ai66 and "Hotbar.getActiveSlot" in _rh66
        and "ItemContainer.removeItemStackFromSlot" in _rh66 and "InventoryChangeEvent.<init>" in _ie66 and "CommandBuffer.invoke" in _ie66), \\
    "0.4.66 T3: the milking inventory facts changed - re-check RanchInvSys (milking XP)"
print("0.4.66 engine checks: taming = UNLOAD -> LOAD role change, crate = replace then REMOVE, milking = held bucket removed + filled bucket added (InventoryChangeEvents)")
rac.addField(CtField.make('public static final String TAME_DEF = "%s";' % R66_TAME, rac))
rac.addField(CtField.make('public static final String CRATE_DEF = "%s";' % R66_CRATE_TEXT, rac))
rac.addField(CtField.make('public static final String MILK_DEF = "%s";' % R66_MILK, rac))
rac.addField(CtField.make('public static final String EMPTY_DEF = "%s";' % R66_EMPTY, rac))
rac.addField(CtField.make('public static final String COWS_DEF = "%s";' % R66_COWS, rac))
rac.addField(CtField.make('public static final String CRATE_ITEM = "Tool_Capture_Crate";', rac))
for _d66 in ("long TAME_XP = %sL" % R66_DEF["ranching.tameXp"], "long CAPTURE_XP = %sL" % R66_DEF["ranching.captureXp"],
             "long MILK_XP = %sL" % R66_DEF["ranching.milkXp"], "long CAP_CD = %s000L" % R66_DEF["ranching.captureCooldownSec"],
             "long MILK_CD = %s000L" % R66_DEF["ranching.milkCooldownSec"], "long COW_MS = %s000L" % R66_DEF["ranching.cowCooldownSec"],
             "java.util.HashSet MILKROLES = new java.util.HashSet()", "long ANIMAL_MS = %s000L" % R66_DEF["ranching.animalCooldownSec"],
             "double RANGE = %s.0" % R66_DEF["ranching.actRange"], "java.util.HashMap TAME = new java.util.HashMap()",
             "java.util.HashSet TAMED = new java.util.HashSet()", "String[] CRATE = new String[0]", "java.util.HashSet MILK = new java.util.HashSet()",
             "java.util.HashSet EMPTY = new java.util.HashSet()", "boolean FAILED = false", "boolean SEEN_TAME = false", "boolean SEEN_CRATE = false",
             "boolean SEEN_MILK = false"):
    rac.addField(CtField.make("public static volatile %s;" % _d66, rac))
for _d66 in ("long PEND_MS = 3000L", "long PAIR_MS = 1000L", "long MPAIR_MS = 250L", "long NOTE_MS = 1500L", "long REL_MS = 604800000L",
             "java.util.HashMap PEND = new java.util.HashMap()",
             "java.util.HashMap CATCH = new java.util.HashMap()", "java.util.ArrayList GONE = new java.util.ArrayList()",
             "java.util.ArrayList RELMARK = new java.util.ArrayList()", "java.util.ArrayList SPAWNED = new java.util.ArrayList()",
             "java.util.HashMap RELEASED = new java.util.HashMap()",
             "java.util.HashMap ANIMAL = new java.util.HashMap()", "java.util.HashMap PCOOL = new java.util.HashMap()",
             "java.util.HashMap MILKST = new java.util.HashMap()", "java.util.HashMap NOTE = new java.util.HashMap()",
             "java.util.HashSet COWS = new java.util.HashSet()",
             "java.util.concurrent.atomic.AtomicLong TAMES = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong CAPTURES = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong MILKS = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong NOBODY = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong REFUSED = new java.util.concurrent.atomic.AtomicLong()"):
    rac.addField(CtField.make("public static final %s;" % _d66, rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static String norm(String id) {
  if (id == null) return null;
  String t = id.trim();
  if (t.startsWith("*")) t = t.substring(1);
  return t.length() == 0 ? null : t;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static java.util.HashSet set(String csv) {
  java.util.HashSet s = new java.util.HashSet();
  String[] ps = csv == null ? new String[0] : csv.split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = norm(ps[i]);
    if (t != null) s.add(t);
  }
  return s;
}"""), rac))
# the tables (once): new objects published through the volatile fields - readers never see a half-filled map
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void tables() {
  if (!TAME.isEmpty()) return;
  java.util.HashMap m = new java.util.HashMap();
  java.util.HashSet tm = new java.util.HashSet();
  String[] ps = TAME_DEF.split(",");
  for (int i = 0; i < ps.length; i++) {
    int e = ps[i].indexOf('=');
    if (e <= 0) continue;
    String w = ps[i].substring(0, e).trim();
    String t = ps[i].substring(e + 1).trim();
    if (w.length() == 0 || t.length() == 0) continue;
    m.put(w, t);
    tm.add(t);
  }
  String[] cs = CRATE_DEF.split(",");
  java.util.ArrayList cl = new java.util.ArrayList();
  for (int i = 0; i < cs.length; i++) {
    String c = cs[i].trim();
    if (c.length() > 0 && !"*".equals(c)) cl.add(c);
  }
  CRATE = (String[]) cl.toArray(new String[0]);
  MILK = set(MILK_DEF);
  EMPTY = set(EMPTY_DEF);
  MILKROLES = set(COWS_DEF);
  TAMED = tm;
  TAME = m;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static long clampL(long v, long lo, long hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  tables();
  TAME_XP = clampL(@PKG@.SkillCfg.lng(p, "ranching.tameXp", @R66T@L), 0L, 1000000L);
  CAPTURE_XP = clampL(@PKG@.SkillCfg.lng(p, "ranching.captureXp", @R66C@L), 0L, 1000000L);
  MILK_XP = clampL(@PKG@.SkillCfg.lng(p, "ranching.milkXp", @R66M@L), 0L, 1000000L);
  CAP_CD = clampL(@PKG@.SkillCfg.lng(p, "ranching.captureCooldownSec", @R66CC@L), 0L, 86400L) * 1000L;
  MILK_CD = clampL(@PKG@.SkillCfg.lng(p, "ranching.milkCooldownSec", @R66MC@L), 0L, 86400L) * 1000L;
  COW_MS = clampL(@PKG@.SkillCfg.lng(p, "ranching.cowCooldownSec", @R66COW@L), 0L, 604800L) * 1000L;
  ANIMAL_MS = clampL(@PKG@.SkillCfg.lng(p, "ranching.animalCooldownSec", @R66A@L), 0L, 604800L) * 1000L;
  RANGE = (double) clampL(@PKG@.SkillCfg.lng(p, "ranching.actRange", @R66R@L), 1L, 64L);
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return "taming " + TAME_XP + " / Capture Crate " + CAPTURE_XP + " (one paid catch per " + (CAP_CD / 1000L) + " s) / milking " + MILK_XP
    + " (a tamed cow near you, once per cow per " + (COW_MS / 1000L) + " s) Ranching XP (" + TAME.size() + " tameable roles, " + CRATE.length + " crate roles; same animal again after " + (ANIMAL_MS / 1000L) + " s; within "
    + ((long) RANGE) + " blocks)";
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static boolean crateRole(String r) {
  if (r == null) return false;
  String[] c = CRATE;
  for (int i = 0; i < c.length; i++) {
    String e = c[i];
    if (e.startsWith("*")) { if (r.endsWith(e.substring(1))) return true; }
    else if (r.equals(e)) return true;
  }
  return false;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static String tameOf(String wild) {
  if (wild == null) return null;
  Object o = TAME.get(wild);
  return o instanceof String ? (String) o : null;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static boolean isTamed(String role) {
  return role != null && TAMED.contains(role);
}"""), rac))
# T1: an UNLOAD of a tameable wild role - remembered PEND_MS (a role change re-adds the same UUID at once)
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean unloaded(java.util.UUID a, String role, long now) {
  if (a == null || tameOf(role) == null) return false;
  if (PEND.size() > 512) {
    java.util.Iterator it = PEND.values().iterator();
    while (it.hasNext()) {
      Object[] e = (Object[]) it.next();
      if (now - ((Long) e[0]).longValue() > PEND_MS) it.remove();
    }
  }
  PEND.put(a, new Object[] { Long.valueOf(now), role });
  return true;
}"""), rac))
# T1: a LOAD of that UUID as exactly the wild role's TameRoleChange role within PEND_MS = a tame (consumes the entry)
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean tamedNow(java.util.UUID a, String role, long now) {
  if (a == null || !isTamed(role)) return false;
  Object[] e = (Object[]) PEND.remove(a);
  if (e == null || now - ((Long) e[0]).longValue() > PEND_MS) return false;
  return role.equals(tameOf((String) e[1]));
}"""), rac))
# per animal: has this animal (UUID) paid this kind (0 tame, 1 crate) within ANIMAL_MS? mark = it pays now
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean animalOk(int kind, java.util.UUID a, long now) {
  if (a == null) return true;
  Long t = (Long) ANIMAL.get(kind + "|" + a);
  long win = kind == 2 ? COW_MS : ANIMAL_MS;   // kind 2 = a milked cow (ranching.cowCooldownSec)
  return t == null || win <= 0L || now - t.longValue() >= win;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void markAnimal(int kind, java.util.UUID a, long now) {
  if (a == null) return;
  if (ANIMAL.size() > 4096) {
    java.util.Iterator it = ANIMAL.values().iterator();
    while (it.hasNext()) {
      if (now - ((Long) it.next()).longValue() >= (ANIMAL_MS > COW_MS ? ANIMAL_MS : COW_MS)) it.remove();
    }
  }
  ANIMAL.put(kind + "|" + a, Long.valueOf(now));
}"""), rac))
# per player: kind 0 tame, 1 crate, 2 milk; cd 0 = no wait
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean playerOk(int kind, java.util.UUID u, long cd, long now) {
  if (u == null) return false;
  if (cd <= 0L) return true;
  long[] c = (long[]) PCOOL.get(u);
  return c == null || c[kind] <= 0L || now - c[kind] >= cd;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void markPlayer(int kind, java.util.UUID u, long now) {
  if (u == null) return;
  long[] c = (long[]) PCOOL.get(u);
  if (c == null) { c = new long[3]; PCOOL.put(u, c); }
  c[kind] = now;
}"""), rac))
# the milkable animals (Tamed_Cow / Tamed_Mosshorn*, from Assets.zip) as RanchNpcSys sees them added / removed - a milking needs one near
rac.addMethod(CtNewMethod.make(J14(r"""
public static boolean isMilkRole(String role) {
  return role != null && MILKROLES.contains(role);
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void cowAdd(Object ref) {
  if (ref == null) return;
  if (COWS.size() > 4096) {
    java.util.Iterator it = COWS.iterator();
    while (it.hasNext()) {
      Object r = it.next();
      if (!(r instanceof @REF@) || !((@REF@) r).isValid()) it.remove();
    }
  }
  COWS.add(ref);
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void cowRemove(Object ref) {
  if (ref != null) COWS.remove(ref);
}"""), rac))
# RanchDropSys / RanchPickSys notes: a player's drop (any item) and a milk-bucket pickup block the milking pair for NOTE_MS
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void note(java.util.UUID u, int which, long now) {
  if (u == null) return;
  long[] n = (long[]) NOTE.get(u);
  if (n == null) { n = new long[2]; NOTE.put(u, n); }
  n[which] = now;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static void notePick(java.util.UUID u, String id, long now) {
  if (MILK.contains(norm(id))) note(u, 1, now);
}"""), rac))
# T3: one slot change -> flags 1 = an empty bucket left the ACTIVE hotbar slot, 2 = a filled milk bucket arrived (3 = both at once)
rac.addMethod(CtNewMethod.make(J14(r"""
public static int scanSlot(Object o, boolean held, int active) {
  if (!(o instanceof @SLT@)) return 0;
  @SLT@ t = (@SLT@) o;
  if (!t.succeeded()) return 0;
  @IS@ b = t.getSlotBefore();
  @IS@ a = t.getSlotAfter();
  String bi = (b == null || b.isEmpty()) ? null : norm(b.getItemId());
  String ai = (a == null || a.isEmpty()) ? null : norm(a.getItemId());
  int bq = bi == null ? 0 : b.getQuantity();
  int aq = ai == null ? 0 : a.getQuantity();
  int f = 0;
  boolean fromHand = held && (int) t.getSlot() == active && bi != null && EMPTY.contains(bi);
  if (fromHand && (ai == null || (bi.equals(ai) && aq < bq))) f = f | 1;
  if (ai != null && MILK.contains(ai) && (bi == null || (ai.equals(bi) && aq > bq))) f = f | 2;
  if (fromHand && ai != null && MILK.contains(ai)) f = f | 3;
  return f;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static int scanOne(Object o, boolean held, int active) {
  if (o instanceof @SLT@) return scanSlot(o, held, active);
  if (!(o instanceof @IST@)) return 0;
  java.util.List l = ((@IST@) o).getSlotTransactions();
  int f = 0;
  if (l == null) return 0;
  for (int i = 0; i < l.size(); i++) f = f | scanSlot(l.get(i), held, active);
  return f;
}"""), rac))
# a whole InventoryChangeEvent transaction: a MOVE (chest, drag, quick-stack) never counts
rac.addMethod(CtNewMethod.make(J14(r"""
public static int scanTx(Object tx, boolean held, int active) {
  if (tx == null || tx instanceof @MVTX66@) return 0;
  if (!(tx instanceof @LTX@)) return scanOne(tx, held, active);
  java.util.List l = ((@LTX@) tx).getList();
  int f = 0;
  if (l == null) return 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @MVTX66@)) f = f | scanOne(o, held, active);
  }
  return f;
}"""), rac))
# T3 pairing: both halves within MPAIR_MS (either order; one ActionInventory = the same tick) = one milking, then cleared. The drop /
# milk-pickup notes are checked LATER (noted, in the deferred RanchActTask kind 2) - a pickup's note can be set after its inventory event
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean milkPair(java.util.UUID u, int f, long now) {
  if (u == null || f == 0) return false;
  long[] s = (long[]) MILKST.get(u);
  if (s == null) { s = new long[2]; MILKST.put(u, s); }
  if ((f & 1) != 0) s[0] = now;
  if ((f & 2) != 0) s[1] = now;
  if (s[0] <= 0L || s[1] <= 0L) return false;
  long d = s[0] - s[1];
  if (d < 0L) d = -d;
  if (d > MPAIR_MS) {
    if (s[0] < s[1]) s[0] = 0L; else s[1] = 0L;
    return false;
  }
  s[0] = 0L;
  s[1] = 0L;
  return true;
}"""), rac))
# a drop (0) or a milk-bucket pickup (1) of player u within NOTE_MS of now = no milking
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean noted(java.util.UUID u, long now) {
  if (u == null) return true;
  long[] n = (long[]) NOTE.get(u);
  return n != null && ((n[0] > 0L && now - n[0] <= NOTE_MS) || (n[1] > 0L && now - n[1] <= NOTE_MS));
}"""), rac))
# T2 crate slot: the ACTIVE hotbar slot's Tool_Capture_Crate going empty -> full (role X) = "C" + X (a catch), full (X) -> empty = "R" + X
# (a release, or a coop put); anything else null
rac.addMethod(CtNewMethod.make(J14(r"""
public static String crateRoleOf(@IS@ s) {
  if (s == null || s.isEmpty() || !CRATE_ITEM.equals(norm(s.getItemId()))) return null;
  Object md = s.getFromMetadataOrNull(@CNM66@.KEYED_CODEC);
  if (!(md instanceof @CNM66@)) return "";
  String k = ((@CNM66@) md).getNpcNameKey();
  return k == null ? "" : k;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static String crateSlot(Object o, int active) {
  if (!(o instanceof @SLT@)) return null;
  @SLT@ t = (@SLT@) o;
  if (!t.succeeded() || (int) t.getSlot() != active) return null;
  String b = crateRoleOf(t.getSlotBefore());
  String a = crateRoleOf(t.getSlotAfter());
  if (b == null || a == null) return null;
  if (b.length() == 0 && a.length() > 0) return "C" + a;
  if (b.length() > 0 && a.length() == 0) return "R" + b;
  return null;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static String crateOne(Object o, int active) {
  if (o instanceof @SLT@) return crateSlot(o, active);
  if (!(o instanceof @IST@)) return null;
  java.util.List l = ((@IST@) o).getSlotTransactions();
  if (l == null) return null;
  for (int i = 0; i < l.size(); i++) {
    String c = crateSlot(l.get(i), active);
    if (c != null) return c;
  }
  return null;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static String crateTx(Object tx, int active) {
  if (tx == null || tx instanceof @MVTX66@) return null;
  if (!(tx instanceof @LTX@)) return crateOne(tx, active);
  java.util.List l = ((@LTX@) tx).getList();
  if (l == null) return null;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (o instanceof @MVTX66@) continue;
    String c = crateOne(o, active);
    if (c != null) return c;
  }
  return null;
}"""), rac))
# drop pending pair entries (Object[] with a Long time at [0]) older than PAIR_MS; keeps a list short
rac.addMethod(CtNewMethod.make(J14(r"""
public static void prune(java.util.ArrayList l, long now) {
  for (int i = l.size() - 1; i >= 0; i--) {
    Object[] e = (Object[]) l.get(i);
    if (now - ((Long) e[0]).longValue() > PAIR_MS) l.remove(i);
  }
  while (l.size() > 256) l.remove(0);
}"""), rac))
# T2 catch pair, inventory half: player u (ref) filled a crate with role in store st. A waiting REMOVE of that role in st within PAIR_MS
# -> { animal UUID, Double x, y, z } (pay now); else the mark waits for the REMOVE
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized Object[] catchMark(java.util.UUID u, Object ref, String role, Object st, long now) {
  if (u == null || role == null || st == null) return null;
  prune(GONE, now);
  for (int i = GONE.size() - 1; i >= 0; i--) {
    Object[] e = (Object[]) GONE.get(i);
    if (e[2] == st && role.equals(e[1])) {
      GONE.remove(i);
      return new Object[] { e[3], e[4], e[5], e[6] };
    }
  }
  CATCH.put(u, new Object[] { Long.valueOf(now), role, st, ref });
  return null;
}"""), rac))
# T2 catch pair, NPC half: a live crate-role animal a left store st at (x, y, z). The most recent waiting crate fill of that role in st
# within PAIR_MS -> { player UUID, player ref } (pay now); else the REMOVE waits for the crate fill
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized Object[] gone(java.util.UUID a, String role, Object st, double x, double y, double z, long now) {
  if (role == null || st == null) return null;
  java.util.UUID bu = null;
  Object[] be = null;
  long bt = -1L;
  java.util.Iterator it = CATCH.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID k = (java.util.UUID) it.next();
    Object[] e = (Object[]) CATCH.get(k);
    long t = ((Long) e[0]).longValue();
    if (now - t > PAIR_MS) { it.remove(); continue; }
    if (e[2] == st && role.equals(e[1]) && t > bt) { bt = t; bu = k; be = e; }
  }
  if (be != null) {
    CATCH.remove(bu);
    return new Object[] { bu, be[3] };
  }
  prune(GONE, now);
  GONE.add(new Object[] { Long.valueOf(now), role, st, a, Double.valueOf(x), Double.valueOf(y), Double.valueOf(z) });
  return null;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void markReleased(java.util.UUID a, long now) {
  if (a == null) return;
  if (RELEASED.size() > 8192) {
    java.util.Iterator it = RELEASED.values().iterator();
    while (it.hasNext()) {
      if (now - ((Long) it.next()).longValue() > REL_MS) it.remove();
    }
  }
  if (RELEASED.size() <= 16384) RELEASED.put(a, Long.valueOf(now));
}"""), rac))
# T2b release pair, inventory half: a crate of role emptied in the active slot in store st; a waiting non-LOAD add of that role -> marked
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void releaseMark(String role, Object st, long now) {
  if (role == null || st == null) return;
  prune(SPAWNED, now);
  for (int i = SPAWNED.size() - 1; i >= 0; i--) {
    Object[] e = (Object[]) SPAWNED.get(i);
    if (e[2] == st && role.equals(e[1])) {
      SPAWNED.remove(i);
      markReleased((java.util.UUID) e[3], now);
      return;
    }
  }
  prune(RELMARK, now);
  RELMARK.add(new Object[] { Long.valueOf(now), role, st });
}"""), rac))
# T2b release pair, NPC half: a crate-role animal a was added (not LOAD) to store st; a waiting crate release of that role -> marked
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void spawned(java.util.UUID a, String role, Object st, long now) {
  if (a == null || role == null || st == null) return;
  prune(RELMARK, now);
  for (int i = RELMARK.size() - 1; i >= 0; i--) {
    Object[] e = (Object[]) RELMARK.get(i);
    if (e[2] == st && role.equals(e[1])) {
      RELMARK.remove(i);
      markReleased(a, now);
      return;
    }
  }
  prune(SPAWNED, now);
  SPAWNED.add(new Object[] { Long.valueOf(now), role, st, a });
}"""), rac))
# was animal a released from a crate? (consumed: once crated again, its next release is a new UUID)
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean wasReleased(java.util.UUID a) {
  return a != null && RELEASED.remove(a) != null;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized void retain(java.util.Set online) {
  MILKST.keySet().retainAll(online);
  NOTE.keySet().retainAll(online);
  CATCH.keySet().retainAll(online);
  long now = System.currentTimeMillis();
  long pcw = CAP_CD > MILK_CD ? CAP_CD : MILK_CD;
  java.util.Iterator ipc = PCOOL.values().iterator();   // by AGE, never by who is online: a relog keeps its waits
  while (ipc.hasNext()) {
    long[] c = (long[]) ipc.next();
    long last = c[0] > c[1] ? c[0] : c[1];
    if (c[2] > last) last = c[2];
    if (now - last >= pcw) ipc.remove();
  }
  prune(GONE, now);
  prune(RELMARK, now);
  prune(SPAWNED, now);
  java.util.Iterator irl = RELEASED.values().iterator();
  while (irl.hasNext()) {
    if (now - ((Long) irl.next()).longValue() > REL_MS) irl.remove();
  }
  java.util.Iterator it = ANIMAL.values().iterator();
  long win = ANIMAL_MS > COW_MS ? ANIMAL_MS : COW_MS;
  while (it.hasNext()) {
    if (now - ((Long) it.next()).longValue() >= win) it.remove();
  }
  java.util.Iterator ic = COWS.iterator();
  while (ic.hasNext()) {
    Object r = ic.next();
    if (!(r instanceof @REF@) || !((@REF@) r).isValid()) ic.remove();
  }
  java.util.Iterator ip = PEND.values().iterator();
  while (ip.hasNext()) {
    Object[] e = (Object[]) ip.next();
    if (now - ((Long) e[0]).longValue() > PEND_MS) ip.remove();
  }
}"""), rac))

# ================= SkillLv (0.4.16): the levels.skill table''')
# the read() defaults come from R66_DEF (J14 tokens)
P.rep('''DEFAULTS_065 = DEFAULTS   # 0.4.66: the 0.4.65 default file
''', '''DEFAULTS_065 = DEFAULTS   # 0.4.66: the 0.4.65 default file
R66T, R66C, R66M, R66CC, R66MC, R66COW, R66A, R66R = (R66_DEF[_k] for _k in ("ranching.tameXp", "ranching.captureXp", "ranching.milkXp", "ranching.captureCooldownSec",
    "ranching.milkCooldownSec", "ranching.cowCooldownSec", "ranching.animalCooldownSec", "ranching.actRange"))   # J14 tokens of RanchAct.read's code defaults
''')

# ---- SkillCfg.load reads the new rows; SkillTick forgets players who left
P.rep('''    {PKG}.Ranch.read(p);        // 0.4.37: Ranching XP from pickups (ranching.*)
''', '''    {PKG}.Ranch.read(p);        // 0.4.37: Ranching XP from pickups (ranching.*)
    {PKG}.RanchAct.read(p);     // 0.4.66: taming / Capture Crate / milking Ranching XP (ranching.tameXp ... ranching.actRange)
''')
P.rep('''    {PKG}.Ranch.retain(online);    // 0.4.37: the Ranching minute windows
''', '''    {PKG}.Ranch.retain(online);    // 0.4.37: the Ranching minute windows
    {PKG}.RanchAct.retain(online); // 0.4.66: milking pairs / notes / cooldowns of players who left, old animal + tame entries
''')

# ---- RanchPickSys: a milk-bucket pickup is noted for the milking pair even while pickup XP is off
P.rep('''    if (!@PKG@.Ranch.ON || why == @ADR37@.LOAD || ref == null) return;
    @PIC37@ pc = (@PIC37@) st.getComponent(ref, @PIC37@.getComponentType());''', '''    if (why == @ADR37@.LOAD || ref == null) return;   // 0.4.66: no Ranch.ON gate here - the milk-bucket pickup note runs either way
    if (!@PKG@.Ranch.ON && @PKG@.RanchAct.MILK_XP <= 0L) return;
    @PIC37@ pc = (@PIC37@) st.getComponent(ref, @PIC37@.getComponentType());''')
P.rep('''    @PKG@.Ranch.picked(st, pr, is.getItemId(), @PKG@.Ranch.qtyOf(ic.isRemovedByPlayerPickup(), is.getQuantity()));
  } catch (Throwable e) {''', '''    @PKG@.RanchAct.notePick(pr.getUuid(), is.getItemId(), System.currentTimeMillis());   // 0.4.66: a picked-up milk bucket is no milking
    @PKG@.Ranch.picked(st, pr, is.getItemId(), @PKG@.Ranch.qtyOf(ic.isRemovedByPlayerPickup(), is.getQuantity()));
  } catch (Throwable e) {''')
# ---- RanchDropSys: a player's drop is noted for the milking pair (the drop ledger stays behind Ranch.ON)
P.rep('''    {DIE37} e = ({DIE37}) ev;
    if (!{PKG}.Ranch.ON) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {IS} is = e.getItemStack();''', '''    {DIE37} e = ({DIE37}) ev;
    if (!{PKG}.Ranch.ON && {PKG}.RanchAct.MILK_XP <= 0L) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {PKG}.RanchAct.note(pr.getUuid(), 0, System.currentTimeMillis());   // 0.4.66: a drop (an empty bucket leaving the hand) is no milking
    if (!{PKG}.Ranch.ON) return;
    {IS} is = e.getItemStack();''')

# ---- RanchAct part 2 (world thread): the deferred tame / crate award, the NPC RefSystem, the milking event system
P.rep('''# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4)''', '''# ================= 0.4.66 RanchAct part 2 (R6): RanchActTask, RanchNpcSys, RanchInvSys =================
# RanchActTask (world thread): kind 0 = a tame of animal a (role, at x y z in store st) -> the nearest player of that world within RANGE
# (not creative); kind 1 = a crate catch PAIRED to player u (ref pref): that player, if within RANGE and not creative, unless animal a was
# released from a crate; kind 2 = a milking pair of player u (ref pref), decided one world task after the pair (the drop / pickup notes
# of the same tick are in by then) -> a tamed cow within RANGE. Then the per-player wait + the per-animal memory (both 0 = off by
# default) -> RanchTask (the pickup award: multipliers, then the minute cap)
rat.addInterface(pool.get("java.lang.Runnable"))
for _d66 in ("int kind", "java.util.UUID a", "String role", "double x", "double y", "double z", "%s st" % ST, "java.util.UUID u", "Object pref"):
    rat.addField(CtField.make("public %s;" % _d66, rat))
rat.addConstructor(CtNewConstructor.make(J14(r"""
public RanchActTask(int kind, java.util.UUID a, String role, double x, double y, double z, @ST@ st) {
  this.kind = kind; this.a = a; this.role = role; this.x = x; this.y = y; this.z = z; this.st = st;
}"""), rat))
# the paying player for a tame at (x, y, z) in store s: nearest within RANGE, not creative; null = nobody
rac.addMethod(CtNewMethod.make(J14(r"""
public static @PR@ nearest(@ST@ s, double x, double y, double z) {
  if (s == null) return null;
  double best = RANGE * RANGE;
  @PR@ got = null;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ mp = (@PR@) it.next();
    if (mp == null || !mp.isValid()) continue;
    @REF@ mr = mp.getReference();
    if (mr == null || !mr.isValid() || mr.getStore() != s) continue;
    @V3D@ p = @PKG@.PartyXp.pos(s, mr);
    if (p == null) continue;
    double dx = p.x() - x;
    double dy = p.y() - y;
    double dz = p.z() - z;
    double d2 = dx * dx + dy * dy + dz * dz;
    if (d2 > best) continue;
    if (@PKG@.SkillXp.creative(s, mr)) continue;
    best = d2;
    got = mp;
  }
  return got;
}"""), rac))
# the award decision for player u: the per-player wait + per-animal memory (0 = off), then the base XP (0 = nothing to pay)
rac.addMethod(CtNewMethod.make(J14(r"""
public static long award(int kind, java.util.UUID u, java.util.UUID a, long now) {
  long xp = kind == 0 ? TAME_XP : (kind == 1 ? CAPTURE_XP : MILK_XP);
  if (u == null || xp <= 0L) return 0L;
  long cd = kind == 1 ? CAP_CD : (kind == 2 ? MILK_CD : 0L);
  if (!playerOk(kind, u, cd, now)) { REFUSED.incrementAndGet(); return 0L; }
  if (!animalOk(kind, a, now)) { REFUSED.incrementAndGet(); return 0L; }
  markPlayer(kind, u, now);
  markAnimal(kind, a, now);
  if (kind == 0) TAMES.incrementAndGet(); else if (kind == 1) CAPTURES.incrementAndGet(); else MILKS.incrementAndGet();
  return xp;
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static void seen(int kind, long xp) {
  String what = null;
  if (kind == 0 && !SEEN_TAME) { SEEN_TAME = true; what = "taming"; }
  if (kind == 1 && !SEEN_CRATE) { SEEN_CRATE = true; what = "a Capture Crate catch"; }
  if (kind == 2 && !SEEN_MILK) { SEEN_MILK = true; what = "milking"; }
  if (what != null) @PKG@.SkillCfg.info("Ranching XP for " + what + " reaches SkyySkills (the first one: " + xp + " base XP)");
}"""), rac))
rac.addMethod(CtNewMethod.make(J14(r"""
public static java.util.UUID uuidOf(@ST@ st, @REF@ ref) {
  @UUC@ uc = (@UUC@) st.getComponent(ref, @UUC@.getComponentType());
  return uc == null ? null : uc.getUuid();
}"""), rac))
# the nearest milkable animal (registry) of store st within RANGE of (x, y, z) -> its UUID; null = none (no milking without a cow)
rac.addMethod(CtNewMethod.make(J14(r"""
public static synchronized java.util.UUID cowNear(@ST@ st, double x, double y, double z) {
  if (st == null) return null;
  double best = RANGE * RANGE;
  java.util.UUID got = null;
  java.util.Iterator it = COWS.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @REF@)) { it.remove(); continue; }
    @REF@ r = (@REF@) o;
    if (!r.isValid()) { it.remove(); continue; }
    if (r.getStore() != st) continue;
    @V3D@ p = @PKG@.PartyXp.pos(st, r);
    if (p == null) continue;
    double dx = p.x() - x;
    double dy = p.y() - y;
    double dz = p.z() - z;
    double d2 = dx * dx + dy * dy + dz * dz;
    if (d2 > best) continue;
    java.util.UUID a = uuidOf(st, r);
    if (a == null) continue;
    best = d2;
    got = a;
  }
  return got;
}"""), rac))
# the world of store st (null = none)
rac.addMethod(CtNewMethod.make(J14(r"""
public static @WLD@ worldOf(@ST@ st) {
  if (st == null) return null;
  Object ext = st.getExternalData();
  if (!(ext instanceof @EST@)) return null;
  return ((@EST@) ext).getWorld();
}"""), rac))
# queue the deferred tame award for NPC ref (its position + world now; the player search on the world thread)
rac.addMethod(CtNewMethod.make(J14(r"""
public static boolean defer(@ST@ st, @REF@ ref, int kind, java.util.UUID a, String role) {
  if (st == null || ref == null) return false;
  @WLD@ w = worldOf(st);
  if (w == null) return false;
  @V3D@ p = @PKG@.PartyXp.pos(st, ref);
  if (p == null) return false;
  w.execute(new @PKG@.RanchActTask(kind, a, role, p.x(), p.y(), p.z(), st));
  return true;
}"""), rac))
# queue a paired award for player u (ref pref): kind 1 = the crate catch of animal a at (x, y, z), kind 2 = a milking
rac.addMethod(CtNewMethod.make(J14(r"""
public static boolean deferFor(@ST@ st, int kind, java.util.UUID u, Object pref, java.util.UUID a, String role, double x, double y, double z) {
  if (u == null || pref == null) return false;
  @WLD@ w = worldOf(st);
  if (w == null) return false;
  @PKG@.RanchActTask t = new @PKG@.RanchActTask(kind, a, role, x, y, z, st);
  t.u = u;
  t.pref = pref;
  w.execute(t);
  return true;
}"""), rac))
rat.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  try {
    long now = System.currentTimeMillis();
    java.util.UUID pu = null;
    if (this.kind == 0) {
      @PR@ pr = @PKG@.RanchAct.nearest(this.st, this.x, this.y, this.z);
      if (pr == null) { @PKG@.RanchAct.NOBODY.incrementAndGet(); return; }
      pu = pr.getUuid();
    } else {
      if (!(this.pref instanceof @REF@)) return;
      @REF@ r = (@REF@) this.pref;
      if (!r.isValid() || r.getStore() != this.st) return;
      pu = this.u;
      if (this.kind == 1 && @PKG@.RanchAct.wasReleased(this.a)) { @PKG@.RanchAct.REFUSED.incrementAndGet(); return; }   // released from a crate
      if (this.kind == 2 && @PKG@.RanchAct.noted(pu, now)) { @PKG@.RanchAct.REFUSED.incrementAndGet(); return; }   // a drop / milk pickup
      if (@PKG@.SkillXp.creative(this.st, r)) return;
      @V3D@ p = @PKG@.PartyXp.pos(this.st, r);
      if (p == null) return;
      if (this.kind == 1) {
        double dx = p.x() - this.x;
        double dy = p.y() - this.y;
        double dz = p.z() - this.z;
        if (dx * dx + dy * dy + dz * dz > @PKG@.RanchAct.RANGE * @PKG@.RanchAct.RANGE) { @PKG@.RanchAct.NOBODY.incrementAndGet(); return; }
      } else {
        this.a = @PKG@.RanchAct.cowNear(this.st, p.x(), p.y(), p.z());
        if (this.a == null) { @PKG@.RanchAct.REFUSED.incrementAndGet(); return; }   // no tamed cow / mosshorn within range (a bought bucket)
      }
    }
    long xp = @PKG@.RanchAct.award(this.kind, pu, this.a, now);
    if (xp <= 0L) return;
    @PKG@.RanchAct.seen(this.kind, xp);
    new @PKG@.RanchTask(pu, xp, @PKG@.SkillStore.pkey(pu)).run();
  } catch (Throwable t) {
    if (!@PKG@.RanchAct.FAILED) { @PKG@.RanchAct.FAILED = true; @PKG@.SkillCfg.warn("Ranching taming / crate / milking award failed (logged once): " + t); }
  }
}"""), rat))
# RanchNpcSys: a RefSystem on NPCEntity (the SkyyPets PetLoadSys pattern). LOAD of a tamed role whose UUID just UNLOADed as its wild role
# = a tame (T1); REMOVE of a live Capture_Crate role = the NPC half of a catch pair (T2); a non-LOAD add of a crate role = the NPC half
# of a release pair (T2b)
rns.addField(CtField.make("public %s query;" % QRY, rns))
rns.addConstructor(CtNewConstructor.make("public RanchNpcSys() { super(); }", rns))
rns.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = (@QRY@) @NPC@.getComponentType();
  return this.query;
}"""), rns))
rns.addMethod(CtNewMethod.make(J14(r"""
public void onEntityAdded(@REF@ ref, @ADR37@ why, @ST@ st, @CB@ cb) {
  try {
    if (ref == null) return;
    @NPC@ n = (@NPC@) st.getComponent(ref, @NPC@.getComponentType());
    if (n == null) return;
    String role = n.getRoleName();
    if (@PKG@.RanchAct.isMilkRole(role)) @PKG@.RanchAct.cowAdd(ref);   // a milkable animal (any add reason)
    if (why != @ADR37@.LOAD && @PKG@.RanchAct.CAPTURE_XP > 0L && @PKG@.RanchAct.crateRole(role))
      @PKG@.RanchAct.spawned(@PKG@.RanchAct.uuidOf(st, ref), role, st, System.currentTimeMillis());   // maybe released from a crate (T2b)
    if (why != @ADR37@.LOAD || @PKG@.RanchAct.TAME_XP <= 0L || !@PKG@.RanchAct.isTamed(role)) return;
    java.util.UUID a = @PKG@.RanchAct.uuidOf(st, ref);
    if (!@PKG@.RanchAct.tamedNow(a, role, System.currentTimeMillis())) return;
    @PKG@.RanchAct.defer(st, ref, 0, a, role);
  } catch (Throwable t) {
    if (!@PKG@.RanchAct.FAILED) { @PKG@.RanchAct.FAILED = true; @PKG@.SkillCfg.warn("Ranching taming check failed (logged once): " + t); }
  }
}"""), rns))
rns.addMethod(CtNewMethod.make(J14(r"""
public void onEntityRemove(@REF@ ref, @RMR37@ why, @ST@ st, @CB@ cb) {
  try {
    if (ref == null) return;
    boolean tame = why == @RMR37@.UNLOAD && @PKG@.RanchAct.TAME_XP > 0L;
    boolean crate = why == @RMR37@.REMOVE && @PKG@.RanchAct.CAPTURE_XP > 0L;
    @NPC@ n = (@NPC@) st.getComponent(ref, @NPC@.getComponentType());
    if (n == null) return;
    String role = n.getRoleName();
    if (@PKG@.RanchAct.isMilkRole(role)) @PKG@.RanchAct.cowRemove(ref);   // a milkable animal leaves (any reason)
    if (!tame && !crate) return;
    if (tame) {
      if (@PKG@.RanchAct.tameOf(role) != null) @PKG@.RanchAct.unloaded(@PKG@.RanchAct.uuidOf(st, ref), role, System.currentTimeMillis());
      return;
    }
    if (!@PKG@.RanchAct.crateRole(role)) return;
    if (st.getComponent(ref, @DTH@.getComponentType()) != null) return;   // a kill (DeathComponent) is never a crate catch (T2)
    @V3D@ p = @PKG@.PartyXp.pos(st, ref);
    if (p == null) return;
    java.util.UUID a = @PKG@.RanchAct.uuidOf(st, ref);
    Object[] m = @PKG@.RanchAct.gone(a, role, st, p.x(), p.y(), p.z(), System.currentTimeMillis());
    if (m != null) @PKG@.RanchAct.deferFor(st, 1, (java.util.UUID) m[0], m[1], a, role, p.x(), p.y(), p.z());   // the crate filled first
  } catch (Throwable t) {
    if (!@PKG@.RanchAct.FAILED) { @PKG@.RanchAct.FAILED = true; @PKG@.SkillCfg.warn("Ranching crate check failed (logged once): " + t); }
  }
}"""), rns))
# RanchInvSys: InventoryChangeEvent on the player (the SmeltSys pattern, Player query) -> the T2 crate halves (catch / release) + T3
# milking pairs
ris.addConstructor(CtNewConstructor.make(J14("public RanchInvSys() { super(@ICE@.class); }"), ris))
ris.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}"""), ris))
ris.addMethod(CtNewMethod.make(J14(r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (@PKG@.RanchAct.MILK_XP <= 0L && @PKG@.RanchAct.CAPTURE_XP <= 0L) return;
    @ICE@ e = (@ICE@) ev;
    Object tx = e.getTransaction();
    if (tx == null || tx instanceof @MVTX66@) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    boolean held = e.getComponentType() == @HOTB@.getComponentType();
    int active = -1;
    if (held) {
      @HOTB@ hb = (@HOTB@) st.getComponent(r, @HOTB@.getComponentType());
      if (hb == null) held = false; else active = (int) hb.getActiveSlot();
    }
    long now = System.currentTimeMillis();
    if (held && @PKG@.RanchAct.CAPTURE_XP > 0L) {
      String c = @PKG@.RanchAct.crateTx(tx, active);
      if (c != null) {
        if (c.startsWith("R")) { @PKG@.RanchAct.releaseMark(c.substring(1), st, now); return; }
        @PR@ cp = (@PR@) st.getComponent(r, @PR@.getComponentType());
        if (cp == null) return;
        String crole = c.substring(1);
        Object[] m = @PKG@.RanchAct.catchMark(cp.getUuid(), r, crole, st, now);
        if (m != null) @PKG@.RanchAct.deferFor(st, 1, cp.getUuid(), r, (java.util.UUID) m[0], crole,
            ((Double) m[1]).doubleValue(), ((Double) m[2]).doubleValue(), ((Double) m[3]).doubleValue());   // the animal left first
        return;
      }
    }
    if (@PKG@.RanchAct.MILK_XP <= 0L) return;
    int f = @PKG@.RanchAct.scanTx(tx, held, active);
    if (f == 0) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if (!@PKG@.RanchAct.milkPair(u, f, now)) return;
    @PKG@.RanchAct.deferFor(st, 2, u, r, null, null, 0.0, 0.0, 0.0);   // decided one world task later (the notes of this tick are in)
  } catch (Throwable t) {
    if (!@PKG@.RanchAct.FAILED) { @PKG@.RanchAct.FAILED = true; @PKG@.SkillCfg.warn("Ranching crate / milking check failed (logged once): " + t); }
  }
}"""), ris))

# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4)''')

# ---- registration (one registerSystem per class) + the ready line
P.rep('''  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.RanchDropSys()); }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not register RanchDropSys - dropped items are not remembered this start: " + t); }}
''', '''  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.RanchDropSys()); }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not register RanchDropSys - dropped items are not remembered this start: " + t); }}
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.RanchNpcSys()); }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not register RanchNpcSys - no Ranching XP for taming / Capture Crates this start: " + t); }}   // 0.4.66
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.RanchInvSys()); }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not register RanchInvSys - no Ranching XP for milking this start: " + t); }}   // 0.4.66
''')
P.rep('''Ranching (" + {PKG}.Ranch.text() + "), Orchard (''', '''Ranching (" + {PKG}.Ranch.text() + "; " + {PKG}.RanchAct.text() + "), Orchard (''')

# ---- the 4 new classes go into the jar with the others
P.rep('''          pdg, pds, pdsu, pcs, rch, rps, rds, rtk, fm3,
''', '''          pdg, pds, pdsu, pcs, rch, rps, rds, rtk, fm3, rac, rns, ris, rat,   # 0.4.66: + RanchAct, RanchNpcSys, RanchInvSys, RanchActTask
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 + 2 and P.s.count("makeClass(") == CLS0 + 4
P.finish()
