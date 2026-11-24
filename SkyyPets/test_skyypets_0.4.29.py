"""Harness for SkyyPets 0.4.29 (pets:fn:tab starter lines + pets:fn:tabact start / efuse for SkyyMenu 0.3.70's Pets tab; tools/pets_0_4_29_patch.py,
round oldmenu2). Build first:
    python tools/pets_0_4_29_patch.py && python SkyyPets/build_skyypets_0.4.29.py
    python SkyyPets/test_skyypets_0.4.29.py [--keep] [--expect-dump] [--dir <folder inside tools/dev/scratch/>]

  S     static   the patch re-runs to identical bytes; no class / system / command / setting added; the jar adds and removes nothing, changed
                 non-class entries = manifest.json; both keys still published
  A/C/AA         (tools/harness_kit.py, -Xverify:all) verify, class compare 0.4.28 -> 0.4.29, engine-access audit
  OLD2  EXECUTED on 0.4.4's stand-in world (real PetStore / PetOps / PetHatchery + the fake inventory):
                 START   a profile waiting for its first pet: the read carries 4 st| lines (type, pet, Common portrait, perk words, on) - none
                         once chosen; op start = the old page's two presses (another type in between asks again), the pet made ONCE, a third
                         press = "already have", a wrong profile token refused (nothing made), the 350 ms guard, an old ask (16 s) asks again
                 EFUSE   op efuse = the old page's Fuse eggs: the first press asks (nothing moves), the second fuses N eggs into 1 of the next
                         rarity ONCE, a double click = "=One moment.", the inventory count changed between the presses = asks again, too few
                         eggs / not an egg / no inventory / a full inventory (everything back) refused
  the 0.4.28 TAB phase + the 0.4.27 phases (SUMMON / PETSLOT / EGGS / IDLE / AGG / REAL / MIG / ECS / PT / live / live2) run again on this jar.
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "oldmenu2", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T428 = _mod(os.path.join(HERE, "test_skyypets_0.4.28.py"), "test_skyypets_0_4_28")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T427, T425, T424, T423, T417, T44, T41 = T428.T427, T428.T425, T428.T424, T428.T423, T428.T417, T428.T44, T428.T41

VERSION = "0.4.29"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.28.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.28.py")
PATCH = os.path.join(TOOLS, "pets_0_4_29_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T428.JAR = T427.JAR = T425.JAR = T424.JAR = T423.JAR = JAR
ADDED = []
EXPECT = {   # 0.4.29: PetTabFn's read (the starter lines) + act (start / efuse); the version text baked into the config kit + migration lines + setup
    'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'PetsCfg': ['~m applyAll', '~m seed'], 'PetsMigDrg': ['~m run'],
    'PetsMigP5': ['~m mgLog', '~m run'], 'PetsMigS2': ['~m run'], 'PetsMigW15': ['~m run'], 'SkyyPetsPlugin': ['~m setup'],
    'PetTabFn': ['~m act', '~m read'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
# the 0.4.25 MIG phase names its version in the Changes line it expects: the same phase with this version
_t425 = open(T425.__file__, encoding="utf8").read()
_src = _t425[_t425.index("def run_mig("):_t425.index("\ndef ", _t425.index("def run_mig(")) + 1]
for _old in (r"\tSkyyPets 0.4.25\t", r"\tSkyyPets 0.4.27\t", r"\tSkyyPets 0.4.28\t"):
    if _src.count(_old) == 1:
        exec(compile(_src.replace(_old, r"\tSkyyPets 0.4.29\t"), T425.__file__, "exec"), T425.__dict__)
        break
else:
    raise AssertionError("0.4.25's MIG phase changed")


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.29 - build script') and g.count('VERSION = "0.4.29"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("= cls(") == o.count("= cls("), "S no class, system or command added")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.check(g.count("CfgRow(") == o.count("CfgRow("), "S no setting added")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, os.path.basename(GEN))
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    K.check('bridge().put("pets:fn:tab", new @PKG@.PetTabFn(0));' in g and 'bridge().put("pets:fn:tabact", new @PKG@.PetTabFn(1));' in g,
            "S pets:fn:tab + pets:fn:tabact published")
    K.check('return ask(u, c, @PKG@.PetOps.pickAsk(si));' in g and 'if (confirmed(u, c)) return @PKG@.PetSnd.slotDone(u, @PKG@.PetOps.chooseStarter(u, si, who), true);' in g
            and 'if (confirmed(u, c)) return @PKG@.PetHatchery.efuse(u, inv, a, who);' in g and 'return ask(u, c, @PKG@.PetHatchery.efuseAsk(u, inv, a));' in g,
            "S start + efuse call the old page's own doors (pickAsk / chooseStarter / efuseAsk / efuse) - no new rule")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), [], "S the jar adds nothing")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


# ======================================================================================================== OLD2: start + efuse, executed
def run_old2(out, jar, scratch, _home):
    W = T424._world(out, jar, scratch, "old2")
    K, JClass = W["K"], W["JClass"]
    Hy, Egg, Ops, Store, Cfg = W["PetHatchery"], W["PetEgg"], W["PetOps"], W["PetStore"], W["PetsCfg"]
    TF = JClass(PKG + "PetTabFn")
    Inv, pi = T41.Inv, T41.proxy_inv
    T427._tells(W)
    EC, EU = "Skyy_PetEgg_Mining_Common", "Skyy_PetEgg_Mining_Uncommon"
    u, k, r = T44._mk(W, 961)
    r.set("starter", "choose")
    Store.save(r)
    inv = Inv({"Food_Egg": 1})

    def rd(iv=None):
        s_ = TF.read(u, "", 0, 0, 0, 42, "", pi(iv if iv is not None else inv))
        return None if s_ is None else str(s_)

    def lines(s_, pre):
        return [l_.split("|") for l_ in s_.split("\n") if l_.startswith(pre + "|")]

    def act(op, arg, iv=None, tok=None, clear=True):
        if clear:
            TF.LAST.clear()
            Hy.CLICK.clear()
        return str(TF.act(u, k if tok is None else tok, op, arg, "harness", pi(iv if iv is not None else inv), None, None, None))
    # ---- START
    K.check(bool(Ops.starterPending(r)) and int(r.count()) == 0, "OLD2 START the stand-in profile waits for its first pet (starter=choose, no pets)")
    s = rd()
    st = lines(s, "st")
    hd = s.split("\n")[0].split("|")
    K.check(len(hd) == 15 and hd[14] == "1", "OLD2 START the header is unchanged (15 fields, starter pending = 1)")
    K.check(len(st) == 4 and [x[2] for x in st] == ["Mining", "Farming", "Foraging", "Combat"] and all(len(x) == 7 for x in st)
            and all(x[6] == "1" for x in st) and all(x[5].startswith("Up to ") or x[5] == "No buffs" for x in st)
            and all(x[4] == "" or x[4].endswith("_Common") for x in st),
            "OLD2 START the read: 4 st| lines (type, pet, its Common portrait, perk words, on): %s" % [x[1:5] for x in st])
    K.notes.append("OLD2 the starter lines: %s" % st)
    n0 = int(r.count())
    m = act("start", "0", tok="old-profile")
    K.check(m.startswith("=Your profile changed") and int(r.count()) == n0 and bool(Ops.starterPending(r)), "OLD2 SAFE a wrong profile token: refused, no pet (%s)" % m)
    m1 = act("start", "1")
    K.check(m1.startswith("=Make the ") and "Press Choose on it again" in m1 and int(r.count()) == n0, "OLD2 START the first press asks (PetOps.pickAsk), no pet: %s" % m1)
    m2 = act("start", "2")
    K.check(m2.startswith("=Make the ") and int(r.count()) == n0, "OLD2 START another type in between = asks again for THAT type (nothing made)")
    _c = str(TF.CONF.get(u))
    TF.CONF.put(u, _c.rsplit(chr(30), 1)[0] + chr(30) + str(int(time.time() * 1000) - 16000))
    mx = act("start", "2")
    K.check(mx.startswith("=Make the ") and int(r.count()) == n0, "OLD2 SAFE an ask older than 15 s never confirms (asks again)")
    m3 = act("start", "2")
    K.check(m3.startswith("+Your first pet is a Common ") and int(r.count()) == n0 + 1 and not bool(Ops.starterPending(r)),
            "OLD2 START the same type twice = PetOps.chooseStarter: ONE Common pet, the choice closed: %s" % m3)
    m4 = act("start", "2", clear=False)
    K.check(m4 == "=One moment." and int(r.count()) == n0 + 1, "OLD2 SAFE a double click (350 ms) = '=One moment.', still ONE pet")
    m5 = act("start", "2")
    m6 = act("start", "2")
    K.check(m5 == "=You already have your first pet." and m6 == m5 and int(r.count()) == n0 + 1, "OLD2 START after the choice = 'already have', nothing made")
    K.check(lines(rd(), "st") == [], "OLD2 START the read has no starter lines once chosen")
    K.check(act("start", "9").startswith("=You already have"), "OLD2 SAFE a bad type after the choice = 'already have'")
    r.set("starter", "choose")
    Store.save(r)
    K.check(act("start", "9").startswith("-There is no such starter pet") and int(r.count()) == n0 + 1, "OLD2 SAFE a type that does not exist = refused (no ask)")
    r.set("starter", "1")
    Store.save(r)
    # ---- EFUSE
    need = int(Cfg.EFUSE_COUNT) if int(Cfg.EFUSE_COUNT) >= 2 else 2
    K.check(bool(Cfg.EFUSE_ON), "OLD2 EFUSE egg fusing is on (the default)")
    invE = Inv({EC: need})
    m1 = act("efuse", EC, iv=invE)
    K.check(m1.startswith("=Fuse %d " % need) and invE.count(EC) == need and invE.count(EU) == 0, "OLD2 EFUSE the first press asks (PetHatchery.efuseAsk), nothing moves: %s" % m1)
    m2 = act("efuse", EC, iv=invE)
    K.check(m2.startswith("+") and invE.count(EC) == 0 and invE.count(EU) == 1, "OLD2 EFUSE the second press = PetHatchery.efuse: %d Common -> 1 Uncommon, ONCE: %s" % (need, m2))
    m3 = act("efuse", EC, iv=invE, clear=False)
    K.check(m3 == "=One moment." and invE.count(EU) == 1, "OLD2 SAFE a double click = '=One moment.' (nothing more)")
    invC = Inv({EC: need})
    act("efuse", EC, iv=invC)
    invC.live[EC] = need + 1
    m4 = act("efuse", EC, iv=invC)
    K.check(m4.startswith("=Fuse") and invC.count(EC) == need + 1 and invC.count(EU) == 0, "OLD2 SAFE the egg count changed between the presses = asks again (nothing fused)")
    invL = Inv({EC: need - 1})
    m5 = act("efuse", EC, iv=invL)
    K.check(m5.startswith("-You need ") and invL.count(EC) == need - 1, "OLD2 EFUSE too few eggs = refused: %s" % m5)
    K.check(act("efuse", "Rock_Stone").startswith("-That is not a pet egg") and act("efuse", "").startswith("-That is not a pet egg"), "OLD2 SAFE not a pet egg = refused")
    m6 = str(TF.act(u, k, "efuse", EC, "harness", None, None, None, None))
    K.check(m6.startswith("-Your inventory could not be read"), "OLD2 SAFE no inventory = refused, nothing moves")
    invF = Inv({EC: need}, refuse={EU})
    act("efuse", EC, iv=invF)
    m7 = act("efuse", EC, iv=invF)
    K.check(m7.startswith("-") and invF.count(EC) == need and invF.count(EU) == 0, "OLD2 SAFE a full inventory = refused, every egg back: %s" % m7)
    m8 = act("efuse", EC, iv=invE, tok="old-profile")
    K.check(m8.startswith("=Your profile changed"), "OLD2 SAFE a wrong profile token: refused")
    K.notes.append("OLD2 counters: reads %d acts %d stale %d guard %d" % (int(TF.READS.get()), int(TF.ACTS.get()), int(TF.STALE.get()), int(TF.GUARD.get())))
    K.save()


if __name__ == "__main__":
    P_ = T427._phase
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[P_("static", run_static), P_("old2", run_old2), P_("tab", T428.run_tab), P_("summon", T427.run_summon), P_("petslot", T427.run_petslot),
                   P_("eggs", T427.run_eggs), P_("idle", T427._petslot(T425.run_idle)), P_("agg", T427._petslot(T425.run_agg)), P_("real", T425.run_real),
                   P_("mig", T425.run_mig), P_("ecs", T424.run_ecs), P_("pt", T425._old(T423.run_pt)),
                   P_("live", T417.run_live), P_("live2", T425.run_live2)],
           script=__file__, live=(T423.T422.T421.T41.LIVE, "Skyy_SkyyPets"))
