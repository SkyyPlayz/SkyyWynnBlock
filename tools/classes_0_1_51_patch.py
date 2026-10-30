"""Derive SkyyClasses/build_skyyclasses_0.1.51.py from the GENERATED SkyyClasses 0.1.50 (build_skyyclasses_0.1.50.py = the tools/deploy_set.py
SET pin; the EDITED lineage: Skyy's hand-edited 0.1.6 (commit ab75b6c) -> classes_0_1_7_patch.py -> ... -> classes_0_1_51_patch.py).
Never re-run an older patch. Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.50
(tools/soundpass_gen.Patch). Line endings kept.
Run:  python tools/classes_0_1_51_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.51.py   (never --deploy)
      then  python SkyyClasses/test_skyyclasses_0.1.51.py
Pairs with SkyyMobs 0.1.23 (tools/mobs_0_1_23_patch.py: element mobs put their element state on players through classes:fn:elemHit).
"""
import os, sys, json, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyelem as EL

NOTE = '''0.1.51 (2026-10-30) = AUGMENTS ROUND A1 - THE ELEMENT EFFECTS ENGINE (research/Augments-Spec.md 4.2-5.5 + 6.1 A1; with SkyyMobs 0.1.23).
  Skyy (docs/answered/gear.md 2026-10-25 AUGMENTS REPLACE POWDERS = D1): "fire will set the enemy on fire, lightning can stager them. air does
  more knock back ... water would put out a burning enemy, but lighting and ice are more effective against a wet enemy. wind and fire combo
  ... increasing the intensity and length of the fire ... i want all the elements to interact realistically." + RAIN "Yes, with a setting"
  + POISON AUGMENT "add it as an augment. but its a weapon modifier. NOT an element." (Poison takes part in no state / reaction here).
  1. NEW BRIDGE classes:fn:elemHit apply(Object[]{ UUID attacker, UUID victim, int[] power5, double[] parts5, Double hit, Boolean heavy
     [, String world] }) -> Boolean queued. power5 / parts5 in the Wynn bridge order of tools/skyyelem.py NAMES (0 Earth, 1 Thunder,
     2 Water, 3 Fire, 4 Air): power = the element's Power on that hit (1-10, clamped; 0 = that element puts no state), parts = that hit's
     element part AFTER the mob's Weak / Resist (the reactions are a % of it). Any thread: it only validates and queues a world job
     (kind 29, the classes:fn:dot pattern; the DoT job cap - 8 x abil.maxLive - drops the rest); every state change runs on the victim's
     world thread (AbilTick). Missing world = the attacker's (or the victim's) player world. Nothing calls it yet in this round: A2 adds the
     SkyyGear caller (its weapon hits) and publishes Boolean gear:elemStates - then Classes stops its own weapon-hit Imbue status (Gear
     sends Imbue's Power 5 itself; the engine also takes max(Power, 5) while Imbue of that element runs - spec 4.3, one state a hit).
  2. THE STATES (spec 5.1; on mobs and players; Power P -> s = min(P, 10) / 5): Burning (DoT: a bridge hit 2 % of the hit a second x s, a
     class hit the old ab.Elements burnPct; 4 s, 3 stacks; the look = SkyyElem_Burning, a damage-free child of vanilla Burn_Template),
     Wet (NEW: 6 s, no damage, Burning can't start; the look SkyyElem_Wet; also while standing in water and - elem.rainWet - out in rain),
     Chilled (-15 % x s speed 3 s) -> 3 Chills in 3 s = Frozen 1.5 s (Classes' freezeOne), Shocked (+5 % x s damage taken 3 s; 30 % x s of
     the Thunder part jumps to the nearest enemy within 3; FLINCH - vanilla Hit_Interrupt_Flinch 0.25 s - on every 2nd Thunder hit),
     Quaked (was "Stagger": every 3rd Earth hit 0.4 s stun + -10 % x s Defence 4 s), Gusted (+1 x s block knockback, heavy hits lift;
     Windswept 2 s). A mob never gets its OWN element's state (SkyyMobs mob:fn:elemOf: a Fire mob never burns, a Water mob is always Wet).
  3. THE INTERACTION MATRIX (spec 5.2, Poison not in it): STEAM, DOUSE, MELT, THAW, FANNED, ELECTROCUTE, GROUNDED, STORM, CONDUCT, MUD,
     SMOTHER, SHATTER, SANDBLAST, WILDFIRE, WIND CHILL - each as the spec's row; reaction damage = round(part x %), its own Damage with the
     element's cause (never crits, never a weapon hit, never a second reaction: Classes' hooks skip its own tagged damage).
  4. ORDER INSIDE ONE HIT (spec 5.3): the states are snapshot first; Earth, Thunder, Water, Fire, Air each check the SNAPSHOT (a hit never
     reacts with a state it puts on itself); each reaction has a cooldown per target (reactCd 1 s); one reaction word a hit (the strongest)
     - a CombatTextUpdate to the attacker only (elem.popup; UNVERIFIED that a send outside the damage group shows).
  5. BOSSES + PLAYERS (spec 5.4 / 5.5): a boss (abil.bossWords) takes stun / freeze / flinch x ab.Elements bossCc 50 %, then 8 s CC
     immunity, flinches at most once in 4 s, never knockback; DoT and reaction damage in full. A player victim (elem.players: an element
     mob's hit through SkyyMobs, or a player's hit where the world's PvP is on and they are not in one party): CC x 50 %, knockback x 60 %,
     then 5 s CC immunity; every state time x S / (S + D) with D = their element Defence (gear:fn:elemDef) - the damage curve. A normal mob:
     after a hard CC (stun / freeze) ccGap 1.5 s before the next (fast weapons can't chain-lock), a flinch at most once a second.
  6. NO DOUBLE COUNT (spec 4.3): one state application per element per hit - a second path for the same attacker + element within
     sameHit 0.1 s is the same hit; Spellblade Imbue (and every other class status: Tempest, Bubble, the Imbue crescent / burst) runs
     THROUGH the engine (statusOn -> elemClass, Power 5 x Momentum's strength) - elem.on OFF = the 0.1.50 statuses exactly.
  7. SERVER SETUP (Classes -> Abilities): elem.on, elem.rainWet (Skyy "Yes, with a setting"), elem.rainWeathers (the weather ids that make
     you Wet - from Assets.zip: every Rain / Storm weather but sand, ash, snow and void storms), elem.players, elem.popup; numbers rows
     ab.ElemStates.numbers + ab.Reactions.numbers (Spellblade abilities tab, a missing key = its default).
  SAVED DATA: none (states live in memory only; new rows read their defaults while missing - no migration). New classes ElemSt (one
  victim's states), ElemCtx (one hit), ElemHitFn (the bridge); no new system / command. Two new effect assets (SkyyElem_Burning,
  SkyyElem_Wet). ROLLBACK to 0.1.50: alone is safe (no caller of classes:fn:elemHit exists before A2; 0.1.50 ignores the new rows);
  with A2 deployed: Gear's ready line says "element states off" and damage still works.
  FIX 2 (second critic pass, 2026-10-30): gearStates() needs elem.on (OFF = the 0.1.50 Imbue path, whatever SkyyGear published - A2 must also
  drop / flip gear:elemStates on its shutdown and its own elem.on edit); a BOSS "flinch" is only vanilla's attack-start block
  (Hit_Interrupt_Stunned - Hit_Interrupt_Flinch plays the Hurt animation in the Action slot and could cut a started wind-up, spec 5.4), never
  while vanilla's Hit_Interrupt_Enraged protection runs, and it spends no CC immunity (the 4 s bossFlinch gap bounds it - the row is live);
  Frozen ends with the REAL hold when the boss clock cut it; the flood prune keeps live CC immunity / flinch clocks; rain needs an open sky
  (the column's heightmap top block at or below the feet - under a roof / in a cave you stay dry); Electrocute + the bridge jumps + Conduct /
  Storm deal "ElemArc" (Lightning cause, NO second Weak / Resist - the part already has it; the class Shock jump keeps 0.1.50's ElemShock);
  a jump recipient is hit at most once per reactCd (an AoE can't stack chains) and gets 0.1.50's +5 % damage taken, never the Shocked state
  (no chain of chains); Storm widens Electrocute's chain too and is only spent when a jump uses it; Wildfire fans only the Burning stacks of
  the SNAPSHOT that still burn (Douse / Smother earlier in the hit -> no Wildfire; a stack this hit lit is never fanned); queued element hits
  have their own cap (8 x abil.maxLive kind 29 jobs - live Burning stacks never block them); shockPart = the Thunder part, renewed by every
  Shock; Electrocute / Conduct look up a stateless bystander's water / rain once a hit, at most 32 lookups a hit; Sandblast weaken 0 = off.
  KEPT (spec drift, recorded): a player's flinch = flinchTime 0.25 x pvpCc 50 % = 0.125 s (spec 5.5 says 0.15 s; one rule, both rows in
  Server Setup). Mud slow stays max 30 % (the engine's slow effects stop at -30 %).

'''

P = G.Patch(os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.50.py"), os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.51.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.50"') and P.s.startswith('"""SkyyClasses 0.1.50 - build script') and P.has("ShadowMark") and not P.has("ElemSt"), "not the SET pin 0.1.50"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyyClasses 0.1.50 - build script (javassist via jpype). GENERATED by tools/classes_0_1_50_patch.py from the generated 0.1.49 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_50_patch.py) - edit the patch, not this file.
Run: python SkyyClasses/build_skyyclasses_0.1.50.py -> SkyyClasses/SkyyClasses-0.1.50.jar (never --deploy). Test: python SkyyClasses/test_skyyclasses_0.1.50.py
''', '''"""SkyyClasses 0.1.51 - build script (javassist via jpype). GENERATED by tools/classes_0_1_51_patch.py from the generated 0.1.50 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_51_patch.py) - edit the patch, not this file.
Run: python SkyyClasses/build_skyyclasses_0.1.51.py -> SkyyClasses/SkyyClasses-0.1.51.jar (never --deploy). Test: python SkyyClasses/test_skyyclasses_0.1.51.py
''' + NOTE + '''=== 0.1.50 (history) ===
''')
P.rep('VERSION = "0.1.50"', 'VERSION = "0.1.51"')

# ================================================================================================ 7. the switch rows (Classes -> Abilities)
with zipfile.ZipFile(os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "install", "release", "package", "game",
                                  "latest", "Assets.zip")) as _az:          # read-only
    _wx = sorted(n.rsplit("/", 1)[1][:-5] for n in _az.namelist() if n.startswith("Server/Weathers/") and n.endswith(".json"))
RAIN_IDS = [w for w in _wx if ("rain" in w.lower() or "storm" in w.lower()) and not any(x in w.lower() for x in ("sand", "ash", "snow", "void"))]
assert "Zone1_Rain" in RAIN_IDS and "Zone1_Storm" in RAIN_IDS and "Zone2_Sand_Storm" not in RAIN_IDS and "Zone3_Snow_Storm" not in RAIN_IDS \
    and "Zone4_AshWastes_Storm" not in RAIN_IDS and len(",".join(RAIN_IDS)) <= 400, RAIN_IDS
RAIN_TEXT = ",".join(RAIN_IDS)
P.rep('''_r("abil.echoDelay", "ECHO_DELAY", "dec", 1.0, "0.2", "10", "s", "abill", "Echo delay", "Seconds from the cast (or its end) to the echo.")
''', '''_r("abil.echoDelay", "ECHO_DELAY", "dec", 1.0, "0.2", "10", "s", "abill", "Echo delay", "Seconds from the cast (or its end) to the echo.")
# 0.1.51 (Augments A1, research/Augments-Spec.md 5): the element states engine - the switches (numbers: ab.ElemStates / ab.Reactions)
_r("elem.on", "ELEM_ON", "bool", True, "", "", "", "abil", "Element states + reactions",
   "Off: element hits only deal damage; class statuses (Spellblade Imbue...) work as before 0.1.51.")
_r("elem.rainWet", "ELEM_RAIN", "bool", True, "", "", "", "abil", "Rain makes you Wet",
   "On: players and mobs out in rain or a storm are Wet (no Burning; Thunder + Water hit harder).")
_r("elem.rainWeathers", "ELEM_RAINIDS", "text", %r, "", "400", "", "abil", "Weathers that make you Wet",
   "Weather ids, comma separated (any case). Sand, ash, snow and void storms are left out.")
_r("elem.players", "ELEM_PVP", "bool", True, "", "", "", "abil", "Element states on players",
   "On: element mobs (and players where PvP is on) put states on players: half CC, 5 s immunity.")
_r("elem.popup", "ELEM_POP", "bool", True, "", "", "", "abil", "Reaction words (element states)",
   "On: STEAM, SHATTER, ELECTROCUTE ... show over the enemy for the player who caused them.")
''' % RAIN_TEXT)

# ================================================================================================ the numbers rows (ab.ElemStates / ab.Reactions)
EX_NUMS = [("wetTime", 6.0, "0", "60"), ("burnPct", 2.0, "0", "100"), ("shockPct", 30.0, "0", "200"), ("flinchEvery", 2.0, "1", "20"),
           ("flinchTime", 0.25, "0", "2"), ("flinchGap", 1.0, "0", "30"), ("bossFlinch", 4.0, "0", "60"), ("ccGap", 1.5, "0", "30"),
           ("bossImmune", 8.0, "0", "60"), ("pvpCc", 50.0, "0", "100"), ("pvpKb", 60.0, "0", "100"), ("pvpImmune", 5.0, "0", "60"),
           ("reactCd", 1.0, "0", "30"), ("sameHit", 0.1, "0", "1"), ("chainRange", 4.0, "0", "16"), ("chainMax", 3.0, "0", "10"),
           ("windswept", 2.0, "0", "30"), ("mudSlow", 25.0, "0", "30"), ("mudTime", 3.0, "0", "30"), ("sandWeaken", 10.0, "0", "40"),
           ("sandTime", 3.0, "0", "30"), ("fanStacks", 4.0, "1", "10"), ("envEvery", 1.0, "0.25", "10")]
RX_NUMS = [("steam", 25.0), ("douse", 25.0), ("melt", 50.0), ("shatter", 50.0), ("electrocute", 50.0), ("elecFlinch", 0.4), ("grounded", 30.0),
           ("sandblast", 20.0), ("fanned", 50.0), ("fanBurn", 25.0), ("fanTime", 50.0), ("stormJumps", 1.0), ("stormRange", 2.0),
           ("wildRange", 3.0), ("classPart", 30.0)]
# FIX (critic: the raw key was the only label + help): a real label + one help line per row (players / mobs / Gear's A2 hits all use them)
EX_TXT = {"wetTime": ("Wet time (s)", "How long a Water hit keeps a target Wet."), "burnPct": ("Burning % of the hit / s", "Augment / mob hits: Burning a second, % of the hit (x Power / 5). Class statuses: Element statuses."),
          "shockPct": ("Shock jump %", "Augment / mob hits: % of the Thunder part that jumps on. Class statuses: Element statuses."), "flinchEvery": ("Flinch every Nth Thunder hit", "Every Nth Thunder hit on a target flinches it."),
          "flinchTime": ("Flinch time (s)", "How long a Thunder flinch stops the target."), "flinchGap": ("Flinch gap (s)", "A normal mob flinches at most once in this time."),
          "bossFlinch": ("Boss flinch gap (s)", "A boss flinches at most once in this time."), "ccGap": ("Normal mob CC gap (s)", "After a stun / freeze, a normal mob is free this long."),
          "bossImmune": ("Boss CC immunity (s)", "After a stun / freeze / flinch, a boss is immune this long."), "pvpCc": ("Player CC %", "Stun / freeze / flinch / slow on players, % of the mob time."),
          "pvpKb": ("Player knockback %", "Air knockback on players, % of the mob push."), "pvpImmune": ("Player CC immunity (s)", "After a CC or a push, a player is immune this long."),
          "reactCd": ("Reaction cooldown (s)", "The same reaction on the same target at most once in this time."), "sameHit": ("Same hit window (s)", "One attacker's same element twice in this time = one hit."),
          "chainRange": ("Chain range (blocks)", "Electrocute / Conduct jump to Wet enemies this close."), "chainMax": ("Chain jumps", "Most enemies one Electrocute / Conduct reaches."),
          "windswept": ("Windswept time (s)", "How long an Air hit leaves a target Windswept."), "mudSlow": ("Mud slow %", "Mud's speed cut (the slow effects stop at 30 %)."),
          "mudTime": ("Mud time (s)", "How long Mud slows."), "sandWeaken": ("Sandblast weaken %", "Sandblast: the target deals this % less (0 = off, 1-9 count as 10)."),
          "sandTime": ("Sandblast time (s)", "How long Sandblast weakens."), "fanStacks": ("Fanned Burning stacks", "Burning stacks a Windswept / fanned target can hold."),
          "envEvery": ("Water / rain check (s)", "How often a target's water / rain is looked up (cost).")}
RX_TXT = {"steam": ("Steam %", "Fire on Wet: % of the Fire part."), "douse": ("Douse %", "Water on Burning: % of the Water part."),
          "melt": ("Melt %", "Fire on Frozen: % of the Fire part."), "shatter": ("Shatter %", "Earth on Frozen: % of the Earth part."),
          "electrocute": ("Electrocute %", "Thunder on Wet: % of the Thunder part."), "elecFlinch": ("Electrocute flinch (s)", "Electrocute's sure flinch."),
          "grounded": ("Grounded %", "Earth + Thunder: % of the part."), "sandblast": ("Sandblast %", "Earth + Air: % of the part."),
          "fanned": ("Fanned time +%", "Fire on Windswept: Burning lasts this % longer."), "fanBurn": ("Wildfire burn +%", "Air on Burning: each stack burns this % harder (once)."),
          "fanTime": ("Wildfire time +%", "Air on Burning: each stack lasts this % longer (once)."), "stormJumps": ("Storm extra jumps", "Thunder + Air: extra Shock jumps."),
          "stormRange": ("Storm extra range (blocks)", "Thunder + Air: extra jump range."), "wildRange": ("Wildfire spread range (blocks)", "Air on Burning: the fire spreads this far."),
          "classPart": ("Class element part %", "Class statuses (Imbue...): % of the hit counted as the element part.")}
assert set(EX_TXT) == set(k for k, _d, _l, _h in EX_NUMS) and set(RX_TXT) == set(k for k, _d in RX_NUMS)
# FIX 2 (critic: two overlapping row sets, the old ones labelled with their raw keys): the 0.1.50 ab.Elements rows get a real label + a help
# line that says which hits use them ("class" = Imbue / Bubble / Tempest...; "all" = every element hit, augments and mobs too)
EL_TXT = {"burnPct": ("Class Burning % of the hit / s", "Class statuses: Burning a second, % of the hit. Augments: Element states."),
          "burnTime": ("Burning time (s)", "All element hits: how long Burning lasts."), "burnStacks": ("Burning stacks", "All element hits: Burning stacks a target holds."),
          "chillSlow": ("Chill slow %", "All element hits: Chilled speed cut (x Power / 5)."), "chillTime": ("Chill time (s)", "All element hits: how long Chilled lasts."),
          "freezeAt": ("Chills to freeze", "All element hits: Chills within the window that freeze."), "freezeWindow": ("Freeze window (s)", "All element hits: the Chills count within this time."),
          "freezeTime": ("Freeze time (s)", "All element hits: how long Frozen lasts."), "staggerEvery": ("Quake every Nth Earth hit", "All element hits: every Nth Earth hit quakes."),
          "staggerTime": ("Quake stun (s)", "All element hits: the Quake's stun."), "staggerDef": ("Quake Defence cut %", "All element hits: Defence cut while Quaked."),
          "staggerDefTime": ("Quake Defence time (s)", "All element hits: how long the Defence cut lasts."),
          "shockPct": ("Class Shock jump % of the hit", "Class statuses: % of the hit that jumps on. Augments: Element states."),
          "shockRange": ("Shock jump range (blocks)", "All element hits: the Shock jump's reach."), "shockVuln": ("Shock damage taken +%", "All element hits: Shocked targets take this % more."),
          "shockTime": ("Shock time (s)", "All element hits: how long Shocked lasts."), "gustUp": ("Gust lift (blocks)", "All element hits: a heavy Air hit lifts this much."),
          "gustKb": ("Gust knockback (blocks)", "All element hits: extra Air knockback (x Power / 5)."), "poisonPct": ("Class Poison % of the hit / s", "Class Poison status: damage a second, % of the hit."),
          "poisonTime": ("Class Poison time (s)", "Class Poison status: how long it lasts."), "bossCc": ("Boss CC %", "All element hits: stun / freeze / flinch / slow on bosses, % of the mob time."),
          "bothBonus": ("Both elements bonus %", "Class statuses: the bonus when both elements hit.")}
import re as _re
for _k, (_lb, _hp) in EL_TXT.items():
    _m = [m_ for m_ in _re.finditer(r'^_n\("ab\.Elements\.%s", .*"abilsb", "%s", "%s"\)$' % (_k, _k, _k), P.s, _re.M)]
    assert len(_m) == 1, _k
    P.rep(_m[0].group(0), _m[0].group(0)[:-len('"%s", "%s")' % (_k, _k))] + '"%s", "%s")' % (_lb, _hp))
_ex_src = "".join('    _n("ab.ElemStates.%s", "EX_%s", "dec", %r, %r, %r, "", "abilsb", %r, %r)\n' % (k, k.upper(), d, lo, hi, EX_TXT[k][0], EX_TXT[k][1]) for k, d, lo, hi in EX_NUMS)
_rx_src = "".join('    _n("ab.Reactions.%s", "RX_%s", "dec", %r, "0", "1000", "", "abilsb", %r, %r)\n' % (k, k.upper(), d, RX_TXT[k][0], RX_TXT[k][1]) for k, d in RX_NUMS)
P.rep('''    _n("ab.Capstones2." + _k, _f, "dec", _d, _lo, _hi, "", "abilx", _k, _k)
''', '''    _n("ab.Capstones2." + _k, _f, "dec", _d, _lo, _hi, "", "abilx", _k, _k)
# 0.1.51 (Augments A1): the element states engine numbers (s / % / blocks; research/Augments-Spec.md 5) + the reaction % / s / blocks
if True:
''' + _ex_src + _rx_src)
P.rep('''                                  + ['ShadowMark', 'Capstones2'])   # 0.1.50: Shadow Mark + the per-path capstones''',
      '''                                  + ['ShadowMark', 'Capstones2']   # 0.1.50: Shadow Mark + the per-path capstones
                                  + ['ElemStates', 'Reactions'])   # 0.1.51: the element states engine (Augments A1)''')
P.rep('''{'Momentum': 'Momentum', 'Elements': 'Element statuses',''', '''{'ElemStates': 'Element states', 'Reactions': 'Element reactions', 'Momentum': 'Momentum', 'Elements': 'Element statuses',''')
P.rep('''["Momentum", "Elements", "ClassTree", "Capstones", "Capstones2"] else''', '''["Momentum", "Elements", "ClassTree", "Capstones", "Capstones2", "ElemStates", "Reactions"] else''')
P.rep('''if _aid in ("Momentum", "Elements") else''', '''if _aid in ("Momentum", "Elements", "ElemStates", "Reactions") else''')

# ================================================================================================ particles + the two look effects
P.rep('''      "FX_ARC": "Sword_Charged_Trail_Blade", "FX_ARC_WING": "Mace_Signature_Slash", "FX_ARC_HIT": "Impact_Sword_Charged", "FX_ARC_WALL": "Impact_Sword_Signature"}''',
      '''      "FX_ARC": "Sword_Charged_Trail_Blade", "FX_ARC_WING": "Mace_Signature_Slash", "FX_ARC_HIT": "Impact_Sword_Charged", "FX_ARC_WALL": "Impact_Sword_Signature",
      # 0.1.51 (Augments A1): the element states + reactions (finite one-shots, checked below like the others)
      "FX_WET": "Water_Splash_Soft", "FX_STEAM": "Water_Splash", "FX_MUD": "Block_Hit_Mud", "FX_SAND": "Block_Hit_Sand", "FX_ICEBRK": "Block_Break_Ice",
      "FX_ZAP": "Dungeon_Goblin_Electric_Fence_Hit", "FX_BOLT2": "Lightning", "FX_STONE": "Block_Hit_Stone"}''')
P.rep('''for _id in EF_IDS:
    assert not [n for n in _azn if n.rsplit("/", 1)[-1].split(".")[0] == _id], "vanilla already has an asset named " + _id
''', '''# 0.1.51 (Augments A1, probe X1): the Burning look = a damage-free child of vanilla Burn_Template (its ApplyConditions - no fire in water,
# Immunity_Fire, players in Adventure only - come with the Parent; the damage stays our DoT) + the NEW Wet look (a blue tint, no damage)
_bt = json.loads(_ASSETS.read("Server/Entity/Effects/Status/Burn_Template.json").decode("utf-8-sig"))
_bn = json.loads(_ASSETS.read("Server/Entity/Effects/Status/Burn.json").decode("utf-8-sig"))
assert _bn.get("Parent") == "Burn_Template" and [c_.get("Id") for c_ in _bt["ApplyConditions"]][:2] == ["InFluid", "HasEffect"] and "DamageCalculator" not in _bt, \\
    "0.1.51: vanilla Burn is no longer a child of Burn_Template (its no-fire-in-water rule)"
EF_FLINCH_ID = "Hit_Interrupt_Flinch"
EF_INTERRUPT_ID = "Hit_Interrupt_Stunned"          # FIX (critic: the walk-stop alone shows nothing): vanilla's "block attack starts" status
_hs = json.loads(_ASSETS.read("Server/Entity/Effects/Status/%s.json" % EF_INTERRUPT_ID).decode("utf-8-sig"))
assert "DamageCalculator" not in _hs and not _hs.get("ApplicationEffects") and _hs.get("Infinite") is False, "0.1.51 fix: vanilla Hit_Interrupt_Stunned changed"
assert "Server/Entity/Effects/Status/%s.json" % EF_FLINCH_ID in _azn and json.loads(_ASSETS.read("Server/Entity/Effects/Status/%s.json" % EF_FLINCH_ID).decode("utf-8-sig"))["ApplicationEffects"]["HorizontalSpeedMultiplier"] == 0, \\
    "0.1.51: the vanilla flinch (a short walk stop) moved"
assert "Server/Entity/Effects/Status/Hit_Interrupt_Enraged.json" in _azn, "0.1.51 fix 2: vanilla's anti-stunlock window (Hit_Interrupt_Enraged) moved"
EF_IDS += ["SkyyElem_Burning", "SkyyElem_Wet"]
RUNE_FILES["Server/Entity/Effects/SkyyClasses/SkyyElem_Burning.json"] = json.dumps({
    "Parent": "Burn_Template", "ApplicationEffects": dict(_bn["ApplicationEffects"]), "OverlapBehavior": "Overwrite", "Infinite": False,
    "Debuff": True, "StatusEffectIcon": _bn["StatusEffectIcon"], "Duration": 4}, indent=2)
RUNE_FILES["Server/Entity/Effects/SkyyClasses/SkyyElem_Wet.json"] = json.dumps({
    "Duration": 6, "OverlapBehavior": "Overwrite", "Debuff": True,
    "ApplicationEffects": {"EntityTopTint": "@WETTINT@", "EntityBottomTint": "#0b2a4a"}}, indent=2)
for _id in EF_IDS:
    assert not [n for n in _azn if n.rsplit("/", 1)[-1].split(".")[0] == _id], "vanilla already has an asset named " + _id
'''.replace("@WETTINT@", EL.COLORS["Water"]))

# ================================================================================================ engine tokens + probes
P.rep('''    "BMAT": "com.hypixel.hytale.protocol.BlockMaterial",
}
''', '''    "BMAT": "com.hypixel.hytale.protocol.BlockMaterial",
}
# 0.1.51 (Augments A1): water (the SkyyFishing block read), rain (the NPC's / the player's weather), the reaction words (SkyyGear's popups)
T.update({
    "FSC":  "com.hypixel.hytale.server.core.universe.world.chunk.section.FluidSection",
    "FLU":  "com.hypixel.hytale.server.core.asset.type.fluid.Fluid",
    "WSUP": "com.hypixel.hytale.server.npc.role.support.WorldSupport",
    "WTRK": "com.hypixel.hytale.builtin.weather.components.WeatherTracker",
    "WTH":  "com.hypixel.hytale.server.core.asset.type.weather.config.Weather",
    "EVW":  "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$EntityViewer",
    "CTU":  "com.hypixel.hytale.protocol.CombatTextUpdate",
    "PCOL": "com.hypixel.hytale.protocol.Color",
    "CHU":  "com.hypixel.hytale.math.util.ChunkUtil",          # fix 2: the open-sky check (SkyyExploration's heightmap read)
    "HMC":  "com.hypixel.hytale.server.core.universe.world.chunk.heightmap.HeightmapColumn",
})
''')
P.rep('''B.probe(pool, T["DCS"], "getAssetMap")          # 0.1.46: the tick causes by id
''', '''B.probe(pool, T["DCS"], "getAssetMap")          # 0.1.46: the tick causes by id
# 0.1.51 (Augments A1): every new engine member with the exact descriptor the element engine calls (read 2026-10-30, HytaleServer.jar)
for c, m, d in ((T["CHS"], "getChunkSectionReferenceAtBlock", "(III)Lcom/hypixel/hytale/component/Ref;"),
                (T["FSC"], "getFluidId", "(III)I"), (T["FSC"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (T["FLU"], "getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/IndexedLookupTableAssetMap;"),
                (T["WSUP"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (T["WSUP"], "getCurrentWeatherIndex", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/ComponentAccessor;)I"),
                (T["WTRK"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"), (T["WTRK"], "getWeatherIndex", "()I"),
                (T["WTH"], "getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/IndexedLookupTableAssetMap;"),
                (T["EVW"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (T["EVW"], "queueUpdate", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/protocol/ComponentUpdate;)V"),
                (T["WLD"], "getWorldConfig", "()Lcom/hypixel/hytale/server/core/universe/world/WorldConfig;"),
                ("com.hypixel.hytale.server.core.universe.world.WorldConfig", "isPvpEnabled", "()Z"),
                (T["UNI"], "getWorld", "(Ljava/util/UUID;)Lcom/hypixel/hytale/server/core/universe/world/World;"),
                (T["UNI"], "getWorld", "(Ljava/lang/String;)Lcom/hypixel/hytale/server/core/universe/world/World;"),          # fix: the bridge's world check
                (T["CHS"], "getChunkReference", "(J)Lcom/hypixel/hytale/component/Ref;"), (T["CHU"], "indexChunkFromBlock", "(II)J"),   # fix 2: open sky
                (T["HMC"], "getHeight", "(II)I"), (T["HMC"], "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset", "(I)Lcom/hypixel/hytale/assetstore/map/JsonAssetWithMap;")):
    assert str(pool.get(c).getMethod(m, d).getName()) == m, "0.1.51: %s.%s%s" % (c, m, d)
pool.get(T["CTU"]).getConstructor("(FLjava/lang/String;Lcom/hypixel/hytale/protocol/Color;)V")
pool.get(T["PCOL"]).getConstructor("(BBB)V")
for _c, _f in ((T["FLU"], "EMPTY_ID"), (T["DMG"], "NULL_SOURCE"), (T["EVW"], "visible")):
    assert pool.get(_c).getField(_f) is not None, "0.1.51: %s.%s" % (_c, _f)
''')

# ================================================================================================ AbilStore: the victims' element states
P.rep('''           "SMARKS", "SMCUT"):''', '''           "SMARKS", "SMCUT",
           # 0.1.51 (Augments A1): victim Ref -> ElemSt (its element states); role id -> long[] {own element (Wynn index, -1 none), until}
           "ELEMS", "ELEMOWN"):''')

# ================================================================================================ the bridge class (next to DotFn)
P.rep('''# 0.1.46 (elem1): classes:fn:dot (SkyyGear's Poison line through the ONE DoT engine; see the header)
abdot = pool.makeClass(PKG + ".DotFn")''', '''# 0.1.51 (Augments A1): classes:fn:elemHit (see the header) - validates + queues only (any thread)
elhit = pool.makeClass(PKG + ".ElemHitFn")
elhit.addInterface(pool.get("java.util.function.Function"))
C(elhit, "public ElemHitFn() { }")
M(elhit, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 6 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof java.util.UUID) || !(a[2] instanceof int[]) || !(a[3] instanceof double[])
        || !(a[4] instanceof Number)) return Boolean.FALSE;
    double h = ((Number) a[4]).doubleValue();
    if (Double.isNaN(h) || Double.isInfinite(h)) return Boolean.FALSE;
    boolean hv = a[5] instanceof Boolean && ((Boolean) a[5]).booleanValue();
    String w = a.length > 6 && a[6] instanceof String ? (String) a[6] : null;
    return Boolean.valueOf(@PKG@.Abil.elemWant((java.util.UUID) a[0], (java.util.UUID) a[1], (int[]) a[2], (double[]) a[3], h, hv, w));
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
# 0.1.46 (elem1): classes:fn:dot (SkyyGear's Poison line through the ONE DoT engine; see the header)
abdot = pool.makeClass(PKG + ".DotFn")''')

# ================================================================================================ Imbue (and every class status) through the engine
P.rep('''public static String statusOn(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, int e, double hv, double str, double dur, long now, boolean heavy) {
  if (t == null || cr == null || e < 0 || e > 5 || !enemy(cb, t, cr)) return null;
''', '''public static String statusOn(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, int e, double hv, double str, double dur, long now, boolean heavy) {
  if (t == null || cr == null || e < 0 || e > 5 || !enemy(cb, t, cr)) return null;
  if (@PKG@.AbilCfg.ELEM_ON && e <= 4) return elemClass(cb, t, cr, u, e, hv, str, dur, now, heavy);   // 0.1.51: the element states engine
''')
P.rep('''    if (imb != null) {
      String sr = imbueStatus(buf, t, att, u, amt, false, now);
      if (sr != null) out = out + " " + sr;
      if (imb[5] < 0.5) { imb[5] = 1.0; used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.IMBUE, null); }
    }''', '''    if (imb != null) {
      if (!gearStates()) {          // 0.1.51: SkyyGear (A2) sends this weapon hit's states itself (Imbue's Power 5 included) - one state a hit
        String sr = imbueStatus(buf, t, att, u, amt, false, now);
        if (sr != null) out = out + " " + sr;
      } else out = out + " gearstates";
      if (imb[5] < 0.5) { imb[5] = 1.0; used(u, @PKG@.ClassCfg.pkey(u), @PKG@.AbilDefs.IMBUE, null); }
    }''')
# FIX (critic: the player texts still said Chill / Stagger): every text that names an element's status says the engine's state while elem.on
# is on (Burning, Wet / Chill, Quake, ...) - elem.on OFF = the 0.1.50 words (ELS). statusOn's own return word (logs) is unchanged.
for _ln in ('''  return "+Elemental Imbue: " + (which == 2 ? "second element " : "") + ELN[e] + " (" + ELS[e] + "). An Elemental sword in your hand uses its own element.";''',
            '''" % " + ELN[e] + " damage and " + ELS[e] + ".");''',
            '''  if (bubLocked(k)) return "Bubble element: " + ELN[e] + " (" + ELS[e] + ") - locked, a class respec frees it";''',
            '''  return "Bubble element: " + ELN[e] + " (" + ELS[e] + ") - Change picks; your next bubble locks it";''',
            '''  return "+Elemental Bubble: " + ELN[e] + " (" + ELS[e] + "). Your next Shield Bubble locks it until a class respec.";''',
            '''    return " Elemental: " + ELN[e] + " (" + ELS[e] + ") - now locked until a class respec.";''',
            '''  return " Elemental: " + ELN[e] + " (" + ELS[e] + ").";'''):
    P.rep(_ln, _ln.replace("ELS[e]", "elsOf(e)"))
# the Burning DoT reaches players (an element mob's / a PvP hit); it ends in water; a job ended from outside (left 0) deals no last tick
P.rep('''public static boolean dotTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  @REF@ cr = casterRef(cb, j.caster);
  if (cr == null || !cr.isValid() || !(j.tref instanceof @REF@)) { j.left = 0; return false; }
  @REF@ t = (@REF@) j.tref;
  if (!enemy(cb, t, cr)) { j.left = 0; return false; }
  hit(cb, t, cr, j.caster, j.amount, j.what);''', '''public static boolean dotTick(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (j.left <= 0) return false;          // 0.1.51: ended from outside (Douse / Smother / Steam / water)
  @REF@ cr = casterRef(cb, j.caster);
  boolean eb = "ElemBurn".equals(j.what);          // 0.1.51: the engine's Burning
  // FIX (critic: a player's Burning went out the moment the Fire mob that lit it died / despawned / its PvP attacker logged out): Burning
  // ON A PLAYER keeps ticking without its caster (a non-entity source, elem.on + elem.players, alive, not creative)
  boolean orphan = eb && (cr == null || !cr.isValid()) && j.tref instanceof @REF@ && isPl(cb, (@REF@) j.tref);
  if (!orphan && (cr == null || !cr.isValid() || !(j.tref instanceof @REF@))) { j.left = 0; return false; }
  @REF@ t = (@REF@) j.tref;
  if (orphan ? !elemBurnLone(cb, t) : (eb ? !elemBurnOk(cb, t, cr, j.caster) : !enemy(cb, t, cr))) { j.left = 0; return false; }
  if (eb && elemInWater(cb, t, now)) { j.left = 0; elemBurnEnd(t); return false; }
  if (orphan) envHit(cb, t, j.caster, j.amount, "ElemBurn");
  else if (eb) elemTick(cb, t, cr, j.caster, j.amount);
  else hit(cb, t, cr, j.caster, j.amount, j.what);''')
P.rep('''  if (j.kind == 28) return dotRun(j, st, cb, now);   // 0.1.46: classes:fn:dot (SkyyGear's Poison line)''',
      '''  if (j.kind == 28) return dotRun(j, st, cb, now);   // 0.1.46: classes:fn:dot (SkyyGear's Poison line)
  if (j.kind == 29) return elemJob(j, st, cb, now);   // 0.1.51: classes:fn:elemHit (the element states engine)''')
P.rep('''    if (j.kind == 26 || j.kind == 28) n++;''', '''    if (j.kind == 26 || j.kind == 28 || j.kind == 29) n++;          // 0.1.51: + queued element hits''')
# FIX 2 (critic: 128 burning mobs x 3 live Burning stacks filled the shared DoT cap and every new element hit - Douse / Smother too - was
# dropped): the queued element hits (kind 29, run next tick) have their OWN cap, 8 x abil.maxLive of them
P.rep('''M(abworld, "public synchronized boolean idle() {''', '''M(abworld, r"""
public synchronized boolean elemFull() {
  prune(System.currentTimeMillis());
  int n = 0;
  for (int i = 0; i < this.jobs.size(); i++) if (((@PKG@.AbilJob) this.jobs.get(i)).kind == 29) n++;
  return (long) n >= 8L * (long) @PKG@.AbilCfg.MAX_LIVE;
}""")   # 0.1.51 fix 2: the element-hit queue's own cap
M(abworld, "public synchronized boolean idle() {''')
P.rep('''  if ("ElemPoison".equals(what)) return "Poison";''', '''  if ("ElemPoison".equals(what)) return "Poison";
  if ("ElemSteam".equals(what)) return "Water";          // 0.1.51: the reactions' own damage (each its element's cause)
  if ("ElemFlare".equals(what)) return "Fire";
  if ("ElemShatter".equals(what) || "ElemSand".equals(what)) return "Earth";
  if ("ElemGround".equals(what) || "ElemArc".equals(what)) return "Lightning";          // fix 2: ElemArc = Electrocute / jumps, no 2nd affinity
  if ("ElemGale".equals(what)) return "Wind";''')

# ================================================================================================ THE ENGINE (Abil late methods + ElemSt / ElemCtx)
ENGINE = r'''
# 0.1.51 (Augments A1): THE ELEMENT STATES ENGINE (header 0.1.51; research/Augments-Spec.md 5). Element index = the Wynn bridge order of
# tools/skyyelem.py NAMES (0 Earth, 1 Thunder, 2 Water, 3 Fire, 4 Air); E2W / W2E map Classes' ELN order (Fire Water Earth Thunder Air).
# ElemSt = one victim's states (world thread only); ElemCtx = one hit. Every method below runs on the victim's world thread.
elst = pool.makeClass(PKG + ".ElemSt")
for _f in ("public long seen;", "public int own;", "public long wetUntil;", "public long burnUntil;", "public long chillUntil;", "public long frozenUntil;",
           "public long[] chills;", "public long shockUntil;", "public double shockPart;", "public int thunderN;", "public long flinchAt;",
           "public int earthN;", "public long quakeUntil;", "public long gustUntil;", "public long ccFree;", "public long envAt;",
           "public boolean envWater;", "public boolean envRain;", "public long[] react;",
           # FIX (critic: one lastAtt slot let a second attacker's hit in between re-open the same-hit guard): a ring of the last 8
           # (attacker x element) keys + their times - the same attacker + element within sameHit is the same hit, whoever hit in between
           "public long[] ga;", "public long[] gt;", "public int gi;",
           "public long jumpAt;"):          # FIX 2: a chain jump hit this victim - no other jump until then (reactCd)
    F(elst, jv(_f))
C(elst, "public ElemSt() { this.own = -2; this.chills = new long[8]; this.react = new long[16]; this.ga = new long[8]; this.gt = new long[8]; this.gi = 0; }")
elctx = pool.makeClass(PKG + ".ElemCtx")
for _f in ("public @CB@ cb;", "public @REF@ t;", "public @REF@ cr;", "public java.util.UUID u;", "public boolean pv;", "public boolean pa;",
           "public boolean boss;", "public long now;", "public boolean heavy;", "public int src;", "public double dur;", "public double hit;",
           "public double[] res;", "public String word;", "public double wv;", "public int wc;", "public StringBuilder log;",
           "public java.util.HashSet jd;",          # FIX: every jump of ONE hit (Electrocute, Conduct, Storm, the Shock jump) shares one done set
           # FIX 2: a stateless bystander's water / rain answer once a hit (+ the lookups made); the Burning stacks of the SNAPSHOT
           "public java.util.HashMap envc;", "public int envn;", "public java.util.HashSet bj;"):
    F(elctx, jv(_f))
C(elctx, "public ElemCtx() { this.word = null; this.wv = -1.0; this.wc = -1; this.log = new StringBuilder(); this.jd = null; this.envc = null; this.envn = 0; this.bj = null; }")
RX_NAMES = ["STEAM", "DOUSE", "MELT", "THAW", "FANNED", "ELECTROCUTE", "GROUNDED", "STORM", "CONDUCT", "MUD", "SMOTHER", "SHATTER", "SANDBLAST",
            "WILDFIRE", "WIND CHILL"]
assert len(RX_NAMES) <= 16 and EL.NAMES == ["Earth", "Thunder", "Water", "Fire", "Air"]
_rgb = [tuple(int(EL.COLORS[_n][_i:_i + 2], 16) for _i in (1, 3, 5)) for _n in EL.NAMES]
for _f in ("public static volatile long ELEM_IN = 0L;", "public static volatile long ELEM_RUN = 0L;", "public static volatile long ELEM_DROP = 0L;",
           "public static volatile long ELEM_REACT = 0L;", "public static volatile long ELEM_POPS = 0L;", "public static volatile long ELEM_DMG = 0L;",
           "public static volatile String LAST_EL = \"\";",
           "public static volatile java.util.List POPS = null;",                         # HARNESS SEAM ONLY (null in the game = the CombatTextUpdate)
           "public static volatile java.util.function.Function ELEMENV = null;",        # HARNESS SEAM ONLY (null = the block / weather / PvP reads)
           "public static final int[] E2W = new int[] { 3, 2, 0, 1, 4 };",              # ELN index (Fire Water Earth Thunder Air) -> Wynn index
           "public static final int[] W2E = new int[] { 2, 3, 1, 0, 4 };",
           "public static final String[] WN = new String[] { " + ", ".join(jstr(_n) for _n in EL.NAMES) + " };",
           "public static final String[] RN = new String[] { " + ", ".join(jstr(_n) for _n in RX_NAMES) + " };",
           "public static final int[] ECR = new int[] { %s };" % ", ".join(str(_c[0]) for _c in _rgb),
           "public static final int[] ECG = new int[] { %s };" % ", ".join(str(_c[1]) for _c in _rgb),
           "public static final int[] ECB = new int[] { %s };" % ", ".join(str(_c[2]) for _c in _rgb),
           "public static final String EF_FLINCH = %s;" % jstr(EF_FLINCH_ID),
           "public static final String EF_INTERRUPT = %s;" % jstr(EF_INTERRUPT_ID),
           "public static final String EF_WETFX = \"SkyyElem_Wet\";", "public static final String EF_BURNFX = \"SkyyElem_Burning\";",
           # FIX: the engine's state names (ELN order Fire Water Earth Thunder Air Poison) for the player texts while elem.on is on
           "public static final String[] ELS2 = new String[] { \"Burning\", \"Wet / Chill\", \"Quake\", \"Shock\", \"Gust\", \"Poison\" };"):
    F(abil, _f)
ABIL_LATE += [
r"""
public static String elsOf(int e) {
  if (e < 0 || e >= ELS.length) return "";
  return @PKG@.AbilCfg.ELEM_ON && e < ELS2.length ? ELS2[e] : ELS[e];
}
""",
r"""
public static boolean gearStates() {
  if (!@PKG@.AbilCfg.ELEM_ON) return false;          // FIX 2 (critic): elem.on OFF = Classes' own 0.1.50 Imbue status, whatever SkyyGear published
  try { return Boolean.TRUE.equals(@PKG@.ClassCfg.bridge().get("gear:elemStates")); } catch (Throwable t) { return false; }
}
""",
r"""
public static boolean isPl(@CAC@ acc, @REF@ r) {
  try { return r != null && acc.getComponent(r, @PR@.getComponentType()) != null; } catch (Throwable t) { return false; }
}
""",
r"""
public static java.util.UUID elemUuid(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @PR@.getComponentType());
    return o instanceof @PR@ ? ((@PR@) o).getUuid() : null;
  } catch (Throwable t) { return null; }
}
""",
r"""
public static String elemWorld(java.util.UUID u) {
  try {
    @PR@ pr = prOf(u);
    if (pr == null) return null;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return null;
    @WLD@ w = @UNI@.get().getWorld(wu);
    return w == null ? null : w.getName();
  } catch (Throwable t) { return null; }
}
""",
r"""
public static boolean elemWorldReal(String n) {
  if (n == null) return false;
  if (@PKG@.AbilWorld.BY.containsKey(n)) return true;          // a world Classes already runs jobs in
  try { return @UNI@.get().getWorld(n) != null; } catch (Throwable t) { return false; }
}
""",
r"""
public static boolean elemWant(java.util.UUID a, java.util.UUID v, int[] pw, double[] pt, double hit, boolean heavy, String world) {
  if (!@PKG@.AbilCfg.ELEM_ON || a == null || v == null || a.equals(v) || pw == null || pt == null || pw.length < 5 || pt.length < 5) return false;
  if (!(hit >= 0.0) || hit > 1.0E7) return false;
  double[] p = new double[5];
  double[] q = new double[5];
  boolean any = false;
  for (int i = 0; i < 5; i++) {
    int x = pw[i];
    if (x < 0) x = 0;
    if (x > 10) x = 10;
    p[i] = (double) x;
    if (x > 0) any = true;
    double y = pt[i];
    if (!(y >= 0.0) || y > 1.0E7) y = 0.0;
    q[i] = y;
  }
  if (!any && !(gearStates() && imbueOf(a, System.currentTimeMillis()) != null)) return false;          // FIX: a running Imbue puts its state (A2)
  String wn = elemWorld(a);          // FIX (critic: any caller string made a world entry nobody ticks): a player's own world first
  if (wn == null) wn = elemWorld(v);
  if (wn == null && world != null && world.length() > 0 && world.length() <= 64 && elemWorldReal(world)) wn = world;
  if (wn == null || wn.length() > 64) return false;
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(wn);
  if (aw.elemFull()) { ELEM_DROP = ELEM_DROP + 1L; return false; }          // FIX 2: its own cap (live Burning stacks never block it)
  @PKG@.AbilJob j = new @PKG@.AbilJob(29, System.currentTimeMillis(), a, "ElemHit", 0.0, 0.0, 0.0, 0.0, hit);
  j.tref = v;
  j.cap = p;
  j.per = q;
  j.sh = heavy ? 1 : 0;
  aw.add(j);
  ELEM_IN = ELEM_IN + 1L;
  return true;
}
""",
r"""
public static boolean elemJob(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (!(j.tref instanceof java.util.UUID) || j.cap == null || j.per == null) return false;
  @REF@ t = casterRef(cb, (java.util.UUID) j.tref);
  @REF@ cr = casterRef(cb, j.caster);
  if (t == null || cr == null || !t.isValid() || !cr.isValid()) return false;
  int[] pw = new int[5];
  for (int i = 0; i < 5 && i < j.cap.length; i++) pw[i] = (int) j.cap[i];
  elemRun(cb, t, cr, j.caster, pw, j.per, j.amount, j.sh == 1, 0, 1.0, 1.0, now);
  return false;
}
""",
r"""
public static String elemClass(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, int e, double hv, double str, double dur, long now, boolean heavy) {
  if (e < 0 || e > 4) return null;
  int w = E2W[e];
  int[] pw = new int[5];
  pw[w] = 5;
  double[] pt = new double[5];
  pt[w] = hv * @PKG@.AbilNum.RX_CLASSPART / 100.0;
  String r = elemRun(cb, t, cr, u, pw, pt, hv, heavy, 1, str, dur, now);
  return r == null ? null : ELS[e];
}
""",
r"""
public static @PKG@.ElemSt elemSt(@REF@ t, long now) {
  Object o = @PKG@.AbilStore.ELEMS.get(t);
  if (o instanceof @PKG@.ElemSt) { ((@PKG@.ElemSt) o).seen = now; return (@PKG@.ElemSt) o; }
  if (@PKG@.AbilStore.ELEMS.size() >= 2048) elemPrune(now);
  @PKG@.ElemSt s = new @PKG@.ElemSt();
  s.seen = now;
  @PKG@.AbilStore.ELEMS.put(t, s);
  return s;
}
""",
r"""
public static boolean elemIdle(@PKG@.ElemSt s, long now) {
  return s.wetUntil <= now && s.burnUntil <= now && s.chillUntil <= now && s.frozenUntil <= now && s.shockUntil <= now && s.quakeUntil <= now
      && s.gustUntil <= now && s.ccFree <= now;
}
""",
r"""
public static int elemPrune0(long now, long age, boolean idle, int keep, boolean keepCc) {
  int n = 0;
  java.util.Iterator it = @PKG@.AbilStore.ELEMS.keySet().iterator();
  while (it.hasNext() && @PKG@.AbilStore.ELEMS.size() > keep) {
    Object k = it.next();
    Object v = @PKG@.AbilStore.ELEMS.get(k);
    boolean dead = !(v instanceof @PKG@.ElemSt) || (k instanceof @REF@ && !((@REF@) k).isValid());
    if (!dead) {
      @PKG@.ElemSt s = (@PKG@.ElemSt) v;
      dead = s.seen + age < now && (!idle || elemIdle(s, now));
      // FIX 2 (critic: a flood reset a boss's / player's CC immunity -> chain-lockable): a live immunity or flinch clock stays
      if (dead && keepCc && (s.ccFree > now || (s.flinchAt > 0L && now - s.flinchAt < ms(Math.max(@PKG@.AbilNum.EX_BOSSFLINCH, @PKG@.AbilNum.EX_FLINCHGAP))))) dead = false;
    }
    if (dead) { it.remove(); n++; }
  }
  return n;
}
""",
r"""
public static int elemPrune(long now) {
  // FIX (critic: past 2048 victims ONE clear() dropped every live state): gone / 30 s unseen first, then idle ones unseen 5 s, then any
  // idle one, and only then (a real flood) the rest down to 1536 - live Wet / Burning / immunity bookkeeping is the last to go
  int n = elemPrune0(now, 30000L, false, 0, false);
  if (@PKG@.AbilStore.ELEMS.size() >= 2048) n = n + elemPrune0(now, 5000L, true, 1536, false);
  if (@PKG@.AbilStore.ELEMS.size() >= 2048) n = n + elemPrune0(now, -1L, true, 1536, false);
  if (@PKG@.AbilStore.ELEMS.size() >= 2048) n = n + elemPrune0(now, -1L, false, 1536, true);          // FIX 2: live CC clocks kept
  if (@PKG@.AbilStore.ELEMS.size() >= 4096) n = n + elemPrune0(now, -1L, false, 3072, false);         // the hard bound
  return n;
}
""",
r"""
public static int elemOwn(String role, long now) {
  if (role == null) return -1;
  Object o = @PKG@.AbilStore.ELEMOWN.get(role);
  if (o instanceof long[] && ((long[]) o)[1] > now) return (int) ((long[]) o)[0];
  int e = -1;
  try {
    Object f = @PKG@.ClassCfg.bridge().get("mob:fn:elemOf");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(role);
      if (r instanceof String) {
        String w = ((String) r).trim();
        for (int i = 0; i < 5; i++) if (WN[i].equalsIgnoreCase(w)) e = i;
      }
    }
  } catch (Throwable x) { e = -1; }
  if (@PKG@.AbilStore.ELEMOWN.size() > 1024) @PKG@.AbilStore.ELEMOWN.clear();
  @PKG@.AbilStore.ELEMOWN.put(role, new long[] { (long) e, now + 10000L });
  return e;
}
""",
r"""
public static boolean elemBoss(@CB@ cb, @REF@ t, long now) {
  // FIX (critic: spec 5.4's boss = SkyyMobs mob:fn:boss - its Boss roles row + the pack bosses; abil.bossWords alone missed them):
  // abil.bossWords OR mob:fn:boss { world, null npc, role, 0, 0, 0 } answers non-null; the answer cached per role 10 s (key "#b:" + role)
  if (bossT(cb, t)) return true;
  String role = roleOf(cb, t);
  if (role == null || role.length() == 0) return false;
  String k = "#b:" + role;
  Object o = @PKG@.AbilStore.ELEMOWN.get(k);
  if (o instanceof long[] && ((long[]) o)[1] > now) return ((long[]) o)[0] == 1L;
  boolean b = false;
  try {
    Object f = @PKG@.ClassCfg.bridge().get("mob:fn:boss");
    String wn = @PKG@.AbilWorld.nameOf(cb.getExternalData());
    if (f instanceof java.util.function.Function && wn != null)
      b = ((java.util.function.Function) f).apply(new Object[] { wn, null, role, Integer.valueOf(0), Integer.valueOf(0), Integer.valueOf(0) }) != null;
  } catch (Throwable x) { b = false; }
  if (@PKG@.AbilStore.ELEMOWN.size() > 1024) @PKG@.AbilStore.ELEMOWN.clear();
  @PKG@.AbilStore.ELEMOWN.put(k, new long[] { b ? 1L : 0L, now + 10000L });
  return b;
}
""",
r"""
public static boolean fluidWater(@WLD@ w, int x, int y, int z) {
  try {
    if (w == null || y < 0 || y > 319) return false;
    @CHS@ cs = w.getChunkStore();
    @REF@ sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return false;
    @FSC@ fs = (@FSC@) cs.getStore().getComponent(sr, @FSC@.getComponentType());
    if (fs == null) return false;
    int fid = fs.getFluidId(x, y, z);
    if (fid == @FLU@.EMPTY_ID) return false;
    Object fl = @FLU@.getAssetMap().getAsset(fid);
    if (!(fl instanceof @FLU@)) return false;
    Object id = ((@FLU@) fl).getId();
    return id != null && id.toString().startsWith("Water");
  } catch (Throwable t) { return false; }
}
""",
r"""
public static boolean skyOpen(@WLD@ w, int x, int y, int z) {
  // FIX 2 (critic: under a roof / in a cave rain still soaked you): the column's heightmap top block (SkyyExploration's read: ChunkStore
  // chunk ref -> HeightmapColumn.getHeight) at or below the feet = open sky; not loaded / unknown = open (the old answer)
  try {
    if (w == null) return true;
    @CHS@ cs = w.getChunkStore();
    @REF@ r = cs.getChunkReference(@CHU@.indexChunkFromBlock(x, z));
    if (r == null || !r.isValid()) return true;
    @HMC@ h = (@HMC@) cs.getStore().getComponent(r, @HMC@.getComponentType());
    if (h == null) return true;
    int v = h.getHeight(x, z);
    return v == Integer.MIN_VALUE || v <= y;
  } catch (Throwable t) { return true; }
}
""",
r"""
public static boolean rainy(String id) {
  if (id == null || id.length() == 0) return false;
  String l = "," + @PKG@.AbilCfg.ELEM_RAINIDS.toLowerCase().replace(" ", "") + ",";
  return l.indexOf("," + id.toLowerCase() + ",") >= 0;
}
""",
r"""
public static boolean rainAt(@CB@ cb, @REF@ t, boolean pv) {
  try {
    int idx = -1;
    if (pv) {
      Object o = cb.getComponent(t, @WTRK@.getComponentType());
      if (o instanceof @WTRK@) idx = ((@WTRK@) o).getWeatherIndex();
    } else {
      Object o = cb.getComponent(t, @WSUP@.getComponentType());
      if (o instanceof @WSUP@) idx = ((@WSUP@) o).getCurrentWeatherIndex(t, cb);
    }
    if (idx < 0) return false;
    Object a = @WTH@.getAssetMap().getAsset(idx);
    if (!(a instanceof @WTH@)) return false;
    Object id = ((@WTH@) a).getId();
    return id != null && rainy(id.toString());
  } catch (Throwable x) { return false; }
}
""",
r"""
public static int elemEnvBits(@CB@ cb, @REF@ t, boolean pv) {
  java.util.function.Function f = ELEMENV;
  if (f != null) { Object o = f.apply(new Object[] { t }); return o instanceof Integer ? ((Integer) o).intValue() : 0; }
  int b = 0;
  try {
    @VEC@ q = pos(cb, t);
    @WLD@ w = ((@ES@) cb.getExternalData()).getWorld();
    if (q != null && w != null) {
      int x = (int) Math.floor(q.x);
      int z = (int) Math.floor(q.z);
      int y = (int) Math.floor(q.y + 0.2);
      if (fluidWater(w, x, y, z) || fluidWater(w, x, y + 1, z)) b = b | 1;
      if (@PKG@.AbilCfg.ELEM_RAIN && rainAt(cb, t, pv) && skyOpen(w, x, y, z)) b = b | 2;          // FIX 2: + an open sky
    }
  } catch (Throwable x) { }
  return b;
}
""",
r"""
public static boolean pvpOn(@CB@ cb, @REF@ t) {
  java.util.function.Function f = ELEMENV;
  if (f != null) { Object o = f.apply(new Object[] { t }); return o instanceof Integer && (((Integer) o).intValue() & 4) != 0; }
  try {
    @WLD@ w = ((@ES@) cb.getExternalData()).getWorld();
    return w != null && w.getWorldConfig() != null && w.getWorldConfig().isPvpEnabled();
  } catch (Throwable x) { return false; }
}
""",
r"""
public static void elemEnv(@CB@ cb, @REF@ t, @PKG@.ElemSt s, boolean pv, long now) {
  if (s.envAt > now) return;
  int b = elemEnvBits(cb, t, pv);
  s.envAt = now + ms(@PKG@.AbilNum.EX_ENVEVERY);
  s.envWater = (b & 1) != 0;
  s.envRain = (b & 2) != 0;
}
""",
r"""
public static boolean elemSoaked(@PKG@.ElemSt s) {
  return s.own == 2 || s.envWater || (s.envRain && @PKG@.AbilCfg.ELEM_RAIN);
}
""",
r"""
public static boolean elemInWater(@CB@ cb, @REF@ t, long now) {
  Object o = @PKG@.AbilStore.ELEMS.get(t);
  if (!(o instanceof @PKG@.ElemSt)) return false;
  @PKG@.ElemSt s = (@PKG@.ElemSt) o;
  elemEnv(cb, t, s, isPl(cb, t), now);
  return s.envWater;
}
""",
r"""
public static boolean elemVictim(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, boolean pv, boolean pa) {
  if (t == null || cr == null || !t.isValid() || !cr.isValid() || t.equals(cr)) return false;
  if (!pv) return pa && enemy(cb, t, cr);
  if (!@PKG@.AbilCfg.ELEM_PVP || !alive(cb, t) || creative(cb, t)) return false;
  if (!pa) return cb.getComponent(cr, @NPC@.getComponentType()) != null;
  if (!pvpOn(cb, t)) return false;
  java.util.UUID vu = elemUuid(cb, t);
  return vu != null && u != null && !vu.equals(u) && !@PKG@.HealTask.inParty(u, vu);
}
""",
r"""
public static boolean elemBurnOk(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u) {
  if (!isPl(cb, t)) return enemy(cb, t, cr);
  return @PKG@.AbilCfg.ELEM_ON && elemVictim(cb, t, cr, u, true, isPl(cb, cr));
}
""",
r"""
public static boolean elemBurnLone(@CB@ cb, @REF@ t) {
  return @PKG@.AbilCfg.ELEM_ON && @PKG@.AbilCfg.ELEM_PVP && t != null && t.isValid() && alive(cb, t) && !creative(cb, t);
}
""",
r"""
public static double elemRes(java.util.UUID vu, int w) {
  if (vu == null || w < 0 || w > 4) return 1.0;
  try {
    java.util.Map b = @PKG@.ClassCfg.bridge();
    Object f = b.get("gear:fn:elemDef");
    if (!(f instanceof java.util.function.Function)) return 1.0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { vu, WN[w] });
    double d = r instanceof Number ? ((Number) r).doubleValue() : 0.0;
    if (!(d > 0.0) || d > 1.0E6) return 1.0;
    Object so = b.get("gear:elem:defScale");
    double s = so instanceof Number ? ((Number) so).doubleValue() : 100.0;
    if (!(s >= 1.0)) s = 100.0;
    return s / (s + d);
  } catch (Throwable x) { return 1.0; }
}
""",
r"""
public static boolean envHit(@CB@ buf, @REF@ t, java.util.UUID cu, double amount, String what) {
  try {
    if (!(amount > 0.0) || t == null || !t.isValid()) return false;
    String cid = causeId(what);
    @DCS@ cause = cid == null ? @DCS@.PROJECTILE : causeOf(cid);
    if (cause == null) return false;
    @DMG@ d = new @DMG@(@DMG@.NULL_SOURCE, cause, (float) amount);
    @PKG@.AbilDmg.tag(d, cu, what);
    @DSYS@.executeDamage(t, buf, d);
    return true;
  } catch (Throwable x) { @PKG@.ClassCfg.warnLimited("an element hit failed: " + x); return false; }
}
""",
r"""
public static boolean elemTick(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID cu, double amount) {
  if (isPl(cb, t) && !isPl(cb, cr)) return envHit(cb, t, cu, amount, "ElemBurn");
  return hit(cb, t, cr, cu, amount, "ElemBurn");
}
""",
r"""
public static boolean elemDmg(@PKG@.ElemCtx c, @REF@ t, double amt, String what) {
  long a = Math.round(amt);
  if (a < 1L || t == null || !t.isValid()) return false;
  ELEM_DMG = ELEM_DMG + a;
  c.log.append(' ').append(what).append('=').append(a);
  if (isPl(c.cb, t) && !c.pa) return envHit(c.cb, t, c.u, (double) a, what);
  return hit(c.cb, t, c.cr, c.u, (double) a, what);
}
""",
r"""
public static void elemFx(@PKG@.ElemCtx c, String id, double dy) {
  @VEC@ q = pos(c.cb, c.t);
  if (q != null) particle(id, q.x, q.y + dy, q.z, c.cb);
}
""",
r"""
public static boolean elemRx(@PKG@.ElemCtx c, @PKG@.ElemSt s, int r, int w, double v) {
  if (r < 0 || r >= RN.length || s.react[r] > c.now) return false;
  s.react[r] = c.now + ms(@PKG@.AbilNum.EX_REACTCD);
  ELEM_REACT = ELEM_REACT + 1L;
  c.log.append(" rx:").append(RN[r]);
  if (c.word == null || v > c.wv) { c.word = RN[r]; c.wv = v; c.wc = w; }
  return true;
}
""",
r"""
public static double elemCc(@PKG@.ElemCtx c, @PKG@.ElemSt s, double secs, int w) {
  if (!(secs > 0.0) || s.ccFree > c.now) return 0.0;
  double m = c.pv ? @PKG@.AbilNum.EX_PVPCC / 100.0 : (c.boss ? @PKG@.AbilNum.EL_BOSSCC / 100.0 : 1.0);
  double r = secs * m * c.res[w];
  return r > 0.0 ? r : 0.0;          // FIX (critic: immunity was spent before the CC landed): only the length here - elemCcSet once it landed
}
""",
r"""
public static void elemCcSet(@PKG@.ElemCtx c, @PKG@.ElemSt s, double r) {
  double gap = c.boss ? @PKG@.AbilNum.EX_BOSSIMMUNE : (c.pv ? @PKG@.AbilNum.EX_PVPIMMUNE : @PKG@.AbilNum.EX_CCGAP);
  long f = c.now + ms(r + gap);
  if (f > s.ccFree) s.ccFree = f;
}
""",
r"""
public static boolean elemFlinch(@PKG@.ElemCtx c, @PKG@.ElemSt s, double secs, boolean sure) {
  long gap = ms(c.boss ? @PKG@.AbilNum.EX_BOSSFLINCH : @PKG@.AbilNum.EX_FLINCHGAP);
  boolean recent = s.flinchAt > 0L && c.now - s.flinchAt < gap;
  if (recent && (!sure || c.boss)) return false;          // a boss: at most once in bossFlinch s, even an Electrocute
  double r = (c.boss || c.pv) ? elemCc(c, s, secs, 1) : secs;
  if (!(r > 0.0)) return false;
  if (c.boss) {
    // FIX 2 (critic, spec 5.4 "never during a wind-up it already started"): vanilla Hit_Interrupt_Flinch plays the role's Hurt animation in
    // the Action slot (Component_Instruction_Hit_Interrupt) and can cut a running boss attack - a boss gets ONLY the attack-start block
    // (Hit_Interrupt_Stunned: no NEW attack for r s, a started one finishes), never inside vanilla's own anti-stunlock window
    // (Hit_Interrupt_Enraged), and it spends no CC immunity: its own bossFlinch gap bounds it (that row is live now)
    if (hasFx(c.cb, c.t, "Hit_Interrupt_Enraged")) return false;
    if (!effect(c.cb, c.t, EF_INTERRUPT, r)) return false;
  } else {
    if (!effect(c.cb, c.t, EF_FLINCH, r)) return false;
    effect(c.cb, c.t, EF_INTERRUPT, r);          // FIX (critic: the walk-stop alone is invisible): + vanilla's attack-start block, OUR length
  }
  s.flinchAt = c.now;
  if (c.pv) elemCcSet(c, s, r);
  c.log.append(" flinch=").append(@PKG@.AbilMath.fmt(r));
  return true;
}
""",
r"""
public static void elemSlow(@PKG@.ElemCtx c, double pct, double secs) {
  double p = pct * (c.pv ? @PKG@.AbilNum.EX_PVPCC / 100.0 : 1.0) * (c.boss ? @PKG@.AbilNum.EL_BOSSCC / 100.0 : 1.0);
  int sl = (int) Math.round(p);
  if (sl > 30) sl = 30;
  if (sl < 1 || !(secs > 0.0)) return;
  effect(c.cb, c.t, spdId(-sl), secs);
}
""",
r"""
public static void elemWeaken(@PKG@.ElemCtx c, double pct, double secs) {
  long p = Math.round(pct);
  if (p < 1L) return;          // FIX 2: 0 = off (the weaken effects are 10-40 %: 1-9 count as 10)
  if (p < 10L) p = 10L;
  if (p > 40L) p = 40L;
  if (secs > 0.0) effect(c.cb, c.t, "SkyyAbility_Weaken_" + p, secs);
}
""",
r"""
public static void elemWet(@PKG@.ElemCtx c, @PKG@.ElemSt s) {
  double secs = @PKG@.AbilNum.EX_WETTIME * c.dur * c.res[2];
  if (!(secs > 0.0)) return;
  long u = c.now + ms(secs);
  if (u > s.wetUntil) s.wetUntil = u;
  effect(c.cb, c.t, EF_WETFX, secs);
  elemFx(c, FX_WET, 1.0);
  c.log.append(" wet");
}
""",
r"""
public static boolean burnLive0(java.util.ArrayList l) {
  for (int i = 0; i < l.size(); i++) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) l.get(i);
    if (j.left > 0 && "ElemBurn".equals(j.what)) return true;
  }
  return false;
}
""",
r"""
public static boolean burnLive(@REF@ t) {
  Object o = @PKG@.AbilStore.DOTS.get(t);
  if (!(o instanceof java.util.ArrayList)) return false;
  java.util.ArrayList l = (java.util.ArrayList) o;
  boolean r = false;
  synchronized (l) { r = burnLive0(l); }
  return r;
}
""",
r"""
public static double burnSum0(java.util.ArrayList l, boolean end, double fanTime, double fanBurn, java.util.HashSet only) {
  double sum = 0.0;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) l.get(i);
    if (j.left <= 0 || !"ElemBurn".equals(j.what)) continue;
    if (only != null && !only.contains(j)) continue;          // FIX 2: only the stacks of the hit's SNAPSHOT
    if (fanTime > 0.0) {          // FIX (critic: Fan compounded x1.25 / x1.5 every second): a stack is fanned ONCE (brk 1 = fanned)
      if (j.brk < 0.5) {
        j.left = (int) Math.ceil((double) j.left * (1.0 + fanTime / 100.0));
        j.amount = j.amount * (1.0 + fanBurn / 100.0);
        j.brk = 1.0;
      }
      if (j.amount > sum) sum = j.amount;
      continue;
    }
    sum = sum + j.amount * (double) j.left;
    if (end) j.left = 0;
  }
  return sum;
}
""",
r"""
public static double burnSum(@REF@ t, boolean end, double fanTime, double fanBurn, java.util.HashSet only) {
  Object o = @PKG@.AbilStore.DOTS.get(t);
  if (!(o instanceof java.util.ArrayList)) return 0.0;
  java.util.ArrayList l = (java.util.ArrayList) o;
  double r = 0.0;
  synchronized (l) { r = burnSum0(l, end, fanTime, fanBurn, only); }
  return r;
}
""",
r"""
public static java.util.HashSet burnSnap0(java.util.ArrayList l) {
  java.util.HashSet h = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) l.get(i);
    if (j.left > 0 && "ElemBurn".equals(j.what)) h.add(j);
  }
  return h;
}
""",
r"""
public static java.util.HashSet burnSnap(@REF@ t) {
  Object o = @PKG@.AbilStore.DOTS.get(t);
  if (!(o instanceof java.util.ArrayList)) return new java.util.HashSet();
  java.util.ArrayList l = (java.util.ArrayList) o;
  java.util.HashSet r = null;
  synchronized (l) { r = burnSnap0(l); }
  return r;
}
""",
r"""
public static int burnMark0(java.util.ArrayList l, java.util.HashSet pre, java.util.HashSet inc) {
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) l.get(i);
    if (j.left <= 0 || !"ElemBurn".equals(j.what)) continue;
    // FIX 2: pre / inc null = every stack; else the snapshot's stacks (inc) + the ones made after pre (the Wildfire stack) - a stack
    // this hit's Fire lit stays unfanned
    if ((pre == null && inc == null) || (inc != null && inc.contains(j)) || (pre != null && !pre.contains(j))) { j.brk = 1.0; n++; }
  }
  return n;
}
""",
r"""
public static int burnMark(@REF@ t) {
  Object o = @PKG@.AbilStore.DOTS.get(t);
  if (!(o instanceof java.util.ArrayList)) return 0;
  java.util.ArrayList l = (java.util.ArrayList) o;
  int r = 0;
  synchronized (l) { r = burnMark0(l, null, null); }
  return r;
}
""",
r"""
public static int burnMarkNew(@REF@ t, java.util.HashSet pre, java.util.HashSet inc) {
  Object o = @PKG@.AbilStore.DOTS.get(t);
  if (!(o instanceof java.util.ArrayList)) return 0;
  java.util.ArrayList l = (java.util.ArrayList) o;
  int r = 0;
  synchronized (l) { r = burnMark0(l, pre, inc); }
  return r;
}
""",
r"""
public static double elemBurnEnd(@REF@ t) {
  Object o = @PKG@.AbilStore.ELEMS.get(t);
  if (o instanceof @PKG@.ElemSt) ((@PKG@.ElemSt) o).burnUntil = 0L;
  return burnSum(t, true, 0.0, 0.0, null);
}
""",
r"""
public static boolean elemBurn(@PKG@.ElemCtx c, @REF@ t, @PKG@.ElemSt s, double perSec, double secs, int cap, boolean chkWet) {
  if (!(perSec > 0.0) || !(secs > 0.0) || s.own == 3) return false;
  if (s.envWater || (chkWet && s.wetUntil > c.now)) return false;          // the hit's own target: its SNAPSHOT decided (a Fire + Water hit burns + soaks)
  dotOn(c.cb, t, c.u, "ElemBurn", perSec, secs, cap, c.now);
  long u = c.now + ms(secs);
  if (u > s.burnUntil) s.burnUntil = u;
  effect(c.cb, t, EF_BURNFX, secs);
  @VEC@ q = pos(c.cb, t);
  if (q != null) particle(FX_FIRE, q.x, q.y + 1.0, q.z, c.cb);
  return true;
}
""",
r"""
public static boolean elemWetAt(@PKG@.ElemCtx c, @REF@ e, @PKG@.ElemSt es) {
  if (es != null) {
    if (es.own < -1) es.own = elemOwn(roleOf(c.cb, e), c.now);
    elemEnv(c.cb, e, es, false, c.now);          // cached per victim (envEvery)
    return es.wetUntil > c.now || elemSoaked(es);
  }
  // FIX 2 (critics: an uncached block + weather read for every stateless bystander on every jump): ONE answer per bystander per hit
  // (ElemCtx.envc, shared by every jump of the hit), at most 32 lookups a hit - past that a stateless bystander counts as dry
  if (c.envc == null) c.envc = new java.util.HashMap();
  Object k = c.envc.get(e);
  if (k instanceof Boolean) return ((Boolean) k).booleanValue();
  boolean wt = elemOwn(roleOf(c.cb, e), c.now) == 2;
  if (!wt && c.envn < 32) {
    c.envn = c.envn + 1;
    int eb = elemEnvBits(c.cb, e, false);
    wt = (eb & 1) != 0 || ((eb & 2) != 0 && @PKG@.AbilCfg.ELEM_RAIN);
  }
  c.envc.put(e, Boolean.valueOf(wt));
  return wt;
}
""",
r"""
public static @REF@ elemNext(@PKG@.ElemCtx c, double x, double y, double z, double r, java.util.HashSet done, boolean wetOnly, boolean jump) {
  java.util.List l = near(c.cb, x, y, z, r);
  @REF@ best = null;
  double bd = 1.0E18;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@) || done.contains(o)) continue;
    @REF@ e = (@REF@) o;
    if (!enemy(c.cb, e, c.cr)) continue;
    @VEC@ q = pos(c.cb, e);
    if (q == null) continue;
    double d = (q.x - x) * (q.x - x) + (q.y - y) * (q.y - y) + (q.z - z) * (q.z - z);
    if (d > r * r || d >= bd) continue;
    Object eo = @PKG@.AbilStore.ELEMS.get(e);
    @PKG@.ElemSt es = null;
    if (eo instanceof @PKG@.ElemSt) es = (@PKG@.ElemSt) eo;
    if (jump && es != null && es.jumpAt > c.now) continue;          // FIX 2 (critic: an AoE stacked N chains on one mob): one jump per reactCd
    if (wetOnly && !elemWetAt(c, e, es)) continue;          // FIX (critics): no state made for a bystander; Wet from water / rain counts too
    bd = d;
    best = e;
  }
  return best;
}
""",
r"""
public static int elemJump(@PKG@.ElemCtx c, int n, double range, double dmg, double vuln, double secs, boolean wetOnly, String what) {
  if (!c.pa || n < 1 || !(range > 0.0)) return 0;          // only a player's hit arcs on to other mobs
  @VEC@ q = pos(c.cb, c.t);
  if (q == null) return 0;
  if (c.jd == null) { c.jd = new java.util.HashSet(); c.jd.add(c.t); }          // FIX: one done set for every jump of this hit
  java.util.HashSet done = c.jd;
  int k = 0;
  for (int i = 0; i < n; i++) {
    @REF@ x = elemNext(c, q.x, q.y, q.z, range, done, wetOnly, true);
    if (x == null) break;
    done.add(x);
    elemDmg(c, x, dmg, what);          // FIX 2: "ElemArc" (no 2nd Weak / Resist on a part that has it); the class Shock jump: 0.1.50's ElemShock
    @PKG@.ElemSt xs = elemSt(x, c.now);
    xs.jumpAt = c.now + ms(@PKG@.AbilNum.EX_REACTCD);          // FIX 2: at most one jump on this victim per reactCd
    if (xs.own < -1) xs.own = elemOwn(roleOf(c.cb, x), c.now);
    if (xs.own != 1 && secs > 0.0)          // FIX 2: 0.1.50's +5 % damage taken only - never the Shocked state (a jump never chains on)
      @PKG@.AbilStore.SHOCKD.put(x, new double[] { (double) (c.now + ms(secs)), vuln });
    @VEC@ w = pos(c.cb, x);
    if (w != null) particle(FX_ZAP, w.x, w.y + 1.0, w.z, c.cb);
    k++;
  }
  if (k > 0) c.log.append(" jump=").append(k);
  return k;
}
""",
r"""
public static int elemSpread(@PKG@.ElemCtx c, double perSec) {
  if (!c.pa || !(perSec > 0.0)) return 0;
  @VEC@ q = pos(c.cb, c.t);
  if (q == null) return 0;
  java.util.HashSet done = new java.util.HashSet();
  done.add(c.t);
  @REF@ x = elemNext(c, q.x, q.y, q.z, @PKG@.AbilNum.RX_WILDRANGE, done, false, false);
  if (x == null) return 0;
  @PKG@.ElemSt xs = elemSt(x, c.now);
  if (xs.own < -1) xs.own = elemOwn(roleOf(c.cb, x), c.now);
  if (!elemBurn(c, x, xs, perSec, @PKG@.AbilNum.EL_BURNTIME * c.dur, (int) Math.round(@PKG@.AbilNum.EL_BURNSTACKS), true)) return 0;
  burnMark(x);          // FIX: a spread (already fanned) stack is never fanned again - no x1.25 per hop
  c.log.append(" spread=1");
  return 1;
}
""",
r"""
public static void elemChill(@PKG@.ElemCtx c, @PKG@.ElemSt s, double sc, int count) {
  if (s.own == 2 || count < 1) return;
  double tm = @PKG@.AbilNum.EL_CHILLTIME * c.dur * c.res[2];
  elemSlow(c, @PKG@.AbilNum.EL_CHILLSLOW * sc, tm);
  long u = c.now + ms(tm);
  if (u > s.chillUntil) s.chillUntil = u;
  long win = ms(@PKG@.AbilNum.EL_FREEZEWINDOW);
  int need = (int) Math.round(@PKG@.AbilNum.EL_FREEZEAT);
  if (need < 1) need = 1;
  if (need > s.chills.length) need = s.chills.length;
  for (int k = 0; k < count; k++) {
    int o = 0;
    for (int i = 1; i < s.chills.length; i++) if (s.chills[i] < s.chills[o]) o = i;
    s.chills[o] = c.now;
  }
  int recent = 0;
  for (int i = 0; i < s.chills.length; i++) if (s.chills[i] > 0L && c.now - s.chills[i] <= win) recent++;
  c.log.append(" chill=").append(recent);
  elemFx(c, FX_FROST_HIT, 1.0);
  if (recent < need) return;
  for (int i = 0; i < s.chills.length; i++) s.chills[i] = 0L;
  double secs = elemCc(c, s, @PKG@.AbilNum.EL_FREEZETIME * c.dur, 2);
  if (!(secs > 0.0)) return;
  int fz = freezeOne(c.cb, c.t, c.u, secs, 1.0, 0.0, c.now);
  if (fz <= 0) return;
  if (fz == 2) {          // FIX 2 (critic): the boss clock cut the hold - Frozen (Shatter / Melt) ends with the REAL freeze
    Object fo = @PKG@.AbilStore.FROZEN.get(c.t);
    if (fo instanceof long[] && ((long[]) fo).length > 1 && ((long[]) fo)[1] > c.now) secs = (double) (((long[]) fo)[1] - c.now) / 1000.0;
  }
  elemCcSet(c, s, secs);
  s.frozenUntil = c.now + ms(secs);
  s.chillUntil = 0L;
  elemFx(c, FX_FROST, 1.0);
  c.log.append(" frozen=").append(@PKG@.AbilMath.fmt(secs));
}
""",
r"""
public static void elemEarth(@PKG@.ElemCtx c, @PKG@.ElemSt s, double sc, double part, boolean burning, boolean wet, boolean frozen, boolean shocked, boolean gusted) {
  if (burning) {
    double rem = burnSum(c.t, false, 0.0, 0.0, null);
    if (elemRx(c, s, 10, 0, rem)) { elemBurnEnd(c.t); elemDmg(c, c.t, rem, "ElemBurn"); elemFx(c, FX_STONE, 0.5); }
  }
  if (wet && elemRx(c, s, 9, 0, 0.0)) {
    if (!elemSoaked(s)) s.wetUntil = 0L;          // a Water mob / one in water or rain stays Wet
    elemSlow(c, @PKG@.AbilNum.EX_MUDSLOW, @PKG@.AbilNum.EX_MUDTIME * c.res[0]);
    elemFx(c, FX_MUD, 0.2);
  }
  if (frozen) {
    double b = part * @PKG@.AbilNum.RX_SHATTER / 100.0;
    if (elemRx(c, s, 11, 0, b)) { unfreeze(c.cb, c.t); @PKG@.AbilStore.FROZEN.remove(c.t); s.frozenUntil = 0L; elemDmg(c, c.t, b, "ElemShatter"); elemFx(c, FX_ICEBRK, 1.0); }
  }
  if (shocked) {
    double b = s.shockPart * @PKG@.AbilNum.RX_GROUNDED / 100.0;
    if (elemRx(c, s, 6, 0, b)) { s.shockUntil = 0L; @PKG@.AbilStore.SHOCKD.remove(c.t); elemDmg(c, c.t, b, "ElemGround"); elemFx(c, FX_STONE, 0.2); }
  }
  if (gusted) {
    double b = part * @PKG@.AbilNum.RX_SANDBLAST / 100.0;
    if (elemRx(c, s, 12, 0, b)) { elemDmg(c, c.t, b, "ElemSand"); elemWeaken(c, @PKG@.AbilNum.EX_SANDWEAKEN, @PKG@.AbilNum.EX_SANDTIME); elemFx(c, FX_SAND, 1.0); }
  }
  if (s.own == 0) return;
  s.earthN = s.earthN + 1;
  long every = Math.round(@PKG@.AbilNum.EL_STAGGEREVERY);
  if (every < 1L) every = 1L;
  if (((long) s.earthN) % every != 0L) { elemFx(c, FX_STONE, 0.2); return; }
  double secs = elemCc(c, s, @PKG@.AbilNum.EL_STAGGERTIME * c.dur, 0);
  if (secs > 0.0) {
    boolean ok = c.pv ? effect(c.cb, c.t, EF_STUN, secs) : stunMob(c.cb, c.t, c.u, secs, c.now) > 0;          // 0 = only slowed (a boss clock)
    if (ok) elemCcSet(c, s, secs);
    else secs = 0.0;
  }
  double dt = @PKG@.AbilNum.EL_STAGGERDEFTIME * c.dur * c.res[0];
  s.quakeUntil = c.now + ms(dt);
  @PKG@.AbilStore.STAGD.put(c.t, new double[] { (double) s.quakeUntil, @PKG@.AbilNum.EL_STAGGERDEF * sc, (double) s.earthN });
  c.log.append(" quake=").append(@PKG@.AbilMath.fmt(secs));
  elemFx(c, FX_SPLIT, 0.1);
}
""",
r"""
public static void elemThunder(@PKG@.ElemCtx c, @PKG@.ElemSt s, double sc, double part, boolean wet, boolean quaked, boolean gusted) {
  double jd = c.src == 1 ? c.hit * @PKG@.AbilNum.EL_SHOCKPCT / 100.0 * sc : part * @PKG@.AbilNum.EX_SHOCKPCT / 100.0 * sc;
  double vuln = @PKG@.AbilNum.EL_SHOCKVULN * sc;
  double st = @PKG@.AbilNum.EL_SHOCKTIME * c.dur;
  boolean grounded = false;
  boolean elec = false;
  int extra = 0;
  double xr = 0.0;
  if (wet) {
    double b = part * @PKG@.AbilNum.RX_ELECTROCUTE / 100.0;
    if (elemRx(c, s, 5, 1, b + 0.001)) {
      elec = true;          // the chain through the Wet replaces this hit's normal jump (no enemy is hit twice)
      elemDmg(c, c.t, b, "ElemArc");          // FIX 2: the part has the Weak / Resist already - no second one
      if (s.own != 1) {          // FIX (critic): a Thunder mob takes the Electrocute damage but never its flinch / chain (own element)
        elemFlinch(c, s, @PKG@.AbilNum.RX_ELECFLINCH, true);
        // FIX 2 (critic: Storm was spent and did nothing next to Electrocute): a Windswept target's STORM widens this chain too
        if (gusted && elemRx(c, s, 7, 1, 0.0)) { extra = (int) Math.round(@PKG@.AbilNum.RX_STORMJUMPS); xr = @PKG@.AbilNum.RX_STORMRANGE; }
        elemJump(c, (int) Math.round(@PKG@.AbilNum.EX_CHAINMAX) + extra, @PKG@.AbilNum.EX_CHAINRANGE + xr, jd, vuln, st, true, "ElemArc");
      }
      elemFx(c, FX_BOLT2, 1.0);
    }
  }
  if (quaked) {
    double b = part * @PKG@.AbilNum.RX_GROUNDED / 100.0;
    if (elemRx(c, s, 6, 1, b)) { grounded = true; s.shockUntil = 0L; @PKG@.AbilStore.SHOCKD.remove(c.t); elemDmg(c, c.t, b, "ElemGround"); elemFx(c, FX_STONE, 0.2); }
  }
  if (grounded || s.own == 1) return;
  s.shockUntil = c.now + ms(st * c.res[1]);
  s.shockPart = part;          // FIX 2 (critic: a stale / twice-scaled value fed Conduct / Grounded / Storm): the Thunder part, every Shock
  @PKG@.AbilStore.SHOCKD.put(c.t, new double[] { (double) s.shockUntil, vuln });
  if (!elec) {
    if (gusted && elemRx(c, s, 7, 1, 0.0)) { extra = (int) Math.round(@PKG@.AbilNum.RX_STORMJUMPS); xr = @PKG@.AbilNum.RX_STORMRANGE; }   // FIX 2: spent only when used
    elemJump(c, 1 + extra, @PKG@.AbilNum.EL_SHOCKRANGE + xr, jd, vuln, st, false, c.src == 1 ? "ElemShock" : "ElemArc");
  }
  s.thunderN = s.thunderN + 1;
  long ev = Math.round(@PKG@.AbilNum.EX_FLINCHEVERY);
  if (ev < 1L) ev = 1L;
  if (((long) s.thunderN) % ev == 0L) elemFlinch(c, s, @PKG@.AbilNum.EX_FLINCHTIME, false);
  c.log.append(" shock");
  elemFx(c, FX_ZAP, 1.0);
}
""",
r"""
public static void elemWater(@PKG@.ElemCtx c, @PKG@.ElemSt s, double sc, double part, boolean burning, boolean wet, boolean chilled, boolean frozen, boolean shocked, boolean quaked) {
  boolean doused = false;
  if (burning) {
    double b = part * @PKG@.AbilNum.RX_DOUSE / 100.0;
    if (elemRx(c, s, 1, 2, b)) { elemBurnEnd(c.t); elemDmg(c, c.t, b, "ElemSteam"); elemFx(c, FX_STEAM, 1.0); doused = true; }
  }
  if (shocked && s.shockPart > 0.0) {          // FIX 2: shockPart is the Thunder part -> the part % (ab.ElemStates shockPct), ElemArc
    double jd = s.shockPart * @PKG@.AbilNum.EX_SHOCKPCT / 100.0;
    if (elemRx(c, s, 8, 2, jd)) elemJump(c, (int) Math.round(@PKG@.AbilNum.EX_CHAINMAX), @PKG@.AbilNum.EX_CHAINRANGE, jd, @PKG@.AbilNum.EL_SHOCKVULN, @PKG@.AbilNum.EL_SHOCKTIME * c.dur, true, "ElemArc");
  }
  if (quaked && elemRx(c, s, 9, 2, 0.0)) { elemSlow(c, @PKG@.AbilNum.EX_MUDSLOW, @PKG@.AbilNum.EX_MUDTIME * c.res[2]); elemFx(c, FX_MUD, 0.2); }
  if (s.own == 2) return;
  if (wet || chilled || frozen) elemChill(c, s, sc, (chilled || frozen) ? 2 : 1);
  else if (doused || !burning) elemWet(c, s);
}
""",
r"""
public static void elemFire(@PKG@.ElemCtx c, @PKG@.ElemSt s, double sc, double part, boolean wet, boolean chilled, boolean frozen, boolean gusted) {
  boolean noBurn = wet;
  int cap = (int) Math.round(@PKG@.AbilNum.EL_BURNSTACKS);
  double tm = @PKG@.AbilNum.EL_BURNTIME;
  if (wet) {
    double b = part * @PKG@.AbilNum.RX_STEAM / 100.0;
    if (elemRx(c, s, 0, 3, b)) { if (!elemSoaked(s)) s.wetUntil = 0L; elemDmg(c, c.t, b, "ElemFlare"); elemFx(c, FX_STEAM, 1.0); }
  }
  if (frozen) {
    double b = part * @PKG@.AbilNum.RX_MELT / 100.0;
    if (elemRx(c, s, 2, 3, b)) { unfreeze(c.cb, c.t); @PKG@.AbilStore.FROZEN.remove(c.t); s.frozenUntil = 0L; s.chillUntil = 0L; elemDmg(c, c.t, b, "ElemFlare"); elemWet(c, s); noBurn = true; }
  } else if (chilled && elemRx(c, s, 3, 3, 0.0)) { s.chillUntil = 0L; elemWet(c, s); noBurn = true; }
  if (noBurn || s.own == 3 || s.envWater) return;          // FIX (critic): FANNED only fires when a Burning can start
  if (gusted && elemRx(c, s, 4, 3, 0.0)) { cap = (int) Math.round(@PKG@.AbilNum.EX_FANSTACKS); tm = tm * (1.0 + @PKG@.AbilNum.RX_FANNED / 100.0); }
  double ps = (c.src == 1 ? @PKG@.AbilNum.EL_BURNPCT : @PKG@.AbilNum.EX_BURNPCT) * c.hit / 100.0 * sc;
  if (elemBurn(c, c.t, s, ps, tm * c.dur * c.res[3], cap, false)) c.log.append(" burn=").append(@PKG@.AbilMath.fmt(ps));
}
""",
r"""
public static void elemAir(@PKG@.ElemCtx c, @PKG@.ElemSt s, double sc, double part, boolean burning, boolean wet, boolean chilled, boolean shocked, boolean quaked, boolean gusted) {
  // FIX 2 (critic, 5.3): only the snapshot's stacks that still burn (a Douse / Smother earlier in this hit ended them -> no Wildfire)
  double bl = burning && c.bj != null ? burnSum(c.t, false, 0.0, 0.0, c.bj) : 0.0;
  if (bl > 0.0 && elemRx(c, s, 13, 4, bl * @PKG@.AbilNum.RX_FANBURN / 100.0)) {
    double best = burnSum(c.t, false, @PKG@.AbilNum.RX_FANTIME, @PKG@.AbilNum.RX_FANBURN, c.bj);
    if (best > 0.0) {
      java.util.HashSet pre = burnSnap(c.t);
      dotOn(c.cb, c.t, c.u, "ElemBurn", best, @PKG@.AbilNum.EL_BURNTIME * c.dur, (int) Math.round(@PKG@.AbilNum.EX_FANSTACKS), c.now);
      burnMarkNew(c.t, pre, c.bj);          // FIX: the new / refreshed stack carries the fanned amount - it is never fanned again
      long u = c.now + ms(@PKG@.AbilNum.EL_BURNTIME * c.dur);
      if (u > s.burnUntil) s.burnUntil = u;
      elemSpread(c, best);
      elemFx(c, FX_MARK, 0.2);
    }
  }
  if (wet && elemRx(c, s, 14, 4, 0.0)) elemChill(c, s, sc, 1);
  else if (chilled) elemChill(c, s, sc, 1);          // the caller passes Chilled OR Frozen (matrix: "Chilled / Frozen: Chill +1")
  if (shocked && s.shockPart > 0.0) {          // FIX 2: as Conduct
    double jd = s.shockPart * @PKG@.AbilNum.EX_SHOCKPCT / 100.0;
    if (elemRx(c, s, 7, 4, jd)) elemJump(c, 1 + (int) Math.round(@PKG@.AbilNum.RX_STORMJUMPS), @PKG@.AbilNum.EL_SHOCKRANGE + @PKG@.AbilNum.RX_STORMRANGE, jd, @PKG@.AbilNum.EL_SHOCKVULN, @PKG@.AbilNum.EL_SHOCKTIME * c.dur, false, "ElemArc");
  }
  if (quaked) {
    double b = part * @PKG@.AbilNum.RX_SANDBLAST / 100.0;
    if (elemRx(c, s, 12, 4, b)) { elemDmg(c, c.t, b, "ElemGale"); elemWeaken(c, @PKG@.AbilNum.EX_SANDWEAKEN, @PKG@.AbilNum.EX_SANDTIME); elemFx(c, FX_SAND, 1.0); }
  }
  if (s.own == 4) return;
  s.gustUntil = c.now + ms(@PKG@.AbilNum.EX_WINDSWEPT);
  if (c.boss) { c.log.append(" gust=boss"); return; }          // bosses: knockback immune (the live Gust rule)
  if (c.pv && s.ccFree > c.now) { c.log.append(" gust=immune"); return; }          // FIX (critic, spec 5.5): a pushed player gets the 5 s immunity
  @VEC@ p = pos(c.cb, c.cr);
  @VEC@ q = pos(c.cb, c.t);
  if (p == null || q == null) return;
  if (c.pv) elemCcSet(c, s, 0.0);
  double dx = q.x - p.x;
  double dz = q.z - p.z;
  double d = Math.sqrt(dx * dx + dz * dz);
  double kb = @PKG@.AbilNum.EL_GUSTKB * sc * (gusted ? 1.5 : 1.0) * (c.pv ? @PKG@.AbilNum.EX_PVPKB / 100.0 : 1.0);
  double f = kb * @PKG@.AbilCfg.PUSH_PER_BLOCK;
  double up = c.heavy ? @PKG@.AbilNum.EL_GUSTUP * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5 * (c.pv ? @PKG@.AbilNum.EX_PVPKB / 100.0 : 1.0) : 0.3;
  if (d > 0.05) push(c.cb, c.t, dx / d * f, up, dz / d * f);
  else push(c.cb, c.t, 0.0, up, 0.0);
  c.log.append(" gust=").append(@PKG@.AbilMath.fmt(kb));
  elemFx(c, FX_SMOKE, 1.0);
}
""",
r"""
public static boolean elemPop(@CB@ cb, @REF@ cr, @REF@ t, String word, int w) {
  java.util.List l = POPS;
  if (l != null) { l.add(word + ":" + w); ELEM_POPS = ELEM_POPS + 1L; return true; }
  try {
    if (word == null || w < 0 || w > 4 || cr == null || t == null) return false;
    Object o = cb.getComponent(cr, @EVW@.getComponentType());
    if (!(o instanceof @EVW@)) return false;
    @EVW@ v = (@EVW@) o;
    if (v.visible == null || !v.visible.contains(t)) return false;          // queueUpdate throws for an entity the player does not see
    v.queueUpdate(t, new @CTU@(0.0f, word, new @PCOL@((byte) ECR[w], (byte) ECG[w], (byte) ECB[w])));
    ELEM_POPS = ELEM_POPS + 1L;
    return true;
  } catch (Throwable x) { return false; }
}
""",
r"""
public static String elemText(@PKG@.ElemSt s, long now) {
  StringBuilder b = new StringBuilder();
  if (s.wetUntil > now) b.append("W");
  if (s.burnUntil > now) b.append("B");
  if (s.chillUntil > now) b.append("C");
  if (s.frozenUntil > now) b.append("F");
  if (s.shockUntil > now) b.append("S");
  if (s.quakeUntil > now) b.append("Q");
  if (s.gustUntil > now) b.append("G");
  return b.length() == 0 ? "-" : b.toString();
}
""",
r"""
public static String elemRun(@CB@ cb, @REF@ t, @REF@ cr, java.util.UUID u, int[] pw, double[] pt, double hit, boolean heavy, int src, double str, double dur, long now) {
  if (!@PKG@.AbilCfg.ELEM_ON || cb == null || t == null || cr == null || u == null || pw == null || pt == null || pw.length < 5 || pt.length < 5) return null;
  if (!t.isValid() || !cr.isValid()) return null;
  @PKG@.ElemCtx c = new @PKG@.ElemCtx();
  c.cb = cb;
  c.t = t;
  c.cr = cr;
  c.u = u;
  c.now = now;
  c.heavy = heavy;
  c.src = src;
  c.hit = 0.0;
  if (hit > 0.0 && hit < 1.0E7) c.hit = hit;
  c.dur = 1.0;
  if (dur > 0.0) c.dur = dur;
  c.pv = isPl(cb, t);
  c.pa = isPl(cb, cr);
  if (!elemVictim(cb, t, cr, u, c.pv, c.pa)) return null;
  c.boss = !c.pv && elemBoss(cb, t, now);          // FIX: abil.bossWords OR SkyyMobs' mob:fn:boss (spec 5.4)
  c.res = new double[] { 1.0, 1.0, 1.0, 1.0, 1.0 };
  if (c.pv) {          // FIX (critic): every element's Defence - Wind Chill / Thaw / Mud put another element's state than the hit's
    java.util.UUID vu = elemUuid(cb, t);
    for (int i = 0; i < 5; i++) c.res[i] = elemRes(vu, i);
  }
  @PKG@.ElemSt s = elemSt(t, now);
  if (s.own < -1) { if (c.pv) s.own = -1; else s.own = elemOwn(roleOf(cb, t), now); }
  elemEnv(cb, t, s, c.pv, now);
  if (elemSoaked(s)) {          // a Water mob is always Wet; water + rain soak
    long wu = now + ms(@PKG@.AbilNum.EX_WETTIME);
    if (wu > s.wetUntil) s.wetUntil = wu;
    if (s.envWater && burnLive(t)) elemBurnEnd(t);
  }
  boolean burning = burnLive(t);          // 1. the SNAPSHOT - a hit never reacts with a state it puts on itself
  if (burning) c.bj = burnSnap(t);          // FIX 2: which Burning stacks the snapshot saw (Wildfire fans only those)
  boolean wet = s.wetUntil > now;
  boolean frozen = s.frozenUntil > now;
  boolean chilled = !frozen && s.chillUntil > now;
  boolean shocked = s.shockUntil > now;
  boolean quaked = s.quakeUntil > now;
  boolean gusted = s.gustUntil > now;
  long ah = u.getMostSignificantBits() ^ u.getLeastSignificantBits();
  double[] imb = null;
  if (src == 0) imb = imbueOf(u, now);
  int ie = -1;
  if (imb != null && (int) imb[1] >= 0 && (int) imb[1] <= 4) ie = E2W[(int) imb[1]];
  long same = ms(@PKG@.AbilNum.EX_SAMEHIT);
  boolean gs = ie >= 0 && gearStates();
  int done = 0;
  for (int w = 0; w < 5; w++) {          // 2. Wynn order: Earth, Thunder, Water, Fire, Air
    int p = pw[w];
    boolean imbOnly = w == ie && p <= 0 && gs;          // FIX (critic): with SkyyGear sending the states (A2) Classes skips its own Imbue path -
    if (imbOnly) p = 5;                                 //   a weapon with no augment of the Imbue element still puts Imbue's state (Power 5)
    if (w == ie && p > 0 && p < 5) p = 5;          // spec 4.3: max(Power, 5) while Imbue of that element runs
    if (p <= 0) continue;
    if (p > 10) p = 10;
    long gk = ah ^ ((long) (w + 1) * -7046029254386353131L);          // FIX: the same-hit key = attacker x element (a ring of 8)
    boolean dup = false;
    for (int g = 0; g < s.ga.length; g++) if (s.ga[g] == gk && s.gt[g] > 0L && now >= s.gt[g] && now - s.gt[g] < same) dup = true;
    if (dup) { c.log.append(" same:").append(WN[w]); continue; }
    int gi = -1;
    for (int g = 0; g < s.ga.length && gi < 0; g++) if (s.ga[g] == gk) gi = g;
    if (gi < 0) { gi = s.gi; s.gi = (s.gi + 1) % s.ga.length; }
    s.ga[gi] = gk;
    s.gt[gi] = now;
    double sc = (double) p / 5.0;
    if (src == 1) { sc = 1.0; if (str > 0.0) sc = str; }
    if (sc > 2.0) sc = 2.0;
    double part = 0.0;
    if (pt[w] > 0.0 && pt[w] < 1.0E7) part = pt[w];
    if (imbOnly && !(part > 0.0)) part = c.hit * @PKG@.AbilNum.RX_CLASSPART / 100.0;
    c.log.append(' ').append(WN[w]).append(p);
    if (w == 0) elemEarth(c, s, sc, part, burning, wet, frozen, shocked, gusted);
    else if (w == 1) elemThunder(c, s, sc, part, wet, quaked, gusted);
    else if (w == 2) elemWater(c, s, sc, part, burning, wet, chilled, frozen, shocked, quaked);
    else if (w == 3) elemFire(c, s, sc, part, wet, chilled, frozen, gusted);
    else elemAir(c, s, sc, part, burning, wet, chilled || frozen, shocked, quaked, gusted);          // FIX: Frozen counts as Chilled for Air
    done++;
  }
  if (done == 0) return null;
  ELEM_RUN = ELEM_RUN + 1L;
  STATUSES = STATUSES + 1L;
  if (c.word != null && c.pa && @PKG@.AbilCfg.ELEM_POP) elemPop(cb, cr, t, c.word, c.wc);          // 5. one word a hit (the strongest)
  StringBuilder ob = new StringBuilder(elemText(s, now));
  if (c.boss) ob.append(" boss");
  if (c.pv) ob.append(" player");
  if (c.word != null) ob.append(" word=").append(c.word);
  ob.append(c.log.toString());
  String out = ob.toString();
  LAST_EL = out;
  return out;
}
""",
]
'''
P.rep('''for _src in ABIL_LATE:
    M(abil, _late_stub(_src))
''', ENGINE.lstrip("\n") + '''for _src in ABIL_LATE:
    M(abil, _late_stub(_src))
''')

# ================================================================================================ the plugin: bridge put / remove, ready line, the jar
P.rep('''  b.put("classes:fn:dot", new @PKG@.DotFn());                // 0.1.46 (elem1): SkyyGear's Poison line through the one DoT engine''',
      '''  b.put("classes:fn:dot", new @PKG@.DotFn());                // 0.1.46 (elem1): SkyyGear's Poison line through the one DoT engine
  b.put("classes:fn:elemHit", new @PKG@.ElemHitFn());        // 0.1.51 (Augments A1): the element states engine (SkyyGear A2, SkyyMobs 0.1.23)''')
P.rep('''  try { @PKG@.ClassCfg.bridge().remove("classes:fn:dot"); } catch (Throwable t) { }         // 0.1.46''',
      '''  try { @PKG@.ClassCfg.bridge().remove("classes:fn:dot"); } catch (Throwable t) { }         // 0.1.46
  try { @PKG@.ClassCfg.bridge().remove("classes:fn:elemHit"); } catch (Throwable t) { }     // 0.1.51''')
P.rep('''classes:fn:dot (status / DoT ticks on their element's DamageCause); bridge''',
      '''classes:fn:dot (status / DoT ticks on their element's DamageCause), classes:fn:elemHit (element states " + (@PKG@.AbilCfg.ELEM_ON ? "on" : "off") + ", rain " + (@PKG@.AbilCfg.ELEM_RAIN ? "Wet" : "off") + "); bridge''')
P.rep('''          abaltf, abfold):               # 0.1.47: + class:fn:altPick, the one-time class tree fold''',
      '''          abaltf, abfold,                # 0.1.47: + class:fn:altPick, the one-time class tree fold
          elst, elctx, elhit):           # 0.1.51: + the element states engine (ElemSt, ElemCtx) + classes:fn:elemHit''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 3, "0.1.51: 3 classes, no command / system"
P.finish()
print("wrote", P.dst)
