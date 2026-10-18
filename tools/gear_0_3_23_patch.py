"""Derive SkyyGear/build_skyygear_0.3.23.py from the LIVE 0.3.22 (build_skyygear_0.3.22.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_22_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_23_patch.py      then      python SkyyGear/build_skyygear_0.3.23.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.23.py   (--static runs without jars / Assets.zip)
The build reads Quirk's PRIVATE art at build time (nothing from it is copied into this repo): the mining armor textures (0.3.21) and now the
metal tool builds (SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE/<Titanium|Lumen>/<Tool>.blockymodel + _Texture.png). Missing = the build stops.

0.3.23 (2026-10-18) = THE METAL TOOLS (round G2, research/Metals-Tools-Fortune-Spec.md section 5 row G2 + 3.3).
Skyy's words (docs/answered/gear.md 2026-10-17): "Yes, full 15-step ladder (Recommended)"; "Yes, all defaults (Recommended)" (spec Q2-Q11: hatchet /
harvester / can tier-ups cost the metal's bars + today's log / crop item; shovel stays vanilla; Lead / Chromium / Slag / Titanium tools copy today's
next-tier specs); the metal art "all of the art looks beautiful! all those items are good to go" (research/Metal-Art-Manifest.md).
  1. 49 NEW FOREVER TOOLS (SkyyGear items, no recipe - lifelong tools are tiered up on the Anvil, never crafted; gear.md 2026-10-12):
       pickaxe / hatchet / multitool of Bronze + Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen   (3 x 9 = 27)
       Harvester Cobalt, Adamantite, Mithril + the 9                                                            (12)
       watering can Mithril + the 9                                                                             (10)
     IDS: a non-vanilla tool metal ends "_SkyWynn" - Tool_Pickaxe_Lead_SkyWynn, Tool_Hatchet_..., Tool_Hatchet_Pickaxe_Multitool_<M>_SkyWynn,
     Tool_Sickle_Harvester_<M>_SkyWynn, Tool_WaterCan_<M>_SkyWynn; the vanilla metals keep the 0.3.12 pattern (Tool_Sickle_Harvester_Cobalt,
     Tool_WaterCan_Mithril). The art manifest's PROPOSED ids (Tool_Pickaxe_Lead, Tool_Multitool_Lead_Wynn ...) are NOT used: Tool_Pickaxe_Lead
     is TerrariaToolsWeapons' (Skyy's Mods folder, checked), and G1's level rows match only <Metal>_SkyWynn ids (critic L1). None is a vanilla id.
     SPECS ("copy today's next-tier specs"): each new metal's Parent = the next vanilla tool ABOVE it on the ladder (Bronze -> Thorium; Lead / Dusk ->
     Cobalt; Chromium / Azurvane -> Adamantite; Slag / Cinder -> Mithril; Titanium / Lumen -> Onyxium) and its INTERNAL tool tier = that tool's
     (Bronze 2 -> 3 - no Bronze tool existed; the 8 zone words 4 / 4 / 5 / 5 / 6 / 6 / 7 / 7; GearLL.TW / GearTool.TIER_W = TOOL_TIERS + G23_ZT).
     Internal tiers never go down along the ladder, so no line cap / log / crop gate falls on a tier-up; the ladder T (ore gate, tags, power)
     is the metal's own step. The multitool = the parent pickaxe's specs with the parent hatchet's Woods spec, our BlockCondition interaction
     SkyyGear_Multitool_Attack (Tag Wood -> Hatchet_Attack, else Pickaxe_Attack - InkBlindCat's Multitools design, MIT, credited in PACK.md) and an
     animation set = vanilla Pickaxe + Hatchet (Mine + Chop); GearDefs.MULTI_OWN makes GearData.multiId know them (two stat sets, fam 6).
     The Harvesters = the 0.3.14 shape (Parent Tool_Sickle_Iron, Hoe_Till secondary, our sweep HitBlock); the cans = the 0.3.12 can shape.
  2. THE ART (generated at BUILD time, never committed - tools/art/make_metal_items.py is imported and its tools() run in memory):
       pickaxe / hatchet / can of the 8 approved metals = the approved files byte for byte (models-local/art/metals/tools, compared when present;
       Titanium / Lumen = Quirk's untouched PRIVATE textures) on the vanilla Mithril pickaxe / hatchet / can models BY PATH (Quirk's models are
       those JSONs, so the textures fit their UV). NO private model ships (main session 2026-10-18: manifest question 3 is still open for Skyy):
       the MULTITOOL = the vanilla Mithril pickaxe model with its metal's pickaxe texture + icon; the HARVESTER = the vanilla Thorium hoe model
       with a build-time recolour of the hoe texture / icon in the metal card's colours (the 0.3.12 Harvester recipe). Quirk's approved
       multitool / harvester art swaps in later (same ids) if Skyy allows shipping the models.
       PLACEHOLDERS (no approved card): Bronze pickaxe / hatchet / can (Quirk's Lumen build) + the Mithril can (Titanium build), the same
       generator recolour with a card from the vanilla ingot textures; the Bronze / Cobalt / Adamantite / Mithril Harvesters use that card too.
  3. THE 15-STEP LADDERS (lifelong.ladders, can.ladders, harvester.ladders; spec 3.3 + Q7): Crude > Copper > Iron > Bronze > Thorium > Lead > Dusk >
     Cobalt > Chromium > Azurvane > Adamantite > Slag > Cinder > Mithril > Titanium > Lumen for the pickaxe, hatchet, Harvester and can. A step costs
     the metal's bars: 25 Copper bars; Enchanted ingots 1 Iron / 1 Thorium / 1 Lead / 2 Cobalt / 2 Chromium / 2 Adamantite / 2 Slag / 3 Mithril /
     3 Titanium (the 0.3.0 counts kept, the zones continue them); alloys (no Enchanted form) 32 Bronze / 64 Dusk / 128 Azurvane / 192 Cinder /
     256 Lumen bars (the Furnace Charm tier-up counts, Skyy 2026-10-17). Hatchet / Harvester / can steps ADD the skill item of the step they
     mirror (today's: Maple 1 / Gumboab 1 / Redwood 2 / Sallow 2 logs, Carrot 1 / Cauliflower 1 / Pumpkin 2 / Tomato 2 crops; Mithril-mirror steps
     Sallow 3 / Cotton 3, Onyxium-mirror steps Sallow 4 / Potato 3). The existing pickaxe steps keep their exact cost. lifelong.ladders max
     length 2000 -> 4000 (the text is longer now). Tier-up gates unchanged: skill level = the new tier's level band start (Lead_SkyWynn 22 ...;
     Bronze 15-23 = Iron's LOCKED band) + SkyyCollections coll:fn:tierup "<kind>:<word>" with the METAL word for the new metals
     (GearLL.tnm: "pickaxe:Lead" - no Collections row yet = open, the L1-type round adds them); every UI text names the metal word, not the
     internal tier's (a Lead pickaxe said "Cobalt").
  4. THE ORE GATE TIGHTENED (spec 3.2 now that every step has a pickaxe): GearLL.PICK_T = T1..T16 (G22_OWN_PICKS = our 9 pickaxes), so "the next
     pickaxe step" is the next LADDER step - an ore two or more steps above you is x gate.twoUpFactor (10x the hits); gate.oreFloor default ""
     (the 0.3.22 note: empty once the alloy pickaxes exist). NEW ROW gate.nextByLadder (default on; off = only the vanilla pickaxes count as steps,
     = 0.3.22's next-step rule): with it off and gate.oreFloor back to Lead,Chromium,Slag,Titanium every pickaxe hits exactly like 0.3.22
     (build-proved). The build prints the hit table (17 pickaxes x 12 ore blocks, 0.3.22 > 0.3.23) and STOPS if any existing pickaxe got
     slower on an ore at or above its half-speed reach; the deliberately slower cells (an ore 2+ ladder steps above a vanilla pickaxe) are listed.
     rpow (the right-tier hit) is unchanged in number (each new step's pickaxe has its next vanilla pickaxe's specs - build-checked).
  5. ONE-TIME UPDATE migrate0323 (PROJECT-RULES 4, the migrate0317 machinery with TEXT values): lifelong.ladders, can.ladders, harvester.ladders
     and gate.oreFloor are rewritten ONLY when the file's one-line entry still holds exactly the 0.3.22 default (trimmed text compare); a hand-
     edited value is kept + noted; verified History copy first; one config-changes.log row each (Undo); the marker at the END (a fresh file
     carries it under the 0.3.23 head); every other byte + line ending kept. Skyy's NewBetaTest file holds the old lifelong.ladders default
     (read-only check 2026-10-18) -> it gets the 15-step ladders on the next start.
  6. LIFELONG REPLACEMENTS (/pickaxe ... critic A2 rule): two ladder steps can share an internal tier now (Lead / Dusk / Cobalt), so GearLL.lrank
     (ladder T x 10 + internal tier) decides "never below the tier you had" (tierFor) and a new doc key lrpL (the rank it was given at; older
     SkyyGear ignores it) makes a replacement tiered up from Lead to Dusk count as invested (never removed when the original turns up).
  7. NOTHING A PLAYER OWNS GETS WORSE (critic round, main session 2026-10-18):
     M1 the 8 zone words count as tool tier words ONLY in our _SkyWynn ids (GearLL.tier / GearTool.tier / tnm: TW0 = the first zone word) -
        TerrariaToolsWeapons' Tool_Pickaxe_Lead / Tool_Axe_Lead keep tier 0 as in 0.3.22;
     M2 the uncapped line: GearLL.isTop = the LAST id of the tool's ladder, or a tool at / above its kind's 0.3.22 top (OLDTOP: pickaxe / hatchet /
        can Adamantite, hoe Thorium, sickle Iron, pole Iron, Harvester Thorium) - an Adamantite pickaxe with 80 Breaking Power levels keeps all 80
        (harness H323 H); topTier = the tier of the ladder's last id;
     M3 HARV_TOP stays 3 (Thorium): a Thorium (or higher) Harvester still reaps every crop in full like 0.3.22 - the new metals add above it;
     L4 the CHG_FAMILIES comment no longer swallows the Wand / Spellbook entries of that build check.
  8. EXTRA SCOPE (main session 2026-10-18, round A1 = SkyyArmory 0.1.33's 76 new-metal weapons): the loot pool (ARMORY_POOL 43 -> 103) gets the
     new Bo / Gauntlets / Kunai / Spellbook / GreatShield / Crossbow / Mage staff ids of the 8 zone metals + the Thorium / Cobalt / Adamantite /
     Mithril crossbows (wands stay out); OWN_TRUST 2 -> 14 crossbows (read from SkyyArmory-0.1.33.jar); upgrade.ladders = the 15-metal Soul Cage
     ladder (Orb > Copper > Iron > Thorium > Lead > Dusk > Cobalt > ... > Lumen > Onyxium, migrate0323) and GearUp.fromRecipeAlt pays a step whose
     recipe takes an EARLIER cage (the Thorium / Cobalt / Adamantite / Mithril cages each have two "next" recipes now: Dusk > Cobalt pays the
     Cobalt recipe with the Dusk cage in the Thorium cage's place). GearBase.kunaiTwin needs no change: it already keys the twin by the full
     <M>_SkyWynn word (Weapon_Daggers_Lead_SkyWynn ... A2), the id itself until the twin exists. tools/tier_tags.py: + the 76 rows (owner
     SkyyArmory, family armory_metal).
Commands: none new. Config: + gate.nextByLadder; defaults lifelong.ladders / can.ladders / harvester.ladders / gate.oreFloor / upgrade.ladders (migrate0323).
Classes: none new. SAVED DATA: + lrpL on newly given lifelong replacements (ignored by 0.3.22); no tier / cap / document of a held tool changes.
ROLLBACK 0.3.23 -> 0.3.22: the 49 items vanish from the jar (a held new-metal tool becomes an unknown item - roll back only before players tier
up past Thorium, or Undo the three ladder rows in Server Setup first); the migrated rows keep the 15-step text, which 0.3.22 parses (unknown ids
= steps it cannot pay - one WARN); gate.oreFloor "" makes 0.3.22 slow the zone ores for low pickaxes - Undo it in the change log.
"""
import os
import sys
import ast
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.22.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.23.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.22"' in s and "GENERATED by tools/gear_0_3_22_patch.py" in s, "not the generated 0.3.22 script"
assert "G23_PICK" not in s and "migrate0323" not in s and "MULTI_OWN" not in s
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


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


def method(anchor_start):
    i = s.index(anchor_start)
    j = s.index('}""")', i)
    return s[i:j + len('}""")')]


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.22":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.22" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.23 (2026-10-18)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.22 - build script (javassist via jpype). GENERATED by tools/gear_0_3_22_patch.py from the LIVE 0.3.21 (itself GENERATED by
tools/gear_0_3_21_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.22.py -> SkyyGear/SkyyGear-0.3.22.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.22.py. Needs Quirk's private textures (../SkyWynn-PRIVATE-art/mining-armor).

''', '''"""SkyyGear 0.3.23 - build script (javassist via jpype). GENERATED by tools/gear_0_3_23_patch.py from the LIVE 0.3.22 (itself GENERATED by
tools/gear_0_3_22_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.23.py -> SkyyGear/SkyyGear-0.3.23.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.23.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''' + NOTE + '''
--- 0.3.22 notes ---
''')
rep('VERSION = "0.3.22"\n', 'VERSION = "0.3.23"\n')

# ================================================================================================================ 1: internal tiers of the new words
rep('''TOOL_TIERS = [("Crude", 0), ("Wood", 0), ("Copper", 1), ("Scrap", 1), ("Bronze", 2), ("Iron", 2), ("Steel", 2), ("Thorium", 3), ("Cobalt", 4),
              ("Adamantite", 5), ("Mithril", 6), ("Onyxium", 7)]
''', '''TOOL_TIERS = [("Crude", 0), ("Wood", 0), ("Copper", 1), ("Scrap", 1), ("Bronze", 3), ("Iron", 2), ("Steel", 2), ("Thorium", 3), ("Cobalt", 4),
              ("Adamantite", 5), ("Mithril", 6), ("Onyxium", 7)]          # 0.3.23: Bronze 2 -> 3 (its tools copy the Thorium specs; none existed)
# 0.3.23 (round G2): the zone metals' INTERNAL tool tier = the next vanilla tool above them on the 15-step ladder ("copy today's next-tier specs")
G23_ZT = [("Lead", 4), ("Dusk", 4), ("Chromium", 5), ("Azurvane", 5), ("Slag", 6), ("Cinder", 6), ("Titanium", 7), ("Lumen", 7)]
TOOL_TIERS_ALL = TOOL_TIERS + G23_ZT
''')
rep('''F(gll, "public static final String[] TW = %s;" % jarr([_w for _w, _t in TOOL_TIERS]))
F(gll, "public static final int[] TN = %s;" % jints([_t for _w, _t in TOOL_TIERS]))''',
    '''F(gll, "public static final String[] TW = %s;" % jarr([_w for _w, _t in TOOL_TIERS_ALL]))          # 0.3.23: + the zone words (G23_ZT)
F(gll, "public static final int[] TN = %s;" % jints([_t for _w, _t in TOOL_TIERS_ALL]))''')
rep('''F(gtool, "public static final String[] TIER_W = %s;" % jarr([w for w, _t in TOOL_TIERS]))
F(gtool, "public static final int[] TIER_N = %s;" % jints([t for _w, t in TOOL_TIERS]))''',
    '''F(gtool, "public static final String[] TIER_W = %s;" % jarr([w for w, _t in TOOL_TIERS_ALL]))          # 0.3.23: + the zone words (G23_ZT)
F(gtool, "public static final int[] TIER_N = %s;" % jints([t for _w, t in TOOL_TIERS_ALL]))''')

# ================================================================================================================ 2: the 49 items + their art
G23_ITEMS = r'''# ================================================================= 0.3.23 THE METAL TOOLS (tools/gear_0_3_23_patch.py, round G2): 49 forever tools of the
# 15-step ladder's metals, their art generated NOW by tools/art/make_metal_items.py (in memory; Quirk's PRIVATE builds read at build time)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools", "art"))
import make_metal_items as MMI
G23_METALS = ["Bronze", "Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]
G23_VAN = [w for w in TT.GEAR_INTERNAL[1:]]          # Copper .. Onyxium: the vanilla tool metals
G23_NEXT = dict((m, min((w for w in G23_VAN if TT.metal_tier(w) > TT.metal_tier(m)), key=TT.metal_tier)) for m in G23_METALS)
assert G23_NEXT == {"Bronze": "Thorium", "Lead": "Cobalt", "Dusk": "Cobalt", "Chromium": "Adamantite", "Azurvane": "Adamantite", "Slag": "Mithril",
                    "Cinder": "Mithril", "Titanium": "Onyxium", "Lumen": "Onyxium"}, G23_NEXT
assert all(dict(TOOL_TIERS_ALL)[m] == dict(TOOL_TIERS)[G23_NEXT[m]] for m in G23_METALS), "the internal tier of a new metal = its next vanilla tool's"
assert [w for w, _t in G23_ZT] == [w for w, _t in TT.TOOL_METALS[len(TOOL_TIERS):]] == G23_METALS[1:], "G23_ZT = tools/tier_tags.py's zone words"
G23_PICK = ["Tool_Pickaxe_%s_SkyWynn" % m for m in G23_METALS]
G23_HATCH = ["Tool_Hatchet_%s_SkyWynn" % m for m in G23_METALS]
G23_MULTI = [MULTI_PRE + m + "_SkyWynn" for m in G23_METALS]
G23_HARV_VAN = ["Cobalt", "Adamantite", "Mithril"]
G23_HARV = [HARV_PRE + m for m in G23_HARV_VAN] + [HARV_PRE + m + "_SkyWynn" for m in G23_METALS]
G23_CAN = ["Tool_WaterCan_Mithril"] + ["Tool_WaterCan_%s_SkyWynn" % m for m in G23_METALS]
G23_IDS = G23_PICK + G23_HATCH + G23_MULTI + G23_HARV + G23_CAN
assert len(G23_IDS) == len(set(G23_IDS)) == 49
assert sorted(G23_IDS) == sorted(TT.G2_FOREVER + TT.G2_HARVESTERS + TT.G2_CANS), "tools/tier_tags.py G2 rows = the items made here"
for _i in G23_IDS:
    assert _i not in AZ_ITEMS and _i not in _AZ_JSON, "0.3.23: %s is a vanilla id now - pick another" % _i
    assert TT.owner(_i) == "SkyyGear" and _i in TT.OWN_IDS and TT.tag_for(_i) is not None, _i
    assert _tool_tier(_i) is not None or _i.split("_")[-2] in dict(G23_ZT), _i
# the next vanilla tools exist (their Tool specs / interactions are the Parent of ours)
for _m in G23_METALS:
    for _p in ("Tool_Pickaxe_", "Tool_Hatchet_"):
        assert (_p + G23_NEXT[_m]) in AZ_ITEMS and az_get(_p + G23_NEXT[_m], "Tool"), _p + G23_NEXT[_m]
# Quirk's PRIVATE metal tool builds (the 0.3.21 folder rule: never in this repo; missing = stop)
G23_PRIV = os.path.join(os.environ.get("SKYWYNN_PRIVATE_ART") or os.path.join(os.path.dirname(os.path.dirname(HERE)), "SkyWynn-PRIVATE-art"),
                        "metal-art", "Tools-PRIVATE")
G23_TOOLS3 = ["Pickaxe", "Hatchet", "WateringCan"]          # main session 2026-10-18: Quirk's multitool / harvester MODELS are not shipped (open for Skyy)
_g23miss = [os.path.join(_b, _t + _x) for _b in ("Titanium", "Lumen") for _t in G23_TOOLS3 for _x in (".blockymodel", "_Texture.png")
            if not os.path.isfile(os.path.join(G23_PRIV, _b, _t + _x))]
if _g23miss:
    raise SystemExit("SkyyGear 0.3.23 needs Quirk's private metal tool builds in %s (missing: %s). Put the SkyWynn-PRIVATE-art folder next to "
                     "the project (or set SKYWYNN_PRIVATE_ART to it) - they are never committed to the public repo." % (G23_PRIV, ", ".join(_g23miss)))
MMI.PRIVATE_TOOLS = G23_PRIV
_g23z = SA.assets()
_g23it = MMI.Items(_g23z)


def _g23_hex(v):
    return "#%02X%02X%02X" % tuple(int(round(x)) for x in v)


def _g23_card(metal, trim, zone, kind, donor):
    """a PLACEHOLDER card (no approved one): the vanilla ingot texture's own colours (Assets.zip, now) + a vanilla trim metal"""
    g = SA.palette_from([SA._read(_g23z, "Resources/Materials/Ingot_Textures/%s.png" % metal)])
    c = SA.palette_from([SA._read(_g23z, "Resources/Materials/Ingot_Textures/%s.png" % trim)])
    return {"zone": zone, "kind": kind, "donor": donor, "base": _g23_hex(g[10]), "shade": _g23_hex(g[4]), "hi": _g23_hex(g[18]),
            "trim": _g23_hex(c[12]), "glow": None, "pattern": None}


def _g23_art(metals, tools_, cards=None):
    """{(tool, metal): (texture png, icon png, Quirk base 'Titanium' | 'Lumen')} from make_metal_items.tools() run in memory for these metals /
    tools; cards = placeholder palette cards added to its table for this run only"""
    saved = (MMI.METALS, MMI.TOOLS)
    added = []
    for _k, _v in sorted((cards or {}).items()):
        assert _k not in MMI.SPEC, _k
        MMI.SPEC[_k] = _v
        MMI.GEM[_k] = None
        added.append(_k)
    res = {}
    try:
        MMI.METALS, MMI.TOOLS = tuple(metals), tuple(tools_)
        o = MMI.Out(write=False)
        MMI.tools(_g23z, _g23it, o)
        for _t in tools_:
            for _m in metals:
                _b = "Lumen" if MMI.SPEC[_m]["kind"] == "alloy" else "Titanium"
                _tp = "tools/Common/Items/Tools/SkyyMetal/%s/%s_Texture.png" % (_t, _m)
                _tex = o.files.get(_tp)
                if _tex is None:
                    assert _m in ("Titanium", "Lumen"), _tp
                    _tex = open(os.path.join(G23_PRIV, _m, _t + "_Texture.png"), "rb").read()          # Quirk's own, untouched
                res[(_t, _m)] = (_tex, o.files["tools/Common/Icons/ItemsGenerated/SkyyMetal_%s_%s.png" % (_t, _m)], _b, _tp)
    finally:
        MMI.METALS, MMI.TOOLS = saved
        for _k in added:
            MMI.SPEC.pop(_k)
            MMI.GEM.pop(_k)
    return res


G23_ART = _g23_art(list(MMI.METALS), G23_TOOLS3)          # the 24 approved pickaxe / hatchet / can textures (they fit the vanilla models' UV)
assert list(MMI.METALS) == G23_METALS[1:] and list(MMI.TOOLS) == ["Pickaxe", "Hatchet", "Multitool", "Harvester", "WateringCan"] and len(G23_ART) == 24
# the approved files byte for byte (models-local/art/metals = what Skyy approved, when this PC has it)
_g23loc = os.path.join(os.path.dirname(HERE), "models-local", "art", "metals")
_g23same = [(k, v[3]) for k, v in sorted(G23_ART.items()) if os.path.isfile(os.path.join(_g23loc, v[3]))]
for _k, _rel in _g23same:
    assert open(os.path.join(_g23loc, _rel), "rb").read() == G23_ART[_k][0], "0.3.23: the generated %s differs from the approved file %s" % (_k, _rel)
    _ip = os.path.join(_g23loc, "tools", "Common", "Icons", "ItemsGenerated", "SkyyMetal_%s_%s.png" % _k)
    assert not os.path.isfile(_ip) or open(_ip, "rb").read() == G23_ART[_k][1], "0.3.23: the generated icon of %s differs from the approved one" % (_k,)
print("0.3.23 art: %d approved metal tool textures + icons generated (%d compared byte for byte with models-local/art/metals%s)"
      % (len(G23_ART), len(_g23same), "" if _g23same else " - not on this PC"))
# PLACEHOLDERS (no approved card yet): Bronze (pickaxe / hatchet / can, Quirk's Lumen build - an alloy) + the Mithril can
G23_CARDS = {"Bronze": _g23_card("Bronze", "Copper", 1, "alloy", "Copper"), "Cobalt": _g23_card("Cobalt", "Iron", 3, "ore", "Cobalt"),
             "Adamantite": _g23_card("Adamantite", "Iron", 4, "ore", "Adamantite"), "Mithril": _g23_card("Mithril", "Gold", 5, "ore", "Mithril")}
G23_ART.update(_g23_art(["Bronze"], G23_TOOLS3, {"Bronze": G23_CARDS["Bronze"]}))
G23_ART.update(_g23_art(["Mithril"], ["WateringCan"], {"Mithril": G23_CARDS["Mithril"]}))
assert len(G23_ART) == 28
print("0.3.23 placeholder cards (vanilla ingot colours): %s" % ", ".join("%s %s/%s/%s" % (m, c["shade"], c["base"], c["hi"]) for m, c in sorted(G23_CARDS.items())))
G23_FILES = {}
G23_ITEMJ = {}
G23_LANG = []
# NO private model ships (main session 2026-10-18; manifest question 3 still open for Skyy): the multitool = the vanilla Mithril pickaxe model with
# its metal's pickaxe texture + icon; the Harvester = the vanilla Thorium hoe model with a build-time recolour (the 0.3.12 Harvester recipe)
# in its metal card's colours. Quirk's approved multitool / harvester art waits for Skyy's answer.
G23_HOE = "Tool_Hoe_Thorium"
G23_HOE_M, G23_HOE_T, G23_HOE_I = az_get(G23_HOE, "Model"), az_get(G23_HOE, "Texture"), az_get(G23_HOE, "Icon")
for _p in (G23_HOE_M, G23_HOE_T, G23_HOE_I):
    assert ("Common/" + _p) in AZ_NAMES, _p
# Quirk's pickaxe / hatchet / can builds ARE the vanilla Mithril pickaxe / hatchet / can models (same JSON - checked): by path
_g23vm = {"Pickaxe": "Items/Tools/Pickaxe/Mithril.blockymodel", "Hatchet": "Items/Tools/Hatchet/Mithril.blockymodel", "WateringCan": CAN_MODEL}
for _t, _vp in sorted(_g23vm.items()):
    assert ("Common/" + _vp) in AZ_NAMES, _vp
    for _b in ("Titanium", "Lumen"):
        assert json.loads(open(os.path.join(G23_PRIV, _b, _t + ".blockymodel"), "rb").read().decode("utf-8-sig")) == json.loads(AZ.read("Common/" + _vp).decode("utf-8-sig")), \
            "0.3.23: Quirk's %s %s model is no longer the vanilla %s - it would need shipping" % (_b, _t, _vp)


def _g23_put(tool, m):
    """the texture + icon of (tool, metal) into the jar; returns (Texture, Icon) as the item JSON writes them"""
    tex, ico, _b, _tp = G23_ART[(tool, m)]
    tp = "Items/Tools/SkyyMetal/%s/%s_Texture.png" % (tool, m)
    ip = "Icons/ItemsGenerated/SkyyMetal_%s_%s.png" % (tool, m)
    G23_FILES["Common/" + tp] = tex
    G23_FILES["Common/" + ip] = ico
    return tp, ip


def _g23_word(i):
    return i.split("_")[-2] if i.endswith("_SkyWynn") else i.split("_")[-1]


def _g23_tr(i):
    return {"Name": "server.items.%s.name" % i, "Description": "server.items.%s.description" % i}


for _m, _pi, _hi, _mi in zip(G23_METALS, G23_PICK, G23_HATCH, G23_MULTI):
    _pp, _hp = "Tool_Pickaxe_" + G23_NEXT[_m], "Tool_Hatchet_" + G23_NEXT[_m]
    for _iid, _par, _tool, _vi in ((_pi, _pp, "Pickaxe", "Tool_Pickaxe_Mithril"), (_hi, _hp, "Hatchet", "Tool_Hatchet_Mithril")):
        _tx, _ic = _g23_put(_tool, _m)
        G23_ITEMJ["Server/Item/Items/SkyyGear/Metal/%s.json" % _iid] = json.dumps({
            "Parent": _par, "TranslationProperties": _g23_tr(_iid), "Model": _g23vm[_tool], "Texture": _tx, "Icon": _ic,
            "IconProperties": az_get(_vi, "IconProperties"), "MaxStack": 1}, indent=2)
    # the multitool: the pickaxe's specs with the hatchet's Woods spec (InkBlindCat's Multitools rule, MIT), both swings, both stat sets
    _tx, _ic = "Items/Tools/SkyyMetal/Pickaxe/%s_Texture.png" % _m, "Icons/ItemsGenerated/SkyyMetal_Pickaxe_%s.png" % _m          # its pickaxe's art
    assert ("Common/" + _tx) in G23_FILES and ("Common/" + _ic) in G23_FILES
    _tool = json.loads(json.dumps(az_get(_pp, "Tool")))
    _wd = [sp for sp in az_get(_hp, "Tool")["Specs"] if sp.get("GatherType") == "Woods"]
    assert len(_wd) == 1 and len([sp for sp in _tool["Specs"] if sp.get("GatherType") == "Woods"]) == 1, (_pp, _hp)
    _tool["Specs"] = [dict(_wd[0]) if sp.get("GatherType") == "Woods" else sp for sp in _tool["Specs"]]
    _iv = json.loads(json.dumps(az_get(_pp, "InteractionVars")))
    for _k, _v in sorted(az_get(_hp, "InteractionVars").items()):
        _iv.setdefault(_k, _v)
    assert "Hatchet_Chop_Damage" in _iv and "Pickaxe_Mine_Damage" in _iv, sorted(_iv)
    G23_ITEMJ["Server/Item/Items/SkyyGear/Metal/%s.json" % _mi] = json.dumps({
        "Parent": _pp, "TranslationProperties": _g23_tr(_mi), "Model": _g23vm["Pickaxe"], "Texture": _tx, "Icon": _ic,
        "IconProperties": az_get("Tool_Pickaxe_Mithril", "IconProperties"), "PlayerAnimationsId": "SkyyGear_Multitool",
        "Interactions": {"Primary": "SkyyGear_Multitool_Attack"}, "InteractionVars": _iv, "Tool": _tool, "MaxStack": 1}, indent=2)
# the multitool swing (InkBlindCat's Multitools design, MIT - credit in PACK.md): a wood block -> the hatchet chop, anything else -> the pickaxe
G23_FILES["Server/Item/Interactions/SkyyGear/Multitool/SkyyGear_Multitool_Attack.json"] = json.dumps({
    "Type": "BlockCondition", "Matchers": [{"Block": {"Tag": "Wood"}}], "Next": "Hatchet_Attack", "Failed": "Pickaxe_Attack"}, indent=2)
G23_FILES["Server/Item/RootInteractions/SkyyGear/SkyyGear_Multitool_Attack.json"] = json.dumps({"Interactions": ["SkyyGear_Multitool_Attack"]}, indent=2)
_g23pa = json.loads(AZ.read("Server/Item/Animations/Pickaxe.json").decode("utf-8-sig"))
_g23ha = json.loads(AZ.read("Server/Item/Animations/Hatchet.json").decode("utf-8-sig"))
assert list(_g23pa["Animations"]) == ["Mine"] and list(_g23ha["Animations"]) == ["Chop"] and _g23pa.get("Parent") == _g23ha.get("Parent") == "Sword"
_g23an = json.loads(json.dumps(_g23pa))
_g23an["Animations"]["Chop"] = _g23ha["Animations"]["Chop"]
G23_FILES["Server/Item/Animations/SkyyGear/SkyyGear_Multitool.json"] = json.dumps(_g23an, indent=2)
for _r in ("Hatchet_Attack", "Pickaxe_Attack"):
    assert [n for n in AZ_NAMES if n.endswith("/Interactions/Weapons/%s/Variants/%s.json" % (_r.split("_")[0], _r))], "no vanilla interaction " + _r
# the Harvesters: the 0.3.14 shape (Thorium's: Parent Tool_Sickle_Iron, Hoe_Till, our sweep HitBlock), the vanilla Thorium hoe model, our recolour
_g23hv = json.loads(HARV_ITEMS["Server/Item/Items/SkyyGear/%s.json" % (HARV_PRE + "Thorium")])
assert _g23hv["Parent"] == "Tool_Sickle_Iron" and _g23hv["Interactions"]["Secondary"] == "Hoe_Till" and _g23hv["PlayerAnimationsId"] == HARV_ANIM
for _hid in G23_HARV:
    _m = _g23_word(_hid)
    _cd = G23_CARDS.get(_m) or MMI.SPEC[_m]          # the approved card (8 zone metals) or the vanilla-ingot placeholder card
    _rp = _ramp((_cd["shade"], _cd["base"], _cd["hi"]))
    _tx = "Items/SkyyGear/Harvester/Harvester_%s.png" % _m
    _ic = "Icons/ItemsGenerated/%s.png" % _hid
    G23_FILES["Common/" + _tx] = SA.recolor(AZ.read("Common/" + G23_HOE_T), _rp, rank=0.4)
    G23_FILES["Common/" + _ic] = SA.recolor_icon(AZ.read("Common/" + G23_HOE_I), _rp, rank=0.4)
    _j = json.loads(json.dumps(_g23hv))
    _j.update({"TranslationProperties": _g23_tr(_hid), "Model": G23_HOE_M, "Texture": _tx, "Icon": _ic,
               "IconProperties": az_get(G23_HOE, "IconProperties"), "Quality": az_get("Tool_Pickaxe_" + (_m if _m in G23_VAN else G23_NEXT[_m]), "Quality") or "Common"})
    assert "Recipe" not in _j
    G23_ITEMJ["Server/Item/Items/SkyyGear/Metal/%s.json" % _hid] = json.dumps(_j, indent=2)
# the cans: the 0.3.12 can shape (vanilla can model by path, our SkyyGear_Can_Use), our art
_g23cj = json.loads(CAN_ITEMS["Server/Item/Items/SkyyGear/Tool_WaterCan_Iron.json"])
for _cid in G23_CAN:
    _m = _g23_word(_cid)
    _tx, _ic = _g23_put("WateringCan", _m)
    _j = json.loads(json.dumps(_g23cj))
    _j.update({"TranslationProperties": _g23_tr(_cid), "Texture": _tx, "Icon": _ic})
    G23_ITEMJ["Server/Item/Items/SkyyGear/Metal/%s.json" % _cid] = json.dumps(_j, indent=2)
assert len(G23_ITEMJ) == 49
for _k, _v in list(G23_FILES.items()) + list(G23_ITEMJ.items()):
    assert _k not in AZ_NAMES and _k not in EXTRA, "a 0.3.23 file would shadow another file: " + _k
    if _k.endswith(".png"):
        _w, _h = SA.png_size(_v)
        assert _w > 0 and _h > 0 and (_w == _h == 64 if "/Icons/" in _k else _w % 32 == 0 and _h % 32 == 0), (_k, _w, _h)
    if _k.endswith(".json"):
        assert "Recipe" not in json.loads(_v), "0.3.23: forever tools are never crafted (gear.md 2026-10-12): " + _k
_g23txt = {"Pickaxe": "Your lifelong pickaxe, one step of the 15-metal ladder. It levels with Mining; tier it up on the Anvil.",
           "Hatchet": "Your lifelong hatchet, one step of the 15-metal ladder. It levels with Foraging; tier it up on the Anvil.",
           "Multitool": "A pickaxe and a hatchet in one (after your first rebirth): stone and ore use your pickaxe upgrades, logs your hatchet's.",
           "Harvester": "Your lifelong farming tool: right-click tills soil; a swing reaps every crop of its tier and lower and cuts plants - one tier higher breaks one at a time for half Farming XP.",
           "WateringCan": "Your lifelong watering can. Hold right-click and look across tilled soil to water it, right-click water to refill. A higher tier waters a bigger square."}
_g23nm = {"Pickaxe": "Pickaxe", "Hatchet": "Hatchet", "Multitool": "Multitool", "Harvester": "Harvester", "WateringCan": "Watering Can"}
for _ids, _tool in ((G23_PICK, "Pickaxe"), (G23_HATCH, "Hatchet"), (G23_MULTI, "Multitool"), (G23_HARV, "Harvester"), (G23_CAN, "WateringCan")):
    for _i in _ids:
        G23_LANG.append("items.%s.name = %s %s" % (_i, _g23_word(_i), _g23nm[_tool]))
        G23_LANG.append("items.%s.description = %s" % (_i, TT.described(_i, _g23txt[_tool])))
EXTRA.update(G23_FILES)
EXTRA.update(G23_ITEMJ)
EXTRA["Server/Languages/en-US/server.lang"] = EXTRA["Server/Languages/en-US/server.lang"] + "\n".join(G23_LANG) + "\n"
_g23z.close()
print("0.3.23 items: %d forever tools (%d pickaxes, %d hatchets, %d multitools, %d Harvesters, %d cans), %d art / model / interaction files"
      % (len(G23_ITEMJ), len(G23_PICK), len(G23_HATCH), len(G23_MULTI), len(G23_HARV), len(G23_CAN), len(G23_FILES)))
'''
before('''# 0.3.0 LIFELONG TOOLS: the tier-up ladders on the Anvil (Skyy 2026-10-13 G1 "25 Copper Ingots (Recommended)"; 2026-10-11 "it costs a''', G23_ITEMS)

# ================================================================================================================ 3: the 15-step ladders
G23_LAD = r'''# ================================================================= 0.3.23 THE 15-STEP TOOL LADDERS (round G2; spec 3.3 + Q7): every step costs its metal's
# bars (Enchanted ingots where tools/skyyench.py has one, the 0.3.0 counts kept; alloy bars = the Furnace Charm tier-up counts); the hatchet /
# Harvester / can steps add the skill item of the vanilla step they mirror (the 0.3.0 / 0.3.12 items and counts). The 0.3.22 defaults stay for migrate0323.
LL_LADDER_OLD = LL_LADDER_DEF
G23_ORDER = list(TT.LADDER[:15])          # Copper .. Lumen
assert G23_ORDER[0] == "Copper" and G23_ORDER[-1] == "Lumen" and set(G23_METALS) | set(G23_VAN[:-1]) == set(G23_ORDER)
G23_BAR = {"Copper": _LLB, "Iron": _lle("Iron", 1), "Bronze": "Ingredient_Bar_Bronze*32", "Thorium": _lle("Thorium", 1), "Lead": _lle("Lead", 1),
           "Dusk": "Ingredient_Bar_Dusk_SkyWynn*64", "Cobalt": _lle("Cobalt", 2), "Chromium": _lle("Chromium", 2),
           "Azurvane": "Ingredient_Bar_Azurvane_SkyWynn*128", "Adamantite": _lle("Adamantite", 2), "Slag": _lle("Slag", 2),
           "Cinder": "Ingredient_Bar_Cinder_SkyWynn*192", "Mithril": _lle("Mithril", 3), "Titanium": _lle("Titanium", 3),
           "Lumen": "Ingredient_Bar_Lumen_SkyWynn*256"}
G23_LOG = {"Iron": ("Maple", 1), "Thorium": ("Gumboab", 1), "Cobalt": ("Redwood", 2), "Adamantite": ("Sallow", 2), "Mithril": ("Sallow", 3), "Onyxium": ("Sallow", 4)}
G23_CROP = {"Iron": ("Carrot", 1), "Thorium": ("Cauliflower", 1), "Cobalt": ("Pumpkin", 2), "Adamantite": ("Tomato", 2), "Mithril": ("Cotton", 3),
            "Onyxium": ("Potato", 3)}


def _g23_mir(m):
    return m if m in G23_VAN else G23_NEXT[m]


def _g23_id(kind, m):
    if m == "Crude":
        return {"pick": "Tool_Pickaxe_Crude", "hatch": "Tool_Hatchet_Crude", "harv": HARV_PRE + "Crude", "can": "Tool_WaterCan_Crude"}[kind]
    if kind == "pick":
        return ("Tool_Pickaxe_" + m) if m in G23_VAN else "Tool_Pickaxe_%s_SkyWynn" % m
    if kind == "hatch":
        return ("Tool_Hatchet_" + m) if m in G23_VAN else "Tool_Hatchet_%s_SkyWynn" % m
    if kind == "harv":
        return (HARV_PRE + m) if m in G23_VAN else HARV_PRE + m + "_SkyWynn"
    return ("Tool_WaterCan_" + m) if m in G23_VAN else "Tool_WaterCan_%s_SkyWynn" % m


def _g23_row(kind, extra):
    r = _g23_id(kind, "Crude")
    for m in G23_ORDER:
        c = G23_BAR[m]
        if extra is not None and m != "Copper":
            c += "+%s%s*%d" % (ENCH.PREFIX, extra[_g23_mir(m)][0], extra[_g23_mir(m)][1])
        r += ">%s(%s)" % (_g23_id(kind, m), c)
    return r


G23_LADROW = {"pick": _g23_row("pick", None), "hatch": _g23_row("hatch", G23_LOG), "harv": _g23_row("harv", G23_CROP), "can": _g23_row("can", G23_CROP)}
assert LL_LADDER_ROWS[0].startswith("Tool_Pickaxe_Crude>") and LL_LADDER_ROWS[3].startswith("Tool_Hatchet_Crude>")
assert all(_x in G23_LADROW["pick"].split(">") for _x in LL_LADDER_ROWS[0].split(">")), "0.3.23: every 0.3.22 pickaxe step keeps its exact cost"
LL_LADDER_ROWS = [G23_LADROW["pick"]] + LL_LADDER_ROWS[1:3] + [G23_LADROW["hatch"]] + LL_LADDER_ROWS[4:]
LL_LADDER_DEF = ",".join(LL_LADDER_ROWS)
assert len(LL_LADDER_DEF) < 4000 and all(32 <= ord(_c) < 127 for _c in LL_LADDER_DEF), len(LL_LADDER_DEF)
def _g23_ids(row):
    """the item ids of one ladder row A>B(cost)>C(cost)"""
    return [_x.split("(")[0].strip() for _x in row.split(">")]


for _r in G23_LADROW.values():
    for _st in _r.split(">")[1:]:
        for _c in _st[_st.index("(") + 1:-1].split("+"):
            _ci = _c.split("*")[0]
            assert _ci in AZ_ITEMS or _ci in ENCH.IDS or _ci in TT.WG_IDS, "0.3.23 ladder material %s is no item" % _ci
    for _i in _g23_ids(_r):
        assert _i in AZ_ITEMS or _i in G23_IDS or _i.startswith(HARV_PRE) or _i.startswith("Tool_WaterCan_"), "0.3.23 ladder names %s" % _i
assert [len(_g23_ids(_r)) for _k, _r in sorted(G23_LADROW.items())] == [16, 16, 16, 16]
# internal tiers never fall along the ladder (no line cap / gate falls on a tier-up; spec UNVERIFIED line "cap(new) >= cap(old)")
for _r in G23_LADROW.values():
    _ts = [dict(TOOL_TIERS_ALL)[w] for w in ["Crude"] + G23_ORDER]
    assert _ts == sorted(_ts), _ts
print("0.3.23 ladders: lifelong.ladders %d chars (pickaxe + hatchet Crude .. Lumen), harvester / can rows %d / %d chars"
      % (len(LL_LADDER_DEF), len(G23_LADROW["harv"]), len(G23_LADROW["can"])))
'''
after('''for _i in re.findall(r"(Tool_[A-Za-z]+_[A-Za-z]+)", LL_LADDER_DEF) + ["Ingredient_Bar_Copper"]:
    assert _i in AZ_ITEMS, "lifelong.ladders names %s - not in Assets.zip" % _i
''', G23_LAD)
G23_CLAD = r'''# 0.3.23: the can + Harvester ladders run Crude .. Lumen (G23_LADROW; the 0.3.22 texts stay for migrate0323)
CAN_LAD_OLD, HARV_LAD_OLD = CAN_LAD_DEF, HARV_LAD_DEF
CAN_LAD_DEF, HARV_LAD_DEF = G23_LADROW["can"], G23_LADROW["harv"]
G23_CAN_LAD = _g23_ids(CAN_LAD_DEF)
G23_HARV_LAD = _g23_ids(HARV_LAD_DEF)
assert set(G23_CAN) <= set(G23_CAN_LAD) and [_x for _x in G23_CAN_LAD if _x in CAN_IDS] == CAN_IDS
assert set(HARV_IDS) <= set(G23_HARV_LAD) and set(G23_HARV) <= set(G23_HARV_LAD) and len(G23_CAN_LAD) == len(G23_HARV_LAD) == 16
for _l in (CAN_LAD_DEF, HARV_LAD_DEF):
    assert len(_l) < 2000 and all(32 <= ord(_c) < 127 for _c in _l)
'''
after('''assert [_x.split("(")[0] for _x in CAN_LAD_DEF.split(">")] == CAN_IDS and [_x.split("(")[0] for _x in HARV_LAD_DEF.split(">")] == HARV_IDS
''', G23_CLAD)
rep('''    LL_KLAD.append(",".join(re.findall(r"(Tool_[A-Za-z]+_[A-Za-z]+)", _row[0])))
assert LL_KLAD[0].endswith("Tool_Pickaxe_Adamantite") and LL_KLAD[2].endswith("Tool_Hoe_Thorium") and LL_KLAD[3].endswith("Tool_Sickle_Iron")''',
    '''    LL_KLAD.append(",".join(_g23_ids(_row[0])))          # 0.3.23: + the _SkyWynn ids (the row's ids, costs dropped)
assert LL_KLAD[0].endswith("Tool_Pickaxe_Lumen_SkyWynn") and LL_KLAD[1].endswith("Tool_Hatchet_Lumen_SkyWynn") and LL_KLAD[2].endswith("Tool_Hoe_Thorium") and LL_KLAD[3].endswith("Tool_Sickle_Iron")
assert len(LL_KLAD[0].split(",")) == len(LL_KLAD[1].split(",")) == 16''')
rep('''LL_KLAD.append(",".join(CAN_IDS))          # 0.3.12: the can's ladder (its costs: can.ladders)''',
    '''LL_KLAD.append(",".join(G23_CAN_LAD))          # 0.3.12: the can's ladder (its costs: can.ladders); 0.3.23: Crude .. Lumen''')
rep('''F(gll, "public static final String HARV_LAD = %s;" % jstr(",".join(HARV_IDS)))
F(gll, "public static final int HARV_TOP = %d;" % dict(TOOL_TIERS)[HARV_TIERS[-1]])          # 0.3.14: the Harvester ladder's top tier (Thorium = 3)
assert dict(TOOL_TIERS)[HARV_TIERS[-1]] == 3 and dict(TOOL_TIERS)["Crude"] == 0 and dict(TOOL_TIERS)["Copper"] == 1''',
    '''F(gll, "public static final String HARV_LAD = %s;" % jstr(",".join(G23_HARV_LAD)))          # 0.3.23: Crude .. Lumen
F(gll, "public static final int HARV_TOP = %d;" % dict(TOOL_TIERS)[HARV_TIERS[-1]])          # 0.3.14: the Harvester's crop top (Thorium = 3); 0.3.23 critic M3: kept, so a Thorium Harvester still reaps every crop in full
assert dict(TOOL_TIERS)[HARV_TIERS[-1]] == 3 and dict(TOOL_TIERS)["Crude"] == 0 and dict(TOOL_TIERS)["Copper"] == 1
# 0.3.23 critic M2: each kind's 0.3.22 ladder top (internal tier, GearLL.tier's words of 0.3.22) - a tool at / above it keeps the uncapped line
def _g23_jt(i):
    for _w in i.split("_")[2:]:
        for _n, _t in TOOL_TIERS:
            if _w.lower() == _n.lower() and _n != "Bronze":
                return _t
    return 0


_g23_old_rows = LL_LADDER_OLD.split(",")
G23_OLDTOP = []
for _k, _n in enumerate(LL_KNAME[:4]):
    _r = [_x for _x in _g23_old_rows if _x.startswith("Tool_%s_Crude>" % _n)][0]
    G23_OLDTOP.append(max(_g23_jt(_x.split("(")[0]) for _x in _r.split(">")))
G23_OLDTOP.append(max(_g23_jt(_x) for _x in LL_POLE_LAD.split(",")))
G23_OLDTOP.append(max(_g23_jt(_x) for _x in CAN_IDS))
assert G23_OLDTOP == [5, 5, 3, 2, 2, 5], G23_OLDTOP
F(gll, "public static final int[] OLDTOP = %s;" % jints(G23_OLDTOP))
F(gll, "public static final int OLDTOP_HARV = %d;" % max(_g23_jt(_x) for _x in HARV_IDS))''')
# the Java load defaults of the two can / Harvester rows (0.3.12 wrote them as literals)
rep('''  CAN_LADDERS = ptext(p, "can.ladders", "Tool_WaterCan_Crude>Tool_WaterCan_Copper(Ingredient_Bar_Copper*25)>Tool_WaterCan_Iron(Skyy_Ench_Carrot*1)>Tool_WaterCan_Thorium(Skyy_Ench_Cauliflower*1)>Tool_WaterCan_Cobalt(Skyy_Ench_Pumpkin*2)>Tool_WaterCan_Adamantite(Skyy_Ench_Tomato*2)").trim();''',
    '''  CAN_LADDERS = ptext(p, "can.ladders", "@CANLADDEF@").trim();          // 0.3.23: Crude .. Lumen''')
rep('''  HARV_LADDERS = ptext(p, "harvester.ladders", "Tool_Sickle_Harvester_Crude>Tool_Sickle_Harvester_Copper(Ingredient_Bar_Copper*25)>Tool_Sickle_Harvester_Iron(Skyy_Ench_Carrot*1)>Tool_Sickle_Harvester_Thorium(Skyy_Ench_Cauliflower*1)").trim();''',
    '''  HARV_LADDERS = ptext(p, "harvester.ladders", "@HARVLADDEF@").trim();          // 0.3.23: Crude .. Lumen''')
rep('''   .replace("@ORETIERS@", ORE_TIERS_DEF).replace("@TIERPOW@", TIER_POW_DEF).replace("@OREFLOOR@", ORE_FLOOR_DEF))          # 0.3.22''',
    '''   .replace("@ORETIERS@", ORE_TIERS_DEF).replace("@TIERPOW@", TIER_POW_DEF).replace("@OREFLOOR@", ORE_FLOOR_DEF)          # 0.3.22
   .replace("@CANLADDEF@", CAN_LAD_DEF).replace("@HARVLADDEF@", HARV_LAD_DEF))          # 0.3.23''')
rep('''    ("lifelong.ladders", "Tool tier-up costs", "lifelong", "text", LL_LADDER_DEF, "0", "2000", "", "", "live,danger",''',
    '''    ("lifelong.ladders", "Tool tier-up costs", "lifelong", "text", LL_LADDER_DEF, "0", "4000", "", "", "live,danger",          # 0.3.23: 2000 -> 4000''')

# ================================================================================================================ 4: the ore gate with every step's pickaxe
G23_GATE = r'''# ================================================================= 0.3.23 THE ORE GATE WITH EVERY STEP'S PICKAXE (round G2; spec 3.2): our 9 pickaxes join PICK_T
# (G22_OWN_PICKS), so "the next pickaxe step" is the next ladder step (gate.nextByLadder; off = the vanilla steps of 0.3.22) and gate.oreFloor's
# interim zone ores go (default ""). The 0.3.22 values stay for the proof table + migrate0323.
G23_PICK_TV, G23_PICK_IDV, ORE_FLOOR_OLD = list(PICK_T), list(PICK_ID), ORE_FLOOR_DEF
G22_OWN_PICKS = list(G23_PICK)
PICK_T = sorted(set(TT.metal_tier(_i.split("_")[2]) for _i in list(_TOOL_AZ_IDS) + G22_OWN_PICKS
                    if _i.startswith("Tool_Pickaxe_") and TT.metal_tier(_i.split("_")[2])))
assert PICK_T == list(range(1, 17)), "0.3.23: a pickaxe on every ladder step: %s" % PICK_T
PICK_ID = []
for _t in PICK_T:
    _c = sorted(_i for _i in list(_TOOL_AZ_IDS) + G22_OWN_PICKS if _i.startswith("Tool_Pickaxe_") and TT.metal_tier(_i.split("_")[2]) == _t)
    PICK_ID.append("Tool_Pickaxe_" + TT.noun(_t) if "Tool_Pickaxe_" + TT.noun(_t) in _c else _c[0])
assert [PICK_ID[_t - 1] for _t in G23_PICK_TV] == G23_PICK_IDV and set(PICK_ID) - set(G23_PICK_IDV) == set(G23_PICK)
ORE_FLOOR_DEF = ""
for _m in G23_METALS:          # our pickaxes' vanilla specs = their Parent's (the next vanilla pickaxe)
    _vs[_m] = _vs[G23_NEXT[_m]]


def _g23_hit(m, w, n, h, gt, q, pt, pid, pnext, fl):
    """the Lv 1 hit of pickaxe metal m on an ore (GearLL.oreDr x slowF, _g22_new's maths): rpow from the step table pt / pid, the next-pickaxe
    rule from pnext (GearLL.nextPick), the floor words fl"""
    t = max(1, TT.metal_tier(m))
    d0 = _g22_v(m, gt, q)
    if t >= n:
        return max(d0, ORE_BASE * TIER_POW[min(t, 16) - 1] / TIER_POW[min(n, 16) - 1])
    k = [i for i, p in enumerate(pt) if p >= n][0]
    ref = max(ORE_BASE, _g22_v(pid[k].split("_")[2], gt, q))
    f = 0.5 if (h and t >= h) else (0.4 if min([p for p in pnext if p > t] or [999]) >= n else 0.1)
    return max(ref, d0 / f) * f if w in fl else ref * f


_g23_fl0 = [x for x in ORE_FLOOR_OLD.split(",") if x]
_g23_fl1 = [x for x in ORE_FLOOR_DEF.split(",") if x]
G23_EXIST = [_m for _m, _mi in _G22_PK]
G23_HITS = []
G23_SLOWER = []
G23_BAD = []
for _m in G23_EXIST + G23_METALS:
    _row = []
    for _w, _n, _h, _b, _gt, _q in G22_BLK:
        _o = _g22_hits(_g23_hit(_m, _w, _n, _h, _gt, _q, G23_PICK_TV, G23_PICK_IDV, G23_PICK_TV, _g23_fl0)) if _m in G23_EXIST else 0
        _x = _g22_hits(_g23_hit(_m, _w, _n, _h, _gt, _q, PICK_T, PICK_ID, PICK_T, _g23_fl1))
        _sw = _g22_hits(_g23_hit(_m, _w, _n, _h, _gt, _q, PICK_T, PICK_ID, G23_PICK_TV, _g23_fl0))          # gate.nextByLadder off + the 0.3.22 floor
        _row.append((_o, _x))
        if _m in G23_EXIST:
            assert _sw == _o, "0.3.23: gate.nextByLadder off + gate.oreFloor %s must hit like 0.3.22: %s on %s %d > %d" % (ORE_FLOOR_OLD, _m, _w, _o, _sw)
            _t = max(1, TT.metal_tier(_m))
            if _o and (not _x or _x > _o):
                (G23_BAD if (_t >= _n or (_h and _t >= _h)) else G23_SLOWER).append((_m, _w, _o, _x))
    G23_HITS.append((_m, _row))
print("0.3.23 ore gate (gate.nextByLadder on; gate.oreFloor '%s'; pickaxe steps T%s) - hits at Lv 1, 0.3.22 > 0.3.23 (0 = refused / none):"
      % (ORE_FLOOR_DEF, ",".join(str(_t) for _t in PICK_T)))
print("  %-16s %s" % ("pickaxe", " ".join("%-9s" % ("%s %d" % (_w[:6], _n)) for _w, _n, _h, _b, _gt, _q in G22_BLK)))
for _m, _row in G23_HITS:
    print("  %-16s %s" % ("%s T%d" % (_m, TT.metal_tier(_m)), " ".join("%-9s" % (("%d>%d" % _c) if _m in G23_EXIST else ("-> %d" % _c[1])) for _c in _row)))
assert not G23_BAD, "0.3.23: an existing pickaxe got slower on an ore inside its own reach: %s" % G23_BAD
print("0.3.23 deliberately slower (an ore 2+ ladder steps above a vanilla pickaxe, spec 3.2 'anything lower = 10x'; gate.nextByLadder off + "
      "gate.oreFloor %s = the 0.3.22 hits): %s" % (ORE_FLOOR_OLD, ", ".join("%s on %s %d>%d" % _x for _x in G23_SLOWER)))
# every step's pickaxe mines its own ores at normal speed and the zone's alloy pickaxe opens the next zone (base ore normal, new ore half)
for _w, _n, _h, _b, _gt, _q in G22_BLK:
    _pm = PICK_ID[_n - 1].split("_")[2]
    assert _g23_hit(_pm, _w, _n, _h, _gt, _q, PICK_T, PICK_ID, PICK_T, _g23_fl1) >= ORE_BASE, (_w, _pm)
for _a, _base, _new in (("Dusk", "Cobalt", "Chromium"), ("Azurvane", "Adamantite", "Slag"), ("Cinder", "Mithril", "Titanium")):
    _nb, _hb = [(_n, _h) for _w, _n, _h in G22_ORE if _w == _base][0]
    _nn, _hn = [(_n, _h) for _w, _n, _h in G22_ORE if _w == _new][0]
    assert TT.metal_tier(_a) >= _nb and _hn <= TT.metal_tier(_a) < _nn, (_a, _base, _new)
# the level bands of the new items (G1's level.material.<Metal>_SkyWynn rows; Bronze = the LOCKED 15-23)
_g23bt = list(BD_ALL) + [("%s_SkyWynn" % _w, _a, _c) for _w, _a, _c in G22_BANDS]
for _i in G23_IDS:
    _e, _s0, _c0 = band_lookup(_g23bt, _i)
    _mw = _g23_word(_i)
    _want = ("bronze", 15, 23) if _mw == "Bronze" else ((_mw.lower(),) + tuple(dict((_w, (_a, _c)) for _w, _a, _c in BD_ALL)[_mw]) if _mw in G23_VAN
                                                        else (_mw.lower() + "_skywynn",) + [(_a, _c) for _w, _a, _c in G22_BANDS if _w == _mw][0])
    assert (_e, _s0, _c0) == _want, "0.3.23: %s reads the level band %s, want %s" % (_i, (_e, _s0, _c0), _want)
# 0.3.23 EXTRA SCOPE (main session 2026-10-18, round A1 = SkyyArmory 0.1.33's 76 new-metal weapons, ids Weapon_<Family>_<M>_SkyWynn +
# Weapon_Crossbow_<Thorium|Cobalt|Adamantite|Mithril>_Wynn): (a) the loot pool gets the new Bo / Gauntlets / Kunai / Spellbook / GreatShield /
# Crossbow / Mage staff ids + the 4 gap crossbows (crafted, never drop-only; level = the level.material.<M>_SkyWynn rows; wands stay out like
# 0.3.21's); (b) OWN_TRUST (above) trusts the 12 new crossbows like the Copper / Onyxium ones; (c) the Soul Cage upgrade ladder runs the 15 steps
# (Copper .. Lumen, then Onyxium; GearUp.fromRecipeAlt pays a step whose recipe takes an EARLIER cage - Dusk -> Cobalt pays the Cobalt cage
# recipe made from the Thorium cage); (d) GearBase.kunaiTwin already maps by the full key <M>_SkyWynn (Weapon_Daggers_Lead_SkyWynn /
# Weapon_Sword_Lead_SkyWynn / Weapon_Longsword_Lead_SkyWynn - A2's twins), the id itself until they exist (harness-checked).
G23_AR_KEYS = ["%s_SkyWynn" % _m for _m in G23_METALS[1:]]
G23_AR_GAP = ["Weapon_Crossbow_%s_Wynn" % _m for _m in ("Thorium", "Cobalt", "Adamantite", "Mithril")]
G23_AR_POOL = (["Weapon_%s_%s" % (_f, _k) for _f in ("Bo", "Fist_Gauntlets", "Kunai", "Spellbook", "GreatShield", "Crossbow", "Staff")
                for _k in G23_AR_KEYS] + G23_AR_GAP)
assert len(G23_AR_POOL) == len(set(G23_AR_POOL)) == 60
assert not [_i for _i in G23_AR_POOL if _i in AZ_ITEMS or _i in set(_p[0] for _p in LOOT_POOL)], "a new Armory pool id is vanilla / already pooled"
_g23aj = os.path.join(os.path.dirname(HERE), "SkyyArmory", "SkyyArmory-0.1.33.jar")
if os.path.isfile(_g23aj):
    with zipfile.ZipFile(_g23aj) as _z:
        G23_AR_JAR = set(os.path.basename(_n)[:-5] for _n in _z.namelist() if _n.startswith("Server/Item/Items/") and _n.endswith(".json"))
        _g23ar_rc = {}
        for _n in _z.namelist():
            if _n.startswith("Server/Item/Items/") and _n.endswith(".json") and "SoulCage" in _n:
                _g23ar_rc[os.path.basename(_n)[:-5]] = json.loads(_z.read(_n).decode("utf-8-sig")).get("Recipe")
    assert set(G23_AR_POOL) <= G23_AR_JAR, "SkyyArmory 0.1.33 lacks %s" % sorted(set(G23_AR_POOL) - G23_AR_JAR)
else:
    G23_AR_JAR, _g23ar_rc = None, None
    print("note: SkyyArmory/SkyyArmory-0.1.33.jar not in the repo - the new Armory ids were not checked against it")
_g23bt0 = list(BD_ALL) + [("%s_SkyWynn" % _w, _a, _c) for _w, _a, _c in G22_BANDS]
for _i in G23_AR_POOL:
    _e, _mn, _cp = band_lookup(_g23bt0, _i)
    assert _e is not None and (_e.endswith("_skywynn") or _i in G23_AR_GAP), (_i, _e)
    assert _ltype(_i) in LOOT_TYPES, (_i, _ltype(_i))
    LOOT_POOL.append((_i, _ltype(_i), 0, False, max(1, _mn), max(max(1, _mn), _cp)))
ARMORY_POOL = ARMORY_POOL + G23_AR_POOL
assert sum(1 for _p in LOOT_POOL if _p[0] in ARMORY_POOL) == len(ARMORY_POOL) == 43 + 60
# (c) the Soul Cage ladder of the 15 steps (+ Onyxium); the 0.3.22 text stays for migrate0323
UP_LADDER_OLD = UP_LADDER_DEF
UP_SOUL15 = (["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_" + (_m if _m in G23_VAN else _m + "_SkyWynn") for _m in G23_ORDER if _m != "Bronze"]
             + ["Weapon_Wand_SoulCage_Onyxium"])
assert [_x for _x in UP_SOUL15 if _x in UP_SOUL] == UP_SOUL and len(UP_SOUL15) == 16
UP_LADDER_DEF = ">".join(UP_SOUL15)
assert len(UP_LADDER_DEF) < 2000 and all(32 <= ord(_c) < 127 for _c in UP_LADDER_DEF)
if _g23ar_rc is not None:          # every step is payable: its recipe takes the cage before it, or (fromRecipeAlt) an EARLIER cage of the ladder
    _g23sub = []
    for _k in range(1, len(UP_SOUL15)):
        _r = _g23ar_rc.get(UP_SOUL15[_k])
        _ins = [_x["ItemId"] for _x in (_r or {}).get("Input", []) if int(_x.get("Quantity", 0)) == 1 and _x.get("ItemId") in UP_SOUL15[:_k]]
        assert _r and len(_ins) == 1, "SkyyArmory 0.1.33: %s is made from no single earlier cage: %s" % (UP_SOUL15[_k], _ins)
        if _ins[0] != UP_SOUL15[_k - 1]:
            _g23sub.append("%s > %s (its recipe takes %s)" % (UP_SOUL15[_k - 1], UP_SOUL15[_k], _ins[0]))
    print("0.3.23 Soul Cage ladder: %d steps; paid through an earlier cage's recipe (GearUp.fromRecipeAlt): %s" % (len(UP_SOUL15) - 1, "; ".join(_g23sub)))
# 0.3.23 ONE-TIME UPDATE migrate0323: the 0.3.22 defaults -> the 15-step ladders + no ore floor (text compare, only untouched lines)
H23_MARK_ID = "SkyyGear 0.3.23 default update"
H23_WHO = "SkyyGear 0.3.23"
H23_KEYS = ["lifelong.ladders", "can.ladders", "harvester.ladders", "gate.oreFloor", "upgrade.ladders"]
H23_OLD = [LL_LADDER_OLD, CAN_LAD_OLD, HARV_LAD_OLD, ORE_FLOOR_OLD, UP_LADDER_OLD]
H23_NEW = [LL_LADDER_DEF, CAN_LAD_DEF, HARV_LAD_DEF, ORE_FLOOR_DEF, UP_LADDER_DEF]
H23_MARK = ("# %s (Skyy 2026-10-17): the 15-metal tool ladders (pickaxe, hatchet, Harvester and can tier up Crude .. Lumen), the 15-metal Soul "
            "Cage upgrade ladder and no ore speed floor (every zone ore has its own pickaxe now)" % H23_MARK_ID)
assert all(32 <= ord(_c) < 127 for _c in H23_MARK) and "=" not in H23_MARK and H23_MARK.startswith("# ")
assert all(o != n for o, n in zip(H23_OLD, H23_NEW)) and all("\\" not in x and "\n" not in x for x in H23_OLD + H23_NEW)
G323_HEAD = "# ---- the metal tools: the 15-step tool ladders, every step's pickaxe in the ore gate (SkyyGear 0.3.23) ----"
G323_ROWK = ["gate.nextByLadder"]
assert all(32 <= ord(_c) < 127 for _c in G323_HEAD) and "=" not in G323_HEAD
'''
before('''CFG_ROWS = [
''', G23_GATE)
# the Server Setup row + field + loader + the danger list + the fresh file
after('''    ("gate.oreFloor", "Ores never below vanilla speed", "lifelong", "text", ORE_FLOOR_DEF, "0", "300", "", "", "live,danger",
     "These ores never break slower than vanilla (zone ores until their alloy pickaxes exist; then empty).",
     "field:GearCfg.ORE_FLOOR;check=GearLL.checkOreFloor"),
''', '''    # 0.3.23 THE METAL TOOLS (round G2): every ladder pickaxe is a step of the ore gate (off = only the vanilla pickaxes, the 0.3.22 speeds)
    ("gate.nextByLadder", "Every ladder pickaxe is a step", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On: ore 2+ ladder steps above your pickaxe = 10x the hits. Off: only vanilla pickaxes count.", "field:GearCfg.GATE_NBL"),
''')
rep('''           "gate.oreTiers", "gate.halfFactor", "tool.tierPower", "lifelong.perkFortune.mining", "gate.oreFloor"}''',
    '''           "gate.oreTiers", "gate.halfFactor", "tool.tierPower", "lifelong.perkFortune.mining", "gate.oreFloor",
           "gate.nextByLadder"}          # 0.3.23: gathering speed''')
rep('''              ("LL_PFORTM", "double", "10.0"), ("ORE_FLOOR", "String", jstr(ORE_FLOOR_DEF))]''',
    '''              ("LL_PFORTM", "double", "10.0"), ("ORE_FLOOR", "String", jstr(ORE_FLOOR_DEF)),
              ("GATE_NBL", "boolean", "true")]          # 0.3.23''')
after('''  ORE_FLOOR = ptext(p, "gate.oreFloor", "@OREFLOOR@").trim();          // critic M1 (checked where it is used)
''', '''  GATE_NBL = pbool(p, "gate.nextByLadder", true);          // 0.3.23: every ladder pickaxe is a step of the ore gate
''')
after('''    L += ["", G322_HEAD]        # 0.3.22: the new rows (absent = the default; no one-time update)
    for k in G322_ROWK:
        scal(k)
''', '''    L += ["", G323_HEAD]        # 0.3.23: the new row (absent = the default) + the migrate0323 marker
    L += [H23_MARK]
    for k in G323_ROWK:
        scal(k)
''')
after('''assert [_dp.get(_k) for _k in G322_ROWK] == [ORE_TIERS_DEF, "0.5", TIER_POW_DEF, "10", ORE_FLOOR_DEF], [_dp.get(_k) for _k in G322_ROWK]
''', '''# 0.3.23: the fresh file holds the new defaults, the migrate0323 marker once, the new row
assert [_dp.get(_k) for _k in H23_KEYS] == H23_NEW and DEFAULT_TEXT.count(H23_MARK_ID) == 1 and _dp.get("gate.nextByLadder") == "true", [_dp.get(_k) for _k in H23_KEYS]
''')

# ================================================================================================================ 5: migrate0323 (the migrate0317 shape, text values)
rep('''F(gcf, "public static final String[] H7_NEW = %s;" % jarr(H7_NEW))
''', '''F(gcf, "public static final String[] H7_NEW = %s;" % jarr(H7_NEW))
F(gcf, "public static final String H23_MARK = %s;" % jstr(H23_MARK))          # 0.3.23 migrate0323
F(gcf, "public static final String H23_MARK_ID = %s;" % jstr(H23_MARK_ID))
F(gcf, "public static final String H23_WHO = %s;" % jstr(H23_WHO))
F(gcf, "public static final String[] H23_KEYS = %s;" % jarr(H23_KEYS))
F(gcf, "public static final String[] H23_OLD = %s;" % jarr(H23_OLD))
F(gcf, "public static final String[] H23_NEW = %s;" % jarr(H23_NEW))
''')
_h7u = method('''public static Object[] h7Update(String text) {''')
_h23u = _h7u.replace("h7Update", "h23Update").replace("H7_", "H23_").replace("h7Old(", "h23Old(")
for _a, _b in ((' + " kept (not the 0.3.16 default " + H23_OLD[i] + ", or not one plain line) - the new default would be " + H23_NEW[i]);',
                ' + " kept (not the 0.3.22 default, or not one plain line) - the new default is " + @PKG@.CfgRows.oneLine(H23_NEW[i]));'),
               ('chg.append(H23_KEYS[i]).append(\' \').append(ov.trim()).append(" -> ").append(H23_NEW[i]);',
                'chg.append(H23_KEYS[i]).append(" -> the 0.3.23 default");')):
    assert _h23u.count(_a) == 1, _a
    _h23u = _h23u.replace(_a, _b)
_mig17 = method('''public static synchronized String migrate0317() {''')
_mig23 = _mig17.replace("migrate0317", "migrate0323").replace("h7Update", "h23Update").replace("h7Log", "h23Log").replace("H7_WHO", "H23_WHO")
for _a, _b in (("skyy.harness.no317", "skyy.harness.no323"),
               ("NOT updated to the 0.3.17 defaults", "NOT updated to the 0.3.23 defaults"),
               ("before the 0.3.17 default update", "before the 0.3.23 default update"),
               ("config.properties updated to the 0.3.17 defaults: \" + chg + \" (Breaking Power 5 % a level, Fortune 2 a level, no tool Fortune cap; Undo in Server Setup's change log; the old file is kept in config-history)",
                "config.properties updated to the 0.3.23 defaults: \" + chg + \" (the 15-metal tool ladders, no ore speed floor; Undo in Server Setup's change log; the old file is kept in config-history)"),
               ("the 0.3.17 default update marker was added", "the 0.3.23 default update marker was added"),
               ("CONFIG 0.3.17 defaults: ", "CONFIG 0.3.23 defaults: "),
               ("could not update config.properties to the 0.3.17 defaults", "could not update config.properties to the 0.3.23 defaults")):
    assert _mig23.count(_a) == 1, _a
    _mig23 = _mig23.replace(_a, _b)
assert "0.3.17" not in _mig23 and "h7" not in _mig23 and "H7_" not in _mig23, _mig23
assert "0.3.16" not in _h23u and "h7" not in _h23u and "H7_" not in _h23u, _h23u
_h7l = method('''public static String h7Log(String k, String o, String n) {''')
_h23l = _h7l.replace("h7Log", "h23Log").replace("H7_WHO", "H23_WHO")
MIG = ('''# ---- 0.3.23 ONE-TIME UPDATE migrate0323 (PROJECT-RULES section 4; tools/gear_0_3_23_patch.py item 5; the migrate0317 machinery with TEXT values).
# Pure text step: null = the marker is already in a comment line (a fresh 0.3.23 file carries it). Else { new text, changes, notes, log rows }.
# Per key of H23_KEYS: every ONE-LINE entry holding exactly the 0.3.22 default (trimmed text) is rewritten when the LAST entry holds it.
M(gcf, r"""
public static boolean h23Old(String v, String old) { return v != null && old != null && v.trim().equals(old); }""")
M(gcf, r"""
''' + _h23u + '''
M(gcf, r"""
''' + _h23l + '''
M(gcf, r"""
''' + _mig23 + '''
''')
before('''# 0.2.1 ready line part: the base stats in force (live values)''', MIG)
rep('''  @PKG@.GearCfg.migrate0322();          // 0.3.22: the new metals' level bands (a pure addition of the missing rows)
''', '''  @PKG@.GearCfg.migrate0322();          // 0.3.22: the new metals' level bands (a pure addition of the missing rows)
  @PKG@.GearCfg.migrate0323();          // 0.3.23: the 15-step tool ladders + no ore floor (only the untouched 0.3.22 defaults)
''')

# ================================================================================================================ 6: GearLL / GearDefs / texts / replacements
after('''F(gll, "public static final int[] PICK_T = %s;" % jints(PICK_T))          # the pickaxe steps that exist (G2 adds its own)
''', '''F(gll, "public static final int[] PICK_TV = %s;" % jints(G23_PICK_TV))          # 0.3.23: the vanilla pickaxe steps (gate.nextByLadder off)
F(gll, "public static final String[] NEW_W = %s;" % jarr(G23_METALS))          # 0.3.23: the tool metals with no vanilla tool (their own word in texts)
''')
rep('''public static int nextPick(int t) {
  for (int i = 0; i < PICK_T.length; i++) if (PICK_T[i] > t) return PICK_T[i];
  return 999;
}""")''', '''public static int nextPick(int t) {
  int[] a = @PKG@.GearCfg.GATE_NBL ? PICK_T : PICK_TV;          // 0.3.23: every ladder pickaxe is a step (gate.nextByLadder)
  for (int i = 0; i < a.length; i++) if (a[i] > t) return a[i];
  return 999;
}""")''')
after('''M(gll, "public static String tname(int t) { return t >= 0 && t < TNAME.length ? TNAME[t] : String.valueOf(t); }")
''', '''# 0.3.23: the word a text / a SkyyCollections tier-up token names for a tool id - its own metal word for the metals with no vanilla tool
# (Tool_Pickaxe_Lead_SkyWynn -> "Lead"; its internal tier would say "Cobalt"), else the internal tier's name (unchanged)
M(gll, r"""
public static String tnm(String id) {
  if (id != null) {
    String[] w = id.split("_");
    for (int i = 2; i < w.length; i++) {
      for (int j = 0; j < NEW_W.length; j++) if (NEW_W[j].equalsIgnoreCase(w[i])) return NEW_W[j];
    }
  }
  return tname(tier(id));
}""")
# 0.3.23: the ladder ORDER of a tool id = its ladder T (tools/tier_tags.py TOOL_METALS) x 10 + its internal tier - two steps may share an internal
# tier now (Lead / Dusk / Cobalt), the rank never does (Crude 10, Copper 11, Iron 22, Bronze 33, Thorium 43, Lead 54, Dusk 64, Cobalt 74 ...)
M(gll, r"""
public static int lrank(String id) {
  if (id == null) return 0;
  String[] w = id.split("_");
  int lt = 0;
  for (int i = 2; i < w.length && lt == 0; i++) {
    for (int j = 0; j < LT_W.length && lt == 0; j++) if (LT_W[j].equalsIgnoreCase(w[i])) lt = LT_N[j];
  }
  return lt * 10 + tier(id);
}""")
''')
rep('''  if (had != null && kOf(had) == k && tier(had) > tier(r)) return had;''',
    '''  if (had != null && kOf(had) == k && lrank(had) > lrank(r)) return had;          // 0.3.23: the ladder rank (Dusk above Lead, same internal tier)''')
rep('''  int t = tier(id);
  // 0.3.2: an exact copy carries the reforge count it was copied with (lrpF) - only a reforge AFTER the copy counts''',
    '''  int t = tier(id);
  int l0 = @PKG@.GearData.num(d, "lrpL", -1);          // 0.3.23: the ladder rank it was given at (a Lead -> Dusk tier-up shares the internal tier)
  if (l0 >= 0 && lrank(id) > l0) return true;
  // 0.3.2: an exact copy carries the reforge count it was copied with (lrpF) - only a reforge AFTER the copy counts''')
rep('''  if (rp) { nd.put("lrp", new org.bson.BsonInt32(1)); nd.put("lrpT", new org.bson.BsonInt32(@PKG@.GearLL.tier(id))); }''',
    '''  if (rp) { nd.put("lrp", new org.bson.BsonInt32(1)); nd.put("lrpT", new org.bson.BsonInt32(@PKG@.GearLL.tier(id))); nd.put("lrpL", new org.bson.BsonInt32(@PKG@.GearLL.lrank(id))); }          // 0.3.23: + lrpL''')
_nrm = s.count('.remove("lrpT");')
_n_nd = s.count('nd.remove("lrpT");')
_n_rd = s.count('rd.remove("lrpT");')
_n_d = s.count(' d.remove("lrpT");')
assert _n_nd + _n_rd + _n_d == _nrm and _nrm >= 7, (_n_nd, _n_rd, _n_d, _nrm)
rep('nd.remove("lrpT");', 'nd.remove("lrpT"); nd.remove("lrpL");', _n_nd)
rep('rd.remove("lrpT");', 'rd.remove("lrpT"); rd.remove("lrpL");', _n_rd)
rep(' d.remove("lrpT");', ' d.remove("lrpT"); d.remove("lrpL");', _n_d)
rep('''    r = f.apply(new Object[] { @PKG@.Gear.pkey(u), ck + ":" + tname(tier(to)) });''',
    '''    r = f.apply(new Object[] { @PKG@.Gear.pkey(u), ck + ":" + tnm(to) });          // 0.3.23: the metal word (pickaxe:Lead)''')
_ntx = s.count("@PKG@.GearLL.tname(@PKG@.GearLL.tier(id))")
assert _ntx >= 3, _ntx
rep("@PKG@.GearLL.tname(@PKG@.GearLL.tier(id))", "@PKG@.GearLL.tnm(id)", _ntx)
rep("@PKG@.GearLL.tname(@PKG@.GearLL.tier(to))", "@PKG@.GearLL.tnm(to)", s.count("@PKG@.GearLL.tname(@PKG@.GearLL.tier(to))"))
# the multitool ids of ours (GearData.multiId: two stat sets, GearTool fam 6)
after('''F(gdf, "public static final String[] MULTI_T = %s;" % jarr(MULTI_TIERS))
''', '''F(gdf, "public static final String[] MULTI_OWN = %s;" % jarr([_g + "_SkyWynn" for _g in G23_METALS]))          # 0.3.23: our multitools (SkyyGear items)
''')
rep('''  for (int i = 0; i < @PKG@.GearDefs.MULTI_T.length; i++) if (@PKG@.GearDefs.MULTI_T[i].equals(t)) return true;
  return false;''', '''  for (int i = 0; i < @PKG@.GearDefs.MULTI_T.length; i++) if (@PKG@.GearDefs.MULTI_T[i].equals(t)) return true;
  for (int i = 0; i < @PKG@.GearDefs.MULTI_OWN.length; i++) if (@PKG@.GearDefs.MULTI_OWN[i].equals(t)) return true;          // 0.3.23
  return false;''')

# ================================================================================================================ 6b: the jar check
rep('''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS) + list(GA2_ITEMS) + list(CAN_ITEMS) + list(HARV_ITEMS) + list(ZM_ITEMS)), "SkyyGear 0.3.21 ships the 32 zone mining pieces + the 8 mystery bags + the 16 Untiered copies + the 5 Sigils + the 68 gathering armor pieces + 6 watering cans + 4 Harvesters"
''', '''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS) + list(GA2_ITEMS) + list(CAN_ITEMS) + list(HARV_ITEMS) + list(ZM_ITEMS) + list(G23_ITEMJ)), "SkyyGear 0.3.23 ships the 49 metal tools + the 32 zone mining pieces + the 8 mystery bags + the 16 Untiered copies + the 5 Sigils + the 68 gathering armor pieces + 6 watering cans + 4 Harvesters"
    for _k, _v in list(G23_ITEMJ.items()) + list(G23_FILES.items()):          # 0.3.23
        assert _jz.read(_k) == (_v.encode("utf-8") if isinstance(_v, str) else _v), "metal tool file missing from the jar: " + _k
    _lang23 = _jz.read("Server/Languages/en-US/server.lang").decode("utf-8")
    assert all(("\\n" + _x + "\\n") in _lang23 for _x in G23_LANG) and len(G23_LANG) == 98, "0.3.23: the metal tool names / tagged descriptions in server.lang"
''')

# ================================================================================================================ 6c: extra scope (A1's Armory weapons)
rep('''OWN_TRUST = ["Weapon_Crossbow_Copper_Wynn", "Weapon_Crossbow_Onyxium_Wynn"]
OWN_SRC_JAR = "SkyyArmory-0.1.3.jar"''', '''OWN_TRUST = ["Weapon_Crossbow_Copper_Wynn", "Weapon_Crossbow_Onyxium_Wynn"]
# 0.3.23 (round A1 = SkyyArmory 0.1.33): + the Thorium / Cobalt / Adamantite / Mithril gap crossbows and the 8 new-metal crossbows - the same
# vanilla Iron crossbow template (Parent Template_Weapon_Crossbow, no own Interactions); read from the 0.1.33 jar (else reproduced)
OWN_TRUST += (["Weapon_Crossbow_%s_Wynn" % _m for _m in ("Thorium", "Cobalt", "Adamantite", "Mithril")]
              + ["Weapon_Crossbow_%s_SkyWynn" % _m for _m in ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")])
assert len(OWN_TRUST) == 14
OWN_SRC_JAR = "SkyyArmory-0.1.33.jar"          # 0.3.23: the first jar with all 14 (0.1.3 had the 2)''')
# GearUp: a step whose recipe takes an EARLIER rung of the same ladder (the soul cages' two "next" recipes)
before('''# the cost of from -> to read from the LIVE CraftingRecipe store (cached until the store's size changes); null = no recipe makes it''', """# 0.3.23 (round A1 extra scope): SkyyArmory 0.1.33 makes the Lead cage from the Thorium cage AND the Cobalt cage from the Thorium cage - two "next"
# recipes. The 15-step Soul Cage ladder (Thorium > Lead > Dusk > Cobalt ...) pays a step with no recipe from its own "from" through the recipe of
# "to" that takes an EARLIER rung of the same ladder (Dusk > Cobalt = the Cobalt cage recipe, the Dusk cage in the Thorium cage's place - a better
# item paid in, never a cheaper path). earlier(x, from): x is a rung below from on the live ladder table (walked back, at most 64 steps)
M(gup, r'''
public static boolean earlier(String x, String from) {
  if (x == null || from == null || x.equals(from)) return false;
  Object[] tb = tab();
  String[] f = (String[]) tb[0];
  String[] t = (String[]) tb[1];
  String cur = from;
  for (int n = 0; n < 64 && cur != null; n++) {
    String prev = null;
    for (int i = 0; i < t.length && prev == null; i++) if (t[i].equals(cur)) prev = f[i];
    if (prev == null) return false;
    if (prev.equals(x)) return true;
    cur = prev;
  }
  return false;
}''')
M(gup, r'''
public static Object[] fromRecipeAlt(@CRR@ rc, String from, String to) {
  if (rc == null) return null;
  @MQ@ po = rc.getPrimaryOutput();
  if (po == null || !to.equals(po.getItemId()) || po.getQuantity() != 1) return null;
  @MQ@[] in = rc.getInput();
  if (in == null) return null;
  String x = null;
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null) continue;
    String iid = in[i].getItemId();
    if (iid == null || iid.equals(from)) return null;
    if (in[i].getQuantity() == 1 && earlier(iid, from)) {
      if (x != null) return null;
      x = iid;
    }
  }
  if (x == null) return null;
  return fromRecipe(rc, x, to);
}''')
""")
rep('''  COST.put(k, best == null ? (Object) Boolean.FALSE : (Object) best);''', '''  if (best == null) {          // 0.3.23: no recipe takes "from" itself - one that takes an EARLIER rung of its ladder (fromRecipeAlt)
    try {
      java.util.Iterator it2 = new java.util.ArrayList(m.values()).iterator();
      while (it2.hasNext()) {
        Object o2 = it2.next();
        if (!(o2 instanceof @CRR@)) continue;
        Object[] r2 = fromRecipeAlt((@CRR@) o2, from, to);
        if (r2 == null) continue;
        String rid2 = (String) r2[2];
        if (best == null || (rid2 != null && (bid == null || rid2.compareTo(bid) < 0))) { best = r2; bid = rid2; }
      }
    } catch (Throwable t2) { @PKG@.Gear.warnOnce("upcost2", "could not read the crafting recipes for the upgrade costs: " + t2); return null; }
  }
  COST.put(k, best == null ? (Object) Boolean.FALSE : (Object) best);''')

rep('''                "Weapon_Crossbow_": (8, 8), "Weapon_Staff_": (26, 24), "Weapon_Wand_": (5, 3), "Weapon_Spellbook_": (6, 5),''',
    '''                "Weapon_Crossbow_": (8 + 12, 8 + 12), "Weapon_Staff_": (26, 24), "Weapon_Wand_": (5, 3), "Weapon_Spellbook_": (6, 5),          # 0.3.23: Crossbow + the 12 own (OWN_TRUST)''')
# ================================================================================================================ 6d: critic M1 / M2
after('''F(gll, "public static final String[] TW = %s;" % jarr([_w for _w, _t in TOOL_TIERS_ALL]))          # 0.3.23: + the zone words (G23_ZT)
''', '''F(gll, "public static final int TW0 = %d;" % len(TOOL_TIERS))          # 0.3.23 critic M1: TW[TW0..] (the zone words) count only in our _SkyWynn ids
''')
rep('''    for (int j = 0; j < TW.length; j++) if (TW[j].equalsIgnoreCase(w[i])) return TN[j];''',
    '''    for (int j = 0; j < TW.length; j++) if (TW[j].equalsIgnoreCase(w[i]) && (j < TW0 || id.endsWith("_SkyWynn"))) return TN[j];          // 0.3.23 critic M1''')
after('''F(gtool, "public static final String[] TIER_W = %s;" % jarr([w for w, _t in TOOL_TIERS_ALL]))          # 0.3.23: + the zone words (G23_ZT)
''', '''F(gtool, "public static final int TW0 = %d;" % len(TOOL_TIERS))          # 0.3.23 critic M1: the zone words count only in our _SkyWynn ids
''')
rep('''    for (int j = 0; j < TIER_W.length; j++) if (TIER_W[j].equalsIgnoreCase(w[i])) return TIER_N[j];''',
    '''    for (int j = 0; j < TIER_W.length; j++) if (TIER_W[j].equalsIgnoreCase(w[i]) && (j < TW0 || id.endsWith("_SkyWynn"))) return TIER_N[j];          // 0.3.23 critic M1''')
rep('''public static String tnm(String id) {
  if (id != null) {''', '''public static String tnm(String id) {
  if (id != null && id.endsWith("_SkyWynn")) {          // critic M1: our ids only''')
rep('''  int m = 0;
  String[] a = l.split(",");
  for (int i = 0; i < a.length; i++) { int t = tier(a[i].trim()); if (t > m) m = t; }
  return m;
}""")''', '''  String[] a = l.split(",");
  return tier(a[a.length - 1].trim());          // 0.3.23 critic M2: the tier of the ladder's LAST id (Lumen), never the highest of any step
}""")
# 0.3.23 critic M2: the uncapped line = the ladder's last id, or a tool at / above its kind's 0.3.22 top (OLDTOP) - no player loses effective levels
M(gll, r"""
public static boolean isTop(int k, String id) {
  if (id == null) return false;
  String l = ladOf(k, id);
  if (l == null || l.length() == 0) l = k >= 0 && k < KLAD.length ? KLAD[k] : "";
  String[] a = l.split(",");
  if (a.length > 0 && id.equals(a[a.length - 1].trim())) return true;
  int ot = (k == 3 && harv(id)) ? OLDTOP_HARV : (k >= 0 && k < OLDTOP.length ? OLDTOP[k] : 99);
  return tier(id) >= ot;
}""")''')
rep('''  if (id != null && t >= topTier(k, id)) return LINE_BIG;''',
    '''  if (id != null && isTop(k, id)) return LINE_BIG;          // 0.3.23 critic M2: the last step, or at / above the 0.3.22 top''')

# ================================================================================================================ 7: manifest
rep('''15-STEP METAL LADDER: tier tags T1 Copper .. T15 Lumen (Onyxium T16)''',
    '''METAL TOOLS: pickaxe, hatchet, multitool, Harvester and watering can in every metal of the 15-step ladder (Bronze .. Lumen), tier-ups Crude .. Lumen. 15-STEP METAL LADDER: tier tags T1 Copper .. T15 Lumen (Onyxium T16)''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i("G23_ZT = [") < _i("G23_METALS = [") < _i("G23_LADROW = {") < _i("CAN_LAD_OLD, HARV_LAD_OLD") < _i("G22_ORE = [") < _i("G23_PICK_TV, G23_PICK_IDV") < _i("CFG_ROWS = [")
assert _i('M(gll, "public static String tname(int t)') < _i("public static String tnm(String id) {") < _i("public static int lrank(String id) {") < _i("public static String tierFor(java.util.UUID u, int k, String had) {")
assert _i("public static int lrank(String id) {") < _i("public static boolean invested(String id, @BD@ d) {")
assert _i('F(gll, "public static final String[] LT_W') < _i('F(gll, "public static final String[] NEW_W') < _i("public static String tnm(String id) {")
assert _i("public static boolean h23Old(") < _i("public static Object[] h23Update(String text) {") < _i("public static String h23Log(") < _i("public static synchronized String migrate0323()") < _i("@PKG@.GearCfg.migrate0323();")
assert _i("@PKG@.GearCfg.migrate0322();") < _i("@PKG@.GearCfg.migrate0323();")
assert _i('F(gdf, "public static final String[] MULTI_OWN') < _i("public static boolean multiId(String id) {")
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
assert s.count(' = mk("') == MK0, "no new class"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.22 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.22 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
