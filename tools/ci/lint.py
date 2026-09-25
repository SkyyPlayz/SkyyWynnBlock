"""SkyWynn repo lint - runs on every push (GitHub Actions, .github/workflows/lint.yml) and locally: python tools/ci/lint.py

It cannot build the mods (that needs the game's HytaleServer.jar, which is never committed). It checks the things that are cheap to
check and expensive to get wrong:
  FAIL  a Python file does not parse
  FAIL  a forbidden file is tracked: game files (HytaleServer.jar, Assets.zip), any .jar except tools/javassist.jar, any file > 5 MB
  FAIL  newest build script of a mod ships a .ui file (inline pages only - see HANDOFF section 2)
  FAIL  newest build script of a mod uses an underscore in a UI element id (#Some_Id) - the client cannot resolve those
  WARN  a command constructor in the newest build script has neither setPermissionGroups(...) nor requirePermission(...) - ordinary
        players cannot run it (HANDOFF "COMMAND RULES"); admin-only-by-design commands are listed in ADMIN_ONLY_OK
  FAIL  newest build script of a mod has a command whose requirePermission node the engine would put into a permission group (e.g.
        hytale:Adventurer = every player): a sub-command that calls requirePermission without setPermissionGroups(new String[0]) under
        a parent that sets groups, a requirePermission command that sets groups itself, or a requirePermission sub-command whose
        parent lint cannot find (details at perm_group_leaks below; SkyyIslands 0.5 /island reload handed every player skyyislands.admin)
Exit code 1 on any FAIL.
Files checked = tracked + untracked-but-not-ignored (what `git add -A` would commit), so a new, not yet committed build script counts.
Extra: python tools/ci/lint.py --perm <build script> ...   runs only the permission-group check on the given files (old / pinned ones).
"""
import os, re, sys, ast, builtins, subprocess, py_compile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_JARS = {"tools/javassist.jar"}
FORBIDDEN_NAMES = {"hytaleserver.jar", "assets.zip"}
# commands that are admin-only on purpose (auto permission node, only "*" admins have it)
ADMIN_ONLY_OK = {"SkyyRolls": {"rolls", "give", "read", "reroll", "clear"},
                 "SkyyClasses": {"set", "reset", "info", "reload"}}  # /classadmin subcommands (parent requires skyyclasses.admin)

fails, warns = [], []

# ---- permission groups (FAIL). Engine facts (HytaleServer.jar bytecode, 2026-09-25):
#   PermissionsModule.start() / reload()  -> refreshVirtualGroups() -> CommandManager.createVirtualPermissionGroups(), which for every
#   registered command merges AbstractCommand.getPermissionGroupsRecursive() -> putRecursivePermissionGroups(map):
#       groups = this.permissionGroups; if (groups == null && parentCommand != null) groups = parentCommand.permissionGroups;
#       if (groups != null && permission != null) for g in groups: map[g].add(permission.getId());
#       then the same for every subCommands value (addSubCommand) - NOT for variantCommands (addUsageVariant)
#   PermissionsModule.hasPermission(uuid, node) then grants the node to every member of such a "virtual group" (default group for
#   every player: hytale:Adventurer). So a requirePermission node lands in a group when the command lists that group itself, or when
#   it is a sub-command that sets no groups of its own and its DIRECT parent does (only one level: the parent's own list).
# The check reads constructors as the javassist compiler would get them: literal Java strings (CtNewConstructor.make('...'),
# C(cls, r"""..."""), f-strings, "..." + ADV + "..."), @TOKEN@ / {NAME} placeholders resolved from the script's module constants
# (T = {"ADV": 'setPermissionGroups(...)', ...}, ADV = '...'), and constructors built by generator helpers (SkyyVault cmd(),
# SkyyEssentials tcmd(), SkyyIslands sub(), ...: a module-level def containing a "public %s(" constructor template and a
# super("%s" call) - each call of such a helper is run with its real arguments and stand-ins for pool / C / M / F, so its generated
# constructor text is checked like a literal one.
P_CTOR = re.compile(r"public\s+([A-Za-z_]\w*)\s*\([^)]*\)\s*\{")
P_SUPER = re.compile(r'super\(\s*"(?:[^"\\]|\\.)*"\s*(,?)')      # group 1 "," = named command; "" = description-only = usage variant
P_REQ = re.compile(r"(?:(?<![\w.])|this\.)requirePermission\s*\(")
P_SPG = re.compile(r"(?:(?<![\w.])|this\.)setPermissionGroups\s*\((.*?)\)\s*;", re.S)
P_SPG1 = re.compile(r"(?:(?<![\w.])|this\.)setPermissionGroup\s*\(")    # setPermissionGroup(GameMode) = Adventurer / WorldEditor
P_EMPTY = re.compile(r"\s*(?:new\s+(?:java\.lang\.)?String\s*\[\s*0\s*\]|new\s+(?:java\.lang\.)?String\s*\[\s*\]\s*\{\s*\}|[\w.@{}]*EMPTY_STRING_ARRAY)\s*$")
P_NEW = r"\(\s*new\s+[^\s(]*?(\w+)\s*\("
P_SUB, P_REG = re.compile("addSubCommand" + P_NEW), re.compile("registerCommand" + P_NEW)
P_TOKEN = re.compile(r"@(\w+)@")
P_JCOMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
P_GEN_CTOR = re.compile(r"public\s+(?:%s|\{\w+\})\s*\(")
P_GEN_SUPER = re.compile(r'super\(\s*\\?["\'](?:%s|\{\w+\})')
_REC = []


class _Unres(Exception):
    pass


class _Stub(str):
    """Stand-in (an empty str) for every name a generator helper uses that lint cannot evaluate (pool, C, M, F, K, ...). Calling it
    records any constructor text passed in; `x in stub` is True so helper self-checks like `if want not in jv(ctor)` pass."""
    def __new__(cls):
        return str.__new__(cls, "")

    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return self

    def __call__(self, *a, **kw):
        for v in list(a) + list(kw.values()):
            if isinstance(v, str) and not isinstance(v, _Stub) and P_CTOR.search(v):
                _REC.append(v)
        return self

    def __getitem__(self, k):
        return self

    def __setitem__(self, k, v):
        pass

    def __contains__(self, x):
        return True

    def __iter__(self):
        return iter(())

    __hash__ = str.__hash__


_STUB = _Stub()


def _lev(n, env):
    """Evaluate a module-constant-only expression (literals, names of evaluated constants, + % *, subscripts); _Unres otherwise."""
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else str(_lev(v.value, env)) for v in n.values)
    if isinstance(n, (ast.Tuple, ast.List, ast.Set)):
        if any(isinstance(e, ast.Starred) for e in n.elts):
            raise _Unres()
        vals = [_lev(e, env) for e in n.elts]
        return tuple(vals) if isinstance(n, ast.Tuple) else (vals if isinstance(n, ast.List) else set(vals))
    if isinstance(n, ast.Dict):
        d = {}
        for k, v in zip(n.keys, n.values):
            if k is None:
                raise _Unres()
            try:
                d[_lev(k, env)] = _lev(v, env)
            except _Unres:
                d[_lev(k, env)] = _STUB
        return d
    if isinstance(n, ast.Name):
        if n.id in env:
            return env[n.id]
        raise _Unres(n.id)
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Mod, ast.Mult)):
        l, r = _lev(n.left, env), _lev(n.right, env)
        try:
            return l + r if isinstance(n.op, ast.Add) else (l % r if isinstance(n.op, ast.Mod) else l * r)
        except Exception:
            raise _Unres()
    if isinstance(n, ast.Subscript):
        v, k = _lev(n.value, env), _lev(n.slice, env)
        try:
            return v[k]
        except Exception:
            raise _Unres()
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("dict", "list", "set", "tuple") \
            and not n.args and not n.keywords:
        return {"dict": dict, "list": list, "set": set, "tuple": tuple}[n.func.id]()
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        return -_lev(n.operand, env)
    raise _Unres()


def _lev_or_stub(n, env):
    try:
        return _lev(n, env)
    except _Unres:
        return _STUB


def _part(n, env):
    try:
        x = _lev(n, env)
        if isinstance(x, str):
            return x
    except _Unres:
        pass
    return "{" + ast.unparse(n) + "}"


def _render(n, env):
    """Java text of a string expression (constants inlined, other names as {name}); None if n is not a string expression."""
    if isinstance(n, ast.Constant):
        return n.value if isinstance(n.value, str) else None
    if isinstance(n, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else _part(v.value, env) for v in n.values)
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        l, r = _render(n.left, env), _render(n.right, env)
        if l is None and r is None:
            try:
                x = _lev(n, env)
                return x if isinstance(x, str) else None
            except _Unres:
                return None
        return (l if l is not None else _part(n.left, env)) + (r if r is not None else _part(n.right, env))
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod):
        return _render(n.left, env)
    return None


def _ctors(text):
    """(class, body) of every brace-balanced `public Name(...) { ... }` in a Java text."""
    res = []
    for m in P_CTOR.finditer(text):
        depth = 0
        for j in range(m.end() - 1, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    res.append((m.group(1), text[m.end():j], text.count("\n", 0, m.start())))
                    break
    return res


def perm_group_leaks(rel, text, model=None):
    """FAIL messages for build script `rel`: command constructors whose requirePermission node the engine adds to a permission group.
    model (a dict, optional) receives what the check saw: verdicts = [(class, line, verdict)] for every requirePermission constructor."""
    tree = ast.parse(text)
    env, helpers, gen, out = {}, {}, [], []

    def expand(s):
        tokens = {}
        for v in env.values():
            if isinstance(v, dict):
                tokens.update((k, x) for k, x in v.items() if isinstance(k, str) and isinstance(x, str) and not isinstance(x, _Stub))
        for _ in range(3):
            s2 = P_TOKEN.sub(lambda m: tokens.get(m.group(1), m.group(0)), s)
            if s2 == s:
                break
            s = s2
        return s

    def run_helper(fd, code, call):
        ns = {"__builtins__": builtins}
        for nm in {n.id for n in ast.walk(fd) if isinstance(n, ast.Name)}:
            if nm in env:
                ns[nm] = env[nm]
            elif not hasattr(builtins, nm):
                ns[nm] = _STUB
        ns["jv"] = ns["J"] = expand          # the scripts' token expanders (so `want in jv(ctor)` self-checks see real text)
        exec(code, ns)
        if any(isinstance(a, ast.Starred) for a in call.args) or any(k.arg is None for k in call.keywords):
            return [], "star arguments"
        args = [_lev_or_stub(a, env) for a in call.args]
        kw = {k.arg: _lev_or_stub(k.value, env) for k in call.keywords}
        del _REC[:]
        err = None
        try:
            ns[fd.name](*args, **kw)
        except (Exception, SystemExit) as e:
            err = "%s %s" % (type(e).__name__, (str(e).splitlines() or [""])[0][:120])
        return list(_REC), err

    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef):
            seg = ast.get_source_segment(text, stmt) or ""
            if P_GEN_CTOR.search(seg) and P_GEN_SUPER.search(seg):
                helpers[stmt.name] = (stmt, compile(ast.Module(body=[stmt], type_ignores=[]), rel, "exec"))
            else:
                helpers.pop(stmt.name, None)
            continue
        if isinstance(stmt, (ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for n in ast.walk(stmt):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in helpers:
                fd, code = helpers[n.func.id]
                recs, err = run_helper(fd, code, n)
                if not recs:
                    out.append("%s:%d cannot read the command constructor that %s(...) generates (%s) - the permission-group check "
                               "needs it (keep generator helpers to plain arguments)" % (rel, n.lineno, fd.name, err or "no constructor"))
                gen.extend((r, n.lineno) for r in recs)
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name):
                    helpers.pop(t.id, None)
                    try:
                        env[t.id] = _lev(stmt.value, env)
                    except _Unres:
                        env.pop(t.id, None)
                elif isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and isinstance(env.get(t.value.id), dict):
                    try:
                        env[t.value.id][_lev(t.slice, env)] = _lev(stmt.value, env)
                    except (_Unres, TypeError):
                        pass

    # every string expression outside the generator helpers, rendered with the final module constants
    skip = set(id(fd) for fd, _c in helpers.values())
    texts = []

    def visit(n):
        if id(n) in skip:
            return
        if isinstance(n, (ast.Constant, ast.JoinedStr, ast.BinOp)):
            t = _render(n, env)
            if t is not None:
                texts.append((t, getattr(n, "lineno", 0)))
                return
        for c in ast.iter_child_nodes(n):
            visit(c)
    visit(tree)

    recs = []   # (class, body, line)
    tops = set()
    for t, line in texts + gen:
        t = P_JCOMMENT.sub("", expand(t))
        tops |= set(P_REG.findall(t))
        for cls, body, off in _ctors(t):
            if P_SUPER.search(body):
                recs.append((cls, body, line + off))
    parents = {}
    for cls, body, _l in recs:
        for c in P_SUB.findall(body):
            parents.setdefault(c, set()).add(cls)

    def groups(body):
        args = P_SPG.findall(body)
        grant = [a.strip() for a in args if not P_EMPTY.match(a)] + (["setPermissionGroup(GameMode)"] if P_SPG1.search(body) else [])
        return "grant" if grant else ("clear" if args else "none"), grant

    grants = set(cls for cls, body, _l in recs if groups(body)[0] == "grant")
    verdicts = []
    for cls, body, line in recs:
        if not P_REQ.search(body):
            continue
        g, what = groups(body)
        variant = P_SUPER.search(body).group(1) != ","
        verdicts.append((cls, line, "grants " + "; ".join(what) if g == "grant" else "clears groups" if g == "clear" else
                         "usage variant" if variant else "sub of " + "/".join(sorted(parents[cls])) if cls in parents else
                         "top-level" if cls in tops else "parent unknown"))
        if g == "grant":
            out.append("%s:%d %s calls requirePermission AND setPermissionGroups(%s): the engine adds its permission node to those "
                       "groups (every member holds it)" % (rel, line, cls, "; ".join(what)))
        elif g == "clear" or variant:
            continue    # groups cleared, or a description-only usage variant (the engine never adds variant nodes to groups)
        elif cls in parents:
            bad = sorted(p for p in parents[cls] if p in grants)
            if bad:
                out.append("%s:%d %s is a sub-command of %s, which sets permission groups: it calls requirePermission without "
                           "setPermissionGroups(new String[0]), so it inherits those groups and the engine adds its node to them "
                           "(every member holds it) - add setPermissionGroups(new String[0])" % (rel, line, cls, "/".join(bad)))
        elif cls not in tops:
            out.append("%s:%d %s calls requirePermission without setPermissionGroups(new String[0]) and lint cannot find the command "
                       "that registers it (registerCommand) or adds it (addSubCommand): if it is a sub-command it inherits its parent's "
                       "groups and the engine adds its node to them - add setPermissionGroups(new String[0])" % (rel, line, cls))
    if model is not None:
        model.update(verdicts=verdicts, grants=grants, tops=tops, parents=parents, ctors=len(recs), generated=len(gen))
    return out


if "--perm" in sys.argv:
    paths = sys.argv[sys.argv.index("--perm") + 1:]
    n = 0
    for p in paths:
        for x in perm_group_leaks(p, open(p, encoding="utf8", errors="replace").read()):
            print("FAIL  " + x)
            n += 1
    print("permission-group check: %d file(s), %d fail(s)" % (len(paths), n))
    sys.exit(1 if n else 0)


def tracked_files():
    # tracked files PLUS untracked ones that are not .gitignored = exactly what `git add -A` would commit, so a new build script
    # (e.g. an untracked build_<mod>_<newer>.py) is checked locally before its first commit; in CI (clean checkout) this is the same as
    # plain `git ls-files`
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout
        return [l.strip() for l in out.splitlines() if l.strip()]
    except Exception:
        res = []
        for dp, dn, fn in os.walk(ROOT):
            dn[:] = [d for d in dn if d not in (".git", "build_classes", "__pycache__")]
            for f in fn:
                res.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))
        return res


def vkey(path):
    m = re.search(r"_(\d+(?:\.\d+)*)\.py$", path)
    return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)


files = tracked_files()
# a tracked file deleted in the working tree but not yet `git rm`-ed (e.g. a scratch script) is not checked: lint reads the working tree,
# and py_compile / open() would otherwise crash the whole run with FileNotFoundError before any check prints (CI checkouts never hit this)
missing = [f for f in files if not os.path.lexists(os.path.join(ROOT, f))]
if missing:
    gone = set(missing)
    files = [f for f in files if f not in gone]

# ---- forbidden files
for f in files:
    low = f.lower()
    base = os.path.basename(low)
    if base in FORBIDDEN_NAMES:
        fails.append("forbidden game file tracked: " + f)
    if low.endswith(".jar") and f not in ALLOWED_JARS:
        fails.append("jar tracked (build output or someone else's mod): " + f)
    p = os.path.join(ROOT, f)
    if os.path.isfile(p) and os.path.getsize(p) > MAX_BYTES:
        fails.append("file over 5 MB: %s (%d bytes)" % (f, os.path.getsize(p)))

# ---- python syntax
for f in files:
    if not f.endswith(".py"):
        continue
    try:
        py_compile.compile(os.path.join(ROOT, f), doraise=True)
    except py_compile.PyCompileError as e:
        fails.append("python does not parse: %s: %s" % (f, str(e).splitlines()[-1][:200]))

# ---- newest build script per mod
newest = {}
for f in files:
    m = re.match(r"^(Skyy[A-Za-z]+)/build_skyy[a-z]+_(\d+(?:\.\d+)*)\.py$", f)
    if m:
        mod = m.group(1)
        if mod not in newest or vkey(f) > vkey(newest[mod]):
            newest[mod] = f

ID_RE = re.compile(r"#([A-Za-z][A-Za-z0-9_]*)")
UI_HINT = re.compile(r"appendInline|\.set\(\"#|addEventBinding")  # runtime page-building code only (old .ui template strings are dead text)
UI_FILE_RE = re.compile(r"""["'][^"']*\.ui["']""")
CMD_RE = re.compile(r'super\("([a-z][a-z0-9_]*)"')

for mod, f in sorted(newest.items()):
    text = open(os.path.join(ROOT, f), encoding="utf8", errors="replace").read()
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if UI_FILE_RE.search(line) and ("files[" in line or "extra_files" in line or "Common/UI" in line):
            fails.append("%s:%d ships a .ui file (build pages inline)" % (f, i))
        if UI_HINT.search(line):
            for m in ID_RE.finditer(line):
                ident = m.group(1)
                if "_" in ident and not ident.isupper():
                    fails.append("%s:%d UI element id with an underscore: #%s" % (f, i, ident))
    for m in CMD_RE.finditer(text):
        name = m.group(1)
        window = text[m.end(): m.end() + 900]
        close = window.find('}"""')
        body = window if close < 0 else window[:close]
        if "setPermissionGroups" in body or "requirePermission" in body or "requireNoPermission" in body or "ADV" in body:
            continue
        if name in ADMIN_ONLY_OK.get(mod, set()):
            continue
        warns.append("%s: command '%s' has no setPermissionGroups/requirePermission (ordinary players cannot run it)" % (f, name))
    try:
        fails.extend("permission groups: " + x for x in perm_group_leaks(f, text))
    except SyntaxError:
        pass    # already a "python does not parse" FAIL

print("SkyWynn lint: %d files, newest build scripts: %s" % (len(files), ", ".join("%s %s" % (m, vkey(p)) for m, p in sorted(newest.items()))))
if missing:
    print("note: %d tracked file(s) deleted in the working tree (not git rm-ed) were skipped: %s" % (len(missing), ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else "")))
for w in warns:
    print("WARN  " + w)
for x in fails:
    print("FAIL  " + x)
print("%d fail(s), %d warning(s)" % (len(fails), len(warns)))
sys.exit(1 if fails else 0)
