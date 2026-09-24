import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
cc = pool.get("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenContainerInteraction")
for mm in cc.getDeclaredMethods():
    print(mm.getName(), mm.getSignature())
