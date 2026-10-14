"""Harness for SkyyCollections 0.2.14 (SHARD CREDIT + REBIRTH RANKS; tools/collections_0_2_14_patch.py). Build first:
    python tools/collections_0_2_14_patch.py && python SkyyCollections/build_skyycollections_0.2.14.py

    python SkyyCollections/test_skyycollections_0.2.14.py [--jar <SkyyCollections-0.2.14.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises
  C   compare  0.2.13 -> 0.2.14: exactly the listed members differ, CollRebirth + CollShardMig added; non-class entries: manifest only
  X   exec     EVERY NEW CODE PATH: the default config text (marker, shard listed, rebirth.rankFactor), the loader (shard listed by default,
               rankFactor read + clamped), CollShardMig.update on the LIVE config.properties text (read only) and on every variant (0.2.1+ default,
               0.2 default, CRLF, already lists shard, hand-edited, missing, two lines, marked, empty), sameAfter; CollRebirth (rise from
               rebirth:fn:cap via the CAP_TEST seam, the 5 s / 0.25 s cache, need / ranks / maxText for 0 / 1 / 2 rebirths and clamps);
               creditShard skips cap.perMinute (capMinute vs creditShard on a real counts file), CollAddTask.shard dispatch
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyCollections (the setup sequence BagMigrate, BypassMig, loadAll, CobMig,
               SigMig, ShardMig): the 1st start appends ,shard to the untouched line once, keeps the old file in config-history byte for byte,
               writes the Undo row; the 2nd start changes nothing; shard is a source after the load
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.14"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards02", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")
OWNER = "0f0f0f0f-1111-2222-3333-444444444444"
# the members 0.2.14 changes (filled from the patch's own list: loader / credit path / page texts / the version texts)
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # CfgFile / configText: the default text
          "CollAddTask": ["+f shard", "~m run"], "CollCredit": ["+m creditShard", "+f SHARD_MAX", "~m creditOne"],
          "CollFn": ["+m creativeHere", "~m apply"], "CollPage": ["~m buildDetail", "~m card"], "CollReg": ["~m configText", "~m loadConfig"],
          "SkyyCollectionsPlugin": ["~m setup"]}
ADDED = ["CollRebirth", "CollShardMig"]


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JLong, JInt, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Util, Cred, Rb, Sm, Bp = (P("CollReg"), P("CollStore"), P("CollUtil"), P("CollCredit"), P("CollRebirth"), P("CollShardMig"), P("CollBypassMig"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    base = os.path.join(scratch, "x", "Skyy_SkyyCollections")
    os.makedirs(base)
    Reg.BASE = Paths.get(base)
    Store.DIR = Paths.get(base).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    cfg = open(os.path.join(base, "config.properties"), encoding="latin-1").read()
    lines = cfg.replace("\r\n", "\n").split("\n")
    K.check(str(Sm.MARK) in lines and lines.index(str(Sm.MARK)) == lines.index("bridge.add.sources=skills:double,skills:felled,shard") - 1
            and "rebirth.rankFactor=2" in lines, "X1: a fresh config.properties lists shard, carries the run-once marker right above it, and rebirth.rankFactor=2")
    K.check(Reg.ADD_SOURCES.contains("shard") and Reg.ADD_SOURCES.contains("skills:double") and Reg.ADD_SOURCES.contains("skills:felled"),
            "X1: the loader: shard is a coll:fn:add source by default")
    K.check(Sm.update(cfg) is None, "X1: a fresh file never updates (marker present)")
    # the loader: no line = the 0.2.14 default; rankFactor read and clamped
    f_ = os.path.join(base, "config.properties")
    for txt, want_shard, want_f in (("cap.perMinute=20000\n", True, 2.0), ("bridge.add.sources=skills:double\nrebirth.rankFactor=3.5\n", False, 3.5),
                                     ("rebirth.rankFactor=0.2\n", True, 1.1), ("rebirth.rankFactor=99\n", True, 10.0), ("rebirth.rankFactor=abc\n", True, 2.0)):
        open(f_, "w", encoding="latin-1").write(txt)
        Reg.loadConfig()
        K.check(bool(Reg.ADD_SOURCES.contains("shard")) == want_shard and abs(float(Rb.FACTOR) - want_f) < 1e-9,
                "X1: loader on %r: shard %s, rankFactor %s" % (txt.strip(), want_shard, want_f))
    open(f_, "w", encoding="latin-1").write(cfg)
    Reg.loadConfig()

    # ---- X2 CollShardMig.update on the live text (read only) and every variant
    def upd(t_):
        r_ = Sm.update(t_)
        return None if r_ is None else (str(r_[0]), str(r_[1]), str(r_[2]), [str(x) for x in r_[3]])

    def props(t_):
        pp = JClass("java.util.Properties")()
        pp.load(JClass("java.io.ByteArrayInputStream")(t_.encode("latin-1")))
        return dict((str(k), str(pp.getProperty(k))) for k in pp.stringPropertyNames())
    live_f = os.path.join(LIVE_DIR, "config.properties")
    live = open(live_f, "rb").read().decode("latin-1") if os.path.isfile(live_f) else "bridge.add.sources=skills:double\n"
    u_ = upd(live)
    pl0, pl1 = props(live), props(u_[0]) if u_ else {}
    old_v = pl0.get("bridge.add.sources")
    want = dict(pl0)
    if old_v in ("skills:double", "skills:double,skills:felled"):
        want["bridge.add.sources"] = old_v + ",shard"
    K.check(u_ is not None and pl1 == want and str(Sm.MARK) in u_[0].replace("\r\n", "\n").split("\n") and upd(u_[0]) is None
            and bool(Bp.sameAfter(live.encode("latin-1"), u_[0].encode("latin-1"), JArray(JString)(u_[3]))),
            "X2: the LIVE config.properties (%s): only bridge.add.sources changes (%s -> %s), the marker is added, sameAfter agrees, run again = nothing: %s"
            % ("found" if os.path.isfile(live_f) else "missing", old_v, pl1.get("bridge.add.sources"), u_[1] if u_ else None))
    v1 = upd("# head\ncap.perMinute=20000\n# sources\nbridge.add.sources=skills:double,skills:felled\nx=1\n")
    v2 = upd("bridge.add.sources=skills:double\r\nx=1\r\n")
    v3 = upd("bridge.add.sources=skills:double,shard\n")
    v4 = upd("bridge.add.sources=skills:double,minion\n")
    v5 = upd("x=1\n")
    v6 = upd("bridge.add.sources=skills:double\nbridge.add.sources=skills:double,skills:felled\n")
    v7 = upd("")
    v8 = upd("bridge.add.sources = skills:double,skills:felled\n")
    v9 = upd("bridge.add.sources=skills:double,\\\n  skills:felled\n")
    K.check(v1 is not None and v1[0].split("\n")[2] == str(Sm.MARK) and "bridge.add.sources=skills:double,skills:felled,shard" in v1[0].split("\n") and v1[3] == ["bridge.add.sources", "skills:double,skills:felled", "skills:double,skills:felled,shard"],
            "X2: the 0.2.1+ default gets ,shard; the marker goes above the line's comment run; one Undo row")
    K.check(v2 is not None and v2[0] == str(Sm.MARK) + "\r\nbridge.add.sources=skills:double,shard\r\nx=1\r\n", "X2: the 0.2 default (skills:double) gets ,shard; CRLF kept on every line: %r" % (v2[0] if v2 else None))
    K.check(v3 is not None and v3[3] == [] and v3[2] == "" and "bridge.add.sources=skills:double,shard" in v3[0], "X2: a list that already has shard: marker only, no change")
    K.check(v4 is not None and v4[3] == [] and "kept (an admin's list)" in v4[2] and "skills:double,minion" in v4[0], "X2: a hand-edited list is KEPT and named: %s" % (v4[2] if v4 else None))
    K.check(v5 is not None and v5[3] == [] and v5[0].startswith(str(Sm.MARK)), "X2: no line: marker only (the loader default lists shard)")
    K.check(v6 is not None and v6[3] == ["bridge.add.sources", "skills:double,skills:felled", "skills:double,skills:felled,shard"]
            and v6[0].split("\n")[1:3] == ["bridge.add.sources=skills:double", "bridge.add.sources=skills:double,skills:felled,shard"],
            "X2: two lines: the LAST one decides (Properties keeps it) and only lines with exactly that text change")
    K.check(v7 is not None and v7[0].startswith(str(Sm.MARK)) and v7[3] == [], "X2: an empty file: marker only")
    K.check(v8 is not None and "bridge.add.sources = skills:double,skills:felled,shard" in v8[0], "X2: the key, separator and spacing are kept")
    K.check(v9 is not None and v9[3] == [] and "skills:felled" in v9[0] and "shard" not in v9[0].replace(str(Sm.MARK), ""), "X2: a continued (multi-line) entry is never rewritten")
    K.check(not Bp.sameAfter(b"a=1\n", b"a=2\n", JArray(JString)([])), "X2: sameAfter refuses any other change")

    # ---- X3 CollRebirth: the rank cap rise per rebirth (rebirth:fn:cap kind "collection")
    @JImplements("java.util.function.Function")
    class Cap(object):
        def __init__(self):
            self.n = {}
            self.calls = []

        @JOverride
        def apply(self, a):
            self.calls.append((str(a[0]), str(a[1]), int(a[2])))
            k = str(a[0])
            if k not in self.n:
                return None
            return JInt(int(a[2]) + self.n[k])
    cap = Cap()
    Rb.CAP_TEST = cap
    Rb.CACHE.clear()
    cW = int(R.byId.get("wheat"))
    mx = int(Reg.maxTier(R, cW))
    last = int(Reg.threshold(R, cW, mx))
    K.eq(int(Rb.rise("p0")), 0, "X3: SkyyRebirth still reading the file (null) = no rise")
    K.check(cap.calls[-1] == ("p0", "collection", 100), "X3: asked as {pkey, collection, base}")
    cap.n["p0"] = 2
    K.eq(int(Rb.rise("p0")), 0, "X3: a null answer is cached only 0.25 s")
    Rb.CACHE.clear()
    K.eq(int(Rb.rise("p0")), 2, "X3: two rebirths = +2 ranks")
    nc = len(cap.calls)
    Rb.rise("p0")
    K.eq(len(cap.calls), nc, "X3: cached (5 s) - SkyyRebirth is not asked again")
    cap.n["big"] = 999
    K.eq(int(Rb.rise("big")), 50, "X3: the rise is clamped to 50")
    K.eq(int(Rb.rise(None)), 0, "X3: no key = 0")
    K.eq([int(Rb.need(R, cW, k)) for k in (1, 2)], [last * 2, last * 4], "X3: rebirth rank k needs the last tier's %d x 2^k" % last)
    K.eq([int(Rb.ranks(R, cW, x, "p0")) for x in (last - 1, last, last * 2 - 1, last * 2, last * 4, last * 100)], [0, 0, 0, 1, 2, 2],
         "X3: ranks reached for 0 / 2 rebirths (capped at the rise)")
    cap.n["p1"] = 1
    K.eq([int(Rb.ranks(R, cW, last * 100, k)) for k in ("p1", "none")], [1, 0], "X3: one rebirth caps at 1; no rebirth = 0")
    Rb.FACTOR = 3.0
    K.eq(int(Rb.need(R, cW, 1)), last * 3, "X3: rebirth.rankFactor 3")
    Rb.FACTOR = 2.0
    t0 = str(Rb.maxText(R, cW, last, None))
    ou = UUID.fromString(OWNER)
    Rb.CACHE.clear()
    t1 = str(Rb.maxText(R, cW, last, ou))
    cap.n[OWNER] = 2
    Rb.CACHE.clear()
    t2 = str(Rb.maxText(R, cW, last + 1, ou))
    t3 = str(Rb.maxText(R, cW, last * 4, ou))
    K.check(t0 == "MAXED" and t1 == "MAXED" and t2.startswith("Rebirth rank 1: ") and t2.endswith(" / " + str(Util.fmt(JLong(last * 2)))) and t3 == "MAXED - rebirth rank 2 of 2",
            "X3: the page text: MAXED without rebirths, 'Rebirth rank 1: n / next' while climbing, 'MAXED - rebirth rank 2 of 2' at the cap: %s | %s" % (t2, t3))
    K.check(str(Rb.maxText(None, 0, 0, ou)) == "MAXED", "X3: maxText never throws (no registry)")
    Rb.CAP_TEST = None
    Rb.CACHE.clear()
    K.eq(int(Rb.rise(OWNER)), 0, "X3: no SkyyRebirth on the bridge = today's caps")

    # ---- X4 the shard credit skips cap.perMinute (a real counts file; no player online = the quiet path)
    ou2 = UUID.fromString("0e0e0e0e-1111-2222-3333-555555555555")
    key = str(Util.pkey(ou2))
    Reg.CAP_MINUTE = 10
    Cred.MINUTE.clear()
    K.eq(int(Cred.capMinute(ou2, JLong(50))), 10, "X4: an ordinary credit is capped at cap.perMinute (10 here)")
    K.eq(int(Cred.capMinute(ou2, JLong(5))), 0, "X4: ... nothing more this minute")
    cWi = str(list(R.items[cW])[0])
    d0 = Store.dataK(key)
    s0 = int(Store.sum(d0, R, cW)) if d0 is not None else 0
    Cred.creditShard(None, ou2, key, cWi, JLong(200))
    d1 = Store.dataK(key)
    s1 = int(Store.sum(d1, R, cW)) if d1 is not None else -1
    K.check(s1 - s0 == 200, "X4: a shard credit of 200 lands although the minute cap (10) is used up: %d -> %d" % (s0, s1))
    Reg.CAP_CREDIT = 100   # fix4: a lowered cap.perCredit never cuts a shard chunk (SkyyShards clears what TRUE paid)
    Cred.creditShard(None, ou2, key, cWi, JLong(256))
    s15 = int(Store.sum(Store.dataK(key), R, cW))
    Reg.CAP_CREDIT = 256
    K.check(s15 - s1 == 256 and int(Cred.SHARD_MAX) == 256, "X4 fix4: cap.perCredit 100 does NOT cut a shard chunk of 256: +%d (SHARD_MAX %d)" % (s15 - s1, int(Cred.SHARD_MAX)))
    Cred.creditShard(None, ou2, key, cWi, JLong(1000))
    s2 = int(Store.sum(Store.dataK(key), R, cW))
    K.check(s2 - s15 == 256, "X4: a shard credit is bounded by SHARD_MAX 256 (coll:fn:add refuses bigger chunks with FALSE first): +%d" % (s2 - s15))
    Reg.CAP_MINUTE = 20000
    at = P("CollAddTask")(ou2, key, cWi, JLong(5))
    at.shard = True
    at.run()          # no Universe in a bare JVM: the task stops at the player lookup (WARN), never credits twice
    K.check(bool(at.shard) and int(Store.sum(Store.dataK(key), R, cW)) == s2, "X4: CollAddTask with shard set runs (bare JVM: no player, nothing credited)")
    # fix3: a creative player's shard credit is refused on the caller's thread (SkyyShards keeps it owed); no store / no ref = not creative
    K.check(not bool(P("CollFn").creativeHere(None, None)) and not bool(P("CollFn")("add").apply(JArray(JObject)([ou2, JString(str(cWi)), JLong(5), JString("shard"), JString(key)]))),
            "X4 fix3: CollFn.creativeHere(no store) = false; coll:fn:add shard without a live player = FALSE (never TRUE then dropped)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Sm = P("CollReg"), P("CollStore"), P("CollShardMig")
    Paths = JClass("java.nio.file.Paths")
    b_ = Paths.get(home)
    cf = os.path.join(home, "config.properties")
    old = open(cf, "rb").read()

    def hist():
        d_ = os.path.join(home, "config-history")
        out_ = []
        for r_, _d, fs_ in os.walk(d_):
            for f_ in fs_:
                out_.append(open(os.path.join(r_, f_), "rb").read())
        return out_
    msgs, snaps = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        Reg.loadAll()
        P("CollCobMig").run(b_)
        P("CollSigMig").run(b_)
        msgs.append(str(Sm.run(b_)))
        Reg.loadAll()
        snaps.append(HK.tree_hash(home))
    new = open(cf, "rb").read()
    h1 = hist()
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else ""
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.14" in l_]
    K.check(msgs[0].startswith("config.properties:") and msgs[1] == "" and snaps[0] == snaps[1],
            "D: the 1st start updates config.properties once, the 2nd start changes nothing: %s" % msgs)
    K.check(new != old and any(h_ == old for h_ in h1) and Reg.ADD_SOURCES.contains("shard")
            and (len(rows) >= 1 or "kept" in msgs[0] or "already" in msgs[0]),
            "D: the old file is kept in config-history (byte for byte), %d Undo row(s), shard is a source after the load" % len(rows))
    K.check(len(new) - len(old) < 400 and new.replace(b"\r\n", b"\n").count(b"\n") == old.replace(b"\r\n", b"\n").count(b"\n") + 1,
            "D: exactly one line more (the marker), the rest byte for byte except the updated value")
    K.notes.append("D: %s" % msgs[0])
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
