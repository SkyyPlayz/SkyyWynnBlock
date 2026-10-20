"""Bare-JVM check for SkyyEssentials 0.1.16 (benches keep their tier when broken; tools/essentials_0_1_16_patch.py). Build first:
    python tools/essentials_0_1_16_patch.py && python SkyyEssentials/build_skyyessentials_0.1.16.py

    python SkyyEssentials/test_skyyessentials_0.1.16.py [--jar <SkyyEssentials-0.1.16.jar>] [--dir <scratch folder>] [--keep] [--only bench,...]

The 0.1.15 harness (test_skyyessentials_0.1.15.py, loaded as a module; it loads 0.1.14's ... 0.1.11's) runs its phases wicon / rename / back /
menu / main / trade / tpa / chat / keep / compost / live1 / live2 against this jar, each in a fresh JVM (-Xverify:all, the game's own JRE);
checks that change ON PURPOSE are listed in SUPERSEDED. New phase bench (the real engine classes BenchBlock / ItemStack / codecs):
  B1  the 7 new classes load and verify; the config row gameplay.benchTiers (loader + default file + Server Setup kit row, default ON)
  B2  BREAK: an upgraded bench (T3, materials inside) -> strip takes the materials OUT of the bench (vanilla's refund after it drops nothing)
  B3  DROP: the bench item that spawns there is tagged once - tier 3, the same materials (ids + amounts), the tooltip (ItemDisplayMetadata:
      name " [T3]", description "T3 Bench ..."); a second drop gets nothing; a 2-stack is never tagged; materials counted: bench + item +
      refunds = what was paid, every step
  B4  a drop that came FIRST waits (DROPPED) and is matched by the removal after it; a removal older than 1.5 s never tags (it is refunded)
  B5  PLACE: the pending placement is taken once (expired = nothing); applyCore restores tier + materials once (a bench already at the tier
      gets nothing: never twice), clamps to the bench's top tier, refuses tier <= 1 (caller refunds)
  B6  switch off / another keeper / tier-1 bench / unknown item = vanilla (nothing taken out of the bench)
  B7  KeepBenchTiers items ("KeepBenchTiers:Tier" + "KeepBenchTiers:UpgradeItems" through its own ArrayCodec shape) read as tier + materials
  B8  a full cycle break -> drop -> place -> break -> drop keeps the same tier and materials, nothing gained or lost
  R1  (review) a placement lives 250 ms / two world ticks; it applies only to the same bench kind, and brings the materials only when the
      placer's count of the tagged item went down (failed placement / removeItemInHand=false / creative = tier only, never a refund)
  R2  (review) removal records older than 5 s are purged in any world; materials go back only on a live world (stop() never throws)
  R3  (review) the drop match radius is 1.5 blocks
  Z   class compare 0.1.15 -> 0.1.16: the 7 new classes; changed only TCfg, the plugin and the config kit classes; trade / tpa / msg / homes /
      back / warps / durability byte-identical
NOT runnable in a bare JVM: the ECS hooks (break / place in a running world, SkyySacks auto-pickup order) - in-game test steps.
Default scratch: tools/dev/scratch/bench2/ess (deleted unless --keep).
"""
import os, sys, re, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "dev"))

_s15 = importlib.util.spec_from_file_location("test_skyyessentials_0_1_15", os.path.join(HERE, "test_skyyessentials_0.1.15.py"))
T15 = importlib.util.module_from_spec(_s15)
_s15.loader.exec_module(T15)
T14, T13, T12, T11 = T15.T14, T15.T13, T15.T12, T15.T11

VERSION = "0.1.16"
PREV = "0.1.15"
PKG = "com.skyy.essentials."
SCRATCH = os.path.abspath(T11.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "bench2", "ess")))
JAR = os.path.abspath(T11.arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
PREV_JAR = os.path.join(HERE, "SkyyEssentials-%s.jar" % PREV)
KEEP = "--keep" in sys.argv
for _m in (T11, T12, T13, T14, T15):
    _m.VERSION, _m.SCRATCH, _m.JAR, _m.KEEP = VERSION, SCRATCH, JAR, KEEP
FAILS = T14.FAILS
check = T14.check
NEW = ["EssBench", "EssBenchApply", "EssBenchRefund", "EssBenchTick", "EssBenchDropSys", "EssBenchPlaceSys", "EssBenchChunkSys"]
# old checks that change on purpose with 0.1.16 (filled from the first run; each says why)
T14.SUPERSEDED += [
    (re.compile(r"^Z: "), "the 0.1.15 byte-compare (0.1.14 -> 0.1.15) - replaced by this harness's Z"),
    (re.compile(r"^K2: 34 loader rows"), "35 loader rows now (+ gameplay.benchTiers last) - phase bench B9"),
    (re.compile(r"^K4: "), "the live file gets the keys it lacks (gameplay.benchTiers) - phase bench B9"),
    (re.compile(r"^K5: setup registers EssDurDeath \+ EssBackSys"), "6 systems now (+ the 4 bench systems) - phase bench B9"),
    (re.compile(r"^U0: non-class files"), "+ CREDITS.txt (the Workbench Tier Keeper MIT notice) - phase bench B9"),
]


def run_bench(jar):
    B = T11.boot(jar)
    import jpype
    from jpype import JClass, JArray, JProxy, JObject
    Cls = JClass("java.lang.Class")
    loader = JClass(PKG + "EssBench").class_.getClassLoader()
    for n in NEW:
        try:
            Cls.forName(PKG + n, True, loader)
            ok = True
        except Exception as e:
            ok = False
            print("  load", n, e)
        check(ok, "B1: %s loads and verifies (-Xverify:all)" % n)
    EB = JClass(PKG + "EssBench")
    W = T11.World(B)          # real Item assets in a fake store (ItemStack needs the item map)
    for iid in ("Bench_WorkBench", "Bench_Furnace", "Ingredient_Bar_Iron", "Wood_Oak_Plank", "Ingredient_Fibre", "Ingredient_Bar_Copper",
                "Rock_Stone_Cobble"):
        W.item(iid, stack=64)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BBK = JClass("com.hypixel.hytale.builtin.crafting.component.BenchBlock")
    IDM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata")
    TC = JClass(PKG + "TCfg")
    keys = [str(k) for k in TC.KEYS]
    check("gameplay.benchTiers" in keys and str(TC.DEFAULTS[keys.index("gameplay.benchTiers")]) == "true", "B1: loader row gameplay.benchTiers, default true")
    check("gameplay.benchTiers=true" in str(TC.DEFAULT_TEXT), "B1: the new-file text has gameplay.benchTiers=true")
    check(bool(EB.ON) and EB.OTHER is None, "B1: ON by default, no other keeper")
    check(str(EB.tagText(2)) == "T2 Bench" and str(EB.tagText(3)) == "T3 Bench", "B1: the tier tag = tools/tier_tags.py ladder_tag")

    def items(*pairs):
        return JArray(IS)([IS(a, b) for a, b in pairs])

    def tally(arrs):
        t = {}
        for arr in arrs:
            if arr is None:
                continue
            for s in arr:
                if s is None or s.isEmpty():
                    continue
                t[str(s.getItemId())] = t.get(str(s.getItemId()), 0) + int(s.getQuantity())
        return t

    PAID = items(("Ingredient_Bar_Iron", 10), ("Wood_Oak_Plank", 4), ("Ingredient_Fibre", 6))
    PAID_T = tally([PAID])
    now = 10_000_000

    def reset():
        EB.REMOVED.clear()
        EB.DROPPED.clear()
        EB.PENDING.clear()
        EB.count()
        EB.ON = True
        EB.OTHER = None

    # ---------------- B2 break
    reset()
    bb = BBK(3, PAID)
    r = EB.strip(bb, "w1", 10, 64, 20, "Bench_WorkBench", None, now)
    check(r is not None and len(bb.getUpgradeItems()) == 0 and int(bb.getTierLevel()) == 3, "B2: strip takes every material out of the T3 bench (vanilla refunds nothing)")
    check(int(EB.PEND) == 1 and tally([r[6]]) == PAID_T, "B2: the removal record holds exactly what was paid: %s" % tally([r[6]] if r is not None else []))
    # ---------------- B3 drop
    two = EB.matchDrop("w1", IS("Bench_WorkBench", 2), 10.5, 64.0, 20.5, None, now + 5)
    check(two is None and int(EB.PEND) == 1, "B3: a 2-stack drop is never tagged (the removal waits)")
    other = EB.matchDrop("w2", IS("Bench_WorkBench", 1), 10.5, 64.0, 20.5, None, now + 5)
    check(other is None and int(EB.PEND) == 1, "B3: a drop in another world is not matched")
    far = EB.matchDrop("w1", IS("Bench_WorkBench", 1), 30.5, 64.0, 20.5, None, now + 5)
    check(far is None and int(EB.PEND) == 1, "B3: a drop 20 blocks away is not matched")
    out = EB.matchDrop("w1", IS("Bench_WorkBench", 1), 10.5, 64.0, 20.5, None, now + 10)
    check(out is not None and int(EB.tierOf(out)) == 3, "B3: the bench item that drops there carries tier 3")
    got = tally([EB.itemsOf(out)]) if out is not None else {}
    check(got == PAID_T, "B3: ... and exactly the paid materials: %s" % got)
    check(int(EB.PEND) == 0 and tally([bb.getUpgradeItems()]) == {}, "B3: the removal is used up; bench empty -> bench + item = paid (no copy)")
    again = EB.matchDrop("w1", IS("Bench_WorkBench", 1), 10.5, 64.0, 20.5, None, now + 20)
    check(again is None, "B3: a second bench drop there gets nothing (one removal tags one drop)")
    disp = out.getFromMetadataOrNull(IDM.KEYED_CODEC) if out is not None else None
    md = str(out.getMetadata().toJson()) if out is not None else ""
    check(disp is not None and disp.getName() is not None and disp.getDescription() is not None, "B3: the item has its own tooltip (ItemDisplayMetadata name + description)")
    check(" [T3]" in md and "T3 Bench" in md and "#e8c25a" in md and "Keeps its upgrades" in md, "B3: name ' [T3]', tooltip starts 'T3 Bench' in level gold: %s" % md[:300])
    check(md.find("T3 Bench") < md.find("Keeps its upgrades"), "B3: the tier tag comes first in the tooltip (tier-tag rule)")
    check(int(EB.tierOf(IS("Bench_WorkBench", 1))) == 0, "B3: a plain bench item has no tier")
    # ---------------- B4 order + age
    reset()
    ref = JObject("drop-ref-1", JClass("java.lang.Object"))
    first = EB.matchDrop("w1", IS("Bench_Furnace", 1), 5.5, 70.0, 5.5, ref, now)
    check(first is None and EB.DROPPED.size() == 1, "B4: a drop that comes before its removal waits (DROPPED)")
    bf = BBK(2, items(("Ingredient_Bar_Copper", 5)))
    EB.strip(bf, "w1", 5, 70, 5, "Bench_Furnace", None, now + 3)
    d = EB.takeDropped("w1", "Bench_Furnace", 5.5, 70.5, 5.5, now + 4)
    check(d is not None and str(d[5]) == "drop-ref-1" and EB.DROPPED.size() == 0, "B4: the removal after it finds that drop (the tick tags it)")
    EB.purgeDropped(now + 10_000)
    reset()
    EB.strip(BBK(3, PAID), "w1", 1, 1, 1, "Bench_WorkBench", None, now)
    late = EB.matchDrop("w1", IS("Bench_WorkBench", 1), 1.5, 1.0, 1.5, None, now + 1600)
    rs = EB.takeRemovedOf("w1")
    check(late is None and len(rs) == 1 and now + 1600 - int(rs[0][7]) > int(EB.MATCH_MS), "B4: a removal older than 1.5 s never tags - the tick gives its materials back instead (exclusive)")
    old_d = EB.matchDrop("w1", IS("Bench_WorkBench", 1), 1.5, 1.0, 1.5, JObject("r2", JClass("java.lang.Object")), now)
    EB.purgeDropped(now + 2500)
    check(EB.DROPPED.size() == 0, "B4: waiting drops are forgotten after 2 s")
    # ---------------- B5 place
    reset()
    tagged = EB.tag(IS("Bench_WorkBench", 1), 3, PAID)
    Obj, Int, Lng, Bool = JClass("java.lang.Object"), JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")

    def pend(tier, its, at, before, kind="Bench_WorkBench"):
        return JArray(Obj)([kind, Int.valueOf(tier), its, Lng.valueOf(at), tagged, None, Int.valueOf(before), Bool.FALSE])
    k = EB.key("w1", 7, 65, 8)
    EB.putPending(k, pend(3, EB.itemsOf(tagged), now, -1), now)
    p1 = EB.takePending(k, now + 100)
    p2 = EB.takePending(k, now + 100)
    check(p1 is not None and p2 is None, "B5: a pending placement is taken once")
    EB.putPending(k, pend(3, EB.itemsOf(tagged), now, -1), now)
    check(EB.takePending(k, now + 300) is None, "R1: an expired placement (250 ms) restores nothing")
    check(int(EB.PLACE_MS) == 250, "R1: the placement window is 250 ms")
    EB.putPending(k, pend(3, EB.itemsOf(tagged), now, -1), now)
    EB.agePending("w1")
    check(EB.PENDING.containsKey(k), "R1: a placement survives the first tick of its world")
    EB.agePending("w2")
    check(EB.PENDING.containsKey(k), "R1: ... other worlds' ticks do not age it")
    EB.agePending("w1")
    check(not EB.PENDING.containsKey(k), "R1: ... and is gone at the second tick")
    pd = pend(3, EB.itemsOf(tagged), now, 2)
    check(EB.admit("Bench_Furnace", pd, 1) is None, "R1: a placement record meeting another bench kind is not applied (no refund either)")
    a1 = EB.admit("Bench_WorkBench", pd, 1)
    check(a1 is not None and int(a1[1]) == 3 and tally([a1[2]]) == PAID_T, "R1: the tagged item really left the inventory (2 -> 1) = tier + materials")
    a2 = EB.admit("Bench_WorkBench", pd, 2)
    check(a2 is not None and int(a2[1]) == 3 and len(a2[2]) == 0, "R1: the item is still there (failed placement given back / removeItemInHand=false / creative) = tier only, no materials")
    a3 = EB.admit("Bench_WorkBench", pd, -1)
    check(a3 is not None and len(a3[2]) == 0, "R1: the inventory could not be counted after = tier only")
    a4 = EB.admit("Bench_WorkBench", pend(3, EB.itemsOf(tagged), now, -1), -1)
    check(a4 is not None and tally([a4[2]]) == PAID_T, "R1: no player to count (vanilla always uses the item up then) = tier + materials")
    swap = BBK()
    a5 = EB.admit("Bench_WorkBench", pd, 2)
    EB.applyCore(swap, int(a5[1]), 3, a5[2])
    check(tally([swap.getUpgradeItems()]) == {}, "R1: the reviewer's swap (tagged placement fails, a plain bench placed there) gets no materials out of nothing")
    nb = BBK()
    t0 = int(nb.getTierLevel())
    rc = EB.applyCore(nb, 3, 3, p1[2])
    check(int(rc) == 1 and int(nb.getTierLevel()) == 3 and tally([nb.getUpgradeItems()]) == PAID_T, "B5: a fresh bench (tier %d) gets tier 3 + the materials" % t0)
    rc2 = EB.applyCore(nb, 3, 3, p1[2])
    check(int(rc2) == 0 and tally([nb.getUpgradeItems()]) == PAID_T, "B5: applied twice (another keeper) = nothing added the second time")
    cb = BBK()
    check(int(EB.applyCore(cb, 3, 2, p1[2])) == 1 and int(cb.getTierLevel()) == 2 and tally([cb.getUpgradeItems()]) == PAID_T,
          "B5: a bench whose top tier is 2 is clamped to T2 and still gets every paid material")
    check(int(EB.applyCore(BBK(), 2, 1, p1[2])) == -1, "B5: a bench without upgrades refuses (the caller gives the materials back)")
    # ---------------- R2 old records, dead worlds; R3 radius
    reset()
    EB.strip(BBK(3, PAID), "deadworld", 1, 1, 1, "Bench_WorkBench", None, now)
    EB.strip(BBK(2, PAID), "w1", 2, 2, 2, "Bench_WorkBench", None, now + 4000)
    old = EB.takeOld(now + 5500)
    check(len(old) == 1 and str(old[0][0]) == "deadworld" and int(EB.PEND) == 1, "R2: a removal older than 5 s is purged whatever its world; the fresh one stays")
    try:
        EB.refundLater(old[0])
        EB.stop()
        ok = True
    except Exception as e:
        ok = False
        print("  R2", e)
    check(ok and int(EB.PEND) == 0, "R2: materials for a world that is not running are dropped with a WARN; stop() never calls a dead world")
    check(abs(float(EB.RADIUS2) - 2.25) < 1e-9, "R3: match radius 1.5 blocks")
    reset()
    EB.strip(BBK(3, PAID), "w1", 10, 64, 20, "Bench_WorkBench", None, now)
    check(EB.matchDrop("w1", IS("Bench_WorkBench", 1), 12.5, 64.0, 20.5, None, now + 1) is None, "R3: a bench drop 2 blocks away is not matched")
    check(EB.matchDrop("w1", IS("Bench_WorkBench", 1), 10.5, 64.0, 20.5, None, now + 2) is not None, "R3: the drop at the block (vanilla spawn spot) still is")
    # ---------------- B6 vanilla cases
    reset()
    EB.ON = False
    b6 = BBK(3, PAID)
    check(EB.strip(b6, "w1", 1, 2, 3, "Bench_WorkBench", None, now) is None and tally([b6.getUpgradeItems()]) == PAID_T, "B6: switch off = vanilla (materials stay for vanilla's refund)")
    EB.ON = True
    EB.OTHER = "KeepBenchTiers"
    check(EB.strip(b6, "w1", 1, 2, 3, "Bench_WorkBench", None, now) is None and tally([b6.getUpgradeItems()]) == PAID_T, "B6: another keeper installed = ours stands down on break")
    EB.OTHER = None
    b1 = BBK(1, items(("Wood_Oak_Plank", 1)))
    check(EB.strip(b1, "w1", 1, 2, 3, "Bench_WorkBench", None, now) is None and len(b1.getUpgradeItems()) == 1, "B6: a tier-1 bench = vanilla")
    check(EB.strip(b6, "w1", 1, 2, 3, None, None, now) is None and tally([b6.getUpgradeItems()]) == PAID_T, "B6: an unknown bench item = vanilla")
    check(int(EB.PEND) == 0, "B6: nothing recorded")
    # ---------------- B7 KeepBenchTiers items
    Codec = JClass("com.hypixel.hytale.codec.Codec")
    AC = JClass("com.hypixel.hytale.codec.codecs.array.ArrayCodec")
    gen = JProxy("java.util.function.IntFunction", dict(apply=lambda n: JArray(IS)(int(n))))
    kcod = AC(IS.CODEC, gen)
    kb = IS("Bench_Furnace", 1).withMetadata("KeepBenchTiers:Tier", Codec.INTEGER, JClass("java.lang.Integer").valueOf(2))
    kb = kb.withMetadata("KeepBenchTiers:UpgradeItems", kcod, items(("Ingredient_Bar_Copper", 5), ("Rock_Stone_Cobble", 12)))
    check(int(EB.tierOf(kb)) == 2 and tally([EB.itemsOf(kb)]) == {"Ingredient_Bar_Copper": 5, "Rock_Stone_Cobble": 12},
          "B7: a KeepBenchTiers item reads as T2 + its materials: %s" % tally([EB.itemsOf(kb)]))
    kb1 = IS("Bench_Furnace", 1).withMetadata("KeepBenchTiers:Tier", Codec.INTEGER, JClass("java.lang.Integer").valueOf(1))
    check(int(EB.tierOf(kb1)) == 0, "B7: a KeepBenchTiers tier 1 = no tier")
    # ---------------- B8 full cycle
    reset()
    bench = BBK(3, PAID)
    for cyc in range(3):
        EB.strip(bench, "w1", 4, 64, 4, "Bench_WorkBench", None, now + cyc * 10)
        it = EB.matchDrop("w1", IS("Bench_WorkBench", 1), 4.5, 64.0, 4.5, None, now + cyc * 10 + 1)
        check(it is not None and len(bench.getUpgradeItems()) == 0 and tally([EB.itemsOf(it)]) == PAID_T, "B8: cycle %d break -> item carries T3 + the paid materials" % cyc)
        bench = BBK()
        EB.applyCore(bench, int(EB.tierOf(it)), 3, EB.itemsOf(it))
        check(int(bench.getTierLevel()) == 3 and tally([bench.getUpgradeItems()]) == PAID_T and int(EB.PEND) == 0,
              "B8: cycle %d place -> T3 bench holds the paid materials again (nothing gained or lost)" % cyc)
    # ---------------- B9 config rows, the live file, setup order, jar files (the old K2 / K4 / K5 / U0 re-checked for 0.1.16)
    rows = T11.script_list("build_skyyessentials_%s.py" % VERSION, "ROWS")
    prow = T11.script_list("build_skyyessentials_%s.py" % PREV, "ROWS")
    check(len(rows) == len(prow) + 1 and rows[:-1] == prow and rows[-1][0] == "gameplay.benchTiers" and rows[-1][6] == "true",
          "B9: loader rows = 0.1.15's %d unchanged + gameplay.benchTiers last (default true)" % len(prow))
    kit = T11.script_list("build_skyyessentials_%s.py" % VERSION, "KIT_ROWS", {"CF": "@config.properties:"})
    pkit = T11.script_list("build_skyyessentials_%s.py" % PREV, "KIT_ROWS", {"CF": "@config.properties:"})
    kb = [r for r in kit if r[0] == "gameplay.benchTiers"]
    check(len(kit) == len(pkit) + 1 and [r for r in kit if r[0] != "gameplay.benchTiers"] == pkit and len(kb) == 1 and kb[0][2] == "gameplay"
          and kb[0][3] == "bool" and kb[0][4] == "true" and "live" in kb[0][9] and kb[0][11].startswith("field:EssBench.ON@config.properties:"),
          "B9: the Server Setup row (Essentials > Gameplay, bool, default on, live, field EssBench.ON); the other rows unchanged")
    check(len(kb) == 1 and len(kb[0][1]) <= 40 and len(kb[0][10]) <= 100, "B9: kit label / help lengths")
    Paths = JClass("java.nio.file.Paths")
    ES = JClass(PKG + "EssStore")
    livef = os.path.join(T11.LIVE, "config.properties")
    if os.path.isfile(livef):
        h2 = os.path.join(SCRATCH, "bench", "live", "Skyy_SkyyEssentials")
        os.makedirs(h2, exist_ok=True)
        shutil.copy2(livef, os.path.join(h2, "config.properties"))
        T11.paths_for(TC, ES, Paths, h2)
        cfg0 = open(livef, "rb").read().decode("latin-1")
        TC.load()
        cfg1 = open(os.path.join(h2, "config.properties"), "rb").read().decode("latin-1")
        nl = "\r\n" if "\r\n" in cfg0 else "\n"
        have = T11.props_of(cfg0)
        byk = dict((r[0], r) for r in rows)
        miss = [rows[int(i_)][0] for i_ in TC.FILE_ORDER if rows[int(i_)][0] not in have]      # appended in the file order
        lines = ["#", "# ---- added by SkyyEssentials %s (keys this file did not have yet, with their defaults) ----" % VERSION]
        for k_ in miss:
            lines += ["# " + byk[k_][8], "%s=%s" % (k_, byk[k_][6])]
        add = ("" if cfg0.endswith("\n") else nl) + nl.join(lines) + nl if miss else ""
        check("gameplay.benchTiers" in miss and cfg1 == cfg0 + add, "B9: the live config.properties = its bytes + exactly the keys it lacked %s: %s" % (miss, cfg1[len(cfg0):][:300]))
        p0, p1 = T11.props_of(cfg0), T11.props_of(cfg1)
        check(dict((k_, v) for k_, v in p1.items() if k_ not in miss) == p0 and p1.get("gameplay.benchTiers") == "true" and bool(EB.ON),
              "B9: every existing value kept, gameplay.benchTiers=true read back")
    else:
        check(False, "B9: no live config at %s" % livef)
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    mm = [m_ for m_ in pool.get(PKG + "SkyyEssentialsPlugin").getDeclaredMethods() if str(m_.getName()) == "setup"][0]
    bos = JClass("java.io.ByteArrayOutputStream")()
    JClass("javassist.bytecode.InstructionPrinter")(JClass("java.io.PrintStream")(bos)).print_(mm)
    su = str(bos.toString()).splitlines()
    rs_ = [i for i, l in enumerate(su) if "registerSystem(" in l]
    st_ = [i for i, l in enumerate(su) if "CfgPub.start(" in l]
    ini = dict((n, [i for i, l in enumerate(su) if (n + ".<init>") in l]) for n in ("EssBenchTick", "EssBenchDropSys", "EssBenchPlaceSys", "EssBenchChunkSys", "EssBackSys", "EssDurDeath"))
    check(len(rs_) == 6 and len(st_) == 1 and max(rs_) < st_[0] and all(len(v) == 1 for v in ini.values())
          and ini["EssBenchChunkSys"][0] > max(ini["EssBenchTick"][0], ini["EssBenchDropSys"][0], ini["EssBenchPlaceSys"][0]),
          "B9: setup registers 6 systems before CfgPub.start; the chunk system (takes the materials out) after the tick / drop / place systems")
    z = zipfile.ZipFile(jar)
    names = z.namelist()
    other = sorted(n for n in names if not n.endswith(".class") and n != "manifest.json")
    kitf = [n for n in other if n.startswith("Common/UI/Custom/SkyyKit/")]
    check(sorted(set(other) - set(kitf)) == ["CREDITS.txt", "Server/Item/ResourceTypes/Compost_Soft.json", "Server/Languages/en-US/server.lang"]
          and len(kitf) == len(T12.SUI.SKY_FILES), "B9: non-class files = CREDITS.txt + the two Compost_Soft files + the kit art (%d)" % len(kitf))
    cls = [n for n in names if n.endswith(".class")]
    check(len(cls) == 97, "B9: 97 classes (0.1.15's 90 + the 7 bench classes): %d" % len(cls))
    print("bench phase done: stripped %d, tagged %d, restored %d" % (EB.STRIPPED.get(), EB.TAGGED.get(), EB.RESTORED.get()))


def compare_jars():
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    short = lambda n: n.rsplit("/", 1)[-1][:-6]
    added = sorted(short(n) for n in set(cb) - set(ca))
    check(added == sorted(NEW) and not (set(ca) - set(cb)), "Z: exactly the 7 bench classes added, none removed: %s" % added)
    changed = sorted(short(n) for n in set(ca) & set(cb) if ca[n] != cb[n])
    allowed = {"TCfg", "SkyyEssentialsPlugin"}
    odd = []
    for n in sorted(set(ca) & set(cb)):
        c = short(n)
        if ca[n] == cb[n] or c in allowed or c.startswith("Cfg"):
            continue
        sa, sb = set(T15.cp_strings(ca[n])), set(T15.cp_strings(cb[n]))
        if set(x.replace(PREV, VERSION) for x in sa - sb) != sb - sa:
            odd.append(c)
    check(not odd, "Z: besides TCfg, the plugin and the config kit classes only the version text changed: %s (changed %s)" % (odd, changed))
    keep = ["TpaCmd", "MsgCmd", "TStore", "TradePage", "HubBar", "EssDur", "EssHome", "EssBackSys", "EssBack", "EssWarp", "EssWIcon", "TBlock", "EssDurDeath"]
    check(all(c not in changed for c in keep), "Z: tpa / msg / trade / homes / back / warps / durability byte-identical: %s" % [c for c in keep if c in changed])
    check("CREDITS.txt" in zb.namelist() and "MIT License" in zb.read("CREDITS.txt").decode("utf8") and "Workbench Tier Keeper" in zb.read("CREDITS.txt").decode("utf8"),
          "Z: CREDITS.txt with the Workbench Tier Keeper MIT notice is in the jar")
    print("Z. class compare %s -> %s: added %s, changed %s" % (PREV, VERSION, added, changed))


PHASES = ("bench", "wicon", "rename", "back", "menu", "main", "trade", "tpa", "chat", "keep", "compost")


def main():
    ph = T11.arg("--phase")
    if "--run" in sys.argv:
        jar = T11.arg("--run")
        if ph == "bench":
            run_bench(jar)
        elif ph == "wicon":
            T14.run_wicon15(jar)
        elif ph == "rename":
            T15.run_rename(jar)
        elif ph == "back":
            T13.run_back(jar)
        elif ph == "menu":
            T12.run_menu(jar)
        elif ph in ("main", "trade", "tpa", "chat", "keep", "compost"):
            getattr(T11, "run_" + ph)(jar)
        else:
            T11.run_live(jar, ph)
        tf = list(T13.FAILS)
        for s_ in T14.SKIPPED:
            print("  superseded:", s_)
        print("%s: %d checks passed, %d failed, %d superseded" % (ph, T14.OKS[0], len(FAILS) + len(tf), len(T14.SKIPPED)))
        for f in FAILS + tf:
            print("  FAILED:", f)
        sys.stdout.flush()
        os._exit(1 if FAILS or tf else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyEssentials/build_skyyessentials_%s.py)" % (JAR, VERSION))
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep), "the scratch folder must be inside tools/dev/scratch/"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = 0
    only = T11.arg("--only")
    for ph in PHASES:
        if only and ph not in only.split(","):
            continue
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
        print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
        rc |= p.returncode
    if not only:
        if os.path.isdir(T11.LIVE):
            dstl = os.path.join(SCRATCH, "live", "mods", "Skyy_SkyyEssentials")
            shutil.copytree(T11.LIVE, dstl)
            for ph in ("live1", "live2"):
                p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
                print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
                rc |= p.returncode
        else:
            print("FAIL no live folder at %s" % T11.LIVE)
            rc |= 1
    compare_jars()
    print("Z: %d checks passed, %d failed" % (T14.OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    rc |= 1 if FAILS else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyEssentials %s bare-JVM check:" % VERSION, "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)


if __name__ == "__main__":
    main()
