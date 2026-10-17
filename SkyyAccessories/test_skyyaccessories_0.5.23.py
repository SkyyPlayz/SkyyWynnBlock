"""Harness for SkyyAccessories 0.5.23 (HOTFIX: the #SkyyAccGrid.Slots client disconnect; tools/accessories_0_5_23_patch.py).
Build first: python tools/accessories_0_5_23_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.23.py

    python SkyyAccessories/test_skyyaccessories_0.5.23.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.22 -> 0.5.23: AccPage + isOpen, ~ build / clearGrid / handleDataEvent; the plugin's version text; non-class: manifest only
  0.5.22's phases on the new jar (test_skyyaccessories_0.5.22.py): assets, power, retire, rows, page, live
  G    THE CLIENT MODEL on the real engine page manager: every packet the server sends is applied to a model of the client's page (a full
       page replaces the element ids, appends add theirs) and EVERY Set / binding selector of EVERY packet must name an element of the
       markup the client has at that moment (= what the real client checks before it disconnects). Walked: first open with no profile
       data (empty bag), BAG with each filter, a selection, CRAFT with each sub, POWER, a full bag (60), then from BAG / CRAFT / POWER:
       Close, a hub row-1 click (Market), a row-2 tab, our own tab; a profile switch; then the page REPLACED by another page (Skyy's
       Market click) and clearGrid / a click on the old page -> NOTHING is sent to the client; the old bag item's open (AccPageFactory).
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_STRICT_COMPARE = HK.run_compare
_sp = importlib.util.spec_from_file_location("acc_h522", os.path.join(HERE, "test_skyyaccessories_0.5.22.py"))
T22 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T22)
HK.run_compare = _STRICT_COMPARE          # 0.5.23 changes no asset: the non-class entries may differ in manifest.json only

VERSION = "0.5.23"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.22.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc0523", "acc")))
PKG = T22.PKG
OMNI = T22.OMNI
EXPECT = {
    "AccPage": ["+m isOpen", "~m build", "~m clearGrid", "~m handleDataEvent"],
    "SkyyAccessoriesPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],     # the version text in Server Setup
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


def run_client(out, jar, scratch, _home):
    from jpype import JClass, JShort
    import hub_tab_kit as HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Paths, UUID, IS = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    home = os.path.join(scratch, "g")
    os.makedirs(os.path.join(home, "bags"), exist_ok=True)
    J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
    J("AccPower").FILE = Paths.get(os.path.join(home, "power.properties"))
    J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
    J("AccPower").load()
    J("AccCraft").LOGF = Paths.get(os.path.join(home, "crafts.log"))
    J("AccHubOpen").register()
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-0000000ac0f2"), "Gridder")
    u1 = P1.pr.getUuid()
    E.bridge.put("profile:epoch:%s" % u1, JClass("java.lang.Long")(1))

    # ---- the client model: the element ids of the page the client shows, fed by every packet sent to P1
    Arr = JClass("java.lang.reflect.Array")
    model = {"ids": set(), "seen": 0, "bad": [], "pages": 0, "updates": 0, "shape": None}

    def fields(o):
        c, out_ = o.getClass(), []
        while c is not None and str(c.getName()) != "java.lang.Object":
            for f_ in c.getDeclaredFields():
                if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                    continue
                f_.setAccessible(True)
                out_.append((str(f_.getName()), f_.get(o)))
            c = c.getSuperclass()
        return out_

    def cmds_in(p):
        cm, evs, clear = [], [], None
        for n_, v_ in fields(p):
            if v_ is None:
                continue
            if n_ == "clear":
                clear = bool(v_)
            if v_.getClass().isArray() and not v_.getClass().getComponentType().isPrimitive():
                comp = str(v_.getClass().getComponentType().getSimpleName())
                for i in range(int(Arr.getLength(v_))):
                    x = Arr.get(v_, i)
                    if x is None:
                        continue
                    d = dict((a, None if b is None else str(b)) for a, b in fields(x))
                    (cm if "Command" in comp else evs).append(d)
        return cm, evs, clear

    def feed(what):
        pk = E.sent(P1)
        for p in pk[model["seen"]:]:
            kind_ = str(p.getClass().getSimpleName())
            if kind_ not in ("CustomPage", "SetPage", "UpdatePage", "CustomPageUpdate"):
                continue
            cm, evs, clear = cmds_in(p)
            if model["shape"] is None and cm:
                model["shape"] = (kind_, sorted(cm[0].keys()), clear)
            if clear or kind_ in ("CustomPage", "SetPage") and clear is None:
                model["ids"] = set()
            if clear:
                model["pages"] += 1
            else:
                model["updates"] += 1
            for c in cm:
                ty, sel, txt = str(c.get("type")), c.get("selector"), c.get("text")
                if "Append" in ty or "Insert" in ty:
                    if sel and sel.lstrip("#").split(" ")[-1] not in model["ids"]:
                        model["bad"].append("%s: append into %s (not in the client's markup)" % (what, sel))
                    if txt:
                        model["ids"] |= set(m.group(2) for m in DECL_RE.finditer(txt))
                elif ty in ("Set", "Remove", "Clear"):
                    if sel is None:
                        continue
                    el = sel.lstrip("#").split(" ")[-1].split(".")[0]
                    if el not in model["ids"]:
                        model["bad"].append("%s: %s %s (not in the client's markup)" % (what, ty, sel))
            for e in evs:
                sel = e.get("selector")
                if sel and sel.lstrip("#").split(".")[0] not in model["ids"]:
                    model["bad"].append("%s: binding %s (not in the client's markup)" % (what, sel))
        model["seen"] = len(pk)
        E.pump(P1)

    def ok(what):
        bad = [b_ for b_ in model["bad"] if b_.startswith(what + ":")]
        K.check(not bad, "%s: every command / binding the client got names an element it has (%s)" % (what, bad[:3]))

    def open_():
        K.check(bool(J("AccHubOpen")().apply(u1)), "open: the tab's open Function opens Void Charms")
        feed("open")
        return E.pg(P1)

    def click(pg, a, extra="", what=None):
        what = what or a
        pg.handleDataEvent(P1.ref, P1.st, '{"a":"%s"%s}' % (a, extra))
        feed(what)
        ok(what)
        return E.pg(P1)

    # FIRST OPEN, no profile data, empty bag
    pg = open_()
    ok("open")
    K.check(model["shape"] is not None and model["pages"] >= 1 and "SkyyAccGrid" in model["ids"],
            "G the first open is one full page and its markup holds #SkyyAccGrid (%s, pages %d)" % (model["shape"], model["pages"]))
    K.check(int(pg.cells) == 100, "G BAG drawn: cells 100 (%s)" % pg.cells)
    for i in range(4):
        click(pg, "fl:%d" % i, what="BAG filter %d (empty bag)" % i)
    # a few accessories + one in the inventory, a selection
    Acc = J("AccStore")
    k1 = str(u1)
    Acc.putK(u1, k1, 0, "Skyy_Talisman_Speed_Epic")
    Acc.putK(u1, k1, 1, OMNI)
    P1.slots["storage"].getInventory().addItemStackToSlot(JShort(0), IS("Skyy_Talisman_Vitality_Rare", 1))
    for i in range(4):
        click(pg, "fl:%d" % i, what="BAG filter %d" % i)
    click(pg, "g", ',"SlotIndex":0', what="BAG select in the bag")
    click(pg, "ig", ',"SlotIndex":0', what="BAG select in the inventory")
    click(pg, "g", ',"SlotIndex":59', what="BAG an empty cell")
    # CRAFT with each sub, POWER, then the clicks that LEAVE the page from a grid-less view (the 0.5.22 crash)
    for view, act in (("CRAFT", "tb:craft"), ("POWER", "tb:power")):
        for leave in ("cl", "hub:close", "hub:h:market", "hub:skills", "hub:h:character"):
            pg = E.pg(P1)
            if pg is None or not str(pg.getClass().getName()).endswith("AccPage"):
                pg = open_()
            click(pg, act, what="%s view" % view)
            K.check(int(pg.cells) == 0, "G %s view: cells 0 - no grid on this view (%s)" % (view, pg.cells))
            if view == "CRAFT":
                for s in range(3):
                    click(pg, "st:%d" % s, what="CRAFT sub %d" % s)
            n0 = len(E.sent(P1))
            click(pg, leave, what="%s then %s" % (view, leave))
    # from BAG: Close / Market / a row-2 tab / our own tab (clearGrid must still empty the grids there)
    for leave in ("hub:accessories", "hub:h:market", "hub:skills", "cl"):
        pg = E.pg(P1)
        if pg is None or not str(pg.getClass().getName()).endswith("AccPage"):
            pg = open_()
        click(pg, "tb:bag", what="BAG view")
        click(pg, leave, what="BAG then %s" % leave)
    # a FULL bag (60)
    ids = [str(x) for x in J("AccDefs").ALL] if hasattr(J("AccDefs"), "ALL") else []
    pg = E.pg(P1) if E.pg(P1) is not None else open_()
    n = 0
    for i in range(60):
        try:
            Acc.putK(u1, k1, i, ids[i % len(ids)] if ids else "Skyy_Talisman_Speed_Epic")
            n += 1
        except Exception:
            break
    click(pg, "fl:0", what="BAG full bag")
    click(pg, "tb:power", what="POWER (full bag)")
    click(pg, "tb:bag", what="BAG again (full bag)")
    # a profile switch (another storage key) while the page is open
    E.bridge.put("profile:epoch:%s" % u1, JClass("java.lang.Long")(2))
    click(pg, "un", what="BAG after a profile switch")
    # THE PAGE REPLACED (Skyy's Market click opened another page): the old page sends nothing any more
    click(pg, "tb:bag", what="BAG before the hand-over")
    K.check(int(pg.cells) == 100, "G BAG: cells 100 before the hand-over")
    other = J("AccPage")(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, other)
    feed("the other page")
    ok("the other page")
    K.check(E.same(E.pg(P1), other) and not E.same(E.pg(P1), pg), "G the old page is not the open page any more")
    K.check(not bool(pg.isOpen()) and bool(other.isOpen()), "G isOpen: the old page false, the new one true")
    n0 = len(E.sent(P1))
    pg.clearGrid()
    K.check(len(E.sent(P1)) == n0 and int(pg.cells) == 0, "G clearGrid on the REPLACED page sends nothing (%d packets)" % (len(E.sent(P1)) - n0))
    pg.cells = 100
    n0 = len(E.sent(P1))
    pg.handleDataEvent(P1.ref, P1.st, '{"a":"hub:h:market"}')
    feed("old page: a late row-1 click")
    K.check(len([p for p in E.sent(P1)[n0:] if "Page" in str(p.getClass().getSimpleName())]) == 0,
            "G a late hub click on the replaced page sends no page packet")
    ok("old page: a late row-1 click")
    # the old bag item's right-click (OpenCustomUIInteraction -> AccPageFactory -> a new AccPage): the same page, the same checks
    fp = J("AccPageFactory")().apply(P1.pr)
    K.check(str(fp.getClass().getName()) == PKG + "AccPage", "G the old bag item's factory makes a Void Charms page")
    P1.pm.openCustomPage(P1.ref, P1.st, fp)
    feed("old bag item open")
    ok("old bag item open")
    click(fp, "tb:craft", what="old bag item: CRAFT")
    click(fp, "cl", what="old bag item: Close from CRAFT")
    K.check(not model["bad"], "G NO command named a missing element in the whole walk (%d full pages, %d updates): %s"
            % (model["pages"], model["updates"], model["bad"][:5]))
    K.check(model["updates"] >= 4, "G the walk saw the grid-emptying updates (%d)" % model["updates"])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[], removed=[],
           phases=[("assets", T22.run_assets), ("power", T22.run_power), ("retire", T22.run_retire), ("rows", T22.run_rows),
                   ("page", T22.run_page), ("client", run_client), ("live", T22.run_live)],
           script=__file__, live=(T22.LIVE_DIR, "Skyy_SkyyAccessories"))
