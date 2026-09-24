"""Deploy the whole SkyWynn test set to the "HUD mod" world in one step - ONLY after Skyy says "deploy".

Usage (game closed):   python tools/deploy_set.py            -> shows the plan, asks for "yes"
                       python tools/deploy_set.py --yes      -> no question (Skyy already said deploy)
                       python tools/deploy_set.py --check    -> only checks that every jar exists

It does exactly what each build script's --deploy block does (B.deploy + B.enable_in_world with disable_prefix="Skyy:"), for every mod
in SET, using the jars that are ALREADY BUILT (it never rebuilds). It refuses to run while a Hytale server (HytaleServer.jar java
process) is running, because replacing a mod jar under a running server can break it. Mods not in SET are left alone.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skyybuild as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD = "HUD mod"
# (mod, version) - keep in sync with HANDOFF section 3 "Versions"
SET = [
    ("SkyyHud", "0.3.6"), ("SkyySacks", "0.7.3"), ("SkyyCoins", "0.1.5"), ("SkyyCollections", "0.2"), ("SkyyParty", "0.1.2"),
    ("SkyyBank", "0.1.2"), ("SkyyIslands", "0.4.4"), ("SkyyBazaar", "0.1.1"), ("SkyyRolls", "0.1.2"), ("SkyySkills", "0.4"),
    ("SkyyAccessories", "0.4.2"), ("SkyyClasses", "0.1.4"), ("SkyyMenu", "0.1.2"), ("SkyyEssentials", "0.1"), ("SkyyProfiles", "0.1"),
    ("SkyyCooking", "0.1"), ("SkyyTrees", "0.1"),
]
# third-party mods that are part of the pack (enabled in the world by their manifest key; their files are NOT in this repo -
# a server owner installs them from their authors, see PACK.md). Never disabled by this script.
PACK_THIRD_PARTY = ["Serj:More Crossbow Tiers", "Helios:Saplings From Trees"]


def server_running():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              # java.exe only: the query's own powershell command line contains the search text and would match itself
                              "Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object { $_.CommandLine -like '*HytaleServer*' } | Measure-Object | Select-Object -ExpandProperty Count"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return out not in ("", "0")
    except Exception as e:
        print("could not check for a running server:", e)
        return True


def newer_builds(mod, ver):
    """Versions of <mod>-<version>.jar on disk that are HIGHER than the pinned one. A note only: SET decides what deploys (a newer jar
    can be an unreviewed build), but it makes a forgotten SET bump visible instead of silently redeploying the old set."""
    import re
    def v(s):
        return tuple(int(x) for x in s.split("."))
    d = os.path.join(ROOT, mod)
    if not os.path.isdir(d):
        return []
    out = []
    for n in os.listdir(d):
        m = re.match(r"^%s-(\d+(?:\.\d+)*)\.jar$" % re.escape(mod), n)
        if m and v(m.group(1)) > v(ver):
            out.append(m.group(1))
    return sorted(out, key=v)


def main():
    missing = []
    plan = []
    for mod, ver in SET:
        jar = os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver))
        if not os.path.isfile(jar):
            missing.append(jar)
        plan.append((mod, ver, jar))
    for mod, ver, jar in plan:
        print("  %-16s %-6s %s" % (mod, ver, "OK" if os.path.isfile(jar) else "MISSING " + jar))
    newer = [(mod, ver, newer_builds(mod, ver)) for mod, ver in SET]
    newer = [x for x in newer if x[2]]
    if newer:
        print("NOTE: newer builds are on disk than SET pins (SET decides what deploys - bump it, and HANDOFF section 3, only for the "
              "builds Skyy approved):")
        for mod, ver, vs in newer:
            print("  %-16s pinned %-6s newer on disk: %s" % (mod, ver, ", ".join(vs)))
    if missing:
        print("STOP: %d jar(s) missing - build them first (python <build script>, no --deploy)." % len(missing))
        return 1
    if "--check" in sys.argv:
        print("all %d jars present" % len(plan))
        return 0
    if server_running():
        print("STOP: a Hytale server is running. Close the world / game first, then run this again.")
        return 1
    if "--yes" not in sys.argv:
        if input("Deploy these %d mods to world '%s'? type yes: " % (len(plan), WORLD)).strip().lower() != "yes":
            print("cancelled")
            return 1
    for mod, ver, jar in plan:
        B.deploy(jar, mod + ".jar")
        B.enable_in_world(WORLD, "Skyy:%s %s" % (ver, mod), disable_prefix="Skyy:")
    for key in PACK_THIRD_PARTY:
        B.enable_in_world(WORLD, key)
    print("deployed %d mods. Start the world and watch the server log for every '[Skyy...] ready' line." % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
