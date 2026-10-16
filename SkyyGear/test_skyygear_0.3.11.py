"""Harness for SkyyGear 0.3.11 (tools/gear_0_3_11_patch.py header) = the 0.3.10 harness's children run on the 0.3.11 jar + H311 (one booted engine,
with SkyyFishing 0.1.7 as its own pack):
    python tools/gear_0_3_11_patch.py && python SkyyGear/build_skyygear_0.3.11.py
    python SkyyGear/test_skyygear_0.3.11.py [--keep] [--only assets,h311,h310,h39,verify,h38,h37,g36,snd,till,life,audit]
(this round ran build + harness through tools/dev/scratch/gear0311/run_head_kit.py = the COMMITTED tools/skyyui.py; children too; the fix round
 2026-10-16 ran plain python with --root tools/dev/scratch/gear0311fix - kit 1.6 was committed by then, so the working tree = HEAD)

  S311 non-class entries 0.3.10 -> 0.3.11: the same entries, only manifest.json changes
  H311 ONE booted engine (the 0.3.5 life setup) + SkyyFishing 0.1.7 + the real plant / weapon / drop list assets:
       W  THE WEAPON FLIP: the plants of sickle.cuts that refuse weapons (Plant_Bush ...) are weapon-breakable after GearSickle.ensure, the
          others (grass, leaves) untouched; part.sickle off = the vanilla value back; on = again; shutdown (unflip) = vanilla
          FIX ROUND: the SERVER SETUP path (the field set + CfgFn.afterHook = the kit's applyRow for a field: row): part.sickle off / on,
          sticks.lists live; an ASSET RELOAD (new objects: a stale FLIP entry + a vanilla container) is flipped / wrapped again by the 10 s look
       V  THE VETO on the REAL GearToolHitSys + REAL DamageBlockEvents: a sword on a bush = cancelled, a sickle / bare hand on a bush = not, a
          sword on grass = not (vanilla); an already-cancelled event untouched; FIX ROUND 2: the refused player is told once per 30 s, the
          sickle's tooltip names what it cuts (not with part.sickle off)
       K  STICKS: Wood_Branch / Wood_Sticks / Plant_Bush wrapped (GearStick); 3000 rolls: sticks.keepPct 50 keeps ~50 % (a 2-5 pile scaled to
          1-3), 100 = vanilla, 0 = none; fibre untouched; unwrap = the original container; a list removed from the row is unwrapped live
       C  THE CUT (seams for the world): a sickle breaking a bush queues one task; the plant gone -> extra Plant Fiber + Sticks (100 % = 1 sure),
          grass AND leaves give fibre only (fix round); the sweep breaks the cut plants around (not stone / logs), each swept plant gets its own
          yield and never sweeps; sickle.sweepMax per tier, sickle.sweepLayers 0 / 2;
          throttle 150 ms; the plant still there = nothing; a sword / bare hand break = no task; protection says no = no sweep; level + Fortune
          raise the chance; reach per tier
       P  THE POLE IN THE KIT: a fresh profile gets the four tools AND the lifelong pole (one Wooden Fishing Rod with our document, SkyyFishing's
          rig lines, the built-in reel, it would cast); a second sweep / restart gives nothing more; a lost pole is not given again (poleKit=1);
          a crash right after the journal -> the next sweep gives it with the SAME uid (one rod); FIX ROUND: the registry on disk names the kit's
          pole but the item never arrived (never seen) -> LL-POLEKIT-REDO gives it again (one rod); a profile with a plain Copper rod gets THAT rod
          marked; a profile that already has a pole = nothing given; lifelong.poleKit off = nothing; gear:fn:poleRule; the bench's Wooden rod
          locked + refused (SkyyFishing 0.1.7 FishBench), the Copper reel needs no Wooden Reel, reelPower(0) = the Wooden reel's
       U  THE UPGRADE TAB on the REAL UpgPage with a counting PageManager: the tab row (Craft | Anvil | Identify | Tools | Upgrade) on every
          Smithing page, the list (lifelong tools first, T1 Crude -> T2 Copper, cost with have / need, why not), Tier up = GearUp.upgrade (25
          Copper Ingots, Mining 5; refused without), a double click of the same token tiers up once, every click answered, mode:6 on the Tools
          page, /upgrade opens the Upgrade tab, every rendered page validates and fits; FIX ROUND: the pole row "T1 Crude -> T2 Copper", gear IN
          Requip listed with Take out (wardrobe:fn:fetch, token-guarded) and then a Tier up row; FIX ROUND 2: the pole / lifelong rows before
          armor, the header counts them
  H310 / H39 / VERIFY / H38 / H37 / G36 / SND / TILL / L35 / AA  the 0.3.10 harness's children on the 0.3.11 jar, run with
       -Dskyy.harness.noPoleKit=true (lifelong.poleKit reads as off = 0.3.10's lifelong flow they were written for; H311 P covers it on)
Scratch: tools/dev/scratch/gear0311/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, glob, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.11"
V310 = "0.3.10"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0311")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J310 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V310))                       # read only
FI7_SRC = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.7.jar")                        # read only (copied into scratch)
PKG = "com.skyy.gear."
RUNNER = os.path.join(SCR_ROOT, "run_head_kit.py")          # the committed-kit runner (scratch); missing = plain python

# ---- the 0.3.10 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H310 = os.path.join(HERE, "test_skyygear_0.3.10.py")
_T310 = open(_H310, encoding="utf-8").read()
_cut = _T310.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H310, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H310 = {"__name__": "skyygear_h310", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T310[:_cut], _H310 + " (library)", "exec"), H310)
sys.argv = _argv
H39 = H310["H39"]
H38 = H39["H38"]
H37, H36, H35, H = H38["H37"], H38["H36"], H38["H35"], H38["H"]
FAKE_DIR = H38["FAKE_DIR"]
FAKE_PKG = H38["FAKE_PKG"]
FAILS, OKS = [], [0]
# by-design changes of 0.3.11 in the older children (prefix of the check text -> why)
# The older children run with -Dskyy.harness.noPoleKit=true (GearCfg's harness seam: lifelong.poleKit reads as off = exactly 0.3.10's lifelong
# flow, their baseline "four tools, the pole from Marlow"); H311 runs without it (the pole in the starting kit). Nothing is waived by default.
WAIVE = [("L35: every 0.3.5 life check passes on 0.3.7 (295 ok) except the explained deviations: unexpected []",
          "pre-existing: the 0.3.10 harness on the pinned 0.3.10 jar gives the same 295 (re-run 2026-10-15) - every check that ran passed or is an explained deviation; only the old >= 300 count")]
# fix round (critic 3.6): with lifelong.poleKit off (the older children's seam) the texts no longer send players to Marlow - SkyyQuests 0.3.4's
# Marlow gives a hook, not a pole
WAIVE += [("L35: every 0.3.5 life check passes on 0.3.7 (293 ok) except the explained deviations: unexpected []",
           "the 295 of the pinned 0.3.10 jar minus the two by-design text deviations of this fix round (G35 P6 / G35 P7 FIX 2: no Marlow pole text, explained below); only the old >= 300 count"),
          ("P1: no pole granted = the row says it comes from Marlow",
           "0.3.11 fix round by design: the kit-off pole row says 'Not handed out on this server - a pole a quest gives you becomes it' (Marlow gives no pole since SkyyQuests 0.3.4); H311 covers the kit-on row")]
WAIVED = []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S311
def run_assets311():
    ea, eb = entries(J310), entries(JAR)
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(sorted(n for n in ea if not n.endswith(".class")) == sorted(n for n in eb if not n.endswith(".class")) and changed == ["manifest.json"],
          "S311: 0.3.10 -> 0.3.11: the same entries, only manifest.json changed among non-class files: %s / added %s gone %s"
          % (changed, sorted(set(eb) - set(ea))[:3], sorted(set(ea) - set(eb))[:3]))
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.11"' in man and "SICKLES cut bushes" in man and "Upgrade tab" in man and "in every starting kit" in man, "S311: the manifest names the round")
    cls = sorted(n for n in set(eb) - set(ea) if n.endswith(".class"))
    check(cls == sorted("com/skyy/gear/%s.class" % c for c in ("GearSickle", "GearSickleTask", "GearSickleSys", "GearStick", "UpgPage")),
          "S311: the new classes: %s" % cls)


# ====================================================================================================== H311
def run_h311(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7          # this child boots with SkyyFishing 0.1.7 (the older children keep 0.1.6)
    mtj = os.path.join(SCRATCH, "packs", "Multitools-1.2.9.jar")
    if os.path.isfile(H310["MT_SRC"]) and not os.path.isfile(mtj):
        shutil.copyfile(H310["MT_SRC"], mtj)
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h311(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H311: the phase raised: %s" % traceback.format_exc()[-1500:])
    K.save()


def _h311(L, K):
    from jpype import JClass, JInt, JShort, JLong, JFloat, JDouble, JObject, JArray, JString, JImplements, JOverride
    import skyyui as SUI
    br, Gear, Cfg = L["br"], L["Gear"], L["Cfg"]
    mkinv, world, PR1, PR2, U1, U2, stack, doc, skills, apply, logs, COINS = (L["mkinv"], L["world"], L["PR1"], L["PR2"], L["U1"], L["U2"], L["stack"],
                                                                            L["doc"], L["skills"], L["apply"], L["logs"], L["COINS"])
    us, jf, ITEM, lls, ids = L["us"], L["jf"], L["ITEM"], L["lls"], L["ids"]
    P = lambda n: JClass(PKG + n)
    Sk, Stk, LL, Life, Ui, Up, Stamp = P("GearSickle"), P("GearStick"), P("GearLL"), P("GearLife"), P("GearUi"), P("GearUp"), P("GearStamp")
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    IDL = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemDropList")
    IDR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemDrop")
    HAL, JL = JClass("java.util.ArrayList"), JClass("java.lang.Long")
    Integer_, Bool_ = JClass("java.lang.Integer"), JClass("java.lang.Boolean")
    V3 = JClass("org.joml.Vector3i")
    afs = L["afs"]
    AZP = L["AZP"]

    # ---- the real assets this phase needs (the cached Assets.zip, in memory): plants, a sword, the stick drop lists
    with zipfile.ZipFile(AZP) as az_:
        nl = az_.namelist()
    want_items = ["Plant_Bush", "Plant_Bush_Green", "Plant_Grass_Lush", "Plant_Leaves_Oak", "Plant_Fern", "Weapon_Sword_Crude", "Wood_Oak_Branch_Long",
                  "Wood_Sticks", "Rock_Stone", "Ingredient_Fibre", "Ingredient_Stick", "Ingredient_Bar_Copper"]
    paths = HAL()
    for i_ in want_items:
        m_ = [n for n in nl if n.startswith("Server/Item/Items/") and n.endswith("/" + i_ + ".json")]
        if m_ and ITEM.getAssetMap().getAsset(i_) is None:
            paths.add(afs.getPath("/" + m_[0]))
    if paths.size() > 0:
        ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", paths)
    dl = HAL()
    for d_ in ("Wood_Branch", "Wood_Sticks", "Plant_Bush", "Plant_Bush_Berry_Red", "Tree_Leaves", "Plant_Fiber"):
        m_ = [n for n in nl if n.startswith("Server/Drops/") and n.endswith("/" + d_ + ".json")]
        if m_ and IDL.getAssetMap().getAsset(d_) is None:
            dl.add(afs.getPath("/" + m_[0]))
    if dl.size() > 0:
        try:
            IDL.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", dl)
        except Exception as e_:
            K.notes.append("H311: drop lists did not load: %s" % str(e_)[:200])
    bmap = BTY.getAssetMap().getAssetMap()
    BT = dict((n, bmap.get(n)) for n in ("Plant_Bush", "Plant_Bush_Green", "Plant_Grass_Lush", "Plant_Leaves_Oak", "Rock_Stone", "Wood_Oak_Branch_Long"))
    K.check(all(v is not None for v in BT.values()) and ITEM.getAssetMap().getAsset("Weapon_Sword_Crude") is not None
            and IDL.getAssetMap().getAsset("Wood_Branch") is not None,
            "H311 setup: the real plant BlockTypes, the Crude Sword and the stick drop lists are in the stores: %s" % [k for k, v in BT.items() if v is None])
    soft = lambda n: BT[n].getGathering().getSoft()

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))

    # ============================================================== W: the weapon flip
    apply()
    Sk.ENS = JLong(0)
    Sk.ensure()
    flip = set(str(k) for k in Sk.FLIP.keySet())
    K.check("Plant_Bush" in flip and "Plant_Bush_Green" in flip and bool(soft("Plant_Bush").isWeaponBreakable()) and "Plant_Grass_Lush" not in flip
            and "Plant_Leaves_Oak" not in flip and bool(soft("Plant_Grass_Lush").isWeaponBreakable()),
            "W the bushes (vanilla: no weapons) are weapon-breakable now; grass / leaves (already breakable) untouched: %d flipped" % len(flip))
    apply(part__sickle="false")
    K.check(not bool(soft("Plant_Bush").isWeaponBreakable()) and int(Sk.FLIP.size()) == 0, "W part.sickle off = the vanilla value back (a config load re-flips at once)")
    apply()
    K.check(bool(soft("Plant_Bush").isWeaponBreakable()) and int(Sk.FLIP.size()) >= 2, "W on again = flipped again")
    apply(sickle__cuts="Plant_Grass")
    K.check(not bool(soft("Plant_Bush").isWeaponBreakable()) and "Plant_Bush" not in set(str(k) for k in Sk.FLIP.keySet()),
            "W a plant that left sickle.cuts gets its vanilla value back")
    apply()
    Sk.unflip()
    K.check(not bool(soft("Plant_Bush").isWeaponBreakable()), "W shutdown (unflip) = vanilla")
    Sk.ENS = JLong(0)
    Sk.ensure()
    # FIX ROUND (engine critic 1): the Server Setup path = the field set + the row's after= hook (no file load)
    CRows, CFn = P("CfgRows"), P("CfgFn")
    aft = dict((k_, str(CRows.BAFTER[int(CRows.index(k_))])) for k_ in ("part.sickle", "sickle.cuts", "sticks.lists"))
    K.check(all(v_.endswith("GearSickle.refresh") for v_ in aft.values()), "W the rows part.sickle / sickle.cuts / sticks.lists carry after=GearSickle.refresh: %s" % aft)
    Cfg.SICKLE_ON = False
    CFn.afterHook(JInt(int(CRows.index("part.sickle"))))
    K.check(not bool(soft("Plant_Bush").isWeaponBreakable()) and int(Sk.FLIP.size()) == 0, "W Server Setup: part.sickle OFF (field + after hook, no file load) = the vanilla value back at once")
    Cfg.SICKLE_ON = True
    CFn.afterHook(JInt(int(CRows.index("part.sickle"))))
    K.check(bool(soft("Plant_Bush").isWeaponBreakable()) and int(Sk.FLIP.size()) >= 2, "W Server Setup: part.sickle ON again = bushes sickle-breakable at once")
    Cfg.SICKLE_CUTS = "Plant_Grass"
    CFn.afterHook(JInt(int(CRows.index("sickle.cuts"))))
    K.check(not bool(soft("Plant_Bush").isWeaponBreakable()), "W Server Setup: a plant taken off sickle.cuts gets its vanilla value back at once")
    apply()
    K.check(bool(soft("Plant_Bush").isWeaponBreakable()), "W ... and back on the list")
    # FIX ROUND (safety critic 1): an asset hot-reload makes NEW objects - simulated: FLIP holds a stale object for Plant_Bush and the "new"
    # one has the vanilla value; the 10 s look (tick, from the BreakBlockEvent system) flips the new one
    SBDc = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.SoftBlockDropType")
    fwb = SBDc.class_.getDeclaredField("isWeaponBreakable")
    fwb.setAccessible(True)
    stale = us.allocateInstance(SBDc.class_)
    Sk.FLIP.put("Plant_Bush", stale)
    fwb.setBoolean(soft("Plant_Bush"), False)
    Sk.ENS = JLong(1)
    Sk.tick()
    K.check(bool(soft("Plant_Bush").isWeaponBreakable()) and Sk.FLIP.get("Plant_Bush") == soft("Plant_Bush"),
            "W asset reload: the look flips the NEW Plant_Bush object (the stale entry replaced)")
    Sk.ENS = JLong(int(JClass("java.lang.System").currentTimeMillis()))
    fwb.setBoolean(soft("Plant_Bush"), False)
    Sk.tick()
    K.check(not bool(soft("Plant_Bush").isWeaponBreakable()), "W the look runs at most every 10 s (a tick 0 s later does nothing)")
    Sk.ENS = JLong(1)
    Sk.tick()

    # ============================================================== V: the veto on the REAL hit system
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    ctor = [c for c in DBE.class_.getConstructors() if len(c.getParameterTypes()) == 5][0]
    pts = [str(p.getName()) for p in ctor.getParameterTypes()]
    JFl = JClass("java.lang.Float")

    def dev(s_, b_, d=1.0):
        args, nf = [], 0
        for p in pts:
            if p.endswith("ItemStack"):
                args.append(s_)
            elif p.endswith("BlockType"):
                args.append(b_)
            elif p == "float":
                args.append(JFl.valueOf(JFloat(1.0 if nf == 0 else d)))
                nf += 1
            else:
                args.append(V3(JInt(0), JInt(64), JInt(0)))
        return ctor.newInstance(JArray(JObject)(args))
    hs = P("GearToolHitSys")()
    invH, csH = mkinv()
    refH, stH, chH, plH = world(invH, csH, PR1)
    skills(Farming=10, Mining=10, Foraging=10)

    def hit(s_, bn):
        e_ = dev(s_, BT[bn])
        hs.handle(JInt(0), chH, stH, None, e_)
        return bool(e_.isCancelled())
    said = L["said"]
    PR1.said = None
    LL.TOLD.remove(JString(str(PR1.getUuid()) + ":sicklebush"))
    v0 = int(Sk.N[1])
    r = [hit(stack("Weapon_Sword_Crude"), "Plant_Bush"), hit(stack("Tool_Sickle_Crude"), "Plant_Bush"), hit(None, "Plant_Bush"),
         hit(stack("Weapon_Sword_Crude"), "Plant_Grass_Lush"), hit(stack("Tool_Sickle_Crude"), "Plant_Leaves_Oak")]
    eq(r, [True, False, False, False, False], "V the REAL hit system: sword on a bush = refused (vanilla's rule), sickle / bare hand on a bush = allowed, sword on "
         "grass = allowed (vanilla), sickle on leaves = allowed")
    K.check(int(Sk.N[1]) - v0 == 1, "V the refusal is counted once")
    e_c = dev(stack("Weapon_Sword_Crude"), BT["Plant_Bush"])
    e_c.setCancelled(True)
    hs.handle(JInt(0), chH, stH, None, e_c)
    K.check(bool(e_c.isCancelled()) and int(Sk.N[1]) - v0 == 1, "V an event another mod cancelled is left alone")
    # FIX ROUND 2 (critic: "for some reason"): the refused player is told why, at most once per GearSickle.VETO_GAP
    tl = [x for x in said(PR1) if "need a sickle" in x]
    K.check(len(tl) == 1 and "Bushes, brambles and vines need a sickle" in tl[0] and "/sickle" in tl[0] and int(Sk.VETO_GAP) == 30000,
            "V (fix round 2) a sword refused on a bush tells the player once: 'Bushes, brambles and vines need a sickle ... /sickle': %s" % said(PR1)[-2:])
    hit(stack("Weapon_Sword_Crude"), "Plant_Bush")
    K.check(len([x for x in said(PR1) if "need a sickle" in x]) == 1 and int(Sk.N[1]) - v0 == 2, "V (fix round 2) a second refusal within 30 s: refused, not told again")
    hit(stack("Tool_Sickle_Crude"), "Plant_Bush")
    hit(stack("Weapon_Sword_Crude"), "Plant_Grass_Lush")
    K.check(len([x for x in said(PR1) if "need a sickle" in x]) == 1, "V (fix round 2) a sickle on a bush / a sword on grass tells nothing")
    GT_ = P("GearTool")

    def tip(id_):
        t_, c_ = HAL(), HAL()
        GT_.lines(None, JString(id_), None, t_, c_)
        return [str(x) for x in t_]
    tps, tpp = tip("Tool_Sickle_Crude"), tip("Tool_Pickaxe_Crude")
    K.check(any("Cuts bushes, grass and leaves" in x for x in tps) and not any("Cuts bushes" in x for x in tpp),
            "V (fix round 2) the sickle's tooltip says 'Cuts bushes, grass and leaves - sweeps the plants around' (a pickaxe's does not): %s" % tps)
    apply(part__sickle="false")
    K.check(not any("Cuts bushes" in x for x in tip("Tool_Sickle_Crude")), "V (fix round 2) part.sickle off: no cut line on the sickle")
    apply()

    # ============================================================== K: the stick cut
    @JImplements("java.util.function.DoubleSupplier")
    class DS(object):
        def __init__(self, seed):
            self.r = random.Random(seed)

        @JOverride
        def getAsDouble(self):
            return self.r.random()

    def roll(lid, n=3000, seed=7):
        c_ = IDL.getAssetMap().getAsset(lid).getContainer()
        ds = DS(seed)
        st_, fb, lo, hi = 0, 0, 0, 0
        for _ in range(n):
            out_ = HAL()
            c_.populateDrops(out_, ds, JString(lid))
            for o in out_:
                if str(o.getItemId()) == "Ingredient_Stick":
                    st_ += 1
                    lo += int(o.getQuantityMin())
                    hi += int(o.getQuantityMax())
                elif str(o.getItemId()) == "Ingredient_Fibre":
                    fb += 1
        return st_, (lo + hi) / 2.0, fb
    wrapped = dict((str(k), str(v.getClass().getName())) for k, v in Sk.WRAP.entrySet())
    K.check(sorted(wrapped) == ["Plant_Bush", "Plant_Bush_Berry_Red", "Wood_Branch", "Wood_Sticks"][:len(wrapped)] and "Wood_Branch" in wrapped
            and str(IDL.getAssetMap().getAsset("Wood_Branch").getContainer().getClass().getName()).endswith("GearStick"),
            "K the stick drop lists are wrapped: %s" % sorted(wrapped))
    apply(sticks__keepPct="100")
    v_br, v_brq, _f0 = roll("Wood_Branch")
    v_pl, v_plq, _f1 = roll("Wood_Sticks")
    v_bu, _q, v_bf = roll("Plant_Bush")
    apply()
    k_br, k_brq, _f2 = roll("Wood_Branch")
    k_pl, k_plq, _f3 = roll("Wood_Sticks")
    k_bu, _q2, k_bf = roll("Plant_Bush")
    fr_br = k_brq / max(v_brq, 1)
    fr_pl = k_plq / max(v_plq, 1)
    fr_bu = k_bu / max(v_bu, 1)
    K.check(0.43 < fr_br < 0.57 and 0.40 < fr_pl < 0.62 and 0.43 < fr_bu < 0.57 and abs(k_bf - v_bf) < 0.12 * max(v_bf, 1) and int(Cfg.STICK_KEEP) == 50,
            "K sticks.keepPct 50 (the default): branches keep %.2f, stick piles %.2f (2-5 -> 1-3), bushes %.2f of the vanilla sticks; bush fibre unchanged (%d vs %d)"
            % (fr_br, fr_pl, fr_bu, k_bf, v_bf))
    apply(sticks__keepPct="0")
    z_br, _a, _b = roll("Wood_Branch", 500)
    apply()
    eq(z_br, 0, "K sticks.keepPct 0 = no stick at all")
    inner = IDL.getAssetMap().getAsset("Wood_Sticks").getContainer().inner
    apply(sticks__lists="Wood_Branch")
    K.check(IDL.getAssetMap().getAsset("Wood_Sticks").getContainer() == inner and "Wood_Sticks" not in set(str(k) for k in Sk.WRAP.keySet()),
            "K a list removed from sticks.lists gets its own container back (live)")
    apply()
    K.check(str(IDL.getAssetMap().getAsset("Wood_Sticks").getContainer().getClass().getName()).endswith("GearStick"), "K ... and is wrapped again when it returns")
    # FIX ROUND: sticks.lists through Server Setup (field + after hook) and an asset reload (a vanilla container again) -> wrapped by the look
    Cfg.STICK_LISTS = "Wood_Branch"
    CFn.afterHook(JInt(int(CRows.index("sticks.lists"))))
    K.check(IDL.getAssetMap().getAsset("Wood_Sticks").getContainer() == inner, "K Server Setup: sticks.lists without Wood_Sticks = its own container back at once")
    apply()
    K.check(str(IDL.getAssetMap().getAsset("Wood_Sticks").getContainer().getClass().getName()).endswith("GearStick"), "K ... and wrapped again")
    fco = IDL.class_.getDeclaredField("container")
    fco.setAccessible(True)
    fco.set(IDL.getAssetMap().getAsset("Wood_Sticks"), inner)
    Sk.ENS = JLong(1)
    Sk.tick()
    K.check(str(IDL.getAssetMap().getAsset("Wood_Sticks").getContainer().getClass().getName()).endswith("GearStick"), "K asset reload: a vanilla container again is wrapped by the 10 s look")
    K.check(int(IDL.getAssetMap().getAsset("Wood_Branch").getContainer().getAllDrops(HAL()).size()) >= 1, "K getAllDrops answers through the wrapper")

    # ============================================================== C: the cut (seams for the world, the bonus give, the break, protection)
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    bctor = [c for c in BBE.class_.getConstructors()]
    bc = [c for c in bctor if [str(p.getName()) for p in c.getParameterTypes()] and any(str(p.getName()).endswith("BlockType") for p in c.getParameterTypes())][0]
    bpts = [str(p.getName()) for p in bc.getParameterTypes()]

    def bev(s_, bn, x, y, z):
        args = []
        for p in bpts:
            if p.endswith("ItemStack"):
                args.append(s_)
            elif p.endswith("BlockType"):
                args.append(BT[bn] if bn in BT else bmap.get(bn))
            elif "Vector3i" in p:
                args.append(V3(JInt(x), JInt(y), JInt(z)))
            else:
                args.append(None)
        return bc.newInstance(JArray(JObject)(args))
    WORLD = {}
    GOT = []
    PERM = [True]

    @JImplements("java.util.function.Function")
    class BlkFn(object):
        @JOverride
        def apply(self, o):
            return JString(WORLD.get((int(o[0]), int(o[1]), int(o[2])), "Empty"))

    @JImplements("java.util.function.Function")
    class GiveFn(object):
        @JOverride
        def apply(self, o):
            GOT.append((str(o[1]), int(o[2])))
            return Bool_.TRUE

    @JImplements("java.util.function.Function")
    class PermFn(object):
        @JOverride
        def apply(self, o):
            return Bool_.TRUE if PERM[0] else Bool_.FALSE
    HELD = [stack("Tool_Sickle_Crude")]

    @JImplements("java.util.function.Function")
    class BrkFn(object):
        """the engine's performBlockBreak: each position -> a real BreakBlockEvent on the player (GearSickleSys = onBreak), then gone"""
        @JOverride
        def apply(self, o):
            n_ = 0
            for v in o[1]:
                key = (int(v.x()), int(v.y()), int(v.z()))
                bn = WORLD.get(key)
                if bn is None or bn == "Empty":
                    continue
                Sk.onBreak(PR1, stH, bev(HELD[0], bn, key[0], key[1], key[2]))
                WORLD[key] = "Empty"
                n_ += 1
            return Integer_.valueOf(n_)
    RUN = HAL()
    Sk.RUN, Sk.BLK, Sk.GIVE, Sk.PERM, Sk.BRK = RUN, BlkFn(), GiveFn(), PermFn(), BrkFn()
    jf(JClass("com.hypixel.hytale.server.core.universe.PlayerRef"), "entity").set(PR1, refH)
    apply(sickle__fiberChance="100", sickle__stickChance="100", sickle__perLevel="0", sickle__perFortune="0")

    def scene():
        WORLD.clear()
        WORLD.update({(0, 64, 0): "Plant_Bush", (1, 64, 0): "Plant_Grass_Lush", (0, 64, 1): "Plant_Leaves_Oak", (-1, 64, 0): "Rock_Stone",
                      (0, 64, -1): "Wood_Oak_Branch_Long", (1, 65, 1): "Plant_Bush_Green", (2, 64, 0): "Plant_Grass_Lush", (0, 66, 0): "Plant_Bush"})
        del GOT[:]
        RUN.clear()
        Sk.LAST.clear()

    def runall():
        res_ = []
        while RUN.size() > 0:
            t_ = RUN.get(JInt(0))
            RUN.remove(t_)
            res_.append(Sk.done(t_))
        return res_
    scene()
    K.check(bool(Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 64, 0))) and int(RUN.size()) == 1 and bool(RUN.get(0).sweep),
            "C a sickle breaking a bush = ONE task for the next tick (a hit: it may sweep)")
    WORLD[(0, 64, 0)] = "Empty"
    rs = runall()
    gone = sorted(k for k, v in WORLD.items() if v == "Empty")
    K.check(rs[0] is not None and list(rs[0]) == [1, 1, 3] and gone == sorted([(0, 64, 0), (1, 64, 0), (0, 64, 1), (1, 65, 1)])
            and WORLD[(-1, 64, 0)] == "Rock_Stone" and WORLD[(0, 64, -1)] == "Wood_Oak_Branch_Long" and WORLD[(2, 64, 0)] == "Plant_Grass_Lush"
            and WORLD[(0, 66, 0)] == "Plant_Bush",
            "C the cut: 1 Fibre + 1 Stick (100 %%), the Crude sweep (reach 1) took grass, leaves and the bush above-diagonal - never stone, a branch "
            "or plants 2 away: %s / gone %s" % (rs[:1] and list(rs[0]) if rs[0] is not None else None, gone))
    K.check(len(rs) == 4 and all(x is not None and list(x)[2] == 0 for x in rs[1:]),
            "C each swept plant got its own yield task and never swept again (SWEEPING guard): %s" % [list(x) if x is not None else None for x in rs])
    eq(sorted(GOT), sorted([("Ingredient_Fibre", 1), ("Ingredient_Stick", 1), ("Ingredient_Fibre", 1), ("Ingredient_Fibre", 1),
                              ("Ingredient_Fibre", 1), ("Ingredient_Stick", 1)]),
         "C the gifts: bush = fibre + stick, grass = fibre only, leaves = fibre only (fix round), the green bush = fibre + stick")
    # the plant still there (a later system cancelled the break) = nothing
    scene()
    Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 64, 0))
    n3 = int(Sk.N[3])
    rs = runall()
    K.check(rs == [None] and not GOT and int(Sk.N[3]) == n3 + 1 and WORLD[(1, 64, 0)] == "Plant_Grass_Lush", "C the plant is still there = no gift, no sweep")
    # a sword / bare hand break, a block that is no cut plant = no task
    scene()
    K.check(not bool(Sk.onBreak(PR1, stH, bev(stack("Weapon_Sword_Crude"), "Plant_Grass_Lush", 1, 64, 0))) and not bool(Sk.onBreak(PR1, stH, bev(None, "Plant_Grass_Lush", 1, 64, 0)))
            and not bool(Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Rock_Stone", -1, 64, 0))) and int(RUN.size()) == 0,
            "C a sword / bare hand cut, or the sickle on stone = no task (vanilla drops only)")
    # throttle: two hits in the same swing sweep once
    scene()
    Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 64, 0))
    Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 66, 0))
    WORLD[(0, 64, 0)] = "Empty"
    WORLD[(0, 66, 0)] = "Empty"
    rs = runall()
    K.check(rs[0] is not None and list(rs[0])[2] >= 1 and rs[1] is not None and list(rs[1])[2] == 0, "C two hits in one swing: one sweep (150 ms), both get their gift")
    # protection says no: no sweep (the gift stays - the cut itself was allowed)
    scene()
    PERM[0] = False
    Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 64, 0))
    WORLD[(0, 64, 0)] = "Empty"
    n8 = int(Sk.N[8])
    rs = runall()
    PERM[0] = True
    K.check(list(rs[0]) == [1, 1, 0] and int(Sk.N[8]) == n8 + 1 and WORLD[(1, 64, 0)] == "Plant_Grass_Lush", "C island protection says no = no sweep (the cut's own gift stays)")
    # reach per tier, sweepMax
    eq([int(Sk.reach(i)) for i in ("Tool_Sickle_Crude", "Tool_Sickle_Copper", "Tool_Sickle_Iron")], [1, 1, 2], "C sickle.sweep reach: Crude 1, Copper 1, Iron 2")
    eq([int(Sk.cap(i)) for i in ("Tool_Sickle_Crude", "Tool_Sickle_Copper", "Tool_Sickle_Iron", "Tool_Sickle_Onyxium")], [24, 24, 40, 80],
       "C sickle.sweepMax per tier (fix round): Crude 24, Copper 24, Iron 40, Onyxium 80")
    K.check(Sk.checkMax("sickle.sweepMax", "24,24,40,40,60,60,80,80") is None and Sk.checkMax("sickle.sweepMax", "24") is not None
            and Sk.checkMax("sickle.sweepMax", "1,1,1,1,1,1,1,201") is not None, "C the Server Setup check of sickle.sweepMax")
    apply(sickle__fiberChance="100", sickle__stickChance="100", sickle__perLevel="0", sickle__perFortune="0", sickle__sweepMax="1,1,1,1,1,1,1,1")
    scene()
    Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 64, 0))
    WORLD[(0, 64, 0)] = "Empty"
    rs = runall()
    eq(list(rs[0])[2], 1, "C sickle.sweepMax 1 = one plant swept")
    # sickle.sweepLayers (fix round): 2 = the bush two above is swept too; 0 = only the cut plant's own layer
    apply(sickle__fiberChance="100", sickle__stickChance="100", sickle__perLevel="0", sickle__perFortune="0", sickle__sweepLayers="2")
    scene()
    Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 64, 0))
    WORLD[(0, 64, 0)] = "Empty"
    rs = runall()
    K.check(WORLD[(0, 66, 0)] == "Empty" and WORLD[(1, 65, 1)] == "Empty" and list(rs[0])[2] == 4, "C sickle.sweepLayers 2: the bush two above is swept too: %s" % list(rs[0]))
    apply(sickle__fiberChance="100", sickle__stickChance="100", sickle__perLevel="0", sickle__perFortune="0", sickle__sweepLayers="0")
    scene()
    Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Bush", 0, 64, 0))
    WORLD[(0, 64, 0)] = "Empty"
    rs = runall()
    K.check(WORLD[(1, 65, 1)] == "Plant_Bush_Green" and WORLD[(1, 64, 0)] == "Empty" and list(rs[0])[2] == 2, "C sickle.sweepLayers 0: only the cut plant's own layer: %s" % list(rs[0]))
    # the chances: 250 % = 2 or 3; level + Fortune add
    apply(sickle__fiberChance="250", sickle__stickChance="0", sickle__perLevel="0", sickle__perFortune="0")
    fs = []
    for i in range(40):
        scene()
        Sk.onBreak(PR1, stH, bev(stack("Tool_Sickle_Crude"), "Plant_Grass_Lush", 2, 64, 0))
        WORLD[(2, 64, 0)] = "Empty"
        Sk.LAST.put(U1, JLong(2 ** 62))          # no sweep here
        fs.append(list(runall()[0])[0])
    K.check(set(fs) == {2, 3}, "C sickle.fiberChance 250 = 2 sure + a half chance of a 3rd: %s" % sorted(set(fs)))
    apply()
    K.check(int(Sk.roll(JDouble(0.0))) == 0 and int(Sk.roll(JDouble(9999.0))) == 5, "C roll: 0 %% = none, a huge chance = at most 5")
    K.check(Sk.checkSweep("sickle.sweep", "1,1,2,2,3,3,4,4") is None and Sk.checkSweep("sickle.sweep", "1,2") is not None and Sk.checkSweep("sickle.sweep", "1,1,2,2,3,3,4,9") is not None,
            "C the Server Setup check of sickle.sweep")
    Sk.RUN, Sk.BLK, Sk.GIVE, Sk.PERM, Sk.BRK = None, None, None, None, None
    K.check("cuts plants" in str(Sk.statusText()) and "sticks kept 50%" in str(Sk.statusText()), "C statusText: %s" % Sk.statusText())

    # ============================================================== P: the pole in the starting kit
    L["wipe_home"]()          # fresh profiles (the older children share this scratch home)
    FB = JClass("com.skyy.fishing.FishBridge")
    FB.questInit()
    FR = JClass("com.skyy.fishing.FishRig")
    FC = JClass("com.skyy.fishing.FishCfg")
    K.check(ITEM.getAssetMap().getAsset("SkyyFishing_Rod_Bamboo") is not None and br.get("fishing:fn:restamp") is not None,
            "P SkyyFishing 0.1.7 is loaded (its rods, fishing:fn:restamp)")
    COINS[0] = 10 ** 7
    skills(Mining=4, Foraging=4, Farming=4, Fishing=4)
    inv, cs = mkinv()
    Life.sweep(PR1, inv, True)
    pk = str(Gear.pkey(U1))
    REG = LL.reg(pk)
    mine = lls(cs, pk)
    poles = [x for x in mine if x[2] == int(LL.POLE)]
    K.check(REG.getProperty("pickaxe.uid") is not None and REG.getProperty("pole.uid") is not None and str(REG.getProperty("poleKit")) == "1" and len(poles) == 1
            and str(poles[0][6].getItemId()) == "SkyyFishing_Rod_Bamboo" and poles[0][3] == str(REG.getProperty("pole.uid")),
            "P a fresh profile: the four tools AND the lifelong pole (one Wooden Fishing Rod, uid = the registry's, poleKit=1): %s" % [(x[0], x[2]) for x in mine])
    K.check(str(REG.getProperty("poleKitHow")) == "give" and str(REG.getProperty("poleKitUid")) == str(REG.getProperty("pole.uid")) and str(REG.getProperty("pole.seen")) == "1",
            "P (fix round) the registry records how the kit did it (poleKitHow=give, poleKitUid = the pole's uid) and the pass saw it")
    pole = poles[0][6]
    K.check(FR.doc(pole) is not None and str(FR.rigOf(pole)[0]) == "0" and float(FC.reelPower(JInt(0))) > 0 and not bool(FR.stale(pole)) and FR.llWhy(pole, U1) is None,
            "P the pole carries SkyyFishing's rig (redrawn by fishing:fn:restamp): no reel fitted = the built-in reel (power %.1f), not stale, it casts for its owner"
            % float(FC.reelPower(JInt(0))))
    lines = [str(l) for l in FR.rodLines(JInt(0), FR.rigOf(pole))]
    K.check([l for l in lines if l.startswith("Reel: basic, built in")], "P its tooltip: 'Reel: basic, built in': %s" % lines[:2])
    # C (continued): YOUR lifelong sickle's level + Fortune raise the sickle chances (a plain sickle works at its own level)
    sick = [x[6] for x in lls(cs, pk) if x[2] == 3]
    skills(Farming=20)
    Gate_ = P("GearGate")
    try:
        Gate_.forget(U1)
    except Exception:
        pass
    ex = float(Sk.extra(U1, sick[0])) if sick else -1.0
    skills(Farming=1)
    try:
        Gate_.forget(U1)
    except Exception:
        pass
    ex1 = float(Sk.extra(U1, sick[0])) if sick else -1.0
    K.check(sick and ex > ex1 >= 0.0, "C your lifelong sickle: Farming 20 = +%.1f %%, Farming 1 = +%.1f %% (level x sickle.perLevel + Fortune x sickle.perFortune)" % (ex, ex1))
    skills(Mining=4, Foraging=4, Farming=4, Fishing=4)
    LL.LAST.clear()
    Life.sweep(PR1, inv, True)
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PR1, inv, True)
    eq(len([x for x in lls(cs, pk) if x[2] == int(LL.POLE)]), 1, "P a second sweep and a restart give nothing more (one pole)")
    sec, slot = poles[0][0], poles[0][1]
    cs[sec].removeItemStackFromSlot(JShort(slot))
    LL.LAST.clear()
    Life.sweep(PR1, inv, True)
    eq(len([x for x in lls(cs, pk) if x[2] == int(LL.POLE)]), 0, "P a LOST pole is not given again by the sweep (poleKit=1; /pole brings it back)")
    nk = [int(x) for x in Life.NK]
    K.check(nk[0] == 1, "P counters: given %s" % nk)
    # a crash right after the journal: the next sweep gives it with the SAME uid
    inv2, cs2 = mkinv()
    pk2 = str(Gear.pkey(U2))
    skills(u=U2, Mining=4, Foraging=4, Farming=4, Fishing=4)
    Life.CRASH_AT = JInt(4)
    try:
        Life.sweep(PR2, inv2, True)
    except Exception:
        pass
    LL.LAST.clear()
    Life.CRASH_AT = JInt(0)
    R2 = LL.reg(pk2)
    pend = R2.getProperty("pole.pend")
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PR2, inv2, True)
    R2 = LL.reg(pk2)
    p2 = [x for x in lls(cs2, pk2) if x[2] == int(LL.POLE)]
    K.check(len(p2) == 1 and (pend is None or str(R2.getProperty("pole.uid")) == str(pend)) and str(R2.getProperty("poleKit")) == "1",
            "P a crash after the journal: the next sweep gives the pole with the journal's uid (%s), one rod" % pend)
    # an existing profile (migrated before 0.3.11) with a plain Copper rod: THAT rod becomes the pole
    U3 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000c3")
    L["PKEY"][str(U3)] = "p3"
    PR3 = L["mkpr"](U3, "Third")
    skills(u=U3, Mining=4, Foraging=4, Farming=4, Fishing=4)
    inv3, cs3 = mkinv()
    Life.sweep(PR3, inv3, True)
    R3 = LL.reg("p3")
    rodp = [x for x in lls(cs3, "p3") if x[2] == int(LL.POLE)]
    for x in rodp:
        cs3[x[0]].removeItemStackFromSlot(JShort(x[1]))
    for k_ in ("pole.uid", "pole.id", "pole.rp", "poleKit", "poleKitAt"):
        R3.remove(k_)
    LL.save("p3", R3)
    cs3["storage"].setItemStackForSlot(JShort(5), stack("SkyyFishing_Rod_Copper"))
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PR3, inv3, True)
    R3 = LL.reg("p3")
    p3 = [x for x in lls(cs3, "p3") if x[2] == int(LL.POLE)]
    K.check(len(p3) == 1 and str(p3[0][6].getItemId()) == "SkyyFishing_Rod_Copper" and ids(cs3).get("SkyyFishing_Rod_Bamboo", 0) == 0,
            "P a profile that carries a plain Copper rod: THAT rod becomes the lifelong pole (no Wooden one given): %s" % [str(x[6].getItemId()) for x in p3])
    # a profile that already has a pole: nothing given, poleKit=1
    Life.CRASH_AT = JInt(0)
    R3.remove("poleKit")
    LL.save("p3", R3)
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PR3, inv3, True)
    K.check(str(LL.reg("p3").getProperty("poleKit")) == "1" and len([x for x in lls(cs3, "p3") if x[2] == int(LL.POLE)]) == 1,
            "P a profile that already has its pole: nothing given, poleKit=1")
    # FIX ROUND (safety critic 2): the registry reached the disk, the pole never did (never seen, not in the inventory) -> given again, once
    U5 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000e5")
    L["PKEY"][str(U5)] = "p5"
    PR5 = L["mkpr"](U5, "Fifth")
    skills(u=U5, Mining=4, Foraging=4, Farming=4, Fishing=4)
    inv5r, cs5r = mkinv()
    Life.sweep(PR5, inv5r, True)
    R5 = LL.reg("p5")
    u5a = str(R5.getProperty("pole.uid"))
    for x in [x for x in lls(cs5r, "p5") if x[2] == int(LL.POLE)]:
        cs5r[x[0]].removeItemStackFromSlot(JShort(x[1]))
    R5.remove("pole.seen")
    LL.save("p5", R5)
    LL.REG.clear()
    LL.LAST.clear()
    logs()
    Life.sweep(PR5, inv5r, True)
    R5 = LL.reg("p5")
    p5 = [x for x in lls(cs5r, "p5") if x[2] == int(LL.POLE)]
    lg5 = [x for x in logs() if "LL-POLEKIT-REDO" in x]
    K.check(len(p5) == 1 and str(R5.getProperty("pole.uid")) != u5a and p5[0][3] == str(R5.getProperty("pole.uid")) and str(R5.getProperty("poleKit")) == "1" and lg5,
            "P (fix round) the kit's pole never arrived (registry on disk, never seen, not carried) -> LL-POLEKIT-REDO gives ONE new pole: %s" % lg5[:1])
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PR5, inv5r, True)
    eq(len([x for x in lls(cs5r, "p5") if x[2] == int(LL.POLE)]), 1, "P (fix round) ... and the next look gives nothing more")
    # lifelong.poleKit off: nothing
    br.put("gear:fn:poleRule", P("GearLLFn")(JInt(5)))          # what the plugin's setup publishes
    apply(lifelong__poleKit="false")
    U4 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000d4")
    L["PKEY"][str(U4)] = "p4"
    PR4 = L["mkpr"](U4, "Fourth")
    inv4, cs4 = mkinv()
    Life.sweep(PR4, inv4, True)
    K.check(not [x for x in lls(cs4, "p4") if x[2] == int(LL.POLE)] and LL.reg("p4").getProperty("pole.uid") is None, "P lifelong.poleKit off = no pole given")
    eq(bool(br.get("gear:fn:poleRule").apply(None)), False, "P gear:fn:poleRule = FALSE while poleKit is off")
    apply()
    eq(bool(br.get("gear:fn:poleRule").apply(None)), True, "P gear:fn:poleRule = TRUE (lifelong tools + poleKit + noCraft)")
    # the bench (SkyyFishing 0.1.7) with the rule: the Wooden rod is locked + refused; the Copper reel needs no Wooden Reel
    FD = JClass("com.skyy.fishing.FishDefs")
    FBn = JClass("com.skyy.fishing.FishBench")
    outs = [str(x) for x in FD.R_OUT]
    r0 = outs.index("SkyyFishing_Rod_Bamboo")
    rc = outs.index("SkyyFishing_Reel_Copper")
    K.check(int(FBn.gate(U1, "p1", JInt(r0))) == 3 and str(FBn.lockTag(U1, "p1", JInt(r0))) == "Your pole: /pole" and "SkyyFishing_Reel_Bamboo" not in outs
            and str(FD.R_PREV[rc]) == "", "P the bench: Wooden rod locked ('Your pole: /pole'), no Wooden Reel recipe, the Copper Reel consumes no Wooden Reel")
    inv5, cs5 = mkinv()
    cs5["storage"].setItemStackForSlot(JShort(0), stack("Ingredient_Stick", 20))
    cs5["storage"].setItemStackForSlot(JShort(1), stack("Ingredient_Fibre", 20))
    msg = str(FBn.craft(cs5["storage"], U1, "p1", JInt(r0)))
    K.check(msg.startswith("-Every player has ONE fishing pole") and ids(cs5).get("Ingredient_Stick") == 20, "P crafting the Wooden rod is refused, nothing used: %s" % msg[:90])

    # ============================================================== U: the Upgrade tab
    FPM = JClass(FAKE_PKG + ".FakePM10")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    ref, st, ch, pl = world(inv, cs, PR1)
    pm_field = None
    k_ = PLA.class_
    while k_ is not None and pm_field is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PMC.class_:
                f_.setAccessible(True)
                pm_field = f_
        k_ = k_.getSuperclass()
    pm_field.set(pl, us.allocateInstance(FPM.class_))
    jf(PRc, "entity").set(PR1, ref)
    ALIGN, LAYOUTS, ELEM_RE, strip_q = H39["ALIGN"], H39["LAYOUTS"], H39["ELEM_RE"], H39["strip_q"]
    rendered = []

    def cmds(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("type", "selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            out_.append(vals)
        return out_

    def evd(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            got = ""
            for f_ in ("data", "eventData"):
                try:
                    v_ = getattr(e_, f_)
                    if v_ is not None:
                        got = str(v_)
                        break
                except Exception:
                    pass
            out_.append(got or str(e_))
        return out_

    def sels(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            try:
                out_.append(str(getattr(e_, "selector")))
            except Exception:
                out_.append(None)
        return out_

    def validate(cl, ev):
        probs, known = [], set()
        for v in cl:
            t_ = v["text"] if v["text"] and "{" in v["text"] else (v["data"] if v["data"] and "{" in v["data"] else None)
            if t_ is not None and "Set" not in (v["type"] or ""):
                sel = v["selector"]
                if sel not in (None, "None", "") and sel.lstrip("#") not in known:
                    probs.append("append into #%s before it exists" % sel)
                try:
                    SUI.check_markup(t_, kit_paths=False)
                except ValueError as e_:
                    probs.append("kit: " + str(e_)[:160])
                if Ui.bad(t_) is not None:
                    probs.append("GearUi.bad: %s" % Ui.bad(t_))
                bare = strip_q(t_)
                for m_ in re.finditer(r"(Horizontal|Vertical)Alignment:\s*(\w+)", bare):
                    if m_.group(2) not in ALIGN:
                        probs.append("%sAlignment %s" % (m_.group(1), m_.group(2)))
                for m_ in re.finditer(r'ItemId: "([^"]*)"', t_):
                    if ITEM.getAssetMap().getAsset(m_.group(1)) is None:
                        probs.append("ItemId %s is no item" % m_.group(1))
                for m_ in ELEM_RE.finditer(bare):
                    if m_.group(2):
                        if m_.group(2) in known:
                            probs.append("#%s created twice" % m_.group(2))
                        known.add(m_.group(2))
            elif v["selector"] and "." in v["selector"]:
                tid = v["selector"].lstrip("#").split(".")[0]
                if tid not in known:
                    probs.append("set on #%s which does not exist" % tid)
        for e_ in ev:
            if e_ and e_.lstrip("#") not in known:
                probs.append("event on %s which does not exist" % e_)
        return probs

    def render(pg_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(ref, ub_, ue_, st)
        cl, ev = cmds(ub_), sels(ue_)
        rendered.append((cl, ev))
        txt = chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl)
        return txt, cl, ev, evd(ue_)

    def click(pg_, data):
        p0, c0 = int(FPM.packets), int(FPM.closes)
        pg_.handleDataEvent(ref, st, data)
        return int(FPM.packets) - p0 + int(FPM.closes) - c0
    skills(Mining=4)
    up = P("UpgPage")(PR1)
    FPM.cur = up
    txt, cl, ev, ed = render(up)
    tabs = re.findall(r"#SkyyGTab(\d)", txt)
    K.check(tabs == ["3", "0", "5", "4", "6"] and "Upgrade" in txt, "U the tab row: Craft | Anvil | Identify | Tools | Upgrade (mode 6): %s" % tabs)
    tok = int(up.tok)
    rows = [list(r_) for r_ in up.rows]
    first = [str(x) if x is not None else None for x in up.rows.get(0)] if up.rows.size() > 0 else []
    K.check(len(first) > 2 and first[2] == "Tool_Pickaxe_Crude" and "T1 Crude -> T2 Copper: " in txt and "(0 / 25)" in txt and "You need Mining" in txt
            and ("up:0:%d" % tok) in " ".join(ed), "U the list: the lifelong pickaxe first, 'T1 Crude -> T2 Copper: <Copper Pickaxe>', '25 <Copper Ingot> (0 / 25) - You need Mining ...', a Tier up button with this build's token: %s | %s | %s"
            % (first, [l for l in txt.split(chr(10)) if "SkyyGURow0" in l and ".Text" in l][:3], [e for e in ed if "up:" in e][:2]))
    n_up = len([e for e in ed if e.startswith("{") and "up:" in e or "up:" in e])
    K.check("Fishing Bench" in txt or "/pole brings it back" in txt, "U the pole row is listed")
    UP_ = P("UpgPage")
    K.check(str(UP_.tierTag("SkyyFishing_Rod_Bamboo")) == "T1 Crude" and str(UP_.tierTag("SkyyFishing_Rod_Iron")) == "T3 Iron"
            and str(UP_.poleNext("SkyyFishing_Rod_Bamboo")) == "SkyyFishing_Rod_Copper" and UP_.poleNext("SkyyFishing_Rod_Iron") is None,
            "U (fix round) the pole's tiers: Wooden = T1 Crude -> Copper, Iron = T3 Iron, the top")
    prow = [l for l in txt.split(chr(10)) if "A.Text" in l and "T1 Crude -> T2 Copper: " in l and ("Fishing Rod" in l or "Rod_Copper" in l or "Rod Copper" in l)]
    K.check(len(prow) == 1, "U (fix round) the pole row reads 'T1 Crude -> T2 Copper: <Copper Fishing Rod>': %s" % prow)
    a0 = click(up, '{"a":"up:0:%d"}' % tok)
    K.check(a0 == 1 and str(up.info).startswith("-") and ids(cs).get("Tool_Pickaxe_Crude", 0) >= 1, "U Tier up without ingots: refused (nothing used), answered once: %s" % up.info)
    cs["storage"].setItemStackForSlot(JShort(20), stack("Ingredient_Bar_Copper", 30))
    skills(Mining=30)
    click(up, '{"a":"refresh"}')
    txt2, cl2, ev2, ed2 = render(up)
    tok2 = int(up.tok)
    i_p = [i for i in range(int(up.rows.size())) if up.rows.get(i)[0] is not None and str(up.rows.get(i)[2]) == "Tool_Pickaxe_Crude"][0]
    ans = [click(up, '{"a":"up:%d:%d"}' % (i_p, tok2)) for _ in range(3)]
    K.check(ans == [1, 1, 1] and ids(cs).get("Tool_Pickaxe_Copper", 0) == 1 and ids(cs).get("Ingredient_Bar_Copper", 0) == 5 and str(up.info).startswith("+"),
            "U Tier up with 30 ingots + Mining 30: the pickaxe is a Copper Pickaxe, 25 ingots used ONCE for 3 clicks of the same token, each answered: %s %s / %s"
            % (ans, ids(cs).get("Ingredient_Bar_Copper"), up.info))
    LL.LAST.clear()
    Life.sweep(PR1, inv, True)          # the stamp scan after the inventory change
    eq(str(LL.reg(pk).getProperty("pickaxe.id")), "Tool_Pickaxe_Copper", "U ... and stays your lifelong pickaxe (the next look writes the registry)")
    for d_ in (None, "{}", '{"a":""}', '{"a":"zzz"}', '{"a":"up:x:y"}', '{"a":"up:99:1"}', '{"a":"pg:1"}', '{"a":"pg:-1"}', '{"a":"mode:9"}',
               '{"a":"rq:x:y"}', '{"a":"rq:99:1"}'):
        eq(click(up, d_), 1, "U a stray click %s is answered once" % d_)
    # FIX ROUND (critic 3.1): gear IN Requip is listed (Take out = wardrobe:fn:fetch, token-guarded), then it tiers up from the inventory
    RQ = [["eq1", "Tool_Pickaxe_Crude"]]
    FETCH = []

    @JImplements("java.util.function.Function")
    class RqList(object):
        @JOverride
        def apply(self, o):
            if str(o[1]) != "items":
                return JArray(JObject)([])
            return JArray(JObject)([JArray(JObject)([JString(a_), JString(b_)]) for a_, b_ in RQ])

    @JImplements("java.util.function.Function")
    class RqFetch(object):
        @JOverride
        def apply(self, o):
            FETCH.append(str(o[1]))
            m_ = [x for x in RQ if x[0] == str(o[1])]
            if not m_:
                return JString("That item is not in your Requip.")
            RQ.remove(m_[0])
            cs["storage"].setItemStackForSlot(JShort(24), stack(m_[0][1]))
            return JString("ok")
    br.put("wardrobe:fn:list", RqList())
    br.put("wardrobe:fn:fetch", RqFetch())
    up.rqAt = JLong(0)
    up.rq = None
    up.pageNo = JInt(0)
    render(up)
    i_rq = [i for i in range(int(up.rows.size())) if str(up.rows.get(i)[0]) == "rq"]
    up.pageNo = JInt(i_rq[0] // 6 if i_rq else 0)
    txr, clr, evr, edr = render(up)
    tokr = int(up.tok)
    K.check(len(i_rq) == 1 and "In Requip: take it out to tier it up" in txr and "Take out" in txr and ("rq:%d:%d" % (i_rq[0], tokr)) in " ".join(edr)
            and "1 in Requip" in txr, "U (fix round) gear IN Requip is listed: tier line, cost, 'In Requip: take it out', a Take out button with this build's token: %s"
            % [l for l in txr.split(chr(10)) if "In Requip" in l][:2])
    n_pick = ids(cs).get("Tool_Pickaxe_Crude", 0)
    ansr = [click(up, '{"a":"rq:%d:%d"}' % (i_rq[0], tokr)) for _ in range(2)] if i_rq else []
    K.check(ansr == [1, 1] and FETCH == ["eq1"] and ids(cs).get("Tool_Pickaxe_Crude", 0) == n_pick + 1 and str(up.info).startswith("="),
            "U (fix round) Take out: fetched ONCE for two clicks of the same token (each answered), the item is in the inventory: %s %s %s" % (ansr, FETCH, up.info))
    up.pageNo = JInt(0)
    render(up)
    K.check(not [i for i in range(int(up.rows.size())) if str(up.rows.get(i)[0]) == "rq"]
            and len([i for i in range(int(up.rows.size())) if up.rows.get(i)[0] is not None and str(up.rows.get(i)[0]) != "rq" and str(up.rows.get(i)[2]) == "Tool_Pickaxe_Crude"]) >= 1,
            "U (fix round) ... the Requip row is gone and the item is a normal Tier up row now")
    br.remove("wardrobe:fn:list")
    br.remove("wardrobe:fn:fetch")
    # FIX ROUND 2 (critic: "lifelong tools first"): the pole / not-on-you lifelong rows come before armor and the rest; the header counts them
    cs["storage"].setItemStackForSlot(JShort(27), stack("Armor_Copper_Head"))
    cs["storage"].setItemStackForSlot(JShort(28), stack("Armor_Copper_Chest"))
    up.pageNo = JInt(0)
    txa = render(up)[0]
    rws = [up.rows.get(i) for i in range(int(up.rows.size()))]
    i_ll = [i for i, e_ in enumerate(rws) if e_[0] is None]
    i_ar = [i for i, e_ in enumerate(rws) if e_[0] is not None and str(e_[0]) != "rq" and int(e_[4]) >= 1]
    hd = [l for l in txa.split(chr(10)) if "SkyyGUHead.Text" in l]
    K.check(i_ll and i_ar and max(i_ll) < min(i_ar) and hd and "on you" in hd[0],
            "U (fix round 2) the pole / lifelong rows %s come before the armor rows %s; header %s" % (i_ll, i_ar, hd[:1]))
    n_on = len([e_ for e_ in rws if (e_[0] is not None and str(e_[0]) != "rq") or (e_[0] is None and str(e_[2]) == "here")])
    K.check(hd and ("(%d on you" % n_on) in hd[0], "U (fix round 2) the header counts the pole on you too: %d - %s" % (n_on, hd[:1]))
    cs["storage"].setItemStackForSlot(JShort(27), None)
    cs["storage"].setItemStackForSlot(JShort(28), None)
    lp = P("LifePage")(PR1)
    FPM.cur = lp
    txl = render(lp)[0]
    K.check("#SkyyGTab6" in txl, "U the Tools tab shows the Upgrade tab too")
    eq(click(lp, '{"a":"mode:6"}'), 1, "U mode:6 on the Tools page is handled (opens /upgrade) and answered")
    FPM.last = None
    try:
        m_ = [m for m in P("UpCmd").class_.getDeclaredMethods() if str(m.getName()) == "execute"][0]
        m_.setAccessible(True)
        m_.invoke(P("UpCmd")(), JArray(JObject)([None, st, ref, PR1, None]))
    except Exception as e_:
        K.notes.append("UpCmd.execute: %s" % str(e_)[:120])
    K.check(FPM.last is not None and str(FPM.last.getClass().getName()).endswith("UpgPage"), "U /upgrade opens the Upgrade tab")
    apply(smith__upgradeTab="false")
    FPM.cur = up
    txo = render(up)[0]
    K.check("#SkyyGTab6" not in txo, "U smith.upgradeTab off: no Upgrade tab in the row")
    apply()
    probs = []
    for cl_, ev_ in rendered:
        probs += validate(cl_, ev_)
    K.check(not probs, "U every page rendered (%d) validates: %s" % (len(rendered), probs[:4]))
    K.notes.append("H311 logs: %s" % [x[:160] for x in logs() if "WARN" in x][:6])


# ====================================================================================================== LIVE: start twice on a live copy
LIVE_GEAR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")          # the deploy world (read only - copied)


def run_live311(out):
    from jpype import JClass
    K = H["Child"](out)
    H["_jvm"]([B.SERVER_JAR, JAR], verify=True)
    home = os.path.join(SCRATCH, "live311", "Skyy_SkyyGear")
    shutil.rmtree(os.path.dirname(home), ignore_errors=True)
    os.makedirs(home)
    for f_ in ("config.properties", "quality.properties"):
        if os.path.isfile(os.path.join(LIVE_GEAR, f_)):
            shutil.copyfile(os.path.join(LIVE_GEAR, f_), os.path.join(home, f_))
    shutil.copytree(os.path.join(LIVE_GEAR, "lifelong"), os.path.join(home, "lifelong"))
    Cfg = JClass(PKG + "GearCfg")
    LL = JClass(PKG + "GearLL")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Paths.get(os.path.join(home, "gear.log"))
    JClass(PKG + "GearQual").load(Paths.get(os.path.join(home, "quality.properties")))
    before = open(os.path.join(home, "config.properties"), "rb").read()
    regs0 = dict((f_, open(os.path.join(home, "lifelong", f_), "rb").read()) for f_ in os.listdir(os.path.join(home, "lifelong")))
    for step in (1, 2):
        Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(home, "no-SkyyRolls", "reforge.properties")))
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218", "migrate031"):
            getattr(Cfg, m)()
        Cfg.load()
        JClass(PKG + "GearSickle").ensure()
        after = open(os.path.join(home, "config.properties"), "rb").read()
        K.check(after == before, "LIVE start %d: the live config.properties copy is byte-identical (the 0.3.11 rows need no one-time update)" % step)
        K.check(bool(Cfg.SICKLE_ON) and int(Cfg.STICK_KEEP) == 50 and bool(Cfg.LL_POLEKIT) and bool(Cfg.UPG_TAB) and float(Cfg.SICKLE_FIB) == 60.0
                and str(Cfg.SICKLE_SW) == "1,1,2,2,3,3,4,4" and str(Cfg.SICKLE_MAX) == "24,24,40,40,60,60,80,80" and int(Cfg.SICKLE_LAY) == 1
                and str(Cfg.SICKLE_STK) == "Plant_Bush,Plant_Bramble", "LIVE start %d: the new rows read their defaults from a file without them" % step)
    txt = before.decode("utf-8", "replace")
    K.check("sickle." not in txt and "sticks." not in txt and "poleKit" not in txt, "LIVE the live file has none of the new keys (defaults apply)")
    poles = []
    for f_ in sorted(os.listdir(os.path.join(home, "lifelong"))):
        P_ = LL.reg(f_[:-len(".properties")])
        poles.append((f_[:12], P_.getProperty("pole.uid") is not None, str(P_.getProperty("migrated"))))
    K.check(all(open(os.path.join(home, "lifelong", f_), "rb").read() == b_ for f_, b_ in regs0.items()), "LIVE the registries were read, not rewritten")
    K.notes.append("LIVE profiles (file, has a pole already, migrated): %s - a profile without a pole gets one at its next join" % poles)
    K.save()


# ====================================================================================================== main
def child(env, *args):
    cmd = [sys.executable] + ([RUNNER] if os.path.isfile(RUNNER) else []) + [os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--root", SCR_ROOT]
    return subprocess.run(cmd, env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        w = [why for pre, why in WAIVE if str(f).startswith(pre)]
        if w:
            WAIVED.append("%s: %s (%s)" % (label, str(f)[:140], w[0]))
            continue
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, str(n)[:500]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H310["run_mkfake10"](arg("--mkfake"))), ("--h311", lambda: run_h311(arg("--out"))),
                     ("--live311", lambda: run_live311(arg("--out"))),
                     ("--h310", lambda: H310["run_h310"](arg("--out"))),
                     ("--life", lambda: H35["run_life"](arg("--out"))),
                     ("--verify", lambda: H["run_verify"](arg("--out"))), ("--h39", lambda: H39["run_h39"](arg("--out"))),
                     ("--h38", lambda: H38["run_h38"](arg("--out"))), ("--h37", lambda: H37["run_h37"](arg("--out"))),
                     ("--g36", lambda: H36["run_g36"](arg("--out"))), ("--snd", lambda: H36["run_snd"](arg("--out"))),
                     ("--till", lambda: H35["run_till"](arg("--out"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
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
    for f_ in (JAR, J310, FI7_SRC, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
        assert os.path.isfile(f_), f_
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    shutil.copyfile(H35["CO_SRC"], H36["CO_JAR"])
    shutil.copyfile(H36["FI6_SRC"], H36["FI_JAR"])
    for f_ in glob.glob(os.path.join(H35["LIVE_PLAYERS"], "*.json")):
        shutil.copyfile(f_, os.path.join(SCRATCH, "players", os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    env_old = dict(env)
    env_old["JAVA_TOOL_OPTIONS"] = env["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noPoleKit=true"
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets311()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        # the older children first (they share the scratch home with H311: H311's profiles would change their baseline), H311 after L35
        for label, flag in (("h310", "--h310"), ("h39", "--h39"), ("verify", "--verify"), ("h38", "--h38"), ("h37", "--h37"),
                            ("g36", "--g36"), ("snd", "--snd"), ("till", "--till")):
            if not want(label):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env_old, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if want("life"):
            _why39 = "0.3.9 by design: Identify moved to the Identify tab; the 0.3.5 check clicks it on the Anvil tab (H39 I covers the reveal)"
            H37["L37_EXTRA"].extend([("G35 R1:", _why39), ("G35 R2:", _why39), ("G35 R3:", _why39), ("G35 R4", _why39), ("G35 R5:", _why39)])
            H37["L37_EXTRA"].append(("G35 P6:", "0.3.11 fix round by design: with the kit off /pole says 'You have no lifelong fishing pole - this server hands none out (lifelong.poleKit is off). A pole a quest gave you: hold it and type /lifelong.' (no Marlow pole since SkyyQuests 0.3.4); the exact-copy half is unchanged"))
            H37["L37_EXTRA"].append(("G35 P7 FIX 2", "0.3.11 fix round by design: the refusal reads 'Only a fishing pole a quest gave you can become your lifelong pole' (no Marlow pole since SkyyQuests 0.3.4); still refused, nothing written"))
            n0 = len(H37["FAILS"])
            H37["run_l35"](env_old)
            for f_ in H37["FAILS"][n0:]:
                w = [why for pre, why in WAIVE if str(f_).startswith(pre)]
                if w:
                    WAIVED.append("L35: %s (%s)" % (str(f_)[:140], w[0]))
                else:
                    FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        if want("h311"):
            out = os.path.join(SCRATCH, "h311.json")
            pr = child(env, "--h311", "--out", out)
            check(pr.returncode == 0, "h311: the child exited cleanly (%s)" % pr.returncode)
            take(out, "h311")
        if want("live"):
            out = os.path.join(SCRATCH, "live311.json")
            pr = child(env, "--live311", "--out", out)
            check(pr.returncode == 0, "live311: the child exited cleanly (%s)" % pr.returncode)
            take(out, "live311")
        if want("audit"):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env_old, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s), %d waived (by design)" % (VERSION, OKS[0], len(FAILS), len(WAIVED)))
    for w in WAIVED:
        print("WAIVED:", w)
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
