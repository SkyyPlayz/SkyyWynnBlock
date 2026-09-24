import zipfile, sys
JAR = r"C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Mods\DynamicTooltipsLib-1.6.2.jar"
with zipfile.ZipFile(JAR) as z:
    names = [n for n in z.namelist() if n.endswith(".class")]
    for n in sorted(names):
        print(n)
    print("---TOTAL---", len(names))
