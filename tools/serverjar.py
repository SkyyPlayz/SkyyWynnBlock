"""Cached copies of the game's HytaleServer.jar / Assets.zip, so our JVMs (jpype builds, harnesses, crosscheck, the smoke server)
never hold the INSTALLED files open (2026-10-13: an open installed jar broke the launcher's update to 0.7.1).

    import serverjar
    serverjar.server_jar()   # -> tools/dev/scratch/serverjar/jar-<size>-<mtime>/HytaleServer.jar   (~110 MB)
    serverjar.assets_zip()   # -> tools/dev/scratch/serverjar/assets-<size>-<mtime>/Assets.zip      (~4 GB, copied only on change)

A copy is refreshed when the installed file's size / mtime changes. The installed file is open only while copying (to a temp name, then
an atomic rename), so two processes may call this at once. The newest 2 copies of each kind are kept; older ones are removed only when
unused for 6 h (a file another process holds open cannot be deleted on Windows anyway). If the installed file is missing (launcher
mid-update) the newest cached copy is used.
"""
import os, sys, time, shutil, uuid

HYTALE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale")
GAME = os.path.join(HYTALE, "install", "release", "package", "game", "latest")
INSTALLED_SERVER_JAR = os.path.join(GAME, "Server", "HytaleServer.jar")
INSTALLED_ASSETS = os.path.join(GAME, "Assets.zip")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dev", "scratch", "serverjar")
KEEP = 2
STALE_S = 6 * 3600


def _entries(prefix):
    try:
        names = [n for n in os.listdir(CACHE) if n.startswith(prefix + "-") and os.path.isdir(os.path.join(CACHE, n))]
    except OSError:
        return []
    def age(n):
        try:
            return os.path.getmtime(os.path.join(CACHE, n))
        except OSError:
            return 0
    return sorted(names, key=age, reverse=True)


def _touch(path):
    try:
        with open(os.path.join(os.path.dirname(path), ".used"), "w") as f:
            f.write(str(time.time()))
    except OSError:
        pass


def _prune(prefix, name, keep_dir):
    try:
        _prune1(prefix, name, keep_dir)
    except OSError:                                             # another process pruned / renamed at the same time
        pass


def _prune1(prefix, name, keep_dir):
    now = time.time()
    for n in _entries(prefix)[KEEP:]:
        d = os.path.join(CACHE, n)
        if d == keep_dir:
            continue
        try:
            used = os.path.getmtime(os.path.join(d, ".used"))
        except OSError:
            used = os.path.getmtime(d)
        if now - used > STALE_S:
            shutil.rmtree(d, ignore_errors=True)
    for n in _entries(prefix):                                  # temp files left by a crashed copy
        d = os.path.join(CACHE, n)
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if f.endswith(".tmp"):
                try:
                    if now - os.path.getmtime(p) > 3600:
                        os.remove(p)
                except OSError:
                    pass


def cached(src, prefix, name=None):
    """Path of a cached copy of src (copied / refreshed when src's size or mtime changed)."""
    name = name or os.path.basename(src)
    try:
        st = os.stat(src)
    except OSError:
        for n in _entries(prefix):                              # installed file missing: newest cached copy
            p = os.path.join(CACHE, n, name)
            if os.path.exists(p):
                print("serverjar: %s missing, using cached %s" % (src, p), file=sys.stderr)
                _touch(p)
                return p
        raise SystemExit("serverjar: missing " + src + " and no cached copy")
    d = os.path.join(CACHE, "%s-%d-%d" % (prefix, st.st_size, int(st.st_mtime)))
    dst = os.path.join(d, name)
    if not (os.path.exists(dst) and os.path.getsize(dst) == st.st_size):
        os.makedirs(d, exist_ok=True)
        for attempt in range(3):
            tmp = "%s.%d.%s.tmp" % (dst, os.getpid(), uuid.uuid4().hex[:8])
            try:
                shutil.copyfile(src, tmp)                       # the only time the installed file is open
                st2 = os.stat(src)
                if (st2.st_size, int(st2.st_mtime)) != (st.st_size, int(st.st_mtime)) or os.path.getsize(tmp) != st.st_size:
                    raise OSError("source changed while copying (launcher updating?)")
                try:
                    os.replace(tmp, dst)                        # atomic; another process may have won the race
                except OSError:
                    if not (os.path.exists(dst) and os.path.getsize(dst) == st.st_size):
                        raise
                break
            except OSError as e:
                if attempt == 2:
                    raise SystemExit("serverjar: could not copy %s: %s" % (src, e))
                time.sleep(2)
            finally:
                if os.path.exists(tmp):
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass
    _touch(dst)
    _prune(prefix, name, d)
    return dst


def server_jar():
    return cached(INSTALLED_SERVER_JAR, "jar")


def assets_zip():
    return cached(INSTALLED_ASSETS, "assets")


if __name__ == "__main__":
    print(server_jar())
    if "--assets" in sys.argv:
        print(assets_zip())
