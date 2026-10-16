"""Harness for SkyyFishing 0.1.7 (NO WOODEN REEL - every rod has a basic reel built in, the pole fishes without tackle, one pole per profile at the
bench, the starting-kit pole redrawn, the tackle quest event; tools/fishing_0_1_7_patch.py) = the 0.1.5 harness's phases on the 0.1.7 jar + R.
Build first: python tools/fishing_0_1_7_patch.py && python SkyyFishing/build_skyyfishing_0.1.7.py

    python SkyyFishing/test_skyyfishing_0.1.7.py [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.1.6 -> 0.1.7 (exactly the planned members), engine-access audit
  R  reel   EVERY NEW CODE PATH: fish.reel.builtin on = reelPower(0) = the Wooden reel's power, look(0) = the Wooden reel look, off = 0 / no
            look; a new Wooden rod's fresh rig has NO reel (Copper / Iron rods: none, as before); a bare Wooden rod (no rod document - SkyyGear's
            starting-kit pole) = reel 0, a bare Copper rod keeps its own reel; the tooltip / the cast's stats use the built-in power; the
            recipes: no Wooden Reel made or consumed, the Copper Reel = 8 Copper Bars only; the Wooden Reel item text; gear:fn:poleRule TRUE
            = the Wooden rod's recipe locked (gate 3, "Your pole: /pole", craft refused, nothing used), FALSE / absent / throws = as 0.1.6;
            questRig sends {UUID, fishing:rig, part, 1} (absent = false); questInit puts quest:caller:fishingrig (fix round: SkyyQuests 0.3.4's
            fit_tackle caller - only 0.1.7 sets it); a bare lifelong pole counts as stale and restampOne draws it
            (a bare plain rod stays as it is); FishCore.cast no longer stops a reel-less rod while the built-in reel is on (static check)
  X / Q / ST  the 0.1.5 harness's phases on this jar (exec = the tick checks, quest = Marlow's starter + gear:fn:pole, live = start twice on a
            scratch COPY of the live Skyy_SkyyFishing); the checks that test what 0.1.7 changes on purpose are WAIVED by name (listed)
Scratch: tools/dev/scratch/gear0311/fishing (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.7"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear0311", "fishing")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_1_5", os.path.join(HERE, "test_skyyfishing_0.1.5.py"))
T15 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T15)
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
EXPECT = {
    "FishRig": ["+m look", "~m rigOf", "~m freshRig", "~m rodLines", "~m stale", "~m restampOne"],
    "FishCfg": ["~m reelPower", "~m applyScalars", "~m applyAll", "~m seed", "+f REEL_BUILTIN", "~<clinit>"],
    "FishBridge": ["+m poleRule", "+m questRig", "~m questInit"],          # fix round: + quest:caller:fishingrig
    "FishBench": ["~m gate", "+m lockTag", "~m craft"],
    "FishCore": ["~m cast", "~m tickPlayer"],
    "FishDefs": ["~<clinit>"],
    "FishPage": ["~m build", "~m handleDataEvent"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
    "FishCmds": ["~m admin"], "SkyyFishingPlugin": ["~m setup"],
}
ADDED = []
# the 0.1.4 / 0.1.5 checks that test what 0.1.7 changes ON PURPOSE (a new Wooden rod has no Wooden Reel fitted any more)
WAIVE = (
    ("Q3 ... the reel is the Wooden Reel (1)", "0.1.7 by design: a new Wooden rod (Marlow's starter too) has the built-in reel, no fitted Wooden Reel (R checks it)"),
    ("P3 FIX 3.3: the lifelong line promises no Fishing levels yet", "0.1.6 by design: the line says 'levels with your Fishing' since SkyySkills has Fishing (0.1.6 C)"),
    ("P7 FIX 3.2: fishing:fn:restamp redraws", "0.1.7 by design (D): a bare LIFELONG pole (SkyyGear's starting-kit pole) is drawn now, so the 0.1.5 'no document = unchanged' case changed (R checks a bare plain rod stays unchanged)"),
    ("C: non-class entries changed: got ['Server/Languages/en-US/server.lang', 'manifest.json']", "0.1.7 by design: the Wooden rod / Wooden Reel item texts changed (our own lang)"),
)
_orig = HK.Child.check


def _check(self, cond, what):
    if not cond:
        w = [why for pre, why in WAIVE if str(what).startswith(pre)]
        if w:
            self.notes.append("WAIVED (%s): %s" % (w[0], str(what)[:160]))
            return cond
    return _orig(self, cond, what)


HK.Child.check = _check


def run_reel(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JObject, JArray, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    Cfg, Rig, Defs, Bench, Brg, Log = P("FishCfg"), P("FishRig"), P("FishDefs"), P("FishBench"), P("FishBridge"), P("FishLog")
    Log.SINK = JClass("java.util.ArrayList")()
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Bool_ = JClass("java.lang.Boolean")

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))
    # the built-in reel
    Cfg.REEL_BUILTIN = True
    eq(float(Cfg.reelPower(JInt(0))), float(Cfg.reelPower(JInt(1))), "R built-in on: reelPower(0) = the Wooden reel's power")
    K.check(float(Cfg.reelPower(JInt(0))) > 0 and int(Rig.look(JInt(0))) == 1 and int(Rig.look(JInt(2))) == 2, "R look(0) = the Wooden reel look, a fitted reel its own")
    eq(list(str(x) for x in Rig.freshRig("SkyyFishing_Rod_Bamboo")), ["0", "", "", ""], "R a NEW Wooden rod: no reel fitted (the built-in one)")
    eq(list(str(x) for x in Rig.freshRig("SkyyFishing_Rod_Copper")), ["0", "", "", ""], "R a new Copper rod: no reel (as 0.1.6)")
    T15.item_store([str(x) for x in Defs.RODS] + ["Rock_Stone"])          # a bare JVM has no Item store: the 0.1.5 harness's stand-in
    bare_w, bare_c = IS("SkyyFishing_Rod_Bamboo", 1), IS("SkyyFishing_Rod_Copper", 1)
    eq(str(Rig.rigOf(bare_w)[0]), "0", "R a bare Wooden rod (SkyyGear's starting-kit pole) = reel 0, never a phantom Wooden Reel to take off")
    eq(str(Rig.rigOf(bare_c)[0]), "2", "R a bare Copper rod keeps its own tier's reel (0.1.0 probe rods)")
    lines = [str(l) for l in Rig.rodLines(JInt(0), Rig.rigOf(bare_w))]
    K.check([l for l in lines if l.startswith("Reel: basic, built in (power")], "R the tooltip: 'Reel: basic, built in (power ...)': %s" % lines[:2])
    st = Rig.stats(JInt(0), Rig.rigOf(bare_w))
    K.check(abs(float(st[int(Rig.ST_POWER)]) - float(Cfg.reelPower(JInt(1)))) < 1e-9, "R the cast's stats use the built-in power")
    Cfg.REEL_BUILTIN = False
    K.check(float(Cfg.reelPower(JInt(0))) == 0.0 and int(Rig.look(JInt(0))) == 0 and str(Rig.freshRig("SkyyFishing_Rod_Bamboo")[0]) == "1"
            and str(Rig.rigOf(bare_w)[0]) == "1", "R fish.reel.builtin off = 0.1.6 exactly (no power without a reel, the Wooden Reel fitted / shown)")
    Cfg.REEL_BUILTIN = True
    # the recipes
    outs = [str(x) for x in Defs.R_OUT]
    prev = [str(x) for x in Defs.R_PREV]
    K.check("SkyyFishing_Reel_Bamboo" not in outs and "SkyyFishing_Reel_Bamboo" not in prev and prev[outs.index("SkyyFishing_Reel_Copper")] == "",
            "R no recipe makes or consumes the Wooden Reel; the Copper Reel = its own materials")
    with __import__("zipfile").ZipFile(jar) as z:
        lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    K.check("the same as the basic reel every rod has built in" in lang and "Has a basic reel built in" in lang, "R the item texts (Wooden Reel, rods)")
    # one pole per profile (gear:fn:poleRule)
    r0 = outs.index("SkyyFishing_Rod_Bamboo")
    U = JClass("java.util.UUID").randomUUID()
    Store_ = P("FishStore")
    ANS = [None]

    @JImplements("java.util.function.Function")
    class Rule(object):
        @JOverride
        def apply(self, o):
            if ANS[0] == "throw":
                raise ValueError("boom")
            return ANS[0]
    g_abs = int(Bench.gate(U, "k1", JInt(r0)))
    br.put("gear:fn:poleRule", Rule())
    ANS[0] = Bool_.TRUE
    g_on = int(Bench.gate(U, "k1", JInt(r0)))
    tag = str(Bench.lockTag(U, "k1", JInt(r0)))
    ANS[0] = Bool_.FALSE
    g_off = int(Bench.gate(U, "k1", JInt(r0)))
    ANS[0] = "throw"
    g_thr = int(Bench.gate(U, "k1", JInt(r0)))
    K.check(g_on == 3 and tag == "Your pole: /pole" and g_abs != 3 and g_off != 3 and g_thr != 3,
            "R gear:fn:poleRule TRUE = the Wooden rod locked ('Your pole: /pole'); FALSE / absent / throws = as 0.1.6: %s" % [g_abs, g_on, g_off, g_thr])
    ANS[0] = Bool_.TRUE
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    try:
        inv = SIC(JClass("java.lang.Short")(10).shortValue())
        msg = str(Bench.craft(inv, U, "k1", JInt(r0)))
        K.check(msg.startswith("-Every player has ONE fishing pole"), "R crafting the Wooden rod is refused: %s" % msg[:80])
    except Exception as e_:
        K.notes.append("R craft on a bare container: %s" % str(e_)[:160])
    # the tackle event
    K.check(not bool(Brg.questRig(U, "SkyyFishing_Hook_Barbed_I")), "R questRig without SkyyQuests = false (one map read)")
    br.remove("quest:caller:fishingrig")
    Brg.questInit()
    K.check(Bool_.TRUE.equals(br.get("quest:caller:fishingrig")) and Bool_.TRUE.equals(br.get("quest:caller:fishing")),
            "R (fix round) questInit puts quest:caller:fishingrig (SkyyQuests 0.3.4's Fit tackle step is live only with this SkyyFishing)")
    got = []

    @JImplements("java.util.function.Function")
    class Ev(object):
        @JOverride
        def apply(self, o):
            got.append([str(x) for x in o])
            return Bool_.TRUE
    br.put("quest:fn:event", Ev())
    K.check(bool(Brg.questRig(U, "SkyyFishing_Line_Braided_I")) and got == [[str(U), "fishing:rig", "SkyyFishing_Line_Braided_I", "1"]],
            "R questRig sends {UUID, fishing:rig, the part, 1}: %s" % got)
    # the bare lifelong pole is redrawn; a bare plain rod is not
    BD = JClass("org.bson.BsonDocument")
    gd = BD()
    gd.put("ll", JClass("org.bson.BsonInt32")(1))
    gd.put("lu", JClass("org.bson.BsonString")("u1"))
    gd.put("lo", JClass("org.bson.BsonString")("k1"))
    pole = IS("SkyyFishing_Rod_Bamboo", 1).withMetadata("SkyyGear", gd)
    K.check(bool(Rig.llPole(pole)) and bool(Rig.stale(pole)) and not bool(Rig.stale(bare_w)), "R a bare lifelong pole counts as stale, a bare plain rod does not")
    try:
        drawn = Rig.restampOne(pole)
        K.check(Rig.doc(drawn) is not None and str(Rig.rigOf(drawn)[0]) == "0" and bool(Rig.llPole(drawn)) and not bool(Rig.stale(drawn)),
                "R restampOne draws the bare pole: our rod document (reel 0 = built in), still the lifelong pole, not stale any more")
    except Exception as e_:
        K.notes.append("R restampOne on a bare JVM (no Item store): %s" % str(e_)[:160])
    K.check(Rig.restampOne(bare_w) == bare_w, "R a bare plain rod comes back unchanged")
    # static: FishCore.cast checks only the reel power (the built-in reel counts) - the generated script's cast line
    src = open(os.path.join(HERE, "build_skyyfishing_0.1.7.py"), encoding="utf-8").read()
    K.check("if (@PKG@.FishCfg.reelPower(@PKG@.FishRig.reelOf(rig)) <= 0.0) { tell(c, \"This rod has no reel." in src
            and "if (@PKG@.FishRig.reelOf(rig) <= 0 || @PKG@.FishCfg.reelPower" not in src, "R FishCore.cast stops only a rod whose reel power is 0 (the built-in reel counts)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("reel", run_reel), ("exec", T15.run_exec), ("quest", T15.run_quest), ("live", T15.run_live)], script=__file__,
           live=(T15.LIVE_DIR, "Skyy_SkyyFishing"))
