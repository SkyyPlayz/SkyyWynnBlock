"""Derive SkyyClasses/build_skyyclasses_0.1.18.py from the CURRENT generated 0.1.17 (build_skyyclasses_0.1.17.py = the tools/deploy_set.py
SET pin). Run:  python tools/classes_0_1_18_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.18.py   then
                python SkyyClasses/test_skyyclasses_0.1.18.py --dir <tools/dev/scratch/...>   (never --deploy: coordinated deploy)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_17_patch.py -> the
generated 0.1.17 read here; tools/classes_0_1_6_patch.py is NEVER re-run. Edit THIS file, never the generated build script.

0.1.18 = THE CLASS ABILITY ENGINE, ROUNDS R5 + R6 + R7 (research/cloud/Ability-Engine-Plan.md section 8; R4 = the real keys waits for
Hytale 0.7's runes). Skyy's words behind it (docs/answered/classes.md + this round's task): "okay, yeah wait till 0.7. Mage starfall and
arcane beam both sound great! so does frost nova spell book move is good for now, might get tweaked later." + "I want to get as much as
we can out of our tokens" + the locks of 0.1.16 / 0.1.17 (4 abilities, 2 primary + 2 crouch alts, 4 shapes each, cost / cooldown per
shape, Mana AND Stamina by the class split, unlock 1 / 10 / 20 / 30, every ability affordable when unlocked). Numbers: plan 4.3 (power x
78 / 22 Mage, 73 / 27 Priest - asserted at build time) and research/cloud/Class-Ability-Shapes.md sections 4 + 5.
WHAT IS NEW
  R5 SHAPES (all built abilities):
  - THE SHAPE RESOLVER (AbilMath.resolveAt / shapeOf, pure, bare-JVM tested), read at the press on the world thread: in the air for at
    least abil.airMin (0.15 s) = the PRIMARY's mid-air shape (crouch in the air belongs to movement); else crouch held (at least
    abil.crouchMin 0.1 s once AbilTick has seen it) = the ALT on that key in its CROUCH shape; else sprinting = the sprinting shape;
    else walking. /cast 3 | 4 = the alts, always their crouch shape. Rows abil.shapes / abil.shapes.sprint / abil.shapes.air (off =
    walking) + player switches classes.abilSprint / classes.abilAir (/settings). AbilTick tracks when crouch went on and when the feet
    left the ground (AbilStore.MOVE, only for players who are crouching / airborne).
  - Shapes (each with its own Mana + Stamina + cooldown rows ab.<Ability>.<sprint|air|crouch>.mana / .stamina / .cooldown):
      Meteor:        Comet (abil.ahead 6 blocks ahead, 3 blocks) / Under Me (lands where you land, no extra delay) / Meteor on Me
                     (on you, 0.5 s, 5 blocks, 2.5 H - you take none: players are never hit)
      Mana Barrier:  Barrier Ahead / Landing Dome / Pocket Dome (on you, 4 blocks, 10 s, 2.5 HP per Mana)
      Sacred Heal:   Running Blessing (a 6-block circle follows you 2 s: each player it touches once, 20 % + the heal over time) /
                     Beacon (where you land, 10 blocks) / Kneel (1 s channel: 20 % more, heal over time doubled; moving more than
                     abil.channelMove 1 block breaks it and gives everything back)
      Shield Bubble: Bubble Ahead / Bubble Below (where you land) / Around Me (on you, 5 blocks, HP 110 %)
    "On landing" shapes wait for the feet to touch the ground (abil.landWait 2 s, then where you are); "ahead" = abil.ahead blocks
    along your look on the flat. Crouch shapes never move you.
  - /classadmin shape <1|2|3|4> <walk|sprint|air|crouch> (admin, as yourself, the full pipeline with that shape forced - typing a command
    cannot sprint or jump; it pays and arms the cooldown like a real cast).
  R6:
  - GUARDIAN SPIRIT (the Priest's A2-alt, PASSIVE, owned at abil.unlock.a2alt 20): a player who would die (the hit is >= their Health
    AFTER armour, the bubble, the barrier - it runs last inside AbilShieldSys) within ab.GuardianSpirit.radius (30) of a Priest who owns it
    (themself or a party member; ab.GuardianSpirit.everyone = anyone) survives at ab.GuardianSpirit.health (30) % of max Health: the hit is
    cancelled, the Priest pays 15 Mana + 1 Stamina (no Mana = no save; creative free; the nearest Priest who can pay). The cooldown
    follows the SAVED player: 12 s, doubling each save (12, 24, 48 ...), reset after ab.GuardianSpirit.resetAfter (30) s without taking
    damage. Out-of-world and command damage are never saved (no void protection - Skyy lines 116-117).
  - FROST NOVA (the Mage's A2-alt, at 20): freeze (vanilla Freeze effect) every enemy within 5 blocks for 2 s + 1.0 H, then Chill
    (vanilla Slow) 3 s; a hit after the first 1 s breaks the freeze (AbilFrostSys, the Inspect group). Shapes Frost Wake (a 2 x 8 strip
    behind you 3 s, freeze 1.5 s), Frost Drop (on landing, 6 blocks; the 1-block push is NOT built), Deep Freeze (4 blocks, 3 s, hits do
    not break it for 2 s).
  - THE STUN-CLOCK BRIDGE (the SkyyClasses side): a freeze on a mob first asks the bridge armory:fn:stunhit (Object[] {the mob's Ref,
    caster UUID, role name, hold ms} -> Long -1 not a boss / 0 its breakout window - do not freeze / >0 freeze at most this long), so
    bosses share the Monk stunlock clock (Skyy 2026-10-08: one shared clock). The SkyyArmory side is NOT in this round: SkyyArmory 0.1.15
    is another builder's round (UT items) - see ARMORY FOLLOW-UP below. Until a SkyyArmory publishes the key, Frost Nova only CHILLS a
    boss (a role holding a word of abil.bossWords = SkyyArmory's stun.bossWords default, whole parts of the name), never freezes it - so
    no ability can stunlock a boss past its breakout; one WARN says so.
  R7:
  - STARFALL (Mage A1-alt A at 30): 12 stars over 3 s on a 6-block area where you look (25 blocks), each 0.3 H in 3 blocks of its fall
    point (sunflower spread, deterministic); Star Trail (the stars fall where you are as you run), Starfall Below (where you land, 7
    blocks, 2 s), Star Shower (on you, 16 stars over 4 s - "you cannot move" is NOT built).
  - ARCANE BEAM (Mage A1-alt B at 30, the CHANNEL kind): a 20-block beam along your look for 3 s, ticking every 0.5 s on the nearest enemy
    on it, 0.5 / 1.0 / 1.5 H per second (ramp 1x -> 3x); Sweep Beam (15 blocks, 2 s, every enemy on it, 1.5x flat, wider), Beam Down
    (straight down, 12 blocks, 2 s - the slow-fall is NOT built), Focused Beam (25 blocks, 4 s, ramp to 3.5x - "cannot move" NOT built).
    It ends early on death, leaving, a profile switch, a weapon swap or your next cast.
  - SANCTUARY (Priest A1-alt A at 30): a 12 s, 8-block holy zone under you: you and your party inside heal 5 % max Health a second
    (others the othersPercent share; the abil.healCap per target) and take 10 % less damage (in AbilShieldSys, before the bubble);
    Pilgrim's Path (5 ahead), landing spot, Inner Sanctum (5 blocks on you, 7 % / s, 15 % less, 10 s).
  - MARTYR'S GRACE (Priest A1-alt B at 30, the CHAIN kind): heals the lowest hurt player within 30 blocks 75 % of max Health, then the next
    lowest 60 / 45 / 30 / 15 % (5 targets, party incl. the Priest first, then others at the othersPercent share; the first heal capped at
    ab.MartyrsGrace.firstCap 90 %, the rest at abil.healCap); Grace in Motion (the player you look at first), Descent (you first),
    Martyr's Vow (1 s channel, 90 % then -20).
  - THE ABILITIES PAGE (/cast page; inline, vanilla look from tools/skyyui.py): your 4 slots as cards - Move a card onto another to swap
    them (that is how you pick your 2 primaries and their key order; both must be unlocked), and the Ability 1 alt card (pick A or B at
    abil.unlock.a1alt, confirmed in the page; the other is locked out). Everything only OUT OF COMBAT (skill:fn:combat).
  - HUD BRIDGE: class:fn:abil -> Object[48]; the first 44 fields keep the 0.1.17 layout (SkyyHud 0.3.18 unchanged); the alt rows' costs are
    their CROUCH-shape costs now; [44] the shape a primary would fire now (walk / sprint / air / crouch), [45] Boolean shapes on, [46]
    "abil3", [47] null.
  - Server Setup -> Classes: new categories Ability shapes / Mage abilities 2 / Priest abilities 2 (labels <= 20 characters); every row's
    key is in the default file. No migration (a missing key reads its default).
NOT IN THIS ROUND (and why): the real Q / E keys (R4, Hytale 0.7 runes); the Frost Drop push, the Beam Down slow-fall and the "cannot move"
  of Star Shower / Focused Beam / Kneel (each needs a velocity / movement-lock probe - UNVERIFIED engine paths, kept out on purpose); the HUD
  swapping rows while crouching (SkyyHud already does it from [32]); Echo / levels / modifiers (R8); hostile projectile deletion (P10); the
  SkyyArmory side of the stun-clock bridge (below); the first-use hints + the player "hints" switch (Class-Ability-Shapes.md section 9 -
  they name the R4 keys, so they come with R4); a shared cooldown when switching the Ability 1 alt (a question for Skyy).
FIX ROUND (critics, 2026-10-09): mid-air = feet off the ground and NOT swimming / in a fluid / creative-flying / climbing / riding /
  mantling / sitting (Abil.groundLike; gliding stays mid-air); the stun-clock bridge fails CLOSED (a published armory:fn:stunhit that throws
  or answers a non-number = the abil.bossWords rule, so a boss is never fully frozen past its breakout); the freeze also puts the vanilla
  Stun on (attacks off - the plan's "freeze = the vanilla Stun"; row abil.freezeStun, default on) and a break takes both off; moving the
  Guardian Spirit passive into a primary slot on the page says that key now does nothing (it still saves from any slot).
FIX ROUND 2 (critics, 2026-10-09): a freeze never overwrites or takes off a Stun another mod put on (a Monk's stunlock): FROZEN records
  whether THIS freeze put the Stun on (hasFx before), only then a break takes it off; the BREAK DAMAGE of spec draft 2.3 (row
  ab.FrostNova.breakPower 0.5 x staff hit, a "FrostNova" hit from the caster - only while they are online in the mob's world); Guardian
  Spirit's record is keyed pkey|uuid (guardKey - per profile); the missing armory:fn:stunhit is an INFO line, not a WARN; the HUD shape
  hint [44] honours the player's /settings switches; /cast 3 | 4 in the air is refused (alts cannot be cast in the air); /class has an
  Abilities button (opens the Abilities page; a spacer for classes without abilities).
  BRIDGE CONTRACT (supersedes the plan's "entity UUID or network id" wording): Object[] { the mob's com.hypixel.hytale.component.Ref (an
  ENGINE class, the same in every mod's class loader - SkyyArmory's own Stun.BY is keyed by that Ref), java.util.UUID caster, String role
  or null, Long hold ms } -> a java.lang.Number; anything else is treated as "no bridge".
ARMORY FOLLOW-UP (for the next SkyyArmory round after 0.1.15 - paste-ready; built + bare-JVM tested on 2026-10-09 as a SkyyArmory 0.1.14 +
  bridge jar, then withdrawn because the 0.1.15 number belongs to the UT-items round). In the Stun class, right after bossHit:
      public static long abilHit(Object target, java.util.UUID who, String role, long now, long holdMs) {
        if (!ArmoryCfg.PART_STUN || target == null || who == null) return -1L;
        if (!bossRole(role, ArmoryCfg.STUN_BOSS)) return -1L;
        long gap = Math.round(ArmoryCfg.STUN_GAP * 1000.0);
        StunRec r = (StunRec) BY.get(target);
        if (r != null && r.openUntil > now) { IGNORED = IGNORED + 1L; return 0L; }          // breakout window: do not freeze
        if (r != null && r.openUntil > 0L) r = null;
        if (r == null || now - r.last > gap) { r = new StunRec(now); BY.put(target, r); tidy(now); }
        long hold = holdMs < 0L ? 0L : holdMs;
        r.who.put(who, Long.valueOf(now + hold));                                         // the caster counts until the freeze ends
        int n = players(r, now, gap);
        long left = needMs(n) - (now - r.start);
        if (left <= 0L) { r.openUntil = now + Math.round(ArmoryCfg.STUN_WINDOW * 1000.0); r.last = now; BREAKS = BREAKS + 1L; return 0L; }
        if (hold > left) hold = left;                                                      // never past the breakout
        r.who.put(who, Long.valueOf(now + hold));
        if (now + hold > r.last) r.last = now + hold;                                      // stun.gap does not restart it while frozen
        return hold > 0L ? hold : 0L;
      }
  + a Function class ArmoryStunFn: apply(Object[] {target, UUID who, String role, Number holdMs}) -> Long.valueOf(Stun.abilHit(...,
  System.currentTimeMillis(), hold)), -1 on bad input / any error; publish() b.put("armory:fn:stunhit", new ArmoryStunFn()) and the key in
  BRIDGE_KEYS (unpublish). Tested contract: not a boss -1, breakout window 0, a hold cut to the time left, a Monk + a Mage on one clock.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.17.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.18.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.17"' in s and "GENERATED by tools/classes_0_1_17_patch.py from the generated 0.1.16" in s, \
    "build_skyyclasses_0.1.17.py is not the generated 0.1.17"
assert "AbilFrostSys" not in s and "GuardianSpirit.health" not in s
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def rep_method(cls_var, sig, new_body):
    """replace the whole M(<cls_var>, r'''\\n<sig>...}''') block whose first line is sig (exactly one) with new_body (the Java text)"""
    global s
    head = 'M(%s, r"""\n%s' % (cls_var, sig)
    assert s.count(head) == 1, "method anchor count %d: %s" % (s.count(head), sig)
    i = s.index(head)
    j = s.index('}""")', i) + len('}""")')
    body = new_body.strip("\n")
    assert body.endswith("}"), sig
    s = s[:i] + 'M(%s, r"""\n%s\n}""")' % (cls_var, body[:-1].rstrip()) + s[j:]


def cut_method(cls_var, sig):
    """cut the whole M(<cls_var>, r'''\\n<sig>...}''') block out of s (a comment stays) and return its text - it is re-added further down,
    after the new methods it calls (javassist compiles a call only to a method that already exists: methods before callers)"""
    global s
    head = 'M(%s, r"""\n%s' % (cls_var, sig)
    assert s.count(head) == 1, "method anchor count %d: %s" % (s.count(head), sig)
    i = s.index(head)
    j = s.index('}""")', i) + len('}""")')
    txt = s[i:j]
    s = s[:i] + "# 0.1.18: %s moved below (it now calls methods added after this point)" % sig.split("(")[0].split(" ")[-1] + s[j:]
    return txt


# ================================================================================================ docstring, Run line, version
rep('''"""SkyyClasses 0.1.17 - build script (javassist via jpype). GENERATED by tools/classes_0_1_17_patch.py from the generated 0.1.16 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_16_patch.py -> 0.1.16) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.18 - build script (javassist via jpype). GENERATED by tools/classes_0_1_18_patch.py from the generated 0.1.17 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_17_patch.py -> 0.1.17) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
0.1.18 (2026-10-09; research/cloud/Ability-Engine-Plan.md rounds R5 + R6 + R7 - R4 waits for Hytale 0.7):
  SHAPES - walking / sprinting / mid-air / crouch for every ability (the resolver at the press; per-shape Mana + Stamina + cooldown rows;
  /classadmin shape forces one for tests); GUARDIAN SPIRIT (Priest passive: a killing blow near you leaves the player at 30 %, 15 Mana +
  1 Stamina, 12 s doubling cooldown per saved player); FROST NOVA (freeze + chill; bosses on the shared stunlock clock through
  armory:fn:stunhit once SkyyArmory publishes it - until then bosses are only chilled); STARFALL, ARCANE BEAM (channel), SANCTUARY (zone), MARTYR'S GRACE (chain); the Abilities page (/cast page: swap
  slots = pick primaries + key order, the Ability 1 alt pick; out of combat); class:fn:abil -> Object[48] (first 44 as 0.1.17). Notes in
  tools/classes_0_1_18_patch.py.
''')
rep('''Run:   python build_skyyclasses_0.1.17.py           -> SkyyClasses/SkyyClasses-0.1.17.jar''',
    '''Run:   python build_skyyclasses_0.1.18.py           -> SkyyClasses/SkyyClasses-0.1.18.jar''')
rep('VERSION = "0.1.17"\n', 'VERSION = "0.1.18"\n')

# ================================================================================================ the registry: everything built now
for _id, _nm, _t, _pas in (("FrostNova", "Frost Nova", 2, False), ("Starfall", "Starfall", 3, False), ("ArcaneBeam", "Arcane Beam", 4, False),
                           ("GuardianSpirit", "Guardian Spirit", 2, True), ("Sanctuary", "Sanctuary", 3, False),
                           ("MartyrsGrace", "Martyr's Grace", 4, False)):
    _c = "Mage" if _id in ("FrostNova", "Starfall", "ArcaneBeam") else "Priest"
    rep('''    ("%s", "%s", "%s", %d, False, %s),''' % (_id, _nm, _c, _t, _pas),
        '''    ("%s", "%s", "%s", %d, True, %s),%s# 0.1.18: built''' % (_id, _nm, _c, _t, _pas, " " * max(1, 22 - len(_id) - len(_nm))))

# ================================================================================================ the 0.1.18 rows (Python, before ABIL_LINES)
ROWS_PY = r'''
# =====================================================================================================================
# 0.1.18 (rounds R5 + R6 + R7; tools/classes_0_1_18_patch.py has the notes): SHAPES for every ability + Frost Nova, Guardian Spirit,
# Starfall, Arcane Beam, Sanctuary, Martyr's Grace. Costs per shape = research/cloud/Ability-Engine-Plan.md 4.3: power (the old Mana-only
# number of research/cloud/Class-Ability-Shapes.md) x the class split, rounded half up, min 1 each - asserted against the plan's table.
# =====================================================================================================================
SHAPES = ["walk", "sprint", "air", "crouch"]
SHAPE_SUFFIX = ["", "_SP", "_AI", "_CR"]
# id -> (row field prefix, Server Setup category of the NEW rows, [(power, cooldown s) walk, sprint, air, crouch])
SHAPE_POWER = [
    ("Meteor", "M", "abils", [(30, 14), (30, 14), (30, 16), (26, 14)]),
    ("ManaBarrier", "B", "abils", [(20, 30), (20, 30), (20, 30), (18, 28)]),
    ("FrostNova", "F", "abilm", [(24, 22), (24, 22), (24, 24), (26, 24)]),
    ("Starfall", "T", "abilm", [(36, 18), (36, 18), (36, 20), (40, 22)]),
    ("ArcaneBeam", "R", "abilm", [(30, 18), (28, 18), (30, 20), (34, 22)]),
    ("SacredHeal", "S", "abils", [(25, 14), (25, 14), (25, 14), (28, 16)]),
    ("ShieldBubble", "U", "abils", [(28, 24), (28, 24), (28, 24), (28, 26)]),
    ("Sanctuary", "Y", "abilp", [(35, 28), (35, 28), (35, 28), (35, 30)]),
    ("MartyrsGrace", "G", "abilp", [(30, 18), (30, 18), (30, 18), (34, 20)]),
]
SHAPE_NAMES = {
    "Meteor": ["Meteor", "Comet", "Under Me", "Meteor on Me"],
    "ManaBarrier": ["Mana Barrier", "Barrier Ahead", "Landing Dome", "Pocket Dome"],
    "FrostNova": ["Frost Nova", "Frost Wake", "Frost Drop", "Deep Freeze"],
    "Starfall": ["Starfall", "Star Trail", "Starfall Below", "Star Shower"],
    "ArcaneBeam": ["Arcane Beam", "Sweep Beam", "Beam Down", "Focused Beam"],
    "SacredHeal": ["Sacred Heal", "Running Blessing", "Beacon", "Kneel"],
    "ShieldBubble": ["Shield Bubble", "Bubble Ahead", "Bubble Below", "Around Me"],
    "GuardianSpirit": ["Guardian Spirit", "Guardian Spirit", "Guardian Spirit", "Guardian Spirit"],
    "Sanctuary": ["Sanctuary", "Pilgrim's Path", "Landing Sanctuary", "Inner Sanctum"],
    "MartyrsGrace": ["Martyr's Grace", "Grace in Motion", "Descent", "Martyr's Vow"],
}
# the plan's 4.3 table (Mana, Stamina, cooldown) per shape - the split must reproduce it exactly
PLAN_43 = {
    "Meteor": [(23, 2, 14), (23, 2, 14), (23, 2, 16), (20, 1, 14)],
    "ManaBarrier": [(16, 1, 30), (16, 1, 30), (16, 1, 30), (14, 1, 28)],
    "FrostNova": [(19, 1, 22), (19, 1, 22), (19, 1, 24), (20, 1, 24)],
    "Starfall": [(28, 2, 18), (28, 2, 18), (28, 2, 20), (31, 2, 22)],
    "ArcaneBeam": [(23, 2, 18), (22, 2, 18), (23, 2, 20), (27, 2, 22)],
    "SacredHeal": [(18, 2, 14), (18, 2, 14), (18, 2, 14), (20, 2, 16)],
    "ShieldBubble": [(20, 2, 24), (20, 2, 24), (20, 2, 24), (20, 2, 26)],
    "Sanctuary": [(26, 2, 28), (26, 2, 28), (26, 2, 28), (26, 2, 30)],
    "MartyrsGrace": [(22, 2, 18), (22, 2, 18), (22, 2, 18), (25, 2, 20)],
}
_SPLIT = {"Mage": (0.78, 0.22), "Priest": (0.73, 0.27)}


def split_cost(power, cls):
    """research/Class-Power-Split.md: Mana = power x the class's Mana %, Stamina = power x its Stamina % / 4; half up, min 1 each"""
    m_, s_ = _SPLIT[cls]
    return float(max(1, int(power * m_ + 0.5))), float(max(1, int(power * s_ / 4.0 + 0.5)))


_ACLS = dict((a[0], a[2]) for a in ABILS)
for _id, _p, _cat, _pw in SHAPE_POWER:
    for _k in range(4):
        _m, _st = split_cost(_pw[_k][0], _ACLS[_id])
        assert (int(_m), int(_st), _pw[_k][1]) == PLAN_43[_id][_k], "%s %s: %s + %s / %s s != plan 4.3 %s" % (_id, SHAPES[_k], _m, _st, _pw[_k][1], PLAN_43[_id][_k])
        if _k == 0 and _id in ("Meteor", "ManaBarrier", "SacredHeal", "ShieldBubble"):
            continue          # their walking rows exist since 0.1.16 / 0.1.17 (same keys, same numbers - asserted below)
        _sn = SHAPE_NAMES[_id][_k]
        _lab = _sn if _k == 0 else "%s (%s)" % (dict((a[0], a[1]) for a in ABILS)[_id], _sn)
        if len(_lab) + len(" cooldown") > 40:
            _lab = _sn          # e.g. "Grace in Motion" (the row's category and help say which ability)
        _cat2 = _cat if _k == 0 or _cat != "abils" else "abils"
        ABIL_ROWS.append(("ab.%s.%s.mana" % (_id, SHAPES[_k]), "%s_MANA%s" % (_p, SHAPE_SUFFIX[_k]), "dec", _m, "0", "1000", "", _cat2, "live",
                          _lab + " Mana", "Mana per cast of this shape."))
        ABIL_ROWS.append(("ab.%s.%s.stamina" % (_id, SHAPES[_k]), "%s_STAM%s" % (_p, SHAPE_SUFFIX[_k]), "dec", _st, "0", "100", "", _cat2, "live",
                          _lab + " Stamina", "Stamina per cast of this shape."))
        ABIL_ROWS.append(("ab.%s.%s.cooldown" % (_id, SHAPES[_k]), "%s_CD%s" % (_p, SHAPE_SUFFIX[_k]), "dec", float(_pw[_k][1]), "0", "600", "s", _cat2,
                          "live", _lab + " cooldown", "Seconds before the ability can be cast again after this shape."))


def _r(key, field, typ, dv, lo, hi, unit, cat, label, help_, flags="live"):
    ABIL_ROWS.append((key, field, typ, dv, lo, hi, unit, cat, flags, label, help_))


# the shape resolver + the shared shape numbers (Ability shapes)
_r("abil.shapes", "SHAPES", "bool", True, "", "", "", "abils", "Ability shapes", "Off: every cast uses its walking shape (crouch still casts your alts).")
_r("abil.shapes.sprint", "SHAPES_SPRINT", "bool", True, "", "", "", "abils", "Sprinting shapes", "Off: casting while sprinting uses the walking shape.")
_r("abil.shapes.air", "SHAPES_AIR", "bool", True, "", "", "", "abils", "Mid-air shapes", "Off: casting in the air uses the walking shape.")
_r("abil.crouchMin", "CROUCH_MIN", "dec", 0.1, "0", "1", "s", "abils", "Crouch held before it counts", "Crouch must be held this long for your alt.", "live,adv")
_r("abil.airMin", "AIR_MIN", "dec", 0.15, "0", "1", "s", "abils", "Time in the air for mid-air shapes", "In the air at least this long = the mid-air shape.", "live,adv")
_r("abil.landWait", "LAND_WAIT", "dec", 2.0, "0.5", "5", "s", "abils", "Longest wait for a landing", "On-landing shapes fire where you are after this long.", "live,adv")
_r("abil.ahead", "AHEAD", "dec", 6.0, "2", "16", "blocks", "abils", "Sprint shapes: blocks ahead", "Comet, Barrier Ahead and Bubble Ahead land this far ahead.")
_r("abil.channelMove", "CHAN_MOVE", "dec", 1.0, "0.2", "5", "blocks", "abils", "Channel: most you may move", "Kneel / Martyr's Vow break (all given back) if you move further.", "live,adv")
_r("ab.Meteor.cometRadius", "M_COMET_R", "dec", 3.0, "1", "16", "blocks", "abils", "Comet size", "Comet (sprint): enemies this close to the impact are hit.")
_r("ab.Meteor.onMeRadius", "M_ONME_R", "dec", 5.0, "1", "16", "blocks", "abils", "Meteor on Me size", "Meteor on Me (crouch): enemies this close to you are hit.")
_r("ab.Meteor.onMePower", "M_ONME_P", "dec", 2.5, "0", "100", "x", "abils", "Meteor on Me damage (x staff hit)", "You never take any of it.")
_r("ab.Meteor.onMeDelay", "M_ONME_D", "dec", 0.5, "0", "5", "s", "abils", "Meteor on Me fall time", "Seconds from the cast to the impact on you.")
_r("ab.ManaBarrier.pocketRadius", "B_POCKET_R", "dec", 4.0, "2", "12", "blocks", "abils", "Pocket Dome size", "Pocket Dome (crouch): a dome on you.")
_r("ab.ManaBarrier.pocketTime", "B_POCKET_T", "dec", 10.0, "1", "60", "s", "abils", "Pocket Dome length", "Seconds the Pocket Dome lasts.")
_r("ab.ManaBarrier.pocketRatio", "B_POCKET_RATIO", "dec", 2.5, "0.5", "10", "x", "abils", "Pocket Dome damage per Mana", "2.5 = every 2.5 damage costs 1 Mana.")
_r("ab.ShieldBubble.aroundRadius", "U_AROUND_R", "dec", 5.0, "2", "16", "blocks", "abils", "Around Me size", "Around Me (crouch): a bubble on you.")
_r("ab.ShieldBubble.aroundHp", "U_AROUND_HP", "int", 110, "10", "500", "%", "abils", "Around Me strength (% max Health)", "How much damage Around Me soaks.")
_r("ab.SacredHeal.blessRadius", "S_BLESS_R", "dec", 6.0, "1", "16", "blocks", "abils", "Running Blessing size", "The circle that follows you (sprint).")
_r("ab.SacredHeal.blessTime", "S_BLESS_T", "dec", 2.0, "0.5", "10", "s", "abils", "Running Blessing length", "Seconds the circle follows you.")
_r("ab.SacredHeal.blessHeal", "S_BLESS_H", "int", 20, "0", "100", "%", "abils", "Running Blessing heal (% max Health)", "Each player it touches, once (+ the heal over time).")
_r("ab.SacredHeal.beaconRadius", "S_BEACON_R", "dec", 10.0, "1", "32", "blocks", "abils", "Beacon size", "Beacon (mid-air): the heal where you land.")
_r("ab.SacredHeal.kneelBonus", "S_KNEEL", "int", 20, "0", "200", "%", "abils", "Kneel extra heal", "Kneel (crouch): the instant heal this % stronger.")
_r("ab.SacredHeal.kneelHot", "S_KNEEL_HOT", "int", 200, "0", "500", "%", "abils", "Kneel heal over time (% of normal)", "200 = doubled.")
_r("ab.SacredHeal.kneelTime", "S_KNEEL_T", "dec", 1.0, "0", "5", "s", "abils", "Kneel channel", "Seconds you kneel before the heal.")
# Frost Nova (Mage A2-alt) - spec draft 2.3
_r("ab.FrostNova.radius", "F_RADIUS", "dec", 5.0, "1", "16", "blocks", "abilm", "Frost Nova size", "Enemies this close to you freeze.")
_r("ab.FrostNova.power", "F_POWER", "dec", 1.0, "0", "100", "x", "abilm", "Frost Nova damage (x staff hit)", "Damage on the freeze.")
_r("ab.FrostNova.freeze", "F_FREEZE", "dec", 2.0, "0.2", "10", "s", "abilm", "Freeze length", "Frozen mobs cannot move (vanilla Freeze).")
_r("ab.FrostNova.breakAfter", "F_BREAK", "dec", 1.0, "0", "10", "s", "abilm", "A hit breaks the freeze after", "Hits in the first seconds do not break it.")
_r("ab.FrostNova.breakPower", "F_BREAK_P", "dec", 0.5, "0", "100", "x", "abilm", "Break damage (x staff hit)", "Extra damage on the mob when a hit breaks its freeze.")   # FIX 2
_r("ab.FrostNova.chill", "F_CHILL", "dec", 3.0, "0", "20", "s", "abilm", "Chill after the freeze", "Seconds the mob stays slowed (vanilla Slow).")
_r("ab.FrostNova.wakeLength", "F_WAKE_L", "dec", 8.0, "2", "24", "blocks", "abilm", "Frost Wake length", "The freezing strip behind you (sprint).")
_r("ab.FrostNova.wakeWidth", "F_WAKE_W", "dec", 2.0, "1", "8", "blocks", "abilm", "Frost Wake width", "How wide the strip is.")
_r("ab.FrostNova.wakeTime", "F_WAKE_T", "dec", 3.0, "0.5", "20", "s", "abilm", "Frost Wake length (time)", "Seconds the strip freezes what enters it.")
_r("ab.FrostNova.wakeFreeze", "F_WAKE_F", "dec", 1.5, "0.2", "10", "s", "abilm", "Frost Wake freeze", "Freeze length on the strip.")
_r("ab.FrostNova.dropRadius", "F_DROP_R", "dec", 6.0, "1", "16", "blocks", "abilm", "Frost Drop size", "Frost Drop (mid-air): the nova where you land.")
_r("ab.FrostNova.deepRadius", "F_DEEP_R", "dec", 4.0, "1", "16", "blocks", "abilm", "Deep Freeze size", "Deep Freeze (crouch): around you.")
_r("ab.FrostNova.deepFreeze", "F_DEEP_F", "dec", 3.0, "0.2", "10", "s", "abilm", "Deep Freeze length", "Freeze length of Deep Freeze.")
_r("abil.freezeStun", "FREEZE_STUN", "bool", True, "", "", "", "abilm", "Frozen mobs cannot attack", "On: the vanilla Stun goes with the Freeze (attacks off too).")
_r("ab.FrostNova.deepBreak", "F_DEEP_B", "dec", 2.0, "0", "10", "s", "abilm", "Deep Freeze unbreakable for", "Hits do not break Deep Freeze this long.")
_r("abil.bossWords", "BOSS_WORDS", "text", "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex,Ogre,Golem,Yeti", "", "200", "", "abilm",
   "Bosses (without the stun clock)", "Used only while SkyyArmory shares no stunlock clock: these mobs are chilled, never frozen.", "live,adv")
# Starfall (Mage A1-alt A) - spec draft 2.3
_r("ab.Starfall.stars", "T_STARS", "int", 12, "1", "40", "", "abilm", "Starfall stars", "Stars per Starfall (Star Trail too).")
_r("ab.Starfall.time", "T_TIME", "dec", 3.0, "0.5", "10", "s", "abilm", "Starfall length", "Seconds the stars fall over.")
_r("ab.Starfall.radius", "T_RADIUS", "dec", 6.0, "1", "16", "blocks", "abilm", "Starfall area", "The stars fall within this distance of the spot.")
_r("ab.Starfall.power", "T_POWER", "dec", 0.3, "0", "10", "x", "abilm", "Damage per star (x staff hit)", "Each star hits every enemy near its fall point.")
_r("ab.Starfall.starRadius", "T_STAR_R", "dec", 3.0, "0.5", "8", "blocks", "abilm", "Star hit size", "Enemies this close to a star's fall point are hit.")
_r("ab.Starfall.range", "T_RANGE", "dec", 25.0, "4", "64", "blocks", "abilm", "Starfall reach", "How far away the spot you look at may be.")
_r("ab.Starfall.belowRadius", "T_BELOW_R", "dec", 7.0, "1", "16", "blocks", "abilm", "Starfall Below area", "Starfall Below (mid-air): where you land.")
_r("ab.Starfall.belowTime", "T_BELOW_T", "dec", 2.0, "0.5", "10", "s", "abilm", "Starfall Below length", "Seconds its stars fall over.")
_r("ab.Starfall.showerStars", "T_SHOWER_N", "int", 16, "1", "40", "", "abilm", "Star Shower stars", "Star Shower (crouch): stars on you.")
_r("ab.Starfall.showerTime", "T_SHOWER_T", "dec", 4.0, "0.5", "10", "s", "abilm", "Star Shower length", "Seconds its stars fall over.")
# Arcane Beam (Mage A1-alt B) - spec draft 2.3
_r("ab.ArcaneBeam.range", "R_RANGE", "dec", 20.0, "2", "64", "blocks", "abilm", "Arcane Beam reach", "Beam length along your look.")
_r("ab.ArcaneBeam.time", "R_TIME", "dec", 3.0, "0.5", "10", "s", "abilm", "Arcane Beam length", "Seconds the beam channels.")
_r("ab.ArcaneBeam.rate", "R_RATE", "dec", 0.5, "0", "10", "x", "abilm", "Beam damage per second (x staff hit)", "At 1x; it ramps up while you channel.")
_r("ab.ArcaneBeam.ramp", "R_RAMP", "dec", 3.0, "1", "10", "x", "abilm", "Beam ramp (last second)", "3 = 1x, 2x, 3x over 3 s.")
_r("ab.ArcaneBeam.width", "R_WIDTH", "dec", 1.0, "0.2", "4", "blocks", "abilm", "Beam width", "Enemies this close to the beam line are on it.")
_r("ab.ArcaneBeam.sweepRange", "R_SWEEP_R", "dec", 15.0, "2", "64", "blocks", "abilm", "Sweep Beam reach", "Sweep Beam (sprint): hits every enemy on it.")
_r("ab.ArcaneBeam.sweepTime", "R_SWEEP_T", "dec", 2.0, "0.5", "10", "s", "abilm", "Sweep Beam length", "Seconds it channels.")
_r("ab.ArcaneBeam.sweepMult", "R_SWEEP_M", "dec", 1.5, "0", "10", "x", "abilm", "Sweep Beam power (flat)", "x the beam's 1x damage, no ramp.")
_r("ab.ArcaneBeam.sweepWidth", "R_SWEEP_W", "dec", 2.0, "0.2", "6", "blocks", "abilm", "Sweep Beam width", "Wider than the beam.")
_r("ab.ArcaneBeam.downRange", "R_DOWN_R", "dec", 12.0, "2", "64", "blocks", "abilm", "Beam Down reach", "Beam Down (mid-air): straight down.")
_r("ab.ArcaneBeam.downTime", "R_DOWN_T", "dec", 2.0, "0.5", "10", "s", "abilm", "Beam Down length", "Seconds it channels.")
_r("ab.ArcaneBeam.focusRange", "R_FOCUS_R", "dec", 25.0, "2", "64", "blocks", "abilm", "Focused Beam reach", "Focused Beam (crouch).")
_r("ab.ArcaneBeam.focusTime", "R_FOCUS_T", "dec", 4.0, "0.5", "10", "s", "abilm", "Focused Beam length", "Seconds it channels.")
_r("ab.ArcaneBeam.focusRamp", "R_FOCUS_RAMP", "dec", 3.5, "1", "10", "x", "abilm", "Focused Beam ramp (last second)", "3.5 = up to 3.5x.")
# Guardian Spirit (Priest A2-alt, passive) - spec draft 2.4, Skyy lines 145-146
_r("ab.GuardianSpirit.mana", "GS_MANA", "dec", 15.0, "0", "1000", "", "abilp", "Guardian Spirit Mana per save", "No Mana = no save.")
_r("ab.GuardianSpirit.stamina", "GS_STAM", "dec", 1.0, "0", "100", "", "abilp", "Guardian Spirit Stamina per save", "No Stamina = no save.")
_r("ab.GuardianSpirit.health", "GS_HP", "int", 30, "1", "100", "%", "abilp", "Saved at (% max Health)", "A killing blow leaves the player at this Health.")
_r("ab.GuardianSpirit.cooldown", "GS_CD", "dec", 12.0, "0", "600", "s", "abilp", "Save cooldown per player (doubles)", "12 = saves at 0, 12, 36, 84 s for one player.")
_r("ab.GuardianSpirit.resetAfter", "GS_RESET", "dec", 30.0, "1", "600", "s", "abilp", "Doubling resets after (no damage)", "Seconds without damage that reset a player's save count.")
_r("ab.GuardianSpirit.radius", "GS_RADIUS", "dec", 30.0, "1", "128", "blocks", "abilp", "Guardian Spirit aura", "Players this close to the Priest can be saved.")
_r("ab.GuardianSpirit.everyone", "GS_ALL", "bool", False, "", "", "", "abilp", "Guardian Spirit saves everyone", "Off: the Priest and their party only (Skyy's default).")
# Sanctuary (Priest A1-alt A) - spec draft 2.4, Skyy line 142
_r("ab.Sanctuary.radius", "Y_RADIUS", "dec", 8.0, "1", "32", "blocks", "abilp", "Sanctuary size", "The holy zone under you.")
_r("ab.Sanctuary.time", "Y_TIME", "dec", 12.0, "1", "60", "s", "abilp", "Sanctuary length", "Seconds the zone lasts.")
_r("ab.Sanctuary.heal", "Y_HEAL", "int", 5, "0", "50", "%", "abilp", "Sanctuary heal per second (% max)", "You and your party inside (others the othersPercent share).")
_r("ab.Sanctuary.cut", "Y_CUT", "int", 10, "0", "90", "%", "abilp", "Sanctuary damage cut", "You and your party inside take this % less damage.")
_r("ab.Sanctuary.ahead", "Y_AHEAD", "dec", 5.0, "1", "16", "blocks", "abilp", "Pilgrim's Path: blocks ahead", "Pilgrim's Path (sprint) lands this far ahead.")
_r("ab.Sanctuary.innerRadius", "Y_IN_R", "dec", 5.0, "1", "32", "blocks", "abilp", "Inner Sanctum size", "Inner Sanctum (crouch): on you.")
_r("ab.Sanctuary.innerHeal", "Y_IN_H", "int", 7, "0", "50", "%", "abilp", "Inner Sanctum heal per second", "% of max Health a second.")
_r("ab.Sanctuary.innerCut", "Y_IN_C", "int", 15, "0", "90", "%", "abilp", "Inner Sanctum damage cut", "% less damage inside.")
_r("ab.Sanctuary.innerTime", "Y_IN_T", "dec", 10.0, "1", "60", "s", "abilp", "Inner Sanctum length", "Seconds it lasts.")
# Martyr's Grace (Priest A1-alt B) - spec draft 2.4, Skyy lines 143-144
_r("ab.MartyrsGrace.range", "G_RANGE", "dec", 30.0, "1", "128", "blocks", "abilp", "Martyr's Grace reach", "Hurt players this close to you can be healed.")
_r("ab.MartyrsGrace.first", "G_FIRST", "int", 75, "0", "100", "%", "abilp", "First heal (% max Health)", "The lowest player first; party (and you) before others.")
_r("ab.MartyrsGrace.drop", "G_DROP", "int", 15, "0", "100", "%", "abilp", "Less per jump", "75 / 60 / 45 / 30 / 15 with 15.")
_r("ab.MartyrsGrace.targets", "G_TARGETS", "int", 5, "1", "20", "", "abilp", "Most players healed", "The chain stops after this many.")
_r("ab.MartyrsGrace.firstCap", "G_CAP", "int", 90, "10", "100", "%", "abilp", "First heal cap (% max Health)", "The one heal above the ability heal cap.")
_r("ab.MartyrsGrace.vowFirst", "G_VOW_F", "int", 90, "0", "100", "%", "abilp", "Martyr's Vow first heal", "Martyr's Vow (crouch): the first heal.")
_r("ab.MartyrsGrace.vowDrop", "G_VOW_D", "int", 20, "0", "100", "%", "abilp", "Martyr's Vow less per jump", "90 / 70 / 50 / 30 / 10 with 20.")
_r("ab.MartyrsGrace.vowTime", "G_VOW_T", "dec", 1.0, "0", "5", "s", "abilp", "Martyr's Vow channel", "Seconds you channel before the chain.")
# the walking rows of the 0.1.16 / 0.1.17 abilities are the plan's walking numbers (same keys as before - no file changes)
assert [(_r_[3]) for _r_ in ABIL_ROWS if _r_[0] in ("ab.Meteor.walk.mana", "ab.ManaBarrier.walk.mana", "ab.SacredHeal.walk.mana", "ab.ShieldBubble.walk.mana")] == [23.0, 18.0, 16.0, 20.0]
# AFFORDABLE WHEN UNLOCKED (Skyy line 173; plan 4.4 pools without boosts): every shape of every ability at its unlock level fits both pools
_POOL = {("Mage", 1): (55, 14.05), ("Mage", 10): (145, 14.5), ("Mage", 20): (245, 15.0), ("Mage", 30): (345, 15.5),
         ("Priest", 1): (47, 15.06), ("Priest", 10): (92, 15.6), ("Priest", 20): (142, 16.2), ("Priest", 30): (192, 16.8)}
_UNL = {0: 1, 1: 10, 2: 20, 3: 30, 4: 30}
_ROWV = dict((_r_[0], _r_[3]) for _r_ in ABIL_ROWS)
_aff = 0
for _a in ABILS:
    _pm, _ps = _POOL[(_a[2], _UNL[_a[3]])]
    if _a[0] == "GuardianSpirit":
        assert _ROWV["ab.GuardianSpirit.mana"] <= _pm and _ROWV["ab.GuardianSpirit.stamina"] <= _ps
        _aff += 1
        continue
    for _sh in SHAPES:
        _mm = _ROWV["ab.%s.%s.mana" % (_a[0], _sh)] + (_ROWV["ab.ManaBarrier.keep"] if _a[0] == "ManaBarrier" else 0.0)
        assert _mm <= _pm and _ROWV["ab.%s.%s.stamina" % (_a[0], _sh)] <= _ps, "%s %s not affordable at its unlock" % (_a[0], _sh)
        _aff += 1
assert _aff == 37, _aff          # the plan's "all 37 shape rows PASS"
'''
rep('''for _r in ABIL_ROWS:
    assert len(_r[9]) <= 40 and len(_r[10]) <= 100, _r[0]''', ROWS_PY + '''for _r in ABIL_ROWS:
    assert len(_r[9]) <= 40 and len(_r[10]) <= 100, _r[0]''')
rep('''    "# Meteor damage = power x one charged shot of the staff or wand held (abil.hitFallback for weapons SkyyArmory does not know).",
]''', '''    "# Meteor damage = power x one charged shot of the staff or wand held (abil.hitFallback for weapons SkyyArmory does not know).",
    "# 0.1.18: ab.<Ability>.sprint / .air / .crouch = the shapes (sprinting, mid-air, crouch alt); abil.shapes* switch them off.",
]''')
rep('''            ("abil", "Abilities"), ("abilx", "Ability numbers")]                                                         # 0.1.16''',
    '''            ("abil", "Abilities"), ("abilx", "Ability numbers"),                                                         # 0.1.16
            ("abils", "Ability shapes"), ("abilm", "Mage abilities 2"), ("abilp", "Priest abilities 2")]       # 0.1.18''')

# ================================================================================================ engine tokens + probes
rep('''    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD":  "com.hypixel.hytale.component.dependency.Order",
}''', '''    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD":  "com.hypixel.hytale.component.dependency.Order",
    # 0.1.18: the look (TargetUtil.getLook -> Transform), the vanilla Freeze / Slow effects (the SkyyArmory ArmoryTree.stun shapes)
    "XFM":  "com.hypixel.hytale.math.vector.Transform",
    "ECC":  "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "EFX":  "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "OVB":  "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior",
}''')
rep('''assert pool.get(T["DPRJ"]).subtypeOf(pool.get(T["DENT"])), "a projectile source is an entity source (the bubble soaks arrows as attacks)"
''', '''assert pool.get(T["DPRJ"]).subtypeOf(pool.get(T["DENT"])), "a projectile source is an entity source (the bubble soaks arrows as attacks)"
# 0.1.18 (shapes, Frost Nova, Guardian Spirit, beams, chains): every new engine member with the descriptor the code calls
for c, m, d in ((T["TU"], "getLook", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/ComponentAccessor;)Lcom/hypixel/hytale/math/vector/Transform;"),
                (T["TU"], "getTargetEntity", "(Lcom/hypixel/hytale/component/Ref;FLcom/hypixel/hytale/component/ComponentAccessor;)Lcom/hypixel/hytale/component/Ref;"),
                (T["XFM"], "getPosition", "()Lorg/joml/Vector3d;"), (T["XFM"], "getDirection", "()Lorg/joml/Vector3d;"),
                (T["ECC"], "addEffect", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/asset/type/entityeffect/config/EntityEffect;FLcom/hypixel/hytale/server/core/asset/type/entityeffect/config/OverlapBehavior;Lcom/hypixel/hytale/component/ComponentAccessor;)Z"),
                (T["ECC"], "removeEffect", "(Lcom/hypixel/hytale/component/Ref;ILcom/hypixel/hytale/component/ComponentAccessor;)V"),
                (T["ECC"], "hasEffect", "(I)Z"), (T["ESM"], "setStatValue", "(IF)F"),
                (T["DMOD"], "getInspectDamageGroup", "()Lcom/hypixel/hytale/component/SystemGroup;")):
    assert str(pool.get(c).getMethod(m, d).getName()) == m, "%s.%s%s" % (c, m, d)
for c, m in ((T["ECC"], "getComponentType"), (T["EFX"], "getAssetMap"), (T["OVB"], "OVERWRITE"), (T["MST"], "onGround"), (T["MST"], "sprinting"),
             (T["MST"], "flying"), (T["MST"], "swimming"), (T["MST"], "inFluid"), (T["MST"], "climbing"), (T["MST"], "mounting"),
             (T["MST"], "mantling"), (T["MST"], "sitting"), (T["MST"], "gliding"),
             (T["UNI"], "getPlayers")):
    B.probe(pool, c, m)
''')

# ================================================================================================ the vanilla effects + particles
rep('''      "FX_BARRIER": "Rings_Rings", "FX_BUBBLE": "Rings_Rings_Ice", "FX_BUBBLE_ON": "Shield_Block", "FX_BREAK": "Shield_Shatter",
      "FX_END": "Item_Break_GlassMagic"}''', '''      "FX_BARRIER": "Rings_Rings", "FX_BUBBLE": "Rings_Rings_Ice", "FX_BUBBLE_ON": "Shield_Block", "FX_BREAK": "Shield_Shatter",
      "FX_END": "Item_Break_GlassMagic",
      # 0.1.18: Frost Nova (burst + per-mob hit), Starfall (each star), Arcane Beam (points along the beam), Sanctuary + Running Blessing
      # rims, the Guardian Spirit save - all finite one-shots (checked below like the 0.1.16 ones)
      "FX_FROST": "Ice_Blast", "FX_FROST_HIT": "Impact_Ice", "FX_STAR": "Explosion_Small", "FX_BEAM": "Blue_Beam",
      "FX_HOLY": "Totem_Heal_Extra", "FX_BLESS": "Potion_Health_Heal", "FX_GUARD": "Potion_Health_Implosion"}''')
rep('''print("ability particles (vanilla, finite one-shots): %s" % ", ".join(sorted(FX.values())))''',
    '''print("ability particles (vanilla, finite one-shots): %s" % ", ".join(sorted(FX.values())))
# 0.1.18: the vanilla status effects Frost Nova applies (Freeze = movement off + the icy look; Slow = the Chill)
EF_FREEZE, EF_SLOW, EF_STUN = "Freeze", "Slow", "Stun"
_efz = json.loads(_ASSETS.read("Server/Entity/Effects/Status/%s.json" % EF_FREEZE).decode("utf-8-sig"))
_efs = json.loads(_ASSETS.read("Server/Entity/Effects/Status/%s.json" % EF_SLOW).decode("utf-8-sig"))
assert _efz["ApplicationEffects"]["MovementEffects"]["DisableAll"] is True, "the vanilla Freeze effect no longer stops movement"
assert 0.0 < _efs["ApplicationEffects"]["HorizontalSpeedMultiplier"] < 1.0, "the vanilla Slow effect no longer slows"
# FIX ROUND (critic): Freeze only stops MOVEMENT; the vanilla Stun also turns the mob's attacks off (SkyyArmory puts it on mobs since 0.1.7)
_eft = json.loads(_ASSETS.read("Server/Entity/Effects/Status/%s.json" % EF_STUN).decode("utf-8-sig"))
assert _eft["ApplicationEffects"]["MovementEffects"]["DisableAll"] is True and "Primary" in _eft["ApplicationEffects"]["AbilityEffects"]["Disabled"],     "the vanilla Stun effect no longer turns attacks off"
print("ability effects (vanilla): %s (movement off), %s (x%s speed)" % (EF_FREEZE, EF_SLOW, _efs["ApplicationEffects"]["HorizontalSpeedMultiplier"]))''')

# ================================================================================================ AbilCfg.text: + the 0.1.18 abilities (after the 0.1.17 ")")
rep('''    + ", Shield Bubble " + @PKG@.ClassCfg.fmtNum(U_MANA) + "+" + @PKG@.ClassCfg.fmtNum(U_STAM) + "/" + @PKG@.ClassCfg.fmtNum(U_CD) + "s)";''',
    '''    + ", Shield Bubble " + @PKG@.ClassCfg.fmtNum(U_MANA) + "+" + @PKG@.ClassCfg.fmtNum(U_STAM) + "/" + @PKG@.ClassCfg.fmtNum(U_CD) + "s)"
    + " shapes=" + (SHAPES ? "on" : "off") + " (Frost Nova " + @PKG@.ClassCfg.fmtNum(F_MANA) + "+" + @PKG@.ClassCfg.fmtNum(F_STAM) + "/" + @PKG@.ClassCfg.fmtNum(F_CD) + "s"
    + ", Starfall " + @PKG@.ClassCfg.fmtNum(T_MANA) + "+" + @PKG@.ClassCfg.fmtNum(T_STAM) + "/" + @PKG@.ClassCfg.fmtNum(T_CD) + "s"
    + ", Arcane Beam " + @PKG@.ClassCfg.fmtNum(R_MANA) + "+" + @PKG@.ClassCfg.fmtNum(R_STAM) + "/" + @PKG@.ClassCfg.fmtNum(R_CD) + "s"
    + ", Guardian Spirit " + @PKG@.ClassCfg.fmtNum(GS_MANA) + "+" + @PKG@.ClassCfg.fmtNum(GS_STAM) + " a save"
    + ", Sanctuary " + @PKG@.ClassCfg.fmtNum(Y_MANA) + "+" + @PKG@.ClassCfg.fmtNum(Y_STAM) + "/" + @PKG@.ClassCfg.fmtNum(Y_CD) + "s"
    + ", Martyr's Grace " + @PKG@.ClassCfg.fmtNum(G_MANA) + "+" + @PKG@.ClassCfg.fmtNum(G_STAM) + "/" + @PKG@.ClassCfg.fmtNum(G_CD) + "s)";''')

# ================================================================================================ AbilDefs: indices, shape names, costs per shape
ABIL_DESCS = {
    "Meteor": "Walk - a meteor where you look. Sprint - Comet lands ahead. Air - lands where you land. Crouch - on you (you take none).",
    "ManaBarrier": "Walk - a dome where you look. Sprint - ahead. Air - where you land. Crouch - Pocket Dome on you.",
    "FrostNova": "Walk - freeze enemies around you. Sprint - a freezing strip behind you. Air - on landing. Crouch - Deep Freeze.",
    "Starfall": "Walk - stars rain where you look. Sprint - along your path. Air - where you land. Crouch - Star Shower on you.",
    "ArcaneBeam": "Walk - a beam that grows stronger. Sprint - sweeps every enemy on it. Air - straight down. Crouch - Focused Beam.",
    "SacredHeal": "Walk - heals everyone near you. Sprint - a circle follows you. Air - Beacon where you land. Crouch - Kneel (stronger).",
    "ShieldBubble": "Walk - a bubble where you look. Sprint - ahead. Air - where you land. Crouch - Around Me (stronger).",
    "GuardianSpirit": "Passive - always on. A killing blow on you or your party near you leaves them alive (costs Mana).",
    "Sanctuary": "Walk - a holy zone under you (heals and protects). Sprint - ahead. Air - where you land. Crouch - Inner Sanctum.",
    "MartyrsGrace": "Walk - heals the lowest players in a chain. Sprint - the one you look at first. Air - you first. Crouch - Martyr's Vow.",
}
rep('''_aff = 0
for _a in ABILS:''', '''ABIL_DESCS_ = %r   # 0.1.18: the Abilities page's one line per ability
assert sorted(ABIL_DESCS_) == sorted(a[0] for a in ABILS) and all(len(v) <= 130 for v in ABIL_DESCS_.values())
_aff = 0
for _a in ABILS:''' % ABIL_DESCS)
rep('''F(abdefs, "public static final int BUBBLE = %d;" % [a[0] for a in ABILS].index("ShieldBubble"))   # 0.1.17''',
    '''F(abdefs, "public static final int BUBBLE = %d;" % [a[0] for a in ABILS].index("ShieldBubble"))   # 0.1.17
# 0.1.18: the R6 / R7 abilities, the shapes, the shape names (chat lines), the page's one-line description per ability
for _n_, _id_ in (("FROST", "FrostNova"), ("STARF", "Starfall"), ("BEAM", "ArcaneBeam"), ("GUARD", "GuardianSpirit"), ("SANCT", "Sanctuary"),
                  ("GRACE", "MartyrsGrace")):
    F(abdefs, "public static final int %s = %d;" % (_n_, [a[0] for a in ABILS].index(_id_)))
F(abdefs, "public static final String[] SHAPES = %s;" % jarr(SHAPES))
F(abdefs, "public static final String[] SNAMES = %s;" % jarr([SHAPE_NAMES[a[0]][k] for a in ABILS for k in range(4)]))
F(abdefs, "public static final String[] DESCS = %s;" % jarr([ABIL_DESCS_[a[0]] for a in ABILS]))''')

COST_PY = r'''
# 0.1.18: Mana / Stamina / cooldown PER SHAPE (sh 0 walk, 1 sprint, 2 air, 3 crouch) - generated from SHAPE_POWER; Guardian Spirit = per save
def _cost_java(fn, kind):
    _l = ["public static double %s(int ai, int sh) {" % fn]
    for _id, _p, _cat, _pw in SHAPE_POWER:
        _i = [a[0] for a in ABILS].index(_id)
        _l.append("  if (ai == %d) { if (sh == 1) return @PKG@.AbilCfg.%s_%s_SP; if (sh == 2) return @PKG@.AbilCfg.%s_%s_AI; if (sh == 3) return @PKG@.AbilCfg.%s_%s_CR; return @PKG@.AbilCfg.%s_%s; }"
                  % (_i, _p, kind, _p, kind, _p, kind, _p, kind))
    if kind != "CD":
        _l.append("  if (ai == %d) return @PKG@.AbilCfg.GS_%s;" % ([a[0] for a in ABILS].index("GuardianSpirit"), kind))
    _l.append("  return 0.0;")
    _l.append("}")
    return "\n".join(_l)


M(abdefs, _cost_java("manaOf", "MANA"))
M(abdefs, _cost_java("stamOf", "STAM"))
M(abdefs, _cost_java("cdOf", "CD"))
M(abdefs, r"""
public static double mana(int ai, int sh) {
  return manaOf(ai, sh < 0 || sh > 3 ? 0 : sh);
}""")
M(abdefs, r"""
public static double stamina(int ai, int sh) {
  return stamOf(ai, sh < 0 || sh > 3 ? 0 : sh);
}""")
M(abdefs, r"""
public static long cdMs(int ai, int sh) {
  double s = cdOf(ai, sh < 0 || sh > 3 ? 0 : sh);
  if (!(s > 0.0)) return 0L;
  return Math.round(s * 1000.0);
}""")
M(abdefs, r"""
public static String sname(int ai, int sh) {
  if (ai < 0 || ai >= IDS.length) return "";
  int k = sh < 0 || sh > 3 ? 0 : sh;
  return SNAMES[ai * 4 + k];
}""")
M(abdefs, r"""
public static int shapeOf(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  for (int i = 0; i < SHAPES.length; i++) if (SHAPES[i].equals(t)) return i;
  if (t.equals("walking")) return 0;
  if (t.equals("run") || t.equals("sprinting")) return 1;
  if (t.equals("jump") || t.equals("midair") || t.equals("mid-air")) return 2;
  return -1;
}""")
M(abdefs, r"""
public static String slotText(int slot) {
  if (slot == 0) return "Primary 1 (/cast 1)";
  if (slot == 1) return "Primary 2 (/cast 2)";
  if (slot == 2) return "Alt 1 (crouch + /cast 1)";
  return "Alt 2 (crouch + /cast 2)";
}""")
'''
rep_method("abdefs", "public static double mana(int ai) {", r"""
public static double mana(int ai) {
  return mana(ai, 0);   // 0.1.18: the walking shape (the per-shape table is mana(ai, sh))
}""")
rep_method("abdefs", "public static double stamina(int ai) {", r"""
public static double stamina(int ai) {
  return stamina(ai, 0);
}""")
rep_method("abdefs", "public static long cdMs(int ai) {", r"""
public static long cdMs(int ai) {
  return cdMs(ai, 0);
}""")
# the per-shape methods go BEFORE the walking wrappers (methods before callers)
rep('''M(abdefs, r"""
public static double mana(int ai) {''', COST_PY + '''M(abdefs, r"""
public static double mana(int ai) {''')

# ================================================================================================ AbilMath: the pure 0.1.18 rules (bare-JVM tested)
MATH_PY = r'''
# 0.1.18 THE SHAPE RESOLVER (plan 3.2; pure). The key: 0 / 1 primaries, 2 / 3 the alts (/cast 3 | 4). In the air a primary key stays the
# primary (crouch in the air = movement, Skyy line 150); on the ground crouch moves it to the alt.
M(abmath, r"""
public static int resolveAt(int slot, boolean crouch, boolean air) {
  if (slot < 0 || slot > 3) return -1;
  if (air && slot < 2) return slot;
  return resolve(slot, crouch);
}""")
# the shape of the RESOLVED slot: an alt = crouch; a primary in the air = mid-air; sprinting = sprint; else walk. on = abil.shapes,
# so / ao = sprinting / mid-air shapes allowed (rows + the player's switches). Off = walk (an alt still casts - in its walking shape).
M(abmath, r"""
public static int shapeOf(int slot, boolean air, boolean sprint, boolean on, boolean so, boolean ao) {
  if (!on || slot < 0) return 0;
  if (slot >= 2) return 3;
  if (air && ao) return 2;
  if (sprint && so) return 1;
  return 0;
}""")
M(abmath, r"""
public static boolean airborne(boolean onGround, long since, long now, long minMs) {
  if (onGround || since <= 0L) return false;
  return now - since >= minMs;
}""")
# crouch counts once held minMs; a crouch AbilTick has not seen yet (since 0) counts (a typed /cast while crouched)
M(abmath, r"""
public static boolean crouchHeld(boolean crouching, long since, long now, long minMs) {
  if (!crouching) return false;
  if (since <= 0L) return true;
  return now - since >= minMs;
}""")
# Guardian Spirit: the saved player's next cooldown = base x 2^(saves - 1) (12, 24, 48 ...), at most 2^10
M(abmath, r"""
public static long guardCd(long baseMs, int saves) {
  if (baseMs <= 0L) return 0L;
  int n = saves < 1 ? 1 : saves;
  if (n > 11) n = 11;
  long m = 1L;
  for (int i = 1; i < n; i++) m = m * 2L;
  return baseMs * m;
}""")
# Arcane Beam: the multiplier at elapsed seconds - whole seconds k step from 'from' to 'to' over n = round(secs) steps (3 s: 1x 2x 3x)
M(abmath, r"""
public static double ramp(double elapsed, double secs, double from, double to) {
  long n = Math.round(secs);
  if (n < 1L) n = 1L;
  if (n == 1L) return to;
  double k = Math.floor(elapsed < 0.0 ? 0.0 : elapsed);
  if (k > (double) (n - 1L)) k = (double) (n - 1L);
  return from + (to - from) * k / (double) (n - 1L);
}""")
# Martyr's Grace: the k-th heal (0 = the first) in % of max Health, never below 0
M(abmath, r"""
public static double chainPct(int k, double first, double drop) {
  double p = first - drop * (double) k;
  return p > 0.0 ? p : 0.0;
}""")
# Frost Wake: the squared flat distance from (px, pz) to the segment a -> b
M(abmath, r"""
public static double segDist2(double px, double pz, double ax, double az, double bx, double bz) {
  double vx = bx - ax;
  double vz = bz - az;
  double l2 = vx * vx + vz * vz;
  double t = 0.0;
  if (l2 > 1.0E-9) t = ((px - ax) * vx + (pz - az) * vz) / l2;
  if (t < 0.0) t = 0.0;
  if (t > 1.0) t = 1.0;
  double dx = px - (ax + vx * t);
  double dz = pz - (az + vz * t);
  return dx * dx + dz * dz;
}""")
# Arcane Beam: {t along the unit ray d from o, the distance of p from the ray's line}
M(abmath, r"""
public static double[] rayDist(double ox, double oy, double oz, double dx, double dy, double dz, double px, double py, double pz) {
  double wx = px - ox;
  double wy = py - oy;
  double wz = pz - oz;
  double t = wx * dx + wy * dy + wz * dz;
  double cx = wx - dx * t;
  double cy = wy - dy * t;
  double cz = wz - dz * t;
  return new double[] { t, Math.sqrt(cx * cx + cy * cy + cz * cz) };
}""")
# the stunlock boss rule WITHOUT SkyyArmory's bridge: a word of the list is a WHOLE part of the role name split at _ (SkyyArmory Stun.bossRole,
# verbatim: Dragon matches Dragon_Fire, not Snapdragon)
M(abmath, r"""
public static boolean bossRole(String role, String words) {
  if (role == null || words == null) return false;
  String r = "_" + role.trim().toLowerCase() + "_";
  String[] ws = words.split(",");
  for (int i = 0; i < ws.length; i++) {
    String w = ws[i].trim().toLowerCase();
    if (w.length() > 0 && r.indexOf("_" + w + "_") >= 0) return true;
  }
  return false;
}""")
# Starfall: star i of n on a disc of radius r - a sunflower spread (deterministic, even cover, every star inside r)
M(abmath, r"""
public static double[] disc(int i, int n, double r) {
  if (n < 1 || !(r > 0.0)) return new double[] { 0.0, 0.0 };
  double a = 2.399963229728653 * (double) i;
  double d = r * Math.sqrt(((double) i + 0.5) / (double) n);
  return new double[] { Math.cos(a) * d, Math.sin(a) * d };
}""")
'''
rep('''# the rim points of a ring of radius r: one about every 2 blocks of its edge, 6 - 16''', MATH_PY.strip("\n") + '''
# the rim points of a ring of radius r: one about every 2 blocks of its edge, 6 - 16''')

# ================================================================================================ AbilStore / AbilJob / AbilZone / AbilWorld
rep('''           "WANT", "SAMPLE"):   # 0.1.17: UUID -> Long the HUD last asked (class:fn:abil); UUID -> double[] {Mana, Stamina, crouch, creative, at}''',
    '''           "WANT", "SAMPLE",    # 0.1.17: UUID -> Long the HUD last asked (class:fn:abil); UUID -> double[] {Mana, Stamina, crouch, creative, at}
           "MOVE", "GUARD", "CHAN", "FROZEN"):   # 0.1.18: UUID -> long[] {crouch since, air since}; UUID -> long[] {saves, next save at, last hurt};
                                                  # UUID -> the running beam (AbilJob); mob Ref -> long[] {a hit breaks it from, frozen until}''')
rep('''           "public double[] done;", "public double[] cap;", "public int left;", "public long every;", "public int hits;", "public String name;",
           "public String pkey;"):   # FIX ROUND: + pkey = the caster's profile at the cast''',
    '''           "public double[] done;", "public double[] cap;", "public int left;", "public long every;", "public int hits;", "public String name;",
           "public String pkey;",    # FIX ROUND: + pkey = the caster's profile at the cast
           # 0.1.18: kind 3 = wait for the landing (ai, sh, until), 5 = a star shower (total, sh 1 = follows the caster, width = star size),
           # 6 = the Arcane Beam channel (start, until, secs, len, width, from, to, sh 1 sweep / 2 down, name = the weapon), 7 = a 1 s channel
           # (Kneel / Martyr's Vow: x y z = where it started, paidMana / paidStam for the refund), 8 = a Frost Nova (freeze, brk, chill)
           "public int ai;", "public int sh;", "public long until;", "public long start;", "public int total;", "public double secs;",
           "public double len;", "public double width;", "public double from;", "public double to;", "public double paidMana;",
           "public double paidStam;", "public double freeze;", "public double brk;", "public double chill;",
           "public double brkAmt;"):   # FIX 2: brkAmt = Frost Nova's break damage (ab.FrostNova.breakPower x staff hit)''')
rep('''           "public double hpMax;", "public double absorbed;", "public double cap;", "public double ratio;", "public double manaPaid;",
           "public int pulsesDue;", "public int pulsesDone;", "public boolean ended;", "public String why;", "public double xpOthers;",
           "public double xpSelf;", "public java.util.HashMap healed;"):''',
    '''           "public double hpMax;", "public double absorbed;", "public double cap;", "public double ratio;", "public double manaPaid;",
           "public int pulsesDue;", "public int pulsesDone;", "public boolean ended;", "public String why;", "public double xpOthers;",
           "public double xpSelf;", "public java.util.HashMap healed;",
           # 0.1.18: kind 3 = Frost Wake (the strip x z -> x2 z2, r = half its width), 4 = Running Blessing (follows the caster), 5 = Sanctuary
           # (pct heal %/s, cut damage %); shape = the shape it was cast in; hit = the mobs / players it already took
           "public double x2;", "public double z2;", "public double amount;", "public double freeze;", "public double pct;", "public double cut;",
           "public int shape;", "public long nextHeal;", "public int hits;", "public java.util.HashSet hit;",
           "public double brkAmt;"):   # FIX 2: Frost Wake's break damage''')
rep('''  int ended = 0;
  while (true) {
    int mine = 0;
    @PKG@.AbilZone oldest = null;
    for (int i = 0; i < this.zones.size(); i++) {
      @PKG@.AbilZone o = (@PKG@.AbilZone) this.zones.get(i);
      if (o.ended || o.caster == null || !o.caster.equals(z.caster)) continue;''', '''  int ended = 0;
  if (z.kind == 3 || z.kind == 4) { this.zones.add(z); this.nz = this.zones.size(); return 0; }   // 0.1.18: short effects never count
  while (true) {
    int mine = 0;
    @PKG@.AbilZone oldest = null;
    for (int i = 0; i < this.zones.size(); i++) {
      @PKG@.AbilZone o = (@PKG@.AbilZone) this.zones.get(i);
      if (o.ended || o.caster == null || !o.caster.equals(z.caster)) continue;
      if (o.kind == 3 || o.kind == 4) continue;   // 0.1.18: Frost Wake / Running Blessing are not placed zones''')

# ================================================================================================ Abil: seams + constants
rep('''           "public static volatile java.util.List SOUNDS = null;",               # HARNESS SEAM ONLY (null): every sound id played''',
    '''           "public static volatile java.util.List SOUNDS = null;",               # HARNESS SEAM ONLY (null): every sound id played
           "public static volatile java.util.function.Function LOOK = null;",    # 0.1.18 HARNESS SEAM ONLY (null = TargetUtil.getLook): Ref -> double[6]
           "public static volatile java.util.function.Function EFFECT = null;",  # 0.1.18 HARNESS SEAM ONLY (null = EffectControllerComponent)
           "public static volatile java.util.function.Function TARGET = null;",  # 0.1.18 HARNESS SEAM ONLY (null = TargetUtil.getTargetEntity): Ref -> UUID
           "public static volatile java.util.List EFFECTS = null;",              # 0.1.18 HARNESS SEAM ONLY (null): every effect put / taken off
           "public static volatile boolean STUN_WARNED = false;",                # 0.1.18: the missing armory:fn:stunhit is said once
           "public static volatile long SAVES = 0L;",                            # 0.1.18: Guardian Spirit saves since the start
           "public static volatile String LAST_GUARD = \\"\\";",                  # 0.1.18: the last Guardian Spirit outcome (harness + info)''')
rep('''F(abil, "public static final String SND_FAIL = %s;" % jstr(SND_FAIL))   # FIX ROUND: the refusal fail sound (vanilla)''',
    '''F(abil, "public static final String SND_FAIL = %s;" % jstr(SND_FAIL))   # FIX ROUND: the refusal fail sound (vanilla)
F(abil, "public static final String EF_FREEZE = %s;" % jstr(EF_FREEZE))   # 0.1.18: Frost Nova's freeze (vanilla Freeze: movement off)
F(abil, "public static final String EF_SLOW = %s;" % jstr(EF_SLOW))       # 0.1.18: the Chill (vanilla Slow)
F(abil, "public static final String EF_STUN = %s;" % jstr(EF_STUN))       # FIX ROUND: under the Freeze, attacks off (vanilla Stun, abil.freezeStun)''')

# ================================================================================================ the methods that move below the new helpers
OLD_RUNJOB = cut_method("abil", "public static boolean runJob(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {")
OLD_ZONETICK = cut_method("abil", "public static boolean zoneTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {")
OLD_SHIELD = cut_method("abil", "public static String shield(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {")
OLD_CASTNOW = cut_method("abil", "public static String castNow(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {")
OLD_CAST = cut_method("abil", "public static String cast(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {")
assert "meteorImpact(j, st, cb); return false;" in OLD_RUNJOB and "if (z.kind == 1 && !z.ended) {" in OLD_ZONETICK
assert "String r = castNow(pr, st, ref, w, arg);" in OLD_CAST

# zoneTick: the 0.1.18 kinds (3 Frost Wake, 4 Running Blessing, 5 Sanctuary) go to zoneTick2; kinds 1 / 2 exactly as 0.1.17
NEW_ZONETICK = OLD_ZONETICK.replace('''public static boolean zoneTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 1 && !z.ended) {''', '''public static boolean zoneTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind >= 3) return zoneTick2(z, st, cb, now);   // 0.1.18
  if (z.kind == 1 && !z.ended) {''')
assert NEW_ZONETICK != OLD_ZONETICK
# shield: SANCTUARY first (you and your party inside take cut % less: any damage but out-of-world / command), then the bubble, the barrier
_SH_A = '''  @PKG@.AbilZone[] zs = aw.zoneArr();
  double amt = (double) amt0;
  String out = "";
'''
assert OLD_SHIELD.count(_SH_A) == 1
NEW_SHIELD = OLD_SHIELD.replace(_SH_A, _SH_A + '''  double cutBest = 0.0;   // 0.1.18: Sanctuary (the strongest one covering you, cast by you or a party member)
  for (int i = 0; i < zs.length; i++) {
    @PKG@.AbilZone z = zs[i];
    if (z.kind != 5 || z.ended || now >= z.until) continue;
    if (!@PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, z.r)) continue;
    if (!u.equals(z.caster) && !@PKG@.HealTask.inParty(z.caster, u)) continue;
    if (z.cut > cutBest) cutBest = z.cut;
  }
  if (cutBest > 0.0) {
    double c0 = amt * cutBest / 100.0;
    amt = amt - c0;
    out = "sanct:" + @PKG@.AbilMath.fmt(c0);
  }
''')
NEW_SHIELD = NEW_SHIELD.replace('''      out = "bubble:" + @PKG@.AbilMath.fmt(take);''', '''      out = out + (out.length() > 0 ? " " : "") + "bubble:" + @PKG@.AbilMath.fmt(take);''')
assert NEW_SHIELD.count("sanct:") == 1 and NEW_SHIELD.count('"bubble:"') == 1

ABIL_018 = r'''
# =====================================================================================================================
# 0.1.18 THE NEW ABILITY CODE (shapes, Frost Nova, Guardian Spirit, Starfall, Arcane Beam, Sanctuary, Martyr's Grace). Every method a moved
# 0.1.17 method (runJob, zoneTick, shield, castNow, cast) now calls comes first. World thread throughout (commands + AbilTick + the damage
# systems).
# =====================================================================================================================
# ---- the movement read at the press (plan 3.2): MovementStates now + when crouch went on / the feet left the ground (AbilTick tracks it)
# FIX ROUND (critic): "mid-air" = the feet off the ground AND not swimming / in a fluid / creative-flying / climbing / riding / mantling /
# sitting (each of those reports onGround false but is not a jump). Gliding stays mid-air on purpose (you are falling and will land).
M(abil, r"""
public static boolean groundLike(@MST@ m) {
  if (m == null) return true;
  return m.onGround || m.flying || m.swimming || m.inFluid || m.climbing || m.mounting || m.mantling || m.sitting;
}""")
M(abil, r"""
public static boolean onGround(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    if (!(o instanceof @MSC@)) return true;
    @MST@ m = ((@MSC@) o).getMovementStates();
    return groundLike(m);
  } catch (Throwable t) { return true; }
}""")
M(abil, r"""
public static boolean sprinting(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    if (!(o instanceof @MSC@)) return false;
    @MST@ m = ((@MSC@) o).getMovementStates();
    return m != null && m.sprinting;
  } catch (Throwable t) { return false; }
}""")
M(abil, r"""
public static long[] moveOf(java.util.UUID u) {
  if (u == null) return null;
  Object o = @PKG@.AbilStore.MOVE.get(u);
  if (o instanceof long[]) return (long[]) o;
  return null;
}""")
M(abil, r"""
public static boolean airNow(@CAC@ acc, @REF@ r, java.util.UUID u, long now) {
  long[] s = moveOf(u);
  return @PKG@.AbilMath.airborne(onGround(acc, r), s == null ? 0L : s[1], now, Math.round(@PKG@.AbilCfg.AIR_MIN * 1000.0));
}""")
M(abil, r"""
public static boolean crouchNow(java.util.UUID u, long now) {
  long[] s = moveOf(u);
  return @PKG@.AbilMath.crouchHeld(true, s == null ? 0L : s[0], now, Math.round(@PKG@.AbilCfg.CROUCH_MIN * 1000.0));
}""")
# AbilTick, every player every world tick: a record only while crouching or airborne (no allocation for a player standing on the ground)
M(abil, r"""
public static void track(@REF@ r, @CAC@ acc, long now) {
  try {
    if (r == null || !@PKG@.AbilCfg.PART) return;
    Object po = acc.getComponent(r, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return;
    java.util.UUID u = ((@PR@) po).getUuid();
    if (u == null) return;
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    if (!(o instanceof @MSC@)) return;
    @MST@ m = ((@MSC@) o).getMovementStates();
    if (m == null) return;
    boolean cr = m.crouching;
    boolean air = !groundLike(m);
    long[] s = moveOf(u);
    if (s == null) {
      if (!cr && !air) return;
      s = new long[] { 0L, 0L };
      @PKG@.AbilStore.MOVE.put(u, s);
    }
    if (cr) { if (s[0] == 0L) s[0] = now; }
    else s[0] = 0L;
    if (air) { if (s[1] == 0L) s[1] = now; }
    else s[1] = 0L;
  } catch (Throwable t) { }
}""")
# ---- where: the look (eye + unit direction), a spot ahead on the flat, the feet
M(abil, r"""
public static double[] look(@CAC@ acc, @REF@ r) {
  try {
    java.util.function.Function f = LOOK;
    if (f != null) {
      Object o = f.apply(r);
      if (o instanceof double[] && ((double[]) o).length >= 6) return (double[]) o;
      return null;
    }
    @XFM@ lk = @TU@.getLook(r, acc);
    if (lk == null) return null;
    @VEC@ p = lk.getPosition();
    @VEC@ d = lk.getDirection();
    if (p == null || d == null) return null;
    double l = Math.sqrt(d.x * d.x + d.y * d.y + d.z * d.z);
    if (!(l > 1.0E-6) || Double.isNaN(l) || Double.isInfinite(l)) return null;
    return new double[] { p.x, p.y, p.z, d.x / l, d.y / l, d.z / l };
  } catch (Throwable t) { return null; }
}""")
M(abil, r"""
public static double[] flat(@CAC@ acc, @REF@ r) {
  double[] lk = look(acc, r);
  if (lk == null) return null;
  double h = Math.sqrt(lk[3] * lk[3] + lk[5] * lk[5]);
  if (!(h > 1.0E-4)) return null;
  return new double[] { lk[3] / h, lk[5] / h };
}""")
M(abil, r"""
public static double[] here(@CAC@ acc, @REF@ r) {
  @VEC@ p = pos(acc, r);
  if (p == null) return null;
  return new double[] { p.x, p.y, p.z };
}""")
# dist blocks ahead along the look on the flat (no look = your feet)
M(abil, r"""
public static double[] ahead(@CAC@ acc, @REF@ r, double dist) {
  @VEC@ p = pos(acc, r);
  if (p == null) return null;
  double[] f = flat(acc, r);
  if (f == null) return new double[] { p.x, p.y, p.z };
  return new double[] { p.x + f[0] * dist, p.y, p.z + f[1] * dist };
}""")
M(abil, r"""
public static @REF@ casterRef(@CB@ cb, java.util.UUID u) {
  try { return ((@ES@) cb.getExternalData()).getRefFromUUID(u); } catch (Throwable t) { return null; }
}""")
# a job / zone still belongs to a caster who is here, alive and on the profile that cast it
M(abil, r"""
public static boolean live(@CAC@ acc, @REF@ cr, java.util.UUID u, String pkey) {
  if (cr == null || !cr.isValid() || !alive(acc, cr)) return false;
  return pkey == null || pkey.equals(@PKG@.ClassCfg.pkey(u));
}""")
M(abil, r"""
public static @PR@ prOf(java.util.UUID u) {
  try { return u == null ? null : @UNI@.get().getPlayer(u); } catch (Throwable t) { return null; }
}""")
# ---- the vanilla effects (Freeze / Slow) + THE STUN-CLOCK BRIDGE (armory:fn:stunhit - a later SkyyArmory; until then bosses are only chilled)
M(abil, r"""
public static boolean effect(@CAC@ acc, @REF@ t, String id, double secs) {
  java.util.List l = EFFECTS;
  if (l != null) l.add(id + ":" + @PKG@.AbilMath.fmt(secs));
  try {
    if (t == null || !(secs > 0.0)) return false;
    java.util.function.Function f = EFFECT;
    if (f != null) {
      Object o = f.apply(new Object[] { t, id, Double.valueOf(secs) });
      return o instanceof Boolean && ((Boolean) o).booleanValue();
    }
    if (!t.isValid()) return false;
    Object co = acc.getComponent(t, @ECC@.getComponentType());
    Object fx = @EFX@.getAssetMap().getAsset(id);
    if (!(co instanceof @ECC@) || !(fx instanceof @EFX@)) return false;
    return ((@ECC@) co).addEffect(t, (@EFX@) fx, (float) secs, @OVB@.OVERWRITE, acc);
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("ability effect " + id + " failed: " + x); return false; }
}""")
M(abil, r"""
public static boolean unfreezeOne(@CAC@ acc, @REF@ t, String id) {
  java.util.List l = EFFECTS;
  if (l != null) l.add("-" + id);
  try {
    if (EFFECT != null) return true;
    if (t == null || !t.isValid()) return false;
    Object co = acc.getComponent(t, @ECC@.getComponentType());
    int i = @EFX@.getAssetMap().getIndex(id);
    if (!(co instanceof @ECC@) || i < 0 || !((@ECC@) co).hasEffect(i)) return false;
    ((@ECC@) co).removeEffect(t, i, acc);
    return true;
  } catch (Throwable x) { return false; }
}""")
# FIX 2: does the mob carry this vanilla effect now (the harness: EFFECT answers "?<id>" - not logged in EFFECTS)
M(abil, r"""
public static boolean hasFx(@CAC@ acc, @REF@ t, String id) {
  try {
    java.util.function.Function f = EFFECT;
    if (f != null) {
      Object o = f.apply(new Object[] { t, "?" + id, Double.valueOf(0.0) });
      return o instanceof Boolean && ((Boolean) o).booleanValue();
    }
    if (t == null || !t.isValid()) return false;
    Object co = acc.getComponent(t, @ECC@.getComponentType());
    int i = @EFX@.getAssetMap().getIndex(id);
    return co instanceof @ECC@ && i >= 0 && ((@ECC@) co).hasEffect(i);
  } catch (Throwable x) { return false; }
}""")
# FIX 2: a break takes the Freeze off, and the Stun ONLY when this freeze put it on (stun = false: another mod's Stun - a Monk's stunlock -
# was already running, so it is left alone)
M(abil, r"""
public static boolean unfreeze(@CAC@ acc, @REF@ t, boolean stun) {
  boolean a = unfreezeOne(acc, t, EF_FREEZE);
  boolean b = stun && unfreezeOne(acc, t, EF_STUN);
  return a || b;
}""")
M(abil, r"""
public static boolean unfreeze(@CAC@ acc, @REF@ t) {
  return unfreeze(acc, t, true);
}""")
M(abil, r"""
public static String roleOf(@CAC@ acc, @REF@ t) {
  try {
    Object no = acc.getComponent(t, @NPC@.getComponentType());
    return no instanceof @NPC@ ? ((@NPC@) no).getRoleName() : null;
  } catch (Throwable x) { return null; }
}""")
# -1 = not a boss, 0 = its breakout window (do not freeze; without the bridge: every abil.bossWords boss), >0 = freeze at most this many ms
M(abil, r"""
public static long stunClock(@REF@ t, java.util.UUID u, String role, long holdMs) {
  try {
    Object f = @PKG@.ClassCfg.bridge().get("armory:fn:stunhit");
    if (!(f instanceof java.util.function.Function)) {
      if (!STUN_WARNED) {
        STUN_WARNED = true;
        @PKG@.ClassCfg.info("armory:fn:stunhit is not there (SkyyArmory does not share its stunlock clock yet) - Frost Nova only CHILLS bosses (abil.bossWords), it never freezes them");   // FIX 2: INFO (expected until SkyyArmory ships it), not a WARN every start
      }
      return @PKG@.AbilMath.bossRole(role, @PKG@.AbilCfg.BOSS_WORDS) ? 0L : -1L;
    }
    Object r = null;
    try { r = ((java.util.function.Function) f).apply(new Object[] { t, u, role, Long.valueOf(holdMs) }); }
    catch (Throwable y) { r = null; @PKG@.ClassCfg.warnLimited("armory:fn:stunhit failed (" + y + ") - this freeze uses abil.bossWords instead"); }
    if (r instanceof Number) return ((Number) r).longValue();
    if (r != null) @PKG@.ClassCfg.warnLimited("armory:fn:stunhit answered " + r.getClass().getName() + ", not a number - this freeze uses abil.bossWords instead");
    return @PKG@.AbilMath.bossRole(role, @PKG@.AbilCfg.BOSS_WORDS) ? 0L : -1L;   // FIX ROUND: fail CLOSED - a boss is only chilled
  } catch (Throwable x) { return @PKG@.AbilMath.bossRole(role, @PKG@.AbilCfg.BOSS_WORDS) ? 0L : -1L; }
}""")
M(abil, r"""
public static void pruneFrozen(long now) {
  java.util.Iterator it = @PKG@.AbilStore.FROZEN.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = @PKG@.AbilStore.FROZEN.get(k);
    if (!(v instanceof long[]) || ((long[]) v)[1] <= now) it.remove();
  }
}""")
# freeze one mob (secs), a hit breaks it after brk s, then Chill: 1 = frozen, 2 = frozen for less (the boss clock cut it), 0 = only chilled
# (a boss in its breakout window), -1 = the effect failed. FROZEN[t] = long[] { break from, ends, 1 = this freeze put the Stun on, caster
# UUID msb, lsb, break damage x 1000 } (FIX 2: a Stun another mod put on - a Monk's stunlock - is never overwritten or taken off)
M(abil, r"""
public static int freezeOne(@CAC@ acc, @REF@ t, java.util.UUID u, double secs, double brk, double chill, long now, double brkAmt) {
  long hold = Math.round(secs * 1000.0);
  long c = stunClock(t, u, roleOf(acc, t), hold);
  if (c == 0L) {
    if (secs + chill > 0.0) effect(acc, t, EF_SLOW, secs + chill);
    return 0;
  }
  boolean cut = c > 0L && c < hold;
  if (cut) hold = c;
  boolean stun = false;
  if (@PKG@.AbilCfg.FREEZE_STUN) {
    Object po = @PKG@.AbilStore.FROZEN.get(t);
    boolean ours = po instanceof long[] && ((long[]) po).length > 2 && ((long[]) po)[2] == 1L && ((long[]) po)[1] > now;
    if (ours || !hasFx(acc, t, EF_STUN)) { effect(acc, t, EF_STUN, (double) hold / 1000.0); stun = true; }
  }
  boolean ok = effect(acc, t, EF_FREEZE, (double) hold / 1000.0);
  if (chill > 0.0) effect(acc, t, EF_SLOW, (double) hold / 1000.0 + chill);
  if (!ok) return -1;
  long ms = u == null ? 0L : u.getMostSignificantBits();
  long ls = u == null ? 0L : u.getLeastSignificantBits();
  long bd = brkAmt > 0.0 && u != null ? Math.round(brkAmt * 1000.0) : 0L;
  @PKG@.AbilStore.FROZEN.put(t, new long[] { now + Math.round(brk * 1000.0), now + hold, stun ? 1L : 0L, ms, ls, bd });
  if (@PKG@.AbilStore.FROZEN.size() > 512) pruneFrozen(now);
  return cut ? 2 : 1;
}""")
M(abil, r"""
public static int freezeOne(@CAC@ acc, @REF@ t, java.util.UUID u, double secs, double brk, double chill, long now) {
  return freezeOne(acc, t, u, secs, brk, chill, now, 0.0);
}""")
# FIX 2 (critic: spec draft 2.3 "a hit breaks it after 1 s: 0.5 H"): the break damage, through the whole pipeline as a "FrostNova" hit
# (frostHit ignores those - no loop); only while the caster is online in the mob's world
M(abil, r"""
public static boolean breakHit(@CAC@ acc, @REF@ t, long[] f) {
  try {
    if (f == null || f.length < 6 || f[5] <= 0L || !(acc instanceof @CB@)) return false;
    java.util.UUID cu = new java.util.UUID(f[3], f[4]);
    @PR@ cp = prOf(cu);
    if (cp == null) return false;
    @REF@ cr = cp.getReference();
    if (cr == null || !cr.isValid() || t == null || !t.isValid() || cr.getStore() != t.getStore()) return false;
    return hit((@CB@) acc, t, cr, cu, (double) f[5] / 1000.0, "FrostNova");
  } catch (Throwable x) { return false; }
}""")
# AbilFrostSys (the Inspect group: the hit landed): a hit on a frozen mob after its break time ends the freeze (not the nova's own hit)
M(abil, r"""
public static String frostHit(@CAC@ acc, @REF@ t, @DMG@ d, long now) {
  if (t == null || d == null) return null;
  Object o = @PKG@.AbilStore.FROZEN.get(t);
  if (!(o instanceof long[])) return null;
  long[] f = (long[]) o;
  if (now >= f[1]) { @PKG@.AbilStore.FROZEN.remove(t); return "over"; }
  if (d.isCancelled() || !(d.getAmount() > 0.0f)) return null;
  if ("FrostNova".equals(@PKG@.AbilDmg.whatOf(d))) return "own";
  if (now < f[0]) return "held";
  @PKG@.AbilStore.FROZEN.remove(t);
  unfreeze(acc, t, f.length < 3 || f[2] == 1L);
  @VEC@ q = pos(acc, t);
  if (q != null) particle(FX_FROST_HIT, q.x, q.y + 1.0, q.z, acc);
  return breakHit(acc, t, f) ? "broken+hit" : "broken";
}""")
# ---- FROST NOVA: the burst (job kind 8, AbilTick: damage needs the CommandBuffer); j.r = radius, amount = damage, freeze / brk / chill
M(abil, r"""
public static int nova(@PKG@.AbilJob j, @CB@ cb, @REF@ cr, long now) {
  particle(FX_FROST, j.x, j.y + 0.5, j.z, cb);
  java.util.List l = near(cb, j.x, j.y, j.z, j.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t)) continue;
    if (!enemy(cb, t, cr)) continue;
    if (j.amount > 0.0) hit(cb, t, cr, j.caster, j.amount, "FrostNova");
    freezeOne(cb, t, j.caster, j.freeze, j.brk, j.chill, now, j.brkAmt);
    @VEC@ q = pos(cb, t);
    if (q != null) particle(FX_FROST_HIT, q.x, q.y + 1.0, q.z, cb);
    n++;
  }
  j.hits = n;
  return n;
}""")
M(abil, r"""
public static @PKG@.AbilJob novaJob(java.util.UUID u, String pkey, double[] at, double r, double amount, double freeze, double brk, double chill, long now, int sh) {
  @PKG@.AbilJob j = new @PKG@.AbilJob(8, now, u, "FrostNova", at[0], at[1], at[2], r, amount);
  j.pkey = pkey;
  j.freeze = freeze;
  j.brk = brk;
  j.chill = chill;
  j.sh = sh;
  j.ai = @PKG@.AbilDefs.FROST;
  return j;
}""")
M(abil, r"""
public static int novaRun(@PKG@.AbilJob j, @CB@ cb, @REF@ cr, long now) {
  int n = nova(j, cb, cr, now);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.FROST, j.sh) + (n == 0 ? " froze nothing." : " froze " + n + (n == 1 ? " enemy" : " enemies") + " for " + @PKG@.AbilMath.fmt(j.freeze) + " s."));
  return n;
}""")
# ---- placed zones of every shape (from a command: acc = the Store; from AbilTick on a landing: acc = the CommandBuffer)
M(abil, r"""
public static @PKG@.AbilZone barrierAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, double[] at, long now, double r, double secs, double ratio, int sh) {
  double mh = max(map(acc, ref), @DST@.getHealth());
  if (!(mh > 0.0)) mh = 100.0;
  long life = Math.round(secs * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(1, u, at[0], at[1], at[2], r, now, now + life);
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.ratio = ratio;
  z.cap = mh * (double) @PKG@.AbilCfg.B_MAX / 100.0;
  z.shape = sh;
  ring(FX_BARRIER, z, acc);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.MANAB, sh) + ": a dome of " + @PKG@.AbilMath.fmt(z.r) + " blocks for " + @PKG@.AbilMath.secs(life) + " s - damage to you inside costs Mana (" + @PKG@.AbilMath.fmt(z.ratio) + " per Mana) instead of Health.");
  aw.addZone(z);   // last
  return z;
}""")
M(abil, r"""
public static @PKG@.AbilZone bubbleAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, double[] at, long now, double r, long hpPct, int sh) {
  double mh = max(map(acc, ref), @DST@.getHealth());
  if (!(mh > 0.0)) mh = 100.0;
  long life = Math.round(@PKG@.AbilCfg.U_TIME * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(2, u, at[0], at[1], at[2], r, now, now + life);
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.hpMax = mh * (double) hpPct / 100.0;
  z.hp = z.hpMax;
  z.shape = sh;
  particle(FX_BUBBLE_ON, at[0], at[1] + 1.0, at[2], acc);
  ring(FX_BUBBLE, z, acc);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.BUBBLE, sh) + ": " + @PKG@.AbilMath.fmt(z.hpMax) + " HP for " + @PKG@.AbilMath.secs(life) + " s - it soaks attacks on you and your party inside and heals at 75 / 50 / 25 % and when it breaks.");
  aw.addZone(z);   // last
  return z;
}""")
M(abil, r"""
public static @PKG@.AbilZone sanctAt(@PR@ pr, @CAC@ acc, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, double[] at, long now, double r, double secs, long pct, long cut, int sh) {
  long life = Math.round(secs * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(5, u, at[0], at[1], at[2], r, now, now + life);
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.pct = (double) pct;
  z.cut = (double) cut;
  z.shape = sh;
  z.nextHeal = now + 1000L;
  ring(FX_HOLY, z, acc);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SANCT, sh) + ": " + @PKG@.AbilMath.fmt(z.r) + " blocks for " + @PKG@.AbilMath.secs(life) + " s - you and your party inside heal " + pct + " % a second and take " + cut + " % less damage.");
  aw.addZone(z);   // last
  return z;
}""")
# FROST WAKE: a 2 x 8 strip from your feet back along your run (r = half its width); RUNNING BLESSING: a circle on you for blessTime s
M(abil, r"""
public static @PKG@.AbilZone wakeAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, double amount, long now) {
  @VEC@ p = pos(acc, ref);
  double[] f = flat(acc, ref);
  if (f == null) f = new double[] { 0.0, 1.0 };
  double len = @PKG@.AbilCfg.F_WAKE_L;
  long life = Math.round(@PKG@.AbilCfg.F_WAKE_T * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(3, u, p.x, p.y, p.z, @PKG@.AbilCfg.F_WAKE_W / 2.0, now, now + life);
  z.x2 = p.x - f[0] * len;
  z.z2 = p.z - f[1] * len;
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.amount = amount;
  z.freeze = @PKG@.AbilCfg.F_WAKE_F;
  z.shape = 1;
  z.hit = new java.util.HashSet();
  z.nextFx = now;
  if (pr != null) say(pr, "Frost Wake: a freezing strip " + @PKG@.AbilMath.fmt(len) + " blocks behind you for " + @PKG@.AbilMath.secs(life) + " s.");
  aw.addZone(z);   // last
  return z;
}""")
M(abil, r"""
public static @PKG@.AbilZone blessAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, long now) {
  @VEC@ p = pos(acc, ref);
  long life = Math.round(@PKG@.AbilCfg.S_BLESS_T * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(4, u, p.x, p.y, p.z, @PKG@.AbilCfg.S_BLESS_R, now, now + life);
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.shape = 1;
  z.hit = new java.util.HashSet();
  z.nextFx = now;
  if (pr != null) say(pr, "Running Blessing: a circle of " + @PKG@.AbilMath.fmt(z.r) + " blocks follows you for " + @PKG@.AbilMath.secs(life) + " s - everyone it touches is healed once.");
  aw.addZone(z);   // last
  return z;
}""")
M(abil, r"""
public static int wakeTick(@PKG@.AbilZone z, @CB@ cb, @REF@ cr, long now) {
  double mx = (z.x + z.x2) / 2.0;
  double mz = (z.z + z.z2) / 2.0;
  double half = Math.sqrt((z.x2 - z.x) * (z.x2 - z.x) + (z.z2 - z.z) * (z.z2 - z.z)) / 2.0;
  java.util.List l = near(cb, mx, z.y, mz, half + z.r + 1.0);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (z.hit.contains(t)) continue;
    if (!enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null || Math.abs(q.y - z.y) > 3.0) continue;
    if (@PKG@.AbilMath.segDist2(q.x, q.z, z.x, z.z, z.x2, z.z2) > z.r * z.r) continue;
    z.hit.add(t);
    if (z.amount > 0.0) hit(cb, t, cr, z.caster, z.amount, "FrostNova");
    freezeOne(cb, t, z.caster, z.freeze, @PKG@.AbilCfg.F_BREAK, @PKG@.AbilCfg.F_CHILL, now, z.brkAmt);
    particle(FX_FROST_HIT, q.x, q.y + 1.0, q.z, cb);
    n++;
  }
  z.hits = z.hits + n;
  return n;
}""")
M(abil, r"""
public static void wakeFx(@PKG@.AbilZone z, @CAC@ acc) {
  for (int i = 0; i <= 4; i++) {
    double f = (double) i / 4.0;
    particle(FX_FROST_HIT, z.x + (z.x2 - z.x) * f, z.y + 0.2, z.z + (z.z2 - z.z) * f, acc);
  }
}""")
# one heal-over-time job for one player (the Sacred Heal shape of healCast's job): per = want x hot % / ticks; done = what the instant took
M(abil, r"""
public static @PKG@.AbilJob hotJob(java.util.UUID u, String pkey, String healer, java.util.UUID t, double want, double got, double cap, double hotPct, double x, double y, double z, double r, long now) {
  int ticks = @PKG@.AbilMath.ticks(@PKG@.AbilCfg.S_HOT_TIME);
  if (ticks <= 0 || !(hotPct > 0.0) || !(want > 0.01)) return null;
  long every = Math.round(@PKG@.AbilCfg.S_HOT_TIME * 1000.0 / (double) ticks);
  if (every < 50L) every = 50L;
  @PKG@.AbilJob h = new @PKG@.AbilJob(2, now + every, u, "SacredHeal", x, y, z, r, 0.0);
  h.targets = new java.util.UUID[] { t };
  h.per = new double[] { want * hotPct / 100.0 / (double) ticks };
  h.done = new double[] { got };
  h.cap = new double[] { cap };
  h.left = ticks;
  h.every = every;
  h.name = healer;
  h.pkey = pkey;
  return h;
}""")
M(abil, r"""
public static int blessTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  inside(st, cb, z, us, rs);
  boolean xp = xpOk(z, st, cb);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  double others = 0.0;
  double self = 0.0;
  int n = 0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    if (z.hit.contains(t)) continue;
    if (!healable(cb, r)) continue;
    z.hit.add(t);
    double mx = max(map(cb, r), @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(z.caster);
    boolean party = isSelf || @PKG@.HealTask.inParty(z.caster, t);
    double want = @PKG@.HealTask.split(@PKG@.AbilMath.heal(mx, @PKG@.AbilCfg.S_BLESS_H, isSelf, @PKG@.AbilCfg.S_SELF), party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    double cap = @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, 0.0);
    double got = apply(cb, r, want, cap);
    @PKG@.AbilJob h = hotJob(z.caster, z.pkey, z.name, t, want, got, cap, (double) @PKG@.AbilCfg.S_HOT, z.x, z.y, z.z, z.r, now);
    if (h != null && aw != null) aw.add(h);
    n++;
    @VEC@ q = pos(cb, r);
    if (q != null) particle(FX_HEAL, q.x, q.y + 1.0, q.z, cb);
    if (!(got > 0.0)) continue;
    z.absorbed = z.absorbed + got;
    if (isSelf) { self = self + got; @PKG@.HealMsg.given(z.caster, z.caster, got); }
    else { others = others + got; @PKG@.HealMsg.given(z.caster, t, got); @PKG@.HealMsg.taken(t, z.caster, z.name, got); }
  }
  if (xp) {
    if (others > 0.0) @PKG@.HealTask.xp(z.caster, others);
    if (self > 0.0) @PKG@.HealTask.xpSelf(z.caster, self);
  }
  z.hits = z.hits + n;
  return n;
}""")
# one Sanctuary pulse (1 Hz): pct % of max Health to you + party (others the othersPercent share), the abil.healCap per target per zone
M(abil, r"""
public static double sanctPulse(@PKG@.AbilZone z, @ST@ st, @CB@ cb, boolean xp) {
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  inside(st, cb, z, us, rs);
  double others = 0.0;
  double self = 0.0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    if (!healable(cb, r)) continue;
    double mx = max(map(cb, r), @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(z.caster);
    boolean party = isSelf || @PKG@.HealTask.inParty(z.caster, t);
    double want = @PKG@.HealTask.split(mx * z.pct / 100.0, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    Object dn = z.healed.get(t);
    double done = dn instanceof Double ? ((Double) dn).doubleValue() : 0.0;
    double got = apply(cb, r, want, @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, done));
    if (!(got > 0.0)) continue;
    z.healed.put(t, Double.valueOf(done + got));
    z.absorbed = z.absorbed + got;
    @VEC@ q = pos(cb, r);
    if (q != null) particle(FX_HEAL, q.x, q.y + 1.0, q.z, cb);
    if (isSelf) { self = self + got; @PKG@.HealMsg.given(z.caster, z.caster, got); }
    else { others = others + got; @PKG@.HealMsg.given(z.caster, t, got); @PKG@.HealMsg.taken(t, z.caster, z.name, got); }
  }
  if (xp) {
    if (others > 0.0) @PKG@.HealTask.xp(z.caster, others);
    if (self > 0.0) @PKG@.HealTask.xpSelf(z.caster, self);
  }
  return others + self;
}""")
M(abil, r"""
public static void zoneEnd2(@PKG@.AbilZone z, @CAC@ acc) {
  z.ended = true;
  @PR@ pr = prOf(z.caster);
  if (z.kind == 5) {
    particle(FX_END, z.x, z.y + 1.0, z.z, acc);
    if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SANCT, z.shape) + " faded (+" + @PKG@.AbilMath.fmt(z.absorbed) + " HP healed).");
    return;
  }
  if (z.kind == 4) {
    if (pr != null) say(pr, "Running Blessing ended - it touched " + z.hits + (z.hits == 1 ? " player" : " players") + " (+" + @PKG@.AbilMath.fmt(z.absorbed) + " HP, healing over time follows).");
    return;
  }
  if (z.kind == 3 && pr != null) say(pr, "Frost Wake melted - it froze " + z.hits + (z.hits == 1 ? " enemy." : " enemies."));
}""")
# the 0.1.18 zone kinds (zoneTick hands them here); false = over (the caller drops it)
M(abil, r"""
public static boolean zoneTick2(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 5) {   // Sanctuary: its own clock (like the bubble); no XP after a profile switch / in creative (xpOk)
    if (z.ended || now >= z.until) { zoneEnd2(z, cb); return false; }
    if (now >= z.nextHeal) {
      z.nextHeal = z.nextHeal + 1000L;
      sanctPulse(z, st, cb, xpOk(z, st, cb));
    }
    if (now >= z.nextFx) { z.nextFx = now + 1000L; ring(FX_HOLY, z, cb); }
    return true;
  }
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  if (!ok || z.ended || now >= z.until) { zoneEnd2(z, cb); return false; }
  if (z.kind == 3) {   // Frost Wake
    wakeTick(z, cb, cr, now);
    if (now >= z.nextFx) { z.nextFx = now + 1000L; wakeFx(z, cb); }
    return true;
  }
  if (z.kind == 4) {   // Running Blessing: the circle is where the Priest is now
    @VEC@ p = pos(cb, cr);
    if (p != null) { z.x = p.x; z.y = p.y; z.z = p.z; }
    blessTick(z, st, cb, now);
    if (now >= z.nextFx) { z.nextFx = now + 500L; ring(FX_BLESS, z, cb); }
    return true;
  }
  return false;
}""")
# ---- the HEAL at a spot (Beacon where you land, Kneel where you knelt): healCast's rules with a centre, a radius and multipliers
M(abil, r"""
public static void gatherAt(@ST@ st, @CAC@ acc, double[] c, double rad, java.util.ArrayList us, java.util.ArrayList rs) {
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ p = (@PR@) it.next();
    if (p == null || !p.isValid()) continue;
    java.util.UUID pu = p.getUuid();
    if (pu == null) continue;
    @REF@ r = p.getReference();
    if (r == null || !r.isValid() || r.getStore() != st) continue;
    @VEC@ q = pos(acc, r);
    if (q == null || !@PKG@.AbilMath.inRange(q.x - c[0], q.y - c[1], q.z - c[2], rad)) continue;
    us.add(pu);
    rs.add(r);
  }
}""")
M(abil, r"""
public static String healAt(@PR@ pr, @ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, double[] c, double rad, double mult, double hotMult, long now, String pkey, int sh) {
  boolean xpOk = !creative(acc, ref) && (pkey == null || pkey.equals(@PKG@.ClassCfg.pkey(u)));
  String healer = pr == null ? "" : pr.getUsername();
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  gatherAt(st, acc, c, rad, us, rs);
  double others = 0.0;
  double self = 0.0;
  int healed = 0;
  int hots = 0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    if (!healable(acc, r)) continue;
    double mx = max(map(acc, r), @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(u);
    boolean party = isSelf || @PKG@.HealTask.inParty(u, t);
    double want = @PKG@.HealTask.split(@PKG@.AbilMath.heal(mx, @PKG@.AbilCfg.S_HEAL, isSelf, @PKG@.AbilCfg.S_SELF) * mult, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    double cap = @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, 0.0);
    double got = apply(acc, r, want, cap);
    @PKG@.AbilJob h = hotJob(u, pkey, healer, t, want, got, cap, (double) @PKG@.AbilCfg.S_HOT * hotMult, c[0], c[1], c[2], rad, now);
    if (h != null && aw != null) { aw.add(h); hots++; }
    @VEC@ q = pos(acc, r);
    if (q != null) particle(FX_HEAL, q.x, q.y + 1.0, q.z, acc);
    if (!(got > 0.0)) continue;
    healed++;
    if (isSelf) { self = self + got; @PKG@.HealMsg.given(u, u, got); }
    else { others = others + got; @PKG@.HealMsg.given(u, t, got); @PKG@.HealMsg.taken(t, u, healer, got); }
  }
  if (xpOk) {
    if (others > 0.0) @PKG@.HealTask.xp(u, others);
    if (self > 0.0) @PKG@.HealTask.xpSelf(u, self);
  }
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SACRED, sh) + ": " + (healed == 0 ? "nobody needed healing" : "+" + @PKG@.AbilMath.fmt(others + self) + " HP to " + healed + (healed == 1 ? " player" : " players")) + (hots > 0 ? ", healing over time." : "."));
  return " healed=" + healed + " hp=" + @PKG@.AbilMath.fmt(others + self) + " hot=" + hots;
}""")
# ---- MARTYR'S GRACE: the chain. Candidates = hurt, healable players within range (you too); party (you count) before others, each group
# lowest Health share first; first (a UUID) goes to the front when it is a candidate; at most G_TARGETS
M(abil, r"""
public static void graceTargets(@ST@ st, @CAC@ acc, java.util.UUID u, double[] c, java.util.UUID first, java.util.ArrayList us, java.util.ArrayList rs) {
  java.util.ArrayList cu = new java.util.ArrayList();
  java.util.ArrayList cr = new java.util.ArrayList();
  gatherAt(st, acc, c, @PKG@.AbilCfg.G_RANGE, cu, cr);
  int n = cu.size();
  double[] key = new double[n];
  boolean[] ok = new boolean[n];
  for (int i = 0; i < n; i++) {
    java.util.UUID t = (java.util.UUID) cu.get(i);
    @REF@ r = (@REF@) cr.get(i);
    if (!healable(acc, r)) continue;
    @ESM@ m = map(acc, r);
    double mx = max(m, @DST@.getHealth());
    double h = cur(m, @DST@.getHealth());
    if (!(mx > 0.0) || !(h >= 0.0) || !(mx - h > 0.01)) continue;
    boolean party = t.equals(u) || @PKG@.HealTask.inParty(u, t);
    key[i] = (party ? 0.0 : 2.0) + h / mx;
    if (first != null && first.equals(t)) key[i] = -1.0;
    ok[i] = true;
  }
  long most = @PKG@.AbilCfg.G_TARGETS;
  while ((long) us.size() < most) {
    int b = -1;
    for (int i = 0; i < n; i++) if (ok[i] && (b < 0 || key[i] < key[b])) b = i;
    if (b < 0) break;
    ok[b] = false;
    us.add(cu.get(b));
    rs.add(cr.get(b));
  }
}""")
M(abil, r"""
public static java.util.UUID lookPlayer(@CAC@ acc, @REF@ ref, double range) {
  try {
    java.util.function.Function f = TARGET;
    if (f != null) {
      Object o = f.apply(ref);
      return o instanceof java.util.UUID ? (java.util.UUID) o : null;
    }
    @REF@ t = @TU@.getTargetEntity(ref, (float) range, acc);
    if (t == null || !t.isValid()) return null;
    Object po = acc.getComponent(t, @PR@.getComponentType());
    return po instanceof @PR@ ? ((@PR@) po).getUuid() : null;
  } catch (Throwable x) { return null; }
}""")
M(abil, r"""
public static java.util.UUID graceFirst(@CAC@ acc, @REF@ ref, java.util.UUID u, int sh) {
  if (sh == 1) return lookPlayer(acc, ref, @PKG@.AbilCfg.G_RANGE);
  if (sh == 2) return u;
  return null;
}""")
M(abil, r"""
public static int graceCount(@ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, int sh) {
  double[] c = here(acc, ref);
  if (c == null) return 0;
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  graceTargets(st, acc, u, c, graceFirst(acc, ref, u, sh), us, rs);
  return us.size();
}""")
M(abil, r"""
public static String graceRun(@PR@ pr, @ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, int sh, String pkey) {
  double[] c = here(acc, ref);
  if (c == null) return " nopos";
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  graceTargets(st, acc, u, c, graceFirst(acc, ref, u, sh), us, rs);
  double fp = sh == 3 ? (double) @PKG@.AbilCfg.G_VOW_F : (double) @PKG@.AbilCfg.G_FIRST;
  double dp = sh == 3 ? (double) @PKG@.AbilCfg.G_VOW_D : (double) @PKG@.AbilCfg.G_DROP;
  boolean xpOk = !creative(acc, ref) && (pkey == null || pkey.equals(@PKG@.ClassCfg.pkey(u)));
  String healer = pr == null ? "" : pr.getUsername();
  double others = 0.0;
  double self = 0.0;
  int healed = 0;
  String order = "";
  for (int k = 0; k < us.size(); k++) {
    java.util.UUID t = (java.util.UUID) us.get(k);
    @REF@ r = (@REF@) rs.get(k);
    double pct = @PKG@.AbilMath.chainPct(k, fp, dp);
    if (!(pct > 0.0)) break;
    double mx = max(map(acc, r), @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(u);
    boolean party = isSelf || @PKG@.HealTask.inParty(u, t);
    double want = @PKG@.HealTask.split(mx * pct / 100.0, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    double got = apply(acc, r, want, @PKG@.AbilMath.capLeft(mx, k == 0 ? @PKG@.AbilCfg.G_CAP : @PKG@.AbilCfg.HEAL_CAP, 0.0));
    @VEC@ q = pos(acc, r);
    if (q != null) particle(FX_HEAL, q.x, q.y + 1.0, q.z, acc);
    order = order + (order.length() > 0 ? "," : "") + @PKG@.AbilMath.fmt(got);
    if (!(got > 0.0)) continue;
    healed++;
    if (isSelf) { self = self + got; @PKG@.HealMsg.given(u, u, got); }
    else { others = others + got; @PKG@.HealMsg.given(u, t, got); @PKG@.HealMsg.taken(t, u, healer, got); }
  }
  if (xpOk) {
    if (others > 0.0) @PKG@.HealTask.xp(u, others);
    if (self > 0.0) @PKG@.HealTask.xpSelf(u, self);
  }
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.GRACE, sh) + ": " + (healed == 0 ? "nobody needed healing." : "+" + @PKG@.AbilMath.fmt(others + self) + " HP to " + healed + (healed == 1 ? " player" : " players") + ", lowest first."));
  return " chain=" + order + " healed=" + healed;
}""")
# ---- STARFALL: a shower job (kind 5). x y z = the centre (sh 1 Star Trail: where the caster is at each star), r = its area, width = a
# star's hit size, amount = a star's damage, total / left = stars, every = the gap
M(abil, r"""
public static @PKG@.AbilJob starJob(java.util.UUID u, String pkey, double[] at, double area, long stars, double secs, double amount, int sh, long now) {
  int n = stars < 1L ? 1 : (int) stars;
  long every = Math.round(secs * 1000.0 / (double) n);
  if (every < 50L) every = 50L;
  @PKG@.AbilJob j = new @PKG@.AbilJob(5, now, u, "Starfall", at[0], at[1], at[2], area, amount);
  j.pkey = pkey;
  j.total = n;
  j.left = n;
  j.every = every;
  j.width = @PKG@.AbilCfg.T_STAR_R;
  j.sh = sh;
  j.ai = @PKG@.AbilDefs.STARF;
  j.hits = 0;
  return j;
}""")
M(abil, r"""
public static boolean starTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) return false;
  int i = j.total - j.left;
  double cx = j.x;
  double cy = j.y;
  double cz = j.z;
  if (j.sh == 1) {
    @VEC@ p = pos(cb, cr);
    if (p != null) { cx = p.x; cy = p.y; cz = p.z; }
  }
  double[] d = @PKG@.AbilMath.disc(i, j.total, j.r);
  double px = cx + d[0];
  double pz = cz + d[1];
  particle(FX_STAR, px, cy + 0.5, pz, cb);
  java.util.List l = near(cb, px, cy, pz, j.width);
  java.util.HashSet seen = new java.util.HashSet();
  for (int k = 0; k < l.size(); k++) {
    Object o = l.get(k);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t)) continue;
    if (!enemy(cb, t, cr)) continue;
    if (hit(cb, t, cr, j.caster, j.amount, "Starfall")) j.hits = j.hits + 1;
  }
  j.left = j.left - 1;
  j.at = j.at + j.every;
  if (j.left > 0) return true;
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.STARF, j.sh) + ": " + j.total + " stars, " + j.hits + (j.hits == 1 ? " hit" : " hits") + " (" + @PKG@.AbilMath.fmt(j.amount) + " damage each before armour).");
  return false;
}""")
# ---- ARCANE BEAM: the channel (kind 6). Ticks every 0.5 s from the cast (0, 0.5 ... secs - 0.5): the nearest enemy on the beam (sh 1 Sweep:
# every enemy on it) takes amount x ramp x 0.5; the beam follows your look (sh 2 Beam Down: straight down). AbilStore.CHAN = the running one.
M(abil, r"""
public static @PKG@.AbilJob beamJob(java.util.UUID u, String pkey, String item, double h, int sh, long now) {
  double len = @PKG@.AbilCfg.R_RANGE;
  double secs = @PKG@.AbilCfg.R_TIME;
  double width = @PKG@.AbilCfg.R_WIDTH;
  double from = 1.0;
  double to = @PKG@.AbilCfg.R_RAMP;
  if (sh == 1) { len = @PKG@.AbilCfg.R_SWEEP_R; secs = @PKG@.AbilCfg.R_SWEEP_T; width = @PKG@.AbilCfg.R_SWEEP_W; from = @PKG@.AbilCfg.R_SWEEP_M; to = @PKG@.AbilCfg.R_SWEEP_M; }
  if (sh == 2) { len = @PKG@.AbilCfg.R_DOWN_R; secs = @PKG@.AbilCfg.R_DOWN_T; }
  if (sh == 3) { len = @PKG@.AbilCfg.R_FOCUS_R; secs = @PKG@.AbilCfg.R_FOCUS_T; to = @PKG@.AbilCfg.R_FOCUS_RAMP; }
  @PKG@.AbilJob j = new @PKG@.AbilJob(6, now, u, "ArcaneBeam", 0.0, 0.0, 0.0, len, h * @PKG@.AbilCfg.R_RATE);
  j.pkey = pkey;
  j.name = item;
  j.start = now;
  j.secs = secs;
  j.until = now + Math.round(secs * 1000.0);
  j.every = 500L;
  j.len = len;
  j.width = width;
  j.from = from;
  j.to = to;
  j.sh = sh;
  j.ai = @PKG@.AbilDefs.BEAM;
  j.hits = 0;
  j.total = 0;
  return j;
}""")
M(abil, r"""
public static boolean beamEnd(@PKG@.AbilJob j, String why) {
  if (@PKG@.AbilStore.CHAN.get(j.caster) == j) @PKG@.AbilStore.CHAN.remove(j.caster);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.BEAM, j.sh) + (why.length() > 0 ? " stopped - " + why : " ended") + ": " + j.hits + (j.hits == 1 ? " hit" : " hits") + ", " + @PKG@.AbilMath.fmt(j.paidMana) + " damage before armour.");
  return false;
}""")
M(abil, r"""
public static boolean beamTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (@PKG@.AbilStore.CHAN.get(j.caster) != j) return beamEnd(j, "you cast again");
  if (!live(cb, cr, j.caster, j.pkey)) return beamEnd(j, "you left");
  String it = hand(cb, cr);
  if (it == null || !it.equals(j.name)) return beamEnd(j, "you swapped your weapon");
  if (now >= j.until) return beamEnd(j, "");
  double ox = 0.0;
  double oy = 0.0;
  double oz = 0.0;
  double dx = 0.0;
  double dy = -1.0;
  double dz = 0.0;
  if (j.sh == 2) {
    @VEC@ p = pos(cb, cr);
    if (p == null) { j.at = j.at + j.every; return true; }
    ox = p.x;
    oy = p.y + 0.5;
    oz = p.z;
  } else {
    double[] lk = look(cb, cr);
    if (lk == null) { j.at = j.at + j.every; return true; }
    ox = lk[0];
    oy = lk[1];
    oz = lk[2];
    dx = lk[3];
    dy = lk[4];
    dz = lk[5];
  }
  double half = j.len / 2.0;
  java.util.List l = near(cb, ox + dx * half, oy + dy * half, oz + dz * half, half + j.width + 1.5);
  java.util.ArrayList on = new java.util.ArrayList();
  @REF@ best = null;
  double bestT = 1.0E18;
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t)) continue;
    if (!enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null) continue;
    double[] rd = @PKG@.AbilMath.rayDist(ox, oy, oz, dx, dy, dz, q.x, q.y + 1.0, q.z);
    if (rd[0] < 0.0 || rd[0] > j.len || rd[1] > j.width) continue;
    on.add(t);
    if (rd[0] < bestT) { bestT = rd[0]; best = t; }
  }
  double mult = @PKG@.AbilMath.ramp((double) (now - j.start) / 1000.0, j.secs, j.from, j.to);
  double dmg = j.amount * mult * (double) j.every / 1000.0;
  double reach = best == null ? j.len : bestT;
  for (double k = 2.0; k <= reach; k = k + 3.0) particle(FX_BEAM, ox + dx * k, oy + dy * k, oz + dz * k, cb);
  if (j.sh == 1) {
    for (int i = 0; i < on.size(); i++) if (hit(cb, (@REF@) on.get(i), cr, j.caster, dmg, "ArcaneBeam")) { j.hits = j.hits + 1; j.paidMana = j.paidMana + dmg; }
  } else if (best != null && hit(cb, best, cr, j.caster, dmg, "ArcaneBeam")) { j.hits = j.hits + 1; j.paidMana = j.paidMana + dmg; }
  j.total = j.total + 1;
  j.at = j.at + j.every;
  return true;
}""")
# ---- the 1 s CHANNEL (kind 7): Kneel / Martyr's Vow fire where you knelt - moving more than abil.channelMove gives everything back
M(abil, r"""
public static String chanRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) return "gone";
  @PR@ pr = prOf(j.caster);
  @VEC@ p = pos(cb, cr);
  if (p == null) return "nopos";
  if (!@PKG@.AbilMath.inRange(p.x - j.x, p.y - j.y, p.z - j.z, @PKG@.AbilCfg.CHAN_MOVE)) {
    @ESM@ m = map(cb, cr);
    if (m != null) {
      if (j.paidMana > 0.0) m.addStatValue(@DST@.getMana(), (float) j.paidMana);
      if (j.paidStam > 0.0) m.addStatValue(@DST@.getStamina(), (float) j.paidStam);
    }
    @PKG@.AbilStore.arm(j.pkey, j.what, now, 0L);
    if (pr != null) send(pr, @PKG@.AbilDefs.sname(j.ai, 3) + " broke - you moved. Your Mana, Stamina and cooldown were given back.", "#ffc800");
    return "moved";
  }
  double[] at = new double[] { p.x, p.y, p.z };
  if (j.ai == @PKG@.AbilDefs.SACRED) return healAt(pr, st, cb, cr, j.caster, at, @PKG@.AbilCfg.S_RADIUS, 1.0 + (double) @PKG@.AbilCfg.S_KNEEL / 100.0, (double) @PKG@.AbilCfg.S_KNEEL_HOT / 100.0, now, j.pkey, 3);
  if (j.ai == @PKG@.AbilDefs.GRACE) return graceRun(pr, st, cb, cr, j.caster, 3, j.pkey);
  return "none";
}""")
M(abil, r"""
public static @PKG@.AbilJob chanJob(java.util.UUID u, String pkey, int ai, double[] at, double secs, double mana, double stam, long now) {
  @PKG@.AbilJob j = new @PKG@.AbilJob(7, now + Math.round(secs * 1000.0), u, @PKG@.AbilDefs.IDS[ai], at[0], at[1], at[2], 0.0, 0.0);
  j.pkey = pkey;
  j.ai = ai;
  j.sh = 3;
  j.paidMana = mana;
  j.paidStam = stam;
  return j;
}""")
# ---- ON LANDING (kind 3): wait for the feet (abil.landWait at most), then the mid-air shape where you are
M(abil, r"""
public static @PKG@.AbilJob landJob(java.util.UUID u, String pkey, int ai, double amount, long now) {
  @PKG@.AbilJob j = new @PKG@.AbilJob(3, now, u, @PKG@.AbilDefs.IDS[ai], 0.0, 0.0, 0.0, 0.0, amount);
  j.pkey = pkey;
  j.ai = ai;
  j.sh = 2;
  j.until = now + Math.round(@PKG@.AbilCfg.LAND_WAIT * 1000.0);
  return j;
}""")
M(abil, r"""
public static String land(@PKG@.AbilJob j, @ST@ st, @CB@ cb, @REF@ cr, double[] at, long now) {
  int ai = j.ai;
  @PR@ pr = prOf(j.caster);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (aw == null) return "noworld";
  if (ai == @PKG@.AbilDefs.METEOR) {
    @PKG@.AbilJob m = new @PKG@.AbilJob(1, now, j.caster, "Meteor", at[0], at[1], at[2], @PKG@.AbilCfg.M_RADIUS, j.amount);
    m.pkey = j.pkey;
    particle(FX_MARK, at[0], at[1] + 0.1, at[2], cb);
    meteorImpact(m, st, cb);
    return "meteor:" + m.hits;
  }
  if (ai == @PKG@.AbilDefs.MANAB) { barrierAt(pr, cb, cr, j.caster, j.pkey, aw, at, now, @PKG@.AbilCfg.B_RADIUS, @PKG@.AbilCfg.B_TIME, @PKG@.AbilCfg.B_RATIO, 2); return "barrier"; }
  if (ai == @PKG@.AbilDefs.BUBBLE) { bubbleAt(pr, cb, cr, j.caster, j.pkey, aw, at, now, @PKG@.AbilCfg.U_RADIUS, @PKG@.AbilCfg.U_HP, 2); return "bubble"; }
  if (ai == @PKG@.AbilDefs.FROST) {
    @PKG@.AbilJob f = novaJob(j.caster, j.pkey, at, @PKG@.AbilCfg.F_DROP_R, j.amount, @PKG@.AbilCfg.F_FREEZE, @PKG@.AbilCfg.F_BREAK, @PKG@.AbilCfg.F_CHILL, now, 2);
    f.brkAmt = j.brkAmt;
    return "nova:" + novaRun(f, cb, cr, now);
  }
  if (ai == @PKG@.AbilDefs.STARF) {
    aw.add(starJob(j.caster, j.pkey, at, @PKG@.AbilCfg.T_BELOW_R, @PKG@.AbilCfg.T_STARS, @PKG@.AbilCfg.T_BELOW_T, j.amount, 2, now));
    if (pr != null) say(pr, "Starfall Below: stars fall around you for " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.T_BELOW_T) + " s.");
    return "stars";
  }
  if (ai == @PKG@.AbilDefs.SACRED) return "heal:" + healAt(pr, st, cb, cr, j.caster, at, @PKG@.AbilCfg.S_BEACON_R, 1.0, 1.0, now, j.pkey, 2);
  if (ai == @PKG@.AbilDefs.SANCT) { sanctAt(pr, cb, j.caster, j.pkey, aw, at, now, @PKG@.AbilCfg.Y_RADIUS, @PKG@.AbilCfg.Y_TIME, @PKG@.AbilCfg.Y_HEAL, @PKG@.AbilCfg.Y_CUT, 2); return "sanct"; }
  return "none";
}""")
F(abil, "public static volatile String LAST_LAND = \"\";")   # the last landing outcome (harness + /classadmin abil info)
M(abil, r"""
public static boolean landTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_LAND = "gone"; return false; }
  if (!onGround(cb, cr) && now < j.until) { j.at = now + 50L; return true; }
  double[] at = here(cb, cr);
  if (at == null) return false;
  LAST_LAND = land(j, st, cb, cr, at, now);
  return false;
}""")
'''

# runJob: + the 0.1.18 kinds
NEW_RUNJOB = r'''M(abil, r"""
public static boolean runJob(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (j == null) return false;
  if (j.kind == 1) { meteorImpact(j, st, cb); return false; }
  if (j.kind == 2) return hotTick(j, st, cb);
  if (j.kind == 3) return landTick(j, st, cb, now);          // 0.1.18: the mid-air shapes wait for the landing
  if (j.kind == 5) return starTick(j, st, cb, now);          // 0.1.18: Starfall
  if (j.kind == 6) return beamTick(j, st, cb, now);          // 0.1.18: Arcane Beam
  if (j.kind == 7) { chanRun(j, st, cb, now); return false; }   // 0.1.18: Kneel / Martyr's Vow
  if (j.kind == 8) {                                           // 0.1.18: Frost Nova
    @REF@ cr = casterRef(cb, j.caster);
    if (live(cb, cr, j.caster, j.pkey)) novaRun(j, cb, cr, now);
    return false;
  }
  return false;
}""")'''

# ---- GUARDIAN SPIRIT (the Priest's passive): called LAST in AbilShieldSys.handle (after armour, the drop filters, the sanctuary, the bubble,
# the barrier). r = the damaged PLAYER. Returns what it did (null = nothing; the harness reads it).
ABIL_018 += r'''
# FIX 2 (critic): the saved player's record is keyed by PROFILE (pkey|uuid, tools/PROFILES-CONTRACT.md item 2) - another profile of the same
# account is another character with its own count and cooldown
M(abil, r"""
public static String guardKey(java.util.UUID u) {
  return @PKG@.ClassCfg.pkey(u) + "|" + u;
}""")
M(abil, r"""
public static boolean guardian(java.util.UUID q) {
  int ci = @PKG@.ClassStore.classIndex(q);
  if (ci < 0 || ci != @PKG@.AbilDefs.CLS[@PKG@.AbilDefs.GUARD] || !@PKG@.ClassDefs.ENABLED[ci]) return false;
  String k = @PKG@.ClassCfg.pkey(q);
  return @PKG@.AbilDefs.owns(@PKG@.AbilDefs.GUARD, level(q, ci), @PKG@.AbilStore.granted(k), @PKG@.AbilStore.pick(k));
}""")
M(abil, r"""
public static boolean guardPays(@CAC@ acc, @REF@ r) {
  if (@PKG@.AbilCfg.CREATIVE_FREE && creative(acc, r)) return true;
  @ESM@ m = map(acc, r);
  double mana = cur(m, @DST@.getMana());
  double stam = cur(m, @DST@.getStamina());
  if (@PKG@.AbilCfg.GS_MANA > 0.0 && !(mana >= 0.0 && @PKG@.AbilMath.enough(mana, @PKG@.AbilCfg.GS_MANA))) return false;
  if (@PKG@.AbilCfg.GS_STAM > 0.0 && !(stam >= 0.0 && @PKG@.AbilMath.enough(stam, @PKG@.AbilCfg.GS_STAM))) return false;
  return true;
}""")
M(abil, r"""
public static String guard(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  if (!@PKG@.AbilCfg.PART || d == null || r == null || d.isCancelled()) return null;
  float a0 = d.getAmount();
  if (!(a0 > 0.0f)) return null;
  @DCS@ cause = null;
  try { cause = d.getCause(); } catch (Throwable t) { cause = null; }
  if (cause != null && (cause == @DCS@.OUT_OF_WORLD || cause == @DCS@.COMMAND)) return null;   // no void protection (Skyy 116-117)
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  if (buf.getComponent(r, @INVU@.getComponentType()) != null) return null;
  java.util.UUID u = ((@PR@) po).getUuid();
  if (u == null) return null;
  long[] rec = null;
  String gk = guardKey(u);
  Object ro = @PKG@.AbilStore.GUARD.get(gk);
  if (ro instanceof long[]) rec = (long[]) ro;
  if (rec != null && now - rec[2] >= Math.round(@PKG@.AbilCfg.GS_RESET * 1000.0)) { @PKG@.AbilStore.GUARD.remove(gk); rec = null; }
  if (rec != null) rec[2] = now;
  @ESM@ m = map(buf, r);
  int hi = @DST@.getHealth();
  double h = cur(m, hi);
  double mx = max(m, hi);
  if (!(h > 0.0) || !(mx > 0.0) || (double) a0 < h - 1.0E-4) return null;   // not a killing blow
  if (rec != null && now < rec[1]) { LAST_GUARD = "cooldown"; return "cooldown"; }
  @VEC@ p = pos(buf, r);
  if (p == null) return null;
  double rad = @PKG@.AbilCfg.GS_RADIUS;
  @PR@ best = null;
  @REF@ bestRef = null;
  double bestD = 1.0E18;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ q = (@PR@) it.next();
    if (q == null || !q.isValid()) continue;
    java.util.UUID qu = q.getUuid();
    if (qu == null) continue;
    @REF@ qr = q.getReference();
    if (qr == null || !qr.isValid() || qr.getStore() != st) continue;
    if (!qu.equals(u) && !@PKG@.AbilCfg.GS_ALL && !@PKG@.HealTask.inParty(qu, u)) continue;
    @VEC@ qp = pos(buf, qr);
    if (qp == null) continue;
    double dd = (qp.x - p.x) * (qp.x - p.x) + (qp.y - p.y) * (qp.y - p.y) + (qp.z - p.z) * (qp.z - p.z);
    if (dd > rad * rad || dd >= bestD) continue;
    if (!guardian(qu) || @PKG@.Kit.busy(qu)) continue;
    if (!qu.equals(u) && !alive(buf, qr)) continue;
    if (!guardPays(buf, qr)) continue;
    best = q;
    bestRef = qr;
    bestD = dd;
  }
  if (best == null) { LAST_GUARD = "nopriest"; return "nopriest"; }
  boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(buf, bestRef);
  @ESM@ pm = map(buf, bestRef);
  if (!free && pm != null) {
    if (@PKG@.AbilCfg.GS_MANA > 0.0) pm.subtractStatValue(@DST@.getMana(), (float) @PKG@.AbilCfg.GS_MANA);
    if (@PKG@.AbilCfg.GS_STAM > 0.0) pm.subtractStatValue(@DST@.getStamina(), (float) @PKG@.AbilCfg.GS_STAM);
  }
  d.setAmount(0.0f);
  d.setCancelled(true);
  m.setStatValue(hi, (float) (mx * (double) @PKG@.AbilCfg.GS_HP / 100.0));
  int cnt = rec == null ? 1 : (int) rec[0] + 1;
  long cd = @PKG@.AbilMath.guardCd(Math.round(@PKG@.AbilCfg.GS_CD * 1000.0), cnt);
  @PKG@.AbilStore.GUARD.put(gk, new long[] { (long) cnt, now + cd, now });
  particle(FX_GUARD, p.x, p.y + 1.0, p.z, buf);
  SAVES = SAVES + 1L;
  boolean self = best.getUuid().equals(u);
  String cost = free ? "free" : "-" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.GS_MANA) + " Mana, -" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.GS_STAM) + " Stamina";
  String next = " Next save for " + (self ? "you" : "them") + " in " + @PKG@.AbilMath.secs(cd) + " s.";
  say(best, "Guardian Spirit saved " + (self ? "you" : ((@PR@) po).getUsername()) + " at " + @PKG@.AbilCfg.GS_HP + " % Health (" + cost + ")." + next);
  if (!self) say((@PR@) po, "A Guardian Spirit (" + best.getUsername() + ") saved you - " + @PKG@.AbilCfg.GS_HP + " % Health.");
  LAST_GUARD = "saved:" + best.getUsername() + " count=" + cnt + " next=" + @PKG@.AbilMath.secs(cd);
  return LAST_GUARD;
}""")
'''

# ---- THE PIPELINE with SHAPES (engine spec 4 + plan 3.2): castAt = castNow + a forced shape (-1 = read it from the body at the press)
NEW_CASTNOW = r'''M(abil, r"""
public static String castAt(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg, int forced) {
  if (pr == null || st == null || ref == null || !ref.isValid()) return "bad";
  java.util.UUID u = pr.getUuid();
  if (!@PKG@.AbilCfg.PART) { refuse(pr, "Class abilities are switched off on this server."); return "off"; }
  int slot = @PKG@.AbilMath.slotOf(arg);
  if (slot < 0) { send(pr, "Usage: /cast 1 or /cast 2 (crouch = your alt), /cast 3 or 4 = your alts, /cast list, /cast swap, /cast page", "#ffc800"); return "usage"; }
  if (@PKG@.Kit.busy(u)) { refuse(pr, "Your profile is still loading - try again in a moment."); return "busy"; }
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) { refuse(pr, noClass()); return "noclass"; }
  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) { refuse(pr, @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first."); return "noabil"; }
  if (!alive(st, ref)) return "dead";
  long now = System.currentTimeMillis();
  boolean crouch = false;
  int s = -1;
  int sh = 0;
  if (forced >= 0) {   // /classadmin shape: the shape is given (crouch = the alt on a primary key)
    crouch = forced == 3 && slot < 2;
    s = @PKG@.AbilMath.resolve(slot, crouch);
    sh = forced;
  } else {             // 0.1.18: read at the press - in the air (abil.airMin), crouch held (abil.crouchMin), sprinting
    boolean air = airNow(st, ref, u, now);
    crouch = !air && crouching(st, ref) && crouchNow(u, now);
    boolean sprint = sprinting(st, ref);
    if (air && slot >= 2 && @PKG@.AbilCfg.SHAPES) {   // FIX 2: alts cannot be cast in the air (shapes spec section 0, Skyy line 150)
      refuse(pr, "Your alts cannot be cast in the air - in the air /cast 1 and /cast 2 fire your primaries' mid-air shapes. Nothing was spent.");
      return "air";
    }
    s = @PKG@.AbilMath.resolveAt(slot, crouch, air);
    sh = @PKG@.AbilMath.shapeOf(s, air, sprint, @PKG@.AbilCfg.SHAPES, @PKG@.AbilCfg.SHAPES_SPRINT && @PKG@.ClassCfg.notifyOn(u, "classes.abilSprint"),
        @PKG@.AbilCfg.SHAPES_AIR && @PKG@.ClassCfg.notifyOn(u, "classes.abilAir"));
  }
  String k = @PKG@.ClassCfg.pkey(u);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  int ai = @PKG@.AbilDefs.find(sl[s]);
  if (ai < 0) { refuse(pr, "No ability on " + @PKG@.AbilDefs.key(s) + "."); return "empty"; }
  String nm = @PKG@.AbilDefs.NAMES[ai];
  int lv = level(u, ci);
  if (!@PKG@.AbilDefs.owns(ai, lv, @PKG@.AbilStore.granted(k), @PKG@.AbilStore.pick(k))) {
    refuse(pr, (s >= 2 ? "No alt yet - " : "") + nm + " unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]) + " (you are " + lv + ").");
    return "locked";
  }
  if (@PKG@.AbilDefs.PASSIVE[ai]) {
    refuse(pr, nm + " is a passive - it is always on: a killing blow on you or your party within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.GS_RADIUS) + " blocks leaves them at " + @PKG@.AbilCfg.GS_HP + " % Health (" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.GS_MANA) + " Mana a save).");
    return "passive";
  }
  if (!@PKG@.AbilDefs.BUILT[ai]) { refuse(pr, nm + " comes in a later update - nothing was spent."); return "soon"; }
  String item = hand(st, ref);
  if (item == null || @PKG@.ClassDefs.ownerOf(item) != ci || !@PKG@.ClassRules.allowed(u, item)) {
    refuse(pr, "Hold your " + @PKG@.ClassDefs.NAMES[ci] + " weapon (" + @PKG@.ClassDefs.WTEXT[ci] + ") to cast " + nm + ".");
    return "weapon";
  }
  String id = @PKG@.AbilDefs.IDS[ai];
  String dn = @PKG@.AbilDefs.sname(ai, sh);
  long left = @PKG@.AbilStore.left(k, id, now);
  if (left > 0L) {
    if (@PKG@.AbilCfg.CD_MSG) refuse(pr, nm + " is " + @PKG@.AbilMath.readyText(left) + ".");
    else click(pr);
    return "cooldown";
  }
  boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(st, ref);
  double mana = free ? 0.0 : @PKG@.AbilDefs.mana(ai, sh);
  double stam = free ? 0.0 : @PKG@.AbilDefs.stamina(ai, sh);
  @ESM@ m = map(st, ref);
  int mi = @DST@.getMana();
  int si = @DST@.getStamina();
  double hm = cur(m, mi);
  double hs = cur(m, si);
  if ((mana > 0.0 && !(hm >= 0.0)) || (stam > 0.0 && !(hs >= 0.0))) {
    refuse(pr, "Your Mana and Stamina are not ready yet - try again in a moment (nothing was spent).");
    return "nostats";
  }
  if (mana > 0.0 && hm >= 0.0 && !@PKG@.AbilMath.enough(hm, mana)) {
    refuse(pr, "Not enough Mana for " + dn + ": " + @PKG@.AbilMath.fmt(hm) + " / " + @PKG@.AbilMath.fmt(mana) + ".");
    return "mana";
  }
  if (stam > 0.0 && hs >= 0.0 && !@PKG@.AbilMath.enough(hs, stam)) {
    refuse(pr, "Not enough Stamina for " + dn + ": " + @PKG@.AbilMath.fmt(hs) + " / " + @PKG@.AbilMath.fmt(stam) + ".");
    return "stamina";
  }
  if (ai == @PKG@.AbilDefs.MANAB && !free && @PKG@.AbilCfg.B_KEEP > 0.0 && hm >= 0.0 && !@PKG@.AbilMath.enough(hm, mana + @PKG@.AbilCfg.B_KEEP)) {
    refuse(pr, "Not enough Mana to power the Mana Barrier: " + @PKG@.AbilMath.fmt(mana) + " to cast + " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.B_KEEP)
        + " left to soak with (you have " + @PKG@.AbilMath.fmt(hm) + ") - nothing was spent.");
    return "mana";
  }
  // where (walking = where you look; sprint = ahead; mid-air = where you land, decided later; crouch = on you)
  double[] at = null;
  if (ai == @PKG@.AbilDefs.METEOR && sh == 0) {
    at = aim(st, ref, @PKG@.AbilCfg.M_RANGE);
    if (at == null) { refuse(pr, "Look at the ground within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.M_RANGE) + " blocks to call the Meteor down - nothing was spent."); return "aim"; }
  }
  if (ai == @PKG@.AbilDefs.STARF && sh == 0) {
    at = aim(st, ref, @PKG@.AbilCfg.T_RANGE);
    if (at == null) { refuse(pr, "Look at the ground within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.T_RANGE) + " blocks to call the stars down - nothing was spent."); return "aim"; }
  }
  if ((ai == @PKG@.AbilDefs.MANAB || ai == @PKG@.AbilDefs.BUBBLE) && sh == 0) {   // 0.1.17: where you look within the reach, else at your feet
    at = spot(st, ref, ai == @PKG@.AbilDefs.MANAB ? @PKG@.AbilCfg.B_RANGE : @PKG@.AbilCfg.U_RANGE);
    if (at == null) { refuse(pr, "Could not find where to place " + nm + " - nothing was spent."); return "aim"; }
  }
  if (ai == @PKG@.AbilDefs.MANAB && sh == 0 && at != null) {   // 0.1.17 FIX ROUND: the walking dome must cover the Mage, else her feet
    @VEC@ me = pos(st, ref);
    if (me != null && !@PKG@.AbilMath.inRange(at[0] - me.x, at[1] - me.y, at[2] - me.z, @PKG@.AbilCfg.B_RADIUS - 0.5)) at = new double[] { me.x, me.y, me.z };
  }
  if (sh == 1 && (ai == @PKG@.AbilDefs.METEOR || ai == @PKG@.AbilDefs.MANAB || ai == @PKG@.AbilDefs.BUBBLE)) at = ahead(st, ref, @PKG@.AbilCfg.AHEAD);
  if (sh == 1 && ai == @PKG@.AbilDefs.SANCT) at = ahead(st, ref, @PKG@.AbilCfg.Y_AHEAD);
  if (at == null && sh != 2) at = here(st, ref);
  if (at == null && sh != 2) { refuse(pr, "Could not find where you are - nothing was spent."); return "aim"; }
  if (ai == @PKG@.AbilDefs.SACRED && (sh == 0 || sh == 3) && needHeal(st, ref, u) == 0) {
    refuse(pr, "Nobody within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.S_RADIUS) + " blocks needs healing - nothing was spent.");
    return "noneed";
  }
  if (ai == @PKG@.AbilDefs.GRACE && graceCount(st, st, ref, u, sh) == 0) {
    refuse(pr, "Nobody within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.G_RANGE) + " blocks needs healing - nothing was spent.");
    return "noneed";
  }
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(w == null ? @PKG@.AbilWorld.nameOf(st.getExternalData()) : w.getName());
  if (aw.full()) { refuse(pr, "Too many abilities are running in this world - try again in a moment."); return "full"; }
  if (mana > 0.0 && hm >= 0.0) m.subtractStatValue(mi, (float) mana);
  if (stam > 0.0 && hs >= 0.0) m.subtractStatValue(si, (float) stam);
  long cd = @PKG@.AbilDefs.cdMs(ai, sh);
  @PKG@.AbilStore.arm(k, id, now, cd);
  @PKG@.AbilStore.CHAN.remove(u);   // 0.1.18: a new cast ends your Arcane Beam
  say(pr, dn + "! -" + @PKG@.AbilMath.fmt(mana) + " Mana, -" + @PKG@.AbilMath.fmt(stam) + " Stamina. Ready again in " + @PKG@.AbilMath.secs(cd) + " s.");
  String extra = "";
  try {
    double h = 0.0;
    if (ai == @PKG@.AbilDefs.METEOR || ai == @PKG@.AbilDefs.FROST || ai == @PKG@.AbilDefs.STARF || ai == @PKG@.AbilDefs.BEAM) h = hOf(item);
    if (ai == @PKG@.AbilDefs.METEOR) {
      if (sh == 0) extra = meteorCast(st, u, aw, at, item, now);
      else if (sh == 2) { aw.add(landJob(u, k, ai, h * @PKG@.AbilCfg.M_POWER, now)); extra = " H=" + @PKG@.AbilMath.fmt(h) + " land"; }
      else {
        double mr0 = sh == 1 ? @PKG@.AbilCfg.M_COMET_R : @PKG@.AbilCfg.M_ONME_R;
        double mAmt = h * (sh == 1 ? @PKG@.AbilCfg.M_POWER : @PKG@.AbilCfg.M_ONME_P);
        long mdl = Math.round((sh == 1 ? @PKG@.AbilCfg.M_DELAY : @PKG@.AbilCfg.M_ONME_D) * 1000.0);
        @PKG@.AbilJob mj = new @PKG@.AbilJob(1, now + mdl, u, "Meteor", at[0], at[1], at[2], mr0, mAmt);
        mj.pkey = k;
        particle(FX_MARK, at[0], at[1] + 0.1, at[2], st);
        aw.add(mj);
        extra = " H=" + @PKG@.AbilMath.fmt(h) + " damage=" + @PKG@.AbilMath.fmt(mAmt) + " r=" + @PKG@.AbilMath.fmt(mr0) + " at=" + @PKG@.AbilMath.fmt(at[0]) + "," + @PKG@.AbilMath.fmt(at[1]) + "," + @PKG@.AbilMath.fmt(at[2]);
      }
    }
    else if (ai == @PKG@.AbilDefs.SACRED) {
      if (sh == 0) extra = healCast(pr, st, ref, u, aw, now);
      else if (sh == 1) { blessAt(pr, st, ref, u, k, aw, now); extra = " bless"; }
      else if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else { aw.add(chanJob(u, k, ai, at, @PKG@.AbilCfg.S_KNEEL_T, mana, stam, now)); extra = " kneel"; }
    }
    else if (ai == @PKG@.AbilDefs.MANAB) {
      if (sh == 0) extra = barrierCast(pr, st, ref, u, aw, at, now);
      else if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else {
        @PKG@.AbilZone zb = sh == 1 ? barrierAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.B_RADIUS, @PKG@.AbilCfg.B_TIME, @PKG@.AbilCfg.B_RATIO, 1)
                                    : barrierAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.B_POCKET_R, @PKG@.AbilCfg.B_POCKET_T, @PKG@.AbilCfg.B_POCKET_RATIO, 3);
        extra = spotText(zb) + " cap=" + @PKG@.AbilMath.fmt(zb.cap) + " ratio=" + @PKG@.AbilMath.fmt(zb.ratio);
      }
    }
    else if (ai == @PKG@.AbilDefs.BUBBLE) {
      if (sh == 0) extra = bubbleCast(pr, st, ref, u, aw, at, now);
      else if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else {
        @PKG@.AbilZone zu = sh == 1 ? bubbleAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.U_RADIUS, @PKG@.AbilCfg.U_HP, 1)
                                    : bubbleAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.U_AROUND_R, @PKG@.AbilCfg.U_AROUND_HP, 3);
        extra = spotText(zu) + " hp=" + @PKG@.AbilMath.fmt(zu.hpMax);
      }
    }
    else if (ai == @PKG@.AbilDefs.FROST) {
      double fAmt = h * @PKG@.AbilCfg.F_POWER;
      double fBrk = h * @PKG@.AbilCfg.F_BREAK_P;   // FIX 2: the break damage
      @PKG@.AbilJob fj = null;
      if (sh == 1) { @PKG@.AbilZone fz = wakeAt(pr, st, ref, u, k, aw, fAmt, now); if (fz != null) fz.brkAmt = fBrk; extra = " wake"; }
      else if (sh == 2) { fj = landJob(u, k, ai, fAmt, now); extra = " land"; }
      else if (sh == 3) fj = novaJob(u, k, at, @PKG@.AbilCfg.F_DEEP_R, fAmt, @PKG@.AbilCfg.F_DEEP_F, @PKG@.AbilCfg.F_DEEP_B, @PKG@.AbilCfg.F_CHILL, now, 3);
      else fj = novaJob(u, k, at, @PKG@.AbilCfg.F_RADIUS, fAmt, @PKG@.AbilCfg.F_FREEZE, @PKG@.AbilCfg.F_BREAK, @PKG@.AbilCfg.F_CHILL, now, 0);
      if (fj != null) { fj.brkAmt = fBrk; aw.add(fj); }
      extra = extra + " H=" + @PKG@.AbilMath.fmt(h) + " damage=" + @PKG@.AbilMath.fmt(fAmt);
    }
    else if (ai == @PKG@.AbilDefs.STARF) {
      double tAmt = h * @PKG@.AbilCfg.T_POWER;
      if (sh == 2) { aw.add(landJob(u, k, ai, tAmt, now)); extra = " land"; }
      else if (sh == 1) aw.add(starJob(u, k, at, 2.0, @PKG@.AbilCfg.T_STARS, @PKG@.AbilCfg.T_TIME, tAmt, 1, now));
      else if (sh == 3) aw.add(starJob(u, k, at, @PKG@.AbilCfg.T_RADIUS, @PKG@.AbilCfg.T_SHOWER_N, @PKG@.AbilCfg.T_SHOWER_T, tAmt, 3, now));
      else aw.add(starJob(u, k, at, @PKG@.AbilCfg.T_RADIUS, @PKG@.AbilCfg.T_STARS, @PKG@.AbilCfg.T_TIME, tAmt, 0, now));
      extra = extra + " H=" + @PKG@.AbilMath.fmt(h) + " star=" + @PKG@.AbilMath.fmt(tAmt);
    }
    else if (ai == @PKG@.AbilDefs.BEAM) {
      @PKG@.AbilJob bj = beamJob(u, k, item, h, sh, now);
      @PKG@.AbilStore.CHAN.put(u, bj);
      aw.add(bj);
      extra = " H=" + @PKG@.AbilMath.fmt(h) + " rate=" + @PKG@.AbilMath.fmt(bj.amount) + " len=" + @PKG@.AbilMath.fmt(bj.len) + " secs=" + @PKG@.AbilMath.fmt(bj.secs);
    }
    else if (ai == @PKG@.AbilDefs.SANCT) {
      if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else {
        @PKG@.AbilZone zy = sh == 3 ? sanctAt(pr, st, u, k, aw, at, now, @PKG@.AbilCfg.Y_IN_R, @PKG@.AbilCfg.Y_IN_T, @PKG@.AbilCfg.Y_IN_H, @PKG@.AbilCfg.Y_IN_C, 3)
                                    : sanctAt(pr, st, u, k, aw, at, now, @PKG@.AbilCfg.Y_RADIUS, @PKG@.AbilCfg.Y_TIME, @PKG@.AbilCfg.Y_HEAL, @PKG@.AbilCfg.Y_CUT, sh);
        extra = spotText(zy) + " heal=" + @PKG@.AbilMath.fmt(zy.pct) + " cut=" + @PKG@.AbilMath.fmt(zy.cut);
      }
    }
    else if (ai == @PKG@.AbilDefs.GRACE) {
      if (sh == 3) { aw.add(chanJob(u, k, ai, at, @PKG@.AbilCfg.G_VOW_T, mana, stam, now)); extra = " vow"; }
      else extra = graceRun(pr, st, st, ref, u, sh, k);
    }
  } catch (Throwable x) {
    if (mana > 0.0 && hm >= 0.0) m.addStatValue(mi, (float) mana);
    if (stam > 0.0 && hs >= 0.0) m.addStatValue(si, (float) stam);
    @PKG@.AbilStore.arm(k, id, now, 0L);
    @PKG@.ClassCfg.warn("ability " + id + " failed after paying - Mana, Stamina and the cooldown were given back: " + x);
    send(pr, nm + " could not be cast - your Mana, Stamina and cooldown were given back (the server log has the details).", "#ffc800");
    return "failed";
  }
  return "ok:" + id + (crouch && slot < 2 ? " crouch" : "") + (sh != 0 ? " shape=" + @PKG@.AbilDefs.SHAPES[sh] : "") + " mana=" + @PKG@.AbilMath.fmt(mana) + " stamina=" + @PKG@.AbilMath.fmt(stam) + extra;
}""")
M(abil, r"""
public static String castNow(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {
  return castAt(pr, st, ref, w, arg, -1);
}""")'''

# where the moved / new methods go: right before the list / swap / admin block (everything they call exists by then)
_P = '''# ---- /cast list, /cast swap, /classadmin abil, the HUD bridge'''
rep(_P, ABIL_018 + "\n" + NEW_ZONETICK + "\n" + NEW_SHIELD + "\n" + NEW_RUNJOB + "\n" + NEW_CASTNOW + "\n" + OLD_CAST + '''
# 0.1.18: /classadmin shape <1-4> <walk|sprint|air|crouch> - the admin's own cast with the shape forced (the full pipeline; it pays)
M(abil, r"""
public static String adminShape(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String slot, String shape) {
  boolean ok = false;
  try { ok = pr.hasPermission("skyyclasses.admin"); } catch (Throwable t) { ok = false; }
  if (!ok) { send(pr, "no permission (skyyclasses.admin)", "#ffc800"); return "denied"; }
  int sh = @PKG@.AbilDefs.shapeOf(shape);
  if (sh < 0 || @PKG@.AbilMath.slotOf(slot) < 0) { send(pr, "Usage: /classadmin shape <1|2|3|4> <walk|sprint|air|crouch>", "#ffc800"); return "usage"; }
  String r = castAt(pr, st, ref, w, slot, sh);
  LAST = r;
  send(pr, "Forced shape " + @PKG@.AbilDefs.SHAPES[sh] + ": " + r, null);
  return r;
}""")
# 0.1.18: the Ability 1 alt pick (the Abilities page): the old A1-alt in your 4 slots becomes the new one, nothing else moves
M(abil, r"""
public static String setPick(String k, int ci, String np) {
  String old = @PKG@.AbilStore.pick(k);
  String nw = np != null && np.trim().equalsIgnoreCase("B") ? "B" : "A";
  int oa = @PKG@.AbilDefs.of(ci, @PKG@.AbilDefs.pickTier(old));
  int na = @PKG@.AbilDefs.of(ci, @PKG@.AbilDefs.pickTier(nw));
  if (oa < 0 || na < 0) return "Your class has no Ability 1 alt.";
  if (nw.equals(old)) return @PKG@.AbilDefs.NAMES[na] + " is already your Ability 1 alt.";
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  String[] ns = new String[4];
  for (int i = 0; i < 4; i++) ns[i] = @PKG@.AbilDefs.IDS[oa].equals(sl[i]) ? @PKG@.AbilDefs.IDS[na] : sl[i];
  if (!@PKG@.AbilStore.set(k, new String[] { "alt", "p1", "p2", "a1", "a2" }, new String[] { nw, ns[0], ns[1], ns[2], ns[3] }))
    return "Your ability file could not be read - nothing changed (see the server log).";
  @PKG@.AbilStore.saveSoon(k);
  return "Your Ability 1 alt is now " + @PKG@.AbilDefs.NAMES[na] + " - " + @PKG@.AbilDefs.NAMES[oa] + " is locked out (switch back here any time out of combat).";
}""")
# 0.1.18: swap two of your 4 slots (the page): both must be unlocked; a re-ordering only
M(abil, r"""
public static String swapSlots(java.util.UUID u, int a, int b) {
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) return "Your class has no abilities yet.";
  if (a < 0 || a > 3 || b < 0 || b > 3 || a == b) return "Pick two different slots.";
  if (combatMs(u) > 0L) return "Leave combat first - abilities change only out of combat.";
  String k = @PKG@.ClassCfg.pkey(u);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  int lv = level(u, ci);
  boolean grant = @PKG@.AbilStore.granted(k);
  String pick = @PKG@.AbilStore.pick(k);
  int x = @PKG@.AbilDefs.find(sl[a]);
  int y = @PKG@.AbilDefs.find(sl[b]);
  if (x < 0 || !@PKG@.AbilDefs.owns(x, lv, grant, pick)) return (x < 0 ? "That slot" : @PKG@.AbilDefs.NAMES[x]) + " is locked - both must be unlocked to swap.";
  if (y < 0 || !@PKG@.AbilDefs.owns(y, lv, grant, pick)) return (y < 0 ? "That slot" : @PKG@.AbilDefs.NAMES[y]) + " is locked - both must be unlocked to swap.";
  String[] ns = new String[] { sl[0], sl[1], sl[2], sl[3] };
  ns[a] = sl[b];
  ns[b] = sl[a];
  if (!@PKG@.AbilStore.set(k, new String[] { "p1", "p2", "a1", "a2" }, ns)) return "Your ability file could not be read - nothing changed (see the server log).";
  @PKG@.AbilStore.saveSoon(k);
  String pv = "";
  if (@PKG@.AbilDefs.PASSIVE[x] && b < 2) pv = " " + @PKG@.AbilDefs.NAMES[x] + " is a passive: it works from any slot, so /cast " + (b + 1) + " does nothing now.";
  if (@PKG@.AbilDefs.PASSIVE[y] && a < 2) pv = " " + @PKG@.AbilDefs.NAMES[y] + " is a passive: it works from any slot, so /cast " + (a + 1) + " does nothing now.";
  return "ok:Swapped " + @PKG@.AbilDefs.NAMES[x] + " and " + @PKG@.AbilDefs.NAMES[y] + ". /cast 1 = " + @PKG@.AbilDefs.NAMES[@PKG@.AbilDefs.find(ns[0])] + ", /cast 2 = " + @PKG@.AbilDefs.NAMES[@PKG@.AbilDefs.find(ns[1])] + "." + pv;
}""")
''' + _P)

# ================================================================================================ /cast list + admin: the passive and the picks
rep('''    if (st.equals("passive")) tx = "passive - comes in a later update";''',
    '''    if (st.equals("passive")) tx = "passive - always on (a killing blow on you or your party near you leaves them at " + @PKG@.AbilCfg.GS_HP + " % Health)";''')
rep('''  out[5] = "  /cast swap = swap your two primaries (out of combat). Hytale 0.7 brings real ability keys.";''',
    '''  out[5] = "  /cast swap = swap your two primaries, /cast page = the Abilities page (out of combat). Sprinting, in the air or crouched changes the shape. Hytale 0.7 brings real ability keys.";''')
rep('''  if (a.equals("reset")) {
    int n = @PKG@.AbilStore.clearCd(k);''', '''  if (a.equals("picka") || a.equals("pickb")) {   // 0.1.18: the Ability 1 alt pick for a player (testing)
    int ci = @PKG@.ClassStore.classIndex(t);
    if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) { send(pr, "That player has no class with abilities.", "#ffc800"); return "noclass"; }
    send(pr, setPick(k, ci, a.equals("pickb") ? "B" : "A") + " (" + t + ")", "#8fe39a");
    return a;
  }
  if (a.equals("reset")) {
    int n = @PKG@.AbilStore.clearCd(k);''')
rep('''    send(pr, "Last cast on this server: " + LAST, null);''',
    '''    send(pr, "Last cast on this server: " + LAST + " | last landing: " + LAST_LAND + " | Guardian Spirit saves: " + SAVES + " (last: " + LAST_GUARD + ")", null);''')
rep('''  send(pr, "Usage: /classadmin abil <player|uuid> <grant|ungrant|reset|info>", "#ffc800");
  return "usage";''', '''  send(pr, "Usage: /classadmin abil <player|uuid> <grant|ungrant|reset|info|pickA|pickB>", "#ffc800");
  return "usage";''')

# ================================================================================================ FIX 2: /class -> Abilities (plan R7 check 1)
# The /class footer row = [the slot] [Abilities] [Close]: the slot gives up one button + gap; a class without abilities (or no class) gets an
# empty spacer there, so Close never moves. The button opens the Abilities page (AbilPage.open - compiled earlier: methods before callers).
rep('''    slot_w = W - CLS_CLOSE_GAP - SUI.BTN_MIN_W                          # the footer slot left of Close
    assert SUI.fit([slot_w, CLS_CLOSE_GAP, SUI.BTN_MIN_W], W, "footer row") == 0''',
    '''    slot_w = W - 2 * CLS_CLOSE_GAP - 2 * SUI.BTN_MIN_W                  # the footer slot left of Abilities + Close (0.1.18)
    assert SUI.fit([slot_w, CLS_CLOSE_GAP, SUI.BTN_MIN_W, CLS_CLOSE_GAP, SUI.BTN_MIN_W], W, "footer row") == 0''')
rep('''        "CLOSE": SUI.java_append(bottom, close),''',
    '''        "CLOSE": SUI.java_append(bottom, close),
        # 0.1.18: the Abilities button (Mage / Priest) or an empty spacer of its size
        "ABIL": SUI.java_append(bottom, SUI.button("SkyyClsAbil", "Abilities", "secondary", w=SUI.BTN_MIN_W,
                                                   anchor={"left": CLS_CLOSE_GAP, "top": (CLS_END_H - SUI.BTN_H) // 2})),
        "ABILGAP": SUI.java_append(bottom, SUI.group("SkyyClsAbilGap", "Left", w=SUI.BTN_MIN_W, h=SUI.BTN_H,
                                                     anchor={"left": CLS_CLOSE_GAP, "top": (CLS_END_H - SUI.BTN_H) // 2})),''')
rep('''              "INFO": 4, "FOOTNF": 4, "FOOTLF": 4, "FOOT": 4, "CLOSE": 2}''',
    '''              "INFO": 4, "FOOTNF": 4, "FOOTLF": 4, "FOOT": 4, "CLOSE": 2, "ABIL": 4, "ABILGAP": 4}''')
rep('''{{CLOSE}}
  ev.addEventBinding(@BT@.Activating, "#SkyyClsClose", @EVD@.of("a", "clsclose"));
}"""''', '''  if (cur >= 0 && @PKG@.AbilDefs.classHas(cur) && @PKG@.ClassDefs.ENABLED[cur]) {   // 0.1.18: /class -> Abilities
{{ABIL}}
    ev.addEventBinding(@BT@.Activating, "#SkyyClsAbil", @EVD@.of("a", "clsabil"));
  } else {
{{ABILGAP}}
  }
{{CLOSE}}
  ev.addEventBinding(@BT@.Activating, "#SkyyClsClose", @EVD@.of("a", "clsclose"));
}"""''')
rep(r'''    if (data.indexOf("clsclose\"") >= 0) { close(); return; }   // 0.1.9: the footer Close - before the profile gates (everyone may close)''',
    r'''    if (data.indexOf("clsclose\"") >= 0) { close(); return; }   // 0.1.9: the footer Close - before the profile gates (everyone may close)
    if (data.indexOf("clsabil\"") >= 0) { @PKG@.AbilPage.open(this.playerRef, st, ref); return; }   // 0.1.18: the Abilities button''')

# ================================================================================================ the HUD bridge: Object[48], alts' costs = crouch shape
rep('''    Object[] out = new Object[44];   // 0.1.17: [0-15] as 0.1.16; the rest = the R2 widget's data (tools/classes_0_1_17_patch.py)''',
    '''    Object[] out = new Object[48];   // 0.1.17: [0-15] as 0.1.16; the rest = the R2 widget's data (tools/classes_0_1_17_patch.py); 0.1.18: + [44-47]''')
rep('''      double mc = ai < 0 ? 0.0 : @PKG@.AbilDefs.mana(ai);
      double sc = ai < 0 ? 0.0 : @PKG@.AbilDefs.stamina(ai);''', '''      int shi = i >= 2 && @PKG@.AbilCfg.SHAPES ? 3 : 0;   // 0.1.18: an alt is always cast in its crouch shape
      double mc = ai < 0 ? 0.0 : @PKG@.AbilDefs.mana(ai, shi);
      double sc = ai < 0 ? 0.0 : @PKG@.AbilDefs.stamina(ai, shi);''')
rep('''    out[33] = @PKG@.ClassDefs.NAMES[ci];
    out[37] = "abil2";''', '''    out[33] = @PKG@.ClassDefs.NAMES[ci];
    out[37] = "abil2";
    String shn = "walk";   // 0.1.18: the shape a primary key would fire now (from the world-thread sample)
    if (smp != null && smp.length >= 7 && @PKG@.AbilCfg.SHAPES) {   // FIX 2: + the player's /settings switches, crouch in the air ignored
      boolean inAir = smp[6] > 0.5;
      if (inAir && @PKG@.AbilCfg.SHAPES_AIR && @PKG@.ClassCfg.notifyOn(u, "classes.abilAir")) shn = "air";
      else if (!inAir && smp[2] > 0.5) shn = "crouch";
      else if (smp[5] > 0.5 && @PKG@.AbilCfg.SHAPES_SPRINT && @PKG@.ClassCfg.notifyOn(u, "classes.abilSprint")) shn = "sprint";
    }
    out[44] = shn;
    out[45] = Boolean.valueOf(@PKG@.AbilCfg.SHAPES);
    out[46] = "abil3";''')
rep('''    @PKG@.AbilStore.SAMPLE.put(u, new double[] { mana, stam, crouching(acc, r) ? 1.0 : 0.0, creative(acc, r) ? 1.0 : 0.0, (double) now });''',
    '''    @PKG@.AbilStore.SAMPLE.put(u, new double[] { mana, stam, crouching(acc, r) ? 1.0 : 0.0, creative(acc, r) ? 1.0 : 0.0, (double) now,
      sprinting(acc, r) ? 1.0 : 0.0, airNow(acc, r, u, now) ? 1.0 : 0.0 });   // 0.1.18: + sprinting, in the air''')
# sample() calls sprinting / airNow, which are added further down now: sample moves below them too
OLD_SAMPLE = cut_method("abil", "public static void sample(@REF@ r, @CAC@ acc, long now) {")
rep(_P, OLD_SAMPLE + "\n" + _P)

# ================================================================================================ AbilTick: + the movement tracking; AbilShieldSys: + Guardian Spirit
rep('''  try {
    if (chunk != null && !@PKG@.AbilStore.WANT.isEmpty()) @PKG@.Abil.sample(chunk.getReferenceTo(idx), cb, System.currentTimeMillis());   // 0.1.17: the HUD sample
  } catch (Throwable t0) { }''', '''  try {
    if (chunk != null) {
      long now0 = System.currentTimeMillis();
      @REF@ r0 = chunk.getReferenceTo(idx);
      @PKG@.Abil.track(r0, cb, now0);                                              // 0.1.18: crouch / air since (the shape resolver)
      if (!@PKG@.AbilStore.WANT.isEmpty()) @PKG@.Abil.sample(r0, cb, now0);       // 0.1.17: the HUD sample
    }
  } catch (Throwable t0) { }''')
rep('''    if (!(ev instanceof @DMG@) || chunk == null) return;
    if (@PKG@.AbilWorld.BY.isEmpty()) return;
    @PKG@.Abil.shield(st, buf, chunk.getReferenceTo(idx), (@DMG@) ev, System.currentTimeMillis());''', '''    if (!(ev instanceof @DMG@) || chunk == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    long now = System.currentTimeMillis();
    if (!@PKG@.AbilWorld.BY.isEmpty()) @PKG@.Abil.shield(st, buf, r, (@DMG@) ev, now);
    @PKG@.Abil.guard(st, buf, r, (@DMG@) ev, now);   // 0.1.18: Guardian Spirit - LAST (after armour, the sanctuary, the bubble, the barrier)''')

# ================================================================================================ AbilFrostSys (the Inspect group: a landed hit breaks a freeze)
rep('''abshieldu = pool.makeClass(PKG + ".AbilShieldSysU", abshield)
C(abshieldu, "public AbilShieldSysU() { super(false); }")''', '''abshieldu = pool.makeClass(PKG + ".AbilShieldSysU", abshield)
C(abshieldu, "public AbilShieldSysU() { super(false); }")
# ---- 0.1.18 AbilFrostSys: DamageEventSystem in the INSPECT group (the hit really landed): a hit on a Frost Nova-frozen mob after its break time
# ends the freeze (the nova's own damage never does). Fast exit while nothing is frozen.
abfrost = pool.makeClass(PKG + ".AbilFrostSys", pool.get(T["DES"]))
F(abfrost, "public static boolean FAILED_ONCE = false;")
C(abfrost, "public AbilFrostSys() { super(); }")
M(abfrost, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(abfrost, "public @SG@ getGroup() { return @DMOD@.get().getInspectDamageGroup(); }")
M(abfrost, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@) || chunk == null || @PKG@.AbilStore.FROZEN.isEmpty()) return;
    @PKG@.Abil.frostHit(buf, chunk.getReferenceTo(idx), (@DMG@) ev, System.currentTimeMillis());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ClassCfg.warn("Frost Nova: the freeze-break hook failed (logged once, freezes then run their full time): " + t); }
  }
}""")''')

# ================================================================================================ THE ABILITIES PAGE (part 1: class, ctor, open)
# AbilPage = an inline CustomUIPage (vanilla look, tools/skyyui.py): its constructor + the static open() exist before CastArgCmd compiles
# (methods before callers); build() / handleDataEvent() are added after the shared SKYY CARD helpers (further down).
rep('''# ---- /cast (player): bare = the list; the usage variant takes one word (HANDOFF COMMAND RULES 2: a variant per positional form)''',
    '''# ---- 0.1.18 AbilPage (part 1): the class, its state, the constructor, open() - build() comes after the card helpers
abpage = pool.makeClass(PKG + ".AbilPage", pool.get(T["PAGE"]))
F(abpage, "public int pending;")      # the card picked with Move (-1 = none)
F(abpage, "public boolean pick;")     # the Ability 1 alt switch is waiting for Confirm
F(abpage, "public String info;")
C(abpage, r"""
public AbilPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.pending = -1;
  this.pick = false;
  this.info = "";
}""")
M(abpage, r"""
public static void open(@PR@ pr, @ST@ st, @REF@ ref) {
  @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (player == null) return;
  player.getPageManager().openCustomPage(ref, st, new @PKG@.AbilPage(pr));
}""")
M(abpage, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\'', ' ').replace('\\\\', ' ');
}""")
# a card's line two: the cost of the shape the slot casts (an alt = its crouch shape), the unlock, or the passive
M(abpage, r"""
public static String costLine(int ai, int slot, boolean own, int ci) {
  if (ai < 0) return "Empty";
  if (!own) return "Unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]);
  if (@PKG@.AbilDefs.PASSIVE[ai]) return "Passive - always on - " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.GS_MANA) + " Mana + " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.GS_STAM) + " Stamina a save";
  int sh = slot >= 2 && @PKG@.AbilCfg.SHAPES ? 3 : 0;
  return (sh == 3 ? @PKG@.AbilDefs.sname(ai, 3) + " (crouch) - " : "") + @PKG@.AbilMath.fmt(@PKG@.AbilDefs.mana(ai, sh)) + " Mana + "
    + @PKG@.AbilMath.fmt(@PKG@.AbilDefs.stamina(ai, sh)) + " Stamina - cooldown " + @PKG@.AbilMath.secs(@PKG@.AbilDefs.cdMs(ai, sh)) + " s";
}""")
# ---- /cast (player): bare = the list; the usage variant takes one word (HANDOFF COMMAND RULES 2: a variant per positional form)''')
rep('''    if (a.equals("swap")) { @PKG@.Abil.swap(pr); return; }''', '''    if (a.equals("swap")) { @PKG@.Abil.swap(pr); return; }
    if (a.equals("page")) { @PKG@.AbilPage.open(pr, store, ref); return; }   // 0.1.18: the Abilities page''')
rep('''  super("Cast a class ability: /cast 1 or 2 (crouch = your alt), /cast 3 or 4 (alts), /cast list, /cast swap");''',
    '''  super("Cast a class ability: /cast 1 or 2 (crouch = your alt), /cast 3 or 4 (alts), /cast list, /cast swap, /cast page");''')
rep('''  this.slotArg = withRequiredArg("slot", "1 | 2 (crouch = alt) | 3 | 4 | list | swap", @ATY@.STRING);''',
    '''  this.slotArg = withRequiredArg("slot", "1 | 2 (crouch = alt) | 3 | 4 | list | swap | page", @ATY@.STRING);''')
rep('''  super("cast", "Cast a class ability: /cast 1 or /cast 2 (crouch = your alt), /cast 3 or 4 = alts, /cast list, /cast swap");''',
    '''  super("cast", "Cast a class ability: /cast 1 or /cast 2 (crouch = your alt), /cast 3 or 4 = alts, /cast list, /cast swap, /cast page");''')

# ================================================================================================ /classadmin shape (admin sub-command)
rep('''# ================= 0.1.6 KitHooks (config kit hooks: check= of the kit rows, the 7 "Use my hotbar" actions) + KitHotbarTask =================''',
    '''# ---- 0.1.18 /classadmin shape <1|2|3|4> <walk|sprint|air|crouch> (requirePermission + empty groups: the AdminAbilCmd pattern)
ashape = pool.makeClass(PKG + ".AdminShapeCmd", pool.get(T["APC"]))
F(ashape, "public @RA@ slotArg;")
F(ashape, "public @RA@ shapeArg;")
C(ashape, r"""
public AdminShapeCmd() {
  super("shape", "(admin) Cast as yourself with a forced shape: /classadmin shape <1|2|3|4> <walk|sprint|air|crouch>");
  requirePermission("skyyclasses.admin");
  setPermissionGroups(new String[0]);
  this.slotArg = withRequiredArg("slot", "1 | 2 (primaries) | 3 | 4 (alts)", @ATY@.STRING);
  this.shapeArg = withRequiredArg("shape", "walk | sprint | air | crouch", @ATY@.STRING);
}""")
M(ashape, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.Abil.adminShape(pr, store, ref, world, String.valueOf(ctx.get(this.slotArg)), String.valueOf(ctx.get(this.shapeArg))); }
  catch (Throwable t) { pr.sendMessage(@MSG@.raw("[Classes] Usage: /classadmin shape <1|2|3|4> <walk|sprint|air|crouch>")); }
}""")

# ================= 0.1.6 KitHooks (config kit hooks: check= of the kit rows, the 7 "Use my hotbar" actions) + KitHotbarTask =================''')
rep('''  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | kit <player> [class] | abil <player> <action> | reload");''',
    '''  super("classadmin", "(admin) /classadmin set <player> <class> | reset <player> | info <player> | kit <player> [class] | abil <player> <action> | shape <slot> <shape> | reload");''')
rep('''  addSubCommand(new @PKG@.AdminAbilCmd());   // 0.1.16''', '''  addSubCommand(new @PKG@.AdminAbilCmd());   // 0.1.16
  addSubCommand(new @PKG@.AdminShapeCmd());  // 0.1.18''')
rep('''  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | kit <player|uuid> [class] | abil <player|uuid> <grant|ungrant|reset|info> | reload"));''',
    '''  pr.sendMessage(@MSG@.raw("[Classes] /classadmin set <player|uuid> <class> | reset <player|uuid> | info <player|uuid> | kit <player|uuid> [class] | abil <player|uuid> <grant|ungrant|reset|info|pickA|pickB> | shape <1-4> <walk|sprint|air|crouch> | reload"));''')

# ================================================================================================ THE ABILITIES PAGE (part 2: build + events, after the card helpers)
AB_PAGE_PY = r'''
# ================= 0.1.18 AbilPage (part 2): /cast page - the Abilities page (research/cloud/Ability-Engine-Plan.md R7). The SKYY CARD list
# (5 cards: your 4 slots + the Ability 1 alt choice) in the vanilla window, the footer row (in-page confirm / result line / hint) + Close.
# Move a card, then "Swap here" on another = swap the two slots (pick your 2 primaries and their key order; both unlocked). Everything only
# out of combat (skill:fn:combat). Nothing closes / opens another page (HANDOFF section 2).
AB_W = CLS_W
AB_PREFIX = "SkyyAb"
AB_SUB_H, AB_SUB_GAP = 26, 8
AB_END_TOP, AB_END_H = 8, SUI.BTN_H + 16
AB_CARDS = 5
AB_BUILD = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int ci = @PKG@.ClassStore.classIndex(u);
  boolean has = ci >= 0 && @PKG@.AbilDefs.classHas(ci) && @PKG@.ClassDefs.ENABLED[ci];
  String k = @PKG@.ClassCfg.pkey(u);
  int lv = has ? @PKG@.Abil.level(u, ci) : 0;
  boolean grant = has && @PKG@.AbilStore.granted(k);
  String pk = has ? @PKG@.AbilStore.pick(k) : "A";
  String[] sl = new String[] { "", "", "", "" };
  if (has) sl = @PKG@.AbilStore.slots(k, ci);
  boolean fight = has && @PKG@.Abil.combatMs(u) > 0L;
  long altLv = @PKG@.AbilDefs.unlock(3);
  boolean canPick = has && (grant || (long) lv >= altLv);
{{SHELL}}
  String sub = !has ? (ci < 0 ? @PKG@.Abil.noClass() : @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first.")
    : @PKG@.ClassDefs.NAMES[ci] + " - " + @PKG@.ClassDefs.SKILLS[ci] + " " + lv + ". The top 2 cards are your primaries (/cast 1 and /cast 2) - crouch + the key casts the alt.";
  if (fight) sub = "You are in combat - leave combat to change your abilities.";
{{SUB}}
{{LIST}}
  for (int i = 0; i < 5; i++) {
    int ai = -1;
    boolean own = false;
    String title = "";
    String l2 = "";
    String l3 = "";
    if (i < 4) {
      ai = has ? @PKG@.AbilDefs.find(sl[i]) : -1;
      own = ai >= 0 && @PKG@.AbilDefs.owns(ai, lv, grant, pk);
      title = (ai < 0 ? "-" : @PKG@.AbilDefs.NAMES[ai]) + " - " + @PKG@.AbilDefs.slotText(i);
      l2 = has ? @PKG@.AbilPage.costLine(ai, i, own, ci) : "";
      l3 = ai < 0 ? "" : @PKG@.AbilDefs.DESCS[ai];
    } else {
      int pa = has ? @PKG@.AbilDefs.of(ci, @PKG@.AbilDefs.pickTier(pk)) : -1;
      int pb = has ? @PKG@.AbilDefs.of(ci, @PKG@.AbilDefs.pickTier(pk.equals("B") ? "A" : "B")) : -1;
      own = canPick;
      title = "Ability 1 alt - " + (pa < 0 ? "-" : @PKG@.AbilDefs.NAMES[pa]) + (canPick ? "" : " (choose at " + (has ? @PKG@.ClassDefs.SKILLS[ci] : "level") + " " + altLv + ")");
      l2 = pb < 0 ? "" : "The other choice is " + @PKG@.AbilDefs.NAMES[pb] + " - picking one locks out the other (switch back here any time).";
      l3 = pb < 0 ? "" : @PKG@.AbilDefs.DESCS[pb];
    }
    boolean pend = i == this.pending;
    boolean on = has && own;
    String ic = has ? @PKG@.ClassDefs.ICONS[ci].split(",")[0] : "Weapon_Sword_Crude";
{{CARD}}
    if (!has || (!own && i < 4)) {
{{LOCKED}}
    } else if (fight) {
{{FIGHT}}
    } else if (i == 4) {
      if (!canPick) {
{{LOCKED}}
      } else {
{{PICK}}
        ev.addEventBinding(@BT@.Activating, "#SkyyAbMove" + i, @EVD@.of("a", "abpick"));
      }
    } else if (pend) {
{{CANCEL}}
      ev.addEventBinding(@BT@.Activating, "#SkyyAbMove" + i, @EVD@.of("a", "abmove" + i));
    } else if (this.pending >= 0) {
{{HERE}}
      ev.addEventBinding(@BT@.Activating, "#SkyyAbMove" + i, @EVD@.of("a", "abmove" + i));
    } else {
{{MOVE}}
      ev.addEventBinding(@BT@.Activating, "#SkyyAbMove" + i, @EVD@.of("a", "abmove" + i));
    }
  }
{{BOTTOM}}
  boolean said = this.info != null && this.info.length() > 0;
  if (has && this.pick && canPick && !fight) {
    int na = @PKG@.AbilDefs.of(ci, @PKG@.AbilDefs.pickTier(pk));
    int nb = @PKG@.AbilDefs.of(ci, @PKG@.AbilDefs.pickTier(pk.equals("B") ? "A" : "B"));
    String q = "Switch your Ability 1 alt to " + (nb < 0 ? "-" : @PKG@.AbilDefs.NAMES[nb]) + "? " + (na < 0 ? "" : @PKG@.AbilDefs.NAMES[na] + " is then locked out.");
{{CONFIRM}}
    ev.addEventBinding(@BT@.Activating, "#SkyyAbYes", @EVD@.of("a", "abyes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyAbNo", @EVD@.of("a", "abno"));
  } else if (said) {
{{INFO}}
  } else {
    String foot = "Move a card then Swap here on another to trade their places. Changes only out of combat. With Hytale 0.7 the keys become your ability keys.";
{{FOOT}}
  }
{{CLOSE}}
  ev.addEventBinding(@BT@.Activating, "#SkyyAbClose", @EVD@.of("a", "abclose"));
}"""


def abil_page_java():
    """AbilPage.build(): AB_BUILD with its {{parts}} from kit calls (the ClassPage recipe; the body is filled exactly)."""
    heights = [AB_SUB_H + AB_SUB_GAP, card_list_h(AB_CARDS), AB_END_TOP + AB_END_H]
    sh = SUI.page_shell("SkyyAbF", AB_W, SUI.TITLE_H + 2 * SUI.CONTENT_PAD + sum(heights), "Abilities", body_id="SkyyAb")
    assert sh.fit(heights) == 0, "the abilities page body must be filled exactly: %s in %d px" % (heights, sh.inner_h)
    body, W = sh.body, sh.inner_w
    slot_w = W - CLS_CLOSE_GAP - SUI.BTN_MIN_W
    assert SUI.fit([slot_w, CLS_CLOSE_GAP, SUI.BTN_MIN_W], W, "footer row") == 0
    i = SUI.J("i")
    act = "SkyyAbAct" + i
    btn = "SkyyAbMove" + i
    ids = {"list": "SkyyAbList", "card": "SkyyAbCard" + i, "icons": "SkyyAbIco" + i, "text": "SkyyAbTxt" + i, "act": act}
    lines = [{"id": "Nm", "text": "safe(title)", "kind": "rowName", "h": 24, "col": "rowName"},
             {"id": "Co", "text": "safe(l2)", "kind": "fieldLabel", "h": 20, "col": "value"},
             {"id": "Ds", "text": "safe(l3)", "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}]
    bottom = "SkyyAbBottom"
    info = SUI.label("SkyyAbInfo", "", "info", w=slot_w, h=AB_END_H, bold=True, wrap=True)
    foot = SUI.label("SkyyAbFoot", "", "caption", w=slot_w, h=AB_END_H, wrap=True)
    confirm = SUI.confirm_view(bottom, "SkyyAbConfirm", slot_w, question=SUI.J("safe(q)"), compact=True, top=0, wrap=True,
                               ids={"box": "SkyyAbConfirm", "yes": "SkyyAbYes", "no": "SkyyAbNo"})
    assert confirm.h == AB_END_H, "the compact confirm row must be the footer slot's height (%d / %d)" % (confirm.h, AB_END_H)
    close = SUI.button("SkyyAbClose", "Close", "secondary", w=SUI.BTN_MIN_W, sound="cancel",
                       anchor={"left": CLS_CLOSE_GAP, "top": (AB_END_H - SUI.BTN_H) // 2})
    mage_icon = [c for c in CLASSES if c["name"] == "Mage"][0]["icons"][0]
    parts = {
        "SHELL": sh.java("b"),
        "SUB": "\n".join([SUI.java_append(body, SUI.label("SkyyAbSub", "", "default", h=AB_SUB_H, align="Center", anchor={"bottom": AB_SUB_GAP})),
                          SUI.java_set("SkyyAbSub", "Text", SUI.J("safe(sub)"))]),
        "LIST": SUI.java_append(body, card_list("SkyyAbList", card_list_h(AB_CARDS))),
        "CARD": card_java(ids, W - 2 * CARD_LIST_PAD, [("pending", "pend"), ("normal", "on"), "off"], lines, icons=None,
                          icon_item=SUI.J("safe(ic)", mage_icon), icon_max=1, on="on"),
        "LOCKED": SUI.java_append(act, card_state("Locked", "disabled")),
        "FIGHT": SUI.java_append(act, card_state("In combat", "disabled")),
        "PICK": SUI.java_append(act, card_button(btn, "Switch")),
        "CANCEL": SUI.java_append(act, card_button(btn, "Cancel", "primary")),
        "HERE": SUI.java_append(act, card_button(btn, "Swap here", "primary")),
        "MOVE": SUI.java_append(act, card_button(btn, "Move")),
        "BOTTOM": SUI.java_append(body, SUI.group(bottom, "Left", h=AB_END_H, anchor={"top": AB_END_TOP})),
        "CONFIRM": confirm.java("b"),
        "INFO": "\n".join([SUI.java_append(bottom, info), SUI.java_set("SkyyAbInfo", "Text", SUI.J("safe(this.info)"))]),
        "FOOT": "\n".join([SUI.java_append(bottom, foot), SUI.java_set("SkyyAbFoot", "Text", SUI.J("safe(foot)"))]),
        "CLOSE": SUI.java_append(bottom, close),
    }
    sh.appends.check(AB_PREFIX)
    indent = {"SHELL": 2, "SUB": 2, "LIST": 2, "CARD": 4, "LOCKED": 6, "FIGHT": 6, "PICK": 8, "CANCEL": 6, "HERE": 6, "MOVE": 6, "BOTTOM": 2,
              "CONFIRM": 4, "INFO": 4, "FOOT": 4, "CLOSE": 2}
    java = java_fill(AB_BUILD, dict((k, java_block(v, indent[k])) for k, v in parts.items()))
    for ident in ("SkyyAbSub", "SkyyAbList", "SkyyAbBottom", "SkyyAbInfo", "SkyyAbFoot", "SkyyAbConfirm", "SkyyAbYes", "SkyyAbNo", "SkyyAbClose"):
        assert ("#%s {" % ident) in java, "the abilities page lost #" + ident
    assert "_" not in "".join(re.findall(r"#(SkyyAb\w*)", java)), "no underscores in element ids (HANDOFF section 2)"
    return java, sh


AB_BUILD_JAVA, AB_SHELL = abil_page_java()
print("abilities page %dx%d (body %dx%d): %d cards %d px high, footer confirm / info + Close, kit %s" % (
    AB_SHELL.w, AB_SHELL.h, AB_SHELL.inner_w, AB_SHELL.inner_h, AB_CARDS, CARD_H, SUI.kit_id()))
M(abpage, AB_BUILD_JAVA)
M(abpage, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("abclose\"") >= 0) { close(); return; }
    java.util.UUID u = this.playerRef.getUuid();
    int ci = @PKG@.ClassStore.classIndex(u);
    if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) {
      this.pending = -1;
      this.pick = false;
      this.info = ci < 0 ? @PKG@.Abil.noClass() : "Your class has no abilities yet.";
      rebuild(); return;
    }
    if (@PKG@.Abil.combatMs(u) > 0L) {
      this.pending = -1;
      this.pick = false;
      this.info = "Leave combat first - abilities change only out of combat.";
      rebuild(); return;
    }
    String k = @PKG@.ClassCfg.pkey(u);
    for (int i = 0; i < 4; i++) {
      if (data.indexOf("abmove" + i + "\"") < 0) continue;
      this.pick = false;
      if (this.pending == i) { this.pending = -1; this.info = ""; rebuild(); return; }
      if (this.pending < 0) {
        String[] sl = @PKG@.AbilStore.slots(k, ci);
        int ai = @PKG@.AbilDefs.find(sl[i]);
        if (ai < 0 || !@PKG@.AbilDefs.owns(ai, @PKG@.Abil.level(u, ci), @PKG@.AbilStore.granted(k), @PKG@.AbilStore.pick(k))) {
          this.info = (ai < 0 ? "That slot" : @PKG@.AbilDefs.NAMES[ai]) + " is locked.";
          rebuild(); return;
        }
        this.pending = i;
        this.info = "Now press Swap here on the card to trade places with " + @PKG@.AbilDefs.NAMES[ai] + " (or Cancel).";
        rebuild(); return;
      }
      int p = this.pending;
      this.pending = -1;
      String r = @PKG@.Abil.swapSlots(u, p, i);
      this.info = r.startsWith("ok:") ? r.substring(3) : r;
      rebuild(); return;
    }
    if (data.indexOf("abpick\"") >= 0) {
      this.pending = -1;
      long need = @PKG@.AbilDefs.unlock(3);
      if (!@PKG@.AbilStore.granted(k) && (long) @PKG@.Abil.level(u, ci) < need) {
        this.info = "You choose your Ability 1 alt at " + @PKG@.ClassDefs.SKILLS[ci] + " " + need + ".";
        rebuild(); return;
      }
      this.pick = true;
      this.info = "";
      rebuild(); return;
    }
    if (data.indexOf("abyes\"") >= 0) {
      if (!this.pick) return;
      this.pick = false;
      this.info = @PKG@.Abil.setPick(k, ci, @PKG@.AbilStore.pick(k).equals("B") ? "A" : "B");
      rebuild(); return;
    }
    if (data.indexOf("abno\"") >= 0) { this.pick = false; this.info = ""; rebuild(); return; }
  } catch (Throwable t) { @PKG@.ClassCfg.warn("abilities page event failed: " + t); }
}""")
'''
rep('''# ================= OpenTask: first-join page open (SkyyHud AttachTask pattern: delay, world-thread hop, WorldMap channel gate) =================''',
    AB_PAGE_PY + '''
# ================= OpenTask: first-join page open (SkyyHud AttachTask pattern: delay, world-thread hop, WorldMap channel gate) =================''')

# ================================================================================================ wiring: quit, setup, jar
rep('''    @PKG@.AbilStore.WANT.remove(u);   // 0.1.17: the HUD sample (zones run on: a Mana Barrier ends at its next tick, the caster is gone)
    @PKG@.AbilStore.SAMPLE.remove(u);''', '''    @PKG@.AbilStore.WANT.remove(u);   // 0.1.17: the HUD sample (zones run on: a Mana Barrier ends at its next tick, the caster is gone)
    @PKG@.AbilStore.SAMPLE.remove(u);
    @PKG@.AbilStore.MOVE.remove(u);   // 0.1.18: the shape resolver's crouch / air times (GUARD stays: a relog must not reset the doubling)
    @PKG@.AbilStore.CHAN.remove(u);   // 0.1.18: a running Arcane Beam stops''')
rep('''    try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilShieldSysU()); } catch (Throwable t2) { @PKG@.ClassCfg.warn("could not register AbilShieldSysU - no Mana Barrier / Shield Bubble soaking this start: " + t2); }
  }
''', '''    try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilShieldSysU()); } catch (Throwable t2) { @PKG@.ClassCfg.warn("could not register AbilShieldSysU - no Mana Barrier / Shield Bubble soaking this start: " + t2); }
  }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilFrostSys()); }   // 0.1.18: a landed hit breaks a Frost Nova freeze (Inspect group)
  catch (Throwable t3) { @PKG@.ClassCfg.warn("could not register AbilFrostSys - Frost Nova freezes run their full time this start: " + t3); }
''')
rep('''  @PKG@.ClassCfg.regSetting("classes.abilChat", "Ability chat lines", "combat", true, "Meteor! -23 Mana, -2 Stamina and what it hit. Refusals (cooldown, not enough Mana) always show");''',
    '''  @PKG@.ClassCfg.regSetting("classes.abilChat", "Ability chat lines", "combat", true, "Meteor! -23 Mana, -2 Stamina and what it hit. Refusals (cooldown, not enough Mana) always show");
  @PKG@.ClassCfg.regSetting("classes.abilSprint", "Ability sprint shapes", "combat", true, "Casting while sprinting uses the sprint shape (Comet, Barrier Ahead ...). Off = the walking shape");   // 0.1.18
  @PKG@.ClassCfg.regSetting("classes.abilAir", "Ability mid-air shapes", "combat", true, "Casting in the air uses the mid-air shape (lands where you land). Off = the walking shape");''')
rep('''          abzone, abshield, abshieldu):   # 0.1.17: + the zone + its damage hook''',
    '''          abzone, abshield, abshieldu,   # 0.1.17: + the zone + its damage hook
          abfrost, ashape, abpage):      # 0.1.18: + the freeze-break hook, /classadmin shape, the Abilities page''')
rep('''class abilities with /cast (Mage Meteor + Mana Barrier, Priest Sacred Heal + Shield Bubble; crouch = your alts).''',
    '''class abilities with /cast (Mage Meteor, Mana Barrier, Frost Nova, Starfall or Arcane Beam; Priest Sacred Heal, Shield Bubble, the Guardian Spirit passive, Sanctuary or Martyr's Grace; sprinting, mid-air and crouch shapes; crouch = your alts; /cast page).''')
rep('''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyClasses] __VER__ ready (__KIT__) - /class, /class kit, /class arrows, /cast, /classadmin; classes "''',
    '''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyClasses] __VER__ ready (__KIT__) - /class, /class kit, /class arrows, /cast (+ /cast page), /classadmin; classes "''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0 + 1, "one AbilFrostSys, no new command (shape is a sub-command)"
for _cls in ("AbilFrostSys", "AdminShapeCmd", "AbilPage"):
    assert s.count('pool.makeClass(PKG + ".%s"' % _cls) == 1, _cls
# javassist order: helpers before callers (every moved method after what it calls; the page's open() before /cast page)
for a_, b_ in (("public static boolean airNow(", "public static String castAt("), ("public static double[] ahead(", "public static String castAt("),
               ("public static @PKG@.AbilJob landJob(", "public static String castAt("), ("public static String graceRun(", "public static String castAt("),
               ("public static int graceCount(", "public static String castAt("), ("public static @PKG@.AbilZone barrierAt(", "public static String castAt("),
               ("public static String castAt(", "public static String castNow("), ("public static String castNow(", "public static String cast(@PR@"),
               ("public static String land(", "public static boolean landTick("), ("public static boolean landTick(", "public static boolean runJob("),
               ("public static boolean starTick(", "public static boolean runJob("), ("public static boolean beamTick(", "public static boolean runJob("),
               ("public static String chanRun(", "public static boolean runJob("), ("public static int novaRun(", "public static boolean runJob("),
               ("public static boolean zoneTick2(", "public static boolean zoneTick("), ("public static boolean zoneTick(", "public void run(@ST@ st, @CB@ cb, long now)"),
               ("public static boolean runJob(", "public void run(@ST@ st, @CB@ cb, long now)"), ("public static String guard(", "@PKG@.Abil.guard(st, buf, r, (@DMG@) ev, now);"), ("public static void track(", "@PKG@.Abil.track(r0, cb, now0);"),
               ("public static boolean sprinting(", "public static void sample("), ("public static void sample(", "public void tick(float dt"),
               ("public static String frostHit(", "@PKG@.Abil.frostHit(buf"), ("public static void open(@PR@ pr, @ST@ st, @REF@ ref)", "@PKG@.AbilPage.open(pr, store, ref)"),
               ("public static String adminShape(", "@PKG@.Abil.adminShape(pr"), ("public AdminShapeCmd()", "addSubCommand(new @PKG@.AdminShapeCmd())"),
               ("public static String setPick(", "public static String adminDo("), ("public static String swapSlots(", "@PKG@.Abil.swapSlots(u, p, i)"),
               ("public static String costLine(", "@PKG@.AbilPage.costLine(ai, i, own, ci)"), ("def card_java(", "AB_BUILD_JAVA, AB_SHELL = abil_page_java()"),
               ("public static double manaOf(", "public static double mana(int ai, int sh)"), ("public static double mana(int ai, int sh)", "public static double mana(int ai) {"),
               ("public static int resolveAt(", "public static String castAt("), ("public static boolean bossRole(", "public static long stunClock("),
               # FIX 2
               ("public static boolean hasFx(", "public static int freezeOne("), ("public static boolean unfreeze(@CAC@ acc, @REF@ t, boolean stun)", "public static boolean unfreeze(@CAC@ acc, @REF@ t) {"),
               ("public static int freezeOne(@CAC@ acc, @REF@ t, java.util.UUID u, double secs, double brk, double chill, long now, double brkAmt)",
                "public static int freezeOne(@CAC@ acc, @REF@ t, java.util.UUID u, double secs, double brk, double chill, long now) {"),
               ("public static boolean breakHit(", "public static String frostHit("), ("public static boolean hit(@CB@", "public static boolean breakHit("),
               ("public static String guardKey(", "public static String guard("), ("public static void open(@PR@ pr, @ST@ st, @REF@ ref)", "@PKG@.AbilPage.open(this.playerRef, st, ref)")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_, b_)
for _gone in ("public static String castNow(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg) {\n  if (pr == null",):
    assert _gone not in s, "the 0.1.17 castNow body is still there"
assert s.count("public static String castNow(") == 1 and s.count("public static boolean runJob(") == 1 and s.count("public static String shield(") == 1 \
    and s.count("public static boolean zoneTick(") == 1 and s.count("public static String cast(@PR@") == 1 and s.count("public static void sample(") == 1
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.1.17 had %d; %d anchored changes + 6 moved methods)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
