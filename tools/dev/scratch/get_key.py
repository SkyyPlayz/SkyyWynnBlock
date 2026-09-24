import jpype
JVM=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\jre\latest\bin\server\jvm.dll"
SRV=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Server\HytaleServer.jar"
jpype.startJVM(JVM, classpath=[SRV], convertStrings=True)
C = jpype.JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata")
f = C.class_.getDeclaredField("KEY")
f.setAccessible(True)
print("KEY =", f.get(None))
Msg = jpype.JClass("com.hypixel.hytale.server.core.Message")
for m in Msg.class_.getDeclaredMethods():
    print(m)
