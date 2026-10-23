"""Harness for SkyyPets 0.4.12 (THE DRAGON FIGHTS: research/Dragon-Pet-Spec.md 4 = round D1; tools/pets_0_4_12_patch.py).
Build first:
    python tools/pets_0_4_12_patch.py && python SkyyPets/build_skyypets_0.4.12.py
    python SkyyPets/test_skyypets_0.4.12.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; 3 new classes (PetFight, PetFightSys, PetGuardSys) + the PetFightApi seam, two new
                 systems, no new command; line endings kept; the jar: the dragon role = the walk role with MaxWalkSpeed 8 and Invulnerable
                 false (the only changed non-class entries: the role + manifest.json); the 9 Dragons rows in the default file; the
                 model numbers (tools/balance_model.py) in the generated script
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.11 -> 0.4.12, engine-access audit
  M     EXECUTED: the row maths against tools/balance_model.py (share at every level / rarity / rebirth = p5_dragon_share; p4hit =
                 p4_hit), the check= hooks, live row edits, the hit average (3x cap, 5 min), the tables (causes, effects, animations)
  F     EXECUTED on a stand-in world (PetWorld.API + PetFight.API, real Damage objects, real PetViews): a summoned Lv 10 Plain dragon;
                 your hit on a mob = its target (assist) + your hit average; it walks there (the mark), lunges after 3 s out of reach,
                 bites within reach every 1.5 s (the amount = your DPS (hit average / time between hits) x the share x 1.5 s, x the mob's element affinity, the element's
                 cause / effect / animation, the P4 hit at the mob's level when you hit nothing yet); its KILLING bite's source becomes
                 the owner (the kill credit), a non-lethal one stays the dragon; never a player / pet / tamed / ally / invulnerable /
                 dead / far target, never from a cancelled hit, ticks never feed the average; Defend mode = what hits you (your own
                 target wins); the drop rules (too far, idle 20 s, fight off); PetGuardSys: every hit on the dragon cancelled, mob hits
                 lower its pool (% of your max Health x (1 + level / 100)), it hits back, the pool refills after 10 s, at 0 = DOWN (the
                 0.4.11 cooldown + line, the creature removed); the card line; the REAL seams never throw without an engine
  DG/VW/ST  0.4.11's phases EXECUTED on this jar (the card's new text), EL410 0.4.10's element phase
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets (0.4.11's live phase): nothing written, the fight rows at their defaults
NOT COVERED (UNVERIFIED in game): the two damage systems inside the ECS dispatch (their handle() only calls the executed PetFight.inspect
/ guard); the role's Seek walking to a non-player target; the bite animation / effect look; DamageSystems.executeDamage with the element
cause (the harness has no asset store: hitNow's real path is only checked not to throw); SkyySkills paying the kill XP from the rewritten
source; mobs never targeting an Intangible dragon.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, subprocess, inspect, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "dragond1fix", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s411 = importlib.util.spec_from_file_location("test_skyypets_0_4_11", os.path.join(HERE, "test_skyypets_0.4.11.py"))
T411 = importlib.util.module_from_spec(_s411)
_s411.loader.exec_module(T411)
HK.run_compare = _cmp0
HK.Child.eq = _eq00          # 0.4.11's C wrapper expects its own new files - ours below
T410, T44, T41 = T411.T410, T411.T44, T411.T41

VERSION = "0.4.12"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.11.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.11.py")
PATCH = os.path.join(TOOLS, "pets_0_4_12_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T411.PKG = T44.PKG = T410.PKG = PKG
T411.JAR, T411.OLD_JAR = JAR, OLD_JAR
KINDS = T411.KINDS
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "PetDragon": ["~m card"], "PetView": ["+f fbites", "+f fchase", "+f fhitAt", "+f fhp", "+f fhpMax", "+f fnext", "+f fpri", "+f ftgt", "+f ftgtAt", "+f fwhy"],
    "PetViews": ["~m spawnNow", "~m upkeep"], "PetTick": ["~m leave"],          # review fixes: track at spawn, forget the hit average at leave
    "PetsCfg": ["+f DRAGON_EVERY", "+f DRAGON_FIGHT", "+f DRAGON_FMODE", "+f DRAGON_HEAL", "+f DRAGON_HP", "+f DRAGON_RANGE", "+f DRAGON_REACH",
                "+f DRAGON_SHARE", "+f DRAGON_STAGEDMG", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"],
    "PetsMigP5": ["~m mgLog", "~m run"], "SkyyPetsPlugin": ["~m setup", "~m shutdown", "~m start"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["PetFight", "PetFightApi", "PetFightSys", "PetGuardSys"]
ROLE = "Server/NPC/Roles/SkyyPets/Skyy_Pet_Dragon.json"


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + the dragon role (Invulnerable false)"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == sorted(["manifest.json", ROLE]), "C: non-class entries changed = manifest.json + the dragon role: %s" % sorted(got))
    return _eq00(self, got, want, what)


HK.Child.eq = _eq


def _model():
    av = sys.argv
    sys.argv = [av[0]]
    import balance_model as BM
    sys.argv = av
    return BM


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.12 - build script') and g.count('VERSION = "0.4.12"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") + 2, "S two new systems, no new command")
    K.check(g.count("= cls(") == o.count("= cls(") + 3 and all(x in g for x in ('fgt = cls("PetFight")', 'fsys = cls("PetFightSys", T["DES"])', 'gsys = cls("PetGuardSys", T["DES"])',
            'pool.makeInterface(PKG + ".PetFightApi")')), "S the new classes: PetFight, PetFightSys, PetGuardSys + PetFightApi")
    K.check("if (slot == 2 && @PKG@.PetDragon.isDragon(v.kind)) @PKG@.PetFight.track(v);" in g and "@PKG@.PetFight.OWNHIT.remove(u);" in g,
            "S review fixes: a summoned dragon is tracked at spawn, a leaver's hit average forgotten")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(x for x in set(z.namelist()) - set(oz.namelist()) if not x.endswith(".class")), [], "S no new non-class entry in the jar")
    rd, ro = json.loads(z.read(ROLE)), json.loads(oz.read(ROLE))
    ro2 = dict(ro)
    ro2["Invulnerable"] = False
    K.check(rd == ro2 and ro["Invulnerable"] is True and rd["DefaultPlayerAttitude"] == "Ignore" and rd["MotionControllerList"][0]["MaxWalkSpeed"] == 8,
            "S the dragon role = 0.4.11's with Invulnerable false (PetGuardSys cancels every hit itself)")
    BM = _model()
    sh = ", ".join("%s=%s" % (k, "%g" % v) for k, v in BM.P5_DRAGON_SHARE.items())
    K.check(("DRAGON_SHARE_DEF = %r" % sh) in g and ("DRAGON_STAGE_DEF = %r" % ",".join("%g" % x for x in BM.P5_DRAGON_STAGE)) in g,
            "S the generated script carries the model's shares + stage factors: %s" % sh)
    K.check(all(r[2] for r in BM.p5_dragon_rows()), "S tools/balance_model.py dragon rows all pass (the summoned dragon on the P5 pet budget)")
    man = json.loads(z.read("manifest.json"))
    K.check("Summoned dragons fight next to you." in json.dumps(man) and "Fighting comes in a later version." not in json.dumps(man), "S the manifest text")
    K.save()


# ======================================================================================================== M: the row maths
def run_m(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "m")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Fg, Cfg = P_("PetFight"), P_("PetsCfg")
    BM = _model()
    K.check(bool(Cfg.DRAGON_FIGHT) and str(Cfg.DRAGON_FMODE) == "follow" and abs(float(Cfg.DRAGON_EVERY) - 1.5) < 1e-9 and int(Cfg.DRAGON_RANGE) == 12
            and abs(float(Cfg.DRAGON_REACH) - 4.5) < 1e-9 and str(Cfg.DRAGON_HP) == "40,60,80,100" and int(Cfg.DRAGON_HEAL) == 10
            and str(Cfg.DRAGON_STAGEDMG) == "40,60,80,100", "M the 9 rows' defaults")
    d = str(Cfg.DEFAULT_TEXT)
    K.check(all(("\n%s=" % k) in d for k in ("pets.dragon.fight", "pets.dragon.fight.mode", "pets.dragon.fight.share", "pets.dragon.stageDamage", "pets.dragon.fight.every",
                                            "pets.dragon.fight.range", "pets.dragon.fight.reach", "pets.dragon.hp", "pets.dragon.fight.heal")), "M the default file carries the 9 rows")
    worst = 0.0
    n = 0
    for k in KINDS:
        for L in (1, 3, 4, 6, 7, 9, 10, 25, 50, 77, 100):
            for ri in range(2, 6):
                for rb in (0, 1, 5):
                    got = float(Fg.share(k, L, ri + 1, rb))
                    want = BM.p5_dragon_share(k, L, ri, rb)
                    worst = max(worst, abs(got - want))
                    n += 1
    K.check(worst < 1e-9, "M PetFight.share = balance_model p5_dragon_share on %d points (worst %.2e)" % (n, worst))
    K.check(abs(float(Fg.share("DragonPlain", 100, 3, 0)) - 0.23) < 1e-12 and float(Fg.share("Wolf", 50, 3, 0)) == 0.0 and float(Fg.share(None, 50, 3, 0)) == 0.0,
            "M share: Plain Lv 100 Rare = 23 %, not a dragon = 0")
    K.check(max(abs(float(Fg.p4hit(L)) - BM.p4_hit(L)) / BM.p4_hit(L) for L in BM.P4_LEVELS) < 1e-3 and abs(float(Fg.p4hit(0)) - BM.p4_hit(1)) < 0.01
            and abs(float(Fg.p4hit(500)) - BM.p4_hit(100)) < 0.01 and BM.p4_hit(5) < float(Fg.p4hit(7)) < BM.p4_hit(10), "M p4hit = balance_model p4_hit (21 points, linear between, clamped)")
    # the hooks
    K.check(Fg.checkShare("k", str(Cfg.DRAGON_SHARE)) is None and Fg.checkShare("k", "-") is None and Fg.checkShare("k", None) is None
            and "not a dragon" in str(Fg.checkShare("k", "Wolf=10")) and "twice" in str(Fg.checkShare("k", "DragonFire=1, dragonfire=2"))
            and "needs" in str(Fg.checkShare("k", "DragonFire")) and "percent" in str(Fg.checkShare("k", "DragonFire=abc")) and "percent" in str(Fg.checkShare("k", "DragonFire=2000")),
            "M checkShare")
    K.check(Fg.checkStages("k", "40,60,80,100") is None and Fg.checkStages("k", "1,2,3") is not None and Fg.checkStages("k", "1,2,3,x") is not None
            and Fg.checkStages("k", "1,2,3,-4") is not None and Fg.checkStages("k", None) is None, "M checkStages")
    # live edits
    Cfg.DRAGON_SHARE = "DragonPlain=50"
    K.check(abs(float(Fg.shareOf("DragonPlain")) - 50.0) < 1e-9 and abs(float(Fg.shareOf("DragonSky")) - 28.0) < 1e-9 and abs(float(Fg.shareOf("dragonfire")) - 25.5) < 1e-9,
            "M a live share edit; an unlisted kind = its built-in share")
    Cfg.DRAGON_SHARE = "-"
    K.check(abs(float(Fg.shareOf("DragonStorm")) - 22.0) < 1e-9, "M share - = all built-in")
    Cfg.DRAGON_STAGEDMG = "10,20,30,200"
    K.check(abs(float(Fg.share("DragonPlain", 100, 3, 0)) - 0.46) < 1e-9 and abs(float(Fg.share("DragonPlain", 1, 3, 0)) - 0.23 * 0.01 * 0.1) < 1e-12, "M a stage edit")
    Cfg.DRAGON_STAGEDMG = "broken"
    K.check(abs(float(Fg.share("DragonPlain", 100, 3, 0)) - 0.23) < 1e-12, "M a broken stage text = the built-in numbers")
    Cfg.reloadAll()
    K.check(abs(float(Fg.hpFrac(1)) - 0.4) < 1e-9 and abs(float(Fg.hpFrac(4)) - 1.0) < 1e-9 and abs(float(Fg.hpFrac(9)) - 1.0) < 1e-9, "M health by stage")
    Cfg.DRAGON_EVERY = 0.1
    K.check(int(Fg.everyMs()) == 500, "M bite time clamped >= 0.5 s")
    Cfg.reloadAll()
    # the hit average
    u = W["UUID"].fromString("00000000-0000-0000-0000-000000009701")
    Fg.ema(u, 30.0, 1000)
    Fg.ema(u, 1000.0, 2000)          # an ability spike: counted as 3 x 30
    K.check(abs(float(Fg.ownerHit(u, 2000)) - (30 * 0.7 + 90 * 0.3)) < 1e-9, "M the hit average: 30 %% new, a spike capped at 3x: %.2f" % float(Fg.ownerHit(u, 2000)))
    K.check(float(Fg.ownerHit(u, 2000 + 300001)) == 0.0 and float(Fg.ownerHit(None, 0)) == 0.0, "M older than 5 min = none")
    Fg.ema(u, 12.0, 2000 + 400000)
    K.check(abs(float(Fg.ownerHit(u, 2000 + 400000)) - 12.0) < 1e-9, "M a stale average restarts at the new hit")
    Fg.ema(u, -5.0, 5)
    Fg.ema(u, float("inf"), 5)
    K.check(abs(float(Fg.ownerHit(u, 2000 + 400000)) - 12.0) < 1e-9, "M negative / infinite hits ignored")
    # dragond1fix: your damage PER SECOND = the hit average / the average time between hits (starts at the P4 reference gap)

    G0 = float(Fg.REF_GAP_MS)
    K.check(abs(G0 - 1000.0 * BM.P4_REF_HIT / BM.P4_REF_DPS) < 0.01, "M the reference gap = P4 hit / P4 DPS (%.1f ms)" % G0)
    u2 = W["UUID"].fromString("00000000-0000-0000-0000-000000009702")
    Fg.ema(u2, 40.0, 10000)
    K.check(abs(float(Fg.ownerDps(u2, 10000)) - 40.0 * 1000.0 / G0) < 1e-6, "M a first hit: your DPS = 40 / the reference gap (%.2f)" % float(Fg.ownerDps(u2, 10000)))
    Fg.ema(u2, 40.0, 11000)          # 1 s later: the gap average moves 30 % toward 1000 ms
    g1 = G0 * 0.7 + 1000.0 * 0.3
    K.check(abs(float(Fg.ownerDps(u2, 11000)) - 40.0 * 1000.0 / g1) < 1e-6, "M a 1 s gap: DPS = 40 / %.1f ms" % g1)
    Fg.ema(u2, 40.0, 11020)          # 20 ms = the same swing (an area hit): the gap average unchanged
    K.check(abs(float(Fg.ownerDps(u2, 11020)) - 40.0 * 1000.0 / g1) < 1e-6, "M a gap under 0.1 s does not count")
    Fg.ema(u2, 40.0, 20000)          # 9 s = counts as 3 s (review fix: a slow hitter's pace, not skipped)
    g2 = g1 * 0.7 + 3000.0 * 0.3
    K.check(abs(float(Fg.ownerDps(u2, 20000)) - 40.0 * 1000.0 / g2) < 1e-6, "M a gap over 3 s counts as 3 s (%.1f ms)" % g2)
    u3 = W["UUID"].fromString("00000000-0000-0000-0000-000000009703")
    for _k in range(30):
        Fg.ema(u3, 40.0, 50000 + 3500 * _k)          # a hit every 3.5 s
    g3 = 1000.0 * 40.0 / float(Fg.ownerDps(u3, 50000 + 3500 * 29))
    K.check(2990.0 < g3 <= 3000.0, "M hits every 3.5 s: the gap average moves to 3000 ms (%.1f; was stuck at %.0f before the fix)" % (g3, G0))
    K.check(float(Fg.ownerDps(u2, 20000 + 300001)) == 0.0 and float(Fg.ownerDps(None, 0)) == 0.0, "M DPS older than 5 min / no owner = none")
    # the tables
    K.eq([str(Fg.causeId(e)) for e in ("Earth", "Thunder", "Water", "Fire", "Air")], ["Earth", "Lightning", "Water", "Fire", "Wind"], "M the element damage causes (tools/skyyelem.py)")
    K.check(Fg.causeId(None) is None and Fg.causeId("Ice") is None and str(Fg.fxOf("Fire")) == "Fire_Staff_Activation" and str(Fg.fxOf(None)) == "Impact_Critical", "M causes / effects")
    K.eq([str(Fg.animOf(m)) for m in ("Nestkeeper_Dragon_Plain_1", "Nestkeeper_Dragon_Tundra_4", "Dragon_Fire", "Skyy_Dragon_Storm", "Skyy_Dragon_Sky", "Fox", None)],
         ["Alerted", "Alerted", "Jump", "Jump", "Jump", "", ""], "M the bite animations (non-looping; Aures' from their zip at build time)")
    K.check(all(bool(Fg.isPetRole(r)) for r in ("Skyy_Pet_Walk", "Skyy_Pet_Dragon", "Test_Pet", "Test_Fly", "Tamed_Horse", "Undead_Ally", "SLB_Knight_Ally"))
            and not any(bool(Fg.isPetRole(r)) for r in ("Trork_Warrior", "Dragon_Fire", None)), "M never: pets, tamed, *_Ally roles")
    K.eq([str(Fg.pct(x)) for x in (2.3, 110.0, -1.0, float("nan"))], ["2.3 %", "110 %", "0 %", "0 %"], "M pct")
    K.save()


# ======================================================================================================== F: the fight on a stand-in world
def run_f(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "f")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JFloat, JObject
    P_ = lambda n: JClass(PKG + n)
    Dg, Cfg, Views, PW, Store, Ops, Fg = P_("PetDragon"), P_("PetsCfg"), P_("PetViews"), P_("PetWorld"), P_("PetStore"), P_("PetOps"), P_("PetFight")
    told = []
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                      "nameOf": lambda u: "Rider", "tell": lambda u, t, c: told.append(str(t))})
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.server.core.universe.world.World")
    Dmg, ES = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage"), JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    UUID = W["UUID"]
    st = U.allocateInstance(Store_.class_)
    st2 = U.allocateInstance(Store_.class_)
    w = U.allocateInstance(World.class_)
    ents, jobs, calls = {}, [], []
    nxt = [100]

    def new_ref(uuid, role, pos, hp=(100.0, 0.0, 100.0), player=None, inv=False, store=None):
        nxt[0] += 1
        r = Ref(store or st, nxt[0])
        ents[int(r.getIndex())] = {"uuid": uuid, "role": role, "pos": list(pos), "removed": False, "ref": r, "hp": list(hp), "player": player, "inv": inv, "dead": False}
        return r
    ent = lambda r: None if r is None else ents.get(int(r.getIndex()))
    uo = UUID.fromString("00000000-0000-0000-0000-000000009801")
    oref = new_ref(uo, None, [10.0, 70.0, 10.0], player=uo)
    roles = {"Skyy_Pet_Walk": 11, "Skyy_Pet_Fly": 12, "Skyy_Pet_Dragon": 13, "Test_Pet": 7, "Test_Fly": 8}

    def spawn(s, role, x, y, z, yaw, model):
        rn = [k for k, v in roles.items() if v == int(role)][0]
        r = new_ref(UUID.randomUUID(), rn, [float(x), float(y), float(z)])
        ent(r)["model"] = str(model)
        return r

    def pos(acc, r):
        e = ent(r)
        return None if e is None or e["removed"] else JArray(JDouble)(e["pos"])

    def remove(acc, r):
        e = ent(r)
        if e is None or e["removed"]:
            return False
        e["removed"] = True
        calls.append(("remove", e["role"]))
        return True
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": lambda m, s: JString("%s" % m), "modelPinned": lambda m, s, seed: JString("%s#%s" % (m, seed)),
           "spawn": spawn, "store": lambda w_: st, "ownerRef": lambda u_: oref if str(u_) == str(uo) else None, "refOf": lambda w_, u_: None,
           "execute": lambda w_, r_: (jobs.append(r_), True)[1], "pos": pos, "setPos": lambda *a: None,
           "teleport": lambda acc, r, x, y, z, yaw: (calls.append(("teleport", (ent(r) or {}).get("role"), round(float(x), 2), round(float(z), 2))), ent(r)["pos"].__setitem__(slice(0, 3), [float(x), float(y), float(z)]))[0],
           "dead": lambda acc, r: bool((ent(r) or {}).get("dead")), "uuid": lambda acc, r: (ent(r) or {}).get("uuid"), "roleOf": lambda acc, r: (ent(r) or {}).get("role"),
           "tags": lambda acc, r: JString(""), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None, "clearDebug": lambda acc, r: None,
           "mark": lambda acc, r, o: calls.append(("mark", (ent(r) or {}).get("role"), (ent(o) or {}).get("role") or "owner")), "remove": remove,
           "hearts": lambda *a: None, "anim": lambda acc, r, a: calls.append(("anim", str(a))), "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: 1.55 if "Plain_4" in str(mid) else 1.0, "fx": lambda acc, i, x, y, z: calls.append(("fx", str(i))),
           "passthrough": lambda acc, r, m: JString("all")}
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)
    hits = []
    hit_ok = [True]

    def hit(cb, t, src, cause, amt):
        if not hit_ok[0]:
            return False
        hits.append((ent(t)["role"], ent(src)["role"], None if cause is None else str(cause), round(float(amt), 4)))
        return True

    def health(acc, r):
        e = ent(r)
        return None if e is None or e["hp"] is None else JArray(JFloat)(e["hp"])
    fapi = {"hit": hit, "health": health, "playerOf": lambda acc, r: (ent(r) or {}).get("player"), "guarded": lambda acc, r: bool((ent(r) or {}).get("inv"))}
    Fg.API = JProxy(PKG + "PetFightApi", dict=fapi)
    Cfg.SPAWN_DELAY = 0
    Cfg.SLOT2_MODE = "always"
    W["names"][str(uo)] = "Rider"
    key = str(Store.pkey(uo))
    Store.KEYOF.put(uo, key)
    r = Store.get(key)
    r.set("starter", "1")
    pid = str(Ops.create(r, None, "DragonPlain", 3, 10, 0, "test", "harness", False))
    r.set("active.2", pid)
    clock = [0]

    def second(plus=1000):
        clock[0] += plus
        Fg.NOW_OFF = clock[0]
        Views.second(uo, oref, st, None, w, "default")
        while jobs:
            jobs.pop(0).run()
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))
    second(0)
    second(0)
    v = Views.view(uo, 2)
    K.check(v is not None and str(v.kind) == "DragonPlain" and int(Fg.DVIEWS.size()) == 1 and abs(float(v.fhpMax) - 110.0) < 1e-6 and abs(float(v.fhp) - 110.0) < 1e-6,
            "F the summoned Lv 10 Plain dragon is tracked, health 100 %% x 1.1 of your 100: %s / %s" % (v and v.fhp, v and v.fhpMax))
    dref = v.ref
    ent(dref)["pos"] = [12.0, 70.0, 10.0]
    mob = new_ref(UUID.randomUUID(), "Trork_Warrior", [18.0, 70.0, 10.0], hp=(80.0, 0.0, 80.0))
    now = lambda: int(Fg.now())

    def dmg(src, amt):
        return Dmg(ES(src), 0, float(amt))
    # ---- your hit = its target + your hit average
    d1 = dmg(oref, 30.0)
    Fg.inspect(None, mob, d1)
    K.check(v.ftgt == mob and str(v.fwhy) == "you hit it" and int(v.fpri) == 2 and abs(float(Fg.ownerHit(uo, now())) - 30.0) < 1e-9 and int(Fg.ASSISTS.get()) == 1,
            "F you hit a Trork: its target (assist) + your hit average 30")
    calls[:] = []
    second()
    K.check(("mark", "Skyy_Pet_Dragon", "Trork_Warrior") in calls and not hits, "F out of reach (6 blocks > 4.5 + size): it walks to it (marked), no bite: %s" % calls)
    second()
    calls[:] = []
    second()
    tele = [c for c in calls if c[0] == "teleport"]
    K.check(len(tele) == 1 and tele[0][1] == "Skyy_Pet_Dragon" and int(Fg.LUNGES.get()) == 1, "F 3 s out of reach: one lunge next to it: %s" % tele)
    dpos = ent(dref)["pos"]
    K.check(math.dist(dpos, ent(mob)["pos"]) <= float(Fg.reach(v)) + 1e-6, "F ... now within reach (%.2f <= %.2f)" % (math.dist(dpos, ent(mob)["pos"]), float(Fg.reach(v))))
    calls[:] = []
    second()
    KD = 1000.0 / float(Fg.REF_GAP_MS)          # dragond1fix: one hit -> damage per second at the reference gap
    want = 30.0 * KD * 0.23 * 0.10 * 1.0 * 1.5
    K.check(len(hits) == 1 and hits[0][:3] == ("Trork_Warrior", "Skyy_Pet_Dragon", "Earth") and abs(hits[0][3] - round(max(1.0, want), 4)) < 1e-4,
            "F the bite: the Trork, from the dragon, Earth cause, %.3f (your 30 a hit / 0.45 s x 2.3 %% x 1.5 s, at least 1): %s" % (want, hits))
    K.check(("fx", "Block_Hit_Dirt") in calls and ("anim", "Alerted") in calls and int(Fg.BITES.get()) == 1, "F the Earth effect + the Alerted animation: %s" % calls)
    second(1000)
    K.check(len(hits) == 1, "F 1 s later: no bite yet (every 1.5 s)")
    second(1000)
    K.check(len(hits) == 2, "F 2 s later: the next bite")
    # the amount: a stronger owner, the mob's affinity, the P4 fallback
    Fg.OWNHIT.clear()
    Fg.ema(uo, 1000.0, now())
    r.set("pet.%s.level" % pid, "50")
    W["BR"].put("mob:fn:elem", JProxy("java.util.function.Function", dict={"apply": lambda a: JClass("java.lang.Integer").valueOf(25 if str(a[0]) == "Trork_Warrior" and str(a[1]) == "Earth" else 0)}))
    a50 = float(Fg.amount(v, r, mob, None, now()))
    K.check(abs(a50 - 1000.0 * KD * 0.23 * 0.5 * 1.5 * 1.25) < 1e-6, "F Lv 50, your hit 1000 (/ 0.45 s), the Trork weak to Earth (+25 %%): %.2f" % a50)
    Fg.OWNHIT.clear()
    W["BR"].put("mob:fn:level", JProxy("java.util.function.Function", dict={"apply": lambda u_: JClass("java.lang.Integer").valueOf(50)}))
    fb0 = int(Fg.FALLBACK.get())
    af = float(Fg.amount(v, r, mob, None, now()))
    K.check(abs(af - float(Fg.p4hit(50)) * KD * 0.23 * 0.5 * 1.5 * 1.25) < 1e-6 and int(Fg.FALLBACK.get()) == fb0 + 1, "F no hit of yours yet: the P4 DPS at the mob's level 50 (%.1f)" % af)
    sh0 = Cfg.DRAGON_SHARE
    Cfg.DRAGON_SHARE = JString("DragonPlain=0")
    K.check(float(Fg.amount(v, r, mob, None, now())) == 0.0, "F a 0 %% share: amount 0 (review fix: no 1-damage floor; bite() skips 0)")
    Cfg.DRAGON_SHARE = sh0
    W["BR"].remove("mob:fn:elem")
    W["BR"].remove("mob:fn:level")
    r.set("pet.%s.level" % pid, "10")
    Fg.ema(uo, 30.0, now())
    # ---- the kill credit: our lethal bite's source -> the owner; a non-lethal one stays the dragon
    dk = dmg(dref, 5.0)
    Fg.MINE.put(dk, v)
    Fg.inspect(None, mob, dk)
    K.check(dk.getSource().getRef() == dref and int(Fg.KILLS.get()) == 0, "F a bite that does not kill: the source stays the dragon")
    ent(mob)["hp"] = [0.0, 0.0, 80.0]
    Fg.inspect(None, mob, dk)
    K.check(dk.getSource().getRef() == oref and int(Fg.KILLS.get()) == 1 and v.ftgt is None and str(v.fwhy) == "killed",
            "F the KILLING bite: its source is now YOU (kill XP / collections / loot / Spoils read it), the target dropped")
    dk2 = dmg(dref, 5.0)
    Fg.MINE.put(dk2, v)
    dk2.setCancelled(True)
    Fg.inspect(None, mob, dk2)
    K.check(dk2.getSource().getRef() == dref, "F a cancelled bite is never credited")
    # ---- never these targets
    def try_target(t, src_amt=20.0, cancel=False, src=None):
        Fg.drop(v, "reset")
        d_ = dmg(src or oref, src_amt)
        d_.setCancelled(cancel)
        Fg.inspect(None, t, d_)
        return v.ftgt == t
    pl = new_ref(UUID.randomUUID(), None, [13.0, 70.0, 10.0], player=UUID.randomUUID())
    pet = new_ref(UUID.randomUUID(), "Skyy_Pet_Walk", [13.0, 70.0, 10.0])
    tamed = new_ref(UUID.randomUUID(), "Tamed_Horse", [13.0, 70.0, 10.0])
    invu = new_ref(UUID.randomUUID(), "Kweebec_Merchant", [13.0, 70.0, 10.0], inv=True)
    dead = new_ref(UUID.randomUUID(), "Trork_Warrior", [13.0, 70.0, 10.0], hp=(0.0, 0.0, 50.0))
    far = new_ref(UUID.randomUUID(), "Trork_Warrior", [40.0, 70.0, 10.0])
    other = new_ref(UUID.randomUUID(), "Trork_Warrior", [13.0, 70.0, 10.0], store=st2)
    mob2 = new_ref(UUID.randomUUID(), "Skeleton_Archer", [14.0, 70.0, 10.0])
    K.eq([try_target(x) for x in (pl, pet, tamed, invu, dead, far, other)], [False] * 7,
         "F never a player / a pet / a tamed animal / an invulnerable NPC / a dead mob / a mob past the 12-block range / a mob in another world")
    K.check(not try_target(mob2, cancel=True) and not try_target(mob2, src_amt=0.0) and try_target(mob2), "F a cancelled / 0 hit is no assist; a real one is")
    # ---- Defend mode: what hits you (your own target wins)
    Fg.drop(v, "reset")
    hm = new_ref(UUID.randomUUID(), "Goblin_Scrapper", [12.0, 70.0, 12.0])
    Fg.inspect(None, oref, dmg(hm, 10.0))
    K.check(v.ftgt is None, "F Follow (default): a mob hitting you is not its target")
    Cfg.DRAGON_FMODE = "defend"
    Fg.inspect(None, oref, dmg(hm, 10.0))
    K.check(v.ftgt == hm and int(v.fpri) == 1 and str(v.fwhy) == "it hit you" and int(Fg.DEFENDS.get()) == 1, "F Defend: a mob that hits you")
    Fg.inspect(None, mob2, dmg(oref, 20.0))
    K.check(v.ftgt == mob2 and int(v.fpri) == 2, "F ... then you hit another mob: your target wins")
    Fg.inspect(None, oref, dmg(hm, 10.0))
    K.check(v.ftgt == mob2, "F ... and a mob hitting you does not take it away")
    Fg.inspect(None, oref, dmg(pet, 10.0))
    Fg.inspect(None, oref, dmg(pl, 10.0))
    K.check(v.ftgt == mob2, "F a pet / a player hitting you is never its target")
    Cfg.reloadAll()
    Cfg.SPAWN_DELAY, Cfg.SLOT2_MODE = 0, "always"
    # ---- the drop rules
    ent(oref)["pos"] = [10.0, 70.0, 10.0]
    ent(mob2)["pos"] = [10.0, 70.0, 30.0]
    second()
    K.check(v.ftgt is None and str(v.fwhy) == "too far from you", "F the target 20 blocks from you (> 12 + 4): dropped (%s)" % v.fwhy)
    ent(mob2)["pos"] = [14.0, 70.0, 10.0]
    Fg.inspect(None, mob2, dmg(oref, 20.0))
    ent(mob2)["pos"] = [40.0, 70.0, 40.0]
    ent(oref)["pos"] = [38.0, 70.0, 38.0]
    ent(dref)["pos"] = [10.0, 70.0, 10.0]
    hit_ok[0] = False          # its bites never land (stuck behind a wall, a creature that cannot be hurt)
    for _ in range(4):
        second(6000)
    hit_ok[0] = True
    K.check(v.ftgt is None and str(v.fwhy) == "nobody fights it", "F nobody hit it for 20 s (its bites never landed): dropped (%s)" % v.fwhy)
    ent(oref)["pos"] = [10.0, 70.0, 10.0]
    ent(dref)["pos"] = [12.0, 70.0, 10.0]
    ent(mob2)["pos"] = [13.0, 70.0, 10.0]
    Fg.inspect(None, mob2, dmg(oref, 20.0))
    Cfg.DRAGON_FIGHT = False
    second()
    K.check(v.ftgt is None and str(v.fwhy) == "off" and "Dragon fighting is off" in str(Fg.cardLine(r, pid)), "F Dragons fight off: it drops the target, the card says so")
    Fg.inspect(None, mob2, dmg(oref, 20.0))
    K.check(v.ftgt is None, "F ... and no new targets")
    Cfg.reloadAll()
    Cfg.SPAWN_DELAY, Cfg.SLOT2_MODE = 0, "always"
    # ---- the card
    cl = str(Fg.cardLine(r, pid))
    K.check(cl == "\nFights next to you in the summon slot: bites for 2.3 % of your damage (Earth), health 110 % of yours.", "F the card line: %r" % cl)
    tip = str(P_("PetsPage").tip(r, pid, 0))
    K.check("Fights next to you in the summon slot: bites for 2.3 %" in tip and "Riding and flying come in a later version." in tip and "Fighting, riding" not in tip, "F the pet card")
    K.check(str(Fg.cardLine(r, "nope")) == "" and str(Fg.cardLine(None, pid)) == "", "F not a dragon / no record: no line")
    # ---- PetGuardSys: every hit on the dragon cancelled; mob hits lower its pool, it hits back; refill; DOWN at 0
    Fg.drop(v, "reset")
    second(0)
    hp0 = float(v.fhp)
    g1 = dmg(pl, 50.0)
    Fg.guard(None, dref, g1)
    g2 = dmg(pet, 50.0)
    Fg.guard(None, dref, g2)
    g3 = Dmg(JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage").NULL_SOURCE, 0, 50.0)
    Fg.guard(None, dref, g3)
    K.check(all(bool(g.isCancelled()) and float(g.getAmount()) == 0.0 for g in (g1, g2, g3)) and abs(float(v.fhp) - hp0) < 1e-9 and v.ftgt is None,
            "F a player's / a pet's / a sourceless (fall, void) hit on the dragon: cancelled, its health unchanged, no target")
    g4 = dmg(hm, 40.0)
    Fg.guard(None, dref, g4)
    K.check(bool(g4.isCancelled()) and float(g4.getAmount()) == 0.0 and abs(float(v.fhp) - (hp0 - 40.0)) < 1e-9 and v.ftgt == hm and str(v.fwhy) == "it hit your dragon"
            and int(Fg.HURT.get()) == 1, "F a mob's hit: cancelled (the real health never moves), its pool 110 -> 70, it hits back")
    other_d = dmg(hm, 10.0)
    Fg.guard(None, mob, other_d)
    K.check(not bool(other_d.isCancelled()) and float(other_d.getAmount()) == 10.0, "F a hit on any other creature is untouched")
    second(5000)
    K.check(abs(float(v.fhp) - 70.0) < 1e-9, "F 5 s later: still 70")
    second(6000)
    K.check(abs(float(v.fhp) - 110.0) < 1e-9, "F 11 s without a mob hit: full again (110)")
    told[:] = []
    calls[:] = []
    Fg.guard(None, dref, dmg(hm, 200.0))
    left = int(Dg.downLeft(pid))
    K.check(int(Fg.DOWNS.get()) == 1 and 50000 < left <= int(Dg.downMs(10)) and ("remove", "Skyy_Pet_Dragon") in calls and Views.view(uo, 2) is None and bool(v.gone),
            "F 0 health = DOWN: the creature removed, back after the Lv 10 cooldown (%d ms)" % left)
    second(0)
    K.check(told == ["[Pets] Your dragon flew back to its summon slot - it comes back in 56 s."] and Views.want(uo, r, key, 2, "default", False) is None,
            "F one chat line, nothing spawns while DOWN: %s" % told)
    Dg.DOWN.clear()
    second(0)
    second(0)
    v2 = Views.view(uo, 2)
    K.check(v2 is not None and v2 is not v and abs(float(v2.fhp) - float(v2.fhpMax)) < 1e-9 and v2.ftgt is None, "F after the cooldown: back with full health, no old target")
    K.check(Fg.byRef(dref) is None and Fg.byRef(v2.ref) == v2, "F the gone view is no longer guarded; the new one is")
    # ---- the REAL seams never throw without an engine
    Fg.API = None
    PW.API = None
    K.check(Fg.health(None, oref) is None and Fg.playerOf(None, oref) is None and not bool(Fg.guarded(None, oref)) and not bool(Fg.tick(dmg(oref, 1.0))),
            "F the real health / playerOf / guarded / tick never throw (no engine)")
    f0 = int(Fg.FAILS.get())
    K.check(not bool(Fg.hitNow(None, mob, dref, "Earth", 5.0, v2)) and int(Fg.FAILS.get()) == f0 + 1, "F the real bite without an engine: false, counted, no throw")
    import re
    K.check(re.match(r"^dragons fight \(Follow\): bites [0-9]+, kills credited 1, ", str(Fg.text())) is not None, "F the ready-line text: %s" % Fg.text())
    K.check(str(Fg.census()).startswith("dragon fight: 0 / 5 element damage causes"), "F the census line (no assets here): %s" % Fg.census())
    Fg.clear()
    K.check(int(Fg.DVIEWS.size()) == 0 and int(Fg.OWNHIT.size()) == 0, "F clear() at shutdown")
    K.save()


# ======================================================================================================== 0.4.11's DG with the 0.4.12 card text
def run_dg(out, jar, scratch, home):
    src = inspect.getsource(T411.run_dg)
    old = '''and "Fighting, riding and flying come in a later version." in tip'''
    assert src.count(old) == 1
    src = src.replace(old, '''and "Riding and flying come in a later version." in tip and "Fights next to you in the summon slot: bites for 0.1 %" in tip''')
    ns = dict(T411.__dict__)
    exec(compile(src, T411.__file__, "exec"), ns)
    ns["run_dg"](out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("m", run_m), ("f", run_f), ("dg", run_dg), ("vw", T411.run_vw), ("st", T411.run_st),
                   ("el410", T410.run_el), ("live", T411.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
