"""SkyWynn UI picture budget: the total pixel AREA of the UI pictures (Common/UI/Custom/**/*.png) the SET's jars ship.

Why (round atlas1, 2026-11-21): the Hytale client packs every custom UI picture of the server (vanilla + pack mods + ours) into ONE
texture atlas at join. When it is full it logs "Texture atlas rejected image: <path>" and every picture that did not fit draws as a
red / white missing texture (client log 2026-11-21 18-03: 912 rejected - SkyyTrees/Map 740, vanilla Common 46, SkyyGlass Clear /
Separator ...; our SET then shipped ~76 Mpx, the 2026-11-14 SET with 0 rejected about 45). The atlas fills big pictures first, so the
small ones (buttons, separators, icons - also vanilla's) are the ones lost.
  WARN  the SET's UI picture area > 45 Mpx (WARN_MPX) - past the only PROVEN-good point (11-14 SET, ~45 Mpx, 0 rejected)
  FAIL  > 60 Mpx (FAIL_MPX) - well under the proven-bad point (11-21 SET, ~76 Mpx, 912 rejected)
Both thresholds are UNPROVEN: the atlas size is unknown, and pack mods' + vanilla's own UI pictures share the same atlas but are NOT
counted here. A WARN means "past the last set known to fit" - check the client log for 'Texture atlas rejected' after the deploy.
A picture path shipped by several jars (the SkyyKit art, byte-identical in every hub jar) is ONE atlas entry: counted once (its largest
copy). Area = width x height of the file as shipped (an @2x file counts its full @2x size; a 1x + @2x pair counts both).
How to stay lean (research: SkyyTrees 0.6.9): never ship a big mostly-clear @2x canvas - ship it at 1x cut to its content, share
identical pictures, draw one picture at every zoom, size icons to their drawn size.
Run:
    python tools/ci/ui_budget.py                                    # the SET jars (tools/deploy_set.py), per-mod table
    python tools/ci/ui_budget.py --jar SkyyTrees/SkyyTrees-0.6.9.jar # a candidate jar replaces its mod's SET entry (a new mod is added)
    python tools/ci/ui_budget.py --top 15                           # + the 15 biggest pictures
    python tools/ci/ui_budget.py --next                             # the NEXT set: each SET mod's newest built jar newer than its pin
Exit 1 on FAIL. tools/ci/lint.py calls lint_check(): the NEXT set decides WARN / FAIL (a lean candidate jar not yet pinned fixes it -
otherwise every parallel round's lint would fail until the pin); the pinned SET alone over FAIL_MPX is a WARN ("pin the lean jars").
Skipped where the jars are not built (GitHub Actions).
Jars are looked for in this checkout, then in the main checkout above .claude/worktrees (built jars are git-ignored).
"""
import os, re, sys, struct, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WARN_MPX, FAIL_MPX = 45.0, 60.0   # unproven: 45 = the last known-good SET, 60 = well under the known-bad 76
UI = "Common/UI/Custom/"


def set_pins(root=ROOT):
    """[(mod, version)] of tools/deploy_set.py SET (read as text: no import, comments stripped)"""
    src = open(os.path.join(root, "tools", "deploy_set.py"), encoding="utf8", errors="replace").read()
    src = re.sub(r"(?m)#.*$", "", src)
    i = src.index("SET = [")
    j = src.index("\n]", i)
    return [(m.group(1), m.group(2)) for m in re.finditer(r'\(\s*"(Skyy[A-Za-z]+)"\s*,\s*"(\d+(?:\.\d+)*)"', src[i:j])]


def _roots(root):
    out = [root]
    p = os.path.normpath(root).replace("\\", "/")
    k = p.find("/.claude/worktrees/")
    if k > 0:
        out.append(p[:k])
    return out


def find_jar(mod, ver, root=ROOT):
    for r in _roots(root):
        p = os.path.join(r, mod, "%s-%s.jar" % (mod, ver))
        if os.path.isfile(p):
            return p
    return None


def _vkey(v):
    return tuple(int(x) for x in v.split("."))


def newer_built(mod, ver, root=ROOT):
    """the newest built <Mod>-<v>.jar (this checkout, then the main checkout) with v > the pin, or None"""
    best = None
    for r in _roots(root):
        d = os.path.join(r, mod)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            m = re.match(re.escape(mod) + r"-(\d+(?:\.\d+)*)\.jar\Z", f)
            if m and _vkey(m.group(1)) > _vkey(ver) and (best is None or _vkey(m.group(1)) > _vkey(best[0])):
                best = (m.group(1), os.path.join(d, f))
    return best


def png_size(head):
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def jar_pictures(jar):
    """{path under Common/UI/Custom/: (w, h)} of one jar's UI pictures"""
    out = {}
    with zipfile.ZipFile(jar) as z:
        for n in z.namelist():
            if n.startswith(UI) and n.lower().endswith(".png"):
                with z.open(n) as f:
                    s = png_size(f.read(24))
                if s:
                    out[n[len(UI):]] = s
    return out


def measure(jars):
    """jars = [(mod, jar path)] -> (rows [(mod, files, own Mpx, shared files)], total px, total files, biggest [(px, path, mod)])"""
    owner, size = {}, {}
    per = {}
    for mod, jar in jars:
        pics = jar_pictures(jar)
        per[mod] = pics
        for p, (w, h) in pics.items():
            owner.setdefault(p, []).append(mod)
            size[p] = max(size.get(p, 0), w * h)
    rows = []
    for mod, _jar in jars:
        own = [p for p in per[mod] if owner[p][0] == mod]
        shared = [p for p in per[mod] if len(owner[p]) > 1]
        rows.append((mod, len(per[mod]), sum(size[p] for p in own), len(shared)))
    big = sorted(((size[p], p, owner[p][0]) for p in size), reverse=True)
    return rows, sum(size.values()), len(size), big


def check(root=ROOT, overrides=(), nxt=False):
    """(warns, fails, table lines) for the SET (+ overrides: candidate jar paths; nxt: every SET mod's newest built jar newer than its
    pin). Missing jars are noted, never a FAIL; with no jar built at all (CI) the check is skipped."""
    pins = set_pins(root)
    over = {}
    if nxt:
        for mod, ver in pins:
            nb = newer_built(mod, ver, root)
            if nb:
                over[mod] = nb
    for j in overrides:
        m = re.match(r"(Skyy[A-Za-z]+)-(\d+(?:\.\d+)*)\.jar\Z", os.path.basename(j))
        if not m or not os.path.isfile(j):
            return [], ["ui_budget: --jar %s is not a built <Mod>-<ver>.jar" % j], []
        over[m.group(1)] = (m.group(2), os.path.abspath(j))
    jars, missing = [], []
    for mod, ver in pins:
        if mod in over:
            ver, p = over.pop(mod)
        else:
            p = find_jar(mod, ver, root)
        if p:
            jars.append((mod + " " + ver, p))
        else:
            missing.append("%s %s" % (mod, ver))
    for mod, (ver, p) in sorted(over.items()):   # a new mod
        jars.append((mod + " " + ver, p))
    if not jars:
        return [], [], ["ui_budget: no SET jar is built here - skipped"]
    pinv = dict(pins)
    cand = sorted(m for m, _p in jars if pinv.get(m.split(" ")[0]) != m.split(" ")[1])   # the jars that are not the SET pin
    rows, total, nfiles, big = measure(jars)
    mpx = total / 1e6
    lines = ["ui_budget: the %s's UI pictures (Common/UI/Custom/*.png, a shared path once): %d files, %.2f Mpx (WARN > %g, FAIL > %g)%s"
             % (("NEXT set (newer built jars: %s)" % (", ".join(cand) or "none")) if (nxt or overrides) else "SET",
                nfiles, mpx, WARN_MPX, FAIL_MPX, ("; %d jar(s) not built here: %s" % (len(missing), ", ".join(missing))) if missing else "")]
    small = []
    for mod, n, own, sh in sorted(rows, key=lambda r: (-r[2], r[0])):
        if own >= 10000:
            lines.append("  %-28s %5d files %7.2f Mpx%s" % (mod, n, own / 1e6, ("  (%d shared, counted at their first jar)" % sh) if sh else ""))
        elif n:
            small.append(mod.split(" ")[0])
    if small:
        lines.append("  + %d jar(s) under 0.01 Mpx of their own (the shared SkyyKit art only): %s" % (len(small), ", ".join(small)))
    warns, fails = [], []
    if mpx > FAIL_MPX:
        fails.append("ui_budget: the SET ships %.2f Mpx of UI pictures > %g - the client UI atlas overflows (red / white missing textures); "
                     "make the biggest pictures lean (python tools/ci/ui_budget.py --top 15)" % (mpx, FAIL_MPX))
    elif mpx > WARN_MPX:
        warns.append("ui_budget: the SET ships %.2f Mpx of UI pictures > %g (FAIL at %g: the client UI atlas overflows)" % (mpx, WARN_MPX, FAIL_MPX) + " - past the last set known to fit (11-14, ~45 Mpx; pack mods + vanilla not counted): check the client log for 'Texture atlas rejected'")
    return warns, fails, lines + ["  biggest: %s" % ", ".join("%s %.2f Mpx" % (p, px / 1e6) for px, p, _m in big[:3])]


def lint_check(root=ROOT):
    """for tools/ci/lint.py: (warns, fails, lines) - FAIL / WARN from the NEXT set; the pinned SET alone over FAIL_MPX = a WARN"""
    w1, f1, l1 = check(root, nxt=True)
    w0, f0, l0 = check(root)
    if f0 and not f1:
        w1 = w1 + ["ui_budget: the PINNED set ships %s - pin the lean built jars (the next set is inside the budget)" % l0[0].split(": ", 2)[-1].split(" (WARN")[0]]
    return w1, f1, l1 + ([l0[0]] if l0 and l0[0] != l1[0] else [])


def main(argv):
    ov, top, i, nxt = [], 0, 1, False
    while i < len(argv):
        if argv[i] == "--next":
            nxt = True
            i += 1
        elif argv[i] == "--jar":
            ov.append(argv[i + 1])
            i += 2
        elif argv[i] == "--top":
            top = int(argv[i + 1])
            i += 2
        else:
            print(__doc__)
            return 2
    warns, fails, lines = check(ROOT, ov, nxt)
    for ln in lines:
        print(ln)
    if top:
        pins = set_pins(ROOT)
        over = dict((re.match(r"(Skyy[A-Za-z]+)-", os.path.basename(j)).group(1), os.path.abspath(j)) for j in ov)
        jars = [(m, over.get(m) or find_jar(m, v)) for m, v in pins]
        jars = [(m, p) for m, p in jars if p]
        _r, _t, _n, big = measure(jars)
        for px, p, m in big[:top]:
            print("  %7.2f Mpx  %s  (%s)" % (px / 1e6, p, m))
    for w in warns:
        print("WARN  " + w)
    for f in fails:
        print("FAIL  " + f)
    print("ui_budget: %s" % ("FAIL" if fails else ("WARN" if warns else "OK")))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
