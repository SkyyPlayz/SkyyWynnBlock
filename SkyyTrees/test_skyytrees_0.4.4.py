"""Harness for SkyyTrees 0.4.4 (Balance P4 Part 4, the SkyyTrees part: five per-rank numbers + T7's at most 5 class-tree ranks on one
(ability, modifier); tools/trees_0_4_4_patch.py + tools/trees_v3_data.py). Build first:
    python tools/trees_0_4_4_patch.py && python SkyyTrees/build_skyytrees_0.4.4.py
    python SkyyTrees/test_skyytrees_0.4.4.py [--dir <empty folder inside tools/dev/scratch/>]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A    verify   every class loads + initialises
  C    compare  0.4.3 -> 0.4.4: exactly the planned members (EXPECT)
  OLD  the 0.4.3 jar's TreeV3 tables (dumped in its own JVM)
  DATA every TreeV3 table vs 0.4.3: the row gates did not move; UMAX differs exactly at the 28 T7 upgrades (= tools/trees_v3_data.py
       T7_MAX); the five P4 upgrades send their new per-rank value (tree:fn:abil "f.<code>=" EXECUTED on a fake player at max ranks); their
       texts say it; no (ability, modifier) over 5 ranks in the jar's own tables
  CLAMP a player file holding the OLD max on a lowered upgrade (Spellblade Arcane Breach Power b2.r1a = 5) reads as the new max 1 and the
       4 points are unspent again (TreeStore.readFile -> TreeV3.spent); the other ranks untouched
  LIVE START TWICE on a scratch COPY of the live Skyy_SkyyTrees folder: nothing new written; LIVE2 = the same player files as the pinned
       0.4.3 writes, unless a live player owns ranks above a T7 max (then those keys only, listed)
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): the effects (SkyyClasses 0.1.44 harness), the page look.
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS
import trees_v3_data as V3D

VERSION = "0.4.4"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.4.3.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "balp4b", "trees")))
LIVE_DIR = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = []
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyTreesPlugin": ["~m setup"], "TreeCfg": ["~m load"],   # the version text
    "TreeV3": ["+f UOLD", "~<clinit>"],                                          # UMAX (T7) + the fx per-rank values + UTEXT; fix2: UOLD
    "TreeV3Mig": ["~m readV3"],                                                  # fix2: a clamp grandfathers the lines it would shut
}
P4_FX = {"Warrior.b1.r5b": ("drStill", 3.0, 5.0), "Archer.b1.r5b": ("dmgFocus", 1.0, 2.0), "Assassin.b2.r5b": ("dmgElite", 3.0, 5.0),
         "Spellblade.b3.r1a": ("momChance", 12.0, 20.0), "Monk.b1.r1a": ("move", 3.0, 4.0)}
TABLES = ("GATES", "UMAX", "UCOST", "UKEY", "UTEXT", "UNAME", "UHK", "UROW", "TU0", "TUN", "TNAME", "RNUM")


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def dump(V):
    o = {}
    for n in TABLES:
        o[n] = [int(y) if isinstance(y, int) else str(y) for y in getattr(V, n)]
    return o


def ukey(cls_branch_id):
    t, b, i = cls_branch_id.split(".")
    return "Class.%s.%s.%s" % (t, b, i)


def setup_dirs(J, base):
    from jpype import JClass
    Paths = JClass("java.nio.file.Paths")
    os.makedirs(os.path.join(base, "players"), exist_ok=True)
    J("TreeStore").DIR = Paths.get(os.path.join(base, "players"))
    J("TreeCfg").FILE = Paths.get(os.path.join(base, "trees.properties"))
    J("TreeStore").DATA.clear()
    J("TreeStore").DIRTY.clear()


def run_old(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    o = dump(JClass(PKG + "TreeV3"))
    json.dump(o, open(os.path.join(scratch, "old043.json"), "w"))
    K.check(len(o["GATES"]) == 19 * 8 and len(o["UMAX"]) == len(o["UKEY"]) > 0, "OLD the 0.4.3 TreeV3 tables read (%d upgrades)" % len(o["UKEY"]))
    K.save()


def run_data(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    V = JClass(PKG + "TreeV3")
    o, n = json.load(open(os.path.join(scratch, "old043.json"))), dump(V)
    K.eq(n["GATES"], o["GATES"], "DATA the row gates of all 19 trees did not move")
    K.eq(n["UKEY"], o["UKEY"], "DATA the same upgrade keys in the same order (saved ids unchanged)")
    for t in ("UCOST", "UHK", "UROW", "TU0", "TUN", "TNAME", "RNUM"):
        K.eq(n[t], o[t], "DATA %s unchanged" % t)
    moved = dict((n["UKEY"][i], (o["UMAX"][i], n["UMAX"][i])) for i in range(len(n["UKEY"])) if n["UMAX"][i] != o["UMAX"][i])
    K.eq(moved, dict((ukey(k), tuple(v)) for k, v in V3D.T7_MAX.items()), "DATA UMAX differs exactly at the %d T7 upgrades (old -> new)" % len(V3D.T7_MAX))
    txt = sorted(n["UKEY"][i] for i in range(len(n["UKEY"])) if n["UTEXT"][i] != o["UTEXT"][i])
    K.eq(txt, sorted(ukey(k) for k in P4_FX), "DATA only the five P4 upgrades' texts changed")
    for k, (code, new, old) in P4_FX.items():
        i = n["UKEY"].index(ukey(k))
        K.check(("%g" % new) in n["UTEXT"][i] and ("%g" % old) not in n["UTEXT"][i].split("max")[0], "DATA %s text says %g: %s" % (k, new, n["UTEXT"][i]))
    # the jar's own tables: no (ability, modifier) over 5 class-tree ranks (UHK 1 = a modifier hook; its target from the data table)
    mr = V3D.mod_ranks()
    K.check(max(mr.values()) <= 5, "DATA tools/trees_v3_data.py: most class-tree ranks on one (ability, modifier) = %d" % max(mr.values()))
    tot = {}
    for t in V3D.TREES:
        for bi, b in enumerate(t["branches"], 1):
            for r in b["rows"]:
                for u in r["ups"]:
                    h = u.get("hook")
                    if h and h[0] == "mod":
                        i = n["UKEY"].index("Class.%s.b%d.%s" % (t["name"], bi, u["id"]))
                        tot[(h[1], h[2])] = tot.get((h[1], h[2]), 0) + n["UMAX"][i]
    K.check(tot == mr and max(tot.values()) <= 5, "DATA the jar's UMAX: most ranks on one (ability, modifier) %d (%d modifiers)" % (max(tot.values()), len(tot)))
    # EXECUTED: the fx part of tree:fn:abil (TreeV3.fxCsv) of a player file holding one P4 upgrade at its max sends the new per-rank total
    base = os.path.join(scratch, "data")
    J = lambda x: JClass(PKG + x)
    setup_dirs(J, base)
    J("TreeCfg").load()
    St = J("TreeStore")
    names = [str(x) for x in V.TNAME]
    got, want = {}, {}
    for k, (code, new, old) in P4_FX.items():
        cls = k.split(".")[0]
        i = n["UKEY"].index(ukey(k))
        f = "p4fx" + cls.lower()
        open(os.path.join(base, "players", f + ".properties"), "w", newline="\n").write("v=3\ntreesV3=1\ngates41=1\n%s=%d\n" % (ukey(k), n["UMAX"][i]))
        d = St.readFile(f)
        got[k] = str(V.fxCsv(d, names.index(cls)))
        want[k] = "f.%s=%s" % (code, ("%g" % (new * n["UMAX"][i])))
    ok = all(("," + want[k] + ",") in (got[k] + ",") or ("," + want[k] + ".0,") in (got[k] + ",") for k in P4_FX)
    K.check(ok, "DATA TreeV3.fxCsv at max ranks sends the new totals %s: %s" % (want, got))
    K.save()


def run_clamp(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda x: JClass(PKG + x)
    base = os.path.join(scratch, "clamp")
    setup_dirs(J, base)
    J("TreeCfg").load()
    V, St = J("TreeV3"), J("TreeStore")
    keys = [str(x) for x in V.UKEY]
    k1, k2 = "Class.Spellblade.b2.r1a", "Class.Spellblade.b2.r1b"
    tv = [str(x) for x in V.TNAME].index("Spellblade")
    lines = ["v=3", "treesV3=1", "gates41=1", "%s=5" % k1, "%s=3" % k2]
    open(os.path.join(base, "players", "p4clamp.properties"), "w", newline="\n").write("\n".join(lines) + "\n")
    d = St.readFile("p4clamp")
    K.check(d is not None and not bool(d.bad), "CLAMP the hand-made v3 player file reads")
    r1, r2 = int(d.rk[keys.index(k1)]), int(d.rk[keys.index(k2)])
    V.derive(d)
    K.eq((r1, r2, int(V.spent(d, tv))), (1, 3, 4), "CLAMP Arcane Breach Power 5 ranks -> the new max 1, Duration 3 kept; spent 8 -> 4 (4 points unspent again)")
    # fix2: a class ability line whose gate the unclamped 8 points reached (the clamped 4 do not) stays open, grandfathered
    G = [int(x) for x in V.GATES]
    shut = []
    for r in range(int(V.TR0[tv]), int(V.TR0[tv]) + int(V.TRN[tv])):
        if int(V.RFK[r]) != 1:
            continue
        li = int(V.lineIdx(V.RFLINE[r]))
        gt = G[tv * 8 + int(V.RNUM[r])]
        if li >= 0 and 4 < gt <= 8:
            shut.append(li)
    ln = [bool(x) for x in V.lines(d, tv)]
    K.check(len(shut) > 0 and all(bool(d.gfa[tv * 5 + li]) and ln[li] for li in shut), "CLAMP fix2: the line(s) %s gated at 5-8 points stay open (grandfathered): %s" % (shut, ln))
    K.check(all(not bool(d.gfa[tv * 5 + li]) for li in range(5) if li not in shut), "CLAMP fix2: no other line grandfathered")
    open(os.path.join(base, "players", "p4ok.properties"), "w", newline="\n").write("\n".join(["v=3", "treesV3=1", "gates41=1", "%s=1" % k1, "%s=3" % k2]) + "\n")
    d2 = St.readFile("p4ok")
    K.check(d2 is not None and int(V.spent(d2, tv)) == 4 and not any(bool(d2.gfa[tv * 5 + li]) for li in range(5)), "CLAMP fix2: a file inside the new maxima grandfathers nothing")
    K.save()


def live_start(jar_, home, K):
    from jpype import JClass
    J = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    J("TreeStore").DIR = Paths.get(os.path.join(home, "players"))
    J("TreeCfg").FILE = Paths.get(os.path.join(home, "trees.properties"))
    J("TreeStore").DATA.clear()
    J("TreeCfg").load()
    bp = Paths.get(home)
    for m in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317", "TreeMig321", "TreeMig323", "TreeMig324"):
        J(m).run(bp)
    datas = []
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        if f.endswith(".properties"):
            datas.append((f, J("TreeStore").readFile(f[:-11])))
    return datas


def players_text(home):
    o = {}
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        t = open(os.path.join(home, "players", f), "rb").read().decode("latin-1")
        o[f] = [l for l in t.splitlines() if not l.startswith("#")]
    return o


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    before = tree_hash(home)
    d1 = live_start(jar, home, K)
    after1 = tree_hash(home)
    new = sorted(k for k in after1 if k not in before)
    changed = sorted(k for k in before if after1.get(k) != before[k])
    K.check(all(c.startswith("players/") for c in changed) and all(n.startswith(("history/treesv3/", "history/gates041/")) or n == "trees-v3-changes.log" for n in new),
            "LIVE start 1: only the existing one-time updates touch files - nothing new in 0.4.4: changed %s new %d" % (changed, len(new)))
    K.check(not [f for f, d in d1 if bool(d.bad)], "LIVE every player file reads (%d files)" % len(d1))
    V = JClass(PKG + "TreeV3")
    keys = [str(x) for x in V.UKEY]
    over = []
    for f in sorted(os.listdir(os.path.join(home, "players"))):
        if not f.endswith(".properties"):
            continue
        for ln in open(os.path.join(home, "players", f), encoding="latin-1"):
            if "=" in ln and not ln.startswith("#"):
                k, v = ln.strip().split("=", 1)
                t7 = dict((ukey(a), b) for a, b in V3D.T7_MAX.items())
                if k in t7:
                    try:
                        if int(v) > t7[k][1]:
                            over.append((f, k, int(v), t7[k][1]))
                    except ValueError:
                        pass
    K.notes.append("LIVE ranks above a T7 max (clamped on read): %s" % (over or "none"))
    json.dump({"text": players_text(home), "over": over}, open(os.path.join(scratch, "live044.json"), "w"))
    for f, d in d1:
        K.notes.append("LIVE %s: spent %s" % (f, ["%s %d" % (str(V.TNAME[tv]), int(V.spent(d, tv))) for tv in range(19) if int(V.spent(d, tv)) > 0]))
    live_start(jar, home, K)
    K.check(tree_hash(home) == after1, "LIVE start 2 changes nothing")
    K.save()


def run_live2(out, jar, scratch, home):
    """the same live copy under the PINNED 0.4.3: its player files equal 0.4.4's unless a T7 clamp applies"""
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, OLD_JAR], verify=False)
    live_start(OLD_JAR, home, K)
    a = players_text(home)
    o = json.load(open(os.path.join(scratch, "live044.json")))
    b, over = o["text"], o["over"]
    if not over:
        K.check(a == b and len(a) > 0, "LIVE2 0.4.3 and 0.4.4 write the same player files from the live copy (%d files; comments ignored)" % len(a))
    else:
        ks = set(x[1] for x in over)
        strip = lambda t: dict((f, [l for l in ls if l.split("=", 1)[0] not in ks]) for f, ls in t.items())
        K.check(strip(a) == strip(b), "LIVE2 the player files differ only at the clamped T7 keys %s" % sorted(ks))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("old", run_old), ("data", run_data), ("clamp", run_clamp), ("live", run_live), ("live2", run_live2)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyTrees"))
