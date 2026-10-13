"""tools/chat_digest.py - after every play test: Jev sifts the session's in-game chat and returns a short problem list (READ ONLY).

Skyy 2026-10-12: "use JEV to sift through chat after every play test." The chat comes from the SkyyEssentials chat mirror in the server
log (tools/chat_tail.py). Lines are cleaned before sending: the "to <player>:" prefix and the player's names are removed (llm.redact),
repeats are folded into "(xN)". The answer is saved to tools/dev/scratch/chat/<log name>.md and printed; Claude reads only that.

Usage:  python tools/chat_digest.py [--log <server log path>] [--world "HUD mod"] [--model typesafe/jev-router]
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE = re.compile(r"^\[\d{4}/\d\d/\d\d (\d\d:\d\d:\d\d)[^\]]*\].*?\[Chat\] to [^:]{1,40}: (.*)$")
PROMPT = """You are checking the in-game chat log of a play-test session of SkyWynn, a Hytale RPG modpack (classes, skills with XP,
gear rarities, Mana, pets, collections). Every line is a message the server sent the player, with its time (UTC) and (xN) for repeats.
Report, as short bullet lists with the times:
1. ERRORS / FAILURES: any error, "failed", "cannot", "unknown command", missing-permission or exception-like text.
2. SUSPICIOUS: the same reward / XP / message given twice at once, numbers that go backwards, XP bars that pass their max without a
   level-up, messages with raw ids or placeholders (e.g. {0}, null, Weapon_..., ui.text...), spam (one message many times a minute).
3. WHAT THE PLAYER DID: a 5-10 line timeline (levels gained, items found, deaths, commands used).
4. TOP 5 things the developer should look at, worst first.
Be factual; quote the exact text; say "none" for an empty section."""


def lines_of(path):
    out, last, count = [], None, 0
    for raw in open(path, encoding="utf-8", errors="replace"):
        m = LINE.match(raw.rstrip("\n"))
        if not m:
            continue
        text = m.group(2)
        if text == last:
            count += 1
            continue
        if last is not None:
            out.append(last_line + (" (x%d)" % count if count > 1 else ""))
        last, count, last_line = text, 1, "%s %s" % (m.group(1), text)
    if last is not None:
        out.append(last_line + (" (x%d)" % count if count > 1 else ""))
    return out


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    world, log, model = "HUD mod", None, llm.FALLBACK_MODEL  # Jev router
    i = 0
    while i < len(argv):
        if argv[i] == "--log":
            log = argv[i + 1]; i += 2; continue
        if argv[i] == "--world":
            world = argv[i + 1]; i += 2; continue
        if argv[i] == "--model":
            model = argv[i + 1]; i += 2; continue
        print(__doc__); return 1
    if not log:
        logs = sorted(glob.glob(os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", world, "logs",
                                             "*_server.log")), key=os.path.getmtime)
        if not logs:
            print("no server logs"); return 1
        log = logs[-1]
    ls = lines_of(log)
    if not ls:
        print("no chat lines in", os.path.basename(log)); return 0
    body = llm.redact("\n".join(ls))
    ans, used, u = llm.ask(PROMPT + "\n\nCHAT (%d lines):\n%s" % (len(ls), body), model=model, do_redact=False)
    d = os.path.join(ROOT, "tools", "dev", "scratch", "chat")
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, os.path.splitext(os.path.basename(log))[0] + ".md")
    open(out, "w", encoding="utf-8").write("# Chat digest - %s (%d lines, %s)\n\n%s\n" % (os.path.basename(log), len(ls), used, ans))
    print(ans)
    print("\n[saved %s; model %s, tokens %s]" % (os.path.relpath(out, ROOT), used, u.get("total_tokens")), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
