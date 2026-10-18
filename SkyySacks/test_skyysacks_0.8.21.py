"""Harness for SkyySacks 0.8.21 (SMELTING FORTUNE in the /craft Furnace; tools/sacks_0_8_21_patch.py).
Build first:
    python tools/sacks_0_8_21_patch.py && python SkyySacks/build_skyysacks_0.8.21.py

    python SkyySacks/test_skyysacks_0.8.21.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.20 -> 0.8.21: exactly the planned members (EXPECT); non-class entries: manifest.json only
  ALLOY the 0.8.20 phase unchanged (alloys, Furnace Charm, Eternal Flame, Charcoal ledger) on the REAL asset stores + the fake alloy pack,
        then NEW in the same JVM - FORTUNE:
          sfKind (vanilla ore -> bar = 1, SkyyAlloy bars = 2, alloys switch, never Tannery / Salvagebench / charcoal / non-bar / switch off);
          oreOfBar (Iron -> Ore_Iron, Bronze none); sfValue (tree:fn:bonus {UUID, Smithing.SSmelt}; absent / not a Number / NaN / an
          exception / inactive profile = 0); sfBudget + sfGrant (skill:fn:oreBudget {UUID, ore, Integer n}: clamps, MISSING = 0 = no
          Fortune, minedOnly off = all, alloys ask each parent's ore in turn); sfExtras (floor + chance, guard); the bench: Fortune units
          roll once each (F 1.0 = exactly double, fu < count, F 0.5 statistics - extras = the ledger exactly), cancel returns inputs only,
          the no-output fallback / Tannery / a non-bar output / switch off make no extras, Eternal Flame keeps fuel + Fortune works, merge
          rules, fu clamps, save / load (q.<i>.sf / fu, hand edits clamped, none written without Fortune), describe text, drainSf log
          lines; config sfKeys + the tree:reads:SkyySacks flag (on = listed, off / shutdown = removed)
  SUP / TG / KEYS / D (live)   the 0.8.18 harness's phases on this jar - unchanged behaviour
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_20", os.path.join(HERE, "test_skyysacks_0.8.20.py"))
T20 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T20)
sys.argv = _argv
HK.run_compare = _orig_compare
T18 = T20.T18

VERSION = "0.8.21"
OLD_VERSION = "0.8.20"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fort-f3", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {
    "ProcBench": ["+f sfDone", "+f ORE_OF", "+f ORE_N", "+m oreQtyOfBar", "+m sfGive", "+m sfOres", "+m sfRefund", "~m cancel", "+m sfKind", "+m oreOfBar", "+m sfValue", "+m sfBudget", "+m sfGrant", "+m sfExtras",
                  "+m addJobF", "~m addJob", "~m finishUnit", "+m sfTake", "~m describe", "~m toProps", "~m fromProps", "~c ", "~<clinit>"],
    "ProcJob": ["+f sf", "+f fu", "+f fb"],
    "ProcTask": ["+m drainSf", "~m run"],
    "CraftPage": ["~m procQueue"],
    "SackCfg": ["+f SF_ON", "+f SF_ALLOYS", "+f SF_MINED", "+f SF_GUARD", "+f SF_READS", "+f SF_NODE", "+f READS_PUT", "+m readsValue", "+m sfPub", "+m sfUnpub",
                "+m sfKeys", "+m sfChanged", "~m reload", "~<clinit>"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the version text + the four Server Setup rows
    "CfgFile": ["~<clinit>"],   # the default config.properties text (+ the six Smelting Fortune template lines)
    # tools/tier_tags.py read at build time (the sort table): SkyyGear 0.3.21's mining armor ids (another builder's table rows)
    "RecipeCmp": ["~<clinit>"],
    "SkyySacksPlugin": ["~m setup", "~m shutdown"],   # the ready line, the reads flag removed
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
UUID0 = T20.UUID0


def fortune_cases(K, L):
    from jpype import JClass, JString, JImplements, JOverride, JDouble, JInt
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    PB = JClass(PKG + "ProcBench")
    PT = JClass(PKG + "ProcTask")
    CFG = JClass(PKG + "SackCfg")
    CL = JClass(PKG + "CraftLog")
    UUID = JClass("java.util.UUID")
    Props = JClass("java.util.Properties")
    Sys = JClass("java.lang.System")
    br = Sys.getProperties().get("skyy.bridge")
    u = UUID.fromString(UUID0)
    k = str(u)
    for kk in ("acc:smelt:" + k, "profile:fn:key", "tree:fn:bonus", "skill:fn:oreBudget"):
        br.remove(kk)

    def bench_ids(r):
        return [str(b.id) for b in (r.getBenchRequirement() or []) if b is not None and b.id is not None]

    def find(out_id, bench):
        for e in CRR.getAssetMap().getAssetMap().entrySet():
            r = e.getValue()
            po = r.getPrimaryOutput()
            if po is not None and str(po.getItemId()) == out_id and bench in bench_ids(r):
                return r
        return None
    riron = find("Ingredient_Bar_Iron", "Furnace")
    if riron is None:
        dbg = []
        for e in CRR.getAssetMap().getAssetMap().entrySet():
            if "Bar_Iron" in str(e.getKey()):
                r = e.getValue()
                po = r.getPrimaryOutput()
                dbg.append((str(e.getKey()), po and str(po.getItemId()), [str(o.getItemId()) for o in (r.getOutputs() or [])], bench_ids(r),
                            [(str(b.type), str(b.id)) for b in (r.getBenchRequirement() or [])]))
        print("DEBUG iron recipes:", dbg[:6], "total", CRR.getAssetMap().getAssetMap().size())
    K.check(riron is not None, "FORTUNE: the vanilla Iron Ingot Furnace recipe is in the store")
    if riron is None:
        return
    RID = str(riron.getId())
    K.eq([str(m.getItemId()) for m in riron.getInput()], ["Ore_Iron"], "FORTUNE: vanilla Iron Ingot = 1 Ore_Iron (%s)" % RID)
    rb = CRR.getAssetMap().getAsset(JString("Alloy_Bronze"))
    rch = None
    rsal = None
    rnb = None
    for e in CRR.getAssetMap().getAssetMap().entrySet():
        r = e.getValue()
        po = r.getPrimaryOutput()
        oid = str(po.getItemId()) if po is not None and po.getItemId() is not None else ""
        bs = bench_ids(r)
        if rch is None and "Furnace" in bs and not oid.startswith("Ingredient_Bar_"):
            rch = r
        if rsal is None and "Salvagebench" in bs and any(str(o.getItemId()).startswith("Ingredient_Bar_") for o in (r.getOutputs() or []) if o is not None and o.getItemId() is not None):
            rsal = r
        if rnb is None and "Workbench" in bs:
            rnb = r

    # ---- 1. which smelts
    kinds = [int(PB.sfKind(riron, JString("Furnace"))), int(PB.sfKind(rb, JString("Furnace"))), int(PB.sfKind(riron, JString("Tannery"))),
             int(PB.sfKind(None, JString("Furnace")))]
    K.eq(kinds, [1, 2, 0, 0], "FORTUNE sfKind: ore row 1, alloy row 2, Tannery 0, null 0")
    K.check(rch is None or int(PB.sfKind(rch, JString("Furnace"))) == 0, "FORTUNE sfKind: a Furnace recipe that makes no bar (%s) = 0" % (rch and rch.getId()))
    K.check(rsal is None or int(PB.sfKind(rsal, JString("Salvagebench"))) == 0, "FORTUNE sfKind: Salvagebench bars (%s) = 0" % (rsal and rsal.getId()))
    K.check(rnb is None or int(PB.sfKind(rnb, JString("Furnace"))) == 0, "FORTUNE sfKind: a Workbench recipe passed as Furnace = 0 (%s)" % (rnb and rnb.getId()))
    CFG.SF_ALLOYS = False
    K.check(int(PB.sfKind(rb, JString("Furnace"))) == 0 and int(PB.sfKind(riron, JString("Furnace"))) == 1, "FORTUNE sfKind: alloys switch off - alloys 0, ore still 1")
    CFG.SF_ALLOYS = True
    CFG.SF_ON = False
    K.check(int(PB.sfKind(riron, JString("Furnace"))) == 0, "FORTUNE sfKind: smelt.fortune.enabled off = 0")
    CFG.SF_ON = True
    K.eq([str(PB.oreOfBar(JString("Ingredient_Bar_Iron"))), PB.oreOfBar(JString("Ingredient_Bar_Bronze")), str(PB.oreOfBar(JString("Ingredient_Bar_Copper")))],
         ["Ore_Iron", None, "Ore_Copper"], "FORTUNE oreOfBar: Iron / Bronze (no ore) / Copper")

    # ---- 2. the tree value
    seen = []

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, a):
            seen.append([str(x) for x in a] if hasattr(a, "__len__") else [str(a)])
            if self.ans == "boom":
                raise RuntimeError("boom")
            if callable(self.ans):
                return self.ans(a)
            return self.ans
    K.eq(float(PB.sfValue(u, JString(k))), 0.0, "FORTUNE sfValue: no SkyyTrees = 0")
    br.put("tree:fn:bonus", Fn(JDouble(0.5)))
    v = float(PB.sfValue(u, JString(k)))
    K.check(v == 0.5 and seen[-1] == [k, "Smithing.SSmelt"], "FORTUNE sfValue: tree:fn:bonus {UUID, Smithing.SSmelt} -> 0.5 (%s, %s)" % (v, seen[-1:]))
    for ans, lab in ((JString("0.5"), "a String"), (JDouble(float("nan")), "NaN"), (JDouble(-1.0), "negative"), ("boom", "an exception"), (None, "null")):
        br.put("tree:fn:bonus", Fn(ans))
        K.eq(float(PB.sfValue(u, JString(k))), 0.0, "FORTUNE sfValue: %s = 0" % lab)
    br.put("tree:fn:bonus", Fn(JDouble(1.0)))
    br.put("profile:fn:key", Fn(JString(k + "-p2")))
    K.eq(float(PB.sfValue(u, JString(k))), 0.0, "FORTUNE sfValue: an inactive profile key = 0")
    br.remove("profile:fn:key")
    K.eq(float(PB.sfValue(u, JString(k))), 1.0, "FORTUNE sfValue: 10 levels x 0.10 = 1.0")

    # ---- 3. the mined-ore budget
    K.eq(int(PB.sfBudget(u, JString("Ore_Iron"), 5)), 0, "FORTUNE sfBudget: no skill:fn:oreBudget = 0 granted (no Fortune)")
    K.eq(int(PB.sfGrant(riron, 1, u, 5, True)), 0, "FORTUNE sfGrant: bridge MISSING + minedOnly = no Fortune units")
    bud = {"Ore_Iron": 3, "Ore_Copper": 10}
    asks = []

    def grant(a):
        ore, n = str(a[1]), int(a[2])
        asks.append((ore, n))
        if n < 0:   # SkyySkills 0.4.50: n < 0 = give back, answers how many were added
            bud[ore] = bud.get(ore, 0) - n
            return JInt(-n)
        g = min(n, bud.get(ore, 0))
        bud[ore] = bud.get(ore, 0) - g
        return JInt(g)
    br.put("skill:fn:oreBudget", Fn(grant))
    seen[:] = []
    K.eq(int(PB.sfGrant(riron, 1, u, 5, True)), 3, "FORTUNE sfGrant: 5 Iron units, 3 mined Iron ore left -> 3 Fortune units")
    K.check(seen[-1][0] == k and seen[-1][1] == "Ore_Iron" and seen[-1][2] == "5", "FORTUNE sfGrant: asked {UUID, Ore_Iron, 5}: %s" % seen[-1:])
    K.eq(int(PB.sfGrant(riron, 1, u, 5, True)), 0, "FORTUNE sfGrant: budget used up -> 0")
    bud.update({"Ore_Iron": 2, "Ore_Copper": 10})
    asks[:] = []
    K.eq(int(PB.sfGrant(rb, 2, u, 4, True)), 2, "FORTUNE sfGrant: Bronze (Copper + Iron bars) x4 - Copper grants 4, Iron 2 -> 2")
    K.eq(asks, [("Ore_Copper", 4), ("Ore_Iron", 4), ("Ore_Copper", -2)], "FORTUNE sfGrant: each parent's ore asked in turn, Copper's 2 over the final 2 given back")
    K.eq(bud["Ore_Copper"], 8, "FORTUNE sfGrant: Copper budget 10 -> 8 (only what the 2 Fortune units use)")
    bud.update({"Ore_Iron": 0, "Ore_Copper": 100})
    asks[:] = []
    K.check(int(PB.sfGrant(rb, 2, u, 4, True)) == 0 and bud["Ore_Copper"] == 100 and asks == [("Ore_Copper", 4), ("Ore_Iron", 4), ("Ore_Copper", -4)],
            "FORTUNE sfGrant (critic M1): Bronze with 100 Copper and 0 Iron budget burns no Copper budget: %s %s" % (asks, bud))
    # critic L5: ore per bar from the bar's own Furnace recipe (Test_Smelt_Gold = 2 Ore_Gold -> 1 Gold Ingot)
    rgold = CRR.getAssetMap().getAsset(JString("Test_Smelt_Gold"))
    rel = CRR.getAssetMap().getAsset(JString("Alloy_Electrum"))
    K.eq([int(PB.oreQtyOfBar(JString(x))) for x in ("Ingredient_Bar_Gold", "Ingredient_Bar_Silver", "Ingredient_Bar_Iron", "Ingredient_Bar_Bronze")],
         [2, 1, 1, 0], "FORTUNE oreQtyOfBar (critic L5): Gold 2, Silver 1, Iron 1, Bronze none")
    bud.update({"Ore_Gold": 100, "Ore_Silver": 100})
    asks[:] = []
    K.check(int(PB.sfGrant(rel, 2, u, 3, True)) == 3 and asks == [("Ore_Gold", 6), ("Ore_Silver", 3)],
            "FORTUNE sfGrant (critic L5): Electrum x3 charges 6 Gold ore + 3 Silver ore: %s" % asks)
    bud.update({"Ore_Gold": 5})
    asks[:] = []
    K.check(int(PB.sfGrant(rgold, 1, u, 3, True)) == 2 and asks == [("Ore_Gold", 6), ("Ore_Gold", -1)] and bud["Ore_Gold"] == 1,
            "FORTUNE sfGrant: an ore row of 2 ore per unit - 5 ore left grants 2 units, the odd ore given back: %s %s" % (asks, bud))
    for ans, lab in ((JInt(99), "more than asked"), (JInt(-4), "negative"), (JString("3"), "a String"), ("boom", "an exception")):
        br.put("skill:fn:oreBudget", Fn(ans))
        K.check(int(PB.sfBudget(u, JString("Ore_Iron"), 5)) == (5 if lab == "more than asked" else 0), "FORTUNE sfBudget: %s" % lab)
    br.put("skill:fn:oreBudget", Fn(JInt(0)))
    K.eq(int(PB.sfGrant(riron, 1, u, 7, False)), 7, "FORTUNE sfGrant: minedOnly off = every unit")
    K.eq(int(PB.sfGrant(riron, 0, u, 7, True)), 0, "FORTUNE sfGrant: kind 0 = none")

    # ---- 4. the roll
    K.eq([int(PB.sfExtras(f, r)) for f, r in ((0.0, 0.0), (1.0, 0.99), (1.0, 0.0), (0.5, 0.49), (0.5, 0.5), (2.5, 0.2), (2.5, 0.7), (float("nan"), 0.0), (-1.0, 0.0))],
         [0, 1, 1, 1, 0, 3, 2, 0, 0], "FORTUNE sfExtras: floor(F) + (roll < F mod 1)")
    CFG.SF_GUARD = 2
    K.eq(int(PB.sfExtras(5.7, 0.0)), 2, "FORTUNE sfExtras: guard 2")
    CFG.SF_GUARD = 0
    K.eq(int(PB.sfExtras(5.7, 0.0)), 0, "FORTUNE sfExtras: guard 0 = never")
    CFG.SF_GUARD = 100

    T = 9000000
    BIG = 10 ** 9

    def mk(name="Furnace", key=k):
        pb = PB(JString(name))
        pb.key = JString(key) if key else None
        pb.fuelMs = BIG
        return pb

    def outd(pb):
        return dict((str(e[0]), int(e[1])) for e in pb.outList())

    def sft(pb):
        return dict((str(e[0]), int(e[1])) for e in pb.sfTake())
    br.remove("acc:smelt:" + k)
    p = mk()
    p.addJobF(JString(RID), 10, 1000, JString("Ore_Iron*1"), T, 1.0, 6, True)
    K.check(int(p.queue.get(0).fu) == 6 and float(p.queue.get(0).sf) == 1.0, "BENCH: the job keeps sf 1.0 / fu 6")
    ds = str(p.describe(1, True)[1])
    K.check("Smelting Fortune 100 percent on 6 of them" in ds, "BENCH: the running line names it: %r" % ds)
    d = int(p.advance(T + 10000))
    K.check(d == 10 and outd(p) == {"Ingredient_Bar_Iron": 16} and sft(p) == {RID: 6} and p.sfTake().isEmpty(),
            "BENCH: 10 units, 6 with F 100 percent -> 16 Iron Ingots, ledger 6 then empty: %s" % outd(p))
    p = mk()
    p.addJobF(JString(RID), 4000, 1, JString("Ore_Iron*1"), T, 0.5, 4000, True)
    p.advance(T + 10 ** 6)
    o = outd(p).get("Ingredient_Bar_Iron", 0)
    x = sft(p).get(RID, 0)
    K.check(o == 4000 + x and 1800 <= x <= 2200 and int(p.queued()) == 0, "BENCH: F 50 percent over 4000 units -> %d extras (about 2000), out = 4000 + ledger exactly (%d)" % (x, o))
    p = mk()
    p.addJobF(JString(RID), 5, 1000, JString("Ore_Iron*1"), T, 2.0, 5, True)
    p.advance(T + 2000)
    br.put("skill:fn:oreBudget", Fn(grant))
    asks[:] = []
    n = int(p.cancel())
    K.eq(asks, [("Ore_Iron", -3)], "BENCH (critic M1): cancel gives the 3 cancelled Fortune units' budget back, once")
    asks[:] = []
    p.cancel()
    K.eq(asks, [], "BENCH: a second cancel gives nothing")
    pnb = mk()
    pnb.addJobF(JString(RID), 4, 1000, JString("Ore_Iron*1"), T, 2.0, 4, False)
    pnb.cancel()
    K.eq(asks, [], "BENCH: Fortune units not taken from the budget (minedOnly was off) give nothing back")
    K.check(n == 3 and outd(p) == {"Ingredient_Bar_Iron": 6, "Ore_Iron": 3} and p.queue.isEmpty(),
            "BENCH: F 200 percent, 2 units done (2 + 4 bars), cancel returns the 3 ores only - no bar: %s" % outd(p))
    p.advance(T + 10 ** 6)
    K.eq(outd(p), {"Ingredient_Bar_Iron": 6, "Ore_Iron": 3}, "BENCH: nothing more after the cancel")
    p = mk()
    p.addJobF(JString("Skyy_No_Such_Recipe"), 2, 1000, JString("Ore_Iron*1"), T, 1.0, 2, True)
    p.advance(T + 10 ** 6)
    K.check(outd(p) == {"Ore_Iron": 2} and p.sfTake().isEmpty(), "BENCH: the no-output fallback gives the inputs back, no extras: %s" % outd(p))
    p = mk("Tannery")
    p.addJobF(JString(RID), 3, 1000, JString("Ore_Iron*1"), T, 1.0, 3, True)
    p.advance(T + 10 ** 6)
    K.check(outd(p).get("Ingredient_Bar_Iron") == 3 and p.sfTake().isEmpty(), "BENCH: never on the Tannery: %s" % outd(p))
    if rch is not None:
        p = mk()
        p.addJobF(JString(str(rch.getId())), 2, 1000, JString("X*1"), T, 3.0, 2, True)
        p.advance(T + 10 ** 6)
        K.check(p.sfTake().isEmpty(), "BENCH: a non-bar output (%s) makes no extras even with fu set" % rch.getId())
    CFG.SF_ON = False
    p = mk()
    p.addJobF(JString(RID), 3, 1000, JString("Ore_Iron*1"), T, 1.0, 3, True)
    p.advance(T + 10 ** 6)
    K.check(outd(p) == {"Ingredient_Bar_Iron": 3}, "BENCH: switched off after queuing - no extras (live emergency switch): %s" % outd(p))
    CFG.SF_ON = True
    br.put("acc:smelt:" + k, JString("5|50|0|1|" + k))
    p = mk()
    p.fuelMs = 0
    p.addFuel(JString("Wood_Oak_Trunk"), 3)
    p.addJobF(JString(RID), 4, 1000, JString("Ore_Iron*1"), T, 1.0, 4, True)
    p.advance(T + 10 ** 6)
    K.check(outd(p) == {"Ingredient_Bar_Iron": 8} and int(p.fuelCount()) == 3 and int(p.fuelMs) == 0,
            "BENCH: Eternal Flame + F 100 percent - 8 bars, the fuel stays: %s fuel %d" % (outd(p), int(p.fuelCount())))
    br.remove("acc:smelt:" + k)
    # merge rules + clamps
    p = mk()
    p.addJobF(JString(RID), 3, 1000, JString("Ore_Iron*1"), T, 1.0, 2, True)
    p.addJobF(JString(RID), 3, 1000, JString("Ore_Iron*1"), T, 1.0, 3, True)
    p.addJobF(JString(RID), 2, 1000, JString("Ore_Iron*1"), T, 0.0, 0, True)
    p.addJobF(JString(RID), 2, 1000, JString("Ore_Iron*1"), T, 0.5, 1, True)
    p.addJob(JString(RID), 1, 1000, JString("Ore_Iron*1"), T)
    p.addJobF(JString(RID), 2, 1000, JString("Ore_Iron*1"), T, 0.5, 1, False)
    q = [(int(j.count), int(j.fu), float(j.sf)) for j in p.queue]
    K.eq([bool(j.fb) for j in p.queue], [True, True, False], "BENCH: another give-back flag = a new job")
    K.eq(q, [(8, 5, 1.0), (3, 1, 0.5), (2, 1, 0.5)], "BENCH: merges keep one snapshot per job (same F / no Fortune units merge, another F = a new job)")
    p2 = mk()
    p2.addJobF(JString(RID), 2, 1000, JString("Ore_Iron*1"), T, 1.0, 5, True)
    p2.addJobF(JString(RID), 2, 999, JString("Ore_Iron*1"), T, -1.0, 2, True)
    K.eq([(int(j.count), int(j.fu)) for j in p2.queue], [(2, 2), (2, 0)], "BENCH: fu clamped to count; F <= 0 = no Fortune units")
    # save / load
    pr = Props()
    p.toProps(pr)
    K.check(str(pr.getProperty("Furnace.q.0.fu")) == "5" and float(str(pr.getProperty("Furnace.q.0.sf"))) == 1.0 and str(pr.getProperty("Furnace.q.1.fu")) == "1",
            "SAVE: q.<i>.sf / fu written")
    p3 = mk()
    p3.fromProps(pr)
    K.eq([(int(j.count), int(j.fu), float(j.sf)) for j in p3.queue], q, "SAVE: loaded back exactly")
    K.check(str(pr.getProperty("Furnace.q.0.fb")) == "1" and pr.getProperty("Furnace.q.2.fb") is None and [bool(j.fb) for j in p3.queue] == [True, True, False],
            "SAVE: q.<i>.fb written only for budget units and loaded back")
    pr.setProperty("Furnace.q.0.fu", "99")
    pr.setProperty("Furnace.q.1.sf", "abc")
    p3.fromProps(pr)
    K.eq([(int(j.count), int(j.fu)) for j in p3.queue], [(8, 8), (3, 0), (2, 1)], "SAVE: a hand-edited fu is clamped to the count, a bad sf = none")
    pr.setProperty("Furnace.q.1.sf", "NaN")
    p3.fromProps(pr)
    K.eq(int(p3.queue.get(1).fu), 0, "SAVE: NaN = none")
    pr2 = Props()
    p0 = mk()
    p0.addJob(JString(RID), 2, 1000, JString("Ore_Iron*1"), T)
    p0.toProps(pr2)
    K.check(pr2.getProperty("Furnace.q.0.sf") is None and pr2.getProperty("Furnace.q.0.fu") is None, "SAVE: a job without Fortune writes no sf / fu (0.8.20 file)")
    # drainSf -> crafts.log lines
    CL.PENDING.clear()
    p = mk()
    p.addJobF(JString(RID), 2, 1000, JString("Ore_Iron*1"), T, 1.0, 2, True)
    p.advance(T + 10 ** 6)
    PT.drainSf(JString(k), p)
    lines = [str(x) for x in CL.PENDING.toArray()]
    K.check(len(lines) == 1 and ("SMELT-FORTUNE %s +2 extra bars" % RID) in lines[0], "LOG: drainSf writes one SMELT-FORTUNE line: %s" % lines)
    CL.PENDING.clear()
    PT.drainSf(JString(k), p)
    K.check(CL.PENDING.isEmpty(), "LOG: nothing twice")

    # ---- 5. config + the reads flag
    pp = Props()
    CFG.sfKeys(pp, True)
    K.check(bool(CFG.SF_ON) and bool(CFG.SF_ALLOYS) and bool(CFG.SF_MINED) and int(CFG.SF_GUARD) == 100 and str(br.get("tree:reads:SkyySacks")) == "Smithing.SSmelt",
            "CFG: defaults true / true / true / 100; tree:reads:SkyySacks = Smithing.SSmelt")
    pp.setProperty("smelt.fortune.enabled", "false")
    pp.setProperty("smelt.fortune.alloys", "false")
    pp.setProperty("smelt.fortune.minedOnly", "false")
    pp.setProperty("smelt.fortune.guard", "5000")
    CFG.sfKeys(pp, False)
    K.check(not bool(CFG.SF_ON) and not bool(CFG.SF_ALLOYS) and not bool(CFG.SF_MINED) and int(CFG.SF_GUARD) == 1000 and br.get("tree:reads:SkyySacks") is None,
            "CFG: hand edits read (guard clamped 1000); off = the reads flag removed")
    CFG.sfKeys(Props(), False)
    K.check(str(br.get("tree:reads:SkyySacks")) == "Smithing.SSmelt" and str(CFG.readsValue()) == "Smithing.SSmelt" and str(CFG.READS_PUT) == "Smithing.SSmelt",
            "CFG: back on - listed again (one writer, readsValue = the whole list)")
    br.put("tree:reads:SkyySacks", JString("Other.Node"))
    CFG.sfUnpub()
    K.check(str(br.get("tree:reads:SkyySacks")) == "Other.Node", "CFG: sfUnpub removes only our own value")
    br.remove("tree:reads:SkyySacks")
    for kk in ("tree:fn:bonus", "skill:fn:oreBudget"):
        br.remove(kk)


_orig_alloy_cases = T20.alloy_cases


def _both(K, L):
    _orig_alloy_cases(K, L)
    fortune_cases(K, L)


def _smelt(ore, bar, secs):
    # an ore -> bar Furnace recipe as a standalone file (the V loader slice loads recipe files, not the recipes inside item JSONs)
    return {"Input": [{"ItemId": ore, "Quantity": 1}], "PrimaryOutput": {"ItemId": bar, "Quantity": 1}, "Output": [{"ItemId": bar, "Quantity": 1}],
            "BenchRequirement": [{"Type": "Processing", "Id": "Furnace"}], "TimeSeconds": secs}


def run_alloy(out, jar, scratch, home):
    """T20.run_alloy with two more files in the fake pack: Test_Smelt_Iron / Test_Smelt_Copper (vanilla's ore -> bar shape, bench Furnace)."""
    import json, zipfile
    T20.alloy_cases = _both
    _zf = zipfile.ZipFile

    class _Z(_zf):
        def __init__(self, f, mode="r", *a, **kw):
            _zf.__init__(self, f, mode, *a, **kw)
            self._fake = mode == "w" and str(f).endswith("fakealloys.zip")

        def close(self):
            if getattr(self, "_fake", False):
                self._fake = False
                self.writestr("Server/Item/Recipes/SkyWynn/Test_Smelt_Iron.json", json.dumps(_smelt("Ore_Iron", "Ingredient_Bar_Iron", 14), indent=1))
                self.writestr("Server/Item/Recipes/SkyWynn/Test_Smelt_Copper.json", json.dumps(_smelt("Ore_Copper", "Ingredient_Bar_Copper", 10), indent=1))
                g = _smelt("Ore_Gold", "Ingredient_Bar_Gold", 12)
                g["Input"][0]["Quantity"] = 2   # critic L5: 2 ore per bar
                self.writestr("Server/Item/Recipes/SkyWynn/Test_Smelt_Gold.json", json.dumps(g, indent=1))
                self.writestr("Server/Item/Recipes/SkyWynn/Test_Smelt_Silver.json", json.dumps(_smelt("Ore_Silver", "Ingredient_Bar_Silver", 12), indent=1))
            _zf.close(self)
    T20.zipfile.ZipFile = _Z
    try:
        T20.run_alloy(out, jar, scratch, home)
    finally:
        T20.zipfile.ZipFile = _zf


def run_sup(out, jar, scratch, home):
    T18.run_sup(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("alloy", run_alloy), ("sup", run_sup), ("tg", T18.T16.run_tg), ("keys", T18.T17.run_keys), ("live", T18.T0810.run_live10)],
           __file__, live=(T18.T16.T15.BETA, "Skyy_SkyySacks"))
