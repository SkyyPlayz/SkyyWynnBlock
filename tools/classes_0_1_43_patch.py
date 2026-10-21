"""Derive SkyyClasses/build_skyyclasses_0.1.43.py from the GENERATED SkyyClasses 0.1.42 (build_skyyclasses_0.1.42.py = the tools/deploy_set.py
SET pin; the EDITED lineage: Skyy's hand-edited 0.1.6 (commit ab75b6c) -> classes_0_1_7_patch.py -> ... -> classes_0_1_42_patch.py -> 0.1.42).
Never re-run an older patch, never edit a generated script - edit this patch (and tools/classes_0_1_43_upfx.py, the UpFx Java it inserts).
Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.42 (tools/soundpass_gen.Patch). Line endings kept.
Run:  python tools/classes_0_1_43_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.43.py   (never --deploy)
      then  python SkyyClasses/test_skyyclasses_0.1.43.py
Deploys TOGETHER with SkyyTrees 0.4.1 (it sends the f.<code> ranks) and SkyyArmory 0.1.41.
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import trees_v3_data as V3D
import classes_0_1_43_upfx as UX

NOTE = '''0.1.43 (2026-10-20) = SKILL TREES 3 ROUND R3a, the SkyyClasses half: THE CLASS-TREE EFFECTS (research/Skill-Trees-3-Spec.md section 3;
  tools/trees_v3_data.py CLASS_FX = every code + number; the engine: NEW class UpFx, Java in tools/classes_0_1_43_upfx.py). Skyy (2026-10-18):
  "in the skill tree, no free upgrades. (i want borderlands style where you have a few upgrades each row, you have to spend an so many points
  total to unlock each row, and the ability's come free with the row they unlock in (you start with the first ability.) (look into all the
  borderlands games and how they build their classes for ideas on what to put in each classes tree.)" + 2026-10-20 "if you have any doubt,
  do research to get good data to base your default on".
  SkyyTrees 0.4.1 puts "f.<code>=<rank x per rank summed over the tree>" into tree:fn:abil; tree:reads:SkyyClasses lists "Class.fx.<code>"
  for every code this build applies (SkyyTrees sells an fx upgrade only then). UpFx reads the codes (cached per list text) at seven hooks:
  1. CAST TIME (Abil.ctxFor, after the 0.3 nodes): "a.<Ability>.pow / rad / dur / cost / cd / hot / radPct" = the ability's numbers (power x,
     radius +, duration +, cost and cooldown -%); spell power (Mage), every-cooldown (Mage / Priest), Overflow (full Mana), the capstones that
     reshape a cast (Holy Land, Prism Overload, Endless Fury, Fracture, Spider's Den, Thousand Palms, Riftmaw's 60 % echo, Cataclysm's radius,
     Arc Cascade's +2 blocks at full Momentum), Guardian Spirit's reach.
  2. AFTER A CAST (castAt0): Rallying Guard's party ward, Momentum per Rift Cleave (+2 Riftmaw), Comet Tail, Cataclysm's 3 stars, Vanishing
     Act's echo smoke + Phantom Edge window, the SHADOW CLONE (the Assassin's free Executioner row-2 ability: Cloak / Vanishing Act leave 1 +
     Split clones for 3 + Duration s - enemies within 6 blocks lose you, then each bursts 3 blocks: 60 % / 40 % of a hit), Warden's Grip,
     Arc Cascade (cost back + a Momentum nova).
  3. A WEAPON HIT (DamageLock.outHook, Filter): weapon / melee / bow / far-shot / low-Health / elite / behind / per-debuff / Marked / Focus
     Fire / Hundred Fists / Bloodthirst / Phantom Edge / Kunai Mark bonuses (together at most +80 %), Lethal hits (x1.5), Deicide, the clone
     pull, kunai marks + weakening; Hunter's Mark / Barbed Mesh vulnerability and Radiant Beacon for every attacker.
  4. AN ABILITY HIT (Abil.hit -> upOut): the same conditional bonuses for abilities + Critical Mass, Dead Eye, Fracture, Glacial Aegis
     (frozen +20 %), Prism Overload's ramp.
  5. A HIT ON A PLAYER (AbilShieldSys, Filter, first): melee / ranged / magic / standing still / shielded / near a rooted enemy cuts,
     Breached / rooted / poisoned / kunai-weakened / Consecrated attackers, Hold the Line / a Guardian save, Aegis Link, Aegis Eternal (all
     together at most 50 %); a BLOCKED hit (Damage.BLOCKED, set by the engine's WieldingDamageReduction) slows the attacker / heals you;
     Mana Barrier slows its attackers; nobody inside a Holy Land Sanctuary is knocked back. LAST (before Guardian Spirit): Last Ward.
  6. A LANDED HIT (AbilFrostSys, Inspect): per-ability slow / knockback / bleed / heal / chain / bounce / repeat / root chance / stun chance,
     Shooting Star, Pinning Shot's mark + bounce, the net's vulnerability / slow / Spider's Den, Firestorm, Black Lotus, Mirror Strike; weapon
     Echo, Thousand Palms, Cleave, knockback, Momentum chance, combo Stamina, bow slow / knockback / Split / Quickdraw, kunai Chain, Imbue
     slow / heal, Still Water slow, Blood Price; KILLS: Thirst, Fleet Ranger, Feedback, Ambush, Ghost Protocol, Deicide, Slipstream,
     Contagion, Second Wind, the debuff spread, Warlord's Domain.
  7. THE PLAYER TICK (AbilTick, 4 a second): the move source "classes.tree" (movement protocol, flat: Haste / Fleetfoot / Fleet Ranger +
     Cloaked + channelling + timed buffs), the Mana regen source "classes" (Mana Tide, Sanctified Mana), dodge-roll Tripwire snares +
     Slipstream stuns, the clones, Rumble, Aegis Eternal's hold, Crimson Eternal, Untouchable, Prism Overload's drain, the zone buffs.
  Ability code paths that call UpFx (late bodies / new late stubs): ctxFor, castAt0, flowAt (combo cap), flowTick (Flowing Form speed),
  flowEnd (ward), inHit (deflect back), counter (No Mind, slow), cloakEnd (Smoke Veil), shockJob / chainOne / palmRun (extra stun), the
  Enrage leech (Red Mist, Crimson overheal), spinTick (Endless Fury), bannerAt / bannerTick (Warlord's Domain), rootMob (the rooted map),
  wardArea (ward boost), hit (upOut), aim (spell range), beamJob (beam reach), starJob (+stars), starTick (Follow), meteorImpact (knockback),
  healCast (Follow + the extras), zoneEnd / zoneEnd2 (Glacial Aegis, Rebound, Hold the Line, the Sanctuary ward), guard (Vigil, spiritDr).
  No saved data, command, setting or page change. ROLLBACK to 0.1.42 together with SkyyTrees 0.4.0 (0.1.42 ignores the f.<code> entries).
  FIX ROUND 1: Server Setup -> Classes "Class tree effects" (abil.treeFx) + "Class tree numbers" (ab.ClassTree.numbers).
  FIX ROUND 2: "Capstone numbers" (ab.Capstones.numbers, every capstone number) + lethal / focusStacks / chainGap; Endless Fury is a Whirlwind
  toggle again (castAt0 turns it off, spinAt / spinTick start + end it), Spider's Den + Holy Land hold a spare charge (castAt0), Holy Land's
  overlap heals 150 % (sanctPulse -> the late stub upOverlap); Rumble's flag per thread; quit drops a waiting Arc Cascade nova. New config
  rows only (read, never written at start).
'''

P = G.Patch(os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.42.py"), os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.43.py"))
assert P.has('VERSION = "0.1.42"') and P.has("treeRank") and not P.has("UpFx"), "not the generated SkyyClasses 0.1.42 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyyClasses 0.1.42 - build script (javassist via jpype). GENERATED by tools/classes_0_1_42_patch.py from the generated 0.1.41 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_42_patch.py) - edit the patch, not this file.
''', '''"""SkyyClasses 0.1.43 - build script (javassist via jpype). GENERATED by tools/classes_0_1_43_patch.py from the generated 0.1.42 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_43_patch.py) - edit the patch, not this file.
''' + NOTE + '''=== 0.1.42 (history; still true unless 0.1.43 above says otherwise) ===
''')
P.rep('VERSION = "0.1.42"', 'VERSION = "0.1.43"')

# ---------------------------------------------------------------------------------------------------- the codes + the reader list
PRELUDE = '''TREE_READS += ",Class.v3mods"   # 0.1.42 fix round: this SkyyClasses reads the Skill Trees 3 modifier ranks (SkyyTrees 0.4.0 sells them only then)
# 0.1.43 SKILL TREES 3 R3a: the class-tree effect codes this build applies (tools/trees_v3_data.py CLASS_FX, owner SkyyClasses) -> UpFx;
# tree:reads:SkyyClasses lists "Class.fx.<code>" for each (SkyyTrees 0.4.1 sells an fx upgrade only while every code is listed)
import trees_v3_data as V3D
V3D.check()
assert V3D.FX_AP == ("pow", "rad", "dur", "cost", "cd", "stun", "slow", "kb", "dot", "heal", "chain", "bounce", "rep", "mom", "ward", "hot", "radPct",
                     "stars", "rootChance", "stunChance"), "UpFx reads the ability parameters by these positions (ap(v, ai, 0..19))"
_upc, _uper = set(), {}
for _t in V3D.TREES:
    if _t["kind"] != "class":
        continue
    for _b in _t["branches"]:
        for _r in _b["rows"]:
            _f = _r["free"]
            if _f and _f["hook"] and _f["hook"][0] == "fx":
                _upc.add(_f["hook"][1])
                _uper.setdefault(_f["hook"][1], 1.0)
            for _u in _r["ups"]:
                for _c, _v in V3D.fx_codes(_u):
                    if V3D.fx_owner(_c) == "SkyyClasses":
                        _upc.add(_c)
                        _uper.setdefault(_c, float(_v))
UPFX_CODES = sorted(_upc)
UPFX_PER = _uper
_abid = [a[0] for a in ABILS]
assert all(_c.split(".")[1] in _abid for _c in UPFX_CODES if _c.startswith("a.")), "an a.<Ability> code names an unknown ability"
UPFX_AP = [UPFX_CODES.index("a.%%s.%%s" %% (_a, _p)) if "a.%%s.%%s" %% (_a, _p) in UPFX_CODES else -1 for _a in _abid for _p in V3D.FX_AP]
UPFX_STATE = %s
_UXC = re.compile(r"@C_([A-Za-z0-9]+)@")
def ux(src):
    def _r(m):
        assert m.group(1) in UPFX_CODES, "UpFx names a code no class upgrade has: " + m.group(1)
        return str(UPFX_CODES.index(m.group(1)))
    return _UXC.sub(_r, src)
TREE_READS += "," + ",".join("Class.fx." + _c for _c in UPFX_CODES)
assert len(TREE_READS) < 20000
print("0.1.43 class-tree effects: %%d codes (%%d ability parameters), tree:reads:SkyyClasses %%d characters" %% (len(UPFX_CODES), sum(1 for _c in UPFX_CODES if _c.startswith("a.")), len(TREE_READS)))
''' % repr(UX.UPFX_STATE)
P.rep('''TREE_READS += ",Class.v3mods"   # 0.1.42 fix round: this SkyyClasses reads the Skill Trees 3 modifier ranks (SkyyTrees 0.4.0 sells them only then)
''', PRELUDE)

# ---------------------------------------------------------------------------------------------------- FIX ROUND: Server Setup rows
# (critic, PROJECT-RULES 4 "Everything a server owner might change is editable in game"): a master switch + one text row of the UpFx numbers
# that have no number in the spec (the AbilNum "numbers" pattern: one row, every key optional; times in SECONDS)
P.rep('''    ("abil.healCap", "HEAL_CAP", "int", 60, "10", "100", "%", "abil", "live", "Ability heal cap per cast",''',
      '''    ("abil.treeFx", "TREE_FX", "bool", True, "", "", "", "abil", "live", "Class tree effects",
     "Off: class-tree upgrades do nothing in SkyyClasses (points stay spent). Health/Mana/Stamina % stay."),   # 0.1.43
    ("abil.healCap", "HEAL_CAP", "int", 60, "10", "100", "%", "abil", "live", "Ability heal cap per cast",''')
P.rep('''_n("ab.Elements.bothBonus", "EL_BOTHBONUS", "dec", 10.0, "0", "10000", "", "abilsb", "bothBonus", "bothBonus")
''', '''_n("ab.Elements.bothBonus", "EL_BOTHBONUS", "dec", 10.0, "0", "10000", "", "abilsb", "bothBonus", "bothBonus")
# 0.1.43 fix round: the class-tree effect numbers (UpFx; first-pass numbers, the spec gives none) - one text row "ab.ClassTree.numbers"
for _k, _f, _d, _lo, _hi in (("drCap", "UX_DRCAP", 50.0, "0", "90"), ("dmgCap", "UX_DMGCAP", 80.0, "0", "500"),
                             ("slowAbility", "UX_SLOWA", 3.0, "0", "30"), ("slowWeapon", "UX_SLOWW", 2.0, "0", "30"),
                             ("cloneTime", "UX_CLONET", 3.0, "0.5", "30"), ("cloneHit", "UX_CLONEH", 60.0, "0", "500"),
                             ("cloneExtra", "UX_CLONEX", 40.0, "0", "500"), ("cloneLure", "UX_CLONER", 6.0, "0", "32"),
                             ("lastWard", "UX_LASTW", 60.0, "1", "3600"), ("ghost", "UX_GHOST", 8.0, "0", "600"),
                             ("noMind", "UX_NOMIND", 6.0, "0", "600"), ("rumble", "UX_RUMBLE", 5.0, "0.5", "600"),
                             ("aegisHold", "UX_AEGIST", 30.0, "1", "600"), ("aegisRadius", "UX_AEGISR", 6.0, "0", "32"),
                             ("gripRadius", "UX_GRIPR", 8.0, "0", "32"), ("glacial", "UX_GLACIAL", 10.0, "0", "600"),
                             ("miracle", "UX_MIRACLE", 8.0, "0", "600"),
                             # fix round 2: the last fixed class-tree constants
                             ("lethal", "UX_LETHAL", 50.0, "0", "500"), ("focusStacks", "UX_FOCUSN", 5.0, "1", "20"),
                             ("chainGap", "UX_CHAING", 0.5, "0.1", "10")):
    _n("ab.ClassTree." + _k, _f, "dec", _d, _lo, _hi, "", "abilx", _k, _k)
# 0.1.43 FIX ROUND 2 (critic: the capstone numbers were fixed in code): one more text row "ab.Capstones.numbers" (AbilNum.CP_*; % / s / blocks)
for _k, _f, _d, _lo, _hi in (("rumbleStun", "CP_RUMBLES", 1.5, "0", "10"), ("aegisCut", "CP_AEGISC", 10.0, "0", "50"),
                             ("aegisSlow", "CP_AEGISS", 40.0, "0", "100"), ("gripRoot", "CP_GRIPT", 2.0, "0", "10"),
                             ("gripWard", "CP_GRIPW", 10.0, "0", "100"), ("domain", "CP_DOMAIN", 60.0, "0", "100"),
                             ("domainKill", "CP_DOMAINK", 2.0, "0", "30"), ("furyMax", "CP_FURYT", 30.0, "1", "600"),
                             ("furyMana", "CP_FURYM", 2.0, "0", "100"), ("furyStamina", "CP_FURYS", 4.0, "0", "100"),
                             ("furyBack", "CP_FURYB", 5.0, "0", "100"), ("furySlow", "CP_FURYV", 30.0, "0", "70"),
                             ("imageHit", "CP_IMAGEH", 30.0, "0", "500"), ("palmsHit", "CP_PALMSH", 40.0, "0", "500"),
                             ("lotus", "CP_LOTUS", 200.0, "0", "1000"), ("deadEye", "CP_DEADEYE", 50.0, "0", "500"),
                             ("spiderStun", "CP_SPIDERS", 1.5, "0", "10"), ("cataStars", "CP_CATAN", 3.0, "0", "20"),
                             ("prismDrain", "CP_PRISMD", 4.0, "0", "100"), ("prismRamp", "CP_PRISMR", 2.0, "0", "100"),
                             ("prismMax", "CP_PRISMX", 40.0, "0", "500"), ("glacialHit", "CP_GLACIALP", 20.0, "0", "500"),
                             ("miracleBelow", "CP_MIRACLEB", 20.0, "1", "99"), ("vigil", "CP_VIGIL", 30.0, "0", "90"),
                             ("holyOverlap", "CP_HOLYO", 150.0, "100", "300")):
    _n("ab.Capstones." + _k, _f, "dec", _d, _lo, _hi, "", "abilx", _k, _k)
''')
P.rep('''                                  + ['ArcaneBreach', 'ElementalImbue', 'Sunder', 'RiftCleave', 'ShatteringArc', 'Momentum', 'Elements'])   # 0.1.25''',
      '''                                  + ['ArcaneBreach', 'ElementalImbue', 'Sunder', 'RiftCleave', 'ShatteringArc', 'Momentum', 'Elements']   # 0.1.25
                                  + ['ClassTree', 'Capstones'])   # 0.1.43 fix round: the class-tree effect numbers; fix round 2: + the capstones''')
P.rep('''{'Momentum': 'Momentum', 'Elements': 'Element statuses'}[_aid]   # 0.1.25: + Momentum / Element statuses''',
      '''{'Momentum': 'Momentum', 'Elements': 'Element statuses', 'ClassTree': 'Class tree', 'Capstones': 'Capstone'}[_aid]   # 0.1.25: + Momentum / Element statuses; 0.1.43: + Class tree, Capstone''')
P.rep('''if _aid not in NEW2_IDS + NEW3_IDS + ["Momentum", "Elements"] else''', '''if _aid not in NEW2_IDS + NEW3_IDS + ["Momentum", "Elements", "ClassTree", "Capstones"] else''')
P.rep('''        ("key=value: stacks, s, blocks, %, power x one hit; no key = its default" if _aid in ("Momentum", "Elements") else''',
      '''        ("key=value: caps %, times s, radius blocks, clone hit %; no key = its default" if _aid == "ClassTree" else   # 0.1.43
         "key=value: hits / cuts / slows %, times s, Mana + Stamina a second; no key = its default" if _aid == "Capstones" else   # 0.1.43 fix 2
         "key=value: stacks, s, blocks, %, power x one hit; no key = its default" if _aid in ("Momentum", "Elements") else''')
# ---------------------------------------------------------------------------------------------------- the UpFx class (after Abil's methods)
def _mu(java):
    j = java.replace('M(upfx, r"""', 'MU(r"""').replace('M(upfx, "', 'MU("')
    assert "M(upfx" not in j
    return j


UPFX_ALL = ('''def MU(src):
    M(upfx, ux(src))
''' + _mu(UX.UPFX_JAVA) + _mu(UX.UPFX_JAVA2) + _mu(UX.UPFX_JAVA3) + _mu(UX.UPFX_JAVA4) + _mu(UX.UPFX_JAVA5) +
           '''print("UpFx: %d methods" % len(upfx.getDeclaredMethods()))
''')
P.rep('''abtick = pool.makeClass(PKG + ".AbilTick", pool.get(T["ETS"]))''', UPFX_ALL + '''abtick = pool.makeClass(PKG + ".AbilTick", pool.get(T["ETS"]))''')

# ---------------------------------------------------------------------------------------------------- the new late stubs (bodies call UpFx)
LATE = r'''
# 0.1.43 SKILL TREES 3 R3a: the late stubs the regular ability code calls (their bodies call UpFx, set at the end like every late body)
ABIL_LATE += [
r"""
public static double upOut(@CAC@ acc, @REF@ t, java.util.UUID cu, String what) {
  return @PKG@.UpFx.outAbil(acc, t, cu, what, System.currentTimeMillis());
}
""",
r"""
public static int upStars(@PKG@.AbilCtx c) {
  return @PKG@.UpFx.stars(c);
}
""",
r"""
public static double[] upStarAt(@CB@ cb, @REF@ cr, @PKG@.AbilCtx c, double px, double py, double pz) {
  return @PKG@.UpFx.starAt(cb, cr, c, px, py, pz);
}
""",
r"""
public static double upRange() {
  return @PKG@.UpFx.range();
}
""",
r"""
public static @VEC@ upHealAt(@ST@ st, @REF@ ref, java.util.UUID u, @VEC@ c) {
  return @PKG@.UpFx.healAt(st, ref, u, c);
}
""",
r"""
public static void upHealed(@ST@ st, @REF@ ref, java.util.UUID u, java.util.ArrayList us, java.util.ArrayList rs, double[] done, double[] want, @VEC@ c, double rad) {
  @PKG@.UpFx.healed(st, ref, u, us, rs, done, want, c, rad);
}
""",
r"""
public static void upZoneEnd(@PKG@.AbilZone z, @CAC@ acc) {
  @PKG@.UpFx.zoneEnded(z, acc);
}
""",
r"""
public static void upSaved(@CB@ buf, @REF@ r, java.util.UUID u, @PR@ best, @REF@ bestRef, @PKG@.AbilCtx bc, @VEC@ p, long cd, String gk, long now) {
  @PKG@.UpFx.saved(buf, r, u, best, bestRef, bc, p, cd, gk, now);
}
""",
r"""
public static void upImpact(@PKG@.AbilJob j, @CB@ cb, @REF@ cr, int n) {
  @PKG@.UpFx.impact(j, cb, cr, n);
}
""",
r"""
public static double upOverlap(@PKG@.AbilZone z, @ST@ st, @VEC@ q) {
  return @PKG@.UpFx.overlap(z, st, q);
}
""",
]
'''
P.rep('''for _src in ABIL_LATE:
    M(abil, _late_stub(_src))''', LATE + '''for _src in ABIL_LATE:
    M(abil, _late_stub(_src))''')

# ---------------------------------------------------------------------------------------------------- the hooks in the regular ability code
P.rep('''    double amt0 = amount * outMult(buf, t, cu, System.currentTimeMillis());   // 0.1.24: Enrage / Frenzy / banner / Mark ... on ability hits too''',
      '''    double amt0 = amount * outMult(buf, t, cu, System.currentTimeMillis()) * upOut(buf, t, cu, what);   // 0.1.24: Enrage / Frenzy / banner / Mark ... on ability hits too; 0.1.43: + the class tree''')
P.rep('''public static double[] aim(@CAC@ acc, @REF@ r, double range) {
  try {''', '''public static double[] aim(@CAC@ acc, @REF@ r, double range) {
  range = range * upRange();   // 0.1.43: Focusing Lens (Mage) - the cast's context
  try {''')
P.rep('''  double len = @PKG@.AbilCfg.R_RANGE;
  double secs = @PKG@.AbilCfg.R_TIME;''', '''  double len = @PKG@.AbilCfg.R_RANGE * upRange();   // 0.1.43: Focusing Lens
  double secs = @PKG@.AbilCfg.R_TIME;''')
P.rep('''  int n = stars < 1L ? 1 : (int) Math.round((double) stars * dm);
  if (n < 1) n = 1;''', '''  int n = stars < 1L ? 1 : (int) Math.round((double) stars * dm);
  if (n < 1) n = 1;
  n = n + upStars(c);   // 0.1.43: Split (+2 stars a rank)''')
P.rep('''    double pz = cz + (q == 0 ? d[1] : -d[1]);
    particle(FX_STAR, px, cy + 0.5, pz, cb);''', '''    double pz = cz + (q == 0 ? d[1] : -d[1]);
    double[] sf = upStarAt(cb, cr, c, px, cy, pz);   // 0.1.43: Follow - the star lands on the nearest enemy within 4 blocks
    if (sf != null) { px = sf[0]; pz = sf[1]; }
    particle(FX_STAR, px, cy + 0.5, pz, cb);''')
P.rep('''  j.hits = n;
  @PR@ pr = @UNI@.get().getPlayer(j.caster);
  if (pr != null) say(pr, (echo ? "Echo: " : "") + (n == 0 ? "Meteor hit nothing." : ''', '''  j.hits = n;
  upImpact(j, cb, cr, n);   // 0.1.43: Meteor's knockback (class tree)
  @PR@ pr = @UNI@.get().getPlayer(j.caster);
  if (pr != null) say(pr, (echo ? "Echo: " : "") + (n == 0 ? "Meteor hit nothing." : ''')
P.rep('''public static String healCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, @PKG@.AbilWorld aw, long now) {
  @VEC@ c = pos(st, ref);''', '''public static String healCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, @PKG@.AbilWorld aw, long now) {
  @VEC@ c = upHealAt(st, ref, u, pos(st, ref));   // 0.1.43: Follow - the most hurt party member within 20 blocks''')
P.rep('''  say(pr, "Sacred Heal: " + (healed == 0 ? "nobody needed healing" : ''', '''  upHealed(st, ref, u, us, rs, done, want, c, rad);   // 0.1.43: Chain reach, Triage, Overheal, Benediction, Miracle, the Sanctuary chain
  say(pr, "Sacred Heal: " + (healed == 0 ? "nobody needed healing" : ''')
P.rep('''public static void zoneEnd(@PKG@.AbilZone z, @CAC@ acc) {
  z.ended = true;''', '''public static void zoneEnd(@PKG@.AbilZone z, @CAC@ acc) {
  z.ended = true;
  upZoneEnd(z, acc);   // 0.1.43: Glacial Aegis, Rebound, Hold the Line''')
P.rep('''  if (z.kind == 5) {
    particle(FX_END, z.x, z.y + 1.0, z.z, acc);''', '''  if (z.kind == 5) {
    upZoneEnd(z, acc);   // 0.1.43: the Sanctuary ward
    particle(FX_END, z.x, z.y + 1.0, z.z, acc);''')
P.rep('''  @PKG@.AbilStore.GUARD.put(gk, new long[] { (long) cnt, now + cd, now });''', '''  @PKG@.AbilStore.GUARD.put(gk, new long[] { (long) cnt, now + cd, now });
  upSaved(buf, r, u, best, bestRef, bestCx, p, cd, gk, now);   // 0.1.43: Guardian Spirit Duration, Undying Vigil''')

# ---------------------------------------------------------------------------------------------------- the hooks in the late bodies
P.rep('''  treeApply(c);
  if (ai == @PKG@.AbilDefs.PALM) c.cdAdd = c.cdAdd - palmCut(c.lvl);''', '''  treeApply(c);
  @PKG@.UpFx.ctx(c);   // 0.1.43: Skill Trees 3 - the class tree's fx codes (power, radius, duration, cost, cooldown, capstones)
  if (ai == @PKG@.AbilDefs.PALM) c.cdAdd = c.cdAdd - palmCut(c.lvl);''')
P.rep('''  if (failed != null) return failed;
  String lvx = cx.lvl > 1 ? " lv=" + cx.lvl : "";''', '''  if (failed == null) { try { @PKG@.UpFx.cast(pr, st, ref, u, k, ai, sh, cx, at, mana, stam, now); } catch (Throwable ux) { @PKG@.UpFx.warn("an after-cast effect", ux); } }   // 0.1.43
  if (failed != null) return failed;
  String lvx = cx.lvl > 1 ? " lv=" + cx.lvl : "";''')
P.rep('''  int mx = (int) @PKG@.AbilNum.FF_MAX;
  if (c != null && "Monk".equals(c.cls) && c.node("PC5") && mx > 18) mx = 18;''', '''  int mx = (int) @PKG@.AbilNum.FF_MAX + @PKG@.UpFx.comboCap(c);   // 0.1.43: Flurry
  if (c != null && "Monk".equals(c.cls) && c.node("PC5") && mx > 18) mx = 18;''')
P.rep('''  int pct = (int) Math.round((double) stk * per * mul) - (monk && z.cx.node("PB4") ? 5 : 0);
  speedFlow(cb, cr, z.caster, pct, now);''', '''  int pct = (int) Math.round((double) stk * per * mul) - (monk && z.cx.node("PB4") ? 5 : 0);
  speedFlow(cb, cr, z.caster, pct + @PKG@.UpFx.flowMove(z), now);   // 0.1.43: Flowing Form Haste''')
P.rep('''  LAST_MONK = "flow end " + z.why + " combo=" + z.total + " waves=" + z.hits;''', '''  @PKG@.UpFx.flowEnded(z, acc, cr);   // 0.1.43: Still Water Ward
  LAST_MONK = "flow end " + z.why + " combo=" + z.total + " waves=" + z.hits;''')
P.rep('''          DEFLECTS = DEFLECTS + 1L;''', '''          DEFLECTS = DEFLECTS + 1L;
          @PKG@.UpFx.deflect(buf, r, att, (double) a0, u);   // 0.1.43: Ricochet''')
P.rep('''  hit(buf, att, r, u, z.amount, "StillWater");
  COUNTERS = COUNTERS + 1L;''', '''  hit(buf, att, r, u, z.amount, "StillWater");
  COUNTERS = COUNTERS + 1L;
  @PKG@.UpFx.countered(buf, r, u, att, z, now);   // 0.1.43: Still Water Slow, No Mind''')
P.rep('''  LAST_ASN = "cloak end " + z.why;''', '''  @PKG@.UpFx.cloakEnded(z, acc, cr);   // 0.1.43: Smoke Veil, Slipstream's window
  LAST_ASN = "cloak end " + z.why;''')
P.rep('''  if (c != null && c.x1 > 0.0) stun = stun * 2.0;
  j.stun = stun;''', '''  if (c != null && c.x1 > 0.0) stun = stun * 2.0;
  j.stun = @PKG@.UpFx.shockStun(c, stun);   // 0.1.43: Duration (+stun), Rumble''')
P.rep('''  stunMob(cb, x, j.caster, stun, now);
  if (j.sh == 3) rootMob(cb, x, j.caster, stun + @PKG@.AbilNum.IC_ANCHORROOT, now, false, false);''', '''  stunMob(cb, x, j.caster, stun + @PKG@.UpFx.stunAdd(c, @PKG@.AbilDefs.IRONC), now);   // 0.1.43: Duration
  if (j.sh == 3) rootMob(cb, x, j.caster, stun + @PKG@.AbilNum.IC_ANCHORROOT, now, false, false);''')
P.rep('''  stunMob(cb, t, j.caster, stun, now);
  if (monk && c.node("PB3")) effect(cb, t, "Vulnerable", 2.0);''', '''  stunMob(cb, t, j.caster, stun + @PKG@.UpFx.stunAdd(c, @PKG@.AbilDefs.PALM), now);   // 0.1.43: Duration
  if (monk && c.node("PB3")) effect(cb, t, "Vulnerable", 2.0);''')
P.rep('''      if (g[6] > 0.0) { apply(buf, att, amt * g[6] / 100.0, amt * g[6] / 100.0); out = out + " leech"; }''',
      '''      if (g[6] > 0.0) { @PKG@.UpFx.leech(buf, att, u, amt * g[6] / 100.0); out = out + " leech"; }   // 0.1.43: Red Mist, Crimson Eternal''')
P.rep('''  if (dealt > 0.0 && z.pct > 0.0) apply(cb, cr, dealt * z.pct / 100.0, dealt * z.pct / 100.0);''',
      '''  if (dealt > 0.0 && z.pct > 0.0) apply(cb, cr, dealt * z.pct / 100.0, dealt * z.pct / 100.0);
  @PKG@.UpFx.spinPulse(z, cb, cr, n);   // 0.1.43: Endless Fury''')
P.rep('''  z.nextHeal = now;
  z.t3 = now;
  aw.addZone(z);
  @PKG@.AbilStore.BANNERS.put(u, z);''', '''  z.nextHeal = now;
  z.t3 = now;
  @PKG@.UpFx.bannerUp(z, c);   // 0.1.43: Warlord's Domain
  aw.addZone(z);
  @PKG@.AbilStore.BANNERS.put(u, z);''')
P.rep('''  @VEC@ p = ok ? pos(cb, cr) : null;
  boolean inside = p != null && @PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, z.r);''', '''  if (ok && @PKG@.UpFx.domain(z)) zoneFollow(z, cb);   // 0.1.43: Warlord's Domain - the banner follows you
  @VEC@ p = ok ? pos(cb, cr) : null;
  boolean inside = p != null && @PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, z.r);''')
P.rep('''  boolean ok = effect(acc, t, "Root", s);''', '''  boolean ok = effect(acc, t, "Root", s);
  if (ok) @PKG@.UpFx.rooted(t, now + ms(s));   // 0.1.43: the rooted map (Thick Hide, Clinch, Dead Eye)''')
P.rep('''public static int wardArea(@CAC@ acc, java.util.UUID caster, double x, double y, double z, double rad, double pct, long until) {
  int n = 0;''', '''public static int wardArea(@CAC@ acc, java.util.UUID caster, double x, double y, double z, double rad, double pct, long until) {
  pct = @PKG@.UpFx.wardPct(caster, pct);   // 0.1.43: the class tree's ward boost (Warrior Ward, Priest Ward)
  int n = 0;''')

# FIX ROUND 2 (critic: Holy Land / Spider's Den / Endless Fury had become stat tweaks): their spec mechanics
# Spider's Den + Holy Land: a spare charge (a cast while on cooldown spends it; the main cooldown keeps running)
P.rep('''  long left = @PKG@.AbilStore.left(k, id, now);
  if (left > 0L) {
    if (@PKG@.AbilCfg.CD_MSG) refuse(pr, nm + " is " + @PKG@.AbilMath.readyText(left) + ".");''', '''  if (ai == @PKG@.AbilDefs.WHIRL) { String fo = @PKG@.UpFx.furyOff(pr, u, k, now); if (fo != null) return fo; }   // 0.1.43 fix 2: Endless Fury - a cast turns the toggled spin off
  long left = @PKG@.AbilStore.left(k, id, now);
  boolean spare = left > 0L && @PKG@.UpFx.spare(u, ai, csv, now);   // 0.1.43 fix 2: Spider's Den / Holy Land - the second charge
  if (left > 0L && !spare) {
    if (@PKG@.AbilCfg.CD_MSG) refuse(pr, nm + " is " + @PKG@.AbilMath.readyText(left) + ".");''')
P.rep('''  @PKG@.AbilStore.arm(k, id, now, cd);
  if ((ai == @PKG@.AbilDefs.RAPID''', '''  if (@PKG@.UpFx.furyOn(cx)) cd = 0L;   // 0.1.43 fix 2: Endless Fury's cooldown starts when the spin ends (UpFx.furyEnd / furyOff)
  if (spare) { @PKG@.UpFx.spareUse(u, ai, now, cd); cd = left; }   // 0.1.43 fix 2: the spare charge - the main cooldown keeps running
  else @PKG@.AbilStore.arm(k, id, now, cd);
  if ((ai == @PKG@.AbilDefs.RAPID''')
P.rep('''  @PKG@.AbilStore.SPINS.put(u, z);
  if (sh == 3) effect(acc, ref, "Root", secs);''', '''  @PKG@.AbilStore.SPINS.put(u, z);
  @PKG@.UpFx.furyUp(z, c, now);   // 0.1.43 fix 2: Endless Fury - the toggled spin
  if (sh == 3) effect(acc, ref, "Root", secs);''')
P.rep('''    if (@PKG@.AbilStore.SPINS.get(z.caster) == z) @PKG@.AbilStore.SPINS.remove(z.caster);''',
      '''    if (@PKG@.AbilStore.SPINS.get(z.caster) == z) @PKG@.AbilStore.SPINS.remove(z.caster);
    @PKG@.UpFx.furyEnd(z, now);   // 0.1.43 fix 2: Endless Fury - the cooldown starts now''')
# Holy Land: the overlap of two of your Sanctuaries heals 150 % (the younger zone's pulse x (holyOverlap - 100) %)
P.rep('''    double want = @PKG@.HealTask.split(mx * z.pct / 100.0, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    Object dn = z.healed.get(t);''', '''    double want = @PKG@.HealTask.split(mx * z.pct / 100.0, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT) * upOverlap(z, st, pos(cb, r));   // 0.1.43 fix 2: Holy Land
    Object dn = z.healed.get(t);''')

# ---------------------------------------------------------------------------------------------------- the systems + the quit
P.rep('''    if (!@PKG@.AbilWorld.BY.isEmpty()) @PKG@.Abil.shield(st, buf, r, (@DMG@) ev, now);''', '''    if (@PKG@.UpFx.ON) @PKG@.UpFx.inc(st, buf, r, (@DMG@) ev, now);   // 0.1.43: the class tree's damage cuts + block effects (before every shield)
    if (!@PKG@.AbilWorld.BY.isEmpty()) @PKG@.Abil.shield(st, buf, r, (@DMG@) ev, now);''')
P.rep('''    @PKG@.Abil.guard(st, buf, r, (@DMG@) ev, now);   // 0.1.18: Guardian Spirit - LAST (after armour, the sanctuary, the bubble, the barrier)''',
      '''    if (@PKG@.UpFx.ON) @PKG@.UpFx.incLast(st, buf, r, (@DMG@) ev, now);   // 0.1.43: Last Ward (after every shield, before Guardian Spirit)
    @PKG@.Abil.guard(st, buf, r, (@DMG@) ev, now);   // 0.1.18: Guardian Spirit - LAST (after armour, the sanctuary, the bubble, the barrier)''')
P.rep('''    @PKG@.Abil.siphonHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);''', '''    @PKG@.Abil.siphonHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);
    if (@PKG@.UpFx.ON) @PKG@.UpFx.landed(buf, chunk.getReferenceTo(idx), (@DMG@) ev, now0);   // 0.1.43: the class tree's on-hit + kill effects''')
P.rep('''      @PKG@.Abil.track(r0, cb, now0);                                              // 0.1.18: crouch / air since (the shape resolver)''',
      '''      @PKG@.Abil.track(r0, cb, now0);                                              // 0.1.18: crouch / air since (the shape resolver)
      @PKG@.UpFx.tick(r0, cb, now0);                                              // 0.1.43: the class tree (4 a second per player)''')
P.rep('''_oh[0].setBody(jv("{ if ($5 != null && (!@PKG@.AbilStore.STRIKE.isEmpty()''', '''_oh[0].setBody(jv("{ if ($5 != null && @PKG@.UpFx.ON) @PKG@.UpFx.out($1, $2, $3, $4, $5, System.currentTimeMillis()); "   # 0.1.43: the class tree (first: it reads the First Strike / God Killer state)
                  "if ($5 != null && (!@PKG@.AbilStore.STRIKE.isEmpty()''')
P.rep('''    @PKG@.AbilStore.MIRFAIL.remove(u);''', '''    @PKG@.AbilStore.MIRFAIL.remove(u);
    @PKG@.UpFx.quit(u);   // 0.1.43: the class tree's per-player state + its move / Mana regen sources''')

# FIX ROUND (critic: the block effects read Damage.BLOCKED, which the engine's WieldingDamageReduction sets - same Filter group, no declared
# order): AbilShieldSys also runs AFTER WieldingDamageReduction (one more DROPS entry: each resolved class = one AFTER dependency)
P.rep('''            '"com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$PlayerDamageFilterSystem" };')''',
      '''            '"com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$PlayerDamageFilterSystem", '
            '"com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$WieldingDamageReduction" };')   # 0.1.43 fix round: Damage.BLOCKED is set first''')
P.rep('''for _c in ("FilterUnkillable", "FilterPlayerWorldConfig", "PlayerDamageFilterSystem"):   # FIX ROUND: the filters AbilShieldSys also runs after''',
      '''for _c in ("FilterUnkillable", "FilterPlayerWorldConfig", "PlayerDamageFilterSystem", "WieldingDamageReduction"):   # FIX ROUND: the filters AbilShieldSys also runs after (0.1.43: + Wielding)''')
# the probes of the engine members UpFx adds (a game update that renames one stops the build)
P.rep('''abtick = pool.makeClass(PKG + ".AbilTick", pool.get(T["ETS"]))''', '''for _c, _m in ((T["DMG"], "BLOCKED"), ("com.hypixel.hytale.server.core.meta.IMetaStore", "getIfPresentMetaObject"), (T["CB"], "getStore"),
               (T["REF"], "getStore"), (T["CB"], "tryRemoveComponent")):   # 0.1.43 UpFx
    B.probe(pool, _c, _m)
abtick = pool.makeClass(PKG + ".AbilTick", pool.get(T["ETS"]))''')

P.rep('''          abp4, abp4f):                  # 0.1.38: + Meteor from the Rift (the world task + armory:on:blink:SkyyClasses)
    c.writeFile(OUT)''', '''          abp4, abp4f,                   # 0.1.38: + Meteor from the Rift (the world task + armory:on:blink:SkyyClasses)
          upfx):                         # 0.1.43: + UpFx, the class-tree effects
    c.writeFile(OUT)''')
assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
assert P.s.count("@PKG@.UpFx.") >= 25
P.finish()
