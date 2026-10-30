"""SkyWynn repo lint - runs on every push (GitHub Actions, .github/workflows/lint.yml) and locally: python tools/ci/lint.py

It cannot build the mods (that needs the game's HytaleServer.jar, which is never committed). It checks the things that are cheap to
check and expensive to get wrong:
  FAIL  a Python file does not parse
  FAIL  a forbidden file is tracked: game files (HytaleServer.jar, Assets.zip), any .jar except tools/javassist.jar, any file > 5 MB
  FAIL  newest build script of a mod ships a .ui file (inline pages only - see HANDOFF section 2)
  FAIL  newest build script of a mod uses an underscore in a UI element id (#Some_Id) - the client cannot resolve those
  FAIL  newest build script of a mod sets Vertical/HorizontalAlignment to Top / Bottom / Left / Right (client: Start / Center / End only)
  WARN  a command constructor in the newest build script has neither setPermissionGroups(...) nor requirePermission(...) - ordinary
        players cannot run it (HANDOFF "COMMAND RULES"); admin-only-by-design commands are listed in ADMIN_ONLY_OK
  FAIL  newest build script of a mod has a command whose requirePermission node the engine would put into a permission group (e.g.
        hytale:Adventurer = every player): a sub-command that calls requirePermission without setPermissionGroups(new String[0]) under
        a parent that sets groups, a requirePermission command that sets groups itself, or a requirePermission sub-command whose
        parent lint cannot find (details at perm_group_leaks below; SkyyIslands 0.5 /island reload handed every player skyyislands.admin)
  WARN  newest build script that imports the vanilla UI kit (tools/skyyui.py) carries a literal colour that is neither a kit colour
        (skyyui.COLOR) nor a rarity / quality colour (RARITY, RARITY_WYNN, QUALITY) - data colours (class, skill, tree colours...)
        go in a module constant UI_DATA_COLORS (a list / tuple / dict of literals or of earlier module constants, dict .values() /
        .keys(), list() / sorted() of those, a + b) or on a line marked ui-data (never a FAIL; research/Vanilla-UI-Style-Guide.md)
  WARN  the same scripts write their own texture / sound path (TexturePath / Background / SoundPath / ... "<path>.png|.ogg") that the
        kit does not verify (skyyui.TEX / SND), or a FontName other than the vanilla Default / Secondary (never a FAIL; ui-data lines
        are skipped)
  WARN  newest build script of ANY mod fills an ItemGridSlot with something other than a new ItemStack(...) built right there
        (`new ItemGridSlot(stack)`): a stack that carries metadata in a grid slot disconnects the client (HANDOFF section 2; the
        SkyyAuctions 0.1 bug). Build the slot as new ItemGridSlot(new ItemStack(id, qty)), as skyyui.java_grid_methods() does
  WARN  (2026-10-16, FAIL once MENU_PATTERN_FAIL = True after sweep S4) the MENU PATTERN in the newest build scripts that import the
        kit (research/Menu-Pattern.md 3, kit 1.7 hub_page): the "< Menu" button, a hub page still on hub_shell / hub_big_shell, a back
        text ("< Back", "Go Back", "< <word>"), a pager or tab_row on a hub page; a line marked menu-pattern-ok is skipped (grid /
        storage pages that keep real slot pages)
  FAIL  (lock_finally_jump, 2026-10-30; WARN if LOCK_JUMP_FAIL = False) a Java `try` whose `finally` releases a lock (unlock() / release()
        / a lock or busy flag cleared) while the try body leaves through break / continue: javassist does not run that finally (SkyyShards
        0.4.14 busy bug). Checked in every PINNED script (tools/deploy_set.py SET) and the newest scripts; // lock-jump-ok skips a line.
        python tools/ci/lint.py --lockjump <scripts>  lists hits; --lockjump-selftest runs the rule's own test cases
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


# ---- lock_finally_jump (2026-10-30): javassist does NOT run a `finally` block when the try body leaves through `break` / `continue`
# (return and throw do run it - SkyyShards 0.4.15 header). SkyyShards 0.4.14 had `LOCK.lock(); try { ... continue; ... } finally { LOCK.unlock(); }`
# in ShParticles.run: every empty slot leaked one lock hold -> every click "busy". Flag a `try` whose `finally` releases a lock / clears a
# busy flag when the try body (not inside a loop / switch of its own, not inside an anonymous class) contains `break` / `continue`.
# Fix: decide with a flag inside the lock and continue AFTER the finally. A line marked  // lock-jump-ok  is skipped.
LOCK_JUMP_FAIL = True       # 2026-10-30: no pinned / newest script hits it (SkyyShards 0.4.15 fixed the only one) -> FAIL; False = WARN
_LJ_REL_RE = re.compile(r"\.\s*(?:unlock|unlockAll|release|releaseAll|releaseLock|tryRelease)\s*\("
                        r"|\b[\w.@]*(?:lock|LOCK|Lock|busy|BUSY|Busy|held|HELD|Held|inFlight|IN_FLIGHT)\w*\s*=\s*(?:false|null|0)\s*;"
                        r"|\b[\w.@]*(?:lock|LOCK|Lock|busy|BUSY|Busy|held|HELD|Held)\w*\s*\.\s*(?:set\s*\(\s*(?:false|0|null)|remove\s*\(|clear\s*\()"
                        r"|LOCK[\w.)(@ ]*\.\s*fix\s*\(")
_LJ_STR_RE = re.compile(r'"(?:\.|[^"\\n])*"|\'(?:\.|[^\'\\n])\'|//[^\n]*|/\*.*?\*/', re.S)


def _lj_clean(text):
    """The text with Java string / char literals and comments blanked (same length, newlines kept) so braces and keywords can be scanned."""
    text = re.sub(r"(?m)^\s*#[^\n]*", lambda m: " " * len(m.group(0)), text)     # Python comment lines
    return _LJ_STR_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def _lj_close(s, i):
    """Index of the } matching the { at s[i] (or -1)."""
    d = 0
    for j in range(i, len(s)):
        c = s[j]
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                return j
    return -1


def _lj_head(s, a, pos):
    """The statement text before s[pos]: back to the previous ; { } that sits outside parentheses (a for header holds ;)."""
    d = 0
    k = pos - 1
    while k >= a:
        c = s[k]
        if c == ")":
            d += 1
        elif c == "(":
            d -= 1
        elif d <= 0 and c in ";{}":
            break
        k -= 1
    return s[k + 1:pos]


_LJ_KW_RE = re.compile(r"\b(break|continue)\b|[{}]")


def _lj_jumps(s, a, b):
    """Offsets of break / continue in s[a:b] that leave the enclosing try (not inside their own loop / switch / anonymous class)."""
    out, stack = [], []
    for m in _LJ_KW_RE.finditer(s, a, b):
        t = m.group(0)
        if t == "{":
            head = _lj_head(s, a, m.start())
            if re.search(r"\b(?:for|while)\s*\(.*\)\s*$", head, re.S) or re.search(r"\bdo\s*$", head):
                stack.append("loop")
            elif re.search(r"\bswitch\s*\(.*\)\s*$", head, re.S):
                stack.append("switch")
            elif re.search(r"\bnew\s+[\w.@{}]+\s*\([^)]*\)\s*$", head, re.S):
                stack.append("class")
            else:
                stack.append("blk")
        elif t == "}":
            if stack:
                stack.pop()
        else:
            if "class" in stack or "loop" in stack:
                continue
            if t == "break" and "switch" in stack:
                continue
            if re.search(r"\b(?:for|while)\s*\(.*\)\s*$", _lj_head(s, a, m.start()), re.S):     # braceless loop body: for (...) continue;
                continue
            out.append(m.start())
    return out


def lock_finally_jumps(rel, text):
    """Lines 'file:line message' for try blocks whose finally releases a lock while the try body leaves by break / continue."""
    s = _lj_clean(text)
    orig = text.splitlines()
    out = []
    for m in re.finditer(r"\btry\s*\{", s):
        o = m.end() - 1
        c = _lj_close(s, o)
        if c < 0:
            continue
        j = c + 1
        while True:     # skip catch clauses
            cm = re.compile(r"\s*catch\s*\([^)]*\)\s*\{").match(s, j)
            if not cm:
                break
            cc = _lj_close(s, cm.end() - 1)
            if cc < 0:
                break
            j = cc + 1
        fm = re.compile(r"\s*finally\s*\{").match(s, j)
        if not fm:
            continue
        fe = _lj_close(s, fm.end() - 1)
        if fe < 0 or not _LJ_REL_RE.search(s, fm.end(), fe):
            continue
        for p in _lj_jumps(s, o + 1, c):
            ln = s.count("\n", 0, p) + 1
            if "lock-jump-ok" in orig[ln - 1]:
                continue
            kw = re.match(r"\w+", s[p:]).group(0)
            out.append("%s:%d `%s` inside a try whose finally (line %d) releases a lock - javassist does not run that finally on break / "
                       "continue, so the lock is never released (SkyyShards 0.4.14 busy bug); set a flag inside the lock and %s after "
                       "the finally" % (rel, ln, kw, s.count(chr(10), 0, fm.end()) + 1, kw))
    return out


def _lj_selftest():
    bad = ('void run() { for (int i = 0; i < 3; i++) { ShStore.LOCK.lock(); try { if (x == null) continue; work(i); }'
           ' finally { ShStore.LOCK.unlock(); } } }')
    good = ('void run() { for (int i = 0; i < 3; i++) { boolean work = false; ShStore.LOCK.lock(); try { work = x != null; }'
            ' finally { ShStore.LOCK.unlock(); } if (!work) continue; work(i); } }')
    inner = 'void f() { LOCK.lock(); try { for (int i = 0; i < 3; i++) { if (i == 1) continue; if (i == 2) break; } return; } finally { LOCK.unlock(); } }'
    cls = 'void g() { for (;;) { LOCK.lock(); try { String s = "continue; } finally {"; a(); } finally { LOCK.unlock(); } } }'
    close = 'void h() { for (;;) { try { if (a) break; } finally { in.close(); } } }'
    cases = ((bad, 1), (good, 0), (inner, 0), (cls, 0), (close, 0))
    n = 0
    for src, want in cases:
        got = len(lock_finally_jumps("selftest", src))
        if got != want:
            print("FAIL  lock_finally_jump selftest: expected %d hit(s), got %d for: %s" % (want, got, src[:70]))
            n += 1
    print("lock_finally_jump selftest: %d case(s), %d fail(s)" % (len(cases), n))
    return n


if "--lockjump-selftest" in sys.argv:
    sys.exit(1 if _lj_selftest() else 0)
if "--lockjump" in sys.argv:
    _n = 0
    for p in sys.argv[sys.argv.index("--lockjump") + 1:]:
        for x in lock_finally_jumps(p, open(p, encoding="utf8", errors="replace").read()):
            print("HIT   " + x)
            _n += 1
    print("lock_finally_jump: %d hit(s)" % _n)
    sys.exit(0)



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
# ---- WARN only: ItemGridSlot content (the metadata rule). `new ItemGridSlot(` (also as the @IGS@ / {IGS} class tokens of the build
# scripts) whose argument is neither empty nor a `new ItemStack(` (@IS@ / {IS}) built right there
GRID_SLOT_NEW_RE = re.compile(r"new\s+(?:[A-Za-z_][\w.]*\.)?(?:ItemGridSlot|@IGS@|\{IGS\})\s*\("
                              r"(?!\s*\)|\s*new\s+(?:[A-Za-z_][\w.]*\.)?(?:ItemStack|@IS@|\{IS\})\s*\()")


def grid_slot_warnings(rel, text):
    """WARN lines for ItemGridSlots built from anything but a fresh new ItemStack(...) (a held stack may carry metadata)."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if GRID_SLOT_NEW_RE.search(line):
            out.append("%s:%d ItemGridSlot built from a stack that is not a new ItemStack(id, qty) made right there - item metadata in "
                       "a grid slot disconnects the client (HANDOFF section 2; use skyyui.java_grid_methods / java_grid_fill)" % (rel, i))
    return out

ALIGN_BAD_RE = re.compile(r"\b(VerticalAlignment|HorizontalAlignment)\s*:\s*(Top|Bottom|Left|Right)\b")

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
        m2 = ALIGN_BAD_RE.search(line)
        if m2:
            fails.append("%s:%d UI %s: %s - the client only accepts Start / Center / End (a Top / Bottom / Left / Right value "
                         "disconnects the player, 2026-10-15 #SkyyGPFig)" % (f, i, m2.group(1), m2.group(2)))
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
    warns.extend(grid_slot_warnings(f, text))
    try:
        fails.extend("permission groups: " + x for x in perm_group_leaks(f, text))
    except SyntaxError:
        pass    # already a "python does not parse" FAIL

# ---- WARN only: literal colours outside the vanilla UI kit, in the newest build scripts that import tools/skyyui.py
KIT_IMPORT_RE = re.compile(r"^[ \t]*(?:import[ \t]+skyyui\b|from[ \t]+skyyui[ \t]+import\b)", re.M)
# a colour literal: #rrggbb[aa] with an optional well-formed (alpha); not an element id (#Facade {, "#Facade.Text") and never a
# malformed alpha such as #ffffff(...) or #123456(1.2.3) (those are skipped - skyyui.norm_color would not parse them)
KIT_HEX_RE = re.compile(r"(?<![0-9A-Za-z_&])#([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)(\(\s*(?:\d+(?:\.\d+)?|\.\d+)\s*\))?"
                        r"(?![0-9A-Za-z_.(])(?!\s*\{)")
KIT_PY_COMMENT_RE = re.compile(r"(?:^|\s)#\s.*$")
KIT_MAX_WARNS = 25
KIT_PATH_RE = re.compile(r'(?:TexturePath|Background|SoundPath|Texture|BarTexturePath|EffectTexturePath|MaskTexturePath|'
                         r'SlotBackground|FallbackTexturePath|LabelMaskTexturePath)\s*:\s*\(?\s*(?:TexturePath\s*:\s*)?\\?"'
                         r'([^"\\]+\.(?:png|ogg))\\?"')
KIT_FONT_RE = re.compile(r'FontName\s*:\s*\\?"([^"\\]*)\\?"')


def _kit_lev(n, env):
    """_lev plus the shapes a UI_DATA_COLORS constant takes: list / tuple / set / sorted(x), d.values() / .keys() / .items(), a + b."""
    if isinstance(n, ast.Call) and not n.keywords:
        f = n.func
        if isinstance(f, ast.Name) and f.id in ("list", "tuple", "set", "sorted") and len(n.args) == 1:
            v = _kit_lev(n.args[0], env)
            try:
                return set(v) if f.id == "set" else list(v)
            except TypeError:
                raise _Unres()
        if isinstance(f, ast.Attribute) and f.attr in ("values", "keys", "items") and not n.args:
            v = _kit_lev(f.value, env)
            if isinstance(v, dict):
                return list(getattr(v, f.attr)())
            raise _Unres()
    if isinstance(n, (ast.List, ast.Tuple, ast.Set)) and not any(isinstance(e, ast.Starred) for e in n.elts):
        out = []
        for e in n.elts:                # an element lint cannot evaluate is skipped, the rest still counts
            try:
                out.append(_kit_lev(e, env))
            except _Unres:
                pass
        return out
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        l, r = _kit_lev(n.left, env), _kit_lev(n.right, env)
        try:
            return (list(l) + list(r)) if isinstance(l, (list, tuple)) and isinstance(r, (list, tuple)) else l + r
        except TypeError:
            raise _Unres()
    if isinstance(n, ast.Dict) and None not in n.keys:
        d = {}
        for k, v in zip(n.keys, n.values):
            try:
                d[_kit_lev(k, env)] = _kit_lev(v, env)
            except (_Unres, TypeError):
                pass
        return d
    return _lev(n, env)


def _kit_strs(v):
    """Every str inside a (nested) list / tuple / set / dict value."""
    if isinstance(v, str):
        return [v]
    if isinstance(v, dict):
        return _kit_strs(list(v.keys())) + _kit_strs(list(v.values()))
    if isinstance(v, (list, tuple, set)):
        return [x for e in v for x in _kit_strs(e)]
    return []


def _kit_code_lines(text):
    """(line number, code) of every line that is not a Python comment and not marked ui-data."""
    for i, line in enumerate(text.splitlines(), 1):
        if "ui-data" in line:
            continue
        yield i, (KIT_PY_COMMENT_RE.sub("", line) if line.lstrip().startswith("#") or " # " in line else line)


def kit_color_warnings(rel, text, kit):
    """WARN lines for literal colours that are not skyyui kit / rarity colours (UI_DATA_COLORS and ui-data lines excepted)."""
    allowed = set(kit.allowed_colors())
    try:
        env = {}
        for stmt in ast.parse(text).body:
            if not isinstance(stmt, ast.Assign):
                continue
            names = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            try:
                v = _kit_lev(stmt.value, env)
            except (_Unres, TypeError, ValueError):
                v = None
            if "UI_DATA_COLORS" in names:
                allowed |= set(kit.norm_color(x) for x in _kit_strs(v))
            for nm in names:            # earlier module constants resolve inside a later UI_DATA_COLORS
                if v is None:
                    env.pop(nm, None)
                else:
                    env[nm] = v
    except SyntaxError:
        return []
    opaque = set(c for c in allowed if "(" not in c and len(c) == 7)
    out, extra = [], 0
    for i, code in _kit_code_lines(text):
        for m in KIT_HEX_RE.finditer(code):
            lit = "#" + m.group(1) + (m.group(2) or "")
            n = kit.norm_color(lit)
            if n in allowed or (m.group(2) and ("#" + m.group(1).lower()) in opaque):
                continue
            if len(out) < KIT_MAX_WARNS:
                out.append("%s:%d colour %s is not a skyyui kit / rarity colour - use skyyui.COLOR[...] (data colours: UI_DATA_COLORS or "
                           "a ui-data line)" % (rel, i, lit))
            else:
                extra += 1
    if extra:
        out.append("%s: %d more non-kit colour(s) not listed" % (rel, extra))
    return out


def kit_style_warnings(rel, text, kit):
    """WARN lines for texture / sound paths the kit does not verify and for fonts other than the vanilla two (ui-data lines excepted)."""
    known = set(kit.TEX.values()) | set(kit.SND.values())
    fonts = set(kit.FONTS)
    out, extra = [], 0
    for i, code in _kit_code_lines(text):
        found = ["path %s is not a skyyui kit texture / sound (skyyui.TEX / SND) - use the kit builders or add it to the kit with its "
                 "vanilla proof" % m.group(1) for m in KIT_PATH_RE.finditer(code) if m.group(1) not in known]
        found += ['FontName "%s" is not a vanilla font (Default / Secondary)' % m.group(1) for m in KIT_FONT_RE.finditer(code)
                  if m.group(1) not in fonts]
        for f in found:
            if len(out) < KIT_MAX_WARNS:
                out.append("%s:%d %s" % (rel, i, f))
            else:
                extra += 1
    if extra:
        out.append("%s: %d more non-kit path / font warning(s) not listed" % (rel, extra))
    return out


_kit_users = [(mod, f) for mod, f in sorted(newest.items())
              if KIT_IMPORT_RE.search(open(os.path.join(ROOT, f), encoding="utf8", errors="replace").read())]
if _kit_users:
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import skyyui as _kit
    except Exception as e:      # the kit itself failing to import is reported, never a FAIL of this rule
        _kit = None
        warns.append("tools/skyyui.py could not be imported (%s: %s) - the kit colour / path / font rules were skipped"
                     % (type(e).__name__, e))
    if _kit is not None:
        for mod, f in _kit_users:
            _src = open(os.path.join(ROOT, f), encoding="utf8", errors="replace").read()
            warns.extend(kit_color_warnings(f, _src, _kit))
            warns.extend(kit_style_warnings(f, _src, _kit))

# ---- WARN (FAIL after the sweep): the MENU PATTERN (research/Menu-Pattern.md 3 + rules 7-8; kit 1.7 tools/skyyui.py hub_page). Skyy
# 2026-10-16: "make sure its consistent across the board, then follow the pattern when making new or adding to existing menus." + "I never
# want to have to use a back button. The menus at the top should always be there for easy navigation." In the newest build script of
# every mod that imports the kit, on code lines (comments and lines marked menu-pattern-ok skipped):
#   menu-button  "< Menu" (HUB_MENU_TEXT / hub_menu_button / the literal) - the kit 1.5 back button
#   old-shell    hub_shell( / hub_big_shell( - a hub page not yet on hub_page() (kit 1.7)
#   back-text    a "< Back" / "Back" / "Go Back" / "< SkyWynn Menu" / "< <word>" text (not "< Prev") - rows 1 + 2 replace them
#   pager        pager( / "< Prev" in a script with hub pages (scroll lists; grid / storage pages mark their line menu-pattern-ok)
#   tab-row      tab_row( in a script with hub pages (a hub page has at most ONE sub-tab row: hub_page(sub=True) + HubBar.subTab)
# One line per (file, rule) with the count and the first lines. MENU_PATTERN_FAIL = True after sweep S4 turns them into FAILs.
MENU_PATTERN_FAIL = True    # flipped 2026-10-17 (all newest scripts pass); allow a line with a  # menu-pattern-ok  marker, a dev probe via MP_EXEMPT_MODS
MP_RULES = (
    ("menu-button", re.compile(r'HUB_MENU_TEXT|hub_menu_button\(|"<\s?Menu"'), False),
    ("old-shell", re.compile(r"\bhub_(?:big_)?shell\("), False),
    ("back-text", re.compile(r'"(?:<\s?(?!Prev\b|Previous\b|PREV\b)[A-Za-z][A-Za-z ]*|Back|Go Back|Back to [A-Za-z ]+)"'), False),
    ("pager", re.compile(r'\bpager\(|"<\s?Prev'), True),
    ("tab-row", re.compile(r"\btab_row\("), True),
)
# retired one-session UI probes (not player menus) are exempt; a /back-command label go(..., "Back", n) is not a menu button
MP_EXEMPT_MODS = ("SkyyUiProbe", "SkyyUiProbeB")
MP_CMD_LABEL_RE = re.compile(r'\bgo\(')
MP_HUB_RE = re.compile(r"\bhub_(?:page|shell|big_shell)\(")


def menu_pattern_warnings(rel, text):
    """WARN (or FAIL) lines of the menu pattern rules for one build script (see MP_RULES above)."""
    hubby = MP_HUB_RE.search(text) is not None
    hits = {}
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#") or "menu-pattern-ok" in line:
            continue
        code = line.split("  # ")[0] if "  # " in line else line
        for name, rx, hub_only in MP_RULES:
            if hub_only and not hubby:
                continue
            if name == "back-text" and MP_CMD_LABEL_RE.search(code):
                continue
            if rx.search(code):
                hits.setdefault(name, []).append(i)
    out = []
    for name, _rx, _h in MP_RULES:
        if name in hits:
            ln = hits[name]
            out.append("%s:%d menu pattern %s: %d line(s) (%s) - research/Menu-Pattern.md 3, tools/HUBS-CONTRACT.md 'Kit 1.7'" % (
                rel, ln[0], name, len(ln), ", ".join(str(x) for x in ln[:6]) + (" ..." if len(ln) > 6 else "")))
    return out


for mod, f in sorted(newest.items()):
    _src = open(os.path.join(ROOT, f), encoding="utf8", errors="replace").read()
    if KIT_IMPORT_RE.search(_src) and mod not in MP_EXEMPT_MODS:
        (fails if MENU_PATTERN_FAIL else warns).extend(menu_pattern_warnings(f, _src))

# ---- lock_finally_jump over the PINNED scripts (tools/deploy_set.py SET) and the newest scripts (WARN, or FAIL once LOCK_JUMP_FAIL)
def _pinned_scripts():
    try:
        src = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf8", errors="replace").read()
        src = re.sub(r"(?m)#.*$", "", src)
        i = src.index("SET = [")
        j = src.index(chr(10) + "]", i)
        return ["%s/build_%s_%s.py" % (m.group(1), m.group(1).lower(), m.group(2))
                for m in re.finditer(r'\(\s*"(Skyy[A-Za-z]+)"\s*,\s*"(\d+(?:\.\d+)*)"', src[i:j])]
    except Exception as e:
        warns.append("lock_finally_jump: could not read the pinned SET from tools/deploy_set.py (%s)" % e)
        return []


_lj_hits = {}
for _f in sorted(set(_pinned_scripts()) | set(newest.values())):
    _p = os.path.join(ROOT, _f)
    if os.path.isfile(_p):
        _lj_hits[_f] = lock_finally_jumps(_f, open(_p, encoding="utf8", errors="replace").read())
for _f, _h in sorted(_lj_hits.items()):
    (fails if LOCK_JUMP_FAIL else warns).extend("lock_finally_jump: " + x for x in _h)

print("SkyWynn lint: %d files, newest build scripts: %s" % (len(files), ", ".join("%s %s" % (m, vkey(p)) for m, p in sorted(newest.items()))))
if missing:
    print("note: %d tracked file(s) deleted in the working tree (not git rm-ed) were skipped: %s" % (len(missing), ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else "")))
for w in warns:
    print("WARN  " + w)
for x in fails:
    print("FAIL  " + x)
print("%d fail(s), %d warning(s)" % (len(fails), len(warns)))
sys.exit(1 if fails else 0)
