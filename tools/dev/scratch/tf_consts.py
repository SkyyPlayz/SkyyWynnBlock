import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
for cn in sys.argv[1:]:
    cc = pool.get(cn)
    for f in cc.getDeclaredFields():
        try: cv = f.getConstantValue()
        except Exception: cv = None
        if cv is not None: print(cn, f.getName(), "=", cv)
