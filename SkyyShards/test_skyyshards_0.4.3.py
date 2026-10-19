"""Harness for SkyyShards 0.4.3 (TOTEM BENCH WORST ORB FIRST; tools/shards_0_4_3_patch.py).
Build first: python tools/shards_0_4_3_patch.py && python SkyyShards/build_skyyshards_0.4.3.py

    python SkyyShards/test_skyyshards_0.4.3.py [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.2 -> 0.4.3: no class added / removed; exactly the planned members differ (EXPECT)
  X / D the 0.4.2 harness's exec (the derived 0.4 X1-X10) + live phases (test_skyyshards_0.4.2.py) on THIS jar - every check as it
                was (0.4.3 changes only ShInv.take2's order of stacks with metadata). Its mig / live2 phases are left out: they test the
                0.4.2 one-time migCoop against the live config still holding shard.coopCollect=false, which the 0.4.2 deploy has migrated;
                ShCfg is byte-identical to 0.4.2 (C proves it)
  W    worst    ShInv.take2 on real containers with rolled Soul Orbs (SkyyGear documents):
                W1 a Rare in storage + a Common in the hotbar: take 1 = the Common (the Rare stays); giveBack = the exact Common back
                W2 plain stacks still first; take() never touches a stack with metadata
                W3 a document without a rarity key ("lvl" only) or without SkyyGear = the lowest (before a Common)
                W4 equal ranks keep the old order (storage, backpack, hotbar last); a lower level first within a rarity; an unknown rarity
                   id = normal; a 3-orb take across sections = worst three, refund restores all three documents exactly
  AA   engine-access audit
Scratch: tools/dev/scratch/sh43/h (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.3"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sh43", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.2 harness as a module (its own __main__ block does not run); it reads the same --dir / --jar
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_2", os.path.join(HERE, "test_skyyshards_0.4.2.py"))
T42 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T42)
T04 = T42.T04
OID = "Weapon_Wand_SoulOrb"


def run_worst(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    T04.item_store([(OID, 1), ("Ingredient_Void_Essence", 100)])
    Inv = JClass(PKG + "ShInv")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BDc = JClass("org.bson.BsonDocument")
    Short = JClass("java.lang.Short")
    AL = JClass("java.util.ArrayList")

    def inv(*caps):          # storage, hotbar, backpack (ShInv.containers order)
        return JArray(IC)([SIC(Short(c).shortValue()) for c in caps])

    def orb(js):
        return IS(OID, 1).withMetadata("SkyyGear", BDc.parse(js)) if js is not None else IS(OID, 1)

    def put(c, sec, slot, st):
        c[sec].setItemStackForSlot(Short(slot).shortValue(), st)

    def docs(c):
        """[(section, slot, SkyyGear json or None)] of every orb left"""
        o = []
        for ci in range(len(c)):
            for s in range(int(c[ci].getCapacity())):
                it = c[ci].getItemStack(Short(s).shortValue())
                if it is not None and not it.isEmpty() and str(it.getItemId()) == OID:
                    md = it.getMetadata()
                    g = md.get("SkyyGear") if md is not None else None
                    o.append((ci, s, str(g.asDocument().toJson()) if g is not None else None))
        return o

    def kj(kept):
        return [str(x.getMetadata().get("SkyyGear").asDocument().toJson()) if x is not None and x.getMetadata() is not None and x.getMetadata().get("SkyyGear") is not None else None for x in kept]
    J = lambda s: str(BDc.parse(s).toJson())
    RARE, COMMON = '{"r": "rare", "lvl": 3}', '{"r": "normal", "lvl": 7}'

    # W1 the bug: a Rare in storage, a Common in the hotbar -> the Common is used
    c = inv(4, 2, 2)
    put(c, 0, 0, orb(RARE))
    put(c, 1, 1, orb(COMMON))
    kept = AL()
    t = int(Inv.take2(c, OID, JLong(1), kept))
    left = docs(c)
    K.check(t == 1 and kj(kept) == [J(COMMON)] and left == [(0, 0, J(RARE))],
            "W1 Rare (storage) + Common (hotbar): take2 1 = the Common, the Rare stays: kept %s left %s" % (kj(kept), left))
    b = int(Inv.giveBack(c, OID, JLong(1), kept))
    K.check(b == 1 and sorted(x[2] for x in docs(c)) == sorted([J(RARE), J(COMMON)]), "W1 giveBack = the exact Common back (document intact): %s" % docs(c))
    K.check(int(Inv.wear(orb(RARE))) == 200003 and int(Inv.wear(orb(COMMON))) == 7 and int(Inv.wear(orb('{"lvl": 5}'))) == -1
            and int(Inv.wear(orb(None))) == -1 and int(Inv.wear(orb('{"r": "weird", "lvl": 2}'))) == 2 and int(Inv.wear(orb('{"r": "Mythic"}'))) == 700000,
            "W1 wear = rarity x 100000 + lvl; no rarity key / no document = -1; unknown id = normal; case-insensitive")

    # W2 plain first; take() never touches metadata stacks
    c = inv(4, 2, 2)
    put(c, 0, 0, orb(COMMON))
    put(c, 1, 0, orb(None))
    kept = AL()
    t = int(Inv.take2(c, OID, JLong(1), kept))
    K.check(t == 1 and kept.size() == 0 and docs(c) == [(0, 0, J(COMMON))], "W2 a plain orb (hotbar) is taken before a rolled Common (storage): %s" % docs(c))
    t2 = int(Inv.take(c, OID, JLong(1)))
    K.check(t2 == 0 and docs(c) == [(0, 0, J(COMMON))], "W2 take() (no kept) never takes a stack with metadata")

    # W3 no rarity key / non-gear metadata = the lowest
    c = inv(4, 2, 2)
    put(c, 0, 0, orb(COMMON))
    put(c, 1, 0, orb('{"lvl": 50}'))
    kept = AL()
    Inv.take2(c, OID, JLong(1), kept)
    K.check(kj(kept) == [J('{"lvl": 50}')] and docs(c) == [(0, 0, J(COMMON))], "W3 an orb whose document has no rarity key goes before a Common: %s" % kj(kept))
    c = inv(4, 2, 2)
    put(c, 0, 0, orb(COMMON))
    put(c, 2, 1, IS(OID, 1).withMetadata("Tag", BDc.parse('{"a": 1}')))
    kept = AL()
    Inv.take2(c, OID, JLong(1), kept)
    K.check(kept.size() == 1 and kept.get(0).getMetadata().get("Tag") is not None and docs(c) == [(0, 0, J(COMMON))],
            "W3 a stack with other metadata (no SkyyGear) goes before a Common")

    # W4 ties keep the old order (storage, backpack, hotbar last); lower level first; unknown id = normal; 3 at once + exact refund
    c = inv(4, 2, 2)
    put(c, 1, 0, orb('{"r": "normal", "lvl": 7, "u": "hot"}'))
    put(c, 2, 0, orb('{"r": "normal", "lvl": 7, "u": "pack"}'))
    put(c, 0, 3, orb('{"r": "normal", "lvl": 7, "u": "sto"}'))
    kept = AL()
    Inv.take2(c, OID, JLong(2), kept)
    K.check(kj(kept) == [J('{"r": "normal", "lvl": 7, "u": "sto"}'), J('{"r": "normal", "lvl": 7, "u": "pack"}')] and len(docs(c)) == 1 and docs(c)[0][0] == 1,
            "W4 equal ranks: storage, then backpack, the hotbar last: %s" % kj(kept))
    c = inv(4, 2, 2)
    L = ['{"r": "rare", "lvl": 5}', '{"r": "legendary", "lvl": 1}', '{"r": "rare", "lvl": 1}', '{"r": "weird", "lvl": 9}', '{"r": "unique", "lvl": 2}']
    put(c, 1, 0, orb(L[0]))
    put(c, 0, 0, orb(L[1]))
    put(c, 0, 1, orb(L[2]))
    put(c, 2, 1, orb(L[3]))
    put(c, 1, 1, orb(L[4]))
    Inv.give(c, "Ingredient_Void_Essence", JLong(3))
    kept = AL()
    t = int(Inv.take2(c, OID, JLong(3), kept))
    K.check(t == 3 and kj(kept) == [J(L[3]), J(L[4]), J(L[2])] and sorted(x[2] for x in docs(c)) == sorted([J(L[0]), J(L[1])]),
            "W4 3 orbs across sections = worst three: unknown id (normal) lvl 9, Unique, Rare lvl 1 (Rare lvl 5 + Legendary stay): %s" % kj(kept))
    txt = str(Inv.keptText(kept))
    b = int(Inv.giveBack(c, OID, JLong(3), kept))
    K.check(b == 3 and sorted(x[2] for x in docs(c)) == sorted(J(x) for x in L) and txt.count(";") == 3 and int(Inv.count(c, "Ingredient_Void_Essence")) == 3,
            "W4 refund: all five documents back exactly, keptText lists the three: %s" % txt[:120])
    K.save()


EXPECT = {
    "ShInv": ["+m gearRank", "+m wear", "~m take2"],
    # the version text only: the profile file header / forms-migration log line, the ready line, the config kit's VERSION
    "ShStore": ["~m save", "~m migrate"], "SkyyShardsPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
}

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("worst", run_worst), ("exec", T04.run_exec), ("live", T04.run_live)],
           script=__file__, live=(T42.LIVE_SH, "mods/Skyy_SkyyShards"))
