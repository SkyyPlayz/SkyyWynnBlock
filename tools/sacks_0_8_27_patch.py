"""Derive SkyySacks/build_skyysacks_0.8.27.py from the SET pin 0.8.26 (the GENERATED build_skyysacks_0.8.26.py; edit THIS file, then
regenerate: python tools/sacks_0_8_27_patch.py; never re-run sacks_0_8_26_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.26 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_27_patch.py   then   python SkyySacks/build_skyysacks_0.8.27.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.27.py [--dir <folder inside tools/dev/scratch/>] [--keep]
0.8.25 (the off-hand refill, tools/sacks_0_8_25_patch.py) is NOT in 0.8.27 either: Skyy parked it ("skip for now").

0.8.27 (2026-10-22) = NORMAL BAG QUALITY TEXT #fefefe (was #ffffff; ui-data). Skyy's 10-22 server log: The Armory's ScribingModule withdrew #ffffff
  (it uses that colour itself) because an item quality draws its text in pure white; SkyyGear 0.3.36 already moved Skyy_Gear_Normal to
  #fefefe (ui-data). Only the TextColor of the shipped quality asset Server/Item/Qualities/Skyy_Bag_Normal.json changes (looks the same).
  BAG_RARITY keeps #ffffff (it is the rarity table SkyyGear's RARITIES are cross-checked against - SkyyGear's own table also keeps #FFFFFF
  and changes only its quality JSON); the bag page colours, the Java tables and every other quality are untouched. No code / saved-data /
  config change. ROLLBACK to 0.8.26: safe (the WARN comes back).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.26.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.27.py"))
assert P.has('VERSION = "0.8.26"\n') and P.has("SackMig0826") and not P.has("utilCounts"), \
    "not the live generated SkyySacks 0.8.26 (0.8.25's off-hand refill must not be in the base)"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.27 (2026-10-22)"):].rstrip() + "\n"

P.rep('''  Undo it in Server Setup -> Changes first if wanted).
"""
''', '''  Undo it in Server Setup -> Changes first if wanted).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.26"\n', 'VERSION = "0.8.27"\n')
P.rep('''        "TextColor": tip,
        "LocalizationKey": "server.general.qualities." + qid,''', '''        "TextColor": "#fefefe" if qid == "Skyy_Bag_Normal" else tip,   # 0.8.27: #ffffff is The Armory Scribing's (its WARN 2026-10-22) - ui-data (a quality asset)
        "LocalizationKey": "server.general.qualities." + qid,''')
P.rep('''    if any(q["QualityValue"] >= 8 for q in quals.values()):
        raise SystemExit("0.8.0 asset check: a bag quality reaches SkyyAuctions' technical threshold (8)")
''', '''    if any(q["QualityValue"] >= 8 for q in quals.values()):
        raise SystemExit("0.8.0 asset check: a bag quality reaches SkyyAuctions' technical threshold (8)")
    # 0.8.27: no quality draws its text in pure white (The Armory's ScribingModule owns it); Normal = the near-white below, the rest unchanged
    _nw, _pw = "#fefefe", "#ffffff"   # ui-data (quality asset colours)
    if quals["Skyy_Bag_Normal"]["TextColor"] != _nw or any(q["TextColor"].lower() == _pw for q in quals.values()) \\
            or any(quals[r[0]]["TextColor"] != r[2] for r in BAG_RARITY[1:]):
        raise SystemExit("0.8.27 asset check: quality text colours %s" % dict((k, q["TextColor"]) for k, q in quals.items()))
''')
P.rep('''    ", ".join("%s %s" % (r[1], r[2]) for r in BAG_RARITY)))
''', '''    ", ".join("%s %s" % (r[1], json.loads(files["Server/Item/Qualities/%s.json" % r[0]])["TextColor"]) for r in BAG_RARITY)))   # 0.8.27: as shipped
''')
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.27 adds no system / command"
P.finish()
