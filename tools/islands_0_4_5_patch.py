"""Derive SkyyIslands/build_skyyislands_0.4.5.py from 0.4.4.
0.4.5 (2026-09-24 hotfix for Skyy's 2-player test): the starter kit failed on EVERY new island
('starter kit failed: java.lang.IllegalStateException: Incorrect store for entity reference'). FillTask.starterKit read the chest
through world.getEntityStore().getStore(), but WorldChunk.getBlockComponentEntity() returns a Ref<ChunkStore> and ItemContainerBlock is
a chunk-store component - so the lookup must use world.getChunkStore().getStore() (World.getChunkStore / ChunkStore.getStore verified
with tools/dev/reflect.py). Nothing else changes. SkyyIslands 0.5 (island settings) must be derived from 0.4.5, not 0.4.4.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.4.4.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.4.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.4.4"', 'VERSION = "0.4.5"')
# the one line inside FillTask.starterKit (the only getEntityStore().getStore() after getBlockComponentEntity(4, 129, 4))
a = s.index("public static int starterKit(")
b = s.index("{ST} store = world.getEntityStore().getStore();", a)
assert b - a < 400, "starterKit store line not where expected"
s = s[:b] + "{ST} store = world.getChunkStore().getStore();   // 0.4.5: block-component refs live in the CHUNK store" + s[b + len("{ST} store = world.getEntityStore().getStore();"):]
first = s.index('"""') + 3
s = s[:first] + "0.4.5: starter-kit hotfix - the chest is read through world.getChunkStore().getStore() (was the entity store: 'Incorrect store\n  for entity reference' on every new island). Notes in tools/islands_0_4_5_patch.py.\n" + s[first:]

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
