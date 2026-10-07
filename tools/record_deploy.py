"""Record a finished deploy in every doc at once (PROJECT-RULES 3 step 5 + 5 "always ready to hand off").

Run AFTER `python tools/deploy_set.py --yes`. It writes, keeping each file's line endings:
  docs/tests/<YYYY-MM>.md   a "## <title> (DEPLOYED <date> <time>, backup <backup>)" section with your numbered steps
  docs/tests/README.md      one index row
  HANDOFF.md                the version column (+ a short note) of every mod you name
  TEST-CHECKLIST.md         the next numbered "Test next" line, after the highest number
  docs/log/<YYYY-MM>.md     one log line
Date, time and backup come from the NEWEST backups/deploy-<date>-<time>/ folder (made by tools/backup_deploy.py), so they
are never guessed. Nothing is written unless every step succeeds (all files are prepared first, then written).

Usage:
  python tools/record_deploy.py --title "SkyyBank 0.1.7 (daily interest)" --mod SkyyBank:0.1.6:0.1.7:"interest once a day" \
      --steps steps.txt --checklist "SkyyBank 0.1.7 - interest once a day" --log "full round, ...; cross-check READY"
  --mod MOD:OLD:NEW[:note]   repeat per mod (HANDOFF row 'MOD | OLD |' becomes 'MOD | NEW |', note appended)
  --steps FILE               numbered test steps (plain lines; '1.' numbering added if missing)
  --checklist TEXT           text of the TEST-CHECKLIST line (number added)
  --log TEXT                 text after 'DEPLOYED <mods>' in the log line
  --dry-run                  print what would change, write nothing
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def rd(p):
    b = open(os.path.join(ROOT, p), "rb").read().decode("utf-8")
    return b, ("\r\n" if "\r\n" in b else "\n")


def newest_backup():
    d = os.path.join(ROOT, "backups")
    names = sorted(n for n in os.listdir(d) if re.match(r"^deploy-\d{8}-\d{4}$", n))
    if not names:
        sys.exit("NOT WRITTEN: no backups/deploy-<date>-<time>/ folder - run tools/backup_deploy.py + deploy_set.py --yes first")
    n = names[-1]
    m = re.match(r"deploy-(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})", n)
    return n, "%s-%s-%s" % m.group(1, 2, 3), "%s:%s" % m.group(4, 5), "%s-%s" % m.group(1, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--mod", action="append", default=[])
    ap.add_argument("--steps", required=True)
    ap.add_argument("--checklist", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    backup, date, time, month = newest_backup()
    out = {}

    # 1. test section
    tp = "docs/tests/%s.md" % month
    s, nl = rd(tp)
    raw = [l.rstrip() for l in open(a.steps, encoding="utf-8").read().splitlines() if l.strip()]
    steps, k = [], 0
    for l in raw:
        if re.match(r"^\d+\.\s", l) or l.startswith((" ", "\t")) or l.endswith(":"):
            steps.append(l)
        else:
            k += 1
            steps.append("%d. %s" % (k, l))
    sec = ["## %s (DEPLOYED %s %s, backup %s)" % (a.title, date, time, backup)] + steps
    out[tp] = s.rstrip("\r\n") + nl + nl.join(sec) + nl

    # 2. tests index
    ip = "docs/tests/README.md"
    s, nl = rd(ip)
    out[ip] = s.rstrip("\r\n") + nl + "| %s (DEPLOYED %s, backup %s) | [%s](%s.md) |" % (a.title, date, backup, month, month) + nl

    # 3. HANDOFF versions
    hp = "HANDOFF.md"
    s, nl = rd(hp)
    mods = []
    for spec in a.mod:
        parts = spec.split(":", 3)
        if len(parts) < 3:
            sys.exit("NOT WRITTEN: --mod needs MOD:OLD:NEW[:note], got %r" % spec)
        mod, old, new = parts[:3]
        note = parts[3] if len(parts) > 3 else ""
        pat = r"^\| %s \| %s \|([^\n]*?)\s*\|(\r?)$" % (re.escape(mod), re.escape(old))
        s, n = re.subn(pat, lambda m: "| %s | %s |%s%s |%s" % (mod, new, m.group(1).rstrip(), ("; " + note) if note else "", m.group(2)),
                       s, 1, flags=re.M)
        if n != 1:
            sys.exit("NOT WRITTEN: HANDOFF.md has no row '| %s | %s |' (already updated? wrong old version?)" % (mod, old))
        mods.append("%s %s" % (mod, new))
    out[hp] = s

    # 4. checklist: next number after the highest "N. " line in the Test next list
    cp = "TEST-CHECKLIST.md"
    s, nl = rd(cp)
    lines = s.split(nl)
    nums = [(int(m.group(1)), i) for i, l in enumerate(lines) for m in [re.match(r"^(\d+)\. ", l)] if m]
    if not nums:
        sys.exit("NOT WRITTEN: no numbered lines in TEST-CHECKLIST.md")
    top, at = max(nums)
    lines.insert(at + 1, "%d. %s" % (top + 1, a.checklist))
    out[cp] = nl.join(lines)
    num = top + 1

    # 5. log line
    lp = "docs/log/%s.md" % month
    s, nl = rd(lp)
    tz = "-0600"
    line = "- %s %s %s: DEPLOYED %s (%s). Backup %s; TEST-CHECKLIST %d." % (date, time, tz, " + ".join(mods) or a.title, a.log, backup, num)
    out[lp] = s.rstrip("\r\n") + nl + line + nl

    for p, txt in out.items():
        if a.dry_run:
            print("would write", p)
        else:
            open(os.path.join(ROOT, p), "wb").write(txt.encode("utf-8"))
    print(("DRY RUN - " if a.dry_run else "") + "recorded: %s, %s %s, backup %s, TEST-CHECKLIST %d (%d files)" % (a.title, date, time, backup, num, len(out)))


if __name__ == "__main__":
    main()
