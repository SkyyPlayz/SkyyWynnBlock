"""Back up Skyy jars + world config.json + Skyy_* world data into backups/deploy-<stamp>/ (reads UserData only)."""
import os, shutil, sys, time, subprocess
PROJECT = r"C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT"
USERDATA = r"C:\Users\SkyLo\AppData\Roaming\Hytale\UserData"
WORLD = os.path.join(USERDATA, "Saves", "HUD mod")

out = subprocess.run(["powershell", "-NoProfile", "-Command",
                      "Get-CimInstance Win32_Process -Filter \"Name like 'java%'\" | Select-Object -ExpandProperty CommandLine"],
                     capture_output=True, text=True).stdout
if "HytaleServer" in out:
    sys.exit("HytaleServer is running - not deploying")

stamp = time.strftime("%Y%m%d-%H%M")
dst = os.path.join(PROJECT, "backups", "deploy-" + stamp)
_n = 2
while os.path.exists(dst):  # two deploys in one minute: never reuse (or fail on) an existing backup folder
    dst = os.path.join(PROJECT, "backups", "deploy-%s-%d" % (stamp, _n)); _n += 1
os.makedirs(os.path.join(dst, "Mods"))
n = 0
for f in os.listdir(os.path.join(USERDATA, "Mods")):
    if f.startswith("Skyy") and f.endswith(".jar"):
        shutil.copy2(os.path.join(USERDATA, "Mods", f), os.path.join(dst, "Mods", f)); n += 1
shutil.copy2(os.path.join(WORLD, "config.json"), os.path.join(dst, "config.json"))
d = 0
for f in os.listdir(os.path.join(WORLD, "mods")):
    if f.startswith("Skyy"):
        shutil.copytree(os.path.join(WORLD, "mods", f), os.path.join(dst, "data", f)); d += 1
print("backup", dst, "jars", n, "data folders", d)
