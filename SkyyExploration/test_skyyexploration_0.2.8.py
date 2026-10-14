"""Harness for SkyyExploration 0.2.8 (Lost Loot piles + supply drops + the reveal page / identify animation service;
tools/exploration_0_2_8_patch.py). Build first: python tools/exploration_0_2_8_patch.py && python SkyyExploration/build_skyyexploration_0.2.8.py

    python SkyyExploration/test_skyyexploration_0.2.8.py [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.2.7 -> 0.2.8: exactly the planned members differ (+ LgFall, LgAir, LgRv, LgRvOpen, LgReveal, LgRvFn); non-class entries:
              manifest.json + the asset pack files of the five blocks (server.lang + T1..T4 changed, T5 added)
  X  exec     EVERY NEW CODE PATH (-Xverify:all): config defaults / apply / check (airdrop.table); the five block JSONs + lang in the jar
              (vanilla paths, particles, lights, names); LgSite tier 5; LgRv card / parse / sorted / rarIdx / queue / show (server row +
              player setting); LgRvFn (explore:fn:reveal) refusals; the LgReveal page build (face down / face up / back) + step (Open next,
              Open all, Close, Back, unknown) + best; LgAir: the timer, a start, the fall, the landing through the 0.2.7 write-ahead act
              (the line first, then the block + landing effects), compass words, announce without a world, adminDrop refusals;
              CLAIM ONCE: Lost Loot (tier 1) - first claim ok, a 2nd player and the same player refused; SUPPLY DROP - two players (the
              2nd refused while the 1st claim waits), RELOG (the claimer gone when the act runs -> the claim undone, nothing given, the
              drop claimable again), the claim by the 2nd player through claimOk (coins + bags + XP cards, best last, the drop vanishes
              and its line goes - on disk too, a re-read registry has no drop), nothing more to claim; the despawn rule (placedAt +
              despawnSeconds, switched off, a claim saved before a restart vanishes then goes); respawn / anyDue / spawnNear ignore drops
  D  live     START TWICE on a scratch COPY of the live Skyy_SkyyExploration: every player record read by 0.2.7 AND 0.2.8 gives the same
              snap(); every luggage registry read on the writer and saved back byte-identical; no other file changes
  AA engine-access audit
Scratch: tools/dev/scratch/lostlootfix/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, time, json, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.2.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-0.2.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "lostlootfix", "harness")))
PKG = "com.skyy.explore."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyExploration")
IDS = ["Skyy_LootChest_T%d" % i for i in (1, 2, 3, 4, 5)]
NONCLASS = sorted(["manifest.json", "Server/Languages/en-US/server.lang"] + ["Server/Item/Items/SkyyExploration/%s.json" % i for i in IDS])

EXPECT = {
    "ExpCfg": ["+f LG_REVEAL", "+f AIR_ON", "+f AIR_INT_S", "+f AIR_RING_MIN", "+f AIR_RING_MAX", "+f AIR_FALL_S", "+f AIR_DESPAWN_S",
               "+f AIR_MAX", "+f AIR_ANNOUNCE", "+f AIR_TABLE", "+f AIR_COIN_MIN", "+f AIR_COIN_MAX", "+f AIR_BAGS", "+f AIR_XP",
               "~m apply", "~m check", "~<clinit>", "~m live", "~m load"],
    "LgApi": ["+m fx", "+m snd", "+m give"],
    "LgEng": ["+f SIDX", "+m fx", "+m snd", "~<clinit>"],
    "LgSite": ["~m parse"],
    "LgCore": ["+f NAME", "+m name", "~m placeNow", "+m airSweep", "~m sweep", "~m respawn", "~m spawnNear", "~m anyDue",
               "~m worldPass", "~m second", "~m give", "+m stackCard", "+m loot", "-m loot", "~m claimOk", "+m refuse", "~m use", "~m listNear",
               "~m adminHere", "+m adminPlace", "+m adminTier", "+m placeNear", "~m statsText", "~<clinit>", "~m undo", "~m claimLater"],
    "ExGuard": ["~m mine", "~m accept"],
    "ExWatch": ["~m tick"],
    "ExAdminOps": ["~m help"],
    "ExLuggageCmd": ["~c "],
    "ExLuggageListCmd": ["~c "],
    "ExploreAdminCmd": ["~c "],
    "SkyyExplorationPlugin": ["+f revealFn", "~m setup", "~m shutdown"],
    "ExpLgMig": ["~m logLine", "~m migrate"],   # its WHO constant (inlined) names the version ("SkyyExploration 0.2.8")
    # the config kit (tools/skyycfg.py): the new rows / the default file text are constants of its classes
    "CfgFile": ["~<clinit>"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
}
ADDED = ["LgFall", "LgAir", "LgRv", "LgRvOpen", "LgReveal", "LgRvFn", "ExAirdropCmd", "ExLuggageTierCmd", "ExLuggageClearCmd", "ExRevealCmd"]


# ---------------------------------------------------------------- C: the kit's compare, with this round's asset pack entries allowed
def run_compare(out, jar, old_jar, pkg, expect, added):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(old_jar), pool_of(jar)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
                lines_.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_))
            return str(b_.getModifiers()) + "\n" + "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = HK.jar_classes(old_jar), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), [], "C: classes removed")
    diffs, same = {}, 0
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(pkg):] if cn.startswith(pkg) else cn] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k for k in dd)
        else:
            same += 1
    print("C. class compare %s -> %s: %d classes identical, %d differ" % (os.path.basename(old_jar), os.path.basename(jar), same, len(diffs)))
    for k in sorted(diffs):
        print("   %-22s %s" % (k, ", ".join(x.split("(")[0] for x in diffs[k])))
    K.eq(sorted(diffs), sorted(expect), "C: the classes that differ")
    for k in sorted(expect):
        got = sorted(x.split("(")[0] if not x[1:].startswith("c ") else x[:3] for x in diffs.get(k, []))
        K.eq(got, sorted(expect[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    K.eq(ed, NONCLASS, "C: non-class entries changed (manifest + the five blocks + lang)")
    K.notes.append("C: %d identical, changed: %s" % (same, {k: [x.split("(")[0] for x in v] for k, v in diffs.items()}))
    K.save()


HK.run_compare = run_compare


def sim(state):
    from jpype import JImplements, JOverride, JArray, JObject, JInt
    G = state["ground"]

    @JImplements(PKG + "LgApi")
    class Sim(object):
        @JOverride
        def blockId(self, w, x, y, z):
            if (x, y, z) in state["placed"]:
                return state["placed"][(x, y, z)]
            return G if y <= 64 else "Empty"
        @JOverride
        def height(self, w, x, z): return 64
        @JOverride
        def hasEntity(self, w, x, y, z): return False
        @JOverride
        def fluid(self, w, x, y, z): return False
        @JOverride
        def place(self, w, x, y, z, id_):
            state["placed"][(x, y, z)] = str(id_)
            state["log"].append(("place", x, y, z, str(id_)))
            return True
        @JOverride
        def clear(self, w, x, y, z):
            state["placed"].pop((x, y, z), None)
            state["log"].append(("clear", x, y, z))
            return True
        @JOverride
        def levelAt(self, wn, x, y, z): return JArray(JObject)([JInt(23), JInt(23)])
        @JOverride
        def occupied(self, w, x, y, z): return False
        @JOverride
        def sound(self, w, x, y, z): state["log"].append(("sound", x, y, z))
        @JOverride
        def poof(self, w, x, y, z): state["log"].append(("poof", x, y, z))
        @JOverride
        def fx(self, w, id_, x, y, z): state["log"].append(("fx", str(id_), float(x), float(y), float(z)))
        @JOverride
        def snd(self, w, id_, x, y, z): state["log"].append(("snd", str(id_)))
        @JOverride
        def give(self, is_): state["given"].append((str(is_.getItemId()), int(is_.getQuantity())))
    return Sim()


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JInt, JLong, JBoolean, JObject, synchronized
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    EIO, Reg, Core, Site, Eng, Cfg, Air, Rv, RvO, Rev, RvF, Fall, CR_ = (
        P("ExpIO"), P("LgReg"), P("LgCore"), P("LgSite"), P("LgEng"), P("ExpCfg"), P("LgAir"), P("LgRv"), P("LgRvOpen"), P("LgReveal"),
        P("LgRvFn"), P("LgFall"), P("ChestReg"))
    Sys, Paths, Executors, Props, CHM, UUID, AL = (JClass("java.lang.System"), JClass("java.nio.file.Paths"),
                                                  JClass("java.util.concurrent.Executors"), JClass("java.util.Properties"),
                                                  JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.UUID"),
                                                  JClass("java.util.ArrayList"))
    LIO = P("LgIO")
    # ---- config
    Cfg.apply(Props())
    K.check(Cfg.LG_REVEAL and Cfg.AIR_ON and Cfg.AIR_INT_S == 1800 and Cfg.AIR_RING_MIN == 32 and Cfg.AIR_RING_MAX == 64 and Cfg.AIR_FALL_S == 10
            and Cfg.AIR_DESPAWN_S == 600 and Cfg.AIR_MAX == 1 and Cfg.AIR_ANNOUNCE == 160 and str(Cfg.AIR_TABLE) == "Zone{zone}_Encounters_Tier4"
            and Cfg.AIR_COIN_MIN == 150 and Cfg.AIR_COIN_MAX == 400 and abs(Cfg.AIR_BAGS - 2.5) < 1e-9 and Cfg.AIR_XP == 1500,
            "X config: an old file without the new lines = the defaults")
    pp = Props()
    for k, v in (("airdrop.enabled", "false"), ("airdrop.intervalSeconds", "5"), ("airdrop.ringMin", "90"), ("airdrop.ringMax", "40"),
                 ("airdrop.perWorld", "99"), ("airdrop.coinsMin", "500"), ("airdrop.coinsMax", "100"), ("airdrop.bags", "50"), ("luggage.reveal", "false")):
        pp.setProperty(k, v)
    Cfg.apply(pp)
    K.check(not Cfg.AIR_ON and Cfg.AIR_INT_S == 60 and Cfg.AIR_RING_MIN == 90 and Cfg.AIR_RING_MAX == 90 and Cfg.AIR_MAX == 20
            and Cfg.AIR_COIN_MAX == 500 and abs(Cfg.AIR_BAGS - 20.0) < 1e-9 and not Cfg.LG_REVEAL,
            "X config: clamps (interval >= 60, ring max >= min, perWorld <= 20, coins max >= min, bags <= 20) + switches")
    Cfg.apply(Props())
    K.check(Cfg.check("airdrop.table", "Zone{zone}_Encounters_Tier4") is None and Cfg.check("airdrop.table", "") is None
            and Cfg.check("airdrop.table", "Zone1_Encounters_Tier3") is None and Cfg.check("airdrop.table", "Zone {zone}") is not None
            and Cfg.check("airdrop.table", "Zone{tier}") is not None, "X config: airdrop.table check ({zone} ok, spaces / other braces refused)")
    defs = str(Cfg.DEFAULTS) if hasattr(Cfg, "DEFAULTS") else ""
    # ---- the asset pack entries
    z = zipfile.ZipFile(jar)
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    names = ["Lost Loot (I)", "Lost Loot (II)", "Lost Loot (III)", "Lost Treasure (IV)", "Supply Drop"]
    K.check(all(("items.%s.name = %s" % (i, n)) in lang for i, n in zip(IDS, names)) and "Unclaimed Luggage" not in lang,
            "X assets: the five names in server.lang (no 'Unclaimed Luggage' left)")
    bj = [json.loads(z.read("Server/Item/Items/SkyyExploration/%s.json" % i)) for i in IDS]
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    an = set(az.namelist())
    ok = True
    for j in bj:
        bt = j["BlockType"]
        ok = ok and ("Common/" + bt["CustomModel"]) in an and ("Common/" + bt["CustomModelTexture"][0]["Texture"]) in an and ("Common/" + j["Icon"]) in an
        ok = ok and "BlockEntity" not in bt and "State" not in bt and bt["Gathering"]["Breaking"]["DropList"] == "Empty"
        ok = ok and bt["Interactions"]["Use"]["Interactions"][0]["Page"]["Id"] == "SkyyLuggage" and bt.get("Particles")
        for p_ in bt["Particles"]:
            ok = ok and any(n.endswith("/" + p_["SystemId"] + ".particlesystem") for n in an)
    K.check(ok, "X assets: every model / texture / icon / particle is a vanilla path; no block entity; drops nothing; Use = our page")
    K.check(bj[3]["BlockType"]["CustomModel"].endswith("Treasure_Pile_Small.blockymodel") and bj[4]["BlockType"]["CustomModel"].endswith("Crate.blockymodel")
            and bj[4]["BlockType"]["Particles"][0]["SystemId"] == "World_Event_Hunt_Marker_Generic" and "Light" in bj[3]["BlockType"] and "Light" in bj[4]["BlockType"]
            and bj[0]["BlockType"]["Particles"][0]["SystemId"] == "Block_Treasure_Sparks" and bj[2]["BlockType"]["Particles"][0]["SystemId"] == "Block_Gem_Sparks",
            "X assets: I/II orange sparks, III white gem sparks + light, IV treasure pile + light, V crate + hunt beam + light")
    # FIX (flash / beam visibility): the falling flash and the landed beam reach the players they are meant for
    def cull(sid):
        t_ = az.read([n for n in an if n.startswith("Server/Particles/") and n.endswith("/" + sid + ".particlesystem")][0]).decode("utf-8")
        m_ = re.search(r'"CullDistance"\s*:\s*([0-9.]+)', t_)
        return float(m_.group(1)) if m_ else 0.0
    far = (64.0 ** 2 + 40.0 ** 2) ** 0.5
    K.check(cull("Firework_Mix4") >= far and float(Air.FALL_H) == 40.0 and cull("World_Event_Hunt_Marker_Generic") >= 256.0,
            "X FIX flash: Firework_Mix4 CullDistance %.0f >= %.0f (ringMax 64, 40 up); the landed beam CullDistance %.0f >= 256 (was 16)"
            % (cull("Firework_Mix4"), far, cull("World_Event_Hunt_Marker_Generic")))
    vanilla_files = [n for n in z.namelist() if not n.endswith(".class") and n in an and n not in ("Server/Languages/en-US/server.lang", "manifest.json")]
    K.check(vanilla_files == [] and not any(n.endswith((".png", ".blockymodel")) for n in z.namelist()),
            "X assets: no vanilla file copied or shadowed, no texture / model in the jar")
    # ---- LgSite tier 5
    K.check(Site.parse("1\t65\t1\t5\t23\t0\t10\t0\t10\t7\t") is not None and Site.parse("1\t65\t1\t6\t23\t0\t10\t0\t10\t7\t") is None,
            "X LgSite.parse: tier 5 (supply drop) read, tier 6 refused")
    # ---- LgRv
    c1 = Rv.card("Bad Id!", "x" * 200, "s\nub", "#12345z", 9, "", None)
    K.check(str(c1[0]) == "Tool_Map" and len(str(c1[1])) == 80 and str(c1[2]) == "s ub" and str(c1[3]) == "#FFFFFF" and str(c1[4]) == "2"
            and str(c1[5]) == "Tool_Map" and str(c1[6]) == "?", "X LgRv.card: bad icon / colour / rank / long text sanitised")
    K.check(Rv.rarIdx("Legendary") == 3 and Rv.rarIdx("untiered") == 7 and Rv.rarIdx("x") == -1 and str(Rv.RCOL[2]) == "#FF55FF"
            and Rv.RRANK[2] == 1 and Rv.RRANK[3] == 2 and Rv.RRANK[0] == 0, "X LgRv rarity table (SkyyGear's ladder)")
    ins = JArray(JString)(["Weapon_Sword_Iron|Iron Sword|Lv 5 - Rare|#FF55FF|1|Skyy_Unid_Bag|Unidentified Sword", "bad", None, "|", "A|B"] +
                          ["Tool_Map|n%d|s|#FFFFFF|0" % i for i in range(12)])
    ps = Rv.parse(ins)
    K.check(len(ps) == 10 and str(ps[0][0]) == "Weapon_Sword_Iron" and str(ps[0][4]) == "1" and str(ps[0][5]) == "Skyy_Unid_Bag"
            and str(ps[1][1]) == "B" and str(ps[1][0]) == "A" and str(ps[1][3]) == "#FFFFFF", "X LgRv.parse: valid cards kept, bad skipped, at most 10")
    K.check(len(Rv.parse("x")) == 0 and len(Rv.parse(None)) == 0, "X LgRv.parse: not a String[] = none")
    l = AL()
    for r_ in (2, 0, 1, 0):
        l.add(Rv.card("Tool_Map", "r%d" % r_, "", "#FFFFFF", r_, "", ""))
    so = Rv.sorted(l)
    K.check([str(c[1]) for c in so] == ["r0", "r0", "r1", "r2"], "X LgRv.sorted: by rank, the best last")
    for i in range(10):
        l.add(Rv.card("Tool_Map", "z%d" % i, "", "#FFFFFF", 0, "", ""))
    K.check(len(Rv.sorted(l)) == 10 and str(Rv.sorted(l)[9][1]) == "r2", "X LgRv.sorted: at most 10 (the best kept)")
    # FIX (cards over 10): 14 finds = "+5 more finds" first (same cover) + the 9 best, the best last
    l14 = AL()
    for i in range(13):
        l14.add(Rv.card("Tool_Map", "c%d" % i, "", "#FFFFFF", 0, "Skyy_LootChest_T5", "Supply Drop"))
    l14.add(Rv.card("Tool_Map", "best", "", "#FFFFFF", 2, "Skyy_LootChest_T5", "Supply Drop"))
    s14 = Rv.sorted(l14)
    K.check(len(s14) == 10 and str(s14[0][1]) == "+5 more finds" and str(s14[0][5]) == "Skyy_LootChest_T5" and str(s14[0][6]) == "Supply Drop"
            and str(s14[9][1]) == "best" and [str(c[1]) for c in s14[1:9]] == ["c%d" % i for i in range(5, 13)],
            "X FIX LgRv.sorted: 14 finds = '+5 more finds' first + the 9 best, the best last (every find counted)")
    l10 = AL()
    for i in range(10):
        l10.add(Rv.card("Tool_Map", "t%d" % i, "", "#FFFFFF", 0, "", ""))
    K.check(len(Rv.sorted(l10)) == 10 and not any(str(c[1]).endswith("more finds") for c in Rv.sorted(l10)), "X FIX LgRv.sorted: exactly 10 = no summary card")
    K.check(not Rv.queue(None, None, "t", "s", so, None, False) and not Rv.queue(None, None, "t", "s", JArray(JArray(JString))(0), None, False),
            "X LgRv.queue: no player / no cards = nothing")
    # a PlayerRef stand-in (never touched off the world thread here): allocate without a constructor
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    us = fu.get(None)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    prA = us.allocateInstance(PRc.class_)
    Rv.LAST = None
    K.check(not Rv.queue(None, prA, "T", "S", so, "identify", True) and Rv.LAST is not None and str(Rv.LAST.title) == "T"
            and str(Rv.LAST.back) == "identify" and Rv.LAST.force and len(Rv.LAST.cards) == 4,
            "X LgRv.queue: the opener is made (world null in the harness: not executed)")
    br = CHM()
    Sys.getProperties().put("skyy.bridge", br)
    EIO.BRIDGE = None
    uA = UUID.fromString("00000000-0000-4000-8000-0000000000a1")
    uB = UUID.fromString("00000000-0000-4000-8000-0000000000b2")
    Rv.LAST = None
    K.check(not Rv.show(None, prA, uA, "T", "S", l) and Rv.LAST is not None and len(Rv.LAST.cards) == 10 and not Rv.LAST.force,
            "X LgRv.show: server row on, no settings registry -> the page is queued (sorted, at most 10)")
    Cfg.LG_REVEAL = False
    Rv.LAST = None
    K.check(not Rv.show(None, prA, uA, "T", "S", l) and Rv.LAST is None, "X LgRv.show: luggage.reveal off -> no page")
    Cfg.LG_REVEAL = True

    @JImplements("java.util.function.Function")
    class SettingsOff:
        @JOverride
        def apply(self, a):
            return JBoolean(not (str(a[1]) == "explore.reveal"))
    br.put("settings:fn:get", SettingsOff())
    Rv.LAST = None
    K.check(not Rv.show(None, prA, uA, "T", "S", l) and Rv.LAST is None, "X LgRv.show: the player's explore.reveal off -> no page")
    br.remove("settings:fn:get")
    K.check(not Rv.show(None, prA, uA, "T", "S", AL()), "X LgRv.show: no cards -> no page")
    # ---- LgRvFn (explore:fn:reveal)
    fn = RvF()
    K.check(not fn.apply(None) and not fn.apply(JArray(JObject)([JString("x")])) and not fn.apply(JArray(JObject)([uA, "t", "s", JArray(JString)(["bad"])])),
            "X explore:fn:reveal: bad input / no valid card -> FALSE")
    K.check(not fn.apply(JArray(JObject)([uA, "Identified", "Lv 43", JArray(JString)(["Weapon_Sword_Iron|Iron Sword|Lv 43 - Rare|#FF55FF|1|Skyy_Unid_Bag|Unidentified Sword"]), "identify"])),
            "X explore:fn:reveal: a valid call with no running universe -> FALSE (never throws)")
    K.check(str(RvF.backOk("identify")) == "identify" and RvF.backOk("say hi;") is None and RvF.backOk("") is None and RvF.backOk(JInt(3)) is None,
            "X explore:fn:reveal: the back command is [a-z0-9 ] only")
    # ---- the LgReveal page
    cards = Rv.sorted(l)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    pg = None
    try:
        pg = Rev(prA, "Lost Loot (III)", "Lv 23 - 4 finds", Rv.sorted(AL(l.subList(0, 4))), None)
    except Exception as e:
        K.check(False, "X page: LgReveal constructor (%s)" % e)
    def cmds(b_):
        return " ".join("%s %s %s" % (c.selector, c.text, c.data) for c in b_.getCommands())
    if pg is not None:
        b = UCB()
        ev = UEB()
        pg.build(None, b, ev, None)
        allt = cmds(b)
        K.check(pg.count() == 4 and pg.shown == 0 and not pg.watching, "X page build (no ref): 4 cards, none open, no watch scheduled")
        K.check("SkyyRvC0" in allt and "SkyyRvC3" in allt and "SkyyRvNext" in allt and "SkyyRvAll" in allt and "SkyyRvClose" in allt
                and "SkyyRvBack" not in allt and "Tool_Map" in allt, "X page build: 4 face-down cards, Open next / Open all / Close")
        K.check(pg.step('{"a":"rvnext"}') == 1 and pg.shown == 1 and pg.lastRank == 0 and str(pg.msg) == "", "X page step: Open next flips one (rank 0)")
        K.check(pg.step('{"a":"rvall"}') == 1 and pg.shown == 4 and pg.lastRank == 2 and str(pg.msg) == "Best find: r2",
                "X page step: Open all flips the rest (the best sound rank), the result line names the best find")
        K.check(pg.step('{"a":"rvnext"}') == 1 and pg.shown == 4, "X page step: Open next after all open changes nothing")
        b2 = UCB()
        pg.build(None, b2, UEB(), None)
        a2 = cmds(b2)
        K.check("SkyyRvNext" not in a2 and "SkyyRvClose" in a2 and "#FFFFFF" in a2, "X page build (all open): no Open buttons, Close stays, faces in colour")
        K.check(pg.step('{"a":"rvclose"}') == 2 and pg.step('{"a":"rvback"}') == 0 and pg.step('{"a":"zzz"}') == 0 and pg.step(None) == 0,
                "X page step: Close = 2; Back without a back command / unknown = answer only")
        pg2 = Rev(prA, "Identified!", "Lv 43", Rv.parse(ins), "identify")
        b3 = UCB()
        pg2.build(None, b3, UEB(), None)
        a3 = cmds(b3)
        K.check("SkyyRvBack" in a3 and "SkyyRvClose" not in a3 and pg2.count() == 10 and pg2.step('{"a":"rvback"}') == 3,
                "X page (bridge call): 10 cards (two rows), < Back instead of Close, Back = 3")
        K.check(str(pg2.note(10)).startswith("Open them") and str(pg.note(4)).startswith("Everything"), "X page note lines")
    # ---- the writer + registry + the Sim engine
    EIO.EXEC = Executors.newSingleThreadScheduledExecutor(LIO(9, None))
    d = os.path.join(scratch, "x")
    Reg.DIR = Paths.get(os.path.join(d, "luggage"))
    P("ExpStore").DIR = Paths.get(os.path.join(d, "players"))
    ground = str(Cfg.LG_GROUND).split(",")[0].strip() + "_Test"
    state = {"placed": {}, "log": [], "ground": ground, "given": []}
    Eng.API = sim(state)
    WF = str(CR_.wf("w1"))
    Reg.ready("w1")
    K.check(PW.wait_until(lambda: Reg.W.containsKey(WF)) and Reg.ready("w1"), "X ready (w1)")
    sites = Reg.sites("w1")
    f1 = os.path.join(d, "luggage", WF + ".tsv")
    now = int(time.time() * 1000)

    @JImplements("java.util.function.Function")
    class CoinAdd:
        @JOverride
        def apply(self, a):
            state["log"].append(("coins", str(a[0]), int(a[1])))
            return JLong(1)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    bagstack = []
    try:
        bagstack.append(IS("Weapon_Sword_Iron", JInt(1)))
    except Exception as e:
        # no asset store in a bare JVM: a stand-in stack with its two fields set (only getItemId / getQuantity are read on this path)
        st_ = us.allocateInstance(IS.class_)
        for fn_, v_ in (("itemId", JString("Skyy_Unid_Weapon_Sword_Legendary")), ("quantity", JInt(1))):
            f_ = IS.class_.getDeclaredField(fn_)
            f_.setAccessible(True)
            f_.set(st_, v_)
        bagstack.append(st_)
        print("  note: ItemStack(id, n) needs the asset store (%s) - a stand-in stack is used for the bag path" % str(e)[:80])

    @JImplements("java.util.function.Function")
    class Box:
        @JOverride
        def apply(self, a):
            state["log"].append(("box", int(a[1]), int(a[3])))
            return bagstack[0] if bagstack else None

    @JImplements("java.util.function.Function")
    class Describe:
        @JOverride
        def apply(self, b_):
            return JArray(JString)(["Unidentified Sword", "Lv 21-25 - Legendary - unidentified"])

    @JImplements("java.util.function.Function")
    class Rarity:
        @JOverride
        def apply(self, b_):
            return JString("legendary")
    br.put("coins:fn:add", CoinAdd())
    br.put("gear:fn:box", Box())
    br.put("gear:fn:describe", Describe())
    br.put("gear:fn:rarity", Rarity())
    EIO.BRIDGE = None
    # ---- compass + announce without a world + admin refusals
    K.check(str(Air.dir(0.0, 0.0, 0.0, -10.0)) == "north" and str(Air.dir(0.0, 0.0, 10.0, 0.0)) == "east" and str(Air.dir(0.0, 0.0, 0.0, 10.0)) == "south"
            and str(Air.dir(0.0, 0.0, -10.0, 0.0)) == "west" and str(Air.dir(0.0, 0.0, 7.0, -7.0)) == "north-east", "X LgAir.dir: compass words (north = -z)")
    K.check(Air.announce(None, Fall(1, 65, 1, 5, now, now)) == 0 and str(Air.adminDrop(None, None, None, now)).startswith("-"),
            "X LgAir.announce without a world = 0; adminDrop without a world refused")
    # ---- the timer -> a start -> the fall -> the landing (write-ahead)
    Air.NEXT.clear()
    Air.FALL.clear()
    Air.POS.clear()
    n13, n14 = Core.N[13], Core.N[14]
    K.check(Air.tick(None, "w1", sites, now) == 4 and int(Air.NEXT.get("w1")) == now + 1800 * 1000, "X LgAir.tick: the first pass sets the timer (interval)")
    Air.NEXT.put("w1", JLong(now - 1))
    K.check(Air.tick(None, "w1", sites, now) == 4 and Air.FALL.get("w1") is None, "X LgAir.tick: due but no eligible player -> waits")
    Air.addPos("w1", 0.0, 0.0)
    nl = len(state["log"])
    K.check(Air.tick(None, "w1", sites, now) == 3 and Air.FALL.get("w1") is not None and Core.N[13] == n13 + 1, "X LgAir.tick: a drop starts falling")
    fa = Air.FALL.get("w1")
    dd = (fa.x * fa.x + fa.z * fa.z) ** 0.5
    K.check(31 <= dd <= 66 and fa.lvl == 23 and fa.land == now + 10000 and int(Air.NEXT.get("w1")) == now + 1800 * 1000,
            "X LgAir.start: 32-64 blocks away (%.1f), Lv from SkyyMobs (23), lands after fallSeconds, next drop after the interval" % dd)
    fx0 = [e for e in state["log"][nl:] if e[0] == "fx"]
    K.check(len(fx0) == 1 and fx0[0][1] == "Firework_Mix4" and abs(fx0[0][3] - (fa.y + 40.0)) < 1e-6, "X LgAir.start: the flash high in the sky (Mix4, 40 up)")
    K.check(Air.tick(None, "w1", sites, now + 5000) == 1, "X LgAir.tick: still falling")
    fx1 = [e for e in state["log"] if e[0] == "fx"][-1]
    K.check(abs(fx1[3] - (fa.y + 1.0 + 20.0)) < 1e-6, "X LgAir.fall: the flash one step lower (half way after half the time)")
    K.check(Air.tick(None, "w1", sites, now + 5500) == 1 and Air.active(sites) == 0, "X nothing in the registry while it falls")
    with synchronized(Reg.WLOCK):
        r = Air.tick(None, "w1", sites, now + 11000)
        sd = [s_ for s_ in Reg.snap(sites) if s_.tier == 5]
        K.check(r == 2 and Air.FALL.get("w1") is None and len(sd) == 1 and sd[0].pend == 1 and (sd[0].x, sd[0].y, sd[0].z) not in state["placed"],
                "X LgAir.land: the line is written first (pend 1), no block yet")
    drop = sd[0]
    gen = Reg.seq(WF).get()
    K.check(PW.wait_until(lambda: Reg.done("w1", gen)) and Core.runActs(WF) >= 1, "X the landing act runs after the write")
    K.check(state["placed"].get((drop.x, drop.y, drop.z)) == "Skyy_LootChest_T5" and Core.N[14] == n14 + 1 and drop.pend == 0
            and str(drop.line()) in open(f1, encoding="utf8").read(), "X the supply drop is placed (T5), counted 'landed', on disk")
    land = [e for e in state["log"] if e[0] in ("poof", "snd")][-2:]
    K.check(("snd", "SFX_Wood_Land") in land and any(e[0] == "poof" for e in land), "X the landing puff + thump")
    K.check(Air.active(sites) == 1, "X one drop out")
    Air.NEXT.put("w1", JLong(now))
    Air.addPos("w1", 0.0, 0.0)
    K.check(Air.tick(None, "w1", sites, now + 12000) == 4 and Air.FALL.get("w1") is None, "X perWorld 1: no second drop while one is out")
    # respawn / anyDue / spawnNear ignore drops
    K.check(Core.respawn(None, "w1", sites, float(drop.x), float(drop.z), now + 10 ** 9) == 0 and not Core.anyDue(sites, now + 10 ** 9),
            "X respawn / anyDue ignore supply drops")
    # ---- CLAIM ONCE (supply drop): two players + relog
    K.check(Core.refuse(drop, 5, uA, now) is None, "X refuse: player A may claim the drop")
    with synchronized(Reg.WLOCK):
        ow, ost, oat = str(drop.who), drop.state, drop.lootedAt
        drop.claim(uA, now, 600000)
        drop.state, drop.lootedAt = 1, now
        ga = Reg.saveGen("w1")
        aA = Core.act(1, None, "w1", drop, ga)
        aA.u, aA.at, aA.oldWho, aA.oldState, aA.oldAt, aA.newWho, aA.k = uA, now, ow, ost, oat, drop.who, str(uA)
        aA.hold = 1
        drop.pend = drop.pend + 1
        Reg.later("w1", aA)
        K.check(str(Core.refuse(drop, 5, uB, now)) == "This supply drop was already claimed." and str(Core.refuse(drop, 5, uA, now)) == "This supply drop was already claimed.",
                "X TWO PLAYERS: while A's claim waits, B (and A again) are refused")
        Core.SWEPT.clear()
        Core.sweep(None, "w1", sites, now + 1000)
        K.check(Reg.has(sites, drop) and drop.state == 1, "X the sweep leaves a drop whose claim waits alone")
    g0 = len(state["given"])
    K.check(PW.wait_until(lambda: Reg.done("w1", ga)) and Core.runActs(WF) == 1, "X RELOG: A's claim write landed, the act ran (A is gone)")
    PW.wait_until(lambda: Reg.settled("w1"))
    txt = open(f1, encoding="utf8").read()
    K.check(drop.state == 0 and str(drop.who) == ow and drop.pend == 0 and len(state["given"]) == g0 and str(drop.line()) in txt
            and state["placed"].get((drop.x, drop.y, drop.z)) == "Skyy_LootChest_T5",
            "X RELOG: the claim undone (on disk too), nothing given, the drop still out and claimable")
    K.check(Core.refuse(drop, 5, uB, now + 2000) is None, "X after the undo player B may claim it")
    # B's claim through claimOk (the loot, the cards, the one-claim vanish, the line goes)
    n15, n5 = Core.N[15], Core.N[5]
    drop.claim(uB, now + 2000, 600000)
    drop.state, drop.lootedAt = 1, now + 2000
    gb = Reg.saveGen("w1")
    PW.wait_until(lambda: Reg.done("w1", gb))
    aB = Core.act(1, None, "w1", drop, gb)
    aB.u, aB.at, aB.pr = uB, now + 2000, prA
    Rv.LAST = None
    Core.claimOk(aB, None, None, None)
    PW.wait_until(lambda: Reg.settled("w1"))
    gv = state["given"][g0:]
    coins = [e for e in state["log"] if e[0] == "coins"]
    boxes = [e for e in state["log"] if e[0] == "box"]
    K.check(Core.N[15] == n15 + 1 and coins and 150 * 1.5 <= coins[-1][2] <= 400 * 1.5 and boxes and all(b_[1] == 23 and b_[2] == 4 for b_ in boxes[-2:])
            and 2 <= len([b_ for b_ in boxes]) <= 3, "X claimOk (drop): coins x zone 2 mult (%s), 2-3 bags at Lv 23 with tier 4 odds (%d)" % (coins[-1][2] if coins else None, len(boxes)))
    if bagstack:
        K.check(len(gv) == len(boxes) and Core.N[5] == n5 + len(boxes), "X claimOk (drop): every bag given (%d)" % len(gv))
    K.check(state["placed"].get((drop.x, drop.y, drop.z)) is None and not Reg.has(sites, drop) and drop.state == 2,
            "X claimOk (drop): it vanished and its line is gone (never comes back)")
    txt = open(f1, encoding="utf8").read()
    K.check("\t5\t23\t" not in txt.split("\n", 1)[1], "X claimOk (drop): not in the file either")
    lc = Rv.LAST
    K.check(lc is not None and str(lc.title) == "Supply Drop" and str(lc.sub).startswith("Lv 23 - ") and len(lc.cards) >= 2
            and str(lc.cards[0][1]).startswith("+") and str(lc.cards[0][5]) == "Skyy_LootChest_T5" and str(lc.cards[0][6]) == "Supply Drop",
            "X claimOk (drop): the reveal page queued - coins / XP cards first, covered by the drop's icon")
    if bagstack:
        K.check(str(lc.cards[len(lc.cards) - 1][3]) == "#55FFFF" and str(lc.cards[len(lc.cards) - 1][1]) == "Unidentified Sword"
                and str(lc.cards[len(lc.cards) - 1][4]) == "2", "X claimOk (drop): the Legendary bag card last, in the Legendary colour (rank 2)")
    K.check(str(Core.refuse(None, 5, uA, now)) == "This supply drop is empty." and Air.active(sites) == 0, "X nothing more to claim")
    # a re-read registry (restart) has no drop
    Reg.W.remove(WF)
    sites = Reg.sites("w1")
    K.check(not any(s_.tier == 5 for s_ in Reg.snap(sites)), "X RESTART: the re-read registry has no supply drop (no dupe)")
    # ---- despawn rule
    with synchronized(Reg.WLOCK):
        s5 = Core.spawn(None, "w1", sites, 300, 65, 300, 5, 23, now)
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    K.check(state["placed"].get((300, 65, 300)) == "Skyy_LootChest_T5", "X despawn setup: a drop out")
    Core.SWEPT.clear()
    Core.sweep(None, "w1", sites, now + 599000)
    K.check(Reg.has(sites, s5), "X despawn: kept before despawnSeconds")
    n16 = Core.N[16]
    Core.SWEPT.clear()
    Core.sweep(None, "w1", sites, now + 600000)
    K.check(not Reg.has(sites, s5) and (300, 65, 300) not in state["placed"] and Core.N[16] == n16 + 1,
            "X despawn: gone after despawnSeconds whoever is near (block + line)")
    with synchronized(Reg.WLOCK):
        s6 = Core.spawn(None, "w1", sites, 400, 65, 400, 5, 23, now)
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    Cfg.AIR_ON = False
    Core.SWEPT.clear()
    Core.sweep(None, "w1", sites, now + 1000)
    K.check(not Reg.has(sites, s6) and (400, 65, 400) not in state["placed"], "X switched off: the drop goes at the next sweep")
    K.check(Air.tick(None, "w1", sites, now) == 0 and Air.NEXT.get("w1") is None, "X switched off: no timer")
    Cfg.AIR_ON = True
    with synchronized(Reg.WLOCK):
        s7 = Core.spawn(None, "w1", sites, 500, 65, 500, 5, 23, now)
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    s7.state, s7.who, s7.lootedAt = 1, "%s:%d" % (uA, now), now
    Core.SWEPT.clear()
    Core.sweep(None, "w1", sites, now + 1000)
    K.check(s7.state == 2 and (500, 65, 500) not in state["placed"] and Reg.has(sites, s7), "X a claim saved before a restart: the drop vanishes")
    Core.SWEPT.clear()
    Core.sweep(None, "w1", sites, now + 2000)
    K.check(not Reg.has(sites, s7), "X ... and its line goes at the next sweep")
    PW.wait_until(lambda: Reg.settled("w1"))
    # spawnNear counts exclude drops
    with synchronized(Reg.WLOCK):
        s8 = Core.spawn(None, "w1", sites, 600, 65, 600, 5, 23, now)
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    pp0 = Cfg.LG_PER_PLAYER
    Cfg.LG_PER_PLAYER = 1
    with synchronized(Reg.WLOCK):
        sn = Core.spawnNear(None, "w1", sites, 600.0, 600.0, now)
    K.check(sn is not None and sn.tier != 5, "X spawnNear: a drop near the player does not count against Lost Loot's per-player cap")
    Cfg.LG_PER_PLAYER = pp0
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    # ---- CLAIM ONCE (Lost Loot tier 1)
    with synchronized(Reg.WLOCK):
        s1 = Core.spawn(None, "w1", sites, 700, 65, 700, 1, 5, now)
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    Core.HOUR.clear()
    K.check(Core.refuse(s1, 1, uA, now) is None, "X Lost Loot: A may claim")
    s1.claim(uA, now, 1800000)
    s1.state, s1.lootedAt = 1, now
    g1 = Reg.saveGen("w1")
    PW.wait_until(lambda: Reg.done("w1", g1))
    a1 = Core.act(1, None, "w1", s1, g1)
    a1.u, a1.at, a1.pr = uA, now, prA
    Core.capAdd(uA, now)
    K.check(str(Core.refuse(s1, 1, uB, now)) == "This Lost Loot was already claimed." and str(Core.refuse(s1, 1, uA, now)) == "This Lost Loot was already claimed.",
            "X Lost Loot: claimed once - B and A refused (share 0)")
    Rv.LAST = None
    Core.claimOk(a1, None, None, None)
    PW.wait_until(lambda: Reg.settled("w1"))
    K.check(s1.state == 2 and Reg.has(sites, s1) and (700, 65, 700) not in state["placed"] and Rv.LAST is not None and str(Rv.LAST.title) == "Lost Loot (I)",
            "X Lost Loot: vanished, its line kept (comes back later), the reveal page queued with its name")
    K.check(str(Core.refuse(s1, 1, uA, now)) == "This Lost Loot is empty.", "X Lost Loot: gone = empty")
    # ---- FIX admin tools: luggage tier <1-4> (placeNear with a chosen tier), luggage clear (clearNear), reveal (the sample through the bridge)
    K.check(str(Core.adminTier(None, None, None, now, "9")).startswith("-The tier is") and str(Core.adminTier(None, None, None, now, "x")).startswith("-The tier is")
            and str(Core.adminTier(None, None, None, now, "4")) == "-No world" and str(Core.adminHere(None, None, None, now)) == "-No world",
            "X FIX adminTier: 1-4 only; a valid tier reaches adminPlace (no world here)")
    pl = []
    for t_ in (4, 3, 2, 1):
        with synchronized(Reg.WLOCK):
            msg = str(Core.placeNear(None, "w1", sites, 2000.0 + 100 * t_, 2000.0, now, t_))
        pl.append((t_, msg))
        PW.wait_until(lambda: Reg.settled("w1"))
        Core.runActs(WF)
    names_ = {4: "Lost Treasure (IV)", 3: "Lost Loot (III)", 2: "Lost Loot (II)", 1: "Lost Loot (I)"}
    K.check(all(m_.startswith("+Placed " + names_[t_]) for t_, m_ in pl), "X FIX placeNear: the chosen tier is placed (%s)" % [m_[:30] for _t, m_ in pl])
    near = [s_ for s_ in Reg.snap(sites) if abs(s_.x - 2400) <= 12 and abs(s_.z - 2000) <= 12]
    K.check(len(near) == 1 and near[0].tier == 4 and state["placed"].get((near[0].x, near[0].y, near[0].z)) == "Skyy_LootChest_T4",
            "X FIX placeNear: tier IV on disk + placed (T4)")
    nx_, ny_, nz_ = near[0].x, near[0].y, near[0].z
    with synchronized(Reg.WLOCK):
        m2 = str(Core.placeNear(None, "w1", sites, 2400.0, 2000.0, now, 0))
    K.check(m2.startswith("-No free spot") and "luggage clear" in m2, "X FIX placeNear: a second one next to it is refused and names 'luggage clear'")
    Air.FALL.put("w1", Fall(2402, 65, 2003, 23, now, now + 10000))
    Air.FALL.put("w2", Fall(2402, 65, 2003, 23, now, now + 10000))
    nsite = len(Reg.snap(sites))
    with synchronized(Reg.WLOCK):
        cm = str(Air.clearNear(None, "w1", sites, 2400.0, 2000.0, 48.0))
    PW.wait_until(lambda: Reg.settled("w1"))
    disk = [l_ for l_ in open(f1, encoding="utf8").read().split("\n")[1:] if l_.startswith("%d\t%d\t%d\t" % (nx_, ny_, nz_))]
    K.check(cm.startswith("+Cleared 1 ") and "falling" in cm and Air.FALL.get("w1") is None and Air.FALL.get("w2") is not None
            and len(Reg.snap(sites)) == nsite - 1 and (nx_, ny_, nz_) not in state["placed"] and not disk,
            "X FIX clearNear: the Lost Treasure within 48 goes (block + line, on disk), the falling drop here stops, other worlds / far sites stay: %s" % cm)
    Air.FALL.remove("w2")
    with synchronized(Reg.WLOCK):
        m3 = str(Core.placeNear(None, "w1", sites, 2400.0, 2000.0, now, 4))
    PW.wait_until(lambda: Reg.settled("w1"))
    Core.runActs(WF)
    K.check(m3.startswith("+Placed Lost Treasure"), "X FIX after clear the spot is free again")
    sx = [s_ for s_ in Reg.snap(sites) if s_.tier == 4 and abs(s_.x - 2400) <= 12][0]
    sx.pend = 1
    with synchronized(Reg.WLOCK):
        cw = str(Air.clearNear(None, "w1", sites, 2400.0, 2000.0, 48.0))
    K.check("still saving" in cw and Reg.has(sites, sx), "X FIX clearNear: a site whose save is pending is left alone")
    sx.pend = 0
    with synchronized(Reg.WLOCK):
        Air.clearNear(None, "w1", sites, 2400.0, 2000.0, 48.0)
    PW.wait_until(lambda: Reg.settled("w1"))
    K.check(str(Air.adminClear(None, None, None)) == "-No world" and str(RvF.sample(None)) == "-No player", "X FIX adminClear / sample refusals")
    sc = RvF.sampleCards()
    psc = Rv.parse(sc)
    K.check(len(psc) == 3 and [str(c[5]) for c in psc] == ["Skyy_Unid_Bag_Unique", "Skyy_Unid_Bag_Rare", "Skyy_Unid_Bag_Legendary"]
            and [str(c[4]) for c in psc] == ["0", "1", "2"] and str(psc[2][3]) == "#55FFFF" and str(psc[1][3]) == "#FF55FF"
            and all(any(n.endswith("/" + str(c[0]) + ".json") and n.startswith("Server/Item/Items/") for n in an) for c in psc),
            "X FIX reveal sample: 3 vanilla items covered by SkyyGear's Unique / Rare / Legendary bags, rarity colours, ranks 0-2")
    K.check(not RvF().apply(JArray(JObject)([uA, "Identified (sample)", "x", sc, "explore"])) and str(RvF.backOk("explore")) == "explore",
            "X FIX reveal sample: the bridge call with back 'explore' (no universe here = FALSE, never throws)")
    src = open(os.path.join(HERE, "build_skyyexploration_0.2.8.py"), encoding="utf8").read()
    javas = re.findall(r'(?:say\(|return "[-+=]|hlp=|crow\("[a-zA-Z.]+", |cpart\("[a-zA-Z.]+", )"?([^"]*)', src)
    old = [j for j in javas if re.search(r"\b[Ll]uggage\b(?!\.)", j) and "/exploreadmin luggage" not in j]
    K.check(not old and '("luggage", "Lost Loot")' in src, "X FIX rename: no player / admin text or Server Setup row says 'luggage' (tab 'Lost Loot'): %s" % old[:4])
    st = str(Core.statsText())
    K.check("supply drops on" in st and "landed" in st and "reveal pages" in st and st.startswith("Lost Loot on"), "X statsText: the drop counters")
    EIO.STOPPING = True
    EIO.stop()
    K.save()


def loader_for(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


# ====================================================================================================== D: start twice on live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Paths, Executors, UUID = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors"), JClass("java.util.UUID")
    h0 = HK.tree_hash(home)
    pd = os.path.join(home, "players")
    keys = sorted(n[:-11] for n in os.listdir(pd) if n.endswith(".properties")) if os.path.isdir(pd) else []
    for start in (1, 2):
        Lo, Ln = loader_for(OLD_JAR), loader_for(jar)
        So, Sn = JClass(PKG + "ExpStore", loader=Lo), JClass(PKG + "ExpStore", loader=Ln)
        for S_ in (So, Sn):
            S_.DIR = Paths.get(pd)
        diff = []
        for k in keys:
            uu = UUID.fromString(k[:36]) if len(k) >= 36 else UUID.randomUUID()
            So.dataK(k, uu)
            Sn.dataK(k, uu)
            po, pn = So.snap(k), Sn.snap(k)
            if (po is None) != (pn is None) or (po is not None and not po.equals(pn)):
                diff.append(k)
        K.check(not diff and len(keys) > 0, "D start %d: %d live records: 0.2.8 snap() = 0.2.7 snap() (diffs %s)" % (start, len(keys), diff[:3]))
        Reg, EIO, LIO = JClass(PKG + "LgReg", loader=Ln), JClass(PKG + "ExpIO", loader=Ln), JClass(PKG + "LgIO", loader=Ln)
        ld = os.path.join(home, "luggage")
        Reg.DIR = Paths.get(ld)
        EIO.STOPPING = False
        EIO.EXEC = Executors.newSingleThreadScheduledExecutor(LIO(9, None))
        worlds = []
        for n in (sorted(os.listdir(ld)) if os.path.isdir(ld) else []):
            if n.endswith(".tsv"):
                hd = open(os.path.join(ld, n), encoding="utf8").readline()
                worlds.append(hd.split(" - world ", 1)[1].rsplit(": x y z", 1)[0])
        for wn in worlds:
            Reg.ready(wn)
        K.check(PW.wait_until(lambda: all(Reg.W.containsKey(JClass(PKG + "ChestReg", loader=Ln).wf(w)) for w in worlds)),
                "D start %d: every luggage registry read on the writer (%s)" % (start, worlds))
        for wn in worlds:
            Reg.save(wn)
        EIO.STOPPING = True
        EIO.stop()
        h1 = HK.tree_hash(home)
        K.check(h1 == h0, "D start %d: every file byte-identical (records read twice, registries saved back): %s"
                % (start, sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))[:8]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyExploration"))
