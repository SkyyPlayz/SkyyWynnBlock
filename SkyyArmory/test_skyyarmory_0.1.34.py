"""Harness for SkyyArmory 0.1.34 (THE VANILLA METAL FAMILIES IN THE 8 NEW METALS, round A2; tools/armory_0_1_34_patch.py). Build first:
    python tools/armory_0_1_34_patch.py && python SkyyArmory/build_skyyarmory_0.1.34.py

    python SkyyArmory/test_skyyarmory_0.1.34.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.33 -> 0.1.34: only the version texts + the pack-check id tables differ (EXPECT); non-class entries: every 0.1.33 file
               byte-equal except manifest.json + server.lang (old lines kept in order; the new lines = the 80 items' names + descriptions)
  J   jar      the 80 new items: ids + prefixes (class locks), the partner's vanilla item (model / Parent / interactions), Icon / Texture /
               Model / bow draw textures present, numbers = an INDEPENDENT recomputation (geometric on the 15-step ladder from Assets.zip,
               floored at every lower step = never down), recipes = the partner's (or the nearest lower vanilla recipe) with the new bar, spears
               drop-only with their own thrown projectile, tier tag + name, the art = the approved copy (models-local/art/metals) when present,
               every new file belongs to a new item, no vanilla path
  X   exec     ArmoryDefs.ITEM_CHECK / PRJ_CHECK carry the new ids; the old tables unchanged (wand / kunai index, soul ranks)
  D   live     START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyArmory: nothing rewritten (no config change in 0.1.34)
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.34", "0.1.33"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "a2", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
NEW8 = ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")
NK = [w + "_SkyWynn" for w in NEW8]
DONOR = {"Lead": "Thorium", "Dusk": "Thorium", "Chromium": "Cobalt", "Azurvane": "Cobalt", "Slag": "Adamantite", "Cinder": "Adamantite",
         "Titanium": "Mithril", "Lumen": "Mithril"}
LADDER = ("Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril",
          "Titanium", "Lumen", "Onyxium")
FAMS = ("Sword", "Longsword", "Axe", "Battleaxe", "Mace", "Club", "Daggers", "Spear", "Shortbow", "Shield")
CLASS_OF = {"Sword": "Warrior", "Spear": "Warrior", "Shield": "Warrior", "Axe": "Berserker", "Battleaxe": "Berserker", "Mace": "Berserker",
            "Club": "Berserker", "Longsword": "Spellblade", "Daggers": "Assassin", "Shortbow": "Archer"}
NEW_IDS = sorted("Weapon_%s_%s" % (f, k) for f in FAMS for k in NK)
EXPECT = {"ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"],          # the version text
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "ArmoryDefs": ["~<clinit>"],          # ITEM_CHECK / PRJ_CHECK: + the 80 items and the 8 spear projectiles
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"],          # the version text (the default file header)
          "SkyyArmoryPlugin": ["~m setup", "~m start"]}          # the version text


def lang_of(z):
    return z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines()


# ---------------------------------------------------------------------------------------------------------------- J: the jar contents
def run_jar(out, jar, scratch, home):
    K = HK.Child(out)
    import tier_tags as TT
    import skyyart as SA
    az = SA.assets()
    azn = set(az.namelist())
    aidx = dict((os.path.basename(n)[:-5], n) for n in azn if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    pidx = dict((os.path.basename(n)[:-5], n) for n in azn if n.startswith("Server/Projectiles/") and n.endswith(".json"))

    def araw(i):
        return json.loads(az.read(aidx[i]).decode("utf-8-sig"))

    def ares(i):
        d = araw(i)
        if not d.get("Parent"):
            return d
        b = ares(d["Parent"])
        for k, v in d.items():
            if k == "Parent":
                continue
            if k == "InteractionVars" and isinstance(b.get(k), dict):
                b[k] = dict(b[k])
                b[k].update(v)
            else:
                b[k] = v
        return b

    zb, za = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nb, na = set(zb.namelist()), set(za.namelist())
    items = {}
    for n in nb:
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            items[os.path.basename(n)[:-5]] = json.loads(zb.read(n).decode("utf-8"))
    old_items = set(os.path.basename(n)[:-5] for n in na if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    K.eq(sorted(set(items) - old_items), NEW_IDS, "J: exactly the 80 new items are added (10 vanilla families x 8 new metals)")
    K.check(not [i for i in NEW_IDS if i in aidx], "J: no new id is a vanilla id")
    K.check(all(i.split("_")[2] in NEW8 and i.endswith("_SkyWynn") for i in NEW_IDS), "J: word 3 = the metal, ids end _SkyWynn")
    lang = dict(l.split(" = ", 1) for l in lang_of(zb) if " = " in l)
    bad_files, bad_shape, bad_tag, bad_name = [], [], [], []
    for i in NEW_IDS:
        it, f, w = items[i], i.split("_")[1], i.split("_")[2]
        pid = "Weapon_%s_%s" % (f, DONOR[w])
        pr, pres = araw(pid), ares(pid)

        def exists(p_):
            return ("Common/" + p_) in nb or ("Common/" + p_) in azn
        for p_ in [it.get("Icon"), it.get("Texture"), it.get("Model")] + [c.get("Texture") for v in (it.get("ItemAppearanceConditions") or {}).values()
                                                                         for c in v if c.get("Texture")]:
            if not p_ or not exists(p_):
                bad_files.append("%s %s" % (i, p_))
        if it.get("Model") != pres.get("Model") or it.get("Parent") != pr.get("Parent") or it.get("Interactions") != pr.get("Interactions") \
                or it.get("Quality", pres.get("Quality")) != pres.get("Quality") or it.get("ItemLevel", pres.get("ItemLevel")) != pres.get("ItemLevel") \
                or not it["Texture"].startswith(os.path.dirname(pres["Texture"]) + "/SkyyArmory_") or it["Icon"] == pres.get("Icon"):
            bad_shape.append(i)
        tag = TT.tag_text(TT.metal_tier(w)) + TT.SEP
        d = lang.get("items.%s.description" % i, "")
        if not d.startswith(tag + CLASS_OF[f] + " ") or TT.combat_tag(i, 0) + TT.SEP != tag:
            bad_tag.append("%s: %r" % (i, d[:50]))
        if lang.get("items.%s.name" % i) != "%s %s" % (w, f):
            bad_name.append(i)
    K.check(not bad_files, "J: every Icon / Texture / Model / bow draw texture exists (jar or Assets.zip): %s" % bad_files[:4])
    K.check(not bad_shape, "J: each item = its zone partner's vanilla item (model, Parent, interactions, quality, level) + our texture / icon: %s" % bad_shape[:4])
    K.check(not bad_tag, "J: every description starts 'T<n> <Metal> - <class> ' (= tier_tags.combat_tag of the id): %s" % bad_tag[:4])
    K.check(not bad_name, "J: every name is '<Metal> <Family>': %s" % bad_name[:4])
    for f in FAMS:          # the class lock prefixes SkyyClasses reads
        K.check(all(i.startswith("Weapon_%s_" % f) for i in NEW_IDS if i.split("_")[1] == f), "J: Weapon_%s_* keeps its prefix (class lock %s)" % (f, CLASS_OF[f]))

    # ---- numbers: an independent recomputation from Assets.zip (geometric on the ladder, floored at every lower step)
    pos = dict((m, n) for n, m in enumerate(LADDER))
    van = [m for m in LADDER if m not in NEW8 and m != "Onyxium"]

    def interp(vals, w):
        pts = sorted((pos[m], float(v)) for m, v in vals.items())
        p = pos[w]
        lo, hi = [q for q in pts if q[0] < p], [q for q in pts if q[0] > p]
        (p0, v0), (p1, v1) = (lo[-1], hi[0]) if (lo and hi) else (pts[-2], pts[-1])
        t = (p - p0) / float(p1 - p0)
        return v0 * (v1 / v0) ** t if (v0 > 0 and v1 > 0) else v0 + (v1 - v0) * t

    def expect(vals, integer):
        out, run = {}, None
        for m in LADDER[:-1]:
            if m in NEW8:
                v = interp(vals, m)
                v = int(v + 0.5 + 1e-9) if integer else round(v, 2)
                v = max(v, run) if run is not None else v
                out[m] = v
            elif m in vals:
                v = vals[m]
            else:
                continue
            run = v if run is None else max(run, v)
        return out

    def leaves(x, p=()):
        if isinstance(x, dict):
            for k, v in x.items():
                for r in leaves(v, p + (k,)):
                    yield r
        elif isinstance(x, list):
            for n, v in enumerate(x):
                for r in leaves(v, p + (n,)):
                    yield r
        elif isinstance(x, (int, float)) and not isinstance(x, bool) and ("BaseDamage" in p or p[-2:] == ("StaminaCost", "Value")):
            yield p, x

    def at(x, p):
        for k in p:
            try:
                x = x[k]
            except (KeyError, IndexError, TypeError):
                return None
        return x

    bad_num, n_num, never_down = [], 0, []
    for f in FAMS:
        res = dict((m, ares("Weapon_%s_%s" % (f, m))) for m in van if ("Weapon_%s_%s" % (f, m)) in aidx)
        for w in NEW8:
            i = "Weapon_%s_%s_SkyWynn" % (f, w)
            for p, v in leaves(res[DONOR[w]].get("InteractionVars") or {}):
                vals = dict((m, at(r.get("InteractionVars"), p)) for m, r in res.items())
                vals = dict((m, x) for m, x in vals.items() if isinstance(x, (int, float)))
                want = expect(vals, False)[w]
                got = at(items[i]["InteractionVars"], p)
                n_num += 1
                if got is None or abs(float(got) - float(want)) > 1e-9:
                    bad_num.append("%s %s: %s want %s" % (i, "/".join(str(x) for x in p), got, want))
                lower = [x for m, x in vals.items() if pos[m] < pos[w]] + [at(items["Weapon_%s_%s_SkyWynn" % (f, m)]["InteractionVars"], p)
                                                                           for m in NEW8 if pos[m] < pos[w] and DONOR[m] in res]
                lower = [x for x in lower if isinstance(x, (int, float))]
                if lower and got is not None and got < max(lower):
                    never_down.append("%s %s" % (i, p[0]))
            if isinstance(res[DONOR[w]].get("MaxDurability"), (int, float)) or f == "Spear":          # critic M: every spear wears out
                vals = dict((m, r["MaxDurability"]) for m, r in res.items() if isinstance(r.get("MaxDurability"), (int, float)))
                n_num += 1
                if items[i].get("MaxDurability") != expect(vals, True)[w]:
                    bad_num.append("%s MaxDurability %s want %s" % (i, items[i].get("MaxDurability"), expect(vals, True)[w]))
    sp = [(w, items["Weapon_Spear_%s_SkyWynn" % w].get("MaxDurability"), items["Weapon_Spear_%s_SkyWynn" % w].get("DurabilityLossOnHit")) for w in NEW8]
    K.check(all(isinstance(d, int) and l == 0.56 for _w, d, l in sp) and [d for _w, d, _l in sp] == sorted(d for _w, d, _l in sp),
            "J: all 8 spears wear out (durability on the ladder, 0.56 a hit, never down): %s" % sp)
    K.check(not bad_num, "J: all %d numbers = the independent ladder recomputation from Assets.zip: %s" % (n_num, bad_num[:3]))
    K.check(not never_down, "J: no new number is below any lower ladder step's (vanilla or new): %s" % never_down[:3])
    sw = [(w, items["Weapon_Sword_%s_SkyWynn" % w]["InteractionVars"]["Swing_Left_Damage"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Physical"])
          for w in NEW8]
    K.notes.append("J: sword left swing on the ladder (Thorium 12, Cobalt 12, Adamantite 14, Mithril 18): %s" % sw)

    # ---- recipes: the partner's (or the nearest lower vanilla recipe) with the new bar; spears drop-only
    bad_rec = []
    for i in NEW_IDS:
        f, w = i.split("_")[1], i.split("_")[2]
        rm = DONOR[w]
        while rm and not araw("Weapon_%s_%s" % (f, rm)).get("Recipe"):
            lo = [m for m in ("Thorium", "Cobalt", "Adamantite", "Mithril") if pos[m] < pos[rm]]
            rm = lo[-1] if lo else None
        if f == "Spear":
            if items[i].get("Recipe") is not None or rm is not None:
                bad_rec.append("%s: a spear recipe" % i)
            continue
        vr = araw("Weapon_%s_%s" % (f, rm))["Recipe"]
        theirs = [(("Ingredient_Bar_%s_SkyWynn" % w) if x.get("ItemId") == "Ingredient_Bar_" + rm else x.get("ItemId"), x.get("Quantity")) for x in vr["Input"]]
        mine = [(x.get("ItemId"), x.get("Quantity")) for x in items[i]["Recipe"]["Input"]]
        benches = [b for b in vr["BenchRequirement"] if b.get("Id") != "Armory"]
        if mine != theirs or items[i]["Recipe"]["BenchRequirement"] != benches:
            bad_rec.append("%s: %s vs %s" % (i, mine, theirs))
        if ("Ingredient_Bar_%s_SkyWynn" % w) not in TT.WG_IDS:
            bad_rec.append("%s: the bar is not SkyyWorldGen's" % i)
    K.check(not bad_rec, "J: recipes = the zone partner's vanilla recipe with the new bar (Mithril gaps -> Adamantite's; no Armory diagram bench; "
                         "spears none): %s" % bad_rec[:3])
    fb = sorted(i for i in NEW_IDS if i.split("_")[1] in ("Longsword", "Axe", "Club") and i.split("_")[2] in ("Titanium", "Lumen"))
    K.check(all(items[i]["Recipe"]["Input"][0]["Quantity"] == araw("Weapon_%s_Adamantite" % i.split("_")[1])["Recipe"]["Input"][0]["Quantity"] for i in fb),
            "J: the 6 Titanium / Lumen longsword / axe / club recipes = the Adamantite recipe (vanilla Mithril has none)")

    # ---- the thrown spears: our projectile + appearance, damage on the ladder, the partner's model
    bad_sp = []
    pvals = dict((m, json.loads(az.read(pidx["Spear_" + m]).decode("utf-8-sig")).get("Damage")) for m in van if ("Spear_" + m) in pidx)
    pvals = dict((m, v) for m, v in pvals.items() if isinstance(v, (int, float)))
    pexp = expect(pvals, False)
    for w in NEW8:
        sid = "SkyyArmory_Spear_%s_SkyWynn" % w
        pj = json.loads(zb.read("Server/Projectiles/Player/SkyyArmory/%s.json" % sid))
        mj = json.loads(zb.read("Server/Models/Projectiles/SkyyArmory/%s.json" % sid))
        it = items["Weapon_Spear_%s_SkyWynn" % w]
        if pj != {"Parent": "Spear_Iron", "Appearance": sid, "Damage": pexp[w]} or mj["DefaultAttachments"] != [{"Model": it["Model"], "Texture": it["Texture"]}] \
                or it["InteractionVars"]["Spear_Throw_Charged_Projectile"]["Interactions"][0]["ProjectileId"] != sid or "Recipe" in it:
            bad_sp.append(w)
    K.check(not bad_sp, "J: each new spear throws its own projectile (Parent Spear_Iron, our appearance, damage on the ladder %s): %s" % (pexp, bad_sp))

    # ---- the art: the approved copy (models-local/art/metals) when present
    man_p = os.path.join(ROOT, "models-local", "art", "metals", "manifest.json")
    if os.path.isfile(man_p):
        man = json.load(open(man_p, encoding="utf-8"))
        src = dict(((e["texture"].split("/")[3], e["metal"]), e) for e in man if str(e.get("texture") or "").startswith("models-local/art/metals/"))
        bad = []
        for i in NEW_IDS:
            f, w = i.split("_")[1], i.split("_")[2]
            e = src.get((f.lower(), w))
            if e is None or zb.read("Common/" + items[i]["Texture"]) != open(os.path.join(ROOT, *e["texture"].split("/")), "rb").read() \
                    or zb.read("Common/" + items[i]["Icon"]) != open(os.path.join(ROOT, *e["icon"].split("/")), "rb").read():
                bad.append(i)
        K.check(not bad, "J: every new texture + icon = the approved copy in models-local/art/metals: %s" % bad[:4])
        K.check(os.path.isfile(os.path.join(ROOT, "models-local", "art", "metals", "_sheets", "weapons-c.png")), "J: the contact sheet _sheets/weapons-c.png exists")
    else:
        K.notes.append("J: no approved art copy here (models-local/art/metals) - art compared in the build only")
    icons = [zb.read("Common/" + items[i]["Icon"]) for i in NEW_IDS]
    K.check(len(set(icons)) == len(icons) and all(SA.png_size(b) == (64, 64) for b in icons), "J: 80 distinct 64x64 icons")
    K.check(all(SA.png_size(zb.read("Common/" + items[i]["Texture"])) == SA.png_size(az.read("Common/" + ares("Weapon_%s_%s" % (i.split("_")[1], DONOR[i.split("_")[2]]))["Texture"]))
                for i in NEW_IDS), "J: every texture keeps its partner's UV size")

    # ---- files: every new file belongs to a new item; nothing on a vanilla path; no vanilla family item overridden
    new_files = sorted(nb - na)
    K.check(not [n for n in new_files if n in azn], "J: no new file sits on a vanilla path")
    stray = [n for n in new_files if not n.endswith(".class") and not [k for k in NK if k in n]]
    K.check(not stray, "J: every new file belongs to a new item (its key in the path): %s" % stray[:5])
    K.eq(len([n for n in new_files if not n.endswith(".class")]), 80 * 3 + 2 * 8, "J: 256 new files (80 x item + texture + icon, 8 x spear projectile + model)")
    K.check(not [n for n in nb if n.startswith("Server/Item/Items/") and os.path.basename(n)[:-5] in aidx and os.path.basename(n).startswith(
        tuple("Weapon_%s_" % f for f in FAMS))], "J: no vanilla family item file is overridden")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: the Java tables
def run_exec(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    D = JClass(PKG + "ArmoryDefs")
    ic, pc = set(str(x) for x in D.ITEM_CHECK), set(str(x) for x in D.PRJ_CHECK)
    K.check(set(NEW_IDS) <= ic, "X: ArmoryDefs.ITEM_CHECK (the pack check) carries the 80 new items")
    K.check(set("SkyyArmory_Spear_%s" % k for k in NK) <= pc, "X: ArmoryDefs.PRJ_CHECK carries the 8 spear projectiles")
    K.eq(len(D.METALS), 16, "X: ArmoryDefs.METALS unchanged (Wood + 7 + 8)")
    K.eq([int(D.wandIndex("Weapon_Wand_Lead_SkyWynn")), int(D.kunaiIndex("Weapon_Kunai_Lumen_SkyWynn"))], [8, 15], "X: A1's indexes unchanged")
    K.eq([int(D.soulRank(t)) for t in range(16)], [0, 1, 2, 3, 4, 5, 6, 7, 3, 4, 4, 5, 5, 6, 6, 7], "X: soul ranks unchanged")
    K.eq(int(D.wandIndex("Weapon_Sword_Lead_SkyWynn")), -1, "X: a new sword is no wand")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.34")
    K.save()


# C: the non-class entries - every old file byte-equal; manifest.json + server.lang (old lines kept in order, only new-item lines added)
_eq0 = HK.Child.eq


def _lang_ok():
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    a, b = lang_of(za), lang_of(zb)
    sa = set(a)
    if [l for l in b if l in sa] != a:
        return False, "an old lang line moved or changed"
    extra = [l for l in b if l not in sa]
    bad = [l for l in extra if not [i for i in NEW_IDS if l.startswith("items.%s." % i)]]
    return (not bad and len(extra) == 2 * len(NEW_IDS)), "%d new lines (want %d), %d not of a new item%s" % (
        len(extra), 2 * len(NEW_IDS), len(bad), (": " + bad[0][:100]) if bad else "")


def _eq(self, got, want, what):
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
        na = set(n for n in za.namelist() if not n.endswith(".class"))
        changed = sorted(n for n in got if n in na)
        removed = sorted(n for n in na if n not in set(zb.namelist()))
        ok, why = _lang_ok()
        self.notes.append("C: %d new files, changed %s; lang: %s" % (len([n for n in got if n not in na]), changed, why))
        return self.check(changed == ["Server/Languages/en-US/server.lang", "manifest.json"] and not removed and ok,
                          "C: old files byte-equal except manifest.json + server.lang (lang: old lines kept, %s)" % why)
    return _eq0(self, got, want, what)


HK.Child.eq = _eq


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("jar", run_jar), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
