import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
from jpype import JClass
cls = sys.argv[1]
cc = pool.get(cls)
for f in cc.getDeclaredFields():
    print("field", f.getName(), f.getType().getName())
ctors = list(cc.getDeclaredConstructors())
cp = cc.getClassFile().getConstPool()
for mm in ctors:
    mi = mm.getMethodInfo()
    ca = mi.getCodeAttribute()
    it = ca.iterator()
    print("==", cls, mm.getSignature())
    while it.hasNext():
        idx = it.next()
        op = it.byteAt(idx)
        if op in (0xb5, 0xb4):  # putfield, getfield
            fi = it.u16bitAt(idx+1)
            fname = cp.getFieldrefName(fi)
            ftype = cp.getFieldrefType(fi)
            print(" ", idx, "putfield" if op==0xb5 else "getfield", fname, ftype)
