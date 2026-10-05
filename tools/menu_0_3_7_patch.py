"""Derive SkyyMenu/build_skyymenu_0.3.7.py from the LIVE SkyyMenu 0.3.6 (python tools/menu_0_3_7_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> ... -> menu_0_3_6_patch.py -> 0.3.6 (= the
tools/deploy_set.py SET pin, generated - never re-run its patch, never re-build it) -> this patch -> 0.3.7. 0.3.6's files stay untouched.

0.3.7 = DATA / TEXT ONLY (no behaviour change):
  1. The Night Vision help texts are gone: SkyyAccessories 0.5.4 RETIRED Night Vision and added the Lantern line (Skyy 2026-10-03:
     "forget night vision, just do the lantern accessory"; deployed 2026-10-04). The Accessories Mods entry (description + the Server
     Setup line) names the Lantern now; the build check asserts no Mods text says Night Vision any more.
  2. The Mods list = tools/deploy_set.py SET of 2026-10-05 + THIS ROUND (ROUND_PINS: SkyyExploration 0.2.3 page guard, SkyyAccessories
     0.5.5, SkyyCooking 0.1.6 - built in parallel; MODS names the round's versions, the live-set check accepts them while SET still pins
     0.2.2 / 0.5.4 / 0.1.5 and checks the round's set too). Version bumps since 0.3.6: Hud 0.3.13, Bazaar 0.1.3, Gear 0.2.2, Skills
     0.4.15, Classes 0.1.11, Trees 0.3.1, UiProbe 0.4, Mobs 0.1.3. NEW entry SkyyArmory 0.1 (live since 2026-10-03, missing from 0.3.6's
     list): wands + staffs, no commands, Server Setup -> Armory. SkyyUiProbe 0.4: one admin line for its /skyprobe map steps.
NOT CHANGED: every class but MenuData's data (the harness byte-compares), SET_KNOWN, the menu look, the config kit pin.
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.6 outside them, byte for byte.
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.6.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.7.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.6"' in s and "0.3.6: THE STUCK-PAGE FIX" in s, "not the generated 0.3.6 script"
assert "@@" not in s, "0.3.6 already holds a @@ token"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# THIS ROUND: the mods that deploy together with this SkyyMenu (mod: (the SET version now, the round's version))
ROUND = {"SkyyExploration": ("0.2.2", "0.2.3"), "SkyyAccessories": ("0.5.4", "0.5.5"), "SkyyCooking": ("0.1.5", "0.1.6")}
# THE ONE VERSION TABLE = tools/deploy_set.py SET of 2026-10-05 (SET order) with the ROUND versions. Bump here, regenerate, rebuild.
MODS_VERSIONS = [
    ("SkyyHud", "0.3.13"), ("SkyySacks", "0.7.12"), ("SkyyCoins", "0.1.5"), ("SkyyCollections", "0.2.5"), ("SkyyParty", "0.1.6"),
    ("SkyyBank", "0.1.6"), ("SkyyIslands", "0.5.5"), ("SkyyBazaar", "0.1.3"), ("SkyyGear", "0.2.2"), ("SkyySkills", "0.4.15"),
    ("SkyyAccessories", "0.5.5"), ("SkyyClasses", "0.1.11"), ("SkyyEssentials", "0.1.7"), ("SkyyProfiles", "0.1.5"),
    ("SkyyCooking", "0.1.6"), ("SkyyTrees", "0.3.1"), ("SkyyExploration", "0.2.3"), ("SkyyGuilds", "0.1.6"), ("SkyyVault", "0.1.5"),
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
    """the generated MODS_VERSIONS block: 5 mods per line (SET order) - the same layout as tools/menu_0_3_6_patch.py"""
    lines = []
    for i in range(0, len(pairs), 5):
        lines.append("    " + ", ".join('"%s": "%s"' % p for p in pairs[i:i + 5]) + ",")
    return "MODS_VERSIONS = {\n" + "\n".join(lines) + "\n}"


_blk = re.findall(r"^MODS_VERSIONS = \{\n.*?^\}", s, re.M | re.S)
assert len(_blk) == 1, "MODS_VERSIONS block: %d found" % len(_blk)

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.6: THE STUCK-PAGE FIX''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.7: DATA / TEXT ONLY (no behaviour change; notes: tools/menu_0_3_7_patch.py): the Night Vision help texts are gone (SkyyAccessories
       0.5.4 retired it for the Lantern line); the Mods list = tools/deploy_set.py SET of 2026-10-05 + this round (ROUND_PINS: SkyyExploration
       0.2.3, SkyyAccessories 0.5.5, SkyyCooking 0.1.6) + the missing SkyyArmory 0.1 entry (26 mods); SkyyUiProbe 0.4 /skyprobe map line;
       the live-set check's two differences fixed (SkyyBazaar 0.1.3's Server Setup page Bazaar, SkyyGear 0.2.2's gear.critFx switch).
  CHECKED 2026-10-05 with SkyyMenu/test_skyymenu_0.3.7.py (needs SkyyMenu-0.3.5.jar + SkyyMenu-0.3.6.jar): 975 checks, 0 fail -
    every 0.3.6 check carried forward (P: 0.3.5 still reproduces the stuck page, 0.3.7 fixes it), F2 the 0.3.7 texts (no Night
    Vision anywhere, the Lantern, SkyyArmory, /skyprobe map, Bazaar Server Setup, gear.critFx), K2 0.3.6 -> 0.3.7 data / version only.
0.3.6: THE STUCK-PAGE FIX''')
rep('VERSION = "0.3.6"', 'VERSION = "0.3.7"')
rep('"set EXPECTED_KIT through tools/menu_0_3_6_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_7_patch.py (or its successor), regenerate, re-test"')
rep(_blk[0], table_text(MODS_VERSIONS))

# ================================================================================================ SkyyAccessories: Night Vision -> Lantern
rep('''     "setup": ("0.4.4", "Accessories", "bag slots, booster lines, notices, Night Vision"),''',
    '''     # 0.3.7: SkyyAccessories 0.5.4 - the Lantern line REPLACES Night Vision (retired: it does nothing, cannot be equipped); Server
     # Setup -> Accessories -> Lantern (on / off, glow and reach per rarity, the highest helper, shared reach)
     "setup": ("0.4.4", "Accessories", "bag slots, booster lines, notices, Lantern"),''')
rep('''booster accessories - Health, Stamina, Mana, Regeneration, Speed, Night Vision (an admin item for now) and more - that work in the bag.''',
    '''booster accessories - Health, Stamina, Mana, Regeneration, Speed, the Lantern (you glow like a torch) and more - that work in the bag.''')

# ================================================================================================ SkyyArmory 0.1 (NEW entry, after SkyyGear)
rep('''                  "/gear - the held item's gear lines, your totals and your Smithing rarity"]},
''', '''                  "/gear - the held item's gear lines, your totals and your Smithing rarity"]},
    # 0.3.7: SkyyArmory 0.1 (live since 2026-10-03, missing from 0.3.6's list): Priest wands in every metal + the Mage staff ladder (tap =
    # quick shot, hold = charged shot, both cost Mana); no command at all (check "" - the Mods view finds it by its plugin name); Server
    # Setup -> Armory (config kit, MOD=MOD constant); no player switch
    {"mod": "SkyyArmory", "version": MODS_VERSIONS["SkyyArmory"], "icon": "Weapon_Wand_Wood", "check": "",
     "config": "Skyy_SkyyArmory/config.properties", "reload": "", "note": "Change it in game: Server Setup -> Armory.",
     "setup": ("0.1", "Armory", "wand and staff damage, quick shots, Mana check"),
     "desc": "Wands and staffs: Priest wands in every metal from Copper to Onyxium and the Mage staff ladder. Tap for a quick shot, hold for a charged shot - both cost Mana, and better metals hit harder. Craft the metal wands at the Weapon Bench (Bow tab).",
     "commands": ["No commands - hold a wand or staff: tap for a quick shot, hold to charge."]},
''')

# ================================================================================================ SkyyUiProbe 0.4: the map probes
rep('''               "/skyprobe win | secgrid - (admin) the two vault window probes (23, 24)"],''',
    '''               "/skyprobe win | secgrid - (admin) the two vault window probes (23, 24)",
               # 0.3.7: SkyyUiProbe 0.4 - the minimap probe steps (each off by default, started only by an op for that player)
               "/skyprobe map [step] - (admin) the minimap probe steps (off by default)"],''')

# ================================================================================================ the live-set check's two differences
# SkyyBazaar 0.1.3 publishes a Server Setup page (Bazaar: the processed goods premium, Skyy_SkyyBazaar/config.properties)
rep('''     "config": "Skyy_SkyyBazaar/products.properties,Skyy_SkyyBazaar/market.properties", "reload": "bazaaradmin reload", "note": "",
     "desc": "A Hypixel-style Bazaar:''', '''     "config": "Skyy_SkyyBazaar/products.properties,Skyy_SkyyBazaar/market.properties,Skyy_SkyyBazaar/config.properties",
     "reload": "bazaaradmin reload", "note": "",
     # 0.3.7: SkyyBazaar 0.1.3 - its Server Setup page (Bazaar -> Market: the processed goods premium, config.properties)
     "setup": ("0.1.3", "Bazaar", "the processed goods premium"),
     "desc": "A Hypixel-style Bazaar:''')
# SkyyGear 0.2.2 registers the player switch gear.critFx (label / tab / help exactly as the mod registers them)
rep('''    ("gear.notices",         "combat",      "Gear update notices",          "One-time line when your old rolled items move to the new gear system", "SkyyGear"),
''', '''    ("gear.notices",         "combat",      "Gear update notices",          "One-time line when your old rolled items move to the new gear system", "SkyyGear"),
    # 0.3.7: SkyyGear 0.2.2 - the crit effects switch
    ("gear.critFx",          "combat",      "Crit effects",                 "CRIT! popup, sparks and the red number on your critical hits", "SkyyGear"),
''')

# ================================================================================================ ROUND_PINS: this round
rep('''# 0.3.4 / 0.3.5 / 0.3.6: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (the
# MODS_VERSIONS table above). To ship it together with e.g. SkyyGear 0.2.1: {"SkyyGear": ("0.2", "0.2.1")} + that version in MODS_VERSIONS.
ROUND_PINS = {}''', '''# 0.3.4 / 0.3.5 / 0.3.6: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (the
# MODS_VERSIONS table above). To ship it together with e.g. SkyyGear 0.2.1: {"SkyyGear": ("0.2", "0.2.1")} + that version in MODS_VERSIONS.
# 0.3.7: deploys WITH SkyyExploration 0.2.3 (page guard), SkyyAccessories 0.5.5 and SkyyCooking 0.1.6 (tools/menu_0_3_7_patch.py ROUND).
# If one of them does not ship, set its MODS_VERSIONS entry back and drop it here (the live-set check names it).
ROUND_PINS = %s''' % repr(dict((m, ROUND[m]) for m in sorted(ROUND))))

# ================================================================================================ build checks: 0.3.7 texts
rep('''assert "Night Vision" in _bym["SkyyAccessories"]["desc"] and "Night Vision" in _bym["SkyyAccessories"]["setup"][2], "SkyyAccessories 0.5.3: Night Vision"''',
    '''# 0.3.7: SkyyAccessories 0.5.4 retired Night Vision for the Lantern line - no Mods text names Night Vision any more
assert "the Lantern" in _bym["SkyyAccessories"]["desc"] and "Lantern" in _bym["SkyyAccessories"]["setup"][2], "SkyyAccessories 0.5.4: the Lantern"
assert "night vision" not in (_alltext3 + " " + " ".join(" ".join(m["setup"]) for m in MODS if "setup" in m)).lower(), \\
    "0.3.7: no Mods text names Night Vision (retired by SkyyAccessories 0.5.4)"
_ar = _bym["SkyyArmory"]
assert _ar["check"] == "" and _ar["setup"][1] == "Armory" and _ar["reload"] == "" and _ar["config"] == "Skyy_SkyyArmory/config.properties" \\
    and not _ar.get("admin") and not [c for c in _ar["commands"] if c.startswith("/")], "SkyyArmory 0.1: no command, Server Setup Armory"
assert [m["mod"] for m in MODS].index("SkyyArmory") == [m["mod"] for m in MODS].index("SkyyGear") + 1, "SkyyArmory right after SkyyGear"
assert [a for a in _bym["SkyyUiProbe"]["admin"] if a.startswith("/skyprobe map")], "SkyyUiProbe 0.4: the /skyprobe map line"''')

# ================================================================================================ live-set check: patch name
rep('_PATCH = "tools/menu_0_3_6_patch.py"', '_PATCH = "tools/menu_0_3_7_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert s.count("MODS_VERSIONS = {") == 1 and s.count('"version": MODS_VERSIONS["') == len(MODS_VERSIONS), \
    "every table mod has exactly one MODS entry"
_mods_part = s[s.index("\nMODS = ["):s.index("\n# ---- Settings (0.2")]
assert "Night Vision" not in "\n".join(ln for ln in _mods_part.split(LF) if not ln.lstrip().startswith("#")), \
    "a MODS text still names Night Vision"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.6 outside the recorded changes"
compile(s, dst, "exec")
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.6 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
