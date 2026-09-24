import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
cls = "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Post"
cc = pool.get(cls)
print("==", cls)
for mm in cc.getDeclaredMethods():
    print(" ", mm.getName(), mm.getSignature())
