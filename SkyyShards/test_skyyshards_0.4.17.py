"""Harness for SkyyShards 0.4.17 (rarity colours + sectioned item text; looks only - tools/shards_0_4_17_patch.py, on top of 0.4.16).
Build first:
    python tools/shards_0_4_17_patch.py && python SkyyShards/build_skyyshards_0.4.17.py
    python SkyyShards/test_skyyshards_0.4.17.py [--keep]

  S17  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand / lock region /
                Java method; line endings kept
  RA   assets   (jar vs the 0.4.16 jar) the six portals = Legendary, each modifier = the rarity of the bench tier that crafts it, every
                other key of those items unchanged; totem items + benches byte-identical; every portal / totem / modifier / bench
                description (both prefixes, identical) parses as <color is="#hex">..</color> spans + \\n only (none nested), starts with
                the tag span in the item's own rarity colour, holds the tag text, the four sections in order, the action line #ffcc00 last,
                the Style Guide 15 colours only; its plain text (spans stripped) keeps 0.4.16's sentence words; every other lang line identical
  RX   executed the Totem Bench page (real builders): Modifiers tab, every slot clicked - the page's frame colour (qRar / gEd) = the jar
                item's Quality colour and its qTag = the description's tag; ShPage.needOf for every modifier on all six benches = the item's
                rarity; ShKind.ofShard -> TQC[3] = the portals' Legendary
  then 0.4.16's open (Pocket costs) + LB bytecode + 0.4.13 flows3 (bench clicks) + 0.4.9 page + D live start twice (scratch copy)
  A verify (-Xverify:all), C compare (0.4.16 -> 0.4.17 = EXPECT; the non-class files = exactly the 10 changed item files + server.lang), AA audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.4.17"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_shards", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.16.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.16.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_17_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_16", os.path.join(HERE, "test_skyyshards_0.4.16.py"))
T416 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T416)
sys.argv[:] = _argv
T415, T414, T413 = T416.T415, T416.T414, T416.T413
T412, T411, T410, T49 = T416.T412, T416.T411, T416.T410, T416.T49
for _m in (T416, T415, T414, T413):
    _m.JAR, _m.GEN = JAR, GEN
T416.SCRATCH = T415.SCRATCH = T414.SCRATCH = SCRATCH
T415.VERSION = VERSION
FK = T416.FK
_h, _g, _p = T416._h, T416._g, T416._p

KINDS = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]
MODS = [("wider", "Wider", "Wider Area", 1), ("faster", "Faster", "Faster", 1), ("replant", "Replant", "Auto-Replant", 2),
        ("compost", "Compost", "Compost", 3), ("storage", "Storage", "Storage", 2), ("rare", "RareFinder", "Rare Finder", 3)]   # = the build's MOD_BENCH
TQ = ["Uncommon", "Rare", "Epic", "Legendary", "Legendary"]
ROMAN = ["I", "II", "III", "IV", "V"]
PORTALS = ["Skyy_Shard_" + k for k in KINDS]
MODIDS = ["Skyy_TotemMod_" + m[1] for m in MODS]
BENCHES = ["Skyy_TotemBench_" + k for k in KINDS]
COLS = {"#d6e4ee", "#7ee08a", "#7f93a6", "#ffcc00", "#9aacbc"}   # fix: + the kit "section" header colour
SPAN = re.compile(r'<color is="(#[0-9a-f]{6})">([^<>]*)</color>')


def _jar(j):
    with zipfile.ZipFile(j) as z:
        return dict((n, z.read(n)) for n in z.namelist())


def _lang(files):
    d = {}
    for ln in files["Server/Languages/en-US/server.lang"].decode("utf8").split("\n"):
        if "=" in ln:
            k, v = ln.split("=", 1)
            assert k not in d, k
            d[k] = v
    return d


def _item_path(files, iid):
    ps = [n for n in files if n.startswith("Server/Item/Items/SkyyShards/") and n.endswith("/%s.json" % iid)]
    assert len(ps) == 1, (iid, ps)
    return ps[0]


def parse(desc):
    """the description as [(colour, text) | '\\n'] - None if anything is not a span or the two-character line break"""
    out, i = [], 0
    while i < len(desc):
        if desc.startswith("\\n", i):
            out.append("\n")
            i += 2
            continue
        m = SPAN.match(desc, i)
        if not m:
            return None
        out.append((m.group(1), m.group(2)))
        i = m.end()
    return out


def plain(desc):
    return "".join(x if x == "\n" else x[1] for x in parse(desc))


# ---------------------------------------------------------------------------------------------------------- S17: static
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.17 - build script') and g.count('VERSION = "0.4.17"\n') == 1, "S17 header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "LOCK.lock()", "\nM(", "\nF(", "\nC("):
        K.check(g.count(w) == o.count(w), "S17 no new %r (%d)" % (w, g.count(w)))
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.17: rarity colours + sectioned item text; 0.4.16: Pocket Dimension costs" in g, "S17 the ready line names the round")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S17 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S17 line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- RA: the item files + text
def expected():
    """item id -> (Quality or None, tag text, action prefix)"""
    e = {}
    for k in KINDS:
        e["Skyy_Shard_" + k] = ("Legendary", "Shard - Legendary", "Right-click: open the shard menu")
        e["Skyy_TotemBench_" + k] = (None, "Totem Bench", "Right-click: open the bench")
    for m in MODS:
        e["Skyy_TotemMod_" + m[1]] = (TQ[m[3] - 1], "Totem modifier - %s - Bench %s" % (TQ[m[3] - 1], ROMAN[m[3] - 1]), "Add it: a placed totem's own page")
    return e


def run_assets(out, jar, _scratch, _home):
    K = HK.Child(out)
    nf, of = _jar(jar), _jar(OLD_JAR)
    nl, ol = _lang(nf), _lang(of)
    E = expected()
    totems = sorted(set(k.split(".")[1] for k in nl if k.startswith("items.Skyy_Totem_") and k.endswith(".description")))
    K.check(len(totems) == 20, "RA 20 totem items in the lang file (%d)" % len(totems))
    for t in totems:
        E[t] = ("Uncommon", "T1 Totem - Uncommon", "")
    # (a) Quality
    for iid in PORTALS + MODIDS:
        p_ = _item_path(nf, iid)
        nj, oj = json.loads(nf[p_]), json.loads(of[p_])
        q0 = oj.pop("Quality", None)
        q1 = nj.pop("Quality", None)
        K.check(q1 == E[iid][0] and nj == oj, "RA (a) %s: Quality %s -> %s, every other key unchanged" % (iid, q0, q1))
    # (c) totems + benches + every other item file unchanged
    same = [n for n in of if n.startswith("Server/Item/") and n not in [_item_path(nf, i) for i in PORTALS + MODIDS]]
    K.check(len(same) >= 46 and all(nf.get(n) == of[n] for n in same), "RA (c) the other %d item files (20 totems, 20 totem blocks, 6 benches) byte-identical" % len(same))
    for t in totems:
        K.check(json.loads(nf[_item_path(nf, t)]).get("Quality") == "Uncommon", "RA (c) %s stays Uncommon (tier I)" % t)
    # (b) the descriptions
    for iid in sorted(E):
        q, tag, act = E[iid]
        d0, d1 = nl.get("items.%s.description" % iid), nl.get("server.items.%s.description" % iid)
        K.check(d0 is not None and d0 == d1, "RA %s: both prefixes written, identical" % iid)
        sp = parse(d0 or "")
        K.check(sp is not None, "RA %s: only <color is=\"#hex\"> spans + \\n (no nesting, no stray markup)" % iid)
        if not sp:
            continue
        K.check(d0.startswith("<color") and sp[0] == (SUI.QUALITY[q or "Common"], tag),
                "RA (b) %s: line 1 = '%s' in its rarity colour %s (%s)" % (iid, tag, SUI.QUALITY[q or "Common"], sp[0]))
        spans = [x for x in sp if x != "\n"]
        K.check(set(c for c, _t in spans[1:]) <= COLS, "RA %s: Style Guide 15 colours only after the tag: %s" % (iid, sorted(set(c for c, _t in spans[1:]))))
        heads = [t for c, t in spans if t in ("WHAT IT DOES", "WORKS IN", "HOW TO USE")]
        K.check(heads == ["WHAT IT DOES", "WORKS IN", "HOW TO USE"], "RA %s: the sections in order: %s" % (iid, heads))
        hc = [c for c, t in spans if t in ("WHAT IT DOES", "WORKS IN", "HOW TO USE")]
        K.check(hc == ["#9aacbc"] * 3 and all(c != "#9aacbc" for c, t in spans if t not in ("WHAT IT DOES", "WORKS IN", "HOW TO USE")),
                "RA fix1 %s: every section header #9aacbc (kit section, pet tooltip), nothing else in it: %s" % (iid, hc))
        txt0 = plain(d0)
        _how = txt0.split("\n\nHOW TO USE\n", 1)[-1].split("\n\n", 1)[0].lower()
        K.check(spans[-1][1].startswith("Right-click") or spans[-1][1].startswith("Add it"), "RA fix3 %s: the action line is a click action: %s" % (iid, spans[-1][1]))
        K.check(spans[-1][1].lower() not in _how and "shard menu - totems tab" not in spans[-1][1].lower(), "RA fix3 %s: the action line does not repeat HOW TO USE" % iid)
        K.check(spans[-1][0] == "#ffcc00" and spans[-1][1].startswith(act) and ": " in spans[-1][1], "RA %s: the action line last, #ffcc00: %s" % (iid, spans[-1]))
        K.check(any(c == "#7ee08a" for c, _t in spans), "RA %s: its key words green #7ee08a" % iid)
        txt = plain(d0)
        K.check(txt.split("\n")[0] == tag and "\n\nWHAT IT DOES\n" in txt and "\n\nHOW TO USE\n" in txt, "RA %s: renders as sections: %r" % (iid, txt[:90]))
        # 0.4.16's sentence words are all still there (looks only)
        ow = set(re.findall(r"[A-Za-z][A-Za-z'-]+", ol["items.%s.description" % iid])) - {"Works", "in", "the", "A", "It", "Shard", "Shards", "totem", "modifier"}
        nw = set(re.findall(r"[A-Za-z][A-Za-z'-]+", txt))
        K.check(not (ow - nw), "RA %s: keeps 0.4.16's words (missing %s)" % (iid, sorted(ow - nw)))
    # every other lang line identical
    ch = sorted(k for k in set(nl) | set(ol) if nl.get(k) != ol.get(k))
    K.check(set(ch) == set(pre + "items.%s.description" % i for i in E for pre in ("", "server.")),
            "RA only the %d description lines changed (names and every other key identical): %s" % (len(ch), [c for c in ch if c.split(".")[-2] not in E][:4]))
    K.check(len(E) == 38, "RA 38 items carry the new text (6 portals, 20 totems, 6 modifiers, 6 benches): %d" % len(E))
    K.save()


# ---------------------------------------------------------------------------------------------------------- RX: the bench page agrees
def run_rarity(out, jar, scratch, _home):
    K = HK.Child(out)
    nf = _jar(jar)
    nl = _lang(nf)
    E = expected()
    L, ou, W, p, lv = T413._L(os.path.join(scratch, "rx"), K)
    Page, PFn, Cfg, Tot, Kd = L["ShPage"], L["ShPageFn"], L["ShCfg"], L["ShTotem"], L["ShKind"]
    cs = L["inv"](27, 27, 9)
    Page.TEST_INV = cs
    TQC = [str(x) for x in Page.TQC]
    K.check(TQC == [SUI.QUALITY[q] for q in TQ] and [str(x) for x in Page.TQN] == TQ, "RX the page's TQC / TQN = the kit's rarity colours %s" % TQC)
    ids = [str(x) for x in Cfg.CRAFT_ID]
    pb = PFn(FK, 2).make(None, ou, "skyy-shard-" + T416.OWNER)
    T410.full(pb)
    for kd in range(6):   # needOf on every bench (the bench tier a modifier needs is the same on all six)
        for mi, mid in enumerate(MODIDS):
            n = int(pb.needOf(kd, ids.index(mid)))
            K.check(TQ[n - 1] == json.loads(nf[_item_path(nf, mid)])["Quality"], "RX needOf(%s, %s) = Bench %s -> %s = the item's Quality" % (KINDS[kd], mid, ROMAN[n - 1], TQ[n - 1]))
    for k, sid in enumerate(PORTALS):
        K.check(int(Kd.ofShard(sid)) >= 0 and TQC[3] == SUI.QUALITY[json.loads(nf[_item_path(nf, sid)])["Quality"]], "RX %s: the page's shard edge TQC[3] = the item's Legendary" % sid)

    def click(a):
        pb.kLast = None
        pb.handleDataEvent(None, None, json.dumps({"a": a}))
        r = T410.full(pb)
        K.check(not r["miss"] and not r["unbound"], "RX %s: the page walks clean %s %s" % (a, r["miss"][:2], r["unbound"][:2]))
    click("bcat3")
    seen = set()
    for s in range(int(pb.gN)):
        click("bg%d" % s)
        mid = str(pb.qIt)
        seen.add(mid)
        q = json.loads(nf[_item_path(nf, mid)])["Quality"]
        tag = plain(nl["items.%s.description" % mid]).split("\n")[0]
        K.check(str(pb.qRar).lower() == SUI.QUALITY[q].lower() == str(pb.gEd[s]).lower() and str(pb.qTag) == tag == E[mid][1],
                "RX the bench's Modifiers slot %d (%s): page frame %s + tag '%s' = the item's %s frame + its text's tag '%s'" % (s + 1, mid, pb.qRar, pb.qTag, q, tag))
    K.check(seen == set(MODIDS), "RX every modifier on the bench page: %s" % sorted(seen))
    Page.TEST_INV = None
    K.save()


def run_live(out, jar, scratch, home):
    T411.run_live411(out, jar, scratch, home)


EXPECT = {   # 0.4.16 -> 0.4.17, checked by hand 2026-10-30: only the version texts (CfgFn opExport / CfgRows header, the ShStore migrate* log
    # lines + save's constant-pool indexes, the ready line in SkyyShardsPlugin.setup)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the non-class files: exactly the 10 item files (6 portals + the 4 modifiers above Bench I) + server.lang differ (manifest.json aside); the classes as EXPECT"""
    nf, of = _jar(jar), _jar(old_jar)
    na = dict((n, b) for n, b in nf.items() if not n.endswith(".class"))
    nb = dict((n, b) for n, b in of.items() if not n.endswith(".class"))
    ch = sorted(n for n in set(na) | set(nb) if na.get(n) != nb.get(n) and n != "manifest.json")
    # Wider Area / Faster are Bench I = Uncommon as before: their files stay byte-identical
    want = sorted([_item_path(nf, i) for i in PORTALS] + [_item_path(nf, "Skyy_TotemMod_" + m[1]) for m in MODS if m[3] > 1] + ["Server/Languages/en-US/server.lang"])
    assert ch == want, "C non-class files differ beyond the item text: %s" % sorted(set(ch) ^ set(want))[:8]
    print("C. %d non-class files: only the %d portal / modifier item files + server.lang changed" % (len(nb), len(want) - 1))
    cps = []
    for j, tag in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag)
        with zipfile.ZipFile(j) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
            for n_ in zi.namelist():
                if not T49.MAP_ENTRY.match(n_) and n_ not in want:
                    zo.writestr(n_, zi.read(n_))
        cps.append(cp)
    T49._ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("assets", run_assets), ("rarity", _h(_g(run_rarity))),
                   ("open", _h(_g(T416.run_open), True)), ("bytecode", T415.run_bytecode),
                   ("flows3", _h(_g(T413.run_flows3))), ("page49", _h(_p(T49.run_page))),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
