"""SkyWynn cross-check: every SET jar together in ONE JVM against HytaleServer.jar (read-only). Replaces the hand-written cross-check.

Usage (game may stay open - nothing is written outside a self-deleting scratch folder):
    python tools/ci/crosscheck.py                                    # the SET jars from tools/deploy_set.py
    python tools/ci/crosscheck.py --jar SkyyCooking/SkyyCooking-0.1.5.jar --jar SkyyMenu/SkyyMenu-0.3.7.jar
                                                                     # candidate jars replace their mod's SET entry (a new mod is added)
    python tools/ci/crosscheck.py --jar ... --baseline               # + command / permission tree diff vs the plain SET jar of each override
    options: --tree (print every command node), --no-init (skip static initialisers), --keep (keep the scratch folder),
             --server <HytaleServer.jar> (default: the installed release jar, see tools/skyybuild.py)

Checks (exit 0 = READY, 1 = problems listed under FAIL; WARN lines never fail):
  1. VERIFY   the JVM runs with -Xverify:all. Every class of every jar is loaded (one class loader per jar, parent = the server jar's
              loader, like separate plugins) and linked (getDeclared* forces linking = bytecode verification), then initialised
              (static initialisers run; cwd / TEMP / TMP / java.io.tmpdir point into the scratch folder, so a stray relative write lands
              there). A VerifyError / NoClassDefFoundError / LinkageError / initialiser exception is a FAIL.
  2. ACCESS   every class / field / method reference in every class's constant pool is resolved the way the JVM resolves it (fields:
              class, superinterfaces, superclasses; methods: class + superclasses, then interfaces; exact descriptor) against the engine
              and the jar itself, and checked for access (public / protected from a subclass / package-private in the same runtime
              package / private in the same class). A reference that does not resolve or is not accessible is "refused" = FAIL. A
              reference into ANOTHER Skyy jar is refused too (cross-mod calls go only through the skyy.bridge map).
  3. COMMANDS every command a jar registers (registerCommand(new X(...)) found in the bytecode) is constructed in the JVM (null / 0 /
              false constructor arguments) and its tree (addSubCommand + addUsageVariant) is read from the engine's AbstractCommand
              fields. Adventurer permission audit (HANDOFF section 3 COMMAND RULES + lint perm_group_leaks, engine putRecursive-
              PermissionGroups semantics):
                FAIL  requirePermission + setPermissionGroups(non-empty) on the same command (the node goes to every group member)
                FAIL  a sub-command with requirePermission, no groups of its own, under a parent that sets groups (inherits = leak)
                FAIL  the engine's own getPermissionGroupsRecursive() puts an explicit permission node into hytale:Adventurer
                FAIL  a usage variant of a player command without hytale:Adventurer (players cannot use that form)
                FAIL  a command name / alias registered by two jars
                WARN  a sub-command of a player command with no groups and an auto node (works through the engine's one-level
                      inheritance, but the rule wants setPermissionGroups on every player node), or an admin sub-command whose
                      empty groups are not explicit, or a command class that could not be constructed
  --baseline  for every --jar override, the same tree of the plain SET jar is built in the same JVM (own loader) and the node lines
              are diffed ("identical" or +/- lines). Auto permission nodes contain the version, so the tree shows them as "auto".

Limitations: commands are constructed with null arguments (a constructor that needs a live plugin object is reported as a WARN and
its tree is skipped); commands added outside a constructor (e.g. parent.addSubCommand(...) in setup()) and commands registered from a
local variable are not seen; invokedynamic is not audited (javassist never emits it); protected instance access is checked by
subclassing only (not the receiver-type rule). Runtime: about 5 s for the 26-jar SET (1,161 classes).
"""
import os, sys, re, time, shutil, zipfile, argparse

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import skyybuild as B      # noqa: E402  (JVM path, javassist, server jar path)

ADV = "hytale:Adventurer"
ACMD = "com.hypixel.hytale.server.core.command.system.AbstractCommand"


def set_jars():
    import deploy_set
    return [(m, v, os.path.join(ROOT, m, "%s-%s.jar" % (m, v))) for m, v in deploy_set.SET]


def mod_of(path):
    m = re.match(r"^(Skyy\w+?)-(\d+(?:\.\d+)*)\.jar$", os.path.basename(path))
    if not m:
        raise SystemExit("cannot read <Mod>-<version>.jar from %s" % path)
    return m.group(1), m.group(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", action="append", default=[])
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--tree", action="store_true")
    ap.add_argument("--no-init", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--server", default=B.SERVER_JAR)
    a = ap.parse_args()
    t0 = time.time()

    base = set_jars()
    jars = list(base)
    overrides = {}
    for p in a.jar:
        p = os.path.abspath(p if os.path.exists(p) else os.path.join(ROOT, p))
        if not os.path.isfile(p):
            raise SystemExit("no such jar: " + p)
        mod, ver = mod_of(p)
        overrides[mod] = (mod, ver, p)
    over_mods = set(overrides)
    jars = [overrides.pop(m) if m in overrides else (m, v, j) for m, v, j in jars] + list(overrides.values())
    missing = [j for _m, _v, j in jars if not os.path.isfile(j)]
    if missing:
        print("FAIL missing jar(s):\n  " + "\n  ".join(missing))
        return 1

    scratch = os.path.join(TOOLS, "dev", "scratch", "crosscheck-%d" % os.getpid())
    os.makedirs(scratch, exist_ok=True)
    for k in ("TEMP", "TMP", "TMPDIR"):
        os.environ[k] = scratch
    cwd0 = os.getcwd()
    os.chdir(scratch)
    code = 1
    try:
        code = run(a, jars, base, over_mods, scratch, t0)
    finally:
        os.chdir(cwd0)
        if not a.keep:
            shutil.rmtree(scratch, ignore_errors=True)
            if os.path.exists(scratch):
                print("note: scratch folder still holds files the JVM keeps open: %s (delete it after this run)" % scratch)
        else:
            print("scratch kept:", scratch)
    sys.stdout.flush()
    os._exit(code)      # static initialisers may have started non-daemon threads; never wait for them


def run(a, jars, base, over_mods, scratch, t0):
    import jpype
    import jpype.imports  # noqa: F401
    jpype.startJVM(B._jvm(), "-Xverify:all", "-XX:-UsePerfData", "-Djava.io.tmpdir=" + scratch, "-Xshare:off",
                   "--add-opens=java.base/java.lang=ALL-UNNAMED", "--enable-native-access=ALL-UNNAMED",
                   classpath=[a.server, B.JAVASSIST], convertStrings=True)   # server on the system class path: its LogManager
                                                                                   # (java.util.logging.manager) loads from there
    J = jpype.JClass
    Class = J("java.lang.Class"); Mod = J("java.lang.reflect.Modifier")
    URL = J("java.net.URL"); File = J("java.io.File"); ULC = J("java.net.URLClassLoader")
    CL = J("java.lang.ClassLoader")
    ClassFile = J("javassist.bytecode.ClassFile"); ConstPool = J("javassist.bytecode.ConstPool")
    DIS = J("java.io.DataInputStream"); BAIS = J("java.io.ByteArrayInputStream")
    Opcode = J("javassist.bytecode.Opcode")
    Throwable = J("java.lang.Throwable")

    def loader(paths, parent):
        arr = jpype.JArray(URL)([File(p).toURI().toURL() for p in paths])
        return ULC(arr, parent)

    srv = CL.getSystemClassLoader()
    if "-Xverify:all" not in [str(x) for x in J("java.lang.management.ManagementFactory").getRuntimeMXBean().getInputArguments()]:
        print("FAIL the JVM did not take -Xverify:all"); return 1
    fails, warns = [], []

    def jerr(e):
        s = str(e.getClass().getName()) + ": " + str(e.getMessage()) if isinstance(e, Throwable) else repr(e)
        c = e.getCause() if isinstance(e, Throwable) else None
        if c is not None:
            s += " <- " + str(c.getClass().getName()) + ": " + str(c.getMessage())
        return s

    # ---------------- load all jars ----------------
    ent = []        # (mod, ver, path, loader, [class names], {name: bytes})
    owner_jar = {}  # class name -> mod (for cross-jar refs)
    for mod, ver, path in jars:
        with zipfile.ZipFile(path) as z:
            data = {n[:-6].replace("/", "."): z.read(n) for n in z.namelist() if n.endswith(".class")}
        for n in data:
            if n in owner_jar:
                fails.append("duplicate class %s in %s and %s" % (n, owner_jar[n], mod))
            owner_jar[n] = mod
        ent.append((mod, ver, path, loader([path], srv), sorted(data), data))

    # 1. VERIFY + INIT
    nclasses = 0
    classes = {}    # (mod, name) -> Class
    for mod, ver, path, ld, names, data in ent:
        for n in names:
            try:
                c = Class.forName(n, False, ld)
                c.getDeclaredMethods(); c.getDeclaredFields(); c.getDeclaredConstructors()   # forces linking = verification
                classes[(mod, n)] = c
                nclasses += 1
            except Exception as e:
                fails.append("VERIFY %s %s: %s" % (mod, n, jerr(e)))
    ninit = 0
    if not a.no_init:
        for (mod, n), c in list(classes.items()):
            try:
                Class.forName(n, True, c.getClassLoader()); ninit += 1
            except Exception as e:
                fails.append("INIT %s %s: %s" % (mod, n, jerr(e)))
    print("verify: %d jars, %d classes loaded + verified (-Xverify:all), %d initialised  [%.0fs]"
          % (len(ent), nclasses, ninit, time.time() - t0))

    # 2. ACCESS audit
    PRIM = {"boolean": "Z", "byte": "B", "char": "C", "short": "S", "int": "I", "long": "J", "float": "F", "double": "D", "void": "V"}

    def desc(c):
        n = str(c.getName())
        if n in PRIM:
            return PRIM[n]
        if n.startswith("["):
            return n.replace(".", "/")
        return "L" + n.replace(".", "/") + ";"

    memb = {}   # Class -> (fields {(name,desc): mods}, methods {(name,desc): mods})

    def members(c):
        k = c
        if k not in memb:
            fs = {}; ms = {}
            for f in c.getDeclaredFields():
                fs[(str(f.getName()), desc(f.getType()))] = int(f.getModifiers())
            for m in c.getDeclaredMethods():
                ms[(str(m.getName()), "(" + "".join(desc(p) for p in m.getParameterTypes()) + ")" + desc(m.getReturnType()))] = int(m.getModifiers())
            for m in c.getDeclaredConstructors():
                ms[("<init>", "(" + "".join(desc(p) for p in m.getParameterTypes()) + ")V")] = int(m.getModifiers())
            memb[k] = (fs, ms)
        return memb[k]

    def find_field(c, key):
        while c is not None:
            fs, _ = members(c)
            if key in fs:
                return c, fs[key]
            for i in c.getInterfaces():
                r = find_field(i, key)
                if r:
                    return r
            c = c.getSuperclass()
        return None

    def find_method(c, key):
        k = c
        while k is not None:
            _, ms = members(k)
            if key in ms:
                return k, ms[key]
            if key[0] == "<init>":
                return None
            k = k.getSuperclass()
        stack = list(c.getInterfaces())
        seen = set()
        while stack:
            i = stack.pop(0)
            if str(i.getName()) in seen:
                continue
            seen.add(str(i.getName()))
            _, ms = members(i)
            if key in ms:
                return i, ms[key]
            stack.extend(i.getInterfaces())
        if c.isInterface():
            obj = Class.forName("java.lang.Object")
            _, ms = members(obj)
            if key in ms and Mod.isPublic(ms[key]):
                return obj, ms[key]
        return None

    def pkg(c):
        n = str(c.getName()); return n.rsplit(".", 1)[0] if "." in n else ""

    def same_pkg(x, y):
        return pkg(x) == pkg(y) and x.getClassLoader() == y.getClassLoader()

    def accessible(r, d, mods):
        if Mod.isPublic(mods):
            return True
        if Mod.isPrivate(mods):
            return r == d
        if same_pkg(r, d):
            return True
        return Mod.isProtected(mods) and d.isAssignableFrom(r)

    cls_cache = {}

    def resolve_class(ld, name):
        if name.startswith("["):
            name = name.lstrip("[")
            if not name.startswith("L"):
                return "prim"
            name = name[1:-1]
        name = name.replace("/", ".")
        k = (ld, name)
        if k not in cls_cache:
            try:
                cls_cache[k] = Class.forName(name, False, ld)
            except Exception as e:
                cls_cache[k] = None
        return cls_cache[k]

    nrefs = 0; refused = []
    TAG_CLASS, TAG_F, TAG_M, TAG_IM = 7, 9, 10, 11
    done = {}
    for mod, ver, path, ld, names, data in ent:
        for n in names:
            r = classes.get((mod, n))
            if r is None:
                continue
            cf = ClassFile(DIS(BAIS(data[n])))
            cp = cf.getConstPool()
            for i in range(1, cp.getSize()):
                t = cp.getTag(i)
                if t not in (TAG_CLASS, TAG_F, TAG_M, TAG_IM):
                    continue
                nrefs += 1
                if t == TAG_CLASS:
                    owner = str(cp.getClassInfo(i)); key = None
                elif t == TAG_F:
                    owner = str(cp.getFieldrefClassName(i)); key = (str(cp.getFieldrefName(i)), str(cp.getFieldrefType(i)))
                elif t == TAG_M:
                    owner = str(cp.getMethodrefClassName(i)); key = (str(cp.getMethodrefName(i)), str(cp.getMethodrefType(i)))
                else:
                    owner = str(cp.getInterfaceMethodrefClassName(i))
                    key = (str(cp.getInterfaceMethodrefName(i)), str(cp.getInterfaceMethodrefType(i)))
                dk = (n, owner, t, key)
                if dk in done:
                    continue
                done[dk] = 1
                why = None
                c = resolve_class(ld, owner)
                if c == "prim":
                    continue
                what = owner + ("" if key is None else "." + key[0] + key[1])
                if c is None:
                    other = owner_jar.get(owner.replace("/", ".").lstrip("[L").rstrip(";"))
                    why = "class not found" + (" (it is in %s - cross-mod calls only through skyy.bridge)" % other if other else "")
                elif not (Mod.isPublic(c.getModifiers()) or same_pkg(r, c)):
                    why = "class not accessible"
                elif t == TAG_F:
                    hit = find_field(c, key)
                    why = "no such field" if not hit else None if accessible(r, hit[0], hit[1]) else "field not accessible"
                elif t in (TAG_M, TAG_IM):
                    if t == TAG_M and c.isInterface():
                        why = "Methodref to an interface"
                    elif t == TAG_IM and not c.isInterface():
                        why = "InterfaceMethodref to a class"
                    else:
                        try:
                            hit = find_method(c, key)
                        except Exception as e:
                            hit = None; why = "cannot reflect: " + jerr(e)
                        if why is None:
                            why = "no such method" if not hit else None if accessible(r, hit[0], hit[1]) else "method not accessible"
                if why:
                    refused.append("ACCESS %s %s -> %s: %s" % (mod, n, what, why))
    fails.extend(refused)
    print("access: %d refs checked (class / field / method constant-pool entries of every class), %d refused  [%.0fs]"
          % (nrefs, len(refused), time.time() - t0))

    # 3. COMMANDS
    try:
        AC = Class.forName(ACMD, False, srv)
    except Exception as e:
        fails.append("COMMANDS cannot load %s: %s" % (ACMD, jerr(e)))
        AC = None

    def fld(n):
        f = AC.getDeclaredField(n); f.setAccessible(True); return f

    INV = (Opcode.INVOKEVIRTUAL, Opcode.INVOKEINTERFACE, Opcode.INVOKESPECIAL, Opcode.INVOKESTATIC)

    def registered(data):
        """class names passed to registerCommand(new X(...)) anywhere in the jar's bytecode."""
        out = []
        for n, b in data.items():
            if b.find(b"registerCommand") < 0:
                continue
            cf = ClassFile(DIS(BAIS(b))); cp = cf.getConstPool()
            for m in cf.getMethods():
                ca = m.getCodeAttribute()
                if ca is None:
                    continue
                it = ca.iterator(); news = []; last = None
                while it.hasNext():
                    p = it.next(); op = it.byteAt(p)
                    if op == Opcode.NEW:
                        news.append(str(cp.getClassInfo(it.u16bitAt(p + 1))))
                    elif op in INV:
                        idx = it.u16bitAt(p + 1)
                        if op == Opcode.INVOKEINTERFACE:
                            mn = str(cp.getInterfaceMethodrefName(idx)); mc = str(cp.getInterfaceMethodrefClassName(idx))
                        else:
                            mn = str(cp.getMethodrefName(idx)); mc = str(cp.getMethodrefClassName(idx))
                        if op == Opcode.INVOKESPECIAL and mn == "<init>" and news and news[-1] == mc:
                            last = news.pop()
                        elif mn == "registerCommand":
                            out.append(last)
        return out

    def default_args(ctor):
        Integer = J("java.lang.Integer"); Long = J("java.lang.Long"); Boolean = J("java.lang.Boolean")
        Float = J("java.lang.Float"); Double = J("java.lang.Double"); Short = J("java.lang.Short")
        Byte = J("java.lang.Byte"); Char = J("java.lang.Character")
        vals = []
        for p in ctor.getParameterTypes():
            n = str(p.getName())
            vals.append({"int": Integer.valueOf(0), "long": Long.valueOf(0), "boolean": Boolean.FALSE, "float": Float.valueOf(0.0),
                         "double": Double.valueOf(0.0), "short": Short.valueOf(0), "byte": Byte.valueOf(0),
                         "char": Char.valueOf("\0")}.get(n))
        return jpype.JArray(J("java.lang.Object"))(vals)

    def build(mod, ld, data):
        """-> (tops [(cmd, class name)], problems)"""
        tops = []; probs = []
        regs = registered(data)
        if any(x is None for x in regs):
            probs.append("WARN COMMANDS %s: a registerCommand argument is not a direct `new X(...)` - that command is not audited" % mod)
        for cn in [x for x in regs if x]:
            try:
                c = Class.forName(cn, True, ld)
                ctors = sorted(c.getDeclaredConstructors(), key=lambda k: len(k.getParameterTypes()))
                obj = None; last = None
                for k in ctors:
                    try:
                        k.setAccessible(True); obj = k.newInstance(default_args(k)); break
                    except Exception as e:
                        last = e
                if obj is None:
                    probs.append("WARN COMMANDS %s: cannot construct %s with null arguments (%s) - tree not audited" % (mod, cn, jerr(last)))
                else:
                    tops.append((obj, cn))
            except Exception as e:
                probs.append("WARN COMMANDS %s: cannot load %s (%s)" % (mod, cn, jerr(e)))
        return tops, probs

    def walk(mod, tops):
        """-> list of node dicts"""
        fSub, fVar, fGroups, fPerm, fOpen, fName = (fld("subCommands"), fld("variantCommands"), fld("permissionGroups"),
                                                  fld("permission"), fld("openToEveryone"), fld("name"))
        nodes = []

        def info(cmd):
            g = fGroups.get(cmd)
            groups = None if g is None else [str(x) for x in g]
            p = fPerm.get(cmd)
            perm = str(p.getId()) if p is not None else ("open" if bool(fOpen.get(cmd)) else "auto")
            return groups, perm

        def rec(cmd, path, kind, parent, top_player, cls):
            groups, perm = info(cmd)
            if parent is None:
                top_player = bool(groups) and ADV in groups
            nd = {"mod": mod, "path": path, "kind": kind, "groups": groups, "perm": perm, "parent": parent, "player": top_player,
                  "cls": cls}
            nodes.append(nd)
            subs = fSub.get(cmd)
            for k in sorted([str(x) for x in subs.keySet()]):
                s = subs.get(k)
                rec(s, path + " " + str(fName.get(s) or k), "sub", nd, top_player, str(s.getClass().getName()))
            vs = fVar.get(cmd)
            if vs is not None:
                for k in sorted([int(x) for x in vs.keySet()]):
                    v = vs.get(jpype.JInt(k))
                    rec(v, path + " <%d args>" % k, "variant", nd, top_player, str(v.getClass().getName()))

        for cmd, cn in tops:
            rec(cmd, "/" + str(cmd.getName()), "top", None, False, cn)
        return nodes

    def line(nd):
        g = "-" if nd["groups"] is None else "[" + ",".join(nd["groups"]) + "]"
        return "%-34s %-7s groups=%-20s perm=%s" % (nd["path"], nd["kind"], g, nd["perm"])

    def audit(nodes, tops):
        out = []
        for nd in nodes:
            g, p, par = nd["groups"], nd["perm"], nd["parent"]
            explicit = p not in ("auto", "open")
            where = "%s %s (%s)" % (nd["mod"], nd["path"], nd["cls"].rsplit(".", 1)[-1])
            if explicit and g:
                out.append("FAIL PERM %s: requirePermission(%s) AND setPermissionGroups(%s) - every group member holds the node"
                           % (where, p, ",".join(g)))
            elif explicit and g is None and nd["kind"] == "sub" and par["groups"]:
                out.append("FAIL PERM %s: requirePermission(%s) without setPermissionGroups(new String[0]) under a parent with groups %s"
                           " - inherits them = leak" % (where, p, par["groups"]))
            elif explicit and g is None and nd["kind"] != "top" and nd["player"]:
                out.append("WARN PERM %s: admin node %s under a player command without an explicit setPermissionGroups(new String[0])"
                           % (where, p))
            elif nd["player"] and not explicit and p != "open" and not (g and ADV in g):
                if g == []:
                    pass    # admin-only by auto node, groups cleared on purpose
                elif nd["kind"] == "variant":
                    out.append("FAIL PERM %s: usage variant of a player command without %s - players cannot use this form" % (where, ADV))
                elif g is None and par["groups"] and ADV in par["groups"]:
                    out.append("WARN PERM %s: no setPermissionGroups - works only through the engine's one-level inheritance" % where)
                else:
                    out.append("FAIL PERM %s: player command node without %s (groups %s)" % (where, ADV, g))
        try:
            for cmd, cn in tops:
                m = cmd.getPermissionGroupsRecursive()
                s = m.get(ADV)
                if s is not None and s.size() > 0:
                    out.append("FAIL PERM engine getPermissionGroupsRecursive(/%s) gives %s explicit node(s): %s"
                               % (cmd.getName(), ADV, ", ".join(sorted(str(x) for x in s))))
        except Exception as e:
            out.append("WARN PERM engine getPermissionGroupsRecursive failed: %s" % jerr(e))
        return out

    allnodes = []; trees = {}
    if AC is not None:
        names = {}
        fAl = fld("aliases")
        for mod, ver, path, ld, cls_names, data in ent:
            tops, probs = build(mod, ld, data)
            nodes = walk(mod, tops)
            trees[mod] = (ver, nodes)
            allnodes.extend(nodes)
            for p in probs + audit(nodes, tops):
                (fails if p.startswith("FAIL") else warns).append(p)
            for cmd, cn in tops:
                al = fAl.get(cmd)
                for nm in [str(cmd.getName())] + ([str(x) for x in al] if al is not None else []):
                    nm = nm.lower()
                    if nm in names and names[nm] != mod:
                        fails.append("FAIL COMMANDS /%s is registered by %s and %s" % (nm, names[nm], mod))
                    names[nm] = mod
        nplayer = sum(1 for n in allnodes if n["player"] and (n["groups"] and ADV in n["groups"]))
        nadmin = len(allnodes) - nplayer
        print("commands: %d top-level, %d nodes audited (%d player nodes with %s, %d admin / op-only)  [%.0fs]"
              % (sum(1 for n in allnodes if n["kind"] == "top"), len(allnodes), nplayer, ADV, nadmin, time.time() - t0))
        if a.tree:
            for n in allnodes:
                print("  %-16s %s" % (n["mod"], line(n)))

        if a.baseline:
            bmap = dict((m, (v, j)) for m, v, j in base)
            if not over_mods:
                print("baseline: no --jar override - the tree is the SET's own")
            for mod in sorted(over_mods):
                if mod not in bmap:
                    print("baseline %s: NEW mod (not in SET) - %d command nodes, all new" % (mod, len(trees[mod][1])))
                    continue
                bv, bj = bmap[mod]
                with zipfile.ZipFile(bj) as z:
                    bdata = {n[:-6].replace("/", "."): z.read(n) for n in z.namelist() if n.endswith(".class")}
                btops, bprobs = build(mod, loader([bj], srv), bdata)
                old = [line(n) for n in walk(mod, btops)]
                new = [line(n) for n in trees[mod][1]]
                if old == new:
                    print("baseline %s %s -> %s: command / permission tree identical (%d nodes)" % (mod, bv, trees[mod][0], len(new)))
                else:
                    print("baseline %s %s -> %s: tree differs" % (mod, bv, trees[mod][0]))
                    for x in old:
                        if x not in new:
                            print("  - " + x)
                    for x in new:
                        if x not in old:
                            print("  + " + x)

    fails = [f if f.startswith("FAIL") else "FAIL " + f for f in fails]
    for w in warns:
        print(w)
    for f in fails[:200]:
        print(f)
    if len(fails) > 200:
        print("... %d more FAIL lines" % (len(fails) - 200))
    print("jars: " + ", ".join("%s %s" % (m, v) for m, v, _j in jars))
    print("%s: %d fail(s), %d warning(s), %.0fs" % ("READY" if not fails else "NOT READY", len(fails), len(warns), time.time() - t0))
    return 0 if not fails else 1


if __name__ == "__main__":
    main()
