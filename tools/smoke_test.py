"""SkyWynn smoke test (PROJECT-RULES section 3 step 3b): start the whole SET on an OFFLINE HytaleServer (no client) against a scratch
COPY of the test world, read its log, stop it.

Usage (game closed - it refuses while any HytaleServer java process runs):
    python tools/smoke_test.py                                   # the SET jars from tools/deploy_set.py (project folders, not Mods)
    python tools/smoke_test.py --jar SkyyGear/SkyyGear-0.2.14.jar  # a candidate jar replaces its mod's SET entry (a new mod is added)
    python tools/smoke_test.py --jar SkyyCore/SkyyCore-1.0.0.jar --jar SkyyBank/SkyyBank-0.1.14.jar   # SkyyCore + a Core-mode module
    python tools/smoke_test.py --jar SkyyBank/SkyyBank-0.1.14.jar --drop SkyyCore    # the MISSING-CORE boot: SkyyBank must be skipped
                                                                 # with the engine's dependency line, everything else starts
    options: --timeout N (seconds to wait for "Hytale Server Booted!", default 240), --linger N (seconds to keep it up after the boot
             so late start-up errors land in the log, default 15), --light (copy the world WITHOUT chunk data - faster, worlds
             regenerate their spawn chunks), --keep (keep the scratch server folder), --xmx 4G (max heap, default 4G)
             --pack-audit-only (just the third-party pack-jar API audit, no server, game may stay open), --skip-pack-audit,
             --allow-pack-api (pack jars with removed Hytale calls do not fail the run)

What it does:
  1. refuses if a HytaleServer java process is running (deploy_set.server_running()).
  2. builds tools/dev/scratch/smoke/run-<stamp>/: a copy of Saves/<deploy_set.WORLD> (config.json, permissions.json, bans.json,
     mods/ data folders, universe/ incl. chunks unless --light; never backup/, logs/, auth.enc), Mods/ = the SET jars (+ --jar
     overrides) + the PACK_THIRD_PARTY mods copied from UserData/Mods (found by their manifest Group:Name), PrefabCache/ = a copy of
     UserData/PrefabCache. The scratch config.json gets exactly what deploy_set --yes would do (SET keys on, older Skyy versions off,
     PACK_THIRD_PARTY on, RETIRED + PACK_DISABLED off) and Backup off.
  3. starts the game's own java + HytaleServer.jar with the launcher's flags minus the client ones: --auth-mode offline,
     --bind 127.0.0.1:<free port>, --assets Assets.zip, --mods <scratch>/Mods, --prefab-cache <scratch>/PrefabCache, --disable-sentry,
     --transport QUICHE; cwd = the scratch world, TEMP/TMP/java.io.tmpdir = scratch, -XX:-UsePerfData.
  4. waits for "Hytale Server Booted!" (or --timeout), lingers, sends "stop" on stdin; kills ONLY its own process if it does not exit.
  5. parses the console log: every SET mod's "[<Mod>] <version> ready" line, "Asset validation failed", "Failed to validate asset"
     records naming Skyy, any SEVERE / ERROR record or Exception mentioning Skyy / com.skyy, plus a short summary of other SEVERE lines.
     SkyyCore era (2026-10-15): a jar whose manifest Dependencies are not in the run (--drop <Mod> takes a mod out on purpose) is
     EXPECTED to be skipped - no ready line, and the log must carry the engine's "Failed to load '<key>' because the dependency
     '<dep>' could not be found!" (that SEVERE is not a fail); a dependency missing WITHOUT --drop is a FAIL. Stable-name jars
     (manifest Name = the mod) are switched on under "Skyy:<Mod>" and every "Skyy:<ver> <Mod>" key of the same mod off (and back).
  6. PACK API AUDIT (2026-10-13, Hytale 0.7.0 removed methods that pack mods still call and only crashed once a player joined): every
     ENABLED third-party pack jar (PACK_THIRD_PARTY, minus PACK_DISABLED) is run through tools/ci/crosscheck.py --jar (method / field
     references vs HytaleServer.jar). A jar with unresolved references fails the run unless --allow-pack-api. Results are cached by jar
     sha1 in tools/dev/scratch/smoke/pack_audit_cache.json.
Exit 0 = PASS, 1 = FAIL, 2 = not run (server running, missing jar, setup error).
The full log goes to tools/dev/scratch/smoke/<stamp>.log; the scratch server folder is deleted (unless --keep). Pack the logs with
python tools/tidy_local.py --yes --scratch smoke.
Never touches the real world, UserData (read only) or the game install (read only).
"""
import argparse, hashlib, json, os, re, shutil, socket, subprocess, sys, threading, time, zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import skyybuild as B
import deploy_set as D

PKG = os.path.join(B.HYTALE, "install", "release", "package")
JAVA = os.path.join(PKG, "jre", "latest", "bin", "java.exe")
GAME = os.path.join(PKG, "game", "latest")
SERVER_JAR = os.path.join(GAME, "Server", "HytaleServer.jar")
ASSETS = os.path.join(GAME, "Assets.zip")
WORLD_SRC = os.path.join(B.USERDATA, "Saves", D.WORLD)
SMOKE = os.path.join(TOOLS, "dev", "scratch", "smoke")
BOOTED = "Hytale Server Booted!"
WORLD_FILES = ("config.json", "permissions.json", "bans.json", "whitelist.json")   # never auth.enc / *.bak / telemetry ids


def lp(p):
    """Windows long-path form (the prefab cache nests deeper than 260 characters)."""
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith("\\\\?\\") else "\\\\?\\" + p


def mod_of(path):
    m = re.match(r"^([A-Za-z]\w*?)-(\d+(?:\.\d+)*)\.jar$", os.path.basename(path))
    if not m:
        raise SystemExit("cannot read <Mod>-<version>.jar from %s" % path)
    return m.group(1), m.group(2)


def read_manifest(path):
    """manifest.json of a mod jar / zip / folder -> dict (or None)."""
    try:
        if os.path.isdir(path):
            p = os.path.join(path, "manifest.json")
            return json.load(open(p, encoding="utf-8-sig")) if os.path.isfile(p) else None
        with zipfile.ZipFile(path) as z:
            if "manifest.json" not in z.namelist():
                return None
            return json.loads(z.read("manifest.json").decode("utf-8-sig"))
    except Exception:
        return None


def key_of(man):
    return "%s:%s" % (man.get("Group", ""), man.get("Name", ""))


def find_pack_mods(keys):
    """{key: path in UserData/Mods} for each wanted manifest key (newest file wins when several match)."""
    want = set(keys)
    found = {}
    for n in os.listdir(B.MODS_DIR):
        p = os.path.join(B.MODS_DIR, n)
        if not (os.path.isdir(p) or n.lower().endswith((".jar", ".zip"))):
            continue
        man = read_manifest(p)
        if not man:
            continue
        k = key_of(man)
        if k in want:
            found.setdefault(k, []).append(p)
    out = {}
    for k, ps in found.items():
        ps.sort(key=os.path.getmtime, reverse=True)
        out[k] = ps
    return out


def free_port():
    # Windows reserves random port ranges (Hyper-V / WinNAT), so OS-picked ephemeral ports can fail a TCP bind;
    # scan a fixed range and take the first port that binds for both UDP (QUIC) and TCP.
    import random
    ports = list(range(25600, 26600))
    random.shuffle(ports)
    for port in ports:
        ok = True
        for kind in (socket.SOCK_DGRAM, socket.SOCK_STREAM):
            s2 = socket.socket(socket.AF_INET, kind)
            try:
                s2.bind(("127.0.0.1", port))
            except OSError:
                ok = False
            finally:
                s2.close()
            if not ok:
                break
        if ok:
            return port
    raise SystemExit("no free port found")


def copy_world(dst, light):
    os.makedirs(dst)
    for f in WORLD_FILES:
        s = os.path.join(WORLD_SRC, f)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(dst, f))
    if os.path.isdir(os.path.join(WORLD_SRC, "mods")):
        shutil.copytree(os.path.join(WORLD_SRC, "mods"), os.path.join(dst, "mods"))
    ign = shutil.ignore_patterns("chunks") if light else None
    if os.path.isdir(os.path.join(WORLD_SRC, "universe")):
        shutil.copytree(os.path.join(WORLD_SRC, "universe"), os.path.join(dst, "universe"), ignore=ign)


def apply_deploy_config(cfg_path, set_keys, off_keys=()):
    """What deploy_set --yes does to the world config (B.enable_in_world / retire_in_world / disable_third_party), on the COPY.
    2026-10-15: a stable key "Skyy:<Mod>" and the versioned "Skyy:<ver> <Mod>" keys are the same mod (B.same_mod_keys); off_keys = mods
    switched off on purpose (--drop: every key of that mod, stable or versioned)."""
    d = json.load(open(cfg_path, encoding="utf-8"))
    mods = d.setdefault("Mods", {})
    for key in set_keys:
        for k in B.same_mod_keys([k for k in mods if k.startswith("Skyy:")], key):
            mods[k] = {"Enabled": False}
        mods[key] = {"Enabled": True}
    for key in off_keys:
        for k in [k for k in mods if B.key_parts(k) == B.key_parts(key)] + [key]:
            mods[k] = {"Enabled": False}
    for key in D.PACK_THIRD_PARTY:
        mods[key] = {"Enabled": True}
    retire = list(D.RETIRED) + (list(getattr(D, "CORE_RETIRES", [])) if any(B.key_parts(k)[1] == "SkyyCore" for k in set_keys) else [])
    for mod in retire:
        for k in list(mods):
            if k == "Skyy:" + mod or (k.startswith("Skyy:") and k.endswith(" " + mod)):
                mods[k] = {"Enabled": False}
    for key in D.PACK_DISABLED:
        if key in mods:
            mods[key] = {"Enabled": False}
    d.setdefault("Backup", {})["Enabled"] = False   # no 30-minute backups of the scratch world
    json.dump(d, open(cfg_path, "w", encoding="utf-8"), indent=2)


# ---------------------------------------------------------------- log parsing
REC = re.compile(r"^\[(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d)\s+(\w+)\]\s+\[([^\]]*)\]\s?(.*)$")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
SKYY = re.compile(r"Skyy|com\.skyy", re.I)


def records(lines):
    """Group log lines into records: (level, logger, first line, full text). Lines without a [date LEVEL] head continue the record."""
    out = []
    for ln in lines:
        m = REC.match(ln)
        if m:
            out.append([m.group(2), m.group(3), ln, ln, m.group(4)])
        elif out:
            out[-1][3] += "\n" + ln
        else:
            out.append(["RAW", "", ln, ln, ln])
    return out


def parse(lines, mods, skipped=None):
    """mods = [(mod, ver)]. skipped = {mod: (its key, [missing dependency keys])} - mods the engine must SKIP (their dependency is
    not in the run on purpose, --drop): no ready line expected, the engine's dependency line required. Returns (fails, info)."""
    fails, notes = [], []
    skipped = skipped or {}
    text = "\n".join(lines)
    recs = records(lines)
    if BOOTED not in text:
        fails.append("the server never printed '%s'" % BOOTED)
    # 1. ready lines
    ready = {}
    for ln in lines:
        m = re.search(r"\[(Skyy\w+)\] (\d+(?:\.\d+)*) ready\b", ln)
        if m:
            ready.setdefault(m.group(1), []).append(m.group(2))
    ok, missing, wrong = [], [], []
    skip_ok = []
    for mod, (key, deps) in sorted(skipped.items()):
        if ready.get(mod):
            fails.append("%s should have been skipped (its dependency %s is not in the run) but printed a ready line" % (mod, ", ".join(deps)))
        for dep in deps:
            want = "Failed to load '%s' because the dependency '%s' could not be found" % (key, dep)
            if want in text:
                skip_ok.append("%s skipped by the engine (dependency %s missing): the line is in the log" % (mod, dep))
            else:
                fails.append("no engine line: %s" % want)
    for mod, ver in mods:
        if mod in skipped:
            continue
        vs = ready.get(mod, [])
        if ver in vs:
            ok.append(mod)
        elif vs:
            wrong.append("%s: expected %s, log says %s" % (mod, ver, ", ".join(sorted(set(vs)))))
        else:
            missing.append("%s %s" % (mod, ver))
    for x in missing:
        fails.append("no ready line: " + x)
    for x in wrong:
        fails.append("ready line with the wrong version: " + x)
    # 2. asset validation
    for r in recs:
        if "Asset validation failed" in r[3]:
            fails.append("asset validation failed: " + r[3][:400])
    third_assets = 0
    for r in recs:
        if "Failed to validate asset" in r[2]:
            if SKYY.search(r[3]):
                fails.append("asset failed to validate (Skyy): " + " | ".join(r[3].splitlines()[:5])[:500])
            else:
                third_assets += 1
    # 3. Skyy SEVERE / ERROR / Exception
    skyy_warn = []
    other_severe = {}
    for lvl, logger, first, full, msg in recs:
        bad_level = lvl in ("SEVERE", "ERROR")
        mentions = bool(SKYY.search(full))
        if "Skipping pack at Skyy_" in first or "Skipping mod Skyy:" in first:
            continue   # world data folders without a manifest / older Skyy versions switched off - expected
        if skipped and "because the dependency" in full and any(("'%s'" % skipped[m][0]) in full for m in skipped):
            continue   # the engine skipping a mod whose dependency was left out on purpose (--drop) - expected, checked above
        if mentions and (bad_level or re.search(r"Exception|Error:|\bat com\.skyy", full)):
            fails.append("%s [%s] %s" % (lvl, logger.strip(), " | ".join(full.splitlines()[:6])[:600]))
        elif mentions and lvl == "WARN":
            skyy_warn.append(first[:300])
        elif bad_level:
            k = "[%s] %s" % (re.sub(r"\s+", " ", logger.strip()), re.sub(r"\d+", "#", msg.strip())[:120])
            other_severe[k] = other_severe.get(k, 0) + 1
    info = {"ok": ok, "skyy_warn": skyy_warn, "other_severe": other_severe, "third_assets": third_assets, "skipped": skip_ok}
    return fails, info


# ---------------------------------------------------------------- pack jar API audit
AUDIT_CACHE = os.path.join(SMOKE, "pack_audit_cache.json")
ACCESS_RX = re.compile(r"^FAIL ACCESS (\S+) (\S+) -> (com\.hypixel\.\S*?): (no such method|no such field|class not found)")   # removed ENGINE API only (com.hypixel.*); MethodHandle.invoke + optional other-mod integrations are ignored


def pack_audit(allow=False):
    """Audit each enabled third-party pack jar with crosscheck --jar. Returns (clean_names, {name: [missing members]}, errors)."""
    pack = find_pack_mods(D.PACK_THIRD_PARTY)
    os.makedirs(SMOKE, exist_ok=True)
    try:
        cache = json.load(open(AUDIT_CACHE, encoding="utf-8"))
    except Exception:
        cache = {}
    clean, bad, errs = [], {}, []
    work = os.path.join(SMOKE, "pack-audit-%d" % os.getpid())
    try:
        for i, (key, ps) in enumerate(sorted(pack.items())):
            if key in D.PACK_DISABLED:
                continue
            p = ps[0]
            if os.path.isdir(p):
                errs.append("%s: a folder, not audited" % key)
                continue
            try:
                sha = hashlib.sha1(open(p, "rb").read()).hexdigest()
            except OSError as e:
                errs.append("%s: cannot read %s (%s)" % (key, os.path.basename(p), e))
                continue
            name = os.path.basename(p)
            res = cache.get(sha)
            if res is None:
                with zipfile.ZipFile(p) as z:
                    has_classes = any(n.endswith(".class") for n in z.namelist())
                if not has_classes:
                    res = {"missing": [], "note": "no classes"}
                else:
                    os.makedirs(work, exist_ok=True)
                    tag = "PackJar%d" % i                       # crosscheck --jar cannot take file names with spaces
                    dst = os.path.join(work, tag + "-1.jar")
                    shutil.copyfile(p, dst)
                    r = subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", dst],
                                       capture_output=True, text=True, errors="replace", cwd=ROOT,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                    out = r.stdout.splitlines()
                    if not any(l.startswith(("READY", "NOT READY")) for l in out):
                        errs.append("%s: crosscheck gave no verdict (%s)" % (name, (r.stderr or r.stdout)[-200:].strip()))
                        continue
                    miss = []
                    for l in out:
                        m = ACCESS_RX.match(l.strip())
                        if m and m.group(1) == tag:
                            miss.append("%s: %s" % (m.group(4), m.group(3)))
                    res = {"missing": sorted(set(miss))}
                cache[sha] = res
            if res["missing"]:
                bad[name] = res["missing"]
            else:
                clean.append(name)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        try:
            json.dump(cache, open(AUDIT_CACHE, "w", encoding="utf-8"), indent=1)
        except OSError:
            pass
    return clean, bad, errs


def print_pack_audit(clean, bad, errs):
    print("PACK API AUDIT (0.7): %d jar(s) clean, %d with removed calls%s" % (len(clean), len(bad), ":" if bad else ""))
    for name, miss in sorted(bad.items()):
        print("  %s: %d missing  e.g. %s" % (name, len(miss), " | ".join(miss[:3])))
    for e in errs:
        print("  NOTE " + e)


# ---------------------------------------------------------------- run
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", action="append", default=[])
    ap.add_argument("--drop", action="append", default=[])     # 2026-10-15: take a mod OUT of the run (e.g. --drop SkyyCore)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--linger", type=int, default=15)
    ap.add_argument("--light", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--xmx", default="4G")
    ap.add_argument("--pack-audit-only", action="store_true")
    ap.add_argument("--skip-pack-audit", action="store_true")
    ap.add_argument("--allow-pack-api", action="store_true")
    a = ap.parse_args()
    t0 = time.time()

    if a.pack_audit_only:
        clean, bad, errs = pack_audit()
        print_pack_audit(clean, bad, errs)
        return 1 if bad and not a.allow_pack_api else 0

    if D.server_running():
        print("NOT RUN: a HytaleServer java process is running (game / world open). Close it first.")
        return 2
    import serverjar                                   # cached copies: never run the server on the INSTALLED jar / Assets.zip
    try:
        srv_jar, assets = serverjar.server_jar(), serverjar.assets_zip()
    except SystemExit as e:
        print("NOT RUN: %s" % e)
        return 2
    for p in (JAVA, srv_jar, assets, WORLD_SRC):
        if not os.path.exists(p):
            print("NOT RUN: missing " + p)
            return 2

    # the jars: SET from the project folders, --jar overrides replace their mod (a new mod is added)
    jars = [(m, v, os.path.join(ROOT, m, "%s-%s.jar" % (m, v))) for m, v in D.SET]
    over = {}
    for p in a.jar:
        p = os.path.abspath(p if os.path.exists(p) else os.path.join(ROOT, p))
        if not os.path.isfile(p):
            print("NOT RUN: no such jar: " + p)
            return 2
        m, v = mod_of(p)
        over[m] = (m, v, p)
    jars = [over.pop(m) if m in over else (m, v, j) for m, v, j in jars] + list(over.values())
    jars = [x for x in jars if x[0] not in a.drop]
    jars.sort(key=lambda x: 0 if x[0] == "SkyyCore" else 1)       # SkyyCore first (cosmetic: the plan + the jar copy order)
    missing = [j for _m, _v, j in jars if not os.path.isfile(j)]
    if missing:
        print("NOT RUN: missing jar(s):\n  " + "\n  ".join(missing))
        return 2
    set_keys = []
    mans = {}
    for m, v, j in jars:
        man = read_manifest(j)
        mans[m] = man or {}
        set_keys.append(key_of(man) if man else "Skyy:%s %s" % (v, m))
    # dependencies (SkyyCore era): every manifest dependency must be in the run - unless its mod was --drop'ped (then the dependent is
    # EXPECTED to be skipped by the engine)
    have = dict((key_of(mans[m]), str(mans[m].get("Version", v))) for m, v, _j in jars if mans[m])
    drop_keys = ["Skyy:" + m for m in a.drop]
    skipped, dep_fail = {}, []
    for m, v, _j in jars:
        for dk, rng in ((mans[m] or {}).get("Dependencies") or {}).items():
            if dk in have:
                try:
                    okr = B.range_ok(rng, have[dk])
                except ValueError:
                    okr = False
                if not okr:
                    dep_fail.append("%s needs %s %s, the run has %s" % (m, dk, rng, have[dk]))
            elif dk in drop_keys or B.key_parts(dk)[1] in a.drop:
                skipped.setdefault(m, (key_of(mans[m]), []))[1].append(dk)
            else:
                dep_fail.append("%s needs %s %s - not in SET or --jar (add it, or --drop it to test the missing-dependency boot)" % (m, dk, rng))
    if dep_fail:
        print("NOT RUN: " + "; ".join(dep_fail))
        return 2
    if a.drop:
        print("smoke: dropped on purpose: %s; expected to be skipped by the engine: %s" % (", ".join(a.drop),
              ", ".join("%s (needs %s)" % (m, ", ".join(d)) for m, (_k, d) in sorted(skipped.items())) or "none"))
    pack = find_pack_mods(D.PACK_THIRD_PARTY)
    pack_missing = [k for k in D.PACK_THIRD_PARTY if k not in pack]

    stamp = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(SMOKE, exist_ok=True)
    run = os.path.join(SMOKE, "run-" + stamp)
    world = os.path.join(run, "world")
    tmp = os.path.join(run, "tmp")
    log_path = os.path.join(SMOKE, stamp + ".log")
    proc = None
    code = 2
    lines = []
    try:
        print("smoke: copying the world '%s'%s ..." % (D.WORLD, " (no chunks)" if a.light else ""))
        copy_world(world, a.light)
        os.makedirs(tmp)
        modsdir = os.path.join(run, "Mods")
        os.makedirs(modsdir)
        for m, v, j in jars:
            shutil.copyfile(j, os.path.join(modsdir, m + ".jar"))
        for k, ps in pack.items():
            p = ps[0]
            dst = os.path.join(modsdir, os.path.basename(p))
            (shutil.copytree if os.path.isdir(p) else shutil.copyfile)(p, dst)
        pc_src = os.path.join(B.USERDATA, "PrefabCache")
        pc = os.path.join(run, "PrefabCache")
        if os.path.isdir(pc_src):
            shutil.copytree(lp(pc_src), lp(pc))
        else:
            os.makedirs(pc)
        apply_deploy_config(os.path.join(world, "config.json"), set_keys, off_keys=drop_keys)
        t_copy = time.time() - t0

        port = free_port()
        cmd = [JAVA, "-Xms768M", "-Xmx" + a.xmx, "-XX:-UsePerfData", "-Djava.io.tmpdir=" + tmp,
               "-XX:+IgnoreUnrecognizedVMOptions", "-XX:+UseCompactObjectHeaders", "-XX:+UseShenandoahGC",
               "-XX:ShenandoahGCMode=generational", "-XX:+UnlockExperimentalVMOptions",
               "-jar", srv_jar, "--auth-mode", "offline", "--bind", "127.0.0.1:%d" % port, "--assets", assets,
               "--mods", modsdir, "--prefab-cache", pc, "--disable-sentry", "--transport", "QUICHE"]
        env = dict(os.environ)
        for k in ("TEMP", "TMP", "TMPDIR"):
            env[k] = tmp
        print("smoke: %d SET jars + %d pack mods, port %d; starting the server (cwd %s)" % (len(jars), len(pack), port, world))
        print("  " + subprocess.list2cmdline(cmd))
        t_start = time.time()
        proc = subprocess.Popen(cmd, cwd=world, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        booted = threading.Event()

        def reader():
            for raw in iter(proc.stdout.readline, b""):
                ln = ANSI.sub("", raw.decode("utf-8", "replace")).rstrip("\r\n")
                lines.append(ln)
                if BOOTED in ln:
                    booted.set()
        th = threading.Thread(target=reader, daemon=True)
        th.start()
        while not booted.is_set() and proc.poll() is None and time.time() - t_start < a.timeout:
            booted.wait(1)
        t_boot = time.time() - t_start
        if booted.is_set():
            print("smoke: booted in %.0f s; lingering %d s" % (t_boot, a.linger))
            end = time.time() + a.linger
            while time.time() < end and proc.poll() is None:
                time.sleep(0.5)
        elif proc.poll() is not None:
            print("smoke: the server EXITED during start-up (code %s) after %.0f s" % (proc.returncode, t_boot))
        else:
            print("smoke: TIMEOUT - no '%s' after %d s" % (BOOTED, a.timeout))
        if proc.poll() is None:
            try:
                proc.stdin.write(b"stop\n")
                proc.stdin.flush()
            except Exception:
                pass
            try:
                proc.wait(120)
                print("smoke: server stopped cleanly (code %s)" % proc.returncode)
            except subprocess.TimeoutExpired:
                print("smoke: no exit 120 s after 'stop' - killing the smoke server (pid %d, ours)" % proc.pid)
                proc.kill()
                proc.wait(30)
        th.join(10)
        t_total = time.time() - t0

        open(log_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        mods = [(m, v) for m, v, _j in jars]
        fails, info = parse(lines, mods, skipped)
        if not booted.is_set() and not any("never printed" in f for f in fails):
            fails.insert(0, "no boot")

        print("")
        print("SMOKE TEST %s - %d mods, copy %.0f s, boot %.0f s, total %.0f s" % ("PASS" if not fails else "FAIL", len(mods), t_copy,
                                                                                  t_boot, t_total))
        print("  ready lines: %d of %d%s" % (len(info["ok"]), len(mods) - len(skipped),
                                             (" (+ %d skipped on purpose)" % len(skipped)) if skipped else ""))
        for x in info.get("skipped", []):
            print("  OK   " + x)
        if pack_missing:
            print("  NOTE pack mod(s) not installed in UserData/Mods: " + ", ".join(pack_missing))
        multi = [(k, ps) for k, ps in pack.items() if len(ps) > 1]
        for k, ps in multi:
            print("  NOTE %s: %d files carry this key, used the newest: %s" % (k, len(ps), os.path.basename(ps[0])))
        for f in fails:
            print("  FAIL " + f)
        if info["skyy_warn"]:
            print("  Skyy WARN lines (%d, not a fail):" % len(info["skyy_warn"]))
            for w in info["skyy_warn"][:15]:
                print("    " + w)
            if len(info["skyy_warn"]) > 15:
                print("    ... %d more in the log" % (len(info["skyy_warn"]) - 15))
        # 2026-10-12 (Hytale 0.7.0): name every mod whose ServerVersion range excludes the running game - it still loads, but may break
        # (Skyy: "if mods we use take too long to update to 0.7.0 lets make our own, unless they are hard to build.")
        ver_rx = re.compile(r"Plugin '([^']+)' targets server version range '([^']+)' which does not match the running server version '([^']+)'")
        off = list(dict.fromkeys(m.groups() for m in (ver_rx.search(l) for l in lines) if m))
        if off:
            print("  VERSION %d mod(s) not made for game %s (load anyway; watch them):" % (len(off), off[0][2]))
            for key, rng, _v in off:
                print("    %s  (%s)" % (key, rng))
        if info["third_assets"]:
            print("  third-party 'Failed to validate asset!' records: %d (not ours)" % info["third_assets"])
        if info["other_severe"]:
            n = sum(info["other_severe"].values())
            print("  other SEVERE / ERROR lines (not ours): %d" % n)
            for k, c in sorted(info["other_severe"].items(), key=lambda x: -x[1])[:12]:
                print("    %3dx %s" % (c, k))
        print("  log: " + log_path)
        code = 0 if not fails else 1
        if not a.skip_pack_audit:
            clean, bad, errs = pack_audit()
            print_pack_audit(clean, bad, errs)
            if bad and not a.allow_pack_api:
                print("  FAIL pack jar(s) call Hytale API that no longer exists (--allow-pack-api to accept)")
                code = 1
    except KeyboardInterrupt:
        print("smoke: interrupted")
        code = 2
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()   # only the process this script started
            try:
                proc.wait(30)
            except Exception:
                pass
        if lines and not os.path.isfile(log_path):
            open(log_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        if a.keep:
            print("scratch kept: " + run)
        else:
            shutil.rmtree(lp(run), ignore_errors=True)
            if os.path.exists(run):
                time.sleep(3)
                shutil.rmtree(lp(run), ignore_errors=True)
            if os.path.exists(run):
                print("note: could not delete all of " + run + " (files still open) - delete it by hand")
    return code


if __name__ == "__main__":
    sys.exit(main())
