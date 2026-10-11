"""tools/llm.py - send cheap SIDE JOBS (log scans, mod surveys, asset digging, bulk text) to OpenRouter, off the Claude budget.

Skyy 2026-10-11: "id like to add open router, because of JEV ... making sure each request is routed to the right model, and sifting
through tonsss of data in seconds for cheap." Builds and reviews stay on Claude; this is only for bulk reading / drafting.

KEY: never in this repo (it is public). Read from Windows Credential Manager first:
    pip install keyring
    python -m keyring set openrouter api_key        (paste the key at the hidden prompt)
else from the user environment variable OPENROUTER_API_KEY. The key is never printed or logged.

Usage:
    python tools/llm.py "question" [--file F ...] [--model typesafe/jev-router] [--max-chars 400000] [--out answer.md] [--no-redact]
    python tools/llm.py --check                       (key found? one tiny request, prints the model that answered)
From Python: import llm; text = llm.ask("question", files=[...])

REDACTION (default on): before sending, file text is cleaned - player names from UserData (Skyy's account names), UUIDs, chat lines
("[Chat]" / "to <player>:"), e-mail addresses and Windows user paths are replaced with placeholders. Game files (Assets.zip,
HytaleServer.jar) are never read by this tool.
"""
import json
import os
import re
import sys
import urllib.request

API = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "typesafe/jev-router"
NAMES = ["SkyLordPlayz", "SkyLo", "Skyy_"]          # account / folder names that appear in logs (Skyy_ = our mod prefix, kept below)
UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
MAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
USERPATH = re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I)
CHAT = re.compile(r"(\[Chat\][^\n]*|\bto [A-Za-z0-9_]{3,16}:[^\n]*)")


def key():
    try:
        import keyring
        k = keyring.get_password("openrouter", "api_key")
        if k:
            return k.strip()
    except Exception:
        pass
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not k:
        sys.exit("No OpenRouter key: run  python -m keyring set openrouter api_key  (or set OPENROUTER_API_KEY), then restart the app.")
    return k


def redact(text):
    text = USERPATH.sub(r"C:\\Users\\<user>", text)
    text = UUID.sub("<uuid>", text)
    text = MAIL.sub("<email>", text)
    text = CHAT.sub("<chat line removed>", text)
    for n in NAMES:
        if n == "Skyy_":
            continue
        text = re.sub(re.escape(n), "<player>", text, flags=re.I)
    return text


def ask(question, files=(), model=DEFAULT_MODEL, max_chars=400000, do_redact=True, system=None):
    parts = []
    for f in files:
        low = f.replace("/", "\\").lower()
        if low.endswith(("assets.zip", "hytaleserver.jar")):
            raise SystemExit("Refused: game files are never sent (%s)" % f)
        with open(f, encoding="utf-8", errors="replace") as h:
            t = h.read()
        parts.append("=== FILE %s ===\n%s" % (os.path.basename(f), redact(t) if do_redact else t))
    body = "\n\n".join(parts)
    if len(body) > max_chars:
        body = body[:max_chars] + "\n[... cut at %d characters ...]" % max_chars
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": (question + ("\n\n" + body if body else ""))})
    req = urllib.request.Request(API, data=json.dumps({"model": model, "messages": msgs}).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + key(), "Content-Type": "application/json",
                                          "X-Title": "SkyWynn tools/llm.py"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit("OpenRouter HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:500]))
    ans = d["choices"][0]["message"]["content"]
    used = d.get("model", model)
    u = d.get("usage") or {}
    return ans, used, u


def main(argv):
    if "--check" in argv:
        ans, used, u = ask("Reply with the single word OK.")
        print("key found; model %s answered: %s (tokens %s)" % (used, ans.strip()[:40], u.get("total_tokens")))
        return 0
    files, model, out, maxc, red, q = [], DEFAULT_MODEL, None, 400000, True, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--file":
            files.append(argv[i + 1]); i += 2; continue
        if a == "--model":
            model = argv[i + 1]; i += 2; continue
        if a == "--out":
            out = argv[i + 1]; i += 2; continue
        if a == "--max-chars":
            maxc = int(argv[i + 1]); i += 2; continue
        if a == "--no-redact":
            red = False; i += 1; continue
        q.append(a); i += 1
    if not q:
        print(__doc__); return 1
    ans, used, u = ask(" ".join(q), files, model, maxc, red)
    if out:
        with open(out, "w", encoding="utf-8") as h:
            h.write(ans)
    print(ans)
    print("\n[model %s, tokens %s]" % (used, u.get("total_tokens")), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
