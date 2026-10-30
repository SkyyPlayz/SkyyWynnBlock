"""Harness for SkyyArmory 0.1.49 (rarity pass: colour-coded item descriptions, Style Guide section 15; tools/armory_0_1_49_patch.py). Build first:
    python tools/armory_0_1_49_patch.py && python SkyyArmory/build_skyyarmory_0.1.49.py
    python SkyyArmory/test_skyyarmory_0.1.49.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes, line endings kept; no new class / system / command; the jar vs 0.1.48: nothing added or
               removed, changed non-class = manifest + lang only; lang: the same keys in the same order, EVERY line without its <color> spans =
               the 0.1.48 line (looks only), 131 descriptions newly coloured, the 24 that had spans byte-identical, names untouched; spans
               balanced, never nested, only #ffcc00 / #7ee08a / #ff7a7a, ASCII; the tier tag first and plain; 6 samples (Wand, Staff, Spellbook,
               Kunai, Bo staff, Soul Cage) + Gauntlet / Crossbow / old Untiered: yellow actions, red costs, green values
  X   exec     colour_desc() / strip_colour() EXECUTED from the generated script (unit cases: every action word, costs, values, a text with
               spans already, no tag, the tag kept plain) and re-run over the 0.1.48 lang = the jar's 0.1.49 lang byte for byte
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.48 -> 0.1.49: only the version-text members (EXPECT)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.49 writes nothing; start 2 = start 1
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the client drawing the spans in the hover popup (0.1.48's Spellblade / ut9 lines use the same
<color is="#..."> form) and SkyyGear's GearView keeping them in its stack tooltip.
"""
import os, sys, json, subprocess, zipfile, re, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_armory", "arm")]
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION, OLD = "0.1.49", "0.1.48"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_49_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
LANG = "Server/Languages/en-US/server.lang"
Y_, G_, R_ = '<color is="#ffcc00">%s</color>', '<color is="#7ee08a">%s</color>', '<color is="#ff7a7a">%s</color>'
EXPECT = {"ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "SkyyArmoryPlugin": ["~m setup", "~m start"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")
strip = lambda t: re.sub(r"</?color[^>]*>", "", t)


def lang_of(jar):
    with zipfile.ZipFile(jar) as z:
        return z.read(LANG).decode("utf-8")


def colour_lib():
    """the generated script's own colour pass helpers (_Y9 / _G9 / _R9 .. colour_desc), executed here as they are in the build"""
    g = open(GEN, encoding="utf8").read()
    a, b = g.index("_Y9 = '<color is="), g.index("UT9_CONTROLS = {")
    c, d = g.index('_N49 = r"'), g.index("COL49 = []")
    H = {"re": re}
    exec(compile(g[a:b] + "\n" + g[c:d], GEN + " (colour pass)", "exec"), H)
    return H


_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    kept = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    if ed == sorted(["manifest.json", LANG]):
        d["ok"] += 1
    else:
        kept.append("C: non-class entries changed = manifest + lang only: got %s" % ed[:8])
    d["fails"] = kept
    d["notes"].append("C: non-class entries changed = manifest + lang (the kit's manifest-only check replaced)")
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = compare_with_assets


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.49 - build script') and g.count('VERSION = "0.1.49"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass(")),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S nothing added, nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, sorted(["manifest.json", LANG]), "S changed non-class = manifest + lang (every item / art / interaction file byte-identical)")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace(OLD, VERSION)) == mb, "S manifest: only the Version (+ the version in Name) changed")
    la, lb = lang_of(OLD_JAR).split("\n"), lang_of(jar).split("\n")
    K.eq([x.split(" = ", 1)[0] for x in lb], [x.split(" = ", 1)[0] for x in la], "S lang: the same keys in the same order (no key added, moved or doubled)")
    K.check(len(set(x.split(" = ", 1)[0] for x in lb if " = " in x)) == len([x for x in lb if " = " in x]), "S lang: each key once")
    K.eq([i for i, (x, y) in enumerate(zip(la, lb)) if strip(y) != strip(x)], [], "S LOOKS ONLY: every 0.1.49 line without its colour spans = the 0.1.48 line")
    ch = [(x, y) for x, y in zip(la, lb) if x != y]
    K.check(len(ch) == 131 and all(".description = " in y and "<color" not in x for x, y in ch), "S 131 description lines newly coloured, nothing else (%d)" % len(ch))
    K.check(all(x == y for x, y in zip(la, lb) if "<color" in x), "S the 24 lines that had spans in 0.1.48 (9 ut9 copies, 15 Spellblade shields) byte-identical")
    K.check(all(x == y for x, y in zip(la, lb) if ".name = " in x), "S every name line untouched")
    bad = []
    for x, y in ch:
        k, t = y.split(" = ", 1)
        sp = re.findall(r'<color is="(#[0-9a-f]{6})">([^<]*)</color>', t)
        if not y.isascii() or t.count("<color ") != t.count("</color>") or t.count("<color ") != len(sp) or re.search(r"<color[^>]*>[^<]*<color", t) \
                or set(c for c, _w in sp) - {"#ffcc00", "#7ee08a", "#ff7a7a"} or not sp:
            bad.append((k, "spans", t))
        iid = k[len("items."):-len(".description")]
        m = re.match(r"T[0-9]+ [A-Za-z]+(?: [A-Za-z]+)* - ", strip(t))
        if m and not t.startswith(m.group(0)):
            bad.append((k, "tag not first + plain", t))
        tg = TT.tag_for(iid)
        if tg and strip(x.split(" = ", 1)[1]).startswith(tg + TT.SEP) != t.startswith(tg + TT.SEP):          # (Wand_Wood had no tag in 0.1.48 either)
            bad.append((k, "tier_tags tag", tg, t))
        if [w for _c, w in sp if _c == "#ffcc00" and not w.endswith(":")]:
            bad.append((k, "a yellow span that is no action label", t))
    K.eq(bad, [], "S every coloured line: ASCII, spans balanced + never nested, only the 3 Style Guide 15 colours, tier tag first and plain, yellow = action labels")
    D = dict((x.split(" = ", 1)[0][len("items."):-len(".description")], x.split(" = ", 1)[1]) for x in lb if x.startswith("items.") and ".description = " in x)
    sam = {
        "Weapon_Wand_Iron": [Y_ % "Tap:", Y_ % "Hold:", Y_ % "Right click:", " Mana. "],
        "Weapon_Staff_Iron": [Y_ % "Tap:", Y_ % "Hold 1 s:", Y_ % "Right click:"],
        "Weapon_Spellbook_Thorium": [Y_ % "Tap:", R_ % "70", "hits up to " + G_ % "5", "within " + G_ % "3.5" + " blocks", Y_ % "Hold:", R_ % "10" + " Mana + " + R_ % "5" + " Stamina"],
        "Weapon_Kunai_Thorium": [Y_ % "Tap:", "throw, " + G_ % "20" + " blocks", R_ % "5" + " Stamina + " + R_ % "3" + " Mana", Y_ % "Hold right click:"],
        "Weapon_Bo_Iron": [Y_ % "Tap:", " damage each. ", Y_ % "Hold + release:", Y_ % "Right click:"],
        "Weapon_Wand_SoulCage_Copper": [Y_ % "Hold right click:", "bind up to " + G_ % "2", R_ % "1.05" + " Mana a second for " + G_ % "7" + " damage a second",
                                        "Look 0.8 s", Y_ % "Hold left click and let go:"],
        "Weapon_Fist_Gauntlets_Copper": [Y_ % "Click:", G_ % "7.3" + " damage; every 4th is a " + G_ % "14.5" + " finisher"],
        "Weapon_Crossbow_Thorium_Wynn": ["Archer crossbow. " + Y_ % "Right click:" + " grapple bolt."],
        "Weapon_Wand_UT_SecondOpinion": [G_ % "50%" + " more", R_ % "40%" + " less damage"],
    }
    miss = [(i, w) for i, ws in sam.items() for w in ws if w not in D.get(i, "")]
    K.eq(miss, [], "S samples (Wand, Staff, Spellbook, Kunai, Bo, Soul Cage + Gauntlet, Crossbow, old Untiered): yellow actions, red costs, green values")
    for i in ("Weapon_Wand_Iron", "Weapon_Staff_Iron", "Weapon_Spellbook_Thorium", "Weapon_Kunai_Thorium", "Weapon_Bo_Iron", "Weapon_Wand_SoulCage_Copper"):
        nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", re.sub(r"<color[^>]*>[^<]*</color>", "", re.sub(r"^T[0-9]+ [A-Za-z]+ - ", "", D[i])).replace("#", ""))
        K.notes.append("S sample %s: %s   (numbers left plain: %s)" % (i, D[i], nums))
    wb = [i for i in D if i.startswith(("Weapon_Wand_", "Weapon_Staff_", "Weapon_Spellbook_", "Weapon_Kunai_")) and "_UT_" not in i and not re.search(r'<color is="#ff7a7a">[0-9.]+</color> Mana', D[i])]
    K.eq(wb, [], "S every wand / staff / spellbook / kunai / soul cage text (not the Untiered copies: no Mana number in their text) shows its Mana cost red")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: the colour pass executed
def run_exec(out, jar, scratch, home):
    K = HK.Child(out)
    H = colour_lib()
    cd, st = H["colour_desc"], H["strip_colour"]
    cases = [
        ("T5 Lead - Tap: quick shot, 4 Mana. Hold: charged shot, 12 Mana. Right click: block.",
         "T5 Lead - " + Y_ % "Tap:" + " quick shot, " + R_ % "4" + " Mana. " + Y_ % "Hold:" + " charged shot, " + R_ % "12" + " Mana. " + Y_ % "Right click:" + " block."),
        ("T3 Bronze - Tap: quick shot, 2 Mana. Hold 1.5 s: charged shot, 9 Mana.",
         "T3 Bronze - " + Y_ % "Tap:" + " quick shot, " + R_ % "2" + " Mana. " + Y_ % "Hold 1.5 s:" + " charged shot, " + R_ % "9" + " Mana."),
        ("Click: 3 quick jabs, 4.5 damage each; jab 6 is a 12 power hit. Hold + release: Rising Strike.",
         Y_ % "Click:" + " " + G_ % "3" + " quick jabs, " + G_ % "4.5" + " damage each; jab 6 is a " + G_ % "12" + " power hit. " + Y_ % "Hold + release:" + " Rising Strike."),
        ("T15 Lumen - Tap: throw, 20 blocks. Hold: teleport, 5 Stamina + 3 Mana. Hold right click: go back.",
         "T15 Lumen - " + Y_ % "Tap:" + " throw, " + G_ % "20" + " blocks. " + Y_ % "Hold:" + " teleport, " + R_ % "5" + " Stamina + " + R_ % "3" + " Mana. " + Y_ % "Hold right click:" + " go back."),
        ("Priest. Hold right click: bind up to 2 enemies. Hold left click and let go: Wings of Fate - glide.",
         "Priest. " + Y_ % "Hold right click:" + " bind up to " + G_ % "2" + " enemies. " + Y_ % "Hold left click and let go:" + " Wings of Fate - glide."),
        ("Untiered wand. Your heal orb heals 50% more. Wand shots deal 40% less damage.",
         "Untiered wand. Your heal orb heals " + G_ % "50%" + " more. Wand shots deal " + R_ % "40%" + " less damage."),
        ("T2 Iron - Click: a heavy jab, 9 damage; every 4th is a 30 finisher.", "T2 Iron - " + Y_ % "Click:" + " a heavy jab, " + G_ % "9" + " damage; every 4th is a " + G_ % "30" + " finisher."),
        ("T4 Thorium - Archer crossbow. Right click: grapple bolt.", "T4 Thorium - Archer crossbow. " + Y_ % "Right click:" + " grapple bolt."),
        ("T4 Thorium - Warrior sword. Made from Thorium bars.", "T4 Thorium - Warrior sword. Made from Thorium bars."),
        ("T9 Azurvane - Spellblade. " + Y_ % "Click:" + " bash 12 damage", "T9 Azurvane - Spellblade. " + Y_ % "Click:" + " bash 12 damage"),
        ("T12 Cinder - Look 0.9 s to make it solid. Signature (fills): up to 8 enemies.", "T12 Cinder - Look 0.9 s to make it solid. Signature (fills): up to " + G_ % "8" + " enemies."),
    ]
    bad = [(a, cd(a), w) for a, w in cases if cd(a) != w or st(cd(a)) != st(a)]
    K.eq(bad, [], "X colour_desc (executed from the generated script): %d unit cases (actions, Hold N s, costs, values, %% more / less, a text with spans, no tag, tag kept plain)" % len(cases))
    K.check(cd("T1 Copper - Tap: x") .startswith("T1 Copper - <color") and cd("Tap: x").startswith("<color"), "X the tag stays plain; an untagged text starts with its action span")
    # the whole pass re-run over the 0.1.48 lang = the jar's 0.1.49 lang
    la, lb = lang_of(OLD_JAR).split("\n"), lang_of(jar).split("\n")
    re_run = []
    for x in la:
        if x.startswith("items.") and ".description = " in x and "<color" not in x:
            k, t = x.split(".description = ", 1)
            x = k + ".description = " + cd(t)
        re_run.append(x)
    K.check(re_run == lb, "X colour_desc over the 0.1.48 lang reproduces the 0.1.49 jar's lang byte for byte (%d lines)" % len(lb))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    fp = os.path.join(home, "config.properties")
    b0 = open(fp, "rb").read()
    hashes = [HK.tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(HK.tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    t1 = open(fp, "rb").read()
    K.check(b"0.1.49" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.49 writes nothing of its own; line endings kept")
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(hashes[0]) | set(hashes[1]) if hashes[0].get(k) != hashes[1].get(k))[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
