import sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import skyybuild as B, zipfile
J = B.start(); pool = J["pool"]
from jpype import JClass
IP = JClass("javassist.bytecode.InstructionPrinter"); PS = JClass("java.io.PrintStream"); BOS = JClass("java.io.ByteArrayOutputStream")
# usage: callers.py <pkgprefix> needle1 needle2 ...
prefix = sys.argv[1]; needles = sys.argv[2:]
with zipfile.ZipFile(B.SERVER_JAR) as z:
    names = [n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class") and n.startswith(prefix)]
for cn in names:
    try: cc = pool.get(cn)
    except Exception: continue
    try: ms = list(cc.getDeclaredMethods()) + list(cc.getDeclaredConstructors())
    except Exception: continue
    for mm in ms:
        bos = BOS(); ip = IP(PS(bos))
        try: ip.print_(mm)
        except Exception: continue
        s = str(bos.toString())
        for l in s.splitlines():
            for nd in needles:
                if nd in l and "invoke" in l:
                    print(cn, mm.getName(), "|", l.strip())
