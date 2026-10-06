"""Derive SkyyArmory/build_skyyarmory_0.1.2.py (+ its harness SkyyArmory/test_skyyarmory_0.1.2.py) from the GENERATED 0.1.1
(SkyyArmory/build_skyyarmory_0.1.1.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_1_patch.py; test_skyyarmory_0.1.1.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_2_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.2.py   then   python SkyyArmory/test_skyyarmory_0.1.2.py
      (never --deploy; SkyyArmory 0.1.2 needs 0.1.1's deploy partners - SkyyClasses 0.1.12+ - and nothing new)

0.1.2 = THE CROSSBOW GRAPPLE BOLT (research/Grapple-Bolt-Spec.md, Grapple Bolt part; Skyy's answers docs/answered/classes.md 2026-10-06 BEAT the
spec defaults) + the traversal Stamina cap 10 -> 5:
  RIGHT CLICK ON A CROSSBOW = GRAPPLE ONLY (Skyy: "Replace guard"): the vanilla root Root_Weapon_Crossbow_Secondary_Guard is overridden
    (RequireNewClick, Cooldown 0.25, the vanilla Rules) -> SkyyArmory_Grapple = EffectCondition [SkyyArmory_Grapple_Out] Match All:
      Next   = ApplyEffect SkyyArmory_Grapple_Click   (a click while a bolt is out / while pulled - the server consumes it)
      Failed = Projectile Config SkyyArmory_Grapple_Bolt (the game's own client-predicted shot, ItemAnimationId Shoot)
    The bolt (ProjectileConfig, fully resolved Projectile_Config_Arrow_Base + LaunchForce 60 / Gravity 6 / TerminalVelocityAir 70;
    model = Arrow_Crude with the rope-brown trail SkyyArmory_Rope_Trail) does no damage (no DamageEntity anywhere), breaks no block
    (no Block_Break_Projectile), and its miss chain has no despawn: it RESTS in the block it hits (StandardPhysicsProvider STATE.RESTING).
    SkyyArmory never touches Ammo, arrows, SwapFrom or the hotbar - loaded bolts and the reload loop stay vanilla / SkyySkills'.
  JAVA: GrappleBoltSys (RefSystem on Projectile + StandardPhysicsProvider, SPAWN, our model id) -> Grapple.onShot: class lock
    (class:fn:allowed on the crossbow in hand - crossbows = Archer), part.grapple, cooldown, newest bolt wins; the bolt's ImpactConsumer is
    WRAPPED (GrappleImpact records the hit - block or entity - then calls the engine's own consumer, so ProjectileHit / ProjectileMiss run
    as before); the player gets the OUT effect. TravTick (per player, world thread) -> Grapple.tickPlayer: consumes the CLICK effect,
    snaps / times out / swap / death / mount / world checks, the per-tick pull, arrival, stall, release, rope dots.
      click, bolt STUCK in a block  -> FULL PULL: Velocity Set toward the bolt every tick (grapple.pullSpeed, downward part at most
                                       grapple.maxDown), ends grapple.stopDistance short (from the chest); bolt above the feet = a hop
                                       (grapple.arriveHop), else a soft stop; grapple.landGrace s without FALL damage (GrappleFallSys)
      click, bolt still FLYING      -> HALF PULL to grapple.halfPercent % of the way to the bolt, the bolt is gone at once
      click while pulled            -> LET GO: last pull velocity x grapple.releaseKeep % + grapple.releaseLift up, normal fall rules
      bolt hits a MOB (Skyy: "Hooks the mob", Harpoon-style) -> click: a SMALL mob (hitbox w x h x d <= grapple.yankSize, default 1 =
        player-sized and smaller) is YANKED to you (its Velocity Set every tick, the dagger dash config); a BIG mob or a BOSS (role name holds
        a grapple.bossWords word) pulls YOU to it; a hooked PLAYER is yanked only with grapple.yankPlayers on (default off) AND world PvP on
        AND not your party - else they pull you.
    Costs (server, at the pull): full 3 Stamina + 1.5 Mana, half 2 + 1 (Mana only where the player has Mana), Stamina regen pause 0.7 s;
    too little = no pull, the "no" sound + a chat line, the bolt stays. Every number is a Server Setup row (Armory > Crossbow grapple).
  TRAVERSAL STAMINA CAP (Skyy 2026-10-06 LOCKED: "Lower cap e.g. 5"): trav.staminaCap default 10 -> 5 (two traversals per bar). ONE-TIME
    UPDATE of an existing config.properties (ArmoryCfg.migrate012, setup() before the loader; the SkyyAccessories migrate055 pattern): a
    one-line trav.staminaCap entry still holding the old default 10 becomes 5; any other value is KEPT and logged; History copy verified
    first; one Undo-able config-changes.log line; a marker comment so it runs once; every other byte and the line endings kept. A file
    without the line (Skyy's live file today) only gets the marker (the new default 5 applies; a later in-game 10 is never turned back).
  Bridge: armory:grapple (the live grapple numbers, String). Pack check: + the crossbow root comes from our pack.
  FIX ROUND (grapple-fix 2026-10-06, critic findings): an Invulnerable mob (Kweebec_Merchant) or a role holding a grapple.noYankWords word
    (traders, pets, mounts, hub NPCs) is never yanked - it pulls you; grapple.bossWords + Chieftain, Elite, Hedera, Rex; a yank has the
    pull's stall rule (a mob behind a fence) and ends with a quarter of its last speed; pulls and yanks EASE near the end (grapple.ease:
    speed at most 4 x the blocks left, at least 4 b/s - less overshoot with ping); the bolt only from an item whose id names a crossbow
    (H1Z blunderbusses share the root); the vanilla root's Tags kept; a stuck bolt taken by another mod (More Arrows' magnet) keeps its
    anchor (the pull still works); a sweep every 300 player ticks drops records of players who are gone (disconnect) and prunes
    GRACE / LASTEND; the OUT / CLICK effect indexes cached; at most 64 rope dots per 100 ms for the whole server.
"""
import os
import re
import pprint

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.1.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.2.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.1.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.2.py")

raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.1"\nMOD = "SkyyArmory"' in s and "FIX ROUND (trav-fix 2026-10-06, critic findings)" in s, "build_skyyarmory_0.1.1.py is not the 0.1.1 pin"
SYS0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ================================================================================================ the grapple rows (spec 1.3 + Skyy's answers)
# (key, label, cat, type, default, min, max, opts, unit, flags, help, ArmoryCfg field, Java type, Java default, config.properties comment)
G_ROWS = [
    ("part.grapple", "Crossbow grapple bolt", "grapple", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = right click on a crossbow does nothing (a bolt is removed at once). The guard needs a rebuild.", "PART_GRAPPLE", "boolean", "true",
     "Crossbow right click = the grapple bolt. Off = right click does nothing (the vanilla guard comes back only with a rebuild)."),
    ("grapple.ropeLength", "Rope length (blocks)", "grapple", "int", "32", "8", "64", "", "blocks", "live",
     "A flying bolt farther than this from you snaps.", "G_ROPE_LEN", "int", "32",
     "A flying grapple bolt farther than this many blocks from you snaps (the grapple is over)."),
    ("grapple.snapDistance", "Rope snaps past (blocks)", "grapple", "int", "40", "8", "96", "", "blocks", "live",
     "For a stuck bolt or a hooked mob.", "G_SNAP", "int", "40",
     "A stuck bolt / a hooked mob farther than this many blocks from you: the rope snaps."),
    ("grapple.anchorSeconds", "Stuck bolt lasts (s)", "grapple", "int", "30", "3", "300", "", "s", "live",
     "Then it drops. A hooked mob is let go after the same time.", "G_ANCHOR", "int", "30",
     "A stuck bolt drops after this many seconds (a hooked mob is let go after the same time)."),
    ("grapple.pullSpeed", "Pull speed (blocks per second)", "grapple", "dec", "24", "8", "40", "", "", "live",
     "Small mobs are yanked at the same speed.", "G_SPEED", "double", "24",
     "Pull speed in blocks per second (also the yank speed of a small hooked mob)."),
    ("grapple.maxDown", "Fastest downward pull (b/s)", "grapple", "dec", "18", "5", "40", "", "", "live",
     "Keeps pull landings under the fall-damage speed (21).", "G_MAXDOWN", "double", "18",
     "The downward part of a pull is at most this (b/s) - landings stay under the fall-damage speed 21."),
    ("grapple.ease", "Slow down near the end (b/s per block)", "grapple", "dec", "4", "0", "20", "", "", "live",
     "Speed = at most this x blocks left (at least 4): less overshoot with ping. 0 = full speed.", "G_EASE", "double", "4",
     "Near the end a pull / yank slows to this x the blocks left (at least 4 b/s) - less overshoot on a laggy link (0 = full speed to the end)."),
    ("grapple.stopDistance", "Stop short of the bolt (blocks)", "grapple", "dec", "1.2", "0.5", "4", "", "blocks", "live",
     "Measured from your chest.", "G_STOP", "double", "1.2",
     "A pull ends this many blocks short of the bolt (measured from your chest)."),
    ("grapple.halfPercent", "Pull before it sticks (% of the way)", "grapple", "int", "50", "10", "100", "step=5", "%", "live",
     "Skyy: half way. The flying bolt is gone after.", "G_HALF_PCT", "int", "50",
     "A pull while the bolt still flies takes you this % of the way to it (Skyy: half way); the bolt is gone after."),
    ("grapple.pullMaxSeconds", "Longest pull (s)", "grapple", "dec", "2.5", "0.5", "6", "", "s", "live",
     "Then you let go automatically.", "G_PULL_MAX", "double", "2.5",
     "The longest pull in seconds - then you let go automatically."),
    ("grapple.releaseKeep", "Speed kept when you let go (%)", "grapple", "int", "100", "0", "150", "step=5", "%", "live",
     "Right click while pulled = let go and keep flying.", "G_KEEP", "int", "100",
     "Right click while pulled = let go: you keep this % of the pull speed."),
    ("grapple.releaseLift", "Lift when you let go (b/s)", "grapple", "dec", "2", "0", "10", "", "", "live",
     "The swing feel.", "G_LIFT", "double", "2",
     "Extra upward speed when you let go (the swing feel)."),
    ("grapple.arriveHop", "Hop on arrival (b/s up)", "grapple", "dec", "6", "0", "12", "", "", "live",
     "Only when the bolt is above your feet (ledges).", "G_HOP", "double", "6",
     "Arriving below a bolt above your feet = a small hop up of this speed (onto ledges)."),
    ("grapple.landGrace", "No fall damage after arriving (s)", "grapple", "dec", "0.5", "0", "3", "", "s", "live",
     "Not after you let go or the rope snaps.", "G_GRACE", "double", "0.5",
     "No fall damage while pulled and this many seconds after an arrival (never after letting go or a snap)."),
    ("grapple.stamina", "Pull Stamina", "grapple", "dec", "3", "0", "10", "", "", "live",
     "Physical traversal: more Stamina than Mana.", "G_STAM", "double", "3",
     "A full pull (bolt stuck / mob hooked) costs this much Stamina..."),
    ("grapple.mana", "Pull Mana", "grapple", "dec", "1.5", "0", "50", "", "", "live",
     "Too little Stamina or Mana = no pull, the bolt stays.", "G_MANA", "double", "1.5",
     "... and this much Mana. Too little of either = no pull, the bolt stays."),
    ("grapple.halfStamina", "Half pull Stamina", "grapple", "dec", "2", "0", "10", "", "", "live",
     "A pull while the bolt still flies.", "G_HSTAM", "double", "2",
     "A half pull (the bolt still flies) costs this much Stamina..."),
    ("grapple.halfMana", "Half pull Mana", "grapple", "dec", "1", "0", "50", "", "", "live",
     "A pull while the bolt still flies.", "G_HMANA", "double", "1",
     "... and this much Mana."),
    ("grapple.regenPause", "Stamina regen pause after a pull (s)", "grapple", "dec", "0.7", "0", "3", "", "s", "live",
     "The vanilla dodge uses 0.7.", "G_REGEN", "double", "0.7",
     "Stamina stops regenerating this long after a pull (the vanilla dodge uses 0.7)."),
    ("grapple.rope", "Rope line", "grapple", "choice", "pull", "", "", "off|Off,pull|While pulled,always|Always", "", "live",
     "always = also while the bolt waits (more particles).", "G_ROPE", "String", "pull",
     "The rope dots: off, pull (while you are pulled) or always (also while the bolt waits)."),
    ("grapple.ropeSpacing", "Rope dot spacing (blocks)", "grapple", "dec", "1.5", "0.5", "4", "", "blocks", "live",
     "Fewer dots = fewer particles.", "G_SPACING", "double", "1.5",
     "One rope dot every this many blocks."),
    ("grapple.cooldown", "Grapple cooldown after it ends (s)", "grapple", "dec", "0", "0", "10", "", "s", "live",
     "0 = none; Stamina is the limit.", "G_CD", "double", "0",
     "No new grapple bolt this many seconds after one ends (0 = none)."),
    ("grapple.yankSize", "Yank mobs up to this size", "grapple", "dec", "1", "0", "20", "", "", "live",
     "Hitbox width x height x depth (player 0.8, skeleton 0.65, cow 4.4). Bigger mobs pull you. 0 = never.", "G_YANK_SIZE", "double", "1",
     "A hooked mob whose hitbox (width x height x depth) is at most this is yanked to you; bigger mobs pull you to them (0 = never yank)."),
    ("grapple.bossWords", "Bosses (role name words)", "grapple", "text", "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex", "", "200", "", "",
     "live", "A mob whose role name holds one of these comma-separated words is never yanked: it pulls you.", "G_BOSS", "String",
     "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex",
     "A mob whose role name holds one of these comma-separated words is a boss: never yanked, it pulls you to it."),
    ("grapple.noYankWords", "Never yanked (role name words)", "grapple", "text", "Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub",
     "", "200", "", "", "live", "Traders, pets, mounts, hub NPCs: they pull you instead. Invulnerable mobs are never yanked either.",
     "G_NOYANK", "String", "Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub",
     "A mob whose role name holds one of these words (traders, pets, mounts, hub NPCs) or that is Invulnerable is never yanked: it pulls you."),
    ("grapple.yankPlayers", "Yank hooked players", "grapple", "bool", "false", "", "", "", "", "live",
     "On = only where PvP is on and they are not in your party. Off = a hooked player pulls you.", "G_YANK_PLAYERS", "boolean", "false",
     "On = a hooked player is yanked where the world's PvP is on and they are not in your party. Off = a hooked player pulls you."),
]
for _r in G_ROWS:
    assert len(_r) == 15 and len(_r[1]) <= 40 and len(_r[10]) <= 100 and all(32 <= ord(c) < 127 for c in "".join(_r)), _r
G_DEF = dict((r[0], r[4]) for r in G_ROWS)
assert G_DEF["grapple.pullSpeed"] == "24" and G_DEF["grapple.stamina"] == "3" and G_DEF["grapple.halfPercent"] == "50"

# the one-time update marker (no '=' - a comment line; the AccCfg.migrate055 rules)
M12_MARK_ID = "SkyyArmory 0.1.2 traversal Stamina cap"
M12_MARK = ("# %s (Skyy 2026-10-06): at most 5 Stamina per traversal (0.1.1: 10) - two traversals per bar; a line still on the old 10 "
            "was updated once" % M12_MARK_ID)
assert "=" not in M12_MARK and all(32 <= ord(c) < 127 for c in M12_MARK)

# ================================================================================================ header + version
rep('''"""SkyyArmory 0.1.1 - build script (javassist via jpype). GENERATED by tools/armory_0_1_1_patch.py from the LIVE 0.1 - edit the patch,
never this file. Run: python SkyyArmory/build_skyyarmory_0.1.1.py -> SkyyArmory/SkyyArmory-0.1.1.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.1.py (scratch tools/dev/scratch/armory011/).
''', '"""SkyyArmory 0.1.2 - build script (javassist via jpype). GENERATED by tools/armory_0_1_2_patch.py from the GENERATED 0.1.1 - edit the\n'
    'patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.2.py -> SkyyArmory/SkyyArmory-0.1.2.jar (never --deploy). Harness:\n'
    'python SkyyArmory/test_skyyarmory_0.1.2.py (scratch tools/dev/scratch/armory012/).\n\n'
    + open(__file__, encoding="utf8").read().split('"""')[1].split("\n", 3)[3].strip() + "\n\n"
    '0.1.1 (the base, everything below is still true unless 0.1.2 above says otherwise):\n')
rep('VERSION = "0.1.1"\nMOD = "SkyyArmory"', 'VERSION = "0.1.2"\nMOD = "SkyyArmory"')

# ================================================================================================ 0.1.2 constants (spec 3.1.1)
rep("# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)", '''# ================================================================= 0.1.2 CROSSBOW GRAPPLE BOLT (research/Grapple-Bolt-Spec.md 3.1)
XBOW_RIGHT = "grapple"           # LOCKED 2026-10-06 (Skyy: "Replace guard"): crossbow right click = the grapple only | "guard" = verification
                                 # builds: no root override (the vanilla guard), the grapple Java idles
CLICK_MODE = "effect"            # clicks 2 / 3 = the CLICK effect the chain applies and the server consumes (the only mode built)
PULL_EVERY = 1                   # the pull's Velocity Set every tick (1) | every other tick (2: half the packets, slow links)
ROPE_MODE = "dots"               # the rope while pulled: particle dots (the only mode built; "stretch" = game probe P1)
BOLT_FORCE, BOLT_GRAVITY = 60, 6 # the bolt flight (client-predicted ProjectileConfig): crossbow bolts are 40 / 10
ROPE_COLOR = "#8a6a45"           # rope brown: the flight trail + the rope dots
ROPE_BUDGET = 64                 # FIX ROUND: at most this many rope dots per 100 ms window, all players together (one ParticleUtil call each)
assert XBOW_RIGHT in ("grapple", "guard") and CLICK_MODE == "effect" and PULL_EVERY in (1, 2) and ROPE_MODE == "dots"
XROOT = "Root_Weapon_Crossbow_Secondary_Guard"           # the vanilla crossbow right click root (the template names it; we override it)
ID_GRAPPLE, ID_GCLICK, ID_GSHOOT = "SkyyArmory_Grapple", "SkyyArmory_Grapple_Click_Step", "SkyyArmory_Grapple_Shoot"
ID_GHIT, ID_GSTICK, ID_GGONE = "SkyyArmory_Grapple_Hit", "SkyyArmory_Grapple_Stick", "SkyyArmory_Grapple_Despawn"
FX_GOUT, FX_GCLICK = "SkyyArmory_Grapple_Out", "SkyyArmory_Grapple_Click"
GBOLT = "SkyyArmory_Grapple_Bolt"                        # the ProjectileConfig id AND its model asset id (the Java knows the bolt by it)
GTRAIL = "SkyyArmory_Rope_Trail"
GDOT = "SkyyArmory_Rope_Dot"
SND_GMISS, SND_GHIT, SND_GNO = "SFX_Arrow_FullCharge_Miss", "SFX_Arrow_FullCharge_Hit", "SFX_Bow_No_Ammo"
SND_GLAUNCH, SND_GLAUNCH_L = "SFX_Bow_T2_Shoot", "SFX_Bow_T2_Shoot_Local"
CFG_GRAPPLE = ''' + "[\n" + "".join("    %r,\n" % (r,) for r in G_ROWS) + ''']
M12_MARK_ID = %r
M12_MARK = %r

# the 0.1.1 settings rows (generated by tools/armory_0_1_1_patch.py from TRAV)''' % (M12_MARK_ID, M12_MARK))
rep("othersPct=50, players=True, maxLive=64, fx=True, stamPct=50, stamCap=10, pierce=0, rangeW=16, rangeS=24, staffBonus=15)",
    "othersPct=50, players=True, maxLive=64, fx=True, stamPct=50, stamCap=5, pierce=0, rangeW=16, rangeS=24, staffBonus=15)   # 0.1.2: stamCap 5")
rep(''' ('trav.staminaCap',
  'Most Stamina per traversal',
  'trav',
  'int',
  '10',
  '0',
  '100',
  '',
  '',
  'live',
  '0 = no cap. Vanilla max Stamina is 10, so a higher cost could never be paid.',
  'STAMINA_CAP',
  'int',
  '10',
  'At most this much Stamina per traversal (0 = no cap; vanilla max Stamina is 10).'),''', ''' ('trav.staminaCap',
  'Most Stamina per traversal',
  'trav',
  'int',
  '5',
  '0',
  '100',
  '',
  '',
  'live',
  'Skyy 2026-10-06: 5 = two traversals per 10-Stamina bar (0.1.1: 10). 0 = no cap.',
  'STAMINA_CAP',
  'int',
  '5',
  'At most this much Stamina per traversal (0 = no cap). Skyy 2026-10-06: 5 = two traversals per 10-Stamina bar.'),''')
rep("""  'Staff quick shots hit this % harder (per Mana) than wand quick shots.')]
""", """  'Staff quick shots hit this % harder (per Mana) than wand quick shots.')] + CFG_GRAPPLE      # 0.1.2: the grapple rows (same machinery)
""")
rep('SWITCHES = ("HOP_MODE", "WAND_STYLE",', 'SWITCHES = ("XBOW_RIGHT", "PULL_EVERY", "HOP_MODE", "WAND_STYLE",')
rep('''assert WAND_STYLE in SA.WAND_STYLES and QUICK_LOOK in ("recolor", "ice") and QUICK_SIZE_MODE in ("scale", "model")''',
    '''assert WAND_STYLE in SA.WAND_STYLES and QUICK_LOOK in ("recolor", "ice") and QUICK_SIZE_MODE in ("scale", "model")
assert XBOW_RIGHT in ("grapple", "guard") and PULL_EVERY in (1, 2), (XBOW_RIGHT, PULL_EVERY)''')

# ================================================================================================ Assets.zip index: + projectile configs, effects
rep('''("Server/Item/ItemSoundSets/", "iss"), ("Server/Item/Category/", "cat")):''',
    '''("Server/Item/ItemSoundSets/", "iss"), ("Server/Item/Category/", "cat"),
                        ("Server/ProjectileConfigs/", "pcfg"), ("Server/Entity/Effects/", "efx")):''')

# ================================================================================================ the grapple assets (spec 2.1 / 2.2 / 2.4 / 3.1.2)
G_ASSETS = r'''
# ================================================================= 0.1.2 GRAPPLE BOLT ASSETS (spec 2.1, 2.2, 2.4, 3.1.2) - the vanilla shapes first
P_XROOT = "Server/Item/RootInteractions/Weapons/Crossbow/%s.json"          # the vanilla path (an override by id, like Wand_Primary)
P_XINT = "Server/Item/Interactions/Weapons/Crossbow/SkyyArmory/%s.json"
P_PCFG = "Server/ProjectileConfigs/SkyyArmory/%s.json"
P_EFX = "Server/Entity/Effects/SkyyArmory/%s.json"
_xt = az_get("item", "Template_Weapon_Crossbow")
assert _xt["Interactions"] == {"SwapFrom": "Root_Weapon_Crossbow_Swap_From", "Primary": "Root_Weapon_Crossbow_Primary_Signature",
                               "Secondary": XROOT, "Ability1": "Root_Weapon_Crossbow_Signature_BigArrow",
                               "Ability3": "Root_Common_StatAmmoReload_Entry"}, _xt["Interactions"]
assert _xt["PlayerAnimationsId"] == "Crossbow" and "Ammo" in _xt["Weapon"]["EntityStatsToClear"], "the crossbow template changed"
VXROOT = az_get("root", XROOT)
assert VXROOT == {"RequireNewClick": True, "Rules": {"Interrupting": ["Primary"]}, "Interactions": [
    {"Type": "Replace", "Var": "Guard_Start", "DefaultOk": True, "DefaultValue": {"Interactions": ["Weapon_Crossbow_Secondary_Guard"]}}],
    "Tags": {"Attack": ["Melee"]}}, VXROOT
_xroot_users = sorted(n for n in AZ_NAMES if n.startswith("Server/") and n.endswith(".json") and ('"%s"' % XROOT).encode() in AZ.read(n))
assert _xroot_users == ["Server/Item/Items/Weapon/Crossbow/Template_Weapon_Crossbow.json"], _xroot_users
for _x in ("Weapon_Crossbow_Iron", "Weapon_Crossbow_Ancient_Steel"):
    _xi = az_get("item", _x)
    assert _xi.get("Parent") == "Template_Weapon_Crossbow" and "Secondary" not in (_xi.get("Interactions") or {}), (_x, _xi.get("Interactions"))
_reload = az_get("root", "Root_Common_StatAmmoReload_Entry")
assert "Secondary" in json.dumps(_reload) or "Secondary" in json.dumps(_xt["InteractionVars"]["Reload_Start"]), "the reload is no longer stopped by a right click"
for _k, _i in (("pcfg", "Projectile_Config_Arrow_Base"), ("pcfg", "Projectile_Config_Arrow_Crossbow"), ("efx", "Stamina_Broken"), ("efx", "Dodge_Left")):
    assert len(_IDX[_k][_i]) == 1, "Assets.zip has %s %s more than once: %s" % (_k, _i, _IDX[_k][_i])      # the ids this build reads are unique
_pb = az_json(az_path("pcfg", "Projectile_Config_Arrow_Base"))
assert _pb == {"Model": "Arrow_Crude", "SpawnRotationOffset": {"Pitch": 2, "Yaw": 0.25, "Roll": 0},
               "Physics": {"Type": "Standard", "Gravity": 15, "TerminalVelocityAir": 50, "TerminalVelocityWater": 15, "RotationMode": "VelocityDamped",
                           "Bounciness": 0.0, "SticksVertically": True}, "LaunchForce": 30, "SpawnOffset": {"X": 0.15, "Y": -0.25, "Z": 0}}, _pb
_pxb = az_json(az_path("pcfg", "Projectile_Config_Arrow_Crossbow"))
assert _pxb["LaunchForce"] == 40 and _pxb["Physics"]["Gravity"] == 10 and _pxb["LaunchWorldSoundEventId"] == SND_GLAUNCH \
    and _pxb["LaunchLocalSoundEventId"] == SND_GLAUNCH_L and "Block_Break_Projectile" in _pxb["Interactions"]["ProjectileMiss"]["Interactions"], _pxb
assert az_get("int", "Common_Projectile_Despawn") == {"Type": "RemoveEntity", "Entity": "User"}
_vam = az_get("model", "Arrow_Crude")
assert [t["TrailId"] for t in _vam["Trails"]] == ["Arrow", "Arrow"] and _vam["HitBox"]["Max"]["X"] == 0.075, _vam
_vtr = az_get("trail", "Arrow")
assert _vtr["Start"]["Color"] == "#ffffff40" and _vtr["LifeSpan"] == 20 and _vtr["RenderMode"] == "BlendAdd", _vtr
assert "Shoot" in resolve("anim", "Crossbow")["Animations"], "the crossbow has no Shoot animation"
for _s in (SND_GMISS, SND_GHIT, SND_GNO, SND_GLAUNCH, SND_GLAUNCH_L):
    assert az_has("sound", _s), "no sound event %s" % _s
assert az_get("efx", "Stamina_Broken").get("Infinite") is True and az_get("efx", "Dodge_Left").get("OverlapBehavior") == "Extend"
_ec = az_get("int", "Weapon_Crossbow_Secondary_Guard")["Next"]
assert _ec["Type"] == "EffectCondition" and _ec["EntityEffectIds"] == ["Stamina_Broken"] and _ec["Match"] == "None", _ec
for _i in (ID_GRAPPLE, ID_GCLICK, ID_GSHOOT, ID_GHIT, ID_GSTICK, ID_GGONE):
    assert not az_has("int", _i) and not az_has("root", _i), _i
for _i in (GBOLT, FX_GOUT, FX_GCLICK, GTRAIL, GDOT):
    assert not az_has("pcfg", _i) and not az_has("efx", _i) and not az_has("model", _i) and not az_has("trail", _i) and _i not in _IDX["psys"], _i
GINTS = []                                     # the grapple interaction ids (the harness + the pack check read them)


def add_gint(iid, obj):
    add_int(P_XINT, iid, obj)
    GINTS.append(iid)


add_gint(ID_GCLICK, {"Type": "ApplyEffect", "EffectId": FX_GCLICK})
add_gint(ID_GSHOOT, {"Type": "Projectile", "RunTime": 0.2, "Effects": {"ItemAnimationId": "Shoot", "ClearAnimationOnFinish": True}, "Config": GBOLT})
add_gint(ID_GRAPPLE, {"Type": "EffectCondition", "EntityEffectIds": [FX_GOUT], "Match": "All", "Next": ID_GCLICK, "Failed": ID_GSHOOT})
add_gint(ID_GSTICK, {"Type": "Simple", "RunTime": 0.1, "Effects": {"WorldSoundEventId": SND_GMISS}})
add_gint(ID_GHIT, {"Type": "Simple", "RunTime": 0.1, "Effects": {"WorldSoundEventId": SND_GHIT}})
add_gint(ID_GGONE, {"Type": "RemoveEntity", "Entity": "User"})
XROOT_JSON = None
if XBOW_RIGHT == "grapple":
    # FIX ROUND: the vanilla Tags are kept too (same root id - anything that reads the Attack tag sees what it saw before)
    XROOT_JSON = {"RequireNewClick": True, "Cooldown": {"Cooldown": 0.25}, "Rules": json.loads(json.dumps(VXROOT["Rules"])), "Interactions": [ID_GRAPPLE],
                  "Tags": json.loads(json.dumps(VXROOT["Tags"]))}
    ROOTS[XROOT] = XROOT_JSON
    put(P_XROOT % XROOT, XROOT_JSON)
# the bolt: Projectile_Config_Arrow_Base fully resolved (no Parent) + our flight, sounds and chains. ProjectileMiss = the impact sound only (no
# Common_Projectile_Despawn, no Block_Break_Projectile): it rests in the block; ProjectileHit = a tick sound + our despawn (no DamageEntity)
PCFG = {"Model": GBOLT, "SpawnRotationOffset": dict(_pb["SpawnRotationOffset"]), "SpawnOffset": dict(_pb["SpawnOffset"]),
        "Physics": {"Type": "Standard", "Gravity": BOLT_GRAVITY, "TerminalVelocityAir": 70, "TerminalVelocityWater": 15, "RotationMode": "VelocityDamped",
                    "Bounciness": 0.0, "SticksVertically": True},
        "LaunchForce": BOLT_FORCE, "LaunchWorldSoundEventId": SND_GLAUNCH, "LaunchLocalSoundEventId": SND_GLAUNCH_L,
        "Interactions": {"ProjectileHit": {"Interactions": [ID_GHIT, ID_GGONE]}, "ProjectileMiss": {"Interactions": [ID_GSTICK]}}}
put(P_PCFG % GBOLT, PCFG)
_gm = json.loads(json.dumps(_vam))
for _t in _gm["Trails"]:
    _t["TrailId"] = GTRAIL
put(P_MODEL % GBOLT, _gm)
GMODEL_JSON = _gm
_gt2 = json.loads(json.dumps(_vtr))
_gt2["Start"]["Color"] = ROPE_COLOR + "e0"
_gt2["End"]["Color"] = ROPE_COLOR + "00"
_gt2["LifeSpan"] = 40
_gt2["RenderMode"] = "BlendLinear"
put(P_TRAIL % GTRAIL, _gt2)
EFX = {FX_GOUT: {"Infinite": True}, FX_GCLICK: {"Duration": 0.5, "OverlapBehavior": "Overwrite"}}
for _e, _d in EFX.items():
    put(P_EFX % _e, _d)


def rope_color(x):
    """a vanilla particle colour moved onto the rope's hue (ROPE_COLOR), saturation / value kept within the rope's range"""
    m = re.match(r"^(rgba\()?#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?(.*)$", x)
    if not m:
        return x
    h6 = m.group(2)
    r, g, b = (int(h6[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    th, ts, tv = colorsys.rgb_to_hsv(*(int(ROPE_COLOR[i:i + 2], 16) / 255.0 for i in (1, 3, 5)))
    r, g, b = colorsys.hsv_to_rgb(th, ts, min(vv, tv * 1.2))
    out = "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in (r, g, b))
    return (m.group(1) or "") + out + (m.group(3) or "") + m.group(4)


def rope_tree(x):
    if isinstance(x, dict):
        return dict((k, (rope_color(v) if (k == "Color" and isinstance(v, str)) else rope_tree(v))) for k, v in x.items())
    if isinstance(x, list):
        return [rope_tree(v) for v in x]
    return x


assert abs(hue(rope_color("#5bff57")) - hue(ROPE_COLOR)) < 2.0
ROPE_FILES = []
_rd = json.loads(AZ.read(_IDX["psys"]["GreenOrbTrail"][0]).decode("utf-8-sig"))      # the blink trail light's base (deployed, seen in game)
for _sp in _rd["Spawners"]:
    _src = _sp["SpawnerId"]
    _dst = "SkyyArmory_Rope_" + _src.replace("GreenOrb", "")
    assert _src in _IDX["pspawn"] and _dst not in PSP.values(), _src
    if (P_PSPAWN % _dst) not in ASSETS:
        put(P_PSPAWN % _dst, rope_tree(json.loads(AZ.read(_IDX["pspawn"][_src][0]).decode("utf-8-sig"))))
        ROPE_FILES.append(P_PSPAWN % _dst)
    _sp["SpawnerId"] = _dst
put(P_PSYS % GDOT, _rd)
ROPE_FILES.append(P_PSYS % GDOT)
G_FILES = [P_XINT % i for i in GINTS] + ([P_XROOT % XROOT] if XROOT_JSON else []) + [P_PCFG % GBOLT, P_MODEL % GBOLT, P_TRAIL % GTRAIL] \
    + [P_EFX % e for e in EFX] + ROPE_FILES
assert all(p in ASSETS for p in G_FILES)
_gtxt = "".join(ASSETS[p] for p in G_FILES)
assert "DamageEntity" not in _gtxt and "Block_Break" not in _gtxt and "Common_Projectile_Despawn" not in _gtxt and '"Ammo"' not in _gtxt \
    and "ModifyInventory" not in _gtxt and "SwapFrom" not in _gtxt, "a grapple file names damage / block breaking / ammo / the inventory"
'''
rep('''PS_RING = PS_GLOW if QUICK_LOOK == "recolor" else "GreenOrbTrail"      # the heal orb's ring points
''', '''PS_RING = PS_GLOW if QUICK_LOOK == "recolor" else "GreenOrbTrail"      # the heal orb's ring points
''' + G_ASSETS)

# ---- the reference closure of the grapple files (after the 0.1.1 closure)
rep('''assert not _bad_ref, "reference closure:\\n  " + "\\n  ".join(_bad_ref)
''', '''assert not _bad_ref, "reference closure:\\n  " + "\\n  ".join(_bad_ref)
# ---- 0.1.2: the grapple files - every id they name exists (ours or Assets.zip)
_gbad = []
if XROOT_JSON:
    _gbad += [x for x in XROOT_JSON["Interactions"] if x not in INTS]
_g = INTS[ID_GRAPPLE]
_gbad += [x for x in (_g["Next"], _g["Failed"]) if x not in INTS] + [x for x in _g["EntityEffectIds"] if x not in EFX]
_gbad += [INTS[ID_GCLICK]["EffectId"]] if INTS[ID_GCLICK]["EffectId"] not in EFX else []
_gbad += [INTS[ID_GSHOOT]["Config"]] if INTS[ID_GSHOOT]["Config"] != GBOLT else []
_gbad += [x for k in ("ProjectileHit", "ProjectileMiss") for x in PCFG["Interactions"][k]["Interactions"] if x not in INTS]
_gbad += [PCFG["Model"]] if (P_MODEL % PCFG["Model"]) not in ASSETS else []
_gbad += [t["TrailId"] for t in GMODEL_JSON["Trails"] if (P_TRAIL % t["TrailId"]) not in ASSETS]
_gbad += [p for p in [GMODEL_JSON["Model"], GMODEL_JSON["Texture"]] + [a["Model"] for a in GMODEL_JSON["DefaultAttachments"]]
          + [a["Texture"] for a in GMODEL_JSON["DefaultAttachments"]] if ("Common/" + p) not in AZ_SET]
_gbad += [s_ for s_ in (PCFG["LaunchWorldSoundEventId"], PCFG["LaunchLocalSoundEventId"]) if not az_has("sound", s_)]
for _f in ROPE_FILES:
    if _f.endswith(".particlesystem"):
        _gbad += [sp["SpawnerId"] for sp in json.loads(ASSETS[_f])["Spawners"] if (P_PSPAWN % sp["SpawnerId"]) not in ASSETS]
    else:
        _tx = json.loads(ASSETS[_f]).get("Particle", {}).get("Texture")
        _gbad += [_tx] if _tx and ("Common/" + _tx) not in AZ_SET else []
_gbad += [] if ("Common/" + json.loads(ASSETS[P_TRAIL % GTRAIL])["TexturePath"]) in AZ_SET else ["trail texture"]
assert not _gbad, "grapple reference closure: %s" % _gbad
''')

# ---- the clash scan knows the two new asset classes
rep('''                   ("Server/Projectiles/", "prj"), ("Server/Models/", "model"), ("Server/Entity/Trails/", "trail"),
                   ("Server/Item/Recipes/", "recipe")):''', '''                   ("Server/Projectiles/", "prj"), ("Server/Models/", "model"), ("Server/Entity/Trails/", "trail"),
                   ("Server/Item/Recipes/", "recipe"), ("Server/ProjectileConfigs/", "pcfg"), ("Server/Entity/Effects/", "efx")):''')

# ================================================================================================ JVM: tokens + probes
rep('''ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"''', '''T.update({   # 0.1.2 grapple (VERIFIED by reflection / bytecode 2026-10-06; every member is probed below)
    "SPPV": "com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsProvider",
    "SPST": "com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsProvider$STATE",
    "PRJC": "com.hypixel.hytale.server.core.modules.projectile.component.Projectile",
    "IMPC": "com.hypixel.hytale.server.core.modules.projectile.config.ImpactConsumer",
    "MODC": "com.hypixel.hytale.server.core.modules.entity.component.ModelComponent",
    "MDL": "com.hypixel.hytale.server.core.asset.type.model.config.Model",
    "V3I": "org.joml.Vector3i",
    "MNT": "com.hypixel.hytale.builtin.mounts.MountedComponent",
    "EST": "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType",
    "RTI": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.RootInteraction",
    "INVU": "com.hypixel.hytale.server.core.modules.entity.component.Invulnerable",     # FIX ROUND: never yank an Invulnerable mob (traders)
})
ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"''')
rep('''assert pool.get(T["MCF"]).getMethod("getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/IndexedLookupTableAssetMap;") is not None
PROBED.append("Damage.HIT_LOCATION<Vector4d>")''', '''assert pool.get(T["MCF"]).getMethod("getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/IndexedLookupTableAssetMap;") is not None
PROBED.append("Damage.HIT_LOCATION<Vector4d>")
# ---- 0.1.2: every engine member the grapple calls (spec 5 T2) - a game update that renames one stops the build
SIGS3 = [
    (T["SPPV"], "getComponentType", T["CTYPE"], []), (T["SPPV"], "getState", T["SPST"], []), (T["SPPV"], "getCreatorUuid", "java.util.UUID", []),
    (T["SPPV"], "getImpactConsumer", T["IMPC"], []), (T["SPPV"], "setImpactConsumer", "void", [T["IMPC"]]),
    (T["SPPV"], "bounceBlockPosition", T["V3I"], []), (T["SPPV"], "<init>", "void", [T["BBX"], "java.util.UUID",
        "com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsConfig", T["VEC"], "boolean"]),
    (T["IMPC"], "onImpact", "void", [T["REF"], T["VEC"], T["V3I"], T["REF"], S_, T["CB"]]),
    (T["PRJC"], "getComponentType", T["CTYPE"], []), (T["MODC"], "getComponentType", T["CTYPE"], []), (T["MODC"], "getModel", T["MDL"], []),
    (T["MDL"], "getModelAssetId", S_, []), (T["MNT"], "getComponentType", T["CTYPE"], []), (T["INVU"], "getComponentType", T["CTYPE"], []),
    (T["ECC"], "removeEffect", "void", [T["REF"], "int", T["CAC"]]), (T["ECC"], "hasEffect", "boolean", ["int"]),
    (T["ESM"], "setStatValue", "float", ["int", "float"]), (T["EST"], "getAssetMap", "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", []),
    ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex", "int", [O_]),
    (T["DMG"], "getCause", T["DCS"], []), (T["BOX"], "height", "double", []), (T["NPC"], "getRoleName", S_, []),
    (T["RTI"], "getAssetMap", "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", []),
    (T["DMOD"], "getFilterDamageGroup", T["SG"], []), (T["CB"], "removeEntity", "void", [T["REF"], T["REMR"]]),
    ("com.hypixel.hytale.server.core.modules.projectile.ProjectileModule", "spawnProjectile", T["REF"],
     ["java.util.UUID", "java.lang.Long", T["REF"], T["CB"], "com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig", T["VEC"], T["VEC"]]),
]
for _c, _m, _r, _a in SIGS3:
    probe_sig(_c, _m, _r, _a)
for _c, _f in ((T["SPST"], "RESTING"), (T["SPST"], "ACTIVE"), (T["SPST"], "INACTIVE"), (T["DCS"], "FALL")):
    _fld = pool.get(_c).getField(_f)
    assert JMod.isPublic(_fld.getModifiers()) and JMod.isStatic(_fld.getModifiers()), "%s.%s is not public static" % (_c, _f)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _f))
assert pool.get(T["IMPC"]).isInterface(), "ImpactConsumer is not an interface any more"
# the engine's own shapes the grapple relies on (bytecode, spec 2.2): StandardPhysicsTickSystem#tick sets RESTING on a block impact and calls
# the provider's ImpactConsumer with a null entity, sets INACTIVE on an entity impact and calls it with the entity; spawnProjectile makes the
# entity with Projectile + PredictedProjectile + ModelComponent and adds it with AddReason.SPAWN; the provider's constructor sets its own
# impact consumer (the one GrappleImpact wraps)
def _calls(cls, meth, desc=None):
    out = []
    for _mm in pool.get(cls).getDeclaredMethods():
        if str(_mm.getName()) != meth or (desc is not None and desc not in str(_mm.getSignature())):
            continue
        _cp, _it = _mm.getMethodInfo().getConstPool(), _mm.getMethodInfo().getCodeAttribute().iterator()
        while _it.hasNext():
            _p = _it.next()
            _op = _it.byteAt(_p)
            if _op in (0xb6, 0xb7, 0xb8, 0xb9):
                _ix = _it.u16bitAt(_p + 1)
                _tg = _cp.getTag(_ix)
                _nm = str(_cp.getInterfaceMethodrefName(_ix)) if _tg == _JCP.CONST_InterfaceMethodref else str(_cp.getMethodrefName(_ix))
                out.append(_nm)
            elif _op in (0xb2, 0xb3, 0xb4, 0xb5):
                out.append("." + str(_cp.getFieldrefName(_it.u16bitAt(_p + 1))))
    return out
_tk = _calls("com.hypixel.hytale.server.core.modules.projectile.system.StandardPhysicsTickSystem", "tick")
assert _tk.count("onImpact") == 2 and ".RESTING" in _tk and ".INACTIVE" in _tk and "rest" in _tk and "getImpactConsumer" in _tk, "StandardPhysicsTickSystem#tick changed"
_sp = _calls("com.hypixel.hytale.server.core.modules.projectile.ProjectileModule", "spawnProjectile", "Ljava/util/UUID;")
assert "addEntity" in _sp and ".SPAWN" in _sp and _sp.count("getComponentType") >= 8 and "createSpawnModel" in _sp, "ProjectileModule.spawnProjectile changed"
_spc = [str(c.getName()) for c in pool.get(T["SPPV"]).getDeclaredConstructors()]
_ic = []
for _k in pool.get(T["SPPV"]).getDeclaredConstructors():
    _cp, _it = _k.getMethodInfo().getConstPool(), _k.getMethodInfo().getCodeAttribute().iterator()
    while _it.hasNext():
        _p = _it.next()
        if _it.byteAt(_p) == 0xb5:
            _ic.append(str(_cp.getFieldrefName(_it.u16bitAt(_p + 1))))
assert "impactConsumer" in _ic, "StandardPhysicsProvider no longer sets its own impact consumer"
# the pull's Velocity Set carries NO VelocityConfig (the GrapplingHook way): PlayerVelocityInstructionSystem#tick must null-check the config
# before VelocityConfig.toPacket (an ifnull between getConfig and toPacket); the server's EffectCondition reads ECC.getActiveEffects
def _ops(cls, meth):
    out = []
    for _mm in pool.get(cls).getDeclaredMethods():
        if str(_mm.getName()) != meth:
            continue
        _cp, _it = _mm.getMethodInfo().getConstPool(), _mm.getMethodInfo().getCodeAttribute().iterator()
        while _it.hasNext():
            _p = _it.next()
            _op = _it.byteAt(_p)
            if _op in (0xc6, 0xc7):
                out.append("?null")
            elif _op in (0xb6, 0xb7, 0xb8, 0xb9):
                _ix = _it.u16bitAt(_p + 1)
                out.append(str(_cp.getInterfaceMethodrefName(_ix)) if _cp.getTag(_ix) == _JCP.CONST_InterfaceMethodref else str(_cp.getMethodrefName(_ix)))
    return out
_pv = _ops("com.hypixel.hytale.server.core.universe.system.PlayerVelocityInstructionSystem", "tick")
assert "getConfig" in _pv and "toPacket" in _pv and "?null" in _pv[_pv.index("getConfig"):_pv.index("toPacket")], "PlayerVelocityInstructionSystem no longer accepts a null VelocityConfig"
_ecr = _ops(PI + "none.EffectConditionInteraction", "firstRun")
assert "getActiveEffects" in _ecr and "containsKey" in _ecr, "EffectConditionInteraction#firstRun no longer reads the active effects"
assert "addInfiniteEffect" in _ops(T["ECC"], "addEffect"), "EffectControllerComponent.addEffect no longer routes Infinite effects"
PROBED.append("PlayerVelocityInstructionSystem null VelocityConfig / EffectConditionInteraction active effects / ECC infinite effects (bytecode)")
PROBED.append("StandardPhysicsTickSystem#tick / ProjectileModule.spawnProjectile / StandardPhysicsProvider.<init> shapes (bytecode)")''')

# ================================================================================================ Java tables + classes
rep('''PRJ_CHECK_IDS = sorted(PRJS)''', '''PRJ_CHECK_IDS = sorted(PRJS)
ROOT_CHECK_IDS = [XROOT] if XROOT_JSON else []      # 0.1.2: the crossbow right click must come from our pack''')
rep('''          "public static final String[] PRJ_CHECK = %s;" % jarr(PRJ_CHECK_IDS),''', '''          "public static final String[] PRJ_CHECK = %s;" % jarr(PRJ_CHECK_IDS),
          "public static final String[] ROOT_CHECK = %s;" % jarr(ROOT_CHECK_IDS),''')
rep('''ttick = pool.makeClass(PKG + ".TravTick", pool.get(T["ETS"]))
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick]''',
    '''ttick = pool.makeClass(PKG + ".TravTick", pool.get(T["ETS"]))
# 0.1.2 grapple (spec 3.1.3): pure maths (bare-JVM tested), the per-player record, the engine glue, the impact wrapper, two systems
gmath = pool.makeClass(PKG + ".GrappleMath")
gstate = pool.makeClass(PKG + ".GrappleState")
grap = pool.makeClass(PKG + ".Grapple")
gimp = pool.makeClass(PKG + ".GrappleImpact")
gbolt = pool.makeClass(PKG + ".GrappleBoltSys", pool.get(T["RSYS"]))
gfall = pool.makeClass(PKG + ".GrappleFallSys", pool.get(T["DES"]))
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall]''')

# ================================================================================================ settings: file text, cats, fixed rows, fields, loader
rep('''    "# At most this much Stamina per traversal (0 = no cap; vanilla max Stamina is 10).",
    "trav.staminaCap=10",''', '''    "# At most this much Stamina per traversal (0 = no cap). Skyy 2026-10-06: 5 = two traversals per 10-Stamina bar.",
    M12_MARK,
    "trav.staminaCap=5",''')
rep('''    "quick.staffBonus=15",
    "",
    "# ---- Mana check (server log)",''', '''    "quick.staffBonus=15",
    "",
    "# ---- crossbow grapple bolt (right click on a crossbow; research/Grapple-Bolt-Spec.md + Skyy's answers 2026-10-06)",
] + [x for _r in CFG_GRAPPLE for x in ("# " + _r[14], "%s=%s" % (_r[0], _r[4]))] + [
    "",
    "# ---- Mana check (server log)",''')
rep('''CFG_CATS = [("trav", "Traversal"), ("blink", "Staff blink"), ("hop", "Wand hop + burst"), ("damage", "Damage"), ("quick", "Quick shot"),''',
    '''CFG_CATS = [("trav", "Traversal"), ("blink", "Staff blink"), ("hop", "Wand hop + burst"), ("grapple", "Crossbow grapple"), ("damage", "Damage"),
            ("quick", "Quick shot"),''')
rep('''FIXED_VAL = dict((f[0], f[3]) for f in FIXED)''', '''FIXED.append(("grapple.flight", "Grapple bolt flight (fixed in the jar)", "grapple", "%d / %d (crossbow bolts 40 / 10)" % (BOLT_FORCE, BOLT_GRAVITY),
              "LaunchForce / Gravity of the client-predicted bolt. Build constants BOLT_FORCE, BOLT_GRAVITY."))
FIXED.append(("grapple.rightClick", "Crossbow right click (fixed in the jar)", "grapple",
              "grapple (the vanilla guard is replaced)" if XBOW_RIGHT == "grapple" else "the vanilla guard (grapple off in this build)",
              "Skyy 2026-10-06: replace the guard. Build constant XBOW_RIGHT."))
FIXED_VAL = dict((f[0], f[3]) for f in FIXED)''')
rep('''          "public static volatile String TRAV_TEXT = \\"\\";",''', '''          "public static volatile String TRAV_TEXT = \\"\\";",
          "public static volatile String GRAPPLE_TEXT = \\"\\";",''')
# the loader lines of the grapple rows (clamped like the kit validates; no '%' - the apply() source is %-formatted)
_gl = []
for _r in G_ROWS:
    k, t, d, lo, hi, fld = _r[0], _r[3], _r[4], _r[5], _r[6], _r[11]
    if t == "bool":
        _gl.append('  %s = bool(c.getProperty("%s"), %s);' % (fld, k, d))
    elif t == "int":
        _gl.append('  %s = intOf(c.getProperty("%s"), %s, %s, %s);' % (fld, k, d, lo, hi))
    elif t == "dec":
        _gl.append('  %s = dec(c.getProperty("%s"), %r, %r, %r);' % (fld, k, float(d), float(lo), float(hi)))
    elif t == "choice":
        _gl.append('  { String gv = String.valueOf(c.getProperty("%s")).trim().toLowerCase(); %s = (gv.equals("off") || gv.equals("always")) ? gv : "pull"; }' % (k, fld))
    elif t == "text":
        _gl.append('  { String gt = c.getProperty("%s"); %s = gt == null ? "%s" : (gt.trim().length() > %s ? gt.trim().substring(0, %s) : gt.trim()); }' % (k, fld, d, hi, hi))
    else:
        raise SystemExit("grapple row type %s" % t)
G_LOADER = "\n".join(_gl)
assert "%" not in G_LOADER
rep('''  STAMINA_CAP = intOf(c.getProperty("trav.staminaCap"), 10, 0, 100);''', '''  STAMINA_CAP = intOf(c.getProperty("trav.staminaCap"), 5, 0, 100);      // 0.1.2: default 5 (Skyy 2026-10-06)''')
rep('''  STAFF_BONUS = intOf(c.getProperty("quick.staffBonus"), 15, 0, 100);
  TRAV_TEXT = travText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:trav", TRAV_TEXT); } catch (Throwable tb) { }''', '''  STAFF_BONUS = intOf(c.getProperty("quick.staffBonus"), 15, 0, 100);
  TRAV_TEXT = travText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:trav", TRAV_TEXT); } catch (Throwable tb) { }
''' + G_LOADER + '''
  GRAPPLE_TEXT = grappleText();
  try { @PKG@.ArmoryDefs.bridge().put("armory:grapple", GRAPPLE_TEXT); } catch (Throwable tg) { }''')
rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''', '''# 0.1.2: the grapple's live numbers (bridge armory:grapple, the start line)
M(cfg, r"""
public static String grappleText() {
  return "grapple " + (PART_GRAPPLE ? "on" : "OFF") + " - rope " + G_ROPE_LEN + " blocks (stuck / hooked: snaps past " + G_SNAP + ", lasts " + G_ANCHOR
    + " s) - pull " + G_SPEED + " b/s (down at most " + G_MAXDOWN + ")" + (G_EASE > 0.0 ? ", eases x" + G_EASE + " near the end" : "") + ", stops " + G_STOP + " short, half pull " + G_HALF_PCT + "%, at most " + G_PULL_MAX
    + " s - let go keeps " + G_KEEP + "% + " + G_LIFT + " up - arrival hop " + G_HOP + ", no fall damage " + G_GRACE + " s - cost " + G_STAM + " Stamina + "
    + G_MANA + " Mana (half " + G_HSTAM + " + " + G_HMANA + "), regen pause " + G_REGEN + " s - rope " + G_ROPE + " every " + G_SPACING + " blocks"
    + (G_CD > 0.0 ? " - cooldown " + G_CD + " s" : "") + " - hooked mobs up to size " + G_YANK_SIZE + " are yanked, bigger ones and bosses (" + G_BOSS
    + ") pull you, never yanked: Invulnerable mobs + (" + G_NOYANK + "), players " + (G_YANK_PLAYERS ? "yanked where PvP is on (never party)" : "never yanked");
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c) {''')

# ---- the one-time trav.staminaCap update (ArmoryCfg.migrate012; the SkyyAccessories migrate055 rules and its kit helpers)
M12_JAVA = r'''
# 0.1.2: the one-time trav.staminaCap update (Skyy 2026-10-06: cap 10 -> 5). The SkyyAccessories 0.5.5 migrate055 rules: a one-line entry still
# on the old default 10 becomes 5 (value text only), anything else is kept and logged, a marker comment makes it run once, History copy verified
# first, one Undo-able change-log line, every other byte and the line endings kept. setup() runs it BEFORE ArmoryCfg.load() + CfgPub.start.
for f in ("public static final String M12_KEY = \"trav.staminaCap\";", "public static final String M12_OLD = \"10\";",
          "public static final String M12_NEW = \"5\";", "public static final String M12_MARK = %s;" % jstr(M12_MARK),
          "public static final String M12_MARK_ID = %s;" % jstr(M12_MARK_ID), "public static final String M12_WHO = \"SkyyArmory 0.1.2\";",
          "public static volatile String M12_LAST = \"\";"):
    F(cfg, f)
M(cfg, r"""
public static boolean m12Is(String v, String want) {
  if (v == null) return false;
  try { return Integer.parseInt(v.trim()) == Integer.parseInt(want); } catch (Throwable t) { return false; }
}""")
# pure text step (ISO-8859-1 chars in and out; the kit's own parser CfgFile). null = the marker is already in a comment line. Else { new text,
# "trav.staminaCap 10 -> 5" or "", String[] kept notes, String[] { key, old, new } or empty }. The LAST live entry (the one Properties keeps)
# decides; the marker goes on its own line right above the first entry, or at the end of a file without one (the file's own line ending)
M(cfg, r"""
public static Object[] m12Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int first = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M12_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (M12_KEY.equals(@PKG@.CfgFile.key(s))) {
      if (first < 0) first = k;
      eff = @PKG@.CfgFile.value(l, k).trim();
      multi = e > k;
    }
    k = e + 1;
  }
  boolean mig = eff != null && !multi && m12Is(eff, M12_OLD);
  String chg = "";
  String[] rows = new String[0];
  java.util.ArrayList kept = new java.util.ArrayList();
  if (mig) {
    chg = M12_KEY + " " + @PKG@.CfgRows.oneLine(eff) + " -> " + M12_NEW;
    rows = new String[] { M12_KEY, eff, M12_NEW };
  } else if (eff != null && (multi || !m12Is(eff, M12_NEW))) {
    kept.add(M12_KEY + "=" + @PKG@.CfgRows.oneLine(eff) + " kept (custom) - the 0.1.2 default is " + M12_NEW);
  }
  String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
  if (first < 0) {
    String out0 = (text.length() == 0 || text.endsWith("\n")) ? text + M12_MARK + nl : text + nl + M12_MARK;
    return new Object[] { out0, chg, (String[]) kept.toArray(new String[0]), rows };
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == first) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M12_MARK + (crm ? "\r" : ""));
    }
    if (mig && e2 == k && M12_KEY.equals(@PKG@.CfgFile.key(s2)) && m12Is(@PKG@.CfgFile.value(l, k).trim(), M12_OLD)) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M12_NEW + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M12_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg, (String[]) kept.toArray(new String[0]), rows };
}""")
M(cfg, r"""
public static String m12Log(String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M12_WHO + "\t-\tupdate\t" + M12_KEY + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""")
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): History + change log live in the folder
# of config.properties (the kit's HOME, Skyy_SkyyArmory)
M(cfg, r"""
public static void m12Kit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.ArmoryLog.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""")
# CfgHist.snapshot swallows its own errors: config-history must really hold a copy with exactly these bytes (the new copy, or the newest one
# when snapshot skipped an equal file) before the rewrite
M(cfg, r"""
public static boolean m12Saved(byte[] old) {
  String[] have = @PKG@.CfgHist.list(0);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(0, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""")
M(cfg, r"""
public static synchronized String migrate012() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m12Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m12Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M12_WHO, "before the 0.1.2 traversal Stamina cap update");
    if (!m12Saved(old)) {
      @PKG@.ArmoryLog.warn("config.properties NOT updated to the 0.1.2 traversal Stamina cap: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    if (rows.length == 3) {
      @PKG@.CfgLog.enqueue(m12Log(rows[1], rows[2]));
      @PKG@.CfgLog.flush();
    }
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.2 traversal Stamina cap: " + chg + " (Skyy 2026-10-06: two traversals per bar; the old file is in config-history; Server Setup -> Changes can undo it)";
    else msg = "config.properties: no trav.staminaCap line held the old 10 - nothing changed (0.1.2 Stamina cap marker added)";
    @PKG@.ArmoryLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.ArmoryLog.info(kept[i]); all.append("; ").append(kept[i]); }
    M12_LAST = all.toString();
    return M12_LAST;
  } catch (Throwable t) {
    @PKG@.ArmoryLog.warn("could not update config.properties to the 0.1.2 traversal Stamina cap (the file is used as it is): " + t);
    return "";
  }
}""")
'''
rep('''M(cfg, "public static void useDefaults() { apply(props(DEF_CFG)); }")
''', '''M(cfg, "public static void useDefaults() { apply(props(DEF_CFG)); }")
''' + M12_JAVA)

# ================================================================================================ pack check: + the crossbow root
rep('''  int mp = packOf(pm, @PKG@.ArmoryDefs.PRJ_CHECK, other, miss);''', '''  int mp = packOf(pm, @PKG@.ArmoryDefs.PRJ_CHECK, other, miss);
  int mr = 0;          // 0.1.2: the crossbow right click root (another pack winning it = the vanilla guard or someone else's chain)
  if (@PKG@.ArmoryDefs.ROOT_CHECK.length > 0) {
    @DAM@ rm = null;
    try { rm = @RTI@.getAssetMap(); } catch (Throwable t) { rm = null; }
    if (rm != null) mr = packOf(rm, @PKG@.ArmoryDefs.ROOT_CHECK, other, miss);
  }''')
rep('''    + " interactions, " + mp + " of " + @PKG@.ArmoryDefs.PRJ_CHECK.length + " projectiles come from " + @PKG@.ArmoryDefs.PACK;''',
    '''    + " interactions, " + mp + " of " + @PKG@.ArmoryDefs.PRJ_CHECK.length + " projectiles, " + mr + " of " + @PKG@.ArmoryDefs.ROOT_CHECK.length
    + " roots (the crossbow right click) come from " + @PKG@.ArmoryDefs.PACK;''')

# ================================================================================================ the grapple Java (spec 3.1.3)
G_JAVA = r'''
# ---------------------------------------------------------------- 0.1.2 THE GRAPPLE BOLT (research/Grapple-Bolt-Spec.md 2.1-2.4 + 3.1.3; Skyy's answers win)
# ---- GrappleMath: PURE maths (no engine type; the bare-JVM harness runs it on numbers)
M(gmath, r"""
public static double dist(double ax, double ay, double az, double bx, double by, double bz) {
  double dx = bx - ax;
  double dy = by - ay;
  double dz = bz - az;
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}""")
# the HALF PULL's target (Skyy: "if you pull before it locks on to something it pulls you half way"): pct % of the way from p to the bolt
M(gmath, r"""
public static double[] halfTarget(double px, double py, double pz, double bx, double by, double bz, int pct) {
  double f = (double) pct / 100.0;
  if (f < 0.0) f = 0.0;
  if (f > 1.0) f = 1.0;
  return new double[] { px + (bx - px) * f, py + (by - py) * f, pz + (bz - pz) * f };
}""")
# the pull's velocity: speed along p -> t, the downward part at most maxDown (landings stay under MinFallSpeedToEngageRoll 21).
# FIX ROUND (critic: ping overshoot): ease > 0 = near the end the speed is at most ease x the distance left (at least 4 b/s, never above
# speed) - the GrapplingHook 2.0.2 shape (min(max, dist x 2.5)); the server sees the player ~ping late, so a slower end overshoots less
M(gmath, r"""
public static double easeSpeed(double l, double speed, double ease) {
  if (!(ease > 0.0)) return speed;
  double e = l * ease;
  if (e < 4.0) e = 4.0;
  return e < speed ? e : speed;
}""")
M(gmath, r"""
public static double[] pullVector(double px, double py, double pz, double tx, double ty, double tz, double speed0, double maxDown, double ease) {
  double dx = tx - px;
  double dy = ty - py;
  double dz = tz - pz;
  double l = Math.sqrt(dx * dx + dy * dy + dz * dz);
  if (!(l > 1.0E-6) || !(speed0 > 0.0) || Double.isNaN(l) || Double.isInfinite(l)) return new double[] { 0.0, 0.0, 0.0 };
  double speed = easeSpeed(l, speed0, ease);
  double vx = dx / l * speed;
  double vy = dy / l * speed;
  double vz = dz / l * speed;
  if (maxDown > 0.0 && vy < -maxDown) vy = -maxDown;
  return new double[] { vx, vy, vz };
}""")
# LET GO (click 3): the last pull velocity x keep % + lift up (Skyy: "let go, and keep momentum ... chain grapples and sorta fly")
M(gmath, r"""
public static double[] releaseVector(double vx, double vy, double vz, int keepPct, double lift) {
  double k = (double) keepPct / 100.0;
  if (k < 0.0) k = 0.0;
  double up = lift > 0.0 ? lift : 0.0;
  return new double[] { vx * k, vy * k + up, vz * k };
}""")
# ARRIVAL: the bolt above the feet = a hop up (onto ledges), else a soft stop (x 0.25)
M(gmath, "public static boolean above(double ty, double feetY) { return ty > feetY + 0.5; }")
M(gmath, r"""
public static double[] arriveVector(double vx, double vy, double vz, boolean above, double hop) {
  if (above && hop > 0.0) return new double[] { vx * 0.25, hop, vz * 0.25 };
  return new double[] { vx * 0.25, vy * 0.25, vz * 0.25 };
}""")
M(gmath, r"""
public static int ropeDots(double d, double spacing) {
  if (!(d > 0.0) || !(spacing > 0.0) || Double.isInfinite(d)) return 0;
  int n = (int) Math.floor(d / spacing);
  if (n > 40) n = 40;
  return n;
}""")
# the stall rule: a pull tick makes progress when the distance shrank by more than 0.1 block below the best so far
M(gmath, "public static boolean progressed(double best, double d) { return d < best - 0.1; }")
M(gmath, r"""
public static boolean bossName(String role, String words) {
  if (role == null || words == null) return false;
  String r = role.toLowerCase();
  String[] ws = words.split(",");
  for (int i = 0; i < ws.length; i++) {
    String w = ws[i].trim().toLowerCase();
    if (w.length() > 0 && r.indexOf(w) >= 0) return true;
  }
  return false;
}""")
# a HOOKED target (Skyy 2026-10-06: Harpoon-style): 1 = YANK it to you, 2 = it pulls YOU. Bosses never yanked; a player only with the row on
# AND PvP on AND not your party; a mob whose hitbox w x h x d is at most yankSize (0 = never) is yanked
M(gmath, r"""
public static int hookKind(double w, double h, double d, double yankSize, boolean boss, boolean player, boolean yankPlayers, boolean pvp, boolean ally) {
  if (boss) return 2;
  if (player) return (yankPlayers && pvp && !ally) ? 1 : 2;
  if (!(yankSize > 0.0)) return 2;
  double v = w * h * d;
  if (!(v > 0.0)) return 2;
  return v <= yankSize + 1.0E-9 ? 1 : 2;
}""")

# ---- GrappleState: one player's grapple (world thread of its store only). mode 1 = bolt OUT, 2 = PULL (you), 3 = YANK (the hooked mob);
# kind 1 = full pull to the stuck bolt, 2 = half pull, 3 = pulled to a hooked big mob / boss / player, 4 = yank
for f in ("public java.util.UUID u;", "public @REF@ ref;", "public @ST@ st;", "public String item;", "public @REF@ bolt;", "public int mode;",
          "public boolean stuck;", "public boolean hooked;", "public @REF@ hook;", "public boolean hookPlayer;", "public boolean boss;",
          "public long shotAt;", "public long stuckAt;", "public long pullAt;", "public int kind;", "public double tx;", "public double ty;",
          "public double tz;", "public double best;", "public int stall;", "public int ticks;", "public double vx;", "public double vy;", "public double vz;",
          "public boolean protect;"):
    F(gstate, f)
C(gstate, r"""
public GrappleState(java.util.UUID u, @REF@ ref, @ST@ st, String item, @REF@ bolt, long now) {
  this.u = u;
  this.ref = ref;
  this.st = st;
  this.item = item;
  this.bolt = bolt;
  this.mode = 1;
  this.stuck = false;
  this.hooked = false;
  this.hook = null;
  this.hookPlayer = false;
  this.boss = false;
  this.shotAt = now;
  this.stuckAt = now;
  this.pullAt = 0L;
  this.kind = 0;
  this.best = 1.0E9;
  this.stall = 0;
  this.ticks = 0;
}""")

# ---- Grapple: the engine glue (never throws to the engine)
for f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap GRACE = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap LASTEND = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long SHOTS = 0L;", "public static volatile long PULLS = 0L;", "public static volatile long HALFS = 0L;",
          "public static volatile long RELEASES = 0L;", "public static volatile long ARRIVALS = 0L;", "public static volatile long SNAPS = 0L;",
          "public static volatile long REFUSED = 0L;", "public static volatile long HOOKS = 0L;", "public static volatile long YANKS = 0L;",
          "public static volatile long ENDS = 0L;", "public static volatile long FALLS = 0L;", "public static volatile long DOTS = 0L;",
          "public static volatile long CLICKS = 0L;", "public static volatile long STALE = 0L;",
          "public static volatile String LAST_WHY = \"\";",
          "public static volatile int OUT_I = -1;", "public static volatile int CLICK_I = -1;",        # FIX ROUND: cached effect indexes
          "public static volatile int SWEEP_N = 0;", "public static volatile long SWEPT = 0L;",       # FIX ROUND: stale-record sweep (disconnects)
          "public static volatile long DOT_WIN = 0L;", "public static volatile int DOT_LEFT = 0;",     # FIX ROUND: the shared rope dot budget
          "public static volatile long DOTS_CUT = 0L;", "public static final int DOT_BUDGET = %d;" % ROPE_BUDGET,
          "public static final int SWEEP_EVERY = 300;",
          "public static volatile boolean SYS_BOLT = false;", "public static volatile boolean SYS_FALL = false;",
          "public static volatile java.util.Map HAND = null;",          # HARNESS SEAM ONLY (null in the game = InventoryComponent.getItemInHand)
          "public static final String BOLT = %s;" % jstr(GBOLT), "public static final String OUT = %s;" % jstr(FX_GOUT),
          "public static final String CLICK = %s;" % jstr(FX_GCLICK), "public static final String PS_ROPE = %s;" % jstr(GDOT),
          "public static final String SND_NO = %s;" % jstr(SND_GNO), "public static final int PULL_EVERY = %d;" % PULL_EVERY):
    F(grap, f)
M(grap, r"""public static void warn(String key, String msg) { @PKG@.ArmoryLog.warnOnce("grapple:" + key, msg); }""")
M(grap, r"""
public static int fxIndex(String id) {
  try { return @EFX@.getAssetMap().getIndex(id); } catch (Throwable t) { return -1; }
}""")
# FIX ROUND (critic: per-tick cost): the OUT / CLICK indexes are looked up once (kept only once found - an asset index never moves)
M(grap, r"""
public static int outI() {
  int i = OUT_I;
  if (i < 0) { i = fxIndex(OUT); if (i >= 0) OUT_I = i; }
  return i;
}""")
M(grap, r"""
public static int clickI() {
  int i = CLICK_I;
  if (i < 0) { i = fxIndex(CLICK); if (i >= 0) CLICK_I = i; }
  return i;
}""")
M(grap, r"""
public static @ECC@ ecc(@CAC@ acc, @REF@ r) {
  try {
    if (r == null) return null;
    Object o = acc.getComponent(r, @ECC@.getComponentType());
    return o instanceof @ECC@ ? (@ECC@) o : null;
  } catch (Throwable t) { return null; }
}""")
M(grap, r"""
public static boolean hasFx(@ECC@ c, int i) {
  try { return c != null && i >= 0 && c.hasEffect(i); } catch (Throwable t) { return false; }
}""")
M(grap, r"""
public static void addFx(@CAC@ acc, @REF@ r, String id) {
  try {
    @ECC@ c = ecc(acc, r);
    Object fx = @EFX@.getAssetMap().getAsset(id);
    if (c != null && fx instanceof @EFX@) c.addEffect(r, (@EFX@) fx, acc);
    else warn("fx:" + id, "the effect " + id + " is not loaded (or the player has no effects) - the grapple cannot see clicks");
  } catch (Throwable t) { warn("addfx", "adding " + id + " failed (" + t + ")"); }
}""")
M(grap, r"""
public static void removeFx(@CAC@ acc, @REF@ r, String id) {
  try {
    @ECC@ c = ecc(acc, r);
    int i = fxIndex(id);
    if (hasFx(c, i)) c.removeEffect(r, i, acc);
  } catch (Throwable t) { warn("rmfx", "removing " + id + " failed (" + t + ")"); }
}""")
M(grap, r"""
public static java.util.UUID uuidOf(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @PR@.getComponentType());
    return o instanceof @PR@ ? ((@PR@) o).getUuid() : null;
  } catch (Throwable t) { return null; }
}""")
M(grap, r"""
public static String hand(@CAC@ acc, @REF@ r, java.util.UUID u) {
  java.util.Map h = HAND;
  if (h != null) {
    Object o = h.get(u);
    return o == null ? null : String.valueOf(o);
  }
  return @PKG@.ArmoryTrav.handItem(acc, r);
}""")
M(grap, "public static boolean same(String a, String b) { return a == null ? b == null : a.equals(b); }")
M(grap, r"""
public static boolean mounted(@CAC@ acc, @REF@ r) {
  try { return acc.getComponent(r, @MNT@.getComponentType()) != null; } catch (Throwable t) { return false; }
}""")
M(grap, r"""
public static @SPPV@ phys(@CAC@ acc, @REF@ b) {
  try {
    if (b == null || !b.isValid()) return null;
    Object o = acc.getComponent(b, @SPPV@.getComponentType());
    return o instanceof @SPPV@ ? (@SPPV@) o : null;
  } catch (Throwable t) { return null; }
}""")
# one Velocity Set (PlayerVelocityInstructionSystem -> one ChangeVelocity packet to that player; NPCVelocityInstructionSystem -> the role's
# motion controller, with the dagger dash's config like a knockback)
M(grap, r"""
public static boolean setVel(@CAC@ acc, @REF@ r, double[] v, boolean npc) {
  try {
    if (r == null || v == null || !r.isValid()) return false;
    Object o = acc.getComponent(r, @VEL@.getComponentType());
    if (!(o instanceof @VEL@)) return false;
    @VCF@ cf = null;
    if (npc) cf = @PKG@.ArmoryTrav.dash();
    ((@VEL@) o).addInstruction(new @VEC@(v[0], v[1], v[2]), cf, @CVT@.Set);
    return true;
  } catch (Throwable t) { warn("vel", "a grapple velocity failed (" + t + ")"); return false; }
}""")
M(grap, r"""
public static void tellRef(@CAC@ acc, @REF@ r, String text) {
  try {
    Object o = acc.getComponent(r, @PR@.getComponentType());
    if (o instanceof @PR@) @PKG@.ArmoryTrav.tell((@PR@) o, text);
  } catch (Throwable t) { }
}""")
# the pull's cost (server-side, live rows): 1 = paid (or not readable - never blocks), 0 = too little (nothing taken). Mana only where the
# player has a Mana pool (max > 0); the Stamina regen pause = the vanilla dodge's Set of StaminaRegenDelay
M(grap, r"""
public static int take(@CAC@ acc, @REF@ r, double stam, double mana) {
  try {
    Object o = acc.getComponent(r, @ESM@.getComponentType());
    if (!(o instanceof @ESM@)) return 1;
    @ESM@ m = (@ESM@) o;
    int si = @DST@.getStamina();
    int mi = @DST@.getMana();
    @ESV@ sv = null;
    @ESV@ mv = null;
    if (si >= 0) sv = m.get(si);
    if (mi >= 0) mv = m.get(mi);
    boolean useMana = mana > 0.0 && mv != null && mv.getMax() > 0.0f;
    if (stam > 0.0 && sv != null && (double) sv.get() + 1.0E-4 < stam) return 0;
    if (useMana && (double) mv.get() + 1.0E-4 < mana) return 0;
    if (stam > 0.0 && sv != null) m.subtractStatValue(si, (float) stam);
    if (useMana) m.subtractStatValue(mi, (float) mana);
    if (@PKG@.ArmoryCfg.G_REGEN > 0.0) {
      int pi = @EST@.getAssetMap().getIndex("StaminaRegenDelay");
      if (pi >= 0 && m.get(pi) != null) m.setStatValue(pi, (float) (0.0 - @PKG@.ArmoryCfg.G_REGEN));
    }
    return 1;
  } catch (Throwable t) { warn("cost", "the grapple cost could not be read (" + t + ") - the pull goes on free"); return 1; }
}""")
M(grap, r"""
public static void rope(@CB@ buf, double ax, double ay, double az, double bx, double by, double bz) {
  if ("off".equals(@PKG@.ArmoryCfg.G_ROPE)) return;
  int n0 = @PKG@.GrappleMath.ropeDots(@PKG@.GrappleMath.dist(ax, ay, az, bx, by, bz), @PKG@.ArmoryCfg.G_SPACING);
  long w = System.currentTimeMillis() / 100L;          // FIX ROUND: one shared budget of DOT_BUDGET dots per 100 ms (all grapplers)
  if (w != DOT_WIN) { DOT_WIN = w; DOT_LEFT = DOT_BUDGET; }
  int n = n0 < DOT_LEFT ? n0 : DOT_LEFT;
  if (n < 0) n = 0;
  DOT_LEFT = DOT_LEFT - n;
  if (n < n0) DOTS_CUT = DOTS_CUT + (long) (n0 - n);
  for (int k = 1; k <= n; k++) {
    double u = (double) k / (double) (n + 1);
    @PKG@.ArmoryTrav.particle(PS_ROPE, ax + (bx - ax) * u, ay + (by - ay) * u, az + (bz - az) * u, buf);
  }
  DOTS = DOTS + (long) n;
}""")
# the end of a grapple: the record goes, the bolt is removed (when still ours and in this store), the OUT / CLICK effects go
M(grap, r"""
public static void endIn(@PKG@.GrappleState s, @CB@ buf, @ST@ st, String why, boolean dropBolt) {
  if (s == null) return;
  STATES.remove(s.u, s);
  LASTEND.put(s.u, Long.valueOf(System.currentTimeMillis()));
  LAST_WHY = why;
  ENDS = ENDS + 1L;
  try { if (dropBolt && s.bolt != null && s.bolt.isValid() && s.st == st) buf.removeEntity(s.bolt, @REMR@.REMOVE); } catch (Throwable t) { }
  try {
    if (s.ref != null && s.ref.isValid() && s.st == st) {
      removeFx(buf, s.ref, OUT);
      removeFx(buf, s.ref, CLICK);
    }
  } catch (Throwable t2) { }
}""")
# GrappleImpact -> here (inside StandardPhysicsTickSystem, the bolt's world thread): a block = STUCK (the anchor), a creature (a player or an NPC
# with stats, not the shooter) = HOOKED (Skyy: "Hooks the mob"), anything else = the grapple is over (the bolt drops)
M(grap, r"""
public static void impact(java.util.UUID u, @REF@ bolt, @VEC@ pos, @REF@ hit, @CB@ buf) {
  if (u == null || bolt == null) return;
  @PKG@.GrappleState s = (@PKG@.GrappleState) STATES.get(u);
  if (s == null || s.mode != 1 || s.hooked || s.bolt == null || !s.bolt.equals(bolt)) return;
  long now = System.currentTimeMillis();
  if (hit == null) {
    s.stuck = true;
    s.stuckAt = now;
    if (pos != null) { s.tx = pos.x; s.ty = pos.y; s.tz = pos.z; }
    LAST_WHY = "bolt stuck";
    return;
  }
  boolean ok = false;
  try {
    ok = hit.isValid() && !hit.equals(s.ref) && !@PKG@.ArmoryTrav.dead(buf, hit)
      && (buf.getComponent(hit, @PR@.getComponentType()) != null
          || (buf.getComponent(hit, @NPC@.getComponentType()) != null && buf.getComponent(hit, @ESM@.getComponentType()) != null));
  } catch (Throwable t) { ok = false; }
  if (!ok) { endIn(s, buf, s.st, "the bolt hit something that cannot be hooked", false); return; }
  s.hooked = true;
  s.hook = hit;
  s.stuckAt = now;
  HOOKS = HOOKS + 1L;
  LAST_WHY = "hooked";
}""")
# ---- GrappleImpact: wraps the bolt's own ImpactConsumer (StandardPhysicsProvider's constructor sets it) - records, then the engine's runs
gimp.addInterface(pool.get(T["IMPC"]))
F(gimp, "public @IMPC@ inner;")
F(gimp, "public java.util.UUID u;")
C(gimp, "public GrappleImpact(@IMPC@ inner, java.util.UUID u) { this.inner = inner; this.u = u; }")
M(gimp, r"""
public void onImpact(@REF@ p, @VEC@ pos, @V3I@ blk, @REF@ hit, String name, @CB@ buf) {
  try { @PKG@.Grapple.impact(this.u, p, pos, hit, buf); }
  catch (Throwable t) { @PKG@.Grapple.warn("impact", "the grapple impact record failed (" + t + ")"); }
  if (this.inner != null) this.inner.onImpact(p, pos, blk, hit, name, buf);
}""")
# GrappleBoltSys.onEntityAdded (SPAWN of our bolt): the class lock (crossbows = Archer), part.grapple, cooldown, newest bolt wins, the impact
# wrapper, the OUT effect. A refused bolt is removed at once (no cost, no OUT)
M(grap, r"""
public static void onShot(@REF@ bolt, @SPPV@ sp, @ST@ st, @CB@ buf) {
  if (bolt == null || sp == null) return;
  long now = System.currentTimeMillis();
  java.util.UUID u = sp.getCreatorUuid();
  if (u == null) return;
  @REF@ pr = null;
  try { pr = ((@ES@) buf.getExternalData()).getRefFromUUID(u); } catch (Throwable t0) { pr = null; }
  if (pr == null || !pr.isValid()) { buf.removeEntity(bolt, @REMR@.REMOVE); LAST_WHY = "shooter gone"; return; }
  if (!@PKG@.ArmoryCfg.PART_GRAPPLE) { buf.removeEntity(bolt, @REMR@.REMOVE); LAST_WHY = "part.grapple off"; return; }
  String item = hand(buf, pr, u);
  if (!@PKG@.ArmoryTrav.allowed(u, item)) {
    buf.removeEntity(bolt, @REMR@.REMOVE);
    REFUSED = REFUSED + 1L;
    LAST_WHY = "class lock";
    tellRef(buf, pr, "Your class cannot use this crossbow's grapple bolt.");
    return;
  }
  if (item != null && item.toLowerCase().indexOf("crossbow") < 0) {
    // FIX ROUND (critic: other packs' items share the root - H1Z blunderbuss): the grapple only from an item whose id names a crossbow
    buf.removeEntity(bolt, @REMR@.REMOVE);
    REFUSED = REFUSED + 1L;
    LAST_WHY = "not a crossbow";
    warn("notxbow:" + item, item + " uses the crossbow right click (another pack shares Root_Weapon_Crossbow_Secondary_Guard): no grapple from it, and its own right click is replaced");
    return;
  }
  Object le = LASTEND.get(u);
  if (@PKG@.ArmoryCfg.G_CD > 0.0 && le instanceof Long && now - ((Long) le).longValue() < Math.round(@PKG@.ArmoryCfg.G_CD * 1000.0)) {
    buf.removeEntity(bolt, @REMR@.REMOVE);
    LAST_WHY = "cooldown";
    return;
  }
  @PKG@.GrappleState old = (@PKG@.GrappleState) STATES.get(u);
  if (old != null) {
    if (old.mode != 1 && old.st == st) { buf.removeEntity(bolt, @REMR@.REMOVE); LAST_WHY = "already pulling"; return; }
    STATES.remove(u, old);
    try { if (old.st == st && old.bolt != null && old.bolt.isValid()) buf.removeEntity(old.bolt, @REMR@.REMOVE); } catch (Throwable t1) { }
  }
  try { sp.setImpactConsumer(new @PKG@.GrappleImpact(sp.getImpactConsumer(), u)); }
  catch (Throwable t2) { warn("wrap", "the bolt's impact could not be watched (" + t2 + ") - bolts that hit a mob drop instead of hooking"); }
  STATES.put(u, new @PKG@.GrappleState(u, pr, st, item, bolt, now));
  addFx(buf, pr, OUT);
  SHOTS = SHOTS + 1L;
  LAST_WHY = "shot";
}""")
M(grap, r"""
public static int hookKind(@CB@ buf, @PKG@.GrappleState s) {
  @REF@ h = s.hook;
  Object po = null;
  try { po = buf.getComponent(h, @PR@.getComponentType()); } catch (Throwable t) { po = null; }
  boolean player = po instanceof @PR@;
  boolean ally = false;
  if (player) ally = @PKG@.ArmoryTrav.ally(s.u, ((@PR@) po).getUuid());
  boolean pvp = @PKG@.ArmoryTrav.pvp(@PKG@.ArmoryTrav.worldOf(buf));
  String role = null;
  try {
    Object no = buf.getComponent(h, @NPC@.getComponentType());
    if (no instanceof @NPC@) role = ((@NPC@) no).getRoleName();
  } catch (Throwable t1) { role = null; }
  boolean boss = @PKG@.GrappleMath.bossName(role, @PKG@.ArmoryCfg.G_BOSS);
  // FIX ROUND (critic: traders / pets yanked): an Invulnerable entity (Kweebec_Merchant, creative players) or a grapple.noYankWords role
  // is never yanked - it pulls you
  boolean prot = @PKG@.GrappleMath.bossName(role, @PKG@.ArmoryCfg.G_NOYANK);
  try { if (buf.getComponent(h, @INVU@.getComponentType()) != null) prot = true; } catch (Throwable t3) { }
  double w = 0.0;
  double hh = 0.0;
  double d = 0.0;
  try {
    Object bo = buf.getComponent(h, @BBX@.getComponentType());
    if (bo instanceof @BBX@ && ((@BBX@) bo).getBoundingBox() != null) {
      @BOX@ b = ((@BBX@) bo).getBoundingBox();
      w = b.width();
      hh = b.height();
      d = b.depth();
    }
  } catch (Throwable t2) { }
  s.hookPlayer = player;
  s.boss = boss;
  s.protect = prot;
  if (prot) return 2;
  return @PKG@.GrappleMath.hookKind(w, hh, d, @PKG@.ArmoryCfg.G_YANK_SIZE, boss, player, @PKG@.ArmoryCfg.G_YANK_PLAYERS, pvp, ally);
}""")
# FIX ROUND (critic: a yank's end left the mob at 24 b/s): the yanked target keeps a quarter of its last Set (like arrive)
M(grap, r"""
public static void yankStop(@PKG@.GrappleState s, @CB@ buf) {
  if (s.hook == null || !s.hook.isValid()) return;
  if (s.vx == 0.0 && s.vy == 0.0 && s.vz == 0.0) return;
  setVel(buf, s.hook, new double[] { s.vx * 0.25, s.vy * 0.25, s.vz * 0.25 }, !s.hookPlayer);
}""")
# click 3 = LET GO: a pull keeps its momentum (one last Set: keep % + lift; normal fall rules - no grace), a yank just stops
M(grap, r"""
public static void release(@PKG@.GrappleState s, @ST@ st, @CB@ buf) {
  RELEASES = RELEASES + 1L;
  if (s.mode == 2) {
    double[] v = @PKG@.GrappleMath.releaseVector(s.vx, s.vy, s.vz, @PKG@.ArmoryCfg.G_KEEP, @PKG@.ArmoryCfg.G_LIFT);
    setVel(buf, s.ref, v, false);
    s.vx = v[0];
    s.vy = v[1];
    s.vz = v[2];
    endIn(s, buf, st, "let go", true);
    return;
  }
  if (s.mode == 3) yankStop(s, buf);
  endIn(s, buf, st, "let go of the mob", true);
}""")
M(grap, r"""
public static void arrive(@PKG@.GrappleState s, @ST@ st, @CB@ buf, @VEC@ p, boolean reached) {
  boolean up = reached && s.kind == 1 && p != null && @PKG@.GrappleMath.above(s.ty, p.y);     // the hop only at a stuck bolt (a ledge)
  double[] v = @PKG@.GrappleMath.arriveVector(s.vx, s.vy, s.vz, up, @PKG@.ArmoryCfg.G_HOP);
  setVel(buf, s.ref, v, false);
  GRACE.put(s.u, Long.valueOf(System.currentTimeMillis() + Math.round(@PKG@.ArmoryCfg.G_GRACE * 1000.0)));
  ARRIVALS = ARRIVALS + 1L;
  endIn(s, buf, st, reached ? (up ? "arrived (hop)" : "arrived") : "blocked", true);
}""")
# click 2 (bolt out): stuck -> FULL pull to it; still flying -> HALF pull (the bolt is gone); hooked -> yank a small mob / be pulled to a big
# one; the cost first (too little = nothing happens, the bolt stays). click while pulled / yanking -> release
M(grap, r"""
public static void click(@PKG@.GrappleState s, @ST@ st, @CB@ buf, long now) {
  if (s.mode == 2 || s.mode == 3) { release(s, st, buf); return; }
  if (s.mode != 1) return;
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, s.ref);
  if (p == null) return;
  int kind = 0;
  double tx = 0.0;
  double ty = 0.0;
  double tz = 0.0;
  if (s.hooked) {
    if (s.hook == null || !s.hook.isValid() || @PKG@.ArmoryTrav.dead(buf, s.hook)) { endIn(s, buf, st, "the hooked mob is gone", true); return; }
    kind = hookKind(buf, s) == 1 ? 4 : 3;
    @VEC@ hp = @PKG@.ArmoryTrav.posOf(buf, s.hook);
    if (hp != null) { tx = hp.x; ty = hp.y + 0.9; tz = hp.z; }
  } else if (s.bolt == null && s.stuck) {
    kind = 1;          // FIX ROUND: the stuck bolt was taken by another mod (More Arrows' magnet) - pull to where it stuck
    tx = s.tx;
    ty = s.ty;
    tz = s.tz;
  } else {
    @SPPV@ sp = phys(buf, s.bolt);
    @VEC@ bp = null;
    if (sp != null) bp = @PKG@.ArmoryTrav.posOf(buf, s.bolt);
    if (sp == null || bp == null) { endIn(s, buf, st, "bolt gone", true); return; }
    @SPST@ bs = sp.getState();
    if (bs == @SPST@.RESTING) { kind = 1; tx = bp.x; ty = bp.y; tz = bp.z; }
    else if (bs == @SPST@.INACTIVE) { endIn(s, buf, st, "bolt stopped", true); return; }
    else {
      kind = 2;
      double[] h = @PKG@.GrappleMath.halfTarget(p.x, p.y + 0.9, p.z, bp.x, bp.y, bp.z, @PKG@.ArmoryCfg.G_HALF_PCT);
      tx = h[0];
      ty = h[1];
      tz = h[2];
    }
  }
  double stam = kind == 2 ? @PKG@.ArmoryCfg.G_HSTAM : @PKG@.ArmoryCfg.G_STAM;
  double mana = kind == 2 ? @PKG@.ArmoryCfg.G_HMANA : @PKG@.ArmoryCfg.G_MANA;
  if (take(buf, s.ref, stam, mana) == 0) {
    REFUSED = REFUSED + 1L;
    LAST_WHY = "too little Stamina or Mana";
    @PKG@.ArmoryTrav.sound(SND_NO, p.x, p.y, p.z, buf);
    tellRef(buf, s.ref, "Not enough Stamina or Mana to pull - " + @PKG@.TravMath.fmt(stam) + " Stamina + " + @PKG@.TravMath.fmt(mana) + " Mana needed.");
    return;
  }
  if (kind == 2) {
    try { if (s.bolt != null && s.bolt.isValid()) buf.removeEntity(s.bolt, @REMR@.REMOVE); } catch (Throwable t) { }
    s.bolt = null;
    HALFS = HALFS + 1L;
  } else if (kind == 4) {
    YANKS = YANKS + 1L;
  } else {
    PULLS = PULLS + 1L;
  }
  s.kind = kind;
  s.mode = kind == 4 ? 3 : 2;
  s.pullAt = now;
  s.tx = tx;
  s.ty = ty;
  s.tz = tz;
  s.best = 1.0E9;
  s.stall = 0;
  s.ticks = 0;
  LAST_WHY = kind == 1 ? "pull" : (kind == 2 ? "half pull" : (kind == 3 ? "pulled to the hooked target" : "yank"));
}""")
# a bolt OUT: flying past grapple.ropeLength / stuck past grapple.snapDistance = the rope snaps; stuck past grapple.anchorSeconds = it drops;
# its block broken (RESTING -> ACTIVE) = not stuck any more; a hooked mob: gone / too far / too long = over
M(grap, r"""
public static void outTick(@PKG@.GrappleState s, @ST@ st, @CB@ buf, long now) {
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, s.ref);
  if (s.hooked) {
    if (s.hook == null || !s.hook.isValid() || @PKG@.ArmoryTrav.dead(buf, s.hook)) { endIn(s, buf, st, "the hooked mob is gone", true); return; }
    @VEC@ hp = @PKG@.ArmoryTrav.posOf(buf, s.hook);
    if (p != null && hp != null && @PKG@.GrappleMath.dist(p.x, p.y, p.z, hp.x, hp.y, hp.z) > (double) @PKG@.ArmoryCfg.G_SNAP) {
      SNAPS = SNAPS + 1L;
      endIn(s, buf, st, "rope snapped", true);
      return;
    }
    if (now - s.stuckAt > (long) @PKG@.ArmoryCfg.G_ANCHOR * 1000L) { endIn(s, buf, st, "hook time", true); return; }
    s.ticks = s.ticks + 1;
    if ("always".equals(@PKG@.ArmoryCfg.G_ROPE) && p != null && hp != null && s.ticks % 4 == 1) rope(buf, p.x, p.y + 0.9, p.z, hp.x, hp.y + 0.9, hp.z);
    return;
  }
  if (s.bolt == null && s.stuck) {
    // FIX ROUND: the stuck bolt was taken by another mod - the anchor (where it stuck) holds until the anchor time / the snap distance
    if (now - s.stuckAt > (long) @PKG@.ArmoryCfg.G_ANCHOR * 1000L) { endIn(s, buf, st, "anchor time", true); return; }
    if (p != null && @PKG@.GrappleMath.dist(p.x, p.y + 0.9, p.z, s.tx, s.ty, s.tz) > (double) @PKG@.ArmoryCfg.G_SNAP) {
      SNAPS = SNAPS + 1L;
      endIn(s, buf, st, "rope snapped", true);
      return;
    }
    s.ticks = s.ticks + 1;
    if ("always".equals(@PKG@.ArmoryCfg.G_ROPE) && p != null && s.ticks % 4 == 1) rope(buf, p.x, p.y + 0.9, p.z, s.tx, s.ty, s.tz);
    return;
  }
  @SPPV@ sp = phys(buf, s.bolt);
  @VEC@ bp = null;
  if (sp != null) bp = @PKG@.ArmoryTrav.posOf(buf, s.bolt);
  if (sp == null || bp == null) { endIn(s, buf, st, "bolt gone", true); return; }
  @SPST@ bs = sp.getState();
  if (bs == @SPST@.RESTING) {
    if (!s.stuck) { s.stuck = true; s.stuckAt = now; }
    s.tx = bp.x;          // FIX ROUND: the anchor = where the bolt rests (kept if another mod takes the bolt)
    s.ty = bp.y;
    s.tz = bp.z;
  } else if (bs == @SPST@.INACTIVE) {
    endIn(s, buf, st, "bolt stopped", true);
    return;
  } else if (s.stuck) {
    s.stuck = false;
  }
  if (p == null) return;
  double d = @PKG@.GrappleMath.dist(p.x, p.y + 0.9, p.z, bp.x, bp.y, bp.z);
  if (s.stuck) {
    if (now - s.stuckAt > (long) @PKG@.ArmoryCfg.G_ANCHOR * 1000L) { endIn(s, buf, st, "anchor time", true); return; }
    if (d > (double) @PKG@.ArmoryCfg.G_SNAP) { SNAPS = SNAPS + 1L; endIn(s, buf, st, "rope snapped", true); return; }
  } else if (d > (double) @PKG@.ArmoryCfg.G_ROPE_LEN) {
    SNAPS = SNAPS + 1L;
    endIn(s, buf, st, "rope snapped", true);
    return;
  }
  s.ticks = s.ticks + 1;
  if ("always".equals(@PKG@.ArmoryCfg.G_ROPE) && s.ticks % 4 == 1) rope(buf, p.x, p.y + 0.9, p.z, bp.x, bp.y, bp.z);
}""")
# PULL (you): every tick (PULL_EVERY) a Set toward the target from the chest; arrival within stopDistance (+ half a hooked mob's width); the
# stall rule (no 0.1 block progress for 9 ticks, counted after the first 0.5 s = ping) = blocked; grapple.pullMaxSeconds = let go (momentum kept)
M(grap, r"""
public static void pullTick(@PKG@.GrappleState s, @ST@ st, @CB@ buf, long now) {
  s.ticks = s.ticks + 1;
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, s.ref);
  if (p == null) return;
  double stop = @PKG@.ArmoryCfg.G_STOP;
  if (s.kind == 3) {
    if (s.hook == null || !s.hook.isValid() || @PKG@.ArmoryTrav.dead(buf, s.hook)) { endIn(s, buf, st, "the hooked mob is gone", true); return; }
    @VEC@ hp = @PKG@.ArmoryTrav.posOf(buf, s.hook);
    if (hp != null) { s.tx = hp.x; s.ty = hp.y + 0.9; s.tz = hp.z; }
    stop = stop + @PKG@.ArmoryTrav.thickness(buf, s.hook) * 0.5;
  }
  double cx = p.x;
  double cy = p.y + 0.9;
  double cz = p.z;
  double d = @PKG@.GrappleMath.dist(cx, cy, cz, s.tx, s.ty, s.tz);
  if (d <= stop) { arrive(s, st, buf, p, true); return; }
  if (now - s.pullAt > Math.round(@PKG@.ArmoryCfg.G_PULL_MAX * 1000.0)) { endIn(s, buf, st, "pull time", true); return; }
  if (@PKG@.GrappleMath.progressed(s.best, d)) {
    s.best = d;
    s.stall = 0;
  } else if (now - s.pullAt > 500L) {
    s.stall = s.stall + 1;
    if (s.stall >= 9) { arrive(s, st, buf, p, false); return; }
  }
  if (PULL_EVERY > 1 && s.ticks % PULL_EVERY != 1) return;
  double[] v = @PKG@.GrappleMath.pullVector(cx, cy, cz, s.tx, s.ty, s.tz, @PKG@.ArmoryCfg.G_SPEED, @PKG@.ArmoryCfg.G_MAXDOWN, @PKG@.ArmoryCfg.G_EASE);
  if (setVel(buf, s.ref, v, false)) {
    s.vx = v[0];
    s.vy = v[1];
    s.vz = v[2];
  }
  if (!"off".equals(@PKG@.ArmoryCfg.G_ROPE) && s.ticks % 4 == 1) rope(buf, cx, cy, cz, s.tx, s.ty, s.tz);
}""")
# YANK (a small hooked mob, or a hooked player where the row allows it): its Velocity is Set toward you every tick until it is next to you
M(grap, r"""
public static void yankTick(@PKG@.GrappleState s, @ST@ st, @CB@ buf, long now) {
  s.ticks = s.ticks + 1;
  if (s.hook == null || !s.hook.isValid() || @PKG@.ArmoryTrav.dead(buf, s.hook)) { endIn(s, buf, st, "the hooked mob is gone", true); return; }
  @VEC@ p = @PKG@.ArmoryTrav.posOf(buf, s.ref);
  @VEC@ hp = @PKG@.ArmoryTrav.posOf(buf, s.hook);
  if (p == null || hp == null) return;
  double stop = @PKG@.ArmoryCfg.G_STOP + @PKG@.ArmoryTrav.thickness(buf, s.hook) * 0.5 + 0.3;
  double d = @PKG@.GrappleMath.dist(hp.x, hp.y, hp.z, p.x, p.y, p.z);
  if (d <= stop) { ARRIVALS = ARRIVALS + 1L; yankStop(s, buf); endIn(s, buf, st, "yanked", true); return; }
  if (now - s.pullAt > Math.round(@PKG@.ArmoryCfg.G_PULL_MAX * 1000.0)) { yankStop(s, buf); endIn(s, buf, st, "yank time", true); return; }
  // FIX ROUND (critic: a mob behind a fence / pen wall): the pull's stall rule - no 0.1 block progress for 9 ticks after 0.5 s = over
  if (@PKG@.GrappleMath.progressed(s.best, d)) {
    s.best = d;
    s.stall = 0;
  } else if (now - s.pullAt > 500L) {
    s.stall = s.stall + 1;
    if (s.stall >= 9) { yankStop(s, buf); endIn(s, buf, st, "yank blocked", true); return; }
  }
  if (PULL_EVERY > 1 && s.ticks % PULL_EVERY != 1) return;
  double[] v = @PKG@.GrappleMath.pullVector(hp.x, hp.y, hp.z, p.x, p.y, p.z, @PKG@.ArmoryCfg.G_SPEED, @PKG@.ArmoryCfg.G_MAXDOWN, @PKG@.ArmoryCfg.G_EASE);
  if (setVel(buf, s.hook, v, !s.hookPlayer)) {
    s.vx = v[0];
    s.vy = v[1];
    s.vz = v[2];
  }
  if (!"off".equals(@PKG@.ArmoryCfg.G_ROPE) && s.ticks % 4 == 1) rope(buf, p.x, p.y + 0.9, p.z, hp.x, hp.y + 0.9, hp.z);
}""")
# FIX ROUND (critic: a disconnect strands the record + its Store): every SWEEP_EVERY player ticks, records whose player body is gone
# (disconnect, island unload) are dropped (their bolt removed when it is in this store), and spent GRACE / LASTEND entries are pruned
M(grap, r"""
public static void sweep(@ST@ st, @CB@ buf, long now) {
  java.util.Iterator it = STATES.values().iterator();
  while (it.hasNext()) {
    @PKG@.GrappleState s = (@PKG@.GrappleState) it.next();
    boolean gone = false;
    try { gone = s.ref == null || !s.ref.isValid(); } catch (Throwable t) { gone = true; }
    if (!gone) continue;
    it.remove();
    SWEPT = SWEPT + 1L;
    try { if (s.st == st && s.bolt != null && s.bolt.isValid()) buf.removeEntity(s.bolt, @REMR@.REMOVE); } catch (Throwable t1) { }
  }
  java.util.Iterator g = GRACE.entrySet().iterator();
  while (g.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) g.next();
    Object v = e.getValue();
    if (!(v instanceof Long) || ((Long) v).longValue() < now) g.remove();
  }
  long keep = Math.round(@PKG@.ArmoryCfg.G_CD * 1000.0) + 1000L;
  java.util.Iterator l = LASTEND.entrySet().iterator();
  while (l.hasNext()) {
    java.util.Map.Entry e2 = (java.util.Map.Entry) l.next();
    Object v2 = e2.getValue();
    if (!(v2 instanceof Long) || now - ((Long) v2).longValue() > keep) l.remove();
  }
}""")
# TravTick -> once per player per world tick: no record = clear a left-over OUT / CLICK effect (a restart, a relog); else the checks (world,
# body, death, mount, swap off the crossbow), the CLICK effect consumed (one click per tick), the OUT effect kept, the mode's tick
M(grap, r"""
public static void tickPlayer(@REF@ r, @ST@ st, @CB@ buf) {
  if (r == null) return;
  SWEEP_N = SWEEP_N + 1;
  if (SWEEP_N >= SWEEP_EVERY) {
    SWEEP_N = 0;
    try { sweep(st, buf, System.currentTimeMillis()); } catch (Throwable ts) { warn("sweep", "the grapple sweep failed (" + ts + ")"); }
  }
  java.util.UUID u = uuidOf(buf, r);
  if (u == null) return;
  @PKG@.GrappleState s = (@PKG@.GrappleState) STATES.get(u);
  if (s == null) {
    @ECC@ c0 = ecc(buf, r);
    if (c0 == null) return;
    int oi = outI();
    int ci = clickI();
    if (hasFx(c0, oi)) { c0.removeEffect(r, oi, buf); STALE = STALE + 1L; }
    if (hasFx(c0, ci)) c0.removeEffect(r, ci, buf);
    return;
  }
  long now = System.currentTimeMillis();
  if (s.st != st) {
    STATES.remove(u, s);
    LASTEND.put(u, Long.valueOf(now));
    LAST_WHY = "left the world";
    ENDS = ENDS + 1L;
    removeFx(buf, r, OUT);
    removeFx(buf, r, CLICK);
    return;
  }
  if (s.ref == null || !s.ref.equals(r)) { endIn(s, buf, st, "a new body", true); removeFx(buf, r, OUT); removeFx(buf, r, CLICK); return; }
  if (@PKG@.ArmoryTrav.dead(buf, r)) { endIn(s, buf, st, "died", true); return; }
  if (mounted(buf, r)) { endIn(s, buf, st, "mounted", true); return; }
  if (!same(s.item, hand(buf, r, u))) { endIn(s, buf, st, "swapped off the crossbow", true); return; }
  @ECC@ c = ecc(buf, r);
  int ci2 = clickI();
  if (hasFx(c, ci2)) {
    c.removeEffect(r, ci2, buf);
    CLICKS = CLICKS + 1L;
    click(s, st, buf, now);
    if (STATES.get(u) != s) return;
  }
  if (c != null && !hasFx(c, outI())) addFx(buf, r, OUT);
  if (s.mode == 1) outTick(s, st, buf, now);
  else if (s.mode == 2) pullTick(s, st, buf, now);
  else if (s.mode == 3) yankTick(s, st, buf, now);
}""")
# GrappleBoltSys.onEntityRemove: our bolt removed by the engine (despawn, a broken block's drop) while it is out and not hooked = over
M(grap, r"""
public static void boltGone(@REF@ bolt, @ST@ st, @CB@ buf) {
  if (bolt == null || STATES.isEmpty()) return;
  java.util.Iterator it = STATES.values().iterator();
  while (it.hasNext()) {
    @PKG@.GrappleState s = (@PKG@.GrappleState) it.next();
    if (s.mode == 1 && !s.hooked && s.bolt != null && s.bolt.equals(bolt)) {
      s.bolt = null;
      if (s.stuck) { LAST_WHY = "bolt taken - the anchor holds"; return; }      // FIX ROUND: More Arrows' magnet takes resting projectiles
      endIn(s, buf, st, "bolt gone", false);
      return;
    }
  }
}""")
# GrappleFallSys: FALL damage is cancelled while you are pulled and within grapple.landGrace after an ARRIVAL (never after a release / snap)
M(grap, r"""
public static boolean fallSafe(java.util.UUID u, long now) {
  if (u == null) return false;
  @PKG@.GrappleState s = (@PKG@.GrappleState) STATES.get(u);
  if (s != null && s.mode == 2 && s.ref != null && s.ref.isValid()) return true;      // FIX ROUND: a stranded record (disconnect) gives no grace
  Object g = GRACE.get(u);
  return g instanceof Long && now <= ((Long) g).longValue();
}""")

# ---- the two grapple systems (one registerSystem per class)
F(gbolt, "public @QRY@ query;")
C(gbolt, "public GrappleBoltSys() { super(); this.query = null; }")
M(gbolt, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @PRJC@.getComponentType(), (@QRY@) @SPPV@.getComponentType() });
  return this.query;
}""")
M(gbolt, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (reason != @ADDR@.SPAWN) return;
    Object mc = buf.getComponent(ref, @MODC@.getComponentType());
    if (!(mc instanceof @MODC@)) return;
    @MDL@ m = ((@MODC@) mc).getModel();
    if (m == null || !@PKG@.Grapple.BOLT.equals(m.getModelAssetId())) return;
    Object sp = buf.getComponent(ref, @SPPV@.getComponentType());
    if (sp instanceof @SPPV@) @PKG@.Grapple.onShot(ref, (@SPPV@) sp, st, buf);
  } catch (Throwable t) { @PKG@.Grapple.warn("added:" + t.getClass().getName(), "grapple shot hook failed (" + t + ")"); }
}""")
M(gbolt, r"""
public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ st, @CB@ buf) {
  try { @PKG@.Grapple.boltGone(ref, st, buf); }
  catch (Throwable t) { @PKG@.Grapple.warn("removed:" + t.getClass().getName(), "grapple bolt remove hook failed (" + t + ")"); }
}""")
C(gfall, "public GrappleFallSys() { super(); }")
M(gfall, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(gfall, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(gfall, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@) || chunk == null) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @DCS@ c = d.getCause();
    if (c == null) return;
    Object cid = c.getId();
    if (c != @DCS@.FALL && !"Fall".equalsIgnoreCase(String.valueOf(cid))) return;
    Object po = buf.getComponent(chunk.getReferenceTo(idx), @PR@.getComponentType());
    if (!(po instanceof @PR@)) return;
    if (@PKG@.Grapple.fallSafe(((@PR@) po).getUuid(), System.currentTimeMillis())) {
      d.setCancelled(true);
      @PKG@.Grapple.FALLS = @PKG@.Grapple.FALLS + 1L;
    }
  } catch (Throwable t) { @PKG@.Grapple.warn("fall:" + t.getClass().getName(), "the grapple fall filter failed (" + t + ")"); }
}""")

'''
rep('''# ---- the three systems (one registerSystem per class)
''', G_JAVA + '''# ---- the three systems (one registerSystem per class)
''')
rep('''public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @PKG@.TravWorld tw = @PKG@.TravWorld.of(store);''', '''public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  if (chunk != null) {          // 0.1.2: the crossbow grapple, per player (world thread)
    try { @PKG@.Grapple.tickPlayer(chunk.getReferenceTo(idx), store, cb); }
    catch (Throwable tg) { @PKG@.Grapple.warn("tick:" + tg.getClass().getName(), "grapple tick failed (" + tg + ")"); }
  }
  try {
    @PKG@.TravWorld tw = @PKG@.TravWorld.of(store);''')

# ================================================================================================ plugin: systems, bridge, migration, log, shutdown
rep('''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory", "armory:trav"]''',
    '''BRIDGE_KEYS = ["armory:wands", "armory:staffs", "armory:quick", "armory:fn:info", "armory:check", "gear:loot:add:SkyyArmory", "armory:trav",
               "armory:grapple"]''')
rep('''  catch (Throwable t7) { @PKG@.ArmoryLog.warn("TravTick could not be registered: " + t7 + " - no trail damage, no heal orb, no quick shot range"); }''',
    '''  catch (Throwable t7) { @PKG@.ArmoryLog.warn("TravTick could not be registered: " + t7 + " - no trail damage, no heal orb, no quick shot range, no grapple pull"); }
  // 0.1.2 grapple: one registerSystem per class
  try { getEntityStoreRegistry().registerSystem(new @PKG@.GrappleBoltSys()); @PKG@.Grapple.SYS_BOLT = true; }
  catch (Throwable t8) { @PKG@.ArmoryLog.warn("GrappleBoltSys could not be registered: " + t8 + " - crossbow grapple bolts fly but never pull"); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.GrappleFallSys()); @PKG@.Grapple.SYS_FALL = true; }
  catch (Throwable t9) { @PKG@.ArmoryLog.warn("GrappleFallSys could not be registered: " + t9 + " - grapple landings take normal fall damage"); }''')
rep('''  b.put("armory:trav", @PKG@.ArmoryCfg.TRAV_TEXT);
}""")''', '''  b.put("armory:trav", @PKG@.ArmoryCfg.TRAV_TEXT);
  b.put("armory:grapple", @PKG@.ArmoryCfg.GRAPPLE_TEXT);
}""")''')
rep('''  @PKG@.ArmoryCfg.FILE = dir.resolve("config.properties");
  @PKG@.ArmoryCfg.load();''', '''  @PKG@.ArmoryCfg.FILE = dir.resolve("config.properties");
  String m12 = @PKG@.ArmoryCfg.migrate012();          // 0.1.2: a trav.staminaCap line still at 10 becomes 5 ONCE (History copy first), before the loader
  @PKG@.ArmoryCfg.load();''')
rep('''  @PKG@.TravWorld.ALL.clear();
  systems();''', '''  @PKG@.TravWorld.ALL.clear();
  @PKG@.Grapple.STATES.clear();
  @PKG@.Grapple.GRACE.clear();
  @PKG@.Grapple.LASTEND.clear();
  systems();''')
rep('''  @PKG@.ArmoryLog.info("@VERSION@ magic traversals: " + @PKG@.ArmoryCfg.TRAV_TEXT + " (systems: hook " + @PKG@.ArmoryTrav.SYS_TRAV + ", hits " + @PKG@.ArmoryTrav.SYS_HIT + ", tick " + @PKG@.ArmoryTrav.SYS_TICK + ")");''',
    '''  @PKG@.ArmoryLog.info("@VERSION@ magic traversals: " + @PKG@.ArmoryCfg.TRAV_TEXT + " (systems: hook " + @PKG@.ArmoryTrav.SYS_TRAV + ", hits " + @PKG@.ArmoryTrav.SYS_HIT + ", tick " + @PKG@.ArmoryTrav.SYS_TICK + ")");
  @PKG@.ArmoryLog.info("@VERSION@ crossbow grapple: " + @PKG@.ArmoryCfg.GRAPPLE_TEXT + " (systems: bolt " + @PKG@.Grapple.SYS_BOLT + ", fall " + @PKG@.Grapple.SYS_FALL + ")" + (m12.length() > 0 ? "; " + m12 : ""));''')
rep('''  unpublish();
  @PKG@.TravWorld.ALL.clear();''', '''  unpublish();
  @PKG@.TravWorld.ALL.clear();
  @PKG@.Grapple.STATES.clear();
  @PKG@.Grapple.GRACE.clear();''')
rep('''man = B.manifest(MOD, VERSION, "SkyWynn armory: 7 metal Priest wands (Copper to Onyxium, tap = blue quick shot that pierces, hold = hop "
                 "back + burst + heal orb) + the Wood wand tap, and the Mage staff ladder (tap = quick shot, hold = blink + light trail). "''',
    '''man = B.manifest(MOD, VERSION, "SkyWynn armory: 7 metal Priest wands (Copper to Onyxium, tap = blue quick shot that pierces, hold = hop "
                 "back + burst + heal orb) + the Wood wand tap, and the Mage staff ladder (tap = quick shot, hold = blink + light trail). "
                 "Crossbow right click = the grapple bolt (shoot, pull, let go; hooks mobs). "''')
rep('''    HOP_MODE, SCAN_MODE, ORB_LOOK, STAFF_STAMINA, len(S_BLINK), MARKER, PS_TRAIL, len(TRAIL_FILES), len(CFG_NEW)))''',
    '''    HOP_MODE, SCAN_MODE, ORB_LOOK, STAFF_STAMINA, len(S_BLINK), MARKER, PS_TRAIL, len(TRAIL_FILES), len(CFG_NEW)))
print("0.1.2 grapple: right click %s, click mode %s, pull every %d tick(s), rope %s (%s), bolt %d / %d, %d interactions + %s, %d files, %d rows; "
      "traversal Stamina cap default 5 (one-time update marker %r)" % (XBOW_RIGHT, CLICK_MODE, PULL_EVERY, ROPE_MODE, ROPE_COLOR, BOLT_FORCE, BOLT_GRAVITY,
      len(GINTS), ("the root override " + XROOT) if XROOT_JSON else "no root override", len(G_FILES), len(CFG_GRAPPLE), M12_MARK_ID))''')

assert s.count("registerSystem(") == SYS0 + 2, "0.1.2 registers exactly 2 more systems"
for _bad in ("stamCap=10", "\"trav.staminaCap=10\"", 'intOf(c.getProperty("trav.staminaCap"), 10'):
    assert _bad not in s, _bad
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))

# ================================================================================================ the harness: 0.1.1's checks (patched for 0.1.2) + the new sections
HARNESS_P9 = r'''# ============================================================================================================ P9. 0.1.2 grapple assets (spec 5 T1)
XROOT = "Root_Weapon_Crossbow_Secondary_Guard"
G_GRAPPLE, G_CLICKSTEP, G_SHOOT = "SkyyArmory_Grapple", "SkyyArmory_Grapple_Click_Step", "SkyyArmory_Grapple_Shoot"
G_HIT, G_STICK, G_GONE = "SkyyArmory_Grapple_Hit", "SkyyArmory_Grapple_Stick", "SkyyArmory_Grapple_Despawn"
G_OUT, G_CLICK, G_BOLT = "SkyyArmory_Grapple_Out", "SkyyArmory_Grapple_Click", "SkyyArmory_Grapple_Bolt"
G_INTS = [G_GRAPPLE, G_CLICKSTEP, G_SHOOT, G_HIT, G_STICK, G_GONE]
J_PCFG = by_dir("Server/ProjectileConfigs/")
J_EFX = by_dir("Server/Entity/Effects/")


def az_json_by_base(prefix, base):
    hits = [n for n in AZN if n.startswith(prefix) and n.endswith("/" + base + ".json")]
    return json.loads(AZ.read(hits[0]).decode("utf-8-sig")) if len(hits) == 1 else None


check(sorted(J_PCFG) == [G_BOLT] and sorted(J_EFX) == sorted([G_OUT, G_CLICK]) and all(i in JINT for i in G_INTS) and XROOT in JROOT,
      "P9 (T1): the grapple files - 6 interactions, the root override, 1 projectile config, 2 effects: %s %s" % (sorted(J_PCFG), sorted(J_EFX)))
check(JROOT[XROOT] == {"RequireNewClick": True, "Cooldown": {"Cooldown": 0.25}, "Rules": {"Interrupting": ["Primary"]}, "Interactions": [G_GRAPPLE],
                       "Tags": {"Attack": ["Melee"]}}
      and J_ROOTS[XROOT] == "Server/Item/RootInteractions/Weapons/Crossbow/%s.json" % XROOT,
      "P9 (2.1, Skyy: replace the guard): the crossbow right click root = our grapple chain only (RequireNewClick + the vanilla Rules + the vanilla Tags "
      "(FIX ROUND), cooldown 0.25 s), at the vanilla path")
check(JROOT[XROOT]["Tags"] == aj("root", XROOT)["Tags"], "P9 (FIX ROUND): the override keeps the vanilla root's Tags (Attack)")
_vr = aj("root", XROOT)
check(_vr["RequireNewClick"] is True and _vr["Rules"] == {"Interrupting": ["Primary"]} and _vr["Interactions"][0]["DefaultValue"]["Interactions"] == ["Weapon_Crossbow_Secondary_Guard"],
      "P9: the vanilla root it replaces is the guard (same click rules kept)")
_tpl = aj("item", "Template_Weapon_Crossbow")
check(_tpl["Interactions"] == {"SwapFrom": "Root_Weapon_Crossbow_Swap_From", "Primary": "Root_Weapon_Crossbow_Primary_Signature", "Secondary": XROOT,
                               "Ability1": "Root_Weapon_Crossbow_Signature_BigArrow", "Ability3": "Root_Common_StatAmmoReload_Entry"}
      and not [n for n in JN if "Crossbow" in n and n.startswith("Server/Item/Items/")],
      "P9 (2.1): every crossbow reaches the root through the vanilla template (no item override shipped); left click / reload / swap stay vanilla")
check(JINT[G_GRAPPLE] == {"Type": "EffectCondition", "EntityEffectIds": [G_OUT], "Match": "All", "Next": G_CLICKSTEP, "Failed": G_SHOOT}
      and JINT[G_CLICKSTEP] == {"Type": "ApplyEffect", "EffectId": G_CLICK},
      "P9 (2.1): the chain - OUT effect on = apply the CLICK effect (clicks 2 / 3), else shoot")
_sh = JINT[G_SHOOT]
check(_sh["Type"] == "Projectile" and _sh["Config"] == G_BOLT and _sh["Effects"] == {"ItemAnimationId": "Shoot", "ClearAnimationOnFinish": True}
      and "Shoot" in aresolve("anim", "Crossbow")["Animations"], "P9: the shot = the game's Projectile interaction on our config, the crossbow's Shoot animation")
_pc = J[J_PCFG[G_BOLT]]
_pb = az_json_by_base("Server/ProjectileConfigs/", "Projectile_Config_Arrow_Base")
check(_pc["LaunchForce"] == 60 and _pc["Physics"]["Gravity"] == 6 and _pc["Physics"]["TerminalVelocityAir"] == 70 and _pc["Physics"]["SticksVertically"] is True
      and _pc["Physics"]["Bounciness"] == 0.0 and "Parent" not in _pc and _pc["Model"] == G_BOLT and _pb is not None
      and _pc["SpawnOffset"] == _pb["SpawnOffset"] and _pc["SpawnRotationOffset"] == _pb["SpawnRotationOffset"]
      and _pc["Interactions"] == {"ProjectileHit": {"Interactions": [G_HIT, G_GONE]}, "ProjectileMiss": {"Interactions": [G_STICK]}},
      "P9 (2.2): the bolt config = Projectile_Config_Arrow_Base resolved + LaunchForce 60 / Gravity 6 / terminal 70, sticks; miss = the sound only (no despawn: it rests), hit = sound + despawn")
_gtxt = json.dumps([JINT[i] for i in G_INTS] + [JROOT[XROOT], _pc] + [J[J_EFX[e]] for e in J_EFX])
check(not [w for w in ("DamageEntity", "Block_Break", "Common_Projectile_Despawn", '"Ammo"', "ModifyInventory", "SwapFrom", "StatModifiers", "Costs") if w in _gtxt],
      "P9 (4): no damage, no block breaking, no Ammo / inventory / stat change anywhere in the grapple chain (loaded bolts + reload untouched; costs are server-side)")
check(JINT[G_GONE] == aj("int", "Common_Projectile_Despawn") == {"Type": "RemoveEntity", "Entity": "User"} and JINT[G_STICK]["Effects"]["WorldSoundEventId"] == "SFX_Arrow_FullCharge_Miss"
      and JINT[G_HIT]["Effects"]["WorldSoundEventId"] == "SFX_Arrow_FullCharge_Hit", "P9: our despawn = the vanilla one (own id); the impact sounds are the crossbow's")
check(J[J_EFX[G_OUT]] == {"Infinite": True} and J[J_EFX[G_CLICK]] == {"Duration": 0.5, "OverlapBehavior": "Overwrite"},
      "P9 (2.1): OUT = Infinite (no icon), CLICK = 0.5 s Overwrite (consumed by the server the tick it sees it)")
_gm = J[J_MODELS[G_BOLT]]
_vam = aj("model", "Arrow_Crude")
_gm2 = copy.deepcopy(_gm)
for _t in _gm2["Trails"]:
    _t["TrailId"] = "Arrow"
check(_gm2 == _vam and [t["TrailId"] for t in _gm["Trails"]] == ["SkyyArmory_Rope_Trail"] * 2, "P9 (2.4): the bolt model = Arrow_Crude with the rope trail")
_rt, _vt = J[J_TRAILS["SkyyArmory_Rope_Trail"]], aj("trail", "Arrow")
check(_rt["LifeSpan"] == 40 and _rt["RenderMode"] == "BlendLinear" and _rt["Start"]["Color"] == "#8a6a45e0" and _rt["End"]["Color"] == "#8a6a4500"
      and _rt["TexturePath"] == _vt["TexturePath"], "P9 (2.4): the rope trail = the vanilla Arrow trail, rope brown, twice as long")
_rd = J[J_PSYS["SkyyArmory_Rope_Dot"]]
_hues = []
for sp_ in _rd["Spawners"]:
    for c_ in re.findall(r'"Color": "(?:rgba\()?#([0-9a-fA-F]{6})', json.dumps(J[J_PSP[sp_["SpawnerId"]]])):
        import colorsys as _cs2
        _hues.append(round(_cs2.rgb_to_hsv(*(int(c_[i:i + 2], 16) / 255.0 for i in (0, 2, 4)))[0] * 360.0))
check(len(_rd["Spawners"]) == 2 and _hues and all(25 <= h_ <= 40 for h_ in _hues), "P9 (2.4): the rope dots = the blink light's 2 spawners in rope brown (hue %s)" % sorted(set(_hues)))
check(all(k.startswith("SkyyArmory_") for k in list(J_PCFG) + list(J_EFX) + G_INTS) and all(az_json_by_base("Server/", k) is None for k in [G_BOLT, G_OUT, G_CLICK] + G_INTS),
      "P9: every new id starts with SkyyArmory_ and none exists in Assets.zip")
print("P9. 0.1.2 grapple assets: the root override, the 6-step chain, the bolt config (60 / 6, rests, no damage), OUT / CLICK effects, rope trail + dots")
'''

HARNESS_Q = r'''    # ---------------- Q. 0.1.2 THE CROSSBOW GRAPPLE - every new path EXECUTED on real engine objects (spec 5 T2-T5 + Skyy's answers)
    ACfg.useDefaults()
    GM, GSt, GR, GImp = (JClass(PKG + n_) for n_ in ("GrappleMath", "GrappleState", "Grapple", "GrappleImpact"))
    GBS, GFS = JClass(PKG + "GrappleBoltSys"), JClass(PKG + "GrappleFallSys")
    r6 = lambda a: [round(float(x), 4) for x in a]
    # --- Q1. GrappleMath (pure, spec T3)
    check(r6(GM.halfTarget(0.0, 1.0, 0.0, 20.0, 1.0, 0.0, 50)) == [10.0, 1.0, 0.0] and r6(GM.halfTarget(0.0, 0.0, 0.0, 20.0, 0.0, 0.0, 10)) == [2.0, 0.0, 0.0]
          and r6(GM.halfTarget(0.0, 0.0, 0.0, 20.0, 0.0, 0.0, 150)) == [20.0, 0.0, 0.0], "Q1 (T3): half target - bolt 20 ahead -> 10 (Skyy: half way), 10% -> 2, clamped at 100%")
    check(r6(GM.pullVector(0.0, 0.0, 0.0, 0.0, 20.0, 0.0, 24.0, 18.0, 0.0)) == [0.0, 24.0, 0.0] and r6(GM.pullVector(0.0, 0.0, 0.0, 0.0, -20.0, 0.0, 24.0, 18.0, 0.0)) == [0.0, -18.0, 0.0]
          and r6(GM.pullVector(0.0, 0.0, 0.0, 5.0, -20.0, 0.0, 24.0, 18.0, 0.0)) == [5.8209, -18.0, 0.0] and r6(GM.pullVector(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 24.0, 18.0, 0.0)) == [0.0, 0.0, 0.0]
          and r6(GM.pullVector(0.0, 0.0, 0.0, 0.0, 20.0, 0.0, 24.0, 18.0, 4.0)) == [0.0, 24.0, 0.0],
          "Q1 (T3): pull vector - 24 b/s along the rope, the downward part clamped to 18 (under the fall-damage 21), nothing at the target")
    check(r6(GM.releaseVector(20.0, 5.0, 0.0, 100, 2.0)) == [20.0, 7.0, 0.0] and r6(GM.releaseVector(20.0, 5.0, 0.0, 50, 2.0)) == [10.0, 4.5, 0.0]
          and r6(GM.releaseVector(20.0, 5.0, 0.0, 0, 0.0)) == [0.0, 0.0, 0.0], "Q1 (T3): release = the pull speed x keep %% + lift (100%% + 2 up)")
    check(r6(GM.arriveVector(8.0, 4.0, 0.0, True, 6.0)) == [2.0, 6.0, 0.0] and r6(GM.arriveVector(8.0, 4.0, 0.0, False, 6.0)) == [2.0, 1.0, 0.0]
          and bool(GM.above(65.0, 64.0)) and not bool(GM.above(64.4, 64.0)), "Q1: arrival - a bolt above the feet = hop 6 up, else a soft stop (x 0.25)")
    check(int(GM.ropeDots(20.0, 1.5)) == 13 and int(GM.ropeDots(0.0, 1.5)) == 0 and int(GM.ropeDots(500.0, 0.5)) == 40 and bool(GM.progressed(10.0, 9.85))
          and not bool(GM.progressed(10.0, 9.95)), "Q1 (T3): a 20-block rope = 13 dots (spec 2.4), capped 40; progress = more than 0.1 block closer")
    check(float(GM.easeSpeed(10.0, 24.0, 4.0)) == 24.0 and float(GM.easeSpeed(3.0, 24.0, 4.0)) == 12.0 and float(GM.easeSpeed(0.5, 24.0, 4.0)) == 4.0
          and float(GM.easeSpeed(3.0, 24.0, 0.0)) == 24.0 and float(GM.easeSpeed(0.5, 3.0, 4.0)) == 3.0
          and r6(GM.pullVector(0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 24.0, 18.0, 4.0)) == [12.0, 0.0, 0.0] and r6(GM.pullVector(0.0, 0.0, 0.0, 0.0, -2.0, 0.0, 24.0, 18.0, 4.0)) == [0.0, -8.0, 0.0],
          "Q1 (FIX ROUND, critic: ping overshoot): the ease - 10 blocks left = full 24, 3 left = 12 (4 x 3), 0.5 left = the 4 b/s floor, ease 0 = off, never above the speed row")
    bw = "Boss,Guardian,Duke,Dragon"
    check(bool(GM.bossName("Goblin_Duke", bw)) and bool(GM.bossName("golem_guardian", bw)) and bool(GM.bossName("Dragon_Frost", bw)) and not bool(GM.bossName("Trork_Warrior", bw))
          and not bool(GM.bossName(None, bw)) and not bool(GM.bossName("Goblin_Duke", "")), "Q1: the boss words match role names (any case)")
    hk = lambda *a: int(GM.hookKind(*a))
    check(hk(0.6, 1.8, 0.6, 1.0, False, False, False, False, False) == 1 and hk(0.7, 0.9, 0.7, 1.0, False, False, False, False, False) == 1
          and hk(1.6, 1.7, 1.6, 1.0, False, False, False, False, False) == 2 and hk(1.4, 2.6, 1.4, 1.0, False, False, False, False, False) == 2
          and hk(0.6, 1.8, 0.6, 1.0, True, False, False, False, False) == 2 and hk(0.6, 1.8, 0.6, 0.0, False, False, False, False, False) == 2
          and hk(0.0, 0.0, 0.0, 1.0, False, False, False, False, False) == 2,
          "Q1 (Skyy: Harpoon-style): a skeleton (0.65) / chicken (0.44) is YANKED, a cow (4.4) / Yeti (5.1) pulls YOU, a boss never yanked, size row 0 = never")
    check(hk(0.65, 1.85, 0.65, 1.0, False, True, False, True, False) == 2 and hk(0.65, 1.85, 0.65, 1.0, False, True, True, True, False) == 1
          and hk(0.65, 1.85, 0.65, 1.0, False, True, True, True, True) == 2 and hk(0.65, 1.85, 0.65, 1.0, False, True, True, False, False) == 2,
          "Q1 (Skyy: PvP): a hooked player is never yanked by default; with the row on only where PvP is on and not your party")

    # --- Q0. the stand-ins the grapple adds (ProjectileModule's component types, ModelComponent, the effect store with our 2 effects, the bolt config)
    PMODc = JClass("com.hypixel.hytale.server.core.modules.projectile.ProjectileModule")
    PRJCc = JClass("com.hypixel.hytale.server.core.modules.projectile.component.Projectile")
    SPPc = JClass("com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsProvider")
    SPST = JClass("com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsProvider$STATE")
    MODCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.ModelComponent")
    MDLx = JClass("com.hypixel.hytale.server.core.asset.type.model.config.Model")
    BOXc = JClass("com.hypixel.hytale.math.shape.Box")
    V3Ic = JClass("org.joml.Vector3i")
    ENTS = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    pmod = U.allocateInstance(PMODc.class_)
    setf(pmod, PMODc, "projectileComponentType", reg_.registerComponent(PRJCc.class_, "IsProjectile", jfield(PRJCc, "CODEC").get(None)))
    setf(pmod, PMODc, "standardPhysicsProviderComponentType", reg_.registerComponent(SPPc.class_, Sup(lambda: None)))
    jfield(PMODc, "instance").set(None, pmod)
    setf(em, EMc, gfield(EMN, "getModelComponentType"), reg_.registerComponent(MODCc.class_, Sup(lambda: None)))
    check(PRJCc.getComponentType() is not None and SPPc.getComponentType() is not None and MODCc.getComponentType() is not None,
          "Q0: Projectile / StandardPhysicsProvider / ModelComponent types registered like ProjectileModule / EntityModule do")
    load(MDLc, [DEC[("model", G_BOLT)]], PACK)          # the bolt config names its model
    gdec = {}
    gbad = []
    for k_, c_, d_ in [(G_OUT, EFXc, J[J_EFX[G_OUT]]), (G_CLICK, EFXc, J[J_EFX[G_CLICK]]), (G_BOLT, PCFGc, J[J_PCFG[G_BOLT]])]:
        o_, why_ = dec(c_, k_, json.dumps(d_))
        if o_ is None or why_:
            gbad.append("%s: %s" % (k_, why_))
        else:
            gdec[k_] = o_
    keep_pl = HashMap(pbu)            # a store load sends its update packet to every online player: none online while loading (the stand-ins have no connection)
    pbu.clear()
    lf_ = [load(EFXc, [gdec[G_OUT], gdec[G_CLICK]], PACK) if not gbad else None, load(PCFGc, [gdec[G_BOLT]], PACK) if not gbad else None]
    pbu.putAll(keep_pl)
    check(not gbad and all(x_ is not False for x_ in lf_), "Q0 (T1): the 2 effects + the bolt config decode through the engine codecs (no unknown key) and load: %s %s" % (gbad, lf_))
    eo, ec_, pcf = gdec.get(G_OUT), gdec.get(G_CLICK), gdec.get(G_BOLT)
    check(eo is not None and bool(eo.isInfinite()) and ec_ is not None and abs(float(ec_.getDuration()) - 0.5) < 1e-6 and str(ec_.getOverlapBehavior()).upper() == "OVERWRITE"
          and int(EFXc.getAssetMap().getIndex(G_OUT)) >= 0 and int(GR.fxIndex(G_CLICK)) >= 0 and int(GR.fxIndex("No_Such_Effect_ZZ")) < 0,
          "Q0: the decoded OUT effect is Infinite, CLICK 0.5 s Overwrite; both have an index in the real effect store: %r" % (
              None if eo is None else (bool(eo.isInfinite()), float(ec_.getDuration()), str(ec_.getOverlapBehavior()), int(EFXc.getAssetMap().getIndex(G_OUT)),
                                       int(GR.fxIndex(G_CLICK)), int(GR.fxIndex("No_Such_Effect_ZZ"))),))
    spc = None if pcf is None else pcf.getPhysicsConfig()
    ikeys = [] if pcf is None else sorted(str(k_) for k_ in pcf.getInteractions().keySet())
    check(pcf is not None and abs(float(pcf.getLaunchForce()) - 60.0) < 1e-9 and str(spc.getClass().getSimpleName()) == "StandardPhysicsConfig"
          and abs(float(spc.getGravity()) - 6.0) < 1e-9 and bool(spc.isSticksVertically()) and ikeys == ["ProjectileHit", "ProjectileMiss"],
          "Q0 (2.2): the decoded bolt config - launch force 60, StandardPhysicsConfig gravity 6, sticks vertically, ProjectileHit + ProjectileMiss chains: %s" % ikeys)
    GR.HAND = HashMap()
    XB = "Weapon_Crossbow_Iron"
    gu, gr_, gpr, gm = player(40, 0.5, 64.0, 0.5)
    put(gr_, ECCc.getComponentType(), ECCc())

    @JImplements("java.util.function.Function")
    class GMembers:
        @JOverride
        def apply(self, o): return JArray(JObject)([str(pu)]) if str(o) == str(gu) else JArray(JObject)([])
    br.put("party:fn:members", GMembers())
    GR.HAND.put(gu, XB)
    SDR = int(ESTc.getAssetMap().getIndex("StaminaRegenDelay"))
    nextb = [7000]

    def bolt(x, y, z, creator=None, model=G_BOLT, fake=None):
        nextb[0] += 1
        r_ = REFc(tst, nextb[0])
        sp_ = SPPc(BBXc(BOXc(-0.075, -0.075, -0.075, 0.075, 0.075, 0.075)), creator if creator is not None else gu, spc, V3(0.0, 0.0, 0.0), False)
        if fake is not None:
            sp_.setImpactConsumer(fake)
        put(r_, SPPc.getComponentType(), sp_)
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        mdl_ = U.allocateInstance(MDLx.class_)
        setf(mdl_, MDLx, gfield("com.hypixel.hytale.server.core.asset.type.model.config.Model", "getModelAssetId"), model)
        put(r_, MODCc.getComponentType(), MODCc(mdl_))
        put(r_, PRJCc.getComponentType(), PRJCc.INSTANCE)
        return r_, sp_

    @JImplements("com.hypixel.hytale.server.core.modules.projectile.config.ImpactConsumer")
    class FakeImpact:
        def __init__(self): self.calls = []
        @JOverride
        def onImpact(self, p, pos, blk, hit, name, buf): self.calls.append((p, None if hit is None else int(hit.getIndex())))
    gsys = GBS()

    def shoot(**kw):
        b_, sp_ = bolt(kw.get("x", 20.5), kw.get("y", 64.9), kw.get("z", 0.5), creator=kw.get("creator"), model=kw.get("model", G_BOLT), fake=kw.get("fake"))
        gsys.onEntityAdded(b_, kw.get("reason", ADDR.SPAWN), tst, tbuf)
        return b_, sp_

    def gstate(u_=None):
        return GR.STATES.get(u_ if u_ is not None else gu)

    def has(r_, id_):
        return bool(GR.hasFx(GR.ecc(tbuf, r_), GR.fxIndex(id_)))

    def click(r_=None, u_=None):
        GR.addFx(tbuf, r_ if r_ is not None else gr_, G_CLICK)
        GR.tickPlayer(r_ if r_ is not None else gr_, tst, tbuf)

    def gtick(r_=None):
        GR.tickPlayer(r_ if r_ is not None else gr_, tst, tbuf)

    def setpos(r_, x, y, z):
        comp(r_, TCc.getComponentType()).getPosition().set(x, y, z)

    def ninstr(r_):
        v_ = comp(r_, VELc.getComponentType())
        return 0 if v_ is None else len(list(v_.getInstructions()))

    def full(stam=10.0, mana=200.0):
        gm.setStatValue(STAM, JFloat(stam))
        gm.setStatValue(MANA, JFloat(mana))
    # the FALL cause as the game has it: Damage keeps a cause INDEX (getCause = the DamageCause store's asset) - load the vanilla Fall.json
    dfall, wfall = dec(DCSc, "Fall", AZ.read("Server/Entity/Damage/Fall.json").decode("utf-8-sig"))
    keep_pl2 = HashMap(pbu)
    pbu.clear()
    lfall = load(DCSc, [dfall], "Hytale:Hytale") if dfall is not None else None
    pbu.putAll(keep_pl2)
    if DCSc.getAssetMap().getAsset("Fall") is not None:
        jfield(DCSc, "FALL").set(None, DCSc.getAssetMap().getAsset("Fall"))
    check(dfall is not None and lfall is not False and DCSc.FALL is not None and str(DCSc.FALL.getId()) == "Fall",
          "Q0: the vanilla Fall damage cause decoded + loaded (Damage resolves its cause through the store): %s %s" % (wfall, lfall))
    TCH = stub("GChunk", "com.hypixel.hytale.component.ArchetypeChunk", ["public static com.hypixel.hytale.component.Ref R = null;"],
               ["public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return R; }"],
               ctor="public GChunk() { super((com.hypixel.hytale.component.Store) null, (com.hypixel.hytale.component.Archetype) null); }")
    tch = U.allocateInstance(TCH.class_)
    gfs = GFS()

    def fall(r_, cause=None, amount=10.0):
        TCH.R = r_
        d_ = DMGc(ENTS(r_), cause if cause is not None else DCSc.FALL, JFloat(amount))
        gfs.handle(0, tch, tst, tbuf, d_)
        return bool(d_.isCancelled())
    reset_buf()
    TW.ALL.clear()

    # --- Q2. SHOOT (right click 1): GrappleBoltSys on the real StandardPhysicsProvider -> the record, the OUT effect, the impact wrapper
    fk = FakeImpact()
    b1, sp1 = shoot(x=10.5, y=66.0, z=0.5, fake=fk)
    s1 = gstate()
    wrap = sp1.getImpactConsumer()
    check(s1 is not None and int(s1.mode) == 1 and s1.bolt == b1 and str(s1.item) == XB and has(gr_, G_OUT) and GImp.class_.isInstance(wrap) and wrap.inner == fk
          and str(wrap.u) == str(gu) and int(GR.SHOTS) == 1 and not list(TBf.REMOVED)
          and bool(GR.ecc(tbuf, gr_).getActiveEffects().containsKey(JInt(int(GR.fxIndex(G_OUT))))),
          "Q2 (2.1 / 3.1): the bolt's SPAWN -> the grapple record (mode OUT, the crossbow in hand), the OUT effect on the shooter (the chain's next right click "
          "= a click), the bolt's own ImpactConsumer wrapped (GrappleImpact.inner = it): %s / %s" % (None if s1 is None else int(s1.mode), str(GR.LAST_WHY)))
    b0, sp0 = bolt(1.0, 1.0, 1.0)
    vanilla_ic = sp0.getImpactConsumer()
    check(vanilla_ic is not None and "StandardPhysicsProvider" in str(vanilla_ic.getClass().getName()),
          "Q2 (VERIFIED in the bare JVM): the real StandardPhysicsProvider constructor sets its own impact consumer - the one the wrapper calls: %s" % vanilla_ic.getClass().getName())
    n_ign = int(GR.SHOTS)
    shoot(model="Arrow_Crude")
    shoot(reason=ADDR.LOAD)
    check(int(GR.SHOTS) == n_ign and gstate().bolt == b1, "Q2: another projectile model (a normal crossbow bolt) and a LOADed bolt are ignored")
    # --- Q3. STUCK IN A BLOCK + FULL PULL (right click 2): the impact (a block) -> stuck; the click -> cost + per-tick Set toward the bolt; arrival hop
    wrap.onImpact(b1, V3(10.5, 66.0, 0.5), V3Ic(10, 66, 0), None, None, tbuf)
    sp1.setState(SPST.RESTING)
    check(bool(s1.stuck) and fk.calls == [(b1, None)] and str(GR.LAST_WHY) == "bolt stuck",
          "Q3 (2.2): a block impact through the wrapper -> the bolt is STUCK (the anchor), and the engine's own consumer still ran once (ProjectileMiss unchanged)")
    full()
    gtick()
    check(int(s1.mode) == 1 and ninstr(gr_) == 0 and gstate().equals(s1), "Q3: a tick without a click changes nothing (no velocity, no cost): %s %s" % (int(s1.mode), ninstr(gr_)))
    click()
    v1 = last_instr(gr_)
    sdr = round(float(gm.get(SDR).get()), 3) if gm.get(SDR) is not None else None
    check(int(s1.mode) == 2 and int(s1.kind) == 1 and sv(gm, STAM) == 7.0 and sv(gm, MANA) == 198.5 and sdr == -0.7 and not has(gr_, G_CLICK) and int(GR.PULLS) == 1,
          "Q3 (1.1 cost): the click on a stuck bolt = FULL PULL - 3 Stamina + 1.5 Mana (10 -> 7, 200 -> 198.5), Stamina regen paused (StaminaRegenDelay %s), the CLICK "
          "effect consumed: %s" % (sdr, str(GR.LAST_WHY)))
    check(v1 is not None and v1[1] == "Set" and v1[2] is None and abs(v1[0][0] - 23.8565) < 1e-3 and abs(v1[0][1] - 2.6242) < 1e-3 and v1[0][2] == 0.0,
          "Q3 (2.3): the same tick a Velocity Set of 24 b/s from the chest toward the bolt (no VelocityConfig = the GrapplingHook way): %s" % (v1,))
    n0 = ninstr(gr_)
    setpos(gr_, 5.5, 64.5, 0.5)
    gtick()
    v2 = last_instr(gr_)
    d2_ = math.sqrt((10.5 - 5.5) ** 2 + (66.0 - 65.4) ** 2)
    check(ninstr(gr_) == n0 + 1 and v2[0][0] > 19.0 and abs(math.sqrt(sum(x * x for x in v2[0])) - min(24.0, 4.0 * d2_)) < 1e-3,
          "Q3: every tick one more Set (re-aimed; FIX ROUND: %.2f blocks left = eased to 4 x that = %.2f b/s): %s" % (d2_, min(24.0, 4.0 * d2_), v2))
    check(bool(GR.fallSafe(gu, int(SYS_.currentTimeMillis()))) and fall(gr_) and not fall(gr_, cause=DCSc.PROJECTILE),
          "Q3 (2.3, GrappleFallSys on a REAL Damage): FALL damage while pulled is cancelled; other damage is not")
    setpos(gr_, 9.6, 64.5, 0.5)
    gtick()
    v3 = last_instr(gr_)
    check(gstate() is None and v3 is not None and v3[0][1] == 6.0 and abs(v3[0][0] - v2[0][0] * 0.25) < 1e-3 and b1 in list(TBf.REMOVED) and not has(gr_, G_OUT)
          and int(GR.ARRIVALS) == 1 and str(GR.LAST_WHY) == "arrived (hop)",
          "Q3 (1.1): within 1.2 of the bolt (from the chest) = ARRIVAL - the bolt above the feet gives the hop (y 6, the run x 0.25), the bolt removed, OUT removed: %s" % (v3,))
    check(fall(gr_) and int(GR.FALLS) >= 2, "Q3 (1.1): landing inside grapple.landGrace (0.5 s) after an arrival = no FALL damage")
    GR.GRACE.clear()
    check(not fall(gr_), "Q3: after the grace, FALL damage is normal again")
    print("Q3. stuck bolt: impact -> stuck, click -> 3 Stamina + 1.5 Mana + regen pause, 24 b/s Sets per tick, arrival hop, no fall damage while pulled / in grace")

    # --- Q4. HALF PULL (right click 2 while the bolt still flies) + Q5. LET GO WITH MOMENTUM (right click 3)
    reset_buf()
    setpos(gr_, 0.5, 64.0, 0.5)
    full()
    GR.LASTEND.clear()
    b2, sp2 = shoot(x=20.5, y=64.9, z=0.5)
    s2 = gstate()
    click()
    v4 = last_instr(gr_)
    check(s2 is not None and int(s2.mode) == 2 and int(s2.kind) == 2 and [round(float(s2.tx), 4), round(float(s2.ty), 4)] == [10.5, 64.9] and b2 in list(TBf.REMOVED)
          and s2.bolt is None and sv(gm, STAM) == 8.0 and sv(gm, MANA) == 199.0 and v4 is not None and r6(v4[0]) == [24.0, 0.0, 0.0] and int(GR.HALFS) == 1,
          "Q4 (Skyy: 'pulls you half way'): a click while the bolt flies -> target half way (10 of 20 blocks), the bolt removed at once, 2 Stamina + 1 Mana, "
          "Set 24 b/s: %s" % (v4,))
    setpos(gr_, 3.5, 64.0, 0.5)
    gtick()
    click()
    v5 = last_instr(gr_)
    check(gstate() is None and v5 is not None and r6(v5[0]) == [24.0, 2.0, 0.0] and v5[1] == "Set" and int(GR.RELEASES) == 1 and not has(gr_, G_OUT)
          and not bool(GR.fallSafe(gu, int(SYS_.currentTimeMillis()))) and not fall(gr_),
          "Q5 (Skyy: 'let go, and keep momentum'): a click while pulled = one last Set (100%% of 24 + 2 up), the grapple is over, NO fall-damage grace: %s" % (v5,))
    reset_buf()
    GR.LASTEND.clear()
    setpos(gr_, 0.5, 64.0, 0.5)
    full()
    b2b, sp2b = shoot(x=20.5, y=64.9, z=0.5)
    click()
    setpos(gr_, 9.8, 64.0, 0.5)
    gtick()
    va = last_instr(gr_)
    check(gstate() is None and va is not None and r6(va[0]) == [6.0, 0.0, 0.0] and str(GR.LAST_WHY) == "arrived" and bool(GR.fallSafe(gu, int(SYS_.currentTimeMillis()))),
          "Q4: a half pull that reaches its point stops softly (24 x 0.25, no hop - the hop is only for a stuck bolt above the feet), with the landing grace: %s" % (va,))
    GR.GRACE.clear()
    print("Q4/Q5. half pull: half way, bolt gone, 2 + 1, soft arrival; let go: (24, 2, 0) kept, normal fall rules")

    # --- Q6. MOB HOOKS (Skyy: 'Hooks the mob'): small = yanked to you, big = pulls you, boss = pulls you; a hooked player (PvP rules)
    def mob(i_, x, y, z, box, role=None):
        r_ = REFc(tst, i_)
        if role is None:
            put(r_, NPCc.getComponentType(), TCc())
        else:
            n_ = U.allocateInstance(NPCc.class_)
            setf(n_, NPCc, gfield("com.hypixel.hytale.server.npc.entities.NPCEntity", "getRoleName"), role)
            put(r_, NPCc.getComponentType(), n_)
        put(r_, ESMc.getComponentType(), stats())
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        put(r_, BBXc.getComponentType(), BBXc(BOXc(-box[0] / 2.0, 0.0, -box[2] / 2.0, box[0] / 2.0, box[1], box[2] / 2.0)))
        put(r_, VELc.getComponentType(), VELc())
        return r_

    def hooked(target):
        reset_buf()
        GR.LASTEND.clear()
        setpos(gr_, 0.5, 64.0, 0.5)
        full()
        b_, sp_ = shoot(x=8.0, y=65.0, z=0.5, fake=FakeImpact())
        sp_.getImpactConsumer().onImpact(b_, V3(8.0, 65.0, 0.5), V3Ic(8, 65, 0), target, "Body", tbuf)
        return b_, gstate()
    skel = mob(60, 10.5, 64.0, 0.5, (0.6, 1.8, 0.6))
    bh, sh = hooked(skel)
    check(sh is not None and bool(sh.hooked) and sh.hook == skel and int(GR.HOOKS) >= 1 and str(GR.LAST_WHY) == "hooked",
          "Q6 (Skyy: 'Hooks the mob'): the bolt hitting an NPC with stats -> HOOKED (the wrapper sees the entity before the engine's ProjectileHit chain)")
    n_p = ninstr(gr_)
    click()
    vm = last_instr(skel)
    check(int(sh.mode) == 3 and int(sh.kind) == 4 and vm is not None and vm[1] == "Set" and vm[2] == (0.97, 0.94, 5.0, "Exp") and vm[0][0] < -23.0
          and sv(gm, STAM) == 7.0 and int(GR.YANKS) >= 1 and ninstr(gr_) == n_p,
          "Q6 (Harpoon-style, small = yanked): a skeleton-sized mob (0.65 < 1) is YANKED - its Velocity Set toward you (-24 b/s, the dagger dash config like a "
          "knockback), the full cost: %s" % (vm,))
    setpos(skel, 1.6, 64.0, 0.5)
    gtick()
    vy_ = last_instr(skel)
    check(gstate() is None and str(GR.LAST_WHY) == "yanked" and not has(gr_, G_OUT) and vy_ is not None and vy_[1] == "Set" and abs(vy_[0][0] - vm[0][0] * 0.25) < 1e-3,
          "Q6: the yanked mob reaches you -> over (FIX ROUND: it keeps a quarter of its last Set, %s -> %s): %s" % (vm[0], vy_, str(GR.LAST_WHY)))
    cow = mob(61, 10.5, 64.0, 0.5, (1.6, 1.7, 1.6))
    bh, sh = hooked(cow)
    n_c = ninstr(cow)
    click()
    vp = last_instr(gr_)
    check(int(sh.mode) == 2 and int(sh.kind) == 3 and vp is not None and vp[0][0] > 23.0 and ninstr(cow) == n_c,
          "Q6 (big = pulls you): a cow-sized mob (4.4 > 1) pulls YOU (your Set toward it; its velocity untouched): %s" % (vp,))
    setpos(cow, 12.5, 64.0, 2.5)
    gtick()
    check(abs(float(sh.tx) - 12.5) < 1e-9 and abs(float(sh.tz) - 2.5) < 1e-9, "Q6: the pull follows the mob as it moves")
    setpos(gr_, 11.4, 64.0, 2.5)
    gtick()
    check(gstate() is None and str(GR.LAST_WHY).startswith("arrived"), "Q6: next to the big mob (stop + half its width) -> arrived: %s" % str(GR.LAST_WHY))
    boss = mob(62, 10.5, 64.0, 0.5, (0.6, 1.8, 0.6), role="Goblin_Duke")
    bh, sh = hooked(boss)
    n_b = ninstr(boss)
    click()
    check(int(sh.mode) == 2 and int(sh.kind) == 3 and bool(sh.boss) and ninstr(boss) == n_b, "Q6 (bosses never yanked): a small boss (Goblin_Duke) pulls you instead")
    GR.STATES.clear()
    su2, sr2, spr2, sm2 = player(63, 10.5, 64.0, 0.5)
    bh, sh = hooked(sr2)
    click()
    k_def = (int(sh.mode), int(sh.kind), bool(sh.hookPlayer))
    GR.STATES.clear()
    ACfg.G_YANK_PLAYERS = True
    wcfg.setPvpEnabled(True)
    bh, sh = hooked(sr2)
    click()
    vpl = last_instr(sr2)
    k_pvp = (int(sh.mode), int(sh.kind), None if vpl is None else vpl[2])
    GR.STATES.clear()
    bh, sh = hooked(rp)
    click()
    k_ally = (int(sh.mode), int(sh.kind))
    GR.STATES.clear()
    wcfg.setPvpEnabled(False)
    ACfg.G_YANK_PLAYERS = False
    check(k_def == (2, 3, True) and k_pvp == (3, 4, None) and k_ally == (2, 3),
          "Q6 (Skyy: players never yanked unless PvP + not party): default - a hooked player pulls you %s; row on + PvP on + a stranger - yanked (a player's Set, "
          "no config) %s; your party member - pulls you %s" % (k_def, k_pvp, k_ally))
    junk = REFc(tst, 64)
    put(junk, TCc.getComponentType(), TCc(V3(5.0, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    bh, sh = hooked(junk)
    check(gstate() is None and "cannot be hooked" in str(GR.LAST_WHY), "Q6: a hit on something that is no creature (an item, a projectile) ends the grapple (the bolt drops)")
    print("Q6. hooks: skeleton yanked (NPC Set + dash config), cow + boss pull you (following it), players never yanked unless the row + PvP + not party")

    # --- Q7. RELOAD + LOADED BOLTS UNTOUCHED: the grapple never changes Ammo (a real stat), never names the inventory beyond reading the hand
    AMMO = int(ESTc.getAssetMap().getIndex("Ammo"))
    ammo_before = ammo_after = None
    if AMMO >= 0:
        SMO2 = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
        MT2 = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
        CT2 = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
        gm.putModifier(AMMO, "armorytest", SMO2(MT2.MAX, CT2.ADDITIVE, JFloat(6.0)))
        gm.setStatValue(AMMO, JFloat(4.0))
        ammo_before = sv(gm, AMMO)
        reset_buf()
        GR.LASTEND.clear()
        setpos(gr_, 0.5, 64.0, 0.5)
        full()
        b7, sp7 = shoot(x=10.5, y=66.0, z=0.5)
        sp7.setState(SPST.RESTING)
        click()
        click()
        ammo_after = sv(gm, AMMO)
    gcalls = set()
    for cn_ in ("Grapple", "GrappleBoltSys", "GrappleFallSys", "GrappleImpact"):
        for mm_ in CPj.get(PKG + cn_).getDeclaredMethods():
            gcalls |= set(calls_of(PKG + cn_, str(mm_.getName())))
    inv_calls = sorted(c_ for c_ in gcalls if ("Item" in c_ or "Inventory" in c_ or "Ammo" in c_ or "Slot" in c_) and c_ != "handItem")
    check(ammo_before == 4.0 and ammo_after == 4.0 and inv_calls == [],
          "Q7 (2.1 VERIFIED): the Ammo stat (the loaded bolts SkyySkills keeps) stays 4 through a shot + pull + release; no grapple method calls an inventory / item / "
          "slot method (the hand is read through ArmoryTrav.handItem only): %s -> %s, %s" % (ammo_before, ammo_after, inv_calls))
    # --- Q8. COSTS: too little Stamina / Mana = no pull, the bolt stays; no Mana pool = Stamina only
    GR.STATES.clear()
    reset_buf()
    GR.LASTEND.clear()
    setpos(gr_, 0.5, 64.0, 0.5)
    b8, sp8 = shoot(x=10.5, y=66.0, z=0.5)
    sp8.setState(SPST.RESTING)
    full(stam=2.5)
    n8 = ninstr(gr_)
    r0 = int(GR.REFUSED)
    click()
    s8 = gstate()
    c_st = (s8 is not None and int(s8.mode) == 1, b8 in list(TBf.REMOVED), ninstr(gr_) == n8, sv(gm, STAM), sv(gm, MANA), int(GR.REFUSED) - r0, str(GR.LAST_WHY))
    full(stam=10.0, mana=1.0)
    click()
    c_mn = (int(gstate().mode), sv(gm, STAM), sv(gm, MANA))
    check(c_st == (True, False, True, 2.5, 200.0, 1, "too little Stamina or Mana") and c_mn == (1, 10.0, 1.0),
          "Q8 (1.1): 2.5 Stamina < 3 -> no pull, nothing taken, the bolt stays; 1 Mana < 1.5 -> no pull: %s / %s" % (c_st, c_mn))
    nm_ = ESMc()
    nm_.update()
    nm_.setStatValue(STAM, JFloat(10.0))
    check(int(GR.take(tbuf, REFc(tst, 65), 3.0, 1.5)) == 1, "Q8: an entity without stats is never blocked")
    put(gr_, ESMc.getComponentType(), nm_)
    mana_max0 = float(nm_.get(MANA).getMax())
    click()
    s8b = gstate()
    put(gr_, ESMc.getComponentType(), gm)
    check(mana_max0 == 0.0 and s8b is not None and int(s8b.mode) == 2 and sv(nm_, STAM) == 7.0,
          "Q8 (1.1): a player with no Mana pool (max 0: Base Mana off) pays the Stamina only: %s" % sv(nm_, STAM))
    GR.STATES.clear()
    print("Q7/Q8. Ammo untouched + no inventory calls; costs: short Stamina / Mana refused (bolt stays), no Mana pool = Stamina only")

    # --- Q9. SWAP OFF THE CROSSBOW, Q10. ARCHERS-ONLY LOCK, Q11. the rest of the state machine
    reset_buf()
    GR.LASTEND.clear()
    full()
    b9, sp9 = shoot()
    GR.HAND.put(gu, "Weapon_Sword_Iron")
    gtick()
    sw = (gstate() is None, b9 in list(TBf.REMOVED), has(gr_, G_OUT), str(GR.LAST_WHY))
    GR.HAND.put(gu, XB)
    check(sw == (True, True, False, "swapped off the crossbow"), "Q9 (spec 1.1): swapping off the crossbow ends the grapple - bolt removed, OUT removed: %s" % (sw,))

    @JImplements("java.util.function.Function")
    class NoXbow:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            return JClass("java.lang.Boolean").FALSE if "Crossbow" in str(a_[1]) else JClass("java.lang.Boolean").TRUE
    br.put("class:fn:allowed", NoXbow())
    reset_buf()
    r10 = int(GR.REFUSED)
    b10, sp10 = shoot()
    lk = (gstate() is None, b10 in list(TBf.REMOVED), int(GR.REFUSED) - r10, str(GR.LAST_WHY), has(gr_, G_OUT))
    br.remove("class:fn:allowed")
    check(lk == (True, True, 1, "class lock", False), "Q10 (Archers only): SkyyClasses' class:fn:allowed refusing the crossbow -> the bolt is removed at its "
                                                      "spawn, no record, no OUT effect, no cost: %s" % (lk,))
    reset_buf()
    ACfg.PART_GRAPPLE = False
    b11, sp11 = shoot()
    p_off = (gstate() is None, b11 in list(TBf.REMOVED), str(GR.LAST_WHY))
    ACfg.PART_GRAPPLE = True
    ACfg.G_CD = 2.0
    GR.LASTEND.put(gu, JClass("java.lang.Long")(int(SYS_.currentTimeMillis())))
    b12, sp12 = shoot()
    p_cd = (gstate() is None, b12 in list(TBf.REMOVED), str(GR.LAST_WHY))
    ACfg.G_CD = 0.0
    check(p_off == (True, True, "part.grapple off") and p_cd == (True, True, "cooldown"), "Q11: part.grapple off / inside grapple.cooldown -> the bolt is removed at spawn: %s %s" % (p_off, p_cd))
    reset_buf()
    GR.LASTEND.clear()
    b13, sp13 = shoot()
    b14, sp14 = shoot()
    check(gstate().bolt == b14 and b13 in list(TBf.REMOVED) and b14 not in list(TBf.REMOVED), "Q11 (race, spec 2.1): a second shot while one is out -> the newest bolt wins, the older is removed")
    setpos(b14, 34.0, 64.9, 0.5)
    gtick()
    sn1 = (gstate() is None, str(GR.LAST_WHY), b14 in list(TBf.REMOVED))
    reset_buf()
    b15, sp15 = shoot(x=30.5, y=64.9, z=0.5)
    sp15.setState(SPST.RESTING)
    gtick()
    k15 = gstate() is not None
    setpos(b15, 41.5, 64.9, 0.5)
    gtick()
    sn2 = (k15, gstate() is None, str(GR.LAST_WHY))
    check(sn1 == (True, "rope snapped", True) and sn2 == (True, True, "rope snapped"),
          "Q11 (1.1): a flying bolt past grapple.ropeLength 32 snaps; a stuck bolt 30 away holds, past grapple.snapDistance 40 snaps: %s %s" % (sn1, sn2))
    reset_buf()
    b16, sp16 = shoot(x=10.5, y=66.0, z=0.5)
    sp16.setState(SPST.RESTING)
    gtick()
    gstate().stuckAt = int(SYS_.currentTimeMillis()) - 31000
    gtick()
    an = (gstate() is None, str(GR.LAST_WHY), b16 in list(TBf.REMOVED))
    b17, sp17 = shoot()
    sp17.setState(SPST.ACTIVE)
    gsys.onEntityRemove(b17, JClass("com.hypixel.hytale.component.RemoveReason").REMOVE, tst, tbuf)
    bg = (gstate() is None, str(GR.LAST_WHY))
    check(an == (True, "anchor time", True) and bg == (True, "bolt gone"), "Q11 (1.1): a stuck bolt drops after grapple.anchorSeconds 30; a bolt the engine removes ends it: %s %s" % (an, bg))
    b18, sp18 = shoot()
    sp18.setState(SPST.RESTING)
    other = U.allocateInstance(TSt.class_)
    GR.tickPlayer(gr_, other, tbuf)
    wc = (gstate() is None, str(GR.LAST_WHY))
    b19, sp19 = shoot()
    put(gr_, DTHc.getComponentType(), TCc())
    gtick()
    dd = (gstate() is None, str(GR.LAST_WHY))
    put(gr_, DTHc.getComponentType(), None)
    check(wc == (True, "left the world") and dd == (True, "died"), "Q11: leaving the world / dying ends the grapple: %s %s" % (wc, dd))
    GR.addFx(tbuf, gr_, G_OUT)
    GR.addFx(tbuf, gr_, G_CLICK)
    st0 = int(GR.STALE)
    gtick()
    check(not has(gr_, G_OUT) and not has(gr_, G_CLICK) and int(GR.STALE) == st0 + 1, "Q11: a left-over OUT / CLICK effect without a record (restart, relog) is cleared on the next tick")
    reset_buf()
    full()
    GR.GRACE.clear()
    b20, sp20 = shoot(x=10.5, y=66.0, z=0.5)
    sp20.setState(SPST.RESTING)
    click()
    gstate().pullAt = int(SYS_.currentTimeMillis()) - 3000
    gtick()
    pt = (gstate() is None, str(GR.LAST_WHY), bool(GR.fallSafe(gu, int(SYS_.currentTimeMillis()))))
    b21, sp21 = shoot(x=10.5, y=66.0, z=0.5)
    sp21.setState(SPST.RESTING)
    full()
    click()
    gstate().pullAt = int(SYS_.currentTimeMillis()) - 600
    for _k in range(10):
        gtick()
    sl = (gstate() is None, str(GR.LAST_WHY), bool(GR.fallSafe(gu, int(SYS_.currentTimeMillis()))))
    GR.GRACE.clear()
    check(pt == (True, "pull time", False) and sl == (True, "blocked", True),
          "Q11 (1.1): grapple.pullMaxSeconds 2.5 -> let go (no grace); no progress for 9 ticks after the first 0.5 s (a wall) -> stop as an arrival (grace): %s %s" % (pt, sl))
    ACfg.TRAV_FX = True
    GR.DOT_WIN = 0          # FIX ROUND: a fresh rope dot budget window (the harness ticks far faster than 100 ms)
    dots0 = int(GR.DOTS)
    GR.rope(tbuf, 0.0, 64.0, 0.0, 20.0, 64.0, 0.0)
    ACfg.G_ROPE = "off"
    GR.rope(tbuf, 0.0, 64.0, 0.0, 20.0, 64.0, 0.0)
    ACfg.G_ROPE = "pull"
    ACfg.TRAV_FX = False
    check(int(GR.DOTS) - dots0 == 13, "Q11 (2.4): the rope = 13 dots for 20 blocks at 1.5 (ParticleUtil on the real path; none with grapple.rope off): %d" % (int(GR.DOTS) - dots0))
    tt_calls = calls_of(PKG + "TravTick", "tick")
    TCH.R = gr_
    reset_buf()
    b22, sp22 = shoot()
    GR.addFx(tbuf, gr_, G_CLICK)
    TT2 = JClass(PKG + "TravTick")()
    TT2.tick(JFloat(0.033), 0, tch, tst, tbuf)
    check("tickPlayer" in tt_calls and int(gstate().mode) == 2 and int(gstate().kind) == 2,
          "Q11: TravTick.tick (the per-player EntityTickingSystem) runs Grapple.tickPlayer for the chunk's player - a click there starts the pull")
    GR.STATES.clear()
    print("Q9-Q11. swap off / class lock / part off / cooldown / newest bolt / snaps / anchor time / engine removal / world / death / stale effects / pull time / stall / rope / TravTick")

    # --- Q12. the rows (spec 1.3 + Skyy's answers), the loader clamps, armory:grapple, the systems' wiring
    Rows3 = JClass(PKG + "CfgRows")
    ks3 = [str(k) for k in Rows3.KEYS]
    df3 = dict(zip(ks3, [str(d) for d in Rows3.DEFS]))
    ty3 = dict(zip(ks3, [str(t) for t in Rows3.TYPES]))
    want_g = {"part.grapple": "true", "grapple.ropeLength": "32", "grapple.snapDistance": "40", "grapple.anchorSeconds": "30", "grapple.pullSpeed": "24",
              "grapple.maxDown": "18", "grapple.stopDistance": "1.2", "grapple.halfPercent": "50", "grapple.pullMaxSeconds": "2.5", "grapple.releaseKeep": "100",
              "grapple.releaseLift": "2", "grapple.arriveHop": "6", "grapple.landGrace": "0.5", "grapple.stamina": "3", "grapple.mana": "1.5",
              "grapple.halfStamina": "2", "grapple.halfMana": "1", "grapple.regenPause": "0.7", "grapple.rope": "pull", "grapple.ropeSpacing": "1.5",
              "grapple.cooldown": "0", "grapple.yankSize": "1", "grapple.bossWords": "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex", "grapple.yankPlayers": "false",
              "grapple.ease": "4", "grapple.noYankWords": "Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub", "trav.staminaCap": "5"}
    bad_g = dict((k, (df3.get(k), v)) for k, v in want_g.items() if df3.get(k) != v)
    check(not bad_g and ty3["grapple.rope"] == "choice" and ty3["grapple.bossWords"] == "text" and ty3["grapple.noYankWords"] == "text" and "grapple.flight" in ks3 and "grapple.rightClick" in ks3
          and int(Rows3.KEEP) == 10, "Q12 (1.3): every grapple row + trav.staminaCap 5 emit with Skyy's / the spec's default, KEEP 10, 2 read-only rows: %s" % bad_g)
    check(int(ACfg.STAMINA_CAP) == 5 and int(ACfg.G_ROPE_LEN) == 32 and abs(float(ACfg.G_SPEED) - 24.0) < 1e-9 and str(ACfg.G_ROPE) == "pull" and not bool(ACfg.G_YANK_PLAYERS),
          "Q12: the loaded defaults (trav.staminaCap 5 = two traversals per bar)")
    pr3 = Props()
    for k_, v_ in (("grapple.pullSpeed", "99"), ("grapple.rope", "ALWAYS"), ("grapple.yankSize", "-1"), ("grapple.halfPercent", "5"), ("grapple.bossWords", "x" * 300),
                   ("trav.staminaCap", "7")):
        pr3.setProperty(k_, v_)
    ACfg.apply(pr3)
    cl3 = (float(ACfg.G_SPEED), str(ACfg.G_ROPE), float(ACfg.G_YANK_SIZE), int(ACfg.G_HALF_PCT), len(str(ACfg.G_BOSS)), int(ACfg.STAMINA_CAP))
    pr3.setProperty("grapple.rope", "rainbow")
    ACfg.apply(pr3)
    check(cl3 == (40.0, "always", 0.0, 10, 200, 7) and str(ACfg.G_ROPE) == "pull" and str(br.get("armory:grapple")).startswith("grapple on - rope 32 blocks"),
          "Q12: the loader clamps like the kit (99 -> 40, ALWAYS -> always, -1 -> 0, 5 -> 10, 300 chars -> 200; an unknown rope mode reads pull); armory:grapple follows: %s" % (cl3,))
    ACfg.useDefaults()
    gtxt = str(ACfg.grappleText())
    check("pull 24.0 b/s (down at most 18.0), eases x4.0 near the end" in gtxt and "cost 3.0 Stamina + 1.5 Mana (half 2.0 + 1.0)" in gtxt and "players never yanked" in gtxt
          and "never yanked: Invulnerable mobs + (Merchant,Trader" in gtxt and abs(float(ACfg.G_EASE) - 4.0) < 1e-9,
          "Q12: armory:grapple carries the live numbers: %s" % gtxt[:200])
    q_ = GBS().getQuery()
    check(q_ is not None and "TravTick" in str(TT2.getClass().getName()), "Q12: GrappleBoltSys queries Projectile + StandardPhysicsProvider (the real component types)")
    print("Q12. %d grapple rows with their defaults, loader clamps, armory:grapple" % len(want_g))

    # --- Q13. THE ONE-TIME trav.staminaCap UPDATE (Skyy 2026-10-06: 10 -> 5): the pure text step, then the real migrate012 on scratch files
    MK = str(ACfg.M12_MARK)

    def upd(t_):
        r_ = ACfg.m12Update(t_)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])
    u1 = upd("a=1\ntrav.staminaCap=10\nb=2\n")
    u2 = upd("a=1\r\n# cap\r\ntrav.staminaCap = 10\r\nb=2\r\n")
    u3 = upd("trav.staminaCap=7\n")
    u4 = upd("quick.life=20\n")
    u5 = upd("quick.life=20")
    u6 = upd(u1[0])
    u7 = upd("trav.staminaCap=1\\\n0\n")
    u8 = upd("trav.staminaCap=10\ntrav.staminaCap=10\n")
    check(u1 == ("a=1\n" + MK + "\ntrav.staminaCap=5\nb=2\n", "trav.staminaCap 10 -> 5", [], ["trav.staminaCap", "10", "5"])
          and u2 == ("a=1\r\n# cap\r\n" + MK + "\r\ntrav.staminaCap = 5\r\nb=2\r\n", "trav.staminaCap 10 -> 5", [], ["trav.staminaCap", "10", "5"])
          and u3[0] == MK + "\ntrav.staminaCap=7\n" and u3[1] == "" and len(u3[2]) == 1 and "kept (custom)" in u3[2][0] and u3[3] == []
          and u4 == ("quick.life=20\n" + MK + "\n", "", [], []) and u5 == ("quick.life=20\n" + MK, "", [], []) and u6 is None
          and u7[1] == "" and "trav.staminaCap=1\\\n0" in u7[0] and len(u7[2]) == 1 and u8[0] == MK + "\ntrav.staminaCap=5\ntrav.staminaCap=5\n",
          "Q13 (PROJECT-RULES 4): the old default 10 -> 5 (value text only, separator + CRLF kept), a hand-set 7 / a continued line KEPT + noted, no line = marker "
          "only (the file's own line end), the marker = runs once, two old lines both: %s / %s / %s" % (u1, u3, u4))
    mdir = os.path.join(SCRATCH, "m12", "mods", "Skyy_SkyyArmory")
    shutil.rmtree(os.path.dirname(os.path.dirname(mdir)), ignore_errors=True)
    os.makedirs(mdir)
    mtxt = ("# SkyyArmory 0.1.1 test file\r\npart.trav=true\r\ntrav.staminaPercent=50\r\n# cap\r\ntrav.staminaCap=10\r\nquick.life=20\r\n").encode("latin-1")
    open(os.path.join(mdir, "config.properties"), "wb").write(mtxt)
    ACfg.DIR = Paths.get(mdir)
    ACfg.FILE = ACfg.DIR.resolve("config.properties")
    mres = str(ACfg.migrate012())
    after = open(os.path.join(mdir, "config.properties"), "rb").read()
    hist = os.path.join(mdir, "config-history")
    baks = sorted(f_ for f_ in os.listdir(hist) if f_.endswith(".bak")) if os.path.isdir(hist) else []
    bak_ok = bool(baks) and open(os.path.join(hist, baks[-1]), "rb").read() == mtxt
    idx_ = open(os.path.join(hist, "index.log"), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(hist, "index.log")) else ""
    logp = os.path.join(mdir, "config-changes.log")
    log_ = open(logp, "rb").read().decode("latin-1") if os.path.isfile(logp) else ""
    mres2 = str(ACfg.migrate012())
    after2 = open(os.path.join(mdir, "config.properties"), "rb").read()
    ACfg.load()
    cap_l = int(ACfg.STAMINA_CAP)
    check(after == upd(mtxt.decode("latin-1"))[0].encode("latin-1") and b"trav.staminaCap=5\r\n" in after and bak_ok and "before the 0.1.2 traversal Stamina cap update" in idx_
          and "\tSkyyArmory 0.1.2\t-\tupdate\ttrav.staminaCap\t10\t5\tok" in log_ and "10 -> 5" in mres and mres2 == "" and after2 == after and cap_l == 5,
          "Q13 (the real ArmoryCfg.migrate012 on a scratch file): the History copy = the old bytes (verified before the rewrite), the Undo-able change-log line "
          "(update trav.staminaCap 10 -> 5), CRLF kept, the second run does nothing, the loader reads 5: %s | %s" % (mres[:120], log_.strip()[-80:]))
    ACfg.DIR = None
    ACfg.FILE = None
    ACfg.useDefaults()
    print("Q13. trav.staminaCap one-time update: text step (old 10 -> 5, custom kept, marker once, CRLF), real migrate012 with History + Undo log, second run idle")

    # --- Q14. FIX ROUND (critic findings 2026-10-06) - every new path EXECUTED
    INVc = JClass("com.hypixel.hytale.server.core.modules.entity.component.Invulnerable")
    setf(em, EMc, gfield(EMN, "getInvulnerableComponentType"), reg_.registerComponent(INVc.class_, Sup(lambda: None)))
    GR.HAND.put(gu, XB)
    GR.STATES.clear()
    GR.GRACE.clear()
    inv_m = mob(70, 10.5, 64.0, 0.5, (0.6, 2.0, 0.6), role="Kweebec_Rootling")
    put(inv_m, INVc.getComponentType(), INVc.INSTANCE)
    bh, sh = hooked(inv_m)
    n_i = ninstr(inv_m)
    click()
    k_inv = (int(sh.mode), int(sh.kind), bool(sh.protect), ninstr(inv_m) == n_i)
    GR.STATES.clear()
    mer = mob(71, 10.5, 64.0, 0.5, (0.6, 2.0, 0.6), role="Kweebec_Merchant")
    bh, sh = hooked(mer)
    click()
    k_mer = (int(sh.mode), int(sh.kind), bool(sh.protect))
    GR.STATES.clear()
    chf = mob(72, 10.5, 64.0, 0.5, (0.6, 1.8, 0.6), role="Trork_Chieftain")
    bh, sh = hooked(chf)
    click()
    k_chf = (int(sh.mode), int(sh.kind), bool(sh.boss))
    GR.STATES.clear()
    check(k_inv == (2, 3, True, True) and k_mer == (2, 3, True) and k_chf == (2, 3, True),
          "Q14 (critic 1.1 + 1.2): a small Invulnerable mob (the Kweebec_Merchant shape, 0.72) pulls YOU (its velocity untouched) %s; a 'Merchant' role "
          "pulls you %s; Trork_Chieftain (new boss word) pulls you %s" % (k_inv, k_mer, k_chf))
    # the yank's stall rule (a mob behind a fence: it does not come closer) + the quarter speed at the end
    fen = mob(73, 10.5, 64.0, 0.5, (0.6, 1.8, 0.6), role="Skeleton_Fighter")
    bh, sh = hooked(fen)
    click()
    k_fy = (int(sh.mode), int(sh.kind))
    sh.pullAt = int(SYS_.currentTimeMillis()) - 600
    vf0 = last_instr(fen)
    for _k in range(10):
        gtick()
    vf1 = last_instr(fen)
    check(k_fy == (3, 4) and gstate() is None and str(GR.LAST_WHY) == "yank blocked" and vf0 is not None and vf1 is not None
          and abs(vf1[0][0] - vf0[0][0] * 0.25) < 1e-3,
          "Q14 (critic 1.3 + 3.3): a yanked mob that makes no progress for 9 ticks after 0.5 s (a fence) is let go, keeping a quarter of its last Set: %s %s -> %s" % (
              k_fy, vf0, vf1))
    # a crossbow-root user that is not a crossbow (H1Z blunderbuss) gets no bolt; a pack crossbow id does
    reset_buf()
    GR.LASTEND.clear()
    GR.HAND.put(gu, "Weapon_Gun_Blunderbuss")
    bb_, spb_ = shoot()
    k_bb = (gstate() is None, bb_ in list(TBf.REMOVED), str(GR.LAST_WHY))
    GR.HAND.put(gu, "VC_Weapon_Crossbow_Void")
    bv_, spv_ = shoot()
    k_vc = (gstate() is not None and str(gstate().item) == "VC_Weapon_Crossbow_Void", bv_ in list(TBf.REMOVED))
    GR.STATES.clear()
    GR.HAND.put(gu, XB)
    check(k_bb == (True, True, "not a crossbow") and k_vc == (True, False),
          "Q14 (critic 2.2): a bolt from Weapon_Gun_Blunderbuss (shares the crossbow root) is removed at spawn %s; VC_Weapon_Crossbow_Void still grapples %s" % (k_bb, k_vc))
    # a stuck bolt taken by another mod (More Arrows' magnet removes resting projectiles): the anchor holds, the pull still works
    reset_buf()
    GR.LASTEND.clear()
    setpos(gr_, 0.5, 64.0, 0.5)
    full()
    ba_, spa_ = shoot(x=10.5, y=66.0, z=0.5, fake=FakeImpact())
    spa_.setState(SPST.RESTING)
    gtick()
    gsys.onEntityRemove(ba_, JClass("com.hypixel.hytale.component.RemoveReason").REMOVE, tst, tbuf)
    sa_ = gstate()
    k_a0 = (sa_ is not None and sa_.bolt is None and bool(sa_.stuck), str(GR.LAST_WHY))
    gtick()
    k_a1 = gstate() is not None and int(gstate().mode) == 1
    click()
    va_ = last_instr(gr_)
    k_a2 = (None if gstate() is None else (int(gstate().mode), int(gstate().kind), round(float(gstate().tx), 3), round(float(gstate().ty), 3)), sv(gm, STAM))
    GR.STATES.clear()
    check(k_a0 == (True, "bolt taken - the anchor holds") and k_a1 and k_a2 == ((2, 1, 10.5, 66.0), 7.0) and va_ is not None and va_[0][0] > 20.0,
          "Q14 (critic 2.1): a stuck bolt removed by another mod keeps the anchor (where it rested) - the click still pulls there for the full cost: %s %s %s" % (k_a0, k_a2, va_))
    # the sweep: a record whose player body is gone (disconnect) is dropped with its bolt; spent GRACE / LASTEND entries pruned; no grace for it
    reset_buf()
    gone_u = UUID.fromString("00000000-0000-0000-0011-000000000077")
    gone_r = REFc(tst, 77)
    gb_, gsp_ = bolt(5.0, 64.0, 0.5)
    gs_ = GSt(gone_u, gone_r, tst, XB, gb_, int(SYS_.currentTimeMillis()))
    gs_.mode = 2
    GR.STATES.put(gone_u, gs_)
    safe_live = bool(GR.fallSafe(gone_u, int(SYS_.currentTimeMillis())))
    setf(gone_r, REFc, "index", JInt(-2147483648))
    safe_gone = bool(GR.fallSafe(gone_u, int(SYS_.currentTimeMillis())))
    now_ = int(SYS_.currentTimeMillis())
    GR.GRACE.put(gone_u, JClass("java.lang.Long")(now_ - 5000))
    GR.GRACE.put(gu, JClass("java.lang.Long")(now_ + 60000))
    GR.LASTEND.put(gone_u, JClass("java.lang.Long")(now_ - 60000))
    sw0 = int(GR.SWEPT)
    GR.SWEEP_N = int(GR.SWEEP_EVERY) - 1
    gtick()
    k_sw = (GR.STATES.get(gone_u) is None, int(GR.SWEPT) - sw0, gb_ in list(TBf.REMOVED), GR.GRACE.get(gone_u) is None, GR.GRACE.get(gu) is not None,
            GR.LASTEND.get(gone_u) is None, int(GR.SWEEP_N))
    GR.GRACE.clear()
    check(safe_live and not safe_gone and k_sw == (True, 1, True, True, True, True, 0),
          "Q14 (critic 3.2): a pulled record whose body is gone gives no fall grace; the sweep (every %d player ticks) drops it + removes its bolt, prunes a spent "
          "GRACE / old LASTEND, keeps a live GRACE: %s" % (int(GR.SWEEP_EVERY), k_sw))
    # the cached effect indexes + the shared rope dot budget
    check(int(GR.OUT_I) == int(GR.fxIndex(G_OUT)) and int(GR.CLICK_I) == int(GR.fxIndex(G_CLICK)) and int(GR.OUT_I) >= 0 and int(GR.outI()) == int(GR.OUT_I),
          "Q14 (critic 2.4 / 3.4): the OUT / CLICK effect indexes are looked up once and cached: %d / %d" % (int(GR.OUT_I), int(GR.CLICK_I)))
    k_rb = None
    for _try in range(5):
        w_ = int(SYS_.currentTimeMillis()) // 100
        GR.DOT_WIN = w_
        GR.DOT_LEFT = 5
        d0_, c0_ = int(GR.DOTS), int(GR.DOTS_CUT)
        GR.rope(tbuf, 0.0, 64.0, 0.0, 20.0, 64.0, 0.0)
        GR.rope(tbuf, 0.0, 64.0, 0.0, 20.0, 64.0, 0.0)
        if int(SYS_.currentTimeMillis()) // 100 == w_:
            k_rb = (int(GR.DOTS) - d0_, int(GR.DOTS_CUT) - c0_, int(GR.DOT_LEFT))
            break
    check(k_rb == (5, 21, 0) and int(GR.DOT_BUDGET) == 64,
          "Q14 (critic 3.5): rope dots share one budget (%d per 100 ms, all players): 5 left -> two 13-dot ropes draw 5, 21 cut: %s" % (int(GR.DOT_BUDGET), k_rb))
    print("Q14. FIX ROUND: Invulnerable / noYank / new boss words pull you, yank stall + quarter stop, ease, no bolt from a blunderbuss, anchor kept when "
          "the bolt is taken, the disconnect sweep, cached effect indexes, the rope dot budget")
    GR.HAND = None
    GR.STATES.clear()
    GR.GRACE.clear()
    GR.LASTEND.clear()
    br.remove("party:fn:members")
    TW.ALL.clear()
'''

traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.1 - test harness. GENERATED by tools/armory_0_1_1_patch.py from test_skyyarmory_0.1.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.2 - test harness. GENERATED by tools/armory_0_1_2_patch.py from test_skyyarmory_0.1.1.py - edit the patch, never this file.
Every 0.1.1 check below still runs (patched where 0.1.2 changed the set on purpose: + the grapple files in the counts, the crossbow root
override, 35 classes, 7 systems, the grapple rows, the trav.staminaCap default 5 - the 0.1.1 traversal checks N2-N7 pin the cap at 10 to keep
their numbers, N8 / G2 check 5; the live-copy start now runs the one-time Stamina cap update). NEW sections EXECUTE the grapple:
  P9  (Python, spec 5 T1) the root override (= our chain only, the vanilla click rules), the EffectCondition / ApplyEffect / Projectile chain, the
      bolt config (Arrow_Base resolved + 60 / 6, rests, miss = sound only, hit = sound + despawn), no damage / block break / Ammo / inventory /
      stat change in any grapple file, OUT Infinite + CLICK 0.5 s, the model + rope trail + rope dots, ids.
  E/D/C (engine) + the Projectile interaction / Standard physics codecs, the ProjectileConfig + EntityEffect stores; the root override compiles
      (RootInteraction.build: EffectCondition -> ApplyEffect | Projectile, no missing step).
  Q   (JVM, spec 5 T2-T5 + Skyy's answers) GrappleMath on numbers; on REAL engine objects (StandardPhysicsProvider built from the decoded bolt
      config, ModelComponent, EffectControllerComponent with the decoded effects in the real store, EntityStatMap, Velocity, Damage) inside the
      0.1.1 map-backed Store / CommandBuffer: shoot -> record + OUT + the ImpactConsumer wrapped (and the engine's own still called); stuck ->
      full pull (3 + 1.5, regen pause, 24 b/s Sets, arrival hop, no fall damage while pulled / in grace); flying -> half pull (bolt gone, 2 + 1);
      let go = momentum (24 + 2 up), normal fall rules; hooks: skeleton yanked (NPC Set + dash config), cow + boss pull you, players never
      yanked unless the row + PvP + not party; Ammo untouched + no inventory call; short Stamina / Mana refused; no Mana pool = Stamina only;
      swap off / class lock / part off / cooldown / newest bolt / snaps / anchor / engine removal / world / death / stale effects / pull time /
      stall / rope / TravTick wiring; the rows + clamps + armory:grapple; the trav.staminaCap one-time update (text step + real migrate012).
Harness seams (null in the game): + Grapple.HAND (the item in hand).

0.1.1 harness: SkyyArmory 0.1.1 - test harness. GENERATED by tools/armory_0_1_1_patch.py from test_skyyarmory_0.1.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.1"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.1 SkyyArmory"',
     'VERSION = "0.1.2"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.2 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory011", "harness")', 'os.path.join(SCRATCH_ROOT, "armory012", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.1.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.2.py')
hrep('''check(len(J_INTS) == 115 and len(J_ROOTS) == 15 and len(J_PRJ) == 39, "P0: 115 interactions (0.1.1: no staff Stamina pair), 15 roots, 39 projectiles (+ 8 blink markers) (%d / %d / %d)" % (''',
     '''check(len(J_INTS) == 121 and len(J_ROOTS) == 16 and len(J_PRJ) == 39, "P0: 121 interactions (0.1.2: + 6 grapple), 16 roots (+ the crossbow root override), 39 projectiles (%d / %d / %d)" % (''')
hrep('''check(sorted(J_MODELS) == ["SkyyArmory_Marker", "SkyyArmory_QuickOrb"] and list(J_TRAILS) == ["SkyyArmory_Orb_Trail_Blue"] and len(J_PSYS) == 4 and len(J_PSP) == 7,''',
     '''check(sorted(J_MODELS) == ["SkyyArmory_Grapple_Bolt", "SkyyArmory_Marker", "SkyyArmory_QuickOrb"] and sorted(J_TRAILS) == ["SkyyArmory_Orb_Trail_Blue", "SkyyArmory_Rope_Trail"]
      and len(J_PSYS) == 5 and len(J_PSP) == 9,''')
hrep('''check(all(k.startswith("SkyyArmory_") or k == "Wand_Primary" for k in list(J_INTS) + list(J_ROOTS)) and "Wand_Primary" in J_INTS''',
     '''check(all(k.startswith("SkyyArmory_") or k in ("Wand_Primary", "Root_Weapon_Crossbow_Secondary_Guard") for k in list(J_INTS) + list(J_ROOTS)) and "Wand_Primary" in J_INTS''')
hrep('''            sets = ("Wand",) if "_Wand_" in i or i == "Wand_Primary" else ("Staff",)''',
     '''            sets = ("Wand",) if "_Wand_" in i or i == "Wand_Primary" else (("Crossbow",) if "_Grapple" in i else ("Staff",))''')
hrep('''PY_OKS, PY_FAILS = OKS[0], len(FAILS)''', HARNESS_P9.rstrip("\n") + "\n" + '''PY_OKS, PY_FAILS = OKS[0], len(FAILS)''')
hrep('''    check(len(names) == 29, "A: 29 classes (22 SkyyArmory incl. 0.1.1's 12 traversal classes + 7 kit)")''',
     '''    check(len(names) == 35, "A: 35 classes (28 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple classes + 7 kit)")''')
hrep('''    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC)''', '''    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC)
    # 0.1.2: the stores of the grapple's effect + bolt config - AssetRegistryLoader.init registers both (checked here)
    EFXc = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    PCFGc = JClass("com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig")
    check(AR.getAssetStore(EFXc.class_) is not None and AR.getAssetStore(PCFGc.class_) is not None,
          "E (0.1.2): the EntityEffect + ProjectileConfig asset stores exist (AssetRegistryLoader.init)")''')
hrep('''    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jfield(C_, "CODEC").get(None))''', '''    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jfield(C_, "CODEC").get(None))
    # 0.1.2: ProjectileModule.setup's registrations (read from its bytecode in the build): the "Projectile" interaction + the "Standard" physics
    PRJIc = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    INTc.CODEC.register("Projectile", PRJIc.class_, PRJIc.CODEC)
    SPCc = JClass("com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsConfig")
    JClass("com.hypixel.hytale.server.core.modules.projectile.config.PhysicsConfig").CODEC.register("Standard", SPCc.class_, SPCc.CODEC)''')
hrep('''"15 of 15 items, 115 of 115 interactions, 39 of 39 projectiles come from Skyy:0.1.1 SkyyArmory"''',
     '''"15 of 15 items, 121 of 121 interactions, 39 of 39 projectiles, 1 of 1 roots (the crossbow right click) come from Skyy:0.1.2 SkyyArmory"''')
hrep('''    check(not comp_bad and n_miss1 == n_miss0 and len(comp_rows) == 15,''', '''    # 0.1.2: the crossbow root override compiles to EffectCondition -> ApplyEffect (the click) | Projectile (the shot), no missing step
    res_x = compile_root("Root_Weapon_Crossbow_Secondary_Guard")
    cls_x = [(cn_, iid_) for cn_, iid_ in res_x["ops"] if iid_ is not None and not iid_.startswith("*")]
    ok_x = (not res_x["bad"] and ("EffectConditionInteraction", "SkyyArmory_Grapple") in cls_x and ("ApplyEffectInteraction", "SkyyArmory_Grapple_Click_Step") in cls_x
            and ("ProjectileInteraction", "SkyyArmory_Grapple_Shoot") in cls_x)
    if not ok_x:
        comp_bad.append("Root_Weapon_Crossbow_Secondary_Guard: bad %s, ops %s" % (res_x["bad"][:2], res_x["ops"]))
    n_miss1 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    check(not comp_bad and n_miss1 == n_miss0 and len(comp_rows) == 15,''')
hrep('''    NN = len(NEW_ROWS)
    check(keys[:10] == want_rows and keys[10:10 + NN] == NEW_ROWS and all(k.startswith("fixed.") or k in ("staff.stamina", "hop.mode") for k in keys[10 + NN:])
          and len(keys) == 10 + NN + 8 + 8 + 5 + 2,''', '''    NEW_ROWS += ["part.grapple", "grapple.ropeLength", "grapple.snapDistance", "grapple.anchorSeconds", "grapple.pullSpeed", "grapple.maxDown",
                 "grapple.ease", "grapple.stopDistance", "grapple.halfPercent", "grapple.pullMaxSeconds", "grapple.releaseKeep", "grapple.releaseLift", "grapple.arriveHop",
                 "grapple.landGrace", "grapple.stamina", "grapple.mana", "grapple.halfStamina", "grapple.halfMana", "grapple.regenPause", "grapple.rope",
                 "grapple.ropeSpacing", "grapple.cooldown", "grapple.yankSize", "grapple.bossWords", "grapple.noYankWords", "grapple.yankPlayers"]      # 0.1.2
    NN = len(NEW_ROWS)
    check(keys[:10] == want_rows and keys[10:10 + NN] == NEW_ROWS and all(k.startswith("fixed.") or k in ("staff.stamina", "hop.mode", "grapple.flight", "grapple.rightClick") for k in keys[10 + NN:])
          and len(keys) == 10 + NN + 8 + 8 + 5 + 2 + 2,''')
hrep('''        setf(p_, PBc, "dataDirectory", Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.1")))''',
     '''        setf(p_, PBc, "dataDirectory", Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.2")))''')
hrep('''    ready = [m_ for lv_, m_ in records()[n_log0:] if "[SkyyArmory] 0.1.1 ready" in m_]''', '''    ready = [m_ for lv_, m_ in records()[n_log0:] if "[SkyyArmory] 0.1.2 ready" in m_]''')
hrep('''    check(all(s1[k] == s0[k] for k in s0), "T: no other mod's file was touched by either start (byte + time identical)")''',
     '''    check(all(s1[k] == s0[k] for k in s0 if not k.startswith("Skyy_SkyyArmory")), "T: no other mod's file was touched by either start (byte + time identical)")
    # 0.1.2: the live COPY gets the one-time trav.staminaCap update on the first start (History copy + marker; Skyy's live file has no cap line =
    # the marker only, the new default 5 applies), nothing on the second start (the no-churn check below)
    kc_ = os.path.join("Skyy_SkyyArmory", "config.properties")
    if kc_ in s0:
        old_ = s0[kc_][0]
        want_ = str(ACfg.m12Update(old_.decode("latin-1"))[0]).encode("latin-1") if ACfg.m12Update(old_.decode("latin-1")) is not None else old_
        hb_ = sorted(k for k in s1 if k.startswith(os.path.join("Skyy_SkyyArmory", "config-history")) and k.endswith(".bak") and k not in s0)
        check(s1[kc_][0] == want_ and (want_ == old_ or (len(hb_) == 1 and s1[hb_[0]][0] == old_)) and str(ACfg.M12_MARK_ID) in s1[kc_][0].decode("latin-1"),
              "T (0.1.2): the live copy's config.properties got the one-time Stamina cap update on the first start (= the text step's result, the old bytes kept "
              "as a History version): %d -> %d bytes, %s" % (len(old_), len(s1[kc_][0]), hb_))''')
hrep('''    check(len(caps) == 2 and all(len(c) == 5 for c in caps) and [str(x.getClass().getSimpleName()) for x in caps[0]] == [
              "ArmoryTuneSys", "ArmorySpawnSys", "ArmoryTravSys", "ArmoryHitSys", "TravTick"] and bool(caps[0][0].ordered) and bool(caps[0][1].ordered),
          "T: setup() hands the registry exactly 5 systems (one registerSystem each; 0.1.1: + ArmoryTravSys, ArmoryHitSys, TravTick), tune + spawn ordered: %s" % (''',
     '''    check(len(caps) == 2 and all(len(c) == 7 for c in caps) and [str(x.getClass().getSimpleName()) for x in caps[0]] == [
              "ArmoryTuneSys", "ArmorySpawnSys", "ArmoryTravSys", "ArmoryHitSys", "TravTick", "GrappleBoltSys", "GrappleFallSys"] and bool(caps[0][0].ordered) and bool(caps[0][1].ordered),
          "T: setup() hands the registry exactly 7 systems (one registerSystem each; 0.1.2: + GrappleBoltSys, GrappleFallSys), tune + spawn ordered: %s" % (''')
hrep('''    trav_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.1 magic traversals: traversals on" in m_]
    check(len(trav_line) == 2 and "hook true, hits true, tick true" in trav_line[0], "T (0.1.1): the start line names the traversal numbers and the 3 systems: %s" % trav_line[:1])''',
     '''    trav_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.2 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_]
    check(len(trav_line) == 2 and "hook true, hits true, tick true" in trav_line[0], "T (0.1.1): the start line names the traversal numbers and the 3 systems: %s" % trav_line[:1])
    gr_line = [m_ for lv_, m_ in records()[n_log0:] if "0.1.2 crossbow grapple: grapple on" in m_]
    check(len(gr_line) == 2 and "systems: bolt true, fall true" in gr_line[0], "T (0.1.2): the grapple start line + its 2 systems: %s" % gr_line[:1])''')
hrep('''    # ---------------- N. 0.1.1 MAGIC TRAVERSALS - every new path EXECUTED (spec 5 T2-T4 + Skyy's section 8)
    ACfg.useDefaults()''', '''    # ---------------- N. 0.1.1 MAGIC TRAVERSALS - every new path EXECUTED (spec 5 T2-T4 + Skyy's section 8)
    ACfg.useDefaults()
    ACfg.STAMINA_CAP = 10          # 0.1.2: N2-N7 keep 0.1.1's numbers at the old cap 10 (the 0.1.2 default 5 is checked in N8, G2 and Q12)''')
hrep('''"quick.range.staff": "24", "quick.staffBonus": "15", "trav.staminaPercent": "50", "trav.staminaCap": "10"}''',
     '''"quick.range.staff": "24", "quick.staffBonus": "15", "trav.staminaPercent": "50", "trav.staminaCap": "5"}''')
hrep('''    check(len(a_s) == 11 and str(a_s[8]) == "Hold - blink 10 blocks + light trail - 10 Stamina" and str(a_s[9]) == "24 blocks" and float(a_s[10]) == 15.0
          and str(a_w[8]) == "Hold - hop back + burst 6 blocks + heal orb 9 blocks - 7.5 Stamina" and str(a_w[9]) == "pierces - 16 blocks" and float(a_w[10]) == 0.0''',
     '''    check(len(a_s) == 11 and str(a_s[8]) == "Hold - blink 10 blocks + light trail - 5 Stamina" and str(a_s[9]) == "24 blocks" and float(a_s[10]) == 15.0
          and str(a_w[8]) == "Hold - hop back + burst 6 blocks + heal orb 9 blocks - 5 Stamina" and str(a_w[9]) == "pierces - 16 blocks" and float(a_w[10]) == 0.0''')
hrep('''    check(trav_txt.startswith("traversals on (Stamina 50% of the Mana, cap 10) - staff hold blink 10 blocks")''',
     '''    check(trav_txt.startswith("traversals on (Stamina 50% of the Mana, cap 5) - staff hold blink 10 blocks")''')
hrep('''        ws_ = ["Charged shot - 30 Mana - %d damage at Lv 15" % fl(175 * ms_), "Hold - blink 10 blocks + light trail - 10 Stamina",''',
     '''        ws_ = ["Charged shot - 30 Mana - %d damage at Lv 15" % fl(175 * ms_), "Hold - blink 10 blocks + light trail - 5 Stamina",''')
hrep('''        ww_ = ["Charged shot - 15 Mana - %d damage at Lv 15" % fl(88 * mw_), "Hold - hop back + burst 6 blocks + heal orb 9 blocks - 7.5 Stamina",''',
     '''        ww_ = ["Charged shot - 15 Mana - %d damage at Lv 15" % fl(88 * mw_), "Hold - hop back + burst 6 blocks + heal orb 9 blocks - 5 Stamina",''')
hrep('''    # ---------------- L2. (last: it changes the store)''', HARNESS_Q.rstrip("\n") + "\n" + '''    # ---------------- L2. (last: it changes the store)''')
tout = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(tout)
print("wrote %s (%d lines)" % (os.path.relpath(TDST, ROOT), tout.count(TNL) + 1))
