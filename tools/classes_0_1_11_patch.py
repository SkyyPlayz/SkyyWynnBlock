"""Derive SkyyClasses/build_skyyclasses_0.1.11.py from the LIVE 0.1.10 (build_skyyclasses_0.1.10.py = the tools/deploy_set.py SET pin).
Run:  python tools/classes_0_1_11_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.11.py   (never --deploy: coordinated deploy)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_10_patch.py
-> the generated 0.1.10 read here; tools/classes_0_1_6_patch.py is NEVER re-run. Edit THIS file, never the generated build script.

0.1.11 = the Priest HEAL CAPS grow with the shot (Skyy 2026-10-03, OPEN-QUESTIONS "ANSWERED 2026-10-03 morning": "RAISE THE CAPS so
charged shots heal clearly more than taps"; the rule = research/SkyyArmory-Spec.md section 15.5, critic + editor checked):
  - CHARGED wand shot: per-hit cap = max(priestHeal.maxPerHit, priestHeal.hpPerMana x the wand's charged Mana). The Mana comes from
    SkyyArmory 0.1+ (bridge armory:fn:info, Object[]{"wand", itemId} -> Object[]{Integer charged, Integer quick, ...} or null): Wood 5,
    Copper 10, Iron 15, Thorium 25, Cobalt 40, Adamantite 60, Mithril / Onyxium 85 -> caps 10 / 20 / 30 / 50 / 80 / 120 / 170 at the
    default hpPerMana 2 (never below the maxPerHit floor - Skyy's live 50 keeps Wood..Thorium at 50).
  - QUICK shot (tap; its projectile id is in SkyyArmory's armory:quick list): cap = the charged cap x priestHeal.quickPercent / 100
    (default 20 = 1/5 = the quick shot's Mana share, so healing per Mana is the same for both shots - a charged hit heals 5x a tap).
  - EVERY OTHER Priest hit keeps today's rule (cap = maxPerHit): spellbooks, melee (no projectile), the totem, a wand SkyyArmory does
    not know, or no SkyyArmory at all. hpPerMana 0 + quickPercent 100 = exactly today's rule.
  - PER SECOND: the target's fixed 1 s window (shared by all Priests) allows max(priestHeal.maxPerSecond, the biggest hit cap that
    reached that player in the window) - at most one charged heal's worth per second; Skyy's live 1000 still wins.
  - The heal itself stays min(sharePercent x the landed damage, cap), overheal clamped first; the Priest's own heal = selfPercent of a
    member's (unchanged). Divinity heal XP: unchanged calls (skill:fn:healxp with the healed HP; self with the trailing Boolean.TRUE) -
    SkyySkills' rule stays 1 XP per HP on others, 1.25 on yourself, at most 900 a minute.
  Engine: ShotRec gains pid = ProjectileComponent.getProjectileAssetName() at launch (ShotTrack.onEntityAdded now always reads the
  legacy ProjectileComponent; null for a physics-only projectile); PriestHealSys passes (item, pid) to HealTask; HealTask.cap(item, pid)
  -> capOf (pure); HealBudget.take(u, want, now, perSec, hitCap) keeps {start, used, top} per target. armory:quick is parsed only when
  the bridge value changes (one volatile holder). Everything stays on the world thread, as in 0.1.10.
  FIX ROUND (review of the Armory round, 2026-10-03):
  - THE WAND'S OWN SHOTS ONLY: the big cap used to follow the item in hand - a bomb, a Fireball or another wand's orb launched with a
    Mithril wand in hand got the 170 cap. SkyyArmory's armory:fn:info now also answers the wand's own charged and quick projectile ids
    (elements 6 + 7); HealTask.caps raises the cap only when the shot's pid is one of THOSE (quick id -> the tap cap, charged id -> the
    charged cap), any other projectile keeps maxPerHit. An older 6-element answer keeps the first build's rule (armory:quick decides).
  - THE PER-SECOND WINDOW TOP: a tap used to raise the 1 s window only to its own cap (Mithril 34), so with maxPerSecond 10 only one tap
    in three healed (0.67 HP per Mana against 2 for charged shots - the "same healing per Mana" of quickPercent 20 was false). A wand shot
    (tap or charged) now raises the window to that WAND'S CHARGED cap; the heal itself keeps the tap's cap. Still at most one charged
    heal's worth per second from all Priests together; Skyy's live maxPerSecond 1000 is unaffected.
  - The Mage card text no longer says "Staves strike up close" (the staff tap is a quick shot since SkyyArmory 0.1; neutral wording also
    holds if Skyy keeps the spear swing - question S2). SkyyProfiles 0.1.5 carries the same old line (its next build).
  Rows (Server Setup -> Classes -> Priest heal, all live; existing keys kept, so NO migration and Skyy's 50 / 1000 stay): NEW
  priestHeal.hpPerMana (dec 0-50, default 2), NEW priestHeal.quickPercent (int 0-100 %, default 20); maxPerHit relabelled "Most HP per
  hit (at least)", maxPerSecond "Most HP per second (at least)". A file without the new keys reads their code defaults (ClassCfg dbl /
  lng), so the live config needs no change. The fresh default file carries the two new lines + the rule in its comments.
Everything else (the /class page, the shared SKYY CARD block = CARD_SHA of SkyyProfiles 0.1.4, commands, permissions, bridge keys,
class rules, kits + the off-hand, arrows, claims, the heal chat lines, DamageLock, DeployGuard, migrate0110) is 0.1.10's - asserted
below. Harness: SkyyClasses/test_skyyclasses_0.1.11.py.
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.10.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.11.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
# the source must be the generated 0.1.10 of the EDITED lineage
assert 'VERSION = "0.1.10"' in s and "GENERATED by tools/classes_0_1_10_patch.py from the LIVE 0.1.9" in s, \
    "build_skyyclasses_0.1.10.py is not the live 0.1.10"
assert "DEF_HEAL_MSG_MS = 10000   # LOCKED Skyy 2026-09-25" in s and "DEF_HEAL_SELF_PCT = 100 " in s, "0.1.10 is not the edited-lineage script"
REG0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
SYS0 = [ln for ln in s.split(LF) if "registerSystem(" in ln]


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


def block(a, b, text=None):
    """the text from anchor a (included) to anchor b (excluded) of `text` (default: the CURRENT source)"""
    t = s if text is None else text
    assert t.count(a) == 1 and t.count(b) == 1, (a[:60], b[:60])
    return t[t.index(a):t.index(b)]


# ================================================================================================ blocks that must stay 0.1.10's
CARD_START = "# =====================================================================================================================\n# SKYY CARD"
CARD_END = "# ======================================================================= (end of the shared SKYY CARD block)"
CARD_SHA = "bf659e0208b537a81ac8758d909f81976f03069816ea9dddb300f843a7eaa028"   # = tools/profiles_0_1_4_patch.py + classes_0_1_9/10_patch.py
_card = block(CARD_START, CARD_END) + CARD_END
assert hashlib.sha256(_card.encode("utf8")).hexdigest() == CARD_SHA, "the 0.1.10 SKYY CARD block is not SkyyProfiles 0.1.4's"
KEEP = [
    _card,                                                                                                    # the shared card component
    block("# ================= ClassPage: /class =================", "# ================= OpenTask:"),      # the whole /class page
    block("# ================= ClassRules:", "# ================= bridge functions ================="),     # the weapon lock
    block("# ================= DamageLock:", "# ================= 0.1.7 DeployGuard:"),                   # blocked hits (reads ShotRec)
    block("# ================= 0.1.7 DeployGuard:", "# ================= 0.1.6 HealBudget:"),             # the Priest-only totem
    block("# ================= 0.1.6 HealMsg:", "# ================= 0.1.6 Kit, part 1:"),                # heal chat lines
    block("# ================= 0.1.6 Kit, part 1:", "# ================= 0.1.6 KitTask:"),                # kits + the off-hand (0.1.10)
    block("# ================= 0.1.6 KitTask:", "# ================= 0.1.6 Kit, part 2:"),                 # KitTask (mode 0/1/2)
    block("# ================= 0.1.7 Arrows:", "# ================= 0.1.6 HealTask:"),                     # daily arrows
    block("# ================= 0.1.6 KitHooks", "# ================= 0.1.6 KitMigrate:"),
    block("# ================= 0.1.6 KitMigrate:", "# ================= ClassPage: /class ================="),
    block("# ================= ClassStore:", "# ================= ClassRules:"),
    block("# ================= 0.1.10 ClassCfg.migrate0110:", "# ================= ClassDefs:"),           # the one-time 0.1.10 update
]

# ================================================================================================ docstring, Run line, version
rep('''"""SkyyClasses 0.1.10 - build script (javassist via jpype). GENERATED by tools/classes_0_1_10_patch.py from the LIVE 0.1.9 (the EDITED
lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> classes_0_1_8_patch.py -> 0.1.8 -> classes_0_1_9_patch.py -> 0.1.9) -
edit the patch, not this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.11 - build script (javassist via jpype). GENERATED by tools/classes_0_1_11_patch.py from the LIVE 0.1.10 (the EDITED
lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_10_patch.py -> 0.1.10) - edit the patch, not this
file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
0.1.11 (2026-10-03, Skyy: "RAISE THE CAPS so charged shots heal clearly more than taps"; research/SkyyArmory-Spec.md 15.5): the Priest
  heal caps grow with the shot.
  - A CHARGED wand shot's per-hit cap = max(priestHeal.maxPerHit, priestHeal.hpPerMana x the wand's charged Mana from SkyyArmory's
    armory:fn:info): Wood 10, Copper 20, Iron 30, Thorium 50, Cobalt 80, Adamantite 120, Mithril / Onyxium 170 at the default 2 per Mana.
  - A QUICK shot (tap; projectile id in armory:quick) = that cap x priestHeal.quickPercent % (20 = 1/5 = the same healing per Mana).
  - Every other Priest hit (spellbooks, melee, the totem, wands SkyyArmory does not know, no SkyyArmory) keeps maxPerHit.
  - Per second each player gets at most max(priestHeal.maxPerSecond, the biggest hit cap of that 1 s window) - one charged heal's worth.
  - ShotRec.pid = ProjectileComponent.getProjectileAssetName() at launch; PriestHealSys -> HealTask(u, dealt, world, item, pid);
    HealTask.cap -> capOf (pure); HealBudget's take keeps the window's top cap. New live rows priestHeal.hpPerMana (2) and
    priestHeal.quickPercent (20 %); maxPerHit / maxPerSecond relabelled "(at least)". No migration: a missing key reads its default.
  - FIX ROUND: the big cap only for the wand's OWN shots (armory:fn:info elements 6 + 7 = its charged / quick projectile ids; a bomb or
    another orb launched with the wand in hand keeps maxPerHit), and a tap raises the 1 s window to its wand's CHARGED cap (with
    maxPerSecond 10 every Mithril tap heals - the same healing per Mana as charged shots). The Mage card text is S2-neutral.
  Heal XP calls, the heal chat lines, the /class page (except the Mage card's text), the SKYY CARD block, kits, arrows, commands and
  bridge keys are 0.1.10's.
''')
rep("Run:   python build_skyyclasses_0.1.10.py           -> SkyyClasses/SkyyClasses-0.1.10.jar",
    "Run:   python build_skyyclasses_0.1.11.py           -> SkyyClasses/SkyyClasses-0.1.11.jar")
rep('''    mark its kit pending (SkyyProfiles 0.1.2 Create Profile). Reads party:fn:members, skill:fn:healxp (0.1.6; 0.1.7 also sends the
    Priest's self-heal HP with a trailing Boolean.TRUE).''', '''    mark its kit pending (SkyyProfiles 0.1.2 Create Profile). Reads party:fn:members, skill:fn:healxp (0.1.6; 0.1.7 also sends the
    Priest's self-heal HP with a trailing Boolean.TRUE), 0.1.11: armory:fn:info + armory:quick (SkyyArmory - the wand heal caps).''')
rep('VERSION = "0.1.10"', 'VERSION = "0.1.11"')
# fix round (review: stale player text - the staff tap is SkyyArmory's quick shot now): S2-neutral, true with the quick shot and with the
# spear swing (Skyy's open question S2); SkyyProfiles 0.1.5 shows the same old line on its class cards until its next build
MAGE_DESC_OLD = "Spellcaster. Staves strike up close and cast magic at range."
MAGE_DESC_NEW = "Spellcaster. Staves cast magic at range - hold to charge a bigger blast."
rep('     "desc": "%s",' % MAGE_DESC_OLD, '     "desc": "%s",   # 0.1.11 fix round: the staff tap is a quick shot (SkyyArmory)' % MAGE_DESC_NEW)

# ================================================================================================ the cap constants + the build-time table
CAP_PY = '''HEAL_MSG_MS_MIN, HEAL_MSG_MS_MAX = 1000, 60000
# 0.1.11 (Skyy 2026-10-03: "RAISE THE CAPS so charged shots heal clearly more than taps"; research/SkyyArmory-Spec.md 15.5): a charged
# wand shot's heal cap = max(maxPerHit, HP_PER_MANA x the wand's charged Mana from SkyyArmory), a quick shot's = that x QUICK_PCT %, every
# other Priest hit = maxPerHit; per second = max(maxPerSecond, the biggest CHARGED cap of the wands whose shots reached the player in
# that 1 s window - fix round: a tap counts with its wand's charged cap, so taps heal as much per Mana as charged shots). Both rows are live.
DEF_HEAL_PER_MANA = 2.0         # priestHeal.hpPerMana (Mithril 85 Mana x 2 = 170 - about a full heal at Lv 40)
DEF_HEAL_QUICK_PCT = 20         # priestHeal.quickPercent (20 = 1/5 = the quick shot's Mana share -> the same healing per Mana)
HEAL_PER_MANA_MIN, HEAL_PER_MANA_MAX = 0.0, 50.0
HEAL_QUICK_MAX = 100
# the SkyyArmory bridge contract (research/SkyyArmory-Spec.md 8 + 15.5): armory:fn:info = Function(Object[]{"wand", itemId}) ->
# Object[]{Integer charged, Integer quick, Double mult, Integer chargedDmg, Integer quickDmg, Double tunePct} or null; armory:quick =
# String, the quick-shot projectile ids (8 wand + 8 staff), comma separated
ARMORY_INFO_KEY = "armory:fn:info"
ARMORY_QUICK_KEY = "armory:quick"


def heal_cap(mana, shot, quick, max_hit, per_mana=DEF_HEAL_PER_MANA, quick_pct=DEF_HEAL_QUICK_PCT):
    """build-time model of HealTask.capOf (the harness runs the jar's own capOf against the same table)"""
    floor = max_hit if max_hit > 0 else 0.0
    if not shot or not mana > 0:
        return floor
    c = per_mana * mana if per_mana > 0 else 0.0
    if not c > floor:
        c = floor
    return c * max(0, min(100, quick_pct)) / 100.0 if quick else c


# research/SkyyArmory-Spec.md 15.5 "Numbers": (wand, charged Mana, damage at its first level charged / quick, caps default 10 / Skyy's 50)
ARMORY_WANDS = [("Wood", 5, 25, 5), ("Copper", 10, 115, 23), ("Iron", 15, 199, 41), ("Thorium", 25, 371, 74), ("Cobalt", 40, 656, 132),
                ("Adamantite", 60, 1155, 232), ("Mithril", 85, 1764, 353), ("Onyxium", 85, 1764, 353)]
SPEC_CAPS = {10.0: [(10, 2), (20, 4), (30, 6), (50, 10), (80, 16), (120, 24), (170, 34), (170, 34)],
             50.0: [(50, 10), (50, 10), (50, 10), (50, 10), (80, 16), (120, 24), (170, 34), (170, 34)]}
SPEC_HEALS = {10.0: [(6.25, 1.25), (20, 4), (30, 6), (50, 10), (80, 16), (120, 24), (170, 34), (170, 34)],
              50.0: [(6.25, 1.25), (28.75, 5.75), (49.75, 10), (50, 10), (80, 16), (120, 24), (170, 34), (170, 34)]}
print("Priest heal caps (0.1.11, hpPerMana %s, quickPercent %d%%) - charged / quick cap -> heal of a hit at the wand's first level:"
      % (DEF_HEAL_PER_MANA, DEF_HEAL_QUICK_PCT))
for _floor in (10.0, 50.0):
    _row = []
    for _i, (_w, _mana, _dc, _dq) in enumerate(ARMORY_WANDS):
        _cc, _qc = heal_cap(_mana, True, False, _floor), heal_cap(_mana, True, True, _floor)
        _hc, _hq = min(_dc * DEF_HEAL_SHARE_PCT / 100.0, _cc), min(_dq * DEF_HEAL_SHARE_PCT / 100.0, _qc)
        assert (_cc, _qc) == SPEC_CAPS[_floor][_i] and (_hc, _hq) == SPEC_HEALS[_floor][_i], (_floor, _w, _cc, _qc, _hc, _hq)
        assert _cc >= 5 * _qc - 1e-9 and _hc > _hq, "a charged hit must heal clearly more than a tap (%s)" % _w
        _row.append("%s %g/%g -> %g/%g" % (_w, _cc, _qc, _hc, _hq))
    print("  maxPerHit %g: %s" % (_floor, ", ".join(_row)))
# hpPerMana 0 + quickPercent 100 = today's rule (cap = maxPerHit for every hit); a hit that is no shot / an unknown wand = maxPerHit
assert all(heal_cap(_m, True, _q, 10.0, 0.0, 100) == 10.0 for _m in (5, 85) for _q in (False, True))
assert heal_cap(85, False, False, 50.0) == 50.0 and heal_cap(0, True, True, 50.0) == 50.0 and heal_cap(85, True, True, 50.0, 2.0, 0) == 0.0
'''
rep("HEAL_MSG_MS_MIN, HEAL_MSG_MS_MAX = 1000, 60000\n", CAP_PY)

# ================================================================================================ engine probe: the projectile's asset id
rep('''pool.get(T["SAS"])
pool.get(T["DES"])

cfg  = pool.makeClass(PKG + ".ClassCfg")''', '''pool.get(T["SAS"])
pool.get(T["DES"])
# 0.1.11: the launched projectile's asset id (ShotTrack -> ShotRec.pid -> the heal cap's quick / charged shot)
B.probe(pool, T["LPC"], "getProjectileAssetName")
assert str(pool.get(T["LPC"]).getMethod("getProjectileAssetName", "()Ljava/lang/String;").getName()) == "getProjectileAssetName"

cfg  = pool.makeClass(PKG + ".ClassCfg")''')

# ================================================================================================ the default file: the rule + the two keys
rep('''    "# a Priest's wand or spellbook hit on a monster heals party members within priestHeal.radius blocks of the Priest by sharePercent of",
    "# the damage (the Priest themself selfPercent of that), at most maxPerHit per hit and maxPerSecond per second for each player",
    "priestHeal.enabled=%s" % str(DEF_HEAL_ON).lower(),
    "priestHeal.sharePercent=%d" % DEF_HEAL_SHARE_PCT,
    "priestHeal.selfPercent=%d" % DEF_HEAL_SELF_PCT,
    "priestHeal.radius=%s" % dnum(DEF_HEAL_RADIUS),
    "priestHeal.maxPerHit=%s" % dnum(DEF_HEAL_MAX_HIT),''', '''    "# a Priest's wand or spellbook hit on a monster heals party members within priestHeal.radius blocks of the Priest by sharePercent of",
    "# the damage (the Priest themself selfPercent of that), capped per hit and per second for each player:",
    "# 0.1.11 (Skyy 2026-10-03, charged shots heal clearly more than taps): a charged wand shot heals at most hpPerMana times the wand's",
    "# charged Mana (from SkyyArmory - Mithril 85 Mana x 2 is 170), never less than maxPerHit; a quick shot (a tap) at most quickPercent",
    "# percent of that (20 is 1/5, the same healing per Mana). Every other Priest hit (spellbooks, melee, wands SkyyArmory does not know)",
    "# at most maxPerHit. Per second each player gets at most maxPerSecond, or one charged heal of the wands that hit when that is more.",
    "priestHeal.enabled=%s" % str(DEF_HEAL_ON).lower(),
    "priestHeal.sharePercent=%d" % DEF_HEAL_SHARE_PCT,
    "priestHeal.selfPercent=%d" % DEF_HEAL_SELF_PCT,
    "priestHeal.radius=%s" % dnum(DEF_HEAL_RADIUS),
    "priestHeal.hpPerMana=%s" % dnum(DEF_HEAL_PER_MANA),      # 0.1.11
    "priestHeal.quickPercent=%d" % DEF_HEAL_QUICK_PCT,        # 0.1.11
    "priestHeal.maxPerHit=%s" % dnum(DEF_HEAL_MAX_HIT),''')

# ================================================================================================ ClassCfg: fields, extraText, load()
rep('''F(cfg, "public static volatile double HEAL_MAX_SEC = %s;" % jdbl(DEF_HEAL_MAX_SEC))
''', '''F(cfg, "public static volatile double HEAL_MAX_SEC = %s;" % jdbl(DEF_HEAL_MAX_SEC))
F(cfg, "public static volatile double HEAL_PER_MANA = %s;" % jdbl(DEF_HEAL_PER_MANA))    # 0.1.11: priestHeal.hpPerMana
F(cfg, "public static volatile long HEAL_QUICK_PCT = %dL;" % DEF_HEAL_QUICK_PCT)          # 0.1.11: priestHeal.quickPercent
''')
rep('''  return " kits=" + (@PKG@.KitCfg.ON ? "on" : "off") + " priestHeal=" + (HEAL_ON ? "on" : "off") + " healShare=" + HEAL_SHARE_PCT
    + "% self=" + HEAL_SELF_PCT + "% radius=" + fmtNum(HEAL_RADIUS)
    + " arrows=" ''', '''  return " kits=" + (@PKG@.KitCfg.ON ? "on" : "off") + " priestHeal=" + (HEAL_ON ? "on" : "off") + " healShare=" + HEAL_SHARE_PCT
    + "% self=" + HEAL_SELF_PCT + "% radius=" + fmtNum(HEAL_RADIUS)
    + " healCaps: hit>=" + fmtNum(HEAL_MAX_HIT) + " second>=" + fmtNum(HEAL_MAX_SEC) + " perMana=" + fmtNum(HEAL_PER_MANA) + " tap=" + HEAL_QUICK_PCT + "%"
    + " arrows=" ''')
rep('''    "__HH__": jdbl(DEF_HEAL_MAX_HIT), "__HS__": jdbl(DEF_HEAL_MAX_SEC), "__CAPMIN__": jdbl(HEAL_CAP_MIN), "__CAPMAX__": jdbl(HEAL_CAP_MAX),
''', '''    "__HH__": jdbl(DEF_HEAL_MAX_HIT), "__HS__": jdbl(DEF_HEAL_MAX_SEC), "__CAPMIN__": jdbl(HEAL_CAP_MIN), "__CAPMAX__": jdbl(HEAL_CAP_MAX),
    # 0.1.11 heal caps per wand Mana / for taps
    "__HPM__": jdbl(DEF_HEAL_PER_MANA), "__HPMMIN__": jdbl(HEAL_PER_MANA_MIN), "__HPMMAX__": jdbl(HEAL_PER_MANA_MAX),
    "__HQP__": "%dL" % DEF_HEAL_QUICK_PCT, "__HQPMAX__": "%dL" % HEAL_QUICK_MAX,
''')
rep('''    HEAL_MAX_SEC = hs;
    HEAL_MSG = bool(p, "priestHeal.messages", __HM__);''', '''    HEAL_MAX_SEC = hs;
    double hpm = dbl(p, "priestHeal.hpPerMana", __HPM__);
    if (hpm < __HPMMIN__) hpm = __HPMMIN__;
    if (hpm > __HPMMAX__) hpm = __HPMMAX__;
    HEAL_PER_MANA = hpm;
    long hqp = lng(p, "priestHeal.quickPercent", __HQP__);
    if (hqp < 0L) hqp = 0L;
    if (hqp > __HQPMAX__) hqp = __HQPMAX__;
    HEAL_QUICK_PCT = hqp;
    HEAL_MSG = bool(p, "priestHeal.messages", __HM__);''')

# ================================================================================================ the rows (kit limits: label 40, help 100)
ROW_PM = ("priestHeal.hpPerMana", "Charged heal cap per wand Mana",
          "Charged wand hit cap = this x its charged Mana (Mithril 85 x 2 = 170), at least Most HP per hit.")
ROW_QP = ("priestHeal.quickPercent", "Tap heal cap (% of charged)",
          "A quick shot's heal cap as % of the charged one. 20 = 1/5 = the same healing per Mana.")
ROW_HIT = ("priestHeal.maxPerHit", "Most HP per hit (at least)",
           "Cap for spellbook, melee and other Priest hits; also the least a charged wand hit's cap can be.")
ROW_SEC = ("priestHeal.maxPerSecond", "Most HP per second (at least)",
           "All Priest heals one player gets in 1 s, added up - at least one charged heal of the wands that hit.")
for _k, _lab, _help in (ROW_PM, ROW_QP, ROW_HIT, ROW_SEC):
    assert len(_lab) <= 40 and len(_help) <= 100 and not set('"\\') & set(_lab + _help), (_k, len(_lab), len(_help))
rep('''    ("priestHeal.maxPerHit", "Most HP per hit (each player)", "priest", "dec", dnum(DEF_HEAL_MAX_HIT), dnum(HEAL_CAP_MIN), dnum(HEAL_CAP_MAX),
     "", "", "live", "Cap for one hit and one player, before the per-second cap.",
     "field:ClassCfg.HEAL_MAX_HIT@config.properties:priestHeal.maxPerHit"),
    ("priestHeal.maxPerSecond", "Most HP per second (each player)", "priest", "dec", dnum(DEF_HEAL_MAX_SEC), dnum(HEAL_CAP_MIN),
     dnum(HEAL_CAP_MAX), "", "", "live", "All Priest heals one player gets in one second, added up.",
     "field:ClassCfg.HEAL_MAX_SEC@config.properties:priestHeal.maxPerSecond"),''', '''    # 0.1.11 (Skyy 2026-10-03: charged shots heal clearly more than taps; research/SkyyArmory-Spec.md 15.5): two new live rows, the two
    # caps relabelled - they are now the floor of a wand hit's cap and of the per-second budget (keys kept: no migration, Skyy's 50 / 1000 stay)
    ("%s", "%s", "priest", "dec", dnum(DEF_HEAL_PER_MANA), dnum(HEAL_PER_MANA_MIN), dnum(HEAL_PER_MANA_MAX), "", "", "live",
     "%s",
     "field:ClassCfg.HEAL_PER_MANA@config.properties:priestHeal.hpPerMana"),
    ("%s", "%s", "priest", "int", str(DEF_HEAL_QUICK_PCT), "0", str(HEAL_QUICK_MAX), "", "%%", "live",
     "%s",
     "field:ClassCfg.HEAL_QUICK_PCT@config.properties:priestHeal.quickPercent"),
    ("%s", "%s", "priest", "dec", dnum(DEF_HEAL_MAX_HIT), dnum(HEAL_CAP_MIN), dnum(HEAL_CAP_MAX),
     "", "", "live", "%s",
     "field:ClassCfg.HEAL_MAX_HIT@config.properties:priestHeal.maxPerHit"),
    ("%s", "%s", "priest", "dec", dnum(DEF_HEAL_MAX_SEC), dnum(HEAL_CAP_MIN),
     dnum(HEAL_CAP_MAX), "", "", "live", "%s",
     "field:ClassCfg.HEAL_MAX_SEC@config.properties:priestHeal.maxPerSecond"),''' % (ROW_PM + ROW_QP + ROW_HIT + ROW_SEC))
rep('''assert len(CFG_ROWS) == 5 + 2 + 1 + 2 * len(CLASSES) + 8 + 4, "row count"   # 0.1.7: + 2 greyed-out switch rows, + 4 arrow rows''',
    '''assert len(CFG_ROWS) == 5 + 2 + 1 + 2 * len(CLASSES) + 10 + 4, "row count"   # 0.1.7: + 2 greyed-out switch rows, + 4 arrow rows; 0.1.11: + 2 heal rows
_PR = [_r[0] for _r in CFG_ROWS if _r[2] == "priest"]
assert _PR == ["priestHeal.enabled", "priestHeal.sharePercent", "priestHeal.selfPercent", "priestHeal.radius", "priestHeal.hpPerMana",
               "priestHeal.quickPercent", "priestHeal.maxPerHit", "priestHeal.maxPerSecond", "priestHeal.messages", "priestHeal.feedbackMs"], _PR''')

# ================================================================================================ ShotRec.pid + ShotTrack reads it at launch
rep('''F(srec, "public String item;")   # 0.1.6: the main-hand item id at launch (null = empty hand), for every tracked shot
F(srec, "public long at;")
C(srec, r"""
public ShotRec(java.util.UUID shooter, String bad, boolean util, String item) {
  this.shooter = shooter;
  this.bad = bad;
  this.util = util;
  this.item = item;
  this.at = System.currentTimeMillis();
}""")''', '''F(srec, "public String item;")   # 0.1.6: the main-hand item id at launch (null = empty hand), for every tracked shot
F(srec, "public String pid;")    # 0.1.11: the projectile asset id at launch (legacy ProjectileComponent; null = physics-only) - the heal cap
F(srec, "public long at;")
C(srec, r"""
public ShotRec(java.util.UUID shooter, String bad, boolean util, String item, String pid) {
  this.shooter = shooter;
  this.bad = bad;
  this.util = util;
  this.item = item;
  this.pid = pid;
  this.at = System.currentTimeMillis();
}""")''')
rep('''    java.util.UUID creator = null;
    @SPP@ sp = (@SPP@) buf.getComponent(ref, @SPP@.getComponentType());
    if (sp != null) creator = sp.getCreatorUuid();
    if (creator == null) {
      @LPC@ lp = (@LPC@) buf.getComponent(ref, @LPC@.getComponentType());
      if (lp != null) creator = lp.getCreatorUuid();
    }
    if (creator == null) return;''', '''    java.util.UUID creator = null;
    @SPP@ sp = (@SPP@) buf.getComponent(ref, @SPP@.getComponentType());
    if (sp != null) creator = sp.getCreatorUuid();
    @LPC@ lp = (@LPC@) buf.getComponent(ref, @LPC@.getComponentType());   // 0.1.11: always read - its asset id tells the heal cap the shot
    if (creator == null && lp != null) creator = lp.getCreatorUuid();
    if (creator == null) return;''')
rep('''    if (SHOTS.size() > %d) purge();
    SHOTS.put(idc.getUuid(), new @PKG@.ShotRec(u, bad, util, item));''', '''    String pid = null;
    if (lp != null) { try { pid = lp.getProjectileAssetName(); } catch (Throwable tp) { pid = null; } }   // 0.1.11 (never costs the lock record)
    if (SHOTS.size() > %d) purge();
    SHOTS.put(idc.getUuid(), new @PKG@.ShotRec(u, bad, util, item, pid));''')

# ================================================================================================ HealBudget: the window keeps its top hit cap
rep('''# ================= 0.1.6 HealBudget: per target, a fixed 1 s window shared by ALL Priests (priestHeal.maxPerSecond) =================
F(hbud, "public static final java.util.concurrent.ConcurrentHashMap USED = new java.util.concurrent.ConcurrentHashMap();")  # UUID -> double[]{start, used}
M(hbud, r"""
public static synchronized double take(java.util.UUID u, double want, long now, double perSec) {
  if (u == null || !(want > 0.0) || !(perSec > 0.0)) return 0.0;
  double[] b = (double[]) USED.get(u);
  if (b == null || (double) now - b[0] >= 1000.0 || (double) now < b[0]) { b = new double[] { (double) now, 0.0 }; USED.put(u, b); }
  double left = perSec - b[1];
  if (!(left > 0.0)) return 0.0;
  double got = want < left ? want : left;
  b[1] = b[1] + got;
  return got;
}""")''', '''# ================= 0.1.6 HealBudget: per target, a fixed 1 s window shared by ALL Priests (priestHeal.maxPerSecond) =================
# 0.1.11 (research/SkyyArmory-Spec.md 15.5): the window also keeps its TOP = the biggest window cap passed in it (fix round: a wand shot -
# tap or charged - passes its WAND'S charged cap, anything else maxPerHit); the window allows max(perSec, top) - at most one full charged
# heal per second from all Priests together (Skyy's live 1000 still wins)
F(hbud, "public static final java.util.concurrent.ConcurrentHashMap USED = new java.util.concurrent.ConcurrentHashMap();")  # UUID -> double[]{start, used, top}
M(hbud, r"""
public static synchronized double take(java.util.UUID u, double want, long now, double perSec, double hitCap) {
  if (u == null || !(want > 0.0)) return 0.0;
  double[] b = (double[]) USED.get(u);
  if (b == null || b.length < 3 || (double) now - b[0] >= 1000.0 || (double) now < b[0]) { b = new double[] { (double) now, 0.0, 0.0 }; USED.put(u, b); }
  if (hitCap > b[2]) b[2] = hitCap;
  double lim = perSec > b[2] ? perSec : b[2];
  double left = lim - b[1];
  if (!(left > 0.0)) return 0.0;
  double got = want < left ? want : left;
  b[1] = b[1] + got;
  return got;
}""")''')

# ================================================================================================ HealTask: the cap of the hit
rep('''F(htask, "public static volatile boolean FAILED_ONCE = false;")
C(htask, "public HealTask(java.util.UUID u, float dealt, String world) { this.u = u; this.dealt = dealt; this.world = world; }")''',
    '''F(htask, "public String item;")   # 0.1.11: the Priest weapon (the item at launch for a shot, the main hand for melee)
F(htask, "public String pid;")    # 0.1.11: the projectile asset id at launch (null = melee or a physics-only projectile)
F(htask, "public static volatile boolean FAILED_ONCE = false;")
F(htask, "public static final String ARMORY_INFO = %s;" % jstr(ARMORY_INFO_KEY))     # 0.1.11: SkyyArmory's wand table
F(htask, "public static final String ARMORY_QUICK = %s;" % jstr(ARMORY_QUICK_KEY))   # 0.1.11: SkyyArmory's quick-shot projectile ids
F(htask, "public static volatile Object[] QC = null;")   # 0.1.11: { the armory:quick value last parsed, its java.util.HashSet (lower case) }
C(htask, "public HealTask(java.util.UUID u, float dealt, String world, String item, String pid) { this.u = u; this.dealt = dealt; this.world = world; this.item = item; this.pid = pid; }")''')
rep('''M(htask, r"""
public static void failOnce(Throwable t) {''', '''# 0.1.11: the ids of a bridge value, lower case: a String split on commas, semicolons, | and white space (or an Object[] / Collection of
# such Strings). Pure, never throws for a String.
M(htask, r"""
public static void addIds(java.util.HashSet s, String t) {
  if (s == null || t == null) return;
  StringBuilder cur = new StringBuilder();
  int n = t.length();
  for (int i = 0; i <= n; i++) {
    char c = i < n ? t.charAt(i) : ',';
    if (c == ',' || c == ';' || c == '|' || c <= ' ') {
      if (cur.length() > 0) { s.add(cur.toString().toLowerCase(java.util.Locale.ROOT)); cur.setLength(0); }
    } else {
      cur.append(c);
    }
  }
}""")
M(htask, r"""
public static java.util.HashSet parseIds(Object raw) {
  java.util.HashSet s = new java.util.HashSet();
  if (raw == null) return s;
  if (raw instanceof Object[]) {
    Object[] a = (Object[]) raw;
    for (int i = 0; i < a.length; i++) if (a[i] != null) addIds(s, String.valueOf(a[i]));
  } else if (raw instanceof java.util.Collection) {
    java.util.Iterator it = ((java.util.Collection) raw).iterator();
    while (it.hasNext()) { Object o = it.next(); if (o != null) addIds(s, String.valueOf(o)); }
  } else {
    addIds(s, String.valueOf(raw));
  }
  return s;
}""")
# 0.1.11: SkyyArmory's quick-shot projectile ids (bridge armory:quick), parsed again only when the bridge value is another object (SkyyArmory
# publishes it once at start; a missing key = no quick shots, cached as such until the key appears). Any thread: one volatile holder whose
# set is never changed after it is published; a value that cannot be read (a Collection changed while read) is not cached.
M(htask, r"""
public static java.util.HashSet quickIds() {
  Object raw = null;
  try { raw = @PKG@.ClassCfg.bridge().get(ARMORY_QUICK); } catch (Throwable t) { raw = null; }
  Object[] c = QC;
  if (c != null && c[0] == raw) return (java.util.HashSet) c[1];
  try {
    java.util.HashSet s = parseIds(raw);
    QC = new Object[] { raw, s };
    return s;
  } catch (Throwable t2) { return new java.util.HashSet(); }
}""")
M(htask, r"""
public static boolean isQuick(String pid) {
  if (pid == null || pid.length() == 0) return false;
  return quickIds().contains(pid.toLowerCase(java.util.Locale.ROOT));
}""")
# 0.1.11: SkyyArmory's answer for a wand (armory:fn:info, Object[]{"wand", itemId} -> Object[]{Integer charged, Integer quick, Double mult,
# Integer chargedDmg, Integer quickDmg, Double tunePct, String chargedProjectileId, String quickProjectileId} or null - the two ids are the
# fix round's; an older SkyyArmory answers 6 elements). null = no SkyyArmory, an id it does not know (spellbooks, the totem), a bad answer.
# Never throws.
M(htask, r"""
public static Object[] wandInfo(String item) {
  if (item == null || item.length() == 0) return null;
  try {
    Object f = @PKG@.ClassCfg.bridge().get(ARMORY_INFO);
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(new Object[] { "wand", item });
    if (!(r instanceof Object[])) return null;
    return (Object[]) r;
  } catch (Throwable t) { return null; }
}""")
# the charged-shot Mana of an answer (element 0); 0 = unknown / not a positive finite number
M(htask, r"""
public static double manaOf(Object[] a) {
  if (a == null || a.length < 1 || !(a[0] instanceof Number)) return 0.0;
  double c = ((Number) a[0]).doubleValue();
  if (!(c > 0.0) || Double.isInfinite(c)) return 0.0;
  return c;
}""")
M(htask, r"""
public static double wandMana(String item) {
  return manaOf(wandInfo(item));
}""")
# 0.1.11 (pure, bare-JVM tested; research/SkyyArmory-Spec.md 15.5): the per-hit cap. A SHOT (a projectile with an asset id) from a wand
# SkyyArmory knows (mana > 0): charged = max(maxHit, perMana x mana), quick = that x quickPct %. Anything else - melee, spellbooks, the
# totem, an unknown wand, no SkyyArmory - keeps maxHit (today's rule). perMana 0 + quickPct 100 = today's rule for every hit.
M(htask, r"""
public static double capOf(double mana, boolean shot, boolean quick, double maxHit, double perMana, long quickPct) {
  double floor = maxHit > 0.0 ? maxHit : 0.0;
  if (!shot || !(mana > 0.0)) return floor;
  double c = perMana > 0.0 ? perMana * mana : 0.0;
  if (!(c > floor)) c = floor;
  if (quick) {
    long q = quickPct < 0L ? 0L : (quickPct > 100L ? 100L : quickPct);
    c = c * (double) q / 100.0;
  }
  return c;
}""")
# 0.1.11 FIX ROUND: which shot of the wand this projectile is - 2 = its quick shot, 1 = its charged shot, 0 = not a shot of THIS wand (a
# bomb, a Fireball, another wand's orb launched with it in hand: the floor). SkyyArmory's answer carries the wand's own ids (elements 6 + 7,
# case-insensitive); an older 6-element answer = the first 0.1.11 rule (quick when armory:quick lists the id, else charged). Pure.
M(htask, r"""
public static int shotKind(Object[] a, String pid) {
  if (a == null || pid == null || pid.length() == 0) return 0;
  if (a.length >= 8 && a[6] instanceof String && a[7] instanceof String) {
    String q = (String) a[7];
    String c = (String) a[6];
    if (q.length() > 0 && q.equalsIgnoreCase(pid)) return 2;
    if (c.length() > 0 && c.equalsIgnoreCase(pid)) return 1;
    return 0;
  }
  return isQuick(pid) ? 2 : 1;
}""")
# 0.1.11 (FIX ROUND): this hit's caps with the live config (Server Setup -> Classes -> Priest heal): { the hit's heal cap, the per-second
# window's top for it }. A shot of the wand in hand: the heal cap = charged / tap cap (capOf), the window top = that wand's CHARGED cap for
# both shots (a tap must not shrink the window to its own cap: with maxPerSecond 10 only every third Mithril tap healed). Anything else
# (melee, spellbooks, the totem, unknown wands, no SkyyArmory, another projectile): { maxPerHit, maxPerHit } = today's rule.
M(htask, r"""
public static double[] caps(String item, String pid) {
  boolean shot = pid != null && pid.length() > 0;
  Object[] a = null;
  if (shot) a = wandInfo(item);
  double mana = manaOf(a);
  int kind = mana > 0.0 ? shotKind(a, pid) : 0;
  double floor = capOf(0.0, false, false, @PKG@.ClassCfg.HEAL_MAX_HIT, @PKG@.ClassCfg.HEAL_PER_MANA, @PKG@.ClassCfg.HEAL_QUICK_PCT);
  if (kind == 0) return new double[] { floor, floor };
  double charged = capOf(mana, true, false, @PKG@.ClassCfg.HEAL_MAX_HIT, @PKG@.ClassCfg.HEAL_PER_MANA, @PKG@.ClassCfg.HEAL_QUICK_PCT);
  double hit = kind == 2 ? capOf(mana, true, true, @PKG@.ClassCfg.HEAL_MAX_HIT, @PKG@.ClassCfg.HEAL_PER_MANA, @PKG@.ClassCfg.HEAL_QUICK_PCT) : charged;
  return new double[] { hit, charged };
}""")
M(htask, r"""
public static double cap(String item, String pid) {
  return caps(item, pid)[0];
}""")
M(htask, r"""
public static void failOnce(Throwable t) {''')
rep('''# heal one player: overheal is clamped first, then the per-second budget of that player is taken, then Health goes up
M(htask, r"""
public static double heal(@ST@ st, @REF@ r, java.util.UUID tu, double want, long now) {''', '''# heal one player: overheal is clamped first, then the per-second budget of that player is taken (0.1.11: with this hit's cap), then Health
# goes up
M(htask, r"""
public static double heal(@ST@ st, @REF@ r, java.util.UUID tu, double want, long now, double hitCap) {''')
rep('''  double got = @PKG@.HealBudget.take(tu, ask, now, @PKG@.ClassCfg.HEAL_MAX_SEC);''',
    '''  double got = @PKG@.HealBudget.take(tu, ask, now, @PKG@.ClassCfg.HEAL_MAX_SEC, hitCap);''')
rep('''public double one(@ST@ st, @VEC@ c, String mid, double want, double r2, long now, String healer) {''',
    '''public double one(@ST@ st, @VEC@ c, String mid, double want, double r2, long now, String healer, double hitCap) {''')
rep('''  double got = heal(st, mr, mu, want, now);
  if (got > 0.0) {
    @PKG@.HealMsg.given(this.u, mu, got);''', '''  double got = heal(st, mr, mu, want, now, hitCap);
  if (got > 0.0) {
    @PKG@.HealMsg.given(this.u, mu, got);''')
rep('''    double want = want((double) this.dealt, @PKG@.ClassCfg.HEAL_SHARE_PCT, @PKG@.ClassCfg.HEAL_MAX_HIT);''',
    '''    double[] cc = caps(this.item, this.pid);   // 0.1.11: charged wand shot / quick shot / any other Priest hit
    double cap = cc[0];
    double top = cc[1];                        // fix round: a tap raises the 1 s window to its wand's CHARGED cap, the heal keeps the tap cap
    double want = want((double) this.dealt, @PKG@.ClassCfg.HEAL_SHARE_PCT, cap);''')
rep('''      try { others = others + one(st, c, ms[i], want, r2, now, healer); } catch (Throwable t1) { failOnce(t1); }
    }
    double self = heal(st, ref, this.u, selfWant(want, @PKG@.ClassCfg.HEAL_SELF_PCT), now);''', '''      try { others = others + one(st, c, ms[i], want, r2, now, healer, top); } catch (Throwable t1) { failOnce(t1); }
    }
    double self = heal(st, ref, this.u, selfWant(want, @PKG@.ClassCfg.HEAL_SELF_PCT), now, top);''')

# ================================================================================================ PriestHealSys: hand (item, pid) to the task
rep('''    java.util.UUID u = null;
    String item = null;
    if (rec != null) {
      u = rec.shooter;
      item = rec.item;
    } else {''', '''    java.util.UUID u = null;
    String item = null;
    String pid = null;   // 0.1.11: the projectile asset id of a shot (the heal cap: charged / quick / other)
    if (rec != null) {
      u = rec.shooter;
      item = rec.item;
      pid = rec.pid;
    } else {''')
rep('''    w.execute(new @PKG@.HealTask(u, dealt, w.getName()));''', '''    w.execute(new @PKG@.HealTask(u, dealt, w.getName(), item, pid));''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
assert [ln for ln in s.split(LF) if "registerSystem(" in ln] == SYS0, "system registrations changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.1.10's changed: %s" % k[:80]
_card2 = block(CARD_START, CARD_END) + CARD_END
assert _card2 == _card and hashlib.sha256(_card2.encode("utf8")).hexdigest() == CARD_SHA, "the SKYY CARD block must stay SkyyProfiles 0.1.4's"
assert s.count("HealBudget.take(") == 1 and s.count("new @PKG@.HealTask(") == 1 and s.count("new @PKG@.ShotRec(") == 1
assert s.count("heal(st, mr, mu, want, now, hitCap)") == 1 and s.count("heal(st, ref, this.u, selfWant(") == 1
# javassist: methods before callers
_ht = block("# ================= 0.1.6 HealTask:", "# ================= 0.1.6 PriestHealSys:")
for _a, _b in (("public static void addIds(", "public static java.util.HashSet parseIds("),
               ("public static java.util.HashSet parseIds(", "public static java.util.HashSet quickIds("),
               ("public static java.util.HashSet quickIds(", "public static boolean isQuick("),
               ("public static boolean isQuick(", "public static double cap("), ("public static double wandMana(", "public static double cap("),
               ("public static double capOf(", "public static double cap("), ("public static double cap(", "public void run()"),
               # fix round: the wand's own shots + the window top
               ("public static Object[] wandInfo(", "public static double manaOf("), ("public static double manaOf(", "public static double wandMana("),
               ("public static boolean isQuick(", "public static int shotKind("), ("public static int shotKind(", "public static double[] caps("),
               ("public static double capOf(", "public static double[] caps("), ("public static Object[] wandInfo(", "public static double[] caps("),
               ("public static double[] caps(", "public static double cap("), ("public static double[] caps(", "public void run()"),
               ("public static double heal(", "public double one("), ("public double one(", "public void run()")):
    assert _ht.index(_a) < _ht.index(_b), (_a, _b)
assert s.index("public static synchronized double take(") < s.index("public static double heal("), "HealBudget.take before HealTask.heal"
assert s.index("public ShotRec(") < s.index("public void onEntityAdded(@REF@ ref, @ADDR@ reason"), "ShotRec before ShotTrack"
assert s.index("public HealTask(") < s.index("w.execute(new @PKG@.HealTask("), "HealTask before PriestHealSys"
assert 'VERSION = "0.1.11"' in s and "priestHeal.hpPerMana" in s and "priestHeal.quickPercent" in s
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.10 had %d)" % (s.count(LF), OLD.count(LF)))
