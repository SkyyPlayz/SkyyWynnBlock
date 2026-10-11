"""Harness for SkyyGear 0.2.12 (TOOLS DO SOMETHING - Mining / Chopping Power + Fortune by tool level, the real tool tooltip; Skyy
2026-10-05 "axes and pickaxes have the levels, now they need to actually do something." + 2026-10-09 "tools still dont have chopping speed,
and foraging fortune. or tree feller"). Build first: python tools/gear_0_2_12_patch.py && python SkyyGear/build_skyygear_0.2.12.py

    python SkyyGear/test_skyygear_0.2.12.py [--jar <SkyyGear-0.2.12.jar>] [--old <SkyyGear-0.2.11.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py and run on the 0.2.12 jar. The carried 0.2.10 ... 0.1 chain is NOT re-run (its old-jar compares need
jars that are no longer kept; every 0.2.11 class except the listed ones is byte-for-byte the same code - C proves it).
  F  stand-ins (FakeChunk / FakeStore / LookupIn / BadAccess ...)
  A  every class of the jar loads + verifies (-Xverify:all)
  V  the vanilla pack store by store + THE JAR as its own pack (real Item / BlockType stores for X): no failed store of its own
  X  EVERY NEW CODE PATH EXECUTED on the real stores (-Xverify:all): X0 rows + the fresh file + clamps; X1 fam / row / tier of every vanilla
     tool (and weapon axes / Skyy items = not tools); X2 power + Fortune per tier vs the python formula (+ cap, part off); X3 TOOLTIP lines
     per tier for every vanilla hatchet / pickaxe + shovel / hoe / sickle (met = green, under-level = red + "(you: N)" + the no-bonus line,
     no owner = neutral, part.tools off, never "coming later"); X4 the block hit: GearTool.onDamage on REAL DamageBlockEvent / BlockType /
     ItemStack objects - hatchet on a log (x factor) vs on stone (vanilla), a WEAPON AXE on a log (vanilla), pickaxe on stone / ore / log,
     shovel on soil, hoe, an under-level tool (vanilla), an old tool without a level (min(level, skill)), no SkyySkills - and the REAL
     GearToolHitSys.handle through a stand-in chunk (normal, cancelled, no player); X5 the bridge skill:bonus:<uuid>["gear"]: the post
     (dd.<skill> = Fortune / 100), another source kept, the container made when absent (older partner), swap to a non-tool / under-level /
     profile:busy = removed, held() caches 1 s per stack, forget + clearAll; X6 status / counters text
  C  CLASS COMPARE 0.2.11 -> 0.2.12 (javassist members): exactly GearTool + GearToolHitSys added, only the planned classes changed; the
     non-class entries: only manifest.json
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder (setup()'s config order): the file is byte-identical (new keys = no
     one-time update), the tool rows read their defaults
  AA THE ENGINE-ACCESS AUDIT (every bytecode reference looked up with the JVM's own access rules; the control is refused)
Scratch: tools/dev/scratch/tools01fix2/gear (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.12"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.join(TOOLS, "dev", "scratch", "tools01fix2")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "gear")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(SCR_ROOT, "SkyyGear-0.2.11.jar")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
NEW_CLASSES = ["GearTool", "GearToolHitSys"]
EXPECT_CHANGED = {"CfgRows", "Gear", "GearBye", "GearReady", "GearCfg", "GearHandSys", "GearView", "SkyyGearPlugin", "CfgFile", "CfgFn"}
TOOL_KEYS = ["part.tools", "tool.power.pickaxe", "tool.power.hatchet", "tool.power.matBonus", "tool.fortune.perLevel", "tool.fortune.perLevelFarm",
             "tool.fortune.matBonus", "tool.fortune.cap"]
PICK_DEF = "1:1.0,10:1.25,20:1.5,30:1.75,40:2.0,49:2.2,100:3.0"
HATCH_DEF = "1:1.0,10:1.2,20:1.45,30:1.65,40:1.85,49:2.0,100:2.6"
TIERS = {"Crude": 0, "Wood": 0, "Copper": 1, "Scrap": 1, "Bronze": 2, "Iron": 2, "Steel": 2, "Thorium": 3, "Cobalt": 4, "Adamantite": 5,
         "Mithril": 6, "Onyxium": 7}

# ---- the 0.2.11 harness's helpers, run on THIS jar (its module text without its main call)
_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
sys.argv_saved = list(sys.argv)
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR, FAKE_PKG = H["FAKE_DIR"], H["FAKE_PKG"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def tier_of(i):
    for w in i.split("_")[2:]:
        for n, t in TIERS.items():
            if w.lower() == n.lower():
                return t
    return 0


def curve(txt, lv):
    p = [(float(a), float(b)) for a, b in (x.split(":") for x in txt.split(","))]
    if lv <= p[0][0]:
        return p[0][1]
    for (l0, v0), (l1, v1) in zip(p, p[1:]):
        if lv <= l1:
            return v0 + (v1 - v0) * (lv - l0) / (l1 - l0)
    return p[-1][1]


def py_power(fam, lv, t):
    if fam in (1, 2):
        c = PICK_DEF
    elif fam == 3:
        c = HATCH_DEF
    else:
        return 1.0
    return max(1.0, min(100.0, curve(c, lv) * (1.0 + 1.5 / 100.0 * t)))


def py_fortune(fam, lv, t):
    per = 0.3 if fam in (4, 5) else 0.2
    import math
    return math.floor(min(per * lv * (1.0 + 2.0 / 100.0 * t), 25.0) * 10.0 + 0.5) / 10.0   # Java Math.round (half up)


# ====================================================================================================== X (the engine child)
def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JString, JFloat, JDouble, JImplements, JOverride, JObject, JBoolean
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    us, jf, ITEM = E["us"], E["jf"], E["ITEM"]
    # ============================================================================ V
    bad = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING")]
    K.check(set(E["fail"]) <= set(E["vfail"]) and not [r for r in bad if "GearTool" in r[1] or "Tool_" in r[1]],
            "V: the jar as its own pack: no failed store of its own (%s vs vanilla %s); nothing about tools in %d SEVERE / WARNING lines (the 0.2.11 "
            "Selector / Stamina bare-JVM gaps of the speed copies)" % (E["fail"], E["vfail"], len(bad)))
    # ============================================================================ X set-up
    P = lambda n: JClass(PKG + n)
    Cfg, Tool, View, Roll, Data, Defs, Gate, Lvl, Hit, Gear = (P("GearCfg"), P("GearTool"), P("GearView"), P("GearRoll"), P("GearData"), P("GearDefs"),
                                                               P("GearGate"), P("GearLevel"), P("GearToolHitSys"), P("Gear"))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD = JClass("org.bson.BsonDocument")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    sysp = JClass("java.lang.System").getProperties()
    br = CHM()
    sysp.put("skyy.bridge", br)
    Cfg.apply(Props(), False)
    LEVELS = {}

    @JImplements("java.util.function.Function")
    class SkillLv:
        @JOverride
        def apply(self, a):
            return JInt(LEVELS.get(str(a[1]), 0))
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000c001")

    def skills(mining=100, foraging=100, farming=100, on=True):
        LEVELS.clear()
        LEVELS.update({"Mining": mining, "Foraging": foraging, "Farming": farming})
        if on:
            br.put("skill:fn:level", SkillLv())
        else:
            br.remove("skill:fn:level")
        Gate.forget(U1)
        Tool.LAST.clear()

    def stack(iid, lvl=None, q=1):
        s_ = IS(iid, JInt(q))
        if lvl is None:
            return s_
        md = BD()
        md.put(str(Defs.DOC_KEY), Roll.newDoc(iid, JInt(0), True, "craft", JInt(lvl)))
        return s_.withMetadata(md)

    def gsrc():
        o = br.get("skill:bonus:" + str(U1))
        if o is None:
            return None
        g = o.get("gear")
        if g is None:
            return None
        out_ = {}
        for k in g.keySet():
            v_ = g.get(k)
            out_[str(k)] = str(v_) if isinstance(v_, str) or "String" in str(type(v_)) else float(v_)
        return out_

    # ============================================================================ X0 the rows + the fresh file
    dt = str(Cfg.defaultsText())
    tail = dt.strip().split("\n")[-(2 * len(TOOL_KEYS) + 1):]
    K.check(tail[0].startswith("# ---- tools:") and [l.split("=", 1)[0] for l in tail[2::2]] == TOOL_KEYS,
            "X0: the fresh file ends with the tools heading + its 8 rows (help + key=value each): %s" % tail[:3])
    vals = dict(l.split("=", 1) for l in tail[2::2])
    K.check(vals == {"part.tools": "true", "tool.power.pickaxe": PICK_DEF, "tool.power.hatchet": HATCH_DEF, "tool.power.matBonus": "1.5",
                     "tool.fortune.perLevel": "0.2", "tool.fortune.perLevelFarm": "0.3", "tool.fortune.matBonus": "2.0", "tool.fortune.cap": "25.0"},
            "X0: the fresh tool rows hold the spec defaults: %s" % vals)
    K.check(bool(Cfg.PART_TOOLS) and str(Cfg.TOOL_PICK) == PICK_DEF and str(Cfg.TOOL_HATCH) == HATCH_DEF and float(Cfg.TOOL_PMAT) == 1.5
            and float(Cfg.TOOL_FPER) == 0.2 and float(Cfg.TOOL_FFARM) == 0.3 and float(Cfg.TOOL_FMAT) == 2.0 and float(Cfg.TOOL_FCAP) == 25.0,
            "X0: a file with no tool line loads the defaults")
    pr_ = Props()
    for k, v in (("tool.power.pickaxe", "5:2,3:1"), ("tool.power.hatchet", " 1:1.0,20:3.0 "), ("tool.fortune.cap", "5000"), ("tool.fortune.perLevel", "-3"),
                 ("part.tools", "false")):
        pr_.setProperty(k, v)
    Cfg.apply(pr_, True)
    K.check(str(Cfg.TOOL_PICK) == PICK_DEF and str(Cfg.TOOL_HATCH) == "1:1.0,20:3.0" and float(Cfg.TOOL_FCAP) == 1000.0 and float(Cfg.TOOL_FPER) == 0.0
            and not bool(Cfg.PART_TOOLS),
            "X0: a refused curve falls back to its default, a good one is trimmed, numbers are clamped (5000 -> 1000, -3 -> 0), part.tools off reads")
    K.check(Cfg.checkCurve("tool.power.pickaxe", "1:0,10:2") is not None and Cfg.checkCurve("tool.power.pickaxe", PICK_DEF) is None,
            "X0: the Server Setup check refuses a 0 factor and takes the default")
    Cfg.apply(Props(), False)

    # ============================================================================ X1 fam / row / tier of every vanilla tool
    imap = ITEM.getAssetMap().getAssetMap()
    ids = sorted(str(k) for k in imap.keySet())
    fams = {"Tool_Pickaxe_": 1, "Tool_Shovel_": 2, "Tool_Hatchet_": 3, "Tool_Hoe_": 4, "Tool_Sickle_": 5}
    with zipfile.ZipFile(H["ASSETS"]) as az_:
        az_ids = sorted(set(os.path.basename(n)[:-5] for n in az_.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json")))
    tools = [i for i in az_ids if i.startswith(tuple(fams))]
    # fix round: each vanilla tool's own spec power on its reference gather type (pickaxe Rocks, shovel Soils, hatchet Woods), Parent chain
    with zipfile.ZipFile(H["ASSETS"]) as az_:
        AZJ = {}
        for n in az_.namelist():
            if n.startswith("Server/Item/Items/") and n.endswith(".json") and os.path.basename(n).startswith(tuple(fams)):
                try:
                    AZJ[os.path.basename(n)[:-5]] = json.loads(az_.read(n).decode("utf-8-sig"))
                except Exception:
                    pass

    def ref_pw(i):
        cur, seen = i, 0
        while cur in AZJ and seen < 16:
            if "Tool" in AZJ[cur]:
                f_ = [v for p, v in fams.items() if i.startswith(p)][0]
                gt_ = {1: "Rocks", 2: "Soils", 3: "Woods"}.get(f_)
                ps_ = [float(sp.get("Power", 0)) for sp in AZJ[cur]["Tool"].get("Specs", []) if sp.get("GatherType") == gt_]
                return ps_[0] if ps_ else 0.0
            cur, seen = AZJ[cur].get("Parent"), seen + 1
        return 0.0

    import math

    def py_hits(p, m):
        if not (p > 0):
            return -1
        import struct
        d = struct.unpack("f", struct.pack("f", p * m))[0]
        return max(1, int(math.ceil(1.0 / d - 0.000001)))
    K.notes.append("X1: %d vanilla gathering tools in Assets.zip, %d of them in the bare-JVM Item store (%s)" % (
        len(tools), len([i for i in tools if i in ids]), [i for i in ids if i.startswith(tuple(fams))]))
    badf = [(i, int(Tool.fam(i)), int(Tool.tier(i))) for i in tools
            if int(Tool.fam(i)) != [v for p, v in fams.items() if i.startswith(p)][0] or int(Tool.tier(i)) != tier_of(i)]
    K.check(len(tools) >= 30 and not badf, "X1: every vanilla gathering tool in the real store has its family + material tier (%d tools; bad %s)" % (len(tools), badf[:4]))
    axes = [i for i in az_ids if i.startswith(("Weapon_Axe_", "Weapon_Battleaxe_"))]
    K.check(axes and all(int(Tool.fam(i)) == 0 for i in axes) and int(Tool.fam("Skyy_Tool_Pickaxe_X")) == 0 and int(Tool.fam(None)) == 0
            and int(Tool.fam("Tool_Bark_Scraper")) == 0,
            "X1: weapon axes (%d), Skyy items, null and other Tool_* are NOT gathering tools" % len(axes))
    K.check([int(Tool.row(JInt(f))) for f in range(0, 7)] == [-1, 0, 0, 1, 2, 2, -1] and [str(Tool.skill(JInt(f))) for f in (1, 2, 3, 4, 5)]
            == ["Mining", "Mining", "Foraging", "Farming", "Farming"], "X1: rows + gate skills (pickaxe + shovel Mining, hatchet Foraging, hoe + sickle Farming)")

    # ============================================================================ X2 power + Fortune per tier
    bad2 = []
    for f in (1, 2, 3, 4, 5):
        for t in range(0, 8):
            for lv in (1, 5, 10, 13, 18, 20, 23, 28, 35, 40, 49, 60, 100):
                pw, fo = float(Tool.power(JInt(f), JInt(lv), JInt(t))), float(Tool.fortune(JInt(f), JInt(lv), JInt(t)))
                if abs(pw - py_power(f, lv, t)) > 1e-9 or abs(fo - py_fortune(f, lv, t)) > 1e-9:
                    bad2.append((f, t, lv, pw, py_power(f, lv, t), fo, py_fortune(f, lv, t)))
    K.check(not bad2, "X2: power + Fortune for 5 families x 8 tiers x 13 levels = the python formula (%d bad: %s)" % (len(bad2), bad2[:3]))
    K.check(float(Tool.power(JInt(1), JInt(1), JInt(0))) == 1.0 and float(Tool.power(JInt(4), JInt(49), JInt(7))) == 1.0
            and float(Tool.fortune(JInt(5), JInt(100), JInt(7))) == 25.0 and float(Tool.fortune(JInt(3), JInt(49), JInt(6))) == 11.0,
            "X2: Lv 1 Crude = vanilla, hoes / sickles never get power, the cap 25, a Lv 49 Mithril hatchet = Fortune 11.0 (Revision 3)")
    Cfg.PART_TOOLS = False
    K.check(float(Tool.power(JInt(3), JInt(40), JInt(6))) == 1.0 and float(Tool.fortune(JInt(3), JInt(40), JInt(6))) == 0.0, "X2: part.tools off = vanilla, no Fortune")
    Cfg.PART_TOOLS = True

    # ============================================================================ X3 the tooltip per tier
    def tip(iid, lvl, owner):
        txt, col = AL(), AL()
        View.lines(iid, Roll.newDoc(iid, JInt(0), True, "craft", JInt(lvl)), owner, txt, col)
        return [(str(txt.get(i)), None if col.get(i) is None else str(col.get(i))) for i in range(txt.size())]
    OK_C, BAD_C, GRAY = str(Defs.C_OK), str(Defs.C_BAD), str(Defs.C_GRAY)
    tip_ids = [i for i in tools if i.startswith(("Tool_Hatchet_", "Tool_Pickaxe_"))] + [i for i in tools if i.startswith(("Tool_Shovel_", "Tool_Hoe_", "Tool_Sickle_"))]
    bad3, shown, HITS = [], {}, {}
    skills()
    for iid in tip_ids:
        f = [v for p, v in fams.items() if iid.startswith(p)][0]
        lv = int(list(Lvl.band(iid))[0])
        t = tier_of(iid)
        sk = ["", "Mining", "Mining", "Foraging", "Farming", "Farming"][f]
        L = tip(iid, lv, U1)
        alltxt = "\n".join(x for x, c in L)
        want_gate = ("Lv %d - Requires %s %d" % (lv, sk, lv), OK_C)
        want_pw = None
        if f <= 3:
            pw_ = py_power(f, lv, t)
            h_, v_ = py_hits(ref_pw(iid), pw_), py_hits(ref_pw(iid), 1.0)
            want_pw = "%s +%d%%: %d %s per %s (vanilla %d)" % ("Chopping Power" if f == 3 else "Mining Power", int(math.floor((pw_ - 1.0) * 100.0 + 0.5)),
                                                            h_, "hit" if h_ == 1 else "hits", "log" if f == 3 else ("soil block" if f == 2 else "stone"), v_)
            HITS[iid] = (lv, h_, v_)
        fo = py_fortune(f, lv, t)
        fs = ("%d" % fo) if fo == int(fo) else ("%.1f" % fo)
        want_fo = "%s Fortune +%s (%s%% extra %s chance)" % (sk, fs, fs, "log" if f == 3 else ("sand / gravel" if f == 2 else ("rock / ore" if f == 1 else "crop")))
        probs = []
        if L[0] != want_gate:
            probs.append(("gate", L[0], want_gate))
        if want_pw and want_pw not in alltxt:
            probs.append(("power", want_pw))
        if f > 3 and "Power" in alltxt:
            probs.append("a hoe / sickle shows power")
        if want_fo not in alltxt:
            probs.append(("fortune", want_fo))
        if (f == 3) != ("Tree Feller unlocks in the Foraging tree" in alltxt):
            probs.append("tree feller line")
        if "coming later" in alltxt or "No bonus" in alltxt or "NORMAL TOOL" not in alltxt or max(len(x) for x, c in L) > 56:
            probs.append("coming later / no-bonus / NORMAL TOOL")
        if probs:
            bad3.append((iid, probs, L))
        if iid in ("Tool_Hatchet_Iron", "Tool_Pickaxe_Mithril", "Tool_Sickle_Iron"):
            shown[iid] = [x for x, c in L if x]
    K.check(not bad3 and len(tip_ids) >= 30, "X3: the tooltip of %d vanilla tools at their band start (skill 100): green gate line, power (not on hoes / sickles), "
            "Fortune, Tree Feller on hatchets, NORMAL TOOL, never 'coming later' (bad %s)" % (len(tip_ids), bad3[:2]))
    for k_, v_ in shown.items():
        K.notes.append("X3 tooltip %s: %s" % (k_, " | ".join(v_)))
    K.notes.append("X3 hits at band start (level, hits, vanilla): %s" % HITS)
    # fix round (critic C1): the tooltip's hit count follows the level - a Copper hatchet at its band start = vanilla 5 (said honestly),
    # Lv 18 = 4; every vanilla pickaxe / shovel / hatchet has a reference power (no "+X% on logs" fallback for them)
    L10, L18 = tip("Tool_Hatchet_Copper", 10, U1), tip("Tool_Hatchet_Copper", 18, U1)
    K.check(any(x.endswith(": 5 hits per log (vanilla 5)") for x, c in L10) and any(x.endswith(": 4 hits per log (vanilla 5)") for x, c in L18)
            and len(HITS) >= 20 and all(v[1] > 0 and v[2] > 0 and v[1] <= v[2] for v in HITS.values()),
            "X3: the hits line follows the level (Copper hatchet Lv 10 = 5 / vanilla 5, Lv 18 = 4 / vanilla 5); never above vanilla: %s / %s" % (L10[1:2], L18[1:2]))
    K.check(int(Tool.hits(JDouble(0.2), JDouble(1.0))) == 5 and int(Tool.hits(JDouble(0.5), JDouble(2.0))) == 1 and int(Tool.hits(JDouble(0.0), JDouble(2.0))) == -1
            and float(Tool.refPower("Tool_Hatchet_Iron")) == 0.3 and float(Tool.refPower("Skyy_Tool_X")) == 0.0,
            "X3: hits(0.2) = 5, hits(0.5 x2) = 1, no power = -1; refPower Iron hatchet 0.3, unknown 0")
    skills(mining=0, foraging=9, farming=0)
    L = tip("Tool_Hatchet_Iron", 20, U1)
    K.check(L[0] == ("Lv 20 - Requires Foraging 20 (you: 9)", BAD_C) and ("No bonus until Foraging 20", BAD_C) in L
            and any(x.startswith("Chopping Power +") for x, c in L), "X3: under-level: red '(you: 9)' + the no-bonus line, the numbers still shown: %s" % L[:4])
    L = tip("Tool_Pickaxe_Copper", 12, None)
    K.check(L[0] == ("Lv 12 - Requires Mining 12", GRAY) and not [x for x, c in L if "No bonus" in x], "X3: no owner = the neutral grey line, no no-bonus line")
    Cfg.PART_TOOLS = False
    L = tip("Tool_Pickaxe_Copper", 12, U1)
    K.check(L[0] == ("Lv 12 - Requires Mining 12", GRAY) and not [x for x, c in L if "Power" in x or "Fortune" in x or "coming later" in x],
            "X3: part.tools off: grey requirement without 'coming later', no tool lines: %s" % L)
    Cfg.PART_TOOLS = True
    skills(on=False)
    L = tip("Tool_Pickaxe_Copper", 12, U1)
    K.check(L[0][1] == GRAY and not [x for x, c in L if "No bonus" in x], "X3: no SkyySkills: grey requirement, no no-bonus line")

    # ============================================================================ X4 the block hit on REAL engine objects
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()

    def block(i):
        b_ = bmap.get(i)
        K.check(b_ is not None, "X4: the real BlockType %s is in the store" % i)
        return b_
    soils = sorted(str(k) for k in bmap.keySet() if bmap.get(k) is not None and bmap.get(k).getGathering() is not None
                   and bmap.get(k).getGathering().getBreaking() is not None and str(bmap.get(k).getGathering().getBreaking().getGatherType()) == "Soils")
    K.notes.append("X4: %d BlockTypes in the store; Soils blocks e.g. %s" % (bmap.size(), soils[:5]))
    LOG, STONE, ORE, GRASS = block("Wood_Oak_Trunk"), block("Rock_Stone"), block("Ore_Iron_Stone"), block(([x for x in soils if x.startswith("Soil_")] + soils + ["Soil_Grass"])[0])
    K.check(str(LOG.getGathering().getBreaking().getGatherType()) == "Woods" and str(STONE.getGathering().getBreaking().getGatherType()) == "Rocks"
            and str(GRASS.getGathering().getBreaking().getGatherType()) == "Soils", "X4: the blocks carry the gather types the rules read")
    K.check(bool(Tool.onType(JInt(3), LOG)) and not bool(Tool.onType(JInt(3), STONE)) and bool(Tool.onType(JInt(1), STONE)) and bool(Tool.onType(JInt(1), ORE))
            and not bool(Tool.onType(JInt(1), LOG)) and bool(Tool.onType(JInt(2), GRASS)) and not bool(Tool.onType(JInt(2), STONE))
            and not bool(Tool.onType(JInt(4), GRASS)) and not bool(Tool.onType(JInt(3), None)),
            "X4: onType: hatchet = Woods only, pickaxe = rock + ore, shovel = Soils, hoe = none")
    skills()
    for i in range(6):
        Tool.N[i] = 0

    def hit(s_, b_, d=0.3):
        Tool.LAST.clear()
        return float(Tool.onDamage(U1, s_, b_, JFloat(d)))
    fh = py_power(3, 20, 2)
    r_log, r_stone = hit(stack("Tool_Hatchet_Iron", 20), LOG), hit(stack("Tool_Hatchet_Iron", 20), STONE)
    r_axe = hit(stack("Weapon_Axe_Iron"), LOG)
    r_bax = hit(stack("Weapon_Battleaxe_Iron"), LOG)
    K.check(abs(r_log - 0.3 * fh) < 1e-5 and abs(r_stone - 0.3) < 1e-7 and abs(r_axe - 0.3) < 1e-7 and abs(r_bax - 0.3) < 1e-7,
            "X4: Iron hatchet Lv 20 on a log x%.4f (%.5f); on stone vanilla (%.5f); a WEAPON axe / battleaxe on a log vanilla (%.5f / %.5f)" % (fh, r_log, r_stone, r_axe, r_bax))
    fp = py_power(1, 23, 2)
    K.check(abs(hit(stack("Tool_Pickaxe_Iron", 23), STONE) - 0.3 * fp) < 1e-5 and abs(hit(stack("Tool_Pickaxe_Iron", 23), ORE, 0.25) - 0.25 * fp) < 1e-5
            and abs(hit(stack("Tool_Pickaxe_Iron", 23), LOG) - 0.3) < 1e-7, "X4: Iron pickaxe Lv 23 x%.4f on stone + iron ore, vanilla on a log" % fp)
    K.check(abs(hit(stack("Tool_Shovel_Iron", 20), GRASS) - 0.3 * py_power(2, 20, 2)) < 1e-5 and abs(hit(stack("Tool_Hoe_Iron", 20), GRASS) - 0.3) < 1e-7,
            "X4: shovel on soil stronger, a hoe never (Fortune only)")
    skills(foraging=5)
    K.check(abs(hit(stack("Tool_Hatchet_Iron", 20), LOG) - 0.3) < 1e-7, "X4: an UNDER-LEVEL hatchet (Foraging 5 < Lv 20) breaks like the plain vanilla tool")
    n2 = int(Tool.N[2])
    old = hit(stack("Tool_Hatchet_Iron"), LOG)
    K.check(abs(old - 0.3 * py_power(3, 5, 2)) < 1e-5,
            "X4: an OLD hatchet without a stored level works at min(its band level, your skill 5) = Lv 5 (x%.4f): %.5f" % (py_power(3, 5, 2), old))
    skills(on=False)
    K.check(abs(hit(stack("Tool_Hatchet_Iron", 20), LOG) - 0.3 * fh) < 1e-5, "X4: without SkyySkills (no skill:fn:level) the tool works at its level")
    skills()
    K.check(abs(hit(None, LOG) - 0.3) < 1e-7 and abs(hit(IS.EMPTY if hasattr(IS, "EMPTY") else None, LOG) - 0.3) < 1e-7, "X4: an empty hand = vanilla")
    K.check(int(Tool.N[0]) >= 5 and int(Tool.N[1]) >= 5 and n2 >= 1, "X4: the counters moved (%s)" % Tool.counters())
    # the REAL GearToolHitSys.handle through a stand-in chunk
    FU = JClass(FAKE_PKG + ".FakeUtil")
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.universe.Universe"):
        FU.single(cn)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    prx = us.allocateInstance(PRc.class_)
    jf(PRc, "uuid").set(prx, U1)
    jf(PRc, "username").set(prx, "Tester")
    FCh = JClass(FAKE_PKG + ".FakeChunk")
    ch = us.allocateInstance(FCh.class_)
    ch.comps = JClass("java.util.IdentityHashMap")()
    ch.comps.put(PRc.getComponentType(), prx)
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    ctor = [c for c in DBE.class_.getConstructors() if len(c.getParameterTypes()) == 5][0]
    pts = [str(p.getName()) for p in ctor.getParameterTypes()]

    JFl = JClass("java.lang.Float")

    def ev(s_, b_, d):
        args, nf = [], 0
        for p in pts:
            if p.endswith("ItemStack"):
                args.append(s_)
            elif p.endswith("BlockType"):
                args.append(b_)
            elif p == "float":
                args.append(JFl.valueOf(JFloat(1.0 if nf == 0 else d)))   # (currentDamage = block health 1.0, damage of the hit)
                nf += 1
            else:
                args.append(JClass(p)(JInt(0), JInt(64), JInt(0)))
        return ctor.newInstance(JArray(JObject)(args))
    hs = Hit()
    e1 = ev(stack("Tool_Hatchet_Iron", 20), LOG, 0.3)
    d_before = float(e1.getDamage())
    Tool.LAST.clear()
    hs.handle(JInt(0), ch, None, None, e1)
    e2 = ev(stack("Tool_Hatchet_Iron", 20), LOG, 0.3)
    e2.setCancelled(True)
    hs.handle(JInt(0), ch, None, None, e2)
    ch2 = us.allocateInstance(FCh.class_)
    ch2.comps = JClass("java.util.IdentityHashMap")()
    e3 = ev(stack("Tool_Hatchet_Iron", 20), LOG, 0.3)
    hs.handle(JInt(0), ch2, None, None, e3)
    e4 = ev(stack("Weapon_Axe_Iron"), LOG, 0.3)
    hs.handle(JInt(0), ch, None, None, e4)
    K.check(abs(float(e1.getDamage()) - d_before * fh) < 1e-5 and abs(float(e2.getDamage()) - d_before) < 1e-7 and abs(float(e3.getDamage()) - d_before) < 1e-7
            and abs(float(e4.getDamage()) - d_before) < 1e-7 and hs.getQuery() is not None,
            "X4: the REAL GearToolHitSys.handle (ctor %s): hatchet hit %.5f -> %.5f; cancelled, no PlayerRef and a weapon axe untouched" % (pts, d_before, float(e1.getDamage())))

    # ============================================================================ X5 the bridge: skill:bonus:<uuid>["gear"]
    br.remove("skill:bonus:" + str(U1))
    skills()
    Tool.LAST.clear()
    Tool.held(U1, stack("Tool_Hatchet_Iron", 20))
    fo20 = py_fortune(3, 20, 2)
    g1 = gsrc()
    K.check(g1 is not None and set(g1) == {"dd.foraging"} and abs(g1["dd.foraging"] - fo20 / 100.0) < 1e-9 and isinstance(br.get("skill:bonus:" + str(U1)), CHM),
            "X5: no container yet (an older partner / no SkyyTrees) -> made; source gear = {dd.foraging: %s / 100}: %s" % (fo20, g1))
    br.get("skill:bonus:" + str(U1)).put("trees", JClass("java.util.Collections").singletonMap("dd.foraging", JDouble(0.2)))
    ps = JClass(PKG + "GearTool").N[3]
    pick = stack("Tool_Pickaxe_Iron", 23)
    Tool.held(U1, pick)
    g2 = gsrc()
    K.check(g2 is not None and set(g2) == {"dd.mining", "only.mining"} and abs(g2["dd.mining"] - py_fortune(1, 23, 2) / 100.0) < 1e-9
            and g2["only.mining"] == "Rock_,Rubble_,Ore_"
            and br.get("skill:bonus:" + str(U1)).get("trees") is not None, "X5: swap to a pickaxe -> dd.mining + only.mining rock / ore (fix B1); the trees source untouched: %s" % g2)
    n3 = int(Tool.N[3])
    Tool.held(U1, pick)
    K.check(int(Tool.N[3]) == n3, "X5: the same stack inside 1 s -> no recompute, no post")
    Tool.held(U1, stack("Tool_Shovel_Iron", 20))
    g2s = gsrc()
    K.check(g2s is not None and g2s.get("only.mining") == "Soil_" and abs(g2s["dd.mining"] - py_fortune(2, 20, 2) / 100.0) < 1e-9,
            "X5: a shovel -> dd.mining + only.mining Soil_ (its Fortune never counts on stone / ore; fix B1): %s" % g2s)
    Tool.held(U1, stack("Weapon_Axe_Iron"))
    K.check(gsrc() is None and br.get("skill:bonus:" + str(U1)).get("trees") is not None, "X5: a weapon axe in hand -> our source removed, the trees' stays")
    Tool.held(U1, stack("Tool_Sickle_Iron", 20))
    K.check(gsrc() == {"dd.farming": py_fortune(5, 20, 2) / 100.0}, "X5: a sickle -> dd.farming (Fortune only, no filter): %s" % gsrc())
    skills(farming=3)
    Tool.held(U1, stack("Tool_Sickle_Iron", 20))
    K.check(gsrc() is None, "X5: an under-level sickle -> no Fortune on the bridge")
    skills()
    br.put("profile:busy:" + str(U1), JBoolean(True))
    Tool.held(U1, stack("Tool_Sickle_Iron", 20))
    K.check(gsrc() is None, "X5: profile:busy -> our source removed (PROFILES-CONTRACT)")
    br.remove("profile:busy:" + str(U1))
    Tool.LAST.clear()
    Tool.held(U1, stack("Tool_Sickle_Iron", 20))
    K.check(gsrc() is not None, "X5: busy cleared -> posted again")
    Tool.forget(U1)
    K.check(gsrc() is None and Tool.LAST.get(U1) is None, "X5: forget (logout) removes the source + the cache")
    # fix round 2 (engine critic LOW 1): a world-thread tick AFTER the disconnect must not post the source back
    Tool.LAST.clear()
    late = Tool.held(U1, stack("Tool_Hatchet_Iron", 20))
    K.check(late is None and gsrc() is None and Tool.LAST.get(U1) is None and Tool.GONE.containsKey(U1),
            "X5: a hand tick after forget (disconnect race) posts nothing and caches nothing")
    Tool.back(U1)
    Tool.held(U1, stack("Tool_Hatchet_Iron", 20))
    K.check(gsrc() is not None and not Tool.GONE.containsKey(U1), "X5: back (PlayerReadyEvent) -> the held tool posts again")
    Tool.forget(U1)
    Tool.clearAll()
    K.check(gsrc() is None and Tool.LAST.isEmpty() and Tool.GONE.isEmpty(), "X5: clearAll (shutdown) removes every source + the gone list")
    # ============================================================================ X6 texts
    K.check("tool stats on" in str(Tool.statusText()) and "skill:bonus" in str(Tool.statusText()) and "tool hits stronger" in str(Tool.counters()),
            "X6: status + counters: %s / %s" % (Tool.statusText(), Tool.counters()))
    Cfg.PART_TOOLS = False
    K.check("OFF" in str(Tool.statusText()), "X6: status says OFF when part.tools is off")
    Cfg.PART_TOOLS = True
    K.save()


# ====================================================================================================== C: class compare
def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(OLD_JAR), pool_of(JAR)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                lines_.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    added = sorted(c[len(PKG):] for c in set(nb) - set(na))
    removed = sorted(set(na) - set(nb))
    K.check(added == NEW_CLASSES and not removed, "C: classes added %s, removed %s" % (added, removed))
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    unexpected = sorted(set(diffs) - EXPECT_CHANGED)
    print("C. class compare 0.2.11 -> 0.2.12:")
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:300]))
    K.check(not unexpected, "C: only the planned classes differ (unexpected: %s)" % {k: diffs[k] for k in unexpected})
    gv = diffs.get("GearView", [])
    K.check(sorted(gv) == ["~m gateLine", "~m lines"], "C: GearView: only gateLine + lines changed: %s" % gv)
    K.check(diffs.get("GearHandSys") == ["~m tick"] and diffs.get("GearBye") == ["~m accept"]
            and diffs.get("GearReady") == ["~m accept"], "C: GearHandSys.tick + GearBye.accept + GearReady.accept only")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    K.check(ed == ["manifest.json"], "C: non-class entries changed = only manifest.json: %s" % ed)
    K.save(diffs=diffs)


# ====================================================================================================== D: start twice on a live copy
def run_live(out, home):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    before = open(os.path.join(home, "config.properties"), "rb").read()
    files0 = sorted(os.path.relpath(os.path.join(r, f), home) for r, d, fs in os.walk(home) for f in fs)
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025"):
            getattr(Cfg, m)()
        Cfg.load()
        after = open(os.path.join(home, "config.properties"), "rb").read()
        K.check(after == before, "D start %d: the live config.properties copy is byte-identical (the tool keys need no one-time update)" % step)
        K.check(bool(Cfg.PART_TOOLS) and str(Cfg.TOOL_PICK) == PICK_DEF and str(Cfg.TOOL_HATCH) == HATCH_DEF and float(Cfg.TOOL_FCAP) == 25.0,
                "D start %d: the tool rows read their defaults from a file without them" % step)
    files1 = sorted(os.path.relpath(os.path.join(r, f), home) for r, d, fs in os.walk(home) for f in fs)
    K.check(files0 == files1, "D: no file added or removed by two starts (%d files)" % len(files0))
    txt = before.decode("utf-8", "replace")
    K.check("part.tools" not in txt and "tool.power" not in txt and "tool.fortune" not in txt, "D: the live file has no tool line (nothing to migrate)")
    K.save()


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD_JAR], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H["run_mkfake"](arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--engine", lambda: run_engine(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--live", lambda: run_live(arg("--out"), arg("--live"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    assert os.path.isfile(JAR), JAR
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside tools/dev/scratch/tools01fix2"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    if not os.path.isfile(OLD_JAR):
        live_jar = os.path.join(B.USERDATA, "Mods", "SkyyGear.jar")
        with zipfile.ZipFile(live_jar) as z_:
            assert '"Version": "0.2.11"' in z_.read("manifest.json").decode("utf-8"), "the installed SkyyGear.jar is not 0.2.11"
        shutil.copyfile(live_jar, OLD_JAR)
        print("C. the installed SkyyGear 0.2.11 jar copied to scratch (read-only source %s)" % live_jar)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("engine", "--engine"), ("compare", "--compare")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        home = os.path.join(SCRATCH, "live")
        shutil.copytree(LIVE_DIR, home)
        print("D. live Skyy_SkyyGear copied (read-only source %s)" % LIVE_DIR)
        out = os.path.join(SCRATCH, "live.json")
        pr = child(env, "--live", home, "--out", out)
        check(pr.returncode == 0, "D: the child exited cleanly")
        take(out, "live")
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
