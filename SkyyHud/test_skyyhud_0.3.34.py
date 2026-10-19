"""SkyyHud 0.3.34 harness - minimap pictures sent slower and without bursts (beta bug 4 = lag; tools/hud_0_3_34_patch.py).
Built on tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir
in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.34.py [--jar SkyyHud-0.3.34.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.33 -> 0.3.34: exactly the listed classes / members differ (MmCfg: default 6 + tilesPerSecond; Minimap: rateOk + assign;
                MmSess: the send ring; HudCfg.load runs HudMig34; the new class HudMig34)
  Q34  speed    HudMig34.update on texts: an untouched 24 -> 6 (value only, the marker on its own line right above it, every other byte and
                LF / CRLF kept); an admin's value kept (+ its INFO note); 6 already / no line = marker only; the last of two entries
                decides; a continued line kept; the marker present or the fresh default file = nothing. HudMig34.run on a scratch file:
                History copy (byte-equal), config-changes.log line (row key, Undo-able), the file rewritten once, a second run = nothing.
                HudCfg.load: a fresh file is written with the marker and never migrated; an old file is moved and read as 6.
                MmCfg.loadFrom: defaults 6 / 16, bounds. Minimap.rateOk: at most N new pictures in ANY 1 s (sliding), 1 and 96, a live
                change, a clock step back never blocks.
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the client log's AddOrUpdate rate, FPS / video-memory evictions, the fill feel at 16 a second.
Scratch: tools/dev/scratch/hud34/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HK
import skyybuild as B

VERSION, PREV = "0.3.34", "0.3.33"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud34", "h")))
PKG = "com.skyy.hud."


def run_q34(out, jar, scratch, home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    K = HK.Child(out)
    H = lambda n: JClass(PKG + n)
    Mig, Cfg, Mm, Map, Sess = H("HudMig34"), H("HudCfg"), H("MmCfg"), H("Minimap"), H("MmSess")
    Paths, Props = JClass("java.nio.file.Paths"), JClass("java.util.Properties")
    MARK = str(Mig.MARK)
    NEW_DEF = str(Cfg.DEFAULT_TEXT)
    K.check(NEW_DEF.count(MARK) == 1 and "\n%s\nmm.tilesPerTick=6\n" % MARK in NEW_DEF and "\nmm.tilesPerSecond=16\n" in NEW_DEF,
            "Q34 the fresh default file: marker right above mm.tilesPerTick=6, mm.tilesPerSecond=16")
    # the 0.3.33 file as Skyy's server has it (the 0.3.33 default text: no marker, 24, no tilesPerSecond, the old comment line)
    OLD_DEF = NEW_DEF.replace(MARK + "\n", "").replace("mm.tilesPerTick=6\n", "mm.tilesPerTick=24\n").replace("mm.tilesPerSecond=16\n", "")
    OLD_DEF = OLD_DEF.replace("# (1-64; up to 3x while several fill); mm.tilesPerSecond = new map pictures sent to one player in any second (1-96);\n"
                              "# mm.partyDots / mm.otherPlayers = dots allowed; mm.disabledWorlds = comma\n",
                              "# (1-64; up to 3x while several fill); mm.partyDots / mm.otherPlayers = dots allowed; mm.disabledWorlds = comma\n")
    K.check("mm.tilesPerTick=24\n" in OLD_DEF and MARK not in OLD_DEF and "tilesPerSecond" not in OLD_DEF, "Q34 the 0.3.33-style file built")

    def upd(t):
        r = Mig.update(t)
        if r is None:
            return None
        return str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]]

    # 1. untouched 24 -> 6, LF
    r = upd(OLD_DEF)
    K.check(r is not None and "mm.tilesPerTick 24 -> 6" == r[1] and r[3] == ["hud.mm.tilesPerTick", "24", "6", "mm.tilesPerTick"] and not r[2],
            "Q34 untouched 24 -> 6: %r" % ((r and r[1:]),))
    K.eq(r[0], OLD_DEF.replace("mm.tilesPerTick=24\n", MARK + "\nmm.tilesPerTick=6\n"), "Q34 ... only that value + the marker line right above it (LF)")
    # 2. CRLF kept
    crlf = OLD_DEF.replace("\n", "\r\n")
    r = upd(crlf)
    K.eq(r[0], crlf.replace("mm.tilesPerTick=24\r\n", MARK + "\r\nmm.tilesPerTick=6\r\n"), "Q34 ... CRLF file: CRLF kept on every line")
    # 3. an admin's value kept
    r = upd(OLD_DEF.replace("mm.tilesPerTick=24\n", "mm.tilesPerTick=12\n"))
    K.check(r[1] == "" and len(r[2]) == 1 and "mm.tilesPerTick=12 kept" in r[2][0] and r[3] == [], "Q34 an admin's 12 kept + noted: %s" % r[2])
    K.check("mm.tilesPerTick=12\n" in r[0] and r[0].count(MARK) == 1, "Q34 ... value unchanged, marker added")
    # 4. 6 already / no line
    r = upd(OLD_DEF.replace("mm.tilesPerTick=24\n", "mm.tilesPerTick = 6\n"))
    K.check(r[1] == "" and not r[2] and "mm.tilesPerTick = 6\n" in r[0], "Q34 6 already: nothing moved, no note")
    t = "defaultLayout=\nmm.enabled=true\n"
    r = upd(t)
    K.eq(r[0], MARK + "\n" + t, "Q34 no mm.tilesPerTick line: only the marker (line 0) - the code default 6 applies")
    # 5. the last entry decides; a continued line is an admin's
    r = upd("mm.tilesPerTick=24\nmm.tilesPerTick=10\n")
    K.check(r[1] == "" and len(r[2]) == 1 and r[0].endswith("mm.tilesPerTick=24\nmm.tilesPerTick=10\n"), "Q34 two entries, the last 10: kept, nothing rewritten")
    r = upd("mm.tilesPerTick=2\\\n4\n")
    K.check(r[1] == "" and len(r[2]) == 1 and "mm.tilesPerTick=2\\\n4\n" in r[0], "Q34 a continued line (=24 over 2 lines): kept")
    r = upd("mm.tilesPerTick=10\nmm.tilesPerTick=24\n")
    K.check(r[1] == "mm.tilesPerTick 24 -> 6" and r[0] == MARK + "\nmm.tilesPerTick=10\nmm.tilesPerTick=6\n", "Q34 two entries, the last 24: only the last moves (marker above the first)")
    # comment run above: the marker goes above the comments on top of the entry
    r = upd("a=1\n# about it\n# more\nmm.tilesPerTick=24\n")
    K.eq(r[0], "a=1\n" + MARK + "\n# about it\n# more\nmm.tilesPerTick=6\n", "Q34 the marker goes above the comment run on top of the entry")
    # 6. run once
    K.check(upd(r[0]) is None, "Q34 the marker present -> nothing (run once)")
    K.check(upd(NEW_DEF) is None, "Q34 the fresh default file -> nothing (never migrated)")
    K.check(Mig.sameAfter(OLD_DEF.encode("latin-1"), upd(OLD_DEF)[0].encode("latin-1"), ["hud.mm.tilesPerTick", "24", "6", "mm.tilesPerTick"]),
            "Q34 sameAfter: only the moved key differs")
    K.check(not Mig.sameAfter(b"a=1\nb=2\n", b"a=1\nb=3\n", ["hud.mm.tilesPerTick", "24", "6", "mm.tilesPerTick"]), "Q34 sameAfter refuses any other change")

    # 7. run() on a scratch file (History first, change log, once)
    d = os.path.join(scratch, "q34", "mods", "Skyy_SkyyHud")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "config.properties")
    old_b = crlf.encode("latin-1")
    open(f, "wb").write(old_b)
    msg = str(Mig.run(Paths.get(f)))
    new_b = open(f, "rb").read()
    K.check("mm.tilesPerTick 24 -> 6" in msg, "Q34 run(): INFO line: %s" % msg[:120])
    K.eq(new_b, crlf.replace("mm.tilesPerTick=24\r\n", MARK + "\r\nmm.tilesPerTick=6\r\n").encode("latin-1"), "Q34 run(): the file rewritten, bytes + CRLF kept")
    hd = os.path.join(d, "config-history")
    baks = [x for x in os.listdir(hd) if x.endswith(".bak")] if os.path.isdir(hd) else []
    K.check(len(baks) == 1 and open(os.path.join(hd, baks[0]), "rb").read() == old_b, "Q34 run(): one History copy, byte-equal to the old file: %s" % baks)
    idx = open(os.path.join(hd, "index.log"), encoding="utf8").read() if os.path.isfile(os.path.join(hd, "index.log")) else ""
    K.check("before the 0.3.34 minimap speed update" in idx, "Q34 run(): History index names the update")
    cl = open(os.path.join(d, "config-changes.log"), encoding="utf8").read() if os.path.isfile(os.path.join(d, "config-changes.log")) else ""
    lines = [x for x in cl.split("\n") if x]
    K.check(len(lines) == 1 and lines[0].split("\t")[1:] == ["SkyyHud 0.3.34", "-", "update", "hud.mm.tilesPerTick", "24", "6", "ok"],
            "Q34 run(): one config-changes.log line, row key, status ok (Undo-able): %s" % lines)
    K.eq(str(Mig.run(Paths.get(f))), "", "Q34 run() again: nothing (the marker)")
    K.eq(open(f, "rb").read(), new_b, "Q34 ... file untouched the second time")
    K.eq(str(Mig.run(Paths.get(os.path.join(d, "missing.properties")))), "", "Q34 run() on no file: nothing")

    # 8. HudCfg.load: fresh file -> written with the marker, not migrated; old file -> moved, read as 6
    d2 = os.path.join(scratch, "q34", "mods2", "Skyy_SkyyHud")
    os.makedirs(d2, exist_ok=True)
    f2 = os.path.join(d2, "config.properties")
    Cfg.FILE = Paths.get(f2)
    try:
        Cfg.load()
        K.eq(open(f2, "rb").read(), NEW_DEF.encode("latin-1"), "Q34 HudCfg.load on no file: the fresh default (with the marker), untouched")
        K.check(int(Mm.TILES_PER_TICK) == 6 and int(Mm.TILES_PER_SEC) == 16, "Q34 ... read as 6 / 16")
        K.check(not os.path.isdir(os.path.join(d2, "config-history")), "Q34 ... no History copy (not migrated)")
        open(f2, "wb").write(OLD_DEF.encode("latin-1"))
        Mm.TILES_PER_TICK = 24
        Cfg.load()
        K.check("mm.tilesPerTick=6\n" in open(f2, encoding="latin-1").read() and int(Mm.TILES_PER_TICK) == 6, "Q34 HudCfg.load on a 0.3.33 file: moved, read as 6")
    except Exception as e:
        K.check(False, "Q34 HudCfg.load threw: %s" % e)

    # 9. MmCfg.loadFrom
    p = Props()
    Mm.loadFrom(p)
    K.check(int(Mm.TILES_PER_TICK) == 6 and int(Mm.TILES_PER_SEC) == 16, "Q34 loadFrom: missing keys = 6 / 16")
    for v, want in (("0", 16), ("97", 16), ("x", 16), ("1", 1), ("96", 96), (" 40 ", 40)):
        p.setProperty("mm.tilesPerSecond", v)
        Mm.loadFrom(p)
        K.eq(int(Mm.TILES_PER_SEC), want, "Q34 loadFrom mm.tilesPerSecond=%r -> %d" % (v, want))
    p.setProperty("mm.tilesPerTick", "65")
    Mm.loadFrom(p)
    K.eq(int(Mm.TILES_PER_TICK), 6, "Q34 loadFrom mm.tilesPerTick out of range -> 6")

    # 10. rateOk: a sliding 1 s window
    def sess():
        return Sess(None)
    Mm.TILES_PER_SEC = 16
    s = sess()
    t0 = 50000000
    got = [bool(Map.rateOk(s, t0 + 10 * i)) for i in range(17)]
    K.check(all(got[:16]) and not got[16], "Q34 rateOk: 16 in 160 ms pass, the 17th waits")
    K.check(not Map.rateOk(s, t0 + 999), "Q34 ... still waiting 999 ms after the first")
    K.check(Map.rateOk(s, t0 + 1000), "Q34 ... one more 1000 ms after the first")
    K.check(not Map.rateOk(s, t0 + 1005), "Q34 ... the next only when the second leaves the window (sliding, no burst)")
    K.check(Map.rateOk(s, t0 + 1010), "Q34 ... and it does at 1010")
    # never more than 16 in ANY 1 s over a long steady stream
    s = sess()
    sent = []
    for ms in range(0, 10000, 50):
        for _ in range(5):
            if Map.rateOk(s, t0 + ms):
                sent.append(ms)
    worst = max(sum(1 for x in sent if a <= x < a + 1000) for a in range(0, 9000, 50))
    K.check(worst == 16 and len(sent) >= 150, "Q34 ... 10 s of demand: at most 16 in any 1 s window (worst %d, %d sent)" % (worst, len(sent)))
    Mm.TILES_PER_SEC = 1
    s = sess()
    K.check(Map.rateOk(s, t0) and not Map.rateOk(s, t0 + 500) and Map.rateOk(s, t0 + 1000), "Q34 ... cap 1")
    Mm.TILES_PER_SEC = 96
    s = sess()
    got = [bool(Map.rateOk(s, t0)) for i in range(97)]
    K.check(all(got[:96]) and not got[96], "Q34 ... cap 96 (the ring's size)")
    Mm.TILES_PER_SEC = 4     # a live lower cap counts the sends already made
    K.check(not Map.rateOk(s, t0 + 10), "Q34 ... a live change to 4 after 96 sends: waits")
    K.check(Map.rateOk(s, t0 - 5000), "Q34 ... a clock step back never blocks")
    Mm.TILES_PER_SEC = 999
    K.eq(int(Mm.tilesPerSecond()), 96, "Q34 tilesPerSecond() clamps to 96")
    Mm.TILES_PER_SEC = 16
    K.save()


EXPECT = {
    "MmCfg": ["+f TILES_PER_SEC", "+m tilesPerSecond", "~<clinit>", "~m loadFrom"],
    "Minimap": ["+m rateOk", "~m assign"],
    "MmSess": ["+f held", "+f ri", "+f rt", "~c "],
    "HudCfg": ["~m load", "~m writeDefaults"],     # writeDefaults: the DEFAULT_TEXT constant (marker, 6, mm.tilesPerSecond) is inlined
    "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],     # the kit's row table + default file (the new row)
    "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
}

if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD, PKG, SCRATCH, EXPECT, ["HudMig34"], [("q34", run_q34)], os.path.abspath(__file__))
