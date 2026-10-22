"""Harness for SkyyCoins 0.1.11 (packprep: StructureV2's Structure Money -> coins; tools/coins_0_1_11_patch.py).
Build first: python tools/coins_0_1_11_patch.py && python SkyyCoins/build_skyycoins_0.1.11.py

    python SkyyCoins/test_skyycoins_0.1.11.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.10 -> 0.1.11: only CoinConfig (SM, the default text, load), CoinTask (+ the Structure Money methods, ~run), the plugin's ready
              line and the kit's version texts differ
  S  static   the patch re-runs to identical bytes; smConvert runs inside CoinTask.run before the death check; no new class / system / command
  X  exec     EXECUTES the new code: smItem (no item / the item loaded, cached a minute), smCount + smTake on real SimpleItemContainers
              (12 + 7 Structure Money over hotbar / storage / backpack / utility -> all taken, every other stack untouched, before / after),
              smPay on a scratch purse (19 x 10 = 190 coins on top of the balance, per profile key), CoinConfig.load: fresh file = the default text
              (pack.structureMoney=10), a file without the line = 10, 25 = 25, 0 = off, junk = 10 + one WARN, negative = 0
  D  live     the 0.1.6 start-twice phase (every live purse reads the same as 0.1.10) + setup (load, CoinMigP7, kit) TWICE on a scratch COPY of
              the live NewBetaTest Skyy_SkyyCoins: 0.1.11 writes nothing of its own (no migration), the second start changes nothing, SM = 10
  AA engine-access audit
Scratch: tools/dev/scratch/packprep/coins (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCoins-0.1.10.jar")
GEN = os.path.join(HERE, "build_skyycoins_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycoins_0.1.10.py")
PATCH = os.path.join(ROOT, "tools", "coins_0_1_11_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "packprep", "coins")))
PKG = "com.skyy.coins."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCoins")
EXPECT = {
    "CoinConfig": ["+f SM", "~<clinit>", "~m load", "~m save"],          # save: the default text constant
    "CoinTask": ["+f SMAT", "+f SMN", "+f SMOK", "+m smBusy", "+m smConts", "+m smConvert", "+m smCount", "+m smItem", "+m smPay", "+m smTake", "~<clinit>", "~m run"],
    "SkyyCoinsPlugin": ["~m setup"],
    "CfgFile": ["~<clinit>"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
SM = "Sv2_Structure_Money"


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


T16 = tmod(os.path.join(HERE, "test_skyycoins_0.1.6.py"), "tc016_for11")
T16.OLD_JAR = OLD_JAR
T16.LIVE_DIR = LIVE_DIR
T110 = tmod(os.path.join(HERE, "test_skyycoins_0.1.10.py"), "tc0110_for11")


def fake_items(JClass, ids):
    """a bare JVM has no Item asset store: one holding bare Item objects for ids (SkyyGear 0.3.35's harness helper, copied)"""
    from jpype import JString, JObject
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    C = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestItemStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestItemStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    FKC = fk.toClass(AS.class_)

    def fld(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    mp = JClass("java.util.concurrent.ConcurrentHashMap")()
    for i in ids:
        o = US.allocateInstance(C.class_)
        fld(C, "id").set(o, JString(i))
        mp.put(JObject(JString(i), JClass("java.lang.Object")), o)
    st = US.allocateInstance(FKC)
    fld(AS, "tClass").set(st, C.class_)
    fld(AS, "assetMap").set(st, DM(mp))
    fld(JClass("com.hypixel.hytale.assetstore.AssetRegistry"), "storeMap").get(None).put(C.class_, st)
    fld(C, "ASSET_STORE").set(None, st)
    return int(sum(1 for i in ids if C.getAssetMap().getAsset(i) is not None))


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyyCoins 0.1.11 - build script') and g.count('VERSION = "0.1.11"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "pool.makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    run = g[g.index("public void run() {{\n  try {{\n    if (pr == null || !pr.isValid()) return;"):]
    K.check(run.index("smConvert(pr, st, r, u, k);") < run.index("Object death = st.getComponent(r, {DC}.getComponentType());"), "S CoinTask.run converts before the death check")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JShort
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    L = T16.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    CT, CF, CS = J("CoinTask"), J("CoinConfig"), J("CoinStore")
    K.check(not bool(CT.smItem()), "X smItem: StructureV2 not loaded -> off")
    K.eq(fake_items(JClass, [SM, "Ingredient_Bar_Gold", "Weapon_Sword_Iron"]), 3, "X the stand-in item store")
    K.check(not bool(CT.smItem()), "X smItem caches the answer for a minute")
    CT.SMAT = 0
    K.check(bool(CT.smItem()), "X smItem: the item loaded -> on")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    hot, sto, bag, uti = SIC(JShort(9)), SIC(JShort(36)), SIC(JShort(9)), SIC(JShort(4))
    hot.setItemStackForSlot(JShort(0), IS(SM, 12))
    hot.setItemStackForSlot(JShort(1), IS("Weapon_Sword_Iron", 1))
    sto.setItemStackForSlot(JShort(5), IS(SM, 5))
    sto.setItemStackForSlot(JShort(6), IS("Ingredient_Bar_Gold", 20))
    bag.setItemStackForSlot(JShort(2), IS(SM, 2))
    cs = JArray(IC)([hot, sto, bag, uti, None])
    K.eq(int(CT.smCount(cs)), 19, "X smCount: 12 + 5 + 2 over hotbar / storage / backpack (a null section skipped)")
    ba = CT.smTake(cs)
    K.eq([int(ba[0]), int(ba[1])], [19, 0], "X smTake: before 19, after 0")
    K.check(hot.getItemStack(JShort(0)) is None or hot.getItemStack(JShort(0)).isEmpty(), "X the Structure Money slots are empty")
    K.check(str(hot.getItemStack(JShort(1)).getItemId()) == "Weapon_Sword_Iron" and int(sto.getItemStack(JShort(6)).getQuantity()) == 20, "X every other stack untouched")
    K.eq([int(x) for x in CT.smTake(cs)], [0, 0], "X a second pass takes nothing")
    # smPay on a scratch purse
    from jpype import JClass as JC
    Paths = JC("java.nio.file.Paths")
    d = os.path.join(scratch, "x")
    os.makedirs(d, exist_ok=True)
    CS.LOG = JC("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCoins")
    CS.DIR = Paths.get(os.path.join(d, "balances"))
    CS.JOURNAL = Paths.get(os.path.join(d, "balances-journal.properties"))
    CS.recover()
    u = JC("java.util.UUID").fromString("00000000-0000-0000-0000-00000000c011")
    k = str(u)
    CS.loadK(u, k)
    CS.setK(u, k, 1000)
    n0 = int(CT.SMN.get())
    K.eq(int(CT.smPay(None, u, k, 19, 10)), 1190, "X smPay: 19 x 10 coins on top of 1,000")
    K.eq(int(CS.getK(u, k)), 1190, "X the purse holds 1,190")
    K.eq(int(CT.SMN.get()) - n0, 19, "X counted")
    k2 = k + "-p2"
    CS.loadK(u, k2)
    CS.setK(u, k2, 5)
    CT.smPay(None, u, k2, 3, 10)
    K.check(int(CS.getK(u, k2)) == 35 and int(CS.getK(u, k)) == 1190, "X per profile key (p2 gets its own 30)")
    # fixer: profile:busy guard (PROFILES-CONTRACT rule 5) - smConvert returns before touching items while the flag is set
    bm = CS.bridge()
    K.check(not bool(CT.smBusy(u)), "X smBusy: no profile:busy flag -> converts")
    bm.put("profile:busy:" + k, JC("java.lang.Boolean").TRUE)
    K.check(bool(CT.smBusy(u)), "X smBusy: profile:busy set (crash recovery pending) -> the items wait")
    bm.remove("profile:busy:" + k)
    K.check(not bool(CT.smBusy(u)) and bool(CT.smBusy(None)), "X smBusy: flag cleared -> converts again; no UUID -> never")
    gsrc = open(GEN, encoding="utf8", newline="").read()
    conv = gsrc[gsrc.index("public static long smConvert("):]
    K.check(conv.index("if (smBusy(u)) return 0L;") < conv.index("smTake(cs)"), "X smConvert checks smBusy before taking any stack")
    # the config
    cf = os.path.join(d, "config.properties")
    CF.FILE = Paths.get(cf)
    CF.load()
    t = open(cf, encoding="latin-1").read()
    K.check("\npack.structureMoney=10\n" in t and int(CF.SM) == 10, "X a fresh file = the default text with pack.structureMoney=10")
    for line, want in (("", 10), ("pack.structureMoney=25\n", 25), ("pack.structureMoney=0\n", 0), ("pack.structureMoney=lots\n", 10), ("pack.structureMoney=-4\n", 0)):
        open(cf, "w", encoding="latin-1").write("penaltyMin=5\npenaltyMax=5\n" + line)
        CF.load()
        K.eq(int(CF.SM), want, "X pack.structureMoney %r -> %d" % (line.strip() or "(no line)", want))
    K.save()


def run_live(out, jar, scratch, home):
    import json
    from jpype import JClass
    tmp = os.path.join(scratch, "live16.json")
    T16.run_live(tmp, jar, scratch, home)          # 0.1.6: every live purse reads the same as the pinned jar (0.1.10), nothing written
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    h0 = HK.tree_hash(home)
    snaps, msgs = [], []
    for start in (1, 2):
        L = T16.loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        msgs.append(T110.setup_kit(J, home))
        if start == 1:
            K.check(int(J("CoinConfig").SM) == 10, "DL the live copy runs with pack.structureMoney = %s" % J("CoinConfig").SM)
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    K.check(all(n.startswith(("config-history", "config-changes")) for n in new) and changed in ([], ["config.properties"]),
            "DL the first start adds only kit history / change files: changed %s new %s (%s)" % (changed, new, msgs[0][:120]))
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "DL the second start changes nothing")
    K.notes.append("DL first start message: %r" % msgs[0][:200])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCoins", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCoins"))
