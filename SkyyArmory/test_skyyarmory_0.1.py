"""SkyyArmory 0.1 - test harness (research/SkyyArmory-Spec.md section 9 T1-T14 + T-live, section 15.6 ST1-ST9 + ST-live). It EXECUTES the
new code paths: the generated assets go through the engine's own codecs and asset stores, the plugin's own Java runs on real engine
objects (decoded interactions / projectiles, a real Holder + ProjectileComponent, real Damage objects, the config kit, the bridge), SkyyGear
0.2.1's real code walks the real decoded chains, SkyySkills' own gate simulation runs on the final asset set, and the plugin's real setup()
runs twice on a scratch COPY of the live world data.

Run:   python SkyyArmory/test_skyyarmory_0.1.py [--jar <jar>] [--dir <scratch>] [--set-file <deploy_set copy>] [--keep] [--no-set]
       Build first: python SkyyArmory/build_skyyarmory_0.1.py. Bare JVM (the game's JRE when present), -Xverify:all, -XX:-UsePerfData;
       TEMP / TMP / java.io.tmpdir in the scratch folder. Game files (HytaleServer.jar, Assets.zip, installed mods) and the live world are
       READ ONLY - the live data is copied into the scratch folder first. Default scratch tools/dev/scratch/armory01/harness; --dir = any
       folder INSIDE tools/dev/scratch/ (fix round) - exactly that folder is deleted at the end unless --keep. --set-file (fix round) = a
       copy of tools/deploy_set.py inside tools/dev/scratch whose SET is read instead (e.g. the planned pin bump: P5 / P7 then check the
       post-pin invariants). Exit code 1 on any failure.

PYTHON PART (no JVM)
  P0  the tables re-derived from Skyy's rule (independent of the build), the jar listing per asset class, every id
  P1  T2  reference closure: every interaction / root / projectile / model / particle / trail / texture / icon / sound / animation / item /
          resource / bench + category / quality an asset names exists in the jar or Assets.zip; no SkyySkills interaction except
          Wand_Primary 0.35 -> Wand_Cast_Left_Charged; no Staff_Primary. FIX ROUND: one NEGATIVE CONTROL per reference class (a broken
          interaction / root / projectile / sound / stat / animation / model / particle / item / bench reference in a copy of our assets)
          must be caught - the engine decode (D) does NOT check references (the review proved four broken ones decode "ok")
  P2  T3 / ST3  SkyySkills' OWN gate simulation (spell_casts, exec'd from the pinned SkyySkills script) on Assets.zip + the pinned SkyySkills
          files + our jar: every wand / staff checks what it spends, tap Q, hold C, Failed spends 0; the Wood / Rotten / Tribal wands 1 / 5
  P3  T5 / ST4 + T7 / ST6  the tap / hold keys and the jumpToChargeValue rule on the JSON; cadence vs Assets.zip
  P4  T9 / ST1 / ST8  recipes = the metal's shortbow (Onyxium = Mithril with Onyxium bars), staff overrides = vanilla except Primary /
          Secondary / vars / the Onyxium recipe, SkyyGear owns the other 7 staff recipes
  P5  T10 / ST8  clash scan: SET jars, pack mods, SkyySkills' _spell_clash rule on our jar, the handover pair (pinned + partner jar).
          FIX ROUND: version-aware - before the pin bump the pinned SkyySkills (0.4.14) ships the 8 staffs and the partner 0.4.15 none;
          after it (SkyySkills >= 0.4.15 pinned) the PINNED jar must ship none, and a pinned SkyyArmory needs SkyyClasses >= 0.1.11
  P6  T11  art: skyyart verify, styles A and B, deterministic, the jar holds B, the blue quick-orb texture
  P7  T13 / ST9  the Mana rule from the SkyySkills jars' own default config text (0.4.14: no class row; 0.4.15: Priest 5 / Mage 10) -
          FIX ROUND: version-aware like P5 (after the pin bump the pinned jar's own rows give the pools)
JVM PART (one JVM: HytaleServer.jar + our jar + SkyyGear 0.2.1 + javassist)
  A   every class loads and verifies (-Xverify:all)                    X   MethodHandles.Lookup access audit of every reference
  E   engine stores: AssetRegistryLoader.init + the EntityStats / Interaction module stores + the 74 interaction codecs (read from
      InteractionModule.setup's bytecode) + the vanilla stat types
  D   T1 / ST1 / ST2  every generated asset decodes through the engine codecs: no exception, no validation failure, no unknown key;
      embedded recipes through CraftingRecipe.CODEC = the model shortbow's (a decode does not look references up - P1 and C do)
  C   FIX ROUND: the REAL engine compile - RootInteraction.build() of our 15 roots + the vanilla Wand_Primary root (our override) + every
      Parallel child root they fork, on the real stores: 0 "Missing interaction" warnings, no placeholder SendMessage step, the operation
      graph = the chain (Charging -> per key: the StatsCondition, its Parallel of cost / launch / effect, the Failed step); a NEGATIVE
      CONTROL (a Charging key naming a missing interaction) is caught
  R   T4 / T5 / ST4  read-back from the decoded objects (rawCosts + resolved costs, entityStatAssets + entityStats, getProjectileId, Charging
      next + sortedKeys) and the jumpToChargeValue rule on the engine's own sortedKeys
  J   T6 / ST5  projectile fields (damage, speeds, gravity, every other field = the resolved vanilla orb), the quick model's hitbox
  L   T-live / ST-live  the plugin's own ArmoryCheck.packCheck() on the REAL asset stores loaded with our pack: INFO; another pack winning +
      a wrong number: WARN; restored: INFO
  G   T8 / ST7  SkyyGear 0.2.1's real code on our ids: bands, isGear / isSpell / skyyItem / slotOf, kOf, mult, GearChg.launchCode on the real
      decoded chains (quick = 0, charged = 1, Wood wand via our Wand_Primary + SkyySkills' hold), spellRange = quick..charged x mult
  S   T6  ArmorySpawnSys / ArmorySpawn on a REAL Holder + ProjectileComponent (initialize + shoot from our decoded projectile): scale
      component, launch velocity 90 x speed / 3, untouched for charged ids / LOAD / part off / speed 3; FIX ROUND: the reach row on a REAL
      DespawnComponent (vanilla's now + 60 s) and a store holding a REAL TimeResource: quick orbs despawn at now + quick.life, charged /
      vanilla orbs / LOAD / part off / quick.life 60 / no store keep the vanilla 60 s
  U   T12  ArmoryTuneSys.handle on REAL Damage objects with a projectile source (per weapon, tune %, quick.damage, part off, foreign ids)
  K   T12  the config kit: rows, read-only rows, tset + its check hook, set / deny / reload through the kit's own op function
  B   bridge: armory:fn:info / wands / staffs / quick / loot / check (fix round: info carries the weapon's own charged + quick
      projectile ids as elements 6 + 7 - SkyyClasses raises the heal cap only for those)
  M   T12  the Mana check from a fake config:fn:SkyySkills (0.4.14 rows -> WARN, 0.4.15 rows -> INFO, no SkyySkills -> skip)
  T   the plugin's REAL setup() twice on a scratch COPY of the live world's mods folder: systems handed to the registry, bridge, kit,
      no churn (the second start changes no file), no other mod's file touched; shutdown unpublishes
  V   T14  the whole SET + SkyyArmory in ONE fresh JVM with -Xverify:all (every class linked = verified) - skipped with --no-set
"""
import os, sys, re, json, zipfile, math, shutil, time, struct, copy, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import skyyart as SA

VERSION = "0.1"
MOD = "SkyyArmory"
PKG = "com.skyy.armory."
PACK = "Skyy:0.1 SkyyArmory"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(arg("--dir", os.path.join(SCRATCH_ROOT, "armory01", "harness")))
_rel = os.path.relpath(SCRATCH, SCRATCH_ROOT).split(os.sep)
if not (SCRATCH + os.sep).startswith(SCRATCH_ROOT + os.sep) or len(_rel) < 2 or ".." in _rel:
    # a sub-folder of a task folder (tools/dev/scratch/<task>/<sub>): never a whole task folder - other agents' work sits next to it
    raise SystemExit("--dir must be a sub-folder of a task folder inside %s, e.g. tools/dev/scratch/<task>/harness (exactly that folder is "
                     "deleted afterwards)" % SCRATCH_ROOT)
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "%s-%s.jar" % (MOD, VERSION))))
KEEP = "--keep" in sys.argv
NO_SET = "--no-set" in sys.argv
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
LIVE = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods")
SET_FILE = os.path.realpath(arg("--set-file", os.path.join(TOOLS, "deploy_set.py")))
if SET_FILE != os.path.realpath(os.path.join(TOOLS, "deploy_set.py")):
    if not (SET_FILE + os.sep).startswith(SCRATCH_ROOT + os.sep):
        raise SystemExit("--set-file must be a copy of tools/deploy_set.py inside %s" % SCRATCH_ROOT)
    print("NOTE: SET pins read from %s (not tools/deploy_set.py)" % SET_FILE)
_dst = open(SET_FILE, encoding="utf-8").read()            # read only, never run
_s0 = _dst.index("SET = [")
PINS = re.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', _dst[_s0:_dst.index("\n]\n", _s0)])
PACKS = re.findall(r'"([^"]+:[^"]+)"', re.search(r"PACK_THIRD_PARTY = \[(.*?)\]", _dst).group(1))
PIN = dict(PINS)
SKILLS_PIN = PIN["SkyySkills"]
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-%s.jar" % SKILLS_PIN)
SKILLS_SCRIPT = os.path.join(ROOT, "SkyySkills", "build_skyyskills_%s.py" % SKILLS_PIN)
PARTNER = "0.4.15"
PARTNER_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-%s.jar" % PARTNER)
CLASSES_PARTNER = "0.1.11"


def vtuple(s):
    return tuple(int(x) for x in str(s).split("."))


POST_PIN = vtuple(SKILLS_PIN) >= vtuple(PARTNER)       # fix round: the planned pin bump is done (SkyySkills 0.4.15+ pinned)
PRE_SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.14.jar")          # the last SkyySkills before the handover
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-%s.jar" % PIN["SkyyGear"])
GEAR_SCRIPT = os.path.join(ROOT, "SkyyGear", "build_skyygear_%s.py" % PIN["SkyyGear"])

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def rhu(x):
    return int(math.floor(x + 0.5 + 1e-9))


# ============================================================================================================ P0. the tables (independent)
METALS = ["Wood", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
NEW = METALS[1:]
COST = dict(zip(METALS, [5, 10, 15, 25, 40, 60, 85, 85]))      # Skyy's numbers (LOCKED) + the proposal Skyy kept (85 / 17)
BANDS = {"Wood": (1, 13), "Copper": (10, 18), "Iron": (15, 23), "Thorium": (20, 28), "Cobalt": (25, 38), "Adamantite": (35, 43),
         "Mithril": (40, 49), "Onyxium": (40, 49)}
STAFF_BASE = 50          # the build's S1 default (the harness reads the jar's own numbers and compares them to this choice)


def wand_row(m):
    c = COST[m]
    k = 1.25 * (c / 5.0) - 0.25          # Skyy: damage multiple = 1.25 x cost multiple - 0.25
    return c, c // 5, k, rhu(25 * k), rhu(5 * k)


def staff_row(m):
    c = 2 * COST[m]
    k = 1.25 * (c / 10.0) - 0.25
    return c, c // 5, k, rhu(STAFF_BASE * k), rhu(STAFF_BASE / 5.0 * k)


W = dict((m, wand_row(m)) for m in METALS)
S = dict((m, staff_row(m)) for m in METALS)
check([(W[m][0], W[m][1]) for m in METALS[:3]] == [(5, 1), (10, 2), (15, 3)] and W["Copper"][2] == 2.25 and W["Iron"][2] == 3.5,
      "P0: Skyy's rungs Wood 5/1, Copper 10/2 (x2.25), Iron 15/3 (x3.5)")
check([(W[m][3], W[m][4]) for m in METALS] == [(25, 5), (56, 11), (88, 18), (150, 30), (244, 49), (369, 74), (525, 105), (525, 105)],
      "P0: wand damage charged / quick = spec 4.3")
check([(S[m][0], S[m][1], S[m][3], S[m][4]) for m in METALS] == [(10, 2, 50, 10), (20, 4, 113, 23), (30, 6, 175, 35), (50, 10, 300, 60),
      (80, 16, 488, 98), (120, 24, 738, 148), (170, 34, 1050, 210), (170, 34, 1050, 210)], "P0: staff ladder = spec 15.2 (base 50)")

if not os.path.isfile(JAR):
    raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.py (%s missing)" % JAR)
JZ = zipfile.ZipFile(JAR)
JN = JZ.namelist()
JSET = set(JN)
J = {}           # path -> parsed JSON (every Server JSON in the jar)
for n in JN:
    if n.startswith("Server/") and n.endswith((".json", ".particlesystem", ".particlespawner")):
        J[n] = json.loads(JZ.read(n).decode("utf-8"))


def by_dir(pre, ext=".json"):
    return dict((os.path.basename(n)[:-len(ext)], n) for n in JN if n.startswith(pre) and n.endswith(ext))


J_ITEMS = by_dir("Server/Item/Items/")
J_INTS = by_dir("Server/Item/Interactions/")
J_ROOTS = by_dir("Server/Item/RootInteractions/")
J_PRJ = by_dir("Server/Projectiles/")
J_MODELS = by_dir("Server/Models/")
J_TRAILS = by_dir("Server/Entity/Trails/")
J_PSYS = by_dir("Server/Particles/", ".particlesystem")
J_PSP = by_dir("Server/Particles/", ".particlespawner")
J_PNG = sorted(n for n in JN if n.endswith(".png"))
WID = dict((m, "Weapon_Wand_" + m) for m in METALS)
SID = dict((m, "Weapon_Staff_" + m) for m in METALS)
QORB = dict((m, "SkyyArmory_QuickOrb_" + m) for m in METALS)
ORB = dict((m, "SkyyArmory_Orb_" + m) for m in NEW)
SORB = dict((m, "SkyyArmory_StaffOrb_" + m) for m in METALS)
SQORB = dict((m, "SkyyArmory_StaffQuickOrb_" + m) for m in METALS)
VAN_ORB = "Skeleton_Mage_Corruption_Orb"
check(sorted(J_ITEMS) == sorted([WID[m] for m in NEW] + [SID[m] for m in METALS]), "P0: 15 items = 7 new wands + the 8 ladder staffs: %s" % sorted(J_ITEMS))
check(len(J_INTS) == 117 and len(J_ROOTS) == 15 and len(J_PRJ) == 31, "P0: 117 interactions, 15 roots, 31 projectiles (%d / %d / %d)" % (
    len(J_INTS), len(J_ROOTS), len(J_PRJ)))
check(sorted(J_PRJ) == sorted(list(ORB.values()) + list(QORB.values()) + list(SORB.values()) + list(SQORB.values())), "P0: projectile ids")
check(list(J_MODELS) == ["SkyyArmory_QuickOrb"] and list(J_TRAILS) == ["SkyyArmory_Orb_Trail_Blue"] and len(J_PSYS) == 3 and len(J_PSP) == 5,
      "P0: quick look = 1 model asset, 1 trail, 3 particle systems, 5 spawners")
check(len(J_PNG) == 15 and "Server/Languages/en-US/server.lang" in JSET and "manifest.json" in JSET, "P0: 15 PNGs (7 textures, 7 icons, 1 orb texture), lang, manifest")
check(all(k.startswith("SkyyArmory_") or k == "Wand_Primary" for k in list(J_INTS) + list(J_ROOTS)) and "Wand_Primary" in J_INTS
      and J_INTS["Wand_Primary"] == "Server/Item/Interactions/Weapons/Wand/Wand_Primary.json", "P0: every interaction / root id is SkyyArmory_* except the Wand_Primary override (vanilla path)")
check(all("skyy" not in i.lower() for i in J_ITEMS), "P0: no 'skyy' in any item id (SkyyGear GearData.skyyItem)")
MAN = json.loads(JZ.read("manifest.json").decode("utf-8"))
check("%s:%s" % (MAN["Group"], MAN["Name"]) == PACK and MAN["IncludesAssetPack"] is True and MAN["Main"] == "com.skyy.armory.SkyyArmoryPlugin",
      "P0: manifest = pack %s, asset pack, main class" % PACK)
JITEM = dict((i, J[p]) for i, p in J_ITEMS.items())
JINT = dict((i, J[p]) for i, p in J_INTS.items())
JROOT = dict((i, J[p]) for i, p in J_ROOTS.items())
JPRJ = dict((i, J[p]) for i, p in J_PRJ.items())
# the jar's own numbers vs the independent tables
for m in NEW:
    c, q, k, cd, qd = W[m]
    check(JINT["SkyyArmory_Wand_Cast_" + m]["Costs"] == {"Mana": c} and JINT["SkyyArmory_Wand_Cast_Cost_" + m]["StatModifiers"] == {"Mana": -c}
          and JINT["SkyyArmory_Wand_Quick_" + m]["Costs"] == {"Mana": q} and JINT["SkyyArmory_Wand_Quick_Cost_" + m]["StatModifiers"] == {"Mana": -q}
          and JPRJ[ORB[m]]["Damage"] == cd and JPRJ[QORB[m]]["Damage"] == qd, "P0: %s wand %d/%d Mana, %d/%d damage in the jar" % (m, c, q, cd, qd))
for m in METALS:
    c, q, k, cd, qd = S[m]
    check(JINT["SkyyArmory_Staff_Cast_" + m]["Costs"] == {"Mana": c} and JINT["SkyyArmory_Staff_Cast_Cost_" + m]["StatModifiers"] == {"Mana": -c}
          and JINT["SkyyArmory_Staff_Quick_" + m]["Costs"] == {"Mana": q} and JPRJ[SORB[m]]["Damage"] == cd and JPRJ[SQORB[m]]["Damage"] == qd,
          "P0: %s staff %d/%d Mana, %d/%d damage in the jar" % (m, c, q, cd, qd))
check(JINT["SkyyArmory_Wand_Quick_Wood"]["Costs"] == {"Mana": 1} and JPRJ[QORB["Wood"]]["Damage"] == 5, "P0: Wood wand tap 1 Mana, 5 damage")
print("P0. tables + listing: %d items, %d interactions, %d roots, %d projectiles, %d PNGs" % (len(J_ITEMS), len(J_INTS), len(J_ROOTS), len(J_PRJ), len(J_PNG)))

# ============================================================================================================ Assets.zip (read only)
AZ = zipfile.ZipFile(AZ_PATH)
AZN = AZ.namelist()
AZS = set(AZN)
AIDX = {}
for n in AZN:
    if not n.startswith("Server/"):
        continue
    for pre, kind, ext in (("Server/Item/Items/", "item", ".json"), ("Server/Item/Interactions/", "int", ".json"),
                           ("Server/Item/RootInteractions/", "root", ".json"), ("Server/Projectiles/", "prj", ".json"),
                           ("Server/Models/", "model", ".json"), ("Server/Entity/Trails/", "trail", ".json"),
                           ("Server/Audio/SoundEvents/", "sound", ".json"), ("Server/Item/Animations/", "anim", ".json"),
                           ("Server/Item/Qualities/", "quality", ".json"), ("Server/Item/ResourceTypes/", "rtype", ".json"),
                           ("Server/Audio/ItemSounds/", "iss", ".json"), ("Server/Particles/", "psys", ".particlesystem"),
                           ("Server/Particles/", "pspawn", ".particlespawner"), ("Server/Entity/Stats/", "stat", ".json"),
                           ("Server/Item/Recipes/", "recipe", ".json")):
        if n.startswith(pre) and n.endswith(ext):
            AIDX.setdefault(kind, {})[os.path.basename(n)[:-len(ext)]] = n
AJ = {}


def aj(kind, aid):
    p = AIDX[kind][aid]
    if p not in AJ:
        AJ[p] = json.loads(AZ.read(p).decode("utf-8-sig"))
    return AJ[p]


def ahas(kind, aid):
    return aid in AIDX.get(kind, {})


def aresolve(kind, aid):
    d = aj(kind, aid)
    if not d.get("Parent"):
        return dict(d)
    base = aresolve(kind, d["Parent"])
    for k, v in d.items():
        if k != "Parent":
            base[k] = v
    return base


SKZ = zipfile.ZipFile(SKILLS_JAR)
SK = {}
for n in SKZ.namelist():
    if n.startswith("Server/") and n.endswith(".json"):
        SK[n] = json.loads(SKZ.read(n).decode("utf-8-sig"))
SK_INTS = dict((os.path.basename(n)[:-5], d) for n, d in SK.items() if n.startswith("Server/Item/Interactions/"))
SK_ITEMS = dict((os.path.basename(n)[:-5], d) for n, d in SK.items() if n.startswith("Server/Item/Items/"))
# the three wood-tier wands as the game loads them (SkyySkills' overrides) WITHOUT the Sword_Swing_* vars: our Wand_Primary override took
# the swing Chaining away, so nothing reaches those vars any more (P2 proves the two casts); loading them would only drag the sword
# swing's effects (trails, sounds) into the bare-JVM stores
WOOD3 = {}
for _i in ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"):
    _d = copy.deepcopy(SK_ITEMS[_i])
    _d["InteractionVars"] = dict((k, v) for k, v in _d["InteractionVars"].items() if not k.startswith("Sword_Swing_"))
    WOOD3[_i] = _d
check(sorted(SK_INTS) == sorted(["Wand_Cast_Left_Charged", "Wand_Cast_Cost", "Staff_Cast_Summon_Charged", "Staff_Cast_Cost", "Spellbook_Cast_Hurl_Charged",
                                 "Spellbook_Cast_Cost", "Gun_Shoot_Flintlock_Charged", "Gun_Shoot_Cost"]), "pinned SkyySkills %s: its 8 interaction overrides" % SKILLS_PIN)
# bench ids + categories (a bench is a BlockType with Bench data inside an item JSON)
BENCH = {}
for i, p in AIDX["item"].items():
    d = aj("item", i)
    bt = d.get("BlockType") if isinstance(d, dict) else None
    b = bt.get("Bench") if isinstance(bt, dict) else None
    if isinstance(b, dict) and b.get("Id"):
        cats = BENCH.setdefault(b["Id"], set())
        for c in b.get("Categories") or []:
            if isinstance(c, dict) and c.get("Id"):
                cats.add(c["Id"])

# ============================================================================================================ P1. T2 reference closure
REF_KEYS = ("Next", "Failed", "Interactions")


def str_refs(x, out):
    """every interaction / root id a generated interaction names (strings under Next / Failed / Interactions, incl. Charging key maps)"""
    if isinstance(x, str):
        out.add(x)
    elif isinstance(x, list):
        for e in x:
            str_refs(e, out)
    elif isinstance(x, dict):
        for k, v in x.items():
            if k in REF_KEYS:
                if isinstance(v, dict) and "Type" not in v and "Interactions" not in v:
                    for vv in v.values():
                        str_refs(vv, out)
                else:
                    str_refs(v, out)
    return out


SKILLS8 = set(SK_INTS)
QM = J[J_MODELS["SkyyArmory_QuickOrb"]]


def closure_bad(JINT, JROOT, JPRJ, JITEM, QM):
    """P1: every broken reference of the given asset tables (fix round: a function, so the negative controls below run the SAME code)"""
    bad = []
    for i, d in JINT.items():
        for r in str_refs(d, set()):
            if r in SKILLS8 and not (i == "Wand_Primary" and r == "Wand_Cast_Left_Charged"):
                bad.append("%s names SkyySkills' %s" % (i, r))
            if r == "Staff_Primary":
                bad.append("%s names Staff_Primary" % i)
            if r not in JINT and r not in JROOT and not ahas("int", r) and not ahas("root", r):
                bad.append("%s -> unknown %s" % (i, r))
        t = d.get("Type")
        if t == "LaunchProjectile" and d["ProjectileId"] not in JPRJ and not ahas("prj", d["ProjectileId"]):
            bad.append("%s launches unknown %s" % (i, d["ProjectileId"]))
        e = d.get("Effects") or {}
        if e.get("WorldSoundEventId") and not ahas("sound", e["WorldSoundEventId"]):
            bad.append("%s: sound %s" % (i, e["WorldSoundEventId"]))
        if e.get("ItemAnimationId"):
            sets = ("Wand",) if "_Wand_" in i or i == "Wand_Primary" else ("Staff",)
            if not any(e["ItemAnimationId"] in aresolve("anim", s)["Animations"] or e["ItemAnimationId"] in aresolve("anim", "Sword").get("Animations", {})
                       or e["ItemAnimationId"] == "Interact" for s in sets):
                bad.append("%s: animation %s not in %s" % (i, e["ItemAnimationId"], sets))
        for st in list((d.get("Costs") or {}).keys()) + list((d.get("StatModifiers") or {}).keys()):
            if not ahas("stat", st):
                bad.append("%s: stat %s" % (i, st))
    for r, d in JROOT.items():
        bad += ["root %s -> %s" % (r, x) for x in d["Interactions"] if x not in JINT]
    for p, d in JPRJ.items():
        if d["Appearance"] not in J_MODELS and not ahas("model", d["Appearance"]):
            bad.append("%s: model %s" % (p, d["Appearance"]))
        for k in ("HitParticles", "DeathParticles"):
            s = d[k]["SystemId"]
            if s not in J_PSYS and not ahas("psys", s):
                bad.append("%s: particle system %s" % (p, s))
        for k in ("HitSoundEventId", "MissSoundEventId"):
            if not ahas("sound", d[k]):
                bad.append("%s: sound %s" % (p, d[k]))
    for f in [QM["Model"], QM["Texture"]] + [a["Model"] for a in QM["DefaultAttachments"]] + [a["Texture"] for a in QM["DefaultAttachments"]]:
        if ("Common/" + f) not in AZS and ("Common/" + f) not in JSET:
            bad.append("quick model file %s" % f)
    for pp in QM["Particles"]:
        if pp["SystemId"] not in J_PSYS and not ahas("psys", pp["SystemId"]):
            bad.append("quick model particle %s" % pp["SystemId"])
    for t in QM["Trails"]:
        if t["TrailId"] not in J_TRAILS and not ahas("trail", t["TrailId"]):
            bad.append("quick model trail %s" % t["TrailId"])
    for s, p in J_PSYS.items():
        for sp in J[p]["Spawners"]:
            if sp["SpawnerId"] not in J_PSP and not ahas("pspawn", sp["SpawnerId"]):
                bad.append("%s spawner %s" % (s, sp["SpawnerId"]))
    for s, p in J_PSP.items():
        tx = (J[p].get("Particle") or {}).get("Texture")
        if tx and ("Common/" + tx) not in AZS:
            bad.append("%s texture %s" % (s, tx))
    for t, p in J_TRAILS.items():
        tp = J[p].get("TexturePath")
        if tp and ("Common/" + tp) not in AZS:
            bad.append("%s texture %s" % (t, tp))
    for i, d in JITEM.items():
        for slot, rid in d["Interactions"].items():
            if rid not in JROOT:
                bad.append("%s %s -> %s" % (i, slot, rid))
        for f in ("Icon", "Texture", "Model"):
            if d.get(f) and ("Common/" + d[f]) not in AZS and ("Common/" + d[f]) not in JSET:
                bad.append("%s %s %s" % (i, f, d[f]))
        if not ahas("quality", d["Quality"]):
            bad.append("%s quality %s" % (i, d["Quality"]))
        if not ahas("iss", d["ItemSoundSetId"]) and d["ItemSoundSetId"] not in AIDX.get("iss", {}):
            bad.append("%s sound set %s" % (i, d["ItemSoundSetId"]))
        if not ahas("anim", d["PlayerAnimationsId"]):
            bad.append("%s animations %s" % (i, d["PlayerAnimationsId"]))
        for pp in d.get("Particles") or []:
            if not ahas("psys", pp["SystemId"]):
                bad.append("%s particle %s" % (i, pp["SystemId"]))
        r = d.get("Recipe")
        if r:
            for x in r["Input"]:
                if x.get("ItemId") and not ahas("item", x["ItemId"]):
                    bad.append("%s input %s" % (i, x["ItemId"]))
                if x.get("ResourceTypeId") and not ahas("rtype", x["ResourceTypeId"]):
                    bad.append("%s resource %s" % (i, x["ResourceTypeId"]))
            for b in r["BenchRequirement"]:
                if b["Id"] not in BENCH or any(c not in BENCH[b["Id"]] for c in b.get("Categories") or []):
                    bad.append("%s bench %s %s" % (i, b["Id"], b.get("Categories")))
    return bad


bad = closure_bad(JINT, JROOT, JPRJ, JITEM, QM)
check(not bad, "P1 (T2): reference closure - every id / file / bench / category an asset names exists (jar or Assets.zip): %s" % bad[:8])
# FIX ROUND (review: the engine decode in D does not look references up - a missing sound, projectile, stat or Charging target decodes "ok"):
# one NEGATIVE CONTROL per reference class - a deep copy of our tables with ONE broken reference must be caught by the same closure code,
# naming the broken id. The real engine compile in C covers the interaction graph a second time.


def mutant(fn):
    t = copy.deepcopy((JINT, JROOT, JPRJ, JITEM, QM))
    fn(*t)
    return closure_bad(*t)


NEG = [
    ("a Charging key -> a missing interaction", "No_Such_Interaction", lambda i, r, p, it, q: i["SkyyArmory_Wand_Primary_Copper"]["Next"].__setitem__("0", "No_Such_Interaction")),
    ("a Parallel child -> a missing interaction", "No_Such_Cost",
     lambda i, r, p, it, q: i["SkyyArmory_Wand_Cast_Copper"]["Next"]["Interactions"][0].__setitem__("Interactions", ["No_Such_Cost"])),
    ("a Failed branch -> a missing interaction", "No_Such_Fail", lambda i, r, p, it, q: i["SkyyArmory_Staff_Quick_Iron"].__setitem__("Failed", "No_Such_Fail")),
    ("a root -> a missing interaction", "No_Such_Root_Step", lambda i, r, p, it, q: r["SkyyArmory_Staff_Primary_Wood"].__setitem__("Interactions", ["No_Such_Root_Step"])),
    ("a launch -> a missing projectile", "Nope_Projectile", lambda i, r, p, it, q: i["SkyyArmory_Wand_Cast_Launch_Copper"].__setitem__("ProjectileId", "Nope_Projectile")),
    ("a missing sound event", "SFX_Does_Not_Exist_At_All",
     lambda i, r, p, it, q: i["SkyyArmory_Wand_Cast_Effect"]["Effects"].__setitem__("WorldSoundEventId", "SFX_Does_Not_Exist_At_All")),
    ("a cost on a missing stat", "NotAStat", lambda i, r, p, it, q: i["SkyyArmory_Wand_Cast_Copper"].__setitem__("Costs", {"NotAStat": 10})),
    ("a spend on a missing stat", "NoSuchStat", lambda i, r, p, it, q: i["SkyyArmory_Staff_Cast_Cost_Iron"].__setitem__("StatModifiers", {"NoSuchStat": -30})),
    ("a missing item animation", "NoSuchAnim", lambda i, r, p, it, q: i["SkyyArmory_Wand_Quick_Launch_Iron"]["Effects"].__setitem__("ItemAnimationId", "NoSuchAnim")),
    ("SkyySkills' charged step named by a metal wand", "Wand_Cast_Left_Charged",
     lambda i, r, p, it, q: i["SkyyArmory_Wand_Primary_Iron"]["Next"].__setitem__("0.35", "Wand_Cast_Left_Charged")),
    ("a projectile on a missing model", "No_Such_Model", lambda i, r, p, it, q: p["SkyyArmory_Orb_Copper"].__setitem__("Appearance", "No_Such_Model")),
    ("a projectile hit on a missing particle system", "No_Such_Particles",
     lambda i, r, p, it, q: p["SkyyArmory_QuickOrb_Mithril"]["HitParticles"].__setitem__("SystemId", "No_Such_Particles")),
    ("a projectile on a missing hit sound", "SFX_No_Hit", lambda i, r, p, it, q: p["SkyyArmory_StaffOrb_Wood"].__setitem__("HitSoundEventId", "SFX_No_Hit")),
    ("an item slot -> a missing root", "No_Such_Root", lambda i, r, p, it, q: it["Weapon_Wand_Copper"]["Interactions"].__setitem__("Primary", "No_Such_Root")),
    ("an item on a missing texture", "Items/Weapons/Wand/Nope.png", lambda i, r, p, it, q: it["Weapon_Wand_Iron"].__setitem__("Texture", "Items/Weapons/Wand/Nope.png")),
    ("a recipe on a missing bench", "No_Such_Bench", lambda i, r, p, it, q: it["Weapon_Wand_Iron"]["Recipe"]["BenchRequirement"][0].__setitem__("Id", "No_Such_Bench")),
    ("a recipe on a missing input item", "Ingredient_Bar_Nope",
     lambda i, r, p, it, q: it["Weapon_Staff_Onyxium"]["Recipe"]["Input"][0].__setitem__("ItemId", "Ingredient_Bar_Nope")),
    ("the quick model on a missing trail", "No_Such_Trail", lambda i, r, p, it, q: q["Trails"][0].__setitem__("TrailId", "No_Such_Trail")),
]
neg_miss = []
for what, needle, fn in NEG:
    got = mutant(fn)
    if not any(needle in x for x in got):
        neg_miss.append("%s (%s): %s" % (what, needle, got[:3]))
check(not neg_miss and closure_bad(JINT, JROOT, JPRJ, JITEM, QM) == [],
      "P1 (fix round): %d negative controls - every broken reference class is caught by the closure (and the real tables still pass): %s" % (
          len(NEG), neg_miss))
print("P1. reference closure: %d interactions, %d roots, %d projectiles, %d items, the quick look - all references resolve; %d negative controls caught" % (
    len(JINT), len(JROOT), len(JPRJ), len(JITEM), len(NEG)))

# ============================================================================================================ P2. T3 / ST3 SkyySkills' gate simulation
src = open(SKILLS_SCRIPT, encoding="utf-8").read()
blk = src[src.index("# >>> SPELL GEN"):src.index("# <<< SPELL GEN")]
SG = {}
exec(blk, SG)
spell_casts = SG["spell_casts"]
INTS_ALL = {}
for i, p in AIDX["int"].items():
    INTS_ALL[i] = aj("int", i)
for i, d in SK_INTS.items():
    INTS_ALL[i] = d
for i, d in JINT.items():
    INTS_ALL[i] = d
ROOTS_ALL = dict((i, aj("root", i)) for i in AIDX["root"])
for i, d in JROOT.items():
    ROOTS_ALL[i] = d


def casts_of(item):
    r = spell_casts(item, INTS_ALL, ROOTS_ALL)
    cs = sorted((c[0], c[1], sorted(s[0] for s in c[2])) for c in r["casts"])
    return cs, r


for m in NEW:
    c, q = W[m][0], W[m][1]
    cs, r = casts_of(JITEM[WID[m]])
    check(cs == sorted([(q, ("int", "SkyyArmory_Wand_Quick_" + m), [-q]), (c, ("int", "SkyyArmory_Wand_Cast_" + m), [-c])]) and not r["free"]
          and not r["fail"] and not r["gain"], "P2 (T3): %s wand - tap checks %d spends %d, hold checks %d spends %d, nothing free / on Failed: %s" % (
              m, q, q, c, c, cs))
for m in METALS:
    c, q = S[m][0], S[m][1]
    cs, r = casts_of(JITEM[SID[m]])
    check(cs == sorted([(q, ("int", "SkyyArmory_Staff_Quick_" + m), [-q]), (c, ("int", "SkyyArmory_Staff_Cast_" + m), [-c])]) and not r["free"]
          and not r["fail"] and not r["gain"], "P2 (ST3): %s staff - tap %d / %d, hold %d / %d (2 x the wand), no free spend: %s" % (m, q, q, c, c, cs))
for iid in ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"):
    cs, r = casts_of(SK_ITEMS[iid])           # SkyySkills' item override (the file the game loads) through our Wand_Primary
    check(len(cs) == 2 and cs[0][:2] == (1, ("int", "SkyyArmory_Wand_Quick_Wood")) and cs[0][2] == [-1]
          and cs[1][0] == 5 and cs[1][1] == ("int", "Wand_Cast_Left_Charged") and cs[1][2] == [-5] and not r["free"] and not r["fail"],
          "P2 (T3): %s - tap checks 1 spends 1 (our quick shot), hold checks 5 spends 5 (SkyySkills' rung): %s" % (iid, cs))
print("P2. SkyySkills' own gate simulation (%s script): 7 wands, 8 staffs, 3 wood-tier wands - every cast checks what it spends" % SKILLS_PIN)


# ============================================================================================================ P3. keys + cadence
def jump(keys, v):
    """ChargingInteraction.jumpToChargeValue: the key with the smallest (value - key) >= 0 (index into the sorted keys), -1 = none"""
    best, bi = 2147483648.0, -1
    for i, k in enumerate(keys):
        if v < k:
            continue
        d = v - k
        if bi == -1 or d < best:
            best, bi = d, i
    return bi


for m in NEW:
    ch = JINT["SkyyArmory_Wand_Primary_" + m]
    ks = sorted(float(k) for k in ch["Next"])
    picks = [ch["Next"][("%g" % ks[jump(ks, v)]) if ks[jump(ks, v)] != 0.0 else "0"] for v in (0.0, 0.1, 0.34, 0.35, 2.0)]
    check(ks == [0.0, 0.35] and picks == ["SkyyArmory_Wand_Quick_" + m] * 3 + ["SkyyArmory_Wand_Cast_" + m] * 2,
          "P3 (T5): %s wand keys {0, 0.35}; 0 / 0.1 / 0.34 -> quick, 0.35 / 2.0 -> charged" % m)
for m in METALS:
    ch = JINT["SkyyArmory_Staff_Primary_" + m]
    ks = sorted(float(k) for k in ch["Next"])
    picks = [ch["Next"]["0" if ks[jump(ks, v)] == 0.0 else "1"] for v in (0.0, 0.5, 0.99, 1.0, 3.0)]
    check(ks == [0.0, 1.0] and picks == ["SkyyArmory_Staff_Quick_" + m] * 3 + ["SkyyArmory_Staff_Cast_" + m] * 2,
          "P3 (ST4): %s staff keys {0, 1}; 0 / 0.5 / 0.99 -> quick, 1.0 / 3.0 -> charged" % m)
VWP = aj("int", "Wand_Primary")
WP = JINT["Wand_Primary"]
a_, b_ = copy.deepcopy(VWP), copy.deepcopy(WP)
a_["Next"].pop("0")
b_["Next"].pop("0")
check(a_ == b_ and WP["Next"]["0"] == "SkyyArmory_Wand_Quick_Wood" and WP["Next"]["0.35"] == "Wand_Cast_Left_Charged",
      "P3 (2.4): the Wand_Primary override = vanilla except Next['0'] (the free swing -> the 1-Mana quick shot); the hold stays SkyySkills'")
check(VWP["Next"]["0"] == {"Type": "Chaining", "ChainingAllowance": 1.25, "Next": ["Sword_Swing_Left_Fast", "Sword_Swing_Right_Fast"]},
      "P3: the vanilla Wand_Primary tap is still the sword-swing Chaining (the shape the override replaces)")


def dur(x, vars_, ints, depth=0):
    if depth > 60:
        raise SystemExit("cadence: too deep")
    if isinstance(x, str):
        if x in ints:
            return dur(ints[x], vars_, ints, depth + 1)
        if x in ROOTS_ALL:
            return dur(ROOTS_ALL[x], vars_, ints, depth + 1)
        raise SystemExit("cadence: unknown " + x)
    if isinstance(x, list):
        return sum(dur(e, vars_, ints, depth + 1) for e in x)
    if not isinstance(x, dict):
        return 0.0
    if "Parent" in x and "Type" not in x:
        base = dict(ints[x["Parent"]])
        base.update(dict((k, v) for k, v in x.items() if k != "Parent"))
        x = base
    t = x.get("Type")
    if t is None and "Interactions" in x:
        return dur(x["Interactions"], vars_, ints, depth + 1)
    if t == "Replace":
        return dur(vars_.get(x["Var"], x.get("DefaultValue")), vars_, ints, depth + 1)
    if t == "Parallel":
        return max(dur(e, vars_, ints, depth + 1) for e in x["Interactions"])
    return float(x.get("RunTime", 0.0)) + (dur(x["Next"], vars_, ints, depth + 1) if x.get("Next") is not None else 0.0)


VANI = dict((i, aj("int", i)) for i in AIDX["int"])
vw = aj("item", "Weapon_Wand_Wood")
vs = aj("item", "Weapon_Staff_Wood")
tap_w = max(dur("Sword_Swing_Left_Fast", vw["InteractionVars"], VANI), dur("Sword_Swing_Right_Fast", vw["InteractionVars"], VANI))
tap_s = max(dur("Spear_Swing_Left", vs["InteractionVars"], VANI), dur("Spear_Swing_Right", vs["InteractionVars"], VANI))
cast_w = dur("Wand_Cast_Left_Charged", vw["InteractionVars"], VANI)
cast_s = dur("Staff_Cast_Summon_Charged", vs["InteractionVars"], VANI)
for m in NEW:
    q_ = dur("SkyyArmory_Wand_Quick_" + m, {}, INTS_ALL)
    c_ = dur("SkyyArmory_Wand_Cast_" + m, {}, INTS_ALL)
    check(q_ >= tap_w - 1e-9 and abs(c_ - cast_w) < 1e-9, "P3 (T7): %s wand tap %.3f s >= vanilla tap %.3f s, charged %.3f s = vanilla %.3f s" % (m, q_, tap_w, c_, cast_w))
for m in METALS:
    q_ = dur("SkyyArmory_Staff_Quick_" + m, {}, INTS_ALL)
    c_ = dur("SkyyArmory_Staff_Cast_" + m, {}, INTS_ALL)
    check(q_ >= tap_s - 1e-9 and abs(c_ - cast_s) < 1e-9, "P3 (ST6): %s staff tap %.3f s >= vanilla %.3f s, charged %.3f s = vanilla %.3f s" % (m, q_, tap_s, c_, cast_s))
check(abs(dur("SkyyArmory_Wand_Quick_Wood", {}, INTS_ALL) - 0.35) < 1e-9 and abs(tap_w - 0.346) < 1e-9 and abs(tap_s - 0.557) < 1e-9,
      "P3: Wood tap 0.35 s; vanilla taps 0.346 s (wand) / 0.557 s (staff)")
print("P3. keys + cadence: wand tap 0.35 s >= %.3f, staff tap 0.56 s >= %.3f, charged chains = vanilla" % (tap_w, tap_s))


# ============================================================================================================ P4. recipes + staff overrides
def model_recipe(metal):
    r = copy.deepcopy(aj("item", "Weapon_Shortbow_" + metal)["Recipe"])
    r["BenchRequirement"] = [b for b in r["BenchRequirement"] if b.get("Id") != "Armory"]
    return r


onyx = model_recipe("Mithril")
for x in onyx["Input"]:
    if x.get("ItemId") == "Ingredient_Bar_Mithril":
        x["ItemId"] = "Ingredient_Bar_Onyxium"
for m in NEW:
    want = onyx if m == "Onyxium" else model_recipe(m)
    check(JITEM[WID[m]].get("Recipe") == want, "P4 (T9): %s wand recipe = the %s shortbow recipe minus the Armory bench%s" % (
        m, "Mithril" if m == "Onyxium" else m, " with Onyxium bars" if m == "Onyxium" else ""))
check(aj("item", "Weapon_Shortbow_Onyxium").get("Recipe") is None and onyx["Input"][0] == {"ItemId": "Ingredient_Bar_Onyxium", "Quantity": 6},
      "P4: vanilla's Onyxium shortbow has no recipe; ours uses 6 Onyxium bars (Skyy's answer)")
check([b["RequiredTierLevel"] if "RequiredTierLevel" in b else 1 for m in NEW for b in JITEM[WID[m]]["Recipe"]["BenchRequirement"]] == [1, 1, 2, 2, 3, 3, 3]
      and all(b["Id"] == "Weapon_Bench" and b["Categories"] == ["Weapon_Bow"] for m in NEW for b in JITEM[WID[m]]["Recipe"]["BenchRequirement"]),
      "P4: every wand at the Weapon Bench > Bow tab, tiers 1 1 2 2 3 3 3")
GZ = zipfile.ZipFile(GEAR_JAR)
gear_recipes = sorted(os.path.basename(n)[:-5] for n in GZ.namelist() if n.startswith("Server/Item/Recipes/"))
check(gear_recipes == sorted("SkyyGear_Recipe_" + i for i in ["Weapon_Wand_Wood"] + [SID[m] for m in METALS[:-1]]),
      "P4 (ST8): SkyyGear %s owns the Wood wand + 7 staff recipes (Wood ... Mithril), none for Onyxium: %s" % (PIN["SkyyGear"], gear_recipes))
for m in METALS:
    v = aj("item", SID[m])
    o = JITEM[SID[m]]
    rest_v = dict((k, x) for k, x in v.items() if k not in ("Interactions", "InteractionVars"))
    rest_o = dict((k, x) for k, x in o.items() if k not in ("Interactions", "InteractionVars", "Recipe"))
    check(rest_v == rest_o and o["Interactions"] == {"Primary": "SkyyArmory_Staff_Primary_" + m, "Secondary": "SkyyArmory_Staff_Primary_" + m}
          and "InteractionVars" not in o and (("Recipe" in o) == (m == "Onyxium")),
          "P4 (ST1): %s staff = vanilla except Primary / Secondary -> our root, no InteractionVars%s" % (m, ", + the Onyxium recipe" if m == "Onyxium" else ""))
check(JITEM[SID["Onyxium"]]["Recipe"] == onyx, "P4 (ST8): the Onyxium staff recipe = the Onyxium wand's (Mithril shortbow, Onyxium bars)")
avail = set()
for i in AIDX["item"]:
    if isinstance(aj("item", i).get("Recipe"), dict):
        avail.add(i + "_Recipe_Generated_0")
avail |= set(AIDX.get("recipe", {}))
mine_r = [i + "_Recipe_Generated_0" for i in JITEM if "Recipe" in JITEM[i]]
check(len(mine_r) == 8 and not set(mine_r) & avail, "P4: 8 embedded recipes (7 wands + the Onyxium staff), no recipe id taken in Assets.zip")
print("P4. recipes: 7 wands + the Onyxium staff = shortbow recipes (Armory dropped); 8 staff overrides = vanilla except the chain")

# ============================================================================================================ P5. T10 / ST8 clash scan


def asset_key(n):
    if n.startswith("Common/"):
        return ("common", n)
    for pre, k in (("Server/Item/Items/", "item"), ("Server/Item/Interactions/", "int"), ("Server/Item/RootInteractions/", "root"),
                   ("Server/Projectiles/", "prj"), ("Server/Models/", "model"), ("Server/Entity/Trails/", "trail")):
        if n.startswith(pre) and n.endswith(".json"):
            return (k, os.path.basename(n)[:-5])
    if n.startswith("Server/Particles/") and n.endswith((".particlesystem", ".particlespawner")):
        return ("p", os.path.basename(n).rsplit(".", 1)[0])
    return None


OURK = set(k for k in (asset_key(n) for n in JN) if k is not None)
STAFFK = set(("item", SID[m]) for m in METALS)
OURX = OURK - STAFFK
checked = []
for mod, ver in PINS:
    if mod == MOD:
        continue
    jp = os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver))
    if not os.path.isfile(jp):
        continue
    with zipfile.ZipFile(jp) as z_:
        ks = set(k for k in (asset_key(n) for n in z_.namelist()) if k is not None)
    check(not (OURX & ks) and (not (STAFFK & ks) or mod == "SkyySkills"), "P5 (T10): SET %s %s ships no SkyyArmory asset %s" % (mod, ver, sorted(OURX & ks)[:4]))
    checked.append(mod)
with zipfile.ZipFile(SKILLS_JAR) as z_:
    skn = z_.namelist()
pin_staffs = sorted(n for n in skn if asset_key(n) in STAFFK)
if POST_PIN:
    # fix round (review: the planned pin bump turned this harness red for the wrong reason): after the bump the PINNED jar is the handover
    # partner - it ships none of the 8 staffs, and the pair is pinned together (the build stops on a partial pin; deploy_set needs the same)
    check(not pin_staffs, "P5 (ST8): pinned SkyySkills %s (the handover is done) ships none of the 8 staff files: %s" % (SKILLS_PIN, pin_staffs))
    check(PIN.get(MOD) == VERSION, "P5 (pair): SkyySkills %s is pinned, so SkyyArmory %s must be pinned in the same SET: %s" % (SKILLS_PIN, VERSION, PIN.get(MOD)))
else:
    check(len(pin_staffs) == 8, "P5 (ST8): pinned SkyySkills %s still ships the 8 staff files (handover partner needed): %d" % (SKILLS_PIN, len(pin_staffs)))
    check(PIN.get(MOD) is None, "P5 (pair): SkyyArmory is not pinned while SkyySkills %s (no handover) is: %s" % (SKILLS_PIN, PIN.get(MOD)))
if PIN.get(MOD) == VERSION:
    check(vtuple(PIN.get("SkyyClasses", "0")) >= vtuple(CLASSES_PARTNER) and POST_PIN,
          "P5 (pair): a pinned SkyyArmory %s has SkyySkills %s+ and SkyyClasses %s+ beside it (pinned: %s / %s)" % (
              VERSION, PARTNER, CLASSES_PARTNER, SKILLS_PIN, PIN.get("SkyyClasses")))
if os.path.isfile(PARTNER_JAR):
    with zipfile.ZipFile(PARTNER_JAR) as z_:
        pn = z_.namelist()
    pks = set(k for k in (asset_key(n) for n in pn) if k is not None)
    check(not (pks & STAFFK) and not (pks & OURX), "P5 (ST8): partner SkyySkills %s ships none of the 8 staff files and no SkyyArmory id" % PARTNER)
    # SkyySkills' own _spell_clash rule (its files, its item ids, its 8 interaction ids) on OUR jar - the 8 ARMORY_OWNED staffs excepted
    p_items = set(os.path.basename(n)[:-5] for n in pn if n.startswith("Server/Item/Items/"))
    p_ints = set(os.path.basename(n)[:-5] for n in pn if n.startswith("Server/Item/Interactions/"))
    p_files = set(n for n in pn if n.startswith("Server/"))
    hit = sorted(n for n in JN if n in p_files or (n.startswith("Server/Item/Items/") and os.path.basename(n)[:-5] in p_items)
                 or (n.startswith("Server/Item/Interactions/") and os.path.basename(n)[:-5] in p_ints))
    check(not hit, "P5 (T10): SkyySkills %s's clash rule finds nothing in our jar: %s" % (PARTNER, hit[:4]))
    psrc = open(os.path.join(ROOT, "SkyySkills", "build_skyyskills_%s.py" % PARTNER), encoding="utf-8").read()
    check('"SkyyArmory_Staff_Cast_Wood"' in psrc and '"SkyyArmory_Staff_Cast_Cost_Wood"' in psrc and "armory:fn:info" in psrc
          and JINT["SkyyArmory_Staff_Cast_Wood"]["Costs"] == {"Mana": 10} and JINT["SkyyArmory_Staff_Cast_Cost_Wood"]["StatModifiers"] == {"Mana": -10},
          "P5: the partner's contract - it reads our SkyyArmory_Staff_Cast_Wood (check 10) / _Cost_Wood (spend 10) and armory:fn:info")
else:
    print("P5. NOTE partner SkyySkills %s not built - the handover pair is checked by its own harness" % PARTNER)
check(not [n for n in JN if os.path.basename(n)[:-5] in ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal")]
      and not [n for n in JN if n.startswith("Server/Item/Interactions/") and os.path.basename(n)[:-5] in SKILLS8],
      "P5 (T10): our jar ships none of SkyySkills' wood wands or its 8 interactions")
pk_found, others = [], []
for f in (sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []):
    p = os.path.join(B.MODS_DIR, f)
    try:
        if os.path.isdir(p):
            man = json.loads(open(os.path.join(p, "manifest.json"), "rb").read().decode("utf-8-sig"))
            nm = [os.path.relpath(os.path.join(r_, x), p).replace(os.sep, "/") for r_, _d, fl in os.walk(p) for x in fl]
        elif f.lower().endswith((".zip", ".jar")):
            with zipfile.ZipFile(p) as mz:
                man = json.loads(mz.read("manifest.json").decode("utf-8-sig"))
                nm = mz.namelist()
        else:
            continue
    except Exception:
        continue
    if not isinstance(man, dict) or str(man.get("Group")) == "Skyy":
        continue
    key = "%s:%s" % (man.get("Group"), man.get("Name"))
    ks = set(k for k in (asset_key(n) for n in nm) if k is not None)
    wp = [n for n in nm if os.path.basename(n) == "Wand_Primary.json"]
    if key in PACKS:
        pk_found.append(key)
        check(not (ks & OURK) and not wp, "P5 (T10): pack mod %s ships no SkyyArmory asset" % key)
    elif ks & OURK or wp:
        others.append(f)
check(sorted(pk_found) == sorted(PACKS), "P5: both pack mods found and checked: %s" % pk_found)
print("P5. clash scan: %d SET jars + %d pack mods clean; installed (not enabled) mods with our ids (NOTE): %s" % (len(checked), len(pk_found), others))

# ============================================================================================================ P6. T11 art
SA.verify(quiet=True)
z = SA.assets()
for m in NEW:
    ta, ia = SA.wand_art(z, m, "A")
    tb, ib = SA.wand_art(z, m, "B")
    tb2, ib2 = SA.wand_art(z, m, "B")
    da, db = SA.png_decode(ta), SA.png_decode(tb)
    check(SA.png_size(ta) == SA.png_size(tb) == (64, 32) and SA.png_size(ia) == SA.png_size(ib) == (64, 64) and ta != tb and (tb, ib) == (tb2, ib2)
          and JZ.read("Common/Items/Weapons/Wand/SkyyArmory_%s_Texture.png" % m) == tb and JZ.read("Common/Icons/ItemsGenerated/SkyyArmory_Wand_%s.png" % m) == ib
          and len(da.px) == 64 * 32 * 4, "P6 (T11): %s - styles A / B both build (64x32 RGBA textures, 64x64 icons), differ, deterministic; the jar holds B" % m)
vt = SA.png_decode(z.read("Common/Items/Weapons/Wand/Wood_Texture.png"))
for m in NEW:
    jt = SA.png_decode(JZ.read("Common/Items/Weapons/Wand/SkyyArmory_%s_Texture.png" % m))
    check([jt.px[i + 3] for i in range(0, len(jt.px), 4)] == [vt.px[i + 3] for i in range(0, len(vt.px), 4)],
          "P6: %s texture keeps the vanilla Wood texture's alpha (same UV layout)" % m)
skel = SA.png_decode(z.read("Common/Items/Projectiles/Fireball_Textures/SkeletonMage.png"))
qt = SA.png_decode(JZ.read("Common/Items/Projectiles/Fireball_Textures/SkyyArmory_QuickOrb_Blue.png"))
op = [(qt.px[i], qt.px[i + 1], qt.px[i + 2]) for i in range(0, len(qt.px), 4) if qt.px[i + 3] > 0]
mean = [sum(c[k] for c in op) / float(len(op)) for k in range(3)]
check((qt.w, qt.h) == (32, 32) and [qt.px[i + 3] for i in range(0, len(qt.px), 4)] == [skel.px[i + 3] for i in range(0, len(skel.px), 4)]
      and mean[2] > mean[0], "P6 (T11): the quick-orb texture is 32x32, keeps SkeletonMage.png's alpha exactly, mean colour blue (B > R): %s" % [round(x) for x in mean])
z.close()
print("P6. art: styles A / B for 7 metals, deterministic, B in the jar, blue orb texture mean %s" % [round(x) for x in mean])


# ============================================================================================================ P7. T13 / ST9 Mana rule (the SkyySkills jars' default text)
def cp_strings(data):
    sizes = {3: 4, 4: 4, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
    count = struct.unpack_from(">H", data, 8)[0]
    pos, i, out = 10, 1, []
    while i < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            n = struct.unpack_from(">H", data, pos)[0]
            pos += 2
            out.append(data[pos:pos + n].decode("utf-8", errors="replace"))
            pos += n
        elif tag in (5, 6):
            pos += 8
            i += 1
        else:
            pos += sizes[tag]
        i += 1
    return out


def jar_defaults(path):
    """key=value lines of the default config text a jar carries in its string constants"""
    out = {}
    with zipfile.ZipFile(path) as z_:
        for n in z_.namelist():
            if not n.endswith(".class"):
                continue
            for s in cp_strings(z_.read(n)):
                if "mana." not in s and "overall." not in s:
                    continue
                for line in s.split("\n"):
                    mm = re.match(r"^\s*((?:mana|overall|perk)\.[A-Za-z0-9_.]+)=([^\s#]+)\s*$", line)
                    if mm:
                        out.setdefault(mm.group(1), mm.group(2))
    return out


def pools(d, cls, per_override=None):
    base = float(d.get("mana.classBase." + cls, d.get("mana.base", "10")))
    per = float(d.get("mana.classPerLevel." + cls, "0")) if per_override is None else per_override
    ovl = float(d.get("overall.manaPerLevel", "0.2"))
    comb = float(d.get("perk.combat.manaPerLevel", "0"))
    return dict((m, base + per * BANDS[m][0] + ovl * math.floor(BANDS[m][0] / 9.0) + comb * BANDS[m][0]) for m in METALS)


# fix round: version-aware like P5 - before the pin bump the pinned jar is 0.4.14 (no class row: why the partner is needed) and the partner
# 0.4.15 gives the pools; after it the PINNED jar must carry the rows and gives the pools (0.4.14's "why" check runs on its jar if built)
OLD14 = SKILLS_JAR if not POST_PIN else PRE_SKILLS_JAR
D14 = jar_defaults(OLD14) if os.path.isfile(OLD14) else None
if D14 is not None:
    check(D14.get("mana.classBase.Priest") == "30" and D14.get("mana.classBase.Mage") == "30" and D14.get("overall.manaPerLevel") == "0.2"
          and "mana.classPerLevel.Priest" not in D14, "P7: %s default text: Priest / Mage base 30, Overall 0.2, no class-level row" % (
              os.path.basename(OLD14)))
    p14 = pools(D14, "Priest")
    over14 = [m for m in METALS if W[m][0] > 0.4 * p14[m]]
    check(over14 == ["Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"] and W["Cobalt"][0] > p14["Cobalt"],
          "P7 (T13): with %s's rows the Priest is short from Iron up (Cobalt+ cannot be cast) - why 0.4.15's row is a deploy partner: %s" % (
              os.path.basename(OLD14), ["%s %d/%.1f" % (m, W[m][0], p14[m]) for m in METALS]))
else:
    print("P7. NOTE %s is not built here - the 'why 0.4.15' comparison is skipped" % os.path.basename(OLD14))
ROWS_JAR = SKILLS_JAR if POST_PIN else PARTNER_JAR
if os.path.isfile(ROWS_JAR):
    D15 = jar_defaults(ROWS_JAR)
    check(D15.get("mana.classPerLevel.Priest") == "5" and D15.get("mana.classPerLevel.Mage") == "10" and D15.get("mana.classBase.Priest") == "30"
          and D15.get("mana.classBase.Mage") == "30", "P7 (ST9): %s SkyySkills %s default text: Max Mana per class level Priest 5, Mage 10 (base 30)" % (
              "pinned" if POST_PIN else "partner", SKILLS_PIN if POST_PIN else PARTNER))
    pp, pm = pools(D15, "Priest"), pools(D15, "Mage")
else:
    check(D14 is not None, "P7: neither the 0.4.15 rows nor 0.4.14's text is readable")
    pp, pm = pools(D14, "Priest", 5.0), pools(D14, "Mage", 10.0)
rows = []
for m in METALS:
    ws, ss = W[m][0] / pp[m], S[m][0] / pm[m]
    rows.append("%s L%d: wand %d/%.1f %.1f%%, staff %d/%.1f %.1f%%" % (m, BANDS[m][0], W[m][0], pp[m], ws * 100, S[m][0], pm[m], ss * 100))
    check(ws <= 0.40 + 1e-9 and ss <= 0.40 + 1e-9, "P7 (T13 / ST9): %s charged shots within 40%% of the fighter pool at Lv %d (wand %.1f%%, staff %.1f%%)" % (
        m, BANDS[m][0], ws * 100, ss * 100))
check(abs(pp["Mithril"] - 230.8) < 1e-6 and abs(pm["Mithril"] - 430.8) < 1e-6 and abs(W["Mithril"][0] / pp["Mithril"] - 0.3683) < 1e-3
      and abs(S["Mithril"][0] / pm["Mithril"] - 0.3946) < 1e-3, "P7: Mithril pools 230.8 / 430.8 -> 36.8% / 39.5% (spec 15.4)")
print("P7. Mana rule (fighter, band start): " + "; ".join(rows))
PY_OKS, PY_FAILS = OKS[0], len(FAILS)
print("PYTHON PART: %d ok, %d FAIL" % (PY_OKS, PY_FAILS))


# ============================================================================================================ JVM PART
def jvm_part():
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride, JObject, JFloat, JInt, JDouble, JBoolean
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    hcls = os.path.join(SCRATCH, "hcls")
    os.makedirs(hcls, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, GEAR_JAR, B.JAVASSIST, hcls], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    Paths, ArrayList, HashMap, HashSet = JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"), JClass("java.util.HashMap"), JClass("java.util.HashSet")
    UUID, Props, CHM = JClass("java.util.UUID"), JClass("java.util.Properties"), JClass("java.util.concurrent.ConcurrentHashMap")
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def setf(o, cls, name, v):
        jfield(cls, name).set(o, v)

    # ---------------- A. load + verify every class of our jar
    names = [n[:-6].replace("/", ".") for n in JN if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, sysl)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("A: load %s: %s" % (n, e))
            print("LOAD FAIL", n, e)
    check(len(names) == 17, "A: 17 classes (10 SkyyArmory + 7 kit)")
    print("A. loaded + verified + initialised %d classes (-Xverify:all)" % len(names))
    if FAILS[PY_FAILS:]:
        return

    # ---------------- X. MethodHandles.Lookup access audit (the JVM's own rules, every reference of every class)
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CPj.appendClassPath(JAR)
    CtNM = JClass("javassist.CtNewMethod")
    lk = CPj.makeClass("armoryharness.LookupIn")
    lk.addMethod(CtNM.make("public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
                           "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(hcls)
    # the test stand-ins: a command buffer whose getComponent answers from a map, a component registry proxy that records systems
    sb = CPj.makeClass("armoryharness.StubBuffer", CPj.get("com.hypixel.hytale.component.CommandBuffer"))
    sb.addField(JClass("javassist.CtField").make("public static java.util.Map COMP = new java.util.HashMap();", sb))
    sb.addMethod(CtNM.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                           "com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) COMP.get(r); }", sb))
    sb.writeFile(hcls)
    rp = CPj.makeClass("armoryharness.CaptureProxy", CPj.get("com.hypixel.hytale.component.ComponentRegistryProxy"))
    rp.addField(JClass("javassist.CtField").make("public static java.util.List CAP = new java.util.ArrayList();", rp))
    rp.addMethod(CtNM.make("public void registerSystem(com.hypixel.hytale.component.system.ISystem s) { CAP.add(s); }", rp))
    rp.writeFile(hcls)
    LIN = JClass("armoryharness.LookupIn")
    MTc = JClass("java.lang.invoke.MethodType")
    CPool = JClass("javassist.bytecode.ConstPool")
    JMod_ = JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5, 0x12, 0x13}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, sysl)

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk_ = LIN.lookupIn(D)
        cc = CPj.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n2 = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it3 = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it3.hasNext():
                p_ = it3.next()
                op_ = it3.byteAt(p_)
                if op_ not in XOPS:
                    continue
                where = "%s.%s @%d" % (cn.rsplit(".", 1)[-1], mi.getName(), p_)
                if op_ == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it3.byteAt(p_ + 1) if op_ == 0x12 else it3.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op_ in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n2 += 1
                try:
                    if op_ in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk_.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op_ in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", sysl).parameterType(0)
                        if op_ in (0xb2, 0xb3):
                            lk_.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk_.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx))
                        else:
                            cname, name, desc = str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, sysl)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn):
                                raise ValueError("constructor %s%s not accessible" % (cname, desc))
                        elif name == "<init>":
                            lk_.findConstructor(C_, mt)
                        elif op_ == 0xb8:
                            lk_.findStatic(C_, name, mt)
                        elif op_ == 0xb7:
                            lk_.findSpecial(C_, name, mt, D)
                        else:
                            lk_.findVirtual(C_, name, mt)
                except Exception as ex2:
                    if "caller-sensitive" in str(ex2):
                        cs_skip[0] += 1
                    else:
                        refused.append("%s: %s" % (where, ex2))
        return refused, n2
    xref, xn = [], 0
    cs_skip = [0]
    for cn in names:
        r2, n2 = lookup_audit(cn)
        xref += r2
        xn += n2
    check(not xref and xn > 1000, "X. all %d references in the %d classes pass MethodHandles.Lookup in their own class: refused %s" % (xn, len(names), xref[:5]))
    print("X. access: %d class / field / method references, %d refused (%d JDK caller-sensitive reflection calls skipped)" % (xn, len(xref), cs_skip[0]))

    # ---------------- E. engine stores
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    bus = JClass("com.hypixel.hytale.event.EventBus")(False)
    setf(hs, HS, "eventBus", bus)
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu = CHM()
    setf(uni, UNI, "playersByUuid", pbu)
    setf(uni, UNI, "players", JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    wmap = CHM()
    setf(uni, UNI, "worlds", wmap)
    setf(uni, UNI, "worldsByUuid", CHM())
    setf(uni, UNI, "unmodifiableWorlds", JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAPLOG)

    def records():
        out = []
        for r in list(CAPLOG):
            try:
                msg = str(r.getMessage())
                ps = r.getParameters()
                if ps is not None and len(ps) > 0:
                    try:
                        msg = str(JClass("java.lang.String").format(msg, ps))
                    except Exception:
                        msg = msg + " " + " ".join(str(p) for p in ps)
                out.append((str(r.getLevel()), msg))
            except Exception:
                pass
        return out
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")

    def reg_ilt(c, path, codec, unknown=False):
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        try:
            AR.register(b_.build())
        except Exception as e:
            print("E. register %s: %s" % (c.class_.getSimpleName(), e))
    reg_ilt(ESTc, "Entity/Stats", ESTc.CODEC)
    reg_ilt(INTc, "Item/Interactions", INTc.CODEC, True)
    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC)
    try:
        AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    except Exception as e:
        print("E. register UnarmedInteractions: %s" % e)
    # the interaction Type codecs exactly as InteractionModule.setup registers them (read from its bytecode)
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            idx = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            t_ = cp_.getTag(idx)
            if t_ == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(idx))
            elif t_ == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(idx))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(idx)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(idx)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jfield(C_, "CODEC").get(None))
    check(len(regs) >= 70 and ("Charging", PI + "client.ChargingInteraction") in regs and ("StatsCondition", PI + "none.StatsConditionInteraction") in regs,
          "E: the interaction codecs registered from InteractionModule.setup's bytecode (%d)" % len(regs))
    AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
    ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")

    def dec(c, key, text):
        """the engine codec of c's store: (object or None, problems text)"""
        st = AR.getAssetStore(c.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300]
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed %s" % [str(x) for x in (vr.getResults() or [])][:3])
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        return o, "; ".join(prob)

    def load(c, objs, pack):
        l_ = ArrayList()
        for o in objs:
            l_.add(o)
        try:
            r_ = AR.getAssetStore(c.class_).loadAssets(pack, l_)
            return not r_.hasFailed()
        except Exception as e:
            print("E. load %s (%s): %s" % (c.class_.getSimpleName(), pack, str(e)[:200]))
            return None
    stats = []
    for i, p in AIDX["stat"].items():
        d = dict(aj("stat", i))
        d.pop("Regenerating", None)         # the regen conditions need EntityStatsModule's condition codecs - only the ids matter here
        o, why = dec(ESTc, i, json.dumps(d))
        if o is not None:
            stats.append(o)
    load(ESTc, stats, "Hytale:Hytale")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    DST.update()
    MANA_I = int(DST.getMana())
    check(MANA_I == int(ESTc.getAssetMap().getIndex("Mana")) and int(ESTc.getAssetMap().getIndex("Stamina")) >= 0,
          "E: vanilla stat types loaded, DefaultEntityStatTypes.getMana() = the Mana index %d" % MANA_I)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")   # our lines through the captured logger
    print("E. engine stores: %d registered, %d interaction codecs, %d stat types" % (AR.getStoreMap().size(), len(regs), len(stats)))

    # ---------------- D. T1 / ST1 / ST2: every generated asset through the engine codecs
    ITMc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    PRJc = JClass("com.hypixel.hytale.server.core.asset.type.projectile.config.Projectile")
    MDLc = JClass("com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset")
    TRLc = JClass("com.hypixel.hytale.server.core.asset.type.trail.config.Trail")
    PSYc = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem")
    PSPc = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSpawner")
    CRRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    # the vanilla assets our chains reach (interactions + roots: the Wood hold through SkyySkills' overrides; the vanilla orb), loaded
    # into the real stores first so the decode of ours sees what the game would (parents before children)
    need_i, need_r = set(), set()

    def closure(x):
        if isinstance(x, str):
            if x in INTS_ALL and x not in need_i and x not in JINT:
                need_i.add(x)
                closure(INTS_ALL[x])
            elif x in ROOTS_ALL and x not in need_r and x not in JROOT:
                need_r.add(x)
                closure(ROOTS_ALL[x])
        elif isinstance(x, list):
            for e in x:
                closure(e)
        elif isinstance(x, dict):
            for k, v in x.items():
                if k not in ("Type", "$Comment"):
                    closure(v)
    for d in list(JINT.values()) + list(WOOD3.values()):
        closure(d)
    vint, vbad = {}, []
    pending = sorted(need_i)
    for _round in range(10):             # parents first: each round is loaded before the next decodes (the codec reads the store)
        nxt, got = [], []
        for i in pending:
            d = SK_INTS.get(i) or aj("int", i)
            if d.get("Parent") and d["Parent"] not in vint and d["Parent"] in need_i:
                nxt.append(i)
                continue
            o, why = dec(INTc, i, json.dumps(d))
            if o is None:
                vbad.append((i, why))
            else:
                vint[i] = o
                got.append(i)
        load(INTc, [vint[i] for i in got if i not in SK_INTS], "Hytale:Hytale")
        load(INTc, [vint[i] for i in got if i in SK_INTS], "Skyy:%s SkyySkills" % SKILLS_PIN)
        pending = nxt
        if not pending:
            break
    vroot = {}
    for r in sorted(need_r):
        o, why = dec(ROOTc, r, json.dumps(aj("root", r)))
        if o is None:
            vbad.append((r, why))
        else:
            vroot[r] = o
    load(ROOTc, list(vroot.values()), "Hytale:Hytale")
    check(not vbad, "D: the vanilla interactions / roots our chains reach decode (%d + %d): %s" % (len(vint), len(vroot), vbad[:3]))
    vorb_parent = aj("prj", "Staff_Wood_Rotten_Corruption_Orb")
    o1, w1 = dec(PRJc, "Staff_Wood_Rotten_Corruption_Orb", json.dumps(vorb_parent))
    load(PRJc, [o1], "Hytale:Hytale")
    o2, w2 = dec(PRJc, VAN_ORB, json.dumps(aj("prj", VAN_ORB)))
    load(PRJc, [o2], "Hytale:Hytale")
    vmodel, wm = dec(MDLc, VAN_ORB, json.dumps(aj("model", VAN_ORB)))
    load(MDLc, [vmodel], "Hytale:Hytale")
    DEC = {}
    bad = []
    for c, table, kind in ((INTc, JINT, "interaction"), (ROOTc, JROOT, "root"), (PRJc, JPRJ, "projectile"),
                           (MDLc, dict((k, J[p]) for k, p in J_MODELS.items()), "model"),
                           (TRLc, dict((k, J[p]) for k, p in J_TRAILS.items()), "trail")):
        for k, d in table.items():
            o, why = dec(c, k, json.dumps(d))
            if o is None or why:
                bad.append("%s %s: %s" % (kind, k, why))
            else:
                DEC[(kind, k)] = o
    for c, table, kind in ((PSPc, J_PSP, "spawner"), (PSYc, J_PSYS, "particle system")):
        for k, p in table.items():
            o, why = dec(c, k, JZ.read(p).decode("utf-8"))
            if o is None or why:
                bad.append("%s %s: %s" % (kind, k, why))
            else:
                DEC[(kind, k)] = o
    check(not bad, "D (T1 / ST2): 117 interactions (incl. the Wand_Primary override), 15 roots, 31 projectiles, the quick model, trail, 3 particle "
                   "systems + 5 spawners decode through the engine codecs - no exception, no validation failure, no unknown key (a decode does "
                   "not look references up: P1's closure + its negative controls and C's engine compile do): %s" % bad[:5])
    # items AFTER the interactions (the vanilla wand items' inline vars name interaction parents)
    ibad = []
    for k, d in JITEM.items():
        o, why = dec(ITMc, k, json.dumps(d))
        if o is None or why:
            ibad.append("%s: %s" % (k, why))
        else:
            DEC[("item", k)] = o
    vitems = {}
    for k in ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"):
        o, why = dec(ITMc, k, json.dumps(WOOD3[k]))
        if o is None or why:
            ibad.append("SkyySkills %s: %s" % (k, why))
        else:
            vitems[k] = o
    check(not ibad, "D (T1 / ST1): the 7 wands + 8 staff overrides decode through Item's engine codec (AssetBuilderCodec.decodeJsonAsset) - "
                    "and SkyySkills' 3 wood wands: %s" % ibad[:4])
    for k in J_ITEMS:
        o = DEC.get(("item", k))
        if o is None:
            continue
        check(int(o.getMaxStack()) == 1 and str(o.getId()) == k and o.getWeapon() is not None,
              "D: %s - MaxStack 1 (Weapon section, SkyyGear's ammo test passes), a weapon" % k)

    def flat(r):
        return {"in": [(None if m_.getItemId() is None else str(m_.getItemId()), None if m_.getResourceTypeId() is None else str(m_.getResourceTypeId()),
                        int(m_.getQuantity())) for m_ in r.getInput()],
                "bench": [(str(b_.type), str(b_.id), None if b_.categories is None else [str(c_) for c_ in b_.categories], int(b_.requiredTierLevel))
                          for b_ in (r.getBenchRequirement() or [])],
                "t": float(r.getTimeSeconds()), "know": bool(r.isKnowledgeRequired())}

    def dec_recipe(txt, key):
        ei = AEI(Paths.get(key + ".json"), ADT(CRRc.class_, key, None))
        try:
            o = CRRc.CODEC.decodeJson(RJR.fromJsonString(txt), ei)
        except Exception as e:
            return None, str(e)[:200]
        bad3 = []
        if ei.getValidationResults().hasFailed():
            bad3.append("validation failed")
        if len(list(ei.getUnknownKeys())) > 0:
            bad3.append("unknown keys %s" % [str(x) for x in ei.getUnknownKeys()])
        return o, "; ".join(bad3)
    for k in sorted(J_ITEMS):
        r = JITEM[k].get("Recipe")
        if r is None:
            continue
        o, why = dec_recipe(json.dumps(r), k + "_Recipe_Generated_0")
        metal = k.rsplit("_", 1)[1]
        mr = model_recipe("Mithril" if metal == "Onyxium" else metal)
        mo, mwhy = dec_recipe(json.dumps(aj("item", "Weapon_Shortbow_" + ("Mithril" if metal == "Onyxium" else metal))["Recipe"]),
                              "Weapon_Shortbow_%s_Recipe_Generated_0" % metal)
        if o is None or why or mo is None or mwhy:
            check(False, "D (T1): recipe of %s decodes: %s / %s" % (k, why, mwhy))
            continue
        a3, b3 = flat(o), flat(mo)
        b3["bench"] = [x_ for x_ in b3["bench"] if x_[1] != "Armory"]
        if metal == "Onyxium":
            b3["in"] = [("Ingredient_Bar_Onyxium" if x_[0] == "Ingredient_Bar_Mithril" else x_[0], x_[1], x_[2]) for x_ in b3["in"]]
        check(a3 == b3, "D (T1): %s's embedded recipe decodes through CraftingRecipe.CODEC = the model shortbow's (inputs, bench + tab + tier, time, "
                        "knowledge)%s: %s" % (k, " with Onyxium bars" if metal == "Onyxium" else "", a3))
    print("D. engine-codec decode: %d of our assets + %d embedded recipes, 0 problems; %d vanilla interactions / %d roots of the chains loaded" % (
        len(DEC), len([k for k in J_ITEMS if JITEM[k].get("Recipe")]), len(vint), len(vroot)))

    # ---------------- R. T4 / T5 / ST4 read-back from the decoded objects
    SCB, CSB, CHI, LPIc = JClass(PI + "none.StatsConditionBaseInteraction"), JClass(PI + "server.ChangeStatBaseInteraction"), JClass(PI + "client.ChargingInteraction"), JClass(PI + "server.LaunchProjectileInteraction")
    f_raw, f_costs = jfield(SCB, "rawCosts"), jfield(SCB, "costs")
    f_esa, f_es = jfield(CSB, "entityStatAssets"), jfield(CSB, "entityStats")
    f_next, f_sk = jfield(CHI, "next"), jfield(CHI, "sortedKeys")

    def check_of(iid):
        o = DEC[("interaction", iid)]
        raw = f_raw.get(o)
        cs = f_costs.get(o)
        return (float(raw.getFloat("Mana")) if raw is not None and raw.containsKey("Mana") else None,
                float(cs.get(JInt(MANA_I))) if cs is not None and cs.containsKey(JInt(MANA_I)) else None)

    def spend_of(iid):
        o = DEC[("interaction", iid)]
        a, s = f_esa.get(o), f_es.get(o)
        return (float(a.getFloat("Mana")) if a is not None and a.containsKey("Mana") else None,
                float(s.get(JInt(MANA_I))) if s is not None and s.containsKey(JInt(MANA_I)) else None)

    def keys_of(iid):
        o = DEC[("interaction", iid)]
        sk_ = [float(x) for x in f_sk.get(o)]
        n_ = f_next.get(o)
        return [round(x, 4) for x in sk_], [str(n_.get(JFloat(x))) for x in sk_]
    for m in METALS:
        rows_ = []
        if m != "Wood":
            c, q = W[m][0], W[m][1]
            rows_ += [("SkyyArmory_Wand_Cast_" + m, c), ("SkyyArmory_Wand_Quick_" + m, q)]
        else:
            rows_ += [("SkyyArmory_Wand_Quick_Wood", 1)]
        rows_ += [("SkyyArmory_Staff_Cast_" + m, S[m][0]), ("SkyyArmory_Staff_Quick_" + m, S[m][1])]
        for iid, want in rows_:
            spend = iid.replace("_Cast_", "_Cast_Cost_").replace("_Quick_", "_Quick_Cost_")
            check(check_of(iid) == (float(want), float(want)) and spend_of(spend) == (-float(want), -float(want)),
                  "R (T4): %s checks %s (raw / resolved Mana index) and %s spends %s" % (iid, check_of(iid), spend, spend_of(spend)))
    for m in NEW:
        ks, ts = keys_of("SkyyArmory_Wand_Primary_" + m)
        check(ks == [0.0, 0.35] and ts == ["SkyyArmory_Wand_Quick_" + m, "SkyyArmory_Wand_Cast_" + m]
              and [ts[jump(ks, v)] for v in (0.0, 0.1, 0.34, 0.35, 2.0)] == [ts[0]] * 3 + [ts[1]] * 2,
              "R (T5): %s - the engine's sortedKeys %s; jumpToChargeValue 0 / 0.1 / 0.34 -> quick, 0.35 / 2.0 -> charged" % (m, ks))
        lp = DEC[("interaction", "SkyyArmory_Wand_Cast_Launch_" + m)]
        lq = DEC[("interaction", "SkyyArmory_Wand_Quick_Launch_" + m)]
        check(str(lp.getProjectileId()) == ORB[m] and str(lq.getProjectileId()) == QORB[m], "R (T4): %s launches %s / %s" % (m, ORB[m], QORB[m]))
    for m in METALS:
        ks, ts = keys_of("SkyyArmory_Staff_Primary_" + m)
        check(ks == [0.0, 1.0] and ts == ["SkyyArmory_Staff_Quick_" + m, "SkyyArmory_Staff_Cast_" + m]
              and [ts[jump(ks, v)] for v in (0.0, 0.5, 0.99, 1.0, 3.0)] == [ts[0]] * 3 + [ts[1]] * 2,
              "R (ST4): %s staff - sortedKeys %s; 0 / 0.5 / 0.99 -> quick, 1.0 / 3.0 -> charged" % (m, ks))
        check(str(DEC[("interaction", "SkyyArmory_Staff_Cast_Launch_" + m)].getProjectileId()) == SORB[m]
              and str(DEC[("interaction", "SkyyArmory_Staff_Quick_Launch_" + m)].getProjectileId()) == SQORB[m], "R (ST4): %s staff launches" % m)
    ks, ts = keys_of("Wand_Primary")
    check(ks == [0.0, 0.35] and ts == ["SkyyArmory_Wand_Quick_Wood", "Wand_Cast_Left_Charged"], "R (2.4): the decoded Wand_Primary override: %s %s" % (ks, ts))
    sta = DEC[("interaction", "SkyyArmory_Staff_Stamina")]
    std = DEC[("interaction", "SkyyArmory_Staff_Stamina_Delay")]
    check(dict((str(k), float(v)) for k, v in dict(f_esa.get(sta)).items()) == {"Stamina": -5.0}
          and dict((str(k), float(v)) for k, v in dict(f_esa.get(std)).items()) == {"StaminaRegenDelay": -1.5}
          and str(jfield(CSB, "changeStatBehaviour").get(std)) == "Set", "R (ST3): the staff hold spends 5 Stamina and Sets the regen delay -1.5 (vanilla)")
    print("R. read-back: every check = its spend at the resolved Mana index %d, keys {0, 0.35} / {0, 1}, launches = the tables" % MANA_I)

    # ---------------- J. T6 / ST5 projectiles + the quick model
    vorb = aresolve("prj", VAN_ORB)
    same_keys = [k for k in vorb if k not in ("Parent", "Damage", "Appearance", "MuzzleVelocity", "TerminalVelocity", "HitParticles", "DeathParticles")]
    for pid in sorted(JPRJ):
        o = DEC[("projectile", pid)]
        d = JPRJ[pid]
        quick = "Quick" in pid
        metal = pid.rsplit("_", 1)[1]
        want = (W[metal][4] if "QuickOrb_" in pid and "Staff" not in pid else W[metal][3] if pid.startswith("SkyyArmory_Orb_") else
                S[metal][4] if "StaffQuickOrb" in pid else S[metal][3])
        check(int(o.getDamage()) == want and float(o.getMuzzleVelocity()) == (90.0 if quick else 30.0)
              and float(o.getTerminalVelocity()) == (150.0 if quick else 50.0) and float(o.getGravity()) == 0.0 and float(o.getTimeToLive()) == 3.1
              and str(o.getAppearance()) == ("SkyyArmory_QuickOrb" if quick else VAN_ORB) and "Parent" not in d
              and all(d[k] == vorb[k] for k in same_keys),
              "J (T6 / ST5): %s - damage %d, speed %s / %s, gravity 0, TTL 3.1, every other field = the resolved vanilla orb" % (
                  pid, int(o.getDamage()), o.getMuzzleVelocity(), o.getTerminalVelocity()))
    qm, vm = DEC[("model", "SkyyArmory_QuickOrb")], vmodel
    hb_q, hb_v = qm.getBoundingBox(), vm.getBoundingBox()
    check(str(hb_q) == str(hb_v), "J (T6): the quick orb model asset keeps the charged orb's hitbox (+-0.1): %s" % hb_q)
    print("J. projectiles: 31 decoded, damage / speed / gravity per table, the rest = the vanilla orb; quick hitbox = charged")

    # ---------------- L. T-live / ST-live: the plugin's own pack check on the REAL stores loaded with our pack
    our_ints = [DEC[("interaction", k)] for k in JINT]
    ok_l = [load(INTc, our_ints, PACK), load(ROOTc, [DEC[("root", k)] for k in JROOT], PACK), load(PRJc, [DEC[("projectile", k)] for k in JPRJ], PACK),
            load(MDLc, [qm], PACK)]
    load(ITMc, list(vitems.values()), "Skyy:%s SkyySkills" % SKILLS_PIN)
    ok_l.append(load(ITMc, [DEC[("item", k)] for k in JITEM], PACK))
    check(all(x is not False for x in ok_l), "L: our interactions / roots / projectiles / model / items load into the real asset stores (%s)" % ok_l)
    CHK = JClass(PKG + "ArmoryCheck")
    r = CHK.packCheck()
    check(str(r[0]) == "info" and "15 of 15 items, 117 of 117 interactions, 31 of 31 projectiles come from Skyy:0.1 SkyyArmory" in str(r[1])
          and "live read-back OK" in str(r[1]), "L (T-live / ST-live): ArmoryCheck.packCheck() on the real stores = one INFO: %s" % str(r[1])[:300])
    INTMAP = INTc.getAssetMap()
    check(str(INTMAP.getAssetPack("Wand_Primary")) == PACK and str(ITMc.getAssetMap().getAssetPack("Weapon_Staff_Wood")) == PACK
          and str(ITMc.getAssetMap().getAssetPack("Weapon_Wand_Wood")) == "Skyy:%s SkyySkills" % SKILLS_PIN,
          "L: the winners - Wand_Primary and the staffs from SkyyArmory, the wood wands from SkyySkills")
    print("L. T-live: packCheck INFO on the real stores (the WARN case runs last - it changes the store)")

    # ---------------- C. FIX ROUND: the REAL engine compile (RootInteraction.build) of our chains on the real stores
    # (review: the decode never looks a reference up and nothing compiled the chains). build() turns a root into its operation list:
    # Interaction.compile resolves every Next / Failed id through Interaction.getInteractionOrUnknown, which for a MISSING id logs WARNING
    # "Missing interaction <id>" and compiles a placeholder SendMessageInteraction instead. A Parallel step forks child roots by id (its
    # protected 'interactions' field) - each child root is built and checked too.
    PARc = JClass(PI + "none.ParallelInteraction")
    SMIc = JClass(PI + "none.simple.SendMessageInteraction")
    f_par = jfield(PARc, "interactions")
    RMAP = ROOTc.getAssetMap()

    def compile_root(rid, seen=None):
        """{"ops": [(simple class, interaction id or None)], "kids": {parallel id: [child root ops]}, "bad": [problems]}"""
        seen = set() if seen is None else seen
        out = {"ops": [], "kids": {}, "bad": []}
        r_ = RMAP.getAsset(rid)
        if r_ is None:
            out["bad"].append("root %s is not in the store" % rid)
            return out
        try:
            r_.build()
        except Exception as e_:
            out["bad"].append("build %s: %s" % (rid, str(e_)[:200]))
            return out
        for i_ in range(int(r_.getOperationMax())):
            op_ = r_.getOperation(i_)
            inner = op_.getInnerOperation()
            if inner is not None and INTc.class_.isInstance(inner):
                cn_, iid_ = str(inner.getClass().getSimpleName()), str(inner.getId())
                out["ops"].append((cn_, iid_))
                if SMIc.class_.isInstance(inner):
                    out["bad"].append("%s compiles a placeholder for a MISSING interaction %s" % (rid, iid_))
                if PARc.class_.isInstance(inner) and iid_ not in seen:
                    seen.add(iid_)
                    for kid in list(f_par.get(inner) or []):
                        k_ = compile_root(str(kid), seen)
                        out["kids"].setdefault(iid_, []).append([x[1] for x in k_["ops"]])
                        out["bad"] += k_["bad"]
            else:
                out["ops"].append((str(op_.getClass().getSimpleName()), None))
        return out
    n_miss0 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    comp_bad, comp_rows = [], []
    for kind_, m in [("Wand", x) for x in NEW] + [("Staff", x) for x in METALS]:
        rid = "SkyyArmory_%s_Primary_%s" % (kind_, m)
        res = compile_root(rid)
        named = [iid_ for cn_, iid_ in res["ops"] if iid_ is not None and not iid_.startswith("*")]
        fail_ = "SkyyArmory_%s_Fail" % kind_
        want_named = [rid, "SkyyArmory_%s_Quick_%s" % (kind_, m), fail_, "SkyyArmory_%s_Cast_%s" % (kind_, m), fail_]
        kids = sorted(res["kids"].values(), key=lambda v: str(v))
        quick_kids = [["SkyyArmory_%s_Quick_Cost_%s" % (kind_, m)], ["SkyyArmory_%s_Quick_Launch_%s" % (kind_, m)], ["SkyyArmory_%s_Quick_Effect" % kind_]]
        cast_kids = ([["SkyyArmory_Staff_Stamina"], ["SkyyArmory_Staff_Stamina_Delay"]] if kind_ == "Staff" else []) + [
            ["SkyyArmory_%s_Cast_Cost_%s" % (kind_, m)], ["SkyyArmory_%s_Cast_Launch_%s" % (kind_, m)], ["SkyyArmory_%s_Cast_Effect" % kind_]]
        classes_ = [cn_ for cn_, iid_ in res["ops"] if iid_ is not None]
        ok_ = (not res["bad"] and named == want_named and classes_[0] == "ChargingInteraction"
               and classes_.count("StatsConditionInteraction") == 2 and classes_.count("ParallelInteraction") == 2
               and sorted([quick_kids, cast_kids], key=lambda v: str(v)) == kids)
        if not ok_:
            comp_bad.append("%s: bad %s, named %s, classes %s, kids %s" % (rid, res["bad"][:2], named, classes_, kids))
        comp_rows.append((rid, len(res["ops"])))
    # the vanilla Wand_Primary ROOT with our override: key 0 = our 1-Mana quick chain, key 0.35 = SkyySkills' charged step
    res_w = compile_root("Wand_Primary")
    named_w = [iid_ for cn_, iid_ in res_w["ops"] if iid_ is not None and not iid_.startswith("*")]
    wq_kids = [k_ for k_ in res_w["kids"].values() if ["SkyyArmory_Wand_Quick_Cost_Wood"] in k_]
    ok_w = (not res_w["bad"] and named_w[:4] == ["Wand_Primary", "SkyyArmory_Wand_Quick_Wood", "SkyyArmory_Wand_Fail", "Wand_Cast_Left_Charged"]
            and len(wq_kids) == 1 and sorted(wq_kids[0]) == [["SkyyArmory_Wand_Quick_Cost_Wood"], ["SkyyArmory_Wand_Quick_Effect"], ["SkyyArmory_Wand_Quick_Launch_Wood"]])
    if not ok_w:
        comp_bad.append("Wand_Primary: bad %s, named %s, kids %s" % (res_w["bad"][:2], named_w, list(res_w["kids"].values())))
    n_miss1 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_])
    check(not comp_bad and n_miss1 == n_miss0 and len(comp_rows) == 15,
          "C (fix round): RootInteraction.build() of our 15 roots + the vanilla Wand_Primary root on the real stores - 0 missing interactions, "
          "no placeholder step, each graph = Charging -> [quick check -> Parallel(cost, launch, effect) | Fail] + [charged check -> Parallel(%s) | "
          "Fail]; Wand_Primary key 0 = our Wood quick chain, key 0.35 = Wand_Cast_Left_Charged: %s" % (
              "Stamina, regen delay, cost, launch, effect for staffs", comp_bad[:3]))
    print("C. engine compile: %d roots + Wand_Primary built, %s operations per root, every Parallel child root built; 0 missing" % (
        len(comp_rows), sorted(set(n_ for r_, n_ in comp_rows))))
    # NEGATIVE CONTROL: a Charging key naming a missing interaction decodes "ok" (the review's finding) but the compile check catches it
    bad_ch = dict(JINT["SkyyArmory_Wand_Primary_Copper"])
    bad_ch["Next"] = {"0": "No_Such_Interaction_ZZ", "0.35": "SkyyArmory_Wand_Cast_Copper"}
    ob_, wb_ = dec(INTc, "SkyyArmoryTest_BadCharging", json.dumps(bad_ch))
    orr_, wr_ = dec(ROOTc, "SkyyArmoryTest_BadRoot", json.dumps({"Interactions": ["SkyyArmoryTest_BadCharging"]}))
    load(INTc, [ob_], "Test:Pack")
    load(ROOTc, [orr_], "Test:Pack")
    res_b = compile_root("SkyyArmoryTest_BadRoot")
    n_miss2 = len([m_ for lv_, m_ in records() if "Missing interaction" in m_ and "No_Such_Interaction_ZZ" in m_])
    check(ob_ is not None and not wb_ and any("No_Such_Interaction_ZZ" in x for x in res_b["bad"]),
          "C (fix round, negative control): a Charging key -> a missing interaction DECODES without a problem (%r) but the compile check catches it "
          "(placeholder step%s): %s" % (wb_, ", + the engine's 'Missing interaction' warning" if n_miss2 else "", res_b["bad"][:2]))

    # ---------------- G. T8 / ST7 SkyyGear's real code on our ids (real decoded + loaded chains)
    GP = "com.skyy.gear."
    GCfg, GChg, GData, GLvl, GBase = (JClass(GP + "GearCfg"), JClass(GP + "GearChg"), JClass(GP + "GearData"), JClass(GP + "GearLevel"),
                                       JClass(GP + "GearBase"))
    GCfg.apply(Props(), False)          # SkyyGear's built-in defaults (its level table = Skyy's bands)
    BD, BI32 = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32")
    GChg.clear()

    def doc(lv):
        d_ = BD()
        d_.put("lvl", BI32(lv))
        return d_
    for m in NEW + ["Wood"]:
        for iid, sp, q_, o_ in ((WID[m], "wand", QORB[m], ORB.get(m, VAN_ORB)), (SID[m], "staff", SQORB[m], SORB[m])):
            band = [int(x) for x in GLvl.band(iid)]
            lc_q, lc_o = int(GChg.launchCode(iid, q_)), int(GChg.launchCode(iid, o_))
            check(band[:2] == list(BANDS[m]) and bool(GData.isGear(iid)) and bool(GData.isSpell(iid)) and not bool(GData.skyyItem(iid))
                  and int(GData.slotOf(iid)) == 1 and float(GBase.kOf(iid, True)) == 1.0 and lc_q == 0 and lc_o == 1,
                  "G (T8 / ST7): %s - band %s, gear + spell (slot 1), not a Skyy item, K = 1; SkyyGear's walk: %s normal (0), %s charged (1): %s %s" % (
                      iid, band[:2], q_, o_, lc_q, lc_o))
            lv = BANDS[m][0]
            sr = GBase.spellRange(iid, doc(lv))
            mult = float(GBase.mult(iid, doc(lv), True))
            lo_hi = ((W[m][4], W[m][3]) if sp == "wand" else (S[m][4], S[m][3]))
            check(sr is not None and abs(float(sr[0]) - lo_hi[0] * mult) < 1e-3 and abs(float(sr[1]) - lo_hi[1] * mult) < 1e-3,
                  "G (3.4): %s at Lv %d - SkyyGear's 'Spell at Lv %d' range %s = quick %d .. charged %d x %.4f" % (
                      iid, lv, lv, [round(float(x), 1) for x in sr] if sr is not None else None, lo_hi[0], lo_hi[1], mult))
    for iid in ("Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"):
        check(int(GChg.launchCode(iid, QORB["Wood"])) == 0 and int(GChg.launchCode(iid, VAN_ORB)) == 1,
              "G (T8): %s through our Wand_Primary - the 1-Mana quick orb normal, the vanilla orb charged" % iid)
    copper_lv10 = GBase.spellRange(WID["Copper"], doc(10))
    check(round(float(copper_lv10[0])) == 23 and round(float(copper_lv10[1])) == 115, "G: Copper wand Lv 10 'Spell at Lv 10: 23-115' (spec 3.4)")
    print("G. SkyyGear %s: bands, spell, K = 1, the walk on the real chains (quick 0 / charged 1 for 16 weapons + 3 wood wands), spellRange" % PIN["SkyyGear"])

    # ---------------- S. T6 spawn hook on a REAL Holder + ProjectileComponent
    ESr = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    LPCc = JClass("com.hypixel.hytale.server.core.entity.entities.ProjectileComponent")
    ESCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.EntityScaleComponent")
    TCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    em = U.allocateInstance(EMc.class_)
    reg_ = ESr.REGISTRY
    setf(em, EMc, "projectileComponentType", reg_.registerComponent(LPCc.class_, "Projectile", jfield(LPCc, "CODEC").get(None)))
    setf(em, EMc, "entityScaleComponentType", reg_.registerComponent(ESCc.class_, "EntityScale", jfield(ESCc, "CODEC").get(None)))
    setf(em, EMc, "transformComponentType", reg_.registerComponent(TCc.class_, "Transform", jfield(TCc, "CODEC").get(None)))
    # fix round (the reach row): the REAL DespawnComponent type + the world clock (TimeResource) in a store, as the game has them
    DSPc = JClass("com.hypixel.hytale.server.core.modules.entity.DespawnComponent")
    TRSc = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    TMc = JClass("com.hypixel.hytale.server.core.modules.time.TimeModule")
    STc = JClass("com.hypixel.hytale.component.Store")
    RSCc = JClass("com.hypixel.hytale.component.Resource")
    Instant = JClass("java.time.Instant")
    setf(em, EMc, "despawnComponentComponentType", reg_.registerComponent(DSPc.class_, "Despawn", jfield(DSPc, "CODEC").get(None)))
    jfield(EMc, "instance").set(None, em)
    trt = reg_.registerResource(TRSc.class_, "Time", jfield(TRSc, "CODEC").get(None))
    tmod = U.allocateInstance(TMc.class_)
    setf(tmod, TMc, "timeResourceType", trt)
    jfield(TMc, "instance").set(None, tmod)
    NOW = Instant.parse("2026-10-03T12:00:00Z")
    clock = TRSc(NOW)
    wstore = U.allocateInstance(STc.class_)
    setf(wstore, STc, "registry", reg_)
    res_arr = JArray(RSCc)(int(trt.getIndex()) + 1)
    res_arr[int(trt.getIndex())] = clock
    setf(wstore, STc, "resources", res_arr)
    ACfg, ASp, ADefs = JClass(PKG + "ArmoryCfg"), JClass(PKG + "ArmorySpawn"), JClass(PKG + "ArmoryDefs")
    ASys = JClass(PKG + "ArmorySpawnSys")
    ADDR = JClass("com.hypixel.hytale.component.AddReason")
    check(str(wstore.getResource(TRSc.getResourceType()).getNow()) == "2026-10-03T12:00:00Z", "S: the test store answers the world clock like the game's")

    def shot(pid, yaw=0.3, pitch=-0.2, despawn=True):
        h_ = reg_.newHolder()
        pc_ = LPCc(pid)
        h_.putComponent(LPCc.getComponentType(), pc_)
        if despawn:      # = ProjectileComponent.assembleDefaultProjectile: DespawnComponent.despawnInMilliseconds(time, 60000)
            h_.putComponent(DSPc.getComponentType(), DSPc.despawnInMilliseconds(clock, 60000))
        ok_ = bool(pc_.initialize())
        pc_.shoot(h_, UUID.randomUUID(), 1.0, 70.0, 2.0, JFloat(yaw), JFloat(pitch))
        return h_, pc_, ok_

    def life_of(h_):
        """seconds from the clock's now to the holder's despawn (None = no DespawnComponent)"""
        d_ = h_.getComponent(DSPc.getComponentType())
        if d_ is None or d_.getDespawn() is None:
            return None
        return round(float(JClass("java.time.Duration").between(NOW, d_.getDespawn()).toMillis()) / 1000.0, 3)

    def vel(pc_):
        v_ = ASp.launchVelocity(pc_.getSimplePhysicsProvider())
        return None if v_ is None else math.sqrt(v_.x() * v_.x() + v_.y() * v_.y() + v_.z() * v_.z())

    def scale_of(h_):
        e_ = h_.getComponent(ESCc.getComponentType())
        return None if e_ is None else round(float(e_.getScale()), 4)
    ACfg.useDefaults()
    sys_ = ASys(True)
    h, pc, ok = shot(QORB["Copper"])
    check(ok and abs(vel(pc) - 90.0) < 1e-6 and scale_of(h) is None and life_of(h) == 60.0,
          "S: a real quick orb after shoot(): launch velocity 90 (nextTickVelocity), no scale yet, the vanilla despawn in 60 s: %s / %s" % (vel(pc), life_of(h)))
    sys_.onEntityAdd(h, ADDR.SPAWN, wstore)
    check(scale_of(h) == 0.6 and abs(vel(pc) - 90.0) < 1e-6 and life_of(h) == 5.0,
          "S (T6): ArmorySpawnSys on SPAWN -> EntityScaleComponent 0.6, speed untouched at the default 3x, despawn moved to now + 5 s (reach row): %s" % life_of(h))
    ACfg.QUICK_SPEED = 1.5
    ACfg.QUICK_SIZE = 40
    ACfg.QUICK_LIFE = 2
    h, pc, ok = shot(SQORB["Iron"])
    v_before = ASp.launchVelocity(pc.getSimplePhysicsProvider())
    dir_before = (v_before.x(), v_before.y(), v_before.z())
    sys_.onEntityAdd(h, ADDR.SPAWN, wstore)
    v_after = ASp.launchVelocity(pc.getSimplePhysicsProvider())
    check(scale_of(h) == 0.4 and abs(vel(pc) - 45.0) < 1e-6 and abs(v_after.x() - dir_before[0] * 0.5) < 1e-9
          and abs(v_after.y() - dir_before[1] * 0.5) < 1e-9 and abs(v_after.z() - dir_before[2] * 0.5) < 1e-9 and life_of(h) == 2.0,
          "S (T6): quick.speed 1.5 / quick.size 40 / quick.life 2 -> a staff quick orb gets scale 0.4, half its launch velocity (same direction), "
          "despawn in 2 s: %s / %s" % (vel(pc), life_of(h)))
    ACfg.useDefaults()
    for pid, why, reason in ((ORB["Copper"], "a charged wand orb", ADDR.SPAWN), (SORB["Copper"], "a charged staff orb", ADDR.SPAWN),
                             (VAN_ORB, "the vanilla orb", ADDR.SPAWN), (QORB["Iron"], "a quick orb LOADED from disk", ADDR.LOAD)):
        h, pc, ok = shot(pid)
        v0 = vel(pc)
        sys_.onEntityAdd(h, reason, wstore)
        check(scale_of(h) is None and abs(vel(pc) - v0) < 1e-9 and life_of(h) == 60.0,
              "S (T6): %s is left alone (no scale, velocity untouched, the vanilla 60 s despawn)" % why)
    ACfg.PART_SPAWN = False
    h, pc, ok = shot(QORB["Iron"])
    sys_.onEntityAdd(h, ADDR.SPAWN, wstore)
    check(scale_of(h) is None and abs(vel(pc) - 90.0) < 1e-6 and life_of(h) == 60.0, "S (T6): part.spawn off -> the built-in orb (no scale, 90, 60 s)")
    ACfg.useDefaults()
    # fix round: the reach row's edges - 60 = vanilla (nothing moves), never LATER than the despawn the orb already has, an orb without a
    # DespawnComponent gets one, no store (never in the game) = untouched without an exception
    ACfg.QUICK_LIFE = 60
    h, pc, ok = shot(QORB["Mithril"])
    sys_.onEntityAdd(h, ADDR.SPAWN, wstore)
    l60 = life_of(h)
    ACfg.useDefaults()
    h, pc, ok = shot(QORB["Mithril"])
    h.getComponent(DSPc.getComponentType()).setDespawn(NOW.plusMillis(1500))
    sys_.onEntityAdd(h, ADDR.SPAWN, wstore)
    l_early = life_of(h)
    h, pc, ok = shot(QORB["Thorium"], despawn=False)
    sys_.onEntityAdd(h, ADDR.SPAWN, wstore)
    l_none = life_of(h)
    h, pc, ok = shot(QORB["Cobalt"])
    sys_.onEntityAdd(h, ADDR.SPAWN, None)
    l_nostore = (life_of(h), scale_of(h))
    check(l60 == 60.0 and l_early == 1.5 and l_none == 5.0 and l_nostore == (60.0, 0.6),
          "S (fix round): quick.life 60 = the vanilla 60 s; an orb that already despawns sooner (1.5 s) keeps it; an orb without a DespawnComponent "
          "gets now + 5 s; no store = the reach is skipped (size still applied), no exception: %s / %s / %s / %s" % (l60, l_early, l_none, l_nostore))
    first = [m_ for lv_, m_ in records() if "first quick orb after start" in m_]
    check(len(first) == 1 and "SkyyArmory_QuickOrb_Copper - scale 0.6, launch speed 90.0 blocks/s" in first[0] and "despawns in 5.0 s (reach row 5 s)" in first[0],
          "S (T-live): the first quick orb logs ONE INFO line with its scale, speed and reach: %s" % first[:1])
    sp_m = ADefs.spawnPlan(QORB["Wood"], True, True, 60, 1.5, "model", 60)
    check(ADefs.spawnPlan(QORB["Wood"], True, True, 100, 3.0, "scale", 60) is None and ADefs.spawnPlan(QORB["Wood"], True, True, 60, 3.0, "model", 60) is None
          and sp_m is not None and [float(x) for x in sp_m] == [0.0, 0.5, 0.0], "S: size 100 + speed 3 + reach 60 = nothing to do; mode 'model' never adds a scale (speed only)")
    pl_ = [ADefs.spawnPlan(QORB["Wood"], True, True, 100, 3.0, "scale", s_) for s_ in (5, 59, 60, 61, 0, -3)]
    check([None if x is None else [float(y) for y in x] for x in pl_] == [[0.0, 1.0, 5000.0], [0.0, 1.0, 59000.0], None, None, None, None]
          and ADefs.spawnPlan(ORB["Copper"], True, True, 60, 1.5, "scale", 5) is None,
          "S (fix round): spawnPlan's reach - 5 s / 59 s move the despawn, 60+ / 0 / negative keep the vanilla one; a charged orb never gets a plan")
    print("S. spawn hook on real Holder + ProjectileComponent + DespawnComponent objects: scale 0.6 / 0.4, speed rows, reach 5 / 2 s, charged / vanilla / "
          "LOAD / part off untouched")

    # ---------------- U. T12 ArmoryTuneSys on REAL Damage objects
    DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DPS = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    SBc = JClass("armoryharness.StubBuffer")
    buf = U.allocateInstance(SBc.class_)
    TS = JClass(PKG + "ArmoryTuneSys")
    tsys = TS(True)
    shooter = REFc(JObject(None, JClass("com.hypixel.hytale.component.Store")), 1)
    nref = [10]

    def hit(pid, amount=100.0):
        nref[0] += 1
        pr_ = REFc(JObject(None, JClass("com.hypixel.hytale.component.Store")), nref[0])
        SBc.COMP.put(pr_, LPCc(pid))
        d_ = DMGc(DPS(shooter, pr_), 0, JFloat(amount))
        tsys.handle(0, None, None, buf, d_)
        return round(float(d_.getAmount()), 4)
    check(hit(ORB["Copper"]) == 100.0 and hit(QORB["Copper"]) == 100.0 and hit(VAN_ORB) == 100.0, "U (T12): 100% / quick 20 = untouched")
    ACfg.TUNE_W = JArray(JDouble)([100, 50, 100, 100, 100, 100, 100, 100])
    check(hit(ORB["Copper"]) == 50.0 and hit(QORB["Copper"]) == 50.0 and hit(ORB["Iron"]) == 100.0 and hit(SORB["Copper"]) == 100.0,
          "U (T12): Copper wand 50% halves both Copper wand shots, nothing else")
    ACfg.TUNE_W = JArray(JDouble)([200, 100, 100, 100, 100, 100, 100, 100])
    check(hit(QORB["Wood"]) == 200.0 and hit(VAN_ORB) == 100.0, "U (T12): the Wood row moves only SkyyArmory_QuickOrb_Wood - never the shared vanilla orb")
    ACfg.useDefaults()
    ACfg.QUICK_DAMAGE = 40
    check(hit(QORB["Mithril"]) == 200.0 and hit(SQORB["Mithril"]) == 200.0 and hit(ORB["Mithril"]) == 100.0 and hit(SORB["Mithril"]) == 100.0,
          "U (T12): quick.damage 40 doubles quick hits only (wand + staff)")
    ACfg.TUNE_S = JArray(JDouble)([100, 100, 100, 100, 100, 100, 300, 100])
    check(hit(SORB["Mithril"]) == 300.0 and hit(SQORB["Mithril"]) == 600.0 and hit(SORB["Onyxium"]) == 100.0, "U (T12): Mithril staff 300% (+ quick 40)")
    ACfg.PART_TUNE = False
    check(hit(SORB["Mithril"]) == 100.0 and hit(QORB["Mithril"]) == 100.0, "U (T12): part.tune off = untouched")
    ACfg.useDefaults()
    d_ = DMGc(JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")(shooter), 0, JFloat(100.0))
    tsys.handle(0, None, None, buf, d_)
    check(float(d_.getAmount()) == 100.0, "U: a melee hit (EntitySource) is never touched")
    pr_dead = REFc(JObject(None, JClass("com.hypixel.hytale.component.Store")))
    d_ = DMGc(DPS(shooter, pr_dead), 0, JFloat(100.0))
    tsys.handle(0, None, None, buf, d_)
    check(float(d_.getAmount()) == 100.0, "U: a projectile ref that is no longer valid is never touched")
    fm = [ADefs.tuneFactor(p_, True, JArray(JDouble)([100] * 8), JArray(JDouble)([100] * 8), 20) for p_ in list(JPRJ) + [VAN_ORB, "Arrow_FullCharge", None]]
    check(all(abs(float(x) - 1.0) < 1e-9 for x in fm), "U: tuneFactor = 1 for every id at the defaults (31 ours + foreign + null)")
    print("U. ArmoryTuneSys on real Damage objects: per-weapon %, Wood quick-only, quick.damage, part off, melee / dead refs untouched")

    # ---------------- K. T12 the config kit (rows, read-only rows, tset + check hook, set / deny, reload)
    Rows, Fn, Pub = JClass(PKG + "CfgRows"), JClass(PKG + "CfgFn"), JClass(PKG + "CfgPub")
    keys = [str(k) for k in Rows.KEYS]
    flags = dict(zip(keys, [str(f) for f in Rows.FLAGS]))
    types = dict(zip(keys, [str(t) for t in Rows.TYPES]))
    defs = dict(zip(keys, [str(d) for d in Rows.DEFS]))
    helps = dict(zip(keys, [str(h) for h in Rows.HELPS]))
    want_rows = ["part.tune", "tune.wand", "tune.staff", "quick.damage", "part.spawn", "quick.size", "quick.speed", "quick.life", "check.on", "check.share"]
    check(keys[:10] == want_rows and all(k.startswith("fixed.") for k in keys[10:]) and len(keys) == 10 + 8 + 8 + 5,
          "K: 10 live rows (fix round: + quick.life) + 21 read-only rows (8 wands, 8 staffs, quick shot, art, Wood tap, staff tap, staff base): %s" % keys[:10])
    check(types["tune.wand"] == "table" and types["tune.staff"] == "table" and "part" in flags["part.tune"].split(",") and "danger" in flags["part.spawn"].split(",")
          and all(flags[k] == "ro" for k in keys[10:]) and all(len(h) <= 100 for h in helps.values()) and types["quick.life"] == "int"
          and defs["quick.life"] == "5" and flags["quick.life"] == "new", "K: row types / flags / help lengths; quick.life int 5 s, new shots only")
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    ADMIN = UUID.fromString("00000000-0000-0000-0003-000000000001")
    PLAIN = UUID.fromString("00000000-0000-0000-0003-000000000002")

    def jset(*xs):
        s_ = HashSet()
        for x in xs:
            s_.add(x)
        return s_

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "armory-test"
        @JOverride
        def getUserPermissions(self, u): return jset("skyyarmory.admin") if str(u) == str(ADMIN) else HashSet()
        @JOverride
        def getGroupsForUser(self, u): return jset("hytale:Adventurer")
        @JOverride
        def getGroupPermissions(self, g): return HashSet()
        @JOverride
        def getEffectiveGroupPermissions(self, g): return HashSet()
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset("hytale:Adventurer")
        @JOverride
        def getUsersWithPermission(self, n): return HashSet()
        @JOverride
        def addUserPermissions(self, *a): return None
        @JOverride
        def removeUserPermissions(self, *a): return None
        @JOverride
        def addUserToGroup(self, *a): return None
        @JOverride
        def addGroupPermissions(self, *a): return None
        @JOverride
        def removeGroupPermissions(self, *a): return None
        @JOverride
        def removeUserFromGroup(self, *a): return None
        @JOverride
        def setUserGroup(self, *a): return None
    pm = U.allocateInstance(PM.class_)
    provs = ArrayList()
    provs.add(Prov())
    setf(pm, PM, "providers", provs)
    setf(pm, PM, "virtualGroups", HashMap())
    jfield(PM, "instance").set(None, pm)
    kdir = os.path.join(SCRATCH, "kit", "mods")
    shutil.rmtree(os.path.dirname(kdir), ignore_errors=True)
    os.makedirs(kdir)
    ACfg.DIR = Paths.get(os.path.join(kdir, "Skyy_SkyyArmory"))
    ACfg.FILE = ACfg.DIR.resolve("config.properties")
    ACfg.load()
    Pub.start(Paths.get(kdir), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory"))
    fn = Fn()

    def op(*a):
        return fn.apply(JArray(JObject)(list(a)))
    r = op("keys", "tune.wand", "")
    check(r is not None and sorted(str(x) for x in r[0]) == sorted(METALS) and all(str(v) == "100" for v in r[2]), "K: tune.wand lists the 8 wands at 100")
    def settle(cond, secs=4.0):
        """a reload: table row applies when the kit's save task has written the file and run ArmoryCfg.reloadAll (~0.5 s)"""
        Pub.flush()
        t0 = time.time()
        while time.time() - t0 < secs:
            if cond():
                return round(time.time() - t0, 2)
            time.sleep(0.05)
        return None
    r = op("tset", "tune.wand", "Copper", "50", ADMIN, "admin", "yes", "menu")
    w_ = settle(lambda: float(ACfg.tunePct(False, 1)) == 50.0)
    check(str(r[0]) == "ok" and w_ is not None and hit(ORB["Copper"]) == 50.0 and hit(ORB["Iron"]) == 100.0,
          "K (T12): Server Setup > Armory: Copper 50%% halves its damage (kit tset -> file -> reload routine -> ArmoryCfg) within %s s: %s" % (
              w_, [str(x) for x in r]))
    r = op("tset", "tune.wand", "Copper", "100", ADMIN, "admin", "yes", "menu")
    check(str(r[0]) == "ok" and settle(lambda: float(ACfg.tunePct(False, 1)) == 100.0) is not None and hit(ORB["Copper"]) == 100.0, "K: back to 100")
    r = op("tset", "tune.wand", "Bronze", "50", ADMIN, "admin", "yes", "menu")
    check(str(r[0]) in ("bad", "unknown") or r is None, "K: an entry that is no weapon is refused (check hook / addMode none): %s" % (None if r is None else [str(x) for x in r]))
    r = op("tset", "tune.staff", "Iron", "600", ADMIN, "admin", "yes", "menu")
    check(str(r[0]) == "bad", "K: 600% is outside 10-500 -> bad")
    r = op("set", "quick.damage", "40", ADMIN, "admin", "yes", "menu")
    check(str(r[0]) == "ok" and int(ACfg.QUICK_DAMAGE) == 40 and hit(QORB["Iron"]) == 200.0 and hit(ORB["Iron"]) == 100.0, "K (T12): quick shot damage 40 doubles quick hits only")
    op("set", "quick.damage", "20", ADMIN, "admin", "yes", "menu")
    r = op("set", "quick.size", "100", PLAIN, "plain", "yes", "menu")
    check(str(r[0]) == "denied" and int(ACfg.QUICK_SIZE) == 60, "K: a player without skyyarmory.admin is denied")
    r = op("set", "quick.life", "12", ADMIN, "admin", "yes", "menu")
    r2 = op("set", "quick.life", "61", ADMIN, "admin", "yes", "menu")
    check(str(r[0]) == "ok" and int(ACfg.QUICK_LIFE) == 12 and str(r2[0]) == "bad" and int(ACfg.QUICK_LIFE) == 12,
          "K (fix round): Quick shot reach 12 s applies live (new shots), 61 is outside 1-60 -> bad: %s / %s" % ([str(x) for x in r], [str(x) for x in r2]))
    op("set", "quick.life", "5", ADMIN, "admin", "yes", "menu")
    r = op("set", "fixed.wand.Copper", "x", ADMIN, "admin", "yes", "menu")
    check(r is None or str(r[0]) in ("bad", "denied", "unknown") , "K: read-only rows cannot be set: %s" % (None if r is None else [str(x) for x in r]))
    check(str(op("get", "fixed.wand.Copper")) == "10 / 2 Mana - x2.25 - 56 / 11 damage - Lv 10-18"
          and str(op("get", "fixed.staff.Mithril")) == "170 / 34 Mana - x21 - 1050 / 210 damage - Lv 40-49"
          and str(op("get", "fixed.art")) == "B - wood handle + metal head (LOCKED)", "K: read-only rows show the fixed numbers: %s" % op("get", "fixed.wand.Copper"))
    r = op("set", "part.spawn", "false", ADMIN, "admin", "", "menu")
    check(str(r[0]) == "confirm", "K: switching a part off asks to confirm first")
    Pub.flush()
    time.sleep(0.8)
    txt = open(os.path.join(kdir, "Skyy_SkyyArmory", "config.properties"), "rb").read().decode("latin-1")
    check("tune.wand.Copper=100" in txt and "quick.damage=20" in txt and "quick.size=60" in txt and "quick.life=5" in txt,
          "K: the file follows the in-game changes (written by the kit)")
    Pub.shutdown()
    ACfg.useDefaults()
    print("K. config kit: 31 rows, tset / set / deny / bad / confirm through the kit's op function, live effect on real Damage objects")

    # ---------------- B. bridge keys + armory:fn:info
    PL = JClass(PKG + "SkyyArmoryPlugin")
    PL.publish()
    br = ADefs.bridge()
    info = br.get("armory:fn:info")
    check(str(br.get("armory:quick")) == ",".join([QORB[m] for m in METALS] + [SQORB[m] for m in METALS])
          and str(br.get("gear:loot:add:SkyyArmory")) == ",".join(WID[m] for m in NEW), "B: armory:quick (16 ids) and gear:loot:add:SkyyArmory (7 wands)")
    wt = str(br.get("armory:wands")).split(",")
    check(len(wt) == 8 and wt[1] == "Weapon_Wand_Copper:10:2:2.25:56:11" and wt[0] == "Weapon_Wand_Wood:5:1:1:25:5", "B: armory:wands format id:charged:quick:mult:dmg:dmg")
    stx = str(br.get("armory:staffs")).split(",")
    check(len(stx) == 8 and stx[6] == "Weapon_Staff_Mithril:170:34:21:1050:210", "B: armory:staffs")

    def fi(kind, iid):
        """the 6 numbers of an armory:fn:info answer (None = no answer)"""
        r_ = info.apply(JArray(JObject)([kind, iid]))
        return None if r_ is None else [float(x.doubleValue()) if hasattr(x, "doubleValue") else float(x) for x in list(r_)[:6]]

    def fids(kind, iid):
        """fix round: elements 6 + 7 = the weapon's own charged / quick projectile ids"""
        r_ = info.apply(JArray(JObject)([kind, iid]))
        # convertStrings=True: a java.lang.String element arrives as a Python str (any other Java object would not)
        return None if r_ is None else (len(r_), str(r_[6]), str(r_[7]), "java.lang.String" if isinstance(r_[6], str) and isinstance(r_[7], str) else repr(type(r_[6])))
    check(fi("wand", "Weapon_Wand_Mithril") == [85, 17, 21.0, 525, 105, 100.0] and fi("wand", "Weapon_Wand_Wood_Rotten") == [5, 1, 1.0, 25, 5, 100.0]
          and fi("wand", "Weapon_Wand_Tribal") == fi("wand", "Weapon_Wand_Wood") and fi("staff", "Weapon_Staff_Wood") == [10, 2, 1.0, 50, 10, 100.0]
          and fi("staff", "Weapon_Wand_Copper") is None and fi("wand", "Weapon_Staff_Copper") is None and fi("wand", "Weapon_Wand_Root") is None,
          "B (15.5): armory:fn:info - Mithril wand 85/17 x21 525/105, Rotten = Tribal = Wood 5/1, Wood staff 10/2 50/10; wrong kinds / unknown wands -> null")
    want_ids = [(WID[m], "wand", ORB.get(m, VAN_ORB), QORB[m]) for m in METALS] + [(i_, "wand", VAN_ORB, QORB["Wood"]) for i_ in ("Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal")] \
        + [(SID[m], "staff", SORB[m], SQORB[m]) for m in METALS]
    got_ids = [(i_, fids(k_, i_)) for i_, k_, c_, q_ in want_ids]
    check(all(g_ == (8, c_, q_, "java.lang.String") for (i_, k_, c_, q_), (_i, g_) in zip(want_ids, got_ids))
          and all(c_ in JPRJ or c_ == VAN_ORB for i_, k_, c_, q_ in want_ids) and all(q_ in JPRJ for i_, k_, c_, q_ in want_ids),
          "B (fix round): armory:fn:info elements 6 + 7 = the weapon's OWN charged / quick projectile ids (the Wood / Rotten / Tribal wands: the vanilla "
          "orb + SkyyArmory_QuickOrb_Wood), each a shipped projectile: %s" % [g for g in got_ids if g[1] is None or g[1][0] != 8][:3])
    r_ = info.apply(JArray(JObject)(["staff", "Weapon_Staff_Wood"]))
    check(str(r_[0].getClass().getName()) == "java.lang.Integer" and str(r_[2].getClass().getName()) == "java.lang.Double",
          "B: the element types are java.lang.Integer / Double (the partner reads a[0] as a Number - SkyySkills 0.4.15 ManaCost.armory)")
    check(info.apply("nope") is None and info.apply(JArray(JObject)(["wand"])) is None, "B: bad arguments -> null, never throws")
    PL.unpublish()
    check(br.get("armory:fn:info") is None and br.get("gear:loot:add:SkyyArmory") is None, "B: shutdown's unpublish removes the keys")
    print("B. bridge: armory:wands / staffs / quick / fn:info / loot published in the agreed formats; unpublished at shutdown")

    # ---------------- M. T12 the Mana check from a fake config:fn:SkyySkills
    @JImplements("java.util.function.Function")
    class FakeSkills:
        def __init__(self, vals, tables): self.vals, self.tables = vals, tables

        @JOverride
        def apply(self, o):
            a = list(o)
            if str(a[0]) == "get":
                v = self.vals.get(str(a[1]))
                return v
            if str(a[0]) == "keys":
                t = self.tables.get(str(a[1]))
                if t is None:
                    return None
                es = JArray(JString)(list(t.keys()))
                return JArray(JObject)([es, es, JArray(JString)(list(t.values()))])
            return None
    vals14 = {"mana.base": "10", "mana.base.enabled": "true", "overall.manaPerLevel": "0.2", "perk.alchemy.manaPerLevel": "0.2"}
    br.put("config:fn:SkyySkills", FakeSkills(vals14, {"mana.classBase": {"Mage": "30", "Priest": "30"}}))
    r = CHK.manaCheck()
    check(str(r[0]) == "warn" and "Cobalt Wand at Divinity 25: 40 of 30.4 max Mana - CANNOT be cast" in str(r[1]) and "comes with SkyySkills 0.4.15" in str(r[1]),
          "M (T12): with 0.4.14's rows the Mana check WARNs (Cobalt+ cannot be cast) and names 0.4.15's row: %s" % str(r[1])[:300])
    br.put("config:fn:SkyySkills", FakeSkills(vals14, {"mana.classBase": {"Mage": "30", "Priest": "30"}, "mana.classPerLevel": {"Mage": "10", "Priest": "5"}}))
    r = CHK.manaCheck()
    check(str(r[0]) == "info" and "Mithril 85/230.8 37%" in str(r[1]) and "Mithril 170/430.8 39%" in str(r[1]) and "every charged shot within 40%" in str(r[1]),
          "M (T12): with 0.4.15's rows (Priest 5, Mage 10): INFO, Mithril 85/230.8 37%%, staff 170/430.8 39%%: %s" % str(r[1])[:400])
    ACfg.CHECK_SHARE = 30
    r = CHK.manaCheck()
    check(str(r[0]) == "warn" and "Mithril Wand at Divinity 40: 85 of 230.8 max Mana (37% > 30%)" in str(r[1]), "M: check.share 30 -> WARN per weapon over 30%")
    ACfg.useDefaults()
    vals_off = dict(vals14, **{"mana.base.enabled": "false"})
    br.put("config:fn:SkyySkills", FakeSkills(vals_off, {"mana.classBase": {"Mage": "30", "Priest": "30"}, "mana.classPerLevel": {"Mage": "10", "Priest": "5"}}))
    r = CHK.manaCheck()
    check(str(r[0]) == "warn" and "Base Mana OFF" in str(r[1]), "M: Base Mana switched off -> the class rows count 0, WARN")
    br.remove("config:fn:SkyySkills")
    r = CHK.manaCheck()
    check(str(r[0]) == "skip", "M: no SkyySkills -> skipped: %s" % r[1])
    CHK.MANA_SIG = ""
    br.put("config:fn:SkyySkills", FakeSkills(vals14, {"mana.classBase": {"Mage": "30", "Priest": "30"}, "mana.classPerLevel": {"Mage": "10", "Priest": "5"}}))
    CHK.manaTick(False)
    check(str(br.get("armory:check")).startswith("Mana check") and str(CHK.MANA_LAST) == str(br.get("armory:check")), "M: manaTick publishes armory:check")
    n0 = len(records())
    CHK.manaTick(False)
    check(len(records()) == n0, "M: no epoch change -> no new log line (no periodic spam)")
    br.put("config:epoch:SkyySkills", JClass("java.lang.Long")(7))
    CHK.manaTick(False)
    check(len(records()) == n0 + 1, "M: SkyySkills' settings epoch changed -> the check runs again (one line)")
    print("M. Mana check: WARN with 0.4.14's rows, INFO with 0.4.15's, share row, Base Mana off, skip without SkyySkills, epoch-driven")

    # ---------------- T. the REAL setup() twice on a scratch COPY of the live world's mods folder
    troot = os.path.join(SCRATCH, "twice", "mods")
    shutil.rmtree(os.path.dirname(troot), ignore_errors=True)
    os.makedirs(troot)
    copied = []
    for sub in ("Skyy_SkyySkills", "Skyy_SkyyClasses", "Skyy_SkyyGear"):
        sp = os.path.join(LIVE, sub)
        if os.path.isdir(sp):
            for fn_ in ("xp.properties", "config.properties"):
                if os.path.isfile(os.path.join(sp, fn_)):
                    os.makedirs(os.path.join(troot, sub), exist_ok=True)
                    shutil.copy2(os.path.join(sp, fn_), os.path.join(troot, sub, fn_))
                    copied.append(sub + "/" + fn_)
    if os.path.isdir(os.path.join(LIVE, "Skyy_SkyyArmory")):
        shutil.copytree(os.path.join(LIVE, "Skyy_SkyyArmory"), os.path.join(troot, "Skyy_SkyyArmory"))
        copied.append("Skyy_SkyyArmory/")
    check(len(copied) >= 3, "T: live data copied into scratch (read only): %s" % copied)
    PBc = JClass("com.hypixel.hytale.server.core.plugin.PluginBase")
    CPc = JClass("armoryharness.CaptureProxy")

    def snap():
        out = {}
        for dp, _dn, fns in os.walk(troot):
            for f_ in fns:
                p_ = os.path.join(dp, f_)
                out[os.path.relpath(p_, troot)] = (open(p_, "rb").read(), os.path.getmtime(p_))
        return out
    s0 = snap()
    caps = []

    def start_plugin():
        CPc.CAP.clear()
        p_ = U.allocateInstance(PL.class_)
        setf(p_, PBc, "logger", JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory"))
        setf(p_, PBc, "dataDirectory", Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1")))
        setf(p_, PBc, "entityStoreRegistry", U.allocateInstance(CPc.class_))
        setf(p_, PBc, "shutdownTasks", JClass("java.util.concurrent.CopyOnWriteArrayList")())
        m_ = PL.class_.getDeclaredMethod("setup")
        m_.setAccessible(True)
        m_.invoke(p_)
        caps.append([s_ for s_ in CPc.CAP])
        Pub.flush()
        time.sleep(0.7)
        sd_ = PL.class_.getDeclaredMethod("shutdown")
        sd_.setAccessible(True)
        try:
            sd_.invoke(p_)
        except Exception:
            Pub.shutdown()
        return p_
    n_log0 = len(records())
    start_plugin()
    s1 = snap()
    time.sleep(1.1)
    start_plugin()
    s2 = snap()
    ready = [m_ for lv_, m_ in records()[n_log0:] if "[SkyyArmory] 0.1 ready" in m_]
    check(len(ready) == 2 and "7 metal wands (style B)" in ready[0] and "8 ladder staffs" in ready[0] and "damage tune on" in ready[0],
          "T: setup() ran twice; ready line: %s" % (ready[:1] or [None])[0])
    new_files = sorted(set(s1) - set(s0))
    check(new_files == [os.path.join("Skyy_SkyyArmory", "config.properties")] or "Skyy_SkyyArmory/" in copied,
          "T: the first start writes only Skyy_SkyyArmory/config.properties: %s" % new_files)
    check(all(s1[k] == s0[k] for k in s0), "T: no other mod's file was touched by either start (byte + time identical)")
    check(sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "T: the second start changes nothing (no churn): %s" % sorted(set(s1) ^ set(s2)))
    cfgtxt = open(os.path.join(troot, "Skyy_SkyyArmory", "config.properties"), "rb").read().decode("latin-1")
    check(cfgtxt == str(ACfg.DEF_CFG) or "Skyy_SkyyArmory/" in copied, "T: the written file is the jar's default text")
    check(len(caps) == 2 and all(len(c) == 2 for c in caps) and str(caps[0][0].getClass().getSimpleName()) == "ArmoryTuneSys"
          and str(caps[0][1].getClass().getSimpleName()) == "ArmorySpawnSys" and bool(caps[0][0].ordered) and bool(caps[0][1].ordered),
          "T: setup() hands the registry exactly 2 systems (one registerSystem each), both ordered (before armour / after the vanilla projectile setup)")
    dep_t = [str(d.toString()) for d in caps[0][0].getDependencies()]
    dep_s = [str(d.toString()) for d in caps[0][1].getDependencies()]
    check(len(dep_t) == 1 and "ArmorDamageReduction" in dep_t[0] and "BEFORE" in dep_t[0].upper() and len(dep_s) == 1 and "OnAddHolderSystem" in dep_s[0]
          and "AFTER" in dep_s[0].upper(), "T: dependencies %s / %s" % (dep_t, dep_s))
    check(br.get("armory:fn:info") is None, "T: after shutdown the bridge keys are gone")
    print("T. real setup() twice on a copy of the live data (%d files copied): only our config file written, no churn, 2 systems, bridge on / off" % len(copied))
    JClass(PKG + "ArmoryCheck").STOP = True
    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both
    bad_txt = json.dumps(dict(JINT["SkyyArmory_Wand_Cast_Copper"], Costs={"Mana": 11}))
    ob, wb = dec(INTc, "SkyyArmory_Wand_Cast_Copper", bad_txt)
    load(INTc, [ob], "Other:Pack")
    r = CHK.packCheck()
    check(str(r[0]) == "warn" and "ANOTHER PACK WINS for 1: SkyyArmory_Wand_Cast_Copper (Other:Pack)" in str(r[1])
          and "SkyyArmory_Wand_Cast_Copper checks 11.0 Mana, not 10.0" in str(r[1]), "L2 (T-live): another pack winning with 11 Mana -> one WARN naming the "
                                                                                     "pack and the live value: %s" % str(r[1])[:400])
    print("L2. T-live WARN: another pack winning an interaction with a wrong number is named (pack + live value)")


# ============================================================================================================ V. T14 the whole SET in one JVM
def set_part():
    jars = []
    for mod, ver in PINS:
        jp = os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver))
        if os.path.isfile(jp) and mod != MOD:
            jars.append(jp)
    jars.append(JAR)
    child = os.path.join(SCRATCH, "set_child.py")
    open(child, "w", encoding="utf-8").write(r'''
import sys, os, zipfile, json
sys.path.insert(0, %r)
import skyybuild as B, jpype
jars = json.loads(sys.argv[1])
tmp = sys.argv[2]
jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
if not os.path.exists(jvm):
    jvm = B._jvm()
jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp, classpath=[B.SERVER_JAR] + jars, convertStrings=True)
Cls = jpype.JClass("java.lang.Class")
L = jpype.JClass("java.lang.ClassLoader").getSystemClassLoader()
n, bad, pk = 0, [], {}
for j in jars:
    for e in zipfile.ZipFile(j).namelist():
        if not e.endswith(".class"):
            continue
        cn = e[:-6].replace("/", ".")
        pk.setdefault(cn.rsplit(".", 1)[0], set()).add(os.path.basename(j))
        try:
            c = Cls.forName(cn, False, L)
            c.getDeclaredMethods()          # links the class = -Xverify:all verifies it (no static initializer runs)
            n += 1
        except Exception as ex:
            bad.append("%%s (%%s): %%s" %% (cn, os.path.basename(j), str(ex)[:200]))
shared = sorted(p for p, s in pk.items() if len(s) > 1)
print("SETRESULT " + json.dumps({"n": n, "bad": bad[:20], "nbad": len(bad), "jars": len(jars), "shared": shared}))
''' % TOOLS)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    out = subprocess.run([sys.executable, child, json.dumps(jars), os.path.join(SCRATCH, "tmp")], capture_output=True, text=True, env=env, timeout=1800)
    line = [l for l in out.stdout.split("\n") if l.startswith("SETRESULT ")]
    if not line:
        check(False, "V (T14): the one-JVM SET run produced no result: %s %s" % (out.stdout[-500:], out.stderr[-800:]))
        return
    res = json.loads(line[0][len("SETRESULT "):])
    check(res["nbad"] == 0 and res["n"] > 1000 and not res["shared"], "V (T14): the SET (%d jars incl. SkyyArmory) in ONE JVM with -Xverify:all - %d classes linked + "
          "verified, %d failed %s, shared packages %s" % (res["jars"], res["n"], res["nbad"], res["bad"][:3], res["shared"]))
    print("V. one JVM: %d jars, %d classes verified (-Xverify:all), 0 failures, no shared package" % (res["jars"], res["n"]))


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    try:
        if not NO_SET:
            set_part()
        jvm_part()
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        FAILS.append("harness crashed (see the traceback above)")
    print("=" * 100)
    print("SkyyArmory %s harness: %d ok, %d FAIL" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:40]:
        print("  FAIL", f)
    if not KEEP:
        try:
            JZ.close()
            AZ.close()
        except Exception:
            pass
    return 1 if FAILS else 0


if __name__ == "__main__":
    rc = main()
    sys.stdout.flush()
    sys.stderr.flush()
    if not KEEP:
        # the JVM keeps a few native files open inside tmp until the process ends: delete what we can now, the rest on the next run
        shutil.rmtree(SCRATCH, ignore_errors=True)
    os._exit(rc)
