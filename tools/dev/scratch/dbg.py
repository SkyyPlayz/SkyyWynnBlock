import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
spec = sys.argv[1]
parts = spec.split("#")
cls, m = parts[0], parts[1]
sig = parts[2] if len(parts) > 2 else None
print("cls=", repr(cls), "m=", repr(m), "sig=", repr(sig))
cc = pool.get(cls)
print("got class", cc.getName())
