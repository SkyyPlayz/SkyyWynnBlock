"""Harness for SkyyArmory 0.1.39 (round LEVEL-BANDS-20, the Armory part; tools/armory_0_1_39_patch.py). Build first (tools/tier_tags.py TT_VERSION 3):
    python tools/armory_0_1_39_patch.py && python SkyyArmory/build_skyyarmory_0.1.39.py

    python SkyyArmory/test_skyyarmory_0.1.39.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.38 -> 0.1.39: only the band / zone / book / version-text members; non-class entries = manifest.json, server.lang, the 72 alloy
               weapon items (Recipe.KnowledgeRequired only), the 4 wraps (ItemLevel only), the 42 book chain / Page Burst orb files (phase B)
  OLD          (helper) the 0.1.38 jar's ArmoryDefs tables + ArmoryCfg.DEF_CFG + the fixed rows, written to the scratch folder
  B   bands    ArmoryDefs.METALS / BAND_A / BAND_B = tools/tier_tags.py TT.band() per metal (and = 0.1.38's TT_VERSION 2 table before); every
               "Lv a-b" of the Server Setup fixed rows (wands, staffs, books, kunai, bo, gauntlets, wraps) = the new band; SoulDrop.zoneOfLevel(0..150)
               = TT.ZONE_TOPS (<= 20 / 40 / 60 -> 1-3, else 4) and 0.1.38's answers = TT.ZONE_TOPS_V2; the wand / staff cost tables = 0.1.38
               (Skyy's locked table); the books = round5(30 % of the Mage pool 30 + 10 L + 0.2 floor(L / 9) at the NEW first level), all <= 40 %,
               damage per Mana unchanged, and the 42 book files differ only in those numbers; the wraps' ItemLevel = their column's start
  T   tags     per family: every item whose id carries a metal word starts its description with TT.combat_tag (and = TT.tag_for where the table
               has it); the server.lang diff vs 0.1.38 = exactly the 51 tag prefixes; the untagged rest is the expected 12 (no metal / UT / Soul Orb)
  K   knowledge exactly the 72 alloy weapons (18 families x Dusk / Azurvane / Cinder / Lumen) carry Recipe.KnowledgeRequired true; every other item
               recipe is false / absent; the 15 hidden Soul ladder twins stay true; no Armory item in Bronze has a recipe (and the 7 vanilla Bronze
               weapons have none); writes the grant table (recipe id, output id, input collections) to the scratch folder for the report
  M   migration ArmoryCfg.DEF_CFG 0.1.38 vs 0.1.39 = the same rows and values (only the essence.zone help comment + the version text differ):
               nothing to migrate (spec 4.1 "Armory ... no band rows -> none")
  D   live     a scratch COPY of Skyy's live config (NewBetaTest, read only): every migration of the jar + load, twice -> the file is byte-identical
               (no row rewritten, no marker added), the loader reads it
  S38 / E38    the 0.1.38 harness's static + engine phases (Soul Cage resource types, hidden twins, SkyyGear's Anvil ladder readers, the real
               engine counting / /craft sequence) run on the 0.1.39 jar, with the two intended 0.1.39 differences put back first (the alloy cages'
               KnowledgeRequired, the tag prefixes)
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the client's look of a locked recipe at the Weapon Bench, SkyyCollections granting the 72 ids,
SkyyGear's Smithing tab on a KnowledgeRequired recipe. Exit code 1 on any failure.
"""
import os, sys, json, zipfile, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION, OLD = "0.1.39", "0.1.38"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "arm39", "harness")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
ASSETS = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), "Assets.zip")
LANG = "Server/Languages/en-US/server.lang"
ALLOYS = ("Bronze", "Dusk", "Azurvane", "Cinder", "Lumen")
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036")
EXPECT = {"SkyyArmoryPlugin": ["~m setup", "~m start"], "ArmoryCheck": ["~m packCheck", "~m packOf"],
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
          "CfgRows2": ["~<clinit>"],          # the version text; the essence.zone help
          "ArmoryDefs": ["~<clinit>"],          # BAND_A / BAND_B
          "ArmoryHooks": ["~<clinit>"],          # the fixed rows' "Lv a-b" + the book rule words
          "SoulDrop": ["~m zoneOfLevel"]}          # TT.ZONE_TOPS


def jload(z, n):
    return json.loads(z.read(n).decode("utf-8-sig"))


def items_of(z):
    return dict((os.path.basename(n)[:-5], n) for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def alloy_of(iid):
    w = [x for x in iid.split("_")[1:] if x in ALLOYS]
    return w[0] if w else None


def gated_expected(z):
    out = []
    for iid, n in items_of(z).items():
        if alloy_of(iid) and "_UT_" not in iid and jload(z, n).get("Recipe"):
            out.append(iid)
    return sorted(out)


def lang_lines(z):
    return z.read(LANG).decode("utf-8").replace("\r\n", "\n").split("\n")


def descs(z):
    return dict((l[len("items."):].split(".description = ", 1)) for l in lang_lines(z) if l.startswith("items.") and ".description = " in l)


_TAGRX = re.compile(r"T[0-9]+ ")

with zipfile.ZipFile(JAR) as _z:
    _GATED = gated_expected(_z)
    _NEWDESC = descs(_z)
with zipfile.ZipFile(OLD_JAR) as _z:
    _OLDDESC = descs(_z)
    _CHANGED = sorted(n for n in items_of(_z).values())
TAGGED = sorted(i for i in _NEWDESC if i in _OLDDESC and _NEWDESC[i] != _OLDDESC[i])
with zipfile.ZipFile(JAR) as _zn, zipfile.ZipFile(OLD_JAR) as _zo:
    _ITEMDIFF = sorted(n for n in _zn.namelist() if n.startswith("Server/Item/Items/") and n in set(_zo.namelist()) and _zn.read(n) != _zo.read(n))
    _BOOKDIFF = sorted(n for n in _zn.namelist() if n.endswith(".json") and n.startswith("Server/") and not n.startswith("Server/Item/Items/") and n in set(_zo.namelist())
                       and _zn.read(n) != _zo.read(n))          # the book chains + Page Burst orbs (checked in phase B)
NONCLASS = sorted(["manifest.json", LANG] + _ITEMDIFF + _BOOKDIFF)
BOOK_METALS = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"] + [w + "_SkyWynn" for w in
                                                                                             ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")]
BOOK_COST = [10, 35, 70, 130, 190, 250, 310, 95, 115, 155, 175, 215, 235, 275, 295]          # 0.1.39 (main session 2026-10-18: 40 % rule at the new starts)
BOOK_DMG = [23, 82, 168, 317, 467, 618, 766, 230, 279, 379, 429, 529, 580, 680, 730]
BOOK_COST38 = [40, 55, 70, 85, 115, 130, 130, 75, 80, 95, 100, 120, 125, 145, 160]


def mage_pool(l):
    return 30 + 10 * l + 0.2 * (l // 9)

_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    E = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = NONCLASS
        return E(self, got, want, what)
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = E


# ---------------------------------------------------------------------------------------------------------------- the 0.1.38 harness (S38 / E38)
_saved = HK.run_compare
_spec = importlib.util.spec_from_file_location("arm38h", os.path.join(HERE, "test_skyyarmory_0.1.38.py"))
H38 = importlib.util.module_from_spec(_spec)
_argv = list(sys.argv)
sys.argv = [sys.argv[0]]          # its module-level HK.arg reads stay at their defaults
_spec.loader.exec_module(H38)
sys.argv = _argv
HK.run_compare = _compare          # (the 0.1.38 module installs its own compare wrapper on import - ours wins)
_ = _saved
_j38 = H38.jload
_l38 = H38.lang_of


def _norm_jload(z, n):
    d = _j38(z, n)
    if os.path.realpath(z.filename) == os.path.realpath(JAR) and n.startswith("Server/Item/Items/") and os.path.basename(n)[:-5] in _GATED:
        assert d["Recipe"]["KnowledgeRequired"] is True, n
        d["Recipe"]["KnowledgeRequired"] = False          # put the 0.1.38 value back (the one intended 0.1.39 difference of a Soul Cage file)
    return d


def _norm_lang(z):
    ls = _l38(z)
    if os.path.realpath(z.filename) != os.path.realpath(JAR):
        return ls
    out = []
    for l in ls:
        if l.startswith("items.") and ".description = " in l:
            iid = l[len("items."):].split(".description = ", 1)[0]
            if iid in TAGGED:
                l = "items.%s.description = %s" % (iid, _OLDDESC[iid])
        out.append(l)
    return out


H38.jload = _norm_jload
H38.lang_of = _norm_lang


def run_static38(out, jar, scratch, home):
    H38.run_static(out, jar, scratch, home)


def run_engine38(out, jar, scratch, home):
    H38.run_engine(out, jar, scratch, home)


# ---------------------------------------------------------------------------------------------------------------- OLD (helper) + B
DEF_FIELDS = ("METALS", "BAND_A", "BAND_B", "W_C", "S_C", "B_COST", "B_DMG")


def dump_defs(jar):
    from jpype import JClass
    D = JClass(PKG + "ArmoryDefs")
    o = {}
    for f in DEF_FIELDS:
        try:
            o[f] = [str(x) if isinstance(x, str) else int(x) for x in getattr(D, f)]
        except AttributeError:
            o[f] = None
    o["DEF_CFG"] = str(JClass(PKG + "ArmoryCfg").DEF_CFG)
    H = JClass(PKG + "ArmoryHooks")
    o["FIXED"] = dict(zip([str(x) for x in H.FIXED_KEYS], [str(x) for x in H.FIXED_VALS]))
    S = JClass(PKG + "SoulDrop")
    o["ZOL"] = [int(S.zoneOfLevel(l)) for l in range(0, 151)]
    return o


def run_old(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR], verify=True)
    o = dump_defs(OLD_JAR)
    json.dump(o, open(os.path.join(scratch, "old_defs.json"), "w"))
    K.check(o["BAND_A"] is not None, "OLD: the 0.1.38 tables read")
    K.save()


def zol_want(tops, l):
    if l <= 0:
        return -1
    for z, t in enumerate(tops[:3]):
        if l <= t:
            return z + 1
    return 4


def run_bands(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    n = dump_defs(jar)
    o = json.load(open(os.path.join(scratch, "old_defs.json")))
    json.dump(n, open(os.path.join(scratch, "new_defs.json"), "w"))
    mn = lambda m: m[:-len("_SkyWynn")] if m.endswith("_SkyWynn") else m
    K.eq(n["METALS"], o["METALS"], "B: the same 16 metals in the same order")
    K.eq([[a, b] for a, b in zip(n["BAND_A"], n["BAND_B"])], [list(TT.band(mn(m))) for m in n["METALS"]], "B: BAND_A / BAND_B = TT.band() (TT_VERSION 3) per metal")
    K.eq([[a, b] for a, b in zip(o["BAND_A"], o["BAND_B"])], [list(TT.METAL_BANDS_V2[mn(m)]) for m in o["METALS"]], "B: control - 0.1.38's table = TT_VERSION 2")
    rows = []
    for k, v in sorted(n["FIXED"].items()):
        m = re.search(r"Lv (\d+)-(\d+)", v)
        if not m:
            continue
        tail = k.split(".", 2)[2]
        wcol = {"Linen": "Copper", "Cotton": "Iron", "Silk": "Thorium", "Cindercloth": "Cobalt", "Shadoweave": "Adamantite"}
        if tail.startswith("Wraps_"):
            if tail[6:] not in wcol:
                continue
            want = TT.band(wcol[tail[6:]])
        else:
            want = TT.band(mn(tail[len("Gauntlets_"):] if tail.startswith("Gauntlets_") else tail))
        if want is None:
            rows.append((k, False, v, None))
            continue
        rows.append((k, (int(m.group(1)), int(m.group(2))) == tuple(want), v[m.start():m.end()], want))
    K.check(len(rows) >= 60 and all(r[1] for r in rows), "B: every fixed row's 'Lv a-b' = the new band (%d rows; wrong: %s)" % (len(rows), [r for r in rows if not r[1]][:5]))
    K.eq(n["ZOL"], [zol_want(TT.ZONE_TOPS, l) for l in range(0, 151)], "B: SoulDrop.zoneOfLevel(0..150) = TT.ZONE_TOPS (<= 20 / 40 / 60 -> 1-3, else 4)")
    K.eq(o["ZOL"], [zol_want(TT.ZONE_TOPS_V2, l) for l in range(0, 151)], "B: control - 0.1.38's zoneOfLevel = TT.ZONE_TOPS_V2")
    K.eq([n[f] for f in ("W_C", "S_C")], [o[f] for f in ("W_C", "S_C")], "B: the wand / staff cost tables = 0.1.38 (Skyy's locked table)")
    K.eq([n["B_COST"], n["B_DMG"], o["B_COST"]], [BOOK_COST, BOOK_DMG, BOOK_COST38], "B: the book cost / damage = the 30 %% rule at the NEW starts (0.1.38: %s)" % o["B_COST"])
    mm = lambda m: m[:-len("_SkyWynn")] if m.endswith("_SkyWynn") else m
    rp = [(m, c, round(100.0 * c / mage_pool(TT.band(mm(m))[0]))) for m, c in zip(BOOK_METALS, n["B_COST"])]
    K.check(all(c == 5 * int(0.30 * mage_pool(TT.band(mm(m))[0]) / 5.0 + 0.5 + 1e-9) for m, c in zip(BOOK_METALS, n["B_COST"])) and all(q <= 40 for _m, _c, q in rp),
            "B: every book = round5(30 %% of the Mage pool at its new first level), all <= 40 %%: %s" % rp)
    K.check(all(abs(d / float(c) - d0 / float(c0)) < 0.05 for c, d, c0, d0 in zip(n["B_COST"], n["B_DMG"], o["B_COST"], o["B_DMG"])),
            "B: damage per Mana of every book unchanged (the curve keeps its shape)")
    # the 42 book files: only the Mana cost / damage numbers moved, to the new values
    badf = []
    with zipfile.ZipFile(jar) as zn, zipfile.ZipFile(OLD_JAR) as zo:
        for p in _BOOKDIFF:
            m = [b for b in BOOK_METALS if p.endswith("_%s.json" % b)]
            if "Spellbook" not in p or len(m) != 1:
                badf.append(p)
                continue
            i = BOOK_METALS.index(m[0])
            olds, news = [], []

            def walk(a, b):
                if isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b):
                    for k in a:
                        walk(a[k], b[k])
                elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
                    for x, y in zip(a, b):
                        walk(x, y)
                elif a != b:
                    olds.append(a)
                    news.append(b)
            walk(jload(zo, p), jload(zn, p))
            okv = lambda v, c, d: isinstance(v, (int, float)) and abs(v) in (c, d)
            if not olds or not all(okv(v, o["B_COST"][i], o["B_DMG"][i]) for v in olds) or not all(okv(v, BOOK_COST[i], BOOK_DMG[i]) for v in news):
                badf.append((p, olds, news))
    K.check(len(_BOOKDIFF) == 42 and not badf, "B: the %d changed book chain / orb files differ only in the Mana cost / damage, old -> new: %s" % (len(_BOOKDIFF), badf[:3]))
    K.check(all(n[f] is not None for f in ("W_C", "S_C", "B_COST", "B_DMG")), "B: those tables exist")
    with zipfile.ZipFile(jar) as z:
        wl = dict((i, jload(z, p)["ItemLevel"]) for i, p in items_of(z).items() if i.startswith("Weapon_Fist_Wraps_"))
    col = {"Linen": "Copper", "Cotton": "Iron", "Silk": "Thorium", "Cindercloth": "Cobalt", "Shadoweave": "Adamantite"}
    K.eq(dict((k, v) for k, v in wl.items() if k.split("_")[-1] in col), dict(("Weapon_Fist_Wraps_" + c, TT.band(m)[0]) for c, m in col.items()),
         "B: the wraps' ItemLevel = their metal column's new band start")
    K.notes.append("B: wraps %s; fixed rows checked %d" % (wl, len(rows)))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- T + K + M (no JVM needed beyond B's dumps)
def run_tags(out, jar, scratch, _home):
    K = HK.Child(out)
    with zipfile.ZipFile(jar) as zn, zipfile.ZipFile(OLD_JAR) as zo:
        ids = items_of(zn)
        dn, do = descs(zn), descs(zo)
        ln, lo = lang_lines(zn), lang_lines(zo)
    fam, bad, untag = {}, [], []
    for iid in sorted(ids):
        d = dn.get(iid)
        if d is None:
            continue
        metal = [w for w in iid.split("_")[1:] if TT.metal_tier(w)]
        if metal and "_UT_" not in iid:
            want = TT.combat_tag(iid, 0)
            ok = d.startswith(want + TT.SEP) and (TT.tag_for(iid) in (None, want))
            f = iid.split("_")[1] if not iid.startswith("Weapon_Fist_") else "Fist_" + iid.split("_")[2]
            r = fam.setdefault(f, [0, 0])
            r[0] += 1
            r[1] += 1 if ok else 0
            if not ok:
                bad.append((iid, d[:30], want))
        elif not _TAGRX.match(d):
            untag.append(iid)
    K.eq(bad, [], "T: every metal-word item's description starts with TT.combat_tag (= TT.tag_for where listed)")
    K.notes.append("T: per family (items, tagged right): %s" % ", ".join("%s %d/%d" % (f, v[1], v[0]) for f, v in sorted(fam.items())))
    K.check(len(fam) >= 18 and sum(v[0] for v in fam.values()) >= 200, "T: %d families, %d items checked" % (len(fam), sum(v[0] for v in fam.values())))
    K.eq(sorted(untag), sorted(["Weapon_Fist_Wraps_Linen", "Weapon_Fist_Wraps_Cotton", "Weapon_Fist_Wraps_Silk", "Weapon_Fist_Wraps_Cindercloth",
                                "Weapon_Fist_Wraps_Shadoweave", "SkyyArmory_Essence_Earth", "SkyyArmory_Essence_Light", "Weapon_Wand_SoulOrb",
                                "Weapon_Staff_UT_Loophole", "Weapon_Wand_UT_SecondOpinion", "Weapon_Bo_UT_Turnstile"]), "T: the untagged rest = no metal in the id / Untiered / the Soul Orb")
    def expect(i):
        t = do[i] if _TAGRX.match(do[i]) else TT.combat_tag(i, 0) + TT.SEP + do[i]
        if i.startswith("Weapon_Spellbook_"):
            k = BOOK_METALS.index(i[len("Weapon_Spellbook_"):])
            t = t.replace("Page Burst, %d Mana" % BOOK_COST38[k], "Page Burst, %d Mana" % BOOK_COST[k], 1)
        return t
    pref = [i for i in TAGGED if not _TAGRX.match(do[i])]
    K.check(len(pref) == 51 and all(dn[i] == expect(i) for i in TAGGED) and len(ln) == len(lo)
            and sorted(set(ln) - set(lo)) == sorted("items.%s.description = %s" % (i, dn[i]) for i in TAGGED)
            and sorted(TAGGED) == sorted(set(pref) | set(i for i in dn if i.startswith("Weapon_Spellbook_") and i != "Weapon_Spellbook_Thorium" and i in do)),
            "T: server.lang vs 0.1.38 = the 51 tag prefixes + the 14 book Mana numbers (%d lines)" % len(TAGGED))
    # every tag number = the ladder (unchanged by the re-band) and the tag's word = the id's metal
    K.check(all(TT.tier_for_level(TT.band(w)[0]) == TT.metal_tier(w) for w in TT.LADDER[1:15]), "T: each metal's new band start lands in its own ladder T (tags and bands agree)")
    K.save()


def run_know(out, jar, scratch, _home):
    K = HK.Child(out)
    with zipfile.ZipFile(jar) as zn, zipfile.ZipFile(OLD_JAR) as zo, zipfile.ZipFile(ASSETS) as az:
        ids = items_of(zn)
        kr, other, olds = [], [], []
        for iid, p in sorted(ids.items()):
            r = jload(zn, p).get("Recipe")
            if not r:
                continue
            if r.get("KnowledgeRequired") is True:
                kr.append(iid)
            elif r.get("KnowledgeRequired") not in (False, None):
                other.append(iid)
            ro = jload(zo, p).get("Recipe")
            if ro.get("KnowledgeRequired") not in (False, None):
                olds.append(iid)
        twins = [n for n in zn.namelist() if n.startswith("Server/Item/Recipes/")]
        tw_ok = all(jload(zn, n).get("KnowledgeRequired") is True for n in twins)
        bronze = [i for i in ids if "Bronze" in i.split("_")]
        vb = [n for n in az.namelist() if n.startswith("Server/Item/Items/") and "Weapon_" in n and "Bronze" in os.path.basename(n)[:-5].split("_")]
        vb_rec = [n for n in vb if jload(az, n).get("Recipe")]
        grants = []
        from_bars = {}
        for iid in kr:
            a = alloy_of(iid)
            p_, q_ = __import__("skyyench").ALLOY_PARENTS[a]
            bars = [x.get("ItemId") or x.get("ResourceTypeId") for x in jload(zn, ids[iid])["Recipe"]["Input"]]
            from_bars[iid] = bars
            grants.append({"recipe": iid + "_Recipe_Generated_0", "output": iid, "alloy": a, "needs": ["%s V" % p_, "%s V" % q_]})
    K.eq(kr, _GATED, "K: exactly the alloy weapon recipes need knowledge")
    K.check(len(kr) == 72 and sorted(set(alloy_of(i) for i in kr)) == ["Azurvane", "Cinder", "Dusk", "Lumen"] and len(set(i.split("_")[1] for i in kr)) >= 17,
            "K: 72 = 18 families x Dusk / Azurvane / Cinder / Lumen (%d)" % len(kr))
    K.eq(other + olds, [], "K: every other recipe is false / absent, and 0.1.38 had none gated")
    K.check(tw_ok and len(twins) == 15, "K: the 15 hidden Soul ladder twins stay KnowledgeRequired (exempt from grants)")
    K.check(not bronze and len(vb) == 7 and not vb_rec, "K: Armory makes no Bronze weapon; the 7 vanilla Bronze weapons have no recipe (nothing to gate)")
    K.check(all(any(("_%s_" % g["alloy"]) in str(b) for b in from_bars[g["output"]]) or g["output"].startswith("Weapon_Wand_SoulCage_") for g in grants),
            "K: every gated recipe is made from its alloy (bars) or is an alloy Soul Cage")
    json.dump(grants, open(os.path.join(scratch, "grants.json"), "w"), indent=1)
    K.notes.append("K: grant table written (%d rows)" % len(grants))
    K.save()


def run_mig(out, jar, scratch, _home):
    K = HK.Child(out)
    o = json.load(open(os.path.join(scratch, "old_defs.json")))["DEF_CFG"]
    n = json.load(open(os.path.join(scratch, "new_defs.json")))["DEF_CFG"]
    rows = lambda t: [l for l in t.replace("\r\n", "\n").split("\n") if l and not l.startswith("#")]
    com = lambda t: [l for l in t.replace("\r\n", "\n").split("\n") if l.startswith("#")]
    K.eq(rows(n), rows(o), "M: every default row (key = value) of 0.1.39 = 0.1.38 (%d rows) - nothing at an old default to migrate" % len(rows(o)))
    dc = sorted(set(com(n)) ^ set(com(o)))
    K.check(all("Outside zones" in l or "0.1.38" in l or "0.1.39" in l for l in dc) and len(dc) <= 4,
            "M: the comments differ only in the essence.zone help / the version: %s" % dc)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read()
    files0 = sorted(os.path.join(dp, fn) for dp, _d, fns in os.walk(home) for fn in fns)
    snaps, msgs = [], []
    for start in (1, 2):
        msgs.append([str(getattr(Cfg, m)()) for m in MIGS])
        Cfg.load()
        snaps.append(open(f, "rb").read())
    files1 = sorted(os.path.join(dp, fn) for dp, _d, fns in os.walk(home) for fn in fns)
    K.check(snaps[0] == before and snaps[1] == before, "D: Skyy's live config is byte-identical after 2 starts (no row rewritten, no marker added)")
    K.eq(files1, files0, "D: no History copy / change-log file added (nothing migrated)")
    K.check(all(m == "" for ms in msgs for m in ms), "D: every migration answers 'nothing to do': %s" % [m for ms in msgs for m in ms if m][:3])
    K.eq([float(Cfg.HOP_FORCE), float(Cfg.HOP_MAXUP)], [30.0, 20.0], "D: the loader reads Skyy's values (hop.force 30, hop.maxUp 20)")
    K.notes.append("D: live config %d bytes, %d files" % (len(before), len(files0)))
    K.save()


if __name__ == "__main__":
    HK.run_compare = _compare
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("old", run_old), ("bands", run_bands), ("tags", run_tags), ("know", run_know), ("mig", run_mig), ("live", run_live),
                   ("static38", run_static38), ("engine38", run_engine38)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
