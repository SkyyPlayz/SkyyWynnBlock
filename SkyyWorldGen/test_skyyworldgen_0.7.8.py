"""Harness for SkyyWorldGen 0.7.8 (Balance P6 part A: zone spawns - the remap pass of the zone islands mask; tools/worldgen_0_7_8_patch.py).
Build first:
    python tools/worldgen_0_7_8_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.8.py

    python SkyyWorldGen/test_skyyworldgen_0.7.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.7 -> 0.7.8: exactly the EXPECTED members differ (WgZ2Isles: the RM_* table + rm* methods + remap, maskWith calls it,
               statusText shows it; WgCfg apply / defaults; WgWeather.tick logs it; version texts); no class added
  P    probe    P6-0 on Assets.zip (cached copy, read only): vanilla world gen places wild crops as per-stage state ids
               (*Plant_Crop_<C>_Block_State_Definitions_<S>, counted per zone folder) and every such id it places is in the remap table;
               every table id exists (item / its state); no ore id in the table
  T    table    the REAL WgZ2Isles.rmBuild on preset ids (RM_IDS = 1000 + i; the asset map is not loaded in a bare JVM): every zone's code
               for every id = an independent python mirror of the rule (window 3z + 2, mushrooms off in Zones 1-3, Zone 5 own-crop rule,
               herbs to the highest in-window grade, trees to the zone's top own species; stage / part kept, nearest lower stage);
               only ids above the window are touched (mushrooms apart); the auto texts; zones.spawnWindow -1 = off; own lists; junk;
               (fix, critic) "auto,Pumpkin>Carrot" = the rule + the pair on top, "auto,Turnip>keep" drops one swap of the rule, junk
               after auto skipped, the description says "auto + own pairs"
  R    remap    the REAL remap() on synthetic GeneratedChunks (32 x 32 columns, ids set through the real GeneratedBlockChunk.setBlock):
               per zone 64 chunks of wild crops (every crop, its states), mushrooms (surface + cave), herbs, trees (rotation 2, a filler),
               and stone / ore stand-ins: after the pass no crop / herb / tree id above the window in Zones 1-4, no Mushroom id in
               Zones 1-3 (caves too), Zone 4-5 keep mushrooms, Zone 5 own-crop share 70 % +- 10 of its patches, one crop per 8 x 8 patch,
               stage kept, rotation kept on trees, the upper (filler) part of a plant -> air, ores / stone / unknown ids identical,
               block states dropped on a swapped voxel; the same chunk twice = the same result (deterministic); island-less columns
               (zone -1) untouched; a chunk with no table id = nothing changed
  S    setup    WgCfg.apply on hand-edited properties (clamps, missing keys keep the defaults, remap texts); the Server Setup rows through
               the config kit's console path (field + file line); START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen (WgCfg.load,
               WgStore.read): no file changed, the 0.7.8 defaults (its file has no zones.spawnWindow line); rmLogOnce without the asset map
               = no log, with preset ids = one line
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED here): that the server's BlockType asset map resolves every state id (the first 5 s tick logs
"... N of M block ids loaded"; the smoke test reads it), how the swapped plants look / grow in game, multi-block plants (only the base kept).
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, zipfile, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION = "0.7.8"
OLD_VERSION = "0.7.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp6afix2", "wg")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
LIVE_WG = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyWorldGen")
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyWorldGenPlugin": ["~m setup"], "WgStore": ["~m markCreated"],
    "WgCfg": ["~m apply", "~m load", "~m reloadAll"],
    "WgWeather": ["~m tick"],
    "WgZ2Isles": ["+f RM_NAMES", "+f RM_FAMOF", "+f RM_KEY", "+f RM_FAM", "+f RM_KIND", "+f RM_TIER", "+f RM_HERB", "+f RM_OWN", "+f RM_TOP",
                  "+f RM_SW", "+f RM_Z5", "+f RM_T1", "+f RM_T2", "+f RM_T3", "+f RM_T4", "+f RM_T5", "+f RM_MAP", "+f RM_OWNT", "+f RM_SKI",
                  "+f RM_ANY", "+f RM_KF", "+f RM_SIG", "+f RM_DESC", "+f RM_IDS", "+f RM_LOADED", "+f RM_LOGGED", "+f RM_SWAP", "+f RM_AIR",
                  "+f RM_CHUNKS", "+m rmFam", "+m rmOwn", "+m rmTarget", "+m rmAutoCode", "+m rmParse", "+m rmSig", "+m rmBuild", "+m rmCheck",
                  "+m remap", "+m rmText", "+m rmLogOnce", "~m maskWith", "~m statusText", "~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            ok = "manifest.json" in got and all(n in ("manifest.json", LANG) or n.endswith("/instance.bson") for n in got)
            if ok and LANG in got:      # server.lang: only its header comment names the version
                a = zipfile.ZipFile(OLD_JAR).read(LANG).decode("utf8").splitlines()
                b = zipfile.ZipFile(HK.arg("--jar", JAR)).read(LANG).decode("utf8").splitlines()
                ok = len(a) == len(b) and [i for i in range(len(a)) if a[i] != b[i]] == [0] and a[0].replace(OLD_VERSION, VERSION) == b[0]
            return self.check(ok, "C: non-class entries changed = manifest.json + instance templates + server.lang header (version text only): %s" % sorted(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


# ------------------------------------------------------------------------------------------- the python mirror of the rule (independent)
class Table(object):
    def __init__(self, I):
        self.names = [str(x) for x in I.RM_NAMES]
        self.famof = [int(x) for x in I.RM_FAMOF]
        self.key = [int(x) for x in I.RM_KEY]
        self.fam = [str(x) for x in I.RM_FAM]
        self.kind = [int(x) for x in I.RM_KIND]
        self.tier = [int(x) for x in I.RM_TIER]
        self.herb = [int(x) for x in I.RM_HERB]
        self.own = [int(x) for x in I.RM_OWN]
        self.top = [int(x) for x in I.RM_TOP]

    def fi(self, n):
        return self.fam.index(n)

    def auto(self, z, f, sw=2):
        """target family + 1 / -1 air / -2 own / -3 Zone 5 / 0 keep - written from the spec, not from the Java"""
        if sw < 0:
            return 0
        k, t = self.kind[f], self.tier[f]
        if z == 4:
            return -3 if (k == 0 and f not in self.own[12:15]) else 0
        if k == 1:                                   # mushrooms: gone in Zones 1-3, kept from Zone 4 (exempt from the window)
            return -1 if z < 3 else 0
        w = 3 * (z + 1) + sw
        if t <= w:
            return 0
        if k == 0:
            return -2
        if k == 2:
            c = [g for g in range(len(self.fam)) if self.kind[g] == 2 and self.herb[g] == self.herb[f] and self.tier[g] <= w]
            return (max(c, key=lambda g: self.tier[g]) + 1) if c else -1
        return self.top[z] + 1 if self.top[z] not in (-1, f) else 0

    def target(self, ids, f, key):
        mine = [(self.key[i], ids[i]) for i in range(len(self.names)) if self.famof[i] == f and ids[i] > 0]
        for k2, b in mine:
            if k2 == key:
                return b
        if 1 <= key <= 15:
            st = sorted((k2, b) for k2, b in mine if 1 <= k2 <= 15)
            lo = [b for k2, b in st if k2 <= key]
            hi = [b for k2, b in st if k2 > key]
            if lo:
                return lo[-1]
            if hi:
                return hi[0]
        if 40 <= key <= 49:                          # a leaf variant -> the plain leaves; a family without leaves: left alone
            pl = [b for k2, b in mine if k2 == 40]
            return pl[0] if pl else -1
        return mine[0][1] if mine else -1


def jvm_and_table(jar, verify=True):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=verify)
    from jpype import JClass
    I = JClass(PKG + "WgZ2Isles")
    return I, Table(I)


def preset(I, n):
    import jpype
    I.RM_IDS = jpype.JArray(jpype.JInt)([1000 + i for i in range(n)])
    I.RM_SIG = ""
    I.rmCheck()


# ------------------------------------------------------------------------------------------- P: the probe on Assets.zip
def run_probe(out, jar, scratch, _home):
    K = HK.Child(out)
    I, T = jvm_and_table(jar)
    import serverjar as SJ
    with zipfile.ZipFile(SJ.assets_zip()) as az:
        nl = az.namelist()
        items = dict((n.rsplit("/", 1)[1][:-5], n) for n in nl if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        bad = []
        for nm in T.names:
            if nm.startswith("*"):
                m = re.match(r"^\*(.+)_State_Definitions_(.+)$", nm)
                base, st = m.group(1), m.group(2)
                j = json.loads(az.read(items[base]).decode("utf-8-sig")) if base in items else {}
                if st not in (((j.get("BlockType") or {}).get("State") or {}).get("Definitions") or {}):
                    bad.append(nm)
            elif nm not in items:
                bad.append(nm)
        K.check(not bad, "P every remap table id exists in Assets.zip (items / their growth states): %d ids, missing %s" % (len(T.names), bad[:5]))
        K.check(not [n for n in T.names if "Ore" in n or n.startswith("Rock_")], "P no ore / rock id in the table (Skyy: ores unchanged)")
        per = collections.defaultdict(collections.Counter)
        for n in nl:
            if n.startswith("Server/World/Default/Zones/") and n.endswith(".json"):
                zk = re.match(r"(Zone\d)", n.split("/")[4])
                zk = zk.group(1) if zk else "Shared"
                for m in re.findall(r'"(\*?Plant_Crop_[A-Za-z]+_Block(?:_State_Definitions_[A-Za-z0-9]+)?)"', az.read(n).decode("utf-8", "replace")):
                    per[zk][m] += 1
    ladder = set(T.fam[f] for f in range(len(T.fam)) if T.kind[f] == 0)
    states = sorted(set(m for c in per.values() for m in c if m.startswith("*")))
    lstates = [s for s in states if re.match(r"^\*Plant_Crop_([A-Za-z]+)_Block_", s).group(1) in ladder]
    K.check(len(lstates) >= 15 and all(s in T.names for s in lstates),
            "P6-0 vanilla world gen places wild crops as per-stage state ids (%d different ladder-crop ids, e.g. %s) - every one is in the table; "
            "not ladder crops (left alone): %s" % (len(lstates), lstates[:3], sorted(set(states) - set(lstates))))
    z1 = per.get("Zone1", {})
    K.check(any("Pumpkin" in s for s in z1) and any("Potato" in s for s in z1) and any("Wheat_Block_State" in s for s in z1),
            "P Zone 1 vanilla land places Wheat, Pumpkin (T7) and Potato (T13) state ids (the ones the window swaps): %s" % sorted(z1)[:6])
    print("P vanilla wild crop ids per zone folder:", dict((k, sum(v.values())) for k, v in per.items()))
    K.save()


# ------------------------------------------------------------------------------------------- T: the table
def run_table(out, jar, scratch, _home):
    K = HK.Child(out)
    I, T = jvm_and_table(jar)
    from jpype import JString
    n = len(T.names)
    ids = [1000 + i for i in range(n)]
    preset(I, n)
    K.eq(int(I.RM_LOADED), n, "T rmBuild on preset ids: all %d loaded" % n)
    K.eq([T.fam[f] for f in T.own], ["Wheat", "Lettuce", "Carrot", "Corn", "Cauliflower", "Turnip", "Pumpkin", "Aubergine", "Tomato",
                                    "Chilli", "Cotton", "Rice", "Potato", "Onion", "Mushroom"], "T own crops per zone = the ladder's three")
    K.eq([T.fam[f] if f >= 0 else None for f in T.top], ["Maple", "Gumboab", "Redwood", "Sallow", None], "T the top own tree per zone")
    bad = []
    touched_above = []
    for z in range(5):
        m = I.RM_MAP[z]
        for i in range(n):
            f = T.famof[i]
            c = T.auto(z, f)
            want = 0
            if c > 0:
                want = T.target(ids, c - 1, T.key[i])
                if want <= 0 or want == ids[i]:
                    want = 0
            elif c in (-2, -3):
                want = c if T.kind[f] == 0 else 0
            elif c == -1:
                want = -1
            got = 0 if m is None else int(m[ids[i]])
            if got != want:
                bad.append((z + 1, T.names[i], got, want))
            if got != 0 and z < 4 and T.kind[f] != 1 and T.tier[f] <= 3 * (z + 1) + 2:
                touched_above.append((z + 1, T.names[i]))
    K.check(not bad, "T every zone's code for every id = the python mirror (%d checks): %s" % (5 * n, bad[:6]))
    K.check(not touched_above, "T only ids above the window are touched (mushrooms apart): %s" % touched_above[:5])
    # the own-crop targets keep the stage: Pumpkin StageFinal -> each own crop's StageFinal; Stage3 -> Wheat Stage3, Lettuce Stage2 (none 3)
    O = I.RM_OWNT
    st = lambda c, s: ids[T.names.index("*Plant_Crop_%s_Block_State_Definitions_%s" % (c, s))]
    K.eq([int(O[0][k][15]) for k in range(3)], [st("Wheat", "StageFinal"), st("Lettuce", "StageFinal"), st("Carrot", "StageFinal")],
         "T Zone 1 own pick: StageFinal -> the own crop's StageFinal")
    K.eq([int(O[0][k][3]) for k in range(3)], [st("Wheat", "Stage3"), st("Lettuce", "Stage2"), st("Carrot", "Stage2")],
         "T Stage3 -> Wheat Stage3, Lettuce / Carrot Stage2 (their nearest lower stage)")
    K.eq(int(O[4][2][15]), ids[T.names.index("Plant_Crop_Mushroom_Cap_Brown")], "T Zone 5 own Mushroom = the collection's Cap_Brown")
    # trees keep their part
    tr = lambda sp, part: ids[T.names.index("Wood_%s_%s" % (sp, part))]
    K.eq(int(I.RM_MAP[3][tr("Crystal", "Branch_Long")]), tr("Sallow", "Branch_Long"), "T Zone 4 Crystal Branch_Long -> Sallow Branch_Long")
    K.eq(int(I.RM_MAP[3][ids[T.names.index("Plant_Leaves_Crystal")]]), ids[T.names.index("Plant_Leaves_Sallow")], "T ... its leaves -> Sallow leaves")
    K.check(I.RM_MAP[3][ids[T.names.index("Plant_Crop_Mushroom_Glowing_Blue")]] == 0 and I.RM_MAP[2][ids[T.names.index("Plant_Crop_Mushroom_Glowing_Blue")]] == -1,
            "T a glowing (cave) mushroom: removed in Zone 3, kept in Zone 4")
    K.eq(int(I.RM_MAP[0][ids[T.names.index("Plant_Crop_Health3")]]), ids[T.names.index("Plant_Crop_Health2")], "T Zone 1 Health3 (T8) -> Health2 (T5)")
    # the settings
    I.RM_SW = -1
    I.rmCheck()
    K.check(all(I.RM_MAP[z] is None for z in range(5)), "T zones.spawnWindow -1 = off in every zone")
    I.RM_SW = 0
    I.rmCheck()
    K.check(int(I.RM_MAP[0][ids[T.names.index("*Plant_Crop_Corn_Block_State_Definitions_StageFinal")]]) == -2,
            "T leeway 0: Zone 1 = T3, so Corn (T4) is swapped too (live)")
    I.RM_SW = 2
    I.RM_T1 = JString("Pumpkin>Carrot, Mushroom>air,Nope>own,Wheat>Nothing,junk")
    I.rmCheck()
    m0 = I.RM_MAP[0]
    K.check(int(m0[st("Pumpkin", "StageFinal")]) == st("Carrot", "StageFinal") and int(m0[ids[T.names.index("Plant_Crop_Mushroom_Cap_Red")]]) == -1
            and int(m0[st("Potato", "StageFinal")]) == 0 and int(m0[st("Wheat", "StageFinal")]) == 0,
            "T an own list for Zone 1 replaces the rule: Pumpkin>Carrot (stage kept), Mushroom>air, nothing else; 3 junk entries skipped")
    I.RM_T1 = JString("off")
    I.rmCheck()
    K.check(I.RM_MAP[0] is None and I.RM_MAP[1] is not None, "T zones.remap.1 = off: no swaps in Zone 1 only")
    I.RM_T1 = JString("")
    I.rmCheck()
    K.check(I.RM_MAP[0] is None, "T empty = off")
    # fix (critic): auto + own pairs on top
    I.RM_T1 = JString("auto")
    I.rmCheck()
    ma = list(I.RM_MAP[0])
    I.RM_T1 = JString("auto, Pumpkin>Carrot,Turnip>keep,junk")
    I.rmCheck()
    mp = list(I.RM_MAP[0])
    tur = [ids[i] for i, n in enumerate(T.names) if "Plant_Crop_Turnip" in n]
    pum = st("Pumpkin", "StageFinal")
    pumf = [ids[i] for i, n in enumerate(T.names) if "Plant_Crop_Pumpkin" in n]
    K.check(ma[pum] == -2 and mp[pum] == st("Carrot", "StageFinal"), "T auto,Pumpkin>Carrot: Pumpkin was own (auto), now Carrot (stage kept): %r -> %r" % (ma[pum], mp[pum]))
    K.check(tur and all(ma[b] == -2 for b in tur) and all(mp[b] == 0 for b in tur), "T auto,Turnip>keep: the %d Turnip ids swapped by auto are kept: %r -> %r"
            % (len(tur), [ma[b] for b in tur], [mp[b] for b in tur]))
    dif = [(T.names[ids.index(b)] if b in ids else b, ma[b], mp[b]) for b in range(len(ma)) if b not in pumf and b not in tur and mp[b] != ma[b]]
    K.check(not dif and int(mp[ids[T.names.index("Plant_Crop_Mushroom_Cap_Red")]]) == -1,
            "T auto + pairs: every other id as the rule (mushrooms still air; %d swaps), junk skipped: %s" % (sum(1 for b in range(len(ma)) if ma[b] != 0), dif[:4]))
    K.check("Zone 1 auto + own pairs" in str(I.RM_DESC), "T the description names auto + own pairs: %s" % str(I.RM_DESC)[:80])
    # fix 2 (critic): a trailing comma / a space before the comma / upper case stay auto (never "own list (0 ids)")
    for tx_, pairs in (("auto,", False), ("auto , ", False), ("AUTO", False), ("auto ,Pumpkin>Carrot", True)):
        I.RM_T1 = JString(tx_)
        I.rmCheck()
        mq = list(I.RM_MAP[0]) if I.RM_MAP[0] is not None else None
        same_rest = mq is not None and all(mq[b] == ma[b] for b in range(len(ma)) if not (pairs and b in pumf))
        K.check(same_rest and (mq[pum] == st("Carrot", "StageFinal")) == pairs
                and ("Zone 1 auto + own pairs" in str(I.RM_DESC)) == pairs and "Zone 1 auto" in str(I.RM_DESC),
                "T fix2 %r = the auto rule%s: %s" % (tx_, " + the pair" if pairs else "", str(I.RM_DESC)[:60]))
    I.RM_T1 = JString("autox")
    I.rmCheck()
    K.check("Zone 1 own list" in str(I.RM_DESC), "T fix2 'autox' is not auto (an own list, junk skipped): %s" % str(I.RM_DESC)[:60])
    I.RM_T1 = JString("Turnip>keep")
    I.rmCheck()
    K.check(I.RM_MAP[0] is None, "T an own list of only keep = no swaps in Zone 1")
    I.RM_T1 = JString("auto")
    I.rmCheck()
    K.check("Zone 1 auto" in str(I.RM_DESC) and "Zone 5 auto" in str(I.RM_DESC), "T the description: %s" % str(I.RM_DESC)[:120])
    K.check(int(I.rmFam(JString("pumpkin"))) == T.fi("Pumpkin") and int(I.rmFam(JString("Fig_Blue"))) == T.fi("Fig_Blue") and int(I.rmFam(JString("x"))) == -1,
            "T family names in any case")
    K.save()


# ------------------------------------------------------------------------------------------- R: the remap on synthetic chunks
def run_remap(out, jar, scratch, _home):
    K = HK.Child(out)
    I, T = jvm_and_table(jar)
    from jpype import JClass, JArray, JInt
    n = len(T.names)
    ids = [1000 + i for i in range(n)]
    preset(I, n)
    GCN = "com.hypixel.hytale.server.core.universe.world.worldgen.GeneratedChunk"
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(B.SERVER_JAR)
    ct = pool.makeClass(GCN + "Skyy078", pool.get(GCN))
    CtM, CtC, CtF = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
    ct.addField(CtF.make("public java.util.HashMap st = new java.util.HashMap();", ct))
    ct.addField(CtF.make("public int cleared = 0;", ct))
    ct.addConstructor(CtC.make("public GeneratedChunkSkyy078() { super(); }", ct))
    ct.addMethod(CtM.make("public com.hypixel.hytale.component.Holder getState(int x, int y, int z) { return (com.hypixel.hytale.component.Holder) this.st.get(x + \",\" + y + \",\" + z); }", ct))
    ct.addMethod(CtM.make("public void setState(int x, int y, int z, com.hypixel.hytale.component.Holder h) { if (h == null) { if (this.st.remove(x + \",\" + y + \",\" + z) != null) this.cleared++; } else this.st.put(x + \",\" + y + \",\" + z, h); }", ct))
    GC = JClass(ct.toClass(JClass(GCN).class_))
    Holder = JClass("com.hypixel.hytale.component.Holder")
    us = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    us.setAccessible(True)
    U = us.get(None)
    crops = [T.names[i] for i in range(n) if T.kind[T.famof[i]] == 0]
    mush = [T.names[i] for i in range(n) if T.kind[T.famof[i]] == 1]
    herbs = [T.names[i] for i in range(n) if T.kind[T.famof[i]] == 2]
    trees = [T.names[i] for i in range(n) if T.kind[T.famof[i]] == 3 and T.key[i] < 40]
    ID = dict(zip(T.names, ids))
    STONE, ORE, UNK = 7, 101, 999

    def build(bx, bz, zone_of):
        g = GC()
        b = g.getBlockChunk()
        for lx in range(32):
            for lz in range(32):
                x, z = bx + lx, bz + lz
                b.setBlock(lx, 90, lz, STONE, 0, 0)
                b.setBlock(lx, 60, lz, ORE if (x + z) % 5 == 0 else STONE, 0, 0)
                h = (x * 7349 + z * 9151) & 1023
                b.setBlock(lx, 91, lz, ID[crops[h % len(crops)]], 0, 0)                 # a wild crop on every column
                if h % 3 == 0:
                    b.setBlock(lx, 61, lz, ID[mush[h % len(mush)]], 0, 0)               # a cave mushroom
                if h % 4 == 0:
                    b.setBlock(lx, 92, lz, ID[herbs[h % len(herbs)]], 0, 0)
                if h % 6 == 0:
                    b.setBlock(lx, 100, lz, ID[trees[h % len(trees)]], 2, 0)             # a tree part, rotation 2
                if h % 11 == 0:
                    b.setBlock(lx, 93, lz, ID[crops[h % len(crops)]], 0, 1)              # the upper (filler) part of a plant
                if h % 13 == 0:
                    b.setBlock(lx, 95, lz, UNK, 0, 0)
        zon = JArray(JInt)([zone_of(i // 34 - 1, i % 34 - 1) for i in range(34 * 34)])
        return g, b, zon

    def snap(b):
        return [[[int(b.getBlock(lx, y, lz)) for y in (60, 61, 90, 91, 92, 93, 95, 100)] for lz in range(32)] for lx in range(32)]

    def fam_of(bid):
        return T.famof[bid - 1000] if 1000 <= bid < 1000 + n else -1
    SPOTS = [((i * 37) % 23 * 32 - 320, (i * 53) % 19 * 32 - 288) for i in range(64)]
    for z in range(5):
        w = 3 * (z + 1) + 2
        above, mleft, mkept, rot_bad, fill_bad, keep_bad, patch_mixed, st_bad = 0, 0, 0, 0, 0, 0, 0, 0
        own_p, tot_p = 0, 0
        for bx, bz in SPOTS:
            g, b, zon = build(bx, bz, lambda a, c: z)
            # a block state on a few crops (dropped when swapped)
            hol = U.allocateInstance(Holder.class_)
            g.st.put("0,91,0", hol)
            before = snap(b)
            I.remap(g, b, bx, bz, zon)
            after = snap(b)
            patches = collections.defaultdict(set)
            for lx in range(32):
                for lz in range(32):
                    bb, aa = before[lx][lz], after[lx][lz]
                    for yi in (0, 2, 6):                                # ore, stone, unknown untouched
                        if bb[yi] != aa[yi]:
                            keep_bad += 1
                    for yi in (1, 3, 4, 7):
                        f = fam_of(aa[yi])
                        if f >= 0 and z < 4 and T.kind[f] != 1 and T.tier[f] > w:
                            above += 1
                        if f >= 0 and T.kind[f] == 1:
                            if z < 3:
                                mleft += 1
                            else:
                                mkept += 1
                    if bb[7] != 0 and aa[7] != 0 and aa[7] != bb[7] and int(b.getRotationIndex(lx, 100, lz)) != 2:
                        rot_bad += 1
                    if bb[5] != 0 and fam_of(bb[5]) >= 0 and aa[5] not in (0, bb[5]):
                        fill_bad += 1
                    fb, fa = fam_of(bb[3]), fam_of(aa[3])
                    if aa[3] != bb[3] and aa[3] > 0:
                        patches[((bx + lx) >> 3, (bz + lz) >> 3)].add(fa)
                        if T.key[aa[3] - 1000] != T.key[bb[3] - 1000] and T.key[bb[3] - 1000] in [T.key[i] for i in range(n) if T.famof[i] == fa]:
                            st_bad += 1
                    if z == 4 and T.kind[fb] == 0:
                        tot_p += 1
                        if aa[3] != bb[3] or fb in T.own[12:15]:
                            own_p += 1
            patch_mixed += sum(1 for v in patches.values() if len(v) > 1)
            if (bx, bz) == SPOTS[0]:
                K.check(not g.st.containsKey("0,91,0") or before[0][0][3] == after[0][0][3], "R Zone %d: the block state of a swapped voxel is dropped" % (z + 1))
                g2, b2, zon2 = build(bx, bz, lambda a, c: z)
                I.remap(g2, b2, bx, bz, zon2)
                K.check(snap(b2) == after, "R Zone %d: the same chunk twice = the same result (deterministic)" % (z + 1))
                g3, b3, zon3 = build(bx, bz, lambda a, c: -1)
                b30 = snap(b3)
                I.remap(g3, b3, bx, bz, zon3)
                K.check(snap(b3) == b30, "R Zone %d: island-less columns (zone -1) are untouched" % (z + 1))
        K.eq((above, keep_bad, rot_bad, fill_bad, patch_mixed, st_bad), (0, 0, 0, 0, 0, 0),
             "R Zone %d over 64 chunks: no id above T%d left / ores, stone, unknown ids identical / tree rotation kept / plant filler -> air / one crop per 8x8 patch / stage kept"
             % (z + 1, w if z < 4 else 15))
        if z < 3:
            K.eq(mleft, 0, "R Zone %d: no Mushroom-collection id left (surface + caves)" % (z + 1))
        else:
            K.check(mkept > 500, "R Zone %d: mushrooms kept (%d)" % (z + 1, mkept))
        if z == 4:
            share = 100.0 * own_p / max(1, tot_p)
            K.check(60.0 <= share <= 80.0, "R Zone 5: %.1f %% of its wild crops are its own (Potato / Onion / Mushroom; target 70 +- 10)" % share)
    # a chunk without any table id: nothing changes; counters move
    g = GC()
    b = g.getBlockChunk()
    for lx in range(32):
        for lz in range(32):
            b.setBlock(lx, 80, lz, STONE, 0, 0)
    zon = JArray(JInt)([0] * (34 * 34))
    K.eq(int(I.remap(g, b, 0, 0, zon)), 0, "R a chunk with no table id: nothing changed")
    K.check(int(I.RM_SWAP.get()) > 0 and int(I.RM_AIR.get()) > 0 and "plants / tree blocks swapped" in str(I.rmText()),
            "R the counters for /zone info: %s" % str(I.rmText())[-120:])
    K.save()


# ------------------------------------------------------------------------------------------- S: settings + start twice
def run_setup(out, jar, scratch, home):
    K = HK.Child(out)
    I, T = jvm_and_table(jar)
    from jpype import JClass, JString
    Cfg, Lg = JClass(PKG + "WgCfg"), JClass(PKG + "WgLog")
    Paths = JClass("java.nio.file.Paths")
    Props = JClass("java.util.Properties")

    def apply(txt):
        p = Props()
        p.load(JClass("java.io.StringReader")(JString(txt)))
        Cfg.apply(p)
        return int(I.RM_SW), int(I.RM_Z5), str(I.RM_T1), str(I.RM_T5)
    K.eq(apply("part.zones=true\n"), (2, 70, "auto", "auto"), "S a file without the 0.7.8 keys keeps the defaults 2 / 70 / auto")
    Cfg.UNLOAD_S = 60
    apply("zones.unloadOldSeconds=60\n")
    K.eq(int(Cfg.UNLOAD_S), 60, "S fix: zones.unloadOldSeconds=60 reads as 60 s (0.7.7's intProp clamped it to 12)")
    apply("zones.unloadOldSeconds=900\n")
    K.eq(int(Cfg.UNLOAD_S), 900, "S fix: 900 s reads as 900")
    apply("zones.unloadOldSeconds=60\n")
    K.eq(apply("zones.spawnWindow=99\nzones.z5OwnPct=-5\nzones.remap.1= Pumpkin>Wheat \nzones.remap.5=off\n"), (15, 0, "Pumpkin>Wheat", "off"),
         "S clamped (99 -> 15, -5 -> 0), texts trimmed")
    K.eq(apply("zones.spawnWindow=-7\n"), (-1, 0, "Pumpkin>Wheat", "off"), "S -7 -> -1 (off); missing keys keep the running values")
    K.eq(apply("zones.spawnWindow=x\nzones.z5OwnPct=70\nzones.remap.1=auto\nzones.remap.5=auto\n"), (-1, 70, "auto", "auto"), "S junk keeps the running value")
    I.RM_SW = 2
    # the Server Setup rows through the kit's console path, on a scratch mods folder
    mods = os.path.join(scratch, "kit", "mods")
    d = os.path.join(mods, "Skyy_SkyyWorldGen")
    os.makedirs(d)
    Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
    Cfg.load()
    t0_ = open(os.path.join(d, "config.properties"), encoding="latin-1").read()
    K.check("#   Zone 1 auto: Turnip>own,Pumpkin>own" in t0_ and "#   Zone 4 auto: " in t0_ and "Crystal>Sallow" in t0_ and "#   Zone 5 auto: Wheat>z5" in t0_
            and "auto,From>To" in t0_, "S fix: the default config.properties lists each zone's auto table under the zones.remap comment")
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyWorldGen"))
    r1 = str(Fn.cmdSetConsole(JString("zones.spawnWindow"), JString("-1")))
    r2 = str(Fn.cmdSetConsole(JString("zones.z5OwnPct"), JString("55")))
    r3 = str(Fn.cmdSetConsole(JString("zones.remap.3"), JString("Rice>Pumpkin")))
    r4 = str(Fn.cmdSetConsole(JString("zones.spawnWindow"), JString("16")))
    CP.shutdown()
    t = open(os.path.join(d, "config.properties"), encoding="latin-1").read()
    K.check(int(I.RM_SW) == -1 and int(I.RM_Z5) == 55 and str(I.RM_T3) == "Rice>Pumpkin" and "zones.spawnWindow=-1" in t and "zones.z5OwnPct=55" in t
            and "zones.remap.3=Rice>Pumpkin" in t, "S the rows set the fields live + the file lines: %s | %s | %s" % (r1, r2, r3))
    K.check(int(I.RM_SW) == -1, "S 16 is refused by the row bounds: %s" % r4)
    I.RM_SW = 2
    I.RM_Z5 = 70
    I.RM_T3 = JString("auto")
    # start twice on the live copy
    if home and os.path.isdir(home):
        def tree():
            o = {}
            for r, _ds, fs in os.walk(home):
                for f in fs:
                    p = os.path.join(r, f)
                    o[os.path.relpath(p, home)] = open(p, "rb").read()
            return o
        t0 = tree()
        St = JClass(PKG + "WgStore")
        for s in (1, 2):
            Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
            St.FILE = Paths.get(os.path.join(home, "worlds.properties"))
            Cfg.load()
            St.read()
            K.check((int(I.RM_SW), int(I.RM_Z5), str(I.RM_T1)) == (2, 70, "auto"), "S start %d on the live copy: the 0.7.8 defaults (no line in the file)" % s)
        K.check(tree() == t0, "S start twice: the live copy is byte-identical (nothing written)")
    else:
        K.check(False, "S no live copy")
    # rmLogOnce: no asset map + no preset = nothing; with preset ids = once
    I.RM_IDS = None
    I.RM_LOGGED = False
    I.rmLogOnce()
    K.check(not bool(I.RM_LOGGED), "S rmLogOnce waits while no block is loaded (bare JVM)")
    preset(I, len(T.names))
    I.rmLogOnce()
    K.check(bool(I.RM_LOGGED) and ("%d of %d block ids loaded" % (len(T.names), len(T.names))) in str(I.rmText()), "S rmLogOnce logs once: %s" % str(I.rmText())[:160])
    K.save()


if __name__ == "__main__":
    HK.run("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("probe", run_probe), ("table", run_table), ("remap", run_remap), ("live", run_setup)], __file__, live=(LIVE_WG, "Skyy_SkyyWorldGen"))
