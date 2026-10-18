"""Harness for SkyyGear 0.3.20 (tools/gear_0_3_20_patch.py header = SALVAGEBENCH HOOK) = the 0.3.19 harness's children run on the 0.3.20
jar + S320 + H320 (inside the h319 child, after H319, on its stand-in pack), plus a --static phase that needs no jar:
    python tools/gear_0_3_20_patch.py && python SkyyGear/build_skyygear_0.3.20.py
    python SkyyGear/test_skyygear_0.3.20.py [--keep] [--only assets,h319,h318,h317,h316,...]
    python SkyyGear/test_skyygear_0.3.20.py --static [--keep]          (no jars, no Assets.zip, no server jar)

  STATIC (--static)
       G  THE PATCH: tools/gear_0_3_20_patch.py run TWICE into a scratch tree (a copy of the patch + build_skyygear_0.3.19.py + deploy_set.py)
          -> byte-identical outputs, = SkyyGear/build_skyygear_0.3.20.py, compiles as Python, keeps the source's line endings
       A  THE ANCHORS in the generated script: VERSION; G320_CLASSES in the jar class list; the 4 classes made once each; GearBenchSys's
          SystemDependency BEFORE TICK, query ProcessingBenchBlock, the cheap GearPackId.has gate before the bench id; the GearFx.setup
          registration (ordered, unordered GearBenchSysU fallback, SORD); move(): SALV-BEGIN + GearLog.flush BEFORE the input removal,
          the removal BEFORE any write, output written with the filter off, viewers with it on, the put-back, the count check; sweep uses
          GearPack.salvBlocked; registerSystem = 0.3.19's + 2, registerCommand unchanged; the build-time engine asserts are in the script
  S320 the jar 0.3.19 -> 0.3.20: adds exactly GearBench + GearBenchDrop + GearBenchSys + GearBenchSysU, removes nothing, changes only
       manifest.json among the files; the changed classes = S320_MUST (+ at most S320_MAY)
       C  BY CLASS FILE: GearBenchSys (an EntityTickingSystem) references ProcessingBenchBlock.getInputContainer, GearPackId.has,
          GearBench.onBench + isSalv + benchId and SystemDependency; GearBenchSysU extends it; GearBench references GearPack.salvBlocked,
          ItemContainer.setItemStackForSlot + removeItemStackFromSlot, GearLog.flush, BenchBlock.getWindows, Window.getPlayerRef,
          GearStamp.invOf; GearBenchDrop (a Function) ItemComponent.generateItemDrops + Store.addEntities; GearFx holds the
          "BenchSystems$ProcessingBenchTick" name and builds GearBenchSys + GearBenchSysU (0.3.19's GearFx neither)
  H320 (the h319 child, ONE booted engine, H319's stand-in pack RookChestBlack loaded) - real GearBench / GearBenchSys code on stand-ins:
       A  isSalv / benchId; the stand-in output (SimpleItemContainer + ALLOW_OUTPUT_ONLY, like the bench) refuses a filtered write
       B  a dropped piece -> the output slot (same stack, same document), input empty, counted 1 before / after, SN, SALV-BEGIN before
          SALV-BLOCK in gear.log; crafted / undocumented / vanilla-with-a-drop-document stay; three stacks: the two blocked ones move, the
          crafted one stays
       C  output full -> the viewer's inventory (their world's store) + ONE red chat line; a viewer in another store = not used
       D  output full, nobody: the drop Function gets the same stack (on the bench, SN[3]); the drop says no = put back (SN[4], SALV-FAILED);
          the drop throws = UNSURE, never put back (SN[5])
       E  the chat line is rate-limited (5 s; QUIET 0 = every time); part.packDrops=false = nothing moves
       T  the REAL GearBenchSys.tick on a ProcessingBenchBlock (input / output / bench id set by reflection) + a BenchBlock with one window
          (a FakeChunk, the CraftingPlugin singleton stand-in): Salvagebench = moved + the window's player told; a "Furnace" bench / a
          crafted piece = untouched; getQuery = ProcessingBenchBlock's type; the ordered system's one dependency = BEFORE
          BenchSystems$ProcessingBenchTick, the U fallback none
  NOT COVERED (needs the smoke test / Skyy in game): the registration on the live ChunkStore (smoke log: no "could not order the
  Salvagebench guard" WARN), the real bench window, the item entity on the bench, hoppers / mods writing into a bench.
Scratch: tools/dev/scratch/salvhook/h320/gear/harness (full run) and .../h320/static (--static), deleted at the end unless --keep.
Exit code 1 on any failure (--static: 0 = PASS).
"""
import os, sys, json, shutil, zipfile, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
STATIC = "--static" in sys.argv
if STATIC:
    sys.dont_write_bytecode = True


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.20"
V319 = "0.3.19"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "salvhook", "h320")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J319 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V319))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_20_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.20.py")
GEN319 = os.path.join(HERE, "build_skyygear_0.3.19.py")

S320_NEW = {"GearBench": "the sweep: a dropped / identified pack piece out of a Salvagebench input (output -> viewer -> on the bench)",
            "GearBenchDrop": "one stack as an item entity on the bench (generateItemDrops + addEntities, vanilla's ejectItems way)",
            "GearBenchSys": "ChunkStore EntityTickingSystem on ProcessingBenchBlock, BEFORE BenchSystems$ProcessingBenchTick",
            "GearBenchSysU": "its unordered fallback (constructor only)"}
S320_MUST = {"GearPool": "SN / SORD + the /gear loot guard line (packText)",
             "GearFx": "setup registers GearBenchSys (ordered) / GearBenchSysU"}
S320_MAY = {"SkyyGearPlugin": "the version text in the ready line", "CfgFn": "config kit: the version", "CfgRows": "config kit: the version",
            "GearCfg": "the version text", "CfgDefaults": "config kit", "CfgKit": "config kit", "CfgPub": "config kit", "CfgFile": "config kit"}
TICK = "com.hypixel.hytale.builtin.crafting.system.BenchSystems$ProcessingBenchTick"

# ---- the 0.3.19 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
if not STATIC:
    _H319 = os.path.join(HERE, "test_skyygear_0.3.19.py")
    _T319 = open(_H319, encoding="utf-8").read()
    _cut = _T319.rindex('if __name__ == "__main__":')
    _argv = sys.argv
    sys.argv = [_H319, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
        (["--only", arg("--only")] if arg("--only") else [])
    H319 = {"__name__": "skyygear_h319", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T319[:_cut], _H319 + " (library)", "exec"), H319)
    sys.argv = _argv
    H319["VERSION"] = VERSION
    H318 = H319["H318"]
    H318["VERSION"] = VERSION
    H318["H317"]["VERSION"] = VERSION
    H316 = H319["H316"]
    H316["VERSION"] = VERSION
    FAKE_PKG = H319["FAKE_PKG"]
    cpool, has_ref = H319["cpool"], H319["has_ref"]
    FAILS, OKS = H316["FAILS"], H316["OKS"]
else:
    FAILS, OKS = [], [0]


def check(cond, what):
    if STATIC:
        if cond:
            OKS[0] += 1
        else:
            FAILS.append(what)
            print("FAIL", what)
        return
    H316["check"](cond, what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S320
def run_assets320():
    ea, eb = entries(J319), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(added == sorted("com/skyy/gear/%s.class" % c for c in S320_NEW) and not gone and changed == ["manifest.json"],
          "S320: 0.3.19 -> 0.3.20 adds GearBench + GearBenchDrop + GearBenchSys + GearBenchSysU, removes nothing, changes only manifest.json among "
          "the files: added %s, gone %s, changed %s" % (added[:6], gone[:4], changed))
    man = eb.get("manifest.json", b"").decode("utf-8", "replace")
    check('"0.3.20"' in man, "S320: the manifest says 0.3.20")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.19 -> 0.3.20: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S320_MUST) | set(S320_MAY), "S320: only GearPool / GearFx (+ version text) changed: unexpected %s"
          % sorted(set(chg) - set(S320_MUST) - set(S320_MAY)))
    check(set(S320_MUST) <= set(chg), "S320: every class the patch edits really changed: unchanged %s" % sorted(set(S320_MUST) - set(chg)))
    try:
        cs = cpool(eb["com/skyy/gear/GearBenchSys.class"])
        cu = cpool(eb["com/skyy/gear/GearBenchSysU.class"])
        cg = cpool(eb["com/skyy/gear/GearBench.class"])
        cd = cpool(eb["com/skyy/gear/GearBenchDrop.class"])
        cf = cpool(eb["com/skyy/gear/GearFx.class"])
        cf0 = cpool(ea["com/skyy/gear/GearFx.class"])
    except Exception as e:
        check(False, "S320 C: the class files could not be read: %s" % e)
        return
    check("com/hypixel/hytale/component/system/tick/EntityTickingSystem" in cs["class"]
          and has_ref(cs, "M", "/ProcessingBenchBlock", "getInputContainer") and has_ref(cs, "M", "/ProcessingBenchBlock", "getComponentType")
          and has_ref(cs, "M", "com/skyy/gear/GearPackId", "has") and has_ref(cs, "M", "com/skyy/gear/GearBench", "onBench")
          and has_ref(cs, "M", "com/skyy/gear/GearBench", "isSalv") and has_ref(cs, "M", "com/skyy/gear/GearBench", "benchId")
          and has_ref(cs, "M", "/SystemDependency", "<init>"),
          "S320 C: GearBenchSys (an EntityTickingSystem) reads ProcessingBenchBlock.getInputContainer, gates on GearPackId.has, then "
          "GearBench.isSalv(benchId) -> onBench; it builds a SystemDependency")
    check("com/skyy/gear/GearBenchSys" in cu["class"] and has_ref(cu, "M", "com/skyy/gear/GearBenchSys", "<init>"),
          "S320 C: GearBenchSysU is the GearBenchSys(false) fallback")
    check(has_ref(cg, "M", "com/skyy/gear/GearPack", "salvBlocked") and has_ref(cg, "M", "/ItemContainer", "setItemStackForSlot")
          and has_ref(cg, "M", "/ItemContainer", "removeItemStackFromSlot") and has_ref(cg, "M", "com/skyy/gear/GearLog", "flush")
          and has_ref(cg, "M", "/BenchBlock", "getWindows") and has_ref(cg, "M", "/Window", "getPlayerRef")
          and has_ref(cg, "M", "com/skyy/gear/GearStamp", "invOf") and has_ref(cg, "M", "com/skyy/gear/GearBenchDrop", "<init>")
          and "Salvagebench" in cg["str"],
          "S320 C: GearBench uses GearPack.salvBlocked, ItemContainer.setItemStackForSlot + removeItemStackFromSlot, GearLog.flush, "
          "BenchBlock.getWindows -> Window.getPlayerRef, GearStamp.invOf, GearBenchDrop; holds 'Salvagebench'")
    check("java/util/function/Function" in cd["class"] and has_ref(cd, "M", "/ItemComponent", "generateItemDrops")
          and has_ref(cd, "M", "com/hypixel/hytale/component/Store", "addEntities"),
          "S320 C: GearBenchDrop (a Function) = ItemComponent.generateItemDrops + Store.addEntities")
    check(TICK in cf["str"] and has_ref(cf, "M", "com/skyy/gear/GearBenchSys", "<init>") and has_ref(cf, "M", "com/skyy/gear/GearBenchSysU", "<init>")
          and TICK not in cf0["str"] and not has_ref(cf0, "M", "com/skyy/gear/GearBenchSys", "<init>"),
          "S320 C: GearFx.setup names BenchSystems$ProcessingBenchTick and builds GearBenchSys + GearBenchSysU (0.3.19's did neither)")


# ====================================================================================================== H320 (in the h319 child)
def _h320(L, K):
    from jpype import JClass, JInt, JShort, JFloat, JString, JArray, JImplements, JOverride
    P = lambda n: JClass(PKG + n)
    GB, GBS, GBSU, GPI, Pool, Data, Roll = P("GearBench"), P("GearBenchSys"), P("GearBenchSysU"), P("GearPackId"), P("GearPool"), L["Data"], L["Roll"]
    ISj = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    FT = JClass("com.hypixel.hytale.server.core.inventory.container.filter.FilterType")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    ITEM, PR1, U1, logs, jf, us, apply = L["ITEM"], L["PR1"], L["U1"], L["logs"], L["jf"], L["us"], L["apply"]
    FS = JClass(FAKE_PKG + ".FakeStore")
    PRA = JArray(PRc)
    RC, VAN = "RookChestBlack", "Armor_Iron_Chest"

    def kc(cond, what):
        K.check(bool(cond), "H320 " + what)

    def cfg(**kv):
        apply(**kv)
        Pool.TAB = None
    cfg()
    try:
        live = bool(GPI.has(RC)) and ITEM.getAssetMap().getAsset(RC) is not None
    except Exception:
        live = False
    kc(live, "setup: H319's stand-in pack id %s is live (a table id with a vanilla Parent)" % RC)
    if not live:
        return

    def blk(src="drop", i=RC):
        return Data.put(ISj(i, JInt(1)), Roll.newDoc(i, JInt(0), True, src), None)

    def cont(n, out=False):
        c_ = SIC(JShort(n))
        if out:
            c_.setGlobalFilter(FT.ALLOW_OUTPUT_ONLY)
        return c_

    def put(c_, k_, s_):
        c_.setItemStackForSlot(JShort(k_), s_, False)
        return c_

    def at(c_, k_):
        return c_.getItemStack(JShort(k_))

    def empty(c_, k_):
        x_ = at(c_, k_)
        return x_ is None or bool(x_.isEmpty())

    def cnt(cs_, i_):
        n_ = 0
        for c_ in cs_:
            for k_ in range(int(c_.getCapacity())):
                x_ = at(c_, k_)
                if x_ is not None and not x_.isEmpty() and str(x_.getItemId()) == i_:
                    n_ += int(x_.getQuantity())
        return n_

    def sn():
        return [int(x_) for x_ in Pool.SN]

    def dsn(a_, b_):
        return [y_ - x_ for x_, y_ in zip(a_, b_)]

    def docj(s_):
        d_ = Data.gearDoc(s_.getMetadata())
        return None if d_ is None else str(d_.toJson())

    def said():
        return L["said"](PR1)

    def stand_ins():
        """Norm (stores new ItemStack(id, qty) - the metadata dropped), Keep (Norm + refuses removal while keep), Throw (getItemStack
        throws while boom), Refuse (setItemStackForSlot throws while refuse): compiled with javassist into the scratch folder, loaded
        by their own class loader whose parent is SimpleItemContainer's"""
        try:
            CP, CtNM, CtNC, CtF = (JClass("javassist.ClassPool"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"),
                                   JClass("javassist.CtField"))
            d_ = os.path.join(SCRATCH, "fake320")
            os.makedirs(d_, exist_ok=True)
            cp_ = CP(True)
            cp_.appendClassPath(JClass("javassist.LoaderClassPath")(SIC.class_.getClassLoader()))
            IS_, SLT = "com.hypixel.hytale.server.core.inventory.ItemStack", "com.hypixel.hytale.server.core.inventory.transaction"
            src = {"Norm": ("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer", [],
                            ["public %s.ItemStackSlotTransaction setItemStackForSlot(short s, %s i, boolean f) { return super.setItemStackForSlot(s, i == null ? null : new %s(i.getItemId(), i.getQuantity()), f); }" % (SLT, IS_, IS_)]),
                   "Keep": ("skyyh320.Norm", ["public boolean keep;"],
                            ["public %s.SlotTransaction removeItemStackFromSlot(short s, boolean f) { if (this.keep) return null; return super.removeItemStackFromSlot(s, f); }" % SLT]),
                   "Throw": ("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer", ["public boolean boom;"],
                             ["public %s getItemStack(short s) { if (this.boom) throw new java.lang.IllegalStateException(\"test: the container throws\"); return super.getItemStack(s); }" % IS_]),
                   "Refuse": ("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer", ["public boolean refuse;"],
                              ["public %s.ItemStackSlotTransaction setItemStackForSlot(short s, %s i, boolean f) { if (this.refuse) throw new java.lang.IllegalStateException(\"test: the slot refuses\"); return super.setItemStackForSlot(s, i, f); }" % (SLT, IS_)])}
            for nm_ in ("Norm", "Keep", "Throw", "Refuse"):
                sup_, fs_, ms_ = src[nm_]
                c_ = cp_.makeClass("skyyh320." + nm_)
                c_.setSuperclass(cp_.get(sup_))
                for f_ in fs_:
                    c_.addField(CtF.make(f_, c_))
                c_.addConstructor(CtNC.make("public %s(short n) { super(n); }" % nm_, c_))
                for m_ in ms_:
                    c_.addMethod(CtNM.make(m_, c_))
                c_.writeFile(d_)
            URL = JClass("java.net.URLClassLoader")
            ucl = URL(JArray(JClass("java.net.URL"))([JClass("java.io.File")(d_).toURI().toURL()]), SIC.class_.getClassLoader())
            return tuple(JClass("skyyh320." + nm_, loader=ucl) for nm_ in ("Norm", "Keep", "Throw", "Refuse"))
        except Exception as e_:
            K.notes.append("H320 M: stand-ins failed: %s" % str(e_)[:600])
            return None

    def full4():
        o_ = cont(4, True)
        for k_ in range(4):
            put(o_, k_, ISj(VAN, JInt(1)))
        return o_
    NOV = PRA(0)

    # ============================================================== A
    kc(bool(GB.isSalv("Salvagebench")) and not bool(GB.isSalv("salvagebench")) and not bool(GB.isSalv("Furnace")) and not bool(GB.isSalv(None))
       and GB.benchId(None) is None and str(GB.BENCH) == "Salvagebench" and int(GB.QUIET) == 5000 and int(GB.COOLMS) == 5000,
       "A: isSalv = exactly the engine id Salvagebench (critic L7), nothing else; benchId(null) null; QUIET + COOLMS 5 s")
    GB.COOL.clear()
    o_ = cont(4, True)
    try:
        o_.setItemStackForSlot(JShort(0), blk())
    except Exception:
        pass
    kc(empty(o_, 0), "A: the stand-in output (ALLOW_OUTPUT_ONLY, like the bench's) refuses a filtered write - the bypass matters")

    # ============================================================== B: output
    s1 = blk()
    d1 = docj(s1)
    in1, out1 = put(cont(1), 0, s1), cont(4, True)
    b0 = cnt([in1, out1], RC)
    n0 = sn()
    logs()
    n = int(GB.sweep(in1, out1, NOV, None, None, "test-b"))
    lg = logs()
    ib = [k_ for k_, x_ in enumerate(lg) if "SALV-BEGIN test-b RookChestBlack x1 (nobody)" in x_]
    ik = [k_ for k_, x_ in enumerate(lg) if "SALV-BLOCK output test-b RookChestBlack x1 (nobody)" in x_]
    kc(n == 1 and empty(in1, 0) and bool(GB.sameAt(out1, JInt(0), s1)) and docj(at(out1, 0)) == d1 and '"drop"' in (d1 or "")
       and b0 == 1 and cnt([in1, out1], RC) == 1 and dsn(n0, sn())[:2] == [1, 1],
       "B: a dropped RookChestBlack leaves the input into output slot 0 - the same stack and document, counted 1 before / after, SN[0] / SN[1] +1 "
       "(sweep %d, SN %s)" % (n, dsn(n0, sn())))
    kc(ib and ik and ib[0] < ik[0] and d1 in lg[ik[0]], "B: gear.log: SALV-BEGIN, then SALV-BLOCK output with the document: %s" % lg[-2:])
    sc, sp, sv = blk("craft"), ISj(RC, JInt(1)), blk("drop", VAN)
    in2, out2 = cont(3), cont(4, True)
    for k_, x_ in enumerate((sc, sp, sv)):
        put(in2, k_, x_)
    n = int(GB.sweep(in2, out2, NOV, None, None, "test-b2"))
    kc(n == 0 and all(bool(GB.sameAt(in2, JInt(k_), x_)) for k_, x_ in enumerate((sc, sp, sv))) and int(GB.emptySlot(out2)) == 0,
       "B: a crafted RookChestBlack, an undocumented one and a vanilla Armor_Iron_Chest with a drop document all stay in the input")
    s3a, s3b = blk("drop"), blk("chest")
    in3, out3 = cont(3), cont(4, True)
    put(in3, 0, s3a)
    put(in3, 1, sc)
    put(in3, 2, s3b)
    n = int(GB.sweep(in3, out3, NOV, None, None, "test-b3"))
    kc(n == 2 and empty(in3, 0) and empty(in3, 2) and bool(GB.sameAt(in3, JInt(1), sc)) and bool(GB.sameAt(out3, JInt(0), s3a))
       and bool(GB.sameAt(out3, JInt(1), s3b)) and cnt([in3, out3], RC) == 3,
       "B: three input stacks: the dropped + the chest one move (output 0, 1), the crafted one stays; 3 counted")

    # ============================================================== C: output full -> the viewer's inventory
    old_ent = jf(PRc, "entity").get(PR1)
    try:
        inv7, cs7 = L["mkinv"]()
        ref7, st7, _ch7, _pl7 = L["world"](inv7, cs7, PR1)
        jf(PRc, "entity").set(PR1, ref7)
        GB.SAID.clear()
        s4 = blk()
        in4, out4 = put(cont(1), 0, s4), full4()
        q0 = len(said())
        n0 = sn()
        n = int(GB.sweep(in4, out4, PRA([PR1]), st7, None, "test-c"))
        new = said()[q0:]
        kc(n == 1 and empty(in4, 0) and L["ids"](cs7).get(RC) == 1 and cnt([in4, out4], VAN) == 4 and dsn(n0, sn())[2] == 1
           and len(new) == 1 and "salvage it with Requip's SALVAGE button, not at a Salvagebench" in new[0] and "went back into your inventory" in new[0],
           "C: output full -> the viewer's inventory (storage), SN[2] +1, ONE chat line pointing to Requip SALVAGE: %s" % new)
        lgc = logs()
        kc([x_ for x_ in lgc if "SALV-BLOCK inventory test-c RookChestBlack x1 (Tester)" in x_], "C: gear.log SALV-BLOCK inventory ... (Tester): %s" % lgc[-1:])
        # a viewer whose Ref lives in another store (another world) is not used; nothing else takes it -> back in the input
        other = us.allocateInstance(FS.class_)
        s5 = blk()
        in5, out5 = put(cont(1), 0, s5), full4()
        n0 = sn()
        n = int(GB.sweep(in5, out5, PRA([PR1]), other, None, "test-c2"))
        lg5 = logs()
        kc(n == 0 and bool(GB.sameAt(in5, JInt(0), s5)) and L["ids"](cs7).get(RC) == 1 and dsn(n0, sn())[4] == 1
           and [x_ for x_ in lg5 if "SALV-FAILED test-c2 RookChestBlack x1 - nowhere to put it, back in the input" in x_],
           "C: a viewer in another store is not used; no drop -> put back into the input (SN[4], SALV-FAILED): %s" % lg5[-1:])

        # ============================================================== D: on the bench (the drop Function)
        got = []

        @JImplements("java.util.function.Function")
        class Drop(object):
            def __init__(self, mode):
                self.mode = mode

            @JOverride
            def apply(self, o):
                got.append(o)
                if self.mode == "throw":
                    raise RuntimeError("test: the drop failed")
                return self.mode == "yes"
        GB.SAID.clear()
        s6 = blk()
        in6, out6 = put(cont(1), 0, s6), full4()
        q0 = len(said())
        n0 = sn()
        n = int(GB.sweep(in6, out6, PRA([PR1]), other, Drop("yes"), "test-d"))
        new = said()[q0:]
        kc(n == 1 and empty(in6, 0) and len(got) == 1 and str(got[0].getItemId()) == RC and docj(got[0]) == docj(s6)
           and cnt([in6, out6], RC) == 0 and dsn(n0, sn())[3] == 1 and len(new) == 1 and "it lies on the bench" in new[0],
           "D: output + inventory full -> the drop Function gets the same stack (SN[3]), the viewer is told 'it lies on the bench': %s" % new)
        lg6 = logs()
        kc([x_ for x_ in lg6 if "SALV-BLOCK ground test-d RookChestBlack" in x_] and not [x_ for x_ in lg6 if "SALV-COUNT" in x_],
           "D: gear.log SALV-BLOCK ground, no count mismatch (1 less in the bench = the dropped one): %s" % lg6[-1:])
        s7 = blk()
        in7, out7 = put(cont(1), 0, s7), full4()
        n0 = sn()
        n = int(GB.sweep(in7, out7, NOV, None, Drop("no"), "test-d2"))
        kc(n == 0 and bool(GB.sameAt(in7, JInt(0), s7)) and dsn(n0, sn())[4] == 1, "D: the drop says no -> put back into the input (SN[4])")
        logs()
        s8 = blk()
        in8, out8 = put(cont(1), 0, s8), full4()
        n0 = sn()
        n = int(GB.sweep(in8, out8, NOV, None, Drop("throw"), "test-d3"))
        lg8 = logs()
        kc(n == 1 and empty(in8, 0) and dsn(n0, sn())[5] == 1 and [x_ for x_ in lg8 if "SALV-UNSURE test-d3 RookChestBlack x1" in x_],
           "D: a drop that throws = UNSURE: never put back (no second copy), SN[5], SALV-UNSURE with the document: %s" % lg8[-1:])

        # ============================================================== E: rate limit, part.packDrops off
        GB.SAID.clear()
        q0 = len(said())
        for k_ in range(2):
            GB.sweep(put(cont(1), 0, blk()), cont(4, True), PRA([PR1]), st7, None, "test-e")
        q1 = len(said())
        GB.QUIET = 0
        GB.sweep(put(cont(1), 0, blk()), cont(4, True), PRA([PR1]), st7, None, "test-e")
        q2 = len(said())
        GB.QUIET = 5000
        kc(q1 - q0 == 1 and q2 - q1 == 1, "E: two pieces within 5 s = ONE chat line; QUIET 0 = a line each time (%d, %d)" % (q1 - q0, q2 - q1))
        cfg(part__packDrops="false")
        s9 = blk()
        in9 = put(cont(1), 0, s9)
        n = int(GB.sweep(in9, cont(4, True), NOV, None, None, "test-e2"))
        cfg()
        kc(n == 0 and bool(GB.sameAt(in9, JInt(0), s9)), "E: part.packDrops=false = plain items, nothing moves")
        logs()

        # ============================================================== M: the critic fixes on container stand-ins (compiled now, scratch)
        SC = stand_ins()
        if SC is None:
            kc(False, "M setup: the container stand-ins (Norm / Keep / Throw / Refuse) could not be compiled")
        else:
            Norm, Keep, Throw, Refuse = SC

            def sc(Cls, n_):
                return Cls(JShort(n_))
            # M1: a container that stores a changed (normalised) copy - the copy is taken out again, the next target gets the ONE stack
            nc = sc(Norm, 4)
            sM = blk()
            kc(int(GB.tryPut(nc, JInt(0), sM, False)) == 0 and empty(nc, 0), "M1: tryPut into a normalising container = 0 and the changed copy is taken out again")
            inA, outA = put(cont(1), 0, sM), sc(Norm, 4)
            inv7b, cs7b = L["mkinv"]()
            ref7b, st7b, _c, _p = L["world"](inv7b, cs7b, PR1)
            jf(PRc, "entity").set(PR1, ref7b)
            n = int(GB.sweep(inA, outA, PRA([PR1]), st7b, None, "test-m1"))
            kc(n == 1 and empty(inA, 0) and int(GB.emptySlot(outA)) == 0 and L["ids"](cs7b).get(RC) == 1
               and cnt([inA, outA], RC) + L["ids"](cs7b).get(RC, 0) == 1,
               "M1: output normalises -> nothing stays there, the viewer gets the ONE copy (never two)")
            lgA = logs()
            kc([x_ for x_ in lgA if "SALV-UNDO RookChestBlack" in x_], "M1: gear.log SALV-UNDO: %s" % lgA[-3:])
            sB = blk()
            inB, outB = put(cont(1), 0, sB), sc(Norm, 4)
            n = int(GB.sweep(inB, outB, NOV, None, None, "test-m1b"))
            kc(n == 0 and bool(GB.sameAt(inB, JInt(0), sB)) and docj(at(inB, 0)) == docj(sB) and int(GB.emptySlot(outB)) == 0,
               "M1: output normalises, nobody to take it -> back in the input with its document, the output empty (one copy)")
            kp = sc(Keep, 4)
            jf(Keep, "keep").setBoolean(kp, True)
            sK = blk()
            inK = put(cont(1), 0, sK)
            n0 = sn()
            n = int(GB.sweep(inK, kp, NOV, None, None, "test-m1c"))
            lgK = logs()
            kc(n == 1 and empty(inK, 0) and cnt([inK, kp], RC) == 1 and dsn(n0, sn())[5] == 1 and [x_ for x_ in lgK if "SALV-UNSURE test-m1c RookChestBlack" in x_],
               "M1: a changed copy that cannot be taken back out = UNSURE, the move stops there: exactly ONE copy, never put back (SN[5]): %s" % lgK[-1:])
            # M2: a container that throws while being read is no target; nothing landed -> put back; the input refusing too -> SALV-LOST
            th = sc(Throw, 4)
            jf(Throw, "boom").setBoolean(th, True)
            sT2 = blk()
            inT2 = put(cont(1), 0, sT2)
            n0 = sn()
            n = int(GB.sweep(inT2, th, NOV, None, None, "test-m2"))
            lgT2 = logs()
            kc(n == 0 and bool(GB.sameAt(inT2, JInt(0), sT2)) and dsn(n0, sn())[4] == 1
               and [x_ for x_ in lgT2 if "SALV-FAILED test-m2 RookChestBlack x1 - nowhere to put it, back in the input" in x_],
               "M2: the output throws on every read -> the piece is back in the input (SN[4], SALV-FAILED): %s" % lgT2[-1:])
            n0 = sn()
            n = int(GB.sweep(inT2, th, NOV, None, None, "test-m2"))
            kc(n == 0 and dsn(n0, sn())[0] == 0 and bool(GB.sameAt(inT2, JInt(0), sT2)) and not [x_ for x_ in logs() if "test-m2" in x_],
               "L3: the same bench right after a put-back rests (COOLMS): not even looked at, no SALV line")
            GB.COOL.clear()
            n = int(GB.sweep(inT2, th, NOV, None, None, "test-m2"))
            kc(n == 0 and dsn(n0, sn())[0] == 1, "L3: after the rest the bench is tried again")
            logs()
            rf = sc(Refuse, 1)
            sR = blk()
            put(rf, 0, sR)
            jf(Refuse, "refuse").setBoolean(rf, True)
            n0 = sn()
            n = int(GB.sweep(rf, th, NOV, None, None, "test-m2b"))
            lgR = logs()
            kc(n == 0 and empty(rf, 0) and dsn(n0, sn())[5] == 1 and [x_ for x_ in lgR if "SALV-LOST test-m2b RookChestBlack x1" in x_ and docj(sR) in x_],
               "M2: output throws AND the input refuses it back -> SALV-LOST with the full document in gear.log (SN[5]): %s" % lgR[-1:])
            GB.COOL.clear()

        # ============================================================== T: the real GearBenchSys.tick
        HM, IHM = JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap")
        FU, FCh = JClass(FAKE_PKG + ".FakeUtil"), JClass(FAKE_PKG + ".FakeChunk")
        PBB = JClass("com.hypixel.hytale.builtin.crafting.component.ProcessingBenchBlock")
        BBK = JClass("com.hypixel.hytale.builtin.crafting.component.BenchBlock")
        PBN = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench")
        BNC = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench")
        PBW = JClass("com.hypixel.hytale.builtin.crafting.window.ProcessingBenchWindow")
        WIN = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window")
        FU.single("com.hypixel.hytale.builtin.crafting.CraftingPlugin")
        ctp, ctb = PBB.getComponentType(), BBK.getComponentType()
        kc(ctp is not None and ctb is not None, "T setup: the CraftingPlugin stand-in gives ProcessingBenchBlock / BenchBlock types")

        def bench(bid, s_):
            pb_ = PBB()
            in_, out_ = put(cont(1), 0, s_), cont(4, True)
            jf(PBB, "inputContainer").set(pb_, in_)
            jf(PBB, "outputContainer").set(pb_, out_)
            bn_ = us.allocateInstance(PBN.class_)
            jf(BNC, "id").set(bn_, JString(bid))
            jf(PBB, "bench").set(pb_, bn_)
            bb_ = BBK()
            if bb_.getWindows() is None:
                jf(BBK, "windows").set(bb_, HM())
            w_ = us.allocateInstance(PBW.class_)
            jf(WIN, "playerRef").set(w_, PR1)
            bb_.getWindows().put(U1, w_)
            ch_ = us.allocateInstance(FCh.class_)
            m_ = IHM()
            m_.put(ctp, pb_)
            m_.put(ctb, bb_)
            jf(FCh, "comps").set(ch_, m_)
            return pb_, in_, out_, ch_
        GBS.TICK = JClass(TICK).class_
        so, su = GBS(True), GBSU()
        dl = list(so.getDependencies())
        kc(len(dl) == 1 and str(dl[0].getOrder()) == "BEFORE" and dl[0].getSystemClass() == JClass(TICK).class_ and su.getDependencies().isEmpty()
           and so.getQuery() == ctp and not bool(so.isParallel(JInt(64), JInt(4))),
           "T: GearBenchSys(true) = ONE SystemDependency BEFORE BenchSystems$ProcessingBenchTick, GearBenchSysU none; query = ProcessingBenchBlock; never parallel: %s" % [str(x_) for x_ in dl])
        st0 = us.allocateInstance(FS.class_)
        GB.SAID.clear()
        sT = blk()
        pbT, inT, outT, chT = bench("Salvagebench", sT)
        kc(len(GB.viewers(chT.getComponent(JInt(0), ctb))) == 1, "T: viewers = the one window's player")
        q0 = len(said())
        so.tick(JFloat(0.05), JInt(0), chT, st0, None)
        new = said()[q0:]
        lgT = logs()
        kc(empty(inT, 0) and bool(GB.sameAt(outT, JInt(0), sT)) and len(new) == 1 and "Requip's SALVAGE button" in new[0]
           and [x_ for x_ in lgT if "SALV-BLOCK output ? ? RookChestBlack x1 (Tester)" in x_],
           "T: the real tick on a Salvagebench: the dropped piece -> output, the window's player told, logged (no world here = '? ?'): %s %s" % (new, lgT[-1:]))
        sF = blk()
        _pb, inF, outF, chF = bench("Furnace", sF)
        so.tick(JFloat(0.05), JInt(0), chF, st0, None)
        sC = blk("craft")
        _pb, inC, outC, chC = bench("Salvagebench", sC)
        su.tick(JFloat(0.05), JInt(0), chC, st0, None)
        kc(bool(GB.sameAt(inF, JInt(0), sF)) and int(GB.emptySlot(outF)) == 0 and bool(GB.sameAt(inC, JInt(0), sC)) and int(GB.emptySlot(outC)) == 0,
           "T: a 'Furnace' Processing bench and a crafted piece on a Salvagebench (GearBenchSysU) are untouched")
        K.notes.append("H320 guard counters after the phase: %s" % sn())
    finally:
        jf(PRc, "entity").set(PR1, old_ent)
        GB.SAID.clear()
        GB.QUIET = 5000
        cfg()


if not STATIC:
    _h319_orig = H319["_h319"]

    def _h319_and_h320(L, K):
        _h319_orig(L, K)
        try:
            _h320(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H320: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_and_h320


# ---- old library jars (tools/tidy_local.py packs every jar a harness names only through "%s" into backups/archive/old-jars-*.tar.xz)
def archived(src, dest):
    """a read-only copy of a packed jar (its newest archive copy) into the scratch folder; None = not in any archive"""
    import tarfile, glob as _g
    rel = os.path.relpath(src, ROOT).replace(os.sep, "/")
    for f in sorted(_g.glob(os.path.join(ROOT, "backups", "archive", "old-jars-*.tar.xz")), key=os.path.getmtime, reverse=True):
        try:
            with tarfile.open(f) as t:
                if rel in t.getnames():
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with open(dest, "wb") as o:
                        o.write(t.extractfile(rel).read())
                    return dest
        except Exception:
            continue
    return None


def missing_lib_jars():
    """every absolute *.jar path the loaded harness libraries name that is not on disk (the full chain asserts on them)"""
    seen, out = set(), set()

    def walk(ns):
        if id(ns) in seen:
            return
        seen.add(id(ns))
        for k, v in list(ns.items()):
            if isinstance(v, str) and v.endswith(".jar") and os.path.isabs(v) and v.startswith(ROOT) and os.sep + "SkyyGear" + os.sep in v \
                    and SCR_BASE not in v and not os.path.isfile(v):
                out.add(v)
            elif isinstance(v, dict) and "__builtins__" in v:
                walk(v)
    if not STATIC:
        walk(H319)
    return sorted(out)


if not STATIC and not os.path.isfile(H319.get("FI7_SRC", "")):          # the h319 child copies SkyyFishing-0.1.7.jar itself
    _fi7 = archived(H319["FI7_SRC"], os.path.join(SCR_BASE, "lib", os.path.basename(H319["FI7_SRC"])))
    if _fi7:
        H319["FI7_SRC"] = _fi7


def run_fallback(want, skipped):
    """S320 + the h319 / h320 child without the older chain (some old SkyyGear library jars are not on disk)"""
    H35, H36 = H316["H35"], H316["H36"]
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    for src_, dst_ in ((H35["CO_SRC"], H36["CO_JAR"]), (H36["FI6_SRC"], H36["FI_JAR"])):
        if os.path.isfile(src_):
            shutil.copyfile(src_, dst_)
        elif not archived(src_, dst_):
            check(False, "fallback: %s is neither on disk nor in backups/archive" % os.path.basename(src_))
    import glob as _g
    for f_ in _g.glob(os.path.join(H35["LIVE_PLAYERS"], "*.json")):
        shutil.copyfile(f_, os.path.join(SCRATCH, "players", os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    try:
        if want("assets"):
            run_assets320()
        p = H316["child"](env, "--mkfake", H316["FAKE_DIR"])
        check(p.returncode == 0, "F: the stand-ins were generated")
        if want("h319"):
            out = os.path.join(SCRATCH, "h319.json")
            pr = H316["child"](env, "--h319", "--out", out)
            check(pr.returncode == 0, "h319+h320: the child exited cleanly (%s)" % pr.returncode)
            H316["take"](out, "h319")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
            shutil.rmtree(os.path.join(SCR_BASE, "lib"), ignore_errors=True)
    print("SkyyGear %s harness (FALLBACK: assets + h319/h320 only): %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    if skipped:
        print("SKIPPED the older phases (h318 .. h30): %d old SkyyGear library jar(s) are not on disk, e.g. %s - tools/tidy_local.py packed them into "
              "backups/archive/old-jars-*.tar.xz; put them back for a full run" % (len(skipped), ", ".join(os.path.basename(x) for x in skipped[:4])))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else (3 if skipped and not arg("--only") else 0))


# ====================================================================================================== STATIC (no jars)
def run_static():
    base = os.path.join(SCR_BASE, "static")
    shutil.rmtree(base, ignore_errors=True)
    outs = []
    try:
        for k in range(2):
            r = os.path.join(base, "run%d" % k)
            os.makedirs(os.path.join(r, "tools"))
            os.makedirs(os.path.join(r, "SkyyGear"))
            shutil.copyfile(PATCH, os.path.join(r, "tools", os.path.basename(PATCH)))
            shutil.copyfile(os.path.join(TOOLS, "deploy_set.py"), os.path.join(r, "tools", "deploy_set.py"))
            shutil.copyfile(GEN319, os.path.join(r, "SkyyGear", os.path.basename(GEN319)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.20.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.20.py (the committed file is the patch's output)")
        src = open(GEN319, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.20.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        # A: anchors
        check('VERSION = "0.3.20"\n' in s and "GENERATED by tools/gear_0_3_20_patch.py" in s, "A: VERSION 0.3.20 + the GENERATED header")
        check("+ G318_CLASSES + G319_CLASSES + G320_CLASSES" in s and "G320_CLASSES = [gbench, gbdrop, gbsys, gbsysU]" in s,
              "A: G320_CLASSES (GearBench, GearBenchDrop, GearBenchSys, GearBenchSysU) in the jar class list")
        for c_ in ("GearBench", "GearBenchDrop", "GearBenchSys", "GearBenchSysU"):
            check(len(re.findall(r'= mk\("%s"' % c_, s)) == 1, "A: %s made once" % c_)
        check(s.count("registerSystem(") == s0.count("registerSystem(") + 2 and s.count("registerCommand(") == s0.count("registerCommand("),
              "A: registerSystem = 0.3.19's + 2 (ordered + fallback), registerCommand unchanged")
        i_t = s.index("public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {\n  try {\n    @PBBK@")
        tb = s[i_t:s.index('}""")', i_t)]
        check(tb.index("@PKG@.GearPackId.has(s.getItemId())") < tb.index("@PKG@.GearBench.isSalv(@PKG@.GearBench.benchId(pb))") < tb.index("@PKG@.GearBench.onBench("),
              "A: the tick gates on GearPackId.has (input stacks) before reading the bench id, then onBench")
        check("this.deps.add(new @SDEP@(@ORD@.BEFORE, TICK));" in s and "this.query = (@QRY@) @PBBK@.getComponentType();" in s
              and 'gbsysU = mk("GearBenchSysU", PKG + ".GearBenchSys")' in s and 'C(gbsysU, "public GearBenchSysU() { super(false); }")' in s,
              "A: GearBenchSys: BEFORE TICK, query ProcessingBenchBlock; GearBenchSysU = super(false)")
        i_s = s.index('Class sbt = cls("com.hypixel.hytale.builtin.crafting.system.BenchSystems$ProcessingBenchTick");')
        sb = s[i_s:i_s + 1400]
        check(sb.index("new @PKG@.GearBenchSys(true)") < sb.index("@PKG@.GearPool.SORD = 1;") < sb.index("new @PKG@.GearBenchSysU()") < sb.index("@PKG@.GearPool.SORD = 2;")
              and s.index("@PKG@.GearChestTagU()") < i_s < s.index("new @PKG@.GearFxInvSys()"),
              "A: GearFx.setup: ordered first (SORD 1), the unordered fallback + WARN (SORD 2), next to the other ChunkStore systems")
        i_m = s.index("public static String move(@IC@ in, int i")
        mb = s[i_m:s.index('}""")', i_m)]
        check(mb.index('"SALV-BEGIN "') < mb.index("@PKG@.GearLog.flush()") < mb.index("in.removeItemStackFromSlot((short) i, false)")
              < mb.index("try {          // critic M2") < mb.index("r = tryPut(out, safeEmpty(out), s, false);") < mb.index("r = tryPut(inv[k], safeEmpty(inv[k]), s, true);")
              < mb.index("r = -1;") < mb.index("drop.apply(s)") < mb.index("} catch (Throwable x2) {") < mb.index('if (how == null && r != 0) how = "unsure";')
              < mb.index("int b = tryPut(in, i, s, false);") < mb.index("b = tryPut(out, safeEmpty(out), s, false); toOut = true;") < mb.index("int after = cnt(all, id);"),
              "A: move: SALV-BEGIN + flush, the input removal, then ONE catch-all around output (filter off) -> viewer (filter on) -> drop; an "
              "unknown state = unsure; else put back (input, then the first empty output); the count check last")
        check('"SALV-LOST "' in mb and '"SALV-COUNT "' in mb and mb.count("COOL.put(where") == 2, "A: SALV-LOST with the document, SALV-COUNT, the bench cooldown on both put-back paths")
        check(" put(" not in mb and "emptySlot(" not in mb.replace("safeEmpty(", ""), "A: move writes only through tryPut / safeEmpty (critic M1 / M2)")
        i_w = s.index("public static int sweep(@IC@ in, @IC@ out")
        check("@PKG@.GearPack.salvBlocked(s.getItemId(), s.getMetadata())" in s[i_w:i_w + 1100] and "< COOLMS" in s[i_w:i_w + 600],
              "A: sweep = GearPack.salvBlocked semantics, a resting bench (COOL) is skipped")
        i_p = s.index("public static int tryPut(@IC@ c, int j, @IS@ s, boolean filter) {")
        pb = s[i_p:s.index('}""")', i_p)]
        check(pb.index("!emptyAt(c, j)) return 0;") < pb.index("c.setItemStackForSlot((short) j, s, filter);") < pb.index("if (sameAt(c, j, s)) return 1;")
              < pb.index("c.removeItemStackFromSlot((short) j, false);") < pb.index('"SALV-UNDO "') < pb.index("return -1;"),
              "A: tryPut writes only an EMPTY slot, reads it back, takes a changed copy out again (SALV-UNDO), else -1 (critic M1)")
        check('public static boolean isSalv(String b) { return BENCH.equals(b); }' in s, "A: isSalv = BENCH.equals (critic L7)")
        check('assert _sbt.find("ProcessingBenchBlock.advanceProcessing") > _sbt.find("ItemContainer.getSlotMaterialsToRemove")' in s
              and '"FilterType.ALLOW_OUTPUT_ONLY" in _calls(SV["PBBK"], "setupSlots")' in s and '_bsv.get("Id") == "Salvagebench"' in s,
              "A: the build re-checks the engine facts (the tick re-reads its input before processing, the output filter, Bench_Salvage)")
        check('+ "; Salvagebench guard " + (SORD == 1 ? "on"' in s, "A: /gear loot (packText) shows the guard state + counters")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
            try:
                os.rmdir(SCR_BASE)
            except OSError:
                pass
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def main():
    if STATIC:
        sys.exit(run_static())
    if "--h319" in sys.argv:
        H319["run_h319"](arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--only", "--keep", "--dir", "--jar", "--root", "--out") for a in sys.argv[1:]):
        H318["main"]()          # an older child flag (0.3.18 dispatches --h318, the rest goes on down)
        return
    assert os.path.isfile(J319), J319
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    gone = missing_lib_jars()
    if gone or (only and set(only.split(",")) <= {"assets", "h319", "h320"}):
        run_fallback(lambda x: want(x) or (x == "h319" and want("h320")), gone)          # a clean S320 + H319 + H320 run, the rest named as SKIPPED
        return
    H318["run_assets318"] = run_assets320          # the jar compare of THIS round (0.3.19 -> 0.3.20)
    _orig_main316 = H316["main"]

    def main316():
        take18 = H316["take"]

        def take5(path, label):
            d = take18(path, label)
            if label == "h316" and want("h319"):
                env = dict(os.environ)
                env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
                env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
                out = os.path.join(SCRATCH, "h319.json")
                pr = H316["child"](env, "--h319", "--out", out)
                check(pr.returncode == 0, "h319+h320: the child exited cleanly (%s)" % pr.returncode)
                take18(out, "h319")
            return d
        H316["take"] = take5
        return _orig_main316()
    H316["main"] = main316
    if only and "h319" in only.split(",") and "h316" not in only.split(","):
        sys.argv[sys.argv.index("--only") + 1] = only + ",h316"
    H318["main"]()


if __name__ == "__main__":
    main()
