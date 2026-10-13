"""perfworld_kit - shared checks for the perfworld lag-fix round harnesses (SkyySkills 0.4.32, SkyyFishing 0.1.3, SkyyMerchants 0.1.3,
SkyyExploration 0.2.7, SkyyIslands 0.5.7; research/Code-Structure-Audit.md findings 2, 3, 11, 12, 18 + pack-wide pattern 1).
Used inside a harness_kit child JVM that has javassist on its classpath (HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar])).

  bridge_static(K, jar)   every static bridge()Ljava/util/Map; in the jar is the lock-free kit form: its FIRST instruction reads the
                          static volatile BRIDGE field (no synchronized(System.class) on the fast path), and a bridge0() sits next to it
  calls(jar)              {"Class.method": set("Owner.method" called)} for every method of the jar (javassist bytecode walk)
  sites(graph, targets)   the jar methods that call one of the targets directly ("java.lang.Thread.sleep", "java.nio.file.Files.move")
  callers(graph, m)       the jar methods that call jar method m ("Class.method")
  reach(graph, entry)     every jar method reachable from entry (by name), entry included
  wait_until(fn, s)       poll fn() up to s seconds
"""
import time

IO_TARGETS = ("java.nio.file.Files.write", "java.nio.file.Files.move", "java.nio.file.Files.newOutputStream",
              "java.nio.file.Files.readAllLines", "java.nio.file.Files.readAllBytes", "java.nio.file.Files.newInputStream",
              "java.nio.file.Files.newBufferedReader", "java.nio.file.Files.newBufferedWriter", "java.nio.file.Files.copy",
              "java.nio.file.Files.readString", "java.nio.file.Files.writeString", "java.nio.file.Files.list",
              "java.io.FileOutputStream.<init>", "java.io.FileInputStream.<init>", "java.io.RandomAccessFile.<init>")
SLEEP = ("java.lang.Thread.sleep",)


def wait_until(fn, secs=10.0):
    end = time.time() + secs
    while time.time() < end:
        try:
            if fn():
                return True
        except Exception:
            pass
        time.sleep(0.01)
    try:
        return bool(fn())
    except Exception:
        return False


def _pool(jar):
    from jpype import JClass
    import skyybuild as B
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    return cp


def _classes(jar):
    import zipfile
    return sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class"))


def calls(jar):
    from jpype import JClass
    cp = _pool(jar)
    CPool = JClass("javassist.bytecode.ConstPool")
    out = {}
    for cn in _classes(jar):
        cc = cp.get(cn)
        short = cn.rsplit(".", 1)[-1]
        for mi in cc.getClassFile2().getMethods():
            key = "%s.%s" % (short, mi.getName())
            s = out.setdefault(key, set())
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cpl, it = mi.getConstPool(), ca.iterator()
            while it.hasNext():
                p = it.next()
                op = it.byteAt(p)
                if op not in (0xb6, 0xb7, 0xb8, 0xb9):
                    continue
                idx = it.u16bitAt(p + 1)
                if cpl.getTag(idx) == CPool.CONST_InterfaceMethodref:
                    c_, n_ = str(cpl.getInterfaceMethodrefClassName(idx)), str(cpl.getInterfaceMethodrefName(idx))
                else:
                    c_, n_ = str(cpl.getMethodrefClassName(idx)), str(cpl.getMethodrefName(idx))
                s.add("%s.%s" % (c_, n_))
    return out


def _short(owner_method, pkg):
    if owner_method.startswith(pkg):
        return owner_method[len(pkg):]
    return None


def sites(graph, targets):
    return sorted(m for m, cs in graph.items() if any(c in targets for c in cs))


def callers(graph, m, pkg):
    return sorted(k for k, cs in graph.items() if any(_short(c, pkg) == m for c in cs))


def reach(graph, entry, pkg):
    seen, todo = set(), [entry]
    while todo:
        m = todo.pop()
        if m in seen or m not in graph:
            continue
        seen.add(m)
        for c in graph[m]:
            s = _short(c, pkg)
            if s is not None and s not in seen:
                todo.append(s)
    return seen


def bridge_static(K, jar):
    """every static bridge()Map of the jar: first instruction = getstatic <same class>.BRIDGE; a bridge0()Map beside it"""
    from jpype import JClass
    cp = _pool(jar)
    found = []
    for cn in _classes(jar):
        cc = cp.get(cn)
        for mi in cc.getClassFile2().getMethods():
            if str(mi.getName()) != "bridge" or str(mi.getDescriptor()) != "()Ljava/util/Map;":
                continue
            ca = mi.getCodeAttribute()
            it = ca.iterator()
            p = it.next()
            op = it.byteAt(p)
            fld = str(mi.getConstPool().getFieldrefName(it.u16bitAt(p + 1))) if op == 0xb2 else None
            has0 = any(str(m.getName()) == "bridge0" for m in cc.getClassFile2().getMethods())
            found.append(cn.rsplit(".", 1)[-1])
            K.check(op == 0xb2 and fld == "BRIDGE" and has0,
                    "BRIDGE %s.bridge() is the lock-free kit form (first instruction getstatic BRIDGE, bridge0 present): op %s field %s bridge0 %s"
                    % (cn, hex(op), fld, has0))
    K.check(len(found) >= 1, "BRIDGE at least one bridge() checked: %s" % found)
    K.notes.append("BRIDGE lock-free bridge() in %s" % found)
    return found
