"""Derive SkyySkills/build_skyyskills_0.4.5.py from 0.4.4 (same style as skills_0_4_4_patch.py: rep(old, new) with asserted single anchors,
newline-agnostic; 0.4.4 stays untouched, its line endings are preserved). Edit THIS file, not the generated script.
0.4.5 = CROSSBOWS STAY LOADED, the Archery level-5 reward (research/Crossbow-Loaded-Spec.md, the only spec, incl. its section 7 review
notes; Skyy's ask 2026-09-25). Anchors are found by their literal 0.4.4 text (spec 3.1 lists them; the spec gives no 0.4.4 line numbers):
 - XbowCfg (perk.archery.keepLoaded.* of xp.properties, appended once to an existing file), 5 Server Setup rows (1 part switch + 4 perks).
 - XbowState + Xbow (memory only, world thread): remember the bolts vanilla refunds on a hotbar switch AWAY from a crossbow, put them back
   3 of SkyySkills' ticks after the switch BACK, paid 1:1 with Crude Arrows from the inventory (pay first, set second).
 - XbowSlotSys (new EntityEventSystem on InventorySetActiveSlotEvent, one registerSystem) + the per-tick hook in AcroSys (before its 1 s gate).
 - Level-up chat unlock line, Stats page line, Perks.tick / Perks.switched / Acro.retainOnline hooks, ready line, manifest.
 - Build checks (spec 3.9): API probes, the crossbow template, the SwapFrom root and its refund ladder read from Assets.zip, and every
   Weapon_Crossbow_* item of Assets.zip and of More Crossbow Tiers (Mods folder, read only) on that template with no override.
 - The .items row's check= hook (XbowCfg.checkItems) refuses typos in Server Setup (review of 0.4.5).
Run:  python tools/skills_0_4_5_patch.py   then   python SkyySkills/build_skyyskills_0.4.5.py   (NO --deploy: coordinated deploy)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.4.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.5.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.4"
s = raw.decode("utf8").replace("\r\n", "\n")
REG0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# spec 3.1: every 0.4.4 anchor by its literal text (each exactly once; the two "called, not patched" rows are plain presence checks)
for _a in ('{PKG}.PartyCfg.ensureDefaults(p);', '{PKG}.BridgeCfg.read(p);', 'pr.sendMessage({MSG}.raw("SKILL LEVEL UP  "',
           'public static void switched(java.util.UUID u) {{', 'public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{',
           'public static long epoch(java.util.UUID u)', '{PKG}.BridgeXp.retain(online);', '{PKG}.Brew.tick(u, store, cb, ref, dt);',
           'public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{',
           '("bridge.bonus.enabled", "Skill tree bonuses"',
           '"On: the class damage bonus also applies when hitting players.", "reload;confirm=on"))',
           'getEntityStoreRegistry().registerSystem(new {PKG}.SmeltSys());', 'assert len(_absent) == 21', 'assert len(CFG_ROWS) == 154',
           'public static int slotOfClass(String c) {{'):
    assert s.count(_a) == 1, "spec 3.1 anchor count %d != 1: %s" % (s.count(_a), _a)
# the Brew.tick hook sits BEFORE AcroSys' once-per-second gate (spec 3.6), and Perks.epoch exists before Perks.switched
assert s.index("{PKG}.Brew.tick(u, store, cb, ref, dt);") < s.index("    if (s[14] < 1.0) return;")
assert s.index("public static long epoch(java.util.UUID u)") < s.index("public static void switched(java.util.UUID u) {{")

# ================================================================ header / version
rep('''"""SkyySkills 0.4.4 - build script (derived from 0.4.3 by tools/skills_0_4_4_patch.py - edit the patch, not this file;
0.4.3 was derived from 0.4.2 by tools/skills_0_4_3_patch.py, 0.4.2 from 0.4.1 by tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by
tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2
by tools/skills_0_3_patch.py)
0.4.4 (research/Classes-Berserker-Priest-Spec.md''', '''"""SkyySkills 0.4.5 - build script (derived from 0.4.4 by tools/skills_0_4_5_patch.py - edit the patch, not this file;
0.4.4 was derived from 0.4.3 by tools/skills_0_4_4_patch.py, 0.4.3 from 0.4.2 by tools/skills_0_4_3_patch.py, 0.4.2 from 0.4.1 by
tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1
by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.5: Crossbows stay loaded (research/Crossbow-Loaded-Spec.md) - the ARCHERY LEVEL-5 REWARD (Skyy's ask 2026-09-25: "the crossbow should
  stay loaded when you scroll off it and scroll back"). Everything 0.4.4 does is unchanged; no saved data changes (0.4.4 <-> 0.4.5 both
  ways is safe: nothing is written to players/<pkey>.properties, only 5 perk.archery.keepLoaded.* lines to xp.properties).
  WHAT VANILLA DOES (spec 1, VERIFIED): "loaded" is the player's Ammo stat (0-6, EntityStatMap), never item data. Scrolling AWAY from a
    loaded crossbow runs its SwapFrom ladder: Adventure only, it refunds min(Ammo, 6) Crude Arrows and does NOT spend Ammo. Scrolling ONTO
    any crossbow queues a clear of Ammo that the next EntityStatsSystems$Recalculate pass applies (cap 6, value 0). So you never lose
    arrows, but you always reload.
  WHO (spec 2.2): an Archer (SkillClass.slot = slotOfClass("Archer") and SkillClass.consistent) whose Archery level on the ACTIVE profile is
    at least perk.archery.keepLoaded.level (5; 0 = every Archer), perk.archery.keepLoaded.enabled on, profile:busy not set, and a crossbow
    whose id starts with an entry of perk.archery.keepLoaded.items (Weapon_Crossbow_ = Iron, Ancient Steel + More Crossbow Tiers) that
    SkyyClasses allows (class:fn:allowed). Nothing new is saved: the flag is computed from the profile's own Archery level and cached per
    UUID (Xbow.ON), refreshed every second (Perks.tick), right after a level up (SkillXp.gain4) and after a profile switch
    (Perks.switched). The cache only decides when to remember and arm; it NEVER decides a payout.
  HOW (spec 2.3-2.5): XbowSlotSys (EntityEventSystem on InventorySetActiveSlotEvent, section -1 = hotbar, Player query; the event is
    dispatched synchronously inside setActiveSlot, so Ammo still equals the refund there). Leaving a crossbow slot that was held for at
    least delayTicks: remember k = min(Ammo, cap, 6) and the exact stack (per hotbar slot, 16 slots). Arriving at a slot whose kept stack
    is still there (ItemStack.isEquivalentType = same id + metadata): arm a restore. Xbow.tick (inside AcroSys, EVERY tick, before its
    1 s gate) lands it delayTicks (3, about 0.1 s) of its own ticks later, after vanilla's wipe: active slot + stack re-checked, waits for
    the Ammo cap (gives up after 60 ticks), target = min(kept, cap), need = target - current (a vanilla reload in the gap is never paid
    twice), live eligibility re-checked UNCACHED (Xbow.eligibleNow), then Crude Arrows are taken from hotbar + storage + backpack with
    vanilla's own call (getCombined(HOTBAR_STORAGE_BACKPACK).removeItemStack(stack, true, true), all or nothing) and re-counted, and only
    then Ammo is set to current + paid. Creative: free only when both the leave and the return were in Creative (vanilla loads free there
    and refunds nothing). Every entry is cleared after the attempt, whatever the outcome.
  ANTI-DUPE (spec 2.6): vanilla refund on leave + our payment on return = net zero; pay first, set second (a failure never gives a bolt);
    no item data is ever written (a dropped / traded / stored / sold crossbow carries nothing); rapid scrolling cancels the armed restore
    and keeps the count (never re-read); a leave within delayTicks of arriving is never recorded (Ammo may still be the previous
    crossbow's). PER-TICK EPOCH CHECK (review 7.4): each XbowState keeps the profile:epoch it was built under (Perks.epoch, one bridge
    read); a different live value wipes it on the next slot event or tick, before any payment (the 1 s Perks.switched is not relied on).
    Relog / world change (new Ref), death (DeathComponent) and a false cached flag also wipe; profile:busy only pauses.
  CONFIG (spec 3.2 / 3.3): XbowCfg, the Crossbows-stay-loaded block of xp.properties (a fresh file has it; an existing one without
    perk.archery.keepLoaded.enabled gets it appended ONCE), read by SkillCfg.load (/skills reload and the kit's reload routine). 5 rows,
    159 in total: perk.archery.keepLoaded.enabled (Parts, live,part,danger - asks when switched OFF), .level (Perks, 0-100), .items
    (Perks, adv, text up to 500; its check= hook XbowCfg.checkItems refuses an empty list, an entry that is not an id start and one no
    loaded item id starts with, and asks first when an entry also matches ids without "Crossbow" - Weapon_ would count swords), .delayTicks
    (Perks, adv, 3-20), .debug (Perks, adv; admins with skyyskills.admin see one chat line per kept / restored / dropped load).
  TEXTS (spec 3.7): level-up chat "  Unlocked: Crossbows stay loaded when you switch slots" under SKILL LEVEL UP Archery 4 -> 5 (gated by
    the skills.levelUp setting like the level-up lines); Stats page (Archery) "Crossbows stay loaded when you switch slots" under Boosts
    right now from the unlock level, and under "Level 5 adds" one level before; the xp.properties load summary, ready line and manifest.
  BUILD CHECKS (spec 3.9): API probes + exact signatures of every call; Weapon_Arrow_Crude / Weapon_Crossbow_Iron exist; every
    Weapon_Crossbow_* item of Assets.zip AND of More Crossbow Tiers (PACK.md; found in the Mods folder by its manifest Serj:More Crossbow
    Tiers and read in memory, missing or installed twice = the build fails) has Parent Template_Weapon_Crossbow and no Weapon or
    Interactions block of its own, and the pack ships no copy of the template or the SwapFrom files (review of 0.4.5: the pack's 4
    crossbows were not checked before); the template clears Ammo, its Ammo modifier is exactly +6 Additive and its
    SwapFrom root is Root_Weapon_Crossbow_Swap_From = ["Weapon_Crossbow_Swap_From"]; the ladder is walked node by node (Condition
    Adventure -> StatsCondition Ammo 6..1 -> ModifyInventory Weapon_Arrow_Crude x k -> ChangeActiveSlot, no other node type): if Hytale
    changes the crossbow the build fails instead of the perk going quiet.
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r7-skills, deleted afterwards; 83 checks): all 87 classes
    load + initialise under -Xverify:all; XbowCfg.read defaults, custom values, clamps (level -5 -> 0, 500 -> 100, delay 1 -> 3, 99 -> 20,
    bad text -> defaults), the item list (blanks dropped, empty -> Weapon_Crossbow_), isCrossbow; SkillCfg.load: a fresh xp.properties =
    DEFAULTS with one block, a 0.4.4 file gets the block appended once at the end (custom values kept, a second load adds nothing), a hand
    edit is read; the flag against a mock bridge + player file: no class / Warrior / Archer 4 off, Archer 5 on, level 0 = every Archer,
    part off, profile:class mismatch, busy, refresh on / off (off drops the state), the weapon rule with and without class:fn:allowed,
    eligibleNow ignores the cache; fresh (absent epoch, baseline, same, change = wipe + flag off), drop, reset; Xbow.line and the Stats
    page (Archery 5 now / 4 next, right after the class damage line, not at 4 now / 5 next, not on other skills, part off, level 0; the
    Divinity heal line kept); retain / forget; the kit: 159 rows, the 5 rows (category, type, default, bounds, flags, position), get,
    part OFF asks / ON does not, level 101 and delay 2 refused, the file lines change in place and the reload routine applies them.
  UNVERIFIED (needs the game, spec section 4): XbowSlotSys + Xbow.onSlot / Xbow.tick on real hotbar switches (the event, the held-long-
    enough guard, the 3-tick restore after vanilla's wipe, the arrow payment through getCombined inside AcroSys, the client's bolt counter
    and its ~0.1 s gap), the level-up unlock line, the 5 rows in SkyyMenu's Server Setup; go/no-go tests 5, 9, 10 and 12.
  NOT HERE (spec 2.9 / 6): shortbows, the Signature meter, the off-hand slot, keeping loads across teleports (all dropped by default).
0.4.4 (research/Classes-Berserker-Priest-Spec.md''')
rep('''Run:   python build_skyyskills_0.4.4.py            -> SkyySkills/SkyySkills-0.4.4.jar
       python build_skyyskills_0.4.4.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.4.5.py            -> SkyySkills/SkyySkills-0.4.5.jar
       python build_skyyskills_0.4.5.py --deploy   -> also copies''')
rep('VERSION = "0.4.4"', 'VERSION = "0.4.5"')

# ================================================================ API probes (spec 1.8 / 3.9)
before('''# ================= default xp.properties (generated here, every id checked against Assets.zip) =================
''', r'''# 0.4.5 crossbows stay loaded (research/Crossbow-Loaded-Spec.md 1.8 / 3.9; tools/dev reflect.py + bcfull.py against HytaleServer.jar
# 2026-09-25): the hotbar switch event, the Ammo stat, the hotbar and the arrow payment (vanilla ModifyInventoryInteraction's call)
ISAS = "com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent"
HOTB = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar"
STOR = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage"
BKPK = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack"
ASIC = "com.hypixel.hytale.server.core.inventory.ActiveSlotInventoryComponent"
ICON = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
for c, m in ((ISAS, "getInventorySectionId"), (ISAS, "getPreviousSlot"), (ISAS, "getNewSlot"), (ESM, "get"), (ESM, "setStatValue"),
             (ESV, "get"), (ESV, "getMax"), (DST, "getAmmo"), (INVC, "getCombined"), (INVC, "HOTBAR_STORAGE_BACKPACK"),
             (INVC, "HOTBAR_SECTION_ID"), (INVC, "DEFAULT_HOTBAR_CAPACITY"), (HOTB, "getComponentType"), (STOR, "getComponentType"),
             (BKPK, "getComponentType"), (ASIC, "getActiveSlot"), (HOTB, "getActiveSlot"), (HOTB, "getInventory"),
             (ICON, "removeItemStack"), (ICON, "getItemStack"), (ICON, "getCapacity"), (CIC, "getCapacity"), (CIC, "getItemStack"),
             (IS, "isEquivalentType"), (IS, "getItemId"), (IS, "getQuantity"), (IS, "isEmpty"), (IST, "succeeded"),
             (DTH, "getComponentType"), (PLA, "getGameMode"), (GM, "Creative"), (PR, "hasPermission"), (ACH, "getReferenceTo"),
             (ITM, "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetMap")):
    B.probe(pool, c, m)
# exact signatures (a renamed or re-typed parameter fails here, not in game)
for c, m, d in ((ISAS, "getInventorySectionId", "()I"), (ISAS, "getPreviousSlot", "()I"), (ISAS, "getNewSlot", "()B"),
                (ESM, "get", "(I)L" + ESV.replace(".", "/") + ";"), (ESM, "setStatValue", "(IF)F"), (ESV, "get", "()F"), (ESV, "getMax", "()F"),
                (DST, "getAmmo", "()I"), (ASIC, "getActiveSlot", "()B"),
                (INVC, "getCombined", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";[Lcom/hypixel/hytale/component/ComponentType;)L" + CIC.replace(".", "/") + ";"),
                (ICON, "removeItemStack", "(L" + IS.replace(".", "/") + ";ZZ)L" + IST.replace(".", "/") + ";"),
                (ICON, "getItemStack", "(S)L" + IS.replace(".", "/") + ";"), (ICON, "getCapacity", "()S"),
                (IS, "isEquivalentType", "(L" + IS.replace(".", "/") + ";)Z"),
                (ITM, "getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/DefaultAssetMap;"),
                ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetMap", "()Ljava/util/Map;")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
# the event's hotbar section id is -1 (spec 1.5) and the hotbar fits the 16 kept-load slots (spec 2.3)
_hsid = pool.get(INVC).getField("HOTBAR_SECTION_ID").getConstantValue()
_hcap = pool.get(INVC).getField("DEFAULT_HOTBAR_CAPACITY").getConstantValue()
assert _hsid is not None and int(_hsid) == -1, "InventoryComponent.HOTBAR_SECTION_ID is %r, not -1" % (_hsid,)
assert _hcap is not None and 1 <= int(_hcap) <= 16, "InventoryComponent.DEFAULT_HOTBAR_CAPACITY is %r (Xbow keeps 16 slots)" % (_hcap,)
''')

# ================================================================ default xp.properties: the Crossbows stay loaded block (XbowCfg)
after('''DIV_DEFAULTS = "\\n".join(DIV_L) + "\\n"
assert all(ord(ch) < 128 for ch in DIV_DEFAULTS) and '"' not in DIV_DEFAULTS
DIV_LIT = json.dumps(DIV_DEFAULTS)
''', r'''# 0.4.5: Crossbows stay loaded, the Archery level-5 reward (research/Crossbow-Loaded-Spec.md 3.2). Appended once to a file without
# perk.archery.keepLoaded.enabled (XbowCfg.ensureDefaults).
XBOW_L = []
XBOW_L.append("# ---------- Crossbows stay loaded (SkyySkills 0.4.5) - the Archery level-5 reward, research/Crossbow-Loaded-Spec.md ----------")
XBOW_L.append("# Comments must stay on their own lines.")
XBOW_L.append("# An Archer whose Archery level is at least 'level' keeps a crossbow's loaded bolts when switching hotbar slots and back.")
XBOW_L.append("# Vanilla gives the bolts back as Crude Arrows when you switch away; switching back loads them again, paid with those arrows.")
XBOW_L.append("perk.archery.keepLoaded.enabled=true")
XBOW_L.append("perk.archery.keepLoaded.level=5")
XBOW_L.append("# item id starts that count as crossbows, comma separated")
XBOW_L.append("perk.archery.keepLoaded.items=Weapon_Crossbow_")
XBOW_L.append("# server ticks after switching back before the bolts return (3-20; 3 = about 0.1 s)")
XBOW_L.append("perk.archery.keepLoaded.delayTicks=3")
XBOW_L.append("# debug=true: players with skyyskills.admin see a chat line for every kept / restored load")
XBOW_L.append("perk.archery.keepLoaded.debug=false")
L.append("")
L.extend(XBOW_L)
XBOW_DEFAULTS = "\n".join(XBOW_L) + "\n"
assert all(ord(ch) < 128 for ch in XBOW_DEFAULTS) and '"' not in XBOW_DEFAULTS
XBOW_LIT = json.dumps(XBOW_DEFAULTS)
# 0.4.5 build checks (spec 3.9): the crossbow facts the stay-loaded perk rests on, read in memory from Assets.zip. The cap of 6, the 1:1
# Crude refund and "the ladder checks Ammo but never spends it" are what the anti-dupe argument (spec 2.6) needs; any change fails here.
must("Weapon_Arrow_Crude")
must("Weapon_Crossbow_Iron")
XBOW_TYPES = ("Condition", "StatsCondition", "ModifyInventory", "ChangeActiveSlot")
def _xbow_types(o, out):
    if isinstance(o, dict):
        if "Type" in o: out.append(o["Type"])
        for _v in o.values(): _xbow_types(_v, out)
    elif isinstance(o, list):
        for _v in o: _xbow_types(_v, out)
    return out
# every crossbow the perk covers must unload exactly like the template checked below: Parent = Template_Weapon_Crossbow and no Weapon
# block (the Ammo cap / clear) and no Interactions block (the SwapFrom root) of its own (spec 1.7: true for all 6 crossbows today)
def _xbow_item(where, n, d):
    assert isinstance(d, dict) and d.get("Parent") == "Template_Weapon_Crossbow", \
        "%s %s: Parent %r, not Template_Weapon_Crossbow (it may unload differently)" % (where, n, d.get("Parent") if isinstance(d, dict) else d)
    _ov = [k for k in ("Weapon", "Interactions") if k in d]
    assert not _ov, "%s %s: its own %s block overrides Template_Weapon_Crossbow (the Ammo cap / clear or the SwapFrom refund may differ)" % (where, n, "/".join(_ov))
# the files the checks below read; a pack that ships its own copy would replace them
XBOW_CORE = ("Template_Weapon_Crossbow.json", "Root_Weapon_Crossbow_Swap_From.json", "Weapon_Crossbow_Swap_From.json")
with zipfile.ZipFile(ASSETS) as _xz:
    _xn = _xz.namelist()
    def _xone(pre, base):
        _hits = [n for n in _xn if n.startswith(pre) and n.endswith("/" + base)]
        assert len(_hits) == 1, "Assets.zip: %d x %s under %s" % (len(_hits), base, pre)
        return json.loads(_xz.read(_hits[0]).decode("utf-8-sig"))
    _xitems = [n for n in _xn if n.startswith("Server/Item/Items/") and n.endswith(".json") and os.path.basename(n).startswith("Weapon_Crossbow_")]
    assert _xitems, "no Weapon_Crossbow_* item in Assets.zip"
    for _n in _xitems:
        _xbow_item("Assets.zip", _n, json.loads(_xz.read(_n).decode("utf-8-sig")))
    _xt = _xone("Server/Item/Items/", "Template_Weapon_Crossbow.json")
    _xw = _xt.get("Weapon") or {}
    assert "Ammo" in (_xw.get("EntityStatsToClear") or []), "Template_Weapon_Crossbow no longer clears Ammo on a switch"
    assert (_xw.get("StatModifiers") or {}).get("Ammo") == [{"Amount": 6, "CalculationType": "Additive"}], "crossbow Ammo cap is not +6 Additive"
    assert (_xt.get("Interactions") or {}).get("SwapFrom") == "Root_Weapon_Crossbow_Swap_From", "crossbow SwapFrom root changed"
    _xr = _xone("Server/Item/RootInteractions/", "Root_Weapon_Crossbow_Swap_From.json")
    assert _xr.get("Interactions") == ["Weapon_Crossbow_Swap_From"], "Root_Weapon_Crossbow_Swap_From.Interactions changed: %r" % (_xr.get("Interactions"),)
    _xl = _xone("Server/Item/Interactions/", "Weapon_Crossbow_Swap_From.json")
assert set(_xl.keys()) == {"Type", "RequiredGameMode", "Failed", "Next"}, "SwapFrom ladder root keys changed: %r" % (sorted(_xl.keys()),)
assert _xl["Type"] == "Condition" and _xl["RequiredGameMode"] == "Adventure" and _xl["Failed"] == {"Type": "ChangeActiveSlot"}, "SwapFrom ladder root changed"
_xnode = _xl["Next"]
for _k in (6, 5, 4, 3, 2, 1):
    assert isinstance(_xnode, dict) and set(_xnode.keys()) == {"Type", "Costs", "Next", "Failed"}, "SwapFrom ladder step %d changed: %r" % (_k, _xnode)
    assert _xnode["Type"] == "StatsCondition" and _xnode["Costs"] == {"Ammo": _k}, "SwapFrom ladder step %d is not StatsCondition Ammo %d" % (_k, _k)
    assert _xnode["Next"] == {"Type": "ModifyInventory", "ItemToAdd": {"Id": "Weapon_Arrow_Crude", "Quantity": _k}, "Next": {"Type": "ChangeActiveSlot"}}, \
        "SwapFrom ladder step %d no longer refunds exactly %d Crude Arrows: %r" % (_k, _k, _xnode["Next"])
    _xnode = _xnode["Failed"]
assert _xnode == {"Type": "ChangeActiveSlot"}, "SwapFrom ladder end changed: %r" % (_xnode,)
_xtypes = _xbow_types(_xl, [])
assert "ChangeStat" not in _xtypes and all(t in XBOW_TYPES for t in _xtypes), "SwapFrom ladder has a node type the design does not know: %r" % (sorted(set(_xtypes)),)
assert _xtypes.count("StatsCondition") == 6 and _xtypes.count("ModifyInventory") == 6
# More Crossbow Tiers (PACK.md, Serj): the perk covers its crossbows through the same Weapon_Crossbow_ prefix, so they get the same item
# rule, read in memory from the Mods folder (never written). The pack is found by its manifest (Group + Name), not its file name; the
# "Endgame&QoL expansion - Crossbow Tiers" pack (not in PACK.md, it overrides Weapon) is never read. Missing or twice = the build fails:
# PACK.md ships it and the Server Setup help names it, so dropping it means updating XBOW_PACK and that help text on purpose.
XBOW_PACK = ("Serj", "More Crossbow Tiers")
def _xpack_find():
    _out = []
    _fs = sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []
    for _f in _fs:
        _p = os.path.join(B.MODS_DIR, _f)
        try:
            if os.path.isdir(_p):
                with open(os.path.join(_p, "manifest.json"), "rb") as _mf:
                    _man = json.loads(_mf.read().decode("utf-8-sig"))
            elif _f.lower().endswith((".zip", ".jar")):
                with zipfile.ZipFile(_p) as _mz:
                    _man = json.loads(_mz.read("manifest.json").decode("utf-8-sig"))
            else:
                continue
        except Exception:
            continue
        if isinstance(_man, dict) and (_man.get("Group"), _man.get("Name")) == XBOW_PACK:
            _out.append((_p, str(_man.get("Version"))))
    return _out
_xpk = _xpack_find()
assert len(_xpk) == 1, ("%s:%s must be in %s exactly once, found %d %r: PACK.md ships it and the stay-loaded perk covers its crossbows "
                        "(install it, or change XBOW_PACK and the perk.archery.keepLoaded.items help)" % (XBOW_PACK + (B.MODS_DIR, len(_xpk), [os.path.basename(_x[0]) for _x in _xpk])))
_xpp, _xpv = _xpk[0]
def _xpack_items(p):
    if os.path.isdir(p):
        _names = [os.path.relpath(os.path.join(_r, _f), p).replace(os.sep, "/") for _r, _ds, _fl in os.walk(p) for _f in _fl]
        def _read(n):
            with open(os.path.join(p, *n.split("/")), "rb") as _fh:
                return _fh.read()
        _its = [n for n in _names if n.startswith("Server/Item/Items/") and n.endswith(".json") and os.path.basename(n).startswith("Weapon_Crossbow_")]
        return _names, [(n, json.loads(_read(n).decode("utf-8-sig"))) for n in _its]
    with zipfile.ZipFile(p) as _pz:
        _names = _pz.namelist()
        _its = [n for n in _names if n.startswith("Server/Item/Items/") and n.endswith(".json") and os.path.basename(n).startswith("Weapon_Crossbow_")]
        return _names, [(n, json.loads(_pz.read(n).decode("utf-8-sig"))) for n in _its]
_xpn, _xpitems = _xpack_items(_xpp)
assert _xpitems, "%s %s has no Server/Item/Items/**/Weapon_Crossbow_*.json any more (check the pack, PACK.md and the Server Setup help)" % (os.path.basename(_xpp), _xpv)
for _n, _d in _xpitems:
    _xbow_item("More Crossbow Tiers " + _xpv, _n, _d)
_xpcore = [n for n in _xpn if os.path.basename(n) in XBOW_CORE]
assert not _xpcore, "More Crossbow Tiers %s ships %r: it would replace the crossbow template / SwapFrom ladder checked from Assets.zip" % (_xpv, _xpcore)
print("crossbows stay loaded: %d crossbow item(s) on Template_Weapon_Crossbow with no Weapon / Interactions override (%d Assets.zip: %s; %d More Crossbow Tiers %s: %s), "
      "SwapFrom ladder = 6 x (StatsCondition Ammo k -> +k Weapon_Arrow_Crude), Ammo cap +6" % (
          len(_xitems) + len(_xpitems), len(_xitems), ", ".join(sorted(os.path.basename(n)[16:-5] for n in _xitems)),
          len(_xpitems), _xpv, ", ".join(sorted(os.path.basename(n)[16:-5] for n, _d in _xpitems))))
''')

# ================================================================ classes
after('''hfn  = pool.makeClass(PKG + ".SkillHealFn")
''', '''# 0.4.5: crossbows stay loaded (research/Crossbow-Loaded-Spec.md 3.2-3.5): config, per-player state, logic, the hotbar switch event system
xcf  = pool.makeClass(PKG + ".XbowCfg")
xst  = pool.makeClass(PKG + ".XbowState")
xbw  = pool.makeClass(PKG + ".Xbow")
xss  = pool.makeClass(PKG + ".XbowSlotSys", pool.get(EES))
''')

# ================================================================ XbowCfg + XbowState (after DivCfg: SkillCfg.load, compiled later, calls XbowCfg)
before('''# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
''', r'''# ================= XbowCfg (0.4.5): perk.archery.keepLoaded.* of xp.properties - crossbows stay loaded (Crossbow-Loaded-Spec 3.2) =========
# Read by SkillCfg.load (/skills reload and the kit's reload routine re-read it); appended ONCE to an existing file without
# perk.archery.keepLoaded.enabled (the FellCfg / PartyCfg pattern; the code defaults are the same values). Clamps = the Server Setup rows.
xcf.addField(CtField.make("public static final String DEFAULTS = " + XBOW_LIT + ";", xcf))
for decl in ("boolean ON = true", "int LEVEL = 5", 'String[] ITEMS = new String[] { "Weapon_Crossbow_" }', "int DELAY = 3", "boolean DEBUG = false"):
    xcf.addField(CtField.make("public static volatile " + decl + ";", xcf))
xcf.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ON = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.enabled", true);
  long lv = {PKG}.SkillCfg.lng(p, "perk.archery.keepLoaded.level", 5L);
  LEVEL = (int) (lv < 0L ? 0L : (lv > 100L ? 100L : lv));
  java.util.ArrayList l = new java.util.ArrayList();
  String raw = p.getProperty("perk.archery.keepLoaded.items", "Weapon_Crossbow_");
  String[] ps = raw == null ? new String[0] : raw.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() > 0) l.add(t);
  }}
  String[] it = new String[l.size()];
  for (int i = 0; i < it.length; i++) it[i] = (String) l.get(i);
  if (it.length == 0) it = new String[] {{ "Weapon_Crossbow_" }};
  ITEMS = it;
  long d = {PKG}.SkillCfg.lng(p, "perk.archery.keepLoaded.delayTicks", 3L);
  DELAY = (int) (d < 3L ? 3L : (d > 20L ? 20L : d));
  DEBUG = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.debug", false);
}}""", xcf))
xcf.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("perk.archery.keepLoaded.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Crossbows stay loaded section (perk.archery.keepLoaded.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Crossbows stay loaded section to xp.properties: " + t); }}
}}""", xcf))
# id starts with one of ITEMS (default Weapon_Crossbow_: Iron, Ancient Steel and the four More Crossbow Tiers crossbows)
xcf.addMethod(CtNewMethod.make("""
public static boolean isCrossbow(String id) {
  if (id == null || id.length() == 0) return false;
  String[] a = ITEMS;
  for (int i = 0; i < a.length; i++) if (a[i] != null && a[i].length() > 0 && id.startsWith(a[i])) return true;
  return false;
}""", xcf))
# check= hook of the perk.archery.keepLoaded.items row (CONFIG-CONTRACT check=, kit runs it before saving an in-game edit, no kit lock
# held): refuses an empty list, an entry that is not an id start (no * : or spaces) and an entry no loaded item id starts with (a typo);
# asks first when an entry also matches ids without "Crossbow" (Weapon_ would count swords and bows). The engine's item map is the one
# the kit's own item check reads; unreadable or empty (bare JVM) = the ids are not checked.
xcf.addMethod(CtNewMethod.make(f"""
public static String checkItems(String key, String v) {{
  if (v == null) return null;
  java.util.Set ids = null;
  try {{
    java.util.Map m = {ITM}.getAssetMap().getAssetMap();
    if (m != null && !m.isEmpty()) ids = m.keySet();
  }} catch (Throwable t) {{ ids = null; }}
  String[] ps = v.split(",");
  int n = 0;
  String wide = null;
  String wideEx = null;
  int wideN = 0;
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    n++;
    if (t.length() > 120) return "An id start is at most 120 characters: " + t.substring(0, 40) + "...";
    for (int k = 0; k < t.length(); k++) {{
      char c = t.charAt(k);
      if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.'))
        return "Write item id starts like Weapon_Crossbow_, separated by commas (no *, : or spaces): " + t;
    }}
    if (ids == null) continue;
    int hit = 0;
    int other = 0;
    String ex = null;
    boolean read = true;
    try {{
      java.util.Iterator it = ids.iterator();
      while (it.hasNext()) {{
        String id = String.valueOf(it.next());
        if (id.startsWith(t)) {{
          hit++;
          if (id.indexOf("Crossbow") < 0) {{ other++; if (ex == null) ex = id; }}
        }}
      }}
    }} catch (Throwable x) {{ read = false; }}
    if (!read) continue;
    if (hit == 0) return "No item id starts with " + t + ".";
    if (other > 0 && wide == null) {{ wide = t; wideN = other; wideEx = ex; }}
  }}
  if (n == 0) return "List at least one item id start, like Weapon_Crossbow_.";
  if (wide != null) {{
    if (wideEx.length() > 40) wideEx = wideEx.substring(0, 40) + "...";
    String w = wide.length() > 40 ? wide.substring(0, 40) + "..." : wide;
    return "?" + w + " also matches " + wideN + " item(s) without Crossbow in the id, like " + wideEx + ". Count them as crossbows?";
  }}
  return null;
}}""", xcf))
xcf.addMethod(CtNewMethod.make("""
public static String text() {
  if (!ON) return "off";
  return "on (Archers from Archery " + LEVEL + ", bolts back after " + DELAY + " ticks" + (DEBUG ? ", DEBUG chat lines on" : "") + ")";
}""", xcf))

# XbowState (spec 2.3): one per online player, world thread only. n / stk / cre = the kept load per hotbar slot (bolts, the stack seen at
# the switch away, Creative then); enterAt = ticks at the last switch onto the current slot (a fresh state = "long ago": no switch was
# seen while the perk was on, so the held item was not just switched onto); pendSlot / pendAt = the armed restore (-1 = none).
xst.addField(CtField.make("public " + REF + " ref;", xst))
xst.addField(CtField.make("public long epoch;", xst))
xst.addField(CtField.make("public long ticks;", xst))
xst.addField(CtField.make("public int[] n;", xst))
xst.addField(CtField.make("public " + IS + "[] stk;", xst))
xst.addField(CtField.make("public boolean[] cre;", xst))
xst.addField(CtField.make("public long enterAt;", xst))
xst.addField(CtField.make("public int pendSlot;", xst))
xst.addField(CtField.make("public long pendAt;", xst))
xst.addConstructor(CtNewConstructor.make(f"""
public XbowState() {{
  this.ref = null;
  this.epoch = -1L;
  this.ticks = 0L;
  this.n = new int[16];
  this.stk = new {IS}[16];
  this.cre = new boolean[16];
  this.enterAt = -1000000L;
  this.pendSlot = -1;
  this.pendAt = 0L;
}}""", xst))

''')
rep('''    {PKG}.DivCfg.ensureDefaults(p);
''', '''    {PKG}.DivCfg.ensureDefaults(p);
    {PKG}.XbowCfg.ensureDefaults(p);
''')
rep('''    {PKG}.BridgeCfg.read(p);
''', '''    {PKG}.BridgeCfg.read(p);
    {PKG}.XbowCfg.read(p);
''')
rep('''+ ", divinity heal XP " + {PKG}.DivCfg.text() + ", bridge skills " +''',
    '''+ ", divinity heal XP " + {PKG}.DivCfg.text() + ", crossbows stay loaded " + {PKG}.XbowCfg.text() + ", bridge skills " +''')

# ================================================================ Xbow part 1 (before SkillXp: gain4, Perks.tick / switched and Acro.retainOnline call it)
before('''# ================= SkillXp: award + level-up (world thread) =================
''', r'''# ================= Xbow part 1 (0.4.5): crossbows stay loaded - the flag, config helpers, texts (research/Crossbow-Loaded-Spec.md 2.2 / 3.4) ==
# S: UUID -> XbowState (memory only). ON: UUID -> Boolean, the CACHED perk flag (spec 2.2 rules 1-3) - it only decides when to remember and
# arm, never a payout (Xbow.eligibleNow is computed live right before arrows are taken). Both pruned to online players by Acro.retainOnline.
xbw.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap S = new java.util.concurrent.ConcurrentHashMap();", xbw))
xbw.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ON = new java.util.concurrent.ConcurrentHashMap();", xbw))
xbw.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FAILED = new java.util.concurrent.ConcurrentHashMap();", xbw))
xbw.addField(CtField.make('public static final String ARROW = "Weapon_Arrow_Crude";', xbw))
xbw.addField(CtField.make('public static final String TEXT = "Crossbows stay loaded when you switch slots";', xbw))
xbw.addField(CtField.make('public static final String UNLOCK = "Unlocked: Crossbows stay loaded when you switch slots";', xbw))
# one server-log warning per failing method (the AcroSys FAILED_ONCE rule)
xbw.addMethod(CtNewMethod.make(f"""
public static void failed(String what, Throwable t) {{
  if (FAILED.putIfAbsent(what, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("crossbows stay loaded: " + what + " failed (logged once): " + t);
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static {PKG}.XbowState state(java.util.UUID u) {{
  {PKG}.XbowState s = ({PKG}.XbowState) S.get(u);
  if (s != null) return s;
  {PKG}.XbowState n = new {PKG}.XbowState();
  Object o = S.putIfAbsent(u, n);
  return o == null ? n : ({PKG}.XbowState) o;
}}""", xbw))
xbw.addMethod(CtNewMethod.make("""
public static void forget(java.util.UUID u) {
  if (u != null) S.remove(u);
}""", xbw))
xbw.addMethod(CtNewMethod.make("""
public static void retain(java.util.Set online) {
  S.keySet().retainAll(online);
  ON.keySet().retainAll(online);
}""", xbw))
# PROFILES-CONTRACT rule 5: no item moves while the live inventory may belong to another profile (an unreadable bridge = busy)
xbw.addMethod(CtNewMethod.make(f"""
public static boolean busy(java.util.UUID u) {{
  try {{
    return Boolean.TRUE.equals({PKG}.SkillStore.bridge().get("profile:busy:" + u.toString()));
  }} catch (Throwable t) {{ return true; }}
}}""", xbw))
# spec 2.2 rules 1-3, uncached: part switch on, class Archer (and SkyyClasses follows the profile), Archery on the ACTIVE profile >= level
xbw.addMethod(CtNewMethod.make(f"""
public static boolean rules(java.util.UUID u) {{
  try {{
    if (u == null || !{PKG}.XbowCfg.ON) return false;
    int a = {PKG}.SkillClass.slotOfClass("Archer");
    if (a < 0 || {PKG}.SkillClass.slot(u) != a) return false;
    if (!{PKG}.SkillClass.consistent(u)) return false;
    return {PKG}.SkillStore.level(u, a) >= {PKG}.XbowCfg.LEVEL;
  }} catch (Throwable t) {{ failed("rules", t); return false; }}
}}""", xbw))
# the cached flag: every second (Perks.tick), after a level up (SkillXp.gain4), after a profile switch (Perks.switched); off = state dropped
xbw.addMethod(CtNewMethod.make("""
public static void refresh(java.util.UUID u) {
  if (u == null) return;
  boolean on = rules(u);
  ON.put(u, on ? Boolean.TRUE : Boolean.FALSE);
  if (!on) forget(u);
}""", xbw))
xbw.addMethod(CtNewMethod.make("""
public static boolean active(java.util.UUID u) {
  return u != null && Boolean.TRUE.equals(ON.get(u)) && !busy(u);
}""", xbw))
# the weapon rule: a crossbow id (perk.archery.keepLoaded.items) that SkyyClasses allows this player (class:fn:allowed, SkillClass.itemOk)
xbw.addMethod(CtNewMethod.make(f"""
public static boolean allowed(java.util.UUID u, String id) {{
  try {{
    if (!{PKG}.XbowCfg.isCrossbow(id)) return false;
    java.util.function.Function f = {PKG}.SkillClass.allowedFn();
    if (f == null) return true;
    return Boolean.TRUE.equals(f.apply(new Object[] {{ u, id }}));
  }} catch (Throwable t) {{ return false; }}
}}""", xbw))
# right before arrows are taken (spec 2.5 step 3): rules 1-4 + the weapon rule, never the cache
xbw.addMethod(CtNewMethod.make("""
public static boolean eligibleNow(java.util.UUID u, String id) {
  return rules(u) && !busy(u) && allowed(u, id);
}""", xbw))
# Stats page (spec 3.7): the Archery "Boosts right now" line from the unlock level, the "Level L adds" line one level before
xbw.addMethod(CtNewMethod.make(f"""
public static String line(java.util.UUID u, int s, int lv, boolean next) {{
  try {{
    if (!{PKG}.XbowCfg.ON || s < 0 || s != {PKG}.SkillClass.slotOfClass("Archer")) return null;
    if (!next && lv >= {PKG}.XbowCfg.LEVEL) return TEXT;
    if (next && lv + 1 == {PKG}.XbowCfg.LEVEL) return TEXT;
  }} catch (Throwable t) {{ failed("stats line", t); }}
  return null;
}}""", xbw))
# wipe every kept load and the armed restore; a later leave must first be held delayTicks again (the Ammo read may be stale right after)
xbw.addMethod(CtNewMethod.make(f"""
public static void reset({PKG}.XbowState s) {{
  for (int i = 0; i < s.n.length; i++) {{ s.n[i] = 0; s.stk[i] = null; s.cre[i] = false; }}
  s.pendSlot = -1;
  s.pendAt = 0L;
  s.enterAt = s.ticks;
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static void drop({PKG}.XbowState s, int slot) {{
  if (slot >= 0 && slot < s.n.length) {{ s.n[slot] = 0; s.stk[slot] = null; s.cre[slot] = false; }}
  s.pendSlot = -1;
}}""", xbw))
# perk.archery.keepLoaded.debug: admins only (the acro.doubleJump.debug rule), at most one line per event
xbw.addMethod(CtNewMethod.make(f"""
public static void dbg({PR} pr, String text) {{
  if (!{PKG}.XbowCfg.DEBUG || pr == null) return;
  try {{
    if (!pr.hasPermission("skyyskills.admin")) return;
    pr.sendMessage({MSG}.raw("[Skills debug] " + text).color("#c8a0ff"));
  }} catch (Throwable t) {{ }}
}}""", xbw))

''')

# ================================================================ SkillXp.gain4: the unlock line + an immediate flag refresh (spec 3.7)
after('''      if (lvOn) pr.sendMessage({MSG}.raw("SKILL LEVEL UP  " + sk + " " + (lv - 1L) + " -> " + lv + reward).color("#ffc800"));
''', '''      if (lvOn && skill == {PKG}.SkillClass.slotOfClass("Archer") && {PKG}.XbowCfg.ON && {PKG}.XbowCfg.LEVEL >= 1 && lv == (long) {PKG}.XbowCfg.LEVEL) pr.sendMessage({MSG}.raw("  " + {PKG}.Xbow.UNLOCK).color("#ffc800"));
''')
before('''    long need = {PKG}.SkillDefs.needFor(r[2]);
''', '''    {PKG}.Xbow.refresh(u);
''')

# ================================================================ Perks.switched / Perks.tick / Acro.retainOnline (spec 3.7)
after('''  {PKG}.SkillCfg.info("profile switch: " + u + " now uses skills of " + {PKG}.SkillStore.pkey(u));
''', '''  {PKG}.Xbow.forget(u);
  {PKG}.Xbow.refresh(u);
''')
after('''    if (repub) {PKG}.SkillStore.publish(u);
''', '''    {PKG}.Xbow.refresh(u);
''')
rep('''    {PKG}.BridgeXp.retain(online);
    {PKG}.HealXp.retain(online);
''', '''    {PKG}.BridgeXp.retain(online);
    {PKG}.HealXp.retain(online);
    {PKG}.Xbow.retain(online);
''')

# ================================================================ Xbow part 2 (after Perks.epoch and Acro.creativeMode, before AcroSys calls Xbow.tick)
before('''# AcroSys: EntityTickingSystem on Player entities''', r'''# ---- 0.4.5 Xbow part 2: crossbows stay loaded - the epoch check, the hotbar switch and the restore (Crossbow-Loaded-Spec 2.4 / 2.5) ----
# spec 2.4 / review 7.4: the profile epoch this state was built under. Absent = no information; the first value is a baseline (the
# Perks.epochChanged rule); a different value wipes the state and turns the cached flag off (Perks.switched -> refresh brings it back
# within 1 s, so no profile file is loaded here). false = wiped now.
xbw.addMethod(CtNewMethod.make(f"""
public static boolean fresh({PKG}.XbowState s, java.util.UUID u) {{
  long e = {PKG}.Perks.epoch(u);
  if (e < 0L) return true;
  if (s.epoch < 0L) {{ s.epoch = e; return true; }}
  if (s.epoch == e) return true;
  reset(s);
  s.epoch = e;
  ON.put(u, Boolean.FALSE);
  return false;
}}""", xbw))
# spec 2.4, from XbowSlotSys (world thread, inside setActiveSlot: the hotbar already shows `neu`, Ammo is still the load vanilla's SwapFrom
# ladder just refunded). A. leaving `prev`, B. arriving at `neu`. No state is created for a player without the perk.
xbw.addMethod(CtNewMethod.make(f"""
public static void onSlot({ST} st, {REF} ref, {PR} pr, java.util.UUID u, int prev, int neu) {{
  try {{
    if (u == null || ref == null) return;
    {PKG}.XbowState s = ({PKG}.XbowState) S.get(u);
    if (s == null) {{
      if (!{PKG}.XbowCfg.ON || !active(u)) return;
      s = state(u);
    }}
    if (s.ref == null) s.ref = ref;
    else if (s.ref != ref) {{ reset(s); s.ref = ref; }}
    fresh(s, u);
    boolean act = {PKG}.XbowCfg.ON && active(u);
    {HOTB} hb = ({HOTB}) st.getComponent(ref, {HOTB}.getComponentType());
    if (hb == null) return;
    {ICON} c = hb.getInventory();
    if (c == null) return;
    int cap = c.getCapacity();
    String msg = null;
    if (prev >= 0 && prev < s.n.length) {{
      if (s.pendSlot != prev) {{
        boolean kept = false;
        {IS} is = prev < cap ? c.getItemStack((short) prev) : null;
        if (act && is != null && !is.isEmpty() && s.ticks - s.enterAt >= (long) {PKG}.XbowCfg.DELAY && allowed(u, is.getItemId())) {{
          {ESM} esm = ({ESM}) st.getComponent(ref, {ESM}.getComponentType());
          {ESV} v = esm == null ? null : esm.get({DST}.getAmmo());
          if (v != null) {{
            int k = (int) Math.floor((double) v.get());
            int mx = (int) Math.floor((double) v.getMax());
            if (k > mx) k = mx;
            if (k > 6) k = 6;
            if (k > 0) {{
              s.n[prev] = k;
              s.stk[prev] = is;
              s.cre[prev] = {PKG}.Acro.creativeMode(st, ref);
              kept = true;
              msg = "kept " + k + " bolts - " + is.getItemId() + ", slot " + (prev + 1);
            }}
          }}
        }}
        if (!kept) {{ s.n[prev] = 0; s.stk[prev] = null; s.cre[prev] = false; }}
      }}
    }}
    s.pendSlot = -1;
    s.enterAt = s.ticks;
    if (neu >= 0 && neu < s.n.length && s.n[neu] > 0) {{
      {IS} ns = neu < cap ? c.getItemStack((short) neu) : null;
      if (act && ns != null && !ns.isEmpty() && s.stk[neu] != null && ns.isEquivalentType(s.stk[neu])) {{
        s.pendSlot = neu;
        s.pendAt = s.ticks;
      }} else {{
        if (msg == null) msg = act ? "load dropped - crossbow left slot " + (neu + 1) : "load dropped - the perk is not active right now";
        s.n[neu] = 0; s.stk[neu] = null; s.cre[neu] = false;
      }}
    }}
    if (msg != null) dbg(pr, msg);
  }} catch (Throwable t) {{ failed("slot switch", t); }}
}}""", xbw))
# spec 2.5, every AcroSys tick (world thread, before its 1 s gate). Nearly every player / tick: no state -> return at once.
xbw.addMethod(CtNewMethod.make(f"""
public static void tick({ST} st, {REF} ref, {PR} pr, java.util.UUID u) {{
  {PKG}.XbowState s = ({PKG}.XbowState) S.get(u);
  if (s == null) return;
  try {{
    s.ticks = s.ticks + 1L;
    if (s.ref != ref) {{ reset(s); s.ref = ref; return; }}
    if (!fresh(s, u)) return;
    if (st.getComponent(ref, {DTH}.getComponentType()) != null) {{ reset(s); return; }}
    if (!{PKG}.XbowCfg.ON || !Boolean.TRUE.equals(ON.get(u))) {{ forget(u); return; }}
    int slot = s.pendSlot;
    if (slot < 0 || slot >= s.n.length) return;
    if (s.ticks - s.pendAt > 60L) {{ drop(s, slot); dbg(pr, "load dropped - the bolt counter did not come back within 60 ticks"); return; }}
    if (busy(u)) return;
    if (s.ticks < s.pendAt + (long) {PKG}.XbowCfg.DELAY) return;
    {HOTB} hb = ({HOTB}) st.getComponent(ref, {HOTB}.getComponentType());
    if (hb == null || hb.getActiveSlot() != slot) {{ drop(s, slot); dbg(pr, "load dropped - crossbow left slot " + (slot + 1)); return; }}
    {ICON} c = hb.getInventory();
    {IS} is = (c == null || slot >= c.getCapacity()) ? null : c.getItemStack((short) slot);
    if (is == null || is.isEmpty() || s.stk[slot] == null || !is.isEquivalentType(s.stk[slot])) {{ drop(s, slot); dbg(pr, "load dropped - crossbow left slot " + (slot + 1)); return; }}
    {ESM} esm = ({ESM}) st.getComponent(ref, {ESM}.getComponentType());
    int ai = {DST}.getAmmo();
    {ESV} v = esm == null ? null : esm.get(ai);
    if (v == null || v.getMax() < 1.0f) return;
    int mx = (int) Math.floor((double) v.getMax());
    int want = s.n[slot];
    int target = want < mx ? want : mx;
    int cur = (int) Math.floor((double) v.get());
    if (cur < 0) cur = 0;
    int need = target - cur;
    if (need <= 0) {{ drop(s, slot); dbg(pr, "nothing to put back - " + cur + " bolts already loaded"); return; }}
    String id = is.getItemId();
    if (!eligibleNow(u, id)) {{
      drop(s, slot);
      ON.put(u, rules(u) ? Boolean.TRUE : Boolean.FALSE);
      dbg(pr, "load dropped - not allowed right now (class, Archery level or weapon)");
      return;
    }}
    boolean free = s.cre[slot] && {PKG}.Acro.creativeMode(st, ref);
    int pay = 0;
    int have = 0;
    if (free) {{
      pay = need;
    }} else {{
      {CIC} comb = {INVC}.getCombined(st, ref, {INVC}.HOTBAR_STORAGE_BACKPACK);
      if (comb != null) {{
        int cc = comb.getCapacity();
        for (int i = 0; i < cc; i++) {{
          {IS} a = comb.getItemStack((short) i);
          if (a != null && !a.isEmpty() && ARROW.equals(a.getItemId())) have = have + a.getQuantity();
        }}
        pay = need < have ? need : have;
        if (pay > 0) {{
          {IST} tx = comb.removeItemStack(new {IS}(ARROW, pay), true, true);
          if (tx == null || !tx.succeeded()) {{
            pay = 0;
          }} else {{
            int left = 0;
            for (int i = 0; i < cc; i++) {{
              {IS} a = comb.getItemStack((short) i);
              if (a != null && !a.isEmpty() && ARROW.equals(a.getItemId())) left = left + a.getQuantity();
            }}
            int took = have - left;
            if (took < pay) pay = took < 0 ? 0 : took;
          }}
        }}
      }}
    }}
    drop(s, slot);
    if (pay > 0) esm.setStatValue(ai, (float) (cur + pay));
    if (free) dbg(pr, "put back " + pay + " bolts (creative, free)");
    else if (pay >= need) dbg(pr, "put back " + pay + " bolts, paid " + pay + " Crude Arrows");
    else dbg(pr, "put back " + pay + " of " + need + " bolts - only " + pay + " Crude Arrows");
  }} catch (Throwable t) {{
    s.pendSlot = -1;
    failed("restore", t);
  }}
}}""", xbw))

''')

# ================================================================ AcroSys: every tick, before the 1 s gate (spec 3.6)
after('''    {PKG}.Brew.tick(u, store, cb, ref, dt);
''', '''    {PKG}.Xbow.tick(store, ref, pr, u);
''')

# ================================================================ XbowSlotSys (spec 3.5, the SmeltSys pattern)
before('''# ================= trees bridge Functions (0.4, Skill-Trees-Spec 9.3 / 10): skill:fn:xp, skill:fn:drops, skill:fn:placed =================
''', r'''# ================= XbowSlotSys (0.4.5): InventorySetActiveSlotEvent on the player (Crossbow-Loaded-Spec 1.5 / 3.5, the SmeltSys pattern) =====
# Fired synchronously by ActiveSlotInventoryComponent.setActiveSlot (after the slot changed; never for a no-op switch). Hotbar only (-1).
xss.addConstructor(CtNewConstructor.make(f"public XbowSlotSys() {{ super({ISAS}.class); }}", xss))
xss.addField(CtField.make("public static boolean FAILED_ONCE = false;", xss))
xss.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", xss))
xss.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {ISAS} e = ({ISAS}) ev;
    if (e.getInventorySectionId() != {INVC}.HOTBAR_SECTION_ID) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {PKG}.Xbow.onSlot(st, r, pr, pr.getUuid(), e.getPreviousSlot(), (int) e.getNewSlot());
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("crossbow hotbar hook failed (logged once): " + t); }}
  }}
}}""", xss))

''')

# ================================================================ Stats page: the Archery line right after the class damage line (spec 3.7)
before('''  if (s == {PKG}.SkillDefs.DIVINITY && !next) out.add({PKG}.DivCfg.statsLine());
''', '''  String xl = {PKG}.Xbow.line(u, s, lv, next);
  if (xl != null) out.add(xl);
''')

# ================================================================ Server Setup rows (spec 3.3)
after('''    ("bridge.bonus.enabled", "Skill tree bonuses", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: SkyyTrees Wisdom (more XP) and Fortune (double drops) nodes are ignored.", "reload"),
''', '''    ("perk.archery.keepLoaded.enabled", "Crossbows stay loaded", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: a crossbow unloads when you switch slots, as in vanilla (its bolts come back as arrows).", "reload"),
''')
after('''        CFG_ROWS.append(("perk.combat.damageVsPlayers", "Class damage bonus vs players", "perks", "bool", "false", "", "", "", "",
                         "live,danger", "On: the class damage bonus also applies when hitting players.", "reload;confirm=on"))
''', '''        # 0.4.5 crossbows stay loaded (research/Crossbow-Loaded-Spec.md 3.3), the Archery level-5 reward
        CFG_ROWS.append(("perk.archery.keepLoaded.level", "Crossbows stay loaded from Archery", "perks", "int", "5", "0", "100", "", "", "live",
                         "Archery level that unlocks it (5 = the level-5 reward, 0 = every Archer).", "reload"))
        CFG_ROWS.append(("perk.archery.keepLoaded.items", "Crossbow ids (stay loaded)", "perks", "text", "Weapon_Crossbow_", "", "500", "", "",
                         "live,adv", "Item id starts that count as crossbows, comma separated. More Crossbow Tiers is included.",
                         "reload;check=XbowCfg.checkItems"))
        CFG_ROWS.append(("perk.archery.keepLoaded.delayTicks", "Stay-loaded restore delay", "perks", "int", "3", "3", "20", "", "", "live,adv",
                         "Server ticks after switching back before the bolts return (3 = about 0.1 s).", "reload"))
        CFG_ROWS.append(("perk.archery.keepLoaded.debug", "Stay-loaded debug lines", "perks", "bool", "false", "", "", "", "", "live,adv",
                         "On: admins see a chat line each time a crossbow load is kept or put back (for testing).", "reload"))
''')
rep('''assert len(CFG_ROWS) == 154, "0.4.3 had 151 rows + 3 Divinity rows (spec 7.1), got %d" % len(CFG_ROWS)   # 0.4.4
''', '''assert len(CFG_ROWS) == 159, "0.4.4 had 154 rows + 5 crossbows-stay-loaded rows (Crossbow-Loaded-Spec 3.9), got %d" % len(CFG_ROWS)   # 0.4.5
for _k in ("perk.archery.keepLoaded.enabled", "perk.archery.keepLoaded.level", "perk.archery.keepLoaded.items",
           "perk.archery.keepLoaded.delayTicks", "perk.archery.keepLoaded.debug"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\\n" + _k + "=") in ("\\n" + XBOW_DEFAULTS), _k
''')

# ================================================================ plugin: register the event system, ready line, class list, manifest
after('''  getEntityStoreRegistry().registerSystem(new {PKG}.SmeltSys());
''', '''  getEntityStoreRegistry().registerSystem(new {PKG}.XbowSlotSys());
''')
rep('''+ "; divinity heal XP " + {PKG}.DivCfg.text() + "; bridge skill:fn:addxp''',
    '''+ "; divinity heal XP " + {PKG}.DivCfg.text() + "; crossbows stay loaded at Archery " + {PKG}.XbowCfg.LEVEL + " (" + ({PKG}.XbowCfg.ON ? "on" : "off") + ")" + "; bridge skill:fn:addxp''')
rep('''fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn):
    c.writeFile(OUT)''', '''fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn, xcf, xst, xbw, xss):
    c.writeFile(OUT)''')
rep('''Alchemy makes potion effects last longer and adds max Mana; Exploration adds max Stamina.''',
    '''Alchemy makes potion effects last longer and adds max Mana; Exploration adds max Stamina; crossbows stay loaded from Archery 5 by default (the level is set in Server Setup; Archers keep their bolts across hotbar switches, paid with the arrows vanilla refunds).''')

# ================================================================ post-conditions
assert s.count('VERSION = "0.4.5"') == 1 and "0.4.4 - build script" not in s and "SkyySkills 0.4.5 - build script" in s
# one new ECS system (engine rule: one registerSystem per class), registered once, before the config publication
assert s.count("registerSystem(") == REG0 + 1 and s.count("registerSystem(new {PKG}.XbowSlotSys())") == 1
# the config block: one default block, loaded + read once, appended after the Divinity block (file order = DEFAULTS order)
assert s.count("L.extend(XBOW_L)") == 1 and s.count("{PKG}.XbowCfg.ensureDefaults(p);") == 1 and s.count("{PKG}.XbowCfg.read(p);") == 1
assert s.index("{PKG}.PartyCfg.ensureDefaults(p);") < s.index("{PKG}.DivCfg.ensureDefaults(p);") < s.index("{PKG}.XbowCfg.ensureDefaults(p);") < s.index("{PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);")
assert s.index("{PKG}.BridgeCfg.read(p);") < s.index("{PKG}.XbowCfg.read(p);")
assert s.index("L.extend(DIV_L)") < s.index("L.extend(XBOW_L)") < s.index('DEFAULTS = "\\n".join(L) + "\\n"')
# javassist: methods (and the classes they use) before their callers
_i = s.index
assert _i("public static void ensureDefaults(java.util.Properties p) {{\n  if (p.getProperty(\"perk.archery.keepLoaded.enabled\")") < _i("public static synchronized String load() {{")
assert _i('xcf.addMethod(CtNewMethod.make("""\npublic static String text() {') < _i("public static synchronized String load() {{")
assert _i("public XbowState() {{") < _i("public static {PKG}.XbowState state(java.util.UUID u) {{")
assert _i("public static int slotOfClass(String c) {{") < _i("public static boolean rules(java.util.UUID u) {{")
assert _i("public static int level(java.util.UUID u, int skill) {{") < _i("public static boolean rules(java.util.UUID u) {{")
assert _i("public static java.util.function.Function allowedFn() {{") < _i("public static boolean allowed(java.util.UUID u, String id) {{")
assert _i("public static void refresh(java.util.UUID u) {") < _i("public static void gain4({PR} pr, int skill, long amount, boolean note, boolean bonus, String party) {{")
assert _i("public static void refresh(java.util.UUID u) {") < _i("public static void switched(java.util.UUID u) {{")
assert _i("public static void refresh(java.util.UUID u) {") < _i("public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{")
assert _i("public static void retain(java.util.Set online) {\n  S.keySet()") < _i("{PKG}.Xbow.retain(online);")
assert _i("public static long epoch(java.util.UUID u)") < _i("public static boolean fresh({PKG}.XbowState s, java.util.UUID u) {{")
assert _i("public static boolean creativeMode({ST} st, {REF} r) {{") < _i("public static void onSlot({ST} st, {REF} ref, {PR} pr, java.util.UUID u, int prev, int neu) {{")
assert _i("public static boolean fresh(") < _i("public static void onSlot(") < _i("public static void tick({ST} st, {REF} ref, {PR} pr, java.util.UUID u) {{")
assert _i("public static void tick({ST} st, {REF} ref, {PR} pr, java.util.UUID u) {{") < _i("{PKG}.Xbow.tick(store, ref, pr, u);")
assert _i("public static void onSlot(") < _i("{PKG}.Xbow.onSlot(st, r, pr, pr.getUuid()")
assert _i("public static String line(java.util.UUID u, int s, int lv, boolean next) {{") < _i("String xl = {PKG}.Xbow.line(u, s, lv, next);")
assert _i("public static boolean eligibleNow(java.util.UUID u, String id) {") < _i("if (!eligibleNow(u, id)) {{")
# review of 0.4.5: the .items row's check= hook exists before the kit is emitted; More Crossbow Tiers' crossbows are checked like vanilla's
assert s.count('"reload;check=XbowCfg.checkItems"') == 1 and s.count("public static String checkItems(String key, String v) {{") == 1
assert _i("public static String checkItems(String key, String v) {{") < _i("kit = CFG.emit(")
assert s.count('_xbow_item("Assets.zip", _n,') == 1 and s.count('_xbow_item("More Crossbow Tiers " + _xpv, _n, _d)') == 1
assert _i("def _xbow_item(where, n, d):") < _i('_xbow_item("Assets.zip", _n,') < _i("_xpk = _xpack_find()") < _i("kit = CFG.emit(")
# the hooks sit where the spec puts them
assert _i("{PKG}.Brew.tick(u, store, cb, ref, dt);\n    {PKG}.Xbow.tick(store, ref, pr, u);") < _i("    if (s[14] < 1.0) return;")
assert s.count("{PKG}.Xbow.refresh(u);") == 3 and s.count("{PKG}.Xbow.forget(u);") == 1 and s.count("{PKG}.Xbow.retain(online);") == 1
assert _i('if (lvOn) pr.sendMessage({MSG}.raw("SKILL LEVEL UP  "') < _i("{PKG}.Xbow.UNLOCK") < _i("    {PKG}.Xbow.refresh(u);\n    long need = {PKG}.SkillDefs.needFor(r[2]);")
assert _i("if (dm > 0.0) out.add(") < _i("String xl = {PKG}.Xbow.line(u, s, lv, next);") < _i("if (s == {PKG}.SkillDefs.DIVINITY && !next) out.add(")
# anti-dupe order in the restore: the live check, then pay, then clear the entry, then set the stat
_t = s[_i("public static void tick({ST} st, {REF} ref, {PR} pr, java.util.UUID u) {{"):]
_t = _t[:_t.index('}}""", xbw))')]
assert _t.index("if (!eligibleNow(u, id))") < _t.index("comb.removeItemStack(new {IS}(ARROW, pay), true, true)") < _t.index("    drop(s, slot);\n    if (pay > 0) esm.setStatValue(ai, (float) (cur + pay));")
assert _t.count("setStatValue(") == 1 and _t.count("removeItemStack(") == 1
assert "xcf, xst, xbw, xss):" in s and s.count("xss  = pool.makeClass(PKG + \".XbowSlotSys\", pool.get(EES))") == 1
# config publication stays the LAST statement of setup(); the new system is registered before it
_su = s[s.index("public void setup() {{"):]
_su = _su[:_su.index('}}""", pl))')]
assert _su.rstrip().endswith("{PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());")
assert _su.index("{PKG}.SkillCfg.load();") < _su.index("registerSystem(new {PKG}.XbowSlotSys())") < _su.index("CfgPub.start(")
for ident in re.findall(r"#(Skyy[A-Za-z0-9_]*)", s):
    assert "_" not in ident, "UI id with an underscore: " + ident
assert "--deploy" in s   # the script keeps its optional deploy switch; this workflow never passes it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.4
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
