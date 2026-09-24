import jpype
JVM=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\jre\latest\bin\server\jvm.dll"
SRV=r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Server\HytaleServer.jar"
jpype.startJVM(JVM, classpath=[SRV], convertStrings=True)
from jpype import JClass
EP = JClass("com.hypixel.hytale.event.EventPriority")
for name in ["FIRST","EARLY","NORMAL","LATE","LAST"]:
    v = getattr(EP, name)
    print(name, v.getValue())
