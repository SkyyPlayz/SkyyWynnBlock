import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
from jpype import JClass
Mnemonic = JClass("javassist.bytecode.Mnemonic")
cls = sys.argv[1]
cc = pool.get(cls)
ctors = list(cc.getDeclaredConstructors())
for mm in ctors:
    mi = mm.getMethodInfo()
    ca = mi.getCodeAttribute()
    if ca is None:
        print("==", cls, mm.getSignature(), "(no code)"); continue
    it = ca.iterator()
    print("==", cls, mm.getSignature())
    while it.hasNext():
        idx = it.next()
        op = it.byteAt(idx)
        name = str(Mnemonic.OPCODE[op])
        print(" ", idx, name)
