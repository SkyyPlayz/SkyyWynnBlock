import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
from jpype import JClass
IP = JClass("javassist.bytecode.InstructionPrinter"); PS = JClass("java.io.PrintStream"); BOS = JClass("java.io.ByteArrayOutputStream")
cc = pool.get(sys.argv[1])
for k in cc.getDeclaredConstructors():
    bos = BOS(); ip = IP(PS(bos)); ip.print_(k.toMethod("ctorx", cc))
    print("==", k.getSignature()); print(str(bos.toString()))
