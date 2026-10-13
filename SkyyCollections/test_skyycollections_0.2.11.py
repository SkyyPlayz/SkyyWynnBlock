"""Harness for SkyyCollections 0.2.11 (the Enchanted materials; tools/collections_0_2_11_patch.py, tools/skyyench.py).
Build first: python tools/collections_0_2_11_patch.py && python SkyyCollections/build_skyycollections_0.2.11.py

    python SkyyCollections/test_skyycollections_0.2.11.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the game's JRE, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.2.10 -> 0.2.11: exactly the listed members differ, the added classes are CollEnch / CollKnowTask / EnchRank / EnchTab /
              EnchTabL; non-class entries: manifest + the Enchanted asset pack (checked file by file in J)
  J  jar      the asset pack: 19 item JSONs (recipe = 100 x the base, Workbench, the Compressing category, KnowledgeRequired, no BlockType,
              stack 100, the Enchanted quality), the quality JSON, server.lang (names, descriptions, the quality label, the tab name),
              every Model / Texture / Icon in the jar or Assets.zip, PNG sizes (icons 64, the tab icon = the vanilla tab icon size), no
              vanilla path replaced, = tools/skyyench.py rebuilt now (byte-identical: the art is deterministic), no un-compress recipe
  X  exec     EXECUTED on the compiled classes (registry loaded from the default files in scratch):
              table: idx / nameOf / CollUtil.prettyItem / prettyRecipe / recipeLabel / bagRank 9 (coins never buy one);
              config: CollEnch.load defaults / ench.on false / bad words / tiers 1-20 / out of range; configText carries the keys;
              Server Setup: CollKit.checkEnchTier against each collection's ladder;
              unlocks: merge (all present) puts each recipe at its collection tier "c.t" exactly once, a second merge adds nothing, a tier
              past the ladder is clamped, a missing recipe / ench.on false merges none; compute() of a profile at Iron III / Adamantite II
              / Oak II gives exactly the Iron + Adamantite Enchanted recipes, not Oak; a bought tier never unlocks one (bagRank 9);
              auto rule (ench01fix2): CollUtil.autoOk refuses all 19 Enchanted + Lantern ids, allows a vanilla id; compute() with
              auto=true gives the same Enchanted set as auto=false (no tier-I unlock) and throws nothing;
              validate(): SkyyVoid's recipe-less Skyy_Sack_ ids are counted as skipped (no unknown-id WARN) while sacks:v2 is set, and are
              still "unknown" without it (the 0.2.10 behaviour);
              knowledge: wantSig, next (only the 19 managed entries change; other entries kept; null when equal), syncData on a REAL engine
              PlayerConfigData (learn, forget, idempotent, foreign entries untouched); note / schedule / retry / retain / CollKnowTask.run
              without a world (the queue is released, nothing throws);
              alias: alias(Enchanted, 1..64) = (the collection's first item, x 100), 0 / 65 / a plain id -> null;
              alias credit (ench01fix): creditWhole of 6400 with cap.perCredit 1 credits all 6400 (one task, never split / clipped),
              the minute cap still clips it, the plain path still clips to cap.perCredit; CollAddTask.whole defaults false and a whole
              task without a world does nothing and throws nothing;
              tooltip (ench01fix): no /smithing promise, no "already collected" claim, the Rubble label names the Ice / Dawnstone gap;
              Workbench tab: EnchTab.applyTo on a REAL engine CraftingBench (appended once, idempotent, a stale entry replaced in place,
              copy-on-write: the old array untouched), EnchRank = table order
  D  live     start twice on a scratch COPY of the live Skyy_SkyyCollections with 0.2.10 and 0.2.11 (loadAll + validate + publish of every
              profile): the folder bytes never change; every profile's coll:recipes on 0.2.11 = 0.2.10's + only Skyy_Ench_ recipes, and
              exactly the ones its collection tiers reach (with the Enchanted recipes present)
  AA engine-access audit
Scratch: tools/dev/scratch/ench01/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, zipfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

VERSION = "0.2.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.10.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ench01", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")
EXPECT = {
    "CollUtil": ["~m bagRank", "~m prettyItem", "+m autoOk"],   # ench01fix2: autoOk = the auto rule's recipe filter
    "CollUnlocks": ["~m publishLocked", "~m publishOnline", "~m compute0"],
    "CollReg": ["~m configText", "~m loadConfig", "~m validate"],
    "CollFn": ["~m apply"],
    "CollKit": ["+m checkEnchTier"],
    "CollSaver": ["~m run"],
    "CollCredit": ["+m creditWhole"],          # ench01fix: the alias credit = one task, cap.perMinute only
    "CollAddTask": ["+f whole", "~m run"],
    "SkyyCollectionsPlugin": ["~m setup", "~m start"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header", "~<clinit>"],    # the config kit: version text + the 20 new rows
    "CfgFile": ["~<clinit>"],                 # the config kit: the default config.properties text (+ ench.on / ench.tier.*)
}
ADDED = ["CollEnch", "CollKnowTask", "EnchRank", "EnchTab", "EnchTabL"]
UID_S = "11111111-2222-3333-4444-555555555555"


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


# ---------------------------------------------------------------------------------------------------------------- J: the asset pack (no JVM)
def run_jar(out, jar, scratch, _home):
    import skyyart as SA
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    with SA.assets() as az:
        vnames = set(az.namelist())
        files, lang = EN.build_assets(az, SA)
        K.check(bool(EN.check_assets(files, az)), "J the build's asset checks pass on a fresh build")
    files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
    nonclass = sorted(n for n in names if not n.endswith(".class") and n != "manifest.json")
    K.eq(nonclass, sorted(files), "J the jar's asset files = tools/skyyench.py's (no more, no less)")
    for p, data in files.items():
        if p in names:
            got = z.read(p)
            K.check(got == (data.encode("utf-8") if isinstance(data, str) else data), "J %s byte-identical to a fresh build (deterministic art)" % p)
    K.check(not (set(files) & vnames - {"Server/Languages/en-US/server.lang"}), "J no vanilla path replaced (server.lang = every pack's merged language file)")
    for eid in EN.IDS:
        n = json.loads(z.read("Server/Item/Items/SkyyCollections/%s.json" % eid))
        t = EN.row(eid[len(EN.PREFIX):])
        r = n["Recipe"]
        inp = r["Input"][0]
        K.check(r["KnowledgeRequired"] is True and r["OutputQuantity"] == 1 and inp["Quantity"] == 100
                and (inp.get("ItemId") == t[2] if t[1] == "I" else inp.get("ResourceTypeId") == t[2]), "J %s recipe = 100 %s -> 1, knowledge" % (eid, t[2]))
        K.eq(r["BenchRequirement"], [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_SkyyCompressing"]}], "J %s Workbench, Compressing tab" % eid)
        K.check("BlockType" not in n and "Parent" not in n and n["MaxStack"] == 100 and n["Quality"] == "Skyy_Enchanted"
                and "Consumable" not in n and "Interactions" not in n, "J %s: not placeable, not edible, stack 100, quality Enchanted" % eid)
        for k in ("Model", "Texture", "Icon"):
            q = "Common/" + n[k]
            K.check(q in names or q in vnames or (q[:-4] + "@2x.png") in vnames, "J %s %s %s exists" % (eid, k, n[k]))
        K.eq(SA.png_size(z.read("Common/" + n["Icon"])), (64, 64), "J %s icon 64 x 64" % eid)
    lt = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for t in EN.TABLE:
        eid = EN.PREFIX + t[0]
        K.check(("\nitems.%s.name=%s\n" % (eid, t[6])) in "\n" + lt and ("server.items.%s.name=%s\n" % (eid, t[6])) in lt
                and ("items.%s.description=" % eid) in lt, "J lang: %s = %s (+ description)" % (eid, t[6]))
    descs = [ln.split("=", 1)[1] for ln in lt.split(chr(10)) if ln.startswith("server.items.Skyy_Ench_") and ".description=" in ln]
    K.check(len(descs) == 19 and all("smithing" not in d_ and "already collected" not in d_ and "adds nothing to your collections" in d_
                                     and "coming soon" in d_ for d_ in descs), "J tooltips (ench01fix): no /smithing promise, no 'already collected' claim")
    rd = [d_ for d_ in descs if "Rubble" in d_]
    K.check(len(rd) == 1 and "but Ice or Dawnstone" in rd[0], "J tooltip (ench01fix): the Rubble one names the Ice / Dawnstone gap: %s" % (rd[:1],))
    K.check("server.general.qualities.Skyy_Enchanted=Enchanted" in lt and "server.benchCategories.workbench.skyycompressing=Compressing" in lt,
            "J lang: the quality label and the tab name")
    with SA.assets() as az:
        ref = SA.png_size(az.read("Common/Icons/CraftingCategories/Workbench/Processing.png"))
    K.eq(SA.png_size(z.read("Common/" + EN.tab_icon_path())), ref, "J the tab icon is the vanilla tab icon size")
    mf = json.loads(z.read("manifest.json"))
    K.check(mf["IncludesAssetPack"] is True and mf["Version"] == VERSION, "J manifest: asset pack, version %s" % VERSION)
    recs = [p for p in names if p.startswith("Server/") and p.endswith(".json") and b'"Recipe"' in z.read(p)]
    K.check(all(p.rsplit("/", 1)[1][:-5].startswith(EN.PREFIX) for p in recs) and len(recs) == 19, "J every recipe in the jar makes an Enchanted item (no un-compress)")
    K.notes.append("J: %d asset files, %d items" % (len(files), len(EN.IDS)))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: executed
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    L = loader_for(jar)
    jc = lambda n: JClass(PKG + n, loader=L)
    En, Reg, Store, Util, Unl, Kit, Tab, Rank, Task = (jc("CollEnch"), jc("CollReg"), jc("CollStore"), jc("CollUtil"), jc("CollUnlocks"),
                                                      jc("CollKit"), jc("EnchTab"), jc("EnchRank"), jc("CollKnowTask"))
    Paths, Props, HashMap, HashSet, UUID = (JClass("java.nio.file.Paths"), JClass("java.util.Properties"), JClass("java.util.HashMap"),
                                            JClass("java.util.HashSet"), JClass("java.util.UUID"))
    # ---- the table + names + coin rule
    for k, t in enumerate(EN.TABLE):
        eid, rid = EN.IDS[k], EN.RIDS[k]
        K.eq(int(En.idx(eid)), k, "X idx %s" % eid)
        K.eq(str(En.nameOf(eid)), t[6], "X nameOf %s" % eid)
        K.eq(str(Util.prettyItem(eid)), t[6], "X prettyItem %s" % eid)
        K.eq(str(Util.prettyRecipe(rid)), t[6], "X prettyRecipe %s" % rid)
        K.eq(str(Util.recipeLabel(rid)), t[6] + " recipe", "X recipeLabel %s" % rid)
        K.eq(int(Util.bagRank(rid)), 9, "X bagRank %s = 9 (coins never unlock it)" % rid)
    for bad in ("Skyy_Ench_Mithril", "Skyy_Ench_", "Rock_Stone_Cobble", None):
        K.eq(int(En.idx(bad)), -1, "X idx %r = -1" % bad)
    K.eq(str(Util.prettyItem("Tool_Pickaxe_Copper")), "Copper Pickaxe", "X prettyItem of other ids unchanged")
    K.eq(int(Util.bagRank("Skyy_Sack_Mining_Rare_Recipe_Generated_0")), 3, "X bagRank of a bag unchanged")
    # ---- config
    p = Props()
    K.eq(str(En.load(p)), "on " + "/".join(str(t[4]) for t in EN.TABLE), "X load: defaults")
    K.check(bool(En.ON), "X load: ON by default")
    p.setProperty("ench.on", "false")
    p.setProperty("ench.tier.iron", "5")
    p.setProperty("ench.tier.copper", "25")
    p.setProperty("ench.tier.oak", "x")
    En.load(p)
    K.check(not bool(En.ON) and int(En.TIER[En.idx("Skyy_Ench_Iron")]) == 5 and int(En.TIER[En.idx("Skyy_Ench_Copper")]) == 3
            and int(En.TIER[En.idx("Skyy_Ench_Oak")]) == 3, "X load: off, a tier, an out-of-range and a bad tier (default kept)")
    p2 = Props()
    p2.setProperty("ench.on", "maybe")
    En.load(p2)
    K.check(bool(En.ON), "X load: a word that is neither on nor off = ON")
    En.load(Props())
    # ---- registry (default files in scratch)
    wbase = os.path.join(scratch, "x", "Skyy_SkyyCollections")
    os.makedirs(wbase)
    Reg.BASE = Paths.get(wbase)
    Store.DIR = Paths.get(wbase).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    cfg = open(os.path.join(wbase, "config.properties"), encoding="utf-8").read()
    K.check("ench.on=true" in cfg and all(("%s=%d" % (EN.tier_key(t[0]), t[4])) in cfg for t in EN.TABLE), "X config.properties (fresh) carries ench.on + 19 tier keys")
    K.check(str(Reg.configText()) == cfg, "X configText = the written file")
    BYID = dict((str(R.id[c]), c) for c in range(R.n))
    for t in EN.TABLE:
        mx = int(Reg.maxTier(R, BYID[t[3]]))
        key = EN.tier_key(t[0])
        K.check(Kit.checkEnchTier(key, str(mx)) is None and Kit.checkEnchTier(key, "1") is None and Kit.checkEnchTier(key, str(mx + 1)) is not None
                and Kit.checkEnchTier(key, "0") is not None and Kit.checkEnchTier(key, "x") is not None, "X checkEnchTier %s: 1..%d" % (key, mx))
    # ---- merge
    allp = HashSet()
    for r_ in EN.RIDS:
        allp.add(r_)
    out1 = HashMap()
    note = str(En.merge(out1, R, allp))
    where = {}
    for k_ in out1.keySet():
        for r_ in out1.get(k_):
            where.setdefault(str(r_), []).append(str(k_))
    K.check(all(where.get(EN.RIDS[k]) == ["%d.%d" % (BYID[t[3]], t[4])] for k, t in enumerate(EN.TABLE)), "X merge: each recipe once, at its collection tier (%s)" % note)
    n1 = sum(len(out1.get(k_)) for k_ in out1.keySet())
    En.merge(out1, R, allp)
    K.eq(sum(len(out1.get(k_)) for k_ in out1.keySet()), n1, "X merge twice: nothing added")
    En.TIER[En.idx("Skyy_Ench_Adamantite")] = 20
    o2 = HashMap()
    En.merge(o2, R, allp)
    ad = BYID["Adamantite"]
    K.check(any(str(x) == EN.RIDS[EN.IDS.index("Skyy_Ench_Adamantite")] for x in (o2.get("%d.%d" % (ad, int(Reg.maxTier(R, ad)))) or [])), "X merge: a tier past the ladder = the last tier")
    En.load(Props())
    part = HashSet()
    part.add(EN.RIDS[0])
    o3 = HashMap()
    K.check("1 of 19" in str(En.merge(o3, R, part)) and o3.size() == 1, "X merge: a recipe the asset store lacks is skipped")
    poff = Props()
    poff.setProperty("ench.on", "off")
    En.load(poff)
    o4 = HashMap()
    K.check("off" in str(En.merge(o4, R, allp)) and o4.size() == 0, "X merge: ench.on off = none")
    En.load(Props())
    K.check(En.present().size() == 0, "X present(): no asset store in a bare JVM = none (validate then merges none - in game the asset pack provides them)")
    # ---- compute: a profile at Iron III / Adamantite II / Oak II
    rec = HashMap()
    for c in range(R.n):
        for t_ in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t_))
            if toks is not None:
                ids = [str(x)[7:].strip() for x in toks if str(x).startswith("recipe:")]
                if ids:
                    rec.put("%d.%d" % (c, t_), JArray(JString)(ids))
    En.merge(rec, R, allp)
    Reg.RECIPES = rec
    Reg.VALIDATED = True
    cd = os.path.join(wbase, "counts")
    os.makedirs(cd, exist_ok=True)
    thr = lambda cid, t_: int(Reg.threshold(R, BYID[cid], t_))
    open(os.path.join(cd, UID_S + ".properties"), "w").write("_schema=2\nOre_Iron=%d\nOre_Adamantite=%d\nWood_Oak_Trunk=%d\n"
                                                              % (thr("Iron", 3), thr("Adamantite", 2), thr("OakLog", 2)))
    u = UUID.fromString(UID_S)
    d = Store.data(u)
    got = sorted(str(x) for x in Unl.compute(d) if str(x).startswith(EN.PREFIX))
    K.eq(got, sorted([EN.RIDS[EN.IDS.index("Skyy_Ench_Iron")], EN.RIDS[EN.IDS.index("Skyy_Ench_Adamantite")]]), "X compute: Iron III + Adamantite II unlock theirs, Oak II does not")
    # ---- ench01fix2: the opt-in auto=true rule never unlocks an Enchanted (or Lantern) recipe
    K.check(all(not Util.autoOk(x) for x in EN.RIDS), "X autoOk: every Enchanted recipe id is refused by the auto rule")
    K.check(not Util.autoOk("Skyy_Talisman_Lantern_Oak_Common") and not Util.autoOk(None) and not Util.autoOk(" Skyy_Ench_Iron_Recipe"),
            "X autoOk: Lantern / null / padded Enchanted ids refused")
    K.check(bool(Util.autoOk("Furniture_Crude_Chest")) and bool(Util.autoOk("Skyy_Sack_Mining_Small")), "X autoOk: other recipe ids still allowed (the 0.2.10 rule)")
    Reg.AUTO = True
    try:
        got_auto = sorted(str(x) for x in Unl.compute(d) if str(x).startswith(EN.PREFIX))
    finally:
        Reg.AUTO = False
    K.eq(got_auto, got, "X compute with auto=true: the same Enchanted recipes as auto=false (no tier-I unlock)")
    # ---- validate: SkyyVoid's recipe-less bag ids
    b = JClass("java.lang.System").getProperties().get("skyy.bridge")
    if b is None:
        b = JClass("java.util.concurrent.ConcurrentHashMap")()
        JClass("java.lang.System").getProperties().put("skyy.bridge", b)
    b.remove("sacks:v2")
    v_off = str(Reg.validate())
    b.put("sacks:v2", JClass("java.lang.Boolean").TRUE)
    v_on = str(Reg.validate())
    import re as _re
    def num(pat, s_):
        m_ = _re.search(pat, s_)
        return int(m_.group(1)) if m_ else 0
    nb = sum(1 for k_ in Reg.REWARDS.keySet() for x in Reg.REWARDS.get(k_) if str(x).startswith("recipe:Skyy_Sack_"))
    K.check(nb >= 20 and num(r"(\d+) Magic Bag recipe id\(s\) skipped", v_on) == nb and num(r"(\d+) unknown recipe id\(s\) skipped", v_off) - num(r"(\d+) unknown recipe id\(s\) skipped", v_on) == nb
            and "Magic Bag recipe" not in v_off, "X validate: with sacks:v2 the %d bag ids are skipped quietly (on: %s | off: %s)" % (nb, v_on[:160], v_off[:120]))
    K.check("Enchanted recipes: 0 of 19" in v_on, "X validate: the Enchanted note is in the recipe-check line")
    b.remove("sacks:v2")
    # ---- knowledge
    w = str(En.wantSig(HashSet()))
    K.eq(w, "0" * 19, "X wantSig: nothing unlocked")
    some = HashSet()
    some.add(EN.RIDS[3])
    some.add(EN.RIDS[7])
    some.add("Tool_Pickaxe_Iron_Recipe_Generated_0")
    w2 = str(En.wantSig(some))
    K.eq(w2, "".join("1" if k in (3, 7) else "0" for k in range(19)), "X wantSig: the unlocked ones")
    En.ON = False
    K.eq(str(En.wantSig(some)), "0" * 19, "X wantSig: ench.on off = forget all")
    En.ON = True
    PCD = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
    pd = PCD()
    ks = HashSet()
    ks.add("Armor_Bronze_Chest")
    ks.add(EN.IDS[0])
    pd.setKnownRecipes(ks)
    K.check(bool(En.syncData(pd, w2)), "X syncData: learn 3 + 7, forget 0 -> changed")
    kn = sorted(str(x) for x in pd.getKnownRecipes())
    K.eq(kn, sorted(["Armor_Bronze_Chest", EN.IDS[3], EN.IDS[7]]), "X syncData: exactly the managed entries changed (a foreign entry kept)")
    K.check(not bool(En.syncData(pd, w2)), "X syncData: again = nothing to do")
    K.check(En.next(pd.getKnownRecipes(), w2) is None and En.next(pd.getKnownRecipes(), "01") is None, "X next: equal / a malformed want = null")
    K.check(bool(En.syncData(pd, "0" * 19)) and sorted(str(x) for x in pd.getKnownRecipes()) == ["Armor_Bronze_Chest"], "X syncData: forget all, the foreign entry stays")
    # note / schedule / retry / retain / the task, with no world (Universe absent): the queue is released, nothing throws
    En.KWANT.clear(); En.KSIG.clear(); En.KPEND.clear()
    En.note(u, some)
    K.check(str(En.KWANT.get(u)) == w2 and En.KPEND.isEmpty() and En.KSIG.get(u) is None, "X note: the want is kept, the queue released (no world), not applied")
    En.retry()
    K.check(En.KPEND.isEmpty(), "X retry: nothing stuck in the queue")
    En.KPEND.put(u, JClass("java.lang.Boolean").TRUE)
    Task(u, UUID.randomUUID()).run()
    K.check(En.KPEND.isEmpty() and En.KSIG.get(u) is None, "X CollKnowTask.run without a player: released, nothing applied")
    JLong = JClass("java.lang.Long")
    En.KPEND.put(u, JLong.valueOf(JClass("java.lang.System").currentTimeMillis()))
    En.schedule(u)
    K.check(En.KPEND.size() == 1, "X schedule: a task queued less than 10 s ago blocks a second one")
    En.KPEND.put(u, JLong.valueOf(JClass("java.lang.System").currentTimeMillis() - 11000))
    En.schedule(u)
    K.check(En.KPEND.isEmpty(), "X schedule: a queued task older than 10 s (never run) expires - re-queued (here: no world, released)")
    En.KPEND.put(u, JLong.valueOf(JClass("java.lang.System").currentTimeMillis()))
    on = HashSet()
    En.retain(on)
    K.check(En.KWANT.isEmpty() and En.KSIG.isEmpty() and En.KPEND.isEmpty(), "X retain: offline players forgotten (want, applied, queued)")
    # ---- alias
    for k, t in enumerate(EN.TABLE):
        a1 = En.alias(EN.IDS[k], 1)
        a64 = En.alias(EN.IDS[k], 64)
        cred = str(R.items[BYID[t[3]]][0])
        K.check(a1 is not None and str(a1[0]) == cred and int(a1[1]) == 100 and int(a64[1]) == 6400, "X alias %s -> %s x 100" % (EN.IDS[k], cred))
    K.check(En.alias(EN.IDS[0], 0) is None and En.alias(EN.IDS[0], 65) is None and En.alias("Ore_Iron", 1) is None, "X alias: 0 / 65 / a plain id -> null")
    # ---- the alias credit (ench01fix): ONE task, cap.perCredit never splits / clips it, cap.perMinute does
    Cred, AT = jc("CollCredit"), jc("CollAddTask")
    pk = str(Util.pkey(u))
    ci = BYID["Iron"]
    first = str(R.items[ci][0])
    cnt = lambda: int(Store.sum(Store.dataK(pk), R, ci))
    oc, om = int(Reg.CAP_CREDIT), int(Reg.CAP_MINUTE)
    Reg.CAP_CREDIT = 1
    Reg.CAP_MINUTE = 10000
    Cred.MINUTE.clear()
    c0 = cnt()
    Cred.creditWhole(None, u, pk, first, 6400)
    c1 = cnt()
    K.eq(c1 - c0, 6400, "X creditWhole: 64 Enchanted = 6400 %s credited at once with cap.perCredit = 1 (not split, not clipped)" % first)
    Cred.creditWhole(None, u, pk, first, 6400)
    c2 = cnt()
    K.eq(c2 - c1, 3600, "X creditWhole: cap.perMinute 10000 still applies (3600 of the second 6400)")
    Cred.creditWhole(None, u, pk, first, 6400)
    K.eq(cnt(), c2, "X creditWhole: minute full = nothing more")
    Reg.CAP_MINUTE = 0
    Cred.creditOne(None, u, pk, first, 6400, False)
    K.eq(cnt() - c2, 1, "X creditOne (a gather) still clips to cap.perCredit (1)")
    Cred.creditWhole(None, u, pk, first, 0)
    Cred.creditWhole(None, None, pk, first, 5)
    K.eq(cnt() - c2, 1, "X creditWhole: 0 / no player = nothing")
    Reg.CAP_CREDIT = oc
    Reg.CAP_MINUTE = om
    Cred.MINUTE.clear()
    t_ = AT(u, pk, first, 6400)
    K.check(not bool(t_.whole), "X CollAddTask.whole defaults false (every 0.2.10 caller keeps creditOne)")
    t_.whole = True
    c3 = cnt()
    t_.run()
    K.eq(cnt(), c3, "X CollAddTask(whole).run without a player: nothing credited, nothing thrown")
    # ---- the Workbench tab on a real engine CraftingBench
    CB = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.CraftingBench")
    CBC = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.CraftingBench$BenchCategory")
    BIC = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.CraftingBench$BenchItemCategory")
    bench = CB()
    f = CB.class_.getDeclaredField("categories")
    f.setAccessible(True)
    van = JArray(CBC)([CBC("Workbench_Crafting", "server.benchCategories.workbench.crafting", "Icons/CraftingCategories/Workbench/Processing.png", JObject(None, JArray(BIC)))])
    f.set(bench, van)
    K.eq(int(Tab.applyTo(bench)), 1, "X tab: appended")
    c1 = bench.getCategories()
    K.check(len(c1) == 2 and str(c1[0].getId()) == "Workbench_Crafting" and str(c1[1].getId()) == "Workbench_SkyyCompressing"
            and str(c1[1].getName()) == EN.TAB_NAME_KEY and str(c1[1].getIcon()) == EN.tab_icon_path() and len(van) == 1, "X tab: after the vanilla tabs, copy-on-write")
    K.eq(int(Tab.applyTo(bench)), 0, "X tab: idempotent")
    stale = JArray(CBC)([c1[0], CBC("Workbench_SkyyCompressing", "x", "y", JObject(None, JArray(BIC)))])
    f.set(bench, stale)
    K.check(int(Tab.applyTo(bench)) == 2 and len(bench.getCategories()) == 2 and str(bench.getCategories()[1].getIcon()) == EN.tab_icon_path(), "X tab: a stale entry replaced in place")
    K.check(Tab.scan(JClass("java.util.ArrayList")()) == 0 and Tab.applyTo(None) == -1, "X tab: scan of nothing / a null bench")
    K.check(str(Tab.sort()) != "", "X tab: sort() answers without an engine registry (%s)" % Tab.sort())
    rk = Rank()
    K.check(all(int(Rank.rank(EN.RIDS[k])) == k for k in range(19)) and rk.compare(EN.RIDS[0], EN.RIDS[1]) < 0 and rk.compare("Z", EN.RIDS[18]) > 0, "X EnchRank: table order, unknown ids last")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- D: live data, two starts
def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    before = HK.tree_hash(home)
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties")) if os.path.isdir(os.path.join(home, "counts")) else []
    res = {}
    for start in (1, 2):
        for tag, j in (("old", OLD_JAR), ("new", jar)):
            L = loader_for(j)
            jc = lambda n: JClass(PKG + n, loader=L)
            Reg, Store, Unl = jc("CollReg"), jc("CollStore"), jc("CollUnlocks")
            P = JClass("java.nio.file.Paths")
            Reg.BASE = P.get(home)
            Store.DIR = P.get(home).resolve("counts")
            Reg.loadAll()
            Reg.validate()
            R = Reg.D
            if tag == "new":   # the asset store is absent in a bare JVM: merge as the game will (every Enchanted recipe present)
                En = jc("CollEnch")
                hs = JClass("java.util.HashSet")()
                for r_ in EN.RIDS:
                    hs.add(r_)
                rec = JClass("java.util.HashMap")(Reg.RECIPES)
                En.merge(rec, R, hs)
                Reg.RECIPES = rec
            got = {}
            for k in keys:
                d = Store.dataK(k)
                got[k] = None if d is None else sorted(str(x) for x in Unl.compute(d))
            res[(start, tag)] = got
        K.eq(HK.tree_hash(home), before, "D start %d: the live copy's bytes are unchanged" % start)
    for k in keys:
        o, n = res[(1, "old")][k], res[(1, "new")][k]
        if o is None:
            K.check(n is None, "D %s: unreadable on both" % k)
            continue
        extra = [x for x in n if x not in o]
        K.check([x for x in o if x not in n] == [] and all(x.startswith(EN.PREFIX) for x in extra), "D %s: 0.2.11 = 0.2.10 + Enchanted recipes only (%s)" % (k, extra))
        K.eq(res[(2, "new")][k], n, "D %s: the second start gives the same" % k)
    K.notes.append("D: %d live profiles; Enchanted recipes unlocked per profile: %s" % (len(keys), dict((k[:8], len([x for x in (res[(1, "new")][k] or []) if x.startswith(EN.PREFIX)])) for k in keys)))
    K.save()


# the kit's compare allows only manifest.json among the non-class entries; 0.2.11 adds the asset pack on purpose: the entries that changed
# must be EXACTLY manifest.json + the asset pack's files (each checked byte for byte in J), anything else still fails
_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added):
    _orig_compare(out, jar, old_jar, pkg, expect, added)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    pack = sorted(n for n in eb if n not in ea)
    ok = (ed == sorted(["manifest.json"] + pack) and all(n.startswith(("Server/Item/Items/SkyyCollections/", "Server/Item/Qualities/Skyy_Enchanted",
          "Common/Items/SkyyCollections/", "Common/Icons/ItemsGenerated/SkyyCollections_Ench_", "Common/Icons/CraftingCategories/SkyyCollections/",
          "Server/Languages/en-US/server.lang")) for n in pack) and len(pack) == 61)
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    if ok:
        d["ok"] += 1
    else:
        d["fails"].append("C: non-class entries changed beyond manifest + the asset pack: %s" % ed[:10])
    d["notes"].append("C: non-class: manifest.json + %d asset-pack files" % len(pack))
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = _compare
HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("jar", run_jar), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
