"""SkyWynn load test (research/Load-Test-Plan.md layers A + B): the whole SET on an OFFLINE HytaleServer against a scratch COPY of the test
world, with N synthetic profiles on disk, idle for a while, with the engine's own stats commands sampled on stdin.

Usage (game closed; waits while another HytaleServer java process runs, e.g. an agent's smoke test):
    python tools/load_test.py                          # 50 synthetic profiles, 180 s observation
    python tools/load_test.py --profiles 200 --observe 600
    options: --profiles N (0 = layer A only), --observe S (idle seconds after boot), --sample S (stats every S s, default 30),
             --xmx 4G, --light (copy the world without chunks), --keep (keep the scratch run), --timeout S (boot wait, default 300),
             --wait M (minutes to wait for other servers to exit, default 30; 0 = refuse at once), --bank-interval S (scratch Bank
             intervalSeconds, default 60 so the interest sweep runs inside the window; 0 = leave), --json out.json

Layer A: boot + idle server, RSS of the java process, stats commands (world tps / server stats cpu|memory|gc / entity count / chunk
         storagestats; the exact spelling is probed at the first sample and the raw replies go into the report), 'Task took N ms' WARNs
         (ours flagged when the task or the line names Skyy / com.skyy).
Layer B: gen_profiles() clones every per-player file of the scratch copy that carries a player UUID in its path (a real profile is the best
         template - nothing invents a format): one source UUID's whole file set per synthetic UUID, round robin over the real UUIDs,
         UUID rewritten in names and in text content. Writes ONLY inside the scratch copy. Measures files / bytes per Skyy_* folder before
         and after, boot time, per-mod 'ready' times, and the time 'stop' takes (final saves).
Layer C (in-JVM fake players) is NOT part of this tool (needs loadharness.py; see the plan).

Safety (same rules as tools/smoke_test.py, whose helpers are imported read-only): never touches the real world, UserData (read only) or
the game install; scratch only tools/dev/scratch/load/run-<stamp>/ (only that folder is deleted); TEMP / TMP / java.io.tmpdir = scratch;
-XX:-UsePerfData; cached server jar / Assets.zip (serverjar.py); kills only the pid it started; never touches the game or other servers.
Exit 0 = booted and no com.skyy Task-took over 25 ms, 1 = fail, 2 = not run. (No TPS getter exists: `world tps` only SETS the rate.)
"""
import argparse, json, os, re, shutil, subprocess, sys, threading, time, uuid

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import smoke_test as S          # helpers only (its main() is not run); smoke_test.py itself is not edited
import skyybuild as B
import deploy_set as D

LOAD = os.path.join(TOOLS, "dev", "scratch", "load")
UUID_RX = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
TASK_RX = re.compile(r"Task took (?:(\d+)s )?(?:(\d+)ms )?(?:(\d+)us )?(?:(\d+)ns )?(?:ns)?:?\s*(.*)$")
TEXT_EXT = (".properties", ".json", ".txt", ".log", ".cfg", ".conf", ".yml", ".yaml", ".csv", ".ini", ".bak")
# stats commands sampled every --sample seconds: (label, candidate spellings, first one that answers sensibly is kept)
# {w} = a world name (console world commands need --world <name>; main worlds are read from the '[World|<name>]' log tags)
# NOTE (verified in the 0.7.1 jar): `world tps` / `world tps reset` only SET the tick rate - the engine has no console TPS getter.
# The world-thread probe (reply latency of the world command `entity count`) stands in for it.
STATS = [("cpu", ["server stats cpu"]),
         ("memory", ["server stats memory"]),
         ("gc", ["server stats gc"]),
         ("entities", ["entity count --world {w}", "world entity count --world {w}"])]
ONCE = [("chunkstorage", ["chunk storagestats --world {w}", "world chunk storagestats --world {w}"])]
SKIP_CLONE = ("Skyy_SkyyPets",)   # pet ids live inside the files: clones trip the mod's 'pet in two files' quarantine (not a real load)
WORLD_RX = re.compile(r"\[World\|([^|\]]+)")


def mask(u):
    return u[:8] + "..."


def folder_stats(mods_dir):
    """{Skyy_* folder: (files, bytes)} under the scratch world's mods/."""
    out = {}
    for d in sorted(os.listdir(mods_dir)):
        p = os.path.join(mods_dir, d)
        if d.startswith("Skyy_") and os.path.isdir(p):
            n = b = 0
            for r, _ds, fs in os.walk(p):
                for f in fs:
                    n += 1
                    try:
                        b += os.path.getsize(os.path.join(r, f))
                    except OSError:
                        pass
            out[d] = (n, b)
    return out


def gen_profiles(mods_dir, n):
    """Layer B. Clone the per-player files of the scratch copy for n synthetic UUIDs. Returns (made_profiles, made_files, source_count)."""
    by_uuid = {}                                         # source uuid(lower) -> [(abs path, rel path)]
    for d in sorted(os.listdir(mods_dir)):
        top = os.path.join(mods_dir, d)
        if not (d.startswith("Skyy_") and os.path.isdir(top)) or d in SKIP_CLONE:
            continue
        for r, _ds, fs in os.walk(top):
            for f in fs:
                ab = os.path.join(r, f)
                rel = os.path.relpath(ab, mods_dir)
                us = {u.lower() for u in UUID_RX.findall(rel)}
                if len(us) == 1:                         # a path naming exactly one player
                    by_uuid.setdefault(next(iter(us)), []).append((ab, rel))
    sources = sorted(by_uuid, key=lambda u: -len(by_uuid[u]))
    if not sources:
        return 0, 0, 0
    made = files = 0
    for i in range(n):
        src = sources[i % len(sources)]
        new = str(uuid.uuid4())
        for ab, rel in by_uuid[src]:
            new_rel = re.sub(src, new, rel, flags=re.I)
            dst = os.path.join(mods_dir, new_rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if rel.lower().endswith(TEXT_EXT):
                try:
                    txt = open(ab, "r", encoding="utf-8", newline="").read()
                    open(dst, "w", encoding="utf-8", newline="").write(re.sub(src, new, txt, flags=re.I))
                    files += 1
                    continue
                except (UnicodeError, OSError):
                    pass
            shutil.copyfile(ab, dst)
            files += 1
        made += 1
    return made, files, len(sources)


def set_bank_interval(mods_dir, secs):
    """SCRATCH config only: Bank interest sweep every `secs` so it runs inside the window."""
    p = os.path.join(mods_dir, "Skyy_SkyyBank", "config.properties")
    if not os.path.isfile(p):
        return False
    txt = open(p, encoding="utf-8").read()
    new, c = re.subn(r"(?m)^intervalSeconds=.*$", "intervalSeconds=%d" % secs, txt)
    if not c:
        return False
    open(p, "w", encoding="utf-8").write(new)
    return True


def rss_mb(pid):
    try:
        r = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"], capture_output=True, text=True,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        m = re.findall(r'"([\d.,\s]+) K"\s*$', r.stdout.strip())
        return int(re.sub(r"\D", "", m[-1])) / 1024.0 if m else None
    except Exception:
        return None


def task_ms(m):
    s, ms, us, ns, _rest = m.groups()
    return int(s or 0) * 1000 + int(ms or 0) + int(us or 0) / 1000.0


def wait_for_quiet(minutes):
    """One server at a time: wait (polling) while another HytaleServer java process runs. True when clear."""
    end = time.time() + minutes * 60
    shown = False
    while D.server_running():
        if time.time() >= end:
            return False
        if not shown:
            print("load: another HytaleServer java process runs (smoke test / game) - waiting up to %d min ..." % minutes)
            shown = True
        time.sleep(10)
    if shown:
        time.sleep(5)                                    # settle, then re-check (a second agent may have started in the gap)
        return not D.server_running()
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profiles", type=int, default=50)
    ap.add_argument("--observe", type=int, default=180)
    ap.add_argument("--sample", type=int, default=30)
    ap.add_argument("--xmx", default="4G")
    ap.add_argument("--light", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--wait", type=int, default=30)
    ap.add_argument("--bank-interval", type=int, default=60)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    if not wait_for_quiet(a.wait):
        print("NOT RUN: a HytaleServer java process is running (game / world / another test). Close it first.")
        return 2
    import serverjar
    try:
        srv_jar, assets = serverjar.server_jar(), serverjar.assets_zip()
    except SystemExit as e:
        print("NOT RUN: %s" % e)
        return 2
    for p in (S.JAVA, srv_jar, assets, S.WORLD_SRC):
        if not os.path.exists(p):
            print("NOT RUN: missing " + p)
            return 2
    jars = [(m, v, os.path.join(S.ROOT, m, "%s-%s.jar" % (m, v))) for m, v in D.SET]
    missing = [j for _m, _v, j in jars if not os.path.isfile(j)]
    if missing:
        print("NOT RUN: missing jar(s):\n  " + "\n  ".join(missing))
        return 2
    set_keys = []
    for m, v, j in jars:
        man = S.read_manifest(j)
        set_keys.append(S.key_of(man) if man else "Skyy:%s %s" % (v, m))
    pack = S.find_pack_mods(D.PACK_THIRD_PARTY)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(LOAD, exist_ok=True)
    run = os.path.join(LOAD, "run-" + stamp)
    world, tmp = os.path.join(run, "world"), os.path.join(run, "tmp")
    report_path = os.path.join(LOAD, stamp + ".txt")
    log_path = os.path.join(LOAD, stamp + ".log")
    proc = None
    code = 2
    lines, stamps = [], []
    out = []                                             # report lines

    def say(s=""):
        s = UUID_RX.sub(lambda m: mask(m.group(0)), s)   # real player UUIDs never go into the report
        print(s)
        out.append(s)
    try:
        t0 = time.time()
        print("load: copying the world '%s'%s ..." % (D.WORLD, " (no chunks)" if a.light else ""))
        S.copy_world(world, a.light)
        os.makedirs(tmp)
        modsdir = os.path.join(run, "Mods")
        os.makedirs(modsdir)
        for m, v, j in jars:
            shutil.copyfile(j, os.path.join(modsdir, m + ".jar"))
        for k, ps in pack.items():
            p = ps[0]
            (shutil.copytree if os.path.isdir(p) else shutil.copyfile)(p, os.path.join(modsdir, os.path.basename(p)))
        pc_src = os.path.join(B.USERDATA, "PrefabCache")
        pc = os.path.join(run, "PrefabCache")
        if os.path.isdir(pc_src):
            shutil.copytree(S.lp(pc_src), S.lp(pc))
        else:
            os.makedirs(pc)
        S.apply_deploy_config(os.path.join(world, "config.json"), set_keys)
        wmods = os.path.join(world, "mods")
        before = folder_stats(wmods)
        made = files = srcs = 0
        t_gen = 0.0
        if a.profiles > 0:
            tg = time.time()
            made, files, srcs = gen_profiles(wmods, a.profiles)
            t_gen = time.time() - tg
            print("load: %d synthetic profiles (%d files) from %d real UUIDs in %.1f s" % (made, files, srcs, t_gen))
        bank_set = a.bank_interval > 0 and set_bank_interval(wmods, a.bank_interval)
        after = folder_stats(wmods)

        port = S.free_port()
        cmd = [S.JAVA, "-Xms768M", "-Xmx" + a.xmx, "-XX:-UsePerfData", "-Djava.io.tmpdir=" + tmp,
               "-XX:+IgnoreUnrecognizedVMOptions", "-XX:+UseCompactObjectHeaders", "-XX:+UseShenandoahGC",
               "-XX:ShenandoahGCMode=generational", "-XX:+UnlockExperimentalVMOptions",
               "-jar", srv_jar, "--auth-mode", "offline", "--bind", "127.0.0.1:%d" % port, "--assets", assets,
               "--mods", modsdir, "--prefab-cache", pc, "--disable-sentry", "--transport", "QUICHE"]
        env = dict(os.environ)
        for k in ("TEMP", "TMP", "TMPDIR"):
            env[k] = tmp
        print("load: starting the server, port %d (cwd %s)" % (port, world))
        t_start = time.time()
        proc = subprocess.Popen(cmd, cwd=world, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        booted = threading.Event()
        lock = threading.Lock()

        def reader():
            for raw in iter(proc.stdout.readline, b""):
                ln = S.ANSI.sub("", raw.decode("utf-8", "replace")).rstrip("\r\n")
                with lock:
                    lines.append(ln)
                    stamps.append(time.time() - t_start)
                if S.BOOTED in ln:
                    booted.set()
        th = threading.Thread(target=reader, daemon=True)
        th.start()
        while not booted.is_set() and proc.poll() is None and time.time() - t_start < a.timeout:
            booted.wait(1)
        t_boot = time.time() - t_start
        series = {k: [] for k, _ in STATS}               # label -> [(t, text)]
        rss = []
        chosen = {}
        once = {}

        probe = []                                       # (el, ms) reply latency of `entity count` = world-thread queue delay

        def ask(c, wait=3.0):
            """Send one console command, return the lines that arrived in the next `wait` seconds (first reply latency in ask.lat)."""
            with lock:
                i = len(lines)
            ask.lat = None
            t = time.time()
            try:
                proc.stdin.write((c + "\n").encode())
                proc.stdin.flush()
            except Exception:
                return []
            while time.time() - t < wait:
                time.sleep(0.02)
                with lock:
                    if any(l.strip() and "Console executed command" not in l for l in lines[i:]):
                        ask.lat = (time.time() - t) * 1000.0
                        break
            time.sleep(0.6)                              # let a multi-line reply finish
            with lock:
                return [l for l in lines[i:] if l.strip()]

        def useful(reply):
            txt = " ".join(reply).lower()
            return bool(reply) and not re.search(r"unknown command|not found|no such|invalid|must be a player|missing required|failed to", txt)

        def worlds():
            with lock:
                seen = [m.group(1) for m in (WORLD_RX.search(l) for l in lines) if m]
            ws = [w for w in dict.fromkeys(seen) if not w.startswith("skyy-island-")]
            return ws[:1] or ["default"]

        if booted.is_set():
            print("load: booted in %.0f s; observing %d s (sample every %d s)" % (t_boot, a.observe, a.sample))
            t_obs = time.time()
            nxt = 0.0
            while time.time() - t_obs < a.observe and proc.poll() is None:
                el = time.time() - t_obs
                if el >= nxt:
                    nxt += a.sample
                    r = rss_mb(proc.pid)
                    if r:
                        rss.append((el, r))
                    for label, cands in STATS:
                        w = worlds()[0]
                        todo = [chosen[label]] if label in chosen else [c.replace("{w}", w) for c in cands]
                        for c in todo:
                            rep = ask(c)
                            if label == "entities" and ask.lat is not None and useful(rep):
                                probe.append((el, ask.lat))
                            if useful(rep):
                                chosen[label] = c
                                series[label].append((el, " | ".join(rep)[:400]))
                                break
                        else:
                            series[label].append((el, "(no usable reply to: %s)" % " / ".join(todo)))
                    if not once:
                        for label, cands in ONCE:
                            for c in [c.replace("{w}", worlds()[0]) for c in cands]:
                                rep = ask(c)
                                if useful(rep):
                                    once[label] = (c, " | ".join(rep)[:600])
                                    break
                            else:
                                once[label] = ("-", "(no usable reply to: %s)" % " / ".join(cands))
                time.sleep(1)
            r = rss_mb(proc.pid)
            if r:
                rss.append((time.time() - t_obs, r))
        elif proc.poll() is not None:
            print("load: the server EXITED during start-up (code %s) after %.0f s" % (proc.returncode, t_boot))
        else:
            print("load: TIMEOUT - no '%s' after %d s" % (S.BOOTED, a.timeout))
        t_stop = None
        if proc.poll() is None:
            ts = time.time()
            try:
                proc.stdin.write(b"stop\n")
                proc.stdin.flush()
            except Exception:
                pass
            try:
                proc.wait(120)
                t_stop = time.time() - ts
            except subprocess.TimeoutExpired:
                print("load: no exit 120 s after 'stop' - killing our server (pid %d)" % proc.pid)
                proc.kill()
                proc.wait(30)
        th.join(10)
        open(log_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")

        # ---------------------------------------------------------- analysis
        fails, info = S.parse(lines, [(m, v) for m, v, _j in jars])
        tasks = []
        for ln, tt in zip(lines, stamps):
            m = TASK_RX.search(ln)
            if m and "Task took" in ln:
                tasks.append((task_ms(m), tt, m.group(5)[:110], bool(S.SKYY.search(ln))))
        ours = [t for t in tasks if t[3]]
        ours_big = [t for t in ours if t[0] > 25]
        ready_t = [tt for ln, tt in zip(lines, stamps) if re.search(r"\[Skyy\w+\] [\d.]+ ready\b", ln)]
        min_tps = None

        say("SKYWYNN LOAD TEST %s  (%s)" % (stamp, time.strftime("%Y-%m-%d %H:%M")))
        say("  settings: profiles=%d observe=%ds sample=%ds xmx=%s%s; %d SET jars + %d pack mods; bank intervalSeconds=%s (scratch)" %
            (a.profiles, a.observe, a.sample, a.xmx, " light" if a.light else "", len(jars), len(pack),
             a.bank_interval if bank_set else "unchanged"))
        say("  boot: %s   (world copy + profile generation before start: %.0f s)" %
            ("%.1f s to '%s'" % (t_boot, S.BOOTED) if booted.is_set() else "NO BOOT", t_start - t0))
        if ready_t:
            say("  mod 'ready' lines: %d of %d, first at %.1f s, last at %.1f s after process start" %
                (len(ready_t), len(jars), min(ready_t), max(ready_t)))
        say("  stop (final saves): %s" % ("%.1f s" % t_stop if t_stop is not None else "n/a"))
        if rss:
            say("  process RSS: boot+0 s %.0f MB -> last %.0f MB (max %.0f MB) over %d samples" %
                (rss[0][1], rss[-1][1], max(r for _t, r in rss), len(rss)))
        say("  engine stats (command spellings that answered: %s)" % (", ".join("%s='%s'" % kv for kv in sorted(chosen.items())) or "none"))
        for label, _c in STATS:
            for el, txt in series[label][:1] + series[label][-1:] if len(series[label]) > 1 else series[label]:
                say("    [%4ds] %-8s %s" % (el, label, txt[:230]))
        for label, (c, txt) in once.items():
            say("    %-8s ('%s') %s" % (label, c, txt[:230]))
        say("  TPS: no console getter in 0.7.1 (world tps only sets the rate). World-thread probe, reply latency of 'entity count': %s" %
            (", ".join("%.0f ms" % ms for _e, ms in probe) or "n/a"))
        say("  'Task took' WARNs: %d total, %d naming Skyy / com.skyy, %d of ours over 25 ms%s" %
            (len(tasks), len(ours), len(ours_big), "" if tasks else " (none)"))
        for ms, tt, what, _o in sorted(tasks, key=lambda x: -x[0])[:8]:
            say("    %7.1f ms at %5.1f s  %s" % (ms, tt, what))
        if a.profiles > 0:
            say("  synthetic data: %d profiles, %d files, from %d real UUIDs (copies; UUIDs rewritten), generated in %.1f s" %
                (made, files, srcs, t_gen))
            grown = [(d, before.get(d, (0, 0)), after[d]) for d in after if after[d] != before.get(d, (0, 0))]
            tot_b, tot_a = sum(x[1] for x in before.values()), sum(x[1] for x in after.values())
            say("  Skyy_* data volume: %d KB -> %d KB; files %d -> %d" %
                (tot_b // 1024, tot_a // 1024, sum(x[0] for x in before.values()), sum(x[0] for x in after.values())))
            for d, (n0, b0), (n1, b1) in sorted(grown, key=lambda x: -(x[2][1] - x[1][1]))[:12]:
                say("    %-28s files %4d -> %5d   bytes %8d -> %9d" % (d, n0, n1, b0, b1))
        for f in fails:
            say("  FAIL(smoke-style) " + f[:300])
        for w in info["skyy_warn"][:10]:
            say("  Skyy WARN: " + w[:240])
        ok = booted.is_set() and not ours_big
        say("  RESULT: %s%s" % ("PASS" if ok else "FAIL", "" if not fails else "  (smoke-style problems above: %d)" % len(fails)))
        say("  log: " + log_path)
        open(report_path, "w", encoding="utf-8").write("\n".join(out) + "\n")
        if a.json:
            json.dump({"stamp": stamp, "profiles": made, "boot_s": t_boot, "stop_s": t_stop, "rss": rss, "series": series,
                       "tasks": tasks, "ours_over_25ms": len(ours_big), "probe_ms": probe, "pass": ok},
                      open(a.json, "w", encoding="utf-8"), indent=1)
        code = 0 if ok else 1
    except KeyboardInterrupt:
        print("load: interrupted")
        code = 2
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()                                  # only the process this script started
            try:
                proc.wait(30)
            except Exception:
                pass
        if args_keep(a):
            print("scratch kept: " + run)
        else:
            shutil.rmtree(S.lp(run), ignore_errors=True)
            if os.path.exists(run):
                time.sleep(3)
                shutil.rmtree(S.lp(run), ignore_errors=True)
            if os.path.exists(run):
                print("note: could not delete all of " + run + " (files still open) - delete it by hand")
    return code


def args_keep(a):
    return a.keep


if __name__ == "__main__":
    sys.exit(main())
