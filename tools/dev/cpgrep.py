import zipfile, sys
sys.path.insert(0, ".")
from cpstrings import read_utf8_constants
JAR = r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Server\HytaleServer.jar"
needles = sys.argv[1:]
with zipfile.ZipFile(JAR) as z:
    for n in z.namelist():
        if not n.endswith(".class") or not n.startswith("com/hypixel"): continue
        try: strs = read_utf8_constants(z.read(n))
        except Exception: continue
        for nd in needles:
            hit = [s for s in strs if nd in s]
            if hit: print(n, nd, hit[:4])
