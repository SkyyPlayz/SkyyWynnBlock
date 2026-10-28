"""Harness for SkyyShards 0.4.15 (HOTFIX: the shard data lock leak - ShParticles.run's `continue` inside a lock region skipped the finally
under javassist; + a guard on every entry point; tools/shards_0_4_15_patch.py, on top of 0.4.14).
Build first:
    python tools/shards_0_4_15_patch.py && python SkyyShards/build_skyyshards_0.4.15.py
    python SkyyShards/test_skyyshards_0.4.15.py [--keep]

  S15  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; no `continue` /
                `break` inside any ShStore.LOCK region of the generated script (control: 0.4.14 has ShParticles.run's); every entry point
                wrapped by the guard; 0.4.14's static lock audit (no bridge under the lock) still clean
  LB   bytecode EVERY method of the jar walked path by path (javassist bytecode, boolean lock flags followed): no return / throw leaves the
                method with a different ShStore.LOCK hold count; control: the same scan on the 0.4.14 jar finds ShParticles.run
  LK   leak     EXECUTED: (proof) the 0.4.14 jar in a child process: one totem particle burst on a shard world leaves the world thread
                holding the lock (hold count > 0 after run() returned) - the reported bug; 0.4.15: the burst (body alone and wrapped) leaves 0,
                a working island's burst too; THE GUARD: a bridge entry point (shard:fn:door) whose body leaks a hold -> released at once,
                ShLock.LEAKS 1, LEAK_LAST names it; a caller's own hold is never released (nesting); the busy WARN's holder text names
                where the lock was taken
  NL / CB / OW / FX   every 0.4.14 lock path (every buy / add / tier-up / bench / craft, decide + door, Collect / owed / owedXp, grant, the
                page fills, Enter Shard's paint step, the busy branches) with the hold count checked AFTER EACH ACTION: 0 on the acting
                thread, the lock free unless a test holder thread holds it on purpose; ShLock.LEAKS 0 (the guard never had to fire)
  414  every older phase (0.4.13 ... 0.4.6, via the 0.4.14 harness) on the 0.4.15 jar; after each: hold count 0, lock free, LEAKS 0
  RP   replant  (Skyy 2026-10-27) a Harvest Spirit I (range 3) replants all 35 empty tilled cells, not the 12 in range; no worker = none (the
                gate); 1 seed per newly planted cell, nearest the centre first (a second regrow uses none, 10 seeds = 10 cells, all in range); the harvest factor still counts only the
                cells within range (mfac 0.700 with all 35 planted = 0.4.14's full range); the card text; 0.4.8's "only in range" checks superseded
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.15"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sh0415", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.14.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.14.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_15_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_14", os.path.join(HERE, "test_skyyshards_0.4.14.py"))
T414 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T414)
sys.argv[:] = _argv
T413 = T414.T413
T414.JAR = T413.JAR = JAR
T414.GEN = T413.GEN = GEN
T414.SCRATCH = SCRATCH
T412, T411, T410, T49, T48, T46 = T414.T412, T414.T411, T414.T410, T414.T49, T414.T48, T414.T46
OWNER = T414.OWNER
FK = T414.FK
SUP = T49._superseded

# the entry points the patch wraps (class, method) - kept in step with tools/shards_0_4_15_patch.py ENTRY
ENTRY = [("ShParticles", "run"), ("ShFill", "run"), ("ShFill", "accept"), ("ShOpened", "accept"), ("ShHop", "run"), ("ShHop", "accept"),
         ("ShClear", "run"), ("ShCheck", "run"), ("ShRain", "run"), ("ShFight", "run"), ("ShSweep", "run"), ("ShRange", "run"), ("ShAura", "run"),
         ("ShTick", "run"), ("ShLv20", "run"), ("ShTotemFn", "apply"), ("ShGate", "apply"), ("ShHand", "apply"), ("ShFn", "apply"),
         ("ShGiveFn", "apply"), ("ShDoor", "apply"), ("ShPlace", "handle"), ("ShPage", "build"), ("ShPage", "handleDataEvent"), ("ShPage", "onDismiss")]


# ---------------------------------------------------------------------------------------------------------- S15: static
def regions(src):
    """[(line, region text)] for every `LOCK.lock(); try {` ... matching `}` of the generated script"""
    out = []
    i = 0
    while True:
        j = src.find("LOCK.lock(); try {", i)
        if j < 0:
            break
        t = src.index("{", j)
        d = 0
        for e in range(t, len(src)):
            if src[e] == "{":
                d += 1
            elif src[e] == "}":
                d -= 1
                if d == 0:
                    break
        out.append((src.count("\n", 0, j) + 1, src[t:e + 1]))
        i = j + 5
    return out


def jump_out(region):
    """a `continue` / `break` in the region that is not inside a loop (or switch) that starts inside the region = it leaves the lock region
    (javassist runs no finally on it)"""
    body = re.sub(r'"(?:\\.|[^"\\])*"', '""', region)
    body = re.sub(r"//[^\n]*", "", body)
    hits = []
    for m in re.finditer(r"\b(continue|break)\s*;", body):
        pre = body[:m.start()]
        # an enclosing loop / switch opened inside the region and not yet closed
        inner = False
        for lm in re.finditer(r"\b(for|while|do|switch)\b", pre):
            k = body.find("{", lm.end())
            if k < 0 or k > m.start():
                continue
            d = 0
            closed = False
            for e in range(k, m.start()):
                if body[e] == "{":
                    d += 1
                elif body[e] == "}":
                    d -= 1
                    if d == 0:
                        closed = True
                        break
            if not closed:
                inner = True
                break
        if not inner:
            hits.append(body[max(0, m.start() - 80):m.end()].replace("\n", " "))
    return hits


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.15 - build script') and g.count('VERSION = "0.4.15"\n') == 1, "S15 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S15 no new %s" % w)
    K.check("0.4.15: the shard data lock leak fixed (totem particles) + a guard on every entry point; 0.4.14: no other mod is called" in g,
            "S15 the ready line names the round (and keeps 0.4.14's)")
    gn = g.replace("\r\n", "\n")
    on = o.replace("\r\n", "\n")
    bad = [(ln, h) for ln, r in regions(gn) for h in jump_out(r)]
    bad0 = [(ln, h) for ln, r in regions(on) for h in jump_out(r)]
    K.check(len(regions(gn)) > 60 and not bad, "S15 no continue / break leaves any of the %d lock regions: %s" % (len(regions(gn)), bad[:3]))
    K.check(len(bad0) == 1 and "hasIsland" in bad0[0][1], "S15 ... (control) the same check on 0.4.14 finds exactly ShParticles.run's continue: %s" % bad0[:2])
    K.check(gn.count("((@PKG@.ShLock) @PKG@.ShStore.LOCK).fix(") == len(ENTRY) and all(('fix("%s.%s", h0)' % e) in gn for e in ENTRY),
            "S15 every entry point runs inside the guard (%d)" % len(ENTRY))
    K.check("this.at = TRACE ? new Throwable(" in gn and "this.atBy = me; this.acq = this.acq + 1L;" in gn and "it took the lock at:" in gn,
            "S15 ShLock remembers who took its outermost hold (always) and the stack (only once TRACE is on)")
    fx = gn[gn.index("public void fix(String where, int h0) {"):]
    fx = fx[:fx.index('}""")')]
    K.check(fx.index("unlock();") < fx.index("LEAKS.incrementAndGet()") < fx.index("\n  try {\n") < fx.index("warnOnce("), "S15 fix() releases the extra holds FIRST, then reports inside try / catch")
    bad1, n1 = T414.lock_audit(gn)
    K.check(n1 > 60 and not bad1, "S15 0.4.14's static lock audit still clean: %d regions, none reaches a bridge: %s" % (n1, bad1[:3]))
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S15 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S15 line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- LB: the bytecode lock-balance scan
RET = set(range(172, 178))
COND = set(range(153, 167)) | {198, 199}
THROWS = set(range(182, 187)) | {191, 192, 187, 189, 50, 83, 46, 79, 108, 112, 190, 180, 181, 194}


def lock_scan(jar):
    """(methods with lock calls, [(class, method, finding)]) - every path of every method, the hold delta at each return / uncaught throw"""
    import zipfile
    from jpype import JClass, JArray, JByte
    CF = JClass("javassist.bytecode.ClassFile")
    DIS, BAIS = JClass("java.io.DataInputStream"), JClass("java.io.ByteArrayInputStream")
    z = zipfile.ZipFile(jar)
    bad, nlock = [], 0
    for n in z.namelist():
        if not n.endswith(".class"):
            continue
        cf = CF(DIS(BAIS(JArray(JByte)(z.read(n)))))
        cname = str(cf.getName())
        if cname.endswith(".ShLock"):
            continue
        cp = cf.getConstPool()
        for mi in cf.getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            ci = ca.iterator()
            order = []
            while ci.hasNext():
                order.append(ci.next())
            ins = {}
            for i, pc in enumerate(order):
                ins[pc] = (ci.byteAt(pc), (order[i + 1] if i + 1 < len(order) else ca.getCodeLength()) - pc)

            def eff(pc):
                op = ins[pc][0]
                if op in (182, 185):
                    idx = ci.u16bitAt(pc + 1)
                    nm = str(cp.getMethodrefName(idx) if op == 182 else cp.getInterfaceMethodrefName(idx))
                    cl = str(cp.getMethodrefClassName(idx) if op == 182 else cp.getInterfaceMethodrefClassName(idx))
                    ty = str(cp.getMethodrefType(idx) if op == 182 else cp.getInterfaceMethodrefType(idx))
                    if ty == "()V" and ("ReentrantLock" in cl or cl.endswith("ShLock") or cl.endswith(".Lock")):
                        return 1 if nm == "lock" else (-1 if nm == "unlock" else 0)
                return 0
            if not any(eff(pc) for pc in order):
                continue
            nlock += 1
            et = ca.getExceptionTable()
            hs = [(et.startPc(i), et.endPc(i), et.handlerPc(i), et.catchType(i) == 0 or str(cp.getClassInfo(et.catchType(i))) == "java.lang.Throwable")
                  for i in range(et.size())]
            mname = str(mi.getName())
            seen = set()
            stack = [(0, 0, ())]
            while stack:
                pc, d, path = stack.pop()
                if (pc, d, path) in seen:
                    continue
                seen.add((pc, d, path))
                if abs(d) > 3:
                    bad.append((cname, mname, "runaway hold delta %d at pc %d" % (d, pc)))
                    continue
                op, ln = ins[pc]
                e = eff(pc)
                loc = dict(path)
                nxt = pc + ln
                if 2 <= op <= 8 and nxt in ins:   # iconst -> istore: a known boolean / int flag
                    o2 = ins[nxt][0]
                    li = ci.byteAt(nxt + 1) if o2 == 54 else (o2 - 59 if 59 <= o2 <= 62 else None)
                    if li is not None:
                        loc[li] = op - 3
                        stack.append((nxt + ins[nxt][1], d, tuple(sorted(loc.items()))))
                        continue
                if (op == 21 or 26 <= op <= 29) and nxt in ins and ins[nxt][0] in (153, 154):   # iload flag -> ifeq / ifne
                    li = ci.byteAt(pc + 1) if op == 21 else op - 26
                    if li in loc:
                        jump = (loc[li] == 0) if ins[nxt][0] == 153 else (loc[li] != 0)
                        stack.append(((nxt + ci.s16bitAt(nxt + 1)) if jump else nxt + ins[nxt][1], d, path))
                        continue
                if op == 54 or 59 <= op <= 62:
                    li = ci.byteAt(pc + 1) if op == 54 else op - 59
                    if li in loc:
                        del loc[li]
                        path = tuple(sorted(loc.items()))
                nd = d + e
                if op in THROWS:
                    for s, en, h, allc in hs:
                        if s <= pc < en:
                            stack.append((h, nd if e < 0 else d, path))
                            if allc:
                                break
                if op in RET:
                    if nd != 0:
                        bad.append((cname, mname, "return at pc %d with hold delta %+d" % (pc, nd)))
                    continue
                if op == 191:
                    if not any(s <= pc < en for s, en, h, a in hs) and nd != 0:
                        bad.append((cname, mname, "throw at pc %d with hold delta %+d" % (pc, nd)))
                    continue
                if op == 167:
                    stack.append((pc + ci.s16bitAt(pc + 1), nd, path))
                    continue
                if op == 200:
                    stack.append((pc + ci.s32bitAt(pc + 1), nd, path))
                    continue
                if op in (168, 201):
                    bad.append((cname, mname, "jsr at %d (not followed)" % pc))
                    continue
                if op in COND:
                    stack.append((pc + ci.s16bitAt(pc + 1), nd, path))
                elif op in (170, 171):
                    a = (pc + 4) & ~3
                    stack.append((pc + ci.s32bitAt(a), nd, path))
                    if op == 170:
                        lo, hi = ci.s32bitAt(a + 4), ci.s32bitAt(a + 8)
                        for k in range(hi - lo + 1):
                            stack.append((pc + ci.s32bitAt(a + 12 + 4 * k), nd, path))
                    else:
                        for k in range(ci.s32bitAt(a + 4)):
                            stack.append((pc + ci.s32bitAt(a + 8 + 8 * k + 4), nd, path))
                    continue
                stack.append((nxt, nd, path))
    return nlock, sorted(set(bad))


def run_bytecode(out, jar, scratch, _home):
    K = HK.Child(out)
    import jpype
    if not jpype.isJVMStarted():
        HK.jvm([B.JAVASSIST], verify=False)
    n, bad = lock_scan(jar)
    K.check(n > 60 and not bad, "LB the bytecode scan: %d methods take / release ShStore.LOCK, no path leaves one with a different hold count: %s" % (n, bad[:4]))
    n0, bad0 = lock_scan(OLD_JAR)
    meths0 = sorted(set("%s.%s" % (c.rsplit(".", 1)[1], m) for c, m, _f in bad0))
    K.check(meths0 == ["ShParticles.run"], "LB ... (control) the same scan on the 0.4.14 jar finds the leak in exactly ShParticles.run: %s" % meths0)
    K.save()


CHK = {"bad": [], "n": 0, "grab": 0}
_W0, _G0, _R0 = T414._world, T414._grab, T414._release


# ---------------------------------------------------------------------------------------------------------- LK: the leak, executed + the guard
def _shard_world(L, name):
    """a World subclass (javassist) named `name`, alive, execute() records; allocated without a constructor"""
    from jpype import JClass
    WC = JClass("com.hypixel.hytale.server.core.universe.world.World")
    CP = JClass("javassist.ClassPool")(True)
    CNM = JClass("javassist.CtNewMethod")
    CF = JClass("javassist.CtField")
    nm = "com.hypixel.hytale.server.core.universe.world.SkyyShLkWorld"
    c = CP.makeClass(nm, CP.get(WC.class_.getName()))
    c.addField(CF.make("public static final java.util.ArrayList Q = new java.util.ArrayList();", c))
    c.addMethod(CNM.make("public void execute(Runnable r) { Q.add(r); }", c))
    c.addMethod(CNM.make("public boolean isAlive() { return true; }", c))
    c.addMethod(CNM.make("public String getName() { return \"%s\"; }" % name, c))
    k = c.toClass(WC.class_)
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    return uf.get(None).allocateInstance(k)


def _burst(L, w, inner=False):
    """one totem particle burst on the shard world's thread: the hold count it leaves behind"""
    from jpype import JClass
    LOCK = L["ShStore"].LOCK
    Part = JClass(PKG + "ShParticles")
    h0 = int(LOCK.getHoldCount())
    pt = Part(w)
    _W0(lambda: pt.runIn() if inner else pt.run())   # the plain world-thread runner (not the per-action checker: it would release)
    return int(LOCK.getHoldCount()) - h0


def run_leak(out, jar, scratch, _home):
    from jpype import JClass, JInt, JString
    K = HK.Child(out)
    L = T414._fx(os.path.join(scratch, "lk"), K)
    St, Cfg = L["ShStore"], L["ShCfg"]
    LOCK = St.LOCK
    p = L["p"]
    Tick = JClass(PKG + "ShTick")
    wn = "skyy-shard-" + OWNER
    w = _shard_world(L, wn)
    Tick.PRESENT.put(wn, JInt(1 << FK))   # a player stands in the Farming region
    T413._set(L, p, "farming.i0.totems", None)
    if "--proof" in sys.argv:   # the 0.4.14 jar (a child of the 0.4.15 run): the reported bug, reproduced
        n = _burst(L, w)
        K.notes.append("PROOF %d" % n)
        K.check(n > 0, "LK proof (the 0.4.14 jar): one totem particle burst left the shard world's thread holding ShStore.LOCK %d time(s) after run() returned" % n)
        while LOCK.isHeldByCurrentThread():
            LOCK.unlock()
        K.save()
        return
    # 1. the proof, on the 0.4.14 jar in its own JVM
    o0 = os.path.join(scratch, "lk-proof.json")
    env = dict(os.environ)
    pr = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", "leak", "--out", o0, "--dir", scratch, "--jar", OLD_JAR, "--proof"],
                        env=env, capture_output=True, text=True)
    d0 = json.load(open(o0)) if os.path.isfile(o0) else {"ok": [], "fails": ["no output: " + pr.stderr[-400:]], "notes": []}
    pn = [x for x in d0["notes"] if str(x).startswith("PROOF ")]
    K.notes.append("the 0.4.14 proof: %s" % pn)
    K.check(pr.returncode == 0 and not d0["fails"] and pn and int(pn[0].split()[1]) > 0,
            "LK the leak REPRODUCED on the 0.4.14 jar: one totem particle burst leaves the shard world's thread holding the lock %s time(s) (fails %s)"
            % (pn[0].split()[1] if pn else "?", d0["fails"][:2]))
    # 2. 0.4.15: the burst leaves nothing - the body alone (the fix) and wrapped (the guard has nothing to do)
    Lk = JClass(PKG + "ShLock")
    l0 = int(Lk.LEAKS.get())
    n1 = _burst(L, w, inner=True)
    n2 = _burst(L, w)
    K.check(n1 == 0 and n2 == 0 and int(Lk.LEAKS.get()) == l0 and not bool(LOCK.isLocked()),
            "LK 0.4.15: a burst over empty slots leaves hold count 0 (body %d, wrapped %d), the lock free, the guard never fired (LEAKS %d)" % (n1, n2, int(Lk.LEAKS.get()) - l0))
    T413._set(L, p, "farming.i0.totems", "harvest_spirit:1:::0:lk0001")
    n3 = _burst(L, w, inner=True)
    K.check(n3 == 0 and not bool(LOCK.isLocked()) and int(Lk.LEAKS.get()) == l0, "LK ... a slot with an island + a totem (settled, the burst itself fails on the stand-in world): hold count %d" % n3)
    T413._set(L, p, "farming.i0.totems", None)
    Tick.PRESENT.remove(wn)
    n4 = _burst(L, w)
    K.check(n4 == 0 and not bool(LOCK.isLocked()), "LK ... no one in a region (the owned regions): hold count %d" % n4)
    # 3. THE GUARD: shard:fn:door's body leaks one hold (a stand-in for SkyyIslands that takes the lock and keeps it) -> released by the wrapper
    Role, Door = L["ShRole"], L["ShDoor"]
    ou, W = L["ou"], L["W"]
    T413._set(L, p, "foraging.placed", "skyy-island-old|5|6|7")
    wk0 = Role.WORLDKEY_TEST

    def leaky(k_):
        LOCK.lock()   # never released by the body
        return JString(W) if str(k_) == OWNER else None
    Role.WORLDKEY_TEST = L["PyFn"](leaky)
    try:
        args = JClass("java.lang.Object")[:]([ou, JString(OWNER), JString("foraging"), JString(W), JInt(10), JInt(129), JInt(10)])
        r = _W0(lambda: Door().apply(args))
    finally:
        Role.WORLDKEY_TEST = wk0
    K.check(int(LOCK.getHoldCount()) == 0 and not bool(LOCK.isLocked()) and int(Lk.LEAKS.get()) == l0 + 1 and str(Lk.LEAK_LAST) == "ShDoor.apply",
            "LK THE GUARD: shard:fn:door's body left one extra hold -> released when the entry point ended (hold %d, locked %s, LEAKS +%d, last %s; door said %s)"
            % (int(LOCK.getHoldCount()), bool(LOCK.isLocked()), int(Lk.LEAKS.get()) - l0, Lk.LEAK_LAST, r))
    m1 = str(Lk.LEAK_MSG)
    K.check("ShDoor.apply" in m1 and "no stack recorded" in m1 and "acquisition #" in m1 and bool(Lk.TRACE),
            "LK ... the first report (cheap mode: no stack was recorded) names the entry point + the acquisition, and switches stack recording on: %r" % m1[-160:])
    Role.WORLDKEY_TEST = L["PyFn"](leaky)
    try:
        _W0(lambda: Door().apply(args))
    finally:
        Role.WORLDKEY_TEST = wk0
    m2 = str(Lk.LEAK_MSG)
    K.check(int(LOCK.getHoldCount()) == 0 and not bool(LOCK.isLocked()) and int(Lk.LEAKS.get()) == l0 + 2 and "ShRole.currentWorld" in m2 and "ShDoor.door" in m2,
            "LK ... a leak after that: released too, and the report names the line that took the lock (ShRole.currentWorld <- ShDoor.door): %r" % m2[-200:])
    l0 += 1
    Cfg.UNDER.set(0)   # the leaky stand-in made the rest of that call count as "under the lock" (on purpose)
    # 4. nesting: a caller's own hold is never released by an entry point it calls
    LOCK.lock()
    try:
        n5 = _burst(L, w)
        h5 = int(LOCK.getHoldCount())
    finally:
        LOCK.unlock()
    K.check(n5 == 0 and h5 == 1 and int(Lk.LEAKS.get()) == l0 + 1 and int(LOCK.getHoldCount()) == 0,
            "LK ... nesting: an entry point run while the caller holds the lock keeps the caller's hold (hold %d inside, released by the caller)" % h5)
    # 5. cheap mode: an outermost hold records only who + the count, no stack
    Lk.TRACE = False
    a0 = int(LOCK.acq)
    _W0(lambda: LOCK.lock())
    try:
        K.check(LOCK.at is None and str(LOCK.atBy).startswith("WorldThread") and int(LOCK.acq) == a0 + 1, "LK TRACE off: an outermost hold allocates no stack (at %s), records the thread %s + acquisition %d" % (LOCK.at, LOCK.atBy, int(LOCK.acq)))
    finally:
        LOCK.unlock()
    Lk.TRACE = True
    # 6. the busy WARN's holder text names where the lock was taken
    LOCK.lock()
    try:
        ht = str(LOCK.holder())
    finally:
        LOCK.unlock()
    K.check("it took the lock at:" in ht and ht.count("\n    at ") > 1 and LOCK.at is not None, "LK the holder text (busy WARN) names where the lock was taken: %r" % ht[-200:])
    T414._under(K, Cfg, "LK")
    K.save()


# ---------------------------------------------------------------------------------------------------------- every action / phase: the hold count


def _world_chk(fn):
    r = _W0(fn)
    from jpype import JClass
    LOCK = JClass(PKG + "ShStore").LOCK
    CHK["n"] += 1
    hc = int(LOCK.getHoldCount())
    lk = bool(LOCK.isLocked()) and CHK["grab"] == 0
    if hc or lk:
        CHK["bad"].append("action %d: hold %d, locked %s" % (CHK["n"], hc, lk))
        while LOCK.isHeldByCurrentThread():
            LOCK.unlock()
    return r


def _grab_chk(LOCK, hold):
    CHK["grab"] += 1
    return _G0(LOCK, hold)


def _release_chk(hold):
    try:
        return _R0(hold)
    finally:
        CHK["grab"] = max(0, CHK["grab"] - 1)


T414._world, T414._grab, T414._release = _world_chk, _grab_chk, _release_chk


def _h(fn, per_action=False):
    """an older phase, then: hold count 0 on this thread, the lock free, the guard never fired; per_action = also after each action"""
    def r(out, jar, scratch, home):
        fn(out, jar, scratch, home)
        import jpype
        if not jpype.isJVMStarted():
            return
        from jpype import JClass
        try:
            LOCK = JClass(PKG + "ShStore").LOCK
            Lk = JClass(PKG + "ShLock")
        except Exception:
            return   # a phase that never loaded the jar
        d_ = json.load(open(out))
        K = HK.Child(out)
        K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
        import time
        for _i in range(50):   # a test holder thread may still be letting go
            if not bool(LOCK.isLocked()):
                break
            time.sleep(0.02)
        K.check(int(LOCK.getHoldCount()) == 0 and not bool(LOCK.isLocked()) and int(Lk.LEAKS.get()) == 0,
                "H after this phase: hold count %d, locked %s, the guard released %d leaked hold(s) (%s)" % (int(LOCK.getHoldCount()), bool(LOCK.isLocked()), int(Lk.LEAKS.get()), Lk.LEAK_LAST))
        if per_action:
            K.check(CHK["n"] > 0 and not CHK["bad"], "H after EACH of the %d actions: hold count 0 on the acting thread, the lock free (unless a test holder held it): %s" % (CHK["n"], CHK["bad"][:4]))
        K.save()
    return r


# ---------------------------------------------------------------------------------------------------------- RP: replant every empty tilled cell
SUP_RP = ("G the Farming starter: 8 Eternal Wheat around the centre + ", "G fix: the 23 cells out of range stay empty")   # 0.4.8's "only in range" replant checks (RP checks the new rule)


def run_geo48(out, jar, scratch, home):
    SUP(SUP_RP, lambda: T49.run_geo48(out, jar, scratch, home))


def run_replant(out, jar, scratch, _home):
    """Skyy 2026-10-27: "Totems should replant every empty tilled cell on the island from the seed store, no matter the range. Range still
    limits what it harvests." """
    import math
    from jpype import JClass, JArray, JInt
    K = HK.Child(out)
    L = T48._setup(os.path.join(scratch, "rp"), K)
    St, Isl, Geo, Fill, Door = (L[n] for n in ("ShStore", "ShIsl", "ShGeo", "ShFill", "ShDoor"))
    ou = L["UUID"].fromString(OWNER)
    W = "skyy-island-" + OWNER
    Door.door(ou, OWNER, "farming", W, 29, 129, -31)
    p = St.get(OWNER)
    Y = int(Geo.Y)
    cx, cz = int(Geo.ox(FK) + Geo.SX[0]), int(Geo.OZ + Geo.SZ[0])
    fxs1, fzs1 = list(Isl.fx(1)), list(Isl.fz(1))
    man = set((int(fxs1[i]), int(fzs1[i])) for i in range(8, int(round(72 * 0.6))))
    inr = set(c for c in man if c[0] * c[0] + c[1] * c[1] <= 9)
    reg = list(Geo.region(p, FK))
    farm = [b for b in reg if int(b[3]) == int(Geo.FARM)]
    pos = set((int(b[0]) - cx, int(b[2]) - cz) for b in farm)
    tills = set((int(b[0]) - cx, int(b[2]) - cz) for b in reg if int(b[3]) == int(Geo.TILL) and int(b[1]) == Y)
    K.check(int(Geo.reach(FK, p, 0)) == 3 and len(farm) == len(man) == 35 and pos == man and man <= tills and len(inr) == 12,
            "RP a Harvest Spirit I (range 3) replants EVERY empty tilled cell of the island: %d replant cells = the %d tilled manual cells (12 of them in range)" % (len(farm), len(man)))
    K.check(all(int(b[6]) == min(20, int(math.ceil(math.sqrt((int(b[0]) - cx) ** 2 + (int(b[2]) - cz) ** 2) - 1e-6))) for b in farm),
            "RP each cell's scan bin = ceil(its distance) (bins <= range = exactly the cells within range)")
    wk = str(p.getProperty("farming.i0.totems"))
    p.setProperty("farming.i0.totems", "")
    f0 = [b for b in Geo.region(p, FK) if int(b[3]) == int(Geo.FARM)]
    p.setProperty("farming.i0.totems", wk)
    K.check(not f0 and int(Geo.reach(FK, p, 0)) == 3, "RP ... the gate kept: no worker totem on the island = nothing replanted (%d)" % len(f0))
    # seeds: 1 per newly planted cell, only on empty cells, never more than the store
    M = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = M
    job = Fill(None, None, None)
    job.kind = FK
    job.prep(p)
    Fill.paintY(None, Geo.region(p, FK), JClass("java.util.HashSet")(), job)
    key = lambda b: "%d,%d,%d" % (int(b[0]), int(b[1]), int(b[2]))
    clr = lambda: [M.remove(key(b)) for b in farm]
    clr()
    p.setProperty("farming.i0.seed", "100")

    def regrow():
        j = Fill(None, None, None)
        j.kind = FK
        j.prep(p)
        Fill.paintY(None, Geo.crops(p, FK), None, j)
        return j
    job = regrow()
    planted = [b for b in farm if M.get(key(b)) is not None]
    K.check(len(planted) == 35 and int(job.seedUsed[0]) == 35 and int(p.getProperty("farming.i0.seed")) == 65 and sum(int(job.pl[j]) for j in range(21)) == 35,
            "RP the regrow plants all 35 empty cells from 35 seeds (store 100 -> %s), the scan counts 35" % p.getProperty("farming.i0.seed"))
    b_ = [int(job.pl[j]) for j in range(21)]
    job2 = regrow()
    K.check(int(job2.seedUsed[0]) == 0 and int(p.getProperty("farming.i0.seed")) == 65 and sum(int(job2.pl[j]) for j in range(21)) == 35,
            "RP ... a second regrow over planted cells uses no seed (store stays 65) and counts the same 35 (no dupes)")
    clr()
    p.setProperty("farming.i0.seed", "10")
    job3 = regrow()
    n3 = sum(1 for b in farm if M.get(key(b)) is not None)
    got3 = [b for b in farm if M.get(key(b)) is not None]
    K.check(n3 == 10 and int(job3.seedUsed[0]) == 10 and int(p.getProperty("farming.i0.seed")) == 0 and all(int(b[6]) <= 3 for b in got3),
            "RP ... 10 seeds for 35 empty cells, range 3: the 10 go to cells within range (nearest first; bins %s), the store at 0" % sorted(int(b[6]) for b in got3))
    b3 = [int(job3.pl[j]) for j in range(21)]
    p.setProperty("farming.i0.pl", str(Isl.binsText(JArray(JInt)(b3))))
    K.check(abs(float(Isl.mfac(FK, p, 0, 1, 3)) - (8 + 0.5 * 10) / 20.0) < 1e-9, "RP ... so the harvested share is the most those 10 seeds can give: (8 + 0.5 x 10) / 20")
    # harvest output stays range-limited: all 35 planted -> the manual factor of the range-3 worker = exactly 0.4.14's fully planted range
    p.setProperty("farming.i0.pl", str(Isl.binsText(JArray(JInt)(b_))))
    mf = float(Isl.mfac(FK, p, 0, 1, 3))
    floor_in = sum(1 for c in man if int(math.floor(math.sqrt(c[0] * c[0] + c[1] * c[1]))) <= 3)
    K.check(abs(mf - (8 + 0.5 * 12) / 20.0) < 1e-9 and sum(b_[:4]) == 12 and floor_in > 12,
            "RP Range still limits what it harvests: 35 planted, the range-3 worker counts the 12 within range (mfac %.3f = 0.4.14's fully planted 0.700; floor bins would have counted %d)" % (mf, floor_in))
    p.setProperty("farming.i0.pl", str(Isl.binsText(JArray(JInt)([0, 0, 2, 3] + [0] * 17))))
    K.check(abs(float(Isl.mfac(FK, p, 0, 1, 3)) - (8 + 0.5 * 5) / 20.0) < 1e-9, "RP ... part planted: 5 within range = (8 + 0.5 x 5) / 20")
    g = open(GEN, encoding="utf8").read()
    K.check("it replants every empty tilled cell of the island (saplings: in its range)" in g and "replants the harvested cells in its range" not in g,
            "RP the Seeds and replanting card no longer says planting is range-limited")
    Fill.TEST_BLOCKS = None
    K.save()


def run_players48(out, jar, scratch, home):
    """the map migration's collect.log line names the RUNNING version: 0.4.15 now"""
    SUP(("P one collect.log line with the Undo", "P the map migration's collect.log line"), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    txt = ""
    for root, _d, fs in os.walk(os.path.join(scratch, "p48")):
        for f_ in fs:
            if f_ == "collect.log":
                txt += open(os.path.join(root, f_), encoding="utf8").read()
    K.check("map migration (SkyyShards 0.4.15) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt,
            "P the map migration's collect.log line (running version 0.4.15) with the Undo")
    K.save()


EXPECT = {   # 0.4.14 -> 0.4.15, checked by hand 2026-10-28: the version texts (CfgFn / CfgRows, ShStore migrate* log lines, the ready line in
    # SkyyShardsPlugin.setup); the leak fix (ShParticles run -> runIn); the guard (ShLock LEAKS / LEAK_LAST / at / trace / fix, lock + holder;
    # every entry point: the body renamed <name>In, the old name = the wrapper)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'ShGeo': ['~m island'],   # replant every empty tilled cell (Skyy 2026-10-27)
    'ShPage': ['~m buildTotem'],   # the Seeds and replanting card's text
    'ShLock': ['+f LEAKS', '+f LEAK_LAST', '+f LEAK_MSG', '+f TRACE', '+f acq', '+f at', '+f atBy', '+m fix', '+m site', '+m trace', '~<clinit>', '~m holder', '~m lock'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],   # save: same source, its constant-pool indexes moved
    'SkyyShardsPlugin': ['~m setup'],
}
for _c, _m in ENTRY:
    EXPECT.setdefault(_c, [])
    EXPECT[_c] += ["+m %sIn" % _m, "~m %s" % _m]
for _c in EXPECT:
    EXPECT[_c] = sorted(set(EXPECT[_c]))
_ORIG_COMPARE = T414._ORIG_COMPARE


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """every non-class file identical (manifest.json aside); the classes as EXPECT"""
    import zipfile as _zf
    with _zf.ZipFile(jar) as a, _zf.ZipFile(old_jar) as b:
        na = dict((n_, a.read(n_)) for n_ in a.namelist() if not n_.endswith(".class"))
        nb = dict((n_, b.read(n_)) for n_ in b.namelist() if not n_.endswith(".class"))
    ch = sorted(n_ for n_ in set(na) | set(nb) if na.get(n_) != nb.get(n_) and n_ != "manifest.json")
    assert not ch, "C non-class files differ: %s" % ch[:8]
    print("C. %d non-class files identical (manifest.json aside)" % len(nb))
    cps = []
    for j, tag in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag)
        with _zf.ZipFile(j) as zi, _zf.ZipFile(cp, "w", _zf.ZIP_DEFLATED) as zo:
            for n_ in zi.namelist():
                if not T49.MAP_ENTRY.match(n_):
                    zo.writestr(n_, zi.read(n_))
        cps.append(cp)
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare
_g, _p = T414._g, T414._p

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("bytecode", run_bytecode), ("leak", run_leak),
                   ("nolock", _h(T414.run_nolock, True)), ("commit", _h(T414.run_commit, True)), ("owed", _h(T414.run_owed, True)), ("fixer", _h(T414.run_fixer, True)),
                   ("lock", _h(_g(T413.run_lock))), ("busy", _h(_g(T413.run_busy, T414.SUP_BZ))), ("place", _h(_g(T413.run_place))), ("walk3", _h(_g(T413.run_walk3))),
                   ("flows3", _h(_g(T413.run_flows3))), ("aura", _h(_g(T413.run_aura))),
                   ("bags", _h(_p(T412.run_bags, lock_ok=True))),
                   ("exec48", _h(_p(T49.run_exec48))), ("exec47", _h(_p(T49.run_exec47, T414.SUP_X47))), ("exec46", _h(_p(T49.run_exec46))),
                   ("centre47", _h(_p(T49.run_centre47))), ("config48", _h(_p(T49.run_config48))), ("mig48", _h(_p(T410.run_mig48))),
                   ("players48", _h(_p(run_players48))), ("geo48", _h(_p(run_geo48))), ("replant", _h(run_replant)), ("config49", _h(_p(T49.run_config))),
                   ("mig49", _h(_p(T49.run_mig))), ("exec49", _h(_p(T49.run_exec))), ("page49", _h(_p(T49.run_page))),
                   ("width", _h(_p(T49.run_width))), ("order", _h(_p(T410.run_order))), ("flows", _h(_p(T410.run_flows))),
                   ("zones", _h(_p(T411.run_zones))), ("balance", _h(_p(T411.run_balance))), ("land", _h(_p(T411.run_land))),
                   ("night", _h(_p(T411.run_night))), ("spawn", _h(_p(T411.run_spawn))), ("buy", _h(_p(T411.run_buy))),
                   ("config", _h(_p(T411.run_config))), ("gate", _h(_p(T411.run_gate))), ("order2", _h(_p(T411.run_order2))),
                   ("live", T411.run_live411)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
