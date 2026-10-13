"""Derive SkyySacks/build_skyysacks_0.8.0.py from the SET pin 0.7.18 (the GENERATED build_skyysacks_0.7.18.py; edit THIS file, then
regenerate: python tools/sacks_0_8_0_patch.py; never re-run sacks_0_7_18_patch.py on top of it).
Run:  python tools/sacks_0_8_0_patch.py   then   python SkyySacks/build_skyysacks_0.8.0.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.0.py

0.8.0 = BAGS V2, shown to players as SkyyVoid (research/Bags-v2-Spec.md; docs/answered/bags.md 2026-10-10: REQUEST Bags v2, LOCKED popups
"Convert + refund", "Item limit per category", "Becomes 'Omni' rarity", LOCKED name "SkyyVoid (Recommended)"; docs/answered/ui.md
2026-10-10: "move the amount to above the withdraw button and make the number there work for all actions", "Move to Void", no Split).
Skyy: "i have an idea for the bags! ..." + "SkyySack isnt a great name any more ..." + "work through your whole list, so everything is
ready to play when i get off work."
The internal id stays SkyySacks (jar, data folder Skyy_SkyySacks, bridge keys sacks:*, world-config key); players see "SkyyVoid" /
"The Void" / "Void Storage". Base = 0.7.18 (private pool writer, no idle hops, inventory-change sweep gating - all KEPT unchanged).

WHAT CHANGES (spec section numbers):
 1  CATEGORIES (1.1): six - Mining, Foraging, Farming, Fishing (new: Fish_* and Food_Fish_Raw* leave Farming), Combat, Smithing;
    Ingredient_Crystal_* joins Mining. SackDefs.CATS = the six; the five legacy bag types stay in SackDefs.LCATS (old bag ids parse).
 2  NO CARRIED BAG ANY MORE (1.2, question 1 default "opener only"): every category is always reachable - sweep, withdraw, refill,
    Requip top-up, the bench / pocket / craft mirror, the Bazaar bridges. SweepTask.caps(inv) now answers "every category" (its
    callers only ask containsKey); the CAPACITY comes from VoidStore.capsK(u, k) / capsBest(k).
 3  STORAGE LEVEL (2.1): level = 1 + floor(sqrt(total / step)), capped at pd.maxLevel; total = SkyyCollections coll:fn:catTotal
    {UUID, category} (0.2.9+), else the Void's own intake count (pd own.<Cat>, counted only while coll:fn:catTotal is missing). The best
    level ever reached is saved (pd best.<Cat>): the shown level never goes down (counts lowered, Collections gone, step raised).
 4  CAPACITY (2.2) = level x pd.perLevel x the rarity multiplier, ONE total for all items of a category (Normal 1 / Unique 1.5 / Rare 2 /
    Legendary 3 / Omni 5). The sweep, Deposit all, the Deposit button and sacks:fn:deposit take only what fits (category room);
    taking out always works; lowering a setting never deletes anything (over-limit pools stay, intake waits).
 5  RARITY UPGRADE (2.3): the page's Upgrade box: level gate (pd.gate.*) + the item cost (pd.cost.<Cat>.<Rarity>), paid from the Void
    first, then the inventory, all or nothing, after a confirm step. The click carries the rarity it upgrades FROM (upgok:<i>:<from>),
    so a double click / a second click in the same tick charges once. Omni = automatic once all six are Legendary (pd.omniAuto, on);
    off = /pdadmin omni <player>. Fishing costs use fish a trap gives (Food_Fish_Raw_Rare / _Epic are never made in survival - the
    Bazaar build says so): DECISION below.
 6  THE PAGE (3.1): one Void page (kit pieces, 1300 x 690 like before + the player inventory window): six category tabs on the left
    (rarity colour, "Lv N", a fill bar), header "Mining - Lv 14 - Rare (x2.0)", storage + level bars, an amber over-limit line, the
    36-cell grid WITH paging (click selects), the action panel: ONE amount box ABOVE Withdraw used by every action (Withdraw, Deposit;
    empty = a stack / all), Pick up all, Deposit all, the Upgrade box with cost cells (have / need, green / red), the stack refill row,
    Craft. No Split (Skyy's answer).
 7  MIGRATION "Convert + refund" (4): per PROFILE KEY, run once (pd v2.first marker), History FIRST (pools/<k> + processing/<k> copied to
    history/<k>-<stamp>/ and read back byte for byte on the writer thread; no verified copy = no migration, retried, WARN once).
    Legacy bags found in a settled profile's storage / hotbar / backpack (join, any sweep, a picked-up bag) are converted, BEST FIRST
    (the Omni, then Legendary .. Normal - the slot order never matters): the best bag of a type sets that category's rarity (max; the
    first bag of a type at the current rarity counts as used too - a lone Normal bag just becomes the Normal start), the Farming bag
    also sets Fishing, the first Omni bag ever = Omni; every OTHER bag is REFUNDED - a second bag of a type, a bag below the rarity the
    category already has, any typed bag once the Void is (or becomes) Omni, every further Omni bag - its whole crafting chain goes into
    the Void (Normal 20 Fibre + 4 Sticks, + 6 Linen / Shadoweave / Cindercloth Scraps per step, an extra Omni = 5 Legendary chains;
    refunds may go over the limit). "Used" counts the journal of every earlier run too, so a bag found later never re-buys a rarity.
    CRASH SAFETY (the journal pd/<k>.journal, fsync per line): C|seq|bag|qty|n0|R-or-F|time|refund is written BEFORE the bag leaves
    its slot; the CREDIT (rarity or refund) is applied only once the removal is durable = 30 s later (three engine player-save ticks,
    the SkyyProfiles marker rule) by the writer thread, then D|seq. Until then a pending R already counts for capacity / the page.
    After a crash: an unsettled C whose bag count in the inventory is still >= n0 came back with the inventory rollback -> X|seq, the
    bag converts again; a lower count = the removal was saved -> the credit is applied now. A refund is idempotent: its seq is stored
    INSIDE the same atomic pool file write (meta key "~v2paid", non-numeric value - SkyySacks 0.7.18 skips and drops it), so a crash
    between the pool write and D never pays twice. Result: every bag = exactly one rarity credit or one refund, never both, never none.
    One INFO log line + one chat line per profile, one migration.log line with the Undo steps.
 8  /pd gives a Pocket Dimension (Skyy_Sack_Pocket, the Omni bag's violet look, opener only - losing it loses nothing) when the player
    has none; every profile gets one at its first v2 login (a full inventory = a chat line: make room, then /pd).
 9  The 21 old bag ids stay DEFINED (no unknown items anywhere), without recipes, tooltip "Old Magic Bag - turns into Pocket Dimension
    rarity when you pick it up". KnowSync forgets its own 21 managed recipe ids (wanted = empty; only those 21 entries).
 10 Bridges: NEW sacks:v2 = Boolean.TRUE (SkyyCollections 0.2.9+ hides bag rewards), sacks:fn:pd (UUID -> Object[] of
    {String cat, Integer level, String rarity, Long cap, Long stored}), sacks:fn:catOf (String -> String). Unchanged shapes:
    sacks:fn:count / all / take / put / commit / deposit / pocketFill / craftList / craftHave / craftPay / craftRefund / craftCommit
    (the bag gate is gone; deposit respects the category limit). sacks:freebags is no longer written (it stays whatever it was).
 11 Server Setup ("SkyyVoid and Crafting"): pd.perLevel, pd.maxLevel, pd.step.<Cat> x6, pd.mult.<Rarity> x5 (asks before an out-of-order
    ladder), pd.gate.<Rarity> x3, pd.cost.<Cat>.<Rarity> x18 (text "itemId:qty,..."; unknown ids refused), pd.omniAuto. The retired
    bag.small / medium / rare / large / omni and bags.freeRecipes rows are gone from the page; their lines stay in the file, unread
    (no rewrite - no config migration needed).
 12 /pdadmin legacybags <player> (admin, skyysacks.admin): gives back the bags the journal removed on that player's ACTIVE profile and
    that turned into RARITY (refunded bags are not given back - their refund is in the pool); each given bag leaves a token (its
    journal G line; a re-conversion that uses it is a "tok" C line - fix round 2: tokens live in the journal only, crash-proof) so a later
    re-conversion of it gives no second credit, and the profile is HELD (pd v2.hold: its old bags stay bags).
    /pdadmin legacybags all = the server-wide hold (pd/_legacybags-all.flag, survives a restart): no old bag converts, and every profile
    gets its rarity bags back at its next sweep (offline players when they next join). /pdadmin resume <player>|all ends a hold.
    /pdadmin omni <player>: Omni for the active profile.
FIX ROUND (critic findings): the Undo line never restores the History copy over a used pool; legacybags all + the hold (above); VoidState
collections concurrent, the pending list lock-free (no world-thread wait on an fsync); one fsync per old-bag stack; an extra Omni bag on an
Omni Void is refunded; the upgrade saves rarity + pool in one writer job; without SkyyCollections a Withdraw + Deposit loop no longer
raises the level; the History copy flushes the live pool first; page actions match the "a" field exactly and every page event carries the
amount box; upgrade costs 1..6 items (= the 6 cells); a level gate above pd.maxLevel acts as the max level (checkGate asks first);
the Furnace / Tannery / craft chat lines say [SkyyVoid].
FIX ROUND 2 (second critics): legacybags all also takes the Pocket Dimension out of storage / hotbar / backpack (0.7.18 does not know it;
no gift and no /pd item while the hold is on; resume all gives it back once); resume all ends the holds of profiles not loaded at the
time (pd/_resume-all.stamp vs v2.holdAt); an Omni bag on a Void that is Omni through six Legendary (Omni auto) is refunded; give-back
tokens are derived from the journal (G lines minus live "tok" C lines - a failed journal write, short removal or crash never spends or
doubles one); a refund retried after a failed pool write is saved + read back before D; the History copy holds up the sweep only while
an old bag is in the inventory; the welcome + Pocket chat lines are one line; Server Setup rows, config comments, /craft page and bench
queue lines say "the Void"; the amount box hint says what an empty box does for Deposit.

TEST SEAMS (no effect in the game): VoidStore.CRASHAT / CRASHN (null in the game) = the harness's crash point for the crash-at-every-step
proof; SacksPage.onEvent(ref, store, player, data) = handleDataEvent with the Player component already looked up (the harness drives it).

DECISIONS (Skyy may change any of them):
 - Fishing upgrade costs: Unique 100 Raw Fish; Rare 500 Raw Fish + 50 Bluegill; Legendary 1,500 Raw Fish + 150 Catfish + 150 Minnow
   (the spec's Rare / Epic Raw Fish are never made in survival). All costs are Server Setup rows.
 - The Pocket item is the Omni bag's look with its own quality "Void" (#cc66cc, the Mythic texture set).
 - The credit of a converted bag waits 30 s (crash safety); the page counts a pending rarity at once.
 - /pdadmin acts on the target's ACTIVE profile only (like every profile-keyed admin tool).
 - Bags in the journal that turned into a REFUND are never given back by /pdadmin legacybags.
ROLLBACK to 0.7.18: no item is lost. Pool files keep their format (+ one "~v2paid" meta line 0.7.18 ignores and drops). The pd/ and
history/ folders and migration.log are ignored by 0.7.18. Converted bags are gone from inventories, so on 0.7.18 a player needs a bag of
that type again to reach a pool (the recipes come back: SkyyCollections shows bag rewards again once sacks:v2 is gone) - BEFORE rolling
back run /pdadmin legacybags all, keep 0.8.0 running until migration.log has a "legacybags all: N old bag(s) given back" line for each
profile that matters (offline players get theirs when they join), then roll back. Under legacybags all each profile's Pocket Dimension also leaves its storage / hotbar /
backpack at that sweep ("N Pocket Dimension item(s) removed" line); a Pocket item a player put in a chest or dropped stays an unknown item
on 0.7.18 (nothing is stored in it - it can be thrown away). Use "all" for a rollback: under /pdadmin legacybags <player> only that
profile is held, and a given-back bag passed to a profile that is not held converts there as rarity. A profile that never joined in that window has no bag
on 0.7.18, but loses nothing for good: its pool is intact and rolling forward again restores its rarity from pd/ (no second credit).
FLOOR (tools/deploy_set.py, main session): never below SkyySacks 0.8.0 once it ran, except after /pdadmin legacybags all as above;
SkyyBazaar 0.1.9 needs SkyySacks 0.8.0.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.18.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.0.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def cut(start, end, new, keep_end=True):
    """replace the text from `start` (included) up to `end` (kept when keep_end) with `new`; both anchors unique"""
    global s
    assert s.count(start) == 1, "cut start anchor count %d: %s" % (s.count(start), start[:120])
    i = s.index(start)
    j = s.index(end, i + len(start))
    assert s.count(end) >= 1
    s = s[:i] + new + (s[j:] if keep_end else s[j + len(end):])


def T(x):
    """the patch texts below are RAW strings (what you read is what the build script gets); QQQ stands for three single quotes"""
    return x.replace("QQQ", "'" * 3)


assert 'VERSION = "0.7.18"' in s and "SackInvSys" in s and "VoidStore" not in s, "the source must be the generated 0.7.18 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
MAKE0 = s.count("pool.makeClass(")

# ================================================================================================= header + version
rep(T(r'''the 10 s save - the never-dupe direction); the parsed coll:recipes set is cached by coll:epoch. No behaviour
change; saved data, bridge keys and assets are 0.7.17's. Details: the patch docstring.
"""'''), T(r'''the 10 s save - the never-dupe direction); the parsed coll:recipes set is cached by coll:epoch. No behaviour
change; saved data, bridge keys and assets are 0.7.17's. Details: the patch docstring.
0.8.0 (derived from 0.7.18 by tools/sacks_0_8_0_patch.py - edit the patch, not this file; research/Bags-v2-Spec.md): BAGS V2, shown to
players as SkyyVoid - ONE Pocket Dimension, six categories (Fishing new, crystals in Mining), no carried bag needed, a storage LEVEL per
category from the items collected (SkyyCollections coll:fn:catTotal), a RARITY per category raised by the Upgrade button (level gate +
item cost), capacity = level x 100 x the rarity multiplier as one item limit per category, Omni once all six are Legendary; the
Void page with the amount box above Withdraw; old Magic Bags convert once per profile (best bag wins, extra bags refunded) with a
History copy first, a journal and a 30 s credit delay (crash safe); /pdadmin legacybags | omni; new bridge keys sacks:v2, sacks:fn:pd,
sacks:fn:catOf. 0.7.18's private writer, idle-hop gating and inventory-change sweeps are kept. Details: the patch docstring.
"""'''))
rep('VERSION = "0.7.18"', 'VERSION = "0.8.0"')

# ================================================================================================= the Bags v2 tables (Python)
rep(T(r'''SMITH_JAVA = " || ".join('''), T(r'''# ================= 0.8.0 BAGS V2 (research/Bags-v2-Spec.md) - the six categories, levels, rarities, costs, refunds =================
# PD_CATS = the Void categories (tab order, spec 3.1); the five legacy bag types (BAG_CATS) stay for the old bag ids, their item JSONs and
# the migration. PD_HOLDS = what each category takes (spec 1.1). All numbers are PLACEHOLDER Server Setup rows (spec 2.4).
PD_CATS = ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing")
assert set(BAG_CATS) < set(PD_CATS) and len(PD_CATS) == 6
PD_HOLDS = {"Mining": "ore, rubble, rock, soil and crystals",
            "Foraging": "logs, planks, sticks, fibre, bark and tree sap",
            "Farming": "plants, raw food and life essence",
            "Fishing": "fish and raw fish",
            "Combat": "bones, feathers, essences, venom sacs, chitin, voidhearts and boom powder",
            "Smithing": "bars and ingots, leather, hides, cloth bolts, fabric scraps, leather straps, iron studs and charcoal"}
assert set(PD_HOLDS) == set(PD_CATS)
PD_RAR = ("Normal", "Unique", "Rare", "Legendary", "Omni")
PD_RCOL = ("#ffffff", "#ffff55", "#ff55ff", "#55ffff", "#cc66cc")      # = BAG_RARITY page colours (Omni = the Mythic #cc66cc)
assert list(PD_RCOL[:4]) == [r[3] for r in BAG_RARITY[:4]] and PD_RCOL[4] == BAG_RARITY[-1][3]
PD_STEP = {"Mining": 25, "Foraging": 20, "Farming": 25, "Fishing": 2, "Combat": 8, "Smithing": 10}
PD_MULT = (1.0, 1.5, 2.0, 3.0, 5.0)
PD_GATE = (10, 25, 50)            # the level gate of the step TO Unique / Rare / Legendary
PD_PER_LEVEL, PD_MAX_LEVEL = 100, 250
assert all(PD_MULT[i] < PD_MULT[i + 1] for i in range(4)) and PD_GATE[0] < PD_GATE[1] < PD_GATE[2] <= PD_MAX_LEVEL
# the upgrade costs (spec 2.3; Fishing: DECISION - the trap fish, see the patch docstring); key (category, target rarity 1..3)
PD_COST = {
    ("Mining", 1): [("Rock_Stone_Cobble", 500), ("Ore_Copper", 250), ("Ore_Iron", 100)],
    ("Mining", 2): [("Rock_Stone_Cobble", 2000), ("Ore_Copper", 1000), ("Ore_Iron", 1000), ("Ore_Thorium", 250)],
    ("Mining", 3): [("Rock_Stone_Cobble", 5000), ("Ore_Iron", 2500), ("Ore_Thorium", 1000), ("Ore_Cobalt", 500), ("Ore_Adamantite", 100)],
    ("Foraging", 1): [("Wood_Oak_Trunk", 500), ("Ingredient_Fibre", 500), ("Ingredient_Tree_Sap", 100)],
    ("Foraging", 2): [("Wood_Oak_Trunk", 2000), ("Wood_Maple_Trunk", 1000), ("Wood_Gumboab_Trunk", 500), ("Ingredient_Tree_Sap", 250)],
    ("Foraging", 3): [("Wood_Oak_Trunk", 5000), ("Wood_Maple_Trunk", 2000), ("Wood_Gumboab_Trunk", 1000), ("Wood_Redwood_Trunk", 1000),
                      ("Wood_Sallow_Trunk", 500), ("Ingredient_Tree_Sap", 500)],
    ("Farming", 1): [("Plant_Crop_Wheat_Item", 500), ("Plant_Crop_Lettuce_Item", 250), ("Ingredient_Life_Essence", 100)],
    ("Farming", 2): [("Plant_Crop_Wheat_Item", 2000), ("Plant_Crop_Carrot_Item", 1000), ("Plant_Crop_Cauliflower_Item", 500),
                     ("Ingredient_Life_Essence", 250)],
    ("Farming", 3): [("Plant_Crop_Wheat_Item", 5000), ("Plant_Crop_Carrot_Item", 2000), ("Plant_Crop_Pumpkin_Item", 1000),
                     ("Plant_Crop_Tomato_Item", 1000), ("Plant_Crop_Cotton_Item", 500), ("Ingredient_Life_Essence", 500)],
    ("Fishing", 1): [("Food_Fish_Raw", 100)],
    ("Fishing", 2): [("Food_Fish_Raw", 500), ("Fish_Bluegill_Item", 50)],
    ("Fishing", 3): [("Food_Fish_Raw", 1500), ("Fish_Catfish_Item", 150), ("Fish_Minnow_Item", 150)],
    ("Combat", 1): [("Ingredient_Bone_Fragment", 250), ("Ingredient_Feathers_Light", 100)],
    ("Combat", 2): [("Ingredient_Bone_Fragment", 1000), ("Ingredient_Feathers_Light", 500), ("Ingredient_Sac_Venom", 100),
                    ("Ingredient_Chitin_Sturdy", 100)],
    ("Combat", 3): [("Ingredient_Bone_Fragment", 2500), ("Ingredient_Feathers_Light", 1000), ("Ingredient_Sac_Venom", 250),
                    ("Ingredient_Chitin_Sturdy", 250), ("Ingredient_Void_Essence", 100), ("Ingredient_Voidheart", 10)],
    ("Smithing", 1): [("Ingredient_Hide_Light", 200), ("Ingredient_Fabric_Scrap_Linen", 100), ("Ingredient_Fabric_Scrap_Wool", 100)],
    ("Smithing", 2): [("Ingredient_Hide_Light", 750), ("Ingredient_Hide_Medium", 500), ("Ingredient_Fabric_Scrap_Linen", 250),
                      ("Ingredient_Fabric_Scrap_Shadoweave", 100)],
    ("Smithing", 3): [("Ingredient_Hide_Light", 2000), ("Ingredient_Hide_Medium", 1000), ("Ingredient_Hide_Heavy", 250),
                      ("Ingredient_Fabric_Scrap_Shadoweave", 250), ("Ingredient_Fabric_Scrap_Cindercloth", 100)],
}
assert sorted(PD_COST) == sorted((c, r) for c in PD_CATS for r in (1, 2, 3)) and all(1 <= len(v) <= 6 for v in PD_COST.values())
def pd_cost_text(cat, r):
    return ",".join("%s:%d" % (i, q) for i, q in PD_COST[(cat, r)])
POCKET = "Skyy_Sack_Pocket"           # the one bag item (the opener); Skyy_Sack_ keeps it out of /trade, the AH, Merchants and SkyyGear
POCKET_Q = "Skyy_Bag_Void"            # its own quality: label "Void", the Mythic look (QualityValue 5 < 8, SkyyAuctions' threshold)
# the refund of an extra legacy bag (spec 4.2): its whole crafting chain (Normal 20 Fibre + 4 Sticks, + BAG_UP_QTY scraps per step)
def refund_chain(rank):
    out = {T1_FIBRE: BAG_BOLT_QTY, T1_STICK: BAG_MAT_QTY}
    for i in range(1, rank):
        out[BAG_BOLTS[i]] = out.get(BAG_BOLTS[i], 0) + BAG_UP_QTY
    return out
def refund_text(rank, times=1):
    ch = refund_chain(rank)
    return ",".join("%s:%d" % (i, q * times) for i, q in sorted(ch.items()))
REFUND_BY_RANK = [refund_text(r) for r in (1, 2, 3, 4)] + [refund_text(4, len(BAG_CATS))]   # index rank-1; [4] = an extra Omni
assert REFUND_BY_RANK[0] == "Ingredient_Fibre:20,Ingredient_Stick:4" and "Ingredient_Fabric_Scrap_Cindercloth:6" in REFUND_BY_RANK[3]
def _pd_ids_check():
    """every cost / refund item exists in Assets.zip and a survival player can get it (a drop list - a fish trap state too - or a recipe)"""
    import zipfile, re
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if not os.path.isfile(za):
        print("note: Assets.zip not found - Void cost ids not cross-checked")
        return
    with zipfile.ZipFile(za) as z:
        nm = z.namelist()
        ids = set(os.path.basename(n)[:-5] for n in nm if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        drops = "\n".join(z.read(n).decode("utf-8-sig", "replace") for n in nm if n.startswith("Server/Drops/") and n.endswith(".json"))
        crafted = set()
        for n in nm:
            if n.startswith("Server/Item/Items/") and n.endswith(".json"):
                t = z.read(n).decode("utf-8-sig", "replace")
                if '"Recipe"' in t or '"BlockType"' in t:   # crafted, or a block the world has (logs, cobble: breaking it gives it)
                    crafted.add(os.path.basename(n)[:-5])
            elif n.startswith("Server/Item/Recipes/") and n.endswith(".json"):
                for m in re.findall(r'"ItemId"\s*:\s*"([A-Za-z0-9_]+)"', z.read(n).decode("utf-8-sig", "replace")):
                    crafted.add(m)
    want = sorted(set(i for v in PD_COST.values() for i, _q in v) | set(i for t in REFUND_BY_RANK for i in re.findall(r"([A-Za-z0-9_]+):", t)))
    bad = [i for i in want if i not in ids]
    if bad:
        raise SystemExit("0.8.0: Void cost / refund item(s) not in Assets.zip: " + ", ".join(bad))
    nosrc = [i for i in want if ('"%s"' % i) not in drops and ('"*%s_State' % i) not in drops and i not in crafted]
    if nosrc:
        raise SystemExit("0.8.0: Void cost item(s) no drop list or recipe gives (survival players could never upgrade): " + ", ".join(nosrc))
    print("Void costs: %d upgrade rows, %d distinct items - all in Assets.zip and obtainable; refunds %s" % (len(PD_COST), len(want), REFUND_BY_RANK[:2]))
_pd_ids_check()
SMITH_JAVA = " || ".join('''))

rep(T(r'''FARM_HOLDS_COOKED = "plants, food and cooked dishes, fish and life essence"'''),
    T(r'''FARM_HOLDS_COOKED = "plants, raw and cooked food and life essence"   # 0.8.0: fish moved to the Fishing category'''))

# ================================================================================================= new classes (javassist: classes first)
rep(T(r'''sinv = pool.makeClass(PKG + ".SackInvSys", pool.get(EES))
'''), T(r'''sinv = pool.makeClass(PKG + ".SackInvSys", pool.get(EES))
# 0.8.0 (Bags v2): VoidState = one profile key's Void data (pd/<key>.properties + its journal); VoidStore = the levels, rarities, capacity,
# the migration journal + settle, the upgrade (static); VoidJob = a writer-thread job (History snapshot, pd save); VoidAdminTask = the
# /pdadmin world task; PdAdminCmd = /pdadmin legacybags | omni <player> (admin, extra arguments read like /craft <words>)
vss = pool.makeClass(PKG + ".VoidState")
vst = pool.makeClass(PKG + ".VoidStore")
vjob = pool.makeClass(PKG + ".VoidJob")
vat = pool.makeClass(PKG + ".VoidAdminTask")
vac = pool.makeClass(PKG + ".PdAdminCmd", pool.get(APC))
'''))

# ================================================================================================= Python helpers of the Void config (after jlit)
rep(T(r'''defs = pool.makeClass(PKG + ".SackDefs")
'''), T(r'''# 0.8.0: the Void config rows as Java (SackCfg fields, the int switch helpers, the file loader, the logged signature)
_PD_CFG_FIELDS = (["public static volatile int PD_PER_LEVEL = %d;" % PD_PER_LEVEL, "public static volatile int PD_MAX_LEVEL = %d;" % PD_MAX_LEVEL]
                  + ["public static volatile int PD_STEP_%s = %d;" % (c.upper(), PD_STEP[c]) for c in PD_CATS]
                  + ["public static volatile double PD_MULT_%s = %r;" % (r.upper(), m) for r, m in zip(PD_RAR, PD_MULT)]
                  + ["public static volatile int PD_GATE_%s = %d;" % (PD_RAR[i + 1].upper(), g) for i, g in enumerate(PD_GATE)]
                  + ["public static volatile String PD_COST_%s_%s = %s;" % (c.upper(), PD_RAR[r].upper(), jlit(pd_cost_text(c, r)))
                     for c in PD_CATS for r in (1, 2, 3)]
                  + ["public static volatile boolean PD_OMNI_AUTO = true;"])
def _sw(arg, cases, dflt):
    """a Java if-chain on an int argument (javassist: no switch on Strings; this keeps the int one explicit)"""
    return "".join("  if (%s == %d) return %s;\n" % (arg, i, v) for i, v in cases) + "  return %s;\n" % dflt
_PD_LOAD = ['  PD_PER_LEVEL = intKey(p, "pd.perLevel", %d, 1, 100000);' % PD_PER_LEVEL,
            '  PD_MAX_LEVEL = intKey(p, "pd.maxLevel", %d, 1, 10000);' % PD_MAX_LEVEL]
_PD_LOAD += ['  PD_STEP_%s = intKey(p, "pd.step.%s", %d, 1, 1000000);' % (c.upper(), c, PD_STEP[c]) for c in PD_CATS]
_PD_LOAD += ['  PD_MULT_%s = decKey(p, "pd.mult.%s", %r, 0.1, 100.0);' % (r.upper(), r, m) for r, m in zip(PD_RAR, PD_MULT)]
_PD_LOAD += ['  PD_GATE_%s = intKey(p, "pd.gate.%s", %d, 1, 10000);' % (PD_RAR[i + 1].upper(), PD_RAR[i + 1], g) for i, g in enumerate(PD_GATE)]
for _c in PD_CATS:
    for _r in (1, 2, 3):
        _f = "PD_COST_%s_%s" % (_c.upper(), PD_RAR[_r].upper())
        _k = "pd.cost.%s.%s" % (_c, PD_RAR[_r])
        _PD_LOAD.append('  { String cv = p.getProperty("%s"); if (cv != null && cv.trim().length() > 0) { if (parseCost(cv) != null) %s = cv.trim(); '
                        'else @PKG@.SackPool.warn("config.properties: %s is not itemId:amount pairs - keeping " + %s); } else %s = %s; }'
                        % (_k, _f, _k, _f, _f, jlit(pd_cost_text(_c, _r))))
_PD_LOAD.append('  PD_OMNI_AUTO = boolKey(p, "pd.omniAuto", true);')
_PD_SIG = ' + "," + '.join(["PD_PER_LEVEL", "PD_MAX_LEVEL"] + ["PD_STEP_" + c.upper() for c in PD_CATS] + ["PD_MULT_" + r.upper() for r in PD_RAR]
                           + ["PD_GATE_" + PD_RAR[i].upper() for i in (1, 2, 3)] + ["PD_OMNI_AUTO"])
defs = pool.makeClass(PKG + ".SackDefs")
'''))

# ================================================================================================= SackDefs: six categories, legacy ids
rep(T(r'''defs.addField(CtField.make("public static final String[] CATS = " + _jarr(BAG_CATS) + ";", defs))
defs.addField(CtField.make("public static final String[] MAT = " + _jarr([BAG_MAT[c] for c in BAG_CATS]) + ";", defs))
ITEM_PLURAL = {"Ingredient_Stick": "Sticks"}   # 0.7.15
defs.addField(CtField.make("public static final String[] MATN = " + _jarr([ITEM_PLURAL.get(BAG_MAT[c], ITEM_NAME[BAG_MAT[c]]) for c in BAG_CATS]) + ";", defs))
defs.addField(CtField.make("public static final String[] HOLDS = " + _jarr([BAG_HOLDS[c] for c in BAG_CATS]) + ";", defs))'''),
T(r'''# 0.8.0: CATS = the six Void categories (PD_CATS; tabs, capacity, levels); LCATS = the five legacy bag types (old bag ids only)
defs.addField(CtField.make("public static final String[] CATS = " + _jarr(PD_CATS) + ";", defs))
defs.addField(CtField.make("public static final String[] LCATS = " + _jarr(BAG_CATS) + ";", defs))
defs.addField(CtField.make("public static final String[] MAT = " + _jarr([BAG_MAT.get(c, T1_STICK) for c in PD_CATS]) + ";", defs))
ITEM_PLURAL = {"Ingredient_Stick": "Sticks"}   # 0.7.15
defs.addField(CtField.make("public static final String[] MATN = " + _jarr([ITEM_PLURAL.get(BAG_MAT.get(c, T1_STICK), ITEM_NAME[BAG_MAT.get(c, T1_STICK)]) for c in PD_CATS]) + ";", defs))
defs.addField(CtField.make("public static final String[] HOLDS = " + _jarr([PD_HOLDS[c] for c in PD_CATS]) + ";", defs))
# 0.8.0: the Void rarity ladder (index 0..4 = Normal, Unique, Rare, Legendary, Omni), page colours, the refund of an extra legacy bag
defs.addField(CtField.make("public static final String[] RNAME = " + _jarr(PD_RAR) + ";", defs))
defs.addField(CtField.make("public static final String[] RCOL = " + _jarr(PD_RCOL) + ";", defs))
defs.addField(CtField.make("public static final String[] REFUND = " + _jarr(REFUND_BY_RANK) + ";", defs))
defs.addField(CtField.make("public static final String POCKET = " + jlit(POCKET) + ";", defs))'''))
rep(T(r'''public static int catIndex(String cat) {
  if (cat == null) return -1;
  for (int i = 0; i < CATS.length; i++) if (CATS[i].equals(cat)) return i;
  return -1;
}""", defs))'''), T(r'''public static int catIndex(String cat) {
  if (cat == null) return -1;
  for (int i = 0; i < CATS.length; i++) if (CATS[i].equals(cat)) return i;
  return -1;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int lcatIndex(String cat) {
  if (cat == null) return -1;
  for (int i = 0; i < LCATS.length; i++) if (LCATS[i].equals(cat)) return i;
  return -1;
}""", defs))'''))
rep(T(r'''  if (itemId.startsWith("Ore_") || itemId.startsWith("Rubble_") || itemId.startsWith("Rock_") || itemId.startsWith("Soil_")) return "Mining";
'''), T(r'''  if (itemId.startsWith("Ore_") || itemId.startsWith("Rubble_") || itemId.startsWith("Rock_") || itemId.startsWith("Soil_")) return "Mining";
  // 0.8.0 (Bags v2 spec 1.1): the crystal shards (the Crystal collection) go to Mining
  if (itemId.startsWith("Ingredient_Crystal_")) return "Mining";
'''))
rep(T(r'''  if (itemId.startsWith("Plant_") || itemId.startsWith("Food_") || itemId.startsWith("Fish_")) return "Farming";'''),
    T(r'''  // 0.8.0 (spec 1.1): fish + raw fish fillets (Uncommon / Rare / Epic / Legendary too) are the new Fishing category; grilled fish is cooked food
  if (itemId.startsWith("Fish_") || itemId.startsWith("Food_Fish_Raw")) return "Fishing";
  if (itemId.startsWith("Plant_") || itemId.startsWith("Food_")) return "Farming";'''))
rep(T(r'''  if (p.length != 4 || catIndex(p[2]) < 0) return null;'''), T(r'''  if (p.length != 4 || lcatIndex(p[2]) < 0) return null;   // 0.8.0: the five legacy bag types'''))
rep(T(r'''public static boolean isBag(String id) {
  return bagName(id) != null;
}QQQ), defs))'''), T(r'''public static boolean isBag(String id) {
  return bagName(id) != null;
}QQQ), defs))
# 0.8.0: an OLD bag id -> its rank (1..4 = Normal..Legendary bag of a type, 5 = the Mythic Omni Bag, 0 = not an old bag) and type
defs.addMethod(CtNewMethod.make(jt(rQQQ
public static int legacyRank(String id) {
  if (id == null || !id.startsWith("Skyy_Sack_")) return 0;
  if (id.equals(OMNI)) return 5;
  String[] p = id.split("_");
  if (p.length != 4 || lcatIndex(p[2]) < 0) return 0;
  return tierRank(p[3]);
}QQQ), defs))
defs.addMethod(CtNewMethod.make(jt(rQQQ
public static String legacyCat(String id) {
  if (legacyRank(id) <= 0 || id.equals(OMNI)) return null;
  return id.split("_")[2];
}QQQ), defs))'''))

# ================================================================================================= SackPool: the pool file's meta lines (refund seqs)
rep(T(r'''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SWEPTQ = new java.util.concurrent.ConcurrentHashMap();", sp))
'''), T(r'''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SWEPTQ = new java.util.concurrent.ConcurrentHashMap();", sp))
# 0.8.0: PMETA = key -> (meta key -> String) of the pool file's "~" lines (never items). "~v2paid" = the seqs of the migration refunds
# credited into this pool, written in the SAME atomic file write as the refunded items (a crash can never pay one twice). The value is never
# a number, so SkyySacks 0.7.18 (a rollback) skips the line and drops it at its next save - harmless.
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PMETA = new java.util.concurrent.ConcurrentHashMap();", sp))
'''))
rep(T(r'''      java.util.Enumeration en = p.propertyNames();
      while (en.hasMoreElements()) {
        String k = (String) en.nextElement();
        try { long v = Long.parseLong(p.getProperty(k).trim()); if (v > 0L) m.put(k, Long.valueOf(v)); } catch (Throwable t) { }
      }'''), T(r'''      java.util.Enumeration en = p.propertyNames();
      java.util.concurrent.ConcurrentHashMap mm = null;
      while (en.hasMoreElements()) {
        String k2 = (String) en.nextElement();
        // 0.8.0: a "~" line is pool META (the migration refund seqs), never an item
        if (k2.startsWith("~")) { if (mm == null) mm = new java.util.concurrent.ConcurrentHashMap(); mm.put(k2, p.getProperty(k2)); continue; }
        try { long v = Long.parseLong(p.getProperty(k2).trim()); if (v > 0L) m.put(k2, Long.valueOf(v)); } catch (Throwable t) { }
      }
      if (mm != null) PMETA.put(k, mm);'''))
rep(T(r'''      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);'''), T(r'''      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    java.util.Map mt = (java.util.Map) PMETA.get(k);   // 0.8.0: the meta lines go into the same atomic write
    if (mt != null) {
      java.util.Iterator mi = mt.entrySet().iterator();
      while (mi.hasNext()) { java.util.Map.Entry me = (java.util.Map.Entry) mi.next(); p.setProperty((String) me.getKey(), String.valueOf(me.getValue())); }
    }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);'''))
rep(T(r'''# The ONE gate of every item move between the live inventory and a pool'''), T(r'''# 0.8.0: the migration refund (VoidStore.settle): the items + the seq in ONE pool change (synchronized like add); false = already paid (the
# seq is in "~v2paid") or the pool is not readable (retried by the next settle). paidHas / unpaid = the same ledger (unpaid after D|seq).
sp.addMethod(CtNewMethod.make(jt(rQQQ
public static synchronized boolean paidHas(String k, String seq) {
  java.util.Map mt = (java.util.Map) PMETA.get(k);
  Object v = mt == null ? null : mt.get("~v2paid");
  if (v == null) return false;
  return (" " + String.valueOf(v) + " ").indexOf(" s" + seq + " ") >= 0;
}QQQ), sp))
sp.addMethod(CtNewMethod.make(jt(rQQQ
public static synchronized boolean credit(String k, String seq, java.util.Map items) {
  if (k == null || seq == null || items == null || !ready(k)) return false;
  if (paidHas(k, seq)) return false;
  java.util.Iterator it = items.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    long q = ((Number) e.getValue()).longValue();
    if (q > 0L) add(k, (String) e.getKey(), q);
  }
  java.util.concurrent.ConcurrentHashMap mt = (java.util.concurrent.ConcurrentHashMap) PMETA.get(k);
  if (mt == null) { mt = new java.util.concurrent.ConcurrentHashMap(); PMETA.put(k, mt); }
  Object v = mt.get("~v2paid");
  String paid = v == null ? "" : String.valueOf(v).trim();
  mt.put("~v2paid", (paid.length() == 0 ? "" : paid + " ") + "s" + seq);
  DIRTY.put(k, Boolean.TRUE);
  return true;
}QQQ), sp))
sp.addMethod(CtNewMethod.make(jt(rQQQ
public static synchronized void unpaid(String k, String seq) {
  java.util.concurrent.ConcurrentHashMap mt = (java.util.concurrent.ConcurrentHashMap) PMETA.get(k);
  if (mt == null || seq == null) return;
  Object v = mt.get("~v2paid");
  if (v == null) return;
  String[] parts = String.valueOf(v).trim().split(" ");
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < parts.length; i++) {
    if (parts[i].length() == 0 || parts[i].equals("s" + seq)) continue;
    if (sb.length() > 0) sb.append(' ');
    sb.append(parts[i]);
  }
  if (sb.length() == 0) mt.remove("~v2paid"); else mt.put("~v2paid", sb.toString());
  if (mt.isEmpty()) PMETA.remove(k);
  DIRTY.put(k, Boolean.TRUE);
}QQQ), sp))
# The ONE gate of every item move between the live inventory and a pool'''))

# ================================================================================================= SackCfg: the Void rows (bound fields + reload)
rep(T(r'''scfg.addField(CtField.make("public static boolean ORDERWARNED = false;", scfg))
'''), T(r'''scfg.addField(CtField.make("public static boolean ORDERWARNED = false;", scfg))
# 0.8.0 (Bags v2 spec 2.4): the Void rows - public static volatile, bound by the config kit (Server Setup), loaded by reload() (pdKeys)
for _f in _PD_CFG_FIELDS:
    scfg.addField(CtField.make(_f, scfg))
scfg.addField(CtField.make('public static volatile String PDSIG = "";', scfg))   # the last logged Void settings (reload logs a change once)
scfg.addMethod(CtNewMethod.make("public static int step(int ci) {\n" + _sw("ci", [(i, "PD_STEP_" + c.upper()) for i, c in enumerate(PD_CATS)], "1") + "}", scfg))
scfg.addMethod(CtNewMethod.make("public static double mult(int r) {\n" + _sw("r", [(i, "PD_MULT_" + n.upper()) for i, n in enumerate(PD_RAR)], "1.0") + "}", scfg))
scfg.addMethod(CtNewMethod.make("public static int gate0(int r) {\n" + _sw("r", [(i + 1, "PD_GATE_" + PD_RAR[i + 1].upper()) for i in range(3)], "1") + "}", scfg))
# the highest storage level in use (pd.maxLevel, at least 1)
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static int maxLevel() {
  int m = PD_MAX_LEVEL;
  return m < 1 ? 1 : m;
}QQQ), scfg))
# fix round: the gate in use never goes above pd.maxLevel (a gate no level can reach would block that upgrade for ever)
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static int gate(int r) {
  int g = gate0(r);
  int m = maxLevel();
  return g > m ? m : g;
}QQQ), scfg))
scfg.addMethod(CtNewMethod.make("public static String cost(int ci, int r) {\n" + "".join(
    "  if (ci == %d && r == %d) return PD_COST_%s_%s;\n" % (i, r, c.upper(), PD_RAR[r].upper()) for i, c in enumerate(PD_CATS) for r in (1, 2, 3))
    + '  return "";\n}', scfg))
# a decimal from the file (the kit's dec words); missing = the default; bad = the default + a warning; out of range = clamped + a warning
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static double decKey(java.util.Properties p, String k, double def, double lo, double hi) {
  String v0 = p.getProperty(k);
  if (v0 == null || v0.trim().length() == 0) return def;
  double n = def;
  try { n = Double.parseDouble(v0.trim()); } catch (Throwable t) { @PKG@.SackPool.warn("config.properties: " + k + "=" + v0.trim() + " is not a number - using " + def); return def; }
  if (n != n || n < lo) { @PKG@.SackPool.warn("config.properties: " + k + "=" + v0.trim() + " is below " + lo + " - using " + lo); return lo; }
  if (n > hi) { @PKG@.SackPool.warn("config.properties: " + k + "=" + v0.trim() + " is above " + hi + " - using " + hi); return hi; }
  return n;
}QQQ), scfg))
# an upgrade cost "itemId:qty,itemId:qty" -> LinkedHashMap id -> Long; null = bad text (empty, a bad pair, qty < 1 or > 1,000,000, > 6 items
# (fix round: = the 6 cost cells of the page's Upgrade box - a 7th item would be charged without being shown),
# an id twice). checkCost (the kit's check= hook) also refuses an id the Item asset map does not know.
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.LinkedHashMap parseCost(String t) {
  if (t == null) return null;
  String s = t.trim();
  if (s.length() == 0) return null;
  String[] parts = s.split(",");
  if (parts.length > 6) return null;   // fix round: the page shows 6 cost cells
  java.util.LinkedHashMap out = new java.util.LinkedHashMap();
  for (int i = 0; i < parts.length; i++) {
    String x = parts[i].trim();
    int c = x.lastIndexOf(':');
    if (c <= 0 || c >= x.length() - 1) return null;
    String id = x.substring(0, c).trim();
    long q = 0L;
    try { q = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable e) { return null; }
    if (q < 1L || q > 1000000L || id.length() == 0 || out.containsKey(id)) return null;
    for (int j = 0; j < id.length(); j++) {
      char ch = id.charAt(j);
      if (!(Character.isLetterOrDigit(ch) || ch == '_')) return null;
    }
    out.put(id, Long.valueOf(q));
  }
  return out;
}QQQ), scfg))
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static String checkCost(String key, String value) {
  java.util.LinkedHashMap m = parseCost(value);
  if (m == null) return "Write it as itemId:amount pairs joined by commas (1 to 6 items, amounts 1 to 1000000), e.g. Ore_Iron:100,Ore_Copper:250";
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    boolean ok = false;
    try { ok = com.hypixel.hytale.server.core.asset.type.item.config.Item.getAssetMap().getAsset(id) != null; } catch (Throwable t) { ok = true; }
    if (!ok) return "Unknown item id " + id + " - nothing was changed";
  }
  return null;
}QQQ), scfg))
# the multiplier ladder must not go down (Normal <= Unique <= Rare <= Legendary <= Omni): asks first (never refuses; ignored on import)
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static String checkMult(String key, String value) {
  if (key == null || value == null) return null;
  double n = 0.0;
  try { n = Double.parseDouble(value.trim()); } catch (Throwable t) { return null; }
  String[] keys = new String[] { "pd.mult.Normal", "pd.mult.Unique", "pd.mult.Rare", "pd.mult.Legendary", "pd.mult.Omni" };
  double[] v = new double[] { PD_MULT_NORMAL, PD_MULT_UNIQUE, PD_MULT_RARE, PD_MULT_LEGENDARY, PD_MULT_OMNI };
  int at = -1;
  for (int i = 0; i < keys.length; i++) if (keys[i].equals(key)) at = i;
  if (at < 0) return null;
  v[at] = n;
  for (int i = 1; i < v.length; i++) {
    if (v[i - 1] > v[i]) return "?The multipliers would go DOWN the ladder (" + keys[i - 1].substring(8) + " " + v[i - 1] + " > " + keys[i].substring(8) + " " + v[i] + ") - an upgrade would shrink the space. Change it anyway?";
  }
  return null;
}QQQ), scfg))
# fix round: a level gate above pd.maxLevel (it then acts as the max level) or out of order (Unique <= Rare <= Legendary): asks first
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static String checkGate(String key, String value) {
  if (key == null || value == null) return null;
  int n = 0;
  try { n = Integer.parseInt(value.trim()); } catch (Throwable t) { return null; }
  if (n > PD_MAX_LEVEL) return "?" + n + " is above the highest storage level (" + PD_MAX_LEVEL + ") - the gate will act as Lv " + PD_MAX_LEVEL + ". Change it anyway?";
  String[] keys = new String[] { "pd.gate.Unique", "pd.gate.Rare", "pd.gate.Legendary" };
  int[] v = new int[] { PD_GATE_UNIQUE, PD_GATE_RARE, PD_GATE_LEGENDARY };
  int at = -1;
  for (int i = 0; i < keys.length; i++) if (keys[i].equals(key)) at = i;
  if (at < 0) return null;
  v[at] = n;
  for (int i = 1; i < v.length; i++) {
    if (v[i - 1] > v[i]) return "?The level gates would go DOWN the ladder (" + keys[i - 1].substring(8) + " " + v[i - 1] + " > " + keys[i].substring(8) + " " + v[i] + "). Change it anyway?";
  }
  return null;
}QQQ), scfg))
# after= hook of every pd.* row (the kit set the field already; the next 2 s tick sees the new value through SweepTask.cfgSig): one log line
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static void pdChanged(String key) {
  try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: Void setting " + key + " changed - applies from each player's next sweep (nothing stored is ever deleted)"); } catch (Throwable t) { }
}QQQ), scfg))
'''))
rep(T(r'''# 0.7.12 review fix 1: after= hook of the bags.pocketCraft row (the kit set POCKET_CRAFT already): one log line + the swap applied at once'''),
    T(r'''# 0.8.0: the Void rows from the file (hand edits + the first load); one log line when they differ from the last logged ones
scfg.addMethod(CtNewMethod.make(jt(rQQQ
public static void pdKeys(java.util.Properties p, boolean first) {
@PDLOAD@
  String sig = "" + @PDSIG@;
  if (!sig.equals(PDSIG)) {
    PDSIG = sig;
    try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: Void - " + PD_PER_LEVEL + " items per storage level (max level " + PD_MAX_LEVEL + "), multipliers Normal " + PD_MULT_NORMAL + " / Unique " + PD_MULT_UNIQUE + " / Rare " + PD_MULT_RARE + " / Legendary " + PD_MULT_LEGENDARY + " / Omni " + PD_MULT_OMNI + ", gates Lv " + PD_GATE_UNIQUE + " / " + PD_GATE_RARE + " / " + PD_GATE_LEGENDARY + ", Omni " + (PD_OMNI_AUTO ? "automatic with all six Legendary" : "by /pdadmin only")); } catch (Throwable t) { }
  }
}QQQ.replace("@PDLOAD@", "\n".join(_PD_LOAD)).replace("@PDSIG@", _PD_SIG)), scfg))
# 0.8.0: the live Void settings as one string (SweepTask.cfgSig: a changed row re-sweeps every player once)
scfg.addMethod(CtNewMethod.make('public static String pdSig() {\n  return "" + ' + _PD_SIG + ';\n}', scfg))
# 0.7.12 review fix 1: after= hook of the bags.pocketCraft row (the kit set POCKET_CRAFT already): one log line + the swap applied at once'''))
rep(T(r'''    linkKeys(p, first);     // 0.7.12: bags.benchChests (bench chest count fallback)
'''), T(r'''    linkKeys(p, first);     // 0.7.12: bags.benchChests (bench chest count fallback)
    pdKeys(p, first);       // 0.8.0: the Void rows (levels, multipliers, gates, costs, Omni)
'''))

# ================================================================================================= KnowSync: no bag recipes any more
cut(T(r'''ksync.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.HashSet wanted(java.util.UUID u) {'''), T(r'''# is the recipe of this bag item unlocked for the player (page texts, /craft)?'''), T(r'''# 0.8.0 (Bags v2 spec 4.3): there are NO bag recipes any more - SkyySacks forgets its own 21 managed entries (SYNCED: the 20 tiered bags
# + the Omni) from every player's known set (next() touches exactly those; one UpdateKnownRecipes per player, then nothing); no other entry
ksync.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.HashSet wanted(java.util.UUID u) {
  return new java.util.HashSet();
}QQQ), ksync))
'''))

# ================================================================================================= VoidState + VoidStore (core, before SweepTask)
rep(T(r'''# ================= SweepTask (runs ON world thread; no disk I/O) =================
'''), T(r'''# ================= 0.8.0 VoidState + VoidStore core (research/Bags-v2-Spec.md 2 + 4; tools/sacks_0_8_0_patch.py docstring) =================
# VoidState = one PROFILE KEY's Void (pd/<key>.properties): rar.<Cat> 0..3 (Normal..Legendary), omni, best.<Cat> (the best storage level
# ever reached - the shown level never goes down), own.<Cat> (items the Void took in, the level total while coll:fn:catTotal is missing),
# v2.first (the run-once marker: set after the History copy), v2.history, v2.welcome / v2.pocket (one-time per profile), ret.<bagId>
# (/pdadmin legacybags tokens), any other line kept as it is. The journal (pd/<key>.journal) is read with it: left = unsettled C lines
# of an earlier run (recovered at the next settled sweep of that key), done = settled ones (/pdadmin legacybags), given = their G lines.
vss.addField(CtField.make("public String key;", vss))
vss.addField(CtField.make("public int[] rar;", vss))
vss.addField(CtField.make("public long[] best;", vss))
vss.addField(CtField.make("public long[] own;", vss))
vss.addField(CtField.make("public boolean omni;", vss))
vss.addField(CtField.make("public long first;", vss))
vss.addField(CtField.make("public String hist;", vss))
vss.addField(CtField.make("public boolean welcome;", vss))
vss.addField(CtField.make("public boolean pocket;", vss))
# fix round: ret / left / done / given are touched by the world thread (decide, recover, usedRank, giveBack) AND the writer thread (saveNow,
# settle) - concurrent collections (no ConcurrentModificationException, no lost update; iteration = a consistent snapshot)
vss.addField(CtField.make("public java.util.Map ret;", vss))
vss.addField(CtField.make("public java.util.Properties extra;", vss))
vss.addField(CtField.make("public java.util.List left;", vss))
vss.addField(CtField.make("public java.util.List done;", vss))
vss.addField(CtField.make("public java.util.Set given;", vss))
# fix round: hold = no old bag converts on this profile (set by /pdadmin legacybags <player>, cleared by /pdadmin resume; saved v2.hold);
# outN = items taken OUT to the inventory on the page since the start (memory only): put back in, they do not count as collected again
vss.addField(CtField.make("public volatile boolean hold;", vss))
# fix round 2: holdAt = when the hold was set (v2.holdAt); a hold set before the last /pdadmin resume all (pd/_resume-all.stamp) is over
vss.addField(CtField.make("public long holdAt;", vss))
vss.addField(CtField.make("public long[] outN;", vss))
vss.addConstructor(CtNewConstructor.make(jt(rQQQ
public VoidState(String k, int n) {
  this.key = k;
  this.rar = new int[n];
  this.best = new long[n];
  this.own = new long[n];
  this.outN = new long[n];
  this.hist = "";
  this.ret = new java.util.concurrent.ConcurrentHashMap();
  this.extra = new java.util.Properties();
  this.left = new java.util.concurrent.CopyOnWriteArrayList();
  this.done = new java.util.concurrent.CopyOnWriteArrayList();
  this.given = java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap());
}QQQ), vss))
# VoidStore fields. PEND = key -> ArrayList of journal entries of THIS run waiting for their 30 s (Object[] {seq, bagId, Integer qty,
# Integer n0, "R" | "F", Long time, refund text, key}); PEND is lock-free (fix round: ConcurrentHashMap of CopyOnWriteArrayList - see pendAdd).
for _decl in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path HDIR;", "public static java.nio.file.Path MIGLOG;",
              "public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
              "public static final java.util.concurrent.ConcurrentHashMap BAD = new java.util.concurrent.ConcurrentHashMap();",
              "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();",
              "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();",
              "public static volatile boolean HOLDALL = false;",   # fix round: /pdadmin legacybags all (pd/_legacybags-all.flag)
              "public static volatile long RESUMEALL = 0L;",       # fix round 2: the time of the last /pdadmin resume all (pd/_resume-all.stamp)
              "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();",
              "public static final java.util.concurrent.ConcurrentHashMap SNAPQ = new java.util.concurrent.ConcurrentHashMap();",
              "public static final java.util.concurrent.ConcurrentHashMap SNAPFAIL = new java.util.concurrent.ConcurrentHashMap();",
              "public static final java.util.concurrent.atomic.AtomicLong SEQ = new java.util.concurrent.atomic.AtomicLong();",
              "public static volatile long SETTLE_MS = 30000L;",
              "public static final java.util.concurrent.atomic.AtomicLong SETTLED = new java.util.concurrent.atomic.AtomicLong();",
              "public static final java.util.concurrent.atomic.AtomicLong CONVERTED = new java.util.concurrent.atomic.AtomicLong();"):
    vst.addField(CtField.make(_decl, vst))
# CRASHAT = the harness's crash point (null in the game: nothing happens); crash(at) throws exactly there (crash-at-every-step proof)
vst.addField(CtField.make("public static volatile String CRASHAT = null;", vst))
vst.addField(CtField.make('public static final String NOREAD = "the Void data of this profile cannot be read right now";', vst))
vst.addField(CtField.make("public static volatile int CRASHN = 1;", vst))      # the harness: crash at the CRASHN-th time that step runs
vst.addField(CtField.make("public static volatile int CRASHHITS = 0;", vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void crash(String at) {
  String c = CRASHAT;
  if (c == null || !c.equals(at)) return;
  CRASHHITS = CRASHHITS + 1;
  if (CRASHHITS >= CRASHN) { CRASHAT = null; throw new IllegalStateException("test crash at " + at); }
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void markDirty(String k) {
  if (k != null) DIRTY.put(k, Boolean.TRUE);
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long num(String v, long def) {
  if (v == null) return def;
  try { return Long.parseLong(v.trim()); } catch (Throwable t) { return def; }
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean bool(java.util.Properties p, String key) {
  return "true".equalsIgnoreCase(String.valueOf(p.getProperty(key, "false")).trim());
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void load(@PKG@.VoidState s, java.util.Properties p) {
  String[] cats = @PKG@.SackDefs.CATS;
  java.util.HashSet mine = new java.util.HashSet();
  for (int i = 0; i < cats.length; i++) {
    long r = num(p.getProperty("rar." + cats[i]), 0L);
    s.rar[i] = r < 0L ? 0 : (r > 3L ? 3 : (int) r);
    s.best[i] = Math.max(0L, num(p.getProperty("best." + cats[i]), 0L));
    s.own[i] = Math.max(0L, num(p.getProperty("own." + cats[i]), 0L));
    mine.add("rar." + cats[i]); mine.add("best." + cats[i]); mine.add("own." + cats[i]);
  }
  s.omni = bool(p, "omni");
  s.first = num(p.getProperty("v2.first"), 0L);
  s.hist = String.valueOf(p.getProperty("v2.history", "")).trim();
  s.welcome = bool(p, "v2.welcome");
  s.pocket = bool(p, "v2.pocket");
  s.hold = bool(p, "v2.hold");   // fix round: /pdadmin legacybags hold
  s.holdAt = num(p.getProperty("v2.holdAt"), 0L);
  // fix round 2: /pdadmin resume all also ends the holds of profiles that were not loaded then (their file still says v2.hold=true)
  if (s.hold && RESUMEALL > 0L && s.holdAt <= RESUMEALL) { s.hold = false; markDirty(s.key); }
  mine.add("omni"); mine.add("v2.first"); mine.add("v2.history"); mine.add("v2.welcome"); mine.add("v2.pocket"); mine.add("v2.hold"); mine.add("v2.holdAt");
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {
    String key = (String) en.nextElement();
    if (key.startsWith("ret.")) continue;   // fix round 2: give-back tokens live in the journal only (G lines minus "tok" C lines)
    if (!mine.contains(key)) s.extra.setProperty(key, p.getProperty(key));
  }
}QQQ), vst))
# journal lines: C|seq|bagId|qty|n0|R-or-F|time|refund, D|seq (settled), X|seq (the bag came back), G|seq (given back by /pdadmin)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void readJournal(@PKG@.VoidState s) throws java.io.IOException {
  java.nio.file.Path f = DIR.resolve(s.key + ".journal");
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  java.util.List lines = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
  java.util.LinkedHashMap open = new java.util.LinkedHashMap();
  java.util.LinkedHashMap closed = new java.util.LinkedHashMap();
  for (int i = 0; i < lines.size(); i++) {
    String ln = ((String) lines.get(i)).trim();
    if (ln.length() == 0 || ln.startsWith("#")) continue;
    String[] a = ln.split("\\|", -1);
    if (a[0].equals("C") && a.length >= 8) {
      Object[] e = new Object[] { a[1], a[2], Integer.valueOf((int) num(a[3], 1L)), Integer.valueOf((int) num(a[4], 0L)), a[5], Long.valueOf(num(a[6], 0L)), a[7], s.key };
      open.put(a[1], e);
    } else if (a.length >= 2 && a[0].equals("D")) {
      Object e = open.remove(a[1]);
      if (e != null) closed.put(a[1], e);
    } else if (a.length >= 2 && a[0].equals("X")) {
      open.remove(a[1]);
    } else if (a.length >= 2 && a[0].equals("G")) {
      s.given.add(a[1]);
      if (a.length >= 4) { Integer t = (Integer) s.ret.get(a[2]); s.ret.put(a[2], Integer.valueOf((t == null ? 0 : t.intValue()) + (int) num(a[3], 1L))); }
    }
  }
  s.left.addAll(open.values());
  s.done.addAll(closed.values());
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static @PKG@.VoidState st(String k) {
  if (k == null) return null;
  @PKG@.VoidState s = (@PKG@.VoidState) STATES.get(k);
  if (s != null) return s;
  Long bad = (Long) BAD.get(k);
  if (bad != null && System.currentTimeMillis() - bad.longValue() < 2000L) return null;
  s = new @PKG@.VoidState(k, @PKG@.SackDefs.CATS.length);
  try {
    if (DIR != null) {
      java.nio.file.Path f = DIR.resolve(k + ".properties");
      if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
        java.util.Properties p = new java.util.Properties();
        java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
        try { p.load(in); } finally { in.close(); }
        load(s, p);
      }
      readJournal(s);
    }
  } catch (Throwable t) {
    if (BAD.put(k, Long.valueOf(System.currentTimeMillis())) == null) @PKG@.SackPool.warn("could not read the Void data of " + k + " (pd/" + k + ".properties / .journal) - files left untouched; that profile's rarity, migration and upgrades wait until it reads: " + t);
    return null;
  }
  if (BAD.remove(k) != null) @PKG@.SackPool.warn("the Void data of " + k + " reads again");
  @PKG@.VoidState prev = (@PKG@.VoidState) STATES.putIfAbsent(k, s);
  return prev != null ? prev : s;
}QQQ), vst))
# pd/<key>.properties: tmp + fsync + atomic rename (the pool file's pattern). true = written.
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static synchronized boolean saveNow(String k) {
  @PKG@.VoidState s = (@PKG@.VoidState) STATES.get(k);
  if (s == null || DIR == null) return false;
  try {
    java.util.Properties p = new java.util.Properties();
    p.putAll(s.extra);
    String[] cats = @PKG@.SackDefs.CATS;
    for (int i = 0; i < cats.length; i++) {
      p.setProperty("rar." + cats[i], String.valueOf(s.rar[i]));
      p.setProperty("best." + cats[i], String.valueOf(s.best[i]));
      if (s.own[i] > 0L) p.setProperty("own." + cats[i], String.valueOf(s.own[i]));
    }
    p.setProperty("omni", String.valueOf(s.omni));
    if (s.first > 0L) p.setProperty("v2.first", String.valueOf(s.first));
    if (s.hist != null && s.hist.length() > 0) p.setProperty("v2.history", s.hist);
    if (s.welcome) p.setProperty("v2.welcome", "true");
    if (s.pocket) p.setProperty("v2.pocket", "true");
    if (s.hold) { p.setProperty("v2.hold", "true"); p.setProperty("v2.holdAt", String.valueOf(s.holdAt)); }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.nio.file.Path dst = DIR.resolve(k + ".properties");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyyVoid (SkyySacks 0.8.0) - this profile's Void: rarity per category (0 Normal .. 3 Legendary), best storage level, Omni, the one-time v2 marker"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    DIRTY.remove(k);
    return true;
  } catch (Throwable t) {
    DIRTY.put(k, Boolean.TRUE);
    @PKG@.KnowSync.warnOnce("could not save the Void data of " + k + " (kept, retried by the next save): " + t);
    return false;
  }
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void flushDirty() {
  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < ks.size(); i++) saveNow((String) ks.get(i));
}QQQ), vst))
# one journal line, appended and fsync'd (the crash proof of a conversion); false = not written (the caller stops)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static synchronized boolean appendJournal(String k, String line) {
  if (k == null || DIR == null) return false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(DIR.resolve(k + ".journal").toFile(), true);
    try { out.write((line + System.lineSeparator()).getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
    return true;
  } catch (Throwable t) {
    @PKG@.KnowSync.warnOnce("could not write the Void journal of " + k + " (nothing converted this time, retried): " + t);
    return false;
  }
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static String nextSeq() {
  return "t" + Long.toString(System.currentTimeMillis(), 36) + "n" + SEQ.incrementAndGet();
}QQQ), vst))
# ---- storage level (spec 2.1): total = coll:fn:catTotal {UUID, category} (SkyyCollections 0.2.9+, the ACTIVE profile), else own.<Cat>
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean collInstalled() {
  try { return @PKG@.SackPool.bridge().get("coll:fn:catTotal") instanceof java.util.function.Function; } catch (Throwable t) { return false; }
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long collTotal(java.util.UUID u, String cat) {
  if (u == null || cat == null) return -1L;
  try {
    Object f = @PKG@.SackPool.bridge().get("coll:fn:catTotal");
    if (!(f instanceof java.util.function.Function)) return -1L;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, cat });
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { }
  return -1L;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int levelOf(long total, int ci) {
  int step = @PKG@.SackCfg.step(ci);
  if (step < 1) step = 1;
  int max = @PKG@.SackCfg.maxLevel();
  if (total <= 0L) return 1;
  double q = Math.floor(Math.sqrt((double) total / (double) step) + 1.0E-9);
  long lv = 1L + (long) q;
  if (lv > (long) max) lv = (long) max;
  return (int) lv;
}QQQ), vst))
# the items a level needs (the inverse): step x (level - 1)^2
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long totalFor(int level, int ci) {
  long n = (long) (level < 1 ? 0 : level - 1);
  long step = (long) @PKG@.SackCfg.step(ci);
  return step * n * n;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long total(java.util.UUID u, String k, int ci) {
  long t = collTotal(u, @PKG@.SackDefs.CATS[ci]);
  if (t >= 0L) return t;
  @PKG@.VoidState s = st(k);
  return s == null ? 0L : s.own[ci];
}QQQ), vst))
# the shown level = max(the saved best, the level from the total), capped at pd.maxLevel; a new best is saved (dirty)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int level(java.util.UUID u, String k, int ci) {
  if (ci < 0 || ci >= @PKG@.SackDefs.CATS.length) return 1;
  int lv = levelOf(total(u, k, ci), ci);
  @PKG@.VoidState s = st(k);
  int max = @PKG@.SackCfg.maxLevel();
  if (s != null) {
    if ((long) lv > s.best[ci]) { s.best[ci] = (long) lv; markDirty(k); }
    if (s.best[ci] > (long) lv) lv = (int) Math.min(s.best[ci], (long) max);
  }
  return lv > max ? max : lv;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int levelBest(String k, int ci) {
  @PKG@.VoidState s = st(k);
  int max = @PKG@.SackCfg.maxLevel();
  long b = s == null ? 1L : Math.max(1L, s.best[ci]);
  return (int) Math.min(b, (long) max);
}QQQ), vst))
# ---- pending conversions of THIS run (R = a bag that raises a rarity once settled; it counts at once for capacity and the page)
# fix round: LOCK-FREE (was synchronized on VoidStore.class, the monitor saveNow / appendJournal hold across an fsync - the world thread's
# capsK / page asked ~48 times per sweep and could wait for the disk). PEND = ConcurrentHashMap of CopyOnWriteArrayList; a key's list is
# never removed once made (a handful of profile keys per run) so an add can never land in a list that was just dropped.
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void pendAdd(String k, Object[] e) {
  java.util.List l = (java.util.List) PEND.get(k);
  if (l == null) {
    java.util.List nl = new java.util.concurrent.CopyOnWriteArrayList();
    l = (java.util.List) PEND.putIfAbsent(k, nl);
    if (l == null) l = nl;
  }
  l.add(e);
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean pendRemove(String k, Object[] e) {
  java.util.List l = (java.util.List) PEND.get(k);
  if (l == null) return false;
  return l.remove(e);
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.ArrayList pendCopy(String k) {
  java.util.List l = (java.util.List) PEND.get(k);
  return l == null ? new java.util.ArrayList() : new java.util.ArrayList(l);
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.ArrayList pendKeys() {
  return new java.util.ArrayList(PEND.keySet());
}QQQ), vst))
# the rarity index (0..3) an R entry gives category ci, -1 none (a Farming bag also sets Fishing)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int rOf(String bag, int ci) {
  int r = @PKG@.SackDefs.legacyRank(bag);
  if (r < 1 || r > 4) return -1;
  String c = @PKG@.SackDefs.legacyCat(bag);
  String me = @PKG@.SackDefs.CATS[ci];
  if (me.equals(c) || ("Fishing".equals(me) && "Farming".equals(c))) return r - 1;
  return -1;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int pendRank(String k, int ci) {
  java.util.ArrayList l = pendCopy(k);
  int best = -1;
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    if (!"R".equals(e[4])) continue;
    int r = rOf((String) e[1], ci);
    if (r > best) best = r;
  }
  return best;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean pendOmni(String k) {
  java.util.ArrayList l = pendCopy(k);
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    if ("R".equals(e[4]) && @PKG@.SackDefs.legacyRank((String) e[1]) == 5) return true;
  }
  return false;
}QQQ), vst))
# ---- rarity + capacity (spec 2.2 / 2.3)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int rarOf(String k, int ci) {
  @PKG@.VoidState s = st(k);
  int r = s == null ? 0 : s.rar[ci];
  int p = pendRank(k, ci);
  return p > r ? p : r;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int legendCount(String k) {
  int n = 0;
  for (int i = 0; i < @PKG@.SackDefs.CATS.length; i++) if (rarOf(k, i) >= 3) n++;
  return n;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean omni(String k) {
  @PKG@.VoidState s = st(k);
  if (s == null) return false;
  if (s.omni || pendOmni(k)) return true;
  return @PKG@.SackCfg.PD_OMNI_AUTO && legendCount(k) >= @PKG@.SackDefs.CATS.length;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int rank(String k, int ci) {
  return omni(k) ? 4 : rarOf(k, ci);
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long capOf(int level, int rank) {
  double c = Math.floor((double) level * (double) @PKG@.SackCfg.PD_PER_LEVEL * @PKG@.SackCfg.mult(rank) + 1.0E-6);
  if (c != c || c < 0.0) return 0L;
  if (c > 2147483647.0) return 2147483647L;
  return (long) c;
}QQQ), vst))
# category -> Integer capacity: capsK with the live totals (the sweep, the page, the bridges: the ACTIVE profile), capsBest from the saved
# best levels only (no UUID needed)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.HashMap capsK(java.util.UUID u, String k) {
  java.util.HashMap out = new java.util.HashMap();
  String[] cats = @PKG@.SackDefs.CATS;
  for (int i = 0; i < cats.length; i++) out.put(cats[i], Integer.valueOf((int) capOf(level(u, k, i), rank(k, i))));
  return out;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.HashMap capsBest(String k) {
  java.util.HashMap out = new java.util.HashMap();
  String[] cats = @PKG@.SackDefs.CATS;
  for (int i = 0; i < cats.length; i++) out.put(cats[i], Integer.valueOf((int) capOf(levelBest(k, i), rank(k, i))));
  return out;
}QQQ), vst))
# the items stored per category (homeOf: cooked food stored in Farming counts there)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long[] usedAll(String k) {
  long[] out = new long[@PKG@.SackDefs.CATS.length];
  java.util.Iterator it = @PKG@.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    int ci = @PKG@.SackDefs.catIndex(@PKG@.SackDefs.homeOf((String) e.getKey()));
    if (ci >= 0) out[ci] += ((Long) e.getValue()).longValue();
  }
  return out;
}QQQ), vst))
# the Void's own intake count (the level total without SkyyCollections; counted only while coll:fn:catTotal is missing - no file writes otherwise)
# fix round: items the page took OUT to the inventory (noteOut) and later put back in are not counted again (a Withdraw + Deposit loop
# raised the level for free); only items beyond what went out count as collected. outN is memory only (a restart forgets it - harmless).
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void noteOut(String k, int ci, long n) {
  if (n <= 0L || ci < 0 || collInstalled()) return;
  @PKG@.VoidState s = st(k);
  if (s == null || ci >= s.outN.length) return;
  s.outN[ci] = s.outN[ci] + n;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void noteIntake(String k, int ci, long n) {
  if (n <= 0L || ci < 0 || collInstalled()) return;
  @PKG@.VoidState s = st(k);
  if (s == null || ci >= s.own.length) return;
  long back = s.outN[ci] < n ? s.outN[ci] : n;
  s.outN[ci] = s.outN[ci] - back;
  long add = n - back;
  if (add <= 0L) return;
  s.own[ci] = s.own[ci] + add;
  markDirty(k);
}QQQ), vst))
# ---- the CREDIT of a conversion (writer thread; spec 4.3): R = the rarity (max, idempotent) saved first; F = the refund into the pool with
# its seq in the same atomic pool write (SackPool.credit: a repeat pays nothing). Then D|seq. false = retry later (nothing half-done counts).
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean applyR(@PKG@.VoidState s, String bag) {
  int r = @PKG@.SackDefs.legacyRank(bag);
  boolean ch = false;
  if (r == 5) { if (!s.omni) { s.omni = true; ch = true; } return ch; }
  for (int ci = 0; ci < s.rar.length; ci++) {
    int g = rOf(bag, ci);
    if (g > s.rar[ci]) { s.rar[ci] = g; ch = true; }
  }
  return ch;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean settle(String k, Object[] e) {
  @PKG@.VoidState s = st(k);
  if (s == null) return false;
  String seq = (String) e[0];
  String bag = (String) e[1];
  if ("R".equals(e[4])) {
    applyR(s, bag);
    if (!saveNow(k)) return false;
    crash("SR");
  } else {
    java.util.LinkedHashMap items = @PKG@.SackCfg.parseCost((String) e[6]);
    if (items != null) {
      // fix round 2: the retry after a failed pool write (paidHas true in memory only) saves + reads back too before D is written
      if (!@PKG@.SackPool.paidHas(k, seq)) {
        if (!@PKG@.SackPool.credit(k, seq, items)) return false;
        @PKG@.SackPool.save(k);
      } else if (@PKG@.SackPool.DIRTY.containsKey(k)) @PKG@.SackPool.save(k);
      if (@PKG@.SackPool.DIRTY.containsKey(k) && !@PKG@.SackPool.paidOnDisk(k, seq)) return false;
    }
    crash("SF");
  }
  if (!appendJournal(k, "D|" + seq)) return false;
  if (!"R".equals(e[4])) @PKG@.SackPool.unpaid(k, seq);
  s.left.remove(e);
  if (!s.done.contains(e)) s.done.add(e);
  SETTLED.incrementAndGet();   // (the D|seq journal line is the record; crafts.log has the VOID-CONVERT line)
  return true;
}QQQ), vst))
# every pending entry whose removal is durable (SETTLE_MS since it was made) - the SackSaver (writer thread, every 10 s) and at once for
# recovered entries (time 0)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int settleDue(long now) {
  int n = 0;
  java.util.ArrayList ks = pendKeys();
  for (int i = 0; i < ks.size(); i++) {
    String k = (String) ks.get(i);
    java.util.ArrayList l = pendCopy(k);
    for (int j = 0; j < l.size(); j++) {
      Object[] e = (Object[]) l.get(j);
      if (((Long) e[5]).longValue() + SETTLE_MS > now) continue;
      try { if (settle(k, e)) { pendRemove(k, e); n++; } } catch (Throwable t) { @PKG@.KnowSync.warnOnce("Void settle failed (retried): " + t); }
    }
  }
  return n;
}QQQ), vst))

# ================= SweepTask (runs ON world thread; no disk I/O) =================
'''))

# SackPool.paidOnDisk: read the pool FILE back for the seq (settle's proof that the refund write reached the disk)
rep(T(r'''# The ONE gate of every item move between the live inventory and a pool'''), T(r'''sp.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean paidOnDisk(String k, String seq) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return false;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    Object v = p.getProperty("~v2paid");
    return v != null && (" " + String.valueOf(v) + " ").indexOf(" s" + seq + " ") >= 0;
  } catch (Throwable t) { return false; }
}QQQ), sp))
# The ONE gate of every item move between the live inventory and a pool'''))

# ================================================================================================= SweepTask: every category, category room
rep(T(r'''public static java.util.HashMap caps(@INV@ inv) {
  java.util.HashMap caps = new java.util.HashMap();
  scan(inv, caps, new java.util.HashMap());
  return caps;
}'''), T(r'''public static java.util.HashMap caps(@INV@ inv) {
  // 0.8.0 (Bags v2 spec 1.2): no bag needs to be carried - every category is reachable (callers ask containsKey); the CAPACITY of a
  // category is VoidStore.capsK / capsBest (one item limit per category)
  java.util.HashMap caps = new java.util.HashMap();
  String[] cats = @PKG@.SackDefs.CATS;
  for (int i = 0; i < cats.length; i++) caps.put(cats[i], Integer.valueOf(2147483647));
  return caps;
}'''))
rep(T(r'''  java.util.HashMap caps = capsIn != null ? capsIn : caps(inv);
  if (caps.isEmpty()) return 0;
  java.util.HashMap left = null;'''), T(r'''  // 0.8.0: capsIn = the category CAPACITY (VoidStore.capsK); none given = the saved best levels (VoidStore.capsBest)
  java.util.HashMap caps = capsIn != null ? capsIn : {PKG}.VoidStore.capsBest(k);
  if (caps.isEmpty()) return 0;
  long[] used = null;   // 0.8.0: the items stored per category (one limit per category, spec 2.2)
  java.util.HashMap left = null;'''))
rep(T(r'''      Integer catCap = (Integer) caps.get(cat);
      if (catCap == null) continue;
      long have = {PKG}.SackPool.get(k, id);
      long room = (long) catCap.intValue() - have;
      if (room <= 0L) continue;'''), T(r'''      Integer catCap = (Integer) caps.get(cat);
      int ci = {PKG}.SackDefs.catIndex(cat);
      if (catCap == null || ci < 0) continue;
      if (used == null) used = {PKG}.VoidStore.usedAll(k);
      long room = (long) catCap.intValue() - used[ci];   // 0.8.0: the room of the CATEGORY (was: of this item)
      if (room <= 0L) continue;'''))
rep(T(r'''      if (removed > 0) {{
        {PKG}.SackPool.add(k, id, (long) removed);
        moved += removed;
        if (ex != null) left.put(id, Long.valueOf(ex.longValue() - (long) removed));'''), T(r'''      if (removed > 0) {{
        {PKG}.SackPool.add(k, id, (long) removed);
        used[ci] = used[ci] + (long) removed;
        {PKG}.VoidStore.noteIntake(k, ci, (long) removed);
        moved += removed;
        if (ex != null) left.put(id, Long.valueOf(ex.longValue() - (long) removed));'''))
rep(T(r'''    + @PKG@.SackDefs.CAP_SMALL + "," + @PKG@.SackDefs.CAP_MEDIUM + "," + @PKG@.SackDefs.CAP_RARE + "," + @PKG@.SackDefs.CAP_LARGE + "," + @PKG@.SackDefs.CAP_OMNI;'''),
    T(r'''    + @PKG@.SackDefs.CAP_SMALL + "," + @PKG@.SackDefs.CAP_MEDIUM + "," + @PKG@.SackDefs.CAP_RARE + "," + @PKG@.SackDefs.CAP_LARGE + "," + @PKG@.SackDefs.CAP_OMNI
    + "," + @PKG@.SackCfg.pdSig();   // 0.8.0: the Void rows (levels, multipliers, gates, Omni)'''))

# ================================================================================================= SackSaver: settle + the Void files
rep(T(r'''  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackCfg.reload(); }} catch (Throwable t) {{ }}'''), T(r'''  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}
  // 0.8.0: the migration credits whose 30 s are up (rarity / refund + D|seq), then the Void files (levels, rarity) - before the pools
  try {{ {PKG}.VoidStore.settleDue(System.currentTimeMillis()); }} catch (Throwable t) {{ }}
  try {{ {PKG}.VoidStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackCfg.reload(); }} catch (Throwable t) {{ }}'''))
rep(T(r'''  // 0.7.7: sacks:freebags follows SkyyCollections appearing / leaving (load order), the one-time notice file is written off the world thread
  try {{ {PKG}.SackCfg.pubFree(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}'''), T(r'''  // 0.8.0: sacks:freebags is no longer published (no bag recipes); the old one-time notice file is still written when it changes
  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}'''))

# ================================================================================================= VoidStore (late): migration, upgrade, admin
rep(T(r'''# CraftPage fields + constructor first (SacksPage references it)
'''), T(r'''# ================= 0.8.0 VoidStore (late: after SackPool.runOnWriter) - the migration, the upgrade, /pdadmin, sacks:fn:pd =================
# VoidJob (fields + constructor first: the methods below construct it; its run() comes after them)
vjob.addInterface(pool.get("java.lang.Runnable"))
vjob.addField(CtField.make("public int mode;", vjob))
vjob.addField(CtField.make("public String k;", vjob))
vjob.addField(CtField.make("public java.util.UUID u;", vjob))
vjob.addConstructor(CtNewConstructor.make("public VoidJob(int mode, String k, java.util.UUID u) { this.mode = mode; this.k = k; this.u = u; }", vjob))
# migration.log (Skyy_SkyySacks/migration.log): one line per profile step with its Undo (PROJECT-RULES 4). Rare: written where it happens.
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static synchronized void migLog(String k, String text) {
  try {
    if (MIGLOG == null) return;
    java.nio.file.Files.createDirectories(MIGLOG.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String l = new java.util.Date().toString() + " " + k + " " + text + System.lineSeparator();
    java.nio.file.Files.write(MIGLOG, l.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { }
}QQQ), vst))
# HISTORY FIRST (writer thread): pools/<k>.properties + processing/<k>.properties -> history/<k>-<stamp>/ (fsync), read back byte for byte;
# only then the run-once marker v2.first (pd file, fsync). Any failure: nothing marked, WARN once, retried after 60 s.
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean snapshot(String k) {
  @PKG@.VoidState s = st(k);
  if (s == null || HDIR == null) return false;
  if (s.first > 0L) return true;
  try {
    String stamp = new java.text.SimpleDateFormat("yyyyMMdd-HHmmss").format(new java.util.Date());
    java.nio.file.Path hd = HDIR.resolve(k + "-" + stamp);
    int g = 0;
    while (java.nio.file.Files.exists(hd, new java.nio.file.LinkOption[0]) && g < 1000) { g++; hd = HDIR.resolve(k + "-" + stamp + "-" + g); }
    java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
    // fix round: the copy is of the LIVE pool - a pool change not yet written is flushed first (a failed write keeps it dirty: no copy now)
    if (@PKG@.SackPool.DIRTY.remove(k) != null) {
      @PKG@.SackPool.save(k);
      if (@PKG@.SackPool.DIRTY.containsKey(k)) throw new java.io.IOException("pools/" + k + ".properties could not be written before the History copy");
    }
    if (@PKG@.ProcStore.DIRTY.containsKey(k)) @PKG@.ProcStore.flushDirty();
    java.nio.file.Path[] src =new java.nio.file.Path[] { @PKG@.SackPool.DIR == null ? null : @PKG@.SackPool.DIR.resolve(k + ".properties"),
                                                         @PKG@.ProcStore.DIR == null ? null : @PKG@.ProcStore.DIR.resolve(k + ".properties") };
    String[] sub = new String[] { "pools", "processing" };
    int copied = 0;
    for (int i = 0; i < src.length; i++) {
      if (src[i] == null || !java.nio.file.Files.exists(src[i], new java.nio.file.LinkOption[0])) continue;
      byte[] raw = java.nio.file.Files.readAllBytes(src[i]);
      java.nio.file.Path d = hd.resolve(sub[i] + "-" + k + ".properties");
      java.io.FileOutputStream out = new java.io.FileOutputStream(d.toFile());
      try { out.write(raw); out.flush(); out.getFD().sync(); } finally { out.close(); }
      byte[] back = java.nio.file.Files.readAllBytes(d);
      if (!java.util.Arrays.equals(raw, back)) throw new java.io.IOException("the History copy " + d + " does not match " + src[i]);
      copied++;
    }
    crash("H");
    s.hist = HDIR.getFileName().toString() + "/" + hd.getFileName().toString();
    s.first = System.currentTimeMillis();
    if (!saveNow(k)) { s.first = 0L; s.hist = ""; throw new java.io.IOException("pd/" + k + ".properties could not be written"); }
    // fix round: the Undo never restores the History copy over a pool that was used since (that would duplicate the items taken out and
    // lose the refunds and everything gathered since) - the copy is the record of the pool before the migration
    migLog(k, "v2 START - History copy " + s.hist + " (" + copied + " file(s), read back and identical; the pool BEFORE the migration, kept as a record). UNDO (in this order, while SkyySacks 0.8.0 still runs): 1) /pdadmin legacybags all (or /pdadmin legacybags <player>) - each player gets the bags that became rarity back at their next sweep on this profile (refunded bags stay refunded in the pool) and no old bag converts again until /pdadmin resume; 2) wait until this profile's line '/pdadmin legacybags: N old bag(s) given back' is in this log; 3) stop the server and roll back the jar. Keep pools/" + k + ".properties as it is - do NOT copy the History copy over it once the player has played since (it would bring back items taken out and lose the refunds and items gathered since). pd/" + k + ".properties and pd/" + k + ".journal can stay (0.7.18 ignores them; rolling forward again keeps the rarity and gives no second credit).");
    SNAPFAIL.remove(k);
    return true;
  } catch (Throwable t) {
    if (SNAPFAIL.put(k, Long.valueOf(System.currentTimeMillis())) == null) @PKG@.SackPool.warn("the Void migration of " + k + " waits: its History copy could not be made or checked (nothing changed; retried every 60 s): " + t);
    return false;
  }
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void scheduleSnap(String k, java.util.UUID u) {
  Long f = (Long) SNAPFAIL.get(k);
  if (f != null && System.currentTimeMillis() - f.longValue() < 60000L) return;
  if (SNAPQ.putIfAbsent(k, Boolean.TRUE) != null) return;
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(1, k, u));
}QQQ), vst))
# the plain containers the Void works with (storage, hotbar, backpack - what the old caps() scanned)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static @IC@[] conts(@INV@ inv) {
  return new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int countIn(@INV@ inv, String id, boolean plainOnly) {
  if (inv == null || id == null) return 0;
  @IC@[] cs = conts(inv);
  int n = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short sl = 0; sl < cap; sl++) {
      @IS@ it = cs[c].getItemStack(sl);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      if (plainOnly) { org.bson.BsonDocument md = it.getMetadata(); if (md != null && !md.isEmpty()) continue; }
      n += it.getQuantity();
    }
  }
  return n;
}QQQ), vst))
# RECOVERY of an earlier run's unsettled C lines (world thread, settled key, BEFORE any conversion): the bag still there (count >= n0) =
# the inventory came back without the removal -> X|seq (it converts again below); fewer = the removal was saved -> settle now (writer)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int recover(@INV@ inv, String k, @PKG@.VoidState s) {
  if (s.left.isEmpty()) return 0;
  java.util.ArrayList l = new java.util.ArrayList(s.left);
  java.util.HashMap cnt = new java.util.HashMap();
  int due = 0;
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    String bag = (String) e[1];
    Integer c = (Integer) cnt.get(bag);
    if (c == null) { c = Integer.valueOf(countIn(inv, bag, false)); cnt.put(bag, c); }
    if (c.intValue() < ((Integer) e[3]).intValue()) {
      e[5] = Long.valueOf(0L);
      s.left.remove(e);
      pendAdd(k, e);
      due++;
      try { @PKG@.CraftLog.later(k, "VOID-RECOVER " + e[0] + " " + bag + " removal was saved - credit now"); } catch (Throwable t) { }
    } else if (appendJournal(k, "X|" + e[0])) {
      s.left.remove(e);
      try { @PKG@.CraftLog.later(k, "VOID-RECOVER " + e[0] + " " + bag + " came back with the inventory - converts again"); } catch (Throwable t) { }
    }
  }
  if (due > 0) @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(3, k, (java.util.UUID) null));
  return due;
}QQQ), vst))
# DECIDE: is this old bag USED for a rarity (R) or an extra (F, refunded)? (spec 4.2 "best bag wins"; extra = a second bag of a type or one
# below the rarity you already have). The bags are decided best first (convert sorts them), so the best of a type is the R one:
#  - a /pdadmin legacybags token of that id = R (it was a rarity bag; no second credit);
#  - the Omni bag: the FIRST one ever (no Omni R in the journal / pending, and the Void not Omni already) = Omni rarity; every other Omni
#    bag is refunded;
#  - a typed bag while the Void is Omni (or will be): below Omni = refunded;
#  - a typed bag when a bag of its type at least this good was used already (journal / pending) = extra = refunded;
#  - else R when its rarity is >= the category's current one (the Farming bag: Farming or Fishing), else (below) refunded.
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int usedRank(String k, @PKG@.VoidState s, String type) {
  java.util.ArrayList l = pendCopy(k);
  l.addAll(s.done);
  int best = 0;
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    if (!"R".equals(e[4])) continue;
    String b = (String) e[1];
    int r = @PKG@.SackDefs.legacyRank(b);
    String t = r == 5 ? "Omni" : @PKG@.SackDefs.legacyCat(b);
    if (type.equals(t) && r > best) best = r;
  }
  return best;
}QQQ), vst))
# fix round 2: the give-back tokens are derived from the journal alone (crash-proof: no separate token file write that could run ahead of or
# behind the journal): tokens of a bag id = the bags G lines gave back (s.ret, rebuilt from the journal at load) minus the C lines of this
# id marked "tok" that are not cancelled (pending, unsettled or settled; an X line drops one). Counted per seq (an entry in two lists
# for a moment counts once).
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int tokAvail(String k, @PKG@.VoidState s, String id) {
  Integer g = (Integer) s.ret.get(id);
  int n = g == null ? 0 : g.intValue();
  if (n <= 0) return 0;
  java.util.ArrayList l = pendCopy(k);
  l.addAll(s.left);
  l.addAll(s.done);
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    if (id.equals(e[1]) && "tok".equals(e[6]) && seen.add(e[0])) n--;
  }
  return n;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int decide(String k, @PKG@.VoidState s, String id) {
  if (tokAvail(k, s, id) > 0) return 2;
  int r = @PKG@.SackDefs.legacyRank(id);
  // fix round 2: a Void that is Omni already (granted, upgraded, or all six Legendary with Omni auto) refunds every Omni bag
  if (r == 5) return (usedRank(k, s, "Omni") == 0 && !omni(k)) ? 1 : 0;
  if (r < 1 || omni(k)) return 0;
  String type = @PKG@.SackDefs.legacyCat(id);
  if (usedRank(k, s, type) >= r) return 0;
  for (int ci = 0; ci < @PKG@.SackDefs.CATS.length; ci++) {
    int g = rOf(id, ci);
    if (g >= 0 && g >= rarOf(k, ci)) return 1;
  }
  return 0;
}QQQ), vst))
# CONVERT every old bag in storage / hotbar / backpack (world thread, settled key, after recover). The bags are taken BEST FIRST (the Omni,
# then Legendary .. Normal), so "best bag wins" does not depend on the slot order. Per stack: journal FIRST (C lines, fsync: one R line for
# a used bag, one F line for the extras of the stack), then the exact slot removal (read back; a short removal puts the stack back and
# cancels with X lines). Returns bags converted; raised gets "Mining Rare, ..." of the R bags, extra[0] = refunded bags.
# the journal lines of a stack's conversion entries: C lines (claim) or X lines (cancel), one per entry
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static String jLines(java.util.ArrayList mine, boolean cancel) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < mine.size(); i++) {
    Object[] e = (Object[]) mine.get(i);
    if (i > 0) sb.append(System.lineSeparator());
    if (cancel) sb.append("X|" + e[0]);
    else sb.append("C|" + e[0] + "|" + e[1] + "|" + e[2] + "|" + e[3] + "|" + e[4] + "|" + e[5] + "|" + e[6]);
  }
  return sb.toString();
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int convert(@INV@ inv, String k, @PKG@.VoidState s, StringBuilder raised, int[] extra) {
  @IC@[] cs = conts(inv);
  java.util.ArrayList found = new java.util.ArrayList();
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short sl = 0; sl < cap; sl++) {
      @IS@ it = cs[c].getItemStack(sl);
      if (it == null || it.isEmpty()) continue;
      int r = @PKG@.SackDefs.legacyRank(it.getItemId());
      if (r <= 0 || it.getQuantity() <= 0) continue;
      int at = found.size();
      while (at > 0 && ((Integer) ((Object[]) found.get(at - 1))[2]).intValue() < r) at--;
      found.add(at, new Object[] { Integer.valueOf(c), Integer.valueOf(sl), Integer.valueOf(r) });
    }
  }
  int n = 0;
  for (int f = 0; f < found.size(); f++) {
    Object[] fs = (Object[]) found.get(f);
    @IC@ cont = cs[((Integer) fs[0]).intValue()];
    short sl = (short) ((Integer) fs[1]).intValue();
    int r = ((Integer) fs[2]).intValue();
    @IS@ it = cont.getItemStack(sl);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    int q = it.getQuantity();
    int n0 = countIn(inv, id, false);
    int dc = decide(k, s, id);
    boolean up = dc > 0;
    long now = System.currentTimeMillis();
    java.util.ArrayList mine = new java.util.ArrayList();
    // fix round 2: a bag used by a give-back token is marked "tok" in its C line - the token is spent exactly when (and as long as) that
    // line stands (cancelled by X = the token is back), so a failed journal write / short removal / crash never loses or doubles a token
    if (up) mine.add(new Object[] { nextSeq(), id, Integer.valueOf(1), Integer.valueOf(n0), "R", Long.valueOf(now), dc == 2 ? "tok" : "-", k });
    int fq = up ? q - 1 : q;
    if (fq > 0) {
      java.util.LinkedHashMap one = @PKG@.SackCfg.parseCost(@PKG@.SackDefs.REFUND[r - 1]);
      StringBuilder rs = new StringBuilder();
      java.util.Iterator ri = one.entrySet().iterator();
      while (ri.hasNext()) {
        java.util.Map.Entry re = (java.util.Map.Entry) ri.next();
        if (rs.length() > 0) rs.append(',');
        rs.append((String) re.getKey()).append(':').append(((Long) re.getValue()).longValue() * (long) fq);
      }
      mine.add(new Object[] { nextSeq(), id, Integer.valueOf(fq), Integer.valueOf(n0), "F", Long.valueOf(now), rs.toString(), k });
    }
    // fix round: the stack's C lines go in ONE append + ONE fsync (was one per line) - a torn last line is skipped by readJournal (< 8 fields)
    // and the slot is only emptied after this returns, so a crash here leaves the bag where it was (recover: X, it converts again)
    if (!appendJournal(k, jLines(mine, false))) {
      appendJournal(k, jLines(mine, true));
      return n;
    }
    crash("C");
    @ISS@ tx = cont.removeItemStackFromSlot(sl, q);
    @IS@ rem = (tx == null || !tx.succeeded()) ? null : tx.getRemainder();
    int removed = (tx == null || !tx.succeeded()) ? 0 : q - (rem == null ? 0 : rem.getQuantity());
    if (removed != q) {
      if (removed > 0) cont.setItemStackForSlot(sl, it);
      appendJournal(k, jLines(mine, true));
      @PKG@.SackPool.warn("Void: an old bag (" + id + " x" + q + ") could not be taken out of its slot - left as it is, tried again later");
      continue;
    }
    crash("REM");
    for (int i = 0; i < mine.size(); i++) pendAdd(k, (Object[]) mine.get(i));
    n += q;
    CONVERTED.addAndGet((long) q);
    if (up) {
      if (raised.length() > 0) raised.append(", ");
      if (r == 5) raised.append("Omni (every category)");
      else {
        String cat = @PKG@.SackDefs.legacyCat(id);
        raised.append(cat).append(' ').append(@PKG@.SackDefs.RNAME[r - 1]);
        if ("Farming".equals(cat)) raised.append(" + Fishing ").append(@PKG@.SackDefs.RNAME[r - 1]);
      }
    }
    extra[0] = extra[0] + fq;
    try { @PKG@.CraftLog.later(k, "VOID-CONVERT " + id + " x" + q + (up ? " rarity" : "") + (fq > 0 ? " refund x" + fq : "") + " (credit in " + (SETTLE_MS / 1000L) + " s)"); } catch (Throwable t) { }
  }
  return n;
}QQQ.replace("@ISS@", ISS)), vst))
# ---- /pdadmin legacybags (world thread of the TARGET player, its settled key): the journal's settled R bags back (G line first - never
# twice; a token per bag so a re-conversion gives no second credit). Returns {given, waiting for free slots, status 0 ok / 1 unreadable /
# 2 no inventory / 3 journal not written}. (fix round: moved before migrate, which calls it under /pdadmin legacybags all)
# save pd/<k> on the writer thread
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void saveAsync(String k) {
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(2, k, (java.util.UUID) null));
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int[] giveBackN(@PLA@ p, String k) {
  int[] out = new int[3];
  @PKG@.VoidState s = st(k);
  if (s == null) { out[2] = 1; return out; }
  @INV@ inv = p.getInventory();
  if (inv == null) { out[2] = 2; return out; }
  @IC@ stor = inv.getStorage();
  int free = 0;
  short cap = stor.getCapacity();
  for (short sl = 0; sl < cap; sl++) { @IS@ it = stor.getItemStack(sl); if (it == null || it.isEmpty()) free++; }
  java.util.ArrayList l = new java.util.ArrayList(s.done);
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    if (!"R".equals(e[4]) || s.given.contains(e[0])) continue;
    int q = ((Integer) e[2]).intValue();
    if (q > free) { out[1] += q; continue; }
    if (!appendJournal(k, "G|" + e[0] + "|" + e[1] + "|" + q)) { out[2] = 3; break; }
    s.given.add(e[0]);
    Integer t = (Integer) s.ret.get(e[1]);
    s.ret.put(e[1], Integer.valueOf((t == null ? 0 : t.intValue()) + q));
    markDirty(k);
    @IST@ tx = stor.addItemStack(new @IS@((String) e[1], q));
    @IS@ rem = tx == null ? null : tx.getRemainder();
    if (tx == null || !tx.succeeded() || (rem != null && !rem.isEmpty())) @PKG@.SackPool.warn("/pdadmin legacybags: " + e[1] + " x" + q + " for " + k + " did not fully fit (journal " + e[0] + ")");
    free -= q;
    out[0] += q;
    try { @PKG@.CraftLog.later(k, "VOID-GIVEBACK " + e[0] + " " + e[1] + " x" + q + " (/pdadmin legacybags)"); } catch (Throwable t2) { }
  }
  if (out[0] > 0) saveAsync(k);
  return out;
}QQQ.replace("@IST@", IST)), vst))
# under /pdadmin legacybags all: this profile's rarity bags back at its sweep; one chat line when bags came back, one per "make room" count
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int autoGive(@PR@ pr, @PLA@ p, String k, @PKG@.VoidState s) {
  boolean any = false;
  java.util.ArrayList l = new java.util.ArrayList(s.done);
  for (int i = 0; i < l.size() && !any; i++) { Object[] e = (Object[]) l.get(i); if ("R".equals(e[4]) && !s.given.contains(e[0])) any = true; }
  if (!any) return 0;
  int[] r = giveBackN(p, k);
  if (r[0] > 0 || r[1] > 0) migLog(k, "/pdadmin legacybags all: " + r[0] + " old bag(s) given back" + (r[1] > 0 ? ", " + r[1] + " waiting for free storage slots" : ""));
  if (r[0] > 0) { try { pr.sendMessage(@MSG@.raw("[SkyyVoid] The server is getting ready to switch back to Magic Bags: " + r[0] + " old bag" + (r[0] == 1 ? " that became Void rarity is" : "s that became Void rarity are") + " back in your inventory. Everything stored stays safe.").color("#cc66cc")); } catch (Throwable t) { } }
  if (r[1] > 0 && TOLD.putIfAbsent(k + ":" + r[1], Boolean.TRUE) == null) { try { pr.sendMessage(@MSG@.raw("[SkyyVoid] Make room for " + r[1] + " old Magic Bag" + (r[1] == 1 ? "" : "s") + " in your storage - they come back as soon as there is space.").color("#cc66cc")); } catch (Throwable t) { } }
  return r[0];
}QQQ), vst))
# fix round 2: does the inventory (storage / hotbar / backpack) hold an old bag? (only then does the sweep wait for the History copy)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean hasLegacy(@INV@ inv) {
  if (inv == null) return false;
  @IC@[] cs = conts(inv);
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short sl = 0; sl < cap; sl++) {
      @IS@ it = cs[c].getItemStack(sl);
      if (it != null && !it.isEmpty() && @PKG@.SackDefs.legacyRank(it.getItemId()) > 0) return true;
    }
  }
  return false;
}QQQ), vst))
# fix round 2 (rollback safety): under /pdadmin legacybags all the Pocket Dimension leaves storage / hotbar / backpack (SkyySacks 0.7.18
# does not know Skyy_Sack_Pocket - it is only the opener, nothing is stored in it); the one-time gift comes back after /pdadmin resume all.
# Returns the items removed (counted before / after).
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static int stripPocket(@INV@ inv, String k, @PKG@.VoidState s) {
  String id = @PKG@.SackDefs.POCKET;
  int before = countIn(inv, id, false);
  if (before <= 0) return 0;
  @IC@[] cs = conts(inv);
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short sl = 0; sl < cap; sl++) {
      @IS@ it = cs[c].getItemStack(sl);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      cs[c].removeItemStackFromSlot(sl, it.getQuantity());
    }
  }
  int gone = before - countIn(inv, id, false);
  if (gone > 0) {
    s.pocket = false;
    markDirty(k);
    migLog(k, "/pdadmin legacybags all: " + gone + " Pocket Dimension item(s) removed from the inventory (SkyySacks 0.7.18 does not know that item; nothing is stored in it - /pdadmin resume all gives it back)");
  }
  return gone;
}QQQ), vst))
# one Pocket Dimension item into storage; true = it fully fit (migrate's gift, /pd)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean givePocket(@INV@ inv) {
  try {
    @IST@ tx = inv.getStorage().addItemStack(new @IS@(@PKG@.SackDefs.POCKET, 1));
    @IS@ rem = tx == null ? null : tx.getRemainder();
    return tx != null && tx.succeeded() && (rem == null || rem.isEmpty());
  } catch (Throwable t) { return false; }
}QQQ.replace("@IST@", IST)), vst))
# THE MIGRATION STEP of the 2 s sweep (world thread, settled key): History first (false = wait: this sweep moves nothing), then recover,
# convert, the one-time welcome + Pocket item per profile, one chat + log line per conversion. true = the sweep may go on.
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean migrate(@PR@ pr, @PLA@ p, java.util.UUID u, String k) {
  @PKG@.VoidState s = st(k);
  if (s == null) return true;
  @INV@ inv = p.getInventory();
  // fix round 2: the History copy blocks the sweep only while an old bag is there to convert - a profile without one keeps its normal
  // sweep, stack refill and Requip top-up while the copy is made (or retried after a disk fault)
  if (s.first <= 0L) { scheduleSnap(k, u); return !hasLegacy(inv); }
  if (inv == null) return true;
  recover(inv, k, s);
  StringBuilder raised = new StringBuilder();
  int[] extra = new int[1];
  // fix round (rollback safety): while /pdadmin legacybags all (HOLDALL) or <player> (s.hold) is on, no old bag converts; under "all" each
  // profile gets its rarity bags back at its sweep (offline players at their next join), the chat says so once
  int n = 0;
  boolean held = HOLDALL;
  if (held || s.hold) {
    if (held) { autoGive(pr, p, k, s); stripPocket(inv, k, s); }
  } else n = convert(inv, k, s, raised, extra);
  // fix round 2 (less chat, Skyy 2026-10-12): the welcome and the Pocket item are ONE chat line
  String hello = "";
  if (!s.welcome) {
    s.welcome = true;
    markDirty(k);
    hello = "[SkyyVoid] Your storage is now the Void - one Pocket Dimension for everything you gather; each category levels up as you collect.";
  }
  if (!s.pocket && !held) {
    s.pocket = true;
    markDirty(k);
    if (countIn(inv, @PKG@.SackDefs.POCKET, false) <= 0) {
      boolean ok = givePocket(inv);
      String pl = ok ? "Here is your Pocket Dimension - right-click it or type /pd to open it (losing it loses nothing)." : "Your inventory is full - make room, then type /pd to get your Pocket Dimension.";
      hello = hello.length() > 0 ? hello + " " + pl : "[SkyyVoid] " + pl;
    }
  }
  if (hello.length() > 0) { try { pr.sendMessage(@MSG@.raw(hello.indexOf("/pd") < 0 ? hello + " Open it with /pd." : hello).color("#cc66cc")); } catch (Throwable t) { } }
  if (n > 0) {
    String line = "[SkyyVoid] Your Magic Bags became Void rarity" + (raised.length() > 0 ? ": " + raised : "") + (extra[0] > 0 ? ". " + extra[0] + " extra bag" + (extra[0] == 1 ? " is" : "s are") + " refunded into the Void (their crafting materials) in " + (SETTLE_MS / 1000L) + " seconds" : "") + ". Nothing was lost.";
    try { pr.sendMessage(@MSG@.raw(line).color("#cc66cc")); } catch (Throwable t) { }
    try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] Void migration " + k + ": " + n + " old bag(s) converted" + (raised.length() > 0 ? " (" + raised + ")" : "") + (extra[0] > 0 ? ", " + extra[0] + " refunded" : "") + " - credit after " + (SETTLE_MS / 1000L) + " s (journal pd/" + k + ".journal)"); } catch (Throwable t) { }
    migLog(k, "converted " + n + " old bag(s)" + (raised.length() > 0 ? ": " + raised : "") + (extra[0] > 0 ? "; " + extra[0] + " extra bag(s) refunded" : "") + " - journal pd/" + k + ".journal. UNDO: /pdadmin legacybags <player> (on this profile) gives the rarity bags back.");
  }
  return true;
}QQQ.replace("@IST@", IST)), vst))
# ---- THE UPGRADE (spec 2.3; world thread, the page): from = the rarity the click was made at (a second click of the same step = "already
# upgraded"); level gate; the cost from the Void first, then plain inventory stacks; all or nothing (pool re-credited, slots restored).
# Returns a page result line: "+" done, "-" refused, "=" info.
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static java.util.ArrayList slotSnap(@IC@[] cs) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) { out.add(null); continue; }
    short cap = cs[c].getCapacity();
    @IS@[] a = new @IS@[cap];
    for (short sl = 0; sl < cap; sl++) a[sl] = cs[c].getItemStack(sl);
    out.add(a);
  }
  return out;
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void slotRestore(@IC@[] cs, java.util.ArrayList snap) {
  for (int c = 0; c < cs.length; c++) {
    @IS@[] a = (@IS@[]) snap.get(c);
    if (a == null || cs[c] == null) continue;
    for (short sl = 0; sl < a.length; sl++) {
      @IS@ was = a[sl];
      @IS@ now = cs[c].getItemStack(sl);
      if (was == now) continue;
      if (was == null || was.isEmpty()) { if (now != null && !now.isEmpty()) cs[c].removeItemStackFromSlot(sl); }
      else cs[c].setItemStackForSlot(sl, was);
    }
  }
}QQQ), vst))
# take n plain items of id out of the slots (read back per slot); returns how many really left
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long takePlain(@IC@[] cs, String id, long n) {
  long got = 0L;
  for (int c = 0; c < cs.length && got < n; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short sl = 0; sl < cap && got < n; sl++) {
      @IS@ it = cs[c].getItemStack(sl);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      org.bson.BsonDocument md = it.getMetadata();
      if (md != null && !md.isEmpty()) continue;
      int q = it.getQuantity();
      int want = (long) q < n - got ? q : (int) (n - got);
      @ISS@ tx = cs[c].removeItemStackFromSlot(sl, want);
      if (tx == null || !tx.succeeded()) continue;
      @IS@ rem = tx.getRemainder();
      int r = want - (rem == null ? 0 : rem.getQuantity());
      if (r > 0) got += (long) r;
    }
  }
  return got;
}QQQ.replace("@ISS@", ISS)), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static String upgrade(@PLA@ p, java.util.UUID u, String k, int ci, int from) {
  if (ci < 0 || ci >= @PKG@.SackDefs.CATS.length) return "-Unknown category";
  String cat = @PKG@.SackDefs.CATS[ci];
  @PKG@.VoidState s = st(k);
  if (s == null) return "-The Void data of this profile cannot be read right now - nothing was taken";
  if (s.first <= 0L) return "-The Void is still getting ready - try again in a moment";
  if (omni(k)) return "=Omni already - every category is at the top";
  int cur = rarOf(k, ci);
  if (cur != from) return "=Already upgraded - " + cat + " is " + @PKG@.SackDefs.RNAME[cur];
  if (cur >= 3) return "=Legendary is the top - Omni comes with all six categories at Legendary";
  int to = cur + 1;
  int lv = level(u, k, ci);
  int g = @PKG@.SackCfg.gate(to);
  if (lv < g) return "-Needs " + cat + " Lv " + g + " (you: " + lv + ")";
  java.util.LinkedHashMap cost = @PKG@.SackCfg.parseCost(@PKG@.SackCfg.cost(ci, to));
  if (cost == null) return "-This upgrade's cost is not set correctly (Server Setup) - nothing was taken";
  @INV@ inv = p.getInventory();
  if (inv == null) return "-No inventory";
  @PKG@.BagMirror.beforeTake(k);
  java.util.Iterator it = cost.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    long need = ((Long) e.getValue()).longValue();
    long have = @PKG@.SackPool.get(k, id) + (long) countIn(inv, id, true);
    if (have < need) return "-Not enough " + id + " (" + have + " / " + need + ")";
  }
  @IC@[] cs = conts(inv);
  java.util.ArrayList snap = slotSnap(cs);
  java.util.LinkedHashMap fromPool = new java.util.LinkedHashMap();
  java.util.LinkedHashMap fromInv = new java.util.LinkedHashMap();
  String bad = null;
  try {
    it = cost.entrySet().iterator();
    while (it.hasNext() && bad == null) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      String id = (String) e.getKey();
      long need = ((Long) e.getValue()).longValue();
      long pp = @PKG@.SackPool.get(k, id);
      long tp = pp < need ? pp : need;
      if (tp > 0L) { @PKG@.SackPool.add(k, id, -tp); fromPool.put(id, Long.valueOf(tp)); }
      long rest = need - tp;
      if (rest > 0L) {
        long got = takePlain(cs, id, rest);
        if (got > 0L) fromInv.put(id, Long.valueOf(got));
        if (got < rest) bad = "-Not enough " + id + " any more - nothing was taken";
      }
    }
  } catch (Throwable t) { bad = "-Internal error - nothing was taken"; @PKG@.SackPool.warn("Void upgrade failed and was rolled back: " + t); }
  if (bad != null) {
    slotRestore(cs, snap);
    java.util.Iterator bi = fromPool.entrySet().iterator();
    while (bi.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) bi.next(); @PKG@.SackPool.add(k, (String) e.getKey(), ((Long) e.getValue()).longValue()); }
    return bad;
  }
  s.rar[ci] = to;
  boolean nowOmni = false;
  if (@PKG@.SackCfg.PD_OMNI_AUTO && !s.omni && legendCount(k) >= @PKG@.SackDefs.CATS.length) { s.omni = true; nowOmni = true; }
  markDirty(k);
  // fix round: ONE writer job saves the rarity and then the pool at once (was: the pool on the debounced saveSoon - a crash in between kept
  // the rarity and gave the paid Void items back); the inventory part still follows the engine's player save (the never-pay-without direction)
  @PKG@.SackPool.runOnWriter(new @PKG@.VoidJob(4, k, (java.util.UUID) null));
  java.util.Iterator ai = fromPool.keySet().iterator();
  while (ai.hasNext()) { try { @PKG@.BagMirror.afterTake(k, (String) ai.next()); } catch (Throwable t) { } }
  try { @PKG@.CraftLog.later(k, "VOID-UPGRADE " + cat + " " + @PKG@.SackDefs.RNAME[cur] + " -> " + @PKG@.SackDefs.RNAME[to] + " paid Void " + fromPool + " inventory " + fromInv + (nowOmni ? " -> OMNI" : "")); } catch (Throwable t) { }
  return "+" + cat + " is now " + @PKG@.SackDefs.RNAME[to] + (nowOmni ? " - all six are Legendary: your Void is OMNI" : "");
}QQQ), vst))
# the page's Deposit button (spec 3.1 / the amount box): up to n (n < 0 = all you carry) plain stacks of id from storage, hotbar and
# backpack into the Void, never past the category room. Returns what moved; -1 = this item never goes into the Void (catOf: cooked food
# while it stays out), -2 = the category is full, 0 = none carried
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static long depositInv(@PLA@ p, java.util.UUID u, String k, String id, long n) {
  String cat = @PKG@.SackDefs.catOf(id);
  if (cat == null) return -1L;
  int ci = @PKG@.SackDefs.catIndex(cat);
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null || ci < 0) return 0L;
  long have = (long) countIn(inv, id, true);
  if (have <= 0L) return 0L;
  Integer cc = (Integer) capsK(u, k).get(cat);
  long room = (cc == null ? 0L : cc.longValue()) - usedAll(k)[ci];
  if (room <= 0L) return -2L;
  long want = n < 0L ? have : (n < have ? n : have);
  if (want > room) want = room;
  long got = takePlain(conts(inv), id, want);
  if (got > 0L) {
    @PKG@.SackPool.add(k, id, got);
    noteIntake(k, ci, got);
    try { @PKG@.CraftLog.later(k, "VOID-DEPOSIT " + id + " " + got + " (page Deposit)"); } catch (Throwable t) { }
  }
  return got;
}QQQ), vst))
# sacks:fn:pd (spec 5): UUID -> Object[] of Object[]{String cat, Integer level, String rarity, Long cap, Long stored} for the ACTIVE profile
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static Object[] pdInfo(Object o) {
  if (!(o instanceof java.util.UUID)) return null;
  java.util.UUID u = (java.util.UUID) o;
  String k = @PKG@.SackPool.pkey(u);
  if (!@PKG@.SackPool.ready(k)) return null;
  String[] cats = @PKG@.SackDefs.CATS;
  long[] used = usedAll(k);
  Object[] out = new Object[cats.length];
  for (int i = 0; i < cats.length; i++) {
    int lv = level(u, k, i);
    int r = rank(k, i);
    out[i] = new Object[] { cats[i], Integer.valueOf(lv), @PKG@.SackDefs.RNAME[r], Long.valueOf(capOf(lv, r)), Long.valueOf(used[i]) };
  }
  return out;
}QQQ), vst))
# ---- /pdadmin legacybags <player>: the bags back (giveBackN) + this profile HELD (fix round: before, the next sweep converted the
# given-back bags again at once); /pdadmin resume <player> lets them convert again (no second credit: the tokens)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static String giveBack(@PLA@ p, String k) {
  @PKG@.VoidState s = st(k);
  if (s == null) return NOREAD;
  if (!s.hold) { s.hold = true; s.holdAt = Math.max(System.currentTimeMillis(), RESUMEALL + 1L); markDirty(k); }
  int[] r = giveBackN(p, k);
  if (r[2] == 1) return NOREAD;
  if (r[2] == 2) return "no inventory";
  saveAsync(k);   // the hold + tokens saved
  migLog(k, "/pdadmin legacybags: " + r[0] + " old bag(s) given back" + (r[1] > 0 ? ", " + r[1] + " waiting for free storage slots" : "") + (r[2] == 3 ? " (the journal could not be written - stopped)" : "") + "; old bags on this profile no longer convert until /pdadmin resume");
  if (r[2] == 3) return r[0] + " old bag(s) given back, then the journal could not be written - stopped (run it again)";
  return r[0] + " old bag(s) given back" + (r[1] > 0 ? " (" + r[1] + " more need free storage slots - run it again)" : "") + "; refunded bags stay refunded; old bags on this profile stay bags until /pdadmin resume";
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static String resume(String k) {
  @PKG@.VoidState s = st(k);
  if (s == null) return NOREAD;
  if (!s.hold) return "this profile was not held";
  s.hold = false;
  markDirty(k);
  saveAsync(k);
  migLog(k, "/pdadmin resume: old bags on this profile convert again (no second credit)");
  return "resumed - old bags on this profile turn into Void rarity again (no second credit)";
}QQQ), vst))
# /pdadmin legacybags all | resume all: the server-wide hold, kept in pd/_legacybags-all.flag (written + fsync'd; a restart keeps it)
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static boolean setHoldAll(boolean on) {
  if (DIR == null) return false;
  try {
    java.nio.file.Path f = DIR.resolve("_legacybags-all.flag");
    if (on) {
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.io.FileOutputStream out = new java.io.FileOutputStream(f.toFile());
      try { out.write(("/pdadmin legacybags all since " + new java.util.Date() + " - every profile gets its rarity bags back at its next sweep; no old bag converts. /pdadmin resume all removes this file." + System.lineSeparator()).getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
    } else {
      // fix round 2: the resume time, fsync'd BEFORE the flag goes - a profile loaded later whose saved hold is older is not held any more
      long now = Math.max(System.currentTimeMillis(), RESUMEALL + 1L);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path stp = DIR.resolve("_resume-all.stamp.tmp");
      java.io.FileOutputStream so = new java.io.FileOutputStream(stp.toFile());
      try { so.write((String.valueOf(now) + System.lineSeparator()).getBytes("UTF-8")); so.flush(); so.getFD().sync(); } finally { so.close(); }
      java.nio.file.Files.move(stp, DIR.resolve("_resume-all.stamp"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      RESUMEALL = now;
      java.nio.file.Files.deleteIfExists(f);
      java.util.Iterator it = STATES.values().iterator();
      while (it.hasNext()) { @PKG@.VoidState s = (@PKG@.VoidState) it.next(); if (s.hold) { s.hold = false; markDirty(s.key); } }
    }
    HOLDALL = on;
    TOLD.clear();
    migLog("ALL", on ? "/pdadmin legacybags all: every profile gets its rarity bags back at its next sweep (offline players at their next join); no old bag converts until /pdadmin resume all" : "/pdadmin resume all: old bags convert again (no second credit)");
    return true;
  } catch (Throwable t) {
    @PKG@.SackPool.warn("/pdadmin: could not " + (on ? "write" : "remove") + " pd/_legacybags-all.flag: " + t);
    return false;
  }
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static void loadHold() {
  try {
    java.nio.file.Path stp = DIR == null ? null : DIR.resolve("_resume-all.stamp");
    RESUMEALL = (stp != null && java.nio.file.Files.exists(stp, new java.nio.file.LinkOption[0])) ? num(new String(java.nio.file.Files.readAllBytes(stp), "UTF-8"), 0L) : 0L;
  } catch (Throwable t) { @PKG@.SackPool.warn("/pdadmin: could not read pd/_resume-all.stamp (holds saved before the last resume all may stay on): " + t); }
  try { HOLDALL = DIR != null && java.nio.file.Files.exists(DIR.resolve("_legacybags-all.flag"), new java.nio.file.LinkOption[0]); } catch (Throwable t) { HOLDALL = false; }
  if (HOLDALL) @PKG@.SackPool.warn("/pdadmin legacybags all is ON (pd/_legacybags-all.flag): old bags do not convert and every profile gets its rarity bags back - /pdadmin resume all ends it");
}QQQ), vst))
vst.addMethod(CtNewMethod.make(jt(rQQQ
public static String grantOmni(String k) {
  @PKG@.VoidState s = st(k);
  if (s == null) return NOREAD;
  if (s.omni) return "this profile's Void is Omni already";
  s.omni = true;
  markDirty(k);
  saveAsync(k);
  migLog(k, "/pdadmin omni: Omni granted");
  return "Omni granted - every category now has the Omni multiplier";
}QQQ), vst))

# ---- VoidJob: a writer-thread job. mode 1 = History snapshot of k (then the player is swept again), 2 = save pd/<k>, 3 = settle now,
# 4 = save pd/<k> then pools/<k> (the upgrade)
vjob.addMethod(CtNewMethod.make(jt(rQQQ
public void run() {
  try {
    if (this.mode == 1) {
      boolean ok = @PKG@.VoidStore.snapshot(this.k);
      @PKG@.VoidStore.SNAPQ.remove(this.k);
      if (ok && this.u != null) @PKG@.SweepTask.INVDIRTY.put(this.u, Boolean.TRUE);
    } else if (this.mode == 2) {
      @PKG@.VoidStore.saveNow(this.k);
    } else if (this.mode == 3) {
      @PKG@.VoidStore.settleDue(System.currentTimeMillis());
    } else if (this.mode == 4) {   // fix round: the upgrade - the rarity, then the pool, both now
      @PKG@.VoidStore.saveNow(this.k);
      if (@PKG@.SackPool.DIRTY.remove(this.k) != null) @PKG@.SackPool.save(this.k);
    }
  } catch (Throwable t) { @PKG@.SackPool.warn("Void job " + this.mode + " failed (retried later): " + t); }
}QQQ), vjob))

# ---- /pdadmin: VoidAdminTask runs on the TARGET's world thread (its Player component, its settled profile key)
vat.addInterface(pool.get("java.lang.Runnable"))
vat.addField(CtField.make("public int mode;", vat))
vat.addField(CtField.make(f"public {PR} admin;", vat))
vat.addField(CtField.make(f"public {PR} target;", vat))
vat.addConstructor(CtNewConstructor.make(f"public VoidAdminTask(int mode, {PR} admin, {PR} target) {{ this.mode = mode; this.admin = admin; this.target = target; }}", vat))
vat.addMethod(CtNewMethod.make(jt(rQQQ
public void run() {
  String msg;
  try {
    @REF@ r = this.target.getReference();
    @ST@ st = r == null ? null : r.getStore();
    @PLA@ p = st == null ? null : (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    String k = @PKG@.SackPool.settledKey(this.target.getUuid());
    if (p == null) msg = "that player is not in a world right now";
    else if (k == null) msg = "that player's profile is loading or switching - try again in a few seconds";
    else if (this.mode == 1) msg = @PKG@.VoidStore.giveBack(p, k);
    else if (this.mode == 3) msg = @PKG@.VoidStore.resume(k);
    else msg = @PKG@.VoidStore.grantOmni(k);
  } catch (Throwable t) { msg = "failed: " + t; }
  try { this.admin.sendMessage(@MSG@.raw("[SkyyVoid admin] " + this.target.getUsername() + ": " + msg)); } catch (Throwable t2) { }
}QQQ), vat))
vac.addConstructor(CtNewConstructor.make(("""
public PdAdminCmd() {
  super("pdadmin", "(admin) /pdadmin legacybags <player>|all | resume <player>|all | omni <player> - Void emergency tools (SkyyVoid)");
  requirePermission("skyysacks.admin");
  setAllowsExtraArguments(true);
}"""), vac))
vac.addMethod(CtNewMethod.make(jt(rQQQ
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String line = "";
    try { line = ctx.getInputString(); } catch (Throwable t) { line = ""; }
    String q = line == null ? "" : line.trim();
    if (q.startsWith("/")) q = q.substring(1).trim();
    String[] a = q.split("\\s+");
    int at = a.length > 0 && a[0].equalsIgnoreCase("pdadmin") ? 1 : 0;
    String act = a.length > at ? a[at].toLowerCase() : "";
    String who = a.length > at + 1 ? a[at + 1] : "";
    int mode = act.equals("legacybags") ? 1 : (act.equals("omni") ? 2 : (act.equals("resume") ? 3 : 0));
    if (mode == 0 || who.length() == 0) { pr.sendMessage(@MSG@.raw("[SkyyVoid admin] Usage: /pdadmin legacybags <player>|all (gives the old bags that became rarity back and stops old bags converting - before a rollback) | /pdadmin resume <player>|all | /pdadmin omni <player>")); return; }
    // fix round: "all" = the server-wide hold (pd/_legacybags-all.flag): every profile, offline players at their next join
    if (who.equalsIgnoreCase("all") && mode != 2) {
      boolean ok = @PKG@.VoidStore.setHoldAll(mode == 1);
      if (ok && mode == 1) {
        java.util.Iterator pi = @UNI@.get().getPlayers().iterator();
        while (pi.hasNext()) { @PR@ x = (@PR@) pi.next(); if (x != null && x.isValid() && x.getUuid() != null) @PKG@.SweepTask.INVDIRTY.put(x.getUuid(), Boolean.TRUE); }
      }
      pr.sendMessage(@MSG@.raw("[SkyyVoid admin] " + (!ok ? "failed - see the server log" : (mode == 1 ? "legacybags all is ON: old bags no longer convert; every player gets the bags that became rarity back at their next sweep (offline players when they join). Check Skyy_SkyySacks/migration.log, then roll back. /pdadmin resume all ends it." : "resume all: old bags turn into Void rarity again (no second credit)"))));
      return;
    }
    @PR@ target = null;
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ x = (@PR@) it.next();
      if (x != null && x.isValid() && who.equalsIgnoreCase(x.getUsername())) target = x;
    }
    if (target == null) { pr.sendMessage(@MSG@.raw("[SkyyVoid admin] No online player named " + who)); return; }
    @WLD@ w = @UNI@.get().getWorld(target.getWorldUuid());
    if (w == null) { pr.sendMessage(@MSG@.raw("[SkyyVoid admin] " + who + " is not in a world right now")); return; }
    w.execute(new @PKG@.VoidAdminTask(mode, pr, target));
  } catch (Throwable t) {
    @PKG@.SackPool.warn("/pdadmin failed: " + t);
    pr.sendMessage(@MSG@.raw("[SkyyVoid admin] failed - see the server log"));
  }
}QQQ.replace("@CTX@", CTX)), vac))

# CraftPage fields + constructor first (SacksPage references it)
'''))

# ================================================================================================= SweepTask.run: the Void step
rep(T(r'''    java.util.UUID u = pr.getUuid();
    INVDIRTY.remove(u);   // 0.7.18: cleared BEFORE the work - a change from here on marks the player again
    java.util.HashMap caps0 = caps(p.getInventory());   // 0.7.18: ONE caps() for the whole sweep
    try {{ {PKG}.KnowSync.sync(r, st, p, u); }} catch (Throwable t1) {{ {PKG}.KnowSync.warnOnce("bag recipe knowledge sync failed: " + t1); }}
    try {{ restamp(p.getInventory()); }} catch (Throwable t2) {{ {PKG}.KnowSync.warnOnce("bag rarity restamp failed: " + t2); }}
    try {{ if (!{PKG}.SackNotice.seen(u)) {PKG}.SackNotice.check(pr, u, k, !caps0.isEmpty()); }} catch (Throwable t3) {{ }}
    // 0.7.11: kept counts + the sweep + the stack refill (items above)
    items(p, k, u, caps0);'''), T(r'''    java.util.UUID u = pr.getUuid();
    INVDIRTY.remove(u);   // 0.7.18: cleared BEFORE the work - a change from here on marks the player again
    try {{ {PKG}.KnowSync.sync(r, st, p, u); }} catch (Throwable t1) {{ {PKG}.KnowSync.warnOnce("bag recipe knowledge sync failed: " + t1); }}   // 0.8.0: forgets the 21 bag recipes once
    // 0.8.0 (Bags v2 spec 4): the Void step - History copy first (until it is verified this sweep moves nothing and the player stays due),
    // then old bags in storage / hotbar / backpack convert (journal + 30 s credit), the one-time welcome + Pocket item per profile
    boolean go = true;
    try {{ go = {PKG}.VoidStore.migrate(pr, p, u, k); }} catch (Throwable t3) {{ {PKG}.KnowSync.warnOnce("Void migration step failed (retried): " + t3); }}
    if (!go) {{ INVDIRTY.put(u, Boolean.TRUE); return; }}
    java.util.HashMap caps0 = {PKG}.VoidStore.capsK(u, k);   // 0.8.0: ONE capacity map per sweep (levels from SkyyCollections)
    // 0.7.11: kept counts + the sweep + the stack refill (items above)
    items(p, k, u, caps0);'''))

# ================================================================================================= stack refill texts: "the Void"
rep(T(r'''RF_HELP = ("A hotbar stack you use tops back up from your bags every 2 seconds. Benches and inventory crafting use your bags too.",
           "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds. Benches and inventory crafting use your bags too.",
           "Stacks never top up by themselves - take items out on this page. Benches and inventory crafting still use your bags.")
RF_OFFSRV = "Stack refill is turned off on this server - your choice is kept. Benches and inventory crafting still use your bags."'''),
    T(r'''RF_HELP = ("A hotbar stack you use tops back up from the Void every 2 seconds. Benches and inventory crafting use the Void too.",
           "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds. Benches and inventory crafting use the Void too.",
           "Stacks never top up by themselves - take items out on this page. Benches and inventory crafting still use the Void.")
RF_OFFSRV = "Stack refill is turned off on this server - your choice is kept. Benches and inventory crafting still use the Void."   # 0.8.0 wording'''))
rep(T(r'''RF_HELP_B = ("A hotbar stack you use tops back up from your bags every 2 seconds. Benches use your bags too.",
             "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds. Benches use your bags too.",
             "Stacks never top up by themselves - take items out on this page. Benches still use your bags.")
RF_OFFSRV_B = "Stack refill is turned off on this server - your choice is kept. Benches still use your bags."'''),
    T(r'''RF_HELP_B = ("A hotbar stack you use tops back up from the Void every 2 seconds. Benches use the Void too.",
             "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds. Benches use the Void too.",
             "Stacks never top up by themselves - take items out on this page. Benches still use the Void.")
RF_OFFSRV_B = "Stack refill is turned off on this server - your choice is kept. Benches still use the Void."'''))

# ================================================================================================= THE VOID PAGE (SacksPage, rewritten)
cut(T(r'''# ================= SacksPage (SkyBlock-style: tabs, capacity, 9x4 icon grid, pick up all / deposit all) ================='''),
    T(r'''# ================= SacksCmd ================='''), T(r'''# ================= SacksPage = THE VOID PAGE (0.8.0, research/Bags-v2-Spec.md 3.1; docs/answered/ui.md 2026-10-10 amount box) =================
# The kit (tools/skyyui.py): page shell, groups, labels, buttons, icon cells, bars, the text field, the status line; the category tabs keep
# the deployed 0.7.7 tab style (rarity-coloured Tertiary). Left: six tabs (rarity colour, "Lv N - stored / space", a fill bar) + the Omni
# line. Middle: the header lines (stored / space bar, collected / next level bar, an amber over-limit line), the 36-cell grid with paging
# (click = select). Right: the selected item, the ONE amount box above Withdraw (every action uses it: Withdraw takes that many - empty =
# one stack; Deposit puts that many of the selected item from your inventory in - empty = all you carry), Pick up all, Deposit all,
# the Upgrade box (level gate, cost cells have / need, Upgrade -> Pay / Cancel). Bottom: the result line + the stack refill row.
page.addField(CtField.make("public String cat;", page))
page.addField(CtField.make("public String sel;", page))
page.addField(CtField.make("public int pageNo;", page))
page.addField(CtField.make("public String[] cells;", page))
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public String amount;", page))
page.addField(CtField.make("public boolean confirm;", page))
page.addField(CtField.make("public String key;", page))
page.addField(CtField.make("public String noticeKey;", page))
page.addField(CtField.make("public boolean carried;", page))   # kept (always true since 0.8.0: no bag needs to be carried)
page.addField(CtField.make("public " + REF + " builtRef;", page))
page.addConstructor(CtNewConstructor.make(f"""
public SacksPage({PR} pr, String cat) {{
  super(pr, {LIFE}.CanDismiss);
  this.cat = cat;
  this.info = "";
  this.amount = "";
  this.carried = true;
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
page.addMethod(CtNewMethod.make("""
public static String num(long v) {
  String d = String.valueOf(v < 0L ? -v : v);
  StringBuilder sb = new StringBuilder();
  int n = d.length();
  for (int i = 0; i < n; i++) {
    if (i > 0 && (n - i) % 3 == 0) sb.append(',');
    sb.append(d.charAt(i));
  }
  return (v < 0L ? "-" : "") + sb.toString();
}""", page))
# a cell's count in at most 6 characters (12,345 -> 12.3k)
page.addMethod(CtNewMethod.make(jt(rQQQ
public static String shortNum(long v) {
  if (v < 10000L) return num(v);
  if (v < 100000L) return (v / 1000L) + "." + ((v % 1000L) / 100L) + "k";
  if (v < 10000000L) return (v / 1000L) + "k";
  return (v / 1000000L) + "M";
}QQQ), page))
page.addMethod(CtNewMethod.make(jt(rQQQ
public static String multTxt(int r) {
  double m = @PKG@.SackCfg.mult(r);
  if (m == Math.floor(m)) return ((long) m) + ".0";
  return String.valueOf(m);
}QQQ), page))
page.addMethod(CtNewMethod.make(jt(rQQQ
public static int fill(long a, long b, int w) {
  if (b <= 0L || a <= 0L) return 0;
  if (a >= b) return w;
  long f = a * (long) w / b;
  return (int) (f < 0L ? 0L : f);
}QQQ), page))
page.addMethod(CtNewMethod.make(jt(rQQQ
public static String pretty(String id) {
  if (id == null) return "";
  String s = id;
  if (s.startsWith("Ingredient_")) s = s.substring(11);
  if (s.endsWith("_Item")) s = s.substring(0, s.length() - 5);
  return s.replace('_', ' ');
}QQQ), page))
# the first category with something stored, else Mining
page.addMethod(CtNewMethod.make(jt(rQQQ
public static int pickCat(String k) {
  long[] u = @PKG@.VoidStore.usedAll(k);
  for (int i = 0; i < u.length; i++) if (u[i] > 0L) return i;
  return 0;
}QQQ), page))
# a page event that carries the amount box (every Void page action reads it)
page.addMethod(CtNewMethod.make(jt(rQQQ
public static @EVD@ amtEvt(String a) {
  return @EVD@.of("a", a).append("@Amt", "#SkyyVAmt.Value");
}QQQ), page))
# one string value out of the page event JSON ("@Amt": "...") - CraftPage.jsonStr's rules (that class is compiled after this one)
page.addMethod(CtNewMethod.make(jt(rQQQ
public static String field(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 40) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}QQQ), page))
# the amount box: "" = dflt, "all" = everything, digits (commas / spaces / dots ignored) >= 1, anything else = -2 (refused)
page.addMethod(CtNewMethod.make(jt(rQQQ
public static long parseAmt(String a, long dflt) {
  if (a == null) return dflt;
  String t = a.trim().toLowerCase();
  if (t.length() == 0) return dflt;
  if (t.equals("all") || t.equals("max")) return 9223372036854775807L;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (c == ',' || c == ' ' || c == '.' || c == '_') continue;
    if (c < '0' || c > '9') return -2L;
    sb.append(c);
  }
  if (sb.length() == 0 || sb.length() > 12) return -2L;
  long n = Long.parseLong(sb.toString());
  return n < 1L ? -2L : n;
}QQQ), page))
page.addMethod(CtNewMethod.make(jt(rQQQ
public static int stackOf(String id) {
  try { @ITM@ it = @PKG@.ProcBench.item(id); if (it != null && it.getMaxStack() > 0) return it.getMaxStack(); } catch (Throwable t) { }
  return 64;
}QQQ), page))
# withdraw up to n (one stack at a time, SweepTask.withdraw: storage, the live-mirror rule, kept counts); stops when the storage is full
page.addMethod(CtNewMethod.make(jt(rQQQ
public static long withdrawN(@PLA@ p, String k, String id, long n) {
  long got = 0L;
  int st = stackOf(id);
  for (int guard = 0; guard < 2000 && got < n; guard++) {
    long want = n - got < (long) st ? n - got : (long) st;
    int added = @PKG@.SweepTask.withdraw(p, k, id, (int) want);
    got += (long) added;
    if ((long) added < want) break;
  }
  if (got > 0L) @PKG@.VoidStore.noteOut(k, @PKG@.SackDefs.catIndex(@PKG@.SackDefs.homeOf(id)), got);   // fix round: no level from re-depositing
  return got;
}QQQ), page))
# the deployed 0.7.7 tab look (a Tertiary button whose label has the category's rarity colour)
page.addField(CtField.make("public static final String SND = " + jlit('(Activate: (SoundPath: "Sounds/ButtonsLightActivate.ogg", MinPitch: -0.4, MaxPitch: 0.4, Volume: 4), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))') + ";", page))
page.addMethod(CtNewMethod.make(jt(rQQQ
public static String tabStyle(boolean sel, String col) {
  String ls = "LabelStyle: (FontSize: 14, TextColor: " + col + ", RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  String d = sel ? "Tertiary_Active" : "Tertiary";
  String h = sel ? "Tertiary_Active" : "Tertiary_Hovered";
  return "Style: TextButtonStyle(Default: (Background: (TexturePath: \"Common/Buttons/" + d + ".png\", Border: 12), " + ls + "), Hovered: (Background: (TexturePath: \"Common/Buttons/" + h + ".png\", Border: 12), " + ls + "), Pressed: (Background: (TexturePath: \"Common/Buttons/Tertiary_Pressed.png\", Border: 12), " + ls + "), Sounds: " + SND + ");";
}QQQ), page))
for _src in SUI.java_status_methods():   # colorOf / textOf of the result line (+ done, - refused, = info)
    page.addMethod(CtNewMethod.make(_src, page))
# 0.7.11 the STACK REFILL row (a per-player setting): the kit's settings row with three small tertiary buttons and a one-line explanation
SUI.verify()
KIT_ID = SUI.kit_id()
RF_SUF = ("Hotbar", "Full", "Off")                      # button id suffixes, in RefillPref.WORDS order
RF_ROW_LABEL = "Stack refill from the Void"
RF_BTN_W, RF_GAP, RF_LABEL_W, RF_HELP_H = 176, 6, 380, 24
RF_ROW = SUI.setting_row("SkyySRefill", "SkyySRefillLbl", label_w=RF_LABEL_W, gap=0)
RF_BTNS = [tuple(SUI.button("SkyySRefill" + RF_SUF[i], RF_LABELS[i], "tertiary", "small", w=RF_BTN_W, selected=sel,
                            anchor={"top": (SUI.SETTING_ROW_H - SUI.BTN_SMALL_H) // 2, "left": RF_GAP if i else 0})
                 for sel in (True, False)) for i in range(3)]
RF_HELP_LBL = SUI.label("SkyySRefillHelp", "", "caption", h=RF_HELP_H, align="Center")
SUI.assert_proven([RF_ROW, RF_HELP_LBL] + [mk for pair in RF_BTNS for mk in pair], what="SkyyVoid stack refill row")
RF_ROW_H = SUI.outer_size(RF_ROW)[1]
RF_JAVA = "\n".join(["  " + SUI.java_append("SkyySBody", RF_ROW), "  " + SUI.java_set("SkyySRefillLbl", "Text", RF_ROW_LABEL)]
                    + ["  " + SUI.java_append("SkyySRefill", SUI.choose("rmode == %d" % i, RF_BTNS[i][0], RF_BTNS[i][1])) for i in range(3)]
                    + ['  ev.addEventBinding(@BT@.Activating, "#SkyySRefill%s", @EVD@.of("a", "refill:%s"));' % (RF_SUF[i], RF_WORDS[i])
                       for i in range(3)]
                    + ["  " + SUI.java_append("SkyySBody", RF_HELP_LBL)])
page.addMethod(CtNewMethod.make(jt(rQQQ
public void refillRow(@UCB@ b, @UEB@ ev, int rmode) {
@RFJAVA@
  int m = rmode < 0 || rmode >= @PKG@.RefillPref.HELP.length ? 0 : rmode;
  boolean pc = @PKG@.SackCfg.POCKET_CRAFT;
  b.set("#SkyySRefillHelp.Text", @PKG@.SackCfg.REFILL_ON ? (pc ? @PKG@.RefillPref.HELP[m] : @PKG@.RefillPref.HELPB[m]) : (pc ? @PKG@.RefillPref.OFFSRV : @PKG@.RefillPref.OFFSRVB));
}QQQ.replace("@RFJAVA@", RF_JAVA)), page))

# ---- the page markup (kit), sizes checked here
VP_W, VP_H = 1300, 690                         # the 0.7.11 footprint height (the player inventory window shows with it)
VSH = SUI.page_shell("SkyyV", VP_W, VP_H, title="SkyyVoid", root_id="SkyySacks", body_id="SkyySBody", bar_id="SkyyVBar", title_id="SkyyVTitle")
VIN_W, VIN_H = VSH.inner_w, VSH.inner_h
V_TAB_W, V_MID_W, V_SIDE_W, V_GAP = 220, 682, 340, 12
V_TOP_H, V_MAIN_H, V_INFO_H, V_UP_H = 34, 478, 26, 226
assert V_TAB_W + V_GAP + V_MID_W + V_GAP + V_SIDE_W == VIN_W, (VIN_W,)
assert 9 * 74 + 8 * 2 == V_MID_W
assert V_TOP_H + V_MAIN_H + V_INFO_H + RF_ROW_H + RF_HELP_H <= VIN_H, "the Void page is taller than its body"
assert 6 * (34 + 18 + 5 + 6) + 44 <= V_MAIN_H, "tabs column"
assert 22 + 8 + 4 + 22 + 8 + 4 + 22 + 4 * 78 + 36 <= V_MAIN_H, "middle column"
assert 70 + 22 + 38 + 6 + 44 + 4 + 44 + 10 + V_UP_H <= V_MAIN_H, "side column"
assert 16 + 24 + 20 + 20 + 3 * 34 + 44 <= V_UP_H, "upgrade box"
assert 16 + RF_LABEL_W + 3 * RF_BTN_W + 2 * RF_GAP <= VIN_W
J_ = SUI.J
VM = {
    "top": SUI.group("SkyyVTop", "Left", h=V_TOP_H),
    "head": SUI.label("SkyyVHead", "", "strong", w=VIN_W - 160, h=V_TOP_H, size=20, col=J_("hcol", "#ffffff")),
    "craft": SUI.button("SkyyVCraft", "Craft", "secondary", "small", w=150, anchor={"left": 10}),
    "main": SUI.group("SkyyVMain", "Left", h=V_MAIN_H),
    "tabs": SUI.group("SkyyVTabs", "Top", w=V_TAB_W, h=V_MAIN_H),
    "tablv": SUI.label("SkyyVTabLv" + J_("i"), "", "caption", w=V_TAB_W, h=18, align="Center"),
    "tabbar": SUI.bar("SkyyVTabBar" + J_("i"), V_TAB_W, 5, J_("tf", "110"), col=J_("tcol", "#ffffff")),
    "tabgap": SUI.spacer(h=6),
    "omni": SUI.label("SkyyVOmni", "", "default", w=V_TAB_W, h=44, size=14, wrap=True, align="Center", col=J_("ocol", "#cc66cc")),
    "gap": SUI.spacer(w=V_GAP),
    "mid": SUI.group("SkyyVMid", "Top", w=V_MID_W, h=V_MAIN_H),
    "store": SUI.label("SkyyVStore", "", "bold", w=V_MID_W, h=22, size=16),
    "storebar": SUI.bar("SkyyVStoreBar", V_MID_W, 8, J_("sf", "300"), col=J_("scol", "#aa7c4a")),
    "sp4": SUI.spacer(h=4),
    "level": SUI.label("SkyyVLevel", "", "default", w=V_MID_W, h=22, size=15),
    "levelbar": SUI.bar("SkyyVLevelBar", V_MID_W, 8, J_("lf", "300"), col="progressBlue"),
    "sp4b": SUI.spacer(h=4),
    "warn": SUI.label("SkyyVWarn", "", "default", w=V_MID_W, h=22, size=14, col=J_("wcol", "#E8A93B")),
    "row": SUI.group("SkyyVRow" + J_("r"), "Left", h=78, pad={"top": 2, "bottom": 2}),
    "cell": SUI.choose("sel != null && sel.equals(cid)",
                       SUI.icon_cell("SkyyVCell" + J_("idx"), item=J_("safe(cid)", "Ore_Copper"), size=74, state="selected", qty=True),
                       SUI.icon_cell("SkyyVCell" + J_("idx"), item=J_("safe(cid)", "Ore_Copper"), size=74, state="normal", qty=True)),
    "cellempty": SUI.icon_cell("SkyyVCell" + J_("idx"), size=74, state="empty"),
    "cellgap": SUI.spacer(w=2),
    "pager": SUI.group("SkyyVPager", "Left", h=36, pad={"top": 4}),
    "prev": SUI.choose("pageNo > 0", SUI.button("SkyyVPrev", "< Prev", "secondary", "small", w=120),
                       SUI.button("SkyyVPrev", "< Prev", "secondary", "small", w=120, disabled=True)),
    "pagel": SUI.label("SkyyVPage", "", "caption", w=V_MID_W - 240, h=32, align="Center"),
    "next": SUI.choose("pageNo < pages - 1", SUI.button("SkyyVNext", "Next >", "secondary", "small", w=120),
                       SUI.button("SkyyVNext", "Next >", "secondary", "small", w=120, disabled=True)),
    "side": SUI.group("SkyyVSide", "Top", w=V_SIDE_W, h=V_MAIN_H),
    "selrow": SUI.group("SkyyVSelRow", "Left", h=70),
    "selic": SUI.choose("sel != null", SUI.icon_cell("SkyyVSelIc", item=J_("safe(sel)", "Ore_Copper"), size=66, state="static", look="plain"),
                        SUI.icon_cell("SkyyVSelIc", size=66, state="static", look="plain")),
    "selcol": SUI.group("SkyyVSelCol", "Top", w=V_SIDE_W - 76, anchor={"left": 10}),
    "selname": SUI.label("SkyyVSelName", "", "strong", w=V_SIDE_W - 76, h=30, size=17),
    "selcount": SUI.label("SkyyVSelCount", "", "caption", w=V_SIDE_W - 76, h=36, wrap=True),
    "amtlbl": SUI.label("SkyyVAmtLbl", "Amount", "section", w=V_SIDE_W, h=22),
    "amt": SUI.text_field("SkyyVAmtBox", "SkyyVAmt", w=V_SIDE_W, h=38, placeholder="empty is one stack or all on Deposit", max_length=12),
    "btns1": SUI.group("SkyyVBtnsA", "Left", h=44, anchor={"top": 6}),
    "wd": SUI.button("SkyyVWd", "Withdraw", "primary", w=167),
    "dep": SUI.button("SkyyVDep", "Deposit", "secondary", w=167, anchor={"left": 6}),
    "btns2": SUI.group("SkyyVBtnsB", "Left", h=44, anchor={"top": 4}),
    "pick": SUI.button("SkyyVPick", "Pick up all", "secondary", w=167),
    "depall": SUI.button("SkyyVDepAll", "Deposit all", "secondary", w=167, anchor={"left": 6}),
    "up": SUI.group("SkyyVUp", "Top", w=V_SIDE_W, h=V_UP_H, anchor={"top": 10}, pad=8, bg="well"),
    "uptitle": SUI.label("SkyyVUpTitle", "", "strong", w=V_SIDE_W - 16, h=24, size=16, col=J_("ucol", "#ffff55")),
    "upsub": SUI.label("SkyyVUpSub", "", "default", w=V_SIDE_W - 16, h=20, size=14),
    "upgate": SUI.label("SkyyVUpGate", "", "default", w=V_SIDE_W - 16, h=20, size=14, col=J_("gcol", "#3d913f")),
    "costrow": SUI.group("SkyyVCostR" + J_("cr"), "Left", h=34),
    "costic": SUI.icon_cell("SkyyVCost" + J_("cx"), item=J_("safe(cid2)", "Ore_Iron"), size=32, state="static", look="plain"),
    "costt": SUI.label("SkyyVCostT" + J_("cx"), "", "default", w=130, h=32, size=13, col=J_("ccol", "#3d913f"), anchor={"left": 4}),
    "upbtnrow": SUI.group("SkyyVUpBtns", "Left", h=40, anchor={"top": 4}),
    "upbtn": SUI.choose("ready", SUI.button("SkyyVUpBtn", "Upgrade", "primary", "small", w=160),
                        SUI.button("SkyyVUpBtn", "Upgrade", "primary", "small", w=160, disabled=True)),
    "upyes": SUI.button("SkyyVUpYes", "Pay", "primary", "small", w=150),
    "upno": SUI.button("SkyyVUpNo", "Cancel", "secondary", "small", w=150, anchor={"left": 8}, sound="cancel"),
    "info": SUI.status_line("SkyySInfo", color_expr="colorOf(this.info)", h=V_INFO_H),
}
_vflat = []
for _mk in VM.values():
    _vflat.extend(_mk.variants() if isinstance(_mk, SUI.Choice) else [_mk])
SUI.assert_proven(_vflat + [m for _p, m in VSH.appends], what="SkyyVoid page")
for _mk in _vflat:
    SUI.check_markup(_mk)
VCOL = {"gold": SUI.COLOR["gold"], "text": SUI.COLOR["text"], "have": SUI.COLOR["have"], "out": SUI.COLOR["outOfStock"],
        "caption": SUI.COLOR["caption"], "fill": SUI.COLOR["progressFill"]}
def vexpr(mk):
    if isinstance(mk, SUI.Choice):
        return "((%s) ? (%s) : (%s))" % (mk.cond, SUI.java_value(mk.a), SUI.java_value(mk.b))
    return SUI.java_value(mk)
def vpage(src):
    import re as _re
    for _n, _mk in VM.items():
        src = src.replace("@@%s@@" % _n, vexpr(_mk))
    for _n, _c in VCOL.items():
        src = src.replace("@C:%s@" % _n, _c)
    src = src.replace("@SHELL@", VSH.java("b")).replace("@TABW@", str(V_TAB_W)).replace("@MIDW@", str(V_MID_W))
    left = _re.findall(r"@@[a-z0-9]+@@|@C:[a-z]+@", src)
    assert not left, left
    return jt(src)
page.addMethod(CtNewMethod.make(vpage(rQQQ
public void upgradeBox(@UCB@ b, @UEB@ ev, @INV@ inv, String k, java.util.UUID u, int ci, int lv, int rk, long cap, boolean omni) {
  String[] cats = @PKG@.SackDefs.CATS;
  int cur = @PKG@.VoidStore.rarOf(k, ci);
  int to = cur + 1;
  String ucol;
  String t1;
  String t2 = "";
  String t3 = "";
  String gcol = "@C:text@";
  boolean ready = false;
  boolean canUp = false;
  java.util.LinkedHashMap cost = null;
  if (omni) {
    ucol = @PKG@.SackDefs.RCOL[4];
    t1 = "Omni - the top of every category";
    t2 = "Space x" + multTxt(4) + " in all six categories";
  } else if (cur >= 3) {
    ucol = @PKG@.SackDefs.RCOL[3];
    t1 = "Legendary - the top rarity";
    t2 = "Omni comes when all six categories are Legendary";
    t3 = @PKG@.VoidStore.legendCount(k) + " of " + cats.length + " are Legendary";
  } else {
    canUp = true;
    ucol = @PKG@.SackDefs.RCOL[to];
    t1 = "Upgrade to " + @PKG@.SackDefs.RNAME[to] + " (x" + multTxt(to) + ")";
    t2 = "Space " + num(cap) + " -> " + num(@PKG@.VoidStore.capOf(lv, to));
    int g = @PKG@.SackCfg.gate(to);
    boolean gateOk = lv >= g;
    t3 = gateOk ? ("Level gate " + cats[ci] + " Lv " + g + " - done") : ("Needs " + cats[ci] + " Lv " + g + " (you: " + lv + ")");
    gcol = gateOk ? "@C:have@" : "@C:out@";
    cost = @PKG@.SackCfg.parseCost(@PKG@.SackCfg.cost(ci, to));
    ready = gateOk && cost != null;
    if (cost == null) t3 = "This step's cost is not set right (Server Setup)";
  }
  b.appendInline("#SkyyVSide", @@up@@);
  b.appendInline("#SkyyVUp", @@uptitle@@);
  b.set("#SkyyVUpTitle.Text", (this.confirm && canUp) ? ("Pay these items for " + @PKG@.SackDefs.RNAME[to] + "?") : t1);
  b.appendInline("#SkyyVUp", @@upsub@@);
  b.set("#SkyyVUpSub.Text", t2);
  b.appendInline("#SkyyVUp", @@upgate@@);
  b.set("#SkyyVUpGate.Text", t3);
  java.util.ArrayList ce = cost == null ? new java.util.ArrayList() : new java.util.ArrayList(cost.entrySet());
  for (int cr = 0; cr < 3; cr++) {
    b.appendInline("#SkyyVUp", @@costrow@@);
    for (int j = 0; j < 2; j++) {
      int cx = cr * 2 + j;
      if (cx >= ce.size()) continue;
      java.util.Map.Entry e = (java.util.Map.Entry) ce.get(cx);
      String cid2 = (String) e.getKey();
      long need = ((Long) e.getValue()).longValue();
      long have = @PKG@.SackPool.get(k, cid2) + (long) @PKG@.VoidStore.countIn(inv, cid2, true);
      boolean ok = have >= need;
      if (!ok) ready = false;
      String ccol = ok ? "@C:have@" : "@C:out@";
      b.appendInline("#SkyyVCostR" + cr, @@costic@@);
      b.appendInline("#SkyyVCostR" + cr, @@costt@@);
      b.set("#SkyyVCostT" + cx + ".Text", shortNum(have) + " / " + shortNum(need));
    }
  }
  b.appendInline("#SkyyVUp", @@upbtnrow@@);
  if (canUp && this.confirm && ready) {
    b.appendInline("#SkyyVUpBtns", @@upyes@@);
    b.appendInline("#SkyyVUpBtns", @@upno@@);
    ev.addEventBinding(@BT@.Activating, "#SkyyVUpYes", amtEvt("upgok:" + ci + ":" + cur));
    ev.addEventBinding(@BT@.Activating, "#SkyyVUpNo", amtEvt("upgno"));
  } else if (canUp) {
    this.confirm = false;
    b.appendInline("#SkyyVUpBtns", @@upbtn@@);
    if (ready) ev.addEventBinding(@BT@.Activating, "#SkyyVUpBtn", amtEvt("upg"));
  } else {
    this.confirm = false;
  }
}QQQ), page))
page.addMethod(CtNewMethod.make(vpage(rQQQ
public void render(@UCB@ b, @UEB@ ev, @PLA@ player, String k, java.util.UUID u) {
  this.key = k;
  this.carried = true;
  String[] cats = @PKG@.SackDefs.CATS;
  int nc = cats.length;
  int ci = @PKG@.SackDefs.catIndex(this.cat);
  if (ci < 0) { ci = pickCat(k); this.cat = cats[ci]; }
  @INV@ inv = player == null ? null : player.getInventory();
  int[] lv = new int[nc];
  int[] rk = new int[nc];
  long[] cap = new long[nc];
  long[] used = @PKG@.VoidStore.usedAll(k);
  for (int i = 0; i < nc; i++) {
    lv[i] = @PKG@.VoidStore.level(u, k, i);
    rk[i] = @PKG@.VoidStore.rank(k, i);
    cap[i] = @PKG@.VoidStore.capOf(lv[i], rk[i]);
  }
  boolean omni = @PKG@.VoidStore.omni(k);
@SHELL@
  String hcol = @PKG@.SackDefs.RCOL[rk[ci]];
  b.appendInline("#SkyySBody", @@top@@);
  b.appendInline("#SkyyVTop", @@head@@);
  b.set("#SkyyVHead.Text", cats[ci] + " - Lv " + lv[ci] + " - " + @PKG@.SackDefs.RNAME[rk[ci]] + " (x" + multTxt(rk[ci]) + ")");
  b.appendInline("#SkyyVTop", @@craft@@);
  ev.addEventBinding(@BT@.Activating, "#SkyyVCraft", @EVD@.of("a", "craft"));
  b.appendInline("#SkyySBody", @@main@@);
  b.appendInline("#SkyyVMain", @@tabs@@);
  for (int i = 0; i < nc; i++) {
    String tcol = @PKG@.SackDefs.RCOL[rk[i]];
    b.appendInline("#SkyyVTabs", "TextButton #SkyyVTab" + i + " { Anchor: (Width: @TABW@, Height: 34); Text: \"" + cats[i] + "\"; " + tabStyle(i == ci, tcol) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyVTab" + i, amtEvt("tab:" + cats[i]));
    b.appendInline("#SkyyVTabs", @@tablv@@);
    b.set("#SkyyVTabLv" + i + ".Text", "Lv " + lv[i] + " - " + shortNum(used[i]) + " / " + shortNum(cap[i]));
    int tf = fill(used[i], cap[i], @TABW@);
    b.appendInline("#SkyyVTabs", @@tabbar@@);
    b.appendInline("#SkyyVTabs", @@tabgap@@);
  }
  String ocol = omni ? @PKG@.SackDefs.RCOL[4] : "@C:caption@";
  b.appendInline("#SkyyVTabs", @@omni@@);
  b.set("#SkyyVOmni.Text", omni ? ("OMNI - every category x" + multTxt(4)) : ("Omni: get all six categories to Legendary (" + @PKG@.VoidStore.legendCount(k) + " / " + nc + ")"));
  b.appendInline("#SkyyVMain", @@gap@@);
  b.appendInline("#SkyyVMain", @@mid@@);
  long st0 = used[ci];
  String scol = st0 > cap[ci] ? "@C:gold@" : "@C:fill@";
  b.appendInline("#SkyyVMid", @@store@@);
  b.set("#SkyyVStore.Text", "Stored " + num(st0) + " / " + num(cap[ci]) + " items");
  int sf = fill(st0, cap[ci], @MIDW@);
  b.appendInline("#SkyyVMid", @@storebar@@);
  b.appendInline("#SkyyVMid", @@sp4@@);
  int max = @PKG@.SackCfg.PD_MAX_LEVEL;
  long tot = @PKG@.VoidStore.total(u, k, ci);
  b.appendInline("#SkyyVMid", @@level@@);
  int lf = @MIDW@;
  if (lv[ci] >= max) b.set("#SkyyVLevel.Text", "Max storage level " + lv[ci] + " - upgrade the rarity for more space");
  else {
    long nxt = @PKG@.VoidStore.totalFor(lv[ci] + 1, ci);
    long cur0 = @PKG@.VoidStore.totalFor(lv[ci], ci);
    long more = @PKG@.VoidStore.capOf(lv[ci] + 1, rk[ci]) - cap[ci];
    b.set("#SkyyVLevel.Text", num(tot) + " / " + num(nxt) + " collected to Lv " + (lv[ci] + 1) + " (+" + num(more) + " space)");
    lf = fill(tot - cur0, nxt - cur0, @MIDW@);
  }
  b.appendInline("#SkyyVMid", @@levelbar@@);
  b.appendInline("#SkyyVMid", @@sp4b@@);
  String wtxt = "";
  String wcol = "@C:gold@";
  if (st0 > cap[ci]) wtxt = "Over the limit (" + num(st0) + " / " + num(cap[ci]) + ") - nothing new goes in until you take some out";
  else if ("Farming".equals(cats[ci]) && !@PKG@.SackDefs.COOKED_FARM) {
    long ck = @PKG@.SackPool.cookedTotal(k);
    if (ck > 0L) { wtxt = "Cooked food no longer goes in - " + num(ck) + (ck == 1L ? " cooked item is" : " cooked items are") + " still here to take out"; wcol = "@C:text@"; }
  }
  b.appendInline("#SkyyVMid", @@warn@@);
  b.set("#SkyyVWarn.Text", wtxt);
  java.util.ArrayList entries = new java.util.ArrayList();
  java.util.Iterator it = @PKG@.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (cats[ci].equals(@PKG@.SackDefs.homeOf((String) e.getKey()))) entries.add(e);
  }
  java.util.Collections.sort(entries, new @PKG@.CountCmp());
  if ("Farming".equals(cats[ci]) && !@PKG@.SackDefs.COOKED_FARM) {
    java.util.ArrayList ckFirst = new java.util.ArrayList();
    java.util.ArrayList rawRest = new java.util.ArrayList();
    for (int q = 0; q < entries.size(); q++) {
      java.util.Map.Entry ce = (java.util.Map.Entry) entries.get(q);
      if (@PKG@.SackDefs.cooked((String) ce.getKey())) ckFirst.add(ce); else rawRest.add(ce);
    }
    ckFirst.addAll(rawRest);
    entries = ckFirst;
  }
  int pages = (entries.size() + 35) / 36;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  this.cells = new String[36];
  String sel = this.sel;
  for (int r = 0; r < 4; r++) {
    b.appendInline("#SkyyVMid", @@row@@);
    for (int c = 0; c < 9; c++) {
      int idx = r * 9 + c;
      int at = this.pageNo * 36 + idx;
      if (at < entries.size()) {
        java.util.Map.Entry e = (java.util.Map.Entry) entries.get(at);
        String cid = (String) e.getKey();
        long cnt = ((Long) e.getValue()).longValue();
        this.cells[idx] = cid;
        b.appendInline("#SkyyVRow" + r, @@cell@@);
        b.set("#SkyyVCell" + idx + "Qty.Text", shortNum(cnt));
        ev.addEventBinding(@BT@.Activating, "#SkyyVCell" + idx, amtEvt("cell:" + idx));
      } else {
        b.appendInline("#SkyyVRow" + r, @@cellempty@@);
      }
      if (c < 8) b.appendInline("#SkyyVRow" + r, @@cellgap@@);
    }
  }
  b.appendInline("#SkyyVMid", @@pager@@);
  b.appendInline("#SkyyVPager", @@prev@@);
  b.appendInline("#SkyyVPager", @@pagel@@);
  b.set("#SkyyVPage.Text", "Page " + (this.pageNo + 1) + " / " + pages + " - " + entries.size() + (entries.size() == 1 ? " kind of item" : " kinds of items"));
  b.appendInline("#SkyyVPager", @@next@@);
  if (this.pageNo > 0) ev.addEventBinding(@BT@.Activating, "#SkyyVPrev", amtEvt("pg:prev"));
  if (this.pageNo < pages - 1) ev.addEventBinding(@BT@.Activating, "#SkyyVNext", amtEvt("pg:next"));
  b.appendInline("#SkyyVMain", @@gap@@);
  b.appendInline("#SkyyVMain", @@side@@);
  b.appendInline("#SkyyVSide", @@selrow@@);
  b.appendInline("#SkyyVSelRow", @@selic@@);
  b.appendInline("#SkyyVSelRow", @@selcol@@);
  b.appendInline("#SkyyVSelCol", @@selname@@);
  b.appendInline("#SkyyVSelCol", @@selcount@@);
  if (sel != null) {
    b.set("#SkyyVSelName.Text", pretty(sel));
    b.set("#SkyyVSelCount.Text", "In the Void " + num(@PKG@.SackPool.get(k, sel)) + " - on you " + num((long) @PKG@.VoidStore.countIn(inv, sel, false)));
  } else {
    b.set("#SkyyVSelName.Text", "Pick an item");
    b.set("#SkyyVSelCount.Text", "Click an item in the grid, type an amount, then Withdraw or Deposit.");
  }
  b.appendInline("#SkyyVSide", @@amtlbl@@);
  b.appendInline("#SkyyVSide", @@amt@@);
  if (this.amount != null && this.amount.length() > 0) b.set("#SkyyVAmt.Value", this.amount);
  b.appendInline("#SkyyVSide", @@btns1@@);
  b.appendInline("#SkyyVBtnsA", @@wd@@);
  b.appendInline("#SkyyVBtnsA", @@dep@@);
  ev.addEventBinding(@BT@.Activating, "#SkyyVWd", amtEvt("wd"));
  ev.addEventBinding(@BT@.Activating, "#SkyyVDep", amtEvt("dep"));
  b.appendInline("#SkyyVSide", @@btns2@@);
  b.appendInline("#SkyyVBtnsB", @@pick@@);
  b.appendInline("#SkyyVBtnsB", @@depall@@);
  ev.addEventBinding(@BT@.Activating, "#SkyyVPick", amtEvt("pickall"));
  ev.addEventBinding(@BT@.Activating, "#SkyyVDepAll", amtEvt("depall"));
  upgradeBox(b, ev, inv, k, u, ci, lv[ci], rk[ci], cap[ci], omni);
  b.appendInline("#SkyySBody", @@info@@);
  b.set("#SkyySInfo.Text", textOf(this.info));
  refillRow(b, ev, @PKG@.RefillPref.choice(u));
}QQQ), page))
page.addMethod(CtNewMethod.make(jt(rQQQ
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  if (u != null) @PKG@.ProcTask.PAGEOPEN.put(u, Boolean.TRUE);   // 0.7.18: the 1 s task keeps visiting (the profile notice)
  String k = @PKG@.SackPool.pkey(u);
  @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  render(b, ev, player, k, u);
}QQQ), page))
page.addMethod(CtNewMethod.make(jt(rQQQ
public void onEvent(@REF@ ref, @ST@ st, @PLA@ player0, String data) {
  try {
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    String[] cats = @PKG@.SackDefs.CATS;
    // fix round: the action is the "a" field compared EQUAL (was: a search of the whole event text - typing "upgok:2:0" or "craft" in the
    // amount box fired that action); every event of this page carries the amount box, so a click never empties it
    String a = field(data, "a");
    String qa = String.valueOf((char) 34) + "@Amt" + String.valueOf((char) 34);
    if (data.indexOf(qa) >= 0) this.amount = field(data, "@Amt");
    for (int c = 0; c < cats.length; c++) {
      if (a.equals("tab:" + cats[c])) { this.cat = cats[c]; this.pageNo = 0; this.sel = null; this.confirm = false; this.info = ""; rebuild(); return; }
    }
    if (a.equals("craft")) {
      if (player0 != null) player0.getPageManager().openCustomPage(ref, st, new @PKG@.CraftPage(this.playerRef, (String) null));
      return;
    }
    for (int m = 0; m < @PKG@.RefillPref.WORDS.length; m++) {
      if (a.equals("refill:" + @PKG@.RefillPref.WORDS[m])) {
        @PKG@.RefillPref.set(u, m);
        this.info = "=Stack refill: " + @PKG@.RefillPref.LABELS[m] + (@PKG@.SackCfg.REFILL_ON ? "" : " (turned off on this server for now)");
        @PKG@.SackPool.saveSoon((String) null);
        rebuild();
        return;
      }
    }
    for (int i = 0; i < 36; i++) {
      if (a.equals("cell:" + i)) {
        if (this.cells != null && this.cells[i] != null) this.sel = this.cells[i];
        this.info = "";
        rebuild();
        return;
      }
    }
    if (a.equals("pg:prev")) { this.pageNo = this.pageNo - 1; rebuild(); return; }
    if (a.equals("pg:next")) { this.pageNo = this.pageNo + 1; rebuild(); return; }
    if (a.equals("upgno")) { this.confirm = false; this.info = ""; rebuild(); return; }
    if (a.equals("upg")) { this.confirm = true; this.info = "=Check the cost, then Pay - or Cancel"; rebuild(); return; }
    @PLA@ player = player0;
    if (player == null) return;
    String k = @PKG@.SackPool.settledKey(u);
    if (k == null) { this.info = "-The Void is paused (profile loading or switching) - try again in a moment"; rebuild(); return; }
    if (this.key != null && !this.key.equals(k)) { this.info = "=Your profile changed - this page now shows it"; this.sel = null; rebuild(); return; }
    if (a.startsWith("upgok:")) {
      String[] f = a.substring(6).split(":");
      this.confirm = false;
      int uci = -1;
      int from = -1;
      try { uci = Integer.parseInt(f[0].trim()); from = Integer.parseInt(f[1].trim()); } catch (Throwable t2) { uci = -1; }
      this.info = uci < 0 ? "-Bad upgrade click" : @PKG@.VoidStore.upgrade(player, u, k, uci, from);
      if (this.info.startsWith("+")) { try { @SNDU@.playSoundEvent2d(ref, @TAI@.getSoundEventIndex("SFX_Player_Craft_Item_Inventory"), @SCAT@.UI, st); } catch (Throwable t3) { } }
      rebuild();
      return;
    }
    boolean wd = a.equals("wd");
    boolean dep = a.equals("dep");
    if (wd || dep) {
      String amt = field(data, "@Amt");
      this.amount = amt;
      String id = this.sel;
      if (id == null) { this.info = "-Pick an item in the grid first"; rebuild(); return; }
      if (wd) {
        long n = parseAmt(amt, (long) stackOf(id));
        if (n == -2L) { this.info = "-Type a number (or leave it empty for one stack)"; rebuild(); return; }
        long got = withdrawN(player, k, id, n);
        this.info = got > 0L ? ("+Took " + num(got) + " " + pretty(id)) : (@PKG@.SackPool.get(k, id) <= 0L ? "-None of it left in the Void" : "-Your storage is full");
      } else {
        long n = parseAmt(amt, -1L);
        if (n == -2L) { this.info = "-Type a number (or leave it empty for all you carry)"; rebuild(); return; }
        long got = @PKG@.VoidStore.depositInv(player, u, k, id, n);
        this.info = got > 0L ? ("+Put " + num(got) + " " + pretty(id) + " into the Void") : (got == -1L ? "-That item does not go into the Void" : (got == -2L ? "-This category is full - level it up or upgrade its rarity" : "-You carry none of it (plain stacks only)"));
      }
      @PKG@.SackPool.saveSoon(k);
      rebuild();
      return;
    }
    if (a.equals("pickall")) {
      long total = 0L;
      java.util.ArrayList ids = new java.util.ArrayList();
      java.util.Iterator it = @PKG@.SackPool.pool(k).entrySet().iterator();
      while (it.hasNext()) { java.util.Map.Entry e2 = (java.util.Map.Entry) it.next(); if (this.cat != null && this.cat.equals(@PKG@.SackDefs.homeOf((String) e2.getKey()))) ids.add(e2.getKey()); }
      for (int i = 0; i < ids.size(); i++) {
        long got = withdrawN(player, k, (String) ids.get(i), 9223372036854775807L);
        total += got;
        if (got <= 0L && @PKG@.SackPool.get(k, (String) ids.get(i)) > 0L) break;
      }
      this.info = total > 0L ? ("+Picked up " + num(total) + " items") : "-Nothing taken (your storage is full, or this category is empty)";
      @PKG@.SackPool.saveSoon(k);
      rebuild();
      return;
    }
    if (a.equals("depall")) {
      @PKG@.SackPool.clearKeptCat(k, this.cat);
      @PKG@.SackPool.forgetSeen(u);
      int moved = @PKG@.SweepTask.sweep(player, k, this.cat, true, (java.util.HashMap) null, @PKG@.VoidStore.capsK(u, k), (java.util.HashMap) null);
      this.info = moved > 0 ? ("+Deposited " + num((long) moved) + " items") : "-Nothing to deposit (or this category is full)";
      if ("Farming".equals(this.cat) && !@PKG@.SackDefs.COOKED_FARM && @PKG@.SweepTask.cookedHeld(player.getInventory()) > 0) this.info = this.info + " - cooked food stays in your inventory";
      @PKG@.SackPool.saveSoon(k);
      rebuild();
      return;
    }
  } catch (Throwable t) { @PKG@.SackPool.warn("Void page event failed: " + t); }
}QQQ), page))
# the engine's entry: the Player component of this page's player (world thread), then onEvent (the harness calls onEvent directly)
page.addMethod(CtNewMethod.make(jt(rQQQ
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  onEvent(ref, st, p, data);
}QQQ), page))
# 0.7.2: the active profile changed while this page is open (ProcTask, world thread): set() only on the result line the last build made
page.addMethod(CtNewMethod.make(f"""
public void profileNotice(String k) {{
  if (this.key == null || k == null || k.equals(this.noticeKey)) return;
  this.noticeKey = k;
  {UCB} c = new {UCB}();
  c.set("#SkyySInfo.Text", "Your profile changed - click a tab to refresh this page");
  sendUpdate(c, false);
}}""", page))

# ================= SacksCmd =================
'''), keep_end=False)

# ================================================================================================= /pd: the Void + the Pocket item
cut(T(r'''cmd.addConstructor(CtNewConstructor.make("""
public SacksCmd() {'''), T(r'''# ================= SacksPageFactory'''), T(r'''cmd.addConstructor(CtNewConstructor.make("""
public SacksCmd() {
  super("sacks", "Open the Void - your SkyyVoid Pocket Dimension (also /pd, /bags)");
  addAliases(new String[] { "pd", "bags" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) {{ pr.sendMessage({MSG}.raw("[SkyyVoid] player not found")); return; }}
    // 0.8.0: the Pocket Dimension item is only the opener - /pd gives one when you have none (dropping it never loses anything)
    try {{
      if (!{PKG}.VoidStore.HOLDALL && {PKG}.VoidStore.countIn(player.getInventory(), {PKG}.SackDefs.POCKET, false) <= 0) {{   // fix round 2: not under legacybags all
        if ({PKG}.VoidStore.givePocket(player.getInventory())) pr.sendMessage({MSG}.raw("[SkyyVoid] Here is your Pocket Dimension - right-click it to open the Void").color("#cc66cc"));
      }}
    }} catch (Throwable tp) {{ }}
    // EXPERIMENT 0.3.0: open with an (empty) container window so the client shows the player inventory below the page (chest style)
    com.hypixel.hytale.server.core.entity.entities.player.windows.Window[] wins = new com.hypixel.hytale.server.core.entity.entities.player.windows.Window[] {{ new com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow(new com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer((short) 9)) }};
    boolean ok = player.getPageManager().openCustomPageWithWindows(ref, store, new {PKG}.SacksPage(pr, (String) null), wins);
    if (!ok) pr.sendMessage({MSG}.raw("[SkyyVoid] openCustomPageWithWindows returned false"));
  }} catch (Throwable t) {{
    {PKG}.SackPool.warn("/pd failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyyVoid] could not open the Void"));
  }}
}}""", cmd))

'''))

# ================================================================================================= player-facing words: "the Void"
rep(T(r'''Materials: your inventory, then your magic bags.";'''), T(r'''Materials: your inventory, then the Void.";'''))
rep(T(r'''No fuel on you or in your bags - logs'''), T(r'''No fuel on you or in the Void - logs'''))
rep(T(r'''Materials are counted from your inventory and your magic bags.'''), T(r'''Materials are counted from your inventory and the Void.'''))
rep(T(r'''inventory crafting (materials from your inventory and your magic bags) - /craft'''), T(r'''inventory crafting (materials from your inventory and the Void) - /craft'''))
# fix round (LOCKED "player-facing name SkyyVoid everywhere"): the last chat lines with the old name + the bench-chest row / file comment
rep(T(r'''pr.sendMessage({MSG}.raw("[SkyySacks] could not open crafting"));'''), T(r'''pr.sendMessage({MSG}.raw("[SkyyVoid] could not open crafting"));'''))
rep(T(r'''pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " is done. '''), T(r'''pr.sendMessage({MSG}.raw("[SkyyVoid] Your " + pb.bench + " is done. '''))
rep(T(r'''pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " ran out of fuel'''), T(r'''pr.sendMessage({MSG}.raw("[SkyyVoid] Your " + pb.bench + " ran out of fuel'''))
rep(T(r'''"On: a bench with your bags linked reports 1 nearby chest. Only if benches ignore bag items.",'''),
    T(r'''"On: an open bench reports 1 nearby chest so it uses the Void. Only if benches ignore Void items.",'''))
rep(T(r'''    "# Bench chest count fallback (true or false): true makes an open bench report at least 1 nearby chest while your bags are linked.",
    "# Turn it on only if benches ignore bag items (the game client may want a chest count first).",'''),
    T(r'''    "# Bench chest count fallback (true or false): true makes an open bench report at least 1 nearby chest while it uses the Void.",
    "# Turn it on only if benches ignore Void items (the game client may want a chest count first).",'''))

# fix round 2 (LOCKED "SkyyVoid everywhere players see it (pages, menu, Server Setup, chat...)"): the Server Setup rows, the config file
# comments and the /craft page / bench queue lines that still said "bags" (keys, bridge names and the Accessory bag text are unchanged)
rep(T(r'''("bags.cookedFood", "Cooked food in the Farming bag", "bags",'''), T(r'''("bags.cookedFood", "Cooked food in Farming", "bags",'''))
rep(T(r'''"On: cooked and prepared food goes into the Farming bag too. Off: raw produce only, cooked stays out.",'''),
    T(r'''"On: cooked and prepared food goes into Farming too. Off: raw produce only, cooked stays out.",'''))
rep(T(r'''("bags.refill", "Stack refill from bags", "bags",'''), T(r'''("bags.refill", "Stack refill from the Void", "bags",'''))
rep(T(r'''"On: each player picks Hotbar only, Full inventory or Off on the bag page. Off: no refill for anyone.",'''),
    T(r'''"On: each player picks Hotbar only, Full inventory or Off on the Void page. Off: no refill at all.",'''))
rep(T(r'''"live", "Players who never picked a mode on the bag page get this one (Hotbar only is the default).",'''),
    T(r'''"live", "Players who never picked a mode on the Void page get this one (Hotbar only is the default).",'''))
rep(T(r'''("bags.pocketCraft", "Bags in inventory crafting", "bags", "bool", "true", "", "", "", "", "live", "On: inventory crafting also uses the bags you carry. Off: inventory only (benches still use bags).",'''),
    T(r'''("bags.pocketCraft", "Void in inventory crafting", "bags", "bool", "true", "", "", "", "", "live", "On: inventory crafting also uses the Void. Off: inventory only (benches still use the Void).",'''))
rep(T(r'''    "# Cooked food in the Farming bag (true or false): false keeps cooked and prepared food (bread, pies, kebabs, salads, graded dishes)",
    "# out of the Farming bag - it stays in your inventory; raw produce still goes in. Cooked food already in a bag stays until taken out.",'''),
    T(r'''    "# Cooked food in Farming (true or false): false keeps cooked and prepared food (bread, pies, kebabs, salads, graded dishes)",
    "# out of the Void's Farming category - it stays in your inventory; raw produce still goes in. Cooked food already stored stays until taken out.",'''))
rep(T(r'''Full inventory or Off on the bag page; false turns it off.",'''), T(r'''Full inventory or Off on the Void page; false turns it off.",'''))
rep(T(r'''    "# Bags in inventory crafting (true or false): true lets inventory (pocket) crafting use the bags you carry, like benches do.",
    "# Set it to false if inventory crafting misbehaves on clients - benches keep using the bags either way.",'''),
    T(r'''    "# Void in inventory crafting (true or false): true lets inventory (pocket) crafting use the Void, like benches do.",
    "# Set it to false if inventory crafting misbehaves on clients - benches keep using the Void either way.",'''))
rep(T(r'''Text: \\"< Back to bags\\";'''), T(r'''Text: \\"< Back to the Void\\";'''))
rep(T(r'''("ON (each player picks Hotbar only / Full inventory / Off on the bag page; players'''), T(r'''("ON (each player picks Hotbar only / Full inventory / Off on the Void page; players'''))
rep(T(r'''"ON - players who never picked a mode on the bag page get "'''), T(r'''"ON - players who never picked a mode on the Void page get "'''))
rep(T(r'''this.info = "bags paused (profile loading or switching) - bag counts come back in a moment";'''),
    T(r'''this.info = "the Void paused (profile loading or switching) - its counts come back in a moment";'''))
rep(T(r'''this.info.startsWith("bags paused")'''), T(r'''this.info.startsWith("the Void paused")'''))
rep(T(r'''this.info = "bags paused (profile loading or switching) - try again in a moment";'''),
    T(r'''this.info = "the Void paused (profile loading or switching) - try again in a moment";'''), count=1)
rep(T(r'''(consumed > 0 ? " - " + consumed + " from bags" : "")'''), T(r'''(consumed > 0 ? " - " + consumed + " from the Void" : "")'''))
rep(T(r'''(consumed > 0 ? " (" + consumed + " from bags)" : "")'''), T(r'''(consumed > 0 ? " (" + consumed + " from the Void)" : "")'''))

# ================================================================================================= sacks:freebags retired
rep(T(r'''public static void pubFree() {
  try {
    Boolean v = Boolean.valueOf(effFree());
    java.util.Map b = @PKG@.SackPool.bridgeW();
    if (!v.equals(b.get("sacks:freebags"))) b.put("sacks:freebags", v);
  } catch (Throwable t) { }
}'''), T(r'''public static void pubFree() {
  // 0.8.0 (Bags v2 spec 5): sacks:freebags is no longer written - there are no bag recipes (an old value stays as it is; nobody reads it)
}'''))

# ================================================================================================= the bridges: category room, sacks:fn:pd / catOf
rep(T(r'''  Integer cc = (Integer) @PKG@.SweepTask.caps(inv).get(cat);
  if (cc == null) return 0L;'''), T(r'''  Integer cc = (Integer) @PKG@.VoidStore.capsK(u, k).get(cat);   // 0.8.0: the category capacity (one limit per category)
  int dci = @PKG@.SackDefs.catIndex(cat);
  if (cc == null || dci < 0) return 0L;'''))
rep(T(r'''  long room = (long) cc.intValue() - @PKG@.SackPool.get(k, id);
  if (room <= 0L) return 0L;
  long want = n < room ? n : room;'''), T(r'''  long room = (long) cc.intValue() - @PKG@.VoidStore.usedAll(k)[dci];   // 0.8.0: the room of the category
  if (room <= 0L) return 0L;
  long want = n < room ? n : room;'''))
rep(T(r'''  @PKG@.SackPool.add(k, id, (long) removed);
  try { @PKG@.CraftLog.later(k, "BAG-DEPOSIT " + id + " " + removed + " (sacks:fn:deposit hotbar slot " + slot + ")"); } catch (Throwable t3) { }'''),
    T(r'''  @PKG@.SackPool.add(k, id, (long) removed);
  @PKG@.VoidStore.noteIntake(k, dci, (long) removed);
  try { @PKG@.CraftLog.later(k, "BAG-DEPOSIT " + id + " " + removed + " (sacks:fn:deposit hotbar slot " + slot + ")"); } catch (Throwable t3) { }'''))
rep(T(r'''    if (this.mode >= 5) return @PKG@.SackBridge.call2(this.mode, o);   // 0.7.17: deposit, pocketFill, the craft bridges'''),
    T(r'''    if (this.mode == 12) return @PKG@.VoidStore.pdInfo(o);   // 0.8.0 sacks:fn:pd
    if (this.mode == 13) return (o instanceof String) ? @PKG@.SackDefs.catOf((String) o) : null;   // 0.8.0 sacks:fn:catOf (the 1.1 rule)
    if (this.mode >= 5) return @PKG@.SackBridge.call2(this.mode, o);   // 0.7.17: deposit, pocketFill, the craft bridges'''))
rep(T(r'''  return this.mode == 3 ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);
}"""), sfn))'''), T(r'''  return (this.mode == 3 || this.mode == 12 || this.mode == 13) ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);
}"""), sfn))'''))

# ================================================================================================= plugin: dirs, keys, /pdadmin, shutdown
rep(T(r'''  {PKG}.RefillPref.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("refill.properties");
  {PKG}.RefillPref.load();
'''), T(r'''  {PKG}.RefillPref.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("refill.properties");
  {PKG}.RefillPref.load();
  // 0.8.0 (Bags v2): the Void per profile key (pd/<key>.properties + .journal), the History copies, the migration log
  {PKG}.VoidStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("pd");
  {PKG}.VoidStore.HDIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("history");
  {PKG}.VoidStore.MIGLOG = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("migration.log");
  {PKG}.VoidStore.loadHold();   // fix round: /pdadmin legacybags all survives a restart (pd/_legacybags-all.flag)
'''))
rep(T(r'''  getCommandRegistry().registerCommand(new {PKG}.CraftCmd());
'''), T(r'''  getCommandRegistry().registerCommand(new {PKG}.CraftCmd());
  getCommandRegistry().registerCommand(new {PKG}.PdAdminCmd());   // 0.8.0: /pdadmin legacybags | omni <player> (skyysacks.admin)
'''))
rep(T(r'''  sbr0.put("sacks:fn:craftCommit", new {PKG}.SackFn(11));
'''), T(r'''  sbr0.put("sacks:fn:craftCommit", new {PKG}.SackFn(11));
  // 0.8.0 (Bags v2 spec 5): sacks:v2 (SkyyCollections hides the bag rewards), the Void per category, the category rule
  sbr0.put("sacks:fn:pd", new {PKG}.SackFn(12));
  sbr0.put("sacks:fn:catOf", new {PKG}.SackFn(13));
  sbr0.put("sacks:v2", Boolean.TRUE);
'''))
rep(T(r'''  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}'''), T(r'''  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.VoidStore.flushDirty(); }} catch (Throwable t) {{ }}   // 0.8.0: levels / rarity (unsettled conversions stay in the journal)
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}'''))
# the ready line keeps "[SkyySacks] <version> ready" (the smoke test); the rest says what 0.8.0 is
_i0 = s.index('getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - ')
_i1 = s.index('");', _i0)
s = s[:_i0] + ('getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - SkyyVoid: /pd (/sacks, /bags) opens the Void = ONE '
               'Pocket Dimension, six categories (Mining, Foraging, Farming, Fishing, Combat, Smithing), each with a storage level from the items '
               'collected (SkyyCollections coll:fn:catTotal) and a rarity (Upgrade button: level gate + item cost; Omni with all six Legendary), '
               'one item limit per category = level x pd.perLevel x the rarity multiplier; old Magic Bags convert once per profile (History copy '
               'first, journal pd/<key>.journal, credit after 30 s); no bag needs to be carried; /craft, benches and inventory crafting use the Void; '
               'the Bazaar sells from it (sacks:fn:take), Requip refills from it; sacks:v2 + sacks:fn:pd + sacks:fn:catOf; /pdadmin legacybags | omni; '
               'storage per profile (pkey); settings: SkyWynn Menu -> Server Setup -> SkyyVoid and Crafting (skyysacks.admin); UI kit {KIT_ID}') + s[_i1:]

# ================================================================================================= Server Setup rows
rep(T(r'''SACK_CFG_CATS = [("craft", "Craft page"), ("bags", "Bags"), ("benches", "Furnace and Tannery")]'''),
    T(r'''SACK_CFG_CATS = [("craft", "Craft page"), ("bags", "The Void"), ("void", "Void levels"), ("voidcost", "Upgrade costs"),
                 ("benches", "Furnace and Tannery")]   # 0.8.0: + the Void rows (the bag caps and free recipes rows are retired)'''))
cut(T(r'''    # 0.7.7 (spec 8.1): the admin override - on = every player knows every bag recipe (the old free recipes), off = collection unlocks.'''),
    T(r'''    # 0.7.8 (Skyy 2026-09-30, "id keep cooked food out")'''), T(r'''    # 0.8.0: bags.freeRecipes is retired (no bag recipes) - its line stays in the file, unread
'''))
rep(T(r'''] + [(k, _CAP_ROW[k][0], _CAP_ROW[k][1], "int", str(d), str(lo), str(hi), "", "", _CAP_ROW[k][2], _CAP_ROW[k][3],
      "field:%s@config.properties:%s%s" % (f, k, ";check=SackCfg.checkTierOrder" if k.startswith("bag.") else ""))
     for (k, f, d, lo, hi) in SACK_CAPS]'''), T(r'''] + [(k, _CAP_ROW[k][0], _CAP_ROW[k][1], "int", str(d), str(lo), str(hi), "", "", _CAP_ROW[k][2], _CAP_ROW[k][3],
      "field:%s@config.properties:%s" % (f, k))
     for (k, f, d, lo, hi) in SACK_CAPS if k.startswith("bench.")]   # 0.8.0: the five bag.* cap rows are retired (lines kept, unread)
# 0.8.0 (Bags v2 spec 2.4): the Void rows, all live (the next sweep / page uses them); lowering any of them never deletes anything
def _pdrow(key, label, cat, typ, dflt, lo, hi, unit, flags, help_, field, extra=""):
    assert len(label) <= 40 and len(help_) <= 100, (key, len(label), len(help_))
    return (key, label, cat, typ, dflt, lo, hi, "", unit, flags, help_, "field:SackCfg.%s@config.properties:%s;after=SackCfg.pdChanged%s" % (field, key, extra))
SACK_CFG_ROWS += [
    _pdrow("pd.perLevel", "Space per storage level", "void", "int", str(PD_PER_LEVEL), "1", "100000", "", "live",
           "Items each storage level adds to a category (x its rarity). Lowering never deletes items.", "PD_PER_LEVEL"),
    _pdrow("pd.maxLevel", "Highest storage level", "void", "int", str(PD_MAX_LEVEL), "1", "10000", "", "live,adv",
           "The storage level a category stops at. Lowering never deletes items.", "PD_MAX_LEVEL"),
    _pdrow("pd.omniAuto", "Omni comes by itself", "void", "bool", "true", "", "", "", "live",
           "On: all six categories at Legendary = Omni. Off: only /pdadmin omni gives it.", "PD_OMNI_AUTO"),
] + [_pdrow("pd.step." + c, "%s items per level step" % c, "void", "int", str(PD_STEP[c]), "1", "1000000", "", "live,adv",
            "Level = 1 + square root of (%s items collected / this). Higher = slower levels." % c, "PD_STEP_" + c.upper())
     for c in PD_CATS
] + [_pdrow("pd.mult." + r, "%s space multiplier" % r, "void", "dec", "%g" % m, "0.1", "100", "x", "live,adv,danger",
            "Space x this at %s. Must not go down the ladder (asks first)." % r, "PD_MULT_" + r.upper(), ";check=SackCfg.checkMult;confirm=always")
     for r, m in zip(PD_RAR, PD_MULT)
] + [_pdrow("pd.gate." + PD_RAR[i + 1], "Level needed for %s" % PD_RAR[i + 1], "void", "int", str(g), "1", "10000", "", "live,adv",
            "A category needs this storage level before its %s upgrade (coins never skip it)." % PD_RAR[i + 1], "PD_GATE_" + PD_RAR[i + 1].upper(),
            ";check=SackCfg.checkGate")
     for i, g in enumerate(PD_GATE)
] + [_pdrow("pd.cost.%s.%s" % (c, PD_RAR[r]), "%s to %s cost" % (c, PD_RAR[r]), "voidcost", "text", pd_cost_text(c, r), "", "400", "",
            "live,adv", "Items this upgrade takes - itemId:amount pairs, commas between. Unknown ids are refused.",
            "PD_COST_%s_%s" % (c.upper(), PD_RAR[r].upper()), ";check=SackCfg.checkCost")
     for c in PD_CATS for r in (1, 2, 3)]'''))
rep(T(r'''kit = CFG.emit(pool, PKG, MOD="SkyySacks", TITLE="Bags and Crafting", VERSION=VERSION, NODE="skyysacks.admin", CATS=SACK_CFG_CATS,'''),
    T(r'''kit = CFG.emit(pool, PKG, MOD="SkyySacks", TITLE="SkyyVoid and Crafting", VERSION=VERSION, NODE="skyysacks.admin", CATS=SACK_CFG_CATS,'''))
# config.properties template (written only when the file is missing): the retired bag lines go, the Void lines come
rep(T(r'''    "# Admins can also change these in game: SkyWynn Menu -> Server Setup -> Bags and Crafting (permission skyysacks.admin).",
    "# Free bag recipes (true or false): true gives every player every bag recipe (the old way); false unlocks them through collections.",
    "# Without SkyyCollections every bag recipe is free anyway.",
    "#bags.freeRecipes=false",'''), T(r'''    "# Admins can also change these in game: SkyWynn Menu -> Server Setup -> SkyyVoid and Crafting (permission skyysacks.admin).",'''))
rep(T(r'''    "# Advanced - remove the # in front of a line to change it. Bag caps: the most of EACH item a Normal (old Small) / Unique (old Medium) /",
    "# Rare / Legendary (old Large) bag holds; bag.omni is the Mythic Omni Bag, for every bag type. The bags a player carries add up.",
    "# Lowering one never deletes pooled items, it only stops new ones going in. The bag tooltips keep the built-in numbers.",
] + ["#%s=%d" % (k, d) for (k, _f, d, _lo, _hi) in _BAG_KEYS] + ['''), T(r'''    "# The Void (SkyyVoid): space of a category = storage level x pd.perLevel x the rarity multiplier; level = 1 + square root of",
    "# (items collected in that category / pd.step.<Category>). Remove the # in front of a line to change it. Lowering never deletes items.",
] + (["#pd.perLevel=%d" % PD_PER_LEVEL, "#pd.maxLevel=%d" % PD_MAX_LEVEL, "#pd.omniAuto=true"]
  + ["#pd.step.%s=%d" % (c, PD_STEP[c]) for c in PD_CATS] + ["#pd.mult.%s=%g" % (r, m) for r, m in zip(PD_RAR, PD_MULT)]
  + ["#pd.gate.%s=%d" % (PD_RAR[i + 1], g) for i, g in enumerate(PD_GATE)]
  + ["#pd.cost.%s.%s=%s" % (c, PD_RAR[r], pd_cost_text(c, r)) for c in PD_CATS for r in (1, 2, 3)]) + ['''))

# ================================================================================================= class list
rep(T(r'''          pcw, psu, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, sbr, sfn, pl, sthr, psj, sinv):   # 0.7.18: + SackThreads, PoolSaveJob, SackInvSys'''),
    T(r'''          pcw, psu, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, sbr, sfn, pl, sthr, psj, sinv,   # 0.7.18: + SackThreads, PoolSaveJob, SackInvSys
          vss, vst, vjob, vat, vac):   # 0.8.0: + VoidState, VoidStore, VoidJob, VoidAdminTask, PdAdminCmd'''))

# ================================================================================================= assets: the old bags (no recipes) + the Pocket
cut(T(r'''def sack_item(item_id, quality, recipe_in, knowledge, page_id):'''), T(r'''files = {}  # pages are built inline'''), T(r'''def sack_item(item_id, quality, page_id, look_of=None):
    # 0.8.0 (Bags v2): no bag has a recipe any more. The 21 old ids stay defined (no unknown items anywhere), right-click still opens the
    # Void; the Pocket Dimension (Skyy_Sack_Pocket) wears the Omni bag's look (look_of).
    node = {
      "TranslationProperties": {"Name": "server.items.%s.name" % item_id, "Description": "server.items.%s.description" % item_id},
      "Categories": ["Items.Tools"],
      "Icon": "Icons/ItemsGenerated/Utility_Bag_Seed.png",
      "Quality": quality,
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
      "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    }
    if look_of is None:
        return bag_look(item_id, node)   # 0.7.14: the bag look (Model / Texture / Icon / IconProperties / Animation / set / particles / SwapTo)
    node.update(BAG_LOOK[look_of])
    if BAG_PARTS["lift"]:
        node["Interactions"]["SwapTo"] = BAG_SWAPTO
    return node
'''))
cut(T(r'''for cat in BAG_CATS:
    prev = None
    for (suf, rar, qid, capk, bolt) in BAG_TIERS:'''), T(r'''# 0.7.7 own qualities (spec 3.2)'''), T(r'''_OLD_DESC = ("Old Magic Bag - it turns into Void rarity (or is refunded) when you pick it up. Everything that was in it is in the Void: "
             "type /pd.")
for cat in BAG_CATS:
    for (suf, rar, qid, capk, bolt) in BAG_TIERS:
        iid = "Skyy_Sack_%s_%s" % (cat, suf)
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(sack_item(iid, qid, "SkyySacks" + cat), indent=2)
        name = "Old %s %s Bag" % (rar, cat)
        lang.append("items.%s.name=%s" % (iid, name))
        lang.append("server.items.%s.name=%s" % (iid, name))
        lang.append("items.%s.description=%s" % (iid, _OLD_DESC))
        lang.append("server.items.%s.description=%s" % (iid, _OLD_DESC))
files["Server/Item/Items/Utility/%s.json" % BAG_OMNI] = json.dumps(sack_item(BAG_OMNI, BAG_RARITY[-1][0], "SkyySacks"), indent=2)
lang.append("items.%s.name=Old Mythic Omni Bag" % BAG_OMNI)
lang.append("server.items.%s.name=Old Mythic Omni Bag" % BAG_OMNI)
lang.append("items.%s.description=%s" % (BAG_OMNI, _OLD_DESC))
lang.append("server.items.%s.description=%s" % (BAG_OMNI, _OLD_DESC))
# 0.8.0: THE POCKET DIMENSION - the one bag item, only the opener (spec 1.2); its own quality "Void" (the Mythic texture set + colour)
files["Server/Item/Items/Utility/%s.json" % POCKET] = json.dumps(sack_item(POCKET, POCKET_Q, "SkyySacks", look_of=BAG_OMNI), indent=2)
_PDESC = ("SkyyVoid - right-click (or type /pd) to open the Void: one storage for everything you gather, six categories that level up as "
          "you collect. This is only the opener - losing it loses nothing, /pd gives a new one.")
lang.append("items.%s.name=Pocket Dimension" % POCKET)
lang.append("server.items.%s.name=Pocket Dimension" % POCKET)
lang.append("items.%s.description=%s" % (POCKET, _PDESC))
lang.append("server.items.%s.description=%s" % (POCKET, _PDESC))
_QV = [r for r in BAG_RARITY if r[1] == "Mythic"][0]
files["Server/Item/Qualities/%s.json" % POCKET_Q] = json.dumps({
    "QualityValue": 5,
    "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % _QV[5],
    "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltip%sArrow.png" % _QV[5],
    "SlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _QV[5],
    "BlockSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _QV[5],
    "SpecialSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _QV[5],
    "TextColor": _QV[2],
    "LocalizationKey": "server.general.qualities." + POCKET_Q,
    "VisibleQualityLabel": True,
    "RenderSpecialSlot": True,
    "ItemEntityConfig": {"ParticleSystemId": _QV[6]}}, indent=2)
lang.append("general.qualities.%s=Void" % POCKET_Q)
lang.append("server.general.qualities.%s=Void" % POCKET_Q)
'''))
cut(T(r'''def _bag_assets_check():'''), T(r'''_bag_assets_check()
'''), T(r'''def _bag_assets_check():
    """0.8.0: 22 bag JSONs (the 21 old ids + the Pocket), NONE with a recipe, 6 qualities (+ Void); lang names / descriptions / labels;
    every Model / Texture / Icon in Assets.zip or the jar; the quality textures and drop particles in Assets.zip; QualityValue < 8"""
    import zipfile
    items = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    if sorted(items) != sorted(MANAGED_IDS + [BAG_OMNI, POCKET]) or len(quals) != len(BAG_RARITY) + 1:
        raise SystemExit("0.8.0 asset check: %d bag items, %d qualities" % (len(items), len(quals)))
    if any("Recipe" in n for n in items.values()):
        raise SystemExit("0.8.0 asset check: a bag item still has a recipe (Bags v2: no bag recipes)")
    for iid, node in items.items():
        if node["Quality"] not in quals:
            raise SystemExit("0.8.0 asset check: %s uses quality %s that is not shipped" % (iid, node["Quality"]))
    if any(q["QualityValue"] >= 8 for q in quals.values()):
        raise SystemExit("0.8.0 asset check: a bag quality reaches SkyyAuctions' technical threshold (8)")
    lt = files["Server/Languages/en-US/server.lang"]
    for iid in items:
        for k in ("server.items.%s.name=" % iid, "server.items.%s.description=" % iid, "\nitems.%s.name=" % iid):
            if k not in "\n" + lt:
                raise SystemExit("0.8.0 asset check: no lang line " + k.strip())
    for qid in quals:
        if ("server.general.qualities.%s=" % qid) not in lt or ("\ngeneral.qualities.%s=" % qid) not in "\n" + lt:
            raise SystemExit("0.8.0 asset check: no quality label for " + qid)
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if not os.path.isfile(za):
        print("note: Assets.zip not found - bag textures, quality textures and drop particles not cross-checked")
        return
    with zipfile.ZipFile(za) as z:
        names = set(z.namelist())
    parts = set(os.path.basename(n)[:-len(".particlesystem")] for n in names if n.endswith(".particlesystem"))
    def exists(p):
        q = "Common/" + p
        return q in names or q in files or (q.endswith(".png") and q[:-4] + "@2x.png" in names)
    for iid, node in items.items():
        for k in ("Model", "Texture", "Icon"):
            if not exists(node[k]):
                raise SystemExit("0.8.0 asset check: %s %s %s is not in Assets.zip or the jar" % (iid, k, node[k]))
    for qid, q in quals.items():
        for k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture", "BlockSlotTexture", "SpecialSlotTexture"):
            if not exists(q[k]):
                raise SystemExit("0.8.0 asset check: quality %s %s %s is not in Assets.zip" % (qid, k, q[k]))
        if q["ItemEntityConfig"]["ParticleSystemId"] not in parts:
            raise SystemExit("0.8.0 asset check: quality %s drop particle %s is not in Assets.zip" % (qid, q["ItemEntityConfig"]["ParticleSystemId"]))
    print("assets checked: %d bag items (21 old ids without recipes + the Pocket Dimension), %d qualities, %d lang lines" % (len(items), len(quals), len(lang)))
_bag_assets_check()
'''), keep_end=False)
rep(T(r'''    items = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    for iid, n in items.items():
        lk = BAG_LOOK[iid]'''), T(r'''    items = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    for iid, n in items.items():
        lk = BAG_LOOK[BAG_OMNI if iid == POCKET else iid]   # 0.8.0: the Pocket wears the Omni bag's look'''))
rep(T(r'''        assert n["Recipe"]["Input"] and n["Quality"] and n["MaxStack"] == 1, iid
    assert len(set(n["Texture"] for n in items.values())) == 21 and len(set(n["Icon"] for n in items.values())) == 21, "21 looks"'''),
    T(r'''        assert "Recipe" not in n and n["Quality"] and n["MaxStack"] == 1, iid   # 0.8.0: no recipes
    assert len(items) == 22 and len(set(n["Texture"] for n in items.values())) == 21 and len(set(n["Icon"] for n in items.values())) == 21, "21 looks (the Pocket = the Omni's)"'''))
cut(T(r'''def _wbtab_checks():'''), T(r'''_wbtab_checks()
'''), T(r'''def _wbtab_checks():
    """0.8.0: no bag recipe anywhere (Bags v2) - the Workbench tab "Accessories & Bags" (tools/skyywbtab.py) stays emitted as this mod's
    fallback copy (SkyyAccessories owns it and its accessory recipes); its two lang lines ship as before"""
    got = [p for p, t in files.items() if p.startswith("Server/Item/Items/") and '"Recipe"' in t]
    assert not got, "0.8.0: bag item(s) with a recipe: %s" % got
    for l in WB.LANG_LINES:
        assert l in lang, l
    print("Workbench tab: no bag recipes any more (Bags v2); the tab definition '%s' is kept as SkyyAccessories' fallback" % WB.TAB_TEXT)
_wbtab_checks()
'''), keep_end=False)
rep(T(r'''print("bag table: %s x %s + %s | caps %s | qualities %s" % ('''), T(r'''print("Void: %s | level = 1 + sqrt(collected / step %s) to %d | space = level x %d x %s | gates %s | Pocket %s" % (
    "/".join(PD_CATS), "/".join(str(PD_STEP[c]) for c in PD_CATS), PD_MAX_LEVEL, PD_PER_LEVEL, "/".join("%s %g" % (r, m) for r, m in zip(PD_RAR, PD_MULT)),
    "/".join(str(g) for g in PD_GATE), POCKET))
print("old bag table: %s x %s + %s | caps %s | qualities %s" % ('''))
rep(T(r'''B.assemble(jar, B.manifest("SkyySacks", VERSION, "SkyBlock-style Magic Bags by rarity (Normal, Unique, Rare, Legendary + the Mythic Omni Bag): matching pickups pool automatically, /pd to view and withdraw, /craft from your bags, bag recipes unlock through collections. Zero dependencies.", PKG + ".SkyySacksPlugin"), OUT, files)'''),
    T(r'''B.assemble(jar, B.manifest("SkyySacks", VERSION, "SkyyVoid: one Pocket Dimension for everything you gather - six categories that level up as you collect, rarity upgrades, /pd to open it, /craft and benches use it. Old Magic Bags convert once. Zero dependencies.", PKG + ".SkyySacksPlugin"), OUT, files)'''))

# ================================================================================================= no "no bag carried" any more
# 0.8.0: SweepTask.caps(inv), VoidStore.capsK and capsBest always answer all six categories (SackDefs.CATS), so the 0.7.x "no bag carried"
# isEmpty() guards are constant false - dropped (capsSig keeps its own: decline gets an empty map for a missing player)
rep(T(r'''  java.util.HashMap caps = capsIn != null ? capsIn : {PKG}.VoidStore.capsBest(k);
  if (caps.isEmpty()) return 0;
'''), T(r'''  java.util.HashMap caps = capsIn != null ? capsIn : {PKG}.VoidStore.capsBest(k);
'''))
rep(T(r'''  if (inv == null || caps == null || caps.isEmpty()) return out;
  @IC@ stor = inv.getStorage();'''), T(r'''  if (inv == null || caps == null) return out;
  @IC@ stor = inv.getStorage();'''))
rep(T(r'''  if (k == null || caps.isEmpty()) {
    decline(u, rec, k, caps, k == null ? "profile not settled" : "no bag carried");'''), T(r'''  if (k == null) {
    decline(u, rec, k, caps, "profile not settled");'''))
rep(T(r'''  java.util.HashMap caps = @PKG@.SweepTask.caps(p.getInventory());
  if (caps.isEmpty()) return false;
'''), T(r'''  java.util.HashMap caps = @PKG@.SweepTask.caps(p.getInventory());
'''))
rep(T(r'''  if (p == null || rec == null || k == null || caps.isEmpty() || !on) {'''), T(r'''  if (p == null || rec == null || k == null || !on) {'''))
rep(T(r'''  java.util.HashMap caps = capsIn != null ? capsIn : caps(inv);   // 0.7.18: the sweep's caps
  if (caps.isEmpty()) return 0;
'''), T(r'''  java.util.HashMap caps = capsIn != null ? capsIn : caps(inv);   // 0.7.18: the sweep's caps
'''), count=2)
rep(T(r'''  java.util.HashMap caps = @PKG@.SweepTask.caps(p.getInventory());
  if (caps.isEmpty()) return out;
'''), T(r'''  java.util.HashMap caps = @PKG@.SweepTask.caps(p.getInventory());
'''))

# ================================================================================================= write + sanity
assert s.count("registerCommand(") == REG0 + 1, "one new command (/pdadmin)"
assert s.count("registerSystem(") == SYS0, "no new ECS system"
assert s.count("pool.makeClass(") == MAKE0 + 5, "five new classes"
assert "VoidStore" in s and 'VERSION = "0.8.0"' in s
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote %s (%d lines)" % (dst, s.count(LF) + 1))
