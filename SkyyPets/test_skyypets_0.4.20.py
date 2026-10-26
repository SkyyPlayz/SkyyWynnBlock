"""Harness for SkyyPets 0.4.20 (the pet widget's data: the bridge pets:fn:hud, class PetHudFn; tools/pets_0_4_20_patch.py).
Build first:
    python tools/pets_0_4_20_patch.py && python SkyyPets/build_skyypets_0.4.20.py
    python SkyyPets/test_skyypets_0.4.20.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; 0.4.19's patch still regenerates 0.4.19 byte for byte; one class added (PetHudFn),
                 no system / command; the jar: no entry added / removed besides the class, changed non-class entries = manifest.json only
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.19 -> 0.4.20, engine-access audit
  PH    EXECUTED on a stand-in world (the 0.4.19 PK seams, real PetViews + the real dragon fight clock): pets:fn:hud for a stranger (no
                 record cached -> null and NO pet file created), both slots empty, a Rare Wolf in the pet slot (17 fields: rarity portrait,
                 level / cap / XP / next level), a '|' in a text, a summoned Lv 50 Fire Dragon (health from its pool, "Bite" ok -> "f" with a
                 target -> "r" ridden), hurt (health down), DOWN ("0" + "d<ms>" + the bar), a Light Dragon's Radiance clock ("c<ms>"), a
                 non-dragon summon (no health, no ability), the summon slot locked (""), dragon fighting off (no health, "Bite" gone,
                 Radiance kept), pets off / profile switching / a bad record -> null; UUID / String / Object[] arguments; setup publishes
                 it + shutdown takes off only ours (the real plugin methods are not run: the bridge lines are read from the script)
  pk    0.4.19's PK phase EXECUTED on this jar (the secret dragons' perks: nothing in the fight changed)
  live  0.4.17's start-twice on a scratch COPY of the live Skyy_SkyyPets (no saved-data change); live2: every live pet file answered by
                 pets:fn:hud (17 fields per filled slot), nothing written
NOT COVERED (UNVERIFIED in game): the widget itself (SkyyHud 0.3.37's harness draws it).
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "petwid", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s419 = importlib.util.spec_from_file_location("test_skyypets_0_4_19", os.path.join(HERE, "test_skyypets_0.4.19.py"))
T419 = importlib.util.module_from_spec(_s419)
_s419.loader.exec_module(T419)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T44, T41, T417 = T419.T44, T419.T41, T419.T417

VERSION = "0.4.20"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.19.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.19.py")
PATCH = os.path.join(TOOLS, "pets_0_4_20_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T419.JAR = JAR
EXPECT = {   # the class compare 0.4.19 -> 0.4.20: PetHudFn + setup / shutdown; every other member = the version text only (the patch's
    # finish() proves the script changed nowhere else: the config kit header / export, the History titles of the one-time migrations)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetsCfg': ['~m applyAll', '~m seed'],
    'PetsMigP5': ['~m mgLog', '~m run'],
    'PetsMigS2': ['~m run'],
    'PetsMigW15': ['~m run'],
    'SkyyPetsPlugin': ['~m setup', '~m shutdown'],
}
ADDED = ["PetHudFn"]
if "--expect-dump" in sys.argv:
    EXPECT = {}


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.20 - build script') and g.count('VERSION = "0.4.20"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls(") + 1,
            "S one class added (PetHudFn), no system or command")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_19_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), ["com/skyy/pets/PetHudFn.class"], "S the jar adds only PetHudFn.class")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    ch = sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n))
    K.eq(ch, ["manifest.json"], "S changed non-class entries = manifest.json (the version)")
    K.check('"pets:fn:hud", new @PKG@.PetHudFn()' in g and 'if (hf instanceof @PKG@.PetHudFn) br.remove("pets:fn:hud", hf);' in g,
            "S setup publishes pets:fn:hud; shutdown takes it off only while it holds ours")
    K.save()


# ======================================================================================================== PH: pets:fn:hud EXECUTED
def run_ph(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "ph")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JFloat, JObject
    P_ = lambda n: JClass(PKG + n)
    Cfg, Views, PW, Store, Ops, Fg, Sec, Dg, Hf = (P_("PetsCfg"), P_("PetViews"), P_("PetWorld"), P_("PetStore"), P_("PetOps"), P_("PetFight"),
                                                   P_("PetSecret"), P_("PetDragon"), P_("PetHudFn"))
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                      "nameOf": lambda u: "Rider", "tell": lambda u, t, c: None})
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.server.core.universe.world.World")
    UUID = W["UUID"]
    st = U.allocateInstance(Store_.class_)
    w = U.allocateInstance(World.class_)
    ents, jobs = {}, []
    nxt = [100]

    def new_ref(uuid, role, pos, hp=(100.0, 0.0, 100.0), player=None):
        nxt[0] += 1
        r = Ref(st, nxt[0])
        ents[int(r.getIndex())] = {"uuid": uuid, "role": role, "pos": list(pos), "removed": False, "hp": list(hp), "player": player, "dead": False}
        return r
    ent = lambda r: None if r is None else ents.get(int(r.getIndex()))
    uo = UUID.fromString("00000000-0000-0000-0000-000000009937")
    oref = new_ref(uo, None, [10.0, 70.0, 10.0], hp=(200.0, 0.0, 200.0), player=uo)
    roles = {"Skyy_Pet_Walk": 11, "Skyy_Pet_Fly": 12, "Skyy_Pet_Dragon": 13, "Test_Pet": 7, "Test_Fly": 8}

    def spawn(s, role, x, y, z, yaw, model):
        rn = [k for k, v in roles.items() if v == int(role)][0]
        return new_ref(UUID.randomUUID(), rn, [float(x), float(y), float(z)])

    def pos(acc, r):
        e = ent(r)
        return None if e is None or e["removed"] else JArray(JDouble)(e["pos"])

    def remove(acc, r):
        e = ent(r)
        if e is None or e["removed"]:
            return False
        e["removed"] = True
        return True
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": lambda m, s: JString("%s" % m), "modelPinned": lambda m, s, seed: JString("%s#%s" % (m, seed)),
           "spawn": spawn, "store": lambda w_: st, "ownerRef": lambda u_: oref if str(u_) == str(uo) else None, "refOf": lambda w_, u_: None,
           "execute": lambda w_, r_: (jobs.append(r_), True)[1], "pos": pos, "setPos": lambda *a: None,
           "teleport": lambda acc, r, x, y, z, yaw: ent(r)["pos"].__setitem__(slice(0, 3), [float(x), float(y), float(z)]),
           "dead": lambda acc, r: bool((ent(r) or {}).get("dead")), "uuid": lambda acc, r: (ent(r) or {}).get("uuid"), "roleOf": lambda acc, r: (ent(r) or {}).get("role"),
           "tags": lambda acc, r: JString(""), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None, "clearDebug": lambda acc, r: None,
           "mark": lambda acc, r, o: None, "remove": remove, "hearts": lambda *a: None, "anim": lambda acc, r, a: None, "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: 1.0, "fx": lambda acc, i, x, y, z: None, "passthrough": lambda acc, r, m: JString("all")}
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)

    def health(acc, r):
        e = ent(r)
        return None if e is None or e["hp"] is None else JArray(JFloat)(e["hp"])
    Fg.API = JProxy(PKG + "PetFightApi", dict={"hit": lambda cb, t, src, cause, amt: True, "health": health, "playerOf": lambda acc, r: (ent(r) or {}).get("player"),
                                                "guarded": lambda acc, r: False})
    Sec.HEAL_API = JProxy("java.util.function.BiFunction", dict={"apply": lambda r, amt: JClass("java.lang.Double").valueOf(float(amt))})

    def reload():
        Cfg.reloadAll()
        Cfg.SPAWN_DELAY = 0
        Cfg.SLOT2_MODE = "always"
    reload()
    W["names"][str(uo)] = "Rider"
    fn = Hf()
    pets_dir = os.path.join(W["home"], "pets")
    files0 = sorted(os.listdir(pets_dir)) if os.path.isdir(pets_dir) else []

    # ---- a stranger: no cached record -> null, and NO file is created (memory only)
    ux = UUID.fromString("00000000-0000-0000-0000-000000000777")
    K.check(fn.apply(ux) is None and (sorted(os.listdir(pets_dir)) if os.path.isdir(pets_dir) else []) == files0 and Store.REC.get(str(ux)) is None,
            "PH a player whose record is not loaded -> null, no disk load, no file written")
    key = str(Store.pkey(uo))
    Store.KEYOF.put(uo, key)
    r = Store.get(key)
    r.set("starter", "1")
    clock = [0]

    def second(plus=1000):
        clock[0] += plus
        Fg.NOW_OFF = clock[0]
        Views.second(uo, oref, st, None, w, "default")
        while jobs:
            jobs.pop(0).run()
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))

    def lines(arg=None):
        a = fn.apply(uo if arg is None else arg)
        return None if a is None else [str(x) for x in a]
    F = lambda s: s.split("|")
    K.eq(lines(), ["", ""], "PH both slots empty -> two empty lines")
    # ---- the pet slot: a Rare Wolf Lv 12 with 420 XP
    pw = str(Ops.create(r, None, "Wolf", 3, 12, 420, "test", "harness", False))
    r.set("active.1", pw)
    a = lines()
    f = F(a[0])
    need = int(P_("PetMath").need(13))
    K.check(len(f) == 17 and f[:10] == ["1", pw, "Wolf", "3", "Wolf", "12", str(int(r.capOf(pw))), "420", str(need), "Skyy_PetIcon_Wolf_Rare"] and f[10:] == [""] * 7 and a[1] == "",
            "PH pet slot: 17 fields - slot, id, kind, rarity 3, name, Lv 12, cap, 420 XP, next level %d, the Rare portrait; no health / ability: %s" % (need, a))
    K.eq(lines(str(uo)), a, "PH ... the same for the UUID's String")
    K.eq(lines(JArray(JObject)([uo])), a, "PH ... and for Object[] { UUID }")
    K.check(fn.apply(JString("not-a-uuid")) is None and fn.apply(None) is None, "PH a bad argument -> null (never throws)")
    r.set("pet.%s.level" % pw, str(int(r.capOf(pw))))
    K.eq(F(lines()[0])[8], "0", "PH at the level cap the next-level XP is 0")
    r.set("pet.%s.level" % pw, "12")
    # ---- a summoned Lv 50 Fire Dragon
    Views.clearAll() if hasattr(Views, "clearAll") else None
    pd = str(Ops.create(r, None, "DragonFire", 5, 50, 1000, "test", "harness", False))
    r.set("active.2", pd)
    second(0)
    second(0)
    v = Views.view(uo, 2)
    K.check(v is not None and str(v.petId) == pd, "PH the Fire Dragon is summoned (a real PetView)")
    second()
    a = lines()
    f = F(a[1])
    mx = round(float(v.fhpMax))
    K.check(len(f) == 17 and f[0] == "2" and f[2] == "DragonFire" and f[3] == "5" and f[9] == "Skyy_PetIcon_DragonFire_Legendary" and f[10] == str(mx) and f[11] == str(mx) and mx > 0
            and f[12] == "Bite" and f[13] == "ok" and f[14] == "" and f[15] == "" and f[16] == "#d6e4ee",
            "PH summon: Legendary Fire Dragon, full health %d / %d from its pool, Bite ready, NO cooldown bar (FIX petwidfix: field 14 ''): %s" % (mx, mx, a[1]))
    v.fhp = float(v.fhpMax) * 0.4
    v.fhitAt = int(Fg.now())
    f = F(lines()[1])
    K.check(f[10] == str(int(-(-float(v.fhp) // 1))) and f[11] == str(mx), "PH hurt: health %s / %s" % (f[10], f[11]))
    mob = new_ref(UUID.randomUUID(), "Trork_Warrior", [13.0, 70.0, 10.0], hp=(500.0, 0.0, 500.0))
    v.ftgt = mob
    K.eq(F(lines()[1])[13:15], ["f", ""], "PH with a target: 'f' (fighting), no bar")
    v.ftgt = None
    v.riding = True
    f = F(lines()[1])
    K.check(f[13] == "r" and f[14] == "" and f[15] == "riding", "PH ridden: 'r' + state riding (Bite: no bar)")
    v.riding = False
    # ---- DOWN
    dm = int(Dg.downMs(50))
    Dg.DOWN.put(pd, JClass("java.lang.Long").valueOf(int(JClass("java.lang.System").currentTimeMillis()) + dm // 2))
    f = F(lines()[1])
    left = int(f[13][1:]) if f[13].startswith("d") else -1
    K.check(f[10] == "0" and f[15] == "down" and 0 < left <= dm // 2 and abs(float(f[14]) - 0.5) < 0.02,
            "PH DOWN: health 0, 'd%d' (back in about half of %d ms), bar %s" % (left, dm, f[14]))
    Dg.DOWN.clear()
    # ---- fighting off: no health, no Bite
    Cfg.DRAGON_FIGHT = False
    f = F(lines()[1])
    K.check(f[10] == "" and f[11] == "" and f[12] == "" and f[13] == "", "PH dragon fighting off: no health pool, no Bite: %s" % f[10:])
    reload()
    # ---- a '|' in a text never breaks the line
    K.eq(str(Hf.safe("a|b\nc")), "a/b c", "PH safe(): '|' -> '/', line breaks -> spaces")
    # ---- Radiance (Light Dragon): the heal clock
    for pid_ in [str(x) for x in r.ids()]:
        if pid_ != pw:
            r.set("pet.%s.kind" % pid_, None)
    pl = str(Ops.create(r, None, "DragonLight", 5, 40, 0, "test", "harness", False))
    r.set("active.2", pl)
    second(0)
    second(0)
    f = F(lines()[1])
    K.check(f[2] == "DragonLight" and f[12] == "Radiance" and f[13] == "ok" and f[14] == "1.000" and f[16] == str(Sec.colOf("DragonLight")), "PH Light Dragon: Radiance (its colour %s), ready, full bar (a real cooldown): %s" % (f[16], f[12:]))
    tot = int(Sec.lightMs())
    Sec.LIGHT_AT.put(pl, JClass("java.lang.Long").valueOf(int(Fg.now()) + tot - 2500))
    f = F(lines()[1])
    K.check(f[13].startswith("c") and 2400 <= tot - int(f[13][1:]) <= 2600 and abs(float(f[14]) - 2500.0 / tot) < 0.01,
            "PH Radiance cooling down: %s, bar %s (of %d ms)" % (f[13], f[14], tot))
    Cfg.DRAGON_FIGHT = False
    f = F(lines()[1])
    K.check(f[10] == "" and f[12] == "Radiance", "PH ... fighting off: no health, Radiance kept (it heals without fighting)")
    reload()
    # ---- FIX petwidfix: a passive secret perk (every secret dragon but the Light one) = "p", no bar; with a target 'f', no bar
    _pas = [str(x) for x in Sec.KINDS if int(Sec.idx(str(x))) != 2]
    K.check(len(_pas) == 3, "PH three passive secret dragons: %s" % _pas)
    for _kd in _pas:
        for pid_ in [str(x) for x in r.ids()]:
            if pid_ != pw:
                r.set("pet.%s.kind" % pid_, None)
        _pp = str(Ops.create(r, None, _kd, 5, 40, 0, "test", "harness", False))
        r.set("active.2", _pp)
        second(0)
        second(0)
        f = F(lines()[1])
        K.check(f[2] == _kd and f[12] == str(Sec.abilName(_kd)) and f[13] == "p" and f[14] == "" and f[16] == str(Sec.colOf(_kd)),
                "PH %s: its perk %s reads 'p' (passive), no cooldown bar: %s" % (_kd, f[12], f[12:]))
        _v = Views.view(uo, 2)
        K.check(_v is not None and str(_v.petId) == _pp, "PH %s is summoned (a real PetView)" % _kd)
        if _v is not None and str(_v.petId) == _pp:
            _v.ftgt = mob
            K.eq(F(lines()[1])[13:15], ["f", ""], "PH %s with a target: 'f', no bar" % _kd)
            _v.ftgt = None
    reload()
    # ---- a non-dragon summon: no health, no ability
    for pid_ in [str(x) for x in r.ids()]:
        if pid_ != pw:
            r.set("pet.%s.kind" % pid_, None)
    ph_ = str(Ops.create(r, None, "Horse", 2, 5, 0, "test", "harness", False))
    r.set("active.2", ph_)
    f = F(lines()[1])
    K.check(f[2] == "Horse" and f[9] == "Skyy_PetIcon_Horse_Uncommon" and f[10:] == [""] * 7, "PH a Horse in the summon slot: no health, no ability: %s" % f)
    # ---- the summon slot locked
    Cfg.SLOT2_MODE = "off"
    a = lines()
    K.check(a[1] == "" and a[0].startswith("1|"), "PH summon slot locked -> '' (the pet slot still answers)")
    reload()
    # ---- cannot answer
    Cfg.ON = False
    K.check(fn.apply(uo) is None, "PH pets off -> null")
    reload()
    W["BR"].put("profile:busy:" + str(uo), JClass("java.lang.Boolean").TRUE)
    K.check(fn.apply(uo) is None, "PH profile switching -> null")
    W["BR"].remove("profile:busy:" + str(uo))
    r.bad = True
    K.check(fn.apply(uo) is None, "PH an unreadable pet file -> null")
    r.bad = False
    K.check(int(Hf.CALLS.get()) > 10, "PH the CALLS counter (%d)" % int(Hf.CALLS.get()))
    _bad = [str(l) for l in P_("PetsLog").LINES if "SEVERE" in str(l) or "pets:fn:hud failed" in str(l)]
    K.check(not _bad, "PH no SEVERE, no 'pets:fn:hud failed': %s" % _bad[:4])
    K.save()


# ======================================================================================================== live2: every live pet file answered
def run_live2(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Log, Hf = P_("PetsCfg"), P_("PetStore"), P_("PetsLog"), P_("PetHudFn")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    res = []
    for _n in range(2):
        t0 = T41.tree(home)
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        Store.scanAll()
        fn = Hf()
        got, bad = 0, []
        pdir = os.path.join(home, "pets")
        for k in sorted(f[:-11] for f in os.listdir(pdir) if f.endswith(".properties")) if os.path.isdir(pdir) else []:
            try:
                u = UUID.fromString(k[:36])
            except Exception:
                continue
            Store.KEYOF.put(u, k)          # = the player joined on that profile: the record is loaded (as PetTickSys does)
            Store.get(k)
            a = fn.apply(u)
            if a is None:
                continue
            for ln in [str(x) for x in a]:
                if ln and len(ln.split("|")) != 17:
                    bad.append((k[:8], ln[:60]))
                elif ln:
                    got += 1
        res.append((got, bad, sorted(x for x in set(t0) | set(T41.tree(home)) if t0.get(x) != T41.tree(home).get(x) and not x.startswith(("config", "migrations")))))
    K.notes.append("LIVE2: %d filled pet / summon slots answered in the live copy" % res[0][0])
    K.check(res[0][1] == [] and res[0] == res[1] and res[0][2] == [],"LIVE2 every live pet file answered by pets:fn:hud (%d filled slots, 17 fields each), nothing written, twice: %s" % (res[0][0], res))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("ph", run_ph), ("pk", T419.run_pk), ("live", T417.run_live), ("live2", run_live2)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
