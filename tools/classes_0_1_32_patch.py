"""Derive SkyyClasses/build_skyyclasses_0.1.32.py from the GENERATED SkyyClasses 0.1.31 (build_skyyclasses_0.1.31.py, built + reviewed in round
armory0129; deploys right before this one; the EDITED lineage: Skyy's hand-edited 0.1.6 (commit ab75b6c) -> classes_0_1_7_patch.py -> ... ->
classes_0_1_31_patch.py -> 0.1.31). Never re-run an older patch, never edit a generated script - edit this patch. Every anchor is asserted;
at the end every change is undone on a copy and compared with 0.1.31 (nothing else changed). Line endings kept.
Run:  python tools/classes_0_1_32_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.32.py   (never --deploy)

0.1.32 (2026-10-16, round sb01) = ARCANE BREACH IS A VISIBLE ARC OF LIGHT + PER-ABILITY COOLDOWNS + THE STACKS BRIDGE.
  Skyy 2026-10-16 (docs/answered/classes.md 'ARCANE BREACH = A VISIBLE ARC OF LIGHT, 5 s COOLDOWN'): "and for the arcane breach ability, when
  play testing it was so fast i had trouble telling what was actually happening.    i want it fully animated. so the player swings the sword
  horizontally in a big slash. and it shoots a big arc of light right where your looking that hurts every enemy it hits and knocks them back.
  (the ark of light should move slightly faster than a quickshot. slow enough to see, but fast enough to aim well.    and well need to adjust
  the cooldown per ability. i felt like 30 seconds was way to long for what the ability actually did. for that one lets go like 5"
  + "make it start at 1.4x damage and scale with level." + "and make it reach 6.5 blocks. so its a little further than normal reach."
  + "and add a stack widget. so any class that uses stacks, you can see your stacks." (SkyyHud draws it; this jar publishes the data).
  1. ARCANE BREACH (walking + sprinting shapes; Breach from Above and Marked Ground stay as they were): the cast plays the vanilla longsword's
     big horizontal charged slash (Server/Item/Animations/Longsword.json "SwingLeftCharged", checked against Assets.zip) and launches a
     crescent of light (vanilla one-shot particles, nothing committed) from chest height along the look direction (pitch clamped to 30
     degrees): ab.ArcaneBreach.numbers speed=15 blocks a second (a shortbow quick shot = Projectile_Config_Arrow_Shortbow_Strength_0
     LaunchForce 12, read from Assets.zip by the build), range=6.5 (was the 5-block arc radius), width=8 (about the old 180-degree 5-block
     arc), knock=2 blocks (away along the flight). Every enemy the crescent passes is hit ONCE: power=1.4 (was 1.2) x one hit x the ability
     level multiplier (cxm(), as every ability) + Breach (the same rules: base + Momentum stacks + levels, capped) + knockback (+ the Imbue
     status when imbued); a wall (the block at the crescent's centre and the one under it both solid) stops it. At the end: +gain Momentum
     and one counted use when anything was hit; the Chain modifier jumps from where it ended; Burning Rift's patches as before.
     The 'angle' key is gone (the arc is a flight now); a file still holding it is fine (an unknown key is ignored).
  2. COOLDOWNS: every ability already has its own Server Setup cooldown (Mage / Priest: ab.<A>.<shape>.cooldown rows; Monk / Assassin:
     ab.<A>.walk.cooldown; Warrior / Berserker / Archer / Spellblade: the cooldown key of ab.<A>.numbers; Guardian Spirit: its save
     cooldown row) - the build now asserts it. Arcane Breach cooldown=5 (was 16; the shapes keep their plan offsets: sprint 5, air 7,
     crouch 5). ONE-TIME UPDATE ClassCfg.migrate0132 (the migrate0110 / 0129 machinery): an ab.ArcaneBreach.numbers line still holding
     EXACTLY the 0.1.31 default text becomes the 0.1.32 default (History version first, verified; one config-changes.log line Server Setup
     -> Changes can Undo; marker comment; byte / line endings kept); a hand-edited line is kept (+ an INFO note).
  3. NEW read-only bridge key class:fn:stacks (SkyyHud's stack widget): apply(Object[]{UUID}) -> String[] rows "name|current|max|secondsLeft|
     colorHex" for the stack resources the player's class has right now: Spellblade "Momentum" (always) + "Rolling" / "Unstoppable" (a
     state row while it holds; secondsLeft = until it drops), Monk "Combo" / "Hundred Fists" (while the aura runs), Berserker "Blood
     Frenzy" (while the toggle is on); secondsLeft = until the next stack falls off. Empty array = none; null = the player is not online.
     A snapshot of the in-memory maps (no world calls), cheap enough for a 250 ms poll. Archer Marks / Assassin poison sit on ENEMIES (not
     the player's own stacks) - not listed.
  Every existing bridge key + its arguments unchanged; no command changes; no saved player data changes.
  ROLLBACK to 0.1.31: config.properties keeps the 0.1.32 ab.ArcaneBreach.numbers text (0.1.31 reads range 6.5 / power 1.4 / cooldown 5 as its
  arc's numbers, ignores speed / width / knock; no angle key = its 90-degree default) - Undo in Server Setup -> Changes restores the old text.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.31.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.32.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.31"' in s and s.startswith('"""SkyyClasses 0.1.31 - build script') and "class:fn:stacks" not in s, "not the generated 0.1.31 script"
REG0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_first = s.split(LF)[0]
rep(_first + LF, '''"""SkyyClasses 0.1.32 - build script (javassist via jpype). GENERATED by tools/classes_0_1_32_patch.py from the generated 0.1.31 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_32_patch.py) - edit the patch, not this file.
0.1.32 = Arcane Breach is a visible arc of light (a flying crescent, 5 s cooldown, 1.4x), class:fn:stacks (notes: tools/classes_0_1_32_patch.py).

''' + _first.replace('"""', '', 1) + LF)
rep('VERSION = "0.1.31"', 'VERSION = "0.1.32"')

# ================================================================================================ 1. the numbers row
rep('''_n("ab.ArcaneBreach.cooldown", "AB_CD", "dec", 16.0, "0", "600", "", "abilsb", "cooldown", "cooldown")
_n("ab.ArcaneBreach.range", "AB_RANGE", "dec", 5.0, "0", "10000", "", "abilsb", "range", "range")
_n("ab.ArcaneBreach.angle", "AB_ANGLE", "dec", 90.0, "0", "10000", "", "abilsb", "angle", "angle")
_n("ab.ArcaneBreach.power", "AB_POWER", "dec", 1.2, "0", "10000", "", "abilsb", "power", "power")''',
    '''_n("ab.ArcaneBreach.cooldown", "AB_CD", "dec", 5.0, "0", "600", "", "abilsb", "cooldown", "cooldown")          # 0.1.32: 16 -> 5 (Skyy 2026-10-16)
_n("ab.ArcaneBreach.range", "AB_RANGE", "dec", 6.5, "0.5", "20", "", "abilsb", "range", "range")          # 0.1.32: the crescent's flight (was the 5-block arc)
_n("ab.ArcaneBreach.speed", "AB_SPEED", "dec", 15.0, "5", "40", "", "abilsb", "speed", "speed")          # 0.1.32: blocks a second (a quick shot = 12)
_n("ab.ArcaneBreach.width", "AB_WIDTH", "dec", 8.0, "0.5", "12", "", "abilsb", "width", "width")          # 0.1.32: the crescent's width (blocks)
_n("ab.ArcaneBreach.knock", "AB_KNOCK", "dec", 2.0, "0", "10000", "", "abilsb", "knock", "knock")          # 0.1.32: knockback (blocks)
_n("ab.ArcaneBreach.power", "AB_POWER", "dec", 1.4, "0", "10000", "", "abilsb", "power", "power")          # 0.1.32: 1.2 -> 1.4 (Skyy 2026-10-16)''')

# the quick-shot speed + the swing animation, read from the release Assets.zip (read-only) by the build
rep('''# 0.1.23 shared
_r("abil.pushPerBlock",''', '''# 0.1.32 (Skyy 2026-10-16): the arc of light flies "slightly faster than a quickshot" - the shortbow's quick shot (a tap = Strength_0)
with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as _az32:          # read-only
    _qs = json.loads(_az32.read("Server/ProjectileConfigs/Weapons/Shortbow/Projectile_Config_Arrow_Shortbow_Strength_0.json").decode("utf-8-sig"))
    _qi = json.loads(_az32.read("Server/Item/Interactions/Weapons/Shortbow/Primary/Shoot/Weapon_Shortbow_Primary_Shoot_Strength_0.json").decode("utf-8-sig"))
    _lsa = json.loads(_az32.read("Server/Item/Animations/Longsword.json").decode("utf-8-sig"))["Animations"]
QUICK_SHOT_SPEED = float(_qs["LaunchForce"])
assert _qi["Config"] == "Projectile_Config_Arrow_Shortbow_Strength_0" and 8.0 <= QUICK_SHOT_SPEED <= 40.0, "the vanilla quick shot moved: %s" % QUICK_SHOT_SPEED
_AB_SPEED = [_r_[3] for _r_ in NUM_ROWS if _r_[0] == "ab.ArcaneBreach.speed"][0]
assert QUICK_SHOT_SPEED < _AB_SPEED <= QUICK_SHOT_SPEED * 1.5, "0.1.32: the arc flies slightly faster than a quick shot (%s / %s)" % (_AB_SPEED, QUICK_SHOT_SPEED)
ARC_ANIM_SET, ARC_ANIM = "Longsword", "SwingLeftCharged"          # the big horizontal charged slash (third + first person)
assert ARC_ANIM in _lsa and _lsa[ARC_ANIM].get("FirstPerson") and _lsa[ARC_ANIM].get("ThirdPerson") and "Swing_Left" in _lsa[ARC_ANIM]["ThirdPerson"], \\
    "0.1.32: the vanilla longsword horizontal slash animation moved"
print("0.1.32: Arcane Breach flies %s blocks a second (a quick shot %s), the %s/%s slash" % (_AB_SPEED, QUICK_SHOT_SPEED, ARC_ANIM_SET, ARC_ANIM))
# 0.1.32 (Skyy 2026-10-16 "we'll need to adjust the cooldown per ability"): every ability has its OWN cooldown in Server Setup
_cd_rows = set(_r_[0] for _r_ in ABIL_ROWS)
_cd_missing = [a[0] for a in ABILS if not ("ab.%s.walk.cooldown" % a[0] in _cd_rows or "ab.%s.cooldown" % a[0] in _cd_rows
                                            or ("cooldown=" in NUM_TEXT.get(a[0], "") and ("," + NUM_TEXT[a[0]]).count(",cooldown=") == 1))]
assert not _cd_missing, "0.1.32: abilities without their own cooldown row: %s" % _cd_missing
print("0.1.32: all %d abilities have their own cooldown row (rows %d, numbers keys %d)" % (len(ABILS), sum(1 for a in ABILS if "ab.%s.walk.cooldown" % a[0] in _cd_rows
      or "ab.%s.cooldown" % a[0] in _cd_rows), sum(1 for a in ABILS if "cooldown=" in NUM_TEXT.get(a[0], ""))))
# 0.1.32 ONE-TIME UPDATE (ClassCfg.migrate0132, the migrate0110 / 0129 machinery): an ab.ArcaneBreach.numbers line still holding EXACTLY the
# 0.1.31 default -> the 0.1.32 default (cooldown 5, range 6.5, power 1.4, + speed / width / knock, no angle); a hand-edited line is kept
MG32_OLD_TEXT = ("mana=8,stamina=1,cooldown=16,range=5,angle=90,power=1.2,breach=15,time=8,perStack=1,stackCap=10,perLevel=0.5,cap=30,step=2,"
                 "sprintTime=7,airRadius=4,airPower=1,airUp=1.5,markRadius=3.5,markBreach=20,gain=3,chainRange=6,durMax=2")
MG32_DEFAULTS = [("ab.ArcaneBreach.numbers", MG32_OLD_TEXT, NUM_TEXT["ArcaneBreach"],
                  "Arcane Breach flies a crescent of light: cooldown 5 s, 6.5 blocks, 1.4x one hit")]
assert NUM_TEXT["ArcaneBreach"] == MG32_OLD_TEXT.replace("cooldown=16,range=5,angle=90,power=1.2,", "cooldown=5,range=6.5,speed=15,width=8,knock=2,power=1.4,"), \\
    "0.1.32: the new default = the old one with exactly the planned keys changed: %s" % NUM_TEXT["ArcaneBreach"]
MG32_MARK_ID = "SkyyClasses 0.1.32 defaults"
MG32_MARK = ("# %s (Skyy 2026-10-16): Arcane Breach flies a crescent of light 6.5 blocks at 15 a second, 1.4x one hit, cooldown 5 s "
             "(ab.ArcaneBreach.numbers)" % MG32_MARK_ID)
MG32_WHO = "SkyyClasses 0.1.32"
assert all(32 <= ord(_c) < 127 for _c in MG32_MARK + "".join("".join(_t) for _t in MG32_DEFAULTS)), "the update texts must be plain ASCII"
assert "=" not in MG32_MARK and MG32_MARK.startswith("# ") and MG32_MARK_ID in MG32_MARK, "the marker must be a doc comment"
assert MG_MARK_ID not in MG32_MARK and MG29_MARK_ID not in MG32_MARK and MG32_MARK_ID not in MG_MARK + MG29_MARK, "the update markers must not find each other"
# 0.1.23 shared
_r("abil.pushPerBlock",''')

# the default file: the marker right above the row (a fresh file is never rewritten by the update)
rep('''] + ["%s=%s" % (_r[0], abil_text(_r[3])) for _r in ABIL_ROWS]''',
    '''] + [_l for _r in ABIL_ROWS for _l in (([MG32_MARK] if _r[0] == "ab.ArcaneBreach.numbers" else []) + ["%s=%s" % (_r[0], abil_text(_r[3]))])]   # 0.1.32: + the marker
assert sum(1 for _l in ABIL_LINES if _l == MG32_MARK) == 1 and ABIL_LINES[ABIL_LINES.index(MG32_MARK) + 1].startswith("ab.ArcaneBreach.numbers="), "0.1.32: the marker"''')

# what it does (class:fn:abilDoes) + the one-line description
rep('''    "ArcaneBreach": "A {AB_ANGLE*2}-degree arc {AB_RANGE} blocks in front: {AB_POWER}x one hit and Breach - they take {AB_BREACH} % more from everyone for {AB_TIME} s (+{AB_PERSTACK} % per Momentum, +{AB_PERLEVEL} % a level, at most {AB_CAP} %). +{AB_GAIN} Momentum.",''',
    '''    "ArcaneBreach": "A slash sends a crescent of light {AB_RANGE} blocks where you look (stops at walls): each enemy it passes takes {AB_POWER}x one hit, is knocked back and Breached - +{AB_BREACH} % damage from everyone for {AB_TIME} s (+{AB_PERSTACK} % per Momentum, +{AB_PERLEVEL} % a level, max {AB_CAP} %). +{AB_GAIN} Momentum.",''')
rep("""'ArcaneBreach': 'Walk - a wide arc: enemies take more from everyone (Breach). Sprint - step in. Air - on landing. Crouch - Marked Ground.'""",
    """'ArcaneBreach': 'Walk - a crescent of light flies where you look (Breach, knockback). Sprint - step in. Air - on landing. Crouch - Marked Ground.'""")

# ================================================================================================ the engine members (probed)
rep('''    "MES":  "com.hypixel.hytale.server.npc.role.support.MarkedEntitySupport",   # 0.1.23: an NPC's targets (Awe, the cloak, the smoke)
''', '''    "MES":  "com.hypixel.hytale.server.npc.role.support.MarkedEntitySupport",   # 0.1.23: an NPC's targets (Awe, the cloak, the smoke)
    # 0.1.32: the Arcane Breach swing (AnimationUtils) + the wall check (the SkyyArmory WorldGrid block read: never loads a chunk)
    "ANU":  "com.hypixel.hytale.server.core.entity.AnimationUtils",
    "ASL":  "com.hypixel.hytale.protocol.AnimationSlot",
    "CHS":  "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BSC":  "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
    "BTY":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BMAT": "com.hypixel.hytale.protocol.BlockMaterial",
''')
rep('''B.probe(pool, T["ST"], "getExternalData")
''', '''B.probe(pool, T["ST"], "getExternalData")
# 0.1.32: the Arcane Breach swing + the wall check - every member with the descriptor the code calls
for c, m, d in ((T["ANU"], "playAnimation", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/protocol/AnimationSlot;Ljava/lang/String;Ljava/lang/String;ZLcom/hypixel/hytale/component/ComponentAccessor;)V"),
                (T["WLD"], "getChunkStore", "()Lcom/hypixel/hytale/server/core/universe/world/storage/ChunkStore;"),
                (T["CHS"], "getChunkSectionReferenceAtBlock", "(III)Lcom/hypixel/hytale/component/Ref;"),
                (T["CHS"], "getStore", "()Lcom/hypixel/hytale/component/Store;"),
                (T["BSC"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"), (T["BSC"], "get", "(III)I"),
                (T["BTY"], "getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/BlockTypeAssetMap;"),
                (T["BTY"], "getMaterial", "()Lcom/hypixel/hytale/protocol/BlockMaterial;"),
                ("com.hypixel.hytale.assetstore.map.BlockTypeAssetMap", "getAsset", "(I)Lcom/hypixel/hytale/assetstore/map/JsonAssetWithMap;"),
                (T["ST"], "getComponent", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/ComponentType;)Lcom/hypixel/hytale/component/Component;")):
    assert str(pool.get(c).getMethod(m, d).getName()) == m, "0.1.32: %s.%s%s" % (c, m, d)
for c, f in ((T["ASL"], "Action"), (T["BMAT"], "Solid"), (T["BTY"], "EMPTY_ID")):
    B.probe(pool, c, f)
assert int(pool.get(T["BTY"]).getField("EMPTY_ID").getConstantValue()) == 0, "0.1.32: BlockType.EMPTY_ID is not 0"
''')
rep('''      "FX_NET": "Block_Hit_Dust", "FX_RAGE": "Impact_Sword_Charged", "FX_FIRE": "Impact_Fire"}''',
    '''      "FX_NET": "Block_Hit_Dust", "FX_RAGE": "Impact_Sword_Charged", "FX_FIRE": "Impact_Fire",
      # 0.1.32: the Arcane Breach crescent of light (white-gold blade trail at the centre, bright slashes on the wings), its hits, a wall
      "FX_ARC": "Sword_Charged_Trail_Blade", "FX_ARC_WING": "Mace_Signature_Slash", "FX_ARC_HIT": "Impact_Sword_Charged", "FX_ARC_WALL": "Impact_Sword_Signature"}''')

# ================================================================================================ the Abil seams / counters
rep('''           "public static volatile java.util.function.Function LOOK = null;",    # 0.1.18 HARNESS SEAM ONLY (null = TargetUtil.getLook): Ref -> double[6]
''', '''           "public static volatile java.util.function.Function LOOK = null;",    # 0.1.18 HARNESS SEAM ONLY (null = TargetUtil.getLook): Ref -> double[6]
           "public static volatile java.util.function.Function SOLID = null;",   # 0.1.32 HARNESS SEAM ONLY (null = the world's blocks): double[3] -> Boolean
           "public static volatile java.util.List ANIMS = null;",                # 0.1.32 HARNESS SEAM ONLY (null): every animation played
           "public static volatile String SOLID_FAIL = null;",                   # 0.1.32: the first failed block read (said once)
           "public static volatile long ARCS = 0L;", "public static volatile long ARC_WALLS = 0L;", "public static volatile long ARC_HITS = 0L;",   # 0.1.32
           "public static final String ARC_ANIM_SET = %s;" % jstr(ARC_ANIM_SET), "public static final String ARC_ANIM = %s;" % jstr(ARC_ANIM),   # 0.1.32
''')

# ================================================================================================ the flight
ARC_JAVA = r'''r"""
public static int arcSolid(@CAC@ acc, double x, double y, double z) {
  java.util.function.Function f = SOLID;
  if (f != null) return Boolean.TRUE.equals(f.apply(new double[] { x, y, z })) ? 1 : 0;
  try {
    @WLD@ w = worldOf(acc);
    if (w == null) return -1;
    @CHS@ cs = w.getChunkStore();
    if (cs == null) return -1;
    @ST@ cst = cs.getStore();
    if (cst == null) return -1;
    int bx = (int) Math.floor(x);
    int by = (int) Math.floor(y);
    int bz = (int) Math.floor(z);
    @REF@ sr = cs.getChunkSectionReferenceAtBlock(bx, by, bz);
    if (sr == null || !sr.isValid()) return -1;
    @BSC@ sec = (@BSC@) cst.getComponent(sr, @BSC@.getComponentType());
    if (sec == null) return -1;
    int id = sec.get(bx, by, bz);
    if (id == @BTY@.EMPTY_ID) return 0;
    Object o = @BTY@.getAssetMap().getAsset(id);
    if (!(o instanceof @BTY@)) return 1;
    return ((@BTY@) o).getMaterial() == @BMAT@.Solid ? 1 : 0;
  } catch (Throwable t) {
    if (SOLID_FAIL == null) { SOLID_FAIL = String.valueOf(t); @PKG@.ClassCfg.warnLimited("Arcane Breach could not read a block (" + t + ") - the arc flies through walls"); }
    return -1;
  }
}
""",
r"""
public static void arcAnim(@CAC@ acc, @REF@ r) {
  java.util.List l = ANIMS;
  if (l != null) { l.add(ARC_ANIM_SET + "/" + ARC_ANIM); return; }
  try {
    if (r != null && r.isValid()) @ANU@.playAnimation(r, @ASL@.Action, ARC_ANIM_SET, ARC_ANIM, true, acc);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the Arcane Breach swing could not play: " + t); }
}
""",
r"""
public static String arcCast(@ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, int stk, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double[] lk = look(st, ref);
  double[] me = here(st, ref);
  if (me == null) return " nopos";
  double ox = me[0];
  double oy = me[1] + 1.1;
  double oz = me[2];
  double dx = 0.0;
  double dy = 0.0;
  double dz = 1.0;
  if (lk != null) { ox = lk[0]; oy = lk[1] - 0.5; oz = lk[2]; dx = lk[3]; dy = lk[4]; dz = lk[5]; }
  else { double[] f = flat(st, ref); if (f != null) { dx = f[0]; dz = f[1]; } }
  double hz = Math.sqrt(dx * dx + dz * dz);
  if (hz < 0.05) {   // straight up / down: fly level along the body's facing
    double[] f2 = flat(st, ref);
    dx = f2 == null ? 0.0 : f2[0];
    dz = f2 == null ? 1.0 : f2[1];
    dy = 0.0;
    hz = Math.sqrt(dx * dx + dz * dz);
    if (hz < 0.05) { dx = 0.0; dz = 1.0; hz = 1.0; }
  }
  double mt = 0.57735;   // tan 30 degrees: the crescent never dives into the ground at your feet
  if (dy > hz * mt) dy = hz * mt;
  if (dy < -hz * mt) dy = -hz * mt;
  double ln = Math.sqrt(dx * dx + dy * dy + dz * dz);
  dx = dx / ln;
  dy = dy / ln;
  dz = dz / ln;
  double rng = @PKG@.AbilNum.AB_RANGE + cxr();
  double wd = @PKG@.AbilNum.AB_WIDTH + cxr();
  double sp = @PKG@.AbilNum.AB_SPEED;
  if (sp < 1.0) sp = 1.0;
  if (rng < 0.5) rng = 0.5;
  if (wd < 0.5) wd = 0.5;
  double amt = h * @PKG@.AbilNum.AB_POWER * cxm();
  @PKG@.AbilJob j = new @PKG@.AbilJob(27, now, u, "ArcaneBreach", ox, oy, oz, rng, amt);
  j.pkey = k;
  j.ai = @PKG@.AbilDefs.BREACH;
  j.sh = sh;
  j.dx = dx;
  j.dy = dy;
  j.dz = dz;
  j.width = wd;
  j.to = sp;
  j.from = 0.0;
  j.start = now;
  j.push = @PKG@.AbilNum.AB_KNOCK;
  j.freeze = breachPctOf(c, @PKG@.AbilNum.AB_BREACH, stk, @PKG@.AbilNum.AB_PERSTACK, @PKG@.AbilNum.AB_STACKCAP, @PKG@.AbilNum.AB_CAP);
  j.secs = durCap(sh == 1 ? @PKG@.AbilNum.AB_SPRINTTIME : @PKG@.AbilNum.AB_TIME, @PKG@.AbilNum.AB_DURMAX);
  j.len = (double) stk;
  j.tref = new java.util.ArrayList();
  j.hits = 0;
  j.every = 50L;
  arcAnim(st, ref);
  aw.add(j);   // last - castNow refunds a cast whose executor throws (nothing queued before)
  ARCS = ARCS + 1L;
  return " flies=" + @PKG@.AbilMath.fmt(rng) + " speed=" + @PKG@.AbilMath.fmt(sp) + " width=" + @PKG@.AbilMath.fmt(wd) + " hit=" + @PKG@.AbilMath.fmt(amt) + " breach=" + @PKG@.AbilMath.fmt(j.freeze) + " secs=" + @PKG@.AbilMath.fmt(j.secs) + " stacks=" + stk;
}
""",
r"""
public static java.util.ArrayList arcHits(@CAC@ acc, @REF@ cr, @PKG@.AbilJob j, double a0, double a1, java.util.ArrayList done) {
  java.util.ArrayList out = new java.util.ArrayList();
  double mid = (a0 + a1) * 0.5;
  double half = j.width * 0.5;
  java.util.List l = near(acc, j.x + j.dx * mid, j.y + j.dy * mid, j.z + j.dz * mid, (a1 - a0) * 0.5 + half + 2.0);
  double hz = Math.sqrt(j.dx * j.dx + j.dz * j.dz);
  double px = hz > 1.0E-6 ? -j.dz / hz : 1.0;
  double pz = hz > 1.0E-6 ? j.dx / hz : 0.0;
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || (done != null && done.contains(t)) || !enemy(acc, t, cr)) continue;
    @VEC@ q = pos(acc, t);
    if (q == null) continue;
    double vx = q.x - j.x;
    double vy = q.y + 0.9 - j.y;
    double vz = q.z - j.z;
    double along = vx * j.dx + vy * j.dy + vz * j.dz;
    if (along < a0 || along > a1) continue;
    if (Math.abs(vx * px + vz * pz) > half + 0.5) continue;
    if (Math.abs(vy - j.dy * along) > 1.6) continue;
    if (!arcClear(acc, j.x + j.dx * along, j.y + j.dy * along, j.z + j.dz * along, q.x, q.z)) continue;   // FIX (critic 1): no wing hits through a side wall
    out.add(t);
  }
  return out;
}
""",
r"""
public static boolean arcClear(@CAC@ acc, double x0, double y, double z0, double x1, double z1) {
  double ddx = x1 - x0;
  double ddz = z1 - z0;
  double d = Math.sqrt(ddx * ddx + ddz * ddz);
  int n = (int) Math.floor(d / 0.5);
  for (int i = 1; i <= n; i++) {   // every 0.5 block from the crescent's centre line out to the target, at the crescent's height (the wall rule)
    double f = (double) i * 0.5 / d;
    double px = x0 + ddx * f;
    double pz = z0 + ddz * f;
    if (arcSolid(acc, px, y, pz) == 1 && arcSolid(acc, px, y - 1.0, pz) == 1) return false;
  }
  return true;
}
""",
r"""
public static int arcFx(@CAC@ acc, @PKG@.AbilJob j, double at) {
  double half = j.width * 0.5;
  double hz = Math.sqrt(j.dx * j.dx + j.dz * j.dz);
  double px = hz > 1.0E-6 ? -j.dz / hz : 1.0;
  double pz = hz > 1.0E-6 ? j.dx / hz : 0.0;
  int n = 0;
  for (int i = -3; i <= 3; i++) {
    double o = (double) i / 3.0 * half;
    double s2 = at - 1.2 * (double) (i * i) / 9.0;   // the wings trail behind the centre: a crescent
    if (s2 < 0.0) s2 = 0.0;
    particle(i == 0 ? FX_ARC : FX_ARC_WING, j.x + j.dx * s2 + px * o, j.y + j.dy * s2, j.z + j.dz * s2 + pz * o, acc);
    n++;
  }
  return n;
}
""",
r"""
public static boolean arcFly(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  @PKG@.AbilCtx c = j.cx;
  if (!live(cb, cr, j.caster, j.pkey)) {   // FIX (critic 3): died / logged out mid-flight = the hits already dealt still count (Momentum + the use);
    // a switched profile gets nothing (another character: used() refuses it the same way)
    boolean same = j.pkey == null || j.pkey.equals(@PKG@.ClassCfg.pkey(j.caster));
    int got = j.tref instanceof java.util.ArrayList ? ((java.util.ArrayList) j.tref).size() : 0;
    if (got > 0 && same && (c == null || !c.echo)) { momAdd(j.caster, (int) Math.round(@PKG@.AbilNum.AB_GAIN), now); used(j.caster, j.pkey, @PKG@.AbilDefs.BREACH, c); }
    LAST_SB = "breach arc gone hit=" + got + (got > 0 ? (same ? " counted" : " switched") : "");
    return false;
  }
  java.util.ArrayList done = j.tref instanceof java.util.ArrayList ? (java.util.ArrayList) j.tref : new java.util.ArrayList();
  j.tref = done;
  double want = (double) (now - j.start) / 1000.0 * j.to;
  if (want > j.r) want = j.r;
  if (want < j.from) want = j.from;
  double d0 = j.from;
  double stop = -1.0;
  double s = d0;
  while (s <= want + 1.0E-9) {   // a wall = the block at the crescent's centre AND the one under it are solid (a step or a fence top lets it pass)
    double bx = j.x + j.dx * s;
    double by = j.y + j.dy * s;
    double bz = j.z + j.dz * s;
    if (arcSolid(cb, bx, by, bz) == 1 && arcSolid(cb, bx, by - 1.0, bz) == 1) { stop = s; break; }
    if (s >= want) break;
    s = s + 0.25;
    if (s > want) s = want;
  }
  double d1 = stop >= 0.0 ? stop : want;
  java.util.ArrayList hs = arcHits(cb, cr, j, d0 - 0.6, d1 + 0.6, done);
  int n = 0;
  boolean imb = imbueOf(j.caster, now) != null;
  double hz = Math.sqrt(j.dx * j.dx + j.dz * j.dz);
  double kx = hz > 1.0E-6 ? j.dx / hz : 0.0;
  double kz = hz > 1.0E-6 ? j.dz / hz : 1.0;
  double kv = j.push * @PKG@.AbilCfg.PUSH_PER_BLOCK;
  for (int i = 0; i < hs.size(); i++) {
    @REF@ t = (@REF@) hs.get(i);
    done.add(t);
    if (j.amount > 0.0 && hit(cb, t, cr, j.caster, j.amount, "ArcaneBreach")) n++;
    breachOn(cb, t, j.caster, j.freeze, j.secs, now, c);
    if (kv > 0.0) push(cb, t, kx * kv, kv * 0.25, kz * kv);
    if (imb && j.amount > 0.0) imbueStatus(cb, t, cr, j.caster, j.amount, true, now);
    @VEC@ q = pos(cb, t);
    if (q != null) particle(FX_ARC_HIT, q.x, q.y + 1.0, q.z, cb);
  }
  j.hits = j.hits + n;
  ARC_HITS = ARC_HITS + (long) n;
  arcFx(cb, j, d1);
  j.from = d1;
  if (stop < 0.0 && d1 < j.r - 1.0E-6) { j.at = now + (j.every > 0L ? j.every : 50L); return true; }
  double ex = j.x + j.dx * d1;
  double ey = j.y + j.dy * d1;
  double ez = j.z + j.dz * d1;
  if (stop >= 0.0) { ARC_WALLS = ARC_WALLS + 1L; particle(FX_ARC_WALL, ex, ey, ez, cb); }
  int extra = 0;
  int ch = c == null ? 0 : c.eff(@PKG@.AbilModDefs.CHAIN);
  if (ch > 0) {   // Chain: the Breach jumps from where the crescent ended to the nearest enemies it missed
    java.util.HashSet skip = new java.util.HashSet(done);
    for (int i = 0; i < ch; i++) {
      @REF@ best = null;
      double bd = 1.0E18;
      java.util.List l = near(cb, ex, ey, ez, @PKG@.AbilNum.AB_CHAINRANGE + j.width * 0.5);
      for (int m = 0; m < l.size(); m++) {
        Object o = l.get(m);
        if (!(o instanceof @REF@) || skip.contains(o) || !enemy(cb, (@REF@) o, cr)) continue;
        @VEC@ w = pos(cb, (@REF@) o);
        if (w == null) continue;
        double dd = (w.x - ex) * (w.x - ex) + (w.z - ez) * (w.z - ez);
        if (dd < bd) { bd = dd; best = (@REF@) o; }
      }
      if (best == null) break;
      skip.add(best);
      breachOn(cb, best, j.caster, j.freeze, j.secs, now, c);
      extra++;
    }
  }
  if (imb && nd(c, "Spellblade", "PA2")) burnPatches(cb, cr, j, done, now);   // Burning Rift: the imbued crescent leaves element patches
  boolean any = done.size() > 0 || extra > 0;
  if (any && (c == null || !c.echo)) { momAdd(j.caster, (int) Math.round(@PKG@.AbilNum.AB_GAIN), now); used(j.caster, j.pkey, @PKG@.AbilDefs.BREACH, c); }
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.BREACH, j.sh) + ": " + (done.size() + extra) + ((done.size() + extra) == 1 ? " enemy" : " enemies") + " Breached - +" + @PKG@.AbilMath.fmt(j.freeze) + " % damage taken for " + @PKG@.AbilMath.fmt(j.secs) + " s" + (extra > 0 ? " (" + extra + " by Chain)" : "") + (stop >= 0.0 ? " (the arc hit a wall)." : "."));
  LAST_SB = "breach arc " + j.sh + " flew=" + @PKG@.AbilMath.fmt(d1) + (stop >= 0.0 ? " wall" : "") + " hit=" + j.hits + " breached=" + (done.size() + extra) + " pct=" + @PKG@.AbilMath.fmt(j.freeze);
  return false;
}
""",
r"""
public static String breachCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {'''
rep('''r"""
public static String breachCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, @PKG@.AbilWorld aw, int sh, double h, long now) {''', ARC_JAVA)
rep('''  int stk = momN(u, now);
  double r = (sh == 3 ? @PKG@.AbilNum.AB_MARKRADIUS : @PKG@.AbilNum.AB_RANGE) + cxr();
  double half = sh == 3 ? 180.0 : @PKG@.AbilNum.AB_ANGLE;''', '''  int stk = momN(u, now);
  if (sh == 0 || sh == 1) return arcCast(st, ref, u, k, aw, sh, h, stk, now);   // 0.1.32: the slash + the flying crescent of light
  double r = @PKG@.AbilNum.AB_MARKRADIUS + cxr();   // 0.1.32: only Marked Ground (crouch) is still a circle around you
  double half = 180.0;''')
rep('''  if (j.kind != 25) return false;
  if (j.ai == @PKG@.AbilDefs.BREACH) breachRun(j, st, cb, now);''', '''  if (j.kind == 27) return arcFly(j, st, cb, now);   // 0.1.32: the Arcane Breach crescent in flight
  if (j.kind != 25) return false;
  if (j.ai == @PKG@.AbilDefs.BREACH) breachRun(j, st, cb, now);''')

# ================================================================================================ 2. the one-time update
rep('''F(cfg, "public static final String MG29_WHO = %s;" % jstr(MG29_WHO))
''', '''F(cfg, "public static final String MG29_WHO = %s;" % jstr(MG29_WHO))
# 0.1.32: the third update's table (migrate0132)
F(cfg, "public static final String[] MG32_KEY = %s;" % jarr([t[0] for t in MG32_DEFAULTS]))
F(cfg, "public static final String[] MG32_OLD = %s;" % jarr([t[1] for t in MG32_DEFAULTS]))
F(cfg, "public static final String[] MG32_NEW = %s;" % jarr([t[2] for t in MG32_DEFAULTS]))
F(cfg, "public static final String[] MG32_WHY = %s;" % jarr([t[3] for t in MG32_DEFAULTS]))
F(cfg, "public static final String MG32_MARK = %s;" % jstr(MG32_MARK))
F(cfg, "public static final String MG32_MARK_ID = %s;" % jstr(MG32_MARK_ID))
F(cfg, "public static final String MG32_WHO = %s;" % jstr(MG32_WHO))
''')
rep('''
# ================= ClassDefs: generated from the Python tables =================''', '''# 0.1.32 (Skyy 2026-10-16): Arcane Breach's numbers row - migrate0110's steps with the 0.1.32 table, right after migrate0129 and before
# ClassCfg.load. "" = nothing done (no file - load() writes the 0.1.32 default with every marker -, marker already there, a failure)
M(cfg, r"""
public static synchronized String migrate0132() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = mgUpdateT(new String(old, "ISO-8859-1"), MG32_KEY, MG32_OLD, MG32_NEW, MG32_WHY, MG32_MARK, MG32_MARK_ID, "0.1.32");
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), MG32_WHO, "before the 0.1.32 defaults update");
    if (!mgSaved(old)) {
      warn("config.properties NOT updated to the 0.1.32 defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLogT(MG32_WHO, rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.32 defaults: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo it)";
    else msg = "config.properties: the ab.ArcaneBreach.numbers line no longer had its 0.1.31 default - nothing changed (0.1.32 defaults marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append('\\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    warn("could not update config.properties to the 0.1.32 defaults (the file is used as it is): " + t);
    return "";
  }
}""")

# ================= ClassDefs: generated from the Python tables =================''')
rep('''  @PKG@.ClassCfg.migrate0129();   // 0.1.29: an untouched kit.Assassin line -> + the Crude Kunai (once; History first)
''', '''  @PKG@.ClassCfg.migrate0129();   // 0.1.29: an untouched kit.Assassin line -> + the Crude Kunai (once; History first)
  @PKG@.ClassCfg.migrate0132();   // 0.1.32: an untouched ab.ArcaneBreach.numbers line -> the flying arc's numbers (once; History first)
''')

# ================================================================================================ 3. class:fn:stacks
rep('''abmig3 = pool.makeClass(PKG + ".AbilMig3")''', '''abstk = pool.makeClass(PKG + ".AbilStacksFn")          # 0.1.32: class:fn:stacks (SkyyHud's stack widget)
abstk.addInterface(pool.get("java.util.function.Function"))
C(abstk, "public AbilStacksFn() { }")
F(abstk, "public static final String UNSTOP_COL = \\"#ffc800\\";")
F(abstk, "public static final String ROLL_COL = \\"#9fe8ee\\";")
# the remaining ms of every live stack of a ring (the AbilMath.live rule), ascending
M(abstk, r"""
public static long[] lefts(long[] ring, long now, long dec) {
  if (ring == null) return new long[0];
  int n = 0;
  long[] tmp = new long[ring.length];
  for (int i = 0; i < ring.length; i++) {
    long g = ring[i];
    if (g > 0L && now - g < dec && now >= g) { tmp[n] = g + dec - now; n++; }
  }
  long[] out = new long[n];
  for (int i = 0; i < n; i++) out[i] = tmp[i];
  for (int i = 1; i < n; i++) {
    long v = out[i];
    int k = i - 1;
    while (k >= 0 && out[k] > v) { out[k + 1] = out[k]; k--; }
    out[k + 1] = v;
  }
  return out;
}""")
M(abstk, r"""
public static String row(String name, int cur, int max, long ms, String col) {
  long t = ms <= 0L ? 0L : Math.round((double) ms / 100.0);
  return name + "|" + cur + "|" + max + "|" + (t / 10L) + "." + (t % 10L) + "|" + col;
}""")
M(abstk, r"""
public static boolean mine(@PKG@.AbilZone z, java.util.UUID u, long now) {
  if (z == null || z.ended || z.ring == null || z.ring.length == 0 || now >= z.until) return false;
  return z.pkey == null || z.pkey.equals(@PKG@.ClassCfg.pkey(u));
}""")
# the rows of one player right now (a snapshot of the in-memory maps; no world call): String[] "name|current|max|secondsLeft|colorHex"
M(abstk, r"""
public static String[] rows(java.util.UUID u, long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || ci >= @PKG@.ClassDefs.NAMES.length) return new String[0];
  String cn = @PKG@.ClassDefs.NAMES[ci];
  String col = @PKG@.ClassDefs.COLORS[ci];
  if ("Spellblade".equals(cn)) {
    Object xo = @PKG@.AbilStore.MOMX.get(u);
    long fl = xo instanceof long[] && ((long[]) xo).length > 6 ? ((long[]) xo)[6] : 0L;
    Object ro = @PKG@.AbilStore.MOMS.get(u);
    long dec = @PKG@.Abil.momDecay(fl);
    int n = @PKG@.Abil.momN(u, now);
    long[] ring = null;
    if (ro instanceof long[]) ring = (long[]) ro;
    long[] left = lefts(ring, now, dec);
    int skip = left.length - n;          // stacks past the max are not counted (momN): the oldest ones go first
    if (skip < 0) skip = 0;
    out.add(row("Momentum", n, @PKG@.Abil.momMax(fl), n > 0 && skip < left.length ? left[skip] : 0L, col));
    int tier = @PKG@.Abil.momTier(n);
    if (tier > 0) {
      int thr = (int) Math.ceil(tier == 2 ? @PKG@.AbilNum.MO_UNSTOPPABLE : @PKG@.AbilNum.MO_ROLLING);
      int ix = skip + n - thr;          // the tier holds until this many stacks more have fallen off
      out.add(row(tier == 2 ? "Unstoppable" : "Rolling", 1, 1, ix >= 0 && ix < left.length ? left[ix] : 0L, tier == 2 ? UNSTOP_COL : ROLL_COL));
    }
  } else if ("Monk".equals(cn)) {
    Object zo = @PKG@.AbilStore.FLOWS.get(u);
    if (zo instanceof @PKG@.AbilZone && mine((@PKG@.AbilZone) zo, u, now)) {
      @PKG@.AbilZone z = (@PKG@.AbilZone) zo;
      long dec = Math.round(@PKG@.AbilNum.FF_DECAY * 1000.0);          // Abil.stacks' rule
      if (z.cx != null && "Monk".equals(z.cx.cls)) {
        if (z.cx.node("PC3")) dec = 7500L;
        else if (z.cx.node("PA4")) dec = 4000L;
      }
      long[] left = lefts(z.ring, now, dec);
      out.add(row(z.ai == @PKG@.AbilDefs.HFISTS ? "Hundred Fists" : "Combo", @PKG@.Abil.stacks(z, now), z.ring.length, left.length > 0 ? left[0] : 0L, col));
    }
  } else if ("Berserker".equals(cn)) {
    Object zo = @PKG@.AbilStore.FRENZ.get(u);
    if (zo instanceof @PKG@.AbilZone && mine((@PKG@.AbilZone) zo, u, now)) {
      @PKG@.AbilZone z = (@PKG@.AbilZone) zo;
      double dm = z.cx == null ? 1.0 : z.cx.durMult;
      long[] left = lefts(z.ring, now, Math.round(@PKG@.AbilNum.BF_DECAY * dm * 1000.0));          // Abil.frenzyStacks' rule
      out.add(row("Blood Frenzy", @PKG@.Abil.frenzyStacks(z, now), z.ring.length, left.length > 0 ? left[0] : 0L, col));
    }
  }
  return (String[]) out.toArray(new String[0]);
}""")
M(abstk, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = null;
    if (o instanceof Object[] && ((Object[]) o).length >= 1 && ((Object[]) o)[0] instanceof java.util.UUID) u = (java.util.UUID) ((Object[]) o)[0];
    else if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    if (u == null || @PKG@.Abil.prOf(u) == null) return null;
    return rows(u, System.currentTimeMillis());
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class:fn:stacks failed: " + t); return null; }
}""")
abmig3 = pool.makeClass(PKG + ".AbilMig3")''')
rep('''  b.put("class:fn:momAdd", new @PKG@.AbilMomAddFn());       // 0.1.31: SkyyArmory's lunges grant their Momentum once
''', '''  b.put("class:fn:momAdd", new @PKG@.AbilMomAddFn());       // 0.1.31: SkyyArmory's lunges grant their Momentum once
  b.put("class:fn:stacks", new @PKG@.AbilStacksFn());       // 0.1.32: SkyyHud's stack widget - String[] "name|current|max|secondsLeft|colorHex"
''')
rep('''  try { @PKG@.ClassCfg.bridge().remove("class:fn:momAdd"); } catch (Throwable t) { }      // 0.1.31
''', '''  try { @PKG@.ClassCfg.bridge().remove("class:fn:momAdd"); } catch (Throwable t) { }      // 0.1.31
  try { @PKG@.ClassCfg.bridge().remove("class:fn:stacks"); } catch (Throwable t) { }      // 0.1.32
''')
rep('''          abmomfn,                       # 0.1.31: + class:fn:momAdd
''', '''          abmomfn,                       # 0.1.31: + class:fn:momAdd
          abstk,                         # 0.1.32: + class:fn:stacks
''')

assert s.count("registerCommand(") == REG0, "command registrations changed"
assert "AB_ANGLE" not in s, "0.1.32: the angle key is gone everywhere"
assert len(re.findall(r'b\.put\("class:fn:', s)) == len(re.findall(r'b\.put\("class:fn:', OLD)) + 1, "0.1.32: one new bridge key"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.31 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines; 0.1.31 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
