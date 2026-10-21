"""Harness for SkyyClasses 0.1.43 (SKILL TREES 3 R3a, the SkyyClasses half: UpFx, the class-tree effects; tools/classes_0_1_43_patch.py +
tools/classes_0_1_43_upfx.py). Build first:
    python tools/classes_0_1_43_patch.py && python SkyyClasses/build_skyyclasses_0.1.43.py
    python SkyyClasses/test_skyyclasses_0.1.43.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/st3r3a/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.42 -> 0.1.43: exactly the planned members (EXPECT) + the new class UpFx
  X   exec     UpFx through a fake tree:fn:abil (the f.<code> list SkyyTrees 0.4.1 sends): the list parse + cache + ON, the ability parameter
               table (every a.<Ability>.<p> code lands on its ability), ranks; ctx() on real AbilCtx objects for every ability parameter and
               every cast-time capstone (Holy Land, Prism, Endless Fury, Fracture, Spider's Den, Thousand Palms, Riftmaw, Cataclysm, Arc Cascade,
               Overflow, Guardian reach, spell power, every-cooldown); stunAdd / shockStun (Rumble) / comboCap / flowMove / stars / range; the
               timed maps, budgets, gaps, wardPct; outAbil (Hunter's Mark, Critical Mass, Dead Eye, Fracture, Glacial Aegis, Prism ramp,
               Bloodthirst, the +80 % cap); cloneAt / cloneUp / later / takeDue; the Smite / blink codes are NOT SkyyClasses'; every engine hook
               with null / fake arguments returns quietly (out, inc, incLast, landed, tick, healAt, healed, zoneEnded, saved, impact, deflect,
               countered, flowEnded, cloakEnded, leech, spinPulse, bannerUp, rooted); tree:reads:SkyyClasses lists Class.fx.<every code>
  W   wiring   the bytecode of every hook site calls UpFx / its late stub (ctxFor, castAt0, hit, aim, beamJob, starJob, starTick, meteorImpact,
               healCast, zoneEnd, zoneEnd2, guard, flowAt, flowTick, flowEnd, inHit, counter, cloakEnd, shockJob, chainOne, palmRun,
               hitLanded2, spinTick, bannerAt, bannerTick, rootMob, wardArea, AbilShieldSys, AbilFrostSys, AbilTick, DamageLock.outHook, ClassQuit)
  ST  start twice on a scratch COPY of the live Skyy_SkyyClasses (every one-time update + load + the kit): nothing written either time
  AA  engine-access audit
NOT COVERED (UNVERIFIED in game): every effect on real mobs / players (the damage events, slows, pushes, stuns, the move / Mana regen
sources, Damage.BLOCKED order vs WieldingDamageReduction, the kill test in the Inspect group).
"""
import os, sys, json, shutil, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import trees_v3_data as V3D

VERSION, OLD = "0.1.43", "0.1.42"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3r3a", "cls")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyClasses")
ADDED = ["UpFx"]
CP_FIELDS = ("RUMBLES", "AEGISC", "AEGISS", "GRIPT", "GRIPW", "DOMAIN", "DOMAINK", "FURYT", "FURYM", "FURYS", "FURYB", "FURYV", "IMAGEH", "PALMSH",
             "LOTUS", "DEADEYE", "SPIDERS", "CATAN", "PRISMD", "PRISMR", "PRISMX", "GLACIALP", "MIRACLEB", "VIGIL", "HOLYO")   # fix round 2
CP_TEXT = ("rumbleStun=1.5,aegisCut=10,aegisSlow=40,gripRoot=2,gripWard=10,domain=60,domainKill=2,furyMax=30,furyMana=2,furyStamina=4,furyBack=5,"
           "furySlow=30,imageHit=30,palmsHit=40,lotus=200,deadEye=50,spiderStun=1.5,cataStars=3,prismDrain=4,prismRamp=2,prismMax=40,glacialHit=20,"
           "miracleBelow=20,vigil=30,holyOverlap=150")
EXPECT = {
    "Abil": ["+m upHealAt", "+m upHealed", "+m upImpact", "+m upOut", "+m upRange", "+m upSaved", "+m upStarAt", "+m upStars", "+m upZoneEnd",
             "~m aim", "~m bannerAt", "~m bannerTick", "~m beamJob", "~m castAt0", "~m chainOne", "~m cloakEnd", "~m counter", "~m ctxFor", "~m flowAt",
             "~m flowEnd", "~m flowTick", "~m guard", "~m healCast", "~m hit", "~m hitLanded2", "~m inHit", "~m meteorImpact", "~m palmRun",
             "~m rootMob", "~m shockJob", "~m spinTick", "+m upOverlap", "~m sanctPulse", "~m spinAt", "~m starJob", "~m starTick", "~m wardArea", "~m zoneEnd", "~m zoneEnd2"],
    "AbilFrostSys": ["~m handle"], "AbilShieldSys": ["~<clinit>", "~m handle"], "AbilTick": ["~m tick"], "ClassQuit": ["~m accept"], "DamageLock": ["~m outHook"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"], "SkyyClassesPlugin": ["~m setup"],   # the version text + tree:reads
    # fix round: the Server Setup rows abil.treeFx + ab.ClassTree.numbers (AbilCfg.TREE_FX / UX_NUMS -> AbilNum.UX_*) - the kit's row tables
    "AbilCfg": ["+f TREE_FX", "+f UX_NUMS", "+f CP_NUMS", "~<clinit>", "~m read"],   # fix round 2: + the Capstone numbers row
    "AbilNum": ["+f S_UX"] + ["+f UX_" + _x for _x in ("AEGISR", "AEGIST", "CLONEH", "CLONER", "CLONET", "CLONEX", "DMGCAP", "DRCAP", "GHOST", "GLACIAL",
                                                       "GRIPR", "LASTW", "MIRACLE", "NOMIND", "RUMBLE", "SLOWA", "SLOWW",
                                                       "LETHAL", "FOCUSN", "CHAING")]   # fix round 2
              + ["+f S_CP"] + ["+f CP_" + _x for _x in CP_FIELDS] + ["~<clinit>", "~m sync"],
    "CfgFile": ["~<clinit>"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "ClassCfg": ["~<clinit>"],
}
EXPECT["CfgRows"] = ["~<clinit>", "~m header"]


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def class_codes():
    codes, per = set(), {}
    for t in V3D.TREES:
        if t["kind"] != "class":
            continue
        for b in t["branches"]:
            for r in b["rows"]:
                f = r["free"]
                if f and f["hook"] and f["hook"][0] == "fx":
                    codes.add(f["hook"][1])
                for u in r["ups"]:
                    for c, v in V3D.fx_codes(u):
                        if V3D.fx_owner(c) == "SkyyClasses":
                            codes.add(c)
                            per.setdefault(c, v)
    return sorted(codes), per


def jpype_long_arr(xs):
    from jpype import JArray, JLong
    return JArray(JLong)(xs)


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    UF, AD, AB, AC, CC, AS, CTX = J("UpFx"), J("AbilDefs"), J("Abil"), J("AbilCfg"), J("ClassCfg"), J("AbilStore"), J("AbilCtx")
    UUID = JClass("java.util.UUID")
    Ref = JClass("com.hypixel.hytale.component.Ref")
    br = CC.bridge()
    codes, per = class_codes()
    K.eq([str(x) for x in UF.CODES], codes, "X UpFx.CODES = every SkyyClasses code of tools/trees_v3_data.py")
    for c in ("blinkStep", "smiteReach", "hp", "mana", "stam", "mreg", "sreg"):
        K.check(int(UF.idx(c)) == -1, "X %s is not SkyyClasses' code" % c)
    ab = [str(x) for x in AD.IDS]
    bad = [c for c in codes if c.startswith("a.") and int(UF.AP[ab.index(c.split(".")[1]) * int(UF.NP) + list(V3D.FX_AP).index(c.split(".")[2])]) != codes.index(c)]
    K.check(not bad, "X every a.<Ability>.<p> code sits at its ability + parameter in UpFx.AP %s" % bad[:4])
    # ---- the list parse (the text SkyyTrees 0.4.1's tree:fn:abil answers) + the cache + ON
    K.check(UF.vec("v3,A1,A2") is None and UF.vec(None) is None, "X a list without f. entries = no codes (null)")
    csv = "v3,A1,A2,f.drMelee=20,f.a.ShieldShockwave.stun=0.5,f.a.ShieldShockwave.rad=2,f.wardBoost=8,f.nope=5,f.dmgFocus=bad,f.echo5=80"
    v = UF.vec(csv)
    K.check(v is not None and bool(UF.ON), "X a list with codes -> the vector + ON")
    K.eq((float(UF.g(v, UF.idx("drMelee"))), float(UF.g(v, UF.idx("wardBoost"))), float(UF.g(v, UF.idx("dmgFocus")))), (20.0, 8.0, 0.0),
         "X the parse: known codes summed, an unknown code / a bad number skipped")
    Sys = JClass("java.lang.System")
    K.check(int(Sys.identityHashCode(UF.vec(csv))) == int(Sys.identityHashCode(v)), "X the vector is cached per list text")
    shock = int(AD.find("ShieldShockwave"))
    K.eq((float(UF.ap(v, shock, 5)), float(UF.ap(v, shock, 1)), float(UF.ap(v, int(AD.find("Meteor")), 5))), (0.5, 2.0, 0.0), "X ap(): the ability parameter of the right ability only")
    K.eq((int(UF.ranks(v, UF.idx("echo5"))), int(UF.ranks(v, UF.idx("drMelee")))), (2, 5), "X ranks = total / per rank (Echo 80 / 40 = 2; Iron Skin 20 / 4 = 5)")
    # ---- a fake tree:fn:abil (SkyyTrees 0.4.1) for of(u)
    u = UUID.fromString("12345678-2222-3333-4444-555555555555")
    ANS = ["v3,A1"]

    @JImplements("java.util.function.Function")
    class Abil(object):
        @JOverride
        def apply(self, a):
            return ANS[0]
    br.put("tree:fn:abil", Abil())

    def tree(s):
        ANS[0] = s
        AS.TREEC.clear()
    tree("v3,A1,f.wardBoost=10")
    K.check(abs(float(UF.wardPct(u, 3.0)) - 3.3) < 1e-9, "X wardPct: Ward +10 % -> a 3 % ward is 3.3 %")
    # ---- ctx(): the cast-time numbers on real AbilCtx objects
    def ctx(ability, cls, lst, echo=False):
        c = CTX()
        c.ai = int(AD.find(ability))
        c.cls = cls
        c.tree = lst
        c.u = u
        c.echo = echo
        UF.ctx(c)
        return c
    c = ctx("Toxin", "Assassin", "v3,f.a.Toxin.pow=20,f.a.Toxin.dur=3,f.a.Toxin.cost=24,f.a.Toxin.slow=12")
    K.check(abs(float(c.treeMain) - 1.2) < 1e-9 and abs(float(c.durAdd) - 3.0) < 1e-9 and abs(float(c.costMult) - 0.76) < 1e-9 and float(c.cdMult) == 1.0,
            "X ctx Toxin: +20 %% power, +3 s, -24 %% cost (%s %s %s)" % (c.treeMain, c.durAdd, c.costMult))
    c = ctx("HuntersNet", "Archer", "v3,f.a.HuntersNet.cd=18,f.xSpider=1,f.a.HuntersNet.pow=9")
    K.check(abs(float(c.cdMult) - 0.82) < 1e-9 and abs(float(c.treeMain) - 1.09) < 1e-9 and float(c.radTree) == 0.0, "X ctx Hunter's Net: Lockdown -18 %, Volley +9 % (FIX 2: Spider's Den = a spare charge, no cooldown cut)")
    c = ctx("Meteor", "Mage", "v3,f.spellPow=12,f.cdAll=8,f.xCataclysm=1")
    K.check(abs(float(c.treeMain) - 1.12) < 1e-9 and abs(float(c.cdMult) - 0.92) < 1e-9 and abs(float(c.radTree) - float(AC.M_RADIUS)) < 1e-9,
            "X ctx Meteor: Astral Focus +12 %, Swift Casting -8 %, Cataclysm doubles the radius (+M_RADIUS)")
    UF.MANAF.put(u, JClass("java.lang.Double").valueOf(1.0))
    c = ctx("Starfall", "Mage", "v3,f.overflow=12")
    K.check(abs(float(c.treeMain) - 1.12) < 1e-9, "X ctx Overflow: at full Mana +12 %")
    UF.MANAF.put(u, JClass("java.lang.Double").valueOf(0.5))
    c = ctx("Starfall", "Mage", "v3,f.overflow=12")
    K.check(float(c.treeMain) == 1.0, "X ctx Overflow: not at full Mana = nothing")
    c = ctx("Sanctuary", "Priest", "v3,f.xHolyLand=1,f.a.Sanctuary.cost=24")
    K.check(float(c.treeMain) == 1.0 and float(c.durMult) == 1.0 and abs(float(c.costMult) - 0.76) < 1e-9, "X FIX 2 ctx Holy Land: no stat tweak any more (2 charges + the overlap instead)")
    c = ctx("ArcaneBeam", "Mage", "v3,f.xPrism=1")
    K.check(abs(float(c.durMult) - 2.0) < 1e-9, "X ctx Prism Overload: the beam lasts 2x")
    c = ctx("Whirlwind", "Berserker", "v3,f.xFury=1,f.a.Whirlwind.pow=32")
    K.check(float(c.durMult) == 1.0 and abs(float(c.treeMain) - 1.32) < 1e-9 and bool(UF.furyOn(c)), "X FIX 2 ctx Endless Fury: a toggle (furyOn), no x2 time; Haste +32 %")
    K.check(not bool(UF.furyOn(ctx("Whirlwind", "Berserker", "v3,f.xFury=1", echo=True))) and not bool(UF.furyOn(ctx("Whirlwind", "Berserker", "v3,f.a.Whirlwind.pow=4"))),
            "X FIX 2 furyOn: never on an echo spin, never without the capstone")
    c = ctx("Sunder", "Spellblade", "v3,f.xFracture=1,f.a.Sunder.dur=6")
    K.check(abs(float(c.cdMult) - 0.5) < 1e-9 and abs(float(c.durAdd) - 6.0) < 1e-9, "X ctx Fracture: Sunder's cooldown halved; +6 s")
    c = ctx("RiftCleave", "Spellblade", "v3,f.xRiftmaw=1")
    K.check(abs(float(c.echoPct) - 0.6) < 1e-9, "X ctx Riftmaw: Rift Cleave echoes at 60 %")
    c = ctx("RiftCleave", "Spellblade", "v3,f.xRiftmaw=1", echo=True)
    K.check(float(c.echoPct) == 0.0, "X ctx Riftmaw: never on an echo")
    c = ctx("SacredHeal", "Priest", "v3,f.a.SacredHeal.radPct=16,f.a.SacredHeal.hot=9")
    K.check(abs(float(c.radTree) - float(AC.S_RADIUS) * 0.16) < 1e-9 and abs(float(c.hotAdd) - 9.0) < 1e-9, "X ctx Sacred Heal: Long Reach +16 % radius, Renewal +9 % HoT")
    c = ctx("GuardianSpirit", "Priest", "v3,f.spiritReach=4")
    K.check(abs(float(c.radAdd) - 4.0) < 1e-9, "X ctx Guardian Spirit: Follow reach +4 (radAdd, what guard() reads)")
    c = ctx("CloakFirstStrike", "Assassin", "v3,f.a.CloakFirstStrike.pow=15")
    K.check(abs(float(c.treeMain) - 1.15) < 1e-9, "X ctx Ambush: First Strike +15 %")
    # Thousand Palms: a live Flowing Form with 10 stacks -> Palm Strike's cooldown x0.1
    now = int(JClass("java.lang.System").currentTimeMillis())
    Z = J("AbilZone")
    fz = Z(8, u, 0.0, 0.0, 0.0, 3.0, now, now + 60000)
    fz.ai = int(AD.FFORM)
    fz.ring = JClass("long[]")(18)
    for i in range(12):
        fz.ring[i] = now
    AS.FLOWS.put(u, fz)
    K.eq(int(UF.flowStacks(u, now)), 12, "X flowStacks reads the live Flowing Form (12)")
    c = ctx("PalmStrike", "Monk", "v3,f.xPalms=1")
    K.check(abs(float(c.cdMult) - 0.1) < 1e-9, "X ctx Thousand Palms: 10+ combo -> Palm Strike cooldown x0.1")
    fz.cx = ctx("FlowingForm", "Monk", "v3,f.flowMove=10,f.comboCap=4")
    K.eq((int(UF.flowMove(fz)), int(UF.comboCap(fz.cx))), (10, 4), "X flowMove (Flowing Form Haste) + comboCap (Flurry)")
    AS.FLOWS.remove(u)
    # Arc Cascade: full Momentum at the cast -> +2 blocks + the mark the cast hook reads
    AB.momAdd(u, 40, now)
    K.check(int(AB.momN(u, now)) > 0, "X Momentum given (%d)" % int(AB.momN(u, now)))
    c = ctx("RiftCleave", "Spellblade", "v3,f.xCascade=1")
    K.check(abs(float(c.radTree) - 2.0) < 1e-9 and UF.CASC.get(u) is not None, "X ctx Arc Cascade at full Momentum: +2 blocks + marked")
    # the per-ability extra stun, Rumble's floor, stars, the range
    sc = ctx("ShieldShockwave", "Warrior", "v3,f.a.ShieldShockwave.stun=0.5")
    K.check(abs(float(UF.stunAdd(sc, shock)) - 0.5) < 1e-9 and abs(float(UF.shockStun(sc, 0.8)) - 1.3) < 1e-9, "X Shockwave Duration +0.5 s")
    UF.RUMB.set(JClass("java.lang.Boolean").TRUE)
    K.check(abs(float(UF.shockStun(sc, 0.2)) - 1.5) < 1e-9, "X Rumble's free Shockwave stuns at least 1.5 s (Capstone numbers rumbleStun)")
    seen = []
    import threading

    def _other():
        seen.append(float(UF.shockStun(sc, 0.2)))
    tt = threading.Thread(target=_other)
    tt.start()
    tt.join()
    K.check(bool(seen) and abs(seen[0] - 0.7) < 1e-9, "X FIX 2 Rumble's flag is per thread: another world's Shockwave in the same moment keeps its own stun (%s)" % seen)
    UF.RUMB.remove()
    K.check(abs(float(UF.shockStun(sc, 0.2)) - 0.7) < 1e-9, "X FIX 2 ... and off again after the free Shockwave")
    K.eq(int(UF.stars(ctx("Starfall", "Mage", "v3,f.a.Starfall.stars=4"))), 4, "X Split +4 stars")
    K.eq(int(UF.stars(ctx("Starfall", "Mage", "v3,f.a.Starfall.stars=4", echo=True))), 0, "X no extra stars on an echo")
    CTX.put(ctx("Meteor", "Mage", "v3,f.rangeAll=18"))
    K.check(abs(float(UF.range()) - 1.18) < 1e-9, "X Focusing Lens: spell range x1.18 (the cast's context)")
    CTX.put(ctx("SacredHeal", "Priest", "v3,f.rangeAll=18"))
    K.check(float(UF.range()) == 1.0, "X range: only a Mage cast")
    CTX.put(None)
    # ---- the timed maps, budgets, gaps
    t1, t2 = Ref(None, 1), Ref(None, 2)
    UF.timedPut(UF.VULN, t1, now + 5000, 8.0)
    UF.timedPut(UF.VULN, t1, now + 9000, 4.0)
    K.eq(float(UF.timed(UF.VULN, t1, now)), 8.0, "X timedPut keeps the stronger running value")
    UF.timedPut(UF.VULN, t1, now + 9000, 12.0)
    K.eq(float(UF.timed(UF.VULN, t1, now)), 12.0, "X a stronger value replaces it")
    K.eq(float(UF.timed(UF.VULN, t1, now + 10000)), 0.0, "X expired = 0 (and removed)")
    K.check([bool(UF.take("k", 2, 500, now)) for _ in range(3)] == [True, True, False] and bool(UF.take("k", 2, 500, now + 600)), "X take(): 2 per window, a new window")
    K.check(bool(UF.gap(UF.LASTW, u, 60000, now)) and not bool(UF.gap(UF.LASTW, u, 60000, now + 1000)) and bool(UF.gap(UF.LASTW, u, 60000, now + 61000)), "X gap(): Last Ward once per 60 s")
    UF.LASTW.remove(u)
    K.eq(list(UF.copy(JClass("double[]")([1.0, 2.0]))), [1.0, 2.0], "X copy()")
    # ---- outAbil: the target-side + conditional ability bonuses
    tree("v3,A1,f.comboSpell=10,f.xDeadEye=1,f.pinVuln=8,f.xFracture=1,f.xGlacial=1,f.xPrism=1,f.bigHitBuff=6,f.dmgElite=5")
    K.eq(float(UF.outAbil(None, None, u, "Meteor", now)), 1.0, "X outAbil without a target = 1")
    K.eq(float(UF.outAbil(None, t2, u, "UpChain", now)), 1.0, "X outAbil of a proc hit = 1 (no doubling)")
    K.check(abs(float(UF.outAbil(None, t2, u, "Meteor", now)) - 1.0) < 1e-9, "X outAbil Meteor on a fresh target = 1")
    K.check(abs(float(UF.outAbil(None, t2, u, "Starfall", now)) - 1.10) < 1e-9, "X Critical Mass: a 2nd different spell within 3 s +10 %")
    UF.timedPut(UF.RT, t2, now + 3000, 1.0)
    K.check(abs(float(UF.outAbil(None, t2, u, "RapidFire", now + 10)) - 1.6) < 1e-9 and float(UF.timed(UF.VULN, t2, now + 10)) == 8.0,
            "X Dead Eye: Rapid Fire +50 % on a rooted target (+ Critical Mass 10) and it keeps Hunter's Mark (8)")
    K.check(abs(float(UF.outAbil(None, t2, u, "RapidFire", now + 20)) - 1.58) < 1e-9, "X ... the Mark counts for every ability hit after (+50 +8)")
    UF.VULN.clear()
    UF.RT.clear()
    UF.SPELLS.clear()
    AS.SUNDER.put(t2, JClass("double[]")([float(now + 5000), 10.0, 0.0, 0.0, 0.0, 0.0]))
    K.check(abs(float(UF.outAbil(None, t2, u, "ShatteringArc", now)) - 1.5) < 1e-9, "X Fracture: Shattering Arc +50 % on a Sundered target")
    AS.SUNDER.clear()
    UF.SPELLS.clear()
    AS.FROZEN.put(t2, JClass("long[]")([now + 3000, now + 3000]))
    K.check(abs(float(UF.outAbil(None, t2, u, "Meteor", now)) - 1.2) < 1e-9, "X Glacial Aegis: frozen enemies take +20 %")
    AS.FROZEN.clear()
    UF.SPELLS.clear()
    bj = J("AbilJob")(6, now, u, "ArcaneBeam", 0.0, 0.0, 0.0, 0.0, 1.0)
    bj.start = now - 5000
    AS.CHAN.put(u, bj)
    K.check(abs(float(UF.outAbil(None, t2, u, "ArcaneBeam", now)) - 1.10) < 1e-9, "X Prism Overload: 5 s held = +10 %")
    bj.start = now - 60000
    UF.SPELLS.clear()
    K.check(abs(float(UF.outAbil(None, t2, u, "ArcaneBeam", now)) - 1.40) < 1e-9, "X ... capped at +40 %")
    AS.CHAN.clear()
    UF.SPELLS.clear()
    UF.timedPut(UF.BUFF, u, now + 4000, 70.0)
    UF.timedPut(UF.VULN, t2, now + 4000, 70.0)
    K.check(abs(float(UF.outAbil(None, t2, u, "Meteor", now)) - 1.8) < 1e-9, "X every bonus together is capped at +80 %")
    UF.BUFF.clear()
    UF.VULN.clear()
    # ---- clones, laters
    tree("v3,A1,f.ShadowClone=1,f.cloneSplit=2,f.cloneDur=2,f.cloneMirror=10")
    vv = UF.of(u)
    UF.cloneAt(u, vv, JClass("double[]")([10.0, 64.0, 20.0]), 20.0, now)
    cl = UF.CLONES.get(u)
    K.check(cl is not None and int(cl.size()) == 3 and abs(float(cl.get(0)[3]) - (now + 5000)) < 1 and abs(float(cl.get(0)[4]) - 12.0) < 1e-9 and abs(float(cl.get(1)[4]) - 8.0) < 1e-9,
            "X Shadow Clone + Split 2: 3 clones, 3 + 2 s, strike 60 % / 40 % of a hit")
    # FIX ROUND 1 (Server Setup): the class-tree numbers row -> AbilNum.UX_* (cloneTime / cloneHit / cloneExtra used by cloneAt)
    AN = J("AbilNum")
    K.eq(str(AC.UX_NUMS), "drCap=50,dmgCap=80,slowAbility=3,slowWeapon=2,cloneTime=3,cloneHit=60,cloneExtra=40,cloneLure=6,lastWard=60,ghost=8,"
         "noMind=6,rumble=5,aegisHold=30,aegisRadius=6,gripRadius=8,glacial=10,miracle=8,lethal=50,focusStacks=5,chainGap=0.5", "X FIX the Class tree numbers row default (every first-pass number)")
    K.eq(str(AC.CP_NUMS), CP_TEXT, "X FIX 2 the Capstone numbers row default (every capstone number)")
    K.eq((float(AN.CP_FURYT), float(AN.CP_HOLYO), float(AN.CP_SPIDERS), float(AN.UX_LETHAL), float(AN.UX_CHAING)), (30.0, 150.0, 1.5, 50.0, 0.5),
         "X FIX 2 the new numbers read their defaults")
    AC.CP_NUMS = "holyOverlap=999,furyMax=12,lotus=-5"
    AN.sync()
    K.eq((float(AN.CP_HOLYO), float(AN.CP_FURYT), float(AN.CP_LOTUS), float(AN.CP_DEADEYE)), (300.0, 12.0, 0.0, 50.0),
         "X FIX 2 an edited Capstone row: read, clamped (holyOverlap 300, lotus 0), a missing key = default")
    AC.CP_NUMS = CP_TEXT
    AN.sync()
    old_nums = AC.UX_NUMS
    AC.UX_NUMS = "cloneTime=5,cloneHit=100,cloneExtra=50,dmgCap=9999,lastWard=0"
    AN.sync()
    K.eq((float(AN.UX_CLONET), float(AN.UX_CLONEH), float(AN.UX_CLONEX), float(AN.UX_DMGCAP), float(AN.UX_LASTW), float(AN.UX_DRCAP)),
         (5.0, 100.0, 50.0, 500.0, 1.0, 50.0), "X FIX an edited row: the keys read, out-of-range clamped (dmgCap 500, lastWard 1 s), a missing key = default")
    UF.CLONES.clear()
    UF.cloneAt(u, vv, JClass("double[]")([10.0, 64.0, 20.0]), 20.0, now)
    cl = UF.CLONES.get(u)
    K.check(abs(float(cl.get(0)[3]) - (now + 7000)) < 1 and abs(float(cl.get(0)[4]) - 20.0) < 1e-9 and abs(float(cl.get(1)[4]) - 10.0) < 1e-9,
            "X FIX cloneAt uses the row: 5 + 2 s, 100 % / 50 %")
    AC.UX_NUMS = old_nums
    AN.sync()
    K.eq(float(AN.UX_CLONET), 3.0, "X FIX back to the default text = the defaults")
    UF.CLONES.clear()
    UF.cloneAt(u, vv, JClass("double[]")([10.0, 64.0, 20.0]), 20.0, now)
    # FIX ROUND 1: the master switch abil.treeFx - off = no codes at all (every hook's vec() is null)
    K.check(bool(AC.TREE_FX), "X FIX Class tree effects default ON")
    AC.TREE_FX = False
    UF.VC.clear()
    K.check(UF.of(u) is None and UF.vec("v3,A1,f.drMelee=20") is None, "X FIX Class tree effects OFF = no codes")
    AC.TREE_FX = True
    K.check(UF.of(u) is not None, "X FIX ... ON again = the codes")
    K.check(bool(UF.cloneUp(u, now)) and not bool(UF.cloneUp(u, now + 6000)), "X cloneUp while a clone stands")
    # FIX ROUND 2: the spare charge (Spider's Den / Holy Land), Holy Land's overlap, Endless Fury's end, the quit
    net, sanct, whirl = int(AD.find("HuntersNet")), int(AD.find("Sanctuary")), int(AD.find("Whirlwind"))
    UF.CHG.clear()
    K.check(bool(UF.spare(u, net, "v3,A1,f.xSpider=1", now)) and bool(UF.spare(u, sanct, "v3,A1,f.xHolyLand=1", now)), "X FIX 2 a spare charge is ready at first")
    K.check(not bool(UF.spare(u, net, "v3,A1,f.xHolyLand=1", now)) and not bool(UF.spare(u, sanct, "v3,A1,f.xSpider=1", now))
            and not bool(UF.spare(u, whirl, "v3,A1,f.xSpider=1,f.xHolyLand=1", now)), "X FIX 2 ... only for the capstone's own ability")
    K.eq(int(UF.spareUse(u, net, now, 18000)), now + 18000, "X FIX 2 spareUse: the spare is back one cooldown later")
    K.check(not bool(UF.spare(u, net, "v3,A1,f.xSpider=1", now + 17999)) and bool(UF.spare(u, net, "v3,A1,f.xSpider=1", now + 18000))
            and bool(UF.spare(u, sanct, "v3,A1,f.xHolyLand=1", now)), "X FIX 2 ... used = not ready until then; the other slot untouched")
    K.eq(float(UF.overlap(None, None, None)), 1.0, "X FIX 2 overlap with nothing = full heal")
    K.eq(str(UF.furyEnd(None, now)), "none", "X FIX 2 furyEnd(null) = nothing")
    K.check(UF.furyOff(None, u, "k", now) is None, "X FIX 2 furyOff without a toggled spin = the cast goes on")
    UF.NOVA.put(u, JClass("double[]")([1.0, 2.0, 3.0, 4.0]))
    UF.CHG.put(u, jpype_long_arr([1, 2]))
    UF.quit(u)
    K.check(UF.NOVA.get(u) is None and UF.CHG.get(u) is None, "X FIX 2 quit drops a waiting Arc Cascade nova + the spare charges")
    UF.later(u, 1, now + 2000)
    lst = UF.LATER.get(u)
    K.eq(int(UF.takeDue(lst, now).size()), 0, "X a later action waits")
    K.eq(int(UF.takeDue(lst, now + 2000).size()), 1, "X ... and is due at its time (taken once)")
    # ---- every engine hook returns quietly on null / fake arguments (the world-thread code paths start; the engine parts are UNVERIFIED here)
    quiet = []
    calls = [("out", lambda: UF.out(None, None, None, None, u, now)), ("inc", lambda: UF.inc(None, None, None, None, now)),
             ("incLast", lambda: UF.incLast(None, None, None, None, now)), ("landed", lambda: UF.landed(None, None, None, now)),
             ("tick", lambda: UF.tick(None, None, now)), ("healAt", lambda: UF.healAt(None, None, u, None)),
             ("healed", lambda: UF.healed(None, None, u, None, None, None, None, None, 0.0)), ("zoneEnded", lambda: UF.zoneEnded(None, None)),
             ("saved", lambda: UF.saved(None, None, u, None, None, None, None, 0, "k", now)), ("impact", lambda: UF.impact(None, None, None, 0)),
             ("deflect", lambda: UF.deflect(None, None, None, 1.0, u)), ("countered", lambda: UF.countered(None, None, u, None, None, now)),
             ("flowEnded", lambda: UF.flowEnded(None, None, None)), ("cloakEnded", lambda: UF.cloakEnded(None, None, None)),
             ("leech", lambda: UF.leech(None, None, u, 0.0)), ("spinPulse", lambda: UF.spinPulse(None, None, None, 0)), ("furyUp", lambda: UF.furyUp(None, None, now)),
             ("overlap", lambda: UF.overlap(None, None, None)), ("spareUse", lambda: UF.spareUse(None, 0, now, 0)),
             ("bannerUp", lambda: UF.bannerUp(None, None)), ("rooted", lambda: UF.rooted(None, now)), ("quit", lambda: UF.quit(u)),
             ("starAt", lambda: UF.starAt(None, None, None, 0.0, 0.0, 0.0)), ("debuffs", lambda: UF.debuffs(None, now)),
             ("movePost", lambda: UF.movePost(u, 0.0)), ("mregPost", lambda: UF.mregPost(u, 0.0))]
    for nm, fn in calls:
        try:
            fn()
        except Exception as e:
            quiet.append("%s: %s" % (nm, str(e)[:120]))
    K.check(not quiet, "X %d engine hooks return quietly on null arguments %s" % (len(calls), quiet))
    # Warlord's Domain on a banner zone
    bz = Z(18, u, 0.0, 0.0, 0.0, 6.0, now, now + 15000)
    bz.pct = 1.0
    UF.bannerUp(bz, ctx("WarlordsBanner", "Berserker", "v3,f.xDomain=1"))
    K.check(bool(UF.domain(bz)) and bool(bz.follow) and abs(float(bz.pct) - 0.6) < 1e-9 and int(bz.until) - now > 3000000, "X Warlord's Domain: follows, 60 %, held for an hour")
    UF.rooted(t1, now + 2000)
    K.check(float(UF.timed(UF.RT, t1, now)) == 1.0, "X rooted(): the rooted map (Thick Hide, Clinch, Dead Eye)")
    # the move source post through the bridge (movement protocol)
    UF.movePost(u, 0.07)
    mv = br.get("move:" + str(u))
    K.check(mv is not None and abs(float(mv.get("classes.tree").get("speed")) - 0.07) < 1e-6 and str(mv.get("classes.tree").get("layer")) == "flat",
            "X the move source classes.tree (flat, +7 %)")
    UF.movePost(u, 0.0)
    K.check(mv.get("classes.tree") is None, "X 0 removes our entry")
    # the reader contract: tree:reads:SkyyClasses lists every code (SkyyTrees sells an fx upgrade only then)
    with zipfile.ZipFile(jar) as z:
        raw = z.read([n for n in z.namelist() if n.endswith("/SkyyClassesPlugin.class")][0])
    miss = [c for c in codes if ("Class.fx." + c).encode() not in raw]
    K.check(not miss and b"Class.v3mods" in raw, "X tree:reads:SkyyClasses lists Class.fx.<code> for all %d codes %s" % (len(codes), miss[:4]))
    # FIX ROUND 1: AbilShieldSys runs AFTER WieldingDamageReduction (it sets Damage.BLOCKED, which the block effects read)
    SH = J("AbilShieldSys")
    K.check(any(str(x).endswith("DamageSystems$WieldingDamageReduction") for x in SH.DROPS), "X FIX AbilShieldSys.DROPS names WieldingDamageReduction")
    dep = SH(True).getDependencies()
    import re as _re
    dn = _re.findall(r"DamageSystems\$(\w+)", str(dep))
    # (outside a running server the engine's filter systems cannot initialise their QUERY - NoClassDefFoundError - so only the ones that load
    # here become dependencies; the real server loads all five, the 0.1.42 FIX ROUND path. Each name = one try/catch AFTER in the constructor)
    K.check(int(dep.size()) >= 1 and "ArmorDamageReduction" in dn and str(dep).count("AFTER") == int(dep.size()) and int(dep.size()) <= 5,
            "X FIX the ordered AbilShieldSys builds its AFTER dependencies from ADR + DROPS (here %d: %s; the rest need the running engine)" % (int(dep.size()), dn))
    K.eq(len(SH.DROPS), 4, "X FIX DROPS = the 3 filters + WieldingDamageReduction")
    # FIX ROUND 3: the mob-keyed marks (KMARK, NETTED) stay at most 2048 entries
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    Long = JClass("java.lang.Long")
    now2 = int(Sys.currentTimeMillis())
    km = CHM()
    for i in range(2049):
        km.put("m%d" % i, jpype_long_arr([now2 - 1, 1, 2]))
    km.put("fresh", jpype_long_arr([now2 + 5000, 1, 2]))
    UF.capMob(km, now2)
    K.check(int(km.size()) == 1 and km.get("fresh") is not None, "X FIX capMob: past 2048 the expired kunai marks go, a live one stays (%d)" % int(km.size()))
    nm = CHM()
    for i in range(2049):
        nm.put("n%d" % i, Long(now2 - 7000))
    nm.put("recent", Long(now2 - 1000))
    UF.capMob(nm, now2)
    K.check(int(nm.size()) == 1 and nm.get("recent") is not None, "X FIX capMob: net times older than 6 s go, a recent one stays")
    sm = CHM()
    sm.put("a", Long(now2 - 99999))
    UF.capMob(sm, now2)
    K.check(int(sm.size()) == 1, "X FIX capMob: under the cap nothing is touched")
    for i in range(2100):
        sm.put("x%d" % i, Long(now2))
    UF.capMob(sm, now2)
    K.check(int(sm.size()) == 0, "X FIX capMob: all still live past the cap = cleared (never unbounded)")
    K.save()


def run_wire(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)

    def calls(cls, meth):
        c = cp.get(PKG + cls)
        out_ = set()
        for m in c.getDeclaredMethods():
            if str(m.getName()) != meth:
                continue
            ci = m.getMethodInfo().getCodeAttribute().iterator()
            cpl = m.getMethodInfo().getConstPool()
            while ci.hasNext():
                pos = ci.next()
                op = ci.byteAt(pos)
                if op in (0xb6, 0xb8, 0xb7, 0xb9):
                    idx = ci.u16bitAt(pos + 1)
                    out_.add(str(cpl.getMethodrefClassName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." +
                             str(cpl.getMethodrefName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefName(idx)))
        return out_
    want = [("Abil", "ctxFor", "UpFx.ctx"), ("Abil", "castAt0", "UpFx.cast"), ("Abil", "hit", "Abil.upOut"), ("Abil", "aim", "Abil.upRange"),
            ("Abil", "beamJob", "Abil.upRange"), ("Abil", "starJob", "Abil.upStars"), ("Abil", "starTick", "Abil.upStarAt"), ("Abil", "meteorImpact", "Abil.upImpact"),
            ("Abil", "healCast", "Abil.upHealAt"), ("Abil", "healCast", "Abil.upHealed"), ("Abil", "zoneEnd", "Abil.upZoneEnd"), ("Abil", "zoneEnd2", "Abil.upZoneEnd"),
            ("Abil", "guard", "Abil.upSaved"), ("Abil", "flowAt", "UpFx.comboCap"), ("Abil", "flowTick", "UpFx.flowMove"), ("Abil", "flowEnd", "UpFx.flowEnded"),
            ("Abil", "inHit", "UpFx.deflect"), ("Abil", "counter", "UpFx.countered"), ("Abil", "cloakEnd", "UpFx.cloakEnded"), ("Abil", "shockJob", "UpFx.shockStun"),
            ("Abil", "chainOne", "UpFx.stunAdd"), ("Abil", "palmRun", "UpFx.stunAdd"), ("Abil", "hitLanded2", "UpFx.leech"), ("Abil", "spinTick", "UpFx.spinPulse"),
            ("Abil", "bannerAt", "UpFx.bannerUp"), ("Abil", "bannerTick", "UpFx.domain"), ("Abil", "rootMob", "UpFx.rooted"), ("Abil", "wardArea", "UpFx.wardPct"),
            ("Abil", "upOut", "UpFx.outAbil"), ("Abil", "upStars", "UpFx.stars"), ("Abil", "upStarAt", "UpFx.starAt"), ("Abil", "upRange", "UpFx.range"),
            ("Abil", "upHealAt", "UpFx.healAt"), ("Abil", "upHealed", "UpFx.healed"), ("Abil", "upZoneEnd", "UpFx.zoneEnded"), ("Abil", "upSaved", "UpFx.saved"),
            ("Abil", "upImpact", "UpFx.impact"), ("AbilShieldSys", "handle", "UpFx.inc"), ("AbilShieldSys", "handle", "UpFx.incLast"),
            ("AbilFrostSys", "handle", "UpFx.landed"), ("AbilTick", "tick", "UpFx.tick"), ("DamageLock", "outHook", "UpFx.out"), ("ClassQuit", "accept", "UpFx.quit"),
            # fix round 2
            ("Abil", "castAt0", "UpFx.furyOff"), ("Abil", "castAt0", "UpFx.spare"), ("Abil", "castAt0", "UpFx.spareUse"), ("Abil", "castAt0", "UpFx.furyOn"),
            ("Abil", "spinAt", "UpFx.furyUp"), ("Abil", "spinTick", "UpFx.furyEnd"), ("Abil", "sanctPulse", "Abil.upOverlap"), ("Abil", "upOverlap", "UpFx.overlap")]
    miss = [w for w in want if w[2] not in calls(w[0], w[1])]
    K.check(not miss, "W every hook site calls its UpFx method (%d sites) %s" % (len(want), miss))
    cs = calls("UpFx", "clones")
    K.check("UpFx.cloneStrike" in cs and "Abil.burst" not in cs, "W FIX 2 a clone strikes one enemy (cloneStrike), never Abil.burst (no AoE for the Assassin)")
    K.check("Abil.burst" not in calls("UpFx", "cloneStrike") and "Abil.hit" in calls("UpFx", "cloneStrike"), "W FIX 2 cloneStrike = one Abil.hit")
    K.check("UpFx.capMob" in calls("UpFx", "outW") and "UpFx.capMob" in calls("UpFx", "landedAbil"), "W FIX 3 the KMARK / NETTED puts are capped (capMob)")
    K.check("ThreadLocal.set" in calls("UpFx", "rumble") and "ThreadLocal.remove" in calls("UpFx", "rumble") and "ThreadLocal.get" in calls("UpFx", "shockStun"),
            "W FIX 2 Rumble's flag is a ThreadLocal (set / removed around the free Shockwave, read by shockStun)")
    sp = calls("UpFx", "spinPulse")
    K.check("EntityStatMap.subtractStatValue" in sp and "UpFx.stat" in sp, "W FIX 2 Endless Fury's pulse: Mana + Stamina drained, Stamina back per full spin")
    K.check("AbilStore.arm" in calls("UpFx", "furyEnd") and "AbilStore.arm" in calls("UpFx", "furyOff"), "W FIX 2 Endless Fury's cooldown starts when it ends (furyEnd / furyOff arm it)")
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "m41": str(Cfg.migrate0141()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if step == "1":   # the live world has not started since 0.1.41: its own pending update (Sacred Heal 8 s) may run - nothing of 0.1.43
        K.check(all(k in ("config.properties", "config-changes.log") or k.startswith("config-history/") for k in ch)
                and (not ch or o["m41"].startswith("config.properties updated to the 0.1.41 defaults")),
                "ST start 1 on a scratch COPY of the live data: only 0.1.41's pending update is written (%s): %s" % (ch, o["m41"][:120]))
    else:
        K.check(not ch and o["m41"] == "", "ST start 2: nothing written (%s)" % ch)
    if step == "2":
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("wire", run_wire), ("st1", run_st1), ("st2", run_st2)], script=__file__)
