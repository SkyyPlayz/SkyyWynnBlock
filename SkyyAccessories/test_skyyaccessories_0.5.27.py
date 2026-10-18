"""Harness for SkyyAccessories 0.5.27 (tools/accessories_0_5_27_patch.py = the Furnace Charm collection gate; Skyy docs/answered/gear.md "you unlock
the charm when both iron and copper reach collection 3"). Build first:
    python tools/accessories_0_5_27_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.27.py
    python SkyyAccessories/test_skyyaccessories_0.5.27.py [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.26 -> 0.5.27: no class added / removed; only the listed members differ; no asset / lang file changes (manifest only)
  FA   0.5.25's charm ASSETS phase on this jar (six items valid, icons, names, tier tags)
  F    0.5.25's charm phase on this jar = NO coll:fn:tierup in the bridge: every old craft / upgrade / lock behaves as before
  G    THE GATE, executed (stub coll:fn:tierup answers):
         G1 no SkyyCollections: gate() null, no requirement line, T1 CAN CRAFT (old behaviour)
         G2 each step I .. V: "0|..." = LOCKED with the red line "<Name> collection III need : have", no "Locked - " sentence, the click
            refuses and uses nothing; "1|..." = the green line, the craft / in-place upgrade goes through; the token asked = charm.furnace:<alloy
            of that step> (Bronze for I - Electrum has none), with the player's UUID
         G3 a malformed / short / null answer = open (old behaviour); Eternal Flame never asks coll:fn:tierup
         G4 an owned charm stays: every gate locked again -> the T5 in Void Charms still smelts (acc:smelt 5|50|75|0), unequip + equip work,
            a spare charm in the inventory is untouched, only the NEXT step's row is locked
         G5 the Craft page markup: #SkyyAccCr<k>Rq is 0 high without a line, CR_RQ_H high with one, its text = the requirement line
  0.5.22 / 0.5.23 phases on the new jar: power, retire, rows, page, client, live
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

_sp = importlib.util.spec_from_file_location("acc_h525", os.path.join(HERE, "test_skyyaccessories_0.5.25.py"))
T25 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T25)
T22, T23 = T25.T22, T25.T23
import skyyonce_harness as OH
HK.run_compare = OH.compare_allowing(lambda n: False)          # no asset may change 0.5.26 -> 0.5.27 (manifest.json is always allowed)

VERSION = "0.5.27"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.26.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc27", "h")))
PKG = T22.PKG
FC, COST = T25.FC, T25.COST
ALLOYS = ["Bronze", "Dusk", "Azurvane", "Cinder", "Lumen"]
NAMES = T25.NAMES
EXPECT = {
    "AccCharm": ["+m gate", "+m gateLock", "~m lockOf"],
    "AccCraft": ["+f RED", "~m lineRow"],
    "AccPage": ["~m buildCraft"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup"],          # the version texts
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


# ======================================================================================== G: the gate, executed
def run_gate(out, jar, scratch, _home):
    K = HK.Child(out)
    M = T22.m18()
    W = M.World(os.path.join(scratch, "g"))
    C, D, A, Ch = W.Craft, W.Defs, W.Acc, W.J("AccCharm")
    from jpype import JClass, JImplements, JOverride, JShort
    for iid in FC:
        W.item(iid, 1, 900)
    mats = sorted(set(m for c in COST for m, _q in c))
    for m in mats:
        W.item(m, 1000, 0)
    VOID = {"n": {}, "owe": {}, "paused": False, "short": 0, "calls": []}
    _keep = M.void_bridge(W, VOID)
    put = [("s", i, m, sum(q for c in COST[:5] for mm, q in c if mm == m)) for i, m in enumerate(mats) if any(mm == m for c in COST[:5] for mm, _q in c)]
    put.append(("s", 30, FC[1], 1))          # a spare Furnace Charm II in the inventory (never counts, never touched)
    inv = W.inv(put=put)
    p, pr, U = W.player(inv, "Gate")
    k = str(U)
    key = "acc:smelt:%s" % U
    RED, GREEN = str(C.RED), str(C.GREEN)

    def sv():
        return "|".join(str(W.bridge.get(key)).split("|")[:4])

    def rows(sub=2):
        out_ = []
        for e in C.rowsFor(U, k, p, sub):
            ri = [str(x) for x in C.lineRow(U, k, p, e)]
            if ri[0].startswith("Skyy_Charm_"):
                out_.append(ri)
        return out_

    def craft(t):
        return str(C.craft(pr, None, None, p, U, k, FC[t - 1] + "_Recipe_SkyyCharm"))

    def charms():
        return sorted([x for x in W.bag(U) if x and x.startswith("Skyy_Charm_")])

    ANS = {}
    CALLS = []

    @JImplements("java.util.function.Function")
    class TierUp(object):
        @JOverride
        def apply(self, a):
            CALLS.append((str(a[0]), str(a[1])))
            return ANS.get(str(a[1]))

    def recipe(t):
        return Ch.recipe(FC[t - 1] + "_Recipe_SkyyCharm")

    # G1 no SkyyCollections
    r0 = rows()
    K.check(len(r0) == 1 and r0[0][0] == FC[0] and r0[0][2] == "NORMAL - CAN CRAFT" and r0[0][7] == "" and len(r0[0]) == 9,
            "G1 no coll:fn:tierup: T1 CAN CRAFT, no requirement line (old behaviour): %s" % r0)
    K.check(all(Ch.gate(U, recipe(t)) is None and Ch.lockOf(U, recipe(t)) is None for t in range(1, 6)), "G1 gate() / lockOf() null for steps I .. V")
    tu = TierUp()
    W.bridge.put("coll:fn:tierup", tu)
    # G2 each step
    for t in range(1, 6):
        tok = "charm.furnace:" + ALLOYS[t - 1]
        nm = NAMES[t - 1]
        ANS.clear()
        ANS[tok] = "0|Lead|Lead|3|500|312"
        del CALLS[:]
        v = rows()
        s0, b0, sv0 = W.slots(inv), W.bag(U), sv()
        r = craft(t)
        line = "Lead collection III 500 : 312"
        K.check(len(v) == 1 and v[0][0] == FC[t - 1] and v[0][2].endswith(" - LOCKED") and v[0][7] == line and v[0][8] == RED and "Locked - " not in v[0][4],
                "G2 %s gate not met: LOCKED, the red line %r, no 'Locked -' sentence: %s" % (nm, line, v))
        K.check(r == "%s is locked - needs %s" % (nm, line) and W.slots(inv) == s0 and W.bag(U) == b0 and sv() == sv0,
                "G2 %s: the click refuses, nothing used: %s" % (nm, r))
        K.check(CALLS and all(c == (str(U), tok) for c in CALLS), "G2 %s asks %s with the player's UUID: %s" % (nm, tok, sorted(set(CALLS))))
        ANS[tok] = "1|Copper|Copper|3|500|900"
        v = rows()
        r = craft(t)
        ok = ("crafted %s" % nm) if t == 1 else ("upgraded to %s in your Void Charms" % nm)
        K.check(v[0][7] == "Copper collection III 500 : 900" and v[0][8] == GREEN and ("CAN CRAFT" in v[0][2] or "CAN UPGRADE" in v[0][2]),
                "G2 %s gate met: the green line, %s: %s" % (nm, v[0][2], v[0][7]))
        K.check(r.startswith(ok) and charms() == [FC[t - 1]], "G2 %s: made / upgraded in place: %s / %s" % (nm, r, charms()))
        if t == 1:
            K.check(not any("Electrum" in c[1] for c in CALLS), "G2 Electrum has no token of its own (it smelts with step I = Bronze's)")
    K.eq(sv(), "5|50|75|0", "G2 after V: acc:smelt 5|50|75|0")
    # G3 malformed answers + Eternal Flame
    ANS.clear()
    for bad in ("garbage", "0|Lead", "2|a|b|3|1|0", None):
        ANS["charm.furnace:Bronze"] = bad
        K.check(Ch.gate(U, recipe(1)) is None and Ch.lockOf(U, recipe(1)) is None, "G3 answer %r = open (old behaviour)" % (bad,))
    ANS["charm.furnace:Bronze"] = "0|Iron|Iron|x|500|1"
    K.eq(str(Ch.lockOf(U, recipe(1))), "needs Iron collection 500 : 1", "G3 a bad tier number still locks (the answer's 0) with no numeral")
    del CALLS[:]
    re_ = Ch.recipe(FC[5] + "_Recipe_SkyyCharm")
    K.check(Ch.gate(U, re_) is None and "Charcoal collection" in str(Ch.lockOf(U, re_)) and not CALLS,
            "G3 Eternal Flame: no coll:fn:tierup call, its own Charcoal lock unchanged: %s" % Ch.lockOf(U, re_))
    # G4 an owned charm stays
    for t in range(1, 6):
        ANS["charm.furnace:" + ALLOYS[t - 1]] = "0|Iron|Iron|3|500|0"
    A.publish(U)
    K.eq(sv(), "5|50|75|0", "G4 every gate locked: the T5 in Void Charms still smelts")
    idx = W.bag(U).index(FC[4])
    K.eq(str(A.unequipK(U, k, idx)), FC[4], "G4 unequip works")
    K.eq((str(A.equipK(U, k, FC[4])), sv()), ("", "5|50|75|0"), "G4 equip back works, acc:smelt back")
    K.check(W.count(inv, FC[1]) == 1, "G4 the spare Furnace Charm II in the inventory is untouched")
    v = rows()
    K.check(len(v) == 1 and v[0][0] == FC[5], "G4 only the NEXT step's row shows (Eternal Flame), no owned step is listed: %s" % [x[0] for x in v])
    K.check(str(D.fcSmelt(W.JArray(JClass("java.lang.String"))(1))) == "0|0|0|0", "G4 fcSmelt unchanged (empty bag = 0|0|0|0)")
    # G5 the Craft page markup
    U2p = W.player(W.inv(put=[("s", 0, "Ingredient_Bar_Copper", 32), ("s", 1, "Ingredient_Bar_Iron", 32)]), "Gate2")
    p2, pr2, U2 = U2p
    Page = W.J("AccPage")
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def page_text(u, pl):
        pg = W.us.allocateInstance(Page.class_)
        for f in W.jclass_fields(Page):
            if str(f.getName()) == "key":
                f.setAccessible(True)
                f.set(pg, str(u))
            if str(f.getName()) == "craftSub":
                f.setAccessible(True)
                f.setInt(pg, 2)
        b = UCB()
        pg.buildCraft(b, UEB(), u, pl)
        txt = []
        for c in b.getCommands():
            cl = c.getClass()
            while cl is not None:
                for f in cl.getDeclaredFields():
                    if not W.Mod.isStatic(f.getModifiers()):
                        f.setAccessible(True)
                        txt.append(str(f.get(c)))
                cl = cl.getSuperclass()
        return "\n".join(txt)
    ANS["charm.furnace:Bronze"] = "0|Iron|Iron|3|500|7"
    t1 = page_text(U2, p2)
    K.check("Rq { Anchor: (Width:" in t1 and "Iron collection III 500 : 7" in t1, "G5 a locked T1 row draws #..Rq with the requirement line")
    import re
    hs = re.findall(r"Label #SkyyAccCr\d+Rq \{ Anchor: \(Width: \d+, Height: (\d+)\)", t1)
    K.check(hs and int(hs[0]) > 0, "G5 ... the line has its height: %s" % hs)
    W.bridge.remove("coll:fn:tierup")
    t2 = page_text(U2, p2)
    hs2 = re.findall(r"Label #SkyyAccCr\d+Rq \{ Anchor: \(Width: \d+, Height: (\d+)\)", t2)
    K.check(hs2 and all(int(h) == 0 for h in hs2), "G5 without a line every #..Rq is 0 high: %s" % hs2[:4])
    K.notes.append("G: the gate phase ran to the end - %d checks ok, %d failed" % (K.ok, len(K.fails)))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("fassets", T25.run_fassets), ("charm", T25.run_charm), ("gate", run_gate), ("power", T22.run_power), ("retire", T22.run_retire),
                   ("rows", T22.run_rows), ("page", T22.run_page), ("client", T23.run_client), ("live", T22.run_live)],
           script=__file__, live=(T22.LIVE_DIR, "Skyy_SkyyAccessories"))
