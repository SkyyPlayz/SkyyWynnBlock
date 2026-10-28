"""Harness for SkyyArmory 0.1.48 (round ut9: the 9 SkyyArmory-family Untiered items of tools/ut28.py; tools/armory_0_1_48_patch.py). Build first:
    python tools/armory_0_1_48_patch.py && python SkyyArmory/build_skyyarmory_0.1.48.py
    python SkyyArmory/test_skyyarmory_0.1.48.py [--keep] [--gear <SkyyGear jar, default the SET pin 0.3.48>]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes, line endings kept; no new class / system / command; the jar vs 0.1.47: added = exactly the
               27 Untiered files (9 items + 18 art), nothing removed, changed non-class = manifest + lang (ONLY the 18 new lines); every copy
               = its base's FINAL file except the planned keys (names, Variant, ItemLevel = the zone-end band start, the look: Texture / Icon
               ours, Model / IconProperties / Scale / Particles from the vanilla model item, no Recipe); its Interactions (Ability 1) = the
               base's; the art = recolours at the source's size; the description has the tier tag first + the Style Guide 15 action colour
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.47 -> 0.1.48: exactly the planned members (EXPECT)
  X   exec     EXECUTED in the JVM: utBase (12 copies), items() (every copy = its base's code: wand / staff / book / kunai index - incl. the
               old Second Opinion / Loophole), ArmorySig2 famOf / baseOf / answer, ArmorySig4 index / famOf / baseOf (Stormfossil), armory:fn:sig;
               mcostPct / mcostX / mcostDelta against a stand-in gear:fn:utfx (the ut28 rows) + clamps; bookMana on the Page Burst codes (the
               Leap.HAND seam: Codex back 25 %, Grimoire 30 % extra, a plain book / a non-book code nothing); utMark (Hotspring aura 50, Cavewind
               heal -100 / dmg +25, Stormfossil staff pierce); auraPick (allies only, never the caster, never twice, 50 % of an ally's share,
               the cap); auraHeal + tickFx(heal orb) with no engine (quiet, nothing added); takeUpTo(null) = 0
  E   engine   a bare server (the SkyyGear 0.2.11 harness boot: vanilla pack store by store with every codec validator), then SkyyGear 0.3.48
               (the SET pin) and THIS jar as packs: the 9 copies in the Item store (toPacket), no failure about them beyond what their own
               base gets; SkyyGear's GearUt.ok = true for ALL 64 ut28 rows now (the 9 waiting rows go live with no SkyyGear change), typeOfId /
               isGear / match at the band ends; GearUtFx answers mcost / aura / pierce / heal by the copy ids
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.48 writes nothing; start 2 = start 1
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the looks on a player; the Page Burst Mana change on a real cast (the orb SPAWN with a real
caster ref); Levitate.begin's Mana x mcostX (only mcostX runs here); the aura's near-the-caster query + TravHeal on real players; Gear's tooltip
with the lang loaded.
"""
import os, sys, json, subprocess, zipfile, re, hashlib, struct, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ut9", "arm")]
import skyybuild as B
import harness_kit as HK
import ut28 as UT28
import tier_tags as TT

VERSION, OLD = "0.1.48", "0.1.47"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEAR_JAR = os.path.abspath(HK.arg("--gear", os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.48.jar")))
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_48_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
LANG = "Server/Languages/en-US/server.lang"
ROWS = UT28.rows()
U9 = [r for r in ROWS if r[4] == "armory"]
IDS9 = [r[0] for r in U9]
BASE9 = dict((r[0], r[5]) for r in U9)
MODEL9 = dict((r[0], r[6]) for r in U9)
P_UT9 = "Server/Item/Items/SkyyArmory/UT/%s.json"
OLD3 = [("Weapon_Staff_UT_Loophole", "Weapon_Staff_Iron"), ("Weapon_Wand_UT_SecondOpinion", "Weapon_Wand_Iron"), ("Weapon_Bo_UT_Turnstile", "Weapon_Bo_Iron")]
EXPECT = {"ArmoryDefs": ["~<clinit>", "~m items", "+f UTB_IDS", "+f UTB_PAY"],          # fix round: the 2 books' own chains          # UT_IDS / UT_BASE + 9; every copy = its base's code
          "ArmorySig4": ["~m index"],          # an id not in the table answers as its utBase
          "ArmoryTrav": ["+m takeUpTo", "+m mcostPct", "+m mcostX", "+m mcostDelta", "+m bookMana", "+m bookPaid", "+m bookWant", "+m bookFloor", "+m auraPick", "+m auraHeal",
                         "+f MC_N", "+f LAST_MC", "+f AURA_N", "~<clinit>", "~m utMark", "~m added", "~m burst", "~m landed", "~m tickFx"],          # landed: fix (b) heal base
          "TravShot": ["+f utAura"], "TravFx": ["+f aura"],
          "Monk": ["~m boHit", "~m fistHit"], "Stun": ["~m fist"],          # fix round 2 (ut9fix2): the Untiered Bo / wraps answer as their base
          "Levitate": ["~m begin"],          # Levitate Mana x mcostX
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "SkyyArmoryPlugin": ["~m setup", "~m start"],          # the version text + the 0.1.48 start line
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "CfgRows2": ["~<clinit>"],          # the default file's header text names the version
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]}          # the kit's version texts (checked: only "0.1.47" -> "0.1.48" strings differ)
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")
# fix round ut9fix: the two Untiered books' own Page Burst chain (gate + charge = the metal's cost x the ut28 mcost, rounded half up)
BOOK9 = {"Weapon_Spellbook_UT_SandscriptCodex": ("Thorium", 70, 53, -25.0), "Weapon_Spellbook_UT_AshfallGrimoire": ("Adamantite", 190, 247, 30.0)}
P_BI, P_BR = "Server/Item/Interactions/Weapons/Spellbook/SkyyArmory/%s.json", "Server/Item/RootInteractions/Weapons/Spellbook/SkyyArmory/%s.json"
BOOK9_FILES = sum([[P_BI % ("SkyyArmory_Spellbook_%s_UT_%s" % (k, i.split("_UT_")[1])) for k in ("Primary", "Cast", "Cast_Cost")]
                   + [P_BR % ("SkyyArmory_Spellbook_Primary_UT_%s" % i.split("_UT_")[1])] for i in BOOK9], [])
UT9_FILES = sorted(sum([[P_UT9 % i, "Common/Items/SkyyArmory/UT/%s.png" % i, "Common/Icons/ItemsGenerated/%s.png" % i] for i in IDS9], []) + BOOK9_FILES)


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def png_wh(b):
    assert b[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    return struct.unpack(">II", b[16:24])


PLANNED = sorted(["manifest.json", LANG] + UT9_FILES)
_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    kept = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    if ed == PLANNED:
        d["ok"] += 1
    else:
        kept.append("C: non-class entries changed = the plan: extra %s, missing %s" % (sorted(set(ed) - set(PLANNED))[:6], sorted(set(PLANNED) - set(ed))[:6]))
    d["fails"] = kept
    d["notes"].append("C: non-class entries changed = manifest + lang + the 35 new Untiered files (27 + the 2 books' 8 chain files) (the kit's manifest-only check replaced)")
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = compare_with_assets


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.48 - build script') and g.count('VERSION = "0.1.48"') == 1, "S header + VERSION")
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
    K.eq(sorted(nb - na), UT9_FILES, "S added = exactly the 9 copies + their 18 art files + the 2 books' 8 chain files (no class)")
    K.eq(sorted(na - nb), [], "S nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, sorted(["manifest.json", LANG]), "S changed non-class = manifest + lang (every base / other file byte-identical)")
    la = za.read(LANG).decode("utf-8").split("\n")
    lb = zb.read(LANG).decode("utf-8").split("\n")
    new = [x for x in lb if x not in set(la)]
    K.check([x for x in la if x not in set(lb)] == [] and len(new) == 18 and sorted(x.split(" = ")[0] for x in new)
            == sorted(["items.%s.%s" % (i, k) for i in IDS9 for k in ("name", "description")]), "S lang: ONLY the 18 new lines (9 names + 9 descriptions), nothing else moved")
    names = dict((x.split(" = ", 1)[0], x.split(" = ", 1)[1]) for x in new)
    bad = []
    for r in U9:
        i, nm, kind, z = r[0], r[1], r[2], r[3]
        ds = names["items.%s.description" % i]
        tag = TT.tag_for(i)
        if names["items.%s.name" % i] != nm or tag is None or not ds.startswith(tag + TT.SEP + "Untiered %s. " % kind) \
                or ds.count('<color is="#ffcc00">') != 3 or ds.count("</color>") != ds.count("<color ") or "," in ds or re.search(r"\d", re.sub(r"<color[^>]*>[^<]*</color>", "", ds[len(tag):])):
            bad.append((i, ds))
        if tag != {1: "T3 Bronze", 2: "T6 Dusk", 3: "T9 Azurvane", 4: "T12 Cinder", 5: "T15 Lumen"}[z]:
            bad.append((i, "tag", tag))
    K.eq(bad, [], "S descriptions: the zone alloy tag first, 'Untiered <kind>.', 3 yellow action spans (Style Guide 15), no number outside a colour span, no comma")
    # fix round 2 (ut9fix2): the books' + kunai's numbers (costs red, helps green) and Cavewind promises no heal orb
    plain = lambda i: re.sub(r"<[^>]+>", "", names["items.%s.description" % i])
    R_, G_ = '<color is="#ff7a7a">%s</color>', '<color is="#7ee08a">%s</color>'
    dsc = lambda i: names["items.%s.description" % i]
    K.check("Page Burst (53 Mana): hits up to 5 within 3.5 blocks." in plain("Weapon_Spellbook_UT_SandscriptCodex") and "Levitate (7.5 Mana + 5 Stamina)" in plain("Weapon_Spellbook_UT_SandscriptCodex")
            and "Page Burst (247 Mana): hits up to 6 within 4.25 blocks." in plain("Weapon_Spellbook_UT_AshfallGrimoire") and "Levitate (13 Mana + 5 Stamina)" in plain("Weapon_Spellbook_UT_AshfallGrimoire")
            and R_ % "53" in dsc("Weapon_Spellbook_UT_SandscriptCodex") and G_ % "5" in dsc("Weapon_Spellbook_UT_SandscriptCodex") and R_ % "247" in dsc("Weapon_Spellbook_UT_AshfallGrimoire"),
            "S FIX2 (c) the Untiered books show their Page Burst Mana (the own chain 53 / 247, red), targets + radius (green, the metal's) and Levitate (x mcost)")
    bk = lambda m: re.sub(r"<[^>]+>", "", [x for x in lb if x.startswith("items.Weapon_Spellbook_%s.description = " % m)][0])
    K.check("hits up to 5 within 3.5 blocks" in bk("Thorium") and "hits up to 6 within 4.25 blocks" in bk("Adamantite") and "Levitate, 10 Mana + 5 Stamina" in bk("Thorium"),
            "S FIX2 (c) the book numbers match the metal book's own text (Thorium / Adamantite)")
    kt = re.sub(r"<[^>]+>", "", [x for x in lb if x.startswith("items.Weapon_Kunai_Thorium.description = ")][0])
    K.check("throw (20 blocks)" in plain("Weapon_Kunai_UT_ScarakStinger") and "teleport where it lands (5 Stamina + 3 Mana)" in plain("Weapon_Kunai_UT_ScarakStinger")
            and "throw, 20 blocks" in kt and "5 Stamina + 3 Mana" in kt, "S FIX2 (c) the Scarak Stinger shows the Thorium kunai's range + teleport cost")
    K.check("heal orb" not in plain("Weapon_Wand_UT_Cavewind") and "charged shot (burst)." in plain("Weapon_Wand_UT_Cavewind") and "(burst + heal orb)" in plain("Weapon_Wand_UT_HotspringBlessing"),
            "S FIX2 (c) Cavewind (heal-100) promises no heal orb; Hotspring Blessing still does")
    K.notes.append("S lang: %s" % plain("Weapon_Spellbook_UT_AshfallGrimoire"))
    K.notes.append("S lang: %s" % names["items.Weapon_Spellbook_UT_SandscriptCodex.description"])
    bidx = dict((os.path.basename(n)[:-5], n) for n in nb if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    azi = dict((os.path.basename(n)[:-5], n) for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    J = lambda zz, n: json.loads(zz.read(n).decode("utf-8-sig"))
    bad = []
    looks = []
    for r in U9:
        i, z = r[0], r[3]
        c = J(zb, P_UT9 % i)
        b = J(zb, bidx[BASE9[i]])
        if J(za, bidx[BASE9[i]]) != b:
            bad.append((i, "base file changed"))
        allowed = {"TranslationProperties", "Variant", "ItemLevel", "Texture", "Icon", "Recipe"}
        if MODEL9[i] != BASE9[i]:
            v = J(az, azi[MODEL9[i]])
            allowed |= {"Model", "IconProperties", "Scale", "Particles"}
            for k in ("Model", "IconProperties", "Scale", "Particles"):
                if c.get(k) != v.get(k):
                    bad.append((i, "look " + k, c.get(k), v.get(k)))
            looks.append("%s = %s" % (i, v["Model"]))
            src_tex, src_ico = v["Texture"], v["Icon"]
        else:
            src_tex, src_ico = b["Texture"], b["Icon"]
        diff = sorted(k for k in set(c) | set(b) if c.get(k) != b.get(k))
        wi = dict(b["Interactions"])
        if i in BOOK9:
            allowed |= {"Interactions"}
            wi["Primary"] = "SkyyArmory_Spellbook_Primary_UT_" + i.split("_UT_")[1]
        if not set(diff) <= allowed or "Recipe" in c or c["Interactions"] != wi or "Ability1" not in c["Interactions"]:
            bad.append((i, "keys", diff))
        if c["TranslationProperties"] != {"Name": "server.items.%s.name" % i, "Description": "server.items.%s.description" % i} or c["Variant"] is not True \
                or c["ItemLevel"] != UT28.ZONE_BAND[z][0] or c["Texture"] != "Items/SkyyArmory/UT/%s.png" % i or c["Icon"] != "Icons/ItemsGenerated/%s.png" % i:
            bad.append((i, "fields", c["ItemLevel"], c["Texture"]))
        for mine, src in ((c["Texture"], src_tex), (c["Icon"], src_ico)):
            sb = zb.read("Common/" + src) if ("Common/" + src) in nb else az.read("Common/" + src)
            mb = zb.read("Common/" + mine)
            if png_wh(mb) != png_wh(sb) or mb == sb:
                bad.append((i, "art", mine, png_wh(mb), png_wh(sb)))
        if c.get("Quality") != b.get("Quality"):
            bad.append((i, "quality"))
    K.eq(bad, [], "S every copy = its base's FINAL file (Ability 1 + meter + chains) except the planned keys; band start levels; the vanilla looks by path; "
                  "orange recolours at the source size; the base Quality kept (SkyyGear stamps Untiered)")
    K.notes.append("S looks: %s" % looks)
    # fix (a): each Untiered book's own chain = the metal's chain with the gate + the charge at the mcost cost; the launch / effect / fail / Levitate shared
    bad = []
    for i, (mt, base, pay, pct) in sorted(BOOK9.items()):
        t = i.split("_UT_")[1]
        pr, prb = J(zb, P_BI % ("SkyyArmory_Spellbook_Primary_UT_" + t)), J(zb, P_BI % ("SkyyArmory_Spellbook_Primary_" + mt))
        cs, csb = J(zb, P_BI % ("SkyyArmory_Spellbook_Cast_UT_" + t)), J(zb, P_BI % ("SkyyArmory_Spellbook_Cast_" + mt))
        co, cob = J(zb, P_BI % ("SkyyArmory_Spellbook_Cast_Cost_UT_" + t)), J(zb, P_BI % ("SkyyArmory_Spellbook_Cast_Cost_" + mt))
        rt = J(zb, P_BR % ("SkyyArmory_Spellbook_Primary_UT_" + t))
        want_pr = dict(prb)
        want_pr["Next"] = dict(prb["Next"])
        want_pr["Next"]["0"] = "SkyyArmory_Spellbook_Cast_UT_" + t
        want_cs = json.loads(json.dumps(csb).replace('"SkyyArmory_Spellbook_Cast_Cost_%s"' % mt, '"SkyyArmory_Spellbook_Cast_Cost_UT_%s"' % t))
        want_cs["Costs"] = {"Mana": pay}
        fxw = [float(w[5:]) for r_ in U9 if r_[0] == i for w in r_[8].split() if w.startswith("mcost")]
        if csb["Costs"] != {"Mana": base} or cob != {"Type": "ChangeStat", "StatModifiers": {"Mana": -base}} or pr != want_pr or cs != want_cs \
                or co != {"Type": "ChangeStat", "StatModifiers": {"Mana": -pay}} or rt != {"Interactions": ["SkyyArmory_Spellbook_Primary_UT_" + t]} \
                or ("SkyyArmory_Spellbook_Cast_Launch_" + mt) not in json.dumps(cs) or prb["Next"]["1"] != pr["Next"]["1"] or fxw != [pct] \
                or pay != int(math.floor(base * (1 + pct / 100.0) + 0.5)):
            bad.append((i, pr, cs, co, rt, fxw))
    K.eq(bad, [], "S FIX (a): the Codex gates + charges 53 Mana (Thorium 70 x 0.75, half up), the Grimoire 247 (Adamantite 190 x 1.3) on their OWN chain; "
                  "the metal's launch (same Page Burst orb code), effect, fail and Levitate shared; the metal chains unchanged")
    K.check(not [n for n in nb if n.startswith("Server/Item/Recipes/") and "_UT_" in n] and not [n for n in nb if n.startswith("Server/Item/Items/")
            and n.endswith(".json") and "_UT_" in n and "Recipe" in J(zb, n)], "S no recipe makes any Untiered item (crafted never UT)")
    K.check(not set(UT9_FILES) & set(az.namelist()), "S no new file shadows an Assets.zip path")
    m = json.loads(zb.read("manifest.json"))
    K.check(m["Version"] == VERSION and "9 Untiered Zone 2-5 weapons" in m["Description"], "S manifest version + description")
    K.check("if (s.utHeal != 0.0 || s.utAura > 0.0) hb = utHealBase(hb, s.utDmg, s.utHeal);" in g
            and 'if (hl != 0.0 || s.utAura > 0.0) { s.utHeal = hl; s.utDmg = utfx(h, "dmg"); }' in g,
            "S FIX (b): an aura wand's orb heals from the damage before its own cut (burst + utMark)")
    K.check("mana = mana * @PKG@.ArmoryTrav.mcostX(item);" in g and "hf.aura = s.utAura;" in g and "if (f.aura > 0.0) auraHeal(f, buf, us, hs);" in g
            and "    bookMana(buf, cu, c);" in g, "S the 4 call sites (Levitate Mana, the orb's aura, the heal tick, the Page Burst spawn)")
    K.check("    String fb = @PKG@.ArmoryDefs.utBase(item);" in g and "if (FIST_IDS[i].equals(fb)) fi = i;" in g and "if (FIST_IDS[i].equals(item)) fi = i;" not in g,
            "S FIX2 (a) Hard Knuckles (Stun.fist, Class.Monk.PB1) finds Untiered wraps by their base")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject, JInt, JDouble, JLong, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Defs, S2, S4, Trav, Leap, TS, TF, SigFn = (JClass(PKG + n) for n in ("ArmoryCfg", "ArmoryDefs", "ArmorySig2", "ArmorySig4", "ArmoryTrav", "Leap",
                                                                               "TravShot", "TravFx", "ArmorySigFn"))
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    Cfg.useDefaults()
    # ---- fix round 2 (ut9fix2): Monk Pole-Vault / Rising Strike find the Untiered Bo + wraps (and The Turnstile) as their base
    Monk = JClass(PKG + "Monk")
    mk = lambda f, i: float(getattr(Monk, f)(JString(i)))
    K.eq([mk("boHit", "Weapon_Bo_UT_CrushingTail"), mk("fistHit", "Weapon_Fist_UT_SteppeWind"), mk("fistHit", "Weapon_Fist_UT_EmberrootWraps"), mk("boHit", "Weapon_Bo_UT_Turnstile")],
         [mk("boHit", "Weapon_Bo_Mithril"), mk("fistHit", "Weapon_Fist_Wraps_Silk"), mk("fistHit", "Weapon_Fist_Wraps_Cindercloth"), mk("boHit", "Weapon_Bo_Iron")],
         "X FIX2 (a) Monk.boHit / fistHit: Crushing Tail, Steppe Wind, Emberroot Wraps, The Turnstile = their base's hit (vault() / rise() refused them before)")
    K.check(mk("boHit", "Weapon_Bo_UT_CrushingTail") > 0.0 and mk("fistHit", "Weapon_Fist_UT_SteppeWind") > 0.0 and mk("fistHit", "Weapon_Fist_UT_EmberrootWraps") > 0.0
            and mk("boHit", "Weapon_Bo_UT_Turnstile") > 0.0 and mk("boHit", "Weapon_Wand_UT_Cavewind") == 0.0 and mk("fistHit", "Weapon_Bo_UT_CrushingTail") == 0.0
            and float(Monk.boHit(None)) == 0.0, "X FIX2 (a) the hits are real (> 0); a wand / the Bo as a fist / null = 0")
    # ---- the copies answer as their base
    allc = OLD3 + [(i, BASE9[i]) for i in IDS9]
    K.eq([(str(a), str(Defs.utBase(JString(a)))) for a, b in allc], [(a, b) for a, b in allc], "X utBase: all 12 Untiered copies -> their base")
    K.eq(str(Defs.utBase(JString("Weapon_Wand_Cobalt"))), "Weapon_Wand_Cobalt", "X utBase: a plain id answers itself")
    idx = lambda f, x: int(getattr(Defs, f)(JString(x)))
    got, want = [], []
    for a, b in allc:
        for f in ("wandIndex", "staffIndex", "bookIndex", "kunaiIndex"):
            got.append((a, f, idx(f, a)))
            want.append((a, f, idx(f, b)))
    K.eq(got, want, "X items(): every Untiered copy = its base's wand / staff / book / kunai index (the Second Opinion's Ricochet now finds its wand)")
    K.check(idx("wandIndex", "Weapon_Wand_UT_HotspringBlessing") >= 0 and idx("bookIndex", "Weapon_Spellbook_UT_AshfallGrimoire") >= 0
            and idx("kunaiIndex", "Weapon_Kunai_UT_ScarakStinger") >= 0 and idx("staffIndex", "Weapon_Staff_UT_Stormfossil") >= 0
            and idx("wandIndex", "Weapon_Wand_UT_SecondOpinion") == idx("wandIndex", "Weapon_Wand_Iron") >= 0 and idx("wandIndex", "Weapon_Spellbook_UT_SandscriptCodex") == -1,
            "X the indices are real (>= 0) and a book copy is no wand")
    fam2 = dict((i, int(S2.famOf(JString(i)))) for i in IDS9)
    K.eq(fam2, {"Weapon_Spellbook_UT_SandscriptCodex": 3, "Weapon_Fist_UT_SteppeWind": 1, "Weapon_Kunai_UT_ScarakStinger": 2, "Weapon_Wand_UT_HotspringBlessing": -1,
                "Weapon_Spellbook_UT_AshfallGrimoire": 3, "Weapon_Fist_UT_EmberrootWraps": 1, "Weapon_Staff_UT_Stormfossil": -1, "Weapon_Wand_UT_Cavewind": -1,
                "Weapon_Bo_UT_CrushingTail": 0}, "X ArmorySig2.famOf: book 3 / fist 1 / kunai 2 / Bo 0 (wand + staff are not sig2)")
    K.eq([(i, float(S2.baseOf(fam2[i], JString(i)))) for i in IDS9 if fam2[i] >= 0], [(i, float(S2.baseOf(fam2[i], JString(BASE9[i])))) for i in IDS9 if fam2[i] >= 0],
         "X ArmorySig2.baseOf: each copy's signature hit = its base's")
    st = "Weapon_Staff_UT_Stormfossil"
    K.check(int(S4.index(JString(st))) == int(S4.index(JString("Weapon_Staff_Mithril"))) >= 0 and int(S4.famOf(JString(st))) == 0
            and float(S4.baseOf(JString(st))) == float(S4.baseOf(JString("Weapon_Staff_Mithril"))) > 0.0,
            "X ArmorySig4: The Stormfossil answers as the Mithril staff (index / family 0 staff / hit %s)" % float(S4.baseOf(JString(st))))
    K.check(int(S4.index(JString("Weapon_Staff_UT_Loophole"))) >= 0 and int(S4.index(JString("Weapon_Nothing_UT_X"))) == -1 and int(S4.index(None)) == -1,
            "X ArmorySig4.index: the Loophole still found by its own row; an unknown / null id = -1")
    sig = SigFn()
    sg = dict((i, sig.apply(JString(i))) for i in IDS9)
    K.check(all(sg[i] is not None and str(sg[i][0]) == str(sig.apply(JString(BASE9[i]))[0]) for i in IDS9),
            "X armory:fn:sig: every copy names its base's Ability 1: %s" % dict((i.split("_UT_")[1], str(sg[i][0]) if sg[i] is not None else None) for i in IDS9))
    K.check(str(sig.apply(JString("Weapon_Wand_UT_SecondOpinion"))[0]) == "Ricochet", "X armory:fn:sig: the Second Opinion = Ricochet (as before)")
    # ---- a stand-in SkyyGear gear:fn:utfx: the ut28 rows (fixed words), "cfg:auraReach" = 8
    fx = {}
    for r in ROWS:
        for w in r[8].split():
            m = re.match(r"^([a-zA-Z]+)([+-][0-9.]+)$", w)
            if m:
                fx[(r[0], m.group(1))] = float(m.group(2))
    over = {}

    @JImplements("java.util.function.Function")
    class Utfx(object):
        @JOverride
        def apply(self, a):
            i, w = str(a[0]), str(a[1])
            if w == "cfg:auraReach":
                return JObject(JDouble(8.0), JClass("java.lang.Double"))
            return JObject(JDouble(over.get((i, w), fx.get((i, w), 0.0))), JClass("java.lang.Double"))
    K.check(float(Trav.mcostPct(JString("Weapon_Spellbook_UT_SandscriptCodex"))) == 0.0, "X mcostPct with no SkyyGear = 0")
    br.put("gear:fn:utfx", Utfx())
    K.eq([float(Trav.mcostPct(JString(i))) for i in ("Weapon_Spellbook_UT_SandscriptCodex", "Weapon_Spellbook_UT_AshfallGrimoire", "Weapon_Spellbook_Thorium", "Weapon_Wand_UT_Cavewind")],
         [-25.0, 30.0, 0.0, 0.0], "X mcostPct reads SkyyGear's mcost words (Codex -25, Grimoire +30, others 0)")
    over[("Weapon_Spellbook_UT_SandscriptCodex", "mcost")] = -500.0
    over[("Weapon_Spellbook_UT_AshfallGrimoire", "mcost")] = 900.0
    K.eq((float(Trav.mcostPct(JString("Weapon_Spellbook_UT_SandscriptCodex"))), float(Trav.mcostPct(JString("Weapon_Spellbook_UT_AshfallGrimoire"))),
          float(Trav.mcostX(JString("Weapon_Spellbook_UT_SandscriptCodex"))), float(Trav.mcostPct(None))), (-100.0, 500.0, 0.0, 0.0),
         "X mcostPct clamps -100 .. 500; mcostX never below 0; null = 0")
    over.clear()
    K.eq((round(float(Trav.mcostX(JString("Weapon_Spellbook_UT_SandscriptCodex"))), 6), round(float(Trav.mcostX(JString("Weapon_Spellbook_UT_AshfallGrimoire"))), 6),
          float(Trav.mcostDelta(70.0, -25.0)), float(Trav.mcostDelta(70.0, 30.0)), float(Trav.mcostDelta(0.0, 30.0))), (0.75, 1.3, -17.5, 21.0, 0.0),
         "X mcostX (Levitate's factor) 0.75 / 1.3; mcostDelta 70 Mana: -17.5 back / +21 extra; no cost = 0")
    # bookMana on the Page Burst codes (the Leap.HAND seam: who holds what)
    HM = JClass("java.util.concurrent.ConcurrentHashMap")()
    Leap.HAND = HM
    u = UUID.randomUUID()
    bcost = [int(x) for x in Defs.B_COST]
    bi = lambda i: idx("bookIndex", i)
    res = []
    for held, code in (("Weapon_Spellbook_UT_SandscriptCodex", 7000 + bi("Weapon_Spellbook_Thorium")), ("Weapon_Spellbook_UT_AshfallGrimoire", 7000 + bi("Weapon_Spellbook_Adamantite")),
                       ("Weapon_Spellbook_Thorium", 7000 + bi("Weapon_Spellbook_Thorium")), ("Weapon_Spellbook_UT_SandscriptCodex", 2000), ("Weapon_Spellbook_UT_SandscriptCodex", 7999)):
        HM.put(u, JString(held))
        n0 = int(Trav.MC_N)
        res.append((round(float(Trav.bookMana(None, u, JInt(code))), 6), int(Trav.MC_N) - n0))
    K.eq(res, [(0.0, 0), (0.0, 0), (0.0, 0), (0.0, 0), (0.0, 0)],
         "X FIX (a) bookMana at the defaults: the Codex / Grimoire chains already charged their mcost cost (53 / 247; the half-Mana rounding is ignored), "
         "a plain book / a non-book code / an index past the books = nothing")
    ti, ai = bi("Weapon_Spellbook_Thorium"), bi("Weapon_Spellbook_Adamantite")
    K.eq([float(Trav.bookPaid(JString("Weapon_Spellbook_UT_SandscriptCodex"), JInt(ti))), float(Trav.bookPaid(JString("Weapon_Spellbook_UT_AshfallGrimoire"), JInt(ai))),
          float(Trav.bookPaid(JString("Weapon_Spellbook_Thorium"), JInt(ti))), float(Trav.bookPaid(None, JInt(ai))), float(Trav.bookPaid(JString("x"), JInt(999))),
          float(Trav.bookWant(JString("Weapon_Spellbook_UT_SandscriptCodex"), JInt(ti))), float(Trav.bookWant(JString("Weapon_Spellbook_UT_AshfallGrimoire"), JInt(ai))),
          float(Trav.bookWant(JString("Weapon_Spellbook_Thorium"), JInt(ti)))],
         [53.0, 247.0, float(bcost[ti]), float(bcost[ai]), 0.0, 52.5, 247.0, float(bcost[ti])],
         "X FIX (a) bookPaid = the copy's own chain (53 / 247) else the metal's cost; bookWant = the metal's cost x the live mcost")
    res = []
    for held, code, pct in (("Weapon_Spellbook_UT_SandscriptCodex", 7000 + ti, -50.0), ("Weapon_Spellbook_UT_AshfallGrimoire", 7000 + ai, 0.0),
                            ("Weapon_Spellbook_UT_AshfallGrimoire", 7000 + ai, 60.0)):
        over[(held, "mcost")] = pct          # an admin's edit of the mcost line (0 = the line removed)
        HM.put(u, JString(held))
        n0 = int(Trav.MC_N)
        res.append((round(float(Trav.bookMana(None, u, JInt(code))), 6), int(Trav.MC_N) - n0))
    over.clear()
    K.eq(res, [(-18.0, 1), (-57.0, 1), (57.0, 1)], "X FIX (a) bookMana after an admin's mcost edit: only the difference from the chain (Codex -50 %: 35 wanted, "
         "18 back; Grimoire line removed: 190 wanted, 57 back; Grimoire +60 %: 304 wanted, 57 extra)")
    K.check(float(Trav.bookMana(None, None, JInt(7000))) == 0.0, "X bookMana: no caster = nothing")
    # fix round 2 (ut9fix2): a hotbar swap between the cast and the orb spawn changes nothing; never back more than the cheapest chain charged
    res = []
    for held, code, pct in (("Weapon_Spellbook_UT_AshfallGrimoire", 7000 + ti, 0.0), ("Weapon_Spellbook_UT_AshfallGrimoire", 7000 + ti, -100.0),
                            ("Weapon_Spellbook_UT_SandscriptCodex", 7000 + ai, -100.0), ("Weapon_Spellbook_Thorium", 7000 + ai, 0.0),
                            ("Weapon_Wand_Cobalt", 7000 + ti, 0.0), ("Weapon_Spellbook_UT_AshfallGrimoire", 7000 + ai, -100.0),
                            ("Weapon_Spellbook_UT_SandscriptCodex", 7000 + ti, -100.0)):
        if pct != 0.0:
            over[(held, "mcost")] = pct
        HM.put(u, JString(held))
        n0 = int(Trav.MC_N)
        res.append((round(float(Trav.bookMana(None, u, JInt(code))), 6), int(Trav.MC_N) - n0))
        over.clear()
    K.eq(res, [(0.0, 0), (0.0, 0), (0.0, 0), (0.0, 0), (0.0, 0), (-190.0, 1), (-53.0, 1)],
         "X FIX2 (b) bookMana: a swap to another book's copy / a metal book / no book = nothing (a Thorium cast + the Grimoire in hand gave 156 back before); "
         "the Grimoire at -100 % gives back at most 190 (the Adamantite chain's cost - a metal cast + a swap to the copy gains nothing), the Codex 53")
    K.eq([float(Trav.bookFloor(JInt(ti))), float(Trav.bookFloor(JInt(ai))), float(Trav.bookFloor(JInt(-1))), float(Trav.bookFloor(JInt(999)))],
         [53.0, 190.0, 0.0, 0.0], "X FIX2 (b) bookFloor: the cheapest chain of the book index (Thorium: the Codex 53; Adamantite: the metal 190); out of range 0")
    K.check(float(Trav.takeUpTo(None, None, 0, 5.0)) == 0.0 and float(Trav.takeUpTo(None, None, -1, 5.0)) == 0.0, "X takeUpTo with no entity / stat = 0 (quiet)")
    # utMark: the aura / heal / pierce words on a real TravShot
    res = {}
    for held, code in (("Weapon_Wand_UT_HotspringBlessing", 2003), ("Weapon_Wand_UT_Cavewind", 2005), ("Weapon_Staff_UT_Stormfossil", 3005), ("Weapon_Wand_Cobalt", 2003)):
        HM.put(u, JString(held))
        s = TS(0.0, 0.0, 0.0, 0.0, code, u, "x")
        Trav.utMark(s, None, u, code)
        res[held] = (float(s.utAura), float(s.utHeal), float(s.utDmg), bool(s.utPierce))
    K.eq(res, {"Weapon_Wand_UT_HotspringBlessing": (50.0, 0.0, -25.0, False), "Weapon_Wand_UT_Cavewind": (0.0, -100.0, 25.0, False),
               "Weapon_Staff_UT_Stormfossil": (0.0, 0.0, 0.0, True), "Weapon_Wand_Cobalt": (0.0, 0.0, 0.0, False)},
         "X utMark: Hotspring aura 50 + its dmg -25 kept (FIX (b)); Cavewind heal -100 + dmg +25 (its orb heals nothing); Stormfossil staff quick shots pierce; a plain wand nothing")
    K.check(round(float(Trav.utHealBase(75.0, -25.0, 0.0)), 6) == 100.0, "X FIX (b) Hotspring: a 75 landed hit (25 % cut) heals from 100 - the full orb share; the aura party gets 50 % of that")
    K.check(float(Trav.utHealBase(100.0, 25.0, -100.0)) == 0.0, "X Cavewind: utHealBase = 0 (burst() makes no heal orb: healBase > 0 needed)")
    Leap.HAND = None
    # auraPick (pure): allies only (class:fn:ally stand-in), never the caster, never one the orb already healed, 50 % of an ally's share, the cap
    me, a1, a2, a3, stranger = (UUID.randomUUID() for _ in range(5))
    party = set(str(x) for x in (a1, a2, a3))

    @JImplements("java.util.function.Function")
    class Ally(object):
        @JOverride
        def apply(self, a):
            return JObject(str(a[1]) in party and str(a[0]) == str(me), JClass("java.lang.Boolean"))
    br.put("class:fn:ally", Ally())
    us, hs = AL(), AL()
    us.add(a3)
    hs.add(JObject(JDouble(9.0), JClass("java.lang.Double")))
    cand = AL()
    for x in (me, a1, stranger, a2, a3, a1, JString("junk")):
        cand.add(x)
    n = int(Trav.auraPick(me, cand, 10.0, 50.0, us, hs))
    party_pct = int(Cfg.ORB_PARTY_PCT)
    half = round(10.0 * party_pct / 100.0 * 0.5, 6)
    K.check(n == 2 and [str(x) for x in us] == [str(a3), str(a1), str(a2)] and [round(float(x), 6) for x in hs] == [9.0, half, half],
            "X auraPick: 2 allies added at 50 %% of an ally's share (party %d %%), never the caster / a stranger / the one the orb healed / a duplicate / junk: %s" % (party_pct, [float(x) for x in hs]))
    us2, hs2 = AL(), AL()
    n2 = int(Trav.auraPick(me, cand, 10.0, 250.0, us2, hs2))
    K.check(n2 == 3 and all(round(float(x), 6) == round(10.0 * party_pct / 100.0, 6) for x in hs2), "X auraPick: aura above 100 is capped at 100 %% (%s)" % [float(x) for x in hs2])
    K.eq([int(Trav.auraPick(me, cand, 10.0, 0.0, AL(), AL())), int(Trav.auraPick(me, cand, 0.0, 50.0, AL(), AL())), int(Trav.auraPick(None, cand, 10.0, 50.0, AL(), AL())),
          int(Trav.auraPick(me, None, 10.0, 50.0, AL(), AL()))], [0, 0, 0, 0], "X auraPick: no aura / no heal / no caster / no list = nothing")
    # auraHeal + the heal orb's tick with no engine: quiet, nothing added
    f = TF(2, 0.0, 64.0, 0.0, 0.0, 64.0, 0.0, 3.0, JLong(10 ** 13), JLong(0), JLong(250), 4.0, me, None, 2003)
    f.aura = 50.0
    us3, hs3 = AL(), AL()
    a0 = int(Trav.AURA_N)
    K.check(int(Trav.auraHeal(f, None, us3, hs3)) == 0 and us3.size() == 0 and int(Trav.AURA_N) == a0, "X auraHeal: no caster entity (no engine) = nothing added, no throw")
    f.aura = 0.0
    K.check(int(Trav.auraHeal(f, None, us3, hs3)) == 0, "X auraHeal: aura 0 = nothing")

    @JImplements("java.util.function.Function")
    class NoOne(object):
        @JOverride
        def apply(self, a):
            return AL()
    Trav.NEAR = NoOne()
    f.aura = 50.0
    try:
        Trav.tickFx(f, None, None, JLong(1000))
        K.check(int(f.ticks) == 1 and int(Trav.AURA_N) == a0, "X tickFx (heal orb, aura 50) with nobody near and no engine: one tick, the aura call quiet")
    except Exception as ex:
        K.check(False, "X tickFx threw: %s" % str(ex)[:300])
    Trav.NEAR = None
    br.remove("class:fn:ally")
    br.remove("gear:fn:utfx")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- E: the booted engine (vanilla + SkyyGear + this jar)
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JString, JArray, JInt
    K = HK.Child(out)
    h211 = os.path.join(ROOT, "SkyyGear", "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", GEAR_JAR, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    gv = re.search(r"SkyyGear-([0-9.]+)\.jar$", GEAR_JAR).group(1)
    H.update({"JAR": GEAR_JAR, "SCRATCH": esc, "VERSION": gv})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, GEAR_JAR, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    ITEM = E["ITEM"]
    # this jar as its own pack (its common files registered like the library's add_common)
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    Paths, FSs, HashMap = JClass("java.nio.file.Paths"), JClass("java.nio.file.FileSystems"), JClass("java.util.HashMap")
    apack = "Skyy:%s SkyyArmory" % VERSION
    fs = FSs.newFileSystem(Paths.get(jar), HashMap())
    n = 0
    with zipfile.ZipFile(jar) as z:
        for nm in z.namelist():
            if nm.startswith("Common/") and not nm.endswith("/"):
                CAR.addCommonAsset(apack, FCA(fs.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(z.read(nm)).hexdigest(), None))
                n += 1
    afail, arec = E["loadpack"](jar, apack, False)
    mine = set(IDS9)
    bmsg = set(r[1] for r in arec if r[0] in ("SEVERE", "WARNING"))

    def same_as_base(m):
        hit = [i for i in mine if i in m]
        return len(hit) == 1 and m.replace(hit[0], BASE9[hit[0]]) in bmsg
    ours = [r for r in arec if r[0] in ("SEVERE", "WARNING") and [i for i in mine if i in r[1]] and not same_as_base(r[1])]
    K.notes.append("E V: the Armory pack: %d common files, failed stores %s (vanilla's %s), %d SEVERE / WARNING lines in all (bare boot), %d about the copies = their base's own" % (
        n, list(afail), list(E["vfail"]), len([r for r in arec if r[0] in ("SEVERE", "WARNING")]),
        len([r for r in arec if r[0] in ("SEVERE", "WARNING") and [i for i in mine if i in r[1]] and same_as_base(r[1])])))
    K.check(not ours and set(afail) <= set(E["vfail"]) | set(E["fail"]), "E V: no failure about the 9 copies beyond their base's (failed stores %s): %s" % (list(afail), [r[1][:200] for r in ours[:3]]))
    # fix (a): the 2 books' own chain files load like the metal's (no SEVERE / WARNING of their own) and sit in the Interaction / root stores
    bt = ["_UT_" + i.split("_UT_")[1] for i in BOOK9]
    btm = dict(("_UT_" + i.split("_UT_")[1], "_" + BOOK9[i][0]) for i in BOOK9)
    tomet = lambda m: [m.replace(x, btm[x]) for x in bt if x in m][0]
    allb = set(r[1] for r in arec)
    hits = [r[1] for r in arec if r[0] in ("SEVERE", "WARNING") and [x for x in bt if x in r[1]]]
    own = [m for m in hits if tomet(m) not in allb]
    K.eq(own, [], "E FIX (a): no SEVERE / WARNING about the books' own Page Burst chains beyond the metal chain's own in this bare boot (%d lines = the metal's, "
                  "e.g. the bare boot has no Mana stat type)" % len(hits))
    try:
        INT = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
        RTI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.RootInteraction")
        miss = [k for t_ in bt for k in ("SkyyArmory_Spellbook_Primary" + t_, "SkyyArmory_Spellbook_Cast" + t_, "SkyyArmory_Spellbook_Cast_Cost" + t_)
                if INT.getAssetMap().getAsset(k) is None and INT.getAssetMap().getAsset(k.replace(t_, btm[t_])) is not None] \
            + [("root", "SkyyArmory_Spellbook_Primary" + t_) for t_ in bt if RTI.getAssetMap().getAsset("SkyyArmory_Spellbook_Primary" + t_) is None]
        K.eq(miss, [], "E FIX (a): the books' own Primary / Cast / Cast_Cost interactions + Primary root are in the engine's stores wherever the metal's are")
    except Exception as ex:
        K.notes.append("E FIX (a): the Interaction store could not be read here (%s) - the load lines above are the proof" % str(ex)[:160])
    for i in IDS9:
        it = ITEM.getAssetMap().getAsset(i)
        try:
            pk = it.toPacket() if it is not None else None
            K.check(it is not None and pk is not None and int(it.getMaxStack()) == 1, "E %s in the Item store (toPacket, max stack 1)" % i)
        except Exception as ex:
            K.check(False, "E %s packet: %s" % (i, str(ex)[:200]))
    # SkyyGear's side: every one of the 64 rows is usable now
    P = lambda nm: JClass("com.skyy.gear." + nm)
    Cfg, Data, Ut, Fx, Pool = P("GearCfg"), P("GearData"), P("GearUt"), P("GearUtFx"), P("GearPool")
    Props = JClass("java.util.Properties")
    p = Props()
    p.load(JClass("java.io.StringReader")(str(Cfg.defaultsText())))
    Cfg.apply(p, False)
    tab = Cfg.UTAB
    okd = dict((r[0], bool(Ut.ok(tab, int(Ut.idx(tab, JString(r[0])))))) for r in ROWS)
    K.eq(okd, dict((r[0], True) for r in ROWS), "E GearUt.ok: ALL 64 ut28 rows usable with this jar loaded (the 9 waiting rows are live - no SkyyGear change needed)")
    bad = []
    for r in U9:
        i = r[0]
        ty = int(Pool.typeOfId(JString(i)))
        lo, hi = UT28.ZONE_BAND[r[3]]
        k = int(Ut.idx(tab, JString(i)))
        if not (ty >= 0 and bool(Data.isGear(JString(i))) and not bool(Ut.crafted(JString(i))) and bool(Ut.match(tab, k, ty, lo)) and bool(Ut.match(tab, k, ty, hi))
                and not bool(Ut.match(tab, k, ty, hi + 1))):
            bad.append((i, ty, str(Pool.T_NAME[ty]) if ty >= 0 else None))
    K.eq(bad, [], "E every Armory copy: a bag type, gear, no recipe, an orange bag of its type at Lv %s may pick it" % sorted(set("%d-%d" % UT28.ZONE_BAND[r[3]] for r in U9)))
    K.notes.append("E bag types: %s" % dict((r[0], str(Pool.T_NAME[int(Pool.typeOfId(JString(r[0])))])) for r in U9))
    GFn = P("GearFn")
    if True:
        q = lambda i, w: float(GFn.utfx(JArray(JClass("java.lang.Object"))([JString(i), JString(w)])))
        K.eq([q("Weapon_Spellbook_UT_SandscriptCodex", "mcost"), q("Weapon_Spellbook_UT_AshfallGrimoire", "mcost"), q("Weapon_Wand_UT_HotspringBlessing", "aura"),
              q("Weapon_Staff_UT_Stormfossil", "pierce"), q("Weapon_Wand_UT_Cavewind", "heal"), q("x", "cfg:auraReach")], [-25.0, 30.0, 50.0, 1.0, -100.0, 8.0],
             "E the REAL gear:fn:utfx answers the words this jar reads by the copy ids (mcost / aura / pierce / heal) + the aura reach 8")
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
    hashes = [tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    t1 = open(fp, "rb").read()
    K.check(b"0.1.48" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.48 writes nothing of its own; line endings kept")
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(hashes[0]) | set(hashes[1]) if hashes[0].get(k) != hashes[1].get(k))[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("engine", run_engine), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
