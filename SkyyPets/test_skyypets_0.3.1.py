"""Harness for SkyyPets 0.3.1 (every rarity boosted the same way: the Pet kinds values x (0.2.x factor / 0.3) / 0.3.0 factor of the kind's
rarity + the one-time kind-value update PetsCfgMig2; tools/pets_0_3_1_patch.py).
Build first: python tools/pets_0_3_1_patch.py; python SkyyPets/build_skyypets_0.3.1.py

    python SkyyPets/test_skyypets_0.3.1.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--no-r030]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.3.0 -> 0.3.1 (exactly the planned members;
              + PetsCfgMig2), engine-access audit
  SYS         CFG   a fresh config: every kind line = the new value (Common kinds unchanged), caps / rarity / curve / rebirth reset unchanged
              BUF   EXECUTED PetBuff.compute for EVERY kind x EVERY rarity x Lv 1 / 20 / 50 / 100 = value x rarity x L / 100 (caps
                    applied); at the kind's own rarity ~x3.33 of 0.2.7 (3.15 - 3.5) at every level, as the Common kinds in 0.3.0
              CMIG2 the one-time update on synthetic files: a 0.3.0 default file (exactly the 19 non-Common kind lines change; history
                    copy byte-equal; 19 change-log lines pets.kinds[<Kind>] with | columns; marker; second run nothing); hand edits kept
                    + noted; number-equal / spaced / reordered default lines updated (spaces kept); a continued line kept; CRLF kept;
                    no file = marker only; a 0.3.1 file = nothing to change; blocked config-history = nothing rewritten, no marker;
                    the LAST entry decides; sameAfter refuses any other change; CHAIN 0.2.7 -> 0.3.1 on one start (PetsCfgMig then
                    PetsCfgMig2: two History copies, original bytes first, 8 + 19 log lines, both markers); the updated file loads
                    the new values; UNDO = the kit's own tset with the logged old columns puts the 0.3.0 line back
  CP          pure Python: the changed classes' string constants differ ONLY in the version text and the 19 kind lines
  LIVE        start TWICE on a scratch COPY of the live Skyy_SkyyPets folder (both updates; only the old-default lines; start 2 writes
              NOTHING)
  R030        the 0.3.0 harness's own SYS / HUB / SND phases (test_skyypets_0.3.0.py --phase ...) EXECUTED on the 0.3.1 jar: the whole
              pet system (starter, buffs, XP, rebirth, fusing + fuzz, level update, 0.3.0 config update, page, hub, sounds) unchanged
Exit code 1 on any failure.
"""
import os, sys, subprocess, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.1"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.3.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pets031", "test")))

RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
OLD_F = [0.3, 0.45, 0.6, 0.8, 1.0, 1.25]       # 0.2.x
NEW_F = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]         # 0.3.0 (unchanged in 0.3.1)
# kind -> (skill, rarity, 0.3.0 stats (= 0.2.x), 0.3.1 stats) - written out by hand, so a wrong formula in the build cannot pass
KV = {
    "Rabbit": ("Farming", "Common", "fortune.farming:10", "fortune.farming:10"),
    "Chicken": ("Farming", "Common", "fortune.farming:7,stamina:10", "fortune.farming:7,stamina:10"),
    "Goat": ("Mining", "Uncommon", "fortune.mining:10,swing.mining:5", "fortune.mining:13.5,swing.mining:7"),
    "Warthog": ("Mining", "Uncommon", "fortune.mining:7,def:15", "fortune.mining:9.5,def:20.5"),
    "Bear": ("Foraging", "Rare", "fortune.foraging:10,swing.foraging:5,str:5", "fortune.foraging:16.5,swing.foraging:8.5,str:8.5"),
    "Turkey": ("Foraging", "Uncommon", "fortune.foraging:7", "fortune.foraging:9.5"),
    "Wolf": ("Combat", "Rare", "str:20,cd:15,cc:5", "str:33.5,cd:25,cc:8.5"),
    "Boar": ("Combat", "Uncommon", "health:60,def:20", "health:82,def:27.5"),
    "Hawk": ("Combat", "Epic", "cc:20,cd:25", "cc:41,cd:51.5"),
    "Ram": ("Combat", "Epic", "def:50,health:80", "def:102.5,health:164"),
    "Skrill": ("Combat", "Epic", "mp:40,mana:40", "mp:82,mana:82"),
    "Tusker": ("Combat", "Rare", "str:30", "str:50"),
    "Mouflon": ("Combat", "Epic", "mp:30,health:50", "mp:61.5,health:102.5"),
    "Horse": ("Exploration", "Uncommon", "speed:5,stamina:20", "speed:7,stamina:27.5"),
    "Camel": ("Exploration", "Rare", "stamina:30", "stamina:50"),
    "Fox": ("Combat", "Uncommon", "str:20,cd:15,cc:5", "str:27.5,cd:20.5,cc:7"),
    "Rat": ("Exploration", "Common", "speed:5,stamina:20", "speed:5,stamina:20"),
    "Skeleton": ("Combat", "Rare", "cc:20,cd:25", "cc:33.5,cd:41.5"),
    "SkeletonKnight": ("Combat", "Rare", "str:20,cd:15,cc:5", "str:33.5,cd:25,cc:8.5"),
    "VoidEye": ("Combat", "Epic", "mp:40,mana:40", "mp:82,mana:82"),
    "VoidCrawler": ("Combat", "Rare", "health:60,def:20", "health:100,def:33.5"),
    "VoidLarva": ("Combat", "Uncommon", "mp:40,mana:40", "mp:54.5,mana:54.5"),
    "Cat": ("Foraging", "Common", "fortune.foraging:7", "fortune.foraging:7"),
    "Dog": ("Combat", "Common", "str:20,cd:15,cc:5", "str:20,cd:15,cc:5"),
    "Corgi": ("Farming", "Common", "fortune.farming:7", "fortune.farming:7"),
    "Frog": ("Farming", "Common", "fortune.farming:7", "fortune.farming:7"),
    "Mouse": ("Mining", "Common", "fortune.mining:7", "fortune.mining:7"),
    "Squirrel": ("Foraging", "Common", "fortune.foraging:7", "fortune.foraging:7"),
    "Bunny": ("Farming", "Common", "fortune.farming:10", "fortune.farming:10"),
    "Meerkat": ("Mining", "Common", "fortune.mining:7", "fortune.mining:7"),
    "Gecko": ("Exploration", "Common", "speed:5,stamina:20", "speed:5,stamina:20"),
}
CHANGED = sorted(k for k, v in KV.items() if v[2] != v[3])
COMPAT8 = [("pets.rarity.common", "1", "0.3"), ("pets.rarity.uncommon", "1.1", "0.45"), ("pets.rarity.rare", "1.2", "0.6"),
           ("pets.rarity.epic", "1.3", "0.8"), ("pets.rarity.legendary", "1.4", "1"), ("pets.rarity.mythic", "1.5", "1.25"),
           ("pets.curve.linear", "120", "60"), ("pets.curve.cubic", "0.08", "0.04")]


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                v = l.split("=", 1)[1].strip()
                return v[1:v.index('"', 1)] if v.startswith('"') else v.split("#")[0].strip()
    except Exception:
        pass
    return "NewBetaTest"


LIVE = os.path.join(B.USERDATA, "Saves", deploy_world(), "mods", "Skyy_SkyyPets")
# class compare 0.3.0 -> 0.3.1: exactly these members differ (+ PetsCfgMig2)
EXPECT = {
    "PetKind": ["~<clinit>"],                 # ADDED (SkeletonKnight's built-in line) carries the new values
    "SkyyPetsPlugin": ["~m setup"],           # + PetsCfgMig2.run after PetsCfgMig.run
    "CfgRows": ["~<clinit>", "~m header"],    # the kit's default config text (the new kind lines) + the "# SkyyPets 0.3.1" header / version
    "PetsCfg": ["~m applyAll", "~m seed"],    # the "# SkyyPets 0.3.1" header line of a seeded file
    "CfgFn": ["~m opExport"],                 # the export code's _ver=0.3.1
}
ADDED = ["PetsCfgMig2"]


def stats(s):
    return [(p.split(":")[0], float(p.split(":")[1])) for p in s.split(",")]


def kind_line(k, which):
    v = KV[k]
    return "%s/%s/%s" % (v[0], v[1], v[2 if which == "old" else 3])


def tree(d):
    out = {}
    for r_, _ds, fs in os.walk(d):
        for f_ in fs:
            p = os.path.join(r_, f_)
            out[os.path.relpath(p, d)] = open(p, "rb").read()
    return out


def props(path):
    out = {}
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="latin-1").read().splitlines():
        if not l or l.startswith("#") or "=" not in l:
            continue
        k, v = l.split("=", 1)
        out[k.strip()] = v.strip()
    return out


# ======================================================================================================== SYS
def run_sys(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Buff, Kind, Mig, Mig2, Rows, Fn = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetBuff"),
        P_("PetKind"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("CfgRows"), P_("CfgFn"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "sys-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    home = os.path.join(mods, "Skyy_SkyyPets")
    Store.ROOT = Paths.get(home)
    Store.DIR = Store.ROOT.resolve("pets")
    # ---------------------------------------------------------------- CFG
    dt = str(Cfg.DEFAULT_TEXT)
    dp = dict((l.split("=", 1)[0], l.split("=", 1)[1]) for l in dt.split("\n") if l.startswith("kind."))
    K.check(dp == dict(("kind." + k, kind_line(k, "new")) for k in KV), "CFG the default config text: every kind line = the 0.3.1 value: %s"
            % [(k, dp.get(k)) for k in sorted(dp) if dp.get(k) != kind_line(k[5:], "new")][:4])
    fp = props(os.path.join(home, "config.properties"))
    K.check(all(fp.get("kind." + k) == kind_line(k, "new") for k in KV), "CFG a fresh config.properties holds the new kind lines")
    bad = []
    for k in KV:
        pk = Cfg.kind(k)
        got = sorted(zip([str(x) for x in pk.keys], [float(x) for x in pk.vals])) if pk is not None else None
        if got != sorted(stats(KV[k][3])) or str(pk.skill) != KV[k][0] or int(pk.rarity) != RARITIES.index(KV[k][1]) + 1:
            bad.append((k, got))
    K.check(not bad, "CFG every kind loads its 0.3.1 values (skill + rarity unchanged): %s" % bad[:4])
    K.check(all(KV[k][2] == KV[k][3] for k in KV if KV[k][1] == "Common") and len(CHANGED) == 19, "CFG the 12 Common kinds keep their values, 19 kinds change")
    K.check(str(Kind.lookup(Kind.ADDED, "SkeletonKnight", "")) == kind_line("SkeletonKnight", "new"), "CFG the built-in SkeletonKnight line (no line in an old file) = the new value")
    K.check([abs(float(getattr(Cfg, "F%d" % (i + 1))) - NEW_F[i]) < 1e-9 for i in range(6)] == [True] * 6 and abs(float(Cfg.FORT_CAP) - 10) < 1e-9
            and abs(float(Cfg.SWING_CAP) - 5) < 1e-9 and str(Cfg.REB_RESET) == "one" and bool(Cfg.CAP_SCALE) and abs(float(Cfg.CURVE_LIN) - 120) < 1e-9
            and int(Cfg.LVL_CAP) == 50 and abs(float(Cfg.REB_STAT) - 5) < 1e-9, "CFG unchanged: rarity x1 ... x1.5, Fortune cap 10, swing cap 5, pet rebirth = back to Lv 1, curve, cap 50")
    # ---------------------------------------------------------------- BUF: every kind x rarity x level, executed
    u = UUID.fromString("00000000-0000-0000-0000-000000000311")
    key = str(Store.pkey(u))
    r = Store.get(key)
    pid = str(Ops.createR(r, None, "Rabbit", 1, 1, 0, 0, "test", "harness", False))
    K.check(not pid.startswith("-") and str(r.active(1)) == pid, "BUF a test pet in the pet slot: %s" % pid)
    SK = [str(x) for x in Kind.STAT_KEYS]
    probs, ratios = [], []
    for k in sorted(KV):
        for ri in range(6):
            for L in (1, 20, 50, 100):
                r.set("pet.%s.kind" % pid, k)
                r.set("pet.%s.rarity" % pid, str(ri + 1))
                r.set("pet.%s.level" % pid, str(L))
                t = [float(x) for x in Buff.compute(r, "w")]
                cm = NEW_F[ri]
                for sk, v in stats(KV[k][3]):
                    want = v * NEW_F[ri] * L / 100.0
                    if sk.startswith("fortune."):
                        want = min(want, 10.0 * cm)
                    if sk.startswith("swing."):
                        want = min(want, 5.0 * cm)
                    got = t[SK.index(sk)]
                    if abs(got - want) > 1e-9:
                        probs.append((k, RARITIES[ri], L, sk, got, want))
                    if RARITIES[ri] == KV[k][1] and L <= 50:
                        old = dict(stats(KV[k][2]))[sk] * OLD_F[ri] * L / 100.0
                        ratios.append((got / old, k, sk, L))
    K.check(not probs, "BUF 31 kinds x 6 rarities x Lv 1/20/50/100 = value x rarity x L / 100 (Fortune / swing caps x rarity): %s" % probs[:4])
    lo, hi = min(ratios), max(ratios)
    K.check(3.15 < lo[0] and hi[0] < 3.5, "BUF every kind AT ITS RARITY, Lv 1 / 20 / 50: x%.3f (%s %s Lv %d) ... x%.3f (%s %s Lv %d) of 0.2.7 (target x3.33 = the Common kinds)"
            % (lo + hi))
    # Skyy's Lv 20 Rabbit stays 2; a Rare Lv 20 Wolf 2.4 str (0.2.7) -> 8.04; the caps still bind above Lv 50
    for kk, ri, L, sk, want in (("Rabbit", 0, 20, "fortune.farming", 2.0), ("Wolf", 2, 20, "str", 8.04), ("Hawk", 3, 20, "cc", 10.66),
                                ("Goat", 1, 20, "fortune.mining", 2.97), ("Bear", 2, 100, "fortune.foraging", 12.0), ("Bear", 2, 100, "swing.foraging", 6.0),
                                ("Bear", 2, 50, "fortune.foraging", 9.9)):
        r.set("pet.%s.kind" % pid, kk); r.set("pet.%s.rarity" % pid, str(ri + 1)); r.set("pet.%s.level" % pid, str(L))
        got = float(list(Buff.compute(r, "w"))[SK.index(sk)])
        K.check(abs(got - want) < 1e-9, "BUF %s %s Lv %d %s = %s (got %s)" % (RARITIES[ri], kk, L, sk, want, got))
    r.set("pet.%s.kind" % pid, "Bear"); r.set("pet.%s.rarity" % pid, "3"); r.set("pet.%s.level" % pid, "100"); r.set("pet.%s.rebirth" % pid, "5")
    got = float(list(Buff.compute(r, "w"))[SK.index("fortune.foraging")])
    K.check(abs(got - 15.0) < 1e-9, "BUF the Fortune cap still binds: a Rare R5 Lv 100 Bear = 10 x 1.2 x 1.25 = 15 (got %s)" % got)
    Cfg.CAP_SCALE = False
    got = float(list(Buff.compute(r, "w"))[SK.index("fortune.foraging")])
    Cfg.CAP_SCALE = True
    K.check(abs(got - 10.0) < 1e-9, "BUF ... cap scaling off = the fixed 10 (got %s)" % got)
    r.set("pet.%s.rebirth" % pid, None)

    # ---------------------------------------------------------------- CMIG2: the one-time kind-value update
    D30 = dt
    for k in CHANGED:
        a = "\nkind.%s=%s\n" % (k, kind_line(k, "new"))
        assert D30.count(a) == 1, k
        D30 = D30.replace(a, "\nkind.%s=%s\n" % (k, kind_line(k, "old")))

    def cm(name, text, crlf=False):
        h = os.path.join(scratch, "cmig2", name, "Skyy_SkyyPets")
        os.makedirs(h, exist_ok=True)
        if text is not None:
            open(os.path.join(h, "config.properties"), "wb").write((text.replace("\n", "\r\n") if crlf else text).encode("latin-1"))
        return h
    hm = cm("default", D30)
    oldb = open(os.path.join(hm, "config.properties"), "rb").read()
    msg = str(Mig2.run(Paths.get(hm)))
    newb = open(os.path.join(hm, "config.properties"), "rb").read()
    ol, nl_ = oldb.decode("latin-1").split("\n"), newb.decode("latin-1").split("\n")
    diff = [(a, b) for a, b in zip(ol, nl_) if a != b]
    K.check(len(ol) == len(nl_) and sorted(diff) == sorted([("kind.%s=%s" % (k, kind_line(k, "old")), "kind.%s=%s" % (k, kind_line(k, "new"))) for k in CHANGED]),
            "CMIG2 a 0.3.0 default file: exactly the 19 non-Common kind lines changed: %s" % diff[:3])
    hst = [f_ for f_ in os.listdir(os.path.join(hm, "config-history")) if f_.endswith(".bak")]
    K.check(len(hst) == 1 and open(os.path.join(hm, "config-history", hst[0]), "rb").read() == oldb, "CMIG2 config-history holds the old bytes first")
    idx = open(os.path.join(hm, "config-history", "index.log"), encoding="utf-8").read()
    K.check("SkyWynn update 0.3.1" in idx and "before the 0.3.1 pet kind values update" in idx, "CMIG2 the History index names the update")
    chl = open(os.path.join(hm, "config-changes.log"), encoding="utf-8").read().splitlines()
    wantl = sorted("\tSkyWynn update 0.3.1\t-\tupdate\tpets.kinds[%s]\t%s\t%s\tok" % (k, kind_line(k, "old").replace("/", "|"), kind_line(k, "new").replace("/", "|")) for k in CHANGED)
    K.check(sorted(l[l.index("\t"):] for l in chl) == wantl, "CMIG2 19 config-changes.log lines pets.kinds[<Kind>] old|cols new|cols ok (Server Setup -> Changes -> Undo): %s" % chl[:2])
    K.check(os.path.exists(os.path.join(hm, "migrations", "pets-031.done")) and "19 kinds" in msg and "Goat fortune.mining:10,swing.mining:5 -> fortune.mining:13.5,swing.mining:7" in msg,
            "CMIG2 the marker + the log message: %s" % msg[:300])
    K.check(str(Mig2.run(Paths.get(hm))) == "" and open(os.path.join(hm, "config.properties"), "rb").read() == newb, "CMIG2 a second start changes nothing")
    # the updated file loads the new values; UNDO through the kit's own table set (what Server Setup -> Changes -> Undo runs)
    Cfg.load(Paths.get(os.path.dirname(hm)))
    pk = Cfg.kind("Goat")
    K.check(sorted(zip([str(x) for x in pk.keys], [float(x) for x in pk.vals])) == sorted(stats(KV["Goat"][3])), "CMIG2 the updated file loads the new Goat values")
    P_("CfgPub").start(Paths.get(os.path.dirname(hm)), None)      # the kit as the plugin starts it (reads that config file)
    Fn_ = Fn()
    ObjA = JArray(JClass("java.lang.Object"))
    ks = Fn_.apply(ObjA(["keys", "pets.kinds", "Goat"]))
    vals = dict(zip([str(x) for x in ks[0]], [str(x) for x in ks[2]])) if ks is not None else {}
    K.check(vals.get("Goat") == kind_line("Goat", "new").replace("/", "|"), "CMIG2 the kit sees the Goat entry exactly as the change-log 'new' column (Undo matches it): %s" % vals.get("Goat"))
    # the server console path (no permission lookup outside a server); the kit writes the file 0.5 s later on its save thread
    rr = Fn_.apply(ObjA(["tset", "pets.kinds", "Goat", kind_line("Goat", "old").replace("/", "|"), None, "console", "yes", "console"]))
    st = [str(x) for x in rr] if rr is not None else []
    import time
    for _w in range(40):
        time.sleep(0.25)
        if ("kind.Goat=%s\n" % kind_line("Goat", "old")) in open(os.path.join(hm, "config.properties"), encoding="latin-1").read():
            break
    pk = Cfg.kind("Goat")
    K.check(st[:1] == ["ok"] and sorted(zip([str(x) for x in pk.keys], [float(x) for x in pk.vals])) == sorted(stats(KV["Goat"][2]))
            and ("kind.Goat=%s\n" % kind_line("Goat", "old")) in open(os.path.join(hm, "config.properties"), encoding="latin-1").read(),
            "CMIG2 UNDO: the kit's tset with the logged old columns = ok, the file line + the loaded Goat back to the 0.3.0 values: %s" % st)
    Cfg.load(Paths.get(mods))
    # hand edits, spaces, number-equal, reordered, a continued line, CRLF
    txt = (D30.replace("kind.Goat=" + kind_line("Goat", "old"), "kind.Goat=Mining/Uncommon/fortune.mining:12,swing.mining:5")
           .replace("kind.Wolf=" + kind_line("Wolf", "old"), "kind.Wolf = Combat / Rare / str:20.0, cd:15,cc:5  ")
           .replace("kind.Hawk=" + kind_line("Hawk", "old"), "kind.Hawk=Combat/Epic/cd:25,cc:20")
           .replace("kind.Ram=" + kind_line("Ram", "old"), "kind.Ram=Combat/Epic/def:50,\\\n  health:80")
           .replace("kind.Tusker=" + kind_line("Tusker", "old"), "kind.Tusker=combat/Rare/str:30")
           .replace("kind.Camel=" + kind_line("Camel", "old"), "kind.Camel=Exploration/Epic/stamina:30"))
    hm = cm("hand", txt, crlf=True)
    oldt = open(os.path.join(hm, "config.properties"), "rb").read().decode("latin-1")
    msg = str(Mig2.run(Paths.get(hm)))
    newt = open(os.path.join(hm, "config.properties"), "rb").read().decode("latin-1")
    K.check("kind.Goat=Mining/Uncommon/fortune.mining:12,swing.mining:5\r\n" in newt and "kind.Ram=Combat/Epic/def:50,\\\r\n  health:80\r\n" in newt
            and "kind.Tusker=combat/Rare/str:30\r\n" in newt and "kind.Camel=Exploration/Epic/stamina:30\r\n" in newt,
            "CMIG2 hand edits kept: Goat value, the continued Ram line, Tusker's skill case, Camel's rarity")
    K.check("kind.Wolf = %s  \r\n" % kind_line("Wolf", "new") in newt and "kind.Hawk=%s\r\n" % kind_line("Hawk", "new") in newt,
            "CMIG2 number-equal / spaced (Wolf: key, separator + trailing spaces kept) and reordered (Hawk) default lines are updated")
    K.check(newt.count("\r\n") == oldt.count("\r\n") and "\n" not in newt.replace("\r\n", ""), "CMIG2 CRLF kept everywhere")
    K.check(all(("kept hand-edited kind.%s=" % k) in msg for k in ("Goat", "Tusker", "Camel")) and "15 kinds" in msg, "CMIG2 each hand edit noted, 15 kinds updated: %s" % msg[:200])
    hm = cm("none", None)
    K.check("the 0.3.1 defaults apply" in str(Mig2.run(Paths.get(hm))) and os.path.exists(os.path.join(hm, "migrations", "pets-031.done")), "CMIG2 no config file = the marker only")
    hm = cm("new", dt)
    oldb = open(os.path.join(hm, "config.properties"), "rb").read()
    K.check("nothing to change" in str(Mig2.run(Paths.get(hm))) and open(os.path.join(hm, "config.properties"), "rb").read() == oldb
            and not os.path.exists(os.path.join(hm, "config-history")), "CMIG2 a 0.3.1 file = nothing to change (no History copy)")
    hm = cm("blocked", D30)
    open(os.path.join(hm, "config-history"), "w").write("x")
    oldb = open(os.path.join(hm, "config.properties"), "rb").read()
    K.check(str(Mig2.run(Paths.get(hm))) == "" and open(os.path.join(hm, "config.properties"), "rb").read() == oldb and not os.path.exists(os.path.join(hm, "migrations", "pets-031.done")),
            "CMIG2 config-history cannot be written = nothing rewritten, no marker (tried again next start)")
    rr = Mig2.mgUpdate("a=1\nkind.Goat=%s\nkind.Goat=Mining/Uncommon/fortune.mining:11\n" % kind_line("Goat", "old"))
    K.check(int(rr[1]) == 0 and "kept hand-edited kind.Goat=Mining/Uncommon/fortune.mining:11" in str(list(rr[2])), "CMIG2 the LAST entry decides (what Properties keeps)")
    o_ = ("kind.Goat=%s\n" % kind_line("Goat", "old")).encode()
    n_ = ("kind.Goat=%s\n" % kind_line("Goat", "new")).encode()
    K.check(bool(Mig2.sameAfter(o_, n_)) and not bool(Mig2.sameAfter(o_ + b"x=1\n", n_ + b"x=2\n"))
            and not bool(Mig2.sameAfter(o_, b"kind.Goat=Mining/Uncommon/fortune.mining:99\n")) and not bool(Mig2.sameAfter(o_, n_ + b"y=1\n")),
            "CMIG2 sameAfter: only planned kind lines, only to the new value, no key added")
    K.check(bool(Mig2.kindEq("Combat / rare / cc:20.0, cd:25", "Combat/Rare/cd:25,cc:20")) and not bool(Mig2.kindEq("Combat/Rare/cc:20", "Combat/Rare/cc:20,cd:25"))
            and not bool(Mig2.kindEq("Combat/Rare/cc:20,cd:25/x", "Combat/Rare/cc:20,cd:25")) and not bool(Mig2.kindEq("Combat/Rare/cc:20,cd:bad", "Combat/Rare/cc:20,cd:25")),
            "CMIG2 kindEq: rarity case + spaces + order + 20.0 = the same line; a missing stat, an extra column, a bad number = not")
    # CHAIN: a 0.2.7 file (old rarity / curve + old kinds) on one 0.3.1 start = PetsCfgMig, then PetsCfgMig2
    D27 = D30
    for k_, n_v, o_v in COMPAT8:
        D27 = D27.replace("\n%s=%s\n" % (k_, n_v), "\n%s=%s\n" % (k_, o_v))
    hm = cm("chain", D27)
    b0 = open(os.path.join(hm, "config.properties"), "rb").read()
    Mig.run(Paths.get(hm))
    b1 = open(os.path.join(hm, "config.properties"), "rb").read()
    Mig2.run(Paths.get(hm))
    b2 = open(os.path.join(hm, "config.properties"), "rb").read()
    hst = sorted(f_ for f_ in os.listdir(os.path.join(hm, "config-history")) if f_.endswith(".bak"))
    K.check(len(hst) == 2 and open(os.path.join(hm, "config-history", hst[0]), "rb").read() == b0 and open(os.path.join(hm, "config-history", hst[1]), "rb").read() == b1,
            "CHAIN two History copies: the 0.2.7 bytes first, then the file after the 0.3.0 update: %s" % hst)
    chl = open(os.path.join(hm, "config-changes.log"), encoding="utf-8").read().splitlines()
    K.check(len(chl) == 27 and sum(1 for l in chl if "\tSkyWynn update 0.3.0\t" in l) == 8 and sum(1 for l in chl if "\tSkyWynn update 0.3.1\t" in l) == 19,
            "CHAIN 8 + 19 change-log lines (0.3.0's first)")
    K.check(os.path.exists(os.path.join(hm, "migrations", "pets-030.done")) and os.path.exists(os.path.join(hm, "migrations", "pets-031.done")), "CHAIN both markers")
    p2 = props(os.path.join(hm, "config.properties"))
    K.check(all(p2.get(k_) == n_v for k_, n_v, o_v in COMPAT8) and all(p2.get("kind." + k) == kind_line(k, "new") for k in KV)
            and b2.decode("latin-1").split("\n").__len__() == b0.decode("latin-1").split("\n").__len__(), "CHAIN the result = the 0.3.1 numbers on every planned line, no line added / lost")
    K.check(Mig.run(Paths.get(hm)) == "" and Mig2.run(Paths.get(hm)) == "" and open(os.path.join(hm, "config.properties"), "rb").read() == b2, "CHAIN a second start changes nothing")
    K.save()


# ======================================================================================================== CP: constant-pool diff
def run_cp(out, jar, scratch, _home):
    import zipfile
    sys.path.insert(0, os.path.join(TOOLS, "dev"))
    from cpstrings import read_utf8_constants as R
    K = HK.Child(out)
    a, b = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    okv = lambda x, v: x == v or x.startswith("# SkyyPets %s - slot pets." % v) or x == "[SkyyPets] %s ready - " % v or (v == "0.3.1" and x == "com/skyy/pets/PetsCfgMig2")
    for c in sorted(EXPECT):
        n = "com/skyy/pets/%s.class" % c
        x, y = set(R(a.read(n))), set(R(b.read(n)))
        bad = [t for t in x - y if not (okv(t, "0.3.0") or any(t == "kind.%s=%s" % (k, kind_line(k, "old")) or t == "%s=%s" % (k, kind_line(k, "old")) for k in CHANGED))]
        bad += [t for t in y - x if not (okv(t, "0.3.1") or any(t == "kind.%s=%s" % (k, kind_line(k, "new")) or t == "%s=%s" % (k, kind_line(k, "new")) for k in CHANGED))]
        K.check(not bad, "CP %s: only the version text + kind lines differ: %s" % (c, [t[:80] for t in bad][:3]))
    K.save()


# ======================================================================================================== LIVE: start twice on a copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, Log = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = tree(home)
    oldcfg = props(os.path.join(home, "config.properties"))

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return [int(x) for x in Store.scanAll()], [int(x) for x in Store.fuseRecover()]
    sc1, fr1 = start()
    t1 = tree(home)
    ch = sorted(k for k in t1 if t0.get(k) != t1[k])
    newcfg = props(os.path.join(home, "config.properties"))
    exp = set(k for k, n, o in COMPAT8 if oldcfg.get(k) is not None and abs(float(oldcfg[k]) - float(o)) < 1e-9)
    exp |= set("kind." + k for k in CHANGED if oldcfg.get("kind." + k) is not None and oldcfg["kind." + k].replace(" ", "") == kind_line(k, "old"))
    chk = set(k for k in newcfg if newcfg.get(k) != oldcfg.get(k))
    K.check(chk == exp, "LIVE start 1: config.properties changed exactly the old-default lines (%d: %s) - got %s" % (len(exp), sorted(exp)[:6], sorted(chk ^ exp)))
    K.check(all(newcfg.get(k) == kind_line(k[5:], "new") for k in exp if k.startswith("kind.")), "LIVE ... to the 0.3.1 kind values")
    K.check(all(k == "config.properties" or k.startswith("config-history") or k == "config-changes.log" or k.startswith("migrations") for k in ch),
            "LIVE start 1 writes only the config updates (+ history / log / markers): %s" % ch)
    print("LIVE: %d lines updated (%d kind lines), files written: %s" % (len(chk), len([k for k in chk if k.startswith("kind.")]), ch))
    K.check(sc1[2] == 0 and sc1[3] == 0 and fr1[0] == 0, "LIVE the pet files read (files, pets, unreadable, dup %s), no cut-off fuse" % sc1)
    sc2, fr2 = start()
    K.check(tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes NOTHING")
    K.save()


# ======================================================================================================== R030: the 0.3.0 phases on 0.3.1
def run_r030(out, jar, scratch, _home):
    K = HK.Child(out)
    t30 = os.path.join(HERE, "test_skyypets_0.3.0.py")
    for ph in ("sys", "hub", "snd"):
        d = os.path.join(scratch, "r030-" + ph)
        os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
        o = os.path.join(d, "out.json")
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(d, "tmp")
        p = subprocess.run([sys.executable, t30, "--phase", ph, "--out", o, "--dir", d, "--jar", jar], env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        open(os.path.join(scratch, "r030-%s.log" % ph), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
        if not os.path.isfile(o):
            K.check(False, "R030 %s: the 0.3.0 phase wrote no result (exit %s): %s" % (ph, p.returncode, (p.stdout + p.stderr)[-600:]))
            continue
        d_ = json.load(open(o))
        K.check(p.returncode == 0 and not d_["fails"] and d_["ok"] > 0, "R030 the 0.3.0 harness's %s phase on the 0.3.1 jar: %d ok, fails %s" % (ph, d_["ok"], d_["fails"][:4]))
        print("R030 %s: %d ok, %d fail(s)" % (ph, d_["ok"], len(d_["fails"])))
    K.save()


if __name__ == "__main__":
    phases = [("cp", run_cp), ("sys", run_sys), ("live", run_live)]
    if "--no-r030" not in sys.argv:
        phases.append(("r030", run_r030))
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE, "Skyy_SkyyPets"))
