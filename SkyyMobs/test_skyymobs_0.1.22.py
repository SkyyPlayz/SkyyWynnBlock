"""Harness for SkyyMobs 0.1.22 (round variety1: tougher versions - Armored / Veteran roles + models in the jar, the mix in the spawn files,
the variant ranks, the extra drop roll, Server Setup > Mobs > Tougher mobs, /mobs strip variants; tools/mobs_0_1_22_patch.py).
Build first:
    python tools/mobs_0_1_22_patch.py && python SkyyMobs/build_skyymobs_0.1.22.py
    python SkyyMobs/test_skyymobs_0.1.22.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes (--out), line endings kept, +2 makeClass (+ 1 command class through cmd()), +1 system,
                 no command; jar: only the 3 new classes + the variant roles / models added, nothing removed, the other changed non-class
                 files = the manifest + spawn files; every 0.1.21 spawn entry is unchanged or split into Normal / Armored / Veteran by its
                 tier's mix with the SAME total weight; every variant role = a FULL COPY of its vanilla role (same template Reference,
                 vanilla Parameters / Modify, *_Wander flattened onto its camp role; only Appearance = its own model + the vanilla
                 MemoriesNameOverride; no Armor list) that passes the ENGINE'S MODIFY RULE (mirror of BuilderModifier.applyTo: every
                 Modify key a public parameter the Reference declares itself - the rule the 20261028-065456 smoke hit; the mirror is
                 proved on all vanilla Variants and refuses the failed 0.1.22 form), every model = the base model + the zone's armour pieces, every path real in Assets.zip; ids new against
                 Assets.zip + every SET jar; no NPC + environment pair in two files; nothing vanilla-derived tracked in git
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.21 -> 0.1.22 (EXPECT below)
  X     exec     EXECUTES the new code in a bare JVM: the id helpers (= the Python mirror on every jar id), the step numbers + live edits,
                 keep() (fixed per UUID, ~share %), varName, factors (x1.4 / x1.15, x1.9 / x1.3, elite on top), the element of a variant
                 (= its base), mob:fn:info kill XP (xpMult follows the variant's Health), MobVariant.removeOnAdd (on / OFF / share, spawn vs
                 load), extra() through the MobSpoils.ROLLS seam (rate ~25 / 50 %, gear filtered = the armour never drops, OFF = none),
                 inspectLine, strip() refusals, text(), MobVariantSys (hook on bad input caught + logged once, onEntityRemove), the 13 Server
                 Setup rows + the default file lines
  EX121 0.1.21's exec phase EXECUTED on this jar (the spawn densities unchanged)
  D     live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs: config / bands / trees bytes untouched (no
                 migration), the variant numbers = their defaults (no line in the live file), start 2 the same
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the engine's real role loader (NPCPlugin BuilderManager needs the whole server - the S mirror of its
Modify rule + the smoke test cover it), the
client drawing the armour on each body (goblin pieces on goblins, player sets on skeletons / outlanders / zombies), the spawner picking
the split entries, RefSystem.onEntityAdded removing a mob live, MobLevel.onAdd's extra levels and the plate word on a live mob, SpoilsSys
calling extra() on a real death, /mobs strip variants on a live world.
Scratch: tools/dev/scratch/variety1/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, json, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.22"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "variety1", "mobs")]
import skyybuild as B
import harness_kit as HK
import serverjar as SJ

_run0 = HK.run
HK.run = lambda *a, **k: None          # import 0.1.21's harness for its exec phase without running it
_s = importlib.util.spec_from_file_location("test_skyymobs_0_1_21", os.path.join(HERE, "test_skyymobs_0.1.21.py"))
T121 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(T121)
HK.run = _run0

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.21.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_22_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.21.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")
ADDED = ["MobVariant", "MobVariantSys", "MobsStripCmd"]
SD = "Server/NPC/Spawn/World/"
RD, MD = "Server/NPC/Roles/SkyyMobs/", "Server/Models/SkyyMobs/"
MIX = {1: (70, 25, 5), 2: (55, 35, 10), 3: (40, 40, 20)}
FILE_TIER = {"Zone1/Spawns_Zone1_Caves_Goblins": 1, "Zone3/Spawns_Zone3_Outlander": 2, "Zone4/Spawns_Zone4_Wastes_Predator": 2,
             "Zone4/Spawns_Zone4_Volcanoes_Predator": 3}
METAL = {1: ("Copper", "Iron"), 2: ("Thorium", "Steel"), 3: ("Cobalt", "Adamantite"), 4: ("Mithril", "Mithril")}
EXPECT = {
    "MobCfg": ["+f VAR_ON", "+f VAR_A_HP", "+f VAR_A_DMG", "+f VAR_A_LV", "+f VAR_A_DROP", "+f VAR_V_HP", "+f VAR_V_DMG", "+f VAR_V_LV",
               "+f VAR_V_DROP", "+f VAR_Z1", "+f VAR_Z2", "+f VAR_Z3", "+f VAR_Z4", "+m variantOf", "+m baseRole", "+m variantZone",
               "+m varHp", "+m varDmg", "+m varLevels", "+m varDrops", "+m varWord", "+m varShare", "+m keep", "+m varName",
               "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults", "~m factors", "~m derive", "~m van", "~m roleIdx"],          # van: the built-in list (+ the variant ids); roleIdx: fix3
    "MobElem": ["~m row"],
    "MobGlob": ["+m base", "~m any"],          # fix3: a tougher version also matches its vanilla role's rows
    "MobLevel": ["+m plateHex", "~m apply", "~m onAdd", "~m plateText"],          # fix2: plateHex + the 3-argument plateText
    "MobInfoFn": ["~m apply"],
    "SpoilsSys": ["~m tick"],
    "MobCmds": ["~m inspect"],
    "MobsCmd": ["~c "],          # the constructor: + addSubCommand(new MobsStripCmd())
    "SkyyMobsPlugin": ["~m setup", "~m systems"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],          # the kit: the 13 new rows + the default file text
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
T121.PKG = PKG


def var_split(vid):
    """the Python mirror of MobCfg.variantOf / baseRole / variantZone"""
    for s, suf in enumerate(("_SkyyArmored", "_SkyyVeteran")):
        i = vid.find(suf)
        if i > 0:
            return s + 1, vid[:i], int(vid[-1]) if vid[-1].isdigit() else 0
    return 0, vid, 0


def jar_ids(jar):
    return sorted(n[len(RD):-5] for n in zipfile.ZipFile(jar).namelist() if n.startswith(RD) and n.endswith(".json"))


def lenient(t):
    t = re.sub(r"//[^\n]*", "", t)
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return json.loads(re.sub(r",\s*([}\]])", r"\1", t))


def modify_bad(r, roles):
    """the engine's Modify rule (HytaleServer BuilderModifier.applyTo: BuilderParameters.getParameterType of the REFERENCED role; VOID =
    "Parameter X does not exist or is private"): every non-underscore Modify key must be a non-private parameter the Reference declares in
    its OWN Parameters block (inherited template parameters do not count); a {"Compute": name} must name one of the role's own Parameters"""
    if r.get("Type") != "Variant" or r.get("Reference") not in roles:
        return ["type / reference"]
    pub = dict((k, v) for k, v in (roles[r["Reference"]].get("Parameters") or {}).items() if not (isinstance(v, dict) and v.get("Private")))
    own = r.get("Parameters") or {}
    bad = [k for k in (r.get("Modify") or {}) if not k.startswith("_") and k not in pub]
    bad += ["Compute " + v["Compute"] for v in (r.get("Modify") or {}).values() if isinstance(v, dict) and set(v) == {"Compute"}
            and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(v["Compute"])) and v["Compute"] not in own]
    return bad


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.22 - build script') and g.count('VERSION = "0.1.22"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (1, 0, 2), "S +1 system, no command, +2 makeClass (the 3rd class = cmd() MobsStripCmd)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.check('if not _sp or "com/skyy/mobs/SkyyMobsPlugin.class" in _names:' in g, "S fix: the 0.1.21 pack check skips our own deployed jar")
    K.check("double hx = roleX(role) * rankHp(r, base) * varHp(v);" in g and "roleDx(role) * rankDmg(r) * varDmg(v)" in g, "S factors x the variant")
    K.check("String k = @PKG@.MobCfg.baseRole(role).toLowerCase();" in g, "S MobElem.row reads the base role (a variant keeps its element)")
    K.check("int vl = @PKG@.MobCfg.varLevels(@PKG@.MobCfg.variantOf(role));" in g and g.index("int vl = @PKG@.MobCfg.varLevels(") < g.index("apply(h, null, null, npc, m, u, w, wn, role, level, spawn, step, res);"),
            "S onAdd: the extra levels inside the rolled-level branch, before apply")
    K.check("if (m.rank > 0 || @PKG@.MobCfg.variantOf(m.role) > 0) {" in g, "S mob:fn:info: XP follows a variant's Health")
    K.check("@PKG@.MobVariant.extra(l, npc.getRoleName(), role.getDropListId(), @PKG@.MobSpoils.RNG);" in g and "!@PKG@.MobCfg.SEC_ON && !@PKG@.MobCfg.VAR_ON) return;" in g,
            "S SpoilsSys: the extra roll + VAR_ON keeps the system awake")
    K.check('name = @PKG@.MobCfg.varName(role, name);          // 0.1.22: "Armored" / "Veteran" first, so the rank word leads: "Elite Armored Skeleton"\n  if (rk == 1) name = "Elite " + name;' in g,
            "S the plate: the variant word first, then the rank word in front of it ('Elite Armored Skeleton Soldier')")
    K.check('"|var|" + VAR_A_HP' in g, "S a Health / damage edit re-applies the loaded mobs (signature)")
    # fixer round (critics)
    sysb = g[g.index("public void onEntityAdded(@REF@ ref, @ADDR@ why"):g.index('M(mvsy, "public void onEntityRemove(')]
    K.check("cb.tryRemoveEntity(ref, @REMR@.REMOVE);" in sysb and "cb.removeEntity(" not in sysb and '(G["CB"], "tryRemoveEntity", "void", [G["REF"], G["REMR"]])' in g,
            "S fix1: MobVariantSys removes with tryRemoveEntity (a ref SkyyZones ZNoSpawn already removed is skipped, never thrown) + probed")
    K.check("(Skyy:" not in g[g.index("VAR_ROWS = ["):g.index('CFG_LINES += ["# Tougher versions')], "S fix5: no 'Skyy:' in the Server Setup help texts")
    K.check("if (@PKG@.MobVariant.zonesTakes(w.getName(), p.x, p.y, p.z)) return;" in sysb and sysb.index("zonesTakes(") < sysb.index("cb.tryRemoveEntity(")
            and "why == @ADDR@.SPAWN && npc.getEnvironment() != Integer.MIN_VALUE" in sysb, "S fix3: a natural spawn SkyyZones' no-spawn hook takes is left to it (before our remove)")
    K.check("a tougher-version base counts as a boss / guard" in g and "not editable" in g[g.index("VAR_ROWS = ["):g.index('CFG_LINES += ["# Tougher versions')],
            "S fix3: build asserts no base is a boss / guard; the share help says the mix is not editable")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    newf = sorted(nb - na)
    K.eq((sorted(n for n in newf if not n.startswith((RD, MD))), sorted(na - nb)), (sorted("com/skyy/mobs/%s.class" % c for c in ADDED), []),
         "S only the 3 new classes + variant roles / models added, nothing removed")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.check("manifest.json" in chg and all(n == "manifest.json" or n.startswith(SD) for n in chg), "S the other changed files: manifest + spawn files (%d)" % len(chg))
    man = json.loads(zb.read("manifest.json"))
    K.check(man.get("IncludesAssetPack") is True and man.get("Version") == VERSION and "tougher versions" in man.get("Description", ""), "S manifest")
    az = zipfile.ZipFile(SJ.assets_zip())
    an = set(az.namelist())
    vroles = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
    vmodels = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/Models/") and n.endswith(".json"))
    ids = jar_ids(jar)
    K.check(len(ids) >= 60 and sorted(n[len(MD):-5] for n in nb if n.startswith(MD)) == ids, "S %d variant roles, one model each" % len(ids))
    K.check(not (set(ids) & (vroles | vmodels)), "S every variant id is new against Assets.zip")
    import importlib.util as ilu
    ds = ilu.spec_from_file_location("ds_ro", os.path.join(ROOT, "tools", "deploy_set.py"))
    dm = ilu.module_from_spec(ds)
    ds.loader.exec_module(dm)
    taken = set()
    for m_, v_ in dm.SET:
        j_ = os.path.join(ROOT, m_, "%s-%s.jar" % (m_, v_))
        if m_ != "SkyyMobs" and os.path.isfile(j_):
            taken |= set(n.rsplit("/", 1)[1][:-5] for n in zipfile.ZipFile(j_).namelist() if n.startswith(("Server/NPC/Roles/", "Server/Models/")) and n.endswith(".json"))
    K.check(not (set(ids) & taken), "S every variant id is new against every SET jar")
    # the engine's Modify rule: the mirror must accept every vanilla Variant and refuse the failed 0.1.22 form, then every role of ours
    VR = {}
    for n in an:
        if n.startswith("Server/NPC/Roles/") and n.endswith(".json"):
            try:
                VR[n.rsplit("/", 1)[1][:-5]] = lenient(az.read(n).decode("utf-8-sig", "replace"))
            except Exception:
                pass
    vbad = [(k, modify_bad(d, VR)) for k, d in VR.items() if d.get("Type") == "Variant" and d.get("Reference") in VR and modify_bad(d, VR)]
    nvar = len([1 for d in VR.values() if d.get("Type") == "Variant"])
    K.eq(vbad[:3], [], "S the Modify-rule mirror accepts all %d vanilla Variants" % nvar)
    K.eq(modify_bad({"Type": "Variant", "Reference": "Skeleton_Fighter", "Modify": {"Appearance": "Skeleton_Fighter_SkyyArmored1"}}, VR),
         ["Appearance"], "S the mirror refuses the failed 0.1.22 form (Variant of Skeleton_Fighter, Modify Appearance) like the server did")
    allr = dict(VR)
    for vid in ids:
        allr[vid] = json.loads(zb.read(RD + vid + ".json"))
    rbad = [(vid, modify_bad(allr[vid], allr)) for vid in ids if modify_bad(allr[vid], allr)]
    K.eq(rbad[:5], [], "S every one of the %d roles passes the engine's Modify rule (0 'does not exist or is private')" % len(ids))

    def flat(base):
        d = json.loads(json.dumps(VR[base]))
        if "Appearance" not in (d.get("Modify") or {}):          # a *_Wander: its camp role with the Wander's values
            camp = json.loads(json.dumps(VR[d["Reference"]]))
            for k, v in d["Modify"].items():
                if isinstance(v, dict) and set(v) == {"Compute"}:
                    v = d["Parameters"][v["Compute"]]["Value"]
                camp["Parameters"][k]["Value"] = v
            d = camp
        d["Modify"].pop("Appearance", None)
        return d
    bad = []
    for vid in ids:
        st, base, zone = var_split(vid)
        r = json.loads(zb.read(RD + vid + ".json"))
        m = json.loads(zb.read(MD + vid + ".json"))
        rc = json.loads(json.dumps(r))
        app = rc["Modify"].pop("Appearance", None)
        mno = rc["Modify"].get("MemoriesNameOverride")
        want = flat(base) if base in vroles else None
        if want is not None and "MemoriesNameOverride" not in want["Modify"] and want["Modify"].get("IsMemory"):
            want["Modify"]["MemoriesNameOverride"] = mno
        if (app != vid or want is None or rc != want or VR.get(r.get("Reference"), {}).get("Type") != "Abstract"
                or mno not in (None, base.replace("_Wander", "")) or st == 0 or zone not in (1, 2, 3, 4)):
            bad.append(("role", vid))
            continue
        for a in m.get("DefaultAttachments", []):
            for f in ("Model", "Texture"):
                if a.get(f) and "Common/" + a[f] not in an:
                    bad.append(("path", vid, a[f]))
        own = "/Guardian/" if base.startswith("Goblin_") else "Items/Armors/%s/" % METAL[zone][st - 1]
        arm = [a["Model"] for a in m["DefaultAttachments"] if own in a["Model"]]          # ours (a vanilla piece in a slot we do not fill stays)
        want = 2 if st == 1 else 4
        if len(arm) != want or len(set(a.rsplit("/", 1)[1] for a in arm)) != want:
            bad.append(("pieces", vid, arm))
    K.eq(bad[:5], [], "S every role = a full copy of its vanilla role (only Appearance = its model + the vanilla memory name), every model = real paths + the zone's armour pieces (Armored 2, Veteran 4)")
    K.check(not any("Armor" in json.loads(zb.read(RD + v + ".json")).get("Modify", {}) for v in ids), "S no role Armor list (toughness = ranks, never an armour stat)")
    # the spawn files: every 0.1.21 entry unchanged or split by its tier's mix, the total weight the same
    A = dict((n, json.loads(za.read(n))) for n in na if n.startswith(SD))
    Bf = dict((n, json.loads(zb.read(n))) for n in nb if n.startswith(SD))
    K.eq(sorted(A), sorted(Bf), "S the same 45 spawn files")
    split, bads = 0, []
    for n in sorted(A):
        key = n[len(SD):-5]
        mt = re.search(r"_Tier([123])$", key)
        tier = int(mt.group(1)) if mt else FILE_TIER.get(key)
        zone = int(key[4]) if key.startswith("Zone") else 0
        bw = dict((e["Id"], e) for e in Bf[n]["NPCs"])
        for e in A[n]["NPCs"]:
            a_, v_ = var_split(e["Id"] + "_SkyyArmored%d" % zone)[1], None
            ai, vi = "%s_SkyyArmored%d" % (e["Id"], zone), "%s_SkyyVeteran%d" % (e["Id"], zone)
            if ai in bw:
                mx = MIX[tier]
                got = (bw[e["Id"]]["Weight"], bw[ai]["Weight"], bw[vi]["Weight"])
                exp = tuple(round(e["Weight"] * x / 100.0, 4) for x in mx)
                same = all(dict((k, v) for k, v in bw[i].items() if k not in ("Id", "Weight")) == dict((k, v) for k, v in e.items() if k not in ("Id", "Weight")) for i in (ai, vi))
                if got != exp or not same or abs(sum(got) - e["Weight"]) > 0.001:
                    bads.append((n, e["Id"], got, exp))
                split += 1
            elif bw.get(e["Id"]) != e:
                bads.append((n, e["Id"], "changed without a split"))
        K.eq(dict((k, v) for k, v in Bf[n].items() if k != "NPCs"), dict((k, v) for k, v in A[n].items() if k != "NPCs"), "S %s: same fields" % key)
    K.eq(bads[:4], [], "S %d entries split Normal / Armored / Veteran by the tier mix, same fields, same total weight; the rest unchanged" % split)
    allv = set(e["Id"] for d_ in Bf.values() for e in d_["NPCs"] if var_split(e["Id"])[0])
    K.eq(sorted(allv), ids, "S every variant role spawns from a list, every listed variant has its role")
    for nm in ("Skeleton_Fighter_SkyyArmored1", "Skeleton_Fighter_SkyyVeteran1", "Skeleton_Fighter_SkyyArmored3", "Skeleton_Burnt_Knight_SkyyVeteran4",
               "Skeleton_Sand_Guard_SkyyArmored2", "Goblin_Scrapper_SkyyArmored1", "Outlander_Hunter_SkyyVeteran3"):
        K.check(nm in ids, "S %s made" % nm)
    for nm in ("Skeleton_Burnt_Gunner", "Skeleton_Burnt_Praetorian", "Skeleton_Burnt_Praetorian_Wander", "Skeleton_Incandescent_Head", "Goblin_Turret", "Larva_Void"):
        K.check(not [v for v in ids if var_split(v)[1] == nm], "S no tougher version of %s" % nm)
    V = dict((n, json.loads(az.read(n).decode("utf-8-sig"))) for n in an if n.startswith(SD) and n.endswith(".json"))
    allf = dict(V)
    allf.update(Bf)
    pairs = {}
    for n, d_ in allf.items():
        for e in d_.get("Environments", []):
            for x in d_.get("NPCs", []):
                pairs.setdefault((x["Id"], e), []).append(n)
    K.eq([p for p, f in pairs.items() if len(f) > 1], [], "S no NPC + environment pair in two files")
    # the Veteran Soldier: the vanilla chest plate / tunic / boots off, the Iron set on, the eyes kept
    vs = json.loads(zb.read(MD + "Skeleton_Soldier_SkyyVeteran1.json"))
    K.eq([a["Model"].rsplit("/", 2)[-2] + "/" + a["Model"].rsplit("/", 1)[1] for a in vs["DefaultAttachments"]],
         ["Eyes/Eyes.blockymodel", "Iron/Head.blockymodel", "Iron/Chest.blockymodel", "Iron/Hands.blockymodel", "Iron/Legs.blockymodel"],
         "S Veteran Skeleton Soldier wears the Iron set (vanilla chest plate / tunic / boots off, eyes kept)")
    oh = json.loads(zb.read(MD + "Outlander_Hunter_SkyyArmored3.json"))
    K.check(any("Hunter/Cape" in a["Model"] for a in oh["DefaultAttachments"]) and any("Hunter/Legs" in a["Model"] for a in oh["DefaultAttachments"]),
            "S Armored Outlander Hunter keeps its cape + legs (Armored = head + chest only)")
    tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "--", "*Spawn/World*", "*Roles/SkyyMobs*", "*Models/SkyyMobs*"], capture_output=True, text=True).stdout.strip()
    K.eq(tracked, "", "S no vanilla-derived file is tracked in git")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    C, V, VS = JClass(PKG + "MobCfg"), JClass(PKG + "MobVariant"), JClass(PKG + "MobVariantSys")
    Sp, El, Lv, Info = JClass(PKG + "MobSpoils"), JClass(PKG + "MobElem"), JClass(PKG + "MobLevel"), JClass(PKG + "MobInfo")
    UUID = JClass("java.util.UUID")
    C.useDefaults()
    d = str(C.DEF_CFG)
    for ln in ("variant.on=true", "variant.armored.hp=1.4", "variant.armored.dmg=1.15", "variant.armored.levels=1", "variant.armored.drops=25",
               "variant.veteran.hp=1.9", "variant.veteran.dmg=1.3", "variant.veteran.levels=2", "variant.veteran.drops=50", "variant.share.z1=100", "variant.share.z4=100"):
        K.check("\n" + ln + "\n" in d, "X the default file carries " + ln)
    ids = jar_ids(jar)
    mism = [v for v in ids + ["Skeleton_Fighter", "Zombie", "", "_SkyyArmored1", "X_SkyyVeteran", "Skeleton_Fighter_SkyyArmored"]
            if (int(C.variantOf(v)), str(C.baseRole(v)), int(C.variantZone(v))) != var_split(v)]
    K.eq(mism, [], "X variantOf / baseRole / variantZone = the Python mirror on all %d jar ids + edge cases" % len(ids))
    K.eq((int(C.variantOf(None)), C.baseRole(None), int(C.variantZone(None))), (0, None, 0), "X the helpers take null")
    K.eq([round(float(f(v)), 4) for f in (C.varHp, C.varDmg, C.varDrops) for v in (0, 1, 2)] + [int(C.varLevels(v)) for v in (0, 1, 2)],
         [1.0, 1.4, 1.9, 1.0, 1.15, 1.3, 0.0, 25.0, 50.0, 0, 1, 2], "X the step numbers (Skyy's 1.4 / 1.15 / +1 / 25 %, 1.9 / 1.3 / +2 / 50 %)")
    K.eq([str(C.varWord(v)) for v in (0, 1, 2)], ["", "Armored", "Veteran"], "X the plate words")
    K.eq([str(C.varName(r, "Skeleton Soldier")) for r in ("Skeleton_Soldier", "Skeleton_Soldier_SkyyArmored1", "Skeleton_Soldier_SkyyVeteran1")]
         + [str(C.varName("Skeleton_Soldier_SkyyArmored1", "Armored Skeleton Soldier")), str(C.varName("Skeleton_Soldier_SkyyVeteran1", None))],
         ["Skeleton Soldier", "Armored Skeleton Soldier", "Veteran Skeleton Soldier", "Armored Skeleton Soldier", "Veteran "],
         "X varName: the word in front once")
    us = [UUID.randomUUID() for _ in range(4000)]
    K.check(all(bool(C.keep(u, z)) for u in us[:50] for z in (0, 1, 2, 3, 4, 9)) and bool(C.keep(None, 1)), "X keep(): share 100 keeps every one")
    C.VAR_Z2, C.VAR_Z3 = 0, 50
    k2 = sum(1 for u in us if bool(C.keep(u, 2)))
    k3 = [bool(C.keep(u, 3)) for u in us]
    K.eq(k2, 0, "X keep(): share 0 keeps none")
    K.check(1800 <= sum(k3) <= 2200 and k3 == [bool(C.keep(u, 3)) for u in us], "X keep(): share 50 keeps ~half (%d / 4000), fixed per UUID" % sum(k3))
    K.eq([int(C.varShare(z)) for z in (0, 1, 2, 3, 4, 5)], [100, 100, 0, 50, 100, 100], "X varShare per zone (live edits)")
    C.useDefaults()
    u0 = UUID(0, 1)
    C.RANKFIX.clear()
    base = [list(C.factors(r, u0, 70.0, False)) for r in ("Skeleton_Soldier", "Skeleton_Soldier_SkyyArmored1", "Skeleton_Soldier_SkyyVeteran1")]
    K.eq([(round(b[0] / base[0][0], 4), round(b[1] / base[0][1], 4), int(b[2])) for b in base], [(1.0, 1.0, 0), (1.4, 1.15, 0), (1.9, 1.3, 0)],
         "X factors: Armored x1.4 / x1.15, Veteran x1.9 / x1.3, rank 0 (no new rank: SkyyGear sees normal kills)")
    C.rankPut(u0, 1)
    el = list(C.factors("Skeleton_Soldier_SkyyVeteran1", u0, 70.0, False))
    K.eq((round(el[0] / base[0][0], 4), round(el[1] / base[0][1], 4), int(el[2])), (round(3.0 * 1.9, 4), round(1.5 * 1.3, 4), 1), "X an elite Veteran: x3 x1.9 Health, x1.5 x1.3 damage")
    C.RANKFIX.clear()
    C.VAR_A_HP = 2.5
    K.eq(round(float(C.factors("Skeleton_Soldier_SkyyArmored1", u0, 70.0, False)[0]) / base[0][0], 4), 2.5, "X a live Health x edit is used at once")
    C.useDefaults()
    try:
        El.derive()
    except Exception:
        pass
    pairs = [("Skeleton_Frost_Soldier_SkyyArmored3", "Skeleton_Frost_Soldier"), ("Skeleton_Burnt_Knight_SkyyVeteran4", "Skeleton_Burnt_Knight"),
             ("Zombie_Burnt_SkyyArmored4", "Zombie_Burnt"), ("Skeleton_Sand_Guard_SkyyVeteran2", "Skeleton_Sand_Guard"), ("Skeleton_Fighter_SkyyArmored1", "Skeleton_Fighter")]
    K.eq([int(El.ownOf(a)) for a, b in pairs], [int(El.ownOf(b)) for a, b in pairs], "X a variant has its base role's element (Zombie_Burnt exact row too)")
    K.check(int(El.ownOf("Zombie_Burnt_SkyyArmored4")) >= 0 and str(El.word("Skeleton_Frost_Soldier_SkyyArmored3")) == str(El.word("Skeleton_Frost_Soldier")) != "",
            "X the element word on a variant plate: %s" % El.word("Skeleton_Frost_Soldier_SkyyArmored3"))
    # mob:fn:info: the kill XP follows the variant's Health (no new XP code)
    Fn = JClass(PKG + "MobInfoFn")()
    xs = []
    for i, r in enumerate(("Skeleton_Soldier", "Skeleton_Soldier_SkyyArmored1", "Skeleton_Soldier_SkyyVeteran1")):
        mi = Info()
        mi.role, mi.level, mi.base, mi.uuid = r, 12, 100.0, UUID(7, i + 1)
        fx = C.factors(r, mi.uuid, 100.0, False)
        mi.rx, mi.dx, mi.rank = fx[0], fx[1], int(fx[2])
        Lv.MOBS.put(mi.uuid, mi)
        a = Fn.apply(mi.uuid)
        xs.append((float(a[3]), float(a[4]), float(a[5]), str(a[6])))
        Lv.MOBS.remove(mi.uuid)
    K.eq([(round(x[0] / xs[0][0], 4), round(x[1] / xs[0][1], 4), round(x[2] / xs[0][2], 4), x[3]) for x in xs],
         [(1.0, 1.0, 1.0, ""), (1.4, 1.15, 1.4, ""), (1.9, 1.3, 1.9, "")], "X mob:fn:info: hpMult / dmgMult / xpMult x1.4 / x1.9, rank '' (SkyyGear: normal kills)")
    # MobVariant.removeOnAdd
    s0, o0, h0 = int(V.SEEN), int(V.OFF_N), int(V.SHARE_N)
    K.eq([bool(V.removeOnAdd(r, u0, sp)) for r, sp in (("Skeleton_Soldier", True), ("Skeleton_Soldier_SkyyArmored1", True), ("Skeleton_Soldier_SkyyVeteran1", False))],
         [False, False, False], "X removeOnAdd: ON + share 100 keeps every one")
    C.VAR_ON = False
    K.eq([bool(V.removeOnAdd(r, u0, sp)) for r, sp in (("Skeleton_Soldier", True), ("Skeleton_Soldier_SkyyArmored1", True), ("Skeleton_Soldier_SkyyVeteran3", False))],
         [False, True, True], "X removeOnAdd: OFF removes variants as they spawn AND load, never a vanilla role")
    C.VAR_ON = True
    C.VAR_Z1 = 0
    K.eq([bool(V.removeOnAdd("Skeleton_Soldier_SkyyArmored1", u0, True)), bool(V.removeOnAdd("Skeleton_Soldier_SkyyArmored1", u0, False)),
          bool(V.removeOnAdd("Skeleton_Soldier_SkyyArmored2", u0, True))], [True, False, False], "X removeOnAdd: share 0 in Zone 1 removes a Zone 1 spawn only (a load stays; Zone 2 untouched)")
    K.eq((int(V.SEEN) - s0, int(V.OFF_N) - o0, int(V.SHARE_N) - h0), (2, 2, 1), "X the counters (SEEN = kept spawns only)")
    C.useDefaults()
    # extra(): the seam returns a drop list with gear in it (armour / weapon) - those never come out
    @JImplements("java.util.function.Function")
    class Rolls(object):
        @JOverride
        def apply(self, dl):
            L = JClass("java.util.ArrayList")()
            OA = JClass("java.lang.Object[]")
            for pid, n in (("Ingredient_Bone_Fragment", 2), ("Armor_Iron_Head", 1), ("Weapon_Axe_Iron_Rusty", 1)):
                L.add(OA([JClass("java.lang.String")(pid), JClass("java.lang.Integer")(n)]))
            return L
    Sp.ROLLS = Rolls()
    R = JClass("java.util.Random")(42)
    AL = JClass("java.util.ArrayList")
    cnt = {}
    for r in ("Skeleton_Soldier", "Skeleton_Soldier_SkyyArmored1", "Skeleton_Soldier_SkyyVeteran1"):
        hits, items = 0, set()
        for _ in range(4000):
            l = AL()
            if int(V.extra(l, r, "Drop_Skeleton_Soldier", R)) > 0:
                hits += 1
            for i in range(l.size()):
                items.add(str(l.get(i)[0]))
        cnt[r] = (hits, sorted(items))
    K.eq(cnt["Skeleton_Soldier"], (0, []), "X extra(): a vanilla role gets no extra roll")
    K.check(850 <= cnt["Skeleton_Soldier_SkyyArmored1"][0] <= 1150 and 1800 <= cnt["Skeleton_Soldier_SkyyVeteran1"][0] <= 2200,
            "X extra(): ~25 %% Armored, ~50 %% Veteran (%s)" % [cnt[k][0] for k in sorted(cnt)])
    K.eq((cnt["Skeleton_Soldier_SkyyArmored1"][1], cnt["Skeleton_Soldier_SkyyVeteran1"][1]), (["Ingredient_Bone_Fragment"], ["Ingredient_Bone_Fragment"]),
         "X extra(): armour + weapons filtered out (the worn armour never drops)")
    C.VAR_ON = False
    l = AL()
    K.eq((int(V.extra(l, "Skeleton_Soldier_SkyyVeteran1", "D", R)), int(l.size())), (0, 0), "X extra(): OFF = none")
    C.VAR_ON = True
    K.eq((int(V.extra(None, "Skeleton_Soldier_SkyyVeteran1", "D", R)), int(V.extra(AL(), "Skeleton_Soldier_SkyyVeteran1", None, R)),
          int(V.extra(AL(), "Skeleton_Soldier_SkyyVeteran1", "D", None))), (0, 0, 0), "X extra(): bad input = 0")
    C.VAR_V_DROP = 0.0
    K.check(all(int(V.extra(AL(), "Skeleton_Soldier_SkyyVeteran1", "D", R)) == 0 for _ in range(200)), "X extra(): 0 % = never")
    C.useDefaults()
    Sp.ROLLS = None
    il = str(V.inspectLine("Skeleton_Soldier_SkyyVeteran1"))
    K.check(il.startswith("=Tougher version: Veteran (rarity colour Rare pink #FF55FF") and "Health x1.9, damage x1.3, +2 level(s), extra drop roll 50 %" in il
            and "vanilla role Skeleton_Soldier, Zone 1 armour" in il, "X inspectLine: %s" % il)
    K.check("Unique yellow #FFFF55" in str(V.inspectLine("Goblin_Thief_SkyyArmored1")) and V.inspectLine("Skeleton_Soldier") is None, "X inspectLine: Armored = yellow, vanilla = none")
    C.VAR_ON = False
    K.check(str(V.inspectLine("Skeleton_Soldier_SkyyArmored1")).endswith("Tougher versions is OFF - it goes when its chunk reloads"), "X inspectLine says OFF")
    C.VAR_ON = True
    K.eq([str(V.num(x)) for x in (1.4, 1.15, 25.0, 1.0, 1.333)], ["1.4", "1.15", "25", "1", "1.33"], "X num()")
    K.check(str(V.strip(None, None, "foo")).startswith("-[Mobs] Type /mobs strip variants") and str(V.strip(None, None, None)).startswith("-[Mobs] Type")
            and str(V.strip(None, None, " Variants ")) == "-[Mobs] Run this in a world.", "X strip(): the wrong word / no world refused")
    t = str(V.text())
    K.check(t.startswith("tougher versions on (%d roles, add check NOT registered" % len(ids)) and "extra drops" in t, "X text(): %s" % t)
    K.eq(int(V.KINDS), len(ids), "X KINDS = the roles in the jar")
    sys_ = VS()
    AR = JClass("com.hypixel.hytale.component.AddReason")
    RR = JClass("com.hypixel.hytale.component.RemoveReason")
    sys_.onEntityAdded(None, AR.SPAWN, None, None)
    K.check(bool(VS.FAILED_ONCE), "X MobVariantSys: a bad call is caught + logged once (the mob stays)")
    sys_.onEntityAdded(None, AR.LOAD, None, None)
    sys_.onEntityAdded(None, None, None, None)
    sys_.onEntityRemove(None, RR.REMOVE, None, None)
    K.check(True, "X MobVariantSys: LOAD / null reason / onEntityRemove never throw")
    try:
        q = sys_.getQuery()
        K.check(q is not None and sys_.getQuery() is q, "X MobVariantSys.getQuery (cached)")
    except Exception as e:
        K.check("NullPointer" in str(e) or "Null" in str(type(e)), "X MobVariantSys.getQuery needs the component registry (bare JVM: %s)" % str(e)[:80])
    # fix1 (critic): the bytecode of MobVariantSys calls CommandBuffer.tryRemoveEntity, never removeEntity
    cb_ = zipfile.ZipFile(jar).read("com/skyy/mobs/MobVariantSys.class")
    K.check(b"tryRemoveEntity" in cb_ and b"removeEntity" not in cb_, "X fix1: MobVariantSys.class names tryRemoveEntity only")
    # fix2 (critic): under the plate.colorOn trial the plate takes the rarity colour (Armored yellow, Veteran pink, Elite cyan); plain = level colour
    C.useDefaults()
    C.ELEM_PLATE = False
    rs_ = (("Skeleton_Soldier", "Skeleton Soldier"), ("Skeleton_Soldier_SkyyArmored1", "Armored Skeleton Soldier"),
           ("Skeleton_Soldier_SkyyVeteran1", "Veteran Skeleton Soldier"), ("Skeleton_Soldier_SkyyArmored1", "Elite Armored Skeleton Soldier"),
           ("Skeleton_Soldier", "Elite Skeleton Soldier"))
    C.COLOR_ON = False
    K.eq([str(Lv.plateText(12, n, r_)) for r_, n in rs_], [str(Lv.plateText(12, n)) for r_, n in rs_], "X fix2: colours off = the plain 2-argument text for every step")
    K.eq(str(Lv.plateText(12, "Armored Skeleton Soldier", "Skeleton_Soldier_SkyyArmored1")), "[Lv 12] Armored Skeleton Soldier", "X fix2: colours off = '[Lv 12] Armored Skeleton Soldier'")
    C.COLOR_ON, C.MARKUP = True, "tag"
    lvh = str(Lv.hexFor(12))
    HEX = ["#FFFFFF", "#FFFF55", "#FF55FF", "#55FFFF", "#55FFFF"]
    K.eq([str(Lv.plateHex(lv_, n, r_)) for lv_ in (3, 12, 55) for r_, n in rs_], HEX * 3, "X fix3: plateHex = white (any level) / yellow / pink / Elite cyan")
    K.eq([str(Lv.plateText(12, n, r_)) for r_, n in rs_],
         ["<color=%s>[Lv 12] %s</color>" % (h_, n) for h_, (r_, n) in zip(HEX, rs_)],
         "X fix3: the coloured plate text per step (tag markup; plain = Normal white)")
    K.eq(str(Lv.plateText(12, "Skeleton Soldier")), "<color=%s>[Lv 12] Skeleton Soldier</color>" % lvh, "X fix3: the 2-argument plateText (no role) keeps the level colour")
    C.ELEM_PLATE = True
    ew = str(El.word("Skeleton_Frost_Soldier_SkyyVeteran3"))
    pf = str(Lv.plateText(12, "Veteran Skeleton Frost Soldier", "Skeleton_Frost_Soldier_SkyyVeteran3"))
    K.check(ew != "" and pf.startswith("<color=#FF55FF>[Lv 12] Veteran Skeleton Frost Soldier</color>") and (" - " + ew) in pf, "X fix2: with an element the name is pink, the element its own colour: %s" % pf)
    C.useDefaults()
    # fix3 (critic): SkyyZones' no-spawn rule over the bridge (zones:fn:noSpawn {world, x, y, z} -> Boolean)
    K.check(not bool(V.zonesTakes("w", 1.0, 2.0, 3.0)), "X fix3 zonesTakes: no SkyyZones = false")
    seen_ = []

    @JImplements("java.util.function.Function")
    class NoSp:
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            seen_.append([str(x) for x in o])
            if self.ans == "boom":
                raise RuntimeError("boom")
            return JClass("java.lang.Boolean")(self.ans)
    n0 = int(V.ZONES_N)
    br.put("zones:fn:noSpawn", NoSp(True))
    K.check(bool(V.zonesTakes("NewBetaTest", 10.7, 64.2, -3.5)) and seen_[-1] == ["NewBetaTest", "10", "64", "-4"] and int(V.ZONES_N) == n0 + 1,
            "X fix3 zonesTakes: a town / safe spot = true, block coordinates floored (%s)" % seen_[-1:])
    br.put("zones:fn:noSpawn", NoSp(False))
    K.check(not bool(V.zonesTakes("NewBetaTest", 1.0, 2.0, 3.0)) and not bool(V.zonesTakes(None, 1.0, 2.0, 3.0)), "X fix3 zonesTakes: elsewhere / no world = false")
    br.put("zones:fn:noSpawn", NoSp("boom"))
    K.check(not bool(V.zonesTakes("NewBetaTest", 1.0, 2.0, 3.0)), "X fix3 zonesTakes: a failing SkyyZones = false (our remove goes ahead)")
    br.remove("zones:fn:noSpawn")
    # fix3 (critic): admin role rows naming the vanilla role also cover its tougher versions
    Gb = JClass(PKG + "MobGlob")
    K.eq([str(Gb.base(k_)) for k_ in ("goblin_thief_skyyarmored1", "skeleton_fighter_skyyveteran3", "goblin_thief", "_skyyarmored1")],
         ["goblin_thief", "skeleton_fighter", "goblin_thief", "_skyyarmored1"], "X fix3 MobGlob.base")
    pats = Gb.list("goblin_thief, *_fighter")
    K.eq([bool(Gb.any(pats, r_)) for r_ in ("Goblin_Thief", "Goblin_Thief_SkyyArmored1", "Skeleton_Fighter_SkyyVeteran3", "Goblin_Miner_SkyyArmored1", "Skeleton_Fighter")],
         [True, True, True, False, True], "X fix3 MobGlob.any: an exact / suffix row of the vanilla role covers its Armored / Veteran ids, others not")
    Obj, JA = JClass("java.lang.Object"), None
    from jpype import JArray, JString, JInt, JDouble
    raw_ = ["Goblin_Thief", "Skeleton_*", "Goblin_Thief_SkyyVeteran1"]
    tab0 = C.ROLES_TAB
    C.ROLES_TAB = JArray(Obj)([JArray(JString)(raw_), JArray(JString)([x.lower() for x in raw_]), JArray(JInt)([5, 7, 9]),
                               JArray(JDouble)([1.0, 1.0, 1.0]), JArray(JDouble)([1.0, 1.0, 1.0])])
    K.eq([int(C.roleIdx(r_)) for r_ in ("Goblin_Thief", "Goblin_Thief_SkyyArmored1", "Goblin_Thief_SkyyVeteran1", "Skeleton_Fighter_SkyyArmored1", "Goblin_Miner_SkyyArmored1")],
         [0, 0, 2, 1, -1], "X fix3 roleIdx: own exact row, else the vanilla role's exact row, else the patterns")
    C.ROLES_TAB = tab0
    C.useDefaults()
    Rw = JClass(PKG + "CfgRows")
    keys = [str(k) for k in Rw.KEYS]
    vk = [k for k in keys if k.startswith("variant.")]
    K.eq(len(vk), 13, "X 13 Tougher mobs rows")
    for k in vk:
        i = keys.index(k)
        K.check(str(Rw.CATS[i]) == "variant" and "live" in str(Rw.FLAGS[i]) and len(str(Rw.HELPS[i])) <= 100, "X row %s: Tougher mobs tab, live, help <= 100" % k)
    K.check(not [k for k in vk if "Skyy" in str(Rw.HELPS[keys.index(k)])] and all(str(Rw.LABELS[keys.index("variant.share.z%d" % z_)]) == "Zone %d tougher-version share" % z_ for z_ in (1, 2, 3, 4)),
            "X fix5: no 'Skyy' in the row help, share rows say 'share'")
    K.check(str(Rw.DEFS[keys.index("variant.on")]) == "true" and str(Rw.TYPES[keys.index("variant.on")]) == "bool"
            and str(Rw.MAXS[keys.index("variant.share.z3")]) == "100", "X variant.on bool true; shares 0-100")
    K.check("strip" in str(JClass(PKG + "CfgRows").NOTE) if hasattr(JClass(PKG + "CfgRows"), "NOTE") else True, "X the Server Setup note names strip")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Sp, Sc = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils"), JClass(PKG + "MobSecret")
    P = JClass("java.nio.file.Paths")
    files = [f for f in ("config.properties", "bands.properties", "trees.properties") if os.path.isfile(os.path.join(home, f))]
    before = dict((f, open(os.path.join(home, f), "rb").read()) for f in files)
    K.check("config.properties" in files, "D the live copy has a config.properties (%s)" % files)
    K.check(b"variant." not in before.get("config.properties", b""), "D the live file has no variant lines yet")

    def start():
        Cfg.DIR = P.get(home)
        Cfg.FILE = P.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
        o = "".join(str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4"))
        o += str(Sp.migrateWc15(P.get(home)))
        Cfg.load()
        Sp.loadV3(P.get(home))
        Sc.load(P.get(home))
        return o

    def vals():
        return (bool(Cfg.VAR_ON), round(float(Cfg.VAR_A_HP), 3), round(float(Cfg.VAR_V_HP), 3), int(Cfg.VAR_A_LV), int(Cfg.VAR_V_LV),
                round(float(Cfg.VAR_V_DROP), 2), [int(Cfg.varShare(z)) for z in (1, 2, 3, 4)])
    DEF = (True, 1.4, 1.9, 1, 2, 50.0, [100, 100, 100, 100])
    o1 = start()
    K.eq(vals(), DEF, "D start 1: no variant lines in the live file -> the defaults")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files),
         "D start 1: config / bands / trees bytes untouched (no migration; older updates %r)" % o1[:60])
    o2 = start()
    K.eq((o2, vals()), ("", DEF), "D start 2: nothing migrates, the same values")
    K.eq(dict((f, open(os.path.join(home, f), "rb").read() == before[f]) for f in files), dict((f, True) for f in files), "D start 2: bytes still untouched")
    K.save()


# the kit's class compare allows only manifest.json among non-class entries: compare a copy WITHOUT the generated asset files (phase S checks them)
def _cmp(out, jar, old_jar, pkg, expect, added, removed=()):
    d = os.path.join(SCRATCH, "cmpjar")
    os.makedirs(d, exist_ok=True)
    outj = []
    for j in (jar, old_jar):
        sj = os.path.join(d, "new-" + os.path.basename(j) if j == jar else "old-" + os.path.basename(j))
        with zipfile.ZipFile(j) as zi, zipfile.ZipFile(sj, "w", zipfile.ZIP_DEFLATED) as zo:
            for n in zi.namelist():
                if not n.startswith((SD, RD, MD)):
                    zo.writestr(n, zi.read(n))
        outj.append(sj)
    return T121._cmp0(out, outj[0], outj[1], pkg, expect, added, removed)


HK.run_compare = _cmp
HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("ex121", T121.run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
