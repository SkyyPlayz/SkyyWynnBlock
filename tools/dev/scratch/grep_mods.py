import zipfile, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, r"C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\tools\dev")
from cpstrings import read_utf8_constants

MODS = r"C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Mods"
needles = sys.argv[1:]

for fn in sorted(os.listdir(MODS)):
    path = os.path.join(MODS, fn)
    if not fn.lower().endswith((".jar", ".zip")):
        continue
    try:
        z = zipfile.ZipFile(path)
    except Exception:
        continue
    with z:
        for n in z.namelist():
            if not n.endswith(".class"):
                continue
            try:
                data = z.read(n)
                strs = read_utf8_constants(data)
            except Exception:
                continue
            for nd in needles:
                hit = [s for s in strs if nd in s]
                if hit:
                    print(fn, "|", n, "|", nd, "|", hit[:6])
