"""Harness for SkyyGear 0.3.23 (tools/gear_0_3_23_patch.py header = THE METAL TOOLS, round G2 + the A1 extra scope) = the 0.3.22 harness (and
through it the whole older chain) run on the 0.3.23 jar + S323 (the jar compare 0.3.22 -> 0.3.23, replacing S322) + H323 (inside the h319 child,
after H319 .. H322, on the same booted engine), plus a --static phase that needs no jar:
    python tools/gear_0_3_23_patch.py && python SkyyGear/build_skyygear_0.3.23.py
    python SkyyGear/test_skyygear_0.3.23.py [--keep] [--only assets,h319,...]
    python SkyyGear/test_skyygear_0.3.23.py --static [--keep]          (no jars, no Assets.zip, no server jar)

  STATIC (--static)
       G  THE PATCH: tools/gear_0_3_23_patch.py run TWICE into a scratch tree (a copy of the patch + build_skyygear_0.3.22.py + deploy_set.py)
          -> byte-identical outputs, = SkyyGear/build_skyygear_0.3.23.py, compiles, keeps the source's line endings
       A  THE ANCHORS: VERSION; no new system / command / class; the items + ladders + gate blocks in order; migrate0323 after migrate0322;
          lrank / tnm before tierFor; fromRecipeAlt before cost0; MULTI_OWN in multiId
  S323 the jar 0.3.22 -> 0.3.23: adds only the 49 item JSONs + their art / models / the multitool interaction + animation set, removes nothing,
       changes only manifest.json + server.lang (0.3.22's lines kept, + the 98 name / tagged description lines); changed classes = S323_MUST (+ MAY)
  H323 (the h319 child, ONE booted engine) - real code:
       A  internal tiers (GearLL.tier / GearTool.tier of the zone words = the next vanilla tool's), lrank strictly up along both 16-step ladders,
          tnm (the metal word for the new metals, the internal tier's name for the rest)
       B  kinds: kOf / toolFam / multiId of the new ids (pickaxe 0, hatchet 1, Harvester 3, can 5, multitool fam 6 and no lifelong kind)
       C  the ladders: KLAD / HARV_LAD / HARV_TOP 7, GearUp.next along the pickaxe / hatchet / Harvester / can / Soul Cage ladders, written costs
          (Dusk 64 alloy bars; hatchet Iron = Enchanted Iron + Maple), GearUp.earlier on the cage ladder
       D  level bands of the new ids (Lead_SkyWynn 22-30 ..., Bronze 15-23); UpgPage.tierTag "T5 Lead"
       E  the ore gate: nextPick by the ladder / by the vanilla steps (gate.nextByLadder), decideI of the new pickaxes (the zone's alloy pickaxe
          opens the next zone: base ore normal, new ore half), gate.oreFloor empty by default
       F  h23Update on a 0.3.22-shaped file (5 rows rewritten, marker at the END, CRLF kept, run once; a hand-edited row kept + noted)
       G  the A1 scope: GearBase.kunaiTwin / monkMetal key the twin by the full <M>_SkyWynn word; GearPool knows the new Armory ids
  NOT COVERED (smoke test / Skyy in game): the art in game, a real tier-up payment, fromRecipeAlt against the live SkyyArmory recipes (the build
  proves each cage step's recipe from the 0.1.33 jar), the migration on the real config.properties, real hits on the zone ores.
Older checks this round changes on purpose are WAIVED with the reason (WAIVE_323).
Scratch: tools/dev/scratch/g2/h323/gear/harness (full run) and .../h323/static (--static), deleted at the end unless --keep.
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


VERSION = "0.3.23"
V322 = "0.3.22"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g2", "h323")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J322 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V322))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_23_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.23.py")
GEN322 = os.path.join(HERE, "build_skyygear_0.3.22.py")
METALS = ["Bronze", "Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]
ORDER = ["Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril",
         "Titanium", "Lumen"]
VAN = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
NEXT = {"Bronze": "Thorium", "Lead": "Cobalt", "Dusk": "Cobalt", "Chromium": "Adamantite", "Azurvane": "Adamantite", "Slag": "Mithril",
        "Cinder": "Mithril", "Titanium": "Onyxium", "Lumen": "Onyxium"}
INTERNAL = {"Crude": 0, "Copper": 1, "Iron": 2, "Thorium": 3, "Cobalt": 4, "Adamantite": 5, "Mithril": 6, "Onyxium": 7}
BANDS22 = {"Lead": (22, 30), "Dusk": (24, 32), "Chromium": (28, 40), "Azurvane": (31, 41), "Slag": (37, 45), "Cinder": (39, 47),
           "Titanium": (45, 55), "Lumen": (50, 60), "Bronze": (15, 23)}
PICK = ["Tool_Pickaxe_%s_SkyWynn" % m for m in METALS]
HATCH = ["Tool_Hatchet_%s_SkyWynn" % m for m in METALS]
MULTI = ["Tool_Hatchet_Pickaxe_Multitool_%s_SkyWynn" % m for m in METALS]
HARV = ["Tool_Sickle_Harvester_" + m for m in ("Cobalt", "Adamantite", "Mithril")] + ["Tool_Sickle_Harvester_%s_SkyWynn" % m for m in METALS]
CAN = ["Tool_WaterCan_Mithril"] + ["Tool_WaterCan_%s_SkyWynn" % m for m in METALS]
NEW_IDS = PICK + HATCH + MULTI + HARV + CAN


def lid(kind, m):
    pre = {"pick": "Tool_Pickaxe_", "hatch": "Tool_Hatchet_", "harv": "Tool_Sickle_Harvester_", "can": "Tool_WaterCan_",
           "cage": "Weapon_Wand_SoulCage_"}[kind]
    return pre + (m if (m in VAN or m == "Crude") else m + "_SkyWynn")


S323_MUST = {"GearLL": "zone tier words, lrank / tnm, nextPick + PICK_T / PICK_TV, KLAD / HARV_LAD / HARV_TOP", "GearCfg": "migrate0323 + gate.nextByLadder + defaults",
             "GearTool": "TIER_W / TIER_N + the zone words", "GearDefs": "MULTI_OWN", "GearData": "multiId knows MULTI_OWN",
             "GearUp": "earlier / fromRecipeAlt in cost0", "GearLife": "tnm in the texts + lrpL", "GearReq": "tnm in the collection token"}
S323_MAY = {"SkyyGearPlugin": "the version text + the migrate0323 call", "Gear": "the setup call", "CfgFn": "config kit: the version",
            "CfgRows": "config kit: the version", "CfgFile": "config kit", "CfgDefaults": "config kit", "CfgKit": "config kit", "CfgPub": "config kit",
            "GearCfgRows": "the row table", "LifePage": "tnm in its texts", "GearPool": "the 60 new Armory pool ids", "GearUt": "the CRAFTED list",
            "GearChg": "the 12 own crossbows", "GearCharged": "the 12 own crossbows", "GearSmith": "ladder texts", "UpgPage": "texts", "GearMerge": "texts",
            "GearView": "texts", "GearHarv": "HARV_TOP", "GearGate": "texts"}


# ---- the 0.3.22 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder (and THIS file)
if not STATIC:
    _H322 = os.path.join(HERE, "test_skyygear_0.3.22.py")
    _T322 = open(_H322, encoding="utf-8").read()
    _cut = _T322.rindex('if __name__ == "__main__":')
    _argv = sys.argv
    _only = arg("--only")
    if _only:          # h323 runs inside the h319 child (like h320 .. h322)
        _only = ",".join(sorted(set(("h319" if x in ("h321", "h322", "h323") else x) for x in _only.split(","))))
    sys.argv = [_H322, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
        (["--only", _only] if _only else []) + [a for a in _argv[1:] if a in ("--h319",)] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H322 = {"__name__": "skyygear_h322", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T322[:_cut], _H322 + " (library)", "exec"), H322)
    sys.argv = _argv
    if _only:
        sys.argv[sys.argv.index("--only") + 1] = _only
    H322["VERSION"] = VERSION
    H321 = H322["H321"]
    H321["VERSION"] = VERSION
    H320 = H322["H320"]
    H320["VERSION"] = VERSION
    H319 = H322["H319"]
    H319["VERSION"] = VERSION
    H316 = H322["H316"]
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


# ====================================================================================================== S323
def run_assets323():
    ea, eb = entries(J322), entries(JAR)
    added, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    items = sorted(os.path.basename(n)[:-5] for n in added if n.startswith("Server/Item/Items/"))
    art = [n for n in added if not n.startswith("Server/Item/Items/")]
    ok_art = all(n.startswith(("Common/Items/Tools/SkyyMetal/", "Common/Icons/ItemsGenerated/SkyyMetal_", "Common/Items/SkyyGear/Harvester/Harvester_",
                                "Common/Icons/ItemsGenerated/Tool_Sickle_Harvester_")) or n in (
        "Server/Item/Interactions/SkyyGear/Multitool/SkyyGear_Multitool_Attack.json", "Server/Item/RootInteractions/SkyyGear/SkyyGear_Multitool_Attack.json",
        "Server/Item/Animations/SkyyGear/SkyyGear_Multitool.json") for n in art)
    check(items == sorted(NEW_IDS) and ok_art and not gone and changed == ["Server/Languages/en-US/server.lang", "manifest.json"],
          "S323: 0.3.22 -> 0.3.23 adds exactly the 49 metal tools + their art / models / multitool swing, removes nothing, changes only manifest + "
          "server.lang: items %d (%s) art ok %s gone %s changed %s" % (len(items), sorted(set(items) ^ set(NEW_IDS))[:4], ok_art, gone[:4], changed))
    nm = [n for n in art if n.endswith(".blockymodel")]
    check(not nm, "S323: no model is shipped (every new item uses a vanilla model by path - Quirk's private models wait for Skyy): %s" % nm)
    tex = [n for n in art if n.endswith(".png") and "/Icons/" not in n]
    ico = [n for n in art if "/Icons/" in n]
    check(len(tex) == 40 and len(ico) == 40, "S323: one texture + one icon per new item, the multitools reuse their pickaxe's: %d / %d" % (len(tex), len(ico)))
    for n in sorted(added):
        if n.startswith("Server/Item/Items/"):
            d = json.loads(eb[n].decode("utf-8"))
            check("Recipe" not in d and d.get("TranslationProperties", {}).get("Name") == "server.items.%s.name" % os.path.basename(n)[:-5]
                  and (d.get("Texture") is None or ("Common/" + d["Texture"]) in eb) and ("Common/" + d["Icon"]) in eb
                  and d["Model"].startswith(("Items/Tools/Pickaxe/", "Items/Tools/Hatchet/", "Items/Tools/Hoe/", "Items/Tools/Watering_Can/")),
                  "S323: %s has no recipe, its own name key and its texture / icon / model in the jar" % os.path.basename(n))
    la = ea["Server/Languages/en-US/server.lang"].decode("utf-8").splitlines()
    lb = eb["Server/Languages/en-US/server.lang"].decode("utf-8").splitlines()
    import tier_tags as TT
    new = [x for x in lb if x not in la]
    tags_ok = all(any(x == "items.%s.description = %s - %s" % (i, TT.tag_for(i), x.split(" - ", 1)[1]) for i in NEW_IDS if x.startswith("items.%s.description" % i))
                  for x in new if ".description = " in x)
    check([x for x in lb if x in set(la)] == la and len(lb) == len(la) + 98 and len(new) == 98 and tags_ok, "S323: server.lang = 0.3.22's lines + 98 new (49 names, 49 descriptions tagged by tools/tier_tags.py): %d new" % len(new))
    check('"0.3.23"' in eb.get("manifest.json", b"").decode("utf-8", "replace"), "S323: the manifest says 0.3.23")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.22 -> 0.3.23: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S323_MUST) | set(S323_MAY), "S323: only the patched classes changed: unexpected %s" % sorted(set(chg) - set(S323_MUST) - set(S323_MAY)))
    check(set(S323_MUST) <= set(chg), "S323: every class the patch edits really changed: unchanged %s" % sorted(set(S323_MUST) - set(chg)))


# ====================================================================================================== H323 (in the h319 child)
def _h323(L, K):
    from jpype import JClass, JInt, JString
    import tier_tags as TT
    P = lambda n: JClass(PKG + n)
    LL, Cfg, Lvl, Data, Defs, apply, FRESH = L["LL"], L["Cfg"], L["Lvl"], L["Data"], L["Defs"], L["apply"], L["FRESH"]
    Tool, Up, Upg, Base, Gear = P("GearTool"), P("GearUp"), P("UpgPage"), P("GearBase"), P("Gear")

    def kc(cond, what):
        K.check(bool(cond), "H323 " + what)
    apply()
    # ============================================================== A
    tz = dict((m, (int(LL.tier(lid("pick", m))), int(Tool.tier(lid("pick", m))))) for m in METALS)
    kc(all(tz[m] == (INTERNAL[NEXT[m]],) * 2 for m in METALS), "A: the internal tier of every new metal = its next vanilla tool's: %s" % tz)
    for kind in ("pick", "hatch", "harv", "can"):
        ids = [lid(kind, "Crude")] + [lid(kind, m) for m in ORDER]
        rk = [int(LL.lrank(i)) for i in ids]
        it = [int(LL.tier(i)) for i in ids]
        kc(rk == sorted(rk) and len(set(rk)) == len(rk) and it == sorted(it), "A: lrank strictly up / internal tier never down along the %s ladder: %s" % (kind, rk))
    tn = [str(LL.tnm(i)) for i in ("Tool_Pickaxe_Lead_SkyWynn", "Tool_Hatchet_Bronze_SkyWynn", "Tool_WaterCan_Mithril", "Tool_Pickaxe_Cobalt", "Tool_Pickaxe_Crude",
                                   "Tool_Sickle_Harvester_Lumen_SkyWynn")]
    kc(tn == ["Lead", "Bronze", "Mithril", "Cobalt", "Crude", "Lumen"], "A: tnm = the metal word for the new metals, else the internal tier's name: %s" % tn)
    # ============================================================== B
    kd = [(int(LL.kOf(i)), int(Data.toolFam(i)), bool(Data.multiId(i))) for i in ("Tool_Pickaxe_Dusk_SkyWynn", "Tool_Hatchet_Slag_SkyWynn",
                                                                                  "Tool_Sickle_Harvester_Cobalt", "Tool_WaterCan_Lumen_SkyWynn",
                                                                                  "Tool_Hatchet_Pickaxe_Multitool_Lead_SkyWynn")]
    kc(kd == [(0, 1, False), (1, 3, False), (3, 5, False), (int(LL.CAN), 0, False), (-1, 6, True)] and bool(LL.harv("Tool_Sickle_Harvester_Lead_SkyWynn"))
       and not bool(Data.multiId("Tool_Hatchet_Pickaxe_Multitool_Firetine")), "B: kinds / families / multitool ids of the new tools: %s" % kd)
    # ============================================================== C
    klad = [str(x) for x in LL.KLAD]
    kc(klad[0].split(",") == [lid("pick", "Crude")] + [lid("pick", m) for m in ORDER] and klad[1].split(",") == [lid("hatch", "Crude")] + [lid("hatch", m) for m in ORDER]
       and klad[int(LL.CAN)].split(",") == [lid("can", "Crude")] + [lid("can", m) for m in ORDER]
       and str(LL.HARV_LAD).split(",") == [lid("harv", "Crude")] + [lid("harv", m) for m in ORDER] and int(LL.HARV_TOP) == 3,
       "C: KLAD pickaxe / hatchet / can + HARV_LAD = Crude .. Lumen (16 each), HARV_TOP stays 3 (critic M3)")
    bad = []
    for kind in ("pick", "hatch", "harv", "can"):
        ids = [lid(kind, "Crude")] + [lid(kind, m) for m in ORDER]
        for a, b in zip(ids, ids[1:]):
            if str(Up.next(a)) != b:
                bad.append((a, str(Up.next(a))))
    cage = ["Weapon_Wand_SoulOrb"] + [lid("cage", m) for m in ORDER if m != "Bronze"] + ["Weapon_Wand_SoulCage_Onyxium"]
    for a, b in zip(cage, cage[1:]):
        if str(Up.next(a)) != b:
            bad.append((a, str(Up.next(a))))
    kc(not bad, "C: GearUp.next walks the 15-step pickaxe / hatchet / Harvester / can and Soul Cage ladders: %s" % bad[:4])

    def wc(a, b):
        w = Up.written(a, b)
        return None if w is None else dict(zip([str(x) for x in w[0]], [int(x) for x in w[1]]))
    wd = (wc("Tool_Pickaxe_Lead_SkyWynn", "Tool_Pickaxe_Dusk_SkyWynn"), wc("Tool_Hatchet_Copper", "Tool_Hatchet_Iron"),
          wc("Tool_Pickaxe_Thorium", "Tool_Pickaxe_Cobalt"), wc("Tool_Pickaxe_Dusk_SkyWynn", "Tool_Pickaxe_Cobalt"),
          wc("Tool_Sickle_Harvester_Cinder_SkyWynn", "Tool_Sickle_Harvester_Mithril"), wc("Tool_WaterCan_Titanium_SkyWynn", "Tool_WaterCan_Lumen_SkyWynn"))
    kc(wd == ({"Ingredient_Bar_Dusk_SkyWynn": 64}, {"Skyy_Ench_Iron": 1, "Skyy_Ench_Maple": 1}, None, {"Skyy_Ench_Cobalt": 2},
              {"Skyy_Ench_Mithril": 3, "Skyy_Ench_Cotton": 3}, {"Ingredient_Bar_Lumen_SkyWynn": 256, "Skyy_Ench_Potato": 3}),
       "C: written tier-up costs (alloy bars; hatchet = bars + log; Harvester / can = bars + crop; Thorium -> Cobalt is no step now): %s" % (wd,))
    kc(bool(Up.earlier("Weapon_Wand_SoulCage_Thorium", "Weapon_Wand_SoulCage_Dusk_SkyWynn")) and not bool(Up.earlier("Weapon_Wand_SoulCage_Dusk_SkyWynn", "Weapon_Wand_SoulCage_Thorium"))
       and not bool(Up.earlier("Weapon_Wand_SoulCage_Thorium", "Weapon_Wand_SoulCage_Thorium")) and bool(Up.earlier("Weapon_Wand_SoulOrb", "Weapon_Wand_SoulCage_Lumen_SkyWynn")),
       "C: GearUp.earlier walks the live cage ladder back (Thorium below Dusk, never itself / above)")
    # ============================================================== D
    bd = dict((m, [int(x) for x in Lvl.band(lid("pick", m))][:2]) for m in METALS)
    bh = [[int(x) for x in Lvl.band(i)][:2] for i in ("Tool_WaterCan_Lead_SkyWynn", "Tool_Hatchet_Pickaxe_Multitool_Lumen_SkyWynn", "Tool_Sickle_Harvester_Cobalt")]
    kc(all(bd[m] == list(BANDS22[m]) for m in METALS) and bh[:2] == [[22, 30], [50, 60]] and bh[2] == [int(x) for x in Lvl.band("Tool_Pickaxe_Cobalt")][:2],
       "D: the new tools' level bands (level.material.<M>_SkyWynn, Bronze 15-23): %s %s" % (bd, bh))
    tg = [str(Upg.tierTag(i)) for i in ("Tool_Pickaxe_Lead_SkyWynn", "Tool_WaterCan_Mithril", "Tool_Hatchet_Pickaxe_Multitool_Bronze_SkyWynn")]
    kc(tg == ["T5 Lead", "T13 Mithril", "T3 Bronze"], "D: UpgPage.tierTag of the new tools: %s" % tg)
    # the harness engine fails to DECODE the vanilla pickaxe / hatchet chain (Tool_Pickaxe_Crude / Tool_Hatchet_Crude "Failed to decode" - a
    # stand-in limit, so their children Tool_Pickaxe_Thorium ... and ours find no parent here); the Harvesters (Parent Tool_Sickle_Iron) and
    # the cans (no Parent) must load; the 27 pickaxes / hatchets / multitools are proved by the smoke test on the real server
    got = [i for i in NEW_IDS if Gear.item(i) is not None]
    kc(all(Gear.item(i) is not None for i in HARV + CAN), "D: the 12 Harvesters + 10 cans are loaded assets: missing %s" % [i for i in HARV + CAN if Gear.item(i) is None][:4])
    K.notes.append("H323 D: %d of 49 new items loaded in the harness engine (the pickaxe / hatchet / multitool Parent chain does not decode here - smoke test)" % len(got))
    # ============================================================== E
    np_on = [int(LL.nextPick(JInt(t))) for t in (1, 2, 3, 4, 13, 15, 16)]
    apply(gate__nextByLadder="false")
    np_off = [int(LL.nextPick(JInt(t))) for t in (1, 2, 3, 4, 13, 15, 16)]
    apply()
    kc(np_on == [2, 3, 4, 5, 14, 16, 999] and np_off == [2, 4, 4, 7, 16, 16, 999] and [int(x) for x in LL.PICK_T] == list(range(1, 17))
       and [int(x) for x in LL.PICK_TV] == [1, 2, 4, 7, 10, 13, 16], "E: nextPick by the ladder (gate.nextByLadder on) / by the vanilla steps (off): %s / %s" % (np_on, np_off))
    dz = []
    for alloy, base, new in (("Dusk", 600, 706), ("Azurvane", 900, 1009), ("Cinder", 1200, 1312)):
        a = [int(x) for x in LL.decideI(lid("pick", alloy), JInt(1), JInt(base))]
        b = [int(x) for x in LL.decideI(lid("pick", alloy), JInt(1), JInt(new))]
        dz.append((alloy, a[0], b[0], b[8]))
    kc([(x[1], x[2], x[3]) for x in dz] == [(0, 1, 4)] * 3, "E: the zone's alloy pickaxe opens the next zone - its base ore normal, its new ore at half: %s" % dz)
    dm = [int(x) for x in LL.decideI("Tool_Hatchet_Pickaxe_Multitool_Lead_SkyWynn", JInt(1), JInt(403))]
    kc(dm[0] == 0 and dm[3] == 5, "E: the Lead multitool mines Lead ore at its ladder tier T5: %s" % dm)
    kc(not any(bool(LL.floorOre(w)) for w in ("Lead", "Chromium", "Slag", "Titanium")) and str(LL.DFLOOR) == "" and bool(Cfg.GATE_NBL),
       "E: gate.oreFloor empty, gate.nextByLadder on by default")
    # ============================================================== H (critic round: nothing a player owns gets worse)
    tf = [(int(LL.tier(i)), int(Tool.tier(i)), str(LL.tnm(i))) for i in ("Tool_Pickaxe_Lead", "Tool_Axe_Lead", "Tool_Pickaxe_Lead_SkyWynn")]
    kc(tf == [(0, 0, "Crude"), (0, 0, "Crude"), (4, 4, "Lead")], "H M1: another mod's Tool_Pickaxe_Lead / Tool_Axe_Lead keep tier 0; ours read 4: %s" % tf)
    Props = JClass("java.util.Properties")
    U1 = L["U1"]

    def cap_of(k, iid, lv=None):
        pp = Props()
        pp.setProperty(str(LL.KIND[k]) + ".id", iid)
        if lv is not None:
            pp.setProperty(str(LL.KIND[k]) + ".up.spd", str(lv))
            return int(LL.lineCap(pp, JInt(k))), int(LL.perkEff(U1, pp, JInt(k), JInt(0)))
        return int(LL.lineCap(pp, JInt(k)))
    big = int(LL.LINE_BIG)
    ad = cap_of(0, "Tool_Pickaxe_Adamantite", 80)
    caps = [cap_of(0, i) for i in ("Tool_Pickaxe_Cobalt", "Tool_Pickaxe_Lead_SkyWynn", "Tool_Pickaxe_Titanium_SkyWynn", "Tool_Pickaxe_Lumen_SkyWynn")]
    caps2 = [cap_of(1, "Tool_Hatchet_Adamantite"), cap_of(int(LL.CAN), "Tool_WaterCan_Adamantite"), cap_of(3, "Tool_Sickle_Harvester_Thorium"),
             cap_of(2, "Tool_Hoe_Thorium"), cap_of(3, "Tool_Sickle_Iron"), cap_of(3, "Tool_Sickle_Harvester_Iron")]
    kc(ad == (big, 80) and caps == [50, 50, big, big] and caps2 == [big, big, big, big, big, 30],
       "H M2: an Adamantite pickaxe with 80 Breaking Power levels keeps all 80 (uncapped like 0.3.22); every 0.3.22 top stays uncapped; Cobalt / Lead 50: %s %s %s" % (ad, caps, caps2))
    kc(int(LL.topTier(JInt(0), "Tool_Pickaxe_Cobalt")) == 7 and bool(LL.isTop(JInt(0), "Tool_Pickaxe_Lumen_SkyWynn")) and not bool(LL.isTop(JInt(0), "Tool_Pickaxe_Dusk_SkyWynn")),
       "H M2: topTier = the ladder's last id's tier; isTop")
    cr = [int(LL.decideI(i, JInt(4), JInt(m))[0]) for i in ("Tool_Sickle_Harvester_Thorium", "Tool_Sickle_Harvester_Lead_SkyWynn") for m in (5, 6, 7)]
    kc(cr == [0] * 6, "H M3: a Thorium (and a Lead) Harvester reaps the tier 5-7 crops in full, like 0.3.22: %s" % cr)
    # ============================================================== F
    keys, olds, news = [str(x) for x in Cfg.H23_KEYS], [str(x) for x in Cfg.H23_OLD], [str(x) for x in Cfg.H23_NEW]
    lines = str(FRESH).split("\n")
    out = []
    for x in lines:
        if str(Cfg.H23_MARK_ID) in x:
            continue
        k = x.split("=", 1)[0]
        out.append(k + "=" + olds[keys.index(k)] if (k in keys and "=" in x) else x)
    old = "\r\n".join(out)
    kc(all(("\r\n%s=%s\r\n" % (k, o)) in old for k, o in zip(keys, olds)) and str(Cfg.H23_MARK_ID) not in old, "F: a 0.3.22-shaped file (the 5 old defaults, no marker)")
    r = Cfg.h23Update(old)
    nt = str(r[0]) if r is not None else ""
    kc(r is not None and all(("\r\n%s=%s\r\n" % (k, n)) in nt for k, n in zip(keys, news)) and nt.count(str(Cfg.H23_MARK_ID)) == 1
       and str(Cfg.H23_MARK) in nt[len(nt) // 2:] and len(str(r[1]).split(", ")) == 5 and len(list(r[3])) == 15 and "\n" not in nt.replace("\r\n", ""),
       "F: h23Update rewrites exactly the 5 old defaults, the marker at the END, CRLF kept: %s" % (str(r[1])[:160] if r is not None else None))
    kc(Cfg.h23Update(nt) is None, "F: a second run = null (run-once marker)")
    r2 = Cfg.h23Update(old.replace("\r\ngate.oreFloor=" + olds[3] + "\r\n", "\r\ngate.oreFloor=Lead\r\n"))
    kc(r2 is not None and "\r\ngate.oreFloor=Lead\r\n" in str(r2[0]) and any("gate.oreFloor=Lead kept" in str(x) for x in r2[2]) and len(str(r2[1]).split(", ")) == 4,
       "F: a hand-edited row is kept + noted, the others still update")
    # ============================================================== G
    tw = [str(Base.kunaiTwin(i)) for i in ("Weapon_Kunai_Lead_SkyWynn", "Weapon_Bo_Dusk_SkyWynn", "Weapon_GreatShield_Lumen_SkyWynn", "Weapon_Kunai_Iron")]
    mm = [str(Base.monkMetal(i)) for i in ("Weapon_Bo_Dusk_SkyWynn", "Weapon_Fist_Gauntlets_Slag_SkyWynn")]
    kc(tw[:3] == ["Weapon_Kunai_Lead_SkyWynn", "Weapon_Bo_Dusk_SkyWynn", "Weapon_GreatShield_Lumen_SkyWynn"] and tw[3] == "Weapon_Daggers_Iron"
       and mm == ["Dusk_SkyWynn", "Slag_SkyWynn"], "G: kunaiTwin keys the twin by the full <M>_SkyWynn word (none loaded yet = the id itself): %s %s" % (tw, mm))
    pid = set(str(x) for x in P("GearPool").P_ID)
    want = ["Weapon_%s_%s_SkyWynn" % (f, m) for f in ("Bo", "Fist_Gauntlets", "Kunai", "Spellbook", "GreatShield", "Crossbow", "Staff") for m in METALS[1:]] + \
        ["Weapon_Crossbow_%s_Wynn" % m for m in ("Thorium", "Cobalt", "Adamantite", "Mithril")]
    kc(set(want) <= pid and not [i for i in pid if i.startswith("Weapon_Wand_") and i.endswith("_SkyWynn")],
       "G: the loot pool knows the 60 new Armory ids (no wand): missing %s" % sorted(set(want) - pid)[:4])


# ---- older checks this round changes ON PURPOSE (prefix, why)
_WHY_GATE = ("0.3.23 by design (spec 3.2 'anything lower = 10x', the 0.3.22 note 'G2 empties gate.oreFloor'): every ladder step has a pickaxe now "
             "(PICK_T 1..16, gate.nextByLadder) and gate.oreFloor is empty - H323 E checks the new gate; off + the old floor = the 0.3.22 hits (build-proved)")
_WHY_LAD = ("0.3.23 by design (Skyy 'Yes, full 15-step ladder' + Q7): the pickaxe / hatchet / Harvester / can / Soul Cage ladders run Crude .. Lumen "
            "with bars (+ the log / crop item) - H323 C checks the new ladders")
WAIVE_323 = [("H322 A: GearLL.LT_* = tools/tier_tags.py TOOL_METALS / LADDER; PICK_T", _WHY_GATE),
             ("H322 A: ltag / lnoun / nextPick", _WHY_GATE),
             ("H322 C: decideI on ore = the model", _WHY_GATE),
             ("H322 D (critic M1): rpow = the right-tier pickaxe", _WHY_GATE + " (rpow numbers unchanged: each new step's pickaxe has its next vanilla pickaxe's specs)"),
             ("H322 D (critic M1): gate.oreFloor (default", _WHY_GATE),
             ("H322 D: LL.hit speed codes", _WHY_GATE)]
if not STATIC:
    _h319_prev = H319["_h319"]

    def _h319_to_h323(L, K):
        _h319_prev(L, K)
        try:
            _h323(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H323: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_to_h323
    H320["run_assets320"] = run_assets323          # the jar compare of THIS round (0.3.22 -> 0.3.23)
    H320["J319"] = J322
    H316["WAIVE_316"].extend(WAIVE_323)


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
            shutil.copyfile(GEN322, os.path.join(r, "SkyyGear", os.path.basename(GEN322)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.23.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.23.py (the committed file is the patch's output)")
        src = open(GEN322, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.23.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.23"\n' in s and "GENERATED by tools/gear_0_3_23_patch.py" in s, "A: VERSION 0.3.23 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        i = s.index
        check(i("G23_ZT = [") < i("G23_METALS = [") < i("G23_LADROW = {") < i("CAN_LAD_OLD, HARV_LAD_OLD") < i("G22_ORE = [") < i("G23_PICK_TV, G23_PICK_IDV")
              < i("G23_AR_POOL = (") < i("UP_SOUL15 = (") < i("H23_KEYS = [") < i("CFG_ROWS = ["), "A: the items, ladders, gate, Armory and migration blocks in order")
        check(i("public static String tnm(String id) {") < i("public static int lrank(String id) {") < i("public static String tierFor(java.util.UUID u, int k, String had) {")
              < i("public static boolean invested(String id, @BD@ d) {"), "A: tnm / lrank before their callers (javassist order)")
        check(i("public static boolean earlier(String x, String from) {") < i("public static Object[] fromRecipeAlt(") < i("public static Object[] cost0(String from, String to) {"),
              "A: earlier / fromRecipeAlt before cost0")
        check(i("@PKG@.GearCfg.migrate0322();") < i("@PKG@.GearCfg.migrate0323();") and s.count("@PKG@.GearCfg.migrate0323();") == 1
              and "CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), H23_WHO" in s, "A: migrate0323 after migrate0322, History snapshot first")
        check("MULTI_OWN.length" in s[i("public static boolean multiId(String id) {"):i("public static boolean multiId(String id) {") + 600],
              "A: multiId knows our multitools")
        check('("gate.nextByLadder", ' in s and '"gate.nextByLadder"}' in s, "A: the Server Setup row gate.nextByLadder (danger list)")
        check('"0", "4000", "", "", "live,danger",          # 0.3.23: 2000 -> 4000' in s, "A: lifelong.ladders may hold 4000 characters")
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
    assert os.path.isfile(J322), J322
    H320["main"]()


if __name__ == "__main__":
    main()
