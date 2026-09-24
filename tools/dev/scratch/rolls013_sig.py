import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
for spec in sys.argv[1:]:
    cls, _, m = spec.partition("#")
    cc = pool.get(cls)
    for mm in list(cc.getDeclaredMethods()):
        if not m or str(mm.getName()) == m:
            print(cls, mm.getName(), mm.getSignature(), mm.getModifiers())
    if not m:
        for f in cc.getDeclaredFields(): print("  F", f.getName(), f.getSignature())
