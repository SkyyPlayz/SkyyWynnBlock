"""SkyyProfiles 0.1.6 - bare-JVM harness: THE CREATE PROFILE PAGE KNOWS THE ASSASSIN + MONK (tools/profiles_0_1_6_patch.py; Skyy LOCKED
2026-10-07 "1. make the classes"). Built ON the 0.1.5 harness (SkyyProfiles/test_skyyprofiles_0.1.5.py, imported for its page builder,
markup model, text / contrast checks and bytecode lister - never edited).

    python SkyyProfiles/test_skyyprofiles_0.1.6.py [--jar <SkyyProfiles-0.1.6.jar>] [--old <SkyyProfiles-0.1.5.jar>] [--dir <scratch>]
                                                   [--live <Skyy_SkyyProfiles folder>] [--keep] [--no15]

  A    every class of both jars loads under -Xverify:all
  P    PAGES: the 0.1.5 harness's 48 page states (33 compat + 15 delete) built by the REAL ProfilePage of the 0.1.6 jar AND of the 0.1.5
       jar DRESSED with the 0.1.6 roster tables (ProfRoster names / skills / texts / colours / weapon texts / icons / roles / playable):
       every state identical (commands + bindings) except "create eight classes", whose class:list says "Shaman:Totems" - 0.1.6 turns
       the Monk card on with it (the alias), 0.1.5 adds an extra "Shaman" card. = the page code did not change, only the table did.
       + 6 NEW states (the SkyyClasses 0.1.14 class:list: seven playable cards incl. Assassin + Monk, a Monk / an Assassin pick, a profile
       still stored as Shaman, seven classes in the list, auto limit 7) through the 0.1.5 harness's markup / layout / text / contrast
       checks with the 0.1.6 data colours (the Monk saffron), and their exact texts
  G16  ALIAS LOGIC on a scratch COPY of the live players folder + a synthetic Shaman player: publish -> profile:class = Monk and
       profile:list says Monk while the file keeps Shaman (byte for byte); every live player publishes exactly its stored class (no
       file written); /profileadmin setclass's path (ProfRoster.entry("shaman") + ProfStore.setClass) stores Monk; roster() with the
       0.1.14 class:list = 7 playable cards; an old "Shaman:Totems" list turns the Monk card on (no 8th card); the auto limit = 7
  F    class bytes 0.1.5 vs 0.1.6: exactly the planned methods / fields (ProfRoster: canon + the alias fields, indexOf / entry / roster;
       ProfStore listText / describe; ProfPub.publishLocked; the page's list card + switch question; ReadyTask's login line; the
       setclass help), version-only classes, no class added or removed
  H15  the 0.1.5 harness run against the 0.1.6 jar (control: the 0.1.5 jar, today's live data): no failure beyond the control's except
       the version / roster shape (its byte-for-byte create-view compare and data colours = part P here; class bytes = part F here;
       the archive record's version text)
"""
import os, sys, re, json, shutil, subprocess, zipfile, hashlib, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.6", "0.1.5"
PKG = "com.skyy.profiles."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "classes014", "profiles-016")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyProfiles-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "UserData", "Saves", "HUD mod",
                                                  "mods", "Skyy_SkyyProfiles")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
LIST14 = "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity,Assassin:Assassination,Monk:Discipline"
DRESS = ("NAMES", "SKILLS", "DESCS", "COLORS", "WTEXT", "ICONS", "ROLES", "ENABLED")
SYN_U = "00000000-0000-0000-0000-0000000005d1"
ASSASSIN_DESC = "Burst damage on one target. Fast twin daggers up close and kunai thrown from range - strike from behind for more."
MONK_DESC = "Fast melee fighter. A bo staff strikes with reach - quick hand wraps and heavy gauntlets."


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def m15():
    """the 0.1.5 harness as a module (its functions only - never run as a script here)"""
    spec = importlib.util.spec_from_file_location("t015", os.path.join(HERE, "test_skyyprofiles_0.1.5.py"))
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]          # its module-level arg() reads only --dir here
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def new_states(m):
    DAY, HOUR = m.DAY, m.HOUR
    seven = [(str(i), "P%d" % i, c, i * HOUR) for i, c in zip(range(1, 8), ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"])]
    six = [(str(i), "Profile %d" % i, c, i * DAY) for i, c in zip(range(1, 7), ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Warrior"])]
    return [
        ("n16 create seven monk", 1, False, [("1", "Main", "Warrior", DAY)], "1", None, "Kiwi", "Monk", "", "auto", LIST14, True, None, {}, None),
        ("n16 create first assassin", 1, True, [], None, None, "Mango", "Assassin", "", "auto", LIST14, True, None, {}, None),
        ("n16 create first none", 1, True, [], None, None, "Pear", None, "", "auto", LIST14, True, None, {}, None),
        ("n16 list shaman profile", 0, False, [("1", "Main", "Warrior", DAY), ("2", "Old alt", "Shaman", HOUR)], "2", None, "", None, "", "auto",
         LIST14, True, None, {}, None),
        ("n16 list seven classes", 0, False, seven, "7", "6", "", None, "", "auto", LIST14, True, None, {}, None),
        ("n16 list six of auto seven", 0, False, six, "1", None, "", None, "", "auto", LIST14, True, None, {}, None),
    ]


# ============================================================================================ child: page states of one jar (+ dressing)
def run_states16(jar, out, dress):
    m = m15()
    orig = m._jvm_start
    side = {}

    def start(jars, extra_cp=()):
        B = orig(jars, extra_cp)
        from jpype import JClass
        R = JClass(PKG + "ProfRoster")
        side["tables"] = dict((k, [bool(x) if k == "ENABLED" else str(x) for x in getattr(R, k)]) for k in DRESS)
        if dress:
            dt = json.load(open(dress))["tables"]
            for k in DRESS:
                arr = getattr(R, k)
                assert len(arr) == len(dt[k]), (k, len(arr), len(dt[k]))
                for i, v in enumerate(dt[k]):
                    arr[i] = v
            side["dressed"] = dict((k, [bool(x) if k == "ENABLED" else str(x) for x in getattr(R, k)]) for k in DRESS)
        return B
    m._jvm_start = start
    m.STATES_DEL = list(m.STATES_DEL) + new_states(m)
    copy = os.path.join(SCRATCH, "live", "Skyy_SkyyProfiles")       # the "LIVE" states read the scratch copy
    m.run_states(jar, out, "new")
    res = json.load(open(out))
    res.update(side)
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: G16 alias logic
def run_g16(jar, home, out):
    m = m15()
    m._jvm_start([jar])
    from jpype import JClass
    Sto, Ros, Cfg = JClass(PKG + "ProfStore"), JClass(PKG + "ProfRoster"), JClass(PKG + "ProfCfg")
    UUID, Paths, JStr, Arr = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")
    pdir = os.path.join(home, "players")
    Sto.DIR = Paths.get(pdir, Arr.newInstance(JStr.class_, 0))
    br = Cfg.bridge()
    G = {"live": {}}

    def sha(f):
        return hashlib.sha256(open(f, "rb").read()).hexdigest()
    before = dict((f, sha(os.path.join(pdir, f))) for f in os.listdir(pdir) if f.endswith(".properties"))
    for f in sorted(before):
        u = UUID.fromString(f[:36])
        Sto.publish(u)
        p = Sto.load(u)
        a = str(p.getProperty("active", ""))
        G["live"][f] = [None if br.get("profile:class:" + f[:36]) is None else str(br.get("profile:class:" + f[:36])),
                        str(p.getProperty("p." + a + ".class", "")), None if br.get("profile:list:" + f[:36]) is None else str(br.get("profile:list:" + f[:36]))]
    us = UUID.fromString(SYN_U)
    Sto.publish(us)
    G["syn"] = [str(br.get("profile:class:" + SYN_U)), str(br.get("profile:list:" + SYN_U)), str(Sto.describe(us))]
    G["after_publish"] = dict((f, sha(os.path.join(pdir, f))) for f in os.listdir(pdir) if f.endswith(".properties"))
    G["before"] = before
    e = Ros.entry("shaman")
    G["entry"] = [str(x) for x in e] if e is not None else None
    G["idx"] = [int(Ros.indexOf(x)) for x in ("Shaman", "shamans", "Monk", "Assassin", "Necromancer")]
    G["canon"] = [None if Ros.canon(x) is None else str(Ros.canon(x)) for x in ("Shaman", "Monk", "Archer", "", None)]
    G["setclass"] = bool(Sto.setClass(us, "2", e[0]))
    G["file2"] = open(os.path.join(pdir, SYN_U + ".properties"), encoding="latin-1").read()
    br.put("class:list", LIST14)
    r = Ros.roster()
    G["roster14"] = [[str(c[0]), str(c[1]), str(c[6])] for c in r]
    Cfg.MAX_SETTING = "auto"
    G["cap14"] = [int(Cfg.classCount()), int(Cfg.capFor(us))]
    br.put("class:list", "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity,Shaman:Totems")
    r = Ros.roster()
    G["roster_old"] = [[str(c[0]), str(c[1]), str(c[6])] for c in r]
    br.put("class:list", "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity")
    G["cap13"] = int(Cfg.capFor(us))
    G["choice"] = str(Ros.choiceText())
    json.dump(G, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--states16" in sys.argv:
        return run_states16(arg("--states16"), arg("--out"), arg("--dress"))
    if "--g16" in sys.argv:
        return run_g16(arg("--g16"), arg("--home"), arg("--out"))
    if "--bytecode" in sys.argv:
        m = m15()
        m.VERSION, m.OLD_VERSION = VERSION, OLD_VERSION
        return m.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    if not SCRATCH.replace("\\", "/").lower().startswith(sroot + "/"):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    m = m15()
    live_before = m.all_hashes(LIVE)
    copy = os.path.join(SCRATCH, "live", "Skyy_SkyyProfiles")
    shutil.copytree(LIVE, copy)
    me = os.path.abspath(__file__)
    # ---------------------------------------------------------------- P: states
    outs = {"new": os.path.join(SCRATCH, "states-new.json"), "old": os.path.join(SCRATCH, "states-old.json")}
    p = subprocess.run([sys.executable, me, "--states16", JAR, "--out", outs["new"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["new"]), "P: state child (0.1.6) ran")
    p = subprocess.run([sys.executable, me, "--states16", OLD_JAR, "--out", outs["old"], "--dress", outs["new"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["old"]), "P: state child (0.1.5 dressed) ran")
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "F: bytecode child ran")
    # ---------------------------------------------------------------- G16 home: a copy of the live players + the synthetic Shaman player
    ghome = os.path.join(SCRATCH, "g16")
    shutil.copytree(os.path.join(LIVE, "players"), os.path.join(ghome, "players"))
    open(os.path.join(ghome, "players", SYN_U + ".properties"), "w", newline="\n").write(
        "active=1\nepoch=3\np.1.name=Old alt\np.1.class=Shaman\np.1.created=1700000000000\np.1.lastPlayed=1700000000000\n"
        "p.2.name=Daggers\np.2.class=Assassin\np.2.created=1700000000000\np.2.lastPlayed=0\n")
    gout = os.path.join(SCRATCH, "g16.json")
    p = subprocess.run([sys.executable, me, "--g16", JAR, "--home", ghome, "--out", gout, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(gout), "G16: child ran")
    h15 = None
    if "--no15" not in sys.argv:
        h15 = {}
        for tag, jj in (("new", JAR), ("ctl", OLD_JAR)):
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyprofiles_0.1.5.py"), "--jar", jj, "--dir",
                                 os.path.join(SCRATCH, "h15-" + tag), "--live", LIVE], env=env, capture_output=True)
            h15[tag] = ph.stdout.decode("utf-8", "replace")
    if FAILS:
        return finish(live_before, m)
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"][:3]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d" % (os.path.basename(new["jar"]), new["loaded"], new["classes"], os.path.basename(old["jar"]),
                                                     old["loaded"], old["classes"]))
    check(old.get("dressed") == new.get("tables") and new["tables"]["NAMES"][6] == "Monk" and new["tables"]["ENABLED"] == [True] * 7,
          "P: the 0.1.5 jar was dressed with the 0.1.6 roster tables: %s" % new["tables"]["NAMES"])
    ns16 = [st[0] for st in new_states(m)]
    same, diff = 0, []
    for nm in new["states"]:
        if nm in ns16:
            continue
        a, b = new["states"][nm], old["states"].get(nm)
        if b is not None and a["commands"] == b["commands"] and a["events"] == b["events"] and a["error"] == b["error"]:
            same += 1
        else:
            diff.append(nm)
    check(diff == ["create eight classes"] and same == 47, "P: %d states identical in 0.1.6 and the dressed 0.1.5; differ only %s" % (same, diff))
    if "create eight classes" in new["states"]:
        tn, to = json.dumps(new["states"]["create eight classes"]["commands"]), json.dumps(old["states"]["create eight classes"]["commands"])
        check("Shaman" not in tn and "Totems" in tn and "Coming later" not in tn and "Totems" not in to and "Coming later" in to,
              "P: create eight classes - class:list 'Shaman:Totems' turns the Monk card on (skill Totems) in 0.1.6; the dressed 0.1.5 left "
              "the Monk 'coming later' (its Shaman entry became an 8th / 9th extra card, never drawn)")
    # the new states through the 0.1.5 markup / layout / text / contrast checks, with the 0.1.6 data colours
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(os.path.join(HERE, "build_skyyprofiles_%s.py" % VERSION), encoding="utf8").read()
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (\[.*?\](?:\s*\+\s*\[.*?\])?)\n", src, re.M | re.S).group(1))
    check("#f08a30" in data_colors and "#ff7a5c" not in data_colors, "P: the Monk saffron is a data colour, the Shaman red is gone")
    m.FAILS, m.OKS = FAILS, OKS            # the 0.1.5 checks report into this harness
    counts = m.new_counts()
    for st in new_states(m) + [s_ for s_ in m.STATES_COMPAT if s_[1] == 1]:
        nm = st[0]
        got = m.markup_checks(nm, new["states"][nm], SUI, counts, data_colors)
        if got is None:
            continue
        root, ids, sets, raw = got
        cards = [i for i in ids if re.fullmatch(r"SkyyPf(Card\d+|Cls\d+|NewCard)", i)]
        check(cards and all(m._pairs(ids[c]["props"].get("Anchor")).get("Height") == m.CARD_H_NEW for c in cards), "P %s: every card %d px" % (nm, m.CARD_H_NEW))
        if nm.startswith("n16 create"):
            cls_ = [i for i in ids if re.fullmatch(r"SkyyPfCls\d+", i)]
            evs = [m.ev_a(e) for e in new["states"][nm]["events"]]
            txt = json.dumps(new["states"][nm]["commands"])
            pick_ = st[7]
            want_ev = [i for i, c_ in enumerate(["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]) if c_ != pick_]
            check(len(cls_) == 7 and [e_ for e_ in evs if e_ and e_.startswith("pfcls")] == ["pfcls%d" % i for i in want_ev] and "Coming later" not in txt and "Discipline" in txt
                  and "Assassination" in txt and MONK_DESC in txt and ASSASSIN_DESC in txt and "Shaman" not in txt,
                  "P %s: seven class cards, every one not picked yet is clickable, the Monk + Assassin texts, nothing 'coming later': %s" % (nm, evs))
    m.report_counts(counts)
    ls_ = json.dumps(new["states"]["n16 list shaman profile"]["commands"])
    check("Monk - combat skill Discipline" in ls_ and "Shaman" not in ls_, "P: a profile stored as Shaman shows 'Monk - combat skill Discipline'")
    l7 = json.dumps(new["states"]["n16 list seven classes"]["commands"])
    check("Switch to P6 (Assassin)?" in l7 and "Monk - combat skill Discipline" in l7 and "Assassin - combat skill Assassination" in l7,
          "P: seven profiles, one per class; the switch question names the Assassin")
    l6 = new["states"]["n16 list six of auto seven"]
    check(any(m.ev_a(e) == "pfnew" for e in l6["events"]) and "All 6 profile slots" not in json.dumps(l6["commands"]),
          "P: 6 profiles with the auto limit and SkyyClasses 0.1.14's list = the 7th can still be created (Create new shown)")
    print("P. %d states identical in 0.1.6 and the dressed 0.1.5 (create eight classes differs by the alias); %d new 0.1.6 states checked "
          "(markup, layout, texts, contrast); %d create views re-checked with the 0.1.6 colours" % (same, len(ns16), len([s_ for s_ in m.STATES_COMPAT if s_[1] == 1])))
    # ---------------------------------------------------------------- G16
    G = json.load(open(gout))
    syn_f = SYN_U + ".properties"
    check(G["after_publish"] == G["before"], "G16: publishing every player (live + synthetic) wrote no file")
    check(all(v[0] == (v[1] or None) for k, v in G["live"].items() if k != syn_f),
          "G16: every live player publishes exactly its stored class: %s" % dict((k, v[:2]) for k, v in G["live"].items() if k != syn_f))
    check(G["syn"][0] == "Monk" and G["syn"][1] == "1:Old alt:Monk,2:Daggers:Assassin" and "Shaman" not in G["syn"][2],
          "G16: p.1.class=Shaman publishes profile:class Monk, profile:list Monk, the admin describe says Monk: %s" % G["syn"])
    check(G["entry"] is not None and G["entry"][0] == "Monk" and G["entry"][1] == "Discipline" and G["idx"] == [6, 6, 6, 5, -1]
          and G["canon"] == ["Monk", "Monk", "Archer", "", None], "G16: entry / indexOf / canon: %s %s %s" % (G["entry"], G["idx"], G["canon"]))
    check(G["setclass"] and "p.2.class=Monk" in G["file2"] and "p.1.class=Shaman" in G["file2"],
          "G16: setclass ... shaman stores Monk; the old p.1 line is not rewritten")
    check(G["roster14"] == [["Archer", "Archery", "1"], ["Warrior", "Swordsmanship", "1"], ["Mage", "Sorcery", "1"], ["Berserker", "Fury", "1"],
                            ["Priest", "Divinity", "1"], ["Assassin", "Assassination", "1"], ["Monk", "Discipline", "1"]],
          "G16: SkyyClasses 0.1.14's class:list = 7 pickable cards: %s" % G["roster14"])
    check(len(G["roster_old"]) == 7 and G["roster_old"][6] == ["Monk", "Totems", "1"] and G["roster_old"][5][2] == "0",
          "G16: an older list naming Shaman turns the Monk card on (no 8th card): %s" % G["roster_old"])
    check(G["cap14"] == [7, 7] and G["cap13"] == 5 and G["choice"] == "Archer, Warrior, Mage, Berserker or Priest",
          "G16: auto limit 7 with SkyyClasses 0.1.14 (5 with 0.1.13's list): %s %s" % (G["cap14"], G["cap13"]))
    print("G16. alias: Shaman profile publishes Monk (file untouched), setclass shaman -> Monk, 7 cards, auto limit 7; %d live players unchanged" % (len(G["live"]) - 1))
    # ---------------------------------------------------------------- F
    bc = json.load(open(bco))
    plan = {
        "com/skyy/profiles/ProfRoster.class": {"changed": ["<clinit>()V", "entry(Ljava/lang/String;)[Ljava/lang/String;", "indexOf(Ljava/lang/String;)I",
                                                          "roster()Ljava/util/ArrayList;"], "new": ["canon(Ljava/lang/String;)Ljava/lang/String;"],
                                              "fields_new": ["ALIAS_FROM [Ljava/lang/String;", "ALIAS_TO [Ljava/lang/String;"]},
        "com/skyy/profiles/ProfStore.class": {"changed": ["describe(Ljava/util/UUID;)Ljava/lang/String;", "listText(Ljava/util/Properties;)Ljava/lang/String;"]},
        "com/skyy/profiles/ProfPub.class": {"changed": ["publishLocked(Ljava/util/UUID;Ljava/util/Map;)V"]},
        "com/skyy/profiles/AdmSetClassCmd.class": {"changed": ["AdmSetClassCmd()V"]},
    }
    bad = []
    seen = set()
    for n_, v in sorted(bc.items()):
        seen.add(n_)
        if n_ in plan:
            w = plan[n_]
            if sorted(v["changed"]) != sorted(w.get("changed", [])) or v["new"] != w.get("new", []) or v["gone"] or v["fields_new"] != w.get("fields_new", []) or v["fields_gone"]:
                bad.append((n_, v["changed"], v["new"], v["fields_new"]))
        elif not v["version_only"]:
            bad.append((n_, v["changed"], v["new"], "not version-only"))
    print("F. class bytes 0.1.5 -> 0.1.6: %s" % dict((k.split("/")[-1], (v["changed"], v["new"], v["version_only"])) for k, v in bc.items()))
    pg = [k for k in bc if k.endswith("/ProfilePage.class") or k.endswith("/ReadyTask.class") or "Join" in k]
    check(not [b_ for b_ in bad if not any(x in b_[0] for x in ("ProfilePage", "ReadyTask", "ProfJoin"))] and all(c in seen for c in plan),
          "F: only the planned classes / methods / fields change (+ version-only classes): %s" % bad[:6])
    for k in pg:          # the page / login line: only the class reads went through canon (the methods that read p.<id>.class for display)
        lst = json.dumps(bc[k]["listing"])
        check(bc[k]["new"] == [] and not bc[k]["fields_new"] and "canon" in lst, "F: %s: changed only where a class is read for display (canon): %s" % (
            k.split("/")[-1], bc[k]["changed"]))
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(set(zo.namelist()) == set(zn.namelist()), "F: no class added or removed: %s" % sorted(set(zo.namelist()) ^ set(zn.namelist())))
    # ---------------------------------------------------------------- H15
    if h15 is not None:
        def fails_of(t):
            return [ln.strip()[len("FAILED: "):] for ln in t.splitlines() if ln.strip().startswith("FAILED: ")] + \
                   [ln[len("FAIL "):] for ln in t.splitlines() if ln.startswith("FAIL ")]
        fn_, fc_ = set(fails_of(h15["new"])), set(fails_of(h15["ctl"]))
        shape = ("C create ", "F: ", "G6 the archive record holds the profile's entries")
        other = sorted(f for f in fn_ - fc_ if not f.startswith(shape) and "colour #f08a30 is a kit / data colour" not in f)
        mn = (list(re.finditer(r"(\d+) checks passed, (\d+) failed", h15["new"])) or [None])[-1]
        mc = (list(re.finditer(r"(\d+) checks passed, (\d+) failed", h15["ctl"])) or [None])[-1]
        check(mn is not None and mc is not None and not other,
              "H15: the 0.1.5 harness on 0.1.6 fails nothing beyond the control's + the version / roster shape: %s" % other[:4])
        print("H15. 0.1.5 harness: on 0.1.6 %s, on 0.1.5 (control, today's live data) %s; control failures: %s; extra on 0.1.6 (shape): %d" % (
            mn.group(0) if mn else "?", mc.group(0) if mc else "?", sorted(fc_)[:4], len(fn_ - fc_)))
    return finish(live_before, m)


def finish(live_before, m):
    check(m.all_hashes(LIVE) == live_before, "the live Skyy_SkyyProfiles folder was never written")
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyProfiles %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
