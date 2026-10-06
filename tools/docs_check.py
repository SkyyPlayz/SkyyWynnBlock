"""Docs safety check for the 2026-10-05 docs consolidation (and any later docs move).

  python tools/docs_check.py                 # compare against BASE (the last commit before the consolidation)
  python tools/docs_check.py --base <ref>    # compare against another commit

1. NOTHING LOST: every non-blank line of every .md file at BASE must still exist somewhere in the repo's .md files now.
   Lines are compared with whitespace collapsed, so a wrapped bullet that was joined into one line still counts.
   Exit code 1 lists every missing line (file:line at BASE).
2. NO NEW BROKEN PATHS: every repo path a .md file mentions (`research/X.md`, `tools/y.py`, `HANDOFF.md` ...) must exist. Paths that
   were already missing at BASE (planned outputs such as a future patch script) are only counted, never a failure. Files moved by
   the consolidation are listed in MOVES (and in INDEX.md); a line counts as kept when only such a path was updated to the new place.
Needs only git + Python 3 (no game files)."""
import os, re, subprocess, sys

BASE = "a8e1fdfc6011d503b2dd3876457beef5ad6faf3b"  # main on 2026-10-05 06:53 -0600, before the consolidation
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = re.compile(r"\s+")
# files moved by the consolidation: a line still counts as kept when only its path mention was updated to the new place
PLANS = ["SkyWynn-Master-Plan.md", "SkyWynn-Decisions.md", "SkyWynn-Server-Setup-Plan.md", "SkyWynn-QoL-Catalog.md",
         "SkyyAccessories-Plan.md", "SkyyClasses-Plan.md", "SkyyDungeons-Plan.md", "SkyyEconomy-Plan.md", "SkyyExploration-Plan.md",
         "SkyyGuilds-Plan.md", "SkyyHUD-Plan.md", "SkyyIslands-Plan.md", "SkyyMinions-Plan.md", "SkyySacks-Plan.md", "SkyySkills-Plan.md"]
MOVES = dict([(p, "docs/plans/" + p) for p in PLANS] + [(p, "docs/archive/" + p) for p in
             ["DESIGN-STATUS.md", "BETA-TEST.md", "SkyWynn-Mod-Roster.md"]])
# living docs the consolidation REWROTE on purpose (their old lines are in git history at BASE); listed, never a failure
REWRITTEN = {
    "README.md": "public front page refreshed (it said 'Private'; new layout links)",
    "CLAUDE.md": "points at INDEX.md too",
    "PROJECT-RULES.md": "'Where to start' + section 5 describe the new docs layout",
    "CLOUD-RESUME.md": "the 'Docs consolidation map' + 'README draft' tasks are done; paths updated",
    "tools/AGENT-BRIEF.md": "builders' reading list + never-edit list use the new layout",
    "tools/CONFIG-CONTRACT.md": "emit() example: KEEP 20 -> 10 (config History keeps 10 versions, 2026-10-05)",
}
REWRITTEN_DIRS = ("research/classes/",)  # Skyy 2026-10-05: class files refined for easy reading (facts kept - see the PR review)
NO_EDIT = {"SkyyGear-Plan.md", "SkyyGear-Stat-Catalog.md"}  # Skyy's own docs: never edited, so their old names resolve through MOVES
MOVE_RE = re.compile(r"(?<![\w/.-])(%s)" % "|".join(re.escape(k) for k in MOVES))


# citations into OPEN-QUESTIONS.md / HANDOFF.md by LINE that the consolidation re-pointed to the moved text (old -> new, exact)
CITES = [("(OPEN-QUESTIONS.md:50-57)", '(docs/answered/gear.md "REQUEST 2026-10-01 (Skyy): gear levels like Wynncraft")'),
         ("OPEN-QUESTIONS line 402", 'docs/answered/ui.md "REQUEST 2026-10-03 (Skyy): MINIMAP"'),
         ("OPEN-QUESTIONS.md (SkyyGear material levels, mob level request), HANDOFF.md (raids / shards note 2026-09-30)",
          "docs/answered/gear.md (SkyyGear material levels) + docs/answered/mobs.md (mob level request), docs/log/2026-09.md (raids / shards "
          "note 2026-09-30)")]
# paths inside the game's Assets.zip (cited by specs, never repo files) and planned outputs named by specs added after BASE
ASSET_DIRS = ("Server/", "Common/")
PATCH_RE = re.compile(r"^tools/\w+_\d+(?:_\d+)+_patch\.py$")  # a spec naming the patch script a future build will write
TEST_RE = re.compile(r"^Skyy\w+/(?:test|build)_skyy\w+_\d+(?:\.\d+)+\.py$")  # planned harness / build of a future version
PLANNED = {"tools/sacks_0_7_13_patch.py", "tools/skyyacctable.py", "tools/skyyacctable_test.py"}  # research/Accessory-Table-Spec.md (paused)
LINK = re.compile(r"\]\(([^)\s]+)\)")  # a markdown link's target: always a path (or a URL / #anchor)


def moved(s):
    s = MOVE_RE.sub(lambda m: MOVES[m.group(1)], s)
    for a, b in CITES:
        s = s.replace(a, b)
    return s
# a repo path inside a doc: optional folders + a file with a doc / code extension
PATH = re.compile(r"(?<![\w/.\\-])((?:[\w.-]+[/\\])*[\w.-]+\.(?:md|py|js|json|txt|ui))(?![\w/])")


def git(*a):
    return subprocess.check_output(["git", "-C", ROOT] + list(a))


def norm(s):
    return WS.sub(" ", s).strip()


def files_at(ref):
    return [f for f in git("ls-tree", "-r", "--name-only", ref).decode("utf-8").split("\n") if f]


def read_at(ref, f):
    return git("show", "%s:%s" % (ref, f)).decode("utf-8", "replace")


def tracked_now():
    out = git("ls-files", "-co", "--exclude-standard").decode("utf-8").split("\n")
    return [f for f in out if f and os.path.exists(os.path.join(ROOT, f))]


def broken_refs(md_files, exists, read):
    """{(doc, path)} for every mentioned repo path that does not exist (root-relative or relative to the doc)."""
    bad = set()
    for f in md_files:
        d = os.path.dirname(f)
        text = read(f)
        for m in LINK.findall(text):  # every markdown link target, lowercase bare names included
            p = m.split("#")[0].replace("%20", " ")
            if not p or p.startswith(("http:", "https:", "mailto:")):
                continue
            if not (exists(os.path.normpath(os.path.join(d, p)).replace("\\", "/")) or exists(p)):
                bad.add((f, p))
        for m in PATH.findall(text):
            p = m.replace("\\", "/")
            if p.startswith(("http", "www.")) or "/" not in p and not re.match(r"^[A-Z][\w-]*\.md$", p):
                continue  # bare names like foo.py / x.json are usually code words, not repo paths; root .md docs are checked
            if "scratch" in p or "<" in p or "*" in p or p.startswith(ASSET_DIRS) or p in PLANNED or PATCH_RE.match(p) or TEST_RE.match(p) \
                    or (f == "CLOUD-RESUME.md" and p.startswith("research/cloud/")):  # a cloud task's planned output
                continue
            cands = [p, os.path.normpath(os.path.join(d, p)).replace("\\", "/")]
            if (f in NO_EDIT or f == "INDEX.md") and p in MOVES:  # INDEX.md's moved-files table names the old places on purpose
                cands.append(MOVES[p])
            if not any(exists(c) for c in cands):
                bad.add((f, p))
    return bad


def main():
    base = BASE
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1]
    old_files = files_at(base)
    old_md = [f for f in old_files if f.endswith(".md")]
    now = tracked_now()
    now_md = [f for f in now if f.endswith(".md")]
    corpus = " \n ".join(norm(open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()) for f in now_md)

    missing, changed = [], {}
    for f in old_md:
        for i, line in enumerate(read_at(base, f).split("\n"), 1):
            n = norm(line)
            if n and n not in corpus and moved(n) not in corpus:
                if f in REWRITTEN or f.startswith(REWRITTEN_DIRS):
                    changed[f] = changed.get(f, 0) + 1
                else:
                    missing.append("%s:%d: %s" % (f, i, n[:160]))
    print("1. nothing lost: %d .md files at %s checked, %d lines missing" % (len(old_md), base[:8], len(missing)))
    for m in missing[:200]:
        print("   MISSING " + m)
    for f in sorted(changed):
        print("   rewritten on purpose: %s (%d old lines) - %s" % (f, changed[f], REWRITTEN.get(f, "class file refined")))

    old_set, now_set = set(old_files), set(now)
    old_text = {}
    old_dirs = {d for f in old_files for d in (f.rsplit("/", k)[0] for k in range(1, f.count("/") + 1))}
    old_bad = broken_refs(old_md, lambda p: p in old_set or p.rstrip("/") in old_dirs,
                          lambda f: old_text.setdefault(f, read_at(base, f)))
    old_bad_paths = {p for _, p in old_bad}
    now_bad = broken_refs(now_md, lambda p: p in now_set or os.path.exists(os.path.join(ROOT, p)),
                          lambda f: open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read())
    new_bad = sorted((f, p) for f, p in now_bad if p not in old_bad_paths)
    print("2. paths: %d mentioned paths missing now, %d were already missing at BASE (planned files), %d NEW"
          % (len(now_bad), len(now_bad) - len(new_bad), len(new_bad)))
    for f, p in new_bad:
        print("   BROKEN %s -> %s" % (f, p))
    ok = not missing and not new_bad
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
