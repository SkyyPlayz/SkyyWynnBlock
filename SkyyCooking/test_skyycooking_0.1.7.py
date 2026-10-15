"""Harness for SkyyCooking 0.1.7 (tools/cooking_0_1_7_patch.py): the FOOD REMAP TO HYTALE 0.7 (round cook017) + the SOUND PASS ROUND 2 part
(meal done + the per-player sound switch).
Build first: python tools/cooking_0_1_7_patch.py && python SkyyCooking/build_skyycooking_0.1.7.py

    python SkyyCooking/test_skyycooking_0.1.7.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py; game files only through the CACHED copies of tools/serverjar.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.6 -> 0.1.7: + CookSnd; CookXpTask.run (the sting), the plugin setup, the kit's rows / version texts only; non-class
               entries: manifest + the generated effects / family checks / graded dishes / lang (the 3 Cooking Bench recipes byte-equal)
  FX  assets   (pure Python, independent of the build script) against the cached 0.7 Assets.zip:
               R  every effect / interaction / root interaction / item / Common file a generated asset names exists (jar or Assets.zip);
                  no jar entry names Food_Instant_Heal_T2 / T3 / Bread (and Assets.zip really lacks them)
               S  every generated effect = its 0.7 vanilla base with ONLY the strength fields x (1 + 0.32 x Grade) and Duration x 2^(Grade/5)
                  (instant effects keep 0.1 s) - the Grade scaling of 0.1.4-0.1.6, unchanged
               M  the mapping table: each dish's heal = HEAL_07[its 0.1.6 heal] at every Grade; the rest of each eat chain = 0.1.6's;
                  the remapped heal numbers = 0.1.6's (10 % -> +10 health, 15 % -> +15 at the base 100 max health); the buff strengths =
                  0.1.6's (only the 0.7 durations differ)
               I  item ids = 0.1.6's; graded dishes keep Parent Template_Food, no Recipe; the 4 flattened dishes carry their vanilla parent
                  dish's keys (Consumable ...); lang keys = 0.1.6's, the heal line says "% health" only for percent heals
               F  every graded HealthRegen check clears 0.7's HealthRegen_Buff_Raw
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage): tools/soundpass_gen.unit (file, rows, check= hook, ids,
      gate, the per-player switch settings:sounds:<uuid>, missing id, offline, ok()); THE CALL SITE's call CookSnd.meal(pr, gave): a graded
      dish = the cook only (UI 2D), gave false = silent, muted = silent, the Meal row off = silent, a batch = ONE sting; static: only
      CookSnd.playTo calls SoundUtil, CookXpTask.run calls CookSnd.meal after the profile check, setup loads sounds.properties before the
      kit; KIT end to end (cmdSetConsole edits, file lines)
  D   live     setup()'s data steps (4 one-time updates, CookCfg.load, CookSnd.load, CfgPub.start) TWICE on a scratch COPY of the live
               Skyy_SkyyCooking: the first adds only sounds.properties (cooking.properties untouched - the live file is already 0.1.6),
               the second changes nothing
  AA  engine-access audit
NOT testable here (UNVERIFIED until the game loads it): the engine applying Food_Health_Restore copies through ApplyEffect (the same
interaction type and asset store as 0.1.6's heals), the tooltip drawing.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK
import soundpass_gen as G
import serverjar as SJ

SK.ASSETS = SJ.assets_zip()   # the cached copy (never the installed game file)
VERSION = "0.1.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCooking-0.1.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "cook017", "harness")))
PKG = "com.skyy.cooking."
LIVE_DIR = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCooking")
SOUNDS = [dict(key="meal", field="MEAL", label="Meal done", id="SFX_Furnace_Bench_Processing_Complete",
               help="A Cooking Bench craft gave a graded dish (not ingredients, not plain food).")]
EXPECT = {
    "CookXpTask": ["~m run"],                                          # the sting
    "SkyyCookingPlugin": ["~m setup"],                                 # CookSnd.load before the kit
    "CookCfg": ["~m load"],                                            # the default text's "SkyyCooking 0.1.7" header line only
    "CookMig": ["~m logLine", "~m migrate"],                           # WHO "SkyyCooking 0.1.7" (History / change-log label)
    "CookXpMig": ["~m migrate"], "CookTblMig": ["~m migrate"], "CookIngMig": ["~m migrate"],   # the same version string
    "CfgHist": ["~m compact", "~m snapshot", "~m versions"],           # the kit: KEEP 20 -> 10
    "CfgFile": ["~<clinit>", "~m init"],                               # the kit: the second file
    "CfgRows": ["+f BRIDGE", "+f DL1", "+m bridge0", "~<clinit>", "~m bridge", "~m defLines", "~m header"],   # + the kit's cached bridge (skyycfg.py since 0.1.6)
    "CfgFn": ["~m opExport"],
}
ADDED = ["CookSnd"]

REMOVED = ["Food_Instant_Heal_T2", "Food_Instant_Heal_T3", "Food_Instant_Heal_Bread"]
HEAL_07 = {"Food_Instant_Heal_T1": "Food_Instant_Heal_T1", "Food_Instant_Heal_T2": "Food_Health_Restore_Small",
           "Food_Instant_Heal_T3": "Food_Health_Restore_Medium", "Food_Instant_Heal_Bread": "Food_Health_Restore_Medium"}
DISHES = ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked", "Food_Bread", "Food_Kebab_Fruit", "Food_Kebab_Meat",
          "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Salad_Berry", "Food_Salad_Mushroom", "Food_Popcorn", "Food_Pie_Apple",
          "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Salad_Caesar"]
BASES = ["Food_Instant_Heal_T1", "Food_Health_Restore_Small", "Food_Health_Restore_Medium"] + \
        ["%s_Buff_T%d" % (f, t) for f in ("HealthRegen", "Meat", "FruitVeggie") for t in (1, 2, 3)]
EFF, INT, ITM = "Server/Entity/Effects/SkyyCook/", "Server/Item/Interactions/SkyyCook/", "Server/Item/Items/SkyyCook/"


def r4(v):
    return float("%.4f" % v)


def run_assets(out, jar, scratch, _home):
    K = HK.Child(out)
    AZ = zipfile.ZipFile(SJ.assets_zip())
    an = AZ.namelist()

    def ids(prefix):
        return dict((os.path.basename(n)[:-5], n) for n in an if n.startswith(prefix) and n.endswith(".json"))
    VE, VI, VR, VIT = ids("Server/Entity/Effects/"), ids("Server/Item/Interactions/"), ids("Server/Item/RootInteractions/"), ids("Server/Item/Items/")
    common = set(n for n in an if n.startswith("Common/"))
    vrd = lambda n: json.loads(AZ.read(n).decode("utf-8-sig"))
    Z, Z6 = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    rd = lambda z, n: json.loads(z.read(n).decode("utf-8-sig"))

    def gen(z, pre):
        return dict((n[len(pre):-5], n) for n in z.namelist() if n.startswith(pre) and n.endswith(".json") and "/" not in n[len(pre):])
    GE, GI, GD = gen(Z, EFF), gen(Z, INT), gen(Z, ITM)
    GR = gen(Z, ITM + "Recipes/")
    GE6, GD6 = gen(Z6, EFF), gen(Z6, ITM)
    # ---------------- R: every reference exists; no removed id anywhere
    errs = []

    def need(pool, gpool, i, where):
        if not isinstance(i, str) or (i not in pool and i not in gpool):
            errs.append("%s -> %r" % (where, i))

    def walk(node, where):
        if isinstance(node, str):
            need(VI, GI, node, where)
            return
        if isinstance(node, list):
            for x in node:
                walk(x, where)
            return
        if not isinstance(node, dict):
            return
        for k, v in node.items():
            if k in ("EffectId", "EntityEffectId"):
                need(VE, GE, v, where)
            elif k == "EntityEffectIds":
                for x in v:
                    need(VE, GE, x, where)
            elif k == "Parent":
                need(VI, GI, v, where)
            elif k in ("Interactions", "Next", "Failed"):
                walk(v, where)
    for i, n in GI.items():
        walk(rd(Z, n), "interaction " + i)
    for i, n in list(GD.items()) + list(GR.items()):
        o = rd(Z, n)
        need(VIT, GD, o.get("Parent"), "item %s Parent" % i)
        for typ, root in (o.get("Interactions") or {}).items():
            if isinstance(root, str):
                need(VR, {}, root, "item %s %s" % (i, typ))
            else:
                walk(root, "item %s %s" % (i, typ))
        for var, vv in (o.get("InteractionVars") or {}).items():
            walk(vv.get("Interactions", []), "item %s %s" % (i, var))
        for p in [o.get("Icon"), (o.get("BlockType") or {}).get("CustomModel")] + [t.get("Texture") for t in (o.get("BlockType") or {}).get("CustomModelTexture", [])]:
            if p and "Common/" + p not in common:
                errs.append("item %s file Common/%s" % (i, p))
        for inp in (o.get("Recipe") or {}).get("Input", []):
            if "ItemId" in inp:
                need(VIT, GD, inp["ItemId"], "recipe %s input" % i)
    K.check(not errs, "R: every effect / interaction / root / item / Common file the %d effects, %d checks, %d dishes, %d recipes name exists in the jar or "
            "the cached 0.7 Assets.zip: %s" % (len(GE), len(GI), len(GD), len(GR), errs[:8]))
    named = [(n, r) for n in Z.namelist() for r in REMOVED if r.encode() in Z.read(n)]
    K.check(not named, "R: no jar entry names Food_Instant_Heal_T2 / T3 / Bread: %s" % named[:5])
    K.check(all(r not in VE for r in REMOVED) and all(b in VE for b in BASES) and "HealthRegen_Buff_Raw" in VE,
            "R: premise - 0.7 Assets.zip lacks the 3 removed heals and has all 12 bases + HealthRegen_Buff_Raw")
    # ---------------- S: Grade scaling unchanged (strength x (1 + 0.32 g), Duration x 2^(g/5); instant effects keep theirs)
    bad, n_ok = [], 0
    for b in BASES:
        d0 = vrd(VE[b])
        for g in range(1, 13):
            S, D = 1.0 + 0.32 * g, 2.0 ** (g / 5.0)
            w = json.loads(json.dumps(d0))
            for k, v in w.get("StatModifiers", {}).items():
                w["StatModifiers"][k] = r4(v * S)
            for _s, lst in w.get("RawStatModifiers", {}).items():
                for m in lst:
                    m["Amount"] = r4(1.0 + (m["Amount"] - 1.0) * S) if m.get("CalculationType") == "Multiplicative" else r4(m["Amount"] * S)
            for _t, lst in w.get("DamageResistance", {}).items():
                for m in lst:
                    m["Amount"] = r4(m["Amount"] * S)
            if d0.get("Duration", 0) > 0.5:
                w["Duration"] = float("%.2f" % (d0["Duration"] * D))
            eid = "Skyy_Cook_%s_G%d" % (b, g)
            if eid not in GE or rd(Z, GE[eid]) != w:
                bad.append(eid)
            else:
                n_ok += 1
    K.check(not bad and n_ok == 144 and len(GE) == 144, "S: all 144 effects = 0.7 vanilla x (1 + 0.32 x Grade) strength, x 2^(Grade/5) Duration "
            "(12 bases x Grades 1-12, nothing else): bad %s, %d effects in the jar" % (bad[:6], len(GE)))
    # ---------------- M: the mapping; the heal numbers = 0.1.6's; the buff strengths = 0.1.6's
    mbad, heal06 = [], {}
    for dish in DISHES:
        c6 = rd(Z6, GD6["Skyy_Cook_%s_G1" % dish])["InteractionVars"]["Effect"]["Interactions"]
        old = c6[0]["EffectId"][len("Skyy_Cook_"):-len("_G1")]
        heal06[dish] = old
        for g in range(1, 13):
            gid = "Skyy_Cook_%s_G%d" % (dish, g)
            c = rd(Z, GD[gid])["InteractionVars"]["Effect"]["Interactions"]
            o6 = rd(Z6, GD6[gid])["InteractionVars"]["Effect"]["Interactions"]
            if c[0] != {"Type": "ApplyEffect", "EffectId": "Skyy_Cook_%s_G%d" % (HEAL_07[old], g)} or c[1:] != o6[1:]:
                mbad.append(gid)
            h7 = rd(Z, GE["Skyy_Cook_%s_G%d" % (HEAL_07[old], g)])["StatModifiers"]["Health"]
            h6 = rd(Z6, GE6["Skyy_Cook_%s_G%d" % (old, g)])["StatModifiers"]["Health"]
            if abs(h7 - h6) > 1e-9:
                mbad.append("%s heal %s (0.1.7) vs %s (0.1.6)" % (gid, h7, h6))
    K.check(not mbad, "M: every dish heals with HEAL_07[its 0.1.6 heal] x S(g), the rest of its eat chain = 0.1.6's, and the heal number = 0.1.6's "
            "(10 %% -> +10 health, 15 %% -> +15 at the base 100): %s" % mbad[:6])
    table = sorted(set((heal06[d], HEAL_07[heal06[d]]) for d in DISHES))
    K.eq(table, sorted(HEAL_07.items()), "M: the 0.1.6 heals in use = the 4 rows of the mapping table")
    sbad = []
    for b in BASES[3:]:
        for g in range(1, 13):
            e7, e6 = rd(Z, GE["Skyy_Cook_%s_G%d" % (b, g)]), rd(Z6, GE6["Skyy_Cook_%s_G%d" % (b, g)])
            e7.pop("Duration"), e6.pop("Duration")
            if e7 != e6:
                sbad.append("%s G%d" % (b, g))
    K.check(not sbad, "M: every buff effect = 0.1.6's except Duration (0.7 numbers): %s" % sbad[:6])
    # ---------------- I: item ids, parents, recipes, lang
    K.eq(sorted(GD), sorted(GD6), "I: the 180 graded dish ids + Recipes folder = 0.1.6's (no item id changed)")
    K.check(sorted(GR) == sorted(gen(Z6, ITM + "Recipes/")) and all(Z.read(n) == Z6.read(ITM + "Recipes/" + i + ".json") for i, n in GR.items()),
            "I: the 3 Cooking Bench recipe variants are byte-equal to 0.1.6")
    pbad = []
    for i, n in GD.items():
        o = rd(Z, n)
        if o.get("Parent") != "Template_Food" or "Recipe" in o or o.get("TranslationProperties") != rd(Z6, GD6[i]).get("TranslationProperties"):
            pbad.append(i)
    K.check(not pbad, "I: every graded dish has Parent Template_Food, no Recipe, the 0.1.6 name keys: %s" % pbad[:5])
    flat = [d for d in DISHES if vrd(VIT[d]).get("Parent") != "Template_Food"]
    fbad = []
    for d in flat:
        pv = vrd(VIT[vrd(VIT[d])["Parent"]])
        o = rd(Z, GD["Skyy_Cook_%s_G1" % d])
        miss = [k for k in pv if k not in ("Recipe", "TranslationProperties", "Parent") and k not in o]
        if miss or o.get("Consumable") != pv.get("Consumable") or o["BlockType"].get("Gathering") != pv["BlockType"].get("Gathering"):
            fbad.append((d, miss))
    K.check(len(flat) == 4 and not fbad, "I: the %d dishes 0.7 put under Food_Pie_Apple (%s) carry every key it would give them (Consumable, Gathering ...): %s"
            % (len(flat), flat, fbad))
    L7 = dict(l.split("=", 1) for l in Z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines() if "=" in l)
    L6 = dict(l.split("=", 1) for l in Z6.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines() if "=" in l)
    lbad = []
    for d in DISHES:
        pct = HEAL_07[heal06[d]] == "Food_Instant_Heal_T1"
        for g in range(1, 13):
            gid = "Skyy_Cook_%s_G%d" % (d, g)
            h = rd(Z, GE["Skyy_Cook_%s_G%d" % (HEAL_07[heal06[d]], g)])["StatModifiers"]["Health"]
            want = 'Instantly restores <color is="#ffffff">%s%s</color> health' % (("%.1f" % h).rstrip("0").rstrip("."), "%" if pct else "")
            if want not in L7.get("server.items.%s.description" % gid, "") or L7.get("server.items.%s.name" % gid) != L6.get("server.items.%s.name" % gid):
                lbad.append(gid)
    K.check(sorted(L7) == sorted(L6) and not lbad, "I: lang keys = 0.1.6's, names unchanged, the heal line says '%% health' only for percent heals: %s" % lbad[:4])
    # ---------------- F: Raw cleared by every graded HealthRegen member
    rbad = []
    for i, n in GI.items():
        if "_HealthRegen_" in i:
            o = rd(Z, n)
            ser = o if o.get("Type") == "Serial" else o.get("Next")
            if {"Type": "ClearEntityEffect", "EntityEffectId": "HealthRegen_Buff_Raw"} not in ser["Interactions"]:
                rbad.append(i)
    K.check(not rbad and sum(1 for i in GI if "_HealthRegen_" in i) == 36, "F: all 36 graded HealthRegen checks clear HealthRegen_Buff_Raw: %s" % rbad[:4])
    K.notes.append("FX: mapping %s; flattened %s" % (table, flat))
    K.save()


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    st = SK.Stage()
    ua, ub = "00000000-0000-0000-0000-0000000000a1", "00000000-0000-0000-0000-0000000000b2"
    pa = st.player("Alice", ua)
    st.player("Bob", ub)
    st.universe()
    J = lambda n: JClass(PKG + n)
    Snd, Rows, Fn, CP = J("CookSnd"), J("CfgRows"), J("CfgFn"), J("CfgPub")
    home = os.path.join(scratch, "snd", "mods", "Skyy_SkyyCooking")
    G.unit(K, st, Snd, Rows, Fn, pa, ua, "SkyyCooking", SOUNDS, home)
    b = G.bridge(st.J)
    # ---- THE CALL SITE's call: CookSnd.meal(pr, this.gave) in CookXpTask.run
    Snd.LAST.clear()
    st.clear()
    K.check(bool(Snd.meal(pa, True)) and st.sounds() == [("Alice", "SFX_Furnace_Bench_Processing_Complete", "UI", "2d")], "SITE a graded dish: the cook only, UI 2D")
    Snd.LAST.clear()
    st.clear()
    K.check(not bool(Snd.meal(pa, False)) and st.sounds() == [], "SITE gave false (ingredients / plain food): silent")
    n = sum(1 for _ in range(8) if bool(Snd.meal(pa, True)))
    K.check(n == 1 and len(st.sounds()) == 1, "SITE a batch (8 dishes in one go) = ONE sting")
    Snd.LAST.clear()
    st.clear()
    b.put("settings:sounds:" + ua, JClass("java.lang.Boolean").FALSE)
    K.check(not bool(Snd.meal(pa, True)) and st.sounds() == [], "SITE the cook muted every sound in /settings: silent")
    b.remove("settings:sounds:" + ua)
    Snd.S_MEAL = False
    K.check(not bool(Snd.meal(pa, True)) and st.sounds() == [], "SITE the Meal done row off: silent")
    Snd.S_MEAL = True
    # ---- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["CookSnd.playTo"], "STATIC only CookSnd.playTo calls SoundUtil")
    K.check(PKG + "CookSnd.meal" in g.get("CookXpTask.run", set()) and PKG + "CookSnd.load" in g.get("SkyyCookingPlugin.setup", set())
            and sorted(m for m, cs in g.items() if PKG + "CookSnd.meal" in cs) == ["CookXpTask.run"],
            "STATIC CookXpTask.run (only) plays the sting; setup loads sounds.properties")
    gen = open(os.path.join(HERE, "build_skyycooking_%s.py" % VERSION), encoding="utf8").read()
    K.check(gen.index("if (!this.key.equals(@PKG@.Cook.pkey(this.u))) return;") < gen.index("@PKG@.CookSnd.meal(pr, this.gave);")
            and gen.index("@PKG@.CookSnd.load(getDataDirectory()") < gen.index("@PKG@.CfgPub.start(getDataDirectory()"),
            "STATIC the sting comes after the profile check; sounds.properties read before the kit starts")
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyyCooking", SOUNDS)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Snd, CP = J("CookCfg"), J("CookSnd"), J("CfgPub")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    snaps, migs = [], []
    import time
    for start in (1, 2):
        Cfg.FILE = Paths.get(os.path.join(home, "cooking.properties"))
        migs.append([str(J(m).migrate()) for m in ("CookMig", "CookXpMig", "CookTblMig", "CookIngMig")])
        Cfg.load()
        t = str(Snd.load(Paths.get(home)))
        CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCooking"))
        K.check(t == "sounds on (1 of 1)" and int(Snd.WARNS.get()) == 0, "DS%d: the live copy reads the sound defaults: %s" % (start, t))
        CP.flush()
        time.sleep(0.6)
        CP.shutdown()
        snaps.append(HK.tree_hash(home))
        time.sleep(1.1)
    K.check(migs == [["", "", "", ""], ["", "", "", ""]], "DS: no one-time update runs on the live (0.1.6) cooking.properties: %s" % migs)
    G.live_twice(K, h0, snaps[0], snaps[1])
    K.check(open(os.path.join(home, "sounds.properties"), encoding="latin-1").read() == G.file_text("SkyyCooking", SOUNDS), "DS: sounds.properties = the default text")
    K.save()


# ---- C: the builtin compare demands only manifest.json among the non-class entries; 0.1.7 also regenerates the assets (checked in FX)
_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added):
    orig_eq = HK.Child.eq

    def eq(self, got, want, what):
        if what != "C: non-class entries changed":
            return orig_eq(self, got, want, what)
        za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
        ok = all(n == "manifest.json" or n == "Server/Languages/en-US/server.lang" or
                 (n.startswith((EFF, INT, ITM)) and not n.startswith(ITM + "Recipes/")) for n in got)
        gone = sorted(n for n in za.namelist() if n not in zb.namelist())
        new = sorted(n for n in zb.namelist() if n not in za.namelist() and not n.endswith(".class"))
        ok = ok and gone == sorted(EFF + "Skyy_Cook_%s_G%d.json" % (r, g) for r in REMOVED for g in range(1, 13)) \
            and new == sorted(EFF + "Skyy_Cook_%s_G%d.json" % (r, g) for r in ("Food_Health_Restore_Small", "Food_Health_Restore_Medium") for g in range(1, 13))
        return self.check(ok and "manifest.json" in got, "C: non-class entries changed = manifest + generated effects / checks / dishes / lang only "
                          "(36 removed-heal effects gone, 24 Restore effects new, recipes untouched): %d changed, %d gone, %d new" % (len(got), len(gone), len(new)))
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added)
    finally:
        HK.Child.eq = orig_eq


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("assets", run_assets), ("snd", run_snd), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCooking"))
