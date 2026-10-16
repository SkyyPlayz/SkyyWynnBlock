"""Harness for SkyyGear 0.3.10 (tools/gear_0_3_10_patch.py header) = the 0.3.9 harness's children run on the 0.3.10 jar + H310 (one booted engine):
    python tools/gear_0_3_10_patch.py && python SkyyGear/build_skyygear_0.3.10.py
    python SkyyGear/test_skyygear_0.3.10.py [--keep] [--only assets,h310,h39,verify,h38,h37,g36,snd,till,life,audit]

  S310 non-class entries 0.3.9 -> 0.3.10: the same entries, only manifest.json changes
  H310 ONE booted engine (the 0.3.5 life setup), the REAL pages on a player whose PageManager is FakePM10 (counts every page packet the engine
       would send: updateLegacyCustomPage = rebuild / sendUpdate, setPage = close) and whose PlayerRef points at the player's Ref:
       R  RAPID CLICKS on the REAL Tools page: 5 clicks of the same +1 within 100 ms = 1 level bought, 5 answers (1 packet each, 4 empty);
          5 clicks each on the redrawn page = as many levels as the points allow, never below 0 free, every click answered once; +1 at max,
          no points, the wrong tier (Vein Mine on a Crude pickaxe), Reset without / with coins (arm, pay, a double click on the same Reset never
          pays), an old token-less click inside 400 ms (dropped, answered), empty / malformed / unknown clicks, a tab click whose command
          fails, a stale click on a page that is no longer open (no packet)
       T  TIER UP on the Tools tab: Copper Pickaxe for 25 Copper Ingots (the Anvil's GearUp.upgrade: same slot, ingots gone, the line + the
          button state), refused without ingots / below Mining 5 (nothing used), a same-token double click tiers up once
       M  MAKE MULTITOOL (the Multitools jar copied to scratch): before rebirth 1 greyed with the rebirth line; after it the plain Iron pickaxe
          + hatchet pair is named and merged (GearMerge.merge), the lifelong pickaxe never; a changed pair is refused; no Multitool tab beside
          Tools; /multitool opens the Tools tab
       P  THE POLE ROW: no pole granted = "From Marlow's fishing quest at the hub pier" (never "Arrives when ...")
       A  ALWAYS ANSWER on the other Smithing pages (Craft, Anvil / Identify, Multitool, the old Identify page): empty, malformed, unknown,
          guarded and failing clicks = exactly one packet each; every Tools page rendered here validates (the 0.3.9 client-side check)
  H39 / VERIFY / H38 / H37 / G36 / SND / TILL / L35 / AA  the 0.3.9 harness's children on the 0.3.10 jar
Scratch: tools/dev/scratch/gear0310/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.10"
V39 = "0.3.9"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0310")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J39 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V39))                       # read only
PKG = "com.skyy.gear."

# ---- the 0.3.9 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder
_H39 = os.path.join(HERE, "test_skyygear_0.3.9.py")
_T39 = open(_H39, encoding="utf-8").read()
_cut = _T39.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H39, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H39 = {"__name__": "skyygear_h39", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T39[:_cut], _H39 + " (library)", "exec"), H39)
sys.argv = _argv
H38 = H39["H38"]
H37, H36, H35, H = H38["H37"], H38["H36"], H38["H35"], H38["H"]
FAKE_DIR = H38["FAKE_DIR"]
FAKE_PKG = H38["FAKE_PKG"]
MT_SRC = os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")          # read only - copied into scratch
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S310
def run_assets310():
    ea, eb = entries(J39), entries(JAR)
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(sorted(ea) == sorted(eb) and changed == ["manifest.json"],
          "S310: 0.3.9 -> 0.3.10: the same entries, only manifest.json changed among non-class files: %s / added %s gone %s"
          % (changed, sorted(set(eb) - set(ea))[:3], sorted(set(ea) - set(eb))[:3]))
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.10"' in man and "Make multitool" in man and "every click answered" in man, "S310: the manifest names the round")


# ====================================================================================================== F: + FakePM10
def run_mkfake10(out_dir):
    H39["run_mkfake9"](out_dir)
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    PMc = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
    PGc = "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
    pm = cp.makeClass(FAKE_PKG + ".FakePM10")
    pm.setSuperclass(cp.get(PMc))
    for f_ in ("public static int packets;", "public static int closes;", "public static int opens;", "public static java.lang.Object cur;",
               "public static java.lang.Object last;", "public static java.lang.Object lastPacket;"):
        pm.addField(CtField.make(f_, pm))
    pm.addConstructor(CtNewConstructor.make("public FakePM10() { super(); }", pm))
    pm.addMethod(CtNewMethod.make("public void updateLegacyCustomPage(com.hypixel.hytale.protocol.packets.interface_.CustomPage p) { packets = packets + 1; lastPacket = p; }", pm))
    pm.addMethod(CtNewMethod.make("public void setPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, com.hypixel.hytale.protocol.packets.interface_.Page p) { closes = closes + 1; cur = null; }", pm))
    pm.addMethod(CtNewMethod.make("public " + PGc + " getCustomPage() { return (" + PGc + ") cur; }", pm))
    pm.addMethod(CtNewMethod.make("public void openCustomPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, " + PGc + " p) { last = p; opens = opens + 1; }", pm))
    pm.writeFile(out_dir)
    print("F+. FakePM10 written")


# ====================================================================================================== H310
def run_h310(out):
    if os.path.isfile(MT_SRC):
        shutil.copyfile(MT_SRC, os.path.join(SCRATCH, "packs", "Multitools-1.2.9.jar"))
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h310(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H310: the phase raised: %s" % traceback.format_exc()[-1500:])
    K.save()


def _h310(L, K):
    from jpype import JClass, JInt, JShort, JLong, JObject, JString, JImplements, JOverride
    import skyyui as SUI
    br, Gear, Cfg, Data, Roll, Smith = L["br"], L["Gear"], L["Cfg"], L["Data"], L["Roll"], L["Smith"]
    mkinv, world, PR1, U1, stack, doc, skills, apply, logs, COINS = (L["mkinv"], L["world"], L["PR1"], L["U1"], L["stack"], L["doc"], L["skills"],
                                                                     L["apply"], L["logs"], L["COINS"])
    us, jf, ITEM = L["us"], L["jf"], L["ITEM"]
    P = lambda n: JClass(PKG + n)
    Ui, Up, LL, Life, Merge, Stamp = P("GearUi"), P("GearUp"), P("GearLL"), P("GearLife"), P("GearMerge"), P("GearStamp")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Integer_ = JClass("java.lang.Integer")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    FPM = JClass(FAKE_PKG + ".FakePM10")

    # ---- the Multitools items (a scratch copy of the pack) so the Make multitool row shows
    mtj = os.path.join(SCRATCH, "packs", "Multitools-1.2.9.jar")
    mt_ok = False
    if os.path.isfile(mtj):
        try:
            L["addpack"](mtj, "InkBlindCat:Multitools")
        except Exception as e_:
            K.notes.append("H310: the Multitools pack did not load: %s" % str(e_)[:200])
        mt_ok = bool(Merge.loaded())
    K.notes.append("H310: Multitools items loaded: %s" % mt_ok)

    # ---- the client-side check of one rendered page (the 0.3.9 harness's rules)
    ALIGN, LAYOUTS, ELEM_RE, strip_q = H39["ALIGN"], H39["LAYOUTS"], H39["ELEM_RE"], H39["strip_q"]

    def cmds(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("type", "selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            out_.append(vals)
        return out_

    def evs(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            try:
                out_.append(str(getattr(e_, "selector")))
            except Exception:
                out_.append(None)
        return out_

    def evdata(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            got = ""
            for f_ in ("data", "eventData"):
                try:
                    v_ = getattr(e_, f_)
                    if v_ is not None:
                        got = str(v_)
                        break
                except Exception:
                    pass
            out_.append(got or str(e_))
        return out_

    def setv(cl, sel):
        return [(v["text"] or "") + (v["data"] or "") for v in cl if v["selector"] == sel]

    def pybad(d):
        try:
            SUI.check_markup(d, kit_paths=False)
        except ValueError as e_:
            return "kit: " + str(e_)[:200]
        bare = strip_q(d)
        for m_ in re.finditer(r"(Horizontal|Vertical)Alignment:\s*(\w+)", bare):
            if m_.group(2) not in ALIGN:
                return "%sAlignment %s" % (m_.group(1), m_.group(2))
        for m_ in re.finditer(r"LayoutMode:\s*(\w+)", bare):
            if m_.group(1) not in LAYOUTS:
                return "LayoutMode " + m_.group(1)
        for m_ in re.finditer(r'ItemId: "([^"]*)"', d):
            if ITEM.getAssetMap().getAsset(m_.group(1)) is None:
                return "ItemId %s is no item" % m_.group(1)
        if re.search(r"(Width|Height):\s*-", bare):
            return "negative size"
        return None

    def validate(cl, ev):
        probs, known = [], set()
        for v in cl:
            t_ = v["text"] if v["text"] and "{" in v["text"] else (v["data"] if v["data"] and "{" in v["data"] else None)
            if t_ is not None and "Set" not in (v["type"] or ""):
                sel = v["selector"]
                if sel not in (None, "None", "") and sel.lstrip("#") not in known:
                    probs.append("append into #%s before it exists" % sel)
                why = pybad(t_)
                if why:
                    probs.append("%s: %s | %s" % (sel, why, t_[:140]))
                if Ui.bad(t_) is not None:
                    probs.append("GearUi.bad: %s" % Ui.bad(t_))
                for m_ in ELEM_RE.finditer(strip_q(t_)):
                    if m_.group(2):
                        if m_.group(2) in known:
                            probs.append("#%s created twice" % m_.group(2))
                        known.add(m_.group(2))
            elif v["selector"] and "." in v["selector"]:
                tid = v["selector"].lstrip("#").split(".")[0]
                if tid not in known:
                    probs.append("set on #%s which does not exist" % tid)
        for e_ in ev:
            if e_ and e_.lstrip("#") not in known:
                probs.append("event on %s which does not exist" % e_)
        return probs

    def child_sum(cl, parent):
        tot = 0
        for v in cl:
            t_ = v["text"] if v["text"] and "{" in v["text"] else None
            if t_ is None or v["selector"] != parent:
                continue
            m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", t_)
            if m_:
                h_ = re.search(r"Height: (\d+)", m_.group(1))
                tot += int(h_.group(1)) if h_ else 0
        return tot

    # ---- a player world whose PageManager counts packets and whose PlayerRef points at its Ref (the real rebuild / sendUpdate run)
    inv, cs = mkinv()
    ref, st, ch, pl = world(inv, cs, PR1)
    pm_field = None
    k_ = PLA.class_
    while k_ is not None and pm_field is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PMC.class_:
                f_.setAccessible(True)
                pm_field = f_
        k_ = k_.getSuperclass()
    pm_field.set(pl, us.allocateInstance(FPM.class_))
    jf(PRc, "entity").set(PR1, ref)
    K.check(PR1.getReference() is not None and pl.getPageManager() is not None and str(pl.getPageManager().getClass().getName()).endswith("FakePM10"),
            "H310 setup: the player's PageManager counts packets, the PlayerRef reaches the player")

    rendered = []

    def render(pg_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(ref, ub_, ue_, st)
        cl, ev = cmds(ub_), evs(ue_)
        rendered.append((cl, ev))
        txt = chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl)
        return txt, cl, ev, evdata(ue_)

    def click(pg_, data):
        """one click through the page's REAL handler; returns the packets + closes it sent"""
        p0, c0 = int(FPM.packets), int(FPM.closes)
        pg_.handleDataEvent(ref, st, data)
        return int(FPM.packets) - p0 + int(FPM.closes) - c0

    def tokOf(pg_):
        return int(pg_.tok)

    # the lifelong tools arrive (the sweep), Mining 4 = 3 points
    COINS[0] = 10 ** 7
    skills(Mining=4, Foraging=4, Farming=4, Fishing=4)
    Life.sweep(PR1, inv, True)
    pk = str(Gear.pkey(U1))
    REG = LL.reg(pk)
    K.check(REG.getProperty("pickaxe.uid") is not None and REG.getProperty("pole.uid") is None,
            "H310 setup: the four lifelong tools arrived, no pole (it comes from Marlow): %s" % sorted(str(k) for k in REG.keySet() if str(k).endswith(".uid")))
    lp = P("LifePage")(PR1)
    FPM.cur = lp
    a0 = [int(Ui.ACK[0]), int(Ui.ACK[1])]
    n_open = click(lp, '{"a":"refresh"}')
    txt, cl, ev, ed = render(lp)
    K.check(n_open == 1 and ("buy:1:%d" % tokOf(lp)) in " ".join(ed) and ("reset:%d" % tokOf(lp)) in " ".join(ed) and ("up:%d" % tokOf(lp)) in " ".join(ed),
            "R0: Refresh = one rebuild packet; the +1 / Reset / Tier up buttons carry this build's token: %s" % [e for e in ed if ":" in e][:6])
    fort = lambda: int(LL.perkOf(LL.reg(pk), JInt(0), JInt(1)))
    free = lambda: int(LL.free(U1, LL.reg(pk), JInt(0)))
    # R1: 5 clicks of the SAME +1 (one page copy) within 100 ms
    t0 = tokOf(lp)
    f0, fr0 = fort(), free()
    ans = [click(lp, '{"a":"buy:1:%d"}' % t0) for _ in range(5)]
    K.check(fort() == f0 + 1 and free() == fr0 - 1 and ans == [1, 1, 1, 1, 1] and str(lp.info).startswith("+Fortune is level 1"),
            "R1: 5 clicks of the same +1 within 100 ms = ONE level (Fortune %d -> %d, free %d -> %d), every click answered by exactly one packet %s: %s"
            % (f0, fort(), fr0, free(), ans, lp.info))
    # R2: 5 clicks each on the redrawn page (each with the newest token) = as many levels as the points allow (2 left), never below 0
    ans2, infos = [], []
    for _ in range(5):
        ans2.append(click(lp, '{"a":"buy:1:%d"}' % tokOf(lp)))
        infos.append(str(lp.info))
    K.check(fort() == f0 + 3 and free() == 0 and ans2 == [1] * 5 and infos[1].startswith("+") and "you have 0 free" in infos[2] and "you have 0 free" in infos[4],
            "R2: 5 fast clicks on the redrawn page = 2 more levels (all 3 points), then 'costs 1 point - you have 0 free', each answered once %s: %s"
            % (ans2, infos))
    # R3: +1 at max (Mining 30 = 29 points; Fortune to 10, then one more)
    skills(Mining=30)
    for _ in range(10):
        click(lp, '{"a":"buy:1:%d"}' % tokOf(lp))
    a_max = click(lp, '{"a":"buy:1:%d"}' % tokOf(lp))
    txm, clm, evm, edm = render(lp)
    K.check(fort() == 10 and a_max == 1 and "top level" in str(lp.info) and any("Max" in x for x in setv(clm, "#SkyyGPk1B.Text")), "R3: +1 at Max = refused ('top level'), answered once: %s" % lp.info)
    # R4: the wrong tier: Vein Mine (perk 3) on a Crude pickaxe
    a_vein = click(lp, '{"a":"buy:3:%d"}' % tokOf(lp))
    K.check(a_vein == 1 and int(LL.perkOf(LL.reg(pk), JInt(0), JInt(3))) == 0 and str(lp.info).startswith("-"), "R4: Vein Mine on Crude = refused, answered once: %s" % lp.info)
    # R5: Reset without coins (arm, pay = refused), with coins (arm, pay), and a double click on the same Reset (never pays)
    COINS[0] = 0
    r_arm = click(lp, '{"a":"reset:%d"}' % tokOf(lp))
    armed_info = str(lp.info)
    r_pay = click(lp, '{"a":"reset:%d"}' % tokOf(lp))
    K.check(r_arm == 1 and r_pay == 1 and armed_info.startswith("=Click Reset again") and "A reset costs" in str(lp.info) and fort() == 10,
            "R5: Reset without coins: arm + pay = 'A reset costs ...', nothing reset, both answered once: %s | %s" % (armed_info, lp.info))
    COINS[0] = 10 ** 7
    lp.armK = JInt(-1)
    td = tokOf(lp)
    d1 = click(lp, '{"a":"reset:%d"}' % td)
    d2 = click(lp, '{"a":"reset:%d"}' % td)
    K.check(d1 == 1 and d2 == 1 and fort() == 10 and COINS[0] == 10 ** 7 and str(lp.info).startswith("=Click Reset again"),
            "R5b: a double click on the same Reset button = armed once, the copy pays nothing (coins %d), both answered" % COINS[0])
    r_ok = click(lp, '{"a":"reset:%d"}' % tokOf(lp))
    K.check(r_ok == 1 and fort() == 0 and COINS[0] < 10 ** 7 and str(lp.info).startswith("+All"), "R5c: Reset with coins = points back, coins taken, answered: %s" % lp.info)
    # R6: an old token-less click inside 400 ms: the second is dropped but answered
    lp.lastClick = JLong(0)
    o1 = click(lp, '{"a":"buy:1"}')
    o2 = click(lp, '{"a":"buy:1"}')
    K.check(o1 == 1 and o2 == 1 and fort() == 1, "R6: two token-less clicks inside 400 ms = one level, both answered (%d / %d)" % (o1, o2))
    # R7: empty / malformed / unknown / a failing tab command / sel / a stale token
    odd = [click(lp, d) for d in (None, "", "{}", '{"a":""}', "not json", '{"a":"zzz"}', '{"a":"buy:x:y"}', '{"a":"mode:0"}', '{"a":"mode:9"}',
                                   '{"a":"sel:1"}', '{"a":"sel:99"}', '{"a":"buy:1:%d"}' % (tokOf(lp) - 5), '{"a":"up"}', '{"a":"mt"}')]
    K.check(odd == [1] * len(odd), "R7: empty / malformed / unknown / tab / sel / stale-token / token-less up+mt clicks: exactly one packet each %s" % odd)
    # R8: a click on a page that is no longer the open page sends nothing more (a stale page's no-op)
    FPM.cur = None
    s_ = click(lp, '{"a":"buy:1:%d"}' % (tokOf(lp) - 3))
    FPM.cur = lp
    K.check(s_ == 0, "R8: a no-op click on a page that is no longer open sends no packet (%d)" % s_)
    K.check(int(Ui.ACK[1]) - a0[1] >= 40 and int(Ui.ACK[0]) - a0[0] >= 10, "R9: GearUi.ACK counted wrapped clicks %d / empty answers %d"
            % (int(Ui.ACK[1]) - a0[1], int(Ui.ACK[0]) - a0[0]))

    # R10 (review fix 1): a throw AFTER the token was used up (sel out of range on Reset) = one redraw with a line and a fresh token that works
    tb = tokOf(lp)
    lp.sel = JInt(99)
    lp.armK = JInt(-1)
    e1 = click(lp, '{"a":"reset:%d"}' % tb)
    ta_ = tokOf(lp)
    info_e = str(lp.info)
    lp.sel = JInt(0)
    f_b = fort()
    txe, cle, eve, ede = render(lp)
    e2 = click(lp, '{"a":"buy:1:%d"}' % tokOf(lp))
    K.check(e1 == 1 and info_e == "-Something went wrong - nothing was changed. Click Refresh." and fort() == f_b + 1 and ta_ != tb,
            "R10: a click that throws after its token was used = one redraw ('Something went wrong ... Click Refresh.'), new token %d -> %d, the next "
            "click works (Fortune %d -> %d): %s" % (tb, ta_, f_b, fort(), info_e))
    # R11 (review fix 2): two copies of the Tools page never share a token; copy A's click does nothing on copy B
    pA, pB = P("LifePage")(PR1), P("LifePage")(PR1)
    render(pA)
    render(pB)
    tA, tB = tokOf(pA), tokOf(pB)
    FPM.cur = pB
    f_c = fort()
    w11 = click(pB, '{"a":"buy:1:%d"}' % tA)
    seen = set()
    dup = 0
    for _ in range(50):
        render(pA)
        render(pB)
        for x_ in (tokOf(pA), tokOf(pB)):
            dup += 1 if x_ in seen else 0
            seen.add(x_)
    FPM.cur = lp
    K.check(tA != tB and w11 == 1 and fort() == f_c and dup == 0, "R11: tokens come from one counter: copy A %d / copy B %d, A's click on B buys nothing "
            "(answered), 100 builds of two copies never repeat a token (%d repeats)" % (tA, tB, dup))

    # ============================================================================ T: Tier up
    lp.sel = JInt(0)
    co = Up.cost("Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper")
    mid, mq = str(co[0][0]), int(co[1][0])
    skills(Mining=2)
    txt, cl, ev, ed = render(lp)
    ta = click(lp, '{"a":"up:%d"}' % tokOf(lp))
    at0 = LL.reg(pk).getProperty("pickaxe.uid")
    pos = Life.find(inv, pk, at0)
    K.check(ta == 1 and str(Stamp.at(inv, pos[0], pos[1]).getItemId()) == "Tool_Pickaxe_Crude" and str(lp.info).startswith("-"),
            "T1: Tier up below Mining 5 / without ingots = refused, nothing used, answered once: %s" % lp.info)
    skills(Mining=30)
    cs["storage"].setItemStackForSlot(JShort(20), stack(mid, mq))
    cs["storage"].setItemStackForSlot(JShort(21), stack(mid, mq))
    txt, cl, ev, ed = render(lp)
    tline = setv(cl, "#SkyyGPTier.Text")
    ok_btn = [v["text"] for v in cl if v["text"] and "#SkyyGPUp" in v["text"]]
    tt = tokOf(lp)
    u1 = click(lp, '{"a":"up:%d"}' % tt)
    u2 = click(lp, '{"a":"up:%d"}' % tt)
    pos = Life.find(inv, pk, at0)
    now_id = str(Stamp.at(inv, pos[0], pos[1]).getItemId()) if pos is not None else None
    left = int(Up.have(inv, mid))
    NCU = str(Gear.itemName("Tool_Pickaxe_Copper"))
    K.check(tline and NCU in tline[0] and ("(%d / %d)" % (mq, mq)) in tline[0] and ok_btn and "Tier up" in ok_btn[0]
            and now_id == "Tool_Pickaxe_Copper" and left == mq and u1 == 1 and u2 == 1 and (NCU + " now") in str(lp.info),
            "T2: Tier up = the Anvil's tier-up: line %s; Crude -> %s in the same lifelong slot, %d of 2x%d ingots left (a same-token double click "
            "tiered up ONCE), answered %d / %d: %s" % (tline[:1], now_id, left, mq, u1, u2, lp.info))
    txt, cl, ev, ed = render(lp)
    K.check("Tier: Copper" in txt and "Tier up button here" in txt and "Tier up: the button on the right" in txt and "Anvil tab" not in txt,
            "T3: the panel shows the new tier; the help + footer name the Tier up button (review fix 4)")

    # ============================================================================ M: Make multitool + no Multitool tab + /multitool
    K.check("\"Multitool\"" not in txt and "#SkyyGTab2" not in txt and "#SkyyGTab4" in txt, "M1: no Multitool tab beside Tools (Craft | Anvil | Identify | Tools)")
    if mt_ok:
        @JImplements("java.util.function.Function")
        class RbCount(object):
            @JOverride
            def apply(self, o):
                return JObject(JInt(0), Integer_)
        apply(multi__rebirthGate="true")
        br.put("rebirth:fn:count", RbCount())
        br.put("rebirth:n:" + str(U1), JObject(JInt(0), Integer_))
        cs["storage"].setItemStackForSlot(JShort(30), stack("Tool_Pickaxe_Iron"))
        cs["storage"].setItemStackForSlot(JShort(31), stack("Tool_Hatchet_Iron"))
        txt, cl, ev, ed = render(lp)
        mline = setv(cl, "#SkyyGPMt.Text")
        m0 = click(lp, '{"a":"mt:%d"}' % tokOf(lp))
        K.check(mline and "first rebirth" in mline[0] and m0 == 1 and "first rebirth" in str(lp.info) and cs["storage"].getItemStack(JShort(30)) is not None,
                "M2: before rebirth 1 the row is greyed with the rebirth line; a click merges nothing, answered: %s | %s" % (mline[:1], lp.info))
        br.put("rebirth:n:" + str(U1), JObject(JInt(1), Integer_))
        txt, cl, ev, ed = render(lp)
        mline = setv(cl, "#SkyyGPMt.Text")
        tm = tokOf(lp)
        m1 = click(lp, '{"a":"mt:%d"}' % tm)
        m2 = click(lp, '{"a":"mt:%d"}' % tm)
        allids = [str(cs[s].getItemStack(JShort(i)).getItemId()) for s in ("hotbar", "storage") for i in range(int(cs[s].getCapacity()))
                  if cs[s].getItemStack(JShort(i)) is not None and not cs[s].getItemStack(JShort(i)).isEmpty()]
        GM = P("GearMulti")
        mids_ = set(str(GM.mid(JInt(i))) for i in range(len(GM.TW)))
        multis = [i for i in allids if i in mids_]
        K.check(mline and str(Gear.itemName("Tool_Pickaxe_Iron")) in mline[0] and str(Gear.itemName("Tool_Hatchet_Iron")) in mline[0] and m1 == 1 and m2 == 1 and len(multis) == 1
                and "Tool_Pickaxe_Iron" not in allids and "Tool_Hatchet_Iron" not in allids and "Tool_Pickaxe_Copper" in allids and str(lp.info).startswith("+Made a"),
                "M3: after rebirth 1 the plain Iron pair is named and merged once (a same-token double click merges once), the lifelong pickaxe stays: %s | %s | %s"
                % (mline[:1], multis, lp.info))
        # a pair that changed since the page was drawn is refused
        cs["storage"].setItemStackForSlot(JShort(30), stack("Tool_Pickaxe_Iron"))
        cs["storage"].setItemStackForSlot(JShort(31), stack("Tool_Hatchet_Iron"))
        render(lp)
        cs["storage"].removeItemStackFromSlot(JShort(31))
        cs["storage"].setItemStackForSlot(JShort(32), stack("Tool_Hatchet_Iron"))
        m3 = click(lp, '{"a":"mt:%d"}' % tokOf(lp))
        K.check(m3 == 1 and str(lp.info).startswith("-Your tools changed") and cs["storage"].getItemStack(JShort(30)) is not None,
                "M4: the pair moved since the page was drawn = refused, nothing merged: %s" % lp.info)
        # M7 (review fix 3): the pair exists but cannot merge (tool rarity off) = the merge's own reason, not 'Your tools changed'
        apply(multi__rebirthGate="true", part__toolRarity="false")
        txr, clr, evr, edr = render(lp)
        mr = setv(clr, "#SkyyGPMt.Text")
        m7 = click(lp, '{"a":"mt:%d"}' % tokOf(lp))
        pvr = Merge.preview(cs["storage"].getItemStack(JShort(30)), cs["storage"].getItemStack(JShort(32)), U1)
        K.check(m7 == 1 and pvr[0] is not None and str(lp.info) == "-" + str(pvr[0]) and "changed" not in str(lp.info) and mr and str(pvr[0]) in mr[0]
                and cs["storage"].getItemStack(JShort(30)) is not None,
                "M7: a pair that cannot merge (tool rarity off) says the merge's reason on the row and after the click, nothing merged: %s" % lp.info)
        br.remove("rebirth:n:" + str(U1))
        br.remove("rebirth:fn:count")
        apply()
        # /multitool opens the Tools tab on the pickaxe
        FPM.last = None
        sw0 = int(Life.N[0])
        cmd = P("MultiCmd")()
        exe = [m_ for m_ in P("MultiCmd").class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
        exe.setAccessible(True)
        exe.invoke(cmd, None, st, ref, PR1, None)
        op = FPM.last
        K.check(op is not None and str(op.getClass().getName()).endswith("LifePage") and int(op.sel) == 0 and int(Life.N[0]) == sw0 + 1,
                "M5: /multitool sweeps the lifelong tools (%d -> %d) and opens the Tools tab (LifePage, the pickaxe)" % (sw0, int(Life.N[0])))
        apply(part__lifelong="false")
        FPM.last = None
        exe.invoke(cmd, None, st, ref, PR1, None)
        K.check(FPM.last is not None and str(FPM.last.getClass().getName()).endswith("MultiPage"), "M6: part.lifelong off = /multitool opens the old Multitool page")
        apply()
    else:
        K.check(False, "M: the Multitools items could not be loaded in the harness - Make multitool not exercised")

    # ============================================================================ P: the pole row
    txt, cl, ev, ed = render(lp)
    rowB = setv(cl, "#SkyyGLRowB4.Text")
    pole_item = Gear.item(LL.KCRUDE[4]) is not None
    K.check((not pole_item) or (rowB and "Marlow" in rowB[0] and "Arrives" not in rowB[0]),
            "P1: no pole granted = the row says it comes from Marlow (pole item loaded %s): %s" % (pole_item, rowB))
    lp.sel = JInt(4)
    txt4, cl4, ev4, ed4 = render(lp)
    K.check("Fishing Bench" in txt4 and "#SkyyGPUp" not in txt4, "P2: the pole panel keeps 'Tier it up at the Fishing Bench' (no Tier up button)")
    lp.sel = JInt(0)

    # ============================================================================ A: always answer on the other Smithing pages
    Smith.NAV_MS = JLong(60000)
    res = {}
    for nm, ctor, datas in (("SmithPage", P("SmithPage"), (None, "{}", '{"a":"zzz"}', '{"a":"refresh"}', '{"a":"refresh"}', '{"a":"mode:2"}', '{"a":"craft:1"}')),
                            ("ReforgePage", P("ReforgePage"), (None, "{}", '{"a":""}', '{"a":"zzz"}', '{"a":"mode:2"}', '{"a":"mode:9"}', '{"a":"sel:999"}',
                                                               '{"a":"up"}', '{"a":"up"}', '{"a":"idall"}', '{"a":"mode:5"}', '{"a":"tick:99"}')),
                            ("MultiPage", P("MultiPage"), (None, "{}", '{"a":"zzz"}', '{"a":"sel:999"}', '{"a":"merge"}', '{"a":"merge"}', '{"a":"mode:3"}')),
                            ("IdentifyPage", P("IdentifyPage"), (None, "{}", '{"a":"zzz"}', '{"a":"refresh"}'))):
        pg = ctor(PR1)
        FPM.cur = pg
        res[nm] = [click(pg, d) for d in datas]
        FPM.cur = None
    K.check(all(v == [1] * len(v) for v in res.values()), "A1: Craft / Anvil / Multitool / old Identify pages: every click (empty, malformed, unknown, "
            "guarded, failing) = exactly one packet: %s" % res)
    Smith.NAV_MS = JLong(0)

    # every Tools page rendered here validates; the right column fits
    probs = []
    for cl_, ev_ in rendered:
        probs += validate(cl_, ev_)
    txt, cl, ev, ed = render(lp)
    colh = child_sum(cl, "#SkyyGPanel")
    K.check(not probs and colh <= 656, "A2: every Tools page rendered (%d) validates; pickaxe panel %d of 656 px: %s" % (len(rendered), colh, probs[:4]))
    K.notes.append("H310 logs: %s" % [x[:160] for x in logs() if "WARN" in x][:6])


# ====================================================================================================== main
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--root", SCR_ROOT], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, str(n)[:500]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: run_mkfake10(arg("--mkfake"))), ("--h310", lambda: run_h310(arg("--out"))),
                     ("--life", lambda: H35["run_life"](arg("--out"))),          # H37's run_l35 child (the 0.3.9 main had no --life: it recursed)
                     ("--verify", lambda: H["run_verify"](arg("--out"))), ("--h39", lambda: H39["run_h39"](arg("--out"))),
                     ("--h38", lambda: H38["run_h38"](arg("--out"))), ("--h37", lambda: H37["run_h37"](arg("--out"))),
                     ("--g36", lambda: H36["run_g36"](arg("--out"))), ("--snd", lambda: H36["run_snd"](arg("--out"))),
                     ("--till", lambda: H35["run_till"](arg("--out"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    for f_ in (JAR, J39, H38["AR26"], H36["FI6_SRC"], H35["CO_SRC"]):
        assert os.path.isfile(f_), f_
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    shutil.copyfile(H35["CO_SRC"], H36["CO_JAR"])
    shutil.copyfile(H36["FI6_SRC"], H36["FI_JAR"])
    for f_ in glob.glob(os.path.join(H35["LIVE_PLAYERS"], "*.json")):
        shutil.copyfile(f_, os.path.join(SCRATCH, "players", os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets310()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("h310", "--h310"), ("h39", "--h39"), ("verify", "--verify"), ("h38", "--h38"), ("h37", "--h37"), ("g36", "--g36"),
                            ("snd", "--snd"), ("till", "--till")):
            if not want(label):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if want("life"):
            # 0.3.9 by design (proven: the same 5 fail on the 0.3.9 jar): Identify lives on its own tab (mode:5) - the 0.3.5 reveal checks
            # click "id" / "rr" / "idall" on the Anvil tab, a stale click of the other tab there (H39 I covers the reveal on the Identify tab)
            _why39 = "0.3.9 by design: Identify moved to the Identify tab; the 0.3.5 check clicks it on the Anvil tab (H39 I covers the reveal)"
            H37["L37_EXTRA"].extend([("G35 R1:", _why39), ("G35 R2:", _why39), ("G35 R3:", _why39), ("G35 R4", _why39), ("G35 R5:", _why39)])
            n0 = len(H37["FAILS"])
            H37["run_l35"](env)
            for f_ in H37["FAILS"][n0:]:
                FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        if want("audit"):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
