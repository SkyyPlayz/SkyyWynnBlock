import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
for cn in sys.argv[1:]:
    cc = pool.get(cn)
    for mm in cc.getDeclaredMethods():
        print(cn, mm.getName(), mm.getSignature())
