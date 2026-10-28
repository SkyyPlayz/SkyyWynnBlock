"""Derive SkyyMobs/build_skyymobs_0.1.22.py from the GENERATED 0.1.21 (build_skyymobs_0.1.21.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_21_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.21
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_22_patch.py   then   python SkyyMobs/build_skyymobs_0.1.22.py   then   python SkyyMobs/test_skyymobs_0.1.22.py
Edit THIS file, never the generated script (never --deploy).

0.1.22 (2026-10-28) = TOUGHER VERSIONS, the Wynncraft way (round variety1 = research/Mob-Variety-Spec.md Proposal B, on top of spawn1 0.1.21).
  Skyy 2026-10-27: "it would be great fi we could also get more mob variety especially for normal regular monsters to fight everywhere. wynn
  craft does this by giving more difficult versions armor an stuff." + popups (docs/answered/mobs.md): "Visible armour (Recommended)",
  "Normal/Armored/Veteran (Recommended)", "XP by Health + drops (Recommended)".
  1. NEW ROLES + MODELS (build time, Assets.zip -> the jar; never committed - PROJECT-RULES 2). For every common monster role our spawn
     files (0.1.21) put into a Zone 1-4 world list - skeletons of every zone family, zombies, outlanders (player rig) and goblin scrappers /
     thieves / miners (goblin rig) - two NEW role ids per zone it spawns in: <Role>_SkyyArmored<zone> and <Role>_SkyyVeteran<zone>, each
     a FULL COPY of the vanilla role (fix after smoke 20261028-065456: a Variant may only Modify the parameters its Reference declares
     itself - Skeleton_Fighter etc. do not declare Appearance, so "Variant of Skeleton_Fighter, Modify Appearance" failed for all 88; the
     copy keeps the vanilla template Reference + vanilla Parameters / Modify, *_Wander roles flattened onto their camp role - var_role) -
     its AI, attacks, weapons, drop list, flock, memory and name key stay vanilla's - with only Appearance = a NEW model = the vanilla model + armour attachments (worn look only, never items):
     player-rig bodies wear the zone's vanilla metal (Z1 Copper / Iron, Z2 Thorium / Steel, Z3 Cobalt / Adamantite, Z4 Mithril; vanilla
     proof: Showcase_Skeleton_Tank / Skeleton_Burnt_Soldier / Temple_Mithril_Guard wear Items/Armors pieces); goblins wear the vanilla
     Goblin_Guardian pieces (bucket helmet, barrel armour, chain gloves / boots - the player sets are sized for the player rig, the goblin
     rig is smaller). Armored = head + chest, Veteran = the full set (head, chest, hands, legs). The vanilla attachments in a filled slot
     (old helmets, tunics, boots, hair) are taken off so nothing clips. Left out on purpose: Trorks (no world spawns, camps only), the
     Burnt Praetorian / elite skeletons (already the heavy ones), the Burnt Gunner ("No guns"), the Incandescent Head (no body), Outlander
     Brute (own rig), and every role an ENABLED pack mod overrides (DungeonBosses' Frost skeletons: their flock / stats stay the pack's).
  2. THE MIX (spawn files, weights split, the total unchanged = 0.1.21's spawn rates and animal shares untouched): Normal : Armored :
     Veteran = 70 : 25 : 5 in Tier 1 lists (easy biomes), 55 : 35 : 10 Tier 2, 40 : 40 : 20 Tier 3 (hardest); non-Wander files by table
     (Zone 1 cave goblins Tier 1, Zone 3 outlanders + Zone 4 wastes Tier 2, Zone 4 volcanoes Tier 3). Build asserts: every new id unique
     against Assets.zip, every SET jar and every mod in Skyy's Mods folder; no NPC + environment pair in two files.
  3. RANKS (SkyyMobs, not an armour stat - the role Armor list stays empty): Armored x1.4 Health / x1.15 damage / +1 level, Veteran x1.9 /
     x1.3 / +2 (the level on top of the band roll; a saved level is kept); the 3 % elite roll still goes on top. MobCfg.factors multiplies
     the variant in, so the live re-apply, the hits and mob:fn:info hpMult / dmgMult follow it. The element is the base role's
     (MobElem.row reads the base id). The nameplate: "[Lv 12] Armored Skeleton Soldier", "Elite Veteran ..." (rank word in front).
     Rarity colours (white / yellow / pink, elites cyan): under the plate.colorOn trial (still OFF: the client's plate colour support is
     UNVERIFIED, P6) the plate takes them - a plain mob white (replaces the trial's old level-colour ladder); without it the WORD carries
     the step and /mobs inspect names the colour. Admin role rows (Never level these, rank lists, role table) naming the vanilla role also
     cover its Armored / Veteran ids (MobGlob.any / MobCfg.roleIdx try the base id).
  4. REWARDS: kill XP follows Health with no new XP code (mob:fn:info xpMult = health share x min(Health x of rank + variant, 10)); drops:
     one more roll of the mob's own drop list at 25 % (Armored) / 50 % (Veteran) - gear / armour / weapons filtered out (MobSpoils.clean),
     so the worn armour never drops (it is a model attachment, never an item). The rank string (7th entry of mob:fn:info) is unchanged:
     Armored / Veteran count as normal kills for SkyyGear (no SkyyGear change).
  5. SERVER SETUP > Mobs > Tougher mobs (13 rows, live): variant.on (OFF = every Armored / Veteran mob is removed as it spawns or loads),
     Health x / damage x / extra levels / extra drop chance per step, variant.share.z1..z4 (% of the built-in mix kept: weights are
     build-time - 0.1.21 A3 - so a lower share removes the extra ones as they spawn; the spawner refills with a fresh pick). The mix
     itself is NOT editable live (A3: the engine copies each spawn weight once, no setter): a share only thins it, never raises the
     Veteran part - a different mix is a rebuild (VAR_MIX). A spawn SkyyZones' town / safe-region hook removes (zones:fn:noSpawn) is left
     to that hook (its plain removeEntity fails on a ref already removed).
  6. /mobs strip variants (admin: requirePermission skyymobs.admin + setPermissionGroups(new String[0])): removes every Armored / Veteran
     mob loaded (and levelled) in your world. /mobs inspect shows the step, its numbers and its colour.
  SAVED DATA: the new role ids are saved in chunks with the mobs. No config migration (new keys; a missing line = the default).
  Classes MobVariant, MobVariantSys (RefSystem: ONE registerSystem), MobsStripCmd (cmd()); no new bridge key.
  ROLLBACK FLOOR: before going back below 0.1.22 - Server Setup > Mobs > Tougher mobs OFF, then /mobs strip variants in each world (or wait
  a game day); a jar without the roles logs "Reloading nonexistent role" WARNs for mobs still saved (harmless, they vanish).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.21.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.22.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.21"') and P.s.startswith('"""SkyyMobs 0.1.21 - build script') and P.has("MobSpawn") and not P.has("MobVariant"), "not the SET pin 0.1.21"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")
HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.22 (2026-10-28)"):].rstrip() + "\n\n"

P.rep('''"""SkyyMobs 0.1.21 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_21_patch.py from the SET pin 0.1.20 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.21.py -> SkyyMobs/SkyyMobs-0.1.21.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.21.py
''', '''"""SkyyMobs 0.1.22 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_22_patch.py from the SET pin 0.1.21 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.22.py -> SkyyMobs/SkyyMobs-0.1.22.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.22.py
''' + NOTE)
P.rep('VERSION = "0.1.21"', 'VERSION = "0.1.22"')

# ---------- 0. fix: 0.1.21's pack check read our OWN deployed jar (Mods/SkyyMobs.jar, enabled) as a pack mod shipping our spawn files - skip it
P.rep('''        _sp = [_n for _n in _names if SPAWN_DIR in _n and _n.endswith(".json")]
        if not _sp:
            continue
''', '''        _sp = [_n for _n in _names if SPAWN_DIR in _n and _n.endswith(".json")]
        if not _sp or "com/skyy/mobs/SkyyMobsPlugin.class" in _names:          # 0.1.22 fix: our own deployed jar is no pack mod
            continue
''')

# ---------- 1. the variant roles + models + the weight split (Python, from Assets.zip) + LEVELLED
P.rep('''for _l in SPAWN_PACK:
    print("   pack: " + _l)
''', r'''for _l in SPAWN_PACK:
    print("   pack: " + _l)
# ================================================================= 0.1.22 (variety1): tougher versions (tools/mobs_0_1_22_patch.py docstring)
VAR_SUF = ("_SkyyArmored", "_SkyyVeteran")          # id = <vanilla role><suffix><zone digit>; MobCfg.variantOf / baseRole / variantZone mirror it
VAR_MIX = {1: (70, 25, 5), 2: (55, 35, 10), 3: (40, 40, 20)}          # Skyy 2026-10-27 "Normal/Armored/Veteran": easy -> hardest
VAR_FILE_TIER = {"Zone1/Spawns_Zone1_Caves_Goblins": 1, "Zone3/Spawns_Zone3_Outlander": 2, "Zone4/Spawns_Zone4_Wastes_Predator": 2,
                 "Zone4/Spawns_Zone4_Volcanoes_Predator": 3}          # the non-Wander files (no TierN in the name)
VAR_METAL = {1: ("Copper", "Iron"), 2: ("Thorium", "Steel"), 3: ("Cobalt", "Adamantite"), 4: ("Mithril", "Mithril")}   # spec B2 (tier_tags LADDER)
VAR_PARTS = (("Head", "Chest"), ("Head", "Chest", "Hands", "Legs"))          # Armored, Veteran
VAR_STEPS = (("armored", "Armored", 1.4, 1.15, 1, 25.0), ("veteran", "Veteran", 1.9, 1.3, 2, 50.0))   # word, Health x, damage x, +levels, drop %
VAR_SKIP_PARTS = ("Gunner", "Praetorian", "Incandescent_Head", "Elite", "Pirate", "Brute", "Turret", "Lab_", "Spectator")
VAR_GOBLINS = ("Goblin_Scrapper", "Goblin_Thief", "Goblin_Miner")
VAR_ZOMBIES = ("Zombie", "Zombie_Sand", "Zombie_Frost", "Zombie_Burnt")
SLOT_WORDS = {"Head": ("head", "helmet", "hat", "hood", "cap.", "_cap", "hair", "mask", "crown"),
              "Chest": ("chest", "tunic", "shirt", "torso", "robe", "armor_", "vest", "coat"),
              "Hands": ("hands", "hand.", "glove", "bracer", "gauntlet"),
              "Legs": ("legs", "leg.", "pants", "shorts", "skirt", "boots", "shoes", "feet", "socks", "calf")}
KEEP_WORDS = ("eyes", "eye.", "eyebrow", "mouth", "ears", "ear.", "face", "beard", "tusk", "fang", "teeth", "jaw")


def var_family(role):
    """'player' (the zone's vanilla metal), 'goblin' (Goblin_Guardian pieces) or None (no tougher versions)"""
    if any(_x in role for _x in VAR_SKIP_PARTS) or role not in ROLES or not levelled(role) or ATT.get(role) != "HOSTILE":
        return None
    if role.startswith("Skeleton_") or role.startswith("Outlander_"):
        return "player"
    if role in VAR_ZOMBIES or any(role.startswith(_z + "_Wander") for _z in VAR_ZOMBIES):
        return "player"
    if role.startswith(VAR_GOBLINS):
        return "goblin"
    return None


def var_id(base, step, zone):
    return "%s%s%d" % (base, VAR_SUF[step], zone)


def var_split(vid):
    """the Python mirror of MobCfg.variantOf / baseRole / variantZone: (step 0 / 1 / 2, base, zone)"""
    for _s, _suf in enumerate(VAR_SUF):
        _i = vid.find(_suf)
        if _i > 0:
            _z = vid[-1]
            return _s + 1, vid[:_i], int(_z) if _z.isdigit() else 0
    return 0, vid, 0


_MODJ = {}
for _n in AZ_NAMES:
    if _n.startswith("Server/Models/") and _n.endswith(".json"):
        try:
            _MODJ[_n.rsplit("/", 1)[1][:-5]] = lenient(AZ.read(_n).decode("utf-8-sig"))
        except Exception:
            pass


def model_key(m, key, depth=0):
    """the effective value of a model field: its own, else the nearest Parent's (None = none)"""
    d = _MODJ.get(m)
    if d is None or depth > 10:
        return None
    if key in d:
        return d[key]
    return model_key(d.get("Parent"), key, depth + 1) if d.get("Parent") else None


def appearance(role):
    p, _root = role_params(role)
    a = p.get("Appearance")
    if isinstance(a, dict) and "Compute" in a:
        a = p.get(a["Compute"])
    return a if isinstance(a, str) else None


def slot_of(path, slots):
    """the filled slot a vanilla attachment sits in (None = keep it): its last folder + file name against the slot words"""
    low = "/".join((path or "").lower().split("/")[-2:])
    if any(_k in low for _k in KEEP_WORDS):
        return None
    for _s in slots:
        if any(_w in low for _w in SLOT_WORDS[_s]):
            return _s
    return None


def piece_texture(folder, part):
    for _t in ("%s_Texture.png", "%s_default.png"):
        _p = "Items/Armors/%s/%s" % (folder, _t % part)
        if "Common/" + _p in _AZSET:
            return _p
    raise SystemExit("0.1.22: no texture for Items/Armors/%s/%s" % (folder, part))


_AZSET = set(AZ_NAMES)
_GOB = dict((slot_of(_a["Model"], ("Head", "Chest", "Hands", "Legs")), _a) for _a in _MODJ["Goblin_Guardian"]["DefaultAttachments"])
assert sorted(_k for _k in _GOB if _k) == ["Chest", "Hands", "Head", "Legs"], "0.1.22: the Goblin_Guardian pieces moved: %s" % sorted(_GOB, key=str)


def pieces(family, step, zone):
    out = []
    for _part in VAR_PARTS[step]:
        if family == "goblin":
            out.append(dict(_GOB[_part]))
        else:
            _m = VAR_METAL[zone][step]
            _mp = "Items/Armors/%s/%s.blockymodel" % (_m, _part)
            assert "Common/" + _mp in _AZSET, "0.1.22: %s missing" % _mp
            out.append({"Model": _mp, "Texture": piece_texture(_m, _part)})
    return out


def var_model(app, family, step, zone):
    d = json.loads(json.dumps(_MODJ[app]))
    slots = VAR_PARTS[step]
    atts = model_key(app, "DefaultAttachments") or []
    keep = [_a for _a in atts if not slot_of(_a.get("Model"), slots)]
    d["DefaultAttachments"] = keep + pieces(family, step, zone)
    rs = model_key(app, "RandomAttachmentSets")
    if isinstance(rs, dict):
        d["RandomAttachmentSets"] = dict((_k, _v) for _k, _v in rs.items()
                                         if not slot_of(_k + ".x", slots) and not any(isinstance(_o, dict) and slot_of(_o.get("Model"), slots)
                                                                                     for _o in (_v or {}).values()))
    for _a in d["DefaultAttachments"]:
        for _f in ("Model", "Texture"):
            assert not _a.get(_f) or "Common/" + _a[_f] in _AZSET, "0.1.22: %s names %s (not in Assets.zip)" % (app, _a.get(_f))
    return d, len(atts) - len(keep)


# the ids that already exist anywhere (vanilla, every SET jar, every mod in Skyy's Mods folder): our ids must be new; the roles an ENABLED
# pack mod overrides get no tougher versions (their flock / stats stay the pack's)
_TAKEN = set(ROLES) | set(_MODJ)
for _m, _v in _dsm.SET:
    _j = os.path.join(ROOT, _m, "%s-%s.jar" % (_m, _v))
    if _m != MOD and os.path.isfile(_j):
        for _n in zipfile.ZipFile(_j).namelist():
            if (_n.startswith("Server/NPC/Roles/") or _n.startswith("Server/Models/")) and _n.endswith(".json"):
                _TAKEN.add(_n.rsplit("/", 1)[1][:-5])
VAR_PACK_OVR = set()
VAR_PACK = "Mods folder / test world config not found - pack check skipped"
if os.path.isdir(B.MODS_DIR) and os.path.isfile(_MW):
    _onv = dict((_kk, bool((_vv or {}).get("Enabled"))) for _kk, _vv in (json.load(open(_MW, encoding="utf-8")).get("Mods") or {}).items())
    _nmods = 0
    for _f in sorted(os.listdir(B.MODS_DIR)):
        try:
            _z = zipfile.ZipFile(os.path.join(B.MODS_DIR, _f))
            _names = _z.namelist()
        except Exception:
            continue
        if "com/skyy/mobs/SkyyMobsPlugin.class" in _names:          # our own deployed jar (an older SkyyMobs) is no pack mod
            continue
        _ids = set(_n.rsplit("/", 1)[1][:-5] for _n in _names if ("Server/NPC/Roles/" in _n or "Server/Models/" in _n) and _n.endswith(".json"))
        _TAKEN |= _ids
        _mf = sorted([_n for _n in _names if _n.lower().endswith("manifest.json")], key=len)
        try:
            _man = lenient(_z.read(_mf[0]).decode("utf-8-sig"))
            _key = "%s:%s" % (_man.get("Group"), _man.get("Name"))
        except Exception:
            _key = "?" + _f
        if _onv.get(_key):
            VAR_PACK_OVR |= _ids
            _nmods += 1
    VAR_PACK = "%d enabled pack mods checked; %d of their role / model ids are vanilla ones they override" % (_nmods, len(VAR_PACK_OVR & (set(ROLES) | set(_MODJ))))


def chain_of(role):
    out, x = [], role
    while x in ROLES and x not in out and len(out) < 12:
        out.append(x)
        x = ROLES[x].get("Reference") if ROLES[x].get("Type") == "Variant" else None
    return out


def own_params(role):
    """the Parameters a Variant of this role may Modify = its OWN declared, non-private Parameters block (engine BuilderModifier.applyTo:
    BuilderParameters.getParameterType of the referenced role, VOID = "Parameter X does not exist or is private"; inherited template
    parameters do NOT count - checked against all 545 vanilla Variants in Assets.zip 2026-10-28: 0 exceptions)"""
    return dict((_k, _v) for _k, _v in ((ROLES.get(role) or {}).get("Parameters") or {}).items() if not (isinstance(_v, dict) and _v.get("Private")))


def modify_ok(role_json):
    """the engine's Modify rule for one role JSON (the step the 0.1.22 smoke test hit): every non-underscore Modify key is a public
    parameter of the Reference; every {"Compute": name} names one of the role's own Parameters; returns the bad keys"""
    if role_json.get("Type") != "Variant":
        return ["not a Variant"]
    pub = own_params(role_json.get("Reference"))
    own = role_json.get("Parameters") or {}
    bad = [_k for _k in (role_json.get("Modify") or {}) if not _k.startswith("_") and _k not in pub]
    bad += ["Compute " + _v["Compute"] for _v in (role_json.get("Modify") or {}).values()
            if isinstance(_v, dict) and set(_v) == {"Compute"} and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(_v["Compute"]))
            and _v["Compute"] not in own]          # an expression (Test_Template_Variant "[ 0+1, 2*5 ]") is not a parameter name
    return bad


def var_role(base, model):
    """fix (smoke 20261028-065456: all 88 roles "Parameter Appearance does not exist or is private"): a vanilla role only lets a Variant
    Modify the parameters it declares itself (Bear_Grizzly declares Appearance, so Bear_Polar may change it; Skeleton_Fighter does not).
    So a tougher version is a FULL COPY of the vanilla role (its Reference = the same vanilla template, its own Parameters + Modify =
    vanilla's, so AI, attacks, weapons, drop list, flock and name key stay vanilla's) with only Modify.Appearance = our model, and the
    memory kept on the vanilla entry (MemoriesNameOverride = the vanilla memory name). A *_Wander role (a Variant of its camp role that only
    sets that role's parameters) is flattened: the camp role's copy with the Wander's values in the camp role's Parameters."""
    d = json.loads(json.dumps(ROLES[base]))
    if d.get("Type") == "Variant" and "Appearance" not in (d.get("Modify") or {}):          # a *_Wander: flatten onto its camp role
        camp = json.loads(json.dumps(ROLES[d["Reference"]]))
        cp = camp.get("Parameters") or {}
        for _k, _v in (d.get("Modify") or {}).items():
            if isinstance(_v, dict) and set(_v) == {"Compute"}:
                _v = ((d.get("Parameters") or {}).get(_v["Compute"]) or {}).get("Value")
            if _k.startswith("_") or _k not in cp or _v is None or isinstance(_v, dict):
                raise SystemExit("0.1.22: cannot flatten %s onto %s (key %s)" % (base, d["Reference"], _k))
            cp[_k] = dict(cp[_k], Value=_v)
        assert appearance(d["Reference"]) == appearance(base), "0.1.22: %s and its camp role differ in model" % base
        d = camp
    m = d.get("Modify") or {}
    if d.get("Type") != "Variant" or not isinstance(m.get("Appearance"), str) or "Appearance" not in own_params(d.get("Reference")):
        raise SystemExit("0.1.22: %s does not set a literal Appearance on a template that exposes it" % base)
    if modify_ok(d):
        raise SystemExit("0.1.22: the vanilla copy of %s breaks the Modify rule: %s" % (base, modify_ok(d)))
    m["Appearance"] = model
    if m.get("IsMemory") and "MemoriesNameOverride" not in m and "MemoriesNameOverride" in own_params(d.get("Reference")):
        m["MemoriesNameOverride"] = base.replace("_Wander", "")          # the kill counts on the vanilla memory, never a new entry
    bad = modify_ok(d)
    assert not bad and d["Reference"] in ROLES and ROLES[d["Reference"]].get("Type") == "Abstract", "0.1.22: %s copy: %s" % (base, bad)
    return d


# the rule mirror must accept every vanilla Variant (else it is wrong, not the role) and refuse the failed 0.1.22 form
assert not [_r for _r, _d in ROLES.items() if _d.get("Type") == "Variant" and _d.get("Reference") in ROLES and modify_ok(_d)], "0.1.22: Modify rule mirror"
assert modify_ok({"Type": "Variant", "Reference": "Skeleton_Fighter", "Modify": {"Appearance": "X"}}) == ["Appearance"], "0.1.22: Modify rule mirror (old form)"
VAR_FILES = {}          # jar path -> text: the variant roles + models (generated here, never committed)
VAR_IDS = {}            # variant id -> (base, step 1 / 2, zone, family)
VAR_SKIPPED = {}        # base -> why no tougher versions (report)
_vsplit = 0
for _k in sorted(SPAWN_NEW):
    _zf = _k.split("/")[0]
    if not _zf.startswith("Zone"):
        continue
    _zone = int(_zf[4:])
    _d = SPAWN_NEW[_k]
    _mt = re.search(r"_Tier([123])$", _k)
    _tier = int(_mt.group(1)) if _mt else VAR_FILE_TIER.get(_k)
    _out = []
    for _e in _d["NPCs"]:
        _b = _e["Id"]
        _fam = var_family(_b)
        _app = appearance(_b) if _fam else None
        _why = None
        if not _fam:
            _why = "not a tougher-version family"
        elif not _app or _app not in _MODJ:
            _why = "no model (%s)" % _app
        elif set(chain_of(_b)) & VAR_PACK_OVR or _app in VAR_PACK_OVR:
            _why = "an enabled pack mod overrides %s" % sorted(set(chain_of(_b) + [_app]) & VAR_PACK_OVR)
        elif not _tier:
            _why = "file %s has no tier" % _k
        if _why:
            VAR_SKIPPED.setdefault(_b, _why)
            _out.append(_e)
            continue
        _w = float(_e["Weight"])
        _mix = VAR_MIX[_tier]
        _out.append(dict(_e, Weight=round(_w * _mix[0] / 100.0, 4)))
        for _s in (0, 1):
            _vid = var_id(_b, _s, _zone)
            _out.append(dict(_e, Id=_vid, Weight=round(_w * _mix[_s + 1] / 100.0, 4)))
            if _vid not in VAR_IDS:
                assert _vid not in _TAKEN and re.fullmatch(r"[A-Za-z0-9_]+", _vid) and var_split(_vid) == (_s + 1, _b, _zone), "0.1.22: id %s" % _vid
                _md, _off = var_model(_app, _fam, _s, _zone)
                VAR_FILES["Server/Models/SkyyMobs/%s.json" % _vid] = spawn_json(_md)
                VAR_FILES["Server/NPC/Roles/SkyyMobs/%s.json" % _vid] = spawn_json(var_role(_b, _vid))          # fix: a full copy (var_role)
                VAR_IDS[_vid] = (_b, _s + 1, _zone, _fam)
        _vsplit += 1
    assert abs(sum(float(_x["Weight"]) for _x in _out) - sum(float(_x["Weight"]) for _x in _d["NPCs"])) < 0.01 * max(1, len(_out)), "0.1.22: %s total weight moved" % _k
    if len(_out) != len(_d["NPCs"]):
        _d["NPCs"] = _out
        SPAWN_FILES[SPAWN_DIR + _k + ".json"] = spawn_json(_d)
assert VAR_IDS, "0.1.22: no tougher versions made"
assert all(_v[3] == "goblin" or _v[0].startswith(("Skeleton_", "Zombie", "Outlander_")) for _v in VAR_IDS.values())
assert any(_b.startswith("Skeleton_Fighter") for _b, _s, _z, _f in VAR_IDS.values()), "0.1.22: the Zone 1 skeleton fighters get tougher versions"
# the one-pair-per-file engine rule again (vanilla + ours after the split) + every id real
_SP_ALL = dict(SPAWN_VAN)
_SP_ALL.update(SPAWN_NEW)
_dup = [(_p, _f) for _p, _f in spawn_pairs(_SP_ALL).items() if len(_f) > 1]
assert not _dup, "0.1.22: an NPC + environment pair in two files: %s" % _dup[:4]
for _k, _d in SPAWN_NEW.items():
    for _e in _d["NPCs"]:
        assert _e["Id"] in ROLES or _e["Id"] in VAR_IDS, "0.1.22: %s names role %s" % (_k, _e["Id"])
# the tougher versions get band levels like their vanilla role (MobCfg.VANILLA = the built-in list)
LEVELLED = sorted(set(LEVELLED) | set(VAR_IDS))
LEVELLED_TEXT = ",".join(LEVELLED)
_lev_low = set(n.lower() for n in LEVELLED)
assert len(LEVELLED_TEXT) < 60000 and all(levelled(_v) for _v in VAR_IDS), "0.1.22: the built-in list"
assert not [_v for _v in VAR_IDS if matches(BOSS_PATS, _v) or matches(GUARDS, _v)], "0.1.22: a tougher version would count as a boss / guard"
# fix3 (critic): MobGlob.any / MobCfg.roleIdx also try the vanilla base id, so no base may be a boss / guard either
assert not [_b for _b, _s, _z, _f in VAR_IDS.values() if matches(BOSS_PATS, _b) or matches(GUARDS, _b)], "0.1.22: a tougher-version base counts as a boss / guard"
# the element: MobElem.row reads the base id - the Python check that every base keeps a row-match it had
print("0.1.22 tougher versions: %d new roles (+ %d models) from %d spawn entries; %s" % (len(VAR_IDS), len(VAR_IDS), _vsplit, VAR_PACK))
for _z in (1, 2, 3, 4):
    _bz = sorted(set(_b for _b, _s, _zz, _f in VAR_IDS.values() if _zz == _z))
    print("   Zone %d (%s): %s" % (_z, " / ".join(VAR_METAL[_z]), ", ".join(_bz) or "-"))
print("   no tougher versions: " + "; ".join("%s (%s)" % (_b, _w) for _b, _w in sorted(VAR_SKIPPED.items()) if _w != "not a tougher-version family"))
# Server Setup > Mobs > Tougher mobs (the data; the kit rows + file lines below)
VAR_ROWS = [("variant.on", "Tougher versions (Armored / Veteran)", "variant", "bool", "true", "", "", "", "", "live",
             "OFF removes them as they spawn or load. Before a rollback: OFF, then /mobs strip variants.", "field:MobCfg.VAR_ON")]
for _w, _lab, _hp, _dm, _lv, _dr in VAR_STEPS:
    _F = "VAR_%s_" % _w[0].upper()
    VAR_ROWS += [("variant.%s.hp" % _w, "%s Health x" % _lab, "variant", "dec", "%g" % _hp, "1", "10", "", "x", "live",
                  "%s mobs' Health x this on top of level and rank (default %gx). XP follows Health." % (_lab, _hp), "field:MobCfg.%sHP;after=MobCfg.derive" % _F),
                 ("variant.%s.dmg" % _w, "%s damage x" % _lab, "variant", "dec", "%g" % _dm, "1", "10", "", "x", "live",
                  "%s mobs' hits x this on top of level and rank (default %gx)." % (_lab, _dm), "field:MobCfg.%sDMG;after=MobCfg.derive" % _F),
                 ("variant.%s.levels" % _w, "%s extra levels" % _lab, "variant", "int", str(_lv), "0", "10", "", "", "live",
                  "%s mobs spawn this many levels above their band roll." % _lab, "field:MobCfg.%sLV" % _F),
                 ("variant.%s.drops" % _w, "%s extra drop chance" % _lab, "variant", "dec", "%g" % _dr, "0", "100", "", "%", "live",
                  "Chance of one more roll of its own drop list. Its armour never drops.", "field:MobCfg.%sDROP" % _F)]
VAR_ROWS += [("variant.share.z%d" % _z, "Zone %d tougher-version share" % _z, "variant", "int", "100", "0", "100", "", "%", "live",
              ("Mix built in (easy 70/25/5 to hardest 40/40/20, not editable): % of it kept. Lower = fewer." if _z == 1 else
               "% of the built-in mix kept in Zone " + str(_z) + ". 100 = all; lower = extras removed as they spawn."), "field:MobCfg.VAR_Z%d" % _z)
             for _z in (1, 2, 3, 4)]
assert len(VAR_ROWS) == 13 and all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in VAR_ROWS), [(len(_r[1]), len(_r[10])) for _r in VAR_ROWS]
''')

# ---------- 2. the default file lines + the Tougher mobs tab
P.rep('''              ] + ["spawn.density.z%d=%d" % (_z, SPAWN_DENS_DEF) for _z in (1, 2, 3, 4)]          # 0.1.21''',
      '''              ] + ["spawn.density.z%d=%d" % (_z, SPAWN_DENS_DEF) for _z in (1, 2, 3, 4)]          # 0.1.21
CFG_LINES += ["# Tougher versions (SkyyMobs 0.1.22): Armored / Veteran mobs wear the zone's vanilla armour (a look, never dropped) and get more",
              "# Health / damage / levels plus an extra drop roll. The mix per biome tier is built in; variant.share.zN keeps that % of it.",
              ] + ["%s=%s" % (_r[0], _r[4]) for _r in VAR_ROWS]          # 0.1.22''')
P.rep('''CFG_CATS.insert(CFG_CATS.index(("secret", "Secret eggs")) + 1, ("spawn", "Spawns"))          # 0.1.21''',
      '''CFG_CATS.insert(CFG_CATS.index(("secret", "Secret eggs")) + 1, ("spawn", "Spawns"))          # 0.1.21
CFG_CATS.insert(CFG_CATS.index(("spawn", "Spawns")) + 1, ("variant", "Tougher mobs"))          # 0.1.22''')
P.rep('''CFG_ROWS += SPAWN_ROWS
''', '''CFG_ROWS += SPAWN_ROWS
CFG_ROWS += VAR_ROWS          # 0.1.22 (variety1): the tougher versions (live)
''')
P.rep('''platetest, reload, spawns (admins).''', '''platetest, reload, spawns, strip (admins).''')

# ---------- 3. MobCfg fields + load + the health signature
P.rep('''    F(cfg, "public static volatile int SPAWN_Z%d = %d;" % (_z, SPAWN_DENS_DEF))
''', '''    F(cfg, "public static volatile int SPAWN_Z%d = %d;" % (_z, SPAWN_DENS_DEF))
F(cfg, "public static volatile boolean VAR_ON = true;")          # 0.1.22 (variety1): the tougher versions
for _w, _lab, _hp, _dm, _lv, _dr in VAR_STEPS:
    _F = "VAR_%s_" % _w[0].upper()
    for _f in ("public static volatile double %sHP = %r;" % (_F, _hp), "public static volatile double %sDMG = %r;" % (_F, _dm),
               "public static volatile int %sLV = %d;" % (_F, _lv), "public static volatile double %sDROP = %r;" % (_F, _dr)):
        F(cfg, _f)
for _z in (1, 2, 3, 4):
    F(cfg, "public static volatile int VAR_Z%d = 100;" % _z)
''')
P.rep('''  SPAWN_Z4 = intOf(c.getProperty("spawn.density.z4"), @SPDEF@, 0, @SPMAX@);''',
      '''  SPAWN_Z4 = intOf(c.getProperty("spawn.density.z4"), @SPDEF@, 0, @SPMAX@);
  VAR_ON = bool(c.getProperty("variant.on"), true);          // 0.1.22: the tougher versions (a missing line = the default)
  VAR_A_HP = dec(c.getProperty("variant.armored.hp"), 1.4, 1.0, 10.0);
  VAR_A_DMG = dec(c.getProperty("variant.armored.dmg"), 1.15, 1.0, 10.0);
  VAR_A_LV = intOf(c.getProperty("variant.armored.levels"), 1, 0, 10);
  VAR_A_DROP = dec(c.getProperty("variant.armored.drops"), 25.0, 0.0, 100.0);
  VAR_V_HP = dec(c.getProperty("variant.veteran.hp"), 1.9, 1.0, 10.0);
  VAR_V_DMG = dec(c.getProperty("variant.veteran.dmg"), 1.3, 1.0, 10.0);
  VAR_V_LV = intOf(c.getProperty("variant.veteran.levels"), 2, 0, 10);
  VAR_V_DROP = dec(c.getProperty("variant.veteran.drops"), 50.0, 0.0, 100.0);
  VAR_Z1 = intOf(c.getProperty("variant.share.z1"), 100, 0, 100);
  VAR_Z2 = intOf(c.getProperty("variant.share.z2"), 100, 0, 100);
  VAR_Z3 = intOf(c.getProperty("variant.share.z3"), 100, 0, 100);
  VAR_Z4 = intOf(c.getProperty("variant.share.z4"), 100, 0, 100);''')
P.rep('''    + "|elem|" + ELEM_MOBS + "|" + ELEM_PLATE;          // 0.1.17: the element plates''',
      '''    + "|elem|" + ELEM_MOBS + "|" + ELEM_PLATE          // 0.1.17: the element plates
    + "|var|" + VAR_A_HP + "|" + VAR_A_DMG + "|" + VAR_V_HP + "|" + VAR_V_DMG;          // 0.1.22: a tougher-version edit re-applies the loaded mobs''')

# ---------- 4. MobCfg: the variant id helpers (before MobElem.row, their first caller) + the numbers (after eliteRoll: mix64) + factors
# ---------- 4a. fix3 (critic): an admin row naming the vanilla role (exact id or a pattern) also covers its Armored / Veteran ids - MobGlob.any
# (Never level these, rank lists, pack helpers, boss list) and MobCfg.roleIdx (the role table) also try the base id (MobGlob.base = lower case)
P.rep('''M(gb, r"""
public static boolean any(String[] pats, String s) {
  if (pats == null || s == null) return false;
  String k = s.toLowerCase();
  for (int i = 0; i < pats.length; i++) if (glob(pats[i], k)) return true;
  return false;
}""")''', '''M(gb, r"""
public static String base(String k) {
  if (k == null) return null;
  int i = k.indexOf("_skyyarmored");
  if (i <= 0) i = k.indexOf("_skyyveteran");
  return i > 0 ? k.substring(0, i) : k;
}""")
M(gb, r"""
public static boolean any(String[] pats, String s) {
  if (pats == null || s == null) return false;
  String k = s.toLowerCase();
  String kb = base(k);          // 0.1.22 fix3: a tougher version also matches its vanilla role's rows
  for (int i = 0; i < pats.length; i++) if (glob(pats[i], k) || (kb != k && glob(pats[i], kb))) return true;
  return false;
}""")''')
P.rep('''  String[] lo = (String[]) t[1];
  String k = role.toLowerCase();
  for (int i = 0; i < lo.length; i++) if (lo[i].indexOf('*') < 0 && lo[i].equals(k)) return i;
  int best = -1, bs = -1;
  for (int i = 0; i < lo.length; i++) {
    if (lo[i].indexOf('*') < 0) continue;
    int sp = @PKG@.MobGlob.spec(lo[i]);
    if (sp > bs && @PKG@.MobGlob.glob(lo[i], k)) { best = i; bs = sp; }
  }
  return best;''', '''  String[] lo = (String[]) t[1];
  String k = role.toLowerCase();
  String kb = @PKG@.MobGlob.base(k);          // 0.1.22 fix3: a tougher version: its own exact row, else its vanilla role's, else the patterns
  for (int i = 0; i < lo.length; i++) if (lo[i].indexOf('*') < 0 && lo[i].equals(k)) return i;
  if (kb != k) for (int i = 0; i < lo.length; i++) if (lo[i].indexOf('*') < 0 && lo[i].equals(kb)) return i;
  int best = -1, bs = -1;
  for (int i = 0; i < lo.length; i++) {
    if (lo[i].indexOf('*') < 0) continue;
    int sp = @PKG@.MobGlob.spec(lo[i]);
    if (sp > bs && (@PKG@.MobGlob.glob(lo[i], k) || (kb != k && @PKG@.MobGlob.glob(lo[i], kb)))) { best = i; bs = sp; }
  }
  return best;''')
P.rep('''# the row of a role: the most literal characters, the first entry on a tie; -1 = none''',
      '''# 0.1.22 (variety1): a tougher-version id = <vanilla role>_SkyyArmored<zone> / _SkyyVeteran<zone> (tools/mobs_0_1_22_patch.py var_split mirrors it)
M(cfg, r"""
public static int variantOf(String role) {
  if (role == null) return 0;
  if (role.indexOf("_SkyyVeteran") > 0) return 2;
  if (role.indexOf("_SkyyArmored") > 0) return 1;
  return 0;
}""")
M(cfg, r"""
public static String baseRole(String role) {
  if (role == null) return null;
  int i = role.indexOf("_SkyyArmored");
  if (i <= 0) i = role.indexOf("_SkyyVeteran");
  return i > 0 ? role.substring(0, i) : role;
}""")
M(cfg, r"""
public static int variantZone(String role) {
  if (variantOf(role) == 0) return 0;
  char c = role.charAt(role.length() - 1);
  return c >= '1' && c <= '9' ? (int) (c - '0') : 0;
}""")
# the row of a role: the most literal characters, the first entry on a tie; -1 = none''')
P.rep('''  String[] p = (String[]) t[0];
  int[] sp = (int[]) t[1];
  String k = role.toLowerCase();''', '''  String[] p = (String[]) t[0];
  int[] sp = (int[]) t[1];
  String k = @PKG@.MobCfg.baseRole(role).toLowerCase();          // 0.1.22: a tougher version has its vanilla role's element''')
P.rep('''# fix2 (critic: clear-all dropped live mobs' ranks): RANKFIX holds at most 2000''', '''# 0.1.22 (variety1): the step numbers (Server Setup > Mobs > Tougher mobs), the zone share roll (fixed per mob UUID, its own salt), the plate word
M(cfg, "public static double varHp(int v) { return v == 2 ? VAR_V_HP : (v == 1 ? VAR_A_HP : 1.0); }")
M(cfg, "public static double varDmg(int v) { return v == 2 ? VAR_V_DMG : (v == 1 ? VAR_A_DMG : 1.0); }")
M(cfg, "public static int varLevels(int v) { return v == 2 ? VAR_V_LV : (v == 1 ? VAR_A_LV : 0); }")
M(cfg, "public static double varDrops(int v) { return v == 2 ? VAR_V_DROP : (v == 1 ? VAR_A_DROP : 0.0); }")
M(cfg, "public static String varWord(int v) { return v == 2 ? \\"Veteran\\" : (v == 1 ? \\"Armored\\" : \\"\\"); }")
M(cfg, r"""
public static int varShare(int zone) {
  if (zone == 1) return VAR_Z1;
  if (zone == 2) return VAR_Z2;
  if (zone == 3) return VAR_Z3;
  if (zone == 4) return VAR_Z4;
  return 100;
}""")
M(cfg, r"""
public static boolean keep(java.util.UUID u, int zone) {
  int s = varShare(zone);
  if (s >= 100) return true;
  if (s <= 0) return false;
  if (u == null) return true;
  long h = mix64(u.getMostSignificantBits() ^ 7046029254386353131L);
  h = mix64(h ^ u.getLeastSignificantBits());
  return Long.remainderUnsigned(h, 100L) < (long) s;
}""")
M(cfg, r"""
public static String varName(String role, String name) {
  String w = varWord(variantOf(role));
  String n = name == null ? "" : name;
  if (w.length() == 0 || n.startsWith(w + " ")) return n;
  return w + " " + n;
}""")
# fix2 (critic: clear-all dropped live mobs' ranks): RANKFIX holds at most 2000''')
P.rep('''  double hx = roleX(role) * rankHp(r, base);''', '''  int v = variantOf(role);          // 0.1.22: x the tougher version (Armored / Veteran)
  double hx = roleX(role) * rankHp(r, base) * varHp(v);''')
P.rep('''  return new double[] { hx, roleDx(role) * rankDmg(r), (double) r };''',
      '''  return new double[] { hx, roleDx(role) * rankDmg(r) * varDmg(v), (double) r };''')

# ---------- 5. MobLevel: the plate word + the extra levels; MobInfoFn: XP follows the variant's Health
P.rep('''  if (rk == 1) name = "Elite " + name;            // 0.1.14: the rank on the plate''', '''  name = @PKG@.MobCfg.varName(role, name);          // 0.1.22: "Armored" / "Veteran" first, so the rank word leads: "Elite Armored Skeleton"
  if (rk == 1) name = "Elite " + name;            // 0.1.14: the rank on the plate''')
P.rep('''      if (level > @PKG@.MobCfg.MAX_LEVEL) level = @PKG@.MobCfg.MAX_LEVEL;
    }
  }
  apply(h, null, null, npc, m, u, w, wn, role, level, spawn, step, res);''', '''      if (level > @PKG@.MobCfg.MAX_LEVEL) level = @PKG@.MobCfg.MAX_LEVEL;
    }
    int vl = @PKG@.MobCfg.varLevels(@PKG@.MobCfg.variantOf(role));          // 0.1.22: a tougher version spawns above its band roll
    if (vl > 0) {
      level = level + vl;
      if (level > @PKG@.MobCfg.MAX_LEVEL) level = @PKG@.MobCfg.MAX_LEVEL;
    }
  }
  apply(h, null, null, npc, m, u, w, wn, role, level, spawn, step, res);''')
P.rep('''    if (m.rank > 0) {   // 0.1.14''', '''    if (m.rank > 0 || @PKG@.MobCfg.variantOf(m.role) > 0) {   // 0.1.22: + a tougher version (XP follows its Health); 0.1.14''')

# ---------- 5b. fix2 (critic): under the plate.colorOn trial the plate takes the step's rarity colour (Armored yellow, Veteran pink), an Elite
# cyan, a plain (Normal) mob white (Skyy 2026-10-27: "nameplates white / yellow / pink, elites cyan" - replaces the old level-colour ladder
# under the trial; fix3 (critic): plain was still the level colour). The 2-argument plateText (no role) keeps the level colour.
P.rep('''# 0.1.17 (elem1, spec 8): + the mob's OWN element''', '''# 0.1.22 fix2: the plate colour of a mob (an Elite cyan, a tougher version its rarity colour, a plain mob Normal white - fix3)
M(lv, r"""
public static String plateHex(int level, String name, String role) {
  if (name != null && name.startsWith("Elite ")) return "@LEG@";
  int v = @PKG@.MobCfg.variantOf(role);
  if (v == 2) return "@RARE@";
  if (v == 1) return "@UNIQ@";
  return "@NORM@";          // fix3 (critic): Skyy's "white" for a Normal mob
}""".replace("@LEG@", SUI.RARITY["Legendary"]).replace("@RARE@", SUI.RARITY["Rare"]).replace("@UNIQ@", SUI.RARITY["Unique"]).replace("@NORM@", SUI.RARITY["Normal"]))
# 0.1.17 (elem1, spec 8): + the mob's OWN element''')
P.rep('''  if (el.length() == 0) return plateText(level, name);
  String f = @PKG@.MobCfg.FORMAT;''', '''  String f = @PKG@.MobCfg.FORMAT;          // 0.1.22 fix2: no element = the same text below (part ""), coloured by plateHex''')
P.rep('''  boolean tok = f.indexOf("{element}") >= 0;
  String t = f.replace("{element}", part)''', '''  if (el.length() == 0) part = "";          // 0.1.22 fix2: no element = the 2-argument text, coloured below by plateHex
  boolean tok = f.indexOf("{element}") >= 0 || el.length() == 0;
  String t = f.replace("{element}", part)''')
P.rep('''  String m = markup(t, hexFor(level), @PKG@.MobCfg.MARKUP);
  return tok ? m : m + markup(part''', '''  String m = markup(t, plateHex(level, name, role), @PKG@.MobCfg.MARKUP);          // 0.1.22 fix2
  return tok ? m : m + markup(part''')

# ---------- 6. engine classes + probes
P.rep('''          "GPCF": "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig",''',
      '''          "GPCF": "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig",
          "RSYS": "com.hypixel.hytale.component.system.RefSystem",          # 0.1.22 (variety1): the tougher-version add check''')
P.rep('''         (G["GPCF"], "getMaxEnvironmentalNPCSpawns", "int", [])]''', '''         (G["GPCF"], "getMaxEnvironmentalNPCSpawns", "int", [])]
# 0.1.22 (variety1): the add hook (SkyyZones' no-spawn pattern), the removal from a command buffer / the command's store, the mob by UUID
SIGS += [(G["RSYS"], "onEntityAdded", "void", [G["REF"], G["ADDR"], G["ST"], G["CB"]]),
         (G["RSYS"], "onEntityRemove", "void", [G["REF"], G["REMR"], G["ST"], G["CB"]]),
         (G["CB"], "tryRemoveEntity", "void", [G["REF"], G["REMR"]]), (G["ST"], "removeEntity", G["HOLD"], [G["REF"], G["REMR"]]),
         (G["WLD"], "getEntityStore", G["EST"], []), (G["EST"], "getRefFromUUID", G["REF"], ["java.util.UUID"])]
B.probe(pool, G["ADDR"], "LOAD")
PROBED.append("AddReason.LOAD")''')

# ---------- 7. the classes
P.rep('''mspk = pool.makeClass(PKG + ".MobSpawnTask")  # 0.1.21: the 30 s re-check (an asset reload puts vanilla back)''',
      '''mspk = pool.makeClass(PKG + ".MobSpawnTask")  # 0.1.21: the 30 s re-check (an asset reload puts vanilla back)
mvar = pool.makeClass(PKG + ".MobVariant")    # 0.1.22 (variety1): the tougher versions (add check, extra drop, strip, inspect, text)
mvsy = pool.makeClass(PKG + ".MobVariantSys", pool.get(G["RSYS"]))   # 0.1.22: variant.on OFF / the zone share remove them as they spawn / load''')
P.rep('''msp, mss, mel, mef, meo, megg, msec, mlds, mvat, mspw, mspk]''', '''msp, mss, mel, mef, meo, megg, msec, mlds, mvat, mspw, mspk, mvar, mvsy]''')

MVAR = r'''# ================================================================= 0.1.22 MobVariant: the tougher versions (tools/mobs_0_1_22_patch.py docstring)
# removeOnAdd = the rule of MobVariantSys (pure: a role, a UUID, spawn or load); inspectLine / strip = the admin lines; extra (below, after
# MobSpoils.clean) = the extra drop roll. KINDS = the variant roles in this jar.
for _f in ("public static final int KINDS = %d;" % len(VAR_IDS), "public static volatile boolean SYS_ON = false;",
           "public static volatile long SEEN = 0L;", "public static volatile long OFF_N = 0L;", "public static volatile long SHARE_N = 0L;",
           "public static volatile long STRIPPED = 0L;", "public static volatile long DROPS = 0L;", "public static volatile long ROLLS = 0L;"):
    F(mvar, _f)
M(mvar, r"""
public static boolean removeOnAdd(String role, java.util.UUID u, boolean spawn) {
  if (@PKG@.MobCfg.variantOf(role) == 0) return false;
  if (!@PKG@.MobCfg.VAR_ON) { OFF_N = OFF_N + 1L; return true; }
  if (spawn && !@PKG@.MobCfg.keep(u, @PKG@.MobCfg.variantZone(role))) { SHARE_N = SHARE_N + 1L; return true; }
  if (spawn) SEEN = SEEN + 1L;
  return false;
}""")
M(mvar, r"""
public static String colour(int v) {
  if (v == 2) return "Rare pink @RARE@";
  if (v == 1) return "Unique yellow @UNIQ@";
  return "Normal white @NORM@";
}""".replace("@RARE@", SUI.RARITY["Rare"]).replace("@UNIQ@", SUI.RARITY["Unique"]).replace("@NORM@", SUI.RARITY["Normal"]))
M(mvar, r"""
public static String num(double d) {
  long r = Math.round(d * 100.0);
  String s = String.valueOf((double) r / 100.0);
  return s.endsWith(".0") ? s.substring(0, s.length() - 2) : s;
}""")
M(mvar, r"""
public static String inspectLine(String role) {
  int v = @PKG@.MobCfg.variantOf(role);
  if (v == 0) return null;
  return "=Tougher version: " + @PKG@.MobCfg.varWord(v) + " (rarity colour " + colour(v) + "; the plate takes it with the plate.colorOn trial, else the word) - Health x"
      + num(@PKG@.MobCfg.varHp(v)) + ", damage x" + num(@PKG@.MobCfg.varDmg(v)) + ", +" + @PKG@.MobCfg.varLevels(v) + " level(s), extra drop roll "
      + num(@PKG@.MobCfg.varDrops(v)) + " % (its armour never drops); vanilla role " + @PKG@.MobCfg.baseRole(role) + ", Zone " + @PKG@.MobCfg.variantZone(role) + " armour"
      + (@PKG@.MobCfg.VAR_ON ? "" : "; Tougher versions is OFF - it goes when its chunk reloads");
}""")
# /mobs strip variants: every Armored / Veteran mob levelled in this world (MobLevel.MOBS; the command runs on the world thread), removed
M(mvar, r"""
public static String strip(@ST@ store, @WLD@ world, String what) {
  if (what == null || !what.trim().equalsIgnoreCase("variants")) return "-[Mobs] Type /mobs strip variants - it removes every Armored / Veteran mob loaded in this world.";
  if (store == null || world == null) return "-[Mobs] Run this in a world.";
  @EST@ es = world.getEntityStore();
  java.util.ArrayList refs = new java.util.ArrayList();
  java.util.Iterator it = @PKG@.MobLevel.MOBS.values().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @PKG@.MobInfo)) continue;
    @PKG@.MobInfo i = (@PKG@.MobInfo) o;
    if (i.uuid == null || @PKG@.MobCfg.variantOf(i.role) == 0 || i.wref == null || i.wref.get() != world) continue;
    @REF@ r = es == null ? null : es.getRefFromUUID(i.uuid);
    if (r != null && r.isValid()) refs.add(r);
  }
  int n = 0;
  for (int k = 0; k < refs.size(); k++) {
    @REF@ r = (@REF@) refs.get(k);
    try { if (r.isValid()) { store.removeEntity(r, @REMR@.REMOVE); n++; } } catch (Throwable t) { @PKG@.MobLog.warnOnce("strip1", "/mobs strip variants: one mob could not be removed (" + t + ")"); }
  }
  STRIPPED = STRIPPED + (long) n;
  return "+[Mobs] Removed " + n + " tougher-version mob" + (n == 1 ? "" : "s") + " (Armored / Veteran) in " + world.getName() + "."
      + (@PKG@.MobCfg.VAR_ON ? " New ones keep spawning while Tougher versions is ON (Server Setup > Mobs > Tougher mobs)." : " Tougher versions is OFF: unloaded ones go as their chunks load.");
}""")
M(mvar, r"""
public static String text() {
  return "tougher versions " + (@PKG@.MobCfg.VAR_ON ? "on" : "OFF") + " (" + KINDS + " roles" + (SYS_ON ? "" : ", add check NOT registered") + "; spawned " + SEEN + ", removed off " + OFF_N + " / share " + SHARE_N + ", stripped " + STRIPPED + ", extra drops " + DROPS + "/" + ROLLS + ")";
}""")

'''
P.rep('''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)''',
      MVAR + '''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)''')

MVSY = r'''# 0.1.22 (variety1): the extra drop roll of a tougher version (any player kill; Spoils rows not needed): one more roll of the mob's own drop
# list without gear (MobSpoils.clean = never its armour / weapons); returns the items added
M(mvar, r"""
public static int extra(java.util.ArrayList l, String role, String dl, java.util.Random rng) {
  int v = @PKG@.MobCfg.variantOf(role);
  if (v == 0 || l == null || dl == null || rng == null || !@PKG@.MobCfg.VAR_ON) return 0;
  double c = @PKG@.MobCfg.varDrops(v);
  ROLLS = ROLLS + 1L;
  if (!(c > 0.0) || !(rng.nextDouble() * 100.0 < c)) return 0;
  java.util.ArrayList x = @PKG@.MobSpoils.clean(@PKG@.MobSpoils.roll(dl));
  if (x.isEmpty()) return 0;
  l.addAll(x);
  DROPS = DROPS + 1L;
  return x.size();
}""")
# fix3 (critic): SkyyZones' no-spawn rule at a spot (zones:fn:noSpawn {world, x, y, z} -> Boolean; no SkyyZones / any failure = false)
F(mvar, "public static volatile long ZONES_N = 0L;")
M(mvar, r"""
public static boolean zonesTakes(String w, double x, double y, double z) {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (!(b instanceof java.util.Map) || w == null) return false;
    Object f = ((java.util.Map) b).get("zones:fn:noSpawn");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { w, Integer.valueOf((int) Math.floor(x)), Integer.valueOf((int) Math.floor(y)), Integer.valueOf((int) Math.floor(z)) });
    if (!Boolean.TRUE.equals(r)) return false;
    ZONES_N = ZONES_N + 1L;
    return true;
  } catch (Throwable t) { return false; }
}""")
# MobVariantSys: variant.on OFF = remove every tougher version as it spawns or loads; a zone share below 100 = remove the extra ones as they spawn
F(mvsy, "public static volatile boolean FAILED_ONCE = false;")
F(mvsy, "public @QRY@ query;")
C(mvsy, "public MobVariantSys() { super(); }")
M(mvsy, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @NPCE@.getComponentType(), (@QRY@) @UUIDC@.getComponentType() });
  return this.query;
}""")
M(mvsy, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ why, @ST@ st, @CB@ cb) {
  try {
    if (why != @ADDR@.SPAWN && why != @ADDR@.LOAD) return;
    @NPCE@ npc = (@NPCE@) st.getComponent(ref, @NPCE@.getComponentType());
    if (npc == null) return;
    String role = npc.getRoleName();
    if (@PKG@.MobCfg.variantOf(role) == 0) return;
    @UUIDC@ uc = (@UUIDC@) st.getComponent(ref, @UUIDC@.getComponentType());
    if (!@PKG@.MobVariant.removeOnAdd(role, uc == null ? null : uc.getUuid(), why == @ADDR@.SPAWN)) return;
    // fix3 (critic): a natural spawn inside a SkyyZones town / safe region is removed by ZNoSpawn with a PLAIN removeEntity (that one fails on
    // a ref already gone) - leave it to that hook (zones:fn:noSpawn = its own rule; ZNoSpawn acts on SPAWN only, so LOAD needs no check)
    if (why == @ADDR@.SPAWN && npc.getEnvironment() != Integer.MIN_VALUE) {
      @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
      @WLD@ w = @PKG@.MobLevel.worldOf(st);
      if (tc != null && w != null) {
        @VEC@ p = tc.getPosition();
        if (@PKG@.MobVariant.zonesTakes(w.getName(), p.x, p.y, p.z)) return;
      }
    }
    cb.tryRemoveEntity(ref, @REMR@.REMOVE);          // fix1 (critic): try = a ref another add hook already removed is skipped, never thrown
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MobLog.warn("the tougher-version add check failed (logged once; that mob stays): " + t); }
  }
}""")
M(mvsy, "public void onEntityRemove(@REF@ ref, @REMR@ why, @ST@ st, @CB@ cb) { }")

'''
P.rep('''# SpoilsSys: NPC + DeathComponent''', MVSY + '''# SpoilsSys: NPC + DeathComponent''')
P.rep('''if (!@PKG@.MobSpoils.ON && !(@PKG@.MobCfg.DEGG_CHANCE > 0.0) && !@PKG@.MobCfg.SEC_ON) return;''',
      '''if (!@PKG@.MobSpoils.ON && !(@PKG@.MobCfg.DEGG_CHANCE > 0.0) && !@PKG@.MobCfg.SEC_ON && !@PKG@.MobCfg.VAR_ON) return;          // 0.1.22: + the tougher versions' extra roll''')
P.rep('''if (@PKG@.MobSpoils.ON) @PKG@.MobSpoils.coins(ku, lvl, @PKG@.MobSpoils.RNG);''',
      '''if (@PKG@.MobSpoils.ON) @PKG@.MobSpoils.coins(ku, lvl, @PKG@.MobSpoils.RNG);
    @PKG@.MobVariant.extra(l, npc.getRoleName(), role.getDropListId(), @PKG@.MobSpoils.RNG);          // 0.1.22: a tougher version's extra drop roll''')

# ---------- 8. /mobs inspect + /mobs strip variants
P.rep('''  L.add("=Plate: " + (plate == null''', '''  String vline = @PKG@.MobVariant.inspectLine(role);          // 0.1.22: the tougher version
  if (vline != null) L.add(vline);
  L.add("=Plate: " + (plate == null''')
P.rep('''cmd("MobsCmd", "mobs", "Mob levels: /mobs shows the level band where you stand", [],''',
      '''cmd("MobsStripCmd", "strip", "Admin: /mobs strip variants removes the Armored / Veteran mobs loaded in this world",
    [("whatArg", "what", "variants", "STRING")], X + "tell(pr, @PKG@.MobVariant.strip(store, world, a0));", perm=A)          # 0.1.22 (variety1)
cmd("MobsCmd", "mobs", "Mob levels: /mobs shows the level band where you stand", [],''')
P.rep('''subs=("MobsInfoCmd", "MobsInspectCmd", "MobsSetCmd", "MobsPlateCmd", "MobsReloadCmd", "MobsSpawnsCmd"))''',
      '''subs=("MobsInfoCmd", "MobsInspectCmd", "MobsSetCmd", "MobsPlateCmd", "MobsReloadCmd", "MobsSpawnsCmd", "MobsStripCmd"))''')

# ---------- 9. plugin: the system, the ready line
P.rep('''  try { getEntityStoreRegistry().registerSystem(new @PKG@.LightDeathSys()); }''',
      '''  // 0.1.22 (variety1): the tougher-version add check (ONE registerSystem); not registered = Tougher versions OFF / the shares remove nothing this start
  try { getEntityStoreRegistry().registerSystem(new @PKG@.MobVariantSys()); @PKG@.MobVariant.SYS_ON = true; }
  catch (Throwable t10) { @PKG@.MobVariant.SYS_ON = false; @PKG@.MobLog.warn("the tougher-version add check could not be registered (" + t10 + ") - this start Tougher versions OFF and the zone shares remove nothing (/mobs strip variants still works)"); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.LightDeathSys()); }''')
P.rep('''@PKG@.MobSpawn.text() + "; /mobs;''', '''@PKG@.MobSpawn.text() + "; " + @PKG@.MobVariant.text() + "; /mobs;''')

# ---------- 10. the jar: + the variant roles / models
P.rep('''assert all(_p.startswith(SPAWN_DIR) and _p.endswith(".json") for _p in SPAWN_FILES)
B.assemble(jar, man, OUT, extra_files=SPAWN_FILES)''', '''man["Description"] += " 0.1.22: tougher versions - Armored / Veteran mobs in the zone's vanilla armour (Server Setup > Mobs > Tougher mobs; /mobs strip variants)."
assert all(_p.startswith(SPAWN_DIR) and _p.endswith(".json") for _p in SPAWN_FILES)
assert all(_p.startswith(("Server/NPC/Roles/SkyyMobs/", "Server/Models/SkyyMobs/")) and _p.endswith(".json") for _p in VAR_FILES)
assert not set(SPAWN_FILES) & set(VAR_FILES) and len(VAR_FILES) == 2 * len(VAR_IDS)
_EXTRA = dict(SPAWN_FILES)
_EXTRA.update(VAR_FILES)
B.assemble(jar, man, OUT, extra_files=_EXTRA)''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 + 1 and P.s.count("makeClass(") == CLS0 + 2, "0.1.22: 2 classes (+ 1 command class through cmd()), 1 system, no command"
_i = P.s.index
assert _i("public static String baseRole(String role)") < _i("String k = @PKG@.MobCfg.baseRole(role)") < _i("public static boolean eliteRoll(") < _i("public static boolean keep(java.util.UUID u") \
    < _i("public static String varName(") < _i("public static double[] factors(") < _i("name = @PKG@.MobCfg.varName(role, name);") < _i("int vl = @PKG@.MobCfg.varLevels(")
assert _i("public static boolean removeOnAdd(") < _i("public static String inspectLine(") < _i("public static String[] inspect(@PR@ pr") < _i('cmd("MobsStripCmd"') < _i('cmd("MobsCmd"')
assert _i("public static java.util.ArrayList clean(") < _i("public static int extra(java.util.ArrayList l") < _i("@PKG@.MobVariant.extra(l, npc.getRoleName()")
assert _i("public static String strip(@ST@ store") < _i('cmd("MobsStripCmd"') and _i("VAR_ROWS = [") < _i('CFG_LINES += ["# Tougher versions') < _i("CFG_ROWS += VAR_ROWS")
assert _i('assert len(LEVELLED_TEXT) < 60000 and all(levelled(_v)') <_i('"public static final String VANILLA = %s;" % jstr(LEVELLED_TEXT)')
P.finish()
print("wrote", P.dst)
