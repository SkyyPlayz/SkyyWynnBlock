"""Harness for SkyyGear 0.3.19 (tools/gear_0_3_19_patch.py header = PACK DROPS, cloud build trial) = the 0.3.18 harness's children run on the
0.3.19 jar + S319 + H319, plus a --static phase that needs no jar:
    python tools/gear_0_3_19_patch.py && python SkyyGear/build_skyygear_0.3.19.py
    python SkyyGear/test_skyygear_0.3.19.py [--keep] [--only assets,h319,h318,h317,h316,...]
    python SkyyGear/test_skyygear_0.3.19.py --static [--keep]          (no jars, no Assets.zip, no server jar - runs anywhere)

  UNVERIFIED: everything except --static was written on the cloud trial box (no SkyyGear jars, no Assets.zip, no cached server jar there)
  and has NEVER RUN. The local session runs it first (it needs SkyyGear-0.3.18.jar + 0.3.19.jar, the older jars the 0.3.18 chain reads,
  Assets.zip and the cached server jar) and fixes the harness where the harness, not the jar, is wrong.

  STATIC (--static; ran OK on the trial box)
       T  THE PACK TABLE (tools/pack_drops.py): the CLI exits 0; check() is empty; rows() unique, in active_sets() order, each field = its
          set (set index, weight index, zone_of(tier), role index); every ut / mythic set at its zone's top tier; one Mythic set per zone x
          weight / weapon type; ids never hold ';' (GearPackId's packed separator) or ','; each packed column < 65535 bytes (one JVM string
          constant); tags "T<n> <Word>" (iron = "T3 Iron"); no id of a todo / needs-ids source or an off set in rows(), and no todo /
          needs-ids id anywhere in the generated build script; the ids H319 loads have the roles H319 expects
       G  THE PATCH: tools/gear_0_3_19_patch.py run TWICE into a scratch tree (a copy of the patch + build_skyygear_0.3.18.py + deploy_set.py;
          the real pack_drops module) -> byte-identical outputs (deterministic), = SkyyGear/build_skyygear_0.3.19.py when that file exists,
          compiles as Python
       A  THE ANCHORS in the generated script: VERSION; the 6 Server Setup rows (key, type, default, min / max = the GearCfg.apply bounds,
          field:GearCfg.<F>, flags; part.packDrops + loot.boss.mythic danger); the 6 CFG_FIELDS defaults; G319_ROWK under G319_HEAD in the
          fresh file; G319_CLASSES in the jar's class list; GearPackId's block after the GearCfg field loop and before every other class's
          use of it; GearPack before GearDeathMark's tick; the bossRoll call inside tick (PACK_ON + try / warnOnce); the swap guard in
          GearCraftSys between craftable() and getReferenceTo(); makeZ adds "pz" only when pz > 0, make() = makeZ(..., 0); no w(int) left;
          the manifest names PACK DROPS + LadyPaladra + CC BY-NC; registerSystem / registerCommand counts = 0.3.18's; mk() classes: only
          GearPackId + GearPack + GearPackGive new, none gone. The review fixes: why / rerollWhy (its weight or any weight, else the zone
          refusal), pickZ refuses a boss bag with no Mythic piece left (M5), matchM / pickItemM by the set share only (M5), rollers' killer
          only for an empty credit list (M4), bossRoll: chance -> bag -> capOk (BN[6], M3) -> seam / GearPackGive task / ground drop,
          GearPackGive (inventory -> feet -> boss, the LOOT boss-give line), BN[7] + "hourly cap", GearCraftPreSys swapVeto (M1), no
          Smithing XP for pack pieces in GearCraftTask (M2), gear.exclude in isGearMs (L2)
       S  THE CHANGED CLASSES by text: every changed line of 0.3.18 -> 0.3.19 mapped to the M / F / C / event_system call it sits in = exactly
          S319_MUST + S319_NEW (the same constants S319 checks on the real jars)
       P  the class-file constant-pool reader S319 C uses, self-tested on every class of tools/javassist.jar
  S319 the jar 0.3.18 -> 0.3.19: adds exactly GearPackId + GearPack + GearPackGive, removes nothing, changes only manifest.json among the files (it says
       0.3.19, PACK DROPS, LadyPaladra); the changed classes = every class of S319_MUST (each explained there) + at most S319_MAY
       C  BY CLASS FILE (the bare engine has no dying NPC / ECS death chunk / real CraftRecipeEvent): GearDeathMark references
          GearPack.bossRoll (and 0.3.18's does not); GearCraftSys references GearPackId.swap; GearPack holds the string "mob:fn:boss" and
          references Gear.fn, GearLoot.ROLLED + capOk, GearUnid.makeZ, new GearPackGive + World.execute, ItemComponent.generateItemDrops +
          CommandBuffer.addEntities; GearPackGive (a Runnable) references ItemContainer.addItemStack, ItemUtils.dropItem, generateItemDrops +
          Store.addEntities, GearStamp.invOf; GearCraftPreSys references GearPack.swapVeto and GearCraftTask GearPackId.has (0.3.18's neither)
  H319 ONE booted engine (the 0.3.5 life setup):
       A  GearPackId = tools/pack_drops.py: ID (count + order), SET / AT / ZONE / ROLE / TY, S_TIER / S_KEY / S_NAME / S_TAG; idx / has /
          tier / tag / at of named ids; GearPool.P_ID = the vanilla rows + the table; part.packDrops=false -> has / tier / tag / at off, idx
          kept; the 6 rows (index, danger / live flags), the fresh file block, the field defaults, the bounds clamp
       B  A SCRATCH STAND-IN PACK (generated now into the scratch folder, never committed; each item = {"Parent": <a vanilla id>} only, the
          cross-pack Parent The Armory itself uses; no file of The Armory is read or copied) with 9 table ids, loaded with addpack(); a
          refused pack = ONE failed check with the reason, the pack checks skipped. Then: RookChestBlack = gear / combat / slot 2, band = the
          Iron level.material row, armorType Rook 1 / Warden 2; a table id not loaded = typeOfId -1, never a candidate; GearPool.table(): live
          type, set-share weights (two Rook chests 0.5 each, one Rook helm 1.0, x loot.packWeight), Mythic rows ok but never match(), ut rows
          never ok; pickItem over 2000 draws = the computed pack share (loose bound), never a Mythic / ut / missing id; part.packDrops=false =
          no pack row, not gear, the band back to the id-word rule
       C  MYTHIC: rangeM = the Iron band of the zone-1 Heavy chest, candM zone 2 = 0; mythicBag(1) = Skyy_Unid_Bag_Mythic with pz 1, r mythic,
          the boss line in its tooltip; open() = IronDragonChestplate (Heavy) / WardenChest (Light), Mythic, box.pz 1; why() / rerollWhy()
          null; reroll keeps the zone; the zone's pieces gone (part.packDrops off) = rerollWhy / why refuse, reroll / open null (M5); a Heavy
          head bag / a zone-3 bag wait, a Cloth chest bag opens into another weight's chest; loot.packWeight 0 = out of normal bags, still
          in the Mythic picks; an ordinary bag has no pz (the 0.3.18 key list); mythicBag(3) = null; pickTypeM lean x3 vs none (zone 4)
       D  TOOLTIP: GearView.lines + descMsg of a documented RookChestBlack: the flavour slot starts "T3 Iron" (grey italic), gone when off
       E  GearPool.packText() / GearLoot.countsText(): "pack drops on", the live / Mythic / ut / missing counts, the 7 counters = GearPool.BN
       F  THE REAL GearPack.bossRoll ON STAND-INS (FakeChunk / FakeStore / FakeBuffer of the older harnesses, a Python mob:fn:boss, the
          GearLoot.SPAWN seam): F0 the real GearDeathMark.tick on a dying boss (the 0.2.11 X10 rig) reaches it; credited >= 15 % roll,
          below not; once per death; not a boss / zone 0 / no Mythic in the zone / Creative / loot.boss.mythic 0 / part.packDrops off / no
          SkyyMobs = nothing; an empty credit list = the killer (logged), credited players all under the bar = nobody (M4); the hourly cap
          (loot.mob.capPerHour 2: the third bag stopped, BN[6], M3 - skipped if the stand-in is an admin); 10 % over 600 deaths (loose; the
          cap row set to 1000 for every F roll)
       G  GearPackGive.run on a stand-in player world (the 0.3.5 world()): the bag lands in the inventory, "LOOT boss-give ... -> inventory",
          the player is told (the feet / boss fallbacks need a real ECS store - S319 C checks them by class file)
Scratch: tools/dev/scratch/trial-armor-drops/h319/gear/harness (full run) and .../h319/static (--static), deleted at the end unless --keep.
Exit code 1 on any failure (--static: 0 = PASS).
"""
import os, sys, json, shutil, zipfile, struct, re, subprocess

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


VERSION = "0.3.19"
V318 = "0.3.18"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "trial-armor-drops", "h319")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J318 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V318))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_19_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.19.py")
GEN318 = os.path.join(HERE, "build_skyygear_0.3.18.py")

# ---- the classes 0.3.19 changes (S319 on the jars, STATIC S on the script text) - each one explained
S319_NEW = {"GearPackId": "the pack table (tools/pack_drops.py as packed columns) + the swap guard",
            "GearPack": "the Mythic boss bags (mythicBag, rollers, swapVeto, bossRoll; SkyyMobs 0.1.10 mob:fn:boss)",
            "GearPackGive": "review H2: the world task that puts a won boss bag into its winner's inventory (else feet, else the boss)"}
S319_MUST = {"GearAnvil": "local rebuild: the Identify / Appraisal Tool lines say Void Charms (patch item 9)",
             "GearFn": "critic fix 2: gear:fn:roll mode 8 - a swap / UT / Mythic output plain, no Smithing XP for pack pieces",
             "GearRoll": "critic fix 1: unidDoc - a UT / Mythic table piece found = plain Normal",
             "GearTag": "critic fix 1: spread - no bags of a UT / Mythic table piece",
             "SmithFn": "critic fix 2: gear:fn:classShow false for a UT / Mythic table piece",
             "GearData": "isGearMs / isGear / kindFor: a table id is combat gear while part.packDrops is on (gear.exclude still wins, review L2)",
             "GearLevel": "level / entry: the table tier's level.material row first",
             "GearSmith": "armorType: the table weight",
             "GearView": "lines + descMsg: the tier tag in the flavour slot",
             "GearPool": "the pack rows after the vanilla ones (P_N0, P_ZONE / P_ROLE / P_SET), liveType, w(t, i), table t[7] / t[8], the "
                         "Mythic picks (set share only, review M5), bcount / BN[7], packText",
             "GearUnid": "pz, makeZ / make, pickZ (a boss bag refused when its zone has no Mythic piece left, review M5) / pick, open / "
                         "reroll keep pz, why / rerollWhy, the boss line in descMsg",
             "GearLoot": "countsText + packText",
             "GearDeathMark": "tick calls GearPack.bossRoll",
             "GearCraftSys": "the swap guard (GearPackId.swap) in the CraftRecipeEvent$Post handler",
             "GearCraftPreSys": "review M1: CraftRecipeEvent$Pre cancels a pack swap while a rolled input piece is held (GearPack.swapVeto)",
             "GearCraftTask": "review M2: no Smithing craft XP for a pack piece",
             "GearCfg": "the 6 fields, their apply() lines, the fresh file block"}
S319_MAY = {"GearDeathMarkU": "its subclass (constructor only; expected byte-identical, allowed if javassist re-emits it)",
            "SkyyGearPlugin": "the version text in the ready line",
            "CfgFn": "config kit: the rows / version", "CfgRows": "config kit: the 6 new rows", "CfgDefaults": "config kit: the 6 defaults",
            "CfgKit": "config kit", "CfgPub": "config kit", "CfgFile": "config kit: the fresh file text"}
# the 6 Server Setup rows: key -> (type, default, min, max, GearCfg field, danger)
ROWS319 = {"part.packDrops": ("bool", "true", "", "", "PACK_ON", True), "loot.packWeight": ("dec", "1", "0", "100", "PACK_W", False),
           "loot.boss.mythic": ("dec", "10", "0", "100", "BOSS_MY", True), "loot.boss.credit": ("int", "15", "0", "100", "BOSS_CREDIT", False),
           "loot.boss.classLean": ("int", "3", "1", "10", "BOSS_LEAN", False),
           "loot.boss.armorShare": ("int", "50", "0", "100", "BOSS_ARMOR", False)}
# the stand-in pack H319 loads: (table id, its set key, its role, vanilla parents to try - "Prefix*" = the first single item with that prefix)
TEST_PACK = [("RookChestBlack", "armory_rook", "drop", ["Armor_Iron_Chest"]),
             ("RookChestAzure", "armory_rook", "drop", ["Armor_Iron_Chest"]),
             ("RookHelmBlack", "armory_rook", "drop", ["Armor_Iron_Head"]),
             ("IronDragonChestplate", "armory_iron_dragon", "mythic", ["Armor_Iron_Chest"]),
             ("WardenChest", "armory_warden", "mythic", ["Armor_Leather_Light_Chest", "Armor_Leather_Medium_Chest", "Armor_Leather_Soft_Chest",
                                                          "Armor_Leather_Heavy_Chest", "Armor_Cloth_Linen_Chest", "Armor_Iron_Chest"]),
             ("GhostCalvaryHelm", "armory_calvary_ghost", "ut", ["Armor_Iron_Head"]),
             ("Sword_Iron_Black", "armory_sword_iron", "drop", ["Weapon_Sword_Iron"]),
             ("LahatChereb", "armory_lahat", "mythic", ["Weapon_Mace_Iron", "Weapon_Mace_*"]),
             ("DualRuneBlade", "armory_dual_runeblade", "mythic", ["Weapon_Daggers_Iron", "Weapon_Daggers_*"])]
NOT_LOADED = ("CalvaryChestBlack", "armory_calvary", "drop")


def cpool(data):
    """the constant pool of a class file (pure Python, no JVM): {"class": set, "str": set, "ref": set((F|M|I, owner, name, descriptor))}"""
    if data[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("not a class file")
    n = struct.unpack(">H", data[8:10])[0]
    ent = [None] * n
    i, p = 1, 10
    while i < n:
        t = data[p]
        if t == 1:
            ln = struct.unpack(">H", data[p + 1:p + 3])[0]
            ent[i] = (1, data[p + 3:p + 3 + ln].decode("utf-8", "replace"))
            p += 3 + ln
        elif t in (3, 4):
            ent[i] = (t, None)
            p += 5
        elif t in (5, 6):
            ent[i] = (t, None)
            p += 9
            i += 1
        elif t in (7, 8, 16, 19, 20):
            ent[i] = (t, struct.unpack(">H", data[p + 1:p + 3])[0])
            p += 3
        elif t in (9, 10, 11, 12, 17, 18):
            ent[i] = (t, struct.unpack(">HH", data[p + 1:p + 5]))
            p += 5
        elif t == 15:
            ent[i] = (t, None)
            p += 4
        else:
            raise ValueError("constant tag %d at byte %d" % (t, p))
        i += 1
    u = lambda k: ent[k][1]
    out = {"class": set(), "str": set(), "ref": set()}
    for e in ent:
        if e is None:
            continue
        if e[0] == 7:
            out["class"].add(u(e[1]))
        elif e[0] == 8:
            out["str"].add(u(e[1]))
        elif e[0] in (9, 10, 11):
            ci, nt = e[1]
            nm, ds = ent[nt][1]
            out["ref"].add(({9: "F", 10: "M", 11: "I"}[e[0]], u(ent[ci][1]), u(nm), u(ds)))
    return out


def has_ref(cp, kind, owner_end, name):
    return any(r[0] in kind and r[1].endswith(owner_end) and r[2] == name for r in cp["ref"])


# ---- the 0.3.18 harness as a library (it loads the older ones); its main runs every child on THIS jar in THIS scratch folder
if not STATIC:
    _H318 = os.path.join(HERE, "test_skyygear_0.3.18.py")
    _T318 = open(_H318, encoding="utf-8").read()
    _cut = _T318.rindex('if __name__ == "__main__":')
    _argv = sys.argv
    sys.argv = [_H318, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
        (["--only", arg("--only")] if arg("--only") else [])
    H318 = {"__name__": "skyygear_h318", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T318[:_cut], _H318 + " (library)", "exec"), H318)
    sys.argv = _argv
    H318["VERSION"] = VERSION
    H318["H317"]["VERSION"] = VERSION
    H316 = H318["H316"]
    H316["VERSION"] = VERSION
    H35 = H318["H35"]
    FI7_SRC = H318["FI7_SRC"]
    FAKE_PKG = H316["FAKE_PKG"]
    WAIVE_319 = []          # (prefix, why): no older check is waived - none is known to change on purpose (add one only with its why)
    H316["WAIVE_316"].extend(WAIVE_319)
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


# ====================================================================================================== S319
def run_assets319():
    ea, eb = entries(J318), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(added == sorted("com/skyy/gear/%s.class" % c for c in S319_NEW) and not gone and changed == ["manifest.json"],
          "S319: 0.3.18 -> 0.3.19 adds GearPack + GearPackGive + GearPackId, removes nothing, changes only manifest.json among the files: added %s, gone %s, changed %s"
          % (added[:4], gone[:4], changed))
    man = eb.get("manifest.json", b"").decode("utf-8", "replace")
    check('"0.3.19"' in man and "PACK DROPS" in man and "LadyPaladra" in man and "CC BY-NC" in man,
          "S319: the manifest says 0.3.19 and names PACK DROPS + LadyPaladra (CC BY-NC credit)")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.18 -> 0.3.19: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S319_MUST) | set(S319_MAY),
          "S319: only the pack-drop classes (+ config / version text) changed: unexpected %s" % sorted(set(chg) - set(S319_MUST) - set(S319_MAY)))
    check(set(S319_MUST) <= set(chg), "S319: every class the patch edits really changed: unchanged %s" % sorted(set(S319_MUST) - set(chg)))
    # C: by class file - the paths the bare engine cannot drive (a real dying NPC in an ECS death chunk, a real CraftRecipeEvent)
    try:
        cdm = cpool(eb["com/skyy/gear/GearDeathMark.class"])
        cdm0 = cpool(ea["com/skyy/gear/GearDeathMark.class"])
        ccs = cpool(eb["com/skyy/gear/GearCraftSys.class"])
        cpk = cpool(eb["com/skyy/gear/GearPack.class"])
    except Exception as e:
        check(False, "S319 C: the class files could not be read: %s" % e)
        return
    check(has_ref(cdm, "M", "com/skyy/gear/GearPack", "bossRoll") and not has_ref(cdm0, "M", "com/skyy/gear/GearPack", "bossRoll"),
          "S319 C: GearDeathMark (the death tick) calls GearPack.bossRoll; 0.3.18's did not")
    check(has_ref(ccs, "M", "com/skyy/gear/GearPackId", "swap"), "S319 C: GearCraftSys (CraftRecipeEvent$Post) calls GearPackId.swap (the swap guard)")
    check("mob:fn:boss" in cpk["str"] and has_ref(cpk, "M", "com/skyy/gear/Gear", "fn")
          and has_ref(cpk, "M", "/ItemComponent", "generateItemDrops") and has_ref(cpk, "MI", "/CommandBuffer", "addEntities")
          and has_ref(cpk, "F", "com/skyy/gear/GearLoot", "ROLLED") and has_ref(cpk, "M", "com/skyy/gear/GearUnid", "makeZ")
          and not has_ref(cpk, "M", "com/skyy/gear/GearLoot", "capOk") and has_ref(cpk, "M", "com/skyy/gear/GearPack", "firstOfFight")
          and has_ref(cpk, "M", "com/skyy/gear/GearPackGive", "<init>")
          and has_ref(cpk, "MI", "/World", "execute"),
          "S319 C: GearPack.bossRoll asks mob:fn:boss through Gear.fn, once per death (GearLoot.ROLLED), once per fight (firstOfFight, no hourly cap - critic 4 / 5), bags by "
          "GearUnid.makeZ, delivered by a GearPackGive world task (World.execute), else ItemComponent.generateItemDrops + CommandBuffer.addEntities")
    try:
        cgv = cpool(eb["com/skyy/gear/GearPackGive.class"])
        cps = cpool(eb["com/skyy/gear/GearCraftPreSys.class"])
        cps0 = cpool(ea["com/skyy/gear/GearCraftPreSys.class"])
        ctk = cpool(eb["com/skyy/gear/GearCraftTask.class"])
        ctk0 = cpool(ea["com/skyy/gear/GearCraftTask.class"])
    except Exception as e:
        check(False, "S319 C: the class files could not be read: %s" % e)
        return
    check(has_ref(cgv, "MI", "/ItemContainer", "addItemStack") and has_ref(cgv, "MI", "/ItemUtils", "dropItem")
          and has_ref(cgv, "M", "/ItemComponent", "generateItemDrops") and has_ref(cgv, "MI", "com/hypixel/hytale/component/Store", "addEntities")
          and has_ref(cgv, "M", "com/skyy/gear/GearStamp", "invOf") and "java/lang/Runnable" in cgv["class"],
          "S319 C: GearPackGive (a Runnable) puts the bag into the winner's containers (ItemContainer.addItemStack), else ItemUtils.dropItem, "
          "else generateItemDrops + Store.addEntities at the boss")
    check(has_ref(cps, "M", "com/skyy/gear/GearPack", "swapVeto") and not has_ref(cps0, "M", "com/skyy/gear/GearPack", "swapVeto"),
          "S319 C: GearCraftPreSys (CraftRecipeEvent$Pre) calls GearPack.swapVeto (review M1); 0.3.18's did not")
    check(has_ref(ctk, "M", "com/skyy/gear/GearPackId", "has") and not has_ref(ctk0, "M", "com/skyy/gear/GearPackId", "has"),
          "S319 C: GearCraftTask asks GearPackId.has before paying Smithing XP (review M2)")


# ====================================================================================================== H319
def run_h319(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h319(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H319: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h319(L, K):
    from jpype import JClass, JInt, JFloat, JDouble, JObject, JString, JLong, JArray, JImplements, JOverride
    import pack_drops as PKD
    br, Gear, Cfg, Data, Roll, Lvl, Smith, View, Defs, ITEM, us, jf = (L["br"], L["Gear"], L["Cfg"], L["Data"], L["Roll"], L["Lvl"], L["Smith"],
                                                                         L["View"], L["Defs"], L["ITEM"], L["us"], L["jf"])
    U1, U2, PR1, PR2, apply, logs, FRESH = L["U1"], L["U2"], L["PR1"], L["PR2"], L["apply"], L["logs"], L["FRESH"]
    P = lambda n: JClass(PKG + n)
    GPI, Pool, Unid, Pack, Loot, CRows = P("GearPackId"), P("GearPool"), P("GearUnid"), P("GearPack"), P("GearLoot"), P("CfgRows")
    AL = JClass("java.util.ArrayList")
    ROWS = PKD.rows()
    SETS = PKD.active_sets()
    RIX = dict((r[0], r) for r in ROWS)

    def kc(cond, what):
        K.check(bool(cond), what)

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))

    def cfg(**kv):
        """apply rows (absent = the fresh default) + forget the bag table (it is cached for 60 s per config epoch)"""
        apply(**kv)
        Pool.TAB = None
    cfg()

    # ============================================================== A: GearPackId = tools/pack_drops.py
    ids = [str(x) for x in GPI.ID]
    eq(len(ids), len(ROWS), "A: GearPackId.ID holds every row of tools/pack_drops.py rows()")
    kc(ids == [r[0] for r in ROWS], "A: ... in the same order (first %s, last %s)" % (ids[:1], ids[-1:]))
    kc([int(x) for x in GPI.SET] == [r[1] for r in ROWS] and [int(x) for x in GPI.AT] == [r[3] for r in ROWS]
       and [int(x) for x in GPI.ZONE] == [r[5] for r in ROWS] and [int(x) for x in GPI.ROLE] == [r[6] for r in ROWS],
       "A: SET / AT / ZONE / ROLE = the table's set index, weight (0 weapon, 1 Heavy, 2 Light, 3 Cloth), zone, role (0 drop, 1 ut, 2 mythic)")
    tk = [str(x) for x in Pool.T_KEY]
    bad_ty = [r[0] for k_, r in enumerate(ROWS) if (int(GPI.TY[k_]) != -1 if r[2] == "armor" else (int(GPI.TY[k_]) < 0 or tk[int(GPI.TY[k_])] != r[2]))]
    kc(not bad_ty, "A: TY = -1 for armor (the live ArmorSlot decides), the bag type of the table's weapon kind: wrong %s" % bad_ty[:5])
    kc([str(x) for x in GPI.S_TIER] == [s["tier"] for s in SETS] and [str(x) for x in GPI.S_KEY] == [s["key"] for s in SETS]
       and [str(x) for x in GPI.S_NAME] == [s["name"] for s in SETS] and [str(x) for x in GPI.S_TAG] == [PKD.tag_of(s["tier"]) for s in SETS],
       "A: the set columns S_TIER / S_KEY / S_NAME / S_TAG = active_sets() (tags from tools/tier_tags.py)")
    eq((int(GPI.idx(ids[0])), int(GPI.idx(ids[-1])), int(GPI.idx("NoSuchPackId")), int(GPI.idx(None))), (0, len(ids) - 1, -1, -1),
       "A: idx of the first / last id, an unknown id, null")
    nm = ["RookChestBlack", "WardenChest", "GhostCalvaryHelm", "IronDragonChestplate", "Sword_Iron_Black", "LahatChereb"]
    eq([(int(GPI.ROLE[GPI.idx(i)]), int(GPI.ZONE[GPI.idx(i)]), int(GPI.AT[GPI.idx(i)])) for i in nm], [(RIX[i][6], RIX[i][5], RIX[i][3]) for i in nm],
       "A: ROLE / ZONE / AT of %s = the Python table" % nm)
    kc(bool(GPI.has("RookChestBlack")) and not bool(GPI.has("Armor_Iron_Chest")) and str(GPI.tier("RookChestBlack")) == "iron"
       and str(GPI.tag("RookChestBlack")) == "T3 Iron" and int(GPI.at("WardenChest")) == 2 and int(GPI.at("RookChestBlack")) == 1
       and int(GPI.at("Sword_Iron_Black")) == 0 and GPI.tier("Armor_Iron_Chest") is None,
       "A: has / tier / tag / at of named ids (RookChestBlack iron 'T3 Iron' Heavy, WardenChest Light, a weapon 0, a vanilla id none)")
    n0 = int(Pool.P_N0)
    kc(len(Pool.P_ID) == n0 + len(ids) and str(Pool.P_ID[n0]) == ids[0] and int(Pool.idIdx(ids[0])) == n0 and int(Pool.P_ROLE[n0]) == ROWS[0][6]
       and int(Pool.P_SET[0]) == -1 and int(Pool.P_ZONE[0]) == 0,
       "A: GearPool rows = %d vanilla rows + the table (P_ID / idIdx / P_ROLE / P_SET / P_ZONE)" % n0)
    cfg(part__packDrops="false")
    kc(not bool(Cfg.PACK_ON) and not bool(GPI.has("RookChestBlack")) and int(GPI.idx("RookChestBlack")) >= 0 and GPI.tier("RookChestBlack") is None
       and GPI.tag("RookChestBlack") is None and int(GPI.at("WardenChest")) == 0,
       "A: part.packDrops=false: has / tier / tag / at off (the plain items of 0.3.18), idx still answers")
    cfg()
    rk = dict((k_, int(CRows.index(k_))) for k_ in ROWS319)
    kc(all(v_ >= 0 for v_ in rk.values()), "A: the 6 Server Setup rows exist: %s" % rk)
    if all(v_ >= 0 for v_ in rk.values()):
        dg = dict((k_, bool(CRows.flag(rk[k_], "danger"))) for k_ in ROWS319)
        lv = dict((k_, bool(CRows.flag(rk[k_], "live"))) for k_ in ROWS319)
        eq(dg, dict((k_, v_[5]) for k_, v_ in ROWS319.items()), "A: danger rows = part.packDrops + loot.boss.mythic (items / rarity = economy)")
        kc(all(lv.values()), "A: every row is live: %s" % lv)
    fr = dict((k_, None) for k_ in ROWS319)
    for ln_ in FRESH.replace("\r\n", "\n").split("\n"):
        if "=" in ln_ and ln_.split("=", 1)[0] in fr:
            fr[ln_.split("=", 1)[0]] = ln_.split("=", 1)[1]
    kc("# ---- pack armor + weapons as mob drops, Mythic boss bags (SkyyGear 0.3.19) ----" in FRESH
       and all(fr[k_] is not None and float(fr[k_] if fr[k_] not in ("true", "false") else int(fr[k_] == "true")) ==
               float(v_[1] if v_[1] not in ("true", "false") else int(v_[1] == "true")) for k_, v_ in ROWS319.items()),
       "A: a fresh config.properties lists the 0.3.19 block with the defaults: %s" % fr)
    eq((bool(Cfg.PACK_ON), float(Cfg.PACK_W), float(Cfg.BOSS_MY), int(Cfg.BOSS_CREDIT), int(Cfg.BOSS_LEAN), int(Cfg.BOSS_ARMOR)),
       (True, 1.0, 10.0, 15, 3, 50), "A: the field defaults (PACK_ON, PACK_W, BOSS_MY, BOSS_CREDIT, BOSS_LEAN, BOSS_ARMOR)")
    cfg(loot__packWeight="-2", loot__boss__mythic="250", loot__boss__credit="500", loot__boss__classLean="0", loot__boss__armorShare="101")
    eq((float(Cfg.PACK_W), float(Cfg.BOSS_MY), int(Cfg.BOSS_CREDIT), int(Cfg.BOSS_LEAN), int(Cfg.BOSS_ARMOR)), (0.0, 100.0, 100, 1, 100),
       "A: out-of-range values clamp to the row bounds")
    cfg()

    # ============================================================== B: the stand-in pack
    def item(i_):
        try:
            return ITEM.getAssetMap().getAsset(i_)
        except Exception:
            return None
    vids = sorted(str(x) for x in ITEM.getAssetMap().getAssetMap().keySet())

    def parent(cands, armor):
        for c_ in cands:
            got = [c_] if not c_.endswith("*") else [v_ for v_ in vids if v_.startswith(c_[:-1])]
            for g_ in got:
                it_ = item(g_)
                if it_ is None or int(it_.getMaxStack()) > 1:
                    continue
                if (it_.getArmor() is not None) == armor:
                    return g_
        return None
    for i_, sk_, ro_, _c in TEST_PACK + [NOT_LOADED + ([],)]:
        kc(i_ in RIX and SETS[RIX[i_][1]]["key"] == sk_ and PKD.ROLES[RIX[i_][6]] == ro_, "B setup: %s is a %s row of %s in tools/pack_drops.py" % (i_, ro_, sk_))
    par = dict((i_, parent(c_, RIX[i_][2] == "armor")) for i_, _s, _r, c_ in TEST_PACK)
    K.notes.append("H319 stand-in pack parents: %s" % par)
    pack = os.path.join(SCRATCH, "packs", "h319-armory-standin.zip")
    with zipfile.ZipFile(pack, "w") as z_:
        z_.writestr("manifest.json", json.dumps({"Group": "SkyWynnTest", "Name": "ArmoryStandIn", "Version": "0.0.1",
                                                 "Description": "SkyyGear 0.3.19 harness stand-in: table ids with a vanilla Parent only"}))
        for i_, p_ in par.items():
            if p_ is not None:
                z_.writestr("Server/Item/Items/%s.json" % i_, json.dumps({"Parent": p_}))
    fail_, rec_ = L["addpack"](pack, "SkyWynnTest:ArmoryStandIn")
    miss = [i_ for i_, p_ in par.items() if p_ is None or item(i_) is None]
    loaded = not fail_ and not miss
    sev = [str(r_[1])[:200] for r_ in rec_ if str(r_[0]) in ("SEVERE", "WARNING")]
    kc(loaded, "B: the engine loads the stand-in pack (failed stores %s, ids missing %s, log %s)" % (list(fail_), miss, sev[:3]))
    if not loaded:
        K.notes.append("H319: the stand-in pack was refused - B / C / D / E / F skipped")
        return
    Pool.TAB = None
    RC, RA, RH, ID, WC, GH, SW, LC, DR = (x[0] for x in TEST_PACK)
    CB = NOT_LOADED[0]
    TY_CHEST, TY_HEAD = tk.index("Armor_Chest"), tk.index("Armor_Head")
    kc(bool(Data.isGear(RC)) and str(Data.kindFor(RC)) == "combat" and int(Data.slotOf(RC)) == 2 and int(Data.slotOf(SW)) == 0,
       "B: RookChestBlack = gear, kind combat, slot 2 (armor); Sword_Iron_Black slot 0")
    MAT, MATCAP = Cfg.MAT, Cfg.MATCAP
    mn = int(Lvl.clamp(JInt(int(MAT.get("iron")))))
    cp_ = MATCAP.get("iron")
    cp_ = int(Lvl.clamp(JInt(int(cp_)))) if cp_ is not None else int(Cfg.capOf(JInt(mn), Cfg.BAND_W))
    cp_ = max(cp_, mn)
    eq([int(x) for x in Lvl.band(RC)], [mn, cp_, 1], "B: band(RookChestBlack) = the Iron level.material row (min, cap, by material)")
    kc(str(Lvl.entry(RC)) == "iron" and int(Lvl.level(RC, None)) == mn, "B: entry / level of RookChestBlack = the iron row")
    eq((int(Smith.armorType(WC)), int(Smith.armorType(RC))), (2, 1), "B: GearSmith.armorType = the table weight (Warden Light 2, Rook Heavy 1)")
    t = Pool.table()
    ok_, lt_ = list(t[2]), list(t[7])
    ix = lambda i_: int(Pool.idIdx(i_))
    eq((int(Pool.typeOfId(CB)), bool(ok_[ix(CB)])), (-1, False), "B: a table id not installed (CalvaryChestBlack) = no type, never a candidate")
    kc(ok_[ix(RC)] and int(lt_[ix(RC)]) == TY_CHEST and int(Pool.typeOfId(RC)) == TY_CHEST and int(lt_[ix(RH)]) == TY_HEAD
       and int(lt_[ix(SW)]) == tk.index("Weapon_Sword"),
       "B: live types: Rook chest = Armor_Chest (its ArmorSlot), Rook helm = Armor_Head, the sword = Weapon_Sword (the table)")
    pw = float(Cfg.PACK_W)
    w_ = lambda i_: float(Pool.w(t, JInt(ix(i_))))
    kc(abs(w_(RC) - pw * 0.5) < 1e-9 and abs(w_(RA) - pw * 0.5) < 1e-9 and abs(w_(RH) - pw * 1.0) < 1e-9,
       "B: picked by set: the two Rook chests weigh %s each (0.5 x loot.packWeight), the one Rook helm %s (1.0)" % (w_(RC), w_(RH)))
    kc(ok_[ix(ID)] and not ok_[ix(GH)] and not any(bool(Pool.match(t, JInt(ix(ID)), JInt(TY_CHEST), JInt(a_), JInt(L_))) for a_ in (0, 1) for L_ in (-1, mn, cp_)),
       "B: IronDragonChestplate (Mythic) is live but never matched by the normal pool; GhostCalvaryHelm (ut) never ok")
    Lb = mn if mn >= 1 else 1
    sv, sp = 0.0, 0.0
    for i_ in range(len(Pool.P_ID)):
        if bool(Pool.match(t, JInt(i_), JInt(TY_CHEST), JInt(1), JInt(Lb))):
            if i_ >= n0:
                sp += float(Pool.w(t, JInt(i_)))
            else:
                sv += float(Pool.w(t, JInt(i_)))
    exp = sp / (sp + sv) if sp + sv > 0 else 0.0
    N = 2000
    got = [str(Pool.pickItem(JInt(TY_CHEST), JInt(1), JInt(Lb))) for _ in range(N)]
    fr_ = sum(1 for g_ in got if g_ in (RC, RA)) / float(N)
    K.notes.append("B pickItem(Armor_Chest, Heavy, Lv %d): pack share %.3f (computed %.3f: pack %.2f vs vanilla %.2f), %s" % (Lb, fr_, exp, sp, sv, sorted(set(got))[:8]))
    kc(abs(fr_ - exp) < 5 * (max(exp * (1 - exp), 0.0025) / N) ** 0.5 + 0.02 and not set(got) & {ID, WC, GH, CB, "None"},
       "B: pickItem over %d draws: the Rook chests %.3f vs the computed set share %.3f; never a Mythic / ut / missing id" % (N, fr_, exp))
    cfg(loot__packWeight="2")
    t2 = Pool.table()
    kc(abs(float(Pool.w(t2, JInt(ix(RC)))) - 1.0) < 1e-9, "B: loot.packWeight 2 doubles a pack row's weight (%s)" % float(Pool.w(t2, JInt(ix(RC)))))
    cfg(part__packDrops="false")
    t3 = Pool.table()
    b3 = [int(x) for x in Lvl.band(RC)]
    kc(not any(bool(t3[2][i_]) for i_ in range(n0, len(Pool.P_ID))) and not bool(Data.isGear(RC)) and Lvl.entry(RC) is None and b3[2] != 1
       and int(Pool.candidates(JInt(TY_CHEST), JInt(1), JInt(Lb))) == sum(1 for i_ in range(n0) if bool(Pool.match(t3, JInt(i_), JInt(TY_CHEST), JInt(1), JInt(Lb)))),
       "B: part.packDrops=false: no pack row ok, RookChestBlack not gear, its band back to the id-word rule (%s)" % b3)
    cfg()

    # ============================================================== C: Mythic bags
    t = Pool.table()
    rg = Pool.rangeM(JInt(TY_CHEST), JInt(1), JInt(1))
    top = int(Cfg.LOOT_TOP)
    eq(None if rg is None else [int(x) for x in rg], [max(1, mn), min(cp_, top)], "C: rangeM(Armor_Chest, Heavy, zone 1) = the Iron band (trimmed to loot.levelTop)")
    eq((int(Pool.candM(JInt(TY_CHEST), JInt(1), JInt(2))), int(Pool.candM(JInt(TY_CHEST), JInt(0), JInt(2))), int(Pool.candM(JInt(TY_CHEST), JInt(0), JInt(1)))),
       (0, 0, 2), "C: candM: zone 2 none loaded; zone 1 chests = Iron Dragon + Warden")
    bn5 = int(Pool.BN[5])
    seen, bad, opened = set(), [], 0
    for _ in range(40):
        bag = Pack.mythicBag(JInt(1), None)
        if bag is None:
            bad.append("null bag")
            continue
        d_ = Unid.doc(bag)
        at_ = str(Data.str(d_, "at", "-"))
        if str(bag.getItemId()) != "Skyy_Unid_Bag_Mythic" or int(Unid.pz(d_)) != 1 or str(Data.str(d_, "r", "?")) != "mythic" \
                or int(Unid.type(d_)) != TY_CHEST or at_ not in ("Heavy", "Light") or Unid.why(d_) is not None:
            bad.append("bag %s %s" % (bag.getItemId(), d_.toJson()[:160]))
            continue
        o_ = Unid.open(d_, U1)
        opened += 1
        want = ID if at_ == "Heavy" else WC
        bx = Unid.boxOf(o_[2]) if o_ is not None else None
        if o_ is None or str(o_[0]) != want or int(Data.rarity(o_[2])) != int(Defs.R_MY) or bx is None or int(Unid.pz(bx)) != 1:
            bad.append("open %s -> %s" % (at_, None if o_ is None else (str(o_[0]), str(o_[2].toJson())[:160])))
            continue
        seen.add(at_)
    kc(not bad and seen == {"Heavy", "Light"},
       "C: mythicBag(1) = a Skyy_Unid_Bag_Mythic (pz 1, r mythic, Armor_Chest, why null) that opens into Iron Dragon (Heavy) / Warden (Light), "
       "Mythic, box.pz 1: seen %s, problems %s" % (sorted(seen), bad[:3]))
    eq(int(Pool.BN[5]) - bn5, opened, "C: every open from a zone's Mythic sets is counted (BN[5])")
    bag = Pack.mythicBag(JInt(1), None)
    if bag is not None:
        d_ = Unid.doc(bag)
        tip = str(d_.toJson())
        ms_ = Unid.descMsg(d_)

        def flat_txt(m_):
            o_ = []

            def walk(fm):
                if fm.rawText is not None:
                    o_.append(str(fm.rawText))
                if fm.children is not None:
                    for ch in fm.children:
                        walk(ch)
            walk(m_.getFormattedMessage())
            return "".join(o_)
        kc("Boss drop: one of Zone 1's Mythic armor pieces." in flat_txt(ms_), "C: the boss bag's tooltip names its zone: %s" % flat_txt(ms_)[:200])
        o_ = Unid.open(d_, U1)
        kc(o_ is not None and Unid.rerollWhy(o_[2]) is None, "C: a boss item may be re-identified (rerollWhy null: its zone's Mythic pieces)")
        r_ = Unid.reroll(o_[2], U1) if o_ is not None else None
        kc(r_ is not None and str(r_[0]) in (ID, WC) and int(Unid.pz(Unid.boxOf(r_[2]))) == 1 and int(Unid.rerolls(Unid.boxOf(r_[2]))) == 1,
           "C: re-identify keeps the zone (a zone-1 Mythic piece again, box.pz 1, n 1): %s" % (None if r_ is None else str(r_[0])))
        cfg(part__packDrops="false")          # the zone's Mythic pieces gone (their mod off): the item cannot be re-identified, the bag waits
        rw0 = Unid.rerollWhy(o_[2]) if o_ is not None else None
        kc(rw0 is not None and str(rw0).startswith("No Zone 1 Mythic ") and str(rw0).endswith(" exists here any more.")
           and Unid.reroll(o_[2], U1) is None and str(Unid.why(d_)).startswith("This Zone 1 Mythic bag waits for its Mythic pieces")
           and Unid.open(d_, U1) is None,
           "C: no Mythic piece of the zone left: rerollWhy / why refuse (zone words), reroll / open = null, never a normal-pool item (review M5): %s" % rw0)
        cfg()
    zb = lambda ty_, at_, z_: Unid.doc(Unid.makeZ(JInt(ty_), JInt(at_), JInt(int(Defs.R_MY)), JInt(max(1, mn)), JInt(min(cp_, top)), "test", "h319", JInt(0), JInt(z_)))
    dH = zb(TY_HEAD, 1, 1)
    dC = zb(TY_CHEST, 3, 1)
    d3 = zb(TY_CHEST, 1, 3)
    oC = Unid.open(dC, U1)
    kc(str(Unid.why(dH)).startswith("This Zone 1 Mythic bag waits") and Unid.open(dH, U1) is None
       and str(Unid.why(d3)).startswith("This Zone 3 Mythic bag waits") and Unid.open(d3, U1) is None
       and Unid.why(dC) is None and oC is not None and str(oC[0]) in (ID, WC) and int(Data.rarity(oC[2])) == int(Defs.R_MY),
       "C: a zone-1 Heavy HEAD bag / a zone-3 bag (no Mythic piece loaded) wait (why, open null); a zone-1 Cloth chest bag opens into a "
       "zone-1 Mythic chest of another weight: %s" % (None if oC is None else str(oC[0])))
    cfg(loot__packWeight="0")
    t0 = Pool.table()
    kc(int(Pool.candM(JInt(TY_CHEST), JInt(0), JInt(1))) == 2 and Pack.mythicBag(JInt(1), None) is not None
       and not any(bool(Pool.match(t0, JInt(i_), JInt(TY_CHEST), JInt(1), JInt(Lb))) for i_ in range(n0, len(Pool.P_ID))),
       "C: loot.packWeight 0 takes the pack out of normal bags but never out of the Mythic boss picks (set share only, review M5)")
    cfg()
    ob = Unid.make(JInt(TY_CHEST), JInt(1), JInt(2), JInt(10), JInt(14), "test", "h319", JInt(0))
    ok0 = Unid.makeZ(JInt(TY_CHEST), JInt(1), JInt(2), JInt(10), JInt(14), "test", "h319", JInt(0), JInt(0))
    kz = [str(x) for x in Unid.doc(ob).keySet()]
    eq(kz, ["v", "mys", "r", "lo", "hi", "at", "src", "ls", "tier", "t", "n", "id"], "C: an ordinary bag has the 0.3.18 fields only (no pz)")
    kc(int(Unid.pz(Unid.doc(ob))) == 0 and [str(x) for x in Unid.doc(ok0).keySet()] == kz, "C: make() = makeZ(..., pz 0): no pz key")
    eq(Pack.mythicBag(JInt(3), None), None, "C: mythicBag(3) = null (no zone-3 Mythic loaded)")
    eq(Pack.mythicBag(JInt(0), None), None, "C: mythicBag(0) = null")
    tyM, tyD = tk.index("Weapon_Mace"), tk.index("Weapon_Daggers")
    if int(Pool.candM(JInt(tyM), JInt(0), JInt(4))) > 0 and int(Pool.candM(JInt(tyD), JInt(0), JInt(4))) > 0:
        lean = JArray(JString)(["Weapon_Mace"])
        M_ = 3000
        a_ = [int(Pool.pickTypeM(False, JInt(4), lean, JInt(3))) for _ in range(M_)]
        b_ = [int(Pool.pickTypeM(False, JInt(4), None, JInt(3))) for _ in range(M_)]
        fa, fb = a_.count(tyM) / float(M_), b_.count(tyM) / float(M_)
        kc(set(a_) | set(b_) <= {tyM, tyD} and abs(fa - 0.75) < 0.05 and abs(fb - 0.5) < 0.05,
           "C: pickTypeM zone 4 (Lahat Chereb mace + Dual Rune Blade daggers): own-class Mace x3 = %.3f (0.75), no lean = %.3f (0.5)" % (fa, fb))
        kc(Pool.pickArmM(JInt(4)) is None, "C: pickArmM zone 4 = null (no zone-4 Mythic armor loaded)")
    else:
        K.notes.append("C: the lean test skipped - the zone-4 Mythic mace / daggers are not candidates (band above loot.levelTop %d?)" % top)

    # ============================================================== D: the tooltip's tier tag
    def msglines(m_):
        segs = []

        def walk(fm, col, it):
            c_ = str(fm.color) if fm.color is not None else col
            i2 = bool(fm.italic) if fm.italic is not None else it
            if fm.rawText is not None:
                segs.append((str(fm.rawText), c_, i2))
            elif fm.messageId is not None:
                segs.append(("<desc:%s>" % fm.messageId, c_, i2))
            if fm.children is not None:
                for ch in fm.children:
                    walk(ch, c_, i2)
        walk(m_.getFormattedMessage(), None, False)
        out_, cur = [], []
        for tx, c_, i2 in segs:
            for k_, p_ in enumerate(tx.split("\n")):
                if k_ > 0:
                    out_.append(cur)
                    cur = []
                if p_:
                    cur.append((p_, c_, i2))
        out_.append(cur)
        return [("".join(x[0] for x in s_), s_[0][1] if s_ else None, any(x[2] for x in s_)) for s_ in out_]

    def tooltip(i_, d_):
        tx, co = AL(), AL()
        View.lines(i_, d_, U1, tx, co)
        return [str(x) for x in tx], msglines(View.descMsg(i_, d_, tx, co))
    tag = PKD.tag_of("iron")
    dR = Roll.newDoc(RC, JInt(0), True, "test", JInt(mn))
    tx, ml = tooltip(RC, dR)
    fl = [m_ for m_ in ml if m_[0].startswith(tag)]
    kc(str(View.FLAVOR) in tx and len(fl) == 1 and str(fl[0][1]).lower() == str(Defs.C_GRAY).lower() and fl[0][2],
       "D: a documented RookChestBlack: the flavour slot starts with %r (grey italic, tools/tier_tags.py): %s" % (tag, fl))
    cfg(part__packDrops="false")
    try:
        tx0, ml0 = tooltip(RC, dR)          # the game never renders a non-gear id; the answer only must not carry the tag
        kc(GPI.tag(RC) is None and not [m_ for m_ in ml0 if m_[0].startswith(tag)], "D: part.packDrops=false: no tier tag")
    except Exception as e_:
        kc(GPI.tag(RC) is None, "D: part.packDrops=false: no tier tag (GearView.lines refused the non-gear id: %s)" % str(e_)[:120])
    cfg()

    # ============================================================== X: the critic fixes on the stand-ins (local rebuild)
    ISj = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    kc(bool(GPI.special(ID)) and bool(GPI.special(GH)) and not bool(GPI.special(RC)) and not bool(GPI.special("Armor_Iron_Chest")),
       "X1: special = a UT / Mythic table row (IronDragonChestplate, GhostCalvaryHelm), not a drop row / a vanilla id")
    dm = Roll.unidDoc(ID, JInt(1), "drop")
    dd = Roll.unidDoc(RC, JInt(1), "drop")
    kc(int(Data.rarity(dm)) == 0 and bool(Data.identified(dm)) and not bool(Data.identified(dd)),
       "X1: a Mythic-row piece their mobs / chests drop = an identified plain Normal piece; a drop row stays an unidentified roll")
    kc(Unid.fromItem(ISj(ID, JInt(1)), JInt(1), JInt(10), "mob") is None and Unid.fromItem(ISj(GH, JInt(1)), JInt(2), JInt(10), "chest") is None
       and Unid.fromItem(ISj(RC, JInt(1)), JInt(1), JInt(10), "mob") is not None,
       "X1: no mystery bag of a UT / Mythic row (a drop row still becomes one)")
    kc(bool(GPI.plainCraft(ID, None)) and bool(GPI.plainCraft(GH, None)) and not bool(GPI.plainCraft(RC, None)) and not bool(GPI.plainCraft(RC, "NoSuchRecipe")),
       "X2: plainCraft: a UT / Mythic row always plain, a drop row only for a swap recipe")
    cs_ = P("SmithFn")(JInt(1))
    kc(cs_.apply(JArray(JObject)([U1, JString(ID)])) == False and cs_.apply(JArray(JObject)([U1, JString(RC)])) is not None,
       "X2: gear:fn:classShow answers false for a Mythic row")
    kc(GPI.resSets(None) is None and not bool(GPI.carries(RC, "NoSuchResource")) and not bool(GPI.carries(None, "x")),
       "X3: resSets / carries answer safely for unknown resources")
    def md_(i_, sr_):
        return Data.put(ISj(i_, JInt(1)), Roll.newDoc(i_, JInt(0), True, sr_), None).getMetadata()
    sb_ = [bool(Pack.salvBlocked(RC, md_(RC, sr_))) for sr_ in ("drop", "chest", "boss", "craft")]
    kc(sb_ == [True, True, True, False] and not bool(Pack.salvBlocked(RC, None)) and not bool(Pack.salvBlocked("Armor_Iron_Chest", md_("Armor_Iron_Chest", "drop")))
       and not bool(GPI.salvage(None)) and Pack.salvVeto(None, None) is None,
       "X8: salvBlocked = a pack piece with a drop / chest / boss document (a crafted one, an undocumented one, a vanilla id: no): %s" % sb_)
    cfg()
    k_ = int(GPI.idx(RC))
    g0 = bool(Data.isGear(RC))
    kc(g0 and int(GPI.gc(k_)) == 1, "X6: isGear caches the pack answer per row (GC = 1 after the first ask)")
    cfg(part__packDrops="false")
    kc(not bool(Data.isGear(RC)), "X6: part.packDrops off = not gear at once (has() is asked before the cache)")
    cfg()
    kc(bool(Data.isGear(RC)) and int(GPI.gc(k_)) == 1, "X6: back on = gear again, cached under the new epoch")

    # ============================================================== E: /gear loot lines
    t = Pool.table()
    live = sum(1 for i_ in range(n0, len(Pool.P_ID)) if bool(t[2][i_]) and int(Pool.P_ROLE[i_]) == 0)
    myth = sum(1 for i_ in range(n0, len(Pool.P_ID)) if bool(t[2][i_]) and int(Pool.P_ROLE[i_]) == 2)
    utn = sum(1 for r in ROWS if r[6] == 1)
    miss_n = sum(1 for i_ in range(n0, len(Pool.P_ID)) if int(Pool.P_ROLE[i_]) != 1 and int(t[7][i_]) < 0)
    pt = str(Pool.packText())
    bn = [int(x) for x in Pool.BN]
    K.notes.append("E packText: %s" % pt)
    kc(pt.startswith("pack drops on: %d normal + %d Mythic pieces live of %d table ids (%d not installed / no slot, %d Untiered candidates"
                     % (live, myth, len(ROWS), miss_n, utn))
       and ("boss kills %d, rolls %d, bags %d, nothing fit %d, zone unknown %d, same fight %d, opened from Mythic sets %d"
            % (bn[0], bn[1], bn[2], bn[3], bn[4], bn[6], bn[5])) in pt and len(bn) == 7,
       "E: packText = the live / Mythic / missing / ut counts (%d / %d / %d / %d) and the counters %s: %s" % (live, myth, miss_n, utn, bn, pt[:220]))
    kc(pt in str(Loot.countsText()), "E: /gear loot (GearLoot.countsText) carries the pack line")
    cfg(part__packDrops="false")
    kc(str(Pool.packText()).startswith("pack drops OFF: 0 normal + 0 Mythic"), "E: off = 'pack drops OFF', nothing live: %s" % str(Pool.packText())[:80])
    cfg()

    # ============================================================== F: the REAL bossRoll on stand-ins
    UUIDJ = JClass("java.util.UUID")
    UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    HRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    R3F = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    UNIc = JClass("com.hypixel.hytale.server.core.universe.Universe")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    V3 = JClass("org.joml.Vector3d")
    IHM, HM, CHM = JClass("java.util.IdentityHashMap"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap")
    Integer = JClass("java.lang.Integer")
    FS, FBuf, FCh = JClass(FAKE_PKG + ".FakeStore"), JClass(FAKE_PKG + ".FakeBuffer"), JClass(FAKE_PKG + ".FakeChunk")
    fst = us.allocateInstance(FS.class_)
    fst.comps = HM()
    buf = us.allocateInstance(FBuf.class_)
    buf.st = fst

    def ref(i_, pr_, gm_):
        r_ = us.allocateInstance(REFc.class_)
        jf(REFc, "index").setInt(r_, JInt(i_))
        jf(REFc, "store").set(r_, fst)
        m_ = IHM()
        pl_ = us.allocateInstance(PLA.class_)
        jf(PLA, "gameMode").set(pl_, gm_)
        m_.put(PLA.getComponentType(), pl_)
        m_.put(PRc.getComponentType(), pr_)
        fst.comps.put(r_, m_)
        jf(PRc, "entity").set(pr_, r_)
        return r_, pl_
    old_ent = (jf(PRc, "entity").get(PR1), jf(PRc, "entity").get(PR2))
    r1, pl1 = ref(41, PR1, GM.Adventure)
    r2, pl2 = ref(42, PR2, GM.Adventure)
    uni = UNIc.get()
    pbu = jf(UNIc, "playersByUuid").get(uni)
    if pbu is None:
        pbu = CHM()
        jf(UNIc, "playersByUuid").set(uni, pbu)
    pbu.put(U1, PR1)
    pbu.put(U2, PR2)

    def mkchunk(npc_u):
        ch_ = us.allocateInstance(FCh.class_)
        m_ = IHM()
        u_ = us.allocateInstance(UUIDC.class_)
        jf(UUIDC, "uuid").set(u_, npc_u)
        m_.put(UUIDC.getComponentType(), u_)
        h_ = us.allocateInstance(HRC.class_)
        jf(HRC, "rotation").set(h_, R3F())
        m_.put(HRC.getComponentType(), h_)
        ch_.comps = m_
        return ch_

    def death(kr):
        o_ = us.allocateInstance(DTH.class_)
        d_ = us.allocateInstance(DMG.class_)
        jf(DMG, "source").set(d_, DENT(kr))
        jf(DTH, "deathInfo").set(o_, d_)
        return o_

    def npc(role):
        n_ = us.allocateInstance(NPCE.class_)
        jf(NPCE, "roleName").set(n_, JString(role))
        return n_
    BOSS = {"zone": 1, "who": [(str(U1), 0.9), (str(U2), 0.1)], "calls": []}

    @JImplements("java.util.function.Function")
    class BossFn(object):
        @JOverride
        def apply(self, o):
            BOSS["calls"].append((str(o[0]), str(o[1]), str(o[2]), float(o[3]), float(o[4]), float(o[5])))
            if not str(o[2]).startswith("Test_Boss"):
                return None
            a_ = JArray(JObject)(4)
            a_[0] = JObject(JInt(BOSS["zone"]), Integer)
            a_[1] = JString(str(o[2]))
            a_[2] = JArray(JString)([w_[0] for w_ in BOSS["who"]])
            a_[3] = JArray(JDouble)([w_[1] for w_ in BOSS["who"]])
            return a_
    SP = []

    @JImplements("java.util.function.BiFunction")
    class Spawn(object):
        @JOverride
        def apply(self, b_, at_):
            SP.append((str(b_.getItemId()), Unid.doc(b_), float(at_.x()), float(at_.y()), float(at_.z())))
            return None
    old_fn, old_sp = br.get("mob:fn:boss"), Loot.SPAWN
    br.put("mob:fn:boss", BossFn())
    Loot.SPAWN = Spawn()
    Loot.ROLLED.clear()
    pos = V3(JDouble(5.0), JDouble(70.0), JDouble(5.0))

    def fcfg(**kv):
        """cfg() with the hourly extra-bag cap out of the way (review M3: boss bags count against loot.mob.capPerHour, default 20)"""
        kv.setdefault("loot__mob__capPerHour", "1000")
        cfg(**kv)
        Loot.HOUR.clear()

    def roll(role="Test_Boss_Duke", u_=None, dc_=None, fresh=True):
        u_ = u_ or UUIDJ.randomUUID()
        if fresh:
            Pack.FIGHT.clear()          # critic fix 4: every stand-in death is its own fight unless a test says otherwise
        del SP[:]
        n_ = int(Pack.bossRoll(mkchunk(u_), JInt(0), fst, buf, dc_, npc(role), pos, "w"))
        return n_, list(SP), u_
    try:
        fcfg(loot__boss__mythic="100")
        # F0: the REAL GearDeathMark.tick (the 0.2.11 X10 rig: a boss NPC whose items drop now, a world name on the store) -> bossRoll
        try:
            TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
            ILM = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig$ItemsLossMode")
            ROLE = JClass("com.hypixel.hytale.server.npc.role.Role")
            ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
            WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
            JClass(FAKE_PKG + ".FakeUtil").mapType("com.hypixel.hytale.server.core.modules.entity.EntityModule", "classToComponentType",
                                                   "com.hypixel.hytale.server.npc.entities.NPCEntity")
            nu0 = UUIDJ.randomUUID()
            ch0 = mkchunk(nu0)
            np0 = npc("Test_Boss_Tick")
            rl0 = us.allocateInstance(ROLE.class_)
            jf(ROLE, "dropDeathItemsInstantly").setBoolean(rl0, True)
            jf(NPCE, "role").set(np0, rl0)
            tc0 = us.allocateInstance(TC.class_)
            jf(TC, "position").set(tc0, V3(JDouble(5.0), JDouble(70.0), JDouble(5.0)))
            dc0 = death(r1)
            jf(DTH, "itemsLossMode").set(dc0, ILM.ALL)
            ch0.comps.put(DTH.getComponentType(), dc0)
            ch0.comps.put(NPCE.getComponentType(), np0)
            ch0.comps.put(TC.getComponentType(), tc0)
            wld = us.allocateInstance(WLD.class_)
            jf(WLD, "name").set(wld, "testworld")
            es0 = us.allocateInstance(ES.class_)
            jf(ES, "world").set(es0, wld)
            old_ext = fst.ext
            fst.ext = es0
            del SP[:]
            P("GearDeathMark")(False).tick(JFloat(0.05), JInt(0), ch0, fst, buf)
            fst.ext = old_ext
            my0 = [x for x in SP if x[0] == "Skyy_Unid_Bag_Mythic"]
            kc(len(my0) == 1 and int(Unid.pz(my0[0][1])) == 1 and BOSS["calls"] and BOSS["calls"][-1] == ("testworld", str(nu0), "Test_Boss_Tick", 5.0, 70.0, 5.0),
               "F0: the REAL GearDeathMark.tick on a dying boss calls GearPack.bossRoll: one Mythic bag (pz 1), mob:fn:boss asked with the world "
               "name, the NPC uuid, its role, its position: %s %s" % ([x[0] for x in SP], BOSS["calls"][-1:]))
        except Exception:
            import traceback
            kc(False, "F0: the GearDeathMark.tick stand-in run raised: %s" % traceback.format_exc()[-900:])
        logs()
        bn0 = [int(x) for x in Pool.BN]
        n1, s1, u1 = roll()
        bn1 = [int(x) for x in Pool.BN]
        lg = [x for x in logs() if "LOOT boss Test_Boss_Duke zone 1" in x]
        kc(n1 == 1 and len(s1) == 1 and s1[0][0] == "Skyy_Unid_Bag_Mythic" and int(Unid.pz(s1[0][1])) == 1 and abs(s1[0][3] - 71.0) < 1e-9
           and BOSS["calls"][-1] == ("w", str(u1), "Test_Boss_Duke", 5.0, 70.0, 5.0)
           and [b - a for a, b in zip(bn0, bn1)] == [1, 1, 1, 0, 0, 0, 0] and lg and "Tester=" in lg[-1] and "(test seam)" in lg[-1] and "Other=" not in lg[-1],
           "F: a zone-1 boss at 100 %%: ONE Mythic bag (pz 1) for the 90 %% player, none for the 10 %% one (credit 15 %%), 1 block up, mob:fn:boss "
           "asked (world, npc, role, x, y, z), counters kills / rolls / bags +1, a LOOT boss log line: %s %s %s" % (n1, [x[0] for x in s1], lg[-1:]))
        n2, s2, _u = roll(u_=u1)
        kc(n2 == 0 and not s2 and [int(x) for x in Pool.BN] == bn1, "F: the same death twice = nothing more (once per death)")
        BOSS["who"] = [(str(U1), 0.5), (str(U2), 0.5)]
        n3, s3, _u = roll()
        kc(n3 == 2 and len(s3) == 2, "F: two players at 50 %% each = two bags (%d)" % n3)
        n4, s4, _u = roll(role="Trork_Grunt")
        kc(n4 == 0 and not s4, "F: mob:fn:boss null (not a boss) = nothing")
        BOSS["zone"] = 0
        bz = int(Pool.BN[4])
        n5, s5, _u = roll()
        kc(n5 == 0 and int(Pool.BN[4]) == bz + 1, "F: zone 0 (unknown) = nothing, counted (zone unknown)")
        BOSS["zone"] = 3
        b3n = int(Pool.BN[3])
        n6, s6, _u = roll()
        kc(n6 == 0 and int(Pool.BN[3]) == b3n + 2, "F: zone 3 (no Mythic piece loaded) = nothing, counted per roller (nothing fit)")
        BOSS["zone"] = 1
        BOSS["who"] = []
        logs()
        n7, s7, _u = roll(dc_=death(r1))
        lg7 = [x for x in logs() if "SkyyMobs credited nobody, the killer rolls" in x]
        kc(n7 == 1 and len(s7) == 1 and lg7, "F: SkyyMobs credited nobody = the killer (a player) rolls, logged: %d %s" % (n7, lg7[-1:]))
        BOSS["who"] = [(str(U1), 0.10), (str(U2), 0.10)]
        br1 = int(Pool.BN[1])
        n7b, s7b, _u = roll(dc_=death(r1))
        kc(n7b == 0 and not s7b and int(Pool.BN[1]) == br1,
           "F: credited players all under loot.boss.credit = nobody rolls, never the killer (review M4)")
        BOSS["who"] = [(str(U1), 1.0)]
        jf(PLA, "gameMode").set(pl1, GM.Creative)
        n8, s8, _u = roll()
        jf(PLA, "gameMode").set(pl1, GM.Adventure)
        kc(n8 == 0, "F: a Creative player never rolls")
        fcfg(loot__boss__mythic="100", loot__mob__capPerHour="2")
        cap3 = [roll()[0] for _ in range(3)]
        kc(cap3 == [1, 1, 1], "F: boss bags are not under the hourly cap (loot.mob.capPerHour 2, three fights = three bags; critic 5): %s" % cap3)
        fcfg(loot__boss__mythic="100")
        b6 = int(Pool.BN[6])
        Pack.FIGHT.clear()
        ph = [roll(role=r_, fresh=False)[0] for r_ in ("Test_Boss_Duke", "Test_Boss_Duke_Phase_2", "Test_Boss_Duke_Phase_3_Fast", "Test_Boss_Other")]
        kc(ph == [1, 0, 0, 1] and int(Pool.BN[6]) == b6 + 2 and str(Pack.family("Goblin_Duke_Phase_3_Slow")) == "Goblin_Duke"
           and str(Pack.family("Skeleton_Elite_Phase_2")) == "Skeleton_Elite" and str(Pack.family("Trork_Chieftain")) == "Trork_Chieftain",
           "F: one roll per boss family per fight (critic 4): phase 1 rolls, its Phase_2 / Phase_3 deaths within 120 s do not (BN[6] +2), another "
           "boss does: %s" % ph)
        nc = len(BOSS["calls"])
        fcfg(loot__boss__mythic="0")
        n9, _s, _u = roll()
        fcfg(loot__boss__mythic="100", part__packDrops="false")
        n10, _s, _u = roll()
        fcfg(loot__boss__mythic="100")
        br.remove("mob:fn:boss")
        n11, _s, _u = roll()
        br.put("mob:fn:boss", BossFn())
        kc(n9 == 0 and n10 == 0 and n11 == 0 and len(BOSS["calls"]) == nc,
           "F: loot.boss.mythic 0 / part.packDrops off / no SkyyMobs (no mob:fn:boss) = nothing, the bridge never asked")
        fcfg()          # loot.boss.mythic 10 (the default), the cap out of the way
        hits = 0
        for _ in range(600):
            hits += roll()[0]
        kc(30 <= hits <= 95, "F: loot.boss.mythic 10 %% over 600 deaths (one credited player): %d bags (~60)" % hits)
        # G: the delivery task itself (bossRoll hands it to world.execute; the seam above stands in for it): into the winner's inventory
        inv7, cs7 = L["mkinv"]()
        ref7, st7, _ch7, _pl7 = L["world"](inv7, cs7, PR1)
        jf(PRc, "entity").set(PR1, ref7)
        bag7 = Pack.mythicBag(JInt(1), None)
        logs()
        P("GearPackGive")(PR1, bag7, st7, pos, R3F(), JInt(1)).run()
        lg8 = [x for x in logs() if "LOOT boss-give Tester zone 1 Skyy_Unid_Bag_Mythic" in x]
        kc(L["ids"](cs7).get("Skyy_Unid_Bag_Mythic") == 1 and lg8 and lg8[-1].endswith("-> inventory")
           and any("Zone 1 Mythic bag for you - it is in your inventory" in x for x in L["said"](PR1)),
           "G: GearPackGive puts the won bag into the winner's inventory, logs 'LOOT boss-give ... -> inventory' and tells the player: %s %s"
           % (lg8[-1:], L["said"](PR1)[-1:]))
        # fix round 1: the winner's Ref lives in another store (changed worlds) -> never their inventory / feet (store None = no boss world here)
        P("GearPackGive")(PR1, Pack.mythicBag(JInt(1), None), None, pos, R3F(), JInt(1)).run()
        lg9 = [x for x in logs() if "LOOT boss-give Tester zone 1 Skyy_Unid_Bag_Mythic" in x]
        kc(L["ids"](cs7).get("Skyy_Unid_Bag_Mythic") == 1 and lg9 and lg9[-1].endswith("-> lost"),
           "G: a winner in another world (Ref store != the boss's) gets nothing in the inventory / at the feet: %s" % lg9[-1:])
    finally:
        Loot.SPAWN = old_sp
        if old_fn is None:
            br.remove("mob:fn:boss")
        else:
            br.put("mob:fn:boss", old_fn)
        pbu.remove(U1)
        pbu.remove(U2)
        jf(PRc, "entity").set(PR1, old_ent[0])
        jf(PRc, "entity").set(PR2, old_ent[1])
        Loot.ROLLED.clear()
        Loot.HOUR.clear()
        cfg()


# ====================================================================================================== STATIC (no jars)
def run_static():
    import difflib
    import pack_drops as PKD
    keep = "--keep" in sys.argv
    sdir = os.path.abspath(os.path.join(SCR_BASE, "static"))
    assert os.path.realpath(sdir).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep)
    shutil.rmtree(sdir, ignore_errors=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        # ---------------------------------------------------------------- T: the pack table
        pr = subprocess.run([sys.executable, os.path.join(TOOLS, "pack_drops.py")], cwd=ROOT, env=env, capture_output=True, text=True)
        check(pr.returncode == 0 and pr.stdout.strip().endswith("OK"), "T: python tools/pack_drops.py exits 0 and says OK (%s: %s)" % (pr.returncode, pr.stdout.strip()[-120:]))
        check(PKD.check() == [], "T: pack_drops.check() finds no problem: %s" % PKD.check()[:3])
        rows, sets = PKD.rows(), PKD.active_sets()
        ids = [r[0] for r in rows]
        check(len(set(ids)) == len(ids) and ids, "T: %d rows, every id once" % len(ids))
        check(ids == [i for s in sets for i in s["ids"]], "T: rows() = active_sets() ids in order")
        badf = [r for r in rows if sets[r[1]]["ids"].count(r[0]) != 1 or r[2] != sets[r[1]]["kind"]
                or r[3] != (0 if r[2] != "armor" else PKD.WEIGHTS.index(sets[r[1]]["weight"]) + 1) or r[4] != sets[r[1]]["tier"]
                or r[5] != PKD.zone_of(r[4]) or PKD.ROLES[r[6]] != sets[r[1]]["role"] or r[6] not in (0, 1, 2)]
        check(not badf, "T: every row's set / kind / weight / tier / zone / role = its set: %s" % badf[:3])
        tops = dict(PKD.ZONES)
        badz = [s["key"] for s in PKD.SETS if s["role"] in ("ut", "mythic") and s["tier"] != tops[PKD.zone_of(s["tier"])] and s["tier"] != "onyxium"]
        check(not badz, "T: every ut / Mythic set sits at its zone's top tier (Skyy 2026-10-17): %s" % badz)
        # ---------------------------------------------------------------- V: the Void Charms wording (patch item 9, local rebuild)
        gsrc = open(os.path.join(HERE, "build_skyygear_%s.py" % VERSION), encoding="utf8").read()
        vnew = ['accessory in your Void Charms - or craft it at a "', '"Identifying needs an Appraisal Tool, but Void Charms is not loaded."',
                '"Identifying needs an Appraisal Tool accessory in your Void Charms."', '" (Void Charms)"',
                '"Identify: needs an Appraisal Tool (Void Charms is not loaded)"']
        vold = [l for l in gsrc.splitlines() if "Accessory Bag" in l and '"' in l and not l.lstrip().startswith("#")
                and "Skyy_Accessory_Bag" not in l and "player-visible" not in l and "Old Accessory Bag" not in l]
        check(all(gsrc.count(v) == 1 for v in vnew) and not vold,
              "V: the player lines say Void Charms (5 lines), no quoted 'Accessory Bag' left: %s" % vold[:2])
        cell = {}
        for s in sets:
            if s["role"] == "mythic":
                cell.setdefault((PKD.zone_of(s["tier"]), s["weight"] if s["kind"] == "armor" else s["kind"]), []).append(s["key"])
        check(all(len(v) == 1 for v in cell.values()), "T: one Mythic set per zone x weight / weapon type: %s" % [v for v in cell.values() if len(v) > 1])
        check(all(";" not in i and "," not in i and all(32 < ord(c) < 127 for c in i) for i in ids), "T: no id holds ';' / ',' / a non-ASCII or space")
        cols = {"ID": ";".join(ids), "S_NAME": ";".join(s["name"] for s in sets), "S_KEY": ";".join(s["key"] for s in sets)}
        check(all(len(v.encode("utf-8")) < 65535 for v in cols.values()), "T: each packed column fits one JVM string constant: %s"
              % dict((k, len(v.encode("utf-8"))) for k, v in cols.items()))
        tags = dict((t, PKD.tag_of(t)) for t in PKD.TIER_WORD)
        check(tags["iron"] == "T3 Iron" and all(re.match(r"^T\d+ [A-Z][a-z]+$", v) for v in tags.values()), "T: the tier tags: %s" % tags)
        off_ids = set(i for s in PKD.SETS if PKD.SOURCES[s["src"]]["status"] != "on" or s["role"] == "off" for i in s["ids"])
        todo_ids = set(i for s in PKD.SETS if PKD.SOURCES[s["src"]]["status"] != "on" for i in s["ids"])
        check(not off_ids & set(ids), "T: no todo / needs-ids / off id is in rows() (what the jar gets): %s" % sorted(off_ids & set(ids))[:5])
        rix = dict((r[0], r) for r in rows)
        for i_, sk_, ro_, _c in TEST_PACK + [NOT_LOADED + ([],)]:
            check(i_ in rix and sets[rix[i_][1]]["key"] == sk_ and PKD.ROLES[rix[i_][6]] == ro_, "T: H319's %s is a %s row of %s" % (i_, ro_, sk_))
        zone4 = [r for r in rows if r[0] in ("LahatChereb", "DualRuneBlade")]
        check(len(zone4) == 2 and all(r[5] == 4 and r[6] == 2 for r in zone4) and len(set(r[2] for r in zone4)) == 2,
              "T: H319's lean test ids are two zone-4 Mythic weapons of two types: %s" % zone4)

        # ---------------------------------------------------------------- G: the patch, twice, into a scratch tree
        outs = []
        for run in (1, 2):
            tree = os.path.join(sdir, "tree%d" % run)
            for sub in ("tools", "SkyyGear"):
                os.makedirs(os.path.join(tree, sub), exist_ok=True)
            shutil.copyfile(PATCH, os.path.join(tree, "tools", os.path.basename(PATCH)))
            shutil.copyfile(os.path.join(TOOLS, "deploy_set.py"), os.path.join(tree, "tools", "deploy_set.py"))
            shutil.copyfile(GEN318, os.path.join(tree, "SkyyGear", os.path.basename(GEN318)))
            code = ("import sys\nsys.path.insert(0, sys.argv[2])\nimport pack_drops\np = sys.argv[1]\n"
                    "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n")
            pr = subprocess.run([sys.executable, "-c", code, os.path.join(tree, "tools", os.path.basename(PATCH)), TOOLS], cwd=tree, env=env,
                                capture_output=True, text=True)
            gen = os.path.join(tree, "SkyyGear", os.path.basename(GEN))
            check(pr.returncode == 0 and os.path.isfile(gen), "G: the patch run %d in the scratch tree (%s: %s)" % (run, pr.returncode, (pr.stdout + pr.stderr).strip()[-300:]))
            if run == 1:
                print("  patch:", pr.stdout.strip().replace("\n", " | ")[:300])
            outs.append(open(gen, "rb").read() if os.path.isfile(gen) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs = byte-identical scripts (%d bytes)" % len(outs[0]))
        if os.path.isfile(GEN):
            check(open(GEN, "rb").read() == outs[0], "G: SkyyGear/build_skyygear_0.3.19.py = the patch output (regenerate it after a patch edit)")
        else:
            print("  note: SkyyGear/build_skyygear_0.3.19.py is not in the repo now - compared the two scratch runs only")
        s = outs[0].decode("utf-8").replace("\r\n", "\n")
        s18 = open(GEN318, encoding="utf-8").read().replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.19.py", "exec")
            check(True, "G: the generated script compiles")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        check(not [i for i in todo_ids if i in s], "T: no todo / needs-ids id anywhere in the generated build script: %s" % [i for i in todo_ids if i in s][:5])

        # ---------------------------------------------------------------- A: anchors
        check(s.count('VERSION = "0.3.19"\n') == 1 and 'VERSION = "0.3.18"\n' not in s, "A: VERSION 0.3.19")
        for k, (ty, df, lo, hi, fld, dang) in ROWS319.items():
            m = re.search(r'\("%s", "[^"]*", "loot", "(\w+)", "([^"]*)", "([^"]*)", "([^"]*)", "[^"]*", "[^"]*", "([^"]*)",\s*"[^"]*"(?:\s*\+\s*\w+)?,'
                          r'\s*"field:GearCfg\.(\w+)"\)' % re.escape(k), s)
            check(m is not None and m.groups() == (ty, df, lo, hi, m.group(5), fld) and ("live" in m.group(5).split(","))
                  and (("danger" in m.group(5).split(",")) == dang),
                  "A: the Server Setup row %s = %s %s [%s..%s] -> GearCfg.%s, live%s: %s" % (k, ty, df, lo, hi, fld, ", danger" if dang else "",
                                                                                          m.groups() if m else None))
        fdef = {"PACK_ON": ("boolean", "true"), "PACK_W": ("double", "1.0"), "BOSS_MY": ("double", "10.0"), "BOSS_CREDIT": ("int", "15"),
                "BOSS_LEAN": ("int", "3"), "BOSS_ARMOR": ("int", "50")}
        check(all(s.count('("%s", "%s", "%s")' % (f, t, v)) == 1 for f, (t, v) in fdef.items()), "A: the 6 CFG_FIELDS with their defaults")
        apl = {"PACK_ON": 'PACK_ON = pbool(p, "part.packDrops", true);'}
        for k, (ty, df, lo, hi, fld, _d) in ROWS319.items():
            if ty == "dec":
                apl[fld] = '%s = pdec(p, "%s", %s, %s, %s);' % (fld, k, float(df), float(lo), float(hi))
            elif ty == "int":
                apl[fld] = '%s = (int) plong(p, "%s", %sL, %sL, %sL);' % (fld, k, df, lo, hi)
        check(all(s.count(v) == 1 for v in apl.values()), "A: GearCfg.apply reads each row with the row's default and bounds: missing %s"
              % [v for v in apl.values() if s.count(v) != 1])
        check('G319_ROWK = ["part.packDrops", "loot.packWeight", "loot.boss.mythic", "loot.boss.credit", "loot.boss.classLean", "loot.boss.armorShare"]' in s
              and '    L += ["", G319_HEAD]' in s and s.index('    L += ["", G319_HEAD]') < s.index("    for k in G319_ROWK:\n        scal(k)")
              and s.index('    L += ["", G317_HEAD]') < s.index('    L += ["", G319_HEAD]'),
              "A: the fresh file: the G319 block (G319_HEAD + the 6 keys) after the 0.3.17 block")
        check(re.search(r'_DANGER = \{[^}]*"part\.packDrops", "loot\.boss\.mythic"\}', s) is not None, "A: part.packDrops + loot.boss.mythic in _DANGER")
        check(s.count("+ G317_CLASSES + G318_CLASSES + G319_CLASSES") == 1 and "G319_CLASSES = G319_EARLY + [gpack, gpgv]" in s,
              "A: GearPackId + GearPack + GearPackGive are in the jar's class list (G319_CLASSES)")
        i_pid = s.index('gpid = mk("GearPackId")')
        i_fl = s.index("for _n, _t, _v in CFG_FIELDS:")
        uses = [m.start() for m in re.finditer(r"@PKG@\.GearPackId\.", s)]
        check(i_fl < i_pid and all(u > i_pid for u in uses) and i_pid < s.index("public static boolean isGearMs(String id, int ms)"),
              "A: GearPackId is built after the GearCfg field loop and before every other class's use of it (javassist compiles at M() time)")
        i_pk = s.index('gpack = mk("GearPack")')
        i_tk = s.index('M(gdm, r"""\npublic void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {')          # GearDeathMark's own tick
        tick = s[i_tk:s.index('}""")', i_tk)]
        check(i_pk < i_tk and all(m.start() > i_pk for m in re.finditer(r"@PKG@\.GearPack\.", s))
              and re.search(r"if \(@PKG@\.GearCfg\.PACK_ON\) \{[^\n]*\n\s*try \{ @PKG@\.GearPack\.bossRoll\(chunk, idx, store, cb, dc, npc, p, wk\); \}\n"
                            r"\s*catch \(Throwable tb\) \{ @PKG@\.Gear\.warnOnce\(\"bossroll\"", tick) is not None
              and "!@PKG@.GearCfg.PACK_ON) return;" in tick,
              "A: GearDeathMark.tick calls GearPack.bossRoll (PACK_ON, try / warnOnce), GearPack built before it")
        i_cs = s.index('event_system(gcrs, "GearCraftSys"')
        i_cb = s.index('r"""', i_cs) + 4
        cs = s[i_cb:s.index('"""', i_cb)]
        check(0 < cs.find("GearRoll.craftable(id)) return;") < cs.find("if (@PKG@.GearPackId.swap(rc, id)) return;") < cs.find("chunk.getReferenceTo(idx)"),
              "A: the swap guard sits in GearCraftSys between craftable() and the roll")
        check('if (pz > 0) d.append("pz", new org.bson.BsonInt32(pz));' in s
              and "public static @IS@ make(int ty, int at, int r, int lo, int hi, String src, String ls, int tier) { return makeZ(ty, at, r, lo, hi, src, ls, tier, 0); }" in s,
              "A: makeZ adds pz only when pz > 0; make() = makeZ(..., 0)")
        check(s.count("if (@PKG@.GearPool.rangeM(ty, at(d), pz(d)) != null || @PKG@.GearPool.rangeM(ty, 0, pz(d)) != null) return null;") == 1
              and 'return "This Zone " + pz(d) + " Mythic bag waits for its Mythic pieces' in s
              and s.count("if (@PKG@.GearPool.rangeM(ty, at(b), pz(b)) != null || @PKG@.GearPool.rangeM(ty, 0, pz(b)) != null) return null;") == 1
              and 'return "No Zone " + pz(b) + " Mythic "' in s
              and s.count("pickZ(type(b), at(b), rar(b), lo(b), hi(b), rerolls(b) + 1, by, pz(b))") == 2
              and "return pickZ(type(d), at(d), rar(d), lo(d), hi(d), 0, by, pz(d));" in s,
              "A: why / rerollWhy: a boss bag / item with a Mythic piece of its zone (its weight or any) = ok, else the zone refusal; open + both "
              "rerolls pass pz on")
        i_pz = s.index("public static Object[] pickZ(")
        pzb = s[i_pz:s.index('}""")', i_pz)]
        check(re.search(r"return new Object\[\] \{ mid, Integer\.valueOf\(mL\), md, ms \};\n\s*\}\n\s*\}\n\s*return null;\n\s*\}\n\s*if \(!ut\)", pzb) is not None,
              "A: pickZ: a boss bag whose zone has no Mythic piece left is refused (null), never the normal pool (review M5)")
        check("!(((double[]) t[8])[i] > 0.0)) return false;" in s and "sum = sum + ((double[]) t[8])[i];" in s and "r = r - ((double[]) t[8])[i];" in s,
              "A: matchM / pickItemM weigh by the set share only, never loot.packWeight (review M5)")
        i_ro = s.index("public static java.util.ArrayList rollers(")
        rob = s[i_ro:s.index('}""")', i_ro)]
        check("if (us.isEmpty() && who.length == 0) {" in rob, "A: rollers: the killer only when SkyyMobs credited nobody (review M4)")
        i_br = s.index("public static int bossRoll(")
        brb = s[i_br:s.index('}""")', i_br)]
        check(0 < brb.find("if (!firstOfFight(pr.getUuid(), fam, now)) { @PKG@.GearPool.bcount(6, 1L); continue; }")
              < brb.find("@PKG@.GearRoll.RNG.nextDouble() * 100.0 < @PKG@.GearCfg.BOSS_MY") < brb.find("mythicBag(z, ")
              and "capOk" not in brb and "String fam = family(role);" in brb
              and "SkyyMobs credited nobody, the killer rolls" in brb
              and "if (seam != null) seam.apply(l.get(i), at);" in brb and "w.execute(new @PKG@.GearPackGive(" in brb
              and "cb.addEntities(hs, @ADDR@.SPAWN);" in brb,
              "A: bossRoll: once per fight per player (BN[6], critic 4), then the chance, then the bag - no hourly cap (critic 5); the seam / a GearPackGive world task / a ground drop "
              "without a world; the 'credited nobody' log line")
        check(s.index('gpgv = mk("GearPackGive")') < s.index("new @PKG@.GearPackGive(") and "public void run() {" in s[s.index('gpgv = mk("GearPackGive")'):i_br]
              and 'how = "inventory"' in s and "@ITU@.dropItem(r, this.bag, this.store); how = \"feet\";" in s
              and "this.store.addEntities(hs, @ADDR@.SPAWN); how = \"boss\";" in s and '"LOOT boss-give "' in s,
              "A: GearPackGive (built before bossRoll uses it): inventory, else ItemUtils.dropItem at the feet, else the boss; the LOOT boss-give line")
        i_gv = s.index('gpgv = mk("GearPackGive")')
        gvb = s[s.index("public void run() {", i_gv):i_br]
        check(0 < gvb.find("here = r != null && r.isValid() && r.getStore() == this.store;") < gvb.find("if (here) inv = @PKG@.GearStamp.invOf(this.pr);")
              < gvb.find('if ("lost".equals(how) && r.isValid() && r.getStore() == this.store) { @ITU@.dropItem(')
              < gvb.find('if ("lost".equals(how) && this.store != null) {') and "@PKG@.GearStamp.invOf(" not in gvb.replace("if (here) inv = @PKG@.GearStamp.invOf(", ""),
              "A: GearPackGive re-checks the winner's Ref (valid, getStore() == the boss's store) before the inventory / feet; else the boss (fix round 1)")
        i_lt = s.index("public static int liveType(int i)")
        ltb = s[i_lt:s.index('}""")', i_lt)]
        check("if (P_AT[i] == 0) return a == null && it.getWeapon() != null ? P_T[i] : -1;" in ltb,
              "A: liveType: a weapon row needs a live weapon (Item.getWeapon), else -1 (fix round 3)")
        check("us.size() < 8" not in rob and "for (int i = 0; i < who.length && i < sh.length; i++) {" in rob,
              "A: rollers: no cap of 8 credited players (fix round 4)")
        i_am = s.index("public static int[] pickArmM(int z) {")
        amb = s[i_am:s.index('}""")', i_am)]
        i_mb = s.index("public static @IS@ mythicBag(")
        mbb = s[i_mb:s.index('}""")', i_mb)]
        check("pickAtM" not in s and amb.find("int k = @PKG@.GearRoll.RNG.nextInt(n);") < amb.find("int j = @PKG@.GearRoll.RNG.nextInt(m);")
              and "if (k == 0 ? armor : !armor) pk = @PKG@.GearPool.pickArmM(z);" in mbb
              and "int wt = @PKG@.GearPool.pickTypeM(false, z, lean, @PKG@.GearCfg.BOSS_LEAN);" in mbb and "pickTypeM(true" not in s
              and s.index("public static int pickTypeM(") < i_am < s.index('gpack = mk("GearPack")'),
              "A: Mythic armor = the weight evenly (pickArmM), then a slot of it; weapons keep pickTypeM's class lean; the other side when empty (fix round 2, Q13)")
        check('F(gpool, "public static final long[] BN = new long[7];")' in s and '", same fight " + BN[6] + ", opened from Mythic sets " + BN[5]' in s,
              "A: BN has 7 counters; packText prints the same-fight skips (critic 4)")
        # ---------------------------------------------------------------- X: the critic fixes (local rebuild), by the generated source
        i_pre = s.index('event_system(gcrp, "GearCraftPreSys"')
        preb = s[i_pre:s.index('"""', s.index('r"""', i_pre) + 4)]
        check(0 < preb.find("@PKG@.GearPackId.special(id0) && !@PKG@.GearPackId.sameSet(rc0, id0)") < preb.find("@PKG@.GearPackId.swap(rc0, id0)")
              and '"CRAFT-BLOCK-PACK "' in preb and "pm.getGameMode() != @GM@.Creative" in preb and "is a Mythic boss drop - it is not crafted here." in preb,
              "X1: CraftRecipeEvent$Pre refuses a UT / Mythic table output (benches + SkyySacks /craft), except a same-set Alteration swap; Creative crafts")
        check("if (@PKG@.GearPackId.special(id)) return newDoc(id, 0, true, src); return newDoc(id, pickRarity(col), false, src);" in s
              and "  if (@PKG@.GearPackId.special(id)) return null;          // critic fix 1" in s
              and "  if (@PKG@.GearPackId.special(s0.getItemId())) return 0;          // critic fix 1" in s,
              "X1: a UT / Mythic table piece found in chests / on mobs = plain Normal (unidDoc), never a bag (fromItem, spread)")
        i_sm = s.index("public static boolean sameSet(@CRR@ rc, String out)")
        smb = s[i_sm:s.index('}""")', i_sm)]
        check("if (rc == null || !alter(rc)) return false;" in smb and "SET[j] != st" in smb and "h.size() != 1" in smb
              and s.index("public static boolean alter(@CRR@ rc)") < i_sm < i_pre,
              "X1: sameSet = an Alteration recipe whose item inputs are rows of the output's set and whose resources only that set carries")
        check("boolean plain = @PKG@.GearPackId.plainCraft(id, a.length > 4 ? a[4] : null);" in s
              and "if (!@PKG@.GearPackId.has(id)) @PKG@.GearRoll.payCraft(u, id, gx.toString(), \"/craft\");" in s
              and "if (@PKG@.GearPackId.special((String) a[1])) return Boolean.FALSE;" in s,
              "X2: gear:fn:roll mode 8: plain for a swap / UT / Mythic output, no XP for pack pieces; gear:fn:classShow hides UT / Mythic rows")
        i_sw = s.index("public static boolean swap(@CRR@ rc, String out)")
        swb = s[i_sw:s.index('}""")', i_sw)]
        check("in[i].getResourceTypeId()" in swb and "resSets(rid) != null" in swb and s.index("public static java.util.HashSet resSets(") < i_sw
              and "@PKG@.GearPackId.carries(sid, rid)" in s and "@PKG@.Gear.itemName(sid) + \" in your inventory carries a rolled rarity" in s,
              "X3: the swap guard + veto read ResourceTypeId inputs (resSets / carries)")
        check("public static String family(String role)" in s and 'role.indexOf("_Phase")' in s and "FIGHT_MS = 120000L" in s,
              "X4: a boss family = the role up to _Phase, once per player per 120 s")
        check("int pc = @PKG@.GearPackId.gc(pk);" in s and "long e = @PKG@.GearCfg.EPOCH;" in s
              and "((Integer) t[9]).intValue() == ic" in s and "now - ((Long) t[1]).longValue() < 60000L" not in s
              and "if (cnt(cs[i], this.bag.getItemId()) != c0) how = \"inventory\";" in s and 'how = "error"' not in s,
              "X6: isGear pack cache (GearCfg.EPOCH), table on epoch / item count only, GearPackGive counts before / after a throwing write")
        check(0 < preb.find("@PKG@.GearPackId.salvage(rc0)") < preb.find("@PKG@.GearPackId.special(id0)")
              and "@PKG@.GearPack.salvVeto(rc0, pv.getInventory())" in preb and '"CRAFT-BLOCK-SALVAGE "' in preb
              and "pv.getGameMode() == @GM@.Creative ? null" in preb,
              "X8: CraftRecipeEvent$Pre refuses a Salvagebench recipe while a dropped / identified pack piece of its input is held (Skyy: Requip only); Creative salvages")
        i_sv = s.index("public static String salvVeto(@CRR@ rc, @INV@ inv)")
        svb = s[i_sv:s.index('}""")', i_sv)]
        check("@PKG@.GearPackId.salvage(rc)" in svb and "@PKG@.GearPackId.carries(sid, rid)" in svb and "salvBlocked(sid, s.getMetadata())" in svb
              and "Requip's SALVAGE button" in svb and s.index("public static boolean salvBlocked(") < i_sv < i_pre
              and '"Salvagebench".equalsIgnoreCase(b[i].id)' in s,
              "X8: salvVeto reads item + resource inputs, blocks a non-craft document, points to Requip SALVAGE")
        check("PKD.coin_keys(_ARMJ[-1])" in s and "no table id carries a Value / Price / Sell / Coin / Worth field" in s,
              "X7: the build's coin-loop guard (tools/pack_drops.py coin_keys on the installed Armory jar)")
        i_cp = s.index('event_system(gcrp, "GearCraftPreSys"')
        cpb = s[i_cp:s.index('"""', s.index('r"""', i_cp) + 4)]
        check("@PKG@.GearPackId.swap(rc0, id0)" in cpb and "@PKG@.GearPack.swapVeto(rc0, id0, ps.getInventory())" in cpb and "e.setCancelled(true);" in cpb
              and "ps.getGameMode() != @GM@.Creative" in cpb and s.index("public static String swapVeto(") < i_cp,
              "A: GearCraftPreSys cancels a pack swap while a rolled input piece is held (GearPack.swapVeto, not in Creative; review M1)")
        check("if (!@PKG@.GearPackId.has(this.id)) @PKG@.GearRoll.payCraft(" in s, "A: GearCraftTask: no Smithing craft XP for a pack piece (review M2)")
        i_al = s.index("public static boolean alter(@CRR@ rc)")
        alb = s[i_al:s.index('}""")', i_al)]
        check('"ArmoryAlteration".equals(b[i].id)' in alb and "rc.getBenchRequirement()" in alb
              and "|| @PKG@.GearPackId.alter(rc)) return null;" in s and i_al < s.index("public static String swapVeto("),
              "A: the swap veto skips The Armory's Alteration Table (bench ArmoryAlteration keeps the input's metadata + quality - local rebuild)")
        i_gm = s.index("public static boolean isGearMs(String id, int ms)")
        gmb = s[i_gm:s.index('}""")', i_gm)]
        check(0 < gmb.find("@PKG@.GearPackId.has(id)") < gmb.find("@PKG@.GearCfg.excl()") < gmb.find("if (ms <= 1) return true;"),
              "A: isGearMs: gear.exclude wins over a pack id (review L2)")
        check("public static double w(int i)" not in s and not re.search(r"[^\w.]w\(i\)", s), "A: GearPool.w(int) is gone, no caller left")
        mline = [ln for ln in s.split("\n") if ln.startswith("man = B.manifest(")]
        check(len(mline) == 1 and "PACK DROPS" in mline[0] and "LadyPaladra" in mline[0] and "CC BY-NC" in mline[0],
              "A: the manifest description names PACK DROPS + LadyPaladra (CC BY-NC)")
        check(s.count("registerSystem(") == s18.count("registerSystem(") and s.count("registerCommand(") == s18.count("registerCommand("),
              "A: no new system / command (registerSystem %d, registerCommand %d)" % (s.count("registerSystem("), s.count("registerCommand(")))
        mk19 = set(re.findall(r'^\w+\s*=\s*mk\("(\w+)"', s, re.M))
        mk18 = set(re.findall(r'^\w+\s*=\s*mk\("(\w+)"', s18, re.M))
        check(mk19 - mk18 == set(S319_NEW) and not mk18 - mk19, "A: classes made: new %s, gone %s" % (sorted(mk19 - mk18), sorted(mk18 - mk19)))

        # ---------------------------------------------------------------- S: the changed classes by text
        a, b = s18.split("\n"), s.split("\n")
        var = dict(re.findall(r'^(\w+)\s*=\s*mk\("(\w+)"', s, re.M))
        java = re.compile(r"^(\s|\}|public |private |protected |static |@|$)")
        touched = {}
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            for j in (range(j1, j2) if j2 > j1 else [j1]):
                k = min(j, len(b) - 1)
                while k > 0 and java.match(b[k]):
                    k -= 1
                m = re.match(r"^(?:M|F|C|event_system)\((\w+),", b[k])
                if m:
                    touched[var.get(m.group(1), m.group(1))] = touched.get(var.get(m.group(1), m.group(1)), 0) + 1
        print("  Java members changed per class: %s" % ", ".join("%s %d" % kv for kv in sorted(touched.items())))
        check(set(touched) == set(S319_MUST) | set(S319_NEW), "S: the Java of exactly S319_MUST + S319_NEW changed: extra %s, missing %s"
              % (sorted(set(touched) - set(S319_MUST) - set(S319_NEW)), sorted((set(S319_MUST) | set(S319_NEW)) - set(touched))))

        # ---------------------------------------------------------------- P: the class-file reader S319 C uses
        jj = os.path.join(TOOLS, "javassist.jar")
        if os.path.isfile(jj):
            n, bad = 0, []
            with zipfile.ZipFile(jj) as z:
                for nm in z.namelist():
                    if nm.endswith(".class"):
                        try:
                            cpool(z.read(nm))
                            n += 1
                        except Exception as e:
                            bad.append("%s: %s" % (nm, e))
                c = cpool(z.read("javassist/ClassPool.class"))
            check(not bad and n > 100 and has_ref(c, "M", "javassist/ClassPool", "get") and "javassist/CtClass" in c["class"],
                  "P: the constant-pool reader reads all %d classes of tools/javassist.jar (ClassPool -> ClassPool.get, CtClass): %s" % (n, bad[:2]))
        else:
            check(False, "P: tools/javassist.jar is missing (the reader's self-test)")
    finally:
        if not keep:
            shutil.rmtree(sdir, ignore_errors=True)
    print("SkyyGear %s harness --static: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    return 1 if FAILS else 0


# ====================================================================================================== main
def main():
    if STATIC:
        sys.exit(run_static())
    if "--h319" in sys.argv:
        run_h319(arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--only", "--keep", "--dir", "--jar", "--root", "--out") for a in sys.argv[1:]):
        H318["main"]()          # an older child flag (0.3.18 dispatches --h318, the rest goes on down)
        return
    assert os.path.isfile(J318), J318
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    H318["run_assets318"] = run_assets319          # the jar compare of THIS round (0.3.18 -> 0.3.19)
    # ours runs after h318: 0.3.18's main wraps H316["main"] (its take3 runs h317 + h318 after the h316 result); this wrapper sits UNDER it,
    # so by the time it runs H316["take"] is 0.3.18's take3 - h319 follows it in the same scratch folder
    _orig_main316 = H316["main"]

    def main316():
        take18 = H316["take"]

        def take4(path, label):
            d = take18(path, label)
            if label == "h316" and want("h319"):
                env = dict(os.environ)
                env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
                env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
                out = os.path.join(SCRATCH, "h319.json")
                pr = H316["child"](env, "--h319", "--out", out)
                check(pr.returncode == 0, "h319: the child exited cleanly (%s)" % pr.returncode)
                take18(out, "h319")
            return d
        H316["take"] = take4
        return _orig_main316()
    H316["main"] = main316
    if only and "h319" in only.split(",") and "h316" not in only.split(","):
        sys.argv[sys.argv.index("--only") + 1] = only + ",h316"
    H318["main"]()


if __name__ == "__main__":
    main()
