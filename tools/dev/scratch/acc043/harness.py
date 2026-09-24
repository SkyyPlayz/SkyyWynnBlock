import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import jpype
JAR = os.path.join(ROOT, "SkyyAccessories", "SkyyAccessories-0.4.3.jar")
jpype.startJVM(B._jvm(), "-Xverify:all", classpath=[JAR, B.SERVER_JAR], convertStrings=True)
J = jpype.JClass
fails = []
def ok(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c: fails.append(msg)

# every class of the jar loads + links + verifies
import zipfile
Class = J("java.lang.Class")
loader = J("java.lang.Thread").currentThread().getContextClassLoader()
for n in zipfile.ZipFile(JAR).namelist():
    if n.endswith(".class"):
        cn = n[:-6].replace("/", ".")
        try:
            Class.forName(cn, True, loader); ok(True, "load+verify " + cn)
        except Exception as e:
            ok(False, "load " + cn + ": " + str(e))

D = J("com.skyy.accessories.AccDefs")
CF, OM = "Skyy_Accessory_Campfire_T1", "Skyy_Accessory_Omni"
ok(not D.isRetired(CF), "Campfire not retired")
for i in ("Skyy_Accessory_Alchemybench_T1", "Skyy_Accessory_Alchemybench_T2", "Skyy_Accessory_Alchemybench_T3", "Skyy_Accessory_Alchemybench_T4", "Skyy_Accessory_Cookingbench_T1"):
    ok(D.isRetired(i), i + " still retired")
    ok(D.rarityOf(i) == 0 and str(D.rarityName(i)) == "Does nothing", i + " rarity 0 / Does nothing")
ok(not D.isRetired("Skyy_Accessory_Workbench_T2") and not D.isRetired(OM), "Workbench / Omni not retired")
ok(D.rarityOf(CF) == 1 and str(D.rarityName(CF)) == "Common" and str(D.rarityColor(CF)) == str(D.RARITY_COLOR[1]), "Campfire Common")
ok(str(D.pretty(CF)) == "Campfire", "pretty Campfire = " + str(D.pretty(CF)))
ok(str(D.pretty("Skyy_Accessory_Alchemybench_T2")) == "Alchemy Bench II - retired", "pretty Alchemy II")
ok(str(D.pretty("Skyy_Accessory_Cookingbench_T1")) == "Cooking Bench - retired", "pretty Cooking")
ok(str(D.retiredWhy("Skyy_Accessory_Alchemybench_T1")).startswith("Retired - brew at a real Alchemy Bench"), "why Alchemy")
ok(str(D.retiredWhy("Skyy_Accessory_Cookingbench_T1")).startswith("Retired - cook at a real Cooking Bench"), "why Cooking")
ok("Cooking Bench accessory is retired" in str(D.retiredChat("Skyy_Accessory_Cookingbench_T1")), "chat Cooking")
ids = [str(x) for x in D.BENCH_IDS]
ok(len(ids) == 11 and ids[-1] == "Campfire" and int(D.BENCH_MAX[10]) == 1 and str(D.BENCH_NAMES[10]) == "Campfire", "BENCH_IDS 11, Campfire last: %s" % ids)
ok([str(x) for x in D.RETIRED] == ["Alchemybench", "Cookingbench"] and [int(x) for x in D.RETIRED_MAX] == [4, 1], "RETIRED arrays")
SA = J("java.lang.String")[:]
def bl(arr):
    return [str(x) for x in D.benchList(SA(arr))]
ok(bl([CF]) == [CF], "benchList Campfire")
o = bl([OM])
ok(len(o) == 11 and CF in o and not any("Alchemy" in x or "Cooking" in x for x in o), "benchList Omni = 11 incl Campfire: %s" % o)
o = bl([CF, OM])
ok(len(o) == 11 and o.count(CF) == 1 and o[0] == CF, "benchList Campfire + Omni: Campfire once")
ok(bl(["Skyy_Accessory_Alchemybench_T4", "Skyy_Accessory_Cookingbench_T1", CF, None]) == [CF], "benchList skips retired, keeps Campfire")

# store: no SkyyProfiles in this JVM -> pkey = uuid
S = J("com.skyy.accessories.AccStore")
tmp = os.path.join(HERE, "bags")
shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
S.DIR = J("java.nio.file.Paths").get(tmp, J("java.lang.String")[:]([]))
UUID = J("java.util.UUID")
u = UUID.randomUUID()
br = S.bridge()
ok(S.moveBlock(u) is None, "moveBlock null without SkyyProfiles")
ok(S.canEquip(u, CF), "canEquip Campfire")
ok(str(S.equip(u, CF)) == "", "equip Campfire into a free slot")
ok(not S.canEquip(u, CF), "second Campfire refused (same tier)")
ok(str(br.get("acc:has:" + str(u))) == CF, "acc:has = " + str(br.get("acc:has:" + str(u))))
ok(S.has(u, CF), "has Campfire")
F = J("com.skyy.accessories.AccFn")()
ok(bool(F.apply(J("java.lang.Object")[:]([u, CF]))), "acc:fn:has Campfire true")
txt = open(os.path.join(tmp, str(u) + ".properties")).read()
ok("slot0=Skyy_Accessory_Campfire_T1" in txt, "bag file saved under the uuid key")
for r in ("Skyy_Accessory_Cookingbench_T1", "Skyy_Accessory_Alchemybench_T3"):
    ok(not S.canEquip(u, r) and S.equip(u, r) is None and not S.has(u, r), r + " refused by the store")
ok(str(S.equip(u, OM)) == "", "equip Omni")
has = str(br.get("acc:has:" + str(u))).split(",")
ok(len(has) == 11 and has.count(CF) == 1, "acc:has with Omni = 11 entries, Campfire once")
ok(S.has(u, "Skyy_Accessory_Salvagebench_T1") and not S.has(u, "Skyy_Accessory_Cookingbench_T1"), "Omni: Salvage yes, Cooking no")
ok(str(S.unequip(u, 0)) == CF and S.canEquip(u, CF), "unequip Campfire, equippable again")
# a bag left over from 0.4.1 (Campfire + Cooking Bench equipped back then)
u2 = UUID.randomUUID()
open(os.path.join(tmp, str(u2) + ".properties"), "w").write("slot0=Skyy_Accessory_Cookingbench_T1\nslot1=Skyy_Accessory_Campfire_T1\n")
S.publish(u2)
ok(str(br.get("acc:has:" + str(u2))) == CF, "old bag: acc:has = Campfire only (Cooking Bench still filtered)")
ok(S.has(u2, CF) and not S.has(u2, "Skyy_Accessory_Cookingbench_T1"), "old bag: has()")
shutil.rmtree(tmp, ignore_errors=True)
print("FAILS:", len(fails))
