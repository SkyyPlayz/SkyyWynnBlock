import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
from jpype import JClass
IP = JClass("javassist.bytecode.InstructionPrinter")
def dump(cls, pred):
    cc = pool.get(cls)
    for k in list(cc.getDeclaredConstructors()) + list(cc.getDeclaredMethods()):
        if not pred(k): continue
        mi = k.getMethodInfo(); ca = mi.getCodeAttribute(); cp = mi.getConstPool()
        print("==", cls, k.getName(), k.getSignature())
        it = ca.iterator()
        while it.hasNext():
            pos = it.next(); print(pos, IP.instructionString(it, pos, cp))
dump("com.hypixel.hytale.server.core.inventory.ItemStack", lambda k: str(k.getName())=="ItemStack" and str(k.getSignature())=="(Ljava/lang/String;IDDLorg/bson/BsonDocument;)V")
dump("com.hypixel.hytale.server.core.asset.type.item.config.Item", lambda k: str(k.getName()) in ("getAssetStore","getAssetMap"))
