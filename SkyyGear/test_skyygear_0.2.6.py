"""Bare-JVM check for SkyyGear 0.2.6 (WEAPON SPEED TIERS: research/cloud/Weapon-Speed-Tiers.md + research/Swing-Speed-Spec.md, Skyy's locks
of 2026-10-06 "Fully random per item" and "only roll on weapons. Not tools"). The 0.2.5 harness (SkyyGear/test_skyygear_0.2.5.py, read only:
the 0.2.3 harness + section AF) runs on the 0.2.6 jar with VERSION 0.2.6 and the new section AG appended inside its child run.

    python SkyyGear/test_skyygear_0.2.6.py [--jar <SkyyGear-0.2.6.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

The carried sections run with GearSpeed.FORCE_OFF set (the bare-JVM hold of the new system: no tier rolls, no weight, no line - their
documents and numbers must stay exactly 0.2.5's); section AG switches it back on and executes every new path. Carried checks that MUST read
differently on 0.2.6 are listed in DEVIATIONS26 with the reason ("DEVIATION (0.2.5/0.2.6, expected)"); any other failure fails the run.
  AG 0.2.6 - every new code path EXECUTED:
     AG0 the generator re-run here on Assets.zip (exec'd from the build script) = the jar's 258 speed assets byte for byte; the 9 replaced roots
         keep every vanilla field; the trees, leaves (cooldown x f) and tier tops; the two rows (types, defaults, flags, help), the fresh
         file's speed block, the loader (bad odds -> default + WARN), swingOdds / checkSwingOdds;
     AG1 the tier roll: pickW on fixed numbers, pick() distribution on 40 000 rolls (25/25/25/25, 10/20/30/40, 1/0/0/0, all 0), ensure()
         only for an identified tier weapon without a tier - never a tool / spell weapon / armor / excluded item / unidentified one, never
         while switched off, never twice;
     AG2 an engine model of the 0.2.6 assets (Assets.zip + the jar's files: real Interaction / RootInteraction / DamageEntityInteraction
         objects): famOf / active() / GearSpeed.walk (the engine's walkChain over every family's tier roots = the tap calculators, the same set
         for every tier, never a charged / signature step);
     AG3 DPS EQUALITY: each of the 9 families' representative item at Lv 1 / 15 / 30 / 49 with 3 modifier sets x 4 tiers through the REAL
         GearHit.weaponHit on real Damage objects (DamageSequence meta) x the cadence of the jar's own assets (the tier chain + the tree leaf
         cooldown): damage per second identical, per hit x w; True Damage / flat elements x w; charged and projectile hits x1; the swap guard;
     AG4 existing items get a tier ONCE (the stamp scan = first touch on 3 000 old documents: distribution, a second scan changes nothing),
         identify rolls it, reforge / level up / clones keep it, the bridge sig;
     AG5 the tooltip (Attack Speed line, per-hit line x w, the charged line, Medium, switched off, an excluded item, a tool), gear:fn:speed,
         Mana per cast (manaCost: damage per Mana equal on every tier), the /gear read line;
     AG6 the tier effect: GearSpeed.tick on the ECS shim with a REAL EffectControllerComponent and real EntityEffect assets (add, refresh,
         swap, Medium / tool / switched off = removed) - the hit weight follows it;
     AG8 the FIX ROUND (critics of 2026-10-06), one check per fix: stochastic rounding of True Damage / flat elements (the mean is
         v x w), the stats-on-hit extra (SignatureEnergy) + the knockback modifier through perHit on a REAL EntityStatMap /
         KnockbackComponent and the engine's own SequenceModifier, the hit weight = the tier the swing ran (no effect = x1, a Medium /
         tier-less item under a lagging effect, the per-family swap window), the effect record kept true (a lost effect, a stray effect
         on the first tick, 3 s / 1.5 s refresh), the idle-state sweep, famOf never caching a miss + dropping its cache on a config
         epoch / the Item reload listener, no tier line while the effects failed to load;
     AG7 start twice on a scratch COPY of the live Skyy_SkyyGear folder: the whole setup() file chain twice, no file changes the second time,
         the speed keys read their defaults (no one-time update);
     AG10 the class byte-compare 0.2.5 -> 0.2.6 (every difference listed) + the non-class entries.
Scratch: only under --dir (default tools/dev/scratch/gear026/harness; the fix round ran it with --dir tools/dev/scratch/gear026fix/harness), deleted at the end unless --keep. Exit code 1 on any unexpected failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
H25 = os.path.join(HERE, "test_skyygear_0.2.5.py")
_t25 = open(H25, encoding="utf-8").read()
_cut = _t25.index('_g = {"__name__": "__main__"')
_n25 = {"__name__": "skyygear_h25", "__file__": H25, "__builtins__": __builtins__}
exec(compile(_t25[:_cut], H25 + " (the 0.2.5 harness text, not run)", "exec"), _n25)
src = _n25["src"]
DEV25 = _n25["DEVIATIONS"]


def sub(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "harness text changed: anchor count %d (want %d): %s" % (n, count, old[:120])
    src = src.replace(old, new)


DEVIATIONS26 = [
    ("Z8: the live data ends with every value of a fresh 0.2.6 file", "the 0.2.5 deviation under the new version text: Z8 replays setup() only up to "
     "migrate023 (base.curve keeps the 0.2.1 default there); AF6 runs migrate025, AG7 starts the whole chain twice on the live copy"),
    ("AB8: no vanilla recipe changed - the jar overrides no item / recipe file", "the jar now also ships the 258 speed assets (the 9 replaced melee "
     "Primary roots, re-timed interactions, walk roots, animation sets, 3 effects) - still no item / recipe file; AG0 + AG10 check the exact list"),
    ("AC6: the SkyyMobs classes are the SET pin's jar", "pre-existing since the mob curve round: tools/deploy_set.py's new STOP code "
     "(_p.get(\"SkyyMobs\", \"0\")) also matches the check's regex; the classes ARE SkyyMobs-0.1.4.jar = the SET pin"),
    ("AE10: non-class entries: only manifest.json changed", "the historical 0.2.2 -> 0.2.3 compare - AG10 compares 0.2.5 -> 0.2.6"),
    ("AF1: 72 Server Setup rows", "74 rows: + swing.tiers + swing.odds (AG0)"),
    ("AF1: the fresh file: steal.maxPerSec under steal.windowS", "the check also asks the header '# SkyyGear 0.2.5 - ' (the version text); AG0 "
     "re-checks both blocks under the 0.2.6 header"),
    ("AF10: one class added (GearABox), none removed", "the historical 0.2.4 -> 0.2.5 compare - AG10 compares 0.2.5 -> 0.2.6"),
    ("AF10: no difference outside the listed 0.2.5 parts", "the historical 0.2.4 -> 0.2.5 compare - AG10 compares 0.2.5 -> 0.2.6"),
    ("AF10: non-class entries: only manifest.json changed", "the historical 0.2.4 -> 0.2.5 compare - AG10 compares 0.2.5 -> 0.2.6"),
]

sub('VERSION = "0.2.5"\nDEVIATIONS = %r' % (DEV25,), 'VERSION = "0.2.6"\nDEVIATIONS = %r' % (DEV25 + DEVIATIONS26,))
sub('os.path.join(TOOLS, "dev", "scratch", "gear025", "harness")', 'os.path.join(TOOLS, "dev", "scratch", "gear026", "harness")')
sub('print("DEVIATION (0.2.5, expected):"', 'print("DEVIATION (0.2.5/0.2.6, expected):"')
sub('expected 0.2.5 deviations (%d listed kinds seen)', 'expected 0.2.5 / 0.2.6 deviations (%d listed kinds seen)')
# the carried sections run with the new system held off (their documents and numbers stay 0.2.5's); AG switches it on
sub('''    bridge = Gear.bridge()
''', '''    bridge = Gear.bridge()
    J("GearSpeed").FORCE_OFF = True     # 0.2.6: the carried sections run without speed tiers (section AG switches them on)
''')

AG_SRC = r'''    # ======================================================================================================================== AG 0.2.6
    # SkyyGear 0.2.6 = WEAPON SPEED TIERS. Every new code path EXECUTED on the AC model + an engine model of the jar's own speed assets.
    import math as _mg
    import random as _rg
    print("AG. 0.2.6: weapon speed tiers - generator, roll, engine walk, DPS, first touch, tooltip, tier effect, live copy, class compare")
    Spd = J("GearSpeed")
    Spd.FORCE_OFF = False
    Cfg.apply(Props(), False)
    Spd.reset()
    jz6 = zipfile.ZipFile(jar)
    jn6 = set(jz6.namelist())
    bsrc6 = open(os.path.join(HERE, "build_skyygear_%s.py" % VERSION), encoding="utf-8").read()
    g6 = {"os": os, "json": json, "AzWalker": AzWalker}
    exec(bsrc6[bsrc6.index("# ---- SPEED GENERATOR BEGIN"):bsrc6.index("# ---- SPEED GENERATOR END")], g6)
    AZP6 = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    az6 = zipfile.ZipFile(AZP6)
    az6n = az6.namelist()
    WK0 = AzWalker(az6, az6n, {})
    VAN6 = sorted(i for i in WK0.items if i.startswith("Weapon_"))
    files6, fams6, skip6, elig6 = g6["speed_build"](WK0, sorted(az6n), VAN6, lambda q_: json.loads(az6.read(q_).decode("utf-8-sig")))
    TIERS = ["Slow", "Medium", "Fast", "Super Fast"]
    FAMS6 = [f_["fam"] for f_ in fams6]

    # ---- AG0. the jar = the generator; the replaced roots; rows, fresh file, loader
    jfiles6 = sorted(n_ for n_ in jn6 if n_.startswith(("Server/Item/Interactions/SkyyGear/Speed/", "Server/Item/RootInteractions/SkyyGear/Speed/",
                                                         "Server/Item/Animations/SkyyGear/", "Server/Entity/Effects/SkyyGear/")))
    roots6 = sorted(f_["path"] for f_ in fams6)
    check(sorted(files6) == sorted(jfiles6 + roots6) and all(jz6.read(k_).decode("utf-8") == v_ for k_, v_ in files6.items()),
          "AG0: the generator re-run on Assets.zip = the jar's %d speed assets byte for byte (deterministic)" % len(files6))
    check(len(files6) == 258 and len(elig6) == 118 and FAMS6 == ["Sword", "Daggers", "Longsword", "Spear", "Battleaxe", "Axe", "Club", "Flail", "Mace"],
          "AG0: 9 melee families, 118 vanilla tier weapons, 258 assets (%d / %d)" % (len(elig6), len(files6)))
    rbad6 = []
    for f_ in fams6:
        van_ = json.loads(az6.read(f_["path"]).decode("utf-8-sig"))
        own_ = json.loads(jz6.read(f_["path"]).decode("utf-8"))
        if dict((k_, v_) for k_, v_ in own_.items() if k_ != "Interactions") != dict((k_, v_) for k_, v_ in van_.items() if k_ != "Interactions") \
                or own_.get("Interactions") != ["SkyyGear_Spd_" + f_["fam"]]:
            rbad6.append(f_["fam"])
        tree_ = json.loads(jz6.read("Server/Item/Interactions/SkyyGear/Speed/SkyyGear_Spd_%s.json" % f_["fam"]).decode("utf-8"))
        cd_ = float((van_.get("Cooldown") or {}).get("Cooldown", 0.35))
        if not (tree_["Type"] == "EffectCondition" and tree_["Match"] == "None" and tree_["Next"] == van_["Interactions"][0]
                and tree_["EntityEffectIds"] == ["SkyyGear_Speed_Slow", "SkyyGear_Speed_Fast", "SkyyGear_Speed_SuperFast"]):
            rbad6.append(f_["fam"] + " top")
        node_ = tree_["Failed"]
        for t_, eid_ in ((0, "SkyyGear_Speed_Slow"), (2, "SkyyGear_Speed_Fast"), (3, "SkyyGear_Speed_SuperFast")):
            lf_ = node_["Next"]
            if not (node_["Match"] == "All" and node_["EntityEffectIds"] == [eid_] and lf_["Type"] == "TriggerCooldown" and "Id" not in lf_["Cooldown"]
                    and abs(lf_["Cooldown"]["Cooldown"] - round(cd_ * f_["f"][t_], 4)) < 1e-9 and lf_["Next"] == "SkyyGear_Spd%s_%s_%s" % ("SMFX"[t_], f_["fam"], van_["Interactions"][0])):
                rbad6.append("%s %s leaf" % (f_["fam"], TIERS[t_]))
            node_ = node_["Failed"]
        if node_ != van_["Interactions"][0]:
            rbad6.append(f_["fam"] + " last Failed")
    check(not rbad6, "AG0: each replaced root keeps every vanilla field (cooldown, RequireNewClick, tags) and only points at SkyyGear_Spd_<family>; "
                     "the tree: no tier effect -> the vanilla interaction, each tier -> TriggerCooldown(vanilla cooldown x f, the root's own id) -> "
                     "its re-timed top: %s" % rbad6)
    for t_ in (0, 2, 3):
        e_ = json.loads(jz6.read("Server/Entity/Effects/SkyyGear/%s.json" % ["SkyyGear_Speed_Slow", "", "SkyyGear_Speed_Fast", "SkyyGear_Speed_SuperFast"][t_]).decode("utf-8"))
        check(e_ == {"Duration": 3, "OverlapBehavior": "Overwrite"}, "AG0: the %s effect is a hidden marker (no icon, no stats): %s" % (TIERS[t_], e_))
    check([float(Spd.weight(i_, t_)) for i_ in range(9) for t_ in range(4)] == [float(x_) for f_ in fams6 for x_ in f_["w"]]
          and [float(x_) for x_ in fams6[1]["f"]] == [1.4, 1.0, 0.7246, 0.7246] and all(abs(a_ - b_) < 1e-3 for f_ in fams6 for a_, b_ in zip(f_["w"], f_["f"]))
          and [str(x_) for x_ in Spd.F_ROOT] == [f_["root"] for f_ in fams6],
          "AG0: the jar's hit weights = the build's cycle ratios per family, each within 0.001 of its tier factor (the dagger's 0.207 s swing floors "
          "Fast + Super Fast at 0.15 s = x0.7246): %s" % dict((f_["fam"], f_["w"]) for f_ in fams6))
    keys6 = [str(k) for k in Rows.KEYS]
    rw6 = dict((str(k), (str(t), str(dd), str(fl), str(h))) for k, t, dd, fl, h in zip(Rows.KEYS, Rows.TYPES, Rows.DEFS, Rows.FLAGS, Rows.HELPS))
    check(len(keys6) == 74 and rw6.get("swing.tiers") == ("bool", "true", "live,danger", "Weapons swing Slow / Medium / Fast / Super Fast (same damage per second). Off = all vanilla.")
          and rw6.get("swing.odds", ("",))[:3] == ("text", "25,25,25,25", "live,danger") and rw6["swing.odds"][3].endswith(PH) and len(rw6["swing.odds"][3]) <= 100,
          "AG0: the two rows (74 in all): swing.tiers bool on, swing.odds text 25,25,25,25, both live + danger: %s / %s" % (rw6.get("swing.tiers"), rw6.get("swing.odds")))
    dt6 = str(Cfg.defaultsText())
    dl6 = dt6.split("\n")
    lu6 = [str(x) for x in Cfg.LU_LINES]
    check(dt6.startswith("# SkyyGear 0.2.6 - ") and dl6[dl6.index("steal.windowS=3") + 1:dl6.index("steal.windowS=3") + 3] == [str(Cfg.SM_ROWC[0]), "steal.maxPerSec=5"]
          and dl6[dl6.index("cost.reforge.set=2500,0") + 1:dl6.index("cost.reforge.set=2500,0") + 1 + len(lu6)] == lu6,
          "AG0: the fresh 0.2.6 file keeps the 0.2.5 blocks where AF1 wants them (steal.maxPerSec under steal.windowS, the level up rows under cost.reforge.set)")
    check(dt6.endswith("\n\n# ---- weapon speed tiers (SkyyGear 0.2.6) ----\n# Weapon speed tiers: %s\nswing.tiers=true\n# Weapon speed tier odds: %s\nswing.odds=25,25,25,25\n"
                       % (rw6["swing.tiers"][3], rw6["swing.odds"][3])), "AG0: the fresh file ends with the speed block (heading + help + key each)")
    check(list(Cfg.swingOdds("25,25,25,25")) == [25.0] * 4 and list(Cfg.swingOdds(" 1, 0 ,0,0 ")) == [1.0, 0.0, 0.0, 0.0] and Cfg.swingOdds("0,0,0,0") is None
          and Cfg.swingOdds("1,2,3") is None and Cfg.swingOdds("a,1,1,1") is None and Cfg.swingOdds("-1,1,1,1") is None and Cfg.swingOdds("1,1,1,1000001") is None
          and Cfg.checkSwingOdds("swing.odds", "10,20,30,40") is None and "four weights" in str(Cfg.checkSwingOdds("swing.odds", "1,2")),
          "AG0: swingOdds / checkSwingOdds (four weights 0-1000000, at least one above 0)")
    pz6 = Props()
    pz6.setProperty("swing.tiers", "false")
    pz6.setProperty("swing.odds", "1,2,x,4")
    Gear.ONCE.clear()
    Cfg.apply(pz6, True)
    check(not bool(Cfg.SWING_ON) and not bool(Spd.on()) and str(Cfg.SWING_ODDS) == "25,25,25,25" and list(Cfg.SWING_W) == [25.0] * 4
          and any(str(k_).startswith("swodds:") for k_ in Gear.ONCE.keySet()), "AG0: the loader - swing.tiers=false read, a bad odds line -> the default + one WARN")
    pz6.setProperty("swing.tiers", "true")
    pz6.setProperty("swing.odds", "10,20,30,40")
    Cfg.apply(pz6, True)
    check(bool(Spd.on()) and list(Cfg.SWING_W) == [10.0, 20.0, 30.0, 40.0], "AG0: the loader - odds 10,20,30,40 read")
    Cfg.apply(Props(), False)
    print("AG0. generator, roots, rows done")

    # ---- AG1. the roll
    seqs_ = [(0.0, 0), (0.2499, 0), (0.25, 1), (0.5, 2), (0.7499, 2), (0.75, 3), (0.9999, 3)]
    w4_ = JArray(JClass("double"))([25.0, 25.0, 25.0, 25.0])
    check(all(int(Spd.pickW(w4_, r_)) == t_ for r_, t_ in seqs_), "AG1: pickW 25/25/25/25 cuts at 0.25 / 0.5 / 0.75")
    w0_ = JArray(JClass("double"))([0.0, 0.0, 0.0, 0.0])
    ws_ = JArray(JClass("double"))([0.0, 0.0, 0.0, 5.0])
    check(int(Spd.pickW(w0_, 0.3)) == 1 and int(Spd.pickW(ws_, 0.0)) == 3 and int(Spd.pickW(ws_, 0.999)) == 3 and int(Spd.pickW(None, 0.5)) == 1,
          "AG1: all weights 0 / null -> Medium; one weight -> always that tier")

    def dist(odds_, n_=40000):
        pz_ = Props()
        pz_.setProperty("swing.odds", odds_)
        Cfg.apply(pz_, True)
        c_ = [0, 0, 0, 0]
        for _i in range(n_):
            c_[int(Spd.pick())] += 1
        Cfg.apply(Props(), False)
        return [x_ / float(n_) for x_ in c_]
    d1_ = dist("25,25,25,25")
    d2_ = dist("10,20,30,40")
    d3_ = dist("1,0,0,0", 4000)
    check(all(abs(x_ - 0.25) < 0.012 for x_ in d1_) and all(abs(x_ - e_) < 0.012 for x_, e_ in zip(d2_, (0.1, 0.2, 0.3, 0.4))) and d3_ == [1.0, 0.0, 0.0, 0.0],
          "AG1: pick() on 40 000 rolls: 25/25/25/25 -> %s; 10/20/30/40 -> %s; 1/0/0/0 -> all Slow" % ([round(x_, 3) for x_ in d1_], [round(x_, 3) for x_ in d2_]))
    print("AG1. roll distribution: %s / %s" % ([round(x_, 4) for x_ in d1_], [round(x_, 4) for x_ in d2_]))

    # ---- AG2. the engine model of the jar's assets: famOf, active, the tier walk
    class MZip(object):
        def __init__(s, a_, j_):
            s.a, s.j, s.jn = a_, j_, set(j_.namelist())

        def namelist(s):
            return sorted(set(s.a.namelist()) | s.jn)

        def read(s, n_):
            return s.j.read(n_) if n_ in s.jn else s.a.read(n_)
    mz6 = MZip(az6, jz6)
    WK_old6 = WK
    WK = AzWalker(mz6, mz6.namelist(), {})
    calc6 = {}

    class SpdModel(Model):
        """the AC0 model + REAL root ids for an item's Primary root and the tier walk roots (GearSpeed reads them by id)"""
        def mkcalc(s, c_, key):
            o_ = Model.mkcalc(s, c_, key)
            if o_ is not None:
                calc6[key] = (o_, c_)
            return o_

        def named(s, rid_):
            if rid_ not in s.roots:
                s.roots[rid_] = RootI(rid_, JArray(JString)([i_ for i_ in (s.ref(r_) for r_ in WK.root_ids(rid_)) if i_]))
            return rid_

        def item(s, iid, as_id=None):
            ob = Model.item(s, iid, as_id)
            it_ = WK.item(iid)
            pr_ = (it_.get("Interactions") or {}).get("Primary")
            if isinstance(pr_, str):
                fz(ItemZ, "interactions").get(ob).put(ITY.Primary, s.named(pr_))
            pa_ = it_.get("PlayerAnimationsId")
            if isinstance(pa_, str):
                fz(ItemZ, "playerAnimationsId").set(ob, pa_)
            return ob
    MS6 = SpdModel()
    TOOLS6 = ["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Shovel_Iron", "Tool_Hoe_Iron", "Tool_Sickle_Iron"]
    MID6 = sorted(set(ALLW) | set(TOOLS6))
    zit6 = dict((i_, MS6.item(i_)) for i_ in MID6 if WK.item(i_) is not None)
    for f_ in fams6:
        for w_ in f_["walk"]:
            if w_:
                MS6.named(w_)
    for key_, (o_, c_) in calc6.items():
        bd_ = I2F()
        for k_i, (cn_, val_) in enumerate(sorted((c_.get("BaseDamage") or {}).items())):
            try:
                bd_.put(JInt(k_i), JFloat(float(val_)))
            except Exception:
                pass
        fz(DCALCz, "baseDamage").set(o_, bd_)
        fz(DCALCz, "type").set(o_, DTYPEc.DPS if str(c_.get("Type", "Absolute")).lower() == "dps" else DTYPEc.ABSOLUTE)
        fz(DCALCz, "randomPercentageModifier").setFloat(o_, JFloat(float(c_.get("RandomPercentageModifier", 0.0) or 0.0)))
    check(not MS6.missing, "AG2: every interaction / root of the 0.2.6 assets resolves in the engine model (%s)" % MS6.missing[:5])
    old_is6 = fz(Inter, "ASSET_STORE").get(None)
    old_rs6 = fz(RootI, "ASSET_STORE").get(None)
    fz(Inter, "ASSET_STORE").set(None, zstore(indexed(MS6.inter)))
    fz(RootI, "ASSET_STORE").set(None, zstore(indexed(MS6.roots)))
    old_items6 = dict((k_, imap.get(k_)) for k_ in zit6)
    for k_, v_ in zit6.items():
        try:
            b_ = WDC.calculate(v_, ITY.Primary)
            w_ = IWPc()
            w_.setBasicDamageBreakdown(b_)
            fz(ItemZ, "weapon").set(v_, w_)
        except Exception:
            pass
        imap.put(k_, v_)
    Chg.clear()
    Base.clear()
    Spd.reset()
    print("AG2. engine model of the 0.2.6 assets: %d interactions, %d roots, %d items" % (len(MS6.inter), len(MS6.roots), len(zit6)))
    fam_got = dict((i_, int(Spd.famOf(i_))) for i_ in MID6)
    want_fam = dict((i_, -1) for i_ in MID6)
    for fi_, f_ in enumerate(fams6):
        for i_ in f_["items"]:
            if bool(Data.isGear(i_)) and int(Data.slotOf(i_)) == 0:
                want_fam[i_] = fi_
    fdiff6 = sorted((i_, fam_got[i_], want_fam[i_]) for i_ in MID6 if fam_got[i_] != want_fam[i_])
    check(not fdiff6, "AG2: GearSpeed.famOf (the runtime rule on the engine Items: Primary root, animation set, own main-path vars) = the build's "
                      "119 proven items exactly; every other weapon, every tool, every spell weapon: none: %s" % fdiff6[:8])
    check(all(int(Spd.famOf(t_)) == -1 for t_ in TOOLS6 if t_ in zit6) and len([t_ for t_ in TOOLS6 if t_ in zit6]) >= 4,
          "AG2: tools (pickaxe / hatchet / shovel / hoe / sickle) are never a tier family (Skyy 2026-10-06)")
    check(str(Spd.rootsText()) == "weapon speed tiers ready: 9/9 melee families on SkyyGear's swing roots", "AG2: the INFO line of the first ready(): %s" % Spd.rootsText())
    check(all(bool(Spd.active(i_)) for i_ in range(9)) and str(Spd.rootFirst("Root_Weapon_Sword_Primary")) == "SkyyGear_Spd_Sword",
          "AG2: active() - every family root in the model is SkyyGear's tree")
    REP6 = {}
    for fi_, f_ in enumerate(fams6):
        its_ = f_["items"]
        REP6[f_["fam"]] = next((i_ for i_ in its_ if i_.endswith("_Iron")), its_[0])
    wbad6 = []
    for fam_, iid_ in sorted(REP6.items()):
        sets_ = [Spd.walk(iid_, JInt(t_)) for t_ in (0, 2, 3)]
        ks_ = [sorted(int(SysJ.identityHashCode(k_)) for k_ in s_.keySet()) for s_ in sets_]
        e_ = Chg.ensure(iid_)
        full_ = [k_ for k_ in e_[0].keySet() if int(e_[0].get(k_)[0]) != 4]
        if not ks_[0] or ks_[0] != ks_[1] or ks_[0] != ks_[2]:
            wbad6.append("%s: tier sets differ / empty %s" % (iid_, [len(k_) for k_ in ks_]))
        if any(sets_[0].containsKey(k_) for k_ in full_):
            wbad6.append("%s: a charged / signature step is in the tap set" % iid_)
        if int(Spd.walk(iid_, JInt(1)).size()) != 0:
            wbad6.append("%s: Medium walks something" % iid_)
    check(not wbad6, "AG2: GearSpeed.walk on the engine model: every family's tap set is the same for Slow / Fast / Super Fast, never empty, "
                     "no charged / signature step in it, Medium walks nothing: %s" % wbad6)
    print("AG2. representative items: %s" % REP6)

    # ---- AG3. DPS equality through the REAL GearHit.weaponHit x the cadence of the jar's assets
    I6 = dict((os.path.basename(n_)[:-5], json.loads(mz6.read(n_).decode("utf-8-sig"))) for n_ in mz6.namelist()
              if n_.startswith("Server/Item/Interactions/") and n_.endswith(".json"))
    R6 = dict((os.path.basename(n_)[:-5], json.loads(mz6.read(n_).decode("utf-8-sig"))) for n_ in mz6.namelist()
              if n_.startswith("Server/Item/RootInteractions/") and n_.endswith(".json"))
    SD6 = g6["SpeedDur"]

    def cadence(f_, t_, iid_):
        vv_ = WK.item(iid_).get("InteractionVars") or {}
        tree_ = I6["SkyyGear_Spd_" + f_["fam"]]
        van_top = tree_["Next"]
        cd0_ = float((R6[f_["root"]].get("Cooldown") or {}).get("Cooldown", 0.35))
        if t_ == 1:
            st_ = SD6(I6, R6, vv_).steps([van_top])
            return sum(max(x_, cd0_) for x_ in st_), len(st_)
        node_ = tree_["Failed"]
        for tt_ in (0, 2, 3):
            if tt_ == t_:
                lf_ = node_["Next"]
                st_ = SD6(I6, R6, vv_).steps([lf_["Next"]])
                return sum(max(x_, lf_["Cooldown"]["Cooldown"]) for x_ in st_), len(st_)
            node_ = node_["Failed"]

    def sdoc(iid_, lv_, t_, mods_=()):
        d_ = Roll.newDoc(iid_, 0, True, "admin", lv_)
        ar_ = JClass("org.bson.BsonArray")()
        for k_, v_ in mods_:
            ar_.add(Data.mod(k_, v_))
        d_.put("mods", ar_)
        if t_ is None:
            d_.remove("spd")
        else:
            d_.put("spd", JClass("org.bson.BsonInt32")(t_))
        return d_

    def sstack(iid_, lv_, t_, mods_=()):
        return Data.put(IS(iid_, 1), sdoc(iid_, lv_, t_, mods_), U1)

    def apply_tier(u_, t_, prev_=None, ago_ms=60000):
        s_ = Spd.state(u_)
        L_ = s_[2]
        L_[2] = -1 if (t_ is None or t_ == 1) else t_
        L_[3] = L_[2] if prev_ is None else (-1 if prev_ == 1 else prev_)
        L_[4] = JClass("java.lang.System").currentTimeMillis() - ago_ms

    def hit(stack_, calc_, base_, shot_=False):
        d_ = DMGc(None, JInt(CIDX["Physical"]), JFloat(float(base_)))
        sq_ = UZ.allocateInstance(DSqc.class_)
        fz(DSqc, "damageCalculator").set(sq_, calc_)
        d_.putMetaObject(DCSYc.DAMAGE_SEQUENCE, sq_)
        r_ = Hit.weaponHit(d_, U1, None, stack_, shot_, None, None, None)
        return float(d_.getAmount()), r_
    MODS6 = [(), (("dmg", 20), ("str", 10)), (("dmg", 35), ("str", 25), ("cd", 40), ("tdmg", 9))]
    dps_bad, dps_rows, n_dps = [], [], 0
    for fam_, iid_ in sorted(REP6.items()):
        f_ = fams6[FAMS6.index(fam_)]
        taps_ = list(Spd.normals(iid_, JInt(2), False).keySet())
        bases_ = []
        for c_ in taps_:
            a_ = JArray(JFloat)(2)
            c_.computeDamageRange(1.0, a_)
            bases_.append(max(1.0, (float(a_[0]) + float(a_[1])) / 2.0))
        cyc_ = dict((t_, cadence(f_, t_, iid_)) for t_ in range(4))
        wj_ = [float(Spd.weight(FAMS6.index(fam_), t_)) for t_ in range(4)]
        for t_ in range(4):
            if abs(cyc_[t_][0] - cyc_[1][0] * wj_[t_]) > 1e-5 * cyc_[1][0] or cyc_[t_][1] != cyc_[1][1]:
                dps_bad.append("%s %s cycle %s vs %s x %s" % (fam_, TIERS[t_], cyc_[t_], cyc_[1], wj_[t_]))
        for lv_ in (1, 15, 30, 49):
            for mods_ in MODS6:
                dps_ = {}
                for t_ in range(4):
                    apply_tier(U1, t_)
                    st_ = sstack(iid_, lv_, t_, mods_)
                    tot_, td_ = 0.0, []
                    for c_, b_ in zip(taps_, bases_):
                        a_, r_ = hit(st_, c_, b_)
                        tot_ += a_
                        td_.append(int(r_[1]) if r_ is not None else 0)
                    per_ = tot_ / len(taps_)
                    dps_[t_] = (per_ * cyc_[t_][1] / cyc_[t_][0], per_, td_)
                    n_dps += 1
                for t_ in range(4):
                    if abs(dps_[t_][0] - dps_[1][0]) > 2e-5 * dps_[1][0] or abs(dps_[t_][1] - dps_[1][1] * wj_[t_]) > 1e-5 * dps_[1][1]:
                        dps_bad.append("%s Lv %d %s %s: DPS %.4f vs Medium %.4f (per hit %.4f vs %.4f)" % (fam_, lv_, mods_, TIERS[t_], dps_[t_][0], dps_[1][0], dps_[t_][1], dps_[1][1]))
                    if mods_ and dict(mods_).get("tdmg") and dps_[t_][2] and any(x_ not in (int(_mg.floor(9 * wj_[t_])), int(_mg.ceil(9 * wj_[t_]))) for x_ in dps_[t_][2]):
                        dps_bad.append("%s %s True Damage %s (want 9 x %s, stochastically rounded)" % (fam_, TIERS[t_], dps_[t_][2], wj_[t_]))
                if lv_ == 15 and mods_ == MODS6[1]:
                    dps_rows.append("%s %s: %s" % (fam_, iid_[7:], ", ".join("%s %.2f/hit %.2f DPS" % (TIERS[t_], dps_[t_][1], dps_[t_][0]) for t_ in range(4))))
    check(not dps_bad and n_dps == 9 * 4 * 3 * 4, "AG3: DAMAGE PER SECOND IDENTICAL on every tier - %d cases (9 families x Lv 1/15/30/49 x 3 modifier sets x 4 tiers) "
          "through the REAL GearHit.weaponHit on real Damage objects x the cadence of the jar's own tier chains + leaf cooldowns; per hit x w; "
          "True Damage x w (floor / ceil, the mean is checked in AG8): %s" % (n_dps, dps_bad[:5]))
    for r_ in dps_rows:
        print("AG3. Lv 15 +20% dmg +10 str: " + r_)
    # charged + projectile hits are never weighted; an excluded item / Medium / switched off = x1
    sw6 = REP6["Sword"]
    e_ = Chg.ensure(sw6)
    full6 = [k_ for k_ in e_[0].keySet() if int(e_[0].get(k_)[0]) == 1]
    tap6 = list(Spd.normals(sw6, JInt(2), False).keySet())
    apply_tier(U1, 3)
    sx_ = sstack(sw6, 15, 3)
    sm_ = sstack(sw6, 15, 1)
    check(full6 and all(abs(hit(sx_, c_, 26.0)[0] - hit(sm_, c_, 26.0)[0]) < 1e-6 for c_ in full6),
          "AG3: the sword's charged thrust (a FULL step) hits the same on Super Fast and Medium (holds are not re-timed, so never weighted)")
    check(abs(hit(sx_, tap6[0], 10.0, True)[0] - hit(sm_, tap6[0], 10.0, True)[0]) < 1e-6, "AG3: a projectile hit (shot) is never weighted")
    apply_tier(U1, None)
    m_none6 = hit(sm_, tap6[0], 10.0)[0]
    apply_tier(U1, 3)
    Spd.FORCE_OFF = True
    off_ = hit(sx_, tap6[0], 10.0)[0]
    Spd.FORCE_OFF = False
    check(abs(off_ - m_none6) < 1e-6 and abs(hit(sx_, tap6[0], 10.0)[0] - float(Spd.weight(0, 3)) * off_) < 1e-4,
          "AG3: switched off = x1 (tier and effect ignored); on = x0.5 for Super Fast")
    # the swap guard: min(the stored tier, the effect now, the one before it within 1.5 s)
    ss_ = sstack(sw6, 15, 0)
    apply_tier(U1, 0)
    a_slow = hit(ss_, tap6[0], 10.0)[0]
    apply_tier(U1, None)
    a_none = hit(ss_, tap6[0], 10.0)[0]
    apply_tier(U1, 0, prev_=3, ago_ms=200)
    a_swap = hit(ss_, tap6[0], 10.0)[0]
    apply_tier(U1, 0, prev_=3, ago_ms=2000)
    a_late = hit(ss_, tap6[0], 10.0)[0]
    apply_tier(U1, 3)
    a_fs = hit(ss_, tap6[0], 10.0)[0]
    ws0_, ws3_ = float(Spd.weight(0, 0)), float(Spd.weight(0, 3))
    check(abs(a_slow - ws0_ * a_none) < 1e-4 and abs(a_swap - ws3_ * a_none) < 1e-4 and abs(a_late - a_slow) < 1e-6 and abs(a_fs - ws3_ * a_none) < 1e-4,
          "AG3: the swap guard - a Slow sword hits x1.4 only while the Slow effect is on (no effect yet = x1, a Super Fast effect = x0.5, the "
          "Super Fast effect of 0.2 s ago = x0.5, of 2 s ago = forgotten): %.3f / %.3f / %.3f / %.3f / %.3f" % (a_slow, a_none, a_swap, a_late, a_fs))
    st0_ = Spd.N.get(3)
    hit(ss_, full6[0], 10.0)
    check(int(Spd.N.get(3)) == int(st0_) + 1, "AG3: a hit that is not a tap step is counted (N[3]) and kept x1")
    print("AG3. DPS equality done")

    # ---- AG4. existing items get a tier ONCE (first touch = the stamp scan), identify, reforge / level up / clones keep it, the sig
    olds_ = []
    cnt_ = [0, 0, 0, 0]
    same_ = 0
    for k_ in range(3000):
        iid_ = REP6[FAMS6[k_ % 9]]
        s0_ = IS(iid_, 1).withMetadata(JClass("org.bson.BsonDocument")(str(JClass(PKG + "GearDefs").DOC_KEY), sdoc(iid_, 15, None)))
        if int(Spd.tierOf(Data.gearDoc(s0_.getMetadata()))) != -1:
            same_ = -99999
        s1_ = Stamp.stampStack(s0_, U1, JArray(JInt)(3))
        t1_ = int(Spd.tierOf(Data.gearDoc(s1_.getMetadata())))
        cnt_[t1_] += 1
        s2_ = Stamp.stampStack(s1_, U1, JArray(JInt)(3))
        if s2_ == s1_ or (s2_.getMetadata() is not None and s2_.getMetadata().equals(s1_.getMetadata())):
            same_ += 1
    check(sum(cnt_) == 3000 and all(abs(x_ / 3000.0 - 0.25) < 0.035 for x_ in cnt_) and same_ == 3000,
          "AG4: FIRST TOUCH - 3 000 old (0.2.5) documents of the 9 families get a tier on their first stamp scan (Slow / Medium / Fast / Super Fast "
          "%s) and a second scan changes nothing (%d / 3000 unchanged)" % (cnt_, same_))
    ex_ = []
    for iid_ in ("Weapon_Sword_Crude", "Weapon_Wand_Wood", "Weapon_Shortbow_Iron", "Weapon_Crossbow_Iron", "Weapon_Staff_Iron"):
        if WK.item(iid_) is not None:
            d_ = sdoc(iid_, 15, None)
            if not same(Spd.ensure(iid_, d_), d_):
                ex_.append(iid_)
    for iid_ in TOOLS6:
        d_ = Data.legacy(iid_)
        if not same(Spd.ensure(iid_, d_), d_) or int(Spd.tierOf(Data.gearDoc(Stamp.stampStack(IS(iid_, 1), U1, JArray(JInt)(3)).getMetadata()) or d_)) != -1:
            ex_.append(iid_)
    check(not ex_, "AG4: no tier is ever rolled on an excluded weapon (Crude sword), a wand / staff, a bow / crossbow or a TOOL (pickaxe, hatchet, "
                   "shovel, hoe, sickle): %s" % ex_)
    u_ = Roll.newDoc(sw6, 2, False, "drop", 15)
    check(int(Spd.tierOf(u_)) == -1 and same(Spd.ensure(sw6, u_), u_), "AG4: an unidentified weapon has no tier yet")
    idd_ = Roll.identify(sw6, u_, U1)
    check(int(Spd.tierOf(idd_)) in (0, 1, 2, 3) and int(Spd.tierOf(u_)) == -1, "AG4: identify rolls it (a clone; the unidentified document is untouched)")
    Spd.FORCE_OFF = True
    off_d = Roll.identify(sw6, u_, U1)
    Spd.FORCE_OFF = False
    check(int(Spd.tierOf(off_d)) == -1, "AG4: switched off: identify rolls no tier (it rolls on the item's next write once switched on)")
    kept_ = []
    for t_ in range(4):
        d_ = sdoc(sw6, 15, t_, (("dmg", 10),))
        for nm_, nd_ in (("reforge", Roll.reforge(sw6, d_)), ("level up", Roll.levelUp(sw6, d_, 16)), ("clone", d_.clone())):
            if int(Spd.tierOf(nd_)) != t_ or int(Spd.tierOf(Data.gearDoc(Data.put(IS(sw6, 1), nd_, U1).getMetadata()))) != t_:
                kept_.append((TIERS[t_], nm_))
    check(not kept_, "AG4: REFORGE keeps the tier (and level up, /gear clones, every rewrite through GearData.put): %s" % kept_)
    gd_ = Roll.newDoc(sw6, 3, True, "admin", 20)
    check(int(Spd.tierOf(gd_)) in (0, 1, 2, 3), "AG4: a new identified weapon (craft / admin give) gets its tier at once")
    a1_ = sdoc(sw6, 15, 0)
    a2_ = a1_.clone()
    a2_.put("spd", JClass("org.bson.BsonInt32")(3))
    a3_ = a1_.clone()
    a3_.remove("spd")
    check(str(View.bridgeSig(sw6, 0, a1_)) != str(View.bridgeSig(sw6, 0, a2_)) and str(View.bridgeSig(sw6, 0, a1_)) == str(View.bridgeSig(sw6, 0, a1_.clone())),
          "AG4: gear:fn:sig - two items that differ only in their tier differ (the AH's 'rolls differ')")
    rs_ = Spd.ROLLS.get()
    print("AG4. first touch / identify / reforge done (%d rolls so far)" % int(rs_))

    # ---- AG5. the tooltip, gear:fn:speed, Mana per cast, /gear read
    def tip(iid_, d_):
        tx_, co_ = ArrayList(), ArrayList()
        View.lines(iid_, d_, None, tx_, co_)
        return [str(x_) for x_ in tx_]
    tbad = []
    for t_ in range(4):
        d_ = sdoc(sw6, 15, t_)
        ls_ = tip(sw6, d_)
        f_ = fams6[0]
        r_ = list(Spd.tapRange(sw6, JInt(t_)))
        m_ = float(Base.mult(sw6, d_, False))
        w_ = float(Spd.weight(0, t_))
        want_ = "Damage at Lv 15: %s per hit" % str(Base.rangeText(JArray(JFloat)([r_[0] * m_ * w_, r_[1] * m_ * w_])))
        c_ = list(Spd.chargedRange(sw6))
        wantc_ = "Charged at Lv 15: %s" % str(Base.rangeText(JArray(JFloat)([c_[0] * m_, c_[1] * m_])))
        i_ = ls_.index("Attack Speed: " + TIERS[t_]) if ("Attack Speed: " + TIERS[t_]) in ls_ else -1
        if i_ < 0 or ls_[i_ + 1] != want_ or ls_[i_ + 2] != wantc_ or any(l_.startswith("Damage at Lv 15: ") and not l_.endswith(" per hit") for l_ in ls_):
            tbad.append((TIERS[t_], ls_[:6], want_, wantc_))
        if t_ == 3:
            print("AG5. Super Fast Lv 15 %s tooltip: %s" % (sw6, ls_[:5]))
        if t_ == 1:
            print("AG5. Medium Lv 15 %s tooltip: %s" % (sw6, ls_[:5]))
    check(not tbad, "AG5: TOOLTIP 'Attack Speed: <tier>' + 'Damage at Lv 15: a-b per hit' (the tap steps x the level multiplier x w) + 'Charged at Lv 15: "
                    "x-y' (x1) on every tier: %s" % tbad[:2])
    sp3 = tip(sw6, sdoc(sw6, 15, 2, (("dmg", 12),)))
    check(any(l_.endswith(" per hit (+12%)") for l_ in sp3), "AG5: the Damage %% roll rides on the per-hit line: %s" % sp3[:4])
    Spd.FORCE_OFF = True
    offl_ = tip(sw6, sdoc(sw6, 15, 3))
    Spd.FORCE_OFF = False
    check(not any(l_.startswith("Attack Speed") or l_.endswith("per hit") for l_ in offl_) and any(l_.startswith("Damage at Lv 15: ") for l_ in offl_),
          "AG5: switched off - no speed line, the 0.2.5 damage line: %s" % offl_[:3])
    crl_ = tip("Weapon_Sword_Crude", sdoc("Weapon_Sword_Crude", 5, 3))
    check(not any(l_.startswith("Attack Speed") for l_ in crl_), "AG5: an excluded item (Crude sword) shows no speed line even with a stored tier")
    tll_ = tip("Tool_Pickaxe_Iron", Data.legacy("Tool_Pickaxe_Iron"))
    check(not any(l_.startswith("Attack Speed") for l_ in tll_), "AG5: a tool shows no speed line")
    fsp_ = J("GearFn")(11)
    su6 = code("SkyyGearPlugin", "setup")
    check(any('"gear:fn:speed"' in l_ and i_ + 1 < len(su6) and "GearFn" in su6[i_ + 1] for i_, l_ in enumerate(su6)),
          "AG5: setup() registers gear:fn:speed as a GearFn (bytecode)")
    a_ = fsp_.apply(sstack(sw6, 15, 2))
    b_ = fsp_.apply(OAc([sw6, sstack(sw6, 15, 0).getMetadata()]))
    c_ = fsp_.apply(OAc(["Weapon_Sword_Crude", sstack("Weapon_Sword_Crude", 5, 0).getMetadata()]))
    check(fsp_ is not None and a_ is not None and list(a_)[0] == "Fast" and abs(float(a_[1]) - float(Spd.weight(0, 2))) < 1e-12 and abs(float(a_[1]) - 0.7) < 1e-3
          and bool(a_[2]) and int(a_[3]) == 2 and str(a_[4]) == "Sword" and b_ is not None and str(b_[0]) == "Slow" and fsp_.apply(IS("Tool_Pickaxe_Iron", 1)) is None
          and c_ is None and fsp_.apply(None) is None, "AG5: gear:fn:speed answers { tier, w, active, index, family } for a stack / {id, metadata}; null for a "
          "tool / an excluded item / bad input: %s / %s / %s" % (None if a_ is None else list(a_), None if b_ is None else list(b_), c_))
    mbad = []
    for base_ in (1, 2, 5, 17, 85):
        for t_ in range(4):
            w_ = fams6[0]["f"][t_]
            c_ = float(Spd.manaCost(float(base_), w_))
            if abs(c_ - _mg.floor(base_ * w_ * 10 + 0.5) / 10.0) > 1e-9:
                mbad.append((base_, t_, c_))
            dmg_ = 10.0 * base_ * w_
            if abs(dmg_ / (base_ * w_) - 10.0) > 1e-9:
                mbad.append((base_, t_, "dpm"))
    check(not mbad and float(Spd.manaCost(2.0, 1.4)) == 2.8 and float(Spd.manaCost(2.0, 0.7)) == 1.4 and float(Spd.manaCost(2.0, 0.5)) == 1.0
          and float(Spd.manaCost(0.0, 1.4)) == 0.0 and float(Spd.manaCost(3.0, -1.0)) == 3.0,
          "AG5: MANA PER CAST = base x w in tenths (Copper quick 2 Mana: Slow 2.8, Fast 1.4, Super Fast 1.0); damage per Mana equal on every tier "
          "(no staff / wand has a tier in 0.2.6 - SkyyArmory's pass): %s" % mbad)
    rd_ = str(Spd.describe(sw6, sdoc(sw6, 15, 2), U1))
    check(rd_.startswith("weapon speed: Sword family (SkyyGear's swing root loaded), Fast - swing time and hit x0.7")
          and "tools never" in str(Spd.describe("Tool_Pickaxe_Iron", Data.legacy("Tool_Pickaxe_Iron"), U1)), "AG5: /gear read line: %s" % rd_[:160])
    rt_ = str(Spd.readyText())
    print("AG5. ready text: " + rt_)
    print("AG5. tooltip / gear:fn:speed / Mana done")

    # ---- AG6. the tier effect on a REAL EffectControllerComponent (ECS shim) + the hit weight following it
    EFXc = JClass(ENG + "asset.type.entityeffect.config.EntityEffect")
    OVBc = JClass(ENG + "asset.type.entityeffect.config.OverlapBehavior")
    RMBc = JClass(ENG + "asset.type.entityeffect.config.RemovalBehavior")
    ECCc = JClass(ENG + "entity.effect.EffectControllerComponent")
    fx6 = {}
    for nm_ in ("SkyyGear_Speed_Slow", "SkyyGear_Speed_Fast", "SkyyGear_Speed_SuperFast", "Some_Other_Effect"):
        o_ = EFXc(nm_)
        acf(EFXc.class_.getName(), "duration").setFloat(o_, JFloat(2.0))
        acf(EFXc.class_.getName(), "overlapBehavior").set(o_, OVBc.OVERWRITE)
        acf(EFXc.class_.getName(), "removalBehavior").set(o_, RMBc.values()[0])
        fx6[nm_] = o_
    fstore_ = acf(EFXc.class_.getName(), "STORE")
    old_fx6 = fstore_.get(None)
    fstore_.set(None, zstore(indexed(fx6)))
    Spd.IDX = None
    Spd.IDX_NEXT = 0
    check(bool(Spd.ready()) and [int(x_) for x_ in Spd.IDX] == [0, -1, 1, 2], "AG6: ready() resolves the three tier effects (Medium = none)")
    ecc6 = ECCc()
    ref6 = mkref(61)
    putc(ref6, "ecc", ecc6)
    U6 = UUID.fromString("00000000-0000-0000-0000-0000000000c6")
    Spd.forget(U6)

    def act():
        m_ = ecc6.getActiveEffects()
        return sorted(str(fx6[k_].getId()) for k_ in fx6 if m_.get(JInt(int(EFXc.getAssetMap().getIndex(k_)))) is not None)
    ebad = []
    s_slow, s_fast, s_med = sstack(sw6, 15, 0), sstack(sw6, 15, 2), sstack(sw6, 15, 1)
    Spd.tick(buf_, ref6, U6, s_slow)
    if act() != ["SkyyGear_Speed_Slow"]:
        ebad.append(("slow", act()))
    Spd.tick(buf_, ref6, U6, s_slow)
    if act() != ["SkyyGear_Speed_Slow"]:
        ebad.append(("slow again", act()))
    Spd.tick(buf_, ref6, U6, s_fast)
    if act() != ["SkyyGear_Speed_Fast"]:
        ebad.append(("swap to fast", act()))
    L6 = Spd.state(U6)[2]
    if not (int(L6[2]) == 2 and int(L6[3]) == 0):
        ebad.append(("applied / prev", int(L6[2]), int(L6[3])))
    Spd.tick(buf_, ref6, U6, s_med)
    if act() != []:
        ebad.append(("medium", act()))
    Spd.tick(buf_, ref6, U6, sstack("Weapon_Sword_Crude", 5, 3))
    Spd.tick(buf_, ref6, U6, s_fast)
    if act() != ["SkyyGear_Speed_Fast"]:
        ebad.append(("fast again", act()))
    Spd.tick(buf_, ref6, U6, IS("Tool_Pickaxe_Iron", 1))
    if act() != []:
        ebad.append(("tool", act()))
    Spd.tick(buf_, ref6, U6, s_fast)
    Spd.FORCE_OFF = True
    Spd.state(U6)[2][0] = 0
    Spd.tick(buf_, ref6, U6, s_fast)
    if act() != []:
        ebad.append(("switched off", act()))
    Spd.FORCE_OFF = False
    # the refresh: an effect with under 1 s left is renewed on the 1 s re-check
    Spd.state(U6)[2][0] = 0
    Spd.tick(buf_, ref6, U6, s_slow)
    ae_ = ecc6.getActiveEffects().get(JInt(int(Spd.IDX[0])))
    acf(JClass(ENG + "entity.effect.ActiveEntityEffect").class_.getName(), "remainingDuration").setFloat(ae_, JFloat(0.4))
    Spd.state(U6)[2][1] = 0
    Spd.tick(buf_, ref6, U6, s_slow)
    rem_ = float(ecc6.getActiveEffects().get(JInt(int(Spd.IDX[0]))).getRemainingDuration())
    if not rem_ > 2.5:
        ebad.append(("refresh", rem_))
    check(not ebad and int(Spd.N.get(0)) >= 5 and int(Spd.N.get(1)) >= 4, "AG6: GearSpeed.tick on a REAL EffectControllerComponent: the held tier's effect on (2 s), "
          "the others off; swap Slow -> Fast; Medium / an excluded item / a TOOL / switched off = no effect; refreshed to 3 s under 1.5 s left: %s" % ebad)
    # the hit weight follows the effect GearSpeed applied (U6's state)
    Spd.tick(buf_, ref6, U6, s_slow)
    d_ = DMGc(None, JInt(CIDX["Physical"]), JFloat(10.0))
    sq_ = UZ.allocateInstance(DSqc.class_)
    fz(DSqc, "damageCalculator").set(sq_, tap6[0])
    d_.putMetaObject(DCSYc.DAMAGE_SEQUENCE, sq_)
    w_now = float(Spd.hitWeight(d_, U6, s_slow))
    Spd.state(U6)[2][4] = JClass("java.lang.System").currentTimeMillis() - 1500
    w_later = float(Spd.hitWeight(d_, U6, s_slow))
    check(abs(w_now - 1.0) < 1e-9 and abs(w_later - float(Spd.weight(0, 0))) < 1e-9, "AG6: the hit weight follows the effect GearSpeed put on: right after Slow went on "
          "(no effect before) x1 (the swap window), a moment later x1.4 (%.2f / %.2f)" % (w_now, w_later))
    # ---- AG8 (fix round, on the same REAL EffectControllerComponent): the effect record kept true, the first tick, 3 s / 1.5 s, the sweep
    AEEc6 = JClass(ENG + "entity.effect.ActiveEntityEffect").class_.getName()
    k8bad = []
    Spd.forget(U6)
    Spd.put(buf_, ref6, ecc6, JInt(3))
    if act() != ["SkyyGear_Speed_SuperFast"]:
        k8bad.append(("stray put", act()))
    Spd.tick(buf_, ref6, U6, s_med)
    L8 = Spd.state(U6)[2]
    if act() != [] or int(L8[2]) != -1:
        k8bad.append(("first tick keeps a stray effect", act(), int(L8[2])))
    Spd.tick(buf_, ref6, U6, s_slow)
    L8 = Spd.state(U6)[2]
    L8[4] = JClass("java.lang.System").currentTimeMillis() - 5000
    lost0_ = int(Spd.N.get(8))
    ecc6.removeEffect(ref6, JInt(int(Spd.IDX[0])), buf_)
    w_stale = float(Spd.hitWeight(d_, U6, s_slow))
    Spd.tick(buf_, ref6, U6, s_slow)
    w_lost = float(Spd.hitWeight(d_, U6, s_slow))
    if not (int(Spd.N.get(8)) == lost0_ + 1 and act() == ["SkyyGear_Speed_Slow"] and int(L8[2]) == 0 and int(L8[3]) == -1 and abs(w_lost - 1.0) < 1e-9):
        k8bad.append(("lost effect", int(Spd.N.get(8)) - lost0_, act(), int(L8[2]), int(L8[3]), w_stale, w_lost))
    L8[4] = JClass("java.lang.System").currentTimeMillis() - 5000
    if abs(float(Spd.hitWeight(d_, U6, s_slow)) - float(Spd.weight(0, 0))) > 1e-9:
        k8bad.append(("after the window", float(Spd.hitWeight(d_, U6, s_slow))))
    # the refresh threshold: 1.6 s left stays, 1.4 s left is put back to 3 s
    ae8 = ecc6.getActiveEffects().get(JInt(int(Spd.IDX[0])))
    acf(AEEc6, "remainingDuration").setFloat(ae8, JFloat(1.6))
    L8[1] = 0
    Spd.tick(buf_, ref6, U6, s_slow)
    r16_ = float(ecc6.getActiveEffects().get(JInt(int(Spd.IDX[0]))).getRemainingDuration())
    acf(AEEc6, "remainingDuration").setFloat(ecc6.getActiveEffects().get(JInt(int(Spd.IDX[0]))), JFloat(1.4))
    L8[1] = 0
    Spd.tick(buf_, ref6, U6, s_slow)
    r14_ = float(ecc6.getActiveEffects().get(JInt(int(Spd.IDX[0]))).getRemainingDuration())
    if not (abs(r16_ - 1.6) < 1e-5 and abs(r14_ - 3.0) < 1e-5):
        k8bad.append(("refresh 1.6 / 1.4", r16_, r14_))
    check(not k8bad, "AG8: (engine critic 1 + 2) the effect record is kept TRUE every tick: the first tick of a player removes a stray tier "
          "effect, an effect the player lost is noted at once (N[8]), put back, and the next hits weigh x1 inside the window (the swing ran "
          "vanilla), x1.4 after; the effect is 3 s and re-put only under 1.5 s left: %s" % k8bad)
    # the idle-state sweep (a disconnect that raced one more tick)
    nowj_ = int(JClass("java.lang.System").currentTimeMillis())
    Ugone = UUID.fromString("00000000-0000-0000-0000-0000000000c8")
    Spd.state(Ugone)[2][5] = nowj_ - 200000
    Spd.SWEEP_AT = 0
    sw1_ = int(Spd.sweep(nowj_))
    sw2_ = int(Spd.sweep(nowj_))
    check(sw1_ >= 1 and Spd.ST.get(Ugone) is None and Spd.ST.get(U6) is not None and sw2_ == 0,
          "AG8: (engine critic 6) states untouched for 2 minutes are swept (at most once a minute), live ones kept: %d / %d" % (sw1_, sw2_))
    fstore_.set(None, old_fx6)
    AcBuf.COMP.remove(ref6)
    Spd.IDX = None
    print("AG6. tier effect done")

    # ---- AG8. the FIX ROUND (critics 2026-10-06): one check per fix
    # (DPS critic 2) True Damage / flat element sum x w with STOCHASTIC rounding: the mean is exactly v x w (Math.round was +100% for TD 1 SF)
    r8bad = []
    if not (int(Spd.sround(12.6, 0.5)) == 13 and int(Spd.sround(12.6, 0.7)) == 12 and int(Spd.sround(5.0, 0.99)) == 5 and int(Spd.sround(0.0, 0.1)) == 0):
        r8bad.append("sround")
    for v_ in (1, 2, 3, 5, 9, 14):
        for w_ in (1.4, 0.7, 0.5, 0.724638):
            tot_ = 0
            n8_ = 4000
            for _i in range(n8_):
                inf_ = JArray(JClass("java.lang.Object"))(6)
                inf_[1] = JClass("java.lang.Integer").valueOf(v_)
                inf_[5] = JClass("java.lang.Integer").valueOf(v_)
                Spd.scaleInfo(inf_, w_)
                if int(inf_[1]) not in (int(_mg.floor(v_ * w_)), int(_mg.ceil(v_ * w_))):
                    r8bad.append(("range", v_, w_, int(inf_[1])))
                    break
                tot_ += int(inf_[1]) + int(inf_[5])
            mean_ = tot_ / (2.0 * n8_)
            if abs(mean_ - v_ * w_) > max(0.035 * v_ * w_, 0.03):
                r8bad.append(("mean", v_, w_, round(mean_, 4)))
    check(not r8bad, "AG8: (DPS critic 2) True Damage / the flat element sum x w are STOCHASTICALLY rounded - every value floor or ceil of v x w, "
          "the mean of 8 000 draws within 3.5%% of v x w for v 1/2/3/5/9/14 x w 1.4/0.7/0.5/0.7246 (so the flat part of DPS is equal too): %s" % r8bad[:4])

    # (DPS critic 1 + 3) stats on hit (SignatureEnergy) + knockback x w through GearHit.weaponHit -> GearSpeed.perHit, then the ENGINE's own
    # SequenceModifier (after the Filter group) on a REAL EntityStatMap: the meter gain per hit = w x the vanilla gain, so per second it is equal
    ESOHc = JClass(ENG + "modules.interaction.interaction.config.server.DamageEntityInteraction$EntityStatOnHit")
    SEQc = JClass(ENG + "modules.entity.damage.DamageCalculatorSystems$Sequence")
    SMODc = JClass(ENG + "modules.entity.damage.DamageCalculatorSystems$SequenceModifier")
    ESRCc = JClass(ENG + "modules.entity.damage.Damage$EntitySource")
    KBCc = JClass(ENG + "entity.knockback.KnockbackComponent")
    V3c = JClass("org.joml.Vector3d")
    esoh8 = UZ.allocateInstance(ESOHc.class_)
    acf(ESOHc.class_.getName(), "entityStatIndex").setInt(esoh8, JInt(HP_I))
    acf(ESOHc.class_.getName(), "amount").setFloat(esoh8, JFloat(5.0))
    acf(ESOHc.class_.getName(), "multipliersPerEntitiesHit").set(esoh8, JArray(JFloat)([1.0, 0.5]))
    acf(ESOHc.class_.getName(), "multiplierPerExtraEntityHit").setFloat(esoh8, JFloat(0.25))
    smod8 = UZ.allocateInstance(SMODc.class_)
    refA8, refV8 = mkref(81), mkref(82)
    ss8 = sstack(sw6, 15, 0)
    p8bad, p8rows = [], []
    for t_ in range(4):
        for cancel_ in (False, True):
            sm8 = ESMc()
            sm8.update()
            putc(refA8, "esm", sm8)
            sm8.addStatValue(JInt(HP_I), JFloat(-50.0))
            kc8 = KBCc()
            putc(refV8, "kb", kc8)
            apply_tier(U1, t_)
            d8 = DMGc(ESRCc(refA8), JInt(CIDX["Physical"]), JFloat(10.0))
            sq8 = UZ.allocateInstance(DSqc.class_)
            fz(DSqc, "damageCalculator").set(sq8, tap6[0])
            fz(DSqc, "sequence").set(sq8, UZ.allocateInstance(SEQc.class_))
            sq8.setEntityStatOnHit(JArray(ESOHc)([esoh8]))
            d8.putMetaObject(DCSYc.DAMAGE_SEQUENCE, sq8)
            h0_ = float(sm8.get(JInt(HP_I)).get())
            Hit.weaponHit(d8, U1, None, ss8, False, None, None, None)
            if cancel_:
                d8.setCancelled(True)
            Spd.perHit(d8, buf_, refA8, refV8)
            if Spd.LAST.get() is not None:
                p8bad.append(("LAST kept", t_))
            if not cancel_:
                smod8.handle(0, None, None, buf_, d8)
            gain_ = float(sm8.get(JInt(HP_I)).get()) - h0_
            kc8.setVelocity(V3c(2.0, 0.0, 0.0))
            kc8.applyModifiers()
            kx_ = float(kc8.getVelocity().x())
            w8 = float(Spd.weight(0, t_))
            if not cancel_:
                p8rows.append("%s: meter +%.3f, knockback x%.3f" % (TIERS[t_], gain_, kx_ / 2.0))
                if abs(gain_ - 5.0 * w8) > 1e-4 or abs(kx_ - 2.0 * w8) > 1e-6:
                    p8bad.append((TIERS[t_], gain_, kx_))
            elif abs(gain_) > 1e-6 or abs(kx_ - 2.0) > 1e-9:
                p8bad.append(("cancelled", TIERS[t_], gain_, kx_))
    # the 2nd entity of one swing (getSequentialHits 1): the engine's array[1] = 0.5, the extra follows it
    ext_ = [float(Spd.statExtra(JFloat(5.0), JArray(JFloat)([1.0, 0.5]), JFloat(0.25), JInt(h_), 1.4)) for h_ in (1, 2, 3)]
    if not (abs(ext_[0] - 2.0) < 1e-5 and abs(ext_[1] - 1.0) < 1e-5 and abs(ext_[2] - 0.5) < 1e-5 and float(Spd.statExtra(JFloat(5.0), None, JFloat(0.25), JInt(1), 1.0)) == 0.0):
        p8bad.append(("statExtra", ext_))
    AcBuf.COMP.remove(refA8)
    AcBuf.COMP.remove(refV8)
    check(not p8bad, "AG8: (DPS critic 1 + 3) a weighted tap also weighs the attacker's STATS ON HIT (SignatureEnergy) and the victim's KNOCKBACK "
          "- GearHit.weaponHit -> GearSpeed.perHit -> the engine's own SequenceModifier on a REAL EntityStatMap: the meter gain per hit = w x "
          "the vanilla gain, the knockback = w x (KnockbackComponent.applyModifiers); a cancelled hit gets neither; the per-entity multiplier "
          "is followed: %s" % (p8bad[:4] or p8rows))
    for r_ in p8rows:
        print("AG8. per hit, vanilla meter +5: " + r_)

    # (engine critic 3 + 4, DPS critic 4) the hit weight = the tier the swing RAN (the effect), the stored tier is not consulted
    sf8 = sstack(sw6, 15, 2)
    apply_tier(U1, None)
    a_fast_noeff = hit(sf8, tap6[0], 10.0)[0]
    a_med_noeff = hit(sm_, tap6[0], 10.0)[0]
    apply_tier(U1, 3)
    a_med_sf = hit(sm_, tap6[0], 10.0)[0]
    crude8 = "Weapon_Sword_Crude"
    ctaps8 = list(Spd.normals(crude8, JInt(2), False).keySet())
    cs8 = sstack(crude8, 5, None)
    a_cr_sf = hit(cs8, ctaps8[0], 10.0)[0] if ctaps8 else -1.0
    apply_tier(U1, None)
    a_cr_none = hit(cs8, ctaps8[0], 10.0)[0] if ctaps8 else -1.0
    apply_tier(U1, 3)
    a_tool = hit(IS("Tool_Pickaxe_Iron", 1), tap6[0], 10.0)[0]
    apply_tier(U1, None)
    a_tool0 = hit(IS("Tool_Pickaxe_Iron", 1), tap6[0], 10.0)[0]
    wm8, wx8, ws8 = float(Spd.weight(0, 1)), float(Spd.weight(0, 3)), float(Spd.weight(0, 0))
    check(abs(a_fast_noeff - a_med_noeff) < 1e-6 and abs(a_med_sf - wx8 * a_med_noeff) < 1e-4 and int(Spd.famOf(crude8)) == -1
          and int(Spd.rootFam(crude8)) == 0 and ctaps8 and abs(a_cr_sf - wx8 * a_cr_none) < 1e-4 and abs(a_tool - a_tool0) < 1e-9,
          "AG8: (engine critic 3 + 4) the hit weight is the tier the swing RAN: a Fast sword with no effect on (the swing was vanilla) x1 (was "
          "x0.7); a Medium sword / the tier-less Crude sword (same replaced root) under a lagging Super Fast effect x0.5 (was x1); a tool x1: "
          "%.3f / %.3f / %.3f / %.3f / %.3f" % (a_fast_noeff, a_med_noeff, a_med_sf, a_cr_sf, a_cr_none))
    wn8 = [int(Spd.winMs(JInt(0), JInt(t_))) for t_ in range(4)]
    apply_tier(U1, 0, prev_=1, ago_ms=wn8[1] + 60)
    a_after = hit(ss_, tap6[0], 10.0)[0]
    apply_tier(U1, 0, prev_=1, ago_ms=max(0, wn8[1] - 100))
    a_inside = hit(ss_, tap6[0], 10.0)[0]
    apply_tier(U1, 0, prev_=3, ago_ms=max(0, wn8[3] - 60))
    a_from_sf = hit(ss_, tap6[0], 10.0)[0]
    wall8 = dict((str(f_["fam"]), [int(Spd.winMs(JInt(i_), JInt(t_))) for t_ in range(4)]) for i_, f_ in enumerate(fams6))
    check(wn8[1] < 1000 and abs(a_after - ws8 * a_med_noeff) < 1e-4 and abs(a_inside - wm8 * a_med_noeff) < 1e-4 and abs(a_from_sf - wx8 * a_med_noeff) < 1e-4
          and all(v_[0] > v_[1] > v_[2] >= v_[3] > 150 for v_ in wall8.values()),
          "AG8: (DPS critic 4) the swap window is the previous tier's longest tap step + 150 ms, not a flat 1 s: a Slow sword after Medium hits "
          "x1.4 from %d ms on (x1 inside it), after Super Fast x0.5 inside its %d ms; windows per family (Slow/Medium/Fast/Super Fast ms): %s"
          % (wn8[1], wn8[3], wall8))
    apply_tier(U1, None)

    # (data critic 1, engine critic 5) famOf: a miss is never cached, the cache drops on a config epoch move and on the Item reload listener
    Spd.FAM.clear()
    miss8 = "Weapon_Sword_NotLoaded_SkyyTest"
    f_miss = int(Spd.famOf(miss8))
    cached_miss = bool(Spd.FAM.containsKey(miss8))
    Spd.famOf(sw6)
    had_sw = bool(Spd.FAM.containsKey(sw6))
    Cfg.EPOCH = int(Cfg.EPOCH) + 1
    Spd.famOf("Weapon_Axe_Iron")
    ep_cleared = not bool(Spd.FAM.containsKey(sw6))
    Spd.famOf(sw6)
    Spd.IDX = JArray(JInt)([0, -1, 1, 2])
    Spd.normals(sw6, JInt(2), False)
    J("GearBoxL")().accept("not an event")
    rs_ok = int(Spd.FAM.size()) == 0 and Spd.IDX is None and int(Spd.NORM.size()) == 0 and Spd.ACT is None
    check(f_miss == -1 and not cached_miss and had_sw and ep_cleared and rs_ok,
          "AG8: (data critic 1, engine critic 5) famOf never caches an item that is not loaded; the family cache drops when GearCfg.EPOCH moves "
          "(a live gear.exclude edit); the Item reload listener (GearBoxL.accept) runs GearSpeed.reset() - families, tap sets, root check and "
          "effect indices rebuilt on next use: %s %s %s %s %s" % (f_miss, cached_miss, had_sw, ep_cleared, rs_ok))
    # (engine critic 3) the tooltip claims no tier while the tier effects failed to load
    dF8 = sdoc(sw6, 15, 2)
    Spd.IDX = None
    Spd.IDX_TOLD = True
    no_line = not bool(Spd.shows(sw6, dF8))
    Spd.IDX_TOLD = False
    yes_line = bool(Spd.shows(sw6, dF8))
    check(no_line and yes_line, "AG8: (engine critic 3) no 'Attack Speed' line while the tier effects failed to load (they would not swing tiered); "
          "shown again once they load (IDX_TOLD reset)")
    print("AG8. fix round done")

    # ---- AG7. start twice on a scratch COPY of the live Skyy_SkyyGear folder (read only): the whole setup() file chain, then again
    MD6 = os.path.join(SCRATCH, "work", "mc026")
    shutil.rmtree(MD6, ignore_errors=True)
    if os.path.isfile(LIVE):
        d7_ = os.path.join(MD6, "live", "mods", "Skyy_SkyyGear")
        shutil.copytree(os.path.dirname(LIVE), d7_)
        cfg_quiet()
        Cfg.DIR = Paths.get(d7_)
        Cfg.FILE = Paths.get(os.path.join(d7_, "config.properties"))
        Log.FILE = None

        def chain7():
            Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(d7_, "..", "Skyy_SkyyRolls", "reforge.properties")))
            for m_ in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025"):
                getattr(Cfg, m_)()
            Cfg.load()

        def snap7(dd_):
            out_ = {}
            for rt_, _ds, fs_ in os.walk(dd_):
                for fn_ in fs_:
                    if fn_ != "gear.log":
                        out_[os.path.relpath(os.path.join(rt_, fn_), dd_)] = rb(os.path.join(rt_, fn_))
            return out_
        s0_ = snap7(d7_)
        chain7()
        s1_ = snap7(d7_)
        chain7()
        s2_ = snap7(d7_)
        lp_ = props(s1_["config.properties"].decode("latin-1"))
        check(s1_ == s2_ and "swing.tiers" not in lp_ and "swing.odds" not in lp_ and bool(Cfg.SWING_ON) and list(Cfg.SWING_W) == [25.0] * 4,
              "AG7: START TWICE on a scratch copy of the live folder (%d files, %s): the second start changes no file; no speed key is written (no "
              "one-time update) and the loader reads the defaults (on, 25/25/25/25)" % (len(s1_), "already 0.2.5-shaped" if s0_ == s1_ else "0.2.5 update ran once"))
        Cfg.FILE = None
        Cfg.DIR = None
        Cfg.apply(Props(), False)
        cfg_quiet()
    else:
        check(False, "AG7: no live config.properties at %s - the live start-twice check could not run" % LIVE)
    shutil.rmtree(MD6, ignore_errors=True)
    print("AG7. live copy done")

    # ---- AG10. class byte-compare 0.2.5 -> 0.2.6
    EXPECT026 = @@EXPECT026@@
    jar025 = os.path.join(HERE, "SkyyGear-0.2.5.jar")
    if os.path.isfile(jar025) and "cls_members" in dir():
        pa9 = Pool(False)
        pa9.appendClassPath(jar025)
        pa9.appendClassPath(B.SERVER_JAR)
        pa9.appendSystemPath()
        pb9 = Pool(False)
        pb9.appendClassPath(jar)
        pb9.appendClassPath(B.SERVER_JAR)
        pb9.appendSystemPath()
        na9 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar025).namelist() if n_.endswith(".class"))
        nb9 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
        diffs9 = {}
        for cn_ in sorted(set(na9) & set(nb9)):
            ma_, mb_ = cls_members(pa9, cn_), cls_members(pb9, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs9[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        print("AG10. class compare 0.2.5 -> 0.2.6: %s" % json.dumps(diffs9, sort_keys=True))
        check(sorted(set(nb9) - set(na9)) == [PKG + "GearSpeed"] and not (set(na9) - set(nb9)), "AG10: one class added (GearSpeed), none removed: %s" % sorted(set(na9) ^ set(nb9)))
        unexp9 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT026.get(c_, [])]) for c_, v_ in diffs9.items())
        unexp9 = dict((c_, v_) for c_, v_ in unexp9.items() if v_)
        missing9 = dict((c_, [m_ for m_ in v_ if m_ not in diffs9.get(c_, [])]) for c_, v_ in EXPECT026.items())
        missing9 = dict((c_, v_) for c_, v_ in missing9.items() if v_)
        check(not unexp9, "AG10: no difference outside the listed 0.2.6 parts: %s" % unexp9)
        check(not missing9, "AG10: every listed 0.2.6 part is really in the jar: %s" % missing9)
        za9, zb9 = zipfile.ZipFile(jar025), zipfile.ZipFile(jar)
        ea9 = [n_ for n_ in za9.namelist() if not n_.endswith(".class")]
        eb9 = [n_ for n_ in zb9.namelist() if not n_.endswith(".class")]
        ediff9 = sorted(n_ for n_ in set(ea9) | set(eb9) if n_ not in ea9 or n_ not in eb9 or za9.read(n_) != zb9.read(n_))
        check(ediff9 == sorted(["manifest.json"] + list(files6)), "AG10: non-class entries: manifest.json + exactly the %d speed assets: %s"
              % (len(files6), [n_ for n_ in ediff9 if n_ not in files6][:6]))
    else:
        check(False, "AG10: SkyyGear-0.2.5.jar (or the compare helper) not found - the class compare could not run")

    # ---- back to the AC model for the restore below
    fz(Inter, "ASSET_STORE").set(None, old_is6)
    fz(RootI, "ASSET_STORE").set(None, old_rs6)
    for k_, v_ in old_items6.items():
        if v_ is None:
            imap.remove(k_)
        else:
            imap.put(k_, v_)
    WK = WK_old6
    Chg.clear()
    Base.clear()
    Spd.reset()
    Spd.forget(U1)
    Spd.forget(U6)
    Spd.FORCE_OFF = True
    print("AG. 0.2.6 done")

'''

# AG10: the members 0.2.5 -> 0.2.6 may differ in (filled from the reviewed compare; anything else fails)
EXPECT026 = {
    # config kit: the two new rows + VERSION 0.2.5 -> 0.2.6 (CfgRows), the export header inlines the VERSION constant (CfgFn.opExport)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport([Ljava/lang/Object;)Ljava/lang/Object;'],
    'CfgRows': ['~<clinit>', '~f VERSION', '~m header()[Ljava/lang/Object;'],
    # /gear read: the weapon speed line
    'GearAdmin': ['~m read(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/inventory/ItemStack;)V'],
    # swing.tiers / swing.odds: fields, the loader, the check hook, the fresh file
    'GearCfg': ['~<clinit>', '+f SWING_ODDS', '+f SWING_ON', '+f SWING_W', '~m apply(Ljava/util/Properties;Z)V',
                '+m checkSwingOdds(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;', '~m defaultsText()Ljava/lang/String;',
                '+m swingOdds(Ljava/lang/String;)[D'],
    # the player's speed state is forgotten with the hand snapshot
    'GearCharged': ['~m forget(Ljava/util/UUID;)V'],
    # the safety net of the roll (first touch)
    'GearData': ['~m put(Lcom/hypixel/hytale/server/core/inventory/ItemStack;Lorg/bson/BsonDocument;Ljava/util/UUID;)Lcom/hypixel/hytale/server/core/inventory/ItemStack;'],
    # gear:fn:speed (mode 11)
    'GearFn': ['~m apply(Ljava/lang/Object;)Ljava/lang/Object;'],
    # the tier effect every tick
    'GearHandSys': ['~m tick(FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V'],
    # the hit weight + True Damage / flat elements x w
    'GearHit': ['~m weaponHit(Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage;Ljava/util/UUID;Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/inventory/ItemStack;ZLcom/skyy/gear/GearShot;Lcom/skyy/gear/GearShot;Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;)[Ljava/lang/Object;'],
    # the roll at a new identified document and at identify
    'GearRoll': ['~m identify(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/UUID;)Lorg/bson/BsonDocument;',
                 '~m newDoc(Ljava/lang/String;IZLjava/lang/String;I)Lorg/bson/BsonDocument;'],
    # the bridge sig (|spd<tier>) + the tooltip lines
    'GearView': ['~m bridgeSig(Ljava/lang/String;ILorg/bson/BsonDocument;)Ljava/lang/String;',
                 '~m statLines(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/ArrayList;Ljava/util/ArrayList;)V'],
    # gear:fn:speed registration + the ready line
    'SkyyGearPlugin': ['~m setup()V'],
    # fix round: a weighted tap's knockback + stats on hit (GearSpeed.perHit right after weaponHit)
    'GearHitSys': ['~m handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V'],
    # fix round: the Item reload listener drops the speed caches (GearSpeed.reset)
    'GearBoxL': ['~m accept(Ljava/lang/Object;)V'],
}
AG_SRC = AG_SRC.replace("@@EXPECT026@@", repr(EXPECT026))
RESTORE = "    # ---- restore the bare-JVM state this section changed (it is the last section; kept tidy anyway)\n"
sub(RESTORE, AG_SRC + "\n" + RESTORE)
_g = {"__name__": "__main__", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(src, H25 + " (run as the SkyyGear 0.2.6 harness)", "exec"), _g)
