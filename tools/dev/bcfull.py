import sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
from jpype import JClass
IP = JClass("javassist.bytecode.InstructionPrinter"); PS = JClass("java.io.PrintStream"); BOS = JClass("java.io.ByteArrayOutputStream")
for spec in sys.argv[1:]:
    parts = spec.split("#")
    cls, m = parts[0], parts[1]
    sig = parts[2] if len(parts) > 2 else None
    cc = pool.get(cls)
    for mm in cc.getDeclaredMethods():
        if str(mm.getName()) == m and (sig is None or sig in str(mm.getSignature())):
            bos = BOS(); ip = IP(PS(bos)); ip.print_(mm)
            print("==", cls, m, mm.getSignature()); print(str(bos.toString()))
