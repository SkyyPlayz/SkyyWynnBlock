"""Harness for SkyyPets 0.4.27 (mount slot = ride only, the pet slot fights, eggs upgrade by rarity; tools/pets_0_4_27_patch.py). Build first:
    python tools/pets_0_4_27_patch.py && python SkyyPets/build_skyypets_0.4.27.py
    python SkyyPets/test_skyypets_0.4.27.py [--keep] [--expect-dump] [--dir <folder inside tools/dev/scratch/>]

  S       static   the patch re-runs to identical bytes; no class / system / command added; one row (pets.mount.summonCooldown); the jar adds and removes
                   nothing, changed non-class entries = manifest.json
  A/C/AA           (tools/harness_kit.py, -Xverify:all) verify, class compare 0.4.26 -> 0.4.27, engine-access audit
  SUMMON  EXECUTED on 0.4.25's stand-in world (real PetViews / PetRide / PetRideFn / PetFight): nothing in the mount slot until summoned; Summon -> ONE
                   creature right under you -> it seats you by itself (the F path's job) -> riding; pressed again = '=' (no 2nd creature, spawnNow refuses a
                   2nd); hop off -> it vanishes (once its role is back), the summon ends, the cooldown; relog / death / another world / the slot changed /
                   a ride refused / a ride that never took / a summon that cannot appear (15 s) / a creature-free world = the same end, never a 2nd
                   creature, nothing saved; a late spawn job after the end refuses; a Horse rides the same way; a fighter-only kind / a young dragon /
                   Pets off -> the reason; null for a non-UUID; the mount never fights
  PETSLOT EXECUTED: the dragon in the PET slot shows, is guarded (DVIEWS), is the one that takes targets (dragonOf), hunts + bites a hostile mob,
                   circles when idle, goes DOWN from the pet slot; the HUD line carries its health + Bite on the pet slot; a mount-slot view never fights
  EGGS    EXECUTED: Common crafted from scratch as before; Uncommon = the Common egg + the old Uncommon materials (the plain Egg is not taken any more);
                   no Common egg -> refused, nothing moves; double click -> exactly one upgrade; a full inventory -> everything back (Common egg
                   included); Void materials committed only after the egg; an open egg move of the Common egg -> refused; Rare -> not craftable
  IDLE/AGG  0.4.25's phases with the dragon in the PET slot (the slot that circles / hunts now); REAL/MIG/ECS/PT/live/live2: the older phases on this
                   jar; a check that tests the REMOVED summon-slot behaviour (F on the circling dragon to ride it, landing after a ride) is listed by name
                   as SUPERSEDED (notes), never silently dropped.
  NOT RUN ANY MORE (superseded whole, 0.4.27 removed what they drive): 0.4.24 RIDE and 0.4.23 RD - both start from "the slot-2 dragon is out on its
                   own" and ride it again and again with F (F again after getting off, landing, re-arming F). A mount slot creature now exists only
                   while summoned and vanishes when you get off; SUMMON covers that life end to end (summon, seat, off, refused, give-up, relog,
                   death, world change, slot change, cooldown). Unchanged code they also touched: pass-through / the shield (PT + ECS still run),
                   mountNow's checks (SUMMON's refused + give-up cases run them).
NOT COVERED (only the game can prove it): the client's seat animation right after the spawn; how fast the vanish looks; real mob hits on the pet-slot dragon.
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util, subprocess, inspect

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "pets1fix", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T425 = _mod(os.path.join(HERE, "test_skyypets_0.4.25.py"), "test_skyypets_0_4_25")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T424, T423, T417, T44, T41 = T425.T424, T425.T423, T425.T417, T425.T44, T425.T41

VERSION = "0.4.27"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.26.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.26.py")
PATCH = os.path.join(TOOLS, "pets_0_4_27_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T425.JAR = T424.JAR = T423.JAR = JAR
ADDED = []
EXPECT = {   # every class 0.4.27 changes (the version text baked into the config kit + migration lines; the new row; the summon / pet-slot / egg changes)
    'CfgFile': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'],
    'PetBuff': ['~m bmSeen', '~m lockedWhy'], 'PetDragon': ['~m card', '~m down', '~m resolve'], 'PetFight': ['~m cardLine', '~m dragonOf', '~m second'], 'PetHatchery': ['~<clinit>', '~m craft'],
    'PetHudFn': ['~m line'], 'PetIdle': ['~m second'], 'PetRide': ['+f OFF_MS', '+m settled', '~m cardLine', '~m rideLine', '~m second'],
    'PetRideFn': ['~m ride'], 'PetView': ['+f asked', '+f offAt', '+f rode'],
    'PetViews': ['+f CALLED', '+f CALL_MS', '+f COOL', '+f ENDS', '+f STALE', '+f SUMMONS', '+m call', '+m called', '+m coolLeft', '+m ended', '+m summonWhy', '~<clinit>',
                 '~m dropped', '~m leave', '~m onRemoved', '~m reconcile', '~m removeAll', '~m removeHere', '~m removeQueued', '~m second', '~m spawnNow', '~m steer',
                 '~m upkeep', '~m want'],
    'PetsCfg': ['+f MOUNT_CD', '~<clinit>', '~m applyAll', '~m applyScalars', '~m seed'],
    'PetsMigDrg': ['~m run'], 'PetsMigP5': ['~m mgLog', '~m run'], 'PetsMigS2': ['~m run'], 'PetsMigW15': ['~m run'],
    'PetsPage': ['~<clinit>', '~m build', '~m hint', '~m summonPart', '~m tip'], 'PetOps': ['~m admin', '~m enforceRoles', '~m loadoutSet', '~m slotName', '~m toSlot'], 'SkyyPetsPlugin': ['~m setup'],          # + pets1fix F3 texts
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

# 0.4.25's MIG phase names its own version in the Changes line it expects: the same phase, with this version
_src = inspect.getsource(T425.run_mig)
assert _src.count(r"\tSkyyPets 0.4.25\t") == 1, "0.4.25's MIG phase changed"
exec(compile(_src.replace(r"\tSkyyPets 0.4.25\t", r"\tSkyyPets 0.4.27\t"), T425.__file__, "exec"), T425.__dict__)

# ---- SUPERSEDED: an older check that tests the summon-slot behaviour 0.4.27 REPLACES (Skyy 2026-11-14) is noted by name, never a silent pass
SUPERSEDED = [          # (phase label, check text prefix, why) - every entry read by hand from the first run on this jar
    ("idle", "IDLE F: the mount job", "F rides only the MOUNT slot creature; the circling dragon is the pet slot one now - SUMMON covers the ride"),
    ("idle", "IDLE mounting (rideAt set)", "no ride from the pet slot"),
    ("idle", "IDLE it took", "no ride from the pet slot"),
    ("idle", "IDLE while ridden", "no ride from the pet slot"),
    ("idle", "IDLE you get off: it lands", "a mount vanishes when you get off (SUMMON), nothing lands"),
]
SUP_HIT = []
_chk0 = HK.Child.check


def _chk(self, cond, msg):
    if not cond:
        m = str(msg)
        for ph, pre, why in SUPERSEDED:
            if ph == CUR[0] and m.startswith(pre):
                self.notes.append("SUPERSEDED by 0.4.27 (%s): %s" % (why, m[:160]))
                SUP_HIT.append(m)
                return True
    return _chk0(self, cond, msg)


HK.Child.check = _chk
CUR = [""]


def _phase(label, fn):
    def run(out, jar, scratch, home):
        CUR[0] = label
        return fn(out, jar, scratch, home)
    return label, run


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.27 - build script') and g.count('VERSION = "0.4.27"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem("), "S no system or command added")
    K.eq(g.count("= cls(") - o.count("= cls("), 0, "S no class added")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.check(g.count('("pets.mount.summonCooldown", "Mount summon cooldown", "show", "int", "3", "0", "60"') == 1 and o.count("summonCooldown") == 0, "S one new row: pets.mount.summonCooldown (int s, default 3, 0-60, live)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, os.path.basename(GEN))
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    K.check('bridge().put("pets:fn:ride", new @PKG@.PetRideFn());' in g, "S the Summon key pets:fn:ride is still published (Menu 0.3.53's card)")
    # FIX pets1fix F3: the second slot is the MOUNT slot in every player-visible text
    new_t = ['MODES = ["Pet slot", "Mount slot", "Fuse", "Rebirth"]', '"Mount slot unlock"', '"Mount slot buff strength"', 'sec("FIGHTING (PET SLOT)")', 'sec("MOUNT SLOT")',
             '"Mount slot - empty"', '"Pick Mount slot below', '"\\nFights next to you in the pet slot: bites for "', '"Summon it from the mount slot"', '"+Click: put it in the mount slot"']
    old_t = ['"Summon slot unlock", "pets"', '"Summon slot buff strength"', '"Summon slot Beastmastery', '"Summon slot pets', '"Summon slot - empty"', 'tc("#d6e4ee", "F on it in the summon slot")',
             'tc("#7f93a6", "Shows only in the summon slot")', '"-The summon slot is locked', '": your summon slot is open', '"While it is in the summon slot"', '"Pick Summon slot',
             '(s == 2 ? "summon slot"', '"FIGHTING (SUMMON SLOT)"', 'sec("SUMMON SLOT")']          # (older version notes in the docstring keep their history)
    K.check(all(t in g for t in new_t) and not any(t in g for t in old_t), "S F3 the player-visible texts say 'mount slot': missing %s, left %s" % ([t for t in new_t if t not in g], [t for t in old_t if t in g]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), [], "S the jar adds nothing")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json (no item / recipe / lang file changed)")
    K.save()


# ======================================================================================================== SUMMON
def _tells(W):
    told = []
    JClass, JProxy = W["JClass"], W["JProxy"]
    W["PetsEng"].API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                     "nameOf": lambda u: W["names"].get(str(u), "?"), "tell": lambda u, t, c: told.append(str(t))})
    return told


def _slot2_live(W):
    n = 0
    for v in W["Views"].LIVE.values().toArray():
        if int(v.slot) == 2 and not bool(v.gone):
            n += 1
    return n


def _same(a, b):
    return a is not None and b is not None and str(a.uuid) == str(b.uuid)


def run_summon(out, jar, scratch, _home):
    W = T425._idle_world(out, jar, scratch, "summon")
    K, Cfg, Views, Rd, Fg, JClass, uo, ent, oref, rider, jobs, second, r, pid, Ops = (W["K"], W["Cfg"], W["Views"], W["Rd"], W["Fg"], W["JClass"], W["uo"], W["ent"],
                                                                                    W["oref"], W["rider"], W["jobs"], W["second"], W["r"], W["pid"], W["Ops"])
    from jpype import JString, JProxy, JArray, JObject, JDouble
    told = _tells(W)
    PW = W["PW"]
    Fn = JClass(PKG + "PetRideFn")
    fn = Fn()
    K.eq(int(Cfg.MOUNT_CD), 3, "SUMMON the cooldown row defaults to 3 s")
    Cfg.DRAGON_FMODE = "follow"
    K.check(str(r.active(1)) == pid, "SUMMON (the stand-in record also lists the dragon in slot 1 - a state /pets never makes: toSlot clears the other slot)")
    for _ in range(3):
        second()
    K.check(Views.view(uo, 1) is None, "SUMMON one pet in both slots: the pet slot does not show it twice while the mount slot holds it")
    r.set("active.1", "")
    for _ in range(2):
        second()
    K.check(Views.view(uo, 2) is None and _slot2_live(W) == 0 and not bool(Views.called(uo)), "SUMMON a dragon in the mount slot is NOT out until summoned (ride only)")
    K.check(fn.apply("x") is None and fn.apply(None) is None, "SUMMON not a UUID -> null")
    other = W["UUID"].fromString("00000000-0000-0000-0000-000000009902")
    ro = str(fn.apply(other))
    K.check(ro.startswith("-") and not bool(Views.called(other)), "SUMMON a player with an empty mount slot -> the reason, nothing summoned (%s)" % ro)
    # ---- summon -> under you -> seated
    s0, sp0 = int(Views.SUMMONS.get()), int(Views.SPAWNED.get())
    r1 = str(fn.apply(uo))
    K.check(r1.startswith("+Summoning your") and bool(Views.called(uo)) and int(Views.SUMMONS.get()) == s0 + 1, "SUMMON pressed: '+Summoning your ...', the summon is on (%s)" % r1)
    r1b = str(fn.apply(uo))
    K.check(r1b.startswith("=Your mount is on its way") and int(Views.SUMMONS.get()) == s0 + 1, "SUMMON pressed again before it appears: '=' and no second summon (%s)" % r1b)
    second()
    dv = Views.view(uo, 2)
    K.check(dv is not None and int(Views.SPAWNED.get()) == sp0 + 1 and _slot2_live(W) == 1, "SUMMON the next second: ONE creature appears")
    dp, op = ent(dv.ref)["pos"], ent(oref)["pos"]
    K.check(abs(dp[0] - op[0]) < 1e-6 and abs(dp[2] - op[2]) < 1e-6 and abs(dp[1] - op[1]) < 1e-6, "SUMMON it appears right under you: %s (you %s)" % (dp, op))
    spec = str(dv.spec)
    K.check(str(Views.spawnNow(uo, 2, spec, W["S"]["w"], "default")).startswith("=already out") and _slot2_live(W) == 1, "SUMMON a second spawn while it is out is refused (no duplicate entity)")
    a0 = int(Rd.ASKED.get())
    second()
    K.check(int(Rd.ASKED.get()) == a0 + 1 and bool(dv.asked) and int(rider["mid"]) != 0, "SUMMON its first second asks the ride itself (the F path's PetRideJob ran: you are put on it)")
    second()
    K.check(bool(dv.riding) and bool(dv.rode) and any("You ride" in t for t in told), "SUMMON ... and you ride it (the ride line told)")
    K.check(any("vanishes when you do" in t for t in told), "SUMMON the ride line says it vanishes when you get off")
    K.check(str(fn.apply(uo)).startswith("=You are already riding it"), "SUMMON pressed while riding: '='")
    K.check(Fg.dragonOf(uo, None) is None and not bool(Fg.second(dv, r, oref, None, JArray(JDouble)([10.0, 70.0, 10.0]))), "SUMMON the mount slot creature never takes targets / fights")
    for _ in range(3):
        second()
    K.check(_same(Views.view(uo, 2), dv) and _slot2_live(W) == 1, "SUMMON it stays while you ride (no second creature)")
    # ---- hop off -> vanishes
    e0, rm0 = int(Views.ENDS.get()), int(Views.REMOVED.get())
    rider["mid"] = 0
    rider["mount"].clear()
    second()
    K.check(bool(dv.gone) and Views.view(uo, 2) is None and _slot2_live(W) == 0 and not bool(Views.called(uo)) and int(Views.ENDS.get()) == e0 + 1 and int(Views.REMOVED.get()) == rm0 + 1,
            "SUMMON you hop off: it vanishes (removed), the summon is over")
    for _ in range(2):
        second()
    K.check(Views.view(uo, 2) is None and _slot2_live(W) == 0, "SUMMON ... and nothing comes back by itself")
    rc = str(fn.apply(uo))
    K.check(rc.startswith("=") and "resting" in rc and not bool(Views.called(uo)), "SUMMON right after: the cooldown (%s)" % rc)
    second(3000)
    rc2 = str(fn.apply(uo))
    K.check(rc2.startswith("+Summoning"), "SUMMON after the cooldown: summoned again (%s)" % rc2)
    second()
    second()
    second()
    dv2 = Views.view(uo, 2)
    K.check(dv2 is not None and not _same(dv2, dv) and bool(dv2.riding) and _slot2_live(W) == 1, "SUMMON ... a fresh creature, and you ride it")
    # ---- hop off while its role is still Empty_Role: it waits (at most 3 s) - never removed mid role change
    ent(dv2.ref)["role"] = "Empty_Role"
    rider["mid"] = 0
    second()
    K.check(not bool(dv2.gone) and _same(Views.view(uo, 2), dv2), "SUMMON off while its own role is not back yet: it waits (no ghost from the engine's role change)")
    ent(dv2.ref)["role"] = "Skyy_Pet_Dragon"
    rider["mount"].clear()
    second()
    K.check(bool(dv2.gone) and _slot2_live(W) == 0, "SUMMON ... its role back: it vanishes")

    def summon_ride():
        Views.COOL.clear()
        x = str(fn.apply(uo))
        second()
        second()
        second()
        v = Views.view(uo, 2)
        return x, v
    # ---- relog
    x, v = summon_ride()
    K.check(v is not None and bool(v.riding), "SUMMON (relog) summoned + riding (%s)" % x)
    Views.leave(uo, "quit")
    while jobs:
        jobs.pop(0).run()
    rider["mid"] = 0          # the engine gets a leaving rider off
    rider["mount"].clear()
    K.check(bool(v.gone) and not bool(Views.called(uo)) and _slot2_live(W) == 0, "SUMMON logout: the creature goes, the summon is over")
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))
    for _ in range(3):
        second()
    K.check(Views.view(uo, 2) is None and _slot2_live(W) == 0, "SUMMON back online: nothing comes back by itself (no duplicate, nothing saved)")
    K.check(len(r.keysWith("summon")) == 0 and len(r.keysWith("called")) == 0, "SUMMON nothing about the summon is in the pet file")
    # ---- death
    x, v = summon_ride()
    ent(oref)["dead"] = True
    second()
    K.check(bool(v.gone) and not bool(Views.called(uo)) and int(rider["mid"]) == 0 and _slot2_live(W) == 0, "SUMMON death: you are put off, it goes, the summon is over")
    ent(oref)["dead"] = False
    second()
    second()
    K.check(Views.view(uo, 2) is None, "SUMMON ... respawned: nothing comes back by itself")
    # ---- another world
    x, v = summon_ride()
    second(wn="other")
    while jobs:
        jobs.pop(0).run()
    rider["mid"] = 0          # leaving the world gets you off
    rider["mount"].clear()
    second(wn="other")
    second(wn="other")
    K.check(bool(v.gone) and Views.view(uo, 2) is None and not bool(Views.called(uo)) and _slot2_live(W) == 0, "SUMMON another world: it goes, nothing follows you there")
    second()
    second()
    # ---- the slot changed while it waits (before the ride)
    Views.COOL.clear()
    str(fn.apply(uo))
    second()
    v = Views.view(uo, 2)
    horse = str(Ops.create(r, None, "Horse", 1, 5, 0, "test", "harness", False))
    r.set("active.2", horse)
    second()
    K.check(v is not None and bool(v.gone) and not bool(Views.called(uo)) and _slot2_live(W) == 0, "SUMMON the mount slot changed: the old creature goes, the summon is over")
    second()
    K.check(Views.view(uo, 2) is None, "SUMMON ... and the new pet does not come out by itself")
    # ---- a Horse rides the same way
    Views.COOL.clear()
    rh = str(fn.apply(uo))
    second()
    second()
    second()
    hv = Views.view(uo, 2)
    K.check(rh.startswith("+Summoning your") and hv is not None and str(hv.kind) == "Horse" and bool(hv.riding), "SUMMON a Horse: summoned + seated (%s)" % rh)
    rider["mid"] = 0
    rider["mount"].clear()
    second()
    K.check(bool(hv.gone) and _slot2_live(W) == 0, "SUMMON ... off the Horse: it vanishes")
    # ---- FIX pets1fix F1: a mount whose look (Pet looks row) flies / swims is refused at the press, never "hop on!" then a silent vanish
    Lk = JClass(PKG + "PetLook")
    hl = [str(x) for x in Lk.look("Horse")]
    lk0 = Cfg.LOOKS
    lkf = JClass("java.util.HashMap")(lk0)
    lkf.put("horse", JArray(JString)([hl[0], hl[1], "fly"]))
    Cfg.LOOKS = lkf
    Views.COOL.clear()
    told[:] = []
    rf = str(fn.apply(uo))
    K.check(rf.startswith("-Your Horse cannot carry you") and "flies or swims" in rf and not bool(Views.called(uo)) and _slot2_live(W) == 0, "SUMMON F1 a flying-look mount: refused with the reason (%s)" % rf)
    Cfg.LOOKS = lk0
    rf2 = str(fn.apply(uo))
    Cfg.LOOKS = lkf          # the look edited AFTER the press: the upkeep tells it and it goes
    for _ in range(3):
        second()
    Cfg.LOOKS = lk0
    K.check(rf2.startswith("+Summoning") and _slot2_live(W) == 0 and not bool(Views.called(uo)) and (any("cannot carry you (its look flies" in t for t in told) or any("cannot come out" in t for t in told)),
            "SUMMON F1 the look turned to flying after the press: told, nothing left out: %s" % told[-2:])
    second()
    r.set("active.2", pid)
    # ---- FIX pets1fix F2: a pet record that is unreadable for a moment (a save / profile switch) never cancels the summon
    Views.COOL.clear()
    told[:] = []
    rb2 = str(fn.apply(uo))
    r.bad = True
    second()
    r.bad = False
    K.check(rb2.startswith("+Summoning") and bool(Views.called(uo)) and not any("cannot come out" in t for t in told), "SUMMON F2 r.bad for one second: the summon stays on, nothing told (%s)" % told)
    second()
    second()
    second()
    vb = Views.view(uo, 2)
    K.check(vb is not None and bool(vb.riding) and _slot2_live(W) == 1, "SUMMON F2 ... then it appears and seats you")
    rider["mid"] = 0
    rider["mount"].clear()
    second()
    K.check(_slot2_live(W) == 0 and not bool(Views.called(uo)), "SUMMON F2 ... off: it vanishes")
    # ---- a ride the game refuses (you sit on something else): told + it vanishes
    Views.COOL.clear()
    told[:] = []
    str(fn.apply(uo))
    second()
    v = Views.view(uo, 2)
    rider["mid"] = 4242
    second()
    second()
    K.check(v is not None and bool(v.gone) and _slot2_live(W) == 0 and not bool(Views.called(uo)) and any("already riding something" in t for t in told),
            "SUMMON a refused ride: the reason is told and the summon vanishes: %s" % told[-3:])
    rider["mid"] = 0
    # ---- a ride that never takes: one retry, the give-up, it vanishes
    rapi2 = {"mount": lambda s, pet, o, ax, ay, az, mv: JString(""), "mountedId": lambda acc, o: 0, "netId": lambda acc, r_: int((ent(r_) or {}).get("net", 0)),
             "hasMount": lambda acc, r_: False, "unmount": lambda acc, r_: True, "dismount": lambda acc, o: None, "resetMove": lambda acc, o: True, "move": lambda acc, o, mid: True,
             "ground": lambda acc, r_: 1, "fly": lambda acc, o, on, h, vv: True, "flyState": lambda acc, o: -1, "saddled": lambda m, s, seed: JString(str(m)), "held": lambda s, o: None}
    api0 = Rd.API
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi2)
    Views.COOL.clear()
    told[:] = []
    f0 = int(Rd.FAILS.get())
    str(fn.apply(uo))
    for _ in range(7):
        second()
    K.check(int(Rd.FAILS.get()) == f0 + 1 and _slot2_live(W) == 0 and not bool(Views.called(uo)) and any("could not carry you - summon it again" in t for t in told),
            "SUMMON a ride that never takes: the give-up is told and the summon vanishes: %s" % told[-3:])
    Rd.API = api0
    # ---- a summon that cannot appear: ends after 15 s
    api_bad = dict(W["api"])
    api_bad["spawn"] = lambda s, role, x, y, z, yaw, model: None
    pw0 = PW.API
    PW.API = JProxy(PKG + "PetWorldApi", dict=api_bad)
    Views.COOL.clear()
    Views.PENDING.clear()
    told[:] = []
    st0 = int(Views.STALE.get())
    str(fn.apply(uo))
    for _ in range(16):
        second()
    K.check(int(Views.STALE.get()) == st0 + 1 and not bool(Views.called(uo)) and any("could not appear" in t for t in told), "SUMMON a summon that cannot appear ends after 15 s (told)")
    PW.API = pw0
    Views.PENDING.clear()
    # ---- a creature-free world after the press: ended at once
    Views.COOL.clear()
    told[:] = []
    str(fn.apply(uo))
    b0 = Cfg.BLOCKED
    Cfg.BLOCKED = "default"
    second()
    K.check(not bool(Views.called(uo)) and _slot2_live(W) == 0 and any("cannot come out here" in t for t in told), "SUMMON a world without pet creatures: the summon ends at once (told)")
    rb = str(fn.apply(uo))
    K.check(rb.startswith("-No pet creatures in this world"), "SUMMON ... pressed there: the reason (%s)" % rb)
    Cfg.BLOCKED = b0
    # ---- a spawn job that runs after the summon ended
    Views.COOL.clear()
    Views.call(uo, Rd.now())
    want = str(Views.want(uo, r, str(W["Store"].pkey(uo)), 2, "default", False))
    Views.CALLED.remove(uo)
    K.check(str(Views.spawnNow(uo, 2, want, W["S"]["w"], "default")).startswith("-the summon ended") and _slot2_live(W) == 0, "SUMMON a late spawn job after the summon ended: refused")
    # ---- refusals
    wolf = str(Ops.create(r, None, "Wolf", 1, 5, 0, "test", "harness", False))
    r.set("active.2", wolf)
    rw = str(fn.apply(uo))
    K.check(rw.startswith("-Your Wolf cannot carry you") and "pet slot" in rw and not bool(Views.called(uo)), "SUMMON a fighter-only pet in the mount slot: the reason names the pet slot (%s)" % rw)
    r.set("active.2", pid)
    lvk = "pet." + pid + ".level"
    old_lv = r.get(lvk)
    r.set(lvk, "1")
    rl = str(fn.apply(uo))
    r.set(lvk, old_lv)
    K.check(rl.startswith("-Your dragon can carry you from Lv") and not bool(Views.called(uo)), "SUMMON a young dragon: the level reason (%s)" % rl)
    r.set("active.2", "")
    re_ = str(fn.apply(uo))
    K.check(re_.startswith("-Your mount slot is empty"), "SUMMON an empty mount slot: the reason (%s)" % re_)
    r.set("active.2", pid)
    Cfg.ON = False
    rof = str(fn.apply(uo))
    Cfg.ON = True
    K.check(rof.startswith("-Pets are switched off"), "SUMMON Pets off: the reason (%s)" % rof)
    Cfg.MOUNT_CD = 0
    Views.COOL.clear()
    x, v = summon_ride()
    rider["mid"] = 0
    rider["mount"].clear()
    second()
    K.check(str(fn.apply(uo)).startswith("+Summoning"), "SUMMON cooldown row 0 = summon again at once")
    Cfg.MOUNT_CD = 3
    K.check(int(Fn.CALLS.get()) >= 20, "SUMMON every press counted (%d)" % int(Fn.CALLS.get()))
    K.save()


# ======================================================================================================== PETSLOT
def run_petslot(out, jar, scratch, _home):
    W = T425._idle_world(out, jar, scratch, "petslot")
    K, Cfg, Views, Rd, Fg, JClass, uo, ent, oref, second, steer, r, pid = (W["K"], W["Cfg"], W["Views"], W["Rd"], W["Fg"], W["JClass"], W["uo"], W["ent"], W["oref"],
                                                                         W["second"], W["steer"], W["r"], W["pid"])
    r.set("active.2", "")
    r.set("active.1", pid)
    for _ in range(3):
        second()
    pv = Views.view(uo, 1)
    K.check(pv is not None and str(pv.role) == "Skyy_Pet_Dragon" and Views.view(uo, 2) is None, "PETSLOT the dragon in the PET slot is out (its dragon role); the mount slot shows nothing")
    K.check(bool(Fg.DVIEWS.containsKey(pv.uuid)) and _same(Fg.byRef(pv.ref), pv), "PETSLOT it is guarded (every hit on it goes through its own health pool)")
    K.check(_same(Fg.dragonOf(uo, None), pv), "PETSLOT it is the dragon that takes targets (you hit it / it hit you)")
    steer(40)
    K.check(bool(pv.iair), "PETSLOT not fighting: it circles (PetIdle, the pet slot now)")
    mu = W["UUID"].randomUUID()
    mob = W["new_ref"](mu, "Goblin_Scrapper", [16.0, 70.0, 10.0])
    W["levels"][str(mu)] = 5
    b0 = int(Fg.BITES.get())
    for _ in range(10):
        second()
        steer(20)
    K.check(pv.ftgt is not None and int(pv.ftgt.getIndex()) == int(mob.getIndex()), "PETSLOT aggressive: it picks the hostile mob near you")
    K.check(int(Fg.BITES.get()) > b0, "PETSLOT ... and bites it (%d bites)" % (int(Fg.BITES.get()) - b0))
    hud = JClass(PKG + "PetHudFn")().apply(uo)
    l1 = str(hud[0]).split("|")
    K.check(len(l1) >= 17 and l1[0] == "1" and l1[10] != "" and l1[12] == "Bite", "PETSLOT the HUD's pet slot line carries its health + Bite: %s" % l1[10:16])
    ds = int(Fg.DOWNS.get()) if hasattr(Fg, "DOWNS") else 0
    K.check(bool(JClass(PKG + "PetDragon").down(pv, W["S"]["st"])), "PETSLOT a pet-slot dragon the game removes goes DOWN (never lost)")
    K.check(int(JClass(PKG + "PetDragon").downLeft(pid)) > 0, "PETSLOT ... its cooldown runs")
    cl = str(Fg.cardLine(r, pid))
    K.check("in the pet slot" in cl and "summon slot" not in cl, "PETSLOT F3 the dragon card says it fights in the pet slot: %s" % cl.strip())
    K.save()


# ======================================================================================================== EGGS
def run_eggs(out, jar, scratch, _home):
    W = T424._world(out, jar, scratch, "eggs")
    K, JClass = W["K"], W["JClass"]
    Hy, Egg, V = W["PetHatchery"], W["PetEgg"], W["V"]
    Inv, pi = T41.Inv, T41.proxy_inv
    EC, EU, ER = "Skyy_PetEgg_Mining_Common", "Skyy_PetEgg_Mining_Uncommon", "Skyy_PetEgg_Mining_Rare"
    craft_in = [str(x) for x in Hy.CRAFT_IN]
    crafts = [str(x) for x in Hy.CRAFT]
    K.eq(len(crafts), 10, "EGGS the 10 rows stay (5 Common crafts + 5 Uncommon upgrades), tier order")
    K.check(all(craft_in[i].startswith("Food_Egg:1,") for i in range(5)) and all(craft_in[i].startswith(crafts[i].replace("_Uncommon", "_Common") + ":1,") for i in range(5, 10)),
            "EGGS Common = the plain Egg + materials; Uncommon = its Common egg + materials: %s" % craft_in)
    K.check(all("Food_Egg" not in craft_in[i] for i in range(5, 10)), "EGGS an upgrade never takes the plain Egg")
    ct = str(Hy.costText(None, pi(Inv()), EU))
    K.check(ct == "1 Common Mining Egg (need 1) + 2 Enchanted Iron (need 2)" or ct.startswith("1 Common Mining Egg (need 1) + 2 "), "EGGS the upgrade cost line: %s" % ct)
    u, k, r = T44._mk(W, 901)

    def craft(inv, egg, clear=True):
        if clear:
            Hy.CLICK.clear()
        return str(Hy.craft(u, pi(inv), egg, "harness"))
    # Common from scratch, as before
    inv = Inv({"Food_Egg": 3, "Skyy_Ench_Cobblestone": 12})
    m = craft(inv, EC)
    K.check(m.startswith("+Crafted a Common Mining Egg") and inv.count(EC) == 1 and inv.count("Food_Egg") == 2 and inv.count("Skyy_Ench_Cobblestone") == 0, "EGGS a Common egg is crafted as before: %s" % m)
    # no Common egg: refused, nothing moves
    inv2 = Inv({"Food_Egg": 3, "Skyy_Ench_Iron": 5})
    m = craft(inv2, EU)
    K.check(m.startswith("-You need 1 more Common Mining Egg") and inv2.live == {"Food_Egg": 3, "Skyy_Ench_Iron": 5}, "EGGS no Common egg: refused, nothing moves (the plain Egg is not enough any more): %s" % m)
    # the upgrade
    inv3 = Inv({EC: 1, "Skyy_Ench_Iron": 2, "Food_Egg": 3})
    m = craft(inv3, EU)
    K.check(m.startswith("+Upgraded: 1 Common Mining Egg -> 1 Uncommon Mining Egg") and inv3.count(EC) == 0 and inv3.count(EU) == 1 and inv3.count("Skyy_Ench_Iron") == 0 and inv3.count("Food_Egg") == 3,
            "EGGS the upgrade takes the Common egg + 2 Enchanted Iron, gives 1 Uncommon (the plain Eggs untouched): %s / %s" % (m, inv3.live))
    # double click: exactly one upgrade
    inv4 = Inv({EC: 1, "Skyy_Ench_Iron": 4})
    m1 = craft(inv4, EU)
    m2 = craft(inv4, EU, clear=False)
    K.check(m1.startswith("+Upgraded") and not m2.startswith("+") and inv4.count(EU) == 1 and inv4.count(EC) == 0 and inv4.count("Skyy_Ench_Iron") == 2, "EGGS double click: one upgrade, the Common egg taken once (%s / %s)" % (m1, m2))
    m3 = craft(inv4, EU)
    K.check(m3.startswith("-You need 1 more Common Mining Egg") and inv4.count(EU) == 1 and inv4.count("Skyy_Ench_Iron") == 2, "EGGS a later click with no Common egg left: refused (no dupe): %s" % m3)
    # full inventory: everything back
    inv5 = Inv({EC: 1, "Skyy_Ench_Iron": 2}, refuse={EU})
    m = craft(inv5, EU)
    K.check(m.startswith("-No room") and inv5.live.get(EC) == 1 and inv5.live.get("Skyy_Ench_Iron") == 2 and inv5.count(EU) == 0, "EGGS a full inventory: nothing used, the Common egg back: %s / %s" % (m, inv5.live))
    # the Void: materials committed only after the egg
    V.live = {"Skyy_Ench_Iron": 5}
    V.save()
    V.calls[:] = []
    inv6 = Inv({EC: 1})
    m = craft(inv6, EU)
    K.check(m.startswith("+Upgraded") and inv6.count(EU) == 1 and inv6.count(EC) == 0 and V.live["Skyy_Ench_Iron"] == 3 and ("commit", "Skyy_Ench_Iron", 2) in V.calls,
            "EGGS Void materials: taken + committed after the egg: %s" % V.calls)
    V.live = {"Skyy_Ench_Iron": 5}
    V.save()
    V.calls[:] = []
    inv7 = Inv({EC: 1}, refuse={EU})
    m = craft(inv7, EU)
    K.check(m.startswith("-No room") and V.live["Skyy_Ench_Iron"] == 5 and inv7.count(EC) == 1 and not any(c[0] == "commit" for c in V.calls), "EGGS a full inventory with Void materials: the Void put back, nothing committed")
    # an open egg move of the Common egg
    r.set("eggdebt.h1", EC + "|1|0")
    inv8 = Inv({EC: 1, "Skyy_Ench_Iron": 2})
    m = craft(inv8, EU)
    r.set("eggdebt.h1", None)
    K.check(m.startswith("=Saving your last egg move") and inv8.count(EC) == 1 and inv8.count(EU) == 0, "EGGS the Common egg has an open egg move: refused, nothing moves: %s" % m)
    # Rare stays uncraftable
    m = craft(Inv({EU: 5}), ER)
    K.check(m.startswith("-Only Common eggs are crafted"), "EGGS a Rare egg is not craftable (no costs for it): %s" % m)
    # every family: Uncommon = its own Common egg
    for i in range(5, 10):
        eu_ = crafts[i]
        ec_ = eu_.replace("_Uncommon", "_Common")
        ins = craft_in[i].split(",")
        have = dict((x.split(":")[0], int(x.split(":")[1])) for x in ins)
        inv9 = Inv(dict(have))
        m = craft(inv9, eu_)
        K.check(m.startswith("+Upgraded") and inv9.count(eu_) == 1 and inv9.count(ec_) == 0 and sum(inv9.live.values()) == 1, "EGGS %s: upgraded from %s (%s)" % (eu_, ec_, m))
    K.save()


# ======================================================================================================== old phases with the dragon in the PET slot
def _petslot_src(fn):
    s = inspect.getsource(fn)
    s = s.replace('Views.view(W["uo"], 2)', 'Views.view(W["uo"], 1)')
    s = s.replace('v2.slot, v2.kind = 1, JString_("DragonPlain")', 'v2.slot, v2.kind = 2, JString_("DragonPlain")')          # "not in the MOUNT slot" now
    g = dict(T425.__dict__)
    exec(compile(s, T425.__file__, "exec"), g)
    return g[fn.__name__]


def _petslot_world(out, jar, scratch, tag):
    W = _iw0(out, jar, scratch, tag)
    W["r"].set("active.1", W["pid"])
    W["r"].set("active.2", "")
    return W


_iw0 = T425._idle_world
_dv0 = T425._dv


def _dv_pet(W):
    for _ in range(3):
        W["second"]()
    return W["Views"].view(W["uo"], 1)


def _petslot(fn):
    f = _petslot_src(fn)

    def run(out, jar, scratch, home):
        T425._idle_world = _petslot_world
        T425._dv = _dv_pet
        f.__globals__["_idle_world"] = _petslot_world
        f.__globals__["_dv"] = _dv_pet
        try:
            f(out, jar, scratch, home)
        finally:
            T425._idle_world = _iw0
            T425._dv = _dv0
    return run


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[_phase("static", run_static), _phase("summon", run_summon), _phase("petslot", run_petslot), _phase("eggs", run_eggs),
                   _phase("idle", _petslot(T425.run_idle)), _phase("agg", _petslot(T425.run_agg)), _phase("real", T425.run_real), _phase("mig", T425.run_mig),
                   _phase("ecs", T424.run_ecs), _phase("pt", T425._old(T423.run_pt)),
                   _phase("live", T417.run_live), _phase("live2", T425.run_live2)],
           script=__file__, live=(T423.T422.T421.T41.LIVE, "Skyy_SkyyPets"))
