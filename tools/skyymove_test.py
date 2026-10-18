"""Test harness for tools/skyymove.py (the shared Skyy movement protocol, Movement 2 = rule 4 per field + rule 4b Jump_Height ride).

    python tools/skyymove_test.py [--armory <TheArmoryMod-*.jar>] [--keep]
    python tools/skyymove_test.py --jar <applier jar> --class <its MoveSync class>      (the same checks on a BUILT jar's own copy)

Compiles the MoveSync class exactly as every applier does (skyymove.add_move_sync, against the cached server jar), loads it in a JVM
(-XX:-UsePerfData, TEMP / TMP in tools/dev/scratch/skyymove-test/) and checks the pure parts sync() is built from:
  1. theirMult == The Armory's own me.ladypaladra.thearmorymod.stats.StatMultiplier.fromMaxima on a grid (their class is loaded from a
     COPY of the jar in the scratch folder - the Mods folder is only read; skipped with a note when no Armory jar is found);
  2. statMax == the engine's EntityStatValue.computeModifiers rule ((asset + add) x mul when a multiplicative modifier exists);
  3. rideAmount solves their multiplier to the target: no other modifier, the Engineering Rig (Multiplicative 0.2 -> x1.2), an extra
     additive modifier, targets below 1, the x2.0 gap; the Rig's own number = x1.2 (research item 5 answered);
  4. rideCheck: a changed amount waits one sync, a match resets the fails, 3 misses in a row fall back (state 2);
  5. fieldStep: 5 strikes pause ONE field; the other field's strikes are untouched (a jump fight never pauses speed);
  6. jumpForce / speedFactor unchanged (protocol v1 numbers) and the KNOWN_WRITERS ride row.
Prints "N ok, 0 fail"; exit 1 on a failure. Scratch folder deleted unless --keep.
"""
import os, sys, shutil, glob, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import skyymove as MV

SCR = os.path.join(ROOT, "tools", "dev", "scratch", "skyymove-test")
OK, FAIL = [0], []


def check(cond, what):
    if cond:
        OK[0] += 1
    else:
        FAIL.append(what)
        print("FAIL:", what)


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv and sys.argv.index(name) + 1 < len(sys.argv) else None


def checks(jpype, M, SM):
    F = jpype.JFloat

    def near(a, b, rel=1e-4):
        return abs(a - b) <= rel * max(1.0, abs(b))

    # 1. their formula
    grid = [(10.0, v) for v in (-5.0, 0.0, 0.5, 2.0, 9.99995, 10.0, 10.00005, 10.01, 12.0, 22.0, 50.0)] + [(0.0, 3.0), (-1.0, 3.0)]
    if SM is not None:
        for am, vm in grid:
            check(float(M.theirMult(F(am), F(vm))) == float(SM.fromMaxima(F(am), F(vm))), "theirMult(%s, %s) == Armory fromMaxima" % (am, vm))
    else:
        print("note: no TheArmoryMod-*.jar found - theirMult checked against the bytecode reading only")
    for am, vm in grid:
        want = 1.0 if am <= 0 or abs(vm - am) <= 1e-4 else max(0.0, 1.0 + vm / am)
        check(near(float(M.theirMult(F(am), F(vm))), want), "theirMult(%s, %s) = %s" % (am, vm, want))
    # 2. the engine's max
    check(near(float(M.statMax(F(10), F(0), F(0), False)), 10.0), "statMax no modifiers")
    check(near(float(M.statMax(F(10), F(0), F(0.2), True)), 2.0), "statMax Rig 0.2 multiplicative = 2")
    check(near(float(M.statMax(F(10), F(3), F(0.5), True)), 6.5), "statMax (10 + 3) x 0.5")
    rig = float(M.theirMult(F(10), M.statMax(F(10), F(0), F(0.2), True)))
    check(near(rig, 1.2), "the Engineering Rig (Jump_Height Multiplicative 0.2) = x1.2 jump force (got %s)" % rig)
    # 3. the solve
    cases = [(0.0, 0.0, False), (0.0, 0.2, True), (0.0, 0.4, True), (3.0, 0.0, False), (2.0, 0.2, True)]
    targets = [0.5, 0.9, 1.0005, 1.05, 1.2, 1.5, 1.9996, 2.0, 2.0001, 2.4, 3.19]
    for add, mul, hm in cases:
        wo = float(M.theirMult(F(10), M.statMax(F(10), F(add), F(mul), hm)))
        for m in targets:
            t = wo * m
            a = float(M.rideAmount(F(10), F(add), F(mul), hm, F(t)))
            got = float(M.theirMult(F(10), M.statMax(F(10), F(add + a), F(mul), hm)))
            check(not math.isnan(a) and near(got, t, 5e-4), "ride solve others(add %s mul %s %s) target %.4f -> amount %s gives %s" % (add, mul, hm, t, a, got))
    check(math.isnan(float(M.rideAmount(F(10), F(0), F(0), True, F(1.5)))), "a multiplicative sum of 0 cannot be solved (NaN -> fallback)")
    check(math.isnan(float(M.rideAmount(F(0), F(0), F(0), False, F(1.5)))), "asset max 0 cannot be solved")
    check(math.isnan(float(M.rideAmount(F(10), F(0), F(0), False, F(-1)))), "a negative target cannot be solved")
    # 4. calibration
    st = jpype.JArray(jpype.JFloat)([-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, float("nan"), 0])
    check(M.rideCheck(st, True, F(5), F(11.8), F(14.0)) and st[10] == 5 and st[9] == 1 and st[8] == 0, "a new amount waits one sync")
    check(M.rideCheck(st, False, F(5), F(14.0), F(14.0)) and st[8] == 0 and near(st[1], 14.0), "their write matches -> riding, no fail")
    check(M.rideCheck(st, False, F(5), F(11.8), F(14.0)) and st[8] == 1, "miss 1")
    check(M.rideCheck(st, False, F(5), F(14.0), F(14.0)) and st[8] == 0, "a match resets the fails")
    check(M.rideCheck(st, False, F(5), F(11.8), F(14.0)) and st[8] == 1, "miss 1 again")
    check(M.rideCheck(st, False, F(5), F(11.8), F(14.0)) and st[8] == 2, "miss 2")
    check((not M.rideCheck(st, False, F(5), F(11.8), F(14.0))) and st[9] == 2, "miss 3 -> fallback (state 2)")
    st2 = jpype.JArray(jpype.JFloat)([-1, -1, 0, 0, 0, 0, 0, 0, 2, 1, 5, 0])
    check(M.rideCheck(st2, False, F(6), F(11.8), F(14.0)) and st2[10] == 6 and st2[8] == 0, "an amount another applier changed waits too (and its misses start over)")
    # 5. per-field strikes
    st = jpype.JArray(jpype.JFloat)([-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, float("nan"), 0])
    codes = []
    for _k in range(7):
        codes.append(int(M.fieldStep(st, 6, False)))          # jump keeps being reset
        check(int(M.fieldStep(st, 2, True)) == 0 and st[2] == 0, "speed at target while jump strikes (round %d)" % _k)
    check(codes == [1, 1, 1, 1, 2, 0, 0], "jump: 4 writes, the 5th write pauses, then silent: %s" % codes)
    check(st[6] == 5 and st[2] == 0, "only the jump field is paused")
    check(int(M.fieldStep(st, 2, False)) == 1 and st[2] == 1, "speed still writes while jump is paused")
    check(int(M.fieldStep(st, 6, True)) == 0 and st[6] == 0, "jump back at target clears its strikes")
    # 6. protocol numbers unchanged
    r = jpype.JArray(jpype.JFloat)([0.25, 0.10, 1.0, 0.2, 0, 0])
    check(near(float(M.speedFactor(r)), 1.25 * 1.10), "speed factor")
    jf = float(M.jumpForce(r, F(11.8)))
    h0 = 11.8 * 11.8 / 64.0
    check(near(jf, math.sqrt(64.0 * (h0 + 1.0) * 1.2)), "jump force (height layers)")
    check(str(M.RIDE_KEY) == "skyy_move_jump" and str(M.JUMP_STAT) == "Jump_Height" and str(M.CFG_RIDE) == "move:cfg:armoryJump", "ride names")
    row = [x for x in MV.KNOWN_WRITERS if (x[0], x[1]) == MV.RIDE_WRITER]
    check(len(row) == 1 and "stat ride" in row[0][2], "KNOWN_WRITERS The Armory row names the ride")
    check(int(M.PROTOCOL) == 1, "protocol stays 1 (entry format unchanged)")


def engine_check(jpype, loader, M):
    """M1 (critic): a small bonus solves to a stat max BELOW the stat's Min 1 (e.g. +5 % jump force -> max 0.5). The REAL engine class
    EntityStatValue (from the server jar, a Jump_Height-shaped EntityStatType Min 1 / Max 10 / Initial 1) takes our modifier, its max is what
    The Armory reads (-> x1.05), nothing throws; removing the modifier gives max 10 back. Skipped with a note when the engine classes cannot be
    built outside a server."""
    F = jpype.JFloat
    try:
        Cls = jpype.JClass("java.lang.Class")
        jpype.JClass("java.lang.Thread").currentThread().setContextClassLoader(loader)          # the engine's LogManager is looked up there
        ld = lambda n: jpype.JClass(Cls.forName(n, True, loader))
        EST = ld("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
        ESV = ld("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
        SMO = ld("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
        MTG = ld("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
        CAL = ld("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
        MODF = ld("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
        t = EST("Jump_Height", 1, 1, 10, False, None, None, None, None)
        v = ESV(0, t)
        # putModifier / removeModifier look the type up in the live asset store (absent outside a server): fill the value's own modifier
        # map and run the engine's own computeModifiers(type) (the min / max maths + the value clamp) - the step putModifier ends with
        cm = ESV.class_.getDeclaredMethod("computeModifiers", EST.class_)
        cm.setAccessible(True)
        fm = ESV.class_.getDeclaredField("modifiers")
        fm.setAccessible(True)
        if fm.get(v) is None:
            fm.set(v, jpype.JClass("java.util.HashMap")())
        mods = fm.get(v)

        def put_(key, mod):
            mods.put(key, mod)
            cm.invoke(v, t)

        def rem_(key):
            mods.remove(key)
            cm.invoke(v, t)
    except Exception as e:
        print("note: engine stat classes not constructible here (%s) - M1 left to the in-game check" % str(e)[:160])
        return
    check(abs(float(v.getMax()) - 10.0) < 1e-4 and abs(float(t.getMax()) - 10.0) < 1e-4, "M1: a fresh Jump_Height-shaped stat has max 10")
    for target in (1.02, 1.05, 1.08, 1.2, 1.6):
        a = float(M.rideAmount(F(10), F(0), F(0), False, F(target)))
        try:
            put_("skyy_move_jump", SMO(MTG.MAX, CAL.ADDITIVE, F(a)))
            ok = True
        except Exception as e:
            ok = False
            print("putModifier threw:", e.getCause() if hasattr(e, "getCause") else e)
        mx = float(v.getMax())
        got = float(M.theirMult(F(10), F(mx)))
        print("M1 +%d%%: engine max %.3f -> their x%.4f, stat value %.3f" % (round((target - 1) * 100), mx, got, float(v.get())))
        check(ok and abs(got - target) <= 5e-4 * target, "M1: +%d%% jump force -> engine max %.3f (Min 1) -> their x%.4f, value %.3f, no throw"
              % (round((target - 1) * 100), mx, got, float(v.get())))
        try:
            rem_("skyy_move_jump")
        except Exception as e:
            c = e.getCause() if hasattr(e, "getCause") else e
            check(False, "M1: removeModifier threw %s" % c)
            c.printStackTrace()
            return
        check(abs(float(v.getMax()) - 10.0) < 1e-4, "M1: modifier removed -> max 10 again (value %.3f)" % float(v.get()))


def main():
    shutil.rmtree(SCR, ignore_errors=True)
    os.makedirs(os.path.join(SCR, "tmp"))
    os.environ["TEMP"] = os.environ["TMP"] = os.path.join(SCR, "tmp")
    os.environ["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"          # TEMP / TMP above = java.io.tmpdir
    import skyybuild as B
    armory = arg("--armory") or (sorted(glob.glob(os.path.join(B.MODS_DIR, "TheArmoryMod-*.jar"))) or [None])[-1]
    acopy = None
    if armory and os.path.isfile(armory):
        acopy = os.path.join(SCR, "armory-copy.jar")
        shutil.copyfile(armory, acopy)
    J = B.start()
    pool, CtField, CtNewMethod = J["pool"], J["CtField"], J["CtNewMethod"]
    MV.probe(B, pool)
    check(True, "probe")
    w = pool.makeClass("skyymovetest.W")
    w.addField(CtField.make("public static StringBuilder LOG = new StringBuilder();", w))
    w.addMethod(CtNewMethod.make("public static void warn(String s) { LOG.append(s).append(' '); }", w))
    cls = pool.makeClass("skyymovetest.MoveSync")
    MV.add_move_sync(cls, CtField, CtNewMethod, "skyymovetest.W.warn")
    out = os.path.join(SCR, "classes")
    w.writeFile(out)
    cls.writeFile(out)
    import jpype
    File = jpype.JClass("java.io.File")
    urls = [File(out).toURI().toURL(), File(J["server_jar"]).toURI().toURL()]
    if acopy:
        urls.append(File(acopy).toURI().toURL())
    UCL = jpype.JClass("java.net.URLClassLoader")
    loader = UCL(jpype.JArray(jpype.JClass("java.net.URL"))(urls), jpype.JClass("java.lang.ClassLoader").getSystemClassLoader())
    M = jpype.JClass(loader.loadClass("skyymovetest.MoveSync"))
    SM = jpype.JClass(loader.loadClass("me.ladypaladra.thearmorymod.stats.StatMultiplier")) if acopy else None
    jar = arg("--jar")
    if jar:          # an applier jar's own copy (SkyyGear GearMove, SkyySkills / SkyyAccessories MoveSync, SkyyCore move.MoveSync)
        urls2 = [File(os.path.abspath(jar)).toURI().toURL(), File(J["server_jar"]).toURI().toURL()]
        loader2 = UCL(jpype.JArray(jpype.JClass("java.net.URL"))(urls2), jpype.JClass("java.lang.ClassLoader").getSystemClassLoader())
        M = jpype.JClass(loader2.loadClass(arg("--class")))
        print("checking %s in %s" % (arg("--class"), os.path.basename(jar)))
    checks(jpype, M, SM)
    engine_check(jpype, loader, M)
    print("%d ok, %d fail" % (OK[0], len(FAIL)))
    if "--keep" not in sys.argv:
        try:
            loader.close()
        except Exception:
            pass
    return 1 if FAIL else 0


def applier_round(name, patch, dst, prev_jar, new_jar, cls, allowed, extra=None):
    """the Movement 2 harness of one applier mod (SkyyGear 0.3.24, SkyySkills 0.4.51, SkyyAccessories 0.5.26): no JVM in this process.
    P  the patch re-run gives the same generated script (byte-identical);
    J  the jar prev -> new: nothing added or removed, the changed entries are a subset of `allowed` and include the MoveSync class;
    K  python tools/skyymove_test.py --jar new --class cls (the kit checks on THIS jar's own copy, Armory formula included);
    X  extra(zipfile of the new jar, check) for the mod's own checks. Returns the exit code (prints "N ok, M fail")."""
    import hashlib, subprocess, zipfile

    def h(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    before = h(dst)
    r = subprocess.run([sys.executable, patch], cwd=ROOT, capture_output=True, text=True)
    check(r.returncode == 0 and h(dst) == before, "P: %s re-run = the same %s (%s)" % (os.path.basename(patch), os.path.basename(dst), r.stderr[-300:]))
    za, zb = zipfile.ZipFile(prev_jar), zipfile.ZipFile(new_jar)
    ha = dict((n, hashlib.sha1(za.read(n)).hexdigest()) for n in za.namelist())
    hb = dict((n, hashlib.sha1(zb.read(n)).hexdigest()) for n in zb.namelist())
    changed = sorted(n for n in ha if n in hb and ha[n] != hb[n])
    check(set(ha) == set(hb), "J: no entry added / removed (%s / %s)" % (sorted(set(hb) - set(ha))[:5], sorted(set(ha) - set(hb))[:5]))
    check(set(changed) <= set(allowed), "J: only the expected entries changed: %s" % sorted(set(changed) - set(allowed)))
    cpath = cls.replace(".", "/") + ".class"
    check(cpath in changed and "manifest.json" in changed, "J: %s + manifest.json changed" % cpath)
    r = subprocess.run([sys.executable, os.path.join(HERE, "skyymove_test.py"), "--jar", new_jar, "--class", cls], cwd=ROOT,
                       capture_output=True, text=True)
    check(r.returncode == 0 and " 0 fail" in r.stdout, "K: the kit checks on %s's %s: %s" % (name, cls, (r.stdout.strip().splitlines() or ["?"])[-1]))
    mf = zb.read("manifest.json").decode("utf-8-sig")
    check('"Version": "%s"' % os.path.basename(new_jar)[len(name) + 1:-4] in mf, "J: manifest Version")
    if extra:
        extra(zb, check)
    print("%s Movement 2 harness: %d ok, %d fail" % (name, OK[0], len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    rc = main()
    if "--keep" not in sys.argv:
        shutil.rmtree(SCR, ignore_errors=True)
    sys.exit(rc)
