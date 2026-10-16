"""Harness for SkyyPets 0.4.1 (THE PET MENU: tabs Pets / Eggs / Hatchery; tools/pets_0_4_1_patch.py).
Build first: python tools/pets_0_4_1_patch.py; python SkyyPets/build_skyypets_0.4.1.py

    python SkyyPets/test_skyypets_0.4.1.py [--dir <folder inside tools/dev/scratch/>] [--no-old]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.0 -> 0.4.1 (exactly the planned members;
              + PetHatchery, PetHatchOpen; non-class entries = manifest + the 30 egg item JSON (no Recipe) + the lang file), engine audit
  HATCH       EXECUTED in a plain -Xverify:all JVM: a fake inventory (with a "saved" copy = the player file), a fake Void (sacks:fn:count /
              take / put / commit, with a "saved" copy = the pool file), a fake clock (PetHatchery.CLOCK_OFF):
              ROWS the Server Setup defaults; CRAFT from the inventory, from the Void (commit only after the egg), every refusal rolled
              back (missing, no room, Void paused, crafting off, a Rare egg); PLACE (inventory, then Void), the slot line + the debt in
              ONE save, full slots refused, the Beastmastery bridge adds slots; WAIT (fake clock: not ready = refused, ready = hatched
              ONCE: one pet, the slot empty, a second press finds nothing; a full collection / no kind = refused, the egg waits); RELOG
              mid-wait (the record released + reloaded, the clock runs on while offline); TAKE OUT (the egg back, the timer lost, the
              credit clears, no room = refused); FUSE PETS (4 -> 1, Mythic only from eggs); FUSE EGGS (4 -> 1, the top rarity, too few,
              no room = everything back); the guard of two open moves of one egg; the ready line once; CRASH a simulated stop after
              EVERY step of place / take-out / hatch (+ the player / Void save timing): restart = REC cleared + scanAll + both recovers +
              the join reconcile -> eggs everywhere + hatched pets == before, every intent closed once; RIGHT-click = one line, null page;
              BENCH no egg recipe in any SET jar (+ every JSON naming a pet egg is ours and has no Recipe)
  STAGE       EXECUTED in the hub stage (tools/hub_tab_kit.py: the REAL PageManager, Universe, inventories): the three tabs (hub
              page_check each, tab clicks, the stuck-tooltip guard), Eggs rows + a craft that cannot give (the stage has no item assets)
              rolled back, the Hatchery: place from a real inventory by a grid click, the slot rows, the fake clock, Hatch -> the reel
              page opens with the pet already saved, the reels to the result, its Hatchery button back to tab 2, Take out (two presses),
              the egg / pet fuse modes
  LIVE        START TWICE on a scratch COPY of the live Skyy_SkyyPets folder: nothing written, no cut-off move
  R040        the 0.4.0 harness's EGG + STAGE phases EXECUTED on the 0.4.1 jar; the differences are the listed EXPECTED_R040 ones
Exit code 1 on any failure.
"""
import os, sys, subprocess, json, zipfile, re, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyeggs as EG

VERSION = "0.4.1"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "petmenu", "test")))
RAR = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]


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
_CFG_F = ["HATCH_SLOTS", "HATCH_NOTIFY", "EGG_CRAFT", "EFUSE_ON", "EFUSE_COUNT", "EFUSE_MAX_S"] + ["HATCH_W%d" % i for i in range(1, 7)]
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],      # the kit: the new rows
    "PetsCfg": sorted(["+f " + f for f in _CFG_F] + ["+m hatchWait", "+m efuseMax", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"]),
    "PetInv": ["+m takeN"], "PetInvReal": ["+m takeN"],
    "PetEggSave": ["+m force0", "~m force"], "PetSaveDone": ["~m accept"],
    "PetEgg": sorted(["+f NOFORCE", "+m vcall", "+m voidCount", "+m voidTake", "+m voidPut", "+m voidCommit", "+m voidSrc", "+m srcCount", "+m srcTake", "~<clinit>", "~m clearDebt", "~m debts"]),
    "PetEggGive": ["~m run"],
    "PetHatchFactory": ["~m apply"],
    "PetHatchPage": ["+m begin", "~m build", "~m go", "~m handleDataEvent"],
    "PetsPage": sorted(["+f EG_CELLS", "+f tab", "+f emode", "+f eids", "+f hsl", "+f egCells", "+m fillEggGrid", "+m slotClick", "+m eggClick",
                        "~c ", "~m build", "~m clearGrid", "~m handleDataEvent"]),
    "PetTick": ["~m leave"], "PetTickSys": ["~m tick"],
    "SkyyPetsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["PetHatchery", "PetHatchOpen"]


def ledger(mods):
    p = os.path.join(mods, "Skyy_SkyyPets", "ledger.log")
    return open(p, encoding="utf-8").read().splitlines() if os.path.exists(p) else []


def _unesc(t):
    o, i = [], 0
    while i < len(t):
        c = t[i]
        if c == "\\" and i + 1 < len(t):
            n = t[i + 1]
            if n == "u" and i + 5 < len(t):
                o.append(chr(int(t[i + 2:i + 6], 16)))
                i += 6
                continue
            o.append({"t": chr(9), "n": chr(10), "r": chr(13), "f": chr(12)}.get(n, n))
            i += 2
            continue
        o.append(c)
        i += 1
    return "".join(o)


def props(path):
    out = {}
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="latin-1").read().splitlines():
        if not l or l.startswith("#"):
            continue
        j, esc = 0, False
        while j < len(l):
            if esc:
                esc = False
            elif l[j] == "\\":
                esc = True
            elif l[j] in "=:":
                break
            j += 1
        if j >= len(l):
            continue
        out[_unesc(l[:j])] = _unesc(l[j + 1:])
    return out


def tree(d):
    out = {}
    for r_, _ds, fs in os.walk(d):
        for f_ in fs:
            p = os.path.join(r_, f_)
            out[os.path.relpath(p, d)] = open(p, "rb").read()
    return out


class Inv(object):
    """one player's inventory as {id: n} + a 'saved' copy = what the player file holds; cap = the most items it takes (None = no limit)"""

    def __init__(self, items=None, cap=None, refuse=()):
        self.live = dict(items or {})
        self.saved = copy.deepcopy(self.live)
        self.cap = cap
        self.refuse = set(refuse)     # ids that never fit (a full inventory for that item)

    def heldId(self):
        return None

    def heldSlot(self):
        return -1

    def heldQty(self):
        return 0

    def count(self, i):
        return int(self.live.get(str(i), 0))

    def takeOne(self, slot, i):
        return 0

    def takeAny(self, i):
        return self.takeN(i, 1)

    def takeN(self, i, n):
        i, n = str(i), int(n)
        t = min(n, self.live.get(i, 0))
        if t > 0:
            self.live[i] -= t
        return t

    def give(self, i, n):
        n = int(n)
        if str(i) in self.refuse:
            return 0
        if self.cap is not None:
            n = max(0, min(n, self.cap - sum(self.live.values())))
        if n:
            self.live[str(i)] = self.live.get(str(i), 0) + n
        return n

    def psave(self):
        self.saved = copy.deepcopy(self.live)

    def restart(self):
        self.live = copy.deepcopy(self.saved)


def proxy_inv(inv):
    from jpype import JProxy
    return JProxy(PKG + "PetInv", dict={"heldId": inv.heldId, "heldSlot": inv.heldSlot, "heldQty": inv.heldQty, "count": inv.count,
                                        "takeOne": inv.takeOne, "takeAny": inv.takeAny, "takeN": inv.takeN, "give": inv.give})


class Void(object):
    """the fake SkyySacks Void of one player: live {id: n}, saved = the pool file, paused = count -1 / take 0; take -> owed (put refunds
    only what a take removed, commit clears it) - the sacks:fn:* shapes"""

    def __init__(self):
        self.live, self.saved, self.paused, self.owed, self.calls = {}, {}, False, {}, []

    def count(self, a):
        self.calls.append(("count", str(a[1])))
        return -1 if self.paused else int(self.live.get(str(a[1]), 0))

    def take(self, a):
        i, n = str(a[1]), int(a[2])
        self.calls.append(("take", i, n))
        if self.paused:
            return 0
        t = min(n, self.live.get(i, 0))
        self.live[i] = self.live.get(i, 0) - t
        self.owed[i] = self.owed.get(i, 0) + t
        return t

    def put(self, a):
        i, n = str(a[1]), int(a[2])
        self.calls.append(("put", i, n))
        t = min(n, self.owed.get(i, 0))
        self.owed[i] = self.owed.get(i, 0) - t
        self.live[i] = self.live.get(i, 0) + t
        return t

    def commit(self, a):
        i, n = str(a[1]), int(a[2])
        self.calls.append(("commit", i, n))
        t = min(n, self.owed.get(i, 0))
        self.owed[i] = self.owed.get(i, 0) - t
        return t

    def save(self):
        self.saved = copy.deepcopy(self.live)

    def restart(self):
        self.live, self.owed = copy.deepcopy(self.saved), {}


def _uarr(JClass, names):
    UUID = JClass("java.util.UUID")
    a = JClass("java.util.UUID[]")(len(names))
    for i, n in enumerate(names):
        a[i] = UUID.fromString(n)
    return a


# ======================================================================================================== HATCH
def run_hatch(out, jar, scratch, _home):
    from jpype import JClass, JProxy
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Egg, Defs, Eng, Hy = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetEgg"), P_("PetEggDefs"),
                                                 P_("PetsEng"), P_("PetHatchery"))
    Paths, UUID, Random, Bool, Long, Integer = (JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.util.Random"),
                                                JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Integer"))
    Sys = JClass("java.lang.System")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "hatch-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    home = os.path.join(mods, "Skyy_SkyyPets")
    Store.ROOT = Paths.get(home)
    Store.DIR = Store.ROOT.resolve("pets")
    pdir = os.path.join(home, "pets")
    told = []
    names = {}
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: _uarr(JClass, list(names)), "byName": lambda n: None,
                                            "nameOf": lambda u: names.get(str(u), str(u)), "tell": lambda u, t, c: told.append((str(u), str(t)))})
    BR = Log.bridge()
    V = Void()
    for k_, f_ in (("count", V.count), ("take", V.take), ("put", V.put), ("commit", V.commit)):
        BR.put("sacks:fn:" + k_, JProxy("java.util.function.Function", dict={"apply": (lambda f: (lambda a: Long(f(list(a)))))(f_)}))
    Egg.RNG = Random(41)
    now = lambda: int(Sys.currentTimeMillis())

    def mk(n):
        u = UUID.fromString("00000000-0000-0000-0000-%012d" % n)
        names[str(u)] = "P%d" % n
        key = str(Store.pkey(u))
        Store.KEYOF.put(u, key)
        r = Store.get(key)
        r.set("starter", "1")
        return u, key, r

    def clk():
        Hy.CLICK.clear()
        Egg.HATCHING.clear()

    def S(x):
        return None if x is None else str(x)

    def place(u, inv, egg):
        clk()
        return [S(x) for x in Hy.place(u, proxy_inv(inv), egg, "harness")]

    def hatch(u, n, hid=None):
        clk()
        return [S(x) for x in Hy.hatch(u, n, hid, "harness")]

    def takeout(u, inv, n, hid=None):
        clk()
        return [S(x) for x in Hy.takeOut(u, proxy_inv(inv), n, hid, "harness")]

    def craft(u, inv, egg):
        clk()
        return str(Hy.craft(u, proxy_inv(inv), egg, "harness"))

    def efuse(u, inv, egg):
        clk()
        return str(Hy.efuse(u, proxy_inv(inv), egg, "harness"))

    def fileof(k):
        return props(os.path.join(pdir, k + ".properties"))

    def settle(u, r, inv, plus=31000):
        """the forced player save landed (or 30 s passed): every open debt / credit of this run clears"""
        inv.psave()
        Egg.debts(u, r, proxy_inv(inv), now() + plus)
        Hy.credits(u, r, proxy_inv(inv), now() + plus)

    # ---------------------------------------------------------------- ROWS
    K.check(int(Cfg.HATCH_SLOTS) == 2 and [int(Cfg.hatchWait(i)) for i in range(1, 7)] == [120, 300, 900, 1800, 3600, 7200]
            and bool(Cfg.HATCH_NOTIFY) and bool(Cfg.EGG_CRAFT) and bool(Cfg.EFUSE_ON) and int(Cfg.EFUSE_COUNT) == 4 and str(Cfg.EFUSE_MAX_S) == "legendary"
            and int(Cfg.efuseMax()) == 5, "ROWS the Hatchery defaults: 2 slots, waits 120/300/900/1800/3600/7200 s, notify, crafting, egg fuse 4 up to Legendary")
    dt = str(Cfg.DEFAULT_TEXT)
    K.check("pets.hatch.slots=2\n" in dt and "pets.hatch.wait.mythic=7200\n" in dt and "pets.eggfuse.maxRarity=legendary\n" in dt and "pets.egg.craft=true\n" in dt,
            "ROWS the default config text holds the new rows")
    Cfg.EFUSE_MAX_S = "mythic"
    K.check(int(Cfg.efuseMax()) == 5, "ROWS a hand-edited egg-fuse top of Mythic still stops at Legendary (Mythic eggs never come from fusing)")
    Cfg.EFUSE_MAX_S = "legendary"
    K.eq([str(x) for x in Hy.CRAFT], sorted([EG.egg_id(c, r) for c, r in EG.RECIPES], key=lambda i: (EG.RARITIES.index(EG.parse_id(i)[1]), EG.name(*EG.parse_id(i)))),
         "ROWS the Eggs tab lists the 10 craftable eggs, tier (rarity) first, then name")
    K.check(str(Hy.costText(None, proxy_inv(Inv()), "Skyy_PetEgg_Combat_Common")) == "1 Egg (0) + 128 Bone Fragments (0) + 16 Light Leather (0)",
            "ROWS the cost line names every input: %s" % Hy.costText(None, proxy_inv(Inv()), "Skyy_PetEgg_Combat_Common"))
    # ---------------------------------------------------------------- RIGHT: the egg's right-click
    rc0 = int(Hy.RIGHT.get())
    K.check(P_("PetHatchFactory")().apply(None) is None and Hy.rightClick("x") is None and int(Hy.RIGHT.get()) == rc0 + 0,
            "RIGHT the right-click factory opens nothing (null) for anything that is not a player")
    # ---------------------------------------------------------------- CRAFT
    u1, k1, r1 = mk(701)
    EC = "Skyy_PetEgg_Mining_Common"        # 1 Food_Egg + 12 Enchanted Cobblestone
    inv1 = Inv({"Food_Egg": 2, "Skyy_Ench_Cobblestone": 5})
    V.live = {"Skyy_Ench_Cobblestone": 20}
    V.save()
    m = craft(u1, inv1, EC)
    K.check(m.startswith("+Crafted a Common Mining Egg") and inv1.count(EC) == 1 and inv1.count("Food_Egg") == 1 and inv1.count("Skyy_Ench_Cobblestone") == 0
            and V.live["Skyy_Ench_Cobblestone"] == 13 and ("commit", "Skyy_Ench_Cobblestone", 7) in V.calls and V.owed.get("Skyy_Ench_Cobblestone") == 0,
            "CRAFT from the inventory first (5), the rest from the Void (7, committed after the egg): %s" % m)
    K.check(any("egg-craft %s" % EC in l for l in ledger(mods)), "CRAFT a ledger line")
    fx = [str(x) for x in Egg.FORCE.keySet().toArray() if str(x).startswith("x.") and str(Egg.FORCE.get(x)) == k1]
    K.check(len(fx) == 1, "CRAFT (critic fix 1) a craft that used the Void asks for a forced player save at the next tick: %s" % fx)
    Egg.FORCE.clear()
    inv1b = Inv({"Food_Egg": 1, "Skyy_Ench_Cobblestone": 2})
    V.live = {"Skyy_Ench_Cobblestone": 3}
    m2 = craft(u1, inv1b, EC)
    K.check(m2.startswith("-You need 12 Enchanted Cobblestone (you have 5)") and inv1b.live == {"Food_Egg": 1, "Skyy_Ench_Cobblestone": 2} and V.live["Skyy_Ench_Cobblestone"] == 3,
            "CRAFT not enough = refused, nothing moved: %s" % m2)
    inv1c = Inv({"Food_Egg": 1, "Skyy_Ench_Cobblestone": 4}, refuse=[EC])
    V.live = {"Skyy_Ench_Cobblestone": 8}
    V.calls = []
    m3 = craft(u1, inv1c, EC)
    K.check(m3.startswith("-No room in your inventory") and inv1c.live.get("Food_Egg") == 1 and inv1c.count("Skyy_Ench_Cobblestone") == 4
            and V.live["Skyy_Ench_Cobblestone"] == 8 and not any(c[0] == "commit" for c in V.calls) and inv1c.count(EC) == 0,
            "CRAFT no room for the egg = every input back (inventory + Void put, no commit): %s %s" % (m3, inv1c.live))
    V.paused = True
    m4 = craft(u1, Inv({"Food_Egg": 1}), EC)
    V.paused = False
    Cfg.EGG_CRAFT = False
    m5 = craft(u1, Inv({"Food_Egg": 1, "Skyy_Ench_Cobblestone": 12}), EC)
    Cfg.EGG_CRAFT = True
    m6 = craft(u1, Inv({"Food_Egg": 1}), "Skyy_PetEgg_Mining_Rare")
    K.check(m4.startswith("-Your Void is busy") and m5.startswith("-Egg crafting is switched off") and m6.startswith("-Only Common and Uncommon"),
            "CRAFT a paused Void / crafting off / a Rare egg = refused: %s | %s | %s" % (m4, m5, m6))
    # ---------------------------------------------------------------- PLACE + WAIT + HATCH
    EID = "Skyy_PetEgg_Mining_Rare"
    inv2 = Inv({EID: 3})
    inv2.psave()
    V.live = {}
    p1 = place(u1, inv2, EID)
    hid1 = p1[1]
    f = fileof(k1)
    K.check(p1[0].startswith("+Rare Mining Egg is in Hatchery slot 1 - it hatches in 15m 00s") and inv2.count(EID) == 2 and p1[2] == "inv"
            and f.get("hatchery.1", "").startswith(EID + "|") and f.get("hatchery.1").split("|")[2] == hid1 and f.get("eggdebt." + hid1, "").startswith(EID + "|3|"),
            "PLACE one egg out (3 -> 2), ONE save holds the slot line + the debt: %s" % p1)
    L = [l for l in ledger(mods) if hid1 in l]
    K.check(len(L) == 2 and "egg-place-intent %s egg=%s slot=1 src=inv before=3" % (hid1, EID) in L[0] and "egg-place-done %s slot=1" % hid1 in L[1]
            and L[0].split("\t")[1] == "-", "PLACE the ledger: intent + done (pet id -)")
    h0 = hatch(u1, 1, hid1)
    K.check(h0[0].startswith("-Still hatching - 15m 00s left") or h0[0].startswith("-Still hatching - 14m"), "WAIT not ready = refused: %s" % h0[0])
    p2 = place(u1, inv2, EID)
    K.check(p2[0].startswith("=Saving your last egg move"), "PLACE a second move of the same egg waits for the first one's player save: %s" % p2[0])
    settle(u1, r1, inv2)
    p2 = place(u1, inv2, EID)
    settle(u1, r1, inv2)
    p3 = place(u1, inv2, EID)
    K.check(p2[0].startswith("+Rare Mining Egg is in Hatchery slot 2") and p3[0].startswith("-All 2 Hatchery slots are in use") and inv2.count(EID) == 1,
            "PLACE slot 2, then full slots = refused, the egg kept: %s" % p3[0])
    BR.put("pets:hatch:slots:" + str(u1), Integer(1))
    p3 = place(u1, inv2, EID)
    K.check(p3[0].startswith("+Rare Mining Egg is in Hatchery slot 3") and int(Hy.slots(u1)) == 3 and "1 from Beastmastery" in str(Hy.headText(r1, u1)),
            "PLACE the Beastmastery bridge pets:hatch:slots:<uuid> = 1 extra slot: %s" % Hy.headText(r1, u1))
    BR.remove("pets:hatch:slots:" + str(u1))
    settle(u1, r1, inv2)
    K.check(int(Hy.slots(u1)) == 2 and int(Hy.shownSlots(r1, u1)) == 3, "PLACE ... the bridge gone: 2 slots, the egg in slot 3 still shows and hatches")
    # the ready line + the fake clock
    told.clear()
    Hy.tickRec(u1, r1, proxy_inv(inv2), now())
    K.check(not told, "WAIT no ready line before the wait")
    Hy.CLOCK_OFF = 15 * 60 * 1000 + 1000
    Hy.tickRec(u1, r1, proxy_inv(inv2), now())
    Hy.tickRec(u1, r1, proxy_inv(inv2), now())
    K.check(len([t for x, t in told if "is ready to hatch" in t]) == 3, "WAIT ready: ONE chat line per egg (3 slots), not again: %s" % told[:4])
    n0 = int(r1.count())
    hh = hatch(u1, 1, hid1)
    hid_h, pid = hh[1], hh[2]
    f = fileof(k1)
    K.check(hh[0].startswith("+You hatched a ") and int(r1.count()) == n0 + 1 and "hatchery.1" not in f and f.get("pet.%s.src" % pid) == "egg:%s:%s" % (EID, hid_h)
            and f.get("hatch.unseen." + hid_h, "").startswith(EID + "|") and int(r1.levelOf(pid)) == 1 and str(r1.kindOf(pid)) in EG.ORDER["Mining"],
            "HATCH ready: ONE save = the slot empty + one Lv 1 Mining pet (src egg:<egg>:<hid>) + the reveal line: %s" % hh)
    L = ledger(mods)
    K.check(any(("hatch-intent %s egg=%s slot=h1 placed=%s" % (hid_h, EID, hid1)) in l for l in L) and any(("hatch-done %s %s" % (hid_h, pid)) in l for l in L),
            "HATCH the ledger: hatch-intent (slot=h1) + hatch-done (0.4.0's recover closes a cut-off one)")
    hh2 = hatch(u1, 1, hid1)
    K.check(hh2[0].startswith("-That slot is empty") and int(r1.count()) == n0 + 1, "HATCH a second press (a stale page) hatches nothing: %s" % hh2[0])
    om = int(Cfg.OWNED_MAX)
    Cfg.OWNED_MAX = int(r1.count())
    hf = hatch(u1, 2)
    Cfg.OWNED_MAX = om
    Cfg.EGG_O_MINING = "-"
    hk = hatch(u1, 2)
    Cfg.EGG_O_MINING = ",".join(EG.ORDER["Mining"])
    K.check(hf[0].startswith("-Your pet collection is full") and hk[0].startswith("-No Mining pet can hatch") and r1.get("hatchery.2") is not None,
            "HATCH a full collection / no kind = refused, the egg waits in its slot: %s | %s" % (hf[0], hk[0]))
    BR.put("profile:busy:" + str(u1), Bool.TRUE)
    hb = hatch(u1, 2)
    pb = place(u1, inv2, EID)
    BR.remove("profile:busy:" + str(u1))
    K.check(hb[0].startswith("-Your profile is still switching") and pb[0].startswith("-Your profile is still switching"), "HATCH / PLACE while the profile switches = refused")
    Hy.CLOCK_OFF = 0
    # ---------------------------------------------------------------- RELOG mid-wait: the record released, the clock runs on while offline
    u3, k3, r3 = mk(703)
    E3 = "Skyy_PetEgg_Farming_Common"      # 120 s
    inv3 = Inv({E3: 1})
    pr3 = place(u3, inv3, E3)
    settle(u3, r3, inv3)
    Hy.CLOCK_OFF = 60 * 1000
    left1 = int(Hy.left(Hy.line(r3, 1), Hy.now()))
    Store.KEYOF.remove(u3)
    Store.release(k3)
    Store.REC.remove(k3)
    Hy.CLOCK_OFF = 125 * 1000                # logged out for a while
    Store.KEYOF.put(u3, k3)
    r3b = Store.get(k3)
    ln = Hy.line(r3b, 1)
    K.check(pr3[0].startswith("+") and 55000 <= left1 <= 61000 and ln is not None and str(ln[2]) == pr3[1] and bool(Hy.ready(ln, Hy.now())),
            "RELOG the slot survives a logout (read back from the file); the wait counts on while offline (60 s left -> ready after 65 s away)")
    hr3 = hatch(u3, 1, pr3[1])
    K.check(hr3[0].startswith("+You hatched") and r3b.get("hatchery.1") is None, "RELOG ... hatched after the relog: %s" % hr3[0])
    Hy.CLOCK_OFF = 0
    # ---------------------------------------------------------------- TAKE OUT
    u4, k4, r4 = mk(704)
    E4 = "Skyy_PetEgg_Combat_Epic"
    inv4 = Inv({E4: 2})
    p4 = place(u4, inv4, E4)
    settle(u4, r4, inv4)
    t1 = takeout(u4, inv4, 1, p4[1])
    f = fileof(k4)
    K.check(t1[0].startswith("+The Epic Combat Egg is back in your inventory (its hatch timer is lost)") and inv4.count(E4) == 2 and "hatchery.1" not in f
            and f.get("eggcredit." + t1[1], "").startswith(E4 + "|1|"), "TAKE OUT the egg back (1 -> 2), the slot empty + a credit in ONE save: %s" % t1[0])
    K.check(any(("egg-remove-intent %s" % t1[1]) in l for l in ledger(mods)) and any(("egg-remove-done %s" % t1[1]) in l for l in ledger(mods)), "TAKE OUT the ledger: intent + done")
    Egg.DONE.put(t1[1], Long(now()))
    Hy.credits(u4, r4, proxy_inv(inv4), now())
    K.check(r4.get("eggcredit." + t1[1]) is None and "eggcredit." + t1[1] not in fileof(k4), "TAKE OUT the forced player save finished = the credit cleared")
    p4b = place(u4, inv4, E4)
    settle(u4, r4, inv4)
    inv4.cap = sum(inv4.live.values())
    t2 = takeout(u4, inv4, 1, p4b[1])
    inv4.cap = None
    K.check(t2[0].startswith("-No room in your inventory") and r4.get("hatchery.1") is not None and inv4.count(E4) == 1, "TAKE OUT no room = refused, the egg stays in its slot: %s" % t2[0])
    t3 = takeout(u4, inv4, 1, "nope")
    K.check(t3[0].startswith("=That slot changed"), "TAKE OUT a stale page (another egg now) = asked again")
    # critic fix 3: the egg leaves the inventory while the credit is open -> a forced save at once + "fell"; after a stop it is never re-given
    u9, k9, r9 = mk(709)
    E9 = "Skyy_PetEgg_Farming_Rare"
    inv9 = Inv({E9: 1})
    p9 = place(u9, inv9, E9)
    settle(u9, r9, inv9)
    t9 = takeout(u9, inv9, 1, p9[1])
    Hy.credits(u9, r9, proxy_inv(inv9), now())
    inv9.takeN(E9, 1)                      # dropped / stashed / sold
    Egg.FORCE.clear()
    Hy.credits(u9, r9, proxy_inv(inv9), now())
    K.check(str(Egg.FORCE.get(t9[1])) == k9 and fileof(k9).get("eggcredit." + t9[1], "").endswith("|fell"),
            "CREDIT (critic fix 3) the egg count fell while the credit is open: a forced save at once + the line says fell")
    Store.REC.clear()
    Egg.SESSION.clear(); Egg.DONE.clear(); Egg.FORCE.clear()
    Store.scanAll()
    inv9.restart()                         # the player file from before the take-out: 0 eggs = the count before
    Store.KEYOF.put(u9, k9)
    r9 = Store.get(k9)
    Hy.credits(u9, r9, proxy_inv(inv9), now())
    K.check(inv9.count(E9) == 0 and r9.get("eggcredit." + t9[1]) is None, "CREDIT ... a stop before that save: the fallen egg is NOT given again (never-dupe)")
    # critic fix 4: a skipped forced save = no blind 30 s clear; the logout hands it to the next join's count reconcile
    inv9.give(E9, 1)
    inv9.psave()
    p10 = place(u9, inv9, E9)
    Egg.NOFORCE.put(p10[1], Bool.TRUE)
    Egg.debts(u9, r9, proxy_inv(inv9), now() + 31000)
    held = r9.get("eggdebt." + p10[1]) is not None
    Hy.forget(u9)
    inv9.psave()                           # the disconnect save
    Egg.debts(u9, r9, proxy_inv(inv9), now())
    K.check(held and r9.get("eggdebt." + p10[1]) is None and inv9.count(E9) == 0 and r9.get("hatchery.1") is not None and not Egg.NOFORCE.containsKey(p10[1]),
            "DEBT (critic fix 4) no forced save: still open after 30 s; after the logout save the join reconciles it by counts (cleared, nothing taken twice)")
    # ---------------------------------------------------------------- VOID: an egg that came from the Void, reconciled against the Void count
    u5, k5, r5 = mk(705)
    E5 = "Skyy_PetEgg_Foraging_Uncommon"
    V.live = {E5: 2}
    V.save()
    inv5 = Inv({})
    inv5.psave()
    p5 = place(u5, inv5, E5)
    f = fileof(k5)
    K.check(p5[0].startswith("+") and p5[2] == "void" and V.live[E5] == 1 and V.owed.get(E5) == 0 and f.get("eggdebt." + p5[1], "").endswith("|void")
            and f.get("hatchery.1", "").endswith("|void"), "VOID no egg in the inventory = taken from the Void (committed after the save), the debt says void")
    # a stop before the pool file was saved: the Void egg came back -> taken again at the join
    Store.REC.clear()
    Egg.SESSION.clear(); Egg.DONE.clear()
    Store.scanAll()
    V.restart()
    Store.KEYOF.put(u5, k5)
    r5 = Store.get(k5)
    Egg.debts(u5, r5, proxy_inv(inv5), now())
    K.check(V.live[E5] == 1 and r5.get("hatchery.1") is not None and any("hatch-reconcile %s" % p5[1] in l for l in ledger(mods)),
            "VOID a stop before the Void was saved: the egg came back in the Void -> taken again (1 Void + 1 in the slot = the 2 before)")
    V.save()
    Egg.DONE.put(p5[1], Long(now()))
    Egg.debts(u5, r5, proxy_inv(inv5), now())
    K.check(r5.get("eggdebt." + p5[1]) is not None, "VOID a player save does not settle a Void debt (it waits 30 s)")
    Egg.debts(u5, r5, proxy_inv(inv5), now() + 31000)
    K.check(r5.get("eggdebt." + p5[1]) is None and V.live[E5] == 1, "VOID ... 30 s later it clears")
    # ---------------------------------------------------------------- FUSE PETS (the 0.3.0 fuse, Hatchery cells)
    u6, k6, r6 = mk(706)
    for _ in range(4):
        Ops.createR(r6, None, "Rabbit", 1, 5, 0, 0, "test", "harness", False)
    for _ in range(4):
        Ops.createR(r6, None, "Goat", 5, 5, 0, 0, "test", "harness", False)
    Ops.createR(r6, None, "Dog", 1, 1, 0, 0, "test", "harness", False)
    g = [str(x) for x in Hy.fuseGroups(r6)]
    K.check(len(g) == 2 and str(r6.kindOf(g[0])) == "Goat" and str(r6.kindOf(g[1])) == "Rabbit", "FUSE PETS one cell per kind + rarity you own 2+ of, rarest first: %s" % [str(r6.kindOf(x)) for x in g])
    ask = str(Ops.fuseAsk(u6, g[1], -1))
    fz = str(Ops.fuse(u6, g[1], 1, str(Ops.fodderKey(r6, g[1])), "harness", -1))
    gz = str(Ops.fuseWhy(r6, g[0]))
    K.check(ask.startswith("=Fuse 4") and fz.startswith("+Fused 4") and int(r6.rarityOf(g[1])) == 2 and int(r6.count()) == 6 and "fusing stops at Legendary" in gz,
            "FUSE PETS 4 Common Rabbits -> 1 Uncommon; 4 Legendary Goats cannot fuse (Mythic only from eggs): %s | %s" % (fz, gz))
    # ---------------------------------------------------------------- FUSE EGGS
    u7, k7, r7 = mk(707)
    E7 = "Skyy_PetEgg_Exploration_Common"
    N7 = "Skyy_PetEgg_Exploration_Uncommon"
    inv7 = Inv({E7: 5})
    a7 = str(Hy.efuseAsk(u7, proxy_inv(inv7), E7))
    z7 = efuse(u7, inv7, E7)
    K.check(a7.startswith("=Fuse 4 Common Exploration Eggs into 1 Uncommon Exploration Egg") and z7.startswith("+Fused 4") and inv7.count(E7) == 1 and inv7.count(N7) == 1,
            "FUSE EGGS 4 Common -> 1 Uncommon (5 -> 1 + 1): %s" % z7)
    z8 = efuse(u7, inv7, E7)
    inv7l = Inv({"Skyy_PetEgg_Exploration_Legendary": 4})
    z9 = efuse(u7, inv7l, "Skyy_PetEgg_Exploration_Legendary")
    inv7f = Inv({E7: 4}, refuse=[N7])
    z10 = efuse(u7, inv7f, E7)
    Cfg.EFUSE_ON = False
    z11 = efuse(u7, Inv({E7: 4}), E7)
    Cfg.EFUSE_ON = True
    K.check(z8.startswith("-You need 4") and "stops at Legendary" in z9 and z10.startswith("-No room") and inv7f.live == {E7: 4} and z11.startswith("-Egg fusing is switched off"),
            "FUSE EGGS too few / Legendary (the top) / no room (all 4 back) / off = refused: %s | %s | %s" % (z8, z9, z10))
    K.check(any("egg-fuse 4 x %s -> 1 %s" % (E7, N7) in l for l in ledger(mods)), "FUSE EGGS a ledger line")

    # ---------------------------------------------------------------- CRASH: a stop after every step of place / take-out / hatch
    def restart(inv):
        Egg.SESSION.clear(); Egg.DONE.clear(); Egg.ANIM.clear(); Egg.HATCHING.clear(); Egg.CLICK.clear(); Egg.FORCE.clear(); Egg.RISE.clear()
        Hy.CLICK.clear(); Hy.NOTIFIED.clear()
        Egg.FAULT = 0
        Store.REC.clear()
        Store.INDEX.clear()
        Store.scanAll()
        a = [int(x) for x in Egg.recover()]
        b = [int(x) for x in Hy.recover()]
        if inv is not None:
            inv.restart()
        return a, b

    def join(u, k, inv):
        Store.KEYOF.put(u, k)
        r = Store.get(k)
        Egg.debts(u, r, proxy_inv(inv), now())
        Hy.credits(u, r, proxy_inv(inv), now())
        Hy.checks(u, r, proxy_inv(inv))
        return r

    def total(k, inv, egg):
        f = fileof(k)
        slots = sum(1 for kk, v in f.items() if kk.startswith("hatchery.") and v.startswith(egg + "|"))
        pets = sum(1 for kk, v in f.items() if kk.endswith(".src") and v.startswith("egg:%s:" % egg))
        return inv.count(egg) + slots + pets

    def open_left():
        L = ledger(mods)
        ints = set(re.search(r"(egg-place-intent|egg-remove-intent|hatch-intent) (\w+)", l).group(2) for l in L if re.search(r"(egg-place-intent|egg-remove-intent|hatch-intent) \w+", l))
        closed = {}
        for l in L:
            mm = re.search(r"(egg-place-done|egg-place-abort|egg-remove-done|egg-remove-abort|hatch-done|hatch-abort) (\w+)", l)
            if mm:
                closed[mm.group(2)] = closed.get(mm.group(2), 0) + 1
        return sorted(h for h in ints if closed.get(h, 0) != 1)

    EK = "Skyy_PetEgg_Mining_Epic"
    bad = []
    for kind_, steps in (("place", (11, 12, 13, 14)), ("remove", (21, 22, 23, 24)), ("hatch", (31, 32, 33))):
        for st_ in steps:
            for psaved in (False, True):     # critic fix 2: an autosave between ANY two steps (then the stop)
                u, k, r = mk(800 + st_ * 2 + (1 if psaved else 0))
                inv = Inv({EK: 3})
                if kind_ != "place":
                    pp = place(u, inv, EK)
                    settle(u, r, inv)
                    if kind_ == "hatch":
                        Hy.CLOCK_OFF = 31 * 60 * 1000
                inv.psave()
                e0 = total(k, inv, EK)
                Egg.FAULT = st_
                threw = False
                try:
                    if kind_ == "place":
                        place(u, inv, EK)
                    elif kind_ == "remove":
                        takeout(u, inv, 1, None)
                    else:
                        hatch(u, 1, None)
                except Exception:
                    threw = True
                Egg.FAULT = 0
                if psaved:
                    inv.psave()            # the player save landed before the stop
                restart(inv)
                r = join(u, k, inv)
                if r.keysWith("eggdebt.").length or r.keysWith("eggcredit.").length:      # a second stop before the player save: still right
                    restart(inv)
                    r = join(u, k, inv)
                    e_mid = total(k, inv, EK)
                    if e_mid != e0:
                        bad.append((kind_, st_, psaved, "second stop", e_mid, e0))
                    settle(u, r, inv)
                Hy.CLOCK_OFF = 0
                e1 = total(k, inv, EK)
                left = [x for x in fileof(k) if x.startswith(("eggdebt.", "eggcredit.", "eggcheck."))]
                if not threw or e1 != e0 or left:
                    bad.append((kind_, st_, psaved, threw, e1, e0, left))
    K.check(not bad, "CRASH a stop after every step of place (11-14) / take-out (21-24) / hatch (31-33), with and without an autosave before it: eggs in the "
                     "inventory + the slots + hatched pets never change, no debt / credit left: %s" % bad[:3])
    ol = open_left()
    K.check(not ol, "CRASH every intent (place / take-out / hatch) closed exactly once: %s" % ol[:4])
    K.check(any("egg-check-return" in l for l in ledger(mods)) and any("egg-check-take" in l for l in ledger(mods)),
            "CRASH (critic fix 2) an autosave inside a cut-off place / take-out is caught at the join: egg-check-return / egg-check-take")
    a_, b_ = restart(None)
    K.check(a_ == [0, 0, 0] and b_ == [0, 0, 0], "CRASH a second start finds nothing open")
    # a lost take-out credit: the slot emptied + saved, the player save never came -> the egg given again at the join
    u8, k8, r8 = mk(880)
    inv8 = Inv({EK: 1})
    p8 = place(u8, inv8, EK)
    settle(u8, r8, inv8)
    t8 = takeout(u8, inv8, 1, p8[1])
    restart(inv8)                         # inventory back to the save before the take-out: 0 eggs
    r8 = join(u8, k8, inv8)
    K.check(t8[0].startswith("+") and inv8.count(EK) == 1 and r8.get("hatchery.1") is None and any("egg-credit-return %s" % t8[1] in l for l in ledger(mods)),
            "CRASH a take-out whose player save never came: the egg given again at the join (credit return)")
    settle(u8, r8, inv8)
    K.check(not list(r8.keysWith("eggcredit.")), "CRASH ... and its credit clears after the next player save")
    # ---------------------------------------------------------------- BENCH: no egg recipe in any SET jar
    zj = zipfile.ZipFile(jar)
    ej = [n for n in zj.namelist() if n.startswith("Server/Item/Items/SkyyPets/Skyy_PetEgg_")]
    K.check(len(ej) == 30 and not any("Recipe" in json.loads(zj.read(n).decode("utf-8")) for n in ej), "BENCH the 30 egg items carry no Recipe")
    lang = zj.read("Server/Languages/en-US/server.lang").decode("utf-8")
    K.check("Right-click" not in lang and "Hatch it in the Hatchery (/pets)" in lang and "Craft it in /pets > Eggs." in lang
            and "server.items.Skyy_PetEgg_Mining_Rare.description=Rare Egg - " in lang, "BENCH the flavor: tier tag first, points at the Hatchery / the Eggs tab")
    sys.path.insert(0, TOOLS)
    import deploy_set as DS
    hits = []
    seen = 0
    for mod, ver in DS.SET:
        jp = os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver)) if mod != "SkyyPets" else jar
        if not os.path.isfile(jp):
            continue
        seen += 1
        z = zipfile.ZipFile(jp)
        for n in z.namelist():
            if not n.endswith(".json"):
                continue
            t = z.read(n).decode("utf-8", "ignore")
            if "Skyy_PetEgg" not in t:
                continue
            if mod != "SkyyPets" or "Recipe" in t:
                hits.append("%s:%s" % (mod, n))
    K.check(seen >= 20 and not hits, "BENCH no item / recipe JSON of the %d SET jars crafts a pet egg (only SkyyPets names them, without a Recipe): %s" % (seen, hits[:3]))
    K.save()


# ======================================================================================================== STAGE
def run_stage(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JShort, JByte
    import hub_tab_kit as HT
    import skyyui as SUI
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Egg, Page, HPage, Reel, Hy, Eng = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetEgg"), P_("PetsPage"),
                                                            P_("PetHatchPage"), P_("PetReel"), P_("PetHatchery"), P_("PetsEng"))
    Paths, UUID, IS = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "stage-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    K.eq(str(P_("PetsHubOpen").register()), "character:pets", "the Pets hub tab is registered")
    Hy.OPENER = P_("PetHatchOpen")()
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000611"), "Keeper")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "123")
    for _ in range(4):
        Ops.createR(r1, None, "Rabbit", 1, 3, 0, 0, "test", "harness", False)
    told = []
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: _uarr(JClass, [str(u1)]), "byName": lambda n: u1, "nameOf": lambda u: "Keeper",
                                            "tell": lambda u, t, c: told.append(str(t))})

    def click(page, P, a, i=None, extra=None, tok=True):
        Hy.CLICK.clear()
        d = '{"a":"%s"' % a + (',"i":"%s"' % i if i is not None else "") + (',"t":"%s"' % page.tok if tok else "") + (extra or "") + "}"
        page.handleDataEvent(P.ref, P.st, d)
        E.pump(P)
        return str(page.info)

    pg = Page(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, pg)
    E.pump(P1)
    built = HT.build(pg, P1)
    w, h, sets, evs = HT.page_check(K, E, P1, built, "SkyyPt", "character", "pets", "Pets", "TAB0 the Pets tab")
    sel = [s for s, _t in evs]
    K.check(all(("#SkyyPtT%d" % i) in sel for i in range(3)) and "#SkyyPtGrid" in sel and int(Page.PER_PAGE) == 60,
            "TAB0 the three tabs are bound, the pets grid keeps 12 x 5 = 60 (%d)" % int(Page.PER_PAGE))
    tb = [t for ty, s_, t, d in built[0] if t and "TextButton #SkyyPtT" in t]
    K.check(len(tb) == 3 and "Primary" in tb[0] and "Primary" not in tb[1] and 'Text: "Hatchery"' in tb[2], "TAB0 the tab row: Pets selected (Primary), Eggs, Hatchery")
    click(pg, P1, "tab", 1, tok=False)
    built1 = HT.build(pg, P1)
    w1, h1, sets1, evs1 = HT.page_check(K, E, P1, built1, "SkyyPt", "character", "pets", "Pets", "TAB1 the Eggs tab")
    K.check(int(pg.tab) == 1 and "#SkyyPtGrid" not in [s for s, _t in evs1] and "Craft a pet egg" in str(sets1.get("#SkyyPtEggH.Text"))
            and "Common Combat Egg" in str(sets1.get("#SkyyPtE0Nm.Text")) and "Uncommon Mining Egg" in str(sets1.get("#SkyyPtE9Nm.Text"))
            and "#SkyyPtE10Nm.Text" not in sets1,
            "TAB1 Eggs: 10 rows, tier then name (Common Combat first, Uncommon Mining last): %s / %s" % (sets1.get("#SkyyPtE0Nm.Text"), sets1.get("#SkyyPtE9Nm.Text")))
    K.check(not any(s.startswith("#SkyyPtE") and s.endswith("Act") for s, _t in evs1) and "Missing" in str(sets1.get("#SkyyPtE0Tg.Text")),
            "TAB1 nothing craftable = no Craft bound, the rows say Missing")
    # materials for a Common Mining egg in the real inventory -> its Craft is bound (the craft itself + its rollback: HATCH - the stage has
    # no item assets, so it could not give the egg nor the materials back)
    st_ = P1.slots["storage"].getInventory()
    st_.addItemStackToSlot(JShort(0), IS("Food_Egg", 2))
    st_.addItemStackToSlot(JShort(1), IS("Skyy_Ench_Cobblestone", 12))
    built1 = HT.build(pg, P1)
    ci = [str(x) for x in Hy.CRAFT].index("Skyy_PetEgg_Mining_Common")
    sets1 = dict((s_, d) for ty, s_, t, d in built1[0] if ty == "Set")
    K.check(("#SkyyPtE%dAct" % ci) in [s for s, _t in built1[1]] and "Ready" in str(sets1.get("#SkyyPtE%dTg.Text" % ci))
            and "12 Enchanted Cobblestone (12)" in str(sets1.get("#SkyyPtE%dSb.Text" % ci)),
            "TAB1 with the materials in a real inventory: Ready + Craft bound, the cost line counts them: %s" % sets1.get("#SkyyPtE%dSb.Text" % ci))
    iv = P_("PetInvReal").of(P1.st, P1.ref)
    K.check(int(iv.takeN("Skyy_Ench_Cobblestone", 5)) == 5 and int(iv.count("Skyy_Ench_Cobblestone")) == 7 and int(iv.takeN("Skyy_Ench_Cobblestone", 50)) == 7
            and int(iv.count("Skyy_Ench_Cobblestone")) == 0, "INV takeN on a real inventory: exactly n (counted), never more than there is")
    # the Hatchery
    hb = P1.slots["hotbar"].getInventory()
    EID = "Skyy_PetEgg_Combat_Common"
    hb.addItemStackToSlot(JShort(2), IS(EID, 3))
    click(pg, P1, "tab", 2, tok=False)
    built2 = HT.build(pg, P1)
    w2, h2, sets2, evs2 = HT.page_check(K, E, P1, built2, "SkyyPt", "character", "pets", "Pets", "TAB2 the Hatchery tab")
    sel2 = [s for s, _t in evs2]
    K.check("#SkyyPtEg" in sel2 and all(("#SkyyPtX%d" % i) in sel2 for i in range(3)) and "0 / 2 slots in use" in str(sets2.get("#SkyyPtHsH.Text"))
            and "Slot 1 - empty" in str(sets2.get("#SkyyPtH1Nm.Text")) and len(list(pg.eids)) == 1 and str(pg.eids[0]) == EID,
            "TAB2 Hatchery: 2 empty slots, the egg grid holds the egg you carry, the modes bound: %s" % sets2.get("#SkyyPtHsH.Text"))
    g0 = click(pg, P1, "eg", extra=',"SlotIndex":0')
    K.check(g0.startswith("+Common Combat Egg is in Hatchery slot 1") and int(iv.count(EID)) == 2 and r1.get("hatchery.1") is not None,
            "TAB2 a grid click puts the egg in slot 1 (taken from the real inventory, counted): %s" % g0)
    built2 = HT.build(pg, P1)
    s2 = dict((s_, d) for ty, s_, t, d in built2[0] if ty == "Set")
    K.check("Hatching - 2m 00s left" in str(s2.get("#SkyyPtH1Sb.Text")) or "Hatching - 1m 5" in str(s2.get("#SkyyPtH1Sb.Text")), "TAB2 slot 1: hatching, the time left: %s" % s2.get("#SkyyPtH1Sb.Text"))
    K.check(len(list(Egg.NOFORCE.keySet())) >= 1, "TAB2 (critic fix 4) the stage has no forced save: the place's debt is marked NOFORCE (no blind 30 s clear)")
    Egg.NOFORCE.clear()                    # (as if the player's own save landed)
    Egg.debts(u1, r1, iv, int(JClass("java.lang.System").currentTimeMillis()) + 31000)
    o1 = click(pg, P1, "slot", 1, extra=',"m":"o"')
    K.check(o1.startswith("=Take the Common Combat Egg out of slot 1? Its hatch timer is lost"), "TAB2 Take out press 1 asks: %s" % o1)
    o2 = click(pg, P1, "slot", 1, extra=',"m":"o"')
    K.check(o2.startswith("-No room in your inventory") and r1.get("hatchery.1") is not None, "TAB2 Take out press 2 (the stage cannot give items): refused, the egg stays: %s" % o2)
    Hy.CLOCK_OFF = 3 * 60 * 1000
    HT.build(pg, P1)
    n0 = int(r1.count())
    o4 = click(pg, P1, "slot", 1, extra=',"m":"o"')
    K.check(o4.startswith("=Take the") and r1.get("hatchery.1") is not None and int(r1.count()) == n0,
            "TAB2 (critic fix 5) a stale Take out on a slot that turned READY only asks to take it out - it never hatches: %s" % o4)
    pg.confirm = ""
    o3 = click(pg, P1, "slot", 1, extra=',"m":"h"')
    cur = E.pg(P1)
    K.check(int(r1.count()) == n0 + 1 and r1.get("hatchery.1") is None and cur is not None and str(cur.getClass().getName()) == PKG + "PetHatchPage" and int(cur.view) in (1, 2),
            "TAB2 READY + Hatch: the pet saved FIRST, then the reel page opens on top (view %s)" % (cur.view if cur is not None else None))
    Hy.CLOCK_OFF = 0
    told.clear()
    frames = 0
    for _ in range(80):
        if int(cur.view) != 1:
            break
        cur.tick(Reel(cur, cur.gen, 0))
        frames += 1
        E.pump(P1)
    K.check(int(cur.view) == 2 and frames >= 20 and len([t for t in told if "You hatched a" in t]) == 1, "HPAGE the two reels run to the result + ONE reveal line (%d steps)" % frames)
    cm, ev = HT.build(cur, P1)
    ab = [t for ty, s_, t, d in cm if t and "TextButton #SkyyHtAgain" in t]
    K.check("#SkyyHtAgain" in [s for s, _t in ev] and ab and 'Text: "Hatchery"' in ab[0] and "#SkyyHtGo" not in [s for s, _t in ev], "HPAGE the result: a Hatchery button (no Hatch another)")
    cur.handleDataEvent(P1.ref, P1.st, '{"a":"hatchery"}')
    E.pump(P1)
    back = E.pg(P1)
    K.check(back is not None and str(back.getClass().getName()) == PKG + "PetsPage" and int(back.tab) == 2, "HPAGE Hatchery opens the Pets page on its Hatchery tab")
    # the hand-held hatch is gone: the hatch page's Hatch refuses
    hp = HPage(P1.pr)
    hb.addItemStackToSlot(JShort(0), IS(EID, 1))
    try:
        hb.setActiveSlot(JByte(0))
    except Exception:
        pass
    P1.pm.openCustomPage(P1.ref, P1.st, hp)
    E.pump(P1)
    HT.build(hp, P1)
    c0 = int(r1.count())
    hp.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % hp.tok)
    E.pump(P1)
    K.check(int(r1.count()) == c0 and "Hatchery" in str(hp.info), "RIGHT the hatch page's own Hatch (an egg in hand) hatches nothing: %s" % hp.info)
    rc0 = int(Hy.RIGHT.get())
    K.check(P_("PetHatchFactory")().apply(P1.pr) is None and int(Hy.RIGHT.get()) == rc0 + 1, "RIGHT the egg's right-click: no page (null), one line to the player")
    # the fuse modes
    pg2 = back
    click(pg2, P1, "emode", 2, tok=False)
    HT.build(pg2, P1)
    K.check(len(list(pg2.eids)) == 1 and str(r1.kindOf(pg2.eids[0])) == "Rabbit", "TAB2 Fuse pets: one cell (4 Common Rabbits)")
    f1 = click(pg2, P1, "eg", extra=',"SlotIndex":0')
    HT.build(pg2, P1)
    f2 = click(pg2, P1, "eg", extra=',"SlotIndex":0')
    K.check(f1.startswith("=Fuse 4") and f2.startswith("+Fused 4"), "TAB2 Fuse pets: press 1 asks, press 2 fuses: %s" % f2)
    click(pg2, P1, "emode", 1, tok=False)
    HT.build(pg2, P1)
    e1 = click(pg2, P1, "eg", extra=',"SlotIndex":0')
    K.check(e1.startswith("-You need 4") , "TAB2 Fuse eggs with 3: refused: %s" % e1)
    n_ = len(E.sent(P1))
    click(pg2, P1, "close", tok=False)
    K.check(len(E.sent(P1)) > n_ and E.pg(P1) is None, "TAB2 Close: one update empties the Hatchery grid first, then the page closes")
    K.save()


# ======================================================================================================== LIVE: start twice on a copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, Log, Egg, Hy = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsLog"), P_("PetEgg"), P_("PetHatchery")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = tree(home)

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return ([int(x) for x in Store.scanAll()], [int(x) for x in Store.fuseRecover()], [int(x) for x in Egg.recover()], [int(x) for x in Hy.recover()])
    sc1, fr1, hr1, hq1 = start()
    t1 = tree(home)
    ch = sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))
    K.check(not ch, "LIVE start 1 writes nothing (no config migration in 0.4.1): %s" % ch)
    K.check(sc1[2] == 0 and sc1[3] == 0 and fr1[0] == 0 and hr1[0] == 0 and hq1[0] == 0, "LIVE every pet file read %s, no cut-off fuse / hatch / egg move" % sc1)
    sc2, fr2, hr2, hq2 = start()
    K.check(tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes NOTHING")
    K.save()


# ======================================================================================================== R040: the 0.4.0 harness on this jar
_HAND = "0.4.1: eggs hatch only in the Hatchery (Skyy: \"hatchery only\") - the hatch page's own Hatch refuses; STAGE / HATCH re-check the reel page via the Hatchery"
_TABS = "0.4.1: the tab row took the \"Your slots\" header's place (STAGE TAB0 checks the page)"
EXPECTED_R040 = {
    "HATCH Hatch: the pet is saved BEFORE any frame": _HAND, "HATCH the reels did not start": _HAND, "HATCH the reels:": _HAND,
    "HATCH the result = ONE reveal line": _HAND, "HATCH ~25 frame updates": _HAND, "HATCH view 2:": _HAND, "HATCH reel 1 stops": _HAND,
    "HATCH reel 2 stops": _HAND, "HATCH Skip mid-reel": _HAND, "HATCH Esc mid-reel": _HAND, "HATCH a player who left mid-reel": _HAND,
    "HATCH ... and comes as ONE line": _HAND, "HATCH skip animation on": _HAND, "HATCH pets.hatch.anim quick": _HAND,
    "HATCH every debt cleared after 30 s": _HAND, "HATCH view 0: the egg, its pet odds": "0.4.1: the hatch page's Hatch is never bound (canGo false)",
    "STATIC Hatch = PetEgg.hatch": "0.4.1: PetHatchPage.go no longer calls PetEgg.hatch (PetHatchery.hatch + begin() do)",
    "HATCH Open pets opens the Pets page on top": _HAND,
    "PAGE the head:": _TABS,
    "STOP at the 0.4.0 hand-held hatch reels": _HAND,
    "HATCH view 1: two reels of 5 cells": _HAND,
}


def run_old(out, jar, scratch, _home, script, phases, expected):
    K = HK.Child(out)
    for ph in phases:
        d = os.path.join(scratch, "%s-%s" % (os.path.basename(script)[:-3], ph))
        os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
        o = os.path.join(d, "out.json")
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(d, "tmp")
        p = subprocess.run([sys.executable, script, "--phase", ph, "--out", o, "--dir", d, "--jar", jar], env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        open(os.path.join(scratch, "%s-%s.log" % (os.path.basename(script)[:-3], ph)), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
        if not os.path.isfile(o):
            K.check(False, "%s %s: the phase wrote no result (exit %s): %s" % (os.path.basename(script), ph, p.returncode, (p.stdout + p.stderr)[-800:]))
            continue
        d_ = json.load(open(o))
        unexp = [f for f in d_["fails"] if not any(f.startswith(e) for e in expected)]
        seen = [e for e in expected if any(f.startswith(e) for f in d_["fails"])]
        K.check(not unexp, "%s %s on the 0.4.1 jar: %d ok, unexpected fails %s" % (os.path.basename(script), ph, d_["ok"], unexp[:4]))
        for e in seen:
            K.notes.append("expected on 0.4.1: %s -> %s" % (e[:90], expected[e]))
        print("%s %s: %d ok, %d fail(s), %d of them expected" % (os.path.basename(script), ph, d_["ok"], len(d_["fails"]), len(d_["fails"]) - len(unexp)))
    K.save()


def run_oldstage(out, jar, scratch, home):
    """the 0.4.0 STAGE phase on this jar; it stops at the hand-held hatch reels (gone in 0.4.1) - every check made before is kept"""
    import importlib.util, traceback
    spec = importlib.util.spec_from_file_location("test_skyypets_040", os.path.join(HERE, "test_skyypets_0.4.0.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    made = []
    orig = HK.Child.__init__

    def init(self, o):
        orig(self, o)
        made.append(self)
    HK.Child.__init__ = init
    try:
        mod.run_stage(out, jar, scratch, home)
    except Exception:
        tb = traceback.format_exc()
        K = made[-1]
        K.fails.append("STOP at the 0.4.0 hand-held hatch reels: " + tb.strip().splitlines()[-1][:160] + " | " + [l for l in tb.splitlines() if "test_skyypets_0.4.0.py" in l][-1].strip())
        K.save()
    finally:
        HK.Child.__init__ = orig


def run_r040(out, jar, scratch, home):
    run_old(out, jar, scratch, home, os.path.join(HERE, "test_skyypets_0.4.0.py"), ("egg",), EXPECTED_R040)
    o2 = out + ".stage.json"
    run_old(o2, jar, scratch, home, os.path.abspath(__file__), ("oldstage",), EXPECTED_R040)
    a, b = json.load(open(out)), json.load(open(o2))
    a["ok"] += b["ok"]
    a["fails"] += b["fails"]
    a["notes"] += b["notes"]
    json.dump(a, open(out, "w"), indent=1)


# ---- C: the non-class entries that may change: manifest + the 30 egg item JSON (no Recipe) + the lang file (the flavor); none removed
_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    orig_eq = HK.Child.eq

    def eq(self, got, want, what):
        if what != "C: non-class entries changed":
            return orig_eq(self, got, want, what)
        za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
        gone = sorted(n for n in za.namelist() if n not in zb.namelist())
        eggs = [n for n in got if n.startswith("Server/Item/Items/SkyyPets/Skyy_PetEgg_")]
        ok = all(n in ("manifest.json", "Server/Languages/en-US/server.lang") or n in eggs for n in got)
        return self.check(ok and not gone and sorted(eggs) == sorted("Server/Item/Items/SkyyPets/%s.json" % EG.egg_id(c, r) for c, r in EG.RECIPES) and "manifest.json" in got and "Server/Languages/en-US/server.lang" in got,
                          "C: non-class entries changed = manifest + the 10 craftable egg item JSON (their Recipe gone) + the lang file; none removed (%d changed: %s)" % (len(got), [n for n in got if n not in eggs][:6]))
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = orig_eq


HK.run_compare = _compare

if __name__ == "__main__":
    phases = [("hatch", run_hatch), ("stage", run_stage), ("live", run_live)]
    if HK.arg("--phase") == "oldstage":
        phases.append(("oldstage", run_oldstage))      # only as R040's child (never a top-level phase of its own)
    if "--no-old" not in sys.argv:
        phases += [("r040", run_r040)]
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE, "Skyy_SkyyPets"))
