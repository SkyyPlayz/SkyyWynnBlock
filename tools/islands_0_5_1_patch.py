"""Derive SkyyIslands/build_skyyislands_0.5.1.py from 0.5 (python tools/islands_0_5_1_patch.py, then build the result).
0.5.1 (2026-09-25 SECURITY hotfix, found by the round-3 cross-check with the real command registry + permissions provider):
/island reload (IslandReloadCmd) called requirePermission("skyyislands.admin") but not setPermissionGroups(new String[0]). A
sub-command inherits its parent's permission groups (/island = hytale:Adventurer), and the engine then puts the sub-command's
permission node into those groups - so EVERY player held skyyislands.admin: island protection bypassed, immune to island bans,
/sethub and /island reload open to all. The fix is the SkyySkills ReloadCmd pattern: clear the inherited groups. Nothing else changes.
Every later SkyyIslands version must derive from 0.5.1.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.1.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.5"', 'VERSION = "0.5.1"')
rep('''  super("reload", "(admin) Re-read Skyy_SkyyIslands/config.properties and every island file after hand edits");
  requirePermission("skyyislands.admin");
}""")''', '''  super("reload", "(admin) Re-read Skyy_SkyyIslands/config.properties and every island file after hand edits");
  requirePermission("skyyislands.admin");
  setPermissionGroups(new String[0]);   // 0.5.1: do NOT inherit /island's hytale:Adventurer (it handed every player skyyislands.admin)
}""")''')
first = s.index('"""') + 3
s = s[:first] + ("0.5.1 (2026-09-25): SECURITY hotfix - /island reload clears its inherited permission groups (every player held\n"
                 "  skyyislands.admin through it). Notes in tools/islands_0_5_1_patch.py.\n") + s[first:]

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
