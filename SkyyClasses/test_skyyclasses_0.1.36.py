"""Harness for SkyyClasses 0.1.36 (round emblems: the class emblems + ability icons in the UI; tools/classes_0_1_36_patch.py; with SkyyProfiles
0.1.17 + SkyyTrees 0.3.22). Build first:
    python tools/classes_0_1_36_patch.py && python SkyyClasses/build_skyyclasses_0.1.36.py
    python SkyyClasses/test_skyyclasses_0.1.36.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/emblems/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.35 -> 0.1.36: exactly the planned members (EXPECT) + the 2 new classes; non-class entries = manifest.json + the language
               file changed, the 5 Spellblade rune pictures (x2) changed, exactly the 17 new art items (x2 files) added
  J   jar      every art item: the PNG = the art file byte for byte (manifest sha256), the item JSON hidden (Debug quality, no Ability /
               Recipe / Interactions), its name in the language file; the Spellblade runes = the approved art (64 + the 2x HUD icon)
  X   exec     on the engine stand-ins of test_skyyclasses_0.1.25.py (its N0 set-up):
               X1 ClassArt.emblem / cardIcons / abilIcon / byName + class:fn:emblem (EmblemFn): loaded -> the item ids, not loaded -> today's
                  look (the weapons / "" / the fallback), aliases (Shaman = Monk), the Locked emblem, junk -> ""
               X2 the panel (class:fn:abilPanel): o[120 + t] = AbilDefs.ICON (the Priest's A3 node = Guardian Spirit's icon item), o[b + 2]
                  the slot rows' pictures; not loaded = ""
               X3 the bridge: setup puts class:fn:emblem, shutdown removes it (bytecode)
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order): nothing written; the live folder only read
  AA  engine-access audit
"""
import os, sys, json, shutil, zipfile, hashlib, textwrap, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS
import perfworld_kit as PW

VERSION, OLD = "0.1.36", "0.1.35"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "emblems", "cls")
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
T25 = os.path.join(HERE, "test_skyyclasses_0.1.25.py")
ADDED = ["ClassArt", "EmblemFn"]
EXPECT = {
    "AbilDefs": ["+f ICON", "~<clinit>"],          # the ability pictures
    "Abil": ["~m panel"],                          # o[b + 2] + o[120 + t] carry AbilDefs.ICON
    "ClassPage": ["~m build"],                     # the class cards: ClassArt.cardIcons
    "AbilPage": ["~m build"],                      # the ability cards: ClassArt.abilIcon
    "SkyyClassesPlugin": ["~m setup", "~m shutdown"],   # class:fn:emblem on / off + the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],          # the version text only
}
CLASSES = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]
EM_DIR = os.path.join(ROOT, "art", "class-emblems")
AB_DIR = os.path.join(ROOT, "art", "ability-icons")
SB = ["ArcaneBreach", "ElementalImbue", "Sunder", "RiftCleave", "ShatteringArc"]
ORIG_COMPARE = HK.run_compare


def art_ids():
    return (["SkyyClasses_Emblem_%s" % c for c in CLASSES] + ["SkyyClasses_Emblem_%s_Locked" % c for c in CLASSES]
            + ["SkyyClasses_Icon_GuardianSpirit"])


def run_compare36(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit's compare, then the non-class rule of THIS round (the kit's own allows manifest.json only)."""
    ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    want_ch = sorted(["Server/Languages/en-US/server.lang", "manifest.json"]
                     + ["Common/Icons/Abilities/SkyyAbility_Spellblade_%s.png" % a for a in SB]
                     + ["Common/Icons/Items/SkyyClasses/SkyyAbility_Spellblade_%s.png" % a for a in SB])
    want_new = sorted(["Common/Icons/Items/SkyyClasses/%s.png" % i for i in art_ids()] + ["Server/Item/Items/SkyyClasses/%s.json" % i for i in art_ids()])
    res = [(changed == want_ch, "C: changed non-class entries = lang + manifest + the 10 Spellblade rune pictures: %s" % changed),
           (sorted(ea - eb) == [], "C: no non-class entry removed: %s" % sorted(ea - eb)),
           (sorted(eb - ea) == want_new, "C: the new non-class entries = the 17 art items x (PNG + JSON): %s" % sorted(set(eb - ea) ^ set(want_new)))]
    ol = za.read("Server/Languages/en-US/server.lang").decode("utf8").split("\n")
    nl = zb.read("Server/Languages/en-US/server.lang").decode("utf8").split("\n")
    res.append((set(ol) <= set(nl) and sorted(set(nl) - set(ol)) == sorted("items.%s.name = " % i + n for i, n in zip(art_ids(), [
        "%s emblem" % c for c in CLASSES] + ["Locked %s emblem" % c for c in CLASSES] + ["Guardian Spirit"])),
        "C: the language file only gains the 17 art item names"))
    for ok, what in res:
        if ok:
            d["ok"] += 1
        else:
            d["fails"].append(what)
            print("FAIL", what)
    json.dump(d, open(out, "w"), indent=1)


def check_jar():
    """J: every art item in the jar (parent process, no JVM)."""
    z = zipfile.ZipFile(JAR)
    em = json.load(open(os.path.join(EM_DIR, "manifest.json"), encoding="utf8"))
    ab = json.load(open(os.path.join(AB_DIR, "manifest.json"), encoding="utf8"))
    esha = dict((f["path"], f["sha256"]) for f in em["files"] if f.get("sha256"))
    asha = dict((f["path"], f["sha256"]) for f in ab["files"] if f.get("sha256"))
    srcs = [("SkyyClasses_Emblem_%s" % c, esha["Common/Icons/ClassEmblems/%s.png" % c]) for c in CLASSES]
    srcs += [("SkyyClasses_Emblem_%s_Locked" % c, esha["Common/Icons/ClassEmblems/%s_Locked.png" % c]) for c in CLASSES]
    srcs += [("SkyyClasses_Icon_GuardianSpirit", asha["Common/Icons/Abilities/Priest/GuardianSpirit.png"])]
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf8")
    for iid, sha in srcs:
        png = z.read("Common/Icons/Items/SkyyClasses/%s.png" % iid)
        js = json.loads(z.read("Server/Item/Items/SkyyClasses/%s.json" % iid).decode("utf8"))
        HK.check(hashlib.sha256(png).hexdigest() == sha, "J: %s picture = the approved art file (sha256)" % iid)
        HK.check(js["Icon"] == "Icons/Items/SkyyClasses/%s.png" % iid and js["Quality"] == "Debug" and js["MaxStack"] == 1
                 and not (set(js) & {"Ability", "Recipe", "Interactions", "Categories"}) and js["DropOnDeath"] is False,
                 "J: %s item = icon-only, hidden (Debug quality), no Ability / Recipe / Interactions" % iid)
        HK.check(("\nitems.%s.name = " % iid) in "\n" + lang, "J: %s has its name" % iid)
    for a in SB:
        p64 = z.read("Common/Icons/Items/SkyyClasses/SkyyAbility_Spellblade_%s.png" % a)
        HK.check(hashlib.sha256(p64).hexdigest() == asha["Common/Icons/Abilities/Spellblade/%s.png" % a],
                 "J: the Spellblade rune %s wears its approved art" % a)
        hud = z.read("Common/Icons/Abilities/SkyyAbility_Spellblade_%s.png" % a)
        HK.check(hud[:8] == b"\x89PNG\r\n\x1a\n" and int.from_bytes(hud[16:20], "big") == 128, "J: ... and its 128 px HUD icon")
    # nothing outside the jar's own folders, nothing under Common/UI/Custom but the kit art
    names = z.namelist()
    HK.check(not [n for n in names if n.startswith("Common/UI/Custom/") and not n.startswith("Common/UI/Custom/SkyyKit/")],
             "J: no texture under Common/UI/Custom outside the kit folder")
    print("J. %d art items checked (picture sha256, hidden item JSON, name), %d Spellblade runes" % (len(srcs), len(SB)))


def run_exec(out, jar, scratch, _home):
    stats_zip = os.path.join(scratch, "stats.zip")
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as zi, \
            zipfile.ZipFile(stats_zip, "w") as zo:
        for n in zi.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                zo.writestr(n, zi.read(n))
    lines = open(T25, encoding="utf8").read().split("\n")
    a = lines.index("def run_exec(out, jar, scratch, _home):") + 1
    b = [i for i, l in enumerate(lines) if l.strip() == "# ---------------- X1 the pure rules"][0]
    ns = {"out": out, "jar": jar, "scratch": scratch, "_home": _home, "HK": HK, "B": B, "PKG": PKG, "ASSETS": stats_zip, "os": os, "sys": sys,
          "json": json, "shutil": shutil, "zipfile": zipfile, "time": time, "__name__": "t25setup"}
    exec(compile(textwrap.dedent("\n".join(lines[a:b])), T25 + " (N0 set-up)", "exec"), ns)
    g = lambda n: ns[n]
    K, C, ck = g("K"), g("C"), g("ck")
    from jpype import JClass, JInt
    A, AD, Defs, Cfg = g("A"), g("AD"), g("Defs"), g("Cfg")
    LOADED = g("RUNES_LOADED")
    mu, pu = g("mu"), g("pu")
    ci_m, ci_p = g("ci_m"), g("ci_p")
    Art, Emb = C("ClassArt"), C("EmblemFn")
    names = [str(x) for x in Defs.NAMES]
    ck(names == CLASSES, "X1: the class order the art ids follow: %s" % names)
    ids = art_ids()
    ck([str(x) for x in Art.EMB] == ids[:8] and [str(x) for x in Art.EMBL] == ids[8:16], "X1: ClassArt.EMB / EMBL = the emblem item ids")
    icon = [str(x) for x in AD.ICON]
    rune = [str(x) for x in AD.RUNE]
    ck(all((icon[i] == rune[i]) if rune[i] else icon[i] == "SkyyClasses_Icon_GuardianSpirit" for i in range(len(rune))) and rune.count("") == 1,
       "X1: AbilDefs.ICON = the rune ids + Guardian Spirit's icon item")
    # ---- not loaded: today's look everywhere
    LOADED.clear()
    for ci, n in enumerate(CLASSES):
        w = str(Defs.ICONS[ci]).split(",")
        ck(str(Art.emblem(ci, False)) == "" and [str(x) for x in Art.cardIcons(ci, True)] == w, "X1: %s, emblem not loaded = the weapons (%s)" % (n, w))
    ck(str(Art.abilIcon(0, "Weapon_Staff_Iron")) == "Weapon_Staff_Iron", "X1: an ability picture not loaded = the fallback")
    fn = Emb()
    ck(str(fn.apply("Warrior")) == "", "X1: class:fn:emblem with nothing loaded = \"\"")
    # ---- loaded
    for i_ in ids + icon:
        if i_:
            LOADED.add(i_)
    for ci, n in enumerate(CLASSES):
        w = str(Defs.ICONS[ci]).split(",")
        got = [str(x) for x in Art.cardIcons(ci, True)]
        ck(got == ["SkyyClasses_Emblem_" + n] + w[:3] and len(got) <= 4, "X1: %s card = emblem + first 3 weapons (%s)" % (n, got))
        ck([str(x) for x in Art.cardIcons(ci, False)][0] == "SkyyClasses_Emblem_%s_Locked" % n, "X1: %s not released = the Locked emblem first" % n)
        ck(str(fn.apply(n)) == "SkyyClasses_Emblem_" + n and str(fn.apply(n.lower() + ":locked")) == "SkyyClasses_Emblem_%s_Locked" % n
           and str(fn.apply(JInt(ci))) == "SkyyClasses_Emblem_" + n, "X1: class:fn:emblem %s / lower-case :locked / index" % n)
    ck(str(fn.apply("Shaman")) == "SkyyClasses_Emblem_Monk", "X1: an old alias (Shaman) = the Monk's emblem")
    ck(str(fn.apply("Nobody")) == "" and str(fn.apply(None)) == "" and str(fn.apply(JInt(99))) == "" and str(fn.apply(JInt(-1))) == ""
       and str(fn.apply(" : ")) == "", "X1: unknown / null / out of range / junk = \"\"")
    ck(str(Art.cardIcons(-1, True).length) == "0" and str(Art.emblem(8, False)) == "", "X1: out-of-range class index = nothing")
    for ai in range(len(icon)):
        ck(str(Art.abilIcon(ai, "X")) == icon[ai], "X1: ability %d picture = %s" % (ai, icon[ai]))
    ck(str(Art.abilIcon(-1, "X")) == "X" and str(Art.abilIcon(len(icon), "X")) == "X", "X1: no ability = the fallback")
    # ---- X2 the panel
    pp = A.panel(pu, None, False)
    pm_ = A.panel(mu, None, False)
    ck(pp is not None and str(pp[0]) == "ok" and pm_ is not None and str(pm_[0]) == "ok", "X2: the panels answer (%s / %s)" % (pp and pp[0], pm_ and pm_[0]))
    pr_nodes = [str(pp[120 + t]) for t in range(5)]
    mg_nodes = [str(pm_[120 + t]) for t in range(5)]
    want_p = [icon[int(AD.of(ci_p, t))] if int(AD.of(ci_p, t)) >= 0 else "" for t in range(5)]
    want_m = [icon[int(AD.of(ci_m, t))] if int(AD.of(ci_m, t)) >= 0 else "" for t in range(5)]
    ck(pr_nodes == want_p and "SkyyClasses_Icon_GuardianSpirit" in pr_nodes, "X2: the Priest's ability nodes = the pictures, Guardian Spirit's icon too: %s" % pr_nodes)
    ck(mg_nodes == want_m and all(mg_nodes), "X2: the Mage's ability nodes = the rune ids: %s" % mg_nodes)
    for pn, pa in (("Priest", pp), ("Mage", pm_)):
        rows = [(str(pa[12 + i * 16]), str(pa[12 + i * 16 + 2])) for i in range(4)]
        IDS = [str(x) for x in AD.IDS]
        ck(all((p == icon[IDS.index(i_)]) if i_ else p == "" for i_, p in rows), "X2: the %s loadout rows' pictures = AbilDefs.ICON: %s" % (pn, rows))
    LOADED.clear()
    pp2 = A.panel(pu, None, False)
    ck([str(pp2[120 + t]) for t in range(5)] == [""] * 5 and all(str(pp2[12 + i * 16 + 2]) == "" for i in range(4)), "X2: nothing loaded = \"\" (the readers keep their icons)")
    # ---- X3 the bridge on / off (bytecode)
    gr = PW.calls(jar)
    ck(PKG + "EmblemFn.<init>" in gr.get("SkyyClassesPlugin.setup", set()), "X3: setup creates EmblemFn (class:fn:emblem)")
    ck(PKG + "ClassArt.cardIcons" in gr.get("ClassPage.build", set()) and PKG + "ClassArt.abilIcon" in gr.get("AbilPage.build", set()),
       "X3: ClassPage.build -> cardIcons, AbilPage.build -> abilIcon (bytecode)")
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(HK.tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = HK.tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = HK.tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(not ch and o["m32"] == "", "ST start %s on a scratch COPY of the live data: nothing written (%s)" % (step, ch))
    if step == "2":
        K.check(HK.tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run_compare = run_compare36
    if "--phase" not in sys.argv:
        check_jar()
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("st1", run_st1), ("st2", run_st2)], script=__file__)
