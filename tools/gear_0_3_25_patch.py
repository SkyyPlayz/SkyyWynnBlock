"""Derive SkyyGear/build_skyygear_0.3.25.py from the LIVE 0.3.24 (build_skyygear_0.3.24.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_24_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_25_patch.py      then      python SkyyGear/build_skyygear_0.3.25.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.25.py   (the 0.3.23 chain on this jar + S325 + H325; --static needs no jar)

0.3.25 (2026-10-18) = THE LIFELONG MULTITOOL MERGE + three small review follow-ups (RESUME NEXT 1 + 5; main session "Gear 0.3.25: multitool merge,
accBp cache, GearReq red row, CAD trust A2"; Skyy 2026-10-18 "work through your whole todo list").
  1. THE LIFELONG MULTITOOL (docs/answered/gear.md: 2026-10-11 "MULTITOOL unlocks after the FIRST rebirth: merge pickaxe + axe, no stat loss, no
     downside"; 2026-10-12 "Fold it in, lock to rebirth 1"; 2026-10-15 "when you hit rebirth 1 and can make a multi tool id just add that as a
     button here in the tools tab"; 2026-10-16 MULTITOOL = TWO STAT SETS: "keep the axe and pickaxe stats seprate like they are still 2 tools ...
     when breaking logs it uses the hatchet spec, and when mining it uses the pickaxe specs ... as a multitool it only takes 1 slot, and when
     upgrading tiers it only takes 1 upgrade"). Gear 0.3.23 shipped the items; this is the player path.
     - THE BUTTON: Tools tab (/toolpoints, /multitool), pickaxe and hatchet panels, "Make multitool": your LIFELONG pickaxe + LIFELONG hatchet,
       both on you, of the SAME tier (Tool_Pickaxe_<X> + Tool_Hatchet_<X> -> Tool_Hatchet_Pickaxe_Multitool_<X>; Iron + Copper = refused with
       "not the same tier - tier one of them up first"); multi.rebirthGate (off by default, like today) = after rebirth 1. The row previews what
       the multitool keeps; the drawn pair must still be the same two stacks at the click; the FIRST click arms it (8 s), the second merges (the
       Harvester's rule - it can't be undone by a player). The old crafted-pair row is gone from the Tools tab (that page only exists with
       lifelong tools on; the part.lifelong-off Multitool page is unchanged).
     - WHAT IS KEPT (nothing is lost): the multitool IS the pickaxe kind's tool (the pickaxe's uid + slot; pickaxe.id = the multitool), the
       hatchet kind keeps ALL its points (hatchet.up.*, .resets, .rb*) = the HATCHET SET; the pickaxe kind's points = the PICKAXE SET. Stone /
       ore use the pickaxe set + Mining level, logs the hatchet set + Foraging level (GearTool.mstats; Vein Mine / Tree Feller caps by each
       skill); Mining points buy the pickaxe set, Foraging points the hatchet set (both rows stay on the Tools tab). The item: the better rarity,
       EVERY modifier line of both tools (they are the multitool's pickaxe + hatchet keys - never lowered; a line that cannot be on a multitool
       refuses the merge), the higher reforge / Sigil counts, the better tool's reforge name. NO DOWNSIDE (new row multi.lifelongFull, on): a
       lifelong multitool skips the crafted multitool's x85 % speed / x70 % Fortune share. Each set keeps its own rebirth modifier.
     - ONE TIER-UP RAISES BOTH (new row multi.ladders = Crude .. Lumen, 16 steps; the vanilla tiers are InkBlindCat's Multitools items, the zone
       metals ours): a step costs the HATCHET step's bars + Enchanted log (+ the lifelong.stickCost sticks) and needs Mining AND Foraging at the
       new tier's start and both tools' collection tokens. Only YOUR lifelong multitool climbs it (a crafted one stays plain).
     - ITEM SAFETY (the 0.3.12 Harvester machinery): a verified History copy of the registry (mtmerge/history/<pk>.properties.<stamp>.bak) and a
       record line (mtmerge/<pk>.log: MERGE stamp, both uids, ids and documents) FIRST; then the journal mt.pend / mt.hatU / mt.id / mt.doc /
       mt.at on disk; (a) the hatchet leaves, (b) the pickaxe's slot becomes the multitool (same uid), (c) ONE registry write (mtFinal: mt=1,
       mtAt, mtHatch, pickaxe.id, the hatchet's tool keys go, its points stay, the snapshot names the multitool). Any refusal restores; a crash
       = mtRecover at the next look finishes it from the journal or drops it (both tools still there = nothing happened). Counted before /
       after (one hatchet + one pickaxe out, one multitool in). The hatchet that turns up later is RETIRED (breaks nothing), an old pickaxe copy
       with the multitool's uid is removed (one exists), /hatchet answers "part of your multitool - /pickaxe brings it back", /lifelong refuses
       a hatchet or any plain multitool; the migration never marks a plain multitool. gear:fn:lifelong "hatchet" answers the multitool's uid
       (SkyyTrees' Tree Feller on logs) and still counts four kinds.
     - NO ADMIN UNDO COMMAND this round (no new command): the History copy + the record line hold everything an admin needs to put both back.
  2. accBp PER-HIT CACHE (0.3.18 review LOW): GearTool.accBp (accessory Breaking Power, read on every block hit) is cached per player + skill
     for 50 ms (about one tick) and the config epoch (GearTool.BPC, bounded 4096); the old body is accBp0 (unchanged math).
  3. GearReq MISSING RED ROW (0.3.18 review LOW): the Upgrade list's Requip row had the level + material rows but no collection row (a tool
     whose collection gate refused showed no red row for it) - + GearReq.collRow; and the multitool's second skill / collection rows (Foraging,
     the hatchet token) so GearReq.listed never swallows a refusal the list does not show.
  4. CHARGED ATTACK DAMAGE TRUST FOR THE A2 WEAPONS (round A2 follow-up, the 0.3.24 note "the stat does not roll on them yet"): SkyyArmory
     0.1.34's 72 Weapon_<Sword|Longsword|Axe|Battleaxe|Mace|Club|Daggers|Spear|Shortbow>_<Lead|Dusk|Chromium|Azurvane|Slag|Cinder|Titanium|
     Lumen>_SkyWynn join CHG_TRUST (GearChg.TRUST) like their vanilla families: each is a vanilla template child or names the vanilla item's own
     interaction chain with its damage vars (asserted per item, read from SkyyArmory-0.1.34.jar, else reproduced from the vanilla Iron item);
     the build-time walk proves every non-club one may roll (GearChg.FALLBACK) - clubs stay out (CHG_EXCL "Weapon_Club_", Skyy "Leave clubs
     alone"), shields are not gear.
  CRITIC FIXES (same version): M1 a hard stop after the registry commit but before the inventory save leaves the plain pickaxe with the
     multitool's uid - it is turned into the multitool IN PLACE from the snapshot (never removed; removed only when the real multitool with that
     uid is also there); the same "only with the merged twin present" rule for the old sickle copy of a Harvester (left alone otherwise). L1 a
     /pickaxe or /hatchet replacement copy (rp) can't be merged. L2 GearNorm.ready waits on mt.pend. L3 harness: crash 62 + a committed rebirth.
Commands: none new. Classes: none new. Config: + multi.ladders, multi.lifelongFull (absent = the default; no one-time update).
SAVED DATA: registry keys mt / mtAt / mtHatch (+ the journal mt.pend / mt.hatU / mt.id / mt.doc / mt.at); Skyy_SkyyGear/mtmerge/<pk>.log +
mtmerge/history/. ROLLBACK 0.3.25 -> 0.3.24: NOT item-clean for merged profiles - 0.3.24 knows no multitool kind (kOf -1): the merged multitool
stays in the inventory but stops working as a lifelong tool and the next look would give a NEW Crude pickaxe and re-adopt nothing for the hatchet
(its uid left the registry). Before a rollback: no merges (multi.rebirthGate on with SkyyRebirth, or part.multitool off), and for merged profiles
restore lifelong/<pk>.properties from mtmerge/history/ and give the hatchet back from the mtmerge/<pk>.log document. Profiles that never merged
are unaffected.
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.24.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.25.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.24"' in s and "GENERATED by tools/gear_0_3_24_patch.py" in s, "not the generated 0.3.24 script"
assert "mtCheck" not in s and "multi.ladders" not in s and "G25_A2" not in s and "accBp0" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
MK0 = s.count(' = mk("')
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def after(anchor, text):
    rep(anchor, anchor + text)


def before(anchor, text):
    rep(anchor, text + anchor)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.24":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.24" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.25 (2026-10-18)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.24 - build script (javassist via jpype). GENERATED by tools/gear_0_3_24_patch.py from the LIVE 0.3.23 (itself GENERATED by
tools/gear_0_3_23_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.24.py -> SkyyGear/SkyyGear-0.3.24.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.24.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''', '''"""SkyyGear 0.3.25 - build script (javassist via jpype). GENERATED by tools/gear_0_3_25_patch.py from the LIVE 0.3.24 (itself GENERATED by
tools/gear_0_3_24_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.25.py -> SkyyGear/SkyyGear-0.3.25.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.25.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''' + NOTE + '''
--- 0.3.24 notes ---
''')
rep('VERSION = "0.3.24"\n', 'VERSION = "0.3.25"\n')

# ================================================================================================================ 4: Charged Attack Damage trust (A2)
after('''_OVL = dict(_MCT)
_OVL.update(_OWN)
''', '''# 0.3.25 (tools/gear_0_3_25_patch.py item 4, round A2 follow-up): SkyyArmory 0.1.34's vanilla-family weapons in the 8 zone metals are trusted like
# their vanilla families - each is a vanilla template child or names the vanilla item's own chain with its damage vars (asserted below, after the
# walker). Clubs are trusted like the vanilla clubs and stay excluded (CHG_EXCL); shields are not gear (no shield id here).
G25_FAMS = ["Sword", "Longsword", "Axe", "Battleaxe", "Mace", "Club", "Daggers", "Spear", "Shortbow"]
G25_MET = ["Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]
G25_A2 = ["Weapon_%s_%s_SkyWynn" % (_f, _m) for _f in G25_FAMS for _m in G25_MET]
assert len(G25_A2) == len(set(G25_A2)) == 72 and not set(G25_A2) & set(OWN_TRUST) and not set(G25_A2) & set(PACK_TRUST)
_g25j = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SkyyArmory", "SkyyArmory-0.1.34.jar")
_G25 = {}
if os.path.isfile(_g25j):
    with zipfile.ZipFile(_g25j) as _z:
        for _n in _z.namelist():
            _b = os.path.basename(_n)[:-5]
            if _n.startswith("Server/Item/Items/") and _n.endswith(".json") and _b in G25_A2:
                _G25[_b] = json.loads(_z.read(_n).decode("utf-8-sig"))
    assert sorted(_G25) == sorted(G25_A2), "SkyyArmory 0.1.34 lacks %s" % sorted(set(G25_A2) - set(_G25))
    G25_FROM = "SkyyArmory-0.1.34.jar"
else:
    _G25 = dict((_i, {"Parent": "Weapon_%s_Iron" % _i.split("_")[1]}) for _i in G25_A2)
    G25_FROM = "REPRODUCED from the vanilla Iron item of each family (no SkyyArmory/SkyyArmory-0.1.34.jar)"
    print("note: A2 weapons " + G25_FROM)
_OVL.update(_G25)
''')
after('''assert not [i for i in OWN_TRUST if i in AZ_NAMES or not str(CW.items.get(i)).startswith("overlay:")], "an own id is a vanilla id now"
''', '''assert not [i for i in G25_A2 if i in AZ_NAMES or not str(CW.items.get(i)).startswith("overlay:")], "0.3.25: an A2 id is a vanilla id now"
for _i, _d in _G25.items():          # 0.3.25: the vanilla family's own chain (a template Parent, or the vanilla root interactions by id)
    _fam = _i.split("_")[1]
    _p = _d.get("Parent")
    _ia = _d.get("Interactions") or {}
    assert (_p is not None and (_p.startswith("Template_Weapon_") or _p == "Weapon_%s_Iron" % _fam) and str(CW.items.get(_p, "")) and not _ia) or \\
        (_p is None and _ia and all(isinstance(_v, str) and _v in CW.inter for _v in _ia.values())), "A2 %s: not a vanilla chain (%s, %s)" % (_i, _p, _ia)
''')
rep('''CHG_TRUST = sorted(set(VANILLA_WEAPONS) | set(PACK_TRUST) | set(OWN_TRUST))
''', '''CHG_TRUST = sorted(set(VANILLA_WEAPONS) | set(PACK_TRUST) | set(OWN_TRUST) | set(G25_A2))          # 0.3.25: + the 72 A2 weapons
''')
rep('''CHG_FAMILIES = {"Weapon_Sword_": (23, 23), "Weapon_Battleaxe_": (15, 15), "Weapon_Mace_": (12, 12), "Weapon_Daggers_": (17, 17),
                "Weapon_Axe_": (13, 13), "Weapon_Longsword_": (21, 20), "Weapon_Spear_": (17, 17), "Weapon_Shortbow_": (19, 14),
                "Weapon_Crossbow_": (8 + 12, 8 + 12), "Weapon_Staff_": (26, 24), "Weapon_Wand_": (5, 3), "Weapon_Spellbook_": (6, 5),          # 0.3.23: Crossbow + the 12 own (OWN_TRUST)
                "Weapon_Club_": (23, 0), "Weapon_Kunai": (1, 0)}     # 0.2.24: Hytale 0.7.0 counts (Daggers, Longsword, Staff, Club)
''', '''CHG_FAMILIES = {"Weapon_Sword_": (23 + 8, 23 + 8), "Weapon_Battleaxe_": (15 + 8, 15 + 8), "Weapon_Mace_": (12 + 8, 12 + 8), "Weapon_Daggers_": (17 + 8, 17 + 8),
                "Weapon_Axe_": (13 + 8, 13 + 8), "Weapon_Longsword_": (21 + 8, 20 + 8), "Weapon_Spear_": (17 + 8, 17 + 8), "Weapon_Shortbow_": (19 + 8, 14 + 8),
                "Weapon_Crossbow_": (8 + 12, 8 + 12), "Weapon_Staff_": (26, 24), "Weapon_Wand_": (5, 3), "Weapon_Spellbook_": (6, 5),          # 0.3.23: Crossbow + the 12 own (OWN_TRUST)
                "Weapon_Club_": (23 + 8, 0), "Weapon_Kunai": (1, 0)}     # 0.2.24: Hytale 0.7.0 counts (Daggers, Longsword, Staff, Club); 0.3.25: + 8 A2 each
''')
after('''assert [i for i in CHG_FALLBACK if not chg_gear(i) or chg_excluded(i)] == []
''', '''# 0.3.25: every A2 weapon but the clubs may roll Charged Attack Damage (the vanilla family's rule), no club does
_g25no = [i for i in G25_A2 if not i.startswith("Weapon_Club_") and i not in CHG_FALLBACK]
assert not _g25no and not [i for i in G25_A2 if i.startswith("Weapon_Club_") and i in CHG_FALLBACK], "A2 weapons that would not roll: %s" % _g25no
print("0.3.25 Charged Attack Damage trust: + %d A2 weapons (%s), %d may roll (clubs excluded)" % (len(G25_A2), G25_FROM, len([i for i in G25_A2 if i in CHG_FALLBACK])))
''')

# ================================================================================================================ 1a: the multitool ladder + rows
after('''G23_HARV_LAD = _g23_ids(HARV_LAD_DEF)
''', '''# 0.3.25 THE LIFELONG MULTITOOL LADDER (multi.ladders; tools/gear_0_3_25_patch.py item 1): the multitool's 16 steps = the pickaxe / hatchet metals
# (Crude .. Lumen; the vanilla tiers are InkBlindCat's Multitools items, the zone metals ours). ONE tier-up raises both sets (Skyy 2026-10-16 "when
# upgrading tiers it only takes 1 upgrade"), so a step costs what the HATCHET's step costs (its bars + its Enchanted log) + the stick rule.
def _g25_mid(m):
    return MULTI_PRE + m if (m == "Crude" or m in MULTI_TIERS) else MULTI_PRE + m + "_SkyWynn"


_g25h = G23_LADROW["hatch"].split(">")
assert _g25h[0] == "Tool_Hatchet_Crude" and len(_g25h) == len(G23_ORDER) + 1
MT_LAD_DEF = _g25_mid("Crude")
for _m, _st in zip(G23_ORDER, _g25h[1:]):
    assert _st.split("(")[0] == _g23_id("hatch", _m), (_m, _st)
    MT_LAD_DEF += ">%s(%s" % (_g25_mid(_m), _st.split("(", 1)[1])
G25_MT_LAD = _g23_ids(MT_LAD_DEF)
assert len(G25_MT_LAD) == 16 and set(G25_MT_LAD) <= set([MULTI_PRE + _t for _t in MULTI_TIERS] + G23_MULTI) and set(G23_MULTI) <= set(G25_MT_LAD)
assert len(MT_LAD_DEF) < 2000 and all(32 <= ord(_c) < 127 for _c in MT_LAD_DEF), len(MT_LAD_DEF)
''')
after('''G324_ROWK = ["move.armoryJump"]
assert all(32 <= ord(_c) < 127 for _c in G324_HEAD) and "=" not in G324_HEAD
''', '''# 0.3.25 THE LIFELONG MULTITOOL: two rows (absent = the default; no one-time update)
G325_HEAD = "# ---- the lifelong multitool: its tier-up costs, no slowdown (SkyyGear 0.3.25) ----"
G325_ROWK = ["multi.ladders", "multi.lifelongFull"]
assert all(32 <= ord(_c) < 127 for _c in G325_HEAD) and "=" not in G325_HEAD
''')
after('''    ("harvester.ladders", "Harvester tier-up costs", "lifelong", "text", HARV_LAD_DEF, "0", "2000", "", "", "live,danger",
     "Harvester tiers on the Anvil, like lifelong.ladders: A>B(Id*25), ladders joined by commas.", "field:GearCfg.HARV_LADDERS;check=GearUp.checkLadders"),
''', '''    # 0.3.25 THE LIFELONG MULTITOOL (tools/gear_0_3_25_patch.py item 1)
    ("multi.ladders", "Multitool tier-up costs", "lifelong", "text", MT_LAD_DEF, "0", "2000", "", "", "live,danger",
     "Lifelong multitool tiers (one tier-up = both sets), like lifelong.ladders: A>B(Id*25).", "field:GearCfg.MULTI_LADDERS;check=GearUp.checkLadders"),
    ("multi.lifelongFull", "Lifelong multitool: no slowdown", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = a merged lifelong multitool works at full speed and Fortune. Off = the multitool share.", "field:GearCfg.MULTI_LLFULL"),
''')
rep('''              ("MOVE_RIDE", "String", '"ride"')]          # 0.3.24''',
    '''              ("MOVE_RIDE", "String", '"ride"'),          # 0.3.24
              ("MULTI_LADDERS", "String", jstr(MT_LAD_DEF)), ("MULTI_LLFULL", "boolean", "true")]          # 0.3.25''')
after('''  HARV_LADDERS = ptext(p, "harvester.ladders", "@HARVLADDEF@").trim();          // 0.3.23: Crude .. Lumen
''', '''  MULTI_LADDERS = ptext(p, "multi.ladders", "@MTLADDEF@").trim();          // 0.3.25: the lifelong multitool's ladder
  MULTI_LLFULL = pbool(p, "multi.lifelongFull", true);          // 0.3.25: a lifelong multitool has no speed / Fortune share
''')
rep('''   .replace("@CANLADDEF@", CAN_LAD_DEF).replace("@HARVLADDEF@", HARV_LAD_DEF))          # 0.3.23''',
    '''   .replace("@CANLADDEF@", CAN_LAD_DEF).replace("@HARVLADDEF@", HARV_LAD_DEF).replace("@MTLADDEF@", MT_LAD_DEF))          # 0.3.23; 0.3.25''')
after('''    L += ["", G324_HEAD]        # 0.3.24: the new row (absent = ride; no one-time update)
    for k in G324_ROWK:
        scal(k)
''', '''    L += ["", G325_HEAD]        # 0.3.25: the two multitool rows (absent = the default; no one-time update)
    for k in G325_ROWK:
        scal(k)
''')
after('''assert _dp.get("move.armoryJump") == "ride", "0.3.24: the fresh file rides The Armory's jump stat"
''', '''assert _dp.get("multi.ladders") == MT_LAD_DEF and _dp.get("multi.lifelongFull") == "true", "0.3.25: the fresh file's multitool rows"
''')

rep('''           "gate.nextByLadder"}          # 0.3.23: gathering speed
''', '''           "gate.nextByLadder",          # 0.3.23: gathering speed
           "multi.ladders", "multi.lifelongFull"}          # 0.3.25: the lifelong multitool's tier-up costs + speed / Fortune (economy)
''')

# the default file is one Java string constant: with the two new rows it passed the class file's 65,535-byte constant limit (javassist
# UTFDataFormatException) - built from 16,000-character literals at run time (the same text)
rep('''M(gcf, "public static String defaultsText() { return " + jlit(DEFAULT_TEXT) + "; }")''',
    '''M(gcf, "public static String defaultsText() { return new StringBuilder()" + "".join(".append(" + jlit(DEFAULT_TEXT[_q:_q + 16000]) + ")" for _q in range(0, len(DEFAULT_TEXT), 16000)) + ".toString(); }")          # 0.3.25: < 64 KB per constant''')

# ================================================================================================================ 1b: GearLL - the multitool kind
after('''F(gll, "public static final String HARV_LAD = %s;" % jstr(",".join(G23_HARV_LAD)))          # 0.3.23: Crude .. Lumen
''', '''F(gll, "public static final String MT_LAD = %s;" % jstr(",".join(G25_MT_LAD)))          # 0.3.25: the lifelong multitool's ladder (Crude .. Lumen)
F(gll, "public static final String MT_CRUDE = %s;" % jstr(G25_MT_LAD[0]))
''')
rep('''M(gll, "public static int kOf(String id) { return id == null ? -1 : (@PKG@.GearData.pole(id) ? POLE : (@PKG@.GearData.can(id) ? CAN : kOfFam(@PKG@.GearData.toolFam(id)))); }")          # 0.3.5: + the pole; 0.3.12: + the can''',
    '''# 0.3.25: a multitool is the PICKAXE kind's tool (the lifelong merge; whatever part.multitool says - off would read it as a hatchet)
M(gll, "public static int kOf(String id) { return id == null ? -1 : (@PKG@.GearData.multiId(id) ? 0 : (@PKG@.GearData.pole(id) ? POLE : (@PKG@.GearData.can(id) ? CAN : kOfFam(@PKG@.GearData.toolFam(id))))); }")          # 0.3.5: + the pole; 0.3.12: + the can; 0.3.25: + the multitool''')
after('''M(gll, "public static boolean merged(java.util.Properties P) { return P != null && \\"1\\".equals(P.getProperty(\\"harv\\")); }")
''', '''# 0.3.25 THE LIFELONG MULTITOOL (tools/gear_0_3_25_patch.py item 1): mt=1 = the profile's lifelong pickaxe + hatchet are ONE multitool = the
# pickaxe kind's tool (its uid; pickaxe.id = the multitool); the hatchet kind keeps only its points (hatchet.up.* / .resets / .rb*) = the HATCHET SET.
# hostK = the kind whose registry names the tool kind k's numbers use; kid = that tool's id
M(gll, "public static boolean mtm(java.util.Properties P) { return P != null && \\"1\\".equals(P.getProperty(\\"mt\\")); }")
M(gll, "public static int hostK(java.util.Properties P, int k) { return k == 1 && mtm(P) ? 0 : k; }")
M(gll, r"""
public static String kid(java.util.Properties P, int k) {
  if (P == null || k < 0 || k >= KIND.length) return null;
  return P.getProperty(KIND[hostK(P, k)] + ".id");
}""")
''')
rep('''public static String crudeOf(int k, String id) {
  if (k == 3 && harv(id)) return HARV_PRE + "Crude";''', '''public static String crudeOf(int k, String id) {
  if (k == 3 && harv(id)) return HARV_PRE + "Crude";
  if ((k == 0 || k == 1) && @PKG@.GearData.multiId(id)) return MT_CRUDE;          // 0.3.25''')
rep('''public static String ladOf(int k, String id) {
  if (k == 3 && harv(id)) return HARV_LAD;''', '''public static String ladOf(int k, String id) {
  if (k == 3 && harv(id)) return HARV_LAD;
  if ((k == 0 || k == 1) && @PKG@.GearData.multiId(id)) return MT_LAD;          // 0.3.25''')
rep('''public static String kname(int k, String id) {
  if (k == 3 && harv(id)) return "Harvester";''', '''public static String kname(int k, String id) {
  if (k == 3 && harv(id)) return "Harvester";
  if ((k == 0 || k == 1) && @PKG@.GearData.multiId(id)) return "Multitool";          // 0.3.25''')
before('''# fix round (Skyy G2 "so lvl 20 mining you get a lvl 20 common iron pickaxe"): the tier /pickaxe gives = the FIRST tier on the kind's ladder
''', '''# 0.3.25: kind k's level rule for the tool id it has now (levelFor asks the id's own kind; the multitool's HATCHET set levels with Foraging)
M(gll, r"""
public static int levelK(java.util.UUID u, int k, String id) {
  if (id == null || k < 0 || k >= KSKILL.length) return -1;
  int h = skill(u, k);
  if (h == -2) return -1;
  if (h < 0) h = 0;
  int f = @PKG@.GearLevel.floor(h);
  int c = cap(id);
  int lv = f < c ? f : c;
  return lv < 1 ? 1 : lv;
}""")
''')
rep('''  String id = P == null ? null : P.getProperty(KIND[k] + ".id");
  int t = id == null ? 0 : tier(id);''', '''  String id = kid(P, k);          // 0.3.25: the multitool for its hatchet set
  int t = id == null ? 0 : tier(id);''')
rep('''  String id = P.getProperty(KIND[k] + ".id");
  if (id == null) id = KCRUDE[k];
  int lv = u == null ? -1 : levelFor(u, id);''', '''  String id = kid(P, k);          // 0.3.25: the multitool for its hatchet set (Tree Feller caps by Foraging)
  if (id == null) id = KCRUDE[k];
  int lv = u == null ? -1 : levelK(u, k, id);''')
rep('''((@PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0) ||''', '''((@PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0 && !@PKG@.GearData.multiId(id)) ||''')
# ladders(): + the multitool row
after('''  if (@PKG@.GearCfg.LL_ON && hl.length() > 0) r = r.trim().length() == 0 ? hl : r + "," + hl;
''', '''  String ml = @PKG@.GearCfg.MULTI_LADDERS == null ? "" : @PKG@.GearCfg.MULTI_LADDERS.trim();          // 0.3.25: the lifelong multitool (multi.ladders)
  if (@PKG@.GearCfg.LL_ON && @PKG@.GearCfg.MULTI_ON && ml.length() > 0) r = r.trim().length() == 0 ? ml : r + "," + ml;
''')
# collWhy: the multitool needs both tools' collection tokens
rep('''public static String collWhy(java.util.UUID u, String to) {
  if (!@PKG@.GearCfg.LL_COLLGATE || u == null || to == null) return null;
  String ck = collKind(to);
  if (ck == null) return null;''', '''public static String collWhy0(java.util.UUID u, String to, String ck) {
  if (!@PKG@.GearCfg.LL_COLLGATE || u == null || to == null) return null;
  if (ck == null) return null;''')
after('''  return "Needs the " + a[2] + " collection " + roman(t) + " (" + a[5] + " / " + a[4] + ") to tier up to " + an(@PKG@.Gear.itemName(to)) + " - /collections.";
}""")
''', '''# 0.3.25: a multitool tier-up needs BOTH tools' collection tokens (pickaxe:<metal>, then hatchet:<metal>)
M(gll, r"""
public static String collWhy(java.util.UUID u, String to) {
  String w = collWhy0(u, to, collKind(to));
  if (w == null && @PKG@.GearData.multiId(to)) w = collWhy0(u, to, "hatchet");
  return w;
}""")
''')
rep('''  if (@PKG@.GearLevel.floor(h) >= need) return collWhy(u, to);          // 0.3.17: + the collection gate
  return "You need " + KSKILL[k] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h + ").";''',
    '''  if (@PKG@.GearLevel.floor(h) < need) return "You need " + KSKILL[k] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h + ").";
  if (@PKG@.GearData.multiId(to)) {          // 0.3.25: the multitool's hatchet set levels with Foraging - one tier-up raises both
    int h1 = skill(u, 1);
    if (h1 != -2) {
      if (h1 < 0) h1 = 0;
      if (@PKG@.GearLevel.floor(h1) < need) return "You need " + KSKILL[1] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h1 + ").";
    }
  }
  return collWhy(u, to);          // 0.3.17: + the collection gate''')
# the tooltip of a lifelong multitool: both sets
rep('''  txt.add("Lifelong " + kname(k, id).toLowerCase() + ": levels with " + KSKILL[k] + " (max Lv " + cap(id) + ")");          // 0.3.12: "watering can", "harvester"''',
    '''  boolean mt25 = k == 0 && @PKG@.GearData.multiId(id);          // 0.3.25: the lifelong multitool's two sets
  txt.add("Lifelong " + kname(k, id).toLowerCase() + ": levels with " + (mt25 ? KSKILL[0] + " (pickaxe set) and " + KSKILL[1] + " (hatchet set)" : KSKILL[k]) + " (max Lv " + cap(id) + ")");          // 0.3.12: "watering can", "harvester"''')
rep('''    if (sb.length() > 0) { txt.add("Upgrades: " + sb.toString()); col.add(null); }
    int fr = free(ow, P, k);
    if (fr > 0) { txt.add(fr + " Upgrade Point" + (fr == 1 ? "" : "s") + " free - /toolpoints"); col.add(@PKG@.GearDefs.C_GOLD); }''',
    '''    if (sb.length() > 0) { txt.add((mt25 ? "Pickaxe set (stone, ore): " : "Upgrades: ") + sb.toString()); col.add(null); }
    int fr = free(ow, P, k);
    if (fr > 0) { txt.add(fr + " Upgrade Point" + (fr == 1 ? "" : "s") + " free" + (mt25 ? " (pickaxe set)" : "") + " - /toolpoints"); col.add(@PKG@.GearDefs.C_GOLD); }
    if (mt25 && mtm(P)) {          // 0.3.25: the hatchet set (logs)
      StringBuilder sh = new StringBuilder();
      for (int p = 0; p < PK.length; p++) {
        int lh = perkEff(ow, P, 1, p);
        if (lh <= 0) continue;
        if (sh.length() > 0) sh.append(", ");
        sh.append(PKN[p]).append(' ').append(lh);
      }
      if (sh.length() > 0) { txt.add("Hatchet set (logs): " + sh.toString()); col.add(null); }
      int fh = free(ow, P, 1);
      if (fh > 0) { txt.add(fh + " Upgrade Point" + (fh == 1 ? "" : "s") + " free (hatchet set) - /toolpoints"); col.add(@PKG@.GearDefs.C_GOLD); }
    }''')

# ================================================================================================================ 1c: GearTool - the two sets, no downside
rep('''  double sp = @PKG@.GearCfg.PART_TOOLS ? (double) @PKG@.GearCfg.MULTI_SPD / 100.0 : 1.0;
  double fp = (double) @PKG@.GearCfg.MULTI_FORT / 100.0;
  double pm = sp;''', '''  boolean llm = @PKG@.GearLL.mine(u, d);          // 0.3.25: YOUR lifelong multitool (the Tools tab merge)
  boolean full = llm && @PKG@.GearCfg.MULTI_LLFULL;          // Skyy 2026-10-11 "merge pickaxe + axe, no stat loss, no downside" (multi.lifelongFull)
  double sp = @PKG@.GearCfg.PART_TOOLS && !full ? (double) @PKG@.GearCfg.MULTI_SPD / 100.0 : 1.0;
  double fp = full ? 1.0 : (double) @PKG@.GearCfg.MULTI_FORT / 100.0;
  double pm = sp;''')
rep('''    double[] b = eff(3, g[1], t, d);''', '''    int gh = llm ? @PKG@.GearLL.levelK(u, 1, id) : g[1];          // 0.3.25: the hatchet set works at your Foraging level (logs)
    if (gh < 1) gh = g[1];
    double[] b = eff(3, gh, t, d);''')
rep('''    double xm = @PKG@.GearLL.mine(u, d) ? @PKG@.GearLL.rbMult(u, 0) : 1.0;          // 0.3.5 fix: the rebirth modifier (lifelong only)
    if (xm > 1.0) {
      pm = pm * xm; if (pm > @PKG@.GearCfg.pmax()) pm = @PKG@.GearCfg.pmax();
      pc = pc * xm; if (pc > @PKG@.GearCfg.pmax()) pc = @PKG@.GearCfg.pmax();
      fm = fm * xm; if (fm > @PKG@.GearCfg.fcap()) fm = @PKG@.GearCfg.fcap(); fm = r1(fm);
      fc = fc * xm; if (fc > @PKG@.GearCfg.fcap()) fc = @PKG@.GearCfg.fcap(); fc = r1(fc);
      wm = wm * xm; if (wm > @PKG@.GearCfg.TOOL_WCAP) wm = @PKG@.GearCfg.TOOL_WCAP;
      wc = wc * xm; if (wc > @PKG@.GearCfg.TOOL_WCAP) wc = @PKG@.GearCfg.TOOL_WCAP;
    }''', '''    double xm = llm ? @PKG@.GearLL.rbMult(u, 0) : 1.0;          // 0.3.5 fix: the rebirth modifier (lifelong only)
    double xh = llm ? @PKG@.GearLL.rbMult(u, 1) : 1.0;          // 0.3.25: each set its own (the hatchet set = the Foraging branch)
    if (xm > 1.0) {
      pm = pm * xm; if (pm > @PKG@.GearCfg.pmax()) pm = @PKG@.GearCfg.pmax();
      fm = fm * xm; if (fm > @PKG@.GearCfg.fcap()) fm = @PKG@.GearCfg.fcap(); fm = r1(fm);
      wm = wm * xm; if (wm > @PKG@.GearCfg.TOOL_WCAP) wm = @PKG@.GearCfg.TOOL_WCAP;
    }
    if (xh > 1.0) {
      pc = pc * xh; if (pc > @PKG@.GearCfg.pmax()) pc = @PKG@.GearCfg.pmax();
      fc = fc * xh; if (fc > @PKG@.GearCfg.fcap()) fc = @PKG@.GearCfg.fcap(); fc = r1(fc);
      wc = wc * xh; if (wc > @PKG@.GearCfg.TOOL_WCAP) wc = @PKG@.GearCfg.TOOL_WCAP;
    }''')

# ================================================================================================================ 2: accBp per-hit cache
rep('''public static double accBp(java.util.UUID u, String sk) {
  if (u == null || sk == null) return 1.0;
  try {
    Object o = @PKG@.Gear.bridge().get("skill:bonus:" + u.toString());''', '''public static double accBp0(java.util.UUID u, String sk) {
  if (u == null || sk == null) return 1.0;
  try {
    Object o = @PKG@.Gear.bridge().get("skill:bonus:" + u.toString());''')
after('''    @PKG@.Gear.warnOnce("accbp", "accessory Breaking Power read failed: " + t);
    return 1.0;
  }
}""")
''', '''# 0.3.25 (0.3.18 review LOW): accBp is asked on every block hit - the sum over every skill:bonus source is cached per player + skill for 50 ms
# (about one tick) and the config epoch (tool.power.max is live); bounded (cleared above 4096 entries). BPN: 0 reads, 1 cache hits
F(gtool, "public static final java.util.concurrent.ConcurrentHashMap BPC = new java.util.concurrent.ConcurrentHashMap();")
F(gtool, "public static final long BP_NS = 50000000L;")
F(gtool, "public static final long[] BPN = new long[2];")
M(gtool, r"""
public static double accBp(java.util.UUID u, String sk) {
  if (u == null || sk == null) return 1.0;
  String ck = u.toString() + "|" + sk;
  long now = System.nanoTime();
  long ep = @PKG@.GearCfg.EPOCH;
  Object o = BPC.get(ck);
  if (o instanceof Object[]) {
    Object[] e = (Object[]) o;
    long at = ((Long) e[1]).longValue();
    if (((Long) e[2]).longValue() == ep && now - at >= 0L && now - at < BP_NS) { BPN[1] = BPN[1] + 1L; return ((Double) e[0]).doubleValue(); }
  }
  double r = accBp0(u, sk);
  if (BPC.size() > 4096) BPC.clear();
  BPC.put(ck, new Object[] { Double.valueOf(r), Long.valueOf(now), Long.valueOf(ep) });
  BPN[0] = BPN[0] + 1L;
  return r;
}""")
''')

# ================================================================================================================ 3: GearReq rows + GearUp text
rep('''    add(rows, lvl(@PKG@.GearLL.KSKILL[k], need, h), @PKG@.GearLevel.floor(h) >= need ? 1 : 0);
    return;''', '''    add(rows, lvl(@PKG@.GearLL.KSKILL[k], need, h), @PKG@.GearLevel.floor(h) >= need ? 1 : 0);
    if (@PKG@.GearData.multiId(to)) {          // 0.3.25: the multitool's hatchet set (GearLL.tierWhy asks Foraging too)
      int h1 = @PKG@.GearLL.skill(u, 1);
      if (h1 != -2) {
        if (h1 < 0) h1 = 0;
        add(rows, lvl(@PKG@.GearLL.KSKILL[1], need, h1), @PKG@.GearLevel.floor(h1) >= need ? 1 : 0);
      }
    }
    return;''')
rep('''public static void collRow(java.util.UUID u, String from, String to, java.util.ArrayList rows) {
  if (!@PKG@.GearCfg.LL_COLLGATE || u == null || to == null || from == null || !@PKG@.GearLL.ladderTool(from)) return;
  String ck = @PKG@.GearLL.collKind(to);
  if (ck == null) return;''', '''public static void collRow0(java.util.UUID u, String from, String to, java.util.ArrayList rows, String ck) {
  if (!@PKG@.GearCfg.LL_COLLGATE || u == null || to == null || from == null || !@PKG@.GearLL.ladderTool(from)) return;
  if (ck == null) return;''')
after('''  add(rows, a[2] + " collection " + @PKG@.GearLL.roman(t2) + " " + a[4].trim() + " : " + a[5].trim(), "1".equals(a[0]) ? 1 : 0);
}""")
''', '''# 0.3.25: the multitool asks both tools' tokens (GearLL.collWhy)
M(gq, r"""
public static void collRow(java.util.UUID u, String from, String to, java.util.ArrayList rows) {
  collRow0(u, from, to, rows, to == null ? null : @PKG@.GearLL.collKind(to));
  if (to != null && @PKG@.GearData.multiId(to)) collRow0(u, from, to, rows, "hatchet");
}""")
''')
# the Upgrade list's Requip row: + the collection row (0.3.18 review LOW: a refused collection gate showed no red row there)
rep('''    if (to0 != null) { @PKG@.GearReq.levelRow(u, id, to0, rqs); @PKG@.GearReq.costRows(inv, u, @PKG@.GearUp.cost(id, to0), rqs); }''',
    '''    if (to0 != null) { @PKG@.GearReq.levelRow(u, id, to0, rqs); @PKG@.GearReq.collRow(u, id, to0, rqs); @PKG@.GearReq.costRows(inv, u, @PKG@.GearUp.cost(id, to0), rqs); }          // 0.3.25: + the collection row''')
rep('''    if (!@PKG@.GearLL.mine(u, d)) return new Object[] { "Only your lifelong " + @PKG@.GearLL.KIND[lk] + " can be tiered up - this one is a plain tool.", to, null };''',
    '''    if (!@PKG@.GearLL.mine(u, d)) return new Object[] { "Only your lifelong " + @PKG@.GearLL.kname(lk, id).toLowerCase() + " can be tiered up - this one is a plain tool.", to, null };          // 0.3.25: "multitool"''')
rep('''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return "Your lifelong " + w + " cannot be merged yet - merging lifelong tools into a multitool comes in a later update.";     // 0.3.0 (0.3.5 fix: the text)''',
    '''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return "Your lifelong " + w + " merges on the Tools tab (/toolpoints): carry your lifelong pickaxe and hatchet of one tier and click Make multitool.";     // 0.3.0 (0.3.5 fix; 0.3.25: the lifelong merge)''')

# ================================================================================================================ 1d: GearLife - the sweep rules
rep('''      if (@PKG@.GearLL.kOf(id) != k) continue;''', '''      if (@PKG@.GearLL.kOf(id) != k || @PKG@.GearData.multiId(id)) continue;          // 0.3.25: a plain multitool is never marked (the merge makes one)''')
after('''    if (k == 2 && @PKG@.GearLL.merged(P)) { done++; continue; }          // 0.3.12 fix round: the hoe is part of the Harvester
''', '''    if (k == 1 && @PKG@.GearLL.mtm(P)) { done++; continue; }          // 0.3.25: the hatchet is part of the multitool
''')
# critic M1 (0.3.25): a hard stop between the registry commit and the engine's inventory save leaves the ONLY stack (the plain pickaxe / sickle
# with the registered uid) - it is never removed unless its merged twin (same uid) is really in the inventory: the pickaxe is turned into the
# multitool in place from the registry snapshot (mtFinal names it); the sickle (no Harvester snapshot) is left alone
rep('''          if (k == 3 && @PKG@.GearLL.merged(P) && !@PKG@.GearLL.harv(id)) { remove(c, i, x, u, "an old copy of your sickle (" + lu + ") - it is part of your Harvester now"); continue; }          // 0.3.12 fix round
''', '''          if (k == 3 && @PKG@.GearLL.merged(P) && !@PKG@.GearLL.harv(id)) { if (twin(inv, pk, lu, 1)) remove(c, i, x, u, "an old copy of your sickle (" + lu + ") - it is part of your Harvester now"); continue; }          // 0.3.12 fix round; 0.3.25 critic M1: only while the Harvester is here
          if (k == 0 && @PKG@.GearLL.mtm(P) && !@PKG@.GearData.multiId(id)) {          // 0.3.25 (critic M1)
            if (twin(inv, pk, lu, 0)) { remove(c, i, x, u, "an old copy of your pickaxe (" + lu + ") - it is part of your multitool now"); continue; }
            if (!mtHeal(c, i, x, u, pk, P)) continue;          // never removed: it stays until it can become the multitool
            x = c.getItemStack((short) i);
            d = docOf(x);
            if (x == null || x.isEmpty() || d == null) continue;
            id = x.getItemId();
          }
''')
after('''        if (k == 2 && @PKG@.GearLL.merged(P)) { if (retire(c, i, x, d, u, "your hoe is part of your Harvester now")) dirty = true; continue; }          // 0.3.12
''', '''        if (k == 1 && @PKG@.GearLL.mtm(P)) { if (retire(c, i, x, d, u, "your hatchet is part of your multitool now")) dirty = true; continue; }          // 0.3.25
''')
after('''  if (k == 2 && @PKG@.GearLL.merged(P)) return "-Your hoe is part of your Harvester now - /harvester brings it back.";          // 0.3.12
''', '''  if (k == 1 && @PKG@.GearLL.mtm(P)) return "-Your hatchet is part of your multitool now - /pickaxe brings the multitool back.";          // 0.3.25
''')
after('''  if (k == 3 && @PKG@.GearLL.merged(P) && !@PKG@.GearLL.harv(x.getItemId())) return "-Your sickle is part of your Harvester now - hold your Harvester (/harvester) instead.";          // 0.3.12 fix round 2
''', '''  if (k == 1 && @PKG@.GearLL.mtm(P)) return "-Your hatchet is part of your multitool now - a hatchet can't be your lifelong tool again.";          // 0.3.25
  if (k == 0 && @PKG@.GearLL.mtm(P) && !@PKG@.GearData.multiId(id)) return "-Your pickaxe is part of your multitool now - hold your multitool (/pickaxe) instead.";
''')
before('''  if (d != null && !@PKG@.GearData.identified(d)) return "-Identify that tool first.";''',
       '''  if (@PKG@.GearData.multiId(id)) return "-A multitool can't be picked as a lifelong tool - merge your lifelong pickaxe and hatchet on the Tools tab (Make multitool).";          // 0.3.25
''')
rep('''  String id = P.getProperty(@PKG@.GearLL.KIND[k] + ".id");
  if (id == null) id = @PKG@.GearLL.KCRUDE[k];
  if (@PKG@.GearLL.isLine(p)) {''', '''  String id = @PKG@.GearLL.kid(P, k);          // 0.3.25: the multitool for its hatchet set
  if (id == null) id = @PKG@.GearLL.KCRUDE[k];
  if (@PKG@.GearLL.isLine(p)) {''')
rep('''    int tl = @PKG@.GearLL.levelFor(u, id);''', '''    int tl = @PKG@.GearLL.levelK(u, k, id);          // 0.3.25: kind k's skill (the hatchet set = Foraging)''')
rep('''  String id = P.getProperty(K + ".id");
  int t = id == null ? 0 : @PKG@.GearLL.tier(id);''', '''  String id = @PKG@.GearLL.kid(P, k);          // 0.3.25: the multitool for its hatchet set
  int t = id == null ? 0 : @PKG@.GearLL.tier(id);''')
after('''  harvRecover(pr, inv, pk, P);          // 0.3.12: a Harvester merge the server did not finish
''', '''  mtRecover(pr, inv, pk, P);          // 0.3.25: a multitool merge the server did not finish
''')
rep('''    if (this.mode == 0) return P.getProperty(@PKG@.GearLL.KIND[k] + ".uid");''',
    '''    if (this.mode == 0) return P.getProperty(@PKG@.GearLL.KIND[@PKG@.GearLL.hostK(P, k)] + ".uid");          // 0.3.25: "hatchet" = the multitool after the merge''')
rep('''      if (@PKG@.GearLL.merged(P0)) n0++;''', '''      if (@PKG@.GearLL.merged(P0)) n0++;
      if (@PKG@.GearLL.mtm(P0)) n0++;          // 0.3.25: the hatchet lives on in the multitool''')

# ================================================================================================================ 1e: GearLife - THE MERGE
MERGE = r'''# 0.3.25 THE LIFELONG MULTITOOL MERGE (tools/gear_0_3_25_patch.py item 1; Skyy 2026-10-11 "merge pickaxe + axe, no stat loss, no downside", 2026-10-16
# MULTITOOL = TWO STAT SETS, 2026-10-15 "add that as a button here in the tools tab"): your lifelong pickaxe + hatchet of ONE tier -> one lifelong
# multitool = the pickaxe kind's tool (its uid + slot); the hatchet kind keeps its points (the hatchet set). The Harvester's machinery: a verified
# History copy + the record line (mtmerge/) FIRST, then mt.pend / mt.hatU / mt.id / mt.doc / mt.at on disk before anything moves; the hatchet
# leaves; the pickaxe's slot gets the multitool; mtFinal = ONE registry write. mtRecover (every look) finishes or drops a journal.
F(glf, "public static final long[] MT = new long[6];")          # 0 made, 1 refused, 2 failed + restored, 3 finished by a later look, 4 journals dropped, 5 History / record failures
M(glf, r"""
public static void mtDrop(java.util.Properties P) {
  P.remove("mt.pend");
  P.remove("mt.hatU");
  P.remove("mt.id");
  P.remove("mt.doc");
  P.remove("mt.at");
}""")
# the multitool of a pickaxe + hatchet pair: Tool_Pickaxe_<X> + Tool_Hatchet_<X> -> Tool_Hatchet_Pickaxe_Multitool_<X>; "" = not the same tier, null = none
M(glf, r"""
public static String mtId(String pid, String hid) {
  if (pid == null || hid == null || !pid.startsWith("Tool_Pickaxe_") || !hid.startsWith("Tool_Hatchet_")) return null;
  String a = pid.substring(13);
  String b = hid.substring(13);
  if (!a.equals(b)) return "";
  String m = @PKG@.GearDefs.MULTI_PRE + a;
  return @PKG@.GearData.multiId(m) ? m : null;
}""")
# one input's lines into best[]: only the multitool's keys (GearDefs.S_TMASK bit 6 = the pickaxe + hatchet pools); NEVER lowered (Skyy "no stat loss");
# returns the lines that cannot be on a multitool (the merge refuses then); info[1] += lines above the multitool's own cap (kept as they are)
M(glf, r"""
public static int mtLines(int[] best, @BD@ d, String mid, int r, int L, int[] info) {
  int dropped = 0;
  if (d == null) return 0;
  @BA@ ms = @PKG@.GearData.mods(d);
  for (int k = 0; k < ms.size(); k++) {
    @BV@ v = ms.get(k);
    if (v == null || !v.isDocument()) { dropped++; continue; }
    @BD@ m = v.asDocument();
    int si = @PKG@.GearDefs.sIndex(@PKG@.GearData.str(m, "s", null));
    int val = @PKG@.GearData.num(m, "v", 0);
    if (si < 0 || (@PKG@.GearDefs.S_TMASK[si] & (1 << 6)) == 0 || val <= 0) { dropped++; continue; }
    if (val > @PKG@.GearMerge.capOf(si, mid, r, L)) info[1]++;
    if (val > best[si]) best[si] = val;
  }
  return dropped;
}""")
# THE MERGED DOCUMENT: the pickaxe's own (uid, owner, birth + rebirth stamps stay; replacement / retired marks go), the better rarity, EVERY line of
# both (the best value of each key), the higher reforge / Sigil counts, the better tool's reforge name, the multitool's kind + the level rule.
# info: [0] lines that cannot be on a multitool, [1] lines above the multitool's cap (kept), [2] lines kept, [3] the level
M(glf, r"""
public static @BD@ mtDoc(@BD@ pd, @BD@ hd, String mid, java.util.UUID u, int[] info) {
  if (pd == null || hd == null || mid == null) return null;
  int rp = @PKG@.GearData.rarity(pd);
  if (rp > @PKG@.GearDefs.R_MY) rp = 0;
  int rh = @PKG@.GearData.rarity(hd);
  if (rh > @PKG@.GearDefs.R_MY) rh = 0;
  int r = rh > rp ? rh : rp;
  @BD@ d = pd.clone();
  d.remove("lrp");
  d.remove("lrpT"); d.remove("lrpL");
  d.remove("lrt");
  d.remove("lrpF");
  d.remove("lrpS");
  d.remove("lcu");
  d.remove("lvU");
  String kd = @PKG@.GearData.kindFor(mid);
  d.put("kind", new org.bson.BsonString(kd));
  if (d.containsKey("gate")) d.put("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kd)));
  d.put("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[@PKG@.GearCfg.ri(r)]));
  d.put("tr", new org.bson.BsonInt32(1));
  int lv = @PKG@.GearLL.levelFor(u, mid);
  if (lv >= 1) d.put("lvl", new org.bson.BsonInt32(lv));
  int L = @PKG@.GearLevel.level(mid, d);
  int n = @PKG@.GearDefs.NS;
  int[] best = new int[n];
  int dropped = mtLines(best, pd, mid, r, L, info) + mtLines(best, hd, mid, r, L, info);
  @BA@ out = new @BA@();
  for (int i = 0; i < n; i++) if (best[i] > 0) out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], best[i]));
  d.put("mods", out);
  int rf = @PKG@.GearData.num(pd, "rfN", 0);
  int rf2 = @PKG@.GearData.num(hd, "rfN", 0);
  if (rf2 > rf) rf = rf2;
  if (rf > 0) d.put("rfN", new org.bson.BsonInt32(rf));
  String nm = rh > rp ? @PKG@.GearData.str(hd, "rf", null) : @PKG@.GearData.str(pd, "rf", null);
  if (nm == null) nm = rh > rp ? @PKG@.GearData.str(pd, "rf", null) : @PKG@.GearData.str(hd, "rf", null);
  if (nm != null) d.put("rf", new org.bson.BsonString(nm));
  int sg = @PKG@.GearData.num(pd, "sgN", 0);
  int sg2 = @PKG@.GearData.num(hd, "sgN", 0);
  if (sg2 > sg) sg = sg2;
  if (sg > 0) d.put("sgN", new org.bson.BsonInt32(sg));
  info[0] = dropped;
  info[2] = out.size();
  info[3] = L;
  return d;
}""")
# Object[] { String why (null = they can merge), int[] pickaxe slot, int[] hatchet slot, String multitool id, BsonDocument merged doc, int[] info }
M(glf, r"""
public static Object[] mtCheck(java.util.UUID u, @INV@ inv, String pk, java.util.Properties P) {
  String w = null;
  if (!@PKG@.GearCfg.LL_ON) w = "Lifelong tools are switched off on this server.";
  else if (!@PKG@.GearCfg.MULTI_ON) w = "Multitools are switched off on this server.";
  else if (u == null || inv == null) w = "Your inventory cannot be read right now.";
  else if (@PKG@.Gear.busy(u)) w = "Your profile is still loading - try again in a moment.";
  else if (P == null || @PKG@.GearLL.bad(P)) w = "Your lifelong tool list cannot be read right now.";
  else if (@PKG@.GearLL.mtm(P)) w = "You already have your multitool.";
  else if (P.getProperty("mt.pend") != null) w = "Your multitool is still being made - try again in a moment.";
  else if (!"1".equals(P.getProperty("migrated"))) w = "Your starting tools are still arriving - free an inventory slot and try again.";
  if (w == null) w = @PKG@.GearLL.rbGate(u);
  if (w == null && @PKG@.GearLL.rbWait(u)) w = "A rebirth is finishing on this profile - try again in a few seconds.";
  if (w != null) return new Object[] { w, null, null, null, null, null };
  String pu = P.getProperty("pickaxe.uid");
  String hu = P.getProperty("hatchet.uid");
  if (pu == null || hu == null) return new Object[] { "You need your lifelong pickaxe and hatchet first.", null, null, null, null, null };
  if (P.getProperty("pickaxe.pend") != null || P.getProperty("hatchet.pend") != null) return new Object[] { "Your tools are still being sorted out - try again in a moment.", null, null, null, null, null };
  int[] pa = find(inv, pk, pu);
  int[] ha = find(inv, pk, hu);
  if (pa == null && ha == null) return new Object[] { "Carry your lifelong pickaxe and hatchet (/pickaxe and /hatchet bring them back).", null, null, null, null, null };
  if (pa == null) return new Object[] { "Carry your lifelong pickaxe too (/pickaxe brings it back).", null, null, null, null, null };
  if (ha == null) return new Object[] { "Carry your lifelong hatchet too (/hatchet brings it back).", null, null, null, null, null };
  @IS@ p = @PKG@.GearStamp.at(inv, pa[0], pa[1]);
  @IS@ h = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
  if (p == null || h == null || p.isEmpty() || h.isEmpty()) return new Object[] { "Your tools moved - try again.", null, null, null, null, null };
  @BD@ pd = docOf(p);
  @BD@ hd = docOf(h);
  if (!@PKG@.GearLL.mine(u, pd) || !@PKG@.GearLL.mine(u, hd)) return new Object[] { "A retired tool can't be merged - hold it and type /lifelong to swap it back first.", null, null, null, null, null };
  if (@PKG@.GearData.multiId(p.getItemId())) return new Object[] { "Your pickaxe is a multitool already.", null, null, null, null, null };
  if ("1".equals(P.getProperty("pickaxe.rp")) || "1".equals(P.getProperty("hatchet.rp")) || @PKG@.GearLL.isRp(pd) || @PKG@.GearLL.isRp(hd))          // critic L1
    return new Object[] { "A replacement copy (from /pickaxe or /hatchet) can't be merged while your original may still turn up.", null, null, null, null, null };
  if (@PKG@.GearLL.kOf(p.getItemId()) != 0 || @PKG@.GearLL.kOf(h.getItemId()) != 1) return new Object[] { "Those are not your lifelong pickaxe and hatchet.", null, null, null, null, null };
  String mid = mtId(p.getItemId(), h.getItemId());
  if (mid != null && mid.length() == 0) return new Object[] { "Your " + @PKG@.Gear.itemName(p.getItemId()) + " and " + @PKG@.Gear.itemName(h.getItemId()) + " are not the same tier - tier one of them up first (a multitool is a pickaxe and a hatchet of one tier).", null, null, null, null, null };
  if (mid == null || (@PKG@.Gear.item(mid) == null && !TEST_ANYITEM)) return new Object[] { "There is no multitool of that tier on this server - tier your tools up first.", null, null, null, null, null };
  int[] info = new int[4];
  @BD@ nd = null;
  try { nd = mtDoc(pd, hd, mid, u, info); } catch (Throwable t) { nd = null; @PKG@.Gear.warn("multitool: the document could not be made: " + t); }
  if (nd == null) return new Object[] { "The multitool could not be made - nothing was used.", null, null, null, null, null };
  if (info[0] > 0) return new Object[] { info[0] + " line" + (info[0] == 1 ? "" : "s") + " of your tools can't be on a multitool - nothing is merged (nothing may be lost).", null, null, null, null, null };
  return new Object[] { null, pa, ha, mid, nd, info };
}""")
M(glf, r"""
public static java.nio.file.Path mtRecFile(String pk) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pk == null || pk.length() == 0) return null;
  return d.resolve("mtmerge").resolve(@PKG@.GearLL.safeKey(pk) + ".log");
}""")
M(glf, r"""
public static boolean mtRec(String pk, String line) {
  java.nio.file.Path f = mtRecFile(pk);
  if (f == null) return false;
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(f.toFile(), true);
    try {
      out.write((line + "\n").getBytes("UTF-8"));
      out.flush();
      out.getFD().sync();
    } finally { out.close(); }
    return true;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("mtrec:" + pk, "the multitool record mtmerge/" + pk + ".log could not be written (" + t + ") - that profile is not merged"); return false; }
}""")
# the verified History copy of the registry file (null = not made: no merge); the registry is written first when it has no file yet
M(glf, r"""
public static String mtBak(String pk, java.util.Properties P, String stamp) {
  try {
    java.nio.file.Path f = @PKG@.GearLL.file(pk);
    if (f == null || @PKG@.GearCfg.DIR == null) return null;
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0]) && !@PKG@.GearLL.save(pk, P)) return null;
    byte[] b = java.nio.file.Files.readAllBytes(f);
    java.nio.file.Path h = @PKG@.GearCfg.DIR.resolve("mtmerge").resolve("history");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    String nm = @PKG@.GearLL.safeKey(pk) + ".properties." + stamp + ".bak";
    java.nio.file.Path c = h.resolve(nm);
    java.nio.file.Files.write(c, b, new java.nio.file.OpenOption[0]);
    byte[] r = java.nio.file.Files.readAllBytes(c);
    if (!java.util.Arrays.equals(b, r)) { @PKG@.Gear.warn("multitool merge: the History copy of lifelong/" + pk + ".properties did not verify - nothing merged"); return null; }
    return nm;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("mtbak:" + pk, "multitool merge: the History copy of lifelong/" + pk + ".properties failed (" + t + ") - nothing merged"); return null; }
}""")
# THE COMMIT: the hatchet kind's TOOL keys leave (its points stay: hatchet.up.* / .resets / .rb* = the hatchet set), mt=1 (+ when, + the hatchet's
# uid), pickaxe.id = the multitool, the exact-copy snapshot names the multitool, the journal goes - ONE write; a failed write changes nothing in memory
M(glf, r"""
public static boolean mtFinal(@PR@ pr, String pk, java.util.Properties P, String how) {
  java.util.UUID u = pr.getUuid();
  String hatU = P.getProperty("mt.hatU");
  String mid = P.getProperty("mt.id");
  String dj = P.getProperty("mt.doc");
  java.util.Properties old = (java.util.Properties) P.clone();
  java.util.ArrayList ks = new java.util.ArrayList(P.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String k = String.valueOf(ks.get(i));
    if (k.startsWith("hatchet.") && !k.startsWith("hatchet.up.") && !k.startsWith("hatchet.rb") && !k.equals("hatchet.resets")) P.remove(k);
  }
  P.setProperty("mt", "1");
  P.setProperty("mtAt", String.valueOf(System.currentTimeMillis()));
  if (hatU != null) P.setProperty("mtHatch", hatU);
  if (mid != null) P.setProperty("pickaxe.id", mid);
  P.setProperty("pickaxe.rp", "0");          // the multitool IS the tool now (its document has no lrp) - an old pickaxe copy that turns up is removed
  P.remove("pickaxe.inv");
  @BD@ nd = null;
  try { if (dj != null) nd = @BD@.parse(new String(java.util.Base64.getDecoder().decode(dj), "UTF-8")); } catch (Throwable t) { nd = null; }
  if (nd != null && mid != null) snapSet(pk, P, "pickaxe", nd, mid);          // an exact copy (/pickaxe) is the multitool from now on
  mtDrop(P);
  if (!@PKG@.GearLL.save(pk, P)) {
    P.clear();
    P.putAll(old);
    return false;
  }
  @PKG@.GearTool.LAST.remove(u);
  @PKG@.GearGate.bump(u);
  @PKG@.GearLog.line("LL-MT-" + how.toUpperCase().replace(' ', '-') + " " + u + " " + pk + " " + P.getProperty("pickaxe.uid") + " " + mid + " (hatchet " + hatU + " is part of it; its points stay = the hatchet set)");
  mtRec(pk, "FINAL " + System.currentTimeMillis() + " " + how.replace(' ', '-') + " " + P.getProperty("pickaxe.uid") + " " + mid);
  return true;
}""")
# the summary the Tools tab shows before the (irreversible) merge: "Rare, keeps 4 lines + both sets of Upgrade Points"
M(glf, r"""
public static String mtSummary(Object[] c) {
  if (c == null || c[0] != null || c[4] == null) return "";
  @BD@ nd = (@BD@) c[4];
  int[] info = (int[]) c[5];
  return @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(nd)] + ", keeps all " + info[2] + " line" + (info[2] == 1 ? "" : "s") + " + both sets of Upgrade Points; stone and ore use the pickaxe set, logs the hatchet set";
}""")
# THE MERGE (Tools tab "Make multitool"; world thread): "+" made, "-" why not / what happened
M(glf, r"""
public static String mtMerge(@PR@ pr, @INV@ inv) {
  if (pr == null || inv == null) return "-Your inventory cannot be read right now - nothing changed.";
  java.util.UUID u = pr.getUuid();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  Object[] c = mtCheck(u, inv, pk, P);
  if (c[0] != null) { MT[1] = MT[1] + 1L; return "-" + (String) c[0]; }
  int[] pa = (int[]) c[1];
  int[] ha = (int[]) c[2];
  String mid = (String) c[3];
  @BD@ nd = (@BD@) c[4];
  @IC@ pc = @PKG@.GearStamp.section(inv, pa[0]);
  @IC@ hc = @PKG@.GearStamp.section(inv, ha[0]);
  @IS@ pick = @PKG@.GearStamp.at(inv, pa[0], pa[1]);
  @IS@ hat = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
  if (pc == null || hc == null || pick == null || hat == null) return "-Your tools moved - try again.";
  @IS@ ns = null;
  try { ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(mid, 1), pick), nd, u); } catch (Throwable t0) { ns = null; @PKG@.Gear.warn("multitool: the stack could not be made for " + pr.getUsername() + ": " + t0); }
  if (ns == null || ns.isEmpty() || !mid.equals(ns.getItemId())) return "-The multitool could not be made - nothing was used.";
  @BD@ pd = docOf(pick);
  @BD@ hd = docOf(hat);
  String pu = @PKG@.GearLL.uid(pd);
  String hu = @PKG@.GearLL.uid(hd);
  String who = pr.getUsername();
  String stamp = String.valueOf(System.currentTimeMillis());
  String bak = mtBak(pk, P, stamp);
  if (bak == null) { MT[5] = MT[5] + 1L; return "-Your tool list could not be backed up - nothing changed. Try again in a moment."; }
  if (!mtRec(pk, "MERGE " + stamp + " " + who + " " + u + " " + pu + " " + pick.getItemId() + " " + b64(pd) + " " + hu + " " + hat.getItemId() + " " + b64(hd) + " -> " + mid + " " + b64(nd) + " " + bak)) { MT[5] = MT[5] + 1L; return "-The merge could not be recorded - nothing changed. Try again in a moment."; }
  @PKG@.GearLog.line("LL-MT-BEGIN " + who + " " + u + " " + pk + " pickaxe " + pick.getItemId() + " @" + @PKG@.GearForge.where(pa[0], pa[1]) + " " + @PKG@.GearMerge.json(pick) + " + hatchet " + hat.getItemId() + " @" + @PKG@.GearForge.where(ha[0], ha[1]) + " " + @PKG@.GearMerge.json(hat) + " -> " + mid + " " + nd.toJson());
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }
  String dj = null;
  try { dj = java.util.Base64.getEncoder().encodeToString(nd.toJson().getBytes("UTF-8")); } catch (Throwable tj) { dj = null; }
  if (dj == null) return "-The multitool could not be made - nothing was used.";
  P.setProperty("mt.pend", pu);
  P.setProperty("mt.hatU", hu);
  P.setProperty("mt.id", mid);
  P.setProperty("mt.doc", dj);
  P.setProperty("mt.at", stamp);
  if (!@PKG@.GearLL.save(pk, P)) { mtDrop(P); return "-Your choice could not be saved - nothing changed."; }
  crash(61);
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int bp = @PKG@.GearStamp.countId(all, pick.getItemId());
  int bh = @PKG@.GearStamp.countId(all, hat.getItemId());
  int bm = @PKG@.GearStamp.countId(all, mid);
  // (a) the hatchet leaves first: a crash after it = mtRecover finishes the multitool from the journal, never copies anything
  Object t1 = null;
  Throwable e1 = null;
  try { t1 = hc.removeItemStackFromSlot((short) ha[1]); } catch (Throwable x1) { e1 = x1; }
  boolean gone = e1 == null && !(t1 instanceof @TXN@ && !((@TXN@) t1).succeeded()) && @PKG@.GearMerge.empty(hc, ha[1]);
  if (!gone) {
    if (@PKG@.GearMerge.empty(hc, ha[1])) { try { hc.setItemStackForSlot((short) ha[1], hat); } catch (Throwable xb) { } }
    mtDrop(P);
    @PKG@.GearLL.save(pk, P);
    MT[2] = MT[2] + 1L;
    @PKG@.GearLog.line("LL-MT-FAILED " + who + " " + u + " (the hatchet was not taken: " + (e1 != null ? String.valueOf(e1) : "the inventory refused it") + ") - nothing used");
    mtRec(pk, "FAILED " + stamp + " hatchet not taken - nothing used");
    return "-The inventory refused the change - nothing was used.";
  }
  @PKG@.GearStamp.selfNote(u, t1);
  crash(62);
  // (b) the pickaxe's slot gets the multitool (the same lifelong uid)
  Object t2 = null;
  Throwable e2 = null;
  try { t2 = pc.setItemStackForSlot((short) pa[1], ns); } catch (Throwable x2) { e2 = x2; }
  @IS@ now = pc.getItemStack((short) pa[1]);
  @BD@ bd = docOf(now);
  boolean put = e2 == null && !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) && now != null && mid.equals(now.getItemId()) && bd != null && pu.equals(@PKG@.GearLL.uid(bd));
  if (!put) {
    try { hc.setItemStackForSlot((short) ha[1], hat); } catch (Throwable xr) { }
    boolean back = @PKG@.GearForge.same(hc.getItemStack((short) ha[1]), hat.getItemId(), @PKG@.GearForge.fp(hat));
    if (back) {
      mtDrop(P);
      @PKG@.GearLL.save(pk, P);
      MT[2] = MT[2] + 1L;
      @PKG@.GearLog.line("LL-MT-FAILED " + who + " " + u + " (the multitool was not written: " + (e2 != null ? String.valueOf(e2) : "the inventory refused it") + ") - RESTORED, nothing used");
      mtRec(pk, "FAILED " + stamp + " multitool not written - restored, nothing used");
      return "-The inventory refused the multitool - nothing was used.";
    }
    @PKG@.Gear.warn("MULTITOOL: the hatchet of " + who + " (" + u + ") could not be put back - the merge is finished at the next look (the journal stays); both documents are in gear.log and mtmerge/" + pk + ".log");
    @PKG@.GearLog.line("LL-MT-RESTORE-FAILED " + who + " " + u + " " + @PKG@.GearMerge.json(hat) + " (the journal stays - mtRecover finishes the multitool)");
    return "-Something went wrong - your multitool is finished at your next look (an admin can find both tools in the server log).";
  }
  @PKG@.GearStamp.selfNote(u, t2);
  crash(63);
  // (c) the registry: the multitool is the pickaxe kind's tool, the hatchet kind keeps its points
  if (!mtFinal(pr, pk, P, "made")) @PKG@.Gear.warn("lifelong: the multitool of " + pk + " could not be written to the registry - the next look finishes it");
  try {
    int ap = @PKG@.GearStamp.countId(all, pick.getItemId());
    int ah = @PKG@.GearStamp.countId(all, hat.getItemId());
    int am = @PKG@.GearStamp.countId(all, mid);
    if (ap != bp - 1 || ah != bh - 1 || am != bm + 1) @PKG@.Gear.warn("MULTITOOL COUNT MISMATCH for " + who + ": " + pick.getItemId() + " " + bp + "->" + ap + ", " + hat.getItemId() + " " + bh + "->" + ah + ", " + mid + " " + bm + "->" + am);
    @PKG@.GearMerge.rqGone(hat, u, who);
    @PKG@.GSnd.upgrade(u);
  } catch (Throwable xa) { }
  MT[0] = MT[0] + 1L;
  return "+Your pickaxe and hatchet are one " + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(nd)] + " " + @PKG@.Gear.itemName(mid) + " now (Lv " + @PKG@.GearLevel.level(mid, nd) + ")! Stone and ore use your pickaxe set, logs your hatchet set - both sets of Upgrade Points stay. Lost it? /pickaxe";
}""")
# a merge the server did not finish (a crash after the journal): the multitool in the pickaxe's place -> commit; both tools still there -> nothing
# happened (the journal goes); the hatchet gone but the pickaxe still a pickaxe -> the multitool is written from the journal, then commit; the
# pickaxe not on the player -> wait (10 minutes, then the journal goes: the hatchet kind still names its uid + snapshot, /hatchet copies it)
M(glf, r"""
public static boolean mtRecover(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  String pend = P.getProperty("mt.pend");
  if (pend == null || pr == null || inv == null) return false;
  java.util.UUID u = pr.getUuid();
  String mid = P.getProperty("mt.id");
  int[] pa = find(inv, pk, pend);
  if (pa != null) {
    @IS@ x = @PKG@.GearStamp.at(inv, pa[0], pa[1]);
    if (x != null && @PKG@.GearData.multiId(x.getItemId())) {
      boolean ok = mtFinal(pr, pk, P, "recovered");
      if (ok) MT[3] = MT[3] + 1L;
      return ok;
    }
    String hu = P.getProperty("mt.hatU");
    if (hu != null && find(inv, pk, hu) != null) {
      mtDrop(P);
      @PKG@.GearLL.save(pk, P);
      MT[4] = MT[4] + 1L;
      @PKG@.GearLog.line("LL-MT-RECOVER " + u + " " + pk + " both tools are still there - nothing happened, the journal goes");
      mtRec(pk, "RECOVER " + System.currentTimeMillis() + " both tools still there - nothing happened");
      return true;
    }
    @BD@ nd = null;
    try {
      String dj = P.getProperty("mt.doc");
      if (dj != null) nd = @BD@.parse(new String(java.util.Base64.getDecoder().decode(dj), "UTF-8"));
    } catch (Throwable t) { nd = null; }
    if (nd == null || mid == null || (@PKG@.Gear.item(mid) == null && !TEST_ANYITEM) || !pend.equals(@PKG@.GearLL.uid(nd)) || x == null) {
      mtDrop(P);
      @PKG@.GearLL.save(pk, P);
      MT[4] = MT[4] + 1L;
      @PKG@.GearLog.line("LL-MT-RECOVER " + u + " " + pk + " the hatchet left but the multitool cannot be made from the journal - the journal goes (/hatchet makes an exact copy)");
      mtRec(pk, "RECOVER " + System.currentTimeMillis() + " journal dropped - the multitool could not be made; /hatchet copies the hatchet");
      return true;
    }
    @IC@ sc = @PKG@.GearStamp.section(inv, pa[0]);
    @IS@ ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(mid, 1), x), nd, u);
    Object t2 = null;
    try { t2 = sc.setItemStackForSlot((short) pa[1], ns); } catch (Throwable x2) { t2 = null; }
    @IS@ now = sc.getItemStack((short) pa[1]);
    if (now == null || !mid.equals(now.getItemId())) { @PKG@.Gear.warnOnce("mtrec:" + pk, "the multitool of " + pk + " could not be finished yet (the inventory refused it) - tried again at the next look"); return false; }
    @PKG@.GearStamp.selfNote(u, t2);
    boolean ok2 = mtFinal(pr, pk, P, "finished from the journal");
    if (ok2) { MT[3] = MT[3] + 1L; tellOnce(pr, "mtrec", "Your multitool is finished.", 5000L); }
    return ok2;
  }
  long at = @PKG@.GearLL.getl(P, "mt.at", 0L);
  long now2 = System.currentTimeMillis();
  if (at > 0L && now2 - at > 600000L) {
    mtDrop(P);
    @PKG@.GearLL.save(pk, P);
    MT[4] = MT[4] + 1L;
    @PKG@.GearLog.line("LL-MT-RECOVER " + u + " " + pk + " the pickaxe is not on the player 10 minutes after the merge began - the journal goes");
    mtRec(pk, "RECOVER " + now2 + " journal dropped - the pickaxe was away for 10 minutes");
    return true;
  }
  return false;
}""")
'''
before('''# THE SWEEP (world thread; join = force, every stamp scan = at most every 400 ms): journals, the migration (once), the look
''', MERGE)
before('''# one look over the inventory: level sync, the registry's item id, returned originals, stale copies, others' stale replacements
''', r'''# 0.3.25 critic M1: the merged twin of a stack (mode 0 = a multitool, 1 = a Harvester) with uid lu of profile pk in this inventory
F(glf, "public static volatile boolean TEST_ANYITEM = false;")          # harness only: the multitool counts as loaded (the stand-in engine decodes no tool items)
M(glf, r"""
public static boolean twin(@INV@ inv, String pk, String lu, int mode) {
  if (inv == null || lu == null) return false;
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty()) continue;
      String id = x.getItemId();
      if (mode == 0 ? !@PKG@.GearData.multiId(id) : !@PKG@.GearLL.harv(id)) continue;
      @BD@ d = docOf(x);
      if (@PKG@.GearLL.isLL(d) && lu.equals(@PKG@.GearLL.uid(d)) && pk.equals(@PKG@.GearLL.owner(d))) return true;
    }
  }
  return false;
}""")
# the plain pickaxe with the multitool's uid and no multitool here (a hard stop after the commit, before the inventory save): it becomes the
# multitool IN PLACE from the snapshot mtFinal wrote (the merged document); false = left as it is (no snapshot / item yet - asked again next look)
M(glf, r"""
public static boolean mtHeal(@IC@ c, int i, @IS@ x, java.util.UUID u, String pk, java.util.Properties P) {
  try {
    @BD@ xd = docOf(x);
    String lu = @PKG@.GearLL.uid(xd);
    @BD@ sd = snapDoc(P, "pickaxe", lu);
    String sid = P.getProperty("pickaxe.snapId");
    if (sd == null || sid == null || !@PKG@.GearData.multiId(sid) || (@PKG@.Gear.item(sid) == null && !TEST_ANYITEM) || !lu.equals(@PKG@.GearLL.uid(sd))) {
      @PKG@.Gear.warnOnce("mtheal:" + pk, "multitool: the plain pickaxe " + lu + " of " + pk + " is the merged multitool's uid but no snapshot can rebuild it yet - it is kept as it is");
      return false;
    }
    @IS@ ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(sid, 1), x), sd, u);
    @PKG@.GearLog.line("LL-MT-HEAL-BEGIN " + u + " " + pk + " " + lu + " " + x.getItemId() + " -> " + sid + " undo: " + @PKG@.GearMerge.json(x));
    Object t = c.setItemStackForSlot((short) i, ns);
    @IS@ now = c.getItemStack((short) i);
    if ((t instanceof @TXN@ && !((@TXN@) t).succeeded()) || now == null || !sid.equals(now.getItemId())) return false;
    @PKG@.GearStamp.selfNote(u, t);
    @PKG@.GearLog.line("LL-MT-HEAL " + u + " " + pk + " " + lu + " is the multitool again (" + sid + ")");
    return true;
  } catch (Throwable t2) { @PKG@.Gear.warnOnce("mtheal2:" + pk, "multitool: the in-place rebuild failed (the pickaxe is kept): " + t2); return false; }
}""")
''')

# ================================================================================================================ 1f: LifePage - the rows, the button
rep('''  String cur = P.getProperty(K + ".uid");
  int[] at = null;
  if (cur != null) at = @PKG@.GearLife.find(inv, pk, cur);
  @IS@ x = at == null ? null : @PKG@.GearStamp.at(inv, at[0], at[1]);
  @BD@ d = x == null ? null : @PKG@.GearLife.docOf(x);
  String id = idOf(x, P, k);''', '''  int hk = @PKG@.GearLL.hostK(P, k);          // 0.3.25: the hatchet set's row shows the multitool
  String cur = P.getProperty(@PKG@.GearLL.KIND[hk] + ".uid");
  int[] at = null;
  if (cur != null) at = @PKG@.GearLife.find(inv, pk, cur);
  @IS@ x = at == null ? null : @PKG@.GearStamp.at(inv, at[0], at[1]);
  @BD@ d = x == null ? null : @PKG@.GearLife.docOf(x);
  String id = idOf(x, P, hk);''')
rep('''  int h = @PKG@.GearLL.skill(u, k);
  int lv = @PKG@.GearLL.levelFor(u, id);
  String sk = @PKG@.GearLL.KSKILL[k] + (h >= 0 ? " " + h : "");''', '''  int h = @PKG@.GearLL.skill(u, k);
  int lv = @PKG@.GearLL.levelK(u, k, id);          // 0.3.25: kind k's skill (the hatchet set = Foraging)
  String sk = (k <= 1 && @PKG@.GearData.multiId(id) ? (k == 0 ? "Pickaxe set - " : "Hatchet set - ") : "") + @PKG@.GearLL.KSKILL[k] + (h >= 0 ? " " + h : "");''')
rep('''  else if (x == null) w = "Not on you - /" + K + " brings it back";''', '''  else if (x == null) w = "Not on you - /" + @PKG@.GearLL.KIND[hk] + " brings it back";          // 0.3.25: /pickaxe for the multitool''')
rep('''  String cur = P.getProperty(K + ".uid");
  int[] at = null;
  if (cur != null) at = @PKG@.GearLife.find(inv, pk, cur);
  @IS@ x = at == null ? null : @PKG@.GearStamp.at(inv, at[0], at[1]);
  String id = idOf(x, P, k);''', '''  int hk = @PKG@.GearLL.hostK(P, k);          // 0.3.25: the hatchet set's panel shows the multitool (its points are the hatchet kind's)
  String cur = P.getProperty(@PKG@.GearLL.KIND[hk] + ".uid");
  int[] at = null;
  if (cur != null) at = @PKG@.GearLife.find(inv, pk, cur);
  @IS@ x = at == null ? null : @PKG@.GearStamp.at(inv, at[0], at[1]);
  String id = idOf(x, P, hk);''')
rep('''  b.set("#SkyyGPTitle.Text", "Your " + @PKG@.GearLL.kname(k, id).toLowerCase() + " - Upgrade Points");          // 0.3.12: "watering can", "harvester"''',
    '''  b.set("#SkyyGPTitle.Text", "Your " + @PKG@.GearLL.kname(k, id).toLowerCase() + (k <= 1 && @PKG@.GearData.multiId(id) ? (k == 0 ? " (pickaxe set)" : " (hatchet set)") : "") + " - Upgrade Points");          // 0.3.12: "watering can", "harvester"; 0.3.25: the multitool's sets''')
rep('''  tierRow(b, ev, u, inv, pk, P, k, id);
  if (k <= 1 && @PKG@.GearCfg.MULTI_ON && @PKG@.GearMerge.loaded()) mtRow(b, ev, u, inv);''', '''  tierRow(b, ev, u, inv, pk, P, hk, id);          // 0.3.25: one tier-up raises both sets (the multitool's own ladder)
  if (k <= 1 && @PKG@.GearCfg.MULTI_ON && !@PKG@.GearLL.mtm(P)) llMtRow(b, ev, u, inv, pk, P);          // 0.3.25: the LIFELONG merge (was the crafted pair)''')
rep('''  int[] at = toolAt(inv, pk, P, k);
  if (at == null) { this.info = "-Your " + K + " is not on you - /" + K + " brings it back."; return; }''', '''  k = @PKG@.GearLL.hostK(P, k);          // 0.3.25: the hatchet set's Upgrade tiers the multitool up
  K = @PKG@.GearLL.KIND[k];
  int[] at = toolAt(inv, pk, P, k);
  if (at == null) { this.info = "-Your " + K + " is not on you - /" + K + " brings it back."; return; }''')
rep('''      else if (cmd.equals("mt")) makeMt(inv0);''', '''      else if (cmd.equals("mt")) makeLlMt(inv0);          // 0.3.25: the lifelong merge''')
before('''# 0.3.12 MAKE HARVESTER on the hoe / sickle panels (the multitool row's shape): before the gate opens greyed with the rebirth line; then your
''', r'''# 0.3.25 MAKE MULTITOOL = YOUR LIFELONG PICKAXE + HATCHET (GearLife.mtCheck / mtMerge; the Harvester row's shape): the row says what the multitool
# keeps, the pair drawn (slot / id / fingerprint of both) must still be the same at the click, and the FIRST click only arms it (8 s) - can't be undone
F(lpg, "public String mlKey;")
F(lpg, "public String mlArmKey;")
F(lpg, "public long mlArm;")
M(lpg, r"""
public void llMtRow(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P) {
  String tx;
  String bl = "Make multitool";
  boolean can = false;
  this.mlKey = null;
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { tx = "Multitool: " + gate; bl = "Rebirth 1"; }
  else {
    Object[] c = @PKG@.GearLife.mtCheck(u, inv, pk, P);
    if (c[0] != null) tx = "Multitool (your pickaxe + hatchet in one tool): " + (String) c[0];
    else {
      int[] pa = (int[]) c[1];
      int[] ha = (int[]) c[2];
      @IS@ p = @PKG@.GearStamp.at(inv, pa[0], pa[1]);
      @IS@ h = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
      String key = pairKey(inv, new int[] { pa[0], pa[1], ha[0], ha[1] });
      boolean armed = key != null && key.equals(this.mlArmKey) && System.currentTimeMillis() - this.mlArm < 8000L && System.currentTimeMillis() >= this.mlArm;
      tx = (armed ? "Click again within 8 s - can't be undone: " : "Multitool: ") + @PKG@.Gear.itemName(p.getItemId()) + " + " + @PKG@.Gear.itemName(h.getItemId()) + " = " + @PKG@.Gear.itemName((String) c[3]) + " (" + @PKG@.GearLife.mtSummary(c) + "). Both are used up.";
      if (armed) bl = "Click again";
      this.mlKey = key;
      can = key != null;
    }
  }
  b.appendInline("#SkyyGPanel", "Group #SkyyGPMlRow { Anchor: (Height: 84); LayoutMode: Left; Label #SkyyGPMl { Anchor: (Width: 392); Text: \"\"; Style: (FontSize: 13, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); } Group { Anchor: (Width: 10); } TextButton #SkyyGPMlB { Anchor: (Width: 160, Height: 44); Text: \"" + bl + "\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set("#SkyyGPMl.Text", tx);
  ev.addEventBinding(@BT@.Activating, "#SkyyGPMlB", @EVD@.of("a", "mt:" + this.tok));
}""")
M(lpg, r"""
public void makeLlMt(@INV@ inv) {
  java.util.UUID u = this.playerRef.getUuid();
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { this.info = "-" + gate; this.mlArmKey = null; return; }
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  Object[] c = @PKG@.GearLife.mtCheck(u, inv, pk, P);
  if (c[0] != null) { this.info = "-" + (String) c[0]; this.mlArmKey = null; return; }
  int[] pa = (int[]) c[1];
  int[] ha = (int[]) c[2];
  String key = pairKey(inv, new int[] { pa[0], pa[1], ha[0], ha[1] });
  if (key == null || this.mlKey == null || !key.equals(this.mlKey)) { this.info = "-Your tools changed - check the multitool line and click again."; this.mlArmKey = null; return; }
  long now = System.currentTimeMillis();
  if (!key.equals(this.mlArmKey) || now - this.mlArm >= 8000L || now < this.mlArm) {          // the first click arms
    this.mlArmKey = key;
    this.mlArm = now;
    this.info = "=Check what the multitool keeps, then click again within 8 s - the merge can't be undone.";
    return;
  }
  this.mlArmKey = null;
  this.info = @PKG@.GearLife.mtMerge(this.playerRef, inv);
  if (this.info.startsWith("+")) this.sel = 0;
}""")
''')

# critic L2: the normal-tools sweep also waits while a multitool merge journal is open
rep('''  if (P.getProperty("harv.pend") != null) return false;
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) if (P.getProperty(@PKG@.GearLL.KIND[k] + ".pend") != null) return false;''',
    '''  if (P.getProperty("harv.pend") != null) return false;
  if (P.getProperty("mt.pend") != null) return false;          // 0.3.25 critic L2
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) if (P.getProperty(@PKG@.GearLL.KIND[k] + ".pend") != null) return false;''')

# ================================================================================================================ manifest
rep('''MOVEMENT: armor Speed keeps working when another mod resets the jump''',
    '''LIFELONG MULTITOOL: merge your lifelong pickaxe + hatchet of one tier on the Tools tab - one tool, both sets of Upgrade Points, one tier-up raises both. MOVEMENT: armor Speed keeps working when another mod resets the jump''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i("public static boolean mtm(java.util.Properties P)") < _i("public static String crudeOf(int k, String id) {") < _i("public static int levelK(") \
    < _i("public static String tierFor(java.util.UUID u, int k, String had) {") < _i("public static int lineCap(java.util.Properties P, int k) {")
assert _i("public static String collWhy0(") < _i("public static String collWhy(java.util.UUID u, String to) {") < _i("public static String tierWhy(java.util.UUID u, String to) {\n  int k = kOf(to);")
assert _i("public static double accBp0(") < _i("public static double accBp(java.util.UUID u, String sk) {") < _i("public static float mdamage(")
assert _i("public static void collRow0(") < _i("public static void collRow(java.util.UUID u, String from, String to, java.util.ArrayList rows) {")
assert _i("public static boolean harvRecover(") < _i("public static boolean mtRecover(") < _i("public static void sweep0(")
assert _i("public static String mtMerge(") < _i("public void llMtRow(") < _i("public void panel(@UCB@ b") and _i("public void makeLlMt(") < _i("public void handleDataEvent(@REF@ ref, @ST@ st, String data) {\n  try {\n    if (data == null) return;\n    String a = @PKG@.Gear.jsonStr(data, \"a\");\n    if (a.length() == 0) return;\n    if (a.startsWith(\"mode:\")) {\n      String c = a.equals(\"mode:3\") ? (@PKG@.GearCfg.SMITH_ON ? \"smithing\" : null) : (a.equals(\"mode:0\") ? \"reforge\"")
assert _i("MT_LAD_DEF = _g25_mid") < _i("G325_HEAD = ") < _i("CFG_ROWS = [")
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
assert s.count(' = mk("') == MK0, "no new class"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.24 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.24 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
