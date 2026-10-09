"""Bare-JVM check for SkyyGear 0.2.10 (THE SIGNATURE CHARGE IS KEPT PER WEAPON ON A SWAP - Skyy LOCKED docs/answered/gear.md 2026-10-08:
"1 tweak , make it stay when you change weapon and change back instead of resetting."). The 0.2.9 harness (SkyyGear/test_skyygear_0.2.9.py,
read only: every 0.1 ... 0.2.9 section, itself on the 0.2.8 harness text) runs on the 0.2.10 jar with VERSION 0.2.10 and the new section AK.

    python SkyyGear/test_skyygear_0.2.10.py [--jar <SkyyGear-0.2.10.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

  AK 0.2.10 - every new path EXECUTED on the real classes, a REAL EntityStatMap (SignatureEnergy / SignatureCharges stat types modelled on
     Assets.zip: Min 0, Max 0 / 100, the weapon's item stat modifiers set the max), real ItemStacks in a real SimpleItemContainer hotbar, the
     ENGINE's own InventorySystems$ActiveSlotChangedEntityEventSystem.handle (queues the new item's EntityStatsToClear) and the ENGINE's own
     StatModifiersManager.recalculateEntityStatModifiers (clear + the held item's max) on the ECS shim of section AC:
     AK0 the model answers (stat types, items, the engine's clear + max on a swap = the vanilla reset);
     AK1 swap away (to a non-weapon) and back: kept, cleared by the engine, restored; the row off = the vanilla reset (negative control);
     AK2 drop / move / another item in the slot (InventoryChangeEvent through GearSigInvSys.handle) -> the kept charge is gone;
     AK3 two identical weapons in two slots keep their own charges; a clamp to a smaller new max; the bow's SignatureCharges too;
     AK4 death (DeathComponent) / logout (PlayerDisconnectEvent) / world switch (PlayerReadyEvent) / profile switch (profile:epoch) /
         profile:busy / the row switched off -> forgotten, nothing restored afterwards;
     AK5 no dupe: several swaps inside one tick keep nothing new; away-and-back inside one tick restores once; a pack weapon the engine
         CARRIES the meter to takes it off the kept value; the engine's Recalculate before / after GearSigTick gives the same result;
     AK6 the Server Setup row + the fresh file; AK7 the class byte-compare 0.2.9 -> 0.2.10 (every difference listed).
     AK8 the review fixes: (1) a SkyySkills crossbow id (its perk.archery.keepLoaded.items through a config:fn:SkyySkills "get" stub) is left
         to SkyySkills - not kept, not restored - while a sword still is, and without SkyySkills the crossbow is kept; (2) GearSigTick(true)
         depends AFTER EntityStatsSystems$Recalculate, the fallback GearSigTickU has no dependency; (3) a kept entry re-made by a slot event
         after the logout clean-up is swept (sweepWith + sweep through Universe.getPlayers()).
  The carried AH3 (start twice on a live copy) runs on the 0.2.10 jar unchanged; the carried AJ3 (0.2.8 -> 0.2.9 compare) is history (AK7).
Scratch: only under --dir (default tools/dev/scratch/sigkeep01/harness), deleted at the end unless --keep. Exit code 1 on any unexpected failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
H29 = os.path.join(HERE, "test_skyygear_0.2.9.py")
_t29 = open(H29, encoding="utf-8").read()
_cut = _t29.rindex('_g = {"__name__": "__main__"')
_n29 = {"__name__": "skyygear_h29", "__file__": H29, "__builtins__": __builtins__}
exec(compile(_t29[:_cut], H29 + " (the 0.2.9 harness text, not run)", "exec"), _n29)
src = _n29["src"]
DEV29 = _n29["DEV28"] + _n29["DEVIATIONS29"]


def sub(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "harness text changed: anchor count %d (want %d): %s" % (n, count, old[:120])
    src = src.replace(old, new)


DEVIATIONS210 = [
    ("AG0: the two rows (74 in all)", "75 rows: + gear.signatureKeep (AK6); the two speed rows are unchanged"),
    ("AG0: the fresh file ends with the speed block", "the 0.2.10 signature-charge block now follows the speed block at the very end (AK6 checks both)"),
    ("AH4: SkyyGear-0.2.6.jar", "pre-existing (the pinned 0.2.9 harness fails it the same way today): the 0.2.6 -> 0.2.7 compare jar was removed by "
     "tools/tidy_local.py - history; AK7 compares 0.2.9 -> 0.2.10"),
]
sub('VERSION = "0.2.9"\nDEVIATIONS = %r' % (DEV29,), 'VERSION = "0.2.10"\nDEVIATIONS = %r' % (DEV29 + DEVIATIONS210,))
sub('os.path.join(TOOLS, "dev", "scratch", "gear029", "harness")', 'os.path.join(TOOLS, "dev", "scratch", "sigkeep01", "harness")')
sub('print("DEVIATION (0.2.5/0.2.6/0.2.7/0.2.8/0.2.9, expected):"', 'print("DEVIATION (0.2.5/0.2.6/0.2.7/0.2.8/0.2.9/0.2.10, expected):"')
sub('expected 0.2.5 / 0.2.6 / 0.2.7 / 0.2.8 / 0.2.9 deviations (%d listed kinds seen)',
    'expected 0.2.5 / 0.2.6 / 0.2.7 / 0.2.8 / 0.2.9 / 0.2.10 deviations (%d listed kinds seen)')
# pre-existing (the pinned 0.2.9 harness crashes the same way today): the 0.2.7 section AH0 opened SkyyGear's historical SkyyArmory-0.1.3.jar,
# removed by tools/tidy_local.py - it reads the two own crossbows from the SET pin's SkyyArmory jar instead (ARMORY_JAR; they are unchanged)
sub('''    with _zf.ZipFile(os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.3.jar")) as zo_:''', '''    with _zf.ZipFile(ARMORY_JAR if os.path.isfile(ARMORY_JAR) else os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.3.jar")) as zo_:''')
sub('''"AH0: both own crossbows read from SkyyArmory/SkyyArmory-0.1.3.jar: %s" % sorted(ownd)''', '''"AH0: both own crossbows read from %s: %s" % (os.path.basename(ARMORY_JAR), sorted(ownd))''')
# AJ3 (0.2.8 -> 0.2.9 compare) is history: AK7 compares 0.2.9 -> 0.2.10
sub('''    jar028 = os.path.join(HERE, "SkyyGear-0.2.8.jar")
    if os.path.isfile(jar028) and "cls_members" in dir():''', '''    jar028 = None          # 0.2.10: the 0.2.8 -> 0.2.9 compare is history - AK7 compares 0.2.9 -> 0.2.10
    if jar028 is None:
        print("AJ3. NOTE (0.2.10) the 0.2.8 -> 0.2.9 class compare is history - AK7 compares 0.2.9 -> 0.2.10")
    elif os.path.isfile(jar028) and "cls_members" in dir():''')

AK_SRC = r'''    # ======================================================================================================================== AK 0.2.10
    print("AK. 0.2.10: the signature charge kept on a weapon swap - executed on a real EntityStatMap + the engine's own clear / recalc")
    Cfg.apply(Props(), False)
    Sig, SigSlot, SigInv, SigTick, SigBye = J("GearSig"), J("GearSigSlotSys"), J("GearSigInvSys"), J("GearSigTick"), J("GearSigBye")
    SigTickU = J("GearSigTickU")
    Sig.XBC = None
    ENGK = "com.hypixel.hytale.server.core."
    ESTk = JClass(ENGK + "modules.entitystats.asset.EntityStatType")
    DSTk = JClass(ENGK + "modules.entitystats.asset.DefaultEntityStatTypes")
    ESMk = JClass(ENGK + "modules.entitystats.EntityStatMap")
    IWPk = JClass(ENGK + "asset.type.item.config.ItemWeapon")
    ISAEk = JClass(ENGK + "event.events.ecs.InventorySetActiveSlotEvent")
    ICEk = JClass(ENGK + "event.events.ecs.InventoryChangeEvent")
    HOTk = JClass(ENGK + "inventory.InventoryComponent$Hotbar")
    UTILk = JClass(ENGK + "inventory.InventoryComponent$Utility")
    TOOLk = JClass(ENGK + "inventory.InventoryComponent$Tool")
    ARMk = JClass(ENGK + "inventory.InventoryComponent$Armor")
    ECCk = JClass(ENGK + "entity.effect.EffectControllerComponent")
    DTHk = JClass(ENGK + "modules.entity.damage.DeathComponent")
    PRk = JClass(ENGK + "universe.PlayerRef")
    ASCk = JClass(ENGK + "inventory.InventorySystems$ActiveSlotChangedEntityEventSystem")
    # GameplayConfig's class init builds DEFAULT, whose constructor reads EntityEffect's asset store: a bare JVM gets an empty one first
    # (probed: the only store it needs), so World.getGameplayConfig() inside the engine's recalc answers GameplayConfig.DEFAULT
    EFFk = JClass(ENGK + "asset.type.entityeffect.config.EntityEffect")
    ak_old_eff = acf(EFFk.class_.getName(), "STORE").get(None)
    if ak_old_eff is None:
        acf(EFFk.class_.getName(), "STORE").set(None, zstore(indexed({})))
    GPCk = JClass(ENGK + "asset.type.gameplay.GameplayConfig")
    I2Ok = JClass("it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap")
    UTLk = JClass(ENGK + "asset.type.item.config.ItemUtility")
    SMOA = JArray(SMO)
    ByteK = JClass("java.lang.Byte")
    SINGLES = [ENGK + "universe.Universe", ENGK + "modules.entity.EntityModule", ENGK + "modules.entitystats.EntityStatsModule",
               ENGK + "modules.entity.damage.DamageModule"]

    def ak_inst(cn_):
        f_ = JClass(cn_).class_.getDeclaredField("instance")
        f_.setAccessible(True)
        return f_
    ak_old_single = dict((cn_, ak_inst(cn_).get(None)) for cn_ in SINGLES)
    for cn_ in SINGLES:
        o_ = UZ.allocateInstance(JClass(cn_).class_)
        for fd_ in JClass(cn_).class_.getDeclaredFields():
            if fd_.getType() == CTYc.class_ and not MODc.isStatic(fd_.getModifiers()):
                fd_.setAccessible(True)
                fd_.set(o_, UZ.allocateInstance(CTYc.class_))
        ak_inst(cn_).set(None, o_)
    CTK = {"pr": PRk.getComponentType(), "hot": HOTk.getComponentType(), "util": UTILk.getComponentType(), "tool": TOOLk.getComponentType(),
           "arm": ARMk.getComponentType(), "ecc": ECCk.getComponentType(), "esm": ESMk.getComponentType(), "dth": DTHk.getComponentType()}
    check(all(v_ is not None for v_ in CTK.values()) and len(set(SysJ.identityHashCode(v_) for v_ in CTK.values())) == len(CTK),
          "AK0: the ECS shim - every component type the engine + GearSig systems ask for resolves to its own object (%s)" % sorted(CTK))

    # ---- the stat model (Assets.zip SignatureEnergy.json Min 0 Max 0 Shared; SignatureCharges.json Min 0 Max 100 Shared) at indices 0 / 1
    def ak_stat(id_, mx_):
        t_ = acalloc(ESTk.class_.getName())
        acf(ESTk.class_.getName(), "id").set(t_, id_)
        acf(ESTk.class_.getName(), "initialValue").setFloat(t_, JFloat(0.0))
        acf(ESTk.class_.getName(), "min").setFloat(t_, JFloat(0.0))
        acf(ESTk.class_.getName(), "max").setFloat(t_, JFloat(mx_))
        acf(ESTk.class_.getName(), "shared").setBoolean(t_, True)
        return t_
    ak_old_est = acf(ESTk.class_.getName(), "ASSET_STORE").get(None)
    ak_est_map = indexed({"SignatureEnergy": ak_stat("SignatureEnergy", 0.0), "SignatureCharges": ak_stat("SignatureCharges", 100.0)})
    fz(ILT, "nextIndex").set(ak_est_map, JClass("java.util.concurrent.atomic.AtomicInteger")(2))
    acf(ESTk.class_.getName(), "ASSET_STORE").set(None, zstore(ak_est_map))
    ak_old_sig = int(acf(DSTk.class_.getName(), "SIGNATURE_ENERGY").getInt(None))
    acf(DSTk.class_.getName(), "SIGNATURE_ENERGY").setInt(None, JInt(0))
    EI, CI = 0, 1
    # a bare JVM has no GameplayConfig asset store: an empty one -> World.getGameplayConfig() answers GameplayConfig.DEFAULT (the engine's own)
    ak_old_gpc = acf(GPCk.class_.getName(), "ASSET_STORE").get(None)
    acf(GPCk.class_.getName(), "ASSET_STORE").set(None, zstore(DAMz()))
    ak_world = acalloc(ENGK + "universe.world.World")
    ak_wcfg = acalloc(ENGK + "universe.world.WorldConfig")
    acf(ENGK + "universe.world.World", "worldConfig").set(ak_world, ak_wcfg)
    acf(ENGK + "universe.world.WorldConfig", "gameplayConfig").set(ak_wcfg, "Default")
    ak_es = acalloc(ENGK + "universe.world.storage.EntityStore")
    acf(ENGK + "universe.world.storage.EntityStore", "world").set(ak_es, ak_world)
    ak_old_ext = AcBuf.EXT
    AcBuf.EXT = ak_es

    # ---- the items (real Item objects in the item asset map; the Weapon block like the vanilla templates)
    def ak_weapon(energy_, charges_=None, clear_=True):
        w_ = IWPk()
        mm_ = I2Ok()
        a_ = SMOA(1)
        a_[0] = SMO(MTG.MAX, CAL.ADDITIVE, JFloat(energy_))
        mm_.put(JInt(EI), a_)
        cl_ = [EI]
        if charges_ is not None:
            b_ = SMOA(1)
            b_[0] = SMO(MTG.MAX, CAL.ADDITIVE, JFloat(charges_))
            mm_.put(JInt(CI), b_)
            cl_.append(CI)
        fz(IWPk, "statModifiers").set(w_, mm_)
        fz(IWPk, "entityStatsToClear").set(w_, JArray(JInt)(cl_) if clear_ else None)
        return w_

    def ak_item(id_, weapon_):
        ob_ = UZ.allocateInstance(ItemZ.class_)
        fz(ItemZ, "id").set(ob_, id_)
        fz(ItemZ, "maxStack").setInt(ob_, 1)
        fz(ItemZ, "weapon").set(ob_, weapon_)
        fz(ItemZ, "utility").set(ob_, UTLk())         # every real Item has its (default) ItemUtility; the engine's recalc asks isCompatible()
        return ob_
    plain_w = IWPk()
    fz(IWPk, "statModifiers").set(plain_w, I2Ok())
    AKI = {"SkSig_Sword": ak_item("SkSig_Sword", ak_weapon(20.0)),               # Template_Weapon_Sword: SignatureEnergy +20, clears it
           "SkSig_Daggers": ak_item("SkSig_Daggers", ak_weapon(27.0)),           # Template_Weapon_Daggers +27
           "SkSig_Crossbow": ak_item("SkSig_Crossbow", ak_weapon(5.0, 1.0)),     # Template_Weapon_Crossbow +5 / SignatureCharges +1, clears both
           "SkSig_Pack": ak_item("SkSig_Pack", ak_weapon(50.0, None, False)),    # a pack weapon: a signature max, NO EntityStatsToClear
           "SkSig_PackBow": ak_item("SkSig_PackBow", ak_weapon(6.0, 1.0, False)),   # a pack bow: both maxes, NO EntityStatsToClear
           "SkSig_Plain": ak_item("SkSig_Plain", plain_w),                      # a weapon without a signature
           "SkSig_Stone": ak_item("SkSig_Stone", None),                         # not a weapon
           "Weapon_Crossbow_SkSig": ak_item("Weapon_Crossbow_SkSig", ak_weapon(5.0, 1.0))}   # a crossbow id SkyySkills' perk covers (AK8)
    ak_old_items = dict((k_, imap.get(k_)) for k_ in AKI)
    for k_, v_ in AKI.items():
        imap.put(k_, v_)

    def ak_stack(id_, dur_=100.0):
        return IS(id_, JInt(1), float(dur_), 100.0, None)
    U9 = UUID.fromString("00000000-0000-0000-0000-0000000000c9")
    hotk = SIC(sh(9))
    hck = mkinv("Hotbar", hotk, 0)
    smk = ESMk()
    smk.update()
    prk = acalloc(PRk.class_.getName())
    acf(PRk.class_.getName(), "uuid").set(prk, U9)
    acf(PRk.class_.getName(), "username").set(prk, "AkSig")
    refk = UZ.allocateInstance(REFc.class_)
    acf(RFc, "index").setInt(refk, JInt(91))
    AKC = {}

    def ak_comps(dead_=False):
        AKC.clear()
        AKC.update({"pr": prk, "hot": hck, "esm": smk})
        if dead_:
            AKC["dth"] = acalloc(DTHk.class_.getName())
        AcChunk.REF = refk
        AcChunk.COMP.clear()
        m_ = IdMap()
        for k_, v_ in AKC.items():
            AcChunk.COMP.put(CTK[k_], v_)
            m_.put(CTK[k_], v_)
        AcBuf.COMP.put(refk, m_)
    ak_comps()
    # the engine's slot-change system reads the held item through its Store argument: a Store subclass made here answers the same fixtures
    StoreK = mkfake("SkyySigStore", "com.hypixel.hytale.component.Store", [
        "public %s getComponent(%s r, %s t) { java.util.IdentityHashMap m = (java.util.IdentityHashMap) %s.COMP.get(r); if (m == null) return null; return (%s) m.get(t); }"
        % (CMPc, RFc, CTc, AcBufC.getName(), CMPc)])
    stk_ = UZ.allocateInstance(StoreK)
    eng_sys = ASCk()
    sig_sys = SigSlot()
    inv_sys = SigInv()
    tick_sys = SigTick(False)
    SMM = smk.getStatModifiersManager()

    def ev_e():
        return float(smk.get(JInt(EI)).get())

    def ev_c():
        return float(smk.get(JInt(CI)).get())

    def mx_e():
        return float(smk.get(JInt(EI)).getMax())

    def active():
        return int(hck.getActiveSlot())

    def engine_recalc():
        # EntityStatsSystems$Recalculate.tick: the engine's own recalc (returns at once when nothing was scheduled)
        SMM.recalculateEntityStatModifiers(refk, smk, buf_)

    def swap(to_, ours_first=True, section_=None):
        # Hotbar.setActiveSlot: the slot is set FIRST, then InventorySetActiveSlotEvent is dispatched to every system on it (synchronously)
        prev_ = active()
        acf(ENGK + "inventory.ActiveSlotInventoryComponent", "activeSlot").setByte(hck, ByteK.parseByte(str(to_)))
        e_ = ISAEk(JInt(int(hck.getSectionId()) if section_ is None else section_), JInt(prev_), ByteK.parseByte(str(to_)))
        if ours_first:
            sig_sys.handle(JInt(0), chk_, None, buf_, e_)
            eng_sys.handle(JInt(0), chk_, stk_, buf_, e_)
        else:
            eng_sys.handle(JInt(0), chk_, stk_, buf_, e_)
            sig_sys.handle(JInt(0), chk_, None, buf_, e_)

    def tick(engine_first=False):
        if engine_first:
            engine_recalc()
        tick_sys.tick(JFloat(0.05), JInt(0), chk_, None, buf_)
        engine_recalc()        # the engine's Recalculate later in the same tick: must change nothing any more

    def earn(v_, c_=None):
        smk.setStatValue(JInt(EI), JFloat(v_))
        if c_ is not None:
            smk.setStatValue(JInt(CI), JFloat(c_))

    def hotset(slot_, stack_):
        tx_ = hotk.setItemStackForSlot(sh(slot_), stack_)
        e_ = ICEk(CTK["hot"], hck, hotk, tx_)
        inv_sys.handle(JInt(0), chk_, None, buf_, e_)
        return tx_

    def reset_all():
        Sig.STATE.clear()
        for i_ in range(9):
            hotk.setItemStackForSlot(sh(i_), None)
        acf(ENGK + "inventory.ActiveSlotInventoryComponent", "activeSlot").setByte(hck, ByteK.parseByte("0"))
        ak_comps()

    def hold(slot_, stack_, charge_=None, chg_=None):
        # put a weapon in a slot and hold it with the meter settled the vanilla way (the engine clears + sets the max), then earn a charge
        reset_all()
        hotk.setItemStackForSlot(sh(slot_), stack_)
        acf(ENGK + "inventory.ActiveSlotInventoryComponent", "activeSlot").setByte(hck, ByteK.parseByte(str(slot_)))
        SMM.queueEntityStatsToClear(JArray(JInt)([EI, CI]))
        SMM.scheduleRecalculate()
        engine_recalc()
        if charge_ is not None:
            earn(charge_, chg_)

    # ---- AK0: the model + the vanilla reset itself (no GearSig: the row off)
    Cfg.SIG_KEEP = False
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    m0_ = mx_e()
    e0_ = ev_e()
    swap(2)
    e1_ = ev_e()                      # the event only QUEUES: the meter is still intact while it is dispatched
    tick()
    e2_, m2_ = ev_e(), mx_e()
    swap(0)
    tick()
    e3_, m3_ = ev_e(), mx_e()
    check(m0_ == 20.0 and e0_ == 15.0 and e1_ == 15.0 and e2_ == 0.0 and m2_ == 0.0 and e3_ == 0.0 and m3_ == 20.0 and Sig.STATE.isEmpty(),
          "AK0: the engine model = the vanilla reset (row off): sword max %s holds 15 -> swap to a stone: the meter is intact during the event (%s), "
          "then the engine's recalc gives max %s / %s -> back on the sword: max %s, meter %s (reset)" % (m0_, e1_, m2_, e2_, m3_, e3_))
    Cfg.SIG_KEEP = True

    # ---- AK1: swap away (non-weapon) and back -> kept, cleared by the engine, restored
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    n0_ = [int(x_) for x_ in Sig.N]
    swap(2)
    k1_ = int(Sig.kept(U9))
    p1_ = bool(Sig.pending(U9))
    tick()
    e1_, p1b_ = ev_e(), bool(Sig.pending(U9))
    swap(0)
    tick()
    e2_, m2_ = ev_e(), mx_e()
    n1_ = [int(x_) for x_ in Sig.N]
    check(k1_ == 1 and p1_ and e1_ == 0.0 and not p1b_ and e2_ == 15.0 and m2_ == 20.0 and Sig.STATE.isEmpty() and n1_[0] - n0_[0] == 1
          and n1_[1] - n0_[1] == 1,
          "AK1: sword 15/20 -> stone (kept 1, pending %s; the engine clamps the meter to %s) -> back on the sword: restored %s / %s, nothing left "
          "kept (counters %s -> %s)" % (p1_, e1_, e2_, m2_, n0_, n1_))
    # the same through a weapon WITH its own signature in between (daggers clear the meter on equip): each comes back
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(1), ak_stack("SkSig_Daggers"))
    swap(1)
    tick()
    ed_ = ev_e()
    earn(9.0)
    swap(0)
    tick()
    es_ = ev_e()
    swap(1)
    tick()
    ed2_, md2_ = ev_e(), mx_e()
    check(ed_ == 0.0 and es_ == 15.0 and ed2_ == 9.0 and md2_ == 27.0,
          "AK1: sword 15 -> daggers start at %s (vanilla clear), earn 9 -> sword back to %s -> daggers back to %s / %s" % (ed_, es_, ed2_, md2_))
    # negative control: the row off -> the vanilla reset; a non-hotbar section event is ignored
    Cfg.SIG_KEEP = False
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(2)
    tick()
    swap(0)
    tick()
    eoff_ = ev_e()
    Cfg.SIG_KEEP = True
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(2, True, -5)
    sec_ = int(Sig.kept(U9))
    check(eoff_ == 0.0 and sec_ == 0, "AK1: negative controls - gear.signatureKeep off = the vanilla reset (%s); a utility-section slot event keeps "
          "nothing (%s)" % (eoff_, sec_))

    # ---- AK2: drop / move / another item -> the kept charge is gone (GearSigInvSys on the hotbar's InventoryChangeEvent)
    def away_keep():
        hold(0, ak_stack("SkSig_Sword"), 15.0)
        hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
        swap(2)
        tick()
        return int(Sig.kept(U9))
    r_ = {}
    k_ = away_keep()
    hotset(0, None)                                   # dropped / traded away
    hotk.setItemStackForSlot(sh(0), ak_stack("SkSig_Sword"))   # a fresh identical sword put back without an event (the restore check still runs)
    swap(0)
    tick()
    r_["drop"] = (k_, int(Sig.kept(U9)), ev_e())
    k_ = away_keep()
    st0_ = hotk.getItemStack(sh(0))
    hotset(0, None)                                   # moved to slot 7 (two transactions, like a drag)
    hotset(7, st0_)
    hotset(0, ak_stack("SkSig_Sword", 100.0))         # ... and another identical sword dragged in
    swap(0)
    tick()
    r_["move"] = (k_, ev_e())
    k_ = away_keep()
    hotset(0, ak_stack("SkSig_Daggers"))              # another item in that slot
    swap(0)
    tick()
    r_["other"] = (k_, ev_e())
    k_ = away_keep()
    hotset(0, ak_stack("SkSig_Sword", 64.0))          # the same id with another durability (another sword) in the slot
    swap(0)
    tick()
    r_["dur"] = (k_, ev_e())
    k_ = away_keep()
    hotset(5, ak_stack("SkSig_Stone"))                # a change in ANOTHER slot keeps it
    hotset(0, hotk.getItemStack(sh(0)).withMetadata(BD()))  # the same sword re-written (a tooltip re-render: same id + durability) keeps it
    swap(0)
    tick()
    r_["keep"] = (k_, ev_e())
    check(r_["drop"] == (1, 0, 0.0) and r_["move"] == (1, 0.0) and r_["other"] == (1, 0.0) and r_["dur"] == (1, 0.0) and r_["keep"] == (1, 15.0),
          "AK2: a kept slot loses its charge when the item is dropped, moved away (even with an identical sword dragged in), replaced or a "
          "different sword; a change in another slot / a re-render of the same item keeps it: %s" % r_)

    # ---- AK3: two identical weapons keep their own charges; clamp; the bow's charges
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(3), ak_stack("SkSig_Sword"))
    swap(3)
    tick()
    t1_ = ev_e()
    earn(7.0)
    swap(0)
    tick()
    t2_ = ev_e()
    swap(3)
    tick()
    t3_ = ev_e()
    swap(0)
    tick()
    t4_ = ev_e()
    check(t1_ == 0.0 and t2_ == 15.0 and t3_ == 7.0 and t4_ == 15.0,
          "AK3: two identical swords in slots 0 / 3 keep their own charges: twin starts %s, slot 0 back %s, slot 3 back %s, slot 0 again %s" % (t1_, t2_, t3_, t4_))
    hold(1, ak_stack("SkSig_Daggers"), 25.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(2)
    tick()
    keepw_ = AKI["SkSig_Daggers"].getWeapon()
    smallw_ = ak_weapon(10.0)
    fz(ItemZ, "weapon").set(AKI["SkSig_Daggers"], smallw_)      # the weapon's max changed while away (an asset reload)
    swap(1)
    tick()
    cl_ = (ev_e(), mx_e())
    fz(ItemZ, "weapon").set(AKI["SkSig_Daggers"], keepw_)
    hold(4, ak_stack("SkSig_Crossbow"), 5.0, 1.0)              # a full meter turned into the loaded big shot (SignatureCharges 1)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(2)
    tick()
    cb0_ = (ev_e(), ev_c())
    swap(4)
    tick()
    cb1_ = (ev_e(), ev_c(), float(smk.get(JInt(CI)).getMax()))
    check(cl_ == (10.0, 10.0) and cb0_ == (0.0, 1.0) and cb1_ == (5.0, 1.0, 101.0),
          "AK3: a kept 25 comes back clamped to the new max (%s); the crossbow's meter AND its loaded shot both come back (%s) - on the stone "
          "the engine clamps the meter to 0 and leaves the shot floating (%s), then the crossbow's own EntityStatsToClear wipes both on equip "
          "(the vanilla loss) before the restore" % (cl_, cb1_, cb0_))

    # ---- AK4: death / logout / world switch / profile switch / busy / row off -> forgotten
    res4_ = {}
    away_keep()
    ak_comps(True)
    tick()
    gone_ = Sig.STATE.isEmpty()
    ak_comps()
    swap(0)
    tick()
    res4_["death"] = (gone_, ev_e())
    away_keep()
    pde_ = acalloc(ENGK + "event.events.player.PlayerDisconnectEvent")
    fpr_ = None
    c_ = pde_.getClass()
    while c_ is not None and fpr_ is None:
        for fd_ in c_.getDeclaredFields():
            if str(fd_.getName()) == "playerRef":
                fpr_ = fd_
        c_ = c_.getSuperclass()
    fpr_.setAccessible(True)
    fpr_.set(pde_, prk)
    SigBye().accept(pde_)
    gone_ = Sig.STATE.isEmpty()
    swap(0)
    tick()
    res4_["logout"] = (gone_, ev_e())
    away_keep()
    # PlayerReadyEvent (join / world switch): its Ref -> a Store that answers the PlayerRef (a Store subclass made here, like the AC shim)
    acf(RFc, "store").set(refk, stk_)
    pre_ = acalloc(ENGK + "event.events.player.PlayerReadyEvent")
    fpr_ = None
    c_ = pre_.getClass()
    while c_ is not None and fpr_ is None:
        for fd_ in c_.getDeclaredFields():
            if str(fd_.getName()) == "playerRef":
                fpr_ = fd_
        c_ = c_.getSuperclass()
    fpr_.setAccessible(True)
    fpr_.set(pre_, refk)
    SigBye().accept(pre_)
    gone_ = Sig.STATE.isEmpty()
    acf(RFc, "store").set(refk, None)
    swap(0)
    tick()
    res4_["world"] = (gone_, ev_e())
    away_keep()
    bridge.put("profile:epoch:" + str(U9), "2")          # SkyyProfiles moved this player's profile epoch (a profile switch)
    swap(0)
    tick()
    res4_["profile"] = (Sig.STATE.isEmpty(), ev_e())
    away_keep()
    bridge.put("profile:busy:" + str(U9), "switching")   # mid-switch: forgotten on the next pass, nothing kept while busy
    tick()
    b1_ = Sig.STATE.isEmpty()
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    bcode_ = int(Sig.leave(U9, hotk, smk, 0, 2))
    bridge.remove("profile:busy:" + str(U9))
    res4_["busy"] = (b1_, bcode_, int(Sig.kept(U9)))
    away_keep()
    Cfg.SIG_KEEP = False
    tick()
    off_ = Sig.STATE.isEmpty()
    Cfg.SIG_KEEP = True
    swap(0)
    tick()
    res4_["off"] = (off_, ev_e())
    bridge.remove("profile:epoch:" + str(U9))
    check(res4_ == {"death": (True, 0.0), "logout": (True, 0.0), "world": (True, 0.0), "profile": (True, 0.0), "busy": (True, 4, 0),
                    "off": (True, 0.0)},
          "AK4: forgotten (and nothing restored afterwards) on death / logout / world switch / profile switch / profile:busy / the row off: %s" % res4_)

    # ---- AK5: no dupe
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(1), ak_stack("SkSig_Daggers"))
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(1)
    swap(2)                     # a second swap inside the same tick: the meter still shows the SWORD's 15 - must not be kept for the daggers
    tick()
    d1_ = (int(Sig.kept(U9)), ev_e())
    swap(1)
    tick()
    d2_ = ev_e()
    swap(0)
    tick()
    d3_ = ev_e()
    check(d1_ == (1, 0.0) and d2_ == 0.0 and d3_ == 15.0,
          "AK5: two swaps in one tick (sword 15 -> daggers -> stone): only the sword's 15 is kept (%s), the daggers get nothing (%s), the sword "
          "gets its 15 back once (%s)" % (d1_, d2_, d3_))
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(2)
    swap(0)                     # away and back inside one tick
    tick()
    a1_ = (ev_e(), int(Sig.kept(U9)))
    swap(2)
    tick()
    swap(0)
    tick()
    a2_ = ev_e()
    check(a1_ == (15.0, 0) and a2_ == 15.0, "AK5: away-and-back inside one tick restores exactly once (%s), a later swap still works (%s)" % (a1_, a2_))
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(5), ak_stack("SkSig_Pack"))
    swap(5)
    tick()
    p1_ = (ev_e(), int(Sig.kept(U9)))             # the engine CARRIED 15 to the pack weapon (no EntityStatsToClear): nothing stays kept for the sword
    swap(0)
    tick()
    p2_ = ev_e()
    swap(5)
    tick()
    p3_ = ev_e()
    check(p1_ == (15.0, 0) and p2_ == 0.0 and p3_ == 15.0,
          "AK5: a pack weapon the engine carries the meter to: the carried 15 comes OFF the sword's kept value (%s); sword back = %s; the pack "
          "weapon's own 15 comes back to it (%s) - never 30" % (p1_, p2_, p3_))
    hold(4, ak_stack("SkSig_Crossbow"), 5.0, 1.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    hotk.setItemStackForSlot(sh(6), ak_stack("SkSig_PackBow"))
    swap(2)
    tick()
    q1_ = (ev_e(), ev_c())         # the stone: energy clamped to 0 (max 0), the loaded shot FLOATS (SignatureCharges base max 100)
    swap(6)
    tick()
    q2_ = (ev_e(), ev_c())         # a pack bow that does not clear: it can USE the floating shot -> it comes off the crossbow's kept value
    swap(4)
    tick()
    q3_ = (ev_e(), ev_c())
    check(q1_ == (0.0, 1.0) and q2_ == (0.0, 1.0) and q3_ == (5.0, 0.0),
          "AK5: a loaded shot left floating on a stone is not kept twice: stone %s -> a pack bow that can fire it %s -> the crossbow gets its "
          "meter back but not the shot the pack bow had (%s) - one shot in all" % (q1_, q2_, q3_))
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(2, False)
    tick(True)
    swap(0, False)
    tick(True)
    o1_ = ev_e()
    plain_ = None
    hold(6, ak_stack("SkSig_Plain"), None)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    plain_ = int(Sig.leave(U9, hotk, smk, 6, 2))
    Sig.STATE.clear()
    check(o1_ == 15.0 and plain_ == 2, "AK5: the engine's Recalculate BEFORE GearSigTick (the other system order) gives the same restore (%s); a "
          "weapon without a signature keeps nothing (leave = %s)" % (o1_, plain_))

    # ---- AK8: the review fixes (2026-10-08)
    from jpype import JImplements as JImpl8, JOverride as JOver8

    @JImpl8("java.util.function.Function")
    class SkillsCfgStub(object):
        def __init__(self, items_):
            self.items_ = items_
            self.calls_ = []

        @JOver8
        def apply(self, a_):
            self.calls_.append([str(x_) for x_ in a_])
            if len(a_) >= 2 and str(a_[0]) == "get" and str(a_[1]) == "perk.archery.keepLoaded.items":
                return self.items_
            return None

    def xb_round(stack_id_):
        Sig.XBC = None
        hold(4, ak_stack(stack_id_), 5.0, 1.0)
        hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
        swap(2)
        tick()
        k_ = int(Sig.kept(U9))
        swap(4)
        tick()
        return (k_, ev_e(), ev_c())
    r8_ = {}
    r8_["no skills"] = xb_round("Weapon_Crossbow_SkSig")              # SkyySkills not loaded: Gear keeps the crossbow too
    stub_ = SkillsCfgStub("Weapon_Crossbow_")
    bridge.put("config:def:SkyySkills", "SkyySkills")
    bridge.put("config:fn:SkyySkills", stub_)
    r8_["skills"] = xb_round("Weapon_Crossbow_SkSig")                 # left to SkyySkills: nothing kept, nothing restored by Gear
    Sig.XBC = None
    hold(4, ak_stack("Weapon_Crossbow_SkSig"), 5.0, 1.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    r8_["code"] = int(Sig.leave(U9, hotk, smk, 4, 2))
    Sig.STATE.clear()
    sw_ = []
    hold(0, ak_stack("SkSig_Sword"), 15.0)                             # a sword is still Gear's with SkyySkills loaded
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    swap(2)
    tick()
    sw_.append(int(Sig.kept(U9)))
    swap(0)
    tick()
    sw_.append(ev_e())
    r8_["sword"] = tuple(sw_)
    stub_.items_ = ""                                                  # an empty answer = SkyySkills' own default Weapon_Crossbow_
    r8_["empty"] = xb_round("Weapon_Crossbow_SkSig")
    stub_.items_ = "Weapon_Crossbow_Other, Something_"                 # SkyySkills covers other ids only: Gear keeps this one
    r8_["other"] = xb_round("Weapon_Crossbow_SkSig")
    calls_ = len(stub_.calls_)
    Sig.XBC = None
    a8_ = [str(x_) for x_ in Sig.xbowPrefixes()]
    b8_ = [str(x_) for x_ in Sig.xbowPrefixes()]                     # cached: no second call inside 5 s
    cache_ok_ = len(stub_.calls_) == calls_ + 1 and a8_ == b8_ == ["Weapon_Crossbow_Other", "Something_"]
    bridge.remove("config:fn:SkyySkills")
    bridge.remove("config:def:SkyySkills")
    Sig.XBC = None
    check(r8_ == {"no skills": (1, 5.0, 1.0), "skills": (0, 0.0, 0.0), "code": 5, "sword": (1, 15.0), "empty": (0, 0.0, 0.0),
                  "other": (1, 5.0, 1.0)} and cache_ok_ and Sig.STATE.isEmpty(),
          "AK8: review fix 1 - with SkyySkills loaded its crossbow ids (perk.archery.keepLoaded.items via config:fn:SkyySkills get; empty = "
          "Weapon_Crossbow_) are left to its Archer perk (not kept / not restored, leave code 5) while a sword still is; without SkyySkills or "
          "for an id it does not cover Gear keeps the crossbow; the id list is cached: %s, cache %s" % (r8_, cache_ok_))
    # review fix 2: the tick system's ordering
    RECk = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Recalculate")
    old_rec_ = SigTick.RECALC
    SigTick.RECALC = RECk.class_
    dO_ = list(SigTick(True).getDependencies())
    dU_ = list(SigTickU().getDependencies())
    dF_ = list(SigTick(False).getDependencies())
    SigTick.RECALC = None
    dN_ = list(SigTick(True).getDependencies())
    SigTick.RECALC = old_rec_
    ord_ok_ = (len(dO_) == 1 and dO_[0].getSystemClass() == RECk.class_ and "AFTER" in str(dO_[0]) and not dU_ and not dF_
               and not dN_ and isinstance(SigTickU(), SigTick) and not bool(SigTick(True).isParallel(JInt(1), JInt(1))))
    check(ord_ok_, "AK8: review fix 2 - GearSigTick(true) runs AFTER EntityStatsSystems$Recalculate (%s); the fallback GearSigTickU / no "
          "Recalculate class = unordered (%s / %s / %s)" % ([str(d_) for d_ in dO_], len(dU_), len(dF_), len(dN_)))
    # review fix 3: an entry re-made after the logout clean-up is swept
    UX = UUID.fromString("00000000-0000-0000-0000-0000000000ca")
    away_keep()
    Sig.state(UX, True)
    on_ = JClass("java.util.HashSet")()
    on_.add(U9)
    sw1_ = int(Sig.sweepWith(on_))
    sw1k_ = (bool(Sig.STATE.containsKey(U9)), bool(Sig.STATE.containsKey(UX)))
    SigBye().accept(pde_)                                              # this player's logout clean-up (forget + sweep)
    hold(0, ak_stack("SkSig_Sword"), 15.0)
    hotk.setItemStackForSlot(sh(2), ak_stack("SkSig_Stone"))
    Sig.STATE.clear()
    late_ = int(Sig.leave(UX, hotk, smk, 0, 2))                        # a late slot event of a player (UX) whose logout clean-up already ran
    late_in_ = bool(Sig.STATE.containsKey(UX))
    uni_ = ak_inst(ENGK + "universe.Universe").get(None)
    fpl_ = acf(ENGK + "universe.Universe", "players")
    old_pl_ = fpl_.get(uni_)
    pl_ = JClass("java.util.ArrayList")()
    pl_.add(prk)
    fpl_.set(uni_, pl_)                                                # only U9 is online
    acf(RFc, "store").set(refk, stk_)
    SigBye().accept(pre_)                                              # U9's next PlayerReadyEvent sweeps UX's leftover entry
    acf(RFc, "store").set(refk, None)
    sw2_ = bool(Sig.STATE.containsKey(UX))
    Sig.state(U9, True)                                                # an online player's entry: sweep() keeps it
    sw3_ = (int(Sig.sweep()), bool(Sig.STATE.containsKey(U9)))
    fpl_.set(uni_, old_pl_)
    sw4_ = int(Sig.sweep())                                            # no player list (bare JVM): sweeps nothing, never throws
    Sig.STATE.clear()
    check(sw1_ == 1 and sw1k_ == (True, False) and late_ == 1 and late_in_ and not sw2_ and sw3_ == (0, True) and sw4_ == 0,
          "AK8: review fix 3 - sweepWith drops only players not online (%s %s); a late slot event after logout re-makes the entry (%s %s) and "
          "the next ready / logout sweep removes it (%s); an online player stays (%s); no player list = no sweep (%s)"
          % (sw1_, sw1k_, late_, late_in_, not sw2_, sw3_, sw4_))

    # ---- AK6: the row + the fresh file
    rk_ = [str(k_) for k_ in Rows.KEYS]
    ri_ = rk_.index("gear.signatureKeep") if "gear.signatureKeep" in rk_ else -1
    dt_ = str(Cfg.defaultsText())
    p0_ = Props()
    Cfg.apply(p0_, False)
    on0_ = bool(Cfg.SIG_KEEP)
    p1k_ = Props()
    p1k_.setProperty("gear.signatureKeep", "false")
    Cfg.apply(p1k_, False)
    off1_ = bool(Cfg.SIG_KEEP)
    Cfg.apply(Props(), False)
    check(ri_ >= 0 and str(Rows.TYPES[ri_]) == "bool" and str(Rows.DEFS[ri_]) == "true" and str(Rows.FLAGS[ri_]) == "live"
          and len(str(Rows.HELPS[ri_])) <= 100 and dt_.endswith("\n# ---- signature charge kept on a weapon swap (SkyyGear 0.2.10) ----\n# "
                                                                 "Keep signature charge on weapon swap: " + str(Rows.HELPS[ri_]) + "\ngear.signatureKeep=true\n")
          and on0_ and not off1_ and "signature charge kept on a weapon swap on" in str(Sig.statusText()),
          "AK6: Server Setup -> Gear -> Combat row gear.signatureKeep (bool, default true, live, no danger); the fresh file ends with it; a missing "
          "line = on, 'false' = off")
    print("AK. counters: %s" % Sig.counters())

    # ---- restore what AK changed
    for k_, v_ in ak_old_items.items():
        if v_ is None:
            imap.remove(k_)
        else:
            imap.put(k_, v_)
    acf(ESTk.class_.getName(), "ASSET_STORE").set(None, ak_old_est)
    acf(DSTk.class_.getName(), "SIGNATURE_ENERGY").setInt(None, JInt(ak_old_sig))
    acf(GPCk.class_.getName(), "ASSET_STORE").set(None, ak_old_gpc)
    acf(EFFk.class_.getName(), "STORE").set(None, ak_old_eff)
    AcBuf.EXT = ak_old_ext
    AcBuf.COMP.remove(refk)
    AcChunk.COMP.clear()
    for cn_, o_ in ak_old_single.items():
        ak_inst(cn_).set(None, o_)
    Sig.STATE.clear()

    # ---- AK7. class byte-compare 0.2.9 -> 0.2.10
    EXPECT0210 = @@EXPECT0210@@
    NEW0210 = ["GearSig", "GearSigBye", "GearSigInvSys", "GearSigSlotSys", "GearSigTick", "GearSigTickU"]
    jar029 = os.path.join(HERE, "SkyyGear-0.2.9.jar")
    if os.path.isfile(jar029) and "cls_members" in dir():
        pa10 = Pool(False)
        pa10.appendClassPath(jar029)
        pa10.appendClassPath(B.SERVER_JAR)
        pa10.appendSystemPath()
        pb10 = Pool(False)
        pb10.appendClassPath(jar)
        pb10.appendClassPath(B.SERVER_JAR)
        pb10.appendSystemPath()
        na10 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar029).namelist() if n_.endswith(".class"))
        nb10 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
        diffs10 = {}
        for cn_ in sorted(set(na10) & set(nb10)):
            ma_, mb_ = cls_members(pa10, cn_), cls_members(pb10, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs10[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        print("AK7. class compare 0.2.9 -> 0.2.10: %s; added %s" % (json.dumps(diffs10, sort_keys=True), sorted(set(nb10) - set(na10))))
        check(not (set(na10) - set(nb10)) and sorted(c_[len(PKG):] for c_ in set(nb10) - set(na10)) == NEW0210,
              "AK7: the six GearSig classes added, none removed: %s" % sorted(set(na10) ^ set(nb10)))
        unexp10 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT0210.get(c_, [])]) for c_, v_ in diffs10.items())
        unexp10 = dict((c_, v_) for c_, v_ in unexp10.items() if v_)
        missing10 = dict((c_, [m_ for m_ in v_ if m_ not in diffs10.get(c_, [])]) for c_, v_ in EXPECT0210.items())
        missing10 = dict((c_, v_) for c_, v_ in missing10.items() if v_)
        check(not unexp10, "AK7: no difference outside the listed 0.2.10 parts: %s" % unexp10)
        check(not missing10, "AK7: every listed 0.2.10 part is really in the jar: %s" % missing10)
        za10, zb10 = zipfile.ZipFile(jar029), zipfile.ZipFile(jar)
        ea10 = [n_ for n_ in za10.namelist() if not n_.endswith(".class")]
        eb10 = [n_ for n_ in zb10.namelist() if not n_.endswith(".class")]
        ediff10 = sorted(n_ for n_ in set(ea10) | set(eb10) if n_ not in ea10 or n_ not in eb10 or za10.read(n_) != zb10.read(n_))
        check(ediff10 == ["manifest.json"], "AK7: non-class entries: only manifest.json changed (no asset): %s" % ediff10)
        # setup() (never run in a bare JVM): the three systems through the guarded _reg loop + GearSigBye on both events (bytecode)
        IPk = JClass("javassist.bytecode.InstructionPrinter")
        bos_ = JClass("java.io.ByteArrayOutputStream")()
        IPk(JClass("java.io.PrintStream")(bos_)).print_(pb10.get(PKG + "SkyyGearPlugin").getDeclaredMethod("setup"))
        su_ = str(bos_.toString())
        reg_ = [l_ for l_ in su_.splitlines() if "<init>" in l_ and "GearSig" in l_]
        check(len([l_ for l_ in reg_ if "GearSigSlotSys.<init>" in l_]) == 1 and len([l_ for l_ in reg_ if "GearSigInvSys.<init>" in l_]) == 1
              and len([l_ for l_ in reg_ if "GearSigTick.<init>" in l_]) == 1 and len([l_ for l_ in reg_ if "GearSigTickU.<init>" in l_]) == 1
              and len([l_ for l_ in reg_ if "GearSigBye.<init>" in l_]) == 2
              and su_.count("PlayerReadyEvent") >= 2 and su_.count("PlayerDisconnectEvent") >= 2 and "EntityStatsSystems$Recalculate" in su_
              and "GearSigTick.RECALC" in su_,
              "AK7: setup() creates GearSigSlotSys / GearSigInvSys once each (the guarded registerSystem loop), GearSigTick(true) ordered after "
              "EntityStatsSystems$Recalculate with the GearSigTickU fallback, and GearSigBye for PlayerDisconnectEvent + PlayerReadyEvent: %s"
              % [l_.strip()[:90] for l_ in reg_])
    else:
        check(False, "AK7: SkyyGear-0.2.9.jar (or the compare helper) not found - the class compare could not run")
    Cfg.apply(Props(), False)
    print("AK. 0.2.10 done")

'''
EXPECT0210 = {
    # VERSION text: CfgRows VERSION, the export header, the fresh file's first line, the ready line; the new row (CfgRows tables)
    'CfgFn': ['~m opExport([Ljava/lang/Object;)Ljava/lang/Object;'],
    'CfgRows': ['~<clinit>', '~f VERSION', '~m header()[Ljava/lang/Object;'],
    # the kit's row tables (the new row)
    'CfgFile': ['~<clinit>'],
    # the SIG_KEEP field + its loader line, the fresh file text
    'GearCfg': ['~<clinit>', '+f SIG_KEEP', '~m apply(Ljava/util/Properties;Z)V', '~m defaultsText()Ljava/lang/String;'],
    # the registrations + the ready line
    'SkyyGearPlugin': ['~m setup()V'],
}
AK_SRC = AK_SRC.replace("@@EXPECT0210@@", repr(EXPECT0210))
RESTORE = "    # ---- restore the bare-JVM state this section changed (it is the last section; kept tidy anyway)\n"
sub(RESTORE, AK_SRC + "\n" + RESTORE)
_g = {"__name__": "__main__", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(src, H29 + " (run as the SkyyGear 0.2.10 harness)", "exec"), _g)
