"""Append answer lines to the 'Q&A with Skyy 2026-10-02' block in OPEN-QUESTIONS.md (creates the block once).
Usage: python qa_append.py <file with lines to append>"""
import sys
p = r"C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\OPEN-QUESTIONS.md"
s = open(p, "rb").read().decode("utf-8")
HEAD = "## Q&A with Skyy 2026-10-02 (all open questions, round by round - newest answers win)\n"
add = open(sys.argv[1], "rb").read().decode("utf-8").strip("\n") + "\n"
if HEAD not in s:
    anchor = "## Numbers picked in the beta round (live now)\n"
    assert s.count(anchor) == 1
    s = s.replace(anchor, HEAD + "\n" + add + "\n" + anchor)
else:
    i = s.index(HEAD)
    j = s.index("\n## ", i + len(HEAD))
    block = s[i:j].rstrip("\n") + "\n" + add
    s = s[:i] + block + s[j:]
open(p, "wb").write(s.encode("utf-8"))
print("ok")
