"""Derive SkyyCooking/build_skyycooking_0.1.10.py from the LIVE SkyyCooking 0.1.9 (build_skyycooking_0.1.9.py = the tools/deploy_set.py SET pin,
DERIVED by tools/cooking_0_1_9_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every change
is undone on a copy and compared with 0.1.9 (nothing else changed). Line endings kept.
Run:  python tools/cooking_0_1_10_patch.py   then   python SkyyCooking/build_skyycooking_0.1.10.py   (never --deploy)
Check: python SkyyCooking/test_skyycooking_0.1.10.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.1.10 = ONE FOOD TYPE (lean round cook0110; docs/answered/skills.md 2026-10-16, Skyy on a screenshot of an Uncommon Vegetable Skewer
 'Health food (Veggie)' restoring health, mana and stamina: "why do vegetables give health mana and stamina? this is 1 food type. not all 3").
 The 0.1.8 higher-tier all-round share (ALLROUND T2 0.15 / T3 0.25 on every bar the families leave empty) is gone: ALLROUND = 0 at every
 tier, so a dish restores ONLY its own families' bars - Veggie = Health, Fruit = Mana, Meat = Stamina, Mushroom = Strength; Grain
 (half Health + half Stamina) and Dairy, Egg & Fish (half Stamina + half Mana) keep their own mixed shares; a dish of several families
 still splits between them (SHARE unchanged). The instant restore, the over-time buffs and every tooltip follow (no Mana Regen / Stamina
 Boost line on a Veggie dish); a Mushroom-only dish (Mushroom Skewer) now restores no bar at once - only its Strength buff (tooltip
 "Grants:"; its eat chain is just the Strength check). Same item ids: food players already hold is the rebuilt item and follows on the next start.
 Running buffs: the over-time levels only the all-round share used (ALLROUND_0_1_9) stay in the jar as effect + check files (the bar
 ladders are byte-equal to 0.1.9), so a buff still running from a 0.1.9 dish keeps loading, still stacks by the one-buff-per-bar rule
 and runs out. No saved data, no id, no class logic changes (only the version texts).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.9.py"), os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.10.py"))
assert P.has('VERSION = "0.1.9"\n') and P.has("DERIVED from build_skyycooking_0.1.8.py by tools/cooking_0_1_9_patch.py") and not P.has("ONE FOOD TYPE"), \
    "not the generated SkyyCooking 0.1.9 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.10 = ONE FOOD TYPE"):].rstrip() + "\n\n"

# ---------- docstring + version
P.rep('''"""SkyyCooking 0.1.9 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.8.py by tools/cooking_0_1_9_patch.py
(0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_8_patch.py / _0_1_7_patch.py /
_0_1_6_patch.py / _0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it,
not this file.
Run:   python build_skyycooking_0.1.9.py            -> SkyyCooking/SkyyCooking-0.1.9.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''', '''"""SkyyCooking 0.1.10 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.9.py by tools/cooking_0_1_10_patch.py
(0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_9_patch.py /
_0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py / _0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py /
_0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.10.py           -> SkyyCooking/SkyyCooking-0.1.10.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''' + NOTE)
P.rep('VERSION = "0.1.9"\n', 'VERSION = "0.1.10"\n')

# ---------- the all-round share: 0 at every tier (one food type = only its own bars)
P.rep('''ALLROUND = {1: 0.0, 2: 0.15, 3: 0.25}                  # higher tiers: this weight on every bar the families leave empty (not Strength)
''', '''ALLROUND_0_1_9 = {1: 0.0, 2: 0.15, 3: 0.25}            # 0.1.8-0.1.9: higher tiers gave this weight on every bar the families left empty
ALLROUND = {1: 0.0, 2: 0.0, 3: 0.0}                    # 0.1.10 (Skyy 2026-10-16: "this is 1 food type. not all 3"): only the families' bars
assert not any(ALLROUND.values()), "0.1.10: no all-round share at any tier"
''')

# ---------- keep the bar levels only the old all-round share used (running 0.1.9 buffs keep loading + stacking; ladders = 0.1.9)
P.rep('''max_clears = 0
for b in BARS:
    ks = sorted(USED[b])
''', '''_AR_NOW, ALLROUND = ALLROUND, ALLROUND_0_1_9          # 0.1.10: the 0.1.9 levels (bar_weights reads the module-level ALLROUND)
USED_0_1_9 = dict((b, set()) for b in BARS)
for (_d, _g) in list(DISH_NUM):
    if _d in RAW: continue
    for _b, (_k, _v) in numbers(DISH_FAMS[_d], DISH_TIER[_d], _g)[3].items(): USED_0_1_9[_b].add(_k)
ALLROUND = _AR_NOW
LEGACY_FX = dict((b, sorted(USED_0_1_9[b] - USED[b])) for b in BARS)
assert all(USED[b] <= USED_0_1_9[b] for b in BARS) and not LEGACY_FX["Strength"], "0.1.10: the families' own levels are a subset of 0.1.9's"
for b in BARS: USED[b] |= USED_0_1_9[b]
print("0.1.10 legacy all-round levels kept (no item applies them; running 0.1.9 buffs run out): " + ", ".join("%s %d" % (b, len(LEGACY_FX[b])) for b in BARS))
max_clears = 0
for b in BARS:
    ks = sorted(USED[b])
''')
# ---------- tooltip: a Mushroom-only dish (Strength) now has no instant restore at all
P.rep('''    body = "Instantly restores " + (", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0])
    bl = fx_bullets(n)
    if bl:
        body += " and grants:\\\\n\\\\n" + "\\\\n".join(bl) + "\\\\n\\\\nDuration: " + W % mmss(buff_dur(sn, dur))
    else:
        body += "."
''', '''    bl = fx_bullets(n)
    if parts:
        body = "Instantly restores " + (", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]) + (" and grants:" if bl else ".")
    else:   # 0.1.10: a Mushroom-only dish restores no bar - only its Strength buff
        body = "Grants:"
    if bl:
        body += "\\\\n\\\\n" + "\\\\n".join(bl) + "\\\\n\\\\nDuration: " + W % mmss(buff_dur(sn, dur))
''')
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added"
P.finish()
