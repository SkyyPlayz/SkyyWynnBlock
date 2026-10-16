"""Harness for SkyyAccessories 0.5.19 (BENCHES USE THE ACCESSORY BAG: bridge acc:fn:bag; tools/accessories_0_5_19_patch.py).
Build first: python tools/accessories_0_5_19_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.19.py

    python SkyyAccessories/test_skyyaccessories_0.5.19.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.5.18 -> 0.5.19: + AccBagFn; AccStore + listK / takeK / putBackK; the plugin's setup / shutdown; the version texts
  BAG acc:fn:bag EXECUTED on the jar's own AccBagFn + the REAL AccStore on scratch bag files: list (retired left out) / take (the slot,
      saved, -1 when absent, a second take finds nothing) / put (that slot when free, else the first free one below the limit; refused
      while the same id or another of its line is in the bag, or no slot is free), the files on disk after each move, a restart (memory
      cleared) reads the same bag; refusals BEFORE anything is looked at: another profile's key, an unreadable bag file, a busy profile,
      bad arguments, no DIR; the plugin publishes / removes the key (setup / shutdown bytecode)
  D   live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyAccessories/bags: every bag file lists the same both times
               without a byte changed; a take + put back on every bag that holds something leaves the same slots (Properties equal)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.5.19"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.18.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "craft01", "acc")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
PKG = "com.skyy.accessories."
EXPECT = {
    "AccStore": ["+m listK", "+m takeK", "+m putBackK"],
    "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],
    "CfgRows": ["~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["AccBagFn"]
T1, T2, T3 = "Skyy_Accessory_Furnace_T1", "Skyy_Accessory_Furnace_T2", "Skyy_Accessory_Furnace_T3"
OTHER = "Skyy_Accessory_Anvil_T1"


def props(f):
    out = {}
    if not os.path.isfile(f):
        return out
    for line in open(f, encoding="latin-1").read().splitlines():
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def run_bag(out, jar, scratch, home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    CHM, System = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System")
    Obj, Int = JClass("java.lang.Object"), JClass("java.lang.Integer")
    Store, Fn, Defs = JClass(PKG + "AccStore"), JClass(PKG + "AccBagFn"), JClass(PKG + "AccDefs")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    Store.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAccessories")
    d = os.path.join(scratch, "bags")
    os.makedirs(d, exist_ok=True)
    fn = Fn()
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0a01")
    k = str(U)
    A = lambda *xs: JArray(Obj)(list(xs))
    call = lambda *xs: fn.apply(A(*xs))
    s = lambda v: None if v is None else str(v)
    K.check(call("list", U, k) is None, "BAG: no DIR (the plugin not set up) -> null, nothing looked at")
    Store.DIR = Paths.get(d)
    K.eq(s(call("list", U, k)), "", "BAG: an empty bag lists \"\"")
    K.check(str(Store.equipK(U, k, JString(T1))) == "" and str(Store.equipK(U, k, JString(OTHER))) == "", "BAG: two accessories equipped (the Equip path)")
    K.eq(s(call("list", U, k)), "%s,%s" % (T1, OTHER), "BAG: list = the bag's ids in slot order")
    f = os.path.join(d, k + ".properties")
    K.check(props(f).get("slot0") == T1 and props(f).get("slot1") == OTHER, "BAG: the bag file holds them (%s)" % props(f))
    r = call("take", U, k, T1)
    K.check(isinstance(int(r), int) and int(r) == 0 and s(call("list", U, k)) == OTHER and "slot0" not in props(f) and props(f).get("slot1") == OTHER,
            "BAG: take T1 -> slot 0, the bag lists only the other one, the file no longer has slot0 (%s)" % props(f))
    K.eq(int(call("take", U, k, T1)), -1, "BAG: a second take of T1 finds nothing (-1) - never twice")
    K.check(bool(call("put", U, k, T1, Int(0))) and props(f).get("slot0") == T1 and s(call("list", U, k)) == "%s,%s" % (T1, OTHER),
            "BAG: put T1 back into slot 0 -> TRUE, saved there")
    K.check(not bool(call("put", U, k, T1, Int(5))), "BAG: put T1 again while T1 is in the bag -> refused (never two)")
    K.check(not bool(call("put", U, k, T2, Int(5))), "BAG: put T2 while T1 (its line) is in the bag -> refused (no swap through the bridge)")
    int(call("take", U, k, T1))
    K.check(str(Store.equipK(U, k, JString(T2))) == "", "BAG: the player equips T2 meanwhile (slot 0 free -> used)")
    K.check(not bool(call("put", U, k, T1, Int(0))) and s(call("list", U, k)) == "%s,%s" % (T2, OTHER),
            "BAG: putting T1 back while T2 of its line is in -> refused (the caller keeps T1 in the inventory)")
    int(call("take", U, k, T2))
    K.check(bool(call("put", U, k, T1, Int(7))) and props(f).get("slot7") == T1 and "slot0" not in props(f),
            "BAG: the slot given (where it came from) is used when it is free (slot 7)")
    int(call("take", U, k, T1))
    # no slot given / taken: the first free slot below the server limit; none free -> refused
    old_slots = int(Store.SLOTS)
    Store.SLOTS = 2
    Store.equipK(U, k, JString("Skyy_Accessory_Salvagebench_T1"))
    K.check(not bool(call("put", U, k, T1, Int(-1))), "BAG: no slot given and no free slot below the server limit -> refused")
    K.check(not bool(call("put", U, k, T1, Int(7))) and "slot7" not in props(f), "BAG: a slot at / above the server limit (7 >= 2) is never filled (review fix A3)")
    K.check(not bool(call("put", U, k, "Ore_Iron", Int(-1))) and not bool(call("put", U, k, "Weapon_Sword_Iron", Int(-1))),
            "BAG: an id that is not one of our accessories is refused (review fix A3)")
    Store.SLOTS = old_slots
    int(call("take", U, k, T1))
    int(call("take", U, k, "Skyy_Accessory_Salvagebench_T1"))
    K.check(bool(call("put", U, k, T1, Int(-1))) and props(f).get("slot0") == T1, "BAG: no slot given -> the first free slot (slot 0)")
    # retired ids are never listed / taken
    ret = [x for x in ("Skyy_Accessory_Alchemybench_T1", "Skyy_Accessory_Cookingbench_T1") if bool(Defs.isRetired(x))]
    if ret:
        Store.stashK(U, k, JString(ret[0]))
        K.check(ret[0] not in s(call("list", U, k)).split(",") and int(call("take", U, k, ret[0])) == -1,
                "BAG: a retired accessory in the bag is never listed or taken (%s)" % ret[0])
    # restart: memory cleared, the file read again
    want = s(call("list", U, k))
    Store.BAGS.clear()
    K.eq(s(call("list", U, k)), want, "BAG: after a restart (memory cleared) the bag file lists the same")
    # refusals before anything is looked at
    K.check(call("list", U, k + "x") is None and call("take", U, "other-key", T1) is None, "BAG: another profile's key -> null (never another bag)")
    bridge.put("profile:busy:" + k, JClass("java.lang.Boolean").TRUE)
    K.check(call("take", U, k, T1) is None and s(call("list", U, k)) is None, "BAG: profile busy -> null, nothing moves")
    bridge.remove("profile:busy:" + k)
    Store.BADFILE.put(JString(str(Paths.get(d).resolve(k + ".properties"))), JString("test"))
    K.check(call("take", U, k, T1) is None, "BAG: a bag file that could not be read -> null (never written)")
    Store.BADFILE.clear()
    K.check(fn.apply(None) is None and call("take", U) is None and call("take", U, k) is None and call(5, U, k) is None and call("zap", U, k, T1) is None,
            "BAG: bad arguments -> null")
    K.check(T1 in s(call("list", U, k)), "BAG: after the refusals the bag is unchanged")
    # the plugin: setup puts acc:fn:bag, shutdown removes it (bytecode)
    import zipfile
    z = zipfile.ZipFile(jar)
    pc = z.read("com/skyy/accessories/SkyyAccessoriesPlugin.class")
    K.check(pc.count(b"acc:fn:bag") >= 1 and b"AccBagFn" in pc, "BAG: the plugin class names acc:fn:bag + AccBagFn (setup put, shutdown remove)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    CHM, System, Obj, Int = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System"), JClass("java.lang.Object"), JClass("java.lang.Integer")
    Store, Fn = JClass(PKG + "AccStore"), JClass(PKG + "AccBagFn")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    Store.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAccessories")
    bd = os.path.join(home, "bags")
    keys = sorted(f[:-len(".properties")] for f in os.listdir(bd) if f.endswith(".properties") and not f.endswith(".more.properties")) if os.path.isdir(bd) else []
    K.check(len(keys) > 0, "D: the live copy has bag files (%d)" % len(keys))
    Store.DIR = Paths.get(bd)
    fn = Fn()

    @__import__("jpype").JImplements("java.util.function.Function")
    class KeyFn(object):
        def __init__(self):
            self.k = None

        @__import__("jpype").JOverride
        def apply(self, u):
            return self.k
    kf = KeyFn()
    bridge.put("profile:fn:key", kf)
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0a02")
    bridge.put("profile:epoch:" + str(U), JClass("java.lang.Long")(1))
    snap = lambda: dict((f, open(os.path.join(bd, f), "rb").read()) for f in sorted(os.listdir(bd)))
    s0 = snap()
    lists = []
    for start in (1, 2):
        Store.BAGS.clear()
        got = {}
        for k in keys:
            kf.k = k
            v = fn.apply(JArray(Obj)(["list", U, k]))
            got[k] = None if v is None else str(v)
        lists.append(got)
    K.check(lists[0] == lists[1] and all(v is not None for v in lists[0].values()), "D: two starts list every live bag the same (%d bags)" % len(keys))
    K.check(snap() == s0, "D: listing wrote nothing (every bag file byte-identical)")
    moved = 0
    for k in keys:
        ids = [x for x in (lists[0][k] or "").split(",") if x]
        if not ids:
            continue
        kf.k = k
        before = (props(os.path.join(bd, k + ".properties")), props(os.path.join(bd, k + ".more.properties")))
        slot = int(fn.apply(JArray(Obj)(["take", U, k, ids[0]])))
        ok = bool(fn.apply(JArray(Obj)(["put", U, k, ids[0], Int(slot)])))
        after = (props(os.path.join(bd, k + ".properties")), props(os.path.join(bd, k + ".more.properties")))
        K.check(slot >= 0 and ok and after == before, "D: bag %s: take %s (slot %d) + put back -> the same slots" % (k, ids[0], slot))
        moved += 1
    K.notes.append("D: %d live bags, %d take + put round trips" % (len(keys), moved))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("bag", run_bag), ("live", run_live)], script=__file__, live=(os.path.join(LIVE_DIR), "Skyy_SkyyAccessories"))
