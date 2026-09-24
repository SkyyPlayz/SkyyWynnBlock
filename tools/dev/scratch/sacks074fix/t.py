import sys, os
ROOT = r"C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import jpype, jpype.imports
jpype.startJVM(B._jvm(), "--enable-native-access=ALL-UNNAMED", classpath=[B.SERVER_JAR, os.path.join(ROOT, "SkyySacks", "SkyySacks-0.7.4.jar")], convertStrings=True)
from jpype import JClass, JProxy, JArray, JObject
CP = JClass("com.skyy.sacks.CraftPage")
MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
CHM = JClass("java.util.concurrent.ConcurrentHashMap")
Sys = JClass("java.lang.System")
b = Sys.getProperties().get("skyy.bridge")
if b is None:
    b = CHM(); Sys.getProperties().put("skyy.bridge", b)
fails = []
def check(name, got, want):
    ok = got == want
    print(("ok  " if ok else "FAIL"), name, "->", got)
    if not ok: fails.append(name)
# campNote
b.remove("cook:campfire:ids"); b.remove("cook:fn:campfactors")
check("note no SkyyCooking", str(CP.campNote()).startswith("Campfire accessory = quick emergency cooking: plain food and no Cooking XP"), True)
b.put("cook:campfire:ids", "Food_Wildmeat_Cooked,Food_Fish_Grilled,Food_Vegetable_Cooked")
check("note defaults (no campfactors)", str(CP.campNote()), "Campfire accessory = emergency cook: 50% Cooking XP, 75% of your cooking bonus. A Cooking Bench gives the full Grade and XP.")
Obj = JClass("java.lang.Object")
D = JClass("java.lang.Double"); Bo = JClass("java.lang.Boolean")
def fn(ret):
    class F:
        def apply(self, a): return ret
    return JProxy("java.util.function.Function", inst=F())
b.put("cook:fn:campfactors", fn(JArray(Obj)([D.valueOf(0.6), D.valueOf(0.25), Bo.TRUE])))
check("note live 25/60", str(CP.campNote()), "Campfire accessory = emergency cook: 25% Cooking XP, 60% of your cooking bonus. A Cooking Bench gives the full Grade and XP.")
b.put("cook:fn:campfactors", fn(JArray(Obj)([D.valueOf(0.75), D.valueOf(0.5), Bo.FALSE])))
check("note enabled=false", str(CP.campNote()).startswith("Campfire accessory = quick emergency cooking: graded cooking is switched off"), True)
b.put("cook:fn:campfactors", fn(JClass("java.lang.String")("junk")))
check("note malformed answer -> defaults", "50% Cooking XP, 75%" in str(CP.campNote()), True)
b.put("cook:fn:campfactors", fn(JArray(Obj)([D.valueOf(3.0), JClass("java.lang.String")("x")])))
check("note out-of-range/non-number -> defaults", "50% Cooking XP, 75%" in str(CP.campNote()), True)
b.remove("cook:fn:campfactors")
# hasItemOutput
def mq(i, q=1): return MQ(i, None, None, q, None)
def rec(prim, outs, bench="Campfire"):
    br = BR(); br.id = bench
    return CRR(JArray(MQ)([mq("Food_Wildmeat_Raw")]), prim, outs, 1, JArray(BR)([br]), 2.0, False, 1)
p = mq("Food_Wildmeat_Cooked")
check("hasItemOutput item-embedded shape (outputs=[primary])", bool(CP.hasItemOutput(rec(p, JArray(MQ)([p])))), True)
check("hasItemOutput empty outputs + primary", bool(CP.hasItemOutput(rec(p, JArray(MQ)([])))), True)
check("hasItemOutput null outputs + null primary", bool(CP.hasItemOutput(rec(None, None))), False)
check("hasItemOutput empty outputs + null primary", bool(CP.hasItemOutput(rec(None, JArray(MQ)([])))), False)
check("hasItemOutput resource-only outputs", bool(CP.hasItemOutput(rec(p, JArray(MQ)([MQ(None, "Fuel", None, 1, None)])))), False)
check("hasItemOutput qty 0", bool(CP.hasItemOutput(rec(None, JArray(MQ)([mq("X", 0)])))), False)
check("hasItemOutput null recipe", bool(CP.hasItemOutput(None)), False)
check("campfireRecipe", bool(CP.campfireRecipe(rec(p, JArray(MQ)([p])))), True)
print("FAILS:", fails)
