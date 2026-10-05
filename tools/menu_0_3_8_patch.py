"""Derive SkyyMenu/build_skyymenu_0.3.8.py from the LIVE SkyyMenu 0.3.7 (python tools/menu_0_3_8_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> ... -> menu_0_3_7_patch.py -> 0.3.7 (= the
tools/deploy_set.py SET pin, generated - never re-run its patch, never re-build it) -> this patch -> 0.3.8. 0.3.7's files stay untouched.

0.3.8 = DATA / TEXT ONLY (no behaviour change):
  1. The Mods list = tools/deploy_set.py SET of 2026-10-05 (evening) + THIS ROUND (ROUND_PINS: SkyyTrees 0.3.2 - class trees ON by
     default, Skyy LOCKED 2026-10-05 - built in parallel; MODS names 0.3.2, the live-set check accepts it while SET still pins 0.3.1 and
     checks the round's set too). Version bumps since 0.3.7: Collections 0.2.6, Party 0.1.7, Bazaar 0.1.4, Gear 0.2.3, Skills 0.4.16,
     Essentials 0.1.8 (Exploration 0.2.3, Accessories 0.5.5 and Cooking 0.1.6 were 0.3.7's round and are pinned now).
  2. Help texts for those versions: SkyyGear 0.2.3 crafted gear pays Smithing XP (Server Setup Gear rows 'Smithing XP per crafted gear',
     'Craft XP tier factor'); SkyySkills 0.4.16 'Own XP list per skill' (Server Setup Skills -> Levels; Mining's own curve); SkyyParty
     0.1.7 TPA / Accept TPA buttons on the party page (with SkyyEssentials 0.1.8's tpa bridge); SkyyBazaar 0.1.4 progression prices;
     SkyyTrees: the Alchemy + Smithing trees (live since 0.3) and the class tree (/tree class; /tree probe for admins), class trees in the
     Server Setup line.
NOT CHANGED: every class but MenuData's data (the harness byte-compares), SET_KNOWN, the menu look, the config kit pin.
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.7 outside them, byte for byte.
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.7.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.8.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.7"' in s and "0.3.7: DATA / TEXT ONLY" in s, "not the generated 0.3.7 script"
assert "@@" not in s, "0.3.7 already holds a @@ token"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# THIS ROUND: the mods that deploy together with this SkyyMenu (mod: (the SET version now, the round's version))
ROUND = {"SkyyTrees": ("0.3.1", "0.3.2")}
# THE ONE VERSION TABLE = tools/deploy_set.py SET of 2026-10-05 evening (SET order) with the ROUND versions. Bump here, regenerate, rebuild.
MODS_VERSIONS = [
    ("SkyyHud", "0.3.13"), ("SkyySacks", "0.7.12"), ("SkyyCoins", "0.1.5"), ("SkyyCollections", "0.2.6"), ("SkyyParty", "0.1.7"),
    ("SkyyBank", "0.1.6"), ("SkyyIslands", "0.5.5"), ("SkyyBazaar", "0.1.4"), ("SkyyGear", "0.2.3"), ("SkyySkills", "0.4.16"),
    ("SkyyAccessories", "0.5.5"), ("SkyyClasses", "0.1.11"), ("SkyyEssentials", "0.1.8"), ("SkyyProfiles", "0.1.5"),
    ("SkyyCooking", "0.1.6"), ("SkyyTrees", "0.3.2"), ("SkyyExploration", "0.2.3"), ("SkyyGuilds", "0.1.6"), ("SkyyVault", "0.1.5"),
    ("SkyyAuctions", "0.1.2"), ("SkyyRanks", "0.1.1"), ("SkyyUiProbe", "0.4"), ("SkyyMobs", "0.1.3"), ("SkyyWorldGen", "0.1"),
    ("SkyyArmory", "0.1"),
]
_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = [x for x in ast.literal_eval(_n.value) if x[0] != "SkyyMenu"]
assert len(set(m for m, v in MODS_VERSIONS)) == len(MODS_VERSIONS), "a mod is twice in MODS_VERSIONS"
for _m, (_frm, _to) in ROUND.items():
    assert (_m, _to) in MODS_VERSIONS, "ROUND %s: MODS_VERSIONS must name %s" % (_m, _to)
if _set is not None:
    _round_set = [(m, ROUND[m][1] if m in ROUND and v == ROUND[m][0] else v) for m, v in _set]
    if sorted(_round_set) != sorted(MODS_VERSIONS):
        print("NOTE: MODS_VERSIONS differs from tools/deploy_set.py SET + ROUND now: table-only %s, SET-only %s" %
              (sorted(set(MODS_VERSIONS) - set(_round_set)), sorted(set(_round_set) - set(MODS_VERSIONS))))


def table_text(pairs):
    """the generated MODS_VERSIONS block: 5 mods per line (SET order) - the same layout as tools/menu_0_3_7_patch.py"""
    lines = []
    for i in range(0, len(pairs), 5):
        lines.append("    " + ", ".join('"%s": "%s"' % p for p in pairs[i:i + 5]) + ",")
    return "MODS_VERSIONS = {\n" + "\n".join(lines) + "\n}"


_blk = re.findall(r"^MODS_VERSIONS = \{\n.*?^\}", s, re.M | re.S)
assert len(_blk) == 1, "MODS_VERSIONS block: %d found" % len(_blk)

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.7: DATA / TEXT ONLY''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.8: DATA / TEXT ONLY (no behaviour change; notes: tools/menu_0_3_8_patch.py): the Mods list = tools/deploy_set.py SET of 2026-10-05
       evening + this round (ROUND_PINS: SkyyTrees 0.3.2, class trees ON by default) - Collections 0.2.6, Party 0.1.7, Bazaar 0.1.4, Gear
       0.2.3, Skills 0.4.16, Essentials 0.1.8 (26 mods); help texts: Gear crafting Smithing XP, Skills own XP list per skill, Party TPA /
       Accept TPA buttons, Bazaar progression prices, Trees Alchemy / Smithing + the class tree (/tree class, /tree probe for admins).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.8.py (every 0.3.7 check carried forward + F3 the 0.3.8 texts + K3 0.3.7 -> 0.3.8 data only).
0.3.7: DATA / TEXT ONLY''')
rep('VERSION = "0.3.7"', 'VERSION = "0.3.8"')
rep('"set EXPECTED_KIT through tools/menu_0_3_7_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_8_patch.py (or its successor), regenerate, re-test"')
rep(_blk[0], table_text(MODS_VERSIONS))

# ================================================================================================ SkyySkills 0.4.16: own XP list per skill
rep('''     "setup": ("0.4.3", "Skills", "levels, class curve, XP rates, perks, Overall Level, Mana"),''',
    '''     # 0.3.8: SkyySkills 0.4.16 - Server Setup -> Skills -> Levels -> 'Own XP list per skill' (levels.skill; Mining by default)
     "setup": ("0.4.3", "Skills", "own XP list per skill, XP rates, perks, Overall Level, Mana"),''')

# ================================================================================================ SkyyTrees: Alchemy / Smithing + class tree
rep('''     "setup": ("0.2.2", "Trees", "node values, Dust, Tree Feller, Vein Burst, tool swings"),
     "desc": "Skill trees: spend the points your skill levels earn on nodes for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - open one tree, for example /tree mining",
                  "/tree quiet - hide the Tree bonus chat line", "/tree reload - (admin) re-read the tree settings"]},''',
    '''     # 0.3.8: SkyyTrees 0.3 - 0.3.2 - the Alchemy + Smithing trees, the class tree (Ability Points from the class skill; ON by default
     # since 0.3.2, Skyy LOCKED 2026-10-05; Server Setup -> Trees -> Class trees), /tree class, the admin /tree probe page
     "setup": ("0.2.2", "Trees", "nodes, Dust, Tree Feller, Vein Burst, swings, class trees"),
     "desc": "Skill trees: spend the points your skill levels earn on nodes for Mining, Foraging, Farming, Cooking, Alchemy, Smithing, Acrobatics and Exploration - and a class tree that spends the Ability Points your class skill earns.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - open one tree, for example /tree mining",
                  "/tree class - your class tree (Ability Points from your class skill)",
                  "/tree quiet - hide the Tree bonus chat line", "/tree reload - (admin) re-read the tree settings",
                  "/tree probe - (admin) the class tree probe page (nothing saved)"]},''')

# ================================================================================================ SkyyParty 0.1.7: TPA buttons
rep('''     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. Turn party invites off''',
    '''     # 0.3.8: SkyyParty 0.1.7 - TPA / Accept TPA buttons on the party page (SkyyEssentials 0.1.8's tpa bridge); no new command or switch
     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. The party page's TPA and Accept TPA buttons send or answer a teleport request in one click. Turn party invites off''')

# ================================================================================================ SkyyEssentials 0.1.8: the tpa bridge
rep('''     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages''',
    '''     # 0.3.8: SkyyEssentials 0.1.8 - the tpa bridge behind SkyyParty's TPA buttons; same commands, switches and Server Setup page
     "desc": "Everyday commands the base game is missing: teleport requests between players (also from the party page), private messages''')

# ================================================================================================ SkyyBazaar 0.1.4: progression prices
rep('''     "desc": "A Hypixel-style Bazaar: instantly buy or sell dozens of resources against the server. Prices move as people trade.",''',
    '''     # 0.3.8: SkyyBazaar 0.1.4 - progression prices (default prices only: about x2 per material tier step)
     "desc": "A Hypixel-style Bazaar: instantly buy or sell dozens of resources against the server. Prices move as people trade, and each higher material tier is worth about twice the one before.",''')

# ================================================================================================ SkyyGear 0.2.3: crafting Smithing XP
rep('''     "setup": ("0.1", "Gear", "rarities, level bands, damage and armor by level, costs"),''',
    '''     # 0.3.8: SkyyGear 0.2.3 - crafted gear pays Smithing XP (Server Setup -> Gear rows 'Smithing XP per crafted gear', 'Craft XP tier factor')
     "setup": ("0.1", "Gear", "level bands, damage and armor by level, crafting Smithing XP"),''')
rep('''Crafted gear comes out at your level within its material's band and rolls, mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",''',
    '''Crafted gear comes out at your level within its material's band, rolls and pays Smithing XP. Mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",''')

# ================================================================================================ ROUND_PINS: this round
rep('''# If one of them does not ship, set its MODS_VERSIONS entry back and drop it here (the live-set check names it).
ROUND_PINS = {'SkyyAccessories': ('0.5.4', '0.5.5'), 'SkyyCooking': ('0.1.5', '0.1.6'), 'SkyyExploration': ('0.2.2', '0.2.3')}''',
    '''# If one of them does not ship, set its MODS_VERSIONS entry back and drop it here (the live-set check names it).
# 0.3.8: deploys WITH SkyyTrees 0.3.2 (class trees ON by default; tools/menu_0_3_8_patch.py ROUND). 0.3.7's round is pinned in SET now.
ROUND_PINS = %s''' % repr(dict((m, ROUND[m]) for m in sorted(ROUND))))

# ================================================================================================ build checks: 0.3.8 texts
rep('''assert [a for a in _bym["SkyyUiProbe"]["admin"] if a.startswith("/skyprobe map")], "SkyyUiProbe 0.4: the /skyprobe map line"''',
    '''assert [a for a in _bym["SkyyUiProbe"]["admin"] if a.startswith("/skyprobe map")], "SkyyUiProbe 0.4: the /skyprobe map line"
# 0.3.8: the texts of Gear 0.2.3, Skills 0.4.16, Party 0.1.7 / Essentials 0.1.8, Bazaar 0.1.4 and Trees 0.3 - 0.3.2
assert "pays Smithing XP" in _bym["SkyyGear"]["desc"] and "crafting Smithing XP" in _bym["SkyyGear"]["setup"][2], "SkyyGear 0.2.3: craft Smithing XP"
assert "own XP list per skill" in _bym["SkyySkills"]["setup"][2], "SkyySkills 0.4.16: Own XP list per skill"
assert "TPA and Accept TPA" in _bym["SkyyParty"]["desc"] and "also from the party page" in _bym["SkyyEssentials"]["desc"], "SkyyParty 0.1.7 TPA buttons"
assert "about twice" in _bym["SkyyBazaar"]["desc"], "SkyyBazaar 0.1.4: progression prices"
_tr = _bym["SkyyTrees"]
assert "Alchemy, Smithing" in _tr["desc"] and "class tree" in _tr["desc"] and "class trees" in _tr["setup"][2] \\
    and [c for c in _tr["commands"] if c.startswith("/tree class ")] and [c for c in _tr["commands"] if c.startswith("/tree probe ") and "(admin)" in c], \\
    "SkyyTrees 0.3 - 0.3.2: Alchemy / Smithing, the class tree, /tree class, /tree probe (admin)"''')

# ================================================================================================ live-set check: patch name
rep('_PATCH = "tools/menu_0_3_7_patch.py"', '_PATCH = "tools/menu_0_3_8_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert s.count("MODS_VERSIONS = {") == 1 and s.count('"version": MODS_VERSIONS["') == len(MODS_VERSIONS), \
    "every table mod has exactly one MODS entry"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.7 outside the recorded changes"
compile(s, dst, "exec")
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.7 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
