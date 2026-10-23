"""Harness for SkyyGear 0.3.44 (gear044: the tier tag is the FIRST tooltip line, under the client's "Slot:" line - tools/gear_0_3_44_patch.py).
Build first:
    python tools/gear_0_3_44_patch.py && python SkyyGear/build_skyygear_0.3.44.py
    python SkyyGear/test_skyygear_0.3.44.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the non-class jar entries = 0.3.43's
              except the manifest (no lang / item / config file changed - tools/ci/langdup.py has nothing new to see)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.43 -> 0.3.44 (EXPECT below)
  X  exec     EXECUTES in a bare JVM: descTag / descRest on the jar's OWN lang texts (every tagged description of this jar: tag = tools/tier_tags.py
              tag_for, the rest without it); markup keeps <color> spans; topTag for a T1 cloth chest, a metal weapon, a tool, a lang-tagged own
              tool, a weapon without a metal word (= tools/tier_tags.py combat_tag on its band start) and untiered items (no tag); then
              GearView.lines - THE tooltip text - for those items: the tag is line 0 (bold label colour), exactly once, the old flavour tag gone,
              every line <= 70 characters; unidentified pieces too; plain() keeps line 0 the bare name, the tag leads line 1 (same line count)
              SMITHING (items 4-6): setWords on EVERY set's real piece names (this jar's lang + the vanilla lang, read only): Maple / Oak / Beech /
              Wheat / Copper / Lead, no name of 60+ carries a tier code, every gathering set unique in its family; noCodes; the colour rows
              (skill met / short / unknown, material enough / short / unknown, GearReq colours, firstShort); upTotal = the summed per-piece
              tier-up cost with the missing piece skipped; canUpOf refuses an unidentified piece + a stack of 2 (GearUp.check), upTotal skips them
              in the middle of the set with their reasons and leaves them out of the total; upSet through its SEAM carries on past refusals
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the real hover look (the client draws "Slot: Chest" above our first description line), the Cloth / Light
weight word (the bare JVM has no item sound sets, so the Woolen Cuirass reads Heavy there - the tag = "T1 Crude " + GearView.WT_NAME[weightOf]),
a lang-tagged description through descMsg (no items in the bare JVM: descTag / descRest / markup are checked on the jar's own lang texts),
the Smithing page itself (setCost / pieceRows read the live inventory + bags; the real upPiece tier-up is the Anvil's, harnessed since 0.2.23).
Scratch: tools/dev/scratch/gear044/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.44"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear044", "harness")]
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.43.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_44_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.43.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
ADDED = []
EXPECT = {
    "GearView": ["+f TAG_RX", "+m bandTag", "+m descRest", "+m descTag", "+m descText", "+m markup", "+m topTag", "~<clinit>", "~m descMsg", "~m lines", "~m plain"],
    "GearSmith": ["+f CODE_RX", "+f KIND_WORDS", "+m firstWord", "+m isCode", "+m kindWord", "+m noCodes", "+m pieceRows", "+m plan", "+m setCost", "+m setCost",
                  "+m setName", "+m setWords", "+m skipText", "+m upTotal", "~<clinit>", "~m groupName", "~m groups"],          # setCost x2 (4 / 5 args)
    "GearReq": ["+m addI", "+m addL", "+m firstShort", "+m has", "+m matRow", "+m sk", "+m skRow"],
    "GearHubOpen": ["+f SEAM", "+m canUp", "+m canUpOf", "+m plan", "+m upSet", "~<clinit>"],
    "SmithPage": ["+m reqLine", "+m tierRow", "+m upAllClick", "-m tierRow", "~m card", "~m pieceRow", "~m piecesArea", "~m skyHde", "~m tupClick"],          # tierRow(.., inv)
    "SkyyGearPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "GearCfg": ["~m defaultsText"],          # the version in the file header
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
LABEL = "*#96a9be"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.44 - build script') and g.count('VERSION = "0.3.44"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no jar entry added / removed")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only non-class change is the manifest (no lang / item / config file)")
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JString, JArray, JImplements, JOverride, JInt, JObject, JBoolean
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    P = lambda n: JClass(PKG + n)
    GV, Data, Defs, Lvl, PackId = P("GearView"), P("GearData"), P("GearDefs"), P("GearLevel"), P("GearPackId")
    AL = JClass("java.util.ArrayList")
    BD, BS, BI, BB = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonBoolean")
    K.eq(str(Defs.C_LABEL), "#96a9be", "X the tier line colour = GearDefs.C_LABEL (vanilla @ColorDefaultLabel)")

    # ---- descTag / descRest on hand-made texts, then on EVERY tagged description this jar writes
    dt = lambda s: (lambda r: None if r is None else str(r))(GV.descTag(None if s is None else JString(s)))
    dr = lambda s: str(GV.descRest(None if s is None else JString(s)))
    K.eq([dt(s) for s in ("T4 Lead - Lead Mining Set - mining armor", "T2 Copper", "T3 Iron Heavy - x", "T12 Cinder - y", "Toast - nice", "The T2 sword",
                          "T2 - nothing", "t2 Iron - lower", "", None)],
         ["T4 Lead", "T2 Copper", "T3 Iron Heavy", "T12 Cinder", None, None, None, None, None, None], "X descTag: the leading tag only")
    K.eq([dr(s) for s in ("T4 Lead - Lead Mining Set - mining armor", "T2 Copper", "Toast - nice", None)],
         ["Lead Mining Set - mining armor", "", "Toast - nice", ""], "X descRest: the text after the tag (the rest of the ' - ' kept)")
    lang = zipfile.ZipFile(jar).read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
    tagged = []
    for ln in lang.splitlines():
        m = re.match(r"items\.(\S+)\.description = (.*)$", ln)
        if m and TT.tag_for(m.group(1)):
            tagged.append((m.group(1), m.group(2)))
    bad = [(i, dt(s), dr(s)[:40]) for i, s in tagged if dt(s) != TT.tag_for(i) or dr(s).startswith(TT.tag_for(i)) or not s.endswith(dr(s))]
    K.check(len(tagged) >= 200 and not bad, "X every tagged description of this jar (%d): descTag = tools/tier_tags.py tag_for, descRest without it %s" % (len(tagged), bad[:3]))

    # ---- markup: <color> spans kept, italic
    bucket = dict(tagged)[TT.IWB_ID]
    mm = GV.markup(JString(GV.descRest(JString(bucket))), JString(str(Defs.C_GRAY)))
    kids = [(str(c.getRawText()), str(c.getColor())) for c in mm.getChildren()]
    K.check(len(kids) >= 2 and kids[0] == ("Never runs dry", "#7ee08a") and kids[1][0].startswith(": right-click") and kids[1][1] == str(Defs.C_GRAY)
            and "<" not in "".join(t for t, c in kids), "X markup: the bucket's green span kept, no tag text left: %s" % kids[:3])
    kp = [(str(c.getRawText()), str(c.getColor())) for c in GV.markup(JString("plain text"), JString("#123456")).getChildren()]
    K.eq(kp, [("plain text", "#123456")], "X markup: a plain text = one grey child")

    # ---- topTag
    def doc(r="rare", lvl=10, ident=True):
        d = BD()
        d.put("r", BS(r))
        d.put("lvl", BI(lvl))
        d.put("id", BB(ident))
        return d
    tt = lambda i, slot, desc=None: (lambda r: None if r is None else str(r))(GV.topTag(JString(i), slot, None if desc is None else JString(desc)))
    slot = lambda i: int(Data.slotOf(JString(i)))
    CH = "Armor_Cloth_Wool_Chest"
    b0 = int(Lvl.band(JString(CH))[0])
    wt = int(GV.weightOf(JString(CH)))
    K.notes.append("X %s: slot %d, band start %d, weight %d (%s; the bare JVM has no sound sets - Cloth in game)" % (CH, slot(CH), b0, wt, str(GV.WT_NAME[wt])))
    K.eq(tt(CH, slot(CH)), "T1 Crude " + str(GV.WT_NAME[wt]), "X topTag: the Woolen Cuirass (Lv %d) = T1 Crude + its weight" % b0)
    K.eq(TT.level_tag(b0, CH), "T1 Crude", "X ... = tools/tier_tags.py level_tag")
    K.eq([slot("Weapon_Sword_Iron"), tt("Weapon_Sword_Iron", slot("Weapon_Sword_Iron"))], [0, "T2 Iron"], "X topTag: a metal weapon = T2 Iron")
    K.eq([tt("Weapon_Sword_Cobalt", 0), tt("Weapon_Daggers_Lead_SkyWynn", 0), tt("Weapon_Sword_Onyxium", 0)], ["T7 Cobalt", "T5 Lead", "T16 Onyxium"],
         "X topTag: other metal weapons (tools/tier_tags.py ladder)")
    K.eq([slot("Tool_Pickaxe_Iron"), tt("Tool_Pickaxe_Iron", 3), tt("Tool_Hatchet_Crude", 3)], [3, TT.tag_for("Tool_Pickaxe_Iron"), TT.tag_for("Tool_Hatchet_Crude")],
         "X topTag: tools = tools/tier_tags.py tag_for")
    K.eq(tt("Tool_WaterCan_Iron", 3, dict(tagged)["Tool_WaterCan_Iron"]), "T2 Iron", "X topTag: an own tool's lang tag")
    nm = "Weapon_Sword_Frost"
    nb = int(Lvl.band(JString(nm))[0])
    K.eq(tt(nm, 0), TT.combat_tag(nm, nb), "X topTag: a weapon without a metal word = tools/tier_tags.py combat_tag at its band start (Lv %d)" % nb)
    K.eq([tt("Tool_Feedbag", 3), tt("Tool_Shears_Basic", 3), tt("Some_Equipment_Thing", 4), tt("Some_Equipment_Thing", 4, "A plain description."), tt("Tool_Feedbag", 3, "Toast - x")],
         [None] * 5, "X topTag: untiered items (a tool without a metal word, equipment, a plain description) = no tag")

    # ---- THE tooltip text: GearView.lines
    def lines(i, d):
        txt, col = AL(), AL()
        GV.lines(JString(i), d, None, txt, col)
        return [(str(txt.get(k)), None if col.get(k) is None else str(col.get(k))) for k in range(txt.size())]
    FLAV = str(GV.FLAVOR)
    cases = [(CH, doc("rare", 1), tt(CH, slot(CH))), ("Weapon_Sword_Iron", doc("rare", 10), "T2 Iron"), ("Tool_Pickaxe_Iron", doc("rare", 10), "T2 Iron"),
             (CH, doc("rare", 1, False), tt(CH, slot(CH))), ("Weapon_Sword_Iron", doc("legendary", 12, False), "T2 Iron")]
    alll = []
    for i, d, want in cases:
        try:
            L = lines(i, d)
        except Exception as ex:
            K.check(False, "X lines(%s) ran in the bare JVM: %s" % (i, str(ex)[:200]))
            continue
        tx = [t.replace(chr(2), "") for t, c in L]
        alll += tx
        K.notes.append("X lines(%s): %s" % (i, tx))
        K.eq(L[0], (want, LABEL), "X lines(%s%s): line 0 = the tier tag, bold label colour" % (i, "" if Data.identified(d) else ", unidentified"))
        K.eq(sum(1 for t in tx if want in t), 1, "X ... the tag appears once")
        K.check(FLAV not in tx, "X ... no flavour slot (no description in the bare JVM) - the old tag-only flavour line is gone")
        K.check(not [t for t in tx[1:] if re.match(r"T\d+ ", t)], "X ... no other line starts with a tier tag")
    K.check(alll and max(len(t) for t in alll) <= 70, "X every tooltip line <= 70 characters (longest %d)" % (max(len(t) for t in alll) if alll else -1))
    # an untiered tool: no tier line, the rest unchanged
    try:
        Lu = lines("Tool_Feedbag", doc("rare", 1))
        K.check(not [t for t, c in Lu if c == LABEL] and not [t for t, c in Lu if re.match(r"T\d+ ", t)], "X lines(an untiered tool): no tier line %s" % [t for t, c in Lu][:4])
    except Exception as ex:
        K.check(False, "X lines(Tool_Feedbag) ran: %s" % str(ex)[:200])

    # ---- plain(): line 0 = the BARE name (Auctions gearName / stackName, Wardrobe twinKey, Exploration loot cards read it); the tag joins line 1
    pl = [str(x) for x in GV.plain(JString("Weapon_Sword_Iron"), doc("rare", 10), None)]
    K.notes.append("X plain(Weapon_Sword_Iron): %s" % pl)
    K.eq(pl[0], str(GV.nameText(JString("Weapon_Sword_Iron"), doc("rare", 10))), "X plain(): line 0 is the bare item name")
    K.check(pl[1].startswith("T2 Iron - ") and sum(1 for x in pl if "T2 Iron" in x) == 1, "X plain(): the tag leads line 1, once: %r" % pl[1])
    pc = [str(x) for x in GV.plain(JString(CH), doc("rare", 1), None)]
    K.check(pc[0] == str(GV.nameText(JString(CH), doc("rare", 1))) and pc[1].startswith(tt(CH, slot(CH)) + " - ") and sum(1 for x in pc if "T1 Crude" in x) == 1, "X plain(cloth chest): %r" % pc[:2])
    pu = [str(x) for x in GV.plain(JString("Tool_Feedbag"), doc("rare", 1), None)]
    K.check(not [x for x in pu if re.match(r"T\d+ ", x)], "X plain(an untiered tool): no tag %s" % pu[:3])
    # the same number of lines as without the tier line: the lines() text minus blanks / flavour / reforge hint (the Ability fold aside)
    txt0, col0 = AL(), AL()
    GV.lines(JString("Tool_Pickaxe_Iron"), doc("rare", 10), None, txt0, col0)
    raw = [str(txt0.get(k)) for k in range(txt0.size())]
    kept = [x for x in raw if x and x != FLAV and x != str(GV.REFORGE_HINT)]
    pp = [str(x) for x in GV.plain(JString("Tool_Pickaxe_Iron"), doc("rare", 10), None)]
    K.eq(len(pp), 1 + len(kept) - 1, "X plain(Iron pickaxe): line count = name + its lines, the tag line folded into line 1 (%d)" % len(pp))

    # ================================================================ items 4-6: the Smithing set pages
    S, Req, HO, Up = P("GearSmith"), P("GearReq"), P("GearHubOpen"), P("GearUp")
    JA = lambda xs: JArray(JString)([JString(x) for x in xs])
    # ---- 4. set names: THE RULE on every set's REAL piece names (this jar's lang + the vanilla lang, read only)
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")).read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
    names = {}
    for src in (az, lang):
        for ln in src.splitlines():
            m = re.match(r"items\.(Armor_\w+?)_(Head|Chest|Hands|Legs)\.name = (.*)$", ln)
            if m:
                names.setdefault(m.group(1), {})[m.group(2)] = m.group(3).strip()
    sw = lambda k: str(S.setWords(JA(list(names[k].values()))))
    K.eq([sw(k) for k in ("Armor_Foraging_F2", "Armor_Foraging_F1", "Armor_Foraging_Beech", "Armor_Farming_P1", "Armor_Fishing_A1", "Armor_Mining_Lead")],
         ["Maple", "Oak", "Beech", "Wheat", "Copper", "Lead"], "X set names: Maple / Oak / Beech / Wheat / Copper (Fishing A1) / Lead - the material word")
    code = re.compile(r"\b[A-Z][0-9]{1,2}\b")
    allw = dict((k, sw(k)) for k in names if len(names[k]) >= 2)
    K.check(len(allw) >= 60 and not [k for k, w in allw.items() if code.search(w)], "X no set name of %d carries a tier code" % len(allw))
    fam = {}
    for k, w in allw.items():
        f = k.split("_")[1]
        if f in ("Foraging", "Farming", "Fishing", "Mining"):
            fam.setdefault(f, []).append(w)
    K.check(all(len(v) == len(set(v)) and all(v) for v in fam.values()), "X every gathering set has its own non-empty name within its family %s" % dict((f, len(v)) for f, v in fam.items()))
    empty = sorted(k for k, w in allw.items() if not w)
    K.notes.append("X sets without shared name words (fall back to the id name minus codes): %s" % empty[:12])
    K.eq([str(S.noCodes(JString(x))) for x in ("Foraging F2 Set", "Farming P7 Set", "Iron Set", "Z2 Lead")], ["Foraging Set", "Farming Set", "Iron Set", "Lead"], "X noCodes")
    SL = ["Head", "Chest", "Hands", "Legs"]
    f2 = ["Armor_Foraging_F2_" + x for x in SL]
    hd = str(S.setName(JString("Armor_Foraging_F2|Maple"), JA(f2), 5))
    K.check(not code.search(hd) and hd.endswith(" Set"), "X a heading in the bare JVM (no item names here) still has no code: %r" % hd)
    K.eq(str(S.groupName(JString("Armor_Mining_Lead|Lead"), 1)), "Lead Set", "X groupName drops the '|word' of the new key")
    K.eq([str(S.firstWord(JString(x))) for x in ("Maple Bark Helm", "Lead", "")], ["Maple", "Lead", ""], "X firstWord")
    # ---- 5. colour rows: met / not met (skill), enough / not enough (material)
    def rows_of(fn):
        rs = AL()
        fn(rs)
        return [(str(Req.tx(rs, i)), int(Req.st(rs, i))) for i in range(rs.size())]
    K.eq(rows_of(lambda r: (Req.skRow(r, "Foraging", 15, 17), Req.skRow(r, "Foraging", 15, 6), Req.skRow(r, "Foraging", 15, -2), Req.skRow(r, "Foraging", 15, -1))),
         [("Foraging 15 (you have 17)", 1), ("Foraging 15 (you have 6)", 0), ("Foraging 15", -1), ("Foraging 15 (you have 0)", 0)], "X skill row: met green / short red / unknown white")
    K.eq(rows_of(lambda r: (Req.matRow(r, "Maple Log", 170, 342), Req.matRow(r, "Maple Log", 170, 42), Req.matRow(r, "Maple Log", 170, 170), Req.matRow(r, "Any Wood", 4, -1))),
         [("Maple Log: 170 (you have 342)", 1), ("Maple Log: 170 (you have 42)", 0), ("Maple Log: 170 (you have 170)", 1), ("Any Wood: 4", -1)], "X material row: enough green / short red / unknown white")
    K.eq([str(Req.col(1)), str(Req.col(0))], [str(Defs.C_OK), str(Defs.C_BAD)], "X the colours = the 0.3.18 GearReq list (C_OK / C_BAD)")
    rs = AL()
    Req.matRow(rs, "Maple Log", 170, 342)
    Req.skRow(rs, "Foraging", 15, 6)
    Req.matRow(rs, "Maple Log", 5, 1)
    K.eq(str(Req.firstShort(rs)), "Foraging 15 (you have 6)", "X firstShort = the first red row")
    rs = AL()
    Req.matRow(rs, "Maple Log", 170, 342)
    K.check(Req.firstShort(rs) is None, "X firstShort: all met = none")
    # ---- 6. the full-set total (upgrade path): Maple from Beech, the player owns 3 of the 4 Beech pieces
    own = JClass("java.util.HashSet")()
    for x in SL[:3]:
        own.add("Armor_Foraging_Beech_" + x)
    ut = S.upTotal(JA(f2), own, None)
    tg = [str(x) for x in ut[0]]
    need = dict((str(k), int(v)) for k, v in ut[1].items())
    per = {}
    for x in SL[:3]:
        c = Up.cost(JString("Armor_Foraging_Beech_" + x), JString("Armor_Foraging_F2_" + x))
        for i in range(len(c[0])):
            per[str(c[0][i])] = per.get(str(c[0][i]), 0) + int(c[1][i])
    K.eq((tg, [str(x) for x in ut[2]]), (f2[:3], f2[3:]), "X upTotal: one target per owned tier-below piece, the missing one skipped")
    K.check(need == per and sum(need.values()) > 0, "X upTotal: the summed cost = the sum of each piece's tier-up cost %s" % need)
    K.notes.append("X Maple set total for 3 pieces: %s" % need)
    K.eq(len(S.upTotal(JA(f2), JClass("java.util.HashSet")(), None)[0]), 0, "X upTotal: nothing owned = no target")
    # ---- 6. the full-set run (GearHubOpen.upSet through the SEAM): all done / a forced failure on piece 3 stops the rest
    calls = []

    @JImplements("java.util.function.Function")
    class One(object):
        def __init__(self, fail_at):
            self.fail_at = fail_at

        @JOverride
        def apply(self, o):
            calls.append(str(o))
            if len(calls) == self.fail_at:
                return JString("-The inventory refused the change - nothing was used.")
            return JString("+" + str(o) + " (Rare, Lv 15)!")
    HO.SEAM = One(0)
    r = HO.upSet(None, None, None, JA(f2))
    K.eq((int(r[0]), calls), (4, f2), "X upSet: every piece once, in order")
    calls[:] = []
    HO.SEAM = One(3)
    r = HO.upSet(None, None, None, JA(f2))
    K.eq((int(r[0]), calls), (3, f2), "X upSet: a refusal on piece 3 is noted and the rest carry on (piece 4 tried; each piece its own paid tier-up)")
    K.check(" - not upgraded: " in str(r[1]) and "The inventory refused" in str(r[1]), "X ... the message collects the reason: %s" % str(r[1])[:160])
    calls[:] = []

    @JImplements("java.util.function.Function")
    class Two(object):
        @JOverride
        def apply(self, o):
            calls.append(str(o))
            return JString("-no " + str(o)) if len(calls) in (2, 3) else JString("+" + str(o) + " (Rare, Lv 15)!")
    HO.SEAM = Two()
    r = HO.upSet(None, None, None, JA(f2))
    K.eq((int(r[0]), calls), (2, f2), "X upSet: two refusals in the middle - all four tried, two done")
    K.check(str(r[1]).count("no Armor_Foraging_F2_") == 2, "X ... both reasons listed: %s" % str(r[1])[:200])
    calls[:] = []
    HO.SEAM = One(1)
    r = HO.upSet(None, None, None, JA(f2))
    K.eq((int(r[0]), calls), (3, f2), "X upSet: the first piece refused, the other three still done")
    # ---- review fix 1: the per-piece checks BEFORE the total (an unidentified piece + a stack of 2 in the middle of the set)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    un = fu.get(None)
    fl = dict((str(f.getName()), f) for f in IS.class_.getDeclaredFields())

    def stack(iid, gd, q=1):
        s_ = un.allocateInstance(IS.class_)
        md = BD()
        if gd is not None:
            md.put(str(Defs.DOC_KEY), gd)
        for n_, v_ in (("itemId", JString(iid)), ("quantity", JInt(q)), ("metadata", md)):
            fl[n_].setAccessible(True)
            fl[n_].set(s_, v_)
        return s_
    def cu(*sts):
        l = AL()
        for x in sts:
            l.add(x)
        r_ = HO.canUpOf(l, None)
        return None if r_ is None else str(r_)
    w_unid = cu(stack("Armor_Foraging_Beech_Chest", doc("rare", 8, False)))
    w_stk = cu(stack("Armor_Foraging_Beech_Hands", doc("rare", 8), 2))
    K.check(w_unid is not None and w_unid.startswith("Identify that item first"), "X canUpOf: an unidentified piece is refused (GearUp.check): %r" % w_unid)
    K.eq(w_stk, "That item is a stack of 2 - split it first.", "X canUpOf: a stack of 2 is refused (GearUp.check)")
    K.eq(cu(stack("Armor_Foraging_Beech_Hands", doc("rare", 8), 2), stack("Armor_Foraging_Beech_Hands", doc("rare", 8, False))), w_stk, "X canUpOf: the first reason of several pieces")
    K.check(cu() is None, "X canUpOf: no piece = none (upTotal lists it as not owned)")
    own4 = JClass("java.util.HashSet")()
    for x in SL:
        own4.add("Armor_Foraging_Beech_" + x)
    why = JClass("java.util.HashMap")()
    why.put("Armor_Foraging_F2_Chest", w_unid)
    why.put("Armor_Foraging_F2_Hands", w_stk)
    ut2 = S.upTotal(JA(f2), own4, why)
    need2 = dict((str(k), int(v)) for k, v in ut2[1].items())
    per2 = {}
    for x in ("Head", "Legs"):
        c = Up.cost(JString("Armor_Foraging_Beech_" + x), JString("Armor_Foraging_F2_" + x))
        for i in range(len(c[0])):
            per2[str(c[0][i])] = per2.get(str(c[0][i]), 0) + int(c[1][i])
    K.eq(([str(x) for x in ut2[0]], [str(x) for x in ut2[2]], [str(x) for x in ut2[3]]),
         (["Armor_Foraging_F2_Head", "Armor_Foraging_F2_Legs"], ["Armor_Foraging_F2_Chest", "Armor_Foraging_F2_Hands"], [w_unid, w_stk]),
         "X upTotal: the unidentified Chest + the stack of 2 Hands in the middle are skipped with their reasons; Head + Legs stay")
    K.check(need2 == per2 and sum(need2.values()) > 0, "X ... the shown total counts only Head + Legs %s" % need2)
    sc_ = JArray(JObject)([JBoolean(True), JA(["Armor_Foraging_F2_Head"]), AL(), ut2[2], ut2[3]])
    stx = str(S.skipText(sc_))
    K.check(stx.startswith("Skipped: ") and "Identify that item first" in stx and "stack of 2" in stx, "X skipText lists each skipped piece + reason: %s" % stx[:160])
    K.eq(str(S.skipText(JArray(JObject)([JBoolean(True), JA([]), AL(), JA([]), JA([])]))), "", "X skipText: none = empty")
    HO.SEAM = None
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec)], __file__)
