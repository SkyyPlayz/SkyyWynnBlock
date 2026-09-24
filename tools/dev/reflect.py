import jpype, sys
JVM=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\jre\latest\bin\server\jvm.dll"
SRV=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Server\HytaleServer.jar"
jpype.startJVM(JVM, classpath=[SRV], convertStrings=True)
Class=jpype.JClass("java.lang.Class"); Mod=jpype.JClass("java.lang.reflect.Modifier")
for name in sys.argv[1:]:
    try: c=Class.forName(name, False, jpype.JClass("java.lang.ClassLoader").getSystemClassLoader())
    except Exception as e: print("!!", name, e); continue
    print("==", name, "extends", c.getSuperclass().getName() if c.getSuperclass() else None, "impl", [i.getName() for i in c.getInterfaces()])
    for m in c.getDeclaredMethods():
        if Mod.isPublic(m.getModifiers()) or Mod.isProtected(m.getModifiers()):
            print("  ", "static " if Mod.isStatic(m.getModifiers()) else "", m.getReturnType().getSimpleName(), m.getName(), "(", ", ".join(p.getSimpleName() for p in m.getParameterTypes()), ")")
    for f in c.getDeclaredFields():
        if Mod.isPublic(f.getModifiers()): print("   F", f.getType().getSimpleName(), f.getName())
    for k in c.getDeclaredConstructors():
        print("   C(", ", ".join(p.getSimpleName() for p in k.getParameterTypes()), ")")
