"""Bare-JVM harness for SkyyTrees 0.3 (tools/trees_0_3_patch.py). PART 1: the Alchemy + Smithing trees, Mining / Smithing Dust 5, the
reader gating "Coming with <mod>", the one-time trees.properties update, two tab rows. PART 2 (section K below, 2026-10-03): the
Wynncraft-style class tree behind class.enabled, its probe page, Ability Points, Undo, the coin respec. Copied forward from
SkyyTrees/test_skyytrees_0.2.5.py (its page-state machinery: the engine's own UICommandBuilder / UIEventBuilder on the REAL TreePage, the
markup model, the layout model, the client font-table text fit, the contrast check, the old-vs-new click compare) and extended so the
NEW code paths are EXECUTED, not only loaded. Committed next to the build so the build docstring's CHECKED claims can be re-run.
FIX ROUND (2026-10-03, after the spec / data / UI reviews): + Deep Reserves' flat Now / Next texts (N), the live Amount in the class
detail and an admin override (K states "class amount override", "class mage amount"), the live-rows note ("class ap rows"), the
element / capstone / P3 / P4 detail lines (K states "class sel element *", "class sel capstone", "class sel p3 / p4"), the Assassin page
and its /tree answers, no cover on reader-gated cells, the stale class page after class.enabled went OFF (k10, k15, k16), the armed
price re-arm (k17), null / throwing coins:fn:take (k18), the class-qualified Undo list (k19), a broken-chain tree respecs free (k20),
no cooldown skip at level 0 (k21); logic child: level() -1 on a bad skill:fn:level, priceOf / negBalance, TreeClass.now, typeLine,
note, badFlag WARN once, cmdClass for an unknown class, valueText for MANA.

    python SkyyTrees/test_skyytrees_0.3.py [--jar <SkyyTrees-0.3.jar>] [--old <SkyyTrees-0.2.5.jar>] [--live <Skyy_SkyyTrees folder>]
                                           [--dir <scratch inside tools/dev/scratch/>] [--keep]

Build first: python tools/trees_0_3_patch.py, then python SkyyTrees/build_skyytrees_0.3.py (and, on a fresh checkout, python
SkyyTrees/build_skyytrees_0.2.5.py - jars are git-ignored; --old = the SET pin 0.2.5). Child processes start fresh JVMs (the game's own
JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar read-only; TEMP / TMP / java.io.tmpdir in the scratch folder; on a JDK 26+ JRE also
--enable-final-field-mutation=ALL-UNNAMED for the PlayerRef stand-in). The live world is READ ONLY: its Skyy_SkyyTrees folder is copied
into the scratch folder and only the copy is ever written (the live trees.properties and player files are compared before / after).
  A  every class of both jars loads and verifies (-Xverify:all)
  B  page states of the SIX 0.2.5 TREES, the real TreePage.build of both jars (0.2.5's 72 grid states + the special states + every
     result text): identical event bindings once the two new tab bindings (#SkyyTrTab6 / #SkyyTrTab7, inside the same tab loop) are
     left out, no 0.2.5 element id missing, every 0.2.5 text still shown
  C  the 0.3 markup as the client gets it (every state, old trees AND new trees): check_markup / check_page / assert_proven, kit
     colours + the eight tree colours only, no FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Right, Center, Full / ItemGrid,
     the page root 1440 x 941, the node grid on the list well, the two tab rows (#SkyyTrHead = tabs 0-3, 6, 7 + the level label,
     #SkyyTrHead2 = tabs 4, 5; the left margin restarts per row), the layout model (the body filled exactly: 869 px), every label's
     text measured with the client's glyph tables fits, every non-button label >= 3.0:1 on its effective background, infoColor
  D  clicks on the six 0.2.5 trees: the 0.2.5 sequences in both jars - identical page state, node levels / off flags / respec times /
     credit (the 0.2.5 parts of the arrays), coin calls and dirty files after every click
  N  the NEW trees on the real page: every Alchemy / Smithing node selected with no reader flag, with all flags, owned-but-coming,
     partial flags: "Coming with <first reader>" card lines exactly on the coming nodes, the detail state / buy line / "Coming soon"
     button on a coming selected node, the info row naming the waiting mods; and click sequences (unlock / level up / toggle / respec
     with debug Dust, the coming refusals, the path pass-through, a reader that goes away and comes back, partial flags)
  K  the CLASS TREE (0.3 part 2): the jar's TreeClass tables against an independent Python model of spec 5-7 (37 nodes, 36 links,
     parents / needs / locks / lanes / pages, the stat kinds and amounts per class, the live totals, the slot and bar-piece tables);
     page states of the class tab on the real TreePage (every class on both pages, reader flags and their alias keys, the no-class /
     unknown-class / no-SkyySkills / unreadable-file / negative-balance / broken-chain / both-picks / node-off / probe states, every
     result text's colour): the class tab button and binding exactly when class.enabled (or probe), the rune strip + pager, the 6 x 9
     slots of 104 x 88 with the node cells where the model puts them, every cell's one state line = the model's, the selected look and
     the coming cover, the gold / grey bar pieces = the model's intact links, the info row (AP free of all, the respec price), the detail
     well (state, Owned / Coming soon / Unlock, Undo live or disabled), the lane note, the footer Respec <Class>; and 14 click
     sequences EXECUTING buy (chain, pick-one, lane count, class level, AP shortage, coming), Undo (allowed, blocked by a child, off,
     empty), respec (armed text, coins taken once through coins:fn:take, refused without enough coins / without SkyyCoins, cooldown,
     free on a negative balance), pages and cells, class trees OFF (no tab, no effect), the PROBE page (a page-local copy, nothing
     saved, no coins), no class, no SkyySkills, the Mana Regen registry posts (Mage); in the logic child: AP maths, intact / spent on
     hand-made sets, the reader alias keys, tree:fn:level / bonus for class keys, TreeFx.stats with class Health + Mana on the stand-in
     stat map, gear:extras + skill:fn:manaregen posts and their removal, the saved Class.<Class> lines (round trip, unknown lines kept,
     the 0.2.5 rollback floor), the 41 Server Setup rows and the class checks, tree:names following class.enabled, /tree class words
  L  logic in a fresh loader: the node table (96 rows; the 0.2.5 rows field for field; the new rows = spec 2 / 3 in the section 16
     order; KEY / READERS / COMING_*), the default file (= 0.2.5's + exactly the new lines; every older ADD block byte for byte 0.2.5's),
     a fresh start (the default file written, the update never runs on it, a second start writes nothing), reads() on odd flag
     values, coming / needTier / pathOk / state / lockShort / buy / respec through TreeOps with debug Dust, the Dust rates of all eight
     trees, tree:fn:level / tree:fn:bonus / skill:bonus xp.alchemy / xp.smithing / tree:names / tree:<uuid>, the Server Setup rows
     (28: 0.2.5's 26 element for element + nodes.Alchemy / nodes.Smithing; dust.perTree help) and checks (Deep Reserves flat, the
     percent ask, checkDust names eight trees, export all -> import preview = nothing to change)
  M  TreeMig on scratch COPIES in the plugin's start order (TreeCfg.load -> TreeMig.run -> CfgPub.start), each start in a fresh loader:
     the live copy (start 1 appends exactly the block after the old bytes, History holds the old bytes, one change-log line
     dust.perTree[Mining] 10 -> 5 the kit lists for Undo; start 2 writes nothing; Undo puts 10 back and start 3 keeps it), then edited
     copies: a hand-set Mining line (kept, INFO), CRLF, no final newline, dust.xpPerDust 20 and 5, a hand-added Alchemy node line,
     config-history blocked (nothing written, retried), a 0.1-style file (the 0.2-0.2.4 blocks first, then the 0.3 block), an empty file
  P  player files: the live copies read by 0.2.5 and by 0.3 (the 0.2.5 parts identical, the new trees empty, no migration flag), saved
     by 0.3 (the same Properties), an Alchemy level saved by 0.3 then read by 0.2.5 (its trees unchanged) and saved by 0.2.5 (the
     Alchemy level is DROPPED - the rollback floor, proven)
  S  the real TreeFx.stats on a stand-in stat map: skyytree_health = Forest Vigor + Forge Hardened, the new skyytree_mana = Deep
     Reserves, removed again at 0
  E  class bytes 0.2.5 vs 0.3: the same classes + TreeMig; the abilities / gather / swing / damage / saver / message / felled / fn /
     admin command classes byte-identical (or version-only); every asset JSON (87) byte-identical; manifest Version + text
  Z  the ENGINE-ACCESS AUDIT with the JVM's own rules: every class / field / method / constructor reference of the 0.3 jar looked up with
     MethodHandles.privateLookupIn(its own class) - 0 refused (a control that calls a protected engine member from outside IS refused)
  F  the state children print no final-field mutation warning
Not testable without the game (UNVERIFIED in the build docstring): the look itself, the client parsing the page, real clicks, the
real stat map / PermissionsModule / scheduler. Nothing is deployed. Default scratch folder: tools/dev/scratch/skyytrees-03 (git-ignored);
--dir must be inside tools/dev/scratch/. At the end (unless --keep) the harness removes only what it made: the whole folder when it
created it, otherwise just its own entries. Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, json, zipfile, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.3", "0.2.5"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyytrees-03")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyTrees-%s.jar" % OLD_VERSION)))
SCRIPT = os.path.join(HERE, "build_skyytrees_%s.py" % VERSION)
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyTrees")))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


PREFIX = "SkyyTr"
PAGE_W, PAGE_H = 1440, 941
BODY_ID, BODY_INNER_H = "SkyyTrRoot", 941 - 38 - 2 * 17        # 869
ASSET_JSON = 87                                                 # the swing-speed / chop asset JSON files in both jars
OWN_ENTRIES = ("tmp", "players-old", "players-new", "states-old.json", "states-new.json", "bytecode.json", "fake", "logic.json",
               "audit.json", "l", "m", "p")
MIN_CONTRAST = 3.0
TREES = ["Mining", "Foraging", "Farming", "Cooking", "Acrobatics", "Exploration", "Alchemy", "Smithing"]
TREES_025 = TREES[:6]
NEW_TABS = ("#SkyyTrTab6", "#SkyyTrTab7")
# the spec 2 / 3 tables (section 16 order): (id, name, kind, max, per, readers)
NEW_TREE = {
    "Alchemy": [("PExtra", "Extra Brew", "ALCH", 25, 0.004, ("SkyySkills",)), ("PDur", "Long Brew", "ALCH", 20, 0.01, ("SkyySkills",)),
                ("PWisdom", "Alchemy Wisdom", "XP", 15, 0.01, ("SkyySkills",)), ("PMana", "Deep Reserves", "MANA", 10, 1.0, ()),
                ("PFrugal", "Frugal Brewer", "ALCH", 10, 0.02, ("SkyySkills",)), ("PHealth", "Health Brews", "ALCH", 15, 0.02, ("SkyySkills",)),
                ("PSig", "Signature Brews", "ALCH", 10, 0.03, ("SkyySkills",)), ("PStam", "Stamina Brews", "ALCH", 10, 0.03, ("SkyySkills",)),
                ("PSeed", "Seed Brews", "ALCH", 10, 0.03, ("SkyySkills",)), ("PDur2", "Long Brew II", "ALCH", 20, 0.01, ("SkyySkills",)),
                ("PDouble", "Double Brew", "ALCH", 10, 0.015, ("SkyySkills",)), ("PMaster", "Master Brewer", "ALCH", 5, 0.05, ("SkyySkills",))],
    "Smithing": [("SRarity", "Fine Craft", "SMITH", 25, 0.004, ("SkyyGear",)), ("SSmelt", "Smelter's Luck", "SMITH", 20, 0.01, ("SkyySkills", "SkyySacks")),
                 ("SWisdom", "Smithing Wisdom", "XP", 15, 0.01, ("SkyySkills",)), ("SReforge", "Steady Hand", "SMITH", 10, 0.04, ("SkyyGear",)),
                 ("SIdent", "Keen Eye", "SMITH", 10, 0.04, ("SkyyGear",)), ("SHealth", "Forge Hardened", "HP", 15, 1.0, ()),
                 ("SAppraise", "Appraiser", "SMITH", 10, 0.01, ("SkyyGear",)), ("SQuick", "Quick Forge", "SMITH", 10, 0.03, ("SkyySacks",)),
                 ("SFuel", "Fuel Saver", "SMITH", 10, 0.03, ("SkyySacks",)), ("SRarity2", "Fine Craft II", "SMITH", 20, 0.005, ("SkyyGear",)),
                 ("SHaggle", "Haggler", "SMITH", 10, 0.02, ("SkyyGear",)), ("SMaster", "Masterwork", "SMITH", 5, 0.01, ("SkyyGear",))],
}
READS_ALL = {"SkyySkills": ",".join("%s.%s" % (tn, n[0]) for tn in ("Alchemy", "Smithing") for n in NEW_TREE[tn] if "SkyySkills" in n[5]),
             "SkyyGear": ",".join("Smithing." + n[0] for n in NEW_TREE["Smithing"] if "SkyyGear" in n[5]),
             "SkyySacks": ",".join("Smithing." + n[0] for n in NEW_TREE["Smithing"] if "SkyySacks" in n[5])}
assert READS_ALL["SkyySkills"].count(",") == 12 and READS_ALL["SkyyGear"].count(",") == 6 and READS_ALL["SkyySacks"].count(",") == 2


def node_index(tn, nid):
    t = TREES.index(tn)
    if tn in NEW_TREE:
        return t * 12 + [n[0] for n in NEW_TREE[tn]].index(nid)
    raise KeyError(nid)


def coming_of(tn, s, reads):
    """expected coming state of slot s (1-12) of a new tree under the reader flags `reads` ({mod: csv} or None)"""
    nid, _nm, _k, _mx, _per, readers = NEW_TREE[tn][s - 1]
    if not readers:
        return False
    for m in readers:
        csv = (reads or {}).get(m)
        if csv is not None and ("%s.%s" % (tn, nid)) in [x.strip() for x in csv.split(",")]:
            return False
    return True


# ---- the per-tree profiles of the 0.2.5 grid states (levels / XP chosen so every node state shows up somewhere)
PROFILES = {
    "Mining": dict(level=34, xp=2000000, nodes={"MSpeed": 10, "MFortune": 7, "MWisdom": 15, "MStamina": 3, "MVeins": 2},
                   off=["MWisdom"]),
    "Foraging": dict(level=60, xp=200000000, nodes={"FSpeed": 10, "FFortune": 20, "FVigor": 5, "FSap": 2, "FCoins": 1, "FSpread": 3,
                                                   "FSpeed2": 4, "FFeller": 5}, off=["FSap"]),
    "Farming": dict(level=20, xp=90000, nodes={"AFortune": 3, "ASeeds": 1, "AHearty": 2}, off=[]),
    "Cooking": dict(level=10, xp=30000, nodes={"CGourmet": 25, "CBatch": 1}, off=["CBatch"]),
    "Acrobatics": dict(level=45, xp=5000000, nodes={"RSpeed": 25, "RJump": 4, "RStamina": 2, "RDodge": 1, "RDouble": 3, "RFall2": 2,
                                                    "RStamina3": 1}, off=["RDouble"]),
    "Exploration": dict(level=5, xp=4000, nodes={"EHeart": 2}, off=[]),
}


def st(name, tree=0, sel=1, msg="", armed=False, levels="profile", xps="profile", nodes=None, off=None, bad=False, en_off=(),
       extra_dust=0, extra_tokens=0, known=None, respec_coins=0, reads=None):
    """one page state (the 0.2.5 shape + reads = {mod: csv} reader flags put on the bridge as tree:reads:<mod>)"""
    if nodes is None:
        nodes = dict(("%s.%s" % (tn, k), v) for tn, p in PROFILES.items() for k, v in p["nodes"].items())
    if off is None:
        off = ["%s.%s" % (tn, k) for tn, p in PROFILES.items() for k in p["off"]]
    if levels == "profile":
        levels = dict((tn, p["level"]) for tn, p in PROFILES.items())
    if xps == "profile":
        xps = dict((tn, p["xp"]) for tn, p in PROFILES.items())
    return dict(name=name, tree=tree, sel=sel, msg=msg, armed=armed, levels=levels, xps=xps, nodes=nodes, off=list(off), bad=bad,
                en_off=list(en_off), extra_dust=extra_dust, extra_tokens=extra_tokens, known=known, respec_coins=respec_coins,
                reads=reads)


RESULT_TEXTS = [  # (message, the result colour kind infoColor must give it)
    ("Unlocked Gem Finder!", "success"), ("Mining Speed is now level 11", "success"), ("Tree Feller is now level 6 - MAX", "success"),
    ("Heavy Pick turned off - its level is kept", "success"), ("Heavy Pick turned on", "success"),
    ("Respec done - every Mining token and all your Mining Dust are back", "success"),
    ("Click Respec again within 10 s to reset the whole Acrobatics tree (everything spent comes back)", "warning"),
    ("Node S7 of the Exploration tree is coming later - Skyy designs the rest of this draft tree later", "info"),
    ("Needs 1,234,567 more Foraging Dust", "error"), ("Vein Burst needs Mining 60", "error"), ("Mining Fortune is already maxed", "error"),
    ("You can respec Mining again in 10 min", "error"), ("SkyySkills is not installed - there is no skills page", "error"),
    ("A respec costs 5,000 coins - you do not have enough", "error"), ("", "info"),
    ("Your Exploration balance is negative (costs changed) - respec first, it is free right now", "error")]
NEW_RESULT_TEXTS = [  # 0.3 only (the old jar has no such message)
    ("Extra Brew is coming with SkyySkills - it does nothing until that mod applies it, so it cannot be unlocked yet", "info"),
    ("Smelter's Luck is coming with SkyySkills or SkyySacks - it does nothing until that mod applies it, so it cannot be levelled up yet", "info"),
    ("Unlocked Deep Reserves!", "success"), ("Unlock a Tier I node first", "error")]

STATES = [st("grid %s S%d" % (tn, s), tree=t, sel=s) for t, tn in enumerate(TREES_025) for s in range(1, 13)]
STATES += [
    st("no skills", levels=None, xps=None),
    st("no xp bridge", tree=1, sel=12, xps=None),
    st("unreadable file", tree=2, sel=4, bad=True, nodes={}, off=[]),
    st("negative balance", tree=0, sel=5, levels={"Mining": 5}, xps={"Mining": 100}),
    st("armed respec acrobatics", tree=4, sel=7, armed=True, msg=RESULT_TEXTS[6][0]),
    st("armed respec exploration", tree=5, sel=1, armed=True),
    st("huge dust and tokens", tree=1, sel=12, extra_dust=123456789012, extra_tokens=1000),
    st("server-disabled node", tree=0, sel=10, en_off=["Mining.MHeavy"]),
    st("exploration unknown", tree=5, sel=2, known="Mining:34,Foraging:60,Farming:20,Cooking:10,Acrobatics:45"),
    st("tree out of range", tree=9, sel=0),
    st("node out of range", tree=3, sel=13),
    st("level 100 all maxed", tree=0, sel=12, levels={"Mining": 100}, xps={"Mining": 10 ** 12},
       nodes=dict(("Mining." + k, v) for k, v in {"MSpeed": 25, "MFortune": 20, "MWisdom": 15, "MStamina": 10, "MGems": 10, "MVeins": 15,
                                                    "MCoins": 10, "MSpread": 10, "MRunner": 10, "MHeavy": 20, "MBars": 10, "MVein": 5}.items()),
       off=[]),
    st("fresh level 0", tree=2, sel=1, levels={"Farming": 0}, xps={"Farming": 0}, nodes={}, off=[]),
]
STATES += [st("result %d" % n, tree=n % 6, sel=1 + n % 12, msg=m) for n, (m, _k) in enumerate(RESULT_TEXTS)]
# 0.3 only: the new trees (levels for all eight trees; the 0.2.5 profiles stay for the old trees)
LV8 = dict((tn, p["level"]) for tn, p in PROFILES.items())
LV8.update({"Alchemy": 40, "Smithing": 45})
XP8 = dict((tn, p["xp"]) for tn, p in PROFILES.items())
XP8.update({"Alchemy": 3000000, "Smithing": 4000000})
OWN_NONE = {"Alchemy.PMana": 3, "Smithing.SHealth": 2}
OWN_ALL = {"Alchemy.PExtra": 5, "Alchemy.PMana": 3, "Alchemy.PHealth": 2, "Alchemy.PMaster": 1, "Smithing.SRarity": 4, "Smithing.SSmelt": 20,
           "Smithing.SReforge": 1, "Smithing.SHealth": 2, "Smithing.SQuick": 3}
NEW_STATES = []
for _fl, _reads, _own in (("no readers", None, OWN_NONE), ("all readers", READS_ALL, OWN_ALL), ("owned but coming", None, OWN_ALL),
                          ("partial", {"SkyySacks": "Smithing.SSmelt", "SkyyGear": " Smithing.SRarity , Smithing.SIdent"}, OWN_NONE)):
    for _t in (6, 7):
        for _s in range(1, 13):
            NEW_STATES.append(st("%s %s S%d" % (_fl, TREES[_t], _s), tree=_t, sel=_s, levels=LV8, xps=XP8, nodes=dict(_own), off=[],
                                 reads=_reads, extra_dust=0))
NEW_STATES += [st("new result %d" % n, tree=6 + n % 2, sel=1 + n, msg=m, levels=LV8, xps=XP8, nodes=dict(OWN_NONE), off=[])
               for n, (m, _k) in enumerate(NEW_RESULT_TEXTS)]
NEW_STATES += [st("alchemy level 0", tree=6, sel=4, levels={"Alchemy": 0}, xps={"Alchemy": 0}, nodes={}, off=[]),
               st("smithing no skills", tree=7, sel=6, levels=None, xps=None, nodes={}, off=[]),
               st("smithing owned off", tree=7, sel=6, levels=LV8, xps=dict(XP8, Smithing=10000000), nodes={"Smithing.SHealth": 15}, off=["Smithing.SHealth"])]

# ---- D: click sequences on the 0.2.5 trees (payloads as the client sends them: {"a":"<payload>"})
CLICKS = [
    ("mining buy toggle respec", st("c1", tree=0, sel=1, respec_coins=500),
     ["trnode5", "trbuy", "trbuy", "trtoggle", "trtoggle", "trnode12", "trbuy", "trnode3", "trbuy", "trtoggle", "trrespec", "trrespec",
      "trrespec", "trrespec", "trtab4", "trnode7", "trbuy", "trtoggle", "trtab9", "trnode13", "junk", "trback"]),
    ("foraging feller", st("c2", tree=1, sel=12), ["trbuy", "trnode10", "trbuy", "trbuy", "trnode12", "trbuy", "trtab1", "trnode11", "trbuy"]),
    ("exploration draft slots", st("c3", tree=5, sel=6), ["trbuy", "trtoggle", "trnode4", "trbuy", "trrespec", "trrespec", "trnode2", "trbuy"]),
    ("no skills", st("c4", levels=None, xps=None), ["trback", "trbuy", "trnode2", "trbuy", "trrespec", "trrespec"]),
    ("unreadable file", st("c5", tree=2, bad=True, nodes={}, off=[]), ["trbuy", "trtoggle", "trrespec", "trrespec", "trtab0", "trbuy"]),
    ("negative balance respec", st("c6", tree=0, sel=1, levels={"Mining": 5}, xps={"Mining": 100}, respec_coins=500),
     ["trbuy", "trrespec", "trrespec", "trbuy"]),
]
# ---- N: click sequences on the new trees (0.3 only). Steps "!reads:<Mod>=<csv>" / "!unreads:<Mod>" change the reader flags.
# Each expected entry: (step index, the message, {node key: level} after it)
NEW_CLICKS = [
    ("alchemy without readers", st("n1", tree=6, sel=1, levels={"Alchemy": 12}, xps={"Alchemy": 50000}, nodes={}, off=[], extra_dust=10 ** 8),
     ["trbuy", "trnode4", "trbuy", "trbuy", "trbuy", "trtoggle", "trtoggle", "trnode2", "trbuy", "trtab6", "trrespec", "trrespec", "trtab7", "trnode6", "trbuy"],
     [(0, NEW_RESULT_TEXTS[0][0], {"Alchemy.PExtra": 0}), (2, "Unlocked Deep Reserves!", {"Alchemy.PMana": 1}),
      (3, "Deep Reserves is now level 2", {"Alchemy.PMana": 2}), (4, "Deep Reserves is now level 3", {"Alchemy.PMana": 3}),
      (5, "Deep Reserves turned off - its level is kept", {}), (6, "Deep Reserves turned on", {}),
      (8, "Long Brew is coming with SkyySkills - it does nothing until that mod applies it, so it cannot be unlocked yet", {"Alchemy.PDur": 0}),
      (11, "Respec done - every Alchemy token and all your Alchemy Dust are back", {"Alchemy.PMana": 0}),
      (14, "Forge Hardened needs Smithing 20", {"Smithing.SHealth": 0})]),
    ("alchemy level gate", st("n2", tree=6, sel=4, levels={"Alchemy": 9}, xps={"Alchemy": 9000}, nodes={}, off=[]),
     ["trbuy"], [(0, "Deep Reserves needs Alchemy 10", {"Alchemy.PMana": 0})]),
    ("smithing with readers", st("n3", tree=7, sel=4, levels={"Smithing": 25}, xps={"Smithing": 600000}, nodes={}, off=[],
                                 extra_dust=10 ** 9, reads=READS_ALL),
     ["trbuy", "trnode1", "trbuy", "trbuy", "trnode4", "trbuy", "trnode6", "trbuy", "!unreads:SkyyGear", "trnode1", "trbuy",
      "!reads:SkyyGear=" + READS_ALL["SkyyGear"], "trbuy", "trrespec", "trrespec"],
     [(0, "Unlock a Tier I node first", {"Smithing.SReforge": 0}), (2, "Unlocked Fine Craft!", {"Smithing.SRarity": 1}),
      (3, "Fine Craft is now level 2", {"Smithing.SRarity": 2}), (5, "Unlocked Steady Hand!", {"Smithing.SReforge": 1}),
      (7, "Unlocked Forge Hardened!", {"Smithing.SHealth": 1}),
      (10, "Fine Craft is coming with SkyyGear - it does nothing until that mod applies it, so it cannot be levelled up yet", {"Smithing.SRarity": 2}),
      (12, "Fine Craft is now level 3", {"Smithing.SRarity": 3}),
      (14, "Respec done - every Smithing token and all your Smithing Dust are back", {"Smithing.SRarity": 0, "Smithing.SReforge": 0, "Smithing.SHealth": 0})]),
    ("smithing partial flags", st("n4", tree=7, sel=2, levels={"Smithing": 25}, xps={"Smithing": 600000}, nodes={}, off=[],
                                  extra_dust=10 ** 9, reads={"SkyySacks": "Smithing.SSmelt"}),
     ["trbuy", "trnode8", "trbuy", "trnode6", "trbuy", "trnode3", "trbuy"],
     [(0, "Unlocked Smelter's Luck!", {"Smithing.SSmelt": 1}),
      (2, "Quick Forge is coming with SkyySacks - it does nothing until that mod applies it, so it cannot be unlocked yet", {"Smithing.SQuick": 0}),
      (4, "Unlocked Forge Hardened!", {"Smithing.SHealth": 1}),
      (6, "Smithing Wisdom is coming with SkyySkills - it does nothing until that mod applies it, so it cannot be unlocked yet", {"Smithing.SWisdom": 0})]),
]


# ============================================================================================ K: the class tree (0.3 part 2) - the model
# An independent re-statement of research/Skill-Trees-2-Spec.md 5-7 + Skyy's answers (the 37-node map, the unlock rule, integrity,
# the stat kinds): the Java tables and every rendered cell must agree with it. Nothing here reads the build script.
CLASSES = ["Archer", "Warrior", "Mage", "Berserker", "Priest"]
CSKILL = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity"]
CMAGIC = {"Mage": True, "Priest": True}
NT_CLASS = 8                                                     # the class tab's tree index (TreeDefs.NT)
# id, AP, parents, need, lock, lane, lane count, page, row, col, role (0 passive, 1 pick, 2 ability, 3/4 modifier A/B, 5 lane, 6 core, 7 element, 8 capstone)
CT = [("ROOT", 1, [], None, None, 0, 0, 0, 0, 4, 0), ("P1", 1, ["ROOT"], None, None, 0, 0, 0, 1, 4, 0),
      ("A1", 1, ["P1"], None, None, 0, 0, 0, 1, 2, 2), ("M1A", 1, ["A1"], "A1", None, 0, 0, 0, 1, 1, 3), ("M1B", 2, ["M1A"], "A1", None, 0, 0, 0, 1, 0, 4),
      ("A2", 1, ["P1"], None, None, 0, 0, 0, 1, 6, 2), ("M2A", 1, ["A2"], "A2", None, 0, 0, 0, 1, 7, 3), ("M2B", 2, ["M2A"], "A2", None, 0, 0, 0, 1, 8, 4),
      ("P2", 1, ["P1"], None, None, 0, 0, 0, 3, 4, 0),
      ("A3", 1, ["P2"], None, None, 0, 0, 0, 3, 2, 2), ("M3A", 1, ["A3"], "A3", None, 0, 0, 0, 3, 1, 3), ("M3B", 2, ["M3A"], "A3", None, 0, 0, 0, 3, 0, 4),
      ("A4", 1, ["P2"], None, None, 0, 0, 0, 3, 6, 2), ("M4A", 1, ["A4"], "A4", None, 0, 0, 0, 3, 7, 3), ("M4B", 2, ["M4A"], "A4", None, 0, 0, 0, 3, 8, 4),
      ("X1", 1, ["P2"], None, "X2", 0, 0, 0, 4, 3, 1), ("X2", 1, ["P2"], None, "X1", 0, 0, 0, 4, 5, 1), ("P3", 1, ["X1", "X2"], None, None, 0, 0, 0, 5, 4, 0),
      ("P4", 1, ["P3"], None, None, 0, 0, 1, 0, 4, 0)]
for _ln, (_pre, _col) in enumerate((("L", 1), ("C", 4), ("R", 7))):
    CT += [(_pre + "1", 1, ["P4"], None, None, _ln + 1, 0, 1, 1, _col, 5), (_pre + "2", 1, [_pre + "1"], None, None, _ln + 1, 0, 1, 2, _col, 5),
           (_pre + "3", 2, [_pre + "2"], None, None, _ln + 1, 0, 1, 3, _col, 5), (_pre + "4", 3, [_pre + "3"], None, None, _ln + 1, 3, 1, 4, _col, 6),
           (_pre + "E", 3, [_pre + "3"], None, None, _ln + 1, 3, 1, 3, _col - 1 if _ln == 0 else _col + 1, 7),
           (_pre + "S", 4, [_pre + "4"], None, None, _ln + 1, 4, 1, 5, _col, 8)]
CT_ID = [n[0] for n in CT]
CT_IDX = dict((n[0], k) for k, n in enumerate(CT))
CT_LINKS = [(p, n[0]) for n in CT for p in n[2] if CT[CT_IDX[p]][7] == n[7]]        # 36 drawn links (P3 > P4 crosses the page break)
assert len(CT) == 37 and len(CT_LINKS) == 36 and sum(n[1] for n in CT) == 65
UNIT = {"H": 4, "S": 2, "M": 5, "R": 5}
SPINE = {False: {"ROOT": ("H", 4), "P1": ("S", 2), "P2": ("H", 4), "X1": ("S", 3), "X2": ("H", 8), "P3": ("R", 5), "P4": ("S", 2)},
         True: {"ROOT": ("H", 4), "P1": ("M", 5), "P2": ("R", 5), "X1": ("M", 8), "X2": ("H", 8), "P3": ("H", 4), "P4": ("R", 5)}}
LANES = {"Archer": (("Boltslinger", "SSSS"), ("Trapper", "HHHH"), ("Sharpshooter", "SXXX")),
         "Warrior": (("Fallen", "SSSS"), ("Battle Monk", "SSHH"), ("Paladin", "HHHH")),
         "Mage": (("Riftwalker", "RRRR"), ("Light Bender", "HHHH"), ("Arcanist", "MMMM")),
         "Berserker": (("Bloodbound", "HHHH"), ("Smasher", "SSSS"), ("Warbringer", "SSHH")),
         "Priest": (("Smiter", "MMMM"), ("Healer", "RRRR"), ("Guardian", "HHHH"))}
XBOW_AMT = {"R2": 2, "R3": 2, "R4": 30}
XBOW_MIN = {"R2": 15, "R3": 15, "R4": 50}
KIND_WORD = {"H": "Vitality", "S": "Might", "M": "Reservoir", "R": "Focus"}


def ct_kind(cn, nid):
    """(kind letter or None, amount, name) of node nid for class cn - the spec's units and lanes"""
    n = CT[CT_IDX[nid]]
    role, lane = n[10], n[5]
    if role in (0, 1):
        k, amt = SPINE[CMAGIC.get(cn, False)][nid]
        return k, amt, None
    if role in (5, 6):
        lname, kinds = LANES[cn][lane - 1]
        k = kinds[int(nid[1]) - 1]
        if k == "X":
            return "X", XBOW_AMT[nid], {"R2": "Bolt Rack I", "R3": "Bolt Rack II", "R4": "Holstered Reload"}[nid]
        return k, UNIT[k] * [1, 1, 2, 3][int(nid[1]) - 1], lname + " " + ["I", "II", "III", "IV"][int(nid[1]) - 1]
    return None, 0, None


def m_listed(reads, mod, key):
    for name in ("tree:reads:" + mod, {"SkyyGear": "gear:tree:readers", "SkyySkills": "skill:tree:readers", "SkyySacks": "sack:tree:readers"}.get(mod)):
        csv = (reads or {}).get(name)
        if csv is not None and key in [x.strip() for x in csv.split(",")]:
            return True
    return False


def m_coming(cn, nid, reads, regen):
    role = CT[CT_IDX[nid]][10]
    if role in (2, 3, 4, 7, 8):
        return "runes (Hytale 0.7)" if role != 7 else "SkyyGear's elemental stats (later)"
    k = ct_kind(cn, nid)[0]
    if k == "S":
        return "" if m_listed(reads, "SkyyGear", "gear:extras") else "SkyyGear"
    if k == "X":
        return "" if m_listed(reads, "SkyySkills", "Class.%s.%s" % (cn, nid)) else "SkyySkills"
    if k == "R":
        return "" if regen else "SkyySkills"
    return ""


def m_intact(own, con_off=()):
    """the intact set (spec 5 integrity): reachable from ROOT over owned, enabled, non-coming-slot nodes; a Need must be intact, a Lock
    must not be owned; iterated to a fixpoint"""
    ok = set(i for i in own if i not in con_off and CT[CT_IDX[i]][10] not in (2, 3, 4, 7, 8))
    while True:
        it = set()
        if "ROOT" in ok:
            it.add("ROOT")
            ch = True
            while ch:
                ch = False
                for n in CT:
                    if n[0] in ok and n[0] not in it and any(p in it for p in n[2]):
                        it.add(n[0])
                        ch = True
        drop = set(i for i in it if (CT[CT_IDX[i]][3] and CT[CT_IDX[i]][3] not in it) or (CT[CT_IDX[i]][4] and CT[CT_IDX[i]][4] in own))
        if not drop:
            return it
        ok -= drop


def m_ap(lvl, first=1, every=2, mx=50, extra=0):
    return extra + (0 if lvl < 1 else min(mx, first + lvl // every))


def m_spent(it, ap_of=None):
    return sum((ap_of or {}).get(i, CT[CT_IDX[i]][1]) for i in it)


def m_reason(own, it, cn, nid, lvl, ap_free, reads=None, regen=False, con_off=(), cmin=None, ap_of=None):
    """0 fine, 1 off, 2 coming, 3 parent, 4 need, 5 lock, 6 lane, 7 level, 8 negative, 9 AP, 10 owned (the Java's order)"""
    n = CT[CT_IDX[nid]]
    if nid in own:
        return 10
    if nid in con_off:
        return 1
    if m_coming(cn, nid, reads, regen):
        return 2
    if not (nid == "ROOT" or any(p in it for p in n[2])):
        return 3
    if n[3] and n[3] not in it:
        return 4
    if n[4] and n[4] in own:
        return 5
    if n[6] and sum(1 for i in it if CT[CT_IDX[i]][5] == n[5]) < n[6]:
        return 6
    mn = (cmin or {}).get(nid, XBOW_MIN.get(nid, 0) if cn == "Archer" else 0)
    if max(lvl, 0) < mn:
        return 7
    if ap_free < 0:
        return 8
    if ap_free < (ap_of or {}).get(nid, n[1]):
        return 9
    return 0


def m_state(own, it, cn, nid, lvl, ap_free, **kw):
    if nid in own:
        return 2 if nid in it else 4
    if m_coming(cn, nid, kw.get("reads"), kw.get("regen", False)):
        return 3
    return 1 if m_reason(own, it, cn, nid, lvl, ap_free, **kw) == 0 else 0


def m_card(own, it, cn, nid, lvl, ap_free, **kw):
    stt = m_state(own, it, cn, nid, lvl, ap_free, **kw)
    n = CT[CT_IDX[nid]]
    cost = (kw.get("ap_of") or {}).get(nid, n[1])
    if stt == 2:
        return "Owned"
    if stt == 3:
        return "Coming"
    if stt == 4:
        return "Locked"
    if stt == 1:
        return "Unlock %d AP" % cost if cost <= 9 else "Unlock"
    why = m_reason(own, it, cn, nid, lvl, ap_free, **kw)
    return {1: "Turned off", 3: ("Locked" if len(n[2]) != 1 else "Needs " + n[2][0]), 4: "Needs " + str(n[3]), 5: "Pick one", 6: "Lane %d" % n[6],
            7: "Lv %d" % (kw.get("cmin") or {}).get(nid, XBOW_MIN.get(nid, 0)), 8: "Respec", 9: "Need %d AP" % cost}.get(why, "Locked")


def m_gold_links(it):
    return [(a, b) for a, b in CT_LINKS if a in it and b in it]


SPINE_OWN = ["ROOT", "P1", "P2", "X1", "P3", "P4", "L1", "L2"]          # the probe page's sample (8 AP)
READS_CLASS = {"tree:reads:SkyyGear": "gear:extras", "tree:reads:SkyySkills": "Class.Archer.R2,Class.Archer.R3,Class.Archer.R4"}
READS_ALIAS = {"gear:tree:readers": "Smithing.SRarity,gear:extras", "skill:tree:readers": "Class.Archer.R2"}


def cst(name, cls="Archer", lvl=23, own=None, cfg=None, tree=NT_CLASS, cpage=0, csel=0, msg="", armed=False, reads=None, regen=False,
        probe=False, undo=(), con_off=(), cmin=None, levels=True, pcls=None, bad=False, coins=True, respec_at=0, camt=None, undo_raw=()):
    """a class page state: the player's class (bridge class:<uuid>; pcls = profile:class:<uuid>), the class skill level, the owned
    node ids, TreeCfg class fields (cfg), reader flags (bridge keys -> csv), the Mana Regen registry stand-in (regen), probe mode, the
    Undo list, server-disabled nodes (con_off = ids), class.minLevel overrides, SkyySkills present (levels), an unreadable file (bad)"""
    c = {"CLASS_ON": True}
    c.update(cfg or {})
    lv = None if not levels else dict((tn, p["level"]) for tn, p in PROFILES.items())
    xp = None if not levels else dict((tn, p["xp"]) for tn, p in PROFILES.items())
    if lv is not None:
        lv.update(dict((sk, lvl) for sk in CSKILL))
    return dict(name=name, cls=cls, pcls=pcls, lvl=lvl, own=list(own if own is not None else SPINE_OWN), cfg=c, tree=tree, cpage=cpage, csel=csel,
                msg=msg, armed=armed, reads=dict(reads or {}), regen=regen, probe=probe, undo=list(undo), con_off=list(con_off), cmin=dict(cmin or {}),
                levels=lv, xps=xp, bad=bad, coins=coins, respec_at=respec_at, camt=dict(camt or {}), undo_raw=list(undo_raw))


CLASS_RESULT_TEXTS = [  # (message, colour kind) - the class tree's answers through infoColor
    ("Unlocked Root! 1 AP spent - 11 left", "success"), ("Unlocked Boltslinger I! 1 AP spent - 3 left (probe - not saved)", "success"),
    ("Undo done - Boltslinger I is open again and its 1 AP are back", "success"),
    ("Respec done - every Ability Point of your Archer tree is back (2,300 coins paid)", "success"),
    ("Click Respec again within 10 s to reset your whole Archer tree - every Ability Point comes back - it costs 2,300 coins (Archery 23 x 100)", "warning"),
    ("Ability I is coming with runes (Hytale 0.7) - it cannot be unlocked yet", "info"),
    ("Might I is coming with SkyyGear - it cannot be unlocked yet", "info"),
    ("Bulwark cannot be taken together with Edge - pick one of the two (a respec resets the choice)", "error"),
    ("Boltslinger IV needs 3 nodes of the Boltslinger lane first (you own 2)", "error"),
    ("A class respec costs 2,300 coins - you do not have enough", "error"),
    ("Might I cannot be undone - Vitality I (P2) still needs it", "error"),
    ("Choose a class first (/class, or create a profile) - your class tree opens here", "error")]
CLASS_STATES = []
for _ci, _cn in enumerate(CLASSES):
    for _pg in (0, 1):
        CLASS_STATES.append(cst("class %s page %d" % (_cn, _pg), cls=_cn, cpage=_pg, csel=0 if _pg == 0 else 18))
CLASS_STATES += [
    cst("class on mining tab", tree=0),                                                   # the class tab in row 2 of a template page
    cst("class off mining tab", tree=0, cfg={"CLASS_ON": False}),                         # no tab, no binding
    cst("class off requested", tree=NT_CLASS, cfg={"CLASS_ON": False}),                  # falls back to Mining
    cst("class readers all", reads=READS_CLASS, regen=True, own=SPINE_OWN + ["R1", "R2"], lvl=40, csel=CT_IDX["R3"], cpage=1),
    cst("class readers alias", reads=READS_ALIAS, regen=True, csel=1),
    cst("class no readers", csel=1),                                                      # P1 Might I: Coming with SkyyGear
    cst("class sel coming slot", csel=CT_IDX["A1"]),
    cst("class sel owned", csel=CT_IDX["P2"]),
    cst("class sel pick one", csel=CT_IDX["X2"]),
    cst("class sel unlockable", csel=CT_IDX["C1"], cpage=1, reads=READS_CLASS, regen=True),
    cst("class lane gate", cpage=1, csel=CT_IDX["L4"], reads=READS_CLASS, regen=True),   # L1 + L2 owned: L4 / LE need 3 lane nodes
    cst("class level gate", cpage=1, csel=CT_IDX["R2"], own=SPINE_OWN + ["R1"], lvl=14, reads=READS_CLASS, regen=True, cfg={"CLASS_ON": True, "C_EXTRA_AP": 2}),
    cst("class level ok", cpage=1, csel=CT_IDX["R2"], own=SPINE_OWN + ["R1"], lvl=15, reads=READS_CLASS, regen=True, cfg={"CLASS_ON": True, "C_EXTRA_AP": 2}),
    cst("class min override", cpage=1, csel=CT_IDX["R2"], own=SPINE_OWN + ["R1"], lvl=15, reads=READS_CLASS, regen=True, cmin={"R2": 30}, cfg={"CLASS_ON": True, "C_EXTRA_AP": 2}),
    cst("class no class", cls=None),
    cst("class unknown class", cls="Assassin"),
    cst("class profile class wins", cls="Archer", pcls="Mage"),
    cst("class no skills", levels=False),
    cst("class negative balance", cfg={"CLASS_ON": True, "AP_MAX": 3}),
    cst("class extra ap", own=[], cfg={"CLASS_ON": True, "C_EXTRA_AP": 5}, lvl=0),
    cst("class broken chain", own=["P1", "P2", "X1"]),
    cst("class both picks", own=["ROOT", "P1", "P2", "X1", "X2", "P3"]),
    cst("class node off", con_off=["P2"], csel=CT_IDX["P2"]),
    cst("class undo ready", undo=[CT_IDX["L2"]], cpage=1, csel=CT_IDX["L2"]),
    cst("class undo off", undo=[CT_IDX["L2"]], cfg={"CLASS_ON": True, "C_UNDO": False}),
    cst("class armed respec", armed=True, msg=CLASS_RESULT_TEXTS[4][0]),
    cst("class probe off", probe=True, cfg={"CLASS_ON": False}),
    cst("class probe page 2", probe=True, cfg={"CLASS_ON": False}, cpage=1, csel=18),
    cst("class probe mage", probe=True, cls="Mage", cfg={"CLASS_ON": False}),
    cst("class bad file", bad=True),
    cst("class all owned", own=[i for i in CT_ID if CT[CT_IDX[i]][10] in (0, 1, 5, 6) and i != "X2"], lvl=100, reads=READS_CLASS, regen=True, cpage=1),
    cst("class ap 50 of 50", own=[], lvl=100),
    # fix round: the element / capstone / P3 / P4 detail lines (2-line Next label), the live Amount, the live AP rows
    cst("class sel element L", cpage=1, csel=CT_IDX["LE"]),
    cst("class sel element C", cpage=1, csel=CT_IDX["CE"], cls="Mage"),
    cst("class sel element R", cpage=1, csel=CT_IDX["RE"], cls="Berserker"),
    cst("class sel capstone", cpage=1, csel=CT_IDX["RS"], cls="Warrior"),
    cst("class sel crossbow", cpage=1, csel=CT_IDX["R4"], own=SPINE_OWN + ["R1", "R2", "R3", "R4"], lvl=60, reads=READS_CLASS, regen=True),
    cst("class sel p3", csel=CT_IDX["P3"]),
    cst("class sel p4", cpage=1, csel=CT_IDX["P4"]),
    cst("class amount override", csel=0, camt={"ROOT": 10}),
    cst("class mage amount", cls="Mage", csel=CT_IDX["P2"], regen=True),
    cst("class ap rows", cfg={"CLASS_ON": True, "AP_FIRST": 2, "AP_EVERY": 5, "AP_MAX": 30}),
] + [cst("class result %d" % n, msg=m) for n, (m, _k) in enumerate(CLASS_RESULT_TEXTS)]
# ---- K: click sequences on the class tab (payloads as the client sends them). Steps "!reads:<key>=<csv>" / "!unreads:<key>" change the
# bridge, "!coins:false" / "!coins:none" / "!coins:true" the coins stand-in. Expected: (step, message, {node id: owned}, extra)
CLASS_CLICKS = [
    ("class buy chain", cst("k1", tree=0, own=[], regen=True),
     ["trtab8", "trc1", "trbuy", "trc2", "trbuy", "!reads:tree:reads:SkyyGear=gear:extras", "trbuy", "trc9", "trbuy", "trc16", "trbuy", "trc17", "trbuy",
      "trc18", "trbuy", "trpgn", "trbuy", "trc20", "trbuy", "trc23", "trbuy", "trundo", "trundo", "trc3", "trbuy", "trpgp", "trrespec", "trrespec"],
     [(2, "Unlocked Root! 1 AP spent - 11 left", {"ROOT": True}), (4, "Might I is coming with SkyyGear - it cannot be unlocked yet", {"P1": False}),
      (6, "Unlocked Might I! 1 AP spent - 10 left", {"P1": True}), (8, "Unlocked Vitality I! 1 AP spent - 9 left", {"P2": True}),
      (10, "Unlocked Edge! 1 AP spent - 8 left", {"X1": True}),
      (12, "Bulwark cannot be taken together with Edge - pick one of the two (a respec resets the choice)", {"X2": False}),
      (14, "Unlocked Focus I! 1 AP spent - 7 left", {"P3": True}), (16, "Unlocked Might II! 1 AP spent - 6 left", {"P4": True}),
      (18, "Unlocked Boltslinger I! 1 AP spent - 5 left", {"L1": True}),
      (20, "Boltslinger IV needs Boltslinger III (L3) first", {"L4": False}),
      (21, "Undo done - Boltslinger I is open again and its 1 AP are back", {"L1": False}),
      (22, "Undo done - Might II is open again and its 1 AP are back", {"P4": False}),
      (24, "Ability I is coming with runes (Hytale 0.7) - it cannot be unlocked yet", {"A1": False}),
      (26, "Click Respec again within 10 s to reset your whole Archer tree - every Ability Point comes back - it costs 2,300 coins (Archery 23 x 100)", {"ROOT": True}),
      (27, "Respec done - every Ability Point of your Archer tree is back (2,300 coins paid)", {"ROOT": False, "P1": False, "P2": False, "X1": False, "P3": False})]),
    ("class respec refusals", cst("k2", own=SPINE_OWN, regen=True, reads=READS_CLASS),
     ["!coins:false", "trrespec", "trrespec", "!coins:none", "trrespec", "trrespec", "!coins:true", "trrespec", "trrespec", "trrespec", "trrespec"],
     [(2, "A class respec costs 2,300 coins - you do not have enough", {"ROOT": True}),
      (5, "A class respec costs 2,300 coins but SkyyCoins is not loaded", {"ROOT": True}),
      (8, "Respec done - every Ability Point of your Archer tree is back (2,300 coins paid)", {"ROOT": False, "L2": False}),
      (10, "Nothing to respec in your Archer tree", {})]),
    ("class respec cooldown", cst("k3", own=["ROOT"], regen=True, respec_at=-1),
     ["trrespec", "trrespec"], [(1, "You can respec your Archer tree again in 10 min", {"ROOT": True})]),
    ("class negative respec free", cst("k4", own=SPINE_OWN, cfg={"CLASS_ON": True, "AP_MAX": 3}),
     ["trc26", "trbuy", "trrespec", "trrespec"],
     [(1, "Your Ability Point balance is negative (the AP rules changed) - respec first, it is free right now", {"C1": False}),
      (3, "Respec done - every Ability Point of your Archer tree is back", {"ROOT": False})]),
    ("class undo blocked", cst("k5", own=[], reads=READS_CLASS, regen=True),
     ["trbuy", "trc2", "trbuy", "trc9", "trbuy", "trundo", "trundo", "trundo", "trundo"],
     [(0, "Unlocked Root! 1 AP spent - 11 left", {"ROOT": True}), (4, "Unlocked Vitality I! 1 AP spent - 9 left", {"P2": True}),
      (5, "Undo done - Vitality I is open again and its 1 AP are back", {"P2": False}),
      (6, "Undo done - Might I is open again and its 1 AP are back", {"P1": False}),
      (7, "Undo done - Root is open again and its 1 AP are back", {"ROOT": False}),
      (8, "Nothing to undo - only unlocks made while this page is open can be undone", {})]),
    ("class undo keeps parents", cst("k6", own=[], reads=READS_CLASS, regen=True),
     ["trbuy", "trc2", "trbuy", "trc9", "trbuy", "!undo:pop", "trundo"],
     [(4, "Unlocked Vitality I! 1 AP spent - 9 left", {"P2": True}), (6, "Might I cannot be undone - Vitality I (P2) still needs it", {"P1": True, "P2": True})]),
    ("class undo switched off", cst("k7", own=[], regen=True, cfg={"CLASS_ON": True, "C_UNDO": False}),
     ["trbuy", "trundo"], [(0, "Unlocked Root! 1 AP spent - 11 left", {"ROOT": True}), (1, "Undo is switched off on this server", {"ROOT": True})]),
    ("class lane and level", cst("k8", own=SPINE_OWN, lvl=14, reads=READS_CLASS, regen=True, cpage=1, cfg={"CLASS_ON": True, "C_EXTRA_AP": 4}),
     ["trc22", "trbuy", "trc23", "trbuy", "trc24", "trbuy", "trc32", "trbuy", "trc33", "trbuy", "trc25", "trbuy"],
     [(1, "Unlocked Boltslinger III! 2 AP spent - 2 left", {"L3": True}), (3, "Boltslinger IV needs 3 AP - you have 2", {"L4": False}),
      (5, "Boltslinger Element is coming with SkyyGear's elemental stats (later) - it cannot be unlocked yet", {"LE": False}),
      (7, "Unlocked Sharpshooter I! 1 AP spent - 1 left", {"R1": True}), (9, "Bolt Rack I needs Archery 15 (you are 14)", {"R2": False}),
      (11, "Boltslinger Capstone is coming with runes (Hytale 0.7) - it cannot be unlocked yet", {"LS": False})]),
    ("class pages and cells", cst("k9", own=SPINE_OWN, regen=True),
     ["trpgp", "trpgn", "trpgn", "trc1", "trc19", "trpgp", "trc37", "trtab0", "trtab8"],
     [(0, "", {}, {"cpage": 0, "csel": 0, "tree": 8}), (1, "", {}, {"cpage": 1, "csel": 18}), (2, "", {}, {"cpage": 1, "csel": 18}),
      (3, "", {}, {"cpage": 0, "csel": 0}), (4, "", {}, {"cpage": 1, "csel": 18}), (5, "", {}, {"cpage": 0, "csel": 0}),
      (6, "", {}, {"cpage": 1, "csel": 36}), (7, "", {}, {"tree": 0}), (8, "", {}, {"tree": 8})]),
    ("class off clicks", cst("k10", tree=NT_CLASS, own=["ROOT"], cfg={"CLASS_ON": False}),
     ["trbuy", "trtab8", "trc1", "trundo"], []),
    ("class probe clicks", cst("k11", probe=True, cfg={"CLASS_ON": False}, own=[], lvl=99, reads=READS_CLASS, regen=True),
     ["trc22", "trbuy", "trc23", "trbuy", "trundo", "trrespec", "trrespec", "trc1", "trbuy"],
     [(1, "Unlocked Boltslinger III! 2 AP spent - 6 left (probe - not saved)", {}), (3, "Unlocked Boltslinger IV! 3 AP spent - 3 left (probe - not saved)", {}),
      (4, "Undo done - Boltslinger IV is open again and its 3 AP are back (probe - not saved)", {}),
      (6, "Respec done - every Ability Point of your Archer tree is back (probe - not saved)", {}),
      (8, "Unlocked Root! 1 AP spent - 15 left (probe - not saved)", {})]),
    ("class no class clicks", cst("k12", cls=None, own=[]), ["trbuy", "trundo", "trrespec", "trrespec"],
     [(0, "Choose a class first (/class, or create a profile) - your class tree opens here", {}),
      (1, "Choose a class first (/class, or create a profile) - your class tree opens here", {})]),
    ("class no skills clicks", cst("k13", levels=False, own=[]), ["trbuy", "trrespec", "trrespec"],
     [(0, "Skill trees need SkyySkills - it is not loaded or did not answer (try again)", {}), (2, "Skill trees need SkyySkills - it is not loaded or did not answer (try again)", {})]),
    ("class mana regen post", cst("k14", cls="Mage", own=["ROOT"], regen=True, reads=READS_CLASS), ["trc2", "trbuy", "trc9", "trbuy", "trundo"],
     [(1, "Unlocked Reservoir I! 1 AP spent - 10 left", {"P1": True}), (3, "Unlocked Focus I! 1 AP spent - 9 left", {"P2": True}),
      (4, "Undo done - Focus I is open again and its 1 AP are back", {"P2": False})]),
    # ---- fix round
    ("class off mid page", cst("k15", own=SPINE_OWN, regen=True), ["trc1", "!cfg:CLASS_ON=false", "trbuy"],
     [(2, "Class trees were switched off - this is the Mining tree now", {"ROOT": True, "P1": True}, {"tree": 0, "armT": -1})]),
    ("class off mid respec", cst("k16", own=SPINE_OWN, regen=True), ["trrespec", "!cfg:CLASS_ON=false", "trrespec"],
     [(0, CLASS_RESULT_TEXTS[4][0], {"ROOT": True}), (2, "Class trees were switched off - this is the Mining tree now", {"ROOT": True}, {"tree": 0, "armT": -1})]),
    ("class respec price change", cst("k17", own=SPINE_OWN, regen=True, reads=READS_CLASS), ["trrespec", "!levels:Archery=40", "trrespec", "trrespec"],
     [(0, CLASS_RESULT_TEXTS[4][0], {"ROOT": True}),
      (2, "Click Respec again within 10 s to reset your whole Archer tree - every Ability Point comes back - it costs 4,000 coins (Archery 40 x 100) (the price changed since your first click)", {"ROOT": True}),
      (3, "Respec done - every Ability Point of your Archer tree is back (4,000 coins paid)", {"ROOT": False, "L2": False})]),
    ("class respec ledger errors", cst("k18", own=SPINE_OWN, regen=True, reads=READS_CLASS),
     ["!coins:null", "trrespec", "trrespec", "!coins:throw", "trrespec", "trrespec"],
     [(2, "A class respec costs 2,300 coins - SkyyCoins could not take them right now (nothing changed) - try again", {"ROOT": True, "L2": True}),
      (5, "A class respec costs 2,300 coins - SkyyCoins could not take them right now (nothing changed) - try again", {"ROOT": True, "L2": True})]),
    ("class undo other class", cst("k19", cls="Mage", own=SPINE_OWN, undo_raw=[CT_IDX["L2"]]), ["trundo"],
     [(0, "Nothing to undo - your class changed since those unlocks", {"L2": True}, {"undo": 0})]),
    ("class broken respec free", cst("k20", own=["P1", "P2", "X1"], regen=True, reads=READS_CLASS), ["trrespec", "trrespec"],
     [(0, "Click Respec again within 10 s to reset your whole Archer tree - every Ability Point comes back - free", {"P1": True}),
      (1, "Respec done - every Ability Point of your Archer tree is back", {"P1": False, "P2": False, "X1": False})]),
    ("class level zero cooldown", cst("k21", own=["ROOT"], lvl=0, regen=True, respec_at=-1), ["trrespec", "trrespec"],
     [(1, "You can respec your Archer tree again in 10 min", {"ROOT": True})]),
]


# ============================================================================================================== child JVMs
def _jre_major(jvm):
    home = os.path.dirname(os.path.dirname(os.path.dirname(jvm)))
    try:
        m = re.search(r'^JAVA_VERSION="(\d+)', open(os.path.join(home, "release"), encoding="utf8", errors="replace").read(), re.M)
    except OSError:
        return 0
    return int(m.group(1)) if m else 0


def _jvm_start(jars, extra_cp=(), verify=True):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    if _jre_major(jvm) >= 26:
        opts.append("--enable-final-field-mutation=ALL-UNNAMED")
    jpype.startJVM(jvm, *opts, classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


def _stand_ins():
    """the Unsafe-allocated PlayerRef (uuid / username set), the ByTree bridge Function and the setf helper - shared by the children"""
    from jpype import JClass, JImplements, JOverride
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    @JImplements("java.util.function.Function")
    class ByTree(object):
        def __init__(self, table, boxed):
            self.table, self.boxed = table, boxed

        @JOverride
        def apply(self, o):
            return self.boxed(int(self.table.get(str(o[1]), 0)))

    me = JClass("java.util.UUID")(0x7ee5, 25)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    return U, setf, ByTree, me, pr


def run_states(jar, out, tag):
    from jpype import JClass, JImplements, JOverride, JArray, JLong, JBoolean, JInt
    _jvm_start([jar])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, load_fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            load_fails.append("%s: %s" % (n, e))
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": load_fails, "states": {}, "clicks": {}, "colors": {},
           "nclicks": {}}
    if load_fails:
        json.dump(res, open(out, "w"), indent=1)
        os._exit(0)
    Page, Store, Cfg, Defs, Data = (JClass(PKG + x) for x in ("TreePage", "TreeStore", "TreeCfg", "TreeDefs", "TreeData"))
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths, Long, Integer, Boolean = (JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Integer"),
                                     JClass("java.lang.Boolean"))
    System = JClass("java.lang.System")
    _U, _setf, ByTree, me, pr = _stand_ins()
    COIN_CALLS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            COIN_CALLS.append(int(o[1].longValue()))
            return Boolean.TRUE

    pdir = os.path.join(SCRATCH, "players-" + tag)
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    bridge = Store.bridge()
    en0 = [bool(x) for x in Cfg.EN]
    is_new = int(Defs.NT) == 8
    has_class = is_new and hasattr(Cfg, "CLASS_ON")
    Cls = JClass(PKG + "TreeClass") if has_class else None
    Cops = JClass(PKG + "TreeClassOps") if has_class else None
    COIN_MODE = ["true"]
    REGEN_CALLS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            COIN_CALLS.append(int(o[1].longValue()))
            if COIN_MODE[0] == "null":          # fix round: a ledger that answers nothing / throws
                return None
            if COIN_MODE[0] == "throw":
                raise RuntimeError("ledger down")
            return Boolean.TRUE if COIN_MODE[0] == "true" else Boolean.FALSE

    @JImplements("java.util.function.Function")
    class Regen(object):
        """the SkyySkills 0.4.12 skill:fn:manaregen registry: records every call as [op, source, value]"""
        @JOverride
        def apply(self, o):
            op = str(o[0])
            REGEN_CALLS.append([op, str(o[2]) if len(o) > 2 else None, float(o[3].doubleValue()) if len(o) > 3 else None])
            return Boolean.TRUE

    def class_idx(name):
        return CLASSES.index(name) if name in CLASSES else -1

    def setup(spec):
        g = spec.get
        for k in list(bridge.keySet()):
            if str(k).startswith(("skill:", "coins:", "profile", "tree:", "move:", "class:", "gear:")):
                bridge.remove(k)
        Store.DATA.clear()
        Store.DIRTY.clear()
        for fn in os.listdir(pdir):
            os.remove(os.path.join(pdir, fn))
        for i, v in enumerate(en0):
            Cfg.EN[i] = v
        for key in g("en_off", ()):
            Cfg.EN[int(Defs.idx(key))] = False
        Cfg.EXTRA_DUST = g("extra_dust", 0)
        Cfg.EXTRA_TOKENS = g("extra_tokens", 0)
        Cfg.RESPEC_COINS = g("respec_coins", 0)
        if g("levels") is not None:
            bridge.put("skill:fn:level", ByTree(spec["levels"], Integer))
        if g("xps") is not None:
            bridge.put("skill:fn:xp", ByTree(spec["xps"], Long))
        if g("known") is not None:
            bridge.put("skill:" + str(me), spec["known"])
        for mod, csv in (g("reads") or {}).items():
            bridge.put(mod if ":" in mod else "tree:reads:" + mod, csv)
        if g("coins", True):
            bridge.put("coins:fn:take", Coins())
        COIN_MODE[0] = "true"
        del COIN_CALLS[:]
        del REGEN_CALLS[:]
        d = Data()
        for key, v in (g("nodes") or {}).items():
            i = int(Defs.idx(key))
            if i >= 0:
                d.lv[i] = v
        for key in g("off", ()):
            i = int(Defs.idx(key))
            if i >= 0:
                d.off[i] = True
        d.bad = bool(g("bad", False))
        ci = -1
        if has_class:
            cfg = {"CLASS_ON": False, "AP_FIRST": 1, "AP_EVERY": 2, "AP_MAX": 50, "C_RESPEC_PER": 100, "C_UNDO": True, "C_EXTRA_AP": 0}
            cfg.update(g("cfg") or {})
            for k, v in cfg.items():
                setattr(Cfg, k, v)
            con = JArray(JBoolean)(int(Cls.NC) * int(Cls.NN))
            cmn = JArray(JInt)(int(Cls.NC) * int(Cls.NN))
            cam = JArray(JInt)(int(Cls.NC) * int(Cls.NN))
            for i in range(len(con)):
                con[i] = True
                cmn[i] = int(Cls.CMIN[i])
                cam[i] = int(Cls.CAMT[i])
            Cls.LAST_REGEN.clear()
            Cls.POSTN.clear()
            eff = g("pcls") or g("cls")
            ci = class_idx(eff)
            if g("cls"):
                bridge.put("class:" + str(me), g("cls"))
            if g("pcls"):
                bridge.put("profile:class:" + str(me), g("pcls"))
            if g("regen"):
                bridge.put("skill:fn:manaregen", Regen())
            if ci >= 0:
                for nid in g("con_off", ()):
                    con[ci * 37 + CT_IDX[nid]] = False
                for nid, v in (g("cmin") or {}).items():
                    cmn[ci * 37 + CT_IDX[nid]] = v
                for nid, v in (g("camt") or {}).items():
                    cam[ci * 37 + CT_IDX[nid]] = v
                for nid in g("own", ()):
                    d.cown[ci * 37 + CT_IDX[nid]] = True
                if g("respec_at", 0) == -1:
                    d.crespecAt[ci] = System.currentTimeMillis()
            Cfg.C_ON = con
            Cfg.C_MIN = cmn
            Cfg.C_AMT = cam
        Store.DATA.put(str(me), d)
        page = Page(pr, spec["tree"])
        page.sel = g("sel", 1)
        page.msg = g("msg", "")
        if g("armed"):
            page.armT = spec["tree"]
            page.armAt = System.currentTimeMillis()
        if has_class:
            page.cpage = g("cpage", 0)
            page.csel = g("csel", 0)
            for n in g("undo", ()):
                page.undo.add(Integer.valueOf((ci if ci >= 0 else 0) * 37 + int(n)))   # fix round: the list holds class x 37 + node
            for n in g("undo_raw", ()):
                page.undo.add(Integer.valueOf(int(n)))                                   # an unqualified / other class's entry
            if g("probe"):
                page.probe = True
                page.pci = ci if ci >= 0 else 0
                page.pd = Cops.probeData(page.pci)
        return page, d

    def render(page):
        b, ev = UCB(), UEB()
        try:
            page.build(None, b, ev, None)
            err = None
        except Exception as e:
            err = str(e)
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        out = {"error": err, "commands": cmds, "events": evs, "tree": int(page.tree)}
        if has_class:
            out["cpage"], out["csel"] = int(page.cpage), int(page.csel)
        return out

    xp_t0 = Cfg.XP_T

    def set_rate(norm):
        """0.3 changes the Mining Dust rate 10 -> 5 (Skyy's lock): for the 0.2.5 compare the new jar renders with Mining at 0.2.5's 10"""
        if not is_new:
            return
        if norm:
            arr = JArray(JLong)(len(xp_t0))
            for i in range(len(xp_t0)):
                arr[i] = xp_t0[i]
            arr[0] = 10
            Cfg.XP_T = arr
        else:
            Cfg.XP_T = xp_t0

    def cown_of(d, ci):
        if ci < 0 or not has_class or d is None:
            return []
        return [CT_ID[n] for n in range(37) if bool(d.cown[ci * 37 + n])]

    def gearx():
        o = bridge.get("gear:extras:" + str(me))
        if o is None:
            return None
        v = o.get("trees")
        return None if v is None else str(v)

    def run_clicks(spec, clicks):
        page, d = setup(spec)
        ci = class_idx(spec.get("pcls") or spec.get("cls")) if has_class else -1
        steps = []
        for p in clicks:
            err = None
            if p.startswith("!reads:"):
                mod, csv = p[7:].split("=", 1)
                bridge.put(mod if ":" in mod else "tree:reads:" + mod, csv)
            elif p.startswith("!unreads:"):
                mod = p[9:]
                bridge.remove(mod if ":" in mod else "tree:reads:" + mod)
            elif p.startswith("!coins:"):
                mode = p[7:]
                if mode == "none":
                    bridge.remove("coins:fn:take")
                else:
                    COIN_MODE[0] = mode
                    bridge.put("coins:fn:take", Coins())
            elif p == "!undo:pop":
                page.undo.remove(page.undo.get(page.undo.size() - 1))
            elif p.startswith("!cfg:"):                     # fix round: a Server Setup change while the page is open
                k_, v_ = p[5:].split("=", 1)
                setattr(Cfg, k_, v_ == "true" if v_ in ("true", "false") else int(v_))
            elif p.startswith("!levels:"):                  # fix round: a class level-up while the page is open
                k_, v_ = p[8:].split("=", 1)
                spec["levels"][k_] = int(v_)
            else:
                try:
                    page.handleDataEvent(None, None, '{"a":"%s"}' % p)
                except Exception as e:
                    err = str(e)[:200]
            step = {"click": p, "err": err, "tree": int(page.tree), "sel": int(page.sel), "msg": None if page.msg is None else str(page.msg),
                    "armT": int(page.armT), "armed": int(page.armAt) > 0, "lv": [int(x) for x in d.lv], "off": [bool(x) for x in d.off],
                    "respec": [int(x) > 0 for x in d.respecAt], "credit": [int(x) for x in d.credit], "coins": list(COIN_CALLS),
                    "dirty": sorted(str(k) for k in Store.DIRTY.keySet())}
            if has_class:
                step.update({"cpage": int(page.cpage), "csel": int(page.csel), "cown": cown_of(d, ci), "undo": int(page.undo.size()),
                             "gearx": gearx(), "regen": list(REGEN_CALLS), "crespec": [int(x) > 0 for x in d.crespecAt],
                             "pcown": cown_of(page.pd, int(page.pci)) if page.pd is not None else None})
            steps.append(step)
        return {"steps": steps, "after": render(page)}

    res["real"] = {}
    for spec in STATES:
        set_rate(True)
        page, _d = setup(spec)
        res["states"][spec["name"]] = render(page)
        if is_new:
            set_rate(False)
            page, _d = setup(spec)
            res["real"][spec["name"]] = render(page)
    set_rate(True)
    for name, spec, clicks in CLICKS:
        res["clicks"][name] = run_clicks(spec, clicks)
    set_rate(False)
    if is_new:
        for spec in NEW_STATES:
            page, _d = setup(spec)
            res["states"][spec["name"]] = render(page)
        for name, spec, clicks, _want in NEW_CLICKS:
            res["nclicks"][name] = run_clicks(spec, clicks)
    res["cstates"], res["cclicks"], res["ctables"] = {}, {}, {}
    if has_class:
        for spec in CLASS_STATES:
            page, _d = setup(spec)
            res["cstates"][spec["name"]] = render(page)
        for name, spec, clicks, _want in CLASS_CLICKS:
            res["cclicks"][name] = run_clicks(spec, clicks)
        for arr in ("NID", "CLASSES", "CSKILL", "CICON", "CCOLOR", "LANE", "CNM", "CIC", "CNOW", "CHOW"):
            res["ctables"][arr] = [str(x) for x in getattr(Cls, arr)]
        for arr in ("NAP", "NPAGE", "NROW", "NCOL", "NLANE", "NLANEN", "NPAR1", "NPAR2", "NNEED", "NLOCK", "NROLE", "CK", "CAMT", "CMIN", "LA", "LB",
                    "SK", "SN", "SARMS", "PL1", "PL2"):
            res["ctables"][arr] = [int(x) for x in getattr(Cls, arr)]
        for arr in ("SR", "SD", "CMAGIC"):
            res["ctables"][arr] = [bool(x) for x in getattr(Cls, arr)]
        res["ctables"]["NN"], res["ctables"]["NC"], res["ctables"]["NSLOT"] = int(Cls.NN), int(Cls.NC), int(Cls.NSLOT)
    if hasattr(Page, "infoColor"):
        for m, _k in RESULT_TEXTS + NEW_RESULT_TEXTS + (CLASS_RESULT_TEXTS if is_new else []):
            res["colors"][m] = str(Page.infoColor(m))
        res["colors"][None] = str(Page.infoColor(None))
    for i, v in enumerate(en0):
        Cfg.EN[i] = v
    json.dump(res, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)          # the scheduler threads a respec may start (HytaleServer.SCHEDULED_EXECUTOR) must not keep the child alive


# ============================================================================================ child: bytecode method compare (javassist)
def vnorm(text):
    """a listing / constant with every version token as V ("SkyyTrees 0.3" in the default file header vs "SkyyTrees 0.2.5")"""
    return text.replace(OLD_VERSION, "V").replace("SkyyTrees " + VERSION, "SkyyTrees V").replace('"' + VERSION + '"', '"V"')


NAMES_025 = ",".join(TREES_025)


def const_pair(a, b):
    """one instruction of an 0.2.5 method vs the same instruction in 0.3 that may differ only by a constant javassist inlines from
    TreeDefs / TreeCfg: N 72 -> 96, NT 6 -> 8, N - SOON_N 64 -> 88, the tree:names text, the default file text (checked in L2)"""
    if (a, b) in (("bipush 72", "bipush 96"), ("bipush 6", "bipush 8"), ("bipush 64", "bipush 88")):
        return True
    if a.startswith("ldc ") and b.startswith("ldc "):
        if NAMES_025 in a and a.replace(NAMES_025, ",".join(TREES)) == b:
            return True
        if a.startswith('ldc "# SkyyTrees 0.2.5 - skill trees for') and b.startswith('ldc "# SkyyTrees 0.3 - skill trees for'):
            return True
    return False


def const_only_change(la, lb):
    """True when listing lb (0.3) = listing la (0.2.5) with only const_pair differences, instruction for instruction"""
    import difflib
    a, b = la.split("\n"), lb.split("\n")
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if op != "replace" or (i2 - i1) != (j2 - j1) or not all(const_pair(x, y) for x, y in zip(a[i1:i2], b[j1:j2])):
            return False
    return True


def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([], [B.JAVASSIST])
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            key = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[key] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool)).replace("\r", "\\r").replace("\n", "\\n")   # one instruction = one line
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[key] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        consts = {}
        for f in list(cc.getDeclaredFields()):
            ca = f.getFieldInfo().getConstantValue()
            if ca:
                consts[str(f.getName())] = str(cc.getClassFile().getConstPool().getLdcValue(ca))
        return ms, fields, consts

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo, co = listing(ClassPool(False), a)
        mn, fn, cn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        consts = dict((k, [co.get(k), cn.get(k)]) for k in set(co) | set(cn) if co.get(k) != cn.get(k))
        const_only = sorted(k for k in changed if const_only_change(mo[k], mn[k]))
        res[n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)), "fields_same": fo == fn,
                  "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)), "consts": consts,
                  "version_only": all(vnorm(mo[k]) == vnorm(mn[k]) for k in changed)
                  and all(vnorm(x or "") == vnorm(y or "") for x, y in consts.values()), "const_only": const_only}
    json.dump(res, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ child: the javassist stand-ins
def run_mkfake(out_dir):
    """skyytest.FakeCB (a CommandBuffer whose getComponent answers one Component), FakeStatMap (an EntityStatMap that records its
    modifiers in a HashMap keyed "<index>:<key>" and answers get(int) with one EntityStatValue), LookupIn (a MethodHandles.Lookup IN a
    class) and BadAccess (the control: a class that is no page calling the page's PROTECTED sendUpdate)"""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    cb = cp.makeClass("skyytest.FakeCB")
    cb.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    cb.addField(CtField.make("public com.hypixel.hytale.component.Component comp;", cb))
    cb.addConstructor(CtNewConstructor.make("public FakeCB() { super(null); }", cb))      # never run (Unsafe.allocateInstance)
    cb.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) { return this.comp; }", cb))
    cb.writeFile(out_dir)
    sm = cp.makeClass("skyytest.FakeStatMap")
    sm.setSuperclass(cp.get("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"))
    sm.addField(CtField.make("public java.util.HashMap mods;", sm))
    sm.addField(CtField.make("public com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue val;", sm))
    sm.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue get(int i) { return this.val; }", sm))
    sm.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier getModifier(int i, String k) { return (com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier) this.mods.get(i + \":\" + k); }", sm))
    sm.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier putModifier(int i, String k, com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier m) { return (com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier) this.mods.put(i + \":\" + k, m); }", sm))
    sm.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier removeModifier(int i, String k) { return (com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier) this.mods.remove(i + \":\" + k); }", sm))
    sm.writeFile(out_dir)
    lk = cp.makeClass("skyytest.LookupIn")
    lk.addMethod(CtNewMethod.make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(out_dir)
    ba = cp.makeClass("skyytest.BadAccess")
    ba.addMethod(CtNewMethod.make(
        "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
        "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    ba.writeFile(out_dir)


# ============================================================================================ child: logic (L, M, P, S)
def run_logic(jar, old, fake, live, out):
    from jpype import JClass, JArray, JObject, JDouble, JString, JImplements, JOverride
    _jvm_start([], [fake])
    R = {"oks": 0, "fails": [], "info": {}}

    def ck(cond, what):
        if cond:
            R["oks"] += 1
        else:
            R["fails"].append(what)
            print("FAIL", what)

    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    Paths, Long, Integer, Boolean = (JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Integer"),
                                     JClass("java.lang.Boolean"))
    U, setf, ByTree, me, pr = _stand_ins()

    def loader(j):
        urls = JArray(URL)(1)
        urls[0] = File(j).toURI().toURL()
        return URLCL(urls, sysl)

    def K(ld):
        return lambda n: JClass(PKG + n, loader=ld)

    def path(p):
        return Paths.get(p)

    def snap(d):
        outd = {}
        for r, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r, f)
                outd[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
        return outd

    def jarr(xs):
        return JArray(JObject)(xs)

    bridge = None
    L3, L25 = loader(jar), loader(old)
    C3, C25 = K(L3), K(L25)
    bridge = C3("TreeStore").bridge()

    def clear_bridge():
        for k in list(bridge.keySet()):
            if str(k).startswith(("skill:", "coins:", "profile", "tree:", "move:")):
                bridge.remove(k)

    # ------------------------------------------------------------------ L1. the node table
    D3, D25 = C3("TreeDefs"), C25("TreeDefs")
    ck(int(D3.N) == 96 and int(D3.NT) == 8 and int(D25.N) == 72 and int(D25.NT) == 6, "L1: 96 nodes / 8 trees (0.2.5: 72 / 6)")
    ck([str(x) for x in D3.TREES] == TREES and str(D3.NAMES_CSV) == ",".join(TREES), "L1: TREES and tree:names = %s" % str(D3.NAMES_CSV))
    ck(str(D3.NAMES_LIST) == ", ".join(TREES), "L1: NAMES_LIST (checkDust's answer)")
    ck([int(x) for x in D3.D_DUST] == [5, 0, 0, 0, 2, 5, 0, 5], "L1: D_DUST Mining 5, Acrobatics 2, Exploration 5, Smithing 5: %s" % list(D3.D_DUST))
    same = True
    for arr in ("ID", "NAME", "NOW", "HOW", "LISTKEY", "D_LIST", "KIND", "TIER", "D_MAX", "D_TOK", "D_B", "D_PER", "D_BASE", "ICON"):
        a3, a25 = [str(x) for x in getattr(D3, arr)][:72], [str(x) for x in getattr(D25, arr)]
        if arr == "ICON":
            a25 = ["Template_Glider" if x == "Glider" else x for x in a25]
        if a3 != a25:
            same = False
            R["info"]["L1 diff " + arr] = [(i, a25[i], a3[i]) for i in range(72) if a3[i] != a25[i]][:5]
    ck(same, "L1: the 72 nodes of 0.2.5 are unchanged field for field (only Glider -> Template_Glider)")
    ck([str(x) for x in D25.ICON].count("Glider") == 2 and [str(x) for x in D3.ICON].count("Template_Glider") == 2
       and "Glider" not in [str(x) for x in D3.ICON], "L1: the two Glider icons are Template_Glider now")
    kinds = {"MANA": 24, "ALCH": 25, "SMITH": 26, "XP": 2, "HP": 3}
    for tn in ("Alchemy", "Smithing"):
        for s, (nid, nm, kd, mx, per, readers) in enumerate(NEW_TREE[tn]):
            i = TREES.index(tn) * 12 + s
            ok = (str(D3.ID[i]) == nid and str(D3.NAME[i]) == nm and int(D3.KIND[i]) == kinds[kd] and int(D3.D_MAX[i]) == mx
                  and abs(float(D3.D_PER[i]) - per) < 1e-12 and str(D3.KEY[i]) == "%s.%s" % (tn, nid)
                  and str(D3.READERS[i]) == ",".join(readers) and str(D3.COMING_WHO[i]) == " or ".join(readers)
                  and str(D3.COMING_CARD[i]) == (("Coming with " + readers[0]) if readers else "")
                  and int(D3.TIER[i]) == [1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6][s] and str(D3.LISTKEY[i]) == "")
            ck(ok, "L1: %s S%d = %s %s %s max %d per %s readers %s" % (tn, s + 1, nid, nm, kd, mx, per, readers))
            ck(int(D3.idx("%s.%s" % (tn, nid))) == i, "L1: TreeDefs.idx(%s.%s) = %d" % (tn, nid, i))
    ck(all(str(D3.READERS[i]) == "" for i in range(72)), "L1: no 0.2.5 node has a reader")
    ck(int(D3.tree("alc")) == 6 and int(D3.tree("smi")) == 7 and int(D3.tree("acr")) == 4 and int(D3.tree("Smithing")) == 7
       and int(D3.tree("al")) == -1, "L1: /tree name and 3-letter prefixes for the new trees")

    # ------------------------------------------------------------------ L2. the default file and the older ADD blocks
    G3, G25 = C3("TreeCfg"), C25("TreeCfg")
    for blk in ("ADD02", "ADD021DJ", "ADD021FEL", "ADD023", "ADD024", "ADD024DODGE"):
        ck(str(getattr(G3, blk)) == str(getattr(G25, blk)), "L2: TreeCfg.%s is byte for byte 0.2.5's" % blk)
    d3l, d25l = str(G3.DEFAULTS).split("\n"), str(G25.DEFAULTS).split("\n")
    import difflib
    ops = [(t, d25l[a:b], d3l[c:d]) for t, a, b, c, d in difflib.SequenceMatcher(None, d25l, d3l, autojunk=False).get_opcodes() if t != "equal"]
    head_ok = ops and ops[0][0] == "replace" and ops[0][1] == [d25l[0]] and ops[0][2] == [d3l[0]] and "Alchemy, Smithing" in d3l[0] and "SkyyTrees 0.3 " in d3l[0]
    ck(head_ok, "L2: the default file header names the new version and trees")
    ins = [x for t, a_, b_ in ops[1:] for x in b_]
    dels = [x for t, a_, b_ in ops[1:] for x in a_]
    ck(not dels and all(t == "insert" for t, _a, _b in ops[1:]), "L2: the 0.3 default file only ADDS lines to 0.2.5's: %s" % dels[:3])
    ck(ins[:3] == ["# Mining and Smithing earn 1 Dust per 5 XP (Skyy 2026-10-02: Mining Dust doubled; Smithing XP comes slowly).",
                   "dust.xpPerDust.Mining=5", "dust.xpPerDust.Smithing=5"] or
       (ins[0].startswith("# Mining and Smithing") and "dust.xpPerDust.Mining=5" in ins and "dust.xpPerDust.Smithing=5" in ins),
       "L2: the new Dust comment + the Mining / Smithing lines: %s" % ins[:3])
    keyed = [x for x in ins if not x.startswith("#") and x]
    ck(len(keyed) == 2 + 24 * 5 + 7 + 3 + 5 * 37 == 317 and sum(1 for x in ins if "skyytrees-0.3-trees" in x) == 1,
       "L2: exactly 2 Dust lines + 120 node lines + the class block (7 + 3 + 185 lines; comments, the marker once) added: %d" % len(keyed))
    pd = dict(x.split("=", 1) for x in d3l if x and not x.startswith("#"))
    ck(pd.get("class.enabled") == "false" and pd.get("class.ap.first") == "1" and pd.get("class.ap.every") == "2" and pd.get("class.ap.max") == "50"
       and pd.get("class.respec.perLevel") == "100" and pd.get("class.undo") == "true" and pd.get("class.debug.extraAp") == "0"
       and pd.get("class.minLevel.Archer.R2") == "15" and pd.get("class.minLevel.Archer.R3") == "15" and pd.get("class.minLevel.Archer.R4") == "50"
       and pd.get("class.nodes.Archer.ROOT") == "true,4,1" and pd.get("class.nodes.Archer.R4") == "true,30,3" and pd.get("class.nodes.Mage.X1") == "true,8,1"
       and pd.get("class.nodes.Priest.RS") == "true,0,4" and len([k for k in pd if k.startswith("class.nodes.")]) == 185,
       "L2: the class block's default lines (class.enabled=false, the AP rule, respec 100 / level, Undo, the crossbow levels, 185 node lines)")
    for tn in ("Alchemy", "Smithing"):
        for s, (nid, _nm, _kd, mx, per, _r) in enumerate(NEW_TREE[tn]):
            k = "%s.%s." % (tn, nid)
            ck(pd.get(k + "max") == str(mx) and float(pd.get(k + "per")) == per and pd.get(k + "B") == str([5, 5, 5, 150, 150, 100, 500, 1000, 1000, 200, 4000, 150000][s])
               and pd.get(k + "tokens") == str([1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3][s]) and pd.get(k + "enabled") == "true",
               "L2: default lines of %s.%s" % (tn, nid))

    # ------------------------------------------------------------------ L3. a fresh start in a fresh loader (the plugin's order)
    def start(base, ld=None, kit=True):
        ld = ld or loader(jar)
        C = K(ld)
        b = path(base)
        C("TreeCfg").FILE = b.resolve("trees.properties")
        C("TreeStore").DIR = b.resolve("players")
        s = str(C("TreeCfg").load())
        m = str(C("TreeMig").run(b))
        if kit:
            C("CfgPub").start(b.getParent(), None)
        return {"C": C, "sum": s, "mig": m, "xp": [int(x) for x in C("TreeCfg").XP_T]}

    fresh = os.path.join(SCRATCH, "l", "fresh", "mods", "Skyy_SkyyTrees")
    os.makedirs(fresh)
    r1 = start(fresh)
    f1 = open(os.path.join(fresh, "trees.properties"), "rb").read()
    ck(f1 == str(G3.DEFAULTS).encode("utf8") and r1["mig"] == "", "L3: a fresh start writes the 0.3 default file and the update does nothing")
    ck(r1["xp"] == [5, 10, 10, 10, 2, 5, 10, 5], "L3: Dust rates Mining 5, Foraging / Farming / Cooking / Alchemy 10, Acrobatics 2, Exploration 5, Smithing 5: %s" % r1["xp"])
    ck("88 of 88 nodes on (8 coming later)" in r1["sum"], "L3: the load summary counts the 96 nodes: %s" % r1["sum"])
    s1 = snap(fresh)
    r2 = start(fresh)
    ck(snap(fresh) == s1 and r2["mig"] == "", "L3: a second start writes nothing")
    CfgFn = r2["C"]("CfgFn")
    hdr = bridge.get("config:def:SkyyTrees")
    rows = [list(map(str, r)) for r in hdr[7]]
    ck(len(rows) == 41 and [r[0] for r in rows][26:28] == ["nodes.Alchemy", "nodes.Smithing"]
       and [r[0] for r in rows][28:] == ["class.enabled", "class.ap.first", "class.ap.every", "class.ap.max", "class.respec.perLevel", "class.undo",
                                          "class.debug.extraAp", "class.minLevel"] + ["class.nodes." + c for c in CLASSES],
       "L9: 41 Server Setup rows: 0.2.5's 26 + nodes.Alchemy / nodes.Smithing + the 13 class rows: %s" % [r[0] for r in rows][26:])
    ck([r[2] for r in rows][28:] == ["classes"] * 13 and "classes" in [str(x) for x in hdr[5]] and "Class trees" in [str(x) for x in hdr[6]], "L9: the class rows sit in the Class trees category")
    ck([str(r[4]) for r in rows][28:35] == ["false", "1", "2", "50", "100", "true", "0"], "L9: the class rows' defaults")
    keys_d = CfgFn().apply(jarr(["keys", "dust.perTree", ""]))
    dmap = dict(zip([str(x) for x in keys_d[0]], [str(x) for x in keys_d[2]]))
    ck(dmap == {"Mining": "5", "Acrobatics": "2", "Exploration": "5", "Smithing": "5"}, "L9: dust.perTree lists Mining 5, Acrobatics 2, Exploration 5, Smithing 5: %s" % dmap)
    keys_a = CfgFn().apply(jarr(["keys", "nodes.Alchemy", ""]))
    keys_s = CfgFn().apply(jarr(["keys", "nodes.Smithing", ""]))
    ck(len(keys_a[0]) == 60 and len(keys_s[0]) == 60 and "PMana.per" in [str(x) for x in keys_a[0]], "L9: nodes.Alchemy / nodes.Smithing list 60 entries each")

    def tset(C, table, entry, value, confirm=""):
        return [str(x) if x is not None else None for x in C("CfgFn")().apply(jarr(["tset", table, entry, value, None, "console", confirm, "console"]))]

    def add(C, table, entry, value, confirm=""):
        return [str(x) if x is not None else None for x in C("CfgFn")().apply(jarr(["add", table, entry, value, None, "console", confirm, "console"]))]
    a1 = tset(r2["C"], "nodes.Alchemy", "PMana.per", "2")
    a2 = tset(r2["C"], "nodes.Alchemy", "PExtra.per", "2")
    a3 = add(r2["C"], "nodes.Smithing", "SNope.max", "3")
    a4 = add(r2["C"], "dust.perTree", "Alchemist", "3")
    a5 = add(r2["C"], "dust.perTree", "Alchemy", "7")
    ck(a1[0] == "confirm" and "per level (0.02 = 2%)" not in (a1[2] or ""), "L9: Deep Reserves per 2 = the plain danger confirm (flat, not a percent ask): %s" % a1)
    ck(a2[0] == "confirm" and "per level (0.02 = 2%)" in (a2[2] or ""), "L9: Extra Brew per 2 asks (more than 100%% per level): %s" % a2)
    ck(a3[0] == "confirm" and "not a Smithing node" in (a3[2] or ""), "L9: an unknown Smithing node asks: %s" % a3)
    ck(a4[0] == "confirm" and ", ".join(TREES) in (a4[2] or ""), "L9: checkDust names all eight trees: %s" % a4)
    ck(a5[0] == "confirm" and "not a tree" not in (a5[2] or ""), "L9: dust.perTree Alchemy is a known tree (only the danger confirm): %s" % a5)
    a6 = add(r2["C"], "dust.perTree", "Alchemy", "7", "yes")
    r2["C"]("CfgPub").flush()
    ck(a6[0] == "ok" and int(r2["C"]("TreeCfg").XP_T[6]) == 7, "L9: a set Alchemy Dust rate applies (RELOAD): %s %s" % (a6, list(r2["C"]("TreeCfg").XP_T)))
    exp = str(r2["C"]("CfgFn")().apply(jarr(["export", "all"])))
    imp = [str(x) for x in r2["C"]("CfgFn")().apply(jarr(["import", exp, None, "console", "preview"]))]
    ck(exp.startswith("SKYY1.SkyyTrees.") and "nothing to change" in (imp[2] or "").lower(), "L9: export all -> import preview = nothing to change: %s" % imp[2][:120])

    # ------------------------------------------------------------------ L6. gating, buy / level / respec through TreeOps (fresh loader)
    lg = loader(jar)
    C = K(lg)
    Ops, Calc, Store, Cfg, Data, Fx, Defs = (C(x) for x in ("TreeOps", "TreeCalc", "TreeStore", "TreeCfg", "TreeData", "TreeFx", "TreeDefs"))
    gdir = os.path.join(SCRATCH, "l", "gate", "mods", "Skyy_SkyyTrees")
    os.makedirs(gdir)
    Cfg.FILE = path(os.path.join(gdir, "trees.properties"))
    Store.DIR = path(os.path.join(gdir, "players"))
    Cfg.load()
    clear_bridge()

    def fresh_data():
        Store.DATA.clear()
        d = Data()
        Store.DATA.put(str(me), d)
        return d

    def lv(d, key):
        return int(d.lv[int(Defs.idx(key))])

    def levels(tbl):
        bridge.put("skill:fn:level", ByTree(tbl, Integer))
        bridge.put("skill:fn:xp", ByTree(dict((k, v * 1000) for k, v in tbl.items()), Long))

    # fix round A: valueText of the MANA kind is flat (Deep Reserves 75 = Alchemy S4), like HP (Forge Hardened 89)
    ck(str(Defs.valueText(75, 3.0)) == "3" and str(Defs.valueText(75, 10.0)) == "10" and str(Defs.valueText(89, 2.0)) == "2" and str(Defs.valueText(72, 0.02)) == "2%",
       "L: valueText - Deep Reserves flat (%s), Forge Hardened flat, Extra Brew a percent" % str(Defs.valueText(75, 3.0)))
    # reads() on odd flag values
    bridge.put("tree:reads:SkyySacks", " Smithing.SSmelt ,Smithing.SQuick,, ")
    ck(bool(Calc.reads("SkyySacks", "Smithing.SSmelt")) and bool(Calc.reads("SkyySacks", "Smithing.SQuick"))
       and not bool(Calc.reads("SkyySacks", "Smithing.SFuel")) and not bool(Calc.reads("SkyySacks", "smithing.ssmelt"))
       and not bool(Calc.reads("SkyySacks", "Smithing.SSmel")) and not bool(Calc.reads("SkyySacks", "")), "L6: reads() trims spaces, is exact and case-sensitive")
    bridge.put("tree:reads:SkyySacks", Integer(5))
    ck(not bool(Calc.reads("SkyySacks", "Smithing.SSmelt")), "L6: a non-String flag counts as nothing")
    clear_bridge()
    # no flags: exactly the nodes with readers are coming; the 0.2.5 trees never
    want_c = [bool(NEW_TREE[TREES[i // 12]][i % 12][5]) if i >= 72 else False for i in range(96)]
    ck([bool(Calc.coming(i)) for i in range(96)] == want_c, "L6: no flags - coming = the nodes with readers")
    ck(str(Calc.comingTree(6)) == "SkyySkills" and str(Calc.comingTree(7)) == "SkyyGear, SkyySkills and SkyySacks"
       and all(str(Calc.comingTree(t)) == "" for t in range(6)), "L6: comingTree names the waiting mods: %s / %s" % (Calc.comingTree(6), Calc.comingTree(7)))
    ck(all(int(Calc.needTier(t, k)) == k - 1 for t in range(6) for k in range(1, 7)), "L6: needTier = tier - 1 in every 0.2.5 tree")
    ck([int(Calc.needTier(6, k)) for k in range(1, 7)] == [0, 0, 2, 2, 2, 2] and [int(Calc.needTier(7, k)) for k in range(1, 7)] == [0, 0, 0, 3, 3, 3],
       "L6: no flags - the path passes over all-coming tiers: Alchemy %s, Smithing %s" % ([int(Calc.needTier(6, k)) for k in range(1, 7)], [int(Calc.needTier(7, k)) for k in range(1, 7)]))
    levels({"Alchemy": 12, "Smithing": 25})
    Cfg.EXTRA_DUST = 10 ** 9
    d = fresh_data()
    ck(str(Ops.buy(pr, 6, 1)) == NEW_RESULT_TEXTS[0][0] and lv(d, "Alchemy.PExtra") == 0, "L6: Extra Brew refused while coming")
    ck(str(Ops.buy(pr, 6, 4)) == "Unlocked Deep Reserves!" and lv(d, "Alchemy.PMana") == 1, "L6: Deep Reserves unlocks before any reader (pass-through)")
    for n in range(2, 11):
        Ops.buy(pr, 6, 4)
    ck(lv(d, "Alchemy.PMana") == 10 and str(Ops.buy(pr, 6, 4)) == "Deep Reserves is already maxed", "L6: Deep Reserves levelled to max with debug Dust")
    bal = [int(x) for x in Calc.balance(me, d, 6, 12)]
    ck(bal[1] == 1 and bal[3] == sum(150 * n ** 3 for n in range(1, 10)), "L6: spent = 1 token + 150 x n^3 Dust: %s" % bal)
    ck(str(Ops.buy(pr, 7, 6)) == "Unlocked Forge Hardened!" and lv(d, "Smithing.SHealth") == 1, "L6: Forge Hardened (tier III) unlocks before any reader")
    v = [float(x) for x in Fx.compute(me)]
    ck(v[75] == 10.0 and v[89] == 1.0, "L6: effect vector Deep Reserves 10, Forge Hardened 1")
    Fx.refresh(me)
    bm = bridge.get("skill:bonus:" + str(me))
    ck(bm is None or bm.get("trees") is None or ("xp.alchemy" not in bm.get("trees") and "xp.smithing" not in bm.get("trees")), "L6: no Wisdom owned -> no xp.alchemy / xp.smithing posted")
    ck(str(bridge.get("tree:" + str(me))).endswith(",Alchemy:1/3,Smithing:1/6"), "L6: tree:<uuid> lists the new trees: %s" % bridge.get("tree:" + str(me)))
    TF, TB = C("TreeFn")(), C("TreeBonusFn")()
    ck(int(TF.apply(jarr([me, "Alchemy.PMana"]))) == 10 and float(TB.apply(jarr([me, "Alchemy.PMana"]))) == 10.0
       and float(TB.apply(jarr([me, "Smithing.SHealth"]))) == 1.0 and float(TB.apply(jarr([me, "Alchemy.PExtra"]))) == 0.0, "L6: tree:fn:level / tree:fn:bonus answer the new keys")
    resp = str(Ops.respec(pr, 6))
    ck(resp == "Respec done - every Alchemy token and all your Alchemy Dust are back" and lv(d, "Alchemy.PMana") == 0, "L6: respec Alchemy: %s" % resp)
    bal = [int(x) for x in Calc.balance(me, d, 6, 12)]
    ck(bal[1] == 0 and bal[3] == 0, "L6: after the respec nothing is spent: %s" % bal)
    levels({"Alchemy": 9})
    ck(str(Ops.buy(pr, 6, 4)) == "Deep Reserves needs Alchemy 10", "L6: the level gate still applies")
    # all flags: nothing is coming, the 0.2.5 path rule
    for m, csv in READS_ALL.items():
        bridge.put("tree:reads:" + m, csv)
    ck(not any(bool(Calc.coming(i)) for i in range(96)) and str(Calc.comingTree(7)) == "", "L6: all flags - nothing is coming")
    ck([int(Calc.needTier(t, k)) for t in (6, 7) for k in range(1, 7)] == [0, 1, 2, 3, 4, 5] * 2, "L6: all flags - needTier = tier - 1")
    levels({"Alchemy": 100, "Smithing": 100})
    d = fresh_data()
    ck(str(Ops.buy(pr, 6, 4)) == "Unlock a Tier I node first", "L6: all flags - Deep Reserves needs a tier I node again")
    ck(str(Ops.buy(pr, 6, 1)) == "Unlocked Extra Brew!" and str(Ops.buy(pr, 6, 4)) == "Unlocked Deep Reserves!", "L6: Extra Brew then Deep Reserves")
    for n in range(2, 6):
        ck(str(Ops.buy(pr, 6, 1)) == "Extra Brew is now level %d" % n, "L6: Extra Brew level %d" % n)
    ck(str(Ops.buy(pr, 6, 3)) == "Unlocked Alchemy Wisdom!" and str(Ops.buy(pr, 7, 3)) == "Unlocked Smithing Wisdom!", "L6: the two Wisdom nodes unlock")
    Ops.buy(pr, 6, 3)
    Fx.refresh(me)
    bm = dict(bridge.get("skill:bonus:" + str(me)).get("trees"))
    ck(abs(float(bm.get("xp.alchemy")) - 0.02) < 1e-9 and abs(float(bm.get("xp.smithing")) - 0.01) < 1e-9, "L6: skill:bonus xp.alchemy 0.02 / xp.smithing 0.01: %s" % bm)
    ck(abs(float(TB.apply(jarr([me, "Alchemy.PExtra"]))) - 0.02) < 1e-12, "L6: tree:fn:bonus Alchemy.PExtra = 5 x 0.004")
    # the reader goes away: owned kept, more levels refused, still counted and answered; respec refunds
    bridge.remove("tree:reads:SkyySkills")
    ck(bool(Calc.coming(72)) and int(Calc.state(d, 72, 100, 99)) == 2, "L6: reader gone - Extra Brew is coming but still owned (state 2)")
    ck(str(Ops.buy(pr, 6, 1)) == "Extra Brew is coming with SkyySkills - it does nothing until that mod applies it, so it cannot be levelled up yet"
       and lv(d, "Alchemy.PExtra") == 5, "L6: reader gone - no more levels")
    ck(abs(float(TB.apply(jarr([me, "Alchemy.PExtra"]))) - 0.02) < 1e-12 and int(Calc.tokSpent(d, 6)) == 3, "L6: reader gone - the levels still answer and count")
    ck(str(C("TreePage").buyText(d, 72, 2, 100, 99, 10 ** 9)) == "Coming with SkyySkills" and not bool(C("TreePage").canAct(d, 72, 2, 99, 10 ** 9)),
       "L6: reader gone - the buy line says Coming with SkyySkills, canAct false")
    ck(str(Ops.respec(pr, 6)).startswith("Respec done") and lv(d, "Alchemy.PExtra") == 0 and int(Calc.tokSpent(d, 6)) == 0, "L6: reader gone - respec refunds")
    # partial: only SkyySacks for Smelter's Luck
    clear_bridge()
    levels({"Smithing": 30})
    bridge.put("tree:reads:SkyySacks", "Smithing.SSmelt")
    d = fresh_data()
    ck(not bool(Calc.coming(85)) and bool(Calc.coming(91)) and bool(Calc.coming(84)), "L6: partial - Smelter's Luck live (either reader), Quick Forge / Fine Craft coming")
    ck(int(Calc.needTier(7, 2)) == 1 and int(Calc.needTier(7, 3)) == 1, "L6: partial - tier I has a live node, tier II is all coming -> tier III needs tier I")
    ck(str(Ops.buy(pr, 7, 6)) == "Unlock a Tier I node first", "L6: partial - Forge Hardened needs a tier I node")
    ck(str(Ops.buy(pr, 7, 2)) == "Unlocked Smelter's Luck!" and str(Ops.buy(pr, 7, 6)) == "Unlocked Forge Hardened!", "L6: partial - Smelter's Luck, then Forge Hardened")
    ck(str(C("TreeCalc").lockShort(d, 91, 30, 99)) == "Coming with SkyySacks" and str(C("TreePage").stateLine(d, 91, 0)) == "Coming with SkyySacks",
       "L6: partial - Quick Forge card / state line")
    ck(str(C("TreePage").needLine(d, 84, 30, 99, 10 ** 9)) == "Waits for the SkyyGear build that applies it - until then it cannot be unlocked", "L6: the need line of a coming node")
    clear_bridge()
    Cfg.EXTRA_DUST = 0

    # ------------------------------------------------------------------ L7. Dust rates
    levels({})
    xp = 1000000
    bridge.put("skill:fn:xp", ByTree(dict((tn, xp) for tn in TREES), Long))
    d = fresh_data()
    got = [int(Calc.balance(me, d, t, 50)[2]) for t in range(8)]
    ck(got == [xp // 5, xp // 10, xp // 10, xp // 10, xp // 2, xp // 5, xp // 10, xp // 5], "L7: Dust = XP / rate per tree: %s" % got)
    clear_bridge()

    # ------------------------------------------------------------------ S. the real TreeFx.stats on a stand-in stat map
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    for fname, val in (("HEALTH", 1), ("STAMINA", 2), ("MANA", 3)):
        f = DST.class_.getDeclaredField(fname)
        f.setAccessible(True)
        f.setInt(None, val)
    # EntityStatMap.getComponentType() reads EntityStatsModule.instance (null in a bare JVM -> NPE, caught by stats as STAT_FAILED): an
    # Unsafe-allocated module answers a null component type, which the stand-in CommandBuffer ignores
    ESMod = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    fi = ESMod.class_.getDeclaredField("instance")
    fi.setAccessible(True)
    fi.set(None, U.allocateInstance(ESMod.class_))
    FSM, FCB = JClass("skyytest.FakeStatMap"), JClass("skyytest.FakeCB")
    ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    smap = U.allocateInstance(FSM.class_)
    smap.mods = JClass("java.util.HashMap")()
    smap.val = U.allocateInstance(ESV.class_)
    cb = U.allocateInstance(FCB.class_)
    cb.comp = smap
    vv = JArray(JDouble)(96)
    vv[15], vv[75], vv[89] = 2.0, 4.0, 3.0              # Forest Vigor (Foraging S4), Deep Reserves, Forge Hardened
    Fx.stats(cb, None, me, vv)
    mods = dict((str(k), float(smap.mods.get(k).getAmount())) for k in smap.mods.keySet())
    ck(not bool(Fx.STAT_FAILED), "S: TreeFx.stats ran without its logged-once failure")
    ck(mods == {"1:skyytree_health": 5.0, "3:skyytree_mana": 4.0}, "S: skyytree_health = 2 + 3, skyytree_mana = 4, no stamina modifier: %s" % mods)
    vv[75] = 0.0
    Fx.stats(cb, None, me, vv)
    mods = dict((str(k), float(smap.mods.get(k).getAmount())) for k in smap.mods.keySet())
    ck(mods == {"1:skyytree_health": 5.0}, "S: Deep Reserves 0 removes skyytree_mana: %s" % mods)
    ck(float(Fx.extraStat(me, 0)) == 0.0 and float(Fx.extraStat(me, 2)) == 0.0, "S: the part-2 hook extraStat answers 0 in part 1")

    # ------------------------------------------------------------------ K. the class tree logic (0.3 part 2; a fresh loader)
    lk_ = loader(jar)
    CK_ = K(lk_)
    Cls, Cops, KStore, KCfg, KData, KFx, KDefs, KCalc = (CK_(x) for x in ("TreeClass", "TreeClassOps", "TreeStore", "TreeCfg", "TreeData", "TreeFx", "TreeDefs", "TreeCalc"))
    kdir = os.path.join(SCRATCH, "l", "class", "mods", "Skyy_SkyyTrees")
    os.makedirs(kdir)
    KCfg.FILE = path(os.path.join(kdir, "trees.properties"))
    KStore.DIR = path(os.path.join(kdir, "players"))
    KCfg.load()
    clear_bridge()
    for k_ in list(bridge.keySet()):
        if str(k_).startswith(("class:", "gear:")):
            bridge.remove(k_)
    ck(not bool(KCfg.CLASS_ON) and int(KCfg.AP_FIRST) == 1 and int(KCfg.AP_EVERY) == 2 and int(KCfg.AP_MAX) == 50 and int(KCfg.C_RESPEC_PER) == 100
       and bool(KCfg.C_UNDO) and int(KCfg.C_EXTRA_AP) == 0 and all(bool(x) for x in KCfg.C_ON) and [int(x) for x in KCfg.C_AP][:7] == [1, 1, 1, 1, 2, 1, 1],
       "K2: the class rows load their defaults (class trees OFF)")
    # AP (answer 1): 0 at level 0, 1 at 1, +1 every 2 levels, 50 at 98 and above
    ck([int(Cls.ap(l)) for l in (0, 1, 2, 3, 10, 23, 97, 98, 100)] == [0, 1, 2, 2, 6, 12, 49, 50, 50], "K2: AP = 1 + floor(level / 2) capped at 50: %s" % [int(Cls.ap(l)) for l in (0, 1, 2, 3, 10, 23, 97, 98, 100)])
    KCfg.C_EXTRA_AP = 5
    KCfg.AP_MAX = 10
    ck([int(Cls.ap(l)) for l in (0, 1, 100)] == [5, 6, 15], "K2: debug extra AP and the cap: %s" % [int(Cls.ap(l)) for l in (0, 1, 100)])
    KCfg.C_EXTRA_AP = 0
    KCfg.AP_MAX = 50
    # fix round C: a skill:fn:level that throws or answers no number is -1 (unavailable), never 0

    @JImplements("java.util.function.Function")
    class LvlBad(object):
        def __init__(self, mode):
            self.mode = mode

        @JOverride
        def apply(self, o):
            if self.mode == "throw":
                raise RuntimeError("skills down")
            return "nope"
    bridge.put("skill:fn:level", LvlBad("throw"))
    l1 = int(Cls.level(me, 0))
    bridge.put("skill:fn:level", LvlBad("str"))
    l2 = int(Cls.level(me, 0))
    bridge.remove("skill:fn:level")
    l3 = int(Cls.level(me, 0))
    levels({"Archery": 0})
    l4 = int(Cls.level(me, 0))
    levels({"Archery": 7})
    ck((l1, l2, l3, l4, int(Cls.level(me, 0)), int(Cls.level(me, -1))) == (-1, -1, -1, 0, 7, 0), "K2: level() = -1 on a throwing / non-number / absent skill:fn:level, else the level: %s" % ((l1, l2, l3, l4),))

    def kdata(ids, ci=0):
        d_ = KData()
        for i in ids:
            KStore.setClassOwn(d_, ci, CT_IDX[i], True)
        return d_

    def intact_ids(d_, ci=0):
        it_ = Cls.intact(d_, ci)
        return set(CT_ID[n] for n in range(37) if bool(it_[n]))
    for own_, note_ in (([], "nothing"), (SPINE_OWN, "the spine"), (["P1", "P2", "X1"], "no root"), (["ROOT", "P1", "P2", "X1", "X2", "P3"], "both picks"),
                        (["ROOT", "P1", "A1", "M1A", "A2"], "rune slots"), (["ROOT", "P1", "P2", "X2", "P3", "P4", "C1", "C2", "C3", "C4", "CE", "CS"], "a lane + coming"),
                        (["ROOT", "P2", "P3", "P4", "L1"], "a gap at P1")):
        d_ = kdata(own_)
        ck(intact_ids(d_) == m_intact(set(own_)) and int(Cls.spent(Cls.intact(d_, 0), 0)) == m_spent(m_intact(set(own_))),
           "K3: intact / spent of %s = the model: %s" % (note_, sorted(intact_ids(d_))))
    ck(intact_ids(kdata(["ROOT", "P1", "P2", "X1", "X2", "P3"])) == set(["ROOT", "P1", "P2"]) and intact_ids(kdata(["P1", "P2", "X1"])) == set(), "K3: both picks drop the pair and P3; no root = nothing")
    KCfg.C_ON[1] = False
    ck(intact_ids(kdata(SPINE_OWN)) == set(["ROOT"]), "K3: P1 switched off on the server drops everything after it: %s" % sorted(intact_ids(kdata(SPINE_OWN))))
    KCfg.C_ON[1] = True
    # reader gating + the alias keys
    ck(str(Cls.comingWho(0, CT_IDX["P1"])) == "SkyyGear" and str(Cls.comingWho(0, CT_IDX["A1"])) == "runes (Hytale 0.7)" and str(Cls.comingWho(0, CT_IDX["LE"])) == "SkyyGear's elemental stats (later)"
       and str(Cls.comingWho(0, CT_IDX["R2"])) == "SkyySkills" and str(Cls.comingWho(0, CT_IDX["P3"])) == "SkyySkills" and str(Cls.comingWho(0, CT_IDX["ROOT"])) == ""
       and str(Cls.comingWho(2, CT_IDX["P1"])) == "", "K4: no flags - Strength waits for SkyyGear, crossbows + Mana Regen for SkyySkills, slots for runes / elements")
    bridge.put("gear:tree:readers", "Smithing.SRarity,gear:extras")
    bridge.put("skill:tree:readers", "Class.Archer.R2")
    ck(bool(KCalc.reads("SkyyGear", "gear:extras")) and bool(KCalc.reads("SkyyGear", "Smithing.SRarity")) and not bool(KCalc.coming(84)) and bool(KCalc.coming(87))
       and str(Cls.comingWho(0, CT_IDX["P1"])) == "" and str(Cls.comingWho(0, CT_IDX["R2"])) == "" and str(Cls.comingWho(0, CT_IDX["R3"])) == "SkyySkills",
       "K4: the alias keys gear:tree:readers / skill:tree:readers count like tree:reads:<Mod> (research/Loot-Unid-Spec.md 6)")
    ck(str(KCalc.readerAlias("SkyyGear")) == "gear:tree:readers" and str(KCalc.readerAlias("SkyySacks")) == "sack:tree:readers" and KCalc.readerAlias("SkyyX") is None, "K4: readerAlias")
    clear_bridge()
    bridge.remove("gear:tree:readers")
    bridge.remove("skill:tree:readers")
    # fix round I: a non-String flag counts as nothing and is WARNed once per key (TreeCalc.WARNED)
    KCalc.WARNED.clear()
    bridge.put("tree:reads:SkyyGear", Integer.valueOf(5))
    bridge.put("skill:tree:readers", Boolean.TRUE)
    r1_ = bool(KCalc.reads("SkyyGear", "gear:extras"))
    r2_ = bool(KCalc.reads("SkyyGear", "gear:extras"))
    r3_ = bool(KCalc.reads("SkyySkills", "Class.Archer.R2"))
    ck(not r1_ and not r2_ and not r3_ and sorted(str(k_) for k_ in KCalc.WARNED.keySet()) == ["skill:tree:readers", "tree:reads:SkyyGear"] and int(KCalc.WARNED.size()) == 2,
       "K4: a non-String tree:reads / alias value never counts and is WARNed once per key: %s" % sorted(str(k_) for k_ in KCalc.WARNED.keySet()))
    bridge.remove("tree:reads:SkyyGear")
    bridge.remove("skill:tree:readers")
    KCalc.WARNED.clear()
    # tree:fn:level / bonus for class keys, the stats SkyyTrees applies, the posts - class trees OFF then ON
    KStore.DATA.clear()
    d_ = kdata(["ROOT", "P1", "P2", "X1", "P3", "P4", "L1", "R1", "R2"])
    KStore.DATA.put(str(me), d_)
    bridge.put("class:" + str(me), "Archer")
    levels({"Archery": 40})
    TF, TB = CK_("TreeFn")(), CK_("TreeBonusFn")()
    ck(int(TF.apply(jarr([me, "Class.Archer.R2"]))) == 0 and float(TB.apply(jarr([me, "Class.Archer.R2"]))) == 0.0 and float(Cls.stat(me, 0)) == 0.0,
       "K5: class trees OFF - tree:fn:level / bonus answer 0 for class keys, no stat")
    KCfg.CLASS_ON = True
    ck(int(TF.apply(jarr([me, "Class.Archer.R2"]))) == 1 and float(TB.apply(jarr([me, "Class.Archer.R2"]))) == 2.0 and float(TB.apply(jarr([me, "Class.Archer.R1"]))) == 2.0
       and float(TB.apply(jarr([me, "Class.Archer.R3"]))) == 0.0 and float(TB.apply(jarr([me, "Class.Mage.P1"]))) == 0.0 and float(TB.apply(jarr([me, "Class.Archer.Nope"]))) == 0.0
       and float(TB.apply(jarr([me, "Class.Archer.P1"]))) == 2.0, "K5: class trees ON - Bolt Rack I answers 1 / 2.0, another class or an unknown id 0")
    ck(float(Cls.stat(me, 0)) == 8.0 and float(Cls.stat(me, 2)) == 0.0 and float(Cls.stat(me, 1)) == 0.0 and float(KFx.extraStat(me, 0)) == 8.0,
       "K5: Archer ROOT + P2 = +8 Health, no Mana: %s" % float(Cls.stat(me, 0)))
    REG = []

    @JImplements("java.util.function.Function")
    class RegenK(object):
        @JOverride
        def apply(self, o):
            REG.append([str(o[0]), str(o[2]) if len(o) > 2 else None, float(o[3].doubleValue()) if len(o) > 3 else None])
            return Boolean.TRUE
    bridge.put("skill:fn:manaregen", RegenK())
    Cls.post(me)
    gx = bridge.get("gear:extras:" + str(me))
    ck(gx is not None and str(gx.get("trees")) == "str:11" and REG == [["add", "trees", 5.0]], "K5: post - Strength P1 2 + X1 3 + P4 2 + L1 2 + R1 2 = str:11 in gear:extras, Mana Regen +5 (Focus I) posted: %s %s" % (gx, REG))
    Cls.post(me)
    ck(len(REG) == 1, "K5: an unchanged value is not re-posted")
    KCfg.CLASS_ON = False
    Cls.post(me)
    ck(gx.get("trees") is None and REG[-1] == ["add", "trees", 0.0], "K5: class trees OFF - the Strength entry goes, Mana Regen 0: %s" % REG[-1])
    KCfg.CLASS_ON = True
    Cls.post(me)
    Cls.clear(me)
    ck(gx.get("trees") is None and REG[-1] == ["remove", "trees", None] and Cls.LAST_REGEN.get(me) is None, "K5: clear() takes both back")
    # the stats on the stand-in map (section S's set-up): Health from Forest Vigor + the class, Mana from the class (a Mage)
    bridge.put("class:" + str(me), "Mage")
    levels({"Sorcery": 40})
    KStore.DATA.clear()
    d_ = kdata(["ROOT", "P1", "P2", "X1", "P3"], 2)
    KStore.DATA.put(str(me), d_)
    ck(float(Cls.stat(me, 0)) == 8.0 and float(Cls.stat(me, 2)) == 13.0, "K6: a Mage's spine = +8 Health (ROOT, P3), +13 Mana (P1, X1): %s / %s" % (float(Cls.stat(me, 0)), float(Cls.stat(me, 2))))
    smap2 = U.allocateInstance(FSM.class_)
    smap2.mods = JClass("java.util.HashMap")()
    smap2.val = U.allocateInstance(ESV.class_)
    cb2 = U.allocateInstance(FCB.class_)
    cb2.comp = smap2
    vv2 = JArray(JDouble)(96)
    vv2[15] = 2.0
    KFx.stats(cb2, None, me, vv2)
    mods2 = dict((str(k_), float(smap2.mods.get(k_).getAmount())) for k_ in smap2.mods.keySet())
    ck(mods2 == {"1:skyytree_health": 10.0, "3:skyytree_mana": 13.0}, "K6: skyytree_health = Forest Vigor 2 + class 8, skyytree_mana = class 13: %s" % mods2)
    KCfg.CLASS_ON = False
    KFx.stats(cb2, None, me, vv2)
    mods2 = dict((str(k_), float(smap2.mods.get(k_).getAmount())) for k_ in smap2.mods.keySet())
    ck(mods2 == {"1:skyytree_health": 2.0}, "K6: class trees OFF - only Forest Vigor stays: %s" % mods2)
    KCfg.CLASS_ON = True
    # TreeClassOps directly: a refused coin take changes nothing (atomic), a successful one resets; buy / undo on a hand-made data
    CALLS = []

    @JImplements("java.util.function.Function")
    class CoinsK(object):
        def __init__(self, ok):
            self.ok = ok

        @JOverride
        def apply(self, o):
            CALLS.append(int(o[1].longValue()))
            return Boolean.TRUE if self.ok else Boolean.FALSE
    bridge.put("class:" + str(me), "Archer")
    levels({"Archery": 23})
    KStore.DATA.clear()
    d_ = kdata(SPINE_OWN)
    KStore.DATA.put(str(me), d_)
    undo_ = JClass("java.util.ArrayList")()
    bridge.put("coins:fn:take", CoinsK(False))
    r_ = str(Cops.respec(me, d_, 0, 23, False))
    ck(r_ == "A class respec costs 2,300 coins - you do not have enough" and CALLS == [2300] and all(bool(d_.cown[n]) for n in (0, 1)), "K7: a refused take leaves the tree alone")
    bridge.remove("coins:fn:take")
    ck(str(Cops.respec(me, d_, 0, 23, False)) == "A class respec costs 2,300 coins but SkyyCoins is not loaded" and bool(d_.cown[0]), "K7: no SkyyCoins - refused")
    bridge.put("coins:fn:take", CoinsK(True))
    r_ = str(Cops.respec(me, d_, 0, 23, False))
    ck(r_ == "Respec done - every Ability Point of your Archer tree is back (2,300 coins paid)" and CALLS == [2300, 2300] and not any(bool(x) for x in d_.cown)
       and int(d_.crespecAt[0]) > 0, "K7: the paid respec takes the coins once and resets: %s" % r_)
    ck(str(Cops.respec(me, d_, 0, 23, False)) == "Nothing to respec in your Archer tree", "K7: nothing to respec")
    b1 = str(Cops.buy(me, d_, 0, 23, CT_IDX["P2"], undo_, False))
    b2 = str(Cops.buy(me, d_, 0, 23, 0, undo_, False))
    b3 = str(Cops.buy(me, d_, 0, 23, 0, undo_, False))
    b4 = str(Cops.buy(me, d_, 0, 23, CT_IDX["P1"], undo_, False))
    ck(b1 == "Vitality I needs Might I (P1) first" and b2 == "Unlocked Root! 1 AP spent - 11 left" and b3 == "You already own Root"
       and b4 == "Might I is coming with SkyyGear - it cannot be unlocked yet" and int(undo_.size()) == 1, "K7: buy - the parent rule, an unlock, owned, a coming node: %s / %s / %s / %s" % (b1, b2, b3, b4))
    ck(str(Cops.respec(me, d_, 0, 23, False)) == "You can respec your Archer tree again in 10 min", "K7: the cooldown after a respec")
    KCfg.C_RESPEC_PER = 0
    d_.crespecAt[0] = 0
    ck(str(Cops.respec(me, d_, 0, 23, False)) == "Respec done - every Ability Point of your Archer tree is back" and CALLS == [2300, 2300], "K7: price 0 = free, no coin call")
    KCfg.C_RESPEC_PER = 100
    ck(int(Cls.respecPrice(23)) == 2300 and int(Cls.respecPrice(0)) == 0 and int(Cls.respecPrice(-5)) == 0, "K7: respecPrice")
    # fix round C / N / P / O: an unreadable level refuses, level 0 never waives the cooldown, priceOf / negBalance, the ledger words,
    # the class-qualified Undo list, the live effect text, the continues texts, the live-rows note
    d_ = kdata(SPINE_OWN)
    d_.crespecAt[0] = 0
    ck(str(Cops.respec(me, d_, 0, -1, False)) == "Skill trees need SkyySkills - it is not loaded or did not answer (try again)" and all(bool(d_.cown[n]) for n in (0, 1))
       and str(Cops.buy(me, d_, 0, -1, CT_IDX["C1"], None, False)) == "Skill trees need SkyySkills - it is not loaded or did not answer (try again)", "K7: a level that could not be read refuses respec and buy")
    d0 = kdata(["ROOT"])
    d0.crespecAt[0] = JClass("java.lang.System").currentTimeMillis()
    ck(str(Cops.respec(me, d0, 0, 0, False)).startswith("You can respec your Archer tree again in") and bool(d0.cown[0]) and not bool(Cops.negBalance(d0, 0, 0)),
       "K7: a level-0 read (AP 0 < spent 1) does not waive the cooldown or go free")
    KCfg.AP_MAX = 3
    ck(bool(Cops.negBalance(d_, 0, 23)) and int(Cops.priceOf(d_, 0, 23, False)) == 0, "K7: AP cap 3 under 8 spent = negative balance = price 0")
    KCfg.AP_MAX = 50
    ck(not bool(Cops.negBalance(d_, 0, 23)) and int(Cops.priceOf(d_, 0, 23, False)) == 2300 and int(Cops.priceOf(d_, 0, 23, True)) == 0
       and int(Cops.priceOf(kdata(["P1", "P2", "X1"]), 0, 23, False)) == 0 and int(Cops.priceOf(d_, 0, 0, False)) == 0 and int(Cops.priceOf(KData(), 0, 23, False)) == 0,
       "K7: priceOf = level x perLevel, 0 in the probe / with nothing intact / at level 0 / on an empty tree")
    del CALLS[:]

    @JImplements("java.util.function.Function")
    class CoinsBad(object):
        def __init__(self, mode):
            self.mode = mode

        @JOverride
        def apply(self, o):
            CALLS.append(int(o[1].longValue()))
            if self.mode == "throw":
                raise RuntimeError("ledger down")
            return None
    bridge.put("coins:fn:take", CoinsBad("null"))
    rn = str(Cops.respec(me, d_, 0, 23, False))
    bridge.put("coins:fn:take", CoinsBad("throw"))
    rt = str(Cops.respec(me, d_, 0, 23, False))
    ck(rn == rt == "A class respec costs 2,300 coins - SkyyCoins could not take them right now (nothing changed) - try again" and CALLS == [2300, 2300]
       and all(bool(d_.cown[CT_IDX[i]]) for i in SPINE_OWN), "K7: a null / throwing coins:fn:take is reported as such and the tree stays: %r" % rn)
    bridge.put("coins:fn:take", CoinsK(True))
    rb = str(Cops.respec(me, kdata(["P1", "P2", "X1"]), 0, 23, False))
    ck(rb == "Respec done - every Ability Point of your Archer tree is back" and CALLS == [2300, 2300], "K7: nothing intact = a free respec, no coin call: %r" % rb)
    d2 = kdata([], 2)
    undo2 = JClass("java.util.ArrayList")()
    ck(str(Cops.buy(me, d2, 2, 23, 0, undo2, False)) == "Unlocked Root! 1 AP spent - 11 left" and int(undo2.get(0)) == 2 * 37 + 0, "K7: the Undo list holds class x 37 + node: %s" % undo2)
    ck(str(Cops.undo(me, d2, 0, undo2, False)) == "Nothing to undo - your class changed since those unlocks" and int(undo2.size()) == 0 and bool(d2.cown[2 * 37]),
       "K7: an Undo under another class clears the list and undoes nothing")
    ck(str(Cops.undo(me, d2, 2, undo2, True)) == "Nothing to undo - only unlocks made while this page is open can be undone (probe - not saved)"
       and str(Cops.respec(me, KData(), 2, 23, True)) == "Nothing to respec in your Mage tree (probe - not saved)", "K7: the probe suffix on the empty answers")
    ck(str(Cls.now(0, 0)) == "+4 max Health" and str(Cls.now(2, CT_IDX["P2"])) == "+5% Mana Regen" and str(Cls.now(0, CT_IDX["X1"])) == "+3 Strength"
       and str(Cls.now(0, CT_IDX["R4"])) == "A hotbar crossbow reloads by itself in 30 s" and str(Cls.now(0, CT_IDX["R2"])) == "+2 bolts in a crossbow magazine"
       and str(Cls.now(0, CT_IDX["A1"])) == "Ability rune slot - coming with runes (Hytale 0.7)" and str(Cls.now(-1, 0)) == "", "K7: TreeClass.now fills the amount: %s" % str(Cls.now(0, 0)))
    KCfg.C_AMT[0] = 10
    ck(str(Cls.now(0, 0)) == "+10 max Health" and str(Cops.nowLine(2, 0, 0)) == "Now: +10 max Health" and str(Cops.givesLine(0, 0)) == "Gives: +10 max Health",
       "K7: an admin-edited Amount shows in the detail texts: %s" % str(Cls.now(0, 0)))
    KCfg.C_AMT[0] = 4
    ck(str(Cops.typeLine(0, CT_IDX["P3"])) == "Passive - 1 AP - continues on page 2" and str(Cops.typeLine(0, CT_IDX["P4"])) == "Passive - 1 AP - continues on page 1"
       and str(Cops.typeLine(0, 0)) == "Passive - 1 AP" and str(Cops.typeLine(0, CT_IDX["LE"])) == "Element - Boltslinger lane - 3 AP", "K7: typeLine with the continues texts")
    it_ = Cls.intact(d_, 0)
    n1 = str(Cops.note(0, 23, it_, 4, False, False, None))
    KCfg.AP_FIRST, KCfg.AP_EVERY, KCfg.AP_MAX = 2, 5, 30
    n2 = str(Cops.note(0, 23, it_, 4, False, False, None))
    KCfg.AP_FIRST, KCfg.AP_EVERY, KCfg.AP_MAX = 1, 2, 50
    ck(n1 == "Boltslinger 2 - Trapper 0 - Sharpshooter 0 - Ability Points come from your Archery level (1 + 1 per 2 levels, max 50)"
       and n2.endswith("(2 + 1 per 5 levels, max 30)") and str(Cops.note(-1, 0, it_, 0, False, False, "Assassin")) == "Your class Assassin has no tree yet - it comes in a later build"
       and str(Cops.note(-1, 0, it_, 0, False, False, None)).startswith("Choose a class with /class"), "K7: the note states the live AP rows / the unknown class: %r" % n1)
    pd_ = Cops.probeData(0)
    ck([CT_ID[n] for n in range(37) if bool(pd_.cown[n])] == SPINE_OWN and str(Cops.buy(me, pd_, 0, 30, CT_IDX["C1"], None, True)) == "Unlocked Trapper I! 1 AP spent - 7 left (probe - not saved)"
       and not bool(d_.cown[CT_IDX["C1"]]), "K7: the probe data + a probe buy touch nothing real")
    # /tree class words
    KCfg.CLASS_ON = False
    ck(str(Cls.cmdClass(me, "class")).startswith("[Trees] Class trees are not switched on yet") and Cls.cmdClass(me, "mining") is None and Cls.cmdClass(me, "ass") is None, "K8: /tree class while off, non-class words")
    KCfg.CLASS_ON = True
    ck(str(Cls.cmdClass(me, "class")) == "" and str(Cls.cmdClass(me, "archer")) == "" and str(Cls.cmdClass(me, "ARC")) == "" and str(Cls.cmdClass(me, "mage")) == "[Trees] Your class is Archer - /tree class opens its tree"
       and str(Cls.cmdClass(me, "cla")) == "", "K8: /tree class, /tree archer, another class")
    ck("Server Setup" not in str(Cls.cmdClass(me, "mage")), "K8: the player answer names no admin menu")
    bridge.put("class:" + str(me), "Assassin")
    ck(str(Cls.cmdClass(me, "class")) == "[Trees] Your class Assassin has no skill tree yet - it comes in a later build" and str(Cls.cmdClass(me, "warrior")) == str(Cls.cmdClass(me, "class")),
       "K8 (fix H): a class this build has no tree for is told so: %s" % str(Cls.cmdClass(me, "class")))
    KCfg.CLASS_ON = False
    ck(str(Cls.cmdClass(me, "class")) == "[Trees] Class trees are not switched on yet on this server", "K8: the OFF answer")
    KCfg.CLASS_ON = True
    bridge.remove("class:" + str(me))
    ck(str(Cls.cmdClass(me, "warrior")) == "[Trees] You have no class yet - choose one with /class (or create a profile)" and str(Cls.cmdClass(me, "class")) == "", "K8: no class yet")
    ck(Cls.classOf(me) is None and int(Cls.classIdx("archer")) == 0 and int(Cls.classIdx("Assassin")) == -1 and int(Cls.nodeIdx("m1b")) == CT_IDX["M1B"] and int(Cls.parseKey("Class.Priest.RS")) == 4 * 37 + CT_IDX["RS"]
       and int(Cls.parseKey("Smithing.SRarity")) == -1, "K8: classOf / classIdx / nodeIdx / parseKey")
    bridge.put("profile:class:" + str(me), "Priest")
    bridge.put("class:" + str(me), "Archer")
    ck(str(Cls.classOf(me)) == "Priest", "K8: profile:class wins over class:")
    bridge.remove("profile:class:" + str(me))
    # tree:names follows class.enabled through the kit (Server Setup) and namesPut / namesRemove
    KStore.namesPut()
    ck(str(bridge.get("tree:names")) == ",".join(TREES + ["Class"]) and str(KStore.NAMES_PUT) == ",".join(TREES + ["Class"]), "K9: tree:names + Class while ON")
    KCfg.CLASS_ON = False
    KStore.namesPut()
    ck(str(bridge.get("tree:names")) == ",".join(TREES), "K9: tree:names without Class while OFF")
    KStore.namesRemove()
    ck(bridge.get("tree:names") is None and KStore.NAMES_PUT is None, "K9: namesRemove takes the value back")
    # the Server Setup checks (TreeKit) and the class rows through the kit (a fresh start folder)
    kkit = os.path.join(SCRATCH, "l", "classkit", "mods", "Skyy_SkyyTrees")
    os.makedirs(kkit)
    rk = start(kkit)
    CKit = rk["C"]
    KitFn = CKit("CfgFn")
    ka = KitFn().apply(jarr(["keys", "class.nodes.Archer", ""]))
    kmap = dict(zip([str(x) for x in ka[0]], [str(x) for x in ka[2]]))
    ck(len(ka[0]) == 37 and kmap.get("ROOT") == "true|4|1" and kmap.get("R4") == "true|30|3" and kmap.get("LS") == "true|0|4", "K9: class.nodes.Archer lists 37 entries: %s" % kmap.get("ROOT"))
    kl = KitFn().apply(jarr(["keys", "class.minLevel", ""]))
    ck(dict(zip([str(x) for x in kl[0]], [str(x) for x in kl[2]])) == {"Archer.R2": "15", "Archer.R3": "15", "Archer.R4": "50"}, "K9: class.minLevel lists the three crossbow levels")
    t1 = tset(CKit, "class.nodes.Archer", "ROOT", "true|9|2")
    t2 = tset(CKit, "class.nodes.Archer", "ROOT", "true|9|11")
    t3 = add(CKit, "class.nodes.Archer", "root", "true|4|1")
    t4 = add(CKit, "class.nodes.Archer", "Nope", "true|4|1")
    t5 = tset(CKit, "class.nodes.Archer", "A1", "true|4|1")
    t6 = tset(CKit, "class.nodes.Mage", "P1", "true|500|1")
    t7 = tset(CKit, "class.minLevel", "Archer.R2", "20")
    t8 = add(CKit, "class.minLevel", "Arcer.R2", "20")
    t9 = add(CKit, "class.minLevel", "Archer.r2", "20")
    ck(t1[0] == "confirm" and "Save it anyway" not in (t1[2] or "") and "must be" not in (t1[2] or ""), "K9: ROOT true|9|2 = only the danger confirm: %s" % t1)
    ck(t2[0] == "bad" and "AP must be a whole number from 0 to 10" in (t2[2] or ""), "K9: AP 11 refused: %s" % t2)
    ck(t3[0] == "confirm" and "capitals matter, the node is ROOT" in (t3[2] or ""), "K9: 'root' asks about capitals: %s" % t3)
    ck(t4[0] == "confirm" and "is not a class node" in (t4[2] or ""), "K9: an unknown id asks: %s" % t4)
    ck(t5[0] == "confirm" and "coming slot" in (t5[2] or ""), "K9: a rune slot's line asks (changes nothing yet): %s" % t5)
    ck(t6[0] == "confirm" and "would give +500 max Mana" in (t6[2] or ""), "K9: a huge Mana amount asks: %s" % t6)
    ck(t7[0] == "confirm" and "not" not in (t7[2] or "").lower(), "K9: class.minLevel Archer.R2 20 = the danger confirm only: %s" % t7)
    ck(t8[0] == "confirm" and "is not a class" in (t8[2] or "") and t9[0] == "confirm" and "not a class node id" in (t9[2] or ""), "K9: minLevel with a wrong class / id asks: %s / %s" % (t8, t9))
    s1 = [str(x) if x is not None else None for x in KitFn().apply(jarr(["set", "class.enabled", "true", None, "console", "yes", "console"]))]
    CKit("CfgPub").flush()
    ck(s1[0] == "ok" and bool(CKit("TreeCfg").CLASS_ON) and str(bridge.get("tree:names")) == ",".join(TREES + ["Class"]), "K9: Server Setup switches class trees ON and tree:names gains Class: %s" % s1)
    s2 = [str(x) if x is not None else None for x in KitFn().apply(jarr(["set", "class.enabled", "false", None, "console", "yes", "console"]))]
    CKit("CfgPub").flush()
    ck(s2[0] == "ok" and not bool(CKit("TreeCfg").CLASS_ON) and str(bridge.get("tree:names")) == ",".join(TREES), "K9: ... and OFF again: %s" % s2)
    t10 = tset(CKit, "class.nodes.Archer", "ROOT", "false|4|1", "yes")
    CKit("CfgPub").flush()
    ck(t10[0] == "ok" and not bool(CKit("TreeCfg").C_ON[0]) and int(CKit("TreeCfg").C_AMT[0]) == 4, "K9: switching ROOT off applies live: %s" % t10)
    exp2 = str(KitFn().apply(jarr(["export", "all"])))
    imp2 = [str(x) for x in KitFn().apply(jarr(["import", exp2, None, "console", "preview"]))]
    ck("nothing to change" in (imp2[2] or "").lower(), "K9: export all -> import preview = nothing to change (class rows included)")
    bridge.remove("tree:names")
    clear_bridge()
    for k_ in list(bridge.keySet()):
        if str(k_).startswith(("class:", "gear:")):
            bridge.remove(k_)

    # ------------------------------------------------------------------ M. TreeMig on scratch copies
    LIVE_TP = os.path.join(live, "trees.properties")
    live_before = open(LIVE_TP, "rb").read()
    live_players_before = snap(os.path.join(live, "players"))
    MARK = "skyytrees-0.3-trees"
    ADD_LINES = [str(x) for x in C3("TreeMig").ADD_LINE]
    ADD_KEYS = [str(x) for x in C3("TreeMig").ADD_KEY]
    LOGRE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\tSkyyTrees 0\.3\t-\tupdate\tdust\.perTree\[Mining\]\t(\d+)\t5\tok$")
    COUNT = [0]

    def case(name, body):
        COUNT[0] += 1
        base = os.path.join(SCRATCH, "m", "%02d-%s" % (COUNT[0], re.sub(r"[^a-z0-9]+", "-", name.lower())), "mods", "Skyy_SkyyTrees")
        os.makedirs(base)
        if body is not None:
            open(os.path.join(base, "trees.properties"), "wb").write(body)
        return base

    def block_for(text, skip=()):
        eol = "\r\n" if "\r\n" in text else "\n"
        lines = [l for k, l in zip(ADD_KEYS, ADD_LINES) if not (k and k in skip)]
        pre = "" if not text else (("" if text.endswith("\n") else eol) + eol)
        return pre + "".join(l + eol for l in lines)

    # (1) the live folder, copied
    lc = os.path.join(SCRATCH, "m", "live", "mods", "Skyy_SkyyTrees")
    shutil.copytree(live, lc)
    s0 = snap(lc)
    ck(s0["trees.properties"] == live_before, "M: the copy is the live trees.properties")
    ck(MARK.encode() not in live_before and b"dust.xpPerDust.Mining" not in live_before and b"Alchemy." not in live_before,
       "M: the live file is a pre-0.3 file without a Mining line (the case the update is for)")
    ra = start(lc)
    s1 = snap(lc)
    rb = start(lc)
    s2 = snap(lc)
    x0, x1 = s0["trees.properties"], s1["trees.properties"]
    changed1 = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    newbak = [k for k in changed1 if k.startswith("config-history/") and k.endswith(".bak")]
    ck(changed1 == sorted(["trees.properties", "config-changes.log", "config-history/index.log"] + newbak) and len(newbak) == 1,
       "M live: start 1 writes only trees.properties, config-history (one .bak + index.log) and config-changes.log: %s" % changed1)
    ck(len(newbak) == 1 and s1[newbak[0]] == x0, "M live: the History copy holds the old bytes")
    idx = s1.get("config-history/index.log", b"").decode("utf8").strip().split("\n")
    ck(len(idx) == 1 and idx[0].startswith("Skyy_SkyyTrees~trees.properties#") and idx[0].endswith("\tSkyyTrees 0.3\tbefore the 0.3 Alchemy + Smithing trees update"),
       "M live: the index.log line: %s" % idx)
    clog = s1.get("config-changes.log", b"").decode("utf8").strip().split("\n")
    mm = LOGRE.match(clog[0]) if len(clog) == 1 else None
    ck(mm is not None and mm.group(1) == "10", "M live: one config-changes.log line dust.perTree[Mining] 10 -> 5 in the kit's format: %s" % clog)
    ck(x1 == x0 + block_for(x0.decode("latin-1")).encode("latin-1"), "M live: the new file = the old bytes + exactly the 0.3 block (LF)")
    ck(x1.count(b"\r") == 0 and x1.count(MARK.encode()) == 1, "M live: LF kept, the marker once")
    ck(b"\nclass.enabled=false\n" in x1 and x1.count(b"\nclass.nodes.") == 185 and not bool(ra["C"]("TreeCfg").CLASS_ON), "M live: the class block is appended, class trees stay OFF")
    ck(ra["xp"][0] == 5 and ra["xp"][7] == 5 and ra["xp"][6] == 10 and rb["xp"][0] == 5, "M live: Mining / Smithing 5, Alchemy 10: %s" % ra["xp"])
    ck(ra["mig"].startswith("trees.properties updated for SkyyTrees 0.3: 317 line(s) added") and "was 10" in ra["mig"] and rb["mig"] == "",
       "M live: the INFO line once, nothing at start 2: %r / %r" % (ra["mig"][:120], rb["mig"]))
    ck(sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)) == [], "M live: start 2 writes nothing")
    Cb = rb["C"]
    lgl = [str(x) for x in Cb("CfgFn")().apply(jarr(["log", Integer.valueOf(20)]))]
    mine = [x for x in lgl if "\tSkyyTrees 0.3\t" in x]
    ck(len(mine) == 1 and mine[0].split("\t")[4:8] == ["dust.perTree[Mining]", "10", "5", "ok"], "M live: the kit's log op lists the update line for Undo: %s" % mine)
    kd = Cb("CfgFn")().apply(jarr(["keys", "dust.perTree", ""]))
    ck(dict(zip([str(x) for x in kd[0]], [str(x) for x in kd[2]])).get("Mining") == "5", "M live: Server Setup shows Mining = 5 (= the line's new value: Undo is offered)")
    un = tset(Cb, "dust.perTree", "Mining", "10", "yes")
    Cb("CfgPub").flush()
    s3 = snap(lc)
    ck(un[0] == "ok" and s3["trees.properties"] == x1.replace(b"\ndust.xpPerDust.Mining=5\n", b"\ndust.xpPerDust.Mining=10\n")
       and int(Cb("TreeCfg").XP_T[0]) == 10, "M live: Undo (a tset back to 10) writes only that value and Mining is 10 again: %s" % un)
    rc = start(lc)
    s4 = snap(lc)
    ck(rc["mig"] == "" and rc["xp"][0] == 10 and s4["trees.properties"] == s3["trees.properties"], "M live: start 3 keeps the undone value (marker)")
    ck(open(LIVE_TP, "rb").read() == live_before and snap(os.path.join(live, "players")) == live_players_before, "M: the LIVE files were never written")

    # (2) edited copies
    def two(name, body):
        base = case(name, body)
        a = start(base)
        sa = snap(base)
        b = start(base)
        sb = snap(base)
        return base, a, b, sa, sb

    base, a, b, sa, sb = two("hand-set mining", live_before.replace(b"dust.xpPerDust.Exploration=5\n", b"dust.xpPerDust.Exploration=5\ndust.xpPerDust.Mining=7\n"))
    t0 = live_before.replace(b"dust.xpPerDust.Exploration=5\n", b"dust.xpPerDust.Exploration=5\ndust.xpPerDust.Mining=7\n")
    ck(sa["trees.properties"] == t0 + block_for(t0.decode("latin-1"), skip=("dust.xpPerDust.Mining",)).encode("latin-1")
       and "config-changes.log" not in sa and a["xp"][0] == 7 and "dust.xpPerDust.Mining=7 kept (an admin's value)" in a["mig"],
       "M hand-set: the Mining line is kept (7), not added again, no Undo line, an INFO line: %r" % a["mig"][-160:])
    ck(sb == sa and b["mig"] == "", "M hand-set: start 2 writes nothing")
    crlf = live_before.replace(b"\n", b"\r\n")
    base, a, b, sa, sb = two("crlf", crlf)
    ck(sa["trees.properties"] == crlf + block_for(crlf.decode("latin-1")).encode("latin-1") and sa["trees.properties"].count(b"\n") == sa["trees.properties"].count(b"\r\n"),
       "M CRLF: the block uses CRLF, every old byte kept")
    ck(sb == sa and a["xp"][0] == 5, "M CRLF: start 2 writes nothing")
    nonl = live_before.rstrip(b"\n")
    base, a, b, sa, sb = two("no final newline", nonl)
    ck(sa["trees.properties"] == nonl + b"\n\n" + block_for("x\n").encode("latin-1")[1:] and sb == sa, "M no final newline: one newline added, then the block")
    g20 = live_before.replace(b"\ndust.xpPerDust=10\n", b"\ndust.xpPerDust=20\n")
    base, a, b, sa, sb = two("global 20", g20)
    cl = sa.get("config-changes.log", b"").decode("utf8").strip().split("\n")
    m20 = LOGRE.match(cl[0]) if len(cl) == 1 else None
    ck(m20 is not None and m20.group(1) == "20" and a["xp"][0] == 5 and a["xp"][1] == 20, "M global 20: the Undo line says 20 -> 5: %s" % cl)
    un = tset(b["C"], "dust.perTree", "Mining", "20", "yes")
    b["C"]("CfgPub").flush()
    ck(un[0] == "ok" and int(b["C"]("TreeCfg").XP_T[0]) == 20, "M global 20: Undo restores the old effective rate 20")
    g5 = live_before.replace(b"\ndust.xpPerDust=10\n", b"\ndust.xpPerDust=5\n")
    base, a, b, sa, sb = two("global 5", g5)
    ck("config-changes.log" not in sa and b"dust.xpPerDust.Mining=5" in sa["trees.properties"] and "Mining earns" not in a["mig"],
       "M global 5: the line is added, no Undo line (nothing changed)")
    hand = live_before + b"Alchemy.PExtra.max=30\n"
    base, a, b, sa, sb = two("hand-added alchemy line", hand)
    tx = sa["trees.properties"]
    ck(tx.count(b"Alchemy.PExtra.max=") == 1 and int(a["C"]("TreeCfg").MAX[72]) == 30 and tx == hand + block_for(hand.decode("latin-1"), skip=("Alchemy.PExtra.max",)).encode("latin-1"),
       "M hand-added: the admin's Alchemy.PExtra.max=30 is kept (no second line), max 30")
    base = case("history blocked", live_before)
    open(os.path.join(base, "config-history"), "wb").write(b"not a folder")
    a = start(base, kit=False)
    ck(a["mig"] == "" and open(os.path.join(base, "trees.properties"), "rb").read() == live_before and a["xp"][0] == 5,
       "M history blocked: nothing written (the code default still gives Mining 5)")
    os.remove(os.path.join(base, "config-history"))
    b = start(base)
    ck(b["mig"].startswith("trees.properties updated") and MARK.encode() in open(os.path.join(base, "trees.properties"), "rb").read(),
       "M history blocked: the next start updates")
    old01 = live_before[:live_before.index(b"# ---------- SkyyTrees 0.2 (appended once to a 0.1 file)")]
    base, a, b, sa, sb = two("0.1 file", old01)
    t01 = sa["trees.properties"]
    ck(t01.startswith(old01) and t01.count(b"dust.xpPerDust.Mining=") == 1 and t01.count(b"dust.xpPerDust.Acrobatics=") == 1
       and t01.index(b"SkyyTrees 0.2 (appended once") < t01.index(b"SkyyTrees 0.2.4 (added once)") < t01.index(MARK.encode())
       and sb == sa and a["xp"][0] == 5 and a["xp"][4] == 2, "M 0.1 file: the 0.2-0.2.4 blocks first, then the 0.3 block; a second start writes nothing")
    nomark = b"\n".join(l for l in x1.split(b"\n") if MARK.encode() not in l)
    base, a, b, sa, sb = two("marker removed by hand", nomark)
    ck(sa["trees.properties"] == nomark + b"\n" + (ADD_LINES[0] + "\n").encode("latin-1") and sb == sa and "config-changes.log" not in sa,
       "M marker removed: only the marker line comes back (nothing else, no Undo line); a second start writes nothing")
    base, a, b, sa, sb = two("empty file", b"")
    ck(MARK.encode() in sa["trees.properties"] and sb == sa and a["xp"][0] == 5, "M empty file: updated once")
    # 0.3 part 2: an admin who switched the class tab on by hand before the update keeps the line (kept, not re-added); the loader reads it
    hon = live_before + b"class.enabled=true\nclass.nodes.Archer.ROOT=true,9,2\n"
    base, a, b, sa, sb = two("hand-set class lines", hon)
    tx = sa["trees.properties"]
    ck(tx.count(b"\nclass.enabled=") == 1 and tx.count(b"\nclass.nodes.Archer.ROOT=") == 1 and bool(a["C"]("TreeCfg").CLASS_ON) and int(a["C"]("TreeCfg").C_AMT[0]) == 9
       and int(a["C"]("TreeCfg").C_AP[0]) == 2 and sb == sa, "M hand-set class lines: kept once, read by the loader (class trees ON, ROOT +9 Health for 2 AP): enabled x%d root x%d on %s amt %s ap %s same %s diff %s mig %r"
       % (tx.count(b"\nclass.enabled="), tx.count(b"\nclass.nodes.Archer.ROOT="), bool(a["C"]("TreeCfg").CLASS_ON), int(a["C"]("TreeCfg").C_AMT[0]), int(a["C"]("TreeCfg").C_AP[0]), sb == sa,
          sorted(k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k)), a["mig"][-200:]))

    # ------------------------------------------------------------------ P. player files round trip
    pdir = os.path.join(SCRATCH, "p", "players")
    shutil.copytree(os.path.join(live, "players"), pdir)
    keys = sorted(f[:-11] for f in os.listdir(pdir) if f.endswith(".properties"))
    ck(len(keys) >= 1, "P: live player files copied: %d" % len(keys))
    S3, S25 = C3("TreeStore"), C25("TreeStore")
    S3.DIR = path(pdir)
    S25.DIR = path(pdir)
    JProps = JClass("java.util.Properties")

    def props(f):
        p = JProps()
        ins = JClass("java.io.FileInputStream")(f)
        try:
            p.load(ins)
        finally:
            ins.close()
        return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())

    for k in keys:
        fp = os.path.join(pdir, k + ".properties")
        before = props(fp)
        d25, d3 = S25.readFile(k), S3.readFile(k)
        ck(not bool(d3.bad) and not bool(d3.mig) and [int(x) for x in d3.lv][:72] == [int(x) for x in d25.lv]
           and [bool(x) for x in d3.off][:72] == [bool(x) for x in d25.off] and [int(x) for x in d3.respecAt][:6] == [int(x) for x in d25.respecAt]
           and [int(x) for x in d3.credit][:6] == [int(x) for x in d25.credit] and bool(d3.quiet) == bool(d25.quiet)
           and bool(d3.noteSwing) == bool(d25.noteSwing) and str(d3.name) == str(d25.name), "P %s: 0.3 reads the 0.2.5 parts exactly like 0.2.5" % k)
        ck(all(int(x) == 0 for x in list(d3.lv)[72:]), "P %s: the new trees start empty" % k)
        S3.DATA.clear()
        S3.install(k, me, d3)
        ck(bool(S3.saveNow(k)) and props(fp) == before, "P %s: saved by 0.3 = the same Properties" % k)
        d3.lv[75] = 2
        S3.saveNow(k)
        ck(props(fp).get("Alchemy.PMana") == "2", "P %s: an Alchemy level is saved (Alchemy.PMana=2)" % k)
        d25b = S25.readFile(k)
        ck([int(x) for x in d25b.lv] == [int(x) for x in d25.lv], "P %s: 0.2.5 reads the 0.3 file with its six trees unchanged" % k)
        S25.DATA.clear()
        S25.install(k, me, d25b)
        S25.saveNow(k)
        d3b = S3.readFile(k)
        ck(int(d3b.lv[75]) == 0 and "Alchemy.PMana" not in props(fp), "P %s: saved by 0.2.5 the Alchemy level is DROPPED (the rollback floor)" % k)
        # 0.3 part 2: class picks round-trip through 0.3 (unknown Class.* lines kept) and are DROPPED by a 0.2.5 save (the same floor)
        d3c = S3.readFile(k)
        S3.DATA.clear()
        S3.install(k, me, d3c)
        d3c.cown[0] = True
        d3c.cown[1] = True
        d3c.crespecAt[2] = 777
        d3c.cextra.add(JArray(JString)(["Class.Assassin", "ROOT,P1"]))
        S3.saveNow(k)
        pp = props(fp)
        ck(pp.get("Class.Archer") == "ROOT,P1" and pp.get("Class.Mage.respecAt") == "777" and pp.get("Class.Assassin") == "ROOT,P1" and pp.get("v") == "2",
           "P %s: Class.Archer / Class.Mage.respecAt / the kept Class.Assassin line are saved, still v=2" % k)
        d3d = S3.readFile(k)
        ck(bool(d3d.cown[0]) and bool(d3d.cown[1]) and not bool(d3d.cown[2]) and int(d3d.crespecAt[2]) == 777 and d3d.cextra.size() == 1
           and str(d3d.cextra.get(0)[0]) == "Class.Assassin",
           "P %s: 0.3 reads its class lines back" % k)
        d25c = S25.readFile(k)
        S25.DATA.clear()
        S25.install(k, me, d25c)
        S25.saveNow(k)
        ck("Class.Archer" not in props(fp) and "Class.Assassin" not in props(fp), "P %s: saved by 0.2.5 the class picks are DROPPED (the rollback floor)" % k)
    json.dump(R, open(out, "w"), indent=1)
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================ child: the engine-access audit (section Z)
def run_audit(jar, fake, out):
    """every class / field / method / constructor reference in the jar looked up with a MethodHandles.Lookup IN the referencing class
    (MethodHandles.privateLookupIn: the JVM's own access rules). Copied from SkyySkills/test_skyyskills_0.4.13.py section Z. Control:
    skyytest.BadAccess must be refused."""
    import skyybuild as B
    from jpype import JClass
    _jvm_start([B.JAVASSIST, jar, fake], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, jar, fake):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass("skyytest.LookupIn"), JClass("java.lang.invoke.MethodType"),
                              JClass("javassist.bytecode.ConstPool"), JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    # a CALLER-SENSITIVE JDK method (Method.invoke, Field.get ...) cannot be looked up through a private lookup at all
                    # ("restricted lookup object") - the lookup API, not an access rule: allowed exactly when it is public in a public class
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9):
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                cs_.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n

    cs_ = set()
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": [], "per": {}}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
        res["per"][cn.rsplit(".", 1)[-1]] = k_
    res["control"] = lookup_audit("skyytest.BadAccess")[0]
    res["caller_sensitive"] = sorted(cs_)
    json.dump(res, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================ parent: markup model (the 0.2.5 harness's,
# unchanged: SkyyClasses/test_skyyclasses_0.1.8.py part Y + SkyyProfiles/test_skyyprofiles_0.1.3.py; a Button's style background and a
# full-size cover Group count as backgrounds for the contrast of the labels after them - the kit's icon cells)
def js(v):
    """The Java string a Set command carries (its data is JSON); non-strings come back as their JSON text."""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:      # UICommandBuilder.set(String, String) sends {"0": value}
        x = x["0"]
    return x if isinstance(x, str) else v


_OPEN = re.compile(r"([A-Z][A-Za-z]*)(?:\s+#([A-Za-z0-9]+))?\s*\{")
_PROP = re.compile(r"([A-Za-z]+)\s*:")
_ID_RE = re.compile(r"(?:^|[;{}])\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9]+)\s*\{")
_TEXT_RE = re.compile(r'\bText: "((?:[^"\\]|\\.)*)"')
_COL_RE = re.compile(r"(?:Background|TextColor|Color):\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)")


def parse_markup(mk):
    """The element tree of one inline markup: [{"type", "id", "props": {name: raw value}, "kids": [...]}] (quotes respected)."""
    pos, n = [0], len(mk)

    def ws():
        while pos[0] < n and mk[pos[0]] in " \t\r\n":
            pos[0] += 1

    def value():
        start, depth = pos[0], 0
        while pos[0] < n:
            c = mk[pos[0]]
            if c == '"':
                pos[0] += 1
                while mk[pos[0]] != '"':
                    pos[0] += 2 if mk[pos[0]] == "\\" else 1
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == ";" and depth == 0:
                v = mk[start:pos[0]].strip()
                pos[0] += 1
                return v
            pos[0] += 1
        raise ValueError("property without ';': %s" % mk[start:start + 60])

    def elem():
        m = _OPEN.match(mk, pos[0])
        if not m:
            raise ValueError("no element at: %s" % mk[pos[0]:pos[0] + 60])
        node = {"type": m.group(1), "id": m.group(2), "props": {}, "kids": []}
        pos[0] = m.end()
        while True:
            ws()
            if pos[0] >= n:
                raise ValueError("unclosed element %s" % node["type"])
            if mk[pos[0]] == "}":
                pos[0] += 1
                return node
            if _OPEN.match(mk, pos[0]):
                node["kids"].append(elem())
                continue
            m2 = _PROP.match(mk, pos[0])
            if not m2:
                raise ValueError("unexpected markup at: %s" % mk[pos[0]:pos[0] + 60])
            pos[0] = m2.end()
            node["props"][m2.group(1)] = value()

    out = []
    while True:
        ws()
        if pos[0] >= n:
            return out
        out.append(elem())


def _pairs(v):
    """'(Width: 10, Top: -3)' -> {"Width": 10, "Top": -3}"""
    out = {}
    if not v:
        return out
    inner = v.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]
    for part in inner.split(","):
        if ":" in part:
            k, x = part.split(":", 1)
            try:
                out[k.strip()] = int(x.strip())
            except ValueError:
                pass
    return out


def _box4(d, h_key="Horizontal", v_key="Vertical"):
    f = d.get("Full")
    hz, vt = d.get(h_key, f), d.get(v_key, f)
    return (d.get("Left", hz), d.get("Right", hz), d.get("Top", vt), d.get("Bottom", vt))


def build_tree(appends):
    """One tree of every (parent, markup) append of a page: returns (root node, {id: node})."""
    ids, root = {}, None
    for parent, mk in appends:
        nodes = parse_markup(mk)
        for nd in nodes:
            stack = [nd]
            while stack:
                x = stack.pop()
                if x["id"]:
                    ids[x["id"]] = x
                stack.extend(x["kids"])
        if parent is None:
            root = nodes[0]
        else:
            ids[parent]["kids"].extend(nodes)
    return root, ids


def layout(root, issues):
    """Place every element (LayoutMode Top / Left / none, Anchor margins, Width / Height, Padding, Full); records every child that
    leaves its parent's content box in issues (decorations with a negative anchor are skipped)."""
    order = []
    a0 = _pairs(root["props"].get("Anchor"))
    todo = [(root, 0, 0, a0.get("Width", 0), a0.get("Height", 0), "root")]
    while todo:
        nd, x, y, w, h, path = todo.pop(0)
        nd["box"] = (x, y, w, h)
        order.append(nd)
        pl, pr_, pt, pb = (v or 0 for v in _box4(_pairs(nd["props"].get("Padding"))))
        ix, iy, iw, ih = x + pl, y + pt, w - pl - pr_, h - pt - pb
        nd["inner"] = (ix, iy, iw, ih)
        mode = nd["props"].get("LayoutMode")
        cur = 0
        name = nd["id"] or nd["type"]
        for k in nd["kids"]:
            a = _pairs(k["props"].get("Anchor"))
            l, r, t, bt = _box4(a)
            kid = "%s>%s" % (path, k["id"] or k["type"])
            if any(v is not None and v < 0 for v in (l, r, t, bt)):
                continue
            if a.get("Full") is not None and mode is None:
                f = a["Full"]
                todo.append((k, ix + f, iy + f, iw - 2 * f, ih - 2 * f, kid))
                continue
            if mode == "Top":
                kw = a.get("Width", iw - (l or 0) - (r or 0))
                kh = a.get("Height")
                if kh is None:
                    kh = ih - cur - (t or 0) - (bt or 0)
                cur += t or 0
                ky, kx = iy + cur, ix + (l or 0)
                cur += kh + (bt or 0)
                if cur > ih:
                    issues.append("%s: children of #%s need %d px of %d (LayoutMode Top)" % (kid, name, cur, ih))
                if (l or 0) + kw + (r or 0) > iw:
                    issues.append("%s: %d px wide in #%s's %d" % (kid, (l or 0) + kw + (r or 0), name, iw))
            elif mode == "Left":
                kh = a.get("Height", ih - (t or 0) - (bt or 0))
                kw = a.get("Width")
                if kw is None:
                    kw = iw - cur - (l or 0) - (r or 0)
                cur += l or 0
                kx, ky = ix + cur, iy + (t or 0)
                cur += kw + (r or 0)
                if cur > iw:
                    issues.append("%s: children of #%s need %d px of %d (LayoutMode Left)" % (kid, name, cur, iw))
                if (t or 0) + kh + (bt or 0) > ih:
                    issues.append("%s: %d px high in #%s's %d" % (kid, (t or 0) + kh + (bt or 0), name, ih))
            else:
                kw, kh = a.get("Width"), a.get("Height")
                if kw is None:
                    kw, kx = iw - (l or 0) - (r or 0), ix + (l or 0)
                else:
                    kx = ix + (l if l is not None else (iw - r - kw if r is not None else (iw - kw) // 2))
                if kh is None:
                    kh, ky = ih - (t or 0) - (bt or 0), iy + (t or 0)
                else:
                    ky = iy + (t if t is not None else (ih - bt - kh if bt is not None else (ih - kh) // 2))
                if kx < ix or ky < iy or kx + kw > ix + iw or ky + kh > iy + ih:
                    issues.append("%s: box %s outside #%s's content box %s" % (kid, (kx, ky, kw, kh), name, (ix, iy, iw, ih)))
            todo.append((k, kx, ky, kw, kh, kid))
        nd["used"] = cur
    return order


def body_fill(ids, body_id):
    nd = ids[body_id]
    tot = 0
    for k in nd["kids"]:
        a = _pairs(k["props"].get("Anchor"))
        _l, _r, t, bt = _box4(a)
        tot += (t or 0) + a.get("Height", 0) + (bt or 0)
    return tot, nd["inner"][3]


# ---------------------------------------------------------------------------- text (the client's own glyph advances)
_FONTS = {}


def font_table(bold, secondary=False):
    import skyyui as SUI
    name = "Lexend-Bold" if secondary else ("NunitoSans-ExtraBold" if bold else "NunitoSans-Medium")
    if name in _FONTS:
        return _FONTS[name]
    p = os.path.join(SUI.GAME_DIR, "Client", "Data", "Shared", "UI", "Fonts", name + ".json")
    if not os.path.isfile(p):
        _FONTS[name] = None
        return None
    d = json.load(open(p, encoding="utf8"))
    adv = dict((g["unicode"], g["advance"]) for g in d["glyphs"])
    _FONTS[name] = (adv, d["metrics"]["lineHeight"])
    return _FONTS[name]


def text_w(text, size, bold, upper, secondary=False):
    ft = font_table(bold, secondary)
    if ft is None:
        return None
    adv = ft[0]
    t = text.upper() if upper else text
    return sum(adv.get(ord(c), adv.get(ord("M"), 0.8)) for c in t) * size


def wrap_lines(text, width, size, bold, upper):
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        cand = wd if not cur else cur + " " + wd
        if text_w(cand, size, bold, upper) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return len(lines), max(text_w(x, size, bold, upper) for x in lines)


def _style(props):
    st_ = props.get("Style", "")
    fs = re.search(r"FontSize: (\d+)", st_)
    col = re.search(r"TextColor: (#[0-9A-Fa-f]{6,8}(?:\([0-9.]+\))?)", st_)
    return {"size": int(fs.group(1)) if fs else 16, "bold": "RenderBold: true" in st_, "upper": "RenderUppercase: true" in st_,
            "wrap": "Wrap: true" in st_, "secondary": 'FontName: "Secondary"' in st_, "color": col.group(1) if col else None}


def check_texts(name, order, sets, counts):
    if font_table(False) is None:
        counts["text_skipped"] = True
        return
    for nd in order:
        if nd["type"] == "Label":
            st_ = _style(nd["props"])
            txt = sets.get(nd["id"]) if nd["id"] and nd["id"] in sets else None
            if txt is None:
                m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
                txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, h = nd["inner"]
            lh = font_table(st_["bold"], st_["secondary"])[1]
            if st_["wrap"]:
                nl, widest = wrap_lines(txt, w, st_["size"], st_["bold"], st_["upper"])
                need = nl * lh * st_["size"]
                ok = need <= h + 0.1 * st_["size"] and widest <= w
                check(ok, "%s: #%s %d lines need %.1f px of %d (%r)" % (name, nd["id"], nl, need, h, txt))
                counts["wrapped"] += 1
                counts["max_lines_fill"] = max(counts["max_lines_fill"], need / float(h))
            else:
                tw = text_w(txt, st_["size"], st_["bold"], st_["upper"], st_["secondary"])
                check(tw <= w, "%s: #%s text %.0f px in %d px (%r)" % (name, nd["id"] or "label", tw, w, txt))
                check(st_["size"] + 4 <= h, "%s: #%s a %d px line in %d px" % (name, nd["id"], st_["size"], h))
                counts["lines"] += 1
                counts["max_line_fill"] = max(counts["max_line_fill"], tw / float(w))
                if tw / float(w) >= counts["widest"][0]:
                    counts["widest"] = (tw / float(w), "%s #%s %.0f/%d px" % (name, nd["id"], tw, w))
        elif nd["type"] == "TextButton":
            m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
            txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, _h = nd["inner"]
            at17 = text_w(txt, 17, True, True)
            at12 = text_w(txt, 12, True, True)
            check(at12 <= w, "%s: button #%s %r does not fit even at 12 px (%.0f of %d)" % (name, nd["id"], txt, at12, w))
            counts["buttons"] += 1
            if at17 > w:
                counts["shrunk"].add("%s (%.0f/%d)" % (txt, at17, w))


# ---------------------------------------------------------------------------- contrast (WCAG ratio on the effective background)
_PATCH_CENTRE = [None]


def patch_centre():
    if _PATCH_CENTRE[0] is not None:
        return _PATCH_CENTRE[0]
    import skyyui as SUI
    z = zipfile.ZipFile(SUI.ASSETS_ZIP)
    path = SUI._zip_path(SUI.TEX["patch"])
    data = z.read(path if path in z.namelist() else path[:-4] + "@2x.png")
    pos, idat, w = 8, b"", None
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _c, _f, inter = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and ctype in (2, 6) and inter == 0, (depth, ctype, inter)
            bpp = 4 if ctype == 6 else 3
        elif typ == b"IDAT":
            idat += body
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _y in range(h):
        f, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b_, c = prev[x], (prev[x - bpp] if x >= bpp else 0)
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b_) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b_) // 2) & 255
            elif f == 4:
                pp = a + b_ - c
                pa, pb, pc = abs(pp - a), abs(pp - b_), abs(pp - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else (b_ if pb <= pc else c))) & 255
        rows.append(line)
        prev = line
    px = rows[h // 2][(w // 2) * bpp:(w // 2) * bpp + 3]
    _PATCH_CENTRE[0] = (px[0], px[1], px[2])
    return _PATCH_CENTRE[0]


def _rgba(c):
    m = re.fullmatch(r"#([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?(?:\(\s*([0-9.]+)\s*\))?", c.strip())
    hx = m.group(1)
    a = float(m.group(3)) if m.group(3) else (int(m.group(2), 16) / 255.0 if m.group(2) else 1.0)
    return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), a


def _over(top, base):
    r, g, b, a = top
    return tuple(a * c + (1 - a) * d for c, d in zip((r, g, b), base))


def _lum(rgb):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = _lum(fg), _lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


_BTN_BG = re.compile(r"Default:\s*\(Background:\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)\)")


def check_contrast(name, root, counts):
    import skyyui as SUI
    stack = [(root, None)]
    while stack:
        nd, bg = stack.pop()
        b = nd["props"].get("Background", "")
        if SUI.TEX["patch"] in b:
            bg = patch_centre()
        elif b.startswith("#") and bg is not None:
            bg = _over(_rgba(b), bg)
        elif b and not b.startswith("#"):
            bg = None
        if nd["type"] == "Button" and bg is not None:
            m = _BTN_BG.search(nd["props"].get("Style", ""))
            if m:
                bg = _over(_rgba(m.group(1)), bg)
        if nd["type"] == "Label" and bg is not None:
            col = _style(nd["props"])["color"]
            if col:
                r = contrast(_over(_rgba(col), bg), bg)
                check(r >= MIN_CONTRAST, "%s: #%s colour %s on %s = %.2f:1 (< %.1f)" % (
                    name, nd["id"] or "label", col, "#%02x%02x%02x" % tuple(int(round(v)) for v in bg), r, MIN_CONTRAST))
                counts["contrasts"] += 1
                if r < counts["min_contrast"][0]:
                    counts["min_contrast"] = (r, "%s #%s %s" % (name, nd["id"] or "label", col))
        if nd["type"] != "TextButton":
            kid_bg = bg
            for k in nd["kids"]:
                stack.append((k, kid_bg))
                a = _pairs(k["props"].get("Anchor"))
                kb = k["props"].get("Background", "")
                if a.get("Full") == 0 and kb.startswith("#") and kid_bg is not None and not k["kids"]:
                    kid_bg = _over(_rgba(kb), kid_bg)


# ---------------------------------------------------------------------------- per state
def ids_of(state):
    out = []
    for t, sel, data, text in state["commands"]:
        if t == "AppendInline" and text:
            out += _ID_RE.findall(text)
    return out


def sets_of(state):
    return dict((sel.lstrip("#")[:-len(".Text")], js(data)) for t, sel, data, text in state["commands"]
                if t == "Set" and sel and sel.endswith(".Text"))


def texts_of(state):
    inl = [x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _TEXT_RE.findall(text) if x]
    return set(inl) | set(v for v in sets_of(state).values() if v)


def strip_new_tabs(events):
    return [e for e in events if e[1] not in NEW_TABS]


def check_state(name, new, SUI, counts, page_colors, class_tab=False, class_page=False):
    """the 0.3 page as the client gets it (the 0.2.5 harness's compare_state minus the old-vs-new part). 0.3 part 2: class_tab = the
    class tab is in tab row 2; class_page = the page IS the class tab (its well holds the rune strip + 6 slot rows, or the no-class label)"""
    check(new["error"] is None, "%s: the page built (%s)" % (name, new["error"]))
    if new["error"]:
        return None
    ap = SUI.Appends()
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in page_colors)
    size = 0
    for idx, (t, sel, data, text) in enumerate(new["commands"]):
        if t == "AppendInline":
            parent = None if sel is None else sel.lstrip("#")
            check(idx != 0 or parent is None, "%s: the first append is the page root" % name)
            try:
                SUI.check_markup(text, prefix=PREFIX, root=(parent is None))
            except ValueError as e:
                check(False, "%s: check_markup: %s" % (name, e))
            ap.append((parent, text))
            size += len(text)
            for c in _COL_RE.findall(text):
                check(SUI.norm_color(c) in allowed, "%s: colour %s is a kit / data colour" % (name, c))
                counts["colours"] += 1
            for bad in ("Width: 0,", "Width: 0)", "FlexWeight", "WrapMaxLines", "LetterSpacing", "LayoutMode: Right", "LayoutMode: Center",
                        "LayoutMode: Full", "ItemGrid"):
                check(bad not in text, "%s: no %s in %s" % (name, bad.strip(",)"), text[:80]))
        elif t == "Set":
            ident, prop = sel.lstrip("#").rsplit(".", 1)
            ap.sets.append((ident, prop, js(data)))
            size += len(data or "")
    counts["max_payload"] = max(counts["max_payload"], size)
    try:
        SUI.check_page(ap, PREFIX)
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
    try:
        SUI.assert_proven(ap, what=name)
        counts["proven"] += 1
    except SUI.UnprovenError as e:
        check(False, "%s: %s" % (name, e))
    counts["appends"] += len(ap)
    root, ids = build_tree(ap)
    a0 = _pairs(root["props"].get("Anchor"))
    check((a0.get("Width"), a0.get("Height")) == (PAGE_W, PAGE_H), "%s: page root %s x %s (want %d x %d)" % (
        name, a0.get("Width"), a0.get("Height"), PAGE_W, PAGE_H))
    for e in new["events"]:
        check(e[1] and e[1].lstrip("#") in ids, "%s: binding target %s exists" % (name, e[1]))
    grid = ids.get("SkyyTrGrid")
    check(grid is not None and SUI.norm_color(grid["props"].get("Background", "")) == SUI.norm_color(SUI.COLOR["well"])
          and _pairs(grid["props"].get("Padding")) == {"Full": SUI.WELL_LIST_PAD} and grid["props"].get("LayoutMode") == "Top",
          "%s: the node grid #SkyyTrGrid is the vanilla list well" % name)
    if grid is not None:
        rows = [k["id"] for k in grid["kids"]]
        if class_page:
            check(rows == ["SkyyTrNoClass"] or rows == ["SkyyTrRs"] + ["SkyyTrCR%d" % r for r in range(6)], "%s: the rune strip + six slot rows (or the no-class label) sit on the grid well (%s)" % (name, rows))
        else:
            check(len(rows) == 6 and all(r and r.startswith("SkyyTrRow") for r in rows), "%s: the six tier rows sit on the grid well (%s)" % (name, rows))
        counts["grid_well"] += 1
    # 0.3: the two tab rows
    h1, h2 = ids.get("SkyyTrHead"), ids.get("SkyyTrHead2")
    k1 = [k["id"] for k in (h1 or {"kids": []})["kids"]]
    k2 = [k["id"] for k in (h2 or {"kids": []})["kids"]]
    check(k1 == ["SkyyTrTab0", "SkyyTrTab1", "SkyyTrTab2", "SkyyTrTab3", "SkyyTrTab6", "SkyyTrTab7", "SkyyTrLvl"]
          and k2 == ["SkyyTrTab4", "SkyyTrTab5"] + (["SkyyTrTab8"] if class_tab else []), "%s: tab row 1 = %s, row 2 = %s" % (name, k1, k2))
    if h1 is not None and h2 is not None:
        firsts = [k for k in h1["kids"] + h2["kids"] if k["id"] in ("SkyyTrTab0", "SkyyTrTab4")]
        others = [k for k in h1["kids"] + h2["kids"] if k["id"] and k["id"].startswith("SkyyTrTab") and k["id"] not in ("SkyyTrTab0", "SkyyTrTab4")]
        check(all("Left" not in _pairs(k["props"].get("Anchor")) for k in firsts) and all(_pairs(k["props"].get("Anchor")).get("Left") == 5 for k in others),
              "%s: the left margin restarts at the first tab of each row" % name)
        counts["tab_rows"] += 1
    issues = []
    order = layout(root, issues)
    check(not issues, "%s: layout: %s" % (name, issues[:4]))
    counts["placed"] += len(order)
    tot, inner = body_fill(ids, BODY_ID)
    check(inner == BODY_INNER_H and tot == BODY_INNER_H, "%s: the body children fill %d px exactly (got %d of %d)" % (name, BODY_INNER_H, tot, inner))
    for nd in order:
        if nd["props"].get("LayoutMode") == "Left" and nd["kids"]:
            counts["min_row_slack"] = min(counts["min_row_slack"], nd["inner"][2] - nd["used"])
    check_texts(name, order, dict((i, v) for i, p, v in ap.sets if p == "Text"), counts)
    check_contrast(name, root, counts)
    counts["states"] += 1
    return ids


def compare_state(name, old, new, SUI, counts, page_colors):
    """a 0.2.5 tree: the 0.3 page = the 0.2.5 page plus the two new tab bindings; every old id and text kept; then check_state"""
    check(old["error"] is None and new["error"] is None, "%s: the page built in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return None
    check(old["events"] == strip_new_tabs(new["events"]) and len(new["events"]) == len(old["events"]) + 2,
          "%s: event bindings identical but the two new tabs (%d / %d)" % (name, len(old["events"]), len(new["events"])))
    counts["bindings"] += len(new["events"])
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni))
    check(not miss, "%s: no old id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    ot, nt = texts_of(old), texts_of(new)
    lost = sorted(ot - nt, key=str)
    check(not lost, "%s: old texts no longer shown: %s" % (name, lost))
    counts["texts"] += len(ot)
    return check_state(name, new, SUI, counts, page_colors)


def new_counts():
    return dict(states=0, bindings=0, ids=0, texts=0, colours=0, check_page=0, proven=0, appends=0, placed=0, min_row_slack=10 ** 6,
                wrapped=0, lines=0, buttons=0, max_lines_fill=0.0, max_line_fill=0.0, widest=(0.0, ""), shrunk=set(), text_skipped=False,
                contrasts=0, min_contrast=(99.0, ""), max_payload=0, grid_well=0, tab_rows=0)


def report_counts(counts, what):
    print("%s %d states: %d bindings, %d old ids kept, %d old texts shown; %d check_page + %d assert_proven / %d appends, %d colours audited, "
          "grid on the well in %d, two tab rows in %d, %d elements placed (tightest Left row slack %d px), largest payload %d chars" % (
              what, counts["states"], counts["bindings"], counts["ids"], counts["texts"], counts["check_page"], counts["proven"],
              counts["appends"], counts["colours"], counts["grid_well"], counts["tab_rows"], counts["placed"], counts["min_row_slack"],
              counts["max_payload"]))
    if counts["text_skipped"]:
        print("   text widths: SKIPPED (no client glyph tables)")
    else:
        print("   text: %d single lines (widest %.0f%%: %s), %d wrapped labels (fullest %.0f%% of their height), %d buttons%s" % (
            counts["lines"], 100 * counts["widest"][0], counts["widest"][1], counts["wrapped"], 100 * counts["max_lines_fill"],
            counts["buttons"], (" (shrink-to-fit at 17 px: %s)" % ", ".join(sorted(counts["shrunk"]))) if counts["shrunk"] else ""))
    print("   contrast: %d labels, lowest %.2f:1 (%s)" % (counts["contrasts"], counts["min_contrast"][0], counts["min_contrast"][1]))


# ============================================================================================ parent
def cleanup(created, before):
    if created:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        return
    for e in OWN_ENTRIES:
        p = os.path.join(SCRATCH, e)
        if e in before or not os.path.exists(p):
            continue
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        else:
            os.remove(p)


def main():
    if "--states" in sys.argv:
        run_states(arg("--states"), arg("--out"), arg("--tag"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    if "--mkfake" in sys.argv:
        run_mkfake(arg("--mkfake"))
        return
    if "--logic" in sys.argv:
        run_logic(arg("--logic"), arg("--old"), arg("--fake"), arg("--live"), arg("--out"))
        return
    if "--audit" in sys.argv:
        run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
    for j, ver in ((JAR, VERSION), (OLD_JAR, OLD_VERSION)):
        if not os.path.isfile(j):
            sys.exit("no %s jar at %s - build it first (python SkyyTrees/build_skyytrees_%s.py, without --deploy)" % (ver, j, ver))
    if not os.path.isfile(os.path.join(LIVE_DIR, "trees.properties")):
        sys.exit("the live trees.properties is not at %s (pass --live <folder>; it is only ever read and copied)" % LIVE_DIR)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/, not %s" % SCRATCH)
    created = not os.path.exists(SCRATCH)
    before = set(os.listdir(SCRATCH)) if not created else set()
    for e in ("l", "m", "p", "fake"):
        if e in before:
            sys.exit("%s already holds a '%s' entry - pass an empty --dir" % (SCRATCH, e))
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    me = os.path.abspath(__file__)
    outs = {}
    try:
        for tag, j in (("new", JAR), ("old", OLD_JAR)):
            outs[tag] = os.path.join(SCRATCH, "states-%s.json" % tag)
            p = subprocess.run([sys.executable, me, "--states", j, "--out", outs[tag], "--tag", tag, "--dir", SCRATCH], env=env,
                               stderr=subprocess.PIPE, encoding="utf8", errors="replace")
            sys.stderr.write("".join(l + "\n" for l in (p.stderr or "").splitlines() if "Picked up JAVA_TOOL_OPTIONS" not in l))
            check(p.returncode == 0 and os.path.isfile(outs[tag]), "state child JVM for %s ran" % j)
            check("mutated reflectively" not in (p.stderr or ""), "F: the %s state child mutated no final field without the JEP 500 option" % tag)
        bco = os.path.join(SCRATCH, "bytecode.json")
        p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(bco), "bytecode child ran")
        fake = os.path.join(SCRATCH, "fake")
        p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and all(os.path.isfile(os.path.join(fake, "skyytest", n + ".class")) for n in ("FakeCB", "FakeStatMap", "LookupIn", "BadAccess")),
              "the stand-in classes were generated")
        lo = os.path.join(SCRATCH, "logic.json")
        p = subprocess.run([sys.executable, me, "--logic", JAR, "--old", OLD_JAR, "--fake", fake, "--live", LIVE_DIR, "--out", lo, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(lo), "logic child ran")
        au = os.path.join(SCRATCH, "audit.json")
        p = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", au, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(au), "engine-access audit child ran")
        if os.path.isfile(outs.get("new", "")) and os.path.isfile(outs.get("old", "")) and os.path.isfile(bco):
            run_parent(outs, bco, lo, au)
    finally:
        if not KEEP:
            cleanup(created, before)
    print("SkyyTrees %s vs %s: %d checks passed, %d failed" % (VERSION, OLD_VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyTrees %s bare-JVM harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(0 if not FAILS else 1)


def run_parent(outs, bco, lo, au):
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    # ---- A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                            os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    if new["load_fails"] or old["load_fails"]:
        return
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    tcolor = eval(re.search(r"^TCOLOR = (\[.*?\])\n", src, re.M).group(1))
    ccolor = eval(re.search(r"^CCOLOR = (\[.*?\])\r?\n", src, re.M).group(1))
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (.*?)\r?\n", src, re.M).group(1), {"TCOLOR": tcolor, "CCOLOR": ccolor})
    check(len(tcolor) == 8 and tcolor[6:] == ["#7fe0d0", "#c0c8d0"] and data_colors[:8] == tcolor, "C: the eight tree colours (+ Alchemy #7fe0d0, Smithing #c0c8d0)")
    check(len(ccolor) == 5 and data_colors[8:13] == ccolor, "C: the five class colours of the class tab (0.3 part 2)")
    page_colors, chat_colors = list(tcolor) + list(ccolor), data_colors[len(tcolor) + len(ccolor):]
    allowed_kit = SUI.allowed_colors()
    for c in chat_colors:
        used = re.findall(r'\.color\("%s"\)|TreeMsg\.say\([^\r\n]*, "%s"\);' % (re.escape(c), re.escape(c)), src)
        check(used and SUI.norm_color(c) not in allowed_kit and c not in page_colors,
              "C: chat colour %s is a Message colour of the script (%d uses), not a kit / page colour" % (c, len(used)))
    # ---- B + C (the 0.2.5 trees)
    counts = new_counts()
    kinds = {"success": SUI.COLOR["success"], "error": SUI.COLOR["error"], "warning": SUI.COLOR["warning"], "info": SUI.COLOR["info"]}
    for spec in STATES:
        nm = spec["name"]
        check(nm in new["states"] and nm in old["states"], "B: state %s built by both jars" % nm)
        if nm not in new["states"] or nm not in old["states"]:
            continue
        ids = compare_state(nm, old["states"][nm], new["states"][nm], SUI, counts, page_colors)
        if ids is not None and "SkyyTrMsg" in ids:
            want = dict((m, k) for m, k in RESULT_TEXTS).get(spec["msg"])
            got = _style(ids["SkyyTrMsg"]["props"])["color"]
            if want is not None:
                check(SUI.norm_color(got) == SUI.norm_color(kinds[want]), "C: %s: the result line colour %s is the %s colour" % (nm, got, want))
    report_counts(counts, "B-C. 0.2.5 trees (Mining at 0.2.5's 10 XP per Dust for the compare):")
    rcounts = new_counts()
    nmine = 0
    for spec in STATES:
        nm = spec["name"]
        if spec["tree"] not in (0, 9) or nm not in new.get("real", {}):
            continue
        real, norm = new["real"][nm], new["states"][nm]
        check_state("real " + nm, real, SUI, rcounts, page_colors)
        sr, sn = sets_of(real), sets_of(norm)
        xpm = (spec["xps"] or {}).get("Mining") if spec["xps"] is not None else None
        if xpm is not None and spec["levels"] is not None:
            dr = int(sr.get("SkyyTrDust", "Dust x")[5:].replace(",", ""))
            dn = int(sn.get("SkyyTrDust", "Dust x")[5:].replace(",", ""))
            check(dr - dn == xpm // 5 - xpm // 10, "C: %s: Mining Dust at 1 per 5 XP (%d, at 10 it was %d)" % (nm, dr, dn))
            if "1 per 10 XP" in sn.get("SkyyTrNote", ""):
                check(sr.get("SkyyTrNote") == sn["SkyyTrNote"].replace("1 per 10 XP", "1 per 5 XP"), "C: %s: the note says 1 per 5 XP" % nm)
            nmine += 1
        check(real["events"] == norm["events"], "C: %s: the Mining rate changes no binding" % nm)
    report_counts(rcounts, "C. Mining states at the real 0.3 rate:")
    print("   %d Mining states: Dust = XP / 5 - spent" % nmine)
    for m, k in RESULT_TEXTS + NEW_RESULT_TEXTS:
        check(new["colors"].get(m) == kinds[k], "C: infoColor(%r) = %s (want %s %s)" % (m, new["colors"].get(m), k, kinds[k]))
        if (m, k) in RESULT_TEXTS:
            check(old["colors"].get(m) == kinds[k], "C: 0.2.5 infoColor(%r) unchanged" % m)
    check(new["colors"].get("null") == kinds["info"], "C: infoColor(null) = the info colour")
    # ---- D clicks (the 0.2.5 trees)
    nsteps = 0
    for name, _spec, clicks in CLICKS:
        a, b = old["clicks"].get(name), new["clicks"].get(name)
        check(a is not None and b is not None, "D: click sequence %s ran in both jars" % name)
        if a is None or b is None:
            continue
        for sa, sb in zip(a["steps"], b["steps"]):
            nb = dict((k_, v_) for k_, v_ in sb.items() if k_ in sa)      # 0.3 part 2: the class keys of a step have no 0.2.5 counterpart
            nb.update(lv=sb["lv"][:72], off=sb["off"][:72], respec=sb["respec"][:6], credit=sb["credit"][:6])
            check(sb["cown"] == [] and sb["undo"] == 0 and sb["gearx"] is None and not any(sb["crespec"]), "D: %s: after %s the class tree is untouched" % (name, sb["click"]))
            check(sa == nb, "D: %s: after %s the page / data / coins / dirty state is identical (%s / %s)" % (
                name, sa["click"], dict((k, v) for k, v in sa.items() if sa.get(k) != nb.get(k)),
                dict((k, v) for k, v in nb.items() if sa.get(k) != nb.get(k))))
            check(not any(sb["lv"][72:]) and not any(sb["respec"][6:]), "D: %s: the new trees untouched" % name)
            nsteps += 1
        check(len(a["steps"]) == len(b["steps"]) == len(clicks), "D: %s: every click ran" % name)
        check(a["after"]["events"] == strip_new_tabs(b["after"]["events"]), "D: %s: the page after the clicks has the same bindings" % name)
        compare_state("after " + name, a["after"], b["after"], SUI, new_counts(), page_colors)
    coins = [s["coins"] for s in new["clicks"]["mining buy toggle respec"]["steps"]]
    check(coins[-1] == [500], "D: the priced respec took 500 coins once (%s)" % coins[-1])
    print("D. clicks: %d sequences, %d clicks with identical effects in both jars" % (len(CLICKS), nsteps))
    # ---- N: the new trees on the real page
    ncounts = new_counts()
    ncoming = 0
    for spec in NEW_STATES:
        nm = spec["name"]
        stt = new["states"].get(nm)
        check(stt is not None, "N: state %s built" % nm)
        if stt is None:
            continue
        ids = check_state(nm, stt, SUI, ncounts, page_colors)
        if ids is None:
            continue
        tn = TREES[spec["tree"]]
        sets = sets_of(stt)
        evs = [e[1] for e in stt["events"]]
        check(evs.count("#SkyyTrBuy") == 1 and len([e for e in evs if e.startswith("#SkyyTrTab")]) == 8
              and len([e for e in evs if re.match(r"#SkyyTrN\d+$", e)]) == 12, "N: %s: 8 tab + 12 node + buy bindings" % nm)
        if not nm.startswith(("alchemy level 0", "smithing no skills", "new result")):
            for s in range(1, 13):
                nid = NEW_TREE[tn][s - 1][0]
                lvl = spec["nodes"].get("%s.%s" % (tn, nid), 0)
                want_c = coming_of(tn, s, spec["reads"]) and lvl == 0
                sb = sets.get("SkyyTrN%dSb" % s, "")
                if want_c:
                    ncoming += 1
                    check(sb == "Coming with " + NEW_TREE[tn][s - 1][5][0], "N: %s: S%d card = %r" % (nm, s, sb))
                else:
                    check(not sb.startswith("Coming"), "N: %s: S%d is not coming (%r)" % (nm, s, sb))
            sel = spec["sel"]
            nid, _nm, _k, _mx, _per, readers = NEW_TREE[tn][sel - 1]
            lvl = spec["nodes"].get("%s.%s" % (tn, nid), 0)
            coming = coming_of(tn, sel, spec["reads"])
            buys = [txt for t, s_, d_, txt in stt["commands"] if t == "AppendInline" and txt and "#SkyyTrBuy {" in txt]
            if coming and lvl == 0:
                check(sets.get("SkyyTrDetState") == "Coming with " + " or ".join(readers) and sets.get("SkyyTrBuyTx") == "Coming with " + " or ".join(readers)
                      and len(buys) == 1 and 'Text: "Coming soon"' in buys[0], "N: %s: the detail panel + Coming soon button of a coming node" % nm)
                check(sets.get("SkyyTrDetNeed", "").startswith("Waits for the " + " or ".join(readers) + " build that applies it"), "N: %s: the need line" % nm)
            elif coming:
                check(sets.get("SkyyTrBuyTx") in ("Coming with " + " or ".join(readers), "MAX") and len(buys) == 1 and 'Text: "Coming soon"' not in buys[0],
                      "N: %s: an OWNED coming node keeps its Level up / Maxed button, the buy line says why" % nm)
            else:
                check(not (sets.get("SkyyTrBuyTx") or "").startswith("Coming") and len(buys) == 1 and 'Text: "Coming soon"' not in buys[0],
                      "N: %s: a live node has no coming text" % nm)
            if nm == "no readers Alchemy S4":   # fix round A: Deep Reserves at level 3 is flat Mana, no percent
                check(sets.get("SkyyTrDetNow") == "Now: +3 max Mana" and sets.get("SkyyTrDetNext") == "Level 4: +4 max Mana",
                      "N: Deep Reserves reads flat Mana: %r / %r" % (sets.get("SkyyTrDetNow"), sets.get("SkyyTrDetNext")))
            if nm == "no readers Smithing S6":
                check(sets.get("SkyyTrDetNow") == "Now: +2 max Health" and sets.get("SkyyTrDetNext") == "Level 3: +3 max Health",
                      "N: Forge Hardened reads flat Health: %r / %r" % (sets.get("SkyyTrDetNow"), sets.get("SkyyTrDetNext")))
            waiting = []
            for s in range(1, 13):
                if coming_of(tn, s, spec["reads"]):
                    for m in NEW_TREE[tn][s - 1][5]:
                        if m not in waiting:
                            waiting.append(m)
            note = sets.get("SkyyTrNote", "")
            if waiting:
                ww = waiting[0] if len(waiting) == 1 else ", ".join(waiting[:-1]) + " and " + waiting[-1]
                check(note.startswith("Coming nodes wait for %s (a later build) - Tokens unlock, Dust (1 per " % ww), "N: %s: the info row %r" % (nm, note))
            else:
                check(not note.startswith("Coming"), "N: %s: no coming note when every node is live" % nm)
        ids_level = sets.get("SkyyTrLvl", "")
        check(ids_level.startswith(tn) or ids_level == "SkyySkills missing", "N: %s: the level label %r" % (nm, ids_level))
    report_counts(ncounts, "N. new trees:")
    print("   %d coming card lines checked" % ncoming)
    nn = 0
    for name, _spec, clicks, want in NEW_CLICKS:
        got = new["nclicks"].get(name)
        check(got is not None and len(got["steps"]) == len(clicks), "N: click sequence %s ran" % name)
        if got is None:
            continue
        for k, msg, lvs in want:
            step = got["steps"][k]
            check(step["err"] is None and step["msg"] == msg, "N: %s step %d (%s): %r (want %r)" % (name, k, step["click"], step["msg"], msg))
            for key, lv_ in lvs.items():
                check(step["lv"][node_index(*key.split("."))] == lv_, "N: %s step %d: %s = %d (want %d)" % (name, k, key, step["lv"][node_index(*key.split("."))], lv_))
            nn += 1
        check(not any(x for x in got["steps"][-1]["lv"][:72]), "N: %s: the 0.2.5 trees untouched" % name)
        check_state("after " + name, got["after"], SUI, new_counts(), page_colors)
    check(new["nclicks"]["alchemy without readers"]["steps"][11]["respec"][6], "N: the Alchemy respec time is saved")
    print("N. clicks: %d sequences, %d expected results (coming refusals, pass-through unlocks, level ups, toggle, respec, a reader "
          "going away and back, partial flags)" % (len(NEW_CLICKS), nn))
    # ---- K: the class tree (0.3 part 2)
    ct = new.get("ctables") or {}
    check(bool(ct), "K: the states child exported the class tables")
    kinds = {None: 0, "H": 1, "S": 2, "M": 3, "R": 4, "X": 5}
    if ct:
        check(ct["NID"] == CT_ID and ct["NN"] == 37 and ct["NC"] == 5 and ct["NSLOT"] == 54, "K1: 37 node ids in the spec's order")
        check(ct["CLASSES"] == CLASSES and ct["CSKILL"] == CSKILL and ct["CMAGIC"] == [c in CMAGIC for c in CLASSES], "K1: classes, class skills, magic classes")
        check(ct["NAP"] == [n[1] for n in CT] and ct["NPAGE"] == [n[7] for n in CT] and ct["NROW"] == [n[8] for n in CT] and ct["NCOL"] == [n[9] for n in CT], "K1: AP, page, row, col of every node")
        check(ct["NLANE"] == [n[5] for n in CT] and ct["NLANEN"] == [n[6] for n in CT] and ct["NROLE"] == [n[10] for n in CT], "K1: lane, lane count, role of every node")
        check(ct["NPAR1"] == [CT_IDX[n[2][0]] if n[2] else -1 for n in CT] and ct["NPAR2"] == [CT_IDX[n[2][1]] if len(n[2]) > 1 else -1 for n in CT], "K1: parents")
        check(ct["NNEED"] == [CT_IDX[n[3]] if n[3] else -1 for n in CT] and ct["NLOCK"] == [CT_IDX[n[4]] if n[4] else -1 for n in CT], "K1: needs and locks")
        check([(CT_ID[a], CT_ID[b]) for a, b in zip(ct["LA"], ct["LB"])] == CT_LINKS, "K1: the 36 drawn links")
        check(ct["LANE"] == [LANES[cn][l][0] for cn in CLASSES for l in range(3)], "K1: the lane names")
        for ci, cn in enumerate(CLASSES):
            for n, nid in enumerate(CT_ID):
                k, amt, nm = ct_kind(cn, nid)
                j = ci * 37 + n
                ok = ct["CK"][j] == kinds[k] and ct["CAMT"][j] == amt and ct["CMIN"][j] == (XBOW_MIN.get(nid, 0) if cn == "Archer" else 0)
                if nm is not None:
                    ok = ok and ct["CNM"][j] == nm
                check(ok, "K1: %s %s = kind %s amount %s name %s (jar: %s %s %s min %s)" % (cn, nid, k, amt, nm, ct["CK"][j], ct["CAMT"][j], ct["CNM"][j], ct["CMIN"][j]))
        spine_names = dict((ci, [ct["CNM"][ci * 37 + CT_IDX[i]] for i in ("ROOT", "P1", "P2", "X1", "X2", "P3", "P4")]) for ci in range(5))
        check(spine_names[0] == ["Root", "Might I", "Vitality I", "Edge", "Bulwark", "Focus I", "Might II"]
              and spine_names[2] == ["Root", "Reservoir I", "Focus I", "Wellspring", "Bulwark", "Vitality I", "Focus II"], "K1: the spine names: %s / %s" % (spine_names[0], spine_names[2]))

        def tot(cn, k, pick="X1"):
            ci = CLASSES.index(cn)
            return sum(ct["CAMT"][ci * 37 + n] for n in range(37) if ct["CK"][ci * 37 + n] == kinds[k] and CT_ID[n] != ("X2" if pick == "X1" else "X1"))
        check((tot("Warrior", "S"), tot("Warrior", "H"), tot("Warrior", "R")) == (25, 56, 5) == (tot("Berserker", "S"), tot("Berserker", "H"), tot("Berserker", "R"))
              and (tot("Archer", "S"), tot("Archer", "H"), tot("Archer", "R"), tot("Archer", "X")) == (23, 36, 5, 34)
              and (tot("Mage", "M"), tot("Mage", "R"), tot("Mage", "H")) == (48, 45, 36) == (tot("Priest", "M"), tot("Priest", "R"), tot("Priest", "H")),
              "K1: the live totals of spec 7 + answer 5")
        for pg in range(2):
            for n, nd in enumerate(CT):
                if nd[7] == pg:
                    check(ct["SK"][pg * 54 + nd[8] * 9 + nd[9]] == 1 and ct["SN"][pg * 54 + nd[8] * 9 + nd[9]] == n, "K1: the slot of %s" % nd[0])
        check(ct["SK"].count(1) == 37 and ct["SK"].count(4) == 5 and ct["SK"].count(2) == 8 and ct["SK"].count(3) == 1 and ct["SK"].count(0) == 108 - 51, "K1: slot kinds")
        check(sum(1 for x in ct["PL1"] if x >= 0) == 75 and sum(1 for x in ct["PL2"] if x >= 0) == 3 and all(any(l == li for l in ct["PL1"]) for li in range(36)),
              "K1: 75 bar pieces, 3 shared, every link drawn")
        check(sum(1 for x in ct["SR"] if x) == 29 and sum(1 for x in ct["SD"] if x) == 21, "K1: 29 right-gap and 21 bottom-gap stubs: %d / %d" % (sum(1 for x in ct["SR"] if x), sum(1 for x in ct["SD"] if x)))
    for m, k in CLASS_RESULT_TEXTS:
        check(new["colors"].get(m) == {"success": SUI.COLOR["success"], "error": SUI.COLOR["error"], "warning": SUI.COLOR["warning"], "info": SUI.COLOR["info"]}[k],
              "K: infoColor(%r) = %s (want %s)" % (m, new["colors"].get(m), k))

    def class_expect(spec):
        """what the model says the class page shows"""
        probe = spec["probe"]
        eff = spec["pcls"] or spec["cls"]
        ci = CLASSES.index(eff) if eff in CLASSES else -1
        if probe:
            ci = ci if ci >= 0 else 0
            own, lvl = set(SPINE_OWN), 30
        else:
            own = set(spec["own"]) if ci >= 0 else set()
            lvl = spec["lvl"] if spec["levels"] is not None else -1
        cfg = spec["cfg"]
        it = m_intact(own, spec["con_off"]) if ci >= 0 and not spec["bad"] else set()
        ap_all = m_ap(max(lvl, 0), cfg.get("AP_FIRST", 1), cfg.get("AP_EVERY", 2), cfg.get("AP_MAX", 50), cfg.get("C_EXTRA_AP", 0)) if ci >= 0 else 0
        ap_free = ap_all - m_spent(it)
        kw = dict(reads=spec["reads"], regen=spec["regen"], con_off=spec["con_off"], cmin=spec["cmin"])
        cn = CLASSES[ci] if ci >= 0 else None
        states = dict((nid, m_state(own, it, cn, nid, lvl, ap_free, **kw)) for nid in CT_ID) if ci >= 0 else {}
        cards = dict((nid, m_card(own, it, cn, nid, lvl, ap_free, **kw)) for nid in CT_ID) if ci >= 0 else {}
        return dict(ci=ci, cn=cn, lvl=lvl, own=own, it=it, ap_all=ap_all, ap_free=ap_free, states=states, cards=cards, probe=probe, kw=kw)

    def mk_of(stt, ident):
        return [txt for t, s_, d_, txt in stt["commands"] if t == "AppendInline" and txt and ("#%s {" % ident) in txt]
    DISABLED = 'Default: (Background: (TexturePath: "Common/Buttons/Disabled.png"'
    kc = new_counts()
    kcells, kgold = 0, 0
    for spec in CLASS_STATES:
        nm = spec["name"]
        stt = new["cstates"].get(nm)
        check(stt is not None, "K: state %s built" % nm)
        if stt is None:
            continue
        ex = class_expect(spec)
        ctab = bool(spec["cfg"].get("CLASS_ON", True)) or spec["probe"]
        cpage_ = ctab and spec["tree"] == NT_CLASS
        ids = check_state(nm, stt, SUI, kc, page_colors, class_tab=ctab, class_page=cpage_)
        if ids is None:
            continue
        evs = [e[1] for e in stt["events"]]
        sets = sets_of(stt)
        check(("#SkyyTrTab8" in evs) == ctab and len([e for e in evs if e.startswith("#SkyyTrTab")]) == (9 if ctab else 8), "K: %s: the class tab binding %s" % (nm, "present" if ctab else "absent"))
        tab8 = mk_of(stt, "SkyyTrTab8")
        if ctab:
            check(len(tab8) == 1 and ('Text: "%s"' % (CLASSES[ex["ci"]] if ex["ci"] >= 0 else "Class")) in tab8[0]
                  and (('Common/Buttons/Primary.png' in tab8[0]) == cpage_), "K: %s: the class tab button says %s (%s)" % (nm, CLASSES[ex["ci"]] if ex["ci"] >= 0 else "Class", "primary" if cpage_ else "secondary"))
        else:
            check(not tab8, "K: %s: no class tab button" % nm)
        if not cpage_:
            check(sets.get("SkyyTrLvl", "").startswith(("Mining", "SkyySkills")), "K: %s: a template page (falls back to Mining): %r" % (nm, sets.get("SkyyTrLvl")))
            check("#SkyyTrUndo" not in evs and not any(re.match(r"#SkyyTrC\d+$", e) for e in evs), "K: %s: no class bindings on a template page" % nm)
            continue
        ci, cn = ex["ci"], ex["cn"]
        eff_cls = spec["pcls"] or spec["cls"]
        unk = (ci < 0 and not ex["probe"] and bool(eff_cls))                      # fix round: a class this build has no tree for (Assassin)
        want_lvl = "SkyySkills missing" if (ex["lvl"] < 0 and not ex["probe"]) else (("%s - no tree yet" % eff_cls if unk else "No class yet") if ci < 0 else "%s %d" % (CSKILL[ci], ex["lvl"]))
        check(sets.get("SkyyTrLvl") == want_lvl, "K: %s: level label %r (want %r)" % (nm, sets.get("SkyyTrLvl"), want_lvl))
        check(sets.get("SkyyTrTok") == "Ability Points %d of %d" % (ex["ap_free"], ex["ap_all"]), "K: %s: AP label %r (want %d of %d)" % (nm, sets.get("SkyyTrTok"), ex["ap_free"], ex["ap_all"]))
        price = 0 if (ci < 0 or ex["lvl"] < 0 or ex["probe"]) else ex["lvl"] * spec["cfg"].get("C_RESPEC_PER", 100)
        want_dust = "Respec free (probe)" if ex["probe"] else ("Respec {:,} coins".format(price) if price > 0 else "Respec free")
        check(sets.get("SkyyTrDust") == want_dust, "K: %s: respec price label %r (want %r)" % (nm, sets.get("SkyyTrDust"), want_dust))
        for e in ("#SkyyTrBuy", "#SkyyTrUndo", "#SkyyTrRespec", "#SkyyTrBack"):
            check(evs.count(e) == 1, "K: %s: binding %s once" % (nm, e))
        resp = mk_of(stt, "SkyyTrRespec")
        want_resp = ("Respec" if ci < 0 else (("Click again to respec " if spec["armed"] else "Respec ") + CLASSES[ci]))
        check(len(resp) == 1 and ('Text: "%s"' % want_resp) in resp[0] and ((DISABLED in resp[0]) == (ci < 0)), "K: %s: the Respec button says %r" % (nm, want_resp))
        grid = ids.get("SkyyTrGrid")
        kids = [k["id"] for k in grid["kids"]] if grid else []
        if ci < 0:
            want_nc = ("Your class %s has no skill tree yet - it comes in a later build" % eff_cls) if unk else "Choose a class with /class"
            check(kids == ["SkyyTrNoClass"] and sets.get("SkyyTrNoClass", "").startswith(want_nc), "K: %s: the no-class label %r" % (nm, sets.get("SkyyTrNoClass")))
            check(not any(re.match(r"#SkyyTrC\d+$", e) for e in evs) and "#SkyyTrPgN" not in evs, "K: %s: no cell / pager bindings without a class" % nm)
            want_nn = ("Your class %s has no tree yet - it comes in a later build" % eff_cls) if unk else "Choose a class with /class"
            check(sets.get("SkyyTrNote", "").startswith(want_nn), "K: %s: the note %r" % (nm, sets.get("SkyyTrNote")))
            check(sets.get("SkyyTrDetName") == "ROOT", "K: %s: the detail title is the bare id without a class: %r" % (nm, sets.get("SkyyTrDetName")))
            continue
        check(kids == ["SkyyTrRs"] + ["SkyyTrCR%d" % r for r in range(6)], "K: %s: rune strip + six slot rows: %s" % (nm, kids))
        cp, sel = stt["cpage"], stt["csel"]
        check(cp == (spec["cpage"] if spec["cpage"] in (0, 1) else 0), "K: %s: page %d" % (nm, cp))
        if not (0 <= sel < 37) or CT[sel][7] != cp:
            sel = 0 if cp == 0 else CT_IDX["P4"]                                       # the page shows its first node then (TreeClass.firstOf)
        check(sets.get("SkyyTrPgL") == "Page %d of 2" % (cp + 1) and sets.get("SkyyTrRsL") == "Rune slots - coming with 0.7", "K: %s: pager caption / strip label" % nm)
        pgp, pgn = mk_of(stt, "SkyyTrPgP"), mk_of(stt, "SkyyTrPgN")
        check(len(pgp) == 1 and ((DISABLED in pgp[0]) == (cp == 0)) and len(pgn) == 1 and ((DISABLED in pgn[0]) == (cp == 1)) and "#SkyyTrPgP" in evs and "#SkyyTrPgN" in evs,
              "K: %s: the pager's Prev / Next looks for page %d" % (nm, cp))
        check(all(("SkyyTrRs%d" % i) in ids for i in range(1, 7)) and all(("SkyyTrRs%dOut" % i) in ids for i in range(1, 7)), "K: %s: six disabled rune cells" % nm)
        page_nodes = [n for n in CT if n[7] == cp]
        cell_evs = sorted(e for e in evs if re.match(r"#SkyyTrC\d+$", e))
        check(cell_evs == sorted("#SkyyTrC%d" % (CT_IDX[n[0]] + 1) for n in page_nodes), "K: %s: the cell bindings are the page's %d nodes" % (nm, len(page_nodes)))
        for n in page_nodes:
            nid = n[0]
            i = CT_IDX[nid] + 1
            sb = sets.get("SkyyTrC%dSb" % i)
            check(sb == ex["cards"][nid], "K: %s: %s card %r (want %r)" % (nm, nid, sb, ex["cards"][nid]))
            cellmk = mk_of(stt, "SkyyTrC%d" % i)
            check(len(cellmk) == 1, "K: %s: one cell markup for %s" % (nm, nid))
            if cellmk:
                is_sel = "Default: (Background: #4274a5)" in cellmk[0]
                has_cover = ("#SkyyTrC%dOut" % i) in cellmk[0]
                check(is_sel == (CT_IDX[nid] == sel), "K: %s: %s selected look %s" % (nm, nid, is_sel))
                # fix round J: the sold-out cover only on the rune / element slots - a reader-gated node keeps the normal grey cell
                check(has_cover == (ex["states"][nid] == 3 and CT_IDX[nid] != sel and CT[CT_IDX[nid]][10] in (2, 3, 4, 7, 8)),
                      "K: %s: %s coming cover %s (state %d, role %d)" % (nm, nid, has_cover, ex["states"][nid], CT[CT_IDX[nid]][10]))
                node = ids.get("SkyyTrC%d" % i)
                a_ = _pairs(node["props"].get("Anchor")) if node else {}
                check((a_.get("Width"), a_.get("Height")) == (100, 84) and ("SkyyTrC%dIc" % i) in ids, "K: %s: %s cell 100 x 84 with its icon" % (nm, nid))
                kcells += 1
        for r in range(6):
            row = ids.get("SkyyTrCR%d" % r)
            sk = row["kids"] if row else []
            check(len(sk) == 9 and all(_pairs(k["props"].get("Anchor")).get("Width") == 104 and _pairs(k["props"].get("Anchor")).get("Height") == 88 for k in sk),
                  "K: %s: row %d holds 9 slots of 104 x 88" % (nm, r))
        gold = sum(1 for t, s_, d_, txt in stt["commands"] if t == "AppendInline" and txt and (s_ or "").startswith("#SkyyTrC") and "Background: #E8A93B" in txt)
        grey = sum(1 for t, s_, d_, txt in stt["commands"] if t == "AppendInline" and txt and (s_ or "").startswith("#SkyyTrC") and "Background: #797b7c" in txt)
        base = cp * 54 * 8
        it_idx = set(CT_IDX[i] for i in ex["it"])

        def lg(l):
            return l >= 0 and ct["LA"][l] in it_idx and ct["LB"][l] in it_idx
        want_gold = sum(1 for q in range(54 * 8) if lg(ct["PL1"][base + q]) or lg(ct["PL2"][base + q]))
        want_all = sum(1 for q in range(54 * 8) if ct["PL1"][base + q] >= 0)
        check(gold == want_gold and gold + grey == want_all, "K: %s: %d gold + %d grey bar pieces (want %d gold of %d)" % (nm, gold, grey, want_gold, want_all))
        kgold += gold
        if ex["own"] == set(SPINE_OWN) and not spec["con_off"] and not spec["bad"]:
            check(gold == (14 if cp == 0 else 10), "K: %s: the spine's gold pieces by hand: %d (want %d)" % (nm, gold, 14 if cp == 0 else 10))
        if 0 <= sel < 37:
            nid = CT_ID[sel]
            st0 = ex["states"][nid]
            who = m_coming(cn, nid, spec["reads"], spec["regen"])
            want_state = {2: "Owned", 1: "Unlockable", 0: "Locked", 3: "Coming with " + who,
                          4: "Owned - chain broken (see Needs)"}[st0]
            check(sets.get("SkyyTrDetState") == want_state, "K: %s: detail state %r (want %r)" % (nm, sets.get("SkyyTrDetState"), want_state))
            check(sets.get("SkyyTrDetName") == "%s  (%s)" % (ct["CNM"][ci * 37 + sel], nid), "K: %s: detail name %r" % (nm, sets.get("SkyyTrDetName")))
            buys = mk_of(stt, "SkyyTrBuy")
            want_btn = "Coming soon" if st0 == 3 else ("Owned" if st0 in (2, 4) else "Unlock")
            check(len(buys) == 1 and ('Text: "%s"' % want_btn) in buys[0] and ((DISABLED in buys[0]) == (st0 != 1)), "K: %s: the buy button is %s (%s)" % (nm, want_btn, "live" if st0 == 1 else "disabled"))
            undos = mk_of(stt, "SkyyTrUndo")
            can_undo = bool(spec["undo"]) and (spec["probe"] or spec["cfg"].get("C_UNDO", True))
            check(len(undos) == 1 and ((DISABLED in undos[0]) != can_undo), "K: %s: the Undo button is %s" % (nm, "live" if can_undo else "disabled"))
            cost = ct["NAP"][sel]
            want_buytx = {3: "Coming with " + who, 2: "Owned", 4: "Owned - chain broken", 1: "Unlock - %d AP" % cost}.get(st0)
            if want_buytx is None:
                why = m_reason(ex["own"], ex["it"], cn, nid, ex["lvl"], ex["ap_free"], **ex["kw"])
                want_buytx = ("Need %d more AP" % (cost - ex["ap_free"])) if why == 9 else ex["cards"][nid]
            check(sets.get("SkyyTrBuyTx") == want_buytx, "K: %s: buy line %r (want %r)" % (nm, sets.get("SkyyTrBuyTx"), want_buytx))
            check(sets.get("SkyyTrDetCost") == ("Cost: -" if st0 == 3 else "Cost: %d AP" % cost), "K: %s: cost line %r" % (nm, sets.get("SkyyTrDetCost")))
            check((sets.get("SkyyTrDetNeed", "") == "") == (st0 in (1, 2)), "K: %s: the Needs line is empty exactly for unlockable / owned: %r" % (nm, sets.get("SkyyTrDetNeed")))
            # fix round B / F / G: the Now / Gives texts carry the LIVE amount (class.nodes Amount), P3 / P4 say where the map continues,
            # an element's Gives line is short enough for the 2-line label (check_texts measures it)
            k_, amt_, _nm_ = ct_kind(cn, nid)
            amt_ = spec["camt"].get(nid, amt_)
            now_ = {"H": "+%d max Health", "S": "+%d Strength", "M": "+%d max Mana", "R": "+%d%% Mana Regen",
                    "X": {"R2": "+%d bolts in a crossbow magazine", "R3": "+%d more bolts - the +4 cap", "R4": "A hotbar crossbow reloads by itself in %d s"}.get(nid, "%d")}.get(k_)
            now_ = now_ % amt_ if now_ else None
            want_now = {2: "Now: " + (now_ or ""), 4: "Now: nothing - the chain is broken"}.get(st0, "Now: not unlocked")
            if st0 != 2 or now_:
                check(sets.get("SkyyTrDetNow") == want_now, "K: %s: %s Now line %r (want %r)" % (nm, nid, sets.get("SkyyTrDetNow"), want_now))
            nxt = sets.get("SkyyTrDetNext", "")
            if now_:
                check(nxt.startswith("Gives: " + now_ + " - "), "K: %s: %s Gives line %r (want the live amount %r)" % (nm, nid, nxt, now_))
            if nid in ("P3", "P4"):
                check(nxt.endswith(" - continues on page %d" % (2 if nid == "P3" else 1)), "K: %s: %s says where the map continues: %r" % (nm, nid, nxt))
            else:
                check("continues on page" not in nxt, "K: %s: %s has no continues text" % (nm, nid))
            if CT[CT_IDX[nid]][10] == 7:
                check(" - later (needs SkyyGear) - Element - " in nxt and len(nxt) < 100, "K: %s: the element's short Gives line: %r" % (nm, nxt))
        note = sets.get("SkyyTrNote", "")
        lanes = " - ".join("%s %d" % (LANES[cn][l][0], sum(1 for i in ex["it"] if CT[CT_IDX[i]][5] == l + 1)) for l in range(3))
        if spec["bad"]:
            want_note = "Your tree file could not be read"
        elif ex["lvl"] < 0 and not ex["probe"]:
            want_note = "Skill trees need SkyySkills"
        elif ex["ap_free"] < 0:
            want_note = "The AP rules changed - your balance is negative"
        elif ex["probe"]:
            want_note = "PROBE - nothing is saved: " + lanes
        else:
            cfg_ = spec["cfg"]
            want_note = lanes + " - Ability Points come from your %s level (%d + 1 per %d levels, max %d)" % (
                CSKILL[ci], cfg_.get("AP_FIRST", 1), cfg_.get("AP_EVERY", 2), cfg_.get("AP_MAX", 50))
        check(note.startswith(want_note), "K: %s: the note %r (want %r...)" % (nm, note, want_note))
    report_counts(kc, "K. class tab states:")
    print("   %d node cells checked against the model, %d gold bar pieces" % (kcells, kgold))
    nk = 0
    for name, spec, clicks, want in CLASS_CLICKS:
        got = new["cclicks"].get(name)
        check(got is not None and len(got["steps"]) == len(clicks), "K: click sequence %s ran" % name)
        if got is None:
            continue
        probe = spec["probe"]
        for entry in want:
            k, msg, owned = entry[0], entry[1], entry[2]
            extra = entry[3] if len(entry) > 3 else {}
            step = got["steps"][k]
            check(step["err"] is None, "K: %s step %d (%s) threw: %s" % (name, k, step["click"], step["err"]))
            if msg:
                check(step["msg"] == msg, "K: %s step %d (%s): %r (want %r)" % (name, k, step["click"], step["msg"], msg))
            for nid, v in owned.items():
                have = step["pcown"] if probe else step["cown"]
                check((nid in have) == v, "K: %s step %d: %s owned = %s (want %s)" % (name, k, nid, nid in have, v))
            for key, v in extra.items():
                check(step.get(key) == v, "K: %s step %d: %s = %r (want %r)" % (name, k, key, step.get(key), v))
            nk += 1
        last = got["steps"][-1]
        check(not any(last["lv"]) and not any(last["off"]) and not any(last["respec"]), "K: %s: the template trees untouched (no Mining buy / respec)" % name)
        ctab = (bool(spec["cfg"].get("CLASS_ON", True)) and "!cfg:CLASS_ON=false" not in clicks) or probe   # fix round: k15 / k16 flip it off mid-page
        check_state("after " + name, got["after"], SUI, new_counts(), page_colors, class_tab=ctab, class_page=(ctab and got["after"]["tree"] == NT_CLASS))
        st = got["steps"]
        if name == "class buy chain":
            check(st[5]["gearx"] is None and st[6]["gearx"] == "str:2" and st[10]["gearx"] == "str:5" and st[16]["gearx"] == "str:7" and st[18]["gearx"] == "str:9"
                  and st[22]["gearx"] == "str:5" and st[27]["gearx"] is None, "K: k1: gear:extras trees = str:N follows the Strength owned (P1 2, X1 3, P4 2, L1 2; the undos and the respec take it back): %s" % [x["gearx"] for x in st])
            check(["add", "trees", 5.0] in st[14]["regen"] and st[27]["regen"][-1] == ["add", "trees", 0.0], "K: k1: Mana Regen posted at Focus I and removed at the respec: %s" % st[27]["regen"][-3:])
            check(st[18]["undo"] == 7 and st[22]["undo"] == 5 and st[27]["undo"] == 0 and st[27]["coins"] == [2300] and st[26]["coins"] == [], "K: k1: Undo list 7 -> 5 -> 0, 2,300 coins taken once at the respec: %s %s" % (st[27]["undo"], st[27]["coins"]))
            check(st[27]["crespec"][0] and not any(st[27]["crespec"][1:]) and "7ee5" in "".join(st[27]["dirty"]) and st[0]["tree"] == 8, "K: k1: the Archer respec time is set, the file is dirty, the class tab opened")
        if name == "class respec refusals":
            check(st[2]["coins"] == [2300] and st[5]["coins"] == [2300] and st[8]["coins"] == [2300, 2300] and st[2]["cown"] == SPINE_OWN and st[5]["cown"] == SPINE_OWN,
                  "K: k2: a refused take changes nothing; the paid respec takes 2,300 once more: %s" % st[8]["coins"])
        if name == "class off clicks":
            check(all(x["cown"] == ["ROOT"] for x in st) and "#SkyyTrTab8" not in [e[1] for e in got["after"]["events"]] and all(x["err"] is None for x in st)
                  and sets_of(got["after"]).get("SkyyTrLvl", "").startswith("Mining"), "K: k10: class trees off - nothing changes, no class tab, the page falls back to Mining")
            check(st[0]["tree"] == 0 and st[0]["msg"] == "Class trees were switched off - this is the Mining tree now" and st[0]["coins"] == [],
                  "K: k10 (fix K): the first click on a stale class page shows Mining and buys nothing: %r" % st[0]["msg"])
        if name in ("class off mid page", "class off mid respec"):
            check(all(x["coins"] == [] for x in st) and st[-1]["tree"] == 0 and st[-1]["cown"] == SPINE_OWN and sets_of(got["after"]).get("SkyyTrLvl", "").startswith("Mining")
                  and "#SkyyTrTab8" not in [e[1] for e in got["after"]["events"]], "K: %s (fix K): no coins, the class picks stay, the page shows Mining without a class tab" % name)
        if name == "class respec price change":
            check(st[2]["coins"] == [] and st[3]["coins"] == [4000] and st[2]["armT"] == 8 and st[3]["armT"] == -1,
                  "K: k17 (fix N): the changed price re-arms without a charge, the third click charges the new price once: %s / %s" % (st[2]["coins"], st[3]["coins"]))
        if name == "class respec ledger errors":
            check(st[2]["coins"] == [2300] and st[5]["coins"] == [2300, 2300] and all(x["cown"] == SPINE_OWN for x in st) and all(x["dirty"] == [] for x in st),
                  "K: k18 (fix P): a null / throwing take is reported, the tree and the file stay as they were: %s" % st[5]["coins"])
        if name == "class broken respec free":
            check(st[1]["coins"] == [] and st[1]["cown"] == [], "K: k20 (fix N): nothing intact = nothing to pay: %s" % st[1]["coins"])
        if name == "class level zero cooldown":
            check(st[1]["coins"] == [] and st[1]["cown"] == ["ROOT"], "K: k21 (fix C): a level-0 read does not waive the cooldown")
        if name == "class probe clicks":
            check(all(x["cown"] == [] for x in st) and all(x["coins"] == [] for x in st) and all(x["dirty"] == [] for x in st), "K: k11: the probe saves nothing, takes no coins, leaves the real data alone")
            check("L3" in st[1]["pcown"] and "L4" in st[3]["pcown"] and "L4" not in st[4]["pcown"] and st[6]["pcown"] == [] and st[8]["pcown"] == ["ROOT"], "K: k11: the probe copy follows the clicks: %s" % [x["pcown"] for x in st])
        if name == "class mana regen post":
            check(["add", "trees", 5.0] in st[3]["regen"] and st[4]["regen"][-1] == ["add", "trees", 0.0] and all(x["gearx"] is None for x in st), "K: k14: a Mage's Focus I posts +5 Mana Regen, the Undo removes it, no Strength: %s" % st[4]["regen"][-2:])
        if name == "class pages and cells":
            check(all(x["err"] is None for x in st), "K: k9: every page / cell click ran")
    print("K. clicks: %d sequences, %d expected results (buy chain, pick-one, lane / level gates, AP shortage, coming slots, Undo, respec with coins "
          "/ refusals / cooldown / free on a negative balance, pages, class trees off, the probe copy, no class, no SkyySkills, Mana Regen posts)" % (len(CLASS_CLICKS), nk))
    # ---- L M P S (the logic child)
    if os.path.isfile(lo):
        lr = json.load(open(lo))
        OKS[0] += lr["oks"]
        for f in lr["fails"]:
            check(False, f)
        for k, v in sorted(lr["info"].items()):
            print("   info", k, v)
        print("L-M-P-S. logic child: %d checks, %d failed" % (lr["oks"] + len(lr["fails"]), len(lr["fails"])))
    # ---- E class bytes + jar entries
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    on, nn_ = set(zo.namelist()), set(zn.namelist())
    check(sorted(nn_ - on) == ["com/skyy/trees/TreeClass.class", "com/skyy/trees/TreeClassOps.class", "com/skyy/trees/TreeMig.class", "com/skyy/trees/TreeProbeCmd.class"]
          and not (on - nn_), "E: the same jar entries + TreeMig, TreeClass, TreeClassOps, TreeProbeCmd: %s / %s" % (sorted(nn_ - on), sorted(on - nn_)))
    diff = set(n for n in on & nn_ if zo.read(n) != zn.read(n))
    assets = [n for n in zn.namelist() if n.endswith(".json") and n != "manifest.json"]
    check(len(assets) == ASSET_JSON and not [n for n in assets if n in diff], "E: every asset file byte-identical (%d JSON)" % len(assets))
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "E: no .ui files in the jar (inline pages only)")
    bc = json.load(open(bco))
    same_or_version = ["TreeAbil", "TreeGather", "TreeSwing", "TreeDmgSys", "TreeSaver", "TreeMsg", "SaveTask", "TreeFelledFn",
                       "TreeQuietCmd", "TreeReloadCmd", "TreeSwingCmd"]   # 0.3 part 2: TreeFn / TreeBonusFn answer class keys now
    for c in same_or_version:
        n = "com/skyy/trees/%s.class" % c
        check(n not in diff or (bc.get(n, {}).get("version_only") and not bc[n]["new"] and not bc[n]["gone"]), "E: %s byte-identical (or version only): %s" % (c, bc.get(n)))
    # the 0.2.5 code that 0.3 did not edit, but that compiles TreeDefs' constants in: only those constants differ
    const_want = {"TreeCalc": ["eff"], "TreeDefs": ["idx", "soon", "tree"], "TreeFx": ["compute"], "TreeCfg": ["load"], "TreeKit": ["checkNode"]}
    # 0.3 part 2 edits readFile / snap / TreeData / postTree / handleDataEvent / apply / shutdown on purpose (the class tree)
    for c, ms in sorted(const_want.items()):
        got = bc.get("com/skyy/trees/%s.class" % c, {})
        for m in ms:
            keys = [k for k in got.get("changed", []) if k.startswith(m + "(")]
            check(len(keys) == 1 and keys[0] in got.get("const_only", []), "E: %s.%s differs from 0.2.5 only by the inlined N / NT / tree-name constants" % (c, m))
    got = bc.get("com/skyy/trees/TreeStore.class", {})
    check(sorted(got.get("new", [])) == ["clearClass(Lcom/skyy/trees/TreeData;IJ)V", "namesPut()V", "namesRemove()V", "setClassOwn(Lcom/skyy/trees/TreeData;IIZ)V"]
          and not got.get("gone") and set(got.get("changed", [])) >= set(["readFile(Ljava/lang/String;)Lcom/skyy/trees/TreeData;", "snap(Ljava/lang/String;)Ljava/util/Properties;"])
          and got.get("fields_new") == ["NAMES_PUT Ljava/lang/String;"], "E: TreeStore: + setClassOwn / clearClass / namesPut / namesRemove, readFile + snap edited, + NAMES_PUT: %s" % got.get("new"))
    got = bc.get("com/skyy/trees/TreeData.class", {})
    check(got.get("fields_new") == ["cextra Ljava/util/ArrayList;", "cown [Z", "crespecAt [J"] and not got.get("new") and not got.get("gone"),
          "E: TreeData: + cown / crespecAt / cextra: %s" % got.get("fields_new"))
    # fix round: TreeCalc gained badFlag + the WARNED map (its static initializer <clinit>), TreePage the armPrice field
    exp = {"TreeCalc": {"new": ["<clinit>()V", "allComing(II)Z", "badFlag(Ljava/lang/String;Ljava/lang/Object;)V", "comingTree(I)Ljava/lang/String;", "coming(I)Z",
                                "listed(Ljava/lang/Object;Ljava/lang/String;)Z", "needTier(II)I",
                                "readerAlias(Ljava/lang/String;)Ljava/lang/String;", "reads(Ljava/lang/String;Ljava/lang/String;)Z"]},
           "TreeFx": {"new": ["extraStat(Ljava/util/UUID;I)D", "stats(Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;Ljava/util/UUID;[D)V"],
                      "gone": ["stats(Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;[D)V"]},
           "TreePage": {"new": ["buildClass(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;Lcom/hypixel/hytale/component/Store;)V"]},
           "TreeKit": {"new": ["checkClassLevel(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;", "checkClassNode(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"]}}
    for c, want in exp.items():
        got = bc.get("com/skyy/trees/%s.class" % c, {})
        check(sorted(got.get("new", [])) == sorted(want.get("new", [])) and sorted(got.get("gone", [])) == sorted(want.get("gone", [])),
              "E: %s new / gone methods: %s / %s" % (c, got.get("new"), got.get("gone")))
    for c in ("TreeOps", "TreeTick", "SkyyTreesPlugin", "TreeFn", "TreeBonusFn", "TreeSkillCmd", "TreesCmd"):
        got = bc.get("com/skyy/trees/%s.class" % c, {})
        check(not got.get("gone") and not got.get("new") and got.get("fields_same", True), "E: %s changed methods only (no new / gone / fields): %s" % (c, got.get("changed")))
    got = bc.get("com/skyy/trees/TreePage.class", {})
    check(got.get("fields_new") == ["armPrice J", "cpage I", "csel I", "pci I", "pd Lcom/skyy/trees/TreeData;", "probe Z", "undo Ljava/util/ArrayList;"] and not got.get("gone"),
          "E: TreePage: + armPrice / cpage / csel / probe / pci / pd / undo: %s" % got.get("fields_new"))
    got = bc.get("com/skyy/trees/TreeCfg.class", {})
    check(set(got.get("fields_new", [])) == set(["CLASS_ON Z", "AP_FIRST I", "AP_EVERY I", "AP_MAX I", "C_RESPEC_PER J", "C_UNDO Z", "C_EXTRA_AP J", "C_ON [Z", "C_AMT [I", "C_AP [I", "C_MIN [I"])
          and not got.get("new") and not got.get("gone"), "E: TreeCfg: + the class.* fields: %s" % got.get("fields_new"))
    got = bc.get("com/skyy/trees/TreeDefs.class", {})
    check(set(got.get("fields_new", [])) >= set(["NAMES_CSV_CLASS Ljava/lang/String;", "KEY [Ljava/lang/String;", "READERS [Ljava/lang/String;"]), "E: TreeDefs: + NAMES_CSV_CLASS: %s" % got.get("fields_new"))
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    mdiff = sorted(k for k in set(mo) | set(mn) if str(mo.get(k)) != str(mn.get(k)))
    check(mdiff == ["Description", "Name", "Version"] and mn["Version"] == VERSION and mn["Name"] == "0.3 SkyyTrees" and "Alchemy, Smithing" in mn["Description"] and "CLASS TREE" in mn["Description"],
          "E: manifest: Version, Name and the description changed only: %s" % mdiff)
    plug = zn.read("com/skyy/trees/SkyyTreesPlugin.class")
    km = re.search(rb"ready \((skyyui [0-9.]+ [0-9a-f]{12})\) - /tree; ", plug)
    check(km is not None and km.group(1).decode("ascii") == SUI.kit_id(), "E: the ready line's kit id is the kit on disk")
    print("E. jar entries: %d, differ: %s" % (len(nn_), ", ".join(sorted(n.split("/")[-1] for n in diff))))
    print("   methods: " + "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("new", "gone", "fields_new") if bc[n].get(x)))
                                      for n in sorted(bc) if bc[n].get("new") or bc[n].get("gone") or bc[n].get("fields_new")))
    # ---- Z engine-access audit
    if os.path.isfile(au):
        a = json.load(open(au))
        check(a["classes"] == 37 and a["refs"] > 2000 and not a["refused"], "Z: %d classes, %d references, refused: %s" % (a["classes"], a["refs"], a["refused"][:5]))
        check(all(a["per"].get(c, 0) > 20 for c in ("TreeClass", "TreeClassOps", "TreeProbeCmd")), "Z: the part-2 classes were audited: %s" % dict((c, a["per"].get(c)) for c in ("TreeClass", "TreeClassOps", "TreeProbeCmd")))
        check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "Z: the control (BadAccess -> protected sendUpdate) is refused: %s" % a["control"])
        check(all(x.startswith("java.") for x in a.get("caller_sensitive", [])), "Z: only public caller-sensitive JDK methods were checked as public: %s" % a.get("caller_sensitive"))
        print("Z. engine-access audit: %d classes, %d references looked up in their own class, 0 refused; control refused; caller-sensitive JDK "
              "calls checked as public: %s" % (a["classes"], a["refs"], ", ".join(a.get("caller_sensitive", []))))


if __name__ == "__main__":
    main()
