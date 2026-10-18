"""Harness for SkyyClasses 0.1.38 (round pa4: Mage PA4 Meteor from the Rift; tools/classes_0_1_38_patch.py). Build first:
    python tools/classes_0_1_38_patch.py && python SkyyClasses/build_skyyclasses_0.1.38.py
    python SkyyClasses/test_skyyclasses_0.1.38.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/pa4/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.37 -> 0.1.38: exactly the planned members (EXPECT) + Pa4Task / Pa4Fn; non-class entries = manifest.json only
  X   exec     on the engine stand-ins of test_skyyclasses_0.1.25.py (its N0 set-up), through Pa4Fn (= what SkyyArmory 0.1.32 calls with
               its Object[8] landing record): X1 the gates (bad records, rows off, class, node, slot, world) answer without casting;
               X2 the rift Meteor: queued + cast through the normal pipeline at the landing spot, same Mana as a Meteor, cooldown armed,
               0.5 s fall, -10 % damage; every Meteor -10 % with the node; X3 refusals are silent for the rift cast only, rows off / 100 %;
               X4 the bridge key + tree:reads in the plugin
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order): nothing written; the live folder only read
  AA  engine-access audit
"""
import os, sys, json, shutil, zipfile, textwrap, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION, OLD = "0.1.38", "0.1.37"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "pa4", "cls")
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
T25 = os.path.join(HERE, "test_skyyclasses_0.1.25.py")
ADDED = ["Pa4Task", "Pa4Fn"]
EXPECT = {
    "Abil": ["+f PA4_AT", "+f LAST_PA4_WHY", "+f PA4_HEARD", "+f PA4_QUEUED", "+f PA4_CASTS", "+f LAST_PA4", "~<clinit>",
             "+m pa4Bridge", "+m pa4Target", "+m pa4Slot", "+m pa4Gate", "+m pa4Land", "+m pa4Cast", "~m castAt0", "~m refuse", "~m click", "~m treeApply"],
    "AbilCfg": ["+f M_RIFT_TGT", "+f M_RIFT_ON", "+f M_RIFT_P", "+f M_RIFT_D", "~<clinit>", "~m read"],   # the 3 rows
    "SkyyClassesPlugin": ["~m setup", "~m shutdown"],                                   # the bridge key, tree:reads, the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "KitMigrate": ["~m runOnce"],   # the version text (+ the rows)
    "CfgFile": ["~<clinit>"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "ClassCfg": ["~<clinit>"],   # the 3 new rows in the kit tables + default file
}


def long_ok(AS, mu):
    try:
        return int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) > 0
    except Exception:
        return False


def run_exec(out, jar, scratch, _home):
    stats_zip = os.path.join(scratch, "stats.zip")
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as zi, \
            zipfile.ZipFile(stats_zip, "w") as zo:
        for n in zi.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                zo.writestr(n, zi.read(n))
    lines = open(T25, encoding="utf8").read().split("\n")
    a = lines.index("def run_exec(out, jar, scratch, _home):") + 1
    b = [i for i, l in enumerate(lines) if l.strip() == "# ---------------- X1 the pure rules"][0]
    ns = {"out": out, "jar": jar, "scratch": scratch, "_home": _home, "HK": HK, "B": B, "PKG": PKG, "ASSETS": stats_zip, "os": os, "sys": sys,
          "json": json, "shutil": shutil, "zipfile": zipfile, "time": time, "__name__": "t25setup"}
    exec(compile(textwrap.dedent("\n".join(lines[a:b])), T25 + " (N0 set-up)", "exec"), ns)
    g = lambda n: ns[n]
    K, C, ck = g("K"), g("C"), g("ck")
    from jpype import JArray, JObject, JString, JClass, JFloat
    A, AS, AC, AW = g("A"), g("AS"), g("AC"), g("AW")
    mu, mm, pu, MANA = g("mu"), g("mm"), g("pu"), g("MANA")
    TREE, HANDS, AIMS, reset_m, said, sv, cast, now_ms = g("TREE"), g("HANDS"), g("AIMS"), g("reset_m"), g("said"), g("sv"), g("cast"), g("now_ms")
    SOUNDS, unthrottle = g("SOUNDS"), g("unthrottle")
    ci_m, ci_p = g("ci_m"), g("ci_p")
    UUID, Dbl, Lng, Bool = JClass("java.util.UUID"), JClass("java.lang.Double"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    fn = C("Pa4Fn")()
    br, NEARL, npc = g("br"), g("NEARL"), g("npc")
    br.put("armory:blinkland", "1")   # SkyyArmory 0.1.32 is there
    foe = npc(501, 33.5, 70.0, -7.5)
    NEARL.append(foe)                 # an enemy within the Meteor radius of the landings below
    aw = AW.of("abil-test")

    def rec(u_, x=20.5, y=64.0, z=0.5, world="abil-test"):
        return JArray(JObject)([u_, None if world is None else JString(world), Dbl(x), Dbl(y), Dbl(z), Lng(now_ms()), Dbl(16.0), Bool(False)])

    def land(r_):
        v_ = fn.apply(r_)
        return None if v_ is None else str(v_)

    def dmg(r_):
        i_ = r_.find(" damage=")
        return float(r_[i_ + 8:].split()[0]) if i_ >= 0 else None

    def tree(csv):
        TREE["csv"] = csv
        AS.TREEC.clear()

    # ---------------- X1 the gates (nothing cast, nothing said)
    reset_m()
    aw.jobs.clear()
    tree("A1,PA4")
    ck(land(None) == "bad" and land(JArray(JObject)(3)) == "bad" and land(JString("x")) == "bad", "X1: no / short / wrong record -> bad")
    ck(land(rec(mu, x=float("nan"))) == "bad", "X1: a NaN landing -> bad")
    AC.M_RIFT_ON = False
    ck(land(rec(mu)) == "off", "X1: ab.Meteor.rift off -> off")
    AC.M_RIFT_ON = True
    AC.PART = False
    ck(land(rec(mu)) == "off", "X1: class abilities off -> off")
    AC.PART = True
    ck(land(rec(pu)) == "class", "X1: a Priest's blink -> class (Mages only)")
    ck(land(rec(UUID.fromString("00000000-0000-0000-00ab-000000009999"))) == "class", "X1: a player with no class -> class")
    tree("A1")
    ck(land(rec(mu)) == "node", "X1: no PA4 in the class tree -> node")
    tree(None)
    ck(land(rec(mu)) == "node", "X1: class trees off / no SkyyTrees (null csv) -> node (a path node needs the tree)")
    tree("A1,PA4")
    ck(int(A.pa4Slot(mu, ci_m)) == 0 and int(A.pa4Slot(pu, ci_p)) == -1 and int(A.pa4Slot(None, 0)) == -1,
       "X1: pa4Slot: the Mage's Meteor is on slot 1 (index 0); a Priest's slots have none")
    ck(str(A.pa4Gate(mu, "A1,PA4")) == "ok:0" and str(A.pa4Gate(mu, "A1")) == "node" and str(A.pa4Gate(pu, "A1,PA4")) == "class",
       "X1: pa4Gate")
    ck(land(rec(mu, world="another-world")) == "world", "X1: a landing in another world than the caster's -> world")
    jobs0 = int(aw.jobs.size())
    ck(sv(mm, MANA) == 400.0 and not said() and jobs0 == 0, "X1: nothing was paid, said or queued by the gates (%s jobs)" % jobs0)

    # ---------------- X2 the rift Meteor vs a plain Meteor
    reset_m()
    aw.jobs.clear()
    tree("A1")
    r_plain = cast("Mage1", "1")
    m_plain = 400.0 - sv(mm, MANA)
    d_plain = dmg(r_plain)
    ck(r_plain.startswith("ok:Meteor") and d_plain and d_plain > 0, "X2: a plain Meteor without the node: %s" % r_plain[:160])
    reset_m()
    aw.jobs.clear()
    tree("A1,PA4")
    r_node = cast("Mage1", "1")
    ck(dmg(r_node) is not None and abs(dmg(r_node) - 0.9 * d_plain) < 1e-6, "X2: with PA4 EVERY Meteor deals 90 %% (the trade-off): %s vs %s" % (dmg(r_node), d_plain))
    j_ = [j for j in list(aw.jobs) if int(j.kind) == 1]
    ck(j_ and abs((int(j_[0].at) - now_ms()) - 1000) < 300 and abs(float(j_[0].x) - float(AIMS["spot"][0])) < 1e-9,
       "X2: ... the walking Meteor still falls where you look after 1 s")
    reset_m()
    aw.jobs.clear()
    h0, q0, c0 = int(A.PA4_HEARD), int(A.PA4_QUEUED), int(A.PA4_CASTS)
    t_ = now_ms()
    r_ = land(rec(mu, 33.5, 70.0, -7.5))
    last = str(A.LAST_PA4)
    ck(r_ == "queued:0", "X2: a Mage with PA4 + Meteor slotted -> queued on the world (slot 1): %s" % r_)
    ck(last.startswith("ok:Meteor") and last.find(" rift") > 0, "X2: ... cast through the normal pipeline (door 3 = rift): %s" % last[:200])
    ck(dmg(last) is not None and abs(dmg(last) - 0.9 * d_plain) < 1e-6, "X2: ... at 90 %% damage: %s" % dmg(last))
    ck(abs((400.0 - sv(mm, MANA)) - m_plain) < 1e-6 and m_plain > 0, "X2: ... the same Mana as a Meteor (%s)" % m_plain)
    ck(" at=33.5,70,-7.5" in last, "X2: ... at the landing spot, not the aim (%s)" % last[last.find(" at="):][:30])
    j_ = [j for j in list(aw.jobs) if int(j.kind) == 1]
    ck(j_ and abs(float(j_[0].x) - 33.5) < 1e-9 and abs(float(j_[0].y) - 70.0) < 1e-9 and abs(float(j_[0].z) + 7.5) < 1e-9,
       "X2: the impact job sits on the landing")
    ck(j_ and abs((int(j_[0].at) - t_) - 500) < 300, "X2: ... and falls in ab.Meteor.riftDelay 0.5 s (%s ms)" % (j_ and (int(j_[0].at) - t_)))
    ck(int(A.PA4_HEARD) - h0 == 1 and int(A.PA4_QUEUED) - q0 == 1 and int(A.PA4_CASTS) - c0 == 1, "X2: counters heard / queued / cast +1")
    lines_ = said()
    ck(any(l.startswith("Meteor from the Rift!") for l in lines_), "X2: the cast line names it: %s" % lines_[:2])
    ck(A.PA4_AT.isEmpty(), "X2: the landing spot is dropped after the cast")
    ck(bool(A.pa4Bridge()), "X2: pa4Bridge sees armory:blinkland")
    ck(long_ok(AS, mu), "X2: the Meteor cooldown is armed")

    # ---------------- X3 refusals: silent for the rift cast, normal for a key cast
    unthrottle()
    SOUNDS.clear()
    m1 = sv(mm, MANA)
    r3 = land(rec(mu))
    ck(r3 == "queued:0" and str(A.LAST_PA4).startswith("cooldown") and not said() and SOUNDS.size() == 0 and sv(mm, MANA) == m1,
       "X3: a blink while Meteor cools down -> no Meteor, no line, no sound, nothing paid (%s)" % str(A.LAST_PA4)[:60])
    unthrottle()
    r4 = cast("Mage1", "1")
    ck(r4 == "cooldown" and said(), "X3: a key cast on cooldown still says so (only the rift cast is muted): %s" % r4)
    reset_m()
    HANDS[1] = "Weapon_Sword_Iron"
    m1 = sv(mm, MANA)
    land(rec(mu))
    ck(str(A.LAST_PA4).startswith("weapon") and not said() and sv(mm, MANA) == m1, "X3: no class weapon in hand -> no Meteor, silent: %s" % str(A.LAST_PA4)[:60])
    HANDS[1] = "Weapon_Staff_Wood"
    reset_m()
    mm.setStatValue(MANA, JFloat(5.0))
    land(rec(mu))
    ck(str(A.LAST_PA4).startswith("mana") and not said() and sv(mm, MANA) == 5.0, "X3: too little Mana -> silent, nothing paid: %s" % str(A.LAST_PA4)[:40])
    reset_m()
    AC.M_RIFT_ON = False
    tree("A1,PA4")
    r5 = cast("Mage1", "1")
    ck(dmg(r5) is not None and abs(dmg(r5) - d_plain) < 1e-6, "X3: ab.Meteor.rift off -> the node does nothing (full Meteor damage again)")
    AC.M_RIFT_ON = True
    AC.M_RIFT_P = 100.0
    reset_m()
    r6 = cast("Mage1", "1")
    ck(dmg(r6) is not None and abs(dmg(r6) - d_plain) < 1e-6, "X3: ab.Meteor.riftPower 100 %% -> no trade-off")
    AC.M_RIFT_P = 90.0
    ck(abs(float(AC.M_RIFT_D) - 0.5) < 1e-9, "X3: the default fall time 0.5 s")

    # ---------------- X5 polish: a target is needed; the -10 % only with SkyyArmory's bridge
    reset_m()
    aw.jobs.clear()
    del NEARL[:]
    m1 = sv(mm, MANA)
    r7 = land(rec(mu))
    ck(r7 == "queued:0" and str(A.LAST_PA4).startswith("notarget") and sv(mm, MANA) == m1 and not said() and not long_ok(AS, mu)
       and int(aw.jobs.size()) == 0, "X5: no enemy at the landing -> no Meteor, nothing paid, no cooldown, silent: %s" % str(A.LAST_PA4)[:60])
    ck(bool(AC.M_RIFT_TGT), "X5: ab.Meteor.riftNeedsTarget defaults ON")
    AC.M_RIFT_TGT = False
    land(rec(mu))
    ck(str(A.LAST_PA4).startswith("ok:Meteor"), "X5: riftNeedsTarget off -> it falls on empty ground too: %s" % str(A.LAST_PA4)[:40])
    AC.M_RIFT_TGT = True
    reset_m()
    NEARL.append(g("PLAYERS")["Priest1"][1])   # another player (no PvP set up in the stand-ins) is not a valid target
    land(rec(mu))
    ck(str(A.LAST_PA4).startswith("notarget"), "X5: a non-hostile player at the landing is no target (the Meteor's own enemy rule): %s" % str(A.LAST_PA4)[:40])
    del NEARL[:]
    NEARL.append(foe)
    reset_m()
    land(rec(mu))
    ck(str(A.LAST_PA4).startswith("ok:Meteor"), "X5: the enemy back -> it falls again")
    br.remove("armory:blinkland")
    reset_m()
    r8 = cast("Mage1", "1")
    ck(not bool(A.pa4Bridge()) and dmg(r8) is not None and abs(dmg(r8) - d_plain) < 1e-6,
       "X5: SkyyArmory without the bridge (rolled back) -> no -10 %% on Meteor: %s vs %s" % (dmg(r8), d_plain))
    br.put("armory:blinkland", "1")

    # ---------------- X4 the bridge key + the reader contract in the plugin
    with zipfile.ZipFile(jar) as z_:
        pb = z_.read("com/skyy/classes/SkyyClassesPlugin.class")
    ck(b"armory:on:blink:SkyyClasses" in pb, "X4: the plugin puts / removes armory:on:blink:SkyyClasses")
    ck(b"Class.Mage.PA4" in pb, "X4: tree:reads:SkyyClasses lists Class.Mage.PA4 (SkyyTrees sells it)")
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(HK.tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = HK.tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = HK.tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(not ch and o["m32"] == "", "ST start %s on a scratch COPY of the live data: nothing written (%s)" % (step, ch))
    if step == "2":
        K.check(HK.tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("st1", run_st1), ("st2", run_st2)], script=__file__)
