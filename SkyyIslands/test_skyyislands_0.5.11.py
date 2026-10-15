"""Harness for SkyyIslands 0.5.11 (THE COPPER CAVE GETS A MOUTH; tools/islands_0_5_11_patch.py) on top of the 0.5.10 harness. Build first:
python tools/islands_0_5_11_patch.py && python SkyyIslands/build_skyyislands_0.5.11.py

    python SkyyIslands/test_skyyislands_0.5.11.py --no-server [--dir <folder inside tools/dev/scratch/>] [--keep]

  MOUTH (bare Python on the build's s3_layout(), 0.5.10 for comparison): a player WALKS from the spawn (8,129,8) into the copper tunnel
        (2-high air cells on a solid floor, steps of 1) - 0.5.10: 0 tunnel cells reachable (the sealed cave Skyy saw), 0.5.11: the tunnel is
        reachable; the opening is VISIBLE from the spawn (a clear line from the eye 8.5,130.6,8.5 into the passage) - 0.5.10: blocked; the
        opening is 3 wide x 3 high (x 11-13, y 129-131 at z 12) on a stone floor under a solid roof, stone walls at x 10 / 14, the passage
        meets the tunnel's 2-high part; no gatherable in front; still 8 copper ore on island 1 (the moved one in the passage wall); only
        island 1's mouth area differs from 0.5.10 (every other block identical)
  S3    every 0.5.10 S3 check on the 0.5.11 jar + layout (the jar's data = the build's layout block for block, the design checks, three() /
        places / PlaceFn / config / row, STATIC: FillTask still fills only new islands / resets and skips a world that has its spawn block)
  A / C / AA  verify, class compare 0.5.10 -> 0.5.11 (StarterIsles' data + the version texts only), engine-access audit
  SND, X, D   the 0.5.9 phases on the 0.5.11 jar (D = START TWICE on a scratch COPY of the live Skyy_SkyyIslands, nothing written)
  S     the REAL server phase is NOT RUN in this round (no server start allowed; UNVERIFIED in game) - pass --no-server.
Assets.zip is read from the CACHED copy (tools/serverjar.py). Exit code 1 on any failure.
"""
import os, sys, math, shutil, collections, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import serverjar

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "start033", "islands", "h")]
if "--no-server" not in sys.argv and "--phase" not in sys.argv:
    sys.argv.append("--no-server")
_spec = importlib.util.spec_from_file_location("test_skyyislands_0_5_10", os.path.join(HERE, "test_skyyislands_0.5.10.py"))
T510 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T510)
T59, T58 = T510.T59, T510.T58

VERSION = "0.5.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.10.jar")
SCRATCH = T510.SCRATCH
PKG = T510.PKG
EXPECT = {                         # the layout data + its block count are inlined constants; the version in the config header
    "StarterIsles": ["~m decode", "~m fill"],
    "FillTask": ["~m run"],
    "IslandCfg": ["~m load"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "SkyyIslandsPlugin": ["~m setup"],
}
ADDED = []
T510.JAR = JAR


def layout_of(v):
    os.environ["S3_ONLY"] = "1"
    sp = importlib.util.spec_from_file_location("build_skyyislands_%s_s3" % v.replace(".", "_"), os.path.join(HERE, "build_skyyislands_%s.py" % v))
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
    except ImportError as e:
        assert "S3_ONLY" in str(e), e
    finally:
        del os.environ["S3_ONLY"]
    return m


T510.layout = lambda: layout_of(VERSION)


class _ZipShim(object):
    """T510.design_checks opens the INSTALLED Assets.zip by path; map it to the cached copy (tools/serverjar.py)"""
    import zipfile as _z

    def ZipFile(self, path, *a, **k):
        if str(path).replace("\\", "/").endswith("game/latest/Assets.zip"):
            path = serverjar.assets_zip()
        return self._z.ZipFile(path, *a, **k)


T510.zipfile = _ZipShim()


def walk_and_look(m):
    L = m.S3_L

    def air(x, y, z):
        b = L.get((x, y, z))
        return b is None or b.startswith("Plant_Grass")

    def solid(x, y, z):
        b = L.get((x, y, z))
        return b is not None and not b.startswith("Plant_")
    start = (8, 129, 8)
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y, z = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dy in (0, 1, -1):
                n = (x + dx, y + dy, z + dz)
                if n in seen or not (-25 < n[0] < 45 and -25 < n[2] < 45):
                    continue
                if air(*n) and air(n[0], n[1] + 1, n[2]) and solid(n[0], n[1] - 1, n[2]) and (dy <= 0 or air(x, y + 2, z)):
                    seen.add(n)
                    q.append(n)
    tunnel = sorted((x, y, z) for (x, y, z) in seen if 13 <= x <= 18 and z in (15, 16) and y == 129)      # feet IN the tunnel (not on the hill)
    e, t = (8.5, 130.6, 8.5), (12.5, 130.0, 13.8)
    los = True
    for i in range(1, 400):
        f = i / 400.0
        c = tuple(int(math.floor(e[k] + (t[k] - e[k]) * f)) for k in range(3))
        if not air(*c):
            los = False
            break
    return tunnel, los


def mouth_checks(K, m, old):
    L, isle = m.S3_L, m.S3_ISLE
    tun0, los0 = walk_and_look(old)
    tun1, los1 = walk_and_look(m)
    K.check(not tun0 and not los0, "MOUTH 0.5.10 (what Skyy saw): no tunnel cell reachable on foot from the spawn, no view in (sealed): %d / %s" % (len(tun0), los0))
    K.check(len(tun1) >= 8 and los1, "MOUTH 0.5.11: a player WALKS from the spawn into the copper tunnel (%d tunnel cells reachable) and SEES the opening from the spawn" % len(tun1))
    mx0, mx1, mz0, mz1 = m.S3_MOUTH
    K.eq((mx0, mx1, mz0, mz1), (11, 13, 12, 14), "MOUTH x 11-13, the opening at z 12, the passage to z 14")
    K.check(all((x, y, z) not in L for x in range(11, 14) for y in range(129, 132) for z in range(12, 15)), "MOUTH 3 wide x 3 high, 3 deep: all air")
    K.check(all(L.get((x, 128, z)) == "Rock_Stone" for x in range(11, 14) for z in range(12, 15)), "MOUTH stone floor")
    K.check(all(L.get((x, 132, z)) == "Rock_Stone" and L.get((x, 133, z)) == "Soil_Grass" for x in range(10, 15) for z in range(12, 15)), "MOUTH stone roof + grass cap")
    K.check(all(L.get((x, y, z), "").startswith(("Rock_Stone", "Ore_Copper")) for x in (10, 14) for y in range(129, 132) for z in range(12, 15)), "MOUTH stone side walls")
    K.check((13, 129, 15) not in L and (13, 130, 15) not in L, "MOUTH the passage meets the tunnel's 2-high part (x 13, z 15)")
    gather = ("Plant_Bush", "Plant_Bush_Green", "Wood_Sticks", "Rubble_Stone", "Rubble_Stone_Mossy", "Plant_Grass_Lush_Short")
    K.check(not [k for k, b in L.items() if b in gather and 10 <= k[0] <= 14 and 9 <= k[2] <= 11], "MOUTH no gatherable in front of it")
    cu0 = sorted(k for k, b in old.S3_L.items() if b == "Ore_Copper_Stone" and old.S3_ISLE.get((k[0], k[2])) == "island1")
    cu1 = sorted(k for k, b in L.items() if b == "Ore_Copper_Stone" and isle.get((k[0], k[2])) == "island1")
    K.check(len(cu0) == len(cu1) == 8 and set(cu0) - set(cu1) == {(13, 129, 14)} and set(cu1) - set(cu0) == {(14, 130, 13)},
            "MOUTH still 8 copper ore in the cave (the one the passage cut moved into its wall): %s -> %s" % (sorted(set(cu0) - set(cu1)), sorted(set(cu1) - set(cu0))))
    diff = set(k for k in set(L) | set(old.S3_L) if L.get(k) != old.S3_L.get(k))
    K.check(diff and all(9 <= x <= 14 and 9 <= z <= 14 and 127 <= y <= 133 for x, y, z in diff),
            "MOUTH only the mouth area of island 1 differs from 0.5.10 (%d blocks, x %s-%s z %s-%s): islands 2 + 3, the trees, plot, chest, spawn unchanged"
            % (len(diff), min(k[0] for k in diff), max(k[0] for k in diff), min(k[2] for k in diff), max(k[2] for k in diff)))
    K.eq(m.S3_PLACES, old.S3_PLACES, "MOUTH the named places (island:places) unchanged")


def run_s3m(out, jar, scratch, home):
    K = HK.Child(out)
    m = layout_of(VERSION)
    old = layout_of("0.5.10")
    mouth_checks(K, m, old)
    K.save()
    T510.run_s3(out + ".s3.json", jar, scratch, home)
    import json
    d = json.load(open(out + ".s3.json"))
    e = json.load(open(out))
    e["ok"] += d["ok"]
    e["fails"] += d["fails"]
    e["notes"] += d.get("notes", [])
    json.dump(e, open(out, "w"), indent=1)


if __name__ == "__main__":
    print("S. real-server phase: NOT RUN in this round (no server start allowed) - UNVERIFIED in game")
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("s3", run_s3m), ("snd", T59.run_snd), ("exec", T58.run_exec), ("live", T58.run_live)], script=__file__,
           live=(T58.LIVE_DIR, "Skyy_SkyyIslands"))
