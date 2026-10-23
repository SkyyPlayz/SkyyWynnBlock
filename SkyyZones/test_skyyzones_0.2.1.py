"""Harness for SkyyZones 0.2.1 (round wg0710: zones:fn:dropBox / zones:fn:restoreBox for SkyyWorldGen 0.7.10's zone reset; tools/zones_0_2_1_patch.py).
Build first:  python tools/zones_0_2_1_patch.py && python SkyyZones/build_skyyzones_0.2.1.py
    python SkyyZones/test_skyyzones_0.2.1.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py; scratch tools/dev/scratch/wg0710/zh):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.2.0 -> 0.2.1: + ZBox; ZFn publish / unpublish; the version texts only
  X   exec     the REAL ZRegen / ZRw / ZBox on a scratch regen/ folder: a world with waiting blocks (D), grown-back checks (V) and recent
               spots inside and outside the reset zone (a java IntBinaryOperator owner, as SkyyWorldGen passes) -> dropBox forgets exactly the
               zone's entries WITHOUT a block write, journals an R line per waiting block, returns their lines; the rest untouched; a fresh
               snapshot; a restart reads the same; restoreBox puts every entry back (an entry the new land made at the same spot kept), the
               restart reads them; bad arguments -> null; the bridge keys are published / removed
  D   live     start twice on a scratch COPY of the live mods folder (the plugin's file start + the kit): only kit / SkyyZones files
  AA  audit    engine-access audit
"""
import os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.2.1", "0.2.0"
PKG = "com.skyy.zones."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyZones-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyZones-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wg0710", "zh")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
EXPECT = {"ZFn": ["~m publish", "~m unpublish"], "SkyyZonesPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
          "ZStore": ["~m parseAll"]}   # the version texts (ready line, export, the regions.properties warning)
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["ZBox"]
W = "skywynn_zones2"


def run_exec(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    J = lambda n: JClass(PKG + n)
    Regen, Box, Fn, Dep = J("ZRegen"), J("ZBox"), J("ZFn"), J("ZDep")
    Paths = JClass("java.nio.file.Paths")
    d = os.path.join(scratch, "regen")
    os.makedirs(d, exist_ok=True)
    now = 1792700000000
    Dep.CLOCK = now

    @JImplements("java.util.function.IntBinaryOperator")
    class Owner(object):
        def __init__(self):
            self.calls = 0

        @JOverride
        def applyAsInt(self, cx, cz):
            self.calls += 1
            return 1 if (-58 <= cx <= 13 and -16 <= cz <= 38) else 0     # Zone 1's land chunks (x -1854..410, z -485..1197)
    inside = [(-900, 70, 700), (-1000, 60, 600), (-500, 80, 400)]
    outside = [(-4224, 70, 384), (1280, 90, 4800), (5000, 60, 5000)]
    lines = ["D %d %d %d Ore_Iron_Stone iron %d 0 Rock_Bedrock" % (x, y, z, now + 60000) for x, y, z in inside + outside]
    lines += ["V -910 70 710 Rock_Stone stone %d 0 Rock_Bedrock" % (now - 1000), "V 1290 90 4810 Rock_Stone stone %d 0 Rock_Bedrock" % (now - 1000)]
    open(os.path.join(d, W + ".journal"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(d, "default.journal"), "w").write("D -900 70 700 Ore_Iron_Stone iron %d 0 Rock_Bedrock\n" % (now + 60000))
    r = str(Regen.start(Paths.get(d)))
    rw = Regen.rw(W, False)
    K.check(rw is not None and rw.dep.size() == 6 and rw.check.size() == 2, "X start: 6 waiting + 2 checked in %s (%s)" % (W, r))
    Fn.publish()
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    drop, back = br.get("zones:fn:dropBox"), br.get("zones:fn:restoreBox")
    K.check(drop is not None and back is not None and str(br.get("zones:version")) == VERSION, "X the bridge publishes zones:fn:dropBox / restoreBox")
    K.check(drop.apply(None) is None and drop.apply(JArray(JObject)([W])) is None and drop.apply(JArray(JObject)([W, "x"])) is None, "X bad arguments -> null")
    own = Owner()
    txt = str(drop.apply(JArray(JObject)([W, own])))
    got = [l for l in txt.splitlines() if l]
    K.eq(sorted(l.split(" ")[0] for l in got), ["D", "D", "D", "V"], "X dropBox returns the zone's 3 waiting + 1 checked spot")
    K.check(all(-58 <= int(l.split(" ")[1]) >> 5 <= 13 for l in got), "X ... all of them in the zone")
    K.check(rw.dep.size() == 3 and rw.check.size() == 1 and all(not bool(Regen.depleted(W, x, y, z)) for x, y, z in inside)
            and all(bool(Regen.depleted(W, x, y, z)) for x, y, z in outside), "X the zone's entries are forgotten (no longer depleted), the others still wait")
    K.check(Regen.rw("default", False).dep.size() == 1, "X another world is untouched")
    snap = open(os.path.join(d, W + ".snap")).read()
    K.check(not os.path.exists(os.path.join(d, W + ".journal")) or os.path.getsize(os.path.join(d, W + ".journal")) == 0, "X a fresh snapshot (the journal emptied)")
    K.check(all(("%d %d %d" % p) not in snap for p in inside) and all(("D %d %d %d" % p) in snap for p in outside), "X the snapshot holds only the outside entries")
    K.check(int(Box.DROPPED.get()) == 3, "X DROPPED counts the waiting blocks")
    Regen.shutdown()
    Regen.start(Paths.get(d))
    rw = Regen.rw(W, False)
    K.check(rw.dep.size() == 3 and rw.check.size() == 1, "X a restart reads the same 3 + 1")
    # a block the new land made waits at one of the old spots: kept on restore
    rw.dep.put(JClass("java.lang.Long").valueOf(Dep.key(-900, 70, 700)), Dep(-900, 70, 700, "Ore_Copper_Stone", "copper", "Rock_Bedrock", 0, now + 5000))
    n = back.apply(JArray(JObject)([W, txt]))
    K.eq(int(n), 3, "X restoreBox puts back 2 waiting + 1 checked (the spot already waiting is kept)")
    K.check(rw.dep.size() == 6 and rw.check.size() == 2 and str(rw.dep.get(JClass("java.lang.Long").valueOf(Dep.key(-900, 70, 700))).orig) == "Ore_Copper_Stone",
            "X after the undo: 6 waiting (3 outside, the new one kept, 2 back), 2 checked")
    Regen.shutdown()
    Regen.start(Paths.get(d))
    rw = Regen.rw(W, False)
    K.check(rw.dep.size() == 6 and rw.check.size() == 2, "X a restart after the undo reads them")
    K.eq(int(back.apply(JArray(JObject)(["new_world", "D 1 70 1 Rock_Stone stone 5 0 Rock_Bedrock\n"]))), 1, "X restoreBox into a world with no regen file yet")
    K.eq(str(drop.apply(JArray(JObject)(["nobody", own]))), "", "X dropBox on a world with no regrow file = empty")
    # fix round 2 (critic: a crash inside the drop lost the rows): every line is spooled (synced) BEFORE anything is dropped
    rw = Regen.rw(W, False)
    d0, c0 = int(rw.dep.size()), int(rw.check.size())
    badf = os.path.join(scratch, "zspool-file")
    open(badf, "w").write("x")
    t_bad = str(drop.apply(JArray(JObject)([W, own, os.path.join(badf, "z.spool")])))
    K.check(t_bad.startswith("#ERROR") and int(rw.dep.size()) == d0 and int(rw.check.size()) == c0, "FX2 the spool cannot be written -> '#ERROR', nothing dropped (%s)" % t_bad.strip()[:120])
    sp = os.path.join(scratch, "zspool", "zones.spool")
    t2 = str(drop.apply(JArray(JObject)([W, own, sp])))
    got2 = sorted(l for l in t2.splitlines() if l)
    sl = sorted(l for l in open(sp).read().splitlines() if l)
    K.check(len(got2) == 4 and got2 == sl and int(rw.dep.size()) == d0 - 3, "FX2 dropBox spools every line it drops (%d lines, spool %d)" % (len(got2), len(sl)))
    K.eq(int(back.apply(JArray(JObject)([W, open(sp).read()]))), 4, "FX2 the spool alone puts them back (a crash after the drop)")
    K.check(int(rw.dep.size()) == d0 and int(rw.check.size()) == c0, "FX2 ... every waiting block + checked spot is back")
    K.eq(int(back.apply(JArray(JObject)([W, open(sp).read() + "\n" + t2]))), 0, "FX2 spool + answer together (what SkyyWorldGen restores) add nothing twice")
    Fn.unpublish()
    K.check(br.get("zones:fn:dropBox") is None and br.get("zones:fn:restoreBox") is None, "X unpublish removes both keys")
    Regen.shutdown()
    K.save()


def snap(d):
    out = {}
    for base, _dirs, fs in os.walk(d):
        for f in fs:
            p_ = os.path.join(base, f)
            out[os.path.relpath(p_, d).replace(os.sep, "/")] = hashlib.sha1(open(p_, "rb").read()).hexdigest()
    return out


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Plug, CPub, Sto = (JClass(PKG + n) for n in ("SkyyZonesPlugin", "CfgPub", "ZStore"))
    Paths = JClass("java.nio.file.Paths")
    Sto.SYNC = True
    before = snap(home)

    def start():
        r = str(Plug.paths(Paths.get(os.path.join(home, "Skyy_SkyyZones"))))
        CPub.start(Paths.get(home), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones"))
        CPub.flush()
        CPub.shutdown()
        return r
    r1 = start()
    s1 = snap(home)
    r2 = start()
    s2 = snap(home)
    ch = sorted(f for f in before if s1.get(f) != before[f] and not f.startswith("Skyy_SkyyZones/"))
    K.check(not ch, "D start 1: every file outside Skyy_SkyyZones byte-identical (%s)" % ch[:5])
    K.check(s1 == s2, "D start 2 changes nothing (%s)" % sorted(f for f in set(s1) | set(s2) if s1.get(f) != s2.get(f)))
    K.notes.append("D: %s | %s" % (r1[:200], r2[:200]))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyZones", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("exec", run_exec), ("live", run_live)], __file__,
           live=(LIVE, "mods"))
