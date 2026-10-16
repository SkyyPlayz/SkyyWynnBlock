"""Harness for SkyyArmory 0.1.29 (THE GREAT SHIELD + THE PUSHING LUNGE + the Warrior sword dash + the blink afterimages;
tools/armory_0_1_29_patch.py). Build first:
    python tools/armory_0_1_29_patch.py && python SkyyArmory/build_skyyarmory_0.1.29.py

    python SkyyArmory/test_skyyarmory_0.1.29.py [--jar <SkyyArmory-0.1.29.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  T   assets   FROM THE JAR: the 7 great shield items (vanilla shield art BY PATH, no art copied, the Battleaxe set, Primary / Secondary =
               our roots, the per-metal vars: bash 0.7 H / slam 1.0 H / the vanilla shield's Stamina per blocked hit, recipes = the shield
               recipe x2 at the shield bench, tier tag first in the description); the bash chain (bash, bash, slam; 90 degrees x 2.5 blocks;
               knockback 16 / 24; the slam's 0.3 s stagger = the vanilla Stun minus its screen effect); the hold (Charging: tap = chain,
               1.0 s = the Bulwark Charge marker = the blink marker shape); the guard (= the vanilla shield guard chain: melee + elements
               x0.3, Projectile x0, x0.7 move); no vanilla shield / sword dash file shipped; the default config carries the 18 new rows
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.28 -> 0.1.29: exactly the listed members differ (version texts normalised), RushState added; non-class: the manifest, the
               lang file, the 24 new files; the hooks (KunaiJob.run kind 4/5 -> Rush.dash, ArmoryTrav.added 15001 -> Rush.marker, blink ->
               shadowTrail, start() -> Rush.thrust, TravTick -> Rush.tickPlayer -> Rush.step / Rush.finish -> Rush.end); no teleport left
               in the rush (Shadow.port gone from Rush.dash)
  X   exec     EVERY NEW PATH without a world: the arc / shield front / crescent band geometry (incl. 3000 random enemies vs a Python copy of
               the rule), carry speed / step speed / stall / pinned, THE LUNGE SIMULATED tick by tick through Rush.step (open field: the
               full length, each enemy cut once, every carried enemy ends AHEAD of you; a wall: stops early, enemies still in front; a
               crowd pressed into a wall: pinned; a boss: cut, not carried, stops you; no line of sight: untouched; Bulwark Charge: the
               3-wide front, its end shove; the crescent gate at 10 Momentum; the timeout), Rush.end, gsH, bossRole, the sword dash force on
               a REAL engine ApplyForceInteraction (x125 / x100 / twice = no compounding / the packet cache dropped), shadowTrail (the seam),
               KunaiJob kind 4 / 5 without a world, tickPlayer / dash without a player, the marker codes, the config loader (defaults,
               clamps, the restart latch), the status text
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory: the 2nd start changes nothing, 0.1.29 does not rewrite the file
  AA  audit    the engine-access audit
The engine-backed parts (moving players / mobs by velocity, the hits through the damage pipeline, the item models + poses on the client, the
Thrust packet reaching the client, SkyyClasses' class lock on the great shields) need the game - the in-game steps. Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.29", "0.1.28"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "armory0129", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyArmory")
METALS = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
GS_IDS = ["Weapon_GreatShield_" + m for m in METALS]
GSI = "Server/Item/Interactions/Weapons/GreatShield/SkyyArmory/%s.json"
GSR = "Server/Item/RootInteractions/Weapons/GreatShield/SkyyArmory/%s.json"
NEW_FILES = sorted(["Server/Item/Items/Weapon/GreatShield/%s.json" % i for i in GS_IDS]
                   + [GSI % ("SkyyArmory_GreatShield_" + x) for x in ("Charging", "Chain", "Bash", "Bash_Selector", "Bash_Pad", "Bash_Damage", "Slam",
                                                                   "Slam_Selector", "Slam_Pad", "Slam_Damage", "Release", "Guard_Entry", "Guard_Wield")]
                   + [GSR % "SkyyArmory_GreatShield_Attack", GSR % "SkyyArmory_GreatShield_Guard",
                      "Server/Entity/Effects/SkyyArmory/SkyyArmory_GreatShield_Stagger.json", "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Bulwark_Charge.json"])
CFG_FIELDS = ["RUSH_SPEED", "RUSH_GAP", "RUSH_PUSH", "GS_ON", "GS_DIST", "GS_SPEED", "GS_HIT", "GS_WIDTH", "GS_STAG", "GS_SHOVE_HIT", "GS_SHOVE",
              "GS_SHOVE_R", "GS_SHOVE_W", "GS_KD", "GS_MANA", "GS_STAM", "THRUST_PCT", "BLINK_SHADOW"]
EXPECT = {}          # filled from the intended change list in run_compare (EXPECT_29)
ADDED = ["ArmoryMineFn", "RushState"]


def jread(z, n):
    return json.loads(z.read(n).decode("utf-8-sig"))


# ---------------------------------------------------------------------------------------------------- T: the assets (parent, no JVM)
def run_assets():
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    azn = set(AZ.namelist())

    def az(n):
        return jread(AZ, n)

    def vitem(i):
        p = [n for n in azn if n.startswith("Server/Item/Items/") and n.endswith("/" + i + ".json")]
        return az(p[0])
    with zipfile.ZipFile(JAR) as z:
        names = z.namelist()
        HK.check(all(n in names for n in NEW_FILES), "T0: the 24 new files are in the jar")
        HK.check(not [n for n in names if n.startswith(("Common/Items/Weapons/Shield/", "Common/Icons/ItemsGenerated/Weapon_Shield"))]
                 and not [n for n in names if os.path.basename(n).startswith("Weapon_Shield_") or "Thrust" in os.path.basename(n)],
                 "T0: no vanilla shield art / shield item / sword dash file in the jar (art by path, the dash changed at run time)")
        lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
        shb = az("Server/Item/Interactions/Weapons/Shield/Secondary/Guard/Guard_Bash/Weapon_Shield_Secondary_Guard_Bash_Damage.json")
        hs = {}
        for m, i in zip(METALS, GS_IDS):
            it = jread(z, "Server/Item/Items/Weapon/GreatShield/%s.json" % i)
            vs = vitem("Weapon_Shield_" + m)
            ls = vitem("Weapon_Longsword_" + m)
            lsh = ls["InteractionVars"]["Longsword_Swing_Left_Damage"]["Interactions"][0]["DamageCalculator"]["BaseDamage"]["Physical"]
            hs[m] = lsh
            HK.check(it["Model"] == vs["Model"] and it["Texture"] == vs["Texture"] and it["Icon"] == vs["Icon"]
                     and ("Common/" + it["Model"]) in azn and ("Common/" + it["Texture"]) in azn and ("Common/" + it["Icon"]) in azn,
                     "T1 %s: the vanilla %s shield art BY PATH (model / texture / icon exist in Assets.zip)" % (i, m))
            HK.check(it["PlayerAnimationsId"] == "Battleaxe" and it["Scale"] == 1.5 and "Utility" not in it
                     and it["Interactions"] == {"Primary": "SkyyArmory_GreatShield_Attack", "Secondary": "SkyyArmory_GreatShield_Guard"},
                     "T1 %s: two-handed (Battleaxe poses, no off-hand Utility), x1.5, our roots" % i)
            iv = it["InteractionVars"]
            bash = iv["GreatShield_Bash_Damage"]["Interactions"][0]
            slam = iv["GreatShield_Slam_Damage"]["Interactions"][0]
            wv = iv["GreatShield_Guard_Wield"]["Interactions"][0]
            vst = (vs.get("InteractionVars") or {}).get("Guard_Wield")
            want_st = vst["Interactions"][0]["StaminaCost"]["Value"] if vst else 28
            HK.check(bash == {"Parent": "SkyyArmory_GreatShield_Bash_Damage", "DamageCalculator": {"BaseDamage": {"Physical": round(0.7 * lsh, 1)}}}
                     and slam == {"Parent": "SkyyArmory_GreatShield_Slam_Damage", "DamageCalculator": {"BaseDamage": {"Physical": round(1.0 * lsh, 1)}}}
                     and wv == {"Parent": "SkyyArmory_GreatShield_Guard_Wield", "StaminaCost": {"Value": want_st, "CostType": "Damage"}},
                     "T1 %s: bash 0.7 H / slam 1.0 H (H = the %s longsword swing %s), Stamina per blocked hit %s (Onyxium = Mithril's)" % (i, m, lsh, want_st))
            HK.check(it["Quality"] == ls["Quality"] and it["ItemLevel"] == ls["ItemLevel"], "T1 %s: quality + level = the same-metal longsword's" % i)
            src = vs.get("Recipe") if m != "Onyxium" else vitem("Weapon_Shield_Mithril")["Recipe"]
            r = it["Recipe"]
            want_in = []
            for x in src["Input"]:
                y = dict(x)
                if m == "Onyxium" and y.get("ItemId") == "Ingredient_Bar_Mithril":
                    y["ItemId"] = "Ingredient_Bar_Onyxium"
                y["Quantity"] = int(x["Quantity"]) * 2
                want_in.append(y)
            HK.check(r["Input"] == want_in and r["BenchRequirement"] == src["BenchRequirement"] and float(r["TimeSeconds"]) == float(src["TimeSeconds"]) + 1.0,
                     "T1 %s: recipe = the %s shield recipe x2, +1 s, the shield bench" % (i, m if m != "Onyxium" else "Mithril (Onyxium bars)"))
            dl = [l for l in lang.split("\n") if l.startswith("items.%s.description = " % i)]
            tag = "T%d %s - " % (METALS.index(m) + 2, m)
            HK.check(len(dl) == 1 and dl[0].split(" = ", 1)[1].startswith(tag + "Spellblade.") and "Bulwark Charge" in dl[0],
                     "T1 %s: the tier tag first in the description (%r)" % (i, dl[0][:70] if dl else None))
            HK.check(("items.%s.name = %s Great Shield" % (i, m)) in lang, "T1 %s: the name" % i)
        HK.check([hs[m] for m in METALS] == sorted(hs.values()), "T1: H grows with the metal: %s" % hs)
        ch = jread(z, GSI % "SkyyArmory_GreatShield_Charging")
        HK.check(ch["Type"] == "Charging" and ch["Effects"] == {"ItemAnimationId": "Guard"} and ch["AllowIndefiniteHold"] is False
                 and ch["Next"] == {"0": "SkyyArmory_GreatShield_Chain", "1.0": "SkyyArmory_GreatShield_Release"}, "T2: the hold: tap = the chain, 1.0 s = the release")
        HK.check(jread(z, GSI % "SkyyArmory_GreatShield_Chain") == {"Type": "Chaining", "ChainingAllowance": 1.25, "Next": [
            "SkyyArmory_GreatShield_Bash", "SkyyArmory_GreatShield_Bash", "SkyyArmory_GreatShield_SlaM".replace("SlaM", "Slam")]}, "T2: the chain bash, bash, slam")
        for nm, anim, t in (("Bash", "GuardBash", (0.25, 0.1, 0.3)), ("Slam", "SwingDown", (0.35, 0.1, 0.4))):
            w = jread(z, GSI % ("SkyyArmory_GreatShield_" + nm))
            sel = jread(z, GSI % ("SkyyArmory_GreatShield_%s_Selector" % nm))
            pad = jread(z, GSI % ("SkyyArmory_GreatShield_%s_Pad" % nm))
            dm = jread(z, GSI % ("SkyyArmory_GreatShield_%s_Damage" % nm))
            he = sel["HitEntity"]["Interactions"]
            HK.check(w["RunTime"] == t[0] and w["Effects"]["ItemAnimationId"] == anim and w["Next"] == "SkyyArmory_GreatShield_%s_Selector" % nm
                     and sel["RunTime"] == t[1] and pad == {"Type": "Simple", "RunTime": t[2]} and sel["Next"] == "SkyyArmory_GreatShield_%s_Pad" % nm,
                     "T2 %s: wind %s s (%s) -> hit window %s s -> recover %s s" % (nm, t[0], anim, t[1], t[2]))
            so = sel["Selector"]
            HK.check(so["Id"] == "Horizontal" and so["Length"] == 90 and so["YawStartOffset"] == -45 and so["EndDistance"] == 2.5 and so["TestLineOfSight"] is True,
                     "T2 %s: 90 degrees in front, 2.5 blocks, line of sight" % nm)
            HK.check(he[0] == {"Type": "Replace", "Var": "GreatShield_%s_Damage" % nm, "DefaultValue": {"Interactions": ["SkyyArmory_GreatShield_%s_Damage" % nm]}}
                     and (he[1:] == [{"Type": "ApplyEffect", "Entity": "Target", "EffectId": "SkyyArmory_GreatShield_Stagger"}] if nm == "Slam" else len(he) == 1),
                     "T2 %s: the item's damage var%s" % (nm, " + the stagger" if nm == "Slam" else ""))
            want = json.loads(json.dumps(shb))
            want["DamageEffects"]["Knockback"]["Force"] = 16 if nm == "Bash" else 24
            want.pop("DamageCalculator")
            HK.check(dict((k, v) for k, v in dm.items() if k != "DamageCalculator") == want and dm["Parent"] == "DamageEntityParent",
                     "T2 %s: the vanilla shield shove damage file, knockback %d" % (nm, 16 if nm == "Bash" else 24))
        stg = jread(z, "Server/Entity/Effects/SkyyArmory/SkyyArmory_GreatShield_Stagger.json")
        vst = az("Server/Entity/Effects/Status/Stun.json")
        vst["Duration"] = 0.3
        vst["ApplicationEffects"].pop("ScreenEffect", None)
        HK.check(stg == vst, "T3: the stagger = the vanilla Stun, 0.3 s, no screen effect")
        rel = jread(z, GSI % "SkyyArmory_GreatShield_Release")
        HK.check(rel["Next"]["Type"] == "LaunchProjectile" and rel["Next"]["ProjectileId"] == "SkyyArmory_Bulwark_Charge", "T3: the release launches the marker")
        HK.check(jread(z, "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Bulwark_Charge.json") == jread(z, "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Crescent_Rush.json"),
                 "T3: the marker = the Crescent Rush / blink marker shape")
        HK.check(jread(z, GSR % "SkyyArmory_GreatShield_Attack") == {"RequireNewClick": True, "ClickQueuingTimeout": 0.3, "Interactions": ["SkyyArmory_GreatShield_Charging"],
                 "Tags": {"Attack": ["Melee"]}}, "T3: the attack root")
        gr = jread(z, GSR % "SkyyArmory_GreatShield_Guard")
        vgr = az("Server/Item/RootInteractions/Weapons/Shield/Root_Weapon_Shield_Secondary_Guard.json")
        HK.check(gr["Rules"] == vgr["Rules"] and gr["RequireNewClick"] is True and gr["Interactions"] == ["SkyyArmory_GreatShield_Guard_Entry"], "T4: the guard root = the shield root shape")
        ge = jread(z, GSI % "SkyyArmory_GreatShield_Guard_Entry")
        vge = az("Server/Item/Interactions/Weapons/Shield/Secondary/Guard/Weapon_Shield_Secondary_Guard.json")
        HK.check(json.dumps(ge) == json.dumps(vge).replace('"Var": "Guard_Wield"', '"Var": "GreatShield_Guard_Wield"').replace(
            '"Weapon_Shield_Secondary_Guard_Wield"', '"SkyyArmory_GreatShield_Guard_Wield"'), "T4: the entry = the vanilla shield guard entry (0.5 Stamina) with our wield")
        gw = jread(z, GSI % "SkyyArmory_GreatShield_Guard_Wield")
        vgw = az("Server/Item/Interactions/Weapons/Shield/Secondary/Guard/Weapon_Shield_Secondary_Guard_Wield.json")
        dmods = gw["AngledWielding"]["DamageModifiers"]
        HK.check(dmods["Projectile"] == 0 and all(dmods[k] == 0.3 for k in dmods if k != "Projectile") and set(("Physical", "Slashing", "Bludgeoning")) <= set(dmods)
                 and gw["AngledWielding"]["KnockbackModifiers"] == vgw["AngledWielding"]["KnockbackModifiers"] and gw["AngledWielding"]["AngleDistance"] == 90
                 and gw["HorizontalSpeedMultiplier"] == 0.7, "T4: the wield: projectiles x0 (100 %% blocked), melee + elements x0.3 (70 %%), move x0.7: %s" % dmods)
        HK.check(dict((k, v) for k, v in gw.items() if k not in ("AngledWielding", "HorizontalSpeedMultiplier")) == dict((k, v) for k, v in vgw.items() if k != "AngledWielding")
                 and gw["AngledWielding"]["Angle"] == vgw["AngledWielding"]["Angle"], "T4: every other field = the vanilla shield wield")
        dc = None
        for n in names:
            if n.endswith("ArmoryCfg.class"):
                dc = z.read(n)
        HK.check(dc is not None and all(k.encode() in dc for k in ("gshield.charge.distance", "blade.rush.speed", "sword.thrust.percent", "blink.shadowTrail")),
                 "T5: the config loader reads the new keys")
        ov = jread(z, "Server/Item/Interactions/Weapons/Longsword/Attacks/Stab_Charged/Longsword_Stab_Charged.json")
        HK.check(ov["Effects"]["ItemAnimationId"] == "SwingLeftCharged", "T6 (fix 7): the Crescent Rush release plays the charged SWING (SwingLeftCharged)")
        HK.check(b"blade.rush.pathHit" in dc, "T6 (fix 8): the loader still reads blade.rush.pathHit (the key is never removed)")
    AZ.close()


# ---------------------------------------------------------------------------------------------------- C: class compare
EXPECT_29 = {
    "ArmoryDefs": ["+f GS_CODE", "+f GS_H", "+f GS_IDS", "+f GS_MARK", "~<clinit>", "~m pids"],
    "ArmoryCfg": ["+f THRUST_NEXT", "+f THRUST_SET"] + ["+f " + f for f in CFG_FIELDS] + ["~m bladeText", "~<clinit>", "~m apply", "~m load",
                  "~m reloadAll", "~m useDefaults"],
    "ArmoryHooks": ["~<clinit>"], "ArmoryTrav": ["+f FX_SHADOW", "+f SHADOWS", "+m shadowTrail", "~<clinit>", "~m added", "~m blink"],
    "KunaiJob": ["~m run"], "CfgRows": ["~<clinit>"], "CfgFile": ["~<clinit>"],
    "Rush": ["+f CARRIED", "+f CATCH_S", "+f CHARGES", "+f CONTACT_LEN", "+f FX_BASH", "+f PINS", "+f PIN_TICKS", "+f SND_BASH", "+f SND_SHOVE",
             "+f STALL_FRAC", "+f STALL_TICKS", "+f THRUST_ID", "+f THRUST_OBJ", "+f THRUST_ORIG", "+f THRUST_WHY", "+f UNSTOP", "+f WALLS",
             "+f COAST_TICKS", "+f GRACE_TICKS", "+f GS_MOM_MAX", "+f MAX_MOBS", "+f MOMS", "+f RUSH_MOM",          # fix round
             "+m arcFx", "+m grantMom", "+m momGain", "+m thrustRestore",          # fix round
             "+m boss", "+m bossRole", "+m carryV", "+m cvy", "+m end", "+m finish", "+m gsH", "+m inArc", "+m inBand", "+m inFront", "+m near",
             "+m pinned", "+m radius", "+m stall", "+m step", "+m stepV", "+m thrust", "+m thrustOn", "-m kindOf", "-m strike", "~<clinit>",
             "~m dash", "~m marker", "~m statusText", "~m tickPlayer"],
    "SkyyArmoryPlugin": ["~m publish", "~m shutdown", "~m start", "~m unpublish"]}          # fix round: + the armory:fn:mine bridge key


def run_compare(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(OLD_JAR), pool_of(jar)

    def code(b_):
        mi_ = b_.getMethodInfo()
        ca_ = mi_.getCodeAttribute()
        if ca_ is None:
            return ""
        it_ = ca_.iterator()
        cpl_ = mi_.getConstPool()
        lines_ = []
        while it_.hasNext():
            pos_ = it_.next()
            ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
            ln_ = re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_)
            lines_.append(ln_.replace(VERSION, "VER").replace(OLD, "VER"))
        return str(b_.getModifiers()) + "\n" + "\n".join(lines_)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = HK.jar_classes(OLD_JAR), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(PKG + a for a in ADDED), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), [], "C: classes removed")
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = sorted(set(("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd))
    print("C. class compare %s -> %s: %d classes differ" % (OLD, VERSION, len(diffs)))
    for k in sorted(diffs):
        print("   %-22s %s" % (k, ", ".join(diffs[k])))
    K.eq(sorted(diffs), sorted(EXPECT_29), "C: the classes that differ")
    for k in sorted(EXPECT_29):
        K.eq(sorted(diffs.get(k, [])), sorted(EXPECT_29[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    K.eq(sorted(eb - ea), NEW_FILES, "C: non-class entries added = the 24 great shield files")
    K.eq(sorted(ea - eb), [], "C: non-class entries removed")
    K.eq(sorted(n for n in ea & eb if za.read(n) != zb.read(n)), ["Server/Item/Interactions/Weapons/Longsword/Attacks/Stab_Charged/Longsword_Stab_Charged.json",
         "Server/Languages/en-US/server.lang", "manifest.json"], "C: non-class entries changed = the manifest, the lang file, the rush release animation (fix 7)")
    oa, ob = json.loads(za.read("Server/Item/Interactions/Weapons/Longsword/Attacks/Stab_Charged/Longsword_Stab_Charged.json").decode("utf-8-sig")), \
        json.loads(zb.read("Server/Item/Interactions/Weapons/Longsword/Attacks/Stab_Charged/Longsword_Stab_Charged.json").decode("utf-8-sig"))
    oa["Effects"]["ItemAnimationId"] = "SwingLeftCharged"
    K.check(oa == ob, "C (fix 7): the rush override changed ONLY its release animation")
    la, lb = za.read("Server/Languages/en-US/server.lang").decode("utf-8-sig"), zb.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
    K.check(lb.startswith(la) and all(l.startswith("items.Weapon_GreatShield_") for l in lb[len(la):].split("\n") if l.strip())
            and len([l for l in lb[len(la):].split("\n") if l.strip()]) == 14, "C: the lang file only GAINS the 14 great shield lines")

    def calls(cls, mname, target):
        c_ = pb.get(PKG + cls)
        for m_ in c_.getDeclaredMethods():
            if str(m_.getName()) != mname:
                continue
            ca = m_.getMethodInfo().getCodeAttribute()
            it_ = ca.iterator()
            cpl_ = m_.getMethodInfo().getConstPool()
            while it_.hasNext():
                pos_ = it_.next()
                if target in str(IP.instructionString(it_, pos_, cpl_)):
                    return True
        return False
    K.check(calls("KunaiJob", "run", "Rush.dash"), "C: KunaiJob.run kind 4 / 5 -> Rush.dash")
    K.check(calls("ArmoryTrav", "added", "Rush.marker") and calls("ArmoryTrav", "added", "15001") and calls("ArmoryTrav", "added", "15000"), "C: ArmoryTrav.added dispatches 15000 + 15001 to Rush.marker")
    K.check(calls("ArmoryTrav", "blink", "ArmoryTrav.shadowTrail") and calls("ArmoryTrav", "blink", "BLINK_SHADOW"), "C: the staff blink draws the afterimages (row-gated)")
    K.check(calls("SkyyArmoryPlugin", "start", "Rush.thrust") and calls("SkyyArmoryPlugin", "shutdown", "THRUST_SET"), "C: start() changes the sword dash; shutdown resets its latch")
    K.check(calls("TravTick", "tick", "Rush.tickPlayer") and calls("Rush", "tickPlayer", "Rush.step") and calls("Rush", "tickPlayer", "Rush.finish")
            and calls("Rush", "finish", "Rush.end"), "C: TravTick -> Rush.tickPlayer -> Rush.step every tick, Rush.finish -> Rush.end at the end")
    K.check(calls("Rush", "tickPlayer", "Leap.vel") and calls("Rush", "finish", "Leap.vel"), "C: the lunge moves you and the carried enemies by velocity (Leap.vel)")
    K.check(not calls("Rush", "dash", "Shadow.port") and not calls("Rush", "tickPlayer", "Shadow.port") and not calls("Rush", "finish", "Shadow.port"),
            "C: NO TELEPORT left in Crescent Rush / Bulwark Charge")
    K.check(calls("Rush", "dash", "TravMath.scanL") and calls("Rush", "dash", "Leap.take") and calls("Rush", "dash", "ArmoryTrav.allowed")
            and calls("Rush", "dash", "Kunai.arena"), "C: the start scans walls (scanL), pays (Leap.take), keeps the class lock + the locked arena")
    K.check(calls("Rush", "near", "Shadow.attitude") and calls("Rush", "near", "Rush.foe") and calls("Rush", "near", "Shadow.protect")
            and calls("Rush", "near", "TravMath.clear"), "C: the candidates: friendly / protected mobs never, line of sight judged")
    K.check(calls("Rush", "finish", "Rush.grantMom") and calls("Rush", "grantMom", "class:fn:momAdd") and calls("SkyyArmoryPlugin", "shutdown", "Rush.thrustRestore"),
            "C (fix 2 / 3): the lunge grants Momentum once at the end; shutdown restores the vanilla dash force")
    K.check(calls("Rush", "tickPlayer", "Rush.hit") and calls("Rush", "finish", "Rush.hit") and calls("Rush", "hit", "DamageSystems.executeDamage"),
            "C: the cuts / the crescent / the shove go through the damage pipeline")

    def first(cls, mname, target):
        c_ = pb.get(PKG + cls)
        for m_ in c_.getDeclaredMethods():
            if str(m_.getName()) != mname:
                continue
            ca = m_.getMethodInfo().getCodeAttribute()
            it_ = ca.iterator()
            cpl_ = m_.getMethodInfo().getConstPool()
            while it_.hasNext():
                pos_ = it_.next()
                if target in str(IP.instructionString(it_, pos_, cpl_)):
                    return int(pos_)
        return -1
    fa, ft = first("Rush", "dash", "Kunai.arena"), first("Rush", "dash", "Leap.take")
    K.check(0 <= fa < ft, "C: the locked-arena check runs BEFORE the cost (Kunai.arena at %d, Leap.take at %d)" % (fa, ft))
    K.save()


# ---------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    R = JClass(PKG + "Rush")
    RS = JClass(PKG + "RushState")
    Cfg = JClass(PKG + "ArmoryCfg")
    Defs = JClass(PKG + "ArmoryDefs")
    Trav = JClass(PKG + "ArmoryTrav")
    UUID = JClass("java.util.UUID")
    U = UUID.randomUUID()
    DA = JArray(JClass("double"))
    DAA = JArray(JArray(JClass("double")))
    OA = JArray(JClass("java.lang.Object"))
    Cfg.useDefaults()
    K.eq([float(Cfg.RUSH_SPEED), float(Cfg.RUSH_GAP), float(Cfg.RUSH_PUSH), bool(Cfg.GS_ON), float(Cfg.GS_DIST), float(Cfg.GS_SPEED), float(Cfg.GS_HIT),
          float(Cfg.GS_WIDTH), float(Cfg.GS_STAG), float(Cfg.GS_SHOVE_HIT), float(Cfg.GS_SHOVE), float(Cfg.GS_SHOVE_R), float(Cfg.GS_SHOVE_W),
          float(Cfg.GS_KD), float(Cfg.GS_MANA), float(Cfg.GS_STAM), int(Cfg.THRUST_PCT), bool(Cfg.BLINK_SHADOW),
          float(Cfg.RUSH_DIST), float(Cfg.RUSH_SWEEP), float(Cfg.RUSH_REACH), int(Cfg.RUSH_ARC), float(Cfg.RUSH_MANA), float(Cfg.RUSH_STAM)],
         [15.0, 1.5, 6.0, True, 8.0, 13.0, 0.6, 3.0, 0.5, 1.0, 12.0, 3.0, 3.0, 1.0, 4.0, 5.0, 125, True, 6.0, 1.5, 4.0, 180, 8.0, 4.0],
         "X0: the defaults (spec: Bulwark 8 blocks, 0.6 H + 0.5 s stagger, shove 1.0 H, 4 Mana + 5 Stamina; the rush keeps 6 / 1.5 H / 4 / 180 / 8 + 4; "
         "sword dash 125 percent; the blink afterimages on)")
    bt = str(Cfg.BLADE_TEXT)
    K.check("LUNGE" in bt and "Bulwark Charge on" in bt and "x125 percent" in bt and "blink afterimages on" in bt, "X0: the blade text: %s" % bt[-260:])
    # X1 the geometry (you at 0 / 64 / 0 looking +x)

    def arc(x, z, y=64.0, reach=4.0, a=180, half=0.3, hh=0.9):
        return bool(R.inArc(0.0, 64.0, 0.0, 1.0, 0.0, x, y + hh, z, hh, half, reach, a))
    K.eq([arc(3, 0), arc(0.2, 4.2), arc(0.2, -4.2), arc(-1, 0), arc(-0.6, 0), arc(4.4, 0), arc(4.2, 0), arc(3, 0, 67.0), arc(2.5, 2.8, a=90), arc(3, 0.5, a=90), arc(-3, 0, a=360)],
         [True, True, True, False, True, False, True, False, False, True, True],
         "X1: inArc: ahead / both sides at 180, not behind (but touching you = in), reach 4 + half, not far above, 90 degrees narrower, 360 all around")

    def front(x, z, ln=1.5, w=3.0, half=0.3):
        return bool(R.inFront(0.0, 64.0, 0.0, 1.0, 0.0, x, 64.9, z, 0.9, half, ln, w))
    K.eq([front(1.0, 0.0), front(1.7, 1.7), front(1.7, 1.9), front(2.0, 0.0), front(-0.5, 0.0), front(-0.2, 0.0)], [True, True, False, False, False, True],
         "X1: inFront: the 3-wide shield front 1.5 ahead (+ half the body), nothing behind")

    def band(x, z):
        return bool(R.inBand(0.0, 64.0, 0.0, 1.0, 0.0, x, 64.9, z, 0.9, 0.3, 8.0, 2.0))
    K.eq([band(5.0, 0.0), band(8.2, 0.0), band(8.5, 0.0), band(5.0, 1.2), band(5.0, 1.4), band(-1.0, 0.0)], [True, True, False, True, False, False],
         "X1: inBand: the crescent 8 ahead, 2 wide (+ half the body)")
    import random
    rnd = random.Random(129)
    bad = []
    for _ in range(3000):
        hx_a = rnd.uniform(0, 2 * math.pi)
        hx, hz = math.cos(hx_a), math.sin(hx_a)
        x, z, a = rnd.uniform(-6, 6), rnd.uniform(-6, 6), rnd.choice([90, 180, 270, 360])
        got = bool(R.inArc(0.0, 64.0, 0.0, hx, hz, x, 64.9, z, 0.9, 0.3, 4.0, a))
        dh = math.hypot(x, z)
        want = dh <= 4.3 and (dh <= 0.8 or a >= 360 or (x * hx + z * hz) / dh >= math.cos(math.radians(a / 2.0)) - 1e-9)
        if got != want:
            bad.append((round(x, 2), round(z, 2), a))
    K.check(not bad, "X1: 3000 random enemies (any look direction) = the Python rule: %d off %s" % (len(bad), bad[:3]))
    # X2 the small rules
    K.eq([round(float(R.carryV(0.0, 1.8, 1.8, 15.0)), 6), round(float(R.carryV(0.0, 0.8, 1.8, 15.0)), 6), round(float(R.carryV(0.0, 3.0, 1.8, 15.0)), 6),
          round(float(R.carryV(0.0, -5.0, 1.8, 15.0)), 6), round(float(R.carryV(0.0, 0.0, 1.8, 2.0)), 6)],
         [15.0, 25.0, 15.0, 30.0, 20.0], "X2: carryV: at the gap = your speed, 1 block short = +10, ahead = your speed (never slower), capped at max(2v, 20) (fix 5)")
    K.eq([round(float(R.stepV(0.0, 6.0, 15.0, 1 / 30.0)), 6), round(float(R.stepV(5.8, 6.0, 15.0, 1 / 30.0)), 6), float(R.stepV(6.0, 6.0, 15.0, 1 / 30.0))],
         [15.0, 6.0, 0.0], "X2: stepV: full speed, never past the end (0.2 left in a 1/30 s tick = 6 blocks a second), done = 0")
    K.eq([int(R.stall(0, 0.5, 0.5)), int(R.stall(0, 0.1, 0.5)), int(R.stall(1, 0.1, 0.5)), int(R.stall(3, 0.0, 0.0))], [0, 1, 2, 0],
         "X2: stall counts ticks moving under 30 percent of the asked step (nothing asked = 0)")
    K.eq([bool(R.pinned(0.0, 0.6, 0.0, 0.3, 4, True)), bool(R.pinned(0.0, 0.6, 0.0, 0.3, 3, True)), bool(R.pinned(0.0, 1.2, 0.0, 0.3, 9, True)),
          bool(R.pinned(0.0, 0.6, 1.2, 0.3, 9, True)), bool(R.pinned(0.0, 0.6, 0.0, 0.3, 0, False)), bool(R.pinned(0.0, -0.5, 0.0, 0.3, 0, False))],
         [True, False, False, False, True, False], "X2: pinned: touching + in your path after 4 carried ticks; a boss at once; beside / behind / with room = no")
    K.eq([int(R.momGain(4, 0)), int(R.momGain(4, 7)), int(R.momGain(5, 2)), int(R.momGain(5, 9))], [0, 2, 2, 3],
         "X2 (fix 2): the lunge's Momentum once: Crescent Rush +2 if it cut anything, Bulwark +1 per enemy cut (max 3)")

    # X3 THE LUNGE, simulated WITH LAG (fix 1): the client applies each speed the server sets `lag` ticks late (a round trip), the server sees
    # the client where it is; the mobs are server-side (no lag); a wall clamps everyone at wallx. The final client position = every speed sent.
    def state(kind=4, far=6.0, v=15.0, mom=0, until=10 ** 12):
        s = RS()
        s.kind, s.sx, s.sy, s.sz, s.hx, s.hz, s.far, s.v, s.h, s.mom, s.gap, s.until = kind, 0.0, 64.0, 0.0, 1.0, 0.0, far, v, 10.0, float(mom), 1.5, until
        return s

    def sim(s, mobs, wallx=None, dt=1 / 30.0, ticks=200, lag=0):
        """mobs: name -> [x, z, movable, los]; returns (reason, final client x, mobs, acts per name, ticks, keys)"""
        cx = 0.0
        cmds = []
        names = sorted(mobs)
        keys = OA([JString(n) for n in names])
        acts = dict((n, []) for n in names)
        reason = -1
        t = 0
        for t in range(ticks):
            arr = DAA([DA([mobs[n][0], 64.0, mobs[n][1], 0.9, 0.3, float(mobs[n][2]), float(mobs[n][3])]) for n in names])
            o = list(R.step(s, cx, 64.0, 0.0, dt, 1000, keys, arr))
            for i, n in enumerate(names):
                a = int(o[3 + 3 * i])
                acts[n].append(a)
                if a in (1, 2):
                    nx = mobs[n][0] + o[4 + 3 * i] * dt
                    mobs[n][0] = min(nx, wallx - 0.3) if wallx is not None else nx
            cmds.append(o[1] if int(o[0]) == 0 else 0.0)
            if int(o[0]) != 0:
                reason = int(o[0])
                break
            v_ = cmds[t - lag] if t - lag >= 0 else 0.0
            nx = cx + v_ * dt
            cx = min(nx, wallx - 0.3) if wallx is not None else nx
        for v_ in cmds[max(0, t - lag):t]:          # the speeds still in flight reach the client after the end
            nx = cx + v_ * dt
            cx = min(nx, wallx - 0.3) if wallx is not None else nx
        return reason, cx, mobs, acts, t, keys
    m0 = {"a_ahead": [2.0, 0.0, 1, 1], "b_side": [3.0, 1.5, 1, 1], "c_left": [5.0, -2.0, 1, 1], "d_far": [8.0, 0.0, 1, 1], "e_behind": [-2.0, 0.0, 1, 1],
          "f_wide": [3.0, 6.0, 1, 1], "g_nolos": [4.0, 0.5, 1, 0]}
    for lag in (0, 4, 9):
        s1 = state()
        rs, px, mo, ac, tk, _k = sim(s1, json.loads(json.dumps(m0)), lag=lag)
        K.check(rs == 1 and abs(px - 6.0) < 0.06 and abs(float(s1.sent) - 6.0) < 1e-6,
                "X3a lag %d ticks: the full length, no early stop, no overshoot (reason %d, client at %.3f of 6, sent %.3f)" % (lag, rs, px, float(s1.sent)))
        cut = sorted(n for n in ac if 1 in ac[n] or 3 in ac[n])
        K.eq(cut, ["a_ahead", "b_side", "c_left", "d_far"], "X3a lag %d: the arc cut every enemy ahead + beside along the WHOLE lunge, not the one behind, "
             "not the one 6 to the side, not the one behind a wall" % lag)
        K.check(all(ac[n].count(1) + ac[n].count(3) == 1 for n in cut), "X3a lag %d: each enemy cut exactly ONCE" % lag)
        ahead = dict((n, round(mo[n][0] - px, 3)) for n in cut)
        K.check(all(v_ >= 0.3 for v_ in ahead.values()), "X3a lag %d: every carried enemy ends AHEAD of the real you, never behind: %s" % (lag, ahead))
        K.check(mo["e_behind"][0] == -2.0 and mo["f_wide"][0] == 3.0 and mo["g_nolos"][0] == 4.0, "X3a lag %d: the others stay where they were" % lag)
        K.eq(int(s1.hits), 4, "X3a lag %d: RushState counts 4 cuts" % lag)
        if lag == 0:
            arr_end = DAA([DA([mo[n][0], 64.0, mo[n][1], 0.9, 0.3, float(mo[n][2]), float(mo[n][3])]) for n in sorted(mo)])
            e1 = list(R.end(s1, px, 64.0, 0.0, _k, arr_end))
            en = dict((n, (int(e1[3 * i]), round(e1[3 * i + 1], 3))) for i, n in enumerate(sorted(mo)))
            K.check(all(en[n] == (2, 6.0) for n in cut) and all(en[n][0] == 0 for n in mo if n not in cut),
                    "X4a: the end at 0 Momentum: the carried enemies are pushed on (6 blocks a second), nothing hit (no crescent): %s" % en)
        # X3b a wall at x = 5: the crowd is pressed into it -> pinned, you stop early, they stay in front
        s2 = state()
        rs, px, mo, ac, tk, _k = sim(s2, {"a": [2.0, 0.0, 1, 1], "b": [3.0, 0.4, 1, 1]}, wallx=5.0, lag=lag)
        K.check(rs == 3 and px < 4.8 and all(mo[n][0] > px + 0.3 for n in mo), "X3b lag %d wall + crowd: stopped early by the pinned crowd (reason %d) at %.2f, "
                "enemies at %s - in front" % (lag, rs, px, [round(mo[n][0], 2) for n in mo]))
        # X3c a bare wall at x = 4: you stop at it; a long lunge (12 blocks) notices the stall (reason 2), a short one coasts out (reason 1)
        s3 = state()
        rs, px, mo, ac, tk, _k = sim(s3, {}, wallx=4.0, lag=lag)
        s3b = state(far=12.0)
        rs2, px2, mo2, ac2, tk2, _k2 = sim(s3b, {}, wallx=4.0, lag=lag)
        K.check(rs in (1, 2) and abs(px - 3.7) < 1e-6 and tk < 40 and rs2 == 2 and abs(px2 - 3.7) < 1e-6 and tk2 < 40,
                "X3c lag %d bare wall: stops at the wall (6 blocks: reason %d after %d ticks; 12 blocks: reason %d after %d ticks)" % (lag, rs, tk, rs2, tk2))
        # X3d a boss in your way: cut once, never carried, you stop in front of it
        s4 = state()
        rs, px, mo, ac, tk, _k = sim(s4, {"boss": [3.0, 0.0, 0, 1]}, lag=lag)
        K.check(rs == 3 and ac["boss"].count(3) == 1 and 1 not in ac["boss"] and 2 not in ac["boss"] and mo["boss"][0] == 3.0 and px < 3.0 - 0.3,
                "X3d lag %d boss: cut once (act 3), not carried, stops you in front of it (reason %d, you %.2f)" % (lag, rs, px))
        # X3e Bulwark Charge: the 3-wide front, 8 blocks at 13, the shove at the end
        s5 = state(kind=5, far=8.0, v=13.0, mom=14)
        rs, px, mo, ac, tk, _k = sim(s5, {"in": [2.0, 1.0, 1, 1], "out": [2.0, 2.5, 1, 1], "far": [7.0, -0.5, 1, 1]}, lag=lag)
        K.check(rs == 1 and abs(px - 8.0) < 0.06 and 1 in ac["in"] and 1 in ac["far"] and not [a for a in ac["out"] if a], "X3e lag %d Bulwark: 8 blocks, the "
                "3-wide front catches 'in' + 'far', not 'out' (2.5 aside): %s" % (lag, dict((n, sorted(set(ac[n]))) for n in ac)))
        K.check(mo["in"][0] > px + 0.3 and mo["far"][0] > px + 0.3, "X3e lag %d: the carried ones end ahead of the real you" % lag)
        if lag == 0:
            arr_end = DAA([DA([mo[n][0], 64.0, mo[n][1], 0.9, 0.3, float(mo[n][2]), float(mo[n][3])]) for n in sorted(mo)])
            e5 = list(R.end(s5, px, 64.0, 0.0, _k, arr_end))
            en = dict((n, (int(e5[3 * i]), round(e5[3 * i + 1], 3))) for i, n in enumerate(sorted(mo)))
            K.check(en["in"] == (1, 12.0) and en["far"] == (1, 12.0) and en["out"][0] == 0, "X4b Bulwark end: the shove hits + pushes (12) what is in front, "
                    "not the one aside: %s" % en)
    # X3f the crescent gate (10 Momentum): an enemy 7 beyond the end (out of the arc all along) is hit at the end only with the gate
    for mom, want in ((12, 1), (5, 0)):
        s6 = state(mom=mom)
        rs, px, mo, ac, tk, _k = sim(s6, {"x": [13.0, 0.0, 1, 1]})
        arr_end = DAA([DA([mo["x"][0], 64.0, 0.0, 0.9, 0.3, 1.0, 1.0])])
        e6 = list(R.end(s6, px, 64.0, 0.0, _k, arr_end))
        K.check(not [a for a in ac["x"] if a] and int(e6[0]) == want, "X4c crescent at %d Momentum: %s (the band 8 ahead of the end)" % (mom, "hit" if want else "none"))
    # X3g a too-long lunge ends (reason 4); no room = the arc where you stand; a null state ends
    s7 = state(until=500)
    o7 = list(R.step(s7, 0.0, 64.0, 0.0, 1 / 30.0, 1000, OA([]), DAA([])))
    K.eq(int(o7[0]), 4, "X3g: past its time = reason 4 (a stuck lunge always ends)")
    s8 = state(far=0.0)
    o8 = list(R.step(s8, 0.0, 64.0, 0.0, 1 / 30.0, 1000, OA([JString("m")]), DAA([DA([2.0, 64.0, 0.0, 0.9, 0.3, 1.0, 1.0])])))
    K.check(int(o8[0]) == 1 and int(o8[3]) == 1, "X3h: no room ahead (0 blocks) = the arc where you stand, then the end")
    K.eq(int(list(R.step(None, 0.0, 64.0, 0.0, 0.03, 0, None, None))[0]), 4, "X3: a null state = ends")
    # X3i (fix 4) the look radius: during = reach + gap + 2, the crescent / shove reach only at the end
    K.eq([float(R.radius(state(), False)), float(R.radius(state(), True)), float(R.radius(state(kind=5), False)), float(R.radius(state(kind=5), True))],
         [7.5, 11.5, 6.5, 8.0], "X3i (fix 4): radius 7.5 / 11.5 (rush), 6.5 / 8 (charge)")
    # X3j (fix 2) the Momentum grant through class:fn:momAdd; armory:fn:mine
    from jpype import JImplements, JOverride
    got = []

    @JImplements("java.util.function.Function")
    class Fn:
        @JOverride
        def apply(self, o):
            got.append((str(o[0]), int(o[1])))
            return JObject(5, JClass("java.lang.Integer"))
    br = Defs.bridge()
    br.put("class:fn:momAdd", Fn())
    K.check(int(R.grantMom(U, 2)) == 2 and got == [(str(U), 2)] and int(R.grantMom(U, 0)) == 0 and len(got) == 1,
            "X3j (fix 2): grantMom calls class:fn:momAdd once with {UUID, 2}; 0 = no call: %s" % got)
    br.remove("class:fn:momAdd")
    K.eq(int(R.grantMom(U, 2)), 0, "X3j: no SkyyClasses = nothing granted (no throw)")
    MF = JClass(PKG + "ArmoryMineFn")()
    dk = JString("a-damage")
    Trav.MINE.put(dk, JObject(True, JClass("java.lang.Boolean")))
    K.check(bool(MF.apply(dk)) and not bool(MF.apply(JString("other"))) and not bool(MF.apply(None)), "X3j (fix 2): armory:fn:mine answers our own damage only")
    Trav.MINE.remove(dk)
    # X5 the shield table, the boss words, the sword dash on a REAL engine ApplyForceInteraction
    K.eq([float(R.gsH("Weapon_GreatShield_Copper")), float(R.gsH("Weapon_GreatShield_Onyxium")), float(R.gsH("Weapon_Shield_Iron")), float(R.gsH(None))],
         [float(Defs.GS_H[0]), float(Defs.GS_H[6]), -1.0, -1.0], "X5: gsH = the table (H Copper %s .. Onyxium %s); a vanilla shield / nothing = -1" % (Defs.GS_H[0], Defs.GS_H[6]))
    K.eq([str(x) for x in Defs.GS_IDS], GS_IDS, "X5: ArmoryDefs.GS_IDS")
    K.eq([bool(R.bossRole("Golem_Firesteel", "golem,yeti")), bool(R.bossRole("Skeleton_Fighter", "golem,yeti")), bool(R.bossRole(None, "x"))],
         [True, False, False], "X5: bossRole = the stunlock's whole-part words")
    AFI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.ApplyForceInteraction")
    AFF = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.ApplyForceInteraction$Force")
    ctor = AFI.class_.getDeclaredConstructor()
    ctor.setAccessible(True)
    o = ctor.newInstance()
    fctor = AFF.class_.getDeclaredConstructor()
    fctor.setAccessible(True)
    f = fctor.newInstance()
    ff = AFF.class_.getDeclaredField("force")
    ff.setAccessible(True)
    ff.setDouble(f, 20.0)
    fs = JArray(AFF)([f])
    fld = AFI.class_.getDeclaredField("forces")
    fld.setAccessible(True)
    fld.set(o, fs)
    INT = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
    cp = INT.class_.getDeclaredField("cachedPacket")
    cp.setAccessible(True)
    cp.set(o, JClass("java.lang.ref.SoftReference")(JString("stale")))
    w1 = str(R.thrustOn(o, 125))
    K.check(abs(float(ff.getDouble(f)) - 25.0) < 1e-9 and cp.get(o) is None and "20 -> 25" in w1, "X5: x125 on a real ApplyForceInteraction: force 20 -> 25, packet cache dropped (%s)" % w1)
    R.thrustOn(o, 125)
    K.check(abs(float(ff.getDouble(f)) - 25.0) < 1e-9, "X5: twice = still 25 (from the kept vanilla value, never compounding)")
    R.thrustOn(o, 100)
    K.check(abs(float(ff.getDouble(f)) - 20.0) < 1e-9, "X5: 100 = vanilla again")
    R.thrustOn(o, 150)
    cp.set(o, JClass("java.lang.ref.SoftReference")(JString("stale")))
    K.check(abs(float(ff.getDouble(f)) - 30.0) < 1e-9 and str(R.thrustRestore()) == "restored to vanilla" and abs(float(ff.getDouble(f)) - 20.0) < 1e-9
            and cp.get(o) is None, "X5 (fix 3): shutdown's thrustRestore puts the vanilla 20 back + drops the packet cache")
    K.check("not loaded" in str(R.thrustOn(None, 125)) and "not loaded" in str(R.thrust()), "X5: no asset = the dash stays vanilla, said so")
    # X6 the blink afterimages (the particle seam)
    PL = JClass("java.util.ArrayList")()
    Trav.PSEEN = PL
    n1 = int(Trav.shadowTrail(0.0, 64.0, 0.0, 16.0, 64.0, 0.0, None))
    n2 = int(Trav.shadowTrail(0.0, 64.0, 0.0, 1.0, 64.0, 0.0, None))
    n3 = int(Trav.shadowTrail(0.0, 64.0, 0.0, 0.0, 64.0, 0.0, None))
    Trav.PSEEN = None
    K.check(n1 == 9 and n2 == 2 and n3 == 0 and all(str(x) == "SkyyArmory_Shadow_Fade" for x in PL), "X6: shadowTrail: 16 blocks = 9 afterimages (max 8 steps), 1 block = 2, "
            "none in place; all SkyyArmory_Shadow_Fade (%d %d %d)" % (n1, n2, n3))
    # X7 the world-thread paths without a world
    KJ = JClass(PKG + "KunaiJob")
    KJ(5, U, None, DA([1.0, 0.0, 0.0]), 0, 0.0, 0.0).run()
    K.eq(str(R.LAST_WHY), "the shield bearer left this world", "X7: KunaiJob kind 5 runs Rush.dash as Bulwark Charge (no player = nothing happens)")
    KJ(4, U, None, DA([1.0, 0.0, 0.0]), 0, 0.0, 0.0).run()
    K.eq(str(R.LAST_WHY), "the swordsman left this world", "X7: kind 4 = Crescent Rush")
    R.PEND.put(U, state())
    R.tickPlayer(None, None, None)
    K.check(R.PEND.containsKey(U), "X7: tickPlayer without a player leaves the lunge alone")
    R.clear()
    K.check(R.PEND.isEmpty(), "X7: clear() empties the lunges")
    K.eq([int(Defs.pidCode("SkyyArmory_Crescent_Rush")), int(Defs.pidCode("SkyyArmory_Bulwark_Charge"))], [15000, 15001], "X7: the marker codes")
    st = str(R.statusText())
    K.check("Bulwark Charge" in st and "sword dash:" in st and "blink afterimages" in st, "X7: statusText: %s" % st[:200])
    # X8 the loader: clamps + the restart latch
    P = JClass("java.util.Properties")()
    for k_, v_ in (("blade.rush.speed", "99"), ("gshield.charge.distance", "0"), ("gshield.charge.stamina", "50"), ("blade.rush.carryGap", "0"),
                   ("sword.thrust.percent", "300"), ("blink.shadowTrail", "false"), ("gshield.charge.enabled", "off")):
        P.setProperty(k_, v_)
    K.check(bool(Cfg.THRUST_SET) and int(Cfg.THRUST_PCT) == 125, "X8: the first load latched the sword dash at 125")
    Cfg.apply(P)
    K.eq([float(Cfg.RUSH_SPEED), float(Cfg.GS_DIST), float(Cfg.GS_STAM), float(Cfg.RUSH_GAP), int(Cfg.THRUST_PCT), int(Cfg.THRUST_NEXT), bool(Cfg.BLINK_SHADOW), bool(Cfg.GS_ON)],
         [40.0, 1.0, 10.0, 0.5, 125, 200, False, False], "X8: the loader clamps like the rows; a live reload keeps the running sword dash (restart row)")
    K.check("x200 after a restart" in str(Cfg.BLADE_TEXT) and "Bulwark Charge OFF" in str(Cfg.BLADE_TEXT), "X8: the text says the dash waits for a restart")
    Cfg.THRUST_SET = False
    Cfg.apply(P)
    K.check(int(Cfg.THRUST_PCT) == 200 and "after a restart" not in str(Cfg.BLADE_TEXT).split("Warrior sword dash")[1], "X8: a fresh start reads 200")
    Cfg.THRUST_SET = False
    Cfg.GUARD_SET = False
    Cfg.useDefaults()
    rk = [str(x) for x in JClass(PKG + "CfgRows").KEYS]
    K.check("blade.rush.pathHit" not in rk and "blade.rush.speed" in rk and "gshield.charge.distance" in rk and "sword.thrust.percent" in rk
            and "blink.shadowTrail" in rk, "X8 (fix 8): Server Setup rows: the dead blade.rush.pathHit hidden, the new rows listed (%d rows)" % len(rk))
    dc = str(Cfg.DEF_CFG)
    K.check(all(("%s=%s" % (k_, v_)) in dc for k_, v_ in (("gshield.charge.distance", "8"), ("gshield.charge.mana", "4"), ("gshield.charge.stamina", "5"),
            ("blade.rush.speed", "15"), ("sword.thrust.percent", "125"), ("blink.shadowTrail", "true"))), "X8: the default config file carries the new rows")
    K.save()


# ---------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    files0 = sorted(os.listdir(home))
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.29 (new keys read their defaults)")
    K.check(sorted(f_ for f_ in os.listdir(home) if not f_.startswith("config-history")) == sorted(f_ for f_ in files0 if not f_.startswith("config-history")),
            "D: no new file in the data folder")
    K.check(bool(Cfg.GS_ON) and int(Cfg.THRUST_PCT) == 125 and float(Cfg.RUSH_SPEED) == 15.0 and bool(Cfg.BLINK_SHADOW), "D: Skyy's file has no new lines -> the defaults apply")
    K.notes.append("D: live config.properties %s bytes" % (len(before) if before else 0))
    K.save()


def main():
    phases = {"mkfake": lambda: HK.run_mkfake(os.path.join(SCRATCH, "fake"), JAR), "verify": lambda: HK.run_verify(HK.arg("--out"), JAR),
              "audit": lambda: HK.run_audit(HK.arg("--out"), JAR, os.path.join(SCRATCH, "fake")),
              "compare": lambda: run_compare(HK.arg("--out"), JAR, SCRATCH, None), "exec": lambda: run_exec(HK.arg("--out"), JAR, SCRATCH, None),
              "live": lambda: run_live(HK.arg("--out"), JAR, SCRATCH, HK.arg("--home"))}
    if "--phase" in sys.argv:
        try:
            phases[HK.arg("--phase")]()
        except SystemExit:
            raise
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR), (JAR, OLD_JAR)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(SCRATCH, "fake"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]

    def child(label, *extra):
        out = os.path.join(SCRATCH, "%s.json" % label)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", out, "--dir", SCRATCH, "--jar", JAR] + list(extra), env=env)
        HK.check(p.returncode == 0, "%s: the child exited cleanly (%s)" % (label, p.returncode))
        return out
    try:
        run_assets()
        child("mkfake")
        for label in ("verify", "compare", "exec"):
            HK.take(child(label), label)
        home = os.path.join(SCRATCH, "live", "Skyy_SkyyArmory")
        if os.path.isdir(LIVE_DIR):
            shutil.copytree(LIVE_DIR, home)
            print("D. live Skyy_SkyyArmory copied (read-only source %s)" % LIVE_DIR)
            HK.take(child("live", "--home", home), "live")
        else:
            HK.check(False, "D: no live folder %s" % LIVE_DIR)
        outa = child("audit")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            HK.check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            HK.check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyArmory %s harness: %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
    for f in HK.FAILS:
        print("FAIL:", f)
    sys.exit(1 if HK.FAILS else 0)


if __name__ == "__main__":
    main()
