"""Derive SkyyGear/build_skyygear_0.3.3.py from the LIVE 0.3.2 (build_skyygear_0.3.2.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_2_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_3_3_patch.py      then      python SkyyGear/build_skyygear_0.3.3.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.3.py

0.3.3 = NO HARVESTING TWO TIERS ABOVE YOUR HOE / SICKLE (lean round). Skyy's words (docs/answered/gear.md 2026-10-14, word for word):
  "No. Cant break 2 tiers above"
Built on the LIVE 0.3.2 (the 0.3.2 lost-tool code is untouched).
1. THE RULE (GearLL.decideI): a crop (category 4) two or more tiers above the held hoe / sickle answers 2 = REFUSED (0.3.1: 1 = slow / half
   XP up to two up, refused only at three up). One tier above stays 1 (no Fortune; SkyySkills 0.4.35 pays farming.tierUpXpFactor = half
   XP through gear:fn:farmTier, which now answers 2 for a two-up crop - the crop no longer breaks, so nothing is paid). Ore and logs keep
   the 0.3.1 ladder (1-2 up slow, 3+ up refused). Crude / Wood still count as tier 1 and a family's top vanilla tier still caps the ask
   (the 0.3.0 FAMMAX rule: a Thorium hoe farms every crop at full XP, an Iron sickle too). gate.on off = nothing gated (unchanged).
   WHO IS REFUSED, in practice: a Crude or Copper hoe on Cauliflower / Turnip (T3) and every crop above (the ask is capped at Thorium = T3).
   An Iron hoe is at most one below (half XP). SICKLES ARE NEVER TWO BELOW: vanilla sickles end at Iron, so the ask is capped at Iron (T2)
   and even a Crude sickle (= T1) is at most one below any crop - asserted at build time below.
2. WHERE IT IS REFUSED (server, VERIFIED bytecode 2026-10-14): breaking a crop with a hoe / sickle = BreakBlockInteraction ->
   BlockHarvestUtils.performBlockDamage -> damageSingleBlock, which fires the cancellable DamageBlockEvent for SOFT blocks too (crops are
   soft: damage 1, then the event at offset 1207); a cancelled event makes the engine call BlockSection.invalidateBlock (re-sends the
   block to the clients) and return before any break / drop / durability loss. The LIVE GearToolHitSys already cancels on GearLL.hit == 2,
   so the new answer refuses the hit there with no new system: no item loss, the crop stays, the tool loses no durability.
   SICKLE AREA SWINGS: the swing's selector runs HarvestCrop on every crop it sweeps (FarmingUtil.harvest -> harvest0 -> giveDrops) and the
   engine fires NO event before the crop changes, so a server-side skip per crop is impossible (only the hidden-marker selector override
   of research/Tool-Levels-Spec.md 13 could do it, client side UNVERIFIED). It is not needed: no sickle is ever two below a crop (item 1);
   the build stops (assert) if a future vanilla ladder ever makes one two below.
   QUESTION FOR SKYY (default: unchanged, the 0.3.0 family-top rule): because vanilla sickles stop at Iron, an Iron sickle counts as
   good enough for every crop and a Crude / Copper sickle is at most "one tier below" any crop - it sweeps Potatoes at half Farming XP while
   a Crude hoe is refused on them. Keep that, or measure sickles against the crop's real tier (then a low sickle could not sweep high
   crops, which needs the client-side selector override of spec 2.3 + an in-game probe first)?
   F-HARVEST WITH THE TOO-LOW HOE / SICKLE IN HAND (fix round 2026-10-14, both critics): REFUSED too. The F-harvest is the block's own
   HarvestCrop root, pushed by UseBlockInteraction.doInteraction only AFTER the cancellable UseBlockEvent$Pre (VERIFIED bytecode, asserted by
   the 0.1.3 build check); the LIVE GearChestOpenSys already listens to that event, so its handler now first asks GearLL.useNo(held, crop):
   a crop two or more tiers above the hoe / sickle in hand (the same decideI answer 2) = the event is cancelled (nothing harvested, the crop
   stays ripe) + the same "Too tough" popup. Creative players are skipped (their left-click never reaches the hit gate either). The same
   pattern is live in SkyyIslands' GuardUse (it cancels UseBlockEvent$Pre for F-harvests on islands).
   EMPTY HAND / ANY OTHER ITEM (F or left-click): UNCHANGED (spec 4.3 "hand harvests are never gated"; SkyySkills pays them in full).
   QUESTION FOR SKYY (default: unchanged): a player turned away with a Crude hoe can still take the crop with an empty hand or a non-farming
   item (sword, seeds ...), at full Farming XP. Gating only other items would not close it (an empty slot still works), so the choice is:
   keep hands / other items free, or refuse two-up crops to anyone not holding a good enough hoe / sickle (no hoe = treated as Crude).
3. TEXTS: a refused crop gets its own popup (the same GearGate.popup toast as the tool gate: player switch gear.blockedPopup, 1.5 s
   throttle): "Too tough for your Copper Hoe" / "This crop needs at least an Iron hoe (Thorium for full Farming XP). Tier yours up on the
   Anvil (/smithing)." Ore / logs keep the 0.3.1 words. The gate.on help, statusText, the manifest sentence and the script header follow.
   No new row, no saved data, no one-time update.
4. FIX ROUND (critics, 2026-10-14): F-harvest with the too-low hoe / sickle refused (item 2; GearLL.cropNo shares the popup, GearLL.useNo
   decides, GearChestOpenSys.handle asks it before its chest work). Rejected: gating other items on crops (an empty hand still bypasses -
   Skyy's question in item 2); gating only ripe crops (Skyy: "Cant break 2 tiers above" - an unripe two-up crop is not broken by that hoe
   either; hands still clear it).
ROLLBACK: 0.3.3 -> 0.3.2 is safe (nothing saved changed; 0.3.2 lets two-up crops break slowly at half XP again).
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.2.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.3.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.2"' in s and "GENERATED by tools/gear_0_3_2_patch.py" in s and "0.3.3" not in s[:400], "not the generated 0.3.2 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.2":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.2" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.2 - build script (javassist via jpype). GENERATED by tools/gear_0_3_2_patch.py from the LIVE 0.3.1 (itself GENERATED by
tools/gear_0_3_1_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.2.py -> SkyyGear/SkyyGear-0.3.2.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.2.py
''', '''"""SkyyGear 0.3.3 - build script (javassist via jpype). GENERATED by tools/gear_0_3_3_patch.py from the LIVE 0.3.2 (itself GENERATED by
tools/gear_0_3_2_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.3.py -> SkyyGear/SkyyGear-0.3.3.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.3.py

0.3.3 = NO HARVESTING TWO TIERS ABOVE YOUR HOE / SICKLE (Skyy 2026-10-14 "No. Cant break 2 tiers above"; notes: tools/gear_0_3_3_patch.py):
a crop two or more tiers above the held hoe / sickle is refused (GearToolHitSys cancels the DamageBlockEvent: the crop stays, no drop, no
durability loss, a "Too tough" popup naming the hoe tier it needs); one tier above stays half Farming XP + no Fortune. Ore / logs keep
1-2 up slow, 3 up refused. Sickles end at Iron, so no sickle is ever two below a crop (build-time assert). Fix round: an F-harvest with
that hoe / sickle in hand is refused too (GearChestOpenSys cancels the UseBlockEvent$Pre); an empty hand / another item stays free.

--- 0.3.2 notes ---
''')
rep('VERSION = "0.3.2"\n', 'VERSION = "0.3.3"\n')

# ================================================================================================================ rows (help text only)
rep('''     "Crude counts as Copper. 1-2 tiers up slow, 3 up refused. Off = every tool breaks every block.", "field:GearCfg.GATE_ON"),''',
    '''     "Crude counts as Copper. 1-2 tiers up slow, 3 up refused; crops 2 up refused. Off = no tier gate.", "field:GearCfg.GATE_ON"),''')

# ================================================================================================================ build-time: sickles
after('''F(gll, "public static final int[] CROP_M = %s;" % jints([_m for _w, _m in LL_CROP]))
''', '''# 0.3.3: a sickle swing harvests through HarvestCrop, which fires no event before the crop changes (FarmingUtil.harvest -> harvest0 ->
# giveDrops) - a too-high crop could not be skipped by the server. Sickles end at Iron (LL_FAMMAX[5]): the ask is capped there, so no sickle
# tier (Crude = 1) is ever two below a crop. If a future vanilla ladder breaks that, stop here (the swing would need the selector override).
for _t33 in range(0, LL_FAMMAX[5] + 1):
    for _w33, _m33 in LL_CROP:
        assert min(_m33, LL_FAMMAX[5]) - max(_t33, 1) <= 1, "0.3.3: a tier-%d sickle is two below %s - sickle swings cannot be refused" % (_t33, _w33)
# the hoes that ARE refused (for the log): the family top caps the ask at Thorium
LL_REFUSED33 = sorted(set("%s>%s" % (_t, _w) for _t in range(0, LL_FAMMAX[4] + 1) for _w, _m in LL_CROP
                          if min(_m, LL_FAMMAX[4]) - max(_t, 1) >= 2))
print("0.3.3 crop gate: two-up crops refused for hoe tiers %s (sickles never: they end at tier %d)"
      % (sorted(set(int(_x.split(">")[0]) for _x in LL_REFUSED33)), LL_FAMMAX[5]))
''')

# ================================================================================================================ GearLL: the decision
rep('''# result -1 = not gated, 0 normal, 1 above your tier (one or two up: slow / no Fortune), 2 refused (three or more up); [5] = tiers above.''',
    '''# result -1 = not gated, 0 normal, 1 above your tier (one or two up: slow / no Fortune), 2 refused (three or more up); [5] = tiers above.
# 0.3.3 (Skyy 2026-10-14 "Cant break 2 tiers above"): a CROP two or more up is refused (only one up = 1: half XP, no Fortune).''')
rep('''  return new int[] { d <= 0 ? 0 : (d <= 2 ? 1 : 2), c, m, t, f, d < 0 ? 0 : d };''',
    '''  int lim = c == 4 ? 1 : 2;          // 0.3.3: crops refuse at two up, ore / logs at three up
  return new int[] { d <= 0 ? 0 : (d <= lim ? 1 : 2), c, m, t, f, d < 0 ? 0 : d };''')
rep('''      } else if (pr != null) {
        int full = fullT(d);
        int need = full - 2;''', '''      } else if (pr != null && d[1] == 4) {
        cropNo(pr, u, icon, tn, d);          // 0.3.3: a crop two or more tiers above the hoe / sickle
      } else if (pr != null) {
        int full = fullT(d);
        int need = full - 2;''')
rep('''# the block hit (GearToolHitSys, world thread): 0 = go on, 1 = one tier up, 3 = two up (the caller multiplies the damage by slowF of it),
# 2 = cancelled (0.3.1: three or more up).''', '''# 0.3.3: the crop refusal popup (the hit gate and the F-harvest gate share it): the lowest tier that harvests the crop is one below its
# (capped) tier
M(gll, r"""
public static void cropNo(@PR@ pr, java.util.UUID u, String icon, String tn, int[] d) {
  int fullC = fullT(d);
  @PKG@.GearGate.popup(pr, u, icon, "Too tough for your " + tn, "This crop needs at least " + an(tname(fullC - 1)) + " " + (d[4] == 5 ? "sickle" : "hoe") + " (" + tname(fullC) + " for full Farming XP). Tier yours up on the Anvil (/smithing).");
}""")
# the block hit (GearToolHitSys, world thread): 0 = go on, 1 = one tier up, 3 = two up (the caller multiplies the damage by slowF of it),
# 2 = cancelled (0.3.1: three or more up; 0.3.3: a crop two or more up - the engine re-sends the block, the crop stays).''')
rep('''# -1 not gated, 0 normal, 1 above your tier (0.3.1: one or two up - half XP, no Fortune), 2 refused (fix round, engine critic 6: plain java.lang types only)''',
    '''# -1 not gated, 0 normal, 1 above your tier (0.3.3: one up only - half XP, no Fortune), 2 refused (0.3.3: two or more up - the crop does not
# break) (fix round, engine critic 6: plain java.lang types only)''')
rep('''", three up refused, bare hands " + (@PKG@.GearCfg.GATE_BARE ? "no logs / ore" : "allowed") + ")" : "OFF (gate.on)");''',
    '''", three up refused, crops two up refused, bare hands " + (@PKG@.GearCfg.GATE_BARE ? "no logs / ore" : "allowed") + ")" : "OFF (gate.on)");''')

# ================================================================================================================ the hit system comment
rep('''    // 0.3.1 THE TIER GATE: three tiers up (or no pickaxe / hatchet on ore / logs) = cancelled: no damage, no drop, no XP; one up = the hit''',
    '''    // 0.3.3: a crop two or more tiers above the hoe / sickle is cancelled here too (crops are soft blocks: the engine fires this event for them,
    // and a cancelled event re-sends the block - VERIFIED bytecode BlockHarvestUtils.damageSingleBlock 2026-10-14)
    // 0.3.1 THE TIER GATE: three tiers up (or no pickaxe / hatchet on ore / logs) = cancelled: no damage, no drop, no XP; one up = the hit''')

# ================================================================================================================ fix round: F-harvest
# GearLL.useNo (after farmTier): an F-harvest (any block use) of a crop two or more tiers above the hoe / sickle IN HAND = refused + the popup.
# Empty hand / any other item = false (hand harvests stay free - Skyy's question). Never throws (a failure lets the use go on).
before('''# NO CRAFTING (Skyy: "you cant make more, you can only upgrade them"): a pickaxe / hatchet / hoe / sickle output''', '''# 0.3.3 fix round: the F-harvest gate (GearChestOpenSys, UseBlockEvent$Pre, world thread): true = cancel the use. Only a hoe / sickle in
# hand two or more tiers below the crop (decideI answer 2 - non-farming items and an empty hand answer -1 on crops); the hit gate's popup.
M(gll, r"""
public static boolean useNo(@PR@ pr, @IS@ s, @TBTY@ bt) {
  try {
    if (s == null || s.isEmpty() || !@PKG@.GearCfg.GATE_ON) return false;
    int[] cm = cat(bt);
    if (cm[0] != 4) return false;
    int[] d = decideC(s, cm[0], cm[1]);
    if (d[0] != 2) return false;
    N[0] = N[0] + 1L;
    if (pr != null) cropNo(pr, pr.getUuid(), s.getItemId(), @PKG@.Gear.itemName(s.getItemId()), d);
    return true;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("lluse", "the F-harvest tier gate failed (the harvest goes on unchanged): " + t); return false; }
}""")
''')
# GearChestOpenSys: the crop check runs first (before the part.chests switch: it belongs to the tool gate, gate.on)
rep('''    @UBPRE@ e = (@UBPRE@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.PART_CHESTS) return;
    @VECI@ tb = e.getTargetBlock();''', '''    @UBPRE@ e = (@UBPRE@) ev;
    if (e.isCancelled()) return;
    // 0.3.3 fix round: an F-harvest with a hoe / sickle two or more tiers below the crop is refused (the engine pushes the block's HarvestCrop
    // root only after this event - VERIFIED bytecode, asserted above); creative is skipped like the hit gate (creative fires no block damage)
    if (@PKG@.GearCfg.GATE_ON && e.getContext() != null) {
      @PLA@ pl0 = (@PLA@) chunk.getComponent(idx, @PLA@.getComponentType());
      if (pl0 == null || pl0.getGameMode() != @GM@.Creative) {
        @PR@ pr0 = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
        if (@PKG@.GearLL.useNo(pr0, e.getContext().getHeldItem(), e.getBlockType())) { e.setCancelled(true); return; }
      }
    }
    if (!@PKG@.GearCfg.PART_CHESTS) return;
    @VECI@ tb = e.getTargetBlock();''')
# the engine members the F gate uses (a game update that moves them stops the build)
after('''assert _ubi.find("InteractionContext.execute") > _ubi.find("UseBlockEvent$Pre.isCancelled"), "UseBlockEvent$Pre no longer runs before the root interaction"
''', '''# 0.3.3 fix round: the F-harvest gate reads the event's context (held item) + block type and cancels it
for _c33, _m33 in (("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent", "getContext"),
                   ("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent", "getBlockType"),
                   (CO["UBPRE"], "setCancelled"), ("com.hypixel.hytale.server.core.entity.InteractionContext", "getHeldItem")):
    B.probe(pool, _c33, _m33)
''')

# ================================================================================================================ the manifest
rep('''a tool tier gate (Crude counts as Copper; one tier up takes 2.5x the hits, two up 10x, three up is refused; no tool no logs or ore)''',
    '''a tool tier gate (Crude counts as Copper; one tier up takes 2.5x the hits, two up 10x, three up is refused; a crop two tiers above your hoe is refused; no tool no logs or ore)''')

# ================================================================================================================ checks on the result
assert s.count("int lim = c == 4 ? 1 : 2;") == 1 and s.count("This crop needs at least ") == 1 and "d <= 2 ? 1 : 2" not in s
assert s.count("GearLL.useNo(") == 1 and s.count("cropNo(pr, ") == 2 and s.find("public static void cropNo(") < s.find("public static int hit(")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.2 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.2 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
