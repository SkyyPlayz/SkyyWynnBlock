"""tools/chat_tail.py - read the in-game chat Skyy saw, from the server log (READ ONLY), so Skyy doesn't need chat screenshots.

SkyyEssentials 0.1.9+ mirrors every chat / system line the server sends a player into the server log as
"[Chat] to <name>: <text>" (Server Setup -> Essentials -> Chat log). This prints those lines from the newest server log of the test world.

Usage:  python tools/chat_tail.py [-n 40] [--grep word] [--all-logs] [--world "HUD mod"]
  -n N        last N chat lines (default 40)
  --grep W    only lines containing W (case-insensitive), e.g. --grep error / --grep Requip
  --all-logs  search every server log of the world (newest last), not just the newest
Times are the log's own (UTC). Logs are only read - the post-session log clean-up moves old ones to the Recycle Bin.
"""
import glob
import os
import re
import sys

LINE = re.compile(r"^\[(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d)[^\]]*\].*?\[Chat\] (.*)$")


def main(argv):
    n, grep, every, world = 40, None, False, "HUD mod"
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "-n":
            n = int(argv[i + 1]); i += 2; continue
        if a == "--grep":
            grep = argv[i + 1].lower(); i += 2; continue
        if a == "--all-logs":
            every = True; i += 1; continue
        if a == "--world":
            world = argv[i + 1]; i += 2; continue
        print(__doc__); return 1
    logs = sorted(glob.glob(os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", world, "logs", "*_server.log")),
                  key=os.path.getmtime)
    if not logs:
        print("no server logs for world", world); return 1
    out = []
    for p in (logs if every else logs[-1:]):
        for raw in open(p, encoding="utf-8", errors="replace"):
            m = LINE.match(raw.rstrip("\n"))
            if m and (grep is None or grep in m.group(2).lower()):
                out.append("%s  %s" % (m.group(1)[11:], m.group(2)))
    print("log:", os.path.basename(logs[-1]), "| %d chat lines%s" % (len(out), " matching " + grep if grep else ""))
    print("\n".join(out[-n:]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
