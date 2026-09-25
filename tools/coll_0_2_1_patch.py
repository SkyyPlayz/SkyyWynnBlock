"""Derive SkyyCollections/build_skyycollections_0.2.1.py from 0.2 (0.2 is left untouched; line endings preserved).
Regenerate after editing this file: delete SkyyCollections/build_skyycollections_0.2.1.py, run python tools/coll_0_2_1_patch.py.
0.2.1 = feedback round 2 (HANDOFF log 2026-09-24 07:05 queue), nothing else:
  1. research/Tree-Fall-Spec.md section 3.2: coll:fn:add accepts the source "skills:felled" by default. SkyySkills 0.4.2 credits
     every log that falls when its player cuts a tree through coll:fn:add {uuid, itemId, Long qty, "skills:felled", pkey}.
     CollReg.loadConfig adds skills:felled to ADD_SOURCES unless bridge.add.felled=false (then it is removed even when listed), so an
     existing config.properties gains it without a file rewrite. New installs get the default lines
     bridge.add.sources=skills:double,skills:felled + bridge.add.felled=true. The per-credit / per-minute caps and the profile check
     (expectKey, CollAddTask) are unchanged and apply to felled credits like to every other coll:fn:add source.
     The startup log line and the /collections reload chat line now END with felled=true|false (the loadAll() summary, whose last
     part is loadConfig(), is appended last in both; the fixed startup text and the reload recipe-check result come before it).
  2. Skyy (2026-09-24, verified-in-game note): "Tier -" for a collection with no tier -> "No tier yet". New CollUtil.tierName(t);
     used on the category-grid card and the collection page header. roman(0) still returns "-" (unused for display after this).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.1.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CRLF = "\r\n" in raw
s = raw.replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------- docstring + version ----------------
rep('''"""SkyyCollections 0.2 - build script (written fresh; the 0.1.5 per-profile code, the coll:recipes bridge contract and the page
command rules are carried over, everything else follows research/Collections-Spec.md).
''', '''"""SkyyCollections 0.2.1 - build script (derived from 0.2 by tools/coll_0_2_1_patch.py - edit the patch, not this file; 0.2 was
written fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything
else follows research/Collections-Spec.md).

0.2.1: felled logs + "No tier yet" (feedback round 2), nothing else.
  - coll:fn:add accepts the source skills:felled by default (research/Tree-Fall-Spec.md 3.2): SkyySkills 0.4.2 credits every log
    that falls when its player cuts a tree. loadConfig adds it to bridge.add.sources unless bridge.add.felled=false (false also
    removes it when listed), so existing config files gain it without a rewrite. Caps and the profile check apply as before.
  - A collection without a tier shows "No tier yet" instead of "Tier -" (category card + collection page header).
''')
rep('''Run:   python build_skyycollections_0.2.py            -> SkyyCollections/SkyyCollections-0.2.jar''',
    '''Run:   python build_skyycollections_0.2.1.py          -> SkyyCollections/SkyyCollections-0.2.1.jar''')
rep('''VERSION = "0.2"
''', '''VERSION = "0.2.1"
''')

# ---------------- 1. skills:felled source ----------------
rep('''    "# coll:fn:add sources other mods may use, any case (skills:double = SkyySkills double drops; add minion when SkyyMinions ships)",
    "bridge.add.sources=skills:double",
]''', '''    "# coll:fn:add sources other mods may use, any case (skills:double = SkyySkills double drops; add minion when SkyyMinions ships)",
    "# skills:felled = logs that fall when you cut a tree (SkyySkills 0.4.2)",
    "bridge.add.sources=skills:double,skills:felled",
    "# skills:felled is accepted even when missing from the list above (older config files); false turns felled-log counting off",
    "bridge.add.felled=true",
]''')
rep('''  ADD_SOURCES = lowerSet(p.getProperty("bridge.add.sources", "skills:double"));
  return "migrate=" + MIGRATE + " auto=" + AUTO + " bypass=" + BYPASS;''',
    '''  java.util.HashSet srcs = lowerSet(p.getProperty("bridge.add.sources", "skills:double,skills:felled"));
  boolean felled = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("bridge.add.felled", "true")).trim());
  if (felled) srcs.add("skills:felled"); else srcs.remove("skills:felled");
  ADD_SOURCES = srcs;
  return "migrate=" + MIGRATE + " auto=" + AUTO + " bypass=" + BYPASS + " felled=" + felled;''')

# ---------------- 2. "No tier yet" ----------------
rep('''  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""")
''', '''  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""")
# 0.2.1: a collection with no tier says so (Skyy: 'Tier -' -> 'No tier yet')
M(util, r"""
public static String tierName(int t) {
  return t <= 0 ? "No tier yet" : "Tier " + roman(t);
}""")
''')
rep('''b.set("#SkyyCCdProg" + n + ".Text", "Tier " + @PKG@.CollUtil.roman(ct) + "    " + (ct >= mx''',
    '''b.set("#SkyyCCdProg" + n + ".Text", @PKG@.CollUtil.tierName(ct) + "    " + (ct >= mx''')
rep('''b.set("#SkyyCDTier.Text", "Tier " + @PKG@.CollUtil.roman(ct) + " of " + @PKG@.CollUtil.roman(mx) + (bt > ct''',
    '''b.set("#SkyyCDTier.Text", (ct <= 0 ? "No tier yet" : "Tier " + @PKG@.CollUtil.roman(ct) + " of " + @PKG@.CollUtil.roman(mx)) + (bt > ct''')

# ---------------- startup log + reload message: the loadAll() summary goes LAST so both lines really end with felled=true|false ----
rep('''log("[SkyyCollections] 0.2 ready - item collections (" + s + "), /collections; migration + recipe check run at start");''',
    '''log("[SkyyCollections] 0.2.1 ready - item collections, /collections; migration + recipe check run at start; " + s);''')
rep('''pr.sendMessage(@MSG@.raw("[Collections] reloaded: " + a + "; " + v));''',
    '''pr.sendMessage(@MSG@.raw("[Collections] reloaded: " + v + "; " + a));''')

out = s.replace("\n", "\r\n") if CRLF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(CRLF)" if CRLF else "(LF)")
