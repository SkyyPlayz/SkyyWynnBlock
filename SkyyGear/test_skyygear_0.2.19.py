"""Harness for SkyyGear 0.2.19 (TOOLTIP RESTYLE, look only: Wynncraft top + SkyBlock bottom; tools/gear_0_2_19_patch.py header).
Build first:
    python tools/gear_0_2_19_patch.py && python SkyyGear/build_skyygear_0.2.19.py

    python SkyyGear/test_skyygear_0.2.19.py [--jar <SkyyGear-0.2.19.jar>] [--old <SkyyGear-0.2.18.jar>] [--mt <Multitools-1.2.9.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py (as the 0.2.12 - 0.2.18 harnesses do).
  S  non-class entries 0.2.18 -> 0.2.19: only the manifest changed
  A  every class of the jar loads + verifies (-Xverify:all)
  R  RENDER, twice: one child per jar (0.2.18, then 0.2.19) boots the bare server (vanilla pack + the jar as its own pack + the Multitools jar
     copied into scratch) and renders the SAME documents with the same bridge: every item family (sword with a speed tier + charge, kit sword,
     battleaxe under level, wand + staff with SkyyArmory's answer, a staff without it (spell row), leather + cloth armor, a Mining Set piece,
     pickaxe, hatchet under level, multitool, 3 Untiered, the Mythic bow, unidentified weapon + armor, an old tool with a dead key, unknown /
     "coming later" keys, mystery bags) for the owner and neutral, + a SWEEP of every forgeable item id in the Item store
     PARENT: no number changed (the set of numbers of every rendering, old vs new), no line longer than the longest 0.2.18 line, the samples
     printed for Skyy
  X  (in the 0.2.19 child, -Xverify:all) EVERY NEW CODE PATH EXECUTED: seg (plain / colour / bold / italic marks -> FormattedMessage fields),
     row, rollLine / rollCol, typeWord, prefixLen / classReq, canReforge, sect, reqLine (every gate state + the tool + the mining paths),
     speedRows, quickRow, weaponRows (wand, melee-tap wand, spell, plain damage), baseRows (levelled + plain armor), rolledRows, statLines (page:
     no style mark, no blank line), trickBad + utRows (lines off, note), lines (identified / unidentified / tool routing / flavour / reforge),
     descMsg (flavour slot italic), plain (no marker), GearUnid.descMsg (range / single level, armor type, Untiered bag), GearBase.shots [7];
     RE-RENDER ONCE: a stack rendered by 0.2.18 -> 0.2.19's apply writes a new display (document untouched) and a second apply returns it unchanged
  C  CLASS COMPARE 0.2.18 -> 0.2.19 (javassist members): only GearView / GearBase / GearUnid (+ the version) differ, exactly the listed members
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: 0.2.19 writes the same bytes as 0.2.18, the 2nd start changes
     nothing (0.2.19 has no one-time update)
  AA THE ENGINE-ACCESS AUDIT
FIX ROUND (critics): X plain() drops "This item can be reforged!" and folds the Ability section into one line; X GearCfg.classSig moves
cfgEpoch when SkyyClasses' class:list / class:weapons:* change (cached 1 s) and the stack re-renders with the new Class Req; PARENT: every
sample's gear:fn:describe text (neutral) fits the SkyyAuctions item page (12 lines, 90 chars) whenever its 0.2.18 text did, the rolled Rare
sword fits it; the level behind every number = "Lv. Min" (0.2.18's "at Lv N" = 0.2.19's Lv. Min N; a Lv 1 kit item = vanilla numbers).
Scratch: tools/dev/scratch/gear0219/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.19"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0219")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-0.2.18.jar")))      # read only
MT_SRC = os.path.abspath(arg("--mt", os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")))   # read only - copied into the scratch folder
MT_JAR = os.path.join(SCRATCH, "mt", "Multitools-1.2.9.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
MULTI_PRE = "Tool_Hatchet_Pickaxe_Multitool_"
EXPECT_CHANGED = {"GearView", "GearBase", "GearUnid", "GearCfg"}

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR = H["FAKE_DIR"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
FAILS, OKS = [], [0]
NUM = re.compile(r"\d+(?:\.\d+)?")


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and b'"0.2.19"' in eb["manifest.json"]
          and b"tooltips in the SkyWynn style" in eb["manifest.json"],
          "S: 0.2.18 -> 0.2.19: no file added / removed, only the manifest changed (version + the tooltip sentence): + %s ~ %s" % (added[:3], changed[:3]))
    check(sorted(n for n in zn.namelist() if n.endswith(".class")) == sorted(n for n in zo.namelist() if n.endswith(".class")),
          "S: the same class files (no class added or removed)")


# ====================================================================================================== R + X: render with one jar
def run_render(out, which, oldres):
    from jpype import JClass, JArray, JInt, JLong, JDouble, JObject, JBoolean, JImplements, JOverride
    K = Child(out)
    new = which == "new"
    jar = JAR if new else OLD_JAR
    H["JAR"] = jar
    H["VERSION"] = VERSION if new else "0.2.18"
    _jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=new, big=True)
    E = H["engine_boot"](K)
    ITEM = E["ITEM"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "R/%s: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (which, E["fail"], E["vfail"]))
    # the bare boot drops the vanilla tools (block sets after items) - load the Tool_* files again (as the 0.2.18 harness does)
    AZP = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip")
    HAL = JClass("java.util.ArrayList")
    afs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(AZP), JClass("java.util.HashMap")())
    with zipfile.ZipFile(AZP) as az_:
        tnames = [n for n in az_.namelist() if n.startswith("Server/Item/Items/Tool/") and n.endswith(".json")]
    tl_ = HAL()
    for n in tnames:
        tl_.add(afs.getPath("/" + n))
    ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl_)
    # the Multitools jar (scratch copy) as pack IBC:Multitools (its Common files first)
    have_mt = os.path.isfile(MT_JAR)
    if have_mt:
        import hashlib
        CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
        FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
        mfs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(MT_JAR), JClass("java.util.HashMap")())
        with zipfile.ZipFile(MT_JAR) as mz_:
            for nm in mz_.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    CAR.addCommonAsset("IBC:Multitools", FCA(mfs.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(mz_.read(nm)).hexdigest(), None))
        E["loadpack"](MT_JAR, "IBC:Multitools", False)
        have_mt = ITEM.getAssetMap().getAsset(MULTI_PRE + "Iron") is not None
    # the item names / descriptions: a bare I18nModule holding the en-US server.lang of Assets.zip + the jar (the bare boot has none)
    I18 = JClass("com.hypixel.hytale.server.core.modules.i18n.I18nModule")
    inst = E["us"].allocateInstance(I18.class_)
    msgs = JClass("java.util.concurrent.ConcurrentHashMap")()
    for zp in (AZP, jar):
        with zipfile.ZipFile(zp) as zz:
            if "Server/Languages/en-US/server.lang" not in zz.namelist():
                continue
            for ln in zz.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
                if " = " in ln and not ln.startswith("#"):
                    k_, v_ = ln.split(" = ", 1)
                    msgs.put("server." + k_.strip(), v_.replace(chr(92) + "n", chr(10)))
    langs = JClass("java.util.concurrent.ConcurrentHashMap")()
    langs.put("en-US", msgs)
    for fname in ("fallbacks", "bundledDefaults", "cachedLanguages"):
        E["jf"](I18, fname).set(inst, JClass("java.util.concurrent.ConcurrentHashMap")())
    E["jf"](I18, "languages").set(inst, langs)
    E["jf"](I18, "messagesVersion").set(inst, JClass("java.util.concurrent.atomic.AtomicLong")())
    E["jf"](I18, "instance").set(None, inst)
    P = lambda n: JClass(PKG + n)
    K.notes.append("R/%s: I18n stand-in: %d en-US lines; Weapon_Sword_Crude description: %s" % (which, msgs.size(), str(P("Gear").tr("server.items.Weapon_Sword_Crude.description"))[:60]))
    (Cfg, Defs, Data, Roll, View, Gate, Speed, Unid, Pool, Base, Gear) = [P(n) for n in (
        "GearCfg", "GearDefs", "GearData", "GearRoll", "GearView", "GearGate", "GearSpeed", "GearUnid", "GearPool", "GearBase", "Gear")]
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD = JClass("org.bson.BsonDocument")
    BA = JClass("org.bson.BsonArray")
    BI32 = JClass("org.bson.BsonInt32")
    BS = JClass("org.bson.BsonString")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    SR = JClass("java.io.StringReader")
    SYS = JClass("java.lang.System")
    br = CHM()
    SYS.getProperties().put("skyy.bridge", br)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000b019")
    LEVELS = {}

    @JImplements("java.util.function.Function")
    class SkillLv:
        @JOverride
        def apply(self, a):
            return JInt(LEVELS.get(str(a[1]), 0))

    @JImplements("java.util.function.Function")
    class Allowed:
        @JOverride
        def apply(self, a):
            return JBoolean(True)

    ARM = {"Weapon_Wand_": ["wand", 5, 1, 0, 40, 8, 100.0, "SkyyGearTestA", "SkyyGearTestB", "", "pierces 3 - 32 blocks (50% past 16)", 0.0],
           "Weapon_Staff_": ["staff", 10, 2, 0, 60, 12, 100.0, "SkyyGearTestA", "SkyyGearTestB", "Hold - blink 16 blocks + light trail - 5 Stamina", "24 blocks", 0.0]}

    @JImplements("java.util.function.Function")
    class ArmInfo:
        @JOverride
        def apply(self, a):
            kind, iid = str(a[0]), str(a[1])
            for pre, v in ARM.items():
                if iid.startswith(pre) and v[0] == kind:
                    qm = 0 if iid == "Weapon_Wand_Wood" else v[2]          # a wand whose tap is still a melee swing (no quick shot)
                    return JArray(JObject)([JInt(v[1]), JInt(qm), JInt(v[3]), JInt(v[4]), JInt(v[5]), JDouble(v[6]), v[7], v[8], v[9], v[10], JDouble(v[11])])
            return None

    def bridge(classes=True, skills=True, armory=True):
        br.clear()
        if skills:
            br.put("skill:fn:level", SkillLv())
        if classes:
            br.put("class:fn:allowed", Allowed())
            br.put("class:skill:" + str(U1), "Swordsmanship")
            br.put("class:list", "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity")
            br.put("class:weapons:Warrior", "Weapon_Sword_,Weapon_Longsword_")
            br.put("class:weapons:Berserker", "Weapon_Battleaxe_,Weapon_Axe_")
            br.put("class:weapons:Mage", "Weapon_Staff_,Weapon_Wand_")
            br.put("class:weapons:Priest", "Weapon_Wand_,Weapon_Spellbook_")
            br.put("class:weapons:Archer", "Weapon_Shortbow_,Weapon_Crossbow_")
            br.put("class:weapons:free", "Weapon_Club_")
        if armory:
            br.put("armory:fn:info", ArmInfo())
        Gate.forget(U1)

    def skills(**kv):
        LEVELS.clear()
        LEVELS.update({"Mining": 49, "Foraging": 49, "Farming": 49, "Smithing": 0, "Swordsmanship": 49, "Combat": 49})
        LEVELS.update(kv)
        Gate.forget(U1)

    FRESH = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(SR(FRESH))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()
    bridge()
    skills()

    def withmods(d, kv):
        a = BA()
        for k, v in kv:
            a.add(Data.mod(k, JInt(v)))
        d.put("mods", a)
        return d

    def mkdoc(iid, r, lvl, mods_=(), ident=True, spd=2, rf=None):
        d = Roll.newDoc(iid, JInt(r), ident, "test", JInt(lvl))
        if ident:
            withmods(d, list(mods_))
            if int(Data.slotOf(iid)) == 0:
                d.put("spd", BI32(spd))
        if rf:
            d.put("rf", BS(rf[0]))
            d.put("rfN", BI32(rf[1]))
        return d

    def flat(msg):
        """a Message -> [(text, colour, bold, italic)] segments (FormattedMessage tree, depth first)"""
        segs = []

        def walk(fm, col, b, it):
            c = str(fm.color) if fm.color is not None else col
            bb = bool(fm.bold) if fm.bold is not None else b
            ii = bool(fm.italic) if fm.italic is not None else it
            if fm.rawText is not None:
                segs.append((str(fm.rawText), c, bb, ii))
            elif fm.messageId is not None:
                segs.append(("<desc:%s>" % fm.messageId, c, bb, ii))
            if fm.children is not None:
                for ch in fm.children:
                    walk(ch, c, bb, ii)
        walk(msg.getFormattedMessage(), None, False, False)
        return segs

    def msglines(msg):
        """the rendered description as lines: [(text, colour, bold, italic)] per line (one style per line here)"""
        out_, cur = [], []
        for t, c, b, i in flat(msg):
            parts = t.split("\n")
            for k, p in enumerate(parts):
                if k > 0:
                    out_.append(cur)
                    cur = []
                if p:
                    cur.append((p, c, b, i))
        out_.append(cur)
        res = []
        for segs in out_:
            if not segs:
                res.append(("", None, False, False))
            else:
                res.append(("".join(x[0] for x in segs), segs[0][1], any(x[2] for x in segs), any(x[3] for x in segs)))
        return res

    def render(iid, d, owner=U1):
        txt, col = AL(), AL()
        View.lines(iid, d, owner, txt, col)
        msg = View.descMsg(iid, d, txt, col)
        nm = View.nameText(iid, d)
        return {"lines": [[str(txt.get(i)), None if col.get(i) is None else str(col.get(i))] for i in range(txt.size())],
                "desc": [list(x) for x in msglines(msg)], "name": str(nm),
                "plain": [str(x) for x in View.plain(iid, d, owner)]}

    R_UT, R_MY, R_SET = int(Defs.R_UT), int(Defs.R_MY), int(Defs.R_SET)
    later = [str(Defs.S_KEY[i]) for i in range(int(Defs.NS)) if int(Defs.S_LIVE[i]) == 0]
    lk = later[0] if later else "str"
    SAMPLES = [
        ("sword (Rare, Fast, reforged)", "Weapon_Sword_Iron", 2, 20, [("dmg", 8), ("str", 12), ("cc", 5), ("spd", -2)], {"spd": 2, "rf": ("Sharp", 2)}),
        ("kit sword (Normal Lv 1)", "Weapon_Sword_Crude", 0, 1, [], {"spd": 1}),
        ("battleaxe (Legendary, under level)", "Weapon_Battleaxe_Iron", 3, 30, [("cd", 20), ("lsteal", 3)], {"skills": {"Swordsmanship": 9}}),
        ("wand (SkyyArmory shots)", "Weapon_Wand_Tribal", 1, 20, [("mp", 10)], {}),
        ("wand, melee tap", "Weapon_Wand_Wood", 0, 5, [], {}),
        ("staff (blink)", "Weapon_Staff_Iron", 2, 20, [("mp", 5), ("cc", 3)], {}),
        ("staff, no SkyyArmory (spell row)", "Weapon_Staff_Iron", 2, 20, [("mp", 5)], {"armory": False}),
        ("light armor", "Armor_Leather_Medium_Chest", 1, 12, [("def", 5), ("hpr", 4)], {}),
        ("cloth armor Lv 1", "Armor_Cloth_Cotton_Head", 0, 1, [], {}),
        ("Mining Set piece", "Armor_Copper_Head", 0, 5, [], {}),
        ("pickaxe (Rare, rolled)", "Tool_Pickaxe_Iron", 2, 23, [("mpow", 20), ("mfort", 5), ("mwis", 7)], {}),
        ("hatchet under level", "Tool_Hatchet_Iron", 0, 15, [], {"skills": {"Foraging": 5}}),
        ("multitool (Legendary)", MULTI_PRE + "Iron", 3, 15, [("mpow", 5), ("cpow", 6), ("mwis", 4), ("fwis", 6)], {}),
        ("Untiered sword (Paperweight)", "Weapon_Sword_UT_Paperweight", 0, 20, [], {}),
        ("Untiered battleaxe (Overtime)", "Weapon_Battleaxe_UT_Overtime", 0, 20, [], {}),
        ("Untiered light armor (Courier)", "Armor_UT_Courier_Chest", 0, 20, [], {}),
        ("Mythic bow (Vampire)", "Weapon_Shortbow_Vampire", R_MY, 30, [("str", 10), ("cc", 4)], {}),
        ("unidentified sword", "Weapon_Sword_Iron", 2, 20, [], {"ident": False}),
        ("unidentified armor", "Armor_Leather_Medium_Head", 1, 12, [], {"ident": False}),
        ("old pickaxe with a dead key", "Tool_Pickaxe_Iron", 0, 23, [("dmg", 5)], {"notr": True}),
        ("unknown + later keys", "Weapon_Sword_Iron", 1, 20, [("zzz", 3), (lk, 4)], {"spd": 0}),
    ]
    samples, docs = {}, {}
    for name, iid, r, lvl, ms, ex in SAMPLES:
        if iid.startswith(MULTI_PRE) and not have_mt:
            K.notes.append("R: no Multitools jar - sample '%s' skipped" % name)
            continue
        if ITEM.getAssetMap().getAsset(iid) is None:
            K.check(False, "R/%s: sample item %s is in the Item store" % (which, iid))
            continue
        bridge(armory=ex.get("armory", True))
        skills(**ex.get("skills", {}))
        d = mkdoc(iid, r, lvl, ms, ident=ex.get("ident", True), spd=ex.get("spd", 2), rf=ex.get("rf"))
        if ex.get("notr"):
            d.remove("tr")
        docs[name] = (iid, d)
        rec = render(iid, d)
        rec["neutral"] = render(iid, d, None)
        rec["id"] = iid
        s0 = Data.put(IS(iid, JInt(1)), d, U1)
        rec["meta"] = str(s0.getMetadata().toJson())
        rec["q"] = int(Gear.quality(s0))
        rec["doc"] = str(d.toJson())
        samples[name] = rec
    bridge()
    skills()
    # mystery bags: a weapon range, an armor single level with its type, an Untiered bag
    bags = {}
    for name, key, at, r, lo, hi in (("bag: Rare sword Lv 5-9", "Weapon_Sword", 0, 2, 5, 9), ("bag: Unique heavy helmet Lv 12", "Armor_Head", 1, 1, 12, 12),
                                     ("bag: Untiered battleaxe Lv 15-29", "Weapon_Battleaxe", 0, R_UT, 15, 29)):
        ty = int(Pool.typeIdx(key))
        st = Unid.make(JInt(ty), JInt(at), JInt(r), JInt(lo), JInt(hi), "test", "test", JInt(1))
        K.check(st is not None, "R/%s: %s made" % (which, name))
        if st is None:
            continue
        bd = Unid.doc(st)
        bags[name] = {"desc": [list(x) for x in msglines(Unid.descMsg(bd))]}
    # the sweep: every forgeable id (weapons, armor, rolling tools) at its band level, Rare, the same modifiers
    sweep = {}
    keys = sorted(str(k) for k in ITEM.getAssetMap().getAssetMap().keySet())
    for iid in keys:
        try:
            if not bool(Data.forgeable(iid)):
                continue
            d = Roll.newDoc(iid, JInt(2), True, "sweep")
            withmods(d, [("dmg", 8), ("str", 12), ("spd", -2)] if int(Data.slotOf(iid)) != 3 else [("mpow", 6), ("mfort", 3)])
            if int(Data.slotOf(iid)) == 0:
                d.put("spd", BI32(2))
            txt, col = AL(), AL()
            View.lines(iid, d, U1, txt, col)
            sweep[iid] = [[str(txt.get(i)), None if col.get(i) is None else str(col.get(i))] for i in range(txt.size())]
        except Exception as e:
            K.check(False, "R/%s: sweep %s rendered: %s" % (which, iid, e))
    K.notes.append("R/%s: %d samples, %d bags, sweep of %d forgeable ids" % (which, len(samples), len(bags), len(sweep)))
    K.save(samples=samples, bags=bags, sweep=sweep)
    if not new:
        return

    # ============================================================================ X: every new code path (0.2.19 jar)
    GRAY, OK, BAD, GOLD = str(Defs.C_GRAY), str(Defs.C_OK), str(Defs.C_BAD), str(Defs.C_GOLD)
    Msg = JClass("com.hypixel.hytale.server.core.Message")
    Q_ID = lambda o: int(JClass("java.lang.System").identityHashCode(o))

    def fm(m):
        f = m.getFormattedMessage()
        return (None if f.rawText is None else str(f.rawText), None if f.color is None else str(f.color).lower(),
                None if f.bold is None else bool(f.bold), None if f.italic is None else bool(f.italic))
    sg = [fm(View.seg("a", None)), fm(View.seg("b", "")), fm(View.seg("c", "#112233")), fm(View.seg("d", View.bold("#445566"))),
          fm(View.seg("e", View.ital("#778899"))), fm(View.seg("f", "*"))]
    K.check(sg[0] == ("a", None, None, None) and sg[1] == ("b", None, None, None) and sg[2] == ("c", "#112233", None, None)
            and sg[3] == ("d", "#445566", True, None) and sg[4] == ("e", "#778899", None, True) and sg[5] == ("f", None, True, None),
            "X seg: no colour / colour / '*' bold / '~' italic marks -> the FormattedMessage fields the client gets (bold, italic VERIFIED set): %s" % sg)
    K.check(str(View.row("Damage", "22-30")) == "Damage 22-30" and str(View.bold(None)) == "*" and str(View.ital("#fff")) == "~#fff",
            "X row / bold / ital")
    rl = [str(View.rollLine("dmg", JInt(8))), str(View.rollLine("spd", JInt(-2))), str(View.rollLine("zzz", JInt(3))), str(View.rollLine("zzz", JInt(-3))),
          str(View.rollLine("mp", JInt(8)))]
    lab = lambda k: str(Defs.S_LABEL[int(Defs.sIndex(k))])
    K.check(rl[0] == "+ %s   +8%s" % (lab("dmg"), str(Defs.S_UNIT[int(Defs.sIndex("dmg"))])) and rl[1].startswith("- %s   -2" % lab("spd"))
            and rl[2] == "+ zzz   +3" and rl[3] == "- zzz   -3" and rl[4].startswith("+ %s   +8" % lab("mp")) and rl[4].endswith(str(View.suffix(int(Defs.sIndex("mp"))))),
            "X rollLine: '+ Label   +N' / '- Label   -N' / unknown key by name / the stat's own note: %s" % rl)
    rcol = [str(View.rollCol("str", JInt(5), False)), str(View.rollCol("str", JInt(-5), False)), str(View.rollCol("str", JInt(5), True)), str(View.rollCol(lk, JInt(5), False))]
    K.check(rcol[:3] == [OK, BAD, GRAY] and (rcol[3] == GRAY or not later), "X rollCol: green up, red down, grey dead / coming later: %s" % rcol)
    tw = dict((i, str(View.typeWord(i))) for i in ("Weapon_Sword_Iron", "Weapon_Shortbow_Iron", "Weapon_Bo_Iron", "Armor_Iron_Head", "Armor_Iron_Chest",
                                                   "Armor_Iron_Hands", "Armor_Iron_Legs", "Armor_Odd", "Tool_Pickaxe_Iron", MULTI_PRE + "Iron", "Weapon_Longbow_X",
                                                   "Skyy_Thing", "Weapon_"))
    K.check(tw["Weapon_Sword_Iron"] == "SWORD" and tw["Weapon_Shortbow_Iron"] == "BOW" and tw["Weapon_Longbow_X"] == "BOW" and tw["Weapon_Bo_Iron"] == "BO STAFF"
            and [tw["Armor_Iron_" + x] for x in ("Head", "Chest", "Hands", "Legs")] == ["HELMET", "CHESTPLATE", "GAUNTLETS", "LEGGINGS"]
            and tw["Tool_Pickaxe_Iron"] == "PICKAXE" and tw[MULTI_PRE + "Iron"] == "MULTITOOL" and tw["Skyy_Thing"] == str(View.slotWord("Skyy_Thing"))
            and tw["Weapon_"] == str(View.slotWord("Weapon_")) and tw["Armor_Odd"] in ("ARMOR", str(View.slotWord("Armor_Odd"))) and str(View.typeWord(None)) == "ITEM",
            "X typeWord: %s" % tw)
    pl = [int(View.prefixLen("Weapon_Sword_,Weapon_", "Weapon_Sword_Iron")), int(View.prefixLen(None, "x")), int(View.prefixLen(" , Weapon_Axe_", "Weapon_Sword_Iron"))]
    cq = [View.classReq("Weapon_Sword_Iron"), View.classReq("Weapon_Wand_Iron"), View.classReq("Weapon_Club_Iron"), View.classReq("Weapon_Gun_X"), View.classReq(None)]
    br.put("class:weapons:Priest", "Weapon_Wand_Iron")               # a longer prefix wins alone
    cq2 = View.classReq("Weapon_Wand_Iron")
    br.remove("class:list")
    cq3 = View.classReq("Weapon_Sword_Iron")
    bridge()
    K.check(pl == [13, -1, -1] and str(cq[0]) == "Warrior" and str(cq[1]) == "Mage / Priest" and cq[2] is None and cq[3] is None and cq[4] is None
            and str(cq2) == "Priest" and cq3 is None,
            "X classReq: one class, two classes sharing a prefix, a free weapon -> none, no match -> none, the longest prefix wins, no SkyyClasses -> "
            "none: %s %s %s %s" % (pl, [None if x is None else str(x) for x in cq], cq2, cq3))
    sw = docs["sword (Rare, Fast, reforged)"][1]
    cr_ = [bool(View.canReforge("Weapon_Sword_Iron", sw)), bool(View.canReforge("Weapon_Sword_Iron", docs["unidentified sword"][1])),
           bool(View.canReforge("Weapon_Sword_UT_Paperweight", docs["Untiered sword (Paperweight)"][1])),
           bool(View.canReforge("Armor_Copper_Head", docs["Mining Set piece"][1])), bool(View.canReforge("Weapon_Sword_Iron", None)),
           bool(View.canReforge("Rock_Stone", sw)), bool(View.canReforge("Tool_Pickaxe_Iron", docs["pickaxe (Rare, rolled)"][1]))]
    K.check(cr_ == [True, False, False, False, False, False, True], "X canReforge: rare sword yes; unidentified / Untiered / Mining Set piece / no doc / "
            "not gear no; a rolled pickaxe yes: %s" % cr_)
    t_, c_ = AL(), AL()
    View.sect(t_, c_, AL(), AL())
    a1, b1 = AL(), AL()
    a1.add("x")
    b1.add(None)
    View.sect(t_, c_, a1, b1)
    View.sect(t_, c_, a1, b1)
    K.check([str(x) for x in t_] == ["x", "", "x"], "X sect: an empty block adds nothing; a blank line only between blocks: %s" % [str(x) for x in t_])

    # reqLine: every state
    LVL = lambda n: int(P("GearLevel").level(docs[n][0], docs[n][1]))
    LS, LP = LVL("sword (Rare, Fast, reforged)"), LVL("pickaxe (Rare, rolled)")
    LM = LVL("Mining Set piece")
    def req(iid, d, owner=U1):
        g = View.reqLine(owner, iid, d, JInt(int(P("GearLevel").level(iid, d))))
        return (str(g[0]), None if g[1] is None else str(g[1]), bool(g[2]), str(g[3]))
    skills()
    q_ok = req("Weapon_Sword_Iron", sw)
    skills(Swordsmanship=9)
    q_low = req("Weapon_Sword_Iron", sw)
    q_neu = req("Weapon_Sword_Iron", sw, None)
    skills()
    br.remove("class:skill:" + str(U1))
    Gate.forget(U1)
    q_pick = req("Weapon_Sword_Iron", sw)
    kit = docs["kit sword (Normal Lv 1)"][1]
    q_pick_ok = req("Weapon_Sword_Crude", kit)
    bridge()
    br.remove("skill:fn:level")
    Gate.forget(U1)
    q_ns = req("Weapon_Sword_Iron", sw)
    apply(level__noSkills="block")
    q_nsb = req("Weapon_Sword_Iron", sw)
    apply()
    bridge()
    Cfg.PART_GATE = False
    q_off = req("Weapon_Sword_Iron", sw)
    apply()
    pk = docs["pickaxe (Rare, rolled)"][1]
    q_t_ok = req("Tool_Pickaxe_Iron", pk)
    skills(Mining=3)
    q_t_low = req("Tool_Pickaxe_Iron", pk)
    q_t_neu = req("Tool_Pickaxe_Iron", pk, None)
    skills()
    q_mine = req("Armor_Copper_Head", docs["Mining Set piece"][1])
    Cfg.PART_TOOLS = False
    q_t_off = req("Tool_Pickaxe_Iron", pk)
    apply()
    nogate = Roll.newDoc("Weapon_Sword_Iron", JInt(1), True, "test", JInt(20))
    nogate.put("kind", BS("tool"))
    nogate.put("gate", BS(""))
    q_none = req("Weapon_Sword_Iron", nogate)
    K.check(q_ok == ("Lv. Min: %d Swordsmanship" % LS, OK, False, "Swordsmanship") and q_low == ("Lv. Min: %d Swordsmanship (you: 9)" % LS, BAD, True, "Swordsmanship")
            and q_neu[1] == GRAY and q_neu[0].startswith("Lv. Min: %d " % LS) and q_pick[1] == BAD and q_pick[0].endswith("(pick a class)") and q_pick[2]
            and q_pick_ok[1] == OK and q_ns == ("Lv. Min: %d" % LS, GRAY, False, "Level") and q_nsb == ("Lv. Min: %d (skills unavailable)" % LS, BAD, True, "Level")
            and q_off[1] == GRAY and q_t_ok == ("Lv. Min: %d Mining" % LP, OK, False, "Mining") and q_t_low == ("Lv. Min: %d Mining (you: 3)" % LP, BAD, False, "Mining")
            and q_t_neu[1] == GRAY and q_mine[0] == "Lv. Min: %d Mining" % LM and q_t_off == ("Lv. Min: %d Mining" % LP, GRAY, False, "Mining") and q_none[0] == "",
            "X reqLine - every gate state: met %s / low %s / neutral %s / pick a class %s (Lv 1 kit %s) / no SkyySkills %s / noSkills block %s / part.gate "
            "off %s / tool met %s, low %s, neutral %s / Mining piece %s / part.tools off %s / no gate %s"
            % (q_ok, q_low, q_neu, q_pick, q_pick_ok, q_ns, q_nsb, q_off, q_t_ok, q_t_low, q_t_neu, q_mine, q_t_off, q_none))
    # gateLine keeps the 0.2.18 text (the Reforge / Identify page sub line)
    gl = View.gateLine(U1, "Weapon_Sword_Iron", sw, JInt(LS))
    K.check(str(gl[0]) == "Lv %d - Requires Swordsmanship %d" % (LS, LS), "X gateLine (pages) unchanged: %s" % gl[0])
    # speedRows / quickRow / weaponRows / baseRows / statLines
    spr = View.speedRows("Weapon_Sword_Iron", sw)
    tl_old = Speed.tipLines("Weapon_Sword_Iron", sw)
    K.check(spr is not None and str(spr[0]) == "Fast Attack Speed"
            and ((spr[1] is None and tl_old[1] is None) or (tl_old[1] is not None and str(spr[1]) == "Damage " + str(tl_old[1]).split(": ")[-1].replace(" per hit", "")))
            and (spr[2] is None) == (tl_old[2] is None) and (spr[2] is None or str(tl_old[2]).endswith(str(spr[2]))),
            "X speedRows = GearSpeed.tipLines' numbers in the new words: %s | %s" % (list(map(str, spr)) if spr else None, list(map(str, tl_old))))
    K.check(View.speedRows("Armor_Leather_Medium_Chest", docs["light armor"][1]) is None, "X speedRows: no tier line -> null")
    sh = Base.shots("Weapon_Wand_Tribal", docs["wand (SkyyArmory shots)"][1])
    K.check(sh is not None and len(sh) == 8 and str(sh[7]) == "pierces 3 - 32 blocks (50% past 16)"
            and str(View.quickRow(sh)) == "Quick Shot %d damage - 1 Mana - pierces 3 - 32 blocks (50%% past 16)" % int(sh[3]),
            "X GearBase.shots [7] quick words + quickRow: %s" % (str(View.quickRow(sh)) if sh is not None else None))
    sh2 = JArray(JObject)([sh[0], sh[1], sh[2], sh[3], sh[4], sh[5], sh[6]])
    K.check(str(View.quickRow(sh2)) == "Quick Shot %d damage - 1 Mana" % int(sh[3]), "X quickRow without words (an older answer, 7 elements)")
    pg_t, pg_c = AL(), AL()
    View.statLines("Weapon_Sword_Iron", sw, pg_t, pg_c)
    pg = [(str(pg_t.get(i)), None if pg_c.get(i) is None else str(pg_c.get(i))) for i in range(pg_t.size())]
    K.check(pg and all(t and (c is None or c.startswith("#")) for t, c in pg) and pg[0] == ("Fast Attack Speed", GRAY)
            and any(t.startswith("+ ") and c == OK for t, c in pg) and any(t.startswith("- ") and c == BAD for t, c in pg),
            "X statLines (the Reforge page column): head + base + rolled rows, plain #hex colours only, no blank line, no style mark: %s" % pg)
    K.check([bool(View.trickBad(JInt(int(P("GearUtFx").T_TAKEN)), JDouble(5.0))), bool(View.trickBad(JInt(int(P("GearUtFx").T_TAKEN)), JDouble(-5.0))),
             bool(View.trickBad(JInt(int(P("GearUtFx").T_RANGE)), JDouble(12.0))), bool(View.trickBad(JInt(0), JDouble(30.0))), bool(View.trickBad(JInt(2), JDouble(-30.0)))]
            == [True, False, True, False, True], "X trickBad: more damage taken / a range limit / a minus = downside")
    apply(part__utLines="false")
    ut_off = render("Weapon_Sword_UT_Paperweight", docs["Untiered sword (Paperweight)"][1])
    apply()
    K.check(["(Untiered lines are off on this server)", GRAY] in ut_off["lines"] and ["Ability: Trade-off", "*" + GOLD] in ut_off["lines"],
            "X utRows: part.utLines off -> the grey 'off' line, the Ability section (note) stays")
    # the samples: structure checks on the 0.2.19 rendering
    S_ = samples
    LVL = lambda n: int(P("GearLevel").level(docs[n][0], docs[n][1]))
    LS, LP, LH = LVL("sword (Rare, Fast, reforged)"), LVL("pickaxe (Rare, rolled)"), LVL("hatchet under level")

    def L(name):
        return [t for t, c in S_[name]["lines"]]

    def LC(name):
        return [(t, c) for t, c in S_[name]["lines"]]
    swl = LC("sword (Rare, Fast, reforged)")
    swt = [t for t, c in swl]
    i_sp, i_dmg = swt.index("Fast Attack Speed"), next((i for i, t in enumerate(swt) if t.startswith("Damage ")), 1)
    i_roll = swt.index("+ %s   +8%%" % lab("dmg"))
    i_cls, i_lv = swt.index("Class Req: Warrior"), swt.index("Lv. Min: %d Swordsmanship" % LS)
    i_ab = swt.index("Ability: Charged Attack") if "Ability: Charged Attack" in swt else -1
    i_fl = swt.index(str(View.FLAVOR)) if str(View.FLAVOR) in swt else -1
    i_rf, i_can, i_rar = swt.index("Reforge: Sharp (2x)"), swt.index("This item can be reforged!"), swt.index("RARE SWORD")
    K.check(i_sp == 0 and swt[1] == "" and i_sp < i_dmg < i_roll < i_cls < i_lv and (i_ab < 0 or i_lv < i_ab < i_rf) and i_rf < i_can < i_rar == len(swt) - 1
            and swl[i_roll][1] == OK and swl[swt.index("- %s   -2%s" % (lab("spd"), str(Defs.S_UNIT[int(Defs.sIndex("spd"))])))][1] == BAD
            and swl[i_rar][1] == "*" + str(Defs.R_HEX[2]) and swl[i_sp][1] == GRAY and swl[i_cls][1] == GRAY and swl[i_lv][1] == OK
            and (i_fl < 0 or i_ab < i_fl < i_rf) and not [t for t in swt if " at Lv " in t or ": +" in t],
            "X lines (sword): speed / blank / Damage / rolled (green + red) / Class Req + Lv. Min / Ability / flavour / Reforge + reforgeable + bold "
            "RARE SWORD: %s" % swt)
    sd = S_["sword (Rare, Fast, reforged)"]["desc"]
    K.check(sd[-1][0] == "RARE SWORD" and sd[-1][2] is True and (i_ab < 0 or any(x[0] == "Ability: Charged Attack" and x[2] for x in sd)),
            "X descMsg: the rarity line (and the Ability header) bold in the message the client gets: %s" % sd[-3:])
    fls = [(n, r_["desc"]) for n, r_ in S_.items() if str(View.FLAVOR) in [t for t, c in r_["lines"]]]
    K.check(fls and all(any(x[0].startswith("<desc:") and x[3] and str(x[1]).lower() == GRAY.lower() for x in dsc) for n, dsc in fls)
            and all(str(View.FLAVOR) not in S_[n]["plain"] and not [p for p in S_[n]["plain"] if p == ""] for n in S_),
            "X flavour slot: the item's own description = an italic grey translation message (%d samples have one); plain() drops the marker and the "
            "blank lines" % len(fls))
    wl = L("wand (SkyyArmory shots)")
    K.check(any(t.startswith("Quick Shot ") for t in wl) and "Ability: Charged Shot" in wl and any(t.startswith("Mana Cost: 5") for t in wl)
            and not [t for t in wl if t.startswith("Damage ")] and "Class Req: Mage / Priest" in wl and "RARE WAND" not in wl and "UNIQUE WAND" in wl,
            "X wand: Quick Shot row, Ability: Charged Shot + Mana Cost, no melee line, two classes: %s" % wl)
    wm = L("wand, melee tap")
    K.check("Ability: Charged Shot" in wm and not [t for t in wm if t.startswith("Quick Shot")],
            "X wand whose tap is a melee swing: the Damage row + the charged shot ability: %s" % wm)
    stl = L("staff (blink)")
    K.check("Hold - blink 16 blocks + light trail - 5 Stamina" in stl and "Mana Cost: 10" in stl, "X staff: the hold words under the ability: %s" % stl)
    sp_ = L("staff, no SkyyArmory (spell row)")
    K.check("Ability: Charged Shot" not in sp_ and not [t for t in sp_ if t.startswith("Quick Shot")],
            "X staff without SkyyArmory: no shot rows (the bare boot resolves no spell / damage numbers - the old jar shows none either): %s" % sp_)
    ar = L("light armor")
    K.check(any(t.startswith("Health +") for t in ar) and any(t.startswith("Resistance ") and "(physical, projectile)" in t for t in ar)
            and "UNIQUE CHESTPLATE" in ar and not [t for t in ar if t.startswith("Class Req")], "X light armor: Health / Resistance rows, UNIQUE CHESTPLATE: %s" % ar)
    cl_ = L("cloth armor Lv 1")
    K.check("NORMAL HELMET" in cl_ and not [t for t in cl_ if ": " in t and t.split(": ")[0] in ("Health", "Armor")], "X cloth Lv 1 (0.2 rows, 'Label value'): %s" % cl_)
    ms_ = LC("Mining Set piece")
    K.check(any(t.startswith("Set: ") for t, c in ms_) and "This item can be reforged!" not in [t for t, c in ms_] and ms_[-1][0] == "SET HELMET",
            "X Mining Set piece: set block kept, not reforgeable, SET HELMET: %s" % ms_)
    pkl = LC("pickaxe (Rare, rolled)")
    pkt = [t for t, c in pkl]
    K.check(any(t.startswith("Mining Power +") for t in pkt) and ("+ %s   +20%%" % lab("mpow"), OK) in pkl and pkt[-1] == "RARE PICKAXE"
            and "This item can be reforged!" in pkt and pkt.index("Lv. Min: %d Mining" % LP) > pkt.index("+ %s   +20%%" % lab("mpow")),
            "X pickaxe: power / Fortune / Wisdom rows, green rolled tool rows, requirement after them, RARE PICKAXE: %s" % pkt)
    ht_ = LC("hatchet under level")
    htt = [t for t, c in ht_]
    hq = "Lv. Min: %d Foraging (you: 5)" % LH
    hn = "No bonus until Foraging %d" % LH
    K.check((hn, BAD) in ht_ and hq in htt and htt.index(hn) == htt.index(hq) + 1
            and "Tree Feller unlocks in the Foraging tree" in htt and htt.index("Tree Feller unlocks in the Foraging tree") < htt.index(hq),
            "X hatchet under level: GearTool's red line moves under the requirement, its grey note stays with the rows: %s" % htt)
    if "multitool (Legendary)" in S_:
        mt = L("multitool (Legendary)")
        K.check(mt[-1] == "LEGENDARY MULTITOOL" and any(t.startswith("Mining Power ") for t in mt) and any(t.startswith("Chopping Power ") for t in mt)
                and ("Lv. Min: %d Mining + Foraging" % LVL("multitool (Legendary)")) in mt, "X multitool: both stat sets, LEGENDARY MULTITOOL: %s" % mt)
    up = LC("Untiered sword (Paperweight)")
    upt = [t for t, c in up]
    K.check(("Ability: Trade-off", "*" + GOLD) in up and ("Hits 50% harder. Swings 40% slower.", GRAY) in up and upt[-1] == "UNTIERED SWORD"
            and "This item can be reforged!" not in upt and any(t.startswith("+ ") for t in upt), "X Untiered sword: Trade-off ability + note, UNTIERED SWORD: %s" % upt)
    uo = LC("Untiered battleaxe (Overtime)")
    K.check(any(t.startswith("Damage +30% while under half Health") and c == GRAY for t, c in uo) and any(t.startswith("Max Health -10%") and c == BAD for t, c in uo),
            "X Untiered battleaxe: the upside trick grey, the downside trick red: %s" % uo)
    uc = LC("Untiered light armor (Courier)")
    K.check(any(t.startswith("Damage taken +5%") and c == BAD for t, c in uc), "X Untiered armor: 'Damage taken +5%%' is a red downside: %s" % uc)
    my = L("Mythic bow (Vampire)")
    K.check(my[-1] == "MYTHIC BOW" and "Class Req: Archer" in my, "X Mythic bow: MYTHIC BOW, Class Req Archer: %s" % my)
    un = LC("unidentified sword")
    unt = [t for t, c in un]
    K.check(unt[0].startswith("Unidentified - ") and ("Cannot be used until identified.", BAD) in un and any(t.startswith("Identify: ") and c == GOLD for t, c in un)
            and unt[-1] == "RARE SWORD" and "This item can be reforged!" not in unt and ("Lv. Min: %d Swordsmanship" % LVL("unidentified sword")) in unt and str(View.FLAVOR) not in unt,
            "X unidentified sword: grey / red, requirement, gold Identify, RARE SWORD, no flavour: %s" % unt)
    ua = L("unidentified armor")
    K.check("Gives no stats until identified." in ua and ua[-1] == "UNIQUE HELMET", "X unidentified armor: %s" % ua)
    dk = LC("old pickaxe with a dead key")
    K.check(any(t.startswith("+ %s   +5" % lab("dmg")) and c == GRAY for t, c in dk), "X a weapon key on an old tool: grey rolled row: %s" % dk)
    uk = LC("unknown + later keys")
    K.check(("+ zzz   +3", OK) in uk and (not later or any(t.startswith("+ ") and c == GRAY for t, c in uk)), "X unknown key by name; a 'coming later' key grey: %s" % uk)
    bw = [x[0] for x in bags["bag: Rare sword Lv 5-9"]["desc"]]
    bh = [x[0] for x in bags["bag: Unique heavy helmet Lv 12"]["desc"]]
    bu = bags["bag: Untiered battleaxe Lv 15-29"]["desc"]
    K.check("Lv. Range: 5-9" in bw and bw[-1] == "RARE SWORD" and bags["bag: Rare sword Lv 5-9"]["desc"][-1][2] is True and any(t.startswith("Identify: ") for t in bw)
            and "Lv. Min: 12" in bh and bh[0] == "Heavy armor" and bh[-1] == "UNIQUE HELMET" and bu[-1][0] == "UNTIERED BATTLEAXE"
            and any("Untiered" in x[0] for x in bu), "X GearUnid.descMsg: range / single level, armor type, Untiered bag, bold rarity line: %s | %s" % (bw, bh))
    # FIX ROUND 1: plain() (gear:fn:describe / /gear) - no reforge hint, the Ability section on one line
    spl = S_["sword (Rare, Fast, reforged)"]["plain"]
    wpl = S_["wand (SkyyArmory shots)"]["plain"]
    stp = S_["staff (blink)"]["plain"]
    upl = S_["Untiered sword (Paperweight)"]["plain"]
    abl = [t for t in wpl if t.startswith("Ability: ")]
    UTA = "Ability: Trade-off - Hits 50% harder. Swings 40% slower"
    K.check(not [n for n in S_ if str(View.REFORGE_HINT) in S_[n]["plain"] or str(View.REFORGE_HINT) in S_[n]["neutral"]["plain"]]
            and str(View.REFORGE_HINT) in swt and "Reforge: Sharp (2x)" in spl and spl[-1] == "RARE SWORD",
            "X plain: the owner hint 'This item can be reforged!' is never in the plain text (it stays in the tooltip): %s" % spl)
    K.check(len(abl) == 1 and abl[0].startswith("Ability: Charged Shot - Deals ") and " damage - Mana Cost: 5" in abl[0]
            and not [t for t in wpl if t.startswith("Deals ") or t.startswith("Mana Cost")]
            and any(t.startswith("Ability: Charged Shot - ") and t.endswith("Hold - blink 16 blocks + light trail - 5 Stamina") for t in stp)
            and UTA in [t[:len(UTA)] for t in upl] and not [t for t in upl if t.startswith("Hits 50%")],
            "X plain: the Ability section folded into one line (final '.' of each part dropped): %s | %s | %s"
            % (abl, [t for t in stp if t.startswith("Ability")], [t for t in upl if t.startswith("Ability")]))
    # FIX ROUND 2: SkyyClasses' data moves cfgEpoch (GearTick's dirty trigger) and the stack re-renders with the new Class Req
    def epoch():
        Cfg.CSIG_AT = JLong(0)
        return int(Cfg.cfgEpoch())
    bridge()
    skills()
    e0 = epoch()
    s_a = View.apply(IS("Weapon_Sword_Iron", JInt(1)), sw, U1)
    Cfg.CSIG_AT = JLong(int(JClass("java.lang.System").currentTimeMillis()))      # the cache is fresh for the next read
    br.put("class:weapons:Warrior", "Weapon_Longsword_")
    br.put("class:weapons:Berserker", "Weapon_Battleaxe_,Weapon_Sword_")
    cached = int(Cfg.cfgEpoch())                    # within the 1 s cache: the old value
    e1 = epoch()
    s_b = View.apply(s_a, sw, U1)
    rt_ = render("Weapon_Sword_Iron", sw)
    br.remove("class:list")
    e2 = epoch()
    bridge()
    e3 = epoch()
    br.put("class:weapons:free", "Weapon_Club_,Weapon_Mace_")
    e4 = epoch()
    bridge()
    e5 = epoch()
    K.check(cached == e0 and e1 != e0 and e2 not in (e0, e1) and e3 == e0 and e4 != e0 and e5 == e0
            and Q_ID(s_b) != Q_ID(s_a) and "Class Req: Berserker" in [t for t, c in rt_["lines"]],
            "X classSig: class:weapons:<Class> / class:list / class:weapons:free change cfgEpoch (cached 1 s, back to the same value when restored); "
            "the stack re-renders to 'Class Req: Berserker': %s" % [cached == e0, e1 != e0, e2, e3 == e0, e4 != e0, e5 == e0, Q_ID(s_b) != Q_ID(s_a)])
    # FIX ROUND 3: the level behind the numbers - a Lv 1 kit sword: Lv. Min: 1 and its hits ARE the vanilla ones
    kl = L("kit sword (Normal Lv 1)")
    K.check(LVL("kit sword (Normal Lv 1)") == 1 and any(t.startswith("Lv. Min: 1") for t in kl) and bool(Base.asVanilla("Weapon_Sword_Crude", kit, False)),
            "X kit sword: Lv. Min: 1 and GearBase.asVanilla (its numbers are the vanilla Lv 1 ones): %s" % kl)
    # RE-RENDER ONCE: a stack written by 0.2.18
    Q = JClass("java.lang.System")
    rr = []
    for name, rec in oldres["samples"].items():
        iid = rec["id"]
        md = BD.parse(rec["meta"])
        s_old = IS(iid, JInt(1)).withMetadata(md).withQuality(JInt(rec["q"]))
        d_ = Data.effective(iid, md)
        s1 = View.apply(s_old, d_, U1)
        s2 = View.apply(s1, d_, U1)
        dj0 = str(md.get(str(Defs.DOC_KEY)).asDocument().toJson())
        dj1 = str(s1.getMetadata().get(str(Defs.DOC_KEY)).asDocument().toJson())
        rr.append((name, Q.identityHashCode(s1) != Q.identityHashCode(s_old), dj0 == dj1, Q.identityHashCode(s2) == Q.identityHashCode(s1),
                   int(Gear.quality(s1)) == rec["q"]))
    bad_rr = [x for x in rr if not all(x[1:])]
    K.check(rr and not bad_rr, "X re-render once: every 0.2.18 stack (%d) gets a new display, its document and quality untouched; a 2nd apply "
            "returns it unchanged: %s" % (len(rr), bad_rr[:3]))
    K.save(samples=samples, bags=bags, sweep=sweep)


# ====================================================================================================== C: class compare
def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_

    def members(p_, cn, vers):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())

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
                t_ = re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))).replace("ldc_w ", "ldc ")
                t_ = re.sub(r"^((if\w*|goto|goto_w|jsr|jsr_w) )\d+$", r"\1N", t_)
                for v_ in vers:
                    t_ = t_.replace(v_, "VER")
                lines_.append(t_)
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_

    pa, pb = pool_of(OLD_JAR), pool_of(JAR)
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, ("0.2.18", "0.2.19")), members(pb, cn, ("0.2.18", "0.2.19"))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    add = sorted(c[len(PKG):] for c in set(nb) - set(na))
    gone = sorted(c[len(PKG):] for c in set(na) - set(nb))
    print("C. class compare 0.2.18 -> 0.2.19: + %s - %s" % (add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:1200]))
    K.check(not add and not gone, "C: no class added or removed: + %s - %s" % (add, gone))
    K.check(set(diffs) == EXPECT_CHANGED, "C: exactly GearView / GearBase / GearUnid / GearCfg changed (the version string is normalised): %s" % sorted(diffs))
    want = {"GearBase": {"~m shots"}, "GearUnid": {"~m descMsg"},
            "GearCfg": {"+f CSIG", "+f CSIG_AT", "+m classCompute", "+m classSig", "~m cfgEpoch", "~<clinit>"},
            "GearView": {"+f FLAVOR", "+f GAP", "+f REFORGE_HINT", "+m bold", "+m ital", "+m seg", "+m row", "+m rollLine", "+m rollCol", "+m typeWord", "+m prefixLen",
                         "+m classReq", "+m canReforge", "+m sect", "+m reqLine", "+m speedRows", "+m quickRow", "+m weaponRows", "+m baseRows",
                         "+m rolledRows", "+m trickBad", "+m utRows", "-m utLines", "~m statLines", "~m lines", "~m descMsg", "~m plain",
                         "~m armorLines", "~m otherArmorLines", "~m levelArmorLines", "+<clinit>"}}
    bad = {}
    for k, v in want.items():
        got = set(diffs.get(k, []))
        if got != v:
            bad[k] = (sorted(v - got), sorted(got - v))
    K.check(not bad, "C: the classes changed exactly where the patch says (missing / extra): %s" % bad)
    K.save(diffs=diffs)


# ====================================================================================================== D: start twice on a scratch copy
def run_start(out, home, which):
    from jpype import JClass
    K = Child(out)
    jar = JAR if which == "new" else OLD_JAR
    _jvm([B.SERVER_JAR, jar], verify=(which == "new"))
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
    K.check(snaps[1] == snaps[0], "D/%s: the 2nd start changes nothing" % which)
    K.save(cfg=snaps[0].decode("latin-1"))


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD_JAR], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def nums(lines):
    return sorted(set(m for t in lines for m in NUM.findall(t)))


def show(title, lines):
    print("  ---- %s" % title)
    for t, c in lines:
        if t == "\x01flavor":
            t = "<the item's own description, italic grey>"
        st = ""
        if c and c[0] == "*":
            st, c = " [bold]", c[1:]
        elif c and c[0] == "~":
            st, c = " [italic]", c[1:]
        print("    %-74s %s%s" % (t, c or "", st))


def compare(old, new):
    """parent: numbers unchanged, line length <= the 0.2.18 max, print the samples"""
    FL = "\x01flavor"
    olds, news = old["samples"], new["samples"]
    check(sorted(olds) == sorted(news), "R: the same samples rendered by both jars")
    diffs = []
    for n in sorted(news):
        for who in ("lines", "neutral"):
            a = olds[n][who] if who == "lines" else olds[n]["neutral"]["lines"]
            b = news[n][who] if who == "lines" else news[n]["neutral"]["lines"]
            na_ = nums([t for t, c in a if t != FL])
            nb_ = nums([t for t, c in b if t != FL])
            if na_ != nb_:
                diffs.append((n, who, sorted(set(na_) ^ set(nb_))))
    check(not diffs, "R: no number changed in any sample (owner + neutral; the set of numbers old vs new): %s" % diffs[:5])
    sd = []
    for iid in sorted(new["sweep"]):
        a = old["sweep"].get(iid)
        if a is None:
            sd.append((iid, "missing in 0.2.18"))
            continue
        if nums([t for t, c in a if t != FL]) != nums([t for t, c in new["sweep"][iid] if t != FL]):
            sd.append((iid, sorted(set(nums([t for t, c in a])) ^ set(nums([t for t, c in new["sweep"][iid]])))))
    check(len(new["sweep"]) > 200 and not sd, "R: the sweep - %d forgeable ids, no number changed: %s" % (len(new["sweep"]), sd[:5]))
    for n in sorted(new["bags"]):
        na_ = nums([x[0] for x in old["bags"][n]["desc"]])
        nb_ = nums([x[0] for x in new["bags"][n]["desc"]])
        check(na_ == nb_, "R: %s - the same numbers: %s / %s" % (n, na_, nb_))

    def longest(res):
        best = (0, "", "")
        for n, r in res["samples"].items():
            for t, c in r["lines"] + r["neutral"]["lines"]:
                if t != FL and len(t) > best[0]:
                    best = (len(t), n, t)
        for iid, ls in res["sweep"].items():
            for t, c in ls:
                if t != FL and len(t) > best[0]:
                    best = (len(t), iid, t)
        for n, r in res["bags"].items():
            for x in r["desc"]:
                if len(x[0]) > best[0]:
                    best = (len(x[0]), n, x[0])
        return best
    # FIX ROUND 1: the SkyyAuctions item page (descText(gl, 1, DESC_LINES 12, DESC_WRAP 90) of gear:fn:describe = the neutral plain())
    def ah_lines(pl):
        return sum(1 + (len(t) - 1) // 90 if t else 1 for t in pl[1:])
    ahbad, ahrows = [], []
    for n in sorted(news):
        a_, b_ = ah_lines(olds[n]["neutral"]["plain"]), ah_lines(news[n]["neutral"]["plain"])
        ahrows.append("%s %d->%d" % (n, a_, b_))
        if b_ > 12 and a_ <= 12:
            ahbad.append((n, a_, b_))
    print("R. Auctions page lines (0.2.18 -> 0.2.19, max 12): " + "; ".join(ahrows))
    check(not ahbad and ah_lines(news["sword (Rare, Fast, reforged)"]["neutral"]["plain"]) <= 12,
          "R: every sample's describe text fits the Auctions item page (12 lines) whenever 0.2.18's did; the rolled Rare sword fits: %s" % ahbad)
    # FIX ROUND 3: 0.2.18's "at Lv N" = 0.2.19's "Lv. Min: N" on every sample (the numbers are the levelled ones of that level)
    lvbad, lvn = [], 0
    for n in sorted(news):
        olv = set(int(x) for t, c in olds[n]["lines"] for x in re.findall(r" at Lv (\d+)", t))
        nlv = set(int(x) for t, c in news[n]["lines"] for x in re.findall(r"^Lv\. Min: (\d+)", t))
        if olv:
            lvn += 1
            if olv != nlv:
                lvbad.append((n, sorted(olv), sorted(nlv)))
    check(lvn >= 1 and not lvbad, "R: the level of 0.2.18's 'at Lv N' = 0.2.19's 'Lv. Min: N' (%d samples had 'at Lv'): %s" % (lvn, lvbad))
    lo, ln = longest(old), longest(new)
    check(ln[0] <= lo[0], "R: no line longer than the longest 0.2.18 line: 0.2.19 max %d (%s: '%s') <= 0.2.18 max %d (%s: '%s')"
          % (ln[0], ln[1], ln[2], lo[0], lo[1], lo[2]))
    print("R. the longest line: 0.2.18 %d chars (%s), 0.2.19 %d chars (%s)" % (lo[0], lo[1], ln[0], ln[1]))
    print("R. SAMPLES (0.2.19, the owner's view; the name line above each block is in the rarity colour):")
    for n in news:
        show("%s  |  name: %s" % (n, news[n]["name"]), news[n]["lines"])
    for n in new["bags"]:
        show(n, [(x[0], ("*" if x[2] else "") + (x[1] or "")) for x in new["bags"][n]["desc"]])
    print("R. 0.2.18 for comparison (sword):")
    show("0.2.18 sword", olds["sword (Rare, Fast, reforged)"]["lines"])


def main():
    for flag, fn in (("--mkfake", lambda: H["run_mkfake"](arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--render-old", lambda: run_render(arg("--out"), "old", None)),
                     ("--render-new", lambda: run_render(arg("--out"), "new", json.load(open(arg("--render-new"))))),
                     ("--compare", lambda: run_compare(arg("--out"))),
                     ("--start", lambda: run_start(arg("--out"), arg("--start"), arg("--which"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
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
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR), (JAR, OLD_JAR)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "0.2.18"' in z_.read("manifest.json").decode("utf-8"), "the old jar is not 0.2.18"
    if os.path.isfile(MT_SRC):
        os.makedirs(os.path.dirname(MT_JAR), exist_ok=True)
        shutil.copyfile(MT_SRC, MT_JAR)          # read-only source; the children load the scratch copy
    else:
        print("note: no Multitools jar - the multitool sample is skipped")
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        oo = os.path.join(SCRATCH, "render-old.json")
        pr = child(env, "--render-old", "--out", oo)
        check(pr.returncode == 0, "render-old: the child exited cleanly (%s)" % pr.returncode)
        old = take(oo, "render-old")
        if old is not None:
            on = os.path.join(SCRATCH, "render-new.json")
            pr = child(env, "--render-new", oo, "--out", on)
            check(pr.returncode == 0, "render-new: the child exited cleanly (%s)" % pr.returncode)
            new = take(on, "render-new")
            if new is not None:
                compare(old, new)
        res = {}
        for which in ("old", "new"):
            home = os.path.join(SCRATCH, "live-" + which)
            shutil.copytree(LIVE_DIR, home)
            out = os.path.join(SCRATCH, "start-%s.json" % which)
            pr = child(env, "--start", home, "--which", which, "--out", out)
            check(pr.returncode == 0, "D/%s: the child exited cleanly" % which)
            res[which] = take(out, "start-" + which)
        print("D. live Skyy_SkyyGear copied twice (read-only source %s)" % LIVE_DIR)
        if res.get("old") and res.get("new"):
            check(res["old"]["cfg"] == res["new"]["cfg"], "D: 0.2.19 starts the live copy to the same config.properties bytes as 0.2.18 (no one-time update)")
            fo = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-old")) if not f.startswith("config-history"))
            fn_ = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-new")) if not f.startswith("config-history"))
            check(fo == fn_, "D: the same files after the starts: %s / %s" % (fo, fn_))
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
