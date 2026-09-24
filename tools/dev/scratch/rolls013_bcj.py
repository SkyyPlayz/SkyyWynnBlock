import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
pool.appendClassPath(sys.argv[1])
from jpype import JClass
IP = JClass("javassist.bytecode.InstructionPrinter"); PS = JClass("java.io.PrintStream"); BOS = JClass("java.io.ByteArrayOutputStream")
for spec in sys.argv[2:]:
    cls, m = spec.rsplit("#", 1)
    cc = pool.get(cls)
    for mm in cc.getDeclaredMethods():
        if str(mm.getName()) == m:
            bos = BOS(); ip = IP(PS(bos)); ip.print_(mm)
            print("==", cls, m, mm.getSignature()); print("\n".join(l for l in str(bos.toString()).splitlines() if l.strip()))
