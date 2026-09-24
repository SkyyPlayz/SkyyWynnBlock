import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
CtNewMethod, CtNewConstructor = J["CtNewMethod"], J["CtNewConstructor"]
AS = "com.hypixel.hytale.assetstore.AssetStore"
c = pool.makeClass("t.FakeStore", pool.get(AS))
c.addConstructor(CtNewConstructor.make("public FakeStore(" + AS + "$Builder b) { super(b); }", c))
c.addMethod(CtNewMethod.make("public com.hypixel.hytale.event.IEventBus getEventBus() { return null; }", c))
c.addMethod(CtNewMethod.make("public void addFileMonitor(String a, java.nio.file.Path p) { }", c))
c.addMethod(CtNewMethod.make("public void removeFileMonitor(java.nio.file.Path p) { }", c))
c.addMethod(CtNewMethod.make("public void handleRemoveOrUpdate(java.util.Set a, java.util.Map b, com.hypixel.hytale.assetstore.AssetUpdateQuery q) { }", c))
c.writeFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rolls013_cls"))
print("ok")
