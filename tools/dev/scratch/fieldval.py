import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
cls = sys.argv[1]; fname = sys.argv[2]
cc = pool.get(cls)
f = cc.getField(fname)
print(fname, "=", f.getConstantValue())
