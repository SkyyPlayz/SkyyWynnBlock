"""SkyyHud 0.3.32 harness - the approved ability icons on the Abilities widget for every class (tools/hud_0_3_32_patch.py).
Built on tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir
in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.32.py [--jar SkyyHud-0.3.32.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.31 -> 0.3.32: exactly the listed classes / members differ; non-class entries: the manifest (compared against a scratch
                copy of the 0.3.31 jar without its 10 own ability PNGs - J32 checks those are exactly the ones removed)
  J32  jar      the 10 Common/UI/Custom/SkyyHud/Abil/*.png copies are gone and nothing else; no "SkyyHud/Abil/" path left in any class;
                the real SkyyClasses 0.1.37 jar (the SET pin) ships an icon item for every one of the 8 classes and puts
                class:fn:abil + class:fn:abilPanel + class:fn:emblem (what the HUD reads)
  I32  icons    Widgets.abilModelU / abilBody on fakes of class:fn:abil (48 fields) + class:fn:abilPanel (Object[78], [b + 2] = the icon):
                for EVERY icon item SkyyClasses 0.1.37 ships (8 classes) the row draws ItemIcon #<base>I<k> with that ItemId; Icons Hide =
                no icon; a cooling row and a grey row (cannot pay, locked) get the dim cover #<base>D<k> (kit cardOverlay) over the icon, a
                ready row none; the crouch alts take slots 2 / 3's icons; a different slot id, "" (not loaded), an id with odd
                characters, a short / not-ok / throwing answer, no abilPanel (older SkyyClasses) = no icon (name only); levels off keeps
                the icons; the 0.3.24 levels unchanged ("Meteor (Lv 3)"); the 5 s cache (one abilPanel call per 25 builds); the icon
                column is in the shape (a state change re-sends) and the widths (innerW) are the 0.3.31 ones; the editor sample shows the
                Meteor + Mana Barrier runes (dimmed while cooling) only with SkyyClasses 0.1.36+ (class:fn:emblem) and Icons Show
  D32  default  Icons Show by default: WLayout.optH (field 11 "2" = chose Hide in 0.3.32+); every older line (no field, "1", "0") = Show;
                ser / parse round-trips, "2" written only for a Hide choice, the short default line unchanged; optOf for other widgets =
                l.opt; the Abilities Settings Hide / Show clicks save optH (fresh read of the layout file), another widget's opton never does;
                modelL with the built-in layout draws the icons
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the client drawing an ItemIcon inside a HUD, the 18 px picture and the dim cover's look.
Scratch: tools/dev/scratch/hudicons/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, zipfile, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HK

VERSION, PREV = "0.3.32", "0.3.31"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_REAL = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hudicons", "h")))
OLD_STRIP = os.path.join(os.path.dirname(SCRATCH), "old", "SkyyHud-%s-noabil.jar" % PREV)
CLASSES_JAR = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.37.jar")
PKG = "com.skyy.hud."
ABIL_PREFIX = "Common/UI/Custom/SkyyHud/Abil/"
OLD_PNGS = ["Meteor", "ManaBarrier", "FrostNova", "Starfall", "ArcaneBeam", "SacredHeal", "ShieldBubble", "GuardianSpirit", "Sanctuary", "MartyrsGrace"]
CLASSES8 = ["Archer", "Assassin", "Berserker", "Mage", "Monk", "Priest", "Spellblade", "Warrior"]


def strip_old():
    """a copy of the 0.3.31 jar without its 10 own ability PNGs (so the kit compare sees only the manifest change)"""
    os.makedirs(os.path.dirname(OLD_STRIP), exist_ok=True)
    zi = zipfile.ZipFile(OLD_REAL)
    with zipfile.ZipFile(OLD_STRIP, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not n.startswith(ABIL_PREFIX):
                zo.writestr(zi.getinfo(n), zi.read(n))


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def icon_items():
    """the icon items SkyyClasses 0.1.37 ships: {class: [ids]} (runes SkyyAbility_<Class>_<Id> + the passive SkyyClasses_Icon_<Id>)"""
    out = {}
    for n in zipfile.ZipFile(CLASSES_JAR).namelist():
        m = re.fullmatch(r"Server/Item/Items/SkyyClasses/SkyyAbility_([A-Za-z]+)_([A-Za-z]+)\.json", n)
        if m:
            out.setdefault(m.group(1), []).append("SkyyAbility_%s_%s" % (m.group(1), m.group(2)))
        m = re.fullmatch(r"Server/Item/Items/SkyyClasses/(SkyyClasses_Icon_[A-Za-z]+)\.json", n)
        if m:
            out.setdefault("Priest", []).append(m.group(1))   # Guardian Spirit (the Priest passive)
    return out


def run_j32(out, jar, scratch, home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_REAL), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq(sorted(na - nb), sorted(ABIL_PREFIX + i + ".png" for i in OLD_PNGS), "J32 exactly the 10 own ability PNGs left the jar")
    K.eq(sorted(nb - na), [], "J32 no file added")
    cls = b"".join(zb.read(n) for n in nb if n.endswith(".class"))
    K.check(b"SkyyHud/Abil/" not in cls, "J32 no class names the old icon folder")
    K.check(b"class:fn:abilPanel" in cls and b"class:fn:emblem" in cls, "J32 the HUD reads class:fn:abilPanel (icons) + class:fn:emblem (the sample gate)")
    if not os.path.isfile(CLASSES_JAR):
        K.check(False, "J32 SkyyClasses 0.1.37 jar missing: %s" % CLASSES_JAR)
        K.save()
        return
    it = icon_items()
    K.eq(sorted(it), CLASSES8, "J32 SkyyClasses 0.1.37 ships icon items for all 8 classes")
    K.check(sum(len(v) for v in it.values()) >= 38, "J32 ... %d icon items (%s)" % (sum(len(v) for v in it.values()), {k: len(v) for k, v in it.items()}))
    zc = zipfile.ZipFile(CLASSES_JAR)
    cc = b"".join(zc.read(n) for n in zc.namelist() if n.endswith(".class"))
    K.check(b"class:fn:abil" in cc and b"class:fn:abilPanel" in cc and b"class:fn:emblem" in cc,
            "J32 SkyyClasses 0.1.37 puts class:fn:abil, class:fn:abilPanel and class:fn:emblem")
    for c, ids in sorted(it.items()):
        for i in ids:
            K.check("Common/Icons/Items/SkyyClasses/%s.png" % i in zc.namelist() or any(n.endswith("/%s.png" % i) for n in zc.namelist()),
                    "J32 %s has its picture in SkyyClasses" % i)
    K.save()


def _panel(ids, icons, lvls=(3, 12, 1, 1), ok="ok", levels=True, n=78):
    from jpype import JClass, JArray, JObject
    Integer, Boolean, String = JClass("java.lang.Integer"), JClass("java.lang.Boolean"), JClass("java.lang.String")
    a = [None] * n
    if n > 0:
        a[0] = String(ok)
    if n > 8:
        a[8] = Boolean(levels)
    for i in range(4):
        b = 12 + 16 * i
        if b + 6 < n:
            a[b] = String(ids[i])
            a[b + 2] = None if icons[i] is None else String(icons[i])
            a[b + 6] = Integer(lvls[i])
    return JArray(JObject)(a)


def run_i32(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    t24 = load_module(os.path.join(HERE, "test_skyyhud_0.3.24.py"), "hud0324h")
    t24.JAR_IN_USE[0] = jar
    K = HK.Child(out)
    E = t24._env(scratch)
    H, bridge = E["H"], E["bridge"]
    Wid = H("Widgets")
    Long, Double, Boolean, String = JClass("java.lang.Long"), JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.String")

    @JImplements("java.util.function.Function")
    class AbilFake(object):
        def __init__(self):
            self.d = {}
            self.reset()

        def reset(self):
            self.d = {"names": ["Meteor", "Mana Barrier", "Frost Nova", "Starfall"], "ids": ["Meteor", "ManaBarrier", "FrostNova", "Starfall"],
                      "state": ["ready", "ready", "ready", "ready"], "left": [0, 0, 0, 0], "total": [0, 0, 0, 0], "crouch": False,
                      "afford": [True, True, True, True]}

        @JOverride
        def apply(self, x):
            d = self.d
            a = [None] * 48
            for i in range(4):
                a[i * 4] = String(d["names"][i])
                a[i * 4 + 1] = Long(d["left"][i])
                a[i * 4 + 2] = Long(d["total"][i])
                a[i * 4 + 3] = String(d["state"][i])
                a[16 + i] = String(d["ids"][i])
                a[20 + i] = Double(23.0)
                a[24 + i] = Double(2.0)
                a[28 + i] = Boolean(d["afford"][i])
                a[38 + i] = Long(10)
            a[32] = Boolean(d["crouch"])
            a[33] = String("Mage")
            a[36] = Boolean(False)
            return JArray(JObject)(a)

    @JImplements("java.util.function.Function")
    class PanelFake(object):
        def __init__(self):
            self.calls, self.r, self.boom = 0, None, False

        @JOverride
        def apply(self, x):
            self.calls += 1
            if self.boom:
                raise RuntimeError("boom")
            return self.r

    @JImplements("java.util.function.Function")
    class EmblemFake(object):
        @JOverride
        def apply(self, x):
            return String("")
    afn, pfn = AbilFake(), PanelFake()
    me = E["pref"](3, "Ana")
    u = me.getUuid()
    bridge.put("class:fn:abil", afn)
    bridge.put("class:fn:abilPanel", pfn)
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    lay = wdef("Abilities")
    BASE = "SkyyWAbil"

    def model(icons=True):
        Wid.ALVC.clear()
        return [None if v is None else str(v) for v in Wid.abilModelU(u, icons)]

    def body(m, sc=100):
        jm = JArray(String)([None if v is None else String(v) for v in m])
        return str(Wid.abilBody(BASE, lay, sc, jm, 6, 290 * sc // 100))

    def icon_el(k, iid):
        return re.search(r'ItemIcon #%sI%d \{ Anchor: \(Left: \d+, Top: \d+, Width: 18, Height: 18\); ItemId: "%s"; \}' % (BASE, k, re.escape(iid)), b_) is not None

    def dim_el(k):
        return re.search(r'Group #%sD%d \{ Anchor: \(Left: \d+, Top: \d+, Width: 18, Height: 18\); Background: #0a0e12\(0\.75\); \}' % (BASE, k), b_) is not None

    # ---- every icon item SkyyClasses 0.1.37 ships (all 8 classes): the row draws it as an ItemIcon by id
    it = icon_items() if os.path.isfile(CLASSES_JAR) else {}
    K.eq(sorted(it), CLASSES8, "I32 the icon items of all 8 classes (SkyyClasses 0.1.37)")
    n_ok = 0
    for c, ids in sorted(it.items()):
        for iid in ids:
            short = iid.split("_")[-1]
            afn.d["ids"] = [short, "ManaBarrier", "FrostNova", "Starfall"]
            pfn.r = _panel([short, "ManaBarrier", "FrostNova", "Starfall"], [iid, None, None, None])
            m = model(True)
            b_ = body(m)
            ok = m[6] == iid and m[13] == "1" and icon_el(0, iid) and not dim_el(0) and ("#%sI1 " % BASE) not in b_
            n_ok += 1 if ok else 0
            K.check(ok, "I32 %s %s: row 0 = ItemIcon %s (ready = no cover; row 1 without an icon = none)" % (c, short, iid))
    K.check(n_ok >= 38, "I32 %d icon items drawn" % n_ok)
    afn.reset()
    ICONS4 = ["SkyyAbility_Mage_Meteor", "SkyyAbility_Mage_ManaBarrier", "SkyyAbility_Mage_FrostNova", "SkyyAbility_Mage_Starfall"]
    IDS4 = ["Meteor", "ManaBarrier", "FrostNova", "Starfall"]
    pfn.r = _panel(IDS4, ICONS4)
    # ---- Icons Hide = no icon
    m = model(False)
    b_ = body(m)
    K.check(m[6] is None and m[11] is None and m[13] == "0" and "ItemIcon" not in b_, "I32 Icons Hide -> no icon, no column")
    K.eq((m[2], m[7]), ("Meteor (Lv 3)", "Mana Barrier (Lv 12)"), "I32 the 0.3.24 levels unchanged")
    # ---- states: ready / cooldown / cannot pay / locked
    m = model(True)
    b_ = body(m)
    K.check(icon_el(0, ICONS4[0]) and icon_el(1, ICONS4[1]) and not dim_el(0) and not dim_el(1), "I32 two ready rows: both icons, no cover")
    afn.d["state"][1], afn.d["left"][1], afn.d["total"][1] = "cooldown", 4000, 10000
    m = model(True)
    b_ = body(m)
    K.check(m[9] is not None and icon_el(1, ICONS4[1]) and dim_el(1) and not dim_el(0), "I32 a cooling row (bar shown): its icon dimmed, the ready one not")
    K.check(b_.index("#%sI1 " % BASE) < b_.index("#%sD1 " % BASE), "I32 ... the cover comes after (over) the icon")
    shape_cd = m[0]
    afn.reset()
    afn.d["afford"][0] = False
    m = model(True)
    b_ = body(m)
    K.check(m[5] == "g" and dim_el(0) and not dim_el(1), "I32 cannot pay (grey row): its icon dimmed")
    afn.reset()
    afn.d["state"][0] = "locked"
    m = model(True)
    b_ = body(m)
    K.check(m[3] == "Lv 10" and icon_el(0, ICONS4[0]) and dim_el(0), "I32 a locked row (Lv 10): icon dimmed")
    afn.reset()
    m = model(True)
    K.check(m[0] != shape_cd and "SkyyAbility_Mage_ManaBarrier" in m[0], "I32 the shape carries the icon + state (a change re-sends the widget): %s" % m[0])
    # ---- crouch: the alts' icons
    afn.d["crouch"] = True
    m = model(True)
    b_ = body(m)
    K.check(m[6] == ICONS4[2] and m[11] == ICONS4[3] and icon_el(0, ICONS4[2]) and icon_el(1, ICONS4[3]), "I32 crouch: the alts' icons (slots 2 / 3)")
    afn.reset()
    # ---- no icon cases
    pfn.r = _panel(["Starfall", "ManaBarrier", "FrostNova", "Meteor"], ICONS4)
    m = model(True)
    K.check(m[6] is None and m[11] == ICONS4[1], "I32 a different slot id -> no icon on that row only")
    pfn.r = _panel(IDS4, ["", None, ICONS4[2], ICONS4[3]])
    m = model(True)
    K.check(m[6] is None and m[11] is None and m[13] == "0", "I32 '' (item not loaded) / null -> name only, no column")
    for bad in ('Bad"Id', "Bad Id", "Bad}Id", "x" * 97):
        pfn.r = _panel(IDS4, [bad, None, None, None])
        m = model(True)
        K.check(m[6] is None, "I32 an odd id %r -> no icon (never written into the markup)" % bad[:12])
    pfn.r = _panel(IDS4, ICONS4, levels=False)
    m = model(True)
    K.check(m[6] == ICONS4[0] and m[2] == "Meteor", "I32 levels off -> the icons stay, no level")
    pfn.r = _panel(IDS4, ICONS4, lvls=(0, 0, 0, 0))
    m = model(True)
    K.check(m[6] == ICONS4[0] and m[2] == "Meteor", "I32 level 0 -> icon, no level")
    pfn.r = _panel(IDS4, ICONS4, ok="noabil")
    K.check(model(True)[6] is None, "I32 status not 'ok' -> no icon")
    pfn.r = _panel(IDS4, ICONS4, n=40)
    K.check(model(True)[6] is None, "I32 a short answer -> no icon")
    pfn.r = String("odd")
    K.check(model(True)[6] is None, "I32 not an Object[] -> no icon")
    pfn.boom = True
    m = model(True)
    K.check(m[6] is None and m[2] == "Meteor", "I32 a throwing abilPanel -> name only, no exception")
    pfn.boom = False
    bridge.remove("class:fn:abilPanel")
    m = model(True)
    K.check(m[6] is None and m[2] == "Meteor" and m[0] != "A0", "I32 no class:fn:abilPanel (older SkyyClasses) -> the widget, names only")
    bridge.put("class:fn:abilPanel", pfn)
    # ---- the 5 s cache
    pfn.r = _panel(IDS4, ICONS4)
    Wid.ALVC.clear()
    c0 = pfn.calls
    for _ in range(25):
        Wid.abilModelU(u, True)
    K.eq(pfn.calls - c0, 1, "I32 25 model builds within 5 s -> ONE abilPanel call")
    # ---- the layout path (HudMain / editor): the built-in layout = Icons Show (0.3.32 default)
    Wid.ALVC.clear()
    ml = [None if v is None else str(v) for v in Wid.modelL("Abilities", me, wdef("Abilities"))]
    K.check(ml[6] == ICONS4[0] and ml[13] == "1", "I32 modelL with the built-in layout -> icons shown (default Show)")
    hl = wdef("Abilities")
    hl.optH = True
    Wid.ALVC.clear()
    ml = [None if v is None else str(v) for v in Wid.modelL("Abilities", me, hl)]
    K.check(ml[6] is None and ml[13] == "0", "I32 modelL with Hide chosen (optH) -> no icons")
    # ---- widths: the icon column as in 0.3.31 (innerW reads m[13] only)
    m = model(True)
    jm = JArray(String)([None if v is None else String(v) for v in m])
    m2 = list(m)
    m2[6] = m2[11] = None
    m2[13] = "1"
    jm2 = JArray(String)([None if v is None else String(v) for v in m2])
    K.eq(int(Wid.innerW("Abilities", jm, 100, 6, True)), int(Wid.innerW("Abilities", jm2, 100, 6, True)), "I32 the width depends on the icon column only")
    for sc in (50, 100, 200):
        b_ = body(m, sc)
        ih = max(1, 18 * sc // 100)
        K.check(re.search(r"ItemIcon #%sI0 \{ Anchor: \(Left: \d+, Top: \d+, Width: %d, Height: %d\);" % (BASE, ih, ih), b_) is not None,
                "I32 at %d %%: the icon is %d px" % (sc, ih))
        K.check(b_.count("{") == b_.count("}"), "I32 at %d %%: balanced markup" % sc)
    # ---- the editor / Settings sample
    s = [None if v is None else str(v) for v in Wid.abilSample(True)]
    K.check(s[6] is None and s[11] is None and s[13] == "0", "I32 sample without class:fn:emblem (SkyyClasses before 0.1.36) -> no icons")
    bridge.put("class:fn:emblem", EmblemFake())
    s = [None if v is None else str(v) for v in Wid.abilSample(True)]
    K.check(s[6] == "SkyyAbility_Mage_Meteor" and s[11] == "SkyyAbility_Mage_ManaBarrier" and s[13] == "1" and s[5] == "n",
            "I32 sample with SkyyClasses 0.1.36+ -> the Meteor + Mana Barrier runes (the swallowed 0.3.24 line fixed: m[5] = n)")
    b_ = body(s)
    K.check(icon_el(0, "SkyyAbility_Mage_Meteor") and icon_el(1, "SkyyAbility_Mage_ManaBarrier") and dim_el(1) and not dim_el(0),
            "I32 sample markup: both icons, the cooling Mana Barrier dimmed")
    s = [None if v is None else str(v) for v in Wid.abilSample(False)]
    K.check(s[6] is None and s[11] is None, "I32 sample with Icons Hide -> no icons")
    K.eq((s[2], s[7]), ("Meteor (Lv 3)", "Mana Barrier (Lv 1)"), "I32 the sample names unchanged")
    bridge.remove("class:fn:abil")
    K.eq(str(Wid.abilModelU(u, True)[0]), "A0", "I32 no class:fn:abil -> hidden (A0)")
    K.save()


def run_d32(out, jar, scratch, home):
    """Icons Show by default: WLayout.optH ("2" = chose Hide in 0.3.32+), every older value = never chosen = Show"""
    from jpype import JClass
    t24 = load_module(os.path.join(HERE, "test_skyyhud_0.3.24.py"), "hud0324h")
    t24.JAR_IN_USE[0] = jar
    K = HK.Child(out)
    E = t24._env(scratch)
    H = E["H"]
    WL, Wid, LS, SP = H("WLayout"), H("Widgets"), H("LayoutStore"), H("SettingsPage")
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    d = wdef("Abilities")
    base = "1,br,460,21,100,0"
    styl = base + ",def,1,0,0,def"
    cases = [(base, False, "a default line (no field 11: the old default Hide / never touched)"),
             (styl + ",0", False, "an old explicit Show (field 11 '0')"),
             (styl + ",1,-", False, "an old long-form '1' (old default / old Hide = never chosen)"),
             (styl + ",2", True, "a 0.3.32 Hide choice (field 11 '2')"),
             (styl + ",2,-,def", True, "a 0.3.32 Hide choice in the long form")]
    for line, hid, what in cases:
        w = WL.parse(line, d)
        K.check(bool(w.optH) == hid and bool(Wid.optOf("Abilities", w)) == (not hid), "D32 %s -> icons %s" % (what, "Hide" if hid else "Show"))
        w2 = WL.parse(str(w.ser()), d)
        K.check(bool(w2.optH) == hid and bool(w2.opt) == bool(w.opt), "D32 ... round-trips through ser: %s" % w.ser())
    K.check(bool(Wid.optOf("Abilities", None)) and bool(Wid.optOf("Abilities", wdef("Abilities"))), "D32 no layout / the built-in layout -> Show")
    w = WL.parse(base, d)
    w.opt, w.optH = True, True
    K.eq(str(w.ser()), styl + ",2", "D32 a Hide choice writes field 11 '2' (0.3.31 reads it as opt true = Hide)")
    w.opt, w.optH = False, False
    K.eq(str(w.ser()), styl + ",0", "D32 a Show choice writes '0' as before")
    w.opt, w.optH = True, False
    K.eq(str(w.ser()), base, "D32 never chosen = the short default line as before")
    for wid in ("Party", "Guild", "Combat", "Feed", "Skills"):
        x = WL.parse(base, wdef(wid))
        y = WL.parse(styl + ",0", wdef(wid))
        K.check(bool(Wid.optOf(wid, x)) and not bool(Wid.optOf(wid, y)) and not x.optH and not y.optH, "D32 %s keeps its own opt (optOf = l.opt)" % wid)
    # the Settings clicks on the Abilities widget save optH (a fresh read of the layout file)
    me = E["pref"](4, "Bo")
    u = me.getUuid()
    LS.CACHE.clear()
    LS.get(u)
    ok = True
    try:
        SP(me, E["plugin"], "Abilities").handleDataEvent(None, None, '{"a":"opton"}')
    except Exception as e:
        ok = False
        K.check(False, "D32 opton on the Abilities settings: %s" % e)
    if ok:
        LS.save(u)
        LS.CACHE.clear()
        l = LS.get(u).get("Abilities")
        K.check(bool(l.optH) and bool(l.opt) and not bool(Wid.optOf("Abilities", l)), "D32 Hide click -> optH saved (fresh read), icons hidden")
        SP(me, E["plugin"], "Abilities").handleDataEvent(None, None, '{"a":"optoff"}')
        LS.save(u)
        LS.CACHE.clear()
        l = LS.get(u).get("Abilities")
        K.check(not bool(l.optH) and bool(Wid.optOf("Abilities", l)), "D32 Show click -> optH cleared (fresh read), icons shown")
        SP(me, E["plugin"], "Combat").handleDataEvent(None, None, '{"a":"opton"}')
        LS.save(u)
        LS.CACHE.clear()
        c = LS.get(u).get("Combat")
        K.check(bool(c.opt) and not bool(c.optH), "D32 opton on another widget never sets optH")
    # the model a layout asks for: default layout -> the icon column
    bridge = E["bridge"]
    K.check(bool(Wid.optOf("Abilities", LS.get(E["pref"](5, "Cy").getUuid()).get("Abilities"))), "D32 a new player's Abilities layout -> Show")
    K.save()


EXPECT = {
    "Widgets": ["+m abilIco", "+m abilIdOk", "+m optOf", "-f ADIR", "-f AICONS", "-m abilIcon", "~<clinit>", "~m abilBody", "~m abilLvOf",
                "~m abilModelU", "~m abilRow", "~m abilSample", "~m model", "~m modelL", "~m sampleU", "~m viewModel"],
    "WLayout": ["+f optH", "~m parse", "~m ser"],                     # field 11 "2" = chose Hide (Icons Show by default)
    "SettingsPage": ["~m build", "~m handleDataEvent"],               # the Icons row lights from optH; opton / optoff set it
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
}

if __name__ == "__main__":
    if "--phase" not in sys.argv:
        assert os.path.realpath(OLD_STRIP).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep)
        strip_old()
    try:
        HK.run("SkyyHud", VERSION, JAR, OLD_STRIP, PKG, SCRATCH, EXPECT, [],
               [("j32", run_j32), ("i32", run_i32), ("d32", run_d32)], os.path.abspath(__file__))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(os.path.dirname(OLD_STRIP), ignore_errors=True)
