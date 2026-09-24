import zipfile, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cpstrings import read_utf8_constants

jarpath = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else ""
with zipfile.ZipFile(jarpath) as z:
    for n in z.namelist():
        if not n.endswith(".class"):
            continue
        if prefix and not n.startswith(prefix):
            continue
        try:
            strs = read_utf8_constants(z.read(n))
        except Exception as e:
            print("!!", n, e)
            continue
        print("=====", n, "(", len(strs), "constants )")
        for s in strs:
            # only print things that look meaningful: method/field names, descriptors with class refs, or literal-ish strings
            if len(s) > 1:
                print(" ", s)
