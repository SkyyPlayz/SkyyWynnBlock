"""Harness for SkyyGear 0.3.59 (round rar3: colour-coded item texts, looks only - tools/gear_0_3_59_patch.py header).
Build first (the build needs Quirk's private art; in a worktree: SKYWYNN_PRIVATE_ART=<path to SkyWynn-PRIVATE-art>):
    python tools/gear_0_3_59_patch.py && python SkyyGear/build_skyygear_0.3.59.py
    python SkyyGear/test_skyygear_0.3.59.py [--keep] [--expect-dump]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.58 jar is the compare base):
  S  static    the patch re-runs to identical bytes; no class / command / system; no jar entry added / removed; the changed non-class entries =
               server.lang + manifest.json; in server.lang ONLY the 324 description lines changed, each = its 0.3.58 text + Style Guide 15 spans
               (balanced, not nested, the 15 / rarity hexes only, the tier tag first and plain), every description coloured, every name byte-identical;
               the before / after text of every changed key -> <scratch>/../dumps/gear.txt
  A  verify    every class loads + initialises with -Xverify:all
  C  compare   0.3.58 -> 0.3.59 (EXPECT below)
  E  engine    the 0.2.11 harness's bare server boot (vanilla pack + THIS jar) - every new path EXECUTED:
               L  GearView.markup on the REAL lang texts of this jar: the tagged body (Tool_Pickaxe_Lead_SkyWynn) and an UNTAGGED coloured one
                  (Weapon_Sword_UT_Paperweight: the new descMsg branch) -> coloured pieces, the words unchanged; descMsg's FLAVOR line uses them
               G  GearView.sig carries the description hash (a stack re-renders once)
               B  GearPackGive.bagParts for every (zone, how, here): head + bag + tail = the 0.3.58 text, null where 0.3.58 sent nothing; bagLine = one
                  Message of three pieces gold / rarity colour / gold (Mythic #CC66CC, Untiered #FFAA00)
               N  (review fix 2) GearView.convText / packText / tierText / salvText joined = the 0.3.58 chat words; partsMsg = one piece per
                  non-empty text, the name in its colour, the rest the line colour; nameHex answers a 7-char hex (dflt when unreadable)
  E58 / E57 / E56 / E55 / E54  the 0.3.58 .. 0.3.54 harnesses' engine phases against THIS jar (every earlier check still passes)
  D  live      start twice on a scratch COPY of Skyy's live Skyy_SkyyGear (the 0.3.58 live phase): no one-time update, the second start changes nothing
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client drawing the coloured flavour line / lang spans (the augment spans already render), the real chat line.
Scratch: tools/dev/scratch/rar3fix/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, re, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.59"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar3fix", "gear")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.58.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_59_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.58.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
T58 = {"__file__": os.path.join(HERE, "test_skyygear_0.3.58.py"), "__name__": "t58"}
_s = open(T58["__file__"], encoding="utf8").read()
exec(compile(_s[:_s.rindex(chr(10) + 'HK.run_compare = T54["run_compare54"]')], T58["__file__"], "exec"), T58)
T57, T56, T55, T54 = T58["T57"], T58["T56"], T58["T55"], T58["T54"]
for _t in (T54, T55, T56, T57, T58):
    _t["SCRATCH"] = SCRATCH
ADDED = []
EXPECT = None if "--expect-dump" in sys.argv else {
    'CfgRows': ['~m header'], 'CfgRows2': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'GearCfg': ['~m defaultsText'], 'SkyyGearPlugin': ['~m setup'],          # the version texts
    'GearPackGive': ['+m bagLine', '+m bagParts', '~m run'],
    'GearBench': ['+f QI', '~<clinit>', '~m sweep', '~m tell'], 'GearCraftPreSys': ['~m handle'], 'GearStamp': ['~m convNote'],          # review fix 2 (item names in chat)
    'GearView': ['+m convText', '+m nameHex', '+m packText', '+m partsMsg', '+m salvText', '+m tierText', '~m descMsg', '~m sig'],          # + review fix 2
}
LANG = "Server/Languages/en-US/server.lang"
HEXES = {"#ffcc00", "#e8c25a", "#7ee08a", "#ff7a7a", "#7f93a6", "#55FF55", "#FFAA00", "#FFFF55", "#FF55FF", "#55FFFF", "#FF5555", "#CC66CC"}
SPANS = re.compile(r'(?:[^<]|<color is="#[0-9A-Fa-f]{6}">[^<]*</color>)*')
TAG = re.compile(r"^T[0-9]+ [A-Za-z]+(?: [A-Za-z]+)* - ")
OLD_LINES = {          # the 0.3.58 GearPackGive texts word for word
    (0, "inventory"): "[Gear] Your UT meter paid out: an orange Untiered bag - it is in your inventory.",
    (0, "feet"): "[Gear] Your UT meter paid out: an orange Untiered bag - your inventory is full, it lies at your feet.",
    (0, "boss"): "[Gear] Your UT meter paid out: an orange Untiered bag - it lies where the mob fell.",
    (3, "inventory"): "[Gear] The boss dropped a Zone 3 Mythic bag for you - it is in your inventory.",
    (3, "feet"): "[Gear] The boss dropped a Zone 3 Mythic bag for you - your inventory is full, it lies at your feet.",
    (3, "boss"): "[Gear] The boss dropped a Zone 3 Mythic bag for you - you left its world, it lies where the boss fell.",
}


def plain(t):
    return re.sub(r"</?color[^>]*>", "", t)


def lang_map(z):
    d = {}
    for l in z.read(LANG).decode("utf-8").splitlines():
        if "=" in l:
            k, v = l.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.59 - build script') and g.count('VERSION = "0.3.59"') == 1, "S header + VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", 'mk("')], [0, 0, 0], "S no class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(zn.namelist()) ^ set(zo.namelist())), [], "S no jar entry added or removed")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and zn.read(n) != zo.read(n)), sorted([LANG, "manifest.json"]),
         "S changed non-class entries = server.lang + manifest.json (no item / quality / art file)")
    a, b = lang_map(zo), lang_map(zn)
    K.eq(sorted(a), sorted(b), "S the same lang keys")
    ch = sorted(k for k in a if a[k] != b[k])
    K.check(len(ch) == 324 and all(k.startswith("items.") and k.endswith(".description") for k in ch), "S exactly the 324 uncoloured description lines changed: %d" % len(ch))
    K.check(all("<color" not in a[k] for k in ch), "S only lines that had no span before")
    K.check(all(plain(b[k]) == a[k] for k in ch), "S every changed text without its spans = the 0.3.58 text: %s" % [k for k in ch if plain(b[k]) != a[k]][:3])
    K.check(all(SPANS.fullmatch(b[k]) and b[k].isascii() for k in ch), "S spans balanced, never nested, ASCII")
    K.check(all(set(re.findall(r"#[0-9A-Fa-f]{6}", b[k])) <= HEXES for k in ch), "S only the Style Guide 15 / rarity hexes")
    K.check(all(TAG.match(a[k]) is None or b[k].startswith(TAG.match(a[k]).group(0)) for k in ch), "S the tier tag stays first and plain")
    K.check(not [k for k in b if k.endswith(".description") and "<color" not in b[k]], "S every description of the jar is colour coded")
    K.check(all(a[k] == b[k] for k in a if not k.endswith(".description")), "S every name / quality label byte-identical")
    ut = [k for k in ch if "_UT_" in k]
    K.check(ut and all('<color is="#FFAA00">Untiered</color>' in b[k] for k in ut), "S every Untiered piece says Untiered in the Untiered orange")
    sg = dict((r, b["items.Skyy_Sigil_%s.description" % r]) for r in ("Unique", "Rare", "Legendary", "Fabled", "Mythic"))
    K.check(all(('<color is="%s">%s</color>' % (h, r)) in sg[r] for r, h in (("Unique", "#FFFF55"), ("Rare", "#FF55FF"), ("Legendary", "#55FFFF"),
                                                                          ("Fabled", "#FF5555"), ("Mythic", "#CC66CC"))), "S each Sigil names its rarity in that rarity's colour")
    K.check('+ ":" + Integer.toHexString(String.valueOf(descText(id)).hashCode());' in g, "S GearView.sig adds the description hash")
    dm = g[g.index("public static @MSG@ descMsg("):g.index("public static String sig(String id, int quality")]
    K.check(dm.index("if (descTag(ds) != null) m.insert(markup(descRest(ds), @PKG@.GearDefs.C_GRAY));") < dm.index('else if (ds.indexOf("<color is=") >= 0) m.insert(markup(ds, @PKG@.GearDefs.C_GRAY));')
            < dm.index("getDescriptionTranslationMessage()"), "S descMsg: tagged -> markup(body); untagged with spans -> markup(text) (NEW); else the translation message")
    K.check('@MSG@.raw("[Gear] " + @PKG@.Gear.itemName(' not in g, "S no Gear chat line names an item in one plain colour any more (review fix 2)")
    K.eq([g.count(w) for w in ("GearView.convText(", "GearView.packText(", "GearView.tierText(", "GearView.salvText(")], [1, 1, 1, 1],
         "S each of the four item-name chat lines goes through GearView.partsMsg once")
    sw = g[g.index("public static int sweep(@IC@ in, @IC@ out"):]
    sw = sw[:sw.index('}""")')]
    K.check(sw.index("QI = @PKG@.Gear.quality(s);") < sw.index("tell(vs, s.getItemId(), how);") < sw.index("QI = -1;"),
            "S GearBench.sweep sets QI from the stack before tell() and resets it after")
    dd = os.path.join(os.path.dirname(scratch), "dumps")
    os.makedirs(dd, exist_ok=True)
    with open(os.path.join(dd, "gear.txt"), "w", encoding="utf8") as fh:
        for k in ch:
            fh.write("%s\n  before: %s\n  after:  %s\n" % (k, a[k], b[k]))
    K.notes.append("S %d changed keys dumped to %s" % (len(ch), os.path.join(dd, "gear.txt")))
    K.save()


def flat(m, acc=None):
    """a Message tree -> [(text, colour)] of every piece with text (depth first)"""
    if acc is None:
        acc = []
    t = m.getRawText()
    if t is not None and len(str(t)) > 0:
        acc.append((str(t), None if m.getColor() is None else str(m.getColor())))
    ch = m.getChildren()
    if ch is not None:
        for i in range(ch.size()):
            flat(ch.get(i), acc)
    return acc


def jhash(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return h


def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JBoolean, JArray
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng59")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    H["engine_boot"](KC(K))
    P = lambda n: JClass(PKG + n)
    View, Defs, Give, Roll = P("GearView"), P("GearDefs"), P("GearPackGive"), P("GearRoll")
    AL = JClass("java.util.ArrayList")
    GRAY = str(Defs.C_GRAY)
    lang = lang_map(zipfile.ZipFile(jar))

    # the bare boot loads no server.lang: hand this jar's texts to the REAL I18nModule's en-US map under each REAL item's own key (harness only)
    I18 = JClass("com.hypixel.hytale.server.core.modules.i18n.I18nModule")
    seeded = []
    try:
        inst = I18.get()
        mp = None if inst is None else inst.getMessages("en-US")
        for iid in ("Tool_Pickaxe_Lead_SkyWynn", "Weapon_Sword_UT_Paperweight", "Armor_UT_OasisWarden_Head"):
            it = P("Gear").item(JString(iid))
            if it is not None and mp is not None:
                mp.put(it.getDescriptionTranslationKey(), JString(lang["items.%s.description" % iid]))
                seeded.append((iid, str(it.getDescriptionTranslationKey())))
    except Exception as e_:
        K.notes.append("L could not seed the I18n map: %s" % e_)
    K.notes.append("L seeded the en-US texts of %s (the bare boot runs no I18nModule: [] = descText answers null, markup is checked on the jar's text)" % seeded)
    # ================================================================================== L markup / descMsg on the REAL lang texts
    for iid, tagged in (("Tool_Pickaxe_Lead_SkyWynn", True), ("Weapon_Sword_UT_Paperweight", False), ("Armor_UT_OasisWarden_Head", True)):
        want = lang["items.%s.description" % iid]
        live = View.descText(JString(iid))
        if live is None:
            K.notes.append("L %s: the boot has no lang text for it - markup checked on the jar's text" % iid)
            src = want
        else:
            K.eq(str(live), want, "L descText(%s) = this jar's coloured lang text" % iid)
            src = str(live)
        body = str(View.descRest(JString(src))) if tagged else src
        K.check((View.descTag(JString(src)) is not None) == tagged, "L %s: tagged %s" % (iid, tagged))
        pcs = flat(View.markup(JString(body), JString(GRAY)))
        K.eq("".join(x for x, _c in pcs), plain(body), "L markup(%s): the words unchanged" % iid)
        spans = re.findall(r'<color is="(#[0-9A-Fa-f]{6})">([^<]*)</color>', body)
        got = [(x, c.lower() if c else c) for x, c in pcs]
        K.check(all((x, h.lower()) in got for h, x in spans) and any(c == GRAY.lower() for _x, c in got),
                "L markup(%s): each span its own colour, the rest the flavour grey: %s" % (iid, got[:4]))
        if live is not None:
            txt, col = AL(), AL()
            txt.add(JString(str(View.FLAVOR)))
            col.add(None)
            d_ = JClass("org.bson.BsonDocument")()
            dm = flat(View.descMsg(JString(iid), d_, txt, col))
            K.eq("".join(x for x, _c in dm), plain(body), "L descMsg(%s) FLAVOR line = the coloured flavour text (%s branch)" % (iid, "tagged" if tagged else "NEW untagged"))
            K.check(any(c and c.lower() == spans[0][0].lower() for _x, c in dm), "L descMsg(%s): the first span's colour is drawn" % iid)
            # ======================================================================== G sig carries the description hash
            sg = str(View.sig(JString(iid), JInt(0), d_, txt, col))
            K.check(sg.endswith(":" + format(jhash(src), "x")), "G sig(%s) ends with the description hash: %s" % (iid, sg[-30:]))
    # ================================================================================== G sig ends with the description hash (whatever descText answers here)
    txt, col = AL(), AL()
    txt.add(JString("Damage 22-30"))
    col.add(JString(GRAY))
    for iid in ("Weapon_Sword_UT_Paperweight", "Weapon_Sword_Iron"):
        dsc = View.descText(JString(iid))
        sg = str(View.sig(JString(iid), JInt(0), JClass("org.bson.BsonDocument")(), txt, col))
        K.check(sg.endswith(":" + format(jhash(str(dsc) if dsc is not None else "null"), "x")), "G sig(%s) ends with the description hash: %s" % (iid, sg[-40:]))
    # ================================================================================== D descMsg: the FLAVOR line of an item without a description = nothing (unchanged path)
    tf, cf = AL(), AL()
    tf.add(JString(str(View.FLAVOR)))
    cf.add(None)
    K.eq(flat(View.descMsg(JString("Weapon_Sword_Iron"), JClass("org.bson.BsonDocument")(), tf, cf)) if View.descText(JString("Weapon_Sword_Iron")) is None else [], [],
         "D descMsg: no description text = no flavour piece (the null guard before the new branch)")
    # ================================================================================== B the bag lines
    RMY, RUT = str(Defs.R_HEX[int(Defs.R_MY)]), str(Defs.R_HEX[int(Defs.R_UT)])
    K.eq((RMY, RUT), ("#CC66CC", "#FFAA00"), "B the Mythic / Untiered colours")
    bad = []
    for z in (0, -1, 3):
        for how in ("inventory", "feet", "boss", "lost", "x"):
            for here in (False, True):
                p_ = Give.bagParts(JInt(z), JString(how), JBoolean(here))
                key = (0 if z <= 0 else 3, how)
                want = OLD_LINES.get(key)
                if z > 0 and how == "boss" and here:
                    want = None
                if want is None:
                    if p_ is not None:
                        bad.append(("no line", z, how, here, list(p_)))
                    continue
                if p_ is None or "".join(str(x) for x in list(p_)[:3]) != want:
                    bad.append((z, how, here, None if p_ is None else list(p_)))
                    continue
                hx = str(p_[3])
                if hx != (RUT if z <= 0 else RMY) or str(p_[1]) != ("Untiered bag" if z <= 0 else "Zone 3 Mythic bag"):
                    bad.append(("colour", z, how, hx, str(p_[1])))
                pcs = flat(Give.bagLine(p_))
                if [c for _x, c in pcs] != [str(Defs.C_GOLD), hx, str(Defs.C_GOLD)] or "".join(x for x, _c in pcs) != want:
                    bad.append(("bagLine", z, how, pcs))
    K.check(not bad, "B bagParts / bagLine: the 0.3.58 words, the bag in its rarity colour, no line where 0.3.58 sent none: %s" % bad[:3])
    # ================================================================================== N (review fix 2) the chat lines that name a gear item
    JStr = JClass("java.lang.String")
    jl = lambda a: "".join("" if x is None else str(x) for x in list(a))
    for q1 in (1, 3):
        K.eq(jl(View.convText(JString("Old Pick"), JInt(q1), JString("Iron Pickaxe"))),
             "[Gear] Old Pick is not used on this server - it became " + ("3 x " if q1 == 3 else "") + "Iron Pickaxe.", "N convText(q1=%d) = the 0.3.58 words" % q1)
    K.eq(jl(View.packText(JString("Zone 2 Blade"), JBoolean(True))),
         "[Gear] Zone 2 Blade is a Mythic boss drop - it is not crafted here. Bosses drop Mythic bags of their zone.", "N packText(Mythic) = the 0.3.58 words")
    K.eq(jl(View.packText(JString("Paperweight"), JBoolean(False))), "[Gear] Paperweight is an Untiered piece - it is never crafted.", "N packText(Untiered) = the 0.3.58 words")
    K.eq(jl(View.tierText(JString("Grove Bark Helmet"), JString("T2 Iron"))), "[Gear] Grove Bark Helmet - T2 Iron Gathering armor is crafted once at its first tier.",
         "N tierText = the 0.3.58 words")
    w_ = "It was moved to the bench's output slot."
    for augn, mid in ((0, " is a dropped / identified piece - salvage it with Requip's SALVAGE button, not at a Salvagebench. "),
                      (1, " carries 1 augment - a Salvagebench would destroy it. Salvage it with Requip's SALVAGE button (it asks first). "),
                      (2, " carries 2 augments - a Salvagebench would destroy them. Salvage it with Requip's SALVAGE button (it asks first). ")):
        K.eq(jl(View.salvText(JString("Iron Sword"), JInt(augn), JString(w_))), "[Gear] Iron Sword" + mid + w_, "N salvText(augn=%d) = the 0.3.58 words" % augn)
    BAD = str(Defs.C_BAD)
    tx = View.packText(JString("Zone 2 Blade"), JBoolean(True))
    cs = JArray(JStr)([None, JString(RMY), None])
    K.eq(flat(View.partsMsg(tx, cs, JString(BAD))), [("[Gear] ", BAD), ("Zone 2 Blade", RMY), (str(tx[2]), BAD)], "N partsMsg: the name in its colour, the rest the line colour")
    tx2 = View.convText(JString("A"), JInt(1), JString(""))
    K.eq([c for _x, c in flat(View.partsMsg(tx2, JArray(JStr)([None, JString("#123456"), None, JString("#654321"), None]), JString("#96a9be")))],
         ["#96a9be", "#123456", "#96a9be", "#96a9be"], "N partsMsg skips an empty piece (the empty name) and keeps the order")
    K.eq(str(View.nameHex(JString("Skyy_No_Such_Item"), JInt(-1), JString("#abcdef"))), "#abcdef", "N nameHex: no item = the line colour")
    K.eq(str(View.nameHex(JString("Weapon_Sword_Iron"), JInt(987654), JString("#abcdef"))), "#abcdef", "N nameHex: an unreadable quality index = the line colour")
    nh = str(View.nameHex(JString("Weapon_Sword_Iron"), JInt(-1), JString("#abcdef")))
    K.check(re.fullmatch(r"#[0-9A-Fa-f]{6}", nh) is not None and nh.upper() != "#AA00AA", "N nameHex(Weapon_Sword_Iron, item quality) = a 7-char hex: %s" % nh)
    qa = list(Defs.QIDX) if Defs.QIDX is not None else []
    if qa and int(qa[int(Defs.R_MY)]) >= 0:
        K.eq(str(View.nameHex(JString("x"), JInt(int(qa[int(Defs.R_MY)])), JString("#abcdef"))).upper(), "#CC66CC", "N nameHex: the Skyy_Gear Mythic quality = #CC66CC")
    else:
        K.notes.append("N the bare boot resolved no Skyy_Gear quality index (QIDX %s) - nameHex on a gear rarity checked by the line colour fallback only" % qa)
    K.eq(int(P("GearBench").QI), -1, "N GearBench.QI starts at -1 (the item's own quality)")
    K.save()


HK.run_compare = T54["run_compare54"]
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("engine58", T58["run_engine"]), ("engine57", T57["run_engine"]), ("engine56", T56["run_engine"]),
        ("engine55", T55["run_engine"]), ("engine54", T54["run_engine"]), ("live", T58["run_live"])], __file__, live=(T58["LIVE_DIR"], "Skyy_SkyyGear"))
