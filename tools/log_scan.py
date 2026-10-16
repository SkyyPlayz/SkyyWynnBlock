r"""tools/log_scan.py - summarise Skyy's newest game logs (server + client) in a few lines, then (optionally) recycle the old ones.

Skyy 2026-10-16: "remeber to build skills for the things you do repeatedly to save tokens and speed things up." + "use jev when you can".
Replaces the hand-run grep / uniq the main session did after every play session (memory: skywynn-check-logs).

Run:  python tools/log_scan.py                 newest server log of the deploy world + newest client log, grouped WARN/SEVERE counts
      python tools/log_scan.py --ours          only lines from our mods ([Skyy...]) and asset errors naming Skyy_ ids
      python tools/log_scan.py --recycle       also move every older *.log (all but the newest of each folder) to the Recycle Bin
Read-only on the logs (PROJECT-RULES 1); --recycle uses the Windows Recycle Bin, never a hard delete.
Vanilla NPC animation noise ("Animation X does not exist for model Y") is dropped. Numbers are folded to # so repeats group.
"""
import os
import re
import sys
import collections

USERDATA = r"C:\Users\SkyLo\AppData\Roaming\Hytale\UserData"


def world():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import deploy_set
        return deploy_set.WORLD
    except Exception:
        return "NewBetaTest"


def newest(d):
    fs = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".log")] if os.path.isdir(d) else []
    fs.sort(key=os.path.getmtime, reverse=True)
    return fs


NOISE = re.compile(r"Animation \S+ does not exist for model|pre-semver YYYY|Skipping pack at Skyy_")   # Skipping pack = our data folders, not packs
HIT = re.compile(r"SEVERE|ERROR|WARN|Exception|Caused by")


def summary(path, ours, top=25):
    c = collections.Counter()
    for line in open(path, encoding="utf-8", errors="replace"):
        if not HIT.search(line) or NOISE.search(line):
            continue
        if ours and not re.search(r"\[Skyy|Skyy_", line):
            continue
        key = re.sub(r"^.*?\|", "", line.strip(), count=1) if "|" in line[:60] else line.strip()
        key = re.sub(r"\d+", "#", re.sub(r"^\[[^\]]*\]\s*", "", key))[:200]
        c[key] += 1
    print("== %s (%d kinds)" % (os.path.basename(path), len(c)))
    for k, n in c.most_common(top):
        print("%5d  %s" % (n, k))


def recycle(paths):
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", wintypes.LPCWSTR), ("pTo", wintypes.LPCWSTR),
                    ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", wintypes.BOOL), ("hNameMappings", ctypes.c_void_p),
                    ("lpszProgressTitle", wintypes.LPCWSTR)]
    n = 0
    for p in paths:
        op = SHFILEOPSTRUCTW(None, 3, p + "\0\0", None, 0x0040 | 0x0010 | 0x0004 | 0x0400, False, None, None)  # DELETE, ALLOWUNDO|NOCONFIRM|SILENT|NOERRORUI
        if ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op)) == 0:
            n += 1
    print("recycled %d old log(s)" % n)


def main():
    ours = "--ours" in sys.argv
    sdir = os.path.join(USERDATA, "Saves", world(), "logs")
    cdir = os.path.join(USERDATA, "Logs")
    old = []
    for d in (sdir, cdir):
        fs = newest(d)
        if not fs:
            print("no logs in", d)
            continue
        summary(fs[0], ours)
        old += fs[1:]
    if "--recycle" in sys.argv:
        recycle(old)
    elif old:
        print("(%d older log(s) left; --recycle moves them to the Recycle Bin)" % len(old))


if __name__ == "__main__":
    main()
