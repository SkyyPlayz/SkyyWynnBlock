"""Derive SkyySkills/build_skyyskills_0.4.12.py from the LIVE generated SkyySkills/build_skyyskills_0.4.11.py (= the tools/deploy_set.py SET
pin; 0.4.11 came from 0.4.10 by tools/skills_0_4_11_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_11_patch.py: rep(old, new) / cut(a, b, new) with asserted single anchors,
newline-agnostic; 0.4.11 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_12_patch.py   then   python SkyySkills/build_skyyskills_0.4.12.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.12.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0412/, deleted afterwards)

0.4.12 = THE CLASS SKILL CURVE + MANA REGEN IN COMBAT (Skyy's Q&A 2026-10-02, OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02"):
  R1 LOCKED: "CLASS SKILL CURVE = the cloud proposal as written (research/cloud/Class-Skill-Curve-Proposal.md): a separate table for
  class skills only, XP per level = 50 x L + 0.25 x L^3 (rounded); ... never below today at any level (levels only go up); editable rows
  levels.class / .scale / .max / .sameAsOthers." + "gathering skills keep the Hypixel table for now".
  R1 / R2 LOCKED: "MANA REGEN IN COMBAT = HALF" - "Mana Regen boosts are PERCENT ("+20% Mana Regen"); in combat the WHOLE regen (vanilla +
  boosts) runs at 50% - one Server Setup row "In-combat Mana regen" (default 50%). Combat = vanilla's window (6 s after taking damage),
  where vanilla gives 0 - our mod supplies the regen there."

PART 1 - CLASS SKILL CURVE
  1. THE TABLE: XP for level L = round(50 x L + 0.25 x L^3) to a step of 10 below 1,000, 50 below 10,000, 500 below 100,000, 5,000
     above (step picked on the unrounded value; round half to even = Python's round(), the proposal's own rounding: level 70 = 89,000).
     The proposal's section 5 table is the reference: this patch reads research/cloud/Class-Skill-Curve-Proposal.md and asserts its 100
     "XP for level" numbers + totals + old totals against CLASS_LEVELS_REF; the generated build script embeds CLASS_LEVELS_REF and asserts
     the formula reproduces it, that every cumulative total is at or below the 0.4.11 table (LEVELS) at every level 1-100, and the
     proposal's section 2 totals (10: 3,510 / 20: 21,540 / 30: 77,290 / 40: 209,090 / 60: 929,090 / 100: 6,627,590).
  2. PER-SLOT LEVELS (proposal section 6 check 1/3): SkillStore keeps TOTAL XP per slot (players/<pkey>.properties <Name>=xp, <Name>.paid
     = the highest PAID level) - the level was always derived from the total through ONE global table (SkillDefs.PER / CUM). The global
     levelOf(long) / intoLevel(long) / needFor(long) / progress(long) are GONE (javassist refuses a leftover call, so nothing can keep the
     old global lookup); every level now comes from SkillDefs.levelOf(slot, total) / intoLevel / needFor / progress(slot, total) /
     maxOf(slot) / cumOf(slot): class slots (SkillDefs.isClass: Archery, Swordsmanship, Assassination, Shaman skill, Sorcery, Fury,
     Divinity) use the CLASS table, every other slot (gathering, Acrobatics, Alchemy, Smithing, Cooking, Exploration, the legacy Combat
     slot) the general table exactly as 0.4.11. Sites: SkillStore (readFile's default paid marker, level, levelsOf = skill:<uuid>, addK,
     owesK, payLocked = the level-up coin rewards), SkillXp.gain4 (level-up lines / next / MAX), SkillMsg + PartyXp chat (progress),
     Overall (sums, listText, the new maxLevel, nextLines), the /skills page rows + its Top 10 view, the Stats page, the Overall page,
     /skills top, the legacy Combat move line. Through them: skill:fn:level, skill:<uuid> (SkyyHud widget, SkyyGuilds' level fallback),
     skill:fn:overall + skill:overall:<uuid>, every perk (health / damage per class level, the crossbow perk level). skill:fn:xp still
     answers the TOTAL XP (unchanged), so SkyyGuilds' guild XP (it sums skill:fn:xp) and SkyyTrees' Dust do not move.
  3. LEVELS ONLY GO UP (the guard "level = max(old, new)"): the effective class table SkillDefs.ECUM[L] = min(class total[L], general
     total[L]) for L up to the class max (recomputed whenever either table changes), so a class level is ALWAYS max(level on the general
     table, level on the class table) - capped only by the admin's own class max level. With the default tables ECUM = the class table
     (asserted: it is at or below the general one everywhere). levels.class.sameAsOthers = the general table itself (0.4.11 behaviour).
  4. ROWS (Server Setup -> Skills -> Levels, after the three existing curve rows, whose labels / help now say "other skills"):
       levels.class              Class skill XP per level (list)   text, the class table, live,danger,adv, check=SkillKit.checkLevels
       levels.class.scale        Class level curve size            int % 10-1000, custom:SkillKit (relative to the default class table)
       levels.class.max          Class max level                   int 1-100, custom:SkillKit (cuts / extends along the class curve;
                                                                   cut levels come back exactly until a restart - own TAIL memory)
       levels.class.sameAsOthers Class skills use the other list   bool, false, live,danger (confirm=on: switching it on drops levels)
     The default file gets the "Class skill levels" block at the end; an existing file without levels.class gets it appended ONCE (the
     ensureX pattern every SkyySkills block used since 0.2, in the file's own line ending; nothing existing is rewritten - no value of an
     existing key changes in 0.4.12, so no History / Undo migration is needed). A file holding levels.class.sameAsOthers but no
     levels.class gets only the list line (an admin's switch is never overwritten).
  5. EXISTING XP + REWARDS (proposal section 3): no player data is rewritten (levels are derived). ClassCurve (new class): at the FIRST
     start of 0.4.12 (no Skyy_SkyySkills/class-curve.properties yet) setup() scans every players/*.properties once, read-only: a class
     slot whose level on the class table is above its level on the general table (= what 0.4.11 showed) is recorded as
     pending.<profile key>=<slot>:<old>:<new> in class-curve.properties (written atomically; no deliveries until it is on disk - else
     WARN and the next start scans again). Later starts only read the file. The first time that profile plays (1 s Perks tick, world
     thread; also before a class skill XP award in SkillXp.gain4; never while profile:busy or in Overall's session hold): ONE chat line
     "[Skills] Class skill curve updated: Divinity is now level 28 (was 15) - +28.6k coins for levels 16 to 28", the level-up coin
     rewards of the gained levels through the normal paid marker (SkillStore.payOwedK - exactly once: the marker only moves after
     SkyyCoins paid, so a later gain / restart never pays them again), the Overall level up (chat + heal, once), the crossbow unlock line
     when Archery passes its unlock level, a republish; the entry becomes done.<profile key>=<time> <summary>. The file is rewritten on
     the 1 s ticker (shutdown too) AFTER the delivered profiles' player files are saved, so "done" is never on disk before their paid
     markers. Start twice = once (the record); the live world has nobody to tell (Skyy's class XP 420 / 384 / 20 are the same level on
     both tables), checked by the harness on a scratch copy.

PART 2 - MANA REGEN IN COMBAT (research/Mana-Cost-And-Regen-Research.md 2.1-2.3)
  Vanilla Mana.json: every 0.2 s +1 Additive while Alive, NoDamageTaken (6 s) and not Charging = 5 per second out of combat, 0 for 6 s
  after taking damage, 0 while holding a charge. ManaRegen (new class) runs inside AcroSys.tick (world thread, every tick, own 0.2 s
  clock): for each positive Additive regen entry of the player's Mana value it evaluates the entry's own engine conditions
  (Condition.eval, the check RegeneratingValue.shouldRegenerate makes; the engine timers are never advanced - the SkyyAccessories 0.5
  Stamina Regen pattern): all pass = OUT OF COMBAT (vanilla adds the rate itself), only NoDamageTaken fails = IN COMBAT (vanilla's pause),
  anything else (charging, dead) = nothing. Then
      out of combat  SkyySkills adds  rate x MR / 100                       (the boost part on top of vanilla's own refill)
      in combat      SkyySkills adds  rate x (1 + MR / 100) x F / 100       (vanilla gives 0 there)
  MR = the player's Mana Regen % (sum of every source registered on skill:fn:manaregen; below 0 counts 0, at most 1000), F = the new row
  mana.regen.inCombat (Server Setup -> Skills -> Overall and Mana -> "In-combat Mana regen", int %, 0-100, default 50; 0 = vanilla).
  Never above max Mana; nothing at max Mana 0 ("classes without Mana": a player with no Mana pool - mana.base / Base Mana by class 0 -
  gets nothing). At the defaults with no boosts: 2.5 Mana per second in combat, out of combat exactly vanilla.
  BRIDGE skill:fn:manaregen = Function apply(Object[]) (java.lang types; memory only - providers register live, like move:<uuid>):
      {"add", UUID, String source, Number percent} -> Boolean   set (replace) that source's % for that player; 0 removes; finite, clamped
                                                               to -1000..1000; source 1-64 characters
      {"remove", UUID, String source} -> Boolean               TRUE = there was an entry
      {"get", UUID} -> Double                                  the total that applies (0..1000)
      {"sources", UUID} -> String[]                            "source=+20" sorted
      {"clear", String source} -> Integer                      that source removed from every player (a provider's shutdown)
  Nothing registers yet. SEE THE TOTAL: Server Setup -> Skills -> Overall and Mana -> "Mana Regen: show mine" (action row: your total,
  your sources, the out / in-combat rates) and the admin command /skills mana (live: Mana now / max, IN COMBAT or out, last hit, the
  rate SkyySkills adds right now).

Unchanged (asserted below + harness): kill / party / heal / grant XP maths, every bridge contract (skill:fn:healxp = the SkyyClasses
contract, skill:fn:addxp, skill:fn:craftxp, skill:fn:xp), ManaMig / HealMig / ManaGuard / SPELL GEN, the systems (registerSystem count),
commands (one registerCommand; + the admin sub-command /skills mana), every event binding, the player file format.

REVIEW FIXES (review of 0.4.12, verdict PASS, 9 Low / Info findings; same version - nothing was deployed):
  R1 the Overall page with NO counted skill (overall.skills=Class without SkyyClasses / with an unknown class: Overall.maxLevel = 0) drew
     the max layout "Level 0 of 0 - the highest Overall Level": max is now omax > 0 && lv >= omax; that page says "No skill counts toward
     the Overall Level on this server" and Overall.nextLines(lv, 0) gives one "Nothing - no skill counts" line instead of an empty box.
  R3 ManaRegen.tick ran last inside AcroSys.tick's one try block (after Acro.move / airJump / dodge / falls, Brew.tick, Xbow.tick): one
     exception there cost that tick's Mana refill. It now runs right after the player's UUID is read, before every other call (its own
     try, so nothing it does can stop the rest either).
  R4 the "Mana Regen: show mine" answer is shown by SkyyMenu in ONE 30 px status line (firstLine, about 110 characters): the action now
     answers ManaRegen.compact (at most 110 characters: the numbers, then as many sources as fit, "+N more"), e.g. "Mana Regen +20%
     (SkyyGear=+20). Refill 6/s, in combat 3/s (50%)."; /skills mana keeps the full text in chat. (The "(action)" Changes-log line is
     the config kit's own action logging - tools/CONFIG-CONTRACT.md - not changeable from a mod.)
  R5 the class curve size message reported the raw list ("level 1 needs 75 XP" at 150%) although class skills level on min(class list,
     other list): it now reports the EFFECTIVE totals after the change (SkillKit.classTotals = SkillDefs.ECUM: "class skill 1 at 50 XP,
     20 at 32.3k, 100 at 9.94m in total"), and says the list is not in use while levels.class.sameAsOthers is on.
  R9 skill:<uuid> (SkyyHud's levels string) went stale after a live curve change until a level up / relog (publishOnline skips players it
     already published): SkillStore.republishAll() forgets who is published (under the PUB lock publishNow holds) after every table
     change - SkillKit.customSet (the four curve rows), SkillKit.reload (the kit's reload after each xp.properties save) and /skills
     reload - so the next 5 s publishOnline republishes every online player.
  NOT CHANGED (reasons in the builder's return): R2 the curve notice stays ungated - research/Settings-Spec.md section 2.3 (LOCKED
  2026-09-25 by Skyy) keeps one-time notices always shown (its own precedent: the old Combat XP move notice); R6 no total Mana Regen cap
  row (nothing registers yet; the default is Skyy's number - MAX_PCT 1000 stays the hard clamp); R7 "classes without Mana" = no Mana pool
  (max 0) stays (Skyy's call); R8 the class level-up coin pace is Skyy's economy call (coinsPerLevel in xp.properties).
"""
import os
import re
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.11.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.12.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.11"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
# the source must be the generated 0.4.11 of the EDITED lineage
assert 'VERSION = "0.4.11"' in s and "derived from the generated 0.4.10 by tools/skills_0_4_11_patch.py" in s, "not the live generated 0.4.11"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "ClassCurve" not in s and "ManaRegen" not in s and "levels.class" not in s and "mana.regen" not in s
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]

# ---------------------------------------------------------------------------------------------------------------- the reference table
# research/cloud/Class-Skill-Curve-Proposal.md section 5 "XP for level" (Skyy 2026-10-02: approved as written) - verbatim
CLASS_LEVELS_REF = [
    50, 100, 160, 220, 280, 350, 440, 530, 630, 750, 880, 1050, 1200, 1400, 1600, 1800, 2100, 2350, 2650, 3000, 3350, 3750, 4200,
    4650, 5150, 5700, 6250, 6900, 7550, 8250, 9000, 9800, 10500, 11500, 12500, 13500, 14500, 15500, 17000, 18000, 19500, 20500,
    22000, 23500, 25000, 26500, 28500, 30000, 32000, 34000, 35500, 38000, 40000, 42000, 44500, 46500, 49000, 51500, 54500, 57000,
    60000, 62500, 65500, 68500, 72000, 75000, 78500, 82000, 85500, 89000, 93000, 97000, 100000, 105000, 110000, 115000, 120000,
    125000, 125000, 130000, 135000, 140000, 145000, 150000, 160000, 165000, 170000, 175000, 180000, 185000, 195000, 200000, 205000,
    210000, 220000, 225000, 235000, 240000, 250000, 255000]
_md = open(os.path.join(ROOT, "research", "cloud", "Class-Skill-Curve-Proposal.md"), encoding="utf8").read()
_sec = _md[_md.index("## 5. Per-level table"):_md.index("## 6.")]
_rows = []
for _ln in _sec.splitlines():
    _m = re.match(r"\|\s*(\d+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|", _ln)
    if _m:
        _rows.append(tuple(int(x.replace(",", "")) for x in _m.groups()))
assert [r[0] for r in _rows] == list(range(1, 101)), "proposal section 5: levels 1-100 expected"
assert [r[1] for r in _rows] == CLASS_LEVELS_REF, "CLASS_LEVELS_REF != the proposal's section 5 'XP for level' column"
_t = 0
for _r in _rows:
    _t += _r[1]
    assert _t == _r[2], ("proposal total", _r)


def _cls_xp(L):
    x = Fraction(50 * L) + Fraction(L ** 3, 4)
    st = 10 if x < 1000 else 50 if x < 10000 else 500 if x < 100000 else 5000
    return round(x / st) * st       # Fraction round = half to even (the proposal's Python round(); level 70: 89,250 -> 89,000)


assert [_cls_xp(L) for L in range(1, 101)] == CLASS_LEVELS_REF, "the formula does not reproduce the proposal table"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def cut(a, b, new):
    """replace s[index(a) : index(b)] (b itself stays) with new"""
    global s
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    s = s[:s.index(a)] + new + s[s.index(b):]


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical: SPELL GEN, ManaMig / HealMig / ManaGuard, the XP maths (BridgeXp part 1, HealXp
# part 1, BridgeTask, KillSys + the gathering systems), every bridge Function contract (skill:fn:xp / drops / placed, addxp, healxp,
# craftxp), the config holders whose rows did not change (DivCfg, XbowCfg, OverallCfg), PartyXp's share code
KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ---- ManaMig (point 2)", "# ---- HealMig (0.4.11 point 5)"),
        block("# ---- HealMig (0.4.11 point 5)", "# ---- ManaGuard (point 3)"),
        block("# ---- ManaGuard (point 3)", "# ================= SkillKit (0.4.3)"),
        block("# ================= BridgeXp part 1 (0.4)", "# ================= HealXp part 1"),
        block("# ================= HealXp part 1", "# ================= Perks (0.3)"),
        block("# ================= BridgeTask (0.4)", "# ================= HealXp part 2"),
        block("# ================= ECS systems", "# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4)"),
        block("# ================= trees bridge Functions (0.4", "# ================= leaderboard ="),
        block("# ================= DivCfg (0.4.4)", "# ================= XbowCfg (0.4.5)"),
        block("# ================= XbowCfg (0.4.5)", "# ================= OverallCfg (0.4.6)"),
        block("# ================= OverallCfg (0.4.6)", "# ================= BridgeCfg (0.4)"),
        block('pxp.addField(CtField.make("public static volatile boolean FAILED_ONCE', "# ================= ECS systems")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.11 - build script (derived from the generated 0.4.10 by tools/skills_0_4_11_patch.py - edit the patch, not this file;
0.4.10 was derived''', '''"""SkyySkills 0.4.12 - build script (derived from the generated 0.4.11 by tools/skills_0_4_12_patch.py - edit the patch, not this file;
0.4.11 was derived from the generated 0.4.10 by tools/skills_0_4_11_patch.py; 0.4.10 was derived''')
HEAD_0412 = '''0.4.12: THE CLASS SKILL CURVE + MANA REGEN IN COMBAT (Skyy's Q&A 2026-10-02 rounds 1-2; full notes in tools/skills_0_4_12_patch.py).
  CLASS SKILLS level on their OWN table (research/cloud/Class-Skill-Curve-Proposal.md, approved as written): XP for level L = 50 x L +
  0.25 x L^3 rounded (10 / 50 / 500 / 5,000 steps, half to even) = the proposal's section 5 table, asserted here (20 at 21,540 XP, 40 at
  209,090, 100 at 6,627,590; 0.4.11: 522,425 / 25.5m / 637.7m). Every level comes from SkillDefs.levelOf(slot, total) (+ intoLevel /
  needFor / progress / maxOf per slot) - the one global lookup is gone. Class level = max(general table, class table) up to the class max
  (levels only go up; the default class table is at or below the general one at every level). Rows (Levels tab): levels.class (list),
  levels.class.scale (%), levels.class.max (1-100), levels.class.sameAsOthers (off). Gathering and every other skill keep their table.
  Existing XP is kept: the first 0.4.12 start records once (class-curve.properties) which profiles' class levels rose; each gets one
  "Class skill curve updated" chat line + the level-up coins of the gained levels (paid marker = exactly once) the next time it plays.
  MANA REGEN IN COMBAT (rounds 1-2): vanilla refills 0 for 6 s after taking damage; SkyySkills now refills Mana there at mana.regen.inCombat
  % (Server Setup "In-combat Mana regen", default 50, 0 = vanilla) of (vanilla rate + Mana Regen boosts); out of combat it adds the boost
  part (vanilla rate x Mana Regen %) on top of vanilla. Never above max Mana, never while charging, nothing without Mana. Boosts are
  percents other mods register per player on skill:fn:manaregen (nothing registers yet); see them in Server Setup ("Mana Regen: show
  mine") or with the admin /skills mana.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.12.py, -Xverify:all, scratch under tools/dev/scratch/skills0412 deleted afterwards):
  the table = the proposal, per-slot levels everywhere (pages, bridge, rewards, Overall), the guard, ClassCurve on copies of the live data
  (nobody to tell on Skyy's world; edited copies: told + paid once, start twice = once), the Mana regen maths on real engine conditions, the
  bridge, the loader, the rows, class bytes vs 0.4.11. UNVERIFIED (needs the game): the in-combat refill feel, /skills mana, the notice line.
  REVIEW FIXES: the Overall page without counted skills is not "max"; the Mana refill runs first in AcroSys.tick (no other call can skip
  it); the "Mana Regen: show mine" answer fits SkyyMenu's one-line status (<= 110 characters); the class curve size message shows the
  effective class totals; skill:<uuid> is republished within 5 s after any live curve change (SkillStore.republishAll).
'''
rep('''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.11: PRIEST''', '''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
''' + HEAD_0412 + '''0.4.11: PRIEST''')
rep('VERSION = "0.4.11"\n', 'VERSION = "0.4.12"\n')


# ---------------------------------------------------------------------------------------------------------------- point 1: the table
rep('''assert len(LEVELS) == 100 and LEVELS[59] == 7000000 and sum(LEVELS[:60]) == 111672425 and LEVELS[99] == 19000000
''', '''assert len(LEVELS) == 100 and LEVELS[59] == 7000000 and sum(LEVELS[:60]) == 111672425 and LEVELS[99] == 19000000
# 0.4.12 (Skyy 2026-10-02 Q&A round 1: "the cloud proposal as written"): the CLASS skill table - research/cloud/Class-Skill-Curve-Proposal.md
# section 5 "XP for level", verbatim (tools/skills_0_4_12_patch.py checked it against the proposal file when it wrote this script)
CLASS_LEVELS_REF = ''' + repr(CLASS_LEVELS_REF) + '''
from fractions import Fraction as _Fr
def _cls_xp(L):
    """XP for class level L = round(50 x L + 0.25 x L^3) to a step of 10 below 1,000, 50 below 10,000, 500 below 100,000, 5,000 above
    (the step is picked on the unrounded value; round half to even = the proposal's Python round(): level 70 = 89,250 -> 89,000)"""
    x = _Fr(50 * L) + _Fr(L ** 3, 4)
    st = 10 if x < 1000 else 50 if x < 10000 else 500 if x < 100000 else 5000
    return round(x / st) * st
CLASS_LEVELS = [_cls_xp(_L) for _L in range(1, 101)]
assert CLASS_LEVELS == CLASS_LEVELS_REF, "the class curve formula does not give the proposal's section 5 table"
_cc, _oc = 0, 0
for _i in range(100):
    _cc += CLASS_LEVELS[_i]
    _oc += LEVELS[_i]
    # Skyy: never below today at any level - the class total for every level is at or below the 0.4.11 (general) total
    assert _cc <= _oc, "class level %d needs %d XP in total, more than the general table's %d" % (_i + 1, _cc, _oc)
assert [sum(CLASS_LEVELS[:_n]) for _n in (10, 20, 30, 40, 60, 100)] == [3510, 21540, 77290, 209090, 929090, 6627590], "proposal section 2 totals"
CLASS_LEVELS_TEXT = ",".join(str(x) for x in CLASS_LEVELS)
''')
rep('''L.append("# is the max level, at most 100)")
''', '''L.append("# is the max level, at most 100). Every skill but the class skills - they level on levels.class (Class skill levels, below).")
''')
rep('''CLS_LIT = json.dumps(CLS_DEFAULTS)
''', r'''CLS_LIT = json.dumps(CLS_DEFAULTS)
# 0.4.12 (Skyy 2026-10-02 Q&A round 1): the class skill table. Appended once to a file without levels.class (SkillCfg.ensureCurve, the
# ensureClass pattern, in the file's own line ending); the code default (SkillDefs.DEFAULT_CPER) is the same list.
CURVE_L = []
CURVE_L.append("# ---------- Class skill levels (SkyySkills 0.4.12) ----------")
CURVE_L.append("# Comments must stay on their own lines.")
CURVE_L.append("# Class skills (Archery, Swordsmanship, Sorcery, Fury, Divinity, later Assassination and the Shaman skill) level on their own")
CURVE_L.append("# table (Skyy 2026-10-02): XP for level L = 50 x L + 0.25 x L^3, rounded to 10 below 1000, 50 below 10000, 500 below 100000")
CURVE_L.append("# and 5000 above - class skill 20 after 21540 XP in total, 40 after 209090, 100 after 6627590. levels= is for every other skill.")
CURVE_L.append("# A class level never needs more total XP than levels= asks for the same level, so class levels never drop below that table.")
CURVE_L.append("# Set levels.class.sameAsOthers to true and class skills use levels= again (the old, slower curve; levels drop back, coins stay).")
CURVE_L.append("# Server Setup - Skills - Levels: the class curve size in percent and the class max level rewrite levels.class.")
CURVE_L.append("levels.class=" + CLASS_LEVELS_TEXT)
CURVE_L.append("levels.class.sameAsOthers=false")
L.append("")
L.extend(CURVE_L)
CURVE_DEFAULTS = "\n".join(CURVE_L) + "\n"
assert all(ord(ch) < 128 for ch in CURVE_DEFAULTS) and '"' not in CURVE_DEFAULTS
assert [_ln for _ln in CURVE_L if not _ln.startswith("#")] == ["levels.class=" + CLASS_LEVELS_TEXT, "levels.class.sameAsOthers=false"]
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in CURVE_L), "a comment looks like a template line"
assert CURVE_DEFAULTS.count("\nlevels.class.sameAsOthers=false\n") == 1   # SkillCfg.ensureCurve drops that line when the file has the key
CURVE_LIT = json.dumps(CURVE_DEFAULTS)
# 0.4.12 (Skyy 2026-10-02 Q&A rounds 1-2): Mana refills in combat at this percent of (vanilla + Mana Regen boosts). Appended once to a file
# without mana.regen.inCombat (SkillCfg.ensureManaRegen); the code default (ManaRegen.IN_COMBAT) is the same number.
MREG_DEF = "50"
MREG_L = []
MREG_L.append("# ---------- Mana regen in combat (SkyySkills 0.4.12) ----------")
MREG_L.append("# Comments must stay on their own lines.")
MREG_L.append("# Vanilla Mana refills 5 per second, but not at all for 6 seconds after you take damage (in combat) and never while you hold")
MREG_L.append("# a charge. mana.regen.inCombat (Skyy 2026-10-02: 50) is how fast Mana refills in combat, as a percent of the normal refill;")
MREG_L.append("# 0 = vanilla (nothing in combat). Mana Regen boosts from other mods (skill:fn:manaregen) are percents of the vanilla refill:")
MREG_L.append("# out of combat +20 percent = 6 per second, in combat the whole refill (vanilla + boosts) runs at mana.regen.inCombat percent.")
MREG_L.append("# Never above max Mana, never while charging, nothing for a player without Mana (max Mana 0).")
MREG_L.append("mana.regen.inCombat=" + MREG_DEF)
L.append("")
L.extend(MREG_L)
MREG_DEFAULTS = "\n".join(MREG_L) + "\n"
assert all(ord(ch) < 128 for ch in MREG_DEFAULTS) and '"' not in MREG_DEFAULTS
assert [_ln for _ln in MREG_L if not _ln.startswith("#")] == ["mana.regen.inCombat=" + MREG_DEF]
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in MREG_L), "a comment looks like a template line"
MREG_LIT = json.dumps(MREG_DEFAULTS)
''')

# ---------------------------------------------------------------------------------------------------------------- new classes (declared
# early: their FIELDS are read by code compiled before their methods - SkillCfg.load sets ManaRegen.IN_COMBAT, Acro.retainOnline prunes
# ManaRegen.CLK)
rep('''opg  = pool.makeClass(PKG + ".OverallPage", pool.get(PAGE))
''', '''opg  = pool.makeClass(PKG + ".OverallPage", pool.get(PAGE))
# 0.4.12: the class skill curve notice (ClassCurve), Mana regen in combat + the Mana Regen % registry (ManaRegen, its bridge Function
# ManaRegenFn) and the admin /skills mana sub-command (ManaCmd)
ccv  = pool.makeClass(PKG + ".ClassCurve")
mrg  = pool.makeClass(PKG + ".ManaRegen")
mrfn = pool.makeClass(PKG + ".ManaRegenFn")
mcmd = pool.makeClass(PKG + ".ManaCmd", pool.get(APC))
mrg.addField(CtField.make("public static volatile int IN_COMBAT = " + MREG_DEF + ";", mrg))   # mana.regen.inCombat (0-100 %)
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CLK = new java.util.concurrent.ConcurrentHashMap();", mrg))   # UUID -> float[]{s}
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SRC = new java.util.concurrent.ConcurrentHashMap();", mrg))   # UUID -> CHM source -> Double %
mrg.addField(CtField.make("public static boolean FAILED_ONCE = false;", mrg))
mrg.addField(CtField.make("public static final double MAX_PCT = 1000.0;", mrg))
mrg.addField(CtField.make("public static final float PULSE = 0.2f;", mrg))   # = vanilla Mana.json's 0.2 s regen interval
''')

# ---------------------------------------------------------------------------------------------------------------- point 2: SkillDefs
cut('''defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in LEVELS), defs))''',
    '''defs.addMethod(CtNewMethod.make("""
public static int indexOf(String s) {''',
    '''defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in LEVELS), defs))
defs.addField(CtField.make("public static volatile long[] PER = DEFAULT_PER;", defs))
defs.addField(CtField.make("public static volatile long[] CUM = new long[] { 0L };", defs))
defs.addField(CtField.make("public static volatile int MAX = 100;", defs))
# 0.4.12 (Skyy 2026-10-02 Q&A round 1, research/cloud/Class-Skill-Curve-Proposal.md): the CLASS skill table (levels.class) - CPER / CCUM /
# CMAX like PER / CUM / MAX - and levels.class.sameAsOthers (SAME). ECUM = the EFFECTIVE class table every class slot levels on:
# ECUM[L] = min(CCUM[L], CUM[L]) for L up to CMAX (a class level never needs more total XP than the general table asks for the same
# level = level max(general, class): levels only go up; capped by the class max), or CUM itself while SAME. recalc() rebuilds it whenever
# either table changes (setTable / setClassTable, both under the SkillDefs lock).
defs.addField(CtField.make("public static final long[] DEFAULT_CPER = new long[] { %s };" % ", ".join("%dL" % x for x in CLASS_LEVELS), defs))
defs.addField(CtField.make("public static volatile long[] CPER = DEFAULT_CPER;", defs))
defs.addField(CtField.make("public static volatile long[] CCUM = new long[] { 0L };", defs))
defs.addField(CtField.make("public static volatile int CMAX = 100;", defs))
defs.addField(CtField.make("public static volatile boolean SAME = false;", defs))
defs.addField(CtField.make("public static volatile long[] ECUM = new long[] { 0L };", defs))
defs.addMethod(CtNewMethod.make("""
public static synchronized void recalc() {
  long[] g = CUM;
  if (SAME) { ECUM = g; return; }
  long[] c = CCUM;
  long[] e = new long[c.length];
  for (int i = 0; i < c.length; i++) {
    long x = c[i];
    if (i < g.length && g[i] < x) x = g[i];
    e[i] = x;
  }
  ECUM = e;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static synchronized void setTable(long[] per) {
  if (per == null || per.length == 0) return;
  long[] cum = new long[per.length + 1];
  cum[0] = 0L;
  for (int i = 0; i < per.length; i++) cum[i + 1] = cum[i] + per[i];
  PER = per; CUM = cum; MAX = per.length;
  recalc();
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static synchronized void setClassTable(long[] per, boolean same) {
  if (per == null || per.length == 0) return;
  long[] cum = new long[per.length + 1];
  cum[0] = 0L;
  for (int i = 0; i < per.length; i++) cum[i + 1] = cum[i] + per[i];
  CPER = per; CCUM = cum; CMAX = per.length; SAME = same;
  recalc();
}""", defs))
# 0.4.12: THE per-slot lookup - the cumulative table a storage slot levels on (class slots: ECUM, every other slot: the general CUM)
defs.addMethod(CtNewMethod.make("""
public static long[] cumOf(int s) {
  return isClass(s) ? ECUM : CUM;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int maxOf(int s) {
  return cumOf(s).length - 1;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int levelIn(long[] cum, long total) {
  int max = cum.length - 1;
  int l = 0;
  while (l < max && total >= cum[l + 1]) l++;
  return l;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int levelOf(int s, long total) {
  return levelIn(cumOf(s), total);
}""", defs))
# the level on the GENERAL table (= what 0.4.11 showed for any slot) - ClassCurve's "was" level
defs.addMethod(CtNewMethod.make("""
public static int generalLevel(long total) {
  return levelIn(CUM, total);
}""", defs))
# XP into the current level of slot s
defs.addMethod(CtNewMethod.make("""
public static long intoLevel(int s, long total) {
  long[] c = cumOf(s);
  return total - c[levelIn(c, total)];
}""", defs))
# XP the current level of slot s needs in total (0 at its max level)
defs.addMethod(CtNewMethod.make("""
public static long needFor(int s, long total) {
  long[] c = cumOf(s);
  int l = levelIn(c, total);
  return l + 1 < c.length ? c[l + 1] - c[l] : 0L;
}""", defs))
''')
rep('''defs.addMethod(CtNewMethod.make("""
public static String progress(long total) {
  long need = needFor(total);
  if (need <= 0L) return "MAX";
  return fmt(intoLevel(total)) + "/" + fmt(need);
}""", defs))''', '''defs.addMethod(CtNewMethod.make("""
public static String progress(int s, long total) {
  long need = needFor(s, total);
  if (need <= 0L) return "MAX";
  return fmt(intoLevel(s, total)) + "/" + fmt(need);
}""", defs))''')

# ---------------------------------------------------------------------------------------------------------------- point 4: SkillCfg
rep('''cfg.addField(CtField.make("public static final String CLASS_DEFAULTS = " + CLS_LIT + ";", cfg))
''', '''cfg.addField(CtField.make("public static final String CLASS_DEFAULTS = " + CLS_LIT + ";", cfg))
# 0.4.12: the class skill levels block and the Mana regen in combat block (ensureCurve / ensureManaRegen append them once)
cfg.addField(CtField.make("public static final String CURVE_DEFAULTS = " + CURVE_LIT + ";", cfg))
cfg.addField(CtField.make("public static final String MREG_DEFAULTS = " + MREG_LIT + ";", cfg))
''')
rep('''  }} catch (Throwable t) {{ warn("could not append the class skill XP section to xp.properties: " + t); }}
}}""", cfg))
''', r'''  }} catch (Throwable t) {{ warn("could not append the class skill XP section to xp.properties: " + t); }}
}}""", cfg))
# 0.4.12: append a block once at the end of xp.properties in the file's OWN line ending (CRLF when the file has CRLF; ensureClass and the
# older blocks always wrote LF), after one blank line; ISO-8859-1 in and out (the blocks are ASCII). Nothing before it changes.
cfg.addMethod(CtNewMethod.make(f"""
public static void appendBlock(String key, String block, String what) {{
  try {{
    byte[] old = java.nio.file.Files.readAllBytes(FILE);
    String t = new String(old, "ISO-8859-1");
    boolean crlf = t.indexOf("\\r\\n") >= 0;
    String nl = crlf ? "\\r\\n" : "\\n";
    String b = crlf ? block.replace("\\n", "\\r\\n") : block;
    String pre = (t.length() == 0 || t.endsWith("\\n")) ? nl : nl + nl;
    java.nio.file.Files.write(FILE, (pre + b).getBytes("ISO-8859-1"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    info("xp.properties: appended the " + what + " section (" + key + ")");
  }} catch (Throwable t) {{ warn("could not append the " + what + " section to xp.properties: " + t); }}
}}""", cfg))
# 0.4.12: the class skill levels block once to a file without levels.class (this load reads the code default class table for the missing
# key, the next load reads the appended line); a file that already holds levels.class.sameAsOthers (an admin's line) gets only the list
cfg.addMethod(CtNewMethod.make(f"""
public static void ensureCurve(java.util.Properties p) {{
  if (p.getProperty("levels.class") != null) return;
  String b = CURVE_DEFAULTS;
  if (p.getProperty("levels.class.sameAsOthers") != null) b = b.replace("\\nlevels.class.sameAsOthers=false\\n", "\\n");
  appendBlock("levels.class", b, "class skill levels");
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static void ensureManaRegen(java.util.Properties p) {{
  if (p.getProperty("mana.regen.inCombat") != null) return;
  appendBlock("mana.regen.inCombat", MREG_DEFAULTS, "Mana regen in combat");
}}""", cfg))
# "own table, max level 100" / "on the other skills' table (levels.class.sameAsOthers)" (load text, ready line)
cfg.addMethod(CtNewMethod.make(f"""
public static String curveText() {{
  if ({PKG}.SkillDefs.SAME) return "on the other skills' table (levels.class.sameAsOthers)";
  return "own table, max level " + {PKG}.SkillDefs.CMAX;
}}""", cfg))
''')
rep('''    ensureClass(p);
    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);
''', '''    ensureClass(p);
    ensureCurve(p);       // 0.4.12: the class skill levels block, once
    ensureManaRegen(p);   // 0.4.12: the Mana regen in combat block, once
    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);
''')
rep('''      if (ok) {PKG}.SkillDefs.setTable(per); else {{ bad++; warn("bad levels= line, using the default table"); }}
    }}
''', '''      if (ok) {PKG}.SkillDefs.setTable(per); else {{ bad++; warn("bad levels= line, using the default table"); }}
    }}
    // 0.4.12: the class skill table (levels.class, the levels= rules: 1-100 numbers above 0, else the default class table) and
    // levels.class.sameAsOthers; setClassTable rebuilds the effective class table against the general one loaded just above
    long[] cper = {PKG}.SkillDefs.DEFAULT_CPER;
    String lc = p.getProperty("levels.class");
    if (lc != null && lc.trim().length() > 0) {{
      String[] cps = lc.split(",");
      long[] cp = new long[cps.length];
      boolean cok = cps.length >= 1 && cps.length <= 100;
      for (int i = 0; i < cps.length && cok; i++) {{
        try {{ cp[i] = Long.parseLong(cps[i].trim()); if (cp[i] <= 0L) cok = false; }} catch (Throwable t) {{ cok = false; }}
      }}
      if (cok) cper = cp; else {{ bad++; warn("bad levels.class= line, using the default class skill table"); }}
    }}
    {PKG}.SkillDefs.setClassTable(cper, bool(p, "levels.class.sameAsOthers", false));
    // 0.4.12: mana.regen.inCombat, clamped to the row bounds 0-100 (a bad number = the default)
    long mrc = lng(p, "mana.regen.inCombat", {MREG_DEF}L);
    {PKG}.ManaRegen.IN_COMBAT = (int) (mrc < 0L ? 0L : (mrc > 100L ? 100L : mrc));
''')
rep(''', max level " + {PKG}.SkillDefs.MAX + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''',
    ''', max level " + {PKG}.SkillDefs.MAX + ", class skills " + curveText() + ", in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "%" + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''')

# ---------------------------------------------------------------------------------------------------------------- point 2: per-slot sites
# SkillStore: the default paid marker of a file without one, level (skill:fn:level / perks), levelsOf (skill:<uuid>), addK (gain4's
# level-up range), owesK / payLocked (the level-up coin rewards)
rep('''  for (int i = 0; i < {PKG}.SkillDefs.N; i++) if (d[{PKG}.SkillDefs.N + i] < 0L) d[{PKG}.SkillDefs.N + i] = (long) {PKG}.SkillDefs.levelOf(d[i]);''',
    '''  for (int i = 0; i < {PKG}.SkillDefs.N; i++) if (d[{PKG}.SkillDefs.N + i] < 0L) d[{PKG}.SkillDefs.N + i] = (long) {PKG}.SkillDefs.levelOf(i, d[i]);''')
rep('''  return {PKG}.SkillDefs.levelOf(data(u)[skill]);''', '''  return {PKG}.SkillDefs.levelOf(skill, data(u)[skill]);''')
rep('''    sb.append({PKG}.SkillDefs.LABELS[order[i]]).append(':').append({PKG}.SkillDefs.levelOf(d[order[i]]));''',
    '''    sb.append({PKG}.SkillDefs.LABELS[order[i]]).append(':').append({PKG}.SkillDefs.levelOf(order[i], d[order[i]]));''')
rep('''    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillDefs.levelOf(d[s]));''',
    '''    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillDefs.levelOf(s, d[s]));''')
rep('''  return new long[] {{ (long) {PKG}.SkillDefs.levelOf(ba[0]), (long) {PKG}.SkillDefs.levelOf(ba[1]), ba[1] }};''',
    '''  return new long[] {{ (long) {PKG}.SkillDefs.levelOf(skill, ba[0]), (long) {PKG}.SkillDefs.levelOf(skill, ba[1]), ba[1] }};''')
rep('''  return rd(d, {PKG}.SkillDefs.N + skill) < (long) {PKG}.SkillDefs.levelOf(rd(d, skill));''',
    '''  return rd(d, {PKG}.SkillDefs.N + skill) < (long) {PKG}.SkillDefs.levelOf(skill, rd(d, skill));''')
rep('''  int lv = {PKG}.SkillDefs.levelOf(rd(d, skill));
  boolean stop = false;''', '''  int lv = {PKG}.SkillDefs.levelOf(skill, rd(d, skill));
  boolean stop = false;''')
# Overall: sums (the Overall Level), listText (the Overall page), nextLines + the new maxLevel (each counted skill at its own max level)
rep('''    sum += {PKG}.SkillDefs.levelOf(d[s]);
    n++;''', '''    sum += {PKG}.SkillDefs.levelOf(s, d[s]);
    n++;''')
rep('''      if (cs >= 0) {{ sum += {PKG}.SkillDefs.levelOf(d[cs]); n++; }}''', '''      if (cs >= 0) {{ sum += {PKG}.SkillDefs.levelOf(cs, d[cs]); n++; }}''')
rep('''    sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillDefs.levelOf(d[s]));''',
    '''    sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillDefs.levelOf(s, d[s]));''')
rep('''      if (cs >= 0) part = {PKG}.SkillClass.skillName(u, cs) + " " + {PKG}.SkillDefs.levelOf(d[cs]) + " (your class)";''',
    '''      if (cs >= 0) part = {PKG}.SkillClass.skillName(u, cs) + " " + {PKG}.SkillDefs.levelOf(cs, d[cs]) + " (your class)";''')
rep('''ovl.addMethod(CtNewMethod.make("""
public static int level(int[] sc) {
  return sc[1] <= 0 ? 0 : sc[0] / sc[1];
}""", ovl))
''', '''ovl.addMethod(CtNewMethod.make("""
public static int level(int[] sc) {
  return sc[1] <= 0 ? 0 : sc[0] / sc[1];
}""", ovl))
# 0.4.12: the highest Overall Level this player can reach = every skill sums() counts at ITS OWN max level (class skills have their own
# max, levels.class.max); no class yet counts the class skill max (the potential), an unknown class is left out like in sums()
ovl.addMethod(CtNewMethod.make(f"""
public static int maxLevel(java.util.UUID u) {{
  int sum = 0;
  int n = 0;
  int[] sl = {PKG}.OverallCfg.SLOTS;
  for (int i = 0; i < sl.length; i++) {{
    int s = sl[i];
    if (s < 0 || s >= {PKG}.SkillDefs.N) continue;
    sum += {PKG}.SkillDefs.maxOf(s);
    n++;
  }}
  if ({PKG}.OverallCfg.CLASS && classesOn()) {{
    String c = classOf(u);
    int cs = c == null ? {PKG}.SkillDefs.CLASS_SLOT[0] : {PKG}.SkillClass.slotOfClass(c);
    if (cs >= 0) {{ sum += {PKG}.SkillDefs.maxOf(cs); n++; }}
  }}
  return n <= 0 ? 0 : sum / n;
}}""", ovl))
''')
# (review fix R1: top 0 = no skill counts toward the Overall Level - one line saying so instead of an empty box)
rep('''public static java.util.ArrayList nextLines(int lv) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (lv >= {PKG}.SkillDefs.MAX) return out;''', '''public static java.util.ArrayList nextLines(int lv, int top) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (top <= 0) {{ out.add("Nothing - no skill counts toward the Overall Level"); return out; }}
  if (lv >= top) return out;''')
# the chat lines: "+12 Mining XP (340/500)" and "[Party] +6 Archery XP (340/500) from Skyy's kill"
rep('''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillDefs.progress(d[i])).append(")");''',
    '''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");''')
rep('''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillClass.skillName(u, i)).append(" XP (").append({PKG}.SkillDefs.progress(d[i])).append(")");''',
    '''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillClass.skillName(u, i)).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");''')

# ---------------------------------------------------------------------------------------------------------------- point 5: ClassCurve
CCV = r'''# ================= ClassCurve (0.4.12): the one-time class skill curve notice + the level-up rewards of the levels the new curve gave ==========
# FILE = Skyy_SkyySkills/class-curve.properties. The FIRST start of 0.4.12 (no file) scans every players/*.properties once (read-only) and
# records pending.<profile key>=<slot>:<level before>:<level now> for each class slot whose level on the class table is above its level on
# the general table (= what 0.4.11 showed); later starts read the file. PENDING / DONE = the records in memory; READY = the file is on
# disk (only then is anybody told); DIRTY = the file must be rewritten (SkillTick flush); SAVE = delivered profile keys whose player file
# is saved before that rewrite (so "done" is never on disk before their paid markers).
ccv.addField(CtField.make("public static java.nio.file.Path FILE;", ccv))
ccv.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();", ccv))
ccv.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();", ccv))
ccv.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SAVE = new java.util.concurrent.ConcurrentHashMap();", ccv))
ccv.addField(CtField.make("public static volatile boolean READY = false;", ccv))
ccv.addField(CtField.make("public static volatile boolean DIRTY = false;", ccv))
ccv.addField(CtField.make("public static volatile String SCANNED = null;", ccv))
ccv.addField(CtField.make('public static final String NAME = "class-curve.properties";', ccv))
ccv.addField(CtField.make('public static final String HEAD1 = "# SkyySkills class skill curve update (0.4.12, Skyy 2026-10-02) - written once at the first start of 0.4.12; do not edit (deleted = the next start scans again: the line again, never the coins)";', ccv))
ccv.addField(CtField.make('public static final String HEAD2 = "# pending.<profile key> = class slot:level before:level now - told and paid the next time that profile plays; done.<profile key> = told";', ccv))
ccv.addMethod(CtNewMethod.make("""
public static String stamp() {
  return new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(new java.util.Date());
}""", ccv))
ccv.addMethod(CtNewMethod.make("""
public static String one(Object v) {
  return String.valueOf(v).replace('\\n', ' ').replace('\\r', ' ');
}""", ccv))
# one player file -> "slot:old:new,..." for every class slot whose level on the effective class table is above its level on the general
# table, "" = none. Pure (reads only the Properties and the loaded tables), any thread.
ccv.addMethod(CtNewMethod.make(f"""
public static String rises(java.util.Properties p) {{
  StringBuilder sb = new StringBuilder();
  for (int j = 0; j < {PKG}.SkillDefs.CLASS_SLOT.length; j++) {{
    int s = {PKG}.SkillDefs.CLASS_SLOT[j];
    long x = 0L;
    try {{ x = Long.parseLong(String.valueOf(p.getProperty({PKG}.SkillDefs.NAMES[s], "0")).trim()); }} catch (Throwable t) {{ x = 0L; }}
    if (x <= 0L) continue;
    int old = {PKG}.SkillDefs.generalLevel(x);
    int nw = {PKG}.SkillDefs.levelOf(s, x);
    if (nw <= old) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(s).append(':').append(old).append(':').append(nw);
  }}
  return sb.toString();
}}""", ccv))
# the whole file, atomically (tmp + the SkillStore move). DIRTY is cleared BEFORE the snapshot, so a change made while this runs is written
# by the next flush; a failure sets it again.
ccv.addMethod(CtNewMethod.make(f"""
public static synchronized boolean write() {{
  DIRTY = false;
  try {{
    StringBuilder sb = new StringBuilder();
    sb.append(HEAD1).append('\\n').append(HEAD2).append('\\n');
    sb.append("scanned=").append(one(SCANNED == null ? "" : SCANNED)).append('\\n');
    java.util.Iterator it = new java.util.TreeMap(PENDING).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      sb.append("pending.").append(e.getKey()).append('=').append(one(e.getValue())).append('\\n');
    }}
    it = new java.util.TreeMap(DONE).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      sb.append("done.").append(e.getKey()).append('=').append(one(e.getValue())).append('\\n');
    }}
    java.nio.file.Path tmp = FILE.resolveSibling(NAME + ".tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    {PKG}.SkillStore.moveRetry(tmp, FILE);
    return true;
  }} catch (Throwable t) {{
    DIRTY = true;
    {PKG}.SkillCfg.warn("could not write " + NAME + " (retried): " + t);
    return false;
  }}
}}""", ccv))
# setup(), right after SkillCfg.load (the tables are loaded) and before any player joins. Returns the INFO text ("" = nothing to say).
ccv.addMethod(CtNewMethod.make(f"""
public static synchronized String start(java.nio.file.Path base) {{
  PENDING.clear();
  DONE.clear();
  SAVE.clear();
  READY = false;
  DIRTY = false;
  SCANNED = null;
  if (base == null) return "";
  FILE = base.resolve(NAME);
  try {{
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.util.Properties p = {PKG}.SkillStore.readLocked(FILE);
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {{
        String k = (String) it.next();
        String v = p.getProperty(k);
        if (k.startsWith("pending.") && k.length() > 8) PENDING.put(k.substring(8), v);
        else if (k.startsWith("done.") && k.length() > 5) DONE.put(k.substring(5), v);
      }}
      SCANNED = p.getProperty("scanned");
      if (SCANNED == null || SCANNED.trim().length() == 0) {{
        PENDING.clear();
        {PKG}.SkillCfg.warn(NAME + " has no scanned= line - nobody is told about the class skill curve (delete the file to scan again)");
        return "";
      }}
      READY = true;
      return PENDING.isEmpty() ? "" : "class skill curve: " + PENDING.size() + " profile(s) still to be told";
    }}
    int files = 0;
    int bad = 0;
    java.io.File[] fs = null;
    if ({PKG}.SkillStore.DIR != null) fs = {PKG}.SkillStore.DIR.toFile().listFiles();
    if (fs != null) for (int i = 0; i < fs.length; i++) {{
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties") || !fs[i].isFile()) continue;
      String k = fn.substring(0, fn.length() - 11);
      try {{
        java.util.Properties p = {PKG}.SkillStore.readLocked(fs[i].toPath());
        files++;
        String r = rises(p);
        if (r.length() > 0) PENDING.put(k, r);
      }} catch (Throwable t) {{
        bad++;
        {PKG}.SkillCfg.warn("class skill curve: could not read " + fn + " (" + t + ") - that profile is not told");
      }}
    }}
    SCANNED = stamp() + " " + files + " profile file(s)" + (bad > 0 ? ", " + bad + " unreadable" : "");
    if (!write()) {{
      PENDING.clear();
      DIRTY = false;
      {PKG}.SkillCfg.warn("class skill curve: " + NAME + " could not be written - nobody is told this run; the next start scans again");
      return "";
    }}
    READY = true;
    String msg = "class skill curve (first start of 0.4.12): " + files + " profile file(s) scanned, " + PENDING.size() + " with a higher class level now - each is told and paid once, the next time it plays";
    {PKG}.SkillCfg.info(msg);
    return msg;
  }} catch (Throwable t) {{
    READY = false;
    DIRTY = false;
    {PKG}.SkillCfg.warn("class skill curve: start failed (nobody is told this run): " + t);
    return "";
  }}
}}""", ccv))
# world thread, the profile's first second on 0.4.12 (Perks.tick) or right before a class skill XP award (SkillXp.gain4): claim the entry
# (PENDING.remove = exactly once), then: the level-up coin rewards of the gained levels through the paid marker (payOwedK - coins only
# move the marker once SkyyCoins paid, so nothing is ever paid twice; unpaid levels stay owed for the normal late payout), ONE chat line,
# the crossbow unlock line (Archery passing its unlock level), the Overall level up (chat + heal, Overall.levelUp), a republish.
ccv.addMethod(CtNewMethod.make(f"""
public static void deliver({PR} pr, java.util.UUID u, String k, String e) {{
  try {{
    long[] d = {PKG}.SkillStore.dataK(k, u);
    String[] parts = e.split(",");
    int[] sl = new int[parts.length];
    int[] was = new int[parts.length];
    int[] now = new int[parts.length];
    int n = 0;
    StringBuilder lines = new StringBuilder();
    StringBuilder sum = new StringBuilder();
    long coins = 0L;
    long first = -1L;
    long last = -1L;
    for (int i = 0; i < parts.length; i++) {{
      String[] f = parts[i].trim().split(":");
      if (f.length < 3) continue;
      int s = -1;
      int old = 0;
      try {{ s = Integer.parseInt(f[0].trim()); old = Integer.parseInt(f[1].trim()); }} catch (Throwable t) {{ s = -1; }}
      if (!{PKG}.SkillDefs.isClass(s)) continue;
      int lv = {PKG}.SkillDefs.levelOf(s, {PKG}.SkillStore.rd(d, s));
      if (lv <= old) continue;
      long[] paid = null;
      if ({PKG}.SkillStore.owesK(k, u, s)) paid = {PKG}.SkillStore.payOwedK(k, u, s);
      if (paid != null) {{
        coins += paid[2];
        if (first < 0L || paid[0] < first) first = paid[0];
        if (paid[1] > last) last = paid[1];
      }}
      if (lines.length() > 0) lines.append(", ");
      lines.append({PKG}.SkillClass.skillName(u, s)).append(" is now level ").append(lv).append(" (was ").append(old).append(")");
      if (sum.length() > 0) sum.append(", ");
      sum.append({PKG}.SkillDefs.NAMES[s]).append(' ').append(old).append(" -> ").append(lv);
      sl[n] = s;
      was[n] = old;
      now[n] = lv;
      n++;
    }}
    if (n == 0) {{
      DONE.put(k, stamp() + " nothing to tell (no class level above its old level any more)");
      DIRTY = true;
      return;
    }}
    String c = "";
    if (coins > 0L) c = n == 1 ? " - +" + {PKG}.SkillDefs.fmt(coins) + " coins for " + (first == last ? "level " + first : "levels " + first + " to " + last) : " - +" + {PKG}.SkillDefs.fmt(coins) + " coins for the new levels";
    pr.sendMessage({MSG}.raw("[Skills] Class skill curve updated: " + lines.toString() + c).color("#ffc800"));
    boolean lvOn = {PKG}.SkillStore.notifyOn(u, "skills.levelUp");
    int archer = {PKG}.SkillClass.slotOfClass("Archer");
    for (int i = 0; i < n; i++) {{
      if (lvOn && sl[i] == archer && {PKG}.XbowCfg.ON && {PKG}.XbowCfg.LEVEL >= 1 && was[i] < {PKG}.XbowCfg.LEVEL && now[i] >= {PKG}.XbowCfg.LEVEL) pr.sendMessage({MSG}.raw("  " + {PKG}.Xbow.UNLOCK).color("#ffc800"));
      {PKG}.Overall.levelUp(pr, u, sl[i], (long) was[i], (long) now[i]);
    }}
    {PKG}.Xbow.refresh(u);
    {PKG}.SkillStore.publish(u);
    {PKG}.SkillStore.DIRTY.put(k, Boolean.TRUE);
    SAVE.put(k, Boolean.TRUE);
    DONE.put(k, stamp() + " " + sum.toString() + (coins > 0L ? " +" + coins + " coins" : ""));
    DIRTY = true;
    {PKG}.SkillCfg.info("class skill curve: told " + k + " - " + sum.toString() + (coins > 0L ? ", paid " + coins + " coins" : ""));
  }} catch (Throwable t) {{
    DONE.put(k, stamp() + " failed: " + t);
    DIRTY = true;
    {PKG}.SkillCfg.warn("class skill curve notice failed for " + k + ": " + t);
  }}
}}""", ccv))
# world thread: nothing pending (every second for every player after the first ones: one isEmpty) / not ready / another profile -> return;
# waits while profile:busy (a profile switch moves the live inventory and purse: PROFILES-CONTRACT rule 5) and while Overall's session hold
# runs (the first seconds of a session before SkyyClasses published the class - Overall.levelUp needs it)
ccv.addMethod(CtNewMethod.make(f"""
public static void tick({PR} pr, java.util.UUID u) {{
  if (!READY || PENDING.isEmpty() || pr == null || u == null) return;
  String k = {PKG}.SkillStore.pkey(u);
  Object e = PENDING.get(k);
  if (!(e instanceof String)) return;
  if ({PKG}.Xbow.busy(u)) return;
  if ({PKG}.Overall.hold(u, pr, System.currentTimeMillis())) return;
  if (PENDING.remove(k) == null) return;
  deliver(pr, u, k, (String) e);
}}""", ccv))
# scheduler thread (SkillTick, every second) + shutdown: the delivered profiles' player files first, then the record
ccv.addMethod(CtNewMethod.make(f"""
public static void flush() {{
  if (!READY || !DIRTY) return;
  java.util.Iterator it = new java.util.ArrayList(SAVE.keySet()).iterator();
  boolean ok = true;
  while (it.hasNext()) {{
    String k = (String) it.next();
    SAVE.remove(k);
    if (!{PKG}.SkillStore.save(k)) {{ SAVE.put(k, Boolean.TRUE); ok = false; }}
  }}
  if (ok) write();
}}""", ccv))

'''
rep('''# ================= SkillXp: award + level-up (world thread) =================
''', CCV + '''# ================= SkillXp: award + level-up (world thread) =================
''')
# SkillXp.gain4: the curve notice before a class skill award (its coins first), the level-up range / next / MAX per slot
rep('''  java.util.UUID u = pr.getUuid();
  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, amount);''', '''  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillDefs.isClass(skill)) {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: a pending class skill curve notice comes first (once)
  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, amount);''')
rep('''    long need = {PKG}.SkillDefs.needFor(r[2]);
    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));''',
    '''    long need = {PKG}.SkillDefs.needFor(skill, r[2]);
    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(skill, r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));''')
# Perks: the legacy Combat move line (the XP now counts in the class slot = its table), the 1 s tick delivers a pending curve notice
rep('''  pr.sendMessage({MSG}.raw("[Skills] Your old Combat XP (level " + {PKG}.SkillDefs.levelOf(x) + ") now counts for " + {PKG}.SkillClass.skillName(u, slot) + ". Each class keeps its own combat level.").color("#ffc800"));''',
    '''  pr.sendMessage({MSG}.raw("[Skills] Your old Combat XP (level " + {PKG}.SkillDefs.levelOf(slot, x) + ") now counts for " + {PKG}.SkillClass.skillName(u, slot) + ". Each class keeps its own combat level.").color("#ffc800"));''')
rep('''    if (repub) {PKG}.SkillStore.publish(u);
    {PKG}.Xbow.refresh(u);
    int[] lv = levels(u);''', '''    if (repub) {PKG}.SkillStore.publish(u);
    {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: the one-time class skill curve notice + its level-up rewards (only while one is pending)
    {PKG}.Xbow.refresh(u);
    int[] lv = levels(u);''')
rep('''    {PKG}.Overall.retain(online);
  }} catch (Throwable t) {{ }}''', '''    {PKG}.Overall.retain(online);
    {PKG}.ManaRegen.CLK.keySet().retainAll(online);   // 0.4.12 (the Mana Regen % entries belong to the mods that registered them)
  }} catch (Throwable t) {{ }}''')

# ---------------------------------------------------------------------------------------------------------------- part 2: ManaRegen
MRG = r'''# ================= ManaRegen (0.4.12): Mana regen in combat + the Mana Regen % registry (Skyy 2026-10-02 Q&A rounds 1-2) =================
# research/Mana-Cost-And-Regen-Research.md 2.1-2.3: vanilla Mana.json = every 0.2 s +1 Additive while Alive, NoDamageTaken (6 s) and not
# Charging (inverse) - 5 a second out of combat, 0 for 6 s after taking damage, 0 while holding a charge. SRC = UUID -> ConcurrentHashMap
# source -> Double Mana Regen % (other mods, skill:fn:manaregen; memory only: providers register live like move:<uuid>); CLK = UUID ->
# float[]{seconds since the last pulse} (pruned to online players by Acro.retainOnline).
mrg.addMethod(CtNewMethod.make("""
public static double clampTotal(double sum) {
  if (!(sum > 0.0)) return 0.0;
  return sum > MAX_PCT ? MAX_PCT : sum;
}""", mrg))
# the % that applies to this player: the sum of every source, below 0 = 0 (no drain), at most MAX_PCT; NaN / infinite entries skipped
mrg.addMethod(CtNewMethod.make("""
public static double total(java.util.UUID u) {
  if (u == null) return 0.0;
  Object o = SRC.get(u);
  if (!(o instanceof java.util.Map)) return 0.0;
  double sum = 0.0;
  java.util.Iterator it = ((java.util.Map) o).values().iterator();
  while (it.hasNext()) {
    Object v = it.next();
    if (!(v instanceof Number)) continue;
    double x = ((Number) v).doubleValue();
    if (Double.isNaN(x) || Double.isInfinite(x)) continue;
    sum = sum + x;
  }
  return clampTotal(sum);
}""", mrg))
# set (replace) one source's % for a player; 0 removes it; false = bad arguments (no player, source 1-64 characters, a finite number)
mrg.addMethod(CtNewMethod.make("""
public static boolean put(java.util.UUID u, String src, double pct) {
  if (u == null || src == null) return false;
  String s = src.trim();
  if (s.length() == 0 || s.length() > 64 || Double.isNaN(pct) || Double.isInfinite(pct)) return false;
  double v = pct < -1000.0 ? -1000.0 : (pct > 1000.0 ? 1000.0 : pct);
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) SRC.get(u);
  if (v == 0.0) {
    if (m != null) m.remove(s);
    return true;
  }
  if (m == null) {
    java.util.concurrent.ConcurrentHashMap nm = new java.util.concurrent.ConcurrentHashMap();
    Object o = SRC.putIfAbsent(u, nm);
    m = o == null ? nm : (java.util.concurrent.ConcurrentHashMap) o;
  }
  m.put(s, Double.valueOf(v));
  return true;
}""", mrg))
mrg.addMethod(CtNewMethod.make("""
public static boolean remove(java.util.UUID u, String src) {
  if (u == null || src == null) return false;
  Object o = SRC.get(u);
  if (!(o instanceof java.util.Map)) return false;
  return ((java.util.Map) o).remove(src.trim()) != null;
}""", mrg))
# "source=+20" for every source of this player, sorted by source
mrg.addMethod(CtNewMethod.make(f"""
public static String[] sources(java.util.UUID u) {{
  Object o = u == null ? null : SRC.get(u);
  if (!(o instanceof java.util.Map)) return new String[0];
  java.util.TreeMap t = new java.util.TreeMap((java.util.Map) o);
  String[] r = new String[t.size()];
  int i = 0;
  java.util.Iterator it = t.entrySet().iterator();
  while (it.hasNext() && i < r.length) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    double v = ((Number) e.getValue()).doubleValue();
    r[i] = e.getKey() + "=" + (v >= 0.0 ? "+" : "") + {PKG}.Overall.num(v);
    i++;
  }}
  return r;
}}""", mrg))
# remove a source from every player (a provider's shutdown); returns how many players had it
mrg.addMethod(CtNewMethod.make("""
public static int clear(String src) {
  if (src == null) return 0;
  String s = src.trim();
  int n = 0;
  java.util.Iterator it = SRC.values().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof java.util.Map && ((java.util.Map) o).remove(s) != null) n++;
  }
  return n;
}""", mrg))
# per second of one regen entry: Additive with a positive amount and interval -> amount / interval (vanilla Mana: 1 / 0.2 s = 5), else 0
# (the Creative Percentage entry, drains)
mrg.addMethod(CtNewMethod.make(f"""
public static float baseOf({RGN} rg) {{
  if (rg == null || rg.getRegenType() != {RGT}.ADDITIVE) return 0.0f;
  float a = rg.getAmount();
  float iv = rg.getInterval();
  if (!(a > 0.0f) || !(iv > 0.0f)) return 0.0f;
  return a / iv;
}}""", mrg))
# the entry's OWN engine conditions, one by one (Condition.eval = eval0 with the inverse flag; exactly what RegeneratingValue.shouldRegenerate
# checks after its timer step - we never call shouldRegenerate / regenerate, they advance the engine's timer): 0 = all pass (vanilla
# regenerates: OUT of combat), 1 = only NoDamageTaken fails (vanilla's in-combat pause), 2 = anything else fails (charging, dead)
mrg.addMethod(CtNewMethod.make(f"""
public static int state({CAC} acc, {REF} ref, java.time.Instant now, {RGN} rg) {{
  {CND}[] cs = rg.getConditions();
  if (cs == null) return 0;
  boolean nd = false;
  for (int i = 0; i < cs.length; i++) {{
    if (cs[i] == null) continue;
    if (cs[i].eval(acc, ref, now)) continue;
    if (cs[i] instanceof {NDT}) nd = true;
    else return 2;
  }}
  return nd ? 1 : 0;
}}""", mrg))
# {{base, out, in}} per second over the Mana value's regen entries: base = every positive Additive entry (vanilla 5), out = the ones running
# now, in = the ones only vanilla's combat pause stops
mrg.addMethod(CtNewMethod.make(f"""
public static float[] rates({CAC} acc, {REF} ref, java.time.Instant now, {RGV}[] rv) {{
  float[] r = new float[] {{ 0.0f, 0.0f, 0.0f }};
  if (rv == null) return r;
  for (int i = 0; i < rv.length; i++) {{
    if (rv[i] == null) continue;
    {RGN} rg = rv[i].getRegenerating();
    float b = baseOf(rg);
    if (!(b > 0.0f)) continue;
    r[0] = r[0] + b;
    int st = state(acc, ref, now, rg);
    if (st == 0) r[1] = r[1] + b;
    else if (st == 1) r[2] = r[2] + b;
  }}
  return r;
}}""", mrg))
# THE maths (pure): Mana SkyySkills adds now = (out x MR / 100 + in x (1 + MR / 100) x F / 100) x seconds, never past max, 0 without a
# Mana pool (max 0) or at max. MR = Mana Regen % (below 0 = 0, at most MAX_PCT), F = mana.regen.inCombat (0-100).
mrg.addMethod(CtNewMethod.make("""
public static float amount(float[] r, double pct, int factor, float secs, float cur, float max) {
  if (r == null || r.length < 3 || !(max > 0.0f) || !(cur < max) || !(secs > 0.0f)) return 0.0f;
  double p = pct > 0.0 ? (pct > MAX_PCT ? MAX_PCT : pct) : 0.0;
  int f = factor < 0 ? 0 : (factor > 100 ? 100 : factor);
  double per = (double) r[1] * p / 100.0 + (double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0;
  double a = per * (double) secs;
  if (!(a > 0.0)) return 0.0f;
  double room = (double) (max - cur);
  if (a > room) a = room;
  return (float) a;
}""", mrg))
# world thread, every tick from AcroSys (before its 1 s gate): one pulse per PULSE seconds (vanilla's own interval), at most 1 s at a time
mrg.addMethod(CtNewMethod.make(f"""
public static void tick(java.util.UUID u, {ST} store, {CB} cb, {REF} ref, float dt) {{
  try {{
    float[] c = (float[]) CLK.get(u);
    if (c == null) {{ c = new float[] {{ 0.0f }}; CLK.put(u, c); }}
    c[0] = c[0] + dt;
    if (c[0] < PULSE) return;
    float secs = c[0];
    c[0] = 0.0f;
    if (secs > 1.0f) secs = 1.0f;
    int f = IN_COMBAT;
    double pct = total(u);
    if (f <= 0 && !(pct > 0.0)) return;
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return;
    int mi = {DST}.getMana();
    if (mi < 0) return;
    {ESV} v = m.get(mi);
    if (v == null) return;
    float max = v.getMax();
    float cur = v.get();
    if (!(max > 0.0f) || !(cur < max)) return;
    java.time.Instant now = (({TMR}) store.getResource({TMR}.getResourceType())).getNow();
    float a = amount(rates(cb, ref, now, v.getRegeneratingValues()), pct, f, secs, cur, max);
    if (a > 0.0f) m.addStatValue(mi, a);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("Mana regen in combat failed (logged once): " + t); }}
  }}
}}""", mrg))
# vanilla's base Mana refill per second from the Mana stat asset (5 in vanilla; 0 when it cannot be read) - texts only
mrg.addMethod(CtNewMethod.make(f"""
public static float vanillaRate() {{
  try {{
    {ESTT} t = ({ESTT}) {ESTT}.getAssetMap().getAsset({DST}.getMana());
    if (t == null) return 0.0f;
    {RGN}[] rs = t.getRegenerating();
    if (rs == null) return 0.0f;
    float b = 0.0f;
    for (int i = 0; i < rs.length; i++) b = b + baseOf(rs[i]);
    return b;
  }} catch (Throwable e) {{ return 0.0f; }}
}}""", mrg))
# one text line (no ECS: any thread) - the Server Setup action and /skills mana
mrg.addMethod(CtNewMethod.make(f"""
public static String text(java.util.UUID u) {{
  double p = total(u);
  String[] src = sources(u);
  float base = vanillaRate();
  int f = IN_COMBAT;
  StringBuilder sb = new StringBuilder();
  sb.append("Mana Regen boosts +").append({PKG}.Overall.num(p)).append("%");
  if (src.length == 0) sb.append(" (none registered)");
  else {{
    sb.append(" (");
    for (int i = 0; i < src.length; i++) {{
      if (i > 0) sb.append(", ");
      sb.append(src[i]);
    }}
    sb.append(")");
  }}
  sb.append(". Out of combat: vanilla ").append(base > 0.0f ? {PKG}.Overall.num((double) base) + "/s" : "refill");
  if (p > 0.0 && base > 0.0f) sb.append(" + ").append({PKG}.Overall.num((double) base * p / 100.0)).append("/s");
  if (f <= 0) sb.append(". In combat: vanilla (no refill for 6 s after a hit)");
  else {{
    sb.append(". In combat: ").append(f).append("% of (vanilla + boosts)");
    if (base > 0.0f) sb.append(" = ").append({PKG}.Overall.num((double) base * (1.0 + p / 100.0) * (double) f / 100.0)).append("/s");
  }}
  sb.append(". Never while charging.");
  return sb.toString();
}}""", mrg))
# review fix R4: the action answer is shown by SkyyMenu in ONE status line (firstLine into a 30 px label, about 110 characters fit), so it
# gets its own compact line of at most 110 characters (99 sources or fewer): the numbers first, then as many sources as the rest of the
# 110 leaves, then "+N more" ("N sources" when not even one fits); /skills mana keeps text() in chat.
# Pure (any thread): p = Mana Regen % (total), src = sources(), base = vanilla's refill per second (vanillaRate, 0 = unknown), f = mana.regen.inCombat.
mrg.addMethod(CtNewMethod.make(f"""
public static String compact(double p, String[] src, float base, int f) {{
  String head = "Mana Regen +" + {PKG}.Overall.num(p) + "%";
  double all = (double) base * (1.0 + p / 100.0);
  String tail = "";
  if (base > 0.0f) tail = ". Refill " + {PKG}.Overall.num(all) + "/s, in combat " + (f <= 0 ? "none (vanilla)" : {PKG}.Overall.num(all * (double) f / 100.0) + "/s (" + f + "%)") + ".";
  else tail = ". In combat " + (f <= 0 ? "no refill (vanilla)" : f + "% of the normal refill") + ".";
  int n = src == null ? 0 : src.length;
  String mid = " (no boosts)";
  if (n > 0) {{
    int room = 110 - head.length() - tail.length() - 13;
    StringBuilder l = new StringBuilder();
    int shown = 0;
    for (int i = 0; i < n; i++) {{
      String x = String.valueOf(src[i]);
      if (l.length() + x.length() + 2 > room) break;
      if (shown > 0) l.append(", ");
      l.append(x);
      shown++;
    }}
    if (shown == 0) mid = " (" + n + (n == 1 ? " source)" : " sources)");
    else mid = " (" + l.toString() + (shown < n ? ", +" + (n - shown) + " more)" : ")");
  }}
  return head + mid + tail;
}}""", mrg))
# Server Setup -> Skills -> Overall and Mana -> "Mana Regen: show mine" (an action row: the admin's own numbers; the kit re-checked the node)
mrg.addMethod(CtNewMethod.make("""
public static Object[] showAction(java.util.UUID who, String name) {
  String t = compact(total(who), sources(who), vanillaRate(), IN_COMBAT);
  if (who == null) t = "In game: your own. " + t;
  if (t.length() > 120) t = t.substring(0, 117) + "...";
  return new Object[] { "ok", "", t };
}""", mrg))
# ================= skill:fn:manaregen (0.4.12): the Mana Regen % registry for other mods - java.lang types only, never throws, any thread
#   {"add", UUID, String source, Number percent} -> Boolean  set / replace that source's % (0 removes; clamped -1000..1000)
#   {"remove", UUID, String source} -> Boolean              TRUE = there was an entry
#   {"get", UUID} -> Double                                 the total that applies (0..1000)
#   {"sources", UUID} -> String[]                           "source=+20" entries, sorted
#   {"clear", String source} -> Integer                     that source removed from every player
#   anything else -> null
mrfn.addInterface(pool.get("java.util.function.Function"))
mrfn.addConstructor(CtNewConstructor.make("public ManaRegenFn() { }", mrfn))
mrfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof String)) return null;
    String op = ((String) a[0]).trim().toLowerCase();
    if (op.equals("clear")) {{
      if (!(a[1] instanceof String)) return Integer.valueOf(0);
      return Integer.valueOf({PKG}.ManaRegen.clear((String) a[1]));
    }}
    java.util.UUID u = null;
    if (a[1] instanceof java.util.UUID) u = (java.util.UUID) a[1];
    if (op.equals("get")) return Double.valueOf({PKG}.ManaRegen.total(u));
    if (op.equals("sources")) return {PKG}.ManaRegen.sources(u);
    if (op.equals("add")) {{
      if (u == null || a.length < 4 || !(a[2] instanceof String) || !(a[3] instanceof Number)) return Boolean.FALSE;
      return Boolean.valueOf({PKG}.ManaRegen.put(u, (String) a[2], ((Number) a[3]).doubleValue()));
    }}
    if (op.equals("remove")) {{
      if (u == null || a.length < 3 || !(a[2] instanceof String)) return Boolean.FALSE;
      return Boolean.valueOf({PKG}.ManaRegen.remove(u, (String) a[2]));
    }}
    return null;
  }} catch (Throwable t) {{ return null; }}
}}""", mrfn))

'''
rep('''# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
''', MRG + '''# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
''')
# review fix R3: FIRST after the player's UUID - before Acro.move / airJump / dodge / falls, Brew.tick and Xbow.tick, which share AcroSys's
# one try block (one exception there would skip the refill for that tick); ManaRegen.tick has its own try, so it cannot stop them either
rep('''    java.util.UUID u = pr.getUuid();
    double[] s = {PKG}.Acro.state(u);''', '''    java.util.UUID u = pr.getUuid();
    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own 0.2 s clock, own try; first, so no call below can skip it)
    double[] s = {PKG}.Acro.state(u);''')

# ---------------------------------------------------------------------------------------------------------------- point 2: the pages
# /skills Top 10 view (row level + the rank line): the leaderboard's own slot s
rep('''                                     SUI.J('"Level " + ' + PKG + '.SkillDefs.levelOf(x)', "Level 12"),''',
    '''                                     SUI.J('"Level " + ' + PKG + '.SkillDefs.levelOf(s, x)', "Level 12"),''')
rep('''                                     + '.SkillDefs.levelOf(d[s]) + " - " + ' + PKG + '.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet"',''',
    '''                                     + '.SkillDefs.levelOf(s, d[s]) + " - " + ' + PKG + '.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet"',''')
# the Overall page: "Level 12 of <the highest Overall Level this player can reach>"
rep('''ov_top(_ap, "SkyyOvBody", SUI.J('"Level " + lv + " of " + ' + PKG + '.SkillDefs.MAX', "Level 12 of 100"),''',
    '''ov_top(_ap, "SkyyOvBody", SUI.J('"Level " + lv + " of " + omax', "Level 12 of 100"),''')
# the /skills rows
rep('''      long total = d[sl];
      int lv = {PKG}.SkillDefs.levelOf(total);
      long cur = {PKG}.SkillDefs.intoLevel(total);
      long need = {PKG}.SkillDefs.needFor(total);''', '''      long total = d[sl];
      int lv = {PKG}.SkillDefs.levelOf(sl, total);
      long cur = {PKG}.SkillDefs.intoLevel(sl, total);
      long need = {PKG}.SkillDefs.needFor(sl, total);''')
# the Stats page
rep('''  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(total);
  long cur = {PKG}.SkillDefs.intoLevel(total);
  long need = {PKG}.SkillDefs.needFor(total);''', '''  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(s, total);
  long cur = {PKG}.SkillDefs.intoLevel(s, total);
  long need = {PKG}.SkillDefs.needFor(s, total);''')
rep('''  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.MAX);''',
    '''  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.maxOf(s));''')
# the Overall page (review fix R1: no counted skill = maxLevel 0 is never the max layout; its average line says why nothing moves)
rep('''  int t = {PKG}.Overall.tenths(sc);
  boolean max = lv >= {PKG}.SkillDefs.MAX;''', '''  int t = {PKG}.Overall.tenths(sc);
  int omax = {PKG}.Overall.maxLevel(u);
  boolean max = omax > 0 && lv >= omax;''')
rep('''  String sub = max ? "Average of your skills " + {PKG}.Overall.avg(t) + " - the highest Overall Level" : "Average of your skills " + {PKG}.Overall.avg(t) + " - Overall Level " + (lv + 1) + " at an average of " + (lv + 1) + ".0";
''', '''  String sub = max ? "Average of your skills " + {PKG}.Overall.avg(t) + " - the highest Overall Level" : "Average of your skills " + {PKG}.Overall.avg(t) + " - Overall Level " + (lv + 1) + " at an average of " + (lv + 1) + ".0";
  if (omax <= 0) sub = "No skill counts toward the Overall Level on this server";
''')
rep('''    java.util.ArrayList nx = {PKG}.Overall.nextLines(lv);''', '''    java.util.ArrayList nx = {PKG}.Overall.nextLines(lv, omax);''')
# /skills top <skill> in chat
rep('''      pr.sendMessage({MSG}.raw("  " + (i + 1) + ". " + e[0] + " - level " + {PKG}.SkillDefs.levelOf(x) + " (" + {PKG}.SkillDefs.fmt(x) + " XP)"));''',
    '''      pr.sendMessage({MSG}.raw("  " + (i + 1) + ". " + e[0] + " - level " + {PKG}.SkillDefs.levelOf(s, x) + " (" + {PKG}.SkillDefs.fmt(x) + " XP)"));''')

# ---------------------------------------------------------------------------------------------------------------- point 4 + part 2: rows
rep('''    ("levels", "XP per level (list)", "levels", "text", LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each level needs, level 1 first; the count is the max level (1-100). Easier: the two rows below.",
     "reload;check=SkillKit.checkLevels"),
    ("levels.scale", "Level curve size", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "XP every level needs as % of the default curve (110 = 10% more). Rewrites the XP per level list.", "custom:SkillKit"),
    ("levels.max", "Max level", "levels", "int", "100", "1", "100", "step=5", "", "live,danger",
     "Cuts or extends the list (new levels follow the default curve, cut ones come back until a restart).", "custom:SkillKit"),''',
    '''    ("levels", "XP per level, other skills (list)", "levels", "text", LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each level of every skill but the class skills needs, level 1 first; the count is the max level.",
     "reload;check=SkillKit.checkLevels"),
    ("levels.scale", "Level curve size, other skills", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "XP every non-class level needs as % of the default curve (110 = 10% more). Rewrites the list above.", "custom:SkillKit"),
    ("levels.max", "Max level, other skills", "levels", "int", "100", "1", "100", "step=5", "", "live,danger",
     "Cuts or extends the list (new levels follow the default curve, cut ones come back until a restart).", "custom:SkillKit"),
    # 0.4.12 (Skyy 2026-10-02 Q&A round 1, research/cloud/Class-Skill-Curve-Proposal.md section 4): the class skill table - the list first
    # (import / restore apply rows in this order, the two class curve rows read it)
    ("levels.class", "Class skill XP per level (list)", "levels", "text", CLASS_LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each class skill level needs (Archery, Sorcery...), level 1 first; the count is the class max.",
     "reload;check=SkillKit.checkLevels"),
    ("levels.class.scale", "Class level curve size", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "Class skill XP per level as % of Skyy's class curve. Never more than the other list asks.", "custom:SkillKit"),
    ("levels.class.max", "Class max level", "levels", "int", "100", "1", "100", "step=5", "", "live,danger",
     "Cuts or extends the class list (new levels follow the class curve; cut ones return until a restart).",
     "custom:SkillKit"),
    ("levels.class.sameAsOthers", "Class skills use the other list", "levels", "bool", "false", "", "", "", "", "live,danger",
     "On: class skills use the list of the other skills again (the old, slower curve; levels drop back).",
     "reload;confirm=on"),''')
rep('''    ("overall.chat", "Overall level-up chat line", "overall", "bool", "true", "", "", "", "", "live",
     "Off: nobody gets the line. On: each player can still hide theirs in /settings.", "reload"),
]''', '''    ("overall.chat", "Overall level-up chat line", "overall", "bool", "true", "", "", "", "", "live",
     "Off: nobody gets the line. On: each player can still hide theirs in /settings.", "reload"),
    # 0.4.12 (Skyy 2026-10-02 Q&A rounds 1-2): Mana refills in combat at this % of (vanilla + Mana Regen boosts); 0 = vanilla
    ("mana.regen.inCombat", "In-combat Mana regen", "overall", "int", MREG_DEF, "0", "100", "step=5", "%", "live",
     "Mana refill for 6 s after you take damage, as % of the normal refill + boosts. 0 = vanilla (none).", "reload"),
    ("mana.regen.show", "Mana Regen: show mine", "overall", "action", "", "", "", "Show my Mana Regen", "", "live",
     "Your Mana Regen boosts (other mods register them, none yet) and the refill in and out of combat.",
     "action:ManaRegen.showAction"),
]''')
rep('''assert len(CFG_ROWS) == 174, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10''',
    '''assert len(CFG_ROWS) == 180, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier; 0.4.12: + the 4 class curve "
                              "rows + mana.regen.inCombat + the mana.regen.show action, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10 / 0.4.12
# 0.4.12: the new keys once each; levels.class / sameAsOthers / mana.regen.inCombat in the default file (= the row default) and in their
# appended blocks; the class rows right after the three general curve rows, the list first
_k12 = [_r[0] for _r in CFG_ROWS]
assert _k12[_k12.index("levels"):_k12.index("levels") + 7] == ["levels", "levels.scale", "levels.max", "levels.class", "levels.class.scale",
                                                                 "levels.class.max", "levels.class.sameAsOthers"], _k12[_k12.index("levels"):][:7]
for _k, _blk12 in (("levels.class", CURVE_DEFAULTS), ("levels.class.sameAsOthers", CURVE_DEFAULTS), ("mana.regen.inCombat", MREG_DEFAULTS)):
    _rw = [_r for _r in CFG_ROWS if _r[0] == _k]
    assert len(_rw) == 1 and _dp.get(_k) == _rw[0][4] and ("\\n" + _k + "=" + _rw[0][4] + "\\n") in ("\\n" + _blk12), _k
assert sum(1 for _r in CFG_ROWS if _r[0] in ("levels.class.scale", "levels.class.max", "mana.regen.show")) == 3
assert [_r for _r in CFG_ROWS if _r[0] == "levels.class"][0][4] == CLASS_LEVELS_TEXT and _dp.get("levels.class") == CLASS_LEVELS_TEXT''')
rep('''               NOTE="Hand edits of xp.properties: /skills reload. Levels tab: curve size % and max level.")''',
    '''               NOTE="Hand edits of xp.properties: /skills reload. Levels tab: class and other skills' curves.")''')

# ---------------------------------------------------------------------------------------------------------------- point 4: SkillKit
rep('''skit.addMethod(CtNewMethod.make("""
public static String customGet(String key) {
  if ("spell.manaDivisor".equals(key)) return String.valueOf(""" + PKG + """.ManaCost.DIVISOR);
  long[] l = curList();
  if ("levels.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  return null;
}""", skit))''', '''# 0.4.12: the class curve rows - the same helpers against the default CLASS table (the d argument) and their own TAIL / LAST memory
skit.addField(CtField.make("public static long[] CTAIL = null;", skit))
skit.addField(CtField.make("public static long[] CLAST = null;", skit))
skit.addMethod(CtNewMethod.make(f"""
public static long[] curListC() {{
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "get", "levels.class" }});
    if (o instanceof String) {{
      long[] r = parseList((String) o);
      if (r != null) return r;
    }}
  }} catch (Throwable t) {{ }}
  long[] p = {PKG}.SkillDefs.CPER;
  long[] c = new long[p.length];
  for (int i = 0; i < p.length; i++) c[i] = p[i];
  return c;
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static long pctOfD(long[] l, long[] d) {
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < l.length; i++) {
    a += (double) l[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }
  if (b <= 0.0) return 100L;
  return Math.round(a * 100.0 / b);
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static long[] withMaxD(long[] cur, int n, long[] d) {
  int len = cur.length;
  long[] r = new long[n];
  int li = len - 1 < d.length ? len - 1 : d.length - 1;
  double base = (double) d[li];
  double f = base > 0.0 ? (double) cur[len - 1] / base : 1.0;
  for (int i = 0; i < n; i++) {
    if (i < len) { r[i] = cur[i]; continue; }
    long di = i < d.length ? d[i] : d[d.length - 1];
    long v = Math.round((double) di * f);
    r[i] = v < 1L ? 1L : v;
  }
  return r;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static long[] scaledToD(long[] cur, long pct, long[] d) {
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < cur.length; i++) {
    a += (double) cur[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }
  if (a <= 0.0 || b <= 0.0) return null;
  double f = ((double) pct / 100.0) * b / a;
  long[] r = new long[cur.length];
  for (int i = 0; i < cur.length; i++) {
    double v = (double) cur[i] * f;
    if (v > 1.0E15) return null;
    long x = Math.round(v);
    r[i] = x < 1L ? 1L : x;
  }
  return r;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized long[] tailForC(long[] cur) {
  long[] t = CTAIL;
  if (t == null || t.length <= cur.length || !sameList(cur, CLAST)) return cur;
  for (int i = 0; i < cur.length; i++) if (t[i] != cur[i]) return cur;
  return t;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void keepTailC(long[] cur) {
  if (tailForC(cur) != cur) return;
  long[] c = new long[cur.length];
  for (int i = 0; i < cur.length; i++) c[i] = cur[i];
  CTAIL = c;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void setLastC(long[] l) {
  long[] c = new long[l.length];
  for (int i = 0; i < l.length; i++) c[i] = l[i];
  CLAST = c;
}""", skit))
# review fix R5: what class skills need NOW = the EFFECTIVE class table (SkillDefs.ECUM = min(class list, other list) up to the class max),
# not the raw list a curve row wrote ("level 1 needs 75 XP" at 150% while class skill 1 still comes at 50) - total XP for class skill 1,
# 20 and the class max; nothing while levels.class.sameAsOthers is on (class skills then level on the other list)
skit.addMethod(CtNewMethod.make(f"""
public static String classTotals() {{
  if ({PKG}.SkillDefs.SAME) return "not in use while Class skills use the other list is on";
  long[] e = {PKG}.SkillDefs.ECUM;
  int top = e.length - 1;
  if (top < 1) return "no class levels";
  StringBuilder sb = new StringBuilder();
  sb.append("class skill 1 at ").append({PKG}.SkillDefs.fmt(e[1])).append(" XP");
  if (top > 20) sb.append(", 20 at ").append({PKG}.SkillDefs.fmt(e[20]));
  if (top > 1) sb.append(", ").append(top).append(" at ").append({PKG}.SkillDefs.fmt(e[top]));
  return sb.append(" in total").toString();
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static String customGet(String key) {
  if ("spell.manaDivisor".equals(key)) return String.valueOf(""" + PKG + """.ManaCost.DIVISOR);
  if ("levels.class.max".equals(key)) return String.valueOf(curListC().length);
  if ("levels.class.scale".equals(key)) return String.valueOf(pctOfD(curListC(), """ + PKG + """.SkillDefs.DEFAULT_CPER));
  long[] l = curList();
  if ("levels.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  return null;
}""", skit))''')
rep('''  }} else if ("levels.scale".equals(key)) {{
    if (n < 10L || n > 1000L) return new Object[] {{ "bad", null, "Must be a whole number from 10 to 1000%." }};
    nl = scaledTo(cur, n);
    if (nl == null) return new Object[] {{ "bad", null, "That would make a level need more than 1000000000000000 XP." }};
    msg = "Level curve size: " + pctOf(nl) + "% of the default - level 1 needs " + {PKG}.SkillDefs.fmt(nl[0]) + " XP, level " + nl.length + " needs " + {PKG}.SkillDefs.fmt(nl[nl.length - 1]) + ". Saved (applies now).";
  }} else {{
    return new Object[] {{ "unknown", null, "Unknown setting: " + key + "." }};
  }}
  {PKG}.SkillDefs.setTable(nl);
  armReload();
  armLater();
  String val = "levels.max".equals(key) ? String.valueOf(nl.length) : String.valueOf(pctOf(nl));
  return new Object[] {{ "ok", val, msg, new String[] {{ "levels", join(nl) }} }};
}}""", skit))''', '''  }} else if ("levels.scale".equals(key)) {{
    if (n < 10L || n > 1000L) return new Object[] {{ "bad", null, "Must be a whole number from 10 to 1000%." }};
    nl = scaledTo(cur, n);
    if (nl == null) return new Object[] {{ "bad", null, "That would make a level need more than 1000000000000000 XP." }};
    msg = "Level curve size: " + pctOf(nl) + "% of the default - level 1 needs " + {PKG}.SkillDefs.fmt(nl[0]) + " XP, level " + nl.length + " needs " + {PKG}.SkillDefs.fmt(nl[nl.length - 1]) + ". Saved (applies now).";
  }} else if ("levels.class.max".equals(key)) {{
    // 0.4.12: the class skill list, the levels.max rules against the default CLASS table (own CTAIL / CLAST memory)
    if (n < 1L || n > 100L) return new Object[] {{ "bad", null, "Must be a whole number from 1 to 100." }};
    long[] cc = curListC();
    int clen = cc.length;
    long[] src = cc;
    if (n < (long) clen) keepTailC(cc);
    else if (n > (long) clen) src = tailForC(cc);
    nl = withMaxD(src, (int) n, {PKG}.SkillDefs.DEFAULT_CPER);
    setLastC(nl);
    int back = src.length < (int) n ? src.length : (int) n;
    if (n < (long) clen) msg = "Class max level: " + n + " (was " + clen + ") - class skill levels above " + n + " removed; players keep their XP; raising it again gives them back exactly (until a restart or another class curve change). Saved (applies now).";
    else if (n > (long) clen && back > clen) msg = "Class max level: " + n + " (was " + clen + ") - class levels " + (clen + 1) + " to " + back + " back with the XP they had before the cut" + (back < (int) n ? ", " + (back + 1) + " to " + n + " added along the class curve" : "") + ". Saved (applies now).";
    else if (n > (long) clen) msg = "Class max level: " + n + " (was " + clen + ") - class levels " + (clen + 1) + " to " + n + " added along the class curve. Saved (applies now).";
    else msg = "Class max level is already " + n + ".";
    cls = true;
  }} else if ("levels.class.scale".equals(key)) {{
    if (n < 10L || n > 1000L) return new Object[] {{ "bad", null, "Must be a whole number from 10 to 1000%." }};
    nl = scaledToD(curListC(), n, {PKG}.SkillDefs.DEFAULT_CPER);
    if (nl == null) return new Object[] {{ "bad", null, "That would make a level need more than 1000000000000000 XP." }};
    msg = null;   // review fix R5: written below from the EFFECTIVE class table, once setClassTable has rebuilt it
    cls = true;
  }} else {{
    return new Object[] {{ "unknown", null, "Unknown setting: " + key + "." }};
  }}
  if (cls) {PKG}.SkillDefs.setClassTable(nl, {PKG}.SkillDefs.SAME);
  else {PKG}.SkillDefs.setTable(nl);
  if (msg == null) msg = "Class level curve size: " + pctOfD(nl, {PKG}.SkillDefs.DEFAULT_CPER) + "% - " + classTotals() + ". Saved (applies now).";
  {PKG}.SkillStore.republishAll();   // review fix R9: skill:<uuid> (SkyyHud) follows the new curve at the next 5 s publish
  armReload();
  armLater();
  String val = ("levels.max".equals(key) || "levels.class.max".equals(key)) ? String.valueOf(nl.length) : String.valueOf(cls ? pctOfD(nl, {PKG}.SkillDefs.DEFAULT_CPER) : pctOf(nl));
  return new Object[] {{ "ok", val, msg, new String[] {{ cls ? "levels.class" : "levels", join(nl) }} }};
}}""", skit))''')
rep('''  long[] cur = curList();
  int len = cur.length;
  long[] nl = null;
  String msg = "";
  if ("levels.max".equals(key)) {{''', '''  long[] cur = curList();
  int len = cur.length;
  long[] nl = null;
  String msg = "";
  boolean cls = false;
  if ("levels.max".equals(key)) {{''')
rep('''public static String customRead(String key, java.util.Map vals) {{
  long[] l = null;
  try {{
    Object o = vals == null ? null : vals.get("levels");
    if (o instanceof String) l = parseList((String) o);
  }} catch (Throwable t) {{ l = null; }}
  if (l == null) l = {PKG}.SkillDefs.DEFAULT_PER;
  if ("levels.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  return null;
}}""", skit))''', '''public static String customRead(String key, java.util.Map vals) {{
  boolean c = key != null && key.startsWith("levels.class.");
  long[] l = null;
  try {{
    Object o = vals == null ? null : vals.get(c ? "levels.class" : "levels");
    if (o instanceof String) l = parseList((String) o);
  }} catch (Throwable t) {{ l = null; }}
  if (l == null) l = c ? {PKG}.SkillDefs.DEFAULT_CPER : {PKG}.SkillDefs.DEFAULT_PER;
  if ("levels.max".equals(key) || "levels.class.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  if ("levels.class.scale".equals(key)) return String.valueOf(pctOfD(l, {PKG}.SkillDefs.DEFAULT_CPER));
  return null;
}}""", skit))''')

# ---------------------------------------------------------------------------------------------------------------- part 2: /skills mana
MCMD = r'''# /skills mana (0.4.12 admin debug): the caller's LIVE Mana regen - Mana now / max, in or out of combat (the regen entry's own conditions,
# like ManaRegen.tick), the last hit, what SkyySkills adds right now, the Mana Regen boosts. World thread (AbstractPlayerCommand runs execute
# on the player's world); admin only: requirePermission + no groups (HANDOFF command rules, lint perm_group_leaks).
mcmd.addConstructor(CtNewConstructor.make('public ManaCmd() { super("mana", "(admin) Your live Mana regen: in or out of combat, boosts, rates"); requirePermission("skyyskills.admin"); setPermissionGroups(new String[0]); }', mcmd))
mcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (!pr.hasPermission("skyyskills.admin")) {{ pr.sendMessage({MSG}.raw("[Skills] no permission (skyyskills.admin)")); return; }}
    java.util.UUID u = pr.getUuid();
    {ESM} m = ({ESM}) store.getComponent(ref, {ESM}.getComponentType());
    int mi = {DST}.getMana();
    {ESV} v = null;
    if (m != null && mi >= 0) v = m.get(mi);
    if (v == null) pr.sendMessage({MSG}.raw("[Skills] Mana: this player has no Mana value").color("#c8b070"));
    else {{
      java.time.Instant now = (({TMR}) store.getResource({TMR}.getResourceType())).getNow();
      float[] r = {PKG}.ManaRegen.rates(store, ref, now, v.getRegeneratingValues());
      double p = {PKG}.ManaRegen.total(u);
      int f = {PKG}.ManaRegen.IN_COMBAT;
      String st;
      if (!(v.getMax() > 0.0f)) st = "no Mana pool (max 0) - nothing refills";
      else if (r[1] > 0.0f) st = "out of combat - vanilla refills " + {PKG}.Overall.num((double) r[1]) + "/s" + (p > 0.0 ? ", SkyySkills adds " + {PKG}.Overall.num((double) r[1] * p / 100.0) + "/s" : "");
      else if (r[2] > 0.0f) st = "IN COMBAT (vanilla's 6 s pause) - SkyySkills refills " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0) + "/s (" + f + "% of " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0)) + "/s)";
      else st = "no refill right now (holding a charge, or dead)";
      String hit = "";
      try {{
        {DDC} dd = ({DDC}) store.getComponent(ref, {DDC}.getComponentType());
        if (dd != null && dd.getLastDamageTime() != null) {{
          long ms = java.time.Duration.between(dd.getLastDamageTime(), now).toMillis();
          if (ms >= 0L && ms < 86400000L) hit = " - last hit " + {PKG}.Overall.num((double) ms / 1000.0) + " s ago";
        }}
      }} catch (Throwable t) {{ }}
      pr.sendMessage({MSG}.raw("[Skills] Mana " + {PKG}.Overall.num((double) v.get()) + " / " + {PKG}.Overall.num((double) v.getMax()) + " - " + st + hit).color("#c8b070"));
    }}
    pr.sendMessage({MSG}.raw("[Skills] " + {PKG}.ManaRegen.text(u)).color("#c8b070"));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills mana failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not read your Mana regen"));
  }}
}}""", mcmd))
'''
rep('''cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{''', MCMD + '''cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{''')
rep('''  addSubCommand(new {PKG}.XpCmd());
}}""", cmd))''', '''  addSubCommand(new {PKG}.XpCmd());
  addSubCommand(new {PKG}.ManaCmd());
}}""", cmd))''')
rep('''  super("skills", "Open your skills page; /skills stats <skill>, /skills top <skill>, /skills quiet");''',
    '''  super("skills", "Open your skills page; /skills stats <skill>, /skills top <skill>, /skills quiet (admins: /skills mana)");''')

# ---------------------------------------------------------------------------------------------------------------- the ticker + the plugin
rep('''  try {{ {PKG}.ManaGuard.tick(this.n); }} catch (Throwable t) {{ }}
}}""", tick))''', '''  try {{ {PKG}.ManaGuard.tick(this.n); }} catch (Throwable t) {{ }}
  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12: the class skill curve record (only after a notice was told)
}}""", tick))''')
rep('''  String rules = {PKG}.SkillCfg.load();
  {PKG}.Acro.djPublish();''', '''  String rules = {PKG}.SkillCfg.load();
  String curve = {PKG}.ClassCurve.start(base);   // 0.4.12: the first 0.4.12 start records once which profiles' class levels rose
  {PKG}.Acro.djPublish();''')
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:overall", new {PKG}.OverallFn());
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:overall", new {PKG}.OverallFn());
  {PKG}.SkillStore.bridge().put("skill:fn:manaregen", new {PKG}.ManaRegenFn());   // 0.4.12: the Mana Regen % registry
''')
rep('''"; bridge skill:fn:addxp + skill:fn:craftxp + skill:fn:healxp (optional Boolean self) + skill:fn:overall + skill:overall:<uuid>; trees bridge on''',
    '''"; class skills level on " + {PKG}.SkillCfg.curveText() + (curve.length() > 0 ? " (" + curve + ")" : "") + "; in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "% of (vanilla + Mana Regen boosts)" + "; bridge skill:fn:addxp + skill:fn:craftxp + skill:fn:healxp (optional Boolean self) + skill:fn:overall + skill:overall:<uuid> + skill:fn:manaregen; trees bridge on''')
rep('''  try {{ if (!{PKG}.SkillStore.DIRTY.isEmpty()) {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}
''', '''  try {{ if (!{PKG}.SkillStore.DIRTY.isEmpty()) {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12
''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:overall"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:overall"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:manaregen"); }} catch (Throwable t) {{ }}   // 0.4.12
''')
rep('''          mcost, mmig, mgd, hmig):   # 0.4.11: + HealMig''', '''          mcost, mmig, mgd, hmig, ccv, mrg, mrfn, mcmd):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd''')

# ---------------------------------------------------------------------------------------------------------------- manifest
rep('''Priest heal XP is what the Priest gets: 1 per HP on others, 1.25 on yourself, up to 900 a minute (Server Setup).''',
    '''Priest heal XP is what the Priest gets: 1 per HP on others, 1.25 on yourself, up to 900 a minute (Server Setup). Class skills level on their own, flatter table (class skill 20 at 21,540 XP, 40 at 209,090; never slower than the other skills' table; Server Setup Levels tab) - existing XP is kept and players are told once, with the coins of the levels they gained. Mana refills in combat at 50% (Server Setup: In-combat Mana regen; vanilla stops it for 6 s after a hit), boosts other mods register count in and out of combat.''')
_mf0 = s.rindex('m = B.manifest("SkyySkills", VERSION, "') + 39
assert '"' not in s[_mf0:s.index('", PKG + ".SkyySkillsPlugin")', _mf0)], "a quote inside the manifest text"

# ---------------------------------------------------------------------------------------------------------------- engine probes
rep('''# 0.4.8 (Skyy 2026-09-30): every vanilla spell's Mana cost / SPELL_DIVISOR (the SPELL GEN block builds the item overrides)
SPELL_DIVISOR = 5''', '''# 0.4.12 Mana regen in combat (research/Mana-Cost-And-Regen-Research.md 2.1-2.2; the SkyyAccessories 0.5 Stamina Regen calls + the single
# condition, read in HytaleServer.jar bytecode 2026-10-02): the Mana value's regen entries, each condition evaluated on its own
# (Condition.eval = eval0 != inverse; NoDamageTakenCondition.eval0 = now - DamageDataComponent.lastDamageTime >= Delay), the store's clock
RGV = "com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue"
RGN = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating"
RGT = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating$RegenType"
CND = "com.hypixel.hytale.server.core.modules.entity.condition.Condition"
NDT = "com.hypixel.hytale.server.core.modules.entity.condition.NoDamageTakenCondition"
TMR = "com.hypixel.hytale.server.core.modules.time.TimeResource"
DDC = "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent"
for c, m in ((ESV, "getRegeneratingValues"), (RGV, "getRegenerating"), (RGN, "getRegenType"), (RGN, "getAmount"), (RGN, "getInterval"),
             (RGN, "getConditions"), (RGT, "ADDITIVE"), (CND, "eval"), (NDT, "eval0"), (TMR, "getResourceType"), (TMR, "getNow"),
             (ST, "getResource"), (ESV, "get"), (ESV, "getMax"), (ESM, "addStatValue"), (ESTT, "getRegenerating"), (DDC, "getLastDamageTime"),
             (DDC, "getComponentType"), (DST, "getMana")):
    B.probe(pool, c, m)
for c, m, d in ((CND, "eval", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (RGN, "getConditions", "()[L" + CND.replace(".", "/") + ";"),
                (ESV, "getRegeneratingValues", "()[L" + RGV.replace(".", "/") + ";"),
                (RGV, "getRegenerating", "()L" + RGN.replace(".", "/") + ";"),
                (TMR, "getNow", "()Ljava/time/Instant;"), (DDC, "getLastDamageTime", "()Ljava/time/Instant;"),
                (ESTT, "getRegenerating", "()[L" + RGN.replace(".", "/") + ";")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
assert pool.get(NDT).subclassOf(pool.get(CND)), "NoDamageTakenCondition is no longer a Condition"
# 0.4.8 (Skyy 2026-09-30): every vanilla spell's Mana cost / SPELL_DIVISOR (the SPELL GEN block builds the item overrides)
SPELL_DIVISOR = 5''')
rep('''if _mana.get("Max") not in (0, 0.0):''', '''# 0.4.12: in-combat Mana regen rests on vanilla's combat pause = a NoDamageTaken condition on a positive Additive Mana regen entry
_mpause = [r for r in _mreg if str(r.get("RegenType", "")).lower() == "additive" and float(r.get("Amount") or 0) > 0 and float(r.get("Interval") or 0) > 0
           and any(c.get("Id") == "NoDamageTaken" and not c.get("Inverse") for c in (r.get("Conditions") or []))]
assert _mpause, "vanilla Mana.json has no Additive regen entry paused by NoDamageTaken any more - the in-combat Mana regen would never run"
print("in-combat Mana regen: vanilla refills %s Mana a second, paused %s s after taking damage; SkyySkills refills %s%% of (vanilla + boosts) there" % (
    sum(float(r["Amount"]) / float(r["Interval"]) for r in _mpause), ",".join(str(c.get("Delay")) for r in _mpause for c in r.get("Conditions") or []
                                                                               if c.get("Id") == "NoDamageTaken"), MREG_DEF))
if _mana.get("Max") not in (0, 0.0):''')

# ---------------------------------------------------------------------------------------------------------------- review fix R9
# skill:<uuid> (the levels string SkyyHud reads) is only republished on a level up, a class change or a new session - publishOnline skips a
# player it has published - so a live curve change (Server Setup rows, /skills reload, the kit's reload after a save) left the old class
# level on the HUD until the next level up or relog. republishAll forgets who is published; the next 5 s publishOnline republishes every
# online player (memory only for loaded players). Under PUB, which publishNow holds while it reads the tables: a publish that ran before
# this used the old table and is forgotten, one after it reads the new table (every caller sets the tables first). One call inside the lock.
rep('''    PUBLISHED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", sto))
''', '''    PUBLISHED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", sto))
# review fix R9 (0.4.12): forget who is published after a live level table change - publishOnline republishes everyone within 5 s
sto.addMethod(CtNewMethod.make("""
public static void republishAll() {
  synchronized (PUB) { PUBLISHED.clear(); }
}""", sto))
''')
rep('''public static String reload() {{
  String r = {PKG}.SkillCfg.load();
  {PKG}.Acro.djPublish();
  return r;
}}""", skit))''', '''public static String reload() {{
  String r = {PKG}.SkillCfg.load();
  {PKG}.SkillStore.republishAll();   // review fix R9 (0.4.12): a curve change in the file reaches skill:<uuid> within 5 s
  {PKG}.Acro.djPublish();
  return r;
}}""", skit))''')
rep('''  String res = {PKG}.SkillCfg.load();
  {PKG}.Acro.djPublish();
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + res + kr));''', '''  String res = {PKG}.SkillCfg.load();
  {PKG}.SkillStore.republishAll();   // review fix R9 (0.4.12)
  {PKG}.Acro.djPublish();
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + res + kr));''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
# no global level lookup is left anywhere (javassist would refuse one too); every SkillDefs level call names its slot
for _old in (".SkillDefs.levelOf(total)", ".SkillDefs.intoLevel(total)", ".SkillDefs.needFor(total)", ".SkillDefs.levelOf(x)",
             ".SkillDefs.levelOf(d[", ".SkillDefs.progress(d[", ".SkillDefs.progress(r[2])", ".SkillDefs.needFor(r[2])", "levelOf(ba[",
             "levelOf(rd(d, skill))", "levelOf(data(u)[skill])"):
    assert _old not in s, "a global level lookup is left: " + _old
assert "public static int levelOf(long total)" not in s and "public static String progress(long total)" not in s
assert re.findall(r"SkillDefs\.MAX\b", s) == ["SkillDefs.MAX"], "SkillDefs.MAX (the general max) is only left in the load text: %r" % re.findall(r"SkillDefs\.MAX\b", s)
# methods before callers: ClassCurve before SkillXp (gain4) and Perks (tick); ManaRegen before AcroSys; ManaCmd before SkillsCmd
assert s.index('ccv.addMethod(CtNewMethod.make(f"""\npublic static void tick(') < s.index("public static void gain4(") < s.index("public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref)")
assert s.index('mrg.addMethod(CtNewMethod.make(f"""\npublic static void tick(') < s.index('asy.addMethod(CtNewMethod.make(f"""\npublic void tick(')
assert s.index("mcmd.addConstructor(") < s.index("public SkillsCmd() {{")
assert s.index("public static int maxLevel(java.util.UUID u)") < s.index("public static java.util.ArrayList nextLines(int lv, int top)")
assert s.index("{PKG}.ClassCurve.start(base);") > s.index("String rules = {PKG}.SkillCfg.load();")
assert s.count("{PKG}.ClassCurve.tick(pr, u);") == 2 and s.count("{PKG}.ManaRegen.tick(u, store, cb, ref, dt);") == 1
# review fixes: R3 the Mana refill is AcroSys.tick's first call after the UUID (before the Acrobatics block, Brew and the crossbow); R9
# republishAll exists before its three callers (SkillKit.customSet / reload, /skills reload) and each calls it after setting the tables;
# R4 compact before showAction; R5 classTotals before customSet and the scale message built after setClassTable; R1 the page guard
_asy = s.index('asy.addMethod(CtNewMethod.make(f"""\npublic void tick(')
assert (_asy < s.index("{PKG}.ManaRegen.tick(u, store, cb, ref, dt);") < s.index("    double[] s = {PKG}.Acro.state(u);", _asy)
        < s.index("    if ({PKG}.AcroCfg.ENABLED) {{", _asy) < s.index("    {PKG}.Brew.tick(u, store, cb, ref, dt);", _asy) < s.index("    {PKG}.Xbow.tick(store, ref, pr, u);", _asy))
assert s.count("{PKG}.SkillStore.republishAll();") == 3 and s.count("public static void republishAll()") == 1
assert s.index("public static void republishAll()") < min(s.index("public static String reload() {{"), s.index("public ReloadCmd()"),
                                                           s.index("public static Object[] customSet(String key, String value)"))
for _a, _b in (("String r = {PKG}.SkillCfg.load();", "{PKG}.SkillStore.republishAll();"), ("String res = {PKG}.SkillCfg.load();", "{PKG}.SkillStore.republishAll();"),
               ("  else {PKG}.SkillDefs.setTable(nl);\n  if (msg == null) msg = ", "  {PKG}.SkillStore.republishAll();")):
    assert s.index(_a) < s.index(_b, s.index(_a)) < s.index(_a) + 200, (_a, _b)
assert s.index("public static String compact(double p, String[] src, float base, int f)") < s.index("public static Object[] showAction(java.util.UUID who, String name)")
assert s.index("public static String classTotals()") < s.index("public static Object[] customSet(String key, String value)")
assert s.count("boolean max = omax > 0 && lv >= omax;") == 1 and s.count("  if (omax <= 0) sub = ") == 1 and s.count("if (top <= 0) {{ out.add(") == 1
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars")
