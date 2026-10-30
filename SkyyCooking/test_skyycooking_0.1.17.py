"""Harness for SkyyCooking 0.1.17 (tools/cooking_0_1_17_patch.py): the rarity + tooltip pass (looks only).
Build first: python tools/cooking_0_1_17_patch.py && python SkyyCooking/build_skyycooking_0.1.17.py

    python SkyyCooking/test_skyycooking_0.1.17.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.16 -> 0.1.17: only SupPage.build (the rarity squares) + the version texts; non-class entries: server.lang + manifest
  L    the lang files of both jars (no JVM): exactly every dish / Flask / Pouch description changed (items.* + server.items.*), every other
       line byte-identical; each dish text = the sectioned layout (type line, RESTORES NOW, BUFFS, GRADE, the dim last line) with
       well-formed <color> spans in the Style Guide 15 hexes only; its numbers = the 0.1.16 text's numbers in the same order (the grade head
       moved under BUFFS, the type line's Grade N first); exact texts for a Grade 2 / Grade 12 / Mushroom-only / raw snack / Flask / Pouch
  PG   EXECUTED SupPage.build into a REAL UICommandBuilder (hub_tab_kit stage, -Xverify:all): a Flask + a Pouch holding one source of every
       Quality - every row's 64 px item square = its Quality colour at 0.4, the row name the soft white rowName colour, the detail square
       #SkyySuDIf = the selected source's Quality at 0.4 (behind the 96 px icon, 4 px in), the title in its Quality; the hub page checks;
       the old 0.1.16 jar's row markup had no square (control)
  LIVE every one-time update + CookCfg / SupCfg load + the store journal on a scratch COPY of the live Skyy_SkyyCooking (NewBetaTest), twice;
       start 2 writes nothing; every live Supplies store renders both tabs (rows + squares) - live, live2
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B
import skyyui as SUI

VERSION, OLD = "0.1.17", "0.1.16"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)
PKG = "com.skyy.cooking."
SCRATCH = HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_cooking", "h"))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCooking")
EXPECT = {
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CookCfg": ["~m load"],   # the version text (no table change)
    "CookIngMig": ["~m migrate"], "CookMig": ["~m logLine", "~m migrate"], "CookTblMig": ["~m migrate"], "CookXpMig": ["~m migrate"],
    "CookNcMig": ["~m migrate"], "CookP3Mig": ["~m migrate"], "CookV3Mig": ["~m migrate"],   # the version text (WHO) only, as in every round
    "SkyyCookingPlugin": ["~m setup"],
    "SupCfg": ["~m load"],
    "SupPage": ["~m build"],   # 0.1.17: the rarity squares (row + detail)
}
_eq0 = HK.Child.eq


def _eq(self, got, want, what):
    """the compare allows manifest.json only among the non-class entries: + server.lang (the new tooltip texts, checked in phase L)"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == ["Server/Languages/en-US/server.lang", "manifest.json"], "C: non-class entries changed = server.lang + manifest.json (%s)" % sorted(got))
    return _eq0(self, got, want, what)


HK.Child.eq = _eq
MIGS = ("CookMig", "CookXpMig", "CookTblMig", "CookIngMig", "CookNcMig", "CookP3Mig", "CookV3Mig")
SOFT, DIM, HEAD, VAL, GOLD, TYPE, ACT = "#d6e4ee", "#7f93a6", "#9aacbc", "#7ee08a", "#e8c25a", "#b7cedd", "#ffcc00"
COLS = {SOFT, DIM, HEAD, VAL, GOLD, TYPE, ACT}
SPAN = re.compile(r'<color is="(#[0-9a-f]{6})">([^<]*)</color>')
NUM = re.compile(r"\d+(?:\.\d+)?")
NL = "\\n"   # the lang file's line break (backslash n)


def c(h, t):
    return '<color is="%s">%s</color>' % (h, t)


def plain(t):
    return re.sub(r'<color is="#[0-9a-f]{6}">|</color>', "", t)


def lang(j):
    return zipfile.ZipFile(j).read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n")


def kv(lines):
    return [tuple(l.split("=", 1)) for l in lines if "=" in l]


# ======================================================================================================== L: the lang texts (no JVM)
def run_lang(out, jar, scratch, _home):
    K = HK.Child(out)
    new, old = lang(jar), lang(OLD_JAR)
    nk, ok_ = kv(new), kv(old)
    K.check([k for k, v in nk] == [k for k, v in ok_] and len(new) == len(old), "L the same %d lang keys in the same order" % len(nk))
    O = dict(ok_)
    ch = [(k, v) for k, v in nk if v != O[k]]
    sup = ["%sSkyy_%s.description" % (p, s) for p in ("items.", "server.items.") for s in ("Flask", "Food_Pouch")]
    dish = [(k, v) for k, v in ch if k not in sup]
    K.check(sorted(k for k, v in ch if k in sup) == sorted(sup), "L the Flask + Pouch descriptions changed (items. + server.items.)")
    K.check(all(k.endswith(".description") for k, v in ch) and all("Eats 25% faster" in O[k] for k, v in dish) and len(dish) == 2 * 501,
            "L only descriptions changed: every dish text (%d = 2 x 501) + Flask + Pouch; every other line byte-identical" % len(dish))
    K.check(not [k for k, v in nk if "Eats 25% faster" in v and v == O[k]], "L no dish text left in the 0.1.16 wording")
    bad_span, bad_fact, bad_shape = [], [], []
    seen = {"raw": 0, "g0": 0, "g": 0, "mush": 0, "g11": 0}
    for k, v in dish:
        o = O[k]
        spans = SPAN.findall(v)
        if set(h for h, t in spans) - COLS or SPAN.sub("", v).count("<") or v.count("<color") != len(spans) or "#ffffff" in v:
            bad_span.append(k)
        m = re.search(r"_G(\d+)\.description$", k)
        g = int(m.group(1)) if m else 0
        raw = "- a raw snack." in o
        on = NUM.findall(plain(o))
        nh = 0 if not g else (4 if g <= 10 else 3)
        if NUM.findall(plain(v)) != ([] if raw else [str(g)]) + on[nh:-1] + on[:nh] + on[-1:] or on[-1] != "25":
            bad_fact.append(k)
        secs = v.split(NL + NL)
        typ = c(TYPE, "RAW SNACK") if raw else c(TYPE, "FOOD") + c(DIM, " - ") + c(GOLD, "Grade %d" % g)
        hs = [s.split(NL)[0] for s in secs[1:-1]]
        want_h = ([c(HEAD, "RESTORES NOW")] if "Instantly restores" in o else []) + ([c(HEAD, "BUFFS")] if "Duration:" in o else []) + \
                 ([c(HEAD, "GRADE")] if g else [])
        if not secs[0].startswith(typ + NL) or hs != want_h or secs[-1] != c(DIM, "Eats 25% faster; getting hit never stops you eating."):
            bad_shape.append((k, hs))
        if g:
            gs = secs[-2]
            if (g <= 10 and c(GOLD, "Cooking %d" % (10 * g)) not in gs) or (g > 10 and "only a Cooking skill tree bonus reaches it" not in gs) \
                    or not re.search(re.escape('<color is="%s">x' % VAL) + r"[0-9.]+ stronger</color>", gs)                     or not re.search(re.escape('<color is="%s">x' % VAL) + r"[0-9.]+ longer</color>", gs):
                bad_shape.append((k, "grade"))
        for s in secs:
            if s.startswith(c(HEAD, "BUFFS")):
                for ln in s.split(NL)[1:-1]:
                    if not (ln.startswith("• " + '<color is="%s">' % SOFT) and c(DIM, "(") in ln and '<color is="%s">' % VAL in ln):
                        bad_shape.append((k, ln))
                if not re.search(re.escape(c(SOFT, "Duration ")) + re.escape('<color is="%s">' % GOLD) + r"\d+:\d\d</color>$", s):
                    bad_shape.append((k, "duration"))
        seen["raw" if raw else ("g" if g else "g0")] += 1
        seen["mush"] += int("Instantly restores" not in o)
        seen["g11"] += int(g > 10)
    K.check(not bad_span, "L every span well-formed, Style Guide 15 colours only, no white #ffffff left (%s)" % bad_span[:3])
    K.check(not bad_fact, "L every dish keeps the 0.1.16 numbers in order (grade head moved under BUFFS) (%s)" % bad_fact[:3])
    K.check(not bad_shape, "L every dish: type line / RESTORES NOW / BUFFS (bullets: name soft white, (dim, values green), Duration gold) / "
            "GRADE / the dim last line (%s)" % bad_shape[:3])
    K.check(seen["raw"] > 0 and seen["g0"] > 0 and seen["g"] > 0 and seen["g"] % 24 == 0 and seen["raw"] + seen["g0"] + seen["g"] == 1002,
            "L kinds seen (raw / Grade 0 / Grade 1-12, x2 prefixes): %s" % seen)
    K.check(seen["mush"] > 0 and seen["g11"] > 0, "L a Mushroom-only dish and Grade 11-12 dishes are among them (%s)" % seen)
    N = dict(nk)
    meat2 = N["server.items.Skyy_Cook_Food_Pie_Meat_G2.description"]
    want2 = NL.join([
        c(TYPE, "FOOD") + c(DIM, " - ") + c(GOLD, "Grade 2"), c(SOFT, "Health + Stamina food") + " " + c(DIM, "(Meat, Grain)"), "",
        c(HEAD, "RESTORES NOW"), c(VAL, "5.9%") + " " + c(SOFT, "health"), c(VAL, "44.3%") + " " + c(SOFT, "stamina"), "",
        c(HEAD, "BUFFS"),
        "• " + c(SOFT, "Health Regen") + " " + c(DIM, "(") + c(VAL, "0.6%") + c(DIM, " health every 2 s, ") + c(VAL, "+5%") + c(DIM, " max health)"),
        "• " + c(SOFT, "Stamina Boost") + " " + c(DIM, "(") + c(VAL, "+44.5%") + c(DIM, " max stamina, ") + c(VAL, "+0.074") + c(DIM, " stamina every 0.1 s)"),
        c(SOFT, "Duration ") + c(GOLD, "7:55"), "",
        c(HEAD, "GRADE"), c(SOFT, "Grade 2 food") + c(DIM, " - ") + c(GOLD, "Cooking 20") + c(DIM, " (or sooner with Cooking tree bonuses)"),
        c(SOFT, "Heal and buffs ") + c(VAL, "x1.64 stronger"), c(SOFT, "Buffs last ") + c(VAL, "x1.32 longer"), "",
        c(DIM, "Eats 25% faster; getting hit never stops you eating.")])
    K.eq(meat2, want2, "L Meat Pie Grade 2: the exact sectioned text")
    K.eq(N["items.Skyy_Cook_Food_Pie_Meat_G2.description"], want2, "L items.* = server.items.* (Meat Pie Grade 2)")
    g12 = N["server.items.Skyy_Cook_Food_Pie_Meat_G12.description"]
    K.check((NL + NL + c(HEAD, "GRADE") + NL + c(SOFT, "Grade 12 food") + c(DIM, " - only a Cooking skill tree bonus reaches it") + NL
             + c(SOFT, "Heal and buffs ") + c(VAL, "x4.84 stronger") + NL + c(SOFT, "Buffs last ") + c(VAL, "x5.28 longer") + NL + NL) in g12,
            "L Meat Pie Grade 12: the tree-only wording, x4.84 / x5.28 green")
    mu = N["server.items.Skyy_Cook_Food_Kebab_Mushroom_G0.description"]
    K.eq(mu, NL.join([c(TYPE, "FOOD") + c(DIM, " - ") + c(GOLD, "Grade 0"), c(SOFT, "Strength food") + " " + c(DIM, "(Mushroom)"), "",
                      c(HEAD, "BUFFS"), "• " + c(SOFT, "Strength +4.1") + " " + c(DIM, "(") + c(VAL, "4.1%") + c(DIM, " more damage)"),
                      c(SOFT, "Duration ") + c(GOLD, "6:00"), "", c(DIM, "Eats 25% faster; getting hit never stops you eating.")]),
         "L Mushroom Kebab Grade 0: no RESTORES NOW section, no GRADE section")
    rb = N["server.items.Skyy_Cook_Food_Beef_Raw_G0.description"]
    K.eq(rb, NL.join([c(TYPE, "RAW SNACK"), c(SOFT, "Stamina food") + " " + c(DIM, "(Meat)"), "", c(HEAD, "RESTORES NOW"),
                      c(VAL, "5%") + " " + c(SOFT, "stamina"), "", c(DIM, "Eats 25% faster; getting hit never stops you eating.")]),
         "L raw beef: RAW SNACK, no grade, no buffs")
    st = [m for m in re.finditer(r"Strength \+[0-9.]+</color> " + re.escape(c(DIM, "(")) + r"[^\\]*", "\n".join(v for k, v in dish)) if "for " in m.group(0)]
    K.check(all(re.search(re.escape(c(DIM, " more damage, for ")) + re.escape('<color is="%s">' % GOLD) + r"\d+:\d\d</color>" + re.escape(c(DIM, ")")), m.group(0)) for m in st),
            "L a capped Strength buff shows its own time in gold (%d bullets)" % len(st))

    def sup_want(what, holds, verb, cmd):
        return NL.join([c(TYPE, "STORAGE") + c(DIM, " - ") + c(SOFT, what), "", c(HEAD, "HOLDS"), c(SOFT, holds), "", c(HEAD, "USE"),
                        c(ACT, "Right click:") + " " + c(SOFT, verb + " the weakest first"),
                        c(ACT, "Crouch + right click:") + " " + c(SOFT, "open it (Storage") + " > " + c(SOFT, "Supplies, " + cmd + ")")])
    for p in ("items.", "server.items."):
        K.eq(N[p + "Skyy_Flask.description"], sup_want("Potions", "Holds your healing potions - they go in by themselves.", "drink", "/flask"), "L %sSkyy_Flask: sectioned" % p)
        K.eq(N[p + "Skyy_Food_Pouch.description"], sup_want("Food", "Holds your cooked food - it goes in by itself.", "eat", "/pouch"), "L %sSkyy_Food_Pouch: sectioned" % p)
    for s_ in ("Flask", "Food_Pouch"):
        a, b = plain(N["server.items.Skyy_%s.description" % s_]).replace(NL, " "), O["server.items.Skyy_%s.description" % s_]
        K.check(all(w in a for w in re.findall(r"[A-Za-z/>+]+", b) if w not in ("Right", "click", "Crouch", "right")) and "Right click:" in a,
                "L %s: every word of the 0.1.16 sentence kept (%s)" % (s_, a[:90]))
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    chg = sorted(n for n in set(z.namelist()) & set(oz.namelist()) if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(chg, ["Server/Languages/en-US/server.lang", "manifest.json"], "L the changed non-class entries = server.lang + manifest.json")
    K.eq(sorted(set(z.namelist()) ^ set(oz.namelist())), [], "L no entry added or removed (no item / asset change)")
    K.save()


# ======================================================================================================== PG / LIVE: the Supplies page, EXECUTED
def frames(cmds):
    """the markup of every append: row square colours by row index, the row name colour, the detail square + title colour"""
    mk = "\n".join(t for ty, s, t, d in cmds if t is not None and ty and "Append" in ty)
    rows = dict((int(m.group(1)), m.group(2)) for m in re.finditer(r"Group #SkyySuR(\d+)F0 \{ Anchor: \(Width: 64, Height: 64[^)]*\); Background: ([^;]+);", mk))
    names = dict((int(m.group(1)), m.group(2)) for m in re.finditer(r"#SkyySuR(\d+)Nm \{[^}]*?TextColor: (#[0-9a-fA-F()., ]+?)[,)]", mk))
    det = re.search(r"Group #SkyySuDIf \{ Anchor: \(Width: 104, Height: 104\); Background: ([^;]+);", mk)
    dic = re.search(r"#SkyySuDIc \{ Anchor: \(Width: 96, Height: 96, Left: 4, Top: 4\)", mk)
    dnm = re.search(r"#SkyySuDNm \{[^}]*?TextColor: (#[0-9a-fA-F]{6})", mk)
    return rows, names, det.group(1) if det else None, bool(dic), dnm.group(1) if dnm else None, mk


def sets_of(cmds):
    return dict((s, d) for ty, s, t, d in cmds if ty == "Set")


def page_stage(scratch, jar):
    import hub_tab_kit as HT
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    from jpype import JClass
    J = lambda n: JClass(PKG + n)
    J("SupLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")
    try:
        J("SupHubOpen").register()
    except Exception:
        pass
    return HT, E, J


def run_pg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HT, E, J = page_stage(scratch, jar)
    Defs, Data, Store, Page = J("SupDefs"), J("SupData"), J("SupStore"), J("SupPage")
    mods = os.path.join(scratch, "pg-mods")
    os.makedirs(os.path.join(mods, "supplies"), exist_ok=True)
    Paths = JClass("java.nio.file.Paths")
    J("SupCfg").load(Paths.get(mods))
    Store.DIR = Paths.get(mods, "supplies")
    P = E.mkp(JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000001717"), "Rarity")
    key = str(P.pr.getUuid())
    d = Data(key)
    d.ready = True
    picks = {}
    for k_, src, col in ((0, Defs.FSRC, Defs.FCOL), (1, Defs.PSRC, Defs.PCOL)):
        by = {}
        for i in range(len(src)):
            by.setdefault(str(col[i]), str(src[i]))
        picks[k_] = by
        for n, (cl, s) in enumerate(sorted(by.items())):
            d.add(k_, s, 3 + n)
    Store.DATA.put(key, d)
    qual = set(SUI.QUALITY[q] for q in ("Common", "Uncommon", "Rare", "Epic", "Legendary"))
    K.check(set(picks[1]) == qual, "PG the Pouch holds one food of every Quality (%s)" % sorted(picks[1]))
    old_ = None
    for tab in (0, 1):
        rows_src = [str(x) for x in J("SupOps").rows(d, tab)]
        for sel in [rows_src[0], rows_src[-1]]:
            pg = Page(P.pr, tab)
            pg.selSrc = sel
            built = HT.build(pg, P)
            cmds, evs = built
            rows, names, det, dic, dnm, mk = frames(cmds)
            want = dict((i, str(Defs.col(tab, s)) + "(0.4)") for i, s in enumerate(rows_src))
            K.eq(rows, want, "PG tab %d: every row's item square = its Quality at 0.4 (%d rows)" % (tab, len(rows_src)))
            K.check(names and all(v.lower() == SOFT for v in names.values()) and len(names) == len(rows_src),
                    "PG tab %d: every row name in the soft white rowName colour (%s)" % (tab, sorted(set(names.values()))))
            dc = str(Defs.col(tab, sel))
            K.eq((det, dic, dnm), (dc + "(0.4)", True, dc), "PG tab %d selected %s: the detail square = its Quality at 0.4, the icon 4 px in, the title in its Quality" % (tab, sel))
            K.check("_" not in "".join(re.findall(r"#(SkyySu\w*)", mk)), "PG tab %d: no underscores in element ids" % tab)
            apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
            try:
                SUI.check_page(apps, "SkyySu")
                K.check(True, "PG tab %d: check_page (markup rules, parents, no duplicate id)" % tab)
            except Exception as e:
                K.check(False, "PG tab %d: check_page: %s" % (tab, e))
            ids = set()
            for _p, m_ in apps:
                ids |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(m_)))
            st = sets_of(cmds)
            bad = [s_ for s_ in st if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_, _t in evs if s_.lstrip("#") not in ids]
            K.check(not bad and "SkyySuDIf" in ids, "PG tab %d: every b.set and binding names an element that exists (%d sets, %d bindings) %s" % (tab, len(st), len(evs), bad[:3]))
            K.check(any(str(Defs.name(tab, rows_src[0])) in str(v) for s_, v in st.items() if s_ == "#SkyySuR0Nm.Text"), "PG tab %d: row 0's name set" % tab)
    # an empty store: no rows, the detail hint (no square)
    d2 = Data(key + "-e")
    d2.ready = True
    Store.DATA.put(key, d2)
    rows, names, det, dic, dnm, mk = frames(HT.build(Page(P.pr, 1), P)[0])
    K.check(not rows and det is None and "#SkyySuEm" in mk and "#SkyySuDHn" in mk, "PG an empty Pouch: no rows, no square, the empty line + the hint")
    K.save()


def run_pg_old(out, jar, scratch, _home):
    """control: the 0.1.16 jar drew no item square colour on its rows (the slot border) and no detail square"""
    from jpype import JClass
    K = HK.Child(out)
    HT, E, J = page_stage(scratch, OLD_JAR)
    Defs, Data, Store, Page = J("SupDefs"), J("SupData"), J("SupStore"), J("SupPage")
    mods = os.path.join(scratch, "pgo-mods")
    os.makedirs(os.path.join(mods, "supplies"), exist_ok=True)
    Paths = JClass("java.nio.file.Paths")
    J("SupCfg").load(Paths.get(mods))
    Store.DIR = Paths.get(mods, "supplies")
    P = E.mkp(JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000001716"), "Old")
    d = Data(str(P.pr.getUuid()))
    d.ready = True
    d.add(1, str(Defs.PSRC[len(Defs.PSRC) - 1]), 2)
    Store.DATA.put(str(P.pr.getUuid()), d)
    rows, names, det, dic, dnm, mk = frames(HT.build(Page(P.pr, 1), P)[0])
    K.check(rows == {0: SUI.COLOR["slotBorder"]} and det is None and names.get(0, "").lower() != SOFT,
            "PG control: 0.1.16 rows had the plain slot border %s, no detail square, a Quality-coloured name %s" % (rows, names))
    K.save()


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def run_live(out, jar, scratch, home):
    from jpype import JClass, JProxy
    K = HK.Child(out)
    HT, E, J = page_stage(scratch, jar)
    Paths = JClass("java.nio.file.Paths")
    Cfg, Store, Defs, Page = J("CookCfg"), J("SupStore"), J("SupDefs"), J("SupPage")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCookTest")

    def start():
        Cfg.FILE = Paths.get(os.path.join(home, "cooking.properties"))
        rs = dict((m, str(J(m).migrate())) for m in MIGS)
        rs["load"] = str(Cfg.load())
        rs["sup"] = str(J("SupCfg").load(Paths.get(home)))
        Store.DIR = Paths.get(home, "supplies")
        Store.DATA.clear()
        rs["journal"] = str(Store.readJournal())
        return rs
    s0 = snapd(home)
    r1 = start()
    s1 = snapd(home)
    r2 = start()
    s2 = snapd(home)
    ch1 = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k in ("cooking.properties", "config-changes.log") or k.startswith("config-history/") or k.startswith("supplies/") for k in ch1),
            "LIVE start 1 changes only the config / History / the store's own files: %s" % ch1)
    K.check(s1 == s2 and all(r2[m] == "" for m in MIGS), "LIVE start 2 writes nothing, every one-time update quiet (%s)" % dict((m, r2[m][:60]) for m in MIGS if r2[m]))
    keys = sorted(f[:-len(".properties")] for f in os.listdir(os.path.join(home, "supplies")) if f.endswith(".properties"))
    K.check(len(keys) >= 1, "LIVE live stores found: %s" % keys)
    cur = [None]
    E.bridge.put("profile:fn:key", JProxy("java.util.function.Function", dict={"apply": lambda u: cur[0]}))
    P = E.mkp(JClass("java.util.UUID").fromString("00000000-0000-0000-0000-00000000170a"), "Live")
    drawn = 0
    for key in keys:
        cur[0] = key
        d = Store.get(key)
        K.check(d is not None and not bool(d.bad), "LIVE store %s loads (not bad)" % key)
        for tab in (0, 1):
            rows, names, det, dic, dnm, mk = frames(HT.build(Page(P.pr, tab), P)[0])
            rs = [str(x) for x in J("SupOps").rows(d, tab)][:120]   # after the build (its sweep may make the store ready)
            K.eq(rows, dict((i, str(Defs.col(tab, s)) + "(0.4)") for i, s in enumerate(rs)), "LIVE %s tab %d: %d rows, each square its Quality" % (key, tab, len(rs)))
            K.check((det is None) == (not rs) and (not rs or det == dnm + "(0.4)"), "LIVE %s tab %d: the detail square = the title's Quality at 0.4 (%s)" % (key, tab, det))
            drawn += len(rs)
            K.check(bool(d.ready), "LIVE store %s is ready once the page swept (tab %d)" % (key, tab))
    s3 = snapd(home)
    K.check(all(s3.get(k) == v for k, v in s2.items() if not k.startswith("supplies/")), "LIVE drawing the pages writes no config")
    K.notes.append("LIVE stores %s, %d rows drawn; start 1 changed %s" % (keys, drawn, ch1))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("lang", run_lang), ("pg", run_pg), ("pgold", run_pg_old), ("live", run_live), ("live2", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyCooking"))
