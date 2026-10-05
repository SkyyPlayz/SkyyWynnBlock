"""Keep the LOCAL-ONLY files (git-ignored: backups, built jars, caches, scratch) small and easy to find. Touches only this project
folder - never UserData, never the game. Run it after every deploy (PROJECT-RULES section 5).

  python tools/tidy_local.py                      # dry run: shows what it would do
  python tools/tidy_local.py --yes                # do it
  python tools/tidy_local.py --yes --scratch a,b  # also pack the finished scratch folders tools/dev/scratch/a + b

1. Build caches: deletes every __pycache__/ and build_classes/ folder (each build recreates them; skyybuild.class_out wipes it anyway).
2. Old jars: per mod keeps the SET jar (tools/deploy_set.py), the newest older jar (one-step rollback) and anything newer than the SET
   (built, not deployed yet); retired mods keep their newest jar. The rest go into backups/archive/old-jars-<date>.tar.xz.
3. Old deploy backups: keeps the newest KEEP backups/deploy-* folders; older ones go into backups/archive/deploys-<YYYY-MM>[-n].tar.xz.
4. --scratch: packs the named tools/dev/scratch/<name> folders into backups/archive/scratch-<name>-<date>.tar.xz. Junk folders
   (_avast_, hsperfdata_*) inside scratch are always deleted.
5. Writes backups/README.md: every backup (folder or archive) with what that deploy changed, + how to restore.

Every archive is re-read and each file compared byte for byte (sha256) BEFORE the originals are removed - nothing is lost except the
build caches in step 1. Needs only Python 3.
"""
import hashlib, io, json, os, re, shutil, sys, tarfile, time, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUPS = os.path.join(ROOT, "backups")
ARCHIVE = os.path.join(BACKUPS, "archive")
SCRATCH = os.path.join(ROOT, "tools", "dev", "scratch")
KEEP = 5
SKIP_WALK = {".git", "backups"}
JAR = re.compile(r"^(Skyy[A-Za-z]+)-(\d+(?:\.\d+)*)(-[\w.-]+)?\.jar$")
DO = "--yes" in sys.argv
TODAY = time.strftime("%Y%m%d")


def ver(s):
    return tuple(int(x) for x in s.split("."))


def load_set():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    src = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()
    m = re.search(r"^SET = \[(.*?)^\]", src, re.S | re.M)
    return dict(re.findall(r'\("(Skyy\w+)", "([\d.]+)"\)', m.group(1)))


def sha(path_or_bytes):
    h = hashlib.sha256()
    if isinstance(path_or_bytes, bytes):
        h.update(path_or_bytes)
    else:
        with open(path_or_bytes, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
    return h.hexdigest()


def size(paths):
    t = 0
    for p in paths:
        if os.path.isfile(p):
            t += os.path.getsize(p)
        else:
            for d, _, fs in os.walk(p):
                t += sum(os.path.getsize(os.path.join(d, f)) for f in fs)
    return t


def mb(n):
    return "%.1f MB" % (n / 1048576.0)


def free_name(base):
    p, n = os.path.join(ARCHIVE, base + ".tar.xz"), 2
    while os.path.exists(p):
        p, n = os.path.join(ARCHIVE, "%s-%d.tar.xz" % (base, n)), n + 1
    return p


def pack(items, out, arc_root):
    """items = files / folders; stored relative to arc_root. Verifies every file, then removes the originals."""
    files = []
    for it in items:
        if os.path.isfile(it):
            files.append(it)
        else:
            for d, _, fs in os.walk(it):
                files += [os.path.join(d, f) for f in fs]
    want = {os.path.relpath(f, arc_root).replace("\\", "/"): sha(f) for f in files}
    print("   pack %d files (%s) -> %s" % (len(files), mb(size(items)), os.path.relpath(out, ROOT)))
    if not DO:
        return
    os.makedirs(ARCHIVE, exist_ok=True)
    tmp = out + ".part"
    with tarfile.open(tmp, "w:xz", preset=9) as t:  # preset 9 = 64 MB window, so repeated jars across backups pack to almost nothing
        for it in items:
            t.add(it, arcname=os.path.relpath(it, arc_root).replace("\\", "/"))
    got = {}
    with tarfile.open(tmp, "r:xz") as t:
        for m in t:
            if m.isfile():
                got[m.name] = sha(t.extractfile(m).read())
    if got != want:
        os.remove(tmp)
        sys.exit("VERIFY FAILED for %s - nothing removed" % out)
    os.replace(tmp, out)
    for it in items:
        shutil.rmtree(it) if os.path.isdir(it) else os.remove(it)
    print("   verified %d files, originals removed (%s)" % (len(got), mb(os.path.getsize(out))))


def step_caches():
    found = []
    for d, subs, _ in os.walk(ROOT):
        subs[:] = [s for s in subs if s not in SKIP_WALK and not (d == ROOT and s == ".claude")]
        for s in list(subs):
            if s in ("__pycache__", "build_classes"):
                found.append(os.path.join(d, s))
                subs.remove(s)
    print("1. build caches: %d folders, %s" % (len(found), mb(size(found))))
    if DO:
        for p in found:
            shutil.rmtree(p, ignore_errors=True)


def step_jars(pins):
    old = []
    for mod in sorted(os.listdir(ROOT)):
        mdir = os.path.join(ROOT, mod)
        if not (mod.startswith("Skyy") and os.path.isdir(mdir)):
            continue
        jars = []
        for f in os.listdir(mdir):
            m = JAR.match(f)
            if m and m.group(1) == mod:
                jars.append((ver(m.group(2)), m.group(3) or "", f))
        if not jars:
            continue
        jars.sort()
        if mod in pins:
            pv = ver(pins[mod])
            plain_old = [j for j in jars if j[0] < pv and not j[1]]
            keep = {j[2] for j in jars if j[0] >= pv and not j[1]} | ({plain_old[-1][2]} if plain_old else set())
        else:  # retired / never pinned: keep the newest
            keep = {[j for j in jars if not j[1]][-1][2]} if any(not j[1] for j in jars) else set()
        old += [os.path.join(mdir, j[2]) for j in jars if j[2] not in keep]
    print("2. old jars: %d to pack (%s)" % (len(old), mb(size(old))))
    if old:
        pack(old, free_name("old-jars-" + TODAY), ROOT)


def step_backups():
    if not os.path.isdir(BACKUPS):
        return
    deps = sorted(d for d in os.listdir(BACKUPS) if d.startswith("deploy-") and os.path.isdir(os.path.join(BACKUPS, d)))
    old = deps[:-KEEP] if len(deps) > KEEP else []
    months = {}
    for d in old:
        months.setdefault(d[7:11] + "-" + d[11:13], []).append(os.path.join(BACKUPS, d))
    print("3. deploy backups: %d folders, keep newest %d, pack %d into %d archive(s)" % (len(deps), KEEP, len(old), len(months)))
    for mo, items in sorted(months.items()):
        pack(items, free_name("deploys-" + mo), BACKUPS)


def step_scratch(names):
    if not os.path.isdir(SCRATCH):
        return
    junk = []
    for d, subs, _ in os.walk(SCRATCH):
        for s in list(subs):
            if s == "_avast_" or s.startswith("hsperfdata_"):
                junk.append(os.path.join(d, s))
                subs.remove(s)
    print("4. scratch: %d junk folders (%s)%s" % (len(junk), mb(size(junk)), "; pack " + ", ".join(names) if names else ""))
    if DO:
        for p in junk:
            shutil.rmtree(p, ignore_errors=True)
    for n in names:
        p = os.path.join(SCRATCH, n)
        if os.path.isdir(p):
            pack([p], free_name("scratch-%s-%s" % (n, TODAY)), SCRATCH)
        else:
            print("   no scratch folder " + n)


def jar_versions_dir(mods_dir):
    out = {}
    for f in sorted(os.listdir(mods_dir)):
        if f.endswith(".jar"):
            out[f[:-4]] = manifest_version(open(os.path.join(mods_dir, f), "rb").read())
    return out


def manifest_version(data):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            return str(json.loads(z.read("manifest.json").decode("utf-8-sig")).get("Version", "?"))
    except Exception:
        return "?"


def all_backups():
    """[(name, where, {jar: version})] oldest first, from folders and archives."""
    res = []
    if os.path.isdir(ARCHIVE):
        for a in sorted(os.listdir(ARCHIVE)):
            if not a.startswith("deploys-") or not a.endswith(".tar.xz"):
                continue
            per = {}
            with tarfile.open(os.path.join(ARCHIVE, a), "r:xz") as t:
                for m in t:
                    parts = m.name.split("/")
                    if m.isfile() and len(parts) == 3 and parts[1] == "Mods" and parts[2].endswith(".jar"):
                        per.setdefault(parts[0], {})[parts[2][:-4]] = manifest_version(t.extractfile(m).read())
            res += [(n, "archive/" + a, per[n]) for n in sorted(per)]
    for d in sorted(os.listdir(BACKUPS)) if os.path.isdir(BACKUPS) else []:
        p = os.path.join(BACKUPS, d, "Mods")
        if d.startswith("deploy-") and os.path.isdir(p):
            res.append((d, "folder", jar_versions_dir(p)))
    return sorted(res)


def step_readme():
    if not DO:
        print("5. backups/README.md: written on --yes")
        return
    rows, prev = [], {}
    for name, where, jars in all_backups():
        ch = ["%s %s" % (j, v) if j not in prev else "%s %s->%s" % (j, prev[j], v) for j, v in sorted(jars.items()) if prev.get(j) != v]
        ch += ["-%s" % j for j in sorted(prev) if j not in jars]
        rows.append("| %s | %s | %s |" % (name, where, ", ".join(ch) if prev else "%d jars (first backup)" % len(jars)))
        prev = jars
    others = sorted(a for a in os.listdir(ARCHIVE) if not a.startswith("deploys-")) if os.path.isdir(ARCHIVE) else []
    txt = """# backups/ - LOCAL ONLY (git-ignored; made by tools/backup_deploy.py, tidied by tools/tidy_local.py)

Written by `python tools/tidy_local.py --yes` on %s - do not edit by hand. Each deploy backup = the live Skyy jars (`Mods/`), the test
world's `config.json` and every `Skyy_*` mod-data folder (`data/`) from just BEFORE that deploy.

## Restore one backup
1. Unpack it if it is in an archive: `tar -xJf backups/archive/<file>.tar.xz -C backups deploy-<stamp>`
   (or `python -c "import tarfile; tarfile.open('backups/archive/<file>.tar.xz').extractall('backups')"`).
2. Game closed. Follow HANDOFF.md "ROLLBACK FLOORS + STEPS" and the comments in `tools/deploy_set.py` before copying anything back.

## Other archives
%s

## Every deploy backup (newest last). A backup is the state just BEFORE its own deploy, so "Changed" (jar versions vs the backup
## before it; -X = jar gone) = what the PREVIOUS deploy(s) put live
| Backup | Where | Changed |
|---|---|---|
%s
""" % (time.strftime("%Y-%m-%d %H:%M"),
       "\n".join("- `archive/%s` - %s" % (a, "old built jars (any version not kept next to its build script)" if a.startswith("old-jars")
                                           else "finished agent scratch folder" if a.startswith("scratch-") else "other")
                 for a in others) or "- none",
       "\n".join(rows))
    with open(os.path.join(BACKUPS, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    print("5. wrote backups/README.md (%d backups listed)" % len(rows))


def main():
    names = []
    if "--scratch" in sys.argv:
        names = [n for n in sys.argv[sys.argv.index("--scratch") + 1].split(",") if n]
    print("tidy_local %s (%s)" % ("RUN" if DO else "DRY RUN - add --yes", ROOT))
    step_caches()
    step_jars(load_set())
    step_backups()
    step_scratch(names)
    step_readme()


if __name__ == "__main__":
    main()
