import sys, jpype, jpype.imports
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
from jpype import JClass
IP = JClass("javassist.bytecode.InstructionPrinter"); PS = JClass("java.io.PrintStream"); BOS = JClass("java.io.ByteArrayOutputStream")
for spec in sys.argv[1:]:
    cls, m = spec.rsplit("#", 1)
    cc = pool.get(cls)
    for mm in cc.getDeclaredMethods():
        if str(mm.getName()) == m:
            bos = BOS(); ip = IP(PS(bos)); ip.print_(mm)
            s = str(bos.toString())
            lines = [l for l in s.splitlines() if "invoke" in l or "getstatic" in l or "ldc" in l or "new " in l or "checkcast" in l]
            print("==", cls, mm.getSignature()); print("\n".join(lines))
