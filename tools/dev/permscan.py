import sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
from jpype import JClass
IP = JClass("javassist.bytecode.InstructionPrinter"); PS = JClass("java.io.PrintStream"); BOS = JClass("java.io.ByteArrayOutputStream")
cc = pool.get("com.hypixel.hytale.server.core.command.system.AbstractCommand")
for mm in list(cc.getDeclaredMethods()) + list(cc.getDeclaredConstructors()):
    bos = BOS(); ip = IP(PS(bos));
    try: ip.print_(mm)
    except Exception as e: continue
    s = str(bos.toString())
    hits = [l for l in s.splitlines() if ("AbstractCommand.permission(" in l or "permissionGroups" in l or "openToEveryone" in l)]
    if hits:
        print("==", mm.getName(), mm.getSignature()); print("\n".join(hits))
