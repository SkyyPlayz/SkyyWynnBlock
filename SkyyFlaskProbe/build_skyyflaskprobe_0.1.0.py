"""SkyyFlaskProbe 0.1.0 - build script (javassist via jpype). Round FP0 of research/Flask-Pouch-Spec.md (section 5 risks R1-R5,
section 6 "FP0 probe"). A THROWAWAY dev / test pack (like SkyyReelProbe / SkyyAbilityProbe): it proves on Hytale 0.7 that a held item
can run a COPY of a vanilla consume chain carrying ANOTHER item's effect without being used up, before FP1 builds the real Potion
Flask + Food Pouch into SkyyCooking. Op-only command, pinned for ONE Skyy test session, then retired.
Run:   python SkyyFlaskProbe/build_skyyflaskprobe_0.1.0.py   -> SkyyFlaskProbe/SkyyFlaskProbe-0.1.0.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set)
Check: python SkyyFlaskProbe/test_skyyflaskprobe_0.1.0.py    (asset closure, no overrides, bare JVM -Xverify:all, pure logic)
Smoke: python tools/smoke_test.py --jar SkyyFlaskProbe/SkyyFlaskProbe-0.1.0.jar --allow-pack-api   (game closed)

SKYY'S WORDS (2026-10-16, docs/answered/skills.md POTION FLASK + FOOD POUCH): "a healing potion that holds all the healing options you
have ... when you right click it it drinks a potion (sorted from worst to best ...)" + "(takes the normal eat/drink time to consume.)"

STABLE-NAME manifest (Name "SkyyFlaskProbe", version only in Version) -> world key "Skyy:SkyyFlaskProbe". Reads (read-only, at build
time) Assets.zip and the SET's SkyyCooking jar (SkyyCooking/SkyyCooking-<SET pin>.jar): the loaded ids copy the EFFECTIVE item - the
SkyyCooking override where Cooking overrides a vanilla food - so the probe jar must be built against the SkyyCooking version it is
deployed with (it references Cooking's effect / check interaction ids; the build asserts every referenced id exists).

WHAT IS IN THE JAR (every id new, prefix Skyy_Probe_ - never the FP1 ids Skyy_Flask_ / Skyy_Food_Pouch_)
  ITEMS (Server/Item/Items/SkyyFlaskProbe/):
    Skyy_Probe_Flask_V_<PotionId>  one per vanilla healing potion (every item whose Secondary is Root_Secondary_Consume_Potion_Health;
                                   asserted 5). Interactions.Secondary = our root copy Skyy_Probe_Root_Potion_Health.
    Skyy_Probe_Pouch_V_<FoodId>    one per food SkyyCooking ships (its overrides of the vanilla foods + its dishes + every graded copy;
                                   every item of the Cooking jar whose resolved Secondary is a Root_Secondary_Consume_Food_T<n>) - ~345
                                   ids = the spec's R4 load-cost test with the real number. Interactions.Secondary = the source's own
                                   vanilla root (it reads the HELD item's Consume_Charge var).
    Skyy_Probe_Flask_Empty / Skyy_Probe_Pouch_Empty   no Interactions (what the held item becomes when the probe store is empty).
    Every loaded id = the source item FLATTENED through its Parent chain (top-level keys; Interactions / InteractionVars merged per key)
    and then: InteractionVars = the source's, except Consume_Charge (food) whose every entry's Parent points at OUR charge copy; the
    look = ONE shared model + icon per kind (flask: vanilla Potion_Large.blockymodel + Red.png + the Potion_Health_Large icon; pouch:
    vanilla Food_Bag.blockymodel + its texture + the Food_Bread icon) - no new texture, no atlas growth; PlayerAnimationsId,
    IconProperties, InteractionConfig, Consumable = the source's (the drink / eat animation, R5); NO BlockType (a held flask must never
    be placeable - vanilla potions / food are blocks, and the crouch branch Block_Secondary would place it), NO Recipe / Tags /
    Categories, MaxStack 1, DropOnDeath false, ONE shared name / description key per kind.
  INTERACTIONS (Server/Item/Interactions/SkyyFlaskProbe/):
    Skyy_Probe_Charge_<parent>  a copy of every charge the sources use (vanilla Consume_Charge_Potion_Fast for potions; SkyyCooking's
                                Skyy_Cook_Consume_Charge_Food_T<n>_Inner_Fast for food) with the ONE "ModifyInventory
                                AdjustHeldItemQuantity -1" step replaced by "ApplyEffect Skyy_Probe_Supply_Used" + the SAME Next (SFX,
                                cooldown, Effect, the 0.2 s gap). ApplyEffect + Next is a vanilla shape (Fire.json). Charge time,
                                FailOnDamage false, HorizontalSpeedMultiplier, animation effects unchanged.
    Skyy_Probe_Cond_Potion_Health  = vanilla Condition_Consume_Potion_Health with the CooldownCondition kept (same id
                                Potion_Consume_Health -> the flask shares the vanilla 15 s potion cooldown) and its Next -> our charge.
  ROOT (Server/Item/RootInteractions/SkyyFlaskProbe/): Skyy_Probe_Root_Potion_Health = vanilla Root_Secondary_Consume_Potion_Health
                                (RequireNewClick true) -> our condition.
  EFFECT (Server/Entity/Effects/SkyyFlaskProbe/): Skyy_Probe_Supply_Used {Duration 0.5, Overwrite} (the SkyyFishing_Click shape).

RUNTIME (memory only, per player; everything on the world thread)
  The probe STORE per player + kind = an ordered list of source ids (/flaskprobe flask | pouch fills it with 10, alternating two test
  sources, so EVERY use swaps the held id - risk R3 / goal d).
  FpStartSys  EntityEventSystem<InteractionChainStartEvent> on players (the SkyyClasses AbilRuneSys shape; 0.7.2 bytecode:
              InteractionManager.syncStart fires it for every client chain and sends a cancel packet when it is cancelled).
              A Secondary chain whose held item is a probe loaded id: store head == that source -> RESERVE (take it off the store,
              remember the chain object + time + health); else (strict ON) CANCEL the event (no drink should happen) or (strict OFF)
              let it run unreserved (the R2 fallback path).
  FpTick      EntityTickingSystem on players (only works when that player has an open reservation / a pending sync / report):
              marker effect seen -> remove it, COMMIT (log ms since start, what the hand holds now = kept?), report health + effects
              1 s later, then SYNC the held item to the store's next loaded id (only once no Secondary chain runs - spec 2.5).
              Reservation open + its chain gone from InteractionManager.getChains() for 250 ms with no marker -> RETURN (put the
              source back at the store head: "cancelled - nothing used"). Marker with no reservation = a FREE use (counted, logged).
  Sync = InventoryComponent.getCombined(HOTBAR_STORAGE_BACKPACK) slot of the first probe item of that kind ->
         ItemContainer.replaceItemStackInSlot(slot, old, new ItemStack(nextId, 1)) (compare-and-swap; never a metadata stack).
COMMAND (op only: requirePermission skyyflaskprobe.admin + no permission groups, like the other probes; alias /fprobe)
  /flaskprobe                 status (both stores, held item, strict, counters, how many probe ids the item asset map holds) + help
  /flaskprobe flask | pouch   fill that store with 10 test items (alternating two kinds) and give the probe item (storage first) or
                              re-sync the one you have
  /flaskprobe wrong           set your probe item to a loaded id that is NOT the store head (then right click: strict ON = the chain
                              must be cancelled; strict OFF = a free use is logged)
  /flaskprobe strict          strict (cancel a chain whose held id is not the store head) ON / OFF, default ON
  /flaskprobe empty           empty both stores (the items become the Empty ids)
  /flaskprobe clear           remove every probe item from your hotbar / storage / backpack + empty the stores (do this before the
                              probe is retired)
Every line also goes to the server log as "[SkyyFlaskProbe] ..." - Skyy's test is read from the log afterwards.
"""
import sys, os, json, zipfile, re, copy
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI

if "--deploy" in sys.argv:
    raise SystemExit("SkyyFlaskProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1.0"
MOD = "SkyyFlaskProbe"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyyflaskprobe.admin"
SUI.verify()
COL_OK, COL_ERR = SUI.COLOR["success"], SUI.COLOR["error"]

# the SkyyCooking jar the probe is built against = the SET pin (read the SET without importing deploy_set's side effects)
_set_src = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()
_m = re.search(r'\("SkyyCooking",\s*"([0-9.]+)"\)', _set_src)
if not _m:
    raise SystemExit("SkyyCooking is not in the tools/deploy_set.py SET")
COOK_VER = _m.group(1)
COOK_JAR = os.path.join(ROOT, "SkyyCooking", "SkyyCooking-%s.jar" % COOK_VER)
if not os.path.isfile(COOK_JAR):
    raise SystemExit("build SkyyCooking %s first (%s missing)" % (COOK_VER, COOK_JAR))

PRE = "Skyy_Probe_"
FLASK_PRE, POUCH_PRE = PRE + "Flask_", PRE + "Pouch_"
FLASK_EMPTY, POUCH_EMPTY = FLASK_PRE + "Empty", POUCH_PRE + "Empty"
MARK = PRE + "Supply_Used"
ROOT_POT = PRE + "Root_Potion_Health"
COND_POT = PRE + "Cond_Potion_Health"
V_ROOT_POT = "Root_Secondary_Consume_Potion_Health"
V_COND_POT = "Condition_Consume_Potion_Health"
V_CHARGE_POT = "Consume_Charge_Potion_Fast"
ITEM_DIR = "Server/Item/Items/SkyyFlaskProbe"
INT_DIR = "Server/Item/Interactions/SkyyFlaskProbe"
ROOT_DIR = "Server/Item/RootInteractions/SkyyFlaskProbe"
FX_PATH = "Server/Entity/Effects/SkyyFlaskProbe/%s.json" % MARK
FLASK_LOOK = {"Model": "Items/Consumables/Potions/Potion_Large.blockymodel", "Texture": "Items/Consumables/Potions/Potion_Textures/Red.png",
              "Icon": "Icons/ItemsGenerated/Potion_Health_Large.png"}
POUCH_LOOK = {"Model": "Items/Consumables/Food/Food_Bag.blockymodel", "Texture": "Items/Consumables/Food/Food_Bag_Texture.png",
              "Icon": "Icons/ItemsGenerated/Food_Bread.png"}
COPY_KEYS = ("PlayerAnimationsId", "IconProperties", "InteractionConfig", "Consumable", "Quality")

az = zipfile.ZipFile(ASSETS)
cz = zipfile.ZipFile(COOK_JAR)
AZ_NAMES = set(az.namelist())
CZ_NAMES = set(cz.namelist())


def idmap(z, names, prefix):
    return dict((n.rsplit("/", 1)[1][:-5], (z, n)) for n in names if n.startswith(prefix) and n.endswith(".json"))


def rd(zn):
    z, n = zn
    return json.loads(z.read(n).decode("utf-8-sig"))


V_ITEMS, C_ITEMS = idmap(az, AZ_NAMES, "Server/Item/Items/"), idmap(cz, CZ_NAMES, "Server/Item/Items/")
ITEMS_ALL = dict(V_ITEMS)
ITEMS_ALL.update(C_ITEMS)                      # a pack file wins over the vanilla one (SkyyCooking's overrides)
INTER = dict(idmap(az, AZ_NAMES, "Server/Item/Interactions/"))
INTER.update(idmap(cz, CZ_NAMES, "Server/Item/Interactions/"))
ROOTS = dict(idmap(az, AZ_NAMES, "Server/Item/RootInteractions/"))
ROOTS.update(idmap(cz, CZ_NAMES, "Server/Item/RootInteractions/"))
EFFECTS = dict(idmap(az, AZ_NAMES, "Server/Entity/Effects/"))
EFFECTS.update(idmap(cz, CZ_NAMES, "Server/Entity/Effects/"))
MERGE_KEYS = ("Interactions", "InteractionVars", "TranslationProperties")


def flat(iid, depth=0):
    """the item resolved through its Parent chain: top-level keys, the dict keys in MERGE_KEYS merged per key (child wins)"""
    if depth > 8:
        raise SystemExit("Parent chain too deep at %s" % iid)
    d = rd(ITEMS_ALL[iid])
    p = d.pop("Parent", None)
    if not p:
        return d
    if p not in ITEMS_ALL:
        raise SystemExit("%s: Parent %s is not a known item" % (iid, p))
    base = flat(p, depth + 1)
    for k, v in d.items():
        if k in MERGE_KEYS and isinstance(v, dict) and isinstance(base.get(k), dict):
            m = dict(base[k])
            m.update(v)
            base[k] = m
        else:
            base[k] = v
    return base


files, lang = {}, []


def put(path, obj):
    if path in files:
        raise SystemExit("duplicate asset path %s" % path)
    files[path] = json.dumps(obj, indent=2)


# ================= the marker-swapped charge copies =================
CHARGES = {}          # source charge id -> our id
CHARGE_TIME = {}      # our id -> charge seconds


def swap_modify(o, out):
    """replace every {"Type": "ModifyInventory", "AdjustHeldItemQuantity": -1, "Next": X} with {"Type": "ApplyEffect", "EffectId": MARK,
    "Next": X}; counts the swaps in out[0]"""
    if isinstance(o, dict):
        if o.get("Type") == "ModifyInventory":
            if o.get("AdjustHeldItemQuantity") != -1 or sorted(o) != ["AdjustHeldItemQuantity", "Next", "Type"]:
                raise SystemExit("unexpected ModifyInventory shape %s" % json.dumps(o)[:300])
            out[0] += 1
            return {"Type": "ApplyEffect", "EffectId": MARK, "Next": swap_modify(o["Next"], out)}
        return dict((k, swap_modify(v, out)) for k, v in o.items())
    if isinstance(o, list):
        return [swap_modify(v, out) for v in o]
    return o


def charging_of(o):
    """the Charging node of a charge interaction (the interaction itself, or the one Charging inside a Serial)"""
    if o.get("Type") == "Charging":
        return o
    cs = [x for x in o.get("Interactions", []) if isinstance(x, dict) and x.get("Type") == "Charging"]
    if o.get("Type") != "Serial" or len(cs) != 1:
        raise SystemExit("charge shape changed: %s" % json.dumps(o)[:300])
    return cs[0]


def charge_copy(src_id):
    if src_id in CHARGES:
        return CHARGES[src_id]
    if src_id not in INTER:
        raise SystemExit("charge interaction %s is missing" % src_id)
    v = rd(INTER[src_id])
    if "Parent" in v:
        raise SystemExit("charge %s has a Parent - flatten it first" % src_id)
    ch = charging_of(v)
    nx = ch.get("Next") or {}
    if ch.get("FailOnDamage") is not False or len(nx) != 1:
        raise SystemExit("%s is no longer a one-step Charging with FailOnDamage false" % src_id)
    n = [0]
    o = swap_modify(copy.deepcopy(v), n)
    if n[0] != 1:
        raise SystemExit("%s: expected exactly one ModifyInventory step, found %d" % (src_id, n[0]))
    our = PRE + "Charge_" + src_id
    put("%s/%s.json" % (INT_DIR, our), o)
    CHARGES[src_id] = our
    CHARGE_TIME[our] = float(list(nx)[0])
    return our


# ---- potions: root -> condition (cooldown kept) -> our charge
V_RP, V_CP = rd(ROOTS[V_ROOT_POT]), rd(INTER[V_COND_POT])
if V_RP != {"RequireNewClick": True, "Interactions": [V_COND_POT]}:
    raise SystemExit("%s changed: %s" % (V_ROOT_POT, V_RP))
if V_CP.get("Type") != "Condition" or V_CP.get("Crouching") is not False or V_CP["Next"].get("Type") != "CooldownCondition" \
        or V_CP["Next"].get("Id") != "Potion_Consume_Health" or V_CP["Next"].get("Next") != V_CHARGE_POT:
    raise SystemExit("%s changed: %s" % (V_COND_POT, json.dumps(V_CP)))
cp = copy.deepcopy(V_CP)
cp["Next"]["Next"] = charge_copy(V_CHARGE_POT)
put("%s/%s.json" % (INT_DIR, COND_POT), cp)
rp = copy.deepcopy(V_RP)
rp["Interactions"] = [COND_POT]
put("%s/%s.json" % (ROOT_DIR, ROOT_POT), rp)
put(FX_PATH, {"Duration": 0.5, "OverlapBehavior": "Overwrite"})


def name_lines(key, name, desc):
    for pre in ("", "server."):
        lang.append("%sitems.%s.name=%s" % (pre, key, name))
        lang.append("%sitems.%s.description=%s" % (pre, key, desc))


name_lines("Skyy_Probe_Flask", "Probe Flask", "FP0 test item. Right click: drink the next potion in the probe store (it stays in your hand). /flaskprobe shows what happened. Throwaway test item.")
name_lines("Skyy_Probe_Pouch", "Probe Pouch", "FP0 test item. Right click: eat the next food in the probe store (it stays in your hand). /flaskprobe shows what happened. Throwaway test item.")
TP = {0: {"Name": "server.items.Skyy_Probe_Flask.name", "Description": "server.items.Skyy_Probe_Flask.description"},
      1: {"Name": "server.items.Skyy_Probe_Pouch.name", "Description": "server.items.Skyy_Probe_Pouch.description"}}

LOADED = {0: [], 1: []}       # kind -> [(source id, loaded id, charge id)]
VARS_SRC = {}                 # loaded id -> the source's flattened InteractionVars (self-check)


def base_item(kind):
    look = FLASK_LOOK if kind == 0 else POUCH_LOOK
    return {"TranslationProperties": dict(TP[kind]), "Icon": look["Icon"], "Model": look["Model"], "Texture": look["Texture"],
            "MaxStack": 1, "DropOnDeath": False}


def loaded_item(kind, src, f):
    d = base_item(kind)
    for k in COPY_KEYS:
        if k in f:
            d[k] = copy.deepcopy(f[k])
    iv = copy.deepcopy(f.get("InteractionVars") or {})
    charge = None
    if kind == 0:
        d["Interactions"] = {"Secondary": ROOT_POT}
        charge = CHARGES[V_CHARGE_POT]
    else:
        d["Interactions"] = {"Secondary": f["Interactions"]["Secondary"]}
        cc = iv.get("Consume_Charge")
        if not cc or not cc.get("Interactions"):
            raise SystemExit("food %s has no Consume_Charge var" % src)
        for e in cc["Interactions"]:
            if not isinstance(e, dict) or not e.get("Parent"):
                raise SystemExit("food %s: unexpected Consume_Charge entry %s" % (src, json.dumps(e)[:200]))
            e["Parent"] = charge_copy(e["Parent"])
            charge = e["Parent"]
    d["InteractionVars"] = iv
    return d, charge


# ---- flask: every vanilla healing potion
POTIONS = sorted(i for i in V_ITEMS if (flat(i).get("Interactions") or {}).get("Secondary") == V_ROOT_POT and not i.endswith("_Template"))
if len(POTIONS) != 5:
    raise SystemExit("expected 5 healing potions with %s, found %s" % (V_ROOT_POT, POTIONS))
for src in POTIONS:
    f = flat(src)
    d, ch = loaded_item(0, src, f)
    lid = FLASK_PRE + "V_" + src
    put("%s/%s.json" % (ITEM_DIR, lid), d)
    LOADED[0].append((src, lid, ch))
    VARS_SRC[lid] = f.get("InteractionVars") or {}
# ---- pouch: every food the SkyyCooking jar ships
FOODS = []
for iid in sorted(C_ITEMS):
    f = flat(iid)
    sec = (f.get("Interactions") or {}).get("Secondary") or ""
    if re.match(r"^Root_Secondary_Consume_Food_T[123]$", sec):
        FOODS.append(iid)
for src in FOODS:
    f = flat(src)
    d, ch = loaded_item(1, src, f)
    lid = POUCH_PRE + "V_" + src
    put("%s/%s.json" % (ITEM_DIR, lid), d)
    LOADED[1].append((src, lid, ch))
    VARS_SRC[lid] = f.get("InteractionVars") or {}
put("%s/%s.json" % (ITEM_DIR, FLASK_EMPTY), base_item(0))
put("%s/%s.json" % (ITEM_DIR, POUCH_EMPTY), base_item(1))
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"

# ---- the two test sources per kind (alternated in the store so every use swaps the held id)
FLASK_TEST = ["Potion_Health_Lesser", "Potion_Health_Small"]
_bread_ch = dict((s, c) for s, l, c in LOADED[1])["Food_Bread"]
_other = [s for s, l, c in LOADED[1] if s.startswith("Skyy_Cook_Food_Skyy_") and s.endswith("_G3") and c != _bread_ch]
if not _other:
    _other = [s for s, l, c in LOADED[1] if s.startswith("Skyy_Cook_Food_Skyy_") and s.endswith("_G3")]
POUCH_TEST = ["Food_Bread", sorted(_other)[0]]
for s in FLASK_TEST:
    assert s in POTIONS, s
CH_OF = dict((s, c) for k in (0, 1) for s, l, c in LOADED[k])

# ================= asset self-checks =================
for p in files:
    if p in AZ_NAMES or p in CZ_NAMES:
        if not p.endswith("server.lang"):
            raise SystemExit("asset path %s exists in Assets.zip / SkyyCooking (override)" % p)
OURS_I = set(p.rsplit("/", 1)[1][:-5] for p in files if p.startswith(INT_DIR + "/"))
OURS_R = set(p.rsplit("/", 1)[1][:-5] for p in files if p.startswith(ROOT_DIR + "/"))
OURS_IT = set(p.rsplit("/", 1)[1][:-5] for p in files if p.startswith(ITEM_DIR + "/"))
for i in OURS_I | OURS_R | OURS_IT | {MARK}:
    if i in INTER or i in ROOTS or i in ITEMS_ALL or i in EFFECTS:
        raise SystemExit("id %s clashes with a vanilla / SkyyCooking id" % i)
KNOWN_I = set(INTER) | OURS_I | set(ROOTS) | OURS_R
KNOWN_FX = set(EFFECTS) | {MARK}
missing = set()


def refs(o):
    """every id string an asset refers to (interaction / root / effect)"""
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("PlayerAnimationsId", "DefaultValue"):     # an animation-set Parent / a vanilla Replace fallback (unchecked, as vanilla)
                continue
            if k in ("Parent", "Next", "Failed", "Secondary", "Primary", "DefaultInteractions") and isinstance(v, str):
                if v not in KNOWN_I:
                    missing.add(("interaction", v))
            elif k == "Next" and isinstance(v, dict) and all(re.match(r"^[0-9.]+$", x) for x in v):
                for x in v.values():
                    if isinstance(x, str) and x not in KNOWN_I:
                        missing.add(("interaction", x))
                    refs(x)
                continue
            elif k == "Interactions" and isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and x not in KNOWN_I:
                        missing.add(("interaction", x))
            elif k in ("EffectId", "EntityEffectId") and isinstance(v, str):
                if v not in KNOWN_FX:
                    missing.add(("effect", v))
            elif k == "EntityEffectIds" and isinstance(v, list):
                for x in v:
                    if x not in KNOWN_FX:
                        missing.add(("effect", x))
            if isinstance(v, (dict, list)):
                refs(v)
    elif isinstance(o, list):
        for x in o:
            refs(x)


for p, txt in files.items():
    if p.endswith(".json"):
        refs(json.loads(txt))
if missing:
    raise SystemExit("referenced ids that exist nowhere: %s" % sorted(missing)[:20])
# every loaded id's vars = its source's flattened vars except the charge Parent
for k in (0, 1):
    for src, lid, ch in LOADED[k]:
        mine = json.loads(files["%s/%s.json" % (ITEM_DIR, lid)])["InteractionVars"]
        want = copy.deepcopy(VARS_SRC[lid])
        if k == 1:
            for e in want["Consume_Charge"]["Interactions"]:
                e["Parent"] = CHARGES[e["Parent"]]
        if json.dumps(mine, sort_keys=True) != json.dumps(want, sort_keys=True):
            raise SystemExit("%s vars differ from %s beyond the charge" % (lid, src))
for our in CHARGES.values():
    t = json.dumps(json.loads(files["%s/%s.json" % (INT_DIR, our)]))
    if "ModifyInventory" in t or MARK not in t:
        raise SystemExit("%s still removes the held item / has no marker" % our)
NLOADED = len(LOADED[0]) + len(LOADED[1])
print("assets: %d flask + %d pouch loaded ids (+2 empty) = %d items, %d charge copies %s, %d files (%d bytes), %d lang lines; SkyyCooking %s"
      % (len(LOADED[0]), len(LOADED[1]), NLOADED + 2, len(CHARGES), dict((c, CHARGE_TIME[c]) for c in CHARGES.values()), len(files),
         sum(len(v) for v in files.values()), len(lang), COOK_VER))
print("test sources: flask %s (charge %s s), pouch %s (charge %s s)" % (FLASK_TEST, [CHARGE_TIME[CH_OF[s]] for s in FLASK_TEST], POUCH_TEST,
                                                                      [CHARGE_TIME[CH_OF[s]] for s in POUCH_TEST]))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.flaskprobe"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "COLOK": COL_OK, "COLERR": COL_ERR, "MARK": MARK, "PRE": PRE,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "HOTB": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "ISST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ICSE": "com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent",
    "ICTX": "com.hypixel.hytale.server.core.entity.InteractionContext",
    "ICHN": "com.hypixel.hytale.server.core.entity.InteractionChain",
    "IMOD": "com.hypixel.hytale.server.core.modules.interaction.InteractionModule",
    "IMGR": "com.hypixel.hytale.server.core.entity.InteractionManager",
    "ITYP": "com.hypixel.hytale.protocol.InteractionType",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "getComponentType"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["PLA"], "getComponentType"),
             (T["INVC"], "getCombined"), (T["INVC"], "STORAGE_HOTBAR_BACKPACK"), (T["INVC"], "HOTBAR_STORAGE_BACKPACK"),
             (T["HOTB"], "getComponentType"), (T["HOTB"], "getActiveItem"), (T["IC"], "addItemStack"), (T["IC"], "getCapacity"),
             (T["IC"], "getItemStack"), (T["IC"], "replaceItemStackInSlot"), (T["IC"], "removeItemStackFromSlot"),
             (T["IS"], "getItemId"), (T["IS"], "isEmpty"), (T["IS"], "getQuantity"), (T["IST"], "succeeded"), (T["IST"], "getRemainder"),
             (T["ISST"], "succeeded"), (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESV"], "get"), (T["DST"], "getHealth"),
             (T["ECC"], "getComponentType"), (T["ECC"], "hasEffect"), (T["ECC"], "removeEffect"), (T["ECC"], "getActiveEffectIndexes"),
             (T["EFX"], "getAssetMap"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset"), (T["EFX"], "getId"),
             (T["ITM"], "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetMap"),
             (T["ICSE"], "getType"), (T["ICSE"], "getContext"), (T["ICSE"], "getChain"), (T["ICSE"], "getRootInteractionId"),
             (T["ICSE"], "setCancelled"), (T["ICTX"], "getHeldItem"), (T["ICHN"], "getType"), (T["ICHN"], "getChainId"),
             (T["IMOD"], "get"), (T["IMOD"], "getInteractionManagerComponent"), (T["IMGR"], "getChains"), (T["ITYP"], "Secondary"),
             (T["ACH"], "getReferenceTo"), (T["ST"], "getComponent"), (T["ST"], "getExternalData"), (T["EST"], "getWorld"),
             (T["EST"], "getStore"), (T["WLD"], "execute"), (T["WLD"], "getEntityStore"),
             (PB, "getCommandRegistry"), (PB, "getEntityStoreRegistry"), (PB, "getLogger"), (PB, "shutdown")):
    B.probe(pool, c, m)
assert pool.get(T["ICSE"]).subtypeOf(pool.get("com.hypixel.hytale.component.system.CancellableEcsEvent")), "the chain start is cancellable"
assert "java.util.Map" in [str(i.getName()) for i in pool.get("it.unimi.dsi.fastutil.ints.Int2ObjectMap").getInterfaces()], "Int2ObjectMap is no java.util.Map"
# the engine does what the hook relies on (0.7 bytecode, read-only): syncStart fires the event and sends a cancel packet when it is cancelled
from jpype import JClass
_IP, _PS, _BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")


def _calls(cls, meth):
    out = []
    for mm in pool.get(cls).getDeclaredMethods():
        if str(mm.getName()) == meth:
            bos = _BOS()
            _IP(_PS(bos)).print_(mm)
            out.append(str(bos.toString()))
    return "\n".join(out)


_sync = _calls(T["IMGR"], "syncStart")
_i = _sync.find("InteractionChainStartEvent.isCancelled")
assert _i > 0 and "InteractionManager.sendCancelPacket" in _sync[_i:_i + 1500], "syncStart no longer cancels a chain on a cancelled start event"

TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None, iface=None):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    if iface:
        c.addInterface(pool.get(iface))
    return c


def jarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs)


# ---- FpLog: server log + chat. SINK (harness hook, null in game) also receives every chat line as "<colour>|<text>".
log = mk("FpLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List SINK;")
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyFlaskProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyFlaskProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s, String col) {
  info((pr == null ? "" : "to " + pr.getUsername() + ": ") + s);
  try { if (SINK != null) SINK.add((col == null ? "" : col) + "|" + s); } catch (Throwable t) { }
  try {
    if (pr != null) {
      @MSG@ m = @MSG@.raw(s);
      if (col != null) m = m.color(col);
      pr.sendMessage(m);
    }
  } catch (Throwable t) { }
}""")

# ---- FpLogic: pure functions on ids (the harness calls them directly)
lg = mk("FpLogic")
F(lg, "public static final String FLASK_PRE = %s;" % json.dumps(FLASK_PRE))
F(lg, "public static final String POUCH_PRE = %s;" % json.dumps(POUCH_PRE))
F(lg, "public static final String FLASK_EMPTY = %s;" % json.dumps(FLASK_EMPTY))
F(lg, "public static final String POUCH_EMPTY = %s;" % json.dumps(POUCH_EMPTY))
F(lg, "public static final String[] FLASK_TEST = %s;" % jarr(FLASK_TEST))
F(lg, "public static final String[] POUCH_TEST = %s;" % jarr(POUCH_TEST))
F(lg, "public static final String[] FLASK_SRC = %s;" % jarr([s for s, l, c in LOADED[0]]))
F(lg, "public static final String[] POUCH_SRC = %s;" % jarr([s for s, l, c in LOADED[1]]))
F(lg, "public static final int NLOADED = %d;" % NLOADED)
# 0 = flask, 1 = pouch, -1 = not a probe item
M(lg, r"""
public static int kindOf(String id) {
  if (id == null) return -1;
  if (id.startsWith(FLASK_PRE)) return 0;
  if (id.startsWith(POUCH_PRE)) return 1;
  return -1;
}""")
# the source id a loaded id carries; "" = the Empty id; null = not a probe item / unknown shape
M(lg, r"""
public static String srcOf(String id) {
  int k = kindOf(id);
  if (k < 0) return null;
  String pre = k == 0 ? FLASK_PRE : POUCH_PRE;
  String rest = id.substring(pre.length());
  if (rest.equals("Empty")) return "";
  if (!rest.startsWith("V_") || rest.length() < 3) return null;
  return rest.substring(2);
}""")
M(lg, r"""
public static boolean known(int kind, String src) {
  if (src == null) return false;
  String[] a = kind == 0 ? FLASK_SRC : POUCH_SRC;
  for (int i = 0; i < a.length; i++) if (a[i].equals(src)) return true;
  return false;
}""")
M(lg, r"""
public static String loadedId(int kind, String src) {
  if (src == null || src.length() == 0) return kind == 0 ? FLASK_EMPTY : POUCH_EMPTY;
  return (kind == 0 ? FLASK_PRE : POUCH_PRE) + "V_" + src;
}""")
M(lg, r"""
public static String kindName(int kind) { return kind == 0 ? "Probe Flask" : "Probe Pouch"; }""")
# the test fill: n entries alternating the two test sources
M(lg, r"""
public static java.util.ArrayList testFill(int kind, int n) {
  String[] t = kind == 0 ? FLASK_TEST : POUCH_TEST;
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < n; i++) l.add(t[i % t.length]);
  return l;
}""")
# a known source of that kind that is NOT the given head (for /flaskprobe wrong)
M(lg, r"""
public static String wrongSrc(int kind, String head) {
  String[] a = kind == 0 ? FLASK_SRC : POUCH_SRC;
  String[] t = kind == 0 ? FLASK_TEST : POUCH_TEST;
  for (int i = a.length - 1; i >= 0; i--) {
    boolean test = false;
    for (int j = 0; j < t.length; j++) if (t[j].equals(a[i])) test = true;
    if (!test && !a[i].equals(head)) return a[i];
  }
  return null;
}""")
# "Food_Bread x5, Skyy_Cook_Food_..._G3 x5" (in store order of first appearance)
M(lg, r"""
public static String summary(java.util.List l) {
  if (l == null || l.isEmpty()) return "empty";
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  for (int i = 0; i < l.size(); i++) {
    Object k = l.get(i);
    Integer c = (Integer) m.get(k);
    m.put(k, Integer.valueOf(c == null ? 1 : c.intValue() + 1));
  }
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    if (sb.length() > 0) sb.append(", ");
    sb.append(String.valueOf(k)).append(" x").append(String.valueOf(m.get(k)));
  }
  return l.size() + " (next " + String.valueOf(l.get(0)) + "): " + sb.toString();
}""")

# ---- FpStore: the per-player probe stores + reservations + counters (memory only; world thread)
sto = mk("FpStore")
for f in ("public static final java.util.concurrent.ConcurrentHashMap Q = new java.util.concurrent.ConcurrentHashMap();",       # "<uuid>:<kind>" -> ArrayList src
          "public static final java.util.concurrent.ConcurrentHashMap RES = new java.util.concurrent.ConcurrentHashMap();",     # uuid -> Object[] {Integer kind, String src, chain, Long t0, Float hp0, Long goneSince, Integer chainId}
          "public static final java.util.concurrent.ConcurrentHashMap SYNC = new java.util.concurrent.ConcurrentHashMap();",    # uuid -> Boolean
          "public static final java.util.concurrent.ConcurrentHashMap REPORT = new java.util.concurrent.ConcurrentHashMap();",  # uuid -> Object[] {Long due, String src, Float hp0, Float hpUse}
          "public static volatile boolean STRICT = true;",
          "public static volatile long USES = 0L;", "public static volatile long RETURNS = 0L;", "public static volatile long CANCELS = 0L;",
          "public static volatile long FREE = 0L;", "public static volatile long STARTS = 0L;"):
    F(sto, f)
M(sto, r"""
public static java.util.ArrayList list(java.util.UUID u, int kind) {
  String k = String.valueOf(u) + ":" + kind;
  java.util.ArrayList l = (java.util.ArrayList) Q.get(k);
  if (l == null) { l = new java.util.ArrayList(); Q.put(k, l); }
  return l;
}""")
M(sto, r"""
public static String head(java.util.UUID u, int kind) {
  java.util.ArrayList l = list(u, kind);
  return l.isEmpty() ? null : (String) l.get(0);
}""")
M(sto, r"""
public static String nextId(java.util.UUID u, int kind) { return @PKG@.FpLogic.loadedId(kind, head(u, kind)); }""")
M(sto, r"""
public static void fill(java.util.UUID u, int kind, java.util.List l) {
  java.util.ArrayList q = list(u, kind);
  q.clear();
  q.addAll(l);
}""")
M(sto, r"""
public static String take(java.util.UUID u, int kind) {
  java.util.ArrayList l = list(u, kind);
  return l.isEmpty() ? null : (String) l.remove(0);
}""")
M(sto, r"""
public static void giveBack(java.util.UUID u, int kind, String src) { list(u, kind).add(0, src); }""")
M(sto, r"""
public static boolean busy(java.util.UUID u) {
  return RES.get(u) != null || SYNC.get(u) != null || REPORT.get(u) != null;
}""")

# ---- FpEng: engine helpers (world thread)
eng = mk("FpEng")
F(eng, "public static int MARK_I = -1;")
M(eng, r"""
public static int markIndex() {
  int i = MARK_I;
  if (i >= 0) return i;
  try { i = @EFX@.getAssetMap().getIndex("@MARK@"); } catch (Throwable t) { i = -1; }
  if (i >= 0) MARK_I = i;
  return i;
}""")
# the marker is there -> remove it (so two uses never merge) and answer true
M(eng, r"""
public static boolean takeMarker(@ST@ st, @REF@ r, @CAC@ acc) {
  int i = markIndex();
  if (i < 0) return false;
  @ECC@ e = (@ECC@) st.getComponent(r, @ECC@.getComponentType());
  if (e == null || !e.hasEffect(i)) return false;
  e.removeEffect(r, i, acc);
  return true;
}""")
M(eng, r"""
public static float health(@ST@ st, @REF@ r) {
  try {
    @ESM@ m = (@ESM@) st.getComponent(r, @ESM@.getComponentType());
    if (m == null) return -1.0f;
    @ESV@ v = m.get(@DST@.getHealth());
    return v == null ? -1.0f : v.get();
  } catch (Throwable t) { return -1.0f; }
}""")
M(eng, r"""
public static String effects(@ST@ st, @REF@ r) {
  try {
    @ECC@ e = (@ECC@) st.getComponent(r, @ECC@.getComponentType());
    if (e == null) return "?";
    int[] ix = e.getActiveEffectIndexes();
    if (ix == null || ix.length == 0) return "none";
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < ix.length; i++) {
      Object a = @EFX@.getAssetMap().getAsset(ix[i]);
      if (sb.length() > 0) sb.append(", ");
      sb.append(a instanceof @EFX@ ? ((@EFX@) a).getId() : ("#" + ix[i]));
    }
    return sb.toString();
  } catch (Throwable t) { return "? (" + t + ")"; }
}""")
M(eng, r"""
public static java.util.Map chains(@ST@ st, @REF@ r) {
  Object im = st.getComponent(r, @IMOD@.get().getInteractionManagerComponent());
  if (!(im instanceof @IMGR@)) return null;
  return (java.util.Map) ((@IMGR@) im).getChains();
}""")
M(eng, r"""
public static boolean alive(@ST@ st, @REF@ r, Object chain) {
  java.util.Map m = chains(st, r);
  if (m == null || chain == null) return false;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) if (it.next() == chain) return true;
  return false;
}""")
M(eng, r"""
public static boolean secondaryRunning(@ST@ st, @REF@ r) {
  java.util.Map m = chains(st, r);
  if (m == null) return false;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) {
    Object c = it.next();
    if (c instanceof @ICHN@ && ((@ICHN@) c).getType() == @ITYP@.Secondary) return true;
  }
  return false;
}""")
M(eng, r"""
public static @IC@ inv(@CAC@ acc, @REF@ r) {
  try { return @INVC@.getCombined(acc, r, @INVC@.HOTBAR_STORAGE_BACKPACK); } catch (Throwable t) { return null; }
}""")
M(eng, r"""
public static int findSlot(@IC@ inv, int kind) {
  if (inv == null) return -1;
  int cap = inv.getCapacity();
  for (int i = 0; i < cap; i++) {
    @IS@ s = inv.getItemStack((short) i);
    if (s != null && !s.isEmpty() && @PKG@.FpLogic.kindOf(s.getItemId()) == kind) return i;
  }
  return -1;
}""")
M(eng, r"""
public static String heldText(@ST@ st, @REF@ r) {
  try {
    @HOTB@ hb = (@HOTB@) st.getComponent(r, @HOTB@.getComponentType());
    @IS@ it = hb == null ? null : hb.getActiveItem();
    if (it == null || it.isEmpty()) return "nothing";
    return it.getItemId() + " x" + it.getQuantity();
  } catch (Throwable t) { return "?"; }
}""")
# write the next loaded id into the slot holding this kind's probe item; answers a log text
M(eng, r"""
public static String setId(@CAC@ acc, @REF@ r, int kind, String want) {
  @IC@ inv = inv(acc, r);
  int i = findSlot(inv, kind);
  if (i < 0) return "no " + @PKG@.FpLogic.kindName(kind) + " in your hotbar / storage / backpack";
  @IS@ old = inv.getItemStack((short) i);
  if (want.equals(old.getItemId())) return "slot " + i + " already holds " + want;
  @ISST@ tx = inv.replaceItemStackInSlot((short) i, old, new @IS@(want, 1));
  boolean ok = tx != null && tx.succeeded();
  return (ok ? "slot " + i + ": " : "FAILED slot " + i + ": ") + old.getItemId() + " -> " + want;
}""")
M(eng, r"""
public static String sync(@CAC@ acc, @REF@ r, java.util.UUID u, int kind) {
  return setId(acc, r, kind, @PKG@.FpStore.nextId(u, kind));
}""")
M(eng, r"""
public static int count(@CAC@ acc, @REF@ r) {
  @IC@ inv = inv(acc, r);
  if (inv == null) return 0;
  int n = 0;
  int cap = inv.getCapacity();
  for (int i = 0; i < cap; i++) {
    @IS@ s = inv.getItemStack((short) i);
    if (s != null && !s.isEmpty() && @PKG@.FpLogic.kindOf(s.getItemId()) >= 0) n = n + s.getQuantity();
  }
  return n;
}""")
M(eng, r"""
public static int probeIds() {
  try {
    java.util.Iterator it = @ITM@.getAssetMap().getAssetMap().keySet().iterator();
    int n = 0;
    while (it.hasNext()) { Object k = it.next(); if (k != null && String.valueOf(k).startsWith("@PRE@")) n++; }
    return n;
  } catch (Throwable t) { return -1; }
}""")

# ---- FpSyncTask: the held-item sync, run through World.execute (never inside a tick's iteration)
syn = mk("FpSyncTask", None, "java.lang.Runnable")
for f in ("public @WLD@ world;", "public @REF@ ref;", "public java.util.UUID uuid;", "public String name;"):
    F(syn, f)
C(syn, "public FpSyncTask(@WLD@ w, @REF@ r, java.util.UUID u, String n) { this.world = w; this.ref = r; this.uuid = u; this.name = n; }")
M(syn, r"""
public void run() {
  try {
    @ST@ st = this.world.getEntityStore().getStore();
    for (int k = 0; k < 2; k++) {
      String s = @PKG@.FpEng.sync((@CAC@) st, this.ref, this.uuid, k);
      if (s.indexOf("no Probe") < 0 && s.indexOf("already holds") < 0) @PKG@.FpLog.info(this.name + " SYNC " + @PKG@.FpLogic.kindName(k) + ": " + s);
    }
  } catch (Throwable t) { @PKG@.FpLog.warn("sync failed: " + t); }
}""")

cmds = mk("FpCmds")
F(cmds, "public static final String OK = \"@COLOK@\";")
F(cmds, "public static final String ERR = \"@COLERR@\";")
# ---- FpCore: the start hook + the tick logic
core = mk("FpCore")
M(core, r"""
public static void onStart(@ICSE@ e, @REF@ r, @ST@ st) {
  if (!"Secondary".equals(String.valueOf(e.getType()))) return;
  @IS@ held = e.getContext() == null ? null : e.getContext().getHeldItem();
  String id = held == null || held.isEmpty() ? null : held.getItemId();
  int kind = @PKG@.FpLogic.kindOf(id);
  if (kind < 0) return;
  @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  @PKG@.FpStore.STARTS = @PKG@.FpStore.STARTS + 1L;
  String src = @PKG@.FpLogic.srcOf(id);
  @ICHN@ ch = e.getChain();
  int cid = ch == null ? 0 : ch.getChainId();
  String head = @PKG@.FpStore.head(u, kind);
  String pre = pr.getUsername() + " START chain #" + cid + " root " + e.getRootInteractionId() + ", held " + id + ": ";
  if (@PKG@.FpStore.RES.get(u) != null) { @PKG@.FpLog.warn(pre + "a reservation is still open - this chain is NOT reserved"); return; }
  if (src != null && src.length() > 0 && src.equals(head)) {
    @PKG@.FpStore.take(u, kind);
    float hp = @PKG@.FpEng.health(st, r);
    @PKG@.FpStore.RES.put(u, new Object[] { Integer.valueOf(kind), src, ch, Long.valueOf(System.currentTimeMillis()), Float.valueOf(hp), Long.valueOf(0L), Integer.valueOf(cid) });
    @PKG@.FpLog.info(pre + "RESERVED 1 " + src + " (store left " + @PKG@.FpStore.list(u, kind).size() + ", health " + hp + ")");
    return;
  }
  if (@PKG@.FpStore.STRICT) {
    e.setCancelled(true);
    @PKG@.FpStore.CANCELS = @PKG@.FpStore.CANCELS + 1L;
    @PKG@.FpStore.SYNC.put(u, Boolean.TRUE);
    @PKG@.FpLog.tell(pr, "Probe: chain #" + cid + " CANCELLED at start - you held " + src + " but the store's next is " + (head == null ? "nothing" : head) + ". You should NOT have drunk / eaten anything.", @PKG@.FpCmds.ERR);
    return;
  }
  @PKG@.FpLog.info(pre + "not the store head (" + head + ") and strict is OFF - running UNRESERVED (the R2 fallback path)");
}""")
M(core, r"""
public static void tick(@REF@ r, @ST@ st, @CB@ cb, @PR@ pr) {
  java.util.UUID u = pr.getUuid();
  if (!@PKG@.FpStore.busy(u)) return;
  long now = System.currentTimeMillis();
  Object[] res = (Object[]) @PKG@.FpStore.RES.get(u);
  boolean mark = @PKG@.FpEng.takeMarker(st, r, (@CAC@) cb);
  if (mark) {
    if (res != null) {
      @PKG@.FpStore.RES.remove(u);
      @PKG@.FpStore.USES = @PKG@.FpStore.USES + 1L;
      int kind = ((Integer) res[0]).intValue();
      long ms = now - ((Long) res[3]).longValue();
      float hp = @PKG@.FpEng.health(st, r);
      @PKG@.FpStore.REPORT.put(u, new Object[] { Long.valueOf(now + 1000L), res[1], res[4], Float.valueOf(hp) });
      @PKG@.FpStore.SYNC.put(u, Boolean.TRUE);
      @PKG@.FpLog.tell(pr, "Probe: USED 1 " + res[1] + " (chain #" + res[6] + ") after " + ms + " ms. In your hand now: " + @PKG@.FpEng.heldText(st, r) + " (still there = not consumed). Store left: " + @PKG@.FpStore.list(u, kind).size() + ".", @PKG@.FpCmds.OK);
    } else {
      @PKG@.FpStore.FREE = @PKG@.FpStore.FREE + 1L;
      @PKG@.FpStore.SYNC.put(u, Boolean.TRUE);
      @PKG@.FpLog.tell(pr, "Probe: a use finished with NO reservation (a FREE use - the store paid nothing). In your hand: " + @PKG@.FpEng.heldText(st, r) + ".", @PKG@.FpCmds.ERR);
    }
  } else if (res != null) {
    long t0 = ((Long) res[3]).longValue();
    if (@PKG@.FpEng.alive(st, r, res[2]) && now - t0 < 30000L) {
      res[5] = Long.valueOf(0L);
    } else {
      long gone = ((Long) res[5]).longValue();
      if (gone == 0L) res[5] = Long.valueOf(now);
      else if (now - gone >= 250L) {
        @PKG@.FpStore.RES.remove(u);
        int kind = ((Integer) res[0]).intValue();
        @PKG@.FpStore.giveBack(u, kind, (String) res[1]);
        @PKG@.FpStore.RETURNS = @PKG@.FpStore.RETURNS + 1L;
        @PKG@.FpStore.SYNC.put(u, Boolean.TRUE);
        @PKG@.FpLog.tell(pr, "Probe: chain #" + res[6] + " ended after " + (gone - t0) + " ms WITHOUT finishing - 1 " + res[1] + " went back to the store (nothing used). Store: " + @PKG@.FpStore.list(u, kind).size() + ".", @PKG@.FpCmds.OK);
      }
    }
  }
  Object[] rep = (Object[]) @PKG@.FpStore.REPORT.get(u);
  if (rep != null && now >= ((Long) rep[0]).longValue()) {
    @PKG@.FpStore.REPORT.remove(u);
    @PKG@.FpLog.tell(pr, "Probe: 1 s after using " + rep[1] + ": health at start " + rep[2] + ", at the end " + rep[3] + ", now " + @PKG@.FpEng.health(st, r) + ". Active effects: " + @PKG@.FpEng.effects(st, r) + ".", null);
  }
  if (@PKG@.FpStore.SYNC.get(u) != null && @PKG@.FpStore.RES.get(u) == null && !@PKG@.FpEng.secondaryRunning(st, r)) {
    @PKG@.FpStore.SYNC.remove(u);
    Object ex = st.getExternalData();
    @WLD@ w = ex instanceof @EST@ ? ((@EST@) ex).getWorld() : null;
    if (w != null) w.execute(new @PKG@.FpSyncTask(w, r, u, pr.getUsername()));
  }
}""")

# ---- FpCmds (made before FpCore: FpCore uses its colours)
M(cmds, r"""
public static void help(@PR@ pr) {
  @PKG@.FpLog.tell(pr, "Flask / Pouch probe (op only): /flaskprobe flask | pouch - fill the probe store with 10 test items and get the probe item", null);
  @PKG@.FpLog.tell(pr, "/flaskprobe wrong - make your probe item show an item that is NOT next in the store; /flaskprobe strict - cancel such clicks ON / OFF", null);
  @PKG@.FpLog.tell(pr, "/flaskprobe empty - empty both stores; /flaskprobe clear - remove every probe item from your inventory (do this before the probe is removed)", null);
}""")
M(cmds, r"""
public static void status(@PR@ pr, @ST@ st, @REF@ ref) {
  java.util.UUID u = pr.getUuid();
  @PKG@.FpLog.tell(pr, "Flask store: " + @PKG@.FpLogic.summary(@PKG@.FpStore.list(u, 0)) + ". Pouch store: " + @PKG@.FpLogic.summary(@PKG@.FpStore.list(u, 1)) + ".", null);
  Object[] res = (Object[]) @PKG@.FpStore.RES.get(u);
  @PKG@.FpLog.tell(pr, "In your hand: " + @PKG@.FpEng.heldText(st, ref) + ". Open reservation: " + (res == null ? "none" : res[1] + " (chain #" + res[6] + ")") + ". Strict: " + (@PKG@.FpStore.STRICT ? "ON" : "OFF") + ".", null);
  @PKG@.FpLog.tell(pr, "Counters (everyone): starts " + @PKG@.FpStore.STARTS + ", used " + @PKG@.FpStore.USES + ", returned " + @PKG@.FpStore.RETURNS + ", cancelled " + @PKG@.FpStore.CANCELS + ", free uses " + @PKG@.FpStore.FREE + ". Probe item ids loaded: " + @PKG@.FpEng.probeIds() + " of " + (@PKG@.FpLogic.NLOADED + 2) + ". Health " + @PKG@.FpEng.health(st, ref) + ".", null);
}""")
M(cmds, r"""
public static void give(@PR@ pr, @ST@ st, @REF@ ref, int kind) {
  java.util.UUID u = pr.getUuid();
  if (@PKG@.FpStore.RES.get(u) != null) { @PKG@.FpLog.tell(pr, "Wait - a use is still running.", ERR); return; }
  @PKG@.FpStore.fill(u, kind, @PKG@.FpLogic.testFill(kind, 10));
  String want = @PKG@.FpStore.nextId(u, kind);
  @IC@ inv = @PKG@.FpEng.inv((@CAC@) st, ref);
  if (@PKG@.FpEng.findSlot(inv, kind) >= 0) {
    @PKG@.FpLog.tell(pr, "Store filled: " + @PKG@.FpLogic.summary(@PKG@.FpStore.list(u, kind)) + ". Your " + @PKG@.FpLogic.kindName(kind) + ": " + @PKG@.FpEng.setId((@CAC@) st, ref, kind, want) + ".", OK);
    return;
  }
  @IC@ dst = null;
  try { dst = @INVC@.getCombined((@CAC@) st, ref, @INVC@.STORAGE_HOTBAR_BACKPACK); } catch (Throwable t) { dst = null; }
  boolean ok = false;
  try {
    @IST@ tx = dst == null ? null : dst.addItemStack(new @IS@(want, 1));
    @IS@ rem = tx == null ? null : tx.getRemainder();
    ok = tx != null && tx.succeeded() && (rem == null || rem.isEmpty());
  } catch (Throwable t) { @PKG@.FpLog.warn("give " + want + " failed: " + t); }
  if (!ok) { @PKG@.FpLog.tell(pr, "No room for the " + @PKG@.FpLogic.kindName(kind) + " - nothing was dropped. Free a slot and try again.", ERR); return; }
  @PKG@.FpLog.tell(pr, "You got the " + @PKG@.FpLogic.kindName(kind) + " (in your storage - drag it to the hotbar). Store: " + @PKG@.FpLogic.summary(@PKG@.FpStore.list(u, kind)) + ". Right click it (Adventure mode) and watch the chat.", OK);
}""")
M(cmds, r"""
public static void wrong(@PR@ pr, @ST@ st, @REF@ ref) {
  java.util.UUID u = pr.getUuid();
  @IC@ inv = @PKG@.FpEng.inv((@CAC@) st, ref);
  for (int k = 0; k < 2; k++) {
    if (@PKG@.FpEng.findSlot(inv, k) < 0) continue;
    String w = @PKG@.FpLogic.wrongSrc(k, @PKG@.FpStore.head(u, k));
    @PKG@.FpLog.tell(pr, "Your " + @PKG@.FpLogic.kindName(k) + " now shows " + w + " (not in the store): " + @PKG@.FpEng.setId((@CAC@) st, ref, k, @PKG@.FpLogic.loadedId(k, w)) + ". Strict is " + (@PKG@.FpStore.STRICT ? "ON: a right click must be cancelled (no drink / eat)." : "OFF: a right click runs and is logged as a FREE use."), OK);
  }
}""")
M(cmds, r"""
public static void clear(@PR@ pr, @ST@ st, @REF@ ref, boolean items) {
  java.util.UUID u = pr.getUuid();
  @PKG@.FpStore.fill(u, 0, new java.util.ArrayList());
  @PKG@.FpStore.fill(u, 1, new java.util.ArrayList());
  if (!items) {
    for (int k = 0; k < 2; k++) @PKG@.FpLog.tell(pr, @PKG@.FpLogic.kindName(k) + " store emptied: " + @PKG@.FpEng.sync((@CAC@) st, ref, u, k) + ".", OK);
    return;
  }
  @PKG@.FpStore.RES.remove(u);
  @PKG@.FpStore.SYNC.remove(u);
  @IC@ inv = @PKG@.FpEng.inv((@CAC@) st, ref);
  int n = 0;
  if (inv != null) {
    int cap = inv.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ s = inv.getItemStack((short) i);
      if (s != null && !s.isEmpty() && @PKG@.FpLogic.kindOf(s.getItemId()) >= 0) { inv.removeItemStackFromSlot((short) i); n++; }
    }
  }
  @PKG@.FpLog.tell(pr, "Removed " + n + " probe item(s); " + @PKG@.FpEng.count((@CAC@) st, ref) + " left. Stores emptied.", OK);
}""")
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, String what) {
  String t = what == null ? "" : what.trim().toLowerCase(java.util.Locale.ROOT);
  @PKG@.FpLog.info(pr.getUsername() + " ran /flaskprobe " + t);
  if (t.equals("flask")) { give(pr, st, ref, 0); return; }
  if (t.equals("pouch")) { give(pr, st, ref, 1); return; }
  if (t.equals("wrong")) { wrong(pr, st, ref); return; }
  if (t.equals("strict")) { @PKG@.FpStore.STRICT = !@PKG@.FpStore.STRICT; @PKG@.FpLog.tell(pr, "Strict is now " + (@PKG@.FpStore.STRICT ? "ON (a click on an item that is not next in the store is cancelled)." : "OFF (such a click runs unreserved and is counted as a free use)."), OK); return; }
  if (t.equals("empty")) { clear(pr, st, ref, false); return; }
  if (t.equals("clear")) { clear(pr, st, ref, true); return; }
  @PKG@.FpLog.tell(pr, "Unknown option '" + (what == null ? "" : what.trim()) + "'.", ERR);
  help(pr);
}""")

# ---- the two systems (ONE registerSystem per class)
ssys = mk("FpStartSys", T["EES"])
F(ssys, "public static boolean FAILED_ONCE = false;")
C(ssys, "public FpStartSys() { super(@ICSE@.class); }")
M(ssys, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(ssys, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || !(ev instanceof @ICSE@)) return;
    @PKG@.FpCore.onStart((@ICSE@) ev, chunk.getReferenceTo(idx), st);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.FpLog.warn("the chain start hook failed (logged once): " + t); }
  }
}""")
tick = mk("FpTick", T["ETS"])
F(tick, "public static boolean FAILED_ONCE = false;")
C(tick, "public FpTick() { super(); }")
M(tick, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(tick, "public boolean isParallel(int a, int b) { return false; }")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (chunk == null) return;
    if (@PKG@.FpStore.RES.isEmpty() && @PKG@.FpStore.SYNC.isEmpty() && @PKG@.FpStore.REPORT.isEmpty()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) store.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.FpCore.tick(r, store, cb, pr);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.FpLog.warn("the probe tick failed (logged once): " + t); }
  }
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
cmd1 = mk("FlaskProbeArgCmd", T["APC"])
F(cmd1, "public @RA@ whatArg;")
C(cmd1, r"""
public FlaskProbeArgCmd() {
  super("(admin) /flaskprobe <flask, pouch, wrong, strict, empty, clear>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("option", "flask, pouch, wrong, strict, empty or clear", @ATY@.STRING);
}""")
M(cmd1, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); }
  catch (Throwable t) { @PKG@.FpLog.tell(pr, "Usage: /flaskprobe <flask, pouch, wrong, strict, empty, clear>", @PKG@.FpCmds.ERR); return; }
  @PKG@.FpCmds.run(ref, store, pr, a);
}""")
cmd = mk("FlaskProbeCmd", T["APC"])
C(cmd, r"""
public FlaskProbeCmd() {
  super("flaskprobe", "(admin) Potion Flask / Food Pouch engine probe (throwaway dev pack): /flaskprobe shows the probe state and the options");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "fprobe" });
  addUsageVariant(new @PKG@.FlaskProbeArgCmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.FpLog.info(pr.getUsername() + " ran /flaskprobe");
  @PKG@.FpCmds.status(pr, store, ref);
  @PKG@.FpCmds.help(pr);
}""")

pl = mk("SkyyFlaskProbePlugin", T["JP"])
C(pl, "public SkyyFlaskProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.FpLog.LOG = getLogger();
  try {
    getCommandRegistry().registerCommand(new @PKG@.FlaskProbeCmd());
    getEntityStoreRegistry().registerSystem(new @PKG@.FpStartSys());
    getEntityStoreRegistry().registerSystem(new @PKG@.FpTick());
  } catch (Throwable t) { @PKG@.FpLog.warn("setup failed: " + t); }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyFlaskProbe] @VERSION@ ready - /flaskprobe (admin): " + (@PKG@.FpLogic.NLOADED + 2) + " probe item ids (" + @PKG@.FpLogic.FLASK_SRC.length + " flask + " + @PKG@.FpLogic.POUCH_SRC.length + " pouch + 2 empty), " + @PKG@.FpEng.probeIds() + " in the item map now, marker effect index " + @PKG@.FpEng.markIndex() + " (throwaway dev pack, remove after the test session)");
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.FpStore.Q.clear();
  @PKG@.FpStore.RES.clear();
  @PKG@.FpStore.SYNC.clear();
  @PKG@.FpStore.REPORT.clear();
  super.shutdown();
}""")

ALL = [log, lg, sto, eng, syn, core, cmds, ssys, tick, cmd1, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "%s-%s.jar" % (MOD, VERSION))
man = B.manifest(MOD, VERSION, "SkyWynn THROWAWAY dev pack (round FP0): Potion Flask / Food Pouch engine probe - a held item runs a copy of a potion's / food's consume chain without being used up (/flaskprobe, admin only). Built against SkyyCooking %s. Remove after the test session." % COOK_VER,
                 PKG + ".SkyyFlaskProbePlugin", stable=True)
B.assemble(jar, man, OUT, files)
