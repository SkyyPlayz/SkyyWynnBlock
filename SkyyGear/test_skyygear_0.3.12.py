"""Harness for SkyyGear 0.3.12 (tools/gear_0_3_12_patch.py header) = the 0.3.11 harness's children run on the 0.3.12 jar + H312 (one booted engine,
with SkyyFishing 0.1.7 as its own pack, the SkyyGearCan interaction type registered the way setup() does):
    python tools/gear_0_3_12_patch.py && python SkyyGear/build_skyygear_0.3.12.py
    python SkyyGear/test_skyygear_0.3.12.py [--keep] [--only assets,h312,h311,h310,h39,verify,h38,h37,g36,snd,till,life,live,audit]

  S312 the jar 0.3.11 -> 0.3.12: only the expected entries are new (6 cans, 4 Harvesters, their textures / icons, the interaction + its root, the
       Harvester animation set, the 5 new classes), changed non-class files = manifest.json + server.lang (only lines added); class compare
       (changed / new / gone) printed; the lang lines carry the tier tags
  H312 ONE booted engine (the 0.3.5 life setup) + SkyyFishing 0.1.7; our interaction type registered on Interaction.CODEC first (setup()'s call):
       A  ASSETS in the engine: the 10 items load (toPacket, MaxStack 1, cans: MaxDurability 100, no block), SkyyGear_Can_Water decodes as a
          GearCanWater (Duration 86400, Radius 1), the root SkyyGear_Can_Use, the SkyyGear_Harvester animation set (Till + the sickle swings),
          no load record about them
       B  KINDS: can = kind 5 (/can), the Harvester = the sickle kind, the vanilla can no kind; tiers, bands, ladders (can.ladders / harvester.ladders
          in GearLL.ladders, written costs), crudeOf / ladOf / kname, noCraft of the vanilla can (can.noVanilla), the Server Setup rows + checks
       C  THE KIT: a fresh profile gets the four + the pole + ONE Crude can (canKit=1, how give, the uid); again / a restart give nothing; a lost can
          is not given again (/can = an exact copy); a crash after the journal -> the same uid; the REDO path; an existing profile gets one; kit off
       D  POINTS: Capacity / Growth / Lasting / Bloom buy on the Tools tab rules (Farming points), GearCan.plan by tier + points (only your can)
       E  THE CLICK on the REAL GearCanWater.interactWithBlock (seams for the world: CTX / SOIL / FLUID / SUPER): Crude 1x1, Copper 3x3 in vanilla's
          own cell order, the water bar (100 / uses), refill on water, empty refused, nothing watered = no water used, wet soil = no Bloom / Growth,
          Bloom + Growth on dry soil, Lasting = the time handed to vanilla, Capacity 5 never dry, a foreign / retired can refused, part.can off;
          waterAs puts the shared fields back even when vanilla throws; the engine glue with no world answers safely
       F  THE HARVESTER: the Tools tab row, the merge (hoe gone, the sickle's slot = the Harvester of the higher tier with the sickle's uid, the
          better rarity, both lines, the points merged + trimmed), the registry (harv=1, no hoe.*), the tab without the hoe row, /hoe /harvester
          /lifelong, an old hoe that turns up is retired, GearTill takes it, the sickle rules + the crop gate, tooltip, the rebirth reset to the
          Crude Harvester, the crash paths (after the journal / after the hoe left / after the Harvester was written), the rebirth gate
       G  THE UPGRADE TAB / TIER UP: the can tiers up Crude -> Copper (25 Copper Ingots, Farming 10) keeping its uid, then waters 3x3
       H  FOLD-INS: skill:fn:hpregen posts (add HP/s + addpct, cached, dropped), the longsword Crescent Rush line, Monk / Spellblade class skills
  LIVE312 start twice on a scratch copy of the live NewBetaTest data: the config bytes untouched, the new rows at their defaults, the registries
       read (not rewritten); then each live profile's first look gives its can ONCE (two looks, a restart between)
  H311 / H310 / H39 / VERIFY / H38 / H37 / G36 / SND / TILL / L35 / AA  the older children on the 0.3.12 jar (-Dskyy.harness.noCanKit=true:
       lifelong.canKit reads as off = 0.3.11's flow they were written for; the pre-0.3.11 ones also noPoleKit as in 0.3.11)
Scratch: tools/dev/scratch/gear0312/harness (deleted at the end unless --keep). Exit code 1 on any failure.
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


VERSION = "0.3.12"
V311 = "0.3.11"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0312")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J311 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V311))                       # read only
PKG = "com.skyy.gear."
CAN_IDS = ["Tool_WaterCan_" + t for t in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite")]
HARV_IDS = ["Tool_Sickle_Harvester_" + t for t in ("Crude", "Copper", "Iron", "Thorium")]
NEW_CLASSES = ["GearCan", "GearCanWater", "GearCanSup", "HarvCmd", "CanCmd"]

# ---- the 0.3.11 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H311 = os.path.join(HERE, "test_skyygear_0.3.11.py")
_T311 = open(_H311, encoding="utf-8").read()
_cut = _T311.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H311, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H311 = {"__name__": "skyygear_h311", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T311[:_cut], _H311 + " (library)", "exec"), H311)
sys.argv = _argv
H310, H39, H38, H37, H36, H35, H = H311["H310"], H311["H39"], H311["H38"], H311["H37"], H311["H36"], H311["H35"], H311["H"]
FAKE_DIR, FAKE_PKG = H311["FAKE_DIR"], H311["FAKE_PKG"]
FI7_SRC = H311["FI7_SRC"]
# the older children's read-only pack jars SkyyArmory 0.1.26 / SkyyCollections 0.2.11 are no longer on disk (tidy_local removes built jars that
# are not pinned): they run with the SET pins SkyyArmory 0.1.28 / SkyyCollections 0.2.19 (supersets of what they read: the wand / staff
# shots, the Enchanted items); a check that depends on the old version's exact numbers is waived below with the reason
_AR_SET = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.28.jar")
_CO_SET = os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.19.jar")
if not os.path.isfile(H38["AR26"]) and os.path.isfile(_AR_SET):
    H38["AR26"] = _AR_SET
if not os.path.isfile(H35["CO_SRC"]) and os.path.isfile(_CO_SET):
    H35["CO_SRC"] = _CO_SET
FAILS, OKS = [], [0]
WAIVE = list(H311["WAIVE"])
# 0.3.12 by design in the older children (they still pass everything else)
WAIVE += [("L35: every 0.3.5 life check passes on 0.3.7 (292 ok) except the explained deviations: unexpected []",
           "every L35 check that ran passed or is an explained deviation (unexpected []); only the old >= 300 count (0.3.11 ran 293 - one more check is an explained 0.3.12 deviation: KCRUDE has 6 kinds)"),
          ("G36 P1: the pole's perks", "0.3.12 by design: LL.PK has 4 more perks (the watering can's cap / grow / last / bloom - mask bit 1 << 5, appended after the six old ones, whose order H312 D asserts); the pole still has Fortune / Wisdom / Steady Line only"),
          ("G36 P8: the Tools page lists FIVE tools", "0.3.12 by design: the Tools tab lists SIX tools (+ the watering can, compact rows: list 640 <= 656 - H312 F renders + validates it) and the pole's panel title reads 'Your fishing pole - Upgrade Points' (GearLL.kname)")]
WAIVED = []

# every engine boot of every child (the older ones too) registers our interaction type first - what the plugin's setup() does in the game
# (FarmingPlugin registers "UseWateringCan" the same way); without it the jar's SkyyGear_Can_Water would be an unknown Type in a bare boot
_ORIG_BOOT = H["engine_boot"]


def engine_boot_312(K):
    from jpype import JClass
    try:
        INTc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
        GCW = JClass(PKG + "GearCanWater")
        INTc.CODEC.register("SkyyGearCan", GCW.class_, GCW.codec())
    except Exception as e:
        K.notes.append("engine_boot_312: the SkyyGearCan type could not be registered: %s" % str(e)[:200])
    return _ORIG_BOOT(K)


for _d in (H, H35.get("H"), H36.get("H"), H37.get("H"), H38.get("H")):
    if isinstance(_d, dict) and "engine_boot" in _d:
        _d["engine_boot"] = engine_boot_312


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S312
def run_assets312():
    ea, eb = entries(J311), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    want_add = set(["Server/Item/Items/SkyyGear/%s.json" % i for i in CAN_IDS + HARV_IDS]
                   + ["Common/Icons/ItemsGenerated/%s.png" % i for i in CAN_IDS + HARV_IDS if i != "Tool_WaterCan_Iron"]
                   + ["Common/Items/SkyyGear/Can/Can_%s.png" % t for t in ("Crude", "Copper", "Thorium", "Cobalt", "Adamantite")]
                   + ["Common/Items/SkyyGear/Harvester/Harvester_%s.png" % t for t in ("Crude", "Copper", "Iron", "Thorium")]
                   + ["Server/Item/Interactions/SkyyGear/Can/SkyyGear_Can_Water.json", "Server/Item/RootInteractions/SkyyGear/SkyyGear_Can_Use.json",
                      "Server/Item/Animations/SkyyGear/SkyyGear_Harvester.json"]
                   + ["com/skyy/gear/%s.class" % c for c in NEW_CLASSES])
    check(set(added) == want_add and not gone and changed == ["Server/Languages/en-US/server.lang", "manifest.json"],
          "S312: 0.3.11 -> 0.3.12 adds exactly the cans / Harvesters / their art / the interaction / the classes, removes nothing, changes only "
          "manifest + lang: extra %s, missing %s, gone %s, changed %s" % (sorted(set(added) - want_add)[:4], sorted(want_add - set(added))[:4], gone[:3], changed))
    la, lb = ea["Server/Languages/en-US/server.lang"].decode("utf-8"), eb["Server/Languages/en-US/server.lang"].decode("utf-8")
    new_lines = [l for l in lb.split("\n") if l not in la.split("\n") and l.strip()]
    check([l for l in lb.split("\n") if l not in set(new_lines)] == la.split("\n"), "S312: server.lang only gains lines (the old ones in the same order)")
    tags = dict((l.split(" = ")[0], l.split(" = ", 1)[1]) for l in new_lines if " = " in l)
    check(len(tags) == 20 and tags.get("items.Tool_WaterCan_Crude.name") == "Crude Watering Can" and tags.get("items.Tool_WaterCan_Crude.description", "").startswith("T1 Crude - ")
          and tags.get("items.Tool_WaterCan_Adamantite.description", "").startswith("T6 Adamantite - ") and tags.get("items.Tool_Sickle_Harvester_Thorium.description", "").startswith("T4 Thorium - ")
          and tags.get("items.Tool_Sickle_Harvester_Iron.name") == "Iron Harvester", "S312: 20 lang lines, names + tier tags first ('T1 Crude - ...'): %s" % list(tags.items())[:3])
    for i in CAN_IDS:
        d = json.loads(eb["Server/Item/Items/SkyyGear/%s.json" % i])
        check(d["Interactions"]["Secondary"] == "SkyyGear_Can_Use" and d["MaxDurability"] == 100 and d["MaxStack"] == 1 and "BlockType" not in d
              and d["Repairable"] is False and d["DurabilityLossOnDeath"] is False and "Recipe" not in d and "State" not in d,
              "S312: %s = right-click SkyyGear_Can_Use, the water bar 100, never a block, not repairable, no death loss, no recipe, no states" % i)
    for i in HARV_IDS:
        d = json.loads(eb["Server/Item/Items/SkyyGear/%s.json" % i])
        check(d["Parent"].startswith("Tool_Sickle_") and d["Interactions"]["Secondary"] == "Hoe_Till" and "Sickle_Attack" in json.dumps(d["Interactions"]["Primary"])
              and d["PlayerAnimationsId"] == "SkyyGear_Harvester" and "Recipe" not in d, "S312: %s = a sickle (Parent %s) + the hoe's Hoe_Till, our animation set, no recipe" % (i, d["Parent"]))
    rt_ = json.loads(eb["Server/Item/RootInteractions/SkyyGear/SkyyGear_Can_Use.json"])
    check(rt_["Interactions"] == ["SkyyGear_Can_Water"] and "Settings" in rt_ and "FirstClick" not in json.dumps(rt_) and "Held" not in json.dumps(rt_),
          "S312 FIX: the can's root = the hoe's shape (Settings + ONE interaction, repeated while held; no FirstClick / charge): %s" % rt_["Interactions"])
    check("Hold right-click and look across tilled soil" in tags.get("items.Tool_WaterCan_Crude.description", ""), "S312 FIX: the can's description says hold and look across the soil")
    iw = json.loads(eb["Server/Item/Interactions/SkyyGear/Can/SkyyGear_Can_Water.json"])
    check(iw["Type"] == "SkyyGearCan" and iw["Duration"] == 86400 and iw["RadiusX"] == 1 and iw["UseLatestTarget"] is True, "S312: SkyyGear_Can_Water = type SkyyGearCan with vanilla's keys")
    an = json.loads(eb["Server/Item/Animations/SkyyGear/SkyyGear_Harvester.json"])
    check("Till" in an["Animations"] and "SwingLeft" in an["Animations"], "S312: the Harvester animation set has the hoe's Till and the sickle swings")
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.12"' in man and "LIFELONG WATERING CAN" in man and "HARVESTER" in man, "S312: the manifest names the round")
    ca = set(n for n in ea if n.endswith(".class"))
    cb = set(n for n in eb if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca & cb if ea[n] != eb[n])
    print("  class compare 0.3.11 -> 0.3.12: %d classes, %d changed (%s), new %s, gone %s"
          % (len(cb), len(chg), ", ".join(chg[:60]), sorted(n.rsplit("/", 1)[1][:-6] for n in cb - ca), sorted(ca - cb)))
    check(not (ca - cb) and sorted(n.rsplit("/", 1)[1][:-6] for n in cb - ca) == sorted(NEW_CLASSES), "S312: class compare - new classes = %s, none gone" % NEW_CLASSES)


# ====================================================================================================== H312
def run_h312(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    mtj = os.path.join(SCRATCH, "packs", "Multitools-1.2.9.jar")
    if os.path.isfile(H310["MT_SRC"]) and not os.path.isfile(mtj):
        shutil.copyfile(H310["MT_SRC"], mtj)
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h312(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H312: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h312(L, K):
    from jpype import JClass, JInt, JShort, JLong, JDouble, JObject, JArray, JString, JImplements, JOverride, JBoolean, JByte
    import skyyui as SUI
    br, Gear, Cfg = L["br"], L["Gear"], L["Cfg"]
    mkinv, world, PR1, PR2, U1, U2, stack, doc, skills, apply, logs, COINS = (L["mkinv"], L["world"], L["PR1"], L["PR2"], L["U1"], L["U2"], L["stack"],
                                                                            L["doc"], L["skills"], L["apply"], L["logs"], L["COINS"])
    us, jf, ITEM, lls, ids, E = L["us"], L["jf"], L["ITEM"], L["lls"], L["ids"], L["E"]
    P = lambda n: JClass(PKG + n)
    LL, Life, Can, Up, Data, Lvl, Ui, Stamp, Defs = (P("GearLL"), P("GearLife"), P("GearCan"), P("GearUp"), P("GearData"), P("GearLevel"), P("GearUi"),
                                                     P("GearStamp"), P("GearDefs"))
    GCW = P("GearCanWater")
    HAL = JClass("java.util.ArrayList")
    V3 = JClass("org.joml.Vector3i")
    Inst = JClass("java.time.Instant")
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    AR = E["AR"]

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))

    def kc(cond, what):
        K.check(bool(cond), what)

    # ============================================================== A: the assets in the engine
    miss = [i for i in CAN_IDS + HARV_IDS if ITEM.getAssetMap().getAsset(i) is None]
    kc(not miss, "A: the 6 cans + 4 Harvesters are in the Item store (missing %s)" % miss)
    bad = []
    for i in CAN_IDS + HARV_IDS:
        it = ITEM.getAssetMap().getAsset(i)
        if it is None:
            continue
        try:
            it.toPacket()
            if int(it.getMaxStack()) != 1:
                bad.append((i, "stack"))
            if i in CAN_IDS and (abs(float(it.getMaxDurability()) - 100.0) > 1e-9 or it.hasBlockType()):
                bad.append((i, "durability / block"))
        except Exception as e:
            bad.append((i, str(e)[:120]))
    kc(not bad, "A: every new item makes its packet, MaxStack 1, cans hold 100 water and are no block: %s" % bad)
    ist = AR.getAssetStore(INTc.class_)
    ia = ist.getAssetMap().getAsset("SkyyGear_Can_Water") if ist is not None else None
    UW = JClass("com.hypixel.hytale.builtin.adventure.farming.interactions.UseWateringCanInteraction")
    kc(ia is not None and str(ia.getClass().getName()) == PKG + "GearCanWater" and int(jf(UW, "radiusX").getInt(ia)) == 1
       and int(jf(UW, "duration").getLong(ia)) == 86400, "A: SkyyGear_Can_Water decodes as a GearCanWater (vanilla's keys: Radius 1, Duration 86400): %s" % (None if ia is None else ia.getClass().getName()))
    rst = AR.getAssetStore(ROOTc.class_)
    kc(rst is not None and rst.getAssetMap().getAsset("SkyyGear_Can_Use") is not None, "A: the root SkyyGear_Can_Use is loaded")
    IPA = JClass("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations")
    ast_ = AR.getAssetStore(IPA.class_)
    kc(ast_ is not None and ast_.getAssetMap().getAsset("SkyyGear_Harvester") is not None, "A: the SkyyGear_Harvester animation set is loaded")
    hv = ITEM.getAssetMap().getAsset("Tool_Sickle_Harvester_Iron")
    hi_ = str(hv.getInteractions()) if hv is not None else ""
    hc_ = ITEM.getAssetMap().getAsset("Tool_Sickle_Harvester_Crude")
    hci_ = str(hc_.getInteractions()) if hc_ is not None else ""
    kc("Secondary=Hoe_Till" in hi_ and "Primary=" in hi_ and "Primary=Sickle_Attack" in hci_ and "Secondary=Hoe_Till" in hci_, "A: the Harvesters' interactions = the sickle swing (Crude: Sickle_Attack, Iron: its inline copy) + Hoe_Till: %s / %s" % (hci_[:100], hi_[:100]))
    rec = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("WaterCan" in r[1] or "SkyyGear_Can" in r[1] or "Harvester" in r[1])]
    kc(not rec, "A: no load record about the cans / Harvesters / the interaction: %s" % [r[1][:160] for r in rec[:3]])

    # ============================================================== B: kinds, tiers, ladders, rows
    apply()
    kc([int(LL.kOf(i)) for i in CAN_IDS] == [5] * 6 and [int(LL.kOf(i)) for i in HARV_IDS] == [3] * 4 and int(LL.kOf("Tool_Watering_Can")) == -1
       and int(LL.CAN) == 5 and str(LL.KIND[5]) == "can", "B: the can = kind 5 'can', the Harvester = the sickle kind (3), the vanilla can no kind")
    kc([int(LL.tier(i)) for i in CAN_IDS] == [0, 1, 2, 3, 4, 5] and [int(LL.tier(i)) for i in HARV_IDS] == [0, 1, 2, 3], "B: tiers Crude 0 .. Adamantite 5 / Thorium 3")
    kc(int(Data.toolFam("Tool_Sickle_Harvester_Iron")) == 5 and int(Data.toolFam("Tool_WaterCan_Iron")) == 0 and int(Data.slotOf("Tool_WaterCan_Iron")) == 3
       and bool(Data.can("Tool_WaterCan_Crude")) and not bool(Data.can("Tool_Watering_Can")), "B: the Harvester is a sickle-family tool, the can a tool without a family")
    bands = [list(Lvl.band(i))[:2] for i in CAN_IDS]
    kc(bands[0][0] == 1 and bands[1][0] == 10 and bands[2][0] == 15 and bands[5][0] == 35, "B: the can's level bands follow its metal (Crude 1, Copper 10, Iron 15 .. Adamantite 35): %s" % bands)
    kc(str(LL.crudeOf(3, "Tool_Sickle_Harvester_Iron")) == "Tool_Sickle_Harvester_Crude" and str(LL.crudeOf(3, "Tool_Sickle_Iron")) == "Tool_Sickle_Crude"
       and str(LL.crudeOf(5, None)) == "Tool_WaterCan_Crude" and str(LL.kname(3, "Tool_Sickle_Harvester_Crude")) == "Harvester" and str(LL.kname(3, "Tool_Sickle_Crude")) == "Sickle"
       and str(LL.ladOf(3, "Tool_Sickle_Harvester_Copper")).startswith("Tool_Sickle_Harvester_Crude,") and str(LL.KLAD[5]).startswith("Tool_WaterCan_Crude,"),
       "B: crudeOf / kname / ladOf answer the Harvester's own ladder, the can's Crude")
    lad = str(LL.ladders())
    kc("Tool_WaterCan_Crude>Tool_WaterCan_Copper(Ingredient_Bar_Copper*25)" in lad and "Tool_Sickle_Harvester_Iron(Skyy_Ench_Carrot*1)" in lad and lad.index("Tool_WaterCan_Crude>") < lad.index(str(Cfg.GARM_LADDERS))
       and str(Up.next("Tool_WaterCan_Crude")) == "Tool_WaterCan_Copper" and str(Up.next("Tool_WaterCan_Cobalt")) == "Tool_WaterCan_Adamantite" and Up.next("Tool_WaterCan_Adamantite") is None
       and str(Up.next("Tool_Sickle_Harvester_Iron")) == "Tool_Sickle_Harvester_Thorium" and Up.next("Tool_Sickle_Harvester_Thorium") is None,
       "B: GearLL.ladders = ... + can.ladders + harvester.ladders + the gathering armor (last): the can climbs to Adamantite, the Harvester to Thorium")
    kc(Up.checkLadders("can.ladders", Cfg.CAN_LADDERS) is None and Up.checkLadders("harvester.ladders", Cfg.HARV_LADDERS) is None,
       "B: both ladders pass GearUp.checkLadders with the real items (Enchanted Carrot / Cauliflower / Pumpkin / Tomato)")
    apply(part__lifelong="false")
    kc("WaterCan" not in str(LL.ladders()), "B: part.lifelong off = no can / Harvester ladders")
    apply()
    kc(bool(LL.noCraft("Tool_Watering_Can")) and not bool(LL.noCraft("Tool_Shovel_Iron")), "B: the vanilla Iron Watering Can is not crafted (can.noVanilla on)")
    apply(can__noVanilla="false")
    kc(not bool(LL.noCraft("Tool_Watering_Can")), "B: can.noVanilla off = the vanilla can crafts again")
    apply()
    CRows = P("CfgRows")
    keys = ["part.can", "lifelong.canKit", "can.area", "can.uses", "can.waterSec", "can.holdSec", "can.capacityPct", "can.growPct", "can.lastPct", "can.bloomPct", "can.noVanilla",
            "can.ladders", "part.harvester", "harvester.rebirthGate", "harvester.ladders"]
    kc(all(int(CRows.index(k)) >= 0 for k in keys), "B: the 15 new Server Setup rows exist (fix round 2: + can.holdSec)")
    kc(chr(10) + "can.holdSec=0.7" + chr(10) in L["FRESH"], "B FIX2: a fresh config.properties lists can.holdSec=0.7")
    FRESH = L["FRESH"]
    kc("# ---- the lifelong watering can, the Harvester (SkyyGear 0.3.12) ----" in FRESH and "\ncan.area=1,3,5,7,9,11\n" in FRESH and "\nharvester.rebirthGate=false\n" in FRESH,
       "B: a fresh config.properties lists the 0.3.12 block")
    kc(Can.checkArea("can.area", "1,3,5") is not None and Can.checkArea("can.area", "1,3,5,7,9,10") is not None and Can.checkArea("can.area", "1,1,1,1,1,1") is None
       and Can.checkUses("can.uses", "0,1,1,1,1,1") is not None and Can.checkUses("can.uses", "5,5,5,5,5,5") is None, "B: the area / uses row checks")
    eq([int(Can.side(t)) for t in range(7)], [1, 3, 5, 7, 9, 11, 11], "B: the square by tier (T1 1x1, T2 3x3, T3 5x5, T4 7x7 ...), clamped above")
    apply(can__area="3,3,3,3,3,3")
    eq(int(Can.side(0)), 3, "B: can.area is live")
    apply(can__area="bad")
    eq(int(Can.side(1)), 3, "B: a bad can.area = the default (one WARN)")
    apply()

    # ============================================================== C: the can in the starting kit
    L["wipe_home"]()
    FB = JClass("com.skyy.fishing.FishBridge")
    FB.questInit()
    skills(Mining=4, Foraging=4, Farming=4, Fishing=4)
    inv, cs = mkinv()
    Life.sweep(PR1, inv, True)
    pk = str(Gear.pkey(U1))
    REG = LL.reg(pk)
    mine = lls(cs, pk)
    cans = [x for x in mine if x[2] == 5]
    kc(len(cans) == 1 and str(cans[0][6].getItemId()) == "Tool_WaterCan_Crude" and str(REG.getProperty("canKit")) == "1" and str(REG.getProperty("canKitHow")) == "give"
       and cans[0][3] == str(REG.getProperty("can.uid")) and str(REG.getProperty("canKitUid")) == cans[0][3] and REG.getProperty("pole.uid") is not None
       and len([x for x in mine if x[2] in (0, 1, 2, 3)]) == 4, "C: a fresh profile: the four tools + the pole + ONE Crude Watering Can (canKit=1, how give, the uid): %s" % [(x[2], str(x[6].getItemId())) for x in mine])
    can0 = cans[0][6]
    kc(abs(float(can0.getDurability()) - 100.0) < 1e-9 and str(REG.getProperty("can.seen")) == "1", "C: the can arrives full (100) and the look saw it")
    tips = [str(x) for x in Life.N]
    LL.LAST.clear()
    Life.sweep(PR1, inv, True)
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PR1, inv, True)
    eq(len([x for x in lls(cs, pk) if x[2] == 5]), 1, "C: a second look and a restart give nothing more (one can)")
    sec, slot = cans[0][0], cans[0][1]
    cs[sec].removeItemStackFromSlot(JShort(slot))
    LL.LAST.clear()
    Life.sweep(PR1, inv, True)
    eq(len([x for x in lls(cs, pk) if x[2] == 5]), 0, "C: a LOST can is not given again by the look (canKit=1)")
    refR, stR, chR, plR = world(inv, cs, PR1)
    r_rc = str(Life.reclaim(PR1, plR, JInt(5)))
    cc = [x for x in lls(cs, pk) if x[2] == 5]
    kc(r_rc.startswith("+") and len(cc) == 1 and str(cc[0][6].getItemId()) == "Tool_WaterCan_Crude", "C: /can makes an exact copy of the lost can: %s" % r_rc[:120])
    kc(int(Life.CK[0]) >= 1, "C: counters %s" % [int(x) for x in Life.CK])
    # a crash right after the journal: the next look gives it with the SAME uid
    inv2, cs2 = mkinv()
    pk2 = str(Gear.pkey(U2))
    skills(u=U2, Mining=4, Foraging=4, Farming=4, Fishing=4)
    Life.sweep(PR2, inv2, True)          # the four + the pole (the can is the 6th give: crash it on its journal)
    R2 = LL.reg(pk2)
    for x in [x for x in lls(cs2, pk2) if x[2] == 5]:
        cs2[x[0]].removeItemStackFromSlot(JShort(x[1]))
    for k_ in ("can.uid", "can.id", "can.rp", "can.seen", "canKit", "canKitHow", "canKitUid", "canKitAt"):
        R2.remove(k_)
    LL.save(pk2, R2)
    LL.REG.clear()
    LL.LAST.clear()
    Life.CRASH_AT = JInt(4)
    try:
        Life.sweep(PR2, inv2, True)
    except Exception:
        pass
    Life.CRASH_AT = JInt(0)
    LL.LAST.clear()
    pend = LL.reg(pk2).getProperty("can.pend")
    LL.REG.clear()
    Life.sweep(PR2, inv2, True)
    R2 = LL.reg(pk2)
    c2 = [x for x in lls(cs2, pk2) if x[2] == 5]
    kc(pend is not None and len(c2) == 1 and str(R2.getProperty("can.uid")) == str(pend) and str(R2.getProperty("canKit")) == "1",
       "C: a crash after the journal: the next look gives the can with the journal's uid (%s), one can" % pend)
    # the REDO path: the registry reached the disk, the can never did
    U5 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000e5")
    L["PKEY"][str(U5)] = "p5"
    PR5 = L["mkpr"](U5, "Fifth")
    skills(u=U5, Mining=4, Foraging=4, Farming=4, Fishing=4)
    inv5, cs5 = mkinv()
    Life.sweep(PR5, inv5, True)
    R5 = LL.reg("p5")
    u5a = str(R5.getProperty("can.uid"))
    for x in [x for x in lls(cs5, "p5") if x[2] == 5]:
        cs5[x[0]].removeItemStackFromSlot(JShort(x[1]))
    R5.remove("can.seen")
    LL.save("p5", R5)
    LL.REG.clear()
    LL.LAST.clear()
    logs()
    Life.sweep(PR5, inv5, True)
    R5 = LL.reg("p5")
    c5 = [x for x in lls(cs5, "p5") if x[2] == 5]
    kc(len(c5) == 1 and str(R5.getProperty("can.uid")) != u5a and [x for x in logs() if "LL-CANKIT-REDO" in x], "C: the kit's can never arrived -> LL-CANKIT-REDO gives ONE new can")
    # an existing profile (migrated before 0.3.12, no can): gets one at its next look
    U3 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000c3")
    L["PKEY"][str(U3)] = "p3"
    PR3 = L["mkpr"](U3, "Third")
    skills(u=U3, Mining=4, Foraging=4, Farming=4, Fishing=4)
    inv3, cs3 = mkinv()
    apply(lifelong__canKit="false")
    Life.sweep(PR3, inv3, True)
    R3 = LL.reg("p3")
    kc(R3.getProperty("can.uid") is None and not [x for x in lls(cs3, "p3") if x[2] == 5] and str(R3.getProperty("migrated")) == "1",
       "C: lifelong.canKit off = a profile gets no can (it migrates as before)")
    apply()
    LL.LAST.clear()
    Life.sweep(PR3, inv3, True)
    kc(len([x for x in lls(cs3, "p3") if x[2] == 5]) == 1 and str(LL.reg("p3").getProperty("canKit")) == "1", "C: kit on again: the existing profile gets its can ONCE at the next look")

    # ============================================================== D: the points + the plan
    skills(Farming=30)
    cc = [x for x in lls(cs, pk) if x[2] == 5]
    canS = cc[0][6]
    dC = doc(canS)
    p0 = [float(x) for x in Can.plan(U1, JString("Tool_WaterCan_Crude"), dC, JDouble(100.0))]
    kc(p0[0] == 1 and p0[1] == 86400 and abs(p0[2] - 5.0) < 1e-9 and p0[3] == 0 and p0[4] == 0, "D: a plain Crude can: 1x1, 86400 s, 100 / 20 waterings = 5 water a watering, no growth / bloom: %s" % p0[:5])
    r_b = [str(Life.buy(U1, JInt(5), JInt(int(LL.PK_CAP)))) for _ in range(2)] + [str(Life.buy(U1, JInt(5), JInt(int(LL.PK_GROW)))), str(Life.buy(U1, JInt(5), JInt(int(LL.PK_LAST)))),
                                                                                    str(Life.buy(U1, JInt(5), JInt(int(LL.PK_BLOOM))))]
    kc(all(x.startswith("+") for x in r_b), "D: Capacity 2, Growth 1, Lasting 1, Bloom 1 bought with Farming points: %s" % r_b)
    kc(str(Life.buy(U1, JInt(0), JInt(int(LL.PK_CAP)))).startswith("-") and str(Life.buy(U1, JInt(5), JInt(1))).startswith("-"),
       "D: Capacity is no pickaxe upgrade; Fortune is no can upgrade")
    p1 = [float(x) for x in Can.plan(U1, JString("Tool_WaterCan_Crude"), dC, JDouble(100.0))]
    kc(abs(p1[1] - 86400 * 1.2) < 1e-6 and abs(p1[2] - 100.0 / (20 * 1.4)) < 1e-9 and abs(p1[3] - 0.04 * 86400) < 1e-6 and abs(p1[4] - 6.0) < 1e-9,
       "D: the plan with the points: Lasting +20%% time, Capacity 2 = 40%% more waterings, Growth 4%% of the wet time, Bloom 6%%: %s" % p1[:5])
    p2 = [float(x) for x in Can.plan(U2, JString("Tool_WaterCan_Crude"), dC, JDouble(100.0))]
    kc(p2[2] == 5.0 and p2[3] == 0 and p2[4] == 0, "D: another player holding your can gets none of your points")
    LP = P("LifePage")
    kc(str(LP.effect(JInt(5), JInt(int(LL.PK_CAP)), JInt(5))) == "never runs dry" and "growth" in str(LP.effect(JInt(5), JInt(int(LL.PK_GROW)), JInt(1)))
       and "fertilize" in str(LP.effect(JInt(5), JInt(int(LL.PK_BLOOM)), JInt(2))), "D: the Tools tab's effect words for the can's points")

    # ============================================================== E: the click (the REAL GearCanWater.interactWithBlock, the world through seams)
    ST = {"pr": PR1, "held": None, "failed": False, "set": [], "time": Inst.ofEpochSecond(JLong(1000000)), "axis": JArray(JInt)([0, -1]), "eye": None, "super": []}
    SOILS = {}
    WATER = set()

    @JImplements("java.util.function.Function")
    class CtxFn(object):
        @JOverride
        def apply(self, o):
            op = str(o[0])
            if op == "pr":
                return ST["pr"]
            if op == "held":
                return ST["held"]
            if op == "set":
                ST["held"] = o[1]
                ST["set"].append(o[1])
                return None
            if op == "fail":
                ST["failed"] = True
                return None
            if op == "failed":
                return JBoolean(ST["failed"])
            if op == "time":
                return ST["time"]
            if op == "axis":
                return ST["axis"]
            if op == "eye":
                return ST["eye"]
            return None

    @JImplements("java.util.function.Function")
    class SoilFn(object):
        @JOverride
        def apply(self, o):
            op = str(o[0])
            x, z = int(o[1]), int(o[3])
            s = SOILS.get((x, z))
            if op == "get":
                if s is None:
                    return None
                return JArray(JObject)([s["until"], JObject(JBoolean(s["fert"]), JClass("java.lang.Boolean")), JObject(JInt(s["y"]), JClass("java.lang.Integer"))])
            if op == "fert":
                if s is None:
                    return JBoolean(False)
                s["fert"] = True
                return JBoolean(True)
            if op == "grow":
                if s is None or s.get("crop") is None:
                    return JBoolean(False)
                s["crop"] = s["crop"] - int(o[4])
                return JBoolean(True)
            return None

    @JImplements("java.util.function.Function")
    class FluidFn(object):
        @JOverride
        def apply(self, o):
            return JBoolean((int(o[0]), int(o[1]), int(o[2])) in WATER)

    @JImplements("java.util.function.Function")
    class SuperFn(object):
        """vanilla UseWateringCan.interactWithBlock: its own cell loop (width centred, depth away), soil at y or y-1 gets now + dur"""
        @JOverride
        def apply(self, o):
            pos, side, dur = o[0], int(o[1]), int(o[2])
            ST["super"].append((int(pos.x()), int(pos.y()), int(pos.z()), side, dur))
            ax0, az0 = int(ST["axis"][0]), int(ST["axis"][1])
            if ax0 != 0 and az0 != 0:
                ax0 = 0
            fx, fz = (1 if az0 != 0 else 0), (1 if ax0 != 0 else 0)
            lo = (side - 1) // 2
            hi = side - 1 - lo
            any_ = False
            for dz in range(side):
                for dx in range(-lo, hi + 1):
                    x = int(pos.x()) + dx * fx + dz * ax0
                    z = int(pos.z()) + dx * fz + dz * az0
                    s = SOILS.get((x, z))
                    if s is not None:
                        s["until"] = ST["time"].plusSeconds(JLong(dur))
                        any_ = True
            if not any_:
                ST["failed"] = True
            return None
    Can.CTX = CtxFn()
    Can.SOIL = SoilFn()
    Can.FLUID = FluidFn()
    Can.SUPER = SuperFn()
    Can.RNG = JClass("java.util.Random")(JLong(7))
    w_ = GCW()
    IWB = [m for m in GCW.class_.getDeclaredMethods() if str(m.getName()) == "interactWithBlock"][0]
    IWB.setAccessible(True)
    POS = V3(JInt(0), JInt(64), JInt(0))

    def click(held, pr=PR1, keep=False, pos=None):
        if not keep:
            Can.LAST.clear()          # fix round: every plain click is a NEW press (the hold-and-sweep window starts over)
        ST["pr"] = pr
        ST["held"] = held
        ST["failed"] = False
        ST["set"] = []
        ST["super"] = []
        IWB.invoke(w_, JArray(JObject)([None, None, None, None, held, POS if pos is None else pos, None]))
        return ST["held"]

    def soils(cells, wet=False, crop=None):
        SOILS.clear()
        for x, z in cells:
            SOILS[(x, z)] = {"y": 63, "until": ST["time"].plusSeconds(JLong(500)) if wet else None, "fert": False, "crop": crop}
    # reset the can's points to none for the plain rows first
    R1 = LL.reg(pk)
    for p_ in ("cap", "grow", "last", "bloom"):
        R1.remove("can.up." + p_)
    LL.save(pk, R1)
    soils([(0, 0)])
    n0 = [int(x) for x in Can.N]
    h1 = click(canS)
    kc(len(ST["super"]) == 1 and ST["super"][0][3] == 1 and ST["super"][0][4] == 86400 and SOILS[(0, 0)]["until"] is not None and not ST["failed"]
       and abs(float(h1.getDurability()) - 95.0) < 1e-9 and str(LL.uid(doc(h1))) == str(LL.uid(dC)),
       "E: a Crude can on dry soil: vanilla's watering runs with side 1 / 86400 s, the soil is wet, the bar 100 -> 95, the lifelong document kept: %s" % ST["super"])
    kc(int(Can.N[4]) - n0[4] == 1, "E: counted one dry soil watered")
    # Copper (3x3) in vanilla's own cell order, facing -z
    cop = Data.put(stack("Tool_WaterCan_Copper"), doc(canS), U1)
    cells9 = [(x, z) for x in (-1, 0, 1) for z in (0, -1, -2)]
    soils(cells9)
    click(cop)
    kc(ST["super"] and ST["super"][0][3] == 3 and all(SOILS[c]["until"] is not None for c in cells9), "E: a Copper can = 3x3 (width centred, 3 deep away from you) - all 9 soils wet")
    rr = JClass("java.util.ArrayList")
    cl_ = Can.cells(None, None, None, POS, JInt(3), ST["time"])
    got_c = sorted((int(cl_.get(i)[0][0]), int(cl_.get(i)[0][2])) for i in range(int(cl_.size())))
    eq(got_c, sorted(cells9), "E: GearCan.cells = vanilla's own cells for the same facing")
    ST["axis"] = JArray(JInt)([1, 0])
    cl2 = Can.cells(None, None, None, POS, JInt(3), ST["time"])
    eq(sorted((int(cl2.get(i)[0][0]), int(cl2.get(i)[0][2])) for i in range(int(cl2.size()))), sorted((x, z) for x in (0, 1, 2) for z in (-1, 0, 1)),
       "E: facing +x = 3 wide along z, 3 deep along x")
    ST["axis"] = JArray(JInt)([0, -1])
    # refill on water
    WATER.add((0, 65, 0))
    half = canS.withDurability(JDouble(40.0))
    h2 = click(half)
    kc(not ST["super"] and abs(float(h2.getDurability()) - 100.0) < 1e-9 and any("full" in s for s in L["said"](PR1)[-2:]), "E: water above the block you look at = REFILL (100), no watering")
    WATER.clear()
    ST["eye"] = JArray(JDouble)([0.5, 66.6, 3.5])
    WATER.add((0, 65, 1))
    h2b = click(half)
    kc(not ST["super"] and abs(float(h2b.getDurability()) - 100.0) < 1e-9, "E: water between your eye and the block = REFILL (the fill raycast)")
    WATER.clear()
    ST["eye"] = None
    # empty
    soils([(0, 0)])
    empty = canS.withDurability(JDouble(0.0))
    h3 = click(empty)
    kc(not ST["super"] and ST["failed"] and any("empty" in s for s in L["said"](PR1)[-2:]), "E: an empty can is refused ('right-click water to fill it'), nothing watered")
    # FIX (UNVERIFIED 0-durability): the last watering leaves the bar at EMPTY (0.001), never 0; that can is empty (refused) and still refills
    soils([(0, 0)])
    lastw = canS.withDurability(JDouble(3.0))
    h3b = click(lastw)
    kc(ST["super"] and abs(float(h3b.getDurability()) - float(Can.EMPTY)) < 1e-12 and float(h3b.getDurability()) > 0.0 and any("empty now" in s for s in L["said"](PR1)[-2:]),
       "E FIX: the last watering leaves the bar at %s (never 0 = never a 'broken' tool), 'empty now': %s" % (float(Can.EMPTY), float(h3b.getDurability())))
    h3c = click(h3b)
    kc(not ST["super"] and ST["failed"], "E FIX: ... a can at EMPTY is refused as empty")
    WATER.add((0, 65, 0))
    h3d = click(h3b)
    kc(abs(float(h3d.getDurability()) - 100.0) < 1e-9, "E FIX: ... and refills on water (100)")
    WATER.clear()
    # FIX (Skyy 2026-10-16 hold-and-sweep): hold the button (the root repeats like the hoe's) and look across a row: each NEW block is watered,
    # the same block again is skipped (no water), soil this can already wet is skipped on a repeat (no water)
    row3 = [(0, 0), (1, 0), (2, 0)]
    soils(row3)
    Can.LAST.clear()
    hs = canS
    seen = []
    for (x_, z_) in row3:
        hs = click(hs, keep=True, pos=V3(JInt(x_), JInt(64), JInt(z_)))
        seen.append((len(ST["super"]), round(float(hs.getDurability()), 6)))
    kc([a for a, b in seen] == [1, 1, 1] and all(SOILS[c]["until"] is not None for c in row3) and abs(float(hs.getDurability()) - (float(canS.getDurability()) - 15.0)) < 1e-9,
       "E FIX: holding over three blocks waters three squares (5 water each): %s" % seen)
    n10 = int(Can.N[10])
    hs2 = click(hs, keep=True, pos=V3(JInt(2), JInt(64), JInt(0)))
    kc(not ST["super"] and not ST["failed"] and abs(float(hs2.getDurability()) - float(hs.getDurability())) < 1e-12 and int(Can.N[10]) == n10 + 1,
       "E FIX: still held on the same block = skipped (no watering, no water, no 'failed')")
    n11 = int(Can.N[11])
    hs3 = click(hs2, keep=True, pos=V3(JInt(1), JInt(64), JInt(0)))
    kc(not ST["super"] and abs(float(hs3.getDurability()) - float(hs2.getDurability())) < 1e-12 and int(Can.N[11]) == n11 + 1,
       "E FIX: held back over soil it already wet = skipped (no water used)")
    hs4 = click(hs3, pos=V3(JInt(1), JInt(64), JInt(0)))
    kc(len(ST["super"]) == 1 and float(hs4.getDurability()) < float(hs3.getDurability()), "E FIX: a NEW press on wet soil still waters it (re-wets, uses water) - as before")
    old_hold = int(Can.HOLD_MS)
    Can.HOLD_MS = JLong(0)
    hs5 = click(hs4, keep=True, pos=V3(JInt(1), JInt(64), JInt(0)))
    kc(len(ST["super"]) == 1, "E FIX: after the hold window (HOLD_MS) the same block is a new press again")
    Can.HOLD_MS = JLong(old_hold)
    # FIX 2 (critic C4): the hold window is the Server Setup row can.holdSec (seconds); HOLD_MS is a harness seam only (-1 = off)
    hw0 = int(Can.holdMs())
    apply(can__holdSec="1.5")
    hw1 = int(Can.holdMs())
    apply(can__holdSec="99")
    hw2 = int(Can.holdMs())
    apply()
    kc(old_hold == -1 and hw0 == 700 and hw1 == 1500 and hw2 == 3000 and int(Can.holdMs()) == 700,
       "E FIX2: the hold window = can.holdSec (default 0.7 s = 700 ms; 1.5 -> 1500; clamped to 3 s): %s" % [old_hold, hw0, hw1, hw2])
    # FIX 2 (critic B2): the hold memory goes with the player (GearFx.forget)
    Can.LAST.put(U2, JArray(JLong)([1, 2, 3, 4]))
    P("GearFx").forget(U2)
    kc(not Can.LAST.containsKey(U2), "E FIX2: GearFx.forget drops the player's GearCan.LAST entry")
    # nothing watered = no water used
    SOILS.clear()
    h4 = click(canS)
    kc(ST["super"] and ST["failed"] and abs(float(h4.getDurability()) - float(canS.getDurability())) < 1e-9, "E: no soil in the square (vanilla marks it Failed) = no water used")
    # wet soil: water used, no Bloom / Growth
    for p_, n_ in (("bloom", "5"), ("grow", "2")):
        R1.setProperty("can.up." + p_, n_)
    LL.save(pk, R1)
    apply(can__bloomPct="50")
    soils([(0, 0)], wet=True, crop=10000)
    h5 = click(canS)
    kc(not SOILS[(0, 0)]["fert"] and SOILS[(0, 0)]["crop"] == 10000 and float(h5.getDurability()) < float(canS.getDurability()),
       "E: already wet soil: watered + water used, but no Bloom / Growth (no double dipping)")
    soils([(0, 0)], crop=10000)
    click(canS)
    kc(SOILS[(0, 0)]["fert"] and SOILS[(0, 0)]["crop"] == 10000 - int(0.08 * 86400), "E: dry soil: Bloom 5 x 50%% = 100%% fertilized, Growth 2 = the crop ticks %d game s ahead" % int(0.08 * 86400))
    apply()
    # Lasting = the time handed to vanilla
    R1.setProperty("can.up.last", "3")
    LL.save(pk, R1)
    soils([(0, 0)])
    click(canS)
    eq(ST["super"][0][4], int(86400 * 1.6), "E: Lasting Water 3 = 86400 x 1.6 s handed to vanilla's watering")
    # Capacity 5 = never runs dry
    R1.setProperty("can.up.cap", "5")
    LL.save(pk, R1)
    soils([(0, 0)])
    n7 = int(Can.N[7])
    h6 = click(canS)
    kc(abs(float(h6.getDurability()) - float(canS.getDurability())) < 1e-9 and int(Can.N[7]) == n7 + 1, "E: Capacity 5 = the bar never goes down")
    for p_ in ("cap", "grow", "last", "bloom"):
        R1.remove("can.up." + p_)
    LL.save(pk, R1)
    # a foreign can / part.can off
    soils([(0, 0)])
    click(canS, pr=PR2)
    kc(not ST["super"] and ST["failed"] and any("another player's watering can" in s for s in L["said"](PR2)[-2:]), "E: another player's lifelong can waters nothing for you")
    apply(part__can="false")
    click(canS)
    kc(not ST["super"] and ST["failed"], "E: part.can off = the can does nothing")
    apply()
    ST["held"] = None
    kc(Can.before(None, None, None, stack("Tool_Hoe_Crude"), POS) is None, "E: not a can -> null (vanilla's own code would run)")
    # waterAs puts the shared fields back even when vanilla's code throws (no world): the REAL super path
    Can.SUPER = None
    WA = [m for m in GCW.class_.getDeclaredMethods() if str(m.getName()) == "waterAs"][0]
    f0 = (int(jf(UW, "radiusX").getInt(w_)), int(jf(UW, "radiusZ").getInt(w_)), int(jf(UW, "duration").getLong(w_)))
    thrown = False
    try:
        WA.invoke(w_, JArray(JObject)([None, None, None, None, canS, POS, None, JInt(7), JLong(1234)]))
    except Exception:
        thrown = True
    kc(thrown and (int(jf(UW, "radiusX").getInt(w_)), int(jf(UW, "radiusZ").getInt(w_)), int(jf(UW, "duration").getLong(w_))) == f0,
       "E: waterAs on the REAL vanilla code (no world -> it throws): radiusX / radiusZ / duration are put back (finally)")
    Can.SUPER = SuperFn()
    # the engine glue with no world answers safely (the in-game paths are the same calls as vanilla's - UNVERIFIED until the game)
    Can.SOIL = None
    Can.FLUID = None
    Can.CTX = None
    kc(Can.soil(None, JInt(0), JInt(0), JInt(0)) is None and not bool(Can.isWater(None, JInt(0), JInt(0), JInt(0))) and not bool(Can.water(None, None, None, POS))
       and Can.prOf(None, None) is None and Can.held(None, canS) == canS and not bool(Can.setHeld(None, canS)) and not bool(Can.failed(None))
       and list(Can.axis(None, None)) == [0, -1] and Can.eye(None, None) is None and Can.gameTime(None) is None
       and not bool(Can.grow(None, JArray(JObject)([None, None, JObject(JInt(63), JClass("java.lang.Integer"))]), JInt(0), JInt(0), JLong(5), None))
       and not bool(Can.fert(None, JArray(JObject)([None, None, JObject(JInt(63), JClass("java.lang.Integer")), None]), JInt(0), JInt(0))) and int(Can.fluidId("Water")) >= -1,
       "E: the engine glue with no world / no context answers safely")
    Can.fail(None)
    Can.CTX = CtxFn()
    Can.SOIL = SoilFn()
    Can.FLUID = FluidFn()
    tip = HAL()
    tic = HAL()
    P("GearTool").lines(U1, JString("Tool_WaterCan_Copper"), doc(canS), tip, tic)
    tl = [str(x) for x in tip]
    kc(any("Waters 3x3" in x for x in tl) and any("30 waterings per fill" in x for x in tl) and any("Lifelong watering can: levels with Farming" in x for x in tl)
       and any("/can" in x for x in tl), "E: the can's tooltip: the square, the waterings, the lifelong lines: %s" % tl)

    # ============================================================== F: the Harvester
    L["wipe_home"]()
    skills(Mining=4, Foraging=4, Farming=30, Fishing=4)
    invH, csH = mkinv()
    Life.sweep(PR1, invH, True)
    RH = LL.reg(pk)
    hoeX = [x for x in lls(csH, pk) if x[2] == 2][0]
    sicX = [x for x in lls(csH, pk) if x[2] == 3][0]
    # the hoe: Rare with a farming line, Copper; the sickle Crude; points: hoe Fortune 3, sickle Wisdom 2 (cost 4)
    TM = [int(x) for x in Defs.S_TMASK]
    fl = [str(Defs.S_KEY[i]) for i in range(len(TM)) if TM[i] & (1 << 5)]
    hd = doc(hoeX[6]).clone()
    hd.put("r", JClass("org.bson.BsonString")("rare"))
    ms = JClass("org.bson.BsonArray")()
    ms.add(Data.mod(JString(fl[0]), JInt(1)))
    hd.put("mods", ms)
    csH[hoeX[0]].setItemStackForSlot(JShort(hoeX[1]), Data.put(Data.carry(stack("Tool_Hoe_Copper"), hoeX[6]), hd, U1))
    RH.setProperty("hoe.up.fort", "3")
    RH.setProperty("sickle.up.wis", "2")
    LL.save(pk, RH)
    LL.LAST.clear()
    Life.sweep(PR1, invH, True)
    RH = LL.reg(pk)
    siU0 = str(RH.getProperty("sickle.uid"))
    hoU0 = str(RH.getProperty("hoe.uid"))
    hoeStack = [x for x in lls(csH, pk) if x[2] == 2][0][6]
    # the Tools tab (REAL LifePage) with a counting PageManager
    FPM = JClass(FAKE_PKG + ".FakePM10")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    ref, st, ch, pl = world(invH, csH, PR1)
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
    ALIGN, ELEM_RE, strip_q = H39["ALIGN"], H39["ELEM_RE"], H39["strip_q"]
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

    def pclick(pg_, data):
        p0, c0 = int(FPM.packets), int(FPM.closes)
        pg_.handleDataEvent(ref, st, data)
        return int(FPM.packets) - p0 + int(FPM.closes) - c0
    lp = LP(PR1)
    FPM.cur = lp
    txt0 = render(lp)[0]
    rows0 = sorted(set(re.findall(r"#SkyyGLRow(\d) ", txt0)))
    kc(rows0 == ["0", "1", "2", "3", "4", "5"] and "(Height: 90)" in txt0 and ("Watering Can" in txt0 or "WaterCan" in txt0), "F: the Tools tab lists 6 tools (+ the can) in the compact rows: %s" % rows0)
    lp.sel = JInt(2)
    txh, clh, evh, edh = render(lp)
    tok = int(lp.tok)
    kc("Make Harvester" in txh and ("hv:%d" % tok) in " ".join(edh) and "Harvester: " in txh and "Both are used up" in txh, "F: the hoe panel offers 'Make Harvester' (the pair named + the fix-round-2 preview) with this build's token")
    lp.sel = JInt(5)
    txc = render(lp)[0]
    kc("Your watering can - Upgrade Points" in txc and "Capacity" in txc and "Growth Boost" in txc and "Lasting Water" in txc and "Bloom" in txc and "Make Harvester" not in txc,
       "F: the can panel: its four points, no Harvester row")
    # the gate
    apply(harvester__rebirthGate="true")

    @JImplements("java.util.function.Function")
    class RbCount(object):
        @JOverride
        def apply(self, o):
            return JObject(JInt(0), JClass("java.lang.Integer"))
    br.put("rebirth:fn:count", RbCount())
    br.put("rebirth:n:" + str(U1), JObject(JInt(0), JClass("java.lang.Integer")))
    kc(str(Life.harvGate(U1)) == "The Harvester comes after your first rebirth.", "F: harvester.rebirthGate on + rebirth 0 = refused ('after your first rebirth')")
    lp.sel = JInt(2)
    kc("Rebirth 1" in render(lp)[0], "F: ... the button reads 'Rebirth 1'")
    br.put("rebirth:n:" + str(U1), JObject(JInt(1), JClass("java.lang.Integer")))
    kc(Life.harvGate(U1) is None, "F: rebirth 1 = open")
    br.remove("rebirth:fn:count")
    br.remove("rebirth:n:" + str(U1))
    apply()
    # THE MERGE (the click)
    lp.sel = JInt(2)
    txp = render(lp)[0]
    logs()
    # FIX 2 (critic A1): the row shows what is kept / lost; the FIRST click only arms (nothing changes), the second within 8 s merges
    kc("keeps" in txp and "Harvester:" in txp and "Both are used up" in txp, "F FIX2: the Harvester row previews the merge (rarity, lines kept / lost): %s"
       % [l for l in txp.split(chr(10)) if "SkyyGPHv|" in l or "#SkyyGPHv." in l][:1])
    a0 = pclick(lp, '{"a":"hv:%d"}' % int(lp.tok))
    txa = render(lp)[0]
    kc(str(lp.info).startswith("=") and [x for x in lls(csH, pk) if x[2] == 2] and LL.reg(pk).getProperty("harv") is None and LL.reg(pk).getProperty("harv.pend") is None
       and "Click again" in txa and "can't be undone" in txa, "F FIX2: the first Make Harvester click only arms it (hoe still there, no journal), the row says 'Click again': %s" % lp.info)
    sv_ = lp.hvKey
    lp.hvKey = "0/0/x/0|0/0/y/0"
    pclick(lp, '{"a":"hv:%d"}' % int(lp.tok))
    kc(str(lp.info).startswith("-Your tools changed") and LL.reg(pk).getProperty("harv") is None, "F FIX2: a pair that is not the one drawn is refused: %s" % lp.info)
    render(lp)
    pclick(lp, '{"a":"hv:%d"}' % int(lp.tok))          # arms again (the refused click dropped the arming)
    render(lp)
    a1 = pclick(lp, '{"a":"hv:%d"}' % int(lp.tok))
    RH = LL.reg(pk)
    hv_ = [x for x in lls(csH, pk) if x[2] == 3]
    hd_ = doc(hv_[0][6]) if hv_ else None
    lg = logs()
    kc(a1 == 1 and str(lp.info).startswith("+") and len(hv_) == 1 and str(hv_[0][6].getItemId()) == "Tool_Sickle_Harvester_Copper" and hv_[0][3] == siU0
       and not [x for x in lls(csH, pk) if x[2] == 2] and not [i for i in ids(csH) if i.startswith("Tool_Hoe_")],
       "F: Make Harvester: the hoe is gone, the sickle's slot = the COPPER Harvester (the higher tier) with the sickle's uid: %s" % lp.info)
    kc(str(RH.getProperty("harv")) == "1" and not [k for k in RH.stringPropertyNames() if str(k).startswith("hoe.")] and str(RH.getProperty("harvHoe")) == hoU0
       and str(RH.getProperty("sickle.id")) == "Tool_Sickle_Harvester_Copper" and RH.getProperty("harv.pend") is None,
       "F: the registry: harv=1, no hoe.* key, harvHoe = the hoe's uid, sickle.id = the Harvester, no journal")
    kc(str(RH.getProperty("sickle.rp")) == "0" and RH.getProperty("sickle.inv") is None, "F FIX2 (critic A2): the merge sets sickle.rp=0 / no sickle.inv (an original sickle that turns up is retired, never restored over the Harvester)")
    kc(str(Data.str(hd_, "r", "")) == "rare" and fl[0] in str(hd_.get("mods")) and bool(LL.isLL(hd_)) and str(LL.owner(hd_)) == pk,
       "F: the Harvester: the better rarity (Rare from the hoe), the hoe's line, still your lifelong tool")
    kc(str(RH.getProperty("sickle.up.fort")) == "3" and str(RH.getProperty("sickle.up.wis")) == "2", "F: the points merged: Fortune 3 (hoe) + Wisdom 2 (sickle)")
    kc([x for x in lg if "LL-HARV-BEGIN" in x] and [x for x in lg if "LL-HARV-MADE" in x], "F: gear.log has LL-HARV-BEGIN (both documents) and LL-HARV-MADE")
    txm = render(lp)[0]
    kc("#SkyyGLRow2 " not in txm and "Harvester" in txm and "Your harvester - Upgrade Points" in txm and "Make Harvester" not in txm,
       "F: the Tools tab after the merge: no hoe row, the Harvester's panel (sel moved to it)")
    kc(str(Life.reclaim(PR1, pl, JInt(2))).startswith("-Your hoe is part of your Harvester now"), "F: /hoe says the hoe is in the Harvester")
    HC = P("HarvCmd")
    exm = [m for m in HC.class_.getDeclaredMethods() if str(m.getName()) == "execute"][0]
    exm.setAccessible(True)
    PR1.said = None
    exm.invoke(HC(), JArray(JObject)([None, st, ref, PR1, None]))
    kc(any("You still have your lifelong sickle" in s for s in L["said"](PR1)), "F: /harvester with the Harvester on you: 'You still have ...' (the sickle kind's reclaim): %s" % L["said"](PR1)[-1:])
    tip2, tic2 = HAL(), HAL()
    P("GearTool").lines(U1, JString("Tool_Sickle_Harvester_Copper"), hd_, tip2, tic2)
    t2 = [str(x) for x in tip2]
    kc(any("Tills soil" in x for x in t2) and any("Cuts bushes" in x for x in t2) and any("Lifelong harvester" in x for x in t2) and any("/harvester" in x for x in t2),
       "F: the Harvester's tooltip: tills + cuts + lifelong harvester + /harvester: %s" % t2)
    kc(bool(P("GearSickle").sickle(hv_[0][6])) and all(list(LL.decideC(hv_[0][6], JInt(4), JInt(m))) == list(LL.decideC(stack("Tool_Sickle_Copper"), JInt(4), JInt(m))) for m in range(0, 8)),
       "F: every sickle rule takes the Harvester (GearSickle.sickle, the crop gate = a Copper sickle's on every crop tier)")
    # GearTill: the Harvester's till (durability -1) passes the hoe gate
    Till = P("GearTill")
    hbefore = hv_[0][6]
    hafter = hbefore.withDurability(JDouble(float(hbefore.getDurability()) - 1.0))
    Till.LASTWHY = ""
    rt = int(Till.onChange(PR1, ref, None, None, hbefore, hafter))
    kc(rt == -1 and str(Till.LASTWHY) == "no world / block map", "F: GearTill takes the Harvester's till like the hoe's (it gets to the world step): %s" % Till.LASTWHY)
    Till.LASTWHY = ""
    sk0 = stack("Tool_Sickle_Crude")
    Till.onChange(PR1, ref, None, None, sk0, sk0.withDurability(JDouble(float(sk0.getDurability()) - 1.0)))
    eq(str(Till.LASTWHY), "", "F: a plain sickle never reaches the till")
    # FIX 2 (critic B1): the Harvester's till ring needs air above the target soil - a swing at a crop (a plant above the soil) is no till
    BTm = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType").getAssetMap()
    Till.IDX = None
    Till.TOI = -1
    if not bool(Till.resolve()) or int(BTm.getIndex("Rock_Stone")) < 0:
        K.notes.append("F FIX2: the till air check skipped - this boot has no block types")
    else:
        TIm, PLm, EMm = int(Till.TOI), int(BTm.getIndex("Rock_Stone")), int(Till.EMPTY)
        GRm = {}
        Intg = JClass("java.lang.Integer")
        Boolc = JClass("java.lang.Boolean")

        @JImplements("java.util.function.Function")
        class BlkM(object):
            @JOverride
            def apply(self, o):
                v_ = GRm.get((int(o[0]), int(o[1]), int(o[2])))
                return None if v_ is None else JObject(JInt(v_), Intg)

        @JImplements("java.util.function.Function")
        class SetM(object):
            @JOverride
            def apply(self, o):
                return JObject(JBoolean(True), Boolc)

        @JImplements("java.util.function.Function")
        class TgtM(object):
            @JOverride
            def apply(self, o):
                return V3(JInt(5), JInt(64), JInt(5))

        @JImplements("java.util.function.Function")
        class PermM(object):
            @JOverride
            def apply(self, o):
                return JObject(JBoolean(True), Boolc)
        Till.BLK, Till.SETB, Till.TARGET, Till.PERM = BlkM(), SetM(), TgtM(), PermM()
        WLDm = JClass("com.hypixel.hytale.server.core.universe.world.World")
        wM = us.allocateInstance(WLDm.class_)
        jf(WLDm, "name").set(wM, "skyy-island-p1")
        Till.HIT.clear()
        res_ = []
        for above in (PLm, EMm):
            GRm.clear()
            GRm[(5, 64, 5)] = TIm
            GRm[(5, 65, 5)] = above
            Till.LASTWHY = ""
            n_ = int(Till.onChange(PR1, None, None, wM, hbefore, hafter))
            res_.append((n_, str(Till.LASTWHY)))
        kc(res_[0][0] == -1 and "Harvester swing" in res_[0][1] and res_[1][0] >= 0 and "Harvester swing" not in res_[1][1],
           "F FIX2: a Harvester swing with a plant above the target soil never tills the ring; air above = the till goes on: %s" % res_)
        Till.BLK, Till.SETB, Till.TARGET, Till.PERM = None, None, None, None
        Till.IDX = None
        Till.TOI = -1
    # an old hoe turns up: retired
    csH["storage"].setItemStackForSlot(JShort(30), hoeStack)
    LL.LAST.clear()
    Life.sweep(PR1, invH, True)
    old_ = [x for x in lls(csH, pk) if x[2] == 2]
    kc(old_ and bool(LL.isRt(doc(old_[0][6]))) and LL.reg(pk).getProperty("hoe.uid") is None, "F: the old hoe that turned up is RETIRED (breaks nothing), the hoe kind stays gone")
    hb = csH["hotbar"]
    hb.setItemStackForSlot(JShort(0), old_[0][6])
    csH["storage"].removeItemStackFromSlot(JShort(old_[0][1]))
    rp_ = str(Life.repick(PR1, pl))
    if rp_.startswith("-Hold the tool"):
        K.notes.append("F: /lifelong check skipped - the stand-in inventory has no active hotbar slot (%s)" % rp_)
    else:
        kc("part of your Harvester" in rp_, "F: /lifelong on the old hoe is refused: %s" % rp_)
    hb.removeItemStackFromSlot(JShort(0))
    # FIX (critic 1.4): an OLD sickle stack with the Harvester's uid (a pre-merge copy) is removed - never the Harvester - whatever the scan order
    for slot_sec, slot_no in (("hotbar", 0), ("backpack", 8)):          # scanned before / after the Harvester (GearStamp.SCAN order)
        csH[slot_sec].setItemStackForSlot(JShort(slot_no), sicX[6])
        LL.LAST.clear()
        Life.sweep(PR1, invH, True)
        hv_now = [x for x in lls(csH, pk) if x[2] == 3]
        kc(len(hv_now) == 1 and str(hv_now[0][6].getItemId()).startswith("Tool_Sickle_Harvester_") and hv_now[0][3] == siU0
           and not [i for i in ids(csH) if i.startswith("Tool_Sickle_") and not i.startswith("Tool_Sickle_Harvester_")],
           "F FIX: an old sickle copy with the Harvester's uid in %s %d is removed, the Harvester stays: %s" % (slot_sec, slot_no, [(x[0], x[1], str(x[6].getItemId())) for x in hv_now]))
    # FIX (critic 1.1): a profile whose one-time migration is not finished: no merge; and a merged profile that runs the migration again gets no hoe
    Um = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000199")
    L["PKEY"][str(Um)] = "pmig"
    PRm = L["mkpr"](Um, "Mig")
    skills(u=Um, Mining=4, Foraging=4, Farming=30, Fishing=4)
    invm, csm = mkinv()
    Life.sweep(PRm, invm, True)
    Rm = LL.reg("pmig")
    Rm.remove("migrated")
    LL.save("pmig", Rm)
    LL.REG.clear()
    rm_ = str(Life.harvest(PRm, invm))
    kc(rm_.startswith("-Your starting tools are still arriving") and LL.reg("pmig").getProperty("harv") is None, "F FIX: no merge before migrated=1: %s" % rm_)
    Rm = LL.reg("pmig")
    Rm.setProperty("migrated", "1")
    LL.save("pmig", Rm)
    rm2 = str(Life.harvest(PRm, invm))
    Rm = LL.reg("pmig")
    Rm.remove("migrated")
    LL.save("pmig", Rm)
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PRm, invm, True)
    Rm = LL.reg("pmig")
    kc(rm2.startswith("+") and str(Rm.getProperty("migrated")) == "1" and Rm.getProperty("hoe.uid") is None and not [x for x in lls(csm, "pmig") if x[2] == 2]
       and not [i for i in ids(csm) if i.startswith("Tool_Hoe_")], "F FIX: a merged profile running the one-time migration again gets NO hoe (the hoe kind counts as done): %s" % rm2[:60])
    # the rebirth reset: the Harvester -> the Crude Harvester
    hvX = [x for x in lls(csH, pk) if x[2] == 3][0]
    RH = LL.reg(pk)
    RH.setProperty("sickle.rbTx", "tx-test")
    ok_rb = bool(Life.rbTool(PR1, csH[hvX[0]], JInt(hvX[1]), hvX[6], doc(hvX[6]), JInt(3), pk, RH))
    nowH = csH[hvX[0]].getItemStack(JShort(hvX[1]))
    kc(ok_rb and str(nowH.getItemId()) == "Tool_Sickle_Harvester_Crude" and str(LL.uid(doc(nowH))) == siU0, "F: a rebirth resets the Harvester to the CRUDE Harvester (not a sickle), same uid")
    RH.remove("sickle.rbTx")
    LL.save(pk, RH)
    # the crash paths
    crash_rows = []
    for step, want in ((31, "dropped"), (32, "finished"), (33, "finished")):
        Uc = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000001%02d" % step)
        pkc = "pc%d" % step
        L["PKEY"][str(Uc)] = pkc
        PRc_ = L["mkpr"](Uc, "Crash%d" % step)
        skills(u=Uc, Mining=4, Foraging=4, Farming=30, Fishing=4)
        invc, csc = mkinv()
        Life.sweep(PRc_, invc, True)
        Life.CRASH_AT = JInt(step)
        try:
            Life.harvest(PRc_, invc)
        except Exception:
            pass
        Life.CRASH_AT = JInt(0)
        pend_ = LL.reg(pkc).getProperty("harv.pend")
        LL.REG.clear()
        LL.LAST.clear()
        Life.sweep(PRc_, invc, True)
        Rc = LL.reg(pkc)
        hvs = [x for x in lls(csc, pkc) if x[2] == 3 and str(x[6].getItemId()).startswith("Tool_Sickle_Harvester_")]
        hoes = [x for x in lls(csc, pkc) if x[2] == 2]
        got = "finished" if (str(Rc.getProperty("harv")) == "1" and len(hvs) == 1 and not hoes) else ("dropped" if (Rc.getProperty("harv") is None and len(hoes) == 1 and not hvs) else "?")
        crash_rows.append((step, pend_ is not None, got, Rc.getProperty("harv.pend")))
        kc(pend_ is not None and got == want and Rc.getProperty("harv.pend") is None,
           "F: a crash at step %d (journal on disk): the next look %s the merge (one tool, no journal): %s" % (step, want, crash_rows[-1]))
    # the points trim: more points spent than earned (Farming 4 = 3 points; hoe Fortune 3 + sickle Wisdom 2 = 7)
    Ut = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000177")
    L["PKEY"][str(Ut)] = "ptrim"
    PRt = L["mkpr"](Ut, "Trim")
    skills(u=Ut, Mining=4, Foraging=4, Farming=4, Fishing=4)
    invt, cst = mkinv()
    Life.sweep(PRt, invt, True)
    Rt = LL.reg("ptrim")
    Rt.setProperty("hoe.up.fort", "3")
    Rt.setProperty("sickle.up.wis", "2")
    LL.save("ptrim", Rt)
    rt_ = str(Life.harvest(PRt, invt))
    Rt = LL.reg("ptrim")
    kc(rt_.startswith("+") and int(LL.spent(Rt, JInt(3))) <= int(LL.earned(Ut, JInt(3))) and any("lost a level" in s for s in L["said"](PRt)),
       "F: the merged points are trimmed to the points you have (spent %d of %d) and you are told: %s" % (int(LL.spent(Rt, JInt(3))), int(LL.earned(Ut, JInt(3))), rt_[:80]))
    kc(str(Life.harvest(PRt, invt)) == "-You already have your Harvester.", "F: a second merge is refused")
    apply(part__harvester="false")
    Uo = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000188")
    L["PKEY"][str(Uo)] = "poff"
    PRo = L["mkpr"](Uo, "Off")
    skills(u=Uo, Mining=4, Foraging=4, Farming=4, Fishing=4)
    invo, cso = mkinv()
    Life.sweep(PRo, invo, True)
    kc(str(Life.harvest(PRo, invo)) == "-The Harvester is switched off on this server.", "F: part.harvester off = no merge")
    apply()
    nfn = P("GearLLFn")(JInt(0))
    eq(int(nfn.apply(U1)), 4, "F: gear:fn:lifelong (bare UUID, SkyyQuests' tutorial) still counts four kinds after the merge")

    # FIX (Skyy 2026-10-16): the CRAFT tab is the SMITHING tab; the Upgrade tab shows 8 rows a page (70 px rows, 58 px icons)
    FPM.cur = lp
    txs = render(lp)[0]
    tab3 = [l for l in txs.split(chr(10)) if "TextButton #SkyyGTab3 " in l]
    kc(tab3 and 'Text: "Smithing"' in tab3[0] and 'Text: "Craft"' not in tab3[0], "F FIX: the tab row's first tab reads 'Smithing' (was Craft): %s" % [re.findall(r'Text: "[^"]*"', l)[:1] for l in tab3])
    for j_, a_ in enumerate(("Armor_Copper_Head", "Armor_Copper_Chest", "Armor_Copper_Legs", "Armor_Copper_Hands", "Armor_Iron_Head", "Armor_Iron_Chest")):
        csH["storage"].setItemStackForSlot(JShort(20 + j_), stack(a_))
    upF = P("UpgPage")(PR1)
    FPM.cur = upF
    txu = render(upF)[0]
    nrow = int(upF.rows.size())
    rows_on = re.findall(r"Group #SkyyGURow\d+ \{ Anchor: \(Height: (\d+)\)", txu)
    kc(nrow >= 9 and len(rows_on) == 8 and set(rows_on) == {"70"} and "Width: 58, Height: 58" in txu and "Width: 786" in txu and "Height: 96" not in txu,
       "F FIX: the Upgrade tab: 8 rows on page 1 of %d rows, each 70 px with a 58 px icon (was 6 of 96 px): %s" % (nrow, rows_on))
    upF.pageNo = JInt(1)
    rows_p2 = re.findall(r"Group #SkyyGURow(\d+) ", render(upF)[0])
    kc(rows_p2 and int(rows_p2[0]) == 8 and len(rows_p2) == min(8, nrow - 8), "F FIX: page 2 starts at row 8: %s" % rows_p2)
    for j_ in range(6):
        csH["storage"].setItemStackForSlot(JShort(20 + j_), None)
    FPM.cur = lp

    # ============================================================== G: the can tiers up (the Upgrade tab's / Anvil's GearUp.upgrade)
    L["wipe_home"]()
    skills(Mining=4, Foraging=4, Farming=12, Fishing=4)
    invG, csG = mkinv()
    Life.sweep(PR1, invG, True)
    cg = [x for x in lls(csG, pk) if x[2] == 5][0]
    up0 = Up.check(cg[6], U1)
    kc(up0[0] is None and str(up0[1]) == "Tool_WaterCan_Copper" and "Copper" in str(Up.shortOfU(invG, U1, up0[2])), "G: tier up without ingots: short of 25 Copper Ingots (%s)" % Up.shortOfU(invG, U1, up0[2]))
    csG["storage"].setItemStackForSlot(JShort(20), stack("Ingredient_Bar_Copper", 30))
    SCANS = [int(x) for x in Stamp.SCAN]
    names = ["hotbar", "armor", "tools", "utility", "storage", "backpack"]
    s_num = SCANS[names.index(cg[0])]
    r_up = Up.upgrade(invG, JInt(s_num), JInt(cg[1]), JString(str(cg[6].getItemId())), P("GearForge").fp(cg[6]), U1, JString("Tester"))
    cg2 = [x for x in lls(csG, pk) if x[2] == 5]
    kc(int(r_up[0]) == 1 and len(cg2) == 1 and str(cg2[0][6].getItemId()) == "Tool_WaterCan_Copper" and cg2[0][3] == cg[3] and ids(csG).get("Ingredient_Bar_Copper") == 5,
       "G: GearUp.upgrade: the can is a Copper Watering Can (same uid, 25 ingots used): %s" % (str(r_up[1]) if r_up is not None else None))
    pc = [float(x) for x in Can.plan(U1, JString("Tool_WaterCan_Copper"), doc(cg2[0][6]), JDouble(100.0))]
    kc(pc[0] == 3 and abs(pc[2] - 100.0 / 30.0) < 1e-9, "G: ... it waters 3x3 now and holds 30 waterings")
    LL.LAST.clear()
    Life.sweep(PR1, invG, True)
    eq(str(LL.reg(pk).getProperty("can.id")), "Tool_WaterCan_Copper", "G: the next look writes the registry (can.id)")
    UP_ = P("UpgPage")
    kc(str(UP_.tierTag("Tool_WaterCan_Copper")) == "T2 Copper" and str(UP_.tierTag("Tool_Sickle_Harvester_Thorium")) == "T4 Thorium", "G: the Upgrade tab's tier tags for the can / Harvester")

    # ============================================================== H: the fold-ins
    CALLS = []

    @JImplements("java.util.function.Function")
    class HpFn(object):
        @JOverride
        def apply(self, o):
            CALLS.append([str(o[0])] + [str(x) for x in list(o)[1:]])
            return JBoolean(True)
    FX = P("GearFx")
    tt = JArray(JInt)(int(Defs.NS))
    tt[int(Defs.I_HPR)] = 4
    tt[int(Defs.I_HPRP)] = 25
    kc(not bool(FX.hpPost(U1, tt, JLong(2000))) and not bool(FX.hpPosted(U1)), "H: without skill:fn:hpregen nothing is posted (Gear heals hpr itself as before)")
    br.put("skill:fn:hpregen", HpFn())
    ok1 = bool(FX.hpPost(U1, tt, JLong(2000)))
    n1 = len(CALLS)
    FX.hpPost(U1, tt, JLong(2000))
    kc(ok1 and bool(FX.hpPosted(U1)) and n1 == 2 and CALLS[0][0] == "add" and CALLS[0][2] == "SkyyGear" and abs(float(CALLS[0][3]) - 2.0) < 1e-9
       and CALLS[1][0] == "addpct" and abs(float(CALLS[1][3]) - 25.0) < 1e-9 and len(CALLS) == 2,
       "H: Raw Health Regen 4 per 2 s = add 2 HP/s, Health Regen %% 25 = addpct 25 (source SkyyGear); the same values again = no second post: %s" % CALLS)
    FX.hpDrop(U1)
    kc(CALLS[-1][0] == "remove" and not bool(FX.hpPosted(U1)), "H: a logout / part.stats off drops the source")
    FX.hpClear()
    kc(CALLS[-1][0] == "clear", "H: shutdown clears the source")
    # FIX (critic 2.2): a SkyySkills reload = a new skill:fn:hpregen object -> Gear posts again at once (no 10 s gap)
    FX.hpPost(U1, tt, JLong(2000))
    nA = len(CALLS)
    br.put("skill:fn:hpregen", HpFn())
    FX.hpPost(U1, tt, JLong(2000))
    kc(len(CALLS) == nA + 2 and CALLS[-2][0] == "add" and CALLS[-1][0] == "addpct", "H FIX: a reloaded SkyySkills (new hpregen object) gets the source again at once: %s" % CALLS[nA:])
    # FIX (critic 2.1): SkyySkills' hp.regen.enabled false (config:fn:SkyySkills get) = not 'posted' - Gear heals Raw Health Regen itself
    CFGV = {"hp.regen.enabled": "false"}

    @JImplements("java.util.function.Function")
    class SkCfg(object):
        @JOverride
        def apply(self, o):
            return JString(CFGV.get(str(o[1]), "")) if str(o[0]) == "get" else None
    br.put("config:fn:SkyySkills", SkCfg())
    FX.SKAT = JLong(0)
    kc(not bool(FX.hpPosted(U1)), "H FIX: SkyySkills' Health regen switched off = Gear heals its own regen (hpPosted false)")
    CFGV["hp.regen.enabled"] = "true"
    FX.SKAT = JLong(0)
    kc(bool(FX.hpPosted(U1)), "H FIX: ... on = SkyySkills heals it (hpPosted true, never twice)")
    br.remove("config:fn:SkyySkills")
    FX.SKAT = JLong(0)
    FX.hpClear()
    br.remove("skill:fn:hpregen")
    GV = P("GearView")
    kc(GV.rushText("Weapon_Longsword_Crude") is None, "H: without SkyyArmory's armory:blade the longsword keeps its Charged Attack line")
    br.put("armory:blade", JString("Spellblade swords: Crescent Rush on (hold the longsword attack: dash 6 + 0.3 a Momentum stack, sweep 1.5 H in 180 deg reach 3, passed enemies 0.5 H, crescent 1 H 8 blocks at 10+ Momentum (Imbue adds its element); 8 Mana + 4 Stamina, no cooldown); Spellblade sword hits x113 percent (Crescent Rush hits too); right-click guard on"))
    rt2 = GV.rushText("Weapon_Longsword_Crude")
    kc(rt2 is not None and "8 Mana + 4 Stamina" in str(rt2) and GV.rushText("Weapon_Sword_Crude") is None, "H: with it: 'Spellblade: hold the attack ... (8 Mana + 4 Stamina).': %s" % rt2)
    br.put("armory:blade", JString("Spellblade swords: Crescent Rush OFF (hold ...)"))
    kc(GV.rushText("Weapon_Longsword_Crude") is None, "H: blade.rush.enabled off = the old line")
    br.remove("armory:blade")
    kc(str(Defs.classSkill("Spellblade")) == "Battlemagic" and str(Defs.classSkill("Monk")) == "Zen" and str(Defs.classSkill("Warrior")) == "Swordsmanship",
       "H: Gear's class -> class skill copy: Spellblade = Battlemagic, Monk = Zen")
    probs = []
    for cl_, ev_ in rendered:
        probs += validate(cl_, ev_)
    kc(not probs, "every Tools page rendered (%d) validates: %s" % (len(rendered), probs[:4]))
    K.notes.append("H312 logs: %s" % [x[:160] for x in logs() if "WARN" in x][:6])


# ====================================================================================================== LIVE: start twice on a live copy
LIVE_GEAR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")          # the deploy world (read only - copied)


def run_live312(out):
    from jpype import JClass
    K = H["Child"](out)
    H["_jvm"]([B.SERVER_JAR, JAR], verify=True)
    home = os.path.join(SCRATCH, "live312", "Skyy_SkyyGear")
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
        K.check(after == before, "LIVE start %d: the live config.properties copy is byte-identical (the 0.3.12 rows need no one-time update)" % step)
        K.check(bool(Cfg.CAN_ON) and bool(Cfg.CAN_KIT) and str(Cfg.CAN_AREA) == "1,3,5,7,9,11" and str(Cfg.CAN_USES) == "20,30,40,60,80,100" and int(Cfg.CAN_SEC) == 86400
                and bool(Cfg.HARV_ON) and not bool(Cfg.HARV_RBGATE) and str(Cfg.CAN_LADDERS).startswith("Tool_WaterCan_Crude>") and "Tool_WaterCan_Crude>" in str(LL.ladders())
                and str(Cfg.LL_LADDERS) in str(LL.ladders()), "LIVE start %d: the new rows read their defaults; the live lifelong.ladders is kept and the can / Harvester ladders join it" % step)
    txt = before.decode("utf-8", "replace")
    K.check("can." not in txt and "harvester." not in txt and "canKit" not in txt, "LIVE the live file has none of the new keys (defaults apply)")
    have = []
    for f_ in sorted(os.listdir(os.path.join(home, "lifelong"))):
        P_ = LL.reg(f_[:-len(".properties")])
        have.append((f_[:12], P_.getProperty("can.uid") is not None, str(P_.getProperty("migrated")), P_.getProperty("harv") is not None))
    K.check(all(open(os.path.join(home, "lifelong", f_), "rb").read() == b_ for f_, b_ in regs0.items()), "LIVE the registries were read, not rewritten")
    K.check(not any(h[1] or h[3] for h in have), "LIVE no live profile has a can or a Harvester yet (each gets its can at its next join): %s" % have)
    K.notes.append("LIVE profiles (file, has a can, migrated, merged): %s" % have)
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
        print("  note (%s): %s" % (label, str(n)[:500]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H310["run_mkfake10"](arg("--mkfake"))), ("--h312", lambda: run_h312(arg("--out"))),
                     ("--live312", lambda: run_live312(arg("--out"))), ("--h311", lambda: H311["run_h311"](arg("--out"))),
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
    # a child flag this file does not know must never fall through into the full run (it would spawn itself again and again)
    _known = {"--only", "--keep", "--dir", "--jar", "--root", "--out"}
    _unk = [a for a in sys.argv[1:] if a.startswith("--") and a not in _known]
    if _unk:
        print("unknown child flag(s) %s - nothing run" % _unk)
        sys.exit(2)
    for f_ in (JAR, J311, FI7_SRC, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
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
    env_311 = dict(env)
    env_311["JAVA_TOOL_OPTIONS"] = env["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noCanKit=true"
    env_old = dict(env_311)
    env_old["JAVA_TOOL_OPTIONS"] = env_311["JAVA_TOOL_OPTIONS"] + " -Dskyy.harness.noPoleKit=true"
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets312()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
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
        if want("h311"):
            out = os.path.join(SCRATCH, "h311.json")
            pr = child(env_311, "--h311", "--out", out)
            check(pr.returncode == 0, "h311: the child exited cleanly (%s)" % pr.returncode)
            take(out, "h311")
        if want("h312"):
            out = os.path.join(SCRATCH, "h312.json")
            pr = child(env, "--h312", "--out", out)
            check(pr.returncode == 0, "h312: the child exited cleanly (%s)" % pr.returncode)
            take(out, "h312")
        if want("live"):
            out = os.path.join(SCRATCH, "live312.json")
            pr = child(env, "--live312", "--out", out)
            check(pr.returncode == 0, "live312: the child exited cleanly (%s)" % pr.returncode)
            take(out, "live312")
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
