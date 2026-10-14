"""Derive SkyyClasses/build_skyyclasses_0.1.22.py from the generated 0.1.21 (the SET pin; the EDITED lineage: Skyy's edited 0.1.6 ->
classes_0_1_7_patch.py -> ... -> classes_0_1_21_patch.py -> 0.1.21; classes_0_1_6_patch.py is never re-run). 0.1.21 stays untouched; its
line endings are kept.
Run:  python tools/classes_0_1_22_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.22.py   (never --deploy)
Test: python SkyyClasses/test_skyyclasses_0.1.22.py [--dir <scratch>] [--keep]

0.1.22 (2026-10-14) = THE REAL KEYS + ABILITY LEVELS + MODIFIERS + THE CLASS-TREE UPGRADES, Mage + Priest (research/Ability-Framework-
Mage-Spec.md phases B2 'abil04' + D 'abil-mods' + E 'abil-tree'; Skyy 2026-10-14: "Link ability's to the ability buttons, and enable the
class skill trees. Add the ability controls and their modifiers to the skill trees, so you can enable, upgrade and customize them in the
skill trees right beside the skill tree." + popups "Build now, /cast backup (Recommended)", "Panel on the right (Recommended)", "Mage +
Priest (Recommended)", and "We are using the new rune system for our ability's right?" -> yes: the Hytale 0.7 rune keys). Skyy's later
answers win over the spec: M8 2026-10-13 (no modifier points: ability levels by USE, 20+ levels with diminishing returns, every modifier
unlocks at a set ability level then levels by use, 2 slots, a STACKABLE modifier at modifier Lv 2 may sit in both slots = double effect +
levels twice as fast), M5 (cooldowns clear on relog), the 2026-10-08 keys (2 PRIMARIES on Ability 2 / 3, the 2 ALTS on crouch + Ability
2 / 3, Ability 1 stays the weapon signature, the roll stays on the sprint press, Skyy's binds never touched).
  THE REAL KEYS (the Hytale 0.7 rune system; SkyyClasses ships an ASSET PACK for the first time - IncludesAssetPack true):
    - 9 hidden rune ITEMS SkyyAbility_<Class>_<Id> (Mage Meteor / ManaBarrier / FrostNova / Starfall / ArcaneBeam, Priest SacredHeal /
      ShieldBubble / Sanctuary / MartyrsGrace; Guardian Spirit is a passive - no rune): Quality Debug (HideFromSearch), no recipe,
      DropOnDeath false, MaxStack 1, the vanilla rune model + blank rune texture (referenced, not copied), our own icons from
      art/ability-icons (64 px item icon + the 128 px Common/Icons/Abilities/<rune id>.png the vanilla rune HUD reads - U2),
      Ability { Slot Core, Cost 0, CostType None, Cooldown 0.25, AbilityKeywords [SkyyClass] (our own keyword asset), Cast
      Root_SkyyAbility_<Class>_<Id> } - no Weapons tags, so CoreItemAbility.canUseWith = any held item with a Weapon block (every
      SkyyArmory staff / spellbook / wand has one; the class gate is our code). The cast root = one named ApplyEffect step that puts the
      0.5 s marker effect SkyyAbility_Mark_<Id> on the caster (RequireNewClick: one chain per press) - it does nothing else.
    - THE HOOK AbilRuneSys = EntityEventSystem<InteractionChainStartEvent> on players: type Ability2 / Ability3 of a Mage / Priest whose
      chain item is one of our runes (or ANY rune in the ability section -11 = a vanilla rune) -> the chain is CANCELLED (the engine sends
      the client a cancel packet: no vanilla cost, cooldown or animation - our root does nothing anyway) and the cast runs one tick later
      on the world thread through the SAME pipeline as /cast (RuneCast -> Abil.castAt door 1): Ability 2 = /cast 1, Ability 3 = /cast 2,
      crouch held = the alt, the walking / sprinting / mid-air shapes from the movement at the press, the roll (MovementStates.rolling)
      = the sprinting shape (abil.rollCast; off = refused). A refusal (cooldown, Mana, weapon, locked, tree) = the usual throttled line
      + fail sound. A vanilla rune on a key of a Mage / Priest is BLOCKED (Skyy M2; second fix round: cancelled, nothing cast, a
      one-line hint every 30 s; abil.vanillaRunes on = the game rune works); other classes and classless players keep the game's runes untouched. A 120 ms repeat guard per key.
    - THE MIRROR (abil.runeHud): every 2 s per player (AbilTick, a map lookup) the wanted pair = the runes of your 2 primaries that you
      may cast now (owned, built, not a passive, enabled in the class tree, the item loaded) is compared with the AbilitySlots section;
      a difference (or 15 s since the last look, or a PlayerReady / profile / loadout change) schedules MirrorTask on the world thread:
      our runes in any wrong ability slot leave, the wanted ones go into slots 0 (Ability 2) / 3 (Ability 3) WHEN THOSE ARE EMPTY - a
      vanilla rune there is never touched (blocked on that key: a hint says to move it). Classless / other classes: our runes
      leave, nothing else changes. Modifier slots 1-2 / 4-5 stay the player's.
    - THE GUARD AbilInvSys = EntityEventSystem<InventoryChangeEvent>: a change of the AbilitySlots section re-checks the mirror at once; a
      SkyyAbility_ item in any other container (dragged into the rune bag / hotbar / storage, picked up from the ground) schedules
      InvClean, which removes every SkyyAbility_ stack outside the AbilitySlots (hotbar, storage, backpack, utility, tools, armour, rune
      bag; counted before / after, logged) - the mirror then puts the slot back.
    - THE FALLBACK (U3, abil.runeFallback): if the hook never fires, the cast root still runs and puts its marker effect on you; AbilTick
      looks for the 2 markers of your mirrored runes (players with a mirror record only), takes the effect off and casts (door 2) - a
      marker within 700 ms of a hook press is ignored (no double cast).
    - abil.runeCooldownFill (OFF by default, UNVERIFIED U6): after a primary's rune cast, arm the player's server CooldownHandler for the
      rune's cast root id for the cooldown (reflection on the private fields the SkyyAbilityProbe reads), so the vanilla slot may show the
      fill. Off by default: an engine cooldown on the root could block the crouch alt on the same key. Logged once on a failure.
    - /cast 1-4 stays (abil.castCmd; off = /cast only lists); /cast list / swap / page always work. Never a command named /abilities.
  ABILITY LEVELS BY USE (abil.levels; per profile in abilities/<pkey>.properties, key u.<Id>): a use counts when the ability DID something
    (Meteor / Starfall / Arcane Beam / Frost Nova: hit >= 1 enemy; Mana Barrier / Shield Bubble: soaked >= 4 HP (+ a bubble heal pulse);
    Sacred Heal / Sanctuary / Martyr's Grace: healed someone; Guardian Spirit: a save), at most one per ability per abil.useEvery 3 s,
    never an echo, never after a profile switch. Uses for level n = round(abil.usesCoef 4.5 x n ^ abil.usesExp 1.5) (Lv 2 = 13, Lv 10 =
    142), up to abil.maxLevel 25 ("20+", Skyy M8). DIMINISHING RETURNS: +abil.perLevel 2 % of the main effect per level up to
    abil.softLevel 10, half that up to abil.halfLevel 20, a quarter after (Lv 10 +18 %, Lv 20 +28 %, Lv 25 +30.5 %). Main effect =
    damage, heal, the Mana Barrier ratio, the bubble HP, the Sanctuary heal, the Guardian Spirit save Health. A level-up line names the
    modifiers it unlocked. Rebirth keeps them readable (class:fn:abilPanel / abilMods).
  MODIFIERS (mods.on; Skyy M8 - NO points): every ability offers its modifiers in unlock order (mods.unlock 2,4,6,8,10 = the ability
    level of the 1st..5th): Meteor Power+ Radius+ Split Lingering Echo; Mana Barrier Power+ Duration+ Ward Follow Knockback+; Frost Nova
    Power+ Radius+ Duration+ Slow; Starfall Power+ Radius+ Duration+ Echo; Arcane Beam Power+ Duration+ Slow Pierce; Sacred Heal Power+
    Radius+ Duration+ Efficiency Echo; Shield Bubble Power+ Radius+ Duration+ Follow Echo; Guardian Spirit Power+ Radius+ Efficiency
    Ward; Sanctuary Power+ Radius+ Duration+ Follow; Martyr's Grace Power+ Chain Efficiency Ward Echo. A modifier levels by use while
    equipped (each counted use = +1 modifier use, +2 when doubled; mods.steps 10,30,60,100 = Lv 2-5). 2 SLOTS per ability (key e.<Id> =
    "Power,Echo"); with class trees on, the slots are the tree's M<line>A / M<line>B nodes. STACKABLE (Power+, Radius+, Duration+,
    Efficiency, Pierce, Chain, Slow, Knockback+): from modifier Lv 2 it may sit in BOTH slots = double effect, levels twice as fast;
    the others (Split, Lingering, Follow, Ward, Echo) never double. Effects per level: Power+ +mods.power 5 % main effect; Radius+
    +mods.radius 0.5 block (Guardian Spirit +5 blocks); Duration+ +mods.duration 10 % (freeze, stars, beam, dome, bubble, zone, heal over
    time); Efficiency -mods.efficiency 5 % Mana + Stamina (never below 50 %); Split = 3 meteors around the spot at 40 % + 5 % a level,
    75 % size; Lingering = burning ground 3 s + 0.5 s a level after Lv 1, 8 % + 2 % a level of the meteor a second; Pierce +1 enemy behind the
    first; Slow = Arcane Beam slows 1 s + 0.5 s a level, Frost Nova chill +1 s a level; Chain = +1 target and -1.6 % drop a level (Lv 5:
    10 targets at 7 %); Ward = a shield of 3 % max Health a level (Mana Barrier: you + party within 4 blocks for the dome's time; Martyr's
    Grace: the overheal, up to that; Guardian Spirit: the saved player, 5 s); Follow = the zone moves with you (Mana Barrier at 80 % +
    5 % a level of its ratio); Knockback+ = the dome bursts when it ends, enemies within its radius + 1 pushed 8 + 2 blocks / s (Skyy M6:
    they may fall); ECHO = the same executor again abil.echoDelay 1 s later at mods.echoBase 20 + mods.echoStep 2.5 % a level (Skyy M9
    20-30 %), without the other modifier, free, no cooldown, never counted, never echoed, dropped when you left (Meteor: the same spot;
    Starfall: a second shower; Sacred Heal: a second instant heal in the same circle; Martyr's Grace: the chain again; Shield Bubble: a
    weaker bubble once where it ended / broke). Numbers resolve ONCE at the cast (AbilCtx, carried by every job / zone it makes).
  THE CLASS-TREE UPGRADES (Skyy LOCKED 2026-10-04 TWO UPGRADE LAYERS: the class tree changes HOW an ability works; levels + modifiers stay
    in the ability). SkyyTrees 0.3.7 publishes tree:fn:abil (UUID -> "A1,A2,M1A,T4=10,..." the intact class nodes, null = class trees
    off / no SkyyTrees = no gate); SkyyClasses lists what it applies in tree:reads:SkyyClasses (the reader contract) so those nodes become
    buyable: A1-A4 = ENABLE ability line 1-4 (A1 Meteor / Sacred Heal, A2 Mana Barrier / Shield Bubble, A3 Frost Nova / Guardian
    Spirit, A4 the Ability 1 alt) - abil.treeGate: with class trees on, an ability needs its A node; M<line>A / M<line>B = its 2
    modifier slots. Path nodes applied (Class-Tree-Paths.md): Mage T4 Barrier Lore (ratio + the Amount %), T6 Quick Hands (cooldowns -
    Amount %), PA3 Phase Step (the dome follows you at full strength, 2 s shorter; the blink part waits for SkyyArmory), PB2 Prism
    (each star strikes a second point, 85 %), PB3 Beam Focus (the beam refracts to a 2nd enemy within 6 blocks at 60 %, starts 0.3 s
    later), PB4 Brilliance (a cast that hits 3+ enemies gives 10 % of its Mana back; Arcane Beam costs 5 % more), PB5 Sunburst (Starfall
    ends with a 1.5 H burst, +4 s cooldown), PC1 Overcharge (cast at full Mana +15 %, under 25 % Mana -10 %), PC3 Charged Dome (the dome
    bursts for 50 % of what it soaked within 4 blocks when it ends; ratio x 0.75 = 1 Mana per 1.5 HP), PC4 Deep Beam (ramp +1x, +0.5 s,
    +10 Mana), PC5 Arch-Mage (a 2 s star well pulls enemies in after the Meteor, +4 s cooldown); Priest T3 Wide Prayer (Sacred Heal
    +1.5 blocks, + the Amount points of heal), T4 Warm Light (heal over time + the Amount points), T6 Patient Spirit (cooldowns -), TS
    Open Aura (the switch: Guardian Spirit saves everyone), PA1 Cleanse (Sacred Heal takes Poison / Burn / Slow / Root / Vulnerable off
    everyone it heals; +5 Mana, heal -10 %), PA3 Beacon (Martyr's Grace: first heal -10 points, every target regenerates 2 % a second
    for 10 s), PA4 Dawnlight (Sanctuary +2 blocks, 2 s shorter, cleanses every 2 s), PA5 Lightbringer (Sacred Heal: your bonus 40 %,
    allies under 30 % Health +25 %, +4 s cooldown), PB1 Thorned Bubble (an attack the bubble soaks hurts the attacker 0.5 H; bubble HP
    -15 %), PB3 Layered Ward (FIX ROUND: the bubble's HP = two layers on one bar, the outer half soaks first, the inner half regrows 3 %
    of the bubble's HP a second; 2 s shorter), PB4 Spirit Shield (FIX ROUND: a save also gives the saved player a 4 s personal bubble =
    a ward of 15 % max Health; saved at 2/3 of the Guardian Spirit Health = 20 % instead of 30 %), PB5 Aegis (the bubble explodes for
    1.5 H in 4 blocks when it breaks, 1 s shorter). WAITING (not listed - they stay "Comes with the class abilities"): Mage PA4 Meteor
    from the Rift (needs the SkyyArmory blink), PC2 Siphon (needs a kill hook); Priest PA2 Radiant Pulse (its text copies Echo - Skyy's
    call: Guiding Light), PB2 Elemental Bubble (an element picker); every SkyyArmory node stays SkyyArmory's.
  BRIDGES for SkyyTrees 0.3.7's ability panel (plain java.lang; any thread):
    class:fn:abilPanel  Object[] { UUID, String treeCsv (or null) } -> Object[78] (status, class, level, combat, pick, canPick, gate, the 4
                        unlock levels, levels / mods on, grant; then 4 x 16 per slot: id, name, rune item (loaded) or "", owned, enabled,
                        line, level, uses, uses to next, level text, mod 0 + level, mod 1 + level, slots, state; the A / B alt names)
    class:fn:abilMods   Object[] { UUID, String abilityId, String treeCsv } -> String[] (head + one row per offered modifier)
    class:fn:abilDo     Object[] { UUID, String action, String a, String b, String treeCsv } -> "+done" / "-why": swap <slot> <slot>,
                        pick A|B, equip <abilityId> <slot>:<mod>, unequip <abilityId> <slot> (out of combat only; the tree's slots)
    class:fn:abilUnlock Integer line 1-4 -> Long class level of that line (abil.unlock.*) - the A nodes' level gate
    tree:reads:SkyyClasses  the class node keys above (removed again at shutdown)
  FIX ROUND (critics): a ward belongs to the profile it was given to (a profile switch drops it); a failed ability-file write is retried
    by the next 30 s flush; a rune the ability slot refuses is logged once per player and the mirror then waits 60 s after 3 failures
    in a row; the per-player key maps are cleared at leave. SkyyTrees 0.3.7 makes the A / M nodes free (0 AP).
  M5: every ability cooldown of a player is cleared when they leave (ClassQuit), so a relog starts fresh. Ability uses are flushed every
    30 s (ClassTick, never the world thread) + at leave + at shutdown.
  class:fn:loadoutGet / Set: the mods part is real now ("mods=Meteor:Power+Echo/ManaBarrier:Ward+-"; an invalid / locked one is skipped
    and listed). class:fn:abil (SkyyHud) keeps its 48 fields; a line the tree has not enabled shows "locked", costs include Efficiency.
  /classadmin abil <player> maxlevels | resetlevels (testing: every ability of that profile to its top level / back to Lv 1).
  Saved data: abilities/<pkey>.properties gains u.<Id>, m.<Id>.<Mod>, e.<Id> - an older jar ignores them (no migration).
  ROLLBACK to 0.1.21: abil.runeHud off + one login first (our runes leave the ability slots), else the rune items stay as dead items
  in the AbilitySlots until removed by hand.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.21.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.22.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.21"' in s and "GENERATED by tools/classes_0_1_21_patch.py from the generated 0.1.20" in s, \
    "build_skyyclasses_0.1.21.py is not the generated 0.1.21"
assert "AbilRuneSys" not in s and "SkyyAbility_" not in s
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old))


def block(cls, sig):
    """the whole M(<cls>, r'''...''') statement whose Java starts with sig -> (start, end)"""
    head = 'M(%s, r"""\n%s' % (cls, sig)
    n = s.count(head)
    assert n == 1, "method block count %d: %s" % (n, head[:120])
    a = s.index(head)
    b = s.index('}""")\n', a) + len('}""")\n')
    return a, b


def replace_method(cls, sig, new_java):
    """swap one generated method for the new Java (new_java = the full method text)"""
    global s
    a, b = block(cls, sig)
    assert new_java.lstrip().startswith(sig.split("(")[0].strip()), "the new method does not start like %s" % sig
    s = s[:a] + 'M(%s, r"""\n%s\n}""")\n' % (cls, new_java.strip()[:-1].rstrip()) + s[b:]
    CHANGES.append(("method", sig))


def method_text(cls, sig):
    a, b = block(cls, sig)
    return s[a:b]


def rep_in(cls, sig, old, new, count=1):
    """a replacement inside one method block only"""
    global s
    a, b = block(cls, sig)
    body = s[a:b]
    n = body.count(old)
    assert n == count, "anchor count %d != %d inside %s: %s" % (n, count, sig[:60], old[:140])
    s = s[:a] + body.replace(old, new) + s[b:]
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.22 (2026-10-14)"):].rstrip()

# ================================================================================================ docstring, version
rep('''"""SkyyClasses 0.1.21 - build script (javassist via jpype). GENERATED by tools/classes_0_1_21_patch.py from the generated 0.1.20 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_20_patch.py -> 0.1.20) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.22 - build script (javassist via jpype). GENERATED by tools/classes_0_1_22_patch.py from the generated 0.1.21 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_21_patch.py -> 0.1.21) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''' + NOTE.replace(LF, LF + "  ").replace("  " + LF, LF) + '''
  Notes in tools/classes_0_1_22_patch.py. CHECKED with SkyyClasses/test_skyyclasses_0.1.22.py.
''')
rep('VERSION = "0.1.21"', 'VERSION = "0.1.22"')

# ================================================================================================ the new Server Setup rows (ABIL_ROWS)
# 0.1.22: two new categories - "Ability keys" (the rune route) and "Ability levels" (levels by use + modifiers)
rep('''_r("ab.MartyrsGrace.vowTime", "G_VOW_T", "dec", 1.0, "0", "5", "s", "abilp", "Martyr's Vow channel", "Seconds you channel before the chain.")
''', '''_r("ab.MartyrsGrace.vowTime", "G_VOW_T", "dec", 1.0, "0", "5", "s", "abilp", "Martyr's Vow channel", "Seconds you channel before the chain.")
# 0.1.22: THE REAL KEYS (the Hytale 0.7 rune route; tools/classes_0_1_22_patch.py)
_r("abil.runeKeys", "RUNE_KEYS", "bool", True, "", "", "", "abilk", "Cast with the Ability 2 / 3 keys",
   "Mage + Priest: the keys cast your 2 primaries, crouch + key your alts (runes in the ability slots).")
_r("abil.castCmd", "CAST_CMD", "bool", True, "", "", "", "abilk", "Cast with /cast 1-4",
   "Off: /cast 1-4 is refused (the keys cast). /cast list, swap and page always work.")
_r("abil.vanillaRunes", "VAN_RUNES", "bool", False, "", "", "", "abilk", "Vanilla runes for Mage + Priest",
   "Off (Skyy M2 Blocked): a game rune on their keys does nothing + a hint. Others keep game runes.")
_r("abil.runeHud", "RUNE_HUD", "bool", True, "", "", "", "abilk", "Ability runes in the rune slots",
   "Puts your 2 primaries' runes into the game's 2 ability slots. Off: our runes leave them.")
_r("abil.runeCooldownFill", "RUNE_FILL", "bool", False, "", "", "", "abilk", "Rune slot cooldown fill (test)",
   "UNVERIFIED: arms the game's own cooldown so the slot shows it. Can block an alt on that key.", "live,adv")
_r("abil.runeFallback", "RUNE_FB", "bool", True, "", "", "", "abilk", "Key fallback (marker effect)",
   "If the key hook never fires, a rune's marker effect still casts.", "live,adv")
_r("abil.rollCast", "ROLL_CAST", "bool", True, "", "", "", "abilk", "Cast during a roll",
   "A key press during the sprint roll casts the sprinting shape. Off: refused.")
_r("abil.treeGate", "TREE_GATE", "bool", True, "", "", "", "abilk", "Abilities need their class tree node",
   "With class trees on, enable each ability (A1-A4) in /tree class. Off: class level only.")
# 0.1.22: ABILITY LEVELS BY USE + MODIFIERS (Skyy M8 2026-10-13: no points; levels 20+ with diminishing returns)
_r("abil.levels", "LEVELS", "bool", True, "", "", "", "abill", "Ability levels",
   "Abilities level up by use (casts that hit or heal). Off: every ability works at Lv 1.")
_r("abil.maxLevel", "MAX_LVL", "int", 25, "1", "100", "", "abill", "Highest ability level", "Skyy: 20+ levels with diminishing returns.")
_r("abil.usesCoef", "USES_COEF", "dec", 4.5, "0.1", "100", "", "abill", "Uses per level (factor)",
   "Uses for level n = factor x n ^ power (Lv 2 = 13, Lv 10 = 142 uses).", "live,adv")
_r("abil.usesExp", "USES_EXP", "dec", 1.5, "0.5", "3", "", "abill", "Uses per level (power)", "See the factor.", "live,adv")
_r("abil.useEvery", "USE_EVERY", "dec", 3.0, "0", "60", "s", "abill", "One counted use every",
   "Per ability. Echoes and casts that hit or heal nothing never count.")
_r("abil.perLevel", "PER_LEVEL", "dec", 2.0, "0", "20", "%", "abill", "Gain per level (main effect)",
   "Full gain up to the soft level, half up to the half level, a quarter after.")
_r("abil.softLevel", "SOFT_LVL", "int", 10, "1", "100", "", "abill", "Full gain up to level", "Diminishing returns start after this level.")
_r("abil.halfLevel", "HALF_LVL", "int", 20, "1", "100", "", "abill", "Half gain up to level", "After this level each level gives a quarter.")
_r("mods.on", "MODS_ON", "bool", True, "", "", "", "abill", "Ability modifiers", "Off: equipped modifiers do nothing (they stay equipped).")
_r("mods.unlock", "MOD_UNLOCK", "text", "2,4,6,8,10", "", "40", "", "abill", "Modifier unlock levels",
   "Ability level for each ability's 1st, 2nd ... 5th modifier.")
_r("mods.steps", "MOD_STEPS", "text", "10,30,60,100", "", "40", "", "abill", "Modifier level steps (uses)",
   "Uses while equipped for modifier Lv 2, 3, 4, 5. Doubled = twice as fast.")
_r("mods.power", "MOD_POWER", "dec", 5.0, "0", "100", "%", "abill", "Power+ per level", "Main effect (damage, heal, shield) per modifier level.")
_r("mods.radius", "MOD_RADIUS", "dec", 0.5, "0", "10", "blocks", "abill", "Radius+ per level", "Blocks per modifier level (Guardian Spirit x 10).")
_r("mods.duration", "MOD_DUR", "dec", 10.0, "0", "100", "%", "abill", "Duration+ per level", "Length per modifier level.")
_r("mods.efficiency", "MOD_EFF", "dec", 5.0, "0", "50", "%", "abill", "Efficiency per level", "Less Mana and Stamina per level (never below half).")
_r("mods.echoBase", "ECHO_BASE", "dec", 20.0, "0", "100", "%", "abill", "Echo strength at Lv 1", "Skyy: 20-30 %. The echo repeats the cast this strong.")
_r("mods.echoStep", "ECHO_STEP", "dec", 2.5, "0", "50", "%", "abill", "Echo strength per level", "Added per Echo level above 1.")
_r("abil.echoDelay", "ECHO_DELAY", "dec", 1.0, "0.2", "10", "s", "abill", "Echo delay", "Seconds from the cast (or its end) to the echo.")
''')
rep('''            ("abils", "Ability shapes"), ("abilm", "Mage abilities 2"), ("abilp", "Priest abilities 2")]       # 0.1.18''',
    '''            ("abils", "Ability shapes"), ("abilm", "Mage abilities 2"), ("abilp", "Priest abilities 2"),       # 0.1.18
            ("abilk", "Ability keys"), ("abill", "Ability levels")]                                         # 0.1.22''')

# ================================================================================================ modifier + rune tables (Python side)
rep('''ABIL_LINES = [
''', '''# 0.1.22 MODIFIERS (Skyy M8: unlocked by ability level, levelled by use, 2 slots, a stackable one may double from its Lv 2)
MODS = [("Power", "Power+", True), ("Radius", "Radius+", True), ("Duration", "Duration+", True), ("Efficiency", "Efficiency", True),
        ("Split", "Split", False), ("Pierce", "Pierce", True), ("Chain", "Chain", True), ("Lingering", "Lingering", False),
        ("Slow", "Slow", True), ("Knockback", "Knockback+", True), ("Follow", "Follow", False), ("Ward", "Ward", False),
        ("Echo", "Echo", False)]
MOD_IDS = [m[0] for m in MODS]
# per ability, in unlock order (research/classes/Mage.md + Priest.md lists; Echo where Skyy added it 2026-10-07)
AB_MODS = {
    "Meteor": ["Power", "Radius", "Split", "Lingering", "Echo"],
    "ManaBarrier": ["Power", "Duration", "Ward", "Follow", "Knockback"],
    "FrostNova": ["Power", "Radius", "Duration", "Slow"],
    "Starfall": ["Power", "Radius", "Duration", "Echo"],
    "ArcaneBeam": ["Power", "Duration", "Slow", "Pierce"],
    "SacredHeal": ["Power", "Radius", "Duration", "Efficiency", "Echo"],
    "ShieldBubble": ["Power", "Radius", "Duration", "Follow", "Echo"],
    "GuardianSpirit": ["Power", "Radius", "Efficiency", "Ward"],
    "Sanctuary": ["Power", "Radius", "Duration", "Follow"],
    "MartyrsGrace": ["Power", "Chain", "Efficiency", "Ward", "Echo"],
}
assert sorted(AB_MODS) == sorted(a[0] for a in ABILS) and all(m in MOD_IDS for v in AB_MODS.values() for m in v)
assert all(2 <= len(v) <= 5 and len(set(v)) == len(v) for v in AB_MODS.values())
assert all("Echo" in AB_MODS[_a] for _a in ("Meteor", "Starfall", "SacredHeal", "MartyrsGrace", "ShieldBubble")), "Skyy's Echo locks"
assert "Follow" in AB_MODS["ShieldBubble"] and "Follow" in AB_MODS["ManaBarrier"], "Skyy's Follow locks (L113, L53)"
# what Power+ (and the ability level) makes stronger, per ability (the panel text)
AB_NOUN = {"Meteor": "damage", "ManaBarrier": "HP per Mana", "FrostNova": "damage", "Starfall": "damage", "ArcaneBeam": "damage",
           "SacredHeal": "heal", "ShieldBubble": "bubble HP", "GuardianSpirit": "Health on a save", "Sanctuary": "heal",
           "MartyrsGrace": "heal"}
# THE RUNES (the Hytale 0.7 route): one hidden rune item per castable ability (no rune for the passive)
RUNE_ABILS = [a for a in ABILS if not a[5]]
assert [a[0] for a in RUNE_ABILS] == ["Meteor", "ManaBarrier", "FrostNova", "Starfall", "ArcaneBeam", "SacredHeal", "ShieldBubble",
                                      "Sanctuary", "MartyrsGrace"]
def rune_id(a): return "SkyyAbility_%s_%s" % (a[2], a[0])
def rune_root(a): return "Root_SkyyAbility_%s_%s" % (a[2], a[0])
def rune_cast(a): return "SkyyAbility_Cast_%s" % a[0]
def rune_mark(a): return "SkyyAbility_Mark_%s" % a[0]
# the class tree nodes SkyyClasses applies (SkyyTrees reader contract tree:reads:SkyyClasses; Class-Tree-Paths.md section 3 / 4)
TREE_K = {"Mage": ["T4", "T6", "PA3", "PB2", "PB3", "PB4", "PB5", "PC1", "PC3", "PC4", "PC5"],
          "Priest": ["T3", "T4", "T6", "TS", "PA1", "PA3", "PA4", "PA5", "PB1", "PB3", "PB4", "PB5"]}   # fix round: + PB3 Layered Ward, PB4 Spirit Shield
TREE_SLOTS = ["A1", "A2", "A3", "A4", "M1A", "M1B", "M2A", "M2B", "M3A", "M3B", "M4A", "M4B"]
TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest") for _n in TREE_SLOTS + TREE_K[_c])
# the debuffs Cleanse (Priest PA1) / Dawnlight (PA4) take off (vanilla status effects, checked against Assets.zip below)
CLEANSE = ["Poison", "Poison_T1", "Poison_T2", "Poison_T3", "Burn", "Slow", "Root", "Vulnerable"]
ABIL_LINES = [
''')
rep('''    "# 0.1.18: ab.<Ability>.sprint / .air / .crouch = the shapes (sprinting, mid-air, crouch alt); abil.shapes* switch them off.",
''', '''    "# 0.1.18: ab.<Ability>.sprint / .air / .crouch = the shapes (sprinting, mid-air, crouch alt); abil.shapes* switch them off.",
    "# 0.1.22: abil.runeKeys, castCmd, vanillaRunes, runeHud ... = the Ability 2 / 3 keys (the Hytale 0.7 runes); abil.levels,",
    "# abil.maxLevel ... = ability levels by use (diminishing returns); mods.* = the modifiers (unlock levels, steps, per level).",
''')
rep('''import skyyroute as RT     # 0.1.20''', '''import skyyart as SA       # 0.1.22: the PNG codec for the rune icons (pure Python; our own art from art/ability-icons)
import skyyroute as RT     # 0.1.20''')

# ================================================================================================ THE RUNE ASSET PACK (build time)
rep('''abdefs = pool.makeClass(PKG + ".AbilDefs")
''', '''# =====================================================================================================================
# 0.1.22 THE RUNE ASSET PACK (the Hytale 0.7 rune keys; tools/classes_0_1_22_patch.py). Every vanilla thing it names is checked here against
# the release Assets.zip (read-only) and every id / path against Assets.zip and the other SET jars (no override, no clash).
# =====================================================================================================================
RUNE_FILES = {}
_azn = set(_ASSETS.namelist())
_vr = json.loads(_ASSETS.read("Server/Item/Items/Rune/Ability/Rune_Fireball.json").decode("utf-8-sig"))
assert _vr["Ability"]["Slot"] == "Core" and _vr["Ability"]["Cast"] == "Root_Ability_Fireball", "the vanilla rune shape changed (Slot / Cast)"
assert set(_vr["Ability"]) <= {"Slot", "Cooldown", "Cost", "CostType", "AbilityKeywords", "Attributes", "Cast", "Weapons"}, sorted(_vr["Ability"])
RUNE_MODEL, RUNE_TEX = "Items/Runes/Rune_Ability.blockymodel", "Items/Runes/Rune_Textures/Rune_Ability_Blank.png"
assert _vr["Model"] == RUNE_MODEL and "Common/" + RUNE_MODEL in _azn and "Common/" + RUNE_TEX in _azn, "the vanilla rune model / blank texture moved"
assert "Server/Audio/ItemSounds/%s.json" % _vr["ItemSoundSetId"] in _azn, "the rune sound set moved"
_dq = json.loads(_ASSETS.read("Server/Item/Qualities/Debug.json").decode("utf-8-sig"))
assert _dq.get("HideFromSearch") is True, "the Debug quality no longer hides items from search"
_dr = json.loads(_ASSETS.read("Server/Item/Interactions/Abilities/Ability_Cast_Fail.json").decode("utf-8-sig"))
assert [n for n in _azn if n.startswith("Server/Item/Interactions/") and n.endswith(".json") and '"ApplyEffect"' in _ASSETS.read(n).decode("utf-8-sig")], "no ApplyEffect step"
assert json.loads(_ASSETS.read("Server/Entity/Effects/Projectiles/Arrow/Crossbow/Crossbow_Combo_1.json").decode("utf-8-sig")) == {"Duration": 5}, \\
    "a Duration-only effect (our marker shape) is no longer vanilla"
assert "Common/Icons/Abilities/Rune_Fireball.png" in _azn, "the rune HUD icon path Icons/Abilities/<rune id>.png moved (U2)"
for _c in CLEANSE:
    assert "Server/Entity/Effects/Status/%s.json" % _c in _azn, "Cleanse: vanilla status effect %s missing" % _c
_vlang = _ASSETS.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
assert "\\nui.abilityKeywords.Fire = " in _vlang and "\\nitems.Rune_Fireball.name = " in _vlang, "the rune language keys moved"
# the HUD icon: our 64 px art scaled 2x (nearest) to the 128 px the vanilla rune icons use
_vic = SA.png_decode(_ASSETS.read("Common/Icons/Abilities/Rune_Fireball.png"))
assert (_vic.w, _vic.h) == (128, 128), "the vanilla rune HUD icons are no longer 128 px"
_ICON_SRC = os.path.join(os.path.dirname(HERE), "art", "ability-icons", "Common", "Icons", "Abilities")


def _icon2x(png):
    im = SA.png_decode(png)
    out = SA.Img(im.w * 2, im.h * 2)
    for _y in range(out.h):
        for _x in range(out.w):
            out.put(_x, _y, im.get(_x // 2, _y // 2))
    return SA.png_encode(out)


RUNE_LANG = ["ui.abilityKeywords.SkyyClass = Class ability"]
for _a in RUNE_ABILS:
    _rid = rune_id(_a)
    assert re.fullmatch(r"SkyyAbility_[A-Za-z]+_[A-Za-z]+", _rid)
    for _id in (_rid, rune_root(_a), rune_cast(_a), rune_mark(_a)):
        assert not [n for n in _azn if n.rsplit("/", 1)[-1].split(".")[0] == _id], "vanilla already has an asset named " + _id
    _png = open(os.path.join(_ICON_SRC, _a[2], _a[0] + ".png"), "rb").read()
    assert SA.png_size(_png) == (64, 64), "%s icon is not 64 x 64" % _a[0]
    RUNE_FILES["Common/Icons/Items/SkyyClasses/%s.png" % _rid] = _png
    RUNE_FILES["Common/Icons/Abilities/%s.png" % _rid] = _icon2x(_png)
    RUNE_FILES["Server/Item/Items/SkyyClasses/%s.json" % _rid] = json.dumps({
        "TranslationProperties": {"Name": "server.items.%s.name" % _rid, "Description": "server.items.%s.description" % _rid},
        "Icon": "Icons/Items/SkyyClasses/%s.png" % _rid, "Quality": "Debug", "Model": RUNE_MODEL, "Texture": RUNE_TEX,
        "PlayerAnimationsId": "Item", "IconProperties": _vr["IconProperties"], "MaxStack": 1, "Scale": _vr["Scale"],
        "ItemSoundSetId": _vr["ItemSoundSetId"], "DropOnDeath": False,
        "Ability": {"Slot": "Core", "Cooldown": 0.25, "Cost": 0, "CostType": "None", "AbilityKeywords": ["SkyyClass"], "Cast": rune_root(_a)}},
        indent=2)
    RUNE_FILES["Server/Item/RootInteractions/SkyyClasses/%s.json" % rune_root(_a)] = json.dumps(
        {"Interactions": [rune_cast(_a)], "RequireNewClick": True}, indent=2)
    RUNE_FILES["Server/Item/Interactions/SkyyClasses/%s.json" % rune_cast(_a)] = json.dumps(
        {"Type": "ApplyEffect", "EffectId": rune_mark(_a)}, indent=2)
    RUNE_FILES["Server/Entity/Effects/SkyyClasses/%s.json" % rune_mark(_a)] = json.dumps({"Duration": 0.5}, indent=2)
    RUNE_LANG += ["items.%s.name = %s" % (_rid, _a[1]),
                  "items.%s.description = Your %s ability - the Ability 2 / 3 key casts it (crouch = your alts). It lives in your ability "
                  "slot and goes back there by itself." % (_rid, _a[2])]
RUNE_FILES["Server/Abilities/Keywords/SkyyClass.json"] = json.dumps({"Name": "server.ui.abilityKeywords.SkyyClass"}, indent=2)
for _l in RUNE_LANG:
    assert ("\\n" + _l.split(" = ")[0] + " ") not in _vlang, "vanilla already has " + _l.split(" = ")[0]
RUNE_FILES["Server/Languages/en-US/server.lang"] = "\\n".join(RUNE_LANG) + "\\n"
# no clash with another SET jar (its files / ids); the language file is shared by design (keys checked instead)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import deploy_set as _DS
for _m, _v in _DS.SET:
    if _m == "SkyyClasses":
        continue
    _jp = os.path.join(os.path.dirname(HERE), _m, "%s-%s.jar" % (_m, _v))
    if not os.path.isfile(_jp):
        continue
    with zipfile.ZipFile(_jp) as _jz:
        _jn = set(_jz.namelist())
        _hit = sorted(p for p in RUNE_FILES if p in _jn and p != "Server/Languages/en-US/server.lang")
        assert not _hit, "%s already ships %s" % (_m, _hit[:3])
        _ids = set(n.rsplit("/", 1)[-1].split(".")[0] for n in _jn)
        assert not [_i for _i in ("SkyyClass",) + tuple(rune_id(a) for a in RUNE_ABILS) if _i in _ids], "%s uses one of our ids" % _m
        if "Server/Languages/en-US/server.lang" in _jn:
            _ol = _jz.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
            assert not [_l for _l in RUNE_LANG if ("\\n" + _l.split(" = ")[0] + " ") in "\\n" + _ol], "%s uses one of our language keys" % _m
print("rune asset pack: %d files (%d runes + roots + cast steps + markers + icons, keyword SkyyClass, %d language lines)"
      % (len(RUNE_FILES), len(RUNE_ABILS), len(RUNE_LANG)))
abdefs = pool.makeClass(PKG + ".AbilDefs")
''')
rep('''F(abdefs, "public static final String[] DESCS = %s;" % jarr([ABIL_DESCS_[a[0]] for a in ABILS]))
''', '''F(abdefs, "public static final String[] DESCS = %s;" % jarr([ABIL_DESCS_[a[0]] for a in ABILS]))
# 0.1.22: the rune item / cast root / marker effect of each ability ("" = none: the passive)
F(abdefs, "public static final String[] RUNE = %s;" % jarr([rune_id(a) if not a[5] else "" for a in ABILS]))
F(abdefs, "public static final String[] ROOT = %s;" % jarr([rune_root(a) if not a[5] else "" for a in ABILS]))
F(abdefs, "public static final String[] MARK = %s;" % jarr([rune_mark(a) if not a[5] else "" for a in ABILS]))
F(abdefs, "public static final String[] NOUN = %s;" % jarr([AB_NOUN[a[0]] for a in ABILS]))
''')

# ================================================================================================ pure Java: AbilMath (levels), AbilModDefs, AbilCtx
rep('''# ---- AbilStore: loadout per profile (abilities/<pkey>.properties), memory cooldowns (pkey|ability), refusal throttle
''', r'''# ---- 0.1.22 ability levels by use (pure, bare-JVM tested): uses for level n = round(coef x n ^ exp) (n >= 2), levels up to max, the
# diminishing-returns gain (Skyy M8: "20+ (diminishing returns on ability levels.)"), the comma lists of the mods.* rows
M(abmath, r"""
public static long usesFor(int n, double coef, double exp) {
  if (n < 2) return 0L;
  long u = Math.round(coef * Math.pow((double) n, exp));
  return u < 1L ? 1L : u;
}""")
M(abmath, r"""
public static long levelStart(int lvl, double coef, double exp) {
  long t = 0L;
  for (int n = 2; n <= lvl; n++) t = t + usesFor(n, coef, exp);
  return t;
}""")
M(abmath, r"""
public static int levelOf(long uses, int max, double coef, double exp) {
  int l = 1;
  long acc = 0L;
  while (l < max) {
    long need = usesFor(l + 1, coef, exp);
    if (uses < acc + need) break;
    acc = acc + need;
    l++;
  }
  return l;
}""")
M(abmath, r"""
public static double bonusPct(int lvl, double per, long soft, long half) {
  if (lvl <= 1 || !(per > 0.0)) return 0.0;
  double b = 0.0;
  for (int k = 2; k <= lvl; k++) {
    if ((long) k <= soft) b = b + per;
    else if ((long) k <= half) b = b + per / 2.0;
    else b = b + per / 4.0;
  }
  return b;
}""")
M(abmath, r"""
public static int[] ints(String s, int[] dflt) {
  if (s == null) return dflt;
  String[] p = s.split(",");
  int[] out = new int[p.length];
  int n = 0;
  for (int i = 0; i < p.length; i++) {
    String t = p[i].trim();
    if (t.length() == 0) continue;
    try { out[n] = Integer.parseInt(t); } catch (Throwable x) { return dflt; }
    if (out[n] < 0) return dflt;
    n++;
  }
  if (n == 0) return dflt;
  int[] r = new int[n];
  for (int i = 0; i < n; i++) r[i] = out[i];
  return r;
}""")
M(abmath, r"""
public static int modLevel(long uses, int[] steps) {
  int l = 1;
  for (int i = 0; steps != null && i < steps.length; i++) if (uses >= (long) steps[i]) l++;
  return l;
}""")
# ---- AbilStore: loadout per profile (abilities/<pkey>.properties), memory cooldowns (pkey|ability), refusal throttle
''')
rep('''# ---- AbilJob: one delayed job (kind 1 = Meteor impact, 2 = a heal-over-time pulse series)
''', '''# ---- 0.1.22 AbilModDefs: the modifier tables (Skyy M8) + the tree node list helpers (SkyyTrees' tree:fn:abil text "A1,T4=10,PB2")
_MOD_J = [MOD_IDS.index(m) for a in ABILS for m in AB_MODS[a[0]]]
_MOD_S, _acc = [], 0
for _a in ABILS:
    _MOD_S.append(_acc)
    _acc += len(AB_MODS[_a[0]])
abmods = pool.makeClass(PKG + ".AbilModDefs")
F(abmods, "public static final String[] MID = %s;" % jarr(MOD_IDS))
F(abmods, "public static final String[] MNAME = %s;" % jarr([m[1] for m in MODS]))
F(abmods, "public static final boolean[] MSTACK = new boolean[] { %s };" % ", ".join("true" if m[2] else "false" for m in MODS))
for _i, _m in enumerate(MOD_IDS):
    F(abmods, "public static final int %s = %d;" % ({"Lingering": "LINGER", "Knockback": "KNOCK"}.get(_m, _m.upper()), _i))
F(abmods, "public static final int[] AMOD = new int[] { %s };" % ", ".join(str(x) for x in _MOD_J))
F(abmods, "public static final int[] AMS = new int[] { %s };" % ", ".join(str(x) for x in _MOD_S))
F(abmods, "public static final int[] AMN = new int[] { %s };" % ", ".join(str(len(AB_MODS[a[0]])) for a in ABILS))
F(abmods, "public static volatile String UNLOCK_SEEN = null;")
F(abmods, "public static volatile int[] UNLOCK = new int[] { 2, 4, 6, 8, 10 };")
F(abmods, "public static volatile String STEPS_SEEN = null;")
F(abmods, "public static volatile int[] STEPS = new int[] { 10, 30, 60, 100 };")
M(abmods, r"""
public static int find(String s) {
  if (s == null) return -1;
  String t = s.trim();
  if (t.length() == 0) return -1;
  for (int i = 0; i < MID.length; i++) if (MID[i].equalsIgnoreCase(t) || MNAME[i].equalsIgnoreCase(t)) return i;
  return -1;
}""")
M(abmods, r"""
public static int count(int ai) {
  return ai < 0 || ai >= AMN.length ? 0 : AMN[ai];
}""")
M(abmods, r"""
public static int at(int ai, int k) {
  if (k < 0 || k >= count(ai)) return -1;
  return AMOD[AMS[ai] + k];
}""")
M(abmods, r"""
public static int pos(int ai, int mi) {
  for (int k = 0; k < count(ai); k++) if (at(ai, k) == mi) return k;
  return -1;
}""")
M(abmods, r"""
public static int[] unlocks() {
  String t = @PKG@.AbilCfg.MOD_UNLOCK;
  if (t != UNLOCK_SEEN) { UNLOCK = @PKG@.AbilMath.ints(t, new int[] { 2, 4, 6, 8, 10 }); UNLOCK_SEEN = t; }
  return UNLOCK;
}""")
M(abmods, r"""
public static int unlockAt(int k) {
  int[] u = unlocks();
  if (k < 0) return 999;
  if (k < u.length) return u[k];
  return u[u.length - 1] + 2 * (k - u.length + 1);
}""")
M(abmods, r"""
public static int[] steps() {
  String t = @PKG@.AbilCfg.MOD_STEPS;
  if (t != STEPS_SEEN) { STEPS = @PKG@.AbilMath.ints(t, new int[] { 10, 30, 60, 100 }); STEPS_SEEN = t; }
  return STEPS;
}""")
M(abmods, r"""
public static int modLevel(long uses) {
  return @PKG@.AbilMath.modLevel(uses, steps());
}""")
# the uses a modifier still needs for its next level (0 = top level)
M(abmods, r"""
public static long modNext(long uses) {
  int[] st = steps();
  for (int i = 0; i < st.length; i++) if (uses < (long) st[i]) return (long) st[i] - uses;
  return 0L;
}""")
M(abmods, r"""
public static boolean csvHas(String csv, String id) {
  if (csv == null || id == null || csv.length() == 0) return false;
  String[] p = csv.split(",");
  for (int i = 0; i < p.length; i++) {
    String t = p[i].trim();
    int e = t.indexOf('=');
    String k = e >= 0 ? t.substring(0, e) : t;
    if (k.equals(id)) return true;
  }
  return false;
}""")
M(abmods, r"""
public static double csvAmt(String csv, String id, double dflt) {
  if (csv == null || id == null || csv.length() == 0) return 0.0;
  String[] p = csv.split(",");
  for (int i = 0; i < p.length; i++) {
    String t = p[i].trim();
    int e = t.indexOf('=');
    String k = e >= 0 ? t.substring(0, e) : t;
    if (!k.equals(id)) continue;
    if (e < 0) return dflt;
    try { return Double.parseDouble(t.substring(e + 1)); } catch (Throwable x) { return dflt; }
  }
  return 0.0;
}""")
# ---- 0.1.22 AbilCtx: ONE cast's resolved numbers (Skyy M8 levels + modifiers, the class-tree nodes) - made at the cast, carried by every
# job / zone the cast makes (AbilJob.cx / AbilZone.cx), so a running effect keeps its snapshot. CUR = the context of the code running on
# THIS thread (a ThreadLocal: every world has its own thread) - set around an executor, read by the shared helpers (Abil.cxm ...).
abctx = pool.makeClass(PKG + ".AbilCtx")
for _f in ("public static final ThreadLocal CUR = new ThreadLocal();",
           "public int ai;", "public int sh;", "public java.util.UUID u;", "public String pkey;", "public String cls;",
           "public int lvl;", "public double base;", "public double treeMain;", "public double main;", "public double radAdd;",
           "public double durMult;", "public double costMult;", "public double cdMult;", "public double costAdd;", "public long cdAdd;",
           "public double durAdd;", "public double radTree;", "public double pctAdd;", "public double hotAdd;",
           "public int m0;", "public int m1;", "public int l0;", "public int l1;", "public boolean echo;", "public double echoPct;",
           "public String tree;", "public double h;", "public double paid;", "public int hits;", "public java.util.HashSet seen;"):
    F(abctx, _f)
C(abctx, r"""
public AbilCtx() {
  this.ai = -1;
  this.m0 = -1;
  this.m1 = -1;
  this.base = 1.0;
  this.treeMain = 1.0;
  this.main = 1.0;
  this.durMult = 1.0;
  this.costMult = 1.0;
  this.cdMult = 1.0;
  this.tree = "";
  this.cls = "";
}""")
M(abctx, r"""
public static @PKG@.AbilCtx get() {
  Object o = CUR.get();
  return o instanceof @PKG@.AbilCtx ? (@PKG@.AbilCtx) o : null;
}""")
M(abctx, r"""
public static void put(@PKG@.AbilCtx c) {
  if (c == null) CUR.remove();
  else CUR.set(c);
}""")
M(abctx, r"""
public int cnt(int mi) {
  int n = 0;
  if (mi >= 0 && this.m0 == mi) n++;
  if (mi >= 0 && this.m1 == mi) n++;
  return n;
}""")
M(abctx, r"""
public int lv(int mi) {
  if (mi < 0) return 0;
  if (this.m0 == mi) return this.l0;
  if (this.m1 == mi) return this.l1;
  return 0;
}""")
# a doubled STACKABLE modifier counts its level twice (Skyy M8: "double the ricochet"); a non-stackable one never doubles
M(abctx, r"""
public int eff(int mi) {
  int c = cnt(mi);
  if (c == 0) return 0;
  int l = lv(mi);
  if (c > 1 && @PKG@.AbilModDefs.MSTACK[mi]) return l * c;
  return l;
}""")
M(abctx, "public boolean has(int mi) { return cnt(mi) > 0; }")
M(abctx, "public boolean node(String id) { return @PKG@.AbilModDefs.csvHas(this.tree, id); }")
M(abctx, "public double amt(String id, double dflt) { return @PKG@.AbilModDefs.csvAmt(this.tree, id, dflt); }")
M(abctx, r"""
public @PKG@.AbilCtx copy() {
  @PKG@.AbilCtx c = new @PKG@.AbilCtx();
  c.ai = this.ai; c.sh = this.sh; c.u = this.u; c.pkey = this.pkey; c.cls = this.cls; c.lvl = this.lvl; c.base = this.base;
  c.treeMain = this.treeMain; c.main = this.main; c.radAdd = this.radAdd; c.durMult = this.durMult; c.costMult = this.costMult;
  c.cdMult = this.cdMult; c.costAdd = this.costAdd; c.cdAdd = this.cdAdd; c.durAdd = this.durAdd; c.radTree = this.radTree;
  c.pctAdd = this.pctAdd; c.hotAdd = this.hotAdd; c.m0 = this.m0; c.m1 = this.m1; c.l0 = this.l0; c.l1 = this.l1; c.echo = this.echo;
  c.echoPct = this.echoPct; c.tree = this.tree; c.h = this.h; c.paid = this.paid;
  return c;
}""")
# the echo (Skyy M9 20-30 %): the same cast at pct strength, WITHOUT the other modifier (no Power+ / Radius+ / Duration+ ...), never
# echoed again, never counted; the class-tree nodes stay (they are how the ability works)
M(abctx, r"""
public @PKG@.AbilCtx echoOf(double pct) {
  @PKG@.AbilCtx c = copy();
  c.echo = true;
  c.echoPct = 0.0;
  c.main = this.base * this.treeMain * pct;
  c.m0 = -1;
  c.m1 = -1;
  c.l0 = 0;
  c.l1 = 0;
  c.radAdd = 0.0;
  c.durMult = 1.0;
  c.hits = 0;
  c.seen = null;
  return c;
}""")
# ---- AbilJob: one delayed job (kind 1 = Meteor impact, 2 = a heal-over-time pulse series)
''')
# ================================================================================================ AbilStore: the 0.1.22 memory maps + the use flush
rep('''           "MOVE", "GUARD", "CHAN", "FROZEN"):   # 0.1.18: UUID -> long[] {crouch since, air since}; UUID -> long[] {saves, next save at, last hurt};
                                                  # UUID -> the running beam (AbilJob); mob Ref -> long[] {a hit breaks it from, frozen until}
    F(abst, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
F(abst, "public static volatile long SAVES = 0L;")
''', '''           "MOVE", "GUARD", "CHAN", "FROZEN",   # 0.1.18: UUID -> long[] {crouch since, air since}; UUID -> long[] {saves, next save at, last hurt};
                                                  # UUID -> the running beam (AbilJob); mob Ref -> long[] {a hit breaks it from, frozen until}
           # 0.1.22: UUID -> Object[] {pkey, Long at, String tree csv} (tree:fn:abil, 1 s); "pkey|Id" -> Long last counted use; UUID -> Object[]
           # the mirror record {want0, want3, Long next check, Boolean in flight, Integer marker 0, Integer marker 3, Long last look}; UUID -> Long
           # the last hook press; "uuid|key" -> Long (the 120 ms repeat guard); UUID -> double[] {ward HP, until}; pkey -> Long first unsaved
           # use; UUID -> Long the vanilla-rune hint; UUID -> Boolean an InvClean is queued
           # 0.1.22 fix: UUID -> String the profile key a ward was given to; UUID -> int[] {failed rune writes in a row}
           # second fix round: pkey -> long[] {due, done} the "enable it in /tree" hint (once per profile per session)
           "TREEC", "LASTUSE", "MIRROR", "LASTHOOK", "LASTKEY", "WARD", "DIRTYAT", "VANTOLD", "CLEANQ", "WARDP", "MIRFAIL", "HINTED"):
    F(abst, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
F(abst, "public static volatile long SAVES = 0L;")
''')
rep('''public static boolean save(String k) {
  if (k == null) return false;
  DIRTY.remove(k);
  boolean ok = @PKG@.AbilSave.write(k);
  if (!ok && DATA.get(k) != null) DIRTY.put(k, Boolean.TRUE);''', '''public static boolean save(String k) {
  if (k == null) return false;
  DIRTY.remove(k);
  DIRTYAT.remove(k);   // 0.1.22: the use counts of k are on disk with it
  boolean ok = @PKG@.AbilSave.write(k);
  if (!ok && DATA.get(k) != null) {
    DIRTY.put(k, Boolean.TRUE);
    DIRTYAT.put(k, Long.valueOf(System.currentTimeMillis()));   // 0.1.22 fix: a failed write is tried again by the next 30 s flush
  }''')
rep('''F(abst, "public static volatile boolean SYNC = false;")   # HARNESS SEAM ONLY (false in the game): write on the caller's thread
''', '''F(abst, "public static volatile boolean SYNC = false;")   # HARNESS SEAM ONLY (false in the game): write on the caller's thread
# 0.1.22: ability USES change often (one per ability per 3 s) - they are kept in memory and written by ClassTick (30 s, never the world
# thread), at leave and at shutdown; markDirty only remembers the key and when its first unsaved change happened
M(abst, r"""
public static void markDirty(String k) {
  if (k == null) return;
  DIRTY.put(k, Boolean.TRUE);
  if (!DIRTYAT.containsKey(k)) DIRTYAT.put(k, Long.valueOf(System.currentTimeMillis()));
}""")
M(abst, r"""
public static int flushOld(long now, long ageMs) {
  int n = 0;
  java.util.Iterator it = new java.util.ArrayList(DIRTYAT.keySet()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    Object o = DIRTYAT.get(k);
    if (o instanceof Long && now - ((Long) o).longValue() < ageMs && now >= ((Long) o).longValue()) continue;
    if (save(k)) n++;
  }
  return n;
}""")
# 0.1.22 fix: every key of a map that starts with that player's uuid (LASTUSE "pkey|Id", LASTKEY "uuid|key") - at leave
M(abst, r"""
public static int dropKeysOf(java.util.concurrent.ConcurrentHashMap m, java.util.UUID u) {
  if (m == null || u == null) return 0;
  String p = u.toString();
  int n = 0;
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object key = it.next();
    if (String.valueOf(key).startsWith(p)) { it.remove(); n++; }
  }
  return n;
}""")
# Skyy M5 "Always reset on relog": every cooldown of every profile of that player (keys "<pkey>|<id>", pkey = uuid or uuid-pN)
M(abst, r"""
public static int clearCdOf(java.util.UUID u) {
  if (u == null) return 0;
  String p = u.toString();
  int n = 0;
  java.util.Iterator it = CD.keySet().iterator();
  while (it.hasNext()) {
    Object key = it.next();
    if (String.valueOf(key).startsWith(p)) { it.remove(); CDLEN.remove(key); n++; }
  }
  return n;
}""")
''')
# ================================================================================================ the new Abil methods (0.1.22)
# Each one is added as a STUB right after the Abil fields (a default return) and gets its real body at the end of the class build
# (CtMethod.setBody): every old executor can call them and they can call every old executor - no ordering problems.
LATE_JAVA = []


def late(src):
    LATE_JAVA.append(src.strip("\n"))


# ---- the cast context of THIS thread (AbilCtx.CUR) - neutral without one
late(r'''
public static double cxm() {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  return c == null ? 1.0 : c.main;
}''')
late(r'''
public static double cxr() {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  return c == null ? 0.0 : c.radAdd + c.radTree;
}''')
late(r'''
public static double cxd() {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  return c == null ? 1.0 : c.durMult;
}''')
late(r'''
public static double cxds(double secs) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  if (c == null) return secs;
  double v = secs * c.durMult + c.durAdd;
  return v < 0.5 ? 0.5 : v;
}''')
late(r'''
public static boolean cxNode(String cls, String id) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  return c != null && cls.equals(c.cls) && c.node(id);
}''')
late(r'''
public static void seenAdd(@PKG@.AbilCtx c, Object t) {
  if (c == null || t == null) return;
  if (c.seen == null) c.seen = new java.util.HashSet();
  c.seen.add(t);
}''')
# SECOND FIX ROUND (critic: fail-open): a tree read that FAILED (SkyyTrees answers "!err", or a throw here) is never cached and never
# means "no gate": the last good answer of this profile (any age) is kept, else "" (fail closed: nothing enabled until the next read)
late(r'''
public static String treeKeep(java.util.UUID u, String k) {
  try {
    Object o = @PKG@.AbilStore.TREEC.get(u);
    if (o instanceof Object[]) {
      Object[] a = (Object[]) o;
      if (k != null && k.equals(a[0])) return (String) a[2];
    }
  } catch (Throwable t) { }
  TREE_ERR = TREE_ERR + 1L;
  return "";
}''')
# ---- the class tree (SkyyTrees 0.3.7 tree:fn:abil: UUID -> the intact class nodes "A1,A2,M1A,T4=10,..."; null = class trees off / none)
late(r'''
public static String treeCsv(java.util.UUID u) {
  if (u == null) return null;
  String k = null;
  try {
    long now = System.currentTimeMillis();
    k = @PKG@.ClassCfg.pkey(u);
    Object o = @PKG@.AbilStore.TREEC.get(u);
    if (o instanceof Object[]) {
      Object[] a = (Object[]) o;
      long at = ((Long) a[1]).longValue();
      if (k.equals(a[0]) && now - at < 1000L && now >= at) return (String) a[2];
    }
    String csv = null;
    Object f = @PKG@.ClassCfg.bridge().get("tree:fn:abil");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String) csv = (String) r;
    }
    if ("!err".equals(csv)) return treeKeep(u, k);
    @PKG@.AbilStore.TREEC.put(u, new Object[] { k, Long.valueOf(now), csv });
    return csv;
  } catch (Throwable t) { return treeKeep(u, k); }
}''')
late(r'''
public static int lineOf(int ai) {
  if (ai < 0) return 0;
  int t = @PKG@.AbilDefs.TIER[ai];
  return t >= 3 ? 4 : t + 1;
}''')
# abil.treeGate: with class trees on (a csv), an ability needs its A<line> node; no csv = no gate (today's behaviour)
late(r'''
public static boolean lineOn(String csv, int ai) {
  if (!@PKG@.AbilCfg.TREE_GATE || csv == null || ai < 0) return true;
  return @PKG@.AbilModDefs.csvHas(csv, "A" + lineOf(ai));
}''')
late(r'''
public static int modSlots(String csv, int ai) {
  if (!@PKG@.AbilCfg.TREE_GATE || csv == null || ai < 0) return 2;
  int l = lineOf(ai);
  int n = 0;
  if (@PKG@.AbilModDefs.csvHas(csv, "M" + l + "A")) n++;
  if (@PKG@.AbilModDefs.csvHas(csv, "M" + l + "B")) n++;
  return n;
}''')
# ---- ability levels + modifiers from the abilities file (u.<Id>, m.<Id>.<Mod>, e.<Id>)
late(r'''
public static long numOf(java.util.Properties p, String key) {
  try {
    String v = p == null ? null : p.getProperty(key);
    if (v == null) return 0L;
    long n = Long.parseLong(v.trim());
    return n < 0L ? 0L : n;
  } catch (Throwable t) { return 0L; }
}''')
late(r'''
public static int alvl(long uses) {
  if (!@PKG@.AbilCfg.LEVELS) return 1;
  return @PKG@.AbilMath.levelOf(uses, (int) @PKG@.AbilCfg.MAX_LVL, @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP);
}''')
late(r'''
public static double lvlMult(int lvl) {
  return 1.0 + @PKG@.AbilMath.bonusPct(lvl, @PKG@.AbilCfg.PER_LEVEL, @PKG@.AbilCfg.SOFT_LVL, @PKG@.AbilCfg.HALF_LVL) / 100.0;
}''')
late(r'''
public static String[] eqOf(java.util.Properties p, String id) {
  String v = p == null ? "" : p.getProperty("e." + id, "");
  String[] r = new String[] { "", "" };
  int c = v.indexOf(',');
  if (c < 0) r[0] = v.trim();
  else { r[0] = v.substring(0, c).trim(); r[1] = v.substring(c + 1).trim(); }
  return r;
}''')
# the modifiers that WORK in the 2 slots now: offered by the ability, unlocked at this level, inside the slots the tree gives, the double rule
late(r'''
public static int[] equipped(java.util.Properties p, int ai, int lvl, int slots) {
  int[] r = new int[] { -1, -1 };
  if (ai < 0) return r;
  String id = @PKG@.AbilDefs.IDS[ai];
  String[] e = eqOf(p, id);
  for (int j = 0; j < 2 && j < slots; j++) {
    int mi = @PKG@.AbilModDefs.find(e[j]);
    int k = @PKG@.AbilModDefs.pos(ai, mi);
    if (mi < 0 || k < 0 || lvl < @PKG@.AbilModDefs.unlockAt(k)) continue;
    if (j == 1 && r[0] == mi) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) continue;
      if (@PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[mi])) < 2) continue;
    }
    r[j] = mi;
  }
  return r;
}''')
# THE TWO UPGRADE LAYERS, class-tree side (Class-Tree-Paths.md 3 + 4; numbers that change HOW the ability works or trade off)
late(r'''
public static void treeApply(@PKG@.AbilCtx c) {
  if (c == null || c.tree == null || c.tree.length() == 0 || c.ai < 0) return;
  int ai = c.ai;
  boolean mage = "Mage".equals(c.cls);
  boolean priest = "Priest".equals(c.cls);
  if (!mage && !priest) return;
  double q = c.amt("T6", 5.0);
  if (q > 0.0) c.cdMult = c.cdMult * (1.0 - (q > 90.0 ? 90.0 : q) / 100.0);
  if (mage) {
    if (ai == @PKG@.AbilDefs.METEOR && c.node("PC5")) c.cdAdd = c.cdAdd + 4000L;
    if (ai == @PKG@.AbilDefs.STARF && c.node("PB5")) c.cdAdd = c.cdAdd + 4000L;
    if (ai == @PKG@.AbilDefs.BEAM && c.node("PC4")) c.costAdd = c.costAdd + 10.0;
    if (ai == @PKG@.AbilDefs.BEAM && c.node("PB4")) c.costMult = c.costMult * 1.05;
    if (ai == @PKG@.AbilDefs.MANAB) {
      double bl = c.amt("T4", 10.0);
      if (bl > 0.0) c.treeMain = c.treeMain * (1.0 + bl / 100.0);
      if (c.node("PC3")) c.treeMain = c.treeMain * 0.75;
      if (c.node("PA3")) c.durAdd = c.durAdd - 2.0;
    }
  }
  if (priest) {
    if (ai == @PKG@.AbilDefs.SACRED) {
      if (c.node("T3")) { c.radTree = c.radTree + 1.5; c.pctAdd = c.pctAdd + c.amt("T3", 2.0); }
      if (c.node("T4")) c.hotAdd = c.hotAdd + c.amt("T4", 10.0);
      if (c.node("PA1")) { c.costAdd = c.costAdd + 5.0; c.treeMain = c.treeMain * 0.9; }
      if (c.node("PA5")) c.cdAdd = c.cdAdd + 4000L;
    }
    if (ai == @PKG@.AbilDefs.BUBBLE) {
      if (c.node("PB1")) c.treeMain = c.treeMain * 0.85;
      if (c.node("PB3")) c.durAdd = c.durAdd - 2.0;   // fix round: Layered Ward (Priest PB3) - 2 s shorter
      if (c.node("PB5")) c.durAdd = c.durAdd - 1.0;
    }
    if (ai == @PKG@.AbilDefs.SANCT && c.node("PA4")) { c.radTree = c.radTree + 2.0; c.durAdd = c.durAdd - 2.0; }
    if (ai == @PKG@.AbilDefs.GRACE && c.node("PA3")) c.pctAdd = c.pctAdd - 10.0;
  }
}''')
# ONE cast's numbers (Skyy M8): level (diminishing returns) x Power+ x the tree; Radius+, Duration+, Efficiency, Echo; the tree's changes
late(r'''
public static @PKG@.AbilCtx ctxFor(java.util.UUID u, String k, int ai, int sh, String csv) {
  @PKG@.AbilCtx c = new @PKG@.AbilCtx();
  c.ai = ai;
  c.sh = sh;
  c.u = u;
  c.pkey = k;
  c.tree = csv == null ? "" : csv;
  if (ai < 0) return c;
  c.cls = @PKG@.ClassDefs.NAMES[@PKG@.AbilDefs.CLS[ai]];
  java.util.Properties p = k == null ? new java.util.Properties() : @PKG@.AbilStore.load(k);
  String id = @PKG@.AbilDefs.IDS[ai];
  c.lvl = alvl(numOf(p, "u." + id));
  c.base = lvlMult(c.lvl);
  if (@PKG@.AbilCfg.MODS_ON) {
    int[] eq = equipped(p, ai, c.lvl, modSlots(csv, ai));
    c.m0 = eq[0];
    c.m1 = eq[1];
    c.l0 = c.m0 < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[c.m0]));
    c.l1 = c.m1 < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[c.m1]));
  }
  double pw = 1.0 + @PKG@.AbilCfg.MOD_POWER * (double) c.eff(@PKG@.AbilModDefs.POWER) / 100.0;
  c.radAdd = (ai == @PKG@.AbilDefs.GUARD ? 10.0 : 1.0) * @PKG@.AbilCfg.MOD_RADIUS * (double) c.eff(@PKG@.AbilModDefs.RADIUS);
  c.durMult = 1.0 + @PKG@.AbilCfg.MOD_DUR * (double) c.eff(@PKG@.AbilModDefs.DURATION) / 100.0;
  double e = @PKG@.AbilCfg.MOD_EFF * (double) c.eff(@PKG@.AbilModDefs.EFFICIENCY) / 100.0;
  if (e > 0.5) e = 0.5;
  c.costMult = 1.0 - e;
  if (c.has(@PKG@.AbilModDefs.ECHO)) c.echoPct = (@PKG@.AbilCfg.ECHO_BASE + @PKG@.AbilCfg.ECHO_STEP * (double) (c.lv(@PKG@.AbilModDefs.ECHO) - 1)) / 100.0;
  treeApply(c);
  c.main = c.base * pw * c.treeMain;
  return c;
}''')
late(r'''
public static double costMana(@PKG@.AbilCtx c, int ai, int sh) {
  double m = @PKG@.AbilDefs.mana(ai, sh);
  if (c == null) return m;
  double v = m * c.costMult + c.costAdd;
  return v < 0.0 ? 0.0 : v;
}''')
late(r'''
public static double costStam(@PKG@.AbilCtx c, int ai, int sh) {
  double m = @PKG@.AbilDefs.stamina(ai, sh);
  if (c == null) return m;
  return m * (c.costMult > 1.0 ? 1.0 : c.costMult);
}''')
late(r'''
public static long cdCx(@PKG@.AbilCtx c, int ai, int sh) {
  long b = @PKG@.AbilDefs.cdMs(ai, sh);
  if (c == null) return b;
  long v = Math.round((double) b * c.cdMult) + c.cdAdd;
  return v < 0L ? 0L : v;
}''')
late(r'''
public static String levelText(int ai, int lvl, long uses) {
  if (ai < 0) return "";
  if (!@PKG@.AbilCfg.LEVELS) return "Lv 1";
  int mx = (int) @PKG@.AbilCfg.MAX_LVL;
  if (lvl >= mx) return "Lv " + lvl + " (top)";
  long a = @PKG@.AbilMath.levelStart(lvl, @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP);
  long b = @PKG@.AbilMath.levelStart(lvl + 1, @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP);
  return "Lv " + lvl + " - " + (uses - a) + " / " + (b - a) + " uses";
}''')
late(r'''
public static String gainText(int ai, int lvl) {
  if (ai < 0) return "";
  return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilMath.bonusPct(lvl, @PKG@.AbilCfg.PER_LEVEL, @PKG@.AbilCfg.SOFT_LVL, @PKG@.AbilCfg.HALF_LVL)) + " % " + @PKG@.AbilDefs.NOUN[ai];
}''')
# the modifiers an ability unlocked on its way from level a to b
late(r'''
public static String newMods(int ai, int a, int b) {
  String s = "";
  for (int k = 0; k < @PKG@.AbilModDefs.count(ai); k++) {
    int at = @PKG@.AbilModDefs.unlockAt(k);
    if (at > a && at <= b) s = s + (s.length() > 0 ? ", " : "") + @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.at(ai, k)];
  }
  return s;
}''')
# ONE COUNTED USE (Skyy 2026-10-04 "ability upgrade points are gained by using the ability" + M8): the ability did something; at most one per
# ability per abil.useEvery; never an echo; never after a profile switch. +1 use, +1 per equipped modifier (+2 doubled); kept in memory,
# written by ClassTick (30 s). A level-up line names the modifiers it unlocked.
late(r'''
public static String used(java.util.UUID u, String k, int ai, @PKG@.AbilCtx cx) {
  try {
    if (u == null || k == null || ai < 0 || !@PKG@.AbilCfg.LEVELS) return "off";
    if (cx != null && cx.echo) return "echo";
    if (!k.equals(@PKG@.ClassCfg.pkey(u))) return "switched";
    long now = System.currentTimeMillis();
    String id = @PKG@.AbilDefs.IDS[ai];
    String key = k + "|" + id;
    Object o = @PKG@.AbilStore.LASTUSE.get(key);
    long gap = Math.round(@PKG@.AbilCfg.USE_EVERY * 1000.0);
    if (o instanceof Long && now - ((Long) o).longValue() < gap && now >= ((Long) o).longValue()) return "soon";
    java.util.Properties p = @PKG@.AbilStore.load(k);
    long uses = numOf(p, "u." + id);
    int l0 = alvl(uses);
    int[] eq = @PKG@.AbilCfg.MODS_ON ? equipped(p, ai, l0, modSlots(treeCsv(u), ai)) : new int[] { -1, -1 };
    String[] ks = new String[3];
    String[] vs = new String[3];
    ks[0] = "u." + id;
    vs[0] = String.valueOf(uses + 1L);
    int n = 1;
    String up = "";
    for (int j = 0; j < 2; j++) {
      int mi = eq[j];
      if (mi < 0) continue;
      if (j == 1 && eq[0] == mi) continue;
      int add = (eq[0] == mi && eq[1] == mi) ? 2 : 1;
      String mk = "m." + id + "." + @PKG@.AbilModDefs.MID[mi];
      long mu = numOf(p, mk);
      int ml0 = @PKG@.AbilModDefs.modLevel(mu);
      int ml1 = @PKG@.AbilModDefs.modLevel(mu + (long) add);
      ks[n] = mk;
      vs[n] = String.valueOf(mu + (long) add);
      n++;
      if (ml1 > ml0) up = up + (up.length() > 0 ? ", " : "") + @PKG@.AbilModDefs.MNAME[mi] + " Lv " + ml1;
    }
    String[] k2 = new String[n];
    String[] v2 = new String[n];
    for (int i = 0; i < n; i++) { k2[i] = ks[i]; v2[i] = vs[i]; }
    if (!@PKG@.AbilStore.set(k, k2, v2)) return "unread";
    @PKG@.AbilStore.LASTUSE.put(key, Long.valueOf(now));
    @PKG@.AbilStore.markDirty(k);
    USES = USES + 1L;
    int l1 = alvl(uses + 1L);
    @PR@ pr = prOf(u);
    if (pr != null && l1 > l0) {
      String nu = newMods(ai, l0, l1);
      say(pr, @PKG@.AbilDefs.NAMES[ai] + " reached Lv " + l1 + "! " + gainText(ai, l1) + "." + (nu.length() > 0 ? " New modifier: " + nu + " - equip it in /tree class." : ""));
    }
    if (pr != null && up.length() > 0) say(pr, @PKG@.AbilDefs.NAMES[ai] + " modifier up: " + up + ".");
    return "use " + (uses + 1L) + (l1 > l0 ? " level " + l1 : "") + (up.length() > 0 ? " mods " + up : "");
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("ability use count failed: " + t); return "failed"; }
}''')
# Brilliance (Mage PB4): a cast whose hits reach 3+ different enemies gives 10 % of its Mana back (once per cast)
late(r'''
public static double brilliance(@PKG@.AbilCtx c, @CAC@ acc, @REF@ cr) {
  if (c == null || c.echo || !(c.paid > 0.0) || !"Mage".equals(c.cls) || !c.node("PB4")) return 0.0;
  if (c.seen == null || c.seen.size() < 3 || cr == null || !cr.isValid()) return 0.0;
  double back = c.paid * 0.10;
  c.paid = 0.0;
  @ESM@ m = map(acc, cr);
  if (m != null) m.addStatValue(@DST@.getMana(), (float) back);
  @PR@ pr = prOf(c.u);
  if (pr != null) say(pr, "Brilliance: +" + @PKG@.AbilMath.fmt(back) + " Mana back (" + c.seen.size() + " enemies hit).");
  return back;
}''')
# ---- METEOR: the job(s) of one meteor (Split = 3 smaller ones around the spot; Echo = the same meteor again ECHO_DELAY after it lands)
late(r'''
public static int meteorSpawn(@PKG@.AbilWorld aw, java.util.UUID u, String k, double x, double y, double z, double baseR, double power, long delay, long now, @CAC@ acc) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double h = c == null ? 0.0 : c.h;
  double amt = h * power * cxm();
  double r = baseR + cxr();
  int n = 0;
  particle(FX_MARK, x, y + 0.1, z, acc);
  if (c != null && c.has(@PKG@.AbilModDefs.SPLIT)) {
    double pct = (40.0 + 5.0 * (double) (c.lv(@PKG@.AbilModDefs.SPLIT) - 1)) / 100.0;
    for (int i = 0; i < 3; i++) {
      double a = 2.0943951023931953 * (double) i + 0.5235987755982988;
      double sx = x + Math.cos(a) * 2.0;
      double sz = z + Math.sin(a) * 2.0;
      @PKG@.AbilJob j = new @PKG@.AbilJob(1, now + delay + (long) (i * 150), u, "Meteor", sx, y, sz, r * 0.75, amt * pct);
      j.pkey = k;
      j.ai = @PKG@.AbilDefs.METEOR;
      if (i > 0) particle(FX_MARK, sx, y + 0.1, sz, acc);
      aw.add(j);
      n++;
    }
  } else {
    @PKG@.AbilJob j = new @PKG@.AbilJob(1, now + delay, u, "Meteor", x, y, z, r, amt);
    j.pkey = k;
    j.ai = @PKG@.AbilDefs.METEOR;
    aw.add(j);
    n++;
  }
  if (c != null && c.echoPct > 0.0 && !c.echo) {
    @PKG@.AbilCtx e = c.echoOf(c.echoPct);
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + delay + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0), u, "Meteor", x, y, z, baseR + c.radTree, h * power * e.main);
    ej.pkey = k;
    ej.ai = @PKG@.AbilDefs.METEOR;
    ej.sh = c.sh;
    ej.cx = e;
    aw.add(ej);
  }
  return n;
}''')
# Lingering (job kind 9): the ground burns, one hit a second on every enemy in it
late(r'''
public static boolean burnTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) return false;
  particle(FX_MARK, j.x, j.y + 0.1, j.z, cb);
  java.util.List l = near(cb, j.x, j.y, j.z, j.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    if (hit(cb, t, cr, j.caster, j.amount, "Meteor")) n++;
  }
  j.hits = j.hits < 0 ? n : j.hits + n;
  j.left = j.left - 1;
  j.at = j.at + (j.every > 0L ? j.every : 1000L);
  return j.left > 0;
}''')
# ECHO (job kind 10, Skyy M9): the same executor again at reduced strength (the job's context is the echo's: echo = true, no modifiers)
late(r'''
public static boolean echoRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) { LAST_ECHO = "gone"; return false; }
  @PR@ pr = prOf(j.caster);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  ECHOES = ECHOES + 1L;
  if (j.ai == @PKG@.AbilDefs.METEOR) {
    @PKG@.AbilJob m = new @PKG@.AbilJob(1, now, j.caster, "Meteor", j.x, j.y, j.z, j.r, j.amount);
    m.pkey = j.pkey;
    m.ai = j.ai;
    m.cx = j.cx;
    particle(FX_MARK, j.x, j.y + 0.1, j.z, cb);
    LAST_ECHO = "meteor:" + meteorImpact(m, st, cb);
    return false;
  }
  if (j.ai == @PKG@.AbilDefs.STARF) {
    if (aw != null) aw.add(starJob(j.caster, j.pkey, new double[] { j.x, j.y, j.z }, j.r, (long) j.total, j.secs, j.amount, 0, now));
    if (pr != null) say(pr, "Echo: a weaker Starfall.");
    LAST_ECHO = "stars";
    return false;
  }
  if (j.ai == @PKG@.AbilDefs.SACRED) {
    LAST_ECHO = "heal:" + healAt(pr, st, cb, cr, j.caster, new double[] { j.x, j.y, j.z }, j.r, 1.0, 0.0, now, j.pkey, j.sh);
    return false;
  }
  if (j.ai == @PKG@.AbilDefs.GRACE) {
    LAST_ECHO = "grace:" + graceRun(pr, st, cb, cr, j.caster, j.sh, j.pkey);
    return false;
  }
  return false;
}''')
late(r'''
public static void echoJob(@PKG@.AbilWorld aw, @PKG@.AbilCtx c, int ai, int sh, double x, double y, double z, double r, double amount, long at) {
  if (aw == null || c == null || c.echo || !(c.echoPct > 0.0)) return;
  @PKG@.AbilCtx e = c.echoOf(c.echoPct);
  @PKG@.AbilJob j = new @PKG@.AbilJob(10, at, c.u, @PKG@.AbilDefs.IDS[ai], x, y, z, r, amount);
  j.pkey = c.pkey;
  j.ai = ai;
  j.sh = sh;
  j.cx = e;
  aw.add(j);
}''')
# ---- LAYERED WARD (Priest PB3, fix round): the bubble's HP is one bar of two layers - the outer half soaks first; while the bar is inside
# the inner half it regrows 3 % of the bubble's HP a second up to the inner half's top. Heal pulses already earned stay earned.
late(r'''
public static double layerRegrow(@PKG@.AbilZone z, long now) {
  if (z == null || z.nextHeal <= 0L || !(z.hpMax > 0.0) || !(z.hp > 0.0)) return 0.0;
  z.nextHeal = now + 1000L;
  double inner = z.hpMax * 0.5;
  if (z.hp >= inner) return 0.0;
  double add = z.hpMax * 0.03;
  if (z.hp + add > inner) add = inner - z.hp;
  z.hp = z.hp + add;
  return add;
}''')
# ---- WARD (Mana Barrier / Martyr's Grace / Guardian Spirit): a small shield on a player (UUID -> {HP, until}); the strongest one is kept
late(r'''
public static double wardGive(java.util.UUID t, double hp, long until) {
  if (t == null || !(hp > 0.0)) return 0.0;
  Object o = @PKG@.AbilStore.WARD.get(t);
  double[] w = null;
  if (o instanceof double[]) w = (double[]) o;
  long now = System.currentTimeMillis();
  String tk = @PKG@.ClassCfg.pkey(t);
  Object wp = @PKG@.AbilStore.WARDP.get(t);
  if (w != null && (long) w[1] > now && w[0] >= hp && tk.equals(wp)) return 0.0;
  @PKG@.AbilStore.WARD.put(t, new double[] { hp, (double) until });
  @PKG@.AbilStore.WARDP.put(t, tk);   // 0.1.22 fix: the ward belongs to this profile only
  return hp;
}''')
# you (and your party with party = true) within rad of x y z get a ward of pct % of their max Health
late(r'''
public static int wardArea(@CAC@ acc, java.util.UUID caster, double x, double y, double z, double rad, double pct, long until) {
  int n = 0;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ p = (@PR@) it.next();
    if (p == null || !p.isValid()) continue;
    java.util.UUID pu = p.getUuid();
    if (pu == null || (!pu.equals(caster) && !@PKG@.HealTask.inParty(caster, pu))) continue;
    @REF@ r = p.getReference();
    if (r == null || !r.isValid()) continue;
    @VEC@ q = null;
    try { q = pos(acc, r); } catch (Throwable t0) { q = null; }
    if (q == null || !@PKG@.AbilMath.inRange(q.x - x, q.y - y, q.z - z, rad)) continue;
    double mx = max(map(acc, r), @DST@.getHealth());
    if (mx > 0.0 && wardGive(pu, mx * pct / 100.0, until) > 0.0) n++;
  }
  return n;
}''')
# AbilShieldSys (the Filter group, after the zones, before Guardian Spirit): a ward soaks the hit
late(r'''
public static String wardHit(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  if (d == null || r == null || d.isCancelled()) return null;
  float a0 = d.getAmount();
  if (!(a0 > 0.0f)) return null;
  @DCS@ cause = null;
  try { cause = d.getCause(); } catch (Throwable t) { cause = null; }
  if (cause != null && (cause == @DCS@.OUT_OF_WORLD || cause == @DCS@.COMMAND)) return null;
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  java.util.UUID u = ((@PR@) po).getUuid();
  Object o = u == null ? null : @PKG@.AbilStore.WARD.get(u);
  if (!(o instanceof double[])) return null;
  double[] w = (double[]) o;
  if ((long) w[1] <= now || !(w[0] > 0.0)) { @PKG@.AbilStore.WARD.remove(u); @PKG@.AbilStore.WARDP.remove(u); return "expired"; }
  if (!@PKG@.ClassCfg.pkey(u).equals(@PKG@.AbilStore.WARDP.get(u))) { @PKG@.AbilStore.WARD.remove(u); @PKG@.AbilStore.WARDP.remove(u); return "otherprofile"; }   // 0.1.22 fix
  double take = (double) a0 < w[0] ? (double) a0 : w[0];
  w[0] = w[0] - take;
  if (!(w[0] > 0.01)) @PKG@.AbilStore.WARD.remove(u);
  double left = (double) a0 - take;
  if (left <= 1.0E-3) { d.setAmount(0.0f); d.setCancelled(true); return "ward:" + @PKG@.AbilMath.fmt(take) + " cancelled"; }
  d.setAmount((float) left);
  return "ward:" + @PKG@.AbilMath.fmt(take) + " left=" + @PKG@.AbilMath.fmt(left);
}''')
# ---- pushes and pulls (Knockback+, Arch-Mage's star well): one Velocity Set with the vanilla dagger dash config (SkyyArmory's knockback way)
late(r'''
public static @VCF@ dashCfg() {
  @VCF@ c = DASH;
  if (c != null) return c;
  try {
    c = new @VCF@();
    c.setAirResistance(DASH_AIR);
    c.setAirResistanceMax(DASH_AIRMAX);
    c.setGroundResistance(DASH_GROUND);
    c.setGroundResistanceMax(DASH_GROUNDMAX);
    c.setThreshold(DASH_THRES);
    c.setStyle(@VTS@.Exp);
    DASH = c;
    return c;
  } catch (Throwable t) { return null; }
}''')
late(r'''
public static boolean push(@CAC@ acc, @REF@ t, double vx, double vy, double vz) {
  java.util.List l = PUSHES;
  if (l != null) l.add(new double[] { vx, vy, vz });
  try {
    if (l != null || t == null || !t.isValid()) return l != null;
    Object o = acc.getComponent(t, @VEL@.getComponentType());
    if (!(o instanceof @VEL@)) return false;
    ((@VEL@) o).addInstruction(new @VEC@(vx, vy, vz), dashCfg(), @CVT@.Set);
    return true;
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("an ability push failed: " + x); return false; }
}''')
# Knockback+ (Mana Barrier): the dome bursts when it ends - enemies within its radius + 1 fly outward (Skyy M6: they may fall)
late(r'''
public static int knockArea(@CB@ cb, @REF@ cr, double x, double y, double z, double rad, double force) {
  java.util.List l = near(cb, x, y, z, rad);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null) continue;
    double dx = q.x - x;
    double dz = q.z - z;
    double d = Math.sqrt(dx * dx + dz * dz);
    if (d < 0.1) { dx = 1.0; dz = 0.0; d = 1.0; }
    if (push(cb, t, dx / d * force, force * 0.4, dz / d * force)) n++;
  }
  particle(FX_BREAK, x, y + 1.0, z, cb);
  return n;
}''')
# damage on every enemy within rad (Charged Dome, Sunburst, Aegis); returns the enemies hit
late(r'''
public static int burst(@CB@ cb, @REF@ cr, java.util.UUID u, double x, double y, double z, double rad, double amount, String what) {
  if (!(amount > 0.0)) return 0;
  java.util.List l = near(cb, x, y, z, rad);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    if (hit(cb, t, cr, u, amount, what)) n++;
  }
  particle(FX_HIT, x, y + 0.5, z, cb);
  return n;
}''')
# Arch-Mage (Mage PC5) star well (zone kind 7): every zone tick, enemies within its radius are pulled toward the centre
late(r'''
public static boolean wellTick(@PKG@.AbilZone z, @CB@ cb, long now) {
  if (z.ended || now >= z.until) return false;
  @REF@ cr = casterRef(cb, z.caster);
  if (cr == null || !cr.isValid()) return false;
  java.util.List l = near(cb, z.x, z.y, z.z, z.r);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t) || !enemy(cb, t, cr)) continue;
    @VEC@ q = pos(cb, t);
    if (q == null) continue;
    double dx = z.x - q.x;
    double dz = z.z - q.z;
    double d = Math.sqrt(dx * dx + dz * dz);
    if (d < 0.6) continue;
    push(cb, t, dx / d * 6.0, 0.2, dz / d * 6.0);
    z.hits = z.hits + 1;
  }
  if (now >= z.nextFx) { z.nextFx = now + 500L; particle(FX_STAR, z.x, z.y + 0.5, z.z, cb); }
  return true;
}''')
# Cleanse (Priest PA1 / PA4): the vanilla debuffs off one player; returns how many were on
late(r'''
public static int cleanse(@CAC@ acc, @REF@ r) {
  int n = 0;
  for (int i = 0; i < CLEANSE.length; i++) if (hasFx(acc, r, CLEANSE[i]) && unfreezeOne(acc, r, CLEANSE[i])) n++;
  return n;
}''')
late(r'''
public static int cleanseIn(@ST@ st, @CAC@ acc, @PKG@.AbilZone z) {
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  inside(st, acc, z, us, rs);
  int n = 0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    if (!t.equals(z.caster) && !@PKG@.HealTask.inParty(z.caster, t)) continue;
    n = n + cleanse(acc, (@REF@) rs.get(i));
  }
  return n;
}''')
# a placed zone that follows its caster (Follow modifier, Mage Phase Step)
late(r'''
public static boolean zoneFollow(@PKG@.AbilZone z, @CB@ cb) {
  @REF@ cr = casterRef(cb, z.caster);
  if (cr == null || !cr.isValid()) return false;
  @VEC@ p = pos(cb, cr);
  if (p == null) return false;
  z.x = p.x;
  z.y = p.y;
  z.z = p.z;
  return true;
}''')
# Thorned Bubble (Priest PB1): an attack the bubble soaked hurts its attacker 0.5 H
late(r'''
public static boolean thorns(@CB@ buf, @PKG@.AbilZone z, @DMG@ d) {
  if (z == null || z.cx == null || !"Priest".equals(z.cx.cls) || !z.cx.node("PB1") || !(z.h > 0.0)) return false;
  try {
    if (!(d.getSource() instanceof @DENT@)) return false;
    @REF@ att = ((@DENT@) d.getSource()).getRef();
    @REF@ cr = casterRef(buf, z.caster);
    if (att == null || !att.isValid() || cr == null || !cr.isValid() || !enemy(buf, att, cr)) return false;
    return hit(buf, att, cr, z.caster, 0.5 * z.h, "ShieldBubble");
  } catch (Throwable t) { return false; }
}''')
# Shield Bubble Echo: once, where the bubble ended or broke, a weaker bubble forms
late(r'''
public static @PKG@.AbilZone bubbleEcho(@PKG@.AbilZone z, @CB@ cb, long now) {
  if (z.cx == null || z.cx.echo || !(z.cx.echoPct > 0.0) || z.echoed) return null;
  z.echoed = true;
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
  @PKG@.AbilCtx e = z.cx.echoOf(z.cx.echoPct);
  long life = Math.round(@PKG@.AbilCfg.U_TIME * 1000.0);
  @PKG@.AbilZone b = new @PKG@.AbilZone(2, z.caster, z.x, z.y, z.z, z.r - z.cx.radAdd, now, now + life);
  b.pkey = z.pkey;
  b.name = z.name;
  b.shape = z.shape;
  b.cx = e;
  b.h = z.h;
  b.echoed = true;
  b.hpMax = z.cx.main > 0.0 ? z.hpMax * e.main / z.cx.main : z.hpMax * z.cx.echoPct;
  b.hp = b.hpMax;
  particle(FX_BUBBLE_ON, b.x, b.y + 1.0, b.z, cb);
  ring(FX_BUBBLE, b, cb);
  @PR@ pr = prOf(z.caster);
  if (pr != null) say(pr, "Echo: a weaker Shield Bubble forms (" + @PKG@.AbilMath.fmt(b.hpMax) + " HP).");
  aw.addZone(b);
  ECHOES = ECHOES + 1L;
  return b;
}''')
# ---- THE RUNE ROUTE (the Hytale 0.7 keys). The rune id of an ability, whether the asset pack loaded it, the pair the slots should hold.
late(r'''
public static boolean runeLoaded(String id) {
  if (id == null || id.length() == 0) return false;
  java.util.function.Function f = ITEMS;
  if (f != null) return Boolean.TRUE.equals(f.apply(id));
  try { return @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return false; }
}''')
# [0] = slot 0 (Use Ability 2 = primary 1), [1] = slot 3 (Use Ability 3 = primary 2); "" = none (locked, a passive, not enabled, no rune)
late(r'''
public static String[] runeWant(java.util.UUID u) {
  String[] w = new String[] { "", "" };
  if (u == null || !@PKG@.AbilCfg.PART || !@PKG@.AbilCfg.RUNE_KEYS || !@PKG@.AbilCfg.RUNE_HUD) return w;
  int ci = @PKG@.ClassStore.classIndex(u);
  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) return w;
  String k = @PKG@.ClassCfg.pkey(u);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  int lv = level(u, ci);
  boolean grant = @PKG@.AbilStore.granted(k);
  String pick = @PKG@.AbilStore.pick(k);
  String csv = treeCsv(u);
  for (int i = 0; i < 2; i++) {
    int ai = @PKG@.AbilDefs.find(sl[i]);
    if (ai < 0 || @PKG@.AbilDefs.PASSIVE[ai] || !@PKG@.AbilDefs.BUILT[ai]) continue;
    if (!@PKG@.AbilDefs.owns(ai, lv, grant, pick) || !lineOn(csv, ai)) continue;
    String id = @PKG@.AbilDefs.RUNE[ai];
    if (runeLoaded(id)) w[i] = id;
  }
  return w;
}''')
late(r'''
public static @IC@ abilSlots(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @ABS@.getComponentType());
    return o instanceof @ABS@ ? ((@ABS@) o).getInventory() : null;
  } catch (Throwable t) { return null; }
}''')
late(r'''
public static String slotId(@IC@ c, int s) {
  try {
    @IS@ it = c.getItemStack((short) s);
    if (it == null || it.isEmpty()) return "";
    String id = it.getItemId();
    return id == null ? "" : id;
  } catch (Throwable t) { return ""; }
}''')
# 1 = the slots need a write (one of our runes in a wrong slot, or a wanted rune's slot is empty), 0 = right, -1 = no ability slots
late(r'''
public static int mirrorNeed(@IC@ c, String[] w) {
  if (c == null) return -1;
  int cap = 0;
  try { cap = (int) c.getCapacity(); } catch (Throwable t) { return -1; }
  for (int s = 0; s < cap; s++) {
    String id = slotId(c, s);
    if (!id.startsWith("SkyyAbility_")) continue;
    if (s == 0 && id.equals(w[0])) continue;
    if (s == 3 && id.equals(w[1])) continue;
    return 1;
  }
  if (w[0].length() > 0 && cap > 0 && slotId(c, 0).length() == 0) return 1;
  if (w[1].length() > 0 && cap > 3 && slotId(c, 3).length() == 0) return 1;
  return 0;
}''')
late(r'''
public static int fxIdx(String rune) {
  if (rune == null || rune.length() == 0) return -1;
  int ai = -1;
  for (int i = 0; i < @PKG@.AbilDefs.RUNE.length; i++) if (rune.equals(@PKG@.AbilDefs.RUNE[i])) ai = i;
  if (ai < 0) return -1;
  java.util.function.Function f = MARKS;
  if (f != null) { Object o = f.apply(@PKG@.AbilDefs.MARK[ai]); return o instanceof Integer ? ((Integer) o).intValue() : -1; }
  try { return @EFX@.getAssetMap().getIndex(@PKG@.AbilDefs.MARK[ai]); } catch (Throwable t) { return -1; }
}''')
late(r'''
public static void mirrorSoon(java.util.UUID u) {
  if (u == null) return;
  Object o = @PKG@.AbilStore.MIRROR.get(u);
  if (o instanceof Object[]) ((Object[]) o)[2] = Long.valueOf(0L);
}''')
# SECOND FIX ROUND (critic: existing Mages / Priests lose their keys on deploy with no hint - an empty rune slot makes a press silent):
# 8 s after the first look of a profile this session (the client has loaded), ONE line names every ability it owns that the class tree
# has not enabled. Class trees off (no csv) or everything enabled = nothing said. Returns the names ("" = no line).
late(r'''
public static String enableHint(@PR@ pr, java.util.UUID u, String k) {
  try {
    if (pr == null || u == null || k == null || !@PKG@.AbilCfg.PART || !@PKG@.AbilCfg.TREE_GATE) return "";
    int ci = @PKG@.ClassStore.classIndex(u);
    if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) return "";
    String csv = treeCsv(u);
    if (csv == null) return "";
    int lv = level(u, ci);
    boolean grant = @PKG@.AbilStore.granted(k);
    String pick = @PKG@.AbilStore.pick(k);
    String names = "";
    int n = 0;
    for (int ai = 0; ai < @PKG@.AbilDefs.IDS.length; ai++) {
      if (@PKG@.AbilDefs.CLS[ai] != ci || !@PKG@.AbilDefs.BUILT[ai]) continue;
      if (!@PKG@.AbilDefs.owns(ai, lv, grant, pick) || lineOn(csv, ai)) continue;
      names = names + (n == 0 ? "" : ", ") + @PKG@.AbilDefs.NAMES[ai];
      n++;
    }
    if (n == 0) return "";
    send(pr, (n == 1 ? "Your ability " + names + " is off" : "Your abilities " + names + " are off") + ": open /tree, class tab, and click Enable (free) - then they go on your Ability 2 / 3 keys.", "#ffc800");
    return names;
  } catch (Throwable t) { return ""; }
}''')
late(r'''
public static String hintTick(@PR@ pr, java.util.UUID u, String k, long now) {
  if (k == null) return "";
  Object o = @PKG@.AbilStore.HINTED.get(k);
  if (!(o instanceof long[])) { @PKG@.AbilStore.HINTED.put(k, new long[] { now + 8000L, 0L }); return "wait"; }
  long[] h = (long[]) o;
  if (h[1] != 0L || now < h[0]) return "";
  h[1] = 1L;
  return enableHint(pr, u, k);
}''')
# MirrorTask (the world thread, outside any system): our runes out of wrong ability slots, the wanted ones into EMPTY slots 0 / 3 (a
# vanilla rune is never touched). Returns what it did ("-0 +3", "" = nothing).
late(r'''
public static String mirrorSet(@PR@ pr, java.util.UUID u) {
  try {
    if (!pr.isValid()) return "gone";
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return "gone";
    @ST@ st = r.getStore();
    @IC@ c = abilSlots(st, r);
    String[] w = runeWant(u);
    if (c == null) return "noslots";
    int cap = (int) c.getCapacity();
    String done = "";
    for (int s = 0; s < cap; s++) {
      String id = slotId(c, s);
      if (!id.startsWith("SkyyAbility_")) continue;
      if ((s == 0 && id.equals(w[0])) || (s == 3 && id.equals(w[1]))) continue;
      c.removeItemStackFromSlot((short) s);
      done = done + " -" + s;
    }
    for (int i = 0; i < 2; i++) {
      int s = i == 0 ? 0 : 3;
      if (s >= cap || w[i].length() == 0 || slotId(c, s).length() > 0) continue;
      c.addItemStackToSlot((short) s, new @IS@(w[i], 1));
      done = done + (slotId(c, s).equals(w[i]) ? " +" : " !") + s;
    }
    if (done.length() > 0) { MIRRORS = MIRRORS + 1L; LAST_MIRROR = pr.getUsername() + done; }
    return done.trim();
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability rune slots of " + u + " could not be set: " + t); return "failed"; }
}''')
# 0.1.22 fix: a rune the ability slot refused (" !0" - U5) is logged ONCE per player; from the 3rd failure in a row the mirror waits 60 s
# (a PlayerReady / profile / loadout change still looks at once); a write that works clears the count. Returns the wait in ms.
late(r'''
public static long mirrorWait(@PR@ pr, java.util.UUID u, String r) {
  if (u == null || r == null) return 2000L;
  if (r.indexOf('!') < 0) {
    if (r.indexOf('+') >= 0) @PKG@.AbilStore.MIRFAIL.remove(u);
    return 2000L;
  }
  Object o = @PKG@.AbilStore.MIRFAIL.get(u);
  int[] f = o instanceof int[] ? (int[]) o : new int[] { 0 };
  f[0] = f[0] + 1;
  @PKG@.AbilStore.MIRFAIL.put(u, f);
  if (f[0] == 1) @PKG@.ClassCfg.warnLimited("the ability slot refused the class rune of " + (pr == null ? String.valueOf(u) : pr.getUsername()) + " (" + r + ", U5) - their keys cast through the hook / marker only if the rune is there; /cast works. Retrying, then every 60 s.");
  return f[0] >= 3 ? 60000L : 2000L;
}''')
late(r'''
public static String mirrorNow(@PR@ pr) {
  if (pr == null) return "gone";
  java.util.UUID u = pr.getUuid();
  String r = mirrorSet(pr, u);
  long wait = mirrorWait(pr, u, r);
  Object o = u == null ? null : @PKG@.AbilStore.MIRROR.get(u);
  if (o instanceof Object[]) { ((Object[]) o)[3] = Boolean.FALSE; ((Object[]) o)[2] = Long.valueOf(System.currentTimeMillis() + wait); }
  return r;
}''')
# a marker effect of the cast root on the player (the hook did not fire - U3 fallback): cast unless the hook took this press already
late(r'''
public static String markerPress(@PR@ pr, java.util.UUID u, int key, @WLD@ w, long now) {
  Object lh = @PKG@.AbilStore.LASTHOOK.get(u);
  if (lh instanceof Long && now - ((Long) lh).longValue() < 700L && now >= ((Long) lh).longValue()) { FB_DUP = FB_DUP + 1L; return "dup"; }
  FALLBACKS = FALLBACKS + 1L;
  if (w != null) w.execute(new @PKG@.RuneCast(pr, key, 2));
  return "cast";
}''')
# AbilTick, every player every tick: the marker fallback (players with a mirror record holding a rune) + the 2 s mirror look
late(r'''
public static void runeTick(@PR@ pr, java.util.UUID u, @REF@ r, @CAC@ acc, long now) {
  Object o = @PKG@.AbilStore.MIRROR.get(u);
  Object[] mr = null;
  if (o instanceof Object[]) mr = (Object[]) o;
  @WLD@ w = null;
  if (mr != null && @PKG@.AbilCfg.RUNE_FB && @PKG@.AbilCfg.RUNE_KEYS) {
    int f0 = ((Integer) mr[4]).intValue();
    int f1 = ((Integer) mr[5]).intValue();
    if (f0 >= 0 || f1 >= 0) {
      Object co = acc.getComponent(r, @ECC@.getComponentType());
      if (co instanceof @ECC@) {
        @ECC@ ec = (@ECC@) co;
        if (f0 >= 0 && ec.hasEffect(f0)) { ec.removeEffect(r, f0, acc); w = worldOf(acc); markerPress(pr, u, 0, w, now); }
        if (f1 >= 0 && ec.hasEffect(f1)) { ec.removeEffect(r, f1, acc); if (w == null) w = worldOf(acc); markerPress(pr, u, 1, w, now); }
      }
    }
  }
  long next = mr == null ? 0L : ((Long) mr[2]).longValue();
  if (now < next && now >= next - 60000L) return;
  if (mr != null && Boolean.TRUE.equals(mr[3]) && now - ((Long) mr[6]).longValue() < 10000L) return;
  String[] want = runeWant(u);
  String k = @PKG@.ClassCfg.pkey(u);
  hintTick(pr, u, k, now);   // second fix round: an owned ability the tree has not enabled -> one hint line per profile per session
  int need = mirrorNeed(abilSlots(acc, r), want);
  Object[] nr = new Object[] { want[0], want[1], Long.valueOf(now + 2000L), Boolean.FALSE, Integer.valueOf(fxIdx(want[0])),
                               Integer.valueOf(fxIdx(want[1])), Long.valueOf(now), k };
  if (need == 1) {
    if (w == null) w = worldOf(acc);
    if (w != null) { nr[3] = Boolean.TRUE; w.execute(new @PKG@.MirrorTask(pr)); }
  }
  @PKG@.AbilStore.MIRROR.put(u, nr);
}''')
late(r'''
public static @WLD@ worldOf(@CAC@ acc) {
  try {
    Object x = acc.getExternalData();
    return x instanceof @ES@ ? ((@ES@) x).getWorld() : null;
  } catch (Throwable t) { return null; }
}''')
# THE HOOK's decision (pure, bare-JVM tested): ignore (not ours: other classes, a weapon's own move), allow (a vanilla rune while
# abil.vanillaRunes), repeat (the 120 ms guard), cast (our rune), vanilla (a game rune on a Mage / Priest: blocked - cancelled + a hint)
late(r'''
public static String runeDecide(java.util.UUID u, int ci, int key, String held, int section, long now) {
  if (u == null || key < 0 || key > 1 || !@PKG@.AbilCfg.PART || !@PKG@.AbilCfg.RUNE_KEYS) return "ignore";
  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) return "ignore";
  String id = held == null ? "" : held;
  boolean ours = id.startsWith("SkyyAbility_");
  boolean vanilla = !ours && id.length() > 0 && section == @INVC@.ABILITIES_SECTION_ID;
  if (!ours && !vanilla) return "ignore";
  if (vanilla && @PKG@.AbilCfg.VAN_RUNES) return "allow";
  String tk = u + "|" + key;
  Object lo = @PKG@.AbilStore.LASTKEY.get(tk);
  @PKG@.AbilStore.LASTKEY.put(tk, Long.valueOf(now));
  @PKG@.AbilStore.LASTHOOK.put(u, Long.valueOf(now));
  if (lo instanceof Long && now - ((Long) lo).longValue() < 120L && now >= ((Long) lo).longValue()) return "repeat";
  return ours ? "cast" : "vanilla";
}''')
# THE HOOK (AbilRuneSys.handle, the world thread inside the system run): our rune / a blocked game rune -> the chain is cancelled (the
# engine tells the client: nothing spent, no animation) and the cast runs a tick later outside the system (RuneCast, door 1)
late(r'''
public static String onRune(@ICSE@ e, int key, @REF@ r, @ST@ st, @CB@ buf) {
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  @PR@ pr = (@PR@) po;
  java.util.UUID u = pr.getUuid();
  int ci = @PKG@.ClassStore.classIndex(u);
  @ICTX@ ctx = e.getContext();
  @IS@ held = ctx == null ? null : ctx.getHeldItem();
  int sec = ctx == null ? 0 : ctx.getHeldItemSectionId();
  String id = held == null || held.isEmpty() ? "" : held.getItemId();
  long now = System.currentTimeMillis();
  String d = runeDecide(u, ci, key, id, sec, now);
  HOOK_SEEN = HOOK_SEEN + 1L;
  if ("ignore".equals(d) || "allow".equals(d)) return d;
  e.setCancelled(true);
  HOOKS = HOOKS + 1L;
  if ("repeat".equals(d)) return d;
  if ("vanilla".equals(d)) {
    Object vt = @PKG@.AbilStore.VANTOLD.get(u);
    if (!(vt instanceof Long) || now - ((Long) vt).longValue() > 30000L) {
      @PKG@.AbilStore.VANTOLD.put(u, Long.valueOf(now));
      send(pr, "Game runes are blocked for " + @PKG@.ClassDefs.NAMES[ci] + "s. Move " + id + " to your rune bag - your class ability rune then takes this slot (or use /cast).", "#ffc800");
    }
    VANBLOCK = VANBLOCK + 1L;
    return d;   // second fix round: Skyy M2 "Blocked" - the game rune does nothing (cancelled), and no class cast either
  }
  @WLD@ w = worldOf(st);
  if (w != null) w.execute(new @PKG@.RuneCast(pr, key, 1));
  return d;
}''')
# RuneCast.run (the world thread, a tick after the press): the /cast pipeline, door 1 (the hook) / 2 (the marker fallback)
late(r'''
public static String runeCast(@PR@ pr, int key, int door) {
  if (pr == null || !pr.isValid()) return "gone";
  @REF@ ref = pr.getReference();
  if (ref == null || !ref.isValid()) return "gone";
  @ST@ st = ref.getStore();
  @WLD@ w = worldOf(st);
  String r = castAt(pr, st, ref, w, key == 0 ? "1" : "2", -1, door);
  LAST = r;
  LAST_RUNE = r;
  if (r.startsWith("ok:")) {
    RUNES = RUNES + 1L;
    if (@PKG@.AbilCfg.RUNE_FILL && r.indexOf(" crouch") < 0) fill(pr, st, ref, key);
  }
  return r;
}''')
# abil.runeCooldownFill (U6, OFF by default): the player's server CooldownHandler for the pressed rune's cast root, armed for its cooldown
late(r'''
public static boolean fill(@PR@ pr, @ST@ st, @REF@ ref, int key) {
  try {
    String[] w = runeWant(pr.getUuid());
    String rune = w[key < 0 || key > 1 ? 0 : key];
    int ai = -1;
    for (int i = 0; i < @PKG@.AbilDefs.RUNE.length; i++) if (rune.equals(@PKG@.AbilDefs.RUNE[i]) && rune.length() > 0) ai = i;
    if (ai < 0) return false;
    long left = @PKG@.AbilStore.total(@PKG@.ClassCfg.pkey(pr.getUuid()), @PKG@.AbilDefs.IDS[ai]);
    if (left <= 0L) return false;
    Object im = st.getComponent(ref, @IMOD@.get().getInteractionManagerComponent());
    java.lang.reflect.Field f = Class.forName("@IMGR@").getDeclaredField("cooldownHandler");
    f.setAccessible(true);
    Object h = f.get(im);
    if (!(h instanceof @CDH@)) throw new IllegalStateException("no CooldownHandler");
    float secs = (float) ((double) left / 1000.0);
    @CDN@ c = ((@CDH@) h).getCooldown(@PKG@.AbilDefs.ROOT[ai], secs, @IMGR@.DEFAULT_CHARGE_TIMES, true, false);
    c.setCooldownMax(secs);
    c.resetCooldown();
    FILLS = FILLS + 1L;
    return true;
  } catch (Throwable t) {
    if (!FILL_WARNED) { FILL_WARNED = true; @PKG@.ClassCfg.warn("abil.runeCooldownFill: the rune slot cooldown could not be armed (logged once, the HUD widget stays the display): " + t); }
    return false;
  }
}''')
# THE GUARD (AbilInvSys, InventoryChangeEvent): the ability slots changed -> mirror look at once; one of our runes anywhere else -> InvClean
late(r'''
public static String onInv(@ICE@ ev, @REF@ r, @CB@ buf) {
  Object po = buf.getComponent(r, @PR@.getComponentType());
  if (!(po instanceof @PR@)) return null;
  @PR@ pr = (@PR@) po;
  java.util.UUID u = pr.getUuid();
  Object t = ev.getComponentType();
  if (t != null && t == @ABS@.getComponentType()) { mirrorSoon(u); return "slots"; }
  @IC@ c = ev.getItemContainer();
  if (c == null) return null;
  int cap = 0;
  try { cap = (int) c.getCapacity(); } catch (Throwable x) { return null; }
  boolean found = false;
  for (int s = 0; s < cap && !found; s++) if (slotId(c, s).startsWith("SkyyAbility_")) found = true;
  if (!found) return null;
  if (@PKG@.AbilStore.CLEANQ.putIfAbsent(u, Boolean.TRUE) != null) return "queued";
  @WLD@ w = worldOf(buf);
  if (w != null) w.execute(new @PKG@.InvClean(pr));
  else @PKG@.AbilStore.CLEANQ.remove(u);
  return "clean";
}''')
late(r'''
public static int cleanIc(@IC@ c) {
  if (c == null) return 0;
  int n = 0;
  int cap = 0;
  try { cap = (int) c.getCapacity(); } catch (Throwable t) { return 0; }
  for (int s = 0; s < cap; s++) {
    String id = slotId(c, s);
    if (!id.startsWith("SkyyAbility_")) continue;
    int q = 1;
    try { q = c.getItemStack((short) s).getQuantity(); } catch (Throwable t) { q = 1; }
    c.removeItemStackFromSlot((short) s);
    if (slotId(c, s).length() == 0) n = n + q;
  }
  return n;
}''')
# InvClean (the world thread): every SkyyAbility_ stack OUTSIDE the ability slots goes (counted before / after); the mirror then refills
late(r'''
public static int cleanNow(@PR@ pr) {
  if (pr == null) return 0;
  java.util.UUID u = pr.getUuid();
  @PKG@.AbilStore.CLEANQ.remove(u);
  try {
    if (!pr.isValid()) return 0;
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) return 0;
    @ST@ st = ref.getStore();
    @PLA@ pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    int n = 0;
    if (pl != null && pl.getInventory() != null) {
      @INV@ inv = pl.getInventory();
      n = n + cleanIc(inv.getHotbar());
      n = n + cleanIc(inv.getStorage());
      n = n + cleanIc(inv.getBackpack());
      n = n + cleanIc(inv.getUtility());
      n = n + cleanIc(inv.getTools());
      n = n + cleanIc(inv.getArmor());
    }
    Object rb = st.getComponent(ref, @RNB@.getComponentType());
    if (rb instanceof @RNB@) n = n + cleanIc(((@RNB@) rb).getInventory());
    if (n > 0) {
      CLEANED = CLEANED + (long) n;
      @PKG@.ClassCfg.info("removed " + n + " ability rune(s) of " + pr.getUsername() + " from outside the ability slots (they only live there)");
      mirrorSoon(u);
    }
    return n;
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability rune clean-up of " + u + " failed: " + t); return -1; }
}''')
# ---- THE PANEL BRIDGES for SkyyTrees 0.3.7 (class:fn:abilPanel / abilMods / abilDo): texts + numbers only, plain java.lang
late(r'''
public static String modText(int ai, int mi, int lvl, int cnt) {
  if (ai < 0 || mi < 0 || lvl <= 0) return "";
  int e = (cnt > 1 && @PKG@.AbilModDefs.MSTACK[mi]) ? lvl * cnt : lvl;
  int l1 = lvl - 1;
  if (mi == @PKG@.AbilModDefs.POWER) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_POWER * (double) e) + " % " + @PKG@.AbilDefs.NOUN[ai];
  if (mi == @PKG@.AbilModDefs.RADIUS) return "+" + @PKG@.AbilMath.fmt((ai == @PKG@.AbilDefs.GUARD ? 10.0 : 1.0) * @PKG@.AbilCfg.MOD_RADIUS * (double) e) + " blocks";
  if (mi == @PKG@.AbilModDefs.DURATION) return "+" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.MOD_DUR * (double) e) + " % longer";
  if (mi == @PKG@.AbilModDefs.EFFICIENCY) {
    double v = @PKG@.AbilCfg.MOD_EFF * (double) e;
    return "-" + @PKG@.AbilMath.fmt(v > 50.0 ? 50.0 : v) + " % Mana and Stamina";
  }
  if (mi == @PKG@.AbilModDefs.SPLIT) return "3 meteors at " + @PKG@.AbilMath.fmt(40.0 + 5.0 * (double) l1) + " % each";
  if (mi == @PKG@.AbilModDefs.PIERCE) return "+" + e + (e == 1 ? " enemy" : " enemies") + " behind the first";
  if (mi == @PKG@.AbilModDefs.CHAIN) return "+" + e + " targets, " + @PKG@.AbilMath.fmt(chainCut(e)) + " % less drop" + (e > 5 ? " (drop floor: the Lv 5 one)" : "");
  if (mi == @PKG@.AbilModDefs.LINGER) return "burns " + @PKG@.AbilMath.fmt(3.0 + 0.5 * (double) l1) + " s, " + @PKG@.AbilMath.fmt(8.0 + 2.0 * (double) l1) + " % a second";
  if (mi == @PKG@.AbilModDefs.SLOW) {
    if (ai == @PKG@.AbilDefs.BEAM) return "slows for " + @PKG@.AbilMath.fmt(1.0 + 0.5 * (double) (e - 1)) + " s";
    return "chill +" + e + " s";
  }
  if (mi == @PKG@.AbilModDefs.KNOCK) return "bursts at the end, push " + @PKG@.AbilMath.fmt(8.0 + 2.0 * (double) (e - 1));
  if (mi == @PKG@.AbilModDefs.FOLLOW) return ai == @PKG@.AbilDefs.MANAB ? "moves with you (" + @PKG@.AbilMath.fmt(80.0 + 5.0 * (double) l1) + " % ratio)" : "moves with you";
  if (mi == @PKG@.AbilModDefs.WARD) {
    String w = @PKG@.AbilMath.fmt(3.0 * (double) lvl) + " % max Health";
    if (ai == @PKG@.AbilDefs.MANAB) return "you + party within 4: shield " + w;
    if (ai == @PKG@.AbilDefs.GRACE) return "overheal = shield up to " + w;
    return "the saved player: shield " + w;
  }
  if (mi == @PKG@.AbilModDefs.ECHO) return "again at " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.ECHO_BASE + @PKG@.AbilCfg.ECHO_STEP * (double) l1) + " % after " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.ECHO_DELAY) + " s";
  return "";
}''')
# class:fn:abilPanel -> Object[78]: [0] ok / off / noclass / noabil, [1] class, [2] Integer class level, [3] Boolean in combat, [4] pick A / B,
# [5] Boolean may pick, [6] Boolean tree gate on, [7] "1,10,20,30" (lines 1-4 unlock levels), [8] Boolean levels on, [9] Boolean mods on,
# [10] the key hint, [11] Boolean admin grant; [12 + 16 i ...] per slot i (0-1 primaries on Ability 2 / 3, 2-3 alts = crouch + key): id,
# name, rune item (loaded) or "", owned (class level), enabled (tree), Integer line, Integer level, Long uses, Long uses to the next
# level, level text, mod 0 id, Integer its level, mod 1 id, Integer its level, Integer modifier slots, state; [76] / [77] the A / B names
late(r'''
public static Object[] panel(java.util.UUID u, String csv0, boolean useCsv) {
  Object[] o = new Object[78];
  o[0] = "noclass";
  if (u == null) return o;
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) return o;
  o[1] = @PKG@.ClassDefs.NAMES[ci];
  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) { o[0] = "noabil"; return o; }
  o[0] = @PKG@.AbilCfg.PART ? "ok" : "off";
  String k = @PKG@.ClassCfg.pkey(u);
  long now = System.currentTimeMillis();
  String csv = csv0;
  if (useCsv) @PKG@.AbilStore.TREEC.put(u, new Object[] { k, Long.valueOf(now), csv0 });
  else csv = treeCsv(u);
  int lv = level(u, ci);
  boolean grant = @PKG@.AbilStore.granted(k);
  String pick = @PKG@.AbilStore.pick(k);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  o[2] = Integer.valueOf(lv);
  o[3] = Boolean.valueOf(combatMs(u) > 0L);
  o[4] = pick;
  o[5] = Boolean.valueOf(grant || (long) lv >= @PKG@.AbilDefs.unlock(3));
  o[6] = Boolean.valueOf(@PKG@.AbilCfg.TREE_GATE && csv != null);
  o[7] = @PKG@.AbilCfg.UNLOCK_A1 + "," + @PKG@.AbilCfg.UNLOCK_A2 + "," + @PKG@.AbilCfg.UNLOCK_A2X + "," + @PKG@.AbilCfg.UNLOCK_A1X;
  o[8] = Boolean.valueOf(@PKG@.AbilCfg.LEVELS);
  o[9] = Boolean.valueOf(@PKG@.AbilCfg.MODS_ON);
  o[10] = @PKG@.AbilCfg.RUNE_KEYS ? "Ability 2 / 3 keys cast your primaries, crouch + key your alts" : "Cast with /cast 1 - 4 (the keys are off on this server)";
  o[11] = Boolean.valueOf(grant);
  java.util.Properties p = @PKG@.AbilStore.load(k);
  for (int i = 0; i < 4; i++) {
    int b = 12 + i * 16;
    int ai = @PKG@.AbilDefs.find(sl[i]);
    String id = ai < 0 ? "" : @PKG@.AbilDefs.IDS[ai];
    long uses = ai < 0 ? 0L : numOf(p, "u." + id);
    int l = alvl(uses);
    int slots = modSlots(csv, ai);
    int[] eq = ai < 0 ? new int[] { -1, -1 } : equipped(p, ai, l, slots);
    String rn = ai < 0 ? "" : @PKG@.AbilDefs.RUNE[ai];
    long nx = 0L;
    if (ai >= 0 && @PKG@.AbilCfg.LEVELS && (long) l < @PKG@.AbilCfg.MAX_LVL) nx = @PKG@.AbilMath.levelStart(l + 1, @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP) - uses;
    o[b] = id;
    o[b + 1] = ai < 0 ? "" : @PKG@.AbilDefs.NAMES[ai];
    o[b + 2] = runeLoaded(rn) ? rn : "";
    o[b + 3] = Boolean.valueOf(ai >= 0 && @PKG@.AbilDefs.owns(ai, lv, grant, pick));
    o[b + 4] = Boolean.valueOf(ai >= 0 && lineOn(csv, ai));
    o[b + 5] = Integer.valueOf(lineOf(ai));
    o[b + 6] = Integer.valueOf(l);
    o[b + 7] = Long.valueOf(uses);
    o[b + 8] = Long.valueOf(nx < 0L ? 0L : nx);
    o[b + 9] = levelText(ai, l, uses);
    o[b + 10] = eq[0] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[0]];
    o[b + 11] = Integer.valueOf(eq[0] < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[eq[0]])));
    o[b + 12] = eq[1] < 0 ? "" : @PKG@.AbilModDefs.MNAME[eq[1]];
    o[b + 13] = Integer.valueOf(eq[1] < 0 ? 0 : @PKG@.AbilModDefs.modLevel(numOf(p, "m." + id + "." + @PKG@.AbilModDefs.MID[eq[1]])));
    o[b + 14] = Integer.valueOf(slots);
    String stt = stateOf(ai, k, lv, grant, pick, now);
    if (ai >= 0 && @PKG@.AbilDefs.owns(ai, lv, grant, pick) && !lineOn(csv, ai)) stt = "disabled";   // owned, the tree has not enabled it
    o[b + 15] = stt;
  }
  int pa = @PKG@.AbilDefs.of(ci, 3);
  int pb = @PKG@.AbilDefs.of(ci, 4);
  o[76] = pa < 0 ? "" : @PKG@.AbilDefs.NAMES[pa];
  o[77] = pb < 0 ? "" : @PKG@.AbilDefs.NAMES[pb];
  return o;
}''')
# class:fn:abilMods -> String[]: [0] = "id|name|level|uses|level text|noun|slots|eq0|eq1|gain text", then one row per offered modifier:
# "mod id|name|unlock level|unlocked 0/1|modifier level|uses|uses to next|equipped count|stackable 0/1|now text|next text|can double 0/1"
late(r'''
public static String[] modRows(java.util.UUID u, String id, String csv) {
  int ci = @PKG@.ClassStore.classIndex(u);
  int ai = @PKG@.AbilDefs.find(id);
  if (u == null || ai < 0 || @PKG@.AbilDefs.CLS[ai] != ci) return new String[0];
  String k = @PKG@.ClassCfg.pkey(u);
  java.util.Properties p = @PKG@.AbilStore.load(k);
  String aid = @PKG@.AbilDefs.IDS[ai];
  long uses = numOf(p, "u." + aid);
  int l = alvl(uses);
  int slots = modSlots(csv, ai);
  int[] eq = equipped(p, ai, l, slots);
  String[] st = eqOf(p, aid);
  int n = @PKG@.AbilModDefs.count(ai);
  String[] out = new String[n + 1];
  out[0] = aid + "|" + @PKG@.AbilDefs.NAMES[ai] + "|" + l + "|" + uses + "|" + levelText(ai, l, uses) + "|" + @PKG@.AbilDefs.NOUN[ai] + "|" + slots
    + "|" + (eq[0] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[0]]) + "|" + (eq[1] < 0 ? "" : @PKG@.AbilModDefs.MID[eq[1]]) + "|" + gainText(ai, l);
  for (int j = 0; j < n; j++) {
    int mi = @PKG@.AbilModDefs.at(ai, j);
    int at = @PKG@.AbilModDefs.unlockAt(j);
    long mu = numOf(p, "m." + aid + "." + @PKG@.AbilModDefs.MID[mi]);
    int ml = @PKG@.AbilModDefs.modLevel(mu);
    int cnt = (eq[0] == mi ? 1 : 0) + (eq[1] == mi ? 1 : 0);
    boolean dbl = @PKG@.AbilModDefs.MSTACK[mi] && ml >= 2;
    String now = l >= at ? modText(ai, mi, ml, cnt > 0 ? cnt : 1) : "unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at;
    long nx = @PKG@.AbilModDefs.modNext(mu);
    String next = l < at ? modText(ai, mi, 1, 1) : (nx > 0L ? "Lv " + (ml + 1) + ": " + modText(ai, mi, ml + 1, 1) : "top level");
    out[j + 1] = @PKG@.AbilModDefs.MID[mi] + "|" + @PKG@.AbilModDefs.MNAME[mi] + "|" + at + "|" + (l >= at ? "1" : "0") + "|" + ml + "|" + mu + "|" + nx
      + "|" + cnt + "|" + (@PKG@.AbilModDefs.MSTACK[mi] ? "1" : "0") + "|" + now + "|" + next + "|" + (dbl ? "1" : "0");
  }
  return out;
}''')
# equip / unequip (the panel and the loadouts): the class's ability, unlocked at this level, a slot the tree gives, the double rule
late(r'''
public static String equipMod(java.util.UUID u, String id, int slot, String mod, String csv, boolean combatOk) {
  int ci = @PKG@.ClassStore.classIndex(u);
  int ai = @PKG@.AbilDefs.find(id);
  if (u == null || ai < 0 || @PKG@.AbilDefs.CLS[ai] != ci) return "-That is not one of your abilities.";
  if (!@PKG@.AbilCfg.MODS_ON) return "-Ability modifiers are switched off on this server.";
  if (!combatOk && combatMs(u) > 0L) return "-Leave combat first - modifiers change only out of combat.";
  String nm = @PKG@.AbilDefs.NAMES[ai];
  String k = @PKG@.ClassCfg.pkey(u);
  java.util.Properties p = @PKG@.AbilStore.load(k);
  String aid = @PKG@.AbilDefs.IDS[ai];
  int slots = modSlots(csv, ai);
  if (slot < 0 || slot > 1) return "-Pick modifier slot 1 or 2.";
  if (slot >= slots) return "-Modifier slot " + (slot + 1) + " of " + nm + " is not open - unlock M" + lineOf(ai) + (slot == 0 ? "A" : "B") + " in your class tree.";
  String[] e = eqOf(p, aid);
  int l = alvl(numOf(p, "u." + aid));
  if (mod == null || mod.length() == 0) {
    if (e[slot].length() == 0) return "-Modifier slot " + (slot + 1) + " of " + nm + " is empty.";
    e[slot] = "";
  } else {
    int mi = @PKG@.AbilModDefs.find(mod);
    int pos = @PKG@.AbilModDefs.pos(ai, mi);
    if (mi < 0 || pos < 0) return "-" + (mi < 0 ? mod : @PKG@.AbilModDefs.MNAME[mi]) + " is not a " + nm + " modifier.";
    int at = @PKG@.AbilModDefs.unlockAt(pos);
    if (l < at) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " unlocks at " + nm + " Lv " + at + " (Lv " + l + " now) - use " + nm + " to level it.";
    int other = @PKG@.AbilModDefs.find(e[slot == 0 ? 1 : 0]);
    if (other == mi) {
      if (!@PKG@.AbilModDefs.MSTACK[mi]) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " cannot be equipped twice.";
      if (@PKG@.AbilModDefs.modLevel(numOf(p, "m." + aid + "." + @PKG@.AbilModDefs.MID[mi])) < 2) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " can go in both slots from modifier Lv 2.";
    }
    if (@PKG@.AbilModDefs.MID[mi].equals(e[slot])) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " is already in slot " + (slot + 1) + ".";
    e[slot] = @PKG@.AbilModDefs.MID[mi];
  }
  String v = e[0] + "," + e[1];
  if (",".equals(v)) v = null;
  if (!@PKG@.AbilStore.set(k, new String[] { "e." + aid }, new String[] { v })) return "-Your ability file could not be read - nothing changed (see the server log).";
  @PKG@.AbilStore.saveSoon(k);
  mirrorSoon(u);
  return "+" + nm + ": slot 1 " + (e[0].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[0])]) + ", slot 2 " + (e[1].length() == 0 ? "empty" : @PKG@.AbilModDefs.MNAME[@PKG@.AbilModDefs.find(e[1])]) + ".";
}''')
# class:fn:abilDo: swap <slot> <slot> | pick A|B | equip <id> <slot>:<mod> | unequip <id> <slot>  ->  "+done" / "-why"
late(r'''
public static String doAction(java.util.UUID u, String act, String a, String b, String csv) {
  if (u == null || act == null) return "-Bad arguments.";
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) return "-Your class has no abilities yet.";
  String x = act.trim().toLowerCase();
  String r = "-Unknown action.";
  if (x.equals("swap")) {
    int sa = -1;
    int sb = -1;
    try { sa = Integer.parseInt(a.trim()); sb = Integer.parseInt(b.trim()); } catch (Throwable t) { return "-Pick two slots."; }
    String s = swapSlots(u, sa, sb);
    r = s.startsWith("ok:") ? "+" + s.substring(3) : "-" + s;
  } else if (x.equals("pick")) {
    if (combatMs(u) > 0L) return "-Leave combat first - abilities change only out of combat.";
    String k = @PKG@.ClassCfg.pkey(u);
    boolean can = @PKG@.AbilStore.granted(k) || (long) level(u, ci) >= @PKG@.AbilDefs.unlock(3);
    if (!can) return "-You choose your Ability 1 alt at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(3) + ".";
    String s = setPick(k, ci, a);
    r = s.startsWith("Your Ability 1 alt is now") ? "+" + s : "-" + s;
  } else if (x.equals("equip")) {
    String v = b == null ? "" : b;
    int c = v.indexOf(':');
    if (c <= 0) return "-Usage: equip <ability> <slot>:<modifier>.";
    int sl = -1;
    try { sl = Integer.parseInt(v.substring(0, c).trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, v.substring(c + 1).trim(), csv, false);
  } else if (x.equals("unequip")) {
    int sl = -1;
    try { sl = Integer.parseInt(b.trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, "", csv, false);
  }
  if (r.startsWith("+")) mirrorSoon(u);
  DOS = DOS + 1L;
  return r;
}''')
# THE PIPELINE (0.1.21's castAt + the doors, the roll, the tree gate, the cast context): door 0 = /cast, 1 = the rune hook, 2 = the marker
# fallback, 3 = /classadmin shape. The context goes on this thread as soon as it exists (castAt clears it whatever happens).
late(r'''
public static String castAt0(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg, int forced, int door) {
  if (pr == null || st == null || ref == null || !ref.isValid()) return "bad";
  java.util.UUID u = pr.getUuid();
  if (!@PKG@.AbilCfg.PART) { refuse(pr, "Class abilities are switched off on this server."); return "off"; }
  int slot = @PKG@.AbilMath.slotOf(arg);
  if (slot < 0) { send(pr, "Usage: /cast 1 or /cast 2 (crouch = your alt), /cast 3 or 4 = your alts, /cast list, /cast swap, /cast page", "#ffc800"); return "usage"; }
  if (door == 0 && !@PKG@.AbilCfg.CAST_CMD) { refuse(pr, "/cast 1-4 is off on this server - your Ability 2 / 3 keys cast (crouch = your alts). /cast list, swap and page still work."); return "cmdoff"; }
  if ((door == 1 || door == 2) && !@PKG@.AbilCfg.RUNE_KEYS) return "keysoff";
  if (@PKG@.Kit.busy(u)) { refuse(pr, "Your profile is still loading - try again in a moment."); return "busy"; }
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) { refuse(pr, noClass()); return "noclass"; }
  if (!@PKG@.AbilDefs.classHas(ci) || !@PKG@.ClassDefs.ENABLED[ci]) { refuse(pr, @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first."); return "noabil"; }
  if (!alive(st, ref)) return "dead";
  long now = System.currentTimeMillis();
  boolean crouch = false;
  int s = -1;
  int sh = 0;
  if (forced >= 0) {
    crouch = forced == 3 && slot < 2;
    s = @PKG@.AbilMath.resolve(slot, crouch);
    sh = forced;
  } else {
    boolean air = airNow(st, ref, u, now);
    crouch = !air && crouching(st, ref) && crouchNow(u, now);
    boolean roll = rolling(st, ref);
    if (roll && !@PKG@.AbilCfg.ROLL_CAST) { refuse(pr, "Not while rolling - cast once your roll ends (Server Setup: Cast during a roll)."); return "roll"; }
    boolean sprint = sprinting(st, ref) || roll;
    if (air && slot >= 2 && @PKG@.AbilCfg.SHAPES) {
      refuse(pr, "Your alts cannot be cast in the air - in the air your keys fire your primaries' mid-air shapes. Nothing was spent.");
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
  String csv = treeCsv(u);
  if (!lineOn(csv, ai)) {
    refuse(pr, (s >= 2 ? "No alt yet - " : "") + "enable " + nm + " in your class tree first: /tree class, node A" + lineOf(ai) + " - nothing was spent.");
    return "tree";
  }
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
  @PKG@.AbilCtx cx = ctxFor(u, k, ai, sh, csv);
  @PKG@.AbilCtx.put(cx);
  boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(st, ref);
  double mana = free ? 0.0 : costMana(cx, ai, sh);
  double stam = free ? 0.0 : costStam(cx, ai, sh);
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
  if ("Mage".equals(cx.cls) && cx.node("PC1") && hm >= 0.0) {
    double mx = max(m, mi);
    if (mx > 0.0 && hm >= mx - 0.5) cx.main = cx.main * 1.15;
    else if (mx > 0.0 && hm < mx * 0.25) cx.main = cx.main * 0.9;
  }
  double[] at = null;
  if (ai == @PKG@.AbilDefs.METEOR && sh == 0) {
    at = aim(st, ref, @PKG@.AbilCfg.M_RANGE);
    if (at == null) { refuse(pr, "Look at the ground within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.M_RANGE) + " blocks to call the Meteor down - nothing was spent."); return "aim"; }
  }
  if (ai == @PKG@.AbilDefs.STARF && sh == 0) {
    at = aim(st, ref, @PKG@.AbilCfg.T_RANGE);
    if (at == null) { refuse(pr, "Look at the ground within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.T_RANGE) + " blocks to call the stars down - nothing was spent."); return "aim"; }
  }
  if ((ai == @PKG@.AbilDefs.MANAB || ai == @PKG@.AbilDefs.BUBBLE) && sh == 0) {
    at = spot(st, ref, ai == @PKG@.AbilDefs.MANAB ? @PKG@.AbilCfg.B_RANGE : @PKG@.AbilCfg.U_RANGE);
    if (at == null) { refuse(pr, "Could not find where to place " + nm + " - nothing was spent."); return "aim"; }
  }
  if (ai == @PKG@.AbilDefs.MANAB && sh == 0 && at != null) {
    @VEC@ me = pos(st, ref);
    if (me != null && !@PKG@.AbilMath.inRange(at[0] - me.x, at[1] - me.y, at[2] - me.z, @PKG@.AbilCfg.B_RADIUS - 0.5)) at = new double[] { me.x, me.y, me.z };
  }
  if (sh == 1 && (ai == @PKG@.AbilDefs.METEOR || ai == @PKG@.AbilDefs.MANAB || ai == @PKG@.AbilDefs.BUBBLE)) at = ahead(st, ref, @PKG@.AbilCfg.AHEAD);
  if (sh == 1 && ai == @PKG@.AbilDefs.SANCT) at = ahead(st, ref, @PKG@.AbilCfg.Y_AHEAD);
  if (at == null && sh != 2) at = here(st, ref);
  if (at == null && sh != 2) { refuse(pr, "Could not find where you are - nothing was spent."); return "aim"; }
  if (ai == @PKG@.AbilDefs.SACRED && (sh == 0 || sh == 3) && needHeal(st, ref, u) == 0) {
    refuse(pr, "Nobody within " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.S_RADIUS + cxr()) + " blocks needs healing - nothing was spent.");
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
  cx.paid = mana;
  long cd = cdCx(cx, ai, sh);
  @PKG@.AbilStore.arm(k, id, now, cd);
  @PKG@.AbilStore.CHAN.remove(u);
  say(pr, dn + "! -" + @PKG@.AbilMath.fmt(mana) + " Mana, -" + @PKG@.AbilMath.fmt(stam) + " Stamina. Ready again in " + @PKG@.AbilMath.secs(cd) + " s.");
  String extra = "";
  String failed = null;
  try {
    double h = hOf(item);
    cx.h = h;
    double hm2 = h * cxm();
    if (ai == @PKG@.AbilDefs.METEOR) {
      if (sh == 2) { aw.add(landJob(u, k, ai, hm2 * @PKG@.AbilCfg.M_POWER, now)); extra = " H=" + @PKG@.AbilMath.fmt(h) + " land"; }
      else {
        double mr0 = sh == 0 ? @PKG@.AbilCfg.M_RADIUS : (sh == 1 ? @PKG@.AbilCfg.M_COMET_R : @PKG@.AbilCfg.M_ONME_R);
        double pw = sh == 3 ? @PKG@.AbilCfg.M_ONME_P : @PKG@.AbilCfg.M_POWER;
        long mdl = Math.round((sh == 3 ? @PKG@.AbilCfg.M_ONME_D : @PKG@.AbilCfg.M_DELAY) * 1000.0);
        int nmj = meteorSpawn(aw, u, k, at[0], at[1], at[2], mr0, pw, mdl, now, st);
        extra = " H=" + @PKG@.AbilMath.fmt(h) + " damage=" + @PKG@.AbilMath.fmt(hm2 * pw) + " r=" + @PKG@.AbilMath.fmt(mr0 + cxr()) + " at=" + @PKG@.AbilMath.fmt(at[0]) + "," + @PKG@.AbilMath.fmt(at[1]) + "," + @PKG@.AbilMath.fmt(at[2]) + " meteors=" + nmj;
      }
    }
    else if (ai == @PKG@.AbilDefs.SACRED) {
      if (sh == 0) extra = healCast(pr, st, ref, u, aw, now);
      else if (sh == 1) { blessAt(pr, st, ref, u, k, aw, now); extra = " bless"; }
      else if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else { aw.add(chanJob(u, k, ai, at, @PKG@.AbilCfg.S_KNEEL_T, mana, stam, now)); extra = " kneel"; }
    }
    else if (ai == @PKG@.AbilDefs.MANAB) {
      if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else {
        @PKG@.AbilZone zb = sh == 3 ? barrierAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.B_POCKET_R, @PKG@.AbilCfg.B_POCKET_T, @PKG@.AbilCfg.B_POCKET_RATIO, 3)
                                    : barrierAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.B_RADIUS, @PKG@.AbilCfg.B_TIME, @PKG@.AbilCfg.B_RATIO, sh);
        extra = spotText(zb) + " cap=" + @PKG@.AbilMath.fmt(zb.cap) + " ratio=" + @PKG@.AbilMath.fmt(zb.ratio) + (zb.follow ? " follow" : "");
      }
    }
    else if (ai == @PKG@.AbilDefs.BUBBLE) {
      if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else {
        @PKG@.AbilZone zu = sh == 3 ? bubbleAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.U_AROUND_R, @PKG@.AbilCfg.U_AROUND_HP, 3)
                                    : bubbleAt(pr, st, ref, u, k, aw, at, now, @PKG@.AbilCfg.U_RADIUS, @PKG@.AbilCfg.U_HP, sh);
        extra = spotText(zu) + " hp=" + @PKG@.AbilMath.fmt(zu.hpMax) + (zu.follow ? " follow" : "");
      }
    }
    else if (ai == @PKG@.AbilDefs.FROST) {
      double fAmt = hm2 * @PKG@.AbilCfg.F_POWER;
      double fBrk = hm2 * @PKG@.AbilCfg.F_BREAK_P;
      @PKG@.AbilJob fj = null;
      if (sh == 1) { @PKG@.AbilZone fz = wakeAt(pr, st, ref, u, k, aw, fAmt, now); if (fz != null) fz.brkAmt = fBrk; extra = " wake"; }
      else if (sh == 2) { fj = landJob(u, k, ai, fAmt, now); extra = " land"; }
      else if (sh == 3) fj = novaJob(u, k, at, @PKG@.AbilCfg.F_DEEP_R, fAmt, @PKG@.AbilCfg.F_DEEP_F, @PKG@.AbilCfg.F_DEEP_B, @PKG@.AbilCfg.F_CHILL, now, 3);
      else fj = novaJob(u, k, at, @PKG@.AbilCfg.F_RADIUS, fAmt, @PKG@.AbilCfg.F_FREEZE, @PKG@.AbilCfg.F_BREAK, @PKG@.AbilCfg.F_CHILL, now, 0);
      if (fj != null) { fj.brkAmt = fBrk; aw.add(fj); }
      extra = extra + " H=" + @PKG@.AbilMath.fmt(h) + " damage=" + @PKG@.AbilMath.fmt(fAmt) + (fj != null ? " r=" + @PKG@.AbilMath.fmt(fj.r) + " freeze=" + @PKG@.AbilMath.fmt(fj.freeze) + " chill=" + @PKG@.AbilMath.fmt(fj.chill) : "");
    }
    else if (ai == @PKG@.AbilDefs.STARF) {
      double tAmt = hm2 * @PKG@.AbilCfg.T_POWER;
      @PKG@.AbilJob sj = null;
      if (sh == 2) { aw.add(landJob(u, k, ai, tAmt, now)); extra = " land"; }
      else if (sh == 1) sj = starJob(u, k, at, 2.0, @PKG@.AbilCfg.T_STARS, @PKG@.AbilCfg.T_TIME, tAmt, 1, now);
      else if (sh == 3) sj = starJob(u, k, at, @PKG@.AbilCfg.T_RADIUS, @PKG@.AbilCfg.T_SHOWER_N, @PKG@.AbilCfg.T_SHOWER_T, tAmt, 3, now);
      else sj = starJob(u, k, at, @PKG@.AbilCfg.T_RADIUS, @PKG@.AbilCfg.T_STARS, @PKG@.AbilCfg.T_TIME, tAmt, 0, now);
      if (sj != null) { aw.add(sj); extra = " stars=" + sj.total + " r=" + @PKG@.AbilMath.fmt(sj.r); }
      extra = extra + " H=" + @PKG@.AbilMath.fmt(h) + " star=" + @PKG@.AbilMath.fmt(tAmt);
    }
    else if (ai == @PKG@.AbilDefs.BEAM) {
      @PKG@.AbilJob bj = beamJob(u, k, item, h, sh, now);
      @PKG@.AbilStore.CHAN.put(u, bj);
      aw.add(bj);
      extra = " H=" + @PKG@.AbilMath.fmt(h) + " rate=" + @PKG@.AbilMath.fmt(bj.amount) + " len=" + @PKG@.AbilMath.fmt(bj.len) + " secs=" + @PKG@.AbilMath.fmt(bj.secs) + " to=" + @PKG@.AbilMath.fmt(bj.to);
    }
    else if (ai == @PKG@.AbilDefs.SANCT) {
      if (sh == 2) { aw.add(landJob(u, k, ai, 0.0, now)); extra = " land"; }
      else {
        @PKG@.AbilZone zy = sh == 3 ? sanctAt(pr, st, u, k, aw, at, now, @PKG@.AbilCfg.Y_IN_R, @PKG@.AbilCfg.Y_IN_T, @PKG@.AbilCfg.Y_IN_H, @PKG@.AbilCfg.Y_IN_C, 3)
                                    : sanctAt(pr, st, u, k, aw, at, now, @PKG@.AbilCfg.Y_RADIUS, @PKG@.AbilCfg.Y_TIME, @PKG@.AbilCfg.Y_HEAL, @PKG@.AbilCfg.Y_CUT, sh);
        extra = spotText(zy) + " heal=" + @PKG@.AbilMath.fmt(zy.pct) + " cut=" + @PKG@.AbilMath.fmt(zy.cut) + (zy.follow ? " follow" : "");
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
    failed = "failed";
  }
  if (failed != null) return failed;
  String lvx = cx.lvl > 1 ? " lv=" + cx.lvl : "";
  String mds = (cx.m0 >= 0 ? " m0=" + @PKG@.AbilModDefs.MID[cx.m0] + cx.l0 : "") + (cx.m1 >= 0 ? " m1=" + @PKG@.AbilModDefs.MID[cx.m1] + cx.l1 : "");
  return "ok:" + id + (crouch && slot < 2 ? " crouch" : "") + (sh != 0 ? " shape=" + @PKG@.AbilDefs.SHAPES[sh] : "") + " mana=" + @PKG@.AbilMath.fmt(mana) + " stamina=" + @PKG@.AbilMath.fmt(stam) + lvx + mds + " main=" + @PKG@.AbilMath.fmt(cx.main) + " cd=" + cd + extra + (door == 1 ? " key" : (door == 2 ? " marker" : ""));
}''')
# the dispatch of one delayed job (0.1.21's runJob + kind 9 Lingering, kind 10 Echo); runJob puts the job's context around it
late(r'''
public static boolean runJob0(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (j.kind == 1) { meteorImpact(j, st, cb); return false; }
  if (j.kind == 2) return hotTick(j, st, cb);
  if (j.kind == 3) return landTick(j, st, cb, now);
  if (j.kind == 5) return starTick(j, st, cb, now);
  if (j.kind == 6) return beamTick(j, st, cb, now);
  if (j.kind == 7) { chanRun(j, st, cb, now); return false; }
  if (j.kind == 8) {
    @REF@ cr = casterRef(cb, j.caster);
    if (live(cb, cr, j.caster, j.pkey)) novaRun(j, cb, cr, now);
    return false;
  }
  if (j.kind == 9) return burnTick(j, st, cb, now);
  if (j.kind == 10) return echoRun(j, st, cb, now);
  return false;
}''')
# one zone tick (0.1.21's zoneTick + Follow); zoneTick puts the zone's context around it
late(r'''
public static boolean zoneTick0(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind >= 3) return zoneTick2(z, st, cb, now);
  if (z.follow && !z.ended) zoneFollow(z, cb);
  if (z.kind == 1 && !z.ended) {
    @REF@ cr = null;
    try { cr = ((@ES@) cb.getExternalData()).getRefFromUUID(z.caster); } catch (Throwable t) { cr = null; }
    if (cr == null || !cr.isValid() || !alive(cb, cr) || (z.pkey != null && !z.pkey.equals(@PKG@.ClassCfg.pkey(z.caster)))) {
      z.why = "left";
    } else {
      double mana = cur(map(cb, cr), @DST@.getMana());
      if (mana >= 0.0 && mana <= 0.01) { z.ended = true; z.why = "mana"; }
    }
    if ("left".equals(z.why)) { zoneEnd(z, cb); return false; }
  }
  if (z.ended) { zoneEnd(z, cb); return false; }
  boolean xp = xpOk(z, st, cb);
  if (z.kind == 2) {
    while (z.pulsesDone < z.pulsesDue && z.pulsesDone < 4) {
      z.pulsesDone = z.pulsesDone + 1;
      pulse(z, st, cb, xp);
    }
    payXp(z, xp);
    if (!(z.hp > 0.0)) { z.why = "broken"; zoneEnd(z, cb); return false; }
    if (z.nextHeal > 0L && now >= z.nextHeal) layerRegrow(z, now);   // fix round: Layered Ward
  }
  if (now >= z.until) { z.why = "time"; zoneEnd(z, cb); return false; }
  if (now >= z.nextFx) {
    z.nextFx = now + 1000L;
    ring(z.kind == 1 ? FX_BARRIER : FX_BUBBLE, z, cb);
  }
  return true;
}''')
late(r'''
public static java.util.UUID uOfKey(String k) {
  try { return k == null || k.length() < 36 ? null : java.util.UUID.fromString(k.substring(0, 36)); } catch (Throwable t) { return null; }
}''')
late(r'''
public static boolean rolling(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    if (!(o instanceof @MSC@)) return false;
    @MST@ m = ((@MSC@) o).getMovementStates();
    return m != null && m.rolling;
  } catch (Throwable t) { return false; }
}''')

rep('''           "public double brkAmt;"):   # FIX 2: brkAmt = Frost Nova's break damage (ab.FrostNova.breakPower x staff hit)
    F(abjob, _f)''', '''           "public double brkAmt;",    # FIX 2: brkAmt = Frost Nova's break damage (ab.FrostNova.breakPower x staff hit)
           "public @PKG@.AbilCtx cx;"):   # 0.1.22: the cast's resolved numbers (levels, modifiers, tree); kind 9 = Lingering, 10 = Echo
    F(abjob, jv(_f))''')
rep('''  this.left = 0;
  this.every = 0L;
  this.hits = -1;
}""")''', '''  this.left = 0;
  this.every = 0L;
  this.hits = -1;
  this.cx = @PKG@.AbilCtx.get();
}""")''')
rep('''           "public double brkAmt;"):   # FIX 2: Frost Wake's break damage
    F(abzone, _f)''', '''           "public double brkAmt;",    # FIX 2: Frost Wake's break damage
           # 0.1.22: the cast's context, the zone follows its caster (Follow / Phase Step), H at the cast (Thorned Bubble, Aegis), the
           # echo bubble was made (Shield Bubble Echo), the next cleanse (Dawnlight), the pull (kind 7 = Arch-Mage's star well)
           "public @PKG@.AbilCtx cx;", "public boolean follow;", "public double h;", "public boolean echoed;", "public long nextCleanse;"):
    F(abzone, jv(_f))''')
rep('''  this.nextFx = start + 1000L;
  this.why = "";
  this.healed = new java.util.HashMap();
}""")''', '''  this.nextFx = start + 1000L;
  this.why = "";
  this.healed = new java.util.HashMap();
  this.cx = @PKG@.AbilCtx.get();
  this.nextCleanse = start + 2000L;
}""")''')

# ================================================================================================ inject the late methods + the new classes
late(r'''
public static String levelLine(java.util.UUID u, int ai) {
  if (u == null || ai < 0) return "";
  java.util.Properties p = @PKG@.AbilStore.load(@PKG@.ClassCfg.pkey(u));
  long uses = numOf(p, "u." + @PKG@.AbilDefs.IDS[ai]);
  return levelText(ai, alvl(uses), uses);
}''')
# the knockback config (the vanilla dagger dash's VelocityConfig, SkyyArmory's knockback numbers) - read from Assets.zip at build time
rep('''RUNE_FILES = {}
''', '''RUNE_FILES = {}
_DASHI = [n for n in _ASSETS.namelist() if n.startswith("Server/Item/Interactions/") and n.endswith("/Daggers_Dash_Backward.json")]
assert len(_DASHI) == 1, "the vanilla dagger dash moved"
_DASH = json.loads(_ASSETS.read(_DASHI[0]).decode("utf-8-sig"))["Interactions"][0]["VelocityConfig"]
assert _DASH["Style"] == "Exp" and all(k in _DASH for k in ("AirResistance", "AirResistanceMax", "GroundResistance", "GroundResistanceMax", "Threshold")), _DASH
''')
# the late bodies, the new classes and the systems go in right before the plugin
rep('''# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")''', r'''# =====================================================================================================================
# 0.1.22: THE RUNE ROUTE CLASSES (the hook, the guard, the tasks) + the panel bridges for SkyyTrees 0.3.7; then the Abil late bodies
# =====================================================================================================================
# AbilRuneSys: EntityEventSystem<InteractionChainStartEvent> on players (the SkyyAbilityProbe P1 hook shape, VERIFIED class in the jar)
abrune = pool.makeClass(PKG + ".AbilRuneSys", pool.get(T["EES"]))
F(abrune, "public static boolean FAILED_ONCE = false;")
C(abrune, "public AbilRuneSys() { super(@ICSE@.class); }")
M(abrune, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(abrune, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || !(ev instanceof @ICSE@) || !@PKG@.AbilCfg.PART || !@PKG@.AbilCfg.RUNE_KEYS) return;
    @ICSE@ e = (@ICSE@) ev;
    String ty = String.valueOf(e.getType());
    int key = "Ability2".equals(ty) ? 0 : ("Ability3".equals(ty) ? 1 : -1);
    if (key < 0) return;
    @PKG@.Abil.onRune(e, key, chunk.getReferenceTo(idx), st, buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ClassCfg.warn("the ability key hook failed (logged once, /cast still works): " + t); }
  }
}""")
# AbilInvSys: EntityEventSystem<InventoryChangeEvent> on players (the SkyyGear GearInvSys / probe P4 watch shape)
abinv = pool.makeClass(PKG + ".AbilInvSys", pool.get(T["EES"]))
F(abinv, "public static boolean FAILED_ONCE = false;")
C(abinv, "public AbilInvSys() { super(@ICE@.class); }")
M(abinv, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(abinv, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || !(ev instanceof @ICE@)) return;
    @PKG@.Abil.onInv((@ICE@) ev, chunk.getReferenceTo(idx), buf);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ClassCfg.warn("the ability rune guard failed (logged once): " + t); }
  }
}""")
# the three world-thread tasks (outside every system: the /cast state of the world)
abrc = pool.makeClass(PKG + ".RuneCast")
abrc.addInterface(pool.get("java.lang.Runnable"))
F(abrc, "public @PR@ pr;")
F(abrc, "public int key;")
F(abrc, "public int door;")
C(abrc, "public RuneCast(@PR@ pr, int key, int door) { this.pr = pr; this.key = key; this.door = door; }")
M(abrc, r"""
public void run() {
  try { @PKG@.Abil.runeCast(this.pr, this.key, this.door); }
  catch (Throwable t) { @PKG@.ClassCfg.warnLimited("an ability key cast failed: " + t); }
  @PKG@.AbilCtx.put(null);
}""")
abmt = pool.makeClass(PKG + ".MirrorTask")
abmt.addInterface(pool.get("java.lang.Runnable"))
F(abmt, "public @PR@ pr;")
C(abmt, "public MirrorTask(@PR@ pr) { this.pr = pr; }")
M(abmt, r"""
public void run() {
  try { @PKG@.Abil.mirrorNow(this.pr); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability rune mirror failed: " + t); }
}""")
abic = pool.makeClass(PKG + ".InvClean")
abic.addInterface(pool.get("java.lang.Runnable"))
F(abic, "public @PR@ pr;")
C(abic, "public InvClean(@PR@ pr) { this.pr = pr; }")
M(abic, r"""
public void run() {
  try { @PKG@.Abil.cleanNow(this.pr); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability rune clean-up failed: " + t); }
}""")
# the panel bridges (SkyyTrees 0.3.7): any thread, never throw
abpf = pool.makeClass(PKG + ".AbilPanelFn")
abpf.addInterface(pool.get("java.util.function.Function"))
C(abpf, "public AbilPanelFn() { }")
M(abpf, r"""
public Object apply(Object o) {
  try {
    if (o instanceof java.util.UUID) return @PKG@.Abil.panel((java.util.UUID) o, null, false);
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 1 || !(a[0] instanceof java.util.UUID)) return null;
    boolean has = a.length > 1;
    return @PKG@.Abil.panel((java.util.UUID) a[0], has && a[1] instanceof String ? (String) a[1] : null, has);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class:fn:abilPanel failed: " + t); return null; }
}""")
abmf = pool.makeClass(PKG + ".AbilModsFn")
abmf.addInterface(pool.get("java.util.function.Function"))
C(abmf, "public AbilModsFn() { }")
M(abmf, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return null;
    String csv = a.length > 2 && a[2] instanceof String ? (String) a[2] : null;
    if (a.length <= 2) csv = @PKG@.Abil.treeCsv((java.util.UUID) a[0]);
    return @PKG@.Abil.modRows((java.util.UUID) a[0], (String) a[1], csv);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class:fn:abilMods failed: " + t); return null; }
}""")
abdf = pool.makeClass(PKG + ".AbilDoFn")
abdf.addInterface(pool.get("java.util.function.Function"))
C(abdf, "public AbilDoFn() { }")
M(abdf, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "-Bad arguments.";
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return "-Bad arguments.";
    java.util.UUID u = (java.util.UUID) a[0];
    String x = a.length > 2 && a[2] != null ? String.valueOf(a[2]) : "";
    String y = a.length > 3 && a[3] != null ? String.valueOf(a[3]) : "";
    String csv = a.length > 4 && a[4] instanceof String ? (String) a[4] : null;
    if (a.length <= 4) csv = @PKG@.Abil.treeCsv(u);
    else @PKG@.AbilStore.TREEC.put(u, new Object[] { @PKG@.ClassCfg.pkey(u), Long.valueOf(System.currentTimeMillis()), csv });
    return @PKG@.Abil.doAction(u, (String) a[1], x, y, csv);
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class:fn:abilDo failed: " + t); return "-Something went wrong - nothing changed (see the server log)."; }
}""")
abuf = pool.makeClass(PKG + ".AbilUnlockFn")
abuf.addInterface(pool.get("java.util.function.Function"))
C(abuf, "public AbilUnlockFn() { }")
M(abuf, r"""
public Object apply(Object o) {
  try {
    int l = o instanceof Number ? ((Number) o).intValue() : Integer.parseInt(String.valueOf(o).trim());
    if (l < 1 || l > 4) return null;
    return Long.valueOf(@PKG@.AbilDefs.unlock(l == 4 ? 3 : l - 1));
  } catch (Throwable t) { return null; }
}""")
# THE LATE BODIES (every class above exists now)
for _src in ABIL_LATE:
    _sig = _src.strip().split("{", 1)[0]
    _name = _sig.split("(")[0].split()[-1]
    _ms = [_m for _m in abil.getDeclaredMethods() if str(_m.getName()) == _name]
    assert len(_ms) == 1, "Abil.%s: %d methods" % (_name, len(_ms))
    _body = _src.strip()[len(_sig):].strip()
    # setBody knows the parameters only as $1, $2 ... (no names after CtNewMethod.make): each name becomes a local copy of its $n
    _ps = [p_.strip() for p_ in _sig[_sig.index("(") + 1:_sig.rindex(")")].split(",") if p_.strip()]
    _pre = "".join(" %s %s = $%d;" % (p_.rsplit(" ", 1)[0].strip(), p_.rsplit(" ", 1)[1].strip(), i_ + 1) for i_, p_ in enumerate(_ps))
    assert _body.startswith("{") and _body.endswith("}"), _name
    _body = "{" + _pre + "\n" + _body[1:]
    try:
        _ms[0].setBody(jv(_body))
    except Exception as _e:
        raise SystemExit("late body failed in Abil.%s: %s\n%s" % (_name, _e, jv(_body)[:4000]))
print("Abil: %d late bodies set" % len(ABIL_LATE))

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")''')

# ================================================================================================ engine names + probes (0.1.22)
rep('''    "OVB":  "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior",
}
''', '''    "OVB":  "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior",
    # 0.1.22: the rune route (the SkyyAbilityProbe 0.1 names, VERIFIED in the 0.7.0 release jar), the knockback (SkyyArmory's shapes)
    "EES":  "com.hypixel.hytale.component.system.EntityEventSystem",
    "ICSE": "com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent",
    "ICTX": "com.hypixel.hytale.server.core.entity.InteractionContext",
    "ICE":  "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent",
    "ABS":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots",
    "RNB":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$RuneBag",
    "IMOD": "com.hypixel.hytale.server.core.modules.interaction.InteractionModule",
    "IMGR": "com.hypixel.hytale.server.core.entity.InteractionManager",
    "CDH":  "com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler",
    "CDN":  "com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler$Cooldown",
    "VEL":  "com.hypixel.hytale.server.core.modules.physics.component.Velocity",
    "VCF":  "com.hypixel.hytale.server.core.modules.splitvelocity.VelocityConfig",
    "CVT":  "com.hypixel.hytale.protocol.ChangeVelocityType",
    "VTS":  "com.hypixel.hytale.protocol.VelocityThresholdStyle",
}
''')
rep('''assert str(pool.get(T["LPC"]).getMethod("getProjectileAssetName", "()Ljava/lang/String;").getName()) == "getProjectileAssetName"
''', '''assert str(pool.get(T["LPC"]).getMethod("getProjectileAssetName", "()Ljava/lang/String;").getName()) == "getProjectileAssetName"
# 0.1.22 (the rune route, levels + modifiers): every new engine member with the descriptor the code calls
def _dsc(c):
    return "L" + c.replace(".", "/") + ";"
for c, m, d in ((T["ICSE"], "getType", "()Lcom/hypixel/hytale/protocol/InteractionType;"), (T["ICSE"], "getContext", "()" + _dsc(T["ICTX"])),
                (T["ICSE"], "setCancelled", "(Z)V"), (T["ICTX"], "getHeldItem", "()" + _dsc(T["IS"])), (T["ICTX"], "getHeldItemSectionId", "()I"),
                (T["ICE"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"), (T["ICE"], "getItemContainer", "()" + _dsc(T["IC"])),
                (T["ABS"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (T["RNB"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (T["INVC"], "getInventory", "()" + _dsc(T["IC"])),
                (T["IC"], "addItemStackToSlot", "(S" + _dsc(T["IS"]) + ")Lcom/hypixel/hytale/server/core/inventory/transaction/ItemStackSlotTransaction;"),
                (T["IC"], "removeItemStackFromSlot", "(S)Lcom/hypixel/hytale/server/core/inventory/transaction/SlotTransaction;"),
                (T["IC"], "getItemStack", "(S)" + _dsc(T["IS"])), (T["IC"], "getCapacity", "()S"),
                (T["ECC"], "hasEffect", "(I)Z"), (T["ECC"], "removeEffect", "(Lcom/hypixel/hytale/component/Ref;ILcom/hypixel/hytale/component/ComponentAccessor;)V"),
                (T["IMOD"], "get", "()" + _dsc(T["IMOD"])), (T["IMOD"], "getInteractionManagerComponent", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (T["CDH"], "getCooldown", "(Ljava/lang/String;F[FZZ)" + _dsc(T["CDN"])), (T["CDN"], "setCooldownMax", "(F)V"), (T["CDN"], "resetCooldown", "()V"),
                (T["VEL"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (T["VEL"], "addInstruction", "(" + _dsc(T["VEC"]) + _dsc(T["VCF"]) + _dsc(T["CVT"]) + ")V"),
                (T["VCF"], "setAirResistance", "(F)V"), (T["VCF"], "setAirResistanceMax", "(F)V"), (T["VCF"], "setGroundResistance", "(F)V"),
                (T["VCF"], "setGroundResistanceMax", "(F)V"), (T["VCF"], "setThreshold", "(F)V"), (T["VCF"], "setStyle", "(" + _dsc(T["VTS"]) + ")V"),
                (T["INV"], "getStorage", "()" + _dsc(T["IC"])), (T["INV"], "getBackpack", "()" + _dsc(T["IC"])), (T["INV"], "getUtility", "()" + _dsc(T["IC"])),
                (T["INV"], "getTools", "()" + _dsc(T["IC"])), (T["INV"], "getArmor", "()" + _dsc(T["IC"])), (T["INV"], "getHotbar", "()" + _dsc(T["IC"])),
                (T["WLD"], "execute", "(Ljava/lang/Runnable;)V"), (T["ES"], "getWorld", "()" + _dsc(T["WLD"]))):
    try:
        assert str(pool.get(c).getMethod(m, d).getName()) == m
    except Exception as _e:
        raise SystemExit("0.1.22 API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
pool.get(T["IS"]).getConstructor("(Ljava/lang/String;I)V")
pool.get(T["ICTX"])
for c, f in ((T["INVC"], "ABILITIES_SECTION_ID"), (T["INVC"], "RUNE_BAG_SECTION_ID"), (T["IMGR"], "DEFAULT_CHARGE_TIMES"), (T["CVT"], "Set"),
             (T["VTS"], "Exp"), (T["MST"], "rolling")):
    B.probe(pool, c, f)
assert int(pool.get(T["INVC"]).getField("ABILITIES_SECTION_ID").getConstantValue()) == -11, "the ability section id is -11"
for c, f in ((T["IMGR"], "cooldownHandler"),):
    pool.get(c).getDeclaredField(f)    # abil.runeCooldownFill reads it by reflection (no getter) - the build stops if it is gone
assert pool.get(T["ICSE"]).subtypeOf(pool.get("com.hypixel.hytale.component.system.CancellableEcsEvent")), "the chain start is cancellable"
assert pool.get(T["ICE"]).subtypeOf(pool.get(T["EV"])) and pool.get(T["ABS"]).subtypeOf(pool.get(T["INVC"])) and pool.get(T["RNB"]).subtypeOf(pool.get(T["INVC"]))
# the engine does what the hook relies on (bytecode, read-only): a cancelled chain start -> InteractionManager.sendCancelPacket; the rune's
# cooldown is armed by TriggerCooldownInteraction INSIDE the cast chain (a chain cancelled at its start never reaches it)
def _calls(cls, meth):
    out = []
    for mi in pool.get(cls).getClassFile2().getMethods():
        if str(mi.getName()) != meth or mi.getCodeAttribute() is None:
            continue
        cp, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
        while it.hasNext():
            p = it.next()
            op = it.byteAt(p)
            if op in (0xb6, 0xb7, 0xb8, 0xb9):
                i = it.u16bitAt(p + 1)
                if op == 0xb9:
                    out.append(str(cp.getInterfaceMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cp.getInterfaceMethodrefName(i)))
                else:
                    out.append(str(cp.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cp.getMethodrefName(i)))
    return out
_sync = _calls(T["IMGR"], "syncStart")
assert "InteractionChainStartEvent.isCancelled" in _sync and "InteractionManager.sendCancelPacket" in _sync[_sync.index("InteractionChainStartEvent.isCancelled"):][:8], \
    "InteractionManager.syncStart no longer sends a cancel packet after a cancelled InteractionChainStartEvent"
_trig = _calls("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.TriggerCooldownInteraction", "firstRun")
assert "CoreItemAbility.getCastRootId" in _trig, "TriggerCooldownInteraction no longer keys the rune cooldown by its Cast root id"
assert "Item.getWeapon" in _calls("com.hypixel.hytale.server.core.asset.type.item.config.CoreItemAbility", "canUseWith"), "canUseWith no longer needs a Weapon block"
''')

# ================================================================================================ the changed Abil methods (0.1.22)
# the pipeline: castAt = castAt0 (the late method) with the context cleared afterwards whatever happens; door 0 = /cast
replace_method("abil", "public static String castAt(", r'''
public static String castAt(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String arg, int forced, int door) {
  String r = "bad";
  try { r = castAt0(pr, st, ref, w, arg, forced, door); }
  finally { @PKG@.AbilCtx.put(null); }
  return r;
}''')
rep_in("abil", "public static String castNow(", "  return castAt(pr, st, ref, w, arg, -1);", "  return castAt(pr, st, ref, w, arg, -1, 0);")
rep_in("abil", "public static String adminShape(", "  String r = castAt(pr, st, ref, w, slot, sh);", "  String r = castAt(pr, st, ref, w, slot, sh, 3);")
# a job / a zone runs with the context of the cast that made it
replace_method("abil", "public static boolean runJob(", r'''
public static boolean runJob(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (j == null) return false;
  boolean again = false;
  @PKG@.AbilCtx.put(j.cx);
  try { again = runJob0(j, st, cb, now); }
  finally { @PKG@.AbilCtx.put(null); }
  return again;
}''')
replace_method("abil", "public static boolean zoneTick(", r'''
public static boolean zoneTick(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  boolean keep = false;
  @PKG@.AbilCtx.put(z.cx);
  try { keep = zoneTick0(z, st, cb, now); }
  finally { @PKG@.AbilCtx.put(null); }
  return keep;
}''')
# METEOR: the impact (+ the counted use, Lingering, Arch-Mage's star well, Brilliance)
replace_method("abil", "public static int meteorImpact(", r'''
public static int meteorImpact(@PKG@.AbilJob j, @ST@ st, @CB@ cb) {
  particle(FX_HIT, j.x, j.y + 0.5, j.z, cb);
  @REF@ cr = null;
  try { cr = ((@ES@) cb.getExternalData()).getRefFromUUID(j.caster); } catch (Throwable t) { cr = null; }
  if (cr == null || !cr.isValid()) { j.hits = 0; return 0; }
  if (j.pkey != null && !j.pkey.equals(@PKG@.ClassCfg.pkey(j.caster))) { j.hits = 0; return 0; }
  @PKG@.AbilCtx c = j.cx;
  boolean echo = c != null && c.echo;
  java.util.List l = near(cb, j.x, j.y, j.z, j.r);
  java.util.HashSet seen = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!seen.add(t)) continue;
    if (!enemy(cb, t, cr)) continue;
    if (hit(cb, t, cr, j.caster, j.amount, "Meteor")) { n++; seenAdd(c, t); }
  }
  j.hits = n;
  @PR@ pr = @UNI@.get().getPlayer(j.caster);
  if (pr != null) say(pr, (echo ? "Echo: " : "") + (n == 0 ? "Meteor hit nothing." : "Meteor hit " + n + (n == 1 ? " enemy" : " enemies") + " (" + @PKG@.AbilMath.fmt(j.amount) + " damage each before armour)."));
  if (c == null || echo) return n;
  if (n > 0) used(j.caster, j.pkey, @PKG@.AbilDefs.METEOR, c);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  long now = System.currentTimeMillis();
  if (aw != null && c.has(@PKG@.AbilModDefs.LINGER)) {
    int lv = c.lv(@PKG@.AbilModDefs.LINGER);
    @PKG@.AbilJob b = new @PKG@.AbilJob(9, now + 1000L, j.caster, "Meteor", j.x, j.y, j.z, j.r * 0.8, j.amount * (0.08 + 0.02 * (double) (lv - 1)));
    b.pkey = j.pkey;
    b.ai = @PKG@.AbilDefs.METEOR;
    b.left = (int) Math.round(3.0 + 0.5 * (double) (lv - 1));   // second fix round: Mage.md (Locked) "the ground keeps burning for 3 s" at Lv 1
    b.every = 1000L;
    b.cx = c;
    aw.add(b);
  }
  if (aw != null && "Mage".equals(c.cls) && c.node("PC5")) {
    @PKG@.AbilZone wz = new @PKG@.AbilZone(7, j.caster, j.x, j.y, j.z, j.r + 2.0, now, now + 2000L);
    wz.pkey = j.pkey;
    wz.name = "";
    wz.cx = c;
    wz.nextFx = now;
    aw.addZone(wz);
  }
  brilliance(c, cb, cr);
  return n;
}''')
# SACRED HEAL (walking): + Radius+ / Power+ / Duration+ / Efficiency, the tree (Wide Prayer, Warm Light, Cleanse, Lightbringer), Echo, the use
replace_method("abil", "public static String healCast(", r'''
public static String healCast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, @PKG@.AbilWorld aw, long now) {
  @VEC@ c = pos(st, ref);
  if (c == null) return " nopos";
  @PKG@.AbilCtx cx = @PKG@.AbilCtx.get();
  double rad = @PKG@.AbilCfg.S_RADIUS + cxr();
  boolean light = cx != null && "Priest".equals(cx.cls) && cx.node("PA5");
  boolean cln = cx != null && "Priest".equals(cx.cls) && cx.node("PA1");
  double pct = ((double) @PKG@.AbilCfg.S_HEAL + (cx == null ? 0.0 : cx.pctAdd)) * cxm();
  long selfB = light ? 40L : @PKG@.AbilCfg.S_SELF;
  double hotPct = (double) @PKG@.AbilCfg.S_HOT + (cx == null ? 0.0 : cx.hotAdd);
  boolean xpOk = !creative(st, ref);
  String healer = pr.getUsername();
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  us.add(u);
  rs.add(ref);
  gather(st, u, c, rad, us, rs);
  int n = us.size();
  java.util.UUID[] tu = new java.util.UUID[n];
  double[] want = new double[n];
  double[] per = new double[n];
  double[] done = new double[n];
  double[] cap = new double[n];
  boolean[] go = new boolean[n];
  int ticks = @PKG@.AbilMath.ticks(@PKG@.AbilCfg.S_HOT_TIME * cxd());
  for (int i = 0; i < n; i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    tu[i] = t;
    if (!healable(st, r)) continue;
    @ESM@ tm = map(st, r);
    double mx = max(tm, @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(u);
    boolean party = isSelf || @PKG@.HealTask.inParty(u, t);
    double w0 = @PKG@.AbilMath.heal(mx, 100L, isSelf, selfB) * pct / 100.0;
    if (light && !isSelf && cur(tm, @DST@.getHealth()) < mx * 0.3) w0 = w0 * 1.25;
    want[i] = @PKG@.HealTask.split(w0, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    cap[i] = @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, 0.0);
    if (ticks > 0) per[i] = want[i] * hotPct / 100.0 / (double) ticks;
    go[i] = true;
  }
  @PKG@.AbilJob j = null;
  if (ticks > 0 && hotPct > 0.0) {
    long every = Math.round(@PKG@.AbilCfg.S_HOT_TIME * cxd() * 1000.0 / (double) ticks);
    if (every < 50L) every = 50L;
    j = new @PKG@.AbilJob(2, now + every, u, "SacredHeal", c.x, c.y, c.z, rad, 0.0);
    j.targets = tu;
    j.per = per;
    j.done = done;
    j.cap = cap;
    j.left = ticks;
    j.every = every;
    j.name = healer;
    j.pkey = @PKG@.ClassCfg.pkey(u);
  }
  double others = 0.0;
  double self = 0.0;
  int healed = 0;
  int cleansed = 0;
  try {
    for (int i = 0; i < n; i++) {
      if (!go[i]) continue;
      java.util.UUID t = tu[i];
      @REF@ r = (@REF@) rs.get(i);
      double got = apply(st, r, want[i], cap[i]);
      done[i] = got;
      if (cln) cleansed = cleansed + cleanse(st, r);
      @VEC@ q = pos(st, r);
      if (q != null) particle(FX_HEAL, q.x, q.y + 1.0, q.z, st);
      if (!(got > 0.0)) continue;
      healed++;
      if (t.equals(u)) { self = self + got; @PKG@.HealMsg.given(u, u, got); }
      else { others = others + got; @PKG@.HealMsg.given(u, t, got); @PKG@.HealMsg.taken(t, u, healer, got); }
    }
    if (xpOk) {
      if (others > 0.0) @PKG@.HealTask.xp(u, others);
      if (self > 0.0) @PKG@.HealTask.xpSelf(u, self);
    }
    if (j != null) aw.add(j);
  } catch (Throwable x) {
    @PKG@.ClassCfg.warn("Sacred Heal stopped after " + healed + " heal(s) - no refund (heals already landed), no XP, no heal over time: " + x);
    return " partial healed=" + healed + " hp=" + @PKG@.AbilMath.fmt(others + self);
  }
  say(pr, "Sacred Heal: " + (healed == 0 ? "nobody needed healing" : "+" + @PKG@.AbilMath.fmt(others + self) + " HP to " + healed + (healed == 1 ? " player" : " players")) + (j != null ? ", healing over " + ticks + " s." : ".") + (cleansed > 0 ? " Cleansed " + cleansed + "." : ""));
  if (healed > 0) used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.SACRED, cx);
  if (cx != null) echoJob(aw, cx, @PKG@.AbilDefs.SACRED, 0, c.x, c.y, c.z, @PKG@.AbilCfg.S_RADIUS + cx.radTree, 0.0, now + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0));
  return " targets=" + n + " healed=" + healed + " hp=" + @PKG@.AbilMath.fmt(others + self) + (cleansed > 0 ? " cleansed=" + cleansed : "");
}''')
rep_in("abil", "public static int needHeal(", "  gather(st, u, c, @PKG@.AbilCfg.S_RADIUS, us, rs);", "  gather(st, u, c, @PKG@.AbilCfg.S_RADIUS + cxr(), us, rs);")
rep_in("abil", "public static @PKG@.AbilZone blessAt(", "@PKG@.AbilCfg.S_BLESS_R, now, now + life);", "@PKG@.AbilCfg.S_BLESS_R + cxr(), now, now + life);")
rep_in("abil", "public static int blessTick(", "@PKG@.AbilMath.heal(mx, @PKG@.AbilCfg.S_BLESS_H, isSelf, @PKG@.AbilCfg.S_SELF), party",
       "@PKG@.AbilMath.heal(mx, @PKG@.AbilCfg.S_BLESS_H, isSelf, @PKG@.AbilCfg.S_SELF) * cxm(), party")
rep_in("abil", "public static @PKG@.AbilZone wakeAt(", "  z.freeze = @PKG@.AbilCfg.F_WAKE_F;", "  z.freeze = @PKG@.AbilCfg.F_WAKE_F * cxd();")
rep_in("abil", "public static void graceTargets(", "  long most = @PKG@.AbilCfg.G_TARGETS;",
       "  @PKG@.AbilCtx gcx = @PKG@.AbilCtx.get();\n  long most = @PKG@.AbilCfg.G_TARGETS + (gcx == null ? 0L : (long) gcx.eff(@PKG@.AbilModDefs.CHAIN));")
rep_in("abil", "public static String chanRun(", "healAt(pr, st, cb, cr, j.caster, at, @PKG@.AbilCfg.S_RADIUS, ", "healAt(pr, st, cb, cr, j.caster, at, @PKG@.AbilCfg.S_RADIUS + cxr(), ")
# the end of a Mana Barrier / Shield Bubble: + the counted use, Knockback+, Charged Dome, Aegis, the bubble's Echo
replace_method("abil", "public static void zoneEnd(", r'''
public static void zoneEnd(@PKG@.AbilZone z, @CAC@ acc) {
  z.ended = true;
  particle("broken".equals(z.why) ? FX_BREAK : FX_END, z.x, z.y + 1.0, z.z, acc);
  if ("left".equals(z.why)) return;
  @PR@ pr = @UNI@.get().getPlayer(z.caster);
  if (pr != null) say(pr, endLine(z));
  @PKG@.AbilCtx c = z.cx;
  boolean echo = c != null && c.echo;
  if (!echo && z.absorbed >= 4.0) used(z.caster, z.pkey, z.kind == 1 ? @PKG@.AbilDefs.MANAB : @PKG@.AbilDefs.BUBBLE, c);
  if (c == null || echo || !(acc instanceof @CB@)) return;
  @CB@ cb = (@CB@) acc;
  @REF@ cr = null;
  try { cr = ((@ES@) cb.getExternalData()).getRefFromUUID(z.caster); } catch (Throwable t) { cr = null; }
  if (cr == null || !cr.isValid()) return;
  if (z.kind == 1 && c.has(@PKG@.AbilModDefs.KNOCK)) knockArea(cb, cr, z.x, z.y, z.z, z.r + 1.0, 8.0 + 2.0 * (double) (c.eff(@PKG@.AbilModDefs.KNOCK) - 1));
  if (z.kind == 1 && "Mage".equals(c.cls) && c.node("PC3") && z.absorbed > 0.0) {
    int nb = burst(cb, cr, z.caster, z.x, z.y, z.z, 4.0, z.absorbed * 0.5, "ManaBarrier");
    if (pr != null) say(pr, "Charged Dome burst: " + @PKG@.AbilMath.fmt(z.absorbed * 0.5) + " damage on " + nb + (nb == 1 ? " enemy." : " enemies."));
  }
  if (z.kind == 2 && "Priest".equals(c.cls) && c.node("PB5") && "broken".equals(z.why)) {
    int na = burst(cb, cr, z.caster, z.x, z.y, z.z, 4.0, 1.5 * z.h, "ShieldBubble");
    if (pr != null) say(pr, "Aegis: the bubble exploded on " + na + (na == 1 ? " enemy." : " enemies."));
  }
  if (z.kind == 2 && ("broken".equals(z.why) || "time".equals(z.why))) bubbleEcho(z, cb, System.currentTimeMillis());
}''')

# FROST NOVA: + Radius+ / Duration+ (longer freeze) / Slow (+1 s chill a level), the counted use, Brilliance
replace_method("abil", "public static @PKG@.AbilJob novaJob(", r'''
public static @PKG@.AbilJob novaJob(java.util.UUID u, String pkey, double[] at, double r, double amount, double freeze, double brk, double chill, long now, int sh) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  @PKG@.AbilJob j = new @PKG@.AbilJob(8, now, u, "FrostNova", at[0], at[1], at[2], r + cxr(), amount);
  j.pkey = pkey;
  j.freeze = freeze * cxd();
  j.brk = brk;
  j.chill = chill + (c == null ? 0.0 : (double) c.eff(@PKG@.AbilModDefs.SLOW));
  j.sh = sh;
  j.ai = @PKG@.AbilDefs.FROST;
  return j;
}''')
replace_method("abil", "public static int novaRun(", r'''
public static int novaRun(@PKG@.AbilJob j, @CB@ cb, @REF@ cr, long now) {
  int n = nova(j, cb, cr, now);
  @PKG@.AbilCtx c = j.cx;
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.FROST, j.sh) + (n == 0 ? " froze nothing." : " froze " + n + (n == 1 ? " enemy" : " enemies") + " for " + @PKG@.AbilMath.fmt(j.freeze) + " s."));
  if (n > 0 && (c == null || !c.echo)) {
    used(j.caster, j.pkey, @PKG@.AbilDefs.FROST, c);
    if (c != null && n >= 3) {
      for (int i = 0; i < n; i++) seenAdd(c, Integer.valueOf(i));
      brilliance(c, cb, cr);
    }
  }
  return n;
}''')
# MANA BARRIER (every shape): Power+ = ratio, Duration+, Follow (80 % + 5 % a level), Ward, the tree (Barrier Lore, Charged Dome, Phase Step)
replace_method("abil", "public static @PKG@.AbilZone barrierAt(", r'''
public static @PKG@.AbilZone barrierAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, double[] at, long now, double r, double secs, double ratio, int sh) {
  double mh = max(map(acc, ref), @DST@.getHealth());
  if (!(mh > 0.0)) mh = 100.0;
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  boolean phase = c != null && "Mage".equals(c.cls) && c.node("PA3");
  boolean fol = c != null && (phase || c.has(@PKG@.AbilModDefs.FOLLOW));
  double rt = ratio * cxm();
  if (fol && !phase) rt = rt * (0.8 + 0.05 * (double) (c.lv(@PKG@.AbilModDefs.FOLLOW) - 1));
  long life = Math.round(cxds(secs) * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(1, u, at[0], at[1], at[2], r, now, now + life);
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.ratio = rt;
  z.cap = mh * (double) @PKG@.AbilCfg.B_MAX / 100.0;
  z.shape = sh;
  z.follow = fol;
  z.h = c == null ? 0.0 : c.h;
  if (fol) {
    @VEC@ p = pos(acc, ref);
    if (p != null) { z.x = p.x; z.y = p.y; z.z = p.z; }
  }
  ring(FX_BARRIER, z, acc);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.MANAB, sh) + ": a dome of " + @PKG@.AbilMath.fmt(z.r) + " blocks for " + @PKG@.AbilMath.secs(life) + " s - damage to you inside costs Mana (" + @PKG@.AbilMath.fmt(z.ratio) + " per Mana) instead of Health." + (fol ? " It moves with you." : ""));
  if (c != null && c.has(@PKG@.AbilModDefs.WARD)) wardArea(acc, u, z.x, z.y, z.z, 4.0, 3.0 * (double) c.lv(@PKG@.AbilModDefs.WARD), now + life);
  aw.addZone(z);
  return z;
}''')
# SHIELD BUBBLE (every shape): Power+ = HP, Radius+, Duration+, Follow, H for Thorned Bubble / Aegis (the tree), Echo at its end
replace_method("abil", "public static @PKG@.AbilZone bubbleAt(", r'''
public static @PKG@.AbilZone bubbleAt(@PR@ pr, @CAC@ acc, @REF@ ref, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, double[] at, long now, double r, long hpPct, int sh) {
  double mh = max(map(acc, ref), @DST@.getHealth());
  if (!(mh > 0.0)) mh = 100.0;
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  boolean fol = c != null && c.has(@PKG@.AbilModDefs.FOLLOW);
  long life = Math.round(cxds(@PKG@.AbilCfg.U_TIME) * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(2, u, at[0], at[1], at[2], r + cxr(), now, now + life);
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.hpMax = mh * (double) hpPct / 100.0 * cxm();
  z.hp = z.hpMax;
  z.shape = sh;
  z.follow = fol;
  z.h = c == null ? 0.0 : c.h;
  boolean lay = c != null && !c.echo && "Priest".equals(c.cls) && c.node("PB3");   // fix round: Layered Ward (Priest PB3)
  z.nextHeal = lay ? now + 1000L : 0L;
  if (fol) {
    @VEC@ p = pos(acc, ref);
    if (p != null) { z.x = p.x; z.y = p.y; z.z = p.z; }
  }
  particle(FX_BUBBLE_ON, z.x, z.y + 1.0, z.z, acc);
  ring(FX_BUBBLE, z, acc);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.BUBBLE, sh) + ": " + @PKG@.AbilMath.fmt(z.hpMax) + " HP for " + @PKG@.AbilMath.secs(life) + " s - it soaks attacks on you and your party inside and heals at 75 / 50 / 25 % and when it breaks." + (fol ? " It moves with you." : "") + (lay ? " Two layers: the inner half regrows 3 % a second." : ""));
  aw.addZone(z);
  return z;
}''')
# SANCTUARY (every shape): Power+ = the heal, Radius+, Duration+, Follow, Dawnlight (+2 blocks, 2 s shorter, cleanses every 2 s)
replace_method("abil", "public static @PKG@.AbilZone sanctAt(", r'''
public static @PKG@.AbilZone sanctAt(@PR@ pr, @CAC@ acc, java.util.UUID u, String pkey, @PKG@.AbilWorld aw, double[] at, long now, double r, double secs, long pct, long cut, int sh) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  long life = Math.round(cxds(secs) * 1000.0);
  @PKG@.AbilZone z = new @PKG@.AbilZone(5, u, at[0], at[1], at[2], r + cxr(), now, now + life);
  z.pkey = pkey;
  z.name = pr == null ? "" : pr.getUsername();
  z.pct = (double) pct * cxm();
  z.cut = (double) cut;
  z.shape = sh;
  z.follow = c != null && c.has(@PKG@.AbilModDefs.FOLLOW);
  z.nextHeal = now + 1000L;
  ring(FX_HOLY, z, acc);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SANCT, sh) + ": " + @PKG@.AbilMath.fmt(z.r) + " blocks for " + @PKG@.AbilMath.secs(life) + " s - you and your party inside heal " + @PKG@.AbilMath.fmt(z.pct) + " % a second and take " + cut + " % less damage." + (z.follow ? " It moves with you." : ""));
  aw.addZone(z);
  return z;
}''')
replace_method("abil", "public static void zoneEnd2(", r'''
public static void zoneEnd2(@PKG@.AbilZone z, @CAC@ acc) {
  z.ended = true;
  @PR@ pr = prOf(z.caster);
  boolean echo = z.cx != null && z.cx.echo;
  if (z.kind == 5) {
    particle(FX_END, z.x, z.y + 1.0, z.z, acc);
    if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SANCT, z.shape) + " faded (+" + @PKG@.AbilMath.fmt(z.absorbed) + " HP healed).");
    if (!echo && z.absorbed > 0.0) used(z.caster, z.pkey, @PKG@.AbilDefs.SANCT, z.cx);
    return;
  }
  if (z.kind == 4) {
    if (pr != null) say(pr, "Running Blessing ended - it touched " + z.hits + (z.hits == 1 ? " player" : " players") + " (+" + @PKG@.AbilMath.fmt(z.absorbed) + " HP, healing over time follows).");
    if (!echo && z.absorbed > 0.0) used(z.caster, z.pkey, @PKG@.AbilDefs.SACRED, z.cx);
    return;
  }
  if (z.kind == 3) {
    if (pr != null) say(pr, "Frost Wake melted - it froze " + z.hits + (z.hits == 1 ? " enemy." : " enemies."));
    if (!echo && z.hits > 0) used(z.caster, z.pkey, @PKG@.AbilDefs.FROST, z.cx);
  }
}''')
replace_method("abil", "public static boolean zoneTick2(", r'''
public static boolean zoneTick2(@PKG@.AbilZone z, @ST@ st, @CB@ cb, long now) {
  if (z.kind == 7) return wellTick(z, cb, now);
  if (z.kind == 5) {
    if (z.ended || now >= z.until) { zoneEnd2(z, cb); return false; }
    if (z.follow) zoneFollow(z, cb);
    if (now >= z.nextHeal) {
      z.nextHeal = z.nextHeal + 1000L;
      sanctPulse(z, st, cb, xpOk(z, st, cb));
    }
    if (z.cx != null && "Priest".equals(z.cx.cls) && z.cx.node("PA4") && now >= z.nextCleanse) { z.nextCleanse = now + 2000L; cleanseIn(st, cb, z); }
    if (now >= z.nextFx) { z.nextFx = now + 1000L; ring(FX_HOLY, z, cb); }
    return true;
  }
  @REF@ cr = casterRef(cb, z.caster);
  boolean ok = live(cb, cr, z.caster, z.pkey);
  if (!ok || z.ended || now >= z.until) { zoneEnd2(z, cb); return false; }
  if (z.kind == 3) {
    wakeTick(z, cb, cr, now);
    if (now >= z.nextFx) { z.nextFx = now + 1000L; wakeFx(z, cb); }
    return true;
  }
  if (z.kind == 4) {
    @VEC@ p = pos(cb, cr);
    if (p != null) { z.x = p.x; z.y = p.y; z.z = p.z; }
    blessTick(z, st, cb, now);
    if (now >= z.nextFx) { z.nextFx = now + 500L; ring(FX_BLESS, z, cb); }
    return true;
  }
  return false;
}''')
# the HEAL at a spot (Beacon, Kneel, the Sacred Heal Echo): the caller passes the full radius; + Power+, the tree, Cleanse, the counted use
replace_method("abil", "public static String healAt(", r'''
public static String healAt(@PR@ pr, @ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, double[] c, double rad, double mult, double hotMult, long now, String pkey, int sh) {
  boolean xpOk = !creative(acc, ref) && (pkey == null || pkey.equals(@PKG@.ClassCfg.pkey(u)));
  String healer = pr == null ? "" : pr.getUsername();
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  @PKG@.AbilCtx cx = @PKG@.AbilCtx.get();
  boolean echo = cx != null && cx.echo;
  boolean light = cx != null && "Priest".equals(cx.cls) && cx.node("PA5");
  boolean cln = cx != null && "Priest".equals(cx.cls) && cx.node("PA1");
  double pct = ((double) @PKG@.AbilCfg.S_HEAL + (cx == null ? 0.0 : cx.pctAdd)) * cxm();
  long selfB = light ? 40L : @PKG@.AbilCfg.S_SELF;
  double hotPct = ((double) @PKG@.AbilCfg.S_HOT + (cx == null ? 0.0 : cx.hotAdd)) * hotMult;
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  gatherAt(st, acc, c, rad, us, rs);
  double others = 0.0;
  double self = 0.0;
  int healed = 0;
  int hots = 0;
  int cleansed = 0;
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID t = (java.util.UUID) us.get(i);
    @REF@ r = (@REF@) rs.get(i);
    if (!healable(acc, r)) continue;
    @ESM@ tm = map(acc, r);
    double mx = max(tm, @DST@.getHealth());
    if (!(mx > 0.0)) continue;
    boolean isSelf = t.equals(u);
    boolean party = isSelf || @PKG@.HealTask.inParty(u, t);
    double w0 = @PKG@.AbilMath.heal(mx, 100L, isSelf, selfB) * pct / 100.0 * mult;
    if (light && !isSelf && cur(tm, @DST@.getHealth()) < mx * 0.3) w0 = w0 * 1.25;
    double want = @PKG@.HealTask.split(w0, party, @PKG@.ClassCfg.HEAL_OTHERS_PCT);
    double cap = @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, 0.0);
    double got = apply(acc, r, want, cap);
    if (cln) cleansed = cleansed + cleanse(acc, r);
    @PKG@.AbilJob h = hotPct > 0.0 ? hotJob(u, pkey, healer, t, want, got, cap, hotPct, c[0], c[1], c[2], rad, now) : null;
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
  if (pr != null) say(pr, (echo ? "Echo: " : "") + @PKG@.AbilDefs.sname(@PKG@.AbilDefs.SACRED, sh) + ": " + (healed == 0 ? "nobody needed healing" : "+" + @PKG@.AbilMath.fmt(others + self) + " HP to " + healed + (healed == 1 ? " player" : " players")) + (hots > 0 ? ", healing over time." : ".") + (cleansed > 0 ? " Cleansed " + cleansed + "." : ""));
  if (healed > 0 && !echo) used(u, pkey, @PKG@.AbilDefs.SACRED, cx);
  if (cx != null && !echo && aw != null) echoJob(aw, cx, @PKG@.AbilDefs.SACRED, sh, c[0], c[1], c[2], rad - cx.radAdd, 0.0, now + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0));
  return " healed=" + healed + " hp=" + @PKG@.AbilMath.fmt(others + self) + " hot=" + hots + (cleansed > 0 ? " cleansed=" + cleansed : "");
}''')
# SECOND FIX ROUND (critic: Chain in both slots at Lv 5 = 15 targets at 0 % drop): the drop cut stops at the single Lv 5 cut (1.6 x 5 =
# 8 %; Skyy's example Lv 5 = 10 targets at 7 %), so a doubled Chain adds targets but the falling heal still ends the chain (~11 at 7 %)
late(r'''
public static double chainCut(int e) {
  double c = 1.6 * (double) (e < 0 ? 0 : e);
  return c > 8.0 ? 8.0 : c;
}''')
# MARTYR'S GRACE: + Power+ (first heal), Chain (+1 target, -1.6 % drop a level), Ward (the overheal), Beacon (first -10, a 10 s regen), Echo
replace_method("abil", "public static String graceRun(", r'''
public static String graceRun(@PR@ pr, @ST@ st, @CAC@ acc, @REF@ ref, java.util.UUID u, int sh, String pkey) {
  double[] c = here(acc, ref);
  if (c == null) return " nopos";
  @PKG@.AbilCtx cx = @PKG@.AbilCtx.get();
  boolean echo = cx != null && cx.echo;
  boolean beacon = cx != null && "Priest".equals(cx.cls) && cx.node("PA3");
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList rs = new java.util.ArrayList();
  graceTargets(st, acc, u, c, graceFirst(acc, ref, u, sh), us, rs);
  double fp = ((sh == 3 ? (double) @PKG@.AbilCfg.G_VOW_F : (double) @PKG@.AbilCfg.G_FIRST) + (cx == null ? 0.0 : cx.pctAdd)) * cxm();
  double dp = (sh == 3 ? (double) @PKG@.AbilCfg.G_VOW_D : (double) @PKG@.AbilCfg.G_DROP) - (cx == null ? 0.0 : chainCut(cx.eff(@PKG@.AbilModDefs.CHAIN)));
  if (dp < 0.0) dp = 0.0;
  if (echo && cx != null && cx.base * cx.treeMain > 0.0) dp = dp * cx.main / (cx.base * cx.treeMain);
  int wardL = cx == null ? 0 : cx.lv(@PKG@.AbilModDefs.WARD);
  boolean xpOk = !creative(acc, ref) && (pkey == null || pkey.equals(@PKG@.ClassCfg.pkey(u)));
  String healer = pr == null ? "" : pr.getUsername();
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  double others = 0.0;
  double self = 0.0;
  int healed = 0;
  int wards = 0;
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
    if (wardL > 0 && want > got + 0.01) {
      double wd = want - got;
      double wm = mx * 3.0 * (double) wardL / 100.0;
      if (wardGive(t, wd < wm ? wd : wm, System.currentTimeMillis() + 10000L) > 0.0) wards++;
    }
    if (beacon && !echo && aw != null) {
      @PKG@.AbilJob rg = new @PKG@.AbilJob(2, System.currentTimeMillis() + 1000L, u, "MartyrsGrace", c[0], c[1], c[2], 0.0, 0.0);
      rg.targets = new java.util.UUID[] { t };
      rg.per = new double[] { mx * 0.02 };
      rg.done = new double[] { got };
      rg.cap = new double[] { @PKG@.AbilMath.capLeft(mx, @PKG@.AbilCfg.HEAL_CAP, 0.0) + mx * 0.2 };
      rg.left = 10;
      rg.every = 1000L;
      rg.name = healer;
      rg.pkey = pkey;
      aw.add(rg);
    }
    if (!(got > 0.0)) continue;
    healed++;
    if (isSelf) { self = self + got; @PKG@.HealMsg.given(u, u, got); }
    else { others = others + got; @PKG@.HealMsg.given(u, t, got); @PKG@.HealMsg.taken(t, u, healer, got); }
  }
  if (xpOk) {
    if (others > 0.0) @PKG@.HealTask.xp(u, others);
    if (self > 0.0) @PKG@.HealTask.xpSelf(u, self);
  }
  if (pr != null) say(pr, (echo ? "Echo: " : "") + @PKG@.AbilDefs.sname(@PKG@.AbilDefs.GRACE, sh) + ": " + (healed == 0 ? "nobody needed healing." : "+" + @PKG@.AbilMath.fmt(others + self) + " HP to " + healed + (healed == 1 ? " player" : " players") + ", lowest first.") + (wards > 0 ? " " + wards + " got a ward." : ""));
  if (healed > 0 && !echo) used(u, pkey, @PKG@.AbilDefs.GRACE, cx);
  if (cx != null && !echo && aw != null) echoJob(aw, cx, @PKG@.AbilDefs.GRACE, sh, c[0], c[1], c[2], 0.0, 0.0, System.currentTimeMillis() + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0));
  return " chain=" + order + " healed=" + healed + (wards > 0 ? " wards=" + wards : "");
}''')
# STARFALL: Duration+ (more stars, longer), Radius+, Sunburst (the end burst), Prism, Echo (a second shower after this one), the use
replace_method("abil", "public static @PKG@.AbilJob starJob(", r'''
public static @PKG@.AbilJob starJob(java.util.UUID u, String pkey, double[] at, double area, long stars, double secs, double amount, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double dm = cxd();
  int n = stars < 1L ? 1 : (int) Math.round((double) stars * dm);
  if (n < 1) n = 1;
  double sx = secs * dm;
  long every = Math.round(sx * 1000.0 / (double) n);
  if (every < 50L) every = 50L;
  @PKG@.AbilJob j = new @PKG@.AbilJob(5, now, u, "Starfall", at[0], at[1], at[2], area + cxr(), amount);
  j.pkey = pkey;
  j.total = n;
  j.left = n;
  j.every = every;
  j.secs = sx;
  j.width = @PKG@.AbilCfg.T_STAR_R;
  j.sh = sh;
  j.ai = @PKG@.AbilDefs.STARF;
  j.hits = 0;
  if (c != null && !c.echo && "Mage".equals(c.cls) && c.node("PB5")) j.brkAmt = c.h * 1.5 * c.main;
  return j;
}''')
replace_method("abil", "public static boolean starTick(", r'''
public static boolean starTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (!live(cb, cr, j.caster, j.pkey)) return false;
  @PKG@.AbilCtx c = j.cx;
  boolean echo = c != null && c.echo;
  boolean prism = c != null && "Mage".equals(c.cls) && c.node("PB2");
  int i = j.total - j.left;
  double cx = j.x;
  double cy = j.y;
  double cz = j.z;
  if (j.sh == 1) {
    @VEC@ p = pos(cb, cr);
    if (p != null) { cx = p.x; cy = p.y; cz = p.z; }
  }
  double[] d = @PKG@.AbilMath.disc(i, j.total, j.r);
  int pts = prism ? 2 : 1;
  double amt = prism ? j.amount * 0.85 : j.amount;
  for (int q = 0; q < pts; q++) {
    double px = cx + (q == 0 ? d[0] : -d[0]);
    double pz = cz + (q == 0 ? d[1] : -d[1]);
    particle(FX_STAR, px, cy + 0.5, pz, cb);
    java.util.List l = near(cb, px, cy, pz, j.width);
    java.util.HashSet seen = new java.util.HashSet();
    for (int k = 0; k < l.size(); k++) {
      Object o = l.get(k);
      if (!(o instanceof @REF@)) continue;
      @REF@ t = (@REF@) o;
      if (!seen.add(t)) continue;
      if (!enemy(cb, t, cr)) continue;
      if (hit(cb, t, cr, j.caster, amt, "Starfall")) { j.hits = j.hits + 1; seenAdd(c, t); }
    }
  }
  j.left = j.left - 1;
  j.at = j.at + j.every;
  if (j.left > 0) return true;
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, (echo ? "Echo: " : "") + @PKG@.AbilDefs.sname(@PKG@.AbilDefs.STARF, j.sh) + ": " + j.total + " stars, " + j.hits + (j.hits == 1 ? " hit" : " hits") + " (" + @PKG@.AbilMath.fmt(amt) + " damage each before armour).");
  if (echo || c == null) return false;
  if (j.brkAmt > 0.0) {
    int nb = burst(cb, cr, j.caster, cx, cy, cz, j.r, j.brkAmt, "Starfall");
    if (pr != null) say(pr, "Sunburst: " + nb + (nb == 1 ? " enemy" : " enemies") + " (" + @PKG@.AbilMath.fmt(j.brkAmt) + " damage each).");
    if (nb > 0) j.hits = j.hits + nb;
  }
  if (j.hits > 0) used(j.caster, j.pkey, @PKG@.AbilDefs.STARF, c);
  brilliance(c, cb, cr);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (c.echoPct > 0.0 && c.main > 0.0 && aw != null) {
    @PKG@.AbilCtx e = c.echoOf(c.echoPct);
    double dm = c.durMult > 0.0 ? c.durMult : 1.0;
    @PKG@.AbilJob ej = new @PKG@.AbilJob(10, now + Math.round(@PKG@.AbilCfg.ECHO_DELAY * 1000.0), j.caster, "Starfall", cx, cy, cz, j.r - c.radAdd, j.amount * e.main / c.main);
    ej.pkey = j.pkey;
    ej.ai = @PKG@.AbilDefs.STARF;
    ej.sh = 0;
    ej.cx = e;
    ej.total = (int) Math.round((double) j.total / dm);
    if (ej.total < 1) ej.total = 1;
    ej.secs = j.secs / dm;
    aw.add(ej);
  }
  return false;
}''')
# ARCANE BEAM: Power+ (via its rate), Duration+, Deep Beam (ramp + 1x, +0.5 s), Beam Focus (starts 0.3 s later), the use at its end
replace_method("abil", "public static @PKG@.AbilJob beamJob(", r'''
public static @PKG@.AbilJob beamJob(java.util.UUID u, String pkey, String item, double h, int sh, long now) {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  double len = @PKG@.AbilCfg.R_RANGE;
  double secs = @PKG@.AbilCfg.R_TIME;
  double width = @PKG@.AbilCfg.R_WIDTH;
  double from = 1.0;
  double to = @PKG@.AbilCfg.R_RAMP;
  if (sh == 1) { len = @PKG@.AbilCfg.R_SWEEP_R; secs = @PKG@.AbilCfg.R_SWEEP_T; width = @PKG@.AbilCfg.R_SWEEP_W; from = @PKG@.AbilCfg.R_SWEEP_M; to = @PKG@.AbilCfg.R_SWEEP_M; }
  if (sh == 2) { len = @PKG@.AbilCfg.R_DOWN_R; secs = @PKG@.AbilCfg.R_DOWN_T; }
  if (sh == 3) { len = @PKG@.AbilCfg.R_FOCUS_R; secs = @PKG@.AbilCfg.R_FOCUS_T; to = @PKG@.AbilCfg.R_FOCUS_RAMP; }
  boolean mage = c != null && "Mage".equals(c.cls);
  if (mage && c.node("PC4") && sh != 1) { to = to + 1.0; secs = secs + 0.5; }
  secs = secs * cxd();
  long delay = mage && c.node("PB3") ? 300L : 0L;
  @PKG@.AbilJob j = new @PKG@.AbilJob(6, now + delay, u, "ArcaneBeam", 0.0, 0.0, 0.0, len, h * @PKG@.AbilCfg.R_RATE * cxm());
  j.pkey = pkey;
  j.name = item;
  j.start = now + delay;
  j.secs = secs;
  j.until = j.start + Math.round(secs * 1000.0);
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
}''')
replace_method("abil", "public static boolean beamEnd(", r'''
public static boolean beamEnd(@PKG@.AbilJob j, String why) {
  if (@PKG@.AbilStore.CHAN.get(j.caster) == j) @PKG@.AbilStore.CHAN.remove(j.caster);
  @PR@ pr = prOf(j.caster);
  if (pr != null) say(pr, @PKG@.AbilDefs.sname(@PKG@.AbilDefs.BEAM, j.sh) + (why.length() > 0 ? " stopped - " + why : " ended") + ": " + j.hits + (j.hits == 1 ? " hit" : " hits") + ", " + @PKG@.AbilMath.fmt(j.paidMana) + " damage before armour.");
  if (j.hits > 0 && (j.cx == null || !j.cx.echo)) used(j.caster, j.pkey, @PKG@.AbilDefs.BEAM, j.cx);
  return false;
}''')
replace_method("abil", "public static boolean beamTick(", r'''
public static boolean beamTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (@PKG@.AbilStore.CHAN.get(j.caster) != j) return beamEnd(j, "you cast again");
  if (!live(cb, cr, j.caster, j.pkey)) return beamEnd(j, "you left");
  String it = hand(cb, cr);
  if (it == null || !it.equals(j.name)) return beamEnd(j, "you swapped your weapon");
  if (now >= j.until) return beamEnd(j, "");
  @PKG@.AbilCtx c = j.cx;
  int pierce = c == null ? 0 : c.eff(@PKG@.AbilModDefs.PIERCE);
  int slowL = c == null ? 0 : c.eff(@PKG@.AbilModDefs.SLOW);
  boolean focus = c != null && "Mage".equals(c.cls) && c.node("PB3");
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
  java.util.ArrayList ts = new java.util.ArrayList();
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
    ts.add(Double.valueOf(rd[0]));
  }
  java.util.ArrayList hitL = new java.util.ArrayList();
  if (j.sh == 1) hitL.addAll(on);
  else {
    boolean[] took = new boolean[on.size()];
    for (int n = 0; n <= pierce; n++) {
      int b = -1;
      for (int i = 0; i < on.size(); i++) if (!took[i] && (b < 0 || ((Double) ts.get(i)).doubleValue() < ((Double) ts.get(b)).doubleValue())) b = i;
      if (b < 0) break;
      took[b] = true;
      hitL.add(on.get(b));
    }
  }
  double mult = @PKG@.AbilMath.ramp((double) (now - j.start) / 1000.0, j.secs, j.from, j.to);
  double dmg = j.amount * mult * (double) j.every / 1000.0;
  double reach = j.len;
  if (j.sh != 1 && hitL.size() > 0) {
    @VEC@ q0 = pos(cb, (@REF@) hitL.get(hitL.size() - 1));
    if (q0 != null) reach = Math.sqrt((q0.x - ox) * (q0.x - ox) + (q0.y + 1.0 - oy) * (q0.y + 1.0 - oy) + (q0.z - oz) * (q0.z - oz));
  }
  for (double k = 2.0; k <= reach; k = k + 3.0) particle(FX_BEAM, ox + dx * k, oy + dy * k, oz + dz * k, cb);
  for (int i = 0; i < hitL.size(); i++) {
    @REF@ t = (@REF@) hitL.get(i);
    if (hit(cb, t, cr, j.caster, dmg, "ArcaneBeam")) {
      j.hits = j.hits + 1;
      j.paidMana = j.paidMana + dmg;
      if (slowL > 0) effect(cb, t, EF_SLOW, 1.0 + 0.5 * (double) (slowL - 1));
    }
  }
  if (focus && j.sh != 1 && hitL.size() > 0) {
    @REF@ first = (@REF@) hitL.get(0);
    @VEC@ fq = pos(cb, first);
    if (fq != null) {
      java.util.List l2 = near(cb, fq.x, fq.y, fq.z, 6.0);
      @REF@ best2 = null;
      double bd = 1.0E18;
      for (int i = 0; i < l2.size(); i++) {
        Object o = l2.get(i);
        if (!(o instanceof @REF@)) continue;
        @REF@ t = (@REF@) o;
        if (hitL.contains(t) || !enemy(cb, t, cr)) continue;
        @VEC@ q = pos(cb, t);
        if (q == null) continue;
        double dd = (q.x - fq.x) * (q.x - fq.x) + (q.y - fq.y) * (q.y - fq.y) + (q.z - fq.z) * (q.z - fq.z);
        if (dd < bd) { bd = dd; best2 = t; }
      }
      if (best2 != null && hit(cb, best2, cr, j.caster, dmg * 0.6, "ArcaneBeam")) {
        j.hits = j.hits + 1;
        j.paidMana = j.paidMana + dmg * 0.6;
        @VEC@ q2 = pos(cb, best2);
        if (q2 != null) particle(FX_BEAM, (fq.x + q2.x) / 2.0, (fq.y + q2.y) / 2.0 + 1.0, (fq.z + q2.z) / 2.0, cb);
      }
    }
  }
  j.total = j.total + 1;
  j.at = j.at + j.every;
  return true;
}''')
# ON LANDING: the mid-air shapes (the job's context is on this thread: the cast's numbers apply)
replace_method("abil", "public static String land(", r'''
public static String land(@PKG@.AbilJob j, @ST@ st, @CB@ cb, @REF@ cr, double[] at, long now) {
  int ai = j.ai;
  @PR@ pr = prOf(j.caster);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (aw == null) return "noworld";
  if (ai == @PKG@.AbilDefs.METEOR) {
    int nm = meteorSpawn(aw, j.caster, j.pkey, at[0], at[1], at[2], @PKG@.AbilCfg.M_RADIUS, @PKG@.AbilCfg.M_POWER, 0L, now, cb);
    return "meteor:" + nm;
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
    if (pr != null) say(pr, "Starfall Below: stars fall around you for " + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.T_BELOW_T * cxd()) + " s.");
    return "stars";
  }
  if (ai == @PKG@.AbilDefs.SACRED) return "heal:" + healAt(pr, st, cb, cr, j.caster, at, @PKG@.AbilCfg.S_BEACON_R + cxr(), 1.0, 1.0, now, j.pkey, 2);
  if (ai == @PKG@.AbilDefs.SANCT) { sanctAt(pr, cb, j.caster, j.pkey, aw, at, now, @PKG@.AbilCfg.Y_RADIUS, @PKG@.AbilCfg.Y_TIME, @PKG@.AbilCfg.Y_HEAL, @PKG@.AbilCfg.Y_CUT, 2); return "sanct"; }
  return "none";
}''')

# GUARDIAN SPIRIT (passive): the tree gate, Radius+ (+5 blocks a level), Efficiency, Power+ (save Health), Ward, Open Aura (TS), the use
replace_method("abil", "public static boolean guardian(", r'''
public static boolean guardian(java.util.UUID q) {
  int ci = @PKG@.ClassStore.classIndex(q);
  if (ci < 0 || ci != @PKG@.AbilDefs.CLS[@PKG@.AbilDefs.GUARD] || !@PKG@.ClassDefs.ENABLED[ci]) return false;
  String k = @PKG@.ClassCfg.pkey(q);
  if (!@PKG@.AbilDefs.owns(@PKG@.AbilDefs.GUARD, level(q, ci), @PKG@.AbilStore.granted(k), @PKG@.AbilStore.pick(k))) return false;
  return lineOn(treeCsv(q), @PKG@.AbilDefs.GUARD);
}''')
replace_method("abil", "public static String guard(", r'''
public static String guard(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  if (!@PKG@.AbilCfg.PART || d == null || r == null || d.isCancelled()) return null;
  float a0 = d.getAmount();
  if (!(a0 > 0.0f)) return null;
  @DCS@ cause = null;
  try { cause = d.getCause(); } catch (Throwable t) { cause = null; }
  if (cause != null && (cause == @DCS@.OUT_OF_WORLD || cause == @DCS@.COMMAND)) return null;
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
  if (!(h > 0.0) || !(mx > 0.0) || (double) a0 < h - 1.0E-4) return null;
  if (rec != null && now < rec[1]) { LAST_GUARD = "cooldown"; return "cooldown"; }
  @VEC@ p = pos(buf, r);
  if (p == null) return null;
  @PR@ best = null;
  @REF@ bestRef = null;
  @PKG@.AbilCtx bestCx = null;
  double bestD = 1.0E18;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ q = (@PR@) it.next();
    if (q == null || !q.isValid()) continue;
    java.util.UUID qu = q.getUuid();
    if (qu == null) continue;
    @REF@ qr = q.getReference();
    if (qr == null || !qr.isValid() || qr.getStore() != st) continue;
    @VEC@ qp = pos(buf, qr);
    if (qp == null) continue;
    double dd = (qp.x - p.x) * (qp.x - p.x) + (qp.y - p.y) * (qp.y - p.y) + (qp.z - p.z) * (qp.z - p.z);
    if (dd >= bestD) continue;
    if (!guardian(qu) || @PKG@.Kit.busy(qu)) continue;
    String qk = @PKG@.ClassCfg.pkey(qu);
    @PKG@.AbilCtx gc = ctxFor(qu, qk, @PKG@.AbilDefs.GUARD, 0, treeCsv(qu));
    double rad = @PKG@.AbilCfg.GS_RADIUS + gc.radAdd;
    if (dd > rad * rad) continue;
    boolean all = @PKG@.AbilCfg.GS_ALL || ("Priest".equals(gc.cls) && gc.node("TS"));
    if (!qu.equals(u) && !all && !@PKG@.HealTask.inParty(qu, u)) continue;
    if (!qu.equals(u) && !alive(buf, qr)) continue;
    if (!guardPaysCx(buf, qr, gc)) continue;
    best = q;
    bestRef = qr;
    bestCx = gc;
    bestD = dd;
  }
  if (best == null) { LAST_GUARD = "nopriest"; return "nopriest"; }
  boolean free = @PKG@.AbilCfg.CREATIVE_FREE && creative(buf, bestRef);
  double gm = costMana(bestCx, @PKG@.AbilDefs.GUARD, 0);
  double gs = costStam(bestCx, @PKG@.AbilDefs.GUARD, 0);
  @ESM@ pm = map(buf, bestRef);
  if (!free && pm != null) {
    if (gm > 0.0) pm.subtractStatValue(@DST@.getMana(), (float) gm);
    if (gs > 0.0) pm.subtractStatValue(@DST@.getStamina(), (float) gs);
  }
  double hpPct = (double) @PKG@.AbilCfg.GS_HP * bestCx.main;
  boolean spirit = "Priest".equals(bestCx.cls) && bestCx.node("PB4");   // fix round: Spirit Shield (Priest PB4)
  if (spirit) hpPct = hpPct * 2.0 / 3.0;
  if (hpPct > 100.0) hpPct = 100.0;
  d.setAmount(0.0f);
  d.setCancelled(true);
  m.setStatValue(hi, (float) (mx * hpPct / 100.0));
  int cnt = rec == null ? 1 : (int) rec[0] + 1;
  long cd = @PKG@.AbilMath.guardCd(Math.round(@PKG@.AbilCfg.GS_CD * 1000.0), cnt);
  @PKG@.AbilStore.GUARD.put(gk, new long[] { (long) cnt, now + cd, now });
  particle(FX_GUARD, p.x, p.y + 1.0, p.z, buf);
  SAVES = SAVES + 1L;
  int wl = bestCx.lv(@PKG@.AbilModDefs.WARD);
  if (wl > 0) wardGive(u, mx * 3.0 * (double) wl / 100.0, now + 5000L);
  if (spirit) { wardGive(u, mx * 0.15, now + 4000L); particle(FX_BUBBLE_ON, p.x, p.y + 1.0, p.z, buf); }   // the strongest ward is kept
  boolean self = best.getUuid().equals(u);
  String cost = free ? "free" : "-" + @PKG@.AbilMath.fmt(gm) + " Mana, -" + @PKG@.AbilMath.fmt(gs) + " Stamina";
  String next = " Next save for " + (self ? "you" : "them") + " in " + @PKG@.AbilMath.secs(cd) + " s.";
  say(best, "Guardian Spirit saved " + (self ? "you" : ((@PR@) po).getUsername()) + " at " + @PKG@.AbilMath.fmt(hpPct) + " % Health (" + cost + ")." + (wl > 0 ? " Ward on." : "") + (spirit ? " Spirit Shield: 4 s bubble." : "") + next);
  if (!self) say((@PR@) po, "A Guardian Spirit (" + best.getUsername() + ") saved you - " + @PKG@.AbilMath.fmt(hpPct) + " % Health.");
  used(best.getUuid(), bestCx.pkey, @PKG@.AbilDefs.GUARD, bestCx);
  LAST_GUARD = "saved:" + best.getUsername() + " count=" + cnt + " next=" + @PKG@.AbilMath.secs(cd) + " hp=" + @PKG@.AbilMath.fmt(hpPct) + (wl > 0 ? " ward" : "") + (spirit ? " spirit" : "");
  return LAST_GUARD;
}''')
# SECOND FIX ROUND (critic: resetlevels / maxlevels could not be undone): the profile's ability data (memory = the newest use counts) is
# copied to abilities/<pkey>.properties.lvl-<stamp>.bak before either writes; null = no copy (then nothing changes). Restore = rename it.
late(r'''
public static String levelsBak(String k, java.util.Properties cur) {
  try {
    java.nio.file.Path d = @PKG@.AbilStore.DIR;
    if (d == null || k == null || cur == null) return null;
    java.nio.file.Files.createDirectories(d, new java.nio.file.attribute.FileAttribute[0]);
    String nm = k + ".properties.lvl-" + System.currentTimeMillis() + ".bak";
    java.util.Properties cp = new java.util.Properties();
    cp.putAll(cur);
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(d.resolve(nm), new java.nio.file.OpenOption[0]);
    try { cp.store(out, "SkyyClasses: ability data of " + k + " before /classadmin abil maxlevels | resetlevels (rename to " + k + ".properties with the server stopped to restore)"); } finally { out.close(); }
    return nm;
  } catch (Throwable t) { @PKG@.ClassCfg.warn("could not back up ability file " + k + ": " + t); return null; }
}''')
late(r'''
public static boolean guardPaysCx(@CAC@ acc, @REF@ r, @PKG@.AbilCtx gc) {
  if (@PKG@.AbilCfg.CREATIVE_FREE && creative(acc, r)) return true;
  @ESM@ m = map(acc, r);
  double mana = cur(m, @DST@.getMana());
  double stam = cur(m, @DST@.getStamina());
  double gm = costMana(gc, @PKG@.AbilDefs.GUARD, 0);
  double gs = costStam(gc, @PKG@.AbilDefs.GUARD, 0);
  if (gm > 0.0 && !(mana >= 0.0 && @PKG@.AbilMath.enough(mana, gm))) return false;
  if (gs > 0.0 && !(stam >= 0.0 && @PKG@.AbilMath.enough(stam, gs))) return false;
  return true;
}''')
# Thorned Bubble: an attack the bubble soaked hurts its attacker (not a player's hit - those pay no absorb XP either)
rep_in("abil", "public static String shield(", '''      best.absorbed = best.absorbed + take;
''', '''      best.absorbed = best.absorbed + take;
      if (!pvp) thorns(buf, best, d);   // 0.1.22: Thorned Bubble (Priest PB1)
''')
# the state of a slot: + "locked" while the class tree has not enabled the line (abil.treeGate)
replace_method("abil", "public static String stateOf(", r'''
public static String stateOf(int ai, String k, int lv, boolean grant, String pick, long now) {
  if (ai < 0) return "empty";
  if (!@PKG@.AbilDefs.owns(ai, lv, grant, pick)) return "locked";
  if (!lineOn(treeCsv(uOfKey(k)), ai)) return "locked";
  if (@PKG@.AbilDefs.PASSIVE[ai]) return "passive";
  if (!@PKG@.AbilDefs.BUILT[ai]) return "soon";
  return @PKG@.AbilStore.left(k, @PKG@.AbilDefs.IDS[ai], now) > 0L ? "cooldown" : "ready";
}''')
replace_method("abil", "public static String[] listLines(", r'''
public static String[] listLines(java.util.UUID u) {
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) return new String[] { noClass() };
  if (!@PKG@.AbilDefs.classHas(ci)) return new String[] { @PKG@.ClassDefs.NAMES[ci] + " abilities are coming later - the Mage and the Priest get theirs first." };
  String k = @PKG@.ClassCfg.pkey(u);
  int lv = level(u, ci);
  boolean grant = @PKG@.AbilStore.granted(k);
  String pick = @PKG@.AbilStore.pick(k);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  String csv = treeCsv(u);
  long now = System.currentTimeMillis();
  java.util.Properties p = @PKG@.AbilStore.load(k);
  String[] out = new String[6];
  out[0] = "Abilities - " + @PKG@.ClassDefs.NAMES[ci] + ", " + @PKG@.ClassDefs.SKILLS[ci] + " " + lv + (grant ? " (admin grant: all four)" : "") + (@PKG@.AbilCfg.PART ? "" : " - switched OFF on this server") + ":";
  for (int i = 0; i < 4; i++) {
    int ai = @PKG@.AbilDefs.find(sl[i]);
    String st = stateOf(ai, k, lv, grant, pick, now);
    String nm = ai < 0 ? "-" : @PKG@.AbilDefs.NAMES[ai];
    String tx = st;
    if (st.equals("ready") || st.equals("cooldown")) {
      @PKG@.AbilCtx c = ctxFor(u, k, ai, i >= 2 && @PKG@.AbilCfg.SHAPES ? 3 : 0, csv);
      tx = st.equals("ready") ? "ready (" + @PKG@.AbilMath.fmt(costMana(c, ai, c.sh)) + " Mana + " + @PKG@.AbilMath.fmt(costStam(c, ai, c.sh)) + " Stamina, cooldown " + @PKG@.AbilMath.secs(cdCx(c, ai, c.sh)) + " s)"
                              : @PKG@.AbilMath.readyText(@PKG@.AbilStore.left(k, @PKG@.AbilDefs.IDS[ai], now));
      String md = (c.m0 >= 0 ? @PKG@.AbilModDefs.MNAME[c.m0] + " " + c.l0 : "") + (c.m1 >= 0 ? (c.m0 >= 0 ? ", " : "") + @PKG@.AbilModDefs.MNAME[c.m1] + " " + c.l1 : "");
      tx = tx + " - " + levelText(ai, c.lvl, numOf(p, "u." + @PKG@.AbilDefs.IDS[ai])) + (md.length() > 0 ? " - " + md : "");
    }
    if (st.equals("locked")) tx = @PKG@.AbilDefs.owns(ai, lv, grant, pick) ? "enable it in your class tree (/tree class, node A" + lineOf(ai) + ")" : "unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]);
    if (st.equals("soon")) tx = "comes in a later update";
    if (st.equals("passive")) tx = "passive - always on (a killing blow on you or your party near you leaves them at " + @PKG@.AbilCfg.GS_HP + " % Health) - " + levelText(ai, alvl(numOf(p, "u." + @PKG@.AbilDefs.IDS[ai])), numOf(p, "u." + @PKG@.AbilDefs.IDS[ai]));
    out[i + 1] = "  " + @PKG@.AbilDefs.key(i) + ": " + nm + " - " + tx;
  }
  out[5] = "  Your Ability 2 / 3 keys cast the top two (crouch = alts); /cast swap or /cast page reorders them. Levels + modifiers: /tree class.";
  return out;
}''')
replace_method("abil", "public static String adminDo(", r'''
public static String adminDo(@PR@ pr, String who, String act) {
  java.util.UUID t = @PKG@.ClassStore.resolve(who);
  if (t == null) { send(pr, "Unknown player - use an online name or a uuid.", "#ffc800"); return "who"; }
  String k = @PKG@.ClassCfg.pkey(t);
  String a = act == null ? "" : act.trim().toLowerCase();
  if (a.equals("grant") || a.equals("ungrant")) {
    boolean on = a.equals("grant");
    if (!@PKG@.AbilStore.set(k, new String[] { "grant" }, new String[] { on ? "true" : null })) { send(pr, "The ability file of " + k + " could not be read - nothing changed.", "#ffc800"); return "unread"; }
    @PKG@.AbilStore.saveSoon(k);
    mirrorSoon(t);
    send(pr, (on ? "Granted all four abilities to " : "Removed the ability grant of ") + t + " (profile " + k + ") - for testing; class levels decide again after ungrant.", "#8fe39a");
    @PR@ tp = @UNI@.get().getPlayer(t);
    if (tp != null && tp.isValid() && on) send(tp, "An admin granted you all four class abilities for testing - /cast list.", "#8fe39a");
    return on ? "grant" : "ungrant";
  }
  if (a.equals("picka") || a.equals("pickb")) {
    int ci = @PKG@.ClassStore.classIndex(t);
    if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) { send(pr, "That player has no class with abilities.", "#ffc800"); return "noclass"; }
    send(pr, setPick(k, ci, a.equals("pickb") ? "B" : "A") + " (" + t + ")", "#8fe39a");
    mirrorSoon(t);
    return a;
  }
  if (a.equals("reset")) {
    int n = @PKG@.AbilStore.clearCd(k);
    send(pr, "Cleared " + n + " ability cooldown(s) of " + t + " (profile " + k + ").", "#8fe39a");
    return "reset";
  }
  if (a.equals("maxlevels") || a.equals("resetlevels")) {
    int ci = @PKG@.ClassStore.classIndex(t);
    if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) { send(pr, "That player has no class with abilities.", "#ffc800"); return "noclass"; }
    boolean mx = a.equals("maxlevels");
    java.util.Properties cur = @PKG@.AbilStore.load(k);
    String bak = levelsBak(k, cur);   // second fix round: a copy first (the use counts are the only record of the levels)
    if (bak == null) { send(pr, "Could not back up the ability file of " + k + " - nothing changed.", "#ffc800"); return "nobak"; }
    long top = @PKG@.AbilMath.levelStart((int) @PKG@.AbilCfg.MAX_LVL, @PKG@.AbilCfg.USES_COEF, @PKG@.AbilCfg.USES_EXP);
    int[] st = @PKG@.AbilModDefs.steps();
    long mtop = st.length == 0 ? 0L : (long) st[st.length - 1];
    java.util.ArrayList ks = new java.util.ArrayList();
    java.util.ArrayList vs = new java.util.ArrayList();
    for (int ai = 0; ai < @PKG@.AbilDefs.IDS.length; ai++) {
      if (@PKG@.AbilDefs.CLS[ai] != ci) continue;
      String uk = "u." + @PKG@.AbilDefs.IDS[ai];
      if (!mx || numOf(cur, uk) < top) { ks.add(uk); vs.add(mx ? String.valueOf(top) : null); }   // maxlevels only RAISES
      for (int j = 0; j < @PKG@.AbilModDefs.count(ai); j++) {
        String mk = "m." + @PKG@.AbilDefs.IDS[ai] + "." + @PKG@.AbilModDefs.MID[@PKG@.AbilModDefs.at(ai, j)];
        if (!mx || numOf(cur, mk) < mtop) { ks.add(mk); vs.add(mx ? String.valueOf(mtop) : null); }
      }
    }
    String[] ka = new String[ks.size()];
    String[] va = new String[vs.size()];
    for (int i = 0; i < ka.length; i++) { ka[i] = (String) ks.get(i); va[i] = (String) vs.get(i); }
    if (!@PKG@.AbilStore.set(k, ka, va)) { send(pr, "The ability file of " + k + " could not be read - nothing changed.", "#ffc800"); return "unread"; }
    @PKG@.AbilStore.saveSoon(k);
    send(pr, (mx ? "Every ability of " + t + " is at its top level now (every modifier unlocked and at its top level; higher counts kept) - for testing." : "Every ability level and modifier level of " + t + " is back to Lv 1.") + " (profile " + k + ") Backup: abilities/" + bak, "#8fe39a");
    return a;
  }
  if (a.equals("info")) {
    String[] l = listLines(t);
    for (int i = 0; i < l.length; i++) send(pr, (i == 0 ? t + ": " : "") + l[i], null);
    send(pr, "Last cast on this server: " + LAST + " | last landing: " + LAST_LAND + " | Guardian Spirit saves: " + SAVES + " (last: " + LAST_GUARD + ")", null);
    send(pr, "Keys: hook " + (HOOK_ON ? "on" : "OFF (" + HOOK_WHY + ")") + ", " + HOOKS + " key presses, " + RUNES + " key casts, " + FALLBACKS + " marker casts (" + FB_DUP + " doubles skipped), " + MIRRORS + " slot fixes (last: " + LAST_MIRROR + "), " + CLEANED + " stray runes removed | uses " + USES + ", echoes " + ECHOES + " | tree read fails " + TREE_ERR + " | tree: " + treeCsv(t), null);
    return "info";
  }
  send(pr, "Usage: /classadmin abil <player|uuid> <grant|ungrant|reset|info|pickA|pickB|maxlevels|resetlevels>", "#ffc800");
  return "usage";
}''')
rep('''  super("abil", "(admin) Class abilities: /classadmin abil <player|uuid> <grant|ungrant|reset|info>");''',
    '''  super("abil", "(admin) Class abilities: /classadmin abil <player|uuid> <grant|ungrant|reset|info|pickA|pickB|maxlevels|resetlevels>");''')
rep('''  this.actArg = withRequiredArg("action", "grant | ungrant | reset | info", @ATY@.STRING);''',
    '''  this.actArg = withRequiredArg("action", "grant | ungrant | reset | info | pickA | pickB | maxlevels | resetlevels", @ATY@.STRING);''')
# AbilTick: + the rune route (the 2 s mirror look, the marker fallback) for every player
replace_method("abil", "public static void track(", r'''
public static void track(@REF@ r, @CAC@ acc, long now) {
  try {
    if (r == null || !@PKG@.AbilCfg.PART) return;
    Object po = acc.getComponent(r, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return;
    java.util.UUID u = ((@PR@) po).getUuid();
    if (u == null) return;
    try { runeTick((@PR@) po, u, r, acc, now); } catch (Throwable t1) { @PKG@.ClassCfg.warnLimited("the ability rune tick failed: " + t1); }
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
}''')
# class:fn:abil (SkyyHud): the same 48 fields; the costs include Efficiency / the tree; a line the tree has not enabled is "locked"
rep_in("abfn", "public Object apply(Object o) {", '''      double mc = ai < 0 ? 0.0 : @PKG@.AbilDefs.mana(ai, shi);
      double sc = ai < 0 ? 0.0 : @PKG@.AbilDefs.stamina(ai, shi);''', '''      @PKG@.AbilCtx hc = ai < 0 ? null : @PKG@.Abil.ctxFor(u, k, ai, shi, @PKG@.Abil.treeCsv(u));   // 0.1.22: Efficiency + the tree
      double mc = ai < 0 ? 0.0 : @PKG@.Abil.costMana(hc, ai, shi);
      double sc = ai < 0 ? 0.0 : @PKG@.Abil.costStam(hc, ai, shi);''')
# AbilShieldSys: the zones, then a WARD (0.1.22), then Guardian Spirit
rep_in("abshield", "public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {", '''    if (!@PKG@.AbilWorld.BY.isEmpty()) @PKG@.Abil.shield(st, buf, r, (@DMG@) ev, now);
''', '''    if (!@PKG@.AbilWorld.BY.isEmpty()) @PKG@.Abil.shield(st, buf, r, (@DMG@) ev, now);
    if (!@PKG@.AbilStore.WARD.isEmpty()) @PKG@.Abil.wardHit(st, buf, r, (@DMG@) ev, now);   // 0.1.22: Ward (Mana Barrier / Grace / Spirit)
''')
# AbilWorld: Arch-Mage's star well (kind 7) is a short effect like Frost Wake / Running Blessing (never counts toward abil.maxZones)
rep('''  if (z.kind == 3 || z.kind == 4) { this.zones.add(z); this.nz = this.zones.size(); return 0; }   // 0.1.18: short effects never count''',
    '''  if (z.kind == 3 || z.kind == 4 || z.kind == 7) { this.zones.add(z); this.nz = this.zones.size(); return 0; }   // 0.1.18: short effects never count (0.1.22: + 7)''')
rep('''      if (o.kind == 3 || o.kind == 4) continue;   // 0.1.18: Frost Wake / Running Blessing are not placed zones''',
    '''      if (o.kind == 3 || o.kind == 4 || o.kind == 7) continue;   // 0.1.18: Frost Wake / Running Blessing are not placed zones (0.1.22: + the star well)''')
# the slot names name the KEYS now (Hytale 0.7)
replace_method("abdefs", "public static String slotText(", r'''
public static String slotText(int slot) {
  if (slot == 0) return "Primary 1 (Ability 2 key)";
  if (slot == 1) return "Primary 2 (Ability 3 key)";
  if (slot == 2) return "Alt 1 (crouch + Ability 2)";
  return "Alt 2 (crouch + Ability 3)";
}''')
replace_method("abdefs", "public static String key(", r'''
public static String key(int slot) {
  if (slot == 0) return "Ability 2 key (/cast 1)";
  if (slot == 1) return "Ability 3 key (/cast 2)";
  if (slot == 2) return "crouch + Ability 2 (/cast 3)";
  return "crouch + Ability 3 (/cast 4)";
}''')
rep('''    String foot = "Move a card then Swap here on another to trade their places. Changes only out of combat. With Hytale 0.7 the keys become your ability keys.";''',
    '''    String foot = "Move a card then Swap here on another to trade their places (out of combat). Your Ability 2 / 3 keys cast the top two. Levels and modifiers: /tree class.";''')
# THE LOADOUT BRIDGE: the mods part is real (0.1.19 reserved it)
replace_method("abload", "public static String get(", r'''
public static String get(java.util.UUID u) {
  if (u == null) return null;
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) return null;
  GETS = GETS + 1L;
  String k = @PKG@.ClassCfg.pkey(u);
  String pk = @PKG@.AbilStore.pick(k);
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  String[] keys = new String[] { "p1", "p2", "a1", "a2" };
  StringBuilder sb = new StringBuilder();
  sb.append("v=1;class=").append(esc(@PKG@.ClassDefs.NAMES[ci])).append(";alt=").append(pk);
  for (int i = 0; i < 4; i++) sb.append(';').append(keys[i]).append('=').append(esc(sl[i]));
  for (int i = 0; i < 4; i++) sb.append(";n").append(i + 1).append('=').append(esc(name(sl[i])));
  sb.append(";mods=");
  java.util.Properties p = @PKG@.AbilStore.load(k);
  String ms = "";
  for (int ai = 0; ai < @PKG@.AbilDefs.IDS.length; ai++) {
    if (@PKG@.AbilDefs.CLS[ai] != ci) continue;
    String[] e = @PKG@.Abil.eqOf(p, @PKG@.AbilDefs.IDS[ai]);
    if (e[0].length() == 0 && e[1].length() == 0) continue;
    ms = ms + (ms.length() > 0 ? "/" : "") + @PKG@.AbilDefs.IDS[ai] + ":" + (e[0].length() == 0 ? "-" : esc(e[0])) + "+" + (e[1].length() == 0 ? "-" : esc(e[1]));
  }
  sb.append(ms);
  return sb.toString();
}''')
rep_in("abload", "public static String apply(", '''  String mods = val(snap, "mods");
  if (mods != null && mods.length() > 0) {
    if (skip.length() > 0) skip.append(", ");
    skip.append("modifiers " + mods.replace('/', ' ') + " (modifiers are not in the game yet)");
  }
''', '''  String mods = val(snap, "mods");
  String mdone = "";
  if (mods != null && mods.length() > 0) {   // 0.1.22: "Meteor:Power+Echo/ManaBarrier:Ward+-" - each one through the panel's own rules
    String csv = @PKG@.Abil.treeCsv(u);
    String[] ab = mods.split("/");
    for (int i = 0; i < ab.length; i++) {
      int c = ab[i].indexOf(':');
      if (c <= 0) continue;
      String aid = ab[i].substring(0, c).trim();
      String[] two = ab[i].substring(c + 1).split("\\\\+");
      for (int sl = 0; sl < 2; sl++) {
        String md = sl < two.length ? two[sl].trim() : "-";
        if (md.equals("-")) md = "";
        String r = @PKG@.Abil.equipMod(u, aid, sl, md, csv, true);
        if (r.startsWith("+")) mdone = aid;
        else if (!(md.length() == 0 && r.indexOf("is empty") >= 0) && r.indexOf("is already in slot") < 0) {
          if (skip.length() > 0) skip.append(", ");
          skip.append(aid + " slot " + (sl + 1) + " (" + r.substring(1) + ")");
        }
      }
    }
  }
''')
# ClassQuit (Skyy M5: cooldowns reset on relog), ClassTick (ability uses flushed every 30 s), ClassReady (a mirror look at every arrival)
rep('''    @PKG@.AbilStore.TOLD.remove(u);   // 0.1.16 (cooldowns stay: keyed by profile, a relog must not reset them)''',
    '''    @PKG@.AbilStore.TOLD.remove(u);   // 0.1.16
    @PKG@.AbilStore.clearCdOf(u);     // 0.1.22 (Skyy M5 "Always reset on relog"): every ability cooldown of this player ends
    try { String qk = @PKG@.ClassCfg.pkey(u); if (@PKG@.AbilStore.DIRTY.containsKey(qk)) @PKG@.AbilStore.saveSoon(qk); } catch (Throwable q0) { }
    @PKG@.AbilStore.MIRROR.remove(u);   // 0.1.22: the rune mirror record, the hook times, the tree cache, a ward
    @PKG@.AbilStore.LASTHOOK.remove(u);
    @PKG@.AbilStore.TREEC.remove(u);
    @PKG@.AbilStore.WARD.remove(u);
    @PKG@.AbilStore.VANTOLD.remove(u);
    @PKG@.AbilStore.CLEANQ.remove(u);
    @PKG@.AbilStore.WARDP.remove(u);   // 0.1.22 fix: nothing per player is kept after leave
    @PKG@.AbilStore.MIRFAIL.remove(u);
    @PKG@.AbilStore.dropKeysOf(@PKG@.AbilStore.LASTKEY, u);
    @PKG@.AbilStore.dropKeysOf(@PKG@.AbilStore.LASTUSE, u);
    @PKG@.AbilStore.dropKeysOf(@PKG@.AbilStore.HINTED, u);   // second fix round''')
rep('''  try { @PKG@.HealMsg.flushDue(); } catch (Throwable t2) { }
''', '''  try { @PKG@.HealMsg.flushDue(); } catch (Throwable t2) { }
  try { @PKG@.AbilStore.flushOld(System.currentTimeMillis(), 30000L); } catch (Throwable t3) { }   // 0.1.22: ability uses, every 30 s
''')
rep('''    @PKG@.Kit.owedLater(pr);   // 0.1.6: every world arrival retries owed kit items, before the once-per-session check
''', '''    @PKG@.Kit.owedLater(pr);   // 0.1.6: every world arrival retries owed kit items, before the once-per-session check
    @PKG@.Abil.mirrorSoon(u);   // 0.1.22: the ability rune slots are looked at on the next tick
''')
# the plugin: the two systems (each in its own try: a failure = logged, /cast and the marker fallback keep working), the bridges
rep('''  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilFrostSys()); }   // 0.1.18: a landed hit breaks a Frost Nova freeze (Inspect group)
  catch (Throwable t3) { @PKG@.ClassCfg.warn("could not register AbilFrostSys - Frost Nova freezes run their full time this start: " + t3); }
''', '''  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilFrostSys()); }   // 0.1.18: a landed hit breaks a Frost Nova freeze (Inspect group)
  catch (Throwable t3) { @PKG@.ClassCfg.warn("could not register AbilFrostSys - Frost Nova freezes run their full time this start: " + t3); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilRuneSys()); @PKG@.Abil.HOOK_ON = true; @PKG@.Abil.HOOK_WHY = "listening"; }   // 0.1.22: the keys
  catch (Throwable t4) { @PKG@.Abil.HOOK_WHY = "registration failed: " + t4; @PKG@.ClassCfg.warn("could not register the ability key hook (AbilRuneSys) - the keys cast through the marker fallback, /cast works: " + t4); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.AbilInvSys()); @PKG@.Abil.INV_ON = true; }   // 0.1.22: the rune guard
  catch (Throwable t5) { @PKG@.ClassCfg.warn("could not register the ability rune guard (AbilInvSys) - a dragged-out rune is only fixed by the 2 s mirror: " + t5); }
''')
rep('''  b.put("class:fn:loadoutSet", new @PKG@.LoadoutSetFn());   // 0.1.19: ... and back (validated: class, alt pick, order, modifiers)
''', '''  b.put("class:fn:loadoutSet", new @PKG@.LoadoutSetFn());   // 0.1.19: ... and back (validated: class, alt pick, order, modifiers)
  b.put("class:fn:abilPanel", new @PKG@.AbilPanelFn());     // 0.1.22: SkyyTrees 0.3.7's ability panel (levels, modifiers, slots)
  b.put("class:fn:abilMods", new @PKG@.AbilModsFn());       // 0.1.22: ... one ability's modifiers
  b.put("class:fn:abilDo", new @PKG@.AbilDoFn());           // 0.1.22: ... swap / pick / equip / unequip (out of combat)
  b.put("class:fn:abilUnlock", new @PKG@.AbilUnlockFn());   // 0.1.22: ... the A1-A4 nodes' class level gate (abil.unlock.*)
  b.put("tree:reads:SkyyClasses", "__READS__");             // 0.1.22: the class tree nodes SkyyClasses applies (reader contract)
''')
rep('''  try { @PKG@.AbilStore.flush(); } catch (Throwable t) { }   // 0.1.16 FIX ROUND: ability files changed but not yet written to disk
''', '''  try { @PKG@.AbilStore.flush(); } catch (Throwable t) { }   // 0.1.16 FIX ROUND: ability files changed but not yet written to disk
  try { @PKG@.ClassCfg.bridge().remove("tree:reads:SkyyClasses"); } catch (Throwable t) { }   // 0.1.22: the reader list it put
''')
rep('''".replace("__VER__", VERSION).replace("__KIT__", KIT_ID))
M(pl, r"""
protected void shutdown() {''', '''".replace("__VER__", VERSION).replace("__KIT__", KIT_ID).replace("__READS__", TREE_READS))
M(pl, r"""
protected void shutdown() {''')
rep('''/cast (+ /cast page), /classadmin; bridge class:fn:loadoutGet + loadoutSet (SkyyWardrobe); classes''',
    '''/cast (+ /cast page), /classadmin; abilities on the Ability 2 / 3 keys (rune hook " + @PKG@.Abil.HOOK_WHY + ", " + __NRUNES__ + " runes), levels + modifiers, the SkyyTrees ability panel bridges; bridge class:fn:loadoutGet + loadoutSet (SkyyWardrobe); classes''')
rep('''.replace("__READS__", TREE_READS))''', '''.replace("__READS__", TREE_READS).replace("__NRUNES__", str(len(RUNE_ABILS))))''')
# the classes, the asset pack, the manifest
rep('''          mrt):                          # 0.1.20: + MsgRoute''', '''          mrt,                           # 0.1.20: + MsgRoute
          abmods, abctx, abrune, abinv, abrc, abmt, abic, abpf, abmf, abdf, abuf):   # 0.1.22: + the rune route, levels, modifiers, panel''')
rep('''m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)''', '''m["IncludesAssetPack"] = True   # 0.1.22: the rune items (SkyyClasses' first asset pack - RUNE_FILES, checked above)
B.assemble(jar, m, OUT, RUNE_FILES)''')
rep('''class abilities with /cast (Mage Meteor''', '''class abilities on the Ability 2 / 3 keys (Hytale 0.7 runes) and /cast, levelling by use with modifiers (Mage Meteor''')


# ================================================================================================ the late methods go in (every late() is done)
for _j in LATE_JAVA:
    assert '"""' not in _j and _j.lstrip().startswith("public static "), _j[:80]
_LATE_NAMES = [_j.split("(")[0].split()[-1] for _j in LATE_JAVA]
assert len(set(_LATE_NAMES)) == len(_LATE_NAMES), "a late method name twice: %s" % sorted(n for n in _LATE_NAMES if _LATE_NAMES.count(n) > 1)
_OLD_ABIL = set(re.findall(r'M\(abil, r"""\npublic static [^\n(]*?([A-Za-z0-9_]+)\(', s))
assert not (set(_LATE_NAMES) & _OLD_ABIL), "a late method shadows an old Abil method: %s" % sorted(set(_LATE_NAMES) & _OLD_ABIL)
rep('''           "public static volatile String LAST = \\"\\";"):                        # the last cast outcome (harness + /classadmin abil info)
    F(abil, _f)
''', '''           "public static volatile String LAST = \\"\\";"):                        # the last cast outcome (harness + /classadmin abil info)
    F(abil, _f)
# 0.1.22: the rune route + levels + modifiers - counters (the harness + /classadmin abil info), harness seams, the knockback config
for _f in ("public static volatile long HOOKS = 0L;", "public static volatile long HOOK_SEEN = 0L;", "public static volatile long RUNES = 0L;",
           "public static volatile long FALLBACKS = 0L;", "public static volatile long FB_DUP = 0L;", "public static volatile long MIRRORS = 0L;",
           "public static volatile long CLEANED = 0L;", "public static volatile long USES = 0L;", "public static volatile long ECHOES = 0L;",
           "public static volatile long FILLS = 0L;", "public static volatile long DOS = 0L;", "public static volatile boolean FILL_WARNED = false;",
           "public static volatile boolean HOOK_ON = false;", "public static volatile String HOOK_WHY = \\"not registered\\";",
           "public static volatile boolean INV_ON = false;", "public static volatile long TREE_ERR = 0L;", "public static volatile long VANBLOCK = 0L;",   # second fix round: failed tree reads
           "public static volatile String LAST_RUNE = \\"\\";", "public static volatile String LAST_MIRROR = \\"\\";",
           "public static volatile String LAST_ECHO = \\"\\";",
           "public static volatile java.util.function.Function ITEMS = null;",   # HARNESS SEAM ONLY (null = Item.getAssetMap): rune id -> Boolean
           "public static volatile java.util.function.Function MARKS = null;",   # HARNESS SEAM ONLY (null = EntityEffect.getAssetMap): id -> Integer
           "public static volatile java.util.List PUSHES = null;",               # HARNESS SEAM ONLY (null): every push / pull (vx, vy, vz)
           "public static @VCF@ DASH = null;",
           "public static final float DASH_AIR = %rf;" % float(_DASH["AirResistance"]),
           "public static final float DASH_AIRMAX = %rf;" % float(_DASH["AirResistanceMax"]),
           "public static final float DASH_GROUND = %rf;" % float(_DASH["GroundResistance"]),
           "public static final float DASH_GROUNDMAX = %rf;" % float(_DASH["GroundResistanceMax"]),
           "public static final float DASH_THRES = %rf;" % float(_DASH["Threshold"]),
           "public static final String[] CLEANSE = %s;" % jarr(CLEANSE)):
    F(abil, _f)
# 0.1.22: every new Abil method as a STUB now (default return); its real body is set at the end of the class build (ABIL_LATE)
ABIL_LATE = [
''' + ",\n".join('r"""\n%s\n"""' % _j for _j in LATE_JAVA) + '''
]


def _late_stub(src):
    sig = src.strip().split("{", 1)[0].strip()
    ret = sig.split("(")[0].split()[-2]
    dv = {"void": "", "boolean": "return false;", "int": "return 0;", "long": "return 0L;", "double": "return 0.0;", "float": "return 0.0f;"}
    return sig + " { " + dv.get(ret, "return null;") + " }"


for _src in ABIL_LATE:
    M(abil, _late_stub(_src))
''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "no new command"
assert s.count("registerSystem(") == SYS0 + 2, "exactly the two new systems (AbilRuneSys, AbilInvSys)"
assert s.index('abctx = pool.makeClass(PKG + ".AbilCtx")') < s.index('abjob = pool.makeClass(PKG + ".AbilJob")') < s.index('abil = pool.makeClass(PKG + ".Abil")')
assert s.index("ABIL_LATE = [") < s.index('M(abil, r"""\npublic static void send(') < s.index("# THE LATE BODIES") < s.index("# ================= plugin =================")
assert 'super("abilities"' not in s and 'addAliases(new String[] { "abilities"' not in s, "never a command named /abilities (vanilla 0.7 owns it)"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.1.21 had %d; %d anchored changes, %d late methods)" % (s.count(LF), OLD.count(LF), len(CHANGES), len(LATE_JAVA)))
