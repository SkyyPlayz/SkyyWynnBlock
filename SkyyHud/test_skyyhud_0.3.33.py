"""SkyyHud 0.3.33 harness - Quest widget texts wrap onto the next row instead of ending in "..." (beta bug 13; tools/hud_0_3_33_patch.py).
Built on tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir
in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.33.py [--jar SkyyHud-0.3.33.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.32 -> 0.3.33: exactly the listed classes / members differ (Widgets: the wrap helpers + shapeOf + the 3 Quest methods;
                HudMain: build + fill use shapeOf)
  Q33  wrap     Widgets on real quest:fn:hud style models: the sample = no extra rows, height 149 at 100 % as before; a long header /
                tracked task / where line / next task wraps onto <key>L<j> rows (no "...", the words kept in order, every row within its
                room measured bold, the first row beside its count / progress); questH grows by exactly the row heights; every pair key
                has its label in questBody's markup and nothing is drawn below the box; a word longer than a row splits by letters;
                text beyond the most rows ends in "..." on the last row only; the empty state wraps too; scales 50 / 67 / 100 / 200
                balanced; shapeOf = the model shape + the row counts (same rows = same shape, e.g. "6/10" -> "7/10" or a new distance;
                another row count = another shape; other widgets / hidden = the model shape)
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the client drawing the extra rows (the font table vs the real glyphs), the re-send look.
Scratch: tools/dev/scratch/bq/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HK

VERSION, PREV = "0.3.33", "0.3.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "bq", "h")))
PKG = "com.skyy.hud."


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_q33(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject
    t24 = load_module(os.path.join(HERE, "test_skyyhud_0.3.24.py"), "hud0324h")
    t24.JAR_IN_USE[0] = jar
    K = HK.Child(out)
    E = t24._env(scratch)
    H, bridge = E["H"], E["bridge"]
    Wid = H("Widgets")
    Double, Integer, Boolean, String = JClass("java.lang.Double"), JClass("java.lang.Integer"), JClass("java.lang.Boolean"), JClass("java.lang.String")
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    lay = wdef("Quest")
    BASE = "SkyyWQuest"

    def task(name, prog="", frac=None, where="", d=-1, done=False):
        return [String(name), String(prog), None if frac is None else Double(frac), String(where), Integer(d), Boolean(done)]

    def model(title, count, tasks):
        a = [String(title), String(count)]
        for t in tasks:
            a += t
        return Wid.questModelOf(JArray(JObject)(a))

    def py(m):
        return [None if v is None else str(v) for v in m]

    def pairs(m, sc=100):
        a = [str(x) for x in Wid.questPairs(m, sc, True)]
        return dict(zip(a[0::2], a[1::2])), a[0::2]

    def rows(m, sc, k):
        return [str(x) for x in Wid.qLines(m, sc, k)]

    def body(m, sc=100):
        return str(Wid.questBody(BASE, lay, sc, m, 6, 300 * sc // 100))

    def labels_ok(m, sc, what):
        b = body(m, sc)
        d, keys = pairs(m, sc)
        miss = [k for k in keys if ("Label #%s%sTxt " % (BASE, k)) not in b]
        K.check(not miss, "Q33 %s: every pair has its label (missing %s)" % (what, miss))
        drawn = set(re.findall(r"Label #%s([A-Z][A-Za-z0-9]*)Txt " % BASE, b))
        extra = sorted(drawn - set(keys))
        K.check(not extra, "Q33 %s: no label without a pair (extra %s)" % (what, extra))
        h = int(Wid.questH(m, sc))
        bottoms = [int(t) + int(hh) for t, hh in re.findall(r"Label #%s[A-Za-z0-9]+Txt \{ Anchor: \(Left: -?\d+, Top: (-?\d+), Width: \d+, Height: (\d+)\)" % BASE, b)]
        K.check(bottoms and max(bottoms) <= h + 4 * sc // 100 + 2, "Q33 %s: nothing drawn below the box (lowest label %s, box %d)" % (what, max(bottoms) if bottoms else None, h))
        K.check(b.count("{") == b.count("}"), "Q33 %s: balanced markup" % what)
        return d, keys, b

    QR = [10, 18, 6, 1, 7, 18, 4, 6, 4, 15, 8, 17]
    # ---- 1. the editor sample (short texts, SkyyQuests present): no extra rows, the 0.3.32 height
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class HudFake(object):
        @JOverride
        def apply(self, x):
            return None
    bridge.put("quest:fn:hud", HudFake())
    s = Wid.questSample()
    d, keys = pairs(s)
    K.check(not [k for k in keys if "L" in k] and not any(v.endswith("...") for v in d.values()), "Q33 sample: no extra rows, nothing cut (%s)" % keys)
    K.eq(int(Wid.questH(s, 100)), 149, "Q33 sample: 149 px high at 100 % as in 0.3.32")
    labels_ok(s, 100, "sample")
    # ---- 2. a long tracked task name wraps (its progress stays on row 1)
    LONG_N = "Craft a crafting accessory at the workbench and then put it into your Void Charms"
    m = model("Getting Started", "3 / 24", [task(LONG_N, "0/1", 0.0, "NE  42 m  -  Island 2", 1), task("Mine stone and copper", "0/2"), task("Chop 10 logs", "6/10")])
    r = rows(m, 100, "N0")
    K.check(len(r) >= 2 and " ".join(r) == LONG_N and not r[-1].endswith("..."), "Q33 long task name -> %d rows, the words kept, no '...': %s" % (len(r), r))
    fs14 = int(Wid.fsOf(14, 100, 6))
    full = 300 - 20 - 14
    r1 = full - int(Wid.textW("0/1", fs14, True)) - 8
    K.check(int(Wid.textW(r[0], fs14, True)) <= r1 and all(int(Wid.textW(x, fs14, True)) <= full for x in r[1:]), "Q33 ... row 1 fits beside '0/1', the rest the full width")
    K.check(int(Wid.textW(r[0] + " " + r[1].split(" ")[0], fs14, True)) > r1, "Q33 ... row 1 is as full as it can be (greedy)")
    K.eq(int(Wid.questH(m, 100)), 149 + (len(r) - 1) * QR[5], "Q33 ... the box grows by exactly the extra task rows (18 px each)")
    d, keys, b = labels_ok(m, 100, "long task")
    K.check(d["N0"] == r[0] and d.get("N0L1") == r[1] and d["S0"] == "0/1", "Q33 ... pairs N0 / N0L1 / S0")
    K.check(not any(v.endswith("...") for v in d.values()), "Q33 ... no text ends in '...'")
    # ---- 3. header, where line, next task wrap too
    LONG_H = "The Very Long Getting Started Tutorial Quest Line Of The Sky Islands"
    LONG_W = "Go north-east past the big oak tree and the old ruins  -  Island 2"
    LONG_T = "Defeat the skeleton captain at the camp on the second island"
    m = model(LONG_H, "3 / 24", [task("Chop 10 logs", "6/10", 0.6, LONG_W, 1), task(LONG_T, "0/1"), task("Mine stone", "0/2")])
    rh, rw, rt = rows(m, 100, "H"), rows(m, 100, "W0"), rows(m, 100, "N1")
    K.check(len(rh) == 2 and len(rw) == 2 and len(rt) == 2, "Q33 header / where / next task -> 2 rows each: %s | %s | %s" % (rh, rw, rt))
    K.check(" ".join(rt) == LONG_T and " ".join(rh).replace("...", "") in LONG_H, "Q33 ... words kept")
    K.eq(int(Wid.questH(m, 100)), 149 + QR[1] + QR[9] + QR[11], "Q33 ... the box grows by header 18 + where 15 + next task 17")
    d, keys, b = labels_ok(m, 100, "header / where / next task")
    K.check(all(k in keys for k in ("HL1", "W0L1", "N1L1")), "Q33 ... pairs HL1 / W0L1 / N1L1: %s" % keys)
    # the where line's row 2 lines up with its text after the arrow
    xw = re.search(r"Label #%sW0Txt \{ Anchor: \(Left: (\d+)," % BASE, b).group(1)
    xw1 = re.search(r"Label #%sW0L1Txt \{ Anchor: \(Left: (\d+)," % BASE, b).group(1)
    K.eq(xw1, xw, "Q33 ... the where line's row 2 starts where its text starts (after the arrow)")
    # ---- 4. a word longer than a row splits by letters; beyond the most rows -> '...' on the last row only
    m = model("Q", "1 / 1", [task("X" * 119, "", None, "", -1)])
    r = rows(m, 100, "N0")
    K.check(len(r) == 3 and r[-1].endswith("...") and not r[0].endswith("...") and not r[1].endswith("..."), "Q33 one 119-letter word -> 3 rows, only the last cut: %s" % [len(x) for x in r])
    K.check(all(int(Wid.textW(x, fs14, True)) <= full for x in r), "Q33 ... every row within the width")
    m = model("Q", "1 / 1", [task(("word " * 30).strip(), "", None, "", -1)])
    r = rows(m, 100, "N0")
    K.check(len(r) == 3 and r[-1].endswith("..."), "Q33 120 characters of words -> the 3 rows, '...' only past the last")
    labels_ok(m, 100, "very long")
    # ---- 5. the empty state's line wraps (the whole width)
    m = model("Tutorial done - pick a new quest line at the board", "", [])
    pm = py(m)
    K.eq(pm[4], "E", "Q33 0 tasks = the empty state")
    m2 = list(pm)
    m2[8] = "Pick one at the quest board in the hub, or ask Marlow at the dock what to do next"
    jm2 = JArray(String)([None if v is None else String(v) for v in m2])
    rw = rows(jm2, 100, "W0")
    K.check(len(rw) == 2 and not rw[-1].endswith("..."), "Q33 empty state: a long line -> 2 rows %s" % rw)
    K.eq(int(Wid.questH(jm2, 100)), 67 + QR[9] + (len(rows(jm2, 100, "H")) - 1) * QR[1], "Q33 ... height grows by the where row (+ a wrapped header)")
    labels_ok(jm2, 100, "empty state")
    # ---- 6. every size
    m = model(LONG_H, "3 / 24", [task(LONG_N, "6/10", 0.6, LONG_W, 3), task(LONG_T, "0/1"), task("Mine stone and copper", "0/2")])
    for sc in (50, 67, 100, 150, 200):
        d, keys, b = labels_ok(m, sc, "size %d %%" % sc)
        K.check(not any(v.endswith("...") for k, v in d.items() if k != "N0L2"), "Q33 size %d %%: no '...' (rows %s)" % (sc, [k for k in keys if "L" in k]))
    # ---- 7. the shape: + the row counts
    sh = str(Wid.shapeOf("Quest", m, lay))
    K.check(sh.startswith(str(m[0]) + "|w"), "Q33 shapeOf = the model shape + |w<rows>: %s" % sh)
    m7 = model(LONG_H, "3 / 24", [task(LONG_N, "7/10", 0.7, LONG_W.replace("42", "41"), 3), task(LONG_T, "0/1"), task("Mine stone and copper", "1/2")])
    K.eq(str(Wid.shapeOf("Quest", m7, lay)), sh, "Q33 progress 6/10 -> 7/10 (same rows) = the same shape (a plain .Text set)")
    m8 = model(LONG_H, "3 / 24", [task("Chop 10 logs", "6/10", 0.6, LONG_W, 3), task(LONG_T, "0/1"), task("Mine stone and copper", "0/2")])
    K.check(str(Wid.shapeOf("Quest", m8, lay)) != sh, "Q33 the tracked task needs fewer rows -> another shape (re-send)")
    big = wdef("Quest")
    big.scale = 50
    want = str(m[0]) + "|w" + "".join(str(int(Wid.qN(m, 50, k))) for k in ("H", "W0", "N0", "N1", "N2"))
    K.eq(str(Wid.shapeOf("Quest", m, big)), want, "Q33 shapeOf counts the rows at the layout's size (50 %)")
    K.eq(str(Wid.shapeOf("Quest", s, lay)).split("|w")[0], str(s[0]), "Q33 sample keeps its own shape first")
    hid = Wid.questModelOf(None)
    K.eq(str(Wid.shapeOf("Quest", hid, lay)), str(hid[0]), "Q33 hidden (Q0) -> the bare shape")
    ab = JArray(String)([String("A0")] + [None] * 13)
    K.eq(str(Wid.shapeOf("Abilities", ab, wdef("Abilities"))), "A0", "Q33 another widget -> its model shape unchanged")
    K.check(Wid.shapeOf("Quest", None, lay) is None, "Q33 no model -> null (as mm[0] never was)")
    # ---- 8. the feed's fitText still cuts (its fixed one-line cards, unchanged)
    K.check(str(Wid.fitText("a" * 200, 100, 14, True)).endswith("..."), "Q33 fitText (feed cards) still cuts")
    K.save()


EXPECT = {
    "Widgets": ["+m qLines", "+m qN", "+m qWrap", "+m shapeOf", "~m questBody", "~m questH", "~m questPairs"],
    "HudMain": ["~m build", "~m fill"],
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
}

if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD, PKG, SCRATCH, EXPECT, [], [("q33", run_q33)], os.path.abspath(__file__))
