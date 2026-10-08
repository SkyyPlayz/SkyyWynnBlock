"""Bare-JVM harness for SkyyTrees 0.3.3 (tools/trees_0_3_3_patch.py) - the CLASS PATH TREES (trunk + 3 locked paths, all 7 classes) and
their one-time migrations. Extends SkyyTrees/test_skyytrees_0.3.2.py / 0.3.1.py (their child-JVM helpers, stand-ins, page-state machinery,
markup / layout / text-fit / contrast checks, bytecode compare and engine-access audit are imported from test_skyytrees_0.3.1.py).

    python SkyyTrees/test_skyytrees_0.3.3.py [--jar <SkyyTrees-0.3.3.jar>] [--prev <SkyyTrees-0.3.2.jar>] [--live <Skyy_SkyyTrees folder>]
                                             [--dir <scratch inside tools/dev/scratch/>] [--keep]

  A  every class of 0.3.3 and 0.3.2 loads, verifies and initialises (-Xverify:all, the game's own JRE)
  E  class bytes 0.3.2 -> 0.3.3: + TreeMig33 only; the template-tree classes (abilities, gather, swing, damage, felled, saver, TreeOps,
     TreeCalc) and the old one-time updates (TreeMig, TreeMig32) do not change
  T  the EIGHT TEMPLATE TREES unchanged: every 0.3.1 / 0.3.2 template page state, result colour and click sequence rendered by BOTH jars on
     the real TreePage (the 0.3.1 harness's STATES / NEW_STATES / CLICKS / NEW_CLICKS) - byte-identical
  K  the CLASS TREES against an INDEPENDENT model of research/cloud/Class-Tree-Build-Map.md (written here, never read from the build):
     K1 the jar's tables (44 nodes, links, pages / rows / cols, roles, lanes, AP, the kinds + amounts + level gates of all 7 classes, the
        hidden switch slots, the ranks, the slot / bar tables incl. the 3-link T1 corner);
     K2 a jar-vs-model FUZZ of the rules on random owned sets of every class under three reader situations (none / today with SkyyArmory
        0.1.9's 12 keys / every reader): skips, intact (the path-lock keep rule), passed, path, reason, state, card, pieceGold, Undo;
     K3 page states on the REAL TreePage of every class (page 1 + 2, no picks / a path picked / a conflict / the probe / the Priest switch
        ON + OFF / Assassin / Monk / a "Shaman" profile): every cell's state line = the model, the hidden switch slot empty on 6 classes,
        the Switch button, the detail lines, the path note, the free-respec label; every state through the 0.3.1 markup / layout /
        text-fit / contrast checks;
     K4 click sequences EXECUTING buy (the path pick + lock, skipped waiting nodes, the switch flip, a crafted click on a hidden node),
        Undo (frees the path), the class respec (coins / free once / cooldown), "Comes with the class abilities" refusals
  L  logic in fresh loaders: effects (Health / Mana / Rift Master -10 Mana, Mana Regen posts, the trees.class movement source with bow /
     crouch / fall, its removal), tree:fn:level / tree:fn:bonus (ranks, the switch, another class, broken chains), readers, /tree class
     words with a Shaman profile, the 43 Server Setup rows + the class checks, the default file (the 0.3.3 class block once)
  M  TreeMig33 on scratch COPIES of the live Skyy_SkyyTrees folder in the plugin's start order (load -> TreeMig -> TreeMig32 -> TreeMig33 ->
     CfgPub.start), each start in a fresh loader: start 1 appends exactly the missing class lines after the old bytes (History = the old
     bytes, no change-log line, the new gates apply at once), start 2 writes nothing; CRLF, no final newline, an admin's line kept, a
     hand-edited retired line named, History blocked (nothing written, retried), an empty file, a pre-0.3 file (the 0.3 block carries the
     0.3.3 marker), a fresh start; 0.3.2 reads the updated file and writes nothing (rollback); the LIVE folder is never written
  P  PLAYER FILES: every live player file (copied) read by 0.3.3 (no migration, the same Properties when saved); the ClassMig33 matrix on
     made-up copies (lane owners of every old class, LS / CS / RS only, retired + new ids, two classes, a .retired line already there =
     nothing again, a Shaman alias line kept): the ids drop, .retired / .freeRespec / .notice written once, the INFO line, START TWICE =
     the same file, the notice taken once, the free respec used once; 0.3.2 reads every migrated file (keeps the new lines, the picks it
     knows) - the rollback; a file owning two paths keeps the one with more AP
  Z  the engine-access audit (every reference of the 0.3.3 jar looked up with the JVM's own rules: 0 refused; the control is refused)
"""
import os, sys, re, shutil, subprocess, json, zipfile, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.3", "0.3.2"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyytrees-033")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
SCRIPT = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyTrees")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
MK33 = "skyytrees-0.3.3-paths"


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# the 0.3.1 harness = the helpers (child JVM start, stand-ins, page states, markup model, bytecode compare, audit)
_spec = importlib.util.spec_from_file_location("t031", os.path.join(HERE, "test_skyytrees_0.3.1.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)
H.SCRATCH = SCRATCH
H.check = check          # the 0.3.1 page checks (check_state) count into this harness

# ============================================================================================================== K: the independent model
# research/cloud/Class-Tree-Build-Map.md sections 2-5 + Class-Tree-Paths.md (2026-10-07). Nothing here reads the build script.
CLASSES = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]
CSKILL = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Discipline"]
MAGIC = ("Mage", "Priest")
# (id, AP, parents, lane, lane count, page, row, col, role) - page 1 = 0.3.2's spine + rune slots (P4 moved to page 2 top right)
P1 = [("ROOT", 1, [], 0, 0, 0, 0, 4, 0), ("P1", 1, ["ROOT"], 0, 0, 0, 1, 4, 0), ("A1", 1, ["P1"], 0, 0, 0, 1, 2, 2),
      ("M1A", 1, ["A1"], 0, 0, 0, 1, 1, 3), ("M1B", 2, ["M1A"], 0, 0, 0, 1, 0, 4), ("A2", 1, ["P1"], 0, 0, 0, 1, 6, 2),
      ("M2A", 1, ["A2"], 0, 0, 0, 1, 7, 3), ("M2B", 2, ["M2A"], 0, 0, 0, 1, 8, 4), ("P2", 1, ["P1"], 0, 0, 0, 3, 4, 0),
      ("A3", 1, ["P2"], 0, 0, 0, 3, 2, 2), ("M3A", 1, ["A3"], 0, 0, 0, 3, 1, 3), ("M3B", 2, ["M3A"], 0, 0, 0, 3, 0, 4),
      ("A4", 1, ["P2"], 0, 0, 0, 3, 6, 2), ("M4A", 1, ["A4"], 0, 0, 0, 3, 7, 3), ("M4B", 2, ["M4A"], 0, 0, 0, 3, 8, 4),
      ("X1", 1, ["P2"], 0, 0, 0, 4, 3, 1), ("X2", 1, ["P2"], 0, 0, 0, 4, 5, 1), ("P3", 1, ["X1", "X2"], 0, 0, 0, 5, 4, 0),
      ("P4", 1, ["P3"], 0, 0, 1, 0, 8, 0)]
NEED = {"M1A": "A1", "M1B": "A1", "M2A": "A2", "M2B": "A2", "M3A": "A3", "M3B": "A3", "M4A": "A4", "M4B": "A4"}
LOCK = {"X1": "X2", "X2": "X1"}
P2 = [("T1", 1, ["ROOT"], 0, 0, 1, 0, 0, 5)] + [("T%d" % k, (1, 1, 2, 2, 2, 3)[k - 1], ["T%d" % (k - 1)], 0, 0, 1, k - 1, 0, 5) for k in range(2, 7)]
P2 += [("TS", 0, ["ROOT"], 0, 0, 1, 0, 2, 9)]
for _l, (_p, _e, _r) in enumerate((("PA", "LE", 1), ("PB", "CE", 3), ("PC", "RE", 5))):
    P2 += [(_p + str(k), (2, 2, 3, 3, 4)[k - 1], ["T1" if k == 1 else _p + str(k - 1)], _l + 1, 0, 1, _r, k + 1, 6) for k in range(1, 6)]
    P2 += [(_e, 3, [_p + "5"], _l + 1, 5, 1, _r, 7, 7)]
MT = P1 + P2
MID = [n[0] for n in MT]
MIX = dict((n[0], k) for k, n in enumerate(MT))
NN = len(MT)
assert NN == 44
LINKS = [(p, n[0]) for n in MT for p in n[2] if MT[MIX[p]][5] == n[5]]
SPINE = {False: {"ROOT": ("H", 4), "P1": ("S", 2), "P2": ("H", 4), "X1": ("S", 3), "X2": ("H", 8), "P3": ("R", 5), "P4": ("S", 2)},
         True: {"ROOT": ("H", 4), "P1": ("M", 5), "P2": ("R", 5), "X1": ("M", 8), "X2": ("H", 8), "P3": ("H", 4), "P4": ("R", 5)}}
# the map's status per page-2 node (section 5): H Health, M Mana, R Mana Regen, V speed, B speed with a bow, C speed crouching, F fall,
# A SkyyArmory, G SkyyGear, K class abilities, L a later build, X SkyySkills crossbow, T the switch
KIND2 = {
    "Warrior": "T1 K T2 H T3 A T4 L T5 G T6 K PA1 K PA2 K PA3 K PA4 K PA5 K PB1 K PB2 K PB3 K PB4 K PB5 K PC1 L PC2 K PC3 G PC4 K PC5 G",
    "Archer": "T1 A T2 L T3 X T4 B T5 G T6 X PA1 K PA2 K PA3 K PA4 K PA5 K PB1 K PB2 K PB3 K PB4 K PB5 G PC1 K PC2 K PC3 K PC4 K PC5 K",
    "Mage": "T1 R T2 A T3 A T4 K T5 M T6 K PA1 A PA2 A PA3 K PA4 K PA5 A PB1 A PB2 K PB3 K PB4 K PB5 K PC1 K PC2 K PC3 K PC4 K PC5 K",
    "Priest": "T1 A T2 M T3 K T4 K T5 R T6 K TS T PA1 K PA2 K PA3 K PA4 K PA5 K PB1 K PB2 K PB3 K PB4 K PB5 K PC1 A PC2 A PC3 A PC4 A PC5 A",
    "Berserker": "T1 H T2 G T3 A T4 K T5 G T6 K PA1 K PA2 K PA3 K PA4 K PA5 K PB1 G PB2 K PB3 K PB4 K PB5 G PC1 L PC2 K PC3 K PC4 K PC5 L",
    "Monk": "T1 V T2 F T3 A T4 A T5 L T6 K PA1 A PA2 A PA3 K PA4 K PA5 A PB1 A PB2 A PB3 K PB4 K PB5 K PC1 K PC2 K PC3 K PC4 K PC5 K",
    "Assassin": "T1 C T2 G T3 A T4 F T5 G T6 K PA1 K PA2 K PA3 K PA4 K PA5 K PB1 K PB2 K PB3 K PB4 K PB5 K PC1 A PC2 A PC3 A PC4 A PC5 K",
}
AMT2 = {("Warrior", "T2"): 8, ("Archer", "T4"): 4, ("Mage", "T1"): 10, ("Mage", "T5"): 10, ("Priest", "T2"): 5, ("Priest", "T5"): 10,
        ("Priest", "TS"): 1, ("Berserker", "T1"): 6, ("Monk", "T1"): 3, ("Monk", "T2"): 10, ("Assassin", "T1"): 10, ("Assassin", "T4"): 15,
        ("Mage", "T2"): 5, ("Mage", "T3"): 2, ("Mage", "PA1"): 50, ("Mage", "PA2"): 3, ("Mage", "PA5"): 25, ("Mage", "PB1"): 5, ("Priest", "T1"): 10,
        ("Monk", "PB1"): 20, ("Assassin", "T3"): 3, ("Assassin", "PC1"): 6, ("Assassin", "PC2"): 2, ("Assassin", "PC3"): 3, ("Assassin", "PC4"): 10,
        ("Archer", "T3"): 1, ("Archer", "T6"): 30}
ARMORY_019 = ["Mage.T2", "Mage.T3", "Mage.PA1", "Mage.PA2", "Mage.PB1", "Priest.T1", "Assassin.T3", "Assassin.PC1", "Assassin.PC2",
              "Assassin.PC3", "Assassin.PC4"]          # SkyyArmory 0.1.9's tree:reads:SkyyArmory (Rift Master PA5 not yet; fix 2: Monk Hard
                                                       # Knuckles PB1 held back - its power-hit test is UNVERIFIED in game)
RANKS = {("Archer", "T3"): [(30, 1), (42, 1), (55, 1)], ("Mage", "T3"): [(30, 1), (42, 1), (55, 1)]}
RETIRED = ["L1", "L2", "L3", "L4", "C1", "C2", "C3", "C4", "R1", "R2", "R3", "R4", "LS", "CS", "RS"]
RET_AP = dict(zip(RETIRED, [1, 1, 2, 3, 1, 1, 2, 3, 1, 1, 2, 3, 0, 0, 0]))


def kind_of(cn, nid):
    n = MT[MIX[nid]]
    if n[8] in (0, 1):
        return SPINE[cn in MAGIC][nid][0]
    if n[8] in (2, 3, 4, 7):
        return "-"
    if nid == "TS" and cn != "Priest":
        return "-"
    d = KIND2[cn].split()
    return dict(zip(d[0::2], d[1::2]))[nid]


def amt_of(cn, nid):
    n = MT[MIX[nid]]
    if n[8] in (0, 1):
        return SPINE[cn in MAGIC][nid][1]
    return AMT2.get((cn, nid), None)


def min_of(cn, nid):
    n = MT[MIX[nid]]
    if n[8] == 5:
        return 75 if (cn, nid) == ("Archer", "T6") else (5, 10, 15, 25, 40, 55)[int(nid[1]) - 1]
    if n[8] == 6:
        return (20, 30, 45, 65, 75)[int(nid[2]) - 1]
    if n[8] == 7:
        return 75
    if n[8] == 9:
        return 1
    return 0


def hidden(cn, nid):
    return nid == "TS" and cn != "Priest"


def slot(nid):
    return MT[MIX[nid]][8] in (2, 3, 4, 7)


def listed(sit, mod, key):
    return key in [x.strip() for x in (sit.get("reads") or {}).get(mod, "").split(",")]


def m_who(cn, nid, sit):
    """'' = live, else who it waits for (the model's comingWho)"""
    if slot(nid):
        return "SkyyGear's elemental stats (later)" if MT[MIX[nid]][8] == 7 else "runes (Hytale 0.7)"
    k = kind_of(cn, nid)
    key = "Class.%s.%s" % (cn, nid)
    if k == "S":
        return "" if listed(sit, "SkyyGear", "gear:extras") else "SkyyGear"
    if k == "X":
        return "" if listed(sit, "SkyySkills", key) else "SkyySkills"
    if k == "R":
        return "" if sit.get("regen") else "SkyySkills"
    if k == "A":
        return "" if listed(sit, "SkyyArmory", key) else "SkyyArmory"
    if k == "G":
        return "" if listed(sit, "SkyyGear", key) else "SkyyGear"
    if k == "K":
        return "" if listed(sit, "SkyyClasses", key) else "the class abilities"
    if k == "L":
        return "a later build"
    return ""


def m_skipkind(cn, nid):
    return not slot(nid) and not hidden(cn, nid) and kind_of(cn, nid) in "SXRAGKL" and kind_of(cn, nid) != "-"


def m_ok(own, cn, nid, con_off=()):
    return nid in own and nid not in con_off and not slot(nid) and not hidden(cn, nid)


def m_skips(own, cn, sit, con_off=()):
    sk, hold = set(), {}
    for nid in reversed(MID):
        h = False
        for c in MID[MIX[nid] + 1:]:
            if nid in MT[MIX[c]][2] and (m_ok(own, cn, c, con_off) or (c in sk and hold.get(c))):
                h = True
                break
        hold[nid] = h
        if nid in own or nid in con_off or not m_skipkind(cn, nid):
            continue
        if h or m_who(cn, nid, sit):
            sk.add(nid)
    return sk


def m_keep(own, cn, con_off=(), ap_of=None):
    apl, has = {1: 0, 2: 0, 3: 0}, set()
    for nid in MID:
        ln = MT[MIX[nid]][3]
        if ln and m_ok(own, cn, nid, con_off):
            has.add(ln)
            apl[ln] += (ap_of or {}).get(nid, MT[MIX[nid]][1])
    if len(has) <= 1:
        return 0
    best = 0
    for l in (1, 2, 3):
        if l in has and (best == 0 or apl[l] > apl[best]):
            best = l
    return best


def m_reach(own, cn, sit, con_off=()):
    """(intact, passed): the integrity fixpoint with skips and the path-lock keep rule"""
    sk = m_skips(own, cn, sit, con_off)
    keep = m_keep(own, cn, con_off)
    ok = set(n for n in own if m_ok(own, cn, n, con_off) and (keep == 0 or MT[MIX[n]][3] in (0, keep)))
    while True:
        it, ps = set(), set()
        if "ROOT" in ok:
            it.add("ROOT")
            ch = True
            while ch:
                ch = False
                for nid in MID[1:]:
                    if nid in it or nid in ps or not (nid in ok or nid in sk):
                        continue
                    if any(p in it or p in ps for p in MT[MIX[nid]][2]):
                        (it if nid in ok else ps).add(nid)
                        ch = True
        drop = [n for n in it if (n in NEED and NEED[n] not in it) or (n in LOCK and LOCK[n] in own)]
        if not drop:
            return it, ps
        ok -= set(drop)


def m_passed(own, it, cn, sit, con_off=()):
    if "ROOT" not in it:
        return set()
    sk, ps = m_skips(own, cn, sit, con_off), set()
    for nid in MID[1:]:
        if nid in sk and any(p in it or p in ps for p in MT[MIX[nid]][2]):
            ps.add(nid)
    return ps


def m_path(it):
    for nid in MID:
        if nid in it and MT[MIX[nid]][8] == 6:
            return MT[MIX[nid]][3]
    return 0


def m_ap(lvl):
    return 0 if lvl < 1 else min(50, 1 + lvl // 2)


def m_reason(own, it, cn, nid, lvl, ap_free, sit, con_off=()):
    n = MT[MIX[nid]]
    if nid in own:
        return 10
    if nid in con_off or hidden(cn, nid):
        return 1
    if m_who(cn, nid, sit):
        return 2
    par = nid == "ROOT" or any(p in it for p in n[2])
    ps = None
    if not par:
        ps = m_passed(own, it, cn, sit, con_off)
        par = any(p in ps for p in n[2])
    if not par:
        return 3
    if nid in NEED and NEED[nid] not in it:
        return 4
    if nid in LOCK and LOCK[nid] in own:
        return 5
    if n[3]:
        p = m_path(it)
        if p and p != n[3]:
            return 11
    if n[4]:
        ps = ps if ps is not None else m_passed(own, it, cn, sit, con_off)
        if sum(1 for x in MID if (x in it or x in ps) and MT[MIX[x]][3] == n[3]) < n[4]:
            return 6
    if max(lvl, 0) < min_of(cn, nid):
        return 7
    if ap_free < 0:
        return 8
    if ap_free < n[1]:
        return 9
    return 0


def m_state(own, it, cn, nid, lvl, ap_free, sit):
    if nid in own:
        return 2 if nid in it else 4
    if m_who(cn, nid, sit):
        return 3
    return 1 if m_reason(own, it, cn, nid, lvl, ap_free, sit) == 0 else 0


def m_card(own, it, cn, nid, lvl, ap_free, sit, on=()):
    stt = m_state(own, it, cn, nid, lvl, ap_free, sit)
    if stt == 2 and nid == "TS":
        return "All players" if nid in on else "Party only"   # fix: OFF (party only) is the LOCKED default
    if stt == 2:
        return "Owned"
    if stt == 3:
        return "Coming"
    if stt == 4:
        return "Locked"
    n = MT[MIX[nid]]
    if stt == 1:
        return "Unlock %d AP" % n[1]
    why = m_reason(own, it, cn, nid, lvl, ap_free, sit)
    if why == 1:
        return "Turned off"
    if why == 3:
        if len(n[2]) != 1:
            return "Locked"
        g, sk = n[2][0], m_skips(own, cn, sit)
        while g in sk and MT[MIX[g]][2]:
            g = MT[MIX[g]][2][0]
        return "Needs " + g
    if why == 4:
        return "Needs " + NEED[nid]
    return {5: "Pick one", 11: "Path locked", 6: "Lane %d" % n[4], 7: "Lv %d" % min_of(cn, nid), 8: "Respec", 9: "Need %d AP" % n[1]}.get(why, "Locked")


def sit_of(name):
    """the reader situations: none / today (SkyySkills' Mana Regen + SkyyArmory 0.1.9) / every reader"""
    if name == "none":
        return {"regen": False, "reads": {}}
    if name == "today":
        return {"regen": True, "reads": {"SkyyArmory": ",".join("Class." + k for k in ARMORY_019)}}
    allk = dict((m, []) for m in ("SkyyArmory", "SkyyGear", "SkyyClasses", "SkyySkills"))
    for cn in CLASSES:
        for nid in MID:
            k = kind_of(cn, nid)
            m = {"A": "SkyyArmory", "G": "SkyyGear", "K": "SkyyClasses", "X": "SkyySkills"}.get(k)
            if m:
                allk[m].append("Class.%s.%s" % (cn, nid))
    allk["SkyyGear"].append("gear:extras")
    return {"regen": True, "reads": dict((m, ",".join(v)) for m, v in allk.items())}


SITS = ["none", "today", "all"]


# ============================================================================================================== child: load
def run_load(jar, out):
    from jpype import JClass
    H._jvm_start([jar])
    Cls = JClass("java.lang.Class")
    ld = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    fails = []
    for n in names:
        try:
            Cls.forName(n, True, ld)
        except Exception as e:
            fails.append("%s: %s" % (n, e))
    json.dump({"classes": len(names), "fails": fails}, open(out, "w"))
    os._exit(0)


# ============================================================================================================== child: template states
def run_tstates(jar, out, tag):
    """the 0.3.1 harness's template page states + clicks (its class lists left out: they model the 0.3.2 map)"""
    H.CLASS_STATES = []
    H.CLASS_CLICKS = []
    H.run_states(jar, out, tag)


# ============================================================================================================== child: the class tree
def run_cls(jar, out):
    from jpype import JClass, JArray, JBoolean, JInt, JImplements, JOverride
    H._jvm_start([jar])
    R = {"tables": {}, "fuzz": [], "pages": {}, "clicks": {}, "errors": []}
    Cls, Cops, Page, Store, Cfg, Data = (JClass(PKG + x) for x in ("TreeClass", "TreeClassOps", "TreePage", "TreeStore", "TreeCfg", "TreeData"))
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths, Integer, Boolean, System = JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.Boolean"), JClass("java.lang.System")
    _U, _setf, ByTree, me, pr = H._stand_ins()
    bridge = Store.bridge()
    pdir = os.path.join(SCRATCH, "players-cls")
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    for arr in ("NID", "CLASSES", "CSKILL", "LANE", "CNM", "CIC", "CNOW", "CHOW", "RET_IDS"):
        R["tables"][arr] = [str(x) for x in getattr(Cls, arr)]
    for arr in ("NAP", "NPAGE", "NROW", "NCOL", "NLANE", "NLANEN", "NPAR1", "NPAR2", "NNEED", "NLOCK", "NROLE", "CK", "CAMT", "CMIN", "LA", "LB",
                "SK", "SN", "SARMS", "PL1", "PL2", "PL3", "CRKL", "CRKA", "CM2", "RET_AP"):
        R["tables"][arr] = [int(x) for x in getattr(Cls, arr)]
    for arr in ("SR", "SD", "CMAGIC", "CHID"):
        R["tables"][arr] = [bool(x) for x in getattr(Cls, arr)]
    R["tables"]["K"] = dict((k, int(getattr(Cls, "K_" + k))) for k in "HSMRXVBCFAGKLT")
    R["tables"]["C_AP"] = [int(x) for x in Cfg.C_AP]
    R["tables"]["C_MIN"] = [int(x) for x in Cfg.C_MIN]
    NC_, NN_ = int(Cls.NC), int(Cls.NN)
    COINS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            COINS.append(int(o[1].longValue()))
            return Boolean.TRUE

    @JImplements("java.util.function.Function")
    class Regen(object):
        @JOverride
        def apply(self, o):
            return Boolean.TRUE

    def bridge_sit(sname):
        for k in list(bridge.keySet()):
            if str(k).startswith(("tree:reads:", "skill:fn:manaregen", "gear:tree:readers", "skill:tree:readers")):
                bridge.remove(k)
        sit = sit_of(sname)
        for mod, csv in sit["reads"].items():
            bridge.put("tree:reads:" + mod, csv)
        if sit["regen"]:
            bridge.put("skill:fn:manaregen", Regen())

    def jbools(xs):
        a = JArray(JBoolean)(NN_)
        for i, x in enumerate(xs):
            a[i] = bool(x)
        return a

    # ---- K2: the fuzz (random owned sets; the model runs in the parent on the same sets)
    rnd = random.Random(33033)
    for sname in SITS:
        bridge_sit(sname)
        for ci, cn in enumerate(CLASSES):
            sets = [[], ["ROOT"], ["ROOT", "T1", "PA1", "PA2"], ["ROOT", "T2", "PB1", "PC1"], ["ROOT", "TS"], ["ROOT", "PA1", "PB1", "PB2"]]
            for _ in range(40):
                p_ = rnd.choice((0.15, 0.3, 0.5, 0.8))
                sets.append([nid for nid in MID if rnd.random() < p_] + (["ROOT"] if rnd.random() < 0.8 else []))
            for s_ in sets:
                own = sorted(set(s_))
                ja = jbools([nid in own for nid in MID])
                it = Cls.intactOf(ja, ci)
                ps = Cls.passed(ja, it, ci)
                lvl = rnd.choice((0, 1, 5, 14, 20, 30, 44, 55, 75, 100))
                apf = rnd.choice((-1, 0, 1, 2, 3, 9, 40))
                sk = Cls.skips(ja, ci)
                lit = Cls.lit(ja, it, ci)
                g1 = Cls.pieceGold(1, lit)
                g0 = Cls.pieceGold(0, lit)
                rec = {"s": sname, "ci": ci, "own": own, "lvl": lvl, "apf": apf,
                       "it": [MID[n] for n in range(NN_) if bool(it[n])], "ps": [MID[n] for n in range(NN_) if bool(ps[n])],
                       "sk": [MID[n] for n in range(NN_) if bool(sk[n])], "lit": [MID[n] for n in range(NN_) if bool(lit[n])],
                       "path": int(Cls.pathOf(it)), "keep": int(Cls.keepLane(ja, ci)),
                       "reason": [int(Cls.reason(ja, it, ci, n, lvl, apf)) for n in range(NN_)],
                       "state": [int(Cls.state(ja, it, ci, n, lvl, apf)) for n in range(NN_)],
                       "card": [str(Cls.cardText(ja, it, ci, n, lvl, apf, int(Cls.state(ja, it, ci, n, lvl, apf)))) for n in range(NN_)],
                       "who": [str(Cls.comingWho(ci, n)) for n in range(NN_)],
                       "gold": [[q for q in range(len(g0)) if bool(g0[q])], [q for q in range(len(g1)) if bool(g1[q])]],
                       "spent": int(Cls.spent(it, ci)),
                       "rtext": [str(Cls.reasonText(ja, it, ci, n, lvl, apf, int(Cls.reason(ja, it, ci, n, lvl, apf)))) for n in range(NN_)]}
                R["fuzz"].append(rec)

    # ---- K3 / K4: the real page
    def setup(cn=None, lvl=30, own=(), sname="today", cpage=0, csel=0, probe=False, on=(), free=False, pcls=None, msg="", respec_at=0):
        for k in list(bridge.keySet()):
            if str(k).startswith(("skill:", "coins:", "profile", "tree:", "move:", "class:", "gear:")):
                bridge.remove(k)
        Store.DATA.clear()
        Store.DIRTY.clear()
        for fn in os.listdir(pdir):
            os.remove(os.path.join(pdir, fn))
        bridge_sit(sname)
        bridge.put("coins:fn:take", Coins())
        del COINS[:]
        Cfg.CLASS_ON = True
        if lvl is not None:
            bridge.put("skill:fn:level", ByTree(dict((sk_, lvl) for sk_ in CSKILL), Integer))
        d = Data()
        ci = CLASSES.index(cn) if cn in CLASSES else -1
        if cn:
            bridge.put("class:" + str(me), cn)
        if pcls:
            bridge.put("profile:class:" + str(me), pcls)
        if ci >= 0:
            for nid in own:
                d.cown[ci * NN_ + MIX[nid]] = True
            for nid in on:
                d.con[ci * NN_ + MIX[nid]] = True
            d.cfree[ci] = bool(free)
            if respec_at:
                d.crespecAt[ci] = System.currentTimeMillis()
        Store.DATA.put(str(me), d)
        page = Page(pr, 8)
        page.cpage = cpage
        page.csel = csel
        page.msg = msg
        if probe:
            page.probe = True
            page.pci = ci if ci >= 0 else 0
            page.pd = Cops.probeData(page.pci)
        return page, d, ci

    def render(page):
        b, ev = UCB(), UEB()
        try:
            page.build(None, b, ev, None)
            err = None
        except Exception as e:
            err = str(e)
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        return {"error": err, "commands": cmds, "events": evs, "tree": int(page.tree), "cpage": int(page.cpage), "csel": int(page.csel)}

    PAGES = []
    for cn in CLASSES:
        for cp in (0, 1):
            PAGES.append(dict(name="%s p%d empty" % (cn, cp), cn=cn, cpage=cp, csel=MIX["ROOT"] if cp == 0 else MIX["T1"]))
            PAGES.append(dict(name="%s p%d root" % (cn, cp), cn=cn, own=["ROOT"], cpage=cp, csel=MIX["PA1"] if cp else MIX["P1"]))
        PAGES.append(dict(name="%s p1 path A" % cn, cn=cn, own=["ROOT", "T1", "T2", "PA1", "PA2"], cpage=1, csel=MIX["PB1"], lvl=40))
        PAGES.append(dict(name="%s p1 conflict" % cn, cn=cn, own=["ROOT", "T1", "PA1", "PB1", "PB2"], cpage=1, csel=MIX["PA1"], lvl=60, sname="all"))
        PAGES.append(dict(name="%s p1 none" % cn, cn=cn, own=["ROOT"], cpage=1, csel=MIX["T3"], sname="none", lvl=20))
        PAGES.append(dict(name="%s p1 all" % cn, cn=cn, own=["ROOT", "T1"], cpage=1, csel=MIX["LE"], sname="all", lvl=99))
        PAGES.append(dict(name="%s probe p1" % cn, cn=cn, cpage=1, csel=MIX["T2"], probe=True))
        PAGES.append(dict(name="%s p1 free respec" % cn, cn=cn, own=["ROOT", "T1"], cpage=1, csel=MIX["T1"], free=True))
    PAGES.append(dict(name="Priest switch on", cn="Priest", own=["ROOT", "TS"], on=["TS"], cpage=1, csel=MIX["TS"], lvl=1))
    PAGES.append(dict(name="Priest switch off", cn="Priest", own=["ROOT", "TS"], cpage=1, csel=MIX["TS"], lvl=1))
    PAGES.append(dict(name="Priest switch unowned", cn="Priest", own=["ROOT"], cpage=1, csel=MIX["TS"], lvl=1))
    PAGES.append(dict(name="Mage hidden switch selected", cn="Mage", own=["ROOT"], cpage=1, csel=MIX["TS"]))
    PAGES.append(dict(name="Shaman profile", cn=None, pcls="Shaman", own=[], cpage=1, csel=MIX["T1"]))
    PAGES.append(dict(name="unknown class", cn=None, pcls="Shaman2", own=[], cpage=0, csel=0))
    PAGES.append(dict(name="no class", cn=None, own=[], cpage=0, csel=0))
    for spec in PAGES:
        cn = spec.get("cn") or ("Monk" if spec.get("pcls") == "Shaman" else None)
        page, d, ci = setup(cn=spec.get("cn"), lvl=spec.get("lvl", 30), own=spec.get("own", ()), sname=spec.get("sname", "today"),
                            cpage=spec["cpage"], csel=spec["csel"], probe=spec.get("probe", False), on=spec.get("on", ()),
                            free=spec.get("free", False), pcls=spec.get("pcls"))
        st = render(page)
        jci = int(Cls.classIdx(Cls.classOf(me))) if not spec.get("probe") else int(page.pci)
        dd = page.pd if spec.get("probe") else d
        if jci >= 0:
            ja = Cls.ownOf(dd, jci)
            it = Cls.intact(dd, jci)
            lv = 30 if spec.get("probe") else spec.get("lvl", 30)
            apf = int(Cls.ap(lv)) - int(Cls.spent(it, jci))
            st["jcards"] = [str(Cls.cardText2(dd, ja, it, jci, n, lv, apf, int(Cls.state(ja, it, jci, n, lv, apf)))) for n in range(NN_)]
            st["jown"] = [MID[n] for n in range(NN_) if bool(ja[n])]
        st["jci"] = jci
        R["pages"][spec["name"]] = {"spec": spec, "state": st}

    # ---- K4: clicks (page.handleDataEvent; the real TreeClassOps)
    def run_clicks(name, setup_kw, clicks):
        page, d, ci = setup(**setup_kw)
        steps = []
        for c in clicks:
            if c.startswith("!lvl:"):
                bridge.put("skill:fn:level", ByTree(dict((sk_, int(c[5:])) for sk_ in CSKILL), Integer))
                continue
            if c.startswith("!sel:"):
                nid = c[5:]
                c = "trc%d" % (MIX[nid] + 1)
            err = None
            try:
                page.handleDataEvent(None, None, '{"a":"%s"}' % c)
            except Exception as e:
                err = str(e)[:200]
            ci_ = int(Cls.classIdx(Cls.classOf(me)))
            steps.append({"click": c, "err": err, "msg": str(page.msg), "csel": int(page.csel), "cpage": int(page.cpage),
                          "own": [MID[n] for n in range(NN_) if ci_ >= 0 and bool(d.cown[ci_ * NN_ + n])],
                          "on": [MID[n] for n in range(NN_) if ci_ >= 0 and bool(d.con[ci_ * NN_ + n])],
                          "free": bool(d.cfree[ci_]) if ci_ >= 0 else False, "coins": list(COINS), "undo": int(page.undo.size()),
                          "dirty": sorted(str(k) for k in Store.DIRTY.keySet()),
                          "bonusTS": float(Cls.bonus(me, "Class.Priest.TS")), "lvlPA1": int(Cls.bonusLevel(me, "Class.Mage.PA1"))})
        R["clicks"][name] = {"steps": steps, "after": render(page)}

    run_clicks("mage path", dict(cn="Mage", lvl=30), [
        "!sel:ROOT", "trbuy", "trpgn", "!sel:T1", "trbuy", "!sel:T2", "trbuy", "!sel:PA1", "trbuy", "!sel:PB1", "trbuy", "!sel:PA2", "trbuy",
        "trundo", "trundo", "!sel:PB1", "trbuy", "!sel:PA1", "trbuy", "trrespec", "trrespec"])
    run_clicks("mage waiting", dict(cn="Mage", lvl=45, sname="none"), [
        "!sel:ROOT", "trbuy", "trpgn", "!sel:T1", "trbuy", "!sel:T5", "trbuy", "!sel:T4", "trbuy", "!sel:PA1", "trbuy", "!sel:PB2", "trbuy"])
    run_clicks("warrior skip", dict(cn="Warrior", lvl=12), [
        "!sel:ROOT", "trbuy", "trpgn", "!sel:T1", "trbuy", "!sel:T2", "trbuy", "!sel:PA1", "trbuy", "!sel:PC3", "trbuy"])
    run_clicks("priest switch", dict(cn="Priest", lvl=1), [
        "!sel:ROOT", "trbuy", "trpgn", "!sel:TS", "trbuy", "trbuy", "trbuy", "trbuy", "trundo"])
    run_clicks("priest gentle hands", dict(cn="Priest", lvl=5), ["!sel:ROOT", "trbuy", "trpgn", "!sel:T1", "trbuy", "!sel:TS", "trbuy"])
    run_clicks("mage hidden", dict(cn="Mage", lvl=30), ["!sel:ROOT", "trbuy", "!sel:TS", "trbuy"])
    run_clicks("free respec", dict(cn="Assassin", lvl=40, own=["ROOT", "T1", "T4"], free=True, respec_at=1), [
        "trpgn", "trrespec", "trrespec", "!sel:ROOT", "trbuy", "trrespec", "trrespec"])
    run_clicks("paid respec", dict(cn="Monk", lvl=22, own=["ROOT", "T1", "T2"]), ["trpgn", "trrespec", "trrespec"])
    run_clicks("level gates", dict(cn="Monk", lvl=4), ["!sel:ROOT", "trbuy", "trpgn", "!sel:T1", "trbuy", "!lvl:6", "trbuy", "!sel:T2", "trbuy",
                                                       "!lvl:10", "trbuy"])
    run_clicks("assassin blink", dict(cn="Assassin", lvl=70), ["!sel:ROOT", "trbuy", "trpgn", "!sel:T1", "trbuy", "!sel:PC1", "trbuy", "!sel:PC2", "trbuy",
                                                              "!sel:PC3", "trbuy", "!sel:PC4", "trbuy", "!sel:PC5", "trbuy", "!sel:PA1", "trbuy"])
    json.dump(R, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================================== child: logic (L M P)
def run_logic(jar, prev, fake, live, out):
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    H._jvm_start([], [fake])
    R = {"oks": 0, "fails": [], "info": {}}

    def ck(cond, what):
        if cond:
            R["oks"] += 1
        else:
            R["fails"].append(what)
            print("FAIL", what)

    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    Paths, Boolean, Integer, Double, Float = (JClass("java.nio.file.Paths"), JClass("java.lang.Boolean"), JClass("java.lang.Integer"),
                                              JClass("java.lang.Double"), JClass("java.lang.Float"))
    _U, setf, ByTree, me, pr = H._stand_ins()

    def loader(j):
        urls = JArray(URL)(1)
        urls[0] = File(j).toURI().toURL()
        return URLCL(urls, sysl)

    def K(ld):
        return lambda n: JClass(PKG + n, loader=ld)

    def path(p):
        return Paths.get(p)

    def snap(d):
        o = {}
        for r, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r, f)
                o[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
        return o

    def jarr(xs):
        return JArray(JObject)(xs)

    def changed(a, b):
        return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))

    C0 = K(loader(jar))
    bridge = C0("TreeStore").bridge()

    def start(base, j=None, kit=True):
        C = K(loader(j or jar))
        b = path(base)
        C("TreeCfg").FILE = b.resolve("trees.properties")
        C("TreeStore").DIR = b.resolve("players")
        s = str(C("TreeCfg").load())
        m = str(C("TreeMig").run(b))
        m32 = str(C("TreeMig32").run(b))
        m33 = str(C("TreeMig33").run(b)) if (j or jar) == jar else ""
        if kit:
            C("CfgPub").start(b.getParent(), None)
        return {"C": C, "sum": s, "mig": m, "m32": m32, "m33": m33, "on": bool(C("TreeCfg").CLASS_ON)}

    COUNT = [0]

    def case(name, body, extra=None, rm=()):
        COUNT[0] += 1
        base = os.path.join(SCRATCH, "m", "%02d-%s" % (COUNT[0], re.sub(r"[^a-z0-9]+", "-", name.lower())), "mods", "Skyy_SkyyTrees")
        shutil.copytree(live, base)
        if body is None:
            os.remove(os.path.join(base, "trees.properties"))
        else:
            open(os.path.join(base, "trees.properties"), "wb").write(body)
        for k, v in (extra or {}).items():
            open(os.path.join(base, k), "ab").write(v)
        for k in rm:
            p_ = os.path.join(base, k)
            if os.path.isdir(p_):
                shutil.rmtree(p_)
        return base

    LIVE_TP = os.path.join(live, "trees.properties")
    live_before = open(LIVE_TP, "rb").read()
    live_snap = snap(live)
    Cfg0 = C0("TreeCfg")
    Mig = C0("TreeMig33")
    ADD_KEY = [str(x) for x in Mig.ADD_KEY]
    ADD_LINE = [str(x) for x in Mig.ADD_LINE]
    RET_KEY = [str(x) for x in Mig.RET_KEY]
    RET_VAL = [str(x) for x in Mig.RET_VAL]
    MARK33 = ADD_LINE[0]
    ck(MK33 in MARK33 and MARK33.startswith("# ") and ADD_KEY[0] == "" and len(RET_KEY) == 78, "M: the 0.3.3 block (marker line first, 78 retired keys)")
    JProps = JClass("java.util.Properties")

    def props_of(b):
        p = JProps()
        p.load(JClass("java.io.ByteArrayInputStream")(b))
        return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())

    def expected_append(old):
        """the model: the old bytes, a missing final newline, one blank line, then the marker + comments + every keyed line the file lacks"""
        pr_ = props_of(old)
        eol = b"\r\n" if b"\r\n" in old else b"\n"
        out_ = old
        if old and not old.endswith(b"\n"):
            out_ += eol
        if old:
            out_ += eol
        miss = [k for k in ADD_KEY if k and k not in pr_]
        for i, (k, l) in enumerate(zip(ADD_KEY, ADD_LINE)):
            if k and k in pr_:
                continue
            if not miss and i > 0:
                continue
            out_ += l.encode("latin-1") + eol
        return out_, len(miss)

    # ------------------------------------------------------------------ L. the default file + a fresh start
    fresh = os.path.join(SCRATCH, "l", "fresh", "mods", "Skyy_SkyyTrees")
    os.makedirs(fresh)
    r1 = start(fresh)
    f1 = open(os.path.join(fresh, "trees.properties"), "rb").read()
    ck(f1 == str(Cfg0.DEFAULTS).encode("utf8") and r1["mig"] == "" and r1["m32"] == "" and r1["m33"] == "", "L: a fresh start writes the 0.3.3 default file, no update runs")
    ck(f1.count(MK33.encode()) == 1 and b"class.nodes.Mage.PA1=true,50,2\n" in f1 and b"class.minLevel.Mage.PA1=20\n" in f1
       and b"class.nodes.Archer.R1" not in f1 and b"class.nodes.Monk.T1=true,3,1\n" in f1 and b"class.nodes.Priest.TS=true,1,0\n" in f1
       and b"class.nodes.Mage.TS" not in f1 and b"class.minLevel.Archer.T6=75\n" in f1, "L: the default class block (paths, Assassin / Monk, TS on the Priest only)")
    s1 = snap(fresh)
    r2 = start(fresh)
    ck(snap(fresh) == s1 and r2["m33"] == "", "L: a second fresh start writes nothing")
    hdr = bridge.get("config:def:SkyyTrees")
    rows = dict((str(r[0]), [str(x) for x in r]) for r in hdr[7])
    ck(len(rows) == 43 and "class.nodes.Assassin" in rows and "class.nodes.Monk" in rows and "PA1" in rows["class.nodes.Mage"][10],
       "L: 43 Server Setup rows (+ class.nodes.Assassin / Monk), the help names the new ids: %d" % len(rows))
    Kit = r2["C"]("TreeKit")
    ck(Kit.checkClassNode("class.nodes.Mage[PA1]", "true|50|2") is None and Kit.checkClassNode("class.nodes.Monk[PB1]", "true|20|2") is None,
       "L: checkClassNode accepts the new ids of every class")
    ck(str(Kit.checkClassNode("class.nodes.Archer[TS]", "true|1|0")).startswith("?TS is only on the Priest tree")
       and str(Kit.checkClassNode("class.nodes.Archer[L3]", "true|8|2")).startswith("?L3 was a 0.3.2 lane node")
       and str(Kit.checkClassNode("class.nodes.Monk[T1]", "true|80|1")).startswith("?Light Step would give +80% move speed"),
       "L: checkClassNode asks about the hidden switch, a retired id, a big move speed")
    ck(Kit.checkClassLevel("class.minLevel[Assassin.PC4]", "65") is None and str(Kit.checkClassLevel("class.minLevel[Warrior.TS]", "1")).startswith("?TS is only"),
       "L: checkClassLevel: Assassin known, the hidden switch asked")

    # ------------------------------------------------------------------ M. TreeMig33 on copies of the live folder
    ck(MK33.encode() not in live_before and b"skyytrees-0.3.2-classon" in live_before, "M: the live file is a 0.3.2 file (the update is for it)")
    lc = case("live", live_before)
    s0 = snap(lc)
    a = start(lc)
    sa = snap(lc)
    ch = changed(s0, sa)
    bak = [k for k in ch if k.startswith("config-history/") and k.endswith(".bak")]
    ck(ch == sorted(["trees.properties", "config-history/index.log"] + bak) and len(bak) == 1,
       "M live: start 1 writes only trees.properties + one History copy + index.log (no change-log line): %s" % ch)
    ck(len(bak) == 1 and sa[bak[0]] == live_before, "M live: the History copy = the old bytes")
    want, nmiss = expected_append(live_before)
    ck(sa["trees.properties"] == want, "M live: the new file = the old bytes + exactly the missing class lines (%d keyed)" % nmiss)
    ck(sa["trees.properties"].startswith(live_before) and props_of(sa["trees.properties"]).items() >= props_of(live_before).items(),
       "M live: every old key keeps its value (the retired lines byte for byte)")
    ck(a["m33"].startswith("trees.properties updated for SkyyTrees 0.3.3: %d line(s) added" % nmiss) and "retired class line(s)" in a["m33"],
       "M live: the INFO lines (added + the retired lines kept): %r" % a["m33"][:200])
    Ca = a["C"]
    Cla = Ca("TreeClass")
    jmin = dict(("%s.%s" % (CLASSES[j // 44], MID[j % 44]), int(Ca("TreeCfg").C_MIN[j])) for j in range(7 * 44))
    ck(jmin["Mage.PA1"] == 20 and jmin["Archer.T6"] == 75 and jmin["Monk.T2"] == 10 and jmin["Priest.TS"] == 1 and jmin["Warrior.LE"] == 75,
       "M live: the appended level gates apply at this start (TreeCfg reloaded): %s" % dict((k, jmin[k]) for k in ("Mage.PA1", "Archer.T6", "Monk.T2", "Priest.TS")))
    b_ = start(lc)
    ck(changed(sa, snap(lc)) == [] and b_["m33"] == "", "M live: start 2 writes nothing (the marker)")
    ck(bool(Ca("TreeCfg").HAS33) and bool(b_["C"]("TreeCfg").HAS33), "M live (fix 2): the appended lines are seen (HAS33)")
    lg = [str(x) for x in b_["C"]("CfgFn")().apply(jarr(["log", Integer.valueOf(50)]))]
    ck(not [x for x in lg if "SkyyTrees 0.3.3" in x], "M live: no change-log line (no value changed)")
    ck(open(LIVE_TP, "rb").read() == live_before and snap(live) == live_snap, "M: the LIVE folder was never written")

    def two(name, body, extra=None, rm=(), kit=True):
        base = case(name, body, extra, rm)
        x0 = snap(base)
        x = start(base, kit=kit)
        xa = snap(base)
        y = start(base, kit=kit)
        xb = snap(base)
        return base, x0, x, xa, y, xb

    crlf = live_before.replace(b"\n", b"\r\n")
    base, x0, x, xa, y, xb = two("crlf", crlf)
    t = xa["trees.properties"]
    ck(t == expected_append(crlf)[0] and t.count(b"\n") == t.count(b"\r\n") and changed(xa, xb) == [], "M CRLF: appended with CRLF, start 2 nothing")
    nonl = live_before.rstrip(b"\n")
    base, x0, x, xa, y, xb = two("no final newline", nonl)
    ck(xa["trees.properties"] == expected_append(nonl)[0] and xa["trees.properties"].startswith(nonl + b"\n\n"), "M no final newline: one added first")
    adm = live_before + b"class.nodes.Mage.PA1=true,75,2\nclass.minLevel.Monk.T1=1\n"
    base, x0, x, xa, y, xb = two("admin lines", adm)
    t = xa["trees.properties"]
    ck(t.count(b"class.nodes.Mage.PA1=") == 1 and b"class.nodes.Mage.PA1=true,75,2\n" in t and t.count(b"class.minLevel.Monk.T1=") == 1
       and t == expected_append(adm)[0], "M an admin's new-key lines are kept, never appended again")
    jm = x["C"]("TreeCfg")
    ck(int(jm.C_AMT[2 * 44 + MIX["PA1"]]) == 75 and int(jm.C_MIN[6 * 44 + MIX["T1"]]) == 1, "M the admin's values are the live ones")
    c3 = RET_VAL[RET_KEY.index("class.nodes.Warrior.C3")]
    hand = live_before.replace(b"class.nodes.Warrior.C3=" + c3.encode(), b"class.nodes.Warrior.C3=true,9,2").replace(b"class.minLevel.Archer.R4=50", b"class.minLevel.Archer.R4=40")
    ck(hand != live_before and hand.count(b"true,9,2") == 1 and b"class.minLevel.Archer.R4=40" in hand, "M (a hand-edited retired line made)")
    base, x0, x, xa, y, xb = two("hand-edited retired", hand)
    kept_ = [l for l in x["m33"].split("\n") if "kept - an admin changed it" in l]
    ck(b"class.nodes.Warrior.C3=true,9,2" in xa["trees.properties"] and len(kept_) == 2 and any(l.startswith("class.nodes.Warrior.C3=true,9,2 kept") for l in kept_)
       and any(l.startswith("class.minLevel.Archer.R4=40 kept") for l in kept_) and xa["trees.properties"] == expected_append(hand)[0],
       "M two hand-edited retired lines are named (kept, nothing carried): %r" % kept_)
    base = case("history blocked", live_before)
    shutil.rmtree(os.path.join(base, "config-history"))
    open(os.path.join(base, "config-history"), "wb").write(b"not a folder")
    x = start(base, kit=False)
    ck(x["m33"] == "" and open(os.path.join(base, "trees.properties"), "rb").read() == live_before, "M History blocked: nothing written")
    # fix 2 (critic: a refused append dropped every new level gate): no 0.3.3 class.nodes line in the file = every NEW pair keeps its built-in
    # level; the 0.3.2 pairs keep the 0.3.1 rule (the live file's Archer R2-R4 lines)
    jb_ = x["C"]("TreeCfg")
    clb_ = x["C"]("TreeClass")
    new_ = [j for j in range(7 * 44) if bool(clb_.NEW33[j])]
    ck(not bool(jb_.HAS33) and len(new_) > 100 and all(int(jb_.C_MIN[j]) == int(clb_.CMIN[j]) for j in new_)
       and int(jb_.C_MIN[2 * 44 + MIX["PA1"]]) == 20 and int(jb_.C_MIN[0 * 44 + MIX["T6"]]) == 75 and int(jb_.C_MIN[6 * 44 + MIX["T2"]]) == 10
       and not bool(clb_.NEW33[2 * 44 + MIX["ROOT"]]) and bool(clb_.NEW33[5 * 44 + MIX["ROOT"]]),
       "M History blocked (fix 2): the new nodes keep their built-in level gates while the 0.3.3 lines are missing (%d new pairs, HAS33 %s)" % (len(new_), bool(jb_.HAS33)))
    os.remove(os.path.join(base, "config-history"))
    y = start(base)
    ck(MK33.encode() in open(os.path.join(base, "trees.properties"), "rb").read() and y["m33"] != "", "M History blocked: the next start updates")
    base, x0, x, xa, y, xb = two("empty file", b"")
    t = xa["trees.properties"]
    ck(t.count(MK33.encode()) == 1 and b"class.nodes.Monk.PB1=true,20,2" in t and changed(xa, xb) == [] and x["m33"] == "",
       "M an empty file: the 0.3 block (with the 0.3.3 class lines + marker), TreeMig33 does nothing")
    pre03 = live_before[:live_before.index(b"# ---------- SkyyTrees 0.3 (added once")].rstrip(b"\n") + b"\n"
    base, x0, x, xa, y, xb = two("pre-0.3 file", pre03)
    t = xa["trees.properties"]
    ck(t.startswith(pre03) and t.count(MK33.encode()) == 1 and x["m33"] == "" and b"class.nodes.Archer.R2" not in t and changed(xa, xb) == [],
       "M a pre-0.3 file: the 0.3 block brings the 0.3.3 class block + marker, TreeMig33 does nothing")
    up = sa["trees.properties"]
    # fix 2: after the append the 0.3.1 rule stands for the new pairs too - a deleted class.minLevel row = no level needed
    dele = up.replace(b"class.minLevel.Mage.PA1=20" + bytes([10]), b"")
    ck(dele != up, "M (a deleted Mage.PA1 level row made)")
    base, x0, x, xa, y, xb = two("deleted new level row", dele)
    jd_ = x["C"]("TreeCfg")
    ck(bool(jd_.HAS33) and int(jd_.C_MIN[2 * 44 + MIX["PA1"]]) == 0 and int(jd_.C_MIN[2 * 44 + MIX["PA2"]]) == int(x["C"]("TreeClass").CMIN[2 * 44 + MIX["PA2"]])
       and changed(x0, xa) == [] and changed(xa, xb) == [],
       "M deleted new level row (fix 2): Mage.PA1 needs no level (0.3.1 rule), PA2 keeps its line, nothing written")
    # fix 2: History restore of the pre-0.3.3 file = the gates stay on (built-in) and the next start appends again (the same lines)
    base, x0, x, xa, y, xb = two("history restore", live_before)
    ck(xa["trees.properties"] == want and changed(xa, xb) == [] and bool(x["C"]("TreeCfg").HAS33), "M History restore (fix 2): the next start appends the same lines once")
    base = case("rollback to 0.3.2", up)
    z0 = snap(base)
    z = start(base, j=prev)
    ck(z["on"] and changed(z0, snap(base)) == [], "M rollback: 0.3.2 reads the updated file and writes nothing")

    # ------------------------------------------------------------------ P. player files
    C = K(loader(jar))
    CP = K(loader(prev))
    Sto, Cls, Cops, Cfg, Fx, Msg = C("TreeStore"), C("TreeClass"), C("TreeClassOps"), C("TreeCfg"), C("TreeFx"), C("TreeMsg")
    e0_ = [False] * (7 * 44)
    nl_ = dict((nid_, str(Cops.needLine(e0_[:44], e0_[:44], ci_, MIX[nid_], 80, 50, 0))) for ci_, nid_ in ((4, "TS"), (6, "T1"), (2, "P1"), (6, "T2")))
    ck(nl_["TS"].endswith(" - it is on page 1") and nl_["T1"].endswith(" - it is on page 1") and "page" not in nl_["P1"] and "page" not in nl_["T2"]
       and nl_["T1"].startswith("Needs: "),
       "P needLine (fix 2): T1 / TS (page 2) name the Root's page when it is missing; same-page parents do not: %s" % nl_)
    ck(any("cannot heal above 80%" in str(Cls.CNOW[j_]) or "cannot heal above 80%" in str(Cls.CHOW[j_]) for j_ in range(7 * 44)) and not any("you heal to 80%" in str(Cls.CNOW[j_]) for j_ in range(7 * 44)),
       "P Guardian's Oath (fix 2): the 80% is a limit, not a heal")
    SP = CP("TreeStore")
    pdir = os.path.join(SCRATCH, "p", "players")
    shutil.copytree(os.path.join(live, "players"), pdir)
    Sto.DIR = path(pdir)
    SP.DIR = path(pdir)
    JP = JClass("java.util.Properties")

    def props(f):
        p = JP()
        ins = JClass("java.io.FileInputStream")(f)
        try:
            p.load(ins)
        finally:
            ins.close()
        return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())

    keys = sorted(f[:-11] for f in os.listdir(pdir) if f.endswith(".properties"))
    ck(len(keys) >= 1, "P: live player files copied: %d" % len(keys))
    for k in keys:
        fp = os.path.join(pdir, k + ".properties")
        before = props(fp)
        d = Sto.readFile(k)
        ck(not bool(d.bad) and not bool(d.mig) and not any(bool(x) for x in d.cown) and not any(bool(x) for x in d.cfree) and all(x is None for x in d.cret),
           "P %s: a live save: no class picks, no migration, nothing retired" % k)
        Sto.DATA.clear()
        Sto.install(k, me, d)
        ck(bool(Sto.saveNow(k)) and props(fp) == before, "P %s: saved by 0.3.3 without a change = the same Properties" % k)
    INFO = []

    # the ClassMig33 matrix (made-up files in the same folder layout)
    def mk(name, lines):
        fp = os.path.join(pdir, name + ".properties")
        open(fp, "w", newline="\n").write("v=2\nquiet=false\n" + "".join(l + "\n" for l in lines))
        return fp

    MAT = [
        ("lanes-warrior", ["Class.Warrior=ROOT,P1,L1,L2,C1", "Class.Warrior.respecAt=12345"],
         {"Warrior": ("L1,L2,C1", 3)}, {"Class.Warrior": "ROOT,P1", "Class.Warrior.respecAt": "12345"}),
        ("lanes-all5", ["Class.Archer=ROOT,R1,R2,R3,R4", "Class.Mage=ROOT,P1,L1,L2,L3,L4", "Class.Priest=ROOT,C1,C2,C3", "Class.Berserker=ROOT,R1",
                        "Class.Warrior=ROOT"],
         {"Archer": ("R1,R2,R3,R4", 7), "Mage": ("L1,L2,L3,L4", 7), "Priest": ("C1,C2,C3", 4), "Berserker": ("R1", 1)},
         {"Class.Archer": "ROOT", "Class.Mage": "ROOT,P1", "Class.Priest": "ROOT", "Class.Berserker": "ROOT", "Class.Warrior": "ROOT"}),
        ("capstones-only", ["Class.Mage=ROOT,LS,CS"], {"Mage": ("LS,CS", 0)}, {"Class.Mage": "ROOT"}),          # fix 2: 0 AP = no free respec / notice
        ("dupes", ["Class.Warrior=ROOT,L1,L1,C1,l1"], {"Warrior": ("L1,C1", 2)}, {"Class.Warrior": "ROOT"}),          # fix 2: a repeated id counts once
        ("mixed-new", ["Class.Mage=ROOT,T1,PA1,L2"], {"Mage": ("L2", 1)}, {"Class.Mage": "ROOT,T1,PA1"}),
        ("ran-before", ["Class.Mage=ROOT,L1", "Class.Mage.retired=L1,L2"], {}, {"Class.Mage": "ROOT", "Class.Mage.retired": "L1,L2"}),
        ("no-lanes", ["Class.Mage=ROOT,P1,T1"], {}, {"Class.Mage": "ROOT,P1,T1"}),
        ("shaman-alias", ["Class.Shaman=ROOT,L1", "Class.Monk=ROOT,T1"], {}, {"Class.Shaman": "ROOT,L1", "Class.Monk": "ROOT,T1"}),
        ("switch-on", ["Class.Priest=ROOT,TS", "Class.Priest.on=TS", "Class.Archer=ROOT,TS"], {}, {"Class.Priest": "ROOT,TS", "Class.Priest.on": "TS", "Class.Archer": "ROOT"}),
        ("switch-default", ["Class.Priest=ROOT,TS"], {}, {"Class.Priest": "ROOT,TS"}),
        ("switch-on-unowned", ["Class.Priest=ROOT", "Class.Priest.on=TS"], {}, {"Class.Priest": "ROOT"}),
        ("assassin-monk", ["Class.Assassin=ROOT,T1,PC1", "Class.Monk=ROOT,T1,T2"], {}, {"Class.Assassin": "ROOT,T1,PC1", "Class.Monk": "ROOT,T1,T2"}),
    ]
    for name, lines, want_mig, want_lines in MAT:
        fp = mk(name, lines)
        Sto.DATA.clear()
        Sto.DIRTY.clear()
        d = Sto.readFile(name)
        got = {}
        for ci, cn in enumerate(CLASSES):
            if d.cret[ci] is not None and not any(l_.startswith("Class.%s.retired=" % cn) for l_ in lines):          # migrated now (not read back)
                got[cn] = (str(d.cret[ci]), int(d.cnote[ci]))
                ck(bool(d.cfree[ci]) == (int(d.cnote[ci]) > 0), "P %s: %s free respec exactly when AP came back (fix 2)" % (name, cn))
        ck(got == dict((cn, v) for cn, v in want_mig.items()) and bool(d.mig) == bool(want_mig), "P %s: migrated %s (want %s)" % (name, got, want_mig))
        Sto.install(name, me, d)
        if bool(Sto.takeMig(d)):
            Sto.DIRTY.put(name, Boolean.TRUE)
        ck(bool(Sto.DIRTY.containsKey(name)) == bool(want_mig), "P %s: marked to save soon exactly when migrated" % name)
        Sto.saveNow(name)
        pp = props(fp)
        wl = dict(want_lines)
        for cn, (ids, n) in want_mig.items():
            wl["Class.%s.retired" % cn] = ids
            if n > 0:          # fix 2
                wl["Class.%s.freeRespec" % cn] = "1"
                wl["Class.%s.notice" % cn] = str(n)
        cls_lines = dict((k_, v_) for k_, v_ in pp.items() if k_.startswith("Class."))
        ck(cls_lines == wl, "P %s: the saved Class lines %s (want %s)" % (name, cls_lines, wl))
        b1 = open(fp, "rb").read()
        # START TWICE: a fresh read of the saved file changes nothing (the .retired line = the marker)
        Sto.DATA.clear()
        Sto.DIRTY.clear()
        d2 = Sto.readFile(name)
        Sto.install(name, me, d2)
        ck(not bool(d2.mig), "P %s: the second read migrates nothing" % name)
        Sto.saveNow(name)
        ck(props(fp) == pp, "P %s: start twice = the same Properties" % name)
        # rollback: 0.3.2 reads the migrated file and keeps the new lines (cextra) when it saves
        SP.DATA.clear()
        dp = SP.readFile(name)
        SP.install(name, me, dp)
        SP.saveNow(name)
        pr2 = props(fp)
        keep_new = all(pr2.get(k_) == v_ for k_, v_ in wl.items() if k_.split(".")[1] not in ("Monk", "Assassin") and len(k_.split(".")) == 3)
        ck(keep_new and all(pr2.get(k_) == v_ for k_, v_ in wl.items() if k_.split(".")[1] in ("Monk", "Assassin", "Shaman")),
           "P %s: 0.3.2 keeps the .retired / .freeRespec / .notice / .on lines and the Assassin / Monk lines (rollback): %s" % (name, dict((k_, v_) for k_, v_ in pr2.items() if k_.startswith("Class."))))
        open(fp, "wb").write(b1)
    # the notice: taken once (TreeStore.takeNote033 + TreeMsg.note033), the file marked dirty
    fp = mk("notice", ["Class.Warrior=ROOT,L1,L3"])
    Sto.DATA.clear()
    Sto.DIRTY.clear()
    bridge.remove("profile:fn:key")
    d = Sto.readFile("notice")
    ck(int(d.cnote[1]) == 3 and bool(d.cfree[1]), "P notice: pending 3 AP for the Warrior")
    Sto.install(str(me), me, d)
    msgs = []
    try:
        Msg.note033(pr, me)
    except Exception as e:
        msgs.append(str(e)[:120])
    ck(int(d.cnote[1]) == 0 and bool(Sto.DIRTY.containsKey(str(me))), "P notice: note033 took the notice once and marked the file to save (send: %s)" % (msgs or "ok"))
    ck(Sto.takeNote033(d) is None, "P notice: nothing pending afterwards")
    # the free respec: no coins, no cooldown, used once
    COINS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            COINS.append(int(o[1].longValue()))
            return Boolean.TRUE
    bridge.put("coins:fn:take", Coins())
    Cfg.CLASS_ON = True
    d.crespecAt[1] = JClass("java.lang.System").currentTimeMillis()
    ck(int(Cops.priceOf(d, 1, 30, False)) == 0 and bool(Cops.freeOf(d, 1, False)), "P free respec: the price is 0 while the free respec is there")
    r_ = str(Cops.respec(me, d, 1, 30, False))
    ck(r_.startswith("Respec done") and "(your free respec)" in r_ and COINS == [] and not bool(d.cfree[1]) and not any(bool(d.cown[44 + n]) for n in range(44)),
       "P free respec: done without coins and despite the cooldown, used once: %r" % r_)
    Sto.setClassOwn(d, 1, 0, True)
    r2_ = str(Cops.respec(me, d, 1, 30, False))
    ck(r2_.startswith("You can respec your Warrior tree again in") and COINS == [], "P free respec: the next respec waits for the cooldown: %r" % r2_)
    d.crespecAt[1] = 0
    r3_ = str(Cops.respec(me, d, 1, 30, False))
    ck(r3_.startswith("Respec done") and COINS == [3000], "P after it: a respec costs level x 100 again: %r %s" % (r3_, COINS))
    # two paths owned (a hand edit): the path with more AP stays
    jd = C("TreeData")()
    for nid in ("ROOT", "T1", "PA1", "PB1", "PB2"):
        jd.cown[2 * 44 + MIX[nid]] = True
    it = Cls.intact(jd, 2)
    ck(bool(it[MIX["PB1"]]) and bool(it[MIX["PB2"]]) and not bool(it[MIX["PA1"]]) and int(Cls.keepLane(Cls.ownOf(jd, 2), 2)) == 2,
       "P two paths owned: Light Bender (4 AP) stays, Riftwalker PA1 (2 AP) breaks and refunds")
    jd2 = C("TreeData")()
    for nid in ("ROOT", "T1", "PA1", "PC1"):
        jd2.cown[2 * 44 + MIX[nid]] = True
    it2 = Cls.intact(jd2, 2)
    ck(int(Cls.keepLane(Cls.ownOf(jd2, 2), 2)) == 1, "P two paths, a tie (2 AP each): the lower lane (PA) stays")

    # ------------------------------------------------------------------ L. effects, bonus, readers
    @JImplements("java.util.function.Function")
    class Regen(object):
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, o):
            self.calls.append([str(o[0]), str(o[2]) if len(o) > 2 else None, float(o[3].doubleValue()) if len(o) > 3 else None])
            return Boolean.TRUE

    LVL = {}

    @JImplements("java.util.function.Function")
    class Lv(object):
        @JOverride
        def apply(self, o):
            return Integer.valueOf(LVL.get(str(o[1]), 0))
    bridge.put("skill:fn:level", Lv())

    def as_class(cn, ids, on=()):
        Sto.DATA.clear()
        bridge.put("class:" + str(me), cn)
        dd = C("TreeData")()
        ci = CLASSES.index(cn)
        for nid in ids:
            dd.cown[ci * 44 + MIX[nid]] = True
        for nid in on:
            dd.con[ci * 44 + MIX[nid]] = True
        Sto.DATA.put(str(me), dd)
        return dd

    rg = Regen()
    bridge.put("skill:fn:manaregen", rg)
    bridge.put("tree:reads:SkyyArmory", ",".join("Class." + k for k in ARMORY_019))
    as_class("Warrior", ["ROOT", "T2"])
    ck(float(Cls.stat(me, 0)) == 4 + 8 and float(Cls.stat(me, 2)) == 0.0, "L Warrior Fortitude: + 8 max Health (Root 4)")
    as_class("Mage", ["ROOT", "T1", "T2", "T3", "T5", "P1"])
    ck(float(Cls.stat(me, 2)) == 5 + 10, "L Mage Arcane Reserve: +10 max Mana (+ P1 5)")
    Cls.post(me)
    ck(rg.calls and rg.calls[-1] == ["add", "trees", 10.0], "L Mage Mana Flow: skill:fn:manaregen add trees 10: %s" % rg.calls[-1:])
    as_class("Mage", ["ROOT", "T1", "PA1", "PA2", "PA3", "PA4"])
    ck(float(Cls.stat(me, 2)) == 0.0, "L Riftwalker without Rift Master: no Mana change")
    ck(str(Cls.comingWho(2, MIX["PA5"])) == "SkyyArmory", "L Rift Master waits for SkyyArmory (0.1.9 does not list it)")
    as_class("Mage", ["ROOT", "T1", "PA1", "PA2", "PA3", "PA4", "PA5"])
    ck(float(Cls.stat(me, 2)) == -10.0, "L Rift Master owned (a later SkyyArmory lists it): SkyyTrees takes its 10 max Mana")
    # movement source trees.class
    def move(cn, ids, held=None, crouch=False):
        as_class(cn, ids)
        Fx.classPost(me, held, crouch)
        m = bridge.get("move:" + str(me))
        e = None if m is None else m.get("trees.class")
        return None if e is None else (str(e.get("layer")), round(float(e.get("speed")), 4), round(float(e.get("fallDamage")), 4), round(float(e.get("jump")), 4))
    ck(move("Monk", ["ROOT", "T1", "T2"]) == ("flat", 0.03, -0.1, 0.0), "L Monk Light Step + Soft Landing: speed 0.03, fallDamage -0.10")
    ck(move("Archer", ["ROOT", "T4"]) is None and move("Archer", ["ROOT", "T4"], "Weapon_Crossbow_Iron") == ("flat", 0.04, 0.0, 0.0)
       and move("Archer", ["ROOT", "T4"], "Weapon_Shortbow_Copper") == ("flat", 0.04, 0.0, 0.0) and move("Archer", ["ROOT", "T4"], "Weapon_Sword_Iron") is None,
       "L Archer Light Step: +0.04 only with a bow / crossbow in hand (the entry goes without)")
    ck(move("Assassin", ["ROOT", "T1", "T3", "T4"]) == ("flat", 0.0, -0.15, 0.0) and move("Assassin", ["ROOT", "T1", "T3", "T4"], crouch=True) == ("flat", 0.1, -0.15, 0.0),
       "L Assassin Quiet Feet only while crouching, Nimble -15% fall")
    move("Monk", ["ROOT", "T1"])
    Fx.clearOne(me)
    mm = bridge.get("move:" + str(me))
    ck(mm is None or mm.get("trees.class") is None, "L clearOne removes the trees.class entry")
    Cfg.CLASS_ON = False
    ck(move("Monk", ["ROOT", "T1", "T2"]) is None, "L class trees off: no movement entry")
    Cfg.CLASS_ON = True
    # tree:fn:bonus / level
    Bfn, Lfn = C("TreeBonusFn")(), C("TreeFn")()

    def bon(key):
        return float(Bfn.apply(jarr([me, key])))

    def lev(key):
        return int(Lfn.apply(jarr([me, key])))
    as_class("Mage", ["ROOT", "T1", "T2", "T3"])
    for lv_, want_ in ((15, 2), (29, 2), (30, 3), (42, 4), (55, 5), (99, 5)):
        LVL["Sorcery"] = lv_
        ck(bon("Class.Mage.T3") == want_ and lev("Class.Mage.T3") == 1, "L Long Blink ranks: Sorcery %d -> +%d blocks" % (lv_, want_))
    ck(bon("Class.Mage.T2") == 5 and bon("Class.Mage.PA1") == 0 and bon("Class.Archer.T4") == 0 and bon("Class.Mage.L1") == 0 and bon("Class.Mage.TS") == 0,
       "L tree:fn:bonus: owned = the Amount; unowned / another class / a retired id / the hidden switch = 0")
    as_class("Priest", ["ROOT", "TS"], on=["TS"])
    ck(bon("Class.Priest.TS") == 1 and lev("Class.Priest.TS") == 1, "L the switch ON: Class.Priest.TS = 1 (every player)")
    as_class("Priest", ["ROOT", "TS"])
    ck(bon("Class.Priest.TS") == 0 and lev("Class.Priest.TS") == 0, "L FIX the switch owned with no ON entry = OFF: 0 (party only, the LOCKED default)")
    as_class("Priest", ["TS"])
    ck(bon("Class.Priest.TS") == 0, "L the switch without its Root: broken chain -> 0")
    as_class("Mage", ["ROOT", "T1", "PA1", "PB1", "PB2"])
    ck(bon("Class.Mage.PA1") == 0 and bon("Class.Mage.PB1") == 5, "L a conflicting file: the dropped path answers 0, the kept one its Amount")
    bridge.put("profile:class:" + str(me), "Shaman")
    as_class("Monk", ["ROOT", "T1"])
    bridge.put("profile:class:" + str(me), "Shaman")
    ck(int(Cls.classIdx("Shaman")) == 6 and int(Cls.classIdx(Cls.classOf(me))) == 6 and str(Cls.cmdClass(me, "class")) == "" and str(Cls.cmdClass(me, "monk")) == "",
       "L a 'Shaman' profile = the Monk tree (/tree class opens it)")
    ck(str(Cls.cmdClass(me, "assassin")).startswith("[Trees] Your class is Monk"), "L /tree assassin as a Monk: names your class")
    bridge.remove("profile:class:" + str(me))
    # readers
    ck(str(Cls.comingWho(1, MIX["T1"])) == "the class abilities" and str(Cls.comingLine(1, MIX["T1"])) == "Comes with the class abilities", "L K kind: Comes with the class abilities")
    bridge.put("tree:reads:SkyyClasses", "Class.Warrior.T1")
    ck(str(Cls.comingWho(1, MIX["T1"])) == "", "L K kind: live once SkyyClasses lists the key")
    bridge.remove("tree:reads:SkyyClasses")
    ck(str(Cls.comingWho(1, MIX["T4"])) == "a later build" and str(Cls.comingLine(1, MIX["T4"])) == "Coming in a later build", "L L kind: never live")
    ck(str(Cls.comingWho(2, MIX["PA5"])) == "SkyyArmory" and str(Cls.comingWho(2, MIX["PA1"])) == "", "L A kind: by tree:reads:SkyyArmory")
    bridge.put("gear:tree:readers", "Class.Warrior.T5")
    ck(str(Cls.comingWho(1, MIX["T5"])) == "", "L G kind: the SkyyGear alias key gear:tree:readers counts too")
    bridge.remove("gear:tree:readers")
    # TreeFx.stats on the stand-in stat map (the 0.3.1 harness's set-up): the class Health / Mana in skyytree_health / skyytree_mana
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    for fname, val in (("HEALTH", 1), ("STAMINA", 2), ("MANA", 3)):
        f = DST.class_.getDeclaredField(fname)
        f.setAccessible(True)
        f.setInt(None, val)
    ESMod = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    fi = ESMod.class_.getDeclaredField("instance")
    fi.setAccessible(True)
    fi.set(None, _U.allocateInstance(ESMod.class_))
    FakeCB, FakeSM = JClass("skyytest.FakeCB"), JClass("skyytest.FakeStatMap")
    ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    sm = _U.allocateInstance(FakeSM.class_)
    sm.mods = JClass("java.util.HashMap")()
    sm.val = _U.allocateInstance(ESV.class_)
    cb = _U.allocateInstance(FakeCB.class_)
    cb.comp = sm
    as_class("Berserker", ["ROOT", "T1"])
    v = Fx.compute(me)
    Fx.stats(cb, None, me, v)
    mods = dict((str(k), float(sm.mods.get(k).getAmount())) for k in sm.mods.keySet())
    ck(not bool(Fx.STAT_FAILED) and mods == {"1:skyytree_health": 10.0}, "L TreeFx.stats: Berserker Thick Skin +6 + Root 4 = skyytree_health 10: %s" % mods)
    as_class("Mage", ["ROOT", "P1", "T1", "T2", "T3", "T5", "PA1", "PA2", "PA3", "PA4", "PA5"])
    Fx.stats(cb, None, me, Fx.compute(me))
    mods = dict((str(k), float(sm.mods.get(k).getAmount())) for k in sm.mods.keySet())
    ck(mods == {"1:skyytree_health": 4.0, "3:skyytree_mana": 5.0}, "L TreeFx.stats: Mage P1 5 + Arcane Reserve 10 - Rift Master 10 = skyytree_mana 5: %s" % mods)
    # TreeTick.crouching (Assassin Quiet Feet's input) on a stand-in CommandBuffer holding a real MovementStatesComponent
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    emf = [f_ for f_ in EM.class_.getDeclaredFields() if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()) and f_.getType() == EM.class_]
    for f_ in emf:
        f_.setAccessible(True)
        f_.set(None, _U.allocateInstance(EM.class_))
    MSCc = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
    MS = JClass("com.hypixel.hytale.protocol.MovementStates")
    msc = _U.allocateInstance(MSCc.class_)
    ms = _U.allocateInstance(MS.class_)
    msf = [f_ for f_ in MSCc.class_.getDeclaredFields() if f_.getType() == MS.class_ and not JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers())]
    for f_ in msf:
        f_.setAccessible(True)
        f_.set(msc, ms)
    cb2 = _U.allocateInstance(FakeCB.class_)
    cb2.comp = msc
    Tick = C("TreeTick")
    ms.crouching = True
    c1 = bool(Tick.crouching(cb2, None))
    ms.crouching = False
    c2 = bool(Tick.crouching(cb2, None))
    cb2.comp = None
    c3 = bool(Tick.crouching(cb2, None))
    ck(len(emf) >= 1 and len(msf) >= 1 and c1 and not c2 and not c3, "L TreeTick.crouching reads MovementStates.crouching (true / false / no component): %s %s %s" % (c1, c2, c3))
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================================== parent
EXPECT_CHANGED = {"TreeClass", "TreeClassOps", "TreeCfg", "TreeData", "TreeStore", "TreeFx", "TreeTick", "TreeMsg", "TreePage", "TreeKit",
                  "TreeDefs", "CfgRows", "CfgFn", "CfgFile", "SkyyTreesPlugin", "TreeMig"}   # the kit classes carry the version / rows
EXPECT_SAME = {"TreeAbil", "TreeGather", "TreeSwing", "TreeDmgSys", "TreeFelledFn", "TreeSaver", "TreeOps", "TreeCalc", "TreeMig32", "SaveTask",
               "TreeFn", "TreeBonusFn"}


def parent_k(res):
    t = res["tables"]
    # ---- K1 tables
    check(t["NID"] == MID, "K1: the 44 node ids in order: %s" % t["NID"])
    check(t["CLASSES"] == CLASSES and t["CSKILL"] == CSKILL and t["CMAGIC"] == [cn in MAGIC for cn in CLASSES], "K1: 7 classes, their skills, magic flags")
    check(t["NAP"] == [n[1] for n in MT] and t["NPAGE"] == [n[5] for n in MT] and t["NROW"] == [n[6] for n in MT] and t["NCOL"] == [n[7] for n in MT],
          "K1: AP / page / row / col of every node")
    check(t["NLANE"] == [n[3] for n in MT] and t["NLANEN"] == [n[4] for n in MT] and t["NROLE"] == [n[8] for n in MT], "K1: lanes, lane counts, roles")
    check(t["NPAR1"] == [MIX[n[2][0]] if n[2] else -1 for n in MT] and t["NPAR2"] == [MIX[n[2][1]] if len(n[2]) > 1 else -1 for n in MT],
          "K1: parents (T1 and TS hang off ROOT)")
    check(t["NNEED"] == [MIX[NEED[n[0]]] if n[0] in NEED else -1 for n in MT] and t["NLOCK"] == [MIX[LOCK[n[0]]] if n[0] in LOCK else -1 for n in MT], "K1: needs, locks")
    check(sorted(zip(t["LA"], t["LB"])) == sorted((MIX[a], MIX[b]) for a, b in LINKS), "K1: the %d drawn links" % len(LINKS))
    KN = t["K"]
    for ci, cn in enumerate(CLASSES):
        for n, nid in enumerate(MID):
            j = ci * 44 + n
            k = kind_of(cn, nid)
            check(t["CK"][j] == (0 if k == "-" else KN[k]), "K1: %s %s kind %s (jar %d)" % (cn, nid, k, t["CK"][j]))
            a_ = amt_of(cn, nid)
            if a_ is not None:
                check(t["CAMT"][j] == a_, "K1: %s %s amount %d (jar %d)" % (cn, nid, a_, t["CAMT"][j]))
            check(t["CMIN"][j] == min_of(cn, nid) and t["C_MIN"][j] == min_of(cn, nid) or hidden(cn, nid), "K1: %s %s level gate %d (jar %d)" % (cn, nid, min_of(cn, nid), t["CMIN"][j]))
            check(t["CHID"][j] == hidden(cn, nid), "K1: %s %s hidden %s" % (cn, nid, hidden(cn, nid)))
            rk = RANKS.get((cn, nid), [])
            check([(t["CRKL"][j * 3 + r], t["CRKA"][j * 3 + r]) for r in range(3)] == (rk + [(0, 0)] * 3)[:3], "K1: %s %s ranks" % (cn, nid))
            check(t["CM2"][j] == (-10 if (cn, nid) == ("Mage", "PA5") else 0), "K1: %s %s extra Mana" % (cn, nid))
            check(t["C_AP"][j] == MT[n][1], "K1: %s %s AP default" % (cn, nid))
        check(t["LANE"][ci * 3:ci * 3 + 3] == {"Warrior": ["Guardian", "Warlord", "Juggernaut"], "Archer": ["Trapper", "Sharpshooter", "Stormbow"],
                                               "Mage": ["Riftwalker", "Light Bender", "Arcanist"], "Priest": ["Lightbringer", "Aegis", "Soulweaver"],
                                               "Berserker": ["Warbringer", "Bloodbound", "Smasher"], "Monk": ["Wind Dancer", "Iron Fist", "Serene"],
                                               "Assassin": ["Shadow", "Venom", "Blink"]}[cn], "K1: %s path names %s" % (cn, t["LANE"][ci * 3:ci * 3 + 3]))
    check(t["RET_IDS"] == RETIRED and t["RET_AP"] == [RET_AP[i] for i in RETIRED], "K1: the retired ids + their AP")
    # slots: page 2 column 1 = corner / T-junction / bar / T-junction / bar / corner; every node in its cell
    for n, nd in enumerate(MT):
        k = nd[5] * 54 + nd[6] * 9 + nd[7]
        check(t["SK"][k] == 1 and t["SN"][k] == n, "K1: the slot of %s" % nd[0])
    col1 = [t["SK"][54 + r * 9 + 1] for r in range(6)]
    arms1 = [t["SARMS"][54 + r * 9 + 1] for r in range(6)]
    check(col1 == [4, 4, 3, 4, 3, 4] and arms1 == [2 | 8, 1 | 4 | 8, 0, 1 | 4 | 8, 0, 1 | 4], "K1: the column-2 bars of page 2: %s %s" % (col1, arms1))
    links = list(zip(t["LA"], t["LB"]))
    corner = [(t["PL1"][q], t["PL2"][q], t["PL3"][q]) for q in range((54 + 1) * 8, (54 + 2) * 8)]
    path_links = sorted(links.index((MIX["T1"], MIX[p])) for p in ("PA1", "PB1", "PC1"))
    check(any(sorted(c) == path_links for c in corner), "K1: T1's corner pieces carry all three path links")
    check(all(any(li in (t["PL1"][q], t["PL2"][q], t["PL3"][q]) for q in range(len(t["PL1"]))) for li in range(len(links))), "K1: every link is drawn")
    # ---- K2 fuzz
    nf = 0
    for rec in res["fuzz"]:
        cn = CLASSES[rec["ci"]]
        sit = sit_of(rec["s"])
        own = set(rec["own"])
        it, ps = m_reach(own, cn, sit)
        sk = m_skips(own, cn, sit)
        ok = (set(rec["it"]) == it and set(rec["ps"]) == ps and set(rec["sk"]) == sk and rec["path"] == m_path(it) and rec["keep"] == m_keep(own, cn))
        if ok:
            reasons = [m_reason(own, it, cn, nid, rec["lvl"], rec["apf"], sit) for nid in MID]
            states = [m_state(own, it, cn, nid, rec["lvl"], rec["apf"], sit) for nid in MID]
            cards = [m_card(own, it, cn, nid, rec["lvl"], rec["apf"], sit) if True else "" for nid in MID]
            # the jar's cardText (not cardText2) shows "Owned" for an owned switch
            cards = ["Owned" if (MID[i] == "TS" and states[i] == 2) else c for i, c in enumerate(cards)]
            whos = [m_who(cn, nid, sit) for nid in MID]
            ok = rec["reason"] == reasons and rec["state"] == states and rec["card"] == cards and rec["who"] == whos
            spent = sum(MT[MIX[x]][1] for x in it)
            ok = ok and rec["spent"] == spent
            for i, nid in enumerate(MID):
                if rec["reason"][i] == 11:
                    ok = ok and "respec to change paths" in rec["rtext"][i]
                if rec["reason"][i] == 2 and whos[i] == "the class abilities":
                    ok = ok and rec["rtext"][i].endswith("comes with the class abilities - it cannot be unlocked yet")
        if not ok:
            nf += 1
            if nf <= 6:
                check(False, "K2: %s %s own=%s lvl %d apf %d: jar it=%s ps=%s / model it=%s ps=%s; reasons jar %s model %s; cards jar %s model %s" % (
                    rec["s"], cn, sorted(own), rec["lvl"], rec["apf"], sorted(rec["it"]), sorted(rec["ps"]), sorted(it), sorted(ps),
                    rec["reason"], [m_reason(own, it, cn, nid, rec["lvl"], rec["apf"], sit) for nid in MID], rec["card"],
                    [m_card(own, it, cn, nid, rec["lvl"], rec["apf"], sit) for nid in MID]))
        else:
            check(True, "")
        # gold: a piece is gold when one of its links has both ends lit (jar lit = model it + used passed)
        lit = set(rec["lit"])
        for pg in (0, 1):
            want = [q for q in range(54 * 8) if any(l >= 0 and MID[t["LA"][l]] in lit and MID[t["LB"][l]] in lit
                                                    for l in (t["PL1"][pg * 432 + q], t["PL2"][pg * 432 + q], t["PL3"][pg * 432 + q]))]
            check(rec["gold"][pg] == want, "K2: gold pieces of page %d (%s %s)" % (pg + 1, rec["s"], cn))
    print("K2: %d random owned sets x 44 nodes x 3 reader situations: %d disagreements" % (len(res["fuzz"]), nf))
    check(nf == 0, "K2: the rules agree with the model on every fuzzed set")
    # ---- K3 pages
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    tcolor = eval(re.search(r"^TCOLOR = (\[.*?\])\r?\n", src, re.M).group(1))
    ccolor = eval(re.search(r"^CCOLOR = (\[.*?\])", src, re.M).group(1))
    page_colors = list(tcolor) + list(ccolor)
    counts = H.new_counts()
    for name, rec in res["pages"].items():
        spec, stt = rec["spec"], rec["state"]
        ids = H.check_state("K3 " + name, stt, SUI, counts, page_colors, class_tab=True, class_page=True)
        if ids is None:
            continue
        sets = H.sets_of(stt)
        evs = [e[1] for e in stt["events"]]
        jci = stt["jci"]
        if jci < 0:
            want = "Your class Shaman2 has no skill tree yet" if spec.get("pcls") == "Shaman2" else "Choose a class with /class"
            check(sets.get("SkyyTrNoClass", "").startswith(want), "K3 %s: the no-class text %r" % (name, sets.get("SkyyTrNoClass")))
            continue
        cn = CLASSES[jci]
        check(spec.get("pcls") != "Shaman" or cn == "Monk", "K3 %s: a Shaman profile shows the Monk tree" % name)
        cp = stt["cpage"]
        sit = sit_of(spec.get("sname", "today"))
        own = set(stt["jown"])
        lvl = 30 if spec.get("probe") else spec.get("lvl", 30)
        it, ps = m_reach(own, cn, sit)
        apf = m_ap(lvl) - sum(MT[MIX[x]][1] for x in it)
        for n, nd in enumerate(MT):
            if nd[5] != cp:
                continue
            want = m_card(own, it, cn, nd[0], lvl, apf, sit, on=spec.get("on", ()))
            got = sets.get("SkyyTrC%dSb" % (n + 1))
            if hidden(cn, nd[0]):
                check(got is None and ("#SkyyTrC%d" % (n + 1)) not in evs, "K3 %s: the hidden switch slot stays empty" % name)
                continue
            check(got == want and stt["jcards"][n] == want, "K3 %s: %s card %r (model %r, jar %r)" % (name, nd[0], got, want, stt["jcards"][n]))
        check(sets.get("SkyyTrLvl") == "%s %d" % (CSKILL[jci], lvl), "K3 %s: level label %r" % (name, sets.get("SkyyTrLvl")))
        check(sets.get("SkyyTrTok") == "Ability Points %d of %d" % (apf, m_ap(lvl)), "K3 %s: AP label %r (want %d of %d)" % (name, sets.get("SkyyTrTok"), apf, m_ap(lvl)))
        pth = m_path(it)
        lane_names = res["tables"]["LANE"][jci * 3:jci * 3 + 3]
        want_note = ("Path: " + lane_names[pth - 1]) if pth else "No path yet - your first path node picks it"
        check(want_note in sets.get("SkyyTrNote", ""), "K3 %s: the note names the path %r" % (name, sets.get("SkyyTrNote")))
        if spec.get("free"):
            check(sets.get("SkyyTrDust") == "Respec free (once)", "K3 %s: the free respec label %r" % (name, sets.get("SkyyTrDust")))
        buy = [txt for t_, s_, d_, txt in stt["commands"] if t_ == "AppendInline" and txt and "#SkyyTrBuy {" in txt]
        if name.startswith("Priest switch on") or name.startswith("Priest switch off"):
            on = name == "Priest switch on"
            check(len(buy) == 1 and 'Text: "Switch"' in buy[0] and sets.get("SkyyTrDetState") == ("Owned - switch ON" if on else "Owned - switch OFF")
                  and sets.get("SkyyTrDetNow", "").startswith("Now: ON" if on else "Now: OFF - party members only"), "K3 %s: the Switch button + state %r / %r" % (name, sets.get("SkyyTrDetState"), sets.get("SkyyTrDetNow")))
        sel = MID[stt["csel"]] if 0 <= stt["csel"] < 44 else None
        if sel and m_who(cn, sel, sit) == "the class abilities" and sel not in own:
            check(sets.get("SkyyTrDetState") == "Comes with the class abilities" and sets.get("SkyyTrBuyTx") == "Comes with the class abilities",
                  "K3 %s: a waiting ability node says 'Comes with the class abilities' (%r)" % (name, sets.get("SkyyTrDetState")))
    H.report_counts(counts, "K3 class pages:")
    # ---- K4 clicks
    cl = res["clicks"]

    def msgs(nm):
        return [s["msg"] for s in cl[nm]["steps"]]

    def step(nm, i):
        return cl[nm]["steps"][i]
    m = msgs("mage path")
    check(m[1].startswith("Unlocked Root!") and m[4].startswith("Unlocked Mana Flow!") and m[6].startswith("Unlocked Spell Focus!"), "K4 mage: Root, Mana Flow, Spell Focus: %s" % m[:7])
    check(m[8].startswith("Unlocked Blink Slash!") and "You follow the Riftwalker path now" in m[8], "K4 mage: PA1 picks Riftwalker: %r" % m[8])
    check(m[10] == "Prism is on the Light Bender path - you follow Riftwalker - respec to change paths" and "PB1" not in step("mage path", 10)["own"]
          or m[10].startswith("Radiant Trail is on the Light Bender path - you follow Riftwalker"), "K4 mage: PB1 refused (path locked): %r" % m[10])
    check(m[12].startswith("Unlocked Rift Echo!"), "K4 mage: PA2: %r" % m[12])
    check(m[13].startswith("Undo done - Rift Echo") and m[14].startswith("Undo done - Blink Slash"), "K4 mage: Undo twice frees the path: %s" % m[13:15])
    check(m[16].startswith("Unlocked Radiant Trail!") and "Light Bender" in m[16], "K4 mage: after Undo PB1 picks Light Bender: %r" % m[16])
    check(m[18].startswith("Blink Slash is on the Riftwalker path - you follow Light Bender"), "K4 mage: now PA1 is the locked one: %r" % m[18])
    check(m[19].startswith("Click Respec again within 10 s") and m[20].startswith("Respec done") and step("mage path", 20)["coins"] == [3000]
          and step("mage path", 20)["own"] == [], "K4 mage: respec 30 x 100 coins, everything back: %s %s" % (m[19:21], step("mage path", 20)["coins"]))
    m = msgs("mage waiting")
    check(m[4] == "Mana Flow is coming with SkyySkills - it cannot be unlocked yet" and m[6].startswith("Unlocked Arcane Reserve!")
          and m[8] == "Barrier Lore comes with the class abilities - it cannot be unlocked yet" and m[10] == "Blink Slash is coming with SkyyArmory - it cannot be unlocked yet"
          and m[12] == "Prism comes with the class abilities - it cannot be unlocked yet", "K4 mage, no readers: the waiting answers + T5 through the skipped T1-T4: %s" % m)
    m = msgs("warrior skip")
    check(m[4] == "Shield Training comes with the class abilities - it cannot be unlocked yet" and m[6].startswith("Unlocked Fortitude!")
          and m[8].startswith("Shield Wall comes with the class abilities") and m[10].startswith("Plate Mastery is coming with SkyyGear"), "K4 warrior: %s" % m)
    m = msgs("priest switch")
    s = cl["priest switch"]["steps"]
    check(m[4].startswith("Unlocked Open Aura! 0 AP spent") and s[4]["bonusTS"] == 0.0 and s[4]["on"] == [], "K4 priest FIX: Open Aura bought (0 AP) starts OFF = party only: %r %r" % (m[4], s[4]))
    check(m[5].startswith("Open Aura is ON") and s[5]["on"] == ["TS"] and s[5]["bonusTS"] == 1.0, "K4 priest FIX: first Switch -> ON (every player): %r" % m[5])
    check(m[6].startswith("Open Aura is OFF - Guardian Spirit saves party members only") and s[6]["on"] == [] and s[6]["bonusTS"] == 0.0
          and m[7].startswith("Open Aura is ON") and s[7]["bonusTS"] == 1.0, "K4 priest: Switch -> OFF -> ON")
    check(s[5]["dirty"] and "TS" in s[7]["own"], "K4 priest: the flip marks the file to save; still owned")
    check(m[8].startswith("Undo done - Open Aura") and "TS" not in s[8]["own"] and s[8]["on"] == [] and s[8]["bonusTS"] == 0.0, "K4 priest: Undo the switch: %r" % m[8])
    m = msgs("priest gentle hands")
    check(m[4].startswith("Unlocked Gentle Hands!") and m[6].startswith("Unlocked Open Aura!"), "K4 priest: Gentle Hands (SkyyArmory lists it) + the switch: %s" % m)
    m = msgs("mage hidden")
    check(m[3] == "No such node" and cl["mage hidden"]["steps"][3]["own"] == ["ROOT"], "K4 a crafted click on the Mage's hidden switch: refused %r" % m[3])
    m = msgs("free respec")
    s = cl["free respec"]["steps"]
    check("free" in m[1] and m[2].startswith("Respec done") and "(your free respec)" in m[2] and s[2]["coins"] == [] and not s[2]["free"],
          "K4 free respec: free + despite the cooldown, once: %s" % m[1:3])
    check(m[6].startswith("You can respec your Assassin tree again in") or m[6].startswith("Click Respec"), "K4 after the free respec the cooldown holds: %s" % m[5:7])
    m = msgs("paid respec")
    check(m[1].endswith("it costs 2,200 coins (Discipline 22 x 100)") and m[2].startswith("Respec done") and cl["paid respec"]["steps"][2]["coins"] == [2200],
          "K4 Monk respec 22 x 100: %s" % m)
    m = msgs("level gates")
    check(m[4] == "Light Step needs Discipline 5 (you are 4)" and m[5].startswith("Unlocked Light Step!") and m[7] == "Soft Landing needs Discipline 10 (you are 6)"
          and m[8].startswith("Unlocked Soft Landing!"), "K4 Monk level gates 5 / 10: %s" % m)
    m = msgs("assassin blink")
    check(m[4].startswith("Unlocked Quiet Feet!") and m[6].startswith("Unlocked Long Throw!") and "Blink path" in m[6] and m[8].startswith("Unlocked Hard Return!")
          and m[10].startswith("Unlocked Double Step!") and m[12].startswith("Unlocked Blink Strike!")
          and m[14] == "Shadow Blink comes with the class abilities - it cannot be unlocked yet"
          and m[16].startswith("Longer Cloak comes with the class abilities"), "K4 Assassin Blink path through SkyyArmory's keys: %s" % m)


def main():
    if "--load" in sys.argv:
        run_load(arg("--load"), arg("--out"))
        return
    if "--tstates" in sys.argv:
        run_tstates(arg("--tstates"), arg("--out"), arg("--tag"))
        return
    if "--cls" in sys.argv:
        run_cls(arg("--cls"), arg("--out"))
        return
    if "--bytecode" in sys.argv:
        H.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    if "--mkfake" in sys.argv:
        H.run_mkfake(arg("--mkfake"))
        return
    if "--logic" in sys.argv:
        run_logic(arg("--logic"), arg("--prev"), arg("--fake"), arg("--live"), arg("--out"))
        return
    if "--audit" in sys.argv:
        H.run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first (without --deploy)" % j)
    root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == root or not here.startswith(root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/, not %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    live_tp = open(os.path.join(LIVE_DIR, "trees.properties"), "rb").read()
    live_players = dict((f, open(os.path.join(LIVE_DIR, "players", f), "rb").read()) for f in os.listdir(os.path.join(LIVE_DIR, "players")))

    def child(args_, out_):
        p = subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stderr=subprocess.PIPE, encoding="utf8", errors="replace")
        err = "".join(l + "\n" for l in (p.stderr or "").splitlines() if "Picked up JAVA_TOOL_OPTIONS" not in l)
        if err.strip():
            sys.stderr.write(err[-4000:])
        check("mutated reflectively" not in (p.stderr or ""), "F: %s mutated no final field without the JEP 500 option" % args_[0])
        return p.returncode == 0 and os.path.isfile(out_)
    try:
        # ---- A
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            o = os.path.join(SCRATCH, "load-%s.json" % tag)
            ok = child(["--load", j], o)
            r = json.load(open(o)) if ok else {"classes": 0, "fails": ["child failed"]}
            check(not r["fails"] and r["classes"] > 0, "A: %s: %d classes load, verify and initialise %s" % (os.path.basename(j), r["classes"], r["fails"][:3]))
            print("A: %s: %d classes under -Xverify:all" % (os.path.basename(j), r["classes"]))
        # ---- E
        bc = os.path.join(SCRATCH, "bytecode.json")
        p = subprocess.run([sys.executable, me, "--bytecode", PREV_JAR, "--new", JAR, "--out", bc, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(bc), "E: bytecode child ran")
        zp, zn = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
        added = sorted(set(zn.namelist()) - set(zp.namelist()))
        gone = sorted(set(zp.namelist()) - set(zn.namelist()))
        check(added == ["com/skyy/trees/TreeMig33.class"] and gone == [], "E: added exactly TreeMig33, nothing removed: %s %s" % (added, gone))
        diff = sorted(n for n in set(zp.namelist()) & set(zn.namelist()) if zp.read(n) != zn.read(n))
        dcls = set(n.split("/")[-1][:-6] for n in diff if n.endswith(".class"))
        check(not (dcls & EXPECT_SAME), "E: the template-tree classes are byte-identical: changed %s" % sorted(dcls & EXPECT_SAME))
        check(dcls <= EXPECT_CHANGED and [n for n in diff if not n.endswith(".class")] == ["manifest.json"], "E: changed classes %s" % sorted(dcls))
        if os.path.isfile(bc):
            res = json.load(open(bc))
            for n, v in sorted(res.items()):
                c = n.split("/")[-1][:-6]
                print("E: %s changed %d methods %s, new %s, gone %s, fields new %s gone %s" % (c, len(v["changed"]), [m.split("(")[0] for m in v["changed"]][:8], [m.split("(")[0] for m in v["new"]],
                                                                                      [m.split("(")[0] for m in v["gone"]], v["fields_new"][:6], v["fields_gone"]))
            mg = res.get("com/skyy/trees/TreeMig.class", {})
            check(set(m.split("(")[0] for m in mg.get("changed", [])) <= {"<clinit>"} and not mg.get("gone"), "E: TreeMig changes only its static block (the 0.3 block's class lines)")
            ops = res.get("com/skyy/trees/TreeClassOps.class", {})
            check(not res.get("com/skyy/trees/TreeData.class", {}).get("fields_gone"), "E: TreeData loses no field (a saved file reads the same)")
        # ---- T: the template trees, both jars
        tn = os.path.join(SCRATCH, "tstates-new.json")
        tp = os.path.join(SCRATCH, "tstates-prev.json")
        check(child(["--tstates", JAR, "--tag", "new"], tn) and child(["--tstates", PREV_JAR, "--tag", "prev"], tp), "T: template state children ran")
        if os.path.isfile(tn) and os.path.isfile(tp):
            a, b = json.load(open(tn)), json.load(open(tp))
            check(not a["load_fails"] and not b["load_fails"], "T: both jars load in the state child")
            for part in ("clicks", "nclicks"):          # the per-class respec times grow 5 -> 7 classes: compare the 5 old ones
                for side in (a, b):
                    for v_ in side.get(part, {}).values():
                        for st_ in v_["steps"]:
                            if "crespec" in st_:
                                st_["crespec"] = st_["crespec"][:5]
            for part in ("states", "real", "clicks", "nclicks", "colors"):
                ka, kb = a.get(part, {}), b.get(part, {})
                same = [k for k in ka if kb.get(k) == ka[k]]
                diffk = sorted(k for k in set(ka) | set(kb) if ka.get(k) != kb.get(k))
                check(not diffk and len(ka) > 0 or part == "colors" and not diffk, "T: %s byte-identical in 0.3.2 and 0.3.3 (%d; differ: %s)" % (part, len(ka), diffk[:5]))
                print("T: %s: %d identical, %d differ" % (part, len(same), len(diffk)))
            counts = H.new_counts()
            import skyyui as SUI
            SUI.verify(quiet=True)
            src = open(SCRIPT, encoding="utf8").read()
            tcolor = eval(re.search(r"^TCOLOR = (\[.*?\])\r?\n", src, re.M).group(1))
            ccolor = eval(re.search(r"^CCOLOR = (\[.*?\])", src, re.M).group(1))
            for nm, stt in list(a["states"].items())[:400]:
                H.check_state("T " + nm, stt, SUI, counts, list(tcolor) + list(ccolor))
            H.report_counts(counts, "T template pages (0.3.3):")
        # ---- K
        kc = os.path.join(SCRATCH, "cls.json")
        check(child(["--cls", JAR], kc), "K: the class child ran")
        if os.path.isfile(kc):
            parent_k(json.load(open(kc)))
        # ---- L M P
        fake = os.path.join(SCRATCH, "fake")
        p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
        check(p.returncode == 0, "stand-in classes generated")
        lo = os.path.join(SCRATCH, "logic.json")
        p = subprocess.run([sys.executable, me, "--logic", JAR, "--prev", PREV_JAR, "--fake", fake, "--live", LIVE_DIR, "--out", lo, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(lo), "logic child ran")
        if os.path.isfile(lo):
            r = json.load(open(lo))
            OKS[0] += r["oks"]
            for f in r["fails"]:
                FAILS.append(f)
            print("L / M / P: %d checks, %d failed" % (r["oks"] + len(r["fails"]), len(r["fails"])))
        # ---- Z
        au = os.path.join(SCRATCH, "audit.json")
        p = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", au, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(au), "Z: audit child ran")
        if os.path.isfile(au):
            z = json.load(open(au))
            check(not z["refused"] and z["refs"] > 10000 and z["control"], "Z: %d references in %d classes, refused %s; control refused %s" % (z["refs"], z["classes"], z["refused"][:3], bool(z["control"])))
            print("Z: %d references in %d classes, %d refused (control refused: %s)" % (z["refs"], z["classes"], len(z["refused"]), bool(z["control"])))
        check(open(os.path.join(LIVE_DIR, "trees.properties"), "rb").read() == live_tp
              and dict((f, open(os.path.join(LIVE_DIR, "players", f), "rb").read()) for f in os.listdir(os.path.join(LIVE_DIR, "players"))) == live_players,
              "the live trees.properties and player files are unchanged")
    finally:
        if not KEEP:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s vs %s: %d checks passed, %d failed" % (VERSION, PREV_VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyTrees %s bare-JVM harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
