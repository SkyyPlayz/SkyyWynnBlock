import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import skyybuild as B
J = B.start(); pool = J["pool"]
cls = sys.argv[1]
cc = pool.get(cls)
for f in cc.getDeclaredFields():
    try:
        cv = f.getConstantValue()
    except Exception:
        cv = None
    print(f.getName(), f.getType().getName(), "=", cv)
