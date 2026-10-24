"""wc15_harness - the shared EXEC + LIVE checks of the wc15 one-time trees.properties update (tools/wc15.py java()), run by the harnesses of
SkyyGear 0.3.45, SkyyMobs 0.1.19 and SkyyClasses 0.1.48 (SkyyAccessories 0.5.33 while Plates was in the round) inside their own child JVM (jpype already started, the mod jar on the class path).

exec_update(K, C, mod)          wcUpdate / wcSame / wcNum on hand-made texts: every old default moves (LF and CRLF kept, "2.0" = 2), custom
                                values kept + noted, a duplicate key (the LAST entry decides), a continued line kept, a missing key = nothing,
                                the marker = null, no trailing line break, a value already new = quiet; the fresh file text (C.V3_TEXT or the
                                given text) carries the marker and the new numbers
exec_migrate(K, C, mod, d)      migrateWc15 on a scratch folder: History copy (exact old bytes) BEFORE the write, the file, change-log lines
                                (Undo form), a second run = nothing; a missing file = nothing; a folder that cannot hold history = file untouched
live_twice(K, C, mod, home, load)  start twice on a scratch COPY of live data: start 1 moves only lines on the old default (+ marker), start 2
                                changes nothing (byte hash), load() then reads the new numbers
"""
import os, hashlib

import trees_v3_effects as V3E
import wc15 as WC


def rows(mod):
    WC.apply(V3E, mod)
    return WC.mig_rows(V3E, mod)


def _file_text(mod, nl="\n", vals=None, extra=""):
    """a trees.properties like the 0.x.y one: a comment head, every WC key (vals: key -> text, default = the OLD text), a non-WC line"""
    L = ["# %s - Skill Trees 3 rows (test copy)" % mod, "tree.Mining.b9.r1a.zz.per=7"]
    for k, o, n, _on, _nn in rows(mod):
        L.append("%s=%s" % (k, (vals or {}).get(k, o)))
    return nl.join(L) + nl + extra


def _upd(C, text):
    from jpype import JString
    r = C.wcUpdate(JString(text))
    if r is None:
        return None
    return str(r[0]), int(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]], [str(x) for x in r[4]]


def _props(text):
    import jpype
    P = jpype.JClass("java.util.Properties")()
    P.load(jpype.JClass("java.io.StringReader")(text))
    return dict((str(k), str(P.getProperty(k))) for k in P.stringPropertyNames())


def exec_update(K, C, mod, fresh_text=None):
    from jpype import JString, JArray
    R = rows(mod)
    keys = [r[0] for r in R]
    mark = WC.mark(mod)
    K.eq([str(x) for x in C.WC_KEY], keys, "X%s WC_KEY = tools/wc15.py mig_rows (%d lines)" % (mod, len(keys)))
    K.eq([str(x) for x in C.WC_NEW], [r[2] for r in R], "X%s WC_NEW" % mod)
    # 1. all old defaults, LF
    t = _file_text(mod)
    u = _upd(C, t)
    K.check(u is not None and u[1] == len(keys) and u[2] == [], "X%s every old default moves (%s)" % (mod, u and u[1:3]))
    exp = _file_text(mod, vals=dict((r[0], r[2]) for r in R)).rstrip("\n") + "\n" + mark + "\n"
    K.eq(u[0], exp, "X%s the new text = old with only the WC values swapped + the marker last" % mod)
    K.eq(u[3], [x for r in R for x in (r[0], r[1], r[2])], "X%s change-log rows key / old / new" % mod)
    K.check(bool(C.wcSame(JString(t).getBytes("ISO-8859-1"), JString(u[0]).getBytes("ISO-8859-1"), JArray(JString)(u[4]))), "X%s wcSame: only the planned keys" % mod)
    bad = u[0].replace("tree.Mining.b9.r1a.zz.per=7", "tree.Mining.b9.r1a.zz.per=8")
    K.check(not bool(C.wcSame(JString(t).getBytes("ISO-8859-1"), JString(bad).getBytes("ISO-8859-1"), JArray(JString)(u[4]))), "X%s wcSame refuses another changed key" % mod)
    K.eq(_upd(C, u[0]), None, "X%s a second pass = null (the marker)" % mod)
    # 2. CRLF kept everywhere
    tc = _file_text(mod, nl="\r\n")
    uc = _upd(C, tc)
    K.check(uc is not None and uc[1] == len(keys) and uc[0].count("\n") == uc[0].count("\r\n") and uc[0].endswith(mark + "\r\n"), "X%s CRLF file: CRLF kept, marker CRLF" % mod)
    # 3. custom values kept + noted; "2.0"-style text = the old number -> moves; a value already new = quiet
    vals = {keys[0]: "77", keys[1]: R[1][2]}
    if len(keys) > 2:
        vals[keys[2]] = R[2][1] + ".0" if "." not in R[2][1] else R[2][1] + "0"
    tu = _file_text(mod, vals=vals)
    uu = _upd(C, tu)
    pu = _props(uu[0])
    K.eq(pu[keys[0]], "77", "X%s a custom value is kept" % mod)
    K.check(len(uu[2]) == 1 and uu[2][0].startswith(keys[0] + "=77 kept"), "X%s ... and noted once: %s" % (mod, uu[2]))
    K.eq(pu[keys[1]], R[1][2], "X%s a value already new stays, quietly" % mod)
    if len(keys) > 2:
        K.eq(pu[keys[2]], R[2][2], "X%s %s=%s (the old number written differently) moves" % (mod, keys[2], vals[keys[2]]))
    K.eq(uu[1], len(keys) - (2 if len(keys) <= 2 else 2), "X%s change count without the kept / already-new lines" % mod)
    # 4. duplicate key: the LAST entry decides (first old, last custom -> kept; first custom, last old -> the last line moves)
    td = _file_text(mod) + "%s=55\n" % keys[0]
    ud = _upd(C, td)
    K.check(_props(ud[0])[keys[0]] == "55" and ud[0].count("%s=%s\n" % (keys[0], R[0][1])) == 1 and any(n.startswith(keys[0] + "=55") for n in ud[2]),
            "X%s a duplicate key: the last (custom) entry is kept, the earlier line untouched" % mod)
    td2 = _file_text(mod, vals={keys[0]: "55"}) + "%s=%s\n" % (keys[0], R[0][1])
    ud2 = _upd(C, td2)
    K.check(_props(ud2[0])[keys[0]] == R[0][2] and ("%s=55\n" % keys[0]) in ud2[0], "X%s a duplicate key: the last (old) entry moves, the first stays" % mod)
    # 5. a continued (two-line) value is not touched
    tl = _file_text(mod).replace("%s=%s\n" % (keys[0], R[0][1]), "%s=\\\n  %s\n" % (keys[0], R[0][1]))
    ul = _upd(C, tl)
    K.check(("%s=\\\n  %s\n" % (keys[0], R[0][1])) in ul[0] and any(n.startswith(keys[0] + "=") and "kept" in n for n in ul[2]), "X%s a continued line is kept + noted" % mod)
    # 6. missing keys: nothing changes but the marker; 7. no trailing line break
    tm = "# only a comment\nother.key=1"
    um = _upd(C, tm)
    K.eq((um[0], um[1], um[2]), (tm + "\n" + mark + "\n", 0, []), "X%s no WC key: the marker only (no trailing break: one added before it)" % mod)
    tmc = "# c\r\nother.key=1"
    K.eq(_upd(C, tmc)[0], tmc + "\r\n" + mark + "\r\n", "X%s CRLF without a trailing break" % mod)
    K.eq(_upd(C, "x=1\n# " + WC.MARK_ID + " hand note\n"), None, "X%s the marker anywhere in a comment = done" % mod)
    K.check(_upd(C, "x=1  # " + WC.MARK_ID + "\n") is not None, "X%s the marker inside a value is not a marker" % mod)
    K.check(float(C.wcNum("  2.50 ")) == 2.5 and str(C.wcNum("abc")) == "nan" and str(C.wcNum(None)) == "nan" and str(C.wcNum("NaN")) == "nan", "X%s wcNum" % mod)
    K.check(bool(C.wcEq(2.0, 2.0)) and not bool(C.wcEq(2.0001, 2.0)) and not bool(C.wcEq(float("nan"), 2.0)), "X%s wcEq" % mod)
    # 8. the fresh file text
    ft = str(C.V3_TEXT) if fresh_text is None else fresh_text
    fp = _props(ft)
    K.check(ft.count(WC.MARK_ID) == 1 and _upd(C, ft) is None, "X%s the fresh trees.properties carries the marker (never updated)" % mod)
    K.eq([fp.get(r[0]) for r in R], [r[2] for r in R], "X%s the fresh file holds the new numbers" % mod)
    K.check(all(ord(c) < 128 for c in ft), "X%s the fresh file is ASCII" % mod)


def _hash(d):
    out = {}
    for root, _ds, fs in os.walk(d):
        for f in fs:
            p = os.path.join(root, f)
            out[os.path.relpath(p, d)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def exec_migrate(K, C, mod, d):
    from jpype import JClass
    Paths = JClass("java.nio.file.Paths")
    R = rows(mod)
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "trees.properties")
    K.eq(str(C.migrateWc15(Paths.get(d))), "", "X%s migrateWc15: no file = nothing" % mod)
    K.check(not os.path.exists(f), "X%s ... and no file written" % mod)
    K.eq(str(C.migrateWc15(None)), "", "X%s migrateWc15(null) = nothing" % mod)
    old = _file_text(mod, nl="\r\n", vals={R[0][0]: "41"}).encode("latin-1")
    open(f, "wb").write(old)
    msg = str(C.migrateWc15(Paths.get(d)))
    new = open(f, "rb").read()
    K.check(msg.startswith("trees.properties: %d Weaponcraft lines raised x1.5" % (len(R) - 1)) and (R[0][0] + "=41 kept") in msg, "X%s migrateWc15 message: %s" % (mod, msg[:160]))
    pn = _props(new.decode("latin-1"))
    K.eq([pn[r[0]] for r in R], ["41"] + [r[2] for r in R[1:]], "X%s the file now holds the new numbers (custom kept)" % mod)
    K.check(new.count(b"\n") == new.count(b"\r\n") and new.decode("latin-1").count(WC.MARK_ID) == 1, "X%s CRLF kept, one marker" % mod)
    hd = os.path.join(d, "config-history")
    baks = sorted(x for x in os.listdir(hd) if x.endswith(".bak")) if os.path.isdir(hd) else []
    K.check(len(baks) == 1 and baks[0].endswith("trees.properties." + baks[0].split("trees.properties.")[-1]) and open(os.path.join(hd, baks[0]), "rb").read() == old,
            "X%s History: one copy with exactly the old bytes (%s)" % (mod, baks))
    idx = open(os.path.join(hd, "index.log"), encoding="utf8").read() if os.path.isfile(os.path.join(hd, "index.log")) else ""
    K.check("before the Weaponcraft x1.5 update (wc15)" in idx, "X%s History index line" % mod)
    lg = os.path.join(d, "config-changes.log")
    lines = [l.split("\t") for l in open(lg, encoding="utf8").read().splitlines()] if os.path.isfile(lg) else []
    K.eq([(l[1], l[3], l[4], l[5], l[6], l[7]) for l in lines], [("%s %s update (wc15)" % (mod, WC.VERSIONS[mod]), "update", r[0], r[1], r[2], "ok") for r in R[1:]],
         "X%s change log: one 'ok' line per moved line (Undo form: key, old, new)" % mod)
    h1 = _hash(d)
    K.eq(str(C.migrateWc15(Paths.get(d))), "", "X%s a second run = nothing" % mod)
    K.eq(_hash(d), h1, "X%s ... and nothing written" % mod)
    # a folder whose history cannot be written: the file stays as it is
    d2 = os.path.join(d, "nohist")
    os.makedirs(d2, exist_ok=True)
    f2 = os.path.join(d2, "trees.properties")
    open(f2, "wb").write(_file_text(mod).encode("latin-1"))
    open(os.path.join(d2, "config-history"), "wb").write(b"a file where the history folder should be")
    b2 = open(f2, "rb").read()
    K.eq(str(C.migrateWc15(JClass("java.nio.file.Paths").get(d2))), "", "X%s History cannot be written -> nothing done" % mod)
    K.eq(open(f2, "rb").read(), b2, "X%s ... the file untouched" % mod)
    K.check(os.path.isfile(os.path.join(d2, "config-history")), "X%s ... the blocking file kept" % mod)


def live_twice(K, C, mod, home, load):
    """home = the scratch COPY of Skyy_<Mod>; load = a Python callable running the mod's own loader of trees.properties after the update"""
    from jpype import JClass
    Paths = JClass("java.nio.file.Paths")
    R = rows(mod)
    f = os.path.join(home, "trees.properties")
    had = os.path.isfile(f)
    before = open(f, "rb").read() if had else b""
    pb = _props(before.decode("latin-1")) if had else {}
    m1 = str(C.migrateWc15(Paths.get(home)))
    load()
    after = open(f, "rb").read() if os.path.isfile(f) else b""
    pa = _props(after.decode("latin-1"))
    moved = [r[0] for r in R if r[0] in pb and abs(float(pb[r[0]]) - r[3]) < 1e-9]
    K.notes.append("D%s live trees.properties: %s; %d WC lines present, %d on the old default -> moved; message: %s" % (
        mod, "present" if had else "absent", sum(1 for r in R if r[0] in pb), len(moved), m1[:200]))
    if had:
        K.check(all(pa.get(k) == dict((r[0], r[2]) for r in R)[k] for k in moved), "D%s start 1: every live line on the old default moved" % mod)
        K.check(all(pa.get(k) == v for k, v in pb.items() if k not in moved), "D%s start 1: every other live value kept" % mod)
        K.check(after.decode("latin-1").count(WC.MARK_ID) == 1, "D%s start 1: the marker" % mod)
        K.check((b"\r\n" in before) == (b"\r\n" in after) or not before, "D%s start 1: line endings kept" % mod)
    # fixer (critic 3 finding 5): the live copy gets exactly one "kept" note per WC line holding a custom value (neither old nor new
    # default) - no unexpected "kept" notes on Skyy's data
    custom = sorted(r[0] for r in R if r[0] in pb and abs(float(pb[r[0]]) - r[3]) > 1e-9 and abs(float(pb[r[0]]) - float(r[2])) > 1e-9)
    kept = sorted(n.split("=", 1)[0] for n in m1.split("\n")[1:] if " kept" in n)
    K.eq(kept, custom, "D%s start 1: one 'kept' note per custom live value, none other (%d)" % (mod, len(custom)))
    h1 = _hash(home)
    m2 = str(C.migrateWc15(Paths.get(home)))
    load()
    K.check(m2 == "" and _hash(home) == h1, "D%s start 2 changes nothing (%r)" % (mod, m2[:80]))
    return moved, pb, pa
