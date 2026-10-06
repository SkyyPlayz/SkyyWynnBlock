"""Derive SkyyGear/build_skyygear_0.2.5.py from the LIVE 0.2.4 (build_skyygear_0.2.4.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_4_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_5_patch.py      then      python SkyyGear/build_skyygear_0.2.5.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.5.py (section AF executes every new path; it also re-runs the 0.2.3 harness on the new jar).

0.2.5 = THE MOB CURVE ROUND, SkyyGear part (research/Mob-Curve-Spec.md sections 2.2-2.6, 6.2, 6.4, 7.2-7.4; every default accepted by Skyy
2026-10-05, docs/answered/mobs.md; Reforge LEVEL UP cap +6 LOCKED 2026-10-04 and armor-box hide LOCKED 2026-10-05, docs/answered/gear.md).
The spec was written for "SkyyGear 0.2.4"; 0.2.4 shipped the traversal tooltip words first (kept here), so everything it names 0.2.4 is
this 0.2.5. DEPLOY + ROLL BACK TOGETHER with SkyyMobs 0.1.4 and SkyySkills 0.4.17 (spec 7.1 pairing; this build STOPS when
tools/deploy_set.py pins SkyyGear 0.2.5 without SkyyMobs 0.1.4+ and SkyySkills 0.4.17+).
  (1) THREE CURVES (spec 2.2). base.curve (label "Weapon curve F(L)") gets the steep default
      1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.1,30:4.5,35:6.5,40:9.6,45:13.6,50:17.5,60:22.5,70:36.0,80:57.0,90:90.0 and drives every NON-spell
      weapon hit (K x F(level) x material bonus, as 0.2.1). NEW base.spellCurve ("Spell curve S(L)", default = the old F
      1:1.0,4:1.6,10:2.0,40:3.0,100:5.0) drives wand / staff / spellbook SHOTS (K = 1: GearHit.weaponHit spell hits, the 0.2.2 "Charged
      shot / Quick shot" lines, "Spell at Lv"). NEW base.hpCurve ("Armor Health curve H(L)", default
      1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.7,30:5.4,35:7.3,40:9.6,45:12.8,50:16.3,60:21.0,70:30.0,80:43.0,90:62.0,100:88.0) drives
      worn armor Health. F and H equal the old F up to Lv 20: nothing changes at item level 1-20. SPEC DEVIATION (text only): the Lv 20 point
      is 2.3333333333333335 (7/3 to double precision), not the spec's 2.333333 - that is 3e-7 low and flips EXACT .5 tooltip roundings (a Lv 13
      Wood staff swing 5 x 2.1 = 10.5 read 10 instead of 0.2.4's 11; the harness found it). K stays
      on F (GearBase.kOf), so the own-base families starting at 30 / 35 (Spellbook_Fire / _Frost, Demon, Rekindle) get a new K and keep
      exactly vanilla at their band start. Every factor <= 90 (curvePts refuses > 100, so older jars still read the defaults).
  (2) gear:fn:curve (spec 7.3) - Function: Object[] { String which ("F" | "S" | "H" | "R", any case), Number level } -> Double (the live
      curve value at that level) or null (unknown name / bad input). Any thread, never throws. SkyyMobs 0.1.4's 15 s WARN reads F(20) / F(40).
  (3) LIFE STEAL CAP (spec 2.5): row steal.maxPerSec ("Life Steal at most", % of max Health per second, default 5, 0 = no cap): each Life
      Steal payout (once per steal.windowS) is at most maxPerSec % x max Health x windowS (15 % per 3 s); the rest is dropped (not carried).
  (4) REFORGE LEVEL UP (Skyy LOCKED 2026-10-04: "in reforge you can spend coins to level it ... with a cap of like 6", cap +6; replaces the
      spec's reforge.raiseLevel - question 5 was answered by this lock): a "Level up" button on the Reforge page raises the item ONE level per
      click for coins = cost.levelUp.<rarity> base + per level x the NEW level; never more than reforge.levelCap (6) levels over the level it
      was made / found at (stored once as "lvl0" in the document at its first level up = its level then), never above its material band's cap
      (the metal's top level) and never above the player's own level in the item's gate skill (the crafted-at-your-level skill, gate floor
      applied). Coins first, refund on any failure (the reforge write safety: same slot, same fingerprint, one item off a stack). The
      modifiers are NOT re-rolled (a reforge re-rolls them at the item's level as before); rarity never changes; an admin /gear level item
      (lvlA) and unidentified items cannot be levelled. Rows (Costs): reforge.levelUp (switch), reforge.levelCap (int 0-50), cost.levelUp
      (table by rarity, Base | Per level - PLACEHOLDERS: Normal 100 + 20, Unique 200 + 40, Rare 400 + 80, Legendary 1000 + 200, Fabled
      2000 + 400, Mythic 4000 + 800, Set 1000 + 200). gear.log LEVELUP lines; no Smithing XP for a level up.
  (5) THE VANILLA ARMOR BOX IS HIDDEN (Skyy LOCKED 2026-10-05 "Yes, hide it"): at start (and after every asset reload, the 0.2.2 listener)
      every gear ARMOR type (an Armor_ id SkyyGear treats as gear of an enforced kind, in the Head / Chest / Legs / Hands slot, additive stat
      modifiers only, its ItemArmor not shared with another item) gets EMPTY stat-modifier and damage-resistance maps (the engine's own fields
      swapped by reflection - one reference write each, so a world thread reading the old map is never disturbed) and its packet cache is
      dropped: the client draws no Health / resistance box, the engine applies nothing for those pieces, and SkyyGear applies ALL of it
      (GearABox keeps the original maps): Health (levelled target H, or the asset's own when part.base / base.armorOn is off) and every other
      stat (Mana, Stamina, Oxygen ...) through the existing lock modifier skyygear_lock_<stat> (signed: it now ADDS the whole amount),
      Physical / Projectile resistance (levelled target R, the asset's own % when levelling is off) + every other resistance entry (Fire,
      Poison, Fall, FLAT parts, BaseDamageResistance per entry like the engine) in GearArmorSys's corrected armor pass. Unidentified /
      under-level pieces give nothing (level.armorNative on) or their own vanilla stats (off) - as before. The tooltip always shows the
      levelled lines + the other lines from the kept maps. Needs the ORDERED GearHitSys + GearArmorSys (else no type is hidden - one WARN).
      Row view.hideArmorBox (General, restart, default on). Rolling back to 0.2.4: the box comes back at its next start (nothing per stack).
      KNOWN LIMIT: an NPC wearing gear armor (only vanilla test roles do) gets no armor stats; armor DamageClassEnhancement / knockback /
      movement lines stay in the asset (the engine keeps applying them; whether the client lists them is UNVERIFIED).
  (6) ONE-TIME UPDATE GearCfg.migrate025 (setup(), right after migrate023, before load(); PROJECT-RULES section 4): marker
      "SkyyGear 0.2.5 level curves"; History copy "before the 0.2.5 level curves" verified first (lvSaved), atomic write (ISO-8859-1 bytes,
      every other byte + the line endings kept), run once. base.curve still holding EXACTLY 1:1.0,4:1.6,10:2.0,40:3.0,100:5.0 (one physical
      line) -> the new F (value only; key, separator, CR kept) + ONE config-changes.log line "base.curve old -> new" (who "SkyyGear 0.2.5",
      via update: Server Setup -> Changes -> Undo puts the old F back). Right after base.curve the block: marker + base.spellCurve +
      base.hpCurve + view.hideArmorBox (help comment + key=value each, only the keys the file lacks): spell = the old F and hp = the new H when
      base.curve was the old or the new default (or missing); a HAND-SET base.curve is kept and copied into BOTH (flat gear stays flat; noted).
      steal.maxPerSec right after steal.windowS; reforge.levelUp + reforge.levelCap + the cost.levelUp table right after the last
      cost.reforge.* line (no anchor -> appended to the block). New keys start at their defaults (no change-log line). Skyy's live file
      (base.curve at the default, LF) -> new F + 1 log line, spells unchanged, the new armor Health curve.
  (7) Server Setup: base.curve relabelled "Weapon curve F(L)"; 7 new rows (base.spellCurve, base.hpCurve, steal.maxPerSec,
      reforge.levelUp, reforge.levelCap, cost.levelUp, view.hideArmorBox); every curve / cap / coin row live + danger.
UNVERIFIED (needs the game): the client drawing NO armor box from empty statModifiers / damageResistance (inferred from the packet code:
ItemArmor.toPacket sends an empty stat map and a null resistance map); the engine never re-reading the original maps after the swap (only
StatModifiersManager.addArmorStatModifiers and ArmorDamageReduction.getResistanceModifiers read them - VERIFIED bytecode); SkyyMenu
editing a ~110-character curve text in its 270 px field; the level-up feel on the coin economy; the level-up coin defaults (placeholders).
CHECKED 2026-10-06 (scratch tools/dev/scratch/mc-gear, deleted afterwards): build "assembled ...SkyyGear-0.2.5.jar" 360,658 bytes, 105 classes
(98 + 7 kit), 72 rows, access audit 19,936 references 0 refused; python tools/ci/lint.py 0 fails (the 26 warnings are SkyySacks 0.7.13's);
test_skyygear_0.2.5.py 1375 ok, 0 FAIL, 35 expected deviations (each listed with its reason; every 0.1 ... 0.2.3 section carried + section AF);
tools/ci/crosscheck.py --jar SkyyGear-0.2.5.jar --baseline READY (28 jars, 1199 classes -Xverify:all, 81,415 refs 0 refused, command tree
identical) and with SkyyMobs 0.1.4 + SkyySkills 0.4.17 (the round's other builders, unreviewed) READY (1205 classes, 0 refused).
FIXER 2026-10-06 (same version, never deployed): data-migration critic item 1 - gcUpdate's crB / crW / crR copied the CR of the anchor's
last line, which is empty when that line is the file's unterminated last line, so a CRLF file without a final newline got bare-LF inserted
lines; such an anchor now takes crDef (the file's own CRLF / LF). Harness AF6(n) (critic case, every anchor last, 600 random CRLF files).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.4.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.5.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.4"' in s and s.startswith('"""SkyyGear 0.2.4 - build script'), "build_skyygear_0.2.4.py is not the live 0.2.4"
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.4 - build script (javassist via jpype). GENERATED by tools/gear_0_2_4_patch.py from the LIVE 0.2.3 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.4.py -> SkyyGear/SkyyGear-0.2.4.jar (never --deploy).

0.2.4 = ''', '''"""SkyyGear 0.2.5 - build script (javassist via jpype). GENERATED by tools/gear_0_2_5_patch.py from the LIVE 0.2.4 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.5.py -> SkyyGear/SkyyGear-0.2.5.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.5 = "):].strip() + '''

0.2.4 (the base, everything below is still true unless 0.2.5 above says otherwise):
0.2.4 = ''')
rep('VERSION = "0.2.4"', 'VERSION = "0.2.5"')

# ================================================================================================================ python constants
rep('''BASE_CURVE_DEF = "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0"
BASE_RES_DEF = "1:1.0,10:1.4,20:1.7,40:2.2,100:3.0"''', '''BASE_CURVE_DEF = "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0"      # 0.2.5: the 0.2.1 F = the Spell curve default + what migrate025 replaces
BASE_RES_DEF = "1:1.0,10:1.4,20:1.7,40:2.2,100:3.0"
# 0.2.5 (research/Mob-Curve-Spec.md 2.2): the steep Weapon curve F (base.curve's new default), the Spell curve S (= the old F) and the Armor
# Health curve H. F and H equal the old F up to Lv 20: the Lv 20 point is written 2.3333333333333335 = 7/3 to double precision (the spec's
# 2.333333 is 3e-7 low and still flips an EXACT .5 tooltip rounding: a Lv 13 / Lv 19 staff swing 5 x 2.1 = 10.5 -> "10" instead of 0.2.4's
# "11"); with 7/3 the curve equals the old F bit for bit at 19 of Lv 0-20 and within 1 ulp at Lv 15 / 19. Every factor <= 90 (curvePts <= 100)
BASE_CURVE_NEW = "1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.1,30:4.5,35:6.5,40:9.6,45:13.6,50:17.5,60:22.5,70:36.0,80:57.0,90:90.0"
BASE_SPELL_DEF = BASE_CURVE_DEF
BASE_HP_DEF = "1:1.0,4:1.6,10:2.0,20:2.3333333333333335,25:3.7,30:5.4,35:7.3,40:9.6,45:12.8,50:16.3,60:21.0,70:30.0,80:43.0,90:62.0,100:88.0"
STEAL_MAX_DEF = 5           # % of max Health per second (spec 2.5, Skyy's question 10 = yes)
LVLUP_CAP_DEF = 6           # Skyy LOCKED 2026-10-04: at most +6 levels over the level the item was made / found at
# coins per +1 level by rarity: base + per level x the NEW level (PLACEHOLDERS - Skyy: "coins per level, rising with level + rarity")
COST_L_DEF = {"normal": (100, 20), "unique": (200, 40), "rare": (400, 80), "legendary": (1000, 200), "fabled": (2000, 400),
              "mythic": (4000, 800), "set": (1000, 200)}''')
rep('''def py_bonus(start, pct=BASE_MAT_DEF):''', '''for _l in range(0, 21):
    assert abs(py_curve(BASE_CURVE_NEW, _l) - py_curve(BASE_CURVE_DEF, _l)) < 1e-15 and abs(py_curve(BASE_HP_DEF, _l) - py_curve(BASE_CURVE_DEF, _l)) < 1e-15, \\
        "0.2.5: F and H must equal the 0.2.1 F at item level %d (nothing changes at Lv 1-20)" % _l
assert [round(py_curve(BASE_CURVE_NEW, _l), 2) for _l in (25, 30, 33, 35, 40, 45, 49)] == [3.1, 4.5, 5.7, 6.5, 9.6, 13.6, 16.72], "spec 2.3 F column"
assert [round(py_curve(BASE_HP_DEF, _l), 2) for _l in (25, 30, 35, 40)] == [3.7, 5.4, 7.3, 9.6], "spec 2.2 H"
assert max(float(_p.split(":")[1]) for _x in (BASE_CURVE_NEW, BASE_HP_DEF) for _p in _x.split(",")) <= 100.0


def py_bonus(start, pct=BASE_MAT_DEF):''')
# the 0.2.5 marker + who (migrate025)
rep('''XC_ROWK = ["xp.craftCurve"]''', '''XC_ROWK = ["xp.craftCurve"]
# 0.2.5: the marker of the one-time update GearCfg.migrate025 (a comment without '='); it heads the level curves block, which a fresh file
# carries right under base.curve and migrate025 adds there to an existing file
GC_MARK_ID = "SkyyGear 0.2.5 level curves"
GC_MARK = ("# %s (Skyy 2026-10-05, the mob curve): weapons follow the steep Weapon curve F(L) after Lv 20, wand / staff / spellbook shots keep "
           "the Spell curve S(L) (the old F), worn armor Health follows the Armor Health curve H(L); SkyyGear shows and applies all armor stats "
           "(the vanilla armor box is hidden, a restart row)" % GC_MARK_ID)
GC_WHO = "SkyyGear 0.2.5"
assert all(32 <= ord(_c) < 127 for _c in GC_MARK) and "=" not in GC_MARK, "the level curves marker must be plain ASCII without '='"
GC_ROWK = ["base.spellCurve", "base.hpCurve", "view.hideArmorBox"]
SM_ROWK = ["steal.maxPerSec"]
LU_ROWK = ["reforge.levelUp", "reforge.levelCap"]
LU_TBLC = "# ---- cost.levelUp.<id>=<base coins>,<coins per item level> (one Reforge level up = base + per level x the new level) ----"
LU_TBLL = ["cost.levelUp.%s=%d,%d" % ((_r,) + COST_L_DEF[_r]) for _r in R_IDS]
assert all(32 <= ord(_c) < 127 for _c in LU_TBLC) and "=" in LU_TBLC and LU_TBLC.startswith("# ---- ") and "spec" not in LU_TBLC.lower()''')

# ================================================================================================================ Server Setup rows
rep('''    ("base.curve", "Level curve F(L)", "base", "text", BASE_CURVE_DEF, "3", "300", "", "", "live,danger",
     "level:factor points, straight lines between. Damage + armor Health." + PH,
     "field:GearCfg.BASE_CURVE;check=GearCfg.checkCurve"),''', '''    ("base.curve", "Weapon curve F(L)", "base", "text", BASE_CURVE_NEW, "3", "300", "", "", "live,danger",
     "Weapon hits (swords, bows, axes ...): level:factor points." + PH,
     "field:GearCfg.BASE_CURVE;check=GearCfg.checkCurve"),
    # 0.2.5 (research/Mob-Curve-Spec.md 2.2, 6.2): spells keep the old F; armor Health its own curve (keep it in step with mob damage)
    ("base.spellCurve", "Spell curve S(L)", "base", "text", BASE_SPELL_DEF, "3", "300", "", "", "live,danger",
     "Wand / staff / spellbook shots; their metal ladder adds the rest." + PH,
     "field:GearCfg.BASE_SPELL;check=GearCfg.checkCurve"),
    ("base.hpCurve", "Armor Health curve H(L)", "base", "text", BASE_HP_DEF, "3", "300", "", "", "live,danger",
     "Worn armor Health; keep it in step with mob damage." + PH,
     "field:GearCfg.BASE_HP;check=GearCfg.checkCurve"),''')
rep('''    ("cost.identify", "Identify cost", "costs", "table",''', '''    # 0.2.5 REFORGE LEVEL UP (Skyy LOCKED 2026-10-04: coins per level, at most +6 over the level it was made / found at)
    ("reforge.levelUp", "Reforge level up", "costs", "bool", "true", "", "", "", "", "live,danger",
     "Reforge page: +1 item level per click for coins (never above your level or the metal's top).",
     "field:GearCfg.LVLUP_ON"),
    ("reforge.levelCap", "Level ups at most", "costs", "int", str(LVLUP_CAP_DEF), "0", "50", "", "", "live,danger",
     "An item rises at most this many levels over the level it was made or found at (Skyy: 6).",
     "field:GearCfg.LVLUP_CAP"),
    ("cost.levelUp", "Level up cost", "costs", "table", "", "0", "1000000000000", "int;none;Base|Per level", "coins",
     "live,danger", "Coins per level up by rarity: base + per level x the new level." + PH,
     "reload@%s:cost.levelUp.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("cost.identify", "Identify cost", "costs", "table",''')
rep('''    ("regen.periodMs", "Regen tick", "combat", "int",''', '''    # 0.2.5 (spec 2.5, Skyy's question 10): Life Steal capped at 5 % of max Health per second (paid each steal window)
    ("steal.maxPerSec", "Life Steal at most", "combat", "dec", str(STEAL_MAX_DEF), "0", "100", "", "%", "live,danger",
     "Life Steal heals at most this % of max Health per second (paid each steal window). 0 = no cap.",
     "field:GearCfg.STEAL_MAX"),
    ("regen.periodMs", "Regen tick", "combat", "int",''')
rep('''     "Gear weapons show only SkyyGear's levelled damage line, not the vanilla box (needs a restart).", "field:GearCfg.HIDE_BOX"),''',
    '''     "Gear weapons show only SkyyGear's levelled damage line, not the vanilla box (needs a restart).", "field:GearCfg.HIDE_BOX"),
    # 0.2.5 (Skyy LOCKED 2026-10-05 "Yes, hide it"): the armor box goes; SkyyGear applies every armor stat of those types itself
    ("view.hideArmorBox", "Hide the vanilla armor box", "general", "bool", "true", "", "", "", "", "restart",
     "SkyyGear shows and applies all gear armor Health / resistance itself (needs a restart).", "field:GearCfg.HIDE_ABOX"),''')
rep('''           "xp.craft", "xp.craftCurve"}''', '''           "xp.craft", "xp.craftCurve",
           # 0.2.5: two curves, the Life Steal cap, the level up switch / cap / coins
           "base.spellCurve", "base.hpCurve", "steal.maxPerSec", "reforge.levelUp", "reforge.levelCap", "cost.levelUp"}''')

# ================================================================================================================ the fresh default file
rep('''    L.append(LS_MARK)          # 0.2.1: the level stats marker + the new settings right under level.armorNative (a fresh file never updates)
    for k in LS_ROWK:
        scal(k)''', '''    L.append(LS_MARK)          # 0.2.1: the level stats marker + the new settings right under level.armorNative (a fresh file never updates)
    for k in LS_ROWK:
        scal(k)
        if k == "base.curve":  # 0.2.5: the level curves marker + its rows right under base.curve (a fresh file never updates)
            L.append(GC_MARK)
            for k2 in GC_ROWK:
                scal(k2)''')
rep('''    for r in R_IDS:
        L.append("cost.reforge.%s=%d,%d" % ((r,) + COST_R_DEF[r]))''', '''    for r in R_IDS:
        L.append("cost.reforge.%s=%d,%d" % ((r,) + COST_R_DEF[r]))
    for k in LU_ROWK:          # 0.2.5: the level up rows + their coin table right under the reforge costs (migrate025 adds them there)
        scal(k)
    L.append(LU_TBLC)
    L += LU_TBLL''')
rep('''    for k in ("combat.strPer", "combat.mpPer", "combat.defScale", "crit.base", "crit.baseDamage", "steal.windowS", "regen.periodMs",
              "speed.per"):
        scal(k)''', '''    for k in ("combat.strPer", "combat.mpPer", "combat.defScale", "crit.base", "crit.baseDamage", "steal.windowS", "steal.maxPerSec",
              "regen.periodMs", "speed.per"):
        scal(k)''')
# the 0.2.1 block asserts: the fresh file's 0.2.1 block now carries the 0.2.5 block lines under base.curve (GC_LINES) - the 0.2.1 shape
# (what migrate021 writes before migrate025 runs) = the fresh lines without them
rep('''LS_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in LS_ROWK]''',
    '''# 0.2.5: the level curves block (marker + its rows, help + key=default each) right under base.curve; GC_LINES = that block in the fresh file
GC_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in GC_ROWK]
GC_ROWL = ["%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k]) for _k in GC_ROWK]
assert GC_ROWL == ["base.spellCurve=" + BASE_SPELL_DEF, "base.hpCurve=" + BASE_HP_DEF, "view.hideArmorBox=true"] and all(_c.startswith("# ") for _c in GC_ROWC)
GC_LINES = [GC_MARK] + [x_ for p_ in zip(GC_ROWC, GC_ROWL) for x_ in p_]
_gi = _DL.index("base.curve=" + BASE_CURVE_NEW)
assert _DL[_gi + 1:_gi + 1 + len(GC_LINES)] == GC_LINES and DEFAULT_TEXT.count(GC_MARK_ID) == 1, "the 0.2.5 block sits right under base.curve"
assert all(_DL.count(_x) == 1 for _x in GC_LINES), "a 0.2.5 block line is not unique in the default file"
SM_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in SM_ROWK]
SM_ROWL = ["%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k]) for _k in SM_ROWK]
assert SM_ROWL == ["steal.maxPerSec=%d" % STEAL_MAX_DEF] and _DL[_DL.index("steal.windowS=3") + 1:_DL.index("steal.windowS=3") + 3] == SM_ROWC + SM_ROWL
LU_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in LU_ROWK]
LU_ROWL = ["%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k]) for _k in LU_ROWK]
assert LU_ROWL == ["reforge.levelUp=true", "reforge.levelCap=%d" % LVLUP_CAP_DEF]
LU_LINES = [x_ for p_ in zip(LU_ROWC, LU_ROWL) for x_ in p_] + [LU_TBLC] + LU_TBLL
_ri = _DL.index("cost.reforge.set=%d,%d" % COST_R_DEF["set"])
assert _DL[_ri + 1:_ri + 1 + len(LU_LINES)] == LU_LINES and _DL[_ri + 1 + len(LU_LINES)].startswith("cost.identify."), "level up rows under cost.reforge"
assert all(_DL.count(_x) == 1 for _x in SM_ROWC + SM_ROWL + LU_LINES), "a 0.2.5 line is not unique in the default file"
for _r in R_IDS:
    assert _dp.get("cost.levelUp." + _r) == "%d,%d" % COST_L_DEF[_r], _r
# the 0.2.1 checks below run on the fresh lines WITHOUT the 0.2.5 block (the shape migrate021 writes; migrate025 then adds the block)
_DL25 = _DL
_DL = [x_ for x_ in _DL if x_ not in GC_LINES]
LS_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in LS_ROWK]''')
rep('''assert all(_c.startswith("# ") for _c in LS_ROWC) and LS_ROWL == ["part.base=true", "base.mode=shape", "base.curve=" + BASE_CURVE_DEF,''',
    '''assert all(_c.startswith("# ") for _c in LS_ROWC) and LS_ROWL == ["part.base=true", "base.mode=shape", "base.curve=" + BASE_CURVE_NEW,''')
rep('''LS_LINES = [LS_MARK] + [x_ for p_ in zip(LS_ROWC, LS_ROWL) for x_ in p_] + [LS_TBLC] + LS_TBLL
assert all(_DL.count(_x) == 1 for _x in LS_LINES), "a 0.2.1 block line is not unique in the default file"''',
    '''LS_LINES = [LS_MARK] + [x_ for p_ in zip(LS_ROWC, LS_ROWL) for x_ in p_] + [LS_TBLC] + LS_TBLL
assert all(_DL.count(_x) == 1 for _x in LS_LINES), "a 0.2.1 block line is not unique in the default file"
_DL = _DL25          # 0.2.5: back to the real fresh lines''')

# ================================================================================================================ (source blocks)
MIG_SRC = r'''# ---- 0.2.5 ONE-TIME UPDATE migrate025 (research/Mob-Curve-Spec.md 6.4; PROJECT-RULES section 4): pure text step. null = the 0.2.5 marker is
# already in a comment line (a fresh file carries it). Else { new text, "base.curve old -> new" ("" = no value changed), String[] notes,
# String[] log rows (key, old, new), "base.spellCurve, ..." (what was added) }. base.curve: ONLY its last entry, one physical line, holding
# exactly the 0.2.1 default is rewritten (value text only; key, separator, CR kept) + one change-log row; the new / a missing value = the
# defaults for the two new curves; a hand-set value is kept and copied into both (flat gear stays flat). The block (marker + the rows the
# file lacks, exactly the fresh file's lines but the decided curve values) goes right after base.curve, else after the last base.* entry,
# else at the end; steal.maxPerSec right after steal.windowS, the level up rows + table right after the last cost.reforge.* entry (no
# anchor: appended to the block). Which keys are there is asked of java.util.Properties (what the loader reads): never shadowed.
M(gcf, r"""
public static Object[] gcUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(GC_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int cS = -1; int cE = -1; int bS = -1; int bE = -1; int wS = -1; int wE = -1; int rS = -1; int rE = -1; int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    if (key != null) {
      if (key.equals("base.curve")) { cS = k; cE = e; }
      if (key.startsWith("base.")) { bS = k; bE = e; }
      if (key.equals("steal.windowS")) { wS = k; wE = e; }
      if (key.startsWith("cost.reforge.")) { rS = k; rE = e; }
    }
    k = e + 1;
  }
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  String cv = pp.getProperty("base.curve");
  String ct = cv == null ? null : cv.trim();
  boolean rewrite = false;
  String spell = SPELL_DEF;
  String hp = HP_DEF;
  if (ct != null && ct.equals(CURVE_OLD) && cS >= 0 && cE == cS && @PKG@.CfgFile.value(l, cS).trim().equals(CURVE_OLD)) {
    rewrite = true;
    chg.append("base.curve ").append(CURVE_OLD).append(" -> ").append(CURVE_DEF);
    rows.add("base.curve");
    rows.add(CURVE_OLD);
    rows.add(CURVE_DEF);
  } else if (ct == null || ct.equals(CURVE_DEF)) {
    spell = SPELL_DEF;
  } else if (checkCurve("base.curve", ct) == null) {
    spell = ct;
    hp = ct;
    notes.add("base.curve=" + @PKG@.CfgRows.oneLine(ct) + " kept (custom) - base.spellCurve and base.hpCurve start as the same text, so weapons, spells and armor Health keep following it (0.2.5 defaults: F " + CURVE_DEF + ", H " + HP_DEF + ")");
  } else {
    notes.add("base.curve=" + @PKG@.CfgRows.oneLine(ct) + " kept - it is not a level:factor list (the loader uses " + CURVE_DEF + "); the new curves start at their defaults");
  }
  StringBuilder added = new StringBuilder();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(GC_MARK);
  String[] gv = new String[] { spell, hp, "true" };
  for (int i = 0; i < GC_ROWK.length; i++) {
    if (pp.getProperty(GC_ROWK[i]) != null) { notes.add(GC_ROWK[i] + " is already in the file - kept"); continue; }
    blk.add(GC_ROWC[i]);
    blk.add(GC_ROWK[i] + "=" + gv[i]);
    if (added.length() > 0) added.append(", ");
    added.append(GC_ROWK[i]);
  }
  java.util.ArrayList sm = new java.util.ArrayList();
  for (int i = 0; i < SM_ROWK.length; i++) {
    if (pp.getProperty(SM_ROWK[i]) != null) { notes.add(SM_ROWK[i] + " is already in the file - kept"); continue; }
    sm.add(SM_ROWC[i]);
    sm.add(SM_ROWL[i]);
    if (added.length() > 0) added.append(", ");
    added.append(SM_ROWK[i]);
  }
  java.util.ArrayList lu = new java.util.ArrayList();
  for (int i = 0; i < LU_ROWK.length; i++) {
    if (pp.getProperty(LU_ROWK[i]) != null) { notes.add(LU_ROWK[i] + " is already in the file - kept"); continue; }
    lu.add(LU_ROWC[i]);
    lu.add(LU_ROWL[i]);
    if (added.length() > 0) added.append(", ");
    added.append(LU_ROWK[i]);
  }
  boolean tc = false;
  for (int i = 0; i < LU_TBLL.length; i++) {
    String lk = LU_TBLL[i].substring(0, LU_TBLL[i].indexOf('='));
    if (pp.getProperty(lk) != null) { notes.add(lk + " is already in the file - kept"); continue; }
    if (!tc) { lu.add(LU_TBLC); tc = true; }
    lu.add(LU_TBLL[i]);
    if (added.length() > 0) added.append(", ");
    added.append(lk);
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    if (rewrite && i == cS) {
      String s2 = (String) l.get(i);
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + CURVE_DEF + (raw[i].endsWith("\r") ? "\r" : ""));
    } else out.add(raw[i]);
  }
  int aS = cS >= 0 ? cS : bS;
  int aE = cS >= 0 ? cE : bE;
  int pB = aS >= 0 ? chAfter(l, aS, aE) : chEnd(l, tail, raw);
  String crB = aS >= 0 && aE < raw.length - 1 ? (raw[aE].endsWith("\r") ? "\r" : "") : crDef;
  int pW = -1;
  String crW = crDef;
  if (sm.size() > 0) {
    if (wS >= 0) { pW = chAfter(l, wS, wE); crW = wE >= raw.length - 1 ? crDef : (raw[wE].endsWith("\r") ? "\r" : ""); }
    else blk.addAll(sm);
  }
  int pR = -1;
  String crR = crDef;
  if (lu.size() > 0) {
    if (rS >= 0) { pR = chAfter(l, rS, rE); crR = rE >= raw.length - 1 ? crDef : (raw[rE].endsWith("\r") ? "\r" : ""); }
    else blk.addAll(lu);
  }
  int[] pos = new int[] { pB, pW, pR };
  java.util.ArrayList[] what = new java.util.ArrayList[] { blk, pW >= 0 ? sm : null, pR >= 0 ? lu : null };
  String[] crs = new String[] { crB, crW, crR };
  boolean[] done = new boolean[3];
  for (int n = 0; n < 3; n++) {
    int best = -1;
    for (int j = 0; j < 3; j++) if (!done[j] && what[j] != null && (best < 0 || pos[j] > pos[best])) best = j;
    if (best < 0) break;
    done[best] = true;
    chPut(out, pos[best], what[best], crs[best]);
  }
  StringBuilder sb = new StringBuilder(text.length() + 2048);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) notes.toArray(new String[0]), (String[]) rows.toArray(new String[0]), added.toString() };
}""")
# one config-changes.log line in the kit's scalar-row format (Server Setup -> Changes undoes it with a plain set back to the old value)
M(gcf, r"""
public static String gcLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + GC_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(), right after migrate023 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes),
# the change-log row, one INFO line (+ one per note), gear.log; "" = nothing done (no file, marker already there, or a failure - WARN, file
# untouched, the next start tries again; the loader then runs the missing rows on their built-in defaults)
M(gcf, r"""
public static synchronized String migrate025() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = gcUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), GC_WHO, "before the 0.2.5 level curves");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated to the 0.2.5 level curves: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is - base.curve keeps its value, the new settings run on their defaults; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(gcLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] notes = (String[]) r[2];
    String add = (String) r[4];
    String msg = chg.length() > 0
      ? "config.properties updated to the 0.2.5 level curves: " + chg + " (weapons grow faster after Lv 20; the old file is in config-history; Server Setup -> Changes can undo it)"
      : "config.properties: base.curve did not hold the 0.2.1 default - no value changed (0.2.5 marker added)";
    if (add.length() > 0) msg = msg + "; new settings: " + add;
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.2.5 level curves: " + (chg.length() > 0 ? chg : "no value changed") + (add.length() > 0 ? "; added " + add : "") + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not update config.properties to the 0.2.5 level curves (the file is used as it is): " + t);
    return "";
  }
}""")
'''

ABOX_SRC = r'''# ================================================================= 0.2.5 GearABox: THE VANILLA ARMOR BOX, HIDDEN PER ITEM TYPE (see the header)
# The client draws the armor box (Health / Physical Resistance / Mana ...) from the ITEM ASSET packet: ItemArmor.toPacket sends its
# statModifiers (EntityStatMap.toPacket) and damageResistanceValues (null when empty) - VERIFIED bytecode. The engine reads the same two maps
# to apply them (StatModifiersManager.addArmorStatModifiers, DamageSystems$ArmorDamageReduction.getResistanceModifiers - the only readers).
# So per gear armor TYPE: keep the two original map objects here (SNAP) and swap the ItemArmor's fields for EMPTY maps (reflection, one
# reference write each: a world thread still iterating the old map keeps a consistent object) + drop the packet cache. The engine then
# applies nothing for those pieces and SkyyGear applies all of it (GearArmor.lockSums / hiddenRes read the kept maps). Restore = the
# original objects back. view.hideArmorBox is a restart row (clients load item definitions at join); start() hides every loaded type, the
# 0.2.2 LoadedAssetsEvent(Item) listener (GearBoxL, LAST priority) re-hides reloaded ones (their fresh maps are kept again).
F(gabox, "public static final java.util.concurrent.ConcurrentHashMap SNAP = new java.util.concurrent.ConcurrentHashMap();")   # id -> Object[] { ItemArmor, stats, res, our empty stats, our empty res }
F(gabox, "public static volatile boolean ON = true;")
F(gabox, "public static volatile boolean ORDERED = false;")
F(gabox, "public static volatile boolean STARTED = false;")
F(gabox, "public static volatile java.lang.reflect.Field FSM = null;")
F(gabox, "public static volatile java.lang.reflect.Field FDR = null;")
M(gabox, r"""
public static synchronized boolean fields() {
  if (FSM != null && FDR != null) return true;
  try {
    java.lang.reflect.Field a = @IAR@.class.getDeclaredField("statModifiers");
    java.lang.reflect.Field b = @IAR@.class.getDeclaredField("damageResistanceValues");
    a.setAccessible(true);
    b.setAccessible(true);
    FSM = a;
    FDR = b;
    return true;
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("aboxfields", "armor box: the engine's ItemArmor fields could not be reached (" + t + ") - gear armor keeps the vanilla box");
    return false;
  }
}""")
# a Head / Chest / Legs / Hands piece (the slots of the base.armor table)
M(gabox, r"""
public static boolean slotOk(@IAR@ a) {
  try {
    Object sl = a == null ? null : a.getArmorSlot();
    if (!(sl instanceof java.lang.Enum)) return false;
    String n = ((java.lang.Enum) sl).name();
    for (int i = 0; i < @PKG@.GearCfg.BA_SLOT.length; i++) if (@PKG@.GearCfg.BA_SLOT[i].equalsIgnoreCase(n)) return true;
  } catch (Throwable t) { }
  return false;
}""")
# the types whose box goes: gear armor of an enforced kind (combat / equipment) in a base.armor slot
M(gabox, r"""
public static boolean target(@ITM@ item) {
  if (item == null) return false;
  @IAR@ a = item.getArmor();
  String id = item.getId();
  if (a == null || id == null) return false;
  if (@PKG@.GearData.slotOf(id) != 2 || !@PKG@.GearData.isGear(id)) return false;
  if (!@PKG@.GearDefs.enforcedKind(@PKG@.GearData.kindFor(id))) return false;
  return slotOk(a);
}""")
# only ADDITIVE stat modifiers (SkyyGear's lock is one additive MAX modifier per stat; a multiplicative one keeps the vanilla box)
M(gabox, r"""
public static boolean additive(Object sm) {
  if (!(sm instanceof java.util.Map)) return true;
  java.util.Iterator e = ((java.util.Map) sm).values().iterator();
  while (e.hasNext()) {
    Object v = e.next();
    if (!(v instanceof Object[])) continue;
    Object[] xs = (Object[]) v;
    for (int j = 0; j < xs.length; j++) if (xs[j] instanceof @SMO@ && ((@SMO@) xs[j]).getCalculationType() != @CAL@.ADDITIVE) return false;
  }
  return true;
}""")
# how many items of the asset map point at each ItemArmor object (an ItemArmor shared by two items is never touched; vanilla shares none)
M(gabox, r"""
public static java.util.IdentityHashMap owners() {
  java.util.IdentityHashMap m = new java.util.IdentityHashMap();
  try {
    java.util.Map am = @ITM@.getAssetMap().getAssetMap();
    if (am == null) return m;
    java.util.Iterator e = new java.util.ArrayList(am.values()).iterator();
    while (e.hasNext()) {
      Object o = e.next();
      if (!(o instanceof @ITM@)) continue;
      @IAR@ a = ((@ITM@) o).getArmor();
      if (a == null) continue;
      Object c = m.get(a);
      m.put(a, Integer.valueOf(c instanceof Integer ? ((Integer) c).intValue() + 1 : 1));
    }
  } catch (Throwable t) { }
  return m;
}""")
# hide one item type; false = nothing to hide (not a target, already hidden, nothing in the maps, shared, non-additive)
M(gabox, r"""
public static synchronized boolean hide(@ITM@ item, java.util.IdentityHashMap own) {
  if (!target(item) || !fields()) return false;
  String id = item.getId();
  @IAR@ a = item.getArmor();
  Object c = own == null ? null : own.get(a);
  if (c instanceof Integer && ((Integer) c).intValue() > 1) {
    @PKG@.Gear.warnOnce("aboxshared:" + id, "armor box: " + id + " shares its armor data with another item - it keeps the vanilla box (levelled the 0.2.4 way)");
    return false;
  }
  Object sm = a.getStatModifiers();
  java.util.Map dr = a.getDamageResistanceValues();
  Object[] o = (Object[]) SNAP.get(id);
  if (o != null && o[0] == a && sm == o[3] && dr == o[4]) return false;
  boolean anyS = sm instanceof java.util.Map && !((java.util.Map) sm).isEmpty();
  boolean anyR = dr != null && !dr.isEmpty();
  if (!anyS && !anyR) return false;
  if (!additive(sm)) {
    @PKG@.Gear.warnOnce("aboxcalc:" + id, "armor box: " + id + " has a non-additive armor stat - it keeps the vanilla box (levelled the 0.2.4 way)");
    return false;
  }
  Object es = new it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap();
  java.util.Map er = new it.unimi.dsi.fastutil.objects.Object2ObjectOpenHashMap();
  SNAP.put(id, new Object[] { a, sm, dr, es, er });
  try {
    FSM.set(a, es);
    FDR.set(a, er);
    item.invalidatePacketCache();
    return true;
  } catch (Throwable t) {
    try { FSM.set(a, sm); FDR.set(a, dr); } catch (Throwable t2) { }
    SNAP.remove(id);
    @PKG@.Gear.warnOnce("abox:" + id, "armor box: could not hide it on " + id + " (" + t + ") - that item keeps its vanilla box");
    return false;
  }
}""")
# the kept maps of a type whose box is hidden RIGHT NOW (the item's live ItemArmor still holds our empty maps); null = not hidden
M(gabox, r"""
public static Object[] snap(String id) {
  if (id == null || SNAP.isEmpty()) return null;
  Object o = SNAP.get(id);
  if (!(o instanceof Object[])) return null;
  Object[] s = (Object[]) o;
  @ITM@ item = @PKG@.Gear.item(id);
  @IAR@ a = item == null ? null : item.getArmor();
  if (a == null || a != s[0]) return null;
  Object cs = a.getStatModifiers();
  Object cr = a.getDamageResistanceValues();
  if (cs != s[3] || cr != s[4]) return null;
  return s;
}""")
M(gabox, "public static boolean hidden(String id) { return snap(id) != null; }")
# what the tooltip / describe read: the kept maps of a hidden type, else the asset's own
M(gabox, r"""
public static Object stats(String id, @IAR@ a) {
  Object[] s = snap(id);
  if (s != null) return s[1];
  return a == null ? null : a.getStatModifiers();
}""")
M(gabox, r"""
public static java.util.Map res(String id, @IAR@ a) {
  Object[] s = snap(id);
  if (s != null) return (java.util.Map) s[2];
  return a == null ? null : a.getDamageResistanceValues();
}""")
M(gabox, r"""
public static boolean anyHidden(@IC@ armor) {
  if (armor == null || SNAP.isEmpty()) return false;
  for (int i = 0; i < armor.getCapacity(); i++) {
    @IS@ s = armor.getItemStack((short) i);
    if (s != null && !s.isEmpty() && hidden(s.getItemId())) return true;
  }
  return false;
}""")
# the kept ADDITIVE Health of a hidden type (-1 = not hidden) and its kept multiplier resistance against one cause id (-1 = not hidden)
M(gabox, r"""
public static float snapHealth(String id) {
  Object[] s = snap(id);
  if (s == null) return -1.0f;
  float sum = 0.0f;
  if (!(s[1] instanceof java.util.Map)) return 0.0f;
  int hi = @DST@.getHealth();
  java.util.Iterator e = ((java.util.Map) s[1]).entrySet().iterator();
  while (e.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) e.next();
    if (!(en.getKey() instanceof Number) || ((Number) en.getKey()).intValue() != hi || !(en.getValue() instanceof Object[])) continue;
    Object[] xs = (Object[]) en.getValue();
    for (int j = 0; j < xs.length; j++) if (xs[j] instanceof @SMO@ && ((@SMO@) xs[j]).getCalculationType() == @CAL@.ADDITIVE) sum = sum + ((@SMO@) xs[j]).getAmount();
  }
  return sum;
}""")
M(gabox, r"""
public static float snapRes(String id, String cause) {
  Object[] s = snap(id);
  if (s == null) return -1.0f;
  if (!(s[2] instanceof java.util.Map)) return 0.0f;
  float sum = 0.0f;
  java.util.Iterator e = ((java.util.Map) s[2]).entrySet().iterator();
  while (e.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) e.next();
    Object k = en.getKey();
    String cid = k instanceof @DCS@ ? ((@DCS@) k).getId() : String.valueOf(k);
    if (!cause.equals(cid) || !(en.getValue() instanceof Object[])) continue;
    Object[] xs = (Object[]) en.getValue();
    for (int j = 0; j < xs.length; j++) if (xs[j] instanceof @RMOD@ && ((@RMOD@) xs[j]).getCalculationType() != @RCT@.FLAT) sum = sum + ((@RMOD@) xs[j]).getAmount();
  }
  return sum;
}""")
M(gabox, r"""
public static void put(java.util.HashMap out, int k, float delta) {
  if (delta == 0.0f) return;
  Integer key = Integer.valueOf(k);
  Object prev = out.get(key);
  out.put(key, Float.valueOf((prev instanceof Float ? ((Float) prev).floatValue() : 0.0f) + delta));
}""")
# the lock want of one worn hidden piece (GearArmor.lockSums; signed: the modifier holds -sum, so an amount SkyyGear ADDS goes in as -amount):
# every kept ADDITIVE stat (the engine's sum per stat), Health replaced by the levelled target tgH when tgH >= 0, x the broken factor f
M(gabox, r"""
public static void addStats(String id, float f, boolean broken, float tgH, java.util.HashMap out) {
  Object[] s = snap(id);
  if (s == null || out == null) return;
  int hi = @DST@.getHealth();
  boolean hd = false;
  if (s[1] instanceof java.util.Map) {
    java.util.Iterator e = ((java.util.Map) s[1]).entrySet().iterator();
    while (e.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) e.next();
      if (!(en.getKey() instanceof Number) || !(en.getValue() instanceof Object[])) continue;
      int k = ((Number) en.getKey()).intValue();
      Object[] xs = (Object[]) en.getValue();
      float sum = 0.0f;
      for (int j = 0; j < xs.length; j++) if (xs[j] instanceof @SMO@ && ((@SMO@) xs[j]).getCalculationType() == @CAL@.ADDITIVE) sum = sum + ((@SMO@) xs[j]).getAmount();
      if (k == hi && tgH >= 0.0f) { sum = tgH; hd = true; }
      if (broken) sum = sum * f;
      put(out, k, -sum);
    }
  }
  if (!hd && tgH > 0.0f) put(out, hi, -(broken ? tgH * f : tgH));
}""")
# one cause entry of an armor resistance map (GearArmor.addRes, with a FLAT part too): an existing entry for that cause id gains the parts; a
# set without it gets a new ArmorResistanceModifiers keyed by the cause asset with the engine's parent link (getInherits)
M(gabox, r"""
public static void putRes(java.util.Map m, String cause, float flat, float mult) {
  if (m == null || cause == null || (flat == 0.0f && mult == 0.0f)) return;
  java.util.Iterator it2 = m.entrySet().iterator();
  while (it2.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it2.next();
    if (en.getKey() instanceof @DCS@ && cause.equals(((@DCS@) en.getKey()).getId()) && en.getValue() instanceof @ARMR@) {
      @ARMR@ r0 = (@ARMR@) en.getValue();
      r0.flatModifier = r0.flatModifier + flat;
      r0.multiplierModifier = r0.multiplierModifier + mult;
      return;
    }
  }
  Object c = null;
  try { c = @DCS@.getAssetMap().getAsset(cause); } catch (Throwable t) { c = null; }
  if (!(c instanceof @DCS@)) return;
  @ARMR@ r = new @ARMR@();
  r.flatModifier = flat;
  r.multiplierModifier = mult;
  String inh = ((@DCS@) c).getInherits();
  if (inh != null) {
    Object pc = null;
    try { pc = @DCS@.getAssetMap().getAsset(inh); } catch (Throwable t2) { pc = null; }
    if (pc instanceof @DCS@) r.inheritedParentId = (@DCS@) pc;
  }
  m.put(c, r);
}""")
# the resistance of one worn hidden piece on top of a getResistanceModifiers map (GearArmor.hiddenRes): every kept entry the way the engine's
# calculateResistanceEntryModifications adds it (FLAT -> flat, else -> multiplier, + BaseDamageResistance as flat per entry), Physical /
# Projectile multiplier = the levelled tgR when tgR >= 0 (a set without those entries gets them), all x k (the broken factor or 1)
M(gabox, r"""
public static void addRes(String id, java.util.Map m, float tgR, float k) {
  Object[] s = snap(id);
  if (s == null || m == null) return;
  float base = 0.0f;
  try { base = (float) ((@IAR@) s[0]).getBaseDamageResistance(); } catch (Throwable t) { base = 0.0f; }
  boolean ph = false;
  boolean pj = false;
  if (s[2] instanceof java.util.Map) {
    java.util.Iterator e = ((java.util.Map) s[2]).entrySet().iterator();
    while (e.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) e.next();
      Object key = en.getKey();
      if (!(en.getValue() instanceof Object[])) continue;
      String cid = key instanceof @DCS@ ? ((@DCS@) key).getId() : String.valueOf(key);
      if (cid == null) continue;
      Object[] xs = (Object[]) en.getValue();
      float fl = base;
      float mu = 0.0f;
      for (int j = 0; j < xs.length; j++) {
        if (!(xs[j] instanceof @RMOD@)) continue;
        @RMOD@ r = (@RMOD@) xs[j];
        if (r.getCalculationType() == @RCT@.FLAT) fl = fl + r.getAmount();
        else mu = mu + r.getAmount();
      }
      if (tgR >= 0.0f && "Physical".equals(cid)) { mu = tgR; ph = true; }
      if (tgR >= 0.0f && "Projectile".equals(cid)) { mu = tgR; pj = true; }
      putRes(m, cid, fl * k, mu * k);
    }
  }
  if (tgR > 0.0f && !ph) putRes(m, "Physical", 0.0f, tgR * k);
  if (tgR > 0.0f && !pj) putRes(m, "Projectile", 0.0f, tgR * k);
}""")
# put the original maps back (only over our own empty maps - never over a newer engine computation)
M(gabox, r"""
public static synchronized boolean restore(@ITM@ item) {
  if (item == null || item.getId() == null || !fields()) return false;
  Object o = SNAP.get(item.getId());
  if (!(o instanceof Object[])) return false;
  Object[] s = (Object[]) o;
  SNAP.remove(item.getId());
  @IAR@ a = item.getArmor();
  if (a == null || a != s[0]) return false;
  Object cs = a.getStatModifiers();
  Object cr = a.getDamageResistanceValues();
  if (cs != s[3] || cr != s[4]) return false;
  try {
    FSM.set(a, s[1]);
    FDR.set(a, s[2]);
    item.invalidatePacketCache();
    return true;
  } catch (Throwable t) { return false; }
}""")
M(gabox, r"""
public static int applyAll(boolean on) {
  java.util.Map m = @ITM@.getAssetMap().getAssetMap();
  if (m == null) return 0;
  java.util.IdentityHashMap own = on ? owners() : null;
  int n = 0;
  java.util.Iterator e = new java.util.ArrayList(m.values()).iterator();
  while (e.hasNext()) {
    Object o = e.next();
    if (!(o instanceof @ITM@)) continue;
    @ITM@ item = (@ITM@) o;
    try {
      boolean ch = on ? hide(item, own) : restore(item);
      if (ch) n++;
    } catch (Throwable t) {
      @PKG@.Gear.warnOnce("abox:" + item.getId(), "armor box: could not " + (on ? "hide" : "restore") + " it on " + item.getId() + " (" + t + ") - that item keeps its vanilla box");
    }
  }
  return n;
}""")
# LoadedAssetsEvent(Item) (the GearBoxL listener, LAST priority): reloaded gear armor types come with fresh maps - keep and hide them again.
# Only after start(): during the first asset load the item map is still filling, so the shared-ItemArmor test (owners) could miss the second
# item of a pair - start() hides everything once every pack is loaded
M(gabox, r"""
public static int onLoaded(Object e) {
  if (!ON || !ORDERED || !STARTED || !(e instanceof @LAE@)) return 0;
  java.util.Map lm = ((@LAE@) e).getLoadedAssets();
  if (lm == null || lm.isEmpty()) return 0;
  java.util.IdentityHashMap own = owners();
  int n = 0;
  java.util.Iterator it2 = new java.util.ArrayList(lm.values()).iterator();
  while (it2.hasNext()) {
    Object o = it2.next();
    if (!(o instanceof @ITM@)) continue;
    try { if (hide((@ITM@) o, own)) n++; }
    catch (Throwable t) { @PKG@.Gear.warnOnce("aboxl:" + ((@ITM@) o).getId(), "armor box: could not hide it on reloaded " + ((@ITM@) o).getId() + " (" + t + ")"); }
  }
  if (n > 0 && STARTED) @PKG@.Gear.info("armor box: hidden on " + n + " reloaded gear armor type(s) - players who joined before the reload keep the vanilla box on those until they rejoin");
  return n;
}""")
M(gabox, r"""
public static String start() {
  STARTED = true;
  if (!ON) return "vanilla armor box shown (view.hideArmorBox off)";
  if (!ORDERED) {
    @PKG@.Gear.warn("the vanilla armor box stays this start: SkyyGear's armor damage systems run unordered, so it could not apply those pieces' resistance itself");
    return "vanilla armor box shown (unordered armor systems)";
  }
  int n = applyAll(true);
  return "vanilla armor box hidden on " + SNAP.size() + " gear armor types (" + n + " at start; SkyyGear applies their Health, resistance and other stats itself)";
}""")
M(gabox, r"""
public static String readyText() {
  return ON ? "the vanilla armor box is hidden on gear armor once every pack is loaded (SkyyGear applies those stats)" : "the vanilla armor box stays (view.hideArmorBox off)";
}""")
'''

LVL_SRC = r'''# ---- 0.2.5 REFORGE LEVEL UP (Skyy LOCKED 2026-10-04): +1 level per click for coins; at most reforge.levelCap (6) over the level the item was
# made / found at (lvl0), never above its band's cap (the metal's top level) and never above the player's own level in the item's gate skill
# (GearRoll.craftHave + the gate floor - the "crafted at your level" skill). Object[] { Integer code, Integer cur, Integer next, Integer max,
# Integer origin, String text }: code 0 = it can go up (max = the highest level it can reach now), 1 off, 2 admin level, 3 at its band cap,
# 4 at +cap, 5 your level too low, 6 your level unknown (no class), 7 unreadable
M(gfg, r"""
public static Object[] lvOut(int code, int cur, int max, int org, String t) {
  return new Object[] { Integer.valueOf(code), Integer.valueOf(cur), Integer.valueOf(cur + 1), Integer.valueOf(max), Integer.valueOf(org), t };
}""")
M(gfg, r"""
public static Object[] lvlInfo(java.util.UUID u, String id, @BD@ d) {
  int cur = @PKG@.GearLevel.level(id, d);
  int org = @PKG@.GearRoll.origin(id, d);
  int[] b = @PKG@.GearLevel.band(id);
  int capUp = org + @PKG@.GearCfg.LVLUP_CAP;
  int max = b[1] < capUp ? b[1] : capUp;
  if (max > 100) max = 100;
  if (!@PKG@.GearCfg.LVLUP_ON || !@PKG@.GearCfg.PART_LEVELS) return lvOut(1, cur, max, org, "Level up is off on this server.");
  if (d == null) return lvOut(7, cur, max, org, "The gear data on this item is unreadable.");
  if (@PKG@.GearData.bool(d, "lvlA", false)) return lvOut(2, cur, max, org, "an admin set its level - it cannot be levelled up.");
  if (cur >= b[1]) return lvOut(3, cur, max, org, @PKG@.GearLevel.bandWord(id) + " caps at Lv " + b[1] + " - a better material goes higher.");
  if (cur >= capUp) return lvOut(4, cur, max, org, "already +" + (cur - org) + " over Lv " + org + " (made / found) - the most is +" + @PKG@.GearCfg.LVLUP_CAP + ".");
  int h = @PKG@.GearRoll.craftHave(id, u);
  if (h < 0) return lvOut(6, cur, max, org, "your level for it is unknown (pick a class) - it never goes above your level.");
  int have = @PKG@.GearLevel.floor(h);
  int top = have < max ? have : max;
  if (cur + 1 > have) return lvOut(5, cur, top, org, "your " + @PKG@.GearRoll.craftLabel(id, u) + " is " + h + " - an item never goes above your level.");
  return lvOut(0, cur, top, org, "Lv " + cur + " -> " + (cur + 1) + " (it can reach Lv " + top + "; made / found at Lv " + org + ")");
}""")
# Object[] { Integer code (1 done, 0 refused, -1 failed + refunded / not refunded), String message, IS newStack, BD before, BD after, Long cost,
# Object[] rest of a stack or null } - the reforge() write safety: same slot + fingerprint, refusals before any coin moves, coins TAKEN FIRST,
# REFUND on any failure, a stack gives up ONE item (GearStamp.takeOne), the new stack replaces the old one in the same slot
M(gfg, r"""
public static Object[] levelUp(@IC@ c, int slot, String expId, String expFp, java.util.UUID u, String who, @IC@[] give, @IC@[] all) {
  @IS@ it = null;
  try { if (c != null && slot >= 0 && slot < c.getCapacity()) it = c.getItemStack((short) slot); } catch (Throwable t0) { it = null; }
  if (!same(it, expId, expFp)) return new Object[] { Integer.valueOf(0), "That item moved or changed - pick it again.", null, null, null, Long.valueOf(0L), null };
  String id = it.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a level up");
  if (why != null) return new Object[] { Integer.valueOf(0), why, null, null, null, Long.valueOf(0L), null };
  Object[] li = lvlInfo(u, id, d);
  if (((Integer) li[0]).intValue() != 0) return new Object[] { Integer.valueOf(0), "Level up: " + (String) li[5], null, null, null, Long.valueOf(0L), null };
  int r = @PKG@.GearData.rarity(d);
  int cur = ((Integer) li[1]).intValue();
  int next = ((Integer) li[2]).intValue();
  long cost = @PKG@.GearCfg.costLevelUp(r, next);
  if (cost > 0L) {
    int t = take(u, cost);
    if (t < 0) return new Object[] { Integer.valueOf(0), "Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken.", null, null, null, Long.valueOf(0L), null };
    if (t == 0) {
      long have = purse(u);
      return new Object[] { Integer.valueOf(0), "Not enough coins: this level up costs " + @PKG@.Gear.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Gear.fmt(have) : "") + ".", null, null, null, Long.valueOf(0L), null };
    }
    @PKG@.GearLog.line("TAKE " + who + " " + u + " " + cost + " levelup " + id);
  }
  @BD@ nd = null;
  @IS@ nu = null;
  Object tx = null;
  Object[] rest = null;
  Throwable err = null;
  try {
    if (it.getQuantity() > 1) {
      rest = @PKG@.GearStamp.takeOne(c, slot, give, all, u);
      if (rest == null) throw new IllegalStateException("the stack could not be split");
      it = c.getItemStack((short) slot);
      if (!same(it, expId, expFp) || it.getQuantity() != 1) throw new IllegalStateException("the stack changed while it was split");
    }
    nd = @PKG@.GearRoll.levelUp(id, d, next);
    nu = @PKG@.GearData.put(it, nd, u);
    tx = c.setItemStackForSlot((short) slot, nu);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && nu != null && nu != it && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Gear.warn("LEVEL UP FAILED for " + who + " (" + u + ") on " + id + ": " + what + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    if (cost > 0L) @PKG@.GearLog.line((back ? "REFUND " : "REFUND-FAILED ") + who + " " + u + " " + cost + " levelup " + id + ": " + what);
    return new Object[] { Integer.valueOf(-1), back ? "The level up failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Gear.fmt(cost) + " coins were refunded." : ".") : "The level up failed and the refund did not go through - an admin can find it in the server log.", null, d, null, Long.valueOf(cost), rest };
  }
  @PKG@.GearLog.line("LEVELUP " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r] + " lv" + cur + " -> lv" + next + " (made / found lv" + li[4] + ", cap +" + @PKG@.GearCfg.LVLUP_CAP + ") cost " + cost + " lvU " + @PKG@.GearData.num(nd, "lvU", 0));
  return new Object[] { Integer.valueOf(1), "Levelled up!", nu, d, nd, Long.valueOf(cost), rest };
}""")

'''

# ================================================================================================================ GearCfg: fields + constants
rep('''("BASE_CURVE", "String", jstr(BASE_CURVE_DEF)),''', '''("BASE_CURVE", "String", jstr(BASE_CURVE_NEW)),''')
rep('''              ("XPC_CURVE", "String", jstr(XPC_CURVE_DEF))]''', '''              ("XPC_CURVE", "String", jstr(XPC_CURVE_DEF)),
              # 0.2.5 the spell + armor Health curves, the Life Steal cap, Reforge level up, the vanilla armor box (restart row)
              ("BASE_SPELL", "String", jstr(BASE_SPELL_DEF)), ("BASE_HP", "String", jstr(BASE_HP_DEF)), ("STEAL_MAX", "double", repr(float(STEAL_MAX_DEF))),
              ("LVLUP_ON", "boolean", "true"), ("LVLUP_CAP", "int", str(LVLUP_CAP_DEF)), ("HIDE_ABOX", "boolean", "true")]''')
rep('''F(gcf, "public static final String XPC_DEF = %s;" % jstr(XPC_CURVE_DEF))''', '''F(gcf, "public static final String XPC_DEF = %s;" % jstr(XPC_CURVE_DEF))
# 0.2.5 Reforge level up coins by rarity (base + per level x the new level)
for _nm, _col in (("LU_BASE", 0), ("LU_PER", 1)):
    F(gcf, "public static volatile long[] %s = new long[] { %s };" % (_nm, ", ".join("%dL" % COST_L_DEF[r][_col] for r in R_IDS)))
    F(gcf, "public static final long[] D%s = new long[] { %s };" % (_nm, ", ".join("%dL" % COST_L_DEF[r][_col] for r in R_IDS)))''')
rep('''F(gcf, "public static final String CURVE_DEF = %s;" % jstr(BASE_CURVE_DEF))''', '''F(gcf, "public static final String CURVE_DEF = %s;" % jstr(BASE_CURVE_NEW))      # 0.2.5: the steep Weapon curve F
F(gcf, "public static final String CURVE_OLD = %s;" % jstr(BASE_CURVE_DEF))      # 0.2.5: the 0.2.1 F (migrate025 replaces it)
F(gcf, "public static final String SPELL_DEF = %s;" % jstr(BASE_SPELL_DEF))
F(gcf, "public static final String HP_DEF = %s;" % jstr(BASE_HP_DEF))''')
rep('''F(gcf, "public static final String[] XC_LINES = %s;" % jarr(XC_LINES))''', '''F(gcf, "public static final String[] XC_LINES = %s;" % jarr(XC_LINES))
# 0.2.5: migrate025 marker / name and the lines it adds (the fresh file's lines; the curve VALUES follow the decision table); the whole
# fresh-file blocks (the harness strips them to compare older shapes)
F(gcf, "public static final String GC_MARK = %s;" % jstr(GC_MARK))
F(gcf, "public static final String GC_MARK_ID = %s;" % jstr(GC_MARK_ID))
F(gcf, "public static final String GC_WHO = %s;" % jstr(GC_WHO))
F(gcf, "public static final String[] GC_ROWK = %s;" % jarr(GC_ROWK))
F(gcf, "public static final String[] GC_ROWC = %s;" % jarr(GC_ROWC))
F(gcf, "public static final String[] GC_LINES = %s;" % jarr(GC_LINES))
F(gcf, "public static final String[] SM_ROWK = %s;" % jarr(SM_ROWK))
F(gcf, "public static final String[] SM_ROWC = %s;" % jarr(SM_ROWC))
F(gcf, "public static final String[] SM_ROWL = %s;" % jarr(SM_ROWL))
F(gcf, "public static final String[] LU_ROWK = %s;" % jarr(LU_ROWK))
F(gcf, "public static final String[] LU_ROWC = %s;" % jarr(LU_ROWC))
F(gcf, "public static final String[] LU_ROWL = %s;" % jarr(LU_ROWL))
F(gcf, "public static final String LU_TBLC = %s;" % jstr(LU_TBLC))
F(gcf, "public static final String[] LU_TBLL = %s;" % jarr(LU_TBLL))
F(gcf, "public static final String[] LU_LINES = %s;" % jarr(LU_LINES))''')

# ================================================================================================================ GearCfg: the loader
rep('''  BASE_CURVE = bcv;''', '''  BASE_CURVE = bcv;
  // 0.2.5 the spell + armor Health curves (a hand edit the check would refuse falls back to its default with one WARN)
  String bsv = ptext(p, "base.spellCurve", SPELL_DEF);
  if (checkCurve("base.spellCurve", bsv) != null) { @PKG@.Gear.warnOnce("scurve:" + bsv, "config.properties: base.spellCurve=" + bsv + " is not a list of level:factor points - the default " + SPELL_DEF + " is used"); bsv = SPELL_DEF; }
  BASE_SPELL = bsv;
  String bhv = ptext(p, "base.hpCurve", HP_DEF);
  if (checkCurve("base.hpCurve", bhv) != null) { @PKG@.Gear.warnOnce("hcurve:" + bhv, "config.properties: base.hpCurve=" + bhv + " is not a list of level:factor points - the default " + HP_DEF + " is used"); bhv = HP_DEF; }
  BASE_HP = bhv;''')
rep('''  STEAL_S = (int) plong(p, "steal.windowS", 3L, 1L, 60L);''', '''  STEAL_S = (int) plong(p, "steal.windowS", 3L, 1L, 60L);
  STEAL_MAX = pdec(p, "steal.maxPerSec", @STEALDEF@, 0.0, 100.0);''')
rep('''  HIDE_BOX = pbool(p, "view.hideDamageBox", true);''', '''  HIDE_BOX = pbool(p, "view.hideDamageBox", true);
  // 0.2.5: the vanilla armor box (a restart row: GearABox reads it once at setup), Reforge level up
  HIDE_ABOX = pbool(p, "view.hideArmorBox", true);
  LVLUP_ON = pbool(p, "reforge.levelUp", true);
  LVLUP_CAP = (int) plong(p, "reforge.levelCap", @LVLCAPDEF@L, 0L, 50L);''')
rep('''  long[] xc = new long[nr];''', '''  long[] xc = new long[nr];
  long[] lub = new long[nr];
  long[] lup = new long[nr];''')
rep('''    xc[i] = xq == null ? DXPC[i] : (long) clampd(xq[0], 0.0, 100000.0);''', '''    xc[i] = xq == null ? DXPC[i] : (long) clampd(xq[0], 0.0, 100000.0);
    double[] cl = cells(p.getProperty("cost.levelUp." + rid), 2);
    if (cl == null) { lub[i] = DLU_BASE[i]; lup[i] = DLU_PER[i]; }
    else { lub[i] = (long) clampd(cl[0], 0.0, 1.0E12); lup[i] = (long) clampd(cl[1], 0.0, 1.0E12); }''')
rep('''  CR_BASE = crb; CR_PER = crp; CI_BASE = cib; CI_PER = cip; XPR = xp; XPC = xc;''',
    '''  CR_BASE = crb; CR_PER = crp; CI_BASE = cib; CI_PER = cip; XPR = xp; XPC = xc; LU_BASE = lub; LU_PER = lup;''')
rep('''}""".replace("@EXCLDEF@", jstr(EXCLUDE_DEF)).replace("@NAMESDEF@", jstr(REFORGE_NAMES_DEF)).replace("@BMATDEF@", repr(BASE_MAT_DEF))''',
    '''}""".replace("@EXCLDEF@", jstr(EXCLUDE_DEF)).replace("@NAMESDEF@", jstr(REFORGE_NAMES_DEF)).replace("@BMATDEF@", repr(BASE_MAT_DEF))
   .replace("@STEALDEF@", repr(float(STEAL_MAX_DEF))).replace("@LVLCAPDEF@", str(LVLUP_CAP_DEF))''')
rep('''M(gcf, "public static long xpReforge(int r) { return XPR[ri(r)]; }")''', '''M(gcf, "public static long xpReforge(int r) { return XPR[ri(r)]; }")
# 0.2.5: the coins of one Reforge level up to level lvl (the NEW level): base + per level x lvl
M(gcf, r"""
public static long costLevelUp(int r, int lvl) {
  int i = ri(r);
  long c = LU_BASE[i] + LU_PER[i] * (long) (lvl < 0 ? 0 : lvl);
  return c < 0L ? 0L : c;
}""")''')
rep('''  String w = "off".equals(BASE_MODE) ? "weapon damage vanilla (base.mode off)" : "weapon damage = vanilla step x K x F(level) x (1 + " + BASE_MAT + "% x band start), F = " + BASE_CURVE;
  String a = BASE_ARMOR ? "armor Health (F) + resistance (R = " + BASE_RES + ") per piece from its slot's Lv 1 values" : "armor values vanilla (base.armorOn off)";''',
    '''  String w = "off".equals(BASE_MODE) ? "weapon damage vanilla (base.mode off)" : "weapon damage = vanilla step x K x F(level) x (1 + " + BASE_MAT + "% x band start), F = " + BASE_CURVE + ", spell shots S = " + BASE_SPELL;
  String a = BASE_ARMOR ? "armor Health (H = " + BASE_HP + ") + resistance (R = " + BASE_RES + ") per piece from its slot's Lv 1 values" : "armor values vanilla (base.armorOn off)";''')

# ================================================================================================================ GearCfg.migrate025
rep('''# 0.2.1 ready line part: the base stats in force (live values)''', MIG_SRC + '''# 0.2.1 ready line part: the base stats in force (live values)''')
rep('''  @PKG@.GearCfg.migrate023();
  @PKG@.GearCfg.load();''', '''  @PKG@.GearCfg.migrate023();
  @PKG@.GearCfg.migrate025();
  @PKG@.GearCfg.load();''')

# ================================================================================================================ pairing STOP (spec 7.1)
rep('''HERE = os.path.dirname(os.path.abspath(__file__))''', '''HERE = os.path.dirname(os.path.abspath(__file__))
# 0.2.5 PAIRING (research/Mob-Curve-Spec.md 7.1, feasibility critic F3): SkyyGear 0.2.5 deploys and rolls back TOGETHER with SkyyMobs 0.1.4
# and SkyySkills 0.4.17 (steep gear vs linear mobs, or health-mode kill XP on the new mob health, otherwise). tools/deploy_set.py is only
# READ here (never run): the build stops when it pins this version without its partners. The main session adds the same STOP there.
_SETF = os.path.join(os.path.dirname(HERE), "tools", "deploy_set.py")
_dsx = open(_SETF, encoding="utf-8").read()
_sx0 = _dsx.index("SET = [")
_PINS25 = dict(re.findall(r'\\("(Skyy\\w+)", "([0-9][0-9.]*)"\\)', _dsx[_sx0:_dsx.index("\\n]\\n", _sx0)]))


def _vt25(x):
    return tuple(int(p) for p in x.split("."))


if _PINS25.get("SkyyGear") == VERSION and not (_vt25(_PINS25.get("SkyyMobs", "0")) >= (0, 1, 4) and _vt25(_PINS25.get("SkyySkills", "0")) >= (0, 4, 17)):
    raise SystemExit("STOP: SkyyGear %s is pinned in tools/deploy_set.py with SkyyMobs %s / SkyySkills %s - the mob curve round deploys and "
                     "rolls back TOGETHER (SkyyMobs 0.1.4+, SkyySkills 0.4.17+)" % (VERSION, _PINS25.get("SkyyMobs"), _PINS25.get("SkyySkills")))''')
assert "import re" in s or re.search(r"^import .*\bre\b", s, re.M), "the build imports re"

# ================================================================================================================ GearABox (new class)
rep('''gboxl = mk("GearBoxL")''', '''gboxl = mk("GearBoxL")
gabox = mk("GearABox")       # 0.2.5: the vanilla ARMOR box hidden per item type (SkyyGear keeps the maps and applies every armor stat itself)''')
rep('''CRIT_CLASSES = [gcrit, gcsy, gcsyU, gcln, gclnU, gctk, gbox, gboxl]''', '''CRIT_CLASSES = [gcrit, gcsy, gcsyU, gcln, gclnU, gctk, gbox, gboxl, gabox]''')
rep('''gboxl.addInterface(pool.get("java.util.function.Consumer"))''', ABOX_SRC + '''gboxl.addInterface(pool.get("java.util.function.Consumer"))''')
rep('''public void accept(Object e) {
  try { @PKG@.GearBox.onLoaded(e); }
  catch (Throwable t) { @PKG@.Gear.warnOnce("boxlistener", "Damage Data box listener failed (" + t + ") - reloaded weapons may show the vanilla box until a restart"); }
}''', '''public void accept(Object e) {
  try { @PKG@.GearBox.onLoaded(e); }
  catch (Throwable t) { @PKG@.Gear.warnOnce("boxlistener", "Damage Data box listener failed (" + t + ") - reloaded weapons may show the vanilla box until a restart"); }
  // 0.2.5: the armor box of reloaded gear armor types (their fresh ItemArmor maps are kept and swapped for empty ones again)
  try { @PKG@.GearABox.onLoaded(e); }
  catch (Throwable t2) { @PKG@.Gear.warnOnce("aboxlistener", "armor box listener failed (" + t2 + ") - reloaded gear armor may show the vanilla box until a restart"); }
}''')

# ================================================================================================================ GearBase: S + H curves
rep('''F(gbase, "public static volatile Object[] RP = null;")''', '''F(gbase, "public static volatile Object[] RP = null;")
# 0.2.5: the Spell curve S(L) (base.spellCurve) and the Armor Health curve H(L) (base.hpCurve), parsed once per text like F / R
F(gbase, "public static volatile String SSRC = null;")
F(gbase, "public static volatile Object[] SP = null;")
F(gbase, "public static volatile String HSRC = null;")
F(gbase, "public static volatile Object[] HP = null;")''')
rep('''  RSRC = null;
  RP = null;
}""")''', '''  RSRC = null;
  RP = null;
  SSRC = null;
  SP = null;
  HSRC = null;
  HP = null;
}""")''')
rep('''# F(L): weapon damage + armor Health; R(L): armor resistance (base.curve / base.resCurve, live: a new text is parsed on first use)''',
    '''M(gbase, r"""
public static synchronized Object[] reS(String s) {
  Object[] p = @PKG@.GearCfg.curvePts(s);
  if (p == null) p = @PKG@.GearCfg.curvePts(@PKG@.GearCfg.SPELL_DEF);
  SP = p;
  SSRC = s;
  return p;
}""")
M(gbase, r"""
public static synchronized Object[] reH(String s) {
  Object[] p = @PKG@.GearCfg.curvePts(s);
  if (p == null) p = @PKG@.GearCfg.curvePts(@PKG@.GearCfg.HP_DEF);
  HP = p;
  HSRC = s;
  return p;
}""")
# F(L): non-spell weapon damage (0.2.5: the steep Weapon curve); R(L): armor resistance (base.curve / base.resCurve, live: a new text is
# parsed on first use); 0.2.5 S(L): spell shots (base.spellCurve), H(L): armor Health (base.hpCurve)''')
rep('''public static double curveR(int lv) {
  String s = @PKG@.GearCfg.BASE_RES;
  Object[] p = RP;
  if (p == null || s != RSRC) p = reR(s);
  return eval(p, (double) lv);
}""")''', '''public static double curveR(int lv) {
  String s = @PKG@.GearCfg.BASE_RES;
  Object[] p = RP;
  if (p == null || s != RSRC) p = reR(s);
  return eval(p, (double) lv);
}""")
M(gbase, r"""
public static double curveS(int lv) {
  String s = @PKG@.GearCfg.BASE_SPELL;
  Object[] p = SP;
  if (p == null || s != SSRC) p = reS(s);
  return eval(p, (double) lv);
}""")
M(gbase, r"""
public static double curveH(int lv) {
  String s = @PKG@.GearCfg.BASE_HP;
  Object[] p = HP;
  if (p == null || s != HSRC) p = reH(s);
  return eval(p, (double) lv);
}""")''')
rep('''# spec 3.2: m = K x F(level) x (1 + base.matBonus % x band start) - the multiplier on the engine's own amount of every step
M(gbase, r"""
public static double mult(String id, @BD@ d, boolean spell) {
  int lv = @PKG@.GearLevel.level(id, d);
  int st = @PKG@.GearLevel.band(id)[0];
  return kOf(id, spell) * curveF(lv) * bonus(st);
}""")''', '''# spec 3.2: m = K x F(level) x (1 + base.matBonus % x band start) - the multiplier on the engine's own amount of every step. 0.2.5: a spell
# SHOT (K = 1) follows the Spell curve S (base.spellCurve = the old F); every other weapon hit the steep Weapon curve F (K stays on F)
M(gbase, r"""
public static double mult(String id, @BD@ d, boolean spell) {
  int lv = @PKG@.GearLevel.level(id, d);
  int st = @PKG@.GearLevel.band(id)[0];
  return kOf(id, spell) * (spell ? curveS(lv) : curveF(lv)) * bonus(st);
}""")''')
rep('''  double h = bh[si] * curveF(lv) * bonus(st);''', '''  double h = bh[si] * curveH(lv) * bonus(st);      // 0.2.5: the Armor Health curve H (base.hpCurve)''')
rep('''      return "base stats: Lv " + lv + " - Health " + @PKG@.Gear.fnum((double) tg[0]) + " (the item's own " + @PKG@.Gear.fnum((double) nativeHealth(it)) + "), resistance " + pct((double) tg[1]) + " physical / " + pct((double) tg[1]) + " projectile (the item's own " + pct((double) assetRes(it, "Physical")) + " / " + pct((double) assetRes(it, "Projectile")) + ")";''',
    '''      // 0.2.5: a hidden armor type's own numbers come from the maps GearABox keeps (the asset's are empty: the engine applies nothing)
      boolean hb = @PKG@.GearABox.hidden(id);
      double oh = hb ? (double) @PKG@.GearABox.snapHealth(id) : (double) nativeHealth(it);
      double op = hb ? (double) @PKG@.GearABox.snapRes(id, "Physical") : (double) assetRes(it, "Physical");
      double oj = hb ? (double) @PKG@.GearABox.snapRes(id, "Projectile") : (double) assetRes(it, "Projectile");
      return "base stats: Lv " + lv + " - Health " + @PKG@.Gear.fnum((double) tg[0]) + " (H " + f3(curveH(lv)) + "; the item's own " + @PKG@.Gear.fnum(oh) + "), resistance " + pct((double) tg[1]) + " physical / " + pct((double) tg[1]) + " projectile (the item's own " + pct(op) + " / " + pct(oj) + ")" + (hb ? "; vanilla armor box hidden - SkyyGear applies every stat of this piece" : "");''')

# ================================================================================================================ GearView: tooltip lines
rep('''    Object sm = a.getStatModifiers();
    if (sm instanceof java.util.Map) {
      java.util.Iterator e = ((java.util.Map) sm).entrySet().iterator();
      while (e.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e.next();
        Object k = en.getKey();
        Object v = en.getValue();
        if (!(k instanceof Number) || !(v instanceof Object[])) continue;''', '''    Object sm = @PKG@.GearABox.stats(id, a);      // 0.2.5: a hidden armor type's kept maps
    if (sm instanceof java.util.Map) {
      java.util.Iterator e = ((java.util.Map) sm).entrySet().iterator();
      while (e.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e.next();
        Object k = en.getKey();
        Object v = en.getValue();
        if (!(k instanceof Number) || !(v instanceof Object[])) continue;''')
rep('''    Object dr = a.getDamageResistanceValues();
    if (dr instanceof java.util.Map && !((java.util.Map) dr).isEmpty()) {''', '''    // 0.2.5: since 0.2 this part read the ResistanceModifier entries as StaticModifier, so it never showed (the vanilla box did); a HIDDEN
    // armor type has no box below any more, so its resistance line shows here from the kept map (FLAT = a number, else a %); other types
    // keep 0.2's lines exactly (none)
    boolean hidA = @PKG@.GearABox.hidden(id);
    Object dr = @PKG@.GearABox.res(id, a);
    if (hidA && dr instanceof java.util.Map && !((java.util.Map) dr).isEmpty()) {''')
rep('''        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @SMO@)) continue;
          @SMO@ m = (@SMO@) xs[i];
          if (m.getCalculationType() == @CAL@.MULTIPLICATIVE) mul = mul + (double) m.getAmount();
          else add = add + (double) m.getAmount();
        }
        String low = cause.toLowerCase();''', '''        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @RMOD@)) continue;
          @RMOD@ m = (@RMOD@) xs[i];
          if (m.getCalculationType() == @RCT@.FLAT) add = add + (double) m.getAmount();
          else mul = mul + (double) m.getAmount();
        }
        String low = cause.toLowerCase();''')
rep('''    java.util.ArrayList st = new java.util.ArrayList();
    int hi = @DST@.getHealth();
    Object sm = a.getStatModifiers();''', '''    java.util.ArrayList st = new java.util.ArrayList();
    int hi = @DST@.getHealth();
    boolean hid = @PKG@.GearABox.hidden(id);       // 0.2.5: the vanilla box is hidden - its flat Physical / Projectile parts show here too
    Object sm = @PKG@.GearABox.stats(id, a);''')
rep('''    Object dr = a.getDamageResistanceValues();
    if (dr instanceof java.util.Map) {
      java.util.Iterator e2 = ((java.util.Map) dr).entrySet().iterator();
      while (e2.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e2.next();
        Object k = en.getKey();
        Object v = en.getValue();
        String cause = k instanceof @DCS@ ? ((@DCS@) k).getId() : String.valueOf(k);
        if (cause == null || "Physical".equals(cause) || "Projectile".equals(cause) || !(v instanceof Object[])) continue;
        Object[] xs = (Object[]) v;
        double fl = 0.0;
        double pc = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @RMOD@)) continue;
          @RMOD@ r = (@RMOD@) xs[i];
          if (r.getCalculationType() == @RCT@.FLAT) fl = fl + (double) r.getAmount();
          else pc = pc + (double) r.getAmount();
        }''', '''    Object dr = @PKG@.GearABox.res(id, a);
    if (dr instanceof java.util.Map) {
      java.util.Iterator e2 = ((java.util.Map) dr).entrySet().iterator();
      while (e2.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e2.next();
        Object k = en.getKey();
        Object v = en.getValue();
        String cause = k instanceof @DCS@ ? ((@DCS@) k).getId() : String.valueOf(k);
        boolean pp = "Physical".equals(cause) || "Projectile".equals(cause);
        if (cause == null || (pp && !hid) || !(v instanceof Object[])) continue;
        Object[] xs = (Object[]) v;
        double fl = 0.0;
        double pc = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @RMOD@)) continue;
          @RMOD@ r = (@RMOD@) xs[i];
          if (r.getCalculationType() == @RCT@.FLAT) fl = fl + (double) r.getAmount();
          else pc = pc + (double) r.getAmount();
        }
        if (pp) pc = 0.0;                          // the levelled % is the line above''')
rep('''  float[] tg = @PKG@.GearBase.armorTarget(id, d);
  if (tg == null || @PKG@.GearBase.armorAsVanilla(id, d)) return false;''', '''  float[] tg = @PKG@.GearBase.armorTarget(id, d);
  // 0.2.5: a hidden armor type ALWAYS shows its levelled lines (no vanilla box under the tooltip any more)
  if (tg == null || (!@PKG@.GearABox.hidden(id) && @PKG@.GearBase.armorAsVanilla(id, d))) return false;''')

# ================================================================================================================ GearArmor: hidden types
rep('''  if (@PKG@.GearData.slotOf(id) != 2) return 0.0f;''', '''  if (@PKG@.GearData.slotOf(id) != 2) return 0.0f;
  if (@PKG@.GearABox.hidden(id)) return 0.0f;      // 0.2.5: a hidden armor type is added whole (GearArmor.lockSums / hiddenRes)''', 2)
rep('''  for (int i = 0; i < armor.getCapacity(); i++) {
    @IS@ s = armor.getItemStack((short) i);
    if (inactive(u, s)) { if (nat) addPiece(s, f, out, true); continue; }
    if (!lv) continue;''', '''  for (int i = 0; i < armor.getCapacity(); i++) {
    @IS@ s = armor.getItemStack((short) i);
    // 0.2.5: a gear armor TYPE whose vanilla box is hidden gives the engine nothing - SkyyGear adds ALL of it here (the want is signed:
    // negative = the lock modifier ADDS): an active piece its levelled Health (H) + every other stat of its kept maps (Health = the kept
    // value when levelling is off); an inactive piece nothing (level.armorNative) or its kept vanilla stats (armorNative off)
    if (s != null && !s.isEmpty() && @PKG@.GearABox.hidden(s.getItemId())) {
      boolean hb = false;
      try { hb = s.isBroken(); } catch (Throwable tb) { hb = false; }
      if (inactive(u, s)) { if (!nat) @PKG@.GearABox.addStats(s.getItemId(), f, hb, -1.0f, out); continue; }
      float th = -1.0f;
      if (lv) {
        float[] tg = @PKG@.GearBase.armorTarget(s.getItemId(), @PKG@.GearData.effective(s.getItemId(), s.getMetadata()));
        if (tg != null) th = tg[0];
      }
      @PKG@.GearABox.addStats(s.getItemId(), f, hb, th, out);
      continue;
    }
    if (inactive(u, s)) { if (nat) addPiece(s, f, out, true); continue; }
    if (!lv) continue;''')
rep('''public static boolean hasResDelta(java.util.UUID u, @IC@ armor) {
  if (armor == null || !@PKG@.GearBase.armorOn()) return false;''', '''public static boolean hasResDelta(java.util.UUID u, @IC@ armor) {
  if (armor == null) return false;
  if (@PKG@.GearABox.anyHidden(armor)) return true;     // 0.2.5: SkyyGear applies a hidden type's resistance itself
  if (!@PKG@.GearBase.armorOn()) return false;''')
rep('''# GearArmorSys (AFTER the engine's ArmorDamageReduction): cur = the engine's result with every worn piece at its ASSET values; full = our''',
    '''# 0.2.5: the resistance of the worn hidden armor types on top of the engine's map (their asset maps are empty): an active piece its
# levelled Physical / Projectile % (R; its kept % when levelling is off) + every other entry of its kept map (FLAT parts, Fire, Poison,
# Fall ..., BaseDamageResistance per entry like the engine); an inactive piece nothing (level.armorNative) or its kept entries (off); a
# broken piece's part x the engine's broken factor when penalties apply
M(garm, r"""
public static void hiddenRes(java.util.UUID u, @IC@ armor, java.util.Map m, boolean pen, @WLD@ w, boolean nat, boolean lv) {
  if (armor == null || m == null) return;
  float bf = -1.0f;
  for (int i = 0; i < armor.getCapacity(); i++) {
    @IS@ s = armor.getItemStack((short) i);
    if (s == null || s.isEmpty()) continue;
    String id = s.getItemId();
    if (!@PKG@.GearABox.hidden(id)) continue;
    boolean ina = inactive(u, s);
    if (ina && nat) continue;
    float tr = -1.0f;
    if (!ina && lv) {
      float[] tg = @PKG@.GearBase.armorTarget(id, @PKG@.GearData.effective(id, s.getMetadata()));
      if (tg != null) tr = tg[1];
    }
    float k = 1.0f;
    boolean br = false;
    try { br = s.isBroken(); } catch (Throwable t) { br = false; }
    if (pen && br) {
      if (bf < 0.0f) bf = resBroken(w);
      k = bf;
    }
    @PKG@.GearABox.addRes(id, m, tr, k);
  }
}""")
# GearArmorSys (AFTER the engine's ArmorDamageReduction): cur = the engine's result with every worn piece at its ASSET values; full = our''')
rep('''  boolean nat = @PKG@.GearCfg.ARMOR_NATIVE;
  boolean lv = @PKG@.GearBase.armorOn();
  if ((!nat && !lv) || full == null) return cur;
  float f = reduce(pre, cause, @ADRC@.getResistanceModifiers(w, full, pen, ecc));
  @IC@ src = nat ? (@IC@) activeCopy(vu, full) : full;
  java.util.Map am = @ADRC@.getResistanceModifiers(w, src, pen, ecc);
  if (lv) levelRes(vu, full, am, pen, w);''', '''  boolean nat = @PKG@.GearCfg.ARMOR_NATIVE;
  boolean lv = @PKG@.GearBase.armorOn();
  boolean hid = @PKG@.GearABox.anyHidden(full);
  if ((!nat && !lv && !hid) || full == null) return cur;
  float f = reduce(pre, cause, @ADRC@.getResistanceModifiers(w, full, pen, ecc));
  @IC@ src = nat ? (@IC@) activeCopy(vu, full) : full;
  java.util.Map am = @ADRC@.getResistanceModifiers(w, src, pen, ecc);
  if (lv) levelRes(vu, full, am, pen, w);
  if (hid) hiddenRes(vu, full, am, pen, w, nat, lv);''')

# ================================================================================================================ GearFx: Life Steal cap
rep('''# never above max, never on a dead player (Health <= 0)''', '''# 0.2.5 (research/Mob-Curve-Spec.md 2.5): one Life Steal payout is at most steal.maxPerSec % x max Health x steal.windowS (0 = no cap;
# an unknown max Health = no cap); the rest is dropped, never carried into the next window
M(gfx, r"""
public static double stealPay(double owed, double maxHp) {
  if (!(owed > 0.0)) return 0.0;
  double c = @PKG@.GearCfg.STEAL_MAX;
  if (!(c > 0.0) || !(maxHp > 0.0)) return owed;
  double cap = maxHp * c / 100.0 * (double) @PKG@.GearCfg.STEAL_S;
  return owed > cap ? cap : owed;
}""")
# never above max, never on a dead player (Health <= 0)''')
rep('''    if (!dead) add(m, @DST@.getHealth(), (float) lv[0], true);''', '''    if (!dead) {
      @ESV@ hv = m.get(@DST@.getHealth());
      double pay = stealPay(lv[0], hv == null ? 0.0 : (double) hv.getMax());
      if (pay > 0.0) add(m, @DST@.getHealth(), (float) pay, true);
    }''')
# GearFx.setup: the ordered flags the armor box needs
rep('''  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearHitSys(true)); }
  catch (Throwable t1) {''', '''  boolean hitOrd = false;
  boolean armOrd = false;
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearHitSys(true)); hitOrd = adr != null; }
  catch (Throwable t1) {''')
rep('''  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearArmorSys(true)); }
  catch (Throwable t2) {''', '''  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearArmorSys(true)); armOrd = adr != null; }
  catch (Throwable t2) {''')
rep('''  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearTrueSys(true)); }''', '''  // 0.2.5: the vanilla armor box is only hidden when SkyyGear's corrected armor pass runs in order (it applies those pieces' resistance)
  @PKG@.GearABox.ORDERED = hitOrd && armOrd;
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearTrueSys(true)); }''')

# ================================================================================================================ GearRoll: level up document
rep('''# spec 5.7: identify rolls the modifiers for the item's rarity (PART B's page and the admin /gear identify call it)''', '''# 0.2.5 REFORGE LEVEL UP: the level the item was made / found at = "lvl0" (written once, at its first level up: its level then), else the
# level it reads now
M(grl, r"""
public static int origin(String id, @BD@ d) {
  try {
    @BV@ v = d == null ? null : d.get("lvl0");
    if (v != null && v.isNumber()) return @PKG@.GearLevel.clamp(v.asNumber().intValue());
  } catch (Throwable t) { }
  return @PKG@.GearLevel.level(id, d);
}""")
# one level up: lvl0 kept (or written now), lvl = next, lvU + 1; rarity, modifiers, reforge name, id and src never change; unknown fields kept
M(grl, r"""
public static @BD@ levelUp(String id, @BD@ doc, int next) {
  @BD@ d = doc.clone();
  int o = origin(id, d);
  stampIfMissing(id, d);
  @BV@ v0 = d.get("lvl0");
  if (v0 == null || !v0.isNumber()) d.put("lvl0", new org.bson.BsonInt32(o));
  d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(next)));
  d.put("lvU", new org.bson.BsonInt32(@PKG@.GearData.num(d, "lvU", 0) + 1));
  d.put("at", new org.bson.BsonInt64(System.currentTimeMillis()));
  return d;
}""")
# spec 5.7: identify rolls the modifiers for the item's rarity (PART B's page and the admin /gear identify call it)''')

# ================================================================================================================ GearForge: level up core
rep('''# ================================================================= GearFn: bridge functions (spec 7.1). Never throw, never touch ECS.''',
    LVL_SRC + '''# ================================================================= GearFn: bridge functions (spec 7.1). Never throw, never touch ECS.''')

# ================================================================================================================ ReforgePage
rep('''    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow2 { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");''',
    '''    // 0.2.5: the level up rule in one line
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow3 { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow3.Text", @PKG@.GearCfg.LVLUP_ON ? "Level up: +1 level for coins, at most +" + @PKG@.GearCfg.LVLUP_CAP + " over the level it was made or found at." : "Level up is off on this server.");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow2 { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");''')
rep('''  String bt = why != null ? (d != null && !@PKG@.GearData.identified(d) ? "Identify it first" : "Cannot reforge") : (poor ? "Not enough coins" : "Reforge");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "Label { Anchor: (Width: 111, Height: 44); Text: \\"\\"; }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnForge { Anchor: (Width: 340, Height: 44); Text: \\"" + @PKG@.Gear.safe(bt) + "\\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnForge", @EVD@.of("a", "forge"));''', '''  String bt = why != null ? (d != null && !@PKG@.GearData.identified(d) ? "Identify it first" : "Cannot reforge") : (poor ? "Not enough coins" : "Reforge");
  // 0.2.5 REFORGE LEVEL UP (Skyy LOCKED 2026-10-04): one line (the next level + its coins, or why not) and a second button
  Object[] li = null;
  if (d != null) li = @PKG@.GearForge.lvlInfo(u, id, d);
  int lc = li == null ? 7 : ((Integer) li[0]).intValue();
  int lnext = li == null ? lvl + 1 : ((Integer) li[2]).intValue();
  long lcost = @PKG@.GearCfg.costLevelUp(r, lnext);
  boolean lpoor = lc == 0 && lcost > 0L && have >= 0L && have < lcost;
  boolean loff = why != null || lc != 0 || lpoor;
  String lt;
  if (!@PKG@.GearCfg.LVLUP_ON) lt = "Level up: off on this server.";
  else if (why != null) lt = d != null && !@PKG@.GearData.identified(d) ? "Level up: identify it first." : "Level up: not for this item.";
  else if (lc == 0) lt = "Level up to Lv " + lnext + ": " + (lcost > 0L ? @PKG@.Gear.fmt(lcost) + " coins" : "free") + " (it can reach Lv " + li[3] + ")";
  else lt = "Level up: " + (String) li[5];
  b.appendInline("#SkyyGAnvil", "Label #SkyyGLvlTxt { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (lc == 0 && !lpoor && why == null ? "#E8A93B" : "#96a9be") + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGLvlTxt.Text", lt);
  String lb = (!@PKG@.GearCfg.LVLUP_ON || why != null) ? "Cannot level up" : (lc == 0 ? (lpoor ? "Not enough coins" : "Level up") : ((lc == 3 || lc == 4) ? "Max level" : "Cannot level up"));
  b.appendInline("#SkyyGAnvil", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnForge { Anchor: (Width: 270, Height: 44); Text: \\"" + @PKG@.Gear.safe(bt) + "\\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  b.appendInline("#SkyyGGo", "Label { Anchor: (Width: 22, Height: 44); Text: \\"\\"; }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnLevel { Anchor: (Width: 270, Height: 44); Text: \\"" + @PKG@.Gear.safe(lb) + "\\"; " + @PKG@.GearUi.btn(loff ? 3 : 1) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnForge", @EVD@.of("a", "forge"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnLevel", @EVD@.of("a", "lvl"));''')
rep('''  b.set("#SkyyGSub.Text", "Pick a weapon or armor piece. A reforge re-rolls its modifiers for coins - the rarity never changes.");''',
    '''  b.set("#SkyyGSub.Text", "Pick a weapon or armor piece. Reforge re-rolls its modifiers, Level up raises it one level - both for coins.");''')
rep('''M(rpg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''', '''# 0.2.5 the level up click: the forge() guards (double click, profile:busy, selection, epoch) -> GearForge.levelUp (same item, refusals, coins
# first, refund); the Before / After columns show the item at both levels
M(rpg, r"""
public void lvlUp(@INV@ inv) {
  long now = System.currentTimeMillis();
  if (now - this.lastForge < 400L) return;
  this.lastForge = now;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was levelled up. Try again in a moment."; return; }
  if (this.selSec < 0) { this.info = "-Pick an item from Your gear first."; return; }
  String ep = @PKG@.Gear.epoch(u);
  if (!ep.equals(this.epoch)) { clearSel(); this.epoch = ep; this.info = "-Your profile changed - pick the item again."; return; }
  @IC@ c = @PKG@.GearStamp.section(inv, this.selSec);
  String name = @PKG@.Gear.itemName(this.selId);
  Object[] res = @PKG@.GearForge.levelUp(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
  int code = ((Integer) res[0]).intValue();
  if (code == 1) {
    this.selFp = @PKG@.GearForge.fp((@IS@) res[2]);
    this.before = (@BD@) res[3];
    this.after = (@BD@) res[4];
    this.fresh = true;
    long cost = ((Long) res[5]).longValue();
    this.info = "+Levelled up! Your " + name + " is now Lv " + @PKG@.GearLevel.level(this.selId, this.after) + (cost > 0L ? " (-" + @PKG@.Gear.fmt(cost) + " coins)." : ".");
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("That item moved")) clearSel();
  this.info = "-" + msg;
}""")
M(rpg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''')
rep('''    if (a.equals("forge")) { forge(inv); rebuild(); return; }''', '''    if (a.equals("forge")) { forge(inv); rebuild(); return; }
    if (a.equals("lvl")) { lvlUp(inv); rebuild(); return; }''')

# ================================================================================================================ GearFn: gear:fn:curve
rep('''M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;''', '''# 0.2.5 gear:fn:curve (research/Mob-Curve-Spec.md 7.3): Object[] { String which ("F" | "S" | "H" | "R", any case), Number level } -> Double
# (the live curve at that level: F = Weapon curve, S = Spell curve, H = Armor Health curve, R = resistance curve) or null; never throws
M(gfn, r"""
public static Object curve(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof String) || !(a[1] instanceof Number)) return null;
    String w = ((String) a[0]).trim().toUpperCase();
    int lv = ((Number) a[1]).intValue();
    double v = 0.0;
    if (w.equals("F")) v = @PKG@.GearBase.curveF(lv);
    else if (w.equals("S")) v = @PKG@.GearBase.curveS(lv);
    else if (w.equals("H")) v = @PKG@.GearBase.curveH(lv);
    else if (w.equals("R")) v = @PKG@.GearBase.curveR(lv);
    else return null;
    if (Double.isNaN(v) || Double.isInfinite(v)) return null;
    return Double.valueOf(v);
  } catch (Throwable t) { return null; }
}""")
M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;
    if (m == 10) return curve(o);''')
rep('''    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid")))''',
    '''    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid", "curve")))''')

# ================================================================================================================ plugin wiring
rep('''  @PKG@.GearBox.ON = @PKG@.GearCfg.HIDE_BOX;''', '''  @PKG@.GearBox.ON = @PKG@.GearCfg.HIDE_BOX;
  // 0.2.5: the vanilla ARMOR box (view.hideArmorBox, restart row: read once here; GearFx.setup below sets GearABox.ORDERED)
  @PKG@.GearABox.ON = @PKG@.GearCfg.HIDE_ABOX;''')
rep('''  try { @PKG@.Gear.info(@PKG@.GearBox.start()); } catch (Throwable t) { @PKG@.Gear.warn("the vanilla Damage Data box could not be hidden (" + t + ") - gear weapons keep it"); }''',
    '''  try { @PKG@.Gear.info(@PKG@.GearBox.start()); } catch (Throwable t) { @PKG@.Gear.warn("the vanilla Damage Data box could not be hidden (" + t + ") - gear weapons keep it"); }
  try { @PKG@.Gear.info(@PKG@.GearABox.start()); } catch (Throwable ta) { @PKG@.Gear.warn("the vanilla armor box could not be hidden (" + ta + ") - gear armor keeps it"); }''')
rep('''+ @PKG@.GearBox.readyText() + "; wand / staff tooltips''', '''+ @PKG@.GearBox.readyText() + "; " + @PKG@.GearABox.readyText() + "; Reforge level up " + (@PKG@.GearCfg.LVLUP_ON ? "on (at most +" + @PKG@.GearCfg.LVLUP_CAP + " levels)" : "off") + "; Life Steal at most " + @PKG@.GearCfg.STEAL_MAX + "% of max Health per second; gear:fn:curve; wand / staff tooltips''')
rep('''SkyBlock-style tooltips (wands / staffs show their charged + quick shots, the vanilla Damage Data box is hidden); crits show a CRIT! popup and vanilla crit sparks; Server Setup -> Gear. Replaces SkyyRolls. Zero dependencies."''',
    '''SkyBlock-style tooltips (wands / staffs show their charged + quick shots, the vanilla Damage Data and armor boxes are hidden - SkyyGear applies the armor stats); weapons and armor Health follow steep level curves after Lv 20 (spells keep their own), made for SkyyMobs' mob curve; Reforge also levels an item up for coins; Life Steal is capped; crits show a CRIT! popup and vanilla crit sparks; Server Setup -> Gear. Replaces SkyyRolls. No hard dependencies (deploy with SkyyMobs 0.1.4 + SkyySkills 0.4.17)."''')

# ================================================================================================================ write
assert s.count("registerSystem(") == SYS0 and s.count("registerCommand(") == CMD0, "0.2.5 adds no system / command"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))
