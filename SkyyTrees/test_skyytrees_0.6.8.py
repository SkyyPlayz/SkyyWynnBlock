"""Harness for SkyyTrees 0.6.8 (the sickle right swing's HitEntity Replace gets DefaultOk true - no more SEVERE "Missing replacement
interactions for interaction: Skyy_Tree_HarvR_HE"; tools/trees_0_6_8_patch.py).
Build first:
    python tools/trees_0_6_8_patch.py && python SkyyTrees/build_skyytrees_0.6.8.py
    python SkyyTrees/test_skyytrees_0.6.8.py [--keep] [--expect-dump] [--base <folder holding the older jars>]
--base: as the 0.6.7 harness (the checkout whose SkyyTrees / SkyyClasses / SkyyPets folders hold the built 0.6.4 / 0.6.6 Trees, Classes 0.1.50,
        Pets 0.4.20 jars; default = this checkout, then the main checkout above .claude/worktrees).
Phases (each its own child JVM, -Xverify:all where classes run; the kit's verify / class compare 0.6.7 -> 0.6.8 / engine-access audit around them):
  static   the generated script = the patch's output (re-run to identical bytes), 0.6.7's patch still regenerates 0.6.7 byte for byte, header /
           version, no new class / system / command / method, line endings kept; the jar vs 0.6.7: the same entries, changed non-class =
           manifest + Skyy_Tree_HarvR_HE.json only, and in that file ONLY "DefaultOk": true was added (DefaultValue / Var / Type kept);
           Skyy_Tree_HarvL_HE unchanged (vanilla Left already had it); both selector overrides byte-equal; vanilla Sickle_Swing_Right_Selector
           still lacks DefaultOk (why the fix is needed) and no vanilla sickle defines the var it names
  harv     EXECUTED in the JVM: the engine's ReplaceInteraction codec decodes Skyy_Tree_HarvR_HE (without its byte-equal DefaultValue, which
           decodes only inside a live AssetStore) of 0.6.8 -> defaultOk true, of 0.6.7 ->
           false (the SEVERE case: ReplaceInteraction.doReplace logs "Missing replacement ..." only when the var is missing AND defaultOk is
           false - bytecode read below), HarvL_HE -> true; the same default interaction + var both times; doReplace's bytecode still guards
           the log line with defaultOk
  effects / old66 / text / bridge / creative / g64 / data / sow / jar65 / path / mig / integ / farm / sap / live   the 0.6.7 harness's phases
           on the 0.6.8 jar (unchanged behaviour; live = start twice on a scratch COPY of the live Skyy_SkyyTrees folder)
Not executed here (UNVERIFIED until the game): a real right-swing hit on a mob with a sickle (the client + the interaction chain); the log
line gone in a live session.
"""
import os, sys, json, subprocess, importlib.util, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.6.8"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "fix1", "trees")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)]
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyytrees_0_6_7", os.path.join(HERE, "test_skyytrees_0.6.7.py"))
T67 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T67)
sys.argv[:] = _argv
T66, T65, T64, T63, T60 = T67.T66, T67.T65, T67.T64, T67.T63, T67.T60
T60.VERSION = VERSION

PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.6.7.jar") if os.path.isfile(os.path.join(HERE, "SkyyTrees-0.6.7.jar")) else os.path.join(T67.BASE, "SkyyTrees", "SkyyTrees-0.6.7.jar")
GEN = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyytrees_0.6.7.py")
PATCH = os.path.join(TOOLS, "trees_0_6_8_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
AZP = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")          # read-only
HE_R = "Server/Item/Interactions/SkyyTrees/Skyy_Tree_HarvR_HE.json"
HE_L = "Server/Item/Interactions/SkyyTrees/Skyy_Tree_HarvL_HE.json"
SEL = ["Server/Item/Interactions/Weapons/Sickle/Attacks/Swing_%s/Sickle_Swing_%s_Selector.json" % (s, s) for s in ("Left", "Right")]
EXPECT = {   # the version strings only (0.6.7 -> 0.6.8; no Java change)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'SkyyTreesPlugin': ['~m setup'],
    'TreeCfg': ['~m load'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyTrees 0.6.8 - build script') and g.count('VERSION = "0.6.8"') == 1 and 'VERSION = "0.6.7"' not in g, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass(") and g.count("\nM(") == o.count("\nM("), "S no new command / system / class / method")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "trees_0_6_7_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb, vz = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar), zipfile.ZipFile(AZP)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq(sorted(nb - na) + sorted(na - nb), [], "S the same jar entries as 0.6.7")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, sorted(["manifest.json", HE_R]), "S changed non-class entries = manifest + Skyy_Tree_HarvR_HE.json")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace("0.6.7", VERSION)) == mb, "S manifest: only the Version changed")
    ro, rn = json.loads(za.read(HE_R).decode("utf-8")), json.loads(zb.read(HE_R).decode("utf-8"))
    K.check("DefaultOk" not in ro and rn.get("DefaultOk") is True and dict((k, v) for k, v in rn.items() if k != "DefaultOk") == ro,
            "S Skyy_Tree_HarvR_HE: ONLY \"DefaultOk\": true added (was %s, now %s)" % (ro, rn))
    K.check(list(rn)[:2] == ["Type", "DefaultOk"], "S DefaultOk sits after Type (the Left file's order)")
    lo = json.loads(zb.read(HE_L).decode("utf-8"))
    K.check(za.read(HE_L) == zb.read(HE_L) and lo.get("DefaultOk") is True and lo.get("Type") == "Replace", "S Skyy_Tree_HarvL_HE unchanged and already DefaultOk")
    K.check(all(za.read(s) == zb.read(s) for s in SEL), "S both sickle selector overrides byte-equal to 0.6.7")
    K.check(json.loads(zb.read(SEL[1]).decode("utf-8"))["HitEntity"]["Interactions"] == ["Skyy_Tree_HarvR_HE"], "S the Right selector override still names Skyy_Tree_HarvR_HE")
    vr = json.loads(vz.read(SEL[1]).decode("utf-8-sig"))["HitEntity"]["Interactions"][0]
    vl = json.loads(vz.read(SEL[0]).decode("utf-8-sig"))["HitEntity"]["Interactions"][0]
    K.check("DefaultOk" not in vr and vl.get("DefaultOk") is True, "S vanilla: Right selector's Replace lacks DefaultOk, Left has it (the cause)")
    K.check(dict((k, v) for k, v in rn.items() if k != "DefaultOk") == vr, "S our HarvR_HE = vanilla's Right Replace + DefaultOk")
    var = vr["Var"]
    defs = []
    for n in vz.namelist():
        if n.startswith("Server/Item/Items/") and "/Tool_Sickle_" in n and n.endswith(".json"):
            iv = json.loads(vz.read(n).decode("utf-8-sig")).get("InteractionVars") or {}
            if var in iv:
                defs.append(n)
    K.eq(defs, [], "S no vanilla sickle defines the var %r (so the missing-var path runs on every right-swing mob hit)" % var)
    K.save()


def run_harv(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    RI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.ReplaceInteraction")
    RJR, EI = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("com.hypixel.hytale.codec.ExtraInfo")

    def fld(o, n):
        f = RI.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f.get(o)

    def dec(text):
        # DefaultValue (an inline RootInteraction) decodes only inside a live AssetStore; it is byte-equal to 0.6.7 (static phase), so the
        # codec reads everything else: Type / DefaultOk / Var (a misspelt or mistyped DefaultOk would be an unknown key or a codec error)
        d = json.loads(text)
        d.pop("DefaultValue", None)
        ei = EI()
        o = RI.CODEC.decodeJson(RJR.fromJsonString(json.dumps(d)), ei)
        uk = [str(x) for x in ei.getUnknownKeys()]
        return o, uk
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    rn, ukn = dec(zn.read(HE_R).decode("utf-8"))
    ro, uko = dec(zo.read(HE_R).decode("utf-8"))
    ln, ukl = dec(zn.read(HE_L).decode("utf-8"))
    K.check(rn is not None and bool(fld(rn, "defaultOk")), "H 0.6.8 Skyy_Tree_HarvR_HE decodes (engine ReplaceInteraction codec) with defaultOk = true")
    K.check(ro is not None and not bool(fld(ro, "defaultOk")), "H 0.6.7 Skyy_Tree_HarvR_HE decoded with defaultOk = false (the SEVERE case)")
    K.check(ln is not None and bool(fld(ln, "defaultOk")), "H Skyy_Tree_HarvL_HE decodes with defaultOk = true (as vanilla Left)")
    K.eq((str(fld(rn, "variable")) if _has(RI, "variable") else str(rn)), (str(fld(ro, "variable")) if _has(RI, "variable") else str(ro).replace("defaultOk=false", "defaultOk=true")),
         "H the same var as 0.6.7")
    K.check(str(rn).replace("defaultOk=true", "defaultOk=false") == str(ro) if "defaultOk=" in str(rn) else True,
            "H the decoded 0.6.8 object = 0.6.7's but for defaultOk: %s" % str(rn)[:300])
    K.check(set(ukn) <= {"Type"} and set(uko) <= {"Type"} and set(ukl) <= {"Type"}, "H no unknown key but the type tag (%s / %s / %s)" % (ukn, uko, ukl))
    # the engine's rule (why defaultOk silences it): doReplace logs "Missing replacement" only behind the defaultOk check
    import skyybuild as SB
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(SB.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    cc = pool.get(RI.class_.getName())
    m = [x for x in cc.getDeclaredMethods() if str(x.getName()) == "doReplace"]
    K.check(len(m) == 1, "H ReplaceInteraction.doReplace exists")
    if m:
        bos = BOS()
        IP(PS(bos)).print_(m[0])
        ls = str(bos.toString()).splitlines()
        i_ok = [i for i, l in enumerate(ls) if "defaultOk" in l and "getfield" in l]
        i_log = [i for i, l in enumerate(ls) if "Missing replacement interactions" in l]
        K.check(i_ok and i_log and i_ok[0] < i_log[0] and "ifne" in ls[i_ok[0] + 1], "H doReplace: getfield defaultOk + ifne (skip) comes before the Missing-replacement log line")
        K.check(any("getRootInteractionOrUnknown" in l for l in ls[i_log[0]:]), "H after the log line it still runs the default (getRootInteractionOrUnknown + execute)")
    K.notes.append("H decoded 0.6.8: %s" % str(rn)[:240])
    K.save()
    sys.stdout.flush()
    os._exit(0)


def _has(RI, n):
    try:
        RI.class_.getDeclaredField(n)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    for _p in (OLD_JAR, T67.OLD_JAR, T67.CJAR, T67.PJAR, T65.OLD_JAR):
        assert os.path.isfile(_p), "missing %s (pass --base <the checkout with the built jars>)" % _p
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("harv", run_harv), ("effects", T67.run_effects), ("old66", T67.run_old66), ("text", T67.run_text),
                   ("bridge", T67.run_bridge), ("creative", T66.run_creative), ("g64", T65.run_g64), ("data", T65.run_data), ("sow", T65.run_sow),
                   ("jar65", T65.run_jar), ("path", T64.run_path), ("mig", T64.run_mig), ("integ", T64.run_integ),
                   ("farm", T63.run_farm), ("sap", T63.run_sap), ("live", T63.run_live)],
           script=__file__, live=(T60.LIVE_DIR, "Skyy_SkyyTrees"))
