"""Harness for SkyyUiProbe 0.6 (the hub icon panel probe + the lazy map tap; SkyyUiProbe/build_skyyuiprobe_0.6.py, WHY 0.6).
Build first: python SkyyUiProbe/build_skyyuiprobe_0.6.py

    python SkyyUiProbe/test_skyyuiprobe_0.6.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, the 0.7.0 HytaleServer.jar, -XX:-UsePerfData, TEMP / TMP in the scratch
folder; the exec phase with -Xverify:all over the SkyyMenu 0.3.19 harness's engine stand-ins + the six real InventoryComponents and the
Combined component of the 0.5 harness's section O):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.5 -> 0.6: + exactly HubBox, HubSess, HubWin, HubNet, HubAct, HubPanel; changed only ProbeCmds (the hubpanel word + the list
              line), SkyProbeArgCmd (its help), MapProbe (needsTap / ensureTap / command, tapOn's log text), SkyyUiProbePlugin (start: no
              tap; shutdown: the panel; the ready line), ProbeLog.kit + ProbeViews.index (the kit id text only) - every probe page identical
  (FIX ROUND: Layout D icons; CREATIVE - SetCreativeItem on the panel / any creative packet carrying an icon id blocked, ordinary creative
   packets pass; an unreadable inventory at close = unknown, not a failed check)
  X  exec     THE HUB PANEL through the 0.7.0 engine's OWN PageManager.setPageWithWindows / WindowManager / ContainerWindow and its OWN
              PacketAdapters.__handleInbound (a stand-in GamePacketHandler of the player):
     OPEN    /skyprobe hubpanel (ProbeCmds.arg): SetPage Bench + OpenWindow (a Container of 9 slots: the 9 icons, our icon ids when the
             item store knows them, else the vanilla stand-ins), the window registered, one session, the inbound filter registered once
     CLICK   every packet naming the panel is BLOCKED (the engine never sees it) and answered on the world thread: MoveItemStack from an
             icon (a click / a drag out), SmartMoveItemStack (shift-click), DropItemStack (the drop key) -> the snap-back (window +
             inventory re-sent) + that icon's hub command run as the player + a chat line + the look-again 1.5 s later; a drag INTO the
             panel, an InventoryAction / SendWindowAction on it -> blocked + snap-back, no hub; two clicks within 0.75 s = one hub; a hub
             whose command is not installed says so; every other packet (moves inside the player's own inventory, movement, page
             events) passes on untouched; after every step 9 icons in the panel, none in the inventory, no WARNING
     ENGINE  as if the filter were not there: the engine's own container moves on the panel (drag out / in, swap, shift-click whole slot,
             the drop key, Take All, Put All, Quick Stack, merge, sort, 2,000 random moves between the panel and the player's real
             inventory): every icon stays in its slot, nothing enters, the player's items unchanged - an icon can never leave or be copied
     CLOSE   the client's close (WindowManager.closeWindow -> HubWin.onClose0): the summary line (blocked / passed / hubs / packets seen),
             the chat line, the session gone, later packets pass on; a second /skyprobe hubpanel replaces the first panel; a hub page that
             replaced the inventory -> the look-again closes the panel window; shutdown removes the filter
     TAP     no outbound tap at start; needsTap = p2 / p2sharp / p4 / p5; /skyprobe map p4 registers it once (ensureTap), status does not
  AA engine-access audit
Scratch: tools/dev/scratch/perfmenu/uiprobe (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.6"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyUiProbe-0.5.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfmenu", "uiprobe")))
PKG = "com.skyy.uiprobe."
MENU_HARNESS = os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py")
ADDED = ["HubBox", "HubSess", "HubWin", "HubNet", "HubAct", "HubPanel"]
EXPECT = {
    "ProbeCmds": ["~m arg", "~m list"],
    "SkyProbeArgCmd": ["~c "],
    "MapProbe": ["+m needsTap", "+m ensureTap", "~m command", "~m tapOn"],
    "SkyyUiProbePlugin": ["~m setup", "~m start", "~m shutdown"],
    # the kit id text only (tools/skyyui.py is still kit 1.4; its file changed since 0.5 was built): every probe page's statements
    # (ProbeViews.p1 ... p24, KitViews) are byte-identical, so the pages send exactly what 0.5 sent
    "ProbeLog": ["~m kit"],
    "ProbeViews": ["~m index"],
    # FIX ROUND: the creative packets in the log lines (ProbeWin.describe) + the parent command's help names hubpanel
    "ProbeWin": ["~m describe"],
    "SkyProbeCmd": ["~c "],
}
# FIX ROUND: Layout D's 3 x 3 centre (SkyyMenu main slots 3-5, 12-14, 21-23; the SkyWynn Menu in Teleport's centre slot)
ICONS = ["Skyy_Menu_Icon_Pets", "Skyy_Menu_Icon_Skills", "Skyy_Menu_Icon_AccessoryBag", "Skyy_Menu_Icon_IslandMenu", "Skyy_Menu",
         "Skyy_Menu_Icon_Crafting", "Skyy_Menu_Icon_Bank", "Skyy_Menu_Icon_Bazaar", "Skyy_Menu_Icon_AuctionHouse"]
VANILLA = ["Farming_Collar", "Tool_Pickaxe_Iron", "Utility_Bag_Seed", "Soil_Grass", "Ingredient_Voidheart", "Bench_WorkBench",
           "Furniture_Ancient_Chest_Large", "Ingredient_Bar_Gold", "Ingredient_Bar_Silver"]
CMDS = ["pets", "skills", "accessories", "island menu", "skymenu", "craft", "bank", "bazaar", "ah"]


def menu_harness():
    spec = importlib.util.spec_from_file_location("menu0319", MENU_HARNESS)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    return m


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JShort, JArray
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    MH = menu_harness()
    E = MH.engine(scratch, hcls)
    U, jf = E.U, E.jf
    PH = "com.hypixel.hytale."
    # ---- the six inventory components + Combined on the stand-in store (the 0.5 harness's section O)
    EMc = JClass(PH + "server.core.modules.entity.EntityModule")
    em = JClass(PH + "server.core.modules.entity.EntityModule").get()
    INVN = PH + "server.core.inventory.InventoryComponent"
    INVc = JClass(INVN)
    CTc = JClass(PH + "component.ComponentType")
    CICc = JClass(PH + "server.core.inventory.container.CombinedItemContainer")
    IC = JClass(PH + "server.core.inventory.container.ItemContainer")
    ISC = JClass(PH + "server.core.inventory.ItemStack")
    nxt = [5000]

    def ctype():
        c_ = CTc()
        nxt[0] += 1
        jf(CTc.class_, "index").setInt(c_, nxt[0])
        jf(CTc.class_, "hashCode").setInt(c_, nxt[0])
        return c_
    KINDS = [("Hotbar", "hotbarInventoryComponentType", 9), ("Storage", "storageInventoryComponentType", 36),
             ("Backpack", "backpackInventoryComponentType", 0), ("Armor", "armorInventoryComponentType", 4),
             ("Utility", "utilityInventoryComponentType", 4), ("Tool", "toolInventoryComponentType", 4)]
    CT_INV = dict((k, ctype()) for k, _f, _n in KINDS)
    CT_COMB = ctype()
    for k, fname, _n in KINDS:
        jf(EMc.class_, fname).set(em, CT_INV[k])
    jf(EMc.class_, "combinedInventoryComponentType").set(em, CT_COMB)
    INVc.setupCombined(CT_INV["Storage"], CT_INV["Armor"], CT_INV["Hotbar"], CT_INV["Utility"], CT_INV["Backpack"], CT_INV["Tool"])

    def admin(uid):
        P = E.player(E.UUID.fromString(uid), name="PanelTester")
        invs = dict((k, JClass(INVN + "$" + k)(JShort(n))) for k, _f, n in KINDS)
        for k in invs:
            P.st.row(P.ref).put(CT_INV[k], invs[k])
        comb = JClass(INVN + "$Combined")()
        for key in (INVc.EVERYTHING, INVc.STORAGE_HOTBAR_BACKPACK):
            a = JArray(IC)(len(key))
            for i, ct in enumerate(list(key)):
                a[i] = invs[[k for k in CT_INV if CT_INV[k] == ct][0]].getInventory()
            comb.getInventories().put(key, CICc(a))
        P.st.row(P.ref).put(CT_COMB, comb)
        P.invs = invs
        P.all = comb.getInventories().get(INVc.EVERYTHING)
        invs["Storage"].getInventory().setItemStackForSlot(JShort(0), ISC("Food_Bread", 10))
        invs["Storage"].getInventory().setItemStackForSlot(JShort(1), ISC("Rock_Stone", 20))
        invs["Hotbar"].getInventory().setItemStackForSlot(JShort(0), ISC("Weapon_Sword_Iron", 1))
        return P

    def counts(c):
        out_ = {}
        for i in range(int(c.getCapacity())):
            s_ = c.getItemStack(JShort(i))
            if s_ is not None and not s_.isEmpty():
                out_[str(s_.getItemId())] = out_.get(str(s_.getItemId()), 0) + int(s_.getQuantity())
        return out_

    def slots(c):
        return [(None if (c.getItemStack(JShort(i)) is None or c.getItemStack(JShort(i)).isEmpty()) else
                 (str(c.getItemStack(JShort(i)).getItemId()), int(c.getItemStack(JShort(i)).getQuantity()))) for i in range(int(c.getCapacity()))]
    HPn = JClass(PKG + "HubPanel")
    PLOG = JClass(PKG + "ProbeLog")
    CMDS_ = JClass(PKG + "ProbeCmds")
    PAD = JClass(PH + "server.core.io.adapter.PacketAdapters")
    GPH = JClass(PH + "server.core.io.handlers.game.GamePacketHandler")
    inbound = jf(PAD.class_, "inboundHandlers").get(None)
    n_in0 = int(inbound.size())
    for cn_ in CMDS[:5]:
        E.CM.cmds.put(cn_.split(" ")[0], U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    P = admin("00000000-0000-0000-0000-0000000000d7")
    INV0 = counts(P.all)

    def logs():
        return [str(x) for x in PLOG.tail()]

    # ------------------------------------------------------------------ OPEN
    PLOG.TAIL.clear()
    n0 = len(E.sent(P))
    CMDS_.arg(P.ref, P.st, P.pr, E.W1, "hubpanel")
    kinds = E.kinds(P, n0)
    K.check("SetPage" in kinds and "OpenWindow" in kinds, "OPEN: /skyprobe hubpanel sends SetPage + OpenWindow: %s" % kinds)
    sp = [p for p in E.sent(P)[n0:] if str(p.getClass().getSimpleName()) == "SetPage"][0]
    K.eq(str(sp.page), "Bench", "OPEN: the page is Bench (the vanilla chest / inventory page)")
    ow = [p for p in E.sent(P)[n0:] if str(p.getClass().getSimpleName()) == "OpenWindow"][0]
    s = HPn.SESS.get(P.pr.getUuid())
    K.check(s is not None and int(s.winId) == int(ow.id) and P.wm.getWindow(int(ow.id)) == s.win, "OPEN: one session, its window registered under the OpenWindow id")
    inv_sec = ow.inventory
    sec = {}
    it_ = inv_sec.items.entrySet().iterator()
    while it_.hasNext():
        e_ = it_.next()
        sec[int(e_.getKey())] = (str(e_.getValue().itemId), int(e_.getValue().quantity))
    K.eq((int(inv_sec.capacity), sec), (9, dict((i, (ICONS[i], 1)) for i in range(9))), "OPEN: the window shows 9 icons (our icon ids: the item store knows them)")
    K.eq(slots(s.box), [(ICONS[i], 1) for i in range(9)], "OPEN: the panel box holds the 9 icons, one each")
    K.check(bool(s.box.armed), "OPEN: the box is armed")
    K.eq(int(inbound.size()), n_in0 + 1, "OPEN: the inbound filter registered once")
    K.check(any("hub panel opened" in l for l in logs()), "OPEN: the log line")
    W = int(s.winId)
    gph = U.allocateInstance(GPH.class_)
    jf(GPH.class_, "playerRef").set(gph, P.pr)
    MIS = JClass(PH + "protocol.packets.inventory.MoveItemStack")
    SMIS = JClass(PH + "protocol.packets.inventory.SmartMoveItemStack")
    DIS = JClass(PH + "protocol.packets.inventory.DropItemStack")
    IAC = JClass(PH + "protocol.packets.inventory.InventoryAction")
    SWA = JClass(PH + "protocol.packets.window.SendWindowAction")
    CMV = JClass(PH + "protocol.packets.player.ClientMovement")
    CPE = JClass(PH + "protocol.packets.interface_.CustomPageEvent")

    def mis(fs, fsl, q, ts, tsl):
        m = MIS()
        m.fromSectionId, m.fromSlotId, m.quantity, m.toSectionId, m.toSlotId = fs, fsl, q, ts, tsl
        return m

    def smis(fs, fsl):
        m = SMIS()
        m.fromSectionId, m.fromSlotId, m.quantity = fs, fsl, 1
        m.moveType = JClass(PH + "protocol.SmartMoveType").values()[0]
        return m

    def dis(sec_, sl):
        m = DIS()
        m.inventorySectionId, m.slotId, m.quantity = sec_, sl, 1
        return m

    def iac(sec_):
        m = IAC()
        m.inventorySectionId = sec_
        m.inventoryActionType = JClass(PH + "protocol.InventoryActionType").values()[0]
        return m

    def swa(i):
        m = SWA()
        m.id = i
        return m

    def invariant(what):
        K.eq(slots(s.box), [(ICONS[i], 1) for i in range(9)], "%s: all 9 icons in their slots" % what)
        K.eq(counts(P.all), INV0, "%s: the player's inventory unchanged (no icon in it)" % what)
        K.check(not any(l.startswith("WARNING") for l in logs()), "%s: no WARNING" % what)

    def send(p, what, blocked, hub=None, world_tasks=1):
        PLOG.TAIL.clear()
        lines0 = int(E.CM.lines.size())
        b = bool(PAD.__handleInbound(gph, p))
        K.eq(b, blocked, "%s: %s" % (what, "BLOCKED (the engine never sees it)" if blocked else "passed on to the engine"))
        q = E.queued(E.W1)
        K.eq(q, ["HubAct"] * world_tasks if blocked else [], "%s: %s" % (what, "one HubAct on the player's world thread" if blocked else "nothing queued"))
        r0 = int(s.resends)
        n0_ = len(E.sent(P))
        E.run_world(E.W1)
        if blocked:
            K.eq(int(s.resends), r0 + 1, "%s: the snap-back ran (window + inventory re-sent)" % what)
        new_lines = [str(E.CM.lines.get(i)) for i in range(lines0, int(E.CM.lines.size()))]
        K.eq(new_lines, [hub] if hub else [], "%s: hub command run as the player: %s" % (what, new_lines))
        invariant(what)
        return E.strs_of(P, n0_)

    # ------------------------------------------------------------------ CLICK
    ch = send(mis(W, 4, 1, -2, 5), "CLICK 1 (MoveItemStack from icon 5 to storage)", True, "skymenu")
    K.check("Opening SkyWynn Menu" in ch, "CLICK 1: the chat line")
    K.check(any("BLOCKED MoveItemStack" in l and "icon 5 (SkyWynn Menu)" in l for l in logs()), "CLICK 1: the blocked packet is logged: %s" % logs()[:3])
    # the look-again was scheduled 1.5 s later (World.scheduleAfter -> the stand-in keeps it as a task)
    s.lastHubAt = 0
    send(smis(W, 3), "CLICK 2 (shift-click icon 4: /island menu, a two-word command)", True, "island menu")
    s.lastHubAt = 0
    send(dis(W, 2), "CLICK 3 (the drop key on icon 3)", True, "accessories")
    s.lastHubAt = 0
    send(mis(-2, 0, 10, W, 4), "CLICK 4 (drag own bread INTO the panel)", True, None)
    send(iac(W), "CLICK 5 (InventoryAction on the panel)", True, None)
    send(swa(W), "CLICK 6 (SendWindowAction on the panel)", True, None)
    s.lastHubAt = 0
    send(mis(W, 1, 1, -1, 3), "CLICK 7 (drag icon 2 to the hotbar)", True, "skills")
    send(mis(W, 1, 1, -1, 3), "CLICK 8 (the same click again within 0.75 s)", True, None)
    s.lastHubAt = 0
    ch = send(mis(W, 7, 1, -2, 6), "CLICK 9 (icon 8: /bazaar not installed)", True, None)
    K.check("not installed" in ch, "CLICK 9: says the hub is not installed")
    send(mis(-2, 0, 1, -2, 9), "PASS 1 (a move inside the player's own storage)", False)
    send(CMV(), "PASS 2 (movement)", False)
    send(CPE(JClass(PH + "protocol.packets.interface_.CustomPageEventType").Data, "{}"), "PASS 3 (a page event)", False)
    K.check(int(s.blocked.get()) == 9 and int(s.passed.get()) == 3 and int(s.hubs) == 4, "CLICK: 9 blocked, 3 passed, 4 hubs (%d %d %d)" % (int(s.blocked.get()), int(s.passed.get()), int(s.hubs)))
    # the vanilla stand-ins when the item store does not know our icons
    E_IMAP = JClass(PH + "server.core.asset.type.item.config.Item").getAssetMap()
    keep_item = E_IMAP.item
    E_IMAP.item = None
    K.eq(list(HPn.iconIds()), VANILLA, "OPEN: without SkyyMenu's icon items the vanilla stand-ins")
    E_IMAP.item = keep_item

    # ------------------------------------------------------------------ CREATIVE (fix round): the creative packets
    SCI = JClass(PH + "protocol.packets.inventory.SetCreativeItem")
    SGCI = JClass(PH + "protocol.packets.inventory.SmartGiveCreativeItem")
    DCI = JClass(PH + "protocol.packets.inventory.DropCreativeItem")
    IQ = JClass(PH + "protocol.ItemQuantity")

    def iq(i_, q_):
        x = IQ()
        x.itemId, x.quantity = i_, q_
        return x

    def sci(sec_, sl, item_):
        m = SCI()
        m.inventorySectionId, m.slotId, m.item, m.override = sec_, sl, item_, True
        return m
    b0, p0, h0 = int(s.blocked.get()), int(s.passed.get()), int(s.hubs)
    s.lastHubAt = 0
    send(sci(W, 2, iq("Rock_Stone", 5)), "CREATIVE 1 (SetCreativeItem into the panel)", True, None)
    send(sci(-2, 7, iq(ICONS[4], 1)), "CREATIVE 2 (SetCreativeItem of a hub icon into storage = a copy)", True, None)
    send(sci(-2, 7, iq(VANILLA[1], 1)), "CREATIVE 3 (SetCreativeItem of a vanilla stand-in id = a copy)", True, None)
    m_ = SGCI()
    m_.item = iq(ICONS[6], 1)
    m_.moveType = JClass(PH + "protocol.SmartMoveType").values()[0]
    send(m_, "CREATIVE 4 (SmartGiveCreativeItem of a hub icon)", True, None)
    m_ = DCI()
    m_.item = iq(ICONS[0], 1)
    send(m_, "CREATIVE 5 (DropCreativeItem of a hub icon)", True, None)
    send(sci(-2, 7, iq("Rock_Stone", 5)), "CREATIVE 6 (SetCreativeItem of an ordinary item into storage)", False)
    m_ = DCI()
    m_.item = iq("Rock_Stone", 1)
    send(m_, "CREATIVE 7 (DropCreativeItem of an ordinary item)", False)
    K.check(int(s.blocked.get()) == b0 + 5 and int(s.passed.get()) == p0 + 2 and int(s.hubs) == h0,
            "CREATIVE: 5 blocked, 2 passed, no hub opened (a creative packet never names an icon slot to take)")

    # ------------------------------------------------------------------ ENGINE backstop (as if the filter were not there)
    box = s.box
    stor = P.invs["Storage"].getInventory()
    hot = P.invs["Hotbar"].getInventory()
    tries = [
        ("drag out", lambda: box.moveItemStackFromSlotToSlot(JShort(0), 1, stor, JShort(10))),
        ("drag out onto bread", lambda: box.moveItemStackFromSlotToSlot(JShort(1), 1, stor, JShort(0))),
        ("drag in", lambda: stor.moveItemStackFromSlotToSlot(JShort(0), 10, box, JShort(2))),
        ("swap", lambda: stor.moveItemStackFromSlotToSlot(JShort(1), 20, box, JShort(3))),
        ("shift-click", lambda: box.moveItemStackFromSlot(JShort(4), stor)),
        ("shift-click into the panel", lambda: stor.moveItemStackFromSlot(JShort(0), box)),
        ("drop key", lambda: box.removeItemStackFromSlot(JShort(5))),
        ("take all", lambda: box.moveAllItemStacksTo(JArray(IC)([stor]))),
        ("put all", lambda: stor.moveAllItemStacksTo(JArray(IC)([box]))),
        ("quick stack", lambda: stor.quickStackTo(JArray(IC)([box]))),
        ("merge", lambda: box.combineItemStacksIntoSlot(stor, JShort(6))),
        ("sort", lambda: box.sortItems(JClass(PH + "protocol.SortType").values()[0])),
    ]
    errs = []
    for name, fn in tries:
        try:
            fn()
        except Exception as ex:
            errs.append("%s: %s" % (name, str(ex)[:120]))
        invariant("ENGINE %s" % name)
    K.check(len(errs) <= 3, "ENGINE: the engine's moves answer without crashing (refusals; %s)" % errs)
    rnd = random.Random(66)
    for i in range(2000):
        a, b_ = (box, stor) if rnd.random() < 0.5 else (stor, box)
        try:
            if rnd.random() < 0.6:
                a.moveItemStackFromSlotToSlot(JShort(rnd.randrange(int(a.getCapacity()))), rnd.randint(1, 20), b_, JShort(rnd.randrange(int(b_.getCapacity()))))
            elif rnd.random() < 0.8:
                a.moveItemStackFromSlot(JShort(rnd.randrange(int(a.getCapacity()))), b_)
            else:
                box.removeItemStackFromSlot(JShort(rnd.randrange(9)))
        except Exception:
            pass
    invariant("ENGINE 2,000 random moves between the panel and the player's inventory")

    # ------------------------------------------------------------------ the look-again + close
    # a hub page now open + the look-again -> the server closes the panel window
    E.W1.tasks = None
    s.lastHubAt = 0
    PAD.__handleInbound(gph, mis(W, 0, 1, -2, 5))
    E.run_world(E.W1)
    act = JClass(PKG + "HubAct")(s, 0, True)
    P.seen = len(E.sent(P))
    P.pm.openCustomPage(P.ref, P.st, JClass(PKG + "ProbePage")(P.pr, 0))
    E.pump(P)
    PLOG.TAIL.clear()
    n1 = len(E.sent(P))
    act.run()
    K.check(any("1.5 s after the hub opened" in l and "ProbePage" in l for l in logs()), "CLOSE: the look-again logs what the client shows")
    K.check(bool(s.closed) and P.wm.getWindow(W) is None and HPn.SESS.get(P.pr.getUuid()) is None, "CLOSE: a hub page replaced the inventory -> the panel window closed, the session gone")
    K.check(any("closed after" in l and "nothing left the panel" in l and "packets seen" in l for l in logs()), "CLOSE: the summary line: %s" % [l for l in logs() if "closed after" in l][:1])
    K.check("Hub panel closed" in E.strs_of(P, n1), "CLOSE: the chat line")
    K.eq(bool(PAD.__handleInbound(gph, mis(W, 0, 1, -2, 5))), False, "CLOSE: later packets pass on (no session)")
    # the client's own close + a second panel replacing the first
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, CPE(JClass(PH + "protocol.packets.interface_.CustomPageEventType").Dismiss, None))
    CMDS_.arg(P.ref, P.st, P.pr, E.W1, "hubpanel")
    s1 = HPn.SESS.get(P.pr.getUuid())
    CMDS_.arg(P.ref, P.st, P.pr, E.W1, "hubpanel")
    s2 = HPn.SESS.get(P.pr.getUuid())
    K.check(s1 is not None and s2 is not None and s1 != s2 and bool(s1.closed) and P.wm.getWindow(int(s1.winId)) is None and P.wm.getWindow(int(s2.winId)) == s2.win,
            "CLOSE: a second /skyprobe hubpanel replaces the first panel (old window closed)")
    K.eq(int(inbound.size()), n_in0 + 1, "CLOSE: still one inbound filter")
    # FIX ROUND (critic 4): an inventory the server cannot read at close (getCombined throws -> -1) is "unknown", not a failed check
    PLOG.TAIL.clear()
    HPn.closed(s2, P.ref, None)
    K.check(bool(s2.closed) and any("closed after" in l and "unknown" in l and "nothing left the panel" in l for l in logs())
            and not any(l.startswith("WARNING") for l in logs()), "FIXR: an unreadable inventory at close = unknown, no ICON CHECK FAILED: %s"
            % [l for l in logs() if "closed after" in l][:1])
    P.wm.closeWindow(P.ref, int(s2.winId), P.st)
    CMDS_.arg(P.ref, P.st, P.pr, E.W1, "hubpanel")
    s2 = HPn.SESS.get(P.pr.getUuid())
    P.wm.closeWindow(P.ref, int(s2.winId), P.st)
    K.check(bool(s2.closed) and HPn.SESS.isEmpty(), "CLOSE: the client's close (WindowManager.closeWindow -> onClose0) ends the session")
    HPn.shutdown()
    K.eq(int(inbound.size()), n_in0, "CLOSE: shutdown removes the inbound filter")
    K.check(HPn.NET is None, "CLOSE: NET cleared")

    # ------------------------------------------------------------------ TAP: the lazy outbound map tap
    MP = JClass(PKG + "MapProbe")
    outbound = jf(PAD.class_, "outboundHandlers").get(None)
    o0 = int(outbound.size())
    K.check(MP.TAPF is None, "TAP: no outbound tap before a map probe asks (0.5 registered it at start)")
    K.eq([bool(MP.needsTap(x)) for x in ("p1a", "p1b", "p2", "p2sharp", "p3", "p3resend", "p4", "p5", "off", "status")],
         [False, False, True, True, False, False, True, True, False, False], "TAP: needsTap = p2, p2sharp, p4, p5")
    for step in ("status", "off"):
        try:
            MP.command(P.ref, P.st, P.pr, E.W1, step)
        except Exception:
            pass
    K.check(MP.TAPF is None and int(outbound.size()) == o0, "TAP: status / off register nothing")
    try:
        MP.command(P.ref, P.st, P.pr, E.W1, "p4")
    except Exception:
        pass
    K.check(MP.TAPF is not None and int(outbound.size()) == o0 + 1, "TAP: /skyprobe map p4 registers the tap")
    try:
        MP.command(P.ref, P.st, P.pr, E.W1, "p5")
    except Exception:
        pass
    MP.ensureTap()
    K.eq(int(outbound.size()), o0 + 1, "TAP: once only")
    MP.tapOff()
    K.check(MP.TAPF is None and int(outbound.size()) == o0, "TAP: tapOff (shutdown) removes it")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyUiProbe", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec)], script=__file__)
