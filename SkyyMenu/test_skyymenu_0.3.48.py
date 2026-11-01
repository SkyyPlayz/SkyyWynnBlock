"""Harness for SkyyMenu 0.3.48 (rarity + tooltip pass for the Pets tile; tools/menu_0_3_48_patch.py). Build first:
    python tools/menu_0_3_48_patch.py && python SkyyMenu/build_skyymenu_0.3.48.py
    python SkyyMenu/test_skyymenu_0.3.48.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the SkyyMenu 0.3.19 engine stand-ins, -Xverify:all):
  S    static   the patch re-runs to identical bytes; no new system / command; line endings kept; non-class jar entries = manifest only;
                MenuData.PET_RKIND = exactly the kinds of SkyyPets' SET jar PetFrames (every kind x 6 rarities present)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.47 -> 0.3.48: exactly the listed members differ
  PET  EXECUTED - the real PetTile / MenuPage.tileLook / MenuPage.put / MenuData.tooltip on pet files in scratch:
       MYTH    a Mythic Rabbit Lv 1 (pet slot), summon empty -> icon Skyy_PetIcon_Rabbit_Mythic, quality frame ON, plain title, every span
               (soft desc, dim headers, Mythic colour "Mythic Rabbit", gold Lv 1, dim empty, gold owned, dim minor), footer #ffcc00,
               names / bodies plain, <= 6 text lines
       NAMED   a renamed Epic Fox in the summon slot -> rarity-coloured name + dim "(" + "Epic Fox" + ")" + gold Lv
       GATE    no pets:fn:giveSecretEgg (SkyyPets < 0.4.19) -> 0.3.47's icon (Skyy_Menu_Icon_Pet_Rabbit), frame skipped
       KINDS   Dog (portrait, no Menu art) -> Skyy_PetIcon_Dog_Common framed; an unknown kind -> ICON_PETS, frame skipped
       EMPTY   no active pet -> "Pets", ICON_PETS, "PET SLOT  empty" dim; pi = {"bad"} / a bad file -> the red line
       CLIP    slotLine on a tiny max -> one colour, the plain text clipped first; just over max -> only a renamed pet's name shortened
       UTIL    framed(), plain(), tc(), tooltip() dim footer #ff7a7a; another tile keeps the frame skipped
       HOME    the real Home page build draws the rarity portrait in the Pets tile
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK
import skyybuild as B
import skyyui as SUI

_s45 = importlib.util.spec_from_file_location("test_skyymenu_0_3_45", os.path.join(HERE, "test_skyymenu_0.3.45.py"))
T45 = importlib.util.module_from_spec(_s45)
_s45.loader.exec_module(T45)
T35 = T45.T35
T19 = T45.T19
T29 = T35.T29

VERSION = "0.3.48"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.47.jar")
GEN = os.path.join(HERE, "build_skyymenu_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.47.py")
PATCH = os.path.join(ROOT, "tools", "menu_0_3_48_patch.py")
PETS_JAR = os.path.join(ROOT, "SkyyPets", "SkyyPets-0.4.22.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_menu", "menu")))
PKG = "com.skyy.menu."
ADDED = []
EXPECT = {
    "MenuData": ["+f PET_RKIND", "+f RAR_COL", "+f TIP_BAD", "+f TIP_DIM", "+f TIP_GOLD", "+f TIP_SOFT", "+m tc", "~<clinit>", "~m tooltip"],   # tooltip: the inlined footer colours
    "MenuUtil": ["+m plain"],
    "PetTile": ["+m framed", "+m frames", "+m rarIdx", "+m ricon", "+m slotLine", "~m body", "~m icon"],
    "MenuPage": ["~m put"],
    # the version string only (as in 0.3.47)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "SkyyMenuPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
RAR = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
RCOL = [SUI.QUALITY["Common"], SUI.QUALITY["Uncommon"], SUI.QUALITY["Rare"], SUI.QUALITY["Epic"], SUI.QUALITY["Legendary"], SUI.RARITY["Mythic"]]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.3.48"') == 1, "S VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    diff = sorted(n for n in set(zn.namelist()) | set(zo.namelist()) if not n.endswith(".class")
                  and (n not in zn.namelist() or n not in zo.namelist() or zn.read(n) != zo.read(n)))
    K.check(diff == ["manifest.json"], "S non-class jar entries changed = manifest only (no SkyyPets file shipped): %s" % diff)
    K.check(not [n for n in zn.namelist() if "PetIcon" in n or "PetFrames" in n], "S no Skyy_PetIcon file in the Menu jar")
    # the frame kinds = SkyyPets' SET jar
    import re
    ns = re.search(r"^PET_RKIND = (\[.*?\])$", g, re.M)
    rk = eval(ns.group(1)) if ns else []
    zp = zipfile.ZipFile(PETS_JAR)
    fr = sorted(n.rsplit("/", 1)[1][:-5] for n in zp.namelist() if "/PetFrames/" in n and n.endswith(".json"))
    kinds = sorted(set(i[len("Skyy_PetIcon_"):i.rindex("_")] for i in fr))
    K.eq(sorted(rk), kinds, "S PET_RKIND = the SkyyPets 0.4.22 PetFrames kinds")
    K.check(len(fr) == 288 and all(("Skyy_PetIcon_%s_%s" % (k, r)) in fr for k in rk for r in RAR), "S every kind x rarity portrait exists (%d)" % len(fr))
    q = dict((r, json.loads(zp.read([n for n in zp.namelist() if n.endswith("/Skyy_PetIcon_Rabbit_%s.json" % r)][0])).get("Quality")) for r in RAR)
    K.check(all(q[r] for r in RAR), "S each rarity portrait carries a Quality (the frame + title colour): %s" % q)
    pg = open(os.path.join(ROOT, "SkyyPets", "build_skyypets_0.4.22.py"), encoding="utf8").read()
    K.check('RARITY_COLORS = [SUI.QUALITY["Common"], SUI.QUALITY["Uncommon"], SUI.QUALITY["Rare"], SUI.QUALITY["Epic"], SUI.QUALITY["Legendary"],\n                 SUI.RARITY["Mythic"]]' in pg,
            "S SkyyPets' RARITY_COLORS is the same expression as MenuData.RAR_COL")
    K.save()


def run_pet(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_p")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_p", "Skyy_SkyyMenu")
    for sub in ("layouts", "settings"):
        os.makedirs(os.path.join(home, sub), exist_ok=True)
    pets = os.path.join(scratch, "home_p", "Skyy_SkyyPets", "pets")
    os.makedirs(pets, exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    MD, PT, MU, MH = JV("MenuData"), JV("PetTile"), JV("MenuUtil"), JV("MenuHub")
    PT.DIR = Paths.get(pets)
    br = MU.bridge()
    E.br = br
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = E.jf(UniC.class_, "playersByUuid").get(UniC.get())
    Obj = JClass("java.lang.Object")
    IGS = JClass("com.hypixel.hytale.server.core.ui.ItemGridSlot")
    f_name, f_desc, f_is = E.jf(IGS.class_, "name"), E.jf(IGS.class_, "description"), E.jf(IGS.class_, "itemStack")

    def tc(h, t):
        return '<color is="%s">%s</color>' % (h, t)

    SOFT, DIM, GOLD, BAD = "#d6e4ee", "#7f93a6", "#e8c25a", "#ff7a7a"
    K.eq([str(x) for x in MD.RAR_COL], RCOL, "MenuData.RAR_COL = SkyyPets' rarity colours (vanilla qualities + Mythic)")
    K.eq([str(MD.FOOT_COLOR), str(MD.DIM_COLOR)], ["#ffcc00", "#ff7a7a"], "footer colours = Style Guide 15 actions / costs")
    K.eq([str(MD.TIP_SOFT), str(MD.TIP_DIM), str(MD.TIP_GOLD), str(MD.TIP_BAD)], [SOFT, DIM, GOLD, BAD], "tooltip colour tokens")

    P = E.player(E.UUID.fromString("00000000-0000-0000-0000-000000003480"), name="SkyyPets048")
    byU.put(P.pr.getUuid(), P.pr)
    E.UniH.PL.add(P.pr)
    E.PLAYERS.add(P.pr)
    u = P.pr.getUuid()
    E.CM.cmds.put("pets", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    br.put("pets:fn:onxp", JString("stand-in"))
    br.put("pets:fn:giveSecretEgg", JString("stand-in"))
    MH.register()
    K.check(bool(PT.installed()), "SkyyPets stand-in installed (pets:fn:onxp + /pets)")
    pi_ = [i for i in range(len(MD.E_ACT)) if str(MD.E_ACT[i]) == "cmdc:pets" and str(MD.E_VIEW[i]) == "main"]
    K.check(len(pi_) == 1, "the Pets tile entry")
    TI = pi_[0]
    pf = os.path.join(pets, str(u) + ".properties")

    def write(lines):
        PT.CACHE.clear()
        with open(pf, "w", encoding="utf8", newline="\n") as f:
            f.write("v=1\n" + "".join(l + "\n" for l in lines))
        os.utime(pf, None)

    def openm():
        m = JV("MenuPage")(P.pr, "main")
        P.pm.openCustomPage(P.ref, P.st, m)
        E.pump(P)
        return m

    def draw(m, slot=3):
        l = [None if x is None else str(x) for x in m.tileLook(TI, False)]
        sl = JClass("java.util.ArrayList")()
        for _ in range(54):
            sl.add(None)
        m.put(sl, slot, l[0], l[1], l[2], l[3], l[4], l[5] == "dim")
        g = sl.get(slot)
        return l, g, str(f_desc.get(g)), str(f_name.get(g)), str(m.names[slot]), str(m.bodies[slot])

    # ================================================================ MYTH
    write(["active.1=a1", "pet.a1.kind=Rabbit", "pet.a1.level=1", "pet.a1.rarity=6"])
    m = openm()
    l, g, desc, nm, pname, pbody = draw(m)
    K.eq(l[0], "Skyy_PetIcon_Rabbit_Mythic", "MYTH: the icon = SkyyPets' Mythic Rabbit portrait")
    K.eq(str(f_is.get(g).getItemId()), "Skyy_PetIcon_Rabbit_Mythic", "MYTH: the slot's item stack is the portrait")
    K.check(not bool(g.isSkipItemQualityBackground()), "MYTH: the quality frame is ON (rarity frame + popup title colour)")
    K.eq(nm, "Pets - Rabbit Lv 1", "MYTH: the popup title stays plain text (no unproven setName markup)")
    K.eq(pname, "Pets - Rabbit Lv 1", "MYTH: names[] (the info line) plain")
    want = (tc(SOFT, "Your pets on this profile. Click to see them all.") + "\n\n"
            + tc(DIM, "PET SLOT  ") + tc(RCOL[5], "Mythic Rabbit") + " " + tc(GOLD, "Lv 1") + "\n"
            + tc(DIM, "SUMMON SLOT  ") + tc(DIM, "empty") + "\n"
            + tc(SOFT, "Pets owned: ") + tc(GOLD, "1") + "\n"
            + tc(DIM, "Pets stay on this profile - every profile has its own.") + "\n"
            + tc(DIM, "Command: /pets (or /pet)") + "\n\n"
            + tc("#ffcc00", "Click to open!"))
    K.eq(desc, want, "MYTH: the whole sectioned, colour-coded tooltip")
    K.check("<color" not in pbody and pbody.startswith("Your pets on this profile.") and "PET SLOT  Mythic Rabbit Lv 1" in pbody
            and "SUMMON SLOT  empty" in pbody, "MYTH: bodies[] (the info box) = the plain text: %r" % pbody)
    txt = [x for x in str(MU.plain(desc)).split("\n") if x.strip()]
    K.check(len(txt) <= 7, "MYTH: at most 6 text lines + the footer (%d)" % len(txt))
    K.check(all(len(x) <= int(JV("StatsCalc").LINE_MAX) for x in txt), "MYTH: every plain line <= LINE_MAX")
    K.check("&" not in desc, "MYTH: no raw & in the tooltip")

    # ================================================================ NAMED (profile name + renamed Epic Fox in the summon slot)
    br.put("profile:name:" + str(u), JString("Banana"))
    write(["active.1=a1", "active.2=b2", "pet.a1.kind=Rabbit", "pet.a1.level=12", "pet.a1.rarity=3",
           "pet.b2.kind=Fox", "pet.b2.name=Rusty", "pet.b2.level=40", "pet.b2.rarity=4", "pet.c3.kind=Dog"])
    m = openm()
    l, g, desc, nm, pname, pbody = draw(m)
    K.eq(l[0], "Skyy_PetIcon_Rabbit_Rare", "NAMED: the pet-slot pet's portrait (Rare)")
    K.check(desc.startswith(tc(SOFT, "Your pets on this profile (Banana). Click to see them all.") + "\n\n"), "NAMED: the profile name in the description")
    K.check((tc(DIM, "PET SLOT  ") + tc(RCOL[2], "Rare Rabbit") + " " + tc(GOLD, "Lv 12")) in desc, "NAMED: the Rare pet line")
    K.check((tc(DIM, "SUMMON SLOT  ") + tc(RCOL[3], "Rusty") + tc(DIM, " (") + tc(RCOL[3], "Epic Fox") + tc(DIM, ")") + " " + tc(GOLD, "Lv 40")) in desc,
            "NAMED: the renamed Epic Fox line: %r" % desc)
    K.check((tc(SOFT, "Pets owned: ") + tc(GOLD, "3")) in desc, "NAMED: owned 3")
    K.check("SUMMON SLOT  Rusty (Epic Fox) Lv 40" in pbody and "<color" not in pbody, "NAMED: plain body")
    br.remove("profile:name:" + str(u))

    # ================================================================ GATE (SkyyPets older than 0.4.19)
    br.remove("pets:fn:giveSecretEgg")
    write(["active.1=a1", "pet.a1.kind=Rabbit", "pet.a1.level=1", "pet.a1.rarity=6"])
    m = openm()
    l, g, desc, nm, pname, pbody = draw(m)
    K.eq(l[0], "Skyy_Menu_Icon_Pet_Rabbit", "GATE: no pets:fn:giveSecretEgg -> 0.3.47's Rabbit icon")
    K.check(bool(g.isSkipItemQualityBackground()), "GATE: frame skipped")
    K.check(PT.ricon(PT.of(u)) is None, "GATE: ricon = null")
    br.put("pets:fn:giveSecretEgg", JString("stand-in"))

    # ================================================================ KINDS
    write(["active.1=a1", "pet.a1.kind=Dog", "pet.a1.level=5"])
    m = openm()
    l, g, desc, nm, pname, pbody = draw(m)
    K.eq(l[0], "Skyy_PetIcon_Dog_Common", "KINDS: Dog (no Menu art) -> SkyyPets' Common Dog portrait (rarity default 1)")
    K.check(not bool(g.isSkipItemQualityBackground()), "KINDS: Dog framed")
    K.check((tc(RCOL[0], "Common Dog") + " " + tc(GOLD, "Lv 5")) in desc, "KINDS: Common colour")
    write(["active.1=a1", "pet.a1.kind=Unicorn", "pet.a1.level=5", "pet.a1.rarity=2"])
    m = openm()
    l, g, desc, nm, pname, pbody = draw(m)
    K.eq(l[0], str(MD.ICON_PETS), "KINDS: an unknown kind -> ICON_PETS")
    K.check(bool(g.isSkipItemQualityBackground()), "KINDS: unknown kind -> frame skipped")
    K.check((tc(RCOL[1], "Uncommon Unicorn") + " " + tc(GOLD, "Lv 5")) in desc, "KINDS: the unknown kind still listed in its rarity colour")
    bad = JArray(JString)(["ok", "Rabbit", "Rabbit", "1", "Shiny", "", "", "", "", "1"])
    K.check(PT.ricon(bad) is None and PT.rarIdx("Shiny") == -1 and PT.rarIdx(None) == -1 and PT.rarIdx("Mythic") == 5, "KINDS: an unknown rarity word -> no portrait")
    K.check(str(PT.icon(bad)) == "Skyy_Menu_Icon_Pet_Rabbit", "KINDS: unknown rarity -> 0.3.47's icon")
    K.check((tc(SOFT, "Shiny Rabbit") + " " + tc(GOLD, "Lv 1")) in str(PT.slotLine(bad, 1, "PET SLOT", 79)), "KINDS: unknown rarity -> soft white")

    # ================================================================ EMPTY + BAD
    write(["pet.c3.kind=Dog"])
    m = openm()
    l, g, desc, nm, pname, pbody = draw(m)
    K.check(l[0] == str(MD.ICON_PETS) and nm == "Pets" and bool(g.isSkipItemQualityBackground()), "EMPTY: no active pet -> 'Pets', ICON_PETS, no frame")
    K.check((tc(DIM, "PET SLOT  ") + tc(DIM, "empty")) in desc and (tc(DIM, "SUMMON SLOT  ") + tc(DIM, "empty")) in desc, "EMPTY: both slots dim 'empty'")
    b1 = str(PT.body(u, JArray(JString)(["bad"])))
    K.check((tc(BAD, "Your pet file could not be read. Ask an admin.")) in b1 and "PET SLOT" not in b1, "BAD: pi = {'bad'} -> the red line")
    b2 = str(PT.body(u, None))
    K.check(tc(BAD, "Your pet file could not be read. Ask an admin.") in b2, "BAD: pi = null -> the red line")
    PT.CACHE.clear()
    with open(pf, "w", encoding="utf8") as f:
        f.write("active.1=a1\npet.a1.kind=Rabbit\n")      # no v=1
    m = openm()
    l, g, desc, nm, pname, pbody = draw(m)
    K.check(l[0] == str(MD.ICON_PETS) and tc(BAD, "Your pet file could not be read. Ask an admin.") in desc and "could not be read" in pbody
            and "<color" not in pbody, "BAD: an unreadable file -> collar + red line, plain body")

    # ================================================================ CLIP
    lng = JArray(JString)(["ok", "SkeletonKnight", "Abcdefghijklmnopqrstuvwx", "100", "Legendary", "", "", "", "", "1"])
    s30 = str(PT.slotLine(lng, 1, "PET SLOT", 30))
    K.eq(s30, tc(RCOL[4], "PET SLOT  Abcdefghijklmnopq..."), "CLIP: a line over max -> the plain text clipped, one rarity colour")
    s79 = str(PT.slotLine(lng, 1, "SUMMON SLOT", 79))
    K.check(len(str(MU.plain(s79))) <= 79 and tc(GOLD, "Lv 100") in s79, "CLIP: the longest real line fits LINE_MAX: %r" % str(MU.plain(s79)))
    # fixer (critic 3): a renamed pet just over max loses the end of its NAME only - header grey, ( ) grey and gold level stay
    s60 = str(PT.slotLine(lng, 1, "PET SLOT", 60))
    K.eq(s60, tc(DIM, "PET SLOT  ") + tc(RCOL[4], "Abcdefghijkl...") + tc(DIM, " (") + tc(RCOL[4], "Legendary Skeleton Knight")
         + tc(DIM, ")") + " " + tc(GOLD, "Lv 100"), "CLIP-FIX: over max -> only the name shortened, every span kept")
    K.eq(len(str(MU.plain(s60))), 60, "CLIP-FIX: the shortened line is exactly max long")
    unr = JArray(JString)(["ok", "SkeletonKnight", "Skeleton Knight", "100", "Legendary", "", "", "", "", "1"])
    s20 = str(PT.slotLine(unr, 1, "PET SLOT", 20))
    K.eq(s20, tc(RCOL[4], "PET SLOT  Legenda..."), "CLIP-FIX: an unrenamed pet over max -> one colour (nothing to shorten)")
    s79u = str(PT.slotLine(unr, 1, "PET SLOT", 79))
    K.eq(s79u, tc(DIM, "PET SLOT  ") + tc(RCOL[4], "Legendary Skeleton Knight") + " " + tc(GOLD, "Lv 100"), "CLIP-FIX: unrenamed in range unchanged")

    # ================================================================ UTIL
    for ic, w in (("Skyy_PetIcon_Dog_Mythic", True), ("Skyy_PetIcon_DragonFire_Legendary", True), ("Skyy_PetIcon_Dog", False),
                  ("Skyy_PetIcon_Dog_Shiny", False), ("Skyy_Menu_Icon_Pet_Rabbit", False), ("Skyy_Menu_Icon_Pets", False), (None, False)):
        K.check(bool(PT.framed(ic)) == w, "UTIL: framed(%r) = %s" % (ic, w))
    for s_, w in (('a<color is="#fff">b</color>c', "abc"), ("plain", "plain"), ("x<color is", "x<color is"), ("", ""), ("1 < 2 > 0", "1 < 2 > 0")):
        K.eq(str(MU.plain(s_)), w, "UTIL: plain(%r)" % s_)
    K.check(MU.plain(None) is None, "UTIL: plain(null) = null")
    K.eq(str(MD.tc("#123456", "t")), tc("#123456", "t"), "UTIL: tc")
    K.eq(str(MD.tooltip("a\nb", "Not installed on this server", True)), "a\n\nb\n\n" + tc("#ff7a7a", "Not installed on this server"), "UTIL: the dim footer red #ff7a7a")
    sl = JClass("java.util.ArrayList")()
    for _ in range(54):
        sl.add(None)
    m.put(sl, 5, "Skyy_Menu_Icon_Bank", "Bank", "Your bank.\nCommand: /bank", "Click to open!", "cmdc:bank", False)
    K.check(bool(sl.get(5).isSkipItemQualityBackground()) and str(m.bodies[5]) == "Your bank.\nCommand: /bank"
            and str(f_desc.get(sl.get(5))) == "Your bank.\n\nCommand: /bank\n\n" + tc("#ffcc00", "Click to open!"),
            "UTIL: another tile keeps the frame skipped, its body unchanged, footer #ffcc00")

    # ================================================================ HOME (a pinned Pets shortcut drawn by the real grid-key path + the page build)
    write(["active.1=a1", "pet.a1.kind=Wolf", "pet.a1.level=9", "pet.a1.rarity=5"])
    m = openm()
    T29.build_page(m, P)
    key = "tile:" + str(MD.E_KEY[TI])
    sl = JClass("java.util.ArrayList")()
    for _ in range(54):
        sl.add(None)
    m.drawKey(sl, 7, key, False)
    g = sl.get(7)
    K.check(g is not None and str(f_is.get(g).getItemId()) == "Skyy_PetIcon_Wolf_Legendary" and not bool(g.isSkipItemQualityBackground()),
            "HOME: drawKey(%s) draws the Legendary Wolf portrait with its frame" % key)
    K.check(str(m.names[7]) == "Pets - Wolf Lv 9" and "<color" not in str(m.bodies[7]) and (tc(RCOL[4], "Legendary Wolf") + " " + tc(GOLD, "Lv 9")) in str(f_desc.get(g)),
            "HOME: plain names / bodies, coloured tooltip")
    K.eq(str(m.nameOf(key)), "Pets - Wolf Lv 9", "HOME: nameOf (status lines) plain")
    m.editing = True
    sl2 = JClass("java.util.ArrayList")()
    for _ in range(54):
        sl2.add(None)
    m.drawKey(sl2, 7, key, False)
    K.check(sl2.get(7) is not None and not bool(sl2.get(7).isSkipItemQualityBackground()) and str(f_name.get(sl2.get(7))) == "Pets - Wolf Lv 9",
            "HOME: the grid editor draws the same framed portrait, plain name")
    m.editing = False

    br.remove("pets:fn:onxp")
    br.remove("pets:fn:giveSecretEgg")
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("pet", run_pet), ("live", T35.run_live)], script=__file__, live=(T35.LIVE_DIR, "Skyy_SkyyMenu"))
