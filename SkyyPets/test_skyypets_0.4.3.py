"""Harness for SkyyPets 0.4.3 (egg cost text "(need N)" + the 8 roster kinds; tools/pets_0_4_3_patch.py).
Build first: python tools/pets_0_4_3_patch.py; python SkyyPets/build_skyypets_0.4.3.py

    python SkyyPets/test_skyypets_0.4.3.py [--dir <folder inside tools/dev/scratch/>]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.2 -> 0.4.3 (exactly the planned members),
              engine audit
  NEW         EXECUTED in a plain -Xverify:all JVM (0.4.1's fake inventory + fake Void): the cost line (need N) - nothing / inventory /
              inventory + Void / enough; the Craft refusal "You need N more ..."; the 39 kinds (the 8 new ones: skill, rarity, stats,
              looks, roles, the Bison baby); an OLD config.properties without their kind lines = the built-in lines (PetKind.ADDED);
              the egg order defaults + an old order line = the same places by the start-rarity rule; a Farming egg can hatch a Mosshorn
  OLD         the 0.4.2 harness's HATCH (= 0.4.1's) + PAGES phases EXECUTED on this jar (with the 0.4.3 egg lists); the only differences
              are the listed EXPECTED_OLD ones (the old cost / Missing / refusal wording)
  LIVE        0.4.1's LIVE phase: start twice on a scratch COPY of the live Skyy_SkyyPets folder - nothing written, no cut-off move
Exit code 1 on any failure.
"""
import os, sys, re, json, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyeggs as EG

_cmp0 = HK.run_compare
_s42 = importlib.util.spec_from_file_location("test_skyypets_0_4_2", os.path.join(HERE, "test_skyypets_0.4.2.py"))
T42 = importlib.util.module_from_spec(_s42)
_s42.loader.exec_module(T42)
T41 = T42.T41
HK.run_compare = _cmp0

VERSION = "0.4.3"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pets043", "test")))

NEW_KINDS = {"Mosshorn": ("Farming", 3), "Bison": ("Farming", 2), "CrystalGolem": ("Mining", 4), "Molerat": ("Mining", 2),
             "Moose": ("Foraging", 3), "Owl": ("Foraging", 2), "Antelope": ("Exploration", 2), "Deer": ("Exploration", 2)}
ORDER_043 = {"Mining": ["CrystalGolem", "Goat", "Warthog", "Molerat", "Meerkat", "Mouse"],
             "Farming": ["Mosshorn", "Bison", "Rabbit", "Bunny", "Chicken", "Corgi", "Frog"],
             "Foraging": ["Bear", "Moose", "Turkey", "Owl", "Cat", "Squirrel"],
             "Exploration": ["Camel", "Horse", "Antelope", "Deer", "Gecko", "Rat"]}
ORDER_042 = dict((c, list(EG.ORDER[c])) for c in ORDER_043)
# the old harnesses read tools/skyyeggs.py ORDER: give them the 0.4.3 lists (the build script extends it the same way)
EG.ORDER = dict(EG.ORDER)
EG.ORDER.update(ORDER_043)

EXPECT = {
    "PetHatchery": ["~m costText", "~m craft"],
    "PetsPage": ["~m build"],
    "PetKind": ["~<clinit>"], "PetLook": ["~<clinit>"],
    "PetsCfg": ["~<clinit>", "~m applyAll", "~m applyScalars", "~m applyTables", "~m seed"],     # the egg order defaults are inlined
    "PetEggDefs": ["~<clinit>"],          # the default egg lists
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyPetsPlugin": ["~m setup"],
}
ADDED = []
_NEW_COST = "0.4.3: the cost line says (need N) instead of the have counts (Skyy 2026-10-16)"
EXPECTED_OLD = {
    "ROWS the cost line names every input": _NEW_COST,
    "CRAFT not enough = refused": "0.4.3: the refusal says 'You need N more ...'",
    "EGGS nothing craftable = no Craft bound": "0.4.3: no Missing tag (the need text says it)",
    "TAB1 nothing craftable = no Craft bound": "0.4.3: no Missing tag (the need text says it)",
}


def run_new(out, jar, scratch, _home):
    from jpype import JClass, JProxy
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Log, Egg, Eng, Hy, Kind, Look = (P_("PetsCfg"), P_("PetStore"), P_("PetsLog"), P_("PetEgg"), P_("PetsEng"), P_("PetHatchery"),
                                                 P_("PetKind"), P_("PetLook"))
    Paths, UUID, Long, Random = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.util.Random")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "new-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    home = os.path.join(mods, "Skyy_SkyyPets")
    Store.ROOT = Paths.get(home)
    Store.DIR = Store.ROOT.resolve("pets")
    names = {}
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(names)), "byName": lambda n: None,
                                            "nameOf": lambda u: names.get(str(u), str(u)), "tell": lambda u, t, c: None})
    BR = Log.bridge()
    V = T41.Void()
    for k_, f_ in (("count", V.count), ("take", V.take), ("put", V.put), ("commit", V.commit)):
        BR.put("sacks:fn:" + k_, JProxy("java.util.function.Function", dict={"apply": (lambda f: (lambda a: Long(f(list(a)))))(f_)}))
    u = UUID.fromString("00000000-0000-0000-0000-000000000743")
    names[str(u)] = "Keeper"
    key = str(Store.pkey(u))
    Store.KEYOF.put(u, key)
    Store.get(key).set("starter", "1")
    EC = "Skyy_PetEgg_Combat_Common"          # 1 Food_Egg + 128 Bone Fragments + 16 Light Leather
    pi = T41.proxy_inv
    # ---------------------------------------------------------------- COST: (need N)
    c0 = str(Hy.costText(None, pi(T41.Inv()), EC))
    K.eq(c0, "1 Egg (need 1) + 128 Bone Fragments (need 128) + 16 Light Leather (need 16)", "COST nothing held: every input says how many more")
    ids = [str(x) for x in Hy.inIds(Hy.craftIndex(EC))]
    bone, leather = ids[1], ids[2]
    V.live = {bone: 22}
    c1 = str(Hy.costText(u, pi(T41.Inv({"Food_Egg": 1})), EC))
    K.eq(c1, "1 Egg + 128 Bone Fragments (need 106) + 16 Light Leather (need 16)", "COST Skyy's example: 22 in the Void -> (need 106); the egg you have says nothing extra")
    V.live = {bone: 100}
    c2 = str(Hy.costText(u, pi(T41.Inv({"Food_Egg": 3, bone: 28, leather: 20})), EC))
    K.eq(c2, "1 Egg + 128 Bone Fragments + 16 Light Leather", "COST inventory + Void together = enough: no need text at all")
    K.check("Void" not in c1 + c2 and "(0" not in c0 + c1, "COST no '(0 + 22 Void)' form left")
    # ---------------------------------------------------------------- CRAFT refusal wording
    V.live = {bone: 22}
    Hy.CLICK.clear()
    inv = T41.Inv({"Food_Egg": 1, leather: 16})
    m = str(Hy.craft(u, pi(inv), EC, "harness"))
    K.check(m == "-You need 106 more Bone Fragments." and inv.live == {"Food_Egg": 1, leather: 16} and V.live[bone] == 22,
            "CRAFT short = refused with the same (need N) number, nothing moved: %s" % m)
    # ---------------------------------------------------------------- KINDS: the 8 roster adds
    ks = list(Cfg.KINDS)
    byid = dict((str(k.id), k) for k in ks)
    K.check(len(ks) == 39 and all(n in byid for n in NEW_KINDS), "KINDS 39 kinds, the 8 roster adds among them (%d)" % len(ks))
    K.check(all(str(byid[n].skill) == s_ and int(byid[n].rarity) == r_ for n, (s_, r_) in NEW_KINDS.items() if n in byid),
            "KINDS each new kind's skill + start rarity (spec 2.3)")
    dt = str(Cfg.DEFAULT_TEXT)
    K.check("kind.Mosshorn=Farming/Rare/fortune.farming:16.5,wisdom.farming:8.5\n" in dt and "kind.CrystalGolem=Mining/Epic/" in dt
            and "look.Owl=Owl_Brown/1.0/fly\n" in dt and "role.Deer=pet\n" in dt and "baby.Bison=Bison_Calf/" in dt,
            "KINDS the default config text holds their kind / look / role / baby lines")
    ld = [str(x) for x in Look.LOOK_DEF]
    K.check("CrystalGolem=Golem_Crystal_Earth/0.45/walk" in ld and "Moose=Moose_Bull/0.5/walk" in ld, "KINDS built-in looks (vanilla models by id)")
    K.check(sorted(str(x).split("=")[0] for x in Kind.ADDED) == sorted(["SkeletonKnight"] + list(NEW_KINDS)), "KINDS PetKind.ADDED = SkeletonKnight + the 8")
    K.eq(str(Kind.display("CrystalGolem")), "Crystal Golem", "KINDS the display name")
    # ---------------------------------------------------------------- ORDER
    for c, v in ORDER_043.items():
        K.eq([str(x) for x in Egg.order(c)], v, "ORDER default %s list (the 0.4.3 places)" % c)
        K.check(("pets.egg.order.%s=%s\n" % (c.lower(), ",".join(v))) in dt, "ORDER the default %s row" % c)
    # ---------------------------------------------------------------- an OLD config (written by 0.4.2): no new kind lines, the old order rows
    old = os.path.join(scratch, "old-mods")
    od = os.path.join(old, "Skyy_SkyyPets")
    os.makedirs(od, exist_ok=True)
    lines = []
    for l in dt.split("\n"):
        k_ = l.split("=", 1)[0]
        if k_ in ["kind." + n for n in NEW_KINDS] + ["look." + n for n in NEW_KINDS] + ["role." + n for n in NEW_KINDS] + ["baby.Bison"]:
            continue
        for c, v in ORDER_042.items():
            if k_ == "pets.egg.order." + c.lower():
                l = "%s=%s" % (k_, ",".join(v))
        lines.append(l)
    open(os.path.join(od, "config.properties"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    Cfg.load(Paths.get(old))
    ks2 = dict((str(k.id), k) for k in Cfg.KINDS)
    K.check(len(ks2) == 39 and str(ks2.get("Mosshorn").stats if ks2.get("Mosshorn") is not None else "") != "",
            "OLDCFG an old config.properties: the 8 new kinds come from their built-in lines (%d kinds)" % len(ks2))
    K.check(any("Mosshorn" in str(x) and "no line in config.properties" in str(x) for x in Log.LINES), "OLDCFG the built-in line use is logged")
    for c, v in ORDER_043.items():
        K.eq([str(x) for x in Egg.order(c)], v, "OLDCFG an old %s order row: the new kinds land on the same places (start-rarity rule)" % c)
    # ---------------------------------------------------------------- a Farming egg can hatch the new top pet
    Egg.RNG = Random(43)
    seen = set()
    for _ in range(4000):
        k = Egg.rollKind("Farming", 4) if hasattr(Egg, "rollKind") else None
        if k is None:
            break
        seen.add(str(k))
    if seen:
        K.check("Mosshorn" in seen and "Bison" in seen, "ROLL 4000 Epic Farming rolls include Mosshorn + Bison: %s" % sorted(seen))
    else:
        w = list(Egg.weights(len(ORDER_043["Farming"]), 2.0, False))
        K.check(len(w) == 7 and 0 < w[0] < w[-1], "ROLL the Farming pool has 7 weights, the best (Mosshorn) the rarest: %s" % [round(x, 3) for x in w])
    K.save()


def run_old(out, jar, scratch, _home):
    K = HK.Child(out)
    for ph in ("old_hatch", "old_pages"):
        d = os.path.join(scratch, ph)
        os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
        o = os.path.join(d, "out.json")
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(d, "tmp")
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", ph, "--out", o, "--dir", d, "--jar", jar], env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        open(os.path.join(scratch, "%s.log" % ph), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
        if not os.path.isfile(o):
            K.check(False, "%s: the phase wrote no result (exit %s): %s" % (ph, p.returncode, (p.stdout + p.stderr)[-800:]))
            continue
        d_ = json.load(open(o))
        unexp = [f for f in d_["fails"] if not any(f.startswith(e) for e in EXPECTED_OLD)]
        K.check(not unexp, "%s on the 0.4.3 jar: %d ok, unexpected fails %s" % (ph, d_["ok"], unexp[:4]))
        for e in EXPECTED_OLD:
            if any(f.startswith(e) for f in d_["fails"]):
                K.notes.append("expected on 0.4.3: %s -> %s" % (e[:90], EXPECTED_OLD[e]))
        print("%s: %d ok, %d fail(s), %d of them expected" % (ph, d_["ok"], len(d_["fails"]), len(d_["fails"]) - len(unexp)))
    K.save()


def run_old_hatch(out, jar, scratch, home):
    T41.run_hatch(out, jar, scratch, home)


def run_old_pages(out, jar, scratch, home):
    T42.run_pages(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    T41.run_live(out, jar, scratch, home)


# ---- C: the non-class entries that may change: manifest + the lang file + the 8 new portraits (item JSON + icon png); none removed
def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    import zipfile
    orig_eq = HK.Child.eq

    def eq(self, got, want, what):
        if what != "C: non-class entries changed":
            return orig_eq(self, got, want, what)
        za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
        gone = sorted(n for n in za.namelist() if n not in zb.namelist())
        new = sorted(n for n in zb.namelist() if n not in za.namelist())
        por = sorted(["Common/Icons/ItemsGenerated/Skyy_PetIcon_%s.png" % k for k in NEW_KINDS] + ["Server/Item/Items/SkyyPets/Icons/Skyy_PetIcon_%s.json" % k for k in NEW_KINDS])
        return self.check(not gone and new == por and sorted(got) == sorted(por + ["manifest.json", "Server/Languages/en-US/server.lang"]),
                          "C: non-class entries changed = manifest + the lang file + the 8 new portraits (16 files, all new); none removed (%d)" % len(got))
    HK.Child.eq = eq
    try:
        _cmp0(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = orig_eq


HK.run_compare = _compare

if __name__ == "__main__":
    if "--phase" in sys.argv and HK.arg("--phase") in ("old_hatch", "old_pages"):
        # a child of run_old: one old phase, its own result file
        HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
               phases=[("old_hatch", run_old_hatch), ("old_pages", run_old_pages)], script=__file__)
    else:
        phases = [("new", run_new), ("old", run_old), ("live", run_live)]
        HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
               phases=phases, script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
