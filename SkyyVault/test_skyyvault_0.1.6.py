"""Bare-JVM harness for SkyyVault 0.1.6 - THE LIFELONG-TOOL FETCH HOOK (vault:fn:findLL / takeLL / doneLL / putBack; Skyy 2026-10-13
LOST TOOL: "if you can, make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"). Committed next to
the build so the build docstring's claims can be re-run instead of trusted. Copy it to the next version and keep it passing.

    python SkyyVault/test_skyyvault_0.1.6.py [--jar <SkyyVault-0.1.6.jar>] [--old <SkyyVault-0.1.5.jar>] [--dir <scratch>]
                                             [--live <a Skyy_SkyyVault data folder>] [--keep]

Build first (python tools/vault_0_1_6_patch.py ; python SkyyVault/build_skyyvault_0.1.6.py). One JVM (the game's JRE, -Xverify:all,
-XX:-UsePerfData; HytaleServer.jar + javassist on the classpath; EACH SkyyVault jar in its own class loader, so 0.1.5 - the live SET
pin - and 0.1.6 run side by side) checks:
  A  every class of both jars loads, verifies and initialises
  B  the 0.1.6 contract in bytes: class names = 0.1.5's + VLL / VLLFn / VLLTask; every other class byte-identical except CfgFn / CfgRows
     (the embedded version string only) and VCodec / VStore / VTick / SkyyVaultPlugin, changed method by method exactly as planned
     (VCodec + isPend / pendCount, VStore fromDoc + infoLines (+ the version string), VTick.run, SkyyVaultPlugin.setup: the four keys);
     no engine member referenced from a class that may not access it; the non-class entries differ only in the manifest
  C  THE HOOK, executed end to end on the 0.1.6 jar in a stand-in universe (one world whose thread is this thread, players, their
     inventory sections, a real /vault session for the "open" cases - VSessions.open2 with the engine's own container + window):
     find (closed / open / not there / wrong profile / other player / unreadable / bad args / pending), take from a CLOSED vault, take
     while OPEN on the page on screen (through the live container - the window is re-sent) and on another page, put-back (own slot, a
     taken slot, a full vault), the gates (not the world thread, profile busy, after a switch, another active profile, a take already
     open), wrong player / unknown tokens, a failed file write (undone, open and closed), the bridge Function (argument parsing, result
     types), and CRASH POINTS 1-4 + "after doneLL": every crash is followed by a simulated restart (memory dropped, the vault re-read
     from its file by the join scan, the 1 s tick + the queued world task resolving it) - the tool exists EXACTLY ONCE (vault file +
     inventory) after every step, with the inventory as the engine saved it either way; and a crash file read by 0.1.5 (rollback) puts
     the tool back into its slot
     FIX ROUND: the 30 s placed note after doneLL (a crash before the engine's player save brings the tool back; the hold ends by
     time only), and snapshots isolated from later changes (VStore.toDoc deep-copies the orphans; a saver thread races takes)
  D  START TWICE on a scratch COPY of the live Skyy_SkyyVault folder (read-only source, both jars): every vault file reads, an open /
     close writes nothing, a second start reads what the first saw, 0.1.5 and 0.1.6 read and write the same (version aside); 0.1.6
     finds no pending take and no lifelong tool of a made-up uid in any live vault
Nothing is deployed and nothing outside the scratch folder is written. --dir (default tools/dev/scratch/test-vault) must lie under
tools/dev/scratch; the harness works in a FRESH run-* sub-folder (TEMP / TMP / java.io.tmpdir point into it) and deletes only that.
Exit code 1 on any failure, 2 on a refused --dir.
"""
import os, sys, re, json, shutil, zipfile, tempfile, collections, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.6", "0.1.5"
PKG = "com.skyy.vault."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def default_live():
    try:
        import skyybuild as B
        w = re.search(r'^WORLD\s*=\s*"([^"]+)"', open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf8").read(), re.M).group(1)
        return os.path.join(B.USERDATA, "Saves", w, "mods", "Skyy_SkyyVault")
    except Exception:
        return ""


SCRATCH_ROOT = os.path.join(TOOLS, "dev", "scratch")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "test-vault")))
WORK = None
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyVault-%s.jar" % OLD_VERSION)))
LIVE = arg("--live", None) or default_live()
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
COUNT = {}
KEYS = ("vault:fn:findLL", "vault:fn:takeLL", "vault:fn:doneLL", "vault:fn:putBack")


def scratch_ok(path):
    root = os.path.normcase(os.path.abspath(SCRATCH_ROOT)).rstrip("\\/") + os.sep
    return os.path.normcase(os.path.abspath(path)).startswith(root)


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what[:800])
    return cond


def tally(key, n=1):
    COUNT[key] = COUNT.get(key, 0) + n


def entries(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n, z.read(n)) for n in z.namelist())
    z.close()
    return out


def classes(jar):
    return dict((n[:-6].replace("/", "."), b) for n, b in entries(jar).items() if n.endswith(".class"))


def run():
    import jpype
    from jpype import JClass, JArray
    import skyybuild as B
    tmp = os.path.join(WORK, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR)}
    CB = {"old": classes(OLD), "new": classes(JAR)}

    # ---------------- A. load + verify + init, both jars
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                tally("A classes " + k)
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised: 0.1.5 %d, 0.1.6 %d classes (-Xverify:all)" % (COUNT.get("A classes old", 0),
                                                                                         COUNT.get("A classes new", 0)))
    if FAILS:
        return
    byte_section(JClass, B, CB)
    E = common(JClass, L)
    hook_section(E)
    live_section(E)


# ------------------------------------------------------------------------------------------------ B. bytes
def byte_section(JClass, B, CB):
    import re as _re
    old, new = CB["old"], CB["new"]
    added = sorted(set(new) - set(old))
    check(added == [PKG + "VLL", PKG + "VLLFn", PKG + "VLLTask"] and not (set(old) - set(new)),
          "B. class names = 0.1.5's + VLL / VLLFn / VLLTask: new %s, gone %s" % (added, sorted(set(old) - set(new))))
    # CfgRows: the shared config kit's lock-free bridge (tools/skyycfg.py 2026-10-13, "picked up at its next build": + BRIDGE, bridge0)
    CODE = ("VCodec", "VStore", "VTick", "SkyyVaultPlugin", "CfgRows")
    ver_only, n_same = [], 0
    for n in sorted(old):
        short = n.rsplit(".", 1)[1]
        if short in CODE or n not in new:
            continue
        if old[n] == new[n]:
            n_same += 1
            OKS[0] += 1
            continue
        swapped = new[n].replace(VERSION.encode(), OLD_VERSION.encode())
        if check(swapped == old[n], "B. %s differs from 0.1.5 by more than its embedded version string" % n):
            ver_only.append(short)
    check(sorted(ver_only) == ["CfgFn"], "B. only CfgFn differs by nothing but the version string: %s" % ver_only)
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")
    Mod = JClass("javassist.Modifier")

    def ct(b):
        return CP(False).makeClass(BAIS(b))

    BRANCH = _re.compile(r"\A(if\w*|goto|goto_w|jsr|jsr_w) (\d+)\Z")

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, raw = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            raw.append((pos, _re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp)))))
        idx = dict((p, i) for i, (p, _t) in enumerate(raw))
        idx[ca.getCodeLength()] = len(raw)
        out = []
        for _p, t in raw:
            t = _re.sub(r"\Aldc_w ", "ldc ", t)
            m2 = BRANCH.match(t)
            if m2:
                t = "%s @%s" % (m2.group(1).replace("_w", ""), idx.get(int(m2.group(2)), "?" + m2.group(2)))
            out.append(t)
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try @%s @%s @%s %s" % (idx.get(et.startPc(i)), idx.get(et.endPc(i)), idx.get(et.handlerPc(i)),
                                               cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        ci = c.getClassInitializer()
        if ci is not None:
            out["<clinit>"] = code_of(ci)
        return out

    def fields(c):
        return sorted((str(f.getName()), str(f.getSignature())) for f in c.getDeclaredFields())

    PLAN = {  # class -> (changed methods, new methods)
        "VCodec": ([], ["isPend(Lorg/bson/BsonDocument;)Z", "pendCount(Lorg/bson/BsonArray;)I"]),
        "VStore": (["fromDoc(Ljava/util/UUID;Lorg/bson/BsonDocument;)Lcom/skyy/vault/VData;",
                    "infoLines(Ljava/util/UUID;IZ)[Ljava/lang/String;",
                    "toDoc(Lcom/skyy/vault/VData;)Lorg/bson/BsonDocument;"], []),
        "VTick": (["run()V"], []),
        "SkyyVaultPlugin": (["setup()V"], []),
        "CfgRows": (["bridge()Ljava/util/Map;"], ["bridge0()Ljava/util/Map;"]),
    }
    for short in CODE:
        n = PKG + short
        ob = old[n]
        nb = new[n].replace(VERSION.encode(), OLD_VERSION.encode()) if short in ("VStore", "CfgRows") else new[n]
        oc, nc = ct(ob), ct(nb)
        extra = [("BRIDGE", "Ljava/util/Map;")] if short == "CfgRows" else []
        check(sorted(fields(oc) + extra) == fields(nc), "B. %s: the same fields%s" % (short, " + the kit's BRIDGE" if extra else ""))
        mo, mn = methods(oc), methods(nc)
        changed = sorted(k2 for k2 in mo if k2 in mn and mo[k2] != mn[k2])
        gone = sorted(set(mo) - set(mn))
        newm = sorted(set(mn) - set(mo))
        want_ch, want_new = PLAN[short]
        check(changed == sorted(want_ch) and newm == sorted(want_new) and not gone,
              "B. %s: changed %s (want %s), new %s (want %s), gone %s" % (short, changed, want_ch, newm, want_new, gone))
        tally("B planned", len(changed) + len(newm))
    # VStore.toDoc: the file's version string + (fix round) the orphans as a deep copy: exactly one BsonArray.clone added, nothing else
    st_new = methods(ct(new[PKG + "VStore"]))
    st_old = methods(ct(old[PKG + "VStore"]))
    td = [k2 for k2 in st_new if k2.startswith("toDoc(")]
    check(len(td) == 1 and any('"%s"' % VERSION in t for t in st_new[td[0]]), "B. VStore.toDoc writes version %s" % VERSION)
    tn, to_ = st_new[td[0]], st_old[td[0]]
    check(sum(1 for t in tn if "BsonArray.clone" in t) == 1 and sum(1 for t in to_ if "clone" in t) == 0 and len(tn) - len(to_) == 2,
          "B. VStore.toDoc: one BsonArray.clone (+ its checkcast) added for the orphans (%d -> %d instructions)" % (len(to_), len(tn)))
    # the setup puts the four keys; VTick.run calls VLL.tick after VSessions.tick
    setup = methods(ct(new[PKG + "SkyyVaultPlugin"]))["setup()V"]
    for key in KEYS:
        check(any('"%s"' % key in t for t in setup), "B. setup puts %s" % key)
    tr = methods(ct(new[PKG + "VTick"]))["run()V"]
    calls = [t for t in tr if t.startswith("invokestatic") and "warnOnce" not in t]
    check(len(calls) == 2 and "VSessions.tick" in calls[0] and "VLL.tick" in calls[1], "B. VTick.run = VSessions.tick, then VLL.tick: %s" % calls)
    # the fromDoc change: one isPend check in the orphan loop, nothing else
    fo = methods(ct(old[PKG + "VStore"]))["fromDoc(Ljava/util/UUID;Lorg/bson/BsonDocument;)Lcom/skyy/vault/VData;"]
    fn = st_new["fromDoc(Ljava/util/UUID;Lorg/bson/BsonDocument;)Lcom/skyy/vault/VData;"]
    check(sum(1 for t in fn if "VCodec.isPend" in t) == 1 and sum(1 for t in fo if "isPend" in t) == 0 and len(fn) - len(fo) <= 22
          and sum(1 for t in fn if t == 'ldc "lld"') == 1,
          "B. fromDoc: one isPend branch added, dropping a placed mark (%d -> %d instructions)" % (len(fo), len(fn)))
    # engine members referenced from a class that may not access them (IllegalAccessError at run time)
    OP = JClass("javassist.bytecode.Opcode")
    FOPS = (OP.GETFIELD, OP.PUTFIELD, OP.GETSTATIC, OP.PUTSTATIC)

    def access_problems(jar):
        pool = CP(True)
        pool.appendClassPath(B.SERVER_JAR)
        pool.appendClassPath(jar)
        bad, n_refs = [], 0
        for cn in sorted(classes(jar)):
            cc = pool.get(cn)
            for m in list(cc.getDeclaredMethods()) + list(cc.getDeclaredConstructors()):
                ca = m.getMethodInfo().getCodeAttribute()
                if ca is None:
                    continue
                cpool = m.getMethodInfo().getConstPool()
                it = ca.iterator()
                while it.hasNext():
                    p0 = it.next()
                    op = it.byteAt(p0)
                    if op not in FOPS and op not in (OP.INVOKEVIRTUAL, OP.INVOKESPECIAL, OP.INVOKESTATIC):
                        continue
                    ix = it.u16bitAt(p0 + 1)
                    if op in FOPS:
                        owner, name, desc = cpool.getFieldrefClassName(ix), cpool.getFieldrefName(ix), cpool.getFieldrefType(ix)
                    else:
                        owner, name, desc = cpool.getMethodrefClassName(ix), cpool.getMethodrefName(ix), cpool.getMethodrefType(ix)
                    if str(owner).startswith(("com.skyy.", "java.", "javax.")):
                        continue
                    n_refs += 1
                    try:
                        oc = pool.get(owner)
                        if op in FOPS:
                            mem, c2 = None, oc
                            while c2 is not None and mem is None:
                                try:
                                    mem = c2.getDeclaredField(name)
                                except Exception:
                                    c2 = c2.getSuperclass()
                        elif str(name) == "<init>":
                            mem = oc.getConstructor(desc)
                        else:
                            mem = oc.getMethod(name, desc)
                    except Exception:
                        continue
                    if mem is None:
                        continue
                    mods, decl = mem.getModifiers(), mem.getDeclaringClass()
                    same_pkg = str(decl.getPackageName()) == str(cc.getPackageName())
                    if Mod.isPrivate(mods) or (Mod.isPackage(mods) and not same_pkg) or (Mod.isProtected(mods) and not same_pkg
                                                                                       and not cc.subclassOf(decl)):
                        bad.append("%s.%s -> %s %s.%s%s" % (cn.rsplit(".", 1)[1], m.getName(), Mod.toString(mods),
                                                             decl.getName(), name, desc))
        return sorted(set(bad)), n_refs
    bad_old, n_old = access_problems(OLD)
    bad_new, n_new = access_problems(JAR)
    check(bad_old == [] and bad_new == [], "B. no inaccessible engine member: 0.1.5 %s, 0.1.6 %s" % (bad_old, bad_new))
    # the engine members the new classes reference (listed for the report; each is a public probe of the build)
    pool = CP(True)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendClassPath(JAR)
    refs = set()
    for short in ("VLL", "VLLFn", "VLLTask"):
        cc = pool.get(PKG + short)
        for k2, code in methods(cc).items():
            for t in code:
                mm = _re.match(r"\A(invoke\w+|getstatic|getfield) (?:Method |Field |InterfaceMethod )?(com\.hypixel\.[\w.$]+)\.(\w+)", t)
                if mm:
                    refs.add("%s.%s" % (mm.group(2).rsplit(".", 1)[1], mm.group(3)))
    eo, en = entries(OLD), entries(JAR)
    diff_e = sorted(n for n in eo if not n.endswith(".class") and n in en and eo[n] != en[n])
    check(sorted(n for n in eo if not n.endswith(".class")) == sorted(n for n in en if not n.endswith(".class")) and diff_e == ["manifest.json"],
          "B. the same non-class entries, only manifest.json differs: %s" % diff_e)
    mo_, mn_ = json.loads(eo["manifest.json"]), json.loads(en["manifest.json"])
    check(mn_.get("Version") == VERSION and dict((k2, v) for k2, v in mo_.items() if k2 not in ("Version", "Name")) ==
          dict((k2, v) for k2, v in mn_.items() if k2 not in ("Version", "Name")), "B. manifest: only Name / Version")
    print("B. %d classes byte-identical, %s version-only, changed as planned: %s (%d methods); inaccessible engine calls 0.1.5 %d -> "
          "0.1.6 %d (%d / %d engine refs); VLL engine refs: %s; only manifest.json among the other entries"
          % (n_same, ver_only, list(CODE), COUNT.get("B planned", 0), len(bad_old), len(bad_new), n_old, n_new, sorted(refs)))


# ------------------------------------------------------------------------------------------------ the stand-in universe
def common(JClass, L):
    from jpype import JShort, JByte
    import skyybuild as B
    UUID, Paths, Long, Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    System = JClass("java.lang.System")
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def jf(jcls, name):
        c = jcls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    def setf(obj, name, val):
        jf(obj.getClass(), name).set(obj, val)

    def sets(jcls, name, val):
        jf(jcls.class_, name).set(None, val)

    def jc(k, name):
        return JClass(PKG + name, loader=L[k])

    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", BR)
    CtPool = JClass("javassist.ClassPool")(True)
    CtPool.appendClassPath(B.SERVER_JAR)
    CtNM, CtNC, CtF = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def fake(name, sup, ctor, flds, meths, neighbor):
        c = CtPool.makeClass(name, CtPool.get(sup))
        for f in flds:
            c.addField(CtF.make(f, c))
        c.addConstructor(CtNC.make(ctor, c))
        for m in meths:
            c.addMethod(CtNM.make(m, c))
        return c.toClass(neighbor)

    # the item asset store: an empty map (Item.UNKNOWN for every id) so ItemStack constructors run
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    FS = fake("com.hypixel.hytale.assetstore.SkyyVault6Assets", "com.hypixel.hytale.assetstore.AssetStore",
              "public SkyyVault6Assets() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", [], [], AS.class_)
    st0 = U.allocateInstance(FS)
    jf(AS.class_, "assetMap").set(st0, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    sets(JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item"), "ASSET_STORE", st0)
    RF, SF_, CMP, CTY = ("com.hypixel.hytale.component.Ref", "com.hypixel.hytale.component.Store", "com.hypixel.hytale.component.Component",
                         "com.hypixel.hytale.component.ComponentType")
    TS = fake("com.hypixel.hytale.component.SkyyVault6Store", SF_,
              "public SkyyVault6Store() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
              "(com.hypixel.hytale.component.IResourceStorage) null); }",
              ["public static java.util.IdentityHashMap M = new java.util.IdentityHashMap();"],
              ["public %s getComponent(%s r, %s t) { java.util.Map m = (java.util.Map) M.get(r); if (m == null) return null; "
               "return (%s) m.get(t); }" % (CMP, RF, CTY, CMP)], JClass(SF_).class_)
    TSc = JClass("com.hypixel.hytale.component.SkyyVault6Store")
    PHc = JClass("com.hypixel.hytale.server.core.io.PacketHandler")
    TPH = fake("com.hypixel.hytale.server.core.io.SkyyVault6PH", "com.hypixel.hytale.server.core.io.PacketHandler",
               "public SkyyVault6PH() { super((com.hypixel.hytale.protocol.io.ChannelConnection) null, "
               "(com.hypixel.hytale.server.core.io.ProtocolVersion) null); }",
               ["public static java.util.ArrayList OUT = new java.util.ArrayList();"],
               ["public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }"], PHc.class_)
    P_ = "com.hypixel.hytale.server.core.entity.entities.player."
    WIN_A = P_ + "windows.Window[]"
    fake(P_ + "pages.SkyyVault6PM", P_ + "pages.PageManager", "public SkyyVault6PM() { super(); }",
         ["public static Object CUR = null;", "public static java.util.ArrayList OPENED = new java.util.ArrayList();"],
         ["public boolean setPageWithWindows(%s r, %s s, com.hypixel.hytale.protocol.packets.interface_.Page pg, boolean b, %s w) { "
          "CUR = null; for (int i = 0; i < w.length; i++) OPENED.add(w[i]); return true; }" % (RF, SF_, WIN_A),
          "public boolean openCustomPageWithWindows(%s r, %s s, %spages.CustomUIPage p, %s w) { CUR = p; "
          "for (int i = 0; i < w.length; i++) OPENED.add(w[i]); return true; }" % (RF, SF_, P_, WIN_A),
          "public void openCustomPage(%s r, %s s, %spages.CustomUIPage p) { CUR = p; }" % (RF, SF_, P_),
          "public %spages.CustomUIPage getCustomPage() { return (%spages.CustomUIPage) CUR; }" % (P_, P_)],
         JClass(P_ + "pages.PageManager").class_)
    PMS = JClass(P_ + "pages.SkyyVault6PM")
    CT = JClass(CTY)
    CT_PR, CT_PLA = CT(), CT()
    CT_INV = [CT() for _ in range(6)]
    Uni = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(Uni.class_)
    WU = UUID.fromString("00000000-0000-0000-0000-0000000000d1")
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    world = U.allocateInstance(World.class_)
    setf(world, "acceptingTasks", JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    Q = JClass("java.util.concurrent.LinkedBlockingDeque")()
    setf(world, "taskQueue", Q)
    setf(world, "name", "vaulttest6")
    # the world thread = THIS thread (TickingThread.isInThread: currentRun.get().thread == Thread.currentThread())
    RunC = Cls.forName("com.hypixel.hytale.server.core.util.thread.TickingThread$Run")
    rctor = RunC.getDeclaredConstructor(Cls.forName("java.lang.Thread"))
    rctor.setAccessible(True)
    RUN = rctor.newInstance(JClass("java.lang.Thread").currentThread())
    CURRUN = JClass("java.util.concurrent.atomic.AtomicReference")(RUN)
    setf(world, "currentRun", CURRUN)
    wmap = JClass("java.util.HashMap")()
    wmap.put(WU, world)
    setf(uni, "worldsByUuid", wmap)
    setf(uni, "playerRefComponentType", CT_PR)
    PLAYERS = JClass("java.util.concurrent.ConcurrentHashMap")()
    setf(uni, "playersByUuid", PLAYERS)
    PLIST = JClass("java.util.ArrayList")()
    setf(uni, "players", PLIST)
    sets(Uni, "instance", uni)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    setf(em, "playerComponentType", CT_PLA)
    for f, t in zip(("hotbarInventoryComponentType", "storageInventoryComponentType", "backpackInventoryComponentType",
                     "armorInventoryComponentType", "utilityInventoryComponentType", "toolInventoryComponentType"), CT_INV):
        setf(em, f, t)
    sets(EM, "instance", em)
    STORE = U.allocateInstance(TS)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Pla = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    WMc = JClass(P_ + "windows.WindowManager")
    IdM = JClass("java.util.IdentityHashMap")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INV = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    StorageC, HotbarC = JClass(INV + "Storage"), JClass(INV + "Hotbar")
    ISC = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD = JClass("org.bson.BsonDocument")

    def mkplayer(u, name):
        ref = U.allocateInstance(JClass(RF).class_)
        setf(ref, "store", STORE)
        pr = U.allocateInstance(PRc.class_)
        setf(pr, "uuid", u)
        setf(pr, "worldUuid", WU)
        setf(pr, "entity", ref)
        setf(pr, "username", name)
        setf(pr, "packetHandler", U.allocateInstance(TPH))
        p = U.allocateInstance(Pla.class_)
        setf(p, "pageManager", U.allocateInstance(PMS))
        comp = IdM()
        comp.put(CT_PR, pr)
        comp.put(CT_PLA, p)
        storage, hot = SIC(JShort(36)), SIC(JShort(9))
        comp.put(CT_INV[1], StorageC(storage))
        comp.put(CT_INV[0], HotbarC(hot, JByte(0)))
        TSc.M.put(ref, comp)
        PLAYERS.put(u, pr)
        PLIST.add(pr)
        return dict(pr=pr, p=p, ref=ref, storage=storage, hot=hot)

    UID = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    U2 = UUID.fromString("00000000-0000-0000-0000-0000000000c2")
    P1 = mkplayer(UID, "Tester")
    P2 = mkplayer(U2, "Other")
    return dict(JClass=JClass, U=U, jf=jf, setf=setf, sets=sets, jc=jc, BR=BR, UUID=UUID, Paths=Paths, Long=Long, Boolean=Boolean,
                Q=Q, world=world, CURRUN=CURRUN, RUN=RUN, PMS=PMS, WMc=WMc, ISC=ISC, BD=BD, SIC=SIC, STORE=STORE, UID=UID, U2=U2,
                P1=P1, P2=P2, PLAYERS=PLAYERS, PLIST=PLIST, PRc=PRc, JShort=JShort)


# ------------------------------------------------------------------------------------------------ C. the hook
def hook_section(E):
    from jpype import JClass, JArray, JImplements, JOverride, JObject
    jc, BR, Q, ISC, BD, SIC, JShort = E["jc"], E["BR"], E["Q"], E["ISC"], E["BD"], E["SIC"], E["JShort"]
    UID, U2, P1, P2, Paths, Long, jf = E["UID"], E["U2"], E["P1"], E["P2"], E["Paths"], E["Long"], E["jf"]
    US = str(UID)
    PK1, PK2 = US, US + "-p2"
    Cfg, Store, VS, Dat, LL, Cod = (jc("new", "VCfg"), jc("new", "VStore"), jc("new", "VSessions"), jc("new", "VData"), jc("new", "VLL"),
                                    jc("new", "VCodec"))
    WinC = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window")
    Obj = JClass("java.lang.Object")
    ACTIVE = [PK1]

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return ACTIVE[0] if str(u) == US else str(u)

    KEYFN = KeyFn()

    def tool(uid, lo, iid="Tool_Pickaxe_Iron"):
        return ISC(iid, 1, BD.parse('{"SkyyGear": {"v": 1, "kind": "tool", "ll": 1, "lu": "%s", "lo": "%s", "tr": 1}}' % (uid, lo)))

    def drain():
        n = 0
        while Q.size() > 0 and n < 60:
            Q.poll().run()
            n += 1
        return n

    def reset_mem(k="new"):
        St, V, LLk = jc(k, "VStore"), jc(k, "VSessions"), (jc(k, "VLL") if k == "new" else None)
        for m in ("CACHE", "PENDING", "BUYING", "LASTBUY", "NAMES"):
            getattr(St, m).clear()
        St.SAVER = None
        St.STOPPING = False
        for m in ("SESSIONS", "LAST", "EPOCHS", "SWITCHED", "BUSYSEEN", "ONLINE"):
            getattr(V, m).clear()
        if LLk is not None:
            for m in ("PEND", "QUEUED", "SEEN", "HELD"):
                getattr(LLk, m).clear()
            LLk.CRASH = 0
            LLk.PEND_MS = 5000
            LLk.HOLD_MS = 30000
        jc(k, "VCfg").WARNED.clear()
        Q.clear()

    def point(d, k="new"):
        C = jc(k, "VCfg")
        C.DIR = Paths.get(d)
        C.VDIR = Paths.get(d).resolve("vaults")
        C.FILE = Paths.get(d).resolve("config.properties")
        C.LOGF = Paths.get(d).resolve("vault.log")
        C.NAMESF = Paths.get(d).resolve("names.properties")
        C.FREE_PAGES, C.MAX_PAGES, C.SLOTS = 2, 10, 36
        C.ARROWS, C.ARROW_LAYOUT = True, "row"
        C.PAGE_MODE, C.OPEN_MODE = False, "chest"
        C.AFTER_SWITCH_MS, C.SAVE_DELAY_MS = 30000, 1000

    def clear_inv(P):
        for c in (P["storage"], P["hot"]):
            c.clear()

    def setup(name, full=False):
        d = os.path.join(WORK, "ll", name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(os.path.join(d, "vaults"))
        point(d)
        reset_mem()
        BR.clear()
        BR.put("profile:fn:key", KEYFN)
        ACTIVE[0] = PK1
        E["CURRUN"].set(E["RUN"])
        clear_inv(P1)
        clear_inv(P2)
        P1["storage"].setItemStackForSlot(JShort(0), ISC("Test_Inv_0", 2), False)
        vd = Dat(UID, 36)
        vd.unlocked = 3
        vd.page(3)
        for pg in (1, 2, 3):
            arr = vd.page(pg)
            for i in range(36 if full else 4):
                arr[i] = ISC("Test_P%d_S%d" % (pg, i), 1 + i % 5)
        vd.page(2)[5] = tool("uidA", PK1)           # the lifelong pickaxe of profile 1: page 2 slot 6
        vd.page(3)[7] = tool("uidA", PK2)           # a stack with the same uid but owned by profile 2 (wrong profile)
        vd.page(1)[9] = tool("uidB", PK1, "Tool_Hatchet_Iron")
        vd.rev = 1
        Store.CACHE.put(UID, vd)
        check(bool(LL.persist(vd)), "C. %s: the starting vault file is written" % name)
        return d, vd

    def vfile(d, u=UID):
        p = os.path.join(d, "vaults", "%s.json" % u)
        return json.loads(open(p, encoding="utf8").read()) if os.path.exists(p) else None

    def doc_count(doc, uid="uidA", lo=PK1):
        """copies of the tool in one vault document (content + orphans)"""
        n = 0
        for pgd in doc.get("content", []):
            for sd in pgd.get("slots", []):
                g = (sd.get("meta") or {}).get("SkyyGear") or {}
                if g.get("lu") == uid and g.get("lo") == lo:
                    n += 1
        for sd in doc.get("orphans", []):
            g = (sd.get("meta") or {}).get("SkyyGear") or {}
            if g.get("lu") == uid and g.get("lo") == lo:
                n += 1
        return n

    def count_uid(d, uid="uidA", lo=PK1, inv=True):
        """copies of the tool: in the vault FILE (content + orphans) + the inventory (as the engine has it)"""
        n = 0
        doc = vfile(d)
        if doc:
            for pgd in doc.get("content", []):
                for sd in pgd.get("slots", []):
                    g = (sd.get("meta") or {}).get("SkyyGear") or {}
                    if g.get("lu") == uid and g.get("lo") == lo:
                        n += 1
            for sd in doc.get("orphans", []):
                g = (sd.get("meta") or {}).get("SkyyGear") or {}
                if g.get("lu") == uid and g.get("lo") == lo:
                    n += 1
        if inv:
            for c in (P1["storage"], P1["hot"]):
                for i in range(int(c.getCapacity())):
                    if LL.match(c.getItemStack(JShort(i)), lo, uid):
                        n += 1
        return n

    def mem_count(vd, uid="uidA", lo=PK1):
        n = 0
        for pg in range(1, int(vd.unlocked) + 1):
            for x in vd.pageCopy(pg):
                if LL.match(x, lo, uid):
                    n += 1
        return n

    def num(v):
        """an EXTENDED-JSON number ({"$numberInt": "2"}) as an int"""
        if isinstance(v, dict):
            v = next(iter(v.values()))
        return None if v is None else int(v)

    def file_where(d, uid="uidA", lo=PK1):
        doc = vfile(d)
        out = []
        for pgd in doc.get("content", []):
            for sd in pgd.get("slots", []):
                g = (sd.get("meta") or {}).get("SkyyGear") or {}
                if g.get("lu") == uid and g.get("lo") == lo:
                    out.append(("slot", num(pgd["page"]), num(sd["slot"])))
        for sd in doc.get("orphans", []):
            g = (sd.get("meta") or {}).get("SkyyGear") or {}
            if g.get("lu") == uid and g.get("lo") == lo:
                out.append(("held" if "lld" in sd else "pend" if "llt" in sd else "orphan", num(sd.get("page")), num(sd.get("slot"))))
        return out

    def place_inv(x):
        """the caller's placing: first empty storage slot, read back"""
        c = P1["storage"]
        for i in range(int(c.getCapacity())):
            cur = c.getItemStack(JShort(i))
            if cur is None or cur.isEmpty():
                c.setItemStackForSlot(JShort(i), x, False)
                return c.getItemStack(JShort(i)) is not None and LL.match(c.getItemStack(JShort(i)), PK1, "uidA")
        return False

    def log_lines(d):
        p = os.path.join(d, "vault.log")
        return open(p, encoding="utf8").read().splitlines() if os.path.exists(p) else []

    def restart(d, k="new"):
        """a crash + restart: every in-memory state dropped, the vault re-read from its file (the join scan of the 1 s tick for 0.1.6)"""
        point(d, k)
        reset_mem(k)
        if k == "new":
            LL.tick()                                   # the join scan: a file with a pending take is read now
            got = Store.CACHE.get(UID)
            return got if got is not None else Store.load(UID)
        return jc(k, "VStore").load(UID)

    def resolve_now():
        """the dangling-take path: PEND_MS 0, the 1 s tick queues ONE VLLTask on the owner's world, the world runs it; HOLD_MS 0 + a
        second tick: the placed notes of closed takes leave the file (as 30 s later in game)"""
        LL.PEND_MS = 0
        LL.HOLD_MS = 0
        LL.tick()
        n = drain()
        LL.tick()
        LL.PEND_MS = 5000
        LL.HOLD_MS = 30000
        return n

    def settle():
        """the 30 s hold after doneLL is over: the placed note leaves the file (time only)"""
        LL.HOLD_MS = 0
        LL.holdTick()
        LL.HOLD_MS = 30000

    def open_vault(page):
        wm = E["WMc"]()
        jf(E["WMc"].class_, "windowId").get(wm).set(100)
        E["setf"](P1["p"], "windowManager", wm)
        E["PMS"].OPENED.clear()
        line = VS.open2(P1["pr"], P1["ref"], E["STORE"], page, 2, None)
        s = VS.current(UID)
        win = E["PMS"].OPENED.get(0) if E["PMS"].OPENED.size() > 0 else None
        if win is not None:
            wm.setWindow(7, win)                       # the engine's own registration (its container change listener)
            jf(WinC.class_, "isDirty").get(win).set(False)
        drain()
        return s, win, line

    def jobj(*xs):
        a = JArray(Obj)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    # ---- 1. find
    d, vd = setup("find")
    reset_mem()                                         # not loaded: find reads the file
    check(str(LL.find(UID, PK1, "uidA")) == "2:6", "C1. find on a closed (unloaded) vault -> 2:6: %s" % LL.find(UID, PK1, "uidA"))
    check(str(LL.find(UID, PK2, "uidA")) == "3:8", "C1. find for profile 2 finds ITS stack (same uid, lo = p2) -> 3:8")
    check(str(LL.find(UID, PK1, "uidB")) == "1:10", "C1. find the hatchet -> 1:10")
    check(LL.find(UID, PK1, "uidZ") is None, "C1. find a uid not in the vault -> null")
    check(LL.find(UID, US + "-p3", "uidA") is None, "C1. find for a profile with no stack there -> null (wrong profile)")
    check(LL.find(U2, PK1, "uidA") is None, "C1. find in another player's (missing) vault -> null")
    check(LL.find(None, PK1, "uidA") is None and LL.find(UID, None, "uidA") is None and LL.find(UID, PK1, "") is None,
          "C1. bad arguments -> null")
    U3 = E["UUID"].fromString("00000000-0000-0000-0000-0000000000e3")
    open(os.path.join(d, "vaults", "%s.json" % U3), "w").write("{ not json")
    check(str(LL.find(U3, str(U3), "uidA")) == "!unreadable", "C1. an unreadable vault file -> !unreadable")
    fn1 = jc("new", "VLLFn")(1)
    check(str(fn1.apply(jobj(UID, PK1, "uidA"))) == "2:6" and fn1.apply(jobj(UID)) is None and fn1.apply(JObject("x", Obj)) is None,
          "C1. vault:fn:findLL through the bridge Function: 2:6 / null on short or wrong arguments")
    before = open(os.path.join(d, "vaults", "%s.json" % UID), "rb").read()
    check(open(os.path.join(d, "vaults", "%s.json" % UID), "rb").read() == before and not os.path.exists(os.path.join(d, "vault.log")),
          "C1. find changes nothing (file, vault.log)")
    print("C1. find: closed / profile 2 / hatchet / missing / wrong profile / other player / bad args / unreadable / bridge - ok")

    # ---- 2. take from a CLOSED vault, place, doneLL
    d, vd = setup("take-closed")
    reset_mem()                                         # closed AND not loaded: take reads the file
    fn2, fn3, fn4 = jc("new", "VLLFn")(2), jc("new", "VLLFn")(3), jc("new", "VLLFn")(4)
    r = fn2.apply(jobj(UID, PK1, "uidA"))
    ok = check(r is not None and not isinstance(r, str) and len(r) == 3, "C2. takeLL from a closed vault returns { token, stack, where }: %s" % r)
    if ok:
        tok, x, where = str(r[0]), r[1], str(r[2])
        vd = Store.CACHE.get(UID)
        check(where == "2:6" and LL.match(x, PK1, "uidA") and int(x.getQuantity()) == 1, "C2. the exact stack, from 2:6")
        check(mem_count(vd) == 0 and LL.PEND.containsKey(tok) and int(Cod.pendCount(vd.orphans)) == 1,
              "C2. in memory: out of the page, one pending record, PEND holds the token")
        check(file_where(d) == [("pend", 2, 5)] and count_uid(d) == 1,
              "C2. SAVED before it returned: the file holds the tool as a pending record only (%s)" % file_where(d))
        check(str(LL.find(UID, PK1, "uidA")) == "!pending", "C2. find while the take is open -> !pending")
        check(str(fn2.apply(jobj(UID, PK1, "uidA"))).startswith("-That tool is already on its way"), "C2. a second take -> refused")
        check(fn3.apply(jobj(U2, tok)) == False and str(fn4.apply(jobj(U2, tok))).startswith("-That fetch belongs to another player"),
              "C2. doneLL / putBack with another player's UUID -> FALSE / refused")
        check(fn3.apply(jobj(UID, "nope")) == False and str(fn4.apply(jobj(UID, "nope"))).startswith("-Nothing to put back"),
              "C2. unknown token -> FALSE / refused")
        check(place_inv(x), "C2. the caller places it in the inventory")
        res = fn3.apply(jobj(UID, tok))
        check(res == True and not LL.PEND.containsKey(tok) and LL.HELD.containsKey(tok) and int(Cod.pendCount(vd.orphans)) == 1, "C2. doneLL -> TRUE, the take is closed (its record held as a placed note)")
        check(file_where(d) == [("held", 2, 5)] and count_uid(d, inv=False) == 1 and LL.HELD.containsKey(tok),
              "C2. after doneLL: in the inventory, and the vault file keeps a PLACED note for 30 s (file %s)" % file_where(d))
        check(LL.find(UID, PK1, "uidA") is None, "C2. find during the hold -> null (the note is not a pending take)")
        check(fn3.apply(jobj(UID, tok)) == False, "C2. a second doneLL -> FALSE")
        check(str(fn4.apply(jobj(UID, tok))).startswith("-Nothing to put back"), "C2. putBack after doneLL -> refused")
        LL.tick()
        check(LL.HELD.containsKey(tok) and file_where(d) == [("held", 2, 5)], "C2. within the 30 s the tick keeps the note")
        settle()
        check(file_where(d) == [] and count_uid(d) == 1 and LL.HELD.isEmpty() and int(vd.orphans.size()) == 0,
              "C2. after the hold: the note left the file, only in the inventory (file %s)" % file_where(d))
        lg = log_lines(d)
        check(any(" LL-TAKE %s %s uidA page 2 slot 6 Tool_Pickaxe_Iron token %s" % (US, PK1, tok) in l for l in lg) and
              any(" LL-DONE %s token %s" % (US, tok) in l for l in lg) and any(" LL-CLOSED %s token %s" % (US, tok) in l for l in lg),
              "C2. vault.log: LL-TAKE + LL-DONE + LL-CLOSED: %s" % lg)
        check(str(LL.find(UID, PK1, "uidA")) == "None" or LL.find(UID, PK1, "uidA") is None, "C2. find afterwards -> null")
    print("C2. take from a closed vault: saved as pending before return, place, doneLL closes it, exactly one copy at every step")

    # ---- 3. the gates (nothing moves; the file is untouched)
    d, vd = setup("gates")
    f0 = open(os.path.join(d, "vaults", "%s.json" % UID), "rb").read()
    E["CURRUN"].set(None)
    check(str(LL.take(UID, PK1, "uidA")).startswith("-The Vault hands a tool out only on your own world"), "C3. not the world thread -> refused")
    E["CURRUN"].set(E["RUN"])
    BR.put("profile:busy:" + US, E["Boolean"].TRUE)
    check(str(LL.take(UID, PK1, "uidA")).startswith("-Your Vault is shut"), "C3. profile busy -> refused")
    BR.remove("profile:busy:" + US)
    check(str(LL.take(UID, PK1, "uidA")).startswith("-Your Vault is shut"), "C3. just after busy ended (the settle window) -> refused")
    VS.SWITCHED.clear()
    VS.BUSYSEEN.clear()
    ACTIVE[0] = PK2
    check(str(LL.take(UID, PK1, "uidA")).startswith("-Your profile is changing"), "C3. pkey is not the active profile -> refused")
    ACTIVE[0] = PK1
    check(str(LL.take(UID, PK1, "uidZ")) == "-It is not in your Vault.", "C3. a uid not in the vault -> -It is not in your Vault.")
    check(str(LL.take(UID, US + "-p3", "uidA")).startswith("-Your profile is changing"), "C3. a profile that is not active -> refused")
    check(str(LL.take(U2, str(U2), "uidA")) == "-It is not in your Vault.", "C3. another player (their own empty vault) -> not there")
    check(open(os.path.join(d, "vaults", "%s.json" % UID), "rb").read() == f0 and mem_count(vd) == 1 and LL.PEND.isEmpty(),
          "C3. every refusal left the vault file, memory and PEND untouched")
    # wrong profile, the RIGHT way round: profile 2 active takes ITS stack, never profile 1's
    ACTIVE[0] = PK2
    r = LL.take(UID, PK2, "uidA")
    check(not isinstance(r, str) and str(r[2]) == "3:8" and mem_count(vd) == 1 and mem_count(vd, lo=PK2) == 0,
          "C3. profile 2 takes its own uidA stack (3:8); profile 1's stack stays: %s" % r)
    if not isinstance(r, str):
        check(LL.back(UID, str(r[0]), "test") == "+3:8", "C3. ... and puts it back to 3:8")
    ACTIVE[0] = PK1
    print("C3. gates: thread / busy / settle / inactive profile / missing / other player refused with nothing changed; wrong profile")

    # ---- 4. take while OPEN on the page on screen (through the live container), then putBack
    d, vd = setup("take-open")
    s, win, _l = open_vault(2)
    if check(s is not None and win is not None and int(s.page) == 2, "C4. a real /vault session on page 2"):
        check(LL.match(s.view.getItemStack(JShort(5)), PK1, "uidA"), "C4. the tool is in the live container slot 6")
        r = LL.take(UID, PK1, "uidA")
        ok = check(not isinstance(r, str), "C4. take from the open vault: %s" % r)
        if ok:
            tok, x = str(r[0]), r[1]
            v5 = s.view.getItemStack(JShort(5))
            check((v5 is None or v5.isEmpty()) and mem_count(vd) == 0, "C4. gone from the live container AND the page array")
            check(bool(jf(WinC.class_, "isDirty").get(win).get()), "C4. the window is marked to re-send (the player sees it go)")
            check(not bool(s.swapping) and not bool(s.closed), "C4. the session is still open and not swapping")
            VS.syncView(s)
            check(mem_count(vd) == 0 and file_where(d) == [("pend", 2, 5)], "C4. a later view sync does not bring it back; the file: pending")
            check(any("(from the open vault)" in l for l in log_lines(d)), "C4. vault.log names the open vault")
            res = LL.back(UID, tok, "test")
            v5 = s.view.getItemStack(JShort(5))
            check(str(res) == "+2:6" and v5 is not None and LL.match(v5, PK1, "uidA") and mem_count(vd) == 1,
                  "C4. putBack -> +2:6, back in the live container and the array: %s" % res)
            check(file_where(d) == [("slot", 2, 5)] and count_uid(d) == 1 and not LL.PEND.containsKey(tok),
                  "C4. the file holds it in its slot again, one copy")
            # take again while open, place, done; then close the vault: the close sync does not resurrect it
            r2 = LL.take(UID, PK1, "uidA")
            if check(not isinstance(r2, str), "C4. a second take while open"):
                place_inv(r2[1])
                check(LL.done(UID, str(r2[0])) == True, "C4. doneLL")
                VS.finalizeWorld(s)
                drain()
                settle()
                check(file_where(d) == [] and count_uid(d) == 1 and mem_count(vd) == 0, "C4. after the vault closed: only in the inventory")
    print("C4. take while open on the page on screen: through the live container (window re-sent), putBack into it, close keeps it out")

    # ---- 5. take while OPEN on ANOTHER page (taken from the stored page), and putBack into a taken slot
    d, vd = setup("take-open-other")
    s, win, _l = open_vault(1)
    if check(s is not None and int(s.page) == 1, "C5. a real /vault session on page 1"):
        before_view = [str(s.view.getItemStack(JShort(i)).getItemId()) if s.view.getItemStack(JShort(i)) is not None else None for i in range(36)]
        r = LL.take(UID, PK1, "uidA")
        if check(not isinstance(r, str) and str(r[2]) == "2:6", "C5. take from page 2 while page 1 is on screen: %s" % r):
            after_view = [str(s.view.getItemStack(JShort(i)).getItemId()) if s.view.getItemStack(JShort(i)) is not None else None for i in range(36)]
            check(before_view == after_view and mem_count(vd) == 0, "C5. the live container (page 1) untouched, page 2 array emptied")
            VS.swap(s, 2)
            v5 = s.view.getItemStack(JShort(5))
            check(v5 is None or v5.isEmpty(), "C5. turning to page 2 shows the slot empty")
            s.view.setItemStackForSlot(JShort(5), ISC("Test_Filler", 3), False)      # the player puts something in its slot
            res = LL.back(UID, str(r[0]), "test")
            check(str(res) == "+1:5", "C5. putBack with its slot taken -> the first free slot of an owned page (1:5): %s" % res)
            check(count_uid(d) == 1 and file_where(d) == [("slot", 1, 4)] and mem_count(vd) == 1, "C5. one copy, in the file at 1:5")
            VS.finalizeWorld(s)
            drain()
            check(file_where(d) == [("slot", 1, 4)] and count_uid(d) == 1, "C5. after the close: still 1:5, one copy")
    print("C5. take while open on another page + putBack into a taken slot (first free slot) - ok")

    # ---- 6. putBack into a FULL vault: kept as a saved plain orphan, placed back at the next start
    d, vd = setup("full", full=True)
    vd.page(2)[5] = tool("uidA", PK1)
    vd.rev = vd.rev + 1
    LL.persist(vd)
    r = LL.take(UID, PK1, "uidA")
    if check(not isinstance(r, str), "C6. take from a full vault"):
        vd.page(2)[5] = ISC("Test_Late", 1)          # the freed slot fills up again (the whole vault is full)
        res = LL.back(UID, str(r[0]), "test")
        check(str(res).startswith("=Your Vault is full") and file_where(d) == [("orphan", 2, 5)] and count_uid(d) == 1,
              "C6. putBack into a full vault -> '=' + kept as a plain orphan in the file: %s %s" % (res, file_where(d)))
        vd.page(2)[5] = None
        vd.rev = vd.rev + 1
        LL.persist(vd)
        vd2 = restart(d)
        check(vd2 is not None and mem_count(vd2) == 1 and LL.match(vd2.page(2)[5], PK1, "uidA") and int(vd2.orphans.size()) == 0,
              "C6. at the next start (slot free again) it is placed back into 2:6")
    print("C6. putBack into a full vault keeps it as a saved orphan; the next start places it back")

    # ---- 7. a FAILED write: the take is undone (closed and open), nothing returned
    for mode in ("closed", "open"):
        d, vd = setup("writefail-" + mode)
        s = None
        if mode == "open":
            s, win, _l = open_vault(2)
        tmpd = os.path.join(d, "vaults", "%s.json.tmp" % UID)
        os.makedirs(tmpd)                                 # the atomic write's tmp file cannot be created -> the write fails
        f0 = open(os.path.join(d, "vaults", "%s.json" % UID), "rb").read()
        res = LL.take(UID, PK1, "uidA")
        check(isinstance(res, str) and str(res).startswith("-Your Vault could not be saved"), "C7 %s. a failed write -> refused: %s" % (mode, res))
        check(mem_count(vd) == 1 and LL.match(vd.page(2)[5], PK1, "uidA") and int(vd.orphans.size()) == 0 and LL.PEND.isEmpty(),
              "C7 %s. undone in memory: back in 2:6, no pending record" % mode)
        if s is not None:
            check(LL.match(s.view.getItemStack(JShort(5)), PK1, "uidA"), "C7 open. back in the live container slot 6")
        check(open(os.path.join(d, "vaults", "%s.json" % UID), "rb").read() == f0 and count_uid(d) == 1,
              "C7 %s. the file is unchanged (the tool in its slot)" % mode)
        check(any("LL-TAKE-FAIL" in l for l in log_lines(d)), "C7 %s. vault.log LL-TAKE-FAIL" % mode)
        os.rmdir(tmpd)
        if s is not None:
            VS.finalizeWorld(s)
            drain()
            check(file_where(d) == [("slot", 2, 5)] and count_uid(d) == 1, "C7 open. after the close: in 2:6, one copy")
    print("C7. a failed file write undoes the take (closed and open vault): nothing returned, nothing lost")

    # ---- 8. CRASH POINTS: every crash + restart leaves exactly one tool, wherever the engine saved the inventory
    def crash_case(name, cp, placed_in_inv_saved, want_after):
        """cp = the crash point (1 take before the write, 2 take after the write, 3 done before its write, 4 putBack before its write,
        0 = no crash in the hook: the crash comes right after doneLL); placed_in_inv_saved = the inventory the restarted server loads
        holds the tool (the engine saved the player after the placing)"""
        d, vd = setup("crash-" + name)
        tok = None
        x = None
        LL.CRASH = cp if cp in (1, 2) else 0
        try:
            r = LL.take(UID, PK1, "uidA")
            if not isinstance(r, str):
                tok, x = str(r[0]), r[1]
        except Exception as e:
            check("test crash point %d" % cp in str(e), "C8 %s. the crash point fired: %s" % (name, e))
        LL.CRASH = 0
        if cp == 2:
            # the take is saved but the caller never got the stack: x stays None
            pass
        if cp in (3, 4, 0):
            check(tok is not None, "C8 %s. take ok" % name)
            if cp in (3, 0):
                place_inv(x)
                LL.CRASH = 3 if cp == 3 else 0
                try:
                    LL.done(UID, tok)
                except Exception as e:
                    check("test crash point 3" in str(e), "C8 %s. crash point 3 fired: %s" % (name, e))
                LL.CRASH = 0
            else:
                LL.CRASH = 4
                try:
                    LL.back(UID, tok, "test")
                except Exception as e:
                    check("test crash point 4" in str(e), "C8 %s. crash point 4 fired: %s" % (name, e))
                LL.CRASH = 0
        # the SAVED state at the crash: the vault file + the inventory as the engine saved it
        clear_inv(P1)
        if placed_in_inv_saved:
            place_inv(x if x is not None else tool("uidA", PK1))
        saved_where = file_where(d)
        vd2 = restart(d)
        n_pend = int(LL.PEND.size())
        find_after_restart = LL.find(UID, PK1, "uidA")
        n = resolve_now()
        total = count_uid(d)
        check(total == 1, "C8 %s. EXACTLY ONE tool after the crash + restart + resolve: %d (file at crash %s, inventory %s, now %s)"
              % (name, total, saved_where, placed_in_inv_saved, file_where(d)))
        where = "inventory" if count_uid(d, inv=True) - count_uid(d, inv=False) == 1 else "vault"
        check(where == want_after and LL.PEND.isEmpty() and int(Cod.pendCount(vd2.orphans)) == 0,
              "C8 %s. ends in the %s (want %s), no take left open (file %s, %d task(s), pending at restart %d, find %s)"
              % (name, where, want_after, file_where(d), n, n_pend, find_after_restart))
        tally("C8 crash cases")
        return d, saved_where, n_pend, find_after_restart

    d1, w1, p1, f1 = crash_case("cp1", 1, False, "vault")
    check(w1 == [("slot", 2, 5)] and p1 == 0 and str(f1) == "2:6", "C8 cp1. the crash before the write: the file still has it in 2:6")
    d2, w2, p2, f2 = crash_case("cp2", 2, False, "vault")
    check(w2 == [("pend", 2, 5)] and p2 == 1 and str(f2) == "!pending", "C8 cp2. the crash after the write: a pending record, read back as pending")
    check(any("LL-PENDING" in l for l in log_lines(d2)) and any("LL-BACK" in l and "auto: not in the inventory" in l for l in log_lines(d2)),
          "C8 cp2. vault.log: LL-PENDING at the join scan, LL-BACK (auto) by the resolve")
    d3, w3, p3, f3 = crash_case("cp2-placed", 2, True, "inventory")
    check(any("LL-AUTODONE" in l for l in log_lines(d3)), "C8 cp2-placed. the tool was already in the saved inventory -> LL-AUTODONE (no dupe)")
    crash_case("cp3", 3, True, "inventory")
    crash_case("cp3-notsaved", 3, False, "vault")
    crash_case("cp4", 4, False, "vault")
    d0, w0, p0, f0_ = crash_case("after-done", 0, True, "inventory")
    check(w0 == [("held", 2, 5)] and p0 == 1 and str(f0_) == "!pending",
          "C8 after-done. the file still holds the placed note; after the restart it is a pending take again (%s, %d, %s)" % (w0, p0, f0_))
    check(any("LL-AUTODONE" in l for l in log_lines(d0)), "C8 after-done. in the saved inventory -> LL-AUTODONE (no dupe)")
    # fix round ("never loss"): the engine did NOT save the inventory after doneLL (a crash inside its 10 s tick): the placed note brings
    # the tool back into the Vault - 0.1.6 before the fix lost it here (0 copies)
    dU, wU, pU, fU = crash_case("after-done-unsaved", 0, False, "vault")
    check(wU == [("held", 2, 5)] and any("LL-BACK" in l and "auto: not in the inventory" in l for l in log_lines(dU))
          and file_where(dU) == [("slot", 2, 5)],
          "C8 after-done-unsaved. crash after doneLL before the engine's player save -> back into 2:6, one copy (was 0 before the fix)")
    # the crash comes when the hold is over (the note already left the file): the engine has saved the inventory by then
    d, vd = setup("after-hold")
    r = LL.take(UID, PK1, "uidA")
    place_inv(r[1])
    LL.done(UID, str(r[0]))
    settle()
    check(file_where(d) == [] and count_uid(d) == 1, "C8 after-hold. the note is gone after 30 s, the saved inventory holds the tool")
    restart(d)
    resolve_now()
    check(count_uid(d) == 1 and file_where(d) == [] and LL.PEND.isEmpty(), "C8 after-hold. restart: one copy, nothing pending")
    print("C8. crash points 1-4 + after doneLL (inventory saved or not) + after the hold: exactly one tool after every crash + restart "
          "(%d cases)" % COUNT.get("C8 crash cases", 0))

    # ---- 8b. the 30 s hold at run time: time only - a tool moved out of the inventory meanwhile is never put back (no dupe)
    d, vd = setup("hold-chest")
    r = LL.take(UID, PK1, "uidA")
    tok = str(r[0])
    place_inv(r[1])
    LL.done(UID, tok)
    clear_inv(P1)                                      # the player put it in a chest within the 30 s
    resolve_now()
    check(file_where(d) == [] and mem_count(vd) == 0 and LL.HELD.isEmpty() and LL.PEND.isEmpty() and count_uid(d) == 0
          and not any("LL-BACK" in l for l in log_lines(d)),
          "C8b. the hold ends by time: no inventory check, nothing put back (the chest holds the one copy)")
    # a take of the SAME tool again during the hold (the player put it back into the vault and fetched it again): two records; a
    # crash before the engine saved the inventory -> the restart resolves both to ONE copy in the vault
    d, vd = setup("hold-retake")
    r = LL.take(UID, PK1, "uidA")
    place_inv(r[1])
    LL.done(UID, str(r[0]))
    clear_inv(P1)
    vd.page(1)[20] = r[1]                              # the player put it into the vault again (1:21)
    vd.rev = vd.rev + 1
    LL.persist(vd)
    r2 = LL.take(UID, PK1, "uidA")
    ok2 = check(not isinstance(r2, str) and str(r2[2]) == "1:21", "C8b. the second take during the hold: %s" % r2)
    if ok2:
        place_inv(r2[1])
        LL.done(UID, str(r2[0]))
        check(sorted(file_where(d)) == [("held", 1, 20), ("held", 2, 5)], "C8b. two placed notes in the file: %s" % file_where(d))
        clear_inv(P1)                                  # the engine never saved the inventory
        restart(d)
        resolve_now()
        check(count_uid(d) == 1 and LL.PEND.isEmpty() and int(Cod.pendCount(Store.CACHE.get(UID).orphans)) == 0,
              "C8b. crash with two notes, inventory not saved -> exactly one copy back in the vault: %s" % file_where(d))
        check(any("already back in a vault slot" in l for l in log_lines(d)), "C8b. the second note closes because the tool is back in a slot")
    print("C8b. the 30 s hold: time-only end (no dupe from a chest), a re-take during the hold resolves to one copy")

    # ---- 9. ROLLBACK: a crash file (pending record) read by 0.1.5 puts the tool back into its slot
    d, vd = setup("rollback")
    LL.CRASH = 2
    try:
        LL.take(UID, PK1, "uidA")
    except Exception:
        pass
    LL.CRASH = 0
    check(file_where(d) == [("pend", 2, 5)], "C9. the crash file holds a pending record")
    vo = restart(d, "old")
    check(vo is not None and LL.match(vo.page(2)[5], PK1, "uidA") and int(vo.orphans.size()) == 0,
          "C9. 0.1.5 reads it as an ordinary orphan and places it back into 2:6 (rollback never loses it)")
    point(d, "new")
    print("C9. rollback: 0.1.5 places a pending record back into its slot")

    # ---- 10. a take left open by the caller (no doneLL / putBack): the Vault resolves it itself after PEND_MS
    d, vd = setup("dangling")
    r = LL.take(UID, PK1, "uidA")
    LL.tick()
    check(drain() == 0 and LL.PEND.size() == 1, "C10. within PEND_MS nothing is resolved")
    place_inv(r[1])                                    # the caller placed it but forgot doneLL
    resolve_now()
    check(LL.PEND.isEmpty() and count_uid(d) == 1 and file_where(d) == [], "C10. placed but not closed -> LL-AUTODONE, one copy (inventory)")
    d, vd = setup("dangling-back")
    r = LL.take(UID, PK1, "uidA")                      # the caller dropped it on the floor of its own code (never placed)
    resolve_now()
    check(LL.PEND.isEmpty() and count_uid(d) == 1 and file_where(d) == [("slot", 2, 5)], "C10. never placed -> put back into 2:6")
    # waits while the gate is shut and while another profile is active
    d, vd = setup("dangling-wait")
    r = LL.take(UID, PK1, "uidA")
    BR.put("profile:busy:" + US, E["Boolean"].TRUE)
    resolve_now()
    check(LL.PEND.size() == 1 and file_where(d) == [("pend", 2, 5)], "C10. profile busy -> the take stays open (saved)")
    BR.remove("profile:busy:" + US)
    VS.BUSYSEEN.clear()
    VS.SWITCHED.clear()
    ACTIVE[0] = PK2
    resolve_now()
    check(LL.PEND.size() == 1, "C10. another profile active -> the take waits (its inventory is not on the player)")
    ACTIVE[0] = PK1
    E["CURRUN"].set(None)
    LL.PEND_MS = 0
    LL.tick()
    check(LL.QUEUED.containsKey(UID), "C10. the tick queues one task on the owner's world")
    E["Q"].poll().run()                               # the world ran it on another thread: refused, re-queued later
    check(LL.PEND.size() == 1 and not LL.QUEUED.containsKey(UID), "C10. a resolve off the world thread does nothing")
    E["CURRUN"].set(E["RUN"])
    LL.PEND_MS = 5000
    resolve_now()
    check(LL.PEND.isEmpty() and count_uid(d) == 1 and file_where(d) == [("slot", 2, 5)], "C10. back on the world thread -> put back")
    # an offline owner: never resolved while offline
    d, vd = setup("dangling-offline")
    r = LL.take(UID, PK1, "uidA")
    E["PLIST"].remove(P1["pr"])
    resolve_now()
    check(LL.PEND.size() == 1 and file_where(d) == [("pend", 2, 5)], "C10. owner offline -> stays pending (saved)")
    E["PLIST"].add(P1["pr"])
    resolve_now()
    check(LL.PEND.isEmpty() and count_uid(d) == 1, "C10. owner back online -> resolved")
    # a STALE PEND entry (its record already closed - e.g. a find on another thread re-registered it a moment before doneLL): never a dupe
    d, vd = setup("stale")
    r = LL.take(UID, PK1, "uidA")
    tok = str(r[0])
    ent = LL.PEND.get(tok)
    place_inv(r[1])
    LL.done(UID, tok)
    LL.PEND.put(tok, ent)
    check(str(LL.back(UID, tok, "test")).startswith("-Nothing to put back") and not LL.PEND.containsKey(tok) and mem_count(vd) == 0
          and file_where(d) == [("held", 2, 5)] and count_uid(d, inv=False) == 1,
          "C10. putBack of a stale entry (its take closed, the placed note held) -> refused, dropped, nothing placed")
    LL.PEND.put(tok, ent)
    check(LL.done(UID, tok) == False and not LL.PEND.containsKey(tok), "C10. doneLL of a stale entry -> FALSE, dropped")
    LL.PEND.put(tok, ent)
    clear_inv(P1)                                      # even with the tool gone from the inventory the stale entry adds nothing
    resolve_now()
    check(LL.PEND.isEmpty() and count_uid(d) == 0 and mem_count(vd) == 0, "C10. a stale entry resolved -> dropped, no copy made")
    print("C10. takes left open resolve themselves (placed -> closed, not placed -> put back), waiting on busy / profile / thread / offline")

    # ---- 11. /vault info: a pending record is not a missing-item orphan
    d, vd = setup("info")
    LL.take(UID, PK1, "uidA")
    lines = [str(x) for x in Store.infoLines(UID, 0, False)]
    check(not any("belong to items this server does not have" in l for l in lines) and
          any("lifelong tool(s) on the way from the vault to your inventory" in l for l in lines), "C11. /vault info: %s" % lines)
    print("C11. /vault info names a pending take, not a missing item")

    # ---- 12. (fix round) a snapshot never sees a change made after it: VStore.toDoc deep-copies the orphans under the monitor
    def snap_doc(sn):
        return json.loads(str(Cod.toJson(sn[0])))

    d, vd = setup("snap")
    sn = vd.snap()                                      # the saver's snapshot BEFORE the take ...
    r = LL.take(UID, PK1, "uidA")                      # ... the take runs before the saver serialises it
    j = snap_doc(sn)
    check(doc_count(j) == 1 and not any("llt" in o for o in j.get("orphans", [])),
          "C12. a snapshot from before the take serialised after it: the tool once, in its slot (was slot + pending: two)")
    sn2 = vd.snap()
    place_inv(r[1])
    LL.done(UID, str(r[0]))
    j2 = snap_doc(sn2)
    check(doc_count(j2) == 1 and [("lld" in o) for o in j2.get("orphans", [])] == [False],
          "C12. a snapshot from before doneLL keeps the record as it was (no placed mark)")
    sn3 = vd.snap()
    settle()
    check(doc_count(snap_doc(sn3)) == 1, "C12. a snapshot from before the hold ended still holds the note")
    d, vd = setup("snap-back")
    r = LL.take(UID, PK1, "uidA")
    sn4 = vd.snap()
    LL.back(UID, str(r[0]), "test")
    j4 = snap_doc(sn4)
    check(doc_count(j4) == 1 and [("llt" in o) for o in j4.get("orphans", [])] == [True],
          "C12. a snapshot from before a putBack: the pending record only (was: neither copy)")
    d, vd = setup("snap-full", full=True)
    vd.page(2)[5] = tool("uidA", PK1)
    vd.rev = vd.rev + 1
    LL.persist(vd)
    r = LL.take(UID, PK1, "uidA")
    vd.page(2)[5] = ISC("Test_Late", 1)
    sn5 = vd.snap()
    LL.back(UID, str(r[0]), "test")                   # full vault: the record becomes a plain orphan (keys removed in place)
    j5 = snap_doc(sn5)
    check(doc_count(j5) == 1 and [("llt" in o) for o in j5.get("orphans", [])] == [True],
          "C12. a snapshot from before a full-vault putBack keeps its llt (the copy is deep)")
    # the saver thread against takes + put-backs: every snapshot it serialises holds the tool exactly once, no exception
    import threading
    d, vd = setup("snap-race")
    stop, seen, bad, jl = [False], [0], [], []

    def saver():
        while not stop[0]:
            try:
                snx = vd.snap()
                n = doc_count(json.loads(str(Cod.toJson(snx[0]))))
                seen[0] += 1
                if n != 1:
                    bad.append("copies %d at rev %s" % (n, snx[1]))
                Store.writeDoc(vd, snx[0], int(snx[1]))   # an older revision than the file is skipped by design
            except Exception as e:
                bad.append("exception %s" % e)
    th = threading.Thread(target=saver)
    th.start()
    cycles = 0
    for i in range(150):
        r = LL.take(UID, PK1, "uidA")
        if isinstance(r, str):
            jl.append(str(r))
            continue
        LL.back(UID, str(r[0]), "race")
        cycles += 1
    stop[0] = True
    th.join()
    check(not bad and seen[0] > 20 and cycles >= 140 and count_uid(d) == 1 and file_where(d) == [("slot", 2, 5)],
          "C12. the saver thread serialised %d snapshots during %d take / putBack cycles: %s; refusals %s; file %s"
          % (seen[0], cycles, bad[:5], jl[:3], file_where(d)))
    print("C12. snapshots are deep copies: take / doneLL / hold end / putBack / full-vault putBack after a snapshot never change it; "
          "saver-thread race: %d snapshots, %d cycles, %d bad" % (seen[0], cycles, len(bad)))


# ------------------------------------------------------------------------------------------------ D. start twice on the live data
def live_section(E):
    from jpype import JClass, JShort
    U, jc, UUID, Paths = E["U"], E["jc"], E["UUID"], E["Paths"]
    PR = E["PRc"]
    if not LIVE or not os.path.isdir(LIVE):
        print("D. skipped: no live Skyy_SkyyVault folder (%s)" % LIVE)
        return
    src_files = {}
    for root, _d, files in os.walk(LIVE):
        for f in files:
            p = os.path.join(root, f)
            src_files[os.path.relpath(p, LIVE)] = open(p, "rb").read()
    check(any(n.startswith("vaults") for n in src_files), "D. the live folder holds vault files: %s" % sorted(src_files))
    E["BR"].clear()
    RESULT = {}
    for k in ("old", "new"):
        Cfg, Store, VS, Btn = jc(k, "VCfg"), jc(k, "VStore"), jc(k, "VSessions"), jc(k, "VBtn")
        dst = os.path.join(WORK, "live", k)
        shutil.copytree(LIVE, dst)
        runs = []
        for run_i in (1, 2):
            Cfg.DIR = Paths.get(dst)
            Cfg.VDIR = Paths.get(dst).resolve("vaults")
            Cfg.FILE = Paths.get(dst).resolve("config.properties")
            Cfg.LOGF = Paths.get(dst).resolve("vault.log")
            Cfg.NAMESF = Paths.get(dst).resolve("names.properties")
            Cfg.WARNED.clear()
            for m in ("CACHE", "PENDING", "BUYING", "LASTBUY", "NAMES"):
                getattr(Store, m).clear()
            Store.SAVER = None
            Store.STOPPING = False
            for m in ("SESSIONS", "LAST", "EPOCHS", "SWITCHED", "BUSYSEEN", "ONLINE"):
                getattr(VS, m).clear()
            if k == "new":
                LL = jc(k, "VLL")
                for m in ("PEND", "QUEUED", "SEEN"):
                    getattr(LL, m).clear()
            before = dict((n, open(os.path.join(dst, n), "rb").read()) for n in sorted(src_files))
            summary = str(Cfg.load())
            Store.loadNames()
            recs = {}
            for n in sorted(os.listdir(os.path.join(dst, "vaults"))):
                if not n.endswith(".json"):
                    continue
                u = UUID.fromString(n[:-5])
                d = Store.load(u)
                if not check(d is not None, "D. %s run %d: vault %s reads" % (k, run_i, n)):
                    continue
                slots = []
                for pg in range(1, int(d.unlocked) + 1):
                    for i, x in enumerate(d.pageCopy(pg)):
                        if x is not None and not x.isEmpty():
                            md = x.getMetadata()
                            slots.append((pg, i, str(x.getItemId()), int(x.getQuantity()), float(x.getDurability()),
                                          float(x.getMaxDurability()), None if md is None else str(md.toJson())))
                recs[n] = (int(d.unlocked), int(d.cap), slots, str(d.orphans))
                if k == "new":
                    check(int(LL.scanPend(d)) == 0 and LL.find(u, str(u), "no-such-uid") is None,
                          "D. new run %d: %s has no pending take and no tool of a made-up uid" % (run_i, n))
                pr = U.allocateInstance(PR.class_)
                E["jf"](PR.class_, "uuid").set(pr, u)
                E["jf"](PR.class_, "username").set(pr, "LiveCopy")
                s = VS.newSession(pr, u, d, 1, 2)
                if check(s is not None, "D. %s run %d: a session opens on the live vault" % (k, run_i)):
                    VS.SESSIONS.put(u, s)
                    VS.retire(s)
            after_look = dict((n, open(os.path.join(dst, n), "rb").read()) for n in sorted(src_files))
            check(after_look == before, "D. %s run %d: a start + an open / close with no change writes nothing: %s" % (
                k, run_i, [n for n in before if before[n] != after_look.get(n)]))
            for n in recs:
                d = Store.CACHE.get(UUID.fromString(n[:-5]))
                d.rev = d.rev + 1
            Store.flushAll()
            written = {}
            for n in recs:
                doc = json.loads(open(os.path.join(dst, "vaults", n), encoding="utf8").read())
                for x in ("savedAt", "rev"):
                    doc.pop(x, None)
                written[n] = doc
            runs.append(dict(summary=summary, recs=recs, written=written,
                             cfg=open(os.path.join(dst, "config.properties"), "rb").read(),
                             names=open(os.path.join(dst, "names.properties"), "rb").read() if os.path.exists(os.path.join(dst, "names.properties")) else None))
        if len(runs) == 2:
            check(runs[0]["recs"] == runs[1]["recs"], "D. %s: the second start reads exactly what the first one saw" % k)
            check(runs[0]["written"] == runs[1]["written"], "D. %s: the second start's save is the same file (savedAt / rev aside)" % k)
            check(runs[0]["summary"] == runs[1]["summary"], "D. %s: the same config both starts" % k)
            check(runs[1]["cfg"] == src_files.get("config.properties") and runs[1]["names"] == src_files.get("names.properties"),
                  "D. %s: config.properties + names.properties untouched" % k)
            for n, doc in runs[0]["written"].items():
                live_doc = json.loads(src_files[os.path.join("vaults", n)].decode("utf8"))
                n_live = sum(len(p.get("slots", [])) for p in live_doc.get("content", [])) + len(live_doc.get("orphans", []))
                n_read = len(runs[0]["recs"][n][2])
                check(n_live == n_read and doc.get("version") == (VERSION if k == "new" else OLD_VERSION),
                      "D. %s: %s - %d stacks in the live file, %d read and written back (version %s)" % (k, n, n_live, n_read, doc.get("version")))
                tally("D stacks " + k, n_read)
        RESULT[k] = runs
    if len(RESULT) == 2 and len(RESULT["old"]) == 2 and len(RESULT["new"]) == 2:
        check(RESULT["old"][0]["recs"] == RESULT["new"][0]["recs"], "D. 0.1.5 and 0.1.6 read the live vaults the same")
        strip = lambda w: dict((n, dict((x, y) for x, y in d.items() if x != "version")) for n, d in w.items())
        check(strip(RESULT["old"][0]["written"]) == strip(RESULT["new"][0]["written"]), "D. 0.1.5 and 0.1.6 write the same file (version aside)")
    print("D. start twice on a copy of %s (%d files): %d / %d stacks read, an open / close writes nothing, the second start = the first, "
          "0.1.5 = 0.1.6" % (LIVE, len(src_files), COUNT.get("D stacks old", 0), COUNT.get("D stacks new", 0)))


def main():
    global WORK
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    if not scratch_ok(SCRATCH):
        print("refused: --dir %s is not under %s" % (SCRATCH, SCRATCH_ROOT))
        return 2
    os.makedirs(SCRATCH, exist_ok=True)
    WORK = tempfile.mkdtemp(prefix="run-", dir=SCRATCH)
    tmp = os.path.join(WORK, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    print("SkyyVault %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAIL", f[:600])
    return 1 if FAILS else 0


if __name__ == "__main__":
    made_scratch = not os.path.exists(SCRATCH)
    code = main()
    if WORK is not None:
        if KEEP:
            print("kept", WORK)
        else:
            shutil.rmtree(WORK, ignore_errors=True)
            if made_scratch and os.path.isdir(SCRATCH) and not os.listdir(SCRATCH):
                os.rmdir(SCRATCH)
    sys.stdout.flush()
    os._exit(code)
