"""Harness for SkyyPets 0.4.0 (PET EGGS + HATCHING, research/Pet-Eggs-Spec.md round R1, + the Pets page redesign; tools/pets_0_4_0_patch.py,
the egg table tools/skyyeggs.py).
Build first: python tools/pets_0_4_0_patch.py; python SkyyPets/build_skyypets_0.4.0.py

    python SkyyPets/test_skyypets_0.4.0.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--no-old]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.3.1 -> 0.4.0 (exactly the planned members;
              + the 11 egg / hatch classes; non-class entries = manifest + the egg assets + the lang file only), engine-access audit
  EGG         EXECUTED in a plain -Xverify:all JVM (a fake PetInv = one player's inventory with a "saved" copy = the player file):
              DATA   30 ids / names / defs, 31 portraits, 6 tokens, every Server Setup row default = tools/skyyeggs.py
              W      the weights for n = 1..20 x 6 rarities = skyyeggs.weights (Python); the top-half rule (a Legendary / Mythic egg never
                     gives a bottom-half pet); the rarity rows; 100,000 SEEDED rolls per egg rarity (roll 1 on the 14-pet Combat list and
                     the 4-pet Mining list, roll 2) within 0.5 % of the spec tables; /petadmin hatchodds for all 30 eggs within 0.5 %
              CHK    the row checks (Legendary / Mythic never C / U, six numbers, unknown kinds, duplicates, -), a hand-edited Legendary
                     row with a Common weight is still never below Rare, order(): unknown / switched-off kinds out, a kind in no list
                     placed by its start rarity, - = none
              HATCH  the happy path (egg -1 counted, one pet Lv 1 src egg:<egg>:<hid>, ONE save holding pet + debt + reveal line, the
                     ledger intent / pet / done), every gate (not held, pets off, eggs off, busy, a full collection, no kind can hatch,
                     a double click, a second hatch at the same time), a slot that gives 0 / 2 eggs (abort take, the extra put back), a
                     failed save (the egg back, save-refund), a failed save + a full inventory (refund-failed + a warning)
              CRASH  a simulated server stop after EVERY step (1 intent, 2 egg taken, 3 debt set, 4 saved, 5 done) and in the createR
                     rename -> ledger gap, + the player-save timing: restart = REC cleared + scanAll + recover + the join reconcile:
                     eggs + hatched pets == the eggs before, never both, never neither; every intent closed once
              DEBT   in-session debts wait for the forced save (DONE) or 30 s; an old debt with the egg back = taken (reconcile), gone =
                     cleared; an unreadable debt line; the reveal line once (not while the reel runs), the Legendary announce
              MYTH   a Mythic pet through roll 2, the buffs (x1.5), the caps, fusing refuses it, its name
              FUZZ   300 random steps (hatch / crash at a random step / player save / restart / reconcile / in-session clear): the egg +
                     pet total never changes, no pet id twice, every debt resolved
              DROP   pets:fn:eggroll: 1 in N, the Fortune luck, pets:luck, the cap per hour, the rarity bands by tier, every refusal,
                     the Exploration roll from pets:fn:onxp; /petadmin egg refusals
              REC    the startup recovery on synthetic ledgers (open intent + debt line = done, + pet src = done, none = abort, a
                     second start writes nothing)
  STAGE       EXECUTED in the hub stage (tools/hub_tab_kit.py: the REAL PageManager, Universe, component stores, REAL inventories):
              the Pets page (hub page_check, the grid of portraits, the flavor text with every spec, the filters, every click mode,
              the slot rows' Take out, a stale token, an empty slot, the starter view still there, the grid cleared before it
              closes); PetInvReal on a real inventory (held / count / takeOne / takeAny / give storage first); the HATCH PAGE: view 0
              markup + odds, Hatch -> the reels driven frame by frame (25 updates, the result, ONE reveal line), Skip, Esc, the skip
              toggle, quick mode, Open pets, a stale page; PetEggGive into a real inventory (and a full one)
  LIVE        START TWICE on a scratch COPY of the live Skyy_SkyyPets folder: nothing written by start 1 or 2 (no config migration in
              0.4.0), every pet file read, no cut-off hatch / fuse
  R031        the 0.3.1 harness's SYS phase EXECUTED on the 0.4.0 jar (kind values, buffs, the 0.3.1 config update)
  R030        the 0.3.0 harness's SYS / SND phases EXECUTED on the 0.4.0 jar: the whole pet system (starter, buffs, XP, rebirth, fusing
              + fuzz, level update, config update, sounds) unchanged; its checks of the removed Open page (detail view, B5 / B6) are the
              listed EXPECTED_R030 differences, each with its reason
Exit code 1 on any failure.
"""
import os, sys, subprocess, json, shutil, zipfile, re, random, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyeggs as EG

VERSION = "0.4.0"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.3.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pets040", "test")))
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
# class compare 0.3.1 -> 0.4.0: exactly these members differ (+ the 11 added classes)
_CFG_F = ["ANNOUNCE", "DROP_CAP", "DROP_COMBAT", "DROP_EXPLORATION", "DROP_FARMING", "DROP_FCAP", "DROP_FISHING", "DROP_FORAGING", "DROP_FPCT",
          "DROP_HIGH", "DROP_HTIER", "DROP_LOW", "DROP_MINING", "DROP_ON", "DROP_W_DEF", "EGG_ON", "EGG_O_COMBAT", "EGG_O_EXPLORATION",
          "EGG_O_FARMING", "EGG_O_FORAGING", "EGG_O_MINING"] + ["EGG_%s%d" % (x, i) for x in "PRW" for i in range(1, 7)] + [
          "EGG_W_DEF", "FORCE_SAVE", "HATCH_ANIM", "REEL_FRAMES", "REEL_S", "SND_REEL", "SND_REEL_ID", "SND_REVEAL", "SND_REVEAL_ID"]
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],      # the kit: the new rows + the 0.4.0 header
    "PetAdminArg1Cmd": ["~c "], "PetAdminArg2Cmd": ["~c "], "PetAdminArg3Cmd": ["~c "], "PetAdminArg4Cmd": ["~c "], "PetAdminArg5Cmd": ["~c "],
    "PetAdminCmd": ["~c "],                   # the usage texts (+ egg, hatchodds)
    "PetCmds": ["~m run"],                    # PetEgg.admin first
    "PetOps": ["~m admin"],                   # the help line + "Mythic comes from eggs"
    "PetRec": ["+m keysWith"],
    "PetTick": ["~m leave"], "PetTickSys": ["~m tick"],      # PetEgg.forget / PetEgg.tickPlayer
    "PetXpFn": ["~m apply"],                  # the Exploration egg roll
    "PetsCfg": sorted(["+f " + f for f in _CFG_F] + ["+m checkDropW", "+m checkEggOrder", "+m checkEggW", "+m dropN", "+m dropW", "+m eggHalf",
                                                      "+m eggOrder", "+m eggRarity", "+m eggRatio", "+m eggW", "~<clinit>", "~m applyAll",
                                                      "~m applyScalars", "~m seed"]),
    "PetsPage": ["+f AREA_SKILLS", "+f MODES", "+f cells", "+f fArea", "+f fRole", "+f mode", "+m act", "+m areaOk", "+m before", "+m buffsAt",
                 "+m cell", "+m clearGrid", "+m hint", "+m jsonInt", "+m modeHint", "+m roleOk", "+m shown", "+m tip", "~<clinit>", "~c ",
                 "~m build", "~m handleDataEvent", "~m iconOf", "+f shownN", "+f PAGE_UPDATES", "+m fillGrid", "+m turnPage"],
    "SkyyPetsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["PetEggDefs", "PetInv", "PetInvReal", "PetEgg", "PetEggGive", "PetSaveDone", "PetEggSave", "PetEggRollFn", "PetHatchPage",
         "PetReel", "PetHatchFactory", "PetEggDefsFn"]


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
    """a pet file (Properties.store output: one line per entry, escaped) -> {key: value}"""
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
    """one player's inventory: hotbar slot 0 (the held egg) + the rest (storage), and 'saved' = what the player file holds"""

    def __init__(self, held=None, n=0, rest=None):
        self.live = {"held": [held, n], "rest": dict(rest or {})}
        self.saved = copy.deepcopy(self.live)
        self.take_mode = "ok"
        self.give_mode = "ok"

    def heldId(self):
        h = self.live["held"]
        return h[0] if h[0] and h[1] > 0 else None

    def heldSlot(self):
        return 0 if self.heldId() else -1

    def heldQty(self):
        h = self.live["held"]
        return h[1] if h[0] else 0

    def count(self, i):
        h = self.live["held"]
        return (h[1] if h[0] == i else 0) + self.live["rest"].get(str(i), 0)

    def takeOne(self, slot, i):
        h = self.live["held"]
        if int(slot) != 0 or h[0] != str(i) or h[1] < 1 or self.take_mode == "zero":
            return 0
        if self.take_mode == "double" and h[1] >= 2:
            h[1] -= 2
            return 2
        h[1] -= 1
        return 1

    def takeAny(self, i):
        i = str(i)
        if self.live["rest"].get(i, 0) > 0:
            self.live["rest"][i] -= 1
            return 1
        h = self.live["held"]
        if h[0] == i and h[1] > 0:
            h[1] -= 1
            return 1
        return 0

    def give(self, i, n):
        if self.give_mode == "full":
            return 0
        self.live["rest"][str(i)] = self.live["rest"].get(str(i), 0) + int(n)
        return int(n)

    def psave(self):
        self.saved = copy.deepcopy(self.live)

    def restart(self):
        self.live = copy.deepcopy(self.saved)


def proxy_inv(inv):
    from jpype import JProxy
    return JProxy(PKG + "PetInv", dict={"heldId": inv.heldId, "heldSlot": inv.heldSlot, "heldQty": inv.heldQty, "count": inv.count,
                                        "takeOne": inv.takeOne, "takeAny": inv.takeAny, "give": inv.give})


# ======================================================================================================== EGG
def run_egg(out, jar, scratch, _home):
    from jpype import JClass, JProxy
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Egg, Defs, Kind, Buff, Eng = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetEgg"), P_("PetEggDefs"),
                                                      P_("PetKind"), P_("PetBuff"), P_("PetsEng"))
    Paths, UUID, Random, Bool = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.util.Random"), JClass("java.lang.Boolean")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "egg-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    home = os.path.join(mods, "Skyy_SkyyPets")
    Store.ROOT = Paths.get(home)
    Store.DIR = Store.ROOT.resolve("pets")
    pdir = os.path.join(home, "pets")
    told = []
    names = {}
    api = JProxy(PKG + "PetsApi", dict={"online": lambda: JClass("java.util.UUID[]")(0) if not names else
                                        _uarr(JClass, list(names)), "byName": lambda n: _by(names, n, UUID),
                                        "nameOf": lambda u: names.get(str(u), str(u)), "tell": lambda u, t, c: told.append((str(u), str(t)))})
    Eng.API = api
    BR = Log.bridge()
    # ---------------------------------------------------------------- ASSET: the round egg model (Skyy 2026-10-16 "make the held item ... look more round")
    zj = zipfile.ZipFile(jar)
    nm = set(zj.namelist())
    mdl = json.loads(zj.read("Common/Items/Pets/Skyy_PetEgg.blockymodel").decode("utf-8"))
    sys.path.insert(0, os.path.join(TOOLS, "art"))
    import pet_egg_model as EGGM
    eg = json.loads(zj.read("Server/Item/Items/SkyyPets/Skyy_PetEgg_Mining_Rare.json").decode("utf-8"))
    K.check(bool(EGGM.check(mdl)) and eg["Model"] == "Items/Pets/Skyy_PetEgg.blockymodel" and eg["Texture"] == "Items/Pets/Skyy_PetEgg_Rare_Round_Texture.png"
            and all(("Common/Items/Pets/Skyy_PetEgg_%s_Round_Texture.png" % r) in nm for r in RAR)
            and not any(n.endswith("_Texture.png") and "Round" not in n and "Skyy_PetEgg" in n for n in nm),
            "ASSET the eggs wear our own round model (6 stacked boxes, the vanilla egg's anchors + outer size) + 6 round textures; the one-box textures are not shipped")
    tus, wart = zj.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_Tusker.png"), zj.read("Common/Icons/ItemsGenerated/Skyy_PetIcon_Warthog.png")
    K.check(tus != wart, "ASSET Tusker and Warthog have different portraits (the Tusker one tinted red)")
    # ---------------------------------------------------------------- DATA
    K.eq([str(x) for x in Defs.IDS], EG.IDS, "DATA the 30 egg ids = skyyeggs")
    K.eq([str(x).split("|ratio=")[0] for x in Defs.DEFS][:2], ["Skyy_PetEgg_Mining_Common|Mining|Common|Common Mining Egg", "Skyy_PetEgg_Mining_Uncommon|Mining|Uncommon|Uncommon Mining Egg"], "DATA pets:egg:defs rows")
    K.check(len(list(Defs.PORTRAITS)) == 31 and str(Defs.portrait("Rabbit")) == "Skyy_PetIcon_Rabbit" and Defs.portrait("Nope") is None
            and [str(x) for x in Defs.TOKENS] == ["Skyy_PetRarity_" + r for r in RAR], "DATA 31 portraits, 6 tokens")
    d0 = str(Defs.DEFS[0])
    K.check(d0 == "Skyy_PetEgg_Mining_Common|Mining|Common|Common Mining Egg|ratio=16|pool=all|rarity=7000/2300/600/90/9/1|order=Goat,Warthog,Meerkat,Mouse"
            and str(Defs.DEFS[4]).endswith("|ratio=2|pool=half|rarity=0/0/6500/2800/600/100|order=Goat,Warthog,Meerkat,Mouse"), "DATA pets:egg:defs = id|cat|rarity|name + the roll weights: %s" % d0)
    Cfg.EGG_W1 = "1/1/1/1/1/1"
    lv = [str(x) for x in P_("PetEggDefsFn")().apply(None)]
    Cfg.EGG_W1 = EG.rarity_text(EG.RARITY_W["Common"])
    K.check(len(lv) == 30 and "|rarity=1/1/1/1/1/1|" in lv[0] and "|rarity=1/1/1/1/1/1|" in lv[6], "DATA pets:fn:eggdefs = the LIVE rows (a changed rarity row shows)")
    K.check(int(Defs.catOfId("Skyy_PetEgg_Combat_Legendary")) == 3 and int(Defs.rarOfId("Skyy_PetEgg_Combat_Legendary")) == 5
            and int(Defs.catOfId("Food_Egg")) == -1 and int(Defs.rarOfId("Skyy_PetEgg_Fishing_Rare")) == 0
            and str(Defs.idOf(4, 6)) == "Skyy_PetEgg_Exploration_Mythic" and Defs.idOf(5, 1) is None, "DATA id <-> category / rarity")
    for i, r in enumerate(RAR):
        K.check(abs(float(Cfg.eggRatio(i + 1)) - EG.RATIO[r]) < 1e-9 and bool(Cfg.eggHalf(i + 1)) == (EG.POOL[r] == "half")
                and list(Cfg.eggRarity(i + 1)) == list(EG.RARITY_W[r]), "DATA the %s egg rows = skyyeggs (ratio, pool, rarity)" % r)
    for c in EG.CATEGORIES:
        K.eq(str(Cfg.eggOrder(c)), ",".join(EG.ORDER[c]), "DATA the %s order row" % c)
        K.eq([str(x) for x in Egg.order(c)], EG.ORDER[c], "DATA order(%s) = the spec 2.2 list" % c)
    K.check([int(Cfg.dropN(s)) for s in EG.DROP_SOURCES] == [EG.DROP_N[s] for s in EG.DROP_SOURCES] and list(Cfg.dropW(False)) == list(EG.DROP_LOW)
            and list(Cfg.dropW(True)) == list(EG.DROP_HIGH) and int(Cfg.DROP_HTIER) == 4 and int(Cfg.DROP_CAP) == 3 and abs(float(Cfg.DROP_FPCT) - 25) < 1e-9
            and abs(float(Cfg.DROP_FCAP) - 2) < 1e-9 and str(Cfg.HATCH_ANIM) == "reel" and int(Cfg.REEL_FRAMES) == 14 and abs(float(Cfg.REEL_S) - 3) < 1e-9
            and str(Cfg.ANNOUNCE) == "legendary" and bool(Cfg.FORCE_SAVE) and bool(Cfg.EGG_ON) and bool(Cfg.DROP_ON), "DATA the drop + hatch rows' defaults")
    dt = str(Cfg.DEFAULT_TEXT)
    K.check("pets.egg.rarity.legendary=0/0/6500/2800/600/100\n" in dt and "pets.egg.order.combat=" + ",".join(EG.ORDER["Combat"]) + "\n" in dt
            and "pets.egg.drop.mining=5000\n" in dt and "pets.hatch.announce=legendary\n" in dt, "DATA the default config text holds the egg rows")
    # ---------------------------------------------------------------- W: weights, the top-half rule, seeded rolls
    bad = []
    for n in range(1, 21):
        for r in RAR:
            a = [float(x) for x in Egg.weights(n, EG.RATIO[r], EG.POOL[r] == "half")]
            b = EG.weights(n, EG.RATIO[r], EG.POOL[r])
            if len(a) != len(b) or any(abs(x - y) > 1e-12 for x, y in zip(a, b)):
                bad.append((n, r))
            if r in EG.NEVER_BELOW_RARE and (any(x != 0 for x in a[max(1, n // 2):]) or any(x <= 0 for x in a[:max(1, n // 2)])):
                bad.append(("top-half", n, r))
    K.check(not bad, "W the weights for n = 1..20 x 6 rarities = skyyeggs.weights + the top-half rule: %s" % bad[:4])
    N = 100000
    for cat, n in (("Combat", 14), ("Mining", 4)):
        for ri, r in enumerate(RAR):
            if r not in ("Common", "Epic", "Mythic"):
                continue
            Egg.RNG = Random(1000 + ri)
            got = {}
            for _ in range(N):
                k = str(Egg.roll1(Egg.RNG, cat, ri + 1))
                got[k] = got.get(k, 0) + 1
            want = EG.percents(n, r)
            dev = max(abs(100.0 * got.get(k, 0) / N - want[i]) for i, k in enumerate(EG.ORDER[cat]))
            K.check(dev < 0.5 and set(got) <= set(EG.ORDER[cat]), "W %d seeded roll-1 draws, a %s %s egg: within %.2f %% of the spec 3.1 table" % (N, r, cat, dev))
    for ri, r in enumerate(RAR):
        Egg.RNG = Random(2000 + ri)
        got = [0] * 6
        for _ in range(N):
            got[int(Egg.roll2(Egg.RNG, ri + 1)) - 1] += 1
        dev = max(abs(100.0 * got[i] / N - EG.RARITY_W[r][i] / 100.0) for i in range(6))
        K.check(dev < 0.5 and (r not in EG.NEVER_BELOW_RARE or got[0] == got[1] == 0), "W %d seeded roll-2 draws, a %s egg: within %.2f %% of the spec 4 table%s" % (
            N, r, dev, " (never below Rare)" if r in EG.NEVER_BELOW_RARE else ""))
    Egg.RNG = None
    worst = 0.0
    for c in EG.CATEGORIES:
        for ri, r in enumerate(RAR):
            t = str(Egg.odds(c, r, "100000"))
            lines = t.split("\n")
            pets = [l for l in lines[1:] if l.startswith("  ") and "%" in l][:len(EG.ORDER[c])]
            for i, l in enumerate(pets):
                m = re.search(r" ([0-9.]+)% / ([0-9.]+)%$", l)
                worst = max(worst, abs(float(m.group(1)) - float(m.group(2))))
                worst = max(worst, abs(float(m.group(1)) - EG.percents(len(EG.ORDER[c]), r)[i]) - 0.05 if abs(EG.percents(len(EG.ORDER[c]), r)[i]) >= 10 else 0)
    K.check(worst < 1.0, "W /petadmin hatchodds for all 30 eggs (unseeded, 100,000 rolls each): expected = the spec tables, rolled within %.2f %%" % worst)
    K.check(str(Egg.odds("Nope", "Rare", None)).startswith("-") and str(Egg.odds("Mining", "Shiny", None)).startswith("-")
            and str(Egg.odds("Mining", "Rare", "0")).startswith("-"), "W hatchodds refuses a bad category / rarity / count")
    K.check(str(Egg.pct(3.9)) == "3.9%" and str(Egg.pct(0.09)) == "0.09%" and str(Egg.pct(0.01)) == "0.01%" and str(Egg.pct(61.8)) == "61.8%"
            and str(Egg.pct(0)) == "0%", "W the % text")
    ot = str(Egg.oddsText("Mining", 5))
    K.check(ot.startswith("Goat 33.3% - Warthog 66.7%") and "other 2 never hatch" in ot, "W the hatch page odds line of a Legendary Mining egg: %s" % ot)
    K.check(str(Egg.rarityText(5)) == "Rare 65% - Epic 28% - Legendary 6.0% - Mythic 1.0%", "W the rarity line: %s" % Egg.rarityText(5))
    # ---------------------------------------------------------------- CHK: the row checks + order()
    chk = lambda k, v: Cfg.checkEggW(k, v)
    K.check(chk("pets.egg.rarity.common", "7000/2300/600/90/9/1") is None and chk("pets.egg.rarity.legendary", "0/0/6500/2800/600/100") is None
            and "never gives a Common" in str(chk("pets.egg.rarity.legendary", "1/0/6500/2800/600/100"))
            and "never gives a Common" in str(chk("pets.egg.rarity.mythic", "0/5/0/6500/2800/700"))
            and chk("pets.egg.rarity.rare", "1/2/3") is not None and chk("pets.egg.rarity.rare", "0/0/0/0/0/0") is not None
            and chk("pets.egg.rarity.rare", "a/b/c/d/e/f") is not None and chk("pets.egg.rarity.rare", "-1/2/3/4/5/6") is not None,
            "CHK the rarity rows: six whole numbers, not all 0, Legendary / Mythic never C / U")
    K.check(Cfg.checkDropW("x", "7500/2000/450/45/5/0") is None and Cfg.checkDropW("x", "1/2") is not None, "CHK the drop rarity rows")
    K.check(Cfg.checkEggOrder("k", "Goat,Mouse") is None and Cfg.checkEggOrder("k", "-") is None and "no pet kind" in str(Cfg.checkEggOrder("k", "Goat,Dragon"))
            and "twice" in str(Cfg.checkEggOrder("k", "Goat,goat")) and Cfg.checkEggOrder("k", "Goat/Mouse") is not None and Cfg.checkEggOrder("k", " , ") is not None,
            "CHK the order rows")
    Cfg.EGG_W5 = "5000/0/2500/1500/900/100"
    w5 = [int(x) for x in Cfg.eggRarity(5)]
    Cfg.EGG_W5 = "garbage"
    K.check(w5 == [0, 0, 2500, 1500, 900, 100] and list(Cfg.eggRarity(5)) == list(EG.RARITY_W["Legendary"]),
            "CHK a hand-edited Legendary row with a Common weight is still never below Rare; a broken row = the built-in")
    Cfg.EGG_W5 = EG.rarity_text(EG.RARITY_W["Legendary"])
    Cfg.KINDS_OFF = "Warthog"
    o1 = [str(x) for x in Egg.order("Mining")]
    Cfg.KINDS_OFF = "-"
    Cfg.EGG_O_MINING = "Mouse,Dragon,Goat"
    o2 = [str(x) for x in Egg.order("Mining")]
    Cfg.EGG_O_MINING = "-"
    o3 = [str(x) for x in Egg.order("Mining")]
    r3n = Egg.roll1(Random(1), "Mining", 1)
    Cfg.EGG_O_MINING = ",".join(EG.ORDER["Mining"])
    K.check(o1 == ["Goat", "Meerkat", "Mouse"], "CHK a switched-off kind leaves the pool: %s" % o1)
    K.check(o2 == ["Warthog", "Mouse", "Goat", "Meerkat"] and any("Dragon, which is not a pet kind" in str(l) for l in list(Log.LINES)),
            "CHK an unknown kind is left out (one warning); kinds in no list go by start rarity: the Uncommon Warthog before the first Common, the Common Meerkat last: %s" % o2)
    K.check(o3 == [] and r3n is None, "CHK - = no pet can hatch from that egg")

    # ---------------------------------------------------------------- HATCH
    def mk(n):
        u = UUID.fromString("00000000-0000-0000-0000-%012d" % n)
        names[str(u)] = "P%d" % n
        key = str(Store.pkey(u))
        Store.KEYOF.put(u, key)
        return u, key, Store.get(key)
    EID = "Skyy_PetEgg_Mining_Rare"

    def hatch(u, inv, egg=EID, clear=True):
        if clear:
            Egg.CLICK.clear()
        return [None if x is None else str(x) for x in Egg.hatch(u, proxy_inv(inv), egg, "harness")]
    u1, k1, r1 = mk(401)
    inv1 = Inv(EID, 3)
    led0 = len(ledger(mods))
    res = hatch(u1, inv1)
    hid, pid = res[1], res[2]
    f1 = props(os.path.join(pdir, k1 + ".properties"))
    K.check(res[0].startswith("+") and inv1.count(EID) == 2 and bool(r1.has(pid)) and int(r1.levelOf(pid)) == 1 and int(r1.xpOf(pid)) == 0
            and str(r1.kindOf(pid)) in EG.ORDER["Mining"] and 1 <= int(r1.rarityOf(pid)) <= 6, "HATCH one press: one egg gone (3 -> 2), one Lv 1 Mining pet: %s" % res)
    K.check(f1.get("pet.%s.src" % pid) == "egg:%s:%s" % (EID, hid) and f1.get("eggdebt." + hid, "").startswith(EID + "|3|")
            and f1.get("hatch.unseen." + hid) == "%s|%s|%s" % (EID, res[3], res[4]) and f1.get("active.1") == pid,
            "HATCH ONE save holds the pet (src egg:<egg>:<hid>), the debt (count before = 3) and the reveal line; the first pet goes in the pet slot")
    L = ledger(mods)[led0:]
    K.check(len(L) == 3 and ("hatch-intent %s egg=%s slot=0 before=3" % (hid, EID)) in L[0] and L[0].split("\t")[1] == "-" and L[1].split("\t")[1] == pid
            and ("hatch-done %s %s" % (hid, pid)) in L[2] and L[2].split("\t")[1] == "-", "HATCH the ledger: intent (pet id -), the pet's own line, done: %s" % [l[-80:] for l in L])
    K.check(Store.ledgerFind(hid) is None, "HATCH /petadmin restore never sees a hatch line (pet id column = -)")
    K.check(str(hid) in Egg.SESSION and int(Egg.HATCHES.get()) >= 1, "HATCH the debt belongs to this server run")
    # gates
    K.check(hatch(u1, Inv("Skyy_PetEgg_Mining_Epic", 1))[0].startswith("-Hold the egg") and hatch(u1, Inv(None, 0))[0].startswith("-Hold the egg"),
            "HATCH a different held item / an empty hand = refused (the page's egg is re-checked)")
    Cfg.ON = False
    a = hatch(u1, inv1)
    Cfg.ON = True
    Cfg.EGG_ON = False
    b = hatch(u1, inv1)
    Cfg.EGG_ON = True
    BR.put("profile:busy:" + str(u1), Bool.TRUE)
    c = hatch(u1, inv1)
    BR.remove("profile:busy:" + str(u1))
    K.check(a[0].startswith("-Pets are switched off") and b[0].startswith("-Pet eggs are switched off") and c[0].startswith("-Your profile is still switching")
            and inv1.count(EID) == 2, "HATCH pets off / eggs off / profile switching = refused, the egg kept")
    om = int(Cfg.OWNED_MAX)
    Cfg.OWNED_MAX = int(r1.count())
    d = hatch(u1, inv1)
    Cfg.OWNED_MAX = om
    K.check(d[0].startswith("-Your pet collection is full (1 / 1). Fuse pets to make room.") and inv1.count(EID) == 2, "HATCH a full collection = refused: %s" % d[0])
    Cfg.EGG_O_MINING = "-"
    e = hatch(u1, inv1)
    Cfg.EGG_O_MINING = ",".join(EG.ORDER["Mining"])
    K.check(e[0].startswith("-No Mining pet can hatch") and inv1.count(EID) == 2, "HATCH no kind can hatch = refused, the egg kept")
    n0 = int(r1.count())
    h1 = hatch(u1, inv1)
    h2 = hatch(u1, inv1, clear=False)
    K.check(h1[0].startswith("+") and h2[0].startswith("=Hatching - one press") and int(r1.count()) == n0 + 1 and inv1.count(EID) == 1,
            "HATCH a double click within 1 s = one hatch")
    Egg.HATCHING.put(u1, JClass("java.lang.Long")(1))
    h3 = hatch(u1, inv1)
    Egg.HATCHING.remove(u1)
    K.check(h3[0].startswith("=Already hatching") and inv1.count(EID) == 1, "HATCH a second hatch while one runs = refused")
    # a slot that gives 0 / 2
    inv2 = Inv(EID, 5)
    inv2.take_mode = "zero"
    n0 = int(r1.count())
    z = hatch(u1, inv2)
    inv2.take_mode = "double"
    z2 = hatch(u1, inv2)
    L = ledger(mods)
    K.check(z[0].startswith("-Your egg could not be taken") and z2[0].startswith("-Your egg could not be taken") and int(r1.count()) == n0
            and inv2.count(EID) == 5 and sum(1 for l in L if "hatch-abort" in l and " take (" in l) == 2, "HATCH a slot that gives 0 / 2 eggs: abort take, the extra put back (5 stay), no pet")
    # a failed save: the pet folder replaced by a file
    real_dir = Store.DIR
    blk = os.path.join(scratch, "blocked-file")
    open(blk, "w").write("x")
    Store.DIR = Paths.get(blk).resolve("pets")
    Store.REC.clear()
    u3, k3, r3 = mk(403)
    inv3 = Inv(EID, 2)
    f = hatch(u3, inv3)
    inv3b = Inv(EID, 2)
    inv3b.give_mode = "full"
    f2 = hatch(u3, inv3b)
    Store.DIR = real_dir
    Store.REC.clear()
    L = ledger(mods)
    K.check(f[0].startswith("-Your pets could not be saved - nothing hatched, your egg is back.") and inv3.count(EID) == 2 and any(" save-refund " in l for l in L),
            "HATCH a failed save: nothing hatched, the egg back (counted), hatch-abort save-refund")
    K.check(f2[0].startswith("-Your pets could not be saved and your egg could not be put back") and any(" refund-failed " in l for l in L)
            and any("could not be put back - give it back by hand" in str(l) for l in list(Log.LINES)), "HATCH ... + a full inventory: refund-failed + a warning for the admin")

    # ---------------------------------------------------------------- CRASH: a stop after every step
    def restart(inv):
        Egg.SESSION.clear(); Egg.DONE.clear(); Egg.ANIM.clear(); Egg.HATCHING.clear(); Egg.CLICK.clear()
        Egg.FAULT = 0
        Store.REC.clear()
        Store.scanAll()
        hr = [int(x) for x in Egg.recover()]
        if inv is not None:
            inv.restart()
        return hr

    def egg_pets(key, hid_):
        p = props(os.path.join(pdir, key + ".properties"))
        return [k[4:-4] for k, v in p.items() if k.endswith(".src") and v == "egg:%s:%s" % (EID, hid_)]

    def last_hid():
        for l in reversed(ledger(mods)):
            m = re.search(r"hatch-intent (\w+) ", l)
            if m:
                return m.group(1)
        return None

    def closed_once(h):
        L = ledger(mods)
        return sum(1 for l in L if re.search(r"hatch-(done|abort) %s\b" % h, l)) == 1

    cases = [(1, False, False), (2, False, False), (3, False, False), (4, False, False), (5, False, False), (4, True, False),
             (0, False, False), (0, False, True)]
    for step, gap, psaved in cases:
        u, k, r = mk(500 + len(cases) * 0 + step * 10 + (1 if gap else 0) + (2 if psaved else 0))
        inv = Inv(EID, 4)
        inv.psave()
        e0 = inv.count(EID)
        Egg.FAULT = step
        threw = False
        try:
            hatch(u, inv)
        except Exception:
            threw = True
        Egg.FAULT = 0
        h_ = last_hid()
        if gap:     # the createR rename landed, its own ledger line did not (the stop came between)
            p = os.path.join(home, "ledger.log")
            ls = open(p, encoding="utf-8").read().splitlines()
            open(p, "w", encoding="utf-8").write("\n".join(l for l in ls if ("egg:%s:%s" % (EID, h_)) not in l) + "\n")
        if psaved:
            inv.psave()        # the player save landed before the stop (the debt was not cleared yet)
        hr = restart(inv)
        u2 = u
        Store.KEYOF.put(u2, k)
        r2 = Store.get(k)
        Egg.debts(u2, r2, proxy_inv(inv), JClass("java.lang.System").currentTimeMillis())
        pets = egg_pets(k, h_)
        after = inv.count(EID)
        kept = [x for x in props(os.path.join(pdir, k + ".properties")) if x.startswith("eggdebt.")]
        if kept:     # a reconciled debt waits for the player save (a second stop before it = taken again): stop once more, then save
            restart(inv)
            Store.KEYOF.put(u2, k)
            r2 = Store.get(k)
            Egg.debts(u2, r2, proxy_inv(inv), JClass("java.lang.System").currentTimeMillis())
            K.check(inv.count(EID) + len(egg_pets(k, h_)) == e0, "CRASH a SECOND stop right after the reconcile (before the player save): still %d" % e0)
            inv.psave()
            Egg.debts(u2, r2, proxy_inv(inv), JClass("java.lang.System").currentTimeMillis() + 31000)
        after = inv.count(EID)
        debt_left = [x for x in props(os.path.join(pdir, k + ".properties")) if x.startswith("eggdebt.")]
        what = "CRASH a stop after step %d%s%s" % (step, " (in the rename -> ledger gap)" if gap else "", " after the player save" if psaved else "")
        K.check((threw or step == 0) and after + len(pets) == e0 and len(pets) in (0, 1) and not debt_left and closed_once(h_),
                "%s: eggs %d + hatched pets %d == %d before, no debt left, the intent closed once (recover %s)" % (what, after, len(pets), e0, hr))
    hr = restart(None)
    K.check(hr == [0, 0, 0], "CRASH a second start finds nothing open")

    # ---------------------------------------------------------------- DEBT + the reveal
    restart(None)
    u4, k4, r4 = mk(404)
    inv4 = Inv(EID, 3)
    told.clear()
    res = hatch(u4, inv4)
    h4 = res[1]
    now = int(JClass("java.lang.System").currentTimeMillis())
    K.check(int(Egg.debts(u4, r4, proxy_inv(inv4), now)) == 0 and r4.get("eggdebt." + h4) is not None, "DEBT an in-session debt waits (no forced save done, < 30 s)")
    K.check(int(Egg.debts(u4, r4, proxy_inv(inv4), now + 31000)) == 1 and r4.get("eggdebt." + h4) is None
            and "eggdebt." + h4 not in props(os.path.join(pdir, k4 + ".properties")) and inv4.count(EID) == 2, "DEBT ... 30 s later it clears (saved), the egg count untouched")
    res = hatch(u4, inv4)
    h5 = res[1]
    Egg.DONE.put(h5, JClass("java.lang.Long")(now))
    K.check(int(Egg.debts(u4, r4, proxy_inv(inv4), now)) == 1 and r4.get("eggdebt." + h5) is None, "DEBT the forced save finished (DONE) = cleared at once")
    K.check(any(("hatch-debt-clear %s (the forced player save finished)" % h5) in l for l in ledger(mods)), "DEBT ... ledger hatch-debt-clear")
    r4.set("eggdebt.zzzz9999", "garbage")
    Egg.debts(u4, r4, proxy_inv(inv4), now)
    K.check(r4.get("eggdebt.zzzz9999") is None and any("could not be read - cleared" in str(l) for l in list(Log.LINES)), "DEBT an unreadable debt line is cleared with a warning")
    told.clear()
    Egg.ANIM.put(h5, JClass("java.lang.Long")(int(JClass("java.lang.System").currentTimeMillis())))
    n1 = int(Egg.unseen(u4, r4))
    Egg.ANIM.clear()
    n2 = int(Egg.unseen(u4, r4))
    n3 = int(Egg.unseen(u4, r4))
    mine = [t for x, t in told if x == str(u4)]
    hz = hatch(u4, Inv(EID, 1))[1]
    Egg.ANIM.put(hz, JClass("java.lang.Long")(int(JClass("java.lang.System").currentTimeMillis()) - 31000))
    told.clear()
    K.check(int(Egg.unseen(u4, r4)) == 1 and any("You hatched a" in t for x, t in told), "DEBT a reel that never finished (30 s) no longer holds its reveal back")
    K.check(n1 == 1 and n2 == 1 and n3 == 0 and len(mine) == 2 and all("You hatched a" in t and "from your Rare Mining Egg" in t for t in mine),
            "DEBT the reveal: none while its reel runs, then ONE chat line per hatch, never again: %s" % mine[:1])
    # Legendary announce: force a Legendary
    Cfg.EGG_W3 = "0/0/0/0/10000/0"
    names[str(UUID.fromString("00000000-0000-0000-0000-000000000999"))] = "Watcher"
    told.clear()
    res = hatch(u4, inv4)
    Egg.unseen(u4, r4)
    Cfg.EGG_W3 = EG.rarity_text(EG.RARITY_W["Rare"])
    ann = [(x, t) for x, t in told if "P404 hatched a Legendary" in t]
    K.check(res[4] == "5" and len(ann) >= 2, "DEBT a Legendary hatch is announced to every online player (row pets.hatch.announce): %s" % ann[:1])
    Cfg.ANNOUNCE = "mythic"
    told.clear()
    Cfg.EGG_W3 = "0/0/0/0/10000/0"
    inv4.live["held"][1] += 1
    hatch(u4, inv4)
    Egg.unseen(u4, r4)
    Cfg.EGG_W3 = EG.rarity_text(EG.RARITY_W["Rare"])
    Cfg.ANNOUNCE = "legendary"
    K.check(not [t for x, t in told if "hatched a Legendary" in t and "P404 hatched" in t], "DEBT ... announce mythic = a Legendary is not announced")

    # a GAIN of that egg while a debt is open asks for a player save at once (the debt then clears on DONE)
    inv4.live["held"][1] += 2
    res = hatch(u4, inv4)
    hg = res[1]
    nowg = int(JClass("java.lang.System").currentTimeMillis())
    Egg.FORCE.clear()
    f0 = int(Egg.REFORCED.get())
    Egg.debts(u4, r4, proxy_inv(inv4), nowg)
    K.check(not Egg.FORCE.containsKey(hg), "DEBT no gain = no extra save")
    c_before_gain = inv4.count(EID)
    inv4.give(EID, 1)
    Egg.debts(u4, r4, proxy_inv(inv4), nowg)
    K.check(Egg.FORCE.containsKey(hg) and int(Egg.REFORCED.get()) >= f0 + 1 and inv4.count(EID) == c_before_gain + 1, "DEBT the player gains that egg while the debt is open: a forced player save is asked for at once")
    Egg.FORCE.clear()
    Egg.debts(u4, r4, proxy_inv(inv4), nowg)
    K.check(not Egg.FORCE.containsKey(hg), "DEBT ... once (no new gain = no new save)")
    Egg.DONE.put(hg, JClass("java.lang.Long")(nowg))
    Egg.debts(u4, r4, proxy_inv(inv4), nowg)
    K.check(r4.get("eggdebt." + hg) is None, "DEBT ... that save done = the debt clears")
    # after a stop: the count before EXACTLY = take; more (a save after the hatch with gains) or less = clear
    for gain, want_take in ((0, True), (2, False), (-1, False)):
        restart(None)
        uq, kq, rq = mk(450 + gain + 1)
        invq = Inv(EID, 5)
        invq.psave()
        hatch(uq, invq)
        if gain:
            invq.live["rest"][EID] = invq.live["rest"].get(EID, 0) + gain
            invq.psave()          # the player was saved after the hatch (with the gain / loss)
        e_saved = invq.saved["held"][1] + invq.saved["rest"].get(EID, 0)
        restart(invq)
        Store.KEYOF.put(uq, kq)
        rq = Store.get(kq)
        Egg.debts(uq, rq, proxy_inv(invq), int(JClass("java.lang.System").currentTimeMillis()))
        took = invq.count(EID) == e_saved - 1
        K.check(took == want_take and (invq.count(EID) == e_saved - (1 if want_take else 0)),
                "DEBT after a stop with %s: %s" % ({0: "no player save since the hatch (the egg came back)", 2: "a save after the hatch + 2 more eggs",
                                                    -1: "a save after the hatch + 1 egg sold"}[gain], "taken" if want_take else "cleared, nothing taken"))
    restart(None)
    Store.KEYOF.put(u4, k4)
    r4 = Store.get(k4)

    # ---------------------------------------------------------------- MYTH
    Cfg.EGG_W3 = "0/0/0/0/0/10000"
    inv4.live["held"][1] += 1
    res = hatch(u4, inv4)
    Cfg.EGG_W3 = EG.rarity_text(EG.RARITY_W["Rare"])
    mp = res[2]
    K.check(int(r4.rarityOf(mp)) == 6 and str(Ops.petName(r4, mp)).startswith("Mythic "), "MYTH a Mythic pet from an egg: %s" % Ops.petName(r4, mp))
    K.check("fusing stops at Legendary" in str(Ops.fuseWhy(r4, mp)), "MYTH fusing refuses a Mythic pet (stops at Legendary): %s" % Ops.fuseWhy(r4, mp))
    r4.set("active.1", mp)
    r4.set("pet.%s.level" % mp, "50")
    pk = Cfg.kind(r4.kindOf(mp))
    t = [float(x) for x in Buff.compute(r4, "w")]
    SK = [str(x) for x in Kind.STAT_KEYS]
    v0 = dict(zip([str(x) for x in pk.keys], [float(x) for x in pk.vals]))
    okm = all(abs(t[SK.index(sk)] - min(v * 1.5 * 50 / 100.0, (10.0 if sk.startswith("fortune.") else 5.0) * 1.5 if sk.startswith(("fortune.", "swing.")) else 1e9)) < 1e-9 for sk, v in v0.items())
    K.check(okm, "MYTH its buffs = value x 1.5 x Lv / 100 (caps x 1.5): %s" % [(sk, t[SK.index(sk)]) for sk in v0])
    K.check("Mythic comes from eggs" in str(Ops.admin("h", "give", "P404", "Rabbit", "Mythic", None)), "MYTH /petadmin give still refuses Mythic (Mythic comes from eggs)")

    # ---------------------------------------------------------------- FUZZ
    restart(None)
    rnd = random.Random(40)
    u5, k5, r5 = mk(405)
    inv5 = Inv(EID, 60)
    inv5.psave()
    E0 = 60
    hatched = set()
    viol = []
    now_ms = lambda: int(JClass("java.lang.System").currentTimeMillis())

    def stop_and_check(it):
        """a server stop: the live inventory falls back to the player file, the pet files are scanned + recovered, the join reconciles"""
        global_r = restart(inv5)
        Store.KEYOF.put(u5, k5)
        rr_ = Store.get(k5)
        Egg.debts(u5, rr_, proxy_inv(inv5), now_ms())
        p_ = props(os.path.join(pdir, k5 + ".properties"))
        pets_ = [k for k, v in p_.items() if k.endswith(".src") and v.startswith("egg:")]
        if os.environ.get("FUZZ_TRACE"):
            print("STOP", it, inv5.count(EID), len(pets_), E0[0], global_r, len([x for x in p_ if x.startswith("eggdebt.")]))
        if inv5.count(EID) + len(pets_) != E0[0]:
            viol.append((it, inv5.count(EID), len(pets_), global_r))
            if os.environ.get("FUZZ_TRACE"):
                print("TRACE", it, viol[-1], E0[0], TRACE[-6:])
        return rr_
    E0 = [60]
    TRACE = []
    for it in range(300):
        op = rnd.random()
        TRACE.append((it, round(op, 2), inv5.count(EID), inv5.saved["held"][1]))
        if op < 0.5:
            Egg.FAULT = rnd.choice([0, 0, 0, 1, 2, 3, 4, 5])
            crashed = False
            try:
                rr = hatch(u5, inv5)
                if rr[0].startswith("+"):
                    hatched.add(rr[1])
            except Exception:
                crashed = True
            Egg.FAULT = 0
            if crashed:                       # the process died: nothing else happens before the restart
                r5 = stop_and_check(it)
                continue
            if rnd.random() < 0.4:
                inv5.psave()                  # the engine's own player save (or the forced one)
            if rnd.random() < 0.3:
                inv5.psave()                  # 30 s later the engine has saved the player: the in-session debt may clear
                Egg.debts(u5, r5, proxy_inv(inv5), now_ms() + 31000)
        elif op < 0.65:
            inv5.psave()
        else:
            r5 = stop_and_check(it)
            if inv5.count(EID) < 3:
                # more eggs of the SAME id only once the debts are settled (30 s + the engine's save): a gain of that egg inside a debt's
                # window + a stop before the debt clears is the one case the count check cannot see (window: ms with the forced save)
                inv5.psave()
                Egg.debts(u5, r5, proxy_inv(inv5), now_ms() + 31000)
                inv5.live["held"][1] += 10
                inv5.psave()
                E0[0] += 10
    E0 = E0[0]
    restart(inv5)
    Store.KEYOF.put(u5, k5)
    r5 = Store.get(k5)
    Egg.debts(u5, r5, proxy_inv(inv5), int(JClass("java.lang.System").currentTimeMillis()))
    inv5.psave()
    Egg.debts(u5, r5, proxy_inv(inv5), int(JClass("java.lang.System").currentTimeMillis()) + 31000)
    p = props(os.path.join(pdir, k5 + ".properties"))
    pets = [k for k, v in p.items() if k.endswith(".src") and v.startswith("egg:")]
    ids = [x for k5_, x in []]
    allids = {}
    for f_ in os.listdir(pdir):
        for kk in props(os.path.join(pdir, f_)):
            if kk.startswith("pet.") and kk.endswith(".kind"):
                allids[kk[4:-5]] = allids.get(kk[4:-5], 0) + 1
    K.check(not viol and inv5.count(EID) + len(pets) == E0 and not [x for x in p if x.startswith("eggdebt.")] and max(allids.values()) == 1,
            "FUZZ 300 random steps (hatch, a stop after a random step, player saves, restarts + reconcile): eggs + hatched pets == %d every restart, "
            "every debt resolved after the last save, no pet id twice (%d hatched): %s" % (E0, len(pets), viol[:3]))

    # ---------------------------------------------------------------- DROP: pets:fn:eggroll
    restart(None)
    u6, k6, r6 = mk(406)
    RollFn = P_("PetEggRollFn")()
    BR.put("pets:fn:eggroll", RollFn)
    queued = []
    qok = [True]
    P_("PetEggGive").QUEUE_API = JProxy("java.util.function.Function", dict={"apply": lambda a: (queued.append(str(a[1])), JClass("java.lang.Boolean")(qok[0]))[1]})
    ObjA = JClass("java.lang.Object[]")
    Dbl, Int = JClass("java.lang.Double"), JClass("java.lang.Integer")
    roll = lambda cat, src, f, tier: RollFn.apply(ObjA([u6, cat, src, Dbl(f), Int(tier)]))
    Cfg.DROP_MINING = 1
    Egg.DROPS.clear()
    a = [roll("Mining", "mining", 0.0, 1) for _ in range(5)]
    K.check(all(x is not None and str(x).startswith("Skyy_PetEgg_Mining_") for x in a[:3]) and a[3] is None and a[4] is None and int(Egg.CAPPED.get()) >= 2,
            "DROP 1 in 1: an egg each roll until the cap (3 per hour per profile), then none: %s" % [str(x) for x in a])
    Cfg.DROP_CAP = 100000
    Egg.DROPS.clear()
    Egg.RNG = Random(7)
    hi = {}
    lo = {}
    for _ in range(4000):
        x = str(roll(None, "mining", 0.0, 5))
        hi[x] = hi.get(x, 0) + 1
        y = str(roll(None, "mining", 0.0, 2))
        lo[y] = lo.get(y, 0) + 1
    pc = lambda d, r: 100.0 * d.get("Skyy_PetEgg_Mining_" + r, 0) / 4000.0
    K.check(abs(pc(lo, "Common") - 75) < 3 and abs(pc(hi, "Common") - 55) < 3 and abs(pc(hi, "Uncommon") - 30) < 3 and pc(lo, "Mythic") == 0,
            "DROP the rarity bands: tier < 4 = 75 %% Common (%.1f), tier >= 4 = 55 %% Common / 30 %% Uncommon (%.1f / %.1f), no Mythic below the high tier"
            % (pc(lo, "Common"), pc(hi, "Common"), pc(hi, "Uncommon")))
    Cfg.DROP_MINING = 10
    Egg.RNG = Random(8)
    h0 = sum(1 for _ in range(20000) if roll(None, "mining", 0.0, 1) is not None)
    Egg.RNG = Random(9)
    h2 = sum(1 for _ in range(20000) if roll(None, "mining", 5.0, 1) is not None)
    BR.put("pets:luck:" + str(u6), Dbl(100.0))
    Egg.RNG = Random(10)
    h3 = sum(1 for _ in range(20000) if roll(None, "mining", 0.0, 1) is not None)
    BR.remove("pets:luck:" + str(u6))
    K.check(abs(h0 / 20000.0 - 0.1) < 0.01 and abs(h2 / 20000.0 - 0.15) < 0.012 and abs(h3 / 20000.0 - 0.2) < 0.012,
            "DROP 1 in 10 = 10 %% (%.3f); Fortune 5 counts only to 2 x 25 %% = x1.5 (%.3f); pets:luck 100 %% = x2 (%.3f)" % (h0 / 20000.0, h2 / 20000.0, h3 / 20000.0))
    Egg.RNG = None
    Cfg.DROP_MINING = 1
    Cfg.DROP_ON = False
    q1 = roll("Mining", "mining", 0.0, 1)
    Cfg.DROP_ON = True
    Cfg.EGG_ON = False
    q2 = roll("Mining", "mining", 0.0, 1)
    Cfg.EGG_ON = True
    BR.put("profile:busy:" + str(u6), Bool.TRUE)
    q3 = roll("Mining", "mining", 0.0, 1)
    BR.remove("profile:busy:" + str(u6))
    q4 = roll("Fishing", "fishing", 0.0, 1)
    q5 = roll(None, "placed", 0.0, 1)
    q6 = RollFn.apply("nonsense")
    q7 = roll("Combat", "mining", 0.0, 1)
    K.check(q1 is None and q2 is None and q3 is None and q4 is None and q5 is None and q6 is None and str(q7).startswith("Skyy_PetEgg_Combat_"),
            "DROP drops off / eggs off / profile switching / Fishing (no Fishing egg yet) / an unknown source / a bad call = null; the category names the egg")
    # an egg that cannot be given (the player not reachable) did not drop: null, no hourly cap spent, not counted
    Cfg.DROP_CAP = 3
    Egg.DROPS.clear()
    qok[0] = False
    d0_ = int(Egg.DROPPED.get())
    z = [roll("Mining", "mining", 0.0, 1) for _ in range(4)]
    qok[0] = True
    z2 = [roll("Mining", "mining", 0.0, 1) for _ in range(4)]
    K.check(z == [None] * 4 and int(Egg.DROPPED.get()) == d0_ + 3 and [x is not None for x in z2] == [True, True, True, False] and int(Egg.NOQUEUE.get()) >= 4,
            "DROP an egg the player cannot get = null, no cap spent, not counted (the next 3 still drop, then the cap): %s" % [str(x) for x in z2])
    Cfg.DROP_CAP = 100000
    # the Exploration roll from SkyySkills' own XP report (pets:fn:onxp)
    Cfg.DROP_EXPLORATION = 1
    Egg.DROPS.clear()
    r0 = int(Egg.ROLLS.get())
    P_("PetXpFn")().apply(ObjA([u6, "Exploration", JClass("java.lang.Long")(50), "SkyySkills"]))
    P_("PetXpFn")().apply(ObjA([u6, "Mining", JClass("java.lang.Long")(50), "SkyySkills"]))
    P_("PetXpFn")().apply(ObjA([u6, "Exploration", JClass("java.lang.Long")(50), "OtherMod"]))
    K.check(int(Egg.ROLLS.get()) == r0 + 1, "DROP each Exploration award SkyySkills reports = ONE egg roll (not Mining XP, not another mod's report)")
    Cfg.DROP_EXPLORATION = EG.DROP_N["exploration"]
    Cfg.DROP_MINING = EG.DROP_N["mining"]
    Cfg.DROP_CAP = 3
    K.check(str(Egg.admin("h", "egg", "Nobody", "Mining", "Rare", None)).startswith("-Nobody is not online") and Egg.admin("h", "list", "x", None, None, None) is None
            and str(Egg.admin("h", "egg", "P406", "Fish", "Rare", None)).startswith("-Which egg") and str(Egg.admin("h", "egg", "P406", "Mining", "Shiny", None)).startswith("-Which rarity")
            and str(Egg.admin("h", "egg", "P406", "Mining", "Rare", "500")).startswith("-How many"),
            "DROP /petadmin egg refusals (offline, category, rarity, count) + other verbs fall through to PetOps")
    qok[0] = False
    ae = str(Egg.admin("h", "egg", "P406", "Mining", "Rare", None))
    qok[0] = True
    ae2 = str(Egg.admin("h", "egg", "P406", "Mining", "Rare", "3"))
    K.check(ae.startswith("-Could not reach") and ae2.startswith("+Sent 3 x Rare Mining Egg") and "where they went" in ae2,
            "DROP /petadmin egg says what really happened (not reachable = refused; queued = sent, the player's chat says where): %s" % ae2)
    P_("PetEggGive").QUEUE_API = None

    # ---------------------------------------------------------------- REC: the startup recovery on synthetic ledgers
    restart(None)
    u7, k7, r7 = mk(407)
    p = os.path.join(home, "ledger.log")
    base = open(p, encoding="utf-8").read()
    line = lambda h: "1\t-\t-\t0\t0\t0\t%s\t%s\thatch-intent %s egg=%s slot=0 before=2 kind=Mouse rarity=1\tharness\t-" % (k7, k7, h, EID)
    r7.set("eggdebt.aaaa0001", EID + "|2|1")
    Ops.createR(r7, None, "Mouse", 1, 1, 0, 0, "egg:%s:aaaa0002" % EID, "harness", False)
    Store.save(r7)
    open(p, "a", encoding="utf-8").write("\n".join([line("aaaa0001"), line("aaaa0002"), line("aaaa0003")]) + "\n")
    hr = restart(None)
    L = open(p, encoding="utf-8").read()
    K.check(hr == [3, 2, 1] and "hatch-done aaaa0001 (recovered" in L and "hatch-done aaaa0002 (recovered" in L and "hatch-abort aaaa0003 crash" in L,
            "REC open intents: a debt line = done, a pet src = done, none = abort crash: %s" % hr)
    t1 = open(p, encoding="utf-8").read()
    hr2 = restart(None)
    K.check(hr2 == [0, 0, 0] and open(p, encoding="utf-8").read() == t1, "REC a second start writes nothing")
    K.check(str(base) in L, "REC only lines were appended")
    K.save()


def _uarr(JClass, names):
    UUID = JClass("java.util.UUID")
    a = JClass("java.util.UUID[]")(len(names))
    for i, n in enumerate(names):
        a[i] = UUID.fromString(n)
    return a


def _by(names, n, UUID):
    for k, v in names.items():
        if v.lower() == str(n).strip().lower():
            return UUID.fromString(k)
    return None


# ======================================================================================================== STAGE (the pages + real inventories)
def run_stage(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JShort, JByte
    import hub_tab_kit as HT
    import skyyui as SUI
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Egg, Defs, Page, HPage, Reel, Inv_, Gv, Eng = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"), P_("PetEgg"),
        P_("PetEggDefs"), P_("PetsPage"), P_("PetHatchPage"), P_("PetReel"), P_("PetInvReal"), P_("PetEggGive"), P_("PetsEng"))
    Paths, UUID, IS = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "stage-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    K.eq(str(P_("PetsHubOpen").register()), "character:pets", "the Pets hub tab is registered")
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000501"), "Hatcher")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    r1.set("starter", "123")
    r1.set("slot2.unlocked", "true")
    kinds = [("Rabbit", 1), ("Rabbit", 1), ("Rabbit", 1), ("Rabbit", 1), ("Wolf", 3), ("Horse", 2), ("Goat", 2), ("Dog", 1), ("Ram", 4), ("Mouse", 6)]
    ids = []
    for i in range(66):
        kd, ra = kinds[i % len(kinds)] if i < len(kinds) else (["Cat", "Frog", "Bear", "Skrill", "Gecko"][i % 5], 1 + i % 5)
        ids.append(str(Ops.createR(r1, None, kd, ra, 1 + (i % 40), 0, 0, "test", "harness", False)))
    K.check(all(not x.startswith("-") for x in ids) and int(r1.count()) == 66, "PAGE 66 pets for the grid")
    # ---------------------------------------------------------------- the Pets page
    pg = Page(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, pg)
    E.pump(P1)
    built = HT.build(pg, P1)
    w, h, sets, evs = HT.page_check(K, E, P1, built, "SkyyPt", "character", "pets", "Pets", "PAGE grid view")
    K.check(int(pg.view) == 0 and int(Page.PER_PAGE) == 60 and len(list(pg.ids)) == 60 and int(pg.cells) == 60, "PAGE 12 x 5 = 60 pets on page 1 (%d)" % len(list(pg.ids)))
    sel = [s for s, _t in evs]
    K.check("#SkyyPtGrid" in sel and all(("#SkyyPtM%d" % i) in sel for i in range(4)) and all(("#SkyyPtF%d" % i) in sel for i in range(4))
            and all(("#SkyyPtA%d" % i) in sel for i in range(8)) and "#SkyyPtS1Act" in sel and "#SkyyPtPgNext" in sel, "PAGE the grid, 4 modes, 4 roles, 8 areas, Take out, the pager are bound")
    K.check(not any("SkyyPtB5" in s or "SkyyPtD0" in s for s in sel) and not any("SkyyPtD0V" in s for s in sets), "PAGE the per-pet Open page is gone (no detail rows, no Fuse / Rebirth buttons)")
    K.check("Your pets (66 / 120)" in str(sets.get("#SkyyPtLowH.Text")), "PAGE the head: %s" % sets.get("#SkyyPtLowH.Text"))
    gb = [t for ty, s_, t, d in built[0] if t and "ItemGrid #SkyyPtGrid" in t]
    K.check(len(gb) == 1 and "SlotsPerRow: 12" in gb[0] and "AreItemsDraggable: false" in gb[0] and "InfoDisplay" not in gb[0], "PAGE an ItemGrid of 12 per row, not draggable, with tooltips")
    shown = [str(x) for x in pg.ids]
    rar = [int(r1.rarityOf(x)) for x in shown]
    K.check(rar == sorted(rar, reverse=True), "PAGE rarest first")
    tip = str(Page.tip(r1, ids[4], 0))
    need = ["Rare</color> Fighter", "Level ", "XP: ", "Skill: Combat", "Buffs now: ", "As a summon: ", "Pet rebirths: ", "Fusing: ", "Abilities: none yet",
            "Owned since ", "id " + ids[4], "Click: put it in your pet slot"]
    K.check(all(n in tip for n in need) and tip.count("<color is=") == 2, "PAGE the flavor text lists every spec (Skyy: no Open needed): %s" % [n for n in need if n not in tip])
    tip2 = str(Page.tip(r1, ids[0], 1))
    K.check("Cannot be summoned (pet slot only)" in tip2 and "Gathering pet" in tip2, "PAGE ... in summon mode a Rabbit says it cannot be summoned")
    K.check(str(Page.iconOf(r1, ids[0])) == "Skyy_PetIcon_Rabbit" and str(Page.iconOf(r1, ids[7])) == "Skyy_PetIcon_Dog", "PAGE every pet wears its portrait")
    # filters
    def shown_for(fr, fa):
        pg.fRole, pg.fArea = fr, fa
        a = [str(x) for x in pg.shown(r1)]
        pg.fRole, pg.fArea = 0, 0
        return a
    roles = lambda a: set(str(Cfg.roles(r1.kindOf(x))) for x in a)
    sk = lambda a: set(str(Cfg.kind(r1.kindOf(x)).skill) for x in a)
    fb, ff, fm = shown_for(1, 0), shown_for(2, 0), shown_for(3, 0)
    K.check(len(fb) + len([x for x in ids if "fighter" in str(Cfg.roles(r1.kindOf(x))) or "mount" in str(Cfg.roles(r1.kindOf(x)))]) == 66
            and all("fighter" not in rr and "mount" not in rr for rr in roles(fb)), "PAGE role filter Bonus = only pets that boost (no fighter / mount)")
    K.check(ff and all("fighter" in rr for rr in roles(ff)) and fm and all("mount" in rr for rr in roles(fm)) and any(r1.kindOf(x) == "Ram" for x in ff) and any(r1.kindOf(x) == "Ram" for x in fm),
            "PAGE Fighters / Mounts (the Ram is both)")
    K.check(sk(shown_for(0, 3)) == {"Mining"} and sk(shown_for(0, 2)) == {"Farming"} and sk(shown_for(0, 1)) == {"Combat"} and shown_for(0, 5) == [] and shown_for(0, 7) == []
            and sk(shown_for(0, 6)) == {"Exploration"} and sk(shown_for(0, 4)) == {"Foraging"}, "PAGE area filters (Fishing / Cooking-Alchemy: no pets yet = empty)")

    def click(page, P, a, i=None, extra=None, tok=True):
        d = '{"a":"%s"' % a + (',"i":"%s"' % i if i is not None else "") + (',"t":"%s"' % page.tok if tok else "") + (extra or "") + "}"
        page.handleDataEvent(P.ref, P.st, d)
        E.pump(P)
        return str(page.info)
    click(pg, P1, "area", 3, tok=False)
    hd = dict((s_, d) for ty, s_, t, d in HT.build(pg, P1)[0] if ty == "Set").get("#SkyyPtLowH.Text")
    K.check(int(pg.fArea) == 3 and len(list(pg.ids)) == len(shown_for(0, 3)) and "shown" in str(hd), "PAGE the Area Mining click filters the grid and the head says how many are shown: %s" % hd)
    click(pg, P1, "area", 5, tok=False)
    st5 = dict((s_, d) for ty, s_, t, d in HT.build(pg, P1)[0] if ty == "Set").get("#SkyyPtStatus.Text")
    K.check(len(list(pg.ids)) == 0 and "No pets match this filter" in str(st5), "PAGE an empty filter result says so (Fishing): %s" % st5)
    click(pg, P1, "area", 0, tok=False)
    HT.build(pg, P1)
    b0, u0_, n0_ = int(Page.BUILDS), int(Page.PAGE_UPDATES), len(E.sent(P1))
    first = [str(x) for x in pg.ids]
    click(pg, P1, "next", tok=False)
    K.check(int(pg.pg) == 1 and int(Page.BUILDS) == b0 and int(Page.PAGE_UPDATES) == u0_ + 1 and len(E.sent(P1)) == n0_ + 1 and [str(x) for x in pg.ids] != first,
            "PAGE Next = ONE partial update (the grid, the head, the page caption) - no rebuild")
    click(pg, P1, "next", tok=False)
    K.check(int(pg.pg) == 1 and int(Page.BUILDS) == b0 + 1, "PAGE Next on the last page = the page as it is (one rebuild answers the click)")
    click(pg, P1, "prev", tok=False)
    K.check(int(pg.pg) == 0 and int(Page.PAGE_UPDATES) == u0_ + 2, "PAGE Prev = a partial update back to page 1")
    click(pg, P1, "area", 0, tok=False)
    # mode 0: a click puts the pet in the pet slot, again takes it out
    HT.build(pg, P1)
    tgt = str(pg.ids[0])
    a1 = click(pg, P1, "g", extra=',"SlotIndex":0')
    K.check(a1.startswith("+") and str(r1.active(1)) == tgt, "PAGE mode Pet slot: a click puts it in the pet slot: %s" % a1)
    HT.build(pg, P1)
    j = [str(x) for x in pg.ids].index(tgt)
    a2 = click(pg, P1, "g", extra=',"SlotIndex":%d' % j)
    K.check(a2.startswith("+") and str(r1.active(1)) == "", "PAGE ... a second click takes it out: %s" % a2)
    # mode 1: summon slot
    click(pg, P1, "mode", 1, tok=False)
    click(pg, P1, "area", 2, tok=False)       # Farming: the Rabbits
    HT.build(pg, P1)
    lst = [str(x) for x in pg.ids]
    ri_ = [i for i, x in enumerate(lst) if r1.kindOf(x) == "Rabbit"][0]
    b1 = click(pg, P1, "g", extra=',"SlotIndex":%d' % ri_)
    click(pg, P1, "area", 1, tok=False)       # Combat: the Wolf
    HT.build(pg, P1)
    lst = [str(x) for x in pg.ids]
    wi = [i for i, x in enumerate(lst) if r1.kindOf(x) == "Wolf"][0]
    b2 = click(pg, P1, "g", extra=',"SlotIndex":%d' % wi)
    K.check(b1.startswith("-") and "pet slot only" in b1 and b2.startswith("+") and str(r1.active(2)) == lst[wi], "PAGE mode Summon slot: a Rabbit is refused, a Wolf is summoned: %s / %s" % (b1, b2))
    # Take out on the summon slot row
    HT.build(pg, P1)
    b3 = click(pg, P1, "out", 2)
    K.check(b3.startswith("+") and str(r1.active(2)) == "", "PAGE the summon slot row's Take out: %s" % b3)
    # mode 2: fuse 4 Common Rabbits (two presses)
    click(pg, P1, "mode", 2, tok=False)
    click(pg, P1, "area", 2, tok=False)
    HT.build(pg, P1)
    lst = [str(x) for x in pg.ids]
    cr = [i for i, x in enumerate(lst) if r1.kindOf(x) == "Rabbit" and int(r1.rarityOf(x)) == 1][0]
    base = lst[cr]
    c1 = click(pg, P1, "g", extra=',"SlotIndex":%d' % cr)
    HT.build(pg, P1)
    cr2 = [str(x) for x in pg.ids].index(base)
    c2 = click(pg, P1, "g", extra=',"SlotIndex":%d' % cr2)
    K.check(c1.startswith("=Fuse 4") and c2.startswith("+Fused 4") and int(r1.rarityOf(base)) == 2 and int(r1.count()) == 63, "PAGE mode Fuse: the first click asks, the second fuses: %s" % c2)
    # the 0.3.0 fixer 2 rule on the grid: a weaker same pet arriving between the two presses = asked again, nothing fused
    for _ in range(4):
        Ops.createR(r1, None, "Rabbit", 2, 30, 0, 0, "test", "harness", False)
    HT.build(pg, P1)
    q1 = click(pg, P1, "g", extra=',"SlotIndex":%d' % [str(x) for x in pg.ids].index(base))
    weak = str(Ops.createR(r1, None, "Rabbit", 2, 1, 0, 0, "test", "harness", False))
    HT.build(pg, P1)
    rar0 = int(r1.rarityOf(base))
    q2 = click(pg, P1, "g", extra=',"SlotIndex":%d' % [str(x) for x in pg.ids].index(base))
    K.check(q1.startswith("=Fuse") and q2.startswith("=") and int(r1.rarityOf(base)) == rar0 and bool(r1.has(weak)),
            "PAGE a weaker pet arrived between the two Fuse clicks: asked again, nothing fused (the 0.3.0 pinned fodder): %s" % q2)
    HT.build(pg, P1)
    q3 = click(pg, P1, "g", extra=',"SlotIndex":%d' % [str(x) for x in pg.ids].index(base))
    K.check(q3.startswith("+Fused") and int(r1.rarityOf(base)) == rar0 + 1 and not bool(r1.has(weak)), "PAGE ... the next click fuses exactly the set it named (the new weakest used): %s" % q3)
    # mode 3: rebirth a max-level pet
    r1.set("pet.%s.level" % ids[5], "50")
    click(pg, P1, "mode", 3, tok=False)
    click(pg, P1, "area", 6, tok=False)       # Exploration: the Horse
    HT.build(pg, P1)
    hi_ = [str(x) for x in pg.ids].index(ids[5])
    d1 = click(pg, P1, "g", extra=',"SlotIndex":%d' % hi_)
    HT.build(pg, P1)
    d2 = click(pg, P1, "g", extra=',"SlotIndex":%d' % [str(x) for x in pg.ids].index(ids[5]))
    K.check(d1.startswith("=Rebirth") and d2.startswith("+") and int(r1.rebirthOf(ids[5])) == 1 and int(r1.levelOf(ids[5])) == 1, "PAGE mode Rebirth: two clicks: %s" % d2)
    click(pg, P1, "mode", 0, tok=False)
    click(pg, P1, "area", 0, tok=False)
    HT.build(pg, P1)
    st0 = str(pg.tok)
    pg.tok = "stale"
    e1 = click(pg, P1, "g", extra=',"SlotIndex":0', tok=False)
    pg.handleDataEvent(P1.ref, P1.st, '{"a":"g","SlotIndex":0,"t":"%s"}' % st0)
    K.check("page changed" in str(pg.info) or "page changed" in e1, "PAGE a stale page's grid click is refused")
    HT.build(pg, P1)
    before = int(r1.count())
    click(pg, P1, "next", tok=False)
    HT.build(pg, P1)
    pg.info = "x"
    sl0 = (str(r1.active(1)), str(r1.active(2)), int(r1.count()))
    pg.handleDataEvent(P1.ref, P1.st, '{"a":"g","SlotIndex":59,"t":"%s"}' % pg.tok)
    K.check(int(pg.pg) == 1 and len(list(pg.ids)) == int(r1.count()) - 60 and str(pg.info) == "x" and (str(r1.active(1)), str(r1.active(2)), int(r1.count())) == sl0, "PAGE page 2 holds the rest; a click on an empty grid slot does nothing (page %d, %d shown of %d, info %s)" % (int(pg.pg), len(list(pg.ids)), int(r1.count()), pg.info))
    n0 = len(E.sent(P1))
    click(pg, P1, "close", tok=False)
    K.check(len(E.sent(P1)) > n0 and E.pg(P1) is None, "PAGE Close: one update empties the grid first (no tooltip left behind), then the page closes")
    # ---------------------------------------------------------------- SND / static: the call graph of the new code (bytecode)
    import perfworld_kit as PW
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["PetSnd.playTo"], "SND only PetSnd.playTo calls SoundUtil (the reel ticks too)")
    act = g.get("PetsPage.act", set())
    K.check(all((PKG + x) in act for x in ("PetSnd.slotDone", "PetOps.toSlot", "PetOps.takeOut", "PetOps.fuse", "PetOps.rebirth", "PetOps.fuseAsk", "PetOps.rebAsk"))
            and (PKG + "PetSnd.slotDone") in g.get("PetsPage.handleDataEvent", set()), "SND every grid click (slots, fuse, rebirth) + Take out + Choose go through PetSnd.slotDone")
    K.check(all((PKG + "PetSnd.play") in g.get("PetHatchPage.tick", set()) for _ in [0]) and (PKG + "PetSnd.pick") in g.get("PetHatchPage.tick", set()),
            "SND the reel ticks / reveals use PetSnd.play(pick(master, row, id)) - the /settings mute + the master switch apply")
    inv_calls = set(c for m, cs in g.items() if m.startswith(("PetInvReal.", "PetEgg.", "PetEggGive.", "PetEggSave.")) for c in cs if c.startswith("com.hypixel."))
    K.check(not [c for c in inv_calls if ".inventory." in c and not c.split(".")[-1] in ("getStorage", "getHotbar", "getBackpack", "getUtility", "getTools",
            "getActiveHotbarSlot", "getItemStack", "getCapacity", "removeItemStackFromSlot", "addItemStack", "getItemId", "getQuantity", "isEmpty", "<init>")],
            "STATIC the egg code touches the inventory only through the probed calls: %s" % sorted(c for c in inv_calls if ".inventory." in c))
    K.check((PKG + "PetEgg.hatch") in g.get("PetHatchPage.go", set()) and (PKG + "PetEggSave.force") in g.get("PetHatchPage.go", set())
            and (PKG + "PetOps.createR") in g.get("PetEgg.hatchLocked", set()), "STATIC Hatch = PetEgg.hatch (createR: one save) then the forced player save")
    # ---------------------------------------------------------------- PetInvReal on a real inventory
    hb = P1.slots["hotbar"]
    try:
        hb.setActiveSlot(JByte(0))
    except Exception:
        pass
    EID = "Skyy_PetEgg_Combat_Epic"
    hb.getInventory().addItemStackToSlot(JShort(0), IS(EID, 3))
    P1.slots["storage"].getInventory().addItemStackToSlot(JShort(5), IS(EID, 2))     # (the stage has no item assets: addItemStack refuses every id)
    iv = Inv_.of(P1.st, P1.ref)
    K.check(iv is not None and str(iv.heldId()) == EID and int(iv.heldSlot()) == 0 and int(iv.heldQty()) == 3 and int(iv.count(EID)) == 5,
            "INV the real inventory: held egg slot 0 x3, 5 in all")
    t1_ = int(iv.takeOne(0, EID))
    c1_, q1_ = int(iv.count(EID)), int(iv.heldQty())
    K.check(t1_ == 1 and c1_ == 4 and q1_ == 2 and int(iv.takeOne(0, "Food_Egg")) == 0 and int(iv.takeOne(5, EID)) == 0,
            "INV takeOne: exactly one from the held slot (counted); a wrong id / slot = 0: took %d, count %d, held %d" % (t1_, c1_, q1_))
    ta_ = int(iv.takeAny(EID)); ca_ = int(iv.count(EID)); gv_ = int(iv.give(EID, 4)); cg_ = int(iv.count(EID))
    # the stage's utility / tool slots refuse a non-utility item (as the game does), so this is the call graph: takeAny walks exactly the
    # containers count() sums
    _inv = "com.hypixel.hytale.server.core.inventory.Inventory."
    _cn = lambda m: sorted(c for c in g.get(m, set()) if c.startswith(_inv + "get") and c != _inv + "getActiveHotbarSlot")
    K.check(_cn("PetInvReal.takeAny") == _cn("PetInvReal.count") and len(_cn("PetInvReal.count")) == 5,
            "INV takeAny walks the same 5 containers count() sums: %s" % _cn("PetInvReal.takeAny"))
    K.check(ta_ == 1 and ca_ == 3 and int(P1.slots["storage"].getInventory().getItemStack(JShort(5)).getQuantity()) == 1 and gv_ == cg_ - ca_,
            "INV takeAny takes from storage first (counted); give reports exactly what the count gained (%d: the stage has no item assets, so 0 here)" % gv_)
    # ---------------------------------------------------------------- the hatch page
    told = []
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: _uarr(JClass, [str(u1)]), "byName": lambda n: u1 if str(n) == "Hatcher" else None,
                                            "nameOf": lambda u: "Hatcher", "tell": lambda u, t, c: told.append(str(t))})
    hb.getInventory().removeItemStackFromSlot(JShort(0))
    hb.getInventory().addItemStackToSlot(JShort(0), IS(EID, 12))
    hp = HPage(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, hp)
    E.pump(P1)
    cm, ev = HT.build(hp, P1)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cm if t is not None and ty and "Append" in ty])
    hsets = dict((s, d) for ty, s, t, d in cm if ty == "Set")
    ok_ = True
    try:
        SUI.check_page(apps, "SkyyHt")
    except Exception as ex:
        ok_ = str(ex)
    idset = set()
    for _p, mk in apps:
        idset |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(mk)))
    badt = [s for s in hsets if s.lstrip("#").split(".")[0] not in idset] + [s for s, _t in ev if s.lstrip("#") not in idset]
    root = apps[0][1]
    K.check(ok_ is True and not badt and 'Anchor: (Width: 760, Height: 640)' in root, "HATCH page view 0: markup rules, every set / binding target exists, 760 x 640: %s %s" % (ok_, badt[:3]))
    K.check("Epic Combat Egg" in str(hsets.get("#SkyyHtName.Text")) and "Ram " in str(hsets.get("#SkyyHtOdds.Text")) and "Dog " in str(hsets.get("#SkyyHtOdds.Text"))
            and "Common 10%" in str(hsets.get("#SkyyHtRar.Text")) and "#SkyyHtGo" in [s for s, _t in ev], "HATCH view 0: the egg, its pet odds, its rarity odds, Hatch bound")
    Cfg.HATCH_ANIM = "reel"
    n_pets = int(r1.count())
    e_before = int(iv.count(EID))
    sent0 = len(E.sent(P1))
    Egg.CLICK.clear()     # (the 1 s click guard - a test presses faster than a player)
    hp.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % hp.tok)
    E.pump(P1)
    K.check(int(r1.count()) == n_pets + 1 and int(iv.count(EID)) == e_before - 1 and int(hp.view) in (1, 2), "HATCH Hatch: the pet is saved BEFORE any frame (pets +1, eggs %d -> %d), view %d" % (e_before, int(iv.count(EID)), int(hp.view)))
    if int(hp.view) == 2:
        K.check(False, "HATCH the reels did not start (the scheduler is missing in the stage?) - info %s" % hp.info)
    frames = 0
    cm1, _e1 = HT.build(hp, P1)
    s1 = dict((s, d) for ty, s, t, d in cm1 if ty == "Set")
    K.check("#SkyyHtA2.Slots" in s1 and "#SkyyHtB0.Slots" in s1 and "?" in str(s1.get("#SkyyHtBN.Text")), "HATCH view 1: two reels of 5 cells, the rarity reel waits (?): %s" % sorted(s1)[:12])
    told.clear()
    for _ in range(80):
        if int(hp.view) != 1:
            break
        hp.tick(Reel(hp, hp.gen, 0))
        frames += 1
        E.pump(P1)
    K.check(int(hp.view) == 2 and frames == int(hp.f1) - 1 + 1 + int(hp.f2) - 1 + 1, "HATCH the reels: %d steps (%d + %d frames + the result)" % (frames, int(hp.f1), int(hp.f2)))
    K.check(len([t for t in told if "You hatched a" in t]) == 1, "HATCH the result = ONE reveal line: %s" % told[:2])
    K.check(int(P_("PetHatchPage").FRAMES) >= 24, "HATCH ~25 frame updates (%d)" % int(P_("PetHatchPage").FRAMES))
    cm2, ev2 = HT.build(hp, P1)
    s2 = dict((s, d) for ty, s, t, d in cm2 if ty == "Set")
    K.check("#SkyyHtR.Slots" in s2 and "#SkyyHtT.Slots" in s2 and "Added to your pets" in str(s2.get("#SkyyHtRes1.Text")) and "#SkyyHtAgain" in [s for s, _t in ev2]
            and "#SkyyHtPets" in [s for s, _t in ev2], "HATCH view 2: portrait + rarity token, Added to your pets, Hatch another + Open pets")
    # strip check: the reel stopped on the result
    K.check(str(hp.s1[int(hp.f1) + 1]) == str(Egg.kindName(hp.kind)) or str(hp.n1[int(hp.f1) + 1]) == str(Egg.kindName(hp.kind)), "HATCH reel 1 stops on the hatched pet")
    K.check(str(hp.s2[int(hp.f2) + 1]) == str(Defs.token(int(hp.prar))), "HATCH reel 2 stops on its rarity")
    # Skip + Esc
    Egg.CLICK.clear()     # (the 1 s click guard - a test presses faster than a player)
    hp.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % hp.tok)
    E.pump(P1)
    told.clear()
    v_before = int(hp.view)
    hp.handleDataEvent(P1.ref, P1.st, '{"a":"skip"}')
    E.pump(P1)
    K.check(v_before == 1 and int(hp.view) == 2 and len([t for t in told if "You hatched a" in t]) == 1, "HATCH Skip mid-reel: the result + ONE reveal line (view %d -> %d, info %s, told %s)" % (v_before, int(hp.view), hp.info, told[:3]))
    Egg.CLICK.clear()     # (the 1 s click guard - a test presses faster than a player)
    hp.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % hp.tok)
    E.pump(P1)
    told.clear()
    g0 = int(hp.gen)
    hp.onDismiss(P1.ref, P1.st)
    hp.tick(Reel(hp, g0, 0))
    K.check(len([t for t in told if "You hatched a" in t]) == 1 and int(hp.gen) > g0, "HATCH Esc mid-reel: the reveal line at once, the reel stops (view %d, info %s, told %s)" % (int(hp.view), hp.info, told[:3]))
    # a disconnect mid-reel: the line waits for the next join (the tick's unseen)
    hp = HPage(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, hp)
    E.pump(P1)
    HT.build(hp, P1)
    Egg.CLICK.clear()
    hp.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % hp.tok)
    E.pump(P1)
    hz = str(hp.hid)
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = HT.jf(UniC.class_, "playersByUuid").get(UniC.get())
    byU.remove(u1)                                    # the player left: not in the Universe, the page is not theirs any more
    P1.pm.openCustomPage(P1.ref, P1.st, Page(P1.pr))
    E.pump(P1)
    told.clear()
    hp.tick(Reel(hp, hp.gen, 0))
    left = r1.get("hatch.unseen." + hz) is not None and not told
    byU.put(u1, P1.pr)
    Egg.unseen(u1, r1)
    K.check(left, "HATCH a player who left mid-reel: no line now, the reveal waits in the record")
    K.check(left and r1.get("hatch.unseen." + hz) is None and len([t for t in told if "You hatched a" in t]) == 1, "HATCH ... and comes as ONE line at the next join")
    # the skip toggle + quick
    P1.pm.openCustomPage(P1.ref, P1.st, hp)
    E.pump(P1)
    hp2 = HPage(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, hp2)
    E.pump(P1)
    HT.build(hp2, P1)
    hp2.handleDataEvent(P1.ref, P1.st, '{"a":"anim","i":"1"}')
    E.pump(P1)
    K.check(str(r1.get("hatch.skipAnim")) == "true", "HATCH the skip toggle is saved in the pet record")
    HT.build(hp2, P1)
    told.clear()
    Egg.CLICK.clear()     # (the 1 s click guard - a test presses faster than a player)
    hp2.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % hp2.tok)
    E.pump(P1)
    K.check(int(hp2.view) == 2 and len([t for t in told if "You hatched a" in t]) == 1, "HATCH skip animation on = straight to the result + the reveal (view %d, info %s, told %s)" % (int(hp2.view), hp2.info, told[:3]))
    hp2.handleDataEvent(P1.ref, P1.st, '{"a":"anim","i":"0"}')
    Cfg.HATCH_ANIM = "quick"
    HT.build(hp2, P1)
    Egg.CLICK.clear()     # (the 1 s click guard - a test presses faster than a player)
    hp2.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % hp2.tok)
    Cfg.HATCH_ANIM = "reel"
    K.check(int(hp2.view) == 2 and r1.get("hatch.skipAnim") is None, "HATCH pets.hatch.anim quick = the result at once; the toggle off again")
    t_old = str(hp2.tok)
    HT.build(hp2, P1)
    c0 = int(r1.count())
    Egg.CLICK.clear()     # (the 1 s click guard - a test presses faster than a player)
    hp2.handleDataEvent(P1.ref, P1.st, '{"a":"go","t":"%s"}' % t_old)
    K.check(int(r1.count()) == c0 and "page changed" in str(hp2.info), "HATCH a stale Hatch press hatches nothing")
    hp2.handleDataEvent(P1.ref, P1.st, '{"a":"pets"}')
    E.pump(P1)
    K.check(E.pg(P1) is not None and str(E.pg(P1).getClass().getName()) == PKG + "PetsPage", "HATCH Open pets opens the Pets page on top")
    # the debts of these hatches (in-session) clear 30 s later; the reveal lines are all shown
    now = int(JClass("java.lang.System").currentTimeMillis())
    Egg.debts(u1, r1, iv, now + 31000)
    K.check(not list(r1.keysWith("eggdebt.")) and not list(r1.keysWith("hatch.unseen.")), "HATCH every debt cleared after 30 s, every reveal shown")
    # PetEggGive into the real inventory (+ a full one)
    c_ = int(iv.count("Skyy_PetEgg_Farming_Common"))
    g = Gv(u1, "Skyy_PetEgg_Farming_Common", 2, "admin")
    g.run()
    K.check(bool(g.done) and int(g.added) == int(iv.count("Skyy_PetEgg_Farming_Common")) - c_ and (int(g.added) == 2 or any("could not give" in str(l) for l in list(Log.LINES))),
            "GIVE PetEggGive.run on the player's real inventory: counted (%d added, %d dropped; the stage has no item assets - nothing is ever silently lost: a warning names it)" % (int(g.added), int(g.dropped)))
    K.save()


# ======================================================================================================== LIVE: start twice on a copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, Log, Egg = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsLog"), P_("PetEgg")
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
        return [int(x) for x in Store.scanAll()], [int(x) for x in Store.fuseRecover()], [int(x) for x in Egg.recover()]
    sc1, fr1, hr1 = start()
    t1 = tree(home)
    ch = sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))
    K.check(not ch or all(k.startswith(("config-history", "migrations")) or k in ("config.properties", "config-changes.log") for k in ch),
            "LIVE start 1 writes nothing but a pending 0.3.x config update (0.4.0 has none): %s" % ch)
    K.check(sc1[2] == 0 and sc1[3] == 0 and fr1[0] == 0 and hr1[0] == 0, "LIVE every pet file read (files, pets, unreadable, dup %s), no cut-off fuse / hatch" % sc1)
    print("LIVE: %d pet files, %d pets; changed at start 1: %s" % (sc1[0], sc1[1], ch))
    sc2, fr2, hr2 = start()
    K.check(tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes NOTHING")
    K.save()


# ======================================================================================================== R031 / R030: older harness phases on this jar
# the 0.3.0 checks that drive the REMOVED per-pet Open page (Skyy 2026-10-16: "we can remove that whole menu, and just use the flavor text")
# - each behaviour is re-checked on the grid in STAGE (Fuse / Rebirth two presses, the pinned fodder, the sounds through slotDone)
_GONE = "0.4.0: the per-pet Open page (detail view + its Fuse / Rebirth buttons) is gone; the grid's click modes do it (STAGE)"
EXPECTED_R030 = {
    "PAGE detail: 13 rows": _GONE, "PAGE Fuse press 1 asks": _GONE, "PAGE Fuse press 2 fuses": _GONE, "PAGE a third press never fuses again": _GONE,
    "PAGE Rebirth: press 1 asks, press 2 rebirths": _GONE, "FIX2 a weaker pet arrived between the presses": _GONE,
    "FIX2 ... the next press fuses exactly the set the new question named": _GONE,
    "STATIC the page's slot clicks go through PetSnd.slotDone": "0.4.0: the grid's clicks go through PetsPage.act (every one still wraps PetSnd.slotDone - STAGE SND)",
    "STATIC exactly 5 slotDone calls": "0.4.0: 4 slotDone calls moved from handleDataEvent into PetsPage.act (STAGE SND counts them)",
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
        K.check(not unexp, "%s %s on the 0.4.0 jar: %d ok, unexpected fails %s" % (os.path.basename(script), ph, d_["ok"], unexp[:4]))
        for e in seen:
            K.notes.append("expected on 0.4.0: %s -> %s" % (e[:90], expected[e]))
        print("%s %s: %d ok, %d fail(s), %d of them expected" % (os.path.basename(script), ph, d_["ok"], len(d_["fails"]), len(d_["fails"]) - len(unexp)))
    K.save()


def run_r031(out, jar, scratch, home):
    run_old(out, jar, scratch, home, os.path.join(HERE, "test_skyypets_0.3.1.py"), ("sys",), {})


def run_r030(out, jar, scratch, home):
    run_old(out, jar, scratch, home, os.path.join(HERE, "test_skyypets_0.3.0.py"), ("sys", "snd"), EXPECTED_R030)


# ---- C: the non-class entries that may change: manifest + the egg assets (items, quality, icons, textures) + the lang file; none removed
_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    orig_eq = HK.Child.eq

    def eq(self, got, want, what):
        if what != "C: non-class entries changed":
            return orig_eq(self, got, want, what)
        za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
        gone = sorted(n for n in za.namelist() if n not in zb.namelist())
        ok = all(n == "manifest.json" or n == "Server/Languages/en-US/server.lang" or n.startswith("Server/Item/Items/SkyyPets/")
                 or n == "Server/Item/Qualities/Skyy_Pet_Mythic.json" or n.startswith("Common/Icons/ItemsGenerated/Skyy_PetEgg_")
                 or n.startswith("Common/Items/Pets/Skyy_PetEgg") or n.startswith("Common/Icons/ItemsGenerated/Skyy_PetIcon_") for n in got)
        n_items = len([n for n in got if n.startswith("Server/Item/Items/SkyyPets/")])
        return self.check(ok and not gone and "manifest.json" in got and n_items == 30 + 31 + 6,
                          "C: non-class entries changed = manifest + 67 item JSON + the Mythic quality + 36 egg art files + 29 build-time portraits + the lang file; none removed (%d changed)" % len(got))
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = orig_eq


HK.run_compare = _compare

if __name__ == "__main__":
    phases = [("egg", run_egg), ("stage", run_stage), ("live", run_live)]
    if "--no-old" not in sys.argv:
        phases += [("r031", run_r031), ("r030", run_r030)]
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE, "Skyy_SkyyPets"))
