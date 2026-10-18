"""Harness for SkyyArmory 0.1.33 (THE NEW-METAL WEAPONS, GROUP A; tools/armory_0_1_33_patch.py). Build first:
    python tools/armory_0_1_33_patch.py && python SkyyArmory/build_skyyarmory_0.1.33.py

    python SkyyArmory/test_skyyarmory_0.1.33.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.32 -> 0.1.33: only the table / text members differ (EXPECT); non-class entries: every 0.1.32 file byte-equal except
               manifest.json + server.lang, whose old lines are all still there in the same order (the new lines are only the 76 new
               items' names + descriptions); every new file belongs to a new item (its id / key in the path)
  J   jar      the 76 new items: ids, prefixes (class locks), Icon / Texture / Model present (jar or Assets.zip), recipes (inputs = vanilla,
               SkyyWorldGen's new bars, our own cages), the new bar in every new-metal recipe, the tier tag first in every description, the
               art = the approved copy (models-local/art/metals) when present, the per-family numbers monotonic on the 15-step ladder
  X   exec     the Java tables on plain values: wand / staff / book / kunai index of the new ids, pidCode of their projectiles, Soul.tierOf +
               ArmoryDefs.soulRank (old tiers = their place, new = the ladder rank), Wings.baseOf through the rank (Lumen = Onyxium), Monk
               boHit / fistHit, Rush.gsH, SoulCageFn (places 8-15, the partner essence), the hooks' table checks, ArmoryCfg defaults on a fresh
               file (every table the full length, the new entries = the build's defaults)
  D   live     START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyArmory: nothing rewritten (no migration in 0.1.33)
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.33", "0.1.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "a1", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
NEW8 = ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")
NK = [w + "_SkyWynn" for w in NEW8]
GAP4 = ("Thorium", "Cobalt", "Adamantite", "Mithril")
DONOR = {"Lead": "Thorium", "Dusk": "Thorium", "Chromium": "Cobalt", "Azurvane": "Cobalt", "Slag": "Adamantite", "Cinder": "Adamantite",
         "Titanium": "Mithril", "Lumen": "Mithril"}
LADDER = ("Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril",
          "Titanium", "Lumen", "Onyxium")
FAMS = [("Weapon_Wand_%s", "Wand"), ("Weapon_Staff_%s", "Staff"), ("Weapon_Spellbook_%s", "Spellbook"), ("Weapon_Kunai_%s", "Kunai"),
        ("Weapon_Bo_%s", "Bo Staff"), ("Weapon_Fist_Gauntlets_%s", "Gauntlets"), ("Weapon_Wand_SoulCage_%s", "Soul Cage"),
        ("Weapon_GreatShield_%s", "Great Shield"), ("Weapon_Crossbow_%s", "Crossbow")]
NEW_IDS = sorted([f % k for f, _n in FAMS for k in NK] + ["Weapon_Crossbow_%s_Wynn" % m for m in GAP4])
# the classes whose members carry the extended tables / texts (the data only - no logic change except Wings + the rank)
# (checked by hand from the compare listing: data arrays / texts / the version text, the Wings rank call, the kit's row holders)
EXPECT = {"ArmoryCfg": ["~<clinit>", "~m load", "~m reloadAll", "~m useDefaults"],          # the table defaults + the version text
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "ArmoryDefs": ["+f SOUL_RANK", "+m soulRank", "~<clinit>"],          # the extended tables + the Wings rank
          "ArmoryHooks": ["~<clinit>", "~m checkBook", "~m checkKunai", "~m checkSoul", "~m checkTune"],          # read-only rows + the words
          "ArmorySpeedFn": ["~<clinit>"],          # the speed-tier table (the new wand / staff roots)
          "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"],          # the default file + the version text
          "CfgRows": ["+m jI", "+m jL", "+m jS", "~<clinit>", "~m header"],          # the kit's row holders (HOLDERS=2) + the version text
          "Monk": ["~<clinit>"], "Stun": ["~<clinit>"],          # the Bo / fist hit tables
          "SkyyArmoryPlugin": ["~m publish", "~m setup", "~m start"],          # the bridge texts + the version
          "SoulCageFn": ["~<clinit>"],          # the 16-place ladder + essences
          "Wings": ["~m arrive"]}          # the heal reads ArmoryDefs.soulRank(tier)


def lang_of(z):
    return z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines()


# ---------------------------------------------------------------------------------------------------------------- J: the jar contents
def run_jar(out, jar, scratch, home):
    K = HK.Child(out)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import tier_tags as TT
    import skyyart as SA
    az = SA.assets()
    azn = set(az.namelist())
    az_items = set(os.path.basename(n)[:-5] for n in azn if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    zb, za = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nb, na = set(zb.namelist()), set(za.namelist())
    items = {}
    for n in nb:
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            items[os.path.basename(n)[:-5]] = json.loads(zb.read(n).decode("utf-8"))
    old_items = set(os.path.basename(n)[:-5] for n in na if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    added = sorted(set(items) - old_items)
    K.eq(added, NEW_IDS, "J: exactly the 76 new items are added (72 new-metal + 4 gap crossbows)")
    K.check(not [i for i in NEW_IDS if i in az_items], "J: no new id is a vanilla id")
    lang = dict(l.split(" = ", 1) for l in lang_of(zb) if " = " in l)
    wg_bars = set("Ingredient_Bar_%s" % k for k in NK)
    K.check(wg_bars <= TT.WG_IDS, "J: the 8 new bars are SkyyWorldGen's ids (tools/tier_tags.py WG_IDS)")
    bad_files, bad_rec, bad_tag, bad_name = [], [], [], []
    for i in NEW_IDS:
        it = items[i]
        word = [w for w in i.split("_") if w in NEW8 or w in GAP4][0]
        for f_ in ("Icon", "Texture", "Model"):
            p_ = it.get(f_)
            if p_ and ("Common/" + p_) not in nb and ("Common/" + p_) not in azn:
                bad_files.append("%s %s %s" % (i, f_, p_))
        r = it.get("Recipe") or {}
        ins = [x.get("ItemId") for x in r.get("Input") or []]
        if not ins or not r.get("BenchRequirement"):
            bad_rec.append("%s: no recipe" % i)
        for x in ins:
            if x and x not in az_items and x not in wg_bars and x not in items:
                bad_rec.append("%s: unknown input %s" % (i, x))
        bar = "Ingredient_Bar_" + (word + "_SkyWynn" if word in NEW8 else word)
        if bar not in ins and not i.startswith("Weapon_Wand_SoulCage_"):
            bad_rec.append("%s: no %s" % (i, bar))
        if i.startswith("Weapon_Wand_SoulCage_") and (bar not in ins or not [x for x in ins if x and x.startswith("Weapon_Wand_SoulCage_")]):
            bad_rec.append("%s: a cage needs the cage before + %s: %s" % (i, bar, ins))
        tag = TT.tag_text(TT.metal_tier(word)) + TT.SEP
        d = lang.get("items.%s.description" % i, "")
        if not d.startswith(tag):
            bad_tag.append("%s: %r" % (i, d[:40]))
        nm = lang.get("items.%s.name" % i, "")
        if not nm.startswith(word + " ") or "_" in nm:
            bad_name.append("%s: %r" % (i, nm))
    K.check(not bad_files, "J: every new item's Icon / Texture / Model exists (jar or Assets.zip): %s" % bad_files[:4])
    K.check(not bad_rec, "J: every new item has a recipe of known inputs with its own bar: %s" % bad_rec[:4])
    K.check(not bad_tag, "J: every new description starts with its tier tag 'T<n> <Metal> - ': %s" % bad_tag[:4])
    K.check(not bad_name, "J: every new name is '<Metal> <family>' (no key underscores): %s" % bad_name[:4])
    # the class locks: the family prefixes of the old items
    for f_, _n in FAMS:
        pre = f_.split("%s")[0]
        K.check(all(i.startswith(pre) for i in [f_ % k for k in NK]), "J: %s* keeps its prefix (class lock)" % pre)
    # the zone partner's recipe with the new bar (wand = partner shortbow; kunai = partner daggers; Bo = partner sword; gauntlets = partner hands)
    def vrec(iid):
        n = [x for x in azn if x.endswith("/" + iid + ".json") and x.startswith("Server/Item/Items/")][0]
        return json.loads(az.read(n).decode("utf-8-sig")).get("Recipe")
    for fam, src in (("Weapon_Wand_%s", "Weapon_Shortbow_%s"), ("Weapon_Kunai_%s", "Weapon_Daggers_%s"), ("Weapon_Bo_%s", "Weapon_Sword_%s"),
                     ("Weapon_Fist_Gauntlets_%s", "Armor_%s_Hands")):
        for w in NEW8:
            mine = [(x.get("ItemId"), x.get("Quantity")) for x in items[fam % (w + "_SkyWynn")]["Recipe"]["Input"]]
            theirs = [(("Ingredient_Bar_%s_SkyWynn" % w) if x.get("ItemId") == "Ingredient_Bar_" + DONOR[w] else x.get("ItemId"), x.get("Quantity"))
                      for x in vrec(src % DONOR[w])["Input"]]
            if mine != theirs:
                K.check(False, "J: %s = %s with the new bar: %s vs %s" % (fam % w, src % DONOR[w], mine, theirs))
    K.check(True, "J: wand / kunai / Bo / gauntlet recipes = the zone partner's with the new bar (checked against Assets.zip)")
    # the great shields: the partner's shield recipe x2 with the new bar
    for w in NEW8:
        mine = [(x.get("ItemId"), x.get("Quantity")) for x in items["Weapon_GreatShield_%s_SkyWynn" % w]["Recipe"]["Input"]]
        theirs = [(("Ingredient_Bar_%s_SkyWynn" % w) if x.get("ItemId") == "Ingredient_Bar_" + DONOR[w] else x.get("ItemId"), int(x.get("Quantity")) * 2)
                  for x in vrec("Weapon_Shield_" + DONOR[w])["Input"]]
        K.eq(mine, theirs, "J: the %s great shield = the %s shield x2 with the new bar" % (w, DONOR[w]))
    # soul cages branch off their partner + the partner tier's essence
    parent = {"Lead": "Thorium", "Dusk": "Lead_SkyWynn", "Chromium": "Cobalt", "Azurvane": "Chromium_SkyWynn", "Slag": "Adamantite",
              "Cinder": "Slag_SkyWynn", "Titanium": "Mithril", "Lumen": "Titanium_SkyWynn"}
    for w in NEW8:
        ins = items["Weapon_Wand_SoulCage_%s_SkyWynn" % w]["Recipe"]["Input"]
        pess = [x["ItemId"] for x in items["Weapon_Wand_SoulCage_" + DONOR[w]]["Recipe"]["Input"] if "Essence" in x["ItemId"]]
        K.eq([ins[0]["ItemId"], ins[2]["ItemId"]], ["Weapon_Wand_SoulCage_" + parent[w], pess[0]], "J: the %s cage <- the %s cage + the %s essence" % (w, parent[w], DONOR[w]))
    # the old cage chain is untouched (old item files byte-equal is checked in C)
    # the art: the approved copy when present
    man_p = os.path.join(ROOT, "models-local", "art", "metals", "manifest.json")
    if os.path.isfile(man_p):
        man = json.load(open(man_p, encoding="utf-8"))
        texs = {}
        for e in man:
            if not str(e.get("texture") or "").startswith("models-local/art/metals/"):
                continue
            fam = e["texture"].split("/")[3]
            if fam in ("wand", "crossbow", "spellbook", "kunai", "bo", "gauntlets", "soulcage", "greatshield", "staff"):
                texs[(fam, e["metal"])] = open(os.path.join(ROOT, *e["texture"].split("/")), "rb").read()
        famkey = {"Weapon_Wand_%s": "wand", "Weapon_Staff_%s": "staff", "Weapon_Spellbook_%s": "spellbook", "Weapon_Kunai_%s": "kunai",
                  "Weapon_Bo_%s": "bo", "Weapon_Fist_Gauntlets_%s": "gauntlets", "Weapon_Wand_SoulCage_%s": "soulcage",
                  "Weapon_GreatShield_%s": "greatshield", "Weapon_Crossbow_%s": "crossbow"}
        bad = []
        for f_, _n in FAMS:
            for w in NEW8:
                t_ = zb.read("Common/" + items[f_ % (w + "_SkyWynn")]["Texture"])
                if t_ != texs.get((famkey[f_], w)):
                    bad.append(f_ % w)
        K.check(not bad, "J: every new texture = the approved copy in models-local/art/metals: %s" % bad[:4])
    else:
        K.notes.append("J: no approved art copy here (models-local/art/metals) - art compared in the build only")
    # numbers monotonic on the ladder (old metals + new, Onyxium aside)
    def order(ids_of):
        seq = [m for m in LADDER if m != "Onyxium" and m != "Bronze"]
        return [(m, ids_of(m)) for m in seq]
    def proj_dmg(name):
        return json.loads(zb.read("Server/Projectiles/Player/SkyyArmory/%s.json" % name))["Damage"]
    for fam, key in (("SkyyArmory_Orb_%s", "wand charged orb"), ("SkyyArmory_StaffOrb_%s", "staff charged orb"),
                     ("SkyyArmory_Spellbook_Burst_%s", "book burst")):
        seq = [(m, proj_dmg(fam % (m + "_SkyWynn" if m in NEW8 else m))) for m in LADDER if m not in ("Onyxium", "Bronze")]
        vals = [v for _m, v in seq]
        K.check(vals == sorted(vals), "J: %s damage climbs the 15-step ladder: %s" % (key, seq))
    def bo_hit(m):
        k = m + "_SkyWynn" if m in NEW8 else m
        iv = items["Weapon_Bo_" + k]["InteractionVars"]["Spear_Swing_Left_Damage"]["Interactions"][0]
        return iv["DamageCalculator"]["BaseDamage"]["Physical"]
    seq = [(m, bo_hit(m)) for m in LADDER if m not in ("Onyxium", "Bronze")]
    K.check([v for _m, v in seq] == sorted(v for _m, v in seq), "J: Bo hit climbs the ladder: %s" % seq)
    def xb(m):
        x = "Weapon_Crossbow_%s" % (m + "_SkyWynn" if m in NEW8 else (m + "_Wynn"))
        if m == "Iron":
            return 10
        return items[x]["InteractionVars"]["Standard_Projectile_Damage"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]
    seq = [(m, xb(m)) for m in LADDER if m not in ("Bronze",)]
    K.check([v for _m, v in seq] == sorted(v for _m, v in seq), "J: crossbow bolt damage climbs the ladder (Iron = vanilla, Onyxium last): %s" % seq)
    def xbk(m, k_):
        x = "Weapon_Crossbow_%s" % (m + "_SkyWynn" if m in NEW8 else (m + "_Wynn"))
        if k_ == "dur":
            return items[x]["MaxDurability"]
        v = {"combo": "Combo_Projectile_Damage", "sig": "Signature_BigArrow_Damage"}[k_]
        return items[x]["InteractionVars"][v]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]
    for k_ in ("combo", "sig", "dur"):          # critic L3: ours never go down along the ladder (Iron = vanilla, left out)
        seq = [(m, xbk(m, k_)) for m in LADDER if m not in ("Bronze", "Iron")]
        K.check([v for _m, v in seq] == sorted(v for _m, v in seq), "J: crossbow %s never goes down along the ladder: %s" % (k_, seq))
    # the gap crossbow recipes: the same-metal vanilla shortbow + 2 leather
    for m in GAP4:
        mine = [(x.get("ItemId"), x.get("Quantity")) for x in items["Weapon_Crossbow_%s_Wynn" % m]["Recipe"]["Input"]]
        sb = vrec("Weapon_Shortbow_" + m)["Input"]
        theirs = [(x.get("ItemId"), int(x.get("Quantity")) + (2 if str(x.get("ItemId")).startswith("Ingredient_Leather_") else 0)) for x in sb]
        K.eq(mine, theirs, "J: the %s crossbow = the %s shortbow + 2 leather (the vanilla Iron crossbow's step)" % (m, m))
    # More Crossbow Tiers' numbers are not ours (ARR): our gap crossbows' damage differs from theirs where their mod is installed
    mct = [f for f in (os.listdir(B.MODS_DIR) if os.path.isdir(B.MODS_DIR) else []) if f.startswith("More_Crossbow_Tiers") and f.endswith(".zip")]
    for f in mct:
        with zipfile.ZipFile(os.path.join(B.MODS_DIR, f)) as mz:
            same = []
            for m in GAP4:
                n = "Server/Item/Items/Weapon_Crossbow_%s.json" % m
                if n in mz.namelist():
                    t = json.loads(mz.read(n).decode("utf-8-sig"))
                    a = t["InteractionVars"]["Standard_Projectile_Damage"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]
                    b = items["Weapon_Crossbow_%s_Wynn" % m]["InteractionVars"]["Standard_Projectile_Damage"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]
                    c = t["InteractionVars"]["Signature_BigArrow_Damage"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]
                    d = items["Weapon_Crossbow_%s_Wynn" % m]["InteractionVars"]["Signature_BigArrow_Damage"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Projectile"]
                    if (a, c) == (b, d):
                        same.append(m)
            K.check(not same, "J: no gap crossbow copies More Crossbow Tiers' numbers (%s): %s" % (f, same))
    # no new file overrides a vanilla path or another family's file
    new_files = sorted(nb - na)
    K.check(not [n for n in new_files if n in azn], "J: no new file sits on a vanilla path")
    K.check(not [n for n in new_files if n.startswith("Common/Items/Weapons/Shield/")], "J: the great shield art is in our own folder (vanilla shields by path)")
    keys = NK + ["%s_Wynn" % m for m in GAP4] + ["SkyyArmory_Crossbow_%s.png" % m for m in GAP4] + ["Crossbow/SkyyArmory_%s_Texture.png" % m for m in GAP4]
    stray = [n for n in new_files if not n.endswith(".class") and not [k for k in keys if k in n]]
    K.check(not stray, "J: every new file belongs to a new item (its key in the path): %s" % stray[:5])
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: the Java tables
def run_exec(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    D = JClass(PKG + "ArmoryDefs")
    K.eq(len(D.METALS), 16, "X: ArmoryDefs.METALS = Wood + 7 + 8")
    K.eq([str(x) for x in D.METALS][8:], NK, "X: ... the new keys at the end (old places kept)")
    for n, k in enumerate(NK):
        K.eq(int(D.wandIndex("Weapon_Wand_" + k)), 8 + n, "X: wandIndex %s" % k)
        K.eq(int(D.staffIndex("Weapon_Staff_" + k)), 8 + n, "X: staffIndex %s" % k)
        K.eq(int(D.bookIndex("Weapon_Spellbook_" + k)), 7 + n, "X: bookIndex %s" % k)
        K.eq(int(D.kunaiIndex("Weapon_Kunai_" + k)), 8 + n, "X: kunaiIndex %s" % k)
        K.eq(int(D.pidCode("SkyyArmory_Orb_" + k)), 2008 + n, "X: pidCode wand orb %s" % k)
        K.eq(int(D.pidCode("SkyyArmory_StaffOrb_" + k)), 4008 + n, "X: pidCode staff orb %s" % k)
        K.eq(int(D.pidCode("SkyyArmory_Spellbook_Burst_" + k)), 7007 + n, "X: pidCode book burst %s" % k)
    K.eq([int(D.wandIndex("Weapon_Wand_" + m)) for m in ("Copper", "Onyxium")], [1, 7], "X: the old wands keep their places")
    K.eq(int(D.wandIndex("Weapon_Wand_Lead")), -1, "X: a bare Weapon_Wand_Lead is not ours")
    # soul tiers + the Wings rank
    S = JClass(PKG + "Soul")
    W = JClass(PKG + "Wings")
    K.eq(int(S.tierOf("Weapon_Wand_SoulCage_Onyxium")), 7, "X: Soul.tierOf Onyxium = 7 (old place)")
    K.eq([int(S.tierOf("Weapon_Wand_SoulCage_" + k)) for k in NK], list(range(8, 16)), "X: Soul.tierOf the new cages = 8 .. 15")
    ranks = [int(D.soulRank(t)) for t in range(16)]
    K.eq(ranks[:8], list(range(8)), "X: soulRank of the old tiers = their place (Wings heal unchanged)")
    K.eq(ranks[8:], [3, 4, 4, 5, 5, 6, 6, 7], "X: soulRank of the new cages = their ladder rank (Lead 3 .. Lumen 7)")
    K.eq(int(D.soulRank(-1)), 0, "X: soulRank(-1) = 0")
    K.eq(float(W.baseOf(100.0, int(D.soulRank(15)), 10.0, 1.0)), float(W.baseOf(100.0, 7, 10.0, 1.0)), "X: the Lumen cage's Wings base = Onyxium's (rank 7)")
    K.check(abs(float(W.baseOf(100.0, int(D.soulRank(8)), 10.0, 1.0)) - 13.0) < 1e-9, "X: the Lead cage's Wings base = 10 + 3 x 1 = 13 %% of 100")
    # Monk + great shield lookups
    M = JClass(PKG + "Monk")
    R = JClass(PKG + "Rush")
    for k in NK:
        K.check(float(M.boHit("Weapon_Bo_" + k)) > 0.0, "X: Monk.boHit %s" % k)
        K.check(float(M.fistHit("Weapon_Fist_Gauntlets_" + k)) > 0.0, "X: Monk.fistHit %s" % k)
        K.check(float(R.gsH("Weapon_GreatShield_" + k)) > 0.0, "X: Rush.gsH %s" % k)
    K.eq(float(M.boHit("Weapon_Bo_Copper")), 9.7, "X: the Copper Bo keeps 9.7")
    K.eq(float(R.gsH("Weapon_GreatShield_Copper")), 11.0, "X: the Copper great shield keeps H 11")
    # armory:fn:soulcage
    F = JClass(PKG + "SoulCageFn")()
    K.eq(int(F.apply(JString("Weapon_Wand_SoulCage_Lead_SkyWynn"))), 8, "X: soulcage fn: Lead cage = place 8")
    K.eq(int(F.apply(JString("Weapon_Wand_SoulCage_Onyxium"))), 7, "X: soulcage fn: Onyxium stays 7")
    arr = JArray(JObject)([JString("essence"), JClass("java.lang.Integer").valueOf(8)])
    K.eq(str(F.apply(arr)), "Ingredient_Ice_Essence", "X: soulcage fn: tier 8 (Lead) essence = Ice (Thorium's)")
    arr = JArray(JObject)([JString("essence"), JClass("java.lang.Integer").valueOf(15)])
    K.eq(str(F.apply(arr)), "Ingredient_Void_Essence", "X: soulcage fn: tier 15 (Lumen) essence = Void (Mithril's)")
    # the hooks: the new entries pass, junk still refused
    H = JClass(PKG + "ArmoryHooks")
    K.check(H.checkBook("book.radius[Lead_SkyWynn]", "3") is None, "X: checkBook accepts Lead_SkyWynn")
    K.check(H.checkKunai("kunai.cooldown[Lumen_SkyWynn]", "3") is None, "X: checkKunai accepts Lumen_SkyWynn")
    K.check(H.checkSoul("soul.bindings[Cinder_SkyWynn]", "3") is None, "X: checkSoul accepts Cinder_SkyWynn")
    K.check(H.checkBook("book.radius[Lead]", "3") is not None, "X: checkBook refuses a bare Lead")
    K.check(H.checkTune("tune.wand[Azurvane_SkyWynn]", "120") is None and H.checkTune("tune.wand[Foo]", "120") is not None, "X: checkTune")
    # ArmoryCfg on a FRESH folder: the default file + every table the full length
    C = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    fresh = os.path.join(scratch, "fresh")
    os.makedirs(fresh, exist_ok=True)
    C.DIR = Paths.get(fresh)
    C.FILE = Paths.get(fresh).resolve("config.properties")
    C.load()
    txt = open(os.path.join(fresh, "config.properties"), "rb").read().decode("latin-1")
    for k in NK:
        for key in ("tune.wand." + k, "tune.staff." + k, "book.radius." + k, "lev.height." + k, "kunai.cooldown." + k, "soul.bindings." + k):
            if ("\n" + key + "=") not in txt:
                K.check(False, "X: the fresh file carries %s" % key)
    K.check(True, "X: the fresh default file carries every new table line")
    K.eq([len(C.BOOK_R), len(C.LEV_H), len(C.K_CD), len(C.SOUL_NT), len(C.TUNE_W), len(C.TUNE_S)], [15, 15, 16, 16, 16, 16], "X: the table lengths")
    K.eq(int(C.SOUL_NT[8]), 7, "X: soul.bindings Lead = 7 (the build default)")
    K.eq(float(C.SOUL_NT[3]), 6.0, "X: soul.bindings Thorium keeps 6")
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
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.33")
    # the live file has no new-metal lines: the tables read their defaults
    K.eq(len(Cfg.BOOK_R), 15, "D: book table = 15 entries on the live file")
    K.check(float(Cfg.K_CD[8]) > 0.0 and float(Cfg.SOUL_DPS[15]) > 0.0, "D: the new entries read their defaults on the live file")
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
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["CfgRows1", "CfgRows2"],
           phases=[("jar", run_jar), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
