"""Harness for SkyyWorldGen 0.7.12 (hotfix leadfix: Lead / Chromium / Slag / Zone 5 Mithril + Titanium veins no longer solid sheets;
tools/worldgen_0_7_12_patch.py). Build first:
    python tools/worldgen_0_7_12_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.12.py

    python SkyyWorldGen/test_skyyworldgen_0.7.12.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; scratch tools/dev/scratch/leadfix/h):
  A    verify     every class loads + initialises with -Xverify:all
  C    compare    0.7.11 -> 0.7.12: only WgZ2Isles' mirror members change
  M    mirror     the REAL WgZ2Isles.mirror() (both jars) on synthetic chunks holding vanilla-shaped veins (one ore core voxel + its
                  6-voxel cracked shell per 8^3 cell): 0.7.11 turns core AND shell into the new ore (ROOT CAUSE: 7 ore blocks per
                  copied vein); 0.7.12 turns only the core into the new ore and the shell into its plain parent; the boost copies
                  keep the vanilla shell block; a shell copy never covers a copied ore voxel; the build-time shell table is vanilla's
  AA   audit      the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION = "0.7.12"
OLD_VERSION = "0.7.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "leadfix", "h")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
ADDED = []
EXPECT = {
    "WgZ2Isles": ["+f MR_ENC", "+f MR_ENC_NAMES", "+f MR_SHELL", "~<clinit>", "~m mirText", "~m mirror", "~m mrIds"],
    # the version text only (VERSION is baked into these strings; tools/soundpass_gen.Patch proves no other change outside the mirror)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyWorldGenPlugin": ["~m setup"], "WgCfg": ["~m load", "~m reloadAll"],
    "WgStore": ["~m markCreated"], "WgZSeed": ["~m save"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

if HK.arg("--phase") == "compare":
    import zipfile
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

CORE, SHELLB, HOST, PARENT, O1, O2 = 500, 501, 8, 9, 600, 700
NB = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def mirror_child(out, jar, is_new):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST])
    import jpype
    from jpype import JClass, JArray, JInt
    Isl = JClass(PKG + "WgZ2Isles")
    # a GeneratedChunk whose getState needs no running server (LegacyModule) - as the 0.7.3 harness did
    pool = JClass("javassist.ClassPool")(True)
    Ctc, Ctm = JClass("javassist.CtNewConstructor"), JClass("javassist.CtNewMethod")
    nm = PKG + "LfNoState%s" % ("New" if is_new else "Old")       # harness-only class, defined next to WgZ2Isles (never in a jar)
    nsc = pool.makeClass(nm, pool.get("com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk"))
    nsc.addConstructor(Ctc.make("public LfNoState%s() { super(); }" % ("New" if is_new else "Old"), nsc))
    nsc.addMethod(Ctm.make("public com.hypixel.hytale.component.Holder getState(int x, int y, int z) { return null; }", nsc))
    nsc.toClass(Isl.class_)
    GCc = JClass(nm)
    IA = JArray(JInt)
    R = {}
    if is_new:
        names = [str(x) for x in Isl.MR_SRC_NAMES]
        encs = [str(x) for x in Isl.MR_ENC_NAMES]
        shells = dict((n, e) for n, e in zip(names, encs) if e)
        K.eq(shells, {"Ore_Thorium_Mud_Cracked": "Soil_Mud_Dry", "Ore_Cobalt_Slate_Cracked": "Rock_Slate",
                      "Ore_Adamantite_Magma_Cracked": "Rock_Magma_Cooled"}, "M the shell table (vanilla's cracked shells -> their parents)")
        K.check(all(not e or n.endswith("_Cracked") for n, e in zip(names, encs)) and len(names) == len(encs),
                "M every real ore source (Ore_Thorium_Mud, Ore_Cobalt_Slate, Ore_Adamantite_Magma ...) stays ore: %d sources" % len(names))
        R["shells"] = shells
    nr = int(Isl.MR_N)
    mrn = [str(x) for x in Isl.MR_NAME]
    # synthetic ids: every rule's sources = CORE (real ore) + SHELLB (vanilla's shell), its new blocks O1 + r / O2 + r, host = 8
    Isl.MR_SRC = JArray(IA)([IA([CORE, SHELLB]) for _r in range(nr)])
    Isl.MR_HOST = JArray(IA)([IA([HOST, PARENT]) for _r in range(nr)])
    Isl.MR_O1 = IA([O1 + r if str(Isl.MR_O1_NAMES[r]) else -1 for r in range(nr)])
    Isl.MR_O2 = IA([O2 + r if str(Isl.MR_O2_NAMES[r]) else -1 for r in range(nr)])
    if is_new:
        Isl.MR_ENC = JArray(IA)([IA([0, PARENT]) for _r in range(nr)])
    sm = [0] * 800
    sm[CORE] = sm[SHELLB] = 1
    Isl.SRCMAP = JArray(jpype.JByte)(sm)
    cover = int(Isl.ORE_COVER)

    def run(r, zone, spots, collide=False):
        g = GCc()
        b = g.getBlockChunk()
        bot = IA([0] * (34 * 34))
        tb = IA([140] * (32 * 32))
        isl = IA([zone] * (34 * 34))
        res = {"core_src": 0, "shell_src": 0, "o_new": 0, "o_new_bad": 0, "parent": 0, "parent_bad": 0, "boost_core": 0, "boost_shell": 0,
               "covered": 0}
        for bx, bz in spots:
            for y in range(0, 141):
                for x in range(32):
                    for z in range(32):
                        b.setBlock(x, y, z, HOST, 0, 0)
            cores, shells = set(), set()
            for cy in range(2, 15):
                c = (4, cy * 8 + 4, 4)
                cores.add(c)
                for d in NB:
                    shells.add((c[0] + d[0], c[1] + d[1], c[2] + d[2]))
                if collide:       # a shell voxel whose slot-1 copy lands on the core's slot-0 copy (31-x, z)
                    shells.add((31 - 4, cy * 8 + 4, 31 - 4))
            for p in cores:
                b.setBlock(p[0], p[1], p[2], CORE, 0, 0)
            for p in shells:
                b.setBlock(p[0], p[1], p[2], SHELLB, 0, 0)
            res["core_src"] += len(cores)
            res["shell_src"] += len(shells)
            Isl.mirror(g, b, bx, bz, bot, tb, isl)

            def refl(s):
                o = set()
                for (x, y, z) in s:
                    o |= {(31 - x, y, z), (x, y, 31 - z), (31 - x, y, 31 - z)}
                return o
            rc, rs = refl(cores), refl(shells)
            for y in range(0, 141):
                for x in range(32):
                    for z in range(32):
                        v = int(b.getBlock(x, y, z))
                        p = (x, y, z)
                        if v in (O1 + r, O2 + r):
                            res["o_new"] += 1
                            res["o_new_bad"] += 0 if p in rc or (not is_new and p in rs) else 1
                        elif v == PARENT:
                            res["parent"] += 1
                            res["parent_bad"] += 0 if p in rs else 1
                        elif v == CORE and p not in cores:
                            res["boost_core"] += 1
                        elif v == SHELLB and p not in shells:
                            res["boost_shell"] += 1
                        if collide and p in rc and p in rs and v != O1 + r and v != O2 + r:
                            res["covered"] += 1
        return res
    spots = [(0, 0), (32, 0), (0, 32), (512, 96), (-64, -64), (1024, 2048), (96, -320), (-640, 288), (4096, 32), (-32, 4096), (160, 160), (-2048, -1024)]
    th = mrn.index("thorium")
    R["thorium"] = run(th, int(Isl.MR_ISL[th]), spots)
    R["cobalt"] = run(mrn.index("cobalt"), int(Isl.MR_ISL[mrn.index("cobalt")]), spots)
    R["adamantite5"] = run(mrn.index("adamantite5"), int(Isl.MR_ISL[mrn.index("adamantite5")]), spots)
    # the collision scene: every slot makes the new ore (no boost; F_LEAD high -> normalised to 1/3 each... x3 = every slot)
    Isl.B_THORIUM, Isl.F_LEAD = 1.0, 3.0
    R["collide"] = run(th, int(Isl.MR_ISL[th]), spots[:4], collide=True)
    Isl.B_THORIUM, Isl.F_LEAD = 1.15, 0.85
    R["text"] = str(Isl.mirText())
    t = R["thorium"]
    ratio = float(t["o_new"]) / max(1, t["core_src"])
    if is_new:
        for k in ("thorium", "cobalt", "adamantite5"):
            m = R[k]
            K.check(m["o_new"] > 0 and m["o_new_bad"] == 0 and m["parent"] > 0 and m["parent_bad"] == 0,
                    "M 0.7.12 %s: new ore only at the reflected CORE spots (%d, %d elsewhere), the shell copies are its plain parent (%d, %d elsewhere)"
                    % (k, m["o_new"], m["o_new_bad"], m["parent"], m["parent_bad"]))
        K.check(0.5 < ratio < 1.6, "M 0.7.12 thorium: new-ore blocks per vanilla ore core voxel %.2f (want ~0.85 x 1.15 = 0.98)" % ratio)
        K.check(t["boost_shell"] > 0 and t["boost_core"] > 0, "M 0.7.12 thorium: boost copies keep vanilla's own core + cracked shell (%d / %d)"
                % (t["boost_core"], t["boost_shell"]))
        c = R["collide"]
        K.check(c["covered"] == 0 and c["o_new"] > 0, "M 0.7.12 a shell copy never covers a copied ore voxel (%d covered, %d ore)" % (c["covered"], c["o_new"]))
        K.check("plain shell blocks" in R["text"], "M mirText names the shell blocks: %s" % R["text"][:200])
    else:
        sh = float(t["o_new"]) / max(1, t["core_src"])
        K.check(sh > 4.0 and t["parent"] == 0, "M ROOT CAUSE 0.7.11 thorium: %.2f new-ore (Lead) blocks per vanilla core voxel - the shell became ore too" % sh)
    K.notes.append(json.dumps(R))
    K.save(r=R)


def run_mirror(out, jar, scratch, home):
    mirror_child(out, jar, True)


def run_mirror_old(out, jar, scratch, home):
    mirror_child(out, OLD_JAR, False)


if __name__ == "__main__":
    HK.run("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("mirror", run_mirror), ("mirrorold", run_mirror_old)], __file__)
