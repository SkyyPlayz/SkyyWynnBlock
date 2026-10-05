"""Record Skyy's answers (2026-10-05 layout): append answer lines to docs/answered/<topic>.md and, with --close, delete the answered
question from OPEN-QUESTIONS.md - so OPEN-QUESTIONS.md only ever holds questions that are still open (Skyy's rule).

Usage:  python tools/qa_append.py <topic> <file with the answer lines> [--close "<words that appear in the open question>"]
  topic = a file name in docs/answered/ without .md (classes, gear, skills, mobs, world, economy, bags, ui, social, pets, project)
  --close may be given more than once; each must match exactly ONE question line in OPEN-QUESTIONS.md (its wrapped lines go with it).
Nothing is written unless every step succeeds. Line endings and bytes of both files are kept."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPEN = os.path.join(ROOT, "OPEN-QUESTIONS.md")


def fail(msg):
    print("NOT WRITTEN: " + msg)
    sys.exit(1)


def main(argv):
    if len(argv) < 3 or argv[1].startswith("-"):
        fail(__doc__)
    topic, src = argv[1], argv[2]
    closes, i = [], 3
    while i < len(argv):
        if argv[i] != "--close" or i + 1 >= len(argv):
            fail("unknown argument %r" % argv[i])
        closes.append(argv[i + 1])
        i += 2
    ans = os.path.join(ROOT, "docs", "answered", topic + ".md")
    if not os.path.exists(ans):
        fail("no topic file %s (topics: %s)" % (ans, ", ".join(sorted(f[:-3] for f in os.listdir(os.path.dirname(ans))
                                                                         if f.endswith(".md") and f != "README.md"))))
    add = open(src, "rb").read().decode("utf-8").strip("\r\n")
    if not add.strip():
        fail("the answer file is empty")
    a = open(ans, "rb").read().decode("utf-8")
    if "## New answers" not in a:
        fail("%s has no '## New answers' block" % ans)
    nl = "\r\n" if a.endswith("\r\n") else "\n"
    a = a.rstrip("\r\n") + nl + add.replace("\r\n", "\n").replace("\n", nl) + nl  # the New answers block is the file's last block

    o = open(OPEN, "rb").read().decode("utf-8")
    lines = o.split("\n")
    for words in closes:
        hits = [k for k, l in enumerate(lines) if l.startswith("- ") and words in l]
        if len(hits) != 1:
            fail("--close %r matches %d question lines in OPEN-QUESTIONS.md (needs exactly 1)" % (words, len(hits)))
        k = hits[0]
        end = k + 1
        while end < len(lines) and lines[end].startswith("  "):
            end += 1  # wrapped lines of the same question
        del lines[k:end]
    open(ans, "wb").write(a.encode("utf-8"))
    if closes:
        open(OPEN, "wb").write("\n".join(lines).encode("utf-8"))
    print("ok: %d line(s) added to docs/answered/%s.md, %d question(s) closed" % (add.count("\n") + 1, topic, len(closes)))


if __name__ == "__main__":
    main(sys.argv)
