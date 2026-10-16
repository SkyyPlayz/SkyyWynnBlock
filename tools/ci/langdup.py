"""SkyWynn lang duplicate check: one writer per language key across the SET jars (research/Tier-Tags-Plan.md section 3 / round T0).

    python tools/ci/langdup.py                                   # the SET jars from tools/deploy_set.py
    python tools/ci/langdup.py --jar SkyyCollections/SkyyCollections-0.2.18.jar
                                                                 # a candidate jar replaces its mod's SET entry (a new mod is added)
    python tools/ci/langdup.py --list                            # + every key two jars write (identical ones too)

Reads every *.lang file inside every jar (read-only; nothing is extracted). A key is compared in its full form: the file's own name is the
prefix the engine puts in front of it (Server/Languages/en-US/server.lang: "items.X.name" = "server.items.X.name"; a key that already
starts with "server." is taken as written), per locale (the folder above the file). So "items.X.description" in one jar and
"server.items.X.description" in another are the SAME key.
  FAIL  one key written by two (or more) jars with DIFFERENT values (which text wins is not defined - the plan's rule: one writer per key)
  FAIL  one jar writes one key twice with different values (e.g. the items.X / server.items.X twins disagree)
  WARN  one key written by two jars with the SAME value (harmless today, but the key still has two owners)
  WARN  a line that is not "key = value" (skipped)
Exit code 1 on any FAIL. Pure Python (zipfile), about a second for the SET.
"""
import os, sys, re, zipfile, argparse

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

KEY_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")


def set_jars():
    import deploy_set
    return [(m, v, os.path.join(ROOT, m, "%s-%s.jar" % (m, v))) for m, v in deploy_set.SET]


def mod_of(path):
    m = re.match(r"^([A-Za-z]\w*?)-(\d+(?:\.\d+)*)\.jar$", os.path.basename(path))
    if not m:
        raise SystemExit("cannot read <Mod>-<version>.jar from %s" % path)
    return m.group(1), m.group(2)


def full_key(lang_path, key):
    """(locale, full key): the file name (server / client / ...) is the key prefix unless the key already carries it"""
    parts = lang_path.replace("\\", "/").split("/")
    locale = parts[-2] if len(parts) >= 2 else ""
    stem = parts[-1][:-5]
    return locale, (key if key.startswith(stem + ".") else stem + "." + key)


def parse_lang(text):
    """[(line number, key, value)] + [bad line numbers]; '#' lines and blank lines skipped; value trimmed (the engine trims too)"""
    rows, bad = [], []
    for n, line in enumerate(text.splitlines(), 1):
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        if "=" not in t:
            bad.append(n)
            continue
        k, v = t.split("=", 1)
        k = k.strip()
        if not KEY_RE.match(k):
            bad.append(n)
            continue
        rows.append((n, k, v.strip()))
    return rows, bad


def jar_keys(path):
    """{(locale, full key): [(lang file, line, value)]} for one jar + [(file, line)] bad lines"""
    out, bad = {}, []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.endswith(".lang"):
                continue
            rows, b = parse_lang(z.read(name).decode("utf-8-sig"))
            bad += [(name, n) for n in b]
            for n, k, v in rows:
                out.setdefault(full_key(name, k), []).append((name, n, v))
    return out, bad


def check(jars):
    """(fails, warns, stats) over [(mod, version, jar path)]"""
    fails, warns = [], []
    owners = {}                  # (locale, key) -> {mod: value}
    nfiles = nkeys = 0
    for mod, ver, path in jars:
        keys, bad = jar_keys(path)
        nkeys += len(keys)
        nfiles += len(set(f for rows in keys.values() for f, _n, _v in rows))
        for f, n in bad:
            warns.append("WARN %s %s: %s line %d is not 'key = value' (skipped)" % (mod, ver, f, n))
        for lk, rows in sorted(keys.items()):
            vals = set(v for _f, _n, v in rows)
            if len(vals) > 1:
                fails.append("FAIL %s %s writes %s [%s] %d times with %d different values: %s" % (
                    mod, ver, lk[1], lk[0], len(rows), len(vals), "; ".join("%s:%d" % (f, n) for f, n, _v in rows)))
            owners.setdefault(lk, {})[mod] = rows[0][2]
    for lk, by in sorted(owners.items()):
        if len(by) < 2:
            continue
        if len(set(by.values())) > 1:
            fails.append("FAIL %s [%s] is written by %d jars with different values: %s" % (
                lk[1], lk[0], len(by), " | ".join("%s = %s" % (m, (v if len(v) <= 70 else v[:67] + "...")) for m, v in sorted(by.items()))))
        else:
            warns.append("WARN %s [%s] is written by %d jars with the same value: %s" % (lk[1], lk[0], len(by), ", ".join(sorted(by))))
    return fails, warns, {"jars": len(jars), "files": nfiles, "keys": len(owners), "jar_keys": nkeys}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", action="append", default=[])
    ap.add_argument("--list", action="store_true", help="print every WARN line (default: the first 20)")
    a = ap.parse_args()
    jars = set_jars()
    overrides = {}
    for p in a.jar:
        p = os.path.abspath(p if os.path.exists(p) else os.path.join(ROOT, p))
        if not os.path.isfile(p):
            raise SystemExit("no such jar: " + p)
        mod, ver = mod_of(p)
        overrides[mod] = (mod, ver, p)
    jars = [overrides.pop(m) if m in overrides else (m, v, j) for m, v, j in jars] + list(overrides.values())
    missing = [j for _m, _v, j in jars if not os.path.isfile(j)]
    if missing:
        print("FAIL missing jar(s):\n  " + "\n  ".join(missing))
        return 1
    fails, warns, st = check(jars)
    for line in fails:
        print(line)
    for line in (warns if a.list else warns[:20]):
        print(line)
    if len(warns) > 20 and not a.list:
        print("... %d more WARN lines (--list)" % (len(warns) - 20))
    print("langdup: %d jars, %d lang files, %d keys (%d per-jar keys); %d FAIL, %d WARN -> %s" % (
        st["jars"], st["files"], st["keys"], st["jar_keys"], len(fails), len(warns), "FAIL" if fails else "OK"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
