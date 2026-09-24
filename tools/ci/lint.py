"""SkyWynn repo lint - runs on every push (GitHub Actions, .github/workflows/lint.yml) and locally: python tools/ci/lint.py

It cannot build the mods (that needs the game's HytaleServer.jar, which is never committed). It checks the things that are cheap to
check and expensive to get wrong:
  FAIL  a Python file does not parse
  FAIL  a forbidden file is tracked: game files (HytaleServer.jar, Assets.zip), any .jar except tools/javassist.jar, any file > 5 MB
  FAIL  newest build script of a mod ships a .ui file (inline pages only - see HANDOFF section 2)
  FAIL  newest build script of a mod uses an underscore in a UI element id (#Some_Id) - the client cannot resolve those
  WARN  a command constructor in the newest build script has neither setPermissionGroups(...) nor requirePermission(...) - ordinary
        players cannot run it (HANDOFF "COMMAND RULES"); admin-only-by-design commands are listed in ADMIN_ONLY_OK
Exit code 1 on any FAIL.
Files checked = tracked + untracked-but-not-ignored (what `git add -A` would commit), so a new, not yet committed build script counts.
"""
import os, re, sys, subprocess, py_compile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_JARS = {"tools/javassist.jar"}
FORBIDDEN_NAMES = {"hytaleserver.jar", "assets.zip"}
# commands that are admin-only on purpose (auto permission node, only "*" admins have it)
ADMIN_ONLY_OK = {"SkyyRolls": {"rolls", "give", "read", "reroll", "clear"},
                 "SkyyClasses": {"set", "reset", "info", "reload"}}  # /classadmin subcommands (parent requires skyyclasses.admin)

fails, warns = [], []


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

print("SkyWynn lint: %d files, newest build scripts: %s" % (len(files), ", ".join("%s %s" % (m, vkey(p)) for m, p in sorted(newest.items()))))
if missing:
    print("note: %d tracked file(s) deleted in the working tree (not git rm-ed) were skipped: %s" % (len(missing), ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else "")))
for w in warns:
    print("WARN  " + w)
for x in fails:
    print("FAIL  " + x)
print("%d fail(s), %d warning(s)" % (len(fails), len(warns)))
sys.exit(1 if fails else 0)
