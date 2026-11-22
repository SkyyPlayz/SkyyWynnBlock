"""Harness for SkyySacks 0.8.41 (round rar3 - tools/sacks_0_8_41_patch.py: colour-coded item texts, looks only).
Build first:
    python tools/sacks_0_8_41_patch.py && python SkyySacks/build_skyysacks_0.8.41.py

    python SkyySacks/test_skyysacks_0.8.41.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S       the patch re-generates the script byte for byte; no jar entry added / removed; the changed non-class entries = server.lang +
          manifest.json; in server.lang ONLY the 44 description lines changed, each = its 0.8.40 text plus Style Guide 15 spans (balanced,
          not nested, only the 15 hexes); every name / quality label byte-identical; the before / after text of every changed key is written
          to <scratch>/../dumps/sacks.txt
  A / C   verify (-Xverify:all) + compare 0.8.40 -> 0.8.41 (only the version texts; server.lang allowed by the S check)
  V41     (review fix 1) the /pd Void page rendered for real (the 0.8.9 Void fixture): every item cell, the selected icon and the upgrade cost
          icons carry the kit icon_cell(icon_bg=) rarity square in SacksPage.qBg(id); #SkyyVSelName in the rarity colour (white without an item);
          SacksPage.qCol = the SkyyBazaar 0.2.3 table; unknown / null ids = the faint grey, no error, a missing asset not cached
  P40 / F37 / S36 / ALL35 / BC36   every 0.8.40 harness case EXECUTED on THIS jar (regression)
  D       start twice on a scratch COPY of the live Skyy_SkyySacks (the 0.8.40 harness' live phases): no migration, no byte changed
Exit code 1 on any failure.
"""
import os, sys, json, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_40", os.path.join(HERE, "test_skyysacks_0.8.40.py"))
T40 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T40)
sys.argv = _argv
HK.run_compare = _RC
T37, T36, T35, T30, BETA = T40.T37, T40.T36, T40.T35, T40.T30, T40.BETA

VERSION = "0.8.41"
OLD_VERSION = "0.8.40"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar3fix", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyySacksPlugin": ["~m setup"],
          "SacksPage": ["+f QBG_A", "+f QBG_NONE", "+f QC", "+f QHEX", "+f QN", "+m qBg", "+m qCol", "+m qHex", "+m qName", "~<clinit>", "~m render", "~m upgradeBox"]}          # + review fix 1 (the Void page rarity squares)
if "--expect-dump" in sys.argv:
    EXPECT = {}
LANG = "Server/Languages/en-US/server.lang"
HEX15 = {"#7f93a6", "#cc66cc", "#ffcc00", "#e8c25a", "#ff7a7a"}
SPANS = re.compile(r'(?:[^<]|<color is="#[0-9a-f]{6}">[^<]*</color>)*')


def plain(t):
    return re.sub(r"</?color[^>]*>", "", t)


def lang_map(z):
    d = {}
    for l in z.read(LANG).decode("utf-8").splitlines():
        if "=" in l:
            k, v = l.split("=", 1)
            d[k] = v
    return d


def cmp_lang(base):
    """the kit's class compare, with server.lang allowed among the changed non-class entries (the static phase checks every line of it)"""
    def f(out, jar, old_jar, pkg, expect, added, removed=()):
        base(out, jar, old_jar, pkg, expect, added, removed)
        d = json.load(open(out))
        w = "C: non-class entries changed: got %r, want %r" % (sorted([LANG, "manifest.json"]), ["manifest.json"])
        if w in d["fails"]:
            d["fails"].remove(w)
            d["ok"] += 1
            d["notes"].append("C: server.lang changed as well (the colour pass, checked line by line in S)")
        json.dump(d, open(out, "w"), indent=1)
    return f


def run_static(out, jar, scratch, home):
    import subprocess, zipfile
    K = HK.Child(out)
    gen = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)
    cp = os.path.join(scratch, "regen.py")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sacks_0_8_41_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(gen, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    g, o = open(gen, encoding="utf8").read(), open(os.path.join(HERE, "build_skyysacks_%s.py" % OLD_VERSION), encoding="utf8").read()
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [0, 0, 0], "S no class / system / command added")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(zn.namelist()) ^ set(zo.namelist())), [], "S no jar entry added or removed")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and zn.read(n) != zo.read(n)), sorted([LANG, "manifest.json"]),
         "S changed non-class entries = server.lang + manifest.json")
    a, b = lang_map(zo), lang_map(zn)
    K.eq(sorted(a), sorted(b), "S the same lang keys (no key added or removed)")
    ch = sorted(k for k in a if a[k] != b.get(k))
    K.check(len(ch) == 44 and all(k.endswith(".description") for k in ch), "S exactly the 44 description lines changed: %d %s" % (len(ch), [k for k in ch if not k.endswith(".description")][:3]))
    K.check(all(plain(b[k]) == a[k] for k in ch), "S every changed text without its spans = the 0.8.40 text: %s" % [k for k in ch if plain(b[k]) != a[k]][:3])
    K.check(all(SPANS.fullmatch(b[k]) and "<color" in b[k] for k in ch), "S spans balanced, never nested, every description coloured")
    K.check(all(set(re.findall(r"#[0-9a-f]{6}", b[k])) <= HEX15 for k in ch), "S only the Style Guide 15 hexes")
    K.check(all(b[k].isascii() for k in ch), "S ASCII only")
    K.check(all(a[k] == b[k] for k in a if not k.endswith(".description")), "S every name / quality label byte-identical")
    dd = os.path.join(os.path.dirname(scratch), "dumps")
    os.makedirs(dd, exist_ok=True)
    with open(os.path.join(dd, "sacks.txt"), "w", encoding="utf8") as fh:
        for k in ch:
            fh.write("%s\n  before: %s\n  after:  %s\n" % (k, a[k], b[k]))
    K.notes.append("S %d changed keys dumped to %s" % (len(ch), os.path.join(dd, "sacks.txt")))
    K.save()


def cases41(K, L, scratch):
    """V41 (review fix 1): the /pd Void page's rarity squares + the selected name colour, EXECUTED through the 0.8.9 Void fixture (real render)"""
    from jpype import JClass, JString
    VS, SPage = L["VS"], L["SPage"]
    fresh, write_pool, player, custom_item, drain = (L[n] for n in ("fresh", "write_pool", "player", "custom_item", "drain"))
    UUID, us, jfield, pref = L["UUID"], L["us"], L["jfield"], L["pref"]
    NONE = "#797b7c(0.15)"
    K.eq([str(SPage.qCol(JString(q))) for q in ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", "Skyy_Enchanted", "Junk", "Technical", "Tool")],
         ["#c9d2dd", "#3e9049", "#2770b7", "#8b339e", "#bb8a2c", "#CC66CC", "#8b339e", "", "", ""],
         "V41 qCol: the SkyyBazaar 0.2.3 table (kit QUALITY Common..Legendary, Mythic #CC66CC, Skyy_Enchanted = Epic; Junk / Technical / Tool none)")
    K.eq(str(SPage.qCol(None)), "", "V41 qCol(null) = none")
    K.eq((str(SPage.qHex(JString("Skyy_No_Such_Item41"))), str(SPage.qBg(JString("Skyy_No_Such_Item41"))), str(SPage.qName(JString("Skyy_No_Such_Item41"), JString("#ffffff")))),
         ("", NONE, "#ffffff"), "V41 an unknown item: no rarity, the faint grey square, the default name colour")
    K.check(SPage.QHEX.get(JString("Skyy_No_Such_Item41")) is None, "V41 a missing item asset is not cached (asked again later)")
    K.eq((str(SPage.qBg(None)), str(SPage.qHex(JString("")))), (NONE, ""), "V41 null / empty id = none (no error)")
    LL, CU = "Ingredient_Leather_Light", "Ingredient_Bar_Copper"
    for i_ in (LL, CU):
        custom_item(i_, 100)
    UCBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def ucb_text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0f41")
    k = str(U)
    base = os.path.join(scratch, "void41")
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {LL: 50, CU: 7})
    VS.st(k).first = 1
    p = player(storage=[])
    for sel in (None, LL):
        pg = us.allocateInstance(SPage.class_)
        jfield(SPage.class_, "playerRef").set(pg, pref(U))
        jfield(SPage.class_, "info").set(pg, JString(""))
        jfield(SPage.class_, "amount").set(pg, JString(""))
        if sel is not None:
            jfield(SPage.class_, "sel").set(pg, JString(sel))
        pg.cat = "Smithing"
        b_, e_ = UCBc(), UEBc()
        err = None
        try:
            pg.render(b_, e_, p, k, U)
        except Exception as ex:
            err = ex
        K.check(err is None, "V41 render Smithing (sel %s) ran: %s" % (sel, err))
        t = ucb_text(b_)
        want = dict((i_, str(SPage.qBg(JString(i_)))) for i_ in (LL, CU))
        cells = re.findall(r"Group #(SkyyVCell\d+If) \{[^{}]*Background: ([^;]+);", t)
        K.check(len(cells) == 2 and all(bg in want.values() for _n, bg in cells),
                "V41 (sel %s) both item cells carry the rarity square #SkyyVCell<n>If with the item's qBg colour: %s / %s" % (sel, cells, want))
        costs = re.findall(r"Group #(SkyyVCost\d+If) \{[^{}]*Background: ([^;]+);", t)
        K.check(len(costs) == 2 and all(bg in want.values() for _n, bg in costs),
                "V41 (sel %s) the two upgrade cost icons carry the rarity square #SkyyVCost<n>If: %s" % (sel, costs))
        si = re.findall(r"Group #SkyyVSelIcIf \{[^{}]*Background: ([^;]+);", t)
        K.check(si == ([] if sel is None else [want[LL]]), "V41 (sel %s) the selected icon's square only when an item is selected: %s" % (sel, si))
        nm = re.search(r"#SkyyVSelName \{[^\n]*", t)
        wn = "#ffffff" if sel is None else str(SPage.qName(JString(sel), JString("#ffffff")))
        K.check(nm is not None and ("TextColor: %s" % wn) in nm.group(0), "V41 (sel %s) #SkyyVSelName drawn in %s: %s" % (sel, wn, None if nm is None else nm.group(0)[:200]))
    K.notes.append("V41 the bare fixture has no ItemQuality assets: qBg answered %s for the stand-in items (the table is checked by qCol)" % want)


def run_v41(out, jar, scratch, home):
    T35.T089.void_cases = cases41
    T35.T089.run_void(out, jar, scratch, home)


HK.run_compare = cmp_lang(HK.run_compare)
if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("static", run_static), ("v41", run_v41), ("p40", T40.run_p40), ("f37", T37.run_f37), ("s36", T36.run_s36), ("all35", T35.run_all35), ("bc36", T36.run_bc36),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
