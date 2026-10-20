"""Derive SkyyMenu/build_skyymenu_0.3.41.py from the LIVE SkyyMenu 0.3.40 (python tools/menu_0_3_41_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_40_patch.py -> 0.3.40 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.41. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.40 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.41.py is its own file.

0.3.41 (2026-10-20) = SKILL TREES 3 IN THE MODS LIST (with SkyyTrees 0.4.0, SkyyClasses 0.1.42, SkyySkills 0.4.55). Skyy (2026-10-18): "drop the
dust" + the Skill Trees 3 answers (docs/answered/skills.md): the SkyyTrees Mods entry no longer mentions Tokens / Dust / Ability Points:
  1. Its Server Setup line: "respec, Dust refund, nodes, Vein Burst, Feller, class trees" (the Token / Dust / AP rows
     left SkyyTrees 0.4.0's Server Setup page - the page itself comes from SkyyTrees through the config kit, nothing to change here).
  2. Its blurb + commands: one Borderlands-style pattern, 1 point a level, rows open on points spent, free row abilities; /tree combat and
     /tree beastmastery.
  3. MODS_VERSIONS: SkyyTrees 0.4.0, SkyySkills 0.4.55, SkyyClasses 0.1.42 (the versions this round deploys).
  No new command, permission, setting, page or bridge key. ROLLBACK to 0.3.40: safe (texts only).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.40.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.41.py"))
assert P.has('VERSION = "0.3.40"\n') and P.has("MENU_ITEM_ONE_HAND") and not P.has("Skill Trees 3"), "not the generated SkyyMenu 0.3.40 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.41: Skill Trees 3 in the Mods list (notes: tools/menu_0_3_41_patch.py): the SkyyTrees entry without Tokens / Dust / AP (blurb, Server
       Setup line, /tree combat + beastmastery); MODS_VERSIONS SkyyTrees 0.4.0, SkyySkills 0.4.55, SkyyClasses 0.1.42.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.41.py.
''')
P.rep('VERSION = "0.3.40"\n', 'VERSION = "0.3.41"\n')
P.rep('''"SkyyGear": "0.3.24", "SkyySkills": "0.4.51",''', '''"SkyyGear": "0.3.24", "SkyySkills": "0.4.55",''')
P.rep('''"SkyyClasses": "0.1.38",''', '''"SkyyClasses": "0.1.42",''')
P.rep('''"SkyyTrees": "0.3.23",''', '''"SkyyTrees": "0.4.0",''')
P.rep('''     "setup": ("0.2.2", "Trees", "nodes, Dust, Tree Feller, Vein Burst, swings, class trees"),
     "desc": "Skill trees: spend the points your skill levels earn on nodes for Mining, Foraging, Farming, Cooking, Alchemy, Smithing, Acrobatics and Exploration - and a class tree that spends the Ability Points your class skill earns.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - open one tree, for example /tree mining",
                  "/tree class - your class tree (Ability Points from your class skill)",''',
      '''     "setup": ("0.2.2", "Trees", "respec, Dust refund, nodes, Vein Burst, Feller, class trees"),   # 0.3.41: Skill Trees 3
     "desc": "Skill Trees 3: your class tree and one tree for each skill (Mining, Foraging, Combat, Beastmastery, Farming, Fishing, Alchemy, Smithing, Cooking, Acrobatics, Exploration). 1 point a level, rows open on the points you spend in a tree, each row's ability or perk comes free. Respec: one free each run, then coins.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - one tree, e.g. /tree mining or /tree combat",
                  "/tree class - your class tree (1 point per class level)",''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.41 adds no system / command"
P.finish()
