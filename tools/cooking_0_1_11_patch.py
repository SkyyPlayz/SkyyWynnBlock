"""Derive SkyyCooking/build_skyycooking_0.1.11.py from the LIVE SkyyCooking 0.1.10 (build_skyycooking_0.1.10.py = the tools/deploy_set.py SET
pin, DERIVED by tools/cooking_0_1_10_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.1.10 (nothing else changed). Line endings kept.
Run:  python tools/cooking_0_1_11_patch.py   then   python SkyyCooking/build_skyycooking_0.1.11.py   (never --deploy)
Check: python SkyyCooking/test_skyycooking_0.1.11.py [--dir <folder inside tools/dev/scratch/>] [--keep]
The FP1 code itself lives in the four blocks below (SUP_ASSETS, SUP_CFG, SUP_JAVA, the plugin lines); this file pastes them in.

0.1.11 = POTION FLASK + FOOD POUCH (round FP1; research/Flask-Pouch-Spec.md sections 1-4 + 6; the FP0 probe SkyyFlaskProbe 0.1.0 passed in
 game 2026-10-17, docs/log/2026-10.md). SKYY'S WORDS (docs/answered/skills.md 2026-10-16): "a healing potion that holds all the healing
 options you have (they do in automatically like our pockets.) and when you right click it it drinks a potion. (sorted from worst to best.
 and drinks the first first.) id like to do that for healing potions and food." + "(takes the normal eat/drink time to consume.)" + popups
 "Two items", "Healing only", "Yes, lifelong", "auto like the void, with a toggle." + answers "all food, we will add a good way to swap
 between health stamina and mana" (worst first across ALL food), "Storage > Supplies", "Fixed for now" (Flask 64, Pouch 256, Server
 Setup), "Cooked only" (raw stays in the Void; Server Setup switch supplies.pouchRaw, default OFF).
 1. TWO LIFELONG ITEMS: Skyy_Flask_Empty / Skyy_Flask_V_<PotionId> (the 5 vanilla healing potions - every item whose Secondary is
    Root_Secondary_Consume_Potion_Health, asserted 5) and Skyy_Food_Pouch_Empty / Skyy_Food_Pouch_V_<FoodId> (every food this build
    ships: the 15 vanilla dish overrides, the 11 own dishes, every graded copy G1-G12 and the 7 raw-snack overrides; the raw ones only
    fill while supplies.pouchRaw is ON). The loaded ids are generated IN THIS BUILD from its own item JSON (spec 3.1 "one writer") - the
    FP0 probe's flat() / swap_modify() / charge_copy() / loaded_item(): a copy of the item's InteractionVars + animation fields; the ONE
    "ModifyInventory AdjustHeldItemQuantity -1" step of the charge is swapped for "ApplyEffect Skyy_Supply_Used" (the marker) followed by
    the same Next - so the effect, the eat / drink time (Cooking's 1.875 s fast eat, the 1.5 s potion), FailOnDamage false and the vanilla
    15 s potion cooldown (Skyy_Supply_Cond_Potion_Health keeps CooldownCondition Potion_Consume_Health) are exactly the item's own. Charge
    copies: Skyy_Supply_Charge_Potion_Fast (of vanilla Consume_Charge_Potion_Fast) and Skyy_Supply_Charge_Food_T<n>_Inner (of Cooking's
    Skyy_Cook_Consume_Charge_Food_T<n>_Inner_Fast); roots Skyy_Supply_Root_Potion_Health / _Root_Food_T<n> / _Root_Empty (RequireNewClick
    kept: every drink / bite is its own hold - FP0 finding 4). Crouch + right click = OpenCustomUI page "SkyySupplies" (the condition's
    Failed branch -> Skyy_Supply_Open; vanilla's Failed was Block_Secondary). The Empty items: right click = marker Skyy_Supply_Empty ->
    the "your Flask is empty" popup. FP0 findings applied: no BlockType on any of our items, Skyy_Cook_Recipe_* never a pouch source, the
    held item becomes the Empty id when the store reaches 0. Shared model / icon (no new texture), MaxStack 1, DropOnDeath false, no
    Recipe / Tags / Quality, untiered (no tier tag). One shared name / description key each (Skyy_Flask, Skyy_Food_Pouch); the live line
    is ItemDisplay metadata (the SkyyRolls way): "Potion Flask (12)" / "Next: Small Health Potion - then 4 more kinds. ...".
    Build self-checks (the probe's): every loaded id's vars = its source's flattened vars except the charge Parent; every referenced id
    exists; no path overrides Assets.zip or this jar; no id clash; the charge copies have no ModifyInventory and carry the marker.
 2. ORDER worst first (spec 3.2): Flask by total healing (instant + regen pulses x amount, from the effect assets; asserted Lesser first),
    then ItemLevel, then name. Pouch across ALL food: Grade low -> high, raw snacks first inside Grade 0, then this build's numbers()
    restore value (instant % + over-time strength), then name. The page and right click use the same order.
 3. THE STORE (per profile, tools/PROFILES-CONTRACT.md): Skyy_SkyyCooking/supplies/<pkey>.properties = flask.auto, pouch.auto,
    given.flask, given.pouch, flask.<id>=n, pouch.<id>=n, skip.<id>=true, res.<seq>=<store>|<id> (an open use), paid=<seq> ... (the
    open journal entries whose effect is in this file). Atomic write (tmp + fsync + ATOMIC_MOVE); a History copy
    (supplies/history/<pkey>-<stamp>.properties, fsynced, read back, newest 10 kept) before the first write of each session. Cached by
    the pkey String. Nothing moves while profile:busy:<uuid> is set (the task retries every 2 s, 30 times).
    JOURNAL Skyy_SkyyCooking/supplies/journal.log (fsynced, one line per change WITH its undo):
      kind|seq|pkey|store|itemId|qty|n0|timeMs|text   kinds C fill (inventory -> store; n0 = that id's inventory count before),
      T take out (store -> inventory; n0 = the count before), Q amend the qty of seq, D settled, X cancelled / undone, R reserve,
      U use, B returned, S setting, G first give.
    CRASH SAFETY = SkyySacks 0.8.17's VoidStore journal + credit-delay pattern (classes VoidStore.appendJournal / readJournal / recover /
    settleDue / settle + SackPool.credit / paidHas / unpaid, the ~v2paid ledger), adapted: the C / T line is fsynced BEFORE the item
    moves; the store change and its seq go into the store file in ONE atomic write (the paid ledger - idempotent); the entry stays open
    for SETTLE_MS = 30 s (3 engine player saves) and is then settled (D) by a 10 s timer. An entry still open at the next start (a crash /
    stop inside the window) is RECOVERED on that profile's first task, before anything else, from the live inventory (the Sacks count
    rule): C - that id's count <= n0 - qty means the removal was saved (keep / credit now), else undo the credit; T - count >= n0 + qty
    means the give was saved (keep / debit now), else credit it back. Open uses (res.*) at start-up are returned. EXACTLY ONCE: counts
    are read before and after every move and only what really moved is credited; plain stacks only (an item with metadata is never
    taken). Fills credit at once (usable at once); the 30 s window only decides what a crash undoes.
 4. USE (spec 3.3, the FP0 runtime): SupStartSys (EntityEventSystem<InteractionChainStartEvent>) on a Secondary chain of a held loaded
    id: crouching = nothing (the page opens), creative = nothing; else reserve 1 of THAT id (store -1, res.<seq>, journal R) or cancel
    the event when the store has none (+ sync). SupTick (players with an open use / a sync / an Empty click only): the marker seen ->
    commit (U); the chain gone from getChains() 250 ms with no marker -> return (B; a cancelled tap = nothing used). The held item is
    synced (ItemContainer.replaceItemStackInSlot compare-and-swap, new ItemStack(id, 1) + ItemDisplay) only when no Secondary chain runs
    and no use is open, so the effect that ran and the item paid are always the same one.
 5. AUTO-FILL like the Void (spec 2.3): InventoryChangeEvent (SupInvSys) + PlayerReady 1.5 s later -> ONE deduplicated world-thread task
    per player (the skyyonce task pattern); from main storage + backpack ONLY (the hotbar is never touched); per store Auto-fill
    (default ON) + per item "Auto-fill this"; full = the rest stays, one popup per supplies.fullNoticeSeconds. supplies.on OFF = the
    items only open the page (they show the Empty id), nothing fills; take-out still works.
 6. BRIDGE (plain java.lang types, put in setup, removed in shutdown only while still ours): supply:fn:claims = Function(Object[]
    {UUID, String itemId}) -> Boolean.TRUE when the Flask / Pouch takes that id NOW (supplies.on, a fillable id - raw only with
    pouchRaw -, that store's Auto-fill ON for the player's CURRENT profile, the id not skipped, the store not full, not busy); answered
    from memory only (the per-player profile cache + the store cache; FALSE when either is not known yet) - cheap and thread-safe;
    supply:fn:counts = Function(UUID) -> HashMap itemId -> Long (null = busy / not loaded); hub:tab:storage:supplies (HUBS-CONTRACT).
 7. LIFELONG (tools/skyyonce.py PREFIX MODE: FlaskOnce* item_prefix Skyy_Flask_, PouchOnce* item_prefix Skyy_Food_Pouch_; switch
    supplies.lifelong). Cooking itself gives every profile one of each ONCE (given.flask / given.pouch, storage first, existing profiles
    too, profile:busy respected; a full inventory = a line naming /flask or /pouch).
 8. THE PAGE Storage > Supplies (kit 1.7 SUI.hub_page 1600 x 980, research/Menu-Pattern.md 3): sub-tabs [Potion Flask] [Food Pouch] + the
    store's Auto-fill switch on the right of the sub row; a scroll_list of list_card rows (worst -> best, the first one "Next"); the
    456 px detail panel (Take 1 = Primary, Take all, Auto-fill this: ON / OFF); footer: the status line + Put all in. No back buttons,
    inline only, icons are plain ids (never an ItemGridSlot). /flask and /pouch (hytale:Adventurer): give one back when you hold none,
    else open the page on that tab (HANDOFF 3 rule 3: nothing else added).
 REVIEW FIXES (critic round): recovery decides the open entries of one (profile, id) as a CHAIN in time order (SupOps.chainCut: the live
    count = the state the inventory was saved at; no match = the per-entry rule) - a take + re-fill or a fill + take before a crash is
    never doubled or lost; a Take keeps that id out of auto-fill and supply:fn:claims for 60 s (SupStore.MUTE; Skyy on the Void: "make it
    so, if you click take out, the auto store doesn't put it back in automatically."); a recovered entry whose D / X line cannot be
    written stays OPEN; a use's store write is retried and then logged loudly (saveHard); the store's dirty flag is a version counter.
    supply:fn:claims stays by id; SkyySacks 0.8.18 asks it only for plain stacks in storage / backpack (and pickups, which land in the
    storage), so a hotbar or metadata stack is never stranded.
 9. SERVER SETUP (Cooking > Supplies, new file Skyy_SkyyCooking/supplies.properties, written from its defaults when missing - no migration):
    supplies.on, supplies.lifelong, supplies.flaskCap 64, supplies.pouchCap 256, supplies.pouchRaw false, supplies.fullNoticeSeconds 60.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.10.py"), os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.11.py"))
assert P.has('VERSION = "0.1.10"\n') and P.has("DERIVED from build_skyycooking_0.1.9.py by tools/cooking_0_1_10_patch.py") and not P.has("POTION FLASK + FOOD POUCH"), \
    "not the generated SkyyCooking 0.1.10 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.11 = POTION FLASK"):].rstrip() + "\n\n"

# ---------- docstring + version
P.rep('''"""SkyyCooking 0.1.10 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.9.py by tools/cooking_0_1_10_patch.py
(0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_9_patch.py /
_0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py / _0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py /
_0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.10.py           -> SkyyCooking/SkyyCooking-0.1.10.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''', '''"""SkyyCooking 0.1.11 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.10.py by tools/cooking_0_1_11_patch.py
(0.1.10 / 0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_10_patch.py /
_0_1_9_patch.py / _0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py / _0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py /
_0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.11.py           -> SkyyCooking/SkyyCooking-0.1.11.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''' + NOTE)
P.rep('VERSION = "0.1.10"\n', 'VERSION = "0.1.11"\n')

# =====================================================================================================================================
# SUP_ASSETS: the item / interaction / effect assets (pure Python), pasted right before the lang file is written
# =====================================================================================================================================
SUP_ASSETS = r'''# =====================================================================================================================
# 0.1.11 SUPPLIES (round FP1, research/Flask-Pouch-Spec.md 1 + 3.1 + 3.2): the Potion Flask + Food Pouch assets, generated HERE from this
# build's own item JSON (G_ITEMS - spec 3.1 "one writer"). Mechanics = the FP0 probe's (SkyyFlaskProbe 0.1.0, proven in game 2026-10-17).
# =====================================================================================================================
import skyyui as SUI
SUI.verify()
SUP_FPRE, SUP_PPRE = "Skyy_Flask_", "Skyy_Food_Pouch_"
SUP_FEMPTY, SUP_PEMPTY = SUP_FPRE + "Empty", SUP_PPRE + "Empty"
SUP_MARK, SUP_MARK_E = "Skyy_Supply_Used", "Skyy_Supply_Empty"
SUP_PAGE = "SkyySupplies"
SUP_OPEN = "Skyy_Supply_Open"
SUP_ROOT_POT, SUP_COND_POT = "Skyy_Supply_Root_Potion_Health", "Skyy_Supply_Cond_Potion_Health"
SUP_ROOT_EMPTY, SUP_COND_EMPTY = "Skyy_Supply_Root_Empty", "Skyy_Supply_Cond_Empty"
SUP_V_ROOT_POT, SUP_V_COND_POT, SUP_V_CHARGE_POT = "Root_Secondary_Consume_Potion_Health", "Condition_Consume_Potion_Health", "Consume_Charge_Potion_Fast"
SUP_ITEM_DIR = "Server/Item/Items/SkyyCook/Supplies"
SUP_INT_DIR = "Server/Item/Interactions/SkyyCook/Supplies"
SUP_ROOT_DIR = "Server/Item/RootInteractions/SkyyCook/Supplies"
SUP_FX_DIR = "Server/Entity/Effects/SkyyCook/Supplies"
SUP_KEY = {0: "Skyy_Flask", 1: "Skyy_Food_Pouch"}
SUP_LOOK = {0: {"Model": "Items/Consumables/Potions/Potion_Large.blockymodel", "Texture": "Items/Consumables/Potions/Potion_Textures/Red.png",
                "Icon": "Icons/ItemsGenerated/Potion_Health_Large.png"},
            1: {"Model": "Items/Consumables/Food/Food_Bag.blockymodel", "Texture": "Items/Consumables/Food/Food_Bag_Texture.png",
                "Icon": "Icons/ItemsGenerated/Food_Bread.png"}}
SUP_COPY_KEYS = ("PlayerAnimationsId", "IconProperties", "InteractionConfig", "Consumable")   # spec 3.1: Quality / model / recipe are the item's own
SUP_FILES = {}
for _k in SUP_LOOK:
    for _f in ("Model", "Texture", "Icon"):
        assert "Common/" + SUP_LOOK[_k][_f] in V_COMMON, "0.1.11: the shared look file %s is not in Assets.zip" % SUP_LOOK[_k][_f]


def sup_put(path, obj):
    if path in files or path in SUP_FILES:
        raise SystemExit("0.1.11: duplicate asset path %s" % path)
    files[path] = SUP_FILES[path] = json.dumps(obj, indent=2)


_SUP_V = {}


def sup_raw(iid):
    if iid in G_ITEMS:
        return copy.deepcopy(G_ITEMS[iid])
    if iid not in V_ITEMS:
        raise SystemExit("0.1.11: item %s is neither in this build nor in Assets.zip" % iid)
    if iid not in _SUP_V:
        _SUP_V[iid] = rd(V_ITEMS[iid])
    return copy.deepcopy(_SUP_V[iid])


SUP_MERGE = ("Interactions", "InteractionVars", "TranslationProperties")


def sup_flat(iid, depth=0):
    """the EFFECTIVE item (this build's file wins over Assets.zip) resolved through its Parent chain (the probe's flat())"""
    if depth > 8:
        raise SystemExit("0.1.11: Parent chain too deep at %s" % iid)
    d = sup_raw(iid)
    p = d.pop("Parent", None)
    if not p:
        return d
    base = sup_flat(p, depth + 1)
    for k, v in d.items():
        if k in SUP_MERGE and isinstance(v, dict) and isinstance(base.get(k), dict):
            m = dict(base[k])
            m.update(v)
            base[k] = m
        else:
            base[k] = v
    return base


def sup_inter(i):
    if i in G_INTER:
        return copy.deepcopy(G_INTER[i])
    if i in V_INTER:
        return rd(V_INTER[i])
    raise SystemExit("0.1.11: interaction %s is missing" % i)


SUP_CHARGES = {}       # source charge id -> our copy
SUP_CHARGE_T = {}      # our copy -> seconds


def sup_swap(o, out):
    """every {"Type": "ModifyInventory", "AdjustHeldItemQuantity": -1, "Next": X} -> {"Type": "ApplyEffect", "EffectId": MARK, "Next": X}"""
    if isinstance(o, dict):
        if o.get("Type") == "ModifyInventory":
            if o.get("AdjustHeldItemQuantity") != -1 or sorted(o) != ["AdjustHeldItemQuantity", "Next", "Type"]:
                raise SystemExit("0.1.11: unexpected ModifyInventory shape %s" % json.dumps(o)[:300])
            out[0] += 1
            return {"Type": "ApplyEffect", "EffectId": SUP_MARK, "Next": sup_swap(o["Next"], out)}
        return dict((k, sup_swap(v, out)) for k, v in o.items())
    if isinstance(o, list):
        return [sup_swap(v, out) for v in o]
    return o


def sup_charging(o):
    if o.get("Type") == "Charging":
        return o
    cs = [x for x in o.get("Interactions", []) if isinstance(x, dict) and x.get("Type") == "Charging"]
    if o.get("Type") != "Serial" or len(cs) != 1:
        raise SystemExit("0.1.11: charge shape changed: %s" % json.dumps(o)[:300])
    return cs[0]


def sup_charge(src_id):
    if src_id in SUP_CHARGES:
        return SUP_CHARGES[src_id]
    if src_id == SUP_V_CHARGE_POT:
        our = "Skyy_Supply_Charge_Potion_Fast"
    else:
        m = re.match(r"^Skyy_Cook_Consume_Charge_Food_T([123])_Inner_Fast$", src_id)
        if not m:
            raise SystemExit("0.1.11: a food eats through %s, not Cooking's fast charge" % src_id)
        our = "Skyy_Supply_Charge_Food_T%s_Inner" % m.group(1)
    v = sup_inter(src_id)
    if "Parent" in v:
        raise SystemExit("0.1.11: charge %s has a Parent" % src_id)
    ch = sup_charging(v)
    nx = ch.get("Next") or {}
    if ch.get("FailOnDamage") is not False or len(nx) != 1:
        raise SystemExit("0.1.11: %s is no longer a one-step Charging with FailOnDamage false" % src_id)
    n = [0]
    o = sup_swap(copy.deepcopy(v), n)
    if n[0] != 1:
        raise SystemExit("0.1.11: %s: expected exactly one ModifyInventory step, found %d" % (src_id, n[0]))
    sup_put("%s/%s.json" % (SUP_INT_DIR, our), o)
    SUP_CHARGES[src_id] = our
    SUP_CHARGE_T[our] = float(list(nx)[0])
    return our


# ---- the crouch branch (page) and the markers
sup_put("%s/%s.json" % (SUP_INT_DIR, SUP_OPEN), {"Type": "Condition", "Crouching": True, "Next": {"Type": "OpenCustomUI", "Page": {"Id": SUP_PAGE}},
                                                  "Failed": {"Type": "Simple"}})
sup_put("%s/%s.json" % (SUP_FX_DIR, SUP_MARK), {"Duration": 0.5, "OverlapBehavior": "Overwrite"})
sup_put("%s/%s.json" % (SUP_FX_DIR, SUP_MARK_E), {"Duration": 0.5, "OverlapBehavior": "Overwrite"})
# ---- potions: root -> condition (cooldown kept, Failed = the page) -> our charge
_vrp, _vcp = rd(V_ROOTS[SUP_V_ROOT_POT]), rd(V_INTER[SUP_V_COND_POT])
if _vrp != {"RequireNewClick": True, "Interactions": [SUP_V_COND_POT]}:
    raise SystemExit("0.1.11: %s changed: %s" % (SUP_V_ROOT_POT, _vrp))
if _vcp.get("Type") != "Condition" or _vcp.get("Crouching") is not False or _vcp.get("Failed") != "Block_Secondary" or \
        _vcp["Next"].get("Type") != "CooldownCondition" or _vcp["Next"].get("Id") != "Potion_Consume_Health" or _vcp["Next"].get("Next") != SUP_V_CHARGE_POT:
    raise SystemExit("0.1.11: %s changed: %s" % (SUP_V_COND_POT, json.dumps(_vcp)))
_cp = copy.deepcopy(_vcp)
_cp["Next"]["Next"] = sup_charge(SUP_V_CHARGE_POT)
_cp["Failed"] = SUP_OPEN
sup_put("%s/%s.json" % (SUP_INT_DIR, SUP_COND_POT), _cp)
sup_put("%s/%s.json" % (SUP_ROOT_DIR, SUP_ROOT_POT), {"RequireNewClick": True, "Interactions": [SUP_COND_POT]})
# ---- food roots: the vanilla T1-T3 roots / conditions with Failed = the page (Next = the vanilla charge, which reads the HELD item's
# Consume_Charge var = our marker copy)
SUP_FOOD_ROOT = {}
for _t in (1, 2, 3):
    _vr, _vc = "Root_Secondary_Consume_Food_T%d" % _t, "Condition_Consume_Food_T%d" % _t
    _r, _c = rd(V_ROOTS[_vr]), rd(V_INTER[_vc])
    if _r != {"RequireNewClick": True, "Interactions": [_vc]} or _c.get("Type") != "Condition" or _c.get("Crouching") is not False or \
            _c.get("Failed") != "Block_Secondary" or _c.get("Next") != "Consume_Charge_Food_T%d" % _t:
        raise SystemExit("0.1.11: the vanilla T%d food root / condition changed: %s / %s" % (_t, _r, _c))
    _c = copy.deepcopy(_c)
    _c["Failed"] = SUP_OPEN
    sup_put("%s/Skyy_Supply_Cond_Food_T%d.json" % (SUP_INT_DIR, _t), _c)
    sup_put("%s/Skyy_Supply_Root_Food_T%d.json" % (SUP_ROOT_DIR, _t), {"RequireNewClick": True, "Interactions": ["Skyy_Supply_Cond_Food_T%d" % _t]})
    SUP_FOOD_ROOT[_vr] = "Skyy_Supply_Root_Food_T%d" % _t
# ---- the Empty items: right click = the empty marker (the popup), crouch = the page
sup_put("%s/%s.json" % (SUP_INT_DIR, SUP_COND_EMPTY), {"Type": "Condition", "Crouching": False, "Next": {"Type": "ApplyEffect", "EffectId": SUP_MARK_E},
                                                        "Failed": SUP_OPEN})
sup_put("%s/%s.json" % (SUP_ROOT_DIR, SUP_ROOT_EMPTY), {"RequireNewClick": True, "Interactions": [SUP_COND_EMPTY]})


def sup_base(kind):
    look = SUP_LOOK[kind]
    return {"TranslationProperties": {"Name": "server.items.%s.name" % SUP_KEY[kind], "Description": "server.items.%s.description" % SUP_KEY[kind]},
            "Icon": look["Icon"], "Model": look["Model"], "Texture": look["Texture"], "MaxStack": 1, "DropOnDeath": False}


def sup_loaded(kind, src, f):
    d = sup_base(kind)
    for k in SUP_COPY_KEYS:
        if k in f:
            d[k] = copy.deepcopy(f[k])
    iv = copy.deepcopy(f.get("InteractionVars") or {})
    if kind == 0:
        d["Interactions"] = {"Secondary": SUP_ROOT_POT}
        ch = SUP_CHARGES[SUP_V_CHARGE_POT]
    else:
        sec = f["Interactions"]["Secondary"]
        d["Interactions"] = {"Secondary": SUP_FOOD_ROOT[sec]}
        cc = iv.get("Consume_Charge")
        if not cc or not cc.get("Interactions"):
            raise SystemExit("0.1.11: food %s has no Consume_Charge var" % src)
        ch = None
        for e in cc["Interactions"]:
            if not isinstance(e, dict) or not e.get("Parent"):
                raise SystemExit("0.1.11: food %s: unexpected Consume_Charge entry %s" % (src, json.dumps(e)[:200]))
            e["Parent"] = sup_charge(e["Parent"])
            ch = e["Parent"]
    d["InteractionVars"] = iv
    return d, ch


def sup_fx_ids(o, out):
    if isinstance(o, dict):
        if o.get("Type") == "ApplyEffect" and isinstance(o.get("EffectId"), str):
            out.append(o["EffectId"])
        for v in o.values():
            sup_fx_ids(v, out)
    elif isinstance(o, list):
        for v in o:
            sup_fx_ids(v, out)


def sup_heal(f):
    """(instant %, regen % in total) of a healing potion, from its effect assets"""
    ids, inst, regen = [], 0.0, 0.0
    sup_fx_ids(f["InteractionVars"]["Effect"], ids)
    for e in ids:
        d = rd(V_EFFECTS[e])
        h = float((d.get("StatModifiers") or {}).get("Health", 0))
        if float(d.get("Duration", 0)) <= 0.5:
            inst += h
        else:
            cd = float(d.get("DamageCalculatorCooldown") or 0)
            regen += h * (max(1, int(float(d["Duration"]) / cd)) if cd > 0 else 1)
    return inst, regen


SUP_LOADED = {0: [], 1: []}     # kind -> [(source id, loaded id, charge id)], worst first
SUP_VARS = {}
lang_sup = []
# ---- the flask: every vanilla healing potion, worst first
_pots = sorted(i for i in V_ITEMS if (sup_flat(i).get("Interactions") or {}).get("Secondary") == SUP_V_ROOT_POT and not i.endswith("_Template"))
if len(_pots) != 5:
    raise SystemExit("0.1.11: expected 5 healing potions with %s, found %s" % (SUP_V_ROOT_POT, _pots))
SUP_F = []
for _s in _pots:
    _f = sup_flat(_s)
    _i, _r = sup_heal(_f)
    if _i <= 0 or _r <= 0:
        raise SystemExit("0.1.11: %s heals nothing? (%s, %s)" % (_s, _i, _r))
    _nm = VLANG.get("items.%s.name" % _s) or _s
    SUP_F.append({"src": _s, "total": _i + _r, "lv": int(_f.get("ItemLevel") or 0), "name": _nm, "q": _f.get("Quality", "Common"),
                  "desc": "Heals %s%% of your health: %s%% at once + %s%% over 5 s. Shares the potion cooldown." % (pct_s(_i + _r), pct_s(_i), pct_s(_r))})
SUP_F.sort(key=lambda e: (e["total"], e["lv"], e["name"]))
assert SUP_F[0]["src"] == "Potion_Health_Lesser", ("0.1.11: Lesser must come first", [e["src"] for e in SUP_F])
for _e in SUP_F:
    _f = sup_flat(_e["src"])
    _d, _ch = sup_loaded(0, _e["src"], _f)
    _lid = SUP_FPRE + "V_" + _e["src"]
    sup_put("%s/%s.json" % (SUP_ITEM_DIR, _lid), _d)
    SUP_LOADED[0].append((_e["src"], _lid, _ch))
    SUP_VARS[_lid] = _f.get("InteractionVars") or {}
# ---- the pouch: every food this build ships (never a Skyy_Cook_Recipe_* - FP0 finding 3), worst first across ALL food
SUP_P = []
for _s in sorted(G_ITEMS):
    if _s.startswith("Skyy_Cook_Recipe_"):
        continue
    _f = sup_flat(_s)
    if not re.match(r"^Root_Secondary_Consume_Food_T[123]$", str((_f.get("Interactions") or {}).get("Secondary"))):
        continue
    if _s in RAW:
        _dish, _g, _raw = _s, 0, True
    elif _s in DISHES or _s in OWN_IDS:
        _dish, _g, _raw = _s, 0, False
    else:
        _m = re.match(r"^Skyy_Cook_(.+)_G(\d+)$", _s)
        if not _m:
            raise SystemExit("0.1.11: food item %s is not a dish / graded dish / raw snack" % _s)
        _dish, _g, _raw = _m.group(1), int(_m.group(2)), False
    _n = DISH_NUM[(_dish, _g)]
    _val = sum(_n[1].values()) + sum(_n[2].values())
    if _raw:
        _nm = VLANG.get("items.%s.name" % _s) or _s
        _ds = "Raw snack - " + bars_title([RAW[_s][0]])
    else:
        _nm = DISH_NAME[_dish] + ((" (Grade %d)" % _g) if _g else "")
        _ds = bars_title(DISH_FAMS[_dish]) + (" - Grade %d" % _g if _g else "")
    _inst = ", ".join("%s%% %s" % (pct_s(_n[1][b]), b.lower()) for b in ("Health", "Mana", "Stamina") if b in _n[1])
    _ds += (" - restores " + _inst + " at once" if _inst else "") + (" + buffs for " + mmss(buff_dur(_n[3], _n[4])) if _n[3] else "")
    SUP_P.append({"src": _s, "g": _g, "raw": _raw, "val": _val, "name": _nm, "q": _f.get("Quality", "Common"), "desc": _ds})
SUP_P.sort(key=lambda e: (e["g"], 0 if e["raw"] else 1, e["val"], e["name"]))
if len(SUP_P) != len(DISHES) + len(RAW) + len(OWN_IDS) + len(GDISHES) * GEN_MAX:
    raise SystemExit("0.1.11: %d pouch sources, expected %d" % (len(SUP_P), len(DISHES) + len(RAW) + len(OWN_IDS) + len(GDISHES) * GEN_MAX))
assert SUP_P[0]["raw"] and all(e["g"] == 0 for e in SUP_P[:len(RAW) + len(DISHES) + len(OWN_IDS)]), "0.1.11: raw snacks, then Grade 0, first"
for _e in SUP_P:
    _f = sup_flat(_e["src"])
    _d, _ch = sup_loaded(1, _e["src"], _f)
    _lid = SUP_PPRE + "V_" + _e["src"]
    sup_put("%s/%s.json" % (SUP_ITEM_DIR, _lid), _d)
    SUP_LOADED[1].append((_e["src"], _lid, _ch))
    SUP_VARS[_lid] = _f.get("InteractionVars") or {}
for _k in (0, 1):
    _d = sup_base(_k)
    _d["Interactions"] = {"Secondary": SUP_ROOT_EMPTY}
    sup_put("%s/%s.json" % (SUP_ITEM_DIR, SUP_FEMPTY if _k == 0 else SUP_PEMPTY), _d)
for _pre in ("items.", "server.items."):
    lang_sup.append("%s%s.name=Potion Flask" % (_pre, SUP_KEY[0]))
    lang_sup.append("%s%s.description=Holds your healing potions - they go in by themselves. Right click: drink the weakest first. Crouch + right click: open it (Storage > Supplies, /flask)." % (_pre, SUP_KEY[0]))
    lang_sup.append("%s%s.name=Food Pouch" % (_pre, SUP_KEY[1]))
    lang_sup.append("%s%s.description=Holds your cooked food - it goes in by itself. Right click: eat the weakest first. Crouch + right click: open it (Storage > Supplies, /pouch)." % (_pre, SUP_KEY[1]))
for _l in lang_sup:
    if _l.split("=", 1)[0] in LANG_KEYS:
        raise SystemExit("0.1.11: lang key %s exists already" % _l.split("=", 1)[0])
lang.extend(lang_sup)
# ---- self-checks (the probe's)
for _p in SUP_FILES:
    if _p in V_COMMON or _p in set(V_ITEMS.values()) | set(V_INTER.values()) | set(V_ROOTS.values()) | set(V_EFFECTS.values()):
        raise SystemExit("0.1.11: asset path %s overrides Assets.zip" % _p)
_ours = dict((p.rsplit("/", 1)[1][:-5], p) for p in SUP_FILES)
for _i in _ours:
    if _i in V_ITEMS or _i in G_ITEMS or _i in V_INTER or _i in G_INTER or _i in V_ROOTS or _i in V_EFFECTS or _i in G_EFFECTS or _i.startswith("Skyy_Probe_"):
        raise SystemExit("0.1.11: id %s clashes with a vanilla / Cooking / probe id" % _i)
_SUP_KI = set(V_INTER) | set(G_INTER) | set(V_ROOTS) | set(i for i, p in _ours.items() if p.startswith((SUP_INT_DIR, SUP_ROOT_DIR)))
_SUP_KF = set(V_EFFECTS) | set(G_EFFECTS) | {SUP_MARK, SUP_MARK_E}
_sup_miss = set()


def sup_refs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("PlayerAnimationsId", "DefaultValue"):     # an animation-set Parent / a vanilla Replace fallback (unchecked, as vanilla)
                continue
            if k in ("Parent", "Next", "Failed", "Secondary", "Primary") and isinstance(v, str):
                if v not in _SUP_KI:
                    _sup_miss.add(("interaction", v))
            elif k == "Next" and isinstance(v, dict) and v and all(re.match(r"^[0-9.]+$", x) for x in v):
                for x in v.values():
                    if isinstance(x, str) and x not in _SUP_KI:
                        _sup_miss.add(("interaction", x))
                    sup_refs(x)
                continue
            elif k == "Interactions" and isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and x not in _SUP_KI:
                        _sup_miss.add(("interaction", x))
            elif k in ("EffectId", "EntityEffectId") and isinstance(v, str):
                if v not in _SUP_KF:
                    _sup_miss.add(("effect", v))
            elif k == "EntityEffectIds" and isinstance(v, list):
                for x in v:
                    if x not in _SUP_KF:
                        _sup_miss.add(("effect", x))
            if isinstance(v, (dict, list)):
                sup_refs(v)
    elif isinstance(o, list):
        for x in o:
            sup_refs(x)


for _p, _t in SUP_FILES.items():
    sup_refs(json.loads(_t))
if _sup_miss:
    raise SystemExit("0.1.11: referenced ids that exist nowhere: %s" % sorted(_sup_miss)[:20])
for _k in (0, 1):
    for _s, _lid, _ch in SUP_LOADED[_k]:
        _o = json.loads(SUP_FILES["%s/%s.json" % (SUP_ITEM_DIR, _lid)])
        _w = copy.deepcopy(SUP_VARS[_lid])
        if _k == 1:
            for _e in _w["Consume_Charge"]["Interactions"]:
                _e["Parent"] = SUP_CHARGES[_e["Parent"]]
        if json.dumps(_o["InteractionVars"], sort_keys=True) != json.dumps(_w, sort_keys=True):
            raise SystemExit("0.1.11: %s vars differ from %s beyond the charge" % (_lid, _s))
        if any(x in _o for x in ("BlockType", "Recipe", "Tags", "Categories", "Quality")) or _o["MaxStack"] != 1 or _o["DropOnDeath"] is not False:
            raise SystemExit("0.1.11: %s must have no BlockType / Recipe / Tags / Quality, MaxStack 1, DropOnDeath false (FP0 finding 2)" % _lid)
for _our in SUP_CHARGES.values():
    _t = SUP_FILES["%s/%s.json" % (SUP_INT_DIR, _our)]
    if "ModifyInventory" in _t or SUP_MARK not in _t:
        raise SystemExit("0.1.11: %s still removes the held item / has no marker" % _our)
assert json.loads(SUP_FILES["%s/%s.json" % (SUP_INT_DIR, SUP_COND_POT)])["Next"]["Id"] == "Potion_Consume_Health", "0.1.11: the flask shares the vanilla potion cooldown"
print("0.1.11 supplies: %d flask + %d pouch loaded ids + 2 empty = %d items, charges %s, %d files (%d bytes), %d lang lines" % (
    len(SUP_LOADED[0]), len(SUP_LOADED[1]), len(SUP_LOADED[0]) + len(SUP_LOADED[1]) + 2, dict((c, SUP_CHARGE_T[c]) for c in SUP_CHARGES.values()),
    len(SUP_FILES), sum(len(v) for v in SUP_FILES.values()), len(lang_sup)))
print("0.1.11 flask order (worst first): " + ", ".join("%s %s%%" % (e["src"], pct_s(e["total"])) for e in SUP_F))
print("0.1.11 pouch order (worst first, first 12 + last 3): " + ", ".join(e["src"] for e in SUP_P[:12]) + " ... " + ", ".join(e["src"] for e in SUP_P[-3:]))
'''

P.rep('''files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"
print("0.1.8 assets: ''', SUP_ASSETS + '''files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"
print("0.1.8 assets: ''')

# =====================================================================================================================================
# SUP_CFG: SupCfg (the config fields, before the kit binds them) + the Server Setup rows
# =====================================================================================================================================
SUP_CFG = r'''# ================= 0.1.11 SUPPLIES: SupCfg (supplies.properties) + Server Setup > Cooking > Supplies (spec 4.4) =================
SUP_DEFAULTS_TEXT = "\n".join([
    "# SkyyCooking %s - supplies.properties: the Potion Flask + Food Pouch. Change them in game: SkyWynn Menu -> Server Setup -> Cooking ->" % VERSION,
    "# Supplies, or edit here and press Reload there.",
    "# off = the Flask / Pouch only open their page (they show empty); nothing new goes in; taking out still works",
    "supplies.on=true",
    "# the two items are lifelong: one each per profile, never dropped, stored or sold (/flask and /pouch give them back)",
    "supplies.lifelong=true",
    "# how many potions the Potion Flask holds (1-10000)",
    "supplies.flaskCap=64",
    "# how many foods the Food Pouch holds (1-10000)",
    "supplies.pouchCap=256",
    "# raw meat, fish, eggs and cheese go in the Food Pouch too (off = they stay ingredients for the Void)",
    "supplies.pouchRaw=false",
    "# how often (seconds) a full Flask / Pouch is mentioned (0 = every time)",
    "supplies.fullNoticeSeconds=60"]) + "\n"
supc = pool.makeClass(PKG + ".SupCfg")
for _d in ("public static volatile boolean ON = true;", "public static volatile boolean LIFELONG = true;", "public static volatile int FLASK_CAP = 64;",
           "public static volatile int POUCH_CAP = 256;", "public static volatile boolean POUCH_RAW = false;",
           "public static volatile long FULL_NOTICE_MS = 60000L;", "public static volatile java.nio.file.Path FILE;",
           "public static final String DEFAULTS = %s;" % json.dumps(SUP_DEFAULTS_TEXT)):
    supc.addField(CtField.make(_d, supc))
Mk(supc, """
public static int cap(int k) { return k == 0 ? FLASK_CAP : POUCH_CAP; }""")
Mk(supc, """
public static int num(String v, int def, int lo, int hi) {
  if (v == null) return def;
  try { int n = Integer.parseInt(v.trim()); if (n < lo) return lo; if (n > hi) return hi; return n; } catch (Throwable t) { return def; }
}""")
Mk(supc, """
public static boolean bool(String v, boolean def) {
  if (v == null) return def;
  String t = v.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("true") || t.equals("on") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("0")) return false;
  return def;
}""")
# the file is written from DEFAULTS only when it is missing (a new file: no migration); a hand-edited file is only read
Mk(supc, """
public static String load(java.nio.file.Path dir) {
  try {
    FILE = dir.resolve("supplies.properties");
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    ON = bool(p.getProperty("supplies.on"), true);
    LIFELONG = bool(p.getProperty("supplies.lifelong"), true);
    FLASK_CAP = num(p.getProperty("supplies.flaskCap"), 64, 1, 10000);
    POUCH_CAP = num(p.getProperty("supplies.pouchCap"), 256, 1, 10000);
    POUCH_RAW = bool(p.getProperty("supplies.pouchRaw"), false);
    FULL_NOTICE_MS = (long) num(p.getProperty("supplies.fullNoticeSeconds"), 60, 0, 3600) * 1000L;
    return "supplies " + (ON ? "on" : "OFF") + ", lifelong " + LIFELONG + ", flask " + FLASK_CAP + ", pouch " + POUCH_CAP + ", raw " + POUCH_RAW;
  } catch (Throwable t) {
    return "supplies.properties could not be read (the defaults run): " + t;
  }
}""")
_SUPF = "@Skyy_SkyyCooking/supplies.properties:"
COOK_CFG_CATS = COOK_CFG_CATS + [("supplies", "Supplies")]
COOK_CFG_ROWS = COOK_CFG_ROWS + [
    ("supplies.on", "Potion Flask + Food Pouch", "supplies", "bool", "true", "", "", "", "", "live",
     "Off: the two items only open their page; nothing new goes in. Taking out still works.", "field:SupCfg.ON" + _SUPF + "supplies.on"),
    ("supplies.lifelong", "Lifelong Flask + Pouch", "supplies", "bool", "true", "", "", "", "", "live",
     "On: one each per profile - never dropped, stored or sold. /flask and /pouch give them back.", "field:SupCfg.LIFELONG" + _SUPF + "supplies.lifelong"),
    ("supplies.flaskCap", "Potion Flask size", "supplies", "int", "64", "1", "10000", "step=1", "", "live",
     "How many potions the Potion Flask holds. Lowering it never removes any.", "field:SupCfg.FLASK_CAP" + _SUPF + "supplies.flaskCap"),
    ("supplies.pouchCap", "Food Pouch size", "supplies", "int", "256", "1", "10000", "step=1", "", "live",
     "How many foods the Food Pouch holds. Lowering it never removes any.", "field:SupCfg.POUCH_CAP" + _SUPF + "supplies.pouchCap"),
    ("supplies.pouchRaw", "Raw food in the Pouch", "supplies", "bool", "false", "", "", "", "", "live",
     "On: raw meat, fish, eggs and cheese go in the Food Pouch too. Off: they stay in the Void.", "field:SupCfg.POUCH_RAW" + _SUPF + "supplies.pouchRaw"),
    ("supplies.fullNoticeSeconds", "Full notice every", "supplies", "int", "60", "0", "3600", "step=1", "s", "live",
     "How often a full Flask / Pouch is mentioned, in seconds. 0 = every time.", "field:SupCfg.FULL_NOTICE_MS*1000" + _SUPF + "supplies.fullNoticeSeconds"),
]
_sdp = CFG.parse_props(SUP_DEFAULTS_TEXT)
for _t in COOK_CFG_ROWS[-6:]:
    assert _t[0] in _sdp and _sdp[_t[0]] == _t[4], ("0.1.11: the supplies row default = its file line", _t[0])
'''
P.rep('''CFG_KIT = CFG.emit(pool, PKG, MOD="SkyyCooking", ''', SUP_CFG + '''CFG_KIT = CFG.emit(pool, PKG, MOD="SkyyCooking", ''')
P.rep('''FILES=[COOK_FILE, "Skyy_SkyyCooking/sounds.properties"], ''', '''FILES=[COOK_FILE, "Skyy_SkyyCooking/sounds.properties", "Skyy_SkyyCooking/supplies.properties"], ''')
P.rep('''DEFAULTS={"cooking.properties": DEFAULTS_TEXT, ''', '''DEFAULTS={"cooking.properties": DEFAULTS_TEXT, "supplies.properties": SUP_DEFAULTS_TEXT, ''')

# =====================================================================================================================================
# SUP_JAVA: every Supplies class (before the plugin; methods before callers)
# =====================================================================================================================================
SUP_JAVA = r'''# ================= 0.1.11 SUPPLIES JAVA (round FP1, research/Flask-Pouch-Spec.md; pasted by tools/cooking_0_1_11_patch.py) =================
# Classes (methods before callers): SupLog, SupDefs, SupData, SupStore, SupEng, FlaskOnce* / PouchOnce* (tools/skyyonce.py PREFIX MODE),
# SupOps, SupTask, SupSettle, SupCore, SupStartSys, SupTick, SupInvSys, SupReady, SupClaimsFn, SupCountsFn, HubBar (kit), SupPage,
# SupPageFactory, SupHubOpen, SupOpen, SupFlaskCmd, SupPouchCmd. Crash safety copies SkyySacks 0.8.17 VoidStore.appendJournal /
# readJournal / recover / settleDue / settle and SackPool.credit / paidHas / unpaid (see the header, point 3).
import skyyonce as ONCE
T.update({
    "INV": INV, "PRE": "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "ICE": "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent",
    "ICSE": "com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent",
    "ICHN": "com.hypixel.hytale.server.core.entity.InteractionChain",
    "IMOD": "com.hypixel.hytale.server.core.modules.interaction.InteractionModule",
    "IMGR": "com.hypixel.hytale.server.core.entity.InteractionManager",
    "ITYP": "com.hypixel.hytale.protocol.InteractionType",
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "MSC": "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "OCU": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction",
    "IDM": "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata",
    "NTU": "com.hypixel.hytale.server.core.util.NotificationUtil",
    "NST": "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle",
    "ISST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BTY": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "COLOK": SUI.COLOR["success"], "COLERR": SUI.COLOR["error"], "COLINFO": SUI.STATUS_INFO["gold"],
})
for c_, m_ in ((T["ICSE"], "getType"), (T["ICSE"], "getContext"), (T["ICSE"], "getChain"), (T["ICSE"], "setCancelled"),
               ("com.hypixel.hytale.server.core.entity.InteractionContext", "getHeldItem"), (T["ICHN"], "getType"), (T["IMOD"], "get"),
               (T["IMOD"], "getInteractionManagerComponent"), (T["IMGR"], "getChains"), (T["ITYP"], "Secondary"), (T["ECC"], "getComponentType"),
               (T["ECC"], "hasEffect"), (T["ECC"], "removeEffect"), (T["EFX"], "getAssetMap"),
               ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"), (T["MSC"], "getComponentType"),
               (T["MSC"], "getMovementStates"), (T["OCU"], "registerSimple"), (T["IDM"], "KEYED_CODEC"), (IS, "withMetadata"), (IS, "getMetadata"),
               (IS, "isEmpty"), (IC, "replaceItemStackInSlot"), (IC, "removeItemStackFromSlot"), (IC, "addItemStack"), (IC, "getCapacity"),
               (IC, "getItemStack"), (T["ISST"], "succeeded"), (T["NTU"], "sendNotification"), (PR, "getPacketHandler"), (PR, "getWorldUuid"),
               (PLA, "getPageManager"), (PLA, "isWaitingForClientReady"), (INV, "getStorage"), (INV, "getBackpack"), (INV, "getHotbar"),
               (INV, "getUtility"), (INV, "getTools"), (INV, "getItemInHand"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["PRE"], "getPlayerRef"),
               (PB, "getEventRegistry")):
    B.probe(pool, c_, m_)
assert pool.get(T["ICSE"]).subtypeOf(pool.get(CEV)), "0.1.11: the chain start event is cancellable (FP0)"
assert "crouching" in [str(f_.getName()) for f_ in pool.get("com.hypixel.hytale.protocol.MovementStates").getFields()], "0.1.11: MovementStates.crouching"
assert "Default" in [str(f_.getName()) for f_ in pool.get(T["NST"]).getFields()], "0.1.11: NotificationStyle.Default"


def sup_F(c, s):
    try:
        c.addField(CtField.make(jsrc(s), c))
    except Exception as e:
        raise SystemExit("0.1.11 field failed in %s:\n%s\n---\n%s" % (c.getName(), e, jsrc(s)[:600]))


def sup_Mr(c, src):
    try:
        c.addMethod(CtNewMethod.make(src, c))
    except Exception as e:
        raise SystemExit("0.1.11 compile failed in %s:\n%s\n---\n%s" % (c.getName(), e, src[:4000]))


def sup_M(c, s):
    sup_Mr(c, jsrc(s))


def sup_C(c, s):
    try:
        c.addConstructor(CtNewConstructor.make(jsrc(s), c))
    except Exception as e:
        raise SystemExit("0.1.11 constructor failed in %s:\n%s\n---\n%s" % (c.getName(), e, jsrc(s)[:1500]))


def smk(name, sup=None, iface=None):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    if iface:
        c.addInterface(pool.get(iface))
    return c


def sjarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs)


SUP_CLASSES = [supc]   # SupCfg (made before the config kit binds its fields)
# ---------------------------------------------------------------- SupLog: log, chat, popup, bridge, busy
slog = smk("SupLog")
SUP_CLASSES.append(slog)
sup_F(slog, "public static volatile @LOG@ LOG;")
sup_F(slog, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
sup_F(slog, "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();")
sup_F(slog, 'public static final String OK = "@COLOK@";')
sup_F(slog, 'public static final String ERR = "@COLERR@";')
sup_F(slog, 'public static final String INFO = "@COLINFO@";')
sup_M(slog, r"""
public static void info(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyCooking] Supplies: " + s); } catch (Throwable t) { }
}""")
sup_M(slog, r"""
public static void warn(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCooking] Supplies: " + s); } catch (Throwable t) { }
}""")
sup_M(slog, r"""
public static void warnOnce(String k, String s) {
  if (ONCE.putIfAbsent(k, Boolean.TRUE) == null) warn(s + " (logged once)");
}""")
sup_M(slog, r"""
public static java.util.Map bridge() { return @PKG@.Cook.bridge(); }""")
sup_M(slog, r"""
public static boolean busy(java.util.UUID u) {
  if (u == null) return true;
  try { return bridge().get("profile:busy:" + u.toString()) != null; } catch (Throwable t) { return false; }
}""")
sup_M(slog, r"""
public static void tell(@PR@ pr, String s, String col) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw(s).color(col)); } catch (Throwable t) { }
}""")
# at most once per ms per player and key (chat / popup spam guard)
sup_M(slog, r"""
public static boolean due(java.util.UUID u, String key, long ms) {
  if (u == null) return false;
  String k = u.toString() + ":" + key;
  long now = System.currentTimeMillis();
  Long last = (Long) TOLD.get(k);
  if (last != null && now - last.longValue() < ms) return false;
  TOLD.put(k, Long.valueOf(now));
  return true;
}""")
sup_M(slog, r"""
public static void pop(@PR@ pr, String title, String body) {
  if (pr == null) return;
  try { @NTU@.sendNotification(pr.getPacketHandler(), @MSG@.raw(title), @MSG@.raw(body), @NST@.Default); }
  catch (Throwable t) { tell(pr, "[Cooking] " + title + " - " + body, INFO); }
}""")

# ---------------------------------------------------------------- SupDefs: the build-time tables (worst first) + pure id logic
sdef = smk("SupDefs")
SUP_CLASSES.append(sdef)
sup_F(sdef, 'public static final String FPRE = "%s";' % SUP_FPRE)
sup_F(sdef, 'public static final String PPRE = "%s";' % SUP_PPRE)
sup_F(sdef, 'public static final String FEMPTY = "%s";' % SUP_FEMPTY)
sup_F(sdef, 'public static final String PEMPTY = "%s";' % SUP_PEMPTY)
sup_F(sdef, 'public static final String MARK = "%s";' % SUP_MARK)
sup_F(sdef, 'public static final String MARK_E = "%s";' % SUP_MARK_E)
sup_F(sdef, "public static final String[] FSRC = %s;" % sjarr([e["src"] for e in SUP_F]))
sup_F(sdef, "public static final String[] FNAME = %s;" % sjarr([e["name"] for e in SUP_F]))
sup_F(sdef, "public static final String[] FDESC = %s;" % sjarr([e["desc"] for e in SUP_F]))
sup_F(sdef, "public static final String[] FCOL = %s;" % sjarr([SUI.QUALITY.get(e["q"], SUI.QUALITY["Common"]) for e in SUP_F]))
sup_F(sdef, "public static final String[] PSRC = %s;" % sjarr([e["src"] for e in SUP_P]))
sup_F(sdef, "public static final String[] PNAME = %s;" % sjarr([e["name"] for e in SUP_P]))
sup_F(sdef, "public static final String[] PDESC = %s;" % sjarr([e["desc"] for e in SUP_P]))
sup_F(sdef, "public static final String[] PCOL = %s;" % sjarr([SUI.QUALITY.get(e["q"], SUI.QUALITY["Common"]) for e in SUP_P]))
sup_F(sdef, "public static final boolean[] PRAW = new boolean[] { %s };" % ", ".join("true" if e["raw"] else "false" for e in SUP_P))
sup_F(sdef, "public static volatile java.util.HashMap IX0 = null;")
sup_F(sdef, "public static volatile java.util.HashMap IX1 = null;")
sup_M(sdef, r"""
public static java.util.HashMap mk(String[] a) {
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < a.length; i++) m.put(a[i], Integer.valueOf(i));
  return m;
}""")
sup_M(sdef, r"""
public static String[] srcs(int k) { return k == 0 ? FSRC : PSRC; }""")
sup_M(sdef, r"""
public static int idx(int k, String src) {
  if (src == null) return -1;
  java.util.HashMap m = k == 0 ? IX0 : IX1;
  if (m == null) {
    m = mk(srcs(k));
    if (k == 0) IX0 = m; else IX1 = m;
  }
  Object o = m.get(src);
  return o == null ? -1 : ((Integer) o).intValue();
}""")
sup_M(sdef, r"""
public static String name(int k, String src) {
  int i = idx(k, src);
  if (i < 0) return String.valueOf(src);
  return k == 0 ? FNAME[i] : PNAME[i];
}""")
sup_M(sdef, r"""
public static String desc(int k, String src) {
  int i = idx(k, src);
  if (i < 0) return "";
  return k == 0 ? FDESC[i] : PDESC[i];
}""")
sup_M(sdef, r"""
public static String col(int k, String src) {
  int i = idx(k, src);
  if (i < 0) return k == 0 ? FCOL[0] : PCOL[0];
  return k == 0 ? FCOL[i] : PCOL[i];
}""")
# 0 = a Flask id, 1 = a Pouch id, -1 = not ours
sup_M(sdef, r"""
public static int kindOf(String id) {
  if (id == null) return -1;
  if (id.startsWith(FPRE)) return 0;
  if (id.startsWith(PPRE)) return 1;
  return -1;
}""")
# the source a loaded id carries; "" = the Empty id; null = not ours / unknown shape
sup_M(sdef, r"""
public static String srcOf(String id) {
  int k = kindOf(id);
  if (k < 0) return null;
  String rest = id.substring((k == 0 ? FPRE : PPRE).length());
  if (rest.equals("Empty")) return "";
  if (!rest.startsWith("V_") || rest.length() < 3) return null;
  return rest.substring(2);
}""")
sup_M(sdef, r"""
public static String loadedId(int k, String src) {
  if (src == null || src.length() == 0) return k == 0 ? FEMPTY : PEMPTY;
  return (k == 0 ? FPRE : PPRE) + "V_" + src;
}""")
# the store an id may fill now (0 flask, 1 pouch, -1 none); raw snacks only with supplies.pouchRaw
sup_M(sdef, r"""
public static int fillKind(String id) {
  if (id == null) return -1;
  if (idx(0, id) >= 0) return 0;
  int i = idx(1, id);
  if (i < 0) return -1;
  if (PRAW[i] && !@PKG@.SupCfg.POUCH_RAW) return -1;
  return 1;
}""")
sup_M(sdef, r"""
public static boolean isRawSrc(int k, String src) { int i = idx(1, src); return k == 1 && i >= 0 && PRAW[i]; }""")
sup_M(sdef, r"""
public static String kindName(int k) { return k == 0 ? "Potion Flask" : "Food Pouch"; }""")
sup_M(sdef, r"""
public static String cmd(int k) { return k == 0 ? "/flask" : "/pouch"; }""")
sup_M(sdef, r"""
public static String what(int k) { return k == 0 ? "healing potions" : "cooked food"; }""")

# ---------------------------------------------------------------- SupData: one profile's store (memory; world thread writes, any thread reads)
sdat = smk("SupData")
SUP_CLASSES.append(sdat)
for _d in ("public String key;", "public java.util.concurrent.ConcurrentHashMap f;", "public java.util.concurrent.ConcurrentHashMap p;",
           "public java.util.concurrent.ConcurrentHashMap skip;", "public volatile boolean fAuto;", "public volatile boolean pAuto;",
           "public volatile boolean givenF;", "public volatile boolean givenP;", "public volatile boolean ready;", "public volatile boolean bad;",
           "public volatile long fTot;", "public volatile long pTot;", "public java.util.LinkedHashMap res;", "public java.util.HashSet paid;",
           "public boolean snapped;", "public volatile long ver;", "public volatile long saved;"):
    sup_F(sdat, _d)
sup_C(sdat, r"""
public SupData(String k) {
  this.key = k;
  this.f = new java.util.concurrent.ConcurrentHashMap();
  this.p = new java.util.concurrent.ConcurrentHashMap();
  this.skip = new java.util.concurrent.ConcurrentHashMap();
  this.fAuto = true; this.pAuto = true; this.givenF = false; this.givenP = false; this.ready = false; this.bad = false;
  this.fTot = 0L; this.pTot = 0L; this.res = new java.util.LinkedHashMap(); this.paid = new java.util.HashSet(); this.snapped = false; this.ver = 0L; this.saved = 0L;
}""")
sup_M(sdat, r"""
public java.util.concurrent.ConcurrentHashMap map(int k) { return k == 0 ? this.f : this.p; }""")
sup_M(sdat, r"""
public long get(int k, String src) {
  if (src == null) return 0L;
  Object o = map(k).get(src);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}""")
sup_M(sdat, r"""
public long tot(int k) { return k == 0 ? this.fTot : this.pTot; }""")
sup_M(sdat, r"""
public void retot() {
  long a = 0L;
  java.util.Iterator it = this.f.values().iterator();
  while (it.hasNext()) a = a + ((Long) it.next()).longValue();
  long b = 0L;
  it = this.p.values().iterator();
  while (it.hasNext()) b = b + ((Long) it.next()).longValue();
  this.fTot = a;
  this.pTot = b;
}""")
# +d (or -d); never below 0 (answers what could not be taken)
sup_M(sdat, r"""
public long add(int k, String src, long d) {
  long n = get(k, src) + d;
  long short_ = 0L;
  if (n < 0L) { short_ = -n; n = 0L; }
  if (n == 0L) map(k).remove(src);
  else map(k).put(src, Long.valueOf(n));
  retot();
  this.ver = this.ver + 1L;
  return short_;
}""")
sup_M(sdat, r"""
public boolean auto(int k) { return k == 0 ? this.fAuto : this.pAuto; }""")
sup_M(sdat, r"""
public void setAuto(int k, boolean v) { if (k == 0) this.fAuto = v; else this.pAuto = v; this.ver = this.ver + 1L; }""")
sup_M(sdat, r"""
public boolean given(int k) { return k == 0 ? this.givenF : this.givenP; }""")
sup_M(sdat, r"""
public void setGiven(int k) { if (k == 0) this.givenF = true; else this.givenP = true; this.ver = this.ver + 1L; }""")
sup_M(sdat, r"""
public void touch() { this.ver = this.ver + 1L; }""")
sup_M(sdat, r"""
public boolean isDirty() { return this.ver != this.saved; }""")
sup_M(sdat, r"""
public boolean skipped(String src) { return src != null && this.skip.containsKey(src); }""")
# the next item a right click uses: the first of the build-time order (worst first) the store holds
sup_M(sdat, r"""
public String next(int k) {
  String[] a = @PKG@.SupDefs.srcs(k);
  for (int i = 0; i < a.length; i++) if (get(k, a[i]) > 0L) return a[i];
  return null;
}""")
sup_M(sdat, r"""
public int kinds(int k) {
  String[] a = @PKG@.SupDefs.srcs(k);
  int n = 0;
  for (int i = 0; i < a.length; i++) if (get(k, a[i]) > 0L) n++;
  return n;
}""")

# ---------------------------------------------------------------- SupStore: files, journal, open entries, per-player runtime maps
ssto = smk("SupStore")
SUP_CLASSES.append(ssto)
for _d in ("public static volatile java.nio.file.Path DIR = null;",
           "public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();",   # pkey -> SupData
           # seq -> Object[] { String kind C/T, String pkey, Integer store, String id, Long qty, Long n0, Long timeMs, Boolean thisJvm }
           "public static final java.util.concurrent.ConcurrentHashMap OPEN = new java.util.concurrent.ConcurrentHashMap();",
           # uuid -> Object[] { Integer store, String id, Object chain, Long t0, Long goneSince, String seq, String pkey }
           "public static final java.util.concurrent.ConcurrentHashMap RES = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap SYNC = new java.util.concurrent.ConcurrentHashMap();",    # uuid -> TRUE
           "public static final java.util.concurrent.ConcurrentHashMap WATCH = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> Object[] { Long t, Integer store }
           "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();",    # uuid -> TRUE (a task is queued)
           "public static final java.util.concurrent.atomic.AtomicLong SEQ = new java.util.concurrent.atomic.AtomicLong(0L);",
           # 0 fills, 1 takes, 2 uses, 3 returns, 4 reserves, 5 cancels, 6 free uses, 7 recovered, 8 save failures, 9 settled, 10 tasks
           "public static final java.util.concurrent.atomic.AtomicLongArray N = new java.util.concurrent.atomic.AtomicLongArray(11);",
           "public static volatile long SETTLE_MS = 30000L;", "public static volatile int HIST_KEEP = 10;"):
    sup_F(ssto, _d)
sup_F(ssto, "public static final java.util.concurrent.ConcurrentHashMap MUTE = new java.util.concurrent.ConcurrentHashMap();")   # pkey|id -> Long until (Take)
sup_F(ssto, "public static volatile long MUTE_MS = 60000L;")
# Skyy (the Void, same wish): "make it so, if you click take out, the auto store doesn't put it back in automatically." - a Take keeps
# that id out of auto-fill (and supply:fn:claims) for MUTE_MS; Put all in still takes it
sup_M(ssto, r"""
public static void mute(String key, String id) { MUTE.put(key + "|" + id, Long.valueOf(System.currentTimeMillis() + MUTE_MS)); }""")
sup_M(ssto, r"""
public static boolean muted(String key, String id) {
  if (key == null || id == null || MUTE.isEmpty()) return false;
  Object o = MUTE.get(key + "|" + id);
  if (!(o instanceof Long)) return false;
  if (((Long) o).longValue() > System.currentTimeMillis()) return true;
  MUTE.remove(key + "|" + id);
  return false;
}""")
sup_M(ssto, r"""
public static String nextSeq() { return "s" + Long.toString(System.currentTimeMillis(), 36) + "n" + SEQ.incrementAndGet(); }""")
sup_M(ssto, r"""
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('|', '/').replace('\n', ' ').replace('\r', ' ');
}""")
sup_M(ssto, r"""
public static String safeKey(String k) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < k.length() && i < 80; i++) {
    char c = k.charAt(i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-') sb.append(c); else sb.append('_');
  }
  return sb.toString();
}""")
sup_M(ssto, r"""
public static String line(String kind, String seq, String key, int store, String id, long qty, long n0, String text) {
  return kind + "|" + seq + "|" + clean(key) + "|" + store + "|" + clean(id) + "|" + qty + "|" + n0 + "|" + System.currentTimeMillis() + "|" + clean(text);
}""")
# THE journal append: one line, flushed + fsynced (SkyySacks VoidStore.appendJournal); false = the caller does not move anything
sup_M(ssto, r"""
public static synchronized boolean append(String line) {
  if (DIR == null) return false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(DIR.resolve("journal.log").toFile(), true);
    try { out.write((line + "\n").getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
    return true;
  } catch (Throwable t) {
    @PKG@.SupLog.warnOnce("journal", "could not write supplies/journal.log - that move was not done: " + t);
    return false;
  }
}""")
sup_M(ssto, r"""
public static void jopen(String seq, String kind, String key, int store, String id, long qty, long n0) {
  OPEN.put(seq, new Object[] { kind, key, Integer.valueOf(store), id, Long.valueOf(qty), Long.valueOf(n0), Long.valueOf(System.currentTimeMillis()), Boolean.TRUE });
}""")
sup_M(ssto, r"""
public static void amend(String seq, long qty) {
  Object[] e = (Object[]) OPEN.get(seq);
  if (e != null) e[4] = Long.valueOf(qty);
}""")
sup_M(ssto, r"""
public static long num(String s, long def) {
  try { return Long.parseLong(s.trim()); } catch (Throwable t) { return def; }
}""")
# start-up: every C / T line without its D / X is an OPEN entry of an earlier run (recovered on that profile's first task); a journal
# above 4 MB moves to journal-<stamp>.old and the open entries are written again into the new one (nothing is deleted)
sup_M(ssto, r"""
public static int readJournal() {
  if (DIR == null) return 0;
  java.nio.file.Path f = DIR.resolve("journal.log");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return 0;
    java.util.List lines = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = 0; i < lines.size(); i++) {
      String ln = ((String) lines.get(i)).trim();
      if (ln.length() == 0 || ln.startsWith("#")) continue;
      String[] a = ln.split("\\|", -1);
      if (a.length < 2) continue;
      if ((a[0].equals("C") || a[0].equals("T")) && a.length >= 9) {
        OPEN.put(a[1], new Object[] { a[0], a[2], Integer.valueOf((int) num(a[3], 0L)), a[4], Long.valueOf(num(a[5], 0L)), Long.valueOf(num(a[6], 0L)), Long.valueOf(num(a[7], 0L)), Boolean.FALSE });
      } else if (a[0].equals("Q") && a.length >= 6) {
        Object[] e = (Object[]) OPEN.get(a[1]);
        if (e != null) e[4] = Long.valueOf(num(a[5], 0L));
      } else if (a[0].equals("D") || a[0].equals("X")) {
        OPEN.remove(a[1]);
      }
    }
    if (java.nio.file.Files.size(f) > 4000000L) {
      String stamp = new java.text.SimpleDateFormat("yyyyMMdd-HHmmss").format(new java.util.Date());
      java.nio.file.Files.move(f, DIR.resolve("journal-" + stamp + ".old"), new java.nio.file.CopyOption[0]);
      append("# journal continued from journal-" + stamp + ".old - the entries still open are copied below");
      java.util.Iterator it = OPEN.entrySet().iterator();
      while (it.hasNext()) {
        java.util.Map.Entry me = (java.util.Map.Entry) it.next();
        Object[] e = (Object[]) me.getValue();
        append(e[0] + "|" + me.getKey() + "|" + e[1] + "|" + e[2] + "|" + e[3] + "|" + e[4] + "|" + e[5] + "|" + e[6] + "|carried over (still open)");
      }
    }
    return OPEN.size();
  } catch (Throwable t) {
    @PKG@.SupLog.warn("could not read supplies/journal.log (" + t + ") - open entries of the last run are not recovered");
    return -1;
  }
}""")
sup_M(ssto, r"""
public static java.nio.file.Path fileOf(String key) { return DIR.resolve(safeKey(key) + ".properties"); }""")
# History copy of the store file before its first write of a session (fsynced, read back; newest HIST_KEEP per profile kept)
sup_M(ssto, r"""
public static boolean snapshot(@PKG@.SupData d) {
  if (d.snapped) return true;
  try {
    java.nio.file.Path f = fileOf(d.key);
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.nio.file.Path hd = DIR.resolve("history");
      java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
      String stamp = new java.text.SimpleDateFormat("yyyyMMdd-HHmmss-SSS").format(new java.util.Date());
      byte[] raw = java.nio.file.Files.readAllBytes(f);
      java.nio.file.Path h = hd.resolve(safeKey(d.key) + "-" + stamp + ".properties");
      java.io.FileOutputStream out = new java.io.FileOutputStream(h.toFile());
      try { out.write(raw); out.flush(); out.getFD().sync(); } finally { out.close(); }
      if (!java.util.Arrays.equals(raw, java.nio.file.Files.readAllBytes(h))) throw new java.io.IOException("the History copy does not match");
      java.io.File[] all = hd.toFile().listFiles();
      java.util.ArrayList mine = new java.util.ArrayList();
      String pre = safeKey(d.key) + "-";
      for (int i = 0; all != null && i < all.length; i++) if (all[i].getName().startsWith(pre) && all[i].getName().endsWith(".properties")) mine.add(all[i].getName());
      java.util.Collections.sort(mine);
      for (int i = 0; i < mine.size() - HIST_KEEP; i++) java.nio.file.Files.deleteIfExists(hd.resolve((String) mine.get(i)));
    }
    d.snapped = true;
    return true;
  } catch (Throwable t) {
    @PKG@.SupLog.warnOnce("hist:" + d.key, "could not make the History copy of supplies/" + d.key + ".properties - nothing is written to it until it works: " + t);
    return false;
  }
}""")
sup_M(ssto, r"""
public static String text(@PKG@.SupData d) {
  java.util.TreeMap m = new java.util.TreeMap();
  m.put("flask.auto", String.valueOf(d.fAuto));
  m.put("pouch.auto", String.valueOf(d.pAuto));
  m.put("given.flask", String.valueOf(d.givenF));
  m.put("given.pouch", String.valueOf(d.givenP));
  java.util.Iterator it = d.f.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put("flask." + e.getKey(), String.valueOf(e.getValue())); }
  it = d.p.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put("pouch." + e.getKey(), String.valueOf(e.getValue())); }
  it = d.skip.keySet().iterator();
  while (it.hasNext()) m.put("skip." + it.next(), "true");
  it = d.res.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put("res." + e.getKey(), String.valueOf(e.getValue())); }
  StringBuilder pb = new StringBuilder();
  it = d.paid.iterator();
  while (it.hasNext()) {
    String s = (String) it.next();
    if (!OPEN.containsKey(s)) { it.remove(); continue; }
    if (pb.length() > 0) pb.append(' ');
    pb.append(s);
  }
  if (pb.length() > 0) m.put("paid", pb.toString());
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyCooking Supplies - the Potion Flask + Food Pouch store of profile ").append(d.key).append(" (written by the server; do not edit while it runs)\n");
  it = m.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); sb.append(e.getKey()).append('=').append(e.getValue()).append('\n'); }
  return sb.toString();
}""")
# atomic write: tmp + fsync + ATOMIC_MOVE (plain replace fallback), 5 x 20 ms retries; never over a file that could not be read
sup_M(ssto, r"""
public static boolean save(@PKG@.SupData d) {
  if (d == null || d.bad || DIR == null) return false;
  if (!snapshot(d)) { N.incrementAndGet(8); return false; }
  java.nio.file.Path f = fileOf(d.key);
  java.nio.file.Path tmp = DIR.resolve(safeKey(d.key) + ".properties.tmp");
  long v0 = d.ver;   // what this write holds; a change after it keeps the store dirty (LOW 10)
  String t = text(d);
  for (int a = 0; a < 5; a++) {
    try {
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      try { out.write(t.getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
      try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
      catch (java.nio.file.AtomicMoveNotSupportedException x) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
      d.saved = v0;
      return true;
    } catch (java.nio.file.FileSystemException x) {
      try { Thread.sleep(20L); } catch (Throwable s) { }
    } catch (Throwable x) {
      @PKG@.SupLog.warnOnce("save:" + d.key, "could not write supplies/" + d.key + ".properties: " + x);
      break;
    }
  }
  N.incrementAndGet(8);
  return false;
}""")
# load one profile's store; open uses (res.*) of a run that stopped mid-drink are returned (journal B, then the file is written)
sup_M(ssto, r"""
public static boolean saveHard(@PKG@.SupData d, String what) {
  if (save(d)) return true;
  try { Thread.sleep(20L); } catch (Throwable t) { }
  if (save(d)) return true;
  @PKG@.SupLog.warn("COULD NOT WRITE supplies/" + (d == null ? "?" : d.key) + ".properties after " + what + " - the change is kept in memory and written with the next change (or at shutdown)");
  return false;
}""")
sup_M(ssto, r"""
public static @PKG@.SupData load(String key) {
  @PKG@.SupData d = new @PKG@.SupData(key);
  if (DIR == null) { d.bad = true; return d; }
  java.nio.file.Path f = fileOf(key);
  java.util.ArrayList back = new java.util.ArrayList();
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)); } finally { in.close(); }
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String k = (String) it.next();
        String v = p.getProperty(k).trim();
        if (k.equals("flask.auto")) d.fAuto = !v.equals("false");
        else if (k.equals("pouch.auto")) d.pAuto = !v.equals("false");
        else if (k.equals("given.flask")) d.givenF = v.equals("true");
        else if (k.equals("given.pouch")) d.givenP = v.equals("true");
        else if (k.equals("paid")) { String[] a = v.split(" "); for (int i = 0; i < a.length; i++) if (a[i].length() > 0) d.paid.add(a[i]); }
        else if (k.startsWith("skip.")) { if (v.equals("true")) d.skip.put(k.substring(5), Boolean.TRUE); }
        else if (k.startsWith("res.")) back.add(new String[] { k.substring(4), v });
        else if (k.startsWith("flask.") || k.startsWith("pouch.")) {
          long n = num(v, -1L);
          if (n > 0L) (k.startsWith("flask.") ? d.f : d.p).put(k.substring(6), Long.valueOf(n));
        }
      }
    }
  } catch (Throwable t) {
    d.bad = true;
    @PKG@.SupLog.warn("supplies/" + key + ".properties could not be read - that profile's Flask / Pouch is paused and the file is never written over: " + t);
    return d;
  }
  d.retot();
  for (int i = 0; i < back.size(); i++) {
    String[] r = (String[]) back.get(i);
    int bar = r[1].indexOf('|');
    if (bar < 0) continue;
    int k = (int) num(r[1].substring(0, bar), 0L);
    String id = r[1].substring(bar + 1);
    d.add(k, id, 1L);
    append(line("B", r[0], key, k, id, 1L, 0L, "start-up: a use that never finished (the server stopped mid-drink) - 1 x " + id + " went back to the store (undo: none)"));
    N.incrementAndGet(3);
  }
  if (!back.isEmpty()) save(d);
  return d;
}""")
sup_M(ssto, r"""
public static @PKG@.SupData peek(String key) { return key == null ? null : (@PKG@.SupData) DATA.get(key); }""")
sup_M(ssto, r"""
public static @PKG@.SupData get(String key) {
  if (key == null) return null;
  @PKG@.SupData d = (@PKG@.SupData) DATA.get(key);
  if (d != null) return d;
  d = load(key);
  Object o = DATA.putIfAbsent(key, d);
  return o != null ? (@PKG@.SupData) o : d;
}""")
# the 10 s timer: an entry of THIS run 30 s old is settled (the engine saved the inventory meanwhile) - D line; a failed append retries
sup_M(ssto, r"""
public static int settle(long now) {
  int n = 0;
  java.util.Iterator it = OPEN.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry me = (java.util.Map.Entry) it.next();
    Object[] e = (Object[]) me.getValue();
    if (!((Boolean) e[7]).booleanValue() || ((Long) e[6]).longValue() + SETTLE_MS > now) continue;
    @PKG@.SupData dd = (@PKG@.SupData) DATA.get(e[1]);
    if (dd != null && dd.isDirty()) continue;   // the store file does not hold this change yet (a failed write): never settle it
    if (!append(line("D", (String) me.getKey(), (String) e[1], ((Integer) e[2]).intValue(), (String) e[3], ((Long) e[4]).longValue(), ((Long) e[5]).longValue(), "settled"))) break;
    it.remove();
    n++;
    N.incrementAndGet(9);
  }
  return n;
}""")

# ---------------------------------------------------------------- SupEng: engine helpers (world thread)
seng = smk("SupEng")
SUP_CLASSES.append(seng)
sup_F(seng, "public static volatile int MI_U = -1;")
sup_F(seng, "public static volatile int MI_E = -1;")
sup_M(seng, r"""
public static int markIndex(boolean empty) {
  int i = empty ? MI_E : MI_U;
  if (i >= 0) return i;
  try { i = @EFX@.getAssetMap().getIndex(empty ? @PKG@.SupDefs.MARK_E : @PKG@.SupDefs.MARK); } catch (Throwable t) { i = -1; }
  if (i >= 0) { if (empty) MI_E = i; else MI_U = i; }
  return i;
}""")
sup_M(seng, r"""
public static boolean takeMarker(@ST@ st, @REF@ r, @CAC@ acc, boolean empty) {
  int i = markIndex(empty);
  if (i < 0) return false;
  @ECC@ e = (@ECC@) st.getComponent(r, @ECC@.getComponentType());
  if (e == null || !e.hasEffect(i)) return false;
  e.removeEffect(r, i, acc);
  return true;
}""")
sup_M(seng, r"""
public static java.util.Map chains(@ST@ st, @REF@ r) {
  Object im = st.getComponent(r, @IMOD@.get().getInteractionManagerComponent());
  if (!(im instanceof @IMGR@)) return null;
  return (java.util.Map) ((@IMGR@) im).getChains();
}""")
sup_M(seng, r"""
public static boolean alive(@ST@ st, @REF@ r, Object chain) {
  if (chain == null) return false;
  java.util.Map m = chains(st, r);
  if (m == null) return false;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) if (it.next() == chain) return true;
  return false;
}""")
sup_M(seng, r"""
public static boolean secondaryRunning(@ST@ st, @REF@ r) {
  try {
    java.util.Map m = chains(st, r);
    if (m == null) return false;
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {
      Object c = it.next();
      if (c instanceof @ICHN@ && ((@ICHN@) c).getType() == @ITYP@.Secondary) return true;
    }
  } catch (Throwable t) { }
  return false;
}""")
sup_M(seng, r"""
public static boolean crouching(@ST@ st, @REF@ r) {
  try {
    @MSC@ m = (@MSC@) st.getComponent(r, @MSC@.getComponentType());
    return m != null && m.getMovementStates() != null && m.getMovementStates().crouching;
  } catch (Throwable t) { return false; }
}""")
sup_M(seng, r"""
public static @WLD@ worldOf(@ST@ st) {
  try { Object ext = st == null ? null : st.getExternalData(); return ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null; } catch (Throwable t) { return null; }
}""")
# the player's sections: 0 hotbar, 1 storage, 2 backpack, 3 utility, 4 tools (moves only ever use 1 + 2; a give 1, 0, 2)
sup_M(seng, r"""
public static @IC@[] secs(@INV@ inv) {
  if (inv == null) return new @IC@[0];
  return new @IC@[] { inv.getHotbar(), inv.getStorage(), inv.getBackpack(), inv.getUtility(), inv.getTools() };
}""")
sup_M(seng, r"""
public static boolean plain(@IS@ s) {
  try { org.bson.BsonDocument d = s.getMetadata(); return d == null || d.isEmpty(); } catch (Throwable t) { return false; }
}""")
sup_M(seng, r"""
public static int qtyOf(@IC@ c, short sl, String id) {
  try {
    @IS@ s = c.getItemStack(sl);
    return s != null && !s.isEmpty() && id.equals(s.getItemId()) ? s.getQuantity() : 0;
  } catch (Throwable t) { return 0; }
}""")
# that id in hotbar + storage + backpack (every stack) - the before / after counts and the recovery rule
sup_M(seng, r"""
public static long countId(@IC@[] cs, String id) {
  long n = 0L;
  for (int c = 0; c < 3 && c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) n = n + qtyOf(cs[c], s, id);
  }
  return n;
}""")
sup_M(seng, r"""
public static int ours(@IC@[] cs, int k) {
  int n = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      if (it != null && !it.isEmpty() && @PKG@.SupDefs.kindOf(it.getItemId()) == k) n++;
    }
  }
  return n;
}""")
sup_M(seng, r"""
public static String nameText(int k, @PKG@.SupData d) {
  return @PKG@.SupDefs.kindName(k) + " (" + (d == null ? 0L : d.tot(k)) + ")";
}""")
sup_M(seng, r"""
public static String descText(int k, @PKG@.SupData d) {
  String nx = d == null ? null : d.next(k);
  if (!@PKG@.SupCfg.ON) return "Switched off on this server. Crouch + right click: see what is inside.";
  if (nx == null) return "Empty - " + @PKG@.SupDefs.what(k) + " in your storage go in by themselves" + (d != null && d.auto(k) ? "" : " once Auto-fill is ON") + ". Crouch + right click: open.";
  int more = d.kinds(k) - 1;
  return "Next: " + @PKG@.SupDefs.name(k, nx) + (more > 0 ? " - then " + more + " more kind" + (more == 1 ? "" : "s") : "") + ". Right click: " + (k == 0 ? "drink" : "eat") + ". Crouch + right click: open.";
}""")
# the held copy's stack: the loaded id of the next item (Empty when there is none or the switch is off) + the ItemDisplay name / line
sup_M(seng, r"""
public static @IS@ display(int k, @PKG@.SupData d) {
  String nx = (d == null || !@PKG@.SupCfg.ON) ? null : d.next(k);
  @IS@ s = new @IS@(@PKG@.SupDefs.loadedId(k, nx), 1);
  return s.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(@MSG@.raw(nameText(k, d)), @MSG@.raw(descText(k, d))));
}""")
sup_M(seng, r"""
public static boolean sameMeta(@IS@ a, @IS@ b) {
  try {
    org.bson.BsonDocument x = a.getMetadata();
    org.bson.BsonDocument y = b.getMetadata();
    if (x == null) return y == null || y.isEmpty();
    return x.equals(y);
  } catch (Throwable t) { return false; }
}""")
# every copy (any section) -> its display stack; only when the id or the text changed; compare-and-swap (FP0 replaceItemStackInSlot)
sup_M(seng, r"""
public static int sync(@IC@[] cs, @PKG@.SupData d) {
  int n = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ old = cs[c].getItemStack(s);
      if (old == null || old.isEmpty()) continue;
      int k = @PKG@.SupDefs.kindOf(old.getItemId());
      if (k < 0) continue;
      @IS@ want = display(k, d);
      if (want.getItemId().equals(old.getItemId()) && sameMeta(old, want)) continue;
      try {
        @ISST@ tx = cs[c].replaceItemStackInSlot(s, old, want);
        if (tx != null && tx.succeeded()) n++;
      } catch (Throwable t) { @PKG@.SupLog.warnOnce("sync", "the held Flask / Pouch could not be updated: " + t); }
    }
  }
  return n;
}""")

# ---------------------------------------------------------------- the lifelong items (tools/skyyonce.py PREFIX MODE)
LIFE_F = ONCE.emit(pool, PKG, "FlaskOnce", item=SUP_FEMPTY, name="Potion Flask", tag="[Cooking]", recall="/flask", mod="SkyyCooking",
                   on_expr=PKG + ".SupCfg.LIFELONG", info_col=SUI.COLOR["success"], warn_col=SUI.STATUS_INFO["gold"], item_prefix=SUP_FPRE)
LIFE_P = ONCE.emit(pool, PKG, "PouchOnce", item=SUP_PEMPTY, name="Food Pouch", tag="[Cooking]", recall="/pouch", mod="SkyyCooking",
                   on_expr=PKG + ".SupCfg.LIFELONG", info_col=SUI.COLOR["success"], warn_col=SUI.STATUS_INFO["gold"], item_prefix=SUP_PPRE)
SUP_LIFE_SETUP = LIFE_F["setup"] + LIFE_P["setup"]
SUP_LIFE_SHUTDOWN = LIFE_F["shutdown"] + LIFE_P["shutdown"]
SUP_CLASSES.extend(LIFE_F["classes"] + LIFE_P["classes"])

# ---------------------------------------------------------------- SupOps: recover, fill, take, first give, the sweep
sops = smk("SupOps")
SUP_CLASSES.append(sops)
sup_F(sops, "public static final java.util.concurrent.ConcurrentHashMap PKC = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> Object[] { epoch, pkey }
# the profile key + this mod's cache of it (supply:fn:claims answers only for the profile the cache knows)
sup_M(sops, r"""
public static String pkey(java.util.UUID u) {
  Object ep = null;
  try { ep = @PKG@.SupLog.bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { ep = null; }
  String k = @PKG@.Cook.pkey(u);
  PKC.put(u, new Object[] { ep, k });
  return k;
}""")
sup_M(sops, r"""
public static String cachedKey(java.util.UUID u) {
  Object[] c = (Object[]) PKC.get(u);
  if (c == null) return null;
  Object ep = null;
  try { ep = @PKG@.SupLog.bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { ep = null; }
  if (c[0] == null ? ep != null : !c[0].equals(ep)) return null;
  return (String) c[1];
}""")
# the recovery rule (pure): was the move of an open entry saved with the inventory? C: count <= n0 - qty; T: count >= n0 + qty
sup_M(sops, r"""
public static boolean saved(String kind, long cnt, long n0, long q) {
  return kind.equals("C") ? cnt <= n0 - q : cnt >= n0 + q;
}""")
# apply one recovery decision; the paid flag after the save = "the store file holds this entry's effect" (idempotent if it runs again)
sup_M(sops, r"""
public static String settleOne(@PKG@.SupData d, String seq, Object[] e, boolean ok) {
  String kind = (String) e[0];
  int k = ((Integer) e[2]).intValue();
  String id = (String) e[3];
  long q = ((Long) e[4]).longValue();
  boolean paid = d.paid.contains(seq);
  String what;
  if (kind.equals("C")) {
    if (ok) { if (!paid) { d.add(k, id, q); d.paid.add(seq); } what = "kept: " + q + " x " + id + " left the inventory before the stop" + (paid ? "" : " - credited now"); }
    else { if (paid) { d.add(k, id, -q); d.paid.remove(seq); } what = "undone: the inventory came back with the " + q + " x " + id + (paid ? " - the store credit was taken back" : ""); }
  } else {
    if (ok) { if (!paid) { d.add(k, id, -q); d.paid.add(seq); } what = "kept: " + q + " x " + id + " reached the inventory before the stop" + (paid ? "" : " - debited now"); }
    else { if (paid) { d.add(k, id, q); d.paid.remove(seq); } what = "undone: the inventory came back without the " + q + " x " + id + (paid ? " - they went back to the store" : ""); }
  }
  return what;
}""")
# HIGH 1 (critic): the open entries of ONE (profile, id) are a chain in time order - state_0 = the first entry's n0, state_j = state_(j-1)
# + (C: -qty, T: +qty). The live count names the state the inventory was saved at: the largest j with count == state_j -> entries 1..j
# were saved, the rest undone. No j matches -> the per-entry rule (saved()). Pure (the harness calls it); -1 = no match.
sup_M(sops, r"""
public static int chainCut(java.util.ArrayList l, long cnt) {
  if (l == null || l.isEmpty()) return -1;
  Object[] e0 = (Object[]) ((Object[]) l.get(0))[1];
  long st = ((Long) e0[5]).longValue();
  int best = st == cnt ? 0 : -1;
  for (int x = 0; x < l.size(); x++) {
    Object[] e = (Object[]) ((Object[]) l.get(x))[1];
    long q = ((Long) e[4]).longValue();
    st = st + (((String) e[0]).equals("C") ? -q : q);
    if (st == cnt) best = x + 1;
  }
  return best;
}""")
# time order (then seq) - a plain insertion sort of { seq, entry } pairs
sup_M(sops, r"""
public static void byTime(java.util.ArrayList l) {
  for (int i = 1; i < l.size(); i++) {
    Object[] a = (Object[]) l.get(i);
    int j = i - 1;
    while (j >= 0) {
      Object[] b = (Object[]) l.get(j);
      long ta = ((Long) ((Object[]) a[1])[6]).longValue();
      long tb = ((Long) ((Object[]) b[1])[6]).longValue();
      if (tb < ta || (tb == ta && ((String) b[0]).compareTo((String) a[0]) <= 0)) break;
      l.set(j + 1, b);
      j--;
    }
    l.set(j + 1, a);
  }
}""")
sup_M(sops, r"""
public static int recover(@IC@[] cs, @PKG@.SupData d) {
  java.util.TreeMap byId = new java.util.TreeMap();
  java.util.Iterator it = @PKG@.SupStore.OPEN.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry me = (java.util.Map.Entry) it.next();
    Object[] e = (Object[]) me.getValue();
    if (!d.key.equals(e[1]) || ((Boolean) e[7]).booleanValue()) continue;
    java.util.ArrayList l = (java.util.ArrayList) byId.get(e[3]);
    if (l == null) { l = new java.util.ArrayList(); byId.put(e[3], l); }
    l.add(new Object[] { me.getKey(), e });
  }
  if (byId.isEmpty()) return 0;
  java.util.ArrayList done = new java.util.ArrayList();
  java.util.Iterator ii = byId.entrySet().iterator();
  while (ii.hasNext()) {
    java.util.Map.Entry ie = (java.util.Map.Entry) ii.next();
    java.util.ArrayList l = (java.util.ArrayList) ie.getValue();
    byTime(l);
    long cnt = @PKG@.SupEng.countId(cs, (String) ie.getKey());
    int cut = chainCut(l, cnt);
    for (int x = 0; x < l.size(); x++) {
      String seq = (String) ((Object[]) l.get(x))[0];
      Object[] e = (Object[]) ((Object[]) l.get(x))[1];
      boolean ok = cut >= 0 ? x < cut : saved((String) e[0], cnt, ((Long) e[5]).longValue(), ((Long) e[4]).longValue());
      String what = settleOne(d, seq, e, ok) + (cut >= 0 ? " (chain of " + l.size() + ", inventory " + cnt + ")" : " (per entry, inventory " + cnt + ")");
      done.add(new Object[] { seq, e, Boolean.valueOf(ok), what });
    }
  }
  if (!@PKG@.SupStore.save(d)) return -1;
  int n = 0;
  for (int i = 0; i < done.size(); i++) {
    Object[] x = (Object[]) done.get(i);
    Object[] e = (Object[]) x[1];
    if (!@PKG@.SupStore.append(@PKG@.SupStore.line(((Boolean) x[2]).booleanValue() ? "D" : "X", (String) x[0], d.key, ((Integer) e[2]).intValue(), (String) e[3], ((Long) e[4]).longValue(), ((Long) e[5]).longValue(), "recovered at start-up - " + x[3]))) continue;   // LOW 8: stays OPEN (+ paid) - the next run decides it again, the same way
    @PKG@.SupStore.OPEN.remove(x[0]);
    d.paid.remove(x[0]);
    n++;
    @PKG@.SupStore.N.incrementAndGet(7);
    @PKG@.SupLog.info("recovered " + x[0] + " (" + d.key + "): " + x[3]);
  }
  return n;
}""")
sup_M(sops, r"""
public static void fullNotice(@PR@ pr, @PKG@.SupData d, int k) {
  if (pr == null) return;
  long ms = @PKG@.SupCfg.FULL_NOTICE_MS;
  if (!@PKG@.SupLog.due(pr.getUuid(), "full" + k, ms <= 0L ? 1L : ms)) return;
  @PKG@.SupLog.pop(pr, "Your " + @PKG@.SupDefs.kindName(k) + " is full", d.tot(k) + " / " + @PKG@.SupCfg.cap(k) + " - the rest stays in your inventory.");
}""")
# THE FILL (auto-fill and Put all in): main storage + backpack ONLY (cs[1], cs[2]; never the hotbar), plain stacks of a fillable id;
# per stack: journal C (fsynced) -> remove -> read back -> credit only what left (Q amends a short removal) -> ONE store write at the end
sup_M(sops, r"""
public static int fill(@PR@ pr, @IC@[] cs, @PKG@.SupData d, int k, boolean manual) {
  if (d == null || d.bad || cs.length < 3) return 0;
  long cap = (long) @PKG@.SupCfg.cap(k);
  int moved = 0;
  boolean full = false;
  boolean stop = false;
  for (int c = 1; c <= 2 && !full && !stop; c++) {
    @IC@ ic = cs[c];
    if (ic == null) continue;
    short capn = ic.getCapacity();
    for (short s = 0; s < capn; s++) {
      @IS@ it = ic.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (@PKG@.SupDefs.fillKind(id) != k) continue;
      if (!manual && (d.skipped(id) || @PKG@.SupStore.muted(d.key, id))) continue;   // HIGH 2: a Take keeps it out for 60 s
      if (!@PKG@.SupEng.plain(it)) continue;
      long room = cap - d.tot(k);
      if (room <= 0L) { full = true; break; }
      int q = it.getQuantity();
      if ((long) q > room) q = (int) room;
      long n0 = @PKG@.SupEng.countId(cs, id);
      String seq = @PKG@.SupStore.nextSeq();
      if (!@PKG@.SupStore.append(@PKG@.SupStore.line("C", seq, d.key, k, id, (long) q, n0, (manual ? "put in" : "auto-fill") + ": " + q + " x " + id + " from " + (c == 1 ? "storage" : "backpack") + " slot " + s + " into the " + @PKG@.SupDefs.kindName(k) + " (undo: take " + q + " out on the Supplies page)"))) { stop = true; break; }
      @PKG@.SupStore.jopen(seq, "C", d.key, k, id, (long) q, n0);
      int b = @PKG@.SupEng.qtyOf(ic, s, id);
      try { ic.removeItemStackFromSlot(s, q); } catch (Throwable t) { }
      int r = b - @PKG@.SupEng.qtyOf(ic, s, id);
      if (r <= 0) {
        @PKG@.SupStore.append(@PKG@.SupStore.line("X", seq, d.key, k, id, (long) q, n0, "nothing left the slot - cancelled"));
        @PKG@.SupStore.OPEN.remove(seq);
        continue;
      }
      if (r != q) {
        @PKG@.SupStore.amend(seq, (long) r);
        @PKG@.SupStore.append(@PKG@.SupStore.line("Q", seq, d.key, k, id, (long) r, n0, "only " + r + " of " + q + " left the slot"));
      }
      d.add(k, id, (long) r);
      d.paid.add(seq);
      moved = moved + r;
      @PKG@.SupStore.N.incrementAndGet(0);
    }
  }
  if (moved > 0) @PKG@.SupStore.save(d);
  if (full) fullNotice(pr, d, k);
  return moved;
}""")
# TAKE OUT: journal T (fsynced) -> debit + paid in ONE store write -> give storage first (storage, hotbar, backpack), counted -> whatever
# did not fit goes back to the store (Q amends, X when nothing moved)
sup_M(sops, r"""
public static String take(@IC@[] cs, @PKG@.SupData d, int k, String id, long n) {
  if (d == null || d.bad || id == null || id.length() == 0 || cs.length < 3) return "-Pick an item first.";
  long have = d.get(k, id);
  long q = n < have ? n : have;
  if (q <= 0L) return "-None left.";
  if (q > 100000L) q = 100000L;
  long n0 = @PKG@.SupEng.countId(cs, id);
  String seq = @PKG@.SupStore.nextSeq();
  if (!@PKG@.SupStore.append(@PKG@.SupStore.line("T", seq, d.key, k, id, q, n0, "take out: " + q + " x " + id + " from the " + @PKG@.SupDefs.kindName(k) + " into the inventory (undo: put them back - Put all in)"))) return "-Could not write the journal - nothing was taken.";
  @PKG@.SupStore.jopen(seq, "T", d.key, k, id, q, n0);
  d.add(k, id, -q);
  d.paid.add(seq);
  if (!@PKG@.SupStore.save(d)) {
    d.add(k, id, q);
    d.paid.remove(seq);
    @PKG@.SupStore.append(@PKG@.SupStore.line("X", seq, d.key, k, id, q, n0, "the store could not be written - nothing taken"));
    @PKG@.SupStore.OPEN.remove(seq);
    return "-Your store could not be saved - nothing was taken.";
  }
  int[] order = new int[] { 1, 0, 2 };
  long left = q;
  for (int o = 0; o < order.length && left > 0L; o++) {
    @IC@ ic = cs[order[o]];
    if (ic == null) continue;
    long b = @PKG@.SupEng.countId(cs, id);
    try { ic.addItemStack(new @IS@(id, (int) left)); } catch (Throwable t) { @PKG@.SupLog.warnOnce("give", "adding to the inventory failed: " + t); }
    long got = @PKG@.SupEng.countId(cs, id) - b;
    if (got > 0L) left = left - got;
  }
  long given = q - left;
  if (left > 0L) {
    d.add(k, id, left);
    if (given <= 0L) {
      d.paid.remove(seq);
      @PKG@.SupStore.save(d);
      @PKG@.SupStore.append(@PKG@.SupStore.line("X", seq, d.key, k, id, q, n0, "no room in the inventory - nothing moved"));
      @PKG@.SupStore.OPEN.remove(seq);
      return "-No room in your inventory - nothing was taken.";
    }
    @PKG@.SupStore.amend(seq, given);
    @PKG@.SupStore.append(@PKG@.SupStore.line("Q", seq, d.key, k, id, given, n0, "only " + given + " of " + q + " fitted - the rest stayed in the store"));
    @PKG@.SupStore.save(d);
  }
  @PKG@.SupStore.N.incrementAndGet(1);
  @PKG@.SupStore.mute(d.key, id);
  return "+Took " + given + " x " + @PKG@.SupDefs.name(k, id) + (left > 0L ? " - no room for " + left + " more" : "") + ". It stays out of Auto-fill for now (Put all in puts it back).";
}""")
# the first give: each profile gets one of each ONCE (given.* marker; existing profiles too), storage first through the lifelong recall
sup_M(sops, r"""
public static void give(@PR@ pr, @INV@ inv, @PKG@.SupData d) {
  for (int k = 0; k < 2; k++) {
    if (d.given(k)) continue;
    String rr = k == 0 ? @PKG@.FlaskOnce.recall(pr, @PKG@.FlaskOnce.secs(inv)) : @PKG@.PouchOnce.recall(pr, @PKG@.PouchOnce.secs(inv));
    if ("+given".equals(rr) || "=have".equals(rr)) {
      d.setGiven(k);
      @PKG@.SupStore.save(d);
      @PKG@.SupStore.append(@PKG@.SupStore.line("G", @PKG@.SupStore.nextSeq(), d.key, k, @PKG@.SupDefs.loadedId(k, null), 1L, 0L, ("+given".equals(rr) ? "first " + @PKG@.SupDefs.kindName(k) + " given" : "the profile already had one") + " (undo: none - it is lifelong; " + @PKG@.SupDefs.cmd(k) + " gives it back)"));
      if ("+given".equals(rr)) @PKG@.SupLog.tell(pr, "[Cooking] You got a " + @PKG@.SupDefs.kindName(k) + " (in your storage - drag it to your hotbar). " + (k == 0 ? "Healing potions" : "Cooked food") + " you pick up go in by themselves; right click " + (k == 0 ? "drinks" : "eats") + " the weakest first. Crouch + right click opens it.", @PKG@.SupLog.OK);
    } else if ("-full".equals(rr) && @PKG@.SupLog.due(pr.getUuid(), "givefull" + k, 600000L)) {
      @PKG@.SupLog.tell(pr, "[Cooking] Your " + @PKG@.SupDefs.kindName(k) + " is waiting - make room in your inventory and type " + @PKG@.SupDefs.cmd(k) + ".", @PKG@.SupLog.INFO);
    }
  }
}""")
sup_M(sops, r"""
public static boolean syncNow(@ST@ st, @REF@ r, java.util.UUID u, @IC@[] cs, @PKG@.SupData d) {
  if (@PKG@.SupStore.RES.get(u) != null || @PKG@.SupEng.secondaryRunning(st, r)) { @PKG@.SupStore.SYNC.put(u, Boolean.TRUE); return false; }
  @PKG@.SupEng.sync(cs, d);
  return true;
}""")
# THE SWEEP (world thread, the player's own task): busy -> later; load + recover the profile's store; first gives; auto-fill; sync
sup_M(sops, r"""
public static String sweep(@PR@ pr, @PLA@ p, @ST@ st, @REF@ r) {
  java.util.UUID u = pr.getUuid();
  if (@PKG@.SupLog.busy(u)) return "busy";
  String k = pkey(u);
  @PKG@.SupData d = @PKG@.SupStore.get(k);
  if (d == null || d.bad) return "bad";
  @INV@ inv = p.getInventory();
  @IC@[] cs = @PKG@.SupEng.secs(inv);
  if (!d.ready) {
    if (recover(cs, d) < 0) return "busy";
    d.ready = true;
  }
  give(pr, inv, d);
  if (@PKG@.SupCfg.ON) {
    for (int kk = 0; kk < 2; kk++) if (d.auto(kk)) fill(pr, cs, d, kk, false);
  }
  syncNow(st, r, u, cs, d);
  return "ok";
}""")
sup_M(sops, r"""
public static java.util.ArrayList rows(@PKG@.SupData d, int k) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (d == null) return l;
  String[] a = @PKG@.SupDefs.srcs(k);
  for (int i = 0; i < a.length; i++) if (d.get(k, a[i]) > 0L) l.add(a[i]);
  return l;
}""")
sup_M(sops, r"""
public static boolean anyFillable(@IC@[] cs, @PKG@.SupData d) {
  for (int c = 1; c <= 2 && c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      int k = @PKG@.SupDefs.fillKind(it.getItemId());
      if (k >= 0 && d.auto(k) && !d.skipped(it.getItemId()) && !@PKG@.SupStore.muted(d.key, it.getItemId())) return true;
    }
  }
  return false;
}""")

# ---------------------------------------------------------------- SupTask: ONE deduplicated world-thread task per player (the skyyonce pattern)
stask = smk("SupTask", None, "java.lang.Runnable")
SUP_CLASSES.append(stask)
for _d in ("public @PR@ pr;", "public @WLD@ world;", "public java.util.UUID wu;", "public int tries;"):
    sup_F(stask, _d)
sup_C(stask, "public SupTask(@PR@ pr, @WLD@ w, java.util.UUID wu, int tries) { this.pr = pr; this.world = w; this.wu = wu; this.tries = tries; }")
sup_M(stask, r"""
public static boolean schedule(@PR@ pr, @WLD@ w, long delay, int tries) {
  if (pr == null || w == null) return false;
  java.util.UUID u = null;
  try { u = pr.getUuid(); } catch (Throwable t) { return false; }
  if (u == null || @PKG@.SupStore.PEND.putIfAbsent(u, Boolean.TRUE) != null) return false;
  try {
    @PKG@.SupTask t = new @PKG@.SupTask(pr, w, pr.getWorldUuid(), tries);
    if (delay <= 0L) w.execute(t);
    else java.util.concurrent.CompletableFuture.delayedExecutor(delay, java.util.concurrent.TimeUnit.MILLISECONDS, (java.util.concurrent.Executor) w).execute(t);
    return true;
  } catch (Throwable x) { @PKG@.SupStore.PEND.remove(u); @PKG@.SupLog.warnOnce("sched", "a world task could not be queued: " + x); return false; }
}""")
sup_M(stask, r"""
public void run() {
  java.util.UUID u = null;
  try {
    u = this.pr.getUuid();
    @PKG@.SupStore.PEND.remove(u);
    if (!this.pr.isValid()) return;
    java.util.UUID nw = this.pr.getWorldUuid();
    if (nw == null || !nw.equals(this.wu)) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PKG@.SupStore.N.incrementAndGet(10);
    String res = p.isWaitingForClientReady() ? "busy" : @PKG@.SupOps.sweep(this.pr, p, st, r);
    if ("busy".equals(res) && this.tries < 30) schedule(this.pr, this.world, 2000L, this.tries + 1);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("task", "the Supplies world task failed: " + t); }
}""")
sset = smk("SupSettle", None, "java.lang.Runnable")
SUP_CLASSES.append(sset)
sup_C(sset, "public SupSettle() { }")
sup_M(sset, r"""
public void run() {
  try { @PKG@.SupStore.settle(System.currentTimeMillis()); } catch (Throwable t) { @PKG@.SupLog.warnOnce("settle", "the journal settle timer failed: " + t); }
}""")

# ---------------------------------------------------------------- SupCore: the use (reserve / commit / return) - the FP0 runtime
score = smk("SupCore")
SUP_CLASSES.append(score)
sup_M(score, r"""
public static boolean reserve(java.util.UUID u, @PKG@.SupData d, int k, String id, Object chain) {
  String seq = @PKG@.SupStore.nextSeq();
  d.add(k, id, -1L);
  d.res.put(seq, k + "|" + id);
  if (!@PKG@.SupStore.save(d)) { d.add(k, id, 1L); d.res.remove(seq); return false; }
  @PKG@.SupStore.append(@PKG@.SupStore.line("R", seq, d.key, k, id, 1L, 0L, "use: 1 x " + id + " reserved for a " + (k == 0 ? "drink" : "bite") + " (undo: it goes back when the use is let go, or at start-up)"));
  @PKG@.SupStore.RES.put(u, new Object[] { Integer.valueOf(k), id, chain, Long.valueOf(System.currentTimeMillis()), Long.valueOf(0L), seq, d.key });
  @PKG@.SupStore.N.incrementAndGet(4);
  return true;
}""")
sup_M(score, r"""
public static void commit(java.util.UUID u, Object[] res) {
  @PKG@.SupStore.RES.remove(u);
  @PKG@.SupData d = @PKG@.SupStore.peek((String) res[6]);
  if (d != null) {
    d.res.remove(res[5]);
    d.touch();
    @PKG@.SupStore.saveHard(d, "a use");
  }
  @PKG@.SupStore.append(@PKG@.SupStore.line("U", (String) res[5], (String) res[6], ((Integer) res[0]).intValue(), (String) res[1], 1L, 0L, "use: 1 x " + res[1] + " used (undo: none - it was drunk / eaten)"));
  @PKG@.SupStore.N.incrementAndGet(2);
  @PKG@.SupStore.SYNC.put(u, Boolean.TRUE);
}""")
sup_M(score, r"""
public static void giveBack(java.util.UUID u, Object[] res, String why) {
  @PKG@.SupStore.RES.remove(u);
  @PKG@.SupData d = @PKG@.SupStore.peek((String) res[6]);
  if (d != null) {
    d.res.remove(res[5]);
    d.add(((Integer) res[0]).intValue(), (String) res[1], 1L);
    @PKG@.SupStore.saveHard(d, "a returned use");
  }
  @PKG@.SupStore.append(@PKG@.SupStore.line("B", (String) res[5], (String) res[6], ((Integer) res[0]).intValue(), (String) res[1], 1L, 0L, "returned: " + why + " - 1 x " + res[1] + " back in the store (nothing used)"));
  @PKG@.SupStore.N.incrementAndGet(3);
  @PKG@.SupStore.SYNC.put(u, Boolean.TRUE);
}""")
sup_M(score, r"""
public static void onStart(@ICSE@ e, @REF@ r, @ST@ st, @CB@ buf) {
  if (!"Secondary".equals(String.valueOf(e.getType()))) return;
  @IS@ held = e.getContext() == null ? null : e.getContext().getHeldItem();
  String id = held == null || held.isEmpty() ? null : held.getItemId();
  int k = @PKG@.SupDefs.kindOf(id);
  if (k < 0) return;
  @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  String src = @PKG@.SupDefs.srcOf(id);
  if (src == null) return;
  if (src.length() == 0) { @PKG@.SupStore.WATCH.put(u, new Object[] { Long.valueOf(System.currentTimeMillis()), Integer.valueOf(k) }); return; }
  if (@PKG@.SupEng.crouching(st, r)) return;
  if (@PKG@.Cook.creative(st, r)) return;
  Object[] res = (Object[]) @PKG@.SupStore.RES.get(u);
  if (res != null) {
    if (@PKG@.SupEng.takeMarker(st, r, (@CAC@) buf, false)) commit(u, res);
    else if (!@PKG@.SupEng.alive(st, r, res[2])) giveBack(u, res, "the last use ended before it finished");
    else { e.setCancelled(true); @PKG@.SupStore.N.incrementAndGet(5); return; }
  }
  if (!@PKG@.SupCfg.ON || @PKG@.SupLog.busy(u)) { e.setCancelled(true); @PKG@.SupStore.SYNC.put(u, Boolean.TRUE); return; }
  @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.pkey(u));
  if (d == null || !d.ready || d.bad) {
    e.setCancelled(true);
    @PKG@.SupStore.N.incrementAndGet(5);
    @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0);
    return;
  }
  if (d.get(k, src) <= 0L) { e.setCancelled(true); @PKG@.SupStore.N.incrementAndGet(5); @PKG@.SupStore.SYNC.put(u, Boolean.TRUE); return; }
  if (!reserve(u, d, k, src, e.getChain())) { e.setCancelled(true); @PKG@.SupStore.N.incrementAndGet(5); }
}""")
sup_M(score, r"""
public static void emptyLine(@PR@ pr, int k) {
  if (!@PKG@.SupLog.due(pr.getUuid(), "empty" + k, 2000L)) return;
  @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.cachedKey(pr.getUuid()));
  String nm = @PKG@.SupDefs.kindName(k);
  if (!@PKG@.SupCfg.ON) { @PKG@.SupLog.pop(pr, nm, "Switched off on this server. Crouch + right click to see what is inside."); return; }
  boolean auto = d == null || d.auto(k);
  @PKG@.SupLog.pop(pr, "Your " + nm + " is empty", (k == 0 ? "Healing potions go in by themselves" : "Cooked food goes in by itself") + (auto ? " (Auto-fill ON)" : " once Auto-fill is ON") + ". Crouch + right click to open it.");
}""")
sup_M(score, r"""
public static void tick(@REF@ r, @ST@ st, @CB@ cb, @PR@ pr) {
  java.util.UUID u = pr.getUuid();
  Object[] res = (Object[]) @PKG@.SupStore.RES.get(u);
  Object[] w = (Object[]) @PKG@.SupStore.WATCH.get(u);
  if (res == null && w == null && @PKG@.SupStore.SYNC.get(u) == null) return;
  long now = System.currentTimeMillis();
  if (res != null) {
    if (@PKG@.SupEng.takeMarker(st, r, (@CAC@) cb, false)) commit(u, res);
    else {
      long t0 = ((Long) res[3]).longValue();
      if (@PKG@.SupEng.alive(st, r, res[2]) && now - t0 < 30000L) res[4] = Long.valueOf(0L);
      else {
        long gone = ((Long) res[4]).longValue();
        if (gone == 0L) res[4] = Long.valueOf(now);
        else if (now - gone >= 250L) giveBack(u, res, "let go before it finished");
      }
    }
  }
  if (w != null) {
    if (@PKG@.SupEng.takeMarker(st, r, (@CAC@) cb, true)) { @PKG@.SupStore.WATCH.remove(u); emptyLine(pr, ((Integer) w[1]).intValue()); }
    else if (now - ((Long) w[0]).longValue() > 3000L) @PKG@.SupStore.WATCH.remove(u);
  }
  if (@PKG@.SupStore.SYNC.get(u) != null && @PKG@.SupStore.RES.get(u) == null && !@PKG@.SupEng.secondaryRunning(st, r)) {
    @PKG@.SupStore.SYNC.remove(u);
    if (!@PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0)) @PKG@.SupStore.SYNC.put(u, Boolean.TRUE);
  }
}""")

# ---------------------------------------------------------------- the four hooks (ONE registerSystem per class)
sss = smk("SupStartSys", EES)
SUP_CLASSES.append(sss)
sup_C(sss, "public SupStartSys() { super(@ICSE@.class); }")
sup_M(sss, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
sup_M(sss, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || !(ev instanceof @ICSE@)) return;
    @PKG@.SupCore.onStart((@ICSE@) ev, chunk.getReferenceTo(idx), st, buf);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("start", "the Flask / Pouch use hook failed: " + t); }
}""")
stk = smk("SupTick", "com.hypixel.hytale.component.system.tick.EntityTickingSystem")
SUP_CLASSES.append(stk)
sup_C(stk, "public SupTick() { super(); }")
sup_M(stk, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
sup_M(stk, "public boolean isParallel(int a, int b) { return false; }")
sup_M(stk, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (chunk == null) return;
    if (@PKG@.SupStore.RES.isEmpty() && @PKG@.SupStore.SYNC.isEmpty() && @PKG@.SupStore.WATCH.isEmpty()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) store.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.SupCore.tick(r, store, cb, pr);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("tick", "the Flask / Pouch tick failed: " + t); }
}""")
sinv = smk("SupInvSys", EES)
SUP_CLASSES.append(sinv)
sup_C(sinv, "public SupInvSys() { super(@ICE@.class); }")
sup_M(sinv, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
sup_M(sinv, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @ICE@)) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if (u == null || @PKG@.SupStore.PEND.containsKey(u)) return;
    String k = @PKG@.SupOps.cachedKey(u);
    @PKG@.SupData d = @PKG@.SupStore.peek(k);
    if (d == null || !d.ready || !d.givenF || !d.givenP) { @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0); return; }
    if (!@PKG@.SupCfg.ON || (!d.fAuto && !d.pAuto)) return;
    @PLA@ p = (@PLA@) chunk.getComponent(idx, @PLA@.getComponentType());
    if (p == null) return;
    if (@PKG@.SupOps.anyFillable(@PKG@.SupEng.secs(p.getInventory()), d)) @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("inv", "the Flask / Pouch inventory hook failed: " + t); }
}""")
srdy = smk("SupReady", None, "java.util.function.Consumer")
SUP_CLASSES.append(srdy)
sup_C(srdy, "public SupReady() { }")
sup_M(srdy, r"""
public void accept(Object o) {
  try {
    if (!(o instanceof @PRE@)) return;
    @REF@ r = ((@PRE@) o).getPlayerRef();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 1500L, 0);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("ready", "the ready hook failed: " + t); }
}""")

# ---------------------------------------------------------------- the bridge functions (plain java.lang types; memory only)
scl = smk("SupClaimsFn", None, "java.util.function.Function")
SUP_CLASSES.append(scl)
sup_C(scl, "public SupClaimsFn() { }")
sup_M(scl, r"""
public Object apply(Object o) {
  try {
    if (!@PKG@.SupCfg.ON || !(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return Boolean.FALSE;
    java.util.UUID u = (java.util.UUID) a[0];
    String id = (String) a[1];
    int k = @PKG@.SupDefs.fillKind(id);
    if (k < 0 || @PKG@.SupLog.busy(u)) return Boolean.FALSE;
    @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.cachedKey(u));
    if (d == null || !d.ready || d.bad || !d.auto(k) || d.skipped(id) || @PKG@.SupStore.muted(d.key, id)) return Boolean.FALSE;
    return d.tot(k) < (long) @PKG@.SupCfg.cap(k) ? Boolean.TRUE : Boolean.FALSE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
scn = smk("SupCountsFn", None, "java.util.function.Function")
SUP_CLASSES.append(scn)
sup_C(scn, "public SupCountsFn() { }")
sup_M(scn, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = o instanceof Object[] && ((Object[]) o).length > 0 ? (java.util.UUID) ((Object[]) o)[0] : (java.util.UUID) o;
    if (u == null || @PKG@.SupLog.busy(u)) return null;
    @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.cachedKey(u));
    if (d == null || !d.ready || d.bad) return null;
    java.util.HashMap m = new java.util.HashMap();
    java.util.Iterator it = d.f.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put(e.getKey(), e.getValue()); }
    it = d.p.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put(e.getKey(), e.getValue()); }
    return m;
  } catch (Throwable t) { return null; }
}""")

# ---------------------------------------------------------------- THE PAGE: Storage > Supplies (kit 1.7 hub page; Menu-Pattern 3)
shubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, page=True)
SUP_CLASSES.append(shubb)
_SHROW = [r_ for r_ in SUI.HUB_TABS if r_[0] == "storage" and r_[1] == "supplies"]
assert len(_SHROW) == 1 and _SHROW[0][3] == "SkyyCooking" and _SHROW[0][5] == "flask", ("0.1.11: Storage > Supplies is SkyyCooking's contract tab", _SHROW)
SSH = SUI.hub_page("SkyySu", "storage", sub=True, footer=True, content_id="SkyySuC")
assert (SSH.w, SSH.h) == (SUI.HUB_PAGE_W, SUI.HUB_PAGE_H) and SSH.content_h == 676, ("0.1.11: the hub page", SSH.content_h)
SUP_HUBJ = SUI.java_hub_page(SSH, "supplies", cls="@PKG@.HubBar")
SIW, SCH = SSH.content_w, SSH.content_h
SUP_SUBW, SUP_AUTO_W = SUI.SUB_TAB_W, 260
SUP_SUBF = SIW - 2 * SUP_SUBW - SUI.SUB_TAB_GAP - SUP_AUTO_W
SUP_DW = SUI.DETAIL_W
SUP_DIN = SUP_DW - 32
SUP_LW = SIW - SUP_DW - 16
SUP_RW = SUP_LW - 2 * SUI.WELL_LIST_PAD - SUI.SCROLL_SIZE - SUI.SCROLL_SPACING
SUP_ROWMAX = 120          # rows drawn at most (a packet-size cap like SkyySacks' 150); the status line says how many more there are
SUP_PUT_W = 260
SUP_HINT_W = SIW - SUP_PUT_W - SUI.FOOT_GAP
assert SUI.assert_sub_tabs_fit(["Potion Flask", "Food Pouch"]) + SUP_SUBF + SUP_AUTO_W == SIW, "0.1.11: the sub row fits 1552"
assert SUP_SUBF > 0 and SUP_RW >= 600, ("0.1.11: list width", SUP_RW)
_J = SUI.J


def sjl(parent, mk):
    return SUI.java_append(parent, mk, page_root=True)


SPK = {
    "SUBF": SUI.spacer(w=SUP_SUBF),
    "AUTO": SUI.button("SkyySuAuto", "", "secondary", "small", w=SUP_AUTO_W, fit=False),
    "MAIN": SUI.group("SkyySuMain", "Left", w=SIW, h=SCH),
    "LS": SUI.scroll_list("SkyySuLs", h=SCH, w=SUP_LW, well=True),
    "DET": SUI.group("SkyySuD", "Top", w=SUP_DW, h=SCH, anchor={"left": 16}, pad=16, bg="well"),
    "EMPTY": SUI.empty_state("SkyySuEm", w=SUP_RW),
    "DIC": SUI.icon_cell("SkyySuDIc", item=_J("dic", "Potion_Health_Small"), size=96, state="static", look="plain"),
    "DNM": SUI.label("SkyySuDNm", "", "strong", w=SUP_DIN, h=30, col=_J("dcol", SUI.QUALITY["Common"]), anchor={"top": 10}, fit=False),
    "DCT": SUI.label("SkyySuDCt", "", "bold", w=SUP_DIN, h=24, fit=False),
    "DTX": SUI.label("SkyySuDTx", "", "caption", w=SUP_DIN, h=150, wrap=True, fit=False),
    "DHINT": SUI.label("SkyySuDHn", "", "caption", w=SUP_DIN, h=150, wrap=True, anchor={"top": 10}, fit=False),
    "T1": SUI.button("SkyySuT1", "Take 1", "primary", w=SUP_DIN, anchor={"top": 8}),
    "TA": SUI.button("SkyySuTa", "Take all", "secondary", w=SUP_DIN, anchor={"top": 8}),
    "SK": SUI.button("SkyySuSk", "", "secondary", w=SUP_DIN, anchor={"top": 8}, fit=False),
}
SUP_FOOT = [SUI.foot_info("SkyySuSt", SUP_HINT_W), SUI.spacer(w=SUI.FOOT_GAP), SUI.foot_button("SkyySuPut", "Put all in", SUP_PUT_W)]
SUP_CARD = SUI.list_card("SkyySuLs", "SkyySuR" + _J("i", "0"), SUP_RW, [
    {"id": "Nm", "text": _J("rnm", "Lesser Health Potion"), "kind": "rowName", "h": 26, "col": _J("rcol", SUI.QUALITY["Common"]),
     "tag": {"id": "Tg", "text": _J("rtg", "Next  -  x12"), "col": "value", "w": 200, "kind": "bold"}},
    {"id": "Sb", "text": _J("rsb", "Heals 30% of your health"), "kind": "rowSub", "h": 44, "col": "rowSub", "wrap": True}],
    look=[("selected", "i == selI"), "normal"], icon_item=_J("ric", "Potion_Health_Small"), var="card",
    action=SUI.list_card_button("SkyySuRb" + _J("i", "0"), "Details"))
SPP = {"SHELL": SSH.java("b"), "SUBF": sjl(SSH.sub, SPK["SUBF"]), "AUTO": sjl(SSH.sub, SPK["AUTO"]),
       "MAIN": "\n".join([sjl(SSH.content, SPK["MAIN"]), sjl("SkyySuMain", SPK["LS"]), sjl("SkyySuMain", SPK["DET"])]),
       "CARD": SUP_CARD.java("b"), "EMPTY": sjl("SkyySuLs", SPK["EMPTY"]),
       "DETON": "\n".join(sjl("SkyySuD", SPK[x]) for x in ("DIC", "DNM", "DCT", "DTX", "T1", "TA", "SK")),
       "DETOFF": sjl("SkyySuD", SPK["DHINT"]),
       "FOOT": "\n".join(sjl(SSH.foot, m_) for m_ in SUP_FOOT)}
# build-time check of the page (kit 1.7 recipe): the shell + rows 1 + 2 + the sub row + content + footer = 1600 x 980, no back / pager
_spv = SUI.hub_page_preview(SSH, tabs=[(r_[0], SUI.hub_tab_label("storage", r_[0])) for r_ in SUI.hub_page_tabs("storage")], my_tab="supplies")
_spv.extend(SUI.sub_tabs_preview("SkyySu", ["Potion Flask", "Food Pouch"], 0))
for _p_, _k_ in ((SSH.sub, "SUBF"), (SSH.sub, "AUTO"), (SSH.content, "MAIN"), ("SkyySuMain", "LS"), ("SkyySuMain", "DET"), ("SkyySuLs", "EMPTY"),
                 ("SkyySuD", "DIC"), ("SkyySuD", "DNM"), ("SkyySuD", "DCT"), ("SkyySuD", "DTX"), ("SkyySuD", "T1"), ("SkyySuD", "TA"), ("SkyySuD", "SK")):
    _spv.append((_p_, SPK[_k_]))
_spv.extend(list(SUP_CARD))
for _m in SUP_FOOT:
    _spv.append((SSH.foot, _m))
SUI.check_page(_spv, "SkyySu")
SUI.assert_proven(_spv, what="Supplies hub page")
SUI.check_sky_paths(_spv, tab_icons=True)
_smp = SUI.assert_menu_page(_spv, SSH, what="Supplies hub page")
assert _smp["rows"] == 2 and _smp["subs"] == 1, _smp
assert SUI.used_width(_spv, SSH.foot) <= SIW and SUI.used_width(_spv, SSH.sub) == SIW, "0.1.11: the footer / sub row fit 1552"
del _spv, _smp

spg = smk("SupPage", T["PAGE"])
SUP_CLASSES.append(spg)
for _d in ("public int tab;", "public String selSrc;", "public String info;",
           "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();"):
    sup_F(spg, _d)
sup_C(spg, r"""
public SupPage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab == 1 ? 1 : 0; this.selSrc = ""; this.info = "";
}""")
for _l in SUI.java_status_methods():
    sup_M(spg, _l)
sup_M(spg, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
sup_M(spg, r"""
public static int toInt(String s) {
  try { return Integer.parseInt(s.trim()); } catch (Throwable t) { return -1; }
}""")
SUP_BUILD = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.SupData d = @PKG@.SupStore.get(@PKG@.SupOps.pkey(u));
  if (d != null && !d.ready && !d.bad && !@PKG@.SupLog.busy(u)) {
    try { @PLA@ p0 = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); if (p0 != null) @PKG@.SupOps.sweep(this.playerRef, p0, st, ref); } catch (Throwable t) { }
  }
  boolean ok = d != null && d.ready && !d.bad;
  int kk = this.tab;
  java.util.ArrayList rows = ok ? @PKG@.SupOps.rows(d, kk) : new java.util.ArrayList();
  int shown = rows.size() < @ROWMAX@ ? rows.size() : @ROWMAX@;
  int selI = -1;
  for (int x = 0; x < shown; x++) if (((String) rows.get(x)).equals(this.selSrc)) selI = x;
  if (selI < 0 && shown > 0) { selI = 0; this.selSrc = (String) rows.get(0); }
  if (shown == 0) this.selSrc = "";
{{SHELL}}
  @HUBJAVA@
  @PKG@.HubBar.subTab(b, ev, "SkyySu", 0, "Potion Flask", kk == 0, "tab0", @SUBW@);
  @PKG@.HubBar.subTab(b, ev, "SkyySu", 1, "Food Pouch", kk == 1, "tab1", @SUBW@);
{{SUBF}}
{{AUTO}}
  b.set("#SkyySuAuto.Text", "Auto-fill: " + (ok && d.auto(kk) ? "ON" : "OFF"));
  ev.addEventBinding(@BTY@.Activating, "#SkyySuAuto", @EVD@.of("a", "auto"));
{{MAIN}}
  for (int i = 0; i < shown; i++) {
    String src = (String) rows.get(i);
    String ric = src;
    String rnm = @PKG@.SupDefs.name(kk, src);
    String rcol = @PKG@.SupDefs.col(kk, src);
    String rtg = (i == 0 ? "Next  -  x" : "x") + d.get(kk, src);
    String rsb = @PKG@.SupDefs.desc(kk, src) + (d.skipped(src) ? "  -  Auto-fill OFF for this one" : "");
{{CARD}}
    ev.addEventBinding(@BTY@.Activating, "#SkyySuRb" + i, @EVD@.of("a", "sel").append("i", String.valueOf(i)));
  }
  if (shown == 0) {
{{EMPTY}}
    b.set("#SkyySuEm.Text", !ok ? "Your Supplies are still loading - open the page again in a moment." : (kk == 0 ? "No healing potions yet - drink-ready potions you pick up go in here." : "No food yet - cooked food you pick up goes in here."));
  }
  if (selI >= 0) {
    String dic = this.selSrc;
    String dcol = @PKG@.SupDefs.col(kk, dic);
{{DETON}}
    b.set("#SkyySuDNm.Text", @PKG@.SupDefs.name(kk, dic));
    b.set("#SkyySuDCt.Text", "You have " + d.get(kk, dic) + (selI == 0 ? "  -  used next" : ""));
    b.set("#SkyySuDTx.Text", @PKG@.SupDefs.desc(kk, dic) + (@PKG@.SupDefs.isRawSrc(kk, dic) ? " Raw food goes in only while the server's Raw food in the Pouch switch is on." : ""));
    b.set("#SkyySuSk.Text", "Auto-fill this: " + (d.skipped(dic) ? "OFF" : "ON"));
    ev.addEventBinding(@BTY@.Activating, "#SkyySuT1", @EVD@.of("a", "t1"));
    ev.addEventBinding(@BTY@.Activating, "#SkyySuTa", @EVD@.of("a", "ta"));
    ev.addEventBinding(@BTY@.Activating, "#SkyySuSk", @EVD@.of("a", "sk"));
  } else {
{{DETOFF}}
    b.set("#SkyySuDHn.Text", "Right click your " + @PKG@.SupDefs.kindName(kk) + " to " + (kk == 0 ? "drink" : "eat") + " the weakest first. It takes the normal " + (kk == 0 ? "drink" : "eat") + " time; getting hit does not stop it.");
  }
{{FOOT}}
  long cap = (long) @PKG@.SupCfg.cap(kk);
  String st0 = !ok ? "=Loading your Supplies." : (@PKG@.SupDefs.kindName(kk) + ": " + d.tot(kk) + " / " + cap + "  -  " + (!@PKG@.SupCfg.ON ? "switched off on this server (taking out still works)." : (d.auto(kk) ? "Auto-fill ON: " + @PKG@.SupDefs.what(kk) + " in your storage and backpack go in by themselves (never from the hotbar)." : "Auto-fill OFF - use Put all in.")) + (rows.size() > shown ? "  Showing the first " + shown + " of " + rows.size() + " kinds." : ""));
  b.set("#SkyySuSt.Text", this.info.length() > 0 ? textOf(this.info) : st0);
  ev.addEventBinding(@BTY@.Activating, "#SkyySuPut", @EVD@.of("a", "put"));
}"""
SUP_BUILD = jsrc(SUP_BUILD.replace("@HUBJAVA@", "@HUBJAVAX@").replace("@ROWMAX@", str(SUP_ROWMAX)).replace("@SUBW@", str(SUP_SUBW)).replace("@HUBJAVAX@", "{{HUBJAVA}}"))
SPP["HUBJAVA"] = jsrc(SUP_HUBJ)
for _k, _v in SPP.items():
    _tag = "{{%s}}" % _k
    assert SUP_BUILD.count(_tag) == 1, _tag
    SUP_BUILD = SUP_BUILD.replace(_tag, _v)
assert "{{" not in SUP_BUILD and "ItemGridSlot" not in SUP_BUILD, "0.1.11: every block placed, never an ItemGridSlot (HANDOFF 2)"
assert "_" not in "".join(re.findall(r"#(SkyySu\w*)", SUP_BUILD.replace("\\", ""))), "0.1.11: no underscores in element ids (HANDOFF 2)"
assert not [t_ for t_ in re.findall(r'Text: \\?"([^"\\]*)', SUP_BUILD) if SUI.MENU_BACK_RE.match(t_) or SUI.MENU_PAGER_RE.match(t_)], "0.1.11: no back / pager text"
sup_Mr(spg, SUP_BUILD)
sup_M(spg, r"""
public void hubAck() {
  try {
    @REF@ hr = this.playerRef.getReference();
    if (hr == null || !hr.isValid()) return;
    @ST@ hs = hr.getStore();
    if (hs == null) return;
    @PLA@ hp = (@PLA@) hs.getComponent(hr, @PLA@.getComponentType());
    if (hp == null || hp.getPageManager() == null || hp.getPageManager().getCustomPage() != this) return;
    @UCB@ hb = new @UCB@();
    hb.set("#SkyySuTitle.Text", "Storage");
    sendUpdate(hb, false);
  } catch (Throwable t) { }
}""")
# one click = one store op (world thread: page events run there), then the held item is synced and the page rebuilt ONCE
sup_M(spg, r"""
public String act(@PLA@ p, @ST@ st, @REF@ ref, String a, int i) {
  java.util.UUID u = this.playerRef.getUuid();
  if (p == null) return "-Could not find you - try again.";
  if (@PKG@.SupLog.busy(u)) return "=Your profile is still loading - try again in a moment.";
  @PKG@.SupData d = @PKG@.SupStore.get(@PKG@.SupOps.pkey(u));
  if (d == null || d.bad) return "-Your Supplies could not be read - nothing was changed (the server log has the details).";
  if (!d.ready) @PKG@.SupOps.sweep(this.playerRef, p, st, ref);
  if (!d.ready) return "=Still loading - try again in a moment.";
  int k = this.tab;
  @IC@[] cs = @PKG@.SupEng.secs(p.getInventory());
  String r = "";
  if (a.equals("sel")) {
    java.util.ArrayList rows = @PKG@.SupOps.rows(d, k);
    if (i >= 0 && i < rows.size()) this.selSrc = (String) rows.get(i);
    return "";
  } else if (a.equals("auto")) {
    boolean v = !d.auto(k);
    d.setAuto(k, v);
    @PKG@.SupStore.save(d);
    @PKG@.SupStore.append(@PKG@.SupStore.line("S", @PKG@.SupStore.nextSeq(), d.key, k, "auto", v ? 1L : 0L, 0L, @PKG@.SupDefs.kindName(k) + " Auto-fill " + (v ? "ON" : "OFF") + " (undo: press Auto-fill again)"));
    int n = v && @PKG@.SupCfg.ON ? @PKG@.SupOps.fill(this.playerRef, cs, d, k, false) : 0;
    r = "+Auto-fill " + (v ? "ON" : "OFF") + (n > 0 ? " - " + n + " went in." : ".");
  } else if (a.equals("t1") || a.equals("ta")) {
    r = @PKG@.SupOps.take(cs, d, k, this.selSrc, a.equals("t1") ? 1L : d.get(k, this.selSrc));
  } else if (a.equals("sk")) {
    if (this.selSrc.length() == 0) return "-Pick an item first.";
    boolean off = !d.skipped(this.selSrc);
    if (off) d.skip.put(this.selSrc, Boolean.TRUE); else d.skip.remove(this.selSrc);
    d.touch();
    @PKG@.SupStore.save(d);
    @PKG@.SupStore.append(@PKG@.SupStore.line("S", @PKG@.SupStore.nextSeq(), d.key, k, this.selSrc, off ? 0L : 1L, 0L, "Auto-fill this " + (off ? "OFF" : "ON") + " for " + this.selSrc + " (undo: press it again)"));
    r = "+" + @PKG@.SupDefs.name(k, this.selSrc) + (off ? " no longer goes in by itself (you can still use it)." : " goes in by itself again.");
  } else if (a.equals("put")) {
    if (!@PKG@.SupCfg.ON) return "-The " + @PKG@.SupDefs.kindName(k) + " is switched off on this server - nothing goes in.";
    int n = @PKG@.SupOps.fill(this.playerRef, cs, d, k, true);
    r = n > 0 ? "+Put " + n + " in." : (d.tot(k) >= (long) @PKG@.SupCfg.cap(k) ? "-Your " + @PKG@.SupDefs.kindName(k) + " is full." : "=Nothing in your storage or backpack can go in (the hotbar is never touched).");
  } else return "";
  @PKG@.SupOps.syncNow(st, ref, u, cs, d);
  return r;
}""")
sup_M(spg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String hr = null;
  try { hr = @PKG@.HubBar.route(this.playerRef, data, "storage", "supplies"); } catch (Throwable th) { hr = null; }
  if (hr != null) {
    if (hr.equals("close")) { close(); return; }
    if (hr.equals("self")) { this.info = ""; rebuild(); return; }
    if (hr.equals("back") || hr.equals("bridge") || hr.equals("command")) { hubAck(); return; }
    this.info = "-That tab could not open right now - try again.";
    rebuild();
    return;
  }
  String a = jsonStr(data, "a");
  if (a.equals("close")) { close(); return; }
  if (a.equals("tab0") || a.equals("tab1")) {
    int t = a.equals("tab0") ? 0 : 1;
    if (t != this.tab) { this.tab = t; this.selSrc = ""; }
    LAST.put(this.playerRef.getUuid(), Integer.valueOf(t));
    this.info = "";
    rebuild();
    return;
  }
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  try { this.info = act(p, st, ref, a, toInt(jsonStr(data, "i"))); }
  catch (Throwable t) { this.info = "-Something went wrong - nothing more was changed."; @PKG@.SupLog.warn("Supplies page click " + a + " failed: " + t); }
  rebuild();
}""")
# OpenCustomUI "SkyySupplies" (crouch + right click on the item): the tab of the item in the hand
spf = smk("SupPageFactory", None, "java.util.function.Function")
SUP_CLASSES.append(spf)
sup_C(spf, "public SupPageFactory() { }")
sup_M(spf, r"""
public Object apply(Object o) {
  @PR@ pr = (@PR@) o;
  int k = -1;
  try {
    @REF@ r = pr.getReference();
    @PLA@ p = (@PLA@) r.getStore().getComponent(r, @PLA@.getComponentType());
    @IS@ h = p.getInventory().getItemInHand();
    if (h != null && !h.isEmpty()) k = @PKG@.SupDefs.kindOf(h.getItemId());
  } catch (Throwable t) { k = -1; }
  if (k < 0) { Object l = @PKG@.SupPage.LAST.get(pr.getUuid()); k = l instanceof Integer ? ((Integer) l).intValue() : 0; }
  return new @PKG@.SupPage(pr, k);
}""")
sho = smk("SupHubOpen", None, "java.util.function.Function")
SUP_CLASSES.append(sho)
sup_C(sho, "public SupHubOpen() { }")
sup_M(sho, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  try {
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) o);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.getPageManager() == null) return Boolean.FALSE;
    Object l = @PKG@.SupPage.LAST.get(pr.getUuid());
    p.getPageManager().openCustomPage(r, st, new @PKG@.SupPage(pr, l instanceof Integer ? ((Integer) l).intValue() : 0));
    return Boolean.TRUE;
  } catch (Throwable t) { @PKG@.SupLog.warn("the Storage > Supplies tab could not open its page: " + t); return Boolean.FALSE; }
}""")
# ---------------------------------------------------------------- SupOpen: start / stop, the bridge, the two commands' body
sopn = smk("SupOpen")
SUP_CLASSES.append(sopn)
sup_F(sopn, "public static volatile Object CLAIMS = null;")
sup_F(sopn, "public static volatile Object COUNTS = null;")
sup_F(sopn, "public static volatile java.util.concurrent.ScheduledFuture TIMER = null;")
sup_M(sopn, r"""
public static void start(java.nio.file.Path dir, @LOG@ log) {
  @PKG@.SupLog.LOG = log;
  String c = @PKG@.SupCfg.load(dir);
  @PKG@.SupStore.DIR = dir.resolve("supplies");
  int open = @PKG@.SupStore.readJournal();
  try { TIMER = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SupSettle(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.SupLog.warn("the journal settle timer did not start (entries settle at the next start instead): " + t); }
  @PKG@.SupLog.info("Potion Flask (" + @PKG@.SupDefs.FSRC.length + " healing potions) + Food Pouch (" + @PKG@.SupDefs.PSRC.length + " foods) - " + c + "; " + open + " journal entries of the last run to recover; /flask /pouch; Storage > Supplies");
}""")
sup_M(sopn, r"""
public static void publish() {
  java.util.Map b = @PKG@.SupLog.bridge();
  CLAIMS = new @PKG@.SupClaimsFn();
  COUNTS = new @PKG@.SupCountsFn();
  b.put("supply:fn:claims", CLAIMS);
  b.put("supply:fn:counts", COUNTS);
  Object[] e = @PKG@.HubBar.put("storage", "supplies", "SkyyCooking", "@HUBLABEL@", @HUBORDER@, "@HUBCMD@", new @PKG@.SupHubOpen(), null);
  if (e == null) @PKG@.SupLog.warn("the Storage > Supplies hub tab could not be put");
}""".replace("@HUBLABEL@", _SHROW[0][4]).replace("@HUBORDER@", str(_SHROW[0][2])).replace("@HUBCMD@", _SHROW[0][5]))
sup_M(sopn, r"""
public static void stop() {
  try { if (TIMER != null) TIMER.cancel(false); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.SupLog.bridge();
    if (CLAIMS != null) b.remove("supply:fn:claims", CLAIMS);
    if (COUNTS != null) b.remove("supply:fn:counts", COUNTS);
  } catch (Throwable t) { }
  try { @PKG@.HubBar.removeAll(); } catch (Throwable t) { }
  java.util.Iterator it = @PKG@.SupStore.DATA.values().iterator();
  while (it.hasNext()) { @PKG@.SupData d = (@PKG@.SupData) it.next(); if (d.isDirty()) @PKG@.SupStore.save(d); }
}""")
# /flask and /pouch: give one back when you hold none (the lifelong recall, storage first), else open the page on that tab
sup_M(sopn, r"""
public static void cmd(@PR@ pr, @ST@ st, @REF@ ref, int k) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { @PKG@.SupLog.tell(pr, "[Cooking] player not found", @PKG@.SupLog.ERR); return; }
    String rr = k == 0 ? @PKG@.FlaskOnce.recall(pr, @PKG@.FlaskOnce.secs(p.getInventory())) : @PKG@.PouchOnce.recall(pr, @PKG@.PouchOnce.secs(p.getInventory()));
    if ("=have".equals(rr)) {
      p.getPageManager().openCustomPage(ref, st, new @PKG@.SupPage(pr, k));
      return;
    }
    String t = k == 0 ? @PKG@.FlaskOnce.recallText(rr) : @PKG@.PouchOnce.recallText(rr);
    if (t != null) @PKG@.SupLog.tell(pr, t, "+given".equals(rr) ? @PKG@.SupLog.OK : @PKG@.SupLog.INFO);
    if ("+given".equals(rr)) @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0);
  } catch (Throwable t) { @PKG@.SupLog.warn(@PKG@.SupDefs.cmd(k) + " failed: " + t); @PKG@.SupLog.tell(pr, "[Cooking] something went wrong - see the server log", @PKG@.SupLog.ERR); }
}""")
for _cn, _w, _k, _d in (("SupFlaskCmd", "flask", 0, "Your Potion Flask: gives it back when you have none, else opens it (Storage > Supplies)"),
                        ("SupPouchCmd", "pouch", 1, "Your Food Pouch: gives it back when you have none, else opens it (Storage > Supplies)")):
    _c = smk(_cn, APC)
    SUP_CLASSES.append(_c)
    sup_C(_c, r"""
public %s() {
  super("%s", "%s");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""" % (_cn, _w, _d))
    sup_M(_c, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.SupOpen.cmd(pr, store, ref, %d);
}""" % _k)

for _c in SUP_CLASSES:
    _c.writeFile(OUT)
print("0.1.11 supplies classes written: %d (+ HubBar, %d lifelong classes)" % (len(SUP_CLASSES), len(LIFE_F["classes"]) + len(LIFE_P["classes"])))
'''
assert SUP_JAVA.startswith("# ================= 0.1.11 SUPPLIES JAVA") and "'''" not in SUP_JAVA
P.rep('''# ================= plugin =================
Ct(pl, ''', SUP_JAVA + '''# ================= plugin =================
Ct(pl, ''')

# ---------- the plugin: setup / shutdown lines + the class list
P.rep('''  getCommandRegistry().registerCommand(new @PKG@.CookAdminCmd());
''', '''  getCommandRegistry().registerCommand(new @PKG@.CookAdminCmd());
  // 0.1.11 SUPPLIES (round FP1): config, store + journal, the four systems (one registerSystem per class), the page, /flask /pouch, bridge, hub tab
  try {
    @PKG@.SupOpen.start(getDataDirectory().resolveSibling("Skyy_SkyyCooking"), getLogger());
    getEntityStoreRegistry().registerSystem(new @PKG@.SupStartSys());
    getEntityStoreRegistry().registerSystem(new @PKG@.SupTick());
    getEntityStoreRegistry().registerSystem(new @PKG@.SupInvSys());
    getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.SupReady());
    @OCU@.registerSimple(this, @PKG@.SkyyCookingPlugin.class, "SkyySupplies", new @PKG@.SupPageFactory());
    getCommandRegistry().registerCommand(new @PKG@.SupFlaskCmd());
    getCommandRegistry().registerCommand(new @PKG@.SupPouchCmd());
    @PKG@.SupOpen.publish();
  } catch (Throwable tSup) { @PKG@.CookCfg.warn("Supplies (Potion Flask + Food Pouch) setup failed: " + tSup); }
""" + SUP_LIFE_SETUP + """''')
P.rep('''  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  super.shutdown();''', '''  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.SupOpen.stop(); } catch (Throwable t) { }   // 0.1.11: bridge keys (only while ours), hub tab, settle timer
""" + SUP_LIFE_SHUTDOWN + """  super.shutdown();''')
P.rep('''jar = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
B.assemble(''', '''# 0.1.11: the Sky Window kit art (the Supplies hub page; HUBS-CONTRACT 2.7) - all 59 files, under Common/UI/Custom/SkyyKit/ only
_kit = SUI.kit_texture_files()
assert len(_kit) == len(SUI.SKY_FILES) == 59 and all(p_.startswith("Common/UI/Custom/SkyyKit/") and p_ not in files for p_ in _kit), "0.1.11: the kit art"
files.update(_kit)
jar = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
B.assemble(''')
assert P.s.count("registerSystem(") == SYS0 + 3 and P.s.count("registerCommand(") == CMD0 + 2, "0.1.11: 3 systems + 2 commands added"
P.finish()
