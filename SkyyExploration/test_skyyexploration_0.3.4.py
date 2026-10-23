"""Harness for SkyyExploration 0.3.4 (round wg0710: explore:fn:dropBox / restoreBox for SkyyWorldGen 0.7.10's zone reset; tools/exploration_0_3_4_patch.py).
Build first:  python tools/exploration_0_3_4_patch.py && python SkyyExploration/build_skyyexploration_0.3.4.py
    python SkyyExploration/test_skyyexploration_0.3.4.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py; scratch tools/dev/scratch/wg0710/xh):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.3.3 -> 0.3.4: + ExpZBox; the plugin's setup / shutdown (the two bridge keys); the version texts
  LIVE  start twice on a scratch COPY of the live Skyy_SkyyExploration (the one-time updates + ExpCfg.load): nothing changes
  ZB    EXECUTED on a second scratch COPY of the live data (Skyy's real records: 4 profiles, the zones2 chest log, 16 luggage sites) + a
        synthetic chestloot/ copy: dropBox for Zone 1 of skywynn_zones2 (a java IntBinaryOperator owner, as SkyyWorldGen passes) with
        one profile LOADED in memory and three only on disk -> the zone's registry entries (R journal lines), luggage sites, chest
        copies, explored chunks, opened chests, regions entered and the Zone1_ regions known are gone (they pay again), paid / total lowered;
        every row of other worlds / outside the zone byte-for-byte kept; earned / owed untouched; restoreBox puts every row back (files and
        memory equal to before as sets); bad arguments -> null; the bridge keys
  AA    engine-access audit
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.3.4", "0.3.3"
PKG = "com.skyy.explore."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wg0710", "xh")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyExploration")
EXPECT = {"SkyyExplorationPlugin": ["~m setup", "~m shutdown"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "ExpLgMig": ["~m logLine", "~m migrate"], "ExpNcMig": ["~m logLine", "~m migrate"], "ExpP3Mig": ["~m migrate"],
          "ExpP7Mig": ["~m migrate"], "ExpCfg": ["~m load"]}   # the version texts (the migrations' WHO, the defaults header)
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["ExpZBox"]
W = "skywynn_zones2"
WF = "skywynn-zones2-4779f1c7"
P3 = "d8ddde89-98b2-4739-983e-a39773d582b6-p3"


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def reset(J):
    J("CfgHist").DIR = None
    J("CfgRows").HOME = None
    J("CfgLog").FILE = None
    J("CfgLog").Q.clear()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg = J("ExpCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Cfg.FILE = JClass("java.nio.file.Paths").get(os.path.join(home, "config.properties"))

    def start():
        reset(J)
        rs = [str(J(m).migrate()) for m in ("ExpLgMig", "ExpNcMig", "ExpP3Mig", "ExpP7Mig")]
        Cfg.load()
        return rs
    s0 = snapd(home)
    start()
    s1 = snapd(home)
    start()
    s2 = snapd(home)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(not ch, "LIVE start 1 on the live copy changes nothing (0.3.4 adds no setting / migration): %s" % ch)
    K.check(s1 == s2, "LIVE start 2 changes nothing")
    K.save()


def run_zb(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Sto, Reg, Lg, Pc, Box, IO = J("ExpCfg"), J("ExpStore"), J("ChestReg"), J("LgReg"), J("PcStore"), J("ExpZBox"), J("ExpIO")
    Paths = JClass("java.nio.file.Paths")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpTest")
    Sto.DIR = Paths.get(os.path.join(home, "players"))
    Reg.DIR = Paths.get(os.path.join(home, "chests"))
    Lg.DIR = Paths.get(os.path.join(home, "luggage"))
    Pc.DIR = Paths.get(os.path.join(home, "chestloot"))
    n_reg = int(Reg.loadAll())

    def inz(x, z):
        return -58 <= (x >> 5) <= 13 and -16 <= (z >> 5) <= 38

    @JImplements("java.util.function.IntBinaryOperator")
    class Owner(object):
        @JOverride
        def applyAsInt(self, cx, cz):
            return 1 if (-58 <= cx <= 13 and -16 <= cz <= 38) else 0
    # synthetic chestloot copies of one profile: one chest in Zone 1, one in Zone 3, one in another world
    pcd = os.path.join(home, "chestloot", P3)
    os.makedirs(pcd, exist_ok=True)
    open(os.path.join(pcd, WF + ".txt"), "w").write('# t\nC -776 75 525 5 {"s": []}\nC 1280 90 4800 6 {"s": []}\n')
    open(os.path.join(pcd, "default-5c13d641.txt"), "w").write('# t\nC -776 75 525 7 {"s": []}\n')
    # the chest log of zones2 before: live entries by position
    log0 = open(os.path.join(home, "chests", WF + ".log")).read()
    live0 = {}
    for l in log0.splitlines():
        p = l.split(" ")
        if p[0] == "A" and len(p) >= 6:
            live0[(int(p[1]), int(p[2]), int(p[3]))] = l
        elif p[0] == "R" and len(p) >= 4:
            live0.pop((int(p[1]), int(p[2]), int(p[3])), None)
    reg_in = [k for k in live0 if inz(k[0], k[2])]
    lug0 = [l for l in open(os.path.join(home, "luggage", WF + ".tsv")).read().splitlines() if l and not l.startswith("#")]
    lug_in = [l for l in lug0 if inz(int(l.split("\t")[0]), int(l.split("\t")[2]))]
    # profile files before
    pl = os.path.join(home, "players")
    keys = sorted(set(n[:-11] for n in os.listdir(pl) if n.endswith(".properties")) | set(n for n in os.listdir(pl) if os.path.isdir(os.path.join(pl, n))))
    before = snapd(pl)
    # profile p3 loaded in memory (its zones2 chunk set too), the others on disk only
    d3 = Sto.dataK(P3, JClass("java.util.UUID").fromString("d8ddde89-98b2-4739-983e-a39773d582b6"))
    cs3 = Sto.chunkSet(d3, WF)
    n3 = int(cs3.size())
    zw3 = int(Sto.zoneFor(d3, WF).size())
    paid3 = int(Sto.paidHere(d3, WF))
    tot3, earned3, chests3 = int(d3.total), int(d3.earned), int(d3.chests)
    K.check(n3 > 0 and zw3 == 5, "ZB profile p3 loaded: %d zones2 chunks, %d regions there, paid %d, total %d, %d chests" % (n3, zw3, paid3, tot3, chests3))
    import struct
    ck3 = [struct.unpack(">q", open(os.path.join(pl, P3, "chunks", WF + ".bin"), "rb").read()[i:i + 8])[0] for i in range(0, n3 * 8, 8)]
    CU = JClass("com.hypixel.hytale.math.util.ChunkUtil")
    ck3_in = [c for c in ck3 if inz(int(CU.xOfChunkIndex(c)) * 32, int(CU.zOfChunkIndex(c)) * 32)]
    Box(0).apply(None)
    drop = Box(0)
    K.check(drop.apply(JArray(JObject)([W])) is None and drop.apply(JArray(JObject)([W, "x", "Zone1_"])) is None, "ZB bad arguments -> null")
    txt = str(drop.apply(JArray(JObject)([W, Owner(), "Zone1_"])))
    rows = [l for l in txt.splitlines() if l]
    kinds = {}
    for l in rows:
        kinds[l[0]] = kinds.get(l[0], 0) + 1
    K.check(kinds.get("A", 0) == len(reg_in) and len(reg_in) > 0, "ZB the registry entries in Zone 1: %d dropped of %d (%d live in the world)" % (kinds.get("A", 0), len(reg_in), len(live0)))
    K.check(kinds.get("L", 0) == len(lug_in) and len(lug_in) > 0, "ZB the %d luggage sites of Zone 1 dropped: %d (the live count changes as Skyy plays)" % (len(lug_in), kinds.get("L", 0)))
    K.check(kinds.get("K", 0) == 1, "ZB the Zone 1 chest copy dropped (Zone 3's and the other world's kept): %d" % kinds.get("K", 0))
    K.check(kinds.get("C", 0) == len(ck3_in) and kinds.get("O", 0) == 5 and kinds.get("Z", 0) == 5, "ZB p3: %d chunks, %d chests, %d regions of zones2 dropped (want %d / 5 / 5)" % (kinds.get("C", 0), kinds.get("O", 0), kinds.get("Z", 0), len(ck3_in)))
    K.check(kinds.get("G", 0) >= 4, "ZB the Zone1_ regions known by every profile dropped (zone discovery pays again): %d rows" % kinds.get("G", 0))
    # registry + its journal
    log1 = open(os.path.join(home, "chests", WF + ".log")).read()
    K.check(log1.startswith(log0) and log1[len(log0):].count("\nR ") + log1[len(log0):].startswith("R ") == len(reg_in), "ZB the chest log: the old lines kept + one R line per dropped chest")
    K.check(all(Reg.get(WF, x, y, z) is None for x, y, z in reg_in) and Reg.size(WF) == len(live0) - len(reg_in), "ZB ChestReg: the zone's chests gone, the rest kept")
    lug1 = [l for l in open(os.path.join(home, "luggage", WF + ".tsv")).read().splitlines() if l and not l.startswith("#")]
    K.check(lug1 == [l for l in lug0 if l not in lug_in], "ZB luggage file: the zone's sites gone, the others byte-identical")
    pc1 = open(os.path.join(pcd, WF + ".txt")).read()
    K.check("C -776 75 525" not in pc1 and "C 1280 90 4800 6" in pc1 and open(os.path.join(pcd, "default-5c13d641.txt")).read().count("C -776") == 1,
            "ZB chestloot: the Zone 1 copy gone, Zone 3 + the other world kept")
    # p3 in memory + files
    K.check(int(cs3.size()) == n3 - len(ck3_in) and int(Sto.zoneFor(d3, WF).size()) == 0 and not any(str(k).startswith("Zone1_") for k in d3.zones.keySet()),
            "ZB p3 in memory: chunks %d -> %d, regions of zones2 gone, no Zone1_ region known" % (n3, int(cs3.size())))
    K.check(int(Sto.paidHere(d3, WF)) == max(0, paid3 - len(ck3_in)) and int(d3.total) == max(0, tot3 - len(ck3_in)) and int(d3.earned) == earned3 and int(d3.chests) == chests3 - 5,
            "ZB p3: paid %d -> %d, total %d -> %d, earned kept, chests %d -> %d" % (paid3, int(Sto.paidHere(d3, WF)), tot3, int(d3.total), chests3, int(d3.chests)))
    Sto.flushDirty()
    IO.drain()
    after = snapd(pl)
    for k in keys:
        if k == P3:
            continue
        pf = k + ".properties"
        if pf in before:
            a = before[pf].decode("latin-1")
            b = after[pf].decode("latin-1")
            ka = dict(l.split("=", 1) for l in a.splitlines() if "=" in l and not l.startswith("#"))
            kb = dict(l.split("=", 1) for l in b.splitlines() if "=" in l and not l.startswith("#"))
            za = set(x for x in ka.get("zones", "").split(",") if x)
            zb = set(x for x in kb.get("zones", "").split(",") if x)
            K.check(zb == set(x for x in za if not x.startswith("Zone1_")) and all(ka[x] == kb.get(x) for x in ka if x != "zones"),
                    "ZB %s on disk: Zone1_ regions gone, every other value kept" % k)
    for f in before:
        if f.startswith(P3) or f.endswith(".properties"):
            continue
        if f.endswith("chests.txt") or f.endswith("zones.txt"):
            keep = [l for l in before[f].decode().splitlines() if not l.startswith(WF + " ")]
            K.check([l for l in after[f].decode().splitlines() if not l.startswith(WF + " ")] == keep, "ZB %s: the other worlds' lines byte-identical" % f)
        elif WF not in f:
            K.check(after.get(f) == before[f], "ZB %s untouched" % f)
    ch3 = after[P3 + "/chests.txt"].decode().splitlines()
    K.check([l for l in ch3 if not l.startswith(WF)] == [l for l in before[P3 + "/chests.txt"].decode().splitlines() if not l.startswith(WF)] and not any(l.startswith(WF) for l in ch3),
            "ZB p3 chests.txt: the zones2 Zone 1 chests gone, the other world's line kept")
    # ---- restore
    back = Box(1)
    n = int(back.apply(JArray(JObject)([W, txt])))
    K.check(n == len(rows) - kinds.get("P", 0), "ZB restoreBox puts every row back: %d of %d" % (n, len(rows) - kinds.get("P", 0)))
    Sto.flushDirty()
    IO.drain()
    K.check(int(cs3.size()) == n3 and int(Sto.zoneFor(d3, WF).size()) == zw3 and int(Sto.paidHere(d3, WF)) == paid3 and int(d3.total) == tot3 and int(d3.chests) == chests3,
            "ZB p3 in memory after the undo = before (chunks %d, regions %d, paid %d, total %d, chests %d)" % (int(cs3.size()), int(Sto.zoneFor(d3, WF).size()), int(Sto.paidHere(d3, WF)), int(d3.total), int(d3.chests)))
    after2 = snapd(pl)
    for f in before:
        if f.endswith(".bin"):
            a = sorted(struct.unpack(">q", before[f][i:i + 8])[0] for i in range(0, len(before[f]), 8))
            b = sorted(struct.unpack(">q", after2[f][i:i + 8])[0] for i in range(0, len(after2[f]), 8))
            K.check(a == b, "ZB %s: the same chunk set after the undo" % f)
        elif f.endswith(".txt"):
            K.check(sorted(before[f].decode().splitlines()) == sorted(after2[f].decode().splitlines()), "ZB %s: the same lines after the undo" % f)
        elif f.endswith(".properties"):
            ka = dict(l.split("=", 1) for l in before[f].decode("latin-1").splitlines() if "=" in l and not l.startswith("#"))
            kb = dict(l.split("=", 1) for l in after2[f].decode("latin-1").splitlines() if "=" in l and not l.startswith("#"))
            ka["zones"] = sorted(ka.get("zones", "").split(","))
            kb["zones"] = sorted(kb.get("zones", "").split(","))
            K.check(ka == kb, "ZB %s: the same values after the undo (%s)" % (f, sorted(k for k in set(ka) | set(kb) if ka.get(k) != kb.get(k))))
    K.check(all(Reg.get(WF, x, y, z) is not None for x, y, z in reg_in) and Reg.size(WF) == len(live0), "ZB ChestReg after the undo = before")
    lug2 = [l for l in open(os.path.join(home, "luggage", WF + ".tsv")).read().splitlines() if l and not l.startswith("#")]
    K.check(sorted(lug2) == sorted(lug0), "ZB luggage after the undo = before")
    K.check("C -776 75 525 5" in open(os.path.join(pcd, WF + ".txt")).read(), "ZB the chest copy is back")
    K.eq(int(back.apply(JArray(JObject)([W, txt]))), 0, "ZB a second restore adds nothing (rows only go back where missing)")
    # ---- fix round checks
    # FX1 (critic: a section failing threw the rows away): a broken loot chest registry entry in the zone -> the rows of every other
    # section still come back, plus an #ERROR line (SkyyWorldGen then stops the reset and puts them back)
    Defs = J("ExpDefs")
    bad_key = JClass("java.lang.Long").valueOf(int(Defs.pack(-700, 80, 500)))
    Reg.W.get(WF).put(bad_key, JClass("java.lang.Integer").valueOf(5))
    txt2 = str(drop.apply(JArray(JObject)([W, Owner(), "Zone1_"])))
    k2 = {}
    for l in txt2.splitlines():
        if l:
            k2[l[0]] = k2.get(l[0], 0) + 1
    K.check("#ERROR the loot chest registry step failed" in txt2 and k2.get("C", 0) == len(ck3_in) and k2.get("L", 0) == len(lug_in) and k2.get("K", 0) == 1,
            "FX1 a failing registry step keeps every other row + says #ERROR (C %d, L %d, K %d)" % (k2.get("C", 0), k2.get("L", 0), k2.get("K", 0)))
    Reg.W.get(WF).remove(bad_key)
    back.apply(JArray(JObject)([W, txt2]))
    back.apply(JArray(JObject)([W, txt]))
    K.check(int(cs3.size()) == n3 and int(Sto.paidHere(d3, WF)) == paid3 and int(d3.total) == tot3 and sorted(
        l for l in open(os.path.join(home, "luggage", WF + ".tsv")).read().splitlines() if l and not l.startswith("#")) == sorted(lug0),
            "FX1 ... and those rows go back (p3 chunks %d, paid %d, total %d, luggage = before)" % (int(cs3.size()), int(Sto.paidHere(d3, WF)), int(d3.total)))
    # FX2 (critic: propsEdit garbled non-Latin-1 text): an offline profile file with a non-Latin-1 name keeps it byte-exact in meaning
    Props = JClass("java.util.Properties")
    pk = "zz-fixround-test"
    pp = Props()
    pp.setProperty("name", "Skÿy 世界 Ж")
    pp.setProperty("zones", "Zone1_A,Zone3_B")
    pp.setProperty("paid." + WF, "10")
    pp.setProperty("total", "12")
    fos = JClass("java.io.FileOutputStream")(os.path.join(pl, pk + ".properties"))
    pp.store(fos, "t")
    fos.close()
    dp = int(Box.propsEdit(pk, WF, JClass("java.util.ArrayList")(JClass("java.util.Arrays").asList(JArray(JObject)(["Zone1_A"]))), JClass("java.util.ArrayList")(), -4, 0, 6))
    rp = Sto.readLocked(Paths.get(os.path.join(pl, pk + ".properties")))
    K.check(str(rp.getProperty("name")) == "Skÿy 世界 Ж" and str(rp.getProperty("zones")) == "Zone3_B" and str(rp.getProperty("total")) == "8"
            and str(rp.getProperty("paid." + WF)) == "6" and dp == -4,
            "FX2 an offline profile's file: a non-Latin-1 name survives, zones / total / paid edited (paid %s, delta %d)" % (rp.getProperty("paid." + WF), dp))
    os.remove(os.path.join(pl, pk + ".properties"))
    # FX3 (critic: cap overshoot): the paid counter only falls as far as the chunks left need
    K.check([int(Box.paidDrop(500, 700, 690)), int(Box.paidDrop(500, 700, 100)), int(Box.paidDrop(700, 700, 100)), int(Box.paidDrop(0, 5, 5))] == [490, 0, 100, 0],
            "FX3 paidDrop: over the cap keeps the paid slots other chunks hold; no cap = every dropped chunk pays again")
    K.check(all(len(l.split(" ")) == 4 for l in txt.splitlines() if l.startswith("P ")), "FX3 the P rows carry chunks + the paid drop")
    # ---- fix round 2
    Sto.flushDirty()
    IO.drain()
    base = snapd(pl)
    # FX4 (critic: a crash inside the drop lost the rows): a spool that cannot be written -> '#ERROR' and NOTHING changed
    badf = os.path.join(scratch, "spool-file")
    open(badf, "w").write("x")
    t_bad = str(drop.apply(JArray(JObject)([W, Owner(), "Zone1_", os.path.join(badf, "x.spool")])))
    Sto.flushDirty()
    IO.drain()
    K.check(t_bad.startswith("#ERROR") and snapd(pl) == base and Reg.size(WF) == len(live0) and int(cs3.size()) == n3,
            "FX4 the spool cannot be written -> '#ERROR', no profile / registry record changed (%s)" % t_bad.strip()[:100])
    # FX4b: every row is in the spool (written before its step changed anything); the spool alone puts everything back
    sp = os.path.join(scratch, "spool", "explore.spool")
    txt4 = str(drop.apply(JArray(JObject)([W, Owner(), "Zone1_", sp])))
    r4 = sorted(l for l in txt4.splitlines() if l and not l.startswith("#"))
    s4 = sorted(l for l in open(sp, encoding="utf8").read().splitlines() if l and not l.startswith("#"))
    K.check(len(r4) == len(rows) and r4 == s4, "FX4 dropBox spools every row it returns (%d rows, spool %d)" % (len(r4), len(s4)))
    # FX5 (critic: the undo rewrote a file it could not read from an empty list): p3's chunk file unreadable (a folder in its place) ->
    # p3 is skipped whole (its other files untouched), every other row goes back, the answer is '#ERROR' (SkyyWorldGen keeps the rows)
    cf3 = os.path.join(pl, P3, "chunks", WF + ".bin")
    ch3_before = open(os.path.join(pl, P3, "chests.txt"), "rb").read()
    os.replace(cf3, cf3 + ".bak")
    os.makedirs(cf3)
    r5 = back.apply(JArray(JObject)([W, open(sp, encoding="utf8").read()]))
    Sto.flushDirty()
    IO.drain()
    K.check(str(r5).startswith("#ERROR") and int(cs3.size()) == n3 - len(ck3_in) and open(os.path.join(pl, P3, "chests.txt"), "rb").read() == ch3_before
            and os.path.isdir(cf3) and Reg.size(WF) == len(live0),
            "FX5 an unreadable profile file: that profile untouched (chunks %d, chests.txt same), the registry rows back, answer '%s'" % (int(cs3.size()), str(r5)[:90]))
    os.rmdir(cf3)
    os.replace(cf3 + ".bak", cf3)
    r6 = back.apply(JArray(JObject)([W, open(sp, encoding="utf8").read() + "\n" + txt4]))
    Sto.flushDirty()
    IO.drain()
    K.check(not str(r6).startswith("#") and int(cs3.size()) == n3 and int(Sto.paidHere(d3, WF)) == paid3 and int(d3.total) == tot3 and int(d3.chests) == chests3,
            "FX5 the retry (spool + answer, as SkyyWorldGen's next start) puts p3 back = before (%s)" % r6)
    after6 = snapd(pl)
    for f in base:
        if f.endswith(".bin"):
            a = sorted(struct.unpack(">q", base[f][i:i + 8])[0] for i in range(0, len(base[f]), 8))
            b = sorted(struct.unpack(">q", after6[f][i:i + 8])[0] for i in range(0, len(after6[f]), 8))
            K.check(a == b, "FX5 %s: the same chunk set after the retry" % f)
        elif f.endswith(".txt"):
            K.check(sorted(base[f].decode().splitlines()) == sorted(after6[f].decode().splitlines()), "FX5 %s: the same lines after the retry" % f)
    K.eq(int(back.apply(JArray(JObject)([W, open(sp, encoding="utf8").read()]))), 0, "FX5 a third restore adds nothing")
    K.save()


if __name__ == "__main__":
    HK.run("SkyyExploration", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("live", run_live), ("live2", run_zb)], __file__,
           live=(LIVE, "Skyy_SkyyExploration"))
