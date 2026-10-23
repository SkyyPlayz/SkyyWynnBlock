"""Harness for SkyyGear 0.3.40 (elemswords: The Armory's 4 Elemental swords as Spellblade Mythic boss specials - tools/gear_0_3_40_patch.py).
Build first:
    python tools/gear_0_3_40_patch.py && python SkyyGear/build_skyygear_0.3.40.py
    python SkyyGear/test_skyygear_0.3.40.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, 1 new class, no new command / system; tools/pack_drops.py: the 4 swords
              are 4 one-id Mythic Longsword sets in zones 2 / 3 / 4 / 5 (Poison / Gravity / Ice / Flame), the table checks pass
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.39 -> 0.3.40 (EXPECT below)
  X  exec     EXECUTES in a bare JVM:
              X1 GearESw.which / elemOf / causeOk / swingOk: the 4 ids, the 3 swing causes, no damage sequence / a shot / esword.on off = no
              X2 innate: Flame +8 fFire, Ice +8 fWater, Gravity +8 fEarth, Poison +20 poison - on a COPY; any other id / off / 0 % = the same array
              X3 the elem1 split maths with the innate part (GearElem.pcts): the sword counts as "the weapon deals it" (a Fire pet adds), Imbue adds
              X4 GearElem.split on real GearStats with a stand-in ItemStack of each sword (Unsafe-allocated, id set): inf[6] carries the element part, the Poison sword inf[7];
                 classes:fn:imbue "Poison;30" adds 30 to the Poison line (NPC victim only), a vanilla longsword = 0.3.39 exactly
              X5 poisonPct / poisonImbue parsing (junk, other elements, no SkyyClasses, asked with {UUID, weapon})
              X6 tooltip text + colour (Style Guide 15 element colours), statusText, the 3 rows' fields + defaults in the fresh file
              X7 GearPackId: each sword = role Mythic in its zone, special (= its Armory recipe is refused by GearCraftPreSys)
              X8 kunaiTwin: without the item map (bare JVM) a sword stays its own base (the Cobalt twin needs the live item - in game)
              X9 fix round: shotSrc (a ProjectileSource hit is never a swing, real Damage objects), the named ability header
  W  wiring   bytecode: weaponHit2 asks GearESw.counted inside the family gate, before the base multiplier; GearHitSys asks GearESw.swing for the
              Untiered tricks; GearElem.split / note use innate (+ poisonImbue); weaponRows shows abilityText; kunaiTwin names the Cobalt longsword;
              the ready line has GearESw.statusText
  D  live     start TWICE on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: every migration + load twice, the second start changes
              nothing, the 3 new rows read their defaults from a file without them (no one-time update)
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): a real swing's DAMAGE_SEQUENCE on The Armory's Fire / Ice / Poison interactions, the Cobalt-twin level
multiplier on the live item map, the boss bag -> identify on a live boss kill, vanilla NPC resistances to the Fire / Ice / Poison causes.
Scratch: tools/dev/scratch/elemswords/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.40"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "elemswords", "gear")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.39.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_40_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.39.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = ["GearESw"]
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],
    "GearCfg": ["+f ESW_ELEM", "+f ESW_ON", "+f ESW_POISON", "~<clinit>", "~m apply", "~m defaultsText"],
    "GearPackId": ["~<clinit>"],
    "GearBase": ["~m kunaiTwin"], "GearView": ["~m weaponRows"], "GearElem": ["~m note", "~m split"], "GearHit": ["~m weaponHit2"], "GearHitSys": ["~m handle"],
    "SkyyGearPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U = "00000000-0000-0000-0000-000000000340"
IDS = ["Weapon_Elemental_Flame", "Weapon_Elemental_Ice", "Weapon_Elemental_Gravity", "Weapon_Elemental_Poison"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.40 - build script') and g.count('VERSION = "0.3.40"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 1), "S no new system / command, 1 new class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    import pack_drops as PKD
    K.check(not PKD.check(), "S tools/pack_drops.py checks pass: %s" % PKD.check())
    rows = dict((r[0], r) for r in PKD.rows())
    got = [(i, PKD.ROLES[rows[i][6]], rows[i][2], rows[i][5], rows[i][4]) for i in IDS if i in rows]
    K.eq(got, [("Weapon_Elemental_Flame", "mythic", "Weapon_Longsword", 5, "mithril"), ("Weapon_Elemental_Ice", "mythic", "Weapon_Longsword", 4, "adamantite"),
               ("Weapon_Elemental_Gravity", "mythic", "Weapon_Longsword", 3, "cobalt"), ("Weapon_Elemental_Poison", "mythic", "Weapon_Longsword", 2, "thorium")],
         "S pack_drops: one Mythic Longsword sword per zone (Poison 2, Gravity 3, Ice 4, Flame 5)")
    sets = [s for s in PKD.active_sets() if any(i in s["ids"] for i in IDS)]
    K.check(len(sets) == 4 and all(len(s["ids"]) == 1 for s in sets), "S 4 one-id sets (each sword its own set share)")
    lz = [(PKD.zone_of(s["tier"]), s["key"]) for s in PKD.active_sets() if s["role"] == "mythic" and s["kind"] == "Weapon_Longsword"]
    K.eq(sorted(lz), [(2, "armory_elemental_poison"), (3, "armory_elemental_gravity"), (4, "armory_elemental_ice"), (5, "armory_elemental_flame")],
         "S no other Longsword Mythic in those zones")
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JInt, JDouble
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Df, E, H, Gv, S = (JClass(PKG + n) for n in ("GearCfg", "GearDefs", "GearElem", "GearHit", "GearView", "GearESw"))
    Pid, Base = JClass(PKG + "GearPackId"), JClass(PKG + "GearBase")
    uu = JClass("java.util.UUID").fromString(U)
    NS = int(Df.NS)
    SI = lambda k: int(Df.sIndex(k))

    def arr(d):
        a = [0] * NS
        for k, v in d.items():
            a[SI(k)] += v
        return JArray(JInt)(a)
    # ---- X1 the decision
    K.eq([int(S.which(i)) for i in IDS + ["Weapon_Longsword_Cobalt", "Weapon_Elemental_Lightning", None]], [0, 1, 2, 3, -1, -1, -1], "X1 which: the 4 ids only")
    K.eq([int(S.elemOf(i)) for i in IDS], [3, 2, 0, 5], "X1 elemOf: Flame Fire, Ice Water, Gravity Earth (GearElem order), Poison 5")
    K.eq([bool(S.causeOk(c)) for c in ("Fire", "Ice", "Poison", "Physical", "Projectile", "Lightning", None)], [True, True, True, False, False, False, False],
         "X1 causeOk: the swords' three swing causes")
    K.eq([bool(S.swingOk("Weapon_Elemental_Flame", "Fire", True, False)), bool(S.swingOk("Weapon_Elemental_Gravity", "Fire", True, False)),
          bool(S.swingOk("Weapon_Elemental_Poison", "Poison", True, False)), bool(S.swingOk("Weapon_Elemental_Ice", "Ice", True, False))], [True] * 4,
         "X1 swingOk: each sword's own swing (Gravity swings Fire in their file)")
    K.eq([bool(S.swingOk("Weapon_Elemental_Flame", "Fire", False, False)), bool(S.swingOk("Weapon_Elemental_Flame", "Fire", True, True)),
          bool(S.swingOk("Weapon_Longsword_Flame", "Fire", True, False)), bool(S.swingOk("Weapon_Elemental_Flame", "Physical", True, False))], [False] * 4,
         "X1 no damage sequence (a DoT tick / ability) / a projectile / another Fire weapon / a non-element cause = not a sword swing")
    Cfg.ESW_ON = False
    K.check(not bool(S.swingOk("Weapon_Elemental_Flame", "Fire", True, False)) and not bool(S.swing(None, None)), "X1 esword.on off = never (0.3.39)")
    Cfg.ESW_ON = True
    K.check(not bool(S.swing(None, None)) and not bool(S.counted(None, None)), "X1 swing / counted with no Damage = false, never throws")
    # ---- X2 innate
    t = arr({"fFire": 3, "poison": 5, "str": 7})
    for i, k, v in (("Weapon_Elemental_Flame", "fFire", 11), ("Weapon_Elemental_Ice", "fWater", 8), ("Weapon_Elemental_Gravity", "fEarth", 8), ("Weapon_Elemental_Poison", "poison", 25)):
        r = S.innate(i, t)
        K.check(int(r[SI(k)]) == v and int(r[SI("str")]) == 7 and int(t[SI(k)]) in (0, 3, 5) and not (r is t),
                "X2 innate %s: %s = %d on a copy (the totals untouched)" % (i, k, int(r[SI(k)])))
    K.check(S.innate("Weapon_Longsword_Cobalt", t) is t or list(S.innate("Weapon_Longsword_Cobalt", t)) == list(t), "X2 any other weapon = the same totals")
    K.check(S.innate(None, t) is t or list(S.innate(None, t)) == list(t), "X2 no weapon = the same totals")
    Cfg.ESW_ON = False
    K.eq(list(S.innate("Weapon_Elemental_Flame", t)), list(t), "X2 esword.on off = no innate part")
    Cfg.ESW_ON = True
    Cfg.ESW_ELEM, Cfg.ESW_POISON = 0, 40
    K.eq((list(S.innate("Weapon_Elemental_Ice", t)) == list(t), int(S.innate("Weapon_Elemental_Poison", t)[SI("poison")])), (True, 45), "X2 esword.elemPct 0 = none, poisonPct 40 = +40")
    Cfg.ESW_ELEM, Cfg.ESW_POISON = 8, 20
    K.check(S.innate("Weapon_Elemental_Flame", None) is None, "X2 null totals = null")
    # ---- X3 the split maths with the innate part
    full = arr({"fFire": 10})
    rolled = arr({})
    pet = arr({"fFire": 10})
    K.eq(round(float(E.pcts(full, rolled, None, pet, True, -1, 0.0)[3]), 6), 0.0, "X3 0.3.39: a Fire pet with a plain weapon = 0")
    K.eq(round(float(E.pcts(S.innate("Weapon_Elemental_Flame", full), S.innate("Weapon_Elemental_Flame", rolled), None, pet, True, -1, 0.0)[3]), 6), 18.0,
         "X3 the Flame sword = Fire 8 + the Fire pet 10 = 18 (the sword deals Fire)")
    K.eq(round(float(E.pcts(S.innate("Weapon_Elemental_Flame", full), S.innate("Weapon_Elemental_Flame", rolled), None, pet, True, 3, 30.0)[3]), 6), 48.0,
         "X3 + a Fire Imbue 30 = 48")
    K.eq([round(float(x), 6) for x in E.pcts(S.innate("Weapon_Elemental_Gravity", arr({})), S.innate("Weapon_Elemental_Gravity", arr({})), None, None, True, -1, 0.0)],
         [8.0, 0.0, 0.0, 0.0, 0.0], "X3 Gravity = Earth only")
    # ---- X4 split on real GearStats with real ItemStacks
    # the bare JVM has no item map (new ItemStack(id, n) asks Item.getAssetStore()): a stand-in stack = an ItemStack allocated without its
    # constructor (sun.misc.Unsafe) with its item id + quantity fields set - getItemId / isEmpty / getMetadata are the real methods
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    un = fu.get(None)
    fl = dict((str(f.getName()), f) for f in IS.class_.getDeclaredFields())
    K.notes.append("X4 ItemStack fields: %s" % sorted(fl))

    def stack(i):
        s_ = un.allocateInstance(IS.class_)
        for n_, v_ in (("itemId", i), ("quantity", JInt(1))):
            if n_ in fl:
                fl[n_].setAccessible(True)
                fl[n_].set(s_, v_)
        return s_
    st = {}
    for i in IDS + ["Weapon_Longsword_Cobalt"]:
        try:
            s_ = stack(i)
            K.check(str(s_.getItemId()) == i and not bool(s_.isEmpty()), "X4 stand-in stack %s (getItemId / isEmpty real)" % i)
            st[i] = s_
        except Exception as ex:
            K.check(False, "X4 stand-in ItemStack %s: %s" % (i, ex))
    if len(st) == 5:
        t0 = arr({"tdmg": 4})

        def sp(i, vnpc=True):
            inf = H.info(uu, t0)
            H.pctInfo(inf, t0, 100.0, 0.5)
            E.split(inf, uu, st[i], None, t0, 100.0, vnpc)
            return inf
        f = sp("Weapon_Elemental_Flame")
        K.check(f[6] is not None and int(list(f[6])[3]) == 8 and sum(list(f[6])) == 8 and int(f[5]) == 8 and int(f[7]) == 0,
                "X4 split, Flame sword, 100 hit: [6] = %s (Fire 8), [5] 8, no Poison" % (None if f[6] is None else list(f[6])))
        g = sp("Weapon_Elemental_Gravity")
        K.check(g[6] is not None and list(g[6]) == [8, 0, 0, 0, 0], "X4 Gravity: Earth 8")
        p = sp("Weapon_Elemental_Poison")
        K.check(int(p[7]) == 20 and (p[6] is None or sum(list(p[6])) == 0), "X4 the Poison sword: Poison line 20 (inf[7]), no element part")
        c = sp("Weapon_Longsword_Cobalt")
        K.check((c[6] is None or sum(list(c[6])) == 0) and int(c[7]) == 0, "X4 a vanilla Cobalt longsword: nothing added (0.3.39)")

        @JImplements("java.util.function.Function")
        class Imb(object):
            def __init__(self, ans):
                self.ans, self.calls = ans, []

            @JOverride
            def apply(self, a):
                self.calls.append([str(x) for x in a])
                return self.ans
        im = Imb("Poison;30")
        br.put("classes:fn:imbue", im)
        p2 = sp("Weapon_Elemental_Poison")
        p3 = sp("Weapon_Elemental_Poison", vnpc=False)
        K.check(int(p2[7]) == 50 and int(p3[7]) == 20, "X4 Imbue 'Poison;30' with the Poison sword on an NPC = Poison 50 (Q8); on a player 20 (the Imbue part is NPC-only)")
        K.check([U, "Weapon_Elemental_Poison"] in im.calls, "X4 classes:fn:imbue asked with {UUID, weapon id}")
        br.remove("classes:fn:imbue")
        Cfg.POISON_ON = False
        K.check(int(sp("Weapon_Elemental_Poison")[7]) == 0, "X4 poison.on off = no Poison from the sword")
        Cfg.POISON_ON = True
        Cfg.ESW_ON = False
        f0 = sp("Weapon_Elemental_Flame")
        K.check((f0[6] is None or sum(list(f0[6])) == 0) and int(sp("Weapon_Elemental_Poison")[7]) == 0, "X4 esword.on off = 0.3.39 (nothing added)")
        Cfg.ESW_ON = True
    # ---- X5 poisonPct / poisonImbue
    K.eq([int(S.poisonPct(s)) for s in ("Poison;30", "poison;37.6", "Fire;30", "Poison;", "Poison;-3", "Poison;x", ";30", None)], [30, 38, -1, -1, -1, -1, -1, -1],
         "X5 poisonPct: only a Poison answer")
    K.eq(int(S.poisonImbue(uu, "Weapon_Elemental_Poison")), 0, "X5 no SkyyClasses = 0")

    @JImplements("java.util.function.Function")
    class Boom(object):
        def __init__(self):
            self.n = 0

        @JOverride
        def apply(self, a):
            self.n += 1
            raise RuntimeError("boom")
    bo = Boom()
    br.put("classes:fn:imbue", bo)
    K.eq((int(S.poisonImbue(uu, "Weapon_Elemental_Poison")), int(S.poisonImbue(uu, "Weapon_Elemental_Flame")), bo.n), (0, 0, 1),
         "X5 a throwing SkyyClasses = 0; another sword never asks")
    br.remove("classes:fn:imbue")
    # ---- X6 tooltip, colours, status, rows
    import skyyelem as ELX
    txt = [S.abilityText(i) for i in IDS]
    K.check(all(t_ is not None for t_ in txt) and "+8% of its hit as Fire" in str(txt[0]) and "as Water" in str(txt[1]) and "as Earth" in str(txt[2])
            and "poisons for +20% of its hit over 10s" in str(txt[3]), "X6 abilityText: %s" % [str(x) for x in txt])
    K.check(all(len(str(x)) <= 110 for x in txt), "X6 the ability lines stay short (%s)" % [len(str(x)) for x in txt])
    K.eq([str(S.abilityCol(i)) for i in IDS], [ELX.COLORS["Fire"], ELX.COLORS["Water"], ELX.COLORS["Earth"], ELX.COLORS["Poison"]], "X6 the line in the element colour (Style Guide 15)")
    K.check(S.abilityText("Weapon_Longsword_Cobalt") is None and S.abilityCol("Weapon_Longsword_Cobalt") is None, "X6 a plain longsword: no Elemental Blade line")
    Cfg.ESW_ON = False
    K.check(S.abilityText("Weapon_Elemental_Flame") is None and "OFF" in str(S.statusText()), "X6 off: no line, ready line says OFF")
    Cfg.ESW_ON = True
    K.check(str(S.statusText()).startswith("Elemental swords on (+8% element, Poison sword 20%"), "X6 ready line: %s" % S.statusText())
    K.eq((bool(Cfg.ESW_ON), int(Cfg.ESW_ELEM), int(Cfg.ESW_POISON)), (True, 8, 20), "X6 the field defaults")
    dt = str(Cfg.defaultsText())
    K.check("\nesword.on=true\n" in dt and "\nesword.elemPct=8\n" in dt and "\nesword.poisonPct=20\n" in dt and dt.count("(SkyyGear 0.3.40) ----") == 1,
            "X6 the fresh file lists the 3 rows with their defaults")
    # ---- X7 GearPackId
    zs = []
    for i in IDS:
        k = int(Pid.idx(i))
        zs.append((k >= 0 and int(Pid.ROLE[k]) == 2, int(Pid.ZONE[k]) if k >= 0 else -1))
    K.eq(zs, [(True, 5), (True, 4), (True, 3), (True, 2)], "X7 GearPackId: Flame Mythic zone 5, Ice 4, Gravity 3, Poison 2")
    sp_ = [bool(Pid.special(i)) for i in IDS]
    K.notes.append("X7 GearPackId.special in the bare JVM (has() needs the live item map): %s" % sp_)
    # ---- X8 kunaiTwin without the item map
    K.eq([str(Base.kunaiTwin(i)) for i in IDS[:1]] + [str(Base.kunaiTwin("Weapon_Kunai_Iron"))], ["Weapon_Elemental_Flame", "Weapon_Kunai_Iron"],
         "X8 no item map: the sword stays its own base (the twin is only taken when Weapon_Longsword_Cobalt is loaded)")
    # ---- X9 (fix critic 1) a ProjectileSource hit is never a swing, even with no launch record while a sword is held
    DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DPRJc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
    DENTc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    dfl = dict((str(f.getName()), f) for f in DMGc.class_.getDeclaredFields())

    def dmg(src_cls):
        d_ = un.allocateInstance(DMGc.class_)
        dfl["source"].setAccessible(True)
        dfl["source"].set(d_, un.allocateInstance(src_cls.class_))
        return d_
    dp, de = dmg(DPRJc), dmg(DENTc)
    K.eq((bool(S.shotSrc(dp)), bool(S.shotSrc(de)), bool(S.shotSrc(None))), (True, False, False), "X9 shotSrc: ProjectileSource yes, EntitySource / none no")
    n0, n1 = int(S.N[0]), int(S.N[1])
    fs = stack("Weapon_Elemental_Flame")
    K.check(not bool(S.swing(dp, fs)) and not bool(S.counted(dp, fs)) and int(S.N[0]) == n0 and int(S.N[1]) == n1 + 1,
            "X9 a projectile hit while holding the Flame sword: no swing (counted as a non-swing sword hit)")
    K.eq([str(S.abilityHead(i)) for i in IDS], ["Ability: Elemental Blade (%s Sword)" % w for w in ("Flame", "Ice", "Gravity", "Poison")],
         "X9 (fix critic 2) the ability header names the sword (their files all say Cobalt Longsword)")
    K.check(S.abilityHead("Weapon_Longsword_Cobalt") is None, "X9 a plain longsword: no header")
    K.save()


def run_wire(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    w = code("GearHit", "weaponHit2")
    K.check("GearESw.counted" in w and w.index("GearHit.family") < w.index("GearESw.counted") < w.index("GearBase.weaponMult"),
            "W weaponHit2: the family gate, then GearESw.counted, before the base multiplier")
    h = code("GearHitSys", "handle")
    K.check("GearESw.swing" in h and h.index("GearHit.weaponHit2") < h.index("GearESw.swing") < h.index("GearUtFx.onHit"), "W GearHitSys: the Untiered tricks also on a sword swing")
    s = code("GearElem", "split")
    K.check(s.count("GearESw.innate") == 2 and "GearESw.poisonImbue" in s and s.index("GearESw.innate") < s.index("GearCfg.ELEM_ON"), "W split: innate on the totals + the rolled lines, poisonImbue")
    n = code("GearElem", "note")
    K.check(n.count("GearESw.innate") == 2, "W note (the Stats totals): innate twice")
    K.check("GearESw.abilityText" in code("GearView", "weaponRows") and "GearESw.abilityCol" in code("GearView", "weaponRows"), "W weaponRows: the Elemental Blade line")
    sw = code("GearESw", "swing")
    K.check("GearESw.shotSrc" in sw and sw.index("GearESw.shotSrc") < sw.index("getCause") < sw.index("GearSpeed.calcOf"), "W swing: the ProjectileSource guard first (fix critic 1)")
    K.check("GearESw.abilityHead" in code("GearView", "weaponRows"), "W weaponRows: the named header (fix critic 2)")
    K.check("Weapon_Longsword_Cobalt" in code("GearBase", "kunaiTwin"), "W kunaiTwin: the Cobalt longsword twin")
    K.check("GearESw.statusText" in code("SkyyGearPlugin", "setup"), "W the ready line")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39"]
    before = open(fc, "rb").read()
    t0 = HK.tree_hash(home)
    m1 = [str(getattr(Cfg, m)()) for m in MIG]
    Cfg.load()
    t1 = HK.tree_hash(home)
    m2 = "".join(str(getattr(Cfg, m)()) for m in MIG)
    Cfg.load()
    t2 = HK.tree_hash(home)
    K.notes.append("D start 1 on the live copy: %s" % [x[:160] for x in m1 if x])
    K.check(m2 == "" and t1 == t2, "D start 2: nothing changes (%r)" % m2[:120])
    txt = open(fc, "rb").read().decode("latin-1")
    K.check("esword." not in txt, "D no one-time update writes the new esword rows (a file without them = the defaults)")
    K.eq((bool(Cfg.ESW_ON), int(Cfg.ESW_ELEM), int(Cfg.ESW_POISON)), (True, 8, 20), "D the live file loads with the esword rows at their defaults")
    K.check((b"\r\n" in before) == ("\r\n" in txt), "D line endings kept")
    K.notes.append("D files changed by start 1 (0.3.39's migrate39 if the live world has not started 0.3.39 yet): %s" % sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))[:8])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("wire", run_wire), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
