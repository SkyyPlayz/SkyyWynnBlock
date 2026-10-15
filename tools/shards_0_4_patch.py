"""Derive SkyyShards/build_skyyshards_0.4.py from build_skyyshards_0.3.2.py (the SET pin; 0.3.2 is left untouched; line endings kept).
Run:  python tools/shards_0_4_patch.py   then   python SkyyShards/build_skyyshards_0.4.py   (never --deploy)
Harness: python SkyyShards/test_skyyshards_0.4.py [--dir <scratch>] [--keep]

0.4 = Gathering-Shards-Spec PHASE 9 (round "shards04": research/Gathering-Shards-Spec.md 9.3, 9.3.1, 9.5, 9.7, 9.8, the phase 9 row and
section 14 questions 15-26 on their [defaults]). Skyy 2026-10-15, word for word (docs/answered/skills.md):
  SHARD MENUS  "i would rather each shard has its own menu. and i was picturing you open them by right clicking the shard on your island,
               not in the menu. (make it so the shard menu can only be opened on your island. and its hidden everywhere else"
  TOTEM BENCH  "since each shard has slightly different totems, should we have a totem bench per shard? with that shards totems? (then id
               do 1 accessory to craft all of them later, but its hard to make.) the totem bench comes on the island, and cant be moved.
               we can have a few upgrade tiers to unlock the better totems that way."
  TOTEM FORMS  "and only some totems start as a hand held totem. things like the collectors start as a totem pole. the one that calls
               rain starts as a hand held totem you can use anywhere. then upgrades to a totem pole you have to place."
WHAT 0.4 CHANGES (every change in the generated script is marked "0.4"):
  1. ONE MENU PER SHARD, OPENED ONLY FROM ITS PORTAL ON YOUR ISLAND (9.5): right-clicking a placed <Kind> Shard opens THAT shard's menu
     (4 tabs: Collect, Upgrades, Islands, Totems; Enter Shard; Pick up Shard). Owner = every button; co-op members (and admins) = the same
     page without Pick up / totem place / pick up, Collect / buy / Grow only with shard.coopCollect; anyone else gets the chat line "This is
     <owner>'s <Kind> Shard." and no page. The SHARDS overview tab, the CRAFT tab (moved to the bench), the SkyWynn Menu route (bridge
     shard:fn:open is no longer published) and the "menu view" are gone. The stand inside the shard hub = an exit page (Back to Island
     only). Right-clicking a placed totem = that totem's OWN page (info, modifiers, booster, range, Pick up; Tier up points to the bench).
     The page's title bar now shows the shard / bench / totem name (0.1-0.3.2 never emitted the shell's title b.set - a blank title).
     After an island reset the owner gets a "Get back lost shard" button in any other shard's menu (the old portal is out of reach).
  2. A TOTEM BENCH PER SHARD (9.7): every hub island gets ONE fixed bench block Skyy_TotemBench_<Kind> (the vanilla Abilities bench model,
     its texture recoloured per shard at BUILD time - never committed; Unbreakable; no recipe, hidden from the creative library); the hub
     repair (every Enter / Grow) pastes it, so existing shard worlds get theirs on the next Enter. Right-click = the bench page (tabs Craft
     / Tier up / Bench): crafts ONLY that shard's totems + the 6 modifiers + extra shards (rebirth 2, any bench), gated by the bench tier
     (Server Setup rows bench.unlock.<kind>.<type> / bench.unlock.mod.<mod>); tiers totems up (shard:fn:totem "cost", the same totem.upCost
     rows, same document + uid, capped by bench.cap<N>); bench tiers I-IV upgraded at the bench: coins + items + a collection tier, then a
     real-time timer in seconds (<kind>.bench / benchTo / benchUpAt; the bench works at the old tier meanwhile; no pay-to-skip). Owner
     only, co-op view only. New Server Setup categories "Totem Bench" and "Bench unlocks" (all PLACEHOLDER numbers).
  3. TOTEM FORMS (9.3.1): Rain, Fertilizer and Blessing of the Sun start as a HAND-HELD Totem I (right-click it in hand ANYWHERE: Rain wets
     the tilled soil within totem.hand.rain.radius for totem.hand.rain.wetSec 30 s (real time) + a 30 s splash shower, the shower even
     with no soil; Fertilizer fertilizes the soil within totem.hand.fert.radius (until harvest); the Sun (by day only) wets within
     totem.hand.sun.radius for totem.hand.sun.wetSec 60 s - the vanilla Water x2.5 / Fertilizer x2 growth modifiers; cooldown
     totem.hand.cooldownSec 120 s per player and type; no tilled soil changed = no cooldown; only on islands / shards you belong to). A
     hand-held Totem I cannot go on a pad ("Tier it up to Totem Pole II at the Totem Bench first"). Every other totem starts as Totem Pole
     I. Names follow the ladder: Totem I (hand) / Totem Pole I-II / Grand Pole III / Ancient Pole IV / Mythic Pole V. A pole in hand says
     where to place it. Documents written by 0.4 carry "f" (h / p).
  4. MIGRATION (9.8, question 18 [grandfather]): placed shards, islands, storage, stored items, compactor, compressor, boosters, totems keep
     their keys and keep working. A placed tier-I Rain / Fertilizer / Sun record gets the flag gf (entry ":gf") once per profile file (run-
     once marker forms=1; a verified History snapshot shards/history/<pkey>.pre-0.4.properties first; a change-log line with the Undo in
     collect.log); a pre-0.4 tier-I hand-held-kind ITEM (a document without "f") counts as gf when 0.4 first sees it (placed / used /
     tiered up). A gf totem works on its pad, can be picked up / placed again as a pole AND used hand-held; tiering it up clears gf.
     Nothing is lost, nothing is given for free. Config: new rows read their defaults when missing (no file rewrite).
  5. Soil kept: a watered / fertilized tilled soil (a state of Soil_Dirt_Tilled) is no longer repainted by the hub repair.
NOT HERE (later rounds): the Totem crafting accessory + /totems (phase 10), the Mana cost of hand-held totems (Mana round), SkyyGear's Anvil
calling shard:fn:totem. UNVERIFIED (needs the game): probe B1 (the recoloured bench block draws, opens, survives the repair), the hand-held
use on a client (Secondary -> OpenCustomUI -> no page), the soil growth effect timing.
ROLLBACK / FLOOR: Shards 0.4 is a FLOOR once a hub has a bench block (0.3.2 does not know Skyy_TotemBench_*) or a document carries f / gf
(0.3.2 reads them as plain totems - a hand-held Totem I would place as a pole). Menu 0.3.27 -> 0.3.26 is safe.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyShards", "build_skyyshards_0.3.2.py")
dst = os.path.join(ROOT, "SkyyShards", "build_skyyshards_0.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.3.2"' in s and s.startswith('"""SkyyShards 0.3.2 - build script') and "BENCH_BLOCKS" not in s


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)


def span(a, b, new):
    """replace s[index(a) : end of the first b after it] (a and b both kept out of the new text unless new repeats them)"""
    global s
    assert s.count(a) == 1, "span start count %d: %s" % (s.count(a), a[:120])
    i = s.index(a)
    j = s.index(b, i)
    s = s[:i] + new + s[j + len(b):]


# ================================================================================================================== header + version
rep('''"""SkyyShards 0.3.2 - build script (javassist via jpype). GENERATED by tools/shards_0_3_2_patch.py from build_skyyshards_0.3.1.py
(edit the patch, never this file). Changes are marked "0.3.2".
Run:   python SkyyShards/build_skyyshards_0.3.2.py   -> SkyyShards/SkyyShards-0.3.2.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.3.2.py   (assets: no item Texture under Blocks/; compare 0.3.1 -> 0.3.2)
''', '''"""SkyyShards 0.4 - build script (javassist via jpype). GENERATED by tools/shards_0_4_patch.py from build_skyyshards_0.3.2.py
(edit the patch, never this file). Changes are marked "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.py   -> SkyyShards/SkyyShards-0.4.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.py

0.4 (2026-10-15) = Gathering-Shards-Spec PHASE 9 (research/Gathering-Shards-Spec.md 9.3.1 / 9.5 / 9.7 / 9.8; notes + Skyy's words:
tools/shards_0_4_patch.py): ONE MENU PER SHARD, opened only by right-clicking that shard's portal on your island (owner / co-op; anyone
else a chat line; no SkyWynn Menu route - shard:fn:open is gone; the hub stand = Back to Island only; a totem = its own page); a fixed
TOTEM BENCH Skyy_TotemBench_<Kind> on every hub (pasted by the hub repair) that crafts only its shard's totems + the modifiers + extra
shards, tiers totems up (capped by the bench tier) and upgrades I-IV with a timer in seconds; TOTEM FORMS - Rain / Fertilizer / Blessing
of the Sun start as a hand-held Totem I (right-click anywhere, cooldown), every other totem as Totem Pole I; the 9.8 MIGRATION (forms=1,
placed tier-I Rain / Fertilizer / Sun keep working as poles: gf). New Server Setup categories Totem Bench + Bench unlocks.

0.3.2 (its build line was: python SkyyShards/build_skyyshards_0.3.2.py -> SkyyShards/SkyyShards-0.3.2.jar)
''')
rep('VERSION = "0.3.2"\n', 'VERSION = "0.4"\n')

# ================================================================================================================== the model
rep('''TOTEM_PAGE_ID = "SkyyShardTotem"        # 0.2: the OpenCustomUI page id of every totem block (the menu on the Totems tab, nearest totem)
''', '''TOTEM_PAGE_ID = "SkyyShardTotem"        # 0.2: the OpenCustomUI page id of every totem block (0.4: the totem's OWN page)
# 0.4 (Gathering-Shards-Spec 9.5 / 9.7): one Totem Bench per shard on its hub island (fixed, Unbreakable, no item form, our page) + the
# page a totem ITEM opens when right-clicked in hand (a hand-held Totem I is used; a pole says where to place it - never a page)
BENCH_BLOCKS = ["Skyy_TotemBench_" + k for k in KINDS]
BENCH_PAGES = ["SkyyTotemBench" + k for k in KINDS]
HAND_PAGE_ID = "SkyyTotemUse"
BENCH_POS = (-3, 0)                     # the bench on the hub plaza (x, z from the hub origin; y + 1): west of the stand, off every bridge
''')
rep('''UP_DEF = "1:10,2:25,3:50,5:100"                            # Enchanted : essence for I->II .. IV->V (spec 9.3 PLACEHOLDER)
''', '''UP_DEF = "1:10,2:25,3:50,5:100"                            # Enchanted : essence for I->II .. IV->V (spec 9.3 PLACEHOLDER)
# 0.4 TOTEM FORMS (spec 9.3.1, question 15 [Rain + Fertilizer + Sun]): these start as a HAND-HELD Totem I, every other totem as Totem Pole I
HAND_KEYS = ("rain", "fertilizer", "sun_blessing")
# fix (critic shards04): the wet times are REAL seconds (spec 9.3.1 / question 17: Rain 30 s, Sun 60 s), turned into game seconds by the world's
# day length when used; the Sun only waters (a timed modifier - the vanilla fertilizer lasts until harvest)
HAND_DEF = {"cooldownSec": 120, "rain.radius": 5, "rain.wetSec": 30, "rain.showSec": 30, "fert.radius": 3, "sun.radius": 5, "sun.wetSec": 60}   # PLACEHOLDER
LADDER = ["Totem Pole I", "Totem Pole II", "Grand Pole III", "Ancient Pole IV", "Mythic Pole V"]   # spec 9.3 (a hand-held tier I = "Totem I")


def _base(n):
    for _suf in (" Totem", " Pole"):
        if n.endswith(_suf):
            return n[:-len(_suf)]
    return n


TOTEM_BASE = [_base(t[2]) for t in TOTEMS]          # "Rain Totem" -> "Rain" (+ " Totem I" / " Totem Pole II" ...)
assert all(k in [t[0] for t in TOTEMS] for k in HAND_KEYS) and TOTEM_BASE[0] == "Harvest Spirit"
# 0.4 THE TOTEM BENCH (spec 9.7; ALL PLACEHOLDER numbers, Server Setup -> Shards -> Totem Bench / Bench unlocks): the bench tier each totem of
# a shard needs (9.3.1 "Bench tier to craft"), the modifiers' tiers, the totem tier a bench tier caps at, the upgrade costs / times / needs
BENCH_UNLOCK = {
    "Farming": {"harvest_spirit": 1, "rain": 1, "scarecrow": 1, "fertilizer": 2, "compost": 2, "pollinator": 2, "season_ward": 2,
                "sun_blessing": 3, "fairy_grove": 3, "mushroom_shade": 3, "harvest_moon": 4},
    "Orchard": {"harvest_spirit": 1, "rain": 1, "fertilizer": 2, "pollinator": 2, "season_ward": 2},
    "Ranching": {"harvest_spirit": 1, "herd_pole": 1, "scarecrow": 1},
    "Foraging": {"lumber_spirit": 1, "fertilizer": 2, "sap_tap": 2},
    "Mining": {"quarry_spirit": 1, "autosmelt_pole": 2, "geode_pole": 3},
    "Combat": {"soul_cage": 1, "lure_pole": 2, "trophy_pole": 3},
}
for _k in range(NK):    # each bench lists exactly the totems that work in its shard (KMASK)
    assert set(BENCH_UNLOCK[KINDS[_k]]) == set(t[0] for _i, t in enumerate(TOTEMS) if (KMASK[_i] >> _k) & 1), KINDS[_k]
MOD_BENCH = {"wider": 1, "faster": 1, "replant": 2, "storage": 2, "compost": 3, "rare": 3}
assert set(MOD_BENCH) == set(m[0] for m in MODS)
BENCH_CAP_DEF = [0, 2, 3, 4, 5]                 # index = bench tier: the highest totem tier it tiers up to (question 20 [yes])
BENCH_COINS_DEF = [0, 0, 25000, 100000, 400000]  # index = the tier being bought (question 26)
BENCH_SEC_DEF = [0, 0, 300, 1800, 7200]
BENCH_NEED_DEF = [0, 0, 3, 5, 7]                # the shard's collection tier
BENCH_ENCH_DEF = [0, 0, 2, 8, 24]               # Enchanted shard material (Bench IV + 10 Void Essence)
# "shard material" (9.7): Farming Enchanted Wheat, Mining Enchanted Copper Ingot, Foraging Enchanted Oak Log; no Enchanted form yet ->
# 100 of the island's base item per Enchanted asked (Ranching Raw Chicken, Orchard Apple, Combat Bone Fragments)
BENCH_MAT = {"Farming": ("Skyy_Ench_Wheat", 1), "Mining": ("Skyy_Ench_Copper", 1), "Foraging": ("Skyy_Ench_Oak", 1),
             "Ranching": ("Food_Chicken_Raw", 100), "Orchard": ("Plant_Fruit_Apple", 100), "Combat": ("Ingredient_Bone_Fragment", 100)}


def _bench_items(k, n):
    _it, _per = BENCH_MAT[KINDS[k]]
    return "%s:%d" % (_it, BENCH_ENCH_DEF[n] * _per) + (",Ingredient_Void_Essence:10" if n == 4 else "")


BENCH_ITEMS_DEF = [[(_bench_items(_k, _n) if _n >= 2 else "") for _k in range(NK)] for _n in range(5)]
BENCH_UNL_FLAT = [BENCH_UNLOCK[KINDS[_k]].get(t[0], 0) for _k in range(NK) for t in TOTEMS]   # index kind * NT + totem; 0 = not on that bench
MOD_UNL_DEF = [MOD_BENCH[m[0]] for m in MODS]
''')
# ================================================================================================================== Assets.zip checks
rep('''for _n in ("Common/" + TOTEM_MODEL, TOTEM_TEX_SRC, TOTEM_ICON_SRC, MOD_ICON_SRC):
    assert _n in AZN, "vanilla asset %s missing" % _n
''', '''for _n in ("Common/" + TOTEM_MODEL, TOTEM_TEX_SRC, TOTEM_ICON_SRC, MOD_ICON_SRC):
    assert _n in AZN, "vanilla asset %s missing" % _n
# 0.4: the Totem Bench look = the vanilla Abilities bench (a 1-block statue hitbox), recoloured per shard at BUILD time; the hand-held
# totems' particles; our new ids are new; the bench costs name real items
BENCH_MODEL = "Blocks/Benches/Abilities_Bench.blockymodel"
BENCH_TEX_SRC = "Common/Blocks/Benches/Abilities_Bench_Active_Texture.png"
# fix (critic shards04, "our own icons only"): the bench's icon = OUR shard portal icon (research/cloud/icons-1013), not a vanilla recolour
for _n in ("Common/" + BENCH_MODEL, BENCH_TEX_SRC, "Server/Item/Block/Hitboxes/Furniture/Statue/Statue_Small.json"):
    assert _n in AZN, "0.4: vanilla asset %s missing" % _n
_ab = json.loads(AZ.read(ITEMS["Bench_Abilities"]).decode("utf-8-sig"))["BlockType"]
assert _ab["CustomModel"] == BENCH_MODEL and _ab["HitboxType"] == "Statue_Small", "0.4: the Abilities bench changed"
HAND_PARTICLES = {"rain": "Water_Can_Splash", "fertilizer": "Dust_Sparkles", "sun_blessing": "Dust_Sparkles_Light"}
for _pp in HAND_PARTICLES.values():
    assert any(n.endswith("/" + _pp + ".particlesystem") for n in AZN), "0.4: particle system %s missing" % _pp
for _iid in BENCH_BLOCKS:
    assert _iid not in ITEMS, "0.4: our id %s clashes with a vanilla item" % _iid
for _row in BENCH_ITEMS_DEF:
    for _txt in _row:
        for _part in [x for x in _txt.split(",") if x]:
            _pid = _part.split(":")[0]
            assert _pid in ITEMS or _pid in _SE.IDS, "0.4: bench cost names unknown item %s" % _pid
''')

# ================================================================================================================== config text + rows
rep('''    "# totem.upCost = tier-up costs on the Anvil (SkyyGear), I->II .. IV->V, each Enchanted:essence.",''',
    '''    "# totem.upCost = tier-up costs at the shard's Totem Bench (0.4), I->II .. IV->V, each Enchanted:essence.",''')
rep('''    "# craft.<ItemId> = a menu recipe: Item:qty,Item:qty;coins (empty = that recipe is off).",''',
    '''    "# craft.<ItemId> = a Totem Bench recipe (0.4: the bench of the totem's shard; modifiers + extra shards at every bench): Item:qty,Item:qty;coins (empty = that recipe is off).",''')
rep('''    "totem.particleSec=2",
    "",
])''', '''    "totem.particleSec=2",
    # 0.4 TOTEM FORMS + THE TOTEM BENCH (spec 9.3.1 / 9.7; PLACEHOLDER numbers; times in seconds)
    "# totem.hand.* = the hand-held Totem I (Rain, Fertilizer, Blessing of the Sun): right-click it anywhere. cooldownSec = seconds before",
    "# the same player can use that type again; rain.radius / fert.radius / sun.radius = blocks around you; rain.wetSec / sun.wetSec =",
    "# real seconds the soil stays wet (crops x2.5 meanwhile); rain.showSec = seconds of the splash shower. Fertilizer = until harvest.",
    "totem.hand.cooldownSec=%d" % HAND_DEF["cooldownSec"], "totem.hand.rain.radius=%d" % HAND_DEF["rain.radius"],
    "totem.hand.rain.wetSec=%d" % HAND_DEF["rain.wetSec"], "totem.hand.rain.showSec=%d" % HAND_DEF["rain.showSec"],
    "totem.hand.fert.radius=%d" % HAND_DEF["fert.radius"], "totem.hand.sun.radius=%d" % HAND_DEF["sun.radius"],
    "totem.hand.sun.wetSec=%d" % HAND_DEF["sun.wetSec"],
    "# bench.capN = the highest totem tier (1-5) a tier N Totem Bench tiers totems up to.",
] + ["bench.cap%d=%d" % (_n, BENCH_CAP_DEF[_n]) for _n in range(1, 5)] + [
    "# bench.upN.* = upgrading a Totem Bench to tier N: coins, seconds it takes (the bench works at the old tier meanwhile), the shard's",
    "# collection tier it needs, and the items per shard (Item:qty,Item:qty).",
] + ["bench.up%d.coins=%d" % (_n, BENCH_COINS_DEF[_n]) for _n in range(2, 5)] + ["bench.up%d.sec=%d" % (_n, BENCH_SEC_DEF[_n]) for _n in range(2, 5)] + \\
    ["bench.up%d.needs=%d" % (_n, BENCH_NEED_DEF[_n]) for _n in range(2, 5)] + \\
    ["bench.up%d.items.%s=%s" % (_n, KKEYS[_k], BENCH_ITEMS_DEF[_n][_k]) for _n in range(2, 5) for _k in range(NK)] + [
    "# bench.unlock.<shard>.<totem> = the bench tier (1-4) that unlocks crafting that totem at that shard's bench;",
    "# bench.unlock.mod.<modifier> = the bench tier that unlocks crafting that modifier (every bench).",
] + ["bench.unlock.%s.%s=%d" % (KKEYS[_k], TOTEMS[_i][0], BENCH_UNL_FLAT[_k * NT + _i]) for _k in range(NK) for _i in range(NT) if BENCH_UNL_FLAT[_k * NT + _i] > 0] + \\
    ["bench.unlock.mod.%s=%d" % (MODS[_i][0], MOD_UNL_DEF[_i]) for _i in range(len(MODS))] + [
    "",
])''')

# ShCfg: the new fields (arrays swapped whole by the loader)
rep('''          "public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT)):
    F(cfg, f)''', '''          # 0.4: the hand-held totems + the Totem Bench (index = bench tier / tier bought; items index = tier x kinds + kind;
          # unlock index = kind x totems + totem, 0 = not on that bench)
          "public static volatile int HAND_CD = %d;" % HAND_DEF["cooldownSec"], "public static volatile int HAND_RAIN_R = %d;" % HAND_DEF["rain.radius"],
          "public static volatile int HAND_RAIN_WET = %d;" % HAND_DEF["rain.wetSec"], "public static volatile int HAND_RAIN_SHOW = %d;" % HAND_DEF["rain.showSec"],
          "public static volatile int HAND_FERT_R = %d;" % HAND_DEF["fert.radius"], "public static volatile int HAND_SUN_R = %d;" % HAND_DEF["sun.radius"],
          "public static volatile int HAND_SUN_WET = %d;" % HAND_DEF["sun.wetSec"],
          "public static volatile int[] BENCH_CAP = new int[] { %s };" % ", ".join(str(x) for x in BENCH_CAP_DEF),
          "public static volatile long[] BENCH_COINS = new long[] { %s };" % ", ".join("%dL" % x for x in BENCH_COINS_DEF),
          "public static volatile int[] BENCH_SEC = new int[] { %s };" % ", ".join(str(x) for x in BENCH_SEC_DEF),
          "public static volatile int[] BENCH_NEED = new int[] { %s };" % ", ".join(str(x) for x in BENCH_NEED_DEF),
          "public static volatile String[] BENCH_ITEMS = new String[] { %s };" % ", ".join(jlit(BENCH_ITEMS_DEF[_n][_k]) for _n in range(5) for _k in range(NK)),
          "public static final String[] DEF_BENCH_ITEMS = new String[] { %s };" % ", ".join(jlit(BENCH_ITEMS_DEF[_n][_k]) for _n in range(5) for _k in range(NK)),
          "public static volatile int[] BENCH_UNL = new int[] { %s };" % ", ".join(str(x) for x in BENCH_UNL_FLAT),
          "public static volatile int[] MOD_UNL = new int[] { %s };" % ", ".join(str(x) for x in MOD_UNL_DEF),
          "public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT)):
    F(cfg, f)''')
rep('''    ("totem.upCost", "Tier-up costs (Anvil)", "totems", "text", UP_DEF, "", "120", "", "", "live",
     "Enchanted:essence for I->II, II->III, III->IV, IV->V (the Anvil in SkyyGear uses them).", "reload@config.properties:totem.upCost"),''',
    '''    ("totem.upCost", "Tier-up costs (Totem Bench)", "totems", "text", UP_DEF, "", "120", "", "", "live",
     "Enchanted:essence for I->II, II->III, III->IV, IV->V (tier up at the shard's Totem Bench).", "reload@config.properties:totem.upCost"),''')
rep('''kit = CFG.emit(pool, PKG''', '''# 0.4: the hand-held totems (Totems) + Server Setup -> Shards -> Totem Bench / Bench unlocks (reload@ rows: the loader swaps the arrays)
CATS = CATS + [("bench", "Totem Bench"), ("benchUnlock", "Bench unlocks")]
ROWS += [
    ("totem.hand.cooldownSec", "Hand-held totem cooldown", "totems", "int", str(HAND_DEF["cooldownSec"]), "0", "86400", "", "s", "live",
     "Seconds before a player can use a hand-held Totem I (Rain, Fertilizer, Sun) of that type again.", "reload@config.properties:totem.hand.cooldownSec"),
    ("totem.hand.rain.radius", "Hand-held Rain: radius", "totems", "int", str(HAND_DEF["rain.radius"]), "0", "16", "", "blocks", "live",
     "Tilled soil within this many blocks of you gets wet.", "reload@config.properties:totem.hand.rain.radius"),
    ("totem.hand.rain.wetSec", "Hand-held Rain: soil stays wet", "totems", "int", str(HAND_DEF["rain.wetSec"]), "0", "86400", "", "s", "live",
     "Seconds (real time) the soil stays wet after a Rain. Wet soil grows crops x2.5.", "reload@config.properties:totem.hand.rain.wetSec"),
    ("totem.hand.rain.showSec", "Hand-held Rain: shower lasts", "totems", "int", str(HAND_DEF["rain.showSec"]), "0", "600", "", "s", "live",
     "Seconds the splash shower is shown around the spot.", "reload@config.properties:totem.hand.rain.showSec"),
    ("totem.hand.fert.radius", "Hand-held Fertilizer: radius", "totems", "int", str(HAND_DEF["fert.radius"]), "0", "16", "", "blocks", "live",
     "Tilled soil within this many blocks of you is fertilized (crops x2 until harvested).", "reload@config.properties:totem.hand.fert.radius"),
    ("totem.hand.sun.radius", "Hand-held Sun: radius", "totems", "int", str(HAND_DEF["sun.radius"]), "0", "16", "", "blocks", "live",
     "By day: tilled soil within this many blocks gets wet for totem.hand.sun.wetSec.", "reload@config.properties:totem.hand.sun.radius"),
    ("totem.hand.sun.wetSec", "Hand-held Sun: soil stays wet", "totems", "int", str(HAND_DEF["sun.wetSec"]), "0", "86400", "", "s", "live",
     "Seconds (real time) the Blessing of the Sun keeps the soil wet (crops x2.5).", "reload@config.properties:totem.hand.sun.wetSec"),
]
ROWS += [("bench.cap%d" % _n, "Bench %s: totems tier up to" % ROMAN[_n - 1], "bench", "int", str(BENCH_CAP_DEF[_n]), "1", "5", "", "", "live",
          "The highest totem tier (1-5) a tier %s Totem Bench tiers totems up to." % ROMAN[_n - 1], "reload@config.properties:bench.cap%d" % _n)
         for _n in range(1, 5)]
ROWS += [("bench.up%d.coins" % _n, "Bench %s upgrade: coins" % ROMAN[_n - 1], "bench", "int", str(BENCH_COINS_DEF[_n]), "0", "1000000000", "", "", "live",
          "Coins to upgrade a Totem Bench to tier %s." % ROMAN[_n - 1], "reload@config.properties:bench.up%d.coins" % _n) for _n in range(2, 5)]
ROWS += [("bench.up%d.sec" % _n, "Bench %s upgrade: time" % ROMAN[_n - 1], "bench", "int", str(BENCH_SEC_DEF[_n]), "0", "2592000", "", "s", "live",
          "Seconds the upgrade to Bench %s takes (real time, also offline). 0 = at once." % ROMAN[_n - 1], "reload@config.properties:bench.up%d.sec" % _n)
         for _n in range(2, 5)]
ROWS += [("bench.up%d.needs" % _n, "Bench %s upgrade: collection tier" % ROMAN[_n - 1], "bench", "int", str(BENCH_NEED_DEF[_n]), "0", "20", "", "", "live",
          "The shard's collection tier (Wheat, Copper ...) needed for Bench %s." % ROMAN[_n - 1], "reload@config.properties:bench.up%d.needs" % _n)
         for _n in range(2, 5)]
ROWS += [("bench.up%d.items.%s" % (_n, KKEYS[_k]), "Bench %s items: %s" % (ROMAN[_n - 1], KINDS[_k]), "bench", "text", BENCH_ITEMS_DEF[_n][_k], "", "300",
          "", "", "live", "Item:qty,Item:qty to upgrade the %s Totem Bench to tier %s (empty = coins only)." % (KINDS[_k], ROMAN[_n - 1]),
          "reload@config.properties:bench.up%d.items.%s" % (_n, KKEYS[_k])) for _n in range(2, 5) for _k in range(NK)]
ROWS += [("bench.unlock.%s.%s" % (KKEYS[_k], TOTEMS[_i][0]), "%s: %s" % (KINDS[_k], TOTEM_BASE[_i]), "benchUnlock", "int",
          str(BENCH_UNL_FLAT[_k * NT + _i]), "1", "4", "", "", "live",
          "The bench tier (1-4) that unlocks crafting the %s at the %s Totem Bench." % (TOTEMS[_i][2], KINDS[_k]),
          "reload@config.properties:bench.unlock.%s.%s" % (KKEYS[_k], TOTEMS[_i][0])) for _k in range(NK) for _i in range(NT) if BENCH_UNL_FLAT[_k * NT + _i] > 0]
ROWS += [("bench.unlock.mod.%s" % MODS[_i][0], "Modifier: %s" % MODS[_i][2], "benchUnlock", "int", str(MOD_UNL_DEF[_i]), "1", "4", "", "", "live",
          "The bench tier (1-4) that unlocks crafting the %s modifier (every bench)." % MODS[_i][2],
          "reload@config.properties:bench.unlock.mod.%s" % MODS[_i][0]) for _i in range(len(MODS))]
for _r in ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, "0.4: Server Setup label / help too long: %s" % (_r[0],)
kit = CFG.emit(pool, PKG''')

# the loader (0.4 rows; a line missing = its default; an EMPTY bench items line = coins only)
rep('''_load += ["  GROWK = gk;"]
''', '''_load += ["  GROWK = gk;"]
_load += ["  HAND_CD = intOf(p.getProperty(\\"totem.hand.cooldownSec\\"), %d, 0, 86400);" % HAND_DEF["cooldownSec"],
          "  HAND_RAIN_R = intOf(p.getProperty(\\"totem.hand.rain.radius\\"), %d, 0, 16);" % HAND_DEF["rain.radius"],
          "  HAND_RAIN_WET = intOf(p.getProperty(\\"totem.hand.rain.wetSec\\"), %d, 0, 86400);" % HAND_DEF["rain.wetSec"],
          "  HAND_RAIN_SHOW = intOf(p.getProperty(\\"totem.hand.rain.showSec\\"), %d, 0, 600);" % HAND_DEF["rain.showSec"],
          "  HAND_FERT_R = intOf(p.getProperty(\\"totem.hand.fert.radius\\"), %d, 0, 16);" % HAND_DEF["fert.radius"],
          "  HAND_SUN_R = intOf(p.getProperty(\\"totem.hand.sun.radius\\"), %d, 0, 16);" % HAND_DEF["sun.radius"],
          "  HAND_SUN_WET = intOf(p.getProperty(\\"totem.hand.sun.wetSec\\"), %d, 0, 86400);" % HAND_DEF["sun.wetSec"],
          "  int[] bcp = new int[5];"]
_load += ["  bcp[%d] = intOf(p.getProperty(\\"bench.cap%d\\"), %d, 1, 5);" % (_n, _n, BENCH_CAP_DEF[_n]) for _n in range(1, 5)]
_load += ["  BENCH_CAP = bcp;", "  long[] bco = new long[5]; int[] bse = new int[5]; int[] bne = new int[5];"]
_load += ["  bco[%d] = (long) intOf(p.getProperty(\\"bench.up%d.coins\\"), %d, 0, 1000000000);" % (_n, _n, BENCH_COINS_DEF[_n]) for _n in range(2, 5)]
_load += ["  bse[%d] = intOf(p.getProperty(\\"bench.up%d.sec\\"), %d, 0, 2592000);" % (_n, _n, BENCH_SEC_DEF[_n]) for _n in range(2, 5)]
_load += ["  bne[%d] = intOf(p.getProperty(\\"bench.up%d.needs\\"), %d, 0, 20);" % (_n, _n, BENCH_NEED_DEF[_n]) for _n in range(2, 5)]
_load += ["  BENCH_COINS = bco; BENCH_SEC = bse; BENCH_NEED = bne;", "  String[] bit = new String[%d];" % (5 * NK),
          "  for (int bq = 0; bq < bit.length; bq++) bit[bq] = DEF_BENCH_ITEMS[bq];"]
_load += ["  { String bv = p.getProperty(\\"bench.up%d.items.%s\\"); if (bv != null) bit[%d] = bv.trim(); }" % (_n, KKEYS[_k], _n * NK + _k)
          for _n in range(2, 5) for _k in range(NK)]
_load += ["  BENCH_ITEMS = bit;", "  int[] bun = new int[%d];" % (NK * NT)]
_load += ["  bun[%d] = intOf(p.getProperty(\\"bench.unlock.%s.%s\\"), %d, 1, 4);" % (_k * NT + _i, KKEYS[_k], TOTEMS[_i][0], BENCH_UNL_FLAT[_k * NT + _i])
          for _k in range(NK) for _i in range(NT) if BENCH_UNL_FLAT[_k * NT + _i] > 0]
_load += ["  BENCH_UNL = bun;", "  int[] mun = new int[%d];" % len(MODS)]
_load += ["  mun[%d] = intOf(p.getProperty(\\"bench.unlock.mod.%s\\"), %d, 1, 4);" % (_i, MODS[_i][0], MOD_UNL_DEF[_i]) for _i in range(len(MODS))]
_load += ["  MOD_UNL = mun;"]
''')
# ShCfg: the bench lookups (after growOf)
rep('''# ================= ShStore: Skyy_SkyyShards/shards/<pkey>.properties (one profile), cached, written at once (tmp + move) =================
''', '''# 0.4: the Totem Bench lookups (spec 9.7). benchCap(tier 1-4) = the highest totem tier it tiers up to; benchItems(tier 2-4, kind) = the
# upgrade items text; benchUnlock(kind, totem) = the bench tier that unlocks it there (0 = not on that bench); modUnlock(modifier)
M(cfg, r"""
public static int benchCap(int tier) {
  int[] a = BENCH_CAP;
  int t = tier < 1 ? 1 : (tier > 4 ? 4 : tier);
  int c = t < a.length ? a[t] : 5;
  return c < 1 ? 1 : (c > 5 ? 5 : c);
}""")
M(cfg, r"""
public static String benchItems(int n, int kd) {
  String[] a = BENCH_ITEMS;
  if (n < 2 || n > 4 || kd < 0 || kd >= @NK@ || n * @NK@ + kd >= a.length) return "";
  String v = a[n * @NK@ + kd];
  return v == null ? "" : v;
}""".replace("@NK@", str(NK)))
M(cfg, r"""
public static int benchUnlock(int kd, int ti) {
  int[] a = BENCH_UNL;
  if (kd < 0 || ti < 0 || ti >= @NT@ || kd * @NT@ + ti >= a.length) return 0;
  return a[kd * @NT@ + ti];
}""".replace("@NT@", str(NT)))
M(cfg, r"""
public static int modUnlock(int mi) {
  int[] a = MOD_UNL;
  if (mi < 0 || mi >= a.length) return 4;
  int t = a[mi];
  return t < 1 ? 1 : (t > 4 ? 4 : t);
}""")

# ================= ShStore: Skyy_SkyyShards/shards/<pkey>.properties (one profile), cached, written at once (tmp + move) =================
''')
# ================================================================================================================== ShStore: the migration hook
# 0.4: ShStore.get runs the one-time 9.8 forms migration on a profile file the first time it is read (migrate: a stub here, its body is
# set once ShTotem exists - javassist compiles a body when it is added; see "ShStore.migrate body" below)
rep('''# the profile's live Properties (the cache owns it; callers change it only while holding ShStore.LOCK - a ReentrantLock, javassist's synchronized blocks hold one call - then save)
M(st, r"""
public static java.util.Properties get(String k) {
  if (!validKey(k) || DIR == null) return null;
  Object o = CACHE.get(k);
  if (o != null) return (java.util.Properties) o;
  java.util.Properties p = readNow(k);
  if (p == null) return null;
  if (p.getProperty("pkey") == null) p.setProperty("pkey", k);   // 0.2: the Harvest Moon roll seed + the Moon Blade lookup know whose shard it is
  Object prev = CACHE.putIfAbsent(k, p);
  return prev != null ? (java.util.Properties) prev : p;
}""")''', '''F(st, "public static final java.util.concurrent.atomic.AtomicLong MIGRATED = new java.util.concurrent.atomic.AtomicLong();")   # 0.4: files migrated
M(st, "public static void migrate(String k, java.util.Properties p) { }")   # 0.4: the body is set below (after ShTotem)
# the profile's live Properties (the cache owns it; callers change it only while holding ShStore.LOCK - a ReentrantLock, javassist's synchronized blocks hold one call - then save)
M(st, r"""
public static java.util.Properties get(String k) {
  if (!validKey(k) || DIR == null) return null;
  Object o = CACHE.get(k);
  if (o != null) return (java.util.Properties) o;
  java.util.Properties p = readNow(k);
  if (p == null) return null;
  if (p.getProperty("pkey") == null) p.setProperty("pkey", k);   // 0.2: the Harvest Moon roll seed + the Moon Blade lookup know whose shard it is
  Object prev = CACHE.putIfAbsent(k, p);
  if (prev != null) return (java.util.Properties) prev;
  migrate(k, p);   // 0.4: the 9.8 forms migration, once per profile file (marker forms=1)
  return p;
}""")''')

# ================================================================================================================== ShTotem: forms + gf
rep('''F(tot, "public static volatile java.util.function.Function SOUL_TEST = null;")      # harness: the armory:fn:soulcage stand-in
''', '''F(tot, "public static volatile java.util.function.Function SOUL_TEST = null;")      # harness: the armory:fn:soulcage stand-in
# 0.4 TOTEM FORMS (spec 9.3.1): the hand-held kinds, the names without "Totem" / "Pole", the tier ladder
F(tot, "public static final boolean[] HAND = new boolean[] { %s };" % ", ".join("true" if t[0] in HAND_KEYS else "false" for t in TOTEMS))
F(tot, "public static final String[] BASE = new String[] { %s };" % ", ".join(jlit(x) for x in TOTEM_BASE))
F(tot, "public static final String[] LADDER = new String[] { %s };" % ", ".join(jlit(x) for x in LADDER))
''')
rep('''public static String[] parse(String e) {
  String[] f = new String[] { "", "1", "", "", "0", "" };''', '''public static String[] parse(String e) {
  String[] f = new String[] { "", "1", "", "", "0", "", "" };   // 0.4: f[6] = flags ("gf" = a grandfathered pre-0.4 tier-I hand-held kind)''')
rep('''  if (a.length > 5) f[5] = a[5].trim().replace(",", "").replace(":", "");
  return f;
}""")
M(tot, r"""
public static String fmt(String[] f) {
  return f[0] + ":" + f[1] + ":" + f[2] + ":" + f[3] + ":" + f[4] + ":" + f[5];
}""")''', '''  if (a.length > 5) f[5] = a[5].trim().replace(",", "").replace(":", "");
  if (a.length > 6 && "gf".equals(a[6].trim())) f[6] = "gf";   // 0.4
  return f;
}""")
# 0.4: the flag rides as a 7th part only when set - an entry without it is byte for byte the 0.3.2 one (0.3.2 reads the first six parts)
M(tot, r"""
public static String fmt(String[] f) {
  String s = f[0] + ":" + f[1] + ":" + f[2] + ":" + f[3] + ":" + f[4] + ":" + f[5];
  if (f.length > 6 && f[6] != null && f[6].length() > 0) s = s + ":" + f[6];
  return s;
}""")''')
rep('''M(tot, r"""
public static String name(String[] f) {
  int ti = idx(f[0]);
  return (ti < 0 ? f[0] : NAMES[ti]) + " " + ROMAN[tierOf(f[1]) - 1];
}""")''', '''# 0.4 FORMS: gf = a grandfathered pre-0.4 tier-I Rain / Fertilizer / Sun (works placed AND in hand); handHeld = a hand-held Totem I (never on
# a pad); usable = may be used in hand (a hand-held kind at tier I, gf too); the name follows the ladder (spec 9.3)
M(tot, "public static boolean gf(String[] f) { return f != null && f.length > 6 && \\"gf\\".equals(f[6]); }")
M(tot, "public static boolean handKind(int ti) { return ti >= 0 && ti < HAND.length && HAND[ti]; }")
M(tot, "public static boolean handHeld(String[] f) { return handKind(idx(f[0])) && tierOf(f[1]) == 1 && !gf(f); }")
M(tot, "public static boolean usable(String[] f) { return handKind(idx(f[0])) && tierOf(f[1]) == 1; }")
# fix (critic shards04): a record ON A PAD was placed as a pole - a tier-I Rain / Fertilizer / Sun there without gf (a forms migration
# still waiting, or a rollback in between) reads as gf (memory only: names, the picked-up item). The file is changed only by migrate().
M(tot, r"""
public static String[] onPad(String e) {
  String[] f = parse(e);
  if (usable(f) && !gf(f)) f[6] = "gf";
  return f;
}""")
M(tot, r"""
public static String form(String[] f) {
  if (handHeld(f)) return "Totem I";
  return LADDER[tierOf(f[1]) - 1];
}""")
M(tot, r"""
public static String name(String[] f) {
  int ti = idx(f[0]);
  return (ti < 0 ? f[0] : BASE[ti]) + " " + form(f);
}""")
M(tot, r"""
public static String nextName(String[] f) {
  int ti = idx(f[0]);
  int t = tierOf(f[1]);
  if (t >= 5) return "";
  return (ti < 0 ? f[0] : BASE[ti]) + " " + LADDER[t];
}""")''')
# the document: + "f" (h / p) and "gf"
rep('''  d.append("uid", new org.bson.BsonString(f[5]));
  return d;
}""")''', '''  d.append("uid", new org.bson.BsonString(f[5]));
  d.append("f", new org.bson.BsonString(handHeld(f) ? "h" : "p"));   // 0.4: every 0.4 document carries its form (spec 9.8)
  if (gf(f)) d.append("gf", new org.bson.BsonInt32(1));
  return d;
}""")''')
rep('''  String[] f = new String[] { KEYS[ti], "1", "", "", "0", "" };
  if (d == null) return f;
  String t = dstr(d, "t");
  if (t.length() > 0 && !t.equals(KEYS[ti])) return null;
  f[1] = String.valueOf(tierOf(String.valueOf(dlong(d, "tier"))));
  if (modIdx(dstr(d, "m1")) >= 0) f[2] = dstr(d, "m1");
  if (modIdx(dstr(d, "m2")) >= 0) f[3] = dstr(d, "m2");
  long b = dlong(d, "bst");
  f[4] = String.valueOf(b > 0L ? now + b : 0L);
  f[5] = dstr(d, "uid").replace(",", "").replace(":", "");
  return f;
}""")''', '''  String[] f = new String[] { KEYS[ti], "1", "", "", "0", "", "" };
  if (d == null) return f;
  String t = dstr(d, "t");
  if (t.length() > 0 && !t.equals(KEYS[ti])) return null;
  f[1] = String.valueOf(tierOf(String.valueOf(dlong(d, "tier"))));
  if (modIdx(dstr(d, "m1")) >= 0) f[2] = dstr(d, "m1");
  if (modIdx(dstr(d, "m2")) >= 0) f[3] = dstr(d, "m2");
  long b = dlong(d, "bst");
  f[4] = String.valueOf(b > 0L ? now + b : 0L);
  f[5] = dstr(d, "uid").replace(",", "").replace(":", "");
  boolean hasF = false;
  try { hasF = d.containsKey("f"); } catch (Throwable x) { hasF = false; }
  if (dlong(d, "gf") == 1L) f[6] = "gf";
  else if (!hasF && HAND[ti] && tierOf(f[1]) == 1) f[6] = "gf";   // 0.4 (spec 9.8): a pre-0.4 tier-I hand-held-kind document = grandfathered
  return f;
}""")''')
rep('''  if (ti >= 0) sb.append("\\nWorks in: ").append(kindsOf(ti)).append(" Shard");
  sb.append("\\nPlace it from the shard menu (Totems tab).");
  return sb.toString();''', '''  if (ti >= 0) sb.append("\\nWorks in: ").append(kindsOf(ti)).append(" Shard");
  if (handHeld(f)) sb.append("\\nHand-held: right-click it anywhere. Tier it up to Totem Pole II at the Totem Bench to place it.");   // 0.4
  else if (gf(f) && usable(f)) sb.append("\\nOld Totem I: works on a pad AND in your hand.\\nPlace it from the shard menu (Totems tab).");
  else sb.append("\\nPlace it from the shard menu (Totems tab).");
  return sb.toString();''')
# shard:fn:totem "up": the new tier is a pole (f = p, gf cleared - spec 9.8); "describe" names the form
rep('''  if ("describe".equals(op)) return name(f) + " - range " + range(f, 0L) + " - " + (WORKER[ti] ? "worker" : "support");''',
    '''  if ("describe".equals(op)) return name(f) + " - range " + range(f, 0L) + " - " + (WORKER[ti] ? "worker" : "support") + (handHeld(f) ? " - hand-held" : "");''')
rep('''    nd.put("tier", new org.bson.BsonInt32(tier + 1));
''', '''    nd.put("tier", new org.bson.BsonInt32(tier + 1));
    nd.put("f", new org.bson.BsonString("p"));   // 0.4: Totem I -> Totem Pole II (spec 9.3.1); a grandfathered one is a plain pole now
    nd.remove("gf");
''')
rep('''  int ti = itemIdx(id);
  if (ti >= 0) return NAMES[ti] + " " + ROMAN[0];''', '''  int ti = itemIdx(id);
  if (ti >= 0) return BASE[ti] + (HAND[ti] ? " Totem I" : " Totem Pole I");   // 0.4: a fresh one comes out in its 9.3.1 form''')
# shard:fn:totem "cost" keeps pricing by the totem's first shard (SkyyGear's Anvil, later); 0.4: costFor / costAt price by a GIVEN shard - the
# Totem Bench of that shard (its upgrade item + essence; Combat = the Soul Orb ladder's essence)
rep('''  if ("cost".equals(op)) {   // 0.3: the Enchanted / upgrade item of the totem's (first) shard + its essence (Combat: the Soul Orb ladder's)
    int kd = firstKind(ti);
    String en = @PKG@.ShKind.UPG[kd];
    String es = essence(kd, tier);
    if (en.equals(es)) return en + ":" + (c[0] + c[1]);
    return en + ":" + c[0] + "," + es + ":" + c[1];
  }''', '''  if ("cost".equals(op)) return costFor(firstKind(ti), tier, c);   // 0.3: the totem's (first) shard; 0.4: the same text through costFor''')
rep('''# shard:fn:totem (SkyyGear's Anvil calls it later): Object[]{ String op, String itemId, String docJson } -> String
''', '''M(tot, r\"\"\"
public static String costFor(int kd, int tier, int[] c) {
  String en = @PKG@.ShKind.UPG[kd];
  String es = essence(kd, tier);
  if (en.equals(es)) return en + ":" + (c[0] + c[1]);
  return en + ":" + c[0] + "," + es + ":" + c[1];
}\"\"\")
M(tot, r\"\"\"
public static String costAt(int kd, String itemId, String json) {
  int ti = itemIdx(itemId);
  if (ti < 0 || !@PKG@.ShKind.ok(kd)) return "err:not a totem";
  @BD@ d = null;
  try { if (json != null && json.trim().length() > 0) d = @BD@.parse(json); } catch (Throwable t) { return "err:bad document"; }
  String[] f = fromDoc(d, itemId, 0L);
  if (f == null) return "err:the document is another totem type";
  int tier = tierOf(f[1]);
  int[] c = upCost(tier);
  if (c == null) return tier >= 5 ? "err:max tier" : "err:the tier-up cost setting is broken (totem.upCost)";
  return costFor(kd, tier, c);
}\"\"\")
# shard:fn:totem (SkyyGear's Anvil calls it later): Object[]{ String op, String itemId, String docJson } -> String
''')
# ================================================================================================================== ShStore.migrate body
rep('''# ================= ShMath: lazy production (spec 9.2; no ticking) - pure, any thread, under the ShStore lock when it changes a profile =================
''', '''# ================= 0.4 ShStore.migrate (spec 9.8, question 18 [grandfather]): once per profile file, marker forms=1 =================
# A placed tier-I Rain / Fertilizer / Sun record (made before 0.4) gets the flag gf: it keeps working on its pad, can be picked up and
# placed again as a pole AND used in hand. PROJECT-RULES 4: a VERIFIED History snapshot of the file first (shards/history/<pkey>.pre-0.4
# .properties, byte-compared), then the change + the marker in one write, then a change-log line with the Undo (collect.log). Nothing
# to change = the marker rides along with the next save (no write). A refused snapshot / save leaves the file and the memory untouched
# (tried again on the next start). Only the totems entries of the islands that hold such a record are rewritten.
M(st, r"""
public static String snapshot(String k) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    java.nio.file.Path h = DIR.resolve("history");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    byte[] src = java.nio.file.Files.readAllBytes(f);
    String name = k + ".pre-0.4.properties";
    java.nio.file.Path t = h.resolve(name);
    if (java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0]) && !java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) {
      name = k + ".pre-0.4." + System.currentTimeMillis() + ".properties";   // an older snapshot stays as it is
      t = h.resolve(name);
    }
    if (!java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) {
      java.nio.file.Path tmp = h.resolve(name + ".tmp");
      java.nio.file.Files.write(tmp, src, new java.nio.file.OpenOption[0]);
      moveInto(tmp, t);
    }
    if (!java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) { @PKG@.ShCfg.warnOnce("snapcheck:" + k, "the forms migration snapshot of " + k + " does not match the file - not migrated"); return null; }
    return "shards/history/" + name;
  } catch (Throwable x) {
    @PKG@.ShCfg.warnOnce("snap:" + k, "the forms migration of " + k + " is waiting: its History snapshot could not be written (" + x + ")");
    return null;
  }
}""")
st.getDeclaredMethod("migrate").setBody(jv(r"""{
  String k = $1;
  java.util.Properties p = $2;
  if (p == null || k == null || "1".equals(p.getProperty("forms"))) return;
  LOCK.lock();
  try {
    if ("1".equals(p.getProperty("forms"))) return;
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    StringBuilder ch = new StringBuilder();
    int n = 0;
    for (int kd = 0; kd < @PKG@.ShKind.N; kd++) {
      for (int s = 0; s < 6; s++) {
        String[] e = @PKG@.ShTotem.entries(kd, p, s);
        boolean any = false;
        for (int i = 0; i < e.length; i++) {
          String[] f = @PKG@.ShTotem.parse(e[i]);
          int ti = @PKG@.ShTotem.idx(f[0]);
          if (ti < 0 || !@PKG@.ShTotem.HAND[ti] || @PKG@.ShTotem.tierOf(f[1]) != 1 || @PKG@.ShTotem.gf(f)) continue;
          f[6] = "gf";
          e[i] = @PKG@.ShTotem.fmt(f);
          any = true;
          n++;
          ch.append(' ').append(@PKG@.ShKind.KEYS[kd]).append(".i").append(s).append(" pad ").append(i + 1).append(' ').append(e[i]);
        }
        if (any) @PKG@.ShTotem.setEntries(kd, p, s, e);
      }
    }
    if (n == 0) { p.setProperty("forms", "1"); return; }
    String snap = snapshot(k);
    if (snap == null) { p.clear(); p.putAll(old); return; }
    p.setProperty("forms", "1");
    String err = save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warnOnce("migsave:" + k, "the forms migration of " + k + " is waiting (the file could not be saved: " + err + ")"); return; }
    MIGRATED.incrementAndGet();
    log("totem forms migration (SkyyShards @VERSION@) " + k + ": " + n + " placed tier-I Rain / Fertilizer / Sun totem(s) kept as poles (gf=1, spec 9.8):" + ch.toString() + " - History snapshot " + snap + " - Undo (with SkyyShards 0.3.2 back in place, server stopped): remove the ':gf' endings and the forms=1 line from shards/" + k + ".properties (copying " + snap + " back over it is right ONLY before any play on 0.4 - it puts back the whole old file)");
    @PKG@.ShCfg.info("totem forms migration: " + k + " - " + n + " old tier-I Rain / Fertilizer / Sun totem(s) kept as poles (collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}"""))

# ================= ShMath: lazy production (spec 9.2; no ticking) - pure, any thread, under the ShStore lock when it changes a profile =================
''')

# ================================================================================================================== ShGeo: the bench on every hub
rep('''F(geo, 'public static final String[] IDS = new String[] { %s };' % ", ".join([jlit(x) for x in GEO_IDS] + [jlit(x) for x in TOTEM_BLOCK]))''',
    '''F(geo, 'public static final String[] IDS = new String[] { %s };' % ", ".join([jlit(x) for x in GEO_IDS] + [jlit(x) for x in TOTEM_BLOCK] + [jlit(x) for x in BENCH_BLOCKS]))   # 0.4: + the benches''')
rep('''F(geo, "public static final int TOTEM = %d;" % len(GEO_IDS))
''', '''F(geo, "public static final int TOTEM = %d;" % len(GEO_IDS))
F(geo, "public static final int BENCH = %d;" % (len(GEO_IDS) + NT))     # 0.4: IDS[BENCH + kind] = that shard's Totem Bench
F(geo, "public static final int BX = %d;" % BENCH_POS[0])
F(geo, "public static final int BZ = %d;" % BENCH_POS[1])
''')
rep('''    if (ax + az <= h - 3) add(out, x, Y - 3, z, STONE);
  }
  add(out, ox, Y + 1, OZ - 3, STANDS[kd]);
}""")''', '''    if (ax + az <= h - 3) add(out, x, Y - 3, z, STONE);
  }
  add(out, ox, Y + 1, OZ - 3, STANDS[kd]);
  add(out, ox + BX, Y + 1, OZ + BZ, BENCH + kd);   // 0.4 (spec 9.7): the shard's fixed Totem Bench - the repair (Enter / Grow) puts it back
}""")''')
rep('''    if (b[3] >= @PKG@.ShGeo.TOTEM) { if (cur.indexOf(id) < 0) n += put(w, b[0], b[1], b[2], id); continue; }   // 0.2: a totem (any rotation state)
    if (!id.equals(cur)) n += put(w, b[0], b[1], b[2], id);''', '''    if (b[3] >= @PKG@.ShGeo.TOTEM) { if (cur.indexOf(id) < 0) n += put(w, b[0], b[1], b[2], id); continue; }   // 0.2: a totem (any rotation state); 0.4: a Totem Bench too
    if (b[3] == @PKG@.ShGeo.TILL && cur.indexOf(id) >= 0) continue;   // 0.4: watered / fertilized tilled soil (a state of it) is kept
    if (!id.equals(cur)) n += put(w, b[0], b[1], b[2], id);''')

# ================================================================================================================== ShGate: the bench may be used
rep('''  if (a.equals("use")) return Boolean.valueOf(crop(block) || (block != null && (block.indexOf("Skyy_Shard_") >= 0 || block.indexOf("Skyy_TotemBlock_") >= 0)));   // 0.2: a totem opens its page; 0.3: every shard stand''',
    '''  if (a.equals("use")) return Boolean.valueOf(crop(block) || (block != null && (block.indexOf("Skyy_Shard_") >= 0 || block.indexOf("Skyy_TotemBlock_") >= 0 || block.indexOf("Skyy_TotemBench_") >= 0)));   // 0.2: a totem opens its page; 0.3: every shard stand; 0.4: the Totem Bench''')
# ================================================================================================================== ShCore: forms, bench, tier-up
rep('''  if (!@PKG@.ShTotem.accepts(ti, kd)) return "-The " + @PKG@.ShTotem.NAMES[ti] + " works in the " + @PKG@.ShTotem.kindsOf(ti) + " Shard - not in this one.";
  String docUid = @PKG@.ShTotem.dstr(d, "uid");''', '''  if (!@PKG@.ShTotem.accepts(ti, kd)) return "-The " + @PKG@.ShTotem.NAMES[ti] + " works in the " + @PKG@.ShTotem.kindsOf(ti) + " Shard - not in this one.";
  if (@PKG@.ShTotem.handHeld(f)) return "-" + @PKG@.ShTotem.name(f) + " is hand-held: right-click it anywhere to use it. Tier it up to Totem Pole II at the Totem Bench first to place it.";   // 0.4 (spec 9.3.1)
  String docUid = @PKG@.ShTotem.dstr(d, "uid");''')
rep('''# Upgrade = the Anvil (SkyyGear). gear:fn:anvil:open (UUID -> Boolean, the player's world thread) when SkyyGear publishes it
M(core, r"""
public static String upgrade(java.util.UUID u) {
  try {
    java.util.function.Function g = @PKG@.ShPay.f("gear:fn:anvil:open");
    if (g != null && Boolean.TRUE.equals(g.apply(u))) return "+Opening the Anvil - pick the totem in your inventory there.";
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("anvil", "gear:fn:anvil:open failed: " + t); }
  return "=Totems tier up on the Anvil (Upgrade) - that comes with the next SkyyGear update. Pick the totem up to take it there.";
}""")''', '''# 0.4 (spec 9.7, question 19 [at the bench]): totems tier up at their shard's Totem Bench (the totem page's Tier up button says where)
M(core, r"""
public static String upgrade(java.util.UUID u, int kd) {
  String nm = @PKG@.ShKind.ok(kd) ? @PKG@.ShKind.NAMES[kd] : "shard's";
  return "=Totems tier up at the " + nm + " Totem Bench on this shard's hub island (next to the stand). Pick the totem up, then use the bench's Tier up tab.";
}""")''')
rep('''M(core, "public static int[] nearest(java.util.Properties p, double x, double z) { return nearest(p, FK, x, z); }")
''', '''M(core, "public static int[] nearest(java.util.Properties p, double x, double z) { return nearest(p, FK, x, z); }")

# ---- 0.4 THE TOTEM BENCH (spec 9.7). Data per shard: <kind>.bench (1-4, missing = Bench I, free with the shard), <kind>.benchTo +
# <kind>.benchUpAt (ms) while an upgrade runs. benchTier is pure: a finished timer counts at once (also while offline / unloaded); the
# next purchase folds it into <kind>.bench.
M(core, r"""
public static int benchTier(int kd, java.util.Properties p, long now) {
  int t = @PKG@.ShStore.intv(p, @PKG@.ShMath.kk(kd, "bench"), 1, 1, 4);
  long at = @PKG@.ShStore.lng(p, @PKG@.ShMath.kk(kd, "benchUpAt"), 0L);
  if (at > 0L && now >= at) { int to = @PKG@.ShStore.intv(p, @PKG@.ShMath.kk(kd, "benchTo"), t, 1, 4); if (to > t) t = to; }
  return t;
}""")
M(core, "public static int benchTo(int kd, java.util.Properties p) { return @PKG@.ShStore.intv(p, @PKG@.ShMath.kk(kd, \\"benchTo\\"), 1, 1, 4); }")
M(core, "public static long benchAt(int kd, java.util.Properties p) { return @PKG@.ShStore.lng(p, @PKG@.ShMath.kk(kd, \\"benchUpAt\\"), 0L); }")
M(core, r"""
public static String secs(long s) {
  if (s < 0L) s = 0L;
  return @PKG@.ShCfg.num(s) + " s" + (s >= 120L ? " (" + @PKG@.ShMath.fmtMs(s * 1000L) + ")" : "");
}""")
# may recipe ri be crafted at shard kd's bench of tier `tier`? null = yes (the bench gates only; craftGate keeps the rebirth / Soul Cage
# rules): that shard's totems by bench.unlock.<kind>.<type>, the 6 modifiers by bench.unlock.mod.<mod>, an extra shard at any bench
M(core, r"""
public static String benchGate(int kd, int tier, int ri) {
  if (ri < 0 || ri >= @PKG@.ShCfg.CRAFT_ID.length) return "Pick a recipe.";
  String id = @PKG@.ShCfg.CRAFT_ID[ri];
  int ti = @PKG@.ShTotem.itemIdx(id);
  int need = 1;
  if (ti >= 0) {
    if (!@PKG@.ShTotem.accepts(ti, kd)) return "The " + @PKG@.ShTotem.NAMES[ti] + " is made at the " + @PKG@.ShTotem.kindsOf(ti) + " Totem Bench.";
    need = @PKG@.ShCfg.benchUnlock(kd, ti);
  } else {
    int mi = @PKG@.ShTotem.modItemIdx(id);
    if (mi < 0) return null;   // an extra shard (rebirth 2): any Totem Bench you own (spec 9.7, question 23)
    need = @PKG@.ShCfg.modUnlock(mi);
  }
  if (need < 1) need = 1;
  if (need > 4) need = 4;
  if (need > tier) return "Needs Bench " + @PKG@.ShTotem.ROMAN[need - 1] + " (this bench: " + @PKG@.ShTotem.ROMAN[(tier < 1 ? 1 : tier) - 1] + ").";
  return null;
}""")
# the common start of a bench click: the shard OWNER only (co-op: view only), a readable file, a shard of that kind; null = go on (p in out[0])
M(core, r"""
public static String benchStart(java.util.UUID u, String k, int kd, @IC@[] cs, Object[] out) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  if (busy(u)) return "-Your profile is still loading - try again in a moment.";
  if (k == null || !@PKG@.ShKind.ok(kd)) return "-This bench belongs to no shard.";
  if (!k.equals(@PKG@.ShCfg.pkey(u))) return "-Only the island owner uses the Totem Bench - co-op members can look.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  boolean own;
  @PKG@.ShStore.LOCK.lock(); try { own = @PKG@.ShMath.owned(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (!own) return "-No " + @PKG@.ShKind.NAMES[kd] + " Shard yet - it comes from the hub quest line.";
  out[0] = p;
  return null;
}""")
# take every input (counted; all back when one falls short) / give them back (the kept stacks with data exactly as they were)
M(core, r"""
public static long[] takeAll(@IC@[] cs, String[] ids, long[] q, java.util.ArrayList kept) {
  long[] took = new long[ids.length];
  for (int i = 0; i < ids.length; i++) {
    took[i] = @PKG@.ShInv.take2(cs, ids[i], q[i], kept);
    if (took[i] < q[i]) {
      for (int j = 0; j <= i; j++) if (took[j] > 0L) @PKG@.ShInv.giveBack(cs, ids[j], took[j], kept);
      return null;
    }
  }
  return took;
}""")
M(core, r"""
public static long refundAll(@IC@[] cs, String[] ids, long[] took, java.util.ArrayList kept) {
  long n = 0L;
  if (took == null) return 0L;
  for (int i = 0; i < ids.length; i++) if (took[i] > 0L) n += @PKG@.ShInv.giveBack(cs, ids[i], took[i], kept);
  return n;
}""")
# craft recipe ri at shard kd's bench (the 0.2-0.3 craft, gated by the bench: owner, shard owned, bench tier)
M(core, r"""
public static String craftAt(java.util.UUID u, String k, int kd, int ri, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = benchStart(u, k, kd, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  int tier;
  @PKG@.ShStore.LOCK.lock(); try { tier = benchTier(kd, p, now()); } finally { @PKG@.ShStore.LOCK.unlock(); }
  String g = benchGate(kd, tier, ri);
  if (g != null) return "-" + g;
  return craft(u, ri, cs);
}""")
# TIER UP the totem in inventory section ci, slot si at shard kd's bench (spec 9.7, question 19 / 20). uid + seen = what the page showed
# (they travel in the click itself, so a second click from the old page can never tier up twice). Order: every check, the cost items
# taken (counted; refunded on any failure), then the totem in its slot SWAPPED for the same document one tier up (same uid, modifiers,
# booster left; Totem I -> Totem Pole II; gf cleared) - read back; a slot that changed meanwhile = the cost back, nothing else moved.
M(core, r"""
public static String tierUp(java.util.UUID u, String k, int kd, int ci, int si, String uid, int seen, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = benchStart(u, k, kd, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  if (ci < 0 || ci >= cs.length || cs[ci] == null) return "-That totem is not in your inventory any more.";
  @IS@ it = cs[ci].getItemStack((short) si);
  String id = it == null || it.isEmpty() ? null : it.getItemId();
  int ti = @PKG@.ShTotem.itemIdx(id);
  if (ti < 0) return "-That totem is not in your inventory any more.";
  long now = now();
  @BD@ d = @PKG@.ShTotem.docOf(it);
  String docUid = @PKG@.ShTotem.dstr(d, "uid");
  if (!docUid.equals(uid == null ? "" : uid)) return "-That totem moved in your inventory - look again.";
  String[] f = @PKG@.ShTotem.fromDoc(d, id, now);
  if (f == null) return "-That totem's document does not match its item - ask an admin (totem.log).";
  int t = @PKG@.ShTotem.tierOf(f[1]);
  if (t != seen) return "=That totem is " + @PKG@.ShTotem.name(f) + " now - the page is up to date.";
  if (!@PKG@.ShTotem.accepts(ti, kd)) return "-The " + @PKG@.ShTotem.NAMES[ti] + " tiers up at the " + @PKG@.ShTotem.kindsOf(ti) + " Totem Bench.";
  if (t >= 5) return "=" + @PKG@.ShTotem.name(f) + " is at the highest tier.";
  int bt;
  @PKG@.ShStore.LOCK.lock(); try { bt = benchTier(kd, p, now); } finally { @PKG@.ShStore.LOCK.unlock(); }
  int cap = @PKG@.ShCfg.benchCap(bt);
  if (t + 1 > cap) return "-Bench " + @PKG@.ShTotem.ROMAN[bt - 1] + " tiers totems up to " + @PKG@.ShTotem.LADDER[cap - 1] + " - upgrade the bench first (Bench tab).";
  String c = @PKG@.ShTotem.costAt(kd, id, d == null ? null : d.toJson());   // the cost in THIS shard's material
  if (c.startsWith("err:")) return "-The tier-up cost is broken (" + c.substring(4) + ") - ask an admin (Server Setup -> Shards -> Tier-up costs).";
  Object[] rc = recipe(c);
  if (rc == null) return "-The tier-up cost could not be read - ask an admin.";
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  for (int i = 0; i < ids.length; i++) {
    long have = @PKG@.ShInv.count(cs, ids[i]);
    if (have < q[i]) return "-You need " + @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]) + " (you have " + @PKG@.ShCfg.num(have) + ").";
  }
  String[] nf = new String[] { f[0], String.valueOf(t + 1), f[2], f[3], f[4], f[5].length() == 0 ? @PKG@.ShTotem.newUid() : f[5], "" };
  @IS@ ns = @PKG@.ShTotem.stack(nf, now);
  if (ns == null) return "-That totem could not be tiered up - ask an admin (totem.log).";
  java.util.ArrayList kept = new java.util.ArrayList();
  long[] took = takeAll(cs, ids, q, kept);
  if (took == null) return "-The cost could not be taken - everything is back.";
  // the SAME slot, swapped in one step (ItemContainer.replaceItemStackInSlot only swaps while the slot still holds exactly `it`): no
  // free slot needed, never two totems with one uid, never none
  try { cs[ci].replaceItemStackInSlot((short) si, it, ns); } catch (Throwable x) { @PKG@.ShCfg.warnOnce("tierswap", "a totem tier-up swap failed (logged once): " + x); }
  @IS@ now2 = cs[ci].getItemStack((short) si);
  @BD@ d2 = @PKG@.ShTotem.docOf(now2);
  boolean done = now2 != null && !now2.isEmpty() && id.equals(now2.getItemId()) && nf[5].equals(@PKG@.ShTotem.dstr(d2, "uid")) && @PKG@.ShTotem.dlong(d2, "tier") == (long) (t + 1);
  if (!done) {
    long r = refundAll(cs, ids, took, kept);
    tlog(u + " " + k + " tierup " + @PKG@.ShTotem.fmt(f) + " NOT SWAPPED (the slot changed) - cost back " + r);
    return "-That totem moved in your inventory - your items are back.";
  }
  tlog(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " tierup " + @PKG@.ShTotem.fmt(f) + " -> " + @PKG@.ShTotem.fmt(nf) + " paid " + c + @PKG@.ShInv.keptText(kept));
  return "+" + @PKG@.ShTotem.name(f) + " is now " + @PKG@.ShTotem.name(nf) + ((t == 1 && @PKG@.ShTotem.HAND[ti]) ? " - place it from the shard menu (Totems tab)." : ".");
}""")
# UPGRADE THE BENCH one tier (spec 9.7): the collection tier, the items (counted), the coins last (items back when they fail), then the
# timer written (a refused save undoes it and refunds both). bench.upN.sec 0 = at once. No pay-to-skip.
M(core, r"""
public static String benchUp(java.util.UUID u, String k, int kd, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = benchStart(u, k, kd, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  long now = now();
  int tier; long at; int to;
  @PKG@.ShStore.LOCK.lock(); try { tier = benchTier(kd, p, now); at = benchAt(kd, p); to = benchTo(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (at > now) return "=The bench is upgrading to Bench " + @PKG@.ShTotem.ROMAN[to - 1] + " - " + secs((at - now + 999L) / 1000L) + " left.";
  if (tier >= 4) return "=This Totem Bench is fully upgraded (Bench IV).";
  int nt = tier + 1;
  int need = @PKG@.ShCfg.BENCH_NEED[nt];
  int ct = @PKG@.ShPay.collTier(u, @PKG@.ShKind.COLL[kd]);
  if (need > 0 && ct < need) return "-Bench " + @PKG@.ShTotem.ROMAN[nt - 1] + " needs " + @PKG@.ShKind.CNAME[kd] + " collection " + need + " (you: " + (ct < 0 ? "?" : String.valueOf(ct)) + ").";
  String txt = @PKG@.ShCfg.benchItems(nt, kd).trim();
  Object[] rc = txt.length() == 0 ? new Object[] { new String[0], new long[0], Long.valueOf(0L) } : recipe(txt);
  if (rc == null) return "-The bench upgrade cost setting is broken - ask an admin (Server Setup -> Shards -> Totem Bench).";
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  long coins = @PKG@.ShCfg.BENCH_COINS[nt];
  for (int i = 0; i < ids.length; i++) {
    long have = @PKG@.ShInv.count(cs, ids[i]);
    if (have < q[i]) return "-You need " + @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]) + " (you have " + @PKG@.ShCfg.num(have) + ").";
  }
  long purse = @PKG@.ShPay.coins(u);
  if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
  java.util.ArrayList kept = new java.util.ArrayList();
  long[] took = takeAll(cs, ids, q, kept);
  if (took == null) return "-The items could not be taken - nothing was bought.";
  if (!@PKG@.ShPay.takeCoins(u, coins)) { refundAll(cs, ids, took, kept); return "-The coins could not be taken - your items are back."; }
  int sec = @PKG@.ShCfg.BENCH_SEC[nt];
  String e;
  @PKG@.ShStore.LOCK.lock(); try {
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    p.setProperty(@PKG@.ShMath.kk(kd, "bench"), String.valueOf(sec <= 0 ? nt : tier));   // a finished earlier upgrade is folded in here
    if (sec <= 0) { p.remove(@PKG@.ShMath.kk(kd, "benchTo")); p.remove(@PKG@.ShMath.kk(kd, "benchUpAt")); }
    else { p.setProperty(@PKG@.ShMath.kk(kd, "benchTo"), String.valueOf(nt)); p.setProperty(@PKG@.ShMath.kk(kd, "benchUpAt"), String.valueOf(now + 1000L * (long) sec)); }
    e = @PKG@.ShStore.save(k, p);
    if (e != null) { p.clear(); p.putAll(old); }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (e != null) {
    long ri = refundAll(cs, ids, took, kept);
    boolean rcn = @PKG@.ShPay.addCoins(u, coins);
    tlog(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " bench " + tier + " -> " + nt + " SAVE FAILED " + e + " - refund items " + ri + ", coins " + (rcn ? coins : 0L) + " of " + coins);
    return "-The upgrade could not be saved - your items" + (rcn ? " and coins are" : " are") + " back." + (rcn ? "" : " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).");
  }
  tlog(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " bench " + tier + " -> " + nt + " in " + sec + " s, paid " + coins + " coins + " + txt + @PKG@.ShInv.keptText(kept));
  if (sec <= 0) return "+Bench " + @PKG@.ShTotem.ROMAN[nt - 1] + " is ready.";
  return "+Bench " + @PKG@.ShTotem.ROMAN[nt - 1] + " in " + secs((long) sec) + " - the bench keeps working at Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + " meanwhile.";
}""")
''')
# ================================================================================================================== hand-held totems
HAND_JAVA = r'''
# ================= 0.4 HAND-HELD TOTEMS (spec 9.3.1, questions 15-17: Rain / Fertilizer / Sun, cooldown now - Mana later, a LOCAL effect) =================
# ShSoil (world thread): the vanilla watering can / fertilizer on ONE tilled soil block (the TilledSoilBlock block component - the
# UseWateringCanInteraction / FertilizeSoilInteraction pattern of the 0.7 server: ensureBlockEntity, setWateredUntil / setFertilized,
# markBlockNeedsSaving, setTicking + scheduleTick so the farming tick redraws it and the crop above grows with the vanilla modifiers
# Water x2.5 / Fertilizer x2). area() = every soil column within r blocks around (x, z), y from the feet down 3 / up 1.
soil = mk("ShSoil")
F(soil, "public static volatile java.util.function.Function TEST = null;")   # harness: (Object[]{x, y, z, r, wet?, fert?}) -> Integer tiles
F(soil, "public static final java.util.concurrent.atomic.AtomicLong TILES = new java.util.concurrent.atomic.AtomicLong();")
M(soil, "public static java.time.Instant later(java.time.Instant cur, java.time.Instant wet) { return cur != null && wet != null && cur.isAfter(wet) ? cur : wet; }")   # fix (critic shards04)
M(soil, r"""
public static boolean one(@WLD@ w, int x, int y, int z, java.time.Instant wet, boolean fert) {
  try {
    @CST@ cs = w.getChunkStore();
    @ST@ store = cs.getStore();
    @REF@ sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return false;
    @BSEC@ bs = (@BSEC@) store.getComponent(sr, @BSEC@.getComponentType());
    com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection bcs = (com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection) store.getComponent(sr, com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection.getComponentType());
    if (bs == null || bcs == null) return false;
    int idx = @CHU@.indexBlock(x, y, z);
    @BTY@ bt = (@BTY@) @BTY@.getAssetMap().getAsset(bs.get(idx));
    if (bt == null || !com.hypixel.hytale.server.core.modules.block.BlockEntity.declaresComponent(bt, com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock.getComponentType())) return false;
    @REF@ br = bcs.getBlockReference(idx);
    if (br == null || !br.isValid()) br = com.hypixel.hytale.server.core.modules.block.BlockEntity.ensureBlockEntity((@CA@) store, sr, bcs, x, y, z, bt, bs.getFiller(idx));
    if (br == null || !br.isValid()) return false;
    com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock ts = (com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock) store.getComponent(br, com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock.getComponentType());
    if (ts == null) return false;
    if (wet != null) ts.setWateredUntil(later(ts.getWateredUntil(), wet));   // fix (critic shards04): a longer watering stays
    if (fert) ts.setFertilized(true);
    bcs.markBlockNeedsSaving(idx);
    bs.setTicking(x, y, z, true);
    if (wet != null) bs.scheduleTick(idx, wet);
    if ((y & 31) != 31) bs.setTicking(x, y + 1, z, true);   // the crop above (same section) ticks again
    return true;
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("soil", "a hand-held totem could not change the soil (logged once): " + t); return false; }
}""")
M(soil, r"""
public static int area(@WLD@ w, double px, double py, double pz, int r, java.time.Instant wet, boolean fert) {
  java.util.function.Function tf = TEST;
  if (tf != null) {
    Object o = tf.apply(new Object[] { Double.valueOf(px), Double.valueOf(py), Double.valueOf(pz), Integer.valueOf(r), Boolean.valueOf(wet != null), Boolean.valueOf(fert) });
    return o instanceof Number ? ((Number) o).intValue() : 0;
  }
  if (w == null || r < 0) return 0;
  int cx = (int) Math.floor(px); int fy = (int) Math.floor(py); int cz = (int) Math.floor(pz);
  int n = 0;
  for (int dx = -r; dx <= r; dx++) for (int dz = -r; dz <= r; dz++) {
    if (dx * dx + dz * dz > r * r) continue;
    for (int y = fy + 1; y >= fy - 3; y--) {
      if (one(w, cx + dx, y, cz + dz, wet, fert)) { n++; break; }
    }
  }
  TILES.addAndGet((long) n);
  return n;
}""")
# the splash shower of a hand-held Rain (world thread): 8 splashes at random spots of the circle, once a second while it lasts (ShTick)
rain = mk("ShRain", None, ("java.lang.Runnable",))
F(rain, "public @WLD@ w;")
F(rain, "public double[] c;")
F(rain, "public String sys;")
F(rain, "public static final java.util.concurrent.atomic.AtomicLong DRAWS = new java.util.concurrent.atomic.AtomicLong();")
C(rain, "public ShRain(@WLD@ w, double[] c, String sys) { this.w = w; this.c = c; this.sys = sys; }")
M(rain, r"""
public void run() {
  try {
    java.util.Random rnd = new java.util.Random();
    int n = this.c[3] <= 0.0 ? 1 : 8;
    for (int i = 0; i < n; i++) {
      double a = rnd.nextDouble() * Math.PI * 2.0;
      double d = Math.sqrt(rnd.nextDouble()) * this.c[3];
      @PTU@.spawnParticleEffect(this.sys, (@V3DC@) new @V3D@(this.c[0] + d * Math.cos(a), this.c[1], this.c[2] + d * Math.sin(a)), (@CA@) this.w.getEntityStore().getStore());
    }
    DRAWS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("rain", "the hand-held totem particles failed (logged once): " + t); }
}""")
# ShHand = the page supplier of HAND_PAGE_ID (every totem ITEM: Interactions Secondary -> OpenCustomUI): it runs on the player's world
# thread, uses a hand-held Totem I (or says where a pole goes) and returns NO page (OpenCustomUIInteraction opens nothing for null).
hand = mk("ShHand", None, ("java.util.function.Function",))
F(hand, "public static final java.util.concurrent.ConcurrentHashMap COOL = new java.util.concurrent.ConcurrentHashMap();")    # uuid|type -> Long ready at
F(hand, "public static final java.util.concurrent.ConcurrentHashMap SHOWER = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> Object[]{ world, double[]{x,y,z,r,until}, particle }
F(hand, "public static final java.util.concurrent.atomic.AtomicLong USES = new java.util.concurrent.atomic.AtomicLong();")
F(hand, "public static volatile java.util.function.Function DAY_TEST = null;")     # harness: the daylight check
F(hand, "public static final java.util.concurrent.ConcurrentHashMap SAID = new java.util.concurrent.ConcurrentHashMap();")    # fix: uuid -> Object[]{ line, Long at }
F(hand, "public static volatile double RATIO_TEST = -1.0;")    # harness: game seconds per real second (< 0 = the world's)
F(hand, "public static final String[] PART = new String[] { %s };" % ", ".join(jlit(HAND_PARTICLES.get(t[0], "")) for t in TOTEMS))
C(hand, "public ShHand() { }")
M(hand, r"""
public static long left(String key, long now) {
  Object o = COOL.get(key);
  if (!(o instanceof Long)) return 0L;
  long l = ((Long) o).longValue() - now;
  return l > 0L ? l : 0L;
}""")
# the world's clock (game time; null = unknown) and daylight (DAY_TEST = the harness)
M(hand, r"""
public static com.hypixel.hytale.server.core.modules.time.WorldTimeResource clock(@WLD@ w) {
  try {
    if (w == null) return null;
    Object r = w.getEntityStore().getStore().getResource(com.hypixel.hytale.server.core.modules.time.WorldTimeResource.getResourceType());
    return r instanceof com.hypixel.hytale.server.core.modules.time.WorldTimeResource ? (com.hypixel.hytale.server.core.modules.time.WorldTimeResource) r : null;
  } catch (Throwable t) { return null; }
}""")
M(hand, r"""
public static boolean day(@WLD@ w) {
  java.util.function.Function dt = DAY_TEST;
  if (dt != null) return Boolean.TRUE.equals(dt.apply(w));
  com.hypixel.hytale.server.core.modules.time.WorldTimeResource c = clock(w);
  return c == null || c.getSunlightFactor() >= 0.25;
}""")
# fix (critic shards04): the wet time is REAL seconds - game seconds per real second = 86400 / (the world's day + night length in seconds)
# (WorldTimeResource.getSecondsPerTick); unknown = 1 (short, never a game day by mistake)
M(hand, r"""
public static double ratio(@WLD@ w) {
  if (RATIO_TEST >= 0.0) return RATIO_TEST;
  try {
    double r = w == null ? 1.0 : com.hypixel.hytale.server.core.modules.time.WorldTimeResource.getSecondsPerTick(w);
    return r > 0.0 && r < 100000.0 ? r : 1.0;
  } catch (Throwable t) { return 1.0; }
}""")
M(hand, r"""
public static long gameSec(@WLD@ w, long realSec) {
  if (realSec <= 0L) return 0L;
  return (long) Math.ceil((double) realSec * ratio(w));
}""")
M(hand, r"""
public static java.time.Instant wetUntil(@WLD@ w, long sec) {
  com.hypixel.hytale.server.core.modules.time.WorldTimeResource c = clock(w);
  java.time.Instant t = c == null ? null : c.getGameTime();
  if (t == null) t = java.time.Instant.now();
  return t.plusSeconds(gameSec(w, sec));
}""")
# fix (critic shards04): the soil of an island / shard you do not belong to is not yours to change (null = go on)
M(hand, r"""
public static String guard(java.util.UUID u, String wn) {
  if (wn == null) return null;
  String owner = @PKG@.ShRole.islandOwner(wn);
  if (owner == null) owner = @PKG@.ShWorlds.ownerOf(wn);
  if (owner == null || @PKG@.ShRole.mayBeIn(u, owner)) return null;
  return "-You can only use a hand-held totem on islands and shards you belong to.";
}""")
# fix (critic shards04): drop cooldowns that are over (never a clear - that would hand everyone a free use)
M(hand, r"""
public static void prune(long now) {
  java.util.Iterator it = COOL.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (!(v instanceof Long) || ((Long) v).longValue() <= now) it.remove();
  }
  java.util.Iterator is = SAID.entrySet().iterator();
  while (is.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) is.next();
    Object[] v = (Object[]) e.getValue();
    if (((Long) v[1]).longValue() + 2000L <= now) is.remove();
  }
}""")
# fix (critic shards04): the same refusal line to the same player within 2 s is not repeated (a held button / fast clicks)
M(hand, r"""
public static boolean quiet(java.util.UUID u, String line, long now) {
  if (u == null || line == null) return false;
  Object o = SAID.get(u);
  if (o instanceof Object[]) {
    Object[] v = (Object[]) o;
    if (line.equals(v[0]) && now - ((Long) v[1]).longValue() < 2000L) return true;
  }
  SAID.put(u, new Object[] { line, Long.valueOf(now) });
  if (SAID.size() > 4096) prune(now);
  return false;
}""")
# use the totem fields f (the item in hand) at (x, y, z) of world w for player u. "+" used, "-" refused, "=" a pole / nothing to do
M(hand, r"""
public static String act(java.util.UUID u, String[] f, @WLD@ w, double x, double y, double z, long now) {
  int ti = @PKG@.ShTotem.idx(f[0]);
  if (ti < 0) return "";
  String nm = @PKG@.ShTotem.name(f);
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (!@PKG@.ShTotem.usable(f)) return "=" + nm + " is a totem pole: place it from your " + @PKG@.ShTotem.kindsOf(ti) + " Shard menu (right-click the shard on your island - Totems tab).";
  String no = w == null ? null : guard(u, w.getName());   // fix (critic shards04)
  if (no != null) return no;
  String key = String.valueOf(u) + "|" + f[0];
  long l = left(key, now);
  if (l > 0L) return "-" + nm + " is resting - " + ((l + 999L) / 1000L) + " s left.";
  boolean sun = "sun_blessing".equals(f[0]);
  boolean rain = "rain".equals(f[0]);
  boolean fert = "fertilizer".equals(f[0]);   // fix (critic shards04): the Sun only waters, for its own (shorter than a day) time
  if (sun && !day(w)) return "-The Blessing of the Sun works by day only.";
  int r = sun ? @PKG@.ShCfg.HAND_SUN_R : (rain ? @PKG@.ShCfg.HAND_RAIN_R : @PKG@.ShCfg.HAND_FERT_R);
  java.time.Instant wetAt = null;
  if (rain) wetAt = wetUntil(w, (long) @PKG@.ShCfg.HAND_RAIN_WET);
  if (sun) wetAt = wetUntil(w, (long) @PKG@.ShCfg.HAND_SUN_WET);
  int n = @PKG@.ShSoil.area(w, x, y, z, r, wetAt, fert);
  String sys = @PKG@.ShHand.PART[ti];
  if (n > 0) {
    COOL.put(key, Long.valueOf(now + 1000L * (long) @PKG@.ShCfg.HAND_CD));
    if (COOL.size() > 4096) prune(now);   // fix (critic shards04): never COOL.clear()
    USES.incrementAndGet();
  }
  if (w != null && sys.length() > 0 && (n > 0 || rain)) {   // fix (critic shards04): the Rain's shower falls anywhere, soil or not
    long until = rain ? now + 1000L * (long) @PKG@.ShCfg.HAND_RAIN_SHOW : now + 1500L;
    SHOWER.put(u, new Object[] { w.getName(), new double[] { x, y + 0.2, z, (double) r, (double) until }, sys });
    try { new @PKG@.ShRain(w, new double[] { x, y + 0.2, z, (double) r, 0.0 }, sys).run(); } catch (Throwable t) { }
  }
  if (n <= 0) {
    if (rain) return "=Rain falls around you - no tilled soil within " + r + " blocks to wet (no cooldown).";
    if (fert) return "=No tilled soil within " + r + " blocks - the hand-held Fertilizer works on tilled soil (crops) for now; saplings come later (no cooldown).";
    return "=No tilled soil within " + r + " blocks - nothing happened (no cooldown).";
  }
  String what = sun ? "the sun warms " + n + " soil tiles (wet for " + @PKG@.ShCfg.HAND_SUN_WET + " s)" : (rain ? "rain wets " + n + " soil tiles for " + @PKG@.ShCfg.HAND_RAIN_WET + " s" : n + " soil tiles fertilized until harvest");
  return "+" + nm + ": " + what + " within " + r + " blocks. Ready again in " + @PKG@.ShCfg.HAND_CD + " s.";
}""")
M(hand, r"""
public static String use(@PR@ pr) {
  @REF@ ref = pr.getReference();
  if (ref == null || !ref.isValid()) return "";
  @ST@ st = ref.getStore();
  @PLA@ pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  @INV@ inv = pl == null ? null : pl.getInventory();
  @IS@ it = inv == null ? null : inv.getItemInHand();
  String id = it == null || it.isEmpty() ? null : it.getItemId();
  int ti = @PKG@.ShTotem.itemIdx(id);
  if (ti < 0) return "";
  long now = @PKG@.ShCore.now();
  String[] f = @PKG@.ShTotem.fromDoc(@PKG@.ShTotem.docOf(it), id, now);
  if (f == null) return "-That totem's document does not match its item - ask an admin (totem.log).";
  @WLD@ w = null;
  try { Object ext = st.getExternalData(); if (ext instanceof @EST@) w = ((@EST@) ext).getWorld(); } catch (Throwable t) { w = null; }
  @TCO@ tc = (@TCO@) st.getComponent(ref, @TCO@.getComponentType());
  if (w == null || tc == null) return "";
  org.joml.Vector3d v = tc.getPosition();
  return act(pr.getUuid(), f, w, v.x, v.y, v.z, now);
}""")
M(hand, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof @PR@)) return null;
    @PR@ pr = (@PR@) o;
    String r = use(pr);
    if (r != null && r.length() > 0 && r.charAt(0) != '+' && quiet(pr.getUuid(), r, @PKG@.ShCore.now())) r = null;   // fix (critic shards04)
    if (r != null && r.length() > 0) {
      char c = r.charAt(0);
      @PKG@.ShSay.to(pr, "[Shards] " + ((c == '+' || c == '-' || c == '=') ? r.substring(1) : r), c == '+' ? "@GOOD@" : (c == '-' ? "@BAD@" : "@INFO@"));
    }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("hand", "a hand-held totem use failed (logged once): " + t); }
  return null;   // never a page (OpenCustomUIInteraction opens nothing for null)
}""".replace("@GOOD@", SUI.COLOR["success"]).replace("@BAD@", SUI.COLOR["error"]).replace("@INFO@", SUI.COLOR["info"]))
'''
rep('''# ================= ShTick: 1 s scheduler tick - idle unload + queue, regrow, sweep, particles, pending placements =================
''', HAND_JAVA + '''
# ================= ShTick: 1 s scheduler tick - idle unload + queue, regrow, sweep, particles, pending placements =================
''')
# ShTick: the hand-held showers (any world: overworld, island, shard)
rep('''    @PKG@.ShWorlds.idle(now);
    @PKG@.ShPlace.verify(now);
''', '''    @PKG@.ShWorlds.idle(now);
    @PKG@.ShPlace.verify(now);
    java.util.Iterator sh = @PKG@.ShHand.SHOWER.entrySet().iterator();   // 0.4: hand-held totem particles while they last
    while (sh.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) sh.next();
      Object[] sv = (Object[]) en.getValue();
      double[] sc = (double[]) sv[1];
      if ((long) sc[4] < now) { sh.remove(); continue; }
      @WLD@ sw = @UNI@.get().getWorld((String) sv[0]);
      if (sw == null || !sw.isAlive()) { sh.remove(); continue; }
      sw.execute(new @PKG@.ShRain(sw, sc, (String) sv[2]));
    }
''')
# ================================================================================================================== the pages (UI)
UI_PY = r'''# --- the summary strip (always). 0.4: views - 0 = a shard's menu (its portal on your island), 1 = the hub stand (exit only), 3 = a totem's
# own page, 4 = a Totem Bench. Each view is its own page shell (own title, own size); build() picks one.
STRIP_H = 84
base = sh.appends
base.append((BODY, SUI.panel(P + "Strip", "simple", w=IW, h=STRIP_H, layout="Left", pad=12)))
STRIP = "#" + P + "Strip"
base.append((STRIP, SUI.item_icon(P + "Icon", J_("this.shardItem", SHARD_ITEM), size=60)))   # 0.3: the open shard's portal item
base.append((STRIP, SUI.spacer(w=12)))
base.append((STRIP, SUI.group(P + "Sum", layout="Top", w=480, h=60)))
base.text("#" + P + "Sum", P + "Sum1", J_("this.sum1", "1 island - 1 totem - 60 items / hour"), "bold", size=15, h=30, w=480)
base.text("#" + P + "Sum", P + "Sum2", J_("this.sum2", "Portal on your island"), "caption", size=13, h=26, w=480)
base.append((STRIP, SUI.group(P + "Sto", layout="Top", w=260, h=60)))
base.text("#" + P + "Sto", P + "Sto1", J_("this.sto1", "Storage 100 / 600 per island"), "default", size=14, h=30, w=260)
base.text("#" + P + "Sto", P + "Sto2", J_("this.sto2", "Full in 8 h 20 m"), "caption", size=13, h=26, w=260, col=J_("this.sto2c", GOOD))
base.append((STRIP, SUI.spacer(w=12)))
s_enter = seg("enter")
s_enter.append((STRIP, SUI.button(P + "Enter", "Enter Shard", "primary", w=200)))
assert 60 + 12 + 480 + 260 + 12 + 200 <= IW - 24, "the strip is wider than the page"
# --- tabs (0.4: the Craft tab moved to the Totem Bench, the Shards overview is gone - one menu per shard)
TABS = ["Collect", "Upgrades", "Islands", "Totems"]
NTAB = len(TABS)
TAB_IDS = [P + "Tab%d" % i for i in range(NTAB)]
TAB_W = (IW - (NTAB - 1) * SUI.TAB_GAP) // NTAB
for t in range(NTAB):
    a = seg("tabs%d" % t)
    a.extend(SUI.tab_row(BODY, P + "Tabs", TAB_IDS, TABS, t, w=TAB_W))
TAB_H = SUI.BTN_H + 2 * SUI.TAB_MARGIN
CH = IH - STRIP_H - TAB_H - 34 - 50
assert CH >= 520, CH
base2 = SUI.Appends()          # after the tab content: status + footer (always)
LW, RW = 700, IW - 700 - 14
assert RW == 352


def panel_pair(a, tag, pre=None):
    pre = pre or P
    a.append((("#" + pre + "Body") if pre != P else BODY, SUI.group(pre + tag, layout="Left", w=IW, h=CH)))
    a.append(("#" + pre + tag, SUI.panel(pre + tag + "L", "simple", w=LW, h=CH, layout="Top", pad=12)))
    a.append(("#" + pre + tag, SUI.spacer(w=14)))
    a.append(("#" + pre + tag, SUI.panel(pre + tag + "R", "simple", w=RW, h=CH, layout="Top", pad=12)))
    return "#" + pre + tag + "L", "#" + pre + tag + "R"


ROWW = LW - 24
# --- Collect tab (0.4: a co-op member without shard.coopCollect sees the rows without Collect buttons)
c0 = seg("c0")
L0, R0 = panel_pair(c0, "C")
c0.append((L0, SUI.label(P + "CHead", "Stored in this shard", "panelTitle", h=30)))
c0.text(L0, P + "CCap", "Your islands make items while you are away. Collect them here.", "caption", h=24)
for i in range(SLOTS):
    for _vo in (False, True):
        a = seg(("crowv%d" if _vo else "crow%d") % i)
        rid = P + "CRow%d" % i
        a.append((L0, SUI.panel(rid, "row", w=ROWW, h=56, layout="Left", pad={"left": 8, "right": 8}, anchor={"bottom": 4})))
        a.append(("#" + rid, SUI.item_icon(rid + "Ic", J_("this.prodItem", CROP["item"]), size=40, anchor={"top": 8})))   # 0.3: the shard's item
        a.append(("#" + rid, SUI.spacer(w=10)))
        a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=330, h=56)))
        a.text("#" + rid + "Tx", rid + "Nm", J_("this.cName[%d]" % i, "Wheat Island 1 - Small"), "rowName", size=15, h=28, w=330)
        a.text("#" + rid + "Tx", rid + "Sb", J_("this.cSub[%d]" % i, "60 / hour - full in 8 h 20 m"), "rowSub", size=12, h=24, w=330)
        a.text("#" + rid, rid + "Am", J_("this.cAmt[%d]" % i, "1,200 / 2,400"), "bold", size=16, h=56, w=150, align="End")
        if not _vo:
            a.append(("#" + rid, SUI.spacer(w=10)))
            a.append(("#" + rid, SUI.button(rid + "Btn", "Collect", "secondary", "small", w=100, anchor={"top": 12})))
ce = seg("cempty")
ce.append((L0, SUI.panel(P + "CEmpty", "well", w=ROWW, h=120, layout="Top")))
ce.text("#" + P + "CEmpty", P + "CEmpty1", "Nothing to collect yet", "bold", h=30, align="Center", w=ROWW - 16)
ce.text("#" + P + "CEmpty", P + "CEmpty2", "Your islands are growing. Come back soon.", "caption", h=26, align="Center", w=ROWW - 16)
c1 = seg("c1")
c1.append((R0, SUI.label(P + "CAllHead", "Collect all", "panelTitle", h=30)))
for j, (samp, col) in enumerate((("1,200 items", None), ("+2,400 Farming XP", GOOD), ("Wheat collection +1,200", GOLD),
                                  ("Last collected 7 h 37 m ago", None), ("Inventory first. What does not fit stays here.", None),
                                  ("XP and collections are paid when you collect.", None))):
    c1.text(R0, P + "CAll%d" % j, J_("this.cAll[%d]" % j, samp), "default" if j < 3 else "caption", size=15 if j < 3 else 13,
            h=30 if j < 3 else 26, w=RW - 24, col=col, wrap=j >= 3)
c1.append((R0, SUI.spacer(h=40)))
c1b = seg("c1b")
c1b.append((R0, SUI.button(P + "CAll", "Collect all", "primary", w=RW - 24)))
# --- Upgrades tab: three cards
u0 = seg("u0")
u0.append((BODY, SUI.group(P + "U", layout="Left", w=IW, h=CH)))
CW_ = (IW - 2 * 14) // 3
assert CW_ * 3 + 28 <= IW
for ci, (cid, ctitle) in enumerate((("Store", "Storage"), ("Comp", "Auto-Compactor"), ("Time", "Time Compressor"))):
    if ci:
        u0.append(("#" + P + "U", SUI.spacer(w=14)))
    u0.append(("#" + P + "U", SUI.panel(P + "U" + cid, "simple", w=CW_, h=CH, layout="Top", pad=12)))
    u0.text("#" + P + "U" + cid, P + "U" + cid + "T", ctitle, "panelTitle", h=30)
US = "#" + P + "UStore"
for j, (samp, kind, col) in enumerate((("Tier 1 of 5", "bold", GOLD), ("Now: 100 items per island", "default", None),
                                       ("Next: 300 items per island", "default", GOOD),
                                       ("Each island of this shard holds this many items. A full island stops making items.", "caption", None),
                                       ("Cost", "section", None), ("5,000 coins (you: 12,000)", "default", J_("this.uCol[5]", GOOD)),
                                       ("1 Enchanted Wheat (you: 0)", "default", J_("this.uCol[6]", BAD)))):
    u0.text(US, P + "UStore%d" % j, J_("this.uTx[%d]" % j, samp), kind, size=14 if kind != "caption" else 13,
            h=48 if j == 3 else 28, w=CW_ - 24, col=col, wrap=j == 3)
u0.append((US, SUI.spacer(h=24)))
ub = seg("ubuy")
ub.append((US, SUI.button(P + "UBuy", "Buy upgrade", "primary", w=CW_ - 24)))
for cid, arr, samples in (("Comp", "cmTx", ("Tier 0 of 2", "Collect gives 1 Enchanted Wheat for every 100 Wheat.", "Next: Auto-Compactor I",
                                                    "Cost", "50,000 coins (you: 12,000)", "8 Enchanted Wheat (you: 0)")),
                          ("Time", "tcTx", ("Tier 0 of 3", "This shard makes items x1 as fast.", "Next: x1.25",
                                            "Cost", "25,000 coins (you: 12,000)", "8 Void Essence (you: 0)"))):
    for j, samp in enumerate(samples):
        kind_ = "bold" if j == 0 else ("section" if j == 3 else ("caption" if j == 1 else "default"))
        u0.text("#" + P + "U" + cid, P + "U" + cid + "X%d" % j, J_("this.%s[%d]" % (arr, j), samp), kind_, size=14 if kind_ != "caption" else 13,
                h=48 if j == 1 else 28, w=CW_ - 24, col=None if j in (1, 3) else J_("this.%sC[%d]" % (arr, j), GOOD), wrap=j == 1)
    u0.append(("#" + P + "U" + cid, SUI.spacer(h=24)))
ucb = seg("ucbuy")
ucb.append(("#" + P + "UComp", SUI.button(P + "UCBuy", "Buy upgrade", "primary", w=CW_ - 24)))
utb = seg("utbuy")
utb.append(("#" + P + "UTime", SUI.button(P + "UTBuy", "Buy upgrade", "primary", w=CW_ - 24)))
# --- Islands tab: the slot map (absolute) + the side panel
i0 = seg("i0")
i0.append((BODY, SUI.group(P + "I", layout="Left", w=IW, h=CH)))
i0.append(("#" + P + "I", SUI.panel(P + "IMap", "well", w=LW, h=CH, layout=None, pad=0)))
i0.append(("#" + P + "I", SUI.spacer(w=14)))
i0.append(("#" + P + "I", SUI.panel(P + "IR", "simple", w=RW, h=CH, layout="Top", pad=12)))
MAPC = (LW // 2, CH // 2 + 10)
SBW, SBH = 160, 56
HBW, HBH = 150, 44
_boxes = [("hub", MAPC[0] - HBW // 2, MAPC[1] - HBH // 2, HBW, HBH)]
i0.text("#" + P + "IMap", P + "IMapT", "Pick a slot to see its island. Islands grow in place; more island types come in a later update.", "caption", w=LW - 24, h=26,
        anchor={"left": 12, "top": 8})
_boxes.append(("title", 12, 8, LW - 24, 26))
i0.append(("#" + P + "IMap", SUI.panel(P + "IHub", "row", w=HBW, h=HBH, layout="Top", anchor={"left": MAPC[0] - HBW // 2, "top": MAPC[1] - HBH // 2})))
i0.append(("#" + P + "IHub", SUI.label(P + "IHubT", "Hub", "bold", w=HBW, h=HBH, align="Center")))
SLOT_UI = []
for i in range(SLOTS):
    ang = math.radians(-90 + 60 * i)
    cx_, cy_ = MAPC[0] + 245 * math.cos(ang), MAPC[1] + 190 * math.sin(ang)
    L_, T_ = int(round(cx_ - SBW / 2)), int(round(cy_ - SBH / 2))
    SLOT_UI.append((L_, T_))
    _boxes.append(("slot%d" % i, L_, T_, SBW, SBH))
for nm_, l_, t_, w_, h_ in _boxes:
    assert l_ >= 4 and t_ >= 4 and l_ + w_ <= LW - 4 and t_ + h_ <= CH - 4, "map box %s outside: %s" % (nm_, (l_, t_, w_, h_))
for a_ in range(len(_boxes)):
    for b_ in range(a_ + 1, len(_boxes)):
        A_, B_ = _boxes[a_], _boxes[b_]
        gx = max(B_[1] - (A_[1] + A_[3]), A_[1] - (B_[1] + B_[3]))
        gy = max(B_[2] - (A_[2] + A_[4]), A_[2] - (B_[2] + B_[4]))
        assert max(gx, gy) >= 8, "map boxes %s and %s touch" % (A_[0], B_[0])
for i in range(SLOTS):
    for state in ("normal", "selected"):
        a = seg("islot%d%s" % (i, state[0]))
        sid = P + "ISl%d" % i
        a.append(("#" + P + "IMap", SUI.group(sid + "Pos", layout="Left", w=SBW, h=SBH, anchor={"left": SLOT_UI[i][0], "top": SLOT_UI[i][1]}, bg="row")))
        a.append(("#" + sid + "Pos", SUI.hover_row(sid + "Sel", state, h=SBH, w=SBW, pad=8, sound="light")))
        a.append(("#" + sid + "Sel", SUI.group(sid + "Tx", layout="Top", w=SBW - 16, h=SBH)))
        a.text("#" + sid + "Tx", sid + "A", J_("this.sName[%d]" % i, "Slot 1 - Wheat"), "rowName", size=14, h=28, w=SBW - 16)
        a.text("#" + sid + "Tx", sid + "B", J_("this.sSub[%d]" % i, "Small"), "rowSub", size=12, h=22, w=SBW - 16)
IR = "#" + P + "IR"
i1 = seg("iside")
i1.text(IR, P + "IRT", J_("this.iTitle", "Slot 1 - Wheat Island"), "panelTitle", h=30, w=RW - 24)
for j, samp in enumerate(("Size: Small (13 x 13)", "Makes 60 items / hour", "Totems: 1 Harvest Spirit I", "Next: Medium (21 x 21)",
                          "Would make 96 items / hour", "Cost", "5,000 coins (you: 12,000)", "8 Eternal Wheat Seeds (you: 0)",
                          "Wheat collection 4 (you: 2)")):
    kind = "section" if j == 5 else "default"
    i1.text(IR, P + "IR%d" % j, J_("this.iTx[%d]" % j, samp), kind, size=14, h=28, w=RW - 24,
            col=J_("this.iCol[%d]" % j, TEXT) if j not in (5,) else None)
i1.append((IR, SUI.spacer(h=12)))
ig = seg("igrow")
ig.append((IR, SUI.button(P + "IGrow", "Grow island", "primary", w=RW - 24)))
# --- Totems tab (the selected island's totems; place from the inventory = the OWNER only; the selected totem on the right)
t0 = seg("t0")
L3, R3 = panel_pair(t0, "T")
t0.append((L3, SUI.label(P + "THead", "Totems", "panelTitle", h=30)))
t0.text(L3, P + "TCap", J_("this.tCap", "Island 1 - Wheat Small - 1 of 3 pads (pick the island on the Islands tab)"), "caption", h=24, w=ROWW)
TROW_W_TX, TROW_W_ST, TROW_W_BTN = 430, 110, 100
assert TROW_W_TX + TROW_W_ST + TROW_W_BTN + 20 + 10 <= ROWW
for i in range(5):
    a = seg("trow%d" % i)
    rid = P + "TRow%d" % i
    a.append((L3, SUI.panel(rid, "row", w=ROWW, h=50, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=TROW_W_TX, h=50)))
    a.text("#" + rid + "Tx", rid + "Nm", J_("this.tName[%d]" % i, "Harvest Spirit Totem Pole I"), "rowName", size=15, h=26, w=TROW_W_TX)
    a.text("#" + rid + "Tx", rid + "Sb", J_("this.tSub[%d]" % i, "Worker - range 3 - 1 / min"), "rowSub", size=12, h=22, w=TROW_W_TX)
    a.text("#" + rid, rid + "St", J_("this.tSt[%d]" % i, "Selected"), "bold", size=14, h=50, w=TROW_W_ST, align="End", col=GOLD)
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Open", "secondary", "small", w=TROW_W_BTN, anchor={"top": 9})))
te = seg("tempty")
te.text(L3, P + "TEmpty", "No totems on this island yet - place one from your inventory below.", "caption", h=30, w=ROWW)
t0b = seg("t0b")
t0b.append((L3, SUI.label(P + "TPHead", "Place from your inventory", "section", h=30)))
for i in range(4):
    a = seg("prow%d" % i)
    rid = P + "PRow%d" % i
    a.append((L3, SUI.panel(rid, "row", w=ROWW, h=40, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.text("#" + rid, rid + "Nm", J_("this.pName[%d]" % i, "Rain Totem Pole II - modifiers: -"), "default", size=14, h=40, w=ROWW - 20 - 110)
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Place", "secondary", "small", w=100, anchor={"top": 4})))
pe = seg("pempty")
pe.text(L3, P + "PEmpty", "No totems in your inventory - craft them at the Totem Bench on the shard's hub island.", "caption", h=30, w=ROWW)
pc = seg("pcoop")
pc.text(L3, P + "PCoop", "Only the island owner places and picks up totems.", "caption", h=30, w=ROWW)
t1 = seg("tside")
t1.text(R3, P + "TDT", J_("this.dTitle", "Harvest Spirit Totem Pole I"), "panelTitle", size=17, h=30, w=RW - 24)
for j in range(8):
    t1.text(R3, P + "TD%d" % j, J_("this.dTx[%d]" % j, "Worker - range 3 blocks"), "default", size=13, h=26, w=RW - 24, col=J_("this.dCol[%d]" % j, TEXT))
t1.append((R3, SUI.spacer(h=6)))
HB = (RW - 24 - 8) // 2
assert HB * 2 + 8 <= RW - 24
td = seg("tdbtn")
TD_BTNS = (("TModAdd", "Add modifier", "TModNext", "Other modifier"), ("TMod1", "Remove mod 1", "TMod2", "Remove mod 2"),
           ("TBoost", "Add booster", "TRange", "Show range"), ("TUp", "Tier up", "TPick", "Pick up"))   # 0.4: Upgrade -> Tier up (the bench)
for gi, (b1, t1_, b2, t2_) in enumerate(TD_BTNS):
    gid = P + "TB%d" % gi
    td.append((R3, SUI.group(gid, layout="Left", w=RW - 24, h=SUI.BTN_SMALL_H, anchor={"bottom": 6})))
    td.append(("#" + gid, SUI.button(P + b1, t1_, "secondary", "small", w=HB)))
    td.append(("#" + gid, SUI.spacer(w=8)))
    td.append(("#" + gid, SUI.button(P + b2, t2_, "secondary", "small", w=HB)))
TD_ACTS = [("TModAdd", "tmodadd"), ("TModNext", "tmodnext"), ("TMod1", "tmodrem1"), ("TMod2", "tmodrem2"),
           ("TBoost", "tboost"), ("TRange", "trange"), ("TUp", "tup"), ("TPick", "tpick")]
TD_BINDS = [(P + i_, v_) for i_, v_ in TD_ACTS]
# --- status + footer (always). 0.4: Pick up Shard (the owner) + Get back lost shard (an island reset left another shard's portal behind)
base2.text(BODY, P + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=IW, align="Center", col=J_("this.stCol", INFO), anchor={"top": 4})
base2.append((BODY, SUI.group(P + "Foot", layout="Left", w=IW, h=SUI.BTN_H, anchor={"top": 6})))
FOOT = "#" + P + "Foot"
REC_W = 330
s_pick = seg("pick")
s_pick.append((FOOT, SUI.button(P + "Pick", "Pick up Shard", "secondary", w=200)))
s_pick.append((FOOT, SUI.spacer(w=IW - 200 - 172)))
s_prec = seg("pickrec")
s_prec.append((FOOT, SUI.button(P + "Pick", "Pick up Shard", "secondary", w=200)))
s_prec.append((FOOT, SUI.spacer(w=12)))
s_prec.append((FOOT, SUI.button(P + "Rec", "Get back lost shard", "secondary", w=REC_W)))
s_prec.append((FOOT, SUI.spacer(w=IW - 200 - 12 - REC_W - 172)))
s_nopick = seg("nopick")
s_nopick.append((FOOT, SUI.spacer(w=IW - 172)))
base3 = SUI.Appends()
base3.append((FOOT, SUI.button(P + "Close", "Close", "secondary", w=172, sound="cancel")))
# the page check: every element of every segment together (ids unique, parents exist, kit-proven markup)
for a_ in list(SEG.values()) + [base2, base3]:
    ALL.extend(a_)
# segments that are exclusive (tabs / slot states / button rows / footers) legitimately repeat ids: check one coherent variant each
VARIANTS = []
for t in range(NTAB):
    for sel in range(SLOTS):
        v = SUI.Appends(sh.appends)
        v.extend(SEG["enter"])
        v.extend(SEG["tabs%d" % t])
        if t == 0:
            for k_ in ["c0"] + ["crow%d" % i for i in range(SLOTS)] + ["c1", "c1b"]:
                v.extend(SEG[k_])
        elif t == 1:
            v.extend(SEG["u0"]); v.extend(SEG["ubuy"]); v.extend(SEG["ucbuy"]); v.extend(SEG["utbuy"])
        elif t == 2:
            v.extend(SEG["i0"])
            for i in range(SLOTS):
                v.extend(SEG["islot%d%s" % (i, "s" if i == sel else "n")])
            v.extend(SEG["iside"]); v.extend(SEG["igrow"])
        else:
            v.extend(SEG["t0"])
            for i in range(5):
                v.extend(SEG["trow%d" % i])
            v.extend(SEG["t0b"])
            for i in range(4):
                v.extend(SEG["prow%d" % i])
            v.extend(SEG["tside"]); v.extend(SEG["tdbtn"])
        v.extend(base2)
        v.extend(SEG["pickrec" if t == 3 else "pick"])
        v.extend(base3)
        VARIANTS.append(v)
        if t != 2:
            break
# the co-op variants (no Collect buttons, no place rows / totem buttons, no Pick up) + the empty Totems tab
v = SUI.Appends(sh.appends); v.extend(SEG["enter"]); v.extend(SEG["tabs0"]); v.extend(SEG["c0"])
for i in range(SLOTS):
    v.extend(SEG["crowv%d" % i])
v.extend(SEG["c1"]); v.extend(base2); v.extend(SEG["nopick"]); v.extend(base3)
VARIANTS.append(v)
v = SUI.Appends(sh.appends); v.extend(SEG["enter"]); v.extend(SEG["tabs3"]); v.extend(SEG["t0"]); v.extend(SEG["tempty"]); v.extend(SEG["t0b"])
v.extend(SEG["pcoop"]); v.extend(SEG["tside"]); v.extend(base2); v.extend(SEG["nopick"]); v.extend(base3)
VARIANTS.append(v)
v = SUI.Appends(sh.appends); v.extend(SEG["enter"]); v.extend(SEG["tabs3"]); v.extend(SEG["t0"]); v.extend(SEG["tempty"]); v.extend(SEG["t0b"])
v.extend(SEG["pempty"]); v.extend(SEG["tside"]); v.extend(base2); v.extend(SEG["pick"]); v.extend(base3)
VARIANTS.append(v)
for v in VARIANTS:
    v.check(P)


def jseg(name):
    return SEG[name].java("b")


def binds(ids_vals):
    return "\n".join('  ev.addEventBinding(@BT@.Activating, "#%s", @EVD@.of("a", "%s"));' % (i, v) for i, v in ids_vals)


BUILD_JAVA = "\n".join([
    sh.java("b"),          # 0.4: the shell WITH its title b.set (0.1-0.3.2 emitted sh.appends only - a blank title bar)
    jseg("enter"), binds([(P + "Enter", "enter")]),
    "  if (this.tab == 0) {", jseg("tabs0"), "  } else if (this.tab == 1) {", jseg("tabs1"), "  } else if (this.tab == 2) {", jseg("tabs2"),
    "  } else {", jseg("tabs3"), "  }",
    binds([(TAB_IDS[i], "tab%d" % i) for i in range(NTAB)]),
    "  if (this.tab == 0) {", jseg("c0"),
    "    if (this.cN == 0) {", jseg("cempty"), "    }",
] + ["    if (this.cN > %d && this.manage) {\n%s\n%s\n    } else if (this.cN > %d) {\n%s\n    }" % (i, jseg("crow%d" % i), binds([(P + "CRow%dBtn" % i, "col%d" % i)]), i, jseg("crowv%d" % i)) for i in range(SLOTS)] + [
    jseg("c1"), "    if (this.manage) {", jseg("c1b"), binds([(P + "CAll", "colall")]), "    }",
    "  } else if (this.tab == 1) {", jseg("u0"), "    if (this.uCan && this.manage) {", jseg("ubuy"), binds([(P + "UBuy", "buy")]), "    }",
    "    if (this.cmCan && this.manage) {", jseg("ucbuy"), binds([(P + "UCBuy", "cmpbuy")]), "    }",
    "    if (this.tcCan && this.manage) {", jseg("utbuy"), binds([(P + "UTBuy", "tcbuy")]), "    }",
    "  } else if (this.tab == 2) {", jseg("i0"),
] + ["    if (this.sel == %d) {\n%s\n    } else {\n%s\n    }\n%s" % (i, jseg("islot%ds" % i), jseg("islot%dn" % i), binds([(P + "ISl%dSel" % i, "slot%d" % i)]))
     for i in range(SLOTS)] + [
    jseg("iside"), "    if (this.iCan && this.manage) {", jseg("igrow"), binds([(P + "IGrow", "grow")]), "    }",
    "  } else {", jseg("t0"),
    "    if (this.tN == 0) {", jseg("tempty"), "    }",
] + ["    if (this.tN > %d) {\n%s\n%s\n    }" % (i, jseg("trow%d" % i), binds([(P + "TRow%dBtn" % i, "tsel%d" % i)])) for i in range(5)] + [
    jseg("t0b"),
    "    if (!this.mine) {", jseg("pcoop"), "    } else if (this.pN == 0) {", jseg("pempty"), "    }",
] + ["    if (this.mine && this.pN > %d) {\n%s\n%s\n    }" % (i, jseg("prow%d" % i), binds([(P + "PRow%dBtn" % i, "tplace%d" % i)])) for i in range(4)] + [
    jseg("tside"), "    if (this.dHas && this.mine) {", jseg("tdbtn"), binds(TD_BINDS), "    }",
    "  }",
    base2.java("b"),
    "  if (this.mine && this.lostKind >= 0) {", jseg("pickrec"), binds([(P + "Pick", "pick"), (P + "Rec", "reclaim")]),
    "  } else if (this.mine) {", jseg("pick"), binds([(P + "Pick", "pick")]), "  } else {", jseg("nopick"), "  }",
    base3.java("b"), binds([(P + "Close", "close")]),
])

# --- 0.4 VIEW 1: the stand inside the shard hub = an EXIT page (Back to Island only - spec 9.5)
X = "SkyyShX"
shx = SUI.page_shell(X, 640, 340, title=J_("this.title", "Farming Shard"), kind="decorated")
XIW = shx.inner_w
XB = "#" + shx.body
xa = SUI.Appends()
xa.text(XB, X + "L0", J_("this.xTx[0]", "You are on the hub island of your Farming Shard."), "bold", size=15, h=30, w=XIW)
xa.text(XB, X + "L1", J_("this.xTx[1]", "The Totem Bench here crafts and tiers up this shard's totems."), "caption", size=13, h=26, w=XIW)
xa.text(XB, X + "L2", J_("this.xTx[2]", "This shard's menu opens from its portal on your island."), "caption", size=13, h=26, w=XIW)
xa.append((XB, SUI.spacer(h=12)))
xa.text(XB, X + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=XIW, align="Center", col=J_("this.stCol", INFO))
xa.append((XB, SUI.group(X + "Foot", layout="Left", w=XIW, h=SUI.BTN_H, anchor={"top": 8})))
xa.append(("#" + X + "Foot", SUI.button(X + "Back", "Back to Island", "primary", w=260)))
xa.append(("#" + X + "Foot", SUI.spacer(w=XIW - 260 - 172)))
xa.append(("#" + X + "Foot", SUI.button(X + "Close", "Close", "secondary", w=172, sound="cancel")))
shx.fit([30, 26, 26, 12, 30, 8 + SUI.BTN_H], "the exit page")
_xv = SUI.Appends(shx.appends)
_xv.extend(xa)
_xv.check(X)
VARIANTS.append(_xv)
BUILD_EXIT = "\n".join([shx.java("b"), xa.java("b"), binds([(X + "Back", "back"), (X + "Close", "close")])])

# --- 0.4 VIEW 3: a placed totem's OWN page (spec 9.3 / 9.8; the owner gets the buttons, co-op members look)
W = "SkyyShW"
shw = SUI.page_shell(W, 660, 640, title=J_("this.title", "Harvest Spirit Totem Pole I"), kind="decorated")
WIW = shw.inner_w
WB = "#" + shw.body
wa = SUI.Appends()
wa.text(WB, W + "Head", J_("this.dTitle", "Harvest Spirit Totem Pole I - pad 1"), "panelTitle", size=17, h=30, w=WIW)
for j in range(8):
    wa.text(WB, W + "D%d" % j, J_("this.dTx[%d]" % j, "Worker - range 3 blocks"), "default", size=13, h=26, w=WIW, col=J_("this.dCol[%d]" % j, TEXT))
wa.append((WB, SUI.spacer(h=6)))
WHB = (WIW - 8) // 2
wbt = SUI.Appends()
for gi, (b1, t1_, b2, t2_) in enumerate(TD_BTNS):
    gid = W + "G%d" % gi
    wbt.append((WB, SUI.group(gid, layout="Left", w=WIW, h=SUI.BTN_SMALL_H, anchor={"bottom": 6})))
    wbt.append(("#" + gid, SUI.button(W + b1[1:], t1_, "secondary", "small", w=WHB)))
    wbt.append(("#" + gid, SUI.spacer(w=8)))
    wbt.append(("#" + gid, SUI.button(W + b2[1:], t2_, "secondary", "small", w=WHB)))
W_BINDS = [(W + i_[1:], v_) for i_, v_ in TD_ACTS]
wvw = SUI.Appends()
wvw.text(WB, W + "View", "Only the island owner can change or pick up this totem.", "caption", h=30, w=WIW)
wft = SUI.Appends()
wft.text(WB, W + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=WIW, align="Center", col=J_("this.stCol", INFO), anchor={"top": 4})
wft.append((WB, SUI.group(W + "Foot", layout="Left", w=WIW, h=SUI.BTN_H, anchor={"top": 6})))
wft.append(("#" + W + "Foot", SUI.spacer(w=WIW - 172)))
wft.append(("#" + W + "Foot", SUI.button(W + "Close", "Close", "secondary", w=172, sound="cancel")))
shw.fit([30, 8 * 26, 6, 4 * (SUI.BTN_SMALL_H + 6), 34, 6 + SUI.BTN_H], "the totem page")
for _wx in (wbt, wvw):
    _wv = SUI.Appends(shw.appends)
    _wv.extend(wa); _wv.extend(_wx); _wv.extend(wft)
    _wv.check(W)
    VARIANTS.append(_wv)
BUILD_TOTEM = "\n".join([shw.java("b"), wa.java("b"), "  if (this.dHas && this.mine) {", wbt.java("b"), binds(W_BINDS), "  } else {", wvw.java("b"), "  }",
                         wft.java("b"), binds([(W + "Close", "close")])])

# --- 0.4 VIEW 4: a Totem Bench (spec 9.7): tabs Craft / Tier up / Bench; the owner gets the buttons, co-op members look
BP = "SkyyShB"
shb = SUI.page_shell(BP, PW, PH, title=J_("this.title", "Farming Totem Bench"), kind="decorated")
assert (shb.inner_w, shb.inner_h) == (IW, IH)
BB = "#" + shb.body
BSEG = {}


def bseg(name):
    a = SUI.Appends()
    BSEG[name] = a
    return a


bs0 = bseg("strip")
bs0.append((BB, SUI.panel(BP + "Strip", "simple", w=IW, h=STRIP_H, layout="Left", pad=12)))
bs0.append(("#" + BP + "Strip", SUI.item_icon(BP + "Icon", J_("this.bIcon", BENCH_BLOCKS[FARM_K]), size=60)))
bs0.append(("#" + BP + "Strip", SUI.spacer(w=12)))
bs0.append(("#" + BP + "Strip", SUI.group(BP + "Sum", layout="Top", w=560, h=60)))
bs0.text("#" + BP + "Sum", BP + "Sum1", J_("this.bTitle", "Totem Bench I of IV"), "bold", size=15, h=30, w=560)
bs0.text("#" + BP + "Sum", BP + "Sum2", J_("this.bSub", "Next: Bench II - see the Bench tab"), "caption", size=13, h=26, w=560, col=J_("this.bSubC", GOOD))
bs0.append(("#" + BP + "Strip", SUI.group(BP + "Cap", layout="Top", w=410, h=60)))
bs0.text("#" + BP + "Cap", BP + "Cap1", J_("this.bCap", "Crafts the Farming Shard's totems."), "default", size=14, h=30, w=410)
bs0.text("#" + BP + "Cap", BP + "Cap2", J_("this.bCap2", "Totems tier up to Totem Pole II here."), "caption", size=13, h=26, w=410)
assert 60 + 12 + 560 + 410 <= IW - 24
BTABS = ["Craft", "Tier up", "Bench"]
BTAB_IDS = [BP + "Tab%d" % i for i in range(len(BTABS))]
BTAB_W = (IW - (len(BTABS) - 1) * SUI.TAB_GAP) // len(BTABS)
for t in range(len(BTABS)):
    bseg("tabs%d" % t).extend(SUI.tab_row(BB, BP + "Tabs", BTAB_IDS, BTABS, t, w=BTAB_W))
# Craft (the 0.2-0.3 Craft tab, moved here): this shard's totems, the 6 modifiers, then every shard (extra shards: rebirth 2)
k0 = bseg("k0")
L4, R4 = panel_pair(k0, "K", BP)
k0.append((L4, SUI.label(BP + "KHead", "Craft", "panelTitle", h=30)))
k0.text(L4, BP + "KCap", J_("this.kCap", "Page 1 of 3 - new totems come out at tier I."), "caption", h=24, w=ROWW)
KROWS = 7
for i in range(KROWS):
    a = bseg("krow%d" % i)
    rid = BP + "KRow%d" % i
    a.append((L4, SUI.panel(rid, "row", w=ROWW, h=50, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=TROW_W_TX, h=50)))
    a.text("#" + rid + "Tx", rid + "Nm", J_("this.kName[%d]" % i, "Harvest Spirit Totem Pole I"), "rowName", size=15, h=26, w=TROW_W_TX)
    a.text("#" + rid + "Tx", rid + "Sb", J_("this.kSub[%d]" % i, "128 Wheat, 8 Life Essence, 500 coins"), "rowSub", size=12, h=22, w=TROW_W_TX)
    a.text("#" + rid, rid + "St", J_("this.kSt[%d]" % i, "Ready"), "bold", size=14, h=50, w=TROW_W_ST, align="End", col=J_("this.kStC[%d]" % i, GOOD))
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Select", "secondary", "small", w=TROW_W_BTN, anchor={"top": 9})))
kp = bseg("kpage")
kp.append((L4, SUI.group(BP + "KPg", layout="Left", w=ROWW, h=SUI.BTN_SMALL_H, anchor={"top": 4})))
kp.append(("#" + BP + "KPg", SUI.button(BP + "KPrev", "Previous", "secondary", "small", w=160)))
kp.append(("#" + BP + "KPg", SUI.spacer(w=ROWW - 320)))
kp.append(("#" + BP + "KPg", SUI.button(BP + "KNext", "Next", "secondary", "small", w=160)))
k1 = bseg("kside")
k1.text(R4, BP + "KT", J_("this.kTitle", "Harvest Spirit Totem Pole I"), "panelTitle", size=17, h=30, w=RW - 24)
for j in range(9):
    k1.text(R4, BP + "KD%d" % j, J_("this.kTx[%d]" % j, "128 Wheat (you: 40)"), "default", size=13, h=26, w=RW - 24, col=J_("this.kCol[%d]" % j, TEXT))
k1.append((R4, SUI.spacer(h=10)))
kc = bseg("kcraft")
kc.append((R4, SUI.button(BP + "KCraft", "Craft", "primary", w=RW - 24)))
# Tier up: this shard's totems in your inventory (6 rows) + the picked one
r0 = bseg("r0")
L5, R5 = panel_pair(r0, "R", BP)
r0.append((L5, SUI.label(BP + "RHead", "Tier up a totem", "panelTitle", h=30)))
r0.text(L5, BP + "RCap", J_("this.rCap", "Totems of this shard tier up to Totem Pole II at this bench."), "caption", h=24, w=ROWW)
RROWS = 6
for i in range(RROWS):
    a = bseg("rrow%d" % i)
    rid = BP + "RRow%d" % i
    a.append((L5, SUI.panel(rid, "row", w=ROWW, h=50, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=TROW_W_TX, h=50)))
    a.text("#" + rid + "Tx", rid + "Nm", J_("this.rName[%d]" % i, "Rain Totem I"), "rowName", size=15, h=26, w=TROW_W_TX)
    a.text("#" + rid + "Tx", rid + "Sb", J_("this.rSub[%d]" % i, "Next: Rain Totem Pole II"), "rowSub", size=12, h=22, w=TROW_W_TX)
    a.text("#" + rid, rid + "St", J_("this.rSt[%d]" % i, "Selected"), "bold", size=14, h=50, w=TROW_W_ST, align="End", col=J_("this.rStC[%d]" % i, GOLD))
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Select", "secondary", "small", w=TROW_W_BTN, anchor={"top": 9})))
re_ = bseg("rempty")
re_.text(L5, BP + "REmpty", "No totem of this shard in your inventory - pick one up from its island first.", "caption", h=30, w=ROWW)
r1 = bseg("rside")
r1.text(R5, BP + "RT", J_("this.rTitle", "Rain Totem I"), "panelTitle", size=17, h=30, w=RW - 24)
for j in range(9):
    r1.text(R5, BP + "RD%d" % j, J_("this.rTx[%d]" % j, "Next: Rain Totem Pole II"), "default", size=13, h=26, w=RW - 24, col=J_("this.rCol[%d]" % j, TEXT))
r1.append((R5, SUI.spacer(h=10)))
rb = bseg("rbtn")
rb.append((R5, SUI.button(BP + "RUp", "Tier up", "primary", w=RW - 24)))
# Bench: what each bench tier unlocks (left) + the next upgrade (right)
e0 = bseg("e0")
L6, R6 = panel_pair(e0, "E", BP)
e0.append((L6, SUI.label(BP + "EHead", "Bench tiers", "panelTitle", h=30)))
for j in range(4):
    e0.text(L6, BP + "ED%d" % j, J_("this.eTx[%d]" % j, "Bench I: Harvest Spirit, Rain, Scarecrow + Wider Area, Faster - up to Totem Pole II"), "default",
            size=13, h=52, w=ROWW, col=J_("this.eCol[%d]" % j, TEXT), wrap=True)
e0.text(L6, BP + "ED4", J_("this.eTx[4]", "Totems you already have stay yours whatever the bench tier."), "caption", size=13, h=26, w=ROWW)
e0.append((R6, SUI.label(BP + "FHead", "Next bench tier", "panelTitle", h=30)))
for j in range(9):
    e0.text(R6, BP + "FD%d" % j, J_("this.fTx[%d]" % j, "25,000 coins (you: 12,000)"), "default", size=13, h=26, w=RW - 24, col=J_("this.fCol[%d]" % j, TEXT))
e0.append((R6, SUI.spacer(h=10)))
eb = bseg("ebtn")
eb.append((R6, SUI.button(BP + "EUp", "Upgrade bench", "primary", w=RW - 24)))
bft = bseg("foot")
bft.text(BB, BP + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=IW, align="Center", col=J_("this.stCol", INFO), anchor={"top": 4})
bft.append((BB, SUI.group(BP + "Foot", layout="Left", w=IW, h=SUI.BTN_H, anchor={"top": 6})))
bft.append(("#" + BP + "Foot", SUI.spacer(w=IW - 172)))
bft.append(("#" + BP + "Foot", SUI.button(BP + "Close", "Close", "secondary", w=172, sound="cancel")))
for t in range(len(BTABS)):
    v = SUI.Appends(shb.appends)
    v.extend(BSEG["strip"]); v.extend(BSEG["tabs%d" % t])
    if t == 0:
        for k_ in ["k0"] + ["krow%d" % i for i in range(KROWS)] + ["kpage", "kside", "kcraft"]:
            v.extend(BSEG[k_])
    elif t == 1:
        for k_ in ["r0"] + ["rrow%d" % i for i in range(RROWS)] + ["rside", "rbtn"]:
            v.extend(BSEG[k_])
    else:
        v.extend(BSEG["e0"]); v.extend(BSEG["ebtn"])
    v.extend(BSEG["foot"])
    v.check(BP)
    VARIANTS.append(v)
v = SUI.Appends(shb.appends); v.extend(BSEG["strip"]); v.extend(BSEG["tabs1"]); v.extend(BSEG["r0"]); v.extend(BSEG["rempty"]); v.extend(BSEG["rside"])
v.extend(BSEG["foot"])
v.check(BP)
VARIANTS.append(v)


def jb(name):
    return BSEG[name].java("b")


BUILD_BENCH = "\n".join([
    shb.java("b"), jb("strip"),
    "  if (this.bTab == 0) {", jb("tabs0"), "  } else if (this.bTab == 1) {", jb("tabs1"), "  } else {", jb("tabs2"), "  }",
    binds([(BTAB_IDS[i], "btab%d" % i) for i in range(len(BTABS))]),
    "  if (this.bTab == 0) {", jb("k0"),
] + ["    if (this.kN > %d) {\n%s\n%s\n    }" % (i, jb("krow%d" % i), binds([(BP + "KRow%dBtn" % i, "bksel%d" % i)])) for i in range(KROWS)] + [
    jb("kpage"), binds([(BP + "KPrev", "bkprev"), (BP + "KNext", "bknext")]),
    jb("kside"), "    if (this.kCan) {", jb("kcraft"), binds([(BP + "KCraft", "bkcraft")]), "    }",
    "  } else if (this.bTab == 1) {", jb("r0"),
    "    if (this.rN == 0) {", jb("rempty"), "    }",
] + ["    if (this.rN > %d) {\n%s\n%s\n    }" % (i, jb("rrow%d" % i), binds([(BP + "RRow%dBtn" % i, "brsel%d" % i)])) for i in range(RROWS)] + [
    jb("rside"),
    # the click carries what the page showed (slot, tier, uid): a second click from the old page can never tier up twice
    "    if (this.rCan) {", jb("rbtn"),
    '  ev.addEventBinding(@BT@.Activating, "#%sRUp", @EVD@.of("a", "brup:" + this.rCi[this.rSel] + ":" + this.rSi[this.rSel] + ":" + this.rTier[this.rSel] + ":" + this.rUid[this.rSel]));' % BP,
    "    }",
    "  } else {", jb("e0"), "    if (this.eCan) {", jb("ebtn"), binds([(BP + "EUp", "bebench")]), "    }",
    "  }",
    jb("foot"), binds([(BP + "Close", "close")]),
])
SUI.assert_proven([mk_ for v in VARIANTS for mk_ in v.markups()], what="SkyyShards shard menu / exit / totem / bench pages")
PAGE_SRC = BUILD_JAVA
print("shard pages: menu %d segments + bench %d segments, %d variants checked, menu %d x %d (content %d px), exit 640 x 340, totem 660 x 640, bench %d x %d"
      % (len(SEG), len(BSEG), len(VARIANTS), PW, PH, CH, PW, PH))
'''
span('''# --- the summary strip (always)
''', '''print("shard menu: %d segments, %d variants checked, page %d x %d, content %d px high" % (len(SEG), len(VARIANTS), PW, PH, CH))
''', UI_PY)
# ================================================================================================================== ShPage (rewritten)
PAGE_PY = r'''# ================= ShPage (0.4: four views - 0 the shard's menu from its portal, 1 the hub stand = exit, 3 a totem's own page, 4 a bench) =================
page = mk("ShPage", T["PAGE"])
for f in ("public java.util.UUID me;", "public boolean testMode;", "public String testWorld;", "public int view;", "public String key;",
          "public int tab;", "public int sel;", "public String title;", "public String sum1;", "public String sum2;", "public String sto1;",
          "public String sto2;", "public String sto2c;", "public int cN;", "public int[] cSlot;", "public String[] cName;", "public String[] cSub;",
          "public String[] cAmt;", "public String[] cAll;", "public String[] uTx;", "public String[] uCol;", "public boolean uCan;",
          "public String[] sName;", "public String[] sSub;", "public String iTitle;", "public String[] iTx;", "public String[] iCol;",
          "public boolean iCan;", "public int tN;", "public String[] tName;", "public String[] tSub;", "public String[] tSt;", "public String[] tCol;",
          "public String stText;", "public String stCol;", "public long pickArm;", "public String lastAction;",
          "public boolean mine;", "public boolean stale;",
          "public int tpad;", "public String tCap;", "public int pN;", "public String[] pName;", "public int[] pCi;", "public int[] pSi;",
          "public boolean dHas;", "public String dTitle;", "public String[] dTx;", "public String[] dCol;", "public int modSel;", "public long tpickArm;",
          "public boolean near;", "public int tIsl;",
          "public int kind;", "public String shardItem;", "public String prodItem;", "public String[] cmTx;", "public String[] cmTxC;",
          "public boolean cmCan;", "public String[] tcTx;", "public String[] tcTxC;", "public boolean tcCan;",
          # 0.4: co-op / lost shard; the exit page; the bench (strip, Craft = k*, Tier up = r*, Bench = e* / f*)
          "public boolean manage;", "public int lostKind;", "public long recArm;", "public String[] xTx;",
          "public int bTab;", "public String bIcon;", "public String bTitle;", "public String bSub;", "public String bSubC;", "public String bCap;", "public String bCap2;",
          "public int kPage;", "public int kSel;", "public int kN;", "public String kCap;", "public String[] kName;", "public String[] kSub;",
          "public String[] kSt;", "public String[] kStC;", "public int[] kIdx;", "public String kTitle;", "public String[] kTx;", "public String[] kCol;",
          "public boolean kCan;",
          "public int rN;", "public int rSel;", "public String rCap;", "public String[] rName;", "public String[] rSub;", "public String[] rSt;", "public String[] rStC;",
          "public int[] rCi;", "public int[] rSi;", "public int[] rTier;", "public String[] rUid;", "public String rTitle;", "public String[] rTx;", "public String[] rCol;",
          "public boolean rCan;", "public String[] eTx;", "public String[] eCol;", "public String[] fTx;", "public String[] fCol;", "public boolean eCan;"):
    F(page, f)
_PAGE_INIT = ("this.tab = 0; this.sel = 0; this.stText = \"\"; this.stCol = \"@INFO@\"; this.pickArm = 0L; this.lastAction = \"\"; this.tpad = 0; this.modSel = 0;"
              " this.tpickArm = 0L; this.kPage = 0; this.kSel = 0; this.kind = @FK@; this.view = 0; this.lostKind = -1; this.recArm = 0L; this.bTab = 0;"
              " this.rSel = 0; this.rN = 0; this.title = \"\";")
C(page, r"""
public ShPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.me = pr == null ? null : pr.getUuid();
  this.testMode = false;
  @INIT@
}""".replace("@INIT@", _PAGE_INIT).replace("@INFO@", INFO).replace("@FK@", str(FARM_K)))
C(page, r"""
public ShPage(java.util.UUID u, String world) {
  super((@PR@) null, @LIFE@.CanDismiss);
  this.me = u;
  this.testMode = true;
  this.testWorld = world;
  @INIT@
}""".replace("@INIT@", _PAGE_INIT).replace("@INFO@", INFO).replace("@FK@", str(FARM_K)))
M(page, r"""
public static @WLD@ worldOf(@ST@ st) {
  try {
    Object ext = st == null ? null : st.getExternalData();
    if (ext instanceof @EST@) return ((@EST@) ext).getWorld();
  } catch (Throwable t) { }
  return null;
}""")
M(page, r"""
public String worldName(@ST@ st) {
  if (this.testMode) return this.testWorld;
  @WLD@ w = worldOf(st);
  return w == null ? null : w.getName();
}""")
# 0.4: a profile key's player name while online (else "another player") - the visitor's chat line
F(page, "public static volatile java.util.function.Function NAME_TEST = null;")
M(page, r"""
public static String ownerName(String key) {
  try {
    if (NAME_TEST != null) { Object o = NAME_TEST.apply(key); if (o instanceof String) return (String) o; }
    if (key == null || key.length() < 36) return "another player";
    @PR@ pr = @UNI@.get().getPlayer(java.util.UUID.fromString(key.substring(0, 36)));
    return pr == null ? "another player" : pr.getUsername();
  } catch (Throwable t) { return "another player"; }
}""")
# 0.4 (spec 9.5): may this page OPEN? null = yes (this.view set), else the chat line ("" = nothing to say). A shard's menu opens only from
# ITS portal on the island it is placed on: the owner, co-op members (+ admins); anyone else "This is <owner>'s <Kind> Shard." The
# stand inside the hub = the exit page; a totem / bench page only inside a shard world, for the owner / co-op.
M(page, r"""
public String openGate(String wn) {
  if (!@PKG@.ShCfg.ON) return "Shards are switched off on this server.";
  if (!@PKG@.ShKind.ok(this.kind)) this.kind = @PKG@.ShKind.FARM;
  String nm = @PKG@.ShKind.NAMES[this.kind];
  if (this.view == 3 || this.view == 4) {
    if (!@PKG@.ShWorlds.isShard(wn)) return "";
    return @PKG@.ShRole.mayBeIn(this.me, @PKG@.ShWorlds.ownerOf(wn)) ? null : "This shard belongs to someone else's island.";
  }
  if (@PKG@.ShWorlds.isShard(wn)) {
    if (!@PKG@.ShRole.mayBeIn(this.me, @PKG@.ShWorlds.ownerOf(wn))) return "This shard belongs to someone else's island.";
    this.view = 1;
    return null;
  }
  String owner = wn == null ? null : @PKG@.ShRole.islandOwner(wn);
  if (owner == null) return "A shard's menu opens only from its portal on your island.";
  java.util.Properties p = @PKG@.ShStore.get(owner);
  String placed = p == null ? "" : @PKG@.ShStore.str(p, @PKG@.ShMath.kk(this.kind, "placed"));
  boolean me = owner.equals(@PKG@.ShCfg.pkey(this.me));
  if (!placed.startsWith(wn + "|")) return me ? "This " + nm + " Shard portal is not linked to your shard any more - ask an admin (/shardadmin info)." : "This is " + ownerName(owner) + "'s " + nm + " Shard.";
  if (me) { this.view = 0; return null; }
  if ((@PKG@.ShRole.coop(@PKG@.ShRole.onIsland(this.me, wn)) || @PKG@.ShCfg.isAdmin(this.me)) && @PKG@.ShRole.mayBeIn(this.me, owner)) { this.view = 0; return null; }
  return "This is " + ownerName(owner) + "'s " + nm + " Shard.";
}""")
# the shard profile this page acts on, re-checked at every build / click (fix: a removed co-op member, a profile switch); null = refused
M(page, r"""
public String resolve(@ST@ st) {
  String wn = worldName(st);
  if (this.view == 1 || this.view == 3 || this.view == 4) {
    if (!@PKG@.ShWorlds.isShard(wn)) return null;
    String sk = @PKG@.ShWorlds.ownerOf(wn);
    return @PKG@.ShRole.mayBeIn(this.me, sk) ? sk : null;
  }
  String owner = wn == null ? null : @PKG@.ShRole.islandOwner(wn);
  if (owner == null) return null;
  java.util.Properties p = @PKG@.ShStore.get(owner);
  String placed = p == null ? "" : @PKG@.ShStore.str(p, @PKG@.ShMath.kk(this.kind, "placed"));
  if (!placed.startsWith(wn + "|")) return null;
  if (owner.equals(@PKG@.ShCfg.pkey(this.me))) return owner;
  if (!@PKG@.ShRole.coop(@PKG@.ShRole.onIsland(this.me, wn)) && !@PKG@.ShCfg.isAdmin(this.me)) return null;
  return @PKG@.ShRole.mayBeIn(this.me, owner) ? owner : null;
}""")
M(page, r"""
public void status(String r) {
  if (r == null || r.length() == 0) { this.stText = ""; return; }
  char c = r.charAt(0);
  this.stCol = c == '+' ? "@GOOD@" : (c == '-' ? "@BAD@" : "@INFO@");
  this.stText = (c == '+' || c == '-' || c == '=') ? r.substring(1) : r;
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@INFO@", INFO))
M(page, r"""
public static String sizeName(int s) {
  return s >= 3 ? "Large (29 x 29)" : (s == 2 ? "Medium (21 x 21)" : "Small (13 x 13)");
}""")
M(page, r"""
public static long perHour(double perMin) {
  return (long) Math.floor(perMin * 60.0 + 0.0000001);
}""")
M(page, r"""
public static String have(long have, long need, String what) {
  return @PKG@.ShCfg.num(need) + " " + what + " (you: " + (have < 0L ? "?" : @PKG@.ShCfg.num(have)) + ")";
}""")
M(page, r"""
public static String costText(Object[] rc, int max) {
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.ShCfg.num(q[i])).append(' ').append(@PKG@.ShTotem.pretty(ids[i])); }
  long c = ((Long) rc[2]).longValue();
  if (c > 0L) { if (sb.length() > 0) sb.append(", "); sb.append(@PKG@.ShCfg.num(c)).append(" coins"); }
  String s = sb.toString();
  return s.length() > max ? s.substring(0, max - 3) + "..." : s;
}""")
M(page, r"""
public static boolean haveAll(Object[] rc, @IC@[] cs) {
  if (cs == null) return false;
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  for (int i = 0; i < ids.length; i++) if (@PKG@.ShInv.count(cs, ids[i]) < q[i]) return false;
  return true;
}""")
M(page, r"""
public static String costWords(String c) {
  if (c == null || c.startsWith("err:")) return "";
  StringBuilder sb = new StringBuilder();
  String[] a = c.split(",");
  for (int i = 0; i < a.length; i++) {
    String[] b = a[i].split(":");
    if (b.length != 2) continue;
    if (sb.length() > 0) sb.append(" + ");
    sb.append(b[1]).append(' ').append(@PKG@.ShTotem.pretty(b[0]));
  }
  return sb.toString();
}""")
# the Totems tab / the totem page texts (under the ShStore lock, settled already): the selected island, its totems on their pads, the
# inventory totems (0.4: a hand-held Totem I is marked - it cannot go on a pad), the selected totem
M(page, r"""
public void fillTotems(java.util.Properties p, @IC@[] cs, long now) {
  int kd = this.kind;
  this.tName = new String[5]; this.tSub = new String[5]; this.tSt = new String[5];
  this.pName = new String[4]; this.pCi = new int[4]; this.pSi = new int[4];
  this.dTx = new String[8]; this.dCol = new String[8];
  for (int i = 0; i < 5; i++) { this.tName[i] = ""; this.tSub[i] = ""; this.tSt[i] = ""; }
  for (int i = 0; i < 4; i++) this.pName[i] = "";
  for (int i = 0; i < 8; i++) { this.dTx[i] = ""; this.dCol[i] = "@TEXT@"; }
  this.tN = 0; this.pN = 0; this.dHas = false; this.dTitle = "No totem selected"; this.tCap = "";
  int s = this.sel < 0 || this.sel > 5 ? 0 : this.sel;
  if (p != null && !@PKG@.ShMath.hasIsland(kd, p, s)) { for (int i = 0; i < 6; i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) { s = i; break; } }
  this.tIsl = s;
  String what = kd == @PKG@.ShKind.FARM ? "crops" : "spots";
  if (p == null || !@PKG@.ShMath.hasIsland(kd, p, s)) { this.tCap = "No island yet."; }
  else {
    int sz = @PKG@.ShMath.size(kd, p, s);
    String[] e = @PKG@.ShTotem.entries(kd, p, s);
    this.tCap = "Island " + (s + 1) + " - " + @PKG@.ShKind.TNAME[kd] + " " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) + " - " + e.length + " of " + @PKG@.ShMath.pads(sz) + " pads - " + @PKG@.ShCfg.dec(@PKG@.ShMath.rate(kd, p, s, now)) + " items / min (pick the island on the Islands tab)";
    this.tN = e.length > 5 ? 5 : e.length;
    if (this.tpad >= this.tN) this.tpad = this.tN - 1;
    if (this.tpad < 0) this.tpad = 0;
    for (int i = 0; i < this.tN; i++) {
      String[] f = @PKG@.ShTotem.onPad(e[i]);   // fix: a placed record is a pole
      int ti = @PKG@.ShTotem.idx(f[0]);
      this.tName[i] = @PKG@.ShTotem.name(f);
      boolean wk = ti >= 0 && @PKG@.ShTotem.WORKER[ti];
      int ef = ti >= 0 ? @PKG@.ShTotem.EFFECT[ti] : 1;
      String eff = wk ? @PKG@.ShCfg.dec(@PKG@.ShTotem.workerRate(kd, f, sz, now)) + " / min" : (ef == 5 ? "rare finds" : (ef == 6 ? "ore -> ingots" : "+" + @PKG@.ShCfg.dec(@PKG@.ShTotem.supportPct(kd, f, now)) + " %"));
      this.tSub[i] = (wk ? "Worker" : "Support") + " - range " + @PKG@.ShTotem.range(f, now) + " - " + eff + (@PKG@.ShTotem.boosted(f, now) ? " - boosted" : "");
      this.tSt[i] = i == this.tpad ? "Selected" : "";
    }
    if (this.tN > 0) {
      String[] f = @PKG@.ShTotem.onPad(e[this.tpad]);
      int ti = @PKG@.ShTotem.idx(f[0]);
      boolean wk = ti >= 0 && @PKG@.ShTotem.WORKER[ti];
      int ef = ti >= 0 ? @PKG@.ShTotem.EFFECT[ti] : 1;
      this.dHas = true;
      this.dTitle = @PKG@.ShTotem.name(f) + " - pad " + (this.tpad + 1);
      if (wk) this.dTx[0] = "Worker: gathers the " + @PKG@.ShKind.WHAT[kd] + " in its range.";
      else if (ef == 4) this.dTx[0] = "Harvest Moon: more crops at night + rare Enchanted crops.";
      else if (ef == 5) this.dTx[0] = "Rare finds: a chance per item of " + @PKG@.ShTotem.pretty(@PKG@.ShKind.BONUS[kd]) + ".";
      else if (ef == 6) this.dTx[0] = "Auto-Smelt: this island's ore comes out as ingots.";
      else this.dTx[0] = "Support: more items for the whole island." + (@PKG@.ShTotem.gf(f) ? " (Old Totem I - also works in your hand.)" : "");
      int r = @PKG@.ShTotem.range(f, now);
      this.dTx[1] = "Range " + r + " blocks: " + @PKG@.ShTotem.cov(sz, r) + " of " + @PKG@.ShTotem.cov(sz, 99) + " " + what;
      this.dTx[2] = wk ? "Makes " + @PKG@.ShCfg.dec(@PKG@.ShTotem.workerRate(kd, f, sz, now)) + " items / min" : (ef == 5 ? "Chance " + @PKG@.ShCfg.dec(@PKG@.ShTotem.enchChance(kd, p, s) * 100.0) + " % per item on this island" : (ef == 6 ? "Collect gives ingots instead of ore" : "+" + @PKG@.ShCfg.dec(@PKG@.ShTotem.supportPct(kd, f, now)) + " % for this island"));
      if (ti >= 0 && !@PKG@.ShTotem.accepts(ti, kd)) { this.dTx[2] = "Does nothing here - it works in the " + @PKG@.ShTotem.kindsOf(ti) + " Shard."; this.dCol[2] = "@BAD@"; }
      int m1 = @PKG@.ShTotem.modIdx(f[2]); int m2 = @PKG@.ShTotem.modIdx(f[3]);
      this.dTx[3] = "Modifier 1: " + (m1 < 0 ? "empty" : @PKG@.ShTotem.MOD_NAMES[m1] + " (" + @PKG@.ShTotem.MOD_DESC[m1] + ")");
      this.dTx[4] = "Modifier 2: " + (m2 < 0 ? "empty" : @PKG@.ShTotem.MOD_NAMES[m2] + " (" + @PKG@.ShTotem.MOD_DESC[m2] + ")");
      long u = 0L;
      try { u = Long.parseLong(f[4]); } catch (Throwable x) { u = 0L; }
      this.dTx[5] = u > now ? "Booster: " + ((u - now + 59999L) / 60000L) + " min left" : "Booster: empty (1 Life, Water or Void Essence)";
      this.dCol[5] = u > now ? "@GOOD@" : "@TEXT@";
      int pick = -1;
      for (int k = 0; k < @PKG@.ShTotem.MOD_ITEMS.length && pick < 0; k++) {
        int kk = (this.modSel + k) % @PKG@.ShTotem.MOD_ITEMS.length;
        if (@PKG@.ShInv.count(cs, @PKG@.ShTotem.MOD_ITEMS[kk]) > 0L) pick = kk;
      }
      if (pick >= 0) this.modSel = pick;
      this.dTx[6] = pick < 0 ? "Add modifier: you have none (craft them at the Totem Bench)" : "Add modifier adds: " + @PKG@.ShTotem.MOD_NAMES[pick] + " (you: " + @PKG@.ShInv.count(cs, @PKG@.ShTotem.MOD_ITEMS[pick]) + ")";
      this.dCol[6] = pick < 0 ? "@BAD@" : "@GOOD@";
      String c = ti < 0 ? "err:" : @PKG@.ShTotem.costAt(kd, @PKG@.ShTotem.ITEMS[ti], @PKG@.ShTotem.doc(f, now).toJson());
      this.dTx[7] = c.startsWith("err:") ? (@PKG@.ShTotem.tierOf(f[1]) >= 5 ? "Highest tier." : "") : "Tier up at the Totem Bench: " + costWords(c);
    }
  }
  java.util.ArrayList l = @PKG@.ShInv.totems(cs);
  for (int i = 0; i < l.size() && this.pN < 4; i++) {
    Object[] a = (Object[]) l.get(i);
    String[] f = @PKG@.ShTotem.fromDoc((@BD@) a[3], (String) a[2], now);
    if (f == null) continue;
    int ti = @PKG@.ShTotem.idx(f[0]);
    String m = (f[2].length() == 0 && f[3].length() == 0) ? "no modifiers" : "modifiers: " + (f[2].length() == 0 ? "-" : @PKG@.ShTotem.MOD_NAMES[@PKG@.ShTotem.modIdx(f[2])]) + ", " + (f[3].length() == 0 ? "-" : @PKG@.ShTotem.MOD_NAMES[@PKG@.ShTotem.modIdx(f[3])]);
    String note = @PKG@.ShTotem.handHeld(f) ? " (hand-held - tier it up at the Totem Bench first)" : (ti >= 0 && !@PKG@.ShTotem.accepts(ti, kd) ? " (" + @PKG@.ShTotem.kindsOf(ti) + " Shard)" : "");
    this.pName[this.pN] = @PKG@.ShTotem.name(f) + " - " + m + note;
    this.pCi[this.pN] = ((Integer) a[0]).intValue();
    this.pSi[this.pN] = ((Integer) a[1]).intValue();
    this.pN++;
  }
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT))
# 0.4 THE BENCH PAGE (spec 9.7): the strip, Craft (this shard's totems, the modifiers, every shard), Tier up (this shard's totems in your
# inventory), Bench (what each tier unlocks + the next upgrade). Never writes.
M(page, r"""
public void fillBenchCraft(@IC@[] cs, int kd, int tier) {
  this.kName = new String[@KR@]; this.kSub = new String[@KR@]; this.kSt = new String[@KR@]; this.kStC = new String[@KR@]; this.kIdx = new int[@KR@];
  this.kTx = new String[9]; this.kCol = new String[9];
  for (int i = 0; i < @KR@; i++) { this.kName[i] = ""; this.kSub[i] = ""; this.kSt[i] = ""; this.kStC[i] = "@TEXT@"; }
  for (int i = 0; i < 9; i++) { this.kTx[i] = ""; this.kCol[i] = "@TEXT@"; }
  int n = @PKG@.ShCfg.CRAFT_ID.length;
  int[] list = new int[n];
  int m = 0;
  for (int i = 0; i < n; i++) { int ti = @PKG@.ShTotem.itemIdx(@PKG@.ShCfg.CRAFT_ID[i]); if (ti >= 0 && @PKG@.ShTotem.accepts(ti, kd)) { list[m] = i; m++; } }
  for (int i = 0; i < n; i++) if (@PKG@.ShTotem.modItemIdx(@PKG@.ShCfg.CRAFT_ID[i]) >= 0) { list[m] = i; m++; }
  for (int i = 0; i < n; i++) if (@PKG@.ShKind.ofShard(@PKG@.ShCfg.CRAFT_ID[i]) >= 0) { list[m] = i; m++; }
  int pages = (m + @KR@ - 1) / @KR@;
  if (pages < 1) pages = 1;
  if (this.kPage < 0) this.kPage = 0;
  if (this.kPage >= pages) this.kPage = pages - 1;
  boolean found = false;
  for (int i = 0; i < m; i++) if (list[i] == this.kSel) found = true;
  if (!found && m > 0) this.kSel = list[0];
  this.kCap = "Page " + (this.kPage + 1) + " of " + pages + " - new totems come out at tier I; better ones unlock with the bench tier.";
  this.kN = 0;
  for (int j = this.kPage * @KR@; j < m && this.kN < @KR@; j++) {
    int i = list[j];
    int r = this.kN;
    String id = @PKG@.ShCfg.CRAFT_ID[i];
    this.kIdx[r] = i;
    this.kName[r] = @PKG@.ShTotem.pretty(id);
    Object[] rc = @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[i]);
    this.kSub[r] = rc == null ? "switched off" : costText(rc, 60);
    String bg = @PKG@.ShCore.benchGate(kd, tier, i);
    String g = bg != null ? bg : @PKG@.ShCore.craftGate(this.me, i);
    boolean items = rc != null && haveAll(rc, cs);
    this.kSt[r] = i == this.kSel ? "Selected" : (bg != null ? "Bench" : (g != null ? "Locked" : (items ? "Ready" : "Need items")));
    this.kStC[r] = i == this.kSel ? "@GOLD@" : (g != null ? "@BAD@" : (items ? "@GOOD@" : "@WARN@"));
    this.kN++;
  }
  String id = @PKG@.ShCfg.CRAFT_ID[this.kSel];
  this.kTitle = @PKG@.ShTotem.pretty(id);
  Object[] rc = @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[this.kSel]);
  String bg = @PKG@.ShCore.benchGate(kd, tier, this.kSel);
  String g = bg != null ? bg : @PKG@.ShCore.craftGate(this.me, this.kSel);
  int j = 0;
  if (rc != null) {
    String[] ids = (String[]) rc[0];
    long[] q = (long[]) rc[1];
    for (int i = 0; i < ids.length && j < 6; i++) {
      long h = @PKG@.ShInv.count(cs, ids[i]);
      this.kTx[j] = @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]) + " (you: " + (cs == null ? "?" : @PKG@.ShCfg.num(h)) + ")";
      this.kCol[j] = cs != null && h >= q[i] ? "@GOOD@" : "@BAD@";
      j++;
    }
    long coins = ((Long) rc[2]).longValue();
    if (coins > 0L) {
      long purse = @PKG@.ShPay.coins(this.me);
      this.kTx[j] = @PKG@.ShCfg.num(coins) + " coins (you: " + (purse < 0L ? "?" : @PKG@.ShCfg.num(purse)) + ")";
      this.kCol[j] = (purse < 0L || purse >= coins) ? "@GOOD@" : "@BAD@";
      j++;
    }
    for (int i = 0; i < ids.length && j < 7; i++) {   // fix2 (critic 3 #3): a weapon (the Priest's Soul Orb) - say which one is taken
      if (!ids[i].startsWith("Weapon_")) continue;
      this.kTx[j] = "Takes a plain " + @PKG@.ShTotem.pretty(ids[i]) + " first, the one in your hotbar last.";
      this.kCol[j] = "@WARN@";
      j++;
    }
  }
  if (g != null && j < 9) { this.kTx[j] = g; this.kCol[j] = "@BAD@"; j++; }
  int ti = @PKG@.ShTotem.itemIdx(id);
  int mi = @PKG@.ShTotem.modItemIdx(id);
  int sk = @PKG@.ShKind.ofShard(id);
  if (j < 9) this.kTx[j] = ti >= 0 ? ((@PKG@.ShTotem.WORKER[ti] ? "A worker totem" : "A support totem") + (@PKG@.ShTotem.HAND[ti] ? " - starts hand-held (right-click it anywhere)." : " - starts as Totem Pole I.")) : (mi >= 0 ? @PKG@.ShTotem.MOD_DESC[mi] + "." : "A " + (sk >= 0 ? @PKG@.ShKind.NAMES[sk] : "") + " Shard for a profile that never had one (rebirth 2; one per profile, ever).");
  this.kCan = this.mine && rc != null && g == null;
}""".replace("@KR@", str(KROWS)).replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT).replace("@GOLD@", GOLD).replace("@WARN@", WARN))
M(page, r"""
public void fillBenchTier(@IC@[] cs, int kd, int tier, long now) {
  this.rName = new String[@RR@]; this.rSub = new String[@RR@]; this.rSt = new String[@RR@]; this.rStC = new String[@RR@];
  this.rCi = new int[@RR@]; this.rSi = new int[@RR@]; this.rTier = new int[@RR@]; this.rUid = new String[@RR@];
  this.rTx = new String[9]; this.rCol = new String[9];
  for (int i = 0; i < @RR@; i++) { this.rName[i] = ""; this.rSub[i] = ""; this.rSt[i] = ""; this.rStC[i] = "@GOLD@"; this.rUid[i] = ""; }
  for (int i = 0; i < 9; i++) { this.rTx[i] = ""; this.rCol[i] = "@TEXT@"; }
  int cap = @PKG@.ShCfg.benchCap(tier);
  this.rN = 0; this.rCan = false; this.rTitle = "No totem picked";
  java.util.ArrayList l = @PKG@.ShInv.totems(cs);
  Object[] fs = new Object[@RR@];
  for (int i = 0; i < l.size() && this.rN < @RR@; i++) {
    Object[] a = (Object[]) l.get(i);
    String[] f = @PKG@.ShTotem.fromDoc((@BD@) a[3], (String) a[2], now);
    if (f == null) continue;
    int ti = @PKG@.ShTotem.idx(f[0]);
    if (!@PKG@.ShTotem.accepts(ti, kd)) continue;
    int r = this.rN;
    int t = @PKG@.ShTotem.tierOf(f[1]);
    fs[r] = f;
    this.rName[r] = @PKG@.ShTotem.name(f);
    this.rSub[r] = t >= 5 ? "Highest tier" : ("Next: " + @PKG@.ShTotem.nextName(f) + (t + 1 > cap ? " - needs a higher bench" : ""));
    this.rCi[r] = ((Integer) a[0]).intValue();
    this.rSi[r] = ((Integer) a[1]).intValue();
    this.rTier[r] = t;
    this.rUid[r] = @PKG@.ShTotem.dstr((@BD@) a[3], "uid");
    this.rN++;
  }
  if (this.rSel < 0 || this.rSel >= this.rN) this.rSel = 0;
  for (int i = 0; i < this.rN; i++) {
    int t = this.rTier[i];
    this.rSt[i] = i == this.rSel ? "Selected" : (t >= 5 ? "Max" : (t + 1 > cap ? "Bench" : ""));
    this.rStC[i] = i == this.rSel ? "@GOLD@" : (t + 1 > cap ? "@WARN@" : "@TEXT@");
  }
  this.rCap = this.rN == 0 ? "No totem of this shard in your inventory." : "Totems of this shard tier up to " + @PKG@.ShTotem.LADDER[cap - 1] + " at this bench (Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + ").";
  if (this.rN == 0) { this.rTx[0] = "Pick a totem up from its island (Totems tab of the shard menu), then come back."; return; }
  String[] f = (String[]) fs[this.rSel];
  int ti = @PKG@.ShTotem.idx(f[0]);
  int t = this.rTier[this.rSel];
  this.rTitle = @PKG@.ShTotem.name(f);
  int j = 0;
  this.rTx[j] = "Range " + @PKG@.ShTotem.range(f, now) + " blocks - " + (@PKG@.ShTotem.WORKER[ti] ? "worker" : "support") + (@PKG@.ShTotem.handHeld(f) ? " - hand-held" : ""); j++;
  if (t >= 5) { this.rTx[j] = "Highest tier - nothing left to tier up."; this.rCol[j] = "@GOLD@"; return; }
  this.rTx[j] = "Next: " + @PKG@.ShTotem.nextName(f) + " (range " + @PKG@.ShCfg.RANGES[t] + ")"; this.rCol[j] = "@GOOD@"; j++;
  if (@PKG@.ShTotem.handHeld(f)) { this.rTx[j] = "Totem I -> Totem Pole II: it becomes a pole you place."; j++; }
  else if (@PKG@.ShTotem.gf(f)) { this.rTx[j] = "Old Totem I: it becomes a normal Totem Pole II."; j++; }
  if (t + 1 > cap) { this.rTx[j] = "Needs a higher bench: Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + " stops at " + @PKG@.ShTotem.LADDER[cap - 1] + "."; this.rCol[j] = "@BAD@"; return; }
  String c = @PKG@.ShTotem.costAt(kd, @PKG@.ShTotem.ITEMS[ti], @PKG@.ShTotem.doc(f, now).toJson());
  Object[] rc = null;
  if (!c.startsWith("err:")) rc = @PKG@.ShCore.recipe(c);
  if (rc == null) { this.rTx[j] = "The tier-up cost setting is broken - ask an admin."; this.rCol[j] = "@BAD@"; return; }
  this.rTx[j] = "Cost"; j++;
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  for (int i = 0; i < ids.length && j < 9; i++) {
    long h = @PKG@.ShInv.count(cs, ids[i]);
    this.rTx[j] = have(cs == null ? -1L : h, q[i], @PKG@.ShTotem.pretty(ids[i]));
    this.rCol[j] = h >= q[i] ? "@GOOD@" : "@BAD@";
    j++;
  }
  this.rCan = this.mine;
}""".replace("@RR@", str(RROWS)).replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT).replace("@GOLD@", GOLD).replace("@WARN@", WARN))
M(page, r"""
public String unlocks(int kd, int n) {
  StringBuilder sb = new StringBuilder();
  for (int ti = 0; ti < @PKG@.ShTotem.KEYS.length; ti++) {
    if (!@PKG@.ShTotem.accepts(ti, kd)) continue;
    int u = @PKG@.ShCfg.benchUnlock(kd, ti);
    if ((u < 1 ? 1 : u) != n) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(@PKG@.ShTotem.BASE[ti]);
  }
  StringBuilder mb = new StringBuilder();
  for (int mi = 0; mi < @PKG@.ShTotem.MOD_NAMES.length; mi++) {
    if (@PKG@.ShCfg.modUnlock(mi) != n) continue;
    if (mb.length() > 0) mb.append(", ");
    mb.append(@PKG@.ShTotem.MOD_NAMES[mi]);
  }
  String s = sb.length() == 0 ? "no new totems" : sb.toString();
  if (mb.length() > 0) s = s + " + " + mb.toString();
  return "Bench " + @PKG@.ShTotem.ROMAN[n - 1] + ": " + s + " - totems up to " + @PKG@.ShTotem.LADDER[@PKG@.ShCfg.benchCap(n) - 1];
}""")
M(page, r"""
public void fillBenchUp(java.util.Properties p, @IC@[] cs, int kd, int tier, int to, long at, long now) {
  this.eTx = new String[5]; this.eCol = new String[5]; this.fTx = new String[9]; this.fCol = new String[9];
  for (int i = 0; i < 5; i++) { this.eTx[i] = ""; this.eCol[i] = "@TEXT@"; }
  for (int i = 0; i < 9; i++) { this.fTx[i] = ""; this.fCol[i] = "@TEXT@"; }
  for (int n = 1; n <= 4; n++) {
    this.eTx[n - 1] = unlocks(kd, n);
    this.eCol[n - 1] = n == tier ? "@GOLD@" : (n < tier ? "@GOOD@" : "@TEXT@");
  }
  this.eTx[4] = "Totems you already have stay yours whatever the bench tier.";
  this.eCan = false;
  int j = 0;
  if (at > now) {
    this.fTx[j] = "Upgrading to Bench " + @PKG@.ShTotem.ROMAN[to - 1]; this.fCol[j] = "@GOLD@"; j++;
    this.fTx[j] = @PKG@.ShCore.secs((at - now + 999L) / 1000L) + " left (real time, also offline)."; j++;
    this.fTx[j] = "The bench keeps working at Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + " meanwhile."; j++;
    return;
  }
  if (tier >= 4) { this.fTx[j] = "Fully upgraded - Bench IV."; this.fCol[j] = "@GOLD@"; return; }
  int nt = tier + 1;
  this.fTx[j] = "Bench " + @PKG@.ShTotem.ROMAN[nt - 1] + " - takes " + @PKG@.ShCore.secs((long) @PKG@.ShCfg.BENCH_SEC[nt]); this.fCol[j] = "@GOOD@"; j++;
  this.fTx[j] = "Cost"; j++;
  long coins = @PKG@.ShCfg.BENCH_COINS[nt];
  long purse = @PKG@.ShPay.coins(this.me);
  this.fTx[j] = have(purse, coins, "coins"); this.fCol[j] = (purse < 0L || purse >= coins) ? "@GOOD@" : "@BAD@"; j++;
  String txt = @PKG@.ShCfg.benchItems(nt, kd).trim();
  Object[] rc = null;
  if (txt.length() > 0) rc = @PKG@.ShCore.recipe(txt);
  if (txt.length() > 0 && rc == null) { this.fTx[j] = "The upgrade item setting is broken (Server Setup)."; this.fCol[j] = "@BAD@"; j++; }
  if (rc != null) {
    String[] ids = (String[]) rc[0];
    long[] q = (long[]) rc[1];
    for (int i = 0; i < ids.length && j < 7; i++) {
      long h = @PKG@.ShInv.count(cs, ids[i]);
      this.fTx[j] = have(cs == null ? -1L : h, q[i], @PKG@.ShTotem.pretty(ids[i])); this.fCol[j] = h >= q[i] ? "@GOOD@" : "@BAD@"; j++;
    }
  }
  int need = @PKG@.ShCfg.BENCH_NEED[nt];
  if (need > 0 && j < 9) {
    int ct = @PKG@.ShPay.collTier(this.me, @PKG@.ShKind.COLL[kd]);
    this.fTx[j] = @PKG@.ShKind.CNAME[kd] + " collection " + need + " (you: " + (ct < 0 ? "?" : String.valueOf(ct)) + ")"; this.fCol[j] = ct >= need ? "@GOOD@" : "@BAD@"; j++;
  }
  this.eCan = this.mine && (txt.length() == 0 || rc != null);
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT).replace("@GOLD@", GOLD))
M(page, r"""
public void fillBench(String k, @IC@[] cs) {
  if (!@PKG@.ShKind.ok(this.kind)) this.kind = @PKG@.ShKind.FARM;
  int kd = this.kind;
  this.key = k;
  this.title = @PKG@.ShKind.NAMES[kd] + " Totem Bench";
  this.bIcon = @PKG@.ShGeo.IDS[@PKG@.ShGeo.BENCH + kd];
  this.mine = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));
  this.bSubC = "@GOOD@";
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  long now = @PKG@.ShCore.now();
  int tier = 1; int to = 1; long at = 0L;
  if (p != null) { @PKG@.ShStore.LOCK.lock(); try { tier = @PKG@.ShCore.benchTier(kd, p, now); to = @PKG@.ShCore.benchTo(kd, p); at = @PKG@.ShCore.benchAt(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); } }
  int cap = @PKG@.ShCfg.benchCap(tier);
  this.bTitle = p == null ? "This shard's file could not be read." : "Totem Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + " of IV";
  if (at > now) { this.bSub = "Upgrading to Bench " + @PKG@.ShTotem.ROMAN[to - 1] + " - " + @PKG@.ShCore.secs((at - now + 999L) / 1000L) + " left"; this.bSubC = "@GOLD@"; }
  else this.bSub = tier >= 4 ? "Fully upgraded" : "Next: Bench " + @PKG@.ShTotem.ROMAN[tier] + " - see the Bench tab";
  this.bCap = "Crafts the " + @PKG@.ShKind.NAMES[kd] + " Shard's totems" + (this.mine ? "." : " - only the island owner uses it.");
  this.bCap2 = "Totems tier up to " + @PKG@.ShTotem.LADDER[cap - 1] + " here.";
  fillBenchCraft(cs, kd, tier);
  fillBenchTier(cs, kd, tier, now);
  fillBenchUp(p, cs, kd, tier, to, at, now);
  if (p == null) { this.kCan = false; this.rCan = false; this.eCan = false; }
}""".replace("@GOOD@", GOOD).replace("@GOLD@", GOLD))
M(page, r"""
public void fillExit(String k) {
  if (!@PKG@.ShKind.ok(this.kind)) this.kind = @PKG@.ShKind.FARM;
  String nm = @PKG@.ShKind.NAMES[this.kind];
  this.key = k;
  this.title = nm + " Shard";
  this.xTx = new String[3];
  boolean own = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));
  this.xTx[0] = own ? "You are on the hub island of your " + nm + " Shard." : "You are on the hub island of this " + nm + " Shard.";
  this.xTx[1] = "The Totem Bench here crafts and tiers up this shard's totems.";
  this.xTx[2] = "This shard's menu opens from its portal on the island.";
}""")
# every text of a shard's menu (view 0) for profile k (settles first; never writes). 0.3: of the open shard (this.kind)
M(page, r"""
public void fill(String k, @IC@[] cs) {
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  if (!@PKG@.ShKind.ok(this.kind)) this.kind = @PKG@.ShKind.FARM;
  int kd = this.kind;
  String nm = @PKG@.ShKind.NAMES[kd];
  String tn = @PKG@.ShKind.TNAME[kd];
  this.key = k;
  this.cSlot = new int[6]; this.cName = new String[6]; this.cSub = new String[6]; this.cAmt = new String[6];
  this.cAll = new String[6]; this.uTx = new String[7]; this.uCol = new String[7];
  this.cmTx = new String[6]; this.cmTxC = new String[6]; this.tcTx = new String[6]; this.tcTxC = new String[6];
  this.sName = new String[6]; this.sSub = new String[6]; this.iTx = new String[9]; this.iCol = new String[9];
  for (int i = 0; i < 6; i++) { this.cName[i] = ""; this.cSub[i] = ""; this.cAmt[i] = ""; this.cAll[i] = ""; this.sName[i] = ""; this.sSub[i] = ""; this.cmTx[i] = ""; this.cmTxC[i] = "@TEXT@"; this.tcTx[i] = ""; this.tcTxC[i] = "@TEXT@"; }
  for (int i = 0; i < 7; i++) { this.uTx[i] = ""; this.uCol[i] = "@TEXT@"; }
  for (int i = 0; i < 9; i++) { this.iTx[i] = ""; this.iCol[i] = "@TEXT@"; }
  this.title = nm + " Shard";
  this.shardItem = @PKG@.ShKind.SHARD[kd];
  this.prodItem = @PKG@.ShKind.PROD[kd];
  this.cN = 0; this.tN = 0; this.uCan = false; this.iCan = false; this.cmCan = false; this.tcCan = false;
  this.mine = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));   // fix (critic): Pick up only for the owner
  this.manage = k != null && @PKG@.ShRole.mayManage(this.me, k);                        // 0.4: co-op Collect / buy / Grow only with shard.coopCollect
  this.stale = false;
  this.lostKind = -1;
  this.sto2c = "@GOOD@";
  this.sum2 = this.mine ? "Your shard portal. Enter Shard takes you to its islands." : "Co-op view - the island owner places totems and picks the shard up.";
  long now = @PKG@.ShCore.now();
  if (p == null) { fillTotems(null, cs, now); this.sum1 = "This shard's file could not be read."; this.sto1 = ""; this.sto2 = ""; return; }
  @PKG@.ShCore.pauseStale(k, kd, p);   // fix2: a portal left in a reset island makes nothing from the first look on
  boolean ownedNow;
  @PKG@.ShStore.LOCK.lock(); try { ownedNow = @PKG@.ShMath.owned(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (!ownedNow) this.sum2 = "No " + nm + " Shard yet - it comes from the hub quest line.";
  if (this.mine) {   // 0.4: an island reset left another shard's portal behind in the old world - "Get back lost shard" returns it
    for (int k2 = 0; k2 < @PKG@.ShKind.N && this.lostKind < 0; k2++) {
      if (k2 == kd) continue;
      String pl2 = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(k2, "placed"));
      if (pl2.length() > 0 && @PKG@.ShRole.stale(pl2, k)) this.lostKind = k2;
    }
  }
  now = @PKG@.ShCore.now();
  long total = 0L; long cap; int islands = 0; int totems = 0; double rate = 0.0; long minFull = -1L; boolean anyFull = false;
  long purse = @PKG@.ShPay.coins(this.me);
  String upg = @PKG@.ShKind.UPG[kd];
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(kd, p, now);
    cap = @PKG@.ShMath.cap(kd, p);
    fillTotems(p, cs, now);   // 0.2
    for (int i = 0; i < 6; i++) {
      boolean has = @PKG@.ShMath.hasIsland(kd, p, i);
      int sz = has ? @PKG@.ShMath.size(kd, p, i) : 0;
      this.sName[i] = "Slot " + (i + 1) + (has ? " - " + tn : "");
      this.sSub[i] = has ? (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) : "Empty";
      if (!has) continue;
      islands++;
      long s = @PKG@.ShMath.stored(kd, p, i);
      double r = @PKG@.ShMath.rate(kd, p, i, now);
      long en = @PKG@.ShMath.ench(kd, p, i);
      long icap = @PKG@.ShMath.capOf(kd, p, i);
      int nt = @PKG@.ShMath.totems(kd, p, i);
      totems += nt;
      rate += r;
      total += s;
      long tf = @PKG@.ShMath.msToFull(kd, p, i, now);
      boolean full = s >= icap;
      if (full) anyFull = true;
      if (tf >= 0L && (minFull < 0L || tf < minFull)) minFull = tf;
      int c = this.cN;
      this.cSlot[c] = i;
      this.cName[c] = tn + " Island " + (i + 1) + " - " + this.sSub[i];
      String bonus = en <= 0L ? "" : (kd == @PKG@.ShKind.FARM ? " - +" + en + " Enchanted" : " - +" + en + " " + @PKG@.ShTotem.pretty(@PKG@.ShKind.BONUS[kd]));
      this.cSub[c] = perHour(r) + " / hour - " + (full ? "FULL - collect to restart it" : (tf < 0L ? "no worker totem here" : "full in " + @PKG@.ShMath.fmtMs(tf))) + bonus + (@PKG@.ShTotem.smelts(kd, p, i) ? " - smelted" : "");
      this.cAmt[c] = @PKG@.ShCfg.num(s) + " / " + @PKG@.ShCfg.num(icap);
      this.cN = c + 1;
    }
    int tier = @PKG@.ShMath.storageTier(kd, p);
    this.uTx[0] = "Tier " + tier + " of 5";
    this.uTx[1] = "Now: " + @PKG@.ShCfg.num(cap) + " items per island";
    this.uTx[3] = "Each island of this shard holds this many items. A full island stops making items.";
    this.uTx[4] = "Cost";
    long hu = @PKG@.ShInv.count(cs, upg);
    if (tier >= 5) {
      this.uTx[2] = "Fully upgraded";
      this.uCol[2] = "@GOLD@";
      this.uTx[5] = "Nothing left to buy here.";
    } else {
      long nc = @PKG@.ShCfg.storeCoins(tier + 1);
      long ne = (long) @PKG@.ShCfg.storeEnch(tier + 1);
      this.uTx[2] = "Next: " + @PKG@.ShCfg.num(100L * (long) @PKG@.ShCfg.stacks(tier + 1)) + " items per island";
      this.uCol[2] = "@GOOD@";
      this.uTx[5] = have(purse, nc, "coins");
      this.uCol[5] = (purse < 0L || purse >= nc) ? "@GOOD@" : "@BAD@";
      this.uTx[6] = have(cs == null ? -1L : hu, ne, @PKG@.ShTotem.pretty(upg));
      this.uCol[6] = (cs != null && hu >= ne) ? "@GOOD@" : "@BAD@";
      this.uCan = true;
    }
    int cm = @PKG@.ShMath.compactor(kd, p);
    String en0 = @PKG@.ShKind.ENCH[kd];
    String en1 = @PKG@.ShKind.SMELT_ENCH[kd];
    boolean form = en0.length() > 0 || en1.length() > 0;
    this.cmTx[0] = "Tier " + cm + " of 2";
    this.cmTxC[0] = cm > 0 ? "@GOLD@" : "@TEXT@";
    this.cmTx[1] = !form ? "Nothing this shard makes has an Enchanted form yet." : (en0.length() > 0 ? "Collect gives 1 " + @PKG@.ShTotem.pretty(en0) + " for every 100 " + @PKG@.ShTotem.pretty(@PKG@.ShKind.PROD[kd]) + "." : "With an Auto-Smelt Pole: 1 " + @PKG@.ShTotem.pretty(en1) + " for every 100 ingots.");
    if (!form) { this.cmTx[2] = "No Auto-Compactor in this shard."; this.cmTxC[2] = "@WARN@"; }
    else if (cm >= 2) { this.cmTx[2] = "Fully upgraded (+" + @PKG@.ShCfg.CMP_STORE + " % storage)"; this.cmTxC[2] = "@GOLD@"; }
    else {
      long cc = @PKG@.ShCfg.CMP_COINS[cm + 1];
      long ci = (long) @PKG@.ShCfg.CMP_ITEMS[cm + 1];
      this.cmTx[2] = cm == 0 ? (en0.length() == 0 ? "Next: Compactor I - needs an Auto-Smelt Pole" : "Next: Auto-Compactor I") : "Next: II (+" + @PKG@.ShCfg.CMP_STORE + " % storage per island)";
      this.cmTxC[2] = cm == 0 && en0.length() == 0 ? "@WARN@" : "@GOOD@";
      this.cmTx[3] = "Cost";
      this.cmTx[4] = have(purse, cc, "coins");
      this.cmTxC[4] = (purse < 0L || purse >= cc) ? "@GOOD@" : "@BAD@";
      this.cmTx[5] = have(cs == null ? -1L : hu, ci, @PKG@.ShTotem.pretty(upg));
      this.cmTxC[5] = (cs != null && hu >= ci) ? "@GOOD@" : "@BAD@";
      this.cmCan = true;
    }
    int tc = @PKG@.ShMath.compressor(kd, p);
    this.tcTx[0] = "Tier " + tc + " of 3";
    this.tcTxC[0] = tc > 0 ? "@GOLD@" : "@TEXT@";
    this.tcTx[1] = "This shard makes items x" + @PKG@.ShCfg.dec(@PKG@.ShTotem.tcMult(kd, p)) + " as fast.";
    if (tc >= 3) { this.tcTx[2] = "Fully upgraded"; this.tcTxC[2] = "@GOLD@"; }
    else {
      long tcc = @PKG@.ShCfg.TC_COINS[tc + 1];
      long tv = (long) @PKG@.ShCfg.TC_VOID[tc + 1];
      long hv = @PKG@.ShInv.count(cs, "Ingredient_Void_Essence");
      this.tcTx[2] = "Next: x" + @PKG@.ShCfg.dec(@PKG@.ShCfg.TC_MULT[tc + 1]);
      this.tcTxC[2] = "@GOOD@";
      this.tcTx[3] = "Cost";
      this.tcTx[4] = have(purse, tcc, "coins");
      this.tcTxC[4] = (purse < 0L || purse >= tcc) ? "@GOOD@" : "@BAD@";
      this.tcTx[5] = have(cs == null ? -1L : hv, tv, "Void Essence");
      this.tcTxC[5] = (cs != null && hv >= tv) ? "@GOOD@" : "@BAD@";
      this.tcCan = true;
    }
    int s = this.sel < 0 || this.sel > 5 ? 0 : this.sel;
    boolean has = @PKG@.ShMath.hasIsland(kd, p, s);
    if (!has) {
      this.iTitle = "Slot " + (s + 1) + " - empty";
      this.iTx[0] = "Pick an island type for this slot.";
      this.iTx[1] = tn + " already has its island.";
      this.iTx[2] = "More island types come in a later update.";
    } else {
      int sz = @PKG@.ShMath.size(kd, p, s);
      double r = @PKG@.ShMath.rate(kd, p, s, now);
      this.iTitle = "Slot " + (s + 1) + " - " + tn + " Island";
      this.iTx[0] = "Size: " + sizeName(sz);
      this.iTx[1] = "Makes " + perHour(r) + " items / hour";
      this.iTx[2] = "Totems: " + @PKG@.ShMath.totems(kd, p, s) + " of " + @PKG@.ShMath.pads(sz) + " pads (Totems tab)";
      if (sz >= 3) {
        this.iTx[3] = "Fully grown.";
        this.iCol[3] = "@GOLD@";
        this.iTx[4] = "Use totems to make more.";
      } else {
        Object[] gi = @PKG@.ShCfg.growOf(kd);
        double nr = @PKG@.ShTotem.islandRate(kd, p, s, sz + 1, now);
        long nc = sz == 1 ? (long) @PKG@.ShCfg.GM_COINS : (long) @PKG@.ShCfg.GL_COINS;
        long ns = gi == null ? 0L : ((Long) (sz == 1 ? gi[1] : gi[2])).longValue();
        String gid = gi == null ? "" : (String) gi[0];
        int ncl = sz == 1 ? @PKG@.ShCfg.GM_COLL : @PKG@.ShCfg.GL_COLL;
        long hs = @PKG@.ShInv.count(cs, gid);
        int ct = @PKG@.ShPay.collTier(this.me, @PKG@.ShKind.COLL[kd]);
        this.iTx[3] = "Next: " + sizeName(sz + 1);
        this.iCol[3] = "@GOOD@";
        this.iTx[4] = "Would make " + perHour(nr) + " items / hour";
        this.iCol[4] = "@GOOD@";
        this.iTx[5] = "Cost";
        this.iTx[6] = have(purse, nc, "coins");
        this.iCol[6] = (purse < 0L || purse >= nc) ? "@GOOD@" : "@BAD@";
        this.iTx[7] = gi == null ? "The grow setting is broken (Server Setup)" : have(cs == null ? -1L : hs, ns, @PKG@.ShTotem.pretty(gid));
        this.iCol[7] = (gi != null && cs != null && hs >= ns) ? "@GOOD@" : "@BAD@";
        this.iTx[8] = @PKG@.ShKind.CNAME[kd] + " collection " + ncl + " (you: " + (ct < 0 ? "?" : String.valueOf(ct)) + ")";
        this.iCol[8] = ct >= ncl ? "@GOOD@" : "@BAD@";
        this.iCan = gi != null;
      }
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long per = (long) @PKG@.ShCfg.xpOf(kd);
  long xp = total * per * (long) @PKG@.ShCfg.XP_PCT / 100L;
  this.cAll[0] = @PKG@.ShCfg.num(total) + " items";
  this.cAll[1] = per <= 0L ? "No XP - this shard pays drops only" : "+" + @PKG@.ShCfg.num(xp) + " " + @PKG@.ShKind.SKILL[kd] + " XP";
  this.cAll[2] = @PKG@.ShKind.CNAME[kd] + " collection +" + @PKG@.ShCfg.num(total);
  long lc = @PKG@.ShStore.lng(p, @PKG@.ShCore.lastKey(kd), 0L);
  this.cAll[3] = lc <= 0L ? "Never collected yet." : "Last collected " + @PKG@.ShMath.fmtMs(now - lc) + " ago.";
  this.cAll[4] = this.manage ? "Inventory first. What does not fit stays here." : "Only the island owner collects here (co-op: an admin can allow it).";
  this.cAll[5] = per <= 0L ? "Collections are paid when you collect." : "XP and collections are paid when you collect.";
  this.sum1 = islands + (islands == 1 ? " island - " : " islands - ") + totems + (totems == 1 ? " totem - " : " totems - ") + perHour(rate) + " items / hour";
  this.sto1 = "Storage " + @PKG@.ShCfg.num(cap) + " per island";
  if (anyFull) { this.sto2 = "An island is FULL - collect now"; this.sto2c = "@BAD@"; }
  else if (totems == 0) { this.sto2 = "No totems - nothing is harvested"; this.sto2c = "@WARN@"; }
  else { this.sto2 = minFull < 0L ? "" : "First island full in " + @PKG@.ShMath.fmtMs(minFull); this.sto2c = "@GOOD@"; }
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@GOLD@", GOLD).replace("@WARN@", WARN).replace("@TEXT@", TEXT))
F(page, "public static volatile @IC@[] TEST_INV = null;")
M(page, r"""
public @IC@[] invOf(@REF@ ref, @ST@ st) {
  if (this.testMode) return @PKG@.ShPage.TEST_INV;
  return @PKG@.ShInv.containers(st, ref);
}""")
M(page, r"""
public static double[] aimPoint(@V3I@ b, double px, double pz) {
  if (b != null) return new double[] { (double) b.x + 0.5, (double) b.z + 0.5 };
  return new double[] { px, pz };
}""")
# a totem's page: select the totem right-clicked (fix4: the one looked at; else the nearest to the player; the player's own world thread)
M(page, r"""
public void nearTo(@REF@ ref, @ST@ st, String k) {
  try {
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null || this.testMode) return;
    @TCO@ tc = (@TCO@) st.getComponent(ref, @TCO@.getComponentType());
    if (tc == null) return;
    org.joml.Vector3d v = tc.getPosition();
    @V3I@ b = null;
    try { b = @TU@.getTargetBlockOrigin(ref, 8.0, st); } catch (Throwable t2) { b = null; }
    double[] a = aimPoint(b, v.x, v.z);
    this.kind = @PKG@.ShKind.ofX(a[0]);
    int[] n;
    @PKG@.ShStore.LOCK.lock(); try { n = @PKG@.ShCore.nearest(p, this.kind, a[0], a[1]); } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (n != null) { this.sel = n[0]; this.tpad = n[1]; }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("near", "the nearest totem could not be found (logged once): " + t); }
}""")
M(page, r"""
public void buildFull(@UCB@ b, @UEB@ ev) {
@PAGE_JAVA@
}""".replace("@PAGE_JAVA@", BUILD_JAVA))
M(page, r"""
public void buildExit(@UCB@ b, @UEB@ ev) {
@PAGE_JAVA@
}""".replace("@PAGE_JAVA@", BUILD_EXIT))
M(page, r"""
public void buildTotem(@UCB@ b, @UEB@ ev) {
@PAGE_JAVA@
}""".replace("@PAGE_JAVA@", BUILD_TOTEM))
M(page, r"""
public void buildBench(@UCB@ b, @UEB@ ev) {
@PAGE_JAVA@
}""".replace("@PAGE_JAVA@", BUILD_BENCH))
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  String k = resolve(st);
  if (k == null) status("-Only the island owner and co-op members can use this shard.");
  if (this.view == 3 && this.near && k != null) { this.near = false; nearTo(ref, st, k); }
  @IC@[] cs = invOf(ref, st);
  if (this.view == 4) fillBench(k, cs);
  else if (this.view == 1) fillExit(k);
  else {
    fill(k, cs);
    if (this.view == 3) this.title = this.dHas ? @PKG@.ShTotem.name(@PKG@.ShTotem.onPad(@PKG@.ShTotem.entries(this.kind, @PKG@.ShStore.get(k), this.tIsl)[this.tpad])) : "Totem";
  }
  if (!@PKG@.ShCfg.ON) status("-Shards are switched off on this server.");
  if (this.view == 1) buildExit(b, ev);
  else if (this.view == 3) buildTotem(b, ev);
  else if (this.view == 4) buildBench(b, ev);
  else buildFull(b, ev);
}""")
M(page, r"""
public static String jsonA(String data) {
  if (data == null) return "";
  int i = data.indexOf("\"a\"");
  if (i < 0) return "";
  i = data.indexOf(':', i + 3);
  if (i < 0) return "";
  int q = data.indexOf('"', i + 1);
  if (q < 0) return "";
  int e = data.indexOf('"', q + 1);
  if (e < 0) return "";
  return data.substring(q + 1, e);
}""")
# 0.4: the bench clicks (view 4). "brup:<section>:<slot>:<tier>:<uid>" = what the page showed when it was built
M(page, r"""
public String actBench(String a, @REF@ ref, @ST@ st) {
  if (a.startsWith("btab")) { int t = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (t >= 0 && t <= 2) this.bTab = t; return ""; }
  if (a.startsWith("bksel")) { int t = a.length() > 5 ? (int) (a.charAt(5) - '0') : -1; if (t >= 0 && t < @KR@ && this.kIdx != null && t < this.kN) this.kSel = this.kIdx[t]; return ""; }
  if (a.equals("bkprev")) { this.kPage = this.kPage - 1; return ""; }
  if (a.equals("bknext")) { this.kPage = this.kPage + 1; return ""; }
  if (a.startsWith("brsel")) { int t = a.length() > 5 ? (int) (a.charAt(5) - '0') : -1; if (t >= 0 && t < @RR@) this.rSel = t; return ""; }
  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  @IC@[] cs = invOf(ref, st);
  if (a.equals("bkcraft")) return @PKG@.ShCore.craftAt(this.me, k, this.kind, this.kSel, cs);
  if (a.equals("bebench")) return @PKG@.ShCore.benchUp(this.me, k, this.kind, cs);
  if (a.startsWith("brup:")) {
    String[] q = a.substring(5).split(":", -1);
    if (q.length < 4) return "-Pick a totem first.";
    int ci = -1; int si = -1; int tr = -1;
    try { ci = Integer.parseInt(q[0]); si = Integer.parseInt(q[1]); tr = Integer.parseInt(q[2]); } catch (Throwable t) { return "-Pick a totem first."; }
    return @PKG@.ShCore.tierUp(this.me, k, this.kind, ci, si, q[3], tr, cs);
  }
  return "";
}""".replace("@KR@", str(KROWS)).replace("@RR@", str(RROWS)))
# one click (world thread): the action, then the page is built again (never periodically)
M(page, r"""
public String act(String a, @REF@ ref, @ST@ st) {
  this.lastAction = a;
  if (this.view == 4) return actBench(a, ref, st);
  if (a.startsWith("tab")) { int t = a.length() > 3 ? (int) (a.charAt(3) - '0') : 0; if (t >= 0 && t <= 3) this.tab = t; return ""; }
  if (a.startsWith("slot")) { int s = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (s >= 0 && s <= 5) { this.sel = s; this.tpad = 0; } return ""; }
  if (a.startsWith("tsel")) { int t = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (t >= 0 && t <= 4) { this.tpad = t; this.tpickArm = 0L; } return ""; }
  if (a.equals("tmodnext")) { this.modSel = (this.modSel + 1) % 6; return ""; }
  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  java.util.UUID u = this.me;
  int kd = this.kind;
  if (this.view == 1) {
    if (!a.equals("back")) return "";
    if (this.testMode) return "=test: back";
    return @PKG@.ShWorld2.leave(st, ref, u, k, kd);
  }
  if (this.view == 0) {
    if (a.equals("colall")) return @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
    if (a.startsWith("col")) {
      int r = a.length() > 3 ? (int) (a.charAt(3) - '0') : -1;
      fill(k, invOf(ref, st));
      if (r < 0 || r >= this.cN) return "-That island is gone - the page is up to date now.";
      return @PKG@.ShCore.collect(u, k, kd, this.cSlot[r], invOf(ref, st));
    }
    if (a.equals("buy")) return @PKG@.ShCore.buyStorage(u, k, kd, invOf(ref, st));
    if (a.equals("cmpbuy")) return @PKG@.ShCore.buyCompactor(u, k, kd, invOf(ref, st));
    if (a.equals("tcbuy")) return @PKG@.ShCore.buyCompressor(u, k, kd, invOf(ref, st));
    if (a.equals("grow")) return @PKG@.ShCore.grow(u, k, kd, this.sel, invOf(ref, st));
    if (a.equals("enter")) {
      if (this.testMode) return "=test: enter";
      return @PKG@.ShWorld2.enter(st, ref, u, k, kd, worldOf(st));
    }
    if (a.equals("pick")) {
      fill(k, invOf(ref, st));
      if (!this.mine) return "-Only the island owner can pick up the shard.";
      long now = System.currentTimeMillis();
      if (now - this.pickArm > 10000L) { this.pickArm = now; return "=Click Pick up Shard again to pick it up. Its islands and storage are kept."; }
      this.pickArm = 0L;
      if (this.testMode) return "=test: pick";
      return @PKG@.ShCore.pickup(u, k, kd, worldOf(st), invOf(ref, st));
    }
    if (a.equals("reclaim")) {   // 0.4: the portal of another shard was left in a reset island's old world
      fill(k, invOf(ref, st));
      if (!this.mine || this.lostKind < 0) return "-No lost shard to get back.";
      long now = System.currentTimeMillis();
      if (now - this.recArm > 10000L) { this.recArm = now; return "=Your " + @PKG@.ShKind.NAMES[this.lostKind] + " Shard's portal was lost in an island reset. Click again to get the shard back (its islands and storage are kept)."; }
      this.recArm = 0L;
      return @PKG@.ShCore.pickup(u, k, this.lostKind, worldOf(st), invOf(ref, st));
    }
  }
  // the totem clicks (the shard menu's Totems tab or a totem's own page; the page is filled first, so tIsl / tpad / pCi / modSel are what the player saw)
  if (a.startsWith("tplace") || a.startsWith("tmod") || a.equals("tboost") || a.equals("trange") || a.equals("tup") || a.equals("tpick")) {
    @IC@[] cs = invOf(ref, st);
    fill(k, cs);
    if (a.startsWith("tplace")) {
      if (this.view != 0) return "";
      int r = a.length() > 6 ? (int) (a.charAt(6) - '0') : -1;
      if (r < 0 || r >= this.pN) return "-That totem is not in your inventory any more.";
      return @PKG@.ShCore.placeTotem(u, k, kd, this.tIsl, this.pCi[r], this.pSi[r], cs);
    }
    if (!this.dHas) return "-Pick a totem first.";
    if (a.equals("tmodadd")) return @PKG@.ShCore.addMod(u, k, kd, this.tIsl, this.tpad, this.modSel, cs);
    if (a.equals("tmodrem1")) return @PKG@.ShCore.removeMod(u, k, kd, this.tIsl, this.tpad, 1, cs);
    if (a.equals("tmodrem2")) return @PKG@.ShCore.removeMod(u, k, kd, this.tIsl, this.tpad, 2, cs);
    if (a.equals("tboost")) return @PKG@.ShCore.addBooster(u, k, kd, this.tIsl, this.tpad, cs);
    if (a.equals("trange")) return @PKG@.ShCore.showRange(k, kd, this.tIsl, this.tpad);
    if (a.equals("tup")) return @PKG@.ShCore.upgrade(u, kd);
    long now = System.currentTimeMillis();
    if (now - this.tpickArm > 10000L) { this.tpickArm = now; return "=Click Pick up again to take this totem into your inventory (tier, modifiers and booster stay with it)."; }
    this.tpickArm = 0L;
    return @PKG@.ShCore.pickTotem(u, k, kd, this.tIsl, this.tpad, cs);
  }
  return "";
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String a = jsonA(data);
  if (a.equals("close")) { if (!this.testMode) close(); return; }
  if (a.length() == 0) return;
  String r = "";
  try { r = act(a, ref, st); } catch (Throwable t) { @PKG@.ShCfg.warn("shard page action " + a + " failed: " + t); r = "-Something went wrong - the server log has the details."; }
  if (r != null && r.length() > 0) status(r);
  if (!this.testMode) {
    if ((a.equals("enter") || a.equals("back")) && r != null && r.startsWith("+")) { close(); return; }
    rebuild();
  }
}""")
# 0.4: the page suppliers - mode 0 = a portal / the hub stand (its kind), 1 = a totem block, 2 = a Totem Bench (its kind). The page is made
# only when openGate says yes (world thread); a refusal says why in chat and opens NOTHING (OpenCustomUIInteraction: null = no page)
pfn = mk("ShPageFn", None, ("java.util.function.Function",))
F(pfn, "public int mode;")
F(pfn, "public int kind;")
F(pfn, "public static final java.util.concurrent.atomic.AtomicLong REFUSED = new java.util.concurrent.atomic.AtomicLong();")
C(pfn, "public ShPageFn(int kd, int mode) { this.kind = kd; this.mode = mode; }")
M(pfn, r"""
public static String worldNameOf(@PR@ pr) {
  try {
    @REF@ r = pr == null ? null : pr.getReference();
    if (r == null || !r.isValid()) return null;
    @WLD@ w = @PKG@.ShPage.worldOf(r.getStore());
    return w == null ? null : w.getName();
  } catch (Throwable t) { return null; }
}""")
M(pfn, r"""
public @PKG@.ShPage make(@PR@ pr, java.util.UUID u, String wn) {
  @PKG@.ShPage pg = pr != null ? new @PKG@.ShPage(pr) : new @PKG@.ShPage(u, wn);
  pg.kind = this.kind;
  if (this.mode == 1) { pg.view = 3; pg.near = true; }
  if (this.mode == 2) pg.view = 4;
  String no = pg.openGate(wn);
  if (no == null) return pg;
  REFUSED.incrementAndGet();
  if (no.length() > 0 && pr != null) @PKG@.ShSay.to(pr, "[Shards] " + no, "@INFO@");
  pg.stText = no;
  return null;
}""".replace("@INFO@", INFO))
M(pfn, "public Object apply(Object o) { @PR@ pr = (@PR@) o; return make(pr, pr == null ? null : pr.getUuid(), worldNameOf(pr)); }")

# ================= bridge Function shard:fn:world (0.4: shard:fn:open - the SkyWynn Menu tile - is gone; one menu per shard, portal only) =================
bfn = mk("ShFn", None, ("java.util.function.Function",))
F(bfn, "public int mode;")
C(bfn, "public ShFn(int m) { this.mode = m; }")
M(bfn, r"""
public Object apply(Object o) {
  try { return o == null ? null : @PKG@.ShWorlds.ownerOf(String.valueOf(o)); } catch (Throwable t) { return null; }
}""")

'''
span('''# ================= ShPage =================
''', '''# ================= /shardadmin (skyyshards.admin)''', PAGE_PY + '''# ================= /shardadmin (skyyshards.admin)''')
# ================================================================================================================== the plugin
rep('''  b.put("shard:fn:open", new @PKG@.ShFn(0));
''', '')   # 0.4: no SkyWynn Menu route to a shard menu (spec 9.5 / question 22) - SkyyMenu 0.3.27 drops its tile; 0.3.26's hides by itself
rep('''  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@PAGEID@", new @PKG@.ShPageFn());
@MOREPAGES@
  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@TPAGEID@", new @PKG@.ShPageFn(true));   // 0.2: right-click a totem''',
    '''  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@PAGEID@", new @PKG@.ShPageFn(@FK@, 0));   // 0.4: the Farming portal / stand
@MOREPAGES@
  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@TPAGEID@", new @PKG@.ShPageFn(@FK@, 1));   // 0.4: right-click a totem = its own page
@BENCHPAGES@
  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@HPAGEID@", new @PKG@.ShHand());   // 0.4: a totem ITEM right-clicked in hand (never a page)''')
rep('''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - SIX SHARDS (''',
    '''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4: ONE MENU PER SHARD (right-click its portal on your island; co-op members a reduced view; the hub stand = Back to Island; a totem = its own page; no SkyWynn Menu route), a TOTEM BENCH I-IV on every hub (" + @PKG@.ShKind.N + " benches Skyy_TotemBench_<Kind>, pages SkyyTotemBench<Kind>: craft, tier up, upgrade with a timer), TOTEM FORMS (Rain / Fertilizer / Sun hand-held Totem I, page @HPAGEID@; poles from tier I), forms migration (forms=1, gf) - SIX SHARDS (''')
rep('''  b.put("shard:version", "@VERSION@");''', '''  b.put("shard:version", "@VERSION@");
  @PKG@.ShCfg.info("bridge: shard:fn:allowed / world / totem / give (0.4: no SkyWynn Menu route - a shard menu opens only from its portal)");''')
rep('''; bridge shard:fn:allowed / open / world / totem / give; " + c + "; data in " + dir);''',
    '''; bridge shard:fn:allowed / world / totem / give; " + c + "; data in " + dir);''')
rep('''}""".replace("@KITID@", KIT_ID).replace("@TPAGEID@", TOTEM_PAGE_ID).replace("@PAGEID@", PAGE_ID).replace("@RX@", str(REGION_X)).replace("@MOREPAGES@", chr(10).join(
    '  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "%s", new @PKG@.ShPageFn(%d));   // 0.3: the %s Shard portal / stand' % (PAGE_IDS[_k], _k, KINDS[_k])
    for _k in range(NK) if _k != FARM_K)))''', '''}""".replace("@KITID@", KIT_ID).replace("@TPAGEID@", TOTEM_PAGE_ID).replace("@PAGEID@", PAGE_ID).replace("@RX@", str(REGION_X)).replace("@MOREPAGES@", chr(10).join(
    '  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "%s", new @PKG@.ShPageFn(%d, 0));   // 0.3: the %s Shard portal / stand' % (PAGE_IDS[_k], _k, KINDS[_k])
    for _k in range(NK) if _k != FARM_K)).replace("@BENCHPAGES@", chr(10).join(
    '  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "%s", new @PKG@.ShPageFn(%d, 2));   // 0.4: the %s Totem Bench' % (BENCH_PAGES[_k], _k, KINDS[_k])
    for _k in range(NK))).replace("@HPAGEID@", HAND_PAGE_ID).replace("@FK@", str(FARM_K)))''')
rep('''  try { b.remove("shard:fn:allowed"); b.remove("shard:fn:open"); b.remove("shard:fn:world"); b.remove("shard:fn:totem"); b.remove("shard:fn:give"); b.remove("shard:version"); } catch (Throwable t) { }''',
    '''  try { b.remove("shard:fn:allowed"); b.remove("shard:fn:world"); b.remove("shard:fn:totem"); b.remove("shard:fn:give"); b.remove("shard:version"); } catch (Throwable t) { }''')
rep('''ALLC = [cfg, st, knd, tot, tfn, mth, geo, fill, wld, op, say, role, gate, inv, pay, core, w2, hop, tick, rng, sweep, part, place, chk, page, pfn, bfn, adm] + ADMC + [admc, gfn, pl]''',
    '''ALLC = [cfg, st, knd, tot, tfn, mth, geo, fill, wld, op, say, role, gate, inv, pay, core, w2, hop, tick, rng, sweep, part, soil, rain, hand, place, chk, page, pfn, bfn, adm] + ADMC + [admc, gfn, pl]   # 0.4: + ShSoil, ShRain, ShHand''')
# the engine members 0.4 calls (each must exist on the 0.7 jar)
rep('''             (T["ST"], "isInThread"), (T["TU"], "getTargetBlockOrigin")):
    B.probe(pool, c, m)''', '''             (T["ST"], "isInThread"), (T["TU"], "getTargetBlockOrigin"),
             # 0.4: the hand-held totems (the vanilla watering can / fertilizer pattern) + the world clock
             (T["INV"], "getItemInHand"), (T["ST"], "getResource"), ("com.hypixel.hytale.server.core.modules.time.WorldTimeResource", "getResourceType"),
             ("com.hypixel.hytale.server.core.modules.time.WorldTimeResource", "getGameTime"), ("com.hypixel.hytale.server.core.modules.time.WorldTimeResource", "getSunlightFactor"),
             ("com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock", "getComponentType"),
             ("com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock", "setWateredUntil"),
             ("com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock", "setFertilized"),
             ("com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock", "getWateredUntil"),   # fix (critic shards04)
             ("com.hypixel.hytale.server.core.modules.time.WorldTimeResource", "getSecondsPerTick"),
             ("com.hypixel.hytale.server.core.modules.block.BlockEntity", "ensureBlockEntity"), ("com.hypixel.hytale.server.core.modules.block.BlockEntity", "declaresComponent"),
             ("com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection", "getComponentType"),
             ("com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection", "getBlockReference"),
             ("com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection", "markBlockNeedsSaving"),
             (T["BSEC"], "getFiller"), (T["BSEC"], "setTicking"), (T["BSEC"], "scheduleTick"), (T["CHU"], "indexBlock"),
             (T["IC"], "replaceItemStackInSlot")):
    B.probe(pool, c, m)''')

# ================================================================================================================== assets
# the totem ITEMS: right-click in hand = HAND_PAGE_ID (a hand-held Totem I is used, a pole says where it goes; never a page)
rep('''        "Model": _hand_model, "Texture": _item_tex, "Scale": 0.305,   # 0.3.2: was _tex_path (Blocks/...)
        "IconProperties": {"Rotation": [22.5, 45, 22.5], "Scale": 0.305, "Translation": [0, -39.6]}}''',
    '''        "Model": _hand_model, "Texture": _item_tex, "Scale": 0.305,   # 0.3.2: was _tex_path (Blocks/...)
        "IconProperties": {"Rotation": [22.5, 45, 22.5], "Scale": 0.305, "Translation": [0, -39.6]},
        "Interactions": {"Secondary": {"RequireNewClick": True, "Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": HAND_PAGE_ID}}]}}}   # 0.4: hand-held use (spec 9.3.1); fix: one use per click''')
rep('''_micon = AZ.read(MOD_ICON_SRC)
''', '''# 0.4: THE TOTEM BENCHES (spec 9.7): the vanilla Abilities bench (model + Statue_Small hitbox) with its texture / icon recoloured per shard
# at BUILD time (vanilla-derived, never committed); Unbreakable, our page, hidden from the creative library (Variant), no recipe
BENCH_RAMPS = dict(SHARD_RAMPS)
BENCH_RAMPS["Farming"] = ("#5a3a00", "#c89411", "#ffe27a")   # ui-data: texture ramp (not UI)
_btex = AZ.read(BENCH_TEX_SRC)
for _k in range(NK):
    _tp = "Blocks/SkyyShards/TotemBench_%s.png" % KINDS[_k]
    _ip = "Icons/ItemsGenerated/%s.png" % BENCH_BLOCKS[_k]
    GEN["Common/" + _tp] = SA.recolor(_btex, _ramp(BENCH_RAMPS[KINDS[_k]]), rank=0.35)
    GEN["Common/" + _ip] = open(os.path.join(ROOT, "research", "cloud", "icons-1013", "icons", "Skyy_Shard_Portal_%s.png" % KINDS[_k]), "rb").read()   # fix: our icon
    TOTEM_JSON["Server/Item/Items/SkyyShards/Benches/%s.json" % BENCH_BLOCKS[_k]] = {
        "TranslationProperties": {"Name": "server.items.%s.name" % BENCH_BLOCKS[_k], "Description": "server.items.%s.description" % BENCH_BLOCKS[_k]},
        "Icon": _ip, "MaxStack": 1, "Variant": True, "PlayerAnimationsId": "Block",
        "BlockType": {"DrawType": "Model", "Material": "Solid", "Opacity": "Transparent", "CustomModel": BENCH_MODEL,
                      "CustomModelTexture": [{"Texture": _tp, "Weight": 1}], "HitboxType": "Statue_Small",
                      "BlockParticleSetId": "Stone", "BlockSoundSetId": "Stone", "PhysicalMaterialId": "Stone", "VariantRotation": "NESW",
                      "Gathering": {"Breaking": {"GatherType": "Unbreakable"}},
                      "Interactions": {"Use": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": BENCH_PAGES[_k]}}]}}}}
    for pre in ("", "server."):
        LANG.append("%sitems.%s.name=%s Totem Bench" % (pre, BENCH_BLOCKS[_k], KINDS[_k]))
        LANG.append("%sitems.%s.description=Crafts and tiers up the %s Shard's totems. It stands on the shard's hub island and cannot be moved." % (pre, BENCH_BLOCKS[_k], KINDS[_k]))
_micon = AZ.read(MOD_ICON_SRC)
''')
rep('''        LANG.append("%sitems.%s.description=%s Works in the %s Shard. Place it from your shard menu (Totems tab)." % (pre, TOTEM_ITEM[_i], _what,
                    " / ".join(_t[4])))''', '''        _form = (" It starts hand-held: right-click it anywhere. Tier it up to Totem Pole II at the Totem Bench to place it." if _t[0] in HAND_KEYS
                 else " Place it from your shard menu (Totems tab).")   # 0.4 (spec 9.3.1)
        if _t[0] == "fertilizer":
            _form += " In hand it fertilizes tilled soil (crops) for now - saplings come later."   # fix (critic shards04)
        LANG.append("%sitems.%s.description=%s Works in the %s Shard.%s" % (pre, TOTEM_ITEM[_i], _what, " / ".join(_t[4]), _form))''')
rep('''        LANG.append("%sitems.%s.description=A totem modifier: %s. Add it in the shard menu (Totems tab)." % (pre, MOD_ITEM[_i], _m[3]))''',
    '''        LANG.append("%sitems.%s.description=A totem modifier: %s. Add it in the shard menu (Totems tab or the totem's own page)." % (pre, MOD_ITEM[_i], _m[3]))''')
rep('''man = B.manifest("SkyyShards", VERSION, "SkyWynn Shards: six shards''', '''man = B.manifest("SkyyShards", VERSION, "SkyWynn Shards (0.4: one menu per shard from its portal on your island, a Totem Bench I-IV on every shard hub, hand-held Rain / Fertilizer / Sun totems): six shards''')

# fix (critic shards04): pickTotem - a tier-I Rain / Fertilizer / Sun picked up FROM A PAD comes back as a (gf) pole, never a hand-held
# Totem I (a forms migration still waiting or a rollback in between left it without gf; it was placed as a pole)
rep('''    if (f[5].length() == 0) f[5] = @PKG@.ShTotem.newUid();
    @IS@ st = @PKG@.ShTotem.stack(f, now);''', '''    if (f[5].length() == 0) f[5] = @PKG@.ShTotem.newUid();
    if (@PKG@.ShTotem.usable(f) && !@PKG@.ShTotem.gf(f)) f[6] = "gf";   // fix (critic shards04): it was on a pad = a pole
    @IS@ st = @PKG@.ShTotem.stack(f, now);''')

# ================================================================================================================== done
assert "BENCH_BLOCKS" in s and "ShHand" in s and 'VERSION = "0.4"' in s
for _gone in ('b.put("shard:fn:open"', "fillOverview", "fromMenu", "SkyyShOTab"):
    assert _gone not in s, "0.4: %s is still in the script" % _gone
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines)" % s.count(LF))
