"""Harness for SkyyGear 0.3.14 (tools/gear_0_3_14_patch.py header) = the 0.3.13 harness's children run on the 0.3.14 jar (with the harness seam
-Dskyy.harness.no314=true = the 0.3.13 flow they were written for) + H314 + LIVE314:
    python tools/gear_0_3_14_patch.py && python SkyyGear/build_skyygear_0.3.14.py
    python SkyyGear/test_skyygear_0.3.14.py [--keep] [--only assets,h314,live314,h313,live313,h312,live,h311,h310,h39,verify,h38,h37,g36,snd,till,life,audit]

  S314 the jar 0.3.13 -> 0.3.14: only the 6 new classes + the SkyyGear_Harvest_Crop interaction are new, nothing gone, changed non-class files =
       manifest.json + server.lang (the 4 Harvester + the Mythic Sigil descriptions) + the 4 Harvester items (their swing vars); class compare
  H314 ONE booted engine (the 0.3.5 life setup, SkyyGearHarvest registered like setup() does) + SkyyFishing 0.1.7 + SkyyCollections 0.2.20:
       A  ROWS + migrate0314: the 11 rows, the fresh file block + marker, the defaults; h4Update on texts (old default rewritten, CRLF kept, hand
          edits kept + noted, a later entry wins, the marker = run once); migrate0314 on a scratch file twice (History copy, change-log rows)
       B  THE KIT: a fresh profile gets pickaxe, hatchet, the CRUDE HARVESTER, the can - no hoe; harv=1 / harvAuto=kit; no hoe row; /hoe and
          /sickle explain + answer for the Harvester; a profile switch gets its own kit
       C  THE MERGE: an old hoe (Copper, a line, Fortune 3) + sickle (Crude, a line, Wisdom 2) -> ONE Copper Harvester (the sickle's uid), both
          lines (more than the rarity's count), points NOT trimmed, harvAuto=1, History copy = the registry's bytes before, the undo record,
          gear.log; run twice = nothing more; crashes at 41 / 42 / 43 finish at the next look; the hoe away -> its SNAPSHOT (the physical one
          retired when it turns up); the hoe in Requip -> fetched, then merged, Requip told; UNDO gives the hoe + sickle back (same uids; a
          snapshot hoe under a new uid in the old one's family), harvAuto=undone, never merged again; undo crashes at 44 / 45 resume
       D  THE SWEEP TIER: decideI (Crude = T1 on crops, the Harvester's own top), farmTier, fullT, onlyFor2; GearHarv.swing (same tier =
          vanilla harvest, one up = ONE per swing, two up = skipped + popup, a plant = vanilla); GearHarvCrop's Failed path; farm.crudeT1 off =
          the 0.3.13 answers; the interaction asset loads as a GearHarvCrop
       E  SIGILS: a Mining Set piece takes a Rare / Mythic Sigil (set field kept, still counts for the full set, reforgeable, a Mythic one
          tiers up); gathering armor still refused; role words / zones / the rolls (statistics); GearSigDrop.mob end to end (stand-in chunk:
          boss / mini / mob / twice / Creative / no killer / no level / drops off); the bag lists wrapped (GearSigBag, with GearNormDrop /
          GearStick around it), rolls add Sigils, other lists never, off = the raw containers back
       F  TILL: hoe.areaElsewhere on = a non-island world tills the ring (GearTill.allowed)
  LIVE314 a scratch copy of the live NewBetaTest Gear data, the start's migrations twice: hoe.areaElsewhere + sigil.mythicUse false -> true
       once (only those value texts + the marker line change), History copy, change-log rows; the second start changes nothing; the live
       registries (read only): which profiles merge at their next look
Scratch: tools/dev/scratch/farm01/harness (deleted at the end unless --keep). Exit code 1 on any failure.
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


VERSION = "0.3.14"
V313 = "0.3.13"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "farm01")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J313 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V313))                       # read only
PKG = "com.skyy.gear."
NEW_CLASSES = ["GearHarv", "GearHarvCrop", "GearHarvSup", "GearSigDrop", "GearSigBag", "GearHarvCmd"]
HARV_IDS = ["Tool_Sickle_Harvester_" + t for t in ("Crude", "Copper", "Iron", "Thorium")]

# ---- the 0.3.13 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H313 = os.path.join(HERE, "test_skyygear_0.3.13.py")
_T313 = open(_H313, encoding="utf-8").read()
_cut = _T313.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H313, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H313 = {"__name__": "skyygear_h313", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T313[:_cut], _H313 + " (library)", "exec"), H313)
sys.argv = _argv
H312, H311, H310, H39, H38, H37, H36, H35, H = (H313["H312"], H313["H311"], H313["H310"], H313["H39"], H313["H38"], H313["H37"], H313["H36"],
                                                H313["H35"], H313["H"])
FAKE_DIR = H313["FAKE_DIR"]
FI7_SRC = H313["FI7_SRC"]
CO20 = H313["CO20"]
LIVE_GEAR = H313["LIVE_GEAR"]
FAILS, OKS = [], [0]
WAIVE = list(H313["WAIVE"])
WAIVED = []
WAIVE.append(("L35: every 0.3.5 life check passes on 0.3.7 (289 ok) except the explained deviations: unexpected []",
              "every L35 check that ran passed or is an explained deviation (unexpected []); only the old >= 300 count (0.3.13 ran 292 - three more checks are explained 0.3.14 deviations: G34 S1, FIX2 M1, G34 S2 = the two default flips)"))
WAIVE.append(("A: no load record about the cans / Harvesters / the interaction", "0.3.14 by design: the Harvesters carry their own swing InteractionVars (HitBlock = SkyyGear_Harvest_Crop); a bare boot loads no vanilla interactions, so their vanilla Parents ('Sickle_Swing_*') are 'not found' there exactly like the vanilla sickles' own vars - H314 D checks every other record"))

# every engine boot of every child also registers SkyyGearHarvest (what the plugin's setup() does in the game; without it the jar's
# SkyyGear_Harvest_Crop would be an unknown Type in a bare boot). The 0.3.12 wrapper (SkyyGearCan) runs inside.
_BOOT_312 = H["engine_boot"]


def engine_boot_314(K):
    from jpype import JClass
    try:
        INTc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
        GHC = JClass(PKG + "GearHarvCrop")
        INTc.CODEC.register("SkyyGearHarvest", GHC.class_, GHC.codec())
        GHC.REG = True
    except Exception as e:
        K.notes.append("engine_boot_314: the SkyyGearHarvest type could not be registered: %s" % str(e)[:200])
    return _BOOT_312(K)


for _d in (H, H35.get("H"), H36.get("H"), H37.get("H"), H38.get("H")):
    if isinstance(_d, dict) and "engine_boot" in _d:
        _d["engine_boot"] = engine_boot_314


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S314
def run_assets314():
    ea, eb = entries(J313), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    want_add = set("com/skyy/gear/%s.class" % c for c in NEW_CLASSES) | {"Server/Item/Interactions/SkyyGear/Harvester/SkyyGear_Harvest_Crop.json"}
    want_chg = sorted(["manifest.json", "Server/Languages/en-US/server.lang"] + ["Server/Item/Items/SkyyGear/%s.json" % h for h in HARV_IDS])
    check(set(added) == want_add and not gone and changed == want_chg,
          "S314: 0.3.13 -> 0.3.14 adds exactly the 6 classes + the interaction, removes nothing, changes only the manifest / lang / 4 Harvesters: "
          "extra %s, missing %s, gone %s, changed %s" % (sorted(set(added) - want_add)[:4], sorted(want_add - set(added))[:4], gone[:3], changed))
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.14"' in man and "ONE FARMING TOOL" in man and "Mining Set" in man, "S314: the manifest names the round")
    ij = json.loads(eb["Server/Item/Interactions/SkyyGear/Harvester/SkyyGear_Harvest_Crop.json"])
    check(ij == {"Type": "SkyyGearHarvest", "RequireNotBroken": True, "Failed": "Block_Break_Adventure"},
          "S314: SkyyGear_Harvest_Crop = type SkyyGearHarvest, vanilla's RequireNotBroken + Failed path, NO durability step: %s" % ij)
    bad = []
    for h in HARV_IDS:
        a_, b_ = json.loads(ea["Server/Item/Items/SkyyGear/%s.json" % h]), json.loads(eb["Server/Item/Items/SkyyGear/%s.json" % h])
        iv = b_.get("InteractionVars", {})
        b2 = dict(b_)
        b2.pop("InteractionVars", None)
        ok = b2 == a_ and len(iv) >= 6
        for side in ("Left", "Right"):
            ent = iv.get("Swing_%s_Selector" % side, {}).get("Interactions", [{}])
            ok = ok and ent[0].get("Parent") == "Sickle_Swing_%s_Selector" % side and ent[0].get("HitBlock") == {"Interactions": ["SkyyGear_Harvest_Crop"]}
        ok = ok and iv.get("Swing_Left_Effect") is not None and iv.get("Swing_Right_Damage") is not None
        if not ok:
            bad.append(h)
    check(not bad, "S314: each Harvester = its 0.3.13 JSON + the base sickle's InteractionVars with both swing selectors' HitBlock = ours: bad %s" % bad)
    la, lb = ea["Server/Languages/en-US/server.lang"].decode("utf-8").split("\n"), eb["Server/Languages/en-US/server.lang"].decode("utf-8").split("\n")
    gone_l = [l_ for l_ in la if l_ not in lb]
    new_l = [l_ for l_ in lb if l_ not in la]
    check(len(gone_l) == 5 and len(new_l) == 5 and all(l_.split(" = ")[0] in [g.split(" = ")[0] for g in gone_l] for l_ in new_l)
          and any("Skyy_Sigil_Mythic.description = A boss treasure: raises an item to Mythic" in l_ for l_ in new_l)
          and all(l_.split(" = ")[1].startswith(("T1 Crude - ", "T2 Copper - ", "T3 Iron - ", "T4 Thorium - ")) for l_ in new_l if "Harvester" in l_),
          "S314: server.lang changes exactly the 4 Harvester descriptions (tier tag first) + the Mythic Sigil one: %s" % new_l)
    ca = set(n for n in ea if n.endswith(".class"))
    cb = set(n for n in eb if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca & cb if ea[n] != eb[n])
    print("  class compare 0.3.13 -> 0.3.14: %d classes, %d changed (%s), new %s, gone %s"
          % (len(cb), len(chg), ", ".join(chg), sorted(n.rsplit("/", 1)[1][:-6] for n in cb - ca), sorted(ca - cb)))
    want_c = {"GearLL", "GearCfg", "GearLife", "GearSigil", "ReforgePage", "GearArmLv", "GearTool", "LifePage", "GearCmd", "HarvCmd", "GearDeathMark",
              "GearNorm", "SkyyGearPlugin", "GearBye"}
    check(set(chg) <= want_c | set(n for n in chg if n.startswith("Cfg")), "S314: only the expected classes changed: unexpected %s" % sorted(set(chg) - want_c))


# ====================================================================================================== H314
def run_h314(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    if os.path.isfile(CO20):
        co = os.path.join(SCRATCH, "packs", "SkyyCollections-0.2.20.jar")
        shutil.copyfile(CO20, co)
        H36["CO_JAR"] = co
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h314(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H314: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h314(L, K):
    from jpype import JClass, JInt, JShort, JLong, JDouble, JObject, JArray, JString, JImplements, JOverride, JBoolean
    br, Gear, Cfg, LL, Life, Up, Data, Stamp = L["br"], L["Gear"], L["Cfg"], L["LL"], L["Life"], L["Up"], L["Data"], L["Stamp"]
    mkinv, PR1, U1, stack, doc, skills, apply, logs, lls, ids = (L["mkinv"], L["PR1"], L["U1"], L["stack"], L["doc"], L["skills"], L["apply"], L["logs"],
                                                                 L["lls"], L["ids"])
    ITEM, E, HOME, PKEY, mkpr, world, said, us, jf = L["ITEM"], L["E"], L["HOME"], L["PKEY"], L["mkpr"], L["world"], L["said"], L["us"], L["jf"]
    P = lambda n: JClass(PKG + n)
    Harv, Crop, SigD, Sig, Mine, Till, Norm, Defs, Forge, View, ArmLv, GSet, LP = (P("GearHarv"), P("GearHarvCrop"), P("GearSigDrop"), P("GearSigil"),
                                                                                  P("GearMine"), P("GearTill"), P("GearNorm"), P("GearDefs"), P("GearForge"),
                                                                                  P("GearView"), P("GearArmLv"), P("GearSet"), P("LifePage"))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD, BS, BA = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString"), JClass("org.bson.BsonArray")
    HAL = JClass("java.util.ArrayList")
    UUID = JClass("java.util.UUID")
    Long_, Bool_, Integer = JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Integer")
    Paths = JClass("java.nio.file.Paths")
    V3i = JClass("org.joml.Vector3i")

    def kc(cond, what):
        K.check(bool(cond), what)

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))

    def look(pr_, inv_):
        LL.LAST.clear()
        Harv.LASTRUN.clear()
        Life.sweep(pr_, inv_, True)
    apply()

    # ============================================================== A: rows + migrate0314
    CRows = P("CfgRows")
    keys = ["harvester.only", "farm.crudeT1", "sigil.drops", "sigil.mob", "sigil.bag", "sigil.mini", "sigil.boss", "sigil.bossZone", "sigil.miniWords",
            "sigil.bossWords", "sigil.bagLists"]
    kc(all(int(CRows.index(k)) >= 0 and bool(CRows.flag(int(CRows.index(k)), "danger")) for k in keys), "A: the 11 Server Setup rows exist (danger rows)")
    FRESH = L["FRESH"]
    kc("# ---- one farming tool, the sweep tier, Sigil drops (SkyyGear 0.3.14) ----" in FRESH and str(Cfg.H4_MARK_ID) in FRESH and "\nharvester.only=true\n" in FRESH
       and "\nhoe.areaElsewhere=true\n" in FRESH and "\nsigil.mythicUse=true\n" in FRESH and "\nsigil.boss=0,0,6,2,0.5\n" in FRESH,
       "A: a fresh config.properties: the 0.3.14 block + the migrate0314 marker; the two flipped defaults read true")
    kc(bool(Cfg.HARV_ONLY) and bool(Cfg.FARM_T1) and bool(Cfg.SIGD_ON) and bool(Cfg.HOE_ELSE) and bool(Cfg.SIG_MY) and bool(Cfg.MINE_SIG),
       "A: the defaults: one farming tool, Crude = T1, Sigil drops, till everywhere, Mythic Sigil usable, Sigils on Mining Sets")
    t1 = "# head\r\na=1\r\nhoe.areaElsewhere=false\r\nsigil.mythicUse = False\r\nb=2\r\n"
    r1 = Cfg.h4Update(JString(t1))
    o1 = str(r1[0]) if r1 is not None else ""
    kc(r1 is not None and "hoe.areaElsewhere=true\r\n" in o1 and "sigil.mythicUse = true\r\n" in o1 and o1.startswith("# head\r\na=1\r\n") and "b=2\r\n" in o1
       and str(Cfg.H4_MARK) + "\r" in o1 and len(list(r1[3])) == 6 and "hoe.areaElsewhere false -> true" in str(r1[1]),
       "A: h4Update rewrites both old defaults (value text only, CRLF kept), adds the marker at the end, 2 change-log rows: %r" % o1[-160:])
    r2 = Cfg.h4Update(JString("hoe.areaElsewhere=no\nsigil.mythicUse=true\n"))
    o2 = str(r2[0])
    kc("hoe.areaElsewhere=no\n" in o2 and "sigil.mythicUse=true\n" in o2 and len(list(r2[3])) == 0 and len(list(r2[2])) == 2, "A: hand-edited values are kept + noted")
    kc(Cfg.h4Update(JString("x=1\n" + str(Cfg.H4_MARK) + "\n")) is None, "A: the marker = run once (null)")
    r4 = Cfg.h4Update(JString("hoe.areaElsewhere=false\nhoe.areaElsewhere=true\n"))
    kc("hoe.areaElsewhere=false\nhoe.areaElsewhere=true\n" in str(r4[0]) and len(list(r4[3])) == 0, "A: a later entry that is not the old default wins - nothing rewritten")
    cf = os.path.join(SCRATCH, "m314", "config.properties")
    os.makedirs(os.path.dirname(cf), exist_ok=True)
    body = FRESH.replace("hoe.areaElsewhere=true", "hoe.areaElsewhere=false").replace("sigil.mythicUse=true", "sigil.mythicUse=false").replace(str(Cfg.H4_MARK) + "\n", "")
    open(cf, "wb").write(body.replace("\n", "\r\n").encode("ISO-8859-1"))
    oldF = Cfg.FILE
    try:
        Cfg.FILE = Paths.get(cf)
        m1 = str(Cfg.migrate0314())
        b1 = open(cf, "rb").read()
        m2 = str(Cfg.migrate0314())
        b2 = open(cf, "rb").read()
        hist = glob.glob(os.path.join(os.path.dirname(cf), "**", "*"), recursive=True)
        lines_b = body.replace("\n", "\r\n").encode("ISO-8859-1").split(b"\r\n")
        lines_a = b1.split(b"\r\n")
        diff = [(x, y) for x, y in zip(lines_b, lines_a) if x != y and x != b""]
        kc("hoe.areaElsewhere false -> true" in m1 and "sigil.mythicUse false -> true" in m1 and m2 == "" and b1 == b2 and len(lines_a) == len(lines_b) + 1
           and sorted(d[1].decode() for d in diff) == ["hoe.areaElsewhere=true", "sigil.mythicUse=true"] and lines_a[-2].decode() == str(Cfg.H4_MARK) and lines_a[-1] == b"",
           "A: migrate0314 on a file: the two lines -> true (nothing else; the marker last), the second start changes nothing: %s / %s / %s" % (m1[:120], m2, diff[:3]))
        kc(any("config-history" in h_ or "history" in h_.lower() for h_ in hist), "A: a History copy was made (%s)" % [os.path.relpath(h_, os.path.dirname(cf)) for h_ in hist][:6])
    finally:
        Cfg.FILE = oldF

    # ============================================================== B: the kit
    L["wipe_home"]()
    skills(Mining=4, Foraging=4, Farming=4, Fishing=4)
    pk = str(Gear.pkey(U1))
    invB, csB = mkinv()
    look(PR1, invB)
    look(PR1, invB)
    R = LL.reg(pk)
    kinds = sorted(set(x[2] for x in lls(csB, pk)))
    hvB = [x for x in lls(csB, pk) if x[2] == 3]
    kc(2 not in kinds and 0 in kinds and 1 in kinds and 5 in kinds and len(hvB) == 1 and str(hvB[0][6].getItemId()) == "Tool_Sickle_Harvester_Crude"
       and not [i for i in ids(csB) if i.startswith("Tool_Hoe_") or (i.startswith("Tool_Sickle_") and "Harvester" not in i)],
       "B: a fresh profile's kit: pickaxe, hatchet, the CRUDE HARVESTER, the can - no hoe, no sickle: kinds %s, %s" % (kinds, sorted(ids(csB))))
    kc(R.getProperty("hoe.uid") is None and str(R.getProperty("harv")) == "1" and str(R.getProperty("harvAuto")) == "kit" and str(R.getProperty("migrated")) == "1",
       "B: the registry: no hoe, harv=1, harvAuto=kit, migrated=1")
    kc(not bool(LP.shown(JInt(2), R)) and bool(LP.shown(JInt(3), R)), "B: the Tools tab has no hoe row")
    refB, stB, chB, plB = world(invB, csB, PR1)
    rh = str(Life.reclaim(PR1, plB, JInt(2)))
    rs_ = str(Life.reclaim(PR1, plB, JInt(3)))
    kc("Hoes are retired" in rh and "You still have your Harvester" in rh and "sickle (" not in rh, "B: /hoe explains + answers for the Harvester: %s" % rh)
    kc("Sickles are retired" in rs_ and "You still have your Harvester" in rs_, "B: /sickle explains + answers for the Harvester: %s" % rs_)
    PKEY[str(U1)] = "p1x"
    invS, csS = mkinv()
    look(PR1, invS)
    RS = LL.reg("p1x")
    kc(str(RS.getProperty("harvAuto")) == "kit" and [x for x in lls(csS, "p1x") if x[2] == 3 and "Harvester" in str(x[6].getItemId())]
       and str(LL.reg(pk).getProperty("harvAuto")) == "kit", "B: a profile switch: the new profile gets its own Crude Harvester; the first keeps its own")
    PKEY[str(U1)] = "p1"

    # ============================================================== C: the merge
    TM = [int(x) for x in Defs.S_TMASK]
    fl = [str(Defs.S_KEY[i]) for i in range(len(TM)) if TM[i] & (1 << 5)]
    kc(len(fl) >= 2, "C: the sickle family has %d line keys (%s)" % (len(fl), fl))

    def old_profile(u_, pk_, name):
        """a 0.3.13 profile: the hoe + sickle of the one-time migration (harvester.only off while they are given)"""
        PKEY[str(u_)] = pk_
        pr_ = PR1 if str(u_) == str(U1) else mkpr(u_, name)
        skills(u=u_, Mining=4, Foraging=4, Farming=4, Fishing=4)
        apply(harvester__only="false")
        inv_, cs_ = mkinv()
        look(pr_, inv_)
        R_ = LL.reg(pk_)
        hoe_ = [x for x in lls(cs_, pk_) if x[2] == 2][0]
        sic_ = [x for x in lls(cs_, pk_) if x[2] == 3][0]
        hd_ = doc(hoe_[6]).clone()
        hd_.put("r", BS("normal"))
        ms_ = BA()
        ms_.add(Data.mod(JString(fl[0]), JInt(1)))
        hd_.put("mods", ms_)
        cs_[hoe_[0]].setItemStackForSlot(JShort(hoe_[1]), Data.put(Data.carry(stack("Tool_Hoe_Copper"), hoe_[6]), hd_, u_))
        sd_ = doc(sic_[6]).clone()
        sd_.put("r", BS("normal"))
        ms2 = BA()
        ms2.add(Data.mod(JString(fl[1]), JInt(1)))
        sd_.put("mods", ms2)
        cs_[sic_[0]].setItemStackForSlot(JShort(sic_[1]), Data.put(sic_[6], sd_, u_))
        R_.setProperty("hoe.up.fort", "3")
        R_.setProperty("sickle.up.wis", "2")
        LL.save(pk_, R_)
        look(pr_, inv_)
        apply()
        return pr_, inv_, cs_, str(R_.getProperty("hoe.uid")), str(R_.getProperty("sickle.uid"))
    PRC, invC, csC, hoU, siU = old_profile(U1, "pc", "Tester")
    pkc = "pc"
    regbytes = open(os.path.join(HOME, "lifelong", pkc + ".properties"), "rb").read()
    kc(LL.reg(pkc).getProperty("harv") is None and [x for x in lls(csC, pkc) if x[2] == 2], "C: the 0.3.13 profile has its hoe + sickle (not merged yet)")
    cnt_normal = int(Cfg.R_MODS[int(Cfg.ri(JInt(0)))])
    logs()
    look(PRC, invC)
    RC = LL.reg(pkc)
    hvC = [x for x in lls(csC, pkc) if x[2] == 3]
    hdC = doc(hvC[0][6]) if hvC else None
    lg = logs()
    kc(len(hvC) == 1 and str(hvC[0][6].getItemId()) == "Tool_Sickle_Harvester_Copper" and hvC[0][3] == siU and not [x for x in lls(csC, pkc) if x[2] == 2]
       and not [i for i in ids(csC) if i.startswith("Tool_Hoe_")], "C: ONE Copper Harvester (the hoe's higher tier) with the sickle's uid; the hoe is gone")
    mods_ = str(hdC.get("mods")) if hdC is not None else ""
    kc(hdC is not None and fl[0] in mods_ and fl[1] in mods_ and bool(LL.isLL(hdC)) and str(LL.owner(hdC)) == pkc,
       "C: EVERY line of both tools (%s + %s; a Normal tool rolls %d - the manual button would keep %d): %s" % (fl[0], fl[1], cnt_normal, min(2, cnt_normal), mods_))
    kc(str(RC.getProperty("sickle.up.fort")) == "3" and str(RC.getProperty("sickle.up.wis")) == "2" and int(LL.spent(RC, JInt(3))) > int(LL.earned(U1, JInt(3)))
       and int(LL.free(U1, RC, JInt(3))) == 0, "C: the points: Fortune 3 (hoe) + Wisdom 2 (sickle) kept, NOT trimmed (spent %d of %d earned, free 0)"
       % (int(LL.spent(RC, JInt(3))), int(LL.earned(U1, JInt(3)))))
    kc(str(RC.getProperty("harv")) == "1" and str(RC.getProperty("harvAuto")) == "1" and str(RC.getProperty("harvAutoHow")) == "inventory"
       and not [k for k in RC.stringPropertyNames() if str(k).startswith("hoe.")] and str(RC.getProperty("harvHoe")) == hoU and RC.getProperty("harv.pend") is None
       and RC.getProperty("harv.auto") is None, "C: the registry: harv=1, harvAuto=1 (inventory), no hoe.* key, harvHoe = the hoe's uid, no journal")
    hist = sorted(glob.glob(os.path.join(HOME, "harvmerge", "history", pkc + ".properties.*.bak")))
    kc(len(hist) == 1 and open(hist[0], "rb").read() == regbytes, "C: the History copy = the registry's bytes before the merge (%s)" % [os.path.basename(h) for h in hist])
    recf = os.path.join(HOME, "harvmerge", pkc + ".log")
    rec = [l_.split("\t") for l_ in open(recf, encoding="utf-8").read().split("\n") if l_.startswith("MERGE")]
    kc(len(rec) == 1 and len(rec[0]) == 15 and rec[0][2] == siU and rec[0][3] == "Tool_Sickle_Harvester_Copper" and rec[0][4] == hoU and rec[0][5] == "Tool_Hoe_Copper"
       and rec[0][7] == "inventory" and rec[0][8] == "Tool_Sickle_Crude" and rec[0][6] != "-" and rec[0][9] != "-",
       "C: the undo record: MERGE stamp, uids, ids, both stacks' metadata, the History file: %s" % [r_[:9] for r_ in rec])
    kc([x for x in lg if "LL-HARV-AUTO-BEGIN" in x] and [x for x in lg if "LL-HARV-AUTO " in x], "C: gear.log has LL-HARV-AUTO-BEGIN (both documents) + LL-HARV-AUTO")
    kc(any("Hoes and sickles are retired" in s_ for s_ in said(PRC)), "C: the player is told: %s" % said(PRC)[-1:])
    look(PRC, invC)
    LL.REG.clear()
    look(PRC, invC)
    rec2 = [l_ for l_ in open(recf, encoding="utf-8").read().split("\n") if l_.startswith("MERGE")]
    kc(len(rec2) == 1 and len(glob.glob(os.path.join(HOME, "harvmerge", "history", pkc + ".properties.*.bak"))) == 1 and len([x for x in lls(csC, pkc) if x[2] == 3]) == 1,
       "C: run twice (+ a restart): no second merge, record or History copy")
    # C2 the crash paths: a crash after the journal (41), after the hoe left (42), after the Harvester was written (43) -> the next look finishes it
    CR2 = {}
    for step in (41, 42, 43):
        Uc = UUID.fromString("00000000-0000-0000-0000-0000000014%02d" % step)
        PRx, invx, csx, hx, sx = old_profile(Uc, "pcr%d" % step, "Crash%d" % step)
        CR2[step] = (Uc, PRx, invx, csx)
        Life.CRASH_AT = JInt(step)
        look(PRx, invx)
        Life.CRASH_AT = JInt(0)
        pend_ = LL.reg("pcr%d" % step).getProperty("harv.pend")
        LL.REG.clear()
        look(PRx, invx)
        Rx = LL.reg("pcr%d" % step)
        hvs = [x for x in lls(csx, "pcr%d" % step) if x[2] == 3 and "Harvester" in str(x[6].getItemId())]
        kc(pend_ is not None and str(Rx.getProperty("harv")) == "1" and len(hvs) == 1 and hvs[0][3] == sx and not [x for x in lls(csx, "pcr%d" % step) if x[2] == 2]
           and Rx.getProperty("harv.pend") is None and str(Rx.getProperty("harvAuto")) == "1" and str(Rx.getProperty("sickle.up.fort")) == "3",
           "C2: a crash at step %d (journal on disk): the next look finishes the merge (one Harvester, no hoe, no journal, no trim)" % step)
    # C3 the hoe away (in a chest): its SNAPSHOT is merged; the physical hoe is retired when it turns up
    U3 = UUID.fromString("00000000-0000-0000-0000-000000001503")
    PR3, inv3, cs3, h3, s3 = old_profile(U3, "psnap", "Snap")
    hx3 = [x for x in lls(cs3, "psnap") if x[2] == 2][0]
    hoeStack3 = hx3[6]
    cs3[hx3[0]].removeItemStackFromSlot(JShort(hx3[1]))
    Harv.FETCH.clear()
    look(PR3, inv3)
    R3 = LL.reg("psnap")
    hv3 = [x for x in lls(cs3, "psnap") if x[2] == 3]
    kc(str(R3.getProperty("harv")) == "1" and str(R3.getProperty("harvAutoHow")) == "snapshot" and hv3 and str(hv3[0][6].getItemId()) == "Tool_Sickle_Harvester_Copper"
       and fl[0] in str(doc(hv3[0][6]).get("mods")), "C3: the hoe away -> merged from its SNAPSHOT (its tier + its line are in the Harvester)")
    cs3["storage"].setItemStackForSlot(JShort(30), hoeStack3)
    look(PR3, inv3)
    old3 = [x for x in lls(cs3, "psnap") if x[2] == 2]
    kc(old3 and bool(LL.isRt(doc(old3[0][6]))) and str(LL.reg("psnap").getProperty("harv")) == "1", "C3: the physical hoe that turns up is RETIRED (breaks nothing)")
    # C3c (critic fix 3) the hoe lost with NO snapshot: the merge waits (never sickle-only); /hoe brings a hoe, then it merges
    U3c = UUID.fromString("00000000-0000-0000-0000-000000001513")
    PR3c, inv3c, cs3c, h3c, s3c = old_profile(U3c, "plost", "Lost")
    hx3c = [x for x in lls(cs3c, "plost") if x[2] == 2][0]
    cs3c[hx3c[0]].removeItemStackFromSlot(JShort(hx3c[1]))
    R3c = LL.reg("plost")
    for k_ in ("hoe.snap", "hoe.snapU", "hoe.snapId"):
        R3c.remove(k_)
    LL.save("plost", R3c)
    LL.REG.clear()
    look(PR3c, inv3c)
    look(PR3c, inv3c)
    R3c = LL.reg("plost")
    kc(R3c.getProperty("harv") is None and str(R3c.getProperty("hoe.uid")) == h3c and [x for x in lls(cs3c, "plost") if x[2] == 3 and "Harvester" not in str(x[6].getItemId())],
       "C3c (critic fix 3): a lost hoe without a snapshot -> NO merge (the sickle stays a sickle, the hoe stays in the registry)")
    ref3c, st3c, ch3c, pl3c = world(inv3c, cs3c, PR3c)
    r3c = str(Life.reclaim(PR3c, pl3c, JInt(2)))
    R3c = LL.reg("plost")
    kc(str(R3c.getProperty("harv")) == "1" and len([x for x in lls(cs3c, "plost") if "Harvester" in str(x[6].getItemId())]) == 1 and "Harvester" in r3c,
       "C3c: /hoe brings a hoe (a new one - no copy existed), then hoe + sickle merge: %s" % r3c[:160])
    # C4 the hoe in Requip: fetched, then merged physically, Requip told
    RQ = {"rows": [], "fetch": [], "gone": [], "room": True}
    CUR = {}

    @JImplements("java.util.function.Function")
    class RqList(object):
        @JOverride
        def apply(self, o):
            rows = RQ["rows"] if str(o[1]) == "items" else []
            arr = JArray(JObject)(len(rows))
            for i_, r_ in enumerate(rows):
                arr[i_] = JArray(JObject)([JString(r_[0]), JString(r_[1]), r_[2]])
            return arr

    @JImplements("java.util.function.Function")
    class RqFetch(object):
        @JOverride
        def apply(self, o):
            eid = str(o[1])
            if not RQ["room"]:
                return JString("no room")
            row = [r_ for r_ in RQ["rows"] if r_[0] == eid][0]
            md = row[2].clone()
            md.put(str(Data.stampKey()), BD("e", BS(eid)))
            cs_ = CUR["cs"]
            for i_ in range(int(cs_["storage"].getCapacity())):
                x_ = cs_["storage"].getItemStack(JShort(i_))
                if x_ is None or x_.isEmpty():
                    cs_["storage"].setItemStackForSlot(JShort(i_), IS(row[1], JInt(1), md))
                    break
            RQ["rows"] = [r_ for r_ in RQ["rows"] if r_[0] != eid]
            RQ["fetch"].append(eid)
            return JString("ok")

    @JImplements("java.util.function.Function")
    class RqGone(object):
        @JOverride
        def apply(self, o):
            RQ["gone"].append((str(o[1]), str(o[2])))
            return JObject(True, Bool_)
    old_list = br.get("wardrobe:fn:list")
    br.put("wardrobe:fn:list", RqList())
    br.put("wardrobe:fn:fetch", RqFetch())
    br.put("wardrobe:fn:gone", RqGone())
    try:
        U4 = UUID.fromString("00000000-0000-0000-0000-000000001604")
        PR4, inv4, cs4, h4, s4 = old_profile(U4, "prq", "Rq")
        CUR["cs"] = cs4
        hx4 = [x for x in lls(cs4, "prq") if x[2] == 2][0]
        RQ["rows"] = [("eHOE", str(hx4[6].getItemId()), hx4[6].getMetadata())]
        cs4[hx4[0]].removeItemStackFromSlot(JShort(hx4[1]))
        RQ["room"] = False
        Harv.FETCH.clear()
        look(PR4, inv4)
        R4w = LL.reg("prq")
        kc(R4w.getProperty("harv") is None and not RQ["fetch"] and [r_ for r_ in RQ["rows"] if r_[0] == "eHOE"] and str(R4w.getProperty("hoe.uid")) == h4,
           "C4 (critic fix 3): the Requip fetch refused -> the merge WAITS (the stored hoe is never merged from its snapshot or retired)")
        RQ["room"] = True
        Harv.FETCH.clear()
        look(PR4, inv4)
        R4 = LL.reg("prq")
        kc(RQ["fetch"] == ["eHOE"] and str(R4.getProperty("harv")) == "1" and str(R4.getProperty("harvAutoHow")) == "inventory" and ("eHOE", "merged") in RQ["gone"]
           and not [x for x in lls(cs4, "prq") if x[2] == 2], "C4: the hoe in Requip: fetched (wardrobe:fn:fetch), merged physically, Requip told it is gone: %s" % RQ)
    finally:
        br.put("wardrobe:fn:list", old_list)
        br.remove("wardrobe:fn:fetch")
        br.remove("wardrobe:fn:gone")
    # C6 UNDO (the C profile): the hoe + sickle come back (same uids), the registry from the History copy, never merged again
    kc(int(Harv.pending(pkc)) == 1, "C6: a merge is on record for the C profile")
    PKEY[str(U1)] = "pc"
    look(PRC, invC)
    kc(Harv.undoWhy(pkc) is None, "C6a (critic fix 4): an unchanged Harvester -> the undo check passes: %s" % Harv.undoWhy(pkc))
    RCa = LL.reg(pkc)
    RCa.setProperty("sickle.up.fort", "4")
    LL.save(pkc, RCa)
    wpk = Harv.undoWhy(pkc)
    RCa.setProperty("sickle.up.fort", "3")
    LL.save(pkc, RCa)
    kc(wpk is not None and "Upgrade Points" in str(wpk), "C6a: Upgrade Points changed since the merge -> the admin check names it: %s" % wpk)
    hvA = [x for x in lls(csC, pkc) if x[2] == 3][0]
    dA = doc(hvA[6]).clone()
    dA.put("rfN", JClass("org.bson.BsonInt32")(JInt(7)))
    csC[hvA[0]].setItemStackForSlot(JShort(hvA[1]), Data.put(hvA[6], dA, U1))
    look(PRC, invC)
    wrf = Harv.undoWhy(pkc)
    Harv.UNDO.put(U1, JString("Admin"))
    look(PRC, invC)
    kc(wrf is not None and "reforged" in str(wrf) and not Harv.UNDO.containsKey(U1) and str(LL.reg(pkc).getProperty("harv")) == "1"
       and [x for x in lls(csC, pkc) if "Harvester" in str(x[6].getItemId())] and int(Harv.N[8]) >= 1,
       "C6a: a reforged Harvester -> the queued undo is REFUSED at the look (nothing changes, the queue entry goes): %s" % wrf)
    Harv.UNDO.put(U1, JString("Admin|force"))
    look(PRC, invC)
    RU = LL.reg(pkc)
    sicU = [x for x in lls(csC, pkc) if x[2] == 3]
    hoeU_ = [x for x in lls(csC, pkc) if x[2] == 2]
    kc(sicU and str(sicU[0][6].getItemId()) == "Tool_Sickle_Crude" and sicU[0][3] == siU and hoeU_ and str(hoeU_[0][6].getItemId()) == "Tool_Hoe_Copper"
       and hoeU_[0][3] == hoU and fl[0] in str(doc(hoeU_[0][6]).get("mods")) and not [x for x in lls(csC, pkc) if "Harvester" in str(x[6].getItemId())],
       "C6: UNDO: the Harvester's slot is the Crude sickle again (same uid), the Copper hoe is back (same uid, its line)")
    kc(RU.getProperty("harv") is None and str(RU.getProperty("harvAuto")) == "undone" and str(RU.getProperty("hoe.uid")) == hoU and str(RU.getProperty("sickle.uid")) == siU
       and str(RU.getProperty("hoe.up.fort")) == "3" and RU.getProperty("harvUndo.pend") is None and not Harv.UNDO.containsKey(U1) and int(Harv.pending(pkc)) == 0,
       "C6: the registry = the History copy's hoe / sickle keys, harvAuto=undone, no journal; nothing pending")
    look(PRC, invC)
    kc(LL.reg(pkc).getProperty("harv") is None and [x for x in lls(csC, pkc) if x[2] == 2], "C6: an undone profile is never merged automatically again")
    refC, stC, chC, plC = world(invC, csC, PRC)
    rh2 = str(Life.reclaim(PRC, plC, JInt(2)))
    kc("retired" not in rh2 and "You still have your lifelong hoe" in rh2, "C6: an undone profile keeps the 0.3.13 /hoe: %s" % rh2)
    # C7 undo crashes (44 after the registry write, 45 after the sickle is back) resume at the next look
    for step, base in ((44, 41), (45, 42)):
        pk_ = "pcr%d" % base
        Ux, PRx, invx, csx = CR2[base]
        PKEY[str(Ux)] = pk_
        recx = [l_.split(chr(9)) for l_ in open(os.path.join(HOME, "harvmerge", pk_ + ".log"), encoding="utf-8").read().split(chr(10)) if l_.startswith("MERGE")][-1]
        look(PRx, invx)
        Harv.UNDO.put(Ux, JString("Admin"))
        Harv.CRASH_AT = JInt(step)
        look(PRx, invx)
        Harv.CRASH_AT = JInt(0)
        mid_ = LL.reg(pk_).getProperty("harvUndo.pend")
        LL.REG.clear()
        look(PRx, invx)
        Rz = LL.reg(pk_)
        k3 = [x for x in lls(csx, pk_) if x[2] == 3]
        k2 = [x for x in lls(csx, pk_) if x[2] == 2]
        kc(mid_ is not None and Rz.getProperty("harvUndo.pend") is None and str(Rz.getProperty("harvAuto")) == "undone" and len(k3) == 1
           and str(k3[0][6].getItemId()) == recx[8] and len(k2) == 1 and str(k2[0][6].getItemId()) == recx[5],
           "C7: an undo crash at step %d (journal harvUndo.pend on disk): the next look finishes it (one sickle %s, one hoe %s)" % (step, recx[8], recx[5]))
    # C8 a snapshot merge undone: the hoe comes back under a NEW uid in the old one's family (the old physical one stays retired)
    Harv.UNDO.put(U3, JString("Admin"))
    look(PR3, inv3)
    R8 = LL.reg("psnap")
    k2_8 = [x for x in lls(cs3, "psnap") if x[2] == 2 and not bool(LL.isRt(doc(x[6])))]
    kc(len(k2_8) == 1 and k2_8[0][3] != h3 and str(R8.getProperty("hoe.uid")) == k2_8[0][3] and h3 in str(R8.getProperty("hoe.nsw") or "")
       and str(Data.str(doc(k2_8[0][6]), "lcu", "")) == h3 and [x for x in lls(cs3, "psnap") if x[2] == 2 and bool(LL.isRt(doc(x[6])))],
       "C8: a SNAPSHOT merge undone: a hoe under a new uid (lcu = the old one, in its family); the old physical hoe stays retired")
    # C9 harvester.only off = the 0.3.13 flow (no merge)
    apply(harvester__only="false")
    U9 = UUID.fromString("00000000-0000-0000-0000-000000001709")
    PKEY[str(U9)] = "poff"
    PR9 = mkpr(U9, "Off")
    skills(u=U9, Mining=4, Foraging=4, Farming=4, Fishing=4)
    inv9, cs9 = mkinv()
    look(PR9, inv9)
    look(PR9, inv9)
    kc([x for x in lls(cs9, "poff") if x[2] == 2] and LL.reg("poff").getProperty("harv") is None, "C9: harvester.only off = the hoe + sickle kit, no merge")
    apply()
    # C10 the Tools tab's Make Harvester while harvester.only is on: the preview shows the automatic rules, the click runs the automatic merge
    R9 = LL.reg("poff")
    c9 = Life.harvCheck(U9, inv9, JString("poff"), R9)
    pv9 = Life.harvPreview(U9, inv9, R9, c9)
    r9 = str(Life.harvest(PR9, inv9))
    R9 = LL.reg("poff")
    kc(c9[0] is None and pv9 is not None and str(pv9[2]) == "0" and str(pv9[4]) == "" and r9.startswith("+Your hoe and sickle are one Harvester")
       and str(R9.getProperty("harv")) == "1" and str(R9.getProperty("harvAuto")) == "1", "C10: Make Harvester (harvester.only on): preview = no line lost / no point trim, the click = the automatic merge: %s" % r9[:90])

    # ============================================================== D: the sweep tier
    def dec(id_, m):
        return list(LL.decideI(JString(id_) if id_ else None, JInt(4), JInt(m)))
    # Skyy 2026-10-16 "Full on starter crops": a farming tool of tier t reaps crops of tier t + 1 in full (Crude = Wheat / Lettuce); hands keep 0.3.5
    tab = [("Tool_Sickle_Harvester_Crude", 1, 0), ("Tool_Sickle_Harvester_Crude", 2, 1), ("Tool_Sickle_Harvester_Crude", 3, 2), ("Tool_Sickle_Harvester_Copper", 1, 0),
           ("Tool_Sickle_Harvester_Copper", 2, 0), ("Tool_Sickle_Harvester_Copper", 3, 1), ("Tool_Sickle_Harvester_Copper", 4, 2), ("Tool_Sickle_Harvester_Iron", 3, 0),
           ("Tool_Sickle_Harvester_Iron", 4, 1), ("Tool_Sickle_Harvester_Iron", 5, 1), ("Tool_Sickle_Harvester_Thorium", 4, 0), ("Tool_Sickle_Harvester_Thorium", 7, 0),
           (None, 1, 0), (None, 2, 1), (None, 3, 2), ("Tool_Hoe_Crude", 1, 0), ("Tool_Hoe_Copper", 2, 0), ("Weapon_Sword_Iron", 1, 0), ("Weapon_Sword_Iron", 2, 1)]
    badt = [(i_, m_, w_, dec(i_, m_)[0]) for i_, m_, w_ in tab if dec(i_, m_)[0] != w_]
    kc(not badt, "D: decideI on crops: Crude reaps Wheat / Lettuce in full, Carrot / Corn half, Cauliflower refused; each tier one pair more; the Harvester's own "
       "top (Thorium) covers every crop; bare hands / other items keep the 0.3.5 rule: wrong %s" % badt)
    kc(int(LL.fullT(JArray(JInt)(dec("Tool_Sickle_Harvester_Thorium", 7)))) == 4 and int(LL.fullT(JArray(JInt)(dec("Tool_Sickle_Harvester_Crude", 3)))) == 3,
       "D: fullT uses the top decideI used ([6])")
    kc(int(LL.farmTier("Plant_Crop_Wheat_StageFinal", "Tool_Sickle_Harvester_Crude")) == 0 and int(LL.farmTier("Plant_Crop_Carrot_StageFinal", "Tool_Sickle_Harvester_Crude")) == 1
       and int(LL.farmTier("Plant_Crop_Cauliflower_StageFinal", "Tool_Sickle_Harvester_Crude")) == 2 and int(LL.farmTier("Plant_Crop_Cauliflower_StageFinal", "Tool_Sickle_Harvester_Copper")) == 1,
       "D: gear:fn:farmTier (SkyySkills' half XP) follows")
    o0 = str(LL.onlyFor2(JInt(5), JInt(0), True, ""))
    o1_ = str(LL.onlyFor2(JInt(5), JInt(1), True, ""))
    o3 = str(LL.onlyFor2(JInt(5), JInt(3), True, ""))
    kc("Wheat" in o0 and "Lettuce" in o0 and "Carrot" not in o0 and "Carrot" in o1_ and "Cauliflower" not in o1_ and "Potato" in o3,
       "D: the Fortune crops: Crude Wheat / Lettuce, Copper + Carrot / Corn, Thorium all: %s / %s" % (o0[:60], o1_[:60]))
    apply(farm__crudeT1="false")
    kc(dec("Tool_Sickle_Harvester_Crude", 1)[0] == 0 and dec("Tool_Sickle_Harvester_Copper", 2)[0] == 1 and dec("Tool_Sickle_Harvester_Iron", 7)[0] == 0
       and dec(None, 1)[0] == 0 and "Carrot" not in str(LL.onlyFor2(JInt(5), JInt(1), True, "")),
       "D: farm.crudeT1 off = the 0.3.13 answers (Crude counts as Copper, Copper one below Carrot, the sickle top)")
    apply()
    BLOCKS = {}
    HELD = [None]
    FAILED = []

    @JImplements("java.util.function.Function")
    class Blk(object):
        @JOverride
        def apply(self, o):
            v_ = BLOCKS.get((int(o[0]), int(o[1]), int(o[2])))
            return None if v_ is None else JString(v_)

    @JImplements("java.util.function.Function")
    class Ctx(object):
        @JOverride
        def apply(self, o):
            k_ = str(o[0])
            if k_ == "pr":
                return PR1
            if k_ == "held":
                return HELD[0]
            if k_ == "fail":
                FAILED.append(1)
                return None
            if k_ == "failed":
                return JObject(bool(FAILED), Bool_)
            return None
    Sk = P("GearSickle")
    Can = P("GearCan")
    Sk.BLK = Blk()
    Can.CTX = Ctx()
    try:
        pos = V3i(JInt(1), JInt(64), JInt(1))

        def sw(block, held):
            BLOCKS[(1, 64, 1)] = block
            HELD[0] = None if held is None else stack(held)
            return int(Harv.swing(None, None, None, HELD[0], pos))
        Harv.ONEUP.clear()
        a1 = sw("Plant_Crop_Carrot_StageFinal", "Tool_Sickle_Harvester_Crude")
        a2 = sw("Plant_Crop_Carrot_StageFinal", "Tool_Sickle_Harvester_Crude")
        Harv.ONEUP.put(U1, JObject(JLong(int(Harv.ONEUP.get(U1)) - 1000), Long_))
        a3 = sw("Plant_Crop_Carrot_StageFinal", "Tool_Sickle_Harvester_Crude")
        kc((a1, a2, a3) == (1, 2, 1), "D: a Crude Harvester on Carrots (one up): ONE crop per swing breaks the ordinary way, the rest of the arc is skipped, the next swing again: %s" % ((a1, a2, a3),))
        PR1.said = None
        res_ = [sw("Plant_Crop_Wheat_StageFinal", "Tool_Sickle_Harvester_Crude"), sw("Plant_Crop_Pumpkin_StageFinal", "Tool_Sickle_Harvester_Copper"),
                sw("Plant_Grass_Sharp", "Tool_Sickle_Harvester_Crude"), sw("Plant_Crop_Potato_StageFinal", "Tool_Sickle_Harvester_Thorium")]
        kc(res_ == [0, 2, 0, 0], "D: Crude on Wheat (Skyy: full on starter crops) = vanilla's sweep harvest, Copper on Pumpkin (two up) = skipped, a plant = vanilla, Thorium on Potato = vanilla: %s" % res_)
        Harv.ONEUP.clear()
        cm = [m for m in Crop.class_.getDeclaredMethods() if str(m.getName()) == "interactWithBlock"][0]
        cm.setAccessible(True)
        BLOCKS[(1, 64, 1)] = "Plant_Crop_Carrot_StageFinal"
        HELD[0] = stack("Tool_Sickle_Harvester_Crude")
        del FAILED[:]
        cm.invoke(Crop(), JArray(JObject)([None, None, None, None, HELD[0], pos, None]))
        f1 = len(FAILED)
        HELD[0] = stack("Tool_Sickle_Harvester_Copper")
        BLOCKS[(1, 64, 1)] = "Plant_Crop_Pumpkin_StageFinal"
        cm.invoke(Crop(), JArray(JObject)([None, None, None, None, HELD[0], pos, None]))
        kc(f1 == 1 and len(FAILED) == 1, "D: GearHarvCrop: one up = the Failed path (the ordinary hit), two up = nothing at all")
    finally:
        Sk.BLK = None
        Can.CTX = None
    INTc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
    hi_ = INTc.getAssetMap().getAsset("SkyyGear_Harvest_Crop")
    kc(hi_ is not None and str(hi_.getClass().getName()) == PKG + "GearHarvCrop", "D: the asset SkyyGear_Harvest_Crop loads as a GearHarvCrop: %s" % (None if hi_ is None else hi_.getClass().getName()))
    # a bare boot loads the vanilla ITEMS but not the vanilla INTERACTIONS: the swing vars' Parents ("Failed to find parent with key 'Sickle_...'")
    # are vanilla interaction files (checked in Assets.zip below) that the game loads - those records are expected here; anything else is not
    with zipfile.ZipFile(L["AZP"]) as az_:
        vint = set(os.path.basename(n)[:-5] for n in az_.namelist() if n.startswith("Server/Item/Interactions/") and n.endswith(".json"))
    pre = re.compile(r"Failed to find parent (?:with key )?'([A-Za-z0-9_]+)'")
    par = lambda r_: (bool(pre.search(r_[1])) and pre.search(r_[1]).group(1) in vint) or "Removing child asset" in r_[1]          # + the reload notes every vanilla weapon gets too
    van = sorted(set(pre.search(r_[1]).group(1) for r_ in E["rec"] if par(r_) and pre.search(r_[1])))
    recs = [r_ for r_ in E["rec"] if r_[0] in ("SEVERE", "WARNING") and ("Harvester" in r_[1] or "SkyyGear_Harvest" in r_[1] or "SkyyGearHarvest" in r_[1]) and not par(r_)]
    kc(not recs, "D: no load record about the Harvesters / the interaction (besides the bare boot's missing VANILLA parents %s): %s" % (van[:8], [r_[1][:160] for r_ in recs[:3]]))

    # ============================================================== E: Sigils
    skills(Mining=40, Foraging=4, Farming=4, Fishing=4)
    mid = "Armor_Copper_Head"
    md0 = Mine.doc(JString(mid), JString("craft"), JInt(5))
    s0 = Data.put(stack(mid), md0, U1)
    d0 = doc(s0)
    kc(Sig.why(s0, d0, JInt(2)) is None and int(Sig.baseR(mid, d0)) == 0 and Sig.why(s0, d0, JInt(5)) is None,
       "E: a Mining Set piece takes a Rare / a Mythic Sigil (Set counts as Normal; sigil.mythicUse on)")
    apply(sigil__mythicUse="false")
    kc(str(Sig.why(s0, d0, JInt(5))) == str(Sig.MYOFF), "E: sigil.mythicUse off = the Mythic Sigil refused again")
    apply()
    invE, csE = mkinv()
    csE["storage"].setItemStackForSlot(JShort(0), s0)
    csE["storage"].setItemStackForSlot(JShort(1), stack("Skyy_Sigil_Rare", 2))
    rE = Sig.apply(invE, JInt(1), JInt(0), JString(mid), Forge.fp(s0), JInt(2), U1, JString("Tester"))
    nE = csE["storage"].getItemStack(JShort(0))
    dE = doc(nE)
    kc(int(rE[0]) == 1 and str(Data.str(dE, "r", "")) == "rare" and str(Data.str(dE, "set", "")) == "mining_copper" and ids(csE).get("Skyy_Sigil_Rare") == 1
       and bool(View.canReforge(mid, dE)), "E: the Sigil applied: Rare, the set field kept, one Sigil used, reforgeable now: %s" % str(rE[1]))
    armor = SIC(JShort(4))
    for i_, pc in enumerate(("Head", "Chest", "Hands", "Legs")):
        pid = "Armor_Copper_" + pc
        d_ = Mine.doc(JString(pid), JString("craft"), JInt(5)).clone()
        d_.put("r", BS("rare"))
        armor.setItemStackForSlot(JShort(i_), Data.put(stack(pid), d_, U1))
    T_ = Cfg.STAB
    cnt = list(GSet.counts0(T_, U1, armor))
    si = int(GSet.idx(JString("mining_copper")))
    kc(si >= 0 and cnt[si] == 4, "E: four Rare (Sigil) Copper pieces still make the full Mining Set (the bonus on top): %s" % (cnt[si] if si >= 0 else cnt))
    dm = d0.clone()
    dm.put("r", BS("mythic"))
    kc(bool(ArmLv.ladderOk(mid, dm)), "E: a Mythic (Sigil) mining piece still tiers up on the Anvil")
    gid = "Armor_Foraging_F1_Head"
    if ITEM.getAssetMap().getAsset(gid) is not None:
        gd = P("GearGArm").doc(JString(gid), JString("craft"), JInt(5))
        kc(Sig.why(Data.put(stack(gid), gd, U1), gd, JInt(2)) is not None, "E: gathering (Foraging) armor still refuses a Sigil (Mining Sets only)")
    roles = [("Golem_Guardian_Void", 2), ("Dragon_Fire", 2), ("Goblin_Duke", 2), ("Trork_Chieftain", 2), ("Golem_Crystal_Earth", 1), ("Skeleton_Elite", 1), ("Yeti", 1),
             ("Rex_Cave", 1), ("Trork_Warrior", 0), ("Snapdragon", 0), ("Skeleton_Fighter", 0)]
    badr = [(r_, w_, int(SigD.kindOf(JString(r_)))) for r_, w_ in roles if int(SigD.kindOf(JString(r_))) != w_]
    kc(not badr and int(SigD.kindOf(None)) == 0, "E: the role words: bosses (Guardian wins over Golem), mini bosses, plain mobs: wrong %s" % badr)
    eq([int(SigD.zoneOf(JInt(x))) for x in (-1, 1, 20, 21, 30, 31, 45, 46, 99)], [1, 1, 1, 2, 2, 3, 3, 4, 4], "E: zones from the mob level")
    kc(SigD.check("sigil.mob", "1,2") is not None and SigD.check("sigil.mob", "0,0,0,0,101") is not None and SigD.check("sigil.bossZone", "1,1,1,1") is None
       and SigD.check("sigil.boss", "0,0,6,2,0.5") is None and SigD.check("sigil.bossZone", "1,1,1,21") is not None, "E: the row checks")
    SigD.RNG = JClass("java.util.Random")(JLong(11))
    ids_ = [str(x) for x in Sig.IDS]

    def stats(tab_, x, n=20000):
        c_ = dict((i, 0) for i in ids_)
        for _ in range(n):
            r_ = SigD.pick(tab_, JDouble(x), None)
            if r_ is not None:
                c_[str(r_)] += 1
        return dict((k_.split("_")[-1], 100.0 * v_ / n) for k_, v_ in c_.items())
    sb4 = stats(SigD.bossT(), 3.0)
    sm = stats(SigD.mobT(), 1.0)
    sn = stats(SigD.miniT(), 1.0)
    kc(1.0 < sb4["Mythic"] < 2.1 and 4.8 < sb4["Fabled"] < 7.0 and 14.5 < sb4["Legendary"] < 19.0 and sb4["Unique"] == 0 and sb4["Rare"] == 0,
       "E: zone-4 boss rolls (x3): Mythic ~1.5%%, Fabled ~6%%, Legendary ~17%% (Mythic first): %s" % sb4)
    kc(0.08 < sm["Unique"] < 0.35 and sum(v for k, v in sm.items() if k != "Unique") == 0 and 3.0 < sn["Rare"] < 5.0 and 1.0 < sn["Legendary"] < 2.1
       and sn["Mythic"] == 0 and sn["Fabled"] == 0, "E: mob rolls = Unique only (~0.2%%), mini boss = Rare ~4%% + Legendary ~1.5%%: %s / %s" % (sm, sn))
    sb1 = stats(SigD.bossT(), 1.0)
    kc(sb1["Mythic"] < sb4["Mythic"] and 0.2 < sb1["Mythic"] < 0.9, "E: the Mythic chance rises with the zone: zone 1 %.2f%% < zone 4 %.2f%%" % (sb1["Mythic"], sb4["Mythic"]))
    SigD.RNG = None
    # GearSigDrop.mob end to end with stand-ins (the 0.2.11 harness's way)
    try:
        FS, FCh = L["FS"], L["FCh"]
        PLA, PRc, REFc, IHM = L["PLA"], L["PR"], L["REFc"], L["IHM"]
        UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
        HRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
        TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
        DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
        DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
        DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
        ILM = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig$ItemsLossMode")
        NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
        ROLE = JClass("com.hypixel.hytale.server.npc.role.Role")
        R3F = JClass("com.hypixel.hytale.math.vector.Rotation3f")
        V3d = JClass("org.joml.Vector3d")
        GM = JClass("com.hypixel.hytale.protocol.GameMode")
        LEVEL = {"lv": 24}

        @JImplements("java.util.function.Function")
        class MobLevel(object):
            @JOverride
            def apply(self, a):
                return JObject(JInt(LEVEL["lv"]), Integer)
        old_ml = br.get("mob:fn:level")
        br.put("mob:fn:level", MobLevel())
        st = us.allocateInstance(FS.class_)
        st.comps = JClass("java.util.HashMap")()
        killer = us.allocateInstance(REFc.class_)
        jf(REFc, "index").setInt(killer, JInt(3))
        jf(REFc, "store").set(killer, st)
        kpl = us.allocateInstance(PLA.class_)
        jf(PLA, "gameMode").set(kpl, GM.Adventure)
        km = IHM()
        km.put(PLA.getComponentType(), kpl)
        km.put(PRc.getComponentType(), PR1)
        st.comps.put(killer, km)
        chunk = us.allocateInstance(FCh.class_)
        # the bare boot's EntityModule has no class -> component type map: give NPCEntity one type (what the NPC plugin registers in the game)
        EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        emi = EMc.get()
        fm_ = jf(EMc, "classToComponentType")
        if fm_.get(emi) is None:
            fm_.set(emi, JClass("java.util.HashMap")())
        if fm_.get(emi).get(NPCE.class_) is None:
            fm_.get(emi).put(NPCE.class_, us.allocateInstance(JClass("com.hypixel.hytale.component.ComponentType").class_))

        def mk(role_name, src=True, dropped=False, u_=None):
            m_ = IHM()
            uc_ = us.allocateInstance(UUIDC.class_)
            jf(UUIDC, "uuid").set(uc_, u_ or UUID.randomUUID())
            m_.put(UUIDC.getComponentType(), uc_)
            hr_ = us.allocateInstance(HRC.class_)
            jf(HRC, "rotation").set(hr_, R3F())
            m_.put(HRC.getComponentType(), hr_)
            tc_ = us.allocateInstance(TC.class_)
            jf(TC, "position").set(tc_, V3d(JDouble(5.0), JDouble(70.0), JDouble(5.0)))
            m_.put(TC.getComponentType(), tc_)
            dc_ = us.allocateInstance(DTH.class_)
            dm_ = us.allocateInstance(DMG.class_)
            jf(DMG, "source").set(dm_, DENT(killer) if src else None)
            jf(DTH, "deathInfo").set(dc_, dm_)
            jf(DTH, "itemsLossMode").set(dc_, ILM.ALL)
            m_.put(DTH.getComponentType(), dc_)
            rl_ = us.allocateInstance(ROLE.class_)
            jf(ROLE, "dropDeathItemsInstantly").setBoolean(rl_, True)
            jf(ROLE, "deathItemsDropped").setBoolean(rl_, dropped)
            np_ = us.allocateInstance(NPCE.class_)
            jf(NPCE, "role").set(np_, rl_)
            jf(NPCE, "roleName").set(np_, role_name)
            m_.put(NPCE.getComponentType(), np_)
            chunk.comps = m_
            return chunk
        SP = []

        @JImplements("java.util.function.BiFunction")
        class Spawn(object):
            @JOverride
            def apply(self, it_, at_):
                SP.append((str(it_.getItemId()), float(at_.y())))
                return None
        Loot = P("GearLoot")
        old_sp = Loot.SPAWN
        Loot.SPAWN = Spawn()
        try:
            apply(sigil__boss="0,0,0,0,100", sigil__mini="0,100,0,0,0", sigil__mob="100,0,0,0,0")
            NU = UUID.randomUUID()
            r_boss = int(SigD.mob(mk("Dragon_Fire", u_=NU), JInt(0), st, None))
            r_twice = int(SigD.mob(mk("Dragon_Fire", u_=NU), JInt(0), st, None))
            r_mini = int(SigD.mob(mk("Golem_Crystal_Earth"), JInt(0), st, None))
            r_mob = int(SigD.mob(mk("Trork_Warrior"), JInt(0), st, None))
            kc((r_boss, r_twice, r_mini, r_mob) == (1, 0, 1, 1) and [x[0] for x in SP] == ["Skyy_Sigil_Mythic", "Skyy_Sigil_Rare", "Skyy_Sigil_Unique"] and SP[0][1] == 71.0,
               "E: GearSigDrop.mob: a boss -> its row (Mythic), the same death never twice, a mini boss (Rare), a levelled mob (Unique), at the mob + (0, 1, 0): %s" % SP)
            del SP[:]
            cases = []
            jf(PLA, "gameMode").set(kpl, GM.Creative)
            cases.append(int(SigD.mob(mk("Dragon_Fire"), JInt(0), st, None)))
            jf(PLA, "gameMode").set(kpl, GM.Adventure)
            cases.append(int(SigD.mob(mk("Dragon_Fire", src=False), JInt(0), st, None)))
            LEVEL["lv"] = -1
            cases.append(int(SigD.mob(mk("Trork_Warrior"), JInt(0), st, None)))
            r_lvl0_boss = int(SigD.mob(mk("Dragon_Fire"), JInt(0), st, None))
            LEVEL["lv"] = 24
            cases.append(int(SigD.mob(mk("Dragon_Fire", dropped=True), JInt(0), st, None)))
            apply(sigil__drops="false", sigil__boss="0,0,0,0,100")
            cases.append(int(SigD.mob(mk("Dragon_Fire"), JInt(0), st, None)))
            kc(cases == [0, 0, 0, 0, 0] and r_lvl0_boss == 1, "E: no Sigil for a Creative killer / no killer / an unlevelled plain mob / items already dropped / sigil.drops off; "
               "a boss without a level still rolls (zone 1): %s %s" % (cases, r_lvl0_boss))
        finally:
            Loot.SPAWN = old_sp
            br.put("mob:fn:level", old_ml) if old_ml is not None else br.remove("mob:fn:level")
            apply()
    except Exception as e:
        import traceback
        K.check(False, "E: the GearSigDrop.mob stand-in run raised: %s" % traceback.format_exc()[-900:])
    # the bag lists
    IDL = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemDropList")
    names = []
    with zipfile.ZipFile(L["AZP"]) as az_:
        for n in az_.namelist():
            if n.startswith("Server/Drops/") and n.endswith(".json"):
                names.append(n)
    tl = HAL()
    for n in names:
        tl.add(L["afs"].getPath("/" + n))
    try:
        IDL.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl)
    except Exception as e:
        K.notes.append("E: loading the vanilla drop lists raised %s" % str(e)[:200])
    z1 = IDL.getAssetMap().getAsset("Zone1_Encounters_Tier1")
    gm = IDL.getAssetMap().getAsset("Drop_Goblin_Miner")
    kc(z1 is not None and gm is not None, "E: the vanilla Zone1_Encounters_Tier1 + Drop_Goblin_Miner lists are loaded")
    raw = z1.getContainer()
    Norm.STARTED = True
    SigD.ensure()
    k_on = br.get("gear:sigil:drops")
    apply(sigil__drops="false")
    SigD.ensure()
    k_off = br.get("gear:sigil:drops")
    apply()
    SigD.ensure()
    kc(k_on is not None and bool(k_on) and k_off is not None and not bool(k_off) and bool(br.get("gear:sigil:drops")),
       "E (critic fix 1): the bridge key gear:sigil:drops = TRUE while Gear rolls Sigils, FALSE with sigil.drops off (SkyyArmory 0.1.30 then rolls its own)")
    Norm.ensure()
    SigD.ensure()
    chain = []
    c_ = z1.getContainer()
    for _ in range(4):
        chain.append(str(c_.getClass().getSimpleName()))
        c_ = getattr(c_, "inner", None) if str(c_.getClass().getName()).startswith(PKG) else None
        if c_ is None:
            break
    kc("GearSigBag" in chain and int(SigD.N[6]) == 16, "E: the 16 Zone<N>_Encounters lists are wrapped (chain %s), %d lists" % (chain, int(SigD.N[6])))
    rnd = random.Random(5)

    @JImplements("java.util.function.DoubleSupplier")
    class DS(object):
        @JOverride
        def getAsDouble(self):
            return rnd.random()
    ds = DS()

    def roll(lst, n):
        got = {}
        for _ in range(n):
            o_ = HAL()
            lst.getContainer().populateDrops(o_, ds, JString(str(lst.getId())))
            for d_ in o_:
                got[str(d_.getItemId())] = got.get(str(d_.getItemId()), 0) + 1
        return got
    apply(sigil__bag="50,0,0,0,0")
    g1 = roll(z1, 2000)
    g2 = roll(gm, 2000)
    rawg = {}
    for _ in range(500):
        o_ = HAL()
        raw.populateDrops(o_, ds, JString("Zone1_Encounters_Tier1"))
        for d_ in o_:
            rawg[str(d_.getItemId())] = rawg.get(str(d_.getItemId()), 0) + 1
    kc(800 < g1.get("Skyy_Sigil_Unique", 0) < 1200 and "Skyy_Sigil_Unique" not in g2 and "Skyy_Sigil_Unique" not in rawg and len(g1) >= 3,
       "E: 2000 rolls at 50%%: the encounter list adds a Unique Sigil ~1000 times (%d), its own drops still come; Drop_Goblin_Miner never" % g1.get("Skyy_Sigil_Unique", 0))
    apply()
    g3 = roll(z1, 4000)
    kc(30 < g3.get("Skyy_Sigil_Unique", 0) < 140, "E: the default 2%% per roll: %d of 4000" % g3.get("Skyy_Sigil_Unique", 0))
    apply(sticks__lists="Zone1_Encounters_Tier1")
    Sk.ENS = 0
    Sk.WR_SRC = None
    Sk.ensure()
    Norm.ensure()
    SigD.ensure()
    cS = z1.getContainer()
    apply(sticks__lists="Zone1_Encounters_Tier1", sigil__bag="50,0,0,0,0")
    gS = roll(z1, 1000)
    kc(str(cS.getClass().getSimpleName()) == "GearStick" and 350 < gS.get("Skyy_Sigil_Unique", 0) < 650, "E: with the stick cut around it the Sigils still roll (%s, %d)" % (cS.getClass().getSimpleName(), gS.get("Skyy_Sigil_Unique", 0)))
    apply(sigil__drops="false")
    Sk.ENS = 0
    Sk.WR_SRC = None
    Sk.ensure()
    SigD.ensure()
    found = False
    c_ = z1.getContainer()
    for _ in range(4):
        if c_ is None:
            break
        if str(c_.getClass().getSimpleName()) == "GearSigBag":
            found = True
        c_ = getattr(c_, "inner", None) if str(c_.getClass().getName()).startswith(PKG) else None
    kc(not found and "Skyy_Sigil_Unique" not in roll(z1, 500) and int(SigD.N[6]) == 0, "E: sigil.drops off = ours leaves every list (the others stay)")
    apply()
    Sk.ENS = 0
    Sk.WR_SRC = None
    Sk.ensure()
    SigD.ensure()
    SigD.unwrapAll()
    kc(not [x for x in [z1.getContainer()] if str(x.getClass().getSimpleName()) == "GearSigBag"] and bool(Cfg.SIGD_ON) and br.get("gear:sigil:drops") is None,
       "E: unwrapAll (shutdown) takes ours off, the switch stays on, the bridge key goes (SkyyArmory rolls again without SkyyGear)")

    # ============================================================== F: the till area everywhere
    @JImplements("java.util.function.Function")
    class NoIsland(object):
        @JOverride
        def apply(self, o):
            return None
    Till.PERM = NoIsland()
    try:
        a_on = int(Till.allowed(U1, JString("zone1")))
        apply(hoe__areaElsewhere="false")
        a_off = int(Till.allowed(U1, JString("zone1")))
        apply()
    finally:
        Till.PERM = None
    kc(a_on == 1 and a_off == 0, "F: hoe.areaElsewhere on (the new default) = a non-island world tills the ring; off = the 0.3.13 rule")
    K.notes.append("H314 status: %s" % str(Harv.statusText()))


# ====================================================================================================== LIVE314
def run_live314(out):
    from jpype import JClass
    K = H["Child"](out)
    H["_jvm"]([B.SERVER_JAR, JAR], verify=True)
    home = os.path.join(SCRATCH, "live314", "Skyy_SkyyGear")
    shutil.rmtree(os.path.dirname(home), ignore_errors=True)
    os.makedirs(home)
    for f_ in ("config.properties", "quality.properties"):
        if os.path.isfile(os.path.join(LIVE_GEAR, f_)):
            shutil.copyfile(os.path.join(LIVE_GEAR, f_), os.path.join(home, f_))
    shutil.copytree(os.path.join(LIVE_GEAR, "lifelong"), os.path.join(home, "lifelong"))
    Cfg = JClass(PKG + "GearCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Paths.get(os.path.join(home, "gear.log"))
    JClass(PKG + "GearQual").load(Paths.get(os.path.join(home, "quality.properties")))
    before = open(os.path.join(home, "config.properties"), "rb").read()
    regs0 = dict((f_, open(os.path.join(home, "lifelong", f_), "rb").read()) for f_ in os.listdir(os.path.join(home, "lifelong")))
    after1 = None
    for step in (1, 2):
        Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(home, "no-SkyyRolls", "reforge.properties")))
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218", "migrate031", "migrate0314"):
            getattr(Cfg, m)()
        Cfg.load()
        now = open(os.path.join(home, "config.properties"), "rb").read()
        if step == 1:
            after1 = now
            bl, al = before.split(b"\n"), now.split(b"\n")
            changed = [(x, y) for x, y in zip(bl, al) if x != y and x.strip() != b""]
            extra = [y for x, y in zip(bl, al) if x != y and x.strip() == b""] + al[len(bl):]
            K.check(sorted(y.strip().decode() for x, y in changed) == ["hoe.areaElsewhere=true", "sigil.mythicUse=true"]
                    and sorted(x.strip().decode() for x, y in changed) == ["hoe.areaElsewhere=false", "sigil.mythicUse=false"]
                    and any(str(Cfg.H4_MARK_ID) in l_.decode("ISO-8859-1") for l_ in extra) and len(al) == len(bl) + 1,
                    "LIVE314 start 1: only the two lines changed false -> true (+ the marker line): %s / extra %s" % (changed, extra[:2]))
        else:
            K.check(now == after1, "LIVE314 start 2: nothing changes any more (run once)")
        K.check(bool(Cfg.HOE_ELSE) and bool(Cfg.SIG_MY) and bool(Cfg.HARV_ONLY) and bool(Cfg.FARM_T1) and bool(Cfg.SIGD_ON),
                "LIVE314 start %d: the live file reads till everywhere + Mythic Sigil on; the new rows their defaults" % step)
    logs_ = glob.glob(os.path.join(home, "**", "config-changes*"), recursive=True)
    txt = "".join(open(f_, encoding="utf-8", errors="replace").read() for f_ in logs_ if os.path.isfile(f_))
    K.check("hoe.areaElsewhere\tfalse\ttrue\tok" in txt and "sigil.mythicUse\tfalse\ttrue\tok" in txt, "LIVE314: two change-log rows with Undo (status ok): %s" % logs_)
    hist = [f_ for f_ in glob.glob(os.path.join(home, "**", "*"), recursive=True) if os.path.isfile(f_) and "hist" in f_.lower()]
    K.check(any(open(f_, "rb").read() == before for f_ in hist), "LIVE314: a History copy holds the live file's bytes before the update (%d history files)" % len(hist))
    K.check(all(open(os.path.join(home, "lifelong", f_), "rb").read() == b_ for f_, b_ in regs0.items()), "LIVE314: the registries were read, not rewritten")
    rep_ = []
    for f_, b_ in sorted(regs0.items()):
        p_ = {}
        for l_ in b_.decode("utf-8", "replace").split("\n"):
            if "=" in l_ and not l_.startswith("#"):
                a_, c_ = l_.split("=", 1)
                p_[a_] = c_.strip()
        rep_.append((f_[:12], "merged" if p_.get("harv") == "1" else ("hoe+sickle -> merges at the next look" if p_.get("hoe.uid") and p_.get("sickle.uid") else "?"),
                     p_.get("hoe.id"), p_.get("sickle.id")))
    K.notes.append("LIVE314 registries (file, state, hoe, sickle): %s" % rep_)
    K.check(len(rep_) >= 1, "LIVE314: the live registries were read (%d)" % len(rep_))
    K.save()


# ====================================================================================================== main
def child(env, *args):
    cmd = [sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--root", SCR_ROOT]
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
        print("  note (%s): %s" % (label, str(n)[:700]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H310["run_mkfake10"](arg("--mkfake"))), ("--h314", lambda: run_h314(arg("--out"))),
                     ("--live314", lambda: run_live314(arg("--out"))),
                     ("--h313", lambda: H313["run_h313"](arg("--out"))), ("--live313", lambda: H313["run_live313"](arg("--out"))),
                     ("--h312", lambda: H312["run_h312"](arg("--out"))), ("--live312", lambda: H312["run_live312"](arg("--out"))),
                     ("--h311", lambda: H311["run_h311"](arg("--out"))), ("--h310", lambda: H310["run_h310"](arg("--out"))),
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
    _known = {"--only", "--keep", "--dir", "--jar", "--root", "--out"}
    _unk = [a for a in sys.argv[1:] if a.startswith("--") and a not in _known]
    if _unk:
        print("unknown child flag(s) %s - nothing run" % _unk)
        sys.exit(2)
    for f_ in (JAR, J313, FI7_SRC, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
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
    env_313 = dict(env)
    env_313["JAVA_TOOL_OPTIONS"] = env["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.no314=true"
    env_312 = dict(env_313)
    env_312["JAVA_TOOL_OPTIONS"] = env_313["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noNormOff=true"
    env_311 = dict(env_312)
    env_311["JAVA_TOOL_OPTIONS"] = env_312["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noCanKit=true"
    env_old = dict(env_311)
    env_old["JAVA_TOOL_OPTIONS"] = env_311["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noPoleKit=true"
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets314()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")

        def run_children(lst):
            for label, flag, ev in lst:
                if not want(label):
                    continue
                out = os.path.join(SCRATCH, "%s.json" % label)
                pr = child(ev, flag, "--out", out)
                check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
                take(out, label)
        run_children((("h310", "--h310", env_old), ("h39", "--h39", env_old), ("verify", "--verify", env_old), ("h38", "--h38", env_old),
                      ("h37", "--h37", env_old), ("g36", "--g36", env_old), ("snd", "--snd", env_old), ("till", "--till", env_old)))
        if want("life"):
            _why39 = "0.3.9 by design: Identify moved to the Identify tab; the 0.3.5 check clicks it on the Anvil tab (H39 I covers the reveal)"
            H37["L37_EXTRA"].extend([("G35 R1:", _why39), ("G35 R2:", _why39), ("G35 R3:", _why39), ("G35 R4", _why39), ("G35 R5:", _why39)])
            H37["L37_EXTRA"].append(("G35 P6:", "0.3.11 fix round by design: with the kit off /pole says 'You have no lifelong fishing pole - this server hands none out (lifelong.poleKit is off). A pole a quest gave you: hold it and type /lifelong.' (no Marlow pole since SkyyQuests 0.3.4); the exact-copy half is unchanged"))
            H37["L37_EXTRA"].append(("G35 P7 FIX 2", "0.3.11 fix round by design: the refusal reads 'Only a fishing pole a quest gave you can become your lifelong pole' (no Marlow pole since SkyyQuests 0.3.4); still refused, nothing written"))
            _why314 = "0.3.14 by design (Skyy 2026-10-16 'let it work'): sigil.mythicUse defaults to true - a fresh config file says so (the build-time text the seam cannot change), the Mythic Sigil works on the Anvil; H314 E covers it"
            H37["L37_EXTRA"].extend([("G34 S1:", "0.3.14 by design: the fresh config's hoe.areaElsewhere and sigil.mythicUse rows read true (Skyy 2026-10-16 'everywhere' / 'let it work'); H314 A checks the new defaults"),
                                     ("FIX2 M1:", _why314), ("G34 S2:", _why314 + " (the M1 step used the Mythic Sigil the S2 step expected)")])
            H37["L37_EXTRA"].append(("M: a NEW profile's first join", "0.3.12 by design: GearLL.KCRUDE has 6 kinds (+ the watering can); the four Crude Common tools still land in storage 0-3 exactly as checked (the can comes from the kit, off here: noCanKit)"))
            n0 = len(H37["FAILS"])
            H37["run_l35"](env_old)
            for f_ in H37["FAILS"][n0:]:
                w = [why for pre, why in WAIVE if str(f_).startswith(pre)]
                if w:
                    WAIVED.append("L35: %s (%s)" % (str(f_)[:140], w[0]))
                else:
                    FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        run_children((("h311", "--h311", env_311), ("h312", "--h312", env_312), ("live", "--live312", env_312), ("h313", "--h313", env_313),
                      ("live313", "--live313", env_313), ("h314", "--h314", env), ("live314", "--live314", env)))          # ours last (the children share the gear home)
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
