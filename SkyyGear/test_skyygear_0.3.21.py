"""Harness for SkyyGear 0.3.21 (tools/gear_0_3_21_patch.py header = ZONE MINING SETS + ARMOR WEIGHT IN THE FLAVOUR TEXT) = the 0.3.20 harness
(and through it the whole older chain) run on the 0.3.21 jar + S321 (the jar compare 0.3.20 -> 0.3.21, replacing S320) + H321 (inside the h319
child, after H319 + H320, on the same booted engine), plus a --static phase that needs no jar:
    python tools/gear_0_3_21_patch.py && python SkyyGear/build_skyygear_0.3.21.py
    python SkyyGear/test_skyygear_0.3.21.py [--keep] [--only assets,h319,...]
    python SkyyGear/test_skyygear_0.3.21.py --static [--keep]          (no jars, no Assets.zip, no server jar)

  STATIC (--static)
       G  THE PATCH: tools/gear_0_3_21_patch.py run TWICE into a scratch tree (a copy of the patch + build_skyygear_0.3.20.py + deploy_set.py)
          -> byte-identical outputs, = SkyyGear/build_skyygear_0.3.21.py, compiles as Python, keeps the source's line endings
       A  THE ANCHORS: VERSION; the 8 zone rows (numbers, bands, ladder); GearMine IDS / TIER / RANK built from MINE + ZM; the zband hooks in
          GearLevel.level + band (after the 0.3.6 sets, before level.item); migrate0321 = the gmUpdate text on the ZM_ block, called after
          migrate0317; the fresh block before the 0.2.14 block; the Smithing ladder sort (Mining only); weightOf before hasDesc / descMsg,
          GearSmith.armorType = weightOf; flavTag in both FLAVOR places; the private art read + the clear stop; no new system / command
  S321 the jar 0.3.20 -> 0.3.21: adds exactly the 32 item JSONs + 32 textures + 32 icons, removes nothing, changes only manifest.json and
       server.lang (= 0.3.20's + the 64 zone lines); the changed classes = S321_MUST (+ S321_MAY); every item points at a VANILLA model
       path, its texture has the vanilla texture's size, its recipe = the vanilla piece's with the zone bar
  H321 (the h319 child, ONE booted engine) - real code:
       A  GearMine: 60 ids / 15 tiers, the zone pieces at index 28-59 (tier 7-14), setFor mining_<metal>, RANK = the ladder
       B  bands: GearLevel.band / level of a zone piece = garmor.zoneBands (default + a live edit + a bad text = default); vanilla tiers
          unchanged; checkZBands
       C  GM_TAB / readMine: the zone Fortune / Wisdom / lamp defaults; a garmor.mining.lead row overrides only Lead
       D  the fresh config: the 8 set.mining_* rows in STAB, setWhy accepts them; zmUpdate on a file without the block adds the 17 keys at the
          end (marker once, CRLF kept), a second run = null, a key already there is kept + noted; zmMissing names a deleted set row
       E  GearMine.doc of a new Lead piece: Set rarity, set mining_lead, level clamped into 22-27; rebirth -> Armor_Copper_<slot>;
          GearSmith.cat = Mining armor
       F  the flavour tag: vanilla Iron / Cloth / Leather armor -> "T3 Iron Heavy" / "... Cloth" / "... Light"; a pack piece = its table tag +
          its table weight; mining / gathering pieces and weapons = no weight; GearSmith.armorType == GearView.weightOf
  NOT COVERED (smoke test / Skyy in game): the items + recipes on the live asset store with SkyyWorldGen's bars, the look of Quirk's
  textures on the vanilla models, the migration on the real config.properties.
Scratch: tools/dev/scratch/minearmor/h321/gear/harness (full run) and .../h321/static (--static), deleted at the end unless --keep.
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


VERSION = "0.3.21"
V320 = "0.3.20"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "minearmor", "h321")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J320 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V320))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_21_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.21.py")
GEN320 = os.path.join(HERE, "build_skyygear_0.3.20.py")
METALS = ["Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]
BASES = ["Thorium", "Thorium", "Cobalt", "Cobalt", "Adamantite", "Adamantite", "Mithril", "Mithril"]
SLOTS = ["Head", "Chest", "Hands", "Legs"]
ZIDS = ["Armor_Mining_%s_%s" % (m, s) for m in METALS for s in SLOTS]
BANDS = [(22, 27), (24, 28), (28, 34), (31, 38), (37, 42), (39, 43), (43, 49), (46, 49)]
LADDER = ["Copper", "Iron", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril", "Titanium",
          "Lumen", "Onyxium"]

S321_MUST = {"GearPool": "the Bo / Fist bag types + the Armory class weapon rows", "GearUnid": "quest bags identify free", "GearMine": "15 tiers, RANK, zband / checkZBands", "GearCfg": "ZM_BANDS, the 60-piece tables, zmUpdate / migrate0321",
             "GearLevel": "the zband hooks", "GearSmith": "the ladder sort, armorType = GearView.weightOf",
             "GearView": "weightOf / tierFor / combatArmor / flavTag + the two FLAVOR places"}
S321_MAY = {"SkyyGearPlugin": "the version text + the migrate0321 call", "GearPackId": "pack rows: bag type indexes moved (+ Weapon_Fist)",
            "GearUt": "CRAFTED = the build-time craftable pool ids (+ the Armory rows)", "Gear": "the setup call", "GearFx": "the setup call",
            "CfgFn": "config kit: the version", "CfgRows": "config kit: the version", "CfgDefaults": "config kit", "CfgKit": "config kit",
            "CfgPub": "config kit", "CfgFile": "config kit", "GearCfgRows": "the row table"}

# ---- the 0.3.20 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
if not STATIC:
    _H320 = os.path.join(HERE, "test_skyygear_0.3.20.py")
    _T320 = open(_H320, encoding="utf-8").read()
    _cut = _T320.rindex('if __name__ == "__main__":')
    _argv = sys.argv
    _only = arg("--only")
    if _only:          # h321 runs inside the h319 child (like h320)
        _only = ",".join(sorted(set(("h319" if x == "h321" else x) for x in _only.split(","))))
    sys.argv = [_H320, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
        (["--only", _only] if _only else []) + [a for a in _argv[1:] if a in ("--h319",)] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H320 = {"__name__": "skyygear_h320", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T320[:_cut], _H320 + " (library)", "exec"), H320)
    sys.argv = _argv
    if _only:
        sys.argv[sys.argv.index("--only") + 1] = _only
    H320["VERSION"] = VERSION
    H319 = H320["H319"]
    H319["VERSION"] = VERSION
    H318 = H320["H318"]
    H316 = H320["H316"]
    cpool, has_ref = H320["cpool"], H320["has_ref"]
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


# ====================================================================================================== S321
def run_assets321():
    ea, eb = entries(J320), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    want = sorted(["Server/Item/Items/SkyyGear/MiningArmor/%s.json" % i for i in ZIDS]
                  + ["Common/Items/SkyyGear/MiningArmor/%s/%s_Texture.png" % (m, s) for m in METALS for s in SLOTS]
                  + ["Common/Icons/ItemsGenerated/%s.png" % i for i in ZIDS])
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(added == want and not gone and changed == ["Server/Languages/en-US/server.lang", "manifest.json"],
          "S321: 0.3.20 -> 0.3.21 adds exactly the 32 items + 32 textures + 32 icons, removes nothing, changes only manifest.json + server.lang: "
          "added %d (unexpected %s), gone %s, changed %s" % (len(added), sorted(set(added) - set(want))[:4], gone[:4], changed))
    check('"0.3.21"' in eb.get("manifest.json", b"").decode("utf-8", "replace"), "S321: the manifest says 0.3.21")
    la, lb = ea["Server/Languages/en-US/server.lang"].decode("utf-8"), eb["Server/Languages/en-US/server.lang"].decode("utf-8")
    new = lb[len(la):].splitlines() if lb.startswith(la) else None
    check(new is not None and len(new) == 64 and all(x.startswith("items.Armor_Mining_") for x in new)
          and "items.Armor_Mining_Lead_Head.name = Lead Helm" in new
          and any(x.startswith("items.Armor_Mining_Lumen_Legs.description = T7 Lumen - Lumen Mining Set") for x in new),
          "S321: server.lang = 0.3.20's + 64 zone lines (names like 'Lead Helm', descriptions led by the tier tag 'T7 Lumen - '): %s" % (new or [])[:2])
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.20 -> 0.3.21: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S321_MUST) | set(S321_MAY), "S321: only the patched classes changed: unexpected %s" % sorted(set(chg) - set(S321_MUST) - set(S321_MAY)))
    check(set(S321_MUST) <= set(chg), "S321: every class the patch edits really changed: unchanged %s" % sorted(set(S321_MUST) - set(chg)))
    check(not [n for n in eb if n.endswith(".blockymodel") and "MiningArmor" in n], "S321: no model file shipped for the zone sets (vanilla by path)")
    import struct
    bad = []
    for k, i in enumerate(ZIDS):
        m, s, b = METALS[k // 4], SLOTS[k % 4], BASES[k // 4]
        j = json.loads(eb["Server/Item/Items/SkyyGear/MiningArmor/%s.json" % i].decode("utf-8"))
        tx = eb.get("Common/" + j.get("Texture", ""), b"")
        ins = [(x["ItemId"], x["Quantity"]) for x in j.get("Recipe", {}).get("Input", [])]
        ok = (j.get("Model") == "Items/Armors/%s/%s.blockymodel" % (b, s) and j.get("Texture") == "Items/SkyyGear/MiningArmor/%s/%s_Texture.png" % (m, s)
              and j.get("Icon") == "Icons/ItemsGenerated/%s.png" % i and j["Armor"]["ArmorSlot"] == s and j.get("ItemLevel") == BANDS[k // 4][0]
              and tx[:8] == b"\x89PNG\r\n\x1a\n" and ins and ins[0][0] == "Ingredient_Bar_%s_SkyWynn" % m
              and not [x for x in ins if x[0].startswith("Ingredient_Bar_") and not x[0].endswith("_SkyWynn")]
              and j.get("TranslationProperties", {}).get("Name") == "server.items.%s.name" % i and "Parent" not in j)
        if not ok:
            bad.append(i)
    check(not bad, "S321: every zone item = the vanilla model of its zone base by path, our texture + icon, its slot, ItemLevel = the band "
                   "start, the recipe on the zone bar (no vanilla bar left), own name key: bad %s" % bad[:4])


# ====================================================================================================== H321 (in the h319 child)
def _h321(L, K):
    from jpype import JClass, JInt, JString
    P = lambda n: JClass(PKG + n)
    Mine, Cfg, Lvl, Smith, View, Data, Defs = P("GearMine"), L["Cfg"], L["Lvl"], L["Smith"], L["View"], L["Data"], L["Defs"]
    apply, FRESH = L["apply"], L["FRESH"]
    SR, Props = JClass("java.io.StringReader"), JClass("java.util.Properties")

    def kc(cond, what):
        K.check(bool(cond), "H321 " + what)

    def band(i):
        b = Lvl.band(i)
        return [int(b[0]), int(b[1]), int(b[2])]
    apply()
    # ============================================================== A
    ids = [str(x) for x in Mine.IDS]
    kc(len(ids) == 60 and ids[28:] == ZIDS and len(Mine.TIER) == 15 and [str(x) for x in Mine.TNAME][7:] == METALS and int(Mine.ZBASE) == 7,
       "A: GearMine 60 ids / 15 tiers, the zone pieces at 28-59 in metal order (%d ids, %s)" % (len(ids), ids[28:30]))
    kc(all(int(Mine.index(i)) == 28 + k and int(Mine.tier(i)) == 7 + k // 4 and bool(Mine.isPiece(i)) and str(Mine.setFor(i)) == "mining_" + METALS[k // 4].lower()
           for k, i in enumerate(ZIDS)), "A: index / tier / isPiece / setFor of every zone piece")
    order = sorted(["Armor_%s_Head" % t if t not in METALS else "Armor_Mining_%s_Head" % t for t in LADDER], key=lambda i: int(Mine.rank(i)))
    kc([int(Mine.rank("Armor_%s_Head" % t if t not in METALS else "Armor_Mining_%s_Head" % t)) for t in LADDER] == list(range(15))
       and int(Mine.rank("Armor_Iron_Chest")) == 1 and int(Mine.rank("Weapon_Sword_Iron")) == -1,
       "A: GearMine.rank = the ladder Copper .. Thorium, Lead, Dusk, Cobalt ... Mithril, Titanium, Lumen, Onyxium (%s)" % order[:5])
    # ============================================================== B
    kc(all(band(i) == [BANDS[k // 4][0], BANDS[k // 4][1], 1] and int(Lvl.level(i, None)) == BANDS[k // 4][0] for k, i in enumerate(ZIDS)),
       "B: GearLevel.band / level of every zone piece = garmor.zoneBands (default %s)" % [band(i) for i in ZIDS[::8]])
    kc(band("Armor_Thorium_Head")[:2] == [20, 28] and band("Armor_Mithril_Legs")[:2] == [40, 49] and band("Armor_Copper_Head")[:2] == [1, 18],
       "B: the vanilla mining tiers keep level.material (Thorium 20-28, Mithril 40-49, copper armor 1-18)")
    apply(garmor__zoneBands="10-12,24-28,28-34,31-38,37-42,39-43,43-49,46-49")
    kc(band("Armor_Mining_Lead_Chest")[:2] == [10, 12] and band("Armor_Mining_Dusk_Chest")[:2] == [24, 28], "B: a live garmor.zoneBands edit moves Lead only")
    apply(garmor__zoneBands="1-2,3")
    kc(band("Armor_Mining_Lead_Chest")[:2] == [22, 27], "B: a bad garmor.zoneBands = the default (one WARN)")
    apply()
    kc(Mine.checkZBands("garmor.zoneBands", "22-27,24-28,28-34,31-38,37-42,39-43,43-49,46-49") is None
       and Mine.checkZBands("garmor.zoneBands", "22-27") is not None and Mine.checkZBands("garmor.zoneBands", "5-4,24-28,28-34,31-38,37-42,39-43,43-49,46-49") is not None,
       "B: checkZBands: 8 min-max pairs, min <= max")
    # ============================================================== C
    f = [float(Mine.fortune(JInt(28 + s))) for s in range(4)]
    w = [float(Mine.wisdom(JInt(56 + s))) for s in range(4)]
    kc(f == [0.4, 0.5, 0.2, 0.4] and w == [1.8, 2.6, 1.1, 1.8] and int(Mine.lamp(JInt(7))) == 2 and int(Mine.lamp(JInt(14))) == 4
       and float(Mine.fortune(JInt(8))) == 0.3, "C: GM_TAB zone defaults in engine slot order (Lead Fortune %s, Lumen Wisdom %s), lamps, Thorium untouched" % (f, w))
    p = Props()
    p.load(SR(FRESH))
    p.setProperty("garmor.mining.lead", "1 2 3 4,0 0 0 0,1")
    t = Cfg.readMine(p)
    kc(list(t[0])[28:32] == [1.0, 2.0, 4.0, 3.0] and list(t[0])[32:36] == [0.4, 0.6, 0.3, 0.4] and list(t[2])[7] == 1,
       "C: a garmor.mining.lead row overrides only Lead (Dusk keeps its default)")
    # ============================================================== D
    sids = [str(x) for x in Cfg.STAB[0]]
    kc(all(("mining_" + m.lower()) in sids for m in METALS), "D: the fresh config's Armor sets hold the 8 zone Mining Sets")
    kc(all(Mine.setWhy("mining_" + m.lower(), "mfort+3 mpow+6 spd+2") is None for m in METALS) and Mine.setWhy("mining_lead", "hp+5") is not None,
       "D: setWhy: the zone sets take mfort / mwis / mpow / spd only")
    fresh = str(FRESH)
    zl = [x for x in fresh.split("\n")]
    hi = zl.index(str(Cfg.ZM_HEAD)) if str(Cfg.ZM_HEAD) in zl else -1
    blk_len = 2 + sum(int(x) for x in Cfg.ZM_GS) + len(Cfg.ZM_GC)
    old = "\r\n".join(x for k, x in enumerate(zl) if not (hi - 1 <= k < hi + blk_len))
    kc(hi > 0 and str(Cfg.ZM_MARK_ID) not in old, "D: a 0.3.20-shaped file (the fresh text minus the zone block)")
    r = Cfg.zmUpdate(old)
    nt = str(r[0]) if r is not None else ""
    pn = Props()
    pn.load(SR(nt))
    kc(r is not None and nt.startswith(old) and nt.count(str(Cfg.ZM_MARK_ID)) == 1 and all(pn.getProperty(str(k)) is not None for k in Cfg.ZM_GK)
       and len(str(r[2]).split(", ")) == 21 and "\r\n" in nt[len(old):] and nt.rstrip().endswith("level.material.Weapon_Crossbow_Copper=1,18"),
       "D: zmUpdate adds the 21 keys (zone rows + the 4 starter level rows) + the marker at the END, nothing before changes, CRLF kept: added %s" % (str(r[2])[:80] if r is not None else None))
    kc(Cfg.zmUpdate(nt) is None, "D: a second run = null (run-once marker)")
    old2 = old + "\r\nset.mining_lead=My Lead,4,mfort+1\r\n"
    r2 = Cfg.zmUpdate(old2)
    kc(r2 is not None and "set.mining_lead is already in the file - kept" in [str(x) for x in r2[1]] and str(r2[0]).count("set.mining_lead=") == 1,
       "D: a key already in the file is kept + noted, never written twice")
    nt3 = nt.replace("set.mining_dusk=Dusk Mining Set,4,mfort+3.5 mpow+7", "")
    kc(str(Cfg.zmMissing(nt3)) == "set.mining_dusk" and "set.mining_dusk=Dusk Mining Set,4,mfort+3.5 mpow+7" in str(Cfg.zmDefaults(nt3)),
       "D: zmMissing / zmDefaults name a deleted zone set row with its default")
    # ============================================================== E
    d = Mine.doc("Armor_Mining_Lead_Head", "craft", JInt(5))
    d2 = Mine.doc("Armor_Mining_Lead_Head", "craft", JInt(60))
    kc(int(Data.rarity(d)) == int(Defs.R_SET) and str(Data.str(d, "set", "")) == "mining_lead" and int(Data.num(d, "lvl", -1)) == 22
       and int(Data.num(d2, "lvl", -1)) == 27, "E: a new Lead piece: Set rarity, set mining_lead, level clamped into 22-27")
    Life = P("GearLife")
    kc(all(str(Life.rbArmorTo(i)) == "Armor_Copper_" + i.rsplit("_", 1)[1] for i in ZIDS[::5]), "E: rebirth -> the Copper piece of the slot")
    kc(all(int(Smith.cat(i)) == 1 for i in ZIDS) and str(Smith.gathSkill("Armor_Mining_Lumen_Legs")) == "Mining", "E: GearSmith: Mining armor, Mining skill")
    # ============================================================== F
    ft = lambda i: (lambda v: None if v is None else str(v))(View.flavTag(i))
    kc(ft("Armor_Bronze_Head") == "T3 Iron Heavy" and ft("Armor_Iron_Head") is None,
       "F: vanilla Bronze armor (Lv 15 band) = 'T3 Iron Heavy'; Iron armor is Mining armor = no weight (got %s / %s)" % (ft("Armor_Bronze_Head"), ft("Armor_Iron_Head")))
    cloth = [i for i in ("Armor_Cloth_Cotton_Head", "Armor_Cloth_Linen_Head", "Armor_Cloth_Silk_Head") if L["ITEM"].getAssetMap().getAsset(i) is not None]
    leath = [i for i in ("Armor_Leather_Light_Head", "Armor_Leather_Medium_Head", "Armor_Leather_Soft_Head") if L["ITEM"].getAssetMap().getAsset(i) is not None]
    kc(cloth and all(ft(i).endswith(" Cloth") and ft(i).startswith("T") for i in cloth) and leath and all(ft(i).endswith(" Light") for i in leath),
       "F: cloth armor ends 'Cloth', leather 'Light': %s %s" % ([ft(i) for i in cloth[:1]], [ft(i) for i in leath[:1]]))
    kc(ft("Armor_Copper_Head") is None and ft("Armor_Mining_Lead_Head") is None and ft("Weapon_Sword_Iron") is None
       and ft("Armor_Foraging_F1_Head") is None and ft("Armor_Onyxium_Head") is None, "F: mining / gathering pieces and weapons get no weight")
    GPI = P("GearPackId")
    pk = [str(x) for x in GPI.ID]
    pa = [i for i in pk if int(GPI.at(i)) > 0 and L["ITEM"].getAssetMap().getAsset(i) is not None][:40]          # the loaded stand-ins
    good = [i for i in pa if ft(i) == str(GPI.tag(i)) + " " + ["", "Heavy", "Light", "Cloth"][int(GPI.at(i))]]
    kc(pa and len(good) == len(pa), "F: a pack armor piece = its table tag + its table weight (%d of %d, e.g. %s)" % (len(good), len(pa), [ft(i) for i in pa[:2]]))
    allv = ["Armor_Iron_Head", "Armor_Bronze_Head", "Armor_Mining_Lead_Head"] + cloth + leath + pa[:10]
    kc(all(int(Smith.armorType(i)) == int(View.weightOf(i)) for i in allv), "F: GearSmith.armorType == GearView.weightOf (one rule)")
    kc(int(View.tierFor(JInt(9), "x")) == 1 and int(View.tierFor(JInt(10), "x")) == 2 and int(View.tierFor(JInt(34), "x")) == 5
       and int(View.tierFor(JInt(40), "x")) == 7 and int(View.tierFor(JInt(1), "Armor_Onyxium_Head")) == 8, "F: tierFor = tools/tier_tags.py tier_for_level")
    kc(str(Smith.groupName("Armor_Mining_Lead", JInt(1))) == "Lead Set" and str(Smith.groupName("Armor_Copper", JInt(1))) == "Copper Set",
       "F: Smithing card titles: 'Lead Set' like 'Copper Set' (critic L1)")
    # ============================================================== G: the starter quest gear
    Pool, Unid = P("GearPool"), P("GearUnid")
    tk = [str(x) for x in Pool.T_KEY]
    pid = [str(x) for x in Pool.P_ID]
    pt = dict((pid[i], tk[int(Pool.P_T[i])]) for i in range(int(Pool.P_N0)))
    kc("Weapon_Fist" in tk and "Weapon_Bo" in tk and str(Pool.T_NAME[tk.index("Weapon_Fist")]) == "Fist Weapon"
       and "Weapon_GreatShield" in tk and str(Pool.T_NAME[tk.index("Weapon_GreatShield")]) == "Great Shield"
       and pt.get("Weapon_Staff_Bo_Wood") == "Weapon_Bo" and pt.get("Weapon_Staff_Bo_Bamboo") == "Weapon_Bo"
       and not [i for i, t in pt.items() if t == "Weapon_Staff" and i.startswith("Weapon_Staff_Bo_")],
       "G: bag types Weapon_Bo (vanilla bo staves, never in a Staff bag) + the new Weapon_Fist + Weapon_GreatShield")
    want = {"Weapon_Bo_Iron": "Weapon_Bo", "Weapon_Fist_Gauntlets_Copper": "Weapon_Fist", "Weapon_Fist_Wraps_Linen": "Weapon_Fist",
            "Weapon_Kunai_Crude": "Weapon_Kunai", "Weapon_Spellbook_Copper": "Weapon_Spellbook", "Weapon_Crossbow_Copper_Wynn": "Weapon_Crossbow",
            "Weapon_GreatShield_Copper": "Weapon_GreatShield", "Weapon_GreatShield_Onyxium": "Weapon_GreatShield"}
    kc(all(pt.get(i) == t for i, t in want.items()) and not [i for i in pid if i.startswith("Weapon_Bo_UT_")],
       "G: SkyyArmory's class weapon ladders are pool rows of their type (UT ids stay out): %s" % dict((i, pt.get(i)) for i in want))
    kc(band("Armor_Leather_Soft_Head")[:2] == [1, 12] and band("Armor_Cloth_Wool_Chest")[:2] == [1, 12] and band("Weapon_Spellbook_Copper")[:2] == [1, 18]
       and band("Weapon_Crossbow_Copper_Wynn")[:2] == [1, 18] and band("Weapon_Kunai_Crude")[:2] == [1, 13] and band("Armor_Leather_Medium_Head")[0] > 1,
       "G: Lv 1 starts: Light (Leather_Soft) + Cloth (Cloth_Wool) armor 1-12, Copper spellbook / crossbow 1-18, Crude kunai 1-13; others unchanged (%s)"
       % [band(i)[:2] for i in ("Armor_Leather_Soft_Head", "Armor_Cloth_Wool_Chest", "Weapon_Spellbook_Copper", "Weapon_Kunai_Crude", "Armor_Leather_Medium_Head")])
    ty = tk.index("Armor_Chest")
    bq = Unid.makeZ(JInt(ty), JInt(2), JInt(1), JInt(3), JInt(5), "quest", "test", JInt(1), JInt(0))
    bm = Unid.makeZ(JInt(ty), JInt(2), JInt(1), JInt(3), JInt(5), "mob", "test", JInt(1), JInt(0))
    cq, cm = int(Unid.cost(Unid.doc(bq))), int(Unid.cost(Unid.doc(bm)))
    apply(unid__questFree="false")
    cq2 = int(Unid.cost(Unid.doc(bq)))
    apply()
    kc(cq == 0 and cm > 0 and cq2 == cm, "G: a quest bag identifies free (unid.questFree on), a mob bag pays %d; questFree off = it pays too (%d / %d)" % (cm, cq, cq2))


if not STATIC:
    _h319_prev = H319["_h319"]

    def _h319_to_h321(L, K):
        _h319_prev(L, K)
        try:
            _h321(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H321: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_to_h321
    H320["run_assets320"] = run_assets321          # the jar compare of THIS round (0.3.20 -> 0.3.21)
    H320["J319"] = J320


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
            shutil.copyfile(GEN320, os.path.join(r, "SkyyGear", os.path.basename(GEN320)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.21.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.21.py (the committed file is the patch's output)")
        src = open(GEN320, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.21.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.21"\n' in s and "GENERATED by tools/gear_0_3_21_patch.py" in s, "A: VERSION 0.3.21 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        # the zone rows
        i_z = s.index("ZM_ROWS = [")
        zr = s[i_z:s.index("]\n", s.index('("lumen"', i_z)) + 2]
        ns = {}
        exec(zr, ns)
        rows = ns["ZM_ROWS"]
        check([r[1] for r in rows] == METALS and [r[2] for r in rows] == BASES and [r[8] for r in rows] == BANDS,
              "A: the 8 zone rows: metals, vanilla bases, bands %s" % [r[8] for r in rows])
        check('ZM_LADDER = ["Copper", "Iron", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril", "Titanium",\n             "Lumen", "Onyxium"]' in s
              and "assert ZM_FULL == [4.5, 5.2, 6.7, 7.5, 9.3, 10.3, 12.5, 13.7]" in s, "A: the ladder + the full-set Fortune ladder are asserted at build time")
        check('F(gmine, "public static final String[] IDS = %s;" % jarr(MINE_IDS + ZM_IDS))' in s and 'jarr([_t.lower() for _t in MINE_ALL_TIERS])' in s
              and 'F(gmine, "public static final int[] RANK = %s;" % jints(MINE_RANK))' in s and "_jd(MINE_F + ZM_F)" in s,
              "A: GearMine / GearCfg tables = the 7 vanilla tiers + the 8 zone tiers")
        i_b = s.index("public static int[] band(String id) {\n  if (id == null) return new int[] { 0, 0, 3 };")
        bb = s[i_b:s.index('}""")', i_b)]
        check(bb.index("@PKG@.GearGArm.band(id)") < bb.index("@PKG@.GearMine.zband(id)") < bb.index("@PKG@.GearCfg.ITEMLVL.get(id)"),
              "A: GearLevel.band: the zone band after the 0.3.6 sets, before level.item / the material match")
        i_l = s.index("public static int level(String id, @BD@ d) {")
        lb = s[i_l:s.index('}""")', i_l)]
        check(lb.index("@PKG@.GearGArm.band(id)") < lb.index("@PKG@.GearMine.zband(id)") < lb.index("@PKG@.GearCfg.ITEMLVL.get(id)"), "A: GearLevel.level: the same order")
        i_g = s.index("public static Object[] gmUpdate(String text) {")
        i_zu = s.index("public static Object[] zmUpdate(String text) {")
        gu = s[i_g:s.index('}""")', i_g)]
        zu = s[i_zu:s.index('}""")', i_zu)]
        check(zu == gu.replace("gmUpdate", "zmUpdate").replace("GM_", "ZM_"), "A: zmUpdate = the 0.2.15 gmUpdate text on the ZM_ block")
        check(s.index("@PKG@.GearCfg.migrate0317();") < s.index("@PKG@.GearCfg.migrate0321();") and s.count("@PKG@.GearCfg.migrate0321();") == 1
              and "CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), ZM_WHO" in s and s.index("if (!lvSaved(old)) {", s.index("public static synchronized String migrate0321()"))
              < s.index("@PKG@.CfgRows.atomicWrite(f, data);", s.index("public static synchronized String migrate0321()")),
              "A: migrate0321 after migrate0317, History snapshot verified before the atomic write")
        check('    L += [""] + ZM_LINES       # 0.3.21' in s and s.index('L += [""] + ZM_LINES') < s.index('L += [""] + GU_LINES'), "A: the fresh block before the 0.2.14 block")
        check('int rk = c == 1 && o0.length > 0 ? @PKG@.GearMine.rank(o0[0]) : -1;' in s and "gk[i] = rk >= 0 ? rk : 1000 + gk[i];" in s,
              "A: the Smithing cards: Mining armor by the ladder, the rest by band start as before")
        check(s.index("public static int weightOf(String id)") < s.index("public static boolean hasDesc(String id)") < s.index("public static @MSG@ descMsg(")
              and "  return @PKG@.GearView.weightOf(id);          // 0.3.21" in s and "String tg = flavTag(id);" in s
              and "if (hasDesc(id) || flavTag(id) != null) add(lt, lc, FLAVOR, null);" in s,
              "A: weightOf before its callers; GearSmith.armorType = weightOf; flavTag in both FLAVOR places")
        check('raise SystemExit("SkyyGear 0.3.21 needs Quirk\'s private mining armor textures' in s and "SKYWYNN_PRIVATE_ART" in s
              and '"the VANILLA model is used"' not in s and "- the VANILLA model is used" in s and "SA.render_icon(_vmodel, _qtex, _props" in s,
              "A: the private textures read at build time with a clear stop; models only compared; icons rendered from the vanilla model")
        check('("garmor.zoneBands", "Zone mining armor levels", "garmor", "text", ZM_BANDS_DEF' in s and '"garmor.zoneBands", "unid.questFree"}' in s
              and 'ZM_BANDS = ptext(p, "garmor.zoneBands", "@ZMBANDS@").trim();' in s, "A: the Server Setup row (danger list, apply line)")
        check("for _i in ARMORY_POOL:" in s and '+ ["Weapon_GreatShield_" + _m for _m in _AM7])' in s and "len(ARMORY_POOL) == 43" in s and '("unid.questFree", "Quest bags identify free", "loot", "bool", "true"' in s
              and 'UNID_QFREE = pbool(p, "unid.questFree", true);' in s and '\\"quest\\".equals(@PKG@.GearData.str(d, \\"src\\"' in s
              and 'ST_BANDS = [("Armor_Leather_Soft", 1, 12), ("Armor_Cloth_Wool", 1, 12), ("Weapon_Spellbook_Copper", 1, 18), ("Weapon_Crossbow_Copper", 1, 18)]' in s
              and '    + ":" + flavTag(id);          // 0.3.21 critic M1' in s and 'soft: SkyyWorldGen 0.7.3+' in s
              and 'if (s.startsWith("Armor_Mining_")) s = s.substring(13);' in s,
              "A: the starter quest gear (Armory pool rows, Lv 1 starts, quest bags free) + the critic fixes (sig, card title, manifest)")
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
    assert os.path.isfile(J320), J320
    H320["main"]()


if __name__ == "__main__":
    main()
