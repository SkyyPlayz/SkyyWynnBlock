import jpype, sys
JVM=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\jre\latest\bin\server\jvm.dll"
SRV=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Server\HytaleServer.jar"
jarpath = sys.argv[1]
names = sys.argv[2:]
jpype.startJVM(JVM, classpath=[SRV, jarpath], convertStrings=True)
Class=jpype.JClass("java.lang.Class"); Mod=jpype.JClass("java.lang.reflect.Modifier")
CL = jpype.JClass("java.lang.ClassLoader").getSystemClassLoader()
for name in names:
    try: c=Class.forName(name, False, CL)
    except Exception as e: print("!!", name, type(e).__name__, e); continue
    print("==", name, "extends", c.getSuperclass().getName() if c.getSuperclass() else None, "impl", [i.getName() for i in c.getInterfaces()])
    for m in c.getDeclaredMethods():
        mod = m.getModifiers()
        print("  ", "static " if Mod.isStatic(mod) else "", ("public" if Mod.isPublic(mod) else "protected" if Mod.isProtected(mod) else "private" if Mod.isPrivate(mod) else "pkg"), m.getReturnType().getSimpleName(), m.getName(), "(", ", ".join(p.getSimpleName() for p in m.getParameterTypes()), ")")
    for f in c.getDeclaredFields():
        mod = f.getModifiers()
        print("   F", "static " if Mod.isStatic(mod) else "", ("public" if Mod.isPublic(mod) else "protected" if Mod.isProtected(mod) else "private" if Mod.isPrivate(mod) else "pkg"), f.getType().getSimpleName(), f.getName())
    for k in c.getDeclaredConstructors():
        print("   C(", ", ".join(p.getSimpleName() for p in k.getParameterTypes()), ")")
