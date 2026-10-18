"""Derive SkyyGear/build_skyygear_0.3.19.py from the LIVE 0.3.18 (build_skyygear_0.3.18.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_18_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_19_patch.py      then      python SkyyGear/build_skyygear_0.3.19.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.19.py   (--static runs without jars / Assets.zip)
Spec: research/Pack-Drops-Spec.md. The table: tools/pack_drops.py (read by the build - a table change needs no new patch).

0.3.19 (2026-10-17) = PACK DROPS (cloud build trial - built by the Grok-bot trial session, NOT deployed; the local session rebuilds it against
the real install). Skyy 2026-10-17 (docs/answered/gear.md): "lets build the arcane robes and armory into the mod so you drop from enemy's
with our modifiers next" + "and the weapons too" + "fewer at lower tiers on the normal drops keep 2 ut but do 1 mythic. and UT and mythic
can reuse looks BUT enhanced (if we can.) ... save the coolest armor and weapons for mythic" + "UT and mythic per zone! not tier. always make
the UT and mythic the highest tier of that zone" + "all combat gear is still drops only. and all Ut and mythic are combat gear". Older locks
kept: docs/answered/gear.md LOCKED 2026-10-08 popup batch 2 ("pool The Armory + ..., keep their crafting, no paid access, drops picked by set,
random colour, crowns / amulets = Cloth, multiplicative pieces special sets only, Lahat Chereb Berserker"; "Mythic boss-only (out of random
drops + Smithing step-up), 10% per kill (20% Challenge) per participant with 15% credit + own-class lean x3").
LICENCE: SkyyGear only REACTS to The Armory's item ids (LadyPaladra, CC BY-NC 3.0: credit, never sold) at runtime - the id table, our own
drop roll, our own modifiers. Nothing of theirs is copied, shipped, recoloured or overridden; a missing id (mod off / renamed) is skipped.
  1. THE PACK TABLE (tools/pack_drops.py -> class GearPackId, ids as one packed string): 1,067 Armory ids in 49 sets (ROLE drop 29, ut 5,
     mythic 15; Academy OFF since the critic round - item 10), each with its set, kind (armor / a weapon bag type), weight (Heavy / Light / Cloth), tier (a level.material row word) and
     zone (Crude / Copper / Iron 1, Thorium 2, Cobalt 3, Adamantite 4, Mithril 5). Void Armor rows wait for their ids, every other mod for
     its author's OK - none of their ids is in the jar.
  2. PACK IDS ARE GEAR (part.packDrops, default ON): GearData.isGear / isGearMs = true for a table id (not stacking), kind combat
     (a kind.prefix row still wins), its level band = its table tier's level.material row (GearLevel.level / entry; a level.item row still
     wins; never their ItemLevel), its armor type = the table weight (bags + Smithing's armorType - their sound set is not used: The Armory
     gives robes Heavy sounds). So crafted Armory pieces roll like our gear, worn ones get SkyyGear's levelled stats + modifiers, their
     unidentified mob / chest drops become bags. Off = exactly 0.3.18 (the ids are plain items again; documents stay on the stacks).
  3. NORMAL DROPS (role drop): the pack ids join the mystery-bag pool (GearPool rows after the vanilla ones) at their band. The bag's slot
     is the LIVE item's ArmorSlot (never guessed); a weapon's bag type comes from the table, only while the live item IS a weapon
     (Item.getWeapon; anything else = never a candidate). PICKED BY SET (Pack-Armor-Plan 2.3 / the 10-08
     lock): one pack set weighs loot.packWeight (1 = one vanilla item) in a bag of that slot, split over its live pieces of that slot, so 179
     Calvary colourways do not drown everything else. Random colour = any colourway of the set (10-08 default).
  4. UT CANDIDATES (role ut: Ghost Rook, Ghost Calvary, Battlegrounds, Ghost Sword, Hepta Axe - none has a recipe in 1.23.0) never drop as normal gear; each
     becomes a real Untiered item the moment its ut.<id> + utfx.<id> rows exist (the existing Untiered table: fixed lines + one trade-off are
     Skyy's call; an id any loaded recipe makes is refused there).
  5. MYTHIC BOSS BAGS (role mythic; SkyyMobs 0.1.10 mob:fn:boss): when a BOSS role dies (SkyyMobs' bosses.roles), every player SkyyMobs
     credited with >= loot.boss.credit % (15) of its damage who is in the same world and not in Creative rolls loot.boss.mythic % (10) for
     one Mythic mystery bag of the boss's ZONE (the killer rolls only when SkyyMobs credited nobody at all; credited players all under the
     bar = nobody; no head-count cap): armor loot.boss.armorShare % (50) - Heavy / Light / Cloth evenly among the weights with a Mythic
     piece in that zone, then a slot of that weight (Q13) - else a weapon type with a Mythic set in that zone, own-class types x
     loot.boss.classLean (3). A won bag counts against the hourly extra-bag cap (loot.mob.capPerHour). The bag (Skyy_Unid_Bag_Mythic, new
     field pz = the zone) goes INTO the winner's inventory (world task GearPackGive: storage, hotbar, backpack; full = at their feet; gone
     or in another world by then = at the boss) - never a ground drop at the boss, which SkyySacks' auto-pickup would hand to the top damager. It identifies into one of
     that zone's Mythic pieces at their band (re-identify keeps the zone); no Mythic piece of its zone left (their mod off / renamed) = the
     bag stays and says so (never a normal-pool item). Once per death. No SkyyMobs 0.1.10 = no boss bags (nothing else changes). Challenge
     mode (20 %) does not exist yet - not built.
  6. SWAP GUARD: a recipe that turns a gear piece into a pack piece (The Armory's Alteration Table colour swap, Elite Rook from a Rook piece)
     is REFUSED while the player holds a rolled piece (rarity above Normal) of its gear input (it would erase the roll); with Normal pieces
     it runs and its output gets no fresh roll and no Smithing XP (no free re-roll / XP loop by swapping colours) - stamped Normal like any
     found item. Crafting pack pieces pays no Smithing XP at all (their recipes are their economy). gear.exclude applies to pack ids too.
     Local rebuild (2026-10-17, bytecode of TheArmoryMod-1.23.0 AlterationTransaction.processFromInventory): the Alteration Table fires
     CraftRecipeEvent$Pre (honours setCancelled) + $Post on the player and builds the new colour as new ItemStack(out, qty, durability,
     the input's WHOLE metadata - EXCLUDED_METADATA_KEYS is empty) + withQuality(the input's) - so a rolled piece keeps its roll there.
     The veto therefore skips recipes on The Armory's "ArmoryAlteration" bench (GearPackId.alter); it still guards every other pack
     recipe that eats a gear piece (Elite Rook from Rook at a normal bench, where the engine makes a fresh stack).
  7. TIER TAG: a pack item's tooltip flavour line starts with its tier tag ("T3 Iron - ...", tools/tier_tags.py numbering) - only in our
     per-stack tooltip; their lang keys are never written.
  8. /gear loot (existing admin command) adds the pack lines: live sets / ids, missing ids, Mythic sets per zone, boss rolls / bags.
  10. CRITIC FIXES (local rebuild 2026-10-17). Skyy's popup answer, word for word: Q "...almost every Armory set we planned as MYTHIC
     (boss-only) or UT can also be CRAFTED at The Armory's own benches ... and The Armory's own chest loot drops some of them too..." ->
     "Block craft, chest = plain (Recommended)".
     a) CraftRecipeEvent$Pre (bench crafting AND SkyySacks /craft, which fires the same Pre) refuses a recipe whose output is a UT /
        Mythic table row (chat line + CRAFT-BLOCK-PACK in gear.log; Creative still crafts). Only an Alteration Table colour swap inside
        the SAME set passes (GearPackId.sameSet: it makes nothing new and keeps the piece's own document). Such a piece their chests /
        mobs drop is a plain Normal piece (GearRoll.unidDoc / GearUnid.fromItem / GearTag.spread): real Mythic rolls only come from
        boss bags. ACADEMY: all 27 of its pieces have a recipe, so it is OFF in tools/pack_drops.py (no longer a UT candidate; no
        recipe-free Armory Cloth set exists to replace it - FOR SKYY: Zone 4 Cloth UT stays empty until you pick one).
     b) gear:fn:roll mode 8 (SkyySacks /craft): no Smithing XP for pack pieces; a swap recipe (a[4] = the recipe id) or a UT / Mythic
        row = a plain Normal piece; gear:fn:classShow answers false for a UT / Mythic row. Found: SkyySacks 0.8.20 lists Armor_Bench
        and Weapon_Bench recipes (the bench accessories), so The Armory's base pieces + upgrades show in /craft; it never lists the
        ArmoryAlteration bench (no accessory). Their ids have no Armor_ / Weapon_ prefix, so /craft puts them on the CRAFTING tab,
        where classShow is not asked (Smithing tab only) - the Pre refusal is what blocks them there (the row still shows).
     c) The swap guard reads ResourceTypeId inputs too (GearPackId.resSets / carries: a resource a live table item carries = gear;
        the veto checks rolled pieces carrying it).
     d) A boss family (role up to "_Phase") rolls once per credited player per 120 s (GearPack.FIGHT; BN[6] = "same fight"):
        Assets.zip 0.7 has separate phase roles (Goblin_Duke + Phase_2 / Phase_3_*, Skeleton_Elite + Phase_2 in the encounter group
        Skeleton_Elite_Encounter_Target) and no in-data role switch was found, so phases may be separate deaths.
     e) Mythic boss bags are NOT under the hourly extra-bag cap any more (d limits them).
     f) GearData.isGear's pack answer cached per row (GearPackId.GC, cleared on GearCfg.EPOCH); GearPool.table rebuilt on the config
        epoch or the item count only; GearPackGive counts the bag before / after a write that throws (nothing landed = the next
        container / the feet). SkyyMobs: DEAD evicts the oldest entry, never clears all.
     g) Build-time coin-loop guard: when TheArmoryMod-*.jar is in the Mods folder, no table id may carry a top-level Value / Price /
        Sell / Coin / Worth field (tools/pack_drops.py coin_keys, read-only).
     h) SALVAGE (Skyy's popup, word for word: Q "...The Armory's own Salvagebench gives back 100% of the materials from its pieces ... Block
        salvaging rolled (dropped / identified) pieces at their bench?" -> "Yes, Requip only (Recommended)"): CraftRecipeEvent$Pre refuses a
        Salvagebench recipe while the player holds a pack piece of its input whose document is not a craft one (GearPack.salvVeto /
        salvBlocked: src drop / chest / boss / legacy ...), pointing to Requip SALVAGE; crafted pieces still salvage. This catches SkyySacks
        /craft (it lists Salvagebench recipes as an instant bench and fires the same Pre). NOT caught: the Salvagebench BLOCK itself - it is
        a Processing bench (ProcessingBenchBlock.tryCompleteOneRecipe -> ItemContainer.removeMaterials in BenchSystems$ProcessingBenchTick,
        VERIFIED bytecode 0.7): only CraftingManager.craftItem / queueCraft fire CraftRecipeEvent$Pre. Proposed hook (next round): a
        ChunkStore ticking system ordered BEFORE BenchSystems$ProcessingBenchTick that, on a Salvagebench, moves a pack stack carrying a
        non-craft document out of ProcessingBenchBlock.getInputContainer() into its output container (counted before / after, never lost),
        plus a chat line to the player who has its ProcessingBenchWindow open.
  9. VOID CHARMS WORDING (folded in by the local rebuild; Skyy 2026-10-17: "i noticed they are still called accessory's in the settings";
     model tools/accessories_0_5_24_patch.py): player-visible "Accessory Bag" meaning the charm feature -> "Void Charms" - the bench-rule
     line ("... accessory in your Void Charms - or craft it at a ..."), the Identify / Appraisal Tool lines ("... accessory in your Void
     Charms.", "(Void Charms)", "Void Charms is not loaded"). Unchanged on purpose: ids, config keys, "Accessory Power", single items
     "accessory", the retired item Skyy_Accessory_Bag (SkyyAccessories names it "Old Accessory Bag"; SkyyGear writes no name for it), code
     comments.
Commands: none new. Server Setup -> Gear -> Loot: part.packDrops, loot.packWeight, loot.boss.mythic, loot.boss.credit, loot.boss.classLean,
loot.boss.armorShare (new keys: a missing line = its default, no one-time update). Classes: + GearPackId, GearPack, GearPackGive. SAVED DATA: a Mythic boss bag carries "pz" (int) in its
SkyyUnid document and in the identified item's box sub-document; nothing else is new (pack items carry the normal SkyyGear document).
ROLLBACK 0.3.19 -> 0.3.18: safe for saved data - 0.3.18 ignores "pz" (a Mythic boss bag then identifies from the normal pool, still Mythic);
the critic review's fixes (H2 delivery, M1-M5, L2) are folded into items 5 and 6 above; the fix round's (winner changed worlds = the boss
fallback, Mythic armor weight evenly, weapon rows need a live weapon, no cap of 8 boss rollers) into items 3 and 5;
pack items keep their documents but 0.3.18 treats them as plain items again (their SkyyGear stats / tooltip go until 0.3.19+ is back).
Set part.packDrops=false first to see that state without a rollback. Pairs with SkyyMobs 0.1.10 (boss bags only; either can roll back alone).
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.18.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.19.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.18"' in s and "GENERATED by tools/gear_0_3_18_patch.py" in s, "not the generated 0.3.18 script"
assert "GearPackId" not in s and "mob:fn:boss" not in s and "part.packDrops" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
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


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.18":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.18" % _set.get("SkyyGear"))

sys.path.insert(0, os.path.join(ROOT, "tools"))
import pack_drops as _PKD
assert not _PKD.check(), "tools/pack_drops.py: %s" % _PKD.check()

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.19 (2026-10-17)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.18 - build script (javassist via jpype). GENERATED by tools/gear_0_3_18_patch.py from the LIVE 0.3.17 (itself GENERATED by
tools/gear_0_3_17_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.18.py -> SkyyGear/SkyyGear-0.3.18.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.18.py

''', '''"""SkyyGear 0.3.19 - build script (javassist via jpype). GENERATED by tools/gear_0_3_19_patch.py from the LIVE 0.3.18 (itself GENERATED by
tools/gear_0_3_18_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.19.py -> SkyyGear/SkyyGear-0.3.19.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.19.py

''' + NOTE + '''
--- 0.3.18 notes ---
''')
rep('VERSION = "0.3.18"\n', 'VERSION = "0.3.19"\n')

# ================================================================================================================ Python: the pack rows
after('''LOOT_TNAME = [_TNAME.get(_k, _k.split("_", 1)[1]) for _k in LOOT_TYPES]
''', '''
# ================================================================= 0.3.19 PACK DROPS (tools/gear_0_3_19_patch.py; the table: tools/pack_drops.py)
# ids only (no file of another mod is read): every active row = (id, set, kind, armor type 0-3, tier word, zone 1-5, role 0 drop / 1 ut / 2 mythic)
import pack_drops as PKD
assert not PKD.check(), "tools/pack_drops.py: %s" % PKD.check()
PACK_SETS = PKD.active_sets()
PACK_ROWS = PKD.rows()
assert PACK_ROWS and len(set(_r[0] for _r in PACK_ROWS)) == len(PACK_ROWS), "a pack id twice"
assert not [_r[0] for _r in PACK_ROWS if _r[0] in AZ_ITEMS], "a pack id is a vanilla item id: %s" % [_r[0] for _r in PACK_ROWS if _r[0] in AZ_ITEMS][:5]
assert not [_r for _r in PACK_ROWS if _r[2] != "armor" and _r[2] not in LOOT_TYPES], "a pack weapon kind is no bag type: %s" % sorted(set(_r[2] for _r in PACK_ROWS if _r[2] != "armor" and _r[2] not in LOOT_TYPES))
_MATW = set(_t.lower() for _t, _l in MATERIALS)
assert set(_r[4] for _r in PACK_ROWS) <= _MATW, "a pack tier has no level.material row: %s" % (set(_r[4] for _r in PACK_ROWS) - _MATW)
assert all(_r[0] for _r in PACK_ROWS) and all("," not in _r[0] and ";" not in _r[0] for _r in PACK_ROWS)
PACK_TAGS = [PKD.tag_of(_s["tier"]) for _s in PACK_SETS]
# critic fix 7 (coin-loop guard): when The Armory is installed, none of the table ids may carry a price field (read-only check of their jar)
import glob as _glob
_ARMJ = sorted(_glob.glob(os.path.join(B.HYTALE, "UserData", "Mods", "TheArmoryMod-*.jar")))
if _ARMJ:
    _CK = PKD.coin_keys(_ARMJ[-1])
    assert not _CK, "a pack id carries a price field - check our Bazaar / Coins listings first: %s" % _CK[:5]
    print("0.3.19 pack coin guard: %s - no table id carries a Value / Price / Sell / Coin / Worth field" % os.path.basename(_ARMJ[-1]))
else:
    print("0.3.19 pack coin guard: The Armory is not in the Mods folder - skipped")
# GearPool rows after the vanilla ones: weapons carry their bag type, armor -1 (the LIVE ArmorSlot decides at run time)
PACK_POOL = [(_r[0], (LOOT_TYPES.index(_r[2]) if _r[2] != "armor" else -1), _r[3], _r[5], _r[6], _r[1]) for _r in PACK_ROWS]
print("0.3.19 pack drops: %d ids in %d sets (%s) - drop %d, ut %d, mythic %d sets; zones %s"
      % (len(PACK_ROWS), len(PACK_SETS), ", ".join(sorted(set(PKD.SOURCES[_s["src"]]["mod"] for _s in PACK_SETS))),
         sum(1 for _s in PACK_SETS if _s["role"] == "drop"), sum(1 for _s in PACK_SETS if _s["role"] == "ut"),
         sum(1 for _s in PACK_SETS if _s["role"] == "mythic"), sorted(set(_r[5] for _r in PACK_ROWS))))
''')

# ================================================================================================================ Server Setup rows + GearCfg
after('''    ("loot.levelShift", "Mob level rarity boost", "loot", "dec", "0.02", "0", "1", "", "", "live,danger",
     "Mob bags: rarities above Normal weigh x(1 + this x (level - 1))." + PH, "field:GearCfg.LEVEL_SHIFT"),
''', '''    # 0.3.19 PACK DROPS (tools/gear_0_3_19_patch.py; research/Pack-Drops-Spec.md). New keys: a missing line means its default (no one-time update)
    ("part.packDrops", "Pack armor + weapons drop", "loot", "bool", "true", "", "", "", "", "live,part,danger",
     "The Armory's armor and weapons are gear and drop from mobs and bosses. Off = plain items again.", "field:GearCfg.PACK_ON"),
    ("loot.packWeight", "Pack set weight in bags", "loot", "dec", "1", "0", "100", "", "x", "live",
     "One pack set weighs this in a bag (1 = one vanilla item)." + PH, "field:GearCfg.PACK_W"),
    ("loot.boss.mythic", "Boss Mythic bag chance", "loot", "dec", "10", "0", "100", "", "%", "live,danger",
     "Per boss kill, each credited player rolls this for a Mythic bag of the boss's zone. 0 = off.", "field:GearCfg.BOSS_MY"),
    ("loot.boss.credit", "Boss credit needed", "loot", "int", "15", "0", "100", "", "%", "live",
     "A player needs this share of the boss's damage to roll (nobody = the killer rolls).", "field:GearCfg.BOSS_CREDIT"),
    ("loot.boss.classLean", "Boss bags: own-class weapon weight", "loot", "int", "3", "1", "10", "", "", "live",
     "Mythic weapon bags: the player's class weapon types count this many times.", "field:GearCfg.BOSS_LEAN"),
    ("loot.boss.armorShare", "Boss bags: armor share", "loot", "int", "50", "0", "100", "", "%", "live",
     "Share of Mythic boss bags that hold armor; the rest a weapon." + PH, "field:GearCfg.BOSS_ARMOR"),
''')
rep('''"salvage.on", "salvage.pct", "salvage.dropPct"}''', '''"salvage.on", "salvage.pct", "salvage.dropPct",
           # 0.3.19: pack items become gear (items, combat stats) + the boss Mythic bag chance (rarity = economy)
           "part.packDrops", "loot.boss.mythic"}''')
after('''assert all(32 <= ord(_c) < 127 for _c in H7_MARK) and "=" not in H7_MARK and H7_MARK.startswith("# ")
''', '''G319_HEAD = "# ---- pack armor + weapons as mob drops, Mythic boss bags (SkyyGear 0.3.19) ----"
G319_ROWK = ["part.packDrops", "loot.packWeight", "loot.boss.mythic", "loot.boss.credit", "loot.boss.classLean", "loot.boss.armorShare"]
assert all(32 <= ord(_c) < 127 for _c in G319_HEAD) and "=" not in G319_HEAD
''')
after('''    L += ["", G317_HEAD]        # 0.3.17: the new rows (absent = the default) + the migrate0317 marker
    L += [H7_MARK]
    for k in G317_ROWK:
        scal(k)
''', '''    L += ["", G319_HEAD]        # 0.3.19: the new rows (absent = the default; no one-time update)
    for k in G319_ROWK:
        scal(k)
''')
rep('''("SALV_DROP", "int", "10")]''', '''("SALV_DROP", "int", "10"),
              # 0.3.19 pack drops + Mythic boss bags
              ("PACK_ON", "boolean", "true"), ("PACK_W", "double", "1.0"), ("BOSS_MY", "double", "10.0"), ("BOSS_CREDIT", "int", "15"),
              ("BOSS_LEAN", "int", "3"), ("BOSS_ARMOR", "int", "50")]''')
after('''  SALV_DROP = (int) plong(p, "salvage.dropPct", 10L, 0L, 100L);
''', '''  // 0.3.19 pack drops + Mythic boss bags (Server Setup -> Gear -> Loot)
  PACK_ON = pbool(p, "part.packDrops", true);
  PACK_W = pdec(p, "loot.packWeight", 1.0, 0.0, 100.0);
  BOSS_MY = pdec(p, "loot.boss.mythic", 10.0, 0.0, 100.0);
  BOSS_CREDIT = (int) plong(p, "loot.boss.credit", 15L, 0L, 100L);
  BOSS_LEAN = (int) plong(p, "loot.boss.classLean", 3L, 1L, 10L);
  BOSS_ARMOR = (int) plong(p, "loot.boss.armorShare", 50L, 0L, 100L);
''')

# ================================================================================================================ 1: GearPackId (before GearData)
before('''# ================================================================= GearData (1/2): id rules + document read + migration (spec 1)
''', '''# ================================================================= 0.3.19 GearPackId: the pack table (tools/pack_drops.py) - ids, sets, weights, tiers, zones, roles.
# Packed strings (one ';'-joined literal per column, split once in <clinit>): ~1,100 ids as array literals would push GearPool's <clinit>
# over the JVM's 64 KB method limit. Methods first (the field initialisers call them).
gpid = mk("GearPackId")
M(gpid, r"""
public static String[] strs(String packed) {
  if (packed == null || packed.length() == 0) return new String[0];
  return packed.split(";", -1);
}""")
M(gpid, r"""
public static int[] ints(String packed) {
  String[] p = strs(packed);
  int[] o = new int[p.length];
  for (int i = 0; i < p.length; i++) o[i] = Integer.parseInt(p[i]);
  return o;
}""")
F(gpid, "public static final String[] ID = strs(%s);" % jstr(";".join(_r[0] for _r in PACK_ROWS)))
F(gpid, "public static final int[] SET = ints(%s);" % jstr(";".join(str(_r[1]) for _r in PACK_ROWS)))
F(gpid, "public static final int[] AT = ints(%s);" % jstr(";".join(str(_r[3]) for _r in PACK_ROWS)))
F(gpid, "public static final int[] ZONE = ints(%s);" % jstr(";".join(str(_r[5]) for _r in PACK_ROWS)))
F(gpid, "public static final int[] ROLE = ints(%s);" % jstr(";".join(str(_r[6]) for _r in PACK_ROWS)))
F(gpid, "public static final int[] TY = ints(%s);" % jstr(";".join(str(_p[1]) for _p in PACK_POOL)))
F(gpid, "public static final String[] S_TIER = strs(%s);" % jstr(";".join(_s["tier"] for _s in PACK_SETS)))
F(gpid, "public static final String[] S_KEY = strs(%s);" % jstr(";".join(_s["key"] for _s in PACK_SETS)))
F(gpid, "public static final String[] S_NAME = strs(%s);" % jstr(";".join(_s["name"] for _s in PACK_SETS)))
F(gpid, "public static final String[] S_TAG = strs(%s);" % jstr(";".join(PACK_TAGS)))
F(gpid, 'public static final String[] ROLE_NAME = new String[] { "drop", "ut", "mythic" };')
F(gpid, "public static volatile java.util.HashMap IX = null;")
# id -> its row (-1 = not in the table); the table itself, whatever part.packDrops says
M(gpid, r"""
public static int idx(String id) {
  if (id == null) return -1;
  java.util.HashMap m = IX;
  if (m == null) {
    m = new java.util.HashMap();
    for (int i = 0; i < ID.length; i++) m.put(ID[i], Integer.valueOf(i));
    IX = m;
  }
  Object o = m.get(id);
  return o instanceof Integer ? ((Integer) o).intValue() : -1;
}""")
M(gpid, "public static boolean has(String id) { return @PKG@.GearCfg.PACK_ON && idx(id) >= 0; }")
# 1 Heavy, 2 Light, 3 Cloth, 0 = a weapon or not a pack item (or part.packDrops off)
M(gpid, r"""
public static int at(String id) {
  if (!@PKG@.GearCfg.PACK_ON) return 0;
  int k = idx(id);
  return k < 0 ? 0 : AT[k];
}""")
# the table tier (a level.material row word, lower case), null = not a pack item (or part.packDrops off)
M(gpid, r"""
public static String tier(String id) {
  if (!@PKG@.GearCfg.PACK_ON) return null;
  int k = idx(id);
  return k < 0 ? null : S_TIER[SET[k]];
}""")
M(gpid, r"""
public static String tag(String id) {
  if (!@PKG@.GearCfg.PACK_ON) return null;
  int k = idx(id);
  return k < 0 ? null : S_TAG[SET[k]];
}""")
# critic fix 1 (Skyy 2026-10-17 popup "Block craft, chest = plain"): a UT or Mythic table row = boss / Untiered only - never crafted here,
# and a copy their own chests / mobs drop stays a plain Normal piece
M(gpid, r"""
public static boolean special(String id) {
  if (!has(id)) return false;
  int k = idx(id);
  return k >= 0 && ROLE[k] >= 1;
}""")
# critic fix 6: GearData.isGear's pack answer per row (MaxStack + gear.exclude), dropped when the config reloads (GearCfg.EPOCH); 0 = ask
F(gpid, "public static volatile byte[] GC = null;")
F(gpid, "public static volatile long GCE = -1L;")
M(gpid, r"""
public static int gc(int k) {
  long e = @PKG@.GearCfg.EPOCH;
  byte[] c = GC;
  if (c == null || GCE != e) { GC = new byte[ID.length]; GCE = e; return 0; }
  if (k < 0 || k >= c.length) return 0;
  return c[k];
}""")
M(gpid, r"""
public static void gcSet(int k, boolean g) {
  byte[] c = GC;
  if (c != null && k >= 0 && k < c.length) c[k] = (byte) (g ? 1 : 2);
}""")
# critic fix 3: recipe inputs by ResourceTypeId (The Armory's Alteration Table and upgrades: IronDragonHelm <- resource AntiqueDragonHelm,
# EliteScorpianHelm <- 2 x resource ScorpianHelm): resource id -> the table SETS whose live items carry it (rebuilt when the item count moves)
F(gpid, "public static volatile java.util.HashMap RES = null;")
F(gpid, "public static volatile int RESN = -2;")
M(gpid, r"""
public static java.util.HashSet resSets(String rid) {
  if (rid == null) return null;
  int n = -1;
  try { n = @ITM@.getAssetMap().getAssetMap().size(); } catch (Throwable t) { n = -1; }
  java.util.HashMap m = RES;
  if (m == null || n != RESN) {
    m = new java.util.HashMap();
    for (int i = 0; i < ID.length; i++) {
      try {
        @ITM@ it = @PKG@.Gear.item(ID[i]);
        if (it == null) continue;
        com.hypixel.hytale.protocol.ItemResourceType[] rs = it.getResourceTypes();
        for (int j = 0; rs != null && j < rs.length; j++) {
          if (rs[j] == null || rs[j].id == null) continue;
          java.util.HashSet h = (java.util.HashSet) m.get(rs[j].id);
          if (h == null) { h = new java.util.HashSet(); m.put(rs[j].id, h); }
          h.add(Integer.valueOf(SET[i]));
        }
      } catch (Throwable t2) { }
    }
    RES = m;
    RESN = n;
  }
  return (java.util.HashSet) m.get(rid);
}""")
M(gpid, r"""
public static boolean carries(String itemId, String rid) {
  if (itemId == null || rid == null) return false;
  try {
    @ITM@ it = @PKG@.Gear.item(itemId);
    if (it == null) return false;
    com.hypixel.hytale.protocol.ItemResourceType[] rs = it.getResourceTypes();
    for (int j = 0; rs != null && j < rs.length; j++) if (rs[j] != null && rid.equals(rs[j].id)) return true;
  } catch (Throwable t) { }
  return false;
}""")
# the swap guard: the output is a pack item and an input is gear-like (a pack item, an Armor_ / Weapon_ id, or a resource type a table
# item carries - critic fix 3) - a colour swap at The Armory's Alteration Table or an upgrade made from a piece: no fresh roll, no Smithing XP
M(gpid, r"""
public static boolean swap(@CRR@ rc, String out) {
  if (rc == null || !has(out)) return false;
  try {
    @MQ@[] in = rc.getInput();
    if (in == null) return false;
    for (int i = 0; i < in.length; i++) {
      if (in[i] == null) continue;
      String q = in[i].getItemId();
      if (q == null) {
        String rid = in[i].getResourceTypeId();
        if (rid != null && resSets(rid) != null) return true;
        continue;
      }
      if (idx(q) >= 0 || q.startsWith("Armor_") || q.startsWith("Weapon_")) return true;
    }
  } catch (Throwable t) { }
  return false;
}""")
# local rebuild: The Armory's Alteration Table recipes (bench "ArmoryAlteration", their AlterationTransaction.isAlterationRecipe rule) carry
# the input's whole metadata + quality onto the new colour - the roll survives, so the swap veto never applies there
M(gpid, r"""
public static boolean alter(@CRR@ rc) {
  if (rc == null) return false;
  try {
    com.hypixel.hytale.protocol.BenchRequirement[] b = rc.getBenchRequirement();
    if (b == null) return false;
    for (int i = 0; i < b.length; i++) if (b[i] != null && "ArmoryAlteration".equals(b[i].id)) return true;
  } catch (Throwable t) { }
  return false;
}""")
# critic fix 1: an Alteration Table recipe that only turns a piece of a set into another colour of the SAME set (every item input a row of
# that set, every resource input carried by that set alone) - it makes nothing new (the input's whole document + quality carry over)
M(gpid, r"""
public static boolean sameSet(@CRR@ rc, String out) {
  if (rc == null || !alter(rc)) return false;
  int k = idx(out);
  if (k < 0) return false;
  int st = SET[k];
  try {
    @MQ@[] in = rc.getInput();
    if (in == null || in.length == 0) return false;
    for (int i = 0; i < in.length; i++) {
      if (in[i] == null) continue;
      String q = in[i].getItemId();
      if (q != null) { int j = idx(q); if (j < 0 || SET[j] != st) return false; continue; }
      java.util.HashSet h = resSets(in[i].getResourceTypeId());
      if (h == null || h.size() != 1 || !h.contains(Integer.valueOf(st))) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}""")
# critic fix 2: SkyySacks /craft (gear:fn:roll mode 8) - a UT / Mythic row or a swap recipe's output is a PLAIN Normal piece (no fresh roll)
M(gpid, r"""
public static boolean plainCraft(String id, Object rid) {
  if (!has(id)) return false;
  if (special(id)) return true;
  if (!(rid instanceof String)) return false;
  try {
    Object o = @CRR@.getAssetMap().getAsset((String) rid);
    return o instanceof @CRR@ && swap((@CRR@) o, id);
  } catch (Throwable t) { return false; }
}""")
# critic round 2 (Skyy 2026-10-17 popup "Yes, Requip only"): a recipe of the vanilla Salvagebench (The Armory's Salvage_* recipes give back
# 100% of a piece's materials)
M(gpid, r"""
public static boolean salvage(@CRR@ rc) {
  if (rc == null) return false;
  try {
    com.hypixel.hytale.protocol.BenchRequirement[] b = rc.getBenchRequirement();
    if (b == null) return false;
    for (int i = 0; i < b.length; i++) if (b[i] != null && "Salvagebench".equalsIgnoreCase(b[i].id)) return true;
  } catch (Throwable t) { }
  return false;
}""")
G319_EARLY = [gpid]

''')

# ================================================================================================================ 2: pack ids are gear
rep('''neverGear(id)) return false;
  if (included(id)) {''', '''neverGear(id)) return false;
  if (@PKG@.GearPackId.has(id)) {          // 0.3.19: a pack table id (tools/pack_drops.py) is gear while part.packDrops is on - never a stacking item
    String[] pex = @PKG@.GearCfg.excl();          // review L2: gear.exclude still applies
    for (int i = 0; i < pex.length; i++) if (id.startsWith(pex[i])) return false;
    if (ms <= 1) return true;
    @PKG@.Gear.warnOnce("packstack:" + id, "pack item " + id + " stacks to " + ms + " - it stays a plain item (only single items can be gear)");
    return false;
  }
  if (included(id)) {''')
rep('''neverGear(id)) return false;
  if (!included(id)) {''', '''neverGear(id)) return false;
  if (@PKG@.GearPackId.has(id)) {          // 0.3.19; critic fix 6: the answer cached per row until the config reloads
    int pk = @PKG@.GearPackId.idx(id);
    int pc = @PKG@.GearPackId.gc(pk);
    if (pc != 0) return pc == 1;
    int pms = maxStack(id);
    boolean pg = isGearMs(id, pms);
    if (pms >= 0) @PKG@.GearPackId.gcSet(pk, pg);          // an item not loaded yet is asked again
    return pg;
  }
  if (!included(id)) {''')
rep('''  if (best != null) return best;
''', '''  if (best != null) return best;
  if (@PKG@.GearPackId.has(id)) return "combat";          // 0.3.19: pack armor / weapons are combat gear (a kind.prefix row above still wins)
''')
# levels: the table tier's level.material row, after level.item and before the id-word look (never their ItemLevel)
rep('''  String mk = look(id.split("_"), mat, mw);          // 0.2.8: Weapon_Kunai_<Metal> looks from its metal word first''',
    '''  String mk = @PKG@.GearPackId.tier(id);          // 0.3.19: a pack item = its table tier's row (CamelCase ids have no metal word)
  if (mk == null || !(mat.get(mk) instanceof Integer)) mk = look(id.split("_"), mat, mw);          // 0.2.8: Weapon_Kunai_<Metal> looks from its metal word first''')
rep('''  return look(id.split("_"), mat, mw);          // 0.2.8: the same look as level()''',
    '''  String pt = @PKG@.GearPackId.tier(id);          // 0.3.19: the same order as level(): a pack item's table tier first
  if (pt != null && mat.get(pt) instanceof Integer) return pt;
  return look(id.split("_"), mat, mw);          // 0.2.8: the same look as level()''')
# Smithing's armor type (and every other reader of it): the table weight, not their sound set
rep('''public static int armorType(String id) {
  try {''', '''public static int armorType(String id) {
  int pa = @PKG@.GearPackId.at(id);          // 0.3.19: a pack piece's weight from the table (The Armory gives robes Heavy sounds)
  if (pa > 0) return pa;
  try {''')
# the tier tag in the tooltip's flavour slot (our per-stack tooltip only; their lang keys are never written)
rep('''    if (hasDesc(id)) add(lt, lc, FLAVOR, null);''',
    '''    if (hasDesc(id) || @PKG@.GearPackId.tag(id) != null) add(lt, lc, FLAVOR, null);          // 0.3.19: + a pack item's tier tag''')
rep('''      try { m.insert(@PKG@.Gear.item(id).getDescriptionTranslationMessage().color(@PKG@.GearDefs.C_GRAY).italic(true)); } catch (Throwable x) { }
''', '''      String tg = @PKG@.GearPackId.tag(id);          // 0.3.19: "T3 Iron - " first (tools/tier_tags.py numbering)
      boolean hd = hasDesc(id);
      if (tg != null) m.insert(@MSG@.raw(hd ? tg + " - " : tg).color(@PKG@.GearDefs.C_GRAY).italic(true));
      if (hd) try { m.insert(@PKG@.Gear.item(id).getDescriptionTranslationMessage().color(@PKG@.GearDefs.C_GRAY).italic(true)); } catch (Throwable x) { }
''')
# the swap guard in the craft roll (CraftRecipeEvent$Post)
rep('''    String id = po.getItemId();
    if (id == null || !@PKG@.GearRoll.craftable(id)) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (pr == null || p == null || p.getInventory() == null) return;''', '''    String id = po.getItemId();
    if (id == null || !@PKG@.GearRoll.craftable(id)) return;
    if (@PKG@.GearPackId.swap(rc, id)) return;          // 0.3.19: a pack piece made from a gear piece (colour swap / upgrade): no fresh roll, no XP
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (pr == null || p == null || p.getInventory() == null) return;''')

# ================================================================================================================ 3: GearPool rows (vanilla + pack)
rep('''F(gpool, "public static final String[] P_ID = %s;" % jarr([p[0] for p in LOOT_POOL]))
F(gpool, "public static final int[] P_T = %s;" % jints([LOOT_TYPES.index(p[1]) for p in LOOT_POOL]))
F(gpool, "public static final int[] P_AT = %s;" % jints([p[2] for p in LOOT_POOL]))
F(gpool, "public static final boolean[] P_DROP = new boolean[] { %s };" % ", ".join("true" if p[3] else "false" for p in LOOT_POOL))
''', '''# 0.3.19: the rows = the vanilla pool (P_N0 rows, unchanged) + the pack table (GearPackId, same order); methods first (the initialisers call them)
M(gpool, r"""
public static String[] catS(String[] a, String[] b) {
  String[] o = new String[a.length + b.length];
  for (int i = 0; i < a.length; i++) o[i] = a[i];
  for (int i = 0; i < b.length; i++) o[a.length + i] = b[i];
  return o;
}""")
M(gpool, r"""
public static int[] catI(int[] a, int[] b) {
  int[] o = new int[a.length + b.length];
  for (int i = 0; i < a.length; i++) o[i] = a[i];
  for (int i = 0; i < b.length; i++) o[a.length + i] = b[i];
  return o;
}""")
M(gpool, r"""
public static int[] fill(int n, int a, int[] b) {
  int[] o = new int[n + b.length];
  for (int i = 0; i < n; i++) o[i] = a;
  for (int i = 0; i < b.length; i++) o[n + i] = b[i];
  return o;
}""")
M(gpool, r"""
public static boolean[] catZ(boolean[] a, int extra) {
  boolean[] o = new boolean[a.length + extra];
  for (int i = 0; i < a.length; i++) o[i] = a[i];
  return o;
}""")
F(gpool, "public static final int P_N0 = %d;" % len(LOOT_POOL))
F(gpool, "public static final String[] P_ID = catS(%s, @PKG@.GearPackId.ID);" % jarr([p[0] for p in LOOT_POOL]))
F(gpool, "public static final int[] P_T = catI(%s, @PKG@.GearPackId.TY);" % jints([LOOT_TYPES.index(p[1]) for p in LOOT_POOL]))
F(gpool, "public static final int[] P_AT = catI(%s, @PKG@.GearPackId.AT);" % jints([p[2] for p in LOOT_POOL]))
F(gpool, "public static final boolean[] P_DROP = catZ(new boolean[] { %s }, @PKG@.GearPackId.ID.length);" % ", ".join("true" if p[3] else "false" for p in LOOT_POOL))
F(gpool, "public static final int[] P_ZONE = fill(%d, 0, @PKG@.GearPackId.ZONE);" % len(LOOT_POOL))
F(gpool, "public static final int[] P_ROLE = fill(%d, 0, @PKG@.GearPackId.ROLE);" % len(LOOT_POOL))
F(gpool, "public static final int[] P_SET = fill(%d, -1, @PKG@.GearPackId.SET);" % len(LOOT_POOL))
# boss bag counters: 0 boss kills seen, 1 rolls, 2 bags made, 3 nothing fits, 4 zone unknown, 5 bags opened from the zone's Mythic sets,
# 6 same fight (a phase / repeat death of a boss family within 120 s - critic fix 4; the hourly cap no longer applies to boss bags)
F(gpool, "public static final long[] BN = new long[7];")
''')
# the bag type of a pack row: weapons = the table's bag type when the live item IS a weapon (Item.getWeapon), armor = the LIVE item's
# ArmorSlot (-1 = not armor / not a weapon / no such item) + the row
# weight - both BEFORE table() (it calls them; methods before callers), so the 0.2.11 w(int i) goes
before('''M(gpool, r"""
public static Object[] table() {''', '''M(gpool, r"""
public static int liveType(int i) {
  if (i < P_N0) return P_T[i];
  try {
    @ITM@ it = @PKG@.Gear.item(P_ID[i]);
    if (it == null) return -1;
    @IAR@ a = it.getArmor();
    if (P_AT[i] == 0) return a == null && it.getWeapon() != null ? P_T[i] : -1;          // fix round: fail closed - a live weapon only
    @ARSL@ sl = a == null ? null : a.getArmorSlot();
    if (sl == null) return -1;
    String k = "Armor_" + sl.name();
    for (int t = 0; t < T_KEY.length; t++) if (T_KEY[t].equals(k)) return t;
    return -1;
  } catch (Throwable x) { return -1; }
}""")
# 0.3.19: a row's pick weight: vanilla 1 (drop-only x loot.dropOnlyWeight); a pack piece = loot.packWeight x its set's share of that slot (t[8])
M(gpool, r"""
public static double w(Object[] t, int i) {
  if (i >= P_N0) return @PKG@.GearCfg.PACK_W * ((double[]) t[8])[i];
  return P_DROP[i] ? @PKG@.GearCfg.DROPONLY_W : 1.0;
}""")
''')
rep('''M(gpool, "public static double w(int i) { return P_DROP[i] ? @PKG@.GearCfg.DROPONLY_W : 1.0; }")
''', '''# 0.3.19: w(int i) -> w(Object[] t, int i) above table() (a pack row's weight needs the table's set shares)
''')
# GearPool.table: + t[7] the live bag type per row, t[8] the pack share; pack rows: part.packDrops, the live item, role ut never in the pool
rep('''  int n = P_ID.length;
  boolean[] ok = new boolean[n];
  int[] lo = new int[n];
  int[] hi = new int[n];
  for (int i = 0; i < n; i++) {
    String id = P_ID[i];
    boolean v = false;
    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex) && !@PKG@.GearUt.has(id) && !@PKG@.GearMine.isPiece(id) && @PKG@.GearGArm.index(id) < 0 && !@PKG@.GearUtFx.mythicId(id); } catch (Throwable x) { v = false; }
    int[] b = @PKG@.GearLevel.band(id);''', '''  int n = P_ID.length;
  boolean[] ok = new boolean[n];
  int[] lo = new int[n];
  int[] hi = new int[n];
  int[] lt = new int[n];
  double[] pw = new double[n];
  for (int i = 0; i < n; i++) {
    String id = P_ID[i];
    boolean v = false;
    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex) && !@PKG@.GearUt.has(id) && !@PKG@.GearMine.isPiece(id) && @PKG@.GearGArm.index(id) < 0 && !@PKG@.GearUtFx.mythicId(id); } catch (Throwable x) { v = false; }
    lt[i] = liveType(i);          // 0.3.19: pack rows by the live item (a missing id / a slot-less piece = never a candidate)
    if (i >= P_N0 && (!@PKG@.GearCfg.PACK_ON || P_ROLE[i] == 1 || lt[i] < 0)) v = false;
    int[] b = @PKG@.GearLevel.band(id);''')
rep('''    ok[i] = v;
    lo[i] = a;
    hi[i] = c;
  }
  t = new Object[] { Long.valueOf(ep), Long.valueOf(now), ok, lo, hi, Integer.valueOf(top), ex };
  TAB = t;
  return t;
}""")''', '''    ok[i] = v;
    lo[i] = a;
    hi[i] = c;
  }
  // 0.3.19 PICKED BY SET: each live pack piece = 1 / (the live pieces of its set in its bag type), so a set weighs 1 per slot
  java.util.HashMap cnt = new java.util.HashMap();
  for (int i = P_N0; i < n; i++) {
    if (!ok[i]) continue;
    String k = P_SET[i] + ":" + lt[i];
    Object o = cnt.get(k);
    cnt.put(k, Integer.valueOf(o instanceof Integer ? ((Integer) o).intValue() + 1 : 1));
  }
  for (int i = P_N0; i < n; i++) {
    if (!ok[i]) continue;
    Object o = cnt.get(P_SET[i] + ":" + lt[i]);
    pw[i] = o instanceof Integer ? 1.0 / (double) ((Integer) o).intValue() : 0.0;
  }
  t = new Object[] { Long.valueOf(ep), Long.valueOf(now), ok, lo, hi, Integer.valueOf(top), ex, lt, pw, Integer.valueOf(ic) };
  TAB = t;
  return t;
}""")''')
# match: the live type, never a Mythic row (bosses only), the pack weight
rep('''public static boolean match(Object[] t, int i, int ty, int at, int L) {
  if (!((boolean[]) t[2])[i] || P_T[i] != ty || !(w(i) > 0.0)) return false;''', '''public static boolean match(Object[] t, int i, int ty, int at, int L) {
  if (!((boolean[]) t[2])[i] || ((int[]) t[7])[i] != ty || P_ROLE[i] == 2 || !(w(t, i) > 0.0)) return false;          // 0.3.19: live type, no Mythic row''')
rep('''public static int idIdx(String id) {
  if (id == null) return -1;
''', '''public static int idIdx(String id) {
  if (id == null) return -1;
  int pk = @PKG@.GearPackId.idx(id);          // 0.3.19: the pack rows by the table's map (P_ID[P_N0 + k] = GearPackId.ID[k])
  if (pk >= 0) return P_N0 + pk;
''')
rep('''public static int typeOfId(String id) {
  int k = idIdx(id);
  if (k >= 0) return P_T[k];''', '''public static int typeOfId(String id) {
  int k = idIdx(id);
  if (k >= P_N0) return liveType(k);          // 0.3.19: a pack row = its live slot / table bag type
  if (k >= 0) return P_T[k];''')
rep('''  for (int i = 0; i < P_ID.length; i++) if (match(t, i, ty, at, L)) { sum = sum + w(i); last = i; }
  if (last < 0 || !(sum > 0.0)) return null;
  double r = @PKG@.GearRoll.RNG.nextDouble() * sum;
  for (int i = 0; i < P_ID.length; i++) {
    if (!match(t, i, ty, at, L)) continue;
    r = r - w(i);''', '''  for (int i = 0; i < P_ID.length; i++) if (match(t, i, ty, at, L)) { sum = sum + w(t, i); last = i; }
  if (last < 0 || !(sum > 0.0)) return null;
  double r = @PKG@.GearRoll.RNG.nextDouble() * sum;
  for (int i = 0; i < P_ID.length; i++) {
    if (!match(t, i, ty, at, L)) continue;
    r = r - w(t, i);''')
# the Mythic picks (zone z) + the pack status line, after pickType (before statusText)
rep('''M(gpool, r"""
public static String statusText() {
  Object[] t = table();
  boolean[] ok = (boolean[]) t[2];
  int n = 0;
  int d = 0;
  for (int i = 0; i < ok.length; i++) if (ok[i]) { n++; if (P_DROP[i]) d++; }
  return "bag pool " + n + " / " + P_ID.length + " items (" + d + " drop-only) in " + T_KEY.length + " types";
}""")''', '''# ---- 0.3.19 the Mythic boss picks: rows of role mythic in zone z (live, part.packDrops on), the same bands and weights as the normal pool
M(gpool, r"""
public static boolean matchM(Object[] t, int i, int ty, int at, int z, int L) {
  if (i < P_N0 || P_ROLE[i] != 2 || P_ZONE[i] != z || !((boolean[]) t[2])[i] || ((int[]) t[7])[i] != ty || !(((double[]) t[8])[i] > 0.0)) return false;          // review M5: the set share only (never loot.packWeight)
  if (at > 0 && P_AT[i] != at) return false;
  return L < 0 || (((int[]) t[3])[i] <= L && L <= ((int[]) t[4])[i]);
}""")
M(gpool, r"""
public static boolean[] levelsM(int ty, int at, int z) {
  boolean[] out = new boolean[102];
  if (ty < 0 || ty >= T_KEY.length) return out;
  Object[] t = table();
  int[] lo = (int[]) t[3];
  int[] hi = (int[]) t[4];
  for (int i = P_N0; i < P_ID.length; i++) {
    if (!matchM(t, i, ty, at, z, -1)) continue;
    for (int L = lo[i]; L <= hi[i] && L <= 101; L++) if (L >= 0) out[L] = true;
  }
  return out;
}""")
M(gpool, r"""
public static int candM(int ty, int at, int z) {
  Object[] t = table();
  int n = 0;
  for (int i = P_N0; i < P_ID.length; i++) if (matchM(t, i, ty, at, z, -1)) n++;
  return n;
}""")
# { lo, hi } = the first / last level with a Mythic candidate of that type + armor type in zone z; null = none
M(gpool, r"""
public static int[] rangeM(int ty, int at, int z) {
  boolean[] lv = levelsM(ty, at, z);
  int lo = -1;
  int hi = -1;
  for (int L = 1; L <= 101; L++) if (lv[L]) { if (lo < 0) lo = L; hi = L; }
  if (lo < 0) return null;
  return new int[] { lo, hi };
}""")
M(gpool, r"""
public static int pickLevelM(int ty, int at, int z, int lo, int hi) {
  boolean[] lv = levelsM(ty, at, z);
  int n = 0;
  for (int L = lo; L <= hi; L++) if (L >= 1 && L <= 101 && lv[L]) n++;
  if (n == 0) return -1;
  int k = @PKG@.GearRoll.RNG.nextInt(n);
  for (int L = lo; L <= hi; L++) {
    if (L < 1 || L > 101 || !lv[L]) continue;
    if (k == 0) return L;
    k--;
  }
  return -1;
}""")
M(gpool, r"""
public static String pickItemM(int ty, int at, int z, int L) {
  Object[] t = table();
  double sum = 0.0;
  int last = -1;
  for (int i = P_N0; i < P_ID.length; i++) if (matchM(t, i, ty, at, z, L)) { sum = sum + ((double[]) t[8])[i]; last = i; }
  if (last < 0 || !(sum > 0.0)) return null;
  double r = @PKG@.GearRoll.RNG.nextDouble() * sum;
  for (int i = P_N0; i < P_ID.length; i++) {
    if (!matchM(t, i, ty, at, z, L)) continue;
    r = r - ((double[]) t[8])[i];
    if (r < 0.0) return P_ID[i];
  }
  return P_ID[last];
}""")
# a Mythic bag's type: armor / weapon by the share, then a type with a Mythic candidate in zone z (own-class weapon types x mult)
M(gpool, r"""
public static int pickTypeM(boolean armor, int z, String[] lean, int mult) {
  double[] wt = new double[T_KEY.length];
  double sum = 0.0;
  for (int ty = 0; ty < T_KEY.length; ty++) {
    if (T_ARM[ty] != armor || candM(ty, 0, z) == 0) continue;
    wt[ty] = !armor && leanHit(T_KEY[ty], lean) ? (double) (mult < 1 ? 1 : mult) : 1.0;
    sum = sum + wt[ty];
  }
  if (!(sum > 0.0)) return -1;
  double r = @PKG@.GearRoll.RNG.nextDouble() * sum;
  int last = -1;
  for (int ty = 0; ty < T_KEY.length; ty++) {
    if (!(wt[ty] > 0.0)) continue;
    last = ty;
    r = r - wt[ty];
    if (r < 0.0) return ty;
  }
  return last;
}""")
# fix round (spec Q13): a Mythic ARMOR bag = { slot type, weight }: the weight (armor type 1-3) evenly among the weights with any Mythic
# piece in zone z, then a slot evenly among the armor slots with a piece of that weight (slot coverage never biases the weight); null = none
M(gpool, r"""
public static int[] pickArmM(int z) {
  boolean[] got = new boolean[4];
  int n = 0;
  for (int at = 1; at <= 3; at++) {
    for (int ty = 0; ty < T_KEY.length && !got[at]; ty++) if (T_ARM[ty] && candM(ty, at, z) > 0) got[at] = true;
    if (got[at]) n++;
  }
  if (n == 0) return null;
  int k = @PKG@.GearRoll.RNG.nextInt(n);
  int at = -1;
  for (int a = 1; a <= 3 && at < 0; a++) {
    if (!got[a]) continue;
    if (k == 0) at = a;
    k--;
  }
  if (at < 0) return null;
  int m = 0;
  for (int ty = 0; ty < T_KEY.length; ty++) if (T_ARM[ty] && candM(ty, at, z) > 0) m++;
  if (m == 0) return null;
  int j = @PKG@.GearRoll.RNG.nextInt(m);
  for (int ty = 0; ty < T_KEY.length; ty++) {
    if (!T_ARM[ty] || candM(ty, at, z) == 0) continue;
    if (j == 0) return new int[] { ty, at };
    j--;
  }
  return null;
}""")
M(gpool, "public static synchronized void bcount(int i, long d) { if (i >= 0 && i < BN.length) BN[i] = BN[i] + d; }")
M(gpool, r"""
public static synchronized String packText() {
  Object[] t = table();
  boolean[] ok = (boolean[]) t[2];
  int live = 0;
  int miss = 0;
  int myth = 0;
  int ut = 0;
  int[] zm = new int[6];
  for (int i = P_N0; i < P_ID.length; i++) {
    if (P_ROLE[i] == 1) { ut++; continue; }
    if (((int[]) t[7])[i] < 0) { miss++; continue; }
    if (!ok[i]) continue;
    if (P_ROLE[i] == 2) { myth++; if (P_ZONE[i] > 0 && P_ZONE[i] < 6) zm[P_ZONE[i]]++; } else live++;
  }
  return "pack drops " + (@PKG@.GearCfg.PACK_ON ? "on" : "OFF") + ": " + live + " normal + " + myth + " Mythic pieces live of " + (P_ID.length - P_N0)
    + " table ids (" + miss + " not installed / no slot, " + ut + " Untiered candidates wait for their ut rows); Mythic pieces by zone 1-5: "
    + zm[1] + " / " + zm[2] + " / " + zm[3] + " / " + zm[4] + " / " + zm[5] + "; boss Mythic bags " + @PKG@.GearCfg.BOSS_MY + "% (credit "
    + @PKG@.GearCfg.BOSS_CREDIT + "%): boss kills " + BN[0] + ", rolls " + BN[1] + ", bags " + BN[2] + ", nothing fit " + BN[3]
    + ", zone unknown " + BN[4] + ", same fight " + BN[6] + ", opened from Mythic sets " + BN[5];
}""")
M(gpool, r"""
public static String statusText() {
  Object[] t = table();
  boolean[] ok = (boolean[]) t[2];
  int n = 0;
  int d = 0;
  for (int i = 0; i < ok.length; i++) if (ok[i]) { n++; if (P_DROP[i]) d++; }
  return "bag pool " + n + " / " + P_ID.length + " items (" + d + " drop-only) in " + T_KEY.length + " types";
}""")''')

# ================================================================================================================ 4: GearUnid - the zone field pz
rep('''M(gunid, "public static int hi(@BD@ d) { int l = lo(d); int h = d == null ? l : @PKG@.GearData.num(d, \\"hi\\", l); return h < l ? l : h; }")
''', '''M(gunid, "public static int hi(@BD@ d) { int l = lo(d); int h = d == null ? l : @PKG@.GearData.num(d, \\"hi\\", l); return h < l ? l : h; }")
# 0.3.19: a Mythic boss bag's zone (1-5; 0 = an ordinary bag) - the bag document and the identified item's box sub-document carry it
M(gunid, "public static int pz(@BD@ d) { int z = d == null ? 0 : @PKG@.GearData.num(d, \\"pz\\", 0); return z < 0 || z > 9 ? 0 : z; }")
''')
rep('''  txt.add(arm ? "Cannot be worn until identified." : "Cannot be used until identified."); col.add(@PKG@.GearDefs.C_BAD);
''', '''  if (pz(d) > 0) { txt.add("Boss drop: one of Zone " + pz(d) + "'s Mythic " + (arm ? "armor pieces" : typeName(ty).toLowerCase() + "s") + "."); col.add(@PKG@.GearDefs.C_LABEL); }          // 0.3.19
  txt.add(arm ? "Cannot be worn until identified." : "Cannot be used until identified."); col.add(@PKG@.GearDefs.C_BAD);
''')
rep('''public static @IS@ make(int ty, int at, int r, int lo, int hi, String src, String ls, int tier) {
  if (ty < 0 || ty >= @PKG@.GearPool.T_KEY.length || r < 0 || r >= BAG.length) return null;''', '''public static @IS@ makeZ(int ty, int at, int r, int lo, int hi, String src, String ls, int tier, int pz) {
  if (ty < 0 || ty >= @PKG@.GearPool.T_KEY.length || r < 0 || r >= BAG.length) return null;''')
rep('''  d.append("id", new org.bson.BsonBoolean(false));
  @IS@ s = new @IS@(BAG[r], 1);
  s = s.withMetadata(KEY, (@BV@) d);
  MADE.incrementAndGet();
  return view(s, d);
}""")''', '''  d.append("id", new org.bson.BsonBoolean(false));
  if (pz > 0) d.append("pz", new org.bson.BsonInt32(pz));          // 0.3.19: a Mythic boss bag's zone (absent = an ordinary bag, byte-identical to 0.3.18)
  @IS@ s = new @IS@(BAG[r], 1);
  s = s.withMetadata(KEY, (@BV@) d);
  MADE.incrementAndGet();
  return view(s, d);
}""")
M(gunid, "public static @IS@ make(int ty, int at, int r, int lo, int hi, String src, String ls, int tier) { return makeZ(ty, at, r, lo, hi, src, ls, tier, 0); }")''')
rep('''  if (rar(d) == @PKG@.GearDefs.R_UT) return @PKG@.GearUt.why(ty, lo(d), hi(d));       // 0.2.14: the orange bag reads the Untiered table
''', '''  if (rar(d) == @PKG@.GearDefs.R_UT) return @PKG@.GearUt.why(ty, lo(d), hi(d));       // 0.2.14: the orange bag reads the Untiered table
  if (pz(d) > 0) {          // 0.3.19: a boss bag opens only into its zone's Mythic pieces (any armor weight when its own has none left)
    if (@PKG@.GearPool.rangeM(ty, at(d), pz(d)) != null || @PKG@.GearPool.rangeM(ty, 0, pz(d)) != null) return null;
    return "This Zone " + pz(d) + " Mythic bag waits for its Mythic pieces (their mod is off or renamed) - it stays safe; an admin can help.";
  }
''')
rep('''public static Object[] pick(int ty, int at, int r, int lo, int hi, int n, java.util.UUID by) {
  if (ty < 0) return null;
  // 0.2.14: an orange bag picks among the Untiered rows of its type (newDoc makes the document Untiered)
  boolean ut = r == @PKG@.GearDefs.R_UT;
  if (!ut) {         // 0.2.15 fix round: an old bag whose range lost its metal pieces (GearUnid.fit)''', '''public static Object[] pickZ(int ty, int at, int r, int lo, int hi, int n, java.util.UUID by, int pz) {
  if (ty < 0) return null;
  // 0.2.14: an orange bag picks among the Untiered rows of its type (newDoc makes the document Untiered)
  boolean ut = r == @PKG@.GearDefs.R_UT;
  // 0.3.19: a Mythic boss bag (pz = its zone) picks among that zone's Mythic pieces of its type at their band; none left = refused (the bag
  // stays - review M5: never a Mythic vanilla item; why() says so)
  if (!ut && pz > 0) {
    int[] mr = @PKG@.GearPool.rangeM(ty, at, pz);
    int mat = at;
    if (mr == null && at > 0) { mat = 0; mr = @PKG@.GearPool.rangeM(ty, 0, pz); }
    if (mr != null) {
      int mL = @PKG@.GearPool.pickLevelM(ty, mat, pz, mr[0], mr[1]);
      String mid = mL < 0 ? null : @PKG@.GearPool.pickItemM(ty, mat, pz, mL);
      if (mid != null) {
        @BD@ md = @PKG@.GearRoll.newDoc(mid, r, true, "box", mL);
        md.put("idAt", new org.bson.BsonInt64(System.currentTimeMillis()));
        if (by != null) md.put("idBy", new org.bson.BsonString(by.toString()));
        @BD@ mb = boxSub(ty, mat, r, mr[0], mr[1], n);
        mb.put("pz", new org.bson.BsonInt32(pz));
        md.put("box", mb);
        @IS@ ms = @PKG@.GearData.put(new @IS@(mid, 1), md, by);
        @PKG@.GearPool.bcount(5, 1L);
        return new Object[] { mid, Integer.valueOf(mL), md, ms };
      }
    }
    return null;
  }
  if (!ut) {         // 0.2.15 fix round: an old bag whose range lost its metal pieces (GearUnid.fit)''')
rep('''  nd.put("box", boxSub(ty, at, r, lo, hi, n));
  @IS@ ns = @PKG@.GearData.put(new @IS@(id, 1), nd, by);
  return new Object[] { id, Integer.valueOf(L), nd, ns };
}""")
M(gunid, "public static Object[] open(@BD@ d, java.util.UUID by) { if (d == null) return null; return pick(type(d), at(d), rar(d), lo(d), hi(d), 0, by); }")''', '''  @BD@ nb = boxSub(ty, at, r, lo, hi, n);
  if (pz > 0) nb.put("pz", new org.bson.BsonInt32(pz));          // 0.3.19: a re-identify of a boss bag's item stays in its zone
  nd.put("box", nb);
  @IS@ ns = @PKG@.GearData.put(new @IS@(id, 1), nd, by);
  return new Object[] { id, Integer.valueOf(L), nd, ns };
}""")
M(gunid, "public static Object[] pick(int ty, int at, int r, int lo, int hi, int n, java.util.UUID by) { return pickZ(ty, at, r, lo, hi, n, by, 0); }")
M(gunid, "public static Object[] open(@BD@ d, java.util.UUID by) { if (d == null) return null; return pickZ(type(d), at(d), rar(d), lo(d), hi(d), 0, by, pz(d)); }")''')
rep('''  return pick(type(b), at(b), rar(b), lo(b), hi(b), rerolls(b) + 1, by);''',
    '''  return pickZ(type(b), at(b), rar(b), lo(b), hi(b), rerolls(b) + 1, by, pz(b));          // 0.3.19: + the boss zone''', 2)

rep('''  if (rar(b) == @PKG@.GearDefs.R_UT) return null;       // fix round (ut02 review): rerollWhy(id, d) decides (another Untiered item?)
''', '''  if (rar(b) == @PKG@.GearDefs.R_UT) return null;       // fix round (ut02 review): rerollWhy(id, d) decides (another Untiered item?)
  if (pz(b) > 0) {          // 0.3.19: a boss item re-identifies inside its zone's Mythic pieces only
    if (@PKG@.GearPool.rangeM(ty, at(b), pz(b)) != null || @PKG@.GearPool.rangeM(ty, 0, pz(b)) != null) return null;
    return "No Zone " + pz(b) + " Mythic " + typeName(ty).toLowerCase() + " exists here any more.";
  }
''')

# ================================================================================================================ 5: GearPack (after GearLoot) - the boss roll
rep('''M(gloot, r"""
public static synchronized String countsText() {
  return countsText0() + "; " + @PKG@.GearUt.dropsText();          // 0.2.16
}""")''', '''M(gloot, r"""
public static synchronized String countsText() {
  return countsText0() + "; " + @PKG@.GearUt.dropsText() + "; " + @PKG@.GearPool.packText();          // 0.2.16; 0.3.19 + the pack line
}""")''')
before('''# ---------------------------------------------------------------- GearBoxFn: gear:fn:box (never throws, never touches ECS)
''', '''# ---------------------------------------------------------------- 0.3.19 GearPack: the Mythic boss bags (SkyyMobs 0.1.10 mob:fn:boss)
gpack = mk("GearPack")
# one Mythic bag of zone z for a player with class lean `lean` (null = nothing fits); armor via pickArmM (weight evenly), weapons via pickTypeM
M(gpack, r"""
public static @IS@ mythicBag(int z, String[] lean) {
  if (z < 1) return null;
  boolean armor = @PKG@.GearRoll.RNG.nextDouble() * 100.0 < (double) @PKG@.GearCfg.BOSS_ARMOR;
  int[] pk = null;
  for (int k = 0; k < 2 && pk == null; k++) {          // the armor share, else the other side when it has no Mythic piece in zone z
    if (k == 0 ? armor : !armor) pk = @PKG@.GearPool.pickArmM(z);          // fix round (Q13): armor = weight evenly, then slot
    else {
      int wt = @PKG@.GearPool.pickTypeM(false, z, lean, @PKG@.GearCfg.BOSS_LEAN);          // weapons: own-class types x loot.boss.classLean
      if (wt >= 0) pk = new int[] { wt, 0 };
    }
  }
  if (pk == null) return null;
  int ty = pk[0];
  int at = pk[1];
  int[] rg = @PKG@.GearPool.rangeM(ty, at, z);
  if (rg == null) return null;
  return @PKG@.GearUnid.makeZ(ty, at, @PKG@.GearDefs.R_MY, rg[0], rg[1], "boss", "zone" + z, 0, z);
}""")
# critic fix 4: a boss FAMILY (the role up to "_Phase", e.g. Goblin_Duke_Phase_2 -> Goblin_Duke) rolls once per credited player per fight
# (FIGHT_MS): phase roles that die one after another (Goblin_Duke, Skeleton_Elite) cannot roll 3-4 times. Expired entries are swept.
F(gpack, "public static final java.util.concurrent.ConcurrentHashMap FIGHT = new java.util.concurrent.ConcurrentHashMap();")
F(gpack, "public static final long FIGHT_MS = 120000L;")
M(gpack, r"""
public static String family(String role) {
  if (role == null) return "";
  int k = role.indexOf("_Phase");
  return k > 0 ? role.substring(0, k) : role;
}""")
M(gpack, r"""
public static boolean firstOfFight(java.util.UUID u, String fam, long now) {
  if (u == null) return false;
  if (FIGHT.size() > 256) {
    Object[] ks = FIGHT.keySet().toArray();
    for (int i = 0; i < ks.length; i++) {
      Object o = FIGHT.get(ks[i]);
      if (!(o instanceof Long) || now - ((Long) o).longValue() >= FIGHT_MS || now < ((Long) o).longValue()) FIGHT.remove(ks[i]);
    }
  }
  String k = fam + "|" + u;
  Object o = FIGHT.get(k);
  if (o instanceof Long && now - ((Long) o).longValue() < FIGHT_MS && now >= ((Long) o).longValue()) return false;
  FIGHT.put(k, Long.valueOf(now));
  return true;
}""")
# the players who roll: SkyyMobs' credit list (>= loot.boss.credit % of the damage); the killer only when nobody is credited at all (review
# M4: credited players all under the bar = nobody); same store, not Creative; no head-count cap (fix round; critic fix 4: once per fight per player)
M(gpack, r"""
public static java.util.ArrayList rollers(Object[] a, @DTHC@ dc, @ST@ store) {
  java.util.ArrayList us = new java.util.ArrayList();
  String[] who = a.length > 2 && a[2] instanceof String[] ? (String[]) a[2] : new String[0];
  double[] sh = a.length > 3 && a[3] instanceof double[] ? (double[]) a[3] : new double[0];
  double need = (double) @PKG@.GearCfg.BOSS_CREDIT / 100.0;
  for (int i = 0; i < who.length && i < sh.length; i++) {
    if (who[i] == null || !(sh[i] + 1.0E-9 >= need)) continue;
    try { java.util.UUID u = java.util.UUID.fromString(who[i]); if (!us.contains(u)) us.add(u); } catch (Throwable t) { }
  }
  if (us.isEmpty() && who.length == 0) {
    @REF@ kr = @PKG@.GearLoot.killer(dc, store);
    @PR@ kp = kr == null ? null : (@PR@) store.getComponent(kr, @PR@.getComponentType());
    if (kp != null && kp.getUuid() != null) us.add(kp.getUuid());
  }
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < us.size(); i++) {
    java.util.UUID u = (java.util.UUID) us.get(i);
    try {
      @PR@ pr = @UNI@.get().getPlayer(u);
      @REF@ rr = pr == null ? null : pr.getReference();
      if (rr == null || !rr.isValid() || rr.getStore() != store) continue;
      @PLA@ pl = (@PLA@) store.getComponent(rr, @PLA@.getComponentType());
      if (pl != null && pl.getGameMode() == @GM@.Creative) continue;
      out.add(pr);
    } catch (Throwable t) { }
  }
  return out;
}""")
# review M1: refuse a colour swap / upgrade at a pack recipe while the player holds a ROLLED piece of its gear input (rarity above Normal):
# the output is a new piece, the roll would be lost; Normal pieces swap freely (null = allowed)
M(gpack, r"""
public static String swapVeto(@CRR@ rc, String out, @INV@ inv) {
  if (inv == null || !@PKG@.GearPackId.swap(rc, out) || @PKG@.GearPackId.alter(rc)) return null;          // local rebuild: the Alteration Table keeps the roll
  @MQ@[] in = rc.getInput();
  if (in == null) return null;
  @IC@[] cs = @PKG@.GearStamp.allOf(inv);
  for (int k = 0; k < in.length; k++) {
    if (in[k] == null) continue;
    String q = in[k].getItemId();
    String rid = q == null ? in[k].getResourceTypeId() : null;          // critic fix 3: a resource input a table item carries
    if (q == null && (rid == null || @PKG@.GearPackId.resSets(rid) == null)) continue;
    if (q != null && !@PKG@.GearData.isGear(q)) continue;
    for (int c = 0; c < cs.length; c++) {
      if (cs[c] == null) continue;
      for (int i = 0; i < cs[c].getCapacity(); i++) {
        @IS@ s = cs[c].getItemStack((short) i);
        if (s == null || s.isEmpty()) continue;
        String sid = s.getItemId();
        if (q != null ? !q.equals(sid) : !@PKG@.GearPackId.carries(sid, rid)) continue;
        @BD@ d = @PKG@.GearData.effective(sid, s.getMetadata());
        if (d != null && @PKG@.GearData.rarity(d) > 0)
          return @PKG@.Gear.itemName(sid) + " in your inventory carries a rolled rarity - this recipe makes a new piece and would erase it. Store the rolled piece first; Normal pieces swap freely.";
      }
    }
  }
  return null;
}""")
# critic round 2 (Skyy 2026-10-17 "Yes, Requip only"): a pack piece whose SkyyGear document did not come from a craft (dropped, found in a
# chest, a boss bag, identified) salvages only through Requip SALVAGE (gear:fn:salvage) - never for 100% at a Salvagebench recipe
M(gpack, r"""
public static boolean salvBlocked(String sid, @BD@ md) {
  if (sid == null || !@PKG@.GearPackId.has(sid)) return false;
  @BD@ d = @PKG@.GearData.effective(sid, md);
  return d != null && @PKG@.GearData.hasAnyDoc(md) && !"craft".equals(@PKG@.GearData.str(d, "src", ""));
}""")
M(gpack, r"""
public static String salvVeto(@CRR@ rc, @INV@ inv) {
  if (inv == null || rc == null || !@PKG@.GearPackId.salvage(rc)) return null;
  @MQ@[] in = rc.getInput();
  if (in == null) return null;
  @IC@[] cs = @PKG@.GearStamp.allOf(inv);
  for (int k = 0; k < in.length; k++) {
    if (in[k] == null) continue;
    String q = in[k].getItemId();
    String rid = q == null ? in[k].getResourceTypeId() : null;
    if (q == null && (rid == null || @PKG@.GearPackId.resSets(rid) == null)) continue;
    if (q != null && !@PKG@.GearPackId.has(q)) continue;
    for (int c = 0; c < cs.length; c++) {
      if (cs[c] == null) continue;
      for (int i = 0; i < cs[c].getCapacity(); i++) {
        @IS@ s = cs[c].getItemStack((short) i);
        if (s == null || s.isEmpty()) continue;
        String sid = s.getItemId();
        if (q != null ? !q.equals(sid) : !@PKG@.GearPackId.carries(sid, rid)) continue;
        if (salvBlocked(sid, s.getMetadata()))
          return @PKG@.Gear.itemName(sid) + " in your inventory is a dropped / identified piece - salvage it with Requip's SALVAGE button, not at a Salvagebench. Store it first to salvage a crafted one here.";
      }
    }
  }
  return null;
}""")
# review H2: a won bag goes INTO its winner's inventory (storage, hotbar, backpack - the engine rule) in a world task after the death tick;
# full = dropped at the winner's feet (ItemUtils.dropItem, vanilla's overflow); the winner gone or in another world now (fix round: the
# task re-checks Ref.getStore() == the boss's store before touching the inventory) = dropped at the boss (vanilla's death-drop
# recipe). A ground drop at the boss would be claimed by SkyySacks' auto-pickup for the top damager (its PickBook death mark).
gpgv = mk("GearPackGive")
gpgv.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PR@ pr;", "public @IS@ bag;", "public @ST@ store;", "public @VEC@ at;", "public @RTF@ rot;", "public int z;"):
    F(gpgv, _f)
M(gpgv, r"""
public static int cnt(@IC@ c, String id) {
  int n = 0;
  if (c == null || id == null) return 0;
  for (int i = 0; i < c.getCapacity(); i++) {
    @IS@ s = c.getItemStack((short) i);
    if (s != null && !s.isEmpty() && id.equals(s.getItemId())) n = n + s.getQuantity();
  }
  return n;
}""")
C(gpgv, r"""
public GearPackGive(@PR@ pr, @IS@ bag, @ST@ store, @VEC@ at, @RTF@ rot, int z) {
  this.pr = pr; this.bag = bag; this.store = store; this.at = at; this.rot = rot; this.z = z;
}""")
M(gpgv, r"""
public void run() {
  String how = "lost";
  boolean here = false;
  try {
    @INV@ inv = null;
    @REF@ r = this.pr == null || !this.pr.isValid() ? null : this.pr.getReference();
    here = r != null && r.isValid() && r.getStore() == this.store;          // fix round: the winner may have changed worlds since the death tick
    if (here) inv = @PKG@.GearStamp.invOf(this.pr);
    if (inv != null) {
      @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
      for (int i = 0; i < cs.length && "lost".equals(how); i++) {
        if (cs[i] == null) continue;
        int c0 = cnt(cs[i], this.bag.getItemId());
        try {
          Object tx = cs[i].addItemStack(this.bag);
          if (!(tx instanceof @TXN@) || ((@TXN@) tx).succeeded()) how = "inventory";
        } catch (Throwable ta) {          // critic fix 6: counted before and after - a write that landed = given (never a second copy); none = go on
          if (cnt(cs[i], this.bag.getItemId()) != c0) how = "inventory";
          @PKG@.Gear.warnOnce("bossgive-add", "boss Mythic bag: a container refused the write: " + ta);
        }
      }
      if ("lost".equals(how) && r.isValid() && r.getStore() == this.store) { @ITU@.dropItem(r, this.bag, this.store); how = "feet"; }
    }
    if ("lost".equals(how) && this.store != null) {
      java.util.ArrayList l = new java.util.ArrayList();
      l.add(this.bag);
      @HLDR@[] hs = @ITC@.generateItemDrops(this.store, l, this.at, this.rot);
      if (hs != null && hs.length > 0) { this.store.addEntities(hs, @ADDR@.SPAWN); how = "boss"; }
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("bossgive", "boss Mythic bag delivery failed: " + t); }
  @PKG@.GearLog.line("LOOT boss-give " + (this.pr == null ? "?" : this.pr.getUsername()) + " zone " + this.z + " " + @PKG@.GearUnid.logText(this.bag) + " -> " + how);
  try {
    if ("inventory".equals(how)) this.pr.sendMessage(@MSG@.raw("[Gear] The boss dropped a Zone " + this.z + " Mythic bag for you - it is in your inventory.").color(@PKG@.GearDefs.C_GOLD));
    else if ("feet".equals(how)) this.pr.sendMessage(@MSG@.raw("[Gear] The boss dropped a Zone " + this.z + " Mythic bag for you - your inventory is full, it lies at your feet.").color(@PKG@.GearDefs.C_GOLD));
    else if ("boss".equals(how) && !here && this.pr != null && this.pr.isValid()) this.pr.sendMessage(@MSG@.raw("[Gear] The boss dropped a Zone " + this.z + " Mythic bag for you - you left its world, it lies where the boss fell.").color(@PKG@.GearDefs.C_GOLD));
  } catch (Throwable tm) { }
}""")
# called from GearDeathMark for a death DropDeathItems handles this tick (the harness seam GearLoot.SPAWN gets the bags instead of the task)
M(gpack, r"""
public static int bossRoll(@ACH@ chunk, int idx, @ST@ store, @CB@ cb, @DTHC@ dc, @NPCE@ npc, @VEC@ p, String wk) {
  if (!@PKG@.GearCfg.PACK_ON || !(@PKG@.GearCfg.BOSS_MY > 0.0) || p == null || npc == null) return 0;
  if (chunk.getComponent(idx, @PLA@.getComponentType()) != null) return 0;
  java.util.function.Function f = @PKG@.Gear.fn("mob:fn:boss");
  if (f == null) return 0;
  @HRC@ hr = (@HRC@) chunk.getComponent(idx, @HRC@.getComponentType());
  if (hr == null) return 0;
  @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
  java.util.UUID nu = uc == null ? null : uc.getUuid();
  if (nu == null) return 0;
  String role = null;
  try { role = npc.getRoleName(); } catch (Throwable tr) { role = null; }
  if (role == null || role.length() == 0) return 0;
  Object r = f.apply(new Object[] { wk, nu, role, Double.valueOf(p.x), Double.valueOf(p.y), Double.valueOf(p.z) });
  if (!(r instanceof Object[])) return 0;
  long now = System.currentTimeMillis();
  @PKG@.GearLoot.prune(now);
  if (@PKG@.GearLoot.ROLLED.putIfAbsent("boss:" + nu, Long.valueOf(now)) != null) return 0;
  Object[] a = (Object[]) r;
  int z = a.length > 0 && a[0] instanceof Integer ? ((Integer) a[0]).intValue() : 0;
  @PKG@.GearPool.bcount(0, 1L);
  if (z < 1 || z > 9) {
    @PKG@.GearPool.bcount(4, 1L);
    @PKG@.GearLog.line("LOOT boss " + role + " " + wk + " " + Math.round(p.x) + " " + Math.round(p.y) + " " + Math.round(p.z) + " - zone unknown, no Mythic roll");
    return 0;
  }
  if (a.length > 2 && a[2] instanceof String[] && ((String[]) a[2]).length == 0)
    @PKG@.GearLog.line("LOOT boss " + role + " zone " + z + " - SkyyMobs credited nobody, the killer rolls");
  java.util.ArrayList prs = rollers(a, dc, store);
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.ArrayList lp = new java.util.ArrayList();
  StringBuilder sb = new StringBuilder();
  String fam = family(role);
  for (int i = 0; i < prs.size(); i++) {
    @PR@ pr = (@PR@) prs.get(i);
    if (!firstOfFight(pr.getUuid(), fam, now)) { @PKG@.GearPool.bcount(6, 1L); continue; }          // critic fix 4: one roll per fight (phases)
    @PKG@.GearPool.bcount(1, 1L);
    if (!(@PKG@.GearRoll.RNG.nextDouble() * 100.0 < @PKG@.GearCfg.BOSS_MY)) continue;
    @IS@ bag = mythicBag(z, @PKG@.GearLoot.lean(pr.getUuid()));
    if (bag == null) { @PKG@.GearPool.bcount(3, 1L); continue; }
    // critic fix 5: a Mythic boss bag is NOT under the hourly extra-bag cap (loot.mob.capPerHour) - the once-per-fight rule limits it
    l.add(bag);
    lp.add(pr);
    sb.append(' ').append(pr.getUsername()).append('=').append(@PKG@.GearUnid.logText(bag));
  }
  if (l.isEmpty()) return 0;
  @VEC@ at = new @VEC@(p);
  at = at.add(0.0, 1.0, 0.0);
  java.util.function.BiFunction seam = @PKG@.GearLoot.SPAWN;
  @WLD@ w = null;
  try { Object ext = store.getExternalData(); if (ext instanceof @EST@) w = ((@EST@) ext).getWorld(); } catch (Throwable tw) { w = null; }
  java.util.ArrayList ground = new java.util.ArrayList();
  for (int i = 0; i < l.size(); i++) {
    if (seam != null) seam.apply(l.get(i), at);
    else if (w != null) w.execute(new @PKG@.GearPackGive((@PR@) lp.get(i), (@IS@) l.get(i), store, at, new @RTF@(hr.getRotation()), z));
    else ground.add(l.get(i));
  }
  if (!ground.isEmpty()) {
    @HLDR@[] hs = @ITC@.generateItemDrops(store, ground, at, new @RTF@(hr.getRotation()));
    if (hs != null && hs.length > 0) cb.addEntities(hs, @ADDR@.SPAWN);
  }
  @PKG@.GearPool.bcount(2, (long) l.size());
  @PKG@.GearLog.line("LOOT boss " + role + " zone " + z + " " + wk + " " + Math.round(p.x) + " " + Math.round(p.y) + " " + Math.round(p.z) + " -> " + l.size() + " Mythic bag(s):" + sb.toString() + (seam != null ? " (test seam)" : ""));
  return l.size();
}""")
G319_CLASSES = G319_EARLY + [gpack, gpgv]

''')
# GearDeathMark: the boss roll next to the extra mob roll (its own switch)
rep('''    if (!@PKG@.GearCfg.PART_DROPS && !@PKG@.GearCfg.LOOT_MOB) return;''',
    '''    if (!@PKG@.GearCfg.PART_DROPS && !@PKG@.GearCfg.LOOT_MOB && !@PKG@.GearCfg.PACK_ON) return;          // 0.3.19: + the boss roll''')
rep('''      try { @PKG@.GearLoot.mobRoll(chunk, idx, store, cb, dc, p, lvl, wk); }
      catch (Throwable tl) { @PKG@.Gear.warnOnce("mobroll", "extra mob drop failed: " + tl); }
    }
''', '''      try { @PKG@.GearLoot.mobRoll(chunk, idx, store, cb, dc, p, lvl, wk); }
      catch (Throwable tl) { @PKG@.Gear.warnOnce("mobroll", "extra mob drop failed: " + tl); }
    }
    if (@PKG@.GearCfg.PACK_ON) {          // 0.3.19: a boss (SkyyMobs mob:fn:boss) rolls Mythic pack bags for its credited players
      try { @PKG@.GearPack.bossRoll(chunk, idx, store, cb, dc, npc, p, wk); }
      catch (Throwable tb) { @PKG@.Gear.warnOnce("bossroll", "boss Mythic drop failed: " + tb); }
    }
''')

# review M1: a rolled gear input is never consumed by a pack swap / upgrade recipe (CraftRecipeEvent$Pre; Creative still crafts)
rep('''    @CRR@ rc0 = e.getCraftedRecipe();
    @MQ@ po0 = rc0 == null ? null : rc0.getPrimaryOutput();
    String id0 = po0 == null ? null : po0.getItemId();
''', '''    @CRR@ rc0 = e.getCraftedRecipe();
    @MQ@ po0 = rc0 == null ? null : rc0.getPrimaryOutput();
    String id0 = po0 == null ? null : po0.getItemId();
    if (rc0 != null && @PKG@.GearPackId.salvage(rc0)) {          // critic round 2 (Skyy 2026-10-17 "Yes, Requip only"): no Salvagebench recipe eats a dropped pack piece
      @REF@ rv = chunk.getReferenceTo(idx);
      @PLA@ pv = rv == null ? null : (@PLA@) st.getComponent(rv, @PLA@.getComponentType());
      String vv = pv == null || pv.getGameMode() == @GM@.Creative ? null : @PKG@.GearPack.salvVeto(rc0, pv.getInventory());
      if (vv != null) {
        e.setCancelled(true);
        @PR@ prv = (@PR@) st.getComponent(rv, @PR@.getComponentType());
        if (prv != null) prv.sendMessage(@MSG@.raw("[Gear] " + vv).color(@PKG@.GearDefs.C_BAD));
        @PKG@.GearLog.line("CRAFT-BLOCK-SALVAGE " + (prv == null ? "?" : prv.getUsername() + " " + prv.getUuid()) + " recipe " + rc0.getId());
        return;
      }
    }
    if (id0 != null && @PKG@.GearPackId.special(id0) && !@PKG@.GearPackId.sameSet(rc0, id0)) {          // critic fix 1 (Skyy 2026-10-17 "Block craft")
      @REF@ rm = chunk.getReferenceTo(idx);
      @PLA@ pm = rm == null ? null : (@PLA@) st.getComponent(rm, @PLA@.getComponentType());
      if (pm == null || pm.getGameMode() != @GM@.Creative) {
        e.setCancelled(true);
        @PR@ prm = rm == null ? null : (@PR@) st.getComponent(rm, @PR@.getComponentType());
        boolean myth = @PKG@.GearPackId.ROLE[@PKG@.GearPackId.idx(id0)] == 2;
        if (prm != null) prm.sendMessage(@MSG@.raw("[Gear] " + @PKG@.Gear.itemName(id0) + (myth ? " is a Mythic boss drop - it is not crafted here. Bosses drop Mythic bags of their zone." : " is an Untiered piece - it is never crafted.")).color(@PKG@.GearDefs.C_BAD));
        @PKG@.GearLog.line("CRAFT-BLOCK-PACK " + (prm == null ? "?" : prm.getUsername() + " " + prm.getUuid()) + " " + id0 + " recipe " + rc0.getId());
        return;
      }
    }
    if (id0 != null && @PKG@.GearPackId.swap(rc0, id0)) {          // 0.3.19 review M1: never erase a rolled piece in a pack swap / upgrade
      @REF@ rs = chunk.getReferenceTo(idx);
      @PLA@ ps = null;
      if (rs != null) ps = (@PLA@) st.getComponent(rs, @PLA@.getComponentType());
      String sv = null;
      if (ps != null && ps.getGameMode() != @GM@.Creative) sv = @PKG@.GearPack.swapVeto(rc0, id0, ps.getInventory());
      if (sv != null) {
        e.setCancelled(true);
        @PR@ prs = (@PR@) st.getComponent(rs, @PR@.getComponentType());
        if (prs != null) prs.sendMessage(@MSG@.raw("[Gear] " + sv).color(@PKG@.GearDefs.C_BAD));
        @PKG@.GearLog.line("CRAFT-BLOCK-SWAP " + (prs == null ? "?" : prs.getUsername() + " " + prs.getUuid()) + " " + id0 + " recipe " + rc0.getId());
        return;
      }
    }
''')
# review M2: no Smithing craft XP for pack pieces (their recipes are their economy - cheap colourways would pay full tier XP)
rep('''      @PKG@.GearRoll.payCraft(u, this.id, got.toString(), this.pr.getUsername());''',
    '''      if (!@PKG@.GearPackId.has(this.id)) @PKG@.GearRoll.payCraft(u, this.id, got.toString(), this.pr.getUsername());          // 0.3.19 review M2: no XP for pack pieces''')

# ================================================================================================================ 10: critic fixes on 0.3.18 code (local rebuild)
# critic fix 1: a UT / Mythic table piece their chests / mobs drop is a plain Normal piece (never a bag, never a rolled rarity)
rep(r'''M(grl, "public static @BD@ unidDoc(String id, int col, String src) { return newDoc(id, pickRarity(col), false, src); }")''',
    r'''M(grl, "public static @BD@ unidDoc(String id, int col, String src) { if (@PKG@.GearPackId.special(id)) return newDoc(id, 0, true, src); return newDoc(id, pickRarity(col), false, src); }")          # critic fix 1: a UT / Mythic table piece found = plain Normal''')
rep(r'''  if (@PKG@.GearMine.isPiece(id) || @PKG@.GearGArm.index(id) >= 0) return null;        // 0.2.15: gathering armor never drops unidentified (0.3.6: + the new sets)
''',
    r'''  if (@PKG@.GearMine.isPiece(id) || @PKG@.GearGArm.index(id) >= 0) return null;        // 0.2.15: gathering armor never drops unidentified (0.3.6: + the new sets)
  if (@PKG@.GearPackId.special(id)) return null;          // critic fix 1: a UT / Mythic table piece = no bag (GearTag.unid -> GearRoll.unidDoc = plain Normal)
''')
rep(r'''  if (@PKG@.GearPool.typeOfId(s0.getItemId()) < 0) return 0;
''',
    r'''  if (@PKG@.GearPool.typeOfId(s0.getItemId()) < 0) return 0;
  if (@PKG@.GearPackId.special(s0.getItemId())) return 0;          // critic fix 1: no bags of a UT / Mythic table piece
''')
# critic fix 2: SkyySacks /craft (gear:fn:roll mode 8): a UT / Mythic row or a swap recipe = plain Normal, no Smithing XP for pack pieces
rep(r'''      Object[] out = new Object[n];
      StringBuilder gx = new StringBuilder();
      for (int i = 0; i < n; i++) {
        @BD@ d = craft ? @PKG@.GearRoll.craftDoc(id, u, lv) : @PKG@.GearRoll.newDoc(id, @PKG@.GearData.isGear(id) ? @PKG@.GearRoll.pickRarity(0) : 0, true, src);''',
    r'''      Object[] out = new Object[n];
      StringBuilder gx = new StringBuilder();
      boolean plain = @PKG@.GearPackId.plainCraft(id, a.length > 4 ? a[4] : null);          // critic fix 2: no fresh roll for a swap / UT / Mythic output
      for (int i = 0; i < n; i++) {
        @BD@ d = plain ? (lv >= 0 ? @PKG@.GearRoll.newDoc(id, 0, true, src, lv) : @PKG@.GearRoll.newDoc(id, 0, true, src))
          : (craft ? @PKG@.GearRoll.craftDoc(id, u, lv) : @PKG@.GearRoll.newDoc(id, @PKG@.GearData.isGear(id) ? @PKG@.GearRoll.pickRarity(0) : 0, true, src));''')
rep(r'''        @PKG@.GearRoll.payCraft(u, id, gx.toString(), "/craft");''',
    r'''        if (!@PKG@.GearPackId.has(id)) @PKG@.GearRoll.payCraft(u, id, gx.toString(), "/craft");          // critic fix 2: no XP for pack pieces''')
rep(r'''      return Boolean.valueOf(@PKG@.GearSmith.shows(u, (String) a[1], u == null || @PKG@.GearSmith.showAll(u)));''',
    r'''      if (@PKG@.GearPackId.special((String) a[1])) return Boolean.FALSE;          // critic fix 2: a UT / Mythic table piece is never offered
      return Boolean.valueOf(@PKG@.GearSmith.shows(u, (String) a[1], u == null || @PKG@.GearSmith.showAll(u)));''')
# critic fix 6: GearPool.table is rebuilt on a config epoch or item-count change only (no 60 s expiry); t[9] = the item count
rep(r'''  if (t != null && ((Long) t[0]).longValue() == ep && now - ((Long) t[1]).longValue() < 60000L && now >= ((Long) t[1]).longValue()
      && ((Integer) t[5]).intValue() == top && ex.equals(t[6])) return t;''',
    r'''  int ic = -1;
  try { ic = @ITM@.getAssetMap().getAssetMap().size(); } catch (Throwable x0) { ic = -1; }
  if (t != null && ((Long) t[0]).longValue() == ep && t.length > 9 && ((Integer) t[9]).intValue() == ic
      && ((Integer) t[5]).intValue() == top && ex.equals(t[6])) return t;          // critic fix 6: the config epoch / the item count, no 60 s expiry''')

# ================================================================================================================ 9: Void Charms wording
# Skyy 2026-10-17: "i noticed they are still called accessory's in the settings" (model: tools/accessories_0_5_24_patch.py)
rep('''accessory in your Accessory Bag - or craft it at a "''', '''accessory in your Void Charms - or craft it at a "''')
rep('''"Identifying needs an Appraisal Tool, but the Accessory Bag is not loaded."''', '''"Identifying needs an Appraisal Tool, but Void Charms is not loaded."''')
rep('''"Identifying needs an Appraisal Tool accessory in your Accessory Bag."''', '''"Identifying needs an Appraisal Tool accessory in your Void Charms."''')
rep('''" (Accessory Bag)"''', '''" (Void Charms)"''')
rep('''"Identify: needs an Appraisal Tool (the Accessory Bag is not loaded)"''', '''"Identify: needs an Appraisal Tool (Void Charms is not loaded)"''')

# ================================================================================================================ the jar: classes + manifest
rep('''+ G317_CLASSES + G318_CLASSES''', '''+ G317_CLASSES + G318_CLASSES + G319_CLASSES''')
rep('''the hoe area tills everywhere; Server Setup -> Gear.''', '''the hoe area tills everywhere; PACK DROPS: The Armory's armor and weapons (by LadyPaladra, CC BY-NC - credit, never sold; install it from its CurseForge page) are gear and drop from levelled mobs inside mystery bags with SkyyGear's rarity, level and modifiers, picked by set (only reacting to its item ids - none of its files are copied), and bosses (with SkyyMobs 0.1.10) drop Mythic bags of their zone's Mythic pack sets; Server Setup -> Gear.''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i('gpid = mk("GearPackId")') < _i("public static boolean isGearMs(") < _i("public static boolean isGear(String id) {")
assert _i('gpid = mk("GearPackId")') < _i("public static String kindFor(") and _i('gpid = mk("GearPackId")') < _i("public static int level(String id, @BD@ d)")
assert _i("public static String[] strs(") < _i("public static final String[] ID = strs(") and _i("public static int[] ints(") < _i("public static final int[] SET = ints(")
assert _i("public static String[] catS(") < _i("public static final String[] P_ID = catS(") and _i("public static int[] fill(") < _i("public static final int[] P_ZONE = fill(")
assert _i("public static int liveType(int i)") < _i("public static double w(Object[] t, int i)") < _i("public static Object[] table()") < _i("public static boolean match(Object[] t, int i, int ty, int at, int L)")
assert _i("public static boolean match(Object[] t, int i, int ty, int at, int L)") < _i("public static int typeOfId(String id)")
assert _i("public static boolean matchM(") < _i("public static boolean[] levelsM(") < _i("public static int[] rangeM(") < _i("public static String pickItemM(") < _i("public static int pickTypeM(")
assert _i("public static int pickTypeM(") < _i("public static int[] pickArmM(") < _i('gpack = mk("GearPack")') and "pickAtM" not in s
assert _i("public static int pickTypeM(") > _i("public static boolean leanHit(") and _i("public static synchronized String packText()") < _i("public static synchronized String countsText()")
assert _i("public static int pz(@BD@ d)") < _i("public static @MSG@ descMsg(@BD@ d)") and _i("public static @IS@ makeZ(") < _i("public static @IS@ make(int ty")
assert _i("public static @IS@ make(int ty") < _i("public static @IS@ roll(int L") and _i("public static Object[] pickZ(") < _i("public static Object[] pick(int ty") < _i("public static Object[] open(@BD@ d")
assert _i("public static int[] rangeM(") < _i("public static String why(@BD@ d)")
assert _i('gpack = mk("GearPack")') > _i("public static synchronized String countsText()") and _i("public static int bossRoll(") < _i("public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {")
assert _i("public static @IS@ mythicBag(") < _i("public static java.util.ArrayList rollers(") < _i("public static int bossRoll(")
assert s.count("pickZ(type(b), at(b), rar(b), lo(b), hi(b), rerolls(b) + 1, by, pz(b))") == 2 and s.count(" pick(type(") == 0
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.18 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.18 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
