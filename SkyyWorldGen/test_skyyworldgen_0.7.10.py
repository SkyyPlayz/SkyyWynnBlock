"""Harness for SkyyWorldGen 0.7.10 (round wg0710: /zone <n> reset + undo; tools/worldgen_0_7_10_patch.py, research/Zone-Reset-Spec.md 10).
Build first:  python tools/worldgen_0_7_10_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.10.py
              python SkyZones/... (SkyyZones 0.2.1 + SkyyExploration 0.3.4 jars for the server phase)
    python SkyyWorldGen/test_skyyworldgen_0.7.10.py [--keep] [--no-smoke]

Phases (fresh child JVMs, tools/harness_kit.py; scratch tools/dev/scratch/wg0710/h):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.9 -> 0.7.10: the planned members only (+ the 7 reset classes + 4 commands)
  F    files    (bare JVM, a scratch COPY of NewBetaTest's skywynn_zones2 chunks + the island layout file - the live world only READ):
               H2 ownerOf on the REAL layout: the stored chunks per zone (spec: 7001 / 49 / 196 / 147 / 49), every chunk owned once, chunks on
                  the line between two zones; the offline store lists the same 7442 chunks the live saver listed (probe P2)
               H4 the reset's file steps (path b = the crash recovery's code): backupChunks of Zone 1 -> the backup's sha1s read back, then
                  Zone 1's index entries removed: every other chunk's blob byte-identical, Zone 1's gone; dropUnchanged (recovery) never
                  touches a chunk made since
               H5 writeBack: every region file's chunk set + every blob byte-identical to the original (blobs compared, not file bytes)
               H6 resetKeep: four backups -> three kept, the gen files no backup needs removed; seeds file save / load round trip (gen,
                  seed, next, history), mix never 0 / the world seed; combine with no gens = the base entries; layoutFor
               T  the 3.4-B tidy on scratch copies: BetterMap fog cells of Zone 1 dropped (cave files untouched) + recorded, the JSON
                  markers / spawn suppression / an array file (StructureV2 style) of Zone 1 dropped, others kept, the undo puts them back
               R  the crash recovery: a journal at step "gen" finishes the drop from the backup; at step "tied" it rolls back (aborted)
  L    live     START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen: WgCfg.load, WgStore.read, WgZSeed.load, WgRZ.boot - no file
               changed (no seeds file = every zone gen 0 = 0.7.9)
  S    server   (game closed only; tools/smoke_test.py, offline, a scratch COPY of NewBetaTest; a test probe plugin): H1 sample chunks of
               all 5 zones before / after a Zone 1 reset (2-5 byte-identical, 1 different), H3 a pick for every zone, H8 the LIVE path from
               the CONSOLE (/zone 1 reset, /zone 1 reset confirm): Zone 1's stored chunks gone or regenerated, every other chunk byte-
               identical, the backup's sha1s = the chunks before, seeds gen 1, the landing moved + on ground; the undo (/zone 1 reset undo
               confirm) puts every Zone 1 chunk back byte-identical + the landing; a second reset uses a NEW seed (gen 2); a confirm without
               a plan is refused; then H7 the kept world's start-up code (boot) twice: the tidy runs once
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, time, zipfile, shutil, hashlib, json, struct, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION = "0.7.10"
OLD_VERSION = "0.7.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wg0710", "h")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
SAVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest")
LIVE_WG = os.path.join(SAVE, "mods", "Skyy_SkyyWorldGen")
ZW = "skywynn_zones2"
WSEED = 20261014
ADDED = ["WgZSeed", "WgRZ", "WgRStore", "WgRTask", "WgROwner", "WgRJob", "WgRArrive", "ZoneReset2Cmd", "ZoneReset3Cmd", "ZoneReset4Cmd", "ZoneResetsCmd"]
EXPECT = {
    "WgZ2Layout": ["+f gsig", "+f obox", "+f zgen", "+f zs"],
    "WgZ2Isles": ["+f RESET_AREA", "+f RESET_TRIES", "+m boxGap", "+m boxesOf", "+m combine", "+m copyEntry", "+m ownerOf", "+m ownerOfBoxes",
                  "+m pickOne", "+m pickZone", "+m seedAt", "+m seedOfEntry", "+m zoneText", "~m isletsHere", "~m placeAt"],
    "WgZ2Gen": ["+f base", "+m layoutNow0", "+m regen", "+m withGens", "~m generateWith", "~m landingOf", "~m layoutNow"],
    "WgZ2Pre": ["~m run"], "WgOpen": ["~m goZone2"], "WgSpawnHome": ["~m send", "~m zone1"], "WgZoneArrive": ["~m run"],
    "WgWeather": ["~m tick"], "WgCfg": ["+f RESET_KEEP", "+f RESET_MAP", "+f RESET_SLOT", "~<clinit>", "~m apply", "~m load", "~m reloadAll"],
    "WgCmds": ["~m listLines"], "WgHooks": ["+m resetList"], "ZoneCmd": ["~c "],
    "SkyyWorldGenPlugin": ["~m setup", "~m start"], "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "WgStore": ["~m markCreated"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            ok = "manifest.json" in got and all(n in ("manifest.json", LANG) or n.endswith("/instance.bson") for n in got)
            if ok and LANG in got:
                a = zipfile.ZipFile(OLD_JAR).read(LANG).decode("utf8").splitlines()
                b = zipfile.ZipFile(HK.arg("--jar", JAR)).read(LANG).decode("utf8").splitlines()
                ok = len(a) == len(b) and [i for i in range(len(a)) if a[i] != b[i]] == [0] and a[0].replace(OLD_VERSION, VERSION) == b[0]
            return self.check(ok, "C: non-class entries changed = manifest.json + instance templates + server.lang header (version text only): %s" % sorted(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def sha(b):
    return hashlib.sha1(bytes(b)).hexdigest()


# ------------------------------------------------------------------------------------------- F: the file steps on a scratch copy
def run_files(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass, JArray, JLong, JInt, JString
    J = lambda n: JClass(PKG + n)
    Isl, Lay, Sd, RZ, St, Cfg = J("WgZ2Isles"), J("WgZ2Layout"), J("WgZSeed"), J("WgRZ"), J("WgRStore"), J("WgCfg")
    Paths, CU, Props = JClass("java.nio.file.Paths"), JClass("com.hypixel.hytale.math.util.ChunkUtil"), JClass("java.util.Properties")
    P = lambda *a: Paths.get(os.path.join(*a))
    save = os.path.join(scratch, "fsave")
    mods = os.path.join(save, "mods")
    wg = os.path.join(mods, "Skyy_SkyyWorldGen")
    wdir = os.path.join(save, "universe", "worlds", ZW)
    os.makedirs(wg)
    lay = "zone2_layout_%d.bin" % WSEED
    shutil.copyfile(os.path.join(LIVE_WG, lay), os.path.join(wg, lay))
    shutil.copytree(os.path.join(SAVE, "universe", "worlds", ZW, "chunks"), os.path.join(wdir, "chunks"))
    shutil.copytree(os.path.join(SAVE, "universe", "worlds", ZW, "resources"), os.path.join(wdir, "resources"))
    bm_src = os.path.join(SAVE, "mods", "BetterMap", "Data", ZW)
    if os.path.isdir(bm_src):
        shutil.copytree(bm_src, os.path.join(mods, "BetterMap", "Data", ZW))
    Isl.LAYDIR = P(wg)
    RZ.MODS = P(mods)
    Sd.load(WSEED)
    K.eq(str(Sd.sig()), "0,0,0,0,0", "seeds: no file = every zone gen 0")
    L = Isl.loadLayout(P(wg, lay), WSEED)
    K.check(L is not None and int(L.n) >= 5, "the real island layout file reads (%s)" % (None if L is None else int(L.n)))
    st = St(None, None, P(wdir, "chunks"))
    allix = [int(x) for x in st.indexes()]
    K.check(len(allix) >= 7442, "H2 the offline store lists the stored chunks (probe P2: 7442 on 2026-10-23 16:00, more as Skyy plays): %d" % len(allix))
    own = {}
    for ix in allix:
        k = int(Isl.ownerOf(L, CU.xOfChunkIndex(JLong(ix)), CU.zOfChunkIndex(JLong(ix))))
        own.setdefault(k, []).append(ix)
    counts = [len(own.get(k, [])) for k in range(5)]
    K.check(sum(counts) == len(allix) and counts[0] >= 7001 and all(c > 0 for c in counts), "H2 stored chunks per zone by ownerOf (spec section 1/4: 7001 / 49 / 196 / 147 / 49 then; the live world grows): %s" % counts)
    K.check(-1 not in own, "H2 every stored chunk has an owner")
    # border chunks: half way between the Zone 1 and Zone 5 boxes, and the boxes' own corners
    bx = [int(v) for v in Isl.boxesOf(L)]
    K.check(len(bx) % 5 == 0 and len(bx) >= 25, "H2 land boxes: %d entries" % (len(bx) // 5))
    b1 = [bx[i:i + 5] for i in range(0, len(bx), 5) if bx[i] == 0][0]
    b5 = [bx[i:i + 5] for i in range(0, len(bx), 5) if bx[i] == 4][0]
    K.check(int(Isl.ownerOfBoxes(JArray(JInt)(bx), b1[1] >> 5, b1[2] >> 5)) == 0 and int(Isl.ownerOfBoxes(JArray(JInt)(bx), b5[3] >> 5, b5[4] >> 5)) == 4,
            "H2 a chunk on a zone's own box corner is that zone's")
    mz = ((b1[4] + b5[2]) // 2) >> 5
    mx = ((b1[1] + b1[3]) // 2) >> 5
    o_mid = int(Isl.ownerOfBoxes(JArray(JInt)(bx), mx, mz))
    K.check(o_mid in (0, 4), "H2 a chunk between Zone 1 and Zone 5 belongs to one of them (%d)" % o_mid)
    K.eq(int(Isl.ownerOfBoxes(JArray(JInt)([0, 0, 0, 30, 31, 1, 66, 0, 95, 31]), 1, 0)), 0, "H2 an exact tie goes to the lower zone")
    # ---- H4: backup + drop of Zone 1 (the file path)
    before = {}
    for ix in allix:
        before[ix] = sha(st.read(JLong(ix)))
    z1 = own[0]
    man = Props()
    bd = P(wg, "zone-resets", ZW, "z1-test")
    t0 = time.time()
    r = RZ.backupChunks(st, JArray(JLong)(z1), bd, man)
    K.check(r is None, "H4 backupChunks of Zone 1's %d chunks: %s (%.1f s)" % (len(z1), r, time.time() - t0))
    K.eq(int(man.getProperty("chunks")), len(z1), "H4 the manifest lists every chunk")
    cl = RZ.chunksOf(man)
    shs = dict((int(a), str(b)) for a, b in zip(cl[0], cl[1]))
    K.check(all(shs.get(ix) == before[ix] for ix in z1), "H4 the backup's sha1s = the chunks before")
    bst = St(None, None, bd.resolve("chunks"))
    K.check(all(sha(bst.read(JLong(ix))) == before[ix] for ix in z1[::97]), "H4 the backup copy reads back blob for blob (sample)")
    bst.close()
    man.setProperty("status", "complete")
    man.setProperty("zone", "1")
    man.setProperty("at", "1")
    man.setProperty("oldGen", "0")
    RZ.writeProps(bd.resolve("manifest.properties"), man, "test")
    for ix in z1:
        st.remove(JLong(ix))
    st.close()
    st = St(None, None, P(wdir, "chunks"))
    after = set(int(x) for x in st.indexes())
    K.check(after == set(allix) - set(z1), "H4 only Zone 1's index entries are gone (%d left)" % len(after))
    K.check(all(sha(st.read(JLong(ix))) == before[ix] for ix in after), "H4 every other zone's chunk blob is byte-identical")
    # recovery's dropUnchanged never touches a chunk made since: write one 'new' chunk at a Zone 1 index
    newb = bytes(b"new chunk data") * 10
    st.write(JLong(z1[0]), newb)
    n = int(RZ.dropUnchanged(man, st))
    K.check(n == 0 and sha(st.read(JLong(z1[0]))) == sha(newb), "H4 dropUnchanged leaves a chunk made after the reset (dropped %d)" % n)
    st.remove(JLong(z1[0]))
    # ---- H5: writeBack
    err = JArray(JString)(1)
    w = int(RZ.writeBack(man, bd, st, err))
    K.eq(w, len(z1), "H5 writeBack wrote every Zone 1 chunk back (%s)" % err[0])
    st.close()
    st = St(None, None, P(wdir, "chunks"))
    now = [int(x) for x in st.indexes()]
    K.check(set(now) == set(allix) and len(now) == len(allix), "H5 every region file's chunk set is the original")
    K.check(all(sha(st.read(JLong(ix))) == before[ix] for ix in allix), "H5 every chunk blob is byte-identical to the original")
    # dropUnchanged on the restored set removes exactly Zone 1 (the recovery of a committed reset)
    n = int(RZ.dropUnchanged(man, st))
    K.eq(n, len(z1), "H4 the crash recovery's drop removes exactly the backed-up Zone 1 chunks")
    w = int(RZ.writeBack(man, bd, st, err))
    st.close()
    # ---- H6 seeds + keep
    K.check(all(int(Sd.mix(WSEED, k, g)) not in (0, WSEED) for k in range(5) for g in range(1, 200)), "H6 mix is never 0 / the world seed")
    K.check(len(set(int(Sd.mix(WSEED, k, g)) for k in range(5) for g in range(1, 60))) == 5 * 59, "H6 every (zone, gen) seed differs")
    K.eq(int(Sd.mix(WSEED, 0, 1)), 386661544, "H6 the gen-1 seed of Zone 1 = the one probe P1 tried")
    g = JArray(JInt)([2, 0, 0, 0, 0])
    s = JArray(JInt)([int(Sd.mix(WSEED, 0, 2)), WSEED, WSEED, WSEED, WSEED])
    nx = JArray(JInt)([3, 1, 1, 1, 1])
    K.check(bool(Sd.save(WSEED, g, s, nx, "harness line one")), "H6 the seeds file writes")
    Sd.load(WSEED)
    K.check(str(Sd.sig()) == "2,0,0,0,0" and int(Sd.SEED[0]) == int(Sd.mix(WSEED, 0, 2)) and int(Sd.NEXT[0]) == 3 and int(Sd.SEED[1]) == WSEED,
            "H6 seeds round trip: %s %s %s" % (Sd.sig(), list(Sd.SEED), list(Sd.NEXT)))
    Sd.save(WSEED, Sd.GEN, Sd.SEED, Sd.NEXT, "harness line two")
    txt = open(os.path.join(wg, "zone2_seeds_%d.properties" % WSEED), encoding="latin-1").read()
    K.check(txt.count("# history: ") == 2 and "harness line one" in txt, "H6 the seeds file keeps a history line per change")
    open(os.path.join(wg, "zone2_seeds_%d.properties" % WSEED), "w").write("zone.1.gen=4\nzone.1.seed=%d\n" % WSEED)
    Sd.load(WSEED)
    K.check(int(Sd.GEN[0]) == 0 and "no seed of its own" in str(Sd.ERR), "H6 a gen without its own seed is refused (zone stays gen 0): %s" % Sd.ERR)
    os.remove(os.path.join(wg, "zone2_seeds_%d.properties" % WSEED))
    Sd.load(WSEED)
    C = Isl.combine(L, JArray(Lay)(5), JArray(JInt)([WSEED] * 5), JArray(JInt)(5))
    same = int(C.n) == int(L.n) and all(float(C.cx[i]) == float(L.cx[i]) and int(C.zone[i]) == int(L.zone[i]) and int(C.area[i]) == int(L.area[i]) for i in range(int(L.n)))
    K.check(same and str(C.gsig) == "0,0,0,0,0" and all(int(x) == WSEED for x in C.zs), "H6 combine with no zone layouts = the base entries in the base order")
    # a fake gen-2 layout for Zone 1 (zone 1's own entries) -> combine puts it in place, other zones untouched
    Z = Lay(5 + 2)
    Z.nMain = 5
    Isl.copyEntry(L, 0, Z, 0)
    Z.cx[0] = float(L.cx[0]) + 100.0
    for i in range(int(L.nMain), int(L.n)):
        if int(L.zone[i]) == 0:
            Isl.copyEntry(L, i, Z, 5)
            break
    Z.zone[6] = 0
    zarr = JArray(Lay)(5)
    zarr[0] = Z
    C2 = Isl.combine(L, zarr, JArray(JInt)([777, WSEED, WSEED, WSEED, WSEED]), JArray(JInt)([2, 0, 0, 0, 0]))
    others = [i for i in range(int(L.n)) if int(L.zone[i]) != 0 and i >= 5]
    c2o = [i for i in range(int(C2.n)) if int(C2.zone[i]) != 0 and i >= 5]
    K.check(float(C2.cx[0]) == float(L.cx[0]) + 100.0 and int(C2.zs[0]) == 777 and str(C2.gsig) == "2,0,0,0,0" and len(c2o) == len(others)
            and all(float(C2.cx[a]) == float(L.cx[b]) for a, b in zip(c2o, others)) and all(float(C2.cx[k]) == float(L.cx[k]) for k in range(1, 5)),
            "H6 combine swaps in Zone 1's own layout, Zones 2-5 + their islets unchanged")
    cx2, cz2 = CU.xOfChunkIndex(JLong(own[2][0])), CU.zOfChunkIndex(JLong(own[2][0]))
    K.check(int(Isl.seedAt(C2, cx2, cz2, WSEED)) == WSEED and int(Isl.seedAt(C2, CU.xOfChunkIndex(JLong(z1[5])), CU.zOfChunkIndex(JLong(z1[5])), WSEED)) == 777
            and int(Isl.seedAt(L, CU.xOfChunkIndex(JLong(z1[5])), CU.zOfChunkIndex(JLong(z1[5])), WSEED)) == WSEED,
            "H1 seedAt: Zone 1's chunk -> its own seed, Zone 3's -> the world seed, a gen-0 layout -> always the world seed")
    # keepTrim: 4 complete backups of Zone 1 (oldGen 0, 1, 2, 3) + gen files 1-4 and a stray 7, current gen 4 -> the 3 newest kept (oldGen
    # 1-3), gen files 1-4 needed (kept backups + the current one), 7 deleted
    rz = os.path.join(wg, "zone-resets", ZW)
    shutil.rmtree(rz)
    for i in range(4):
        d = os.path.join(rz, "z1-2026102%d-000000" % i)
        os.makedirs(d)
        open(os.path.join(d, "manifest.properties"), "w").write("zone=1\nstatus=complete\nat=%d\noldGen=%d\nnewGen=%d\nchunks=0\nstamp=s%d\n" % (1000 + i, i, i + 1, i))
    for gg in (1, 2, 3, 4, 7):
        open(os.path.join(wg, "zone2_layout_%d_z1_g%d.bin" % (WSEED, gg)), "wb").write(b"x")
    open(os.path.join(wg, "zone2_layout_%d_z2_g1.bin" % WSEED), "wb").write(b"x")
    Sd.save(WSEED, JArray(JInt)([4, 0, 0, 0, 0]), JArray(JInt)([int(Sd.mix(WSEED, 0, 4)), WSEED, WSEED, WSEED, WSEED]), JArray(JInt)([5, 1, 1, 1, 1]), "keep test")
    Cfg.RESET_KEEP = 3
    t = str(RZ.keepTrim(0))
    left = sorted(os.listdir(rz))
    gens = sorted(n for n in os.listdir(wg) if n.startswith("zone2_layout_%d_z" % WSEED))
    K.check(left == ["z1-20261021-000000", "z1-20261022-000000", "z1-20261023-000000"], "H6 resetKeep 3: the oldest of four backups deleted: %s (%s)" % (left, t))
    K.check(gens == ["zone2_layout_%d_z1_g%d.bin" % (WSEED, gg) for gg in (1, 2, 3, 4)] + ["zone2_layout_%d_z2_g1.bin" % WSEED],
            "H6 the gen files no kept backup / the current gen needs are deleted (other zones untouched): %s" % gens)
    K.check("3 of 3 backups kept" in t and "1 old one(s) deleted" in t and "1 unused island file(s) deleted" in t, "H6 the keep text: %s" % t)
    lines = [str(x) for x in RZ.listLines()]
    K.check(len(lines) == 7 and "Zone 1 (reset 4)" in lines[1] and lines[1].count("before reset") == 3, "H6 /zone resets lists them newest first: %s" % lines[1][:200])
    K.check(RZ.backups(0).size() == 3 and RZ.backups(1).size() == 0, "H6 backups() per zone")
    K.check(not bool(RZ.deleteTree(P(wg))) and os.path.isdir(wg), "H6 deleteTree refuses anything outside zone-resets/")
    shutil.rmtree(rz)
    for n in os.listdir(wg):
        if n.startswith("zone2_layout_%d_z" % WSEED) or n.startswith("zone2_seeds_"):
            os.remove(os.path.join(wg, n))
    Sd.load(WSEED)
    # ---- T: the 3.4-B tidy on the copies
    res = os.path.join(wdir, "resources")
    open(os.path.join(wdir, "structurev2-spawns.json"), "w").write(json.dumps({"version": 2, "spawns": [
        {"id": "a", "x": -900, "z": 700}, {"id": "b", "x": 1280, "z": 4800}, {"id": "c", "anchorX": -700.0, "anchorZ": 500.0}],
        "bossIslandArenaBounds": [{"minX": -1000, "maxX": -900, "minZ": 600, "maxZ": 700}, {"minX": 3600, "maxX": 3800, "minZ": -2600, "maxZ": -2500}]}))
    files0 = {}
    for r, _d, fs in os.walk(save):
        for f in fs:
            files0[os.path.relpath(os.path.join(r, f), save)] = open(os.path.join(r, f), "rb").read()
    bm = os.path.join(mods, "BetterMap", "Data", ZW)
    cells0 = {}
    for n in (os.listdir(bm) if os.path.isdir(bm) else []):
        b = open(os.path.join(bm, n), "rb").read()
        v, c = struct.unpack(">ii", b[:8])
        cells0[n] = [struct.unpack(">q", b[8 + i * 8:16 + i * 8])[0] for i in range(c)]
    bdx = os.path.join(wg, "zone-resets", ZW, "z1-tidy")
    os.makedirs(bdx)
    Cfg.RESET_MAP = True
    t = str(RZ.tidyZone(L, 0, "reset", P(bdx)))
    K.check("entries of the old land dropped" in t, "T tidy: %s" % t)
    mk = json.load(open(os.path.join(res, "BlockMapMarkers.json")))
    K.check("-928,112,710" not in mk.get("Markers", {}), "T the Forgotten Temple marker on Zone 1 is dropped")
    sp = json.load(open(os.path.join(res, "SpawnSuppressionController.json")))
    K.check(len(sp.get("SpawnSuppressorMap", {})) == 0, "T the Spawn_Camp suppression on Zone 1 is dropped")
    sv = json.load(open(os.path.join(wdir, "structurev2-spawns.json")))
    K.check([e["id"] for e in sv["spawns"]] == ["b"] and len(sv["bossIslandArenaBounds"]) == 1 and sv["version"] == 2,
            "T StructureV2-style arrays: Zone 1 entries (x / z, anchorX / anchorZ, min..max bounds) dropped, Zone 3 / 4 kept: %s" % sv)
    for n, cs in cells0.items():
        b = open(os.path.join(bm, n), "rb").read()
        c = struct.unpack(">i", b[4:8])[0]
        now = [struct.unpack(">q", b[8 + i * 8:16 + i * 8])[0] for i in range(c)]
        if n.startswith("cave-"):
            K.check(now == cs, "T BetterMap cave overlay %s untouched" % n)
        else:
            z1c = [v for v in cs if int(Isl.ownerOf(L, (v >> 32) >> 1, ((v & 0xffffffff) - (1 << 32) if v & 0x80000000 else v & 0xffffffff) >> 1)) == 0]
            K.check(len(now) == len(cs) - len(z1c) and len(z1c) > 0, "T BetterMap fog %s: %d of %d cells on Zone 1 dropped" % (n, len(z1c), len(cs)))
    rec = sorted(os.listdir(os.path.join(bdx, "tied", "B-dropped")))
    K.check("BlockMapMarkers.json" in rec and "structurev2-spawns.json" in rec and any(r.startswith("bettermap-") for r in rec), "T every drop is recorded: %s" % rec)
    # the undo's tidy: drop zone 1 again (nothing left) + put the recorded entries back
    shutil.copytree(os.path.join(bdx, "tied", "B-dropped"), os.path.join(bdx, "tied", "B-restore"))
    shutil.rmtree(os.path.join(bdx, "tied", "B-dropped"))
    t = str(RZ.tidyZone(L, 0, "undo", P(bdx)))
    mk = json.load(open(os.path.join(res, "BlockMapMarkers.json")))
    sv = json.load(open(os.path.join(wdir, "structurev2-spawns.json")))
    K.check("-928,112,710" in mk["Markers"] and sorted(e["id"] for e in sv["spawns"]) == ["a", "b", "c"] and len(sv["bossIslandArenaBounds"]) == 2,
            "T undo: the recorded entries are back (%s)" % t)
    for n, cs in cells0.items():
        b = open(os.path.join(bm, n), "rb").read()
        c = struct.unpack(">i", b[4:8])[0]
        now = [struct.unpack(">q", b[8 + i * 8:16 + i * 8])[0] for i in range(c)]
        K.check(sorted(now) == sorted(cs), "T undo: BetterMap %s cells back (%d)" % (n, len(now)))
    Cfg.RESET_MAP = False
    t = str(RZ.tidyZone(L, 0, "reset", None))
    K.check("BetterMap fog kept" in t, "T zones.resetMap off keeps the fog: %s" % t)
    # ---- R: the crash recovery (+ the tidy queue it leaves)
    shutil.rmtree(os.path.join(wg, "zone-resets"))
    bdr = os.path.join(wg, "zone-resets", ZW, "z1-rec")
    os.makedirs(bdr)
    st = St(None, None, P(wdir, "chunks"))
    man = Props()
    RZ.backupChunks(st, JArray(JLong)(z1), P(bdr), man)
    for kk, vv in (("zone", "1"), ("status", "writing"), ("at", "5"), ("oldGen", "0"), ("newLanding", "")):
        man.setProperty(kk, vv)
    RZ.writeProps(P(bdr, "manifest.properties"), man, "t")
    st.close()
    RZ.journal("reset", 0, "tied", "z1-rec", None)
    s1 = str(RZ.recovery())
    m1 = open(os.path.join(bdr, "manifest.properties")).read()
    K.check("before the world changed" in s1 and "status=aborted" in m1 and not os.path.exists(os.path.join(wg, "zone-resets", "inprogress.properties")),
            "R a stop at 'tied' rolls back: aborted, nothing removed (%s)" % s1[:160])
    st = St(None, None, P(wdir, "chunks"))
    K.check(set(int(x) for x in st.indexes()) == set(allix), "R ... every chunk still stored")
    st.close()
    man.setProperty("status", "writing")
    RZ.writeProps(P(bdr, "manifest.properties"), man, "t")
    RZ.journal("reset", 0, "gen", "z1-rec", None)
    s2 = str(RZ.recovery())
    st = St(None, None, P(wdir, "chunks"))
    left = set(int(x) for x in st.indexes())
    st.close()
    K.check(left == set(allix) - set(z1) and "finished now: %d old chunk(s)" % len(z1) in s2, "R a stop after the new seed was written: the next start drops Zone 1's old chunks (%s)" % s2[:160])
    K.check("status=complete" in open(os.path.join(bdr, "manifest.properties")).read() and os.path.isfile(os.path.join(wg, "zone-resets", "tidy.properties")),
            "R ... the backup is complete and the tidy is queued")
    s3 = str(RZ.tidyRun())
    K.check("zone 1 (reset)" in s3 and not os.path.exists(os.path.join(wg, "zone-resets", "tidy.properties")), "R the queued tidy runs once: %s" % s3[:200])
    K.eq(str(RZ.tidyRun()), "no tidy queued", "R ... and not again")
    # ---- fix round checks (critic findings, each EXECUTED here)
    # FR1 (critic: crash between "seeds written" and the next journal step) - the "commit" step: put Zone 1 back first
    st = St(None, None, P(wdir, "chunks"))
    RZ.writeBack(man, P(bdr), st, err)
    st.close()
    man.setProperty("newGen", "1")
    man.setProperty("status", "writing")
    RZ.writeProps(P(bdr, "manifest.properties"), man, "t")
    RZ.journal("reset", 0, "commit", "z1-rec", None)
    s4 = str(RZ.recovery())
    st = St(None, None, P(wdir, "chunks"))
    left = set(int(x) for x in st.indexes())
    st.close()
    K.check("before the world changed" in s4 and left == set(allix) and "status=aborted" in open(os.path.join(bdr, "manifest.properties")).read(),
            "FR1 a stop at 'commit' with the seeds file NOT yet on the new gen rolls back (%s)" % s4[:140])
    Sd.save(WSEED, JArray(JInt)([1, 0, 0, 0, 0]), JArray(JInt)([int(Sd.mix(WSEED, 0, 1)), WSEED, WSEED, WSEED, WSEED]), JArray(JInt)([2, 1, 1, 1, 1]), "fix round commit test")
    Sd.load(WSEED)
    man.setProperty("status", "writing")
    RZ.writeProps(P(bdr, "manifest.properties"), man, "t")
    RZ.journal("reset", 0, "commit", "z1-rec", None)
    s5 = str(RZ.recovery())
    st = St(None, None, P(wdir, "chunks"))
    left = set(int(x) for x in st.indexes())
    st.close()
    K.check("finished now: %d old chunk(s)" % len(z1) in s5 and left == set(allix) - set(z1) and "status=complete" in open(os.path.join(bdr, "manifest.properties")).read(),
            "FR1 a stop at 'commit' with the seeds file already on the new gen rolls FORWARD (%s)" % s5[:140])
    tq = open(os.path.join(wg, "zone-resets", "tidy.properties"), encoding="latin-1").read()
    K.check("1|reset|z1-rec" in tq, "FR1 ... and queues the reset's tidy")
    # FR2 (critic: undo before a restart deleted the restored land's pack-mod records) + FR1 for an undo: an undo stopped at 'commit'
    # (today's chunks may be part removed) rolls forward at the next start AND cancels the never-run tidy of the reset it undoes
    bdu = os.path.join(wg, "zone-resets", ZW, "z1-u")
    os.makedirs(bdu)
    st = St(None, None, P(wdir, "chunks"))
    mu = Props()
    RZ.backupChunks(st, JArray(JLong)([]), P(bdu), mu)
    st.close()
    for kk, vv in (("zone", "1"), ("kind", "undo"), ("status", "writing"), ("at", "6"), ("oldGen", "1"), ("newGen", "0")):
        mu.setProperty(kk, vv)
    RZ.writeProps(P(bdu, "manifest.properties"), mu, "t")
    RZ.journal("undo", 0, "commit", "z1-u", "z1-rec")
    s6 = str(RZ.recovery())
    st = St(None, None, P(wdir, "chunks"))
    now = set(int(x) for x in st.indexes())
    okb = all(sha(st.read(JLong(ix))) == before[ix] for ix in z1[::50])
    st.close()
    Sd.load(WSEED)
    K.check("undo of Zone 1 was interrupted - finished now" in s6 and now == set(allix) and okb and int(Sd.GEN[0]) == 0 and not os.path.isdir(os.path.join(bdr, "chunks"))
            and "status=restored" in open(os.path.join(bdr, "manifest.properties")).read(),
            "FR1 an undo stopped at 'commit' rolls forward: every Zone 1 chunk back byte-identical, gen 0, the undone backup's chunks removed, marked restored (%s)" % s6[:160])
    K.check("1 finished undo folder(s) removed" in str(RZ.tiedRetry()) and not os.path.isdir(bdr), "FX3 the next start's tiedRetry removes the restored folder")
    K.check(not os.path.exists(os.path.join(wg, "zone-resets", "tidy.properties")),
            "FR2 the undo cancelled the reset's queued tidy (never ran) and queued none of its own - the restored land keeps its records")
    RZ.tidyQueue(0, "reset", "z1-x")
    time.sleep(0.02)
    RZ.tidyQueue(1, "reset", "z2-y")
    K.check(bool(RZ.tidyCancel(0, "z1-x")) and not bool(RZ.tidyCancel(0, "z1-x")) and not bool(RZ.tidyCancel(0, "z2-y"))
            and "2|reset|z2-y" in open(os.path.join(wg, "zone-resets", "tidy.properties"), encoding="latin-1").read(),
            "FR2 tidyCancel removes only that zone's entry for that backup")
    RZ.tidyCancel(1, "z2-y")
    K.check(not os.path.exists(os.path.join(wg, "zone-resets", "tidy.properties")), "FR2 ... the emptied tidy file is removed")
    for n in os.listdir(wg):
        if n.startswith("zone2_seeds_"):
            os.remove(os.path.join(wg, n))
    Sd.load(WSEED)
    # FR3 (critic: a mod's partial drop): an #ERROR line in a tied answer stops the reset; #WARN lines do not
    Tk = J("WgRTask")
    e1 = Tk.tiedError(JArray(JString)(["", "C a 1\nA 1 2 3 x y\n#ERROR the luggage step failed: boom\nK x\n"]))
    e2 = Tk.tiedError(JArray(JString)([None, "C a 1\n#WARN profile p not fully dropped: x\n"]))
    e3 = Tk.tiedError(JArray(JString)(["#ERROR the bridge answered null\n", None]))
    K.check(str(e1) == "SkyyExploration: #ERROR the luggage step failed: boom" and e2 is None and str(e3) == "SkyyZones: #ERROR the bridge answered null",
            "FR3 tiedError: %s | %s | %s" % (e1, e2, e3))
    t5 = Tk(5, None, None, 0)
    K.check(not bool(t5.giveUp()) and bool(t5.finish()), "FR3 a step 5 the job gave up on puts its rows back itself when it ends")
    t5b = Tk(5, None, None, 0)
    K.check(not bool(t5b.finish()) and bool(t5b.giveUp()), "FR3 ... one that ended first leaves the put-back to the job")
    # FR4 (critic: players offline on the reset zone): the saved player files -> the relocation list (not online, world + position)
    pdir = os.path.join(save, "universe", "players")
    os.makedirs(pdir, exist_ok=True)
    def pj(world, x, z):
        return json.dumps({"Components": {"Transform": {"Position": {"X": x, "Y": 37.0, "Z": z}}, "Player": {"PlayerData": {"World": world}}}}, indent=2)
    u1, u2, u3, u4 = ("11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222", "33333333-3333-3333-3333-333333333333",
                      "44444444-4444-4444-4444-444444444444")
    open(os.path.join(pdir, u1 + ".json"), "w").write(pj(ZW, -1251.0, 1045.0))
    open(os.path.join(pdir, u2 + ".json"), "w").write(pj(ZW, 1280.0, 4800.0))
    open(os.path.join(pdir, u3 + ".json"), "w").write(pj("default", -1251.0, 1045.0))
    open(os.path.join(pdir, u4 + ".json"), "w").write("{ not json " + ZW)
    open(os.path.join(pdir, u1 + ".json.bak"), "w").write(pj(ZW, -1251.0, 1045.0))
    K.eq(int(RZ.relocScan(L, None, 0, False)), 1, "FR4 the plan counts the one player offline on Zone 1 (other zone / other world / broken file / .bak skipped)")
    K.check(RZ.RELOC.isEmpty(), "FR4 ... the plan lists nobody")
    K.eq(int(RZ.relocScan(L, None, 0, True)), 1, "FR4 the reset lists that player")
    K.check(str(list(RZ.RELOC.keySet())) == "['%s']" % u1 and os.path.isfile(os.path.join(wg, "zone-resets", "relocate.properties")), "FR4 ... kept in zone-resets/relocate.properties")
    RZ.RELOC.clear()
    K.check(int(RZ.relocLoad()) == 1 and int(RZ.RELOC.get(u1)) == 0, "FR4 the next start reads the list back")
    RZ.RELOC.clear()
    RZ.relocSave()
    K.check(not os.path.exists(os.path.join(wg, "zone-resets", "relocate.properties")), "FR4 an empty list removes its file")
    shutil.rmtree(pdir)
    # ---- fix round 2 checks (second critics), EXECUTED on scratch folders
    zr = os.path.join(wg, "zone-resets", ZW)
    def mkb(name, status, files):
        b = os.path.join(zr, name)
        os.makedirs(os.path.join(b, "tied"), exist_ok=True)
        open(os.path.join(b, "manifest.properties"), "w").write("zone=1\nstatus=%s\nat=9\n" % status)
        for fn, tx in files.items():
            open(os.path.join(b, "tied", fn), "w", encoding="utf8", newline="").write(tx)
        return b
    # FX1 a backup's rows = tied/*.txt + the spools, every line once
    b1 = mkb("z1-rows", "aborted", {"zones.txt": "D 1 2 3 a\nD 4 5 6 b\n", "zones.spool": "D 4 5 6 b\nD 7 8 9 c\n", "explore.spool": "# SkyyExploration hdr\nC p 12\nC p 12\n"})
    ro = Tk.rowsOf(P(b1))
    K.check(str(ro[0]) == "D 1 2 3 a\nD 4 5 6 b\nD 7 8 9 c\n" and str(ro[1]) == "# SkyyExploration hdr\nC p 12\n" and bool(Tk.hasRows(ro)),
            "FX1 rowsOf merges the answer + the spool, each line once: %r / %r" % (str(ro[0]), str(ro[1])))
    b0 = mkb("z1-none", "aborted", {})
    ro0 = Tk.rowsOf(P(b0))
    K.check(ro0[0] is None and ro0[1] is None and not bool(Tk.hasRows(ro0)), "FX1 ... a backup without tied files has no rows")
    K.check(bool(Tk.restoredOk("regrow 3, exploration 7")) and not bool(Tk.restoredOk("regrow 3 - NOT ALL PUT BACK (kept)")) and not bool(Tk.restoredOk("FAILED: x"))
            and bool(Tk.restoredOk("nothing to put back")), "FX1 restoredOk")
    # FX2 tiedMark: complete -> tiedpending (after = restored) -> ok -> restored; aborted -> tiedpending (after = aborted) -> ok -> aborted
    b2 = mkb("z1-mark", "complete", {"zones.txt": "D 1 1 1 a\n"})
    Tk.tiedMark(P(b2), False)
    m2 = open(os.path.join(b2, "manifest.properties")).read()
    Tk.tiedMark(P(b2), True)
    m2b = open(os.path.join(b2, "manifest.properties")).read()
    Tk.tiedMark(P(b1), False)
    m1 = open(os.path.join(b1, "manifest.properties")).read()
    K.check("status=tiedpending" in m2 and "statusAfter=restored" in m2 and "status=restored" in m2b and "status=tiedpending" in m1 and "statusAfter=aborted" in m1
            and "zone=1" in m2b, "FX2 tiedMark: the rows not back -> tiedpending (hidden from undo), back -> the status after")
    K.check(not any(str(e[0].getFileName()) in ("z1-mark", "z1-rows") for e in RZ.backups(0)), "FX2 ... a tiedpending / restored backup is never offered to /zone 1 reset undo")
    # FX3 the next start: tiedRetry queues each tiedpending backup's rows (op 10, with its folder), removes the restored ones, leaves the rest
    RZ.PENDQ.clear()
    tr = str(RZ.tiedRetry())
    q = list(RZ.PENDQ)
    K.check("1 backup(s) with regrow / exploration rows" in tr and "1 finished undo folder(s) removed" in tr and len(q) == 1 and int(q[0].op) == 10
            and str(q[0].dir.getFileName()) == "z1-rows" and str(q[0].a[0]).count("D ") == 3 and not os.path.isdir(b2) and os.path.isdir(b0),
            "FX3 tiedRetry: %s" % tr)
    RZ.PENDQ.clear()
    K.eq(str(RZ.tiedRetry()).count("backup(s)"), 1, "FX3 ... still pending until op 10 marks it (it is queued again at every start)")
    RZ.PENDQ.clear()
    # FX4 a crash INSIDE step 5 (journal 'tiedstart'): the spooled rows go back through the next start (critic 1 #3)
    for d in (b0, b1):
        shutil.rmtree(d)
    b4 = mkb("z1-ts", "writing", {"explore.spool": "# SkyyExploration hdr\nC p 5\n", "zones.spool": "D 1 2 3 a\n"})
    RZ.journal("reset", 0, "tiedstart", "z1-ts", None)
    s7 = str(RZ.recovery())
    m4 = open(os.path.join(b4, "manifest.properties")).read()
    K.check("stopped at 'tiedstart' before the world changed" in s7 and "rows go back when the world loads" in s7 and "status=tiedpending" in m4 and "statusAfter=aborted" in m4
            and not os.path.exists(os.path.join(wg, "zone-resets", "inprogress.properties")), "FX4 %s" % s7[:200])
    RZ.PENDQ.clear()
    K.check("1 backup(s)" in str(RZ.tiedRetry()) and len(list(RZ.PENDQ)) == 1, "FX4 ... the next start queues them")
    RZ.PENDQ.clear()
    shutil.rmtree(b4)
    b5 = mkb("z1-ts2", "writing", {})
    RZ.journal("reset", 0, "tiedstart", "z1-ts2", None)
    s8 = str(RZ.recovery())
    K.check("nothing to do" in s8 and "status=aborted" in open(os.path.join(b5, "manifest.properties")).read(), "FX4 a stop at 'tiedstart' before any row was spooled: aborted, nothing to do")
    shutil.rmtree(b5)
    # FX5 HOLD (critics 2 #1 / 3 #1): a zone with a queued tidy stays closed until the restart; a cancelled tidy opens it again
    RZ.tidyQueue(0, "reset", "z1-h")
    h = int(RZ.holdSync())
    t_hold = str(RZ.closedText(0))
    RZ.close(0)
    t_run = str(RZ.closedText(0))
    RZ.open(0)
    K.check(h == 1 and bool(RZ.closed(0)) and not bool(RZ.closed(1)) and "after the next server restart" in t_hold and "being rebuilt" in t_run,
            "FX5 a queued tidy holds Zone 1 closed (%s)" % t_hold)
    RZ.tidyCancel(0, "z1-h")
    K.check(int(RZ.holdSync()) == 0 and not bool(RZ.closed(0)), "FX5 ... the undo's cancel opens it again")
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass
    Cfg, St, Isl, Sd, RZ = (JClass(PKG + n) for n in ("WgCfg", "WgStore", "WgZ2Isles", "WgZSeed", "WgRZ"))
    Paths = JClass("java.nio.file.Paths")
    if not (home and os.path.isdir(home)):
        K.check(False, "L no live copy")
        K.save()
        return

    def tree():
        o = {}
        for r, _ds, fs in os.walk(home):
            for f in fs:
                p = os.path.join(r, f)
                o[os.path.relpath(p, home)] = open(p, "rb").read()
        return o
    t0 = tree()
    for s in (1, 2):
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        St.FILE = Paths.get(os.path.join(home, "worlds.properties"))
        Cfg.load()
        St.read()
        Isl.LAYDIR = Paths.get(home)
        Sd.load(Isl.SEED)
        b = str(RZ.boot(Paths.get(home), Paths.get(os.path.dirname(home))))
        K.check(str(Sd.sig()) == "0,0,0,0,0" and "no unfinished reset" in b and "no tidy queued" in b, "L start %d: every zone gen 0, nothing to recover / tidy (%s)" % (s, b))
    K.check(tree() == t0, "L start twice: the live copy is byte-identical - %d files" % len(t0))
    K.check(int(Cfg.RESET_KEEP) == 3 and int(Cfg.RESET_SLOT) == 600 and bool(Cfg.RESET_MAP), "L the live config (no reset rows yet) runs on the defaults 3 / 600 / on")
    K.save()


# ------------------------------------------------------------------------------------------- S: the real server (probe plugin)
PROBE_SRC = r'''
import os, sys
TOOLS = %(tools)r
sys.path.insert(0, TOOLS)
import skyybuild as B
J = B.start(server_jar=B.SERVER_JAR)
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
pool.insertClassPath(%(jar)r)
W = "com.skyy.worldgen."
T = {"W": W, "WLD": "com.hypixel.hytale.server.core.universe.world.World", "UNI": "com.hypixel.hytale.server.core.universe.Universe",
     "CU": "com.hypixel.hytale.math.util.ChunkUtil", "GC": "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk",
     "GCS": "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunkSection", "OUT": %(out)r,
     "CMGR": "com.hypixel.hytale.server.core.command.system.CommandManager", "CON": "com.hypixel.hytale.server.core.console.ConsoleSender",
     "CS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore", "REF": "com.hypixel.hytale.component.Ref",
     "BSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
     "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType", "LOG": "com.hypixel.hytale.logger.HytaleLogger"}
def jv(s):
    for k in sorted(T, key=len, reverse=True):
        s = s.replace("@%%s@" %% k, T[k])
    return s
def M(c, s):
    try: c.addMethod(CtNewMethod.make(jv(s), c))
    except Exception as e: raise SystemExit("compile %%s: %%s\n%%s" %% (c.getName(), e, jv(s)[:3000]))
def F(c, s): c.addField(CtField.make(jv(s), c))
run = pool.makeClass("wgq.Run")
run.addInterface(pool.get("java.lang.Runnable"))
F(run, "public static @LOG@ LOG;")
F(run, "public static final StringBuffer OUTB = new StringBuffer();")
F(run, "public static volatile int OK = 0;")
F(run, "public static volatile int BAD = 0;")
run.addConstructor(CtNewConstructor.make("public Run() { }", run))
M(run, r"""
public static void log(String m) {
  OUTB.append(m).append('\n');
  try { LOG.at(java.util.logging.Level.INFO).log("[SkyyWgProbe] " + m); } catch (Throwable t) { }
}""")
M(run, r"""
public static void check(boolean c, String what) { if (c) { OK++; log("OK " + what); } else { BAD++; log("FAIL " + what); } }""")
M(run, r"""
public static void flush() {
  try {
    java.nio.file.Path d = java.nio.file.Paths.get("@OUT@", new String[0]);
    java.nio.file.Files.createDirectories(d, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(d.resolve("probe.txt"), OUTB.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
  } catch (Throwable t) { }
}""")
M(run, r"""
public static long hashChunk(@GC@ gc) {
  long h = 1125899906842597L;
  for (int sy = 0; sy < 10; sy++) {
    @GCS@ sec = gc.getBlockChunk().getSection(sy * 32);
    if (sec == null) { h = h * 31L + 7L; continue; }
    int[] d = sec.getData();
    if (d == null) { h = h * 31L + 11L; continue; }
    for (int i = 0; i < d.length; i++) h = h * 31L + (long) d[i];
  }
  return h;
}""")
M(run, r"""
public static void cmd(String c) {
  try {
    Object f = @CMGR@.get().handleCommand(@CON@.INSTANCE, c);
    if (f instanceof java.util.concurrent.CompletableFuture) ((java.util.concurrent.CompletableFuture) f).get(30L, java.util.concurrent.TimeUnit.SECONDS);
  } catch (Throwable t) { log("cmd '" + c + "' failed: " + t); }
  log("console> " + c);
}""")
M(run, r"""
public static boolean waitIdle(long ms) {
  long end = System.currentTimeMillis() + ms;
  try { Thread.sleep(500L); } catch (Throwable t) { }
  while (@W@WgRZ.BUSY.get() && System.currentTimeMillis() < end) { try { Thread.sleep(250L); } catch (Throwable t) { } }
  return !@W@WgRZ.BUSY.get();
}""")
# sha1 of every stored chunk (the live store, read only)
M(run, r"""
public static java.util.HashMap shas(@WLD@ w) throws Exception {
  @W@WgRTask t = new @W@WgRTask(4, w, null, 0);
  long[] all = (long[]) @W@WgRJob.onW(w, t, 60000L);
  @W@WgRStore st = new @W@WgRStore(t.a, t.b, null);
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < all.length; i++) {
    byte[] b = st.read(all[i]);
    if (b != null) m.put(Long.valueOf(all[i]), @W@WgRZ.sha1(b));
  }
  return m;
}""")
M(run, r"""
public static long[] samples(@W@WgZ2Layout L) {
  long[] o = new long[10];
  for (int k = 0; k < 5; k++) {
    o[2 * k] = @CU@.indexChunk(((int) Math.floor(L.lx[k])) >> 5, ((int) Math.floor(L.lz[k])) >> 5);
    o[2 * k + 1] = @CU@.indexChunk((((int) Math.floor(L.cx[k])) >> 5) + 3, (((int) Math.floor(L.cz[k])) >> 5) - 2);
  }
  return o;
}""")
M(run, r"""
public static long[] gen(@W@WgZ2Gen g, @W@WgZ2Layout L, int s, long[] ix) throws Exception {
  long[] h = new long[ix.length];
  for (int i = 0; i < ix.length; i++) {
    int cx = @CU@.xOfChunkIndex(ix[i]);
    int cz = @CU@.zOfChunkIndex(ix[i]);
    h[i] = hashChunk((@GC@) g.generateWith(L, s, ix[i], cx, cz, null, null).get(180L, java.util.concurrent.TimeUnit.SECONDS));
  }
  return h;
}""")
M(run, r"""
public static String blockAt(@WLD@ w, int x, int y, int z) {
  @CS@ cs = w.getChunkStore();
  @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
  if (r == null || !r.isValid()) return null;
  Object s = cs.getStore().getComponent(r, @BSEC@.getComponentType());
  if (!(s instanceof @BSEC@)) return null;
  Object t = @BTY@.getAssetMap().getAsset(((@BSEC@) s).get(x, y, z));
  if (!(t instanceof @BTY@)) return "Empty";
  return String.valueOf(((@BTY@) t).getId());
}""")
blk = pool.makeClass("wgq.Blk")
blk.addInterface(pool.get("java.lang.Runnable"))
for f in ("public @WLD@ w;", "public int x;", "public int y;", "public int z;", "public volatile String res;", "public volatile boolean done;"):
    F(blk, f)
blk.addConstructor(CtNewConstructor.make(jv("public Blk(@WLD@ w, int x, int y, int z) { this.w = w; this.x = x; this.y = y; this.z = z; }"), blk))
M(blk, "public void run() { try { StringBuilder sb = new StringBuilder(); for (int d = 0; d <= 4; d++) sb.append(wgq.Run.blockAt(this.w, this.x, this.y - d, this.z)).append(d < 4 ? \",\" : \"\"); this.res = sb.toString(); } catch (Throwable t) { this.res = \"ERR \" + t; } this.done = true; }")
M(run, r"""
public static int count(java.util.HashMap m, @W@WgZ2Layout L, int k, boolean in) {
  int n = 0;
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) { long ix = ((Long) it.next()).longValue(); boolean o = @W@WgZ2Isles.ownerOf(L, @CU@.xOfChunkIndex(ix), @CU@.zOfChunkIndex(ix)) == k; if (o == in) n++; }
  return n;
}""")
# every key of a (not zone k by L) is in b with the same sha
M(run, r"""
public static int sameOthers(java.util.HashMap a, java.util.HashMap b, @W@WgZ2Layout L, int k) {
  int bad = 0;
  java.util.Iterator it = a.keySet().iterator();
  while (it.hasNext()) {
    Long ix = (Long) it.next();
    if (@W@WgZ2Isles.ownerOf(L, @CU@.xOfChunkIndex(ix.longValue()), @CU@.zOfChunkIndex(ix.longValue())) == k) continue;
    if (!String.valueOf(a.get(ix)).equals(String.valueOf(b.get(ix)))) bad++;
  }
  return bad;
}""")
M(run, open(%(body)r, encoding="utf8").read().split("#BODY\n", 1)[1])
pl = pool.makeClass("wgq.SkyyWgProbePlugin", pool.get("com.hypixel.hytale.server.core.plugin.JavaPlugin"))
pl.addConstructor(CtNewConstructor.make("public SkyyWgProbePlugin(com.hypixel.hytale.server.core.plugin.JavaPluginInit init) { super(init); }", pl))
M(pl, "public void setup() { wgq.Run.LOG = getLogger(); wgq.Run.log(\"1.0.0 ready (TEST PROBE wg0710 H - never deploy)\"); Thread t = new Thread(new wgq.Run(), \"SkyyWgProbeH\"); t.setDaemon(true); t.start(); }")
out = os.path.join(%(pdir)r, "classes")
import shutil
shutil.rmtree(out, ignore_errors=True)
os.makedirs(out)
for c in (run, blk, pl):
    c.writeFile(out)
man = B.manifest("SkyyWgProbe", "1.0.0", "TEST PROBE wg0710 H (scratch only, never deployed)", "wgq.SkyyWgProbePlugin")
man["IncludesAssetPack"] = False
man["Dependencies"] = {%(key)r: "*"}
B.assemble(os.path.join(%(pdir)r, "SkyyWgProbe-1.0.0.jar"), man, out)
'''

PROBE_BODY = r'''#BODY
public void run() {
  try {
    @UNI@ u = null;
    for (int i = 0; i < 1200; i++) { try { u = @UNI@.get(); if (u != null && u.getDefaultWorld() != null) break; } catch (Throwable t) { } Thread.sleep(250L); }
    Thread.sleep(4000L);
    @WLD@ w = u.getWorld("skywynn_zones2");
    if (w == null) w = (@WLD@) u.loadWorld("skywynn_zones2").get(240L, java.util.concurrent.TimeUnit.SECONDS);
    @W@WgZ2Gen g = @W@WgZ2Isles.genOf(w);
    int s = (int) w.getWorldConfig().getSeed();
    @W@WgZ2Layout L0 = g.layoutNow(s);
    check(L0 != null && !L0.failed && L0.gsig == null && g.base == L0 && "0,0,0,0,0".equals(@W@WgZSeed.sig()), "H1 no seeds file: the live layout is the gen-0 base (0.7.9's)");
    long[] smp = samples(L0);
    long[] h0 = gen(g, L0, s, smp);
    // ---- H3: a pick for every zone (gen from NEXT), never changing anything
    for (int k = 0; k < 5; k++) {
      int[] out = new int[1];
      String[] why = new String[1];
      long t0 = System.currentTimeMillis();
      @W@WgZ2Layout Z = @W@WgZ2Isles.pickZone(g, L0, g.base, s, k, 1, 600, @W@WgZ2Isles.counts(), out, why);
      if (Z == null) { log("H3 zone " + (k + 1) + ": no fit - " + why[0]); continue; }
      double mv = Math.sqrt((Z.cx[k] - g.base.cx[k]) * (Z.cx[k] - g.base.cx[k]) + (Z.cz[k] - g.base.cz[k]) * (Z.cz[k] - g.base.cz[k]));
      double gp = 1.0E9;
      for (int j = 0; j < L0.n; j++) { int zj = j < L0.nMain ? j : L0.zone[j]; if (zj == k || !L0.found[j]) continue; gp = Math.min(gp, @W@WgZ2Isles.boxGap(Z, k, L0, j)); }
      check(mv <= 600.0 + 64.0 && gp >= 900.0 && (double) Z.area[k] >= 0.7 * (double) g.base.area[k] && Z.seed == @W@WgZSeed.mix(s, k, out[0]),
            "H3 zone " + (k + 1) + " gen " + out[0] + " (" + why[0] + ", " + (System.currentTimeMillis() - t0) + " ms): centre moved " + Math.round(mv) + ", gap " + Math.round(gp) + ", area " + (100L * Z.area[k] / Math.max(1L, g.base.area[k])) + "%, " + @W@WgZ2Isles.zoneText(Z, k));
    }
    java.util.HashMap A = shas(w);
    int z1n = count(A, L0, 0, true);
    log("H8 stored before: " + A.size() + " chunks, Zone 1 " + z1n);
    String land0 = @W@WgCfg.ZSPAWN;
    // ---- refusals + the dry run
    cmd("zone 1 reset confirm");
    waitIdle(30000L);
    check(@W@WgZSeed.GEN[0] == 0, "H8 a confirm without a plan changes nothing");
    cmd("zone 9 reset");
    cmd("zone 1 reset");
    check(waitIdle(120000L) && @W@WgRZ.PLANS.get("r0") != null && @W@WgZSeed.GEN[0] == 0, "H8 /zone 1 reset (console) = a plan, nothing changed");
    cmd("zone 1 reset confirm");
    check(waitIdle(900000L), "H8 the reset finished");
    log("H8 last: " + @W@WgRZ.LAST);
    @W@WgZ2Layout L1 = g.layoutReady(s);
    check(@W@WgZSeed.GEN[0] >= 1 && L1 != null && L1.gsig != null && L1.zs[0] == @W@WgZSeed.SEED[0] && L1.zs[1] == s, "H8 Zone 1 is on gen " + @W@WgZSeed.GEN[0] + " (seed " + @W@WgZSeed.SEED[0] + "), Zones 2-5 on the world seed");
    java.util.HashMap Bm = shas(w);
    int gone = 0;
    int changed = 0;
    java.util.Iterator it = A.keySet().iterator();
    while (it.hasNext()) {
      Long ix = (Long) it.next();
      if (@W@WgZ2Isles.ownerOf(L0, @CU@.xOfChunkIndex(ix.longValue()), @CU@.zOfChunkIndex(ix.longValue())) != 0) continue;
      Object v = Bm.get(ix);
      if (v == null) gone++; else if (!v.equals(A.get(ix))) changed++;
    }
    check(gone + changed == z1n, "H8 every Zone 1 chunk of before is gone (" + gone + ") or new (" + changed + ") of " + z1n);
    check(sameOthers(A, Bm, L0, 0) == 0, "H8 every chunk of Zones 2-5 is byte-identical after the reset");
    long[] h1 = gen(g, L1, s, smp);
    boolean same25 = true;
    for (int i = 2; i < 10; i++) if (h1[i] != h0[i]) same25 = false;
    check(same25, "H1 sample chunks of Zones 2-5 generate byte-identical after the Zone 1 reset");
    check(h1[0] != h0[0] || h1[1] != h0[1], "H1 Zone 1's sample chunks generate differently on its new seed");
    java.util.ArrayList bl = @W@WgRZ.backups(0);
    java.util.Properties bm = bl.isEmpty() ? null : (java.util.Properties) ((Object[]) bl.get(0))[1];
    check(bm != null && Integer.parseInt(bm.getProperty("chunks", "-1")) == z1n, "H8 the backup lists Zone 1's " + z1n + " chunks");
    if (bm != null) {
      Object[] cl = @W@WgRZ.chunksOf(bm);
      long[] ix = (long[]) cl[0];
      String[] sh = (String[]) cl[1];
      int bad = 0;
      for (int i = 0; i < ix.length; i++) if (!sh[i].equals(A.get(Long.valueOf(ix[i])))) bad++;
      check(bad == 0, "H8 the backup's sha1s = Zone 1's chunks before the reset");
    }
    check(!land0.equals(@W@WgCfg.ZSPAWN) && @W@WgCfg.ZSPAWN.length() > 0, "H8 the Zone 1 landing (server spawn) moved: " + land0 + " -> " + @W@WgCfg.ZSPAWN);
    check(@W@WgRZ.closed(0) && (@W@WgRZ.HOLD & 1) != 0 && @W@WgRZ.closedText(0).indexOf("restart") > 0, "FX5 after the reset Zone 1 stays closed until the restart: " + @W@WgRZ.closedText(0));
    double[] p = @W@WgCfg.parseSpawn(@W@WgCfg.ZSPAWN);
    // fix round 2: the reset no longer pre-loads (the restart's WgZ2Pre does, after the tidy) - the probe loads the landing chunk itself
    try { w.getChunkStore().getChunkReferenceAsync(@CU@.indexChunk(((int) Math.floor(p[0])) >> 5, ((int) Math.floor(p[2])) >> 5)).get(120L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { log("H7 landing chunk load: " + t); }
    wgq.Blk bk = new wgq.Blk(w, (int) Math.floor(p[0]), (int) Math.floor(p[1]), (int) Math.floor(p[2]));
    w.execute(bk);
    for (int i = 0; i < 400 && !bk.done; i++) Thread.sleep(50L);
    check(bk.res != null && bk.res.indexOf("Empty") != 0 || (bk.res != null && !bk.res.endsWith("Empty,Empty,Empty")), "H7 the new landing is over ground (blocks from y to y-4: " + bk.res + ")");
    check(Bm.size() > 0 && @W@WgRZ.CLOSED == 0, "H8 the zone is open again");
    check(@W@WgRZ.RELOC.containsKey("d8ddde89-98b2-4739-983e-a39773d582b6") && java.nio.file.Files.exists(@W@WgRZ.relocFile(), new java.nio.file.LinkOption[0]), "FR4 the REAL player file offline on Zone 1 (-1251, 1045) is listed for their island: " + @W@WgRZ.RELOC);
    // ---- the undo
    cmd("zone 1 reset undo");
    check(waitIdle(60000L) && @W@WgRZ.PLANS.get("u0") != null, "H5 /zone 1 reset undo = a plan");
    cmd("zone 1 reset undo confirm");
    check(waitIdle(900000L), "H5 the undo finished");
    log("H5 last: " + @W@WgRZ.LAST);
    check(!java.nio.file.Files.exists(@W@WgRZ.root().resolve("tidy.properties"), new java.nio.file.LinkOption[0]), "FR2 the undo (no restart since the reset) cancelled the reset's next-start tidy and queued none");
    check(!@W@WgRZ.closed(0) && @W@WgRZ.HOLD == 0, "FX5 ... and Zone 1 is open again (nothing to tidy)");
    java.util.HashMap Cm = shas(w);
    int miss = 0;
    int diff = 0;
    int extra = 0;
    it = A.keySet().iterator();
    while (it.hasNext()) { Long ix = (Long) it.next(); Object v = Cm.get(ix); if (v == null) miss++; else if (!v.equals(A.get(ix))) diff++; }
    it = Cm.keySet().iterator();
    while (it.hasNext()) { Long ix = (Long) it.next(); if (!A.containsKey(ix)) extra++; }
    check(miss == 0 && diff == 0, "H5 after the undo every chunk of before is back byte-identical (missing " + miss + ", different " + diff + ", extra " + extra + ")");
    check(@W@WgZSeed.GEN[0] == 0 && land0.equals(@W@WgCfg.ZSPAWN), "H5 the seed (gen 0) and the landing " + land0 + " are back");
    long[] h2 = gen(g, g.layoutReady(s), s, smp);
    check(java.util.Arrays.equals(h2, h0), "H1 after the undo every sample chunk (all 5 zones) generates as before");
    java.util.ArrayList bl2 = @W@WgRZ.backups(0);
    check(bl2.size() == 1 && "undo".equals(((java.util.Properties) ((Object[]) bl2.get(0))[1]).getProperty("kind")), "H5 the reset's backup is gone, the safety backup of the undone land is kept");
    // ---- a second reset = new land (gen 2, never gen 1 again)
    int s1 = 0;
    cmd("zone reset 1");
    waitIdle(20000L);
    check(@W@WgRZ.PLANS.get("r0") == null, "FX6 the swapped form /zone reset 1 is gone (usage only, no plan)");
    cmd("zone 1 reset list");
    cmd("zone 1 reset");
    waitIdle(120000L);
    cmd("zone 1 reset confirm");
    check(waitIdle(900000L) && @W@WgZSeed.GEN[0] >= 2, "H6 a second reset uses a NEW generation (" + @W@WgZSeed.GEN[0] + ", seed " + @W@WgZSeed.SEED[0] + ")");
    log("H6 last: " + @W@WgRZ.LAST);
    log("H6 resets: " + @W@WgRZ.listLines()[1]);
    Object[] rl = @W@WgHooks.resetList(null, "console");
    check(rl != null && "ok".equals(rl[0]) && String.valueOf(rl[2]).length() < 400 && String.valueOf(rl[2]).indexOf("Zone 1: reset ") == 0, "FX7 the Server Setup answer is one short line per zone (" + String.valueOf(rl[2]).length() + " chars): " + rl[2]);
    check(@W@WgRZ.closed(0), "FX5 the second reset holds Zone 1 closed again");
  } catch (Throwable t) { log("probe FAILED " + t); BAD++; }
  log("RESULT ok=" + OK + " fail=" + BAD);
  flush();
}'''


def server_phase():
    if "--no-smoke" in sys.argv:
        print("S. skipped (--no-smoke) - the live path is UNVERIFIED by this run")
        HK.check(True, "S skipped")
        return
    import deploy_set as DS
    if DS.server_running():
        print("S. NOT RUN: a HytaleServer is running (the game / another smoke test) - the live path is UNVERIFIED by this run")
        return
    pdir = os.path.join(SCRATCH, "probe")
    odir = os.path.join(SCRATCH, "probe-out")
    os.makedirs(pdir, exist_ok=True)
    key = "Skyy:%s SkyyWorldGen" % VERSION
    body = os.path.join(pdir, "body.txt")
    open(body, "w", encoding="utf8").write(PROBE_BODY)
    open(os.path.join(pdir, "pb.py"), "w", encoding="utf8").write(PROBE_SRC % {"tools": os.path.join(ROOT, "tools"), "jar": JAR, "out": odir.replace("\\", "/"),
                                                                                 "pdir": pdir, "key": key, "body": body})
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    r1 = subprocess.run([sys.executable, os.path.join(pdir, "pb.py")], cwd=pdir, env=env, capture_output=True, text=True, timeout=900)
    pj = os.path.join(pdir, "SkyyWgProbe-1.0.0.jar")
    okb = r1.returncode == 0 and os.path.isfile(pj)
    HK.check(okb, "S the test probe builds: %s" % (r1.stdout + r1.stderr)[-1500:])
    if not okb:
        return
    jars = [JAR, os.path.join(ROOT, "SkyyZones", "SkyyZones-0.2.1.jar"), os.path.join(ROOT, "SkyyExploration", "SkyyExploration-0.3.4.jar"), pj]
    smoke = os.path.join(ROOT, "tools", "dev", "scratch", "smoke")
    before = set(os.listdir(smoke)) if os.path.isdir(smoke) else set()
    args = [sys.executable, os.path.join(ROOT, "tools", "smoke_test.py"), "--linger", "1500", "--xmx", "6G", "--allow-pack-api", "--keep"]
    for j in jars:
        args += ["--jar", j]
    t0 = time.time()
    r2 = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=3600)
    open(os.path.join(SCRATCH, "smoke-out.txt"), "w", encoding="utf8").write(r2.stdout + r2.stderr)
    new = sorted(set(os.listdir(smoke)) - before) if os.path.isdir(smoke) else []
    runs = [n for n in new if n.startswith("run-")]
    logs = [n for n in new if n.endswith(".log")]
    txt = open(os.path.join(odir, "probe.txt"), encoding="utf8").read() if os.path.isfile(os.path.join(odir, "probe.txt")) else ""
    for l in txt.splitlines():
        if l.startswith(("OK ", "FAIL ", "H", "RESULT", "console", "probe")):
            print("   S " + l[:400])
    m = re.search(r"RESULT ok=(\d+) fail=(\d+)", txt)
    HK.check(m is not None and int(m.group(2)) == 0 and int(m.group(1)) >= 20, "S the probe on the REAL server: %s (%.0f s)" % (m.group(0) if m else "no RESULT", time.time() - t0))
    for l in txt.splitlines():
        if l.startswith("FAIL "):
            HK.check(False, "S " + l)
    so = r2.stdout or ""
    ours = [l for l in so.splitlines() if l.strip().startswith("FAIL") and "SkyyWgProbe" not in l]
    HK.check(not ours and ("SMOKE TEST PASS" in so or "no ready line: SkyyWgProbe" in so), "S smoke: every SET ready line, no Skyy SEVERE: %s" % ours[:5])
    if logs:
        lg = open(os.path.join(smoke, logs[-1]), encoding="utf-8", errors="replace").read()
        sev = [l for l in lg.splitlines() if ("SEVERE" in l or "ERROR" in l) and "SkyyWorldGen" in l]
        HK.check(not sev, "S no SEVERE / ERROR line of SkyyWorldGen in the server log: %s" % sev[:3])
        shutil.copyfile(os.path.join(smoke, logs[-1]), os.path.join(SCRATCH, "server.log"))
    # H7: the kept world's start-up code (WgRZ.boot) twice on its files: the queued tidy runs once
    # fix round: OUR run folder only (smoke_test prints it) - another agent's smoke server may be running in a newer run-* folder
    mk = re.search(r"scratch kept: (.+)", r2.stdout or "")
    runs = [os.path.basename(mk.group(1).strip())] if mk and os.path.isdir(mk.group(1).strip()) else []
    if runs:
        rw = os.path.join(smoke, runs[-1], "world")
        kept = os.path.join(SCRATCH, "kept")
        os.makedirs(kept, exist_ok=True)
        shutil.copytree(os.path.join(rw, "mods", "Skyy_SkyyWorldGen"), os.path.join(kept, "mods", "Skyy_SkyyWorldGen"))
        if os.path.isdir(os.path.join(rw, "mods", "BetterMap")):
            shutil.copytree(os.path.join(rw, "mods", "BetterMap"), os.path.join(kept, "mods", "BetterMap"))
        shutil.copytree(os.path.join(rw, "universe", "worlds", ZW, "resources"), os.path.join(kept, "universe", "worlds", ZW, "resources"))
        shutil.rmtree(os.path.join(smoke, runs[-1]), ignore_errors=True)
        out = os.path.join(SCRATCH, "boot.json")
        r3 = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", "boot", "--out", out, "--dir", SCRATCH, "--jar", JAR, "--home", kept], env=env)
        HK.take(out, "boot")


def run_boot(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    from jpype import JClass
    Isl, Sd, RZ, Cfg = (JClass(PKG + n) for n in ("WgZ2Isles", "WgZSeed", "WgRZ", "WgCfg"))
    Paths = JClass("java.nio.file.Paths")
    wg = os.path.join(home, "mods", "Skyy_SkyyWorldGen")
    Cfg.FILE = Paths.get(os.path.join(wg, "config.properties"))
    Cfg.load()
    Isl.LAYDIR = Paths.get(wg)
    Sd.load(Isl.SEED)
    K.check(int(Sd.GEN[0]) >= 2 and int(Sd.GEN[1]) == 0, "H7 the kept world's seeds file: %s" % Sd.text())
    b1 = str(RZ.boot(Paths.get(wg), Paths.get(os.path.join(home, "mods"))))
    K.check("zone 1 (reset)" in b1 and "zone 1 (undo)" not in b1 and b1.count("zone 1 (reset)") == 1 and "no unfinished reset" in b1,
            "H7 start 1 runs the ONE queued tidy (the second reset; the first was cancelled by the undo before any restart): %s" % b1[:400])
    K.check("offline player(s) go to their island" in b1, "FR4 start 1 reads the offline-player list back: %s" % b1[-200:])
    snap = dict((os.path.relpath(os.path.join(r, f), home), open(os.path.join(r, f), "rb").read()) for r, _d, fs in os.walk(home) for f in fs)
    b2 = str(RZ.boot(Paths.get(wg), Paths.get(os.path.join(home, "mods"))))
    snap2 = dict((os.path.relpath(os.path.join(r, f), home), open(os.path.join(r, f), "rb").read()) for r, _d, fs in os.walk(home) for f in fs)
    K.check("no tidy queued" in b2 and snap == snap2, "H7 start 2 changes nothing (%s)" % b2)
    L = RZ.bootLayout()
    K.check(L is not None and str(L.gsig).startswith(str(int(Sd.GEN[0])) + ",") and int(L.zs[0]) == int(Sd.SEED[0]), "H7 the start-up layout = gen 0 + the Zone 1 gen file (%s)" % (None if L is None else L.gsig))
    K.save()


if __name__ == "__main__":
    if HK.arg("--phase") == "boot":
        try:
            run_boot(HK.arg("--out"), JAR, SCRATCH, HK.arg("--home"))
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
        sys.exit(0)
    if "--phase" not in sys.argv and "--server-only" not in sys.argv:
        pass
    if "--phase" not in sys.argv:
        import atexit
    _run0 = HK.run

    def _run_with_server(*a, **kw):
        # the server phase runs after the bare phases, before the kit prints the verdict (it calls sys.exit)
        _check0 = HK.check
        _exit0 = sys.exit

        def _exit(code=0):
            sys.exit = _exit0
            if "--phase" not in sys.argv:
                server_phase()
                print("SkyyWorldGen %s harness (with the server phase): %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
                for f in HK.FAILS:
                    print("FAIL:", f)
                _exit0(1 if HK.FAILS else 0)
            _exit0(code)
        sys.exit = _exit
        return _run0(*a, **kw)
    _run_with_server("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
                     [("files", run_files), ("live", run_live)], __file__, live=(LIVE_WG, "Skyy_SkyyWorldGen"))
