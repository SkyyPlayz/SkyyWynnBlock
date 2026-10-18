"""SkyyQuests 0.4.1 harness (THE STARTER CAMP GEAR, lean round questgear; tools/quests_0_4_1_patch.py) on top of the 0.4.0 harness
(test_skyyquests_0.4.0.py -> 0.3.4 -> ... -> 0.3: every older phase runs again on the 0.4.1 jar; the old gear checks that pinned the 0.2
call pattern on purpose are waived by name - each one has its replacement in G41).

    python SkyyQuests/test_skyyquests_0.4.1.py [--jar SkyyQuests-0.4.1.jar] [--keep]

  A / C / AA  verify, class compare 0.4.0 -> 0.4.1 (non-class entries: manifest.json only), engine-access audit
  G41   gear41  QPay over a stand-in gear:fn:box that makes real ItemStacks WITH a SkyyUnid {lo} document:
                SLOT   gear:head..legs ask the class's weight first (gear:fn:box's ItemStack form: Armor_Wood_* Heavy, Armor_Leather_Soft_*
                       Light, Armor_Cloth_Wool_* Cloth), then the slot's type key; a bag above the class level is kept only as a last resort
                ARMOR  gear:armor = the class weight in the 4 slots, then the 4 type keys - armor keys only
                SECOND gear:second = the class's second weapon types, then its own weapons (usable now first); Priest = its own weapons
                MONK   no bag type at all: gear:weapon / gear:second pay ONE plain Weapon_Staff_Bo_Bamboo (WARN once); an unknown id = waits
                NONE   never a null key, never an armor key for a weapon, never a weapon key for armor; classless = type keys only
                WORDS  rewardProblem / rewardText / payOne know head chest hands legs second; checkGear; the 3 config defaults
                CAMP   tutorial.defeat_mobs: a fresh file pays the set; an old copy (gear:weapon,gear:armor) loads with the set and is NOT
                       rewritten; an owner's own reward is kept; the mini boss keeps gear:weapon,gear:armor
  LV41  live41  a scratch COPY of the live Skyy_SkyyQuests: starting writes nothing, the camp loads with the set, the boss unchanged; who
                already finished the camp / boss (never paid again) and which gear claims still wait
  OLD   every 0.4.0 phase (page40 claim40 mig34 fish34 merge chain migt isl snd defs engine life pay crash static npc board fish live40)
Scratch: tools/dev/scratch/questgear/h (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, json, shutil, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4.1"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "questgear", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)]
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("test_skyyquests_0_4_0", os.path.join(HERE, "test_skyyquests_0.4.0.py"))
T040 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T040)
T034, T033, T03 = T040.T034, T040.T033, T040.T03

JAR = T040.JAR
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.4.0.jar")
SCRATCH, FAKE_DIR, PKG = T03.SCRATCH, T03.FAKE_DIR, T03.PKG
CAMP = "gear:head,gear:chest,gear:hands,gear:legs,gear:second"
EXPECT = {
    "QPay": ["+f ARM_W", "+f ITEMS", "+f KINDS", "+f REP", "+f SLOT_KINDS", "+m bagKeys", "+m bagLo", "+m box1", "+m className", "+m classVal",
             "+m firstFit", "+m gearBag", "+m itemOk", "+m kindOk", "+m repOf", "+m slotOf", "+m srcOf", "+m weaponKeys", "+m weightOf", "~<clinit>", "~m gearBag", "~m payOne"],
    "QDefs": ["+m gearText", "~<clinit>", "~m parse", "~m rewardProblem", "~m rewardText"],
    "QCfg": ["+f GEAR_ARM", "+f GEAR_NOBAG", "+f GEAR_SEC", "~<clinit>", "~m load"],
    "QHooks": ["+m checkGear"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],     # the 3 rows + the version texts
    "SkyyQuestsPlugin": ["~m setup"],                                # the ready line's version
}
ADDED, REMOVED = [], []

# ---------------------------------------------------------------------------------------------------- waivers: the 0.2 gear call pattern
# Each waived check pinned the 0.2 gear:fn:box CALL PATTERN that 0.4.1 changes on purpose (the class weight is asked through gear:fn:box's
# ItemStack form first; the camp pays the set); its replacement check in G41 is named.
WAIVE41 = (
    ("G5 an armor bag: armor slots only", "G41 ARMOR (the class weight's 4 plain pieces, then the 4 slot keys - armor only)"),
    ("G5 no armor fits = null", "G41 ARMOR (8 calls for a classed player: 4 weight pieces + 4 slot keys, never a weapon)"),
    ("FIX-C4 defeat_mobs pays an unidentified weapon AND an armor piece", "G41 CAMP (the set + the second weapon; Skyy 2026-10-17)"),
    ("FIX2-R table 0 + gear in the file = gear only", "G41 CAMP (the camp's gear words, unchanged rule)"),
    ("FIX2-W ... then the class:weapons:free types", "G41 M1 (review M1: the Warrior's second weapon type, the spear, is asked after the free types now)"),
    ("S2 the gear bag is made only by the payer", "G41 M2 (the only new caller is the 2-argument gearBag wrapper itself, which nothing in the jar calls)"),
)
_chk040 = HK.Child.check


def _check41(self, cond, what):
    if not cond:
        for w, why in WAIVE41:
            if str(what).startswith(w):
                self.notes.append("WAIVED (0.4.1, on purpose; covered by %s): %s" % (why, str(what)[:140]))
                return cond
    return _chk040(self, cond, what)


HK.Child.check = _check41


def _eq_as_check(self, got, want, what):
    return self.check(got == want, "%s (got %r, want %r)" % (what, got, want))


# K.eq goes through check (so a waived eq is waived too)
if not getattr(HK.Child, "_eq41", False):
    _eq0 = HK.Child.eq

    def _eq41(self, got, want, what):
        if got != want:
            for w, why in WAIVE41:
                if str(what).startswith(w):
                    self.notes.append("WAIVED (0.4.1, on purpose; covered by %s): %s (got %r)" % (why, str(what)[:120], got))
                    return False
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq41
    HK.Child._eq41 = True

# the compare: 0.4.0 already shipped the 59 kit files - 0.4.1 changes only manifest.json among the non-class entries
def _compare41(out, jar, old_jar, pkg, expect, added, removed=()):
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed":
            return self.check(sorted(got) == ["manifest.json"], "C: non-class entries changed = manifest.json only (%s)" % sorted(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq
    try:
        T040._orig_cmp(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = _eq0


HK.run_compare = _compare41


# ---------------------------------------------------------------------------------------------------- G41
def run_gear41(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    X = T040.QStage(K, scratch, "g41")
    Pl, u, p, s = X.player(1, "Gear")
    br = X.E.bridge
    Pay, Defs, Cfg = X.Pay, X.Defs, X.Cfg
    PyFn = T03.fn_class()
    Int = JClass("java.lang.Integer")
    ItemS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD, BI = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32")
    Log = X.P("QLog")

    def mkbag(lo):
        d = BD()
        d.append("lo", BI(lo))
        d.append("hi", BI(lo + 2))
        return ItemS("Rock_Stone", 1).withMetadata("SkyyUnid", d)
    avail = {}
    calls = []

    def box(a):
        k = a[0]
        key = None if k is None else ("#" + str(k.getItemId()) if isinstance(k, ItemS) else str(k))
        calls.append((key, int(a[1]), str(a[2]), int(a[3]), str(a[4])))
        lo = avail.get(key)
        return None if lo is None else mkbag(lo)
    br.put("gear:fn:box", PyFn(box))
    lvl = {"L": 1}
    br.put("skill:fn:level", PyFn(lambda a: Int(lvl["L"])))

    def ask(cls, kind, L, av):
        avail.clear()
        avail.update(av)
        del calls[:]
        lvl["L"] = L
        if cls:
            br.put("class:" + str(u), cls)
        else:
            br.remove("class:" + str(u))
        r = Pay.gearBag(u, kind)
        return r, [c_[0] for c_ in calls]
    W = {"Warrior": "Weapon_Sword_,Weapon_Spear_,Weapon_Shield_", "Mage": "Weapon_Staff_,Halloween_Broomstick,Weapon_Spellbook_",
         "Archer": "Weapon_Shortbow_,Weapon_Crossbow_,Weapon_Arrow_", "Priest": "Weapon_Wand_,Weapon_Deployable_Healing_Totem",
         "Monk": "Weapon_Staff_Bo_,Weapon_Bo_,Weapon_Fist_", "Assassin": "Weapon_Daggers_,Weapon_Kunai"}
    for c_, w_ in W.items():
        br.put("class:weapons:" + c_, w_)
    br.remove("class:weapons:free")
    lo_of = lambda r: int(Pay.bagLo(r)) if r is not None else None
    # SLOT
    r, c = ask("Warrior", "head", 3, {"#Armor_Wood_Head": 1, "Armor_Head": 1})
    K.check(r is not None and c == ["#Armor_Wood_Head"] and lo_of(r) == 1, "G41 SLOT a Warrior's helmet = the Heavy piece first (one call): %s" % c)
    K.check(all(c2[1:4] == (3, "quest", 0) and c2[4] == str(u) for c2 in calls), "G41 SLOT ... at the class level, src quest, tier 0, the player")
    r, c = ask("Mage", "chest", 1, {"#Armor_Cloth_Wool_Chest": 5, "Armor_Chest": 1})
    K.check(c == ["#Armor_Cloth_Wool_Chest", "Armor_Chest"] and lo_of(r) == 1, "G41 SLOT a Lv 1 Mage: Cloth starts at Lv 5 -> the chest slot in a weight that fits Lv 1: %s" % c)
    r, c = ask("Mage", "chest", 6, {"#Armor_Cloth_Wool_Chest": 5, "Armor_Chest": 6})
    K.check(c == ["#Armor_Cloth_Wool_Chest"] and lo_of(r) == 5, "G41 SLOT a Lv 6 Mage gets the Cloth chest: %s" % c)
    r, c = ask("Mage", "legs", 1, {"#Armor_Cloth_Wool_Legs": 5, "Armor_Legs": 4})
    K.check(c == ["#Armor_Cloth_Wool_Legs", "Armor_Legs"] and lo_of(r) == 5, "G41 SLOT nothing fits Lv 1 = the class weight's bag (the first made), never nothing")
    r, c = ask("Archer", "hands", 2, {"#Armor_Leather_Soft_Hands": 1})
    K.check(c == ["#Armor_Leather_Soft_Hands"] and r is not None, "G41 SLOT an Archer's gauntlets = Light: %s" % c)
    r, c = ask("Priest", "legs", 1, {})
    K.check(r is None and c == ["#Armor_Cloth_Wool_Legs", "Armor_Legs"], "G41 SLOT no bag at all = null (the claim waits quietly): %s" % c)
    r, c = ask(None, "head", 1, {"Armor_Head": 1})
    K.check(c == ["Armor_Head"] and r is not None, "G41 NONE a classless player = the slot's type key only: %s" % c)
    r, c = ask("Gardener", "head", 1, {"Armor_Head": 1})
    K.check(c == ["Armor_Head"], "G41 NONE a class with no weight listed = the slot's type key only: %s" % c)
    # ARMOR
    r, c = ask("Warrior", "armor", 2, {"Armor_Legs": 1})
    K.check(sorted(c[:4]) == sorted("#Armor_Wood_" + x for x in ("Head", "Chest", "Hands", "Legs")) and c[-1] == "Armor_Legs"
            and all(str(x).startswith(("Armor_", "#Armor_")) for x in c) and r is not None,
            "G41 ARMOR gear:armor = the class weight in the 4 slots, then the slot keys until one fits (armor only): %s" % c)
    r, c = ask("Warrior", "armor", 2, {"#Armor_Wood_Chest": 1})
    K.check(len(c) <= 4 and c[-1] == "#Armor_Wood_Chest" and r is not None, "G41 ARMOR ... a Heavy piece that fits stops the search: %s" % c)
    r, c = ask("Warrior", "armor", 2, {})
    K.check(r is None and len(c) == 8 and None not in c and not [x for x in c if "Weapon" in str(x)], "G41 ARMOR no armor fits = null, never a weapon")
    # SECOND
    r, c = ask("Archer", "second", 1, {"Weapon_Crossbow": 15, "Weapon_Shortbow": 1})
    K.check(c[0] == "Weapon_Crossbow" and lo_of(r) == 1 and "Weapon_Shortbow" in c, "G41 SECOND a Lv 1 Archer: crossbows start at Lv 15 -> a bow that fits: %s" % c)
    r, c = ask("Archer", "second", 16, {"Weapon_Crossbow": 15, "Weapon_Shortbow": 1})
    K.check(c == ["Weapon_Crossbow"] and lo_of(r) == 15, "G41 SECOND a Lv 16 Archer gets the crossbow: %s" % c)
    r, c = ask("Warrior", "second", 1, {"Weapon_Spear": 1, "Weapon_Sword": 1})
    K.check(c == ["Weapon_Spear"] and r is not None, "G41 SECOND a Warrior's second weapon = a spear: %s" % c)
    r, c = ask("Assassin", "second", 1, {"Weapon_Kunai": 20})
    K.check(c[0] == "Weapon_Kunai" and lo_of(r) == 20, "G41 SECOND nothing usable now = the second weapon's bag anyway (never nothing): %s" % c)
    r, c = ask("Priest", "second", 1, {"Weapon_Wand": 1})
    K.check("Weapon_Wand" in c and r is not None and not [x for x in c if x not in ("Weapon_Wand", "Weapon_Deployable_Healing_Totem")], "G41 SECOND the Priest (no second weapon yet) = a wand: %s" % c)
    K.check(not [x for x in c if str(x).startswith("Armor")], "G41 NONE a weapon reward never asks for armor")
    # M1 (review): the boss's gear:weapon asks the class's second weapon types LAST (the camp paid one of those)
    for _i in range(12):
        r, c = ask("Archer", "weapon", 20, {"Weapon_Shortbow": 1, "Weapon_Crossbow": 15})
        if "Weapon_Crossbow" in c or c[-1] != "Weapon_Shortbow":
            break
    K.check("Weapon_Crossbow" not in c and c[-1] == "Weapon_Shortbow", "G41 M1 gear:weapon = the class's own (non-second) types first, 12 times: %s" % c)
    r, c = ask("Archer", "weapon", 20, {"Weapon_Crossbow": 15})
    K.check(c[-1] == "Weapon_Crossbow" and r is not None, "G41 M1 ... the second weapon type only when nothing else fits: %s" % c)
    # M2 (review): src "quest" only for a tutorial grant (SkyyGear's free quest identify), "board" for every other grant
    K.check(str(Pay.srcOf("%s:tutorial.defeat_mobs:15" % str(u))) == "quest" and str(Pay.srcOf("%s:board.hunt10@20380:4" % str(u))) == "board"
            and str(Pay.srcOf("%s:mining.mining_level5:2" % str(u))) == "board" and str(Pay.srcOf(None)) == "board", "G41 M2 srcOf: tutorial = quest, the rest = board")
    avail.clear()
    avail["#Armor_Wood_Head"] = 1
    del calls[:]
    br.put("class:" + str(u), "Warrior")
    r = Pay.gearBag(u, "head", "board")
    K.check(r is not None and [c_[2] for c_ in calls] == ["board"], "G41 M2 a board grant asks gear:fn:box with src board: %s" % calls)
    # MONK
    HS = JClass("java.util.HashSet")()
    HS.add("Weapon_Staff_Bo_Bamboo")
    Pay.ITEMS = HS                     # the harness has no Item asset map (the game asks it)
    nw = len([x for x in (Log.LINES or []) if "no gear bag for the Monk" in str(x)])
    r, c = ask("Monk", "weapon", 1, {})
    K.check(r is not None and str(r.getItemId()) == "Weapon_Staff_Bo_Bamboo" and int(r.getQuantity()) == 1 and r.getMetadata() is None
            and sorted(c) == ["Weapon_Bo", "Weapon_Fist", "Weapon_Staff_Bo"],
            "G41 MONK no bag type at all: ONE plain Weapon_Staff_Bo_Bamboo (after asking each type once): %s %s" % (r, c))
    r, c = ask("Monk", "second", 1, {})
    K.check(r is not None and str(r.getItemId()) == "Weapon_Staff_Bo_Bamboo" and c[0] == "Weapon_Fist", "G41 MONK gear:second too: %s" % c)
    K.eq(len([x for x in (Log.LINES or []) if "no gear bag for the Monk" in str(x)]) - nw, 1, "G41 MONK ... a WARN once")
    r, c = ask("Monk", "weapon", 1, {"Weapon_Bo": 1})
    K.check(r is not None and str(r.getItemId()) == "Rock_Stone", "G41 MONK once SkyyGear has a bo bag, the bag is paid")
    HS = JClass("java.util.HashSet")()
    HS.add("Weapon_Staff_Wood")
    Pay.ITEMS = HS
    r, c = ask("Monk", "weapon", 1, {})
    K.check(r is None, "G41 MONK an id the game does not know = no plain weapon (the claim waits)")
    Pay.ITEMS = None
    r, c = ask("Mage", "head", 1, {})
    K.check(r is None, "G41 MONK the plain weapon is never paid for an armor word")
    # WORDS
    K.check(Defs.rewardProblem(CAMP) is None and Defs.rewardProblem("gear:feet") is not None, "G41 WORDS rewardProblem knows the 5 new words")
    K.eq(str(Defs.rewardText(CAMP)), "+1 unidentified helmet  +1 unidentified chestplate  +1 unidentified gauntlets  +1 unidentified leggings  +1 unidentified second weapon",
         "G41 WORDS rewardText")
    K.eq(str(Defs.rewardText("gear:weapon,gear:armor")), "+1 unidentified weapon  +1 unidentified armor", "G41 WORDS the 0.2 words read as before")
    K.eq(int(Pay.payOne(p, s, "gear|shield|%s:t.x:1" % str(u))), -1, "G41 WORDS payOne: an unknown kind = LOST? as before")
    pr0 = p.pr
    p.pr = None
    K.eq(int(Pay.payOne(p, s, "gear|second|%s:t.x:2" % str(u))), 0, "G41 WORDS payOne: gear|second is a known kind (no world = refused, waits)")
    p.pr = pr0
    H = X.P("QHooks")
    K.check(H.checkGear("quests.gear.classArmor", str(Cfg.GEAR_ARM)) is None and H.checkGear("quests.gear.classArmor", "Mage:Plate") is not None
            and H.checkGear("quests.gear.classSecond", str(Cfg.GEAR_SEC)) is None and H.checkGear("quests.gear.classSecond", "Archer:Bow") is not None
            and H.checkGear("quests.gear.classSecond", "Archer:Weapon_Shortbow_Iron") is not None and H.checkGear("quests.gear.noBagWeapon", str(Cfg.GEAR_NOBAG)) is None
            and H.checkGear("quests.gear.classArmor", "Mage") is not None, "G41 WORDS checkGear (the defaults pass; bad weights / types are refused)")
    K.check(str(Cfg.GEAR_ARM).startswith("Warrior:Heavy") and "Mage:Cloth" in str(Cfg.GEAR_ARM) and "Spellblade:Light" in str(Cfg.GEAR_ARM)
            and "Archer:Weapon_Crossbow" in str(Cfg.GEAR_SEC) and str(Cfg.GEAR_NOBAG) == "Monk:Weapon_Staff_Bo_Bamboo",
            "G41 WORDS the 3 defaults loaded (%s | %s | %s)" % (Cfg.GEAR_ARM, Cfg.GEAR_SEC, Cfg.GEAR_NOBAG))
    cf = os.path.join(X.base, "config.properties")
    txt = open(cf, encoding="utf-8").read()
    open(cf, "w", encoding="utf-8").write("\n".join(l_ for l_ in txt.split("\n") if not l_.startswith("gear.")) + "\ngear.classArmor=Mage:Heavy\n")
    Cfg.load()
    K.check(str(Cfg.GEAR_ARM) == "Mage:Heavy" and str(Cfg.GEAR_NOBAG) == "Monk:Weapon_Staff_Bo_Bamboo", "G41 WORDS a missing line = the default, a set line is read")
    r, c = ask("Mage", "head", 1, {"#Armor_Wood_Head": 1})
    K.check(c == ["#Armor_Wood_Head"], "G41 WORDS ... and used (Mage:Heavy -> the Heavy piece)")
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load()
    # CAMP: the tutorial file
    tf = os.path.join(X.base, "quests", "tutorial.properties")
    fresh = open(tf, encoding="utf-8").read()
    L = Defs.line("tutorial")
    by = dict((str(t.id), t) for t in L.tasks)
    K.check("task.12.reward=" + CAMP + "\n" in fresh and "updated by 0.3.3" in fresh and "gear:second = your class's second weapon" in fresh,
            "G41 CAMP a fresh server's file: the camp pays the set (+ the header names the words)")
    K.eq(str(Defs.rewardOf(L, by["defeat_mobs"])), CAMP, "G41 CAMP the fresh camp reward")
    K.eq(str(Defs.rewardOf(L, by["mini_boss"])), "gear:weapon,gear:armor", "G41 CAMP the mini boss keeps a weapon + an armor piece")
    old = fresh.replace("task.12.reward=" + CAMP + "\n", "task.12.reward=gear:weapon,gear:armor\n")
    for nm, body, want in (("old", old, CAMP), ("edited", fresh.replace("task.12.reward=" + CAMP + "\n", "task.12.reward=gear:armor,gear:weapon\n"), "gear:armor,gear:weapon")):
        open(tf, "w", encoding="utf-8", newline="").write(body)
        b0 = open(tf, "rb").read()
        Defs.load()
        t2 = [t for t in Defs.line("tutorial").tasks if str(t.id) == "defeat_mobs"][0]
        K.eq(str(Defs.rewardOf(Defs.line("tutorial"), t2)), want, "G41 CAMP an %s copy loads with %s" % (nm, want))
        K.check(open(tf, "rb").read() == b0 and not os.path.exists(tf + ".0.4.1.new"), "G41 CAMP ... the %s file is not rewritten (no byte changes)" % nm)
    K.check(not [str(x) for x in Defs.PROBLEMS], "G41 CAMP no file problems: %s" % [str(x) for x in Defs.PROBLEMS])
    K.save()


# ---------------------------------------------------------------------------------------------------- LV41: the live copy
def run_live41(out, jar, scratch, home):
    K = HK.Child(out)
    if home is None or not os.path.isdir(home):
        K.check(False, "LV41 no live copy")
        K.save()
        return
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(mods)
    X = T040.QStage(K, scratch, "lv41", base=home)
    K.eq(HK.tree_hash(mods), h0, "LV41 starting 0.4.1 on the live copy writes nothing (no one-time update)")
    L = X.Defs.line("tutorial")
    by = dict((str(t.id), t) for t in L.tasks)
    K.eq(str(X.Defs.rewardOf(L, by["defeat_mobs"])), CAMP, "LV41 the live camp (gear:weapon,gear:armor in the file) loads with the set")
    K.eq(str(X.Defs.rewardOf(L, by["mini_boss"])), "gear:weapon,gear:armor", "LV41 the live boss is unchanged")
    pdir = os.path.join(home, "players")
    camp, boss, waiting = [], [], []
    for f in sorted(os.listdir(pdir)):
        t = open(os.path.join(pdir, f), encoding="utf-8").read()
        if "\ndone.tutorial.defeat_mobs=" in "\n" + t:
            camp.append(f)
        if "\ndone.tutorial.mini_boss=" in "\n" + t:
            boss.append(f)
        waiting += [(f, l_.split("=", 1)[1]) for l_ in t.split("\n") if l_.startswith("claim.") and "gear|" in l_]
    K.notes.append("LV41 profiles that finished the camp (never paid again): %d %s" % (len(camp), camp))
    K.notes.append("LV41 profiles that finished the boss: %d %s" % (len(boss), boss))
    K.notes.append("LV41 gear claims still waiting (0.4.1 pays them): %s" % waiting)
    K.check(True, "LV41 counted %d camp / %d boss finishers, %d waiting gear claim(s)" % (len(camp), len(boss), len(waiting)))
    K.eq(HK.tree_hash(mods), h0, "LV41 nothing written")
    K.save()


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        T03.mkfake(HK.arg("--mkfake"), JAR)
        sys.exit(0)
    if "--phase" not in sys.argv:
        shutil.rmtree(FAKE_DIR, ignore_errors=True)
        os.makedirs(FAKE_DIR, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(FAKE_DIR, "tmp")
        env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    lg = T033.legacy
    phases = [("gear41", run_gear41), ("page40", T040.run_page40), ("claim40", T040.run_claim40),
              ("mig34", T034.run_mig34), ("fish34", T034.run_fish34),
              ("merge", T033.run_merge), ("chain", T033.run_chain), ("migt", T033.run_migt),
              ("isl", lg(T040.T032.run_isl)), ("snd", lg(T040.T031.run_snd)), ("defs", lg(T03.run_defs)), ("engine", lg(T03.run_engine)),
              ("life", lg(T03.run_life)), ("pay", lg(T03.run_pay)), ("crash", lg(T03.run_crash)), ("static", lg(T03.run_static)),
              ("npc", lg(T03.run_npc)), ("board", lg(T03.run_board)), ("fish", lg(T03.run_fish)), ("live40", T040.run_live40),
              ("live41", run_live41)]
    only = HK.arg("--only")
    if only:
        phases = [ph for ph in phases if ph[0] in only.split(",")]
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, phases, os.path.abspath(__file__), live=(T040.LIVE_Q, "Skyy_SkyyQuests"),
               removed=REMOVED)
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
    sys.exit(1 if HK.FAILS else 0)
