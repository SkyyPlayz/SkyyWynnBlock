"""Harness for SkyyCollections 0.2.13 (UNIQUE SIGILS FROM COLLECTIONS: item rewards + the one-time rewards.properties update;
tools/collections_0_2_13_patch.py). Build first:
    python tools/collections_0_2_13_patch.py && python SkyyCollections/build_skyycollections_0.2.13.py

    python SkyyCollections/test_skyycollections_0.2.13.py [--jar <SkyyCollections-0.2.13.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises
  C   compare  0.2.12 -> 0.2.13: exactly the listed members differ (+ the version texts), CollSigMig added; non-class entries: manifest only
  X   exec     EVERY NEW CODE PATH: the default rewards (tokens + marker), itemAt / itemLabel / rewardTextB / rewardLines, the Server Setup token
               check (every form, one item a tier), THE GIVE on REAL SimpleItemContainers (SECS + ITEMOK seams): a gathered tier VI pays one
               Unique Sigil (marker on disk BEFORE the item, rewards-items.log, counts before / after), never twice, owed while full /
               offline / not loaded, paid by the retry once there is room, tiers without an item never write a marker; CollSigMig.update on the
               LIVE rewards.properties text (read only) and on every hand-edited / removed / CRLF / already-marked variant
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyCollections (the setup sequence BagMigrate, BypassMig, loadAll, CobMig,
               SigMig): the 1st start adds the four tokens + the marker, keeps the old file in config-history, writes 4 Undo rows; the 2nd start
               changes nothing; the loaded table = the old one + the tokens
  AA  audit    the engine-access audit
Not executed here: a crash between the marker save and the add (by construction: the marker is on disk first, so the worst case is one lost
reward, named in rewards-items.log). Exit code 1 on any failure.
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.13"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.12.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear4fix2", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")
TOK = "item:Skyy_Sigil_Unique:1"
# the members 0.2.13 changes (version-text-only: CfgFn opExport / CfgRows header + <clinit> / SkyyCollectionsPlugin setup = the version + the
# CollSigMig.run call in setup; CfgRows <clinit> also carries the Tier rewards row's new help text)
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CollKit": ["~m checkReward", "~m rewardToken"],
          "CollReg": ["+m itemAt", "+m itemLabel", "~m rewardLines", "~m rewardTextB", "~m rewardsText"],
          "CollRewards": ["+f EPSEEN", "+f ITEMOK", "+f ITEMS", "+f SECS", "+f TOLD", "+f WARNI", "+m countIn", "+m giveTier", "+m itemLoaded", "+m itemOwed",
                          "+m noteEpoch", "+m profileHold", "+m pruneTold", "+m secsOf", "+m tellWait", "~<clinit>", "~m owedAny", "~m settle"],
          "CollUnlocks": ["~m publish", "~m publishOnline"], "CollSaver": ["~m run"],          # fixer 2: the epoch stamp, EPSEEN / TOLD pruning
          "SkyyCollectionsPlugin": ["~m setup"]}
ADDED = ["CollSigMig"]


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JShort, JInt, JLong, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Util, Rew, Cred, Kit, Sig, Cob = (P("CollReg"), P("CollStore"), P("CollUtil"), P("CollRewards"), P("CollCredit"), P("CollKit"),
                                                  P("CollSigMig"), P("CollCobMig"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    base = os.path.join(scratch, "x", "Skyy_SkyyCollections")
    os.makedirs(base)
    Reg.BASE = Paths.get(base)
    Store.DIR = Paths.get(base).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    DEF = str(Reg.rewardsText())
    lines = DEF.split("\n")
    K.check(str(Sig.MARK3) in lines and lines.index(str(Sig.MARK3)) == lines.index("# bags: Mining from Cobblestone (0.2.8)") + 1
            and "Wheat.6=recipe:Tool_Sickle_Iron_Recipe_Generated_0," + TOK in lines and "OakLog.6=recipe:Tool_Hatchet_Iron_Recipe_Generated_0," + TOK in lines
            and "Cobblestone.6=recipe:Tool_Pickaxe_Iron_Recipe_Generated_0," + TOK in lines and "Bone.6=" + TOK in lines,
            "X1: a fresh rewards.properties carries the Unique Sigil at tier VI of Wheat / OakLog / Cobblestone / Bone + the run-once marker under the 0.2.8 one")
    cW, cO, cC, cB = [int(R.byId.get(k)) for k in ("wheat", "oaklog", "cobblestone", "bone")]
    it6 = [None if Reg.itemAt(R, c, 6) is None else (str(Reg.itemAt(R, c, 6)[0]), int(Reg.itemAt(R, c, 6)[1])) for c in (cW, cO, cC, cB)]
    K.check(it6 == [("Skyy_Sigil_Unique", 1)] * 4 and Reg.itemAt(R, cW, 5) is None and Reg.itemAt(R, cW, 7) is None,
            "X1: itemAt reads tier VI's item (and nothing on the other tiers): %s" % it6)
    K.check(str(Reg.itemLabel("Skyy_Sigil_Unique", 1)) == "+1 Unique Sigil" and str(Reg.itemLabel("Skyy_Sigil_Mythic", 2)) == "+2 Mythic Sigil"
            and str(Reg.itemLabel("Ingredient_Bar_Iron", 3)).startswith("+3 ") and "+1 Unique Sigil" in str(Reg.rewardTextB(R, cW, 6, False))
            and "+1 Unique Sigil" in [str(x) for x in Reg.rewardLines(R, cB, 6)] and "Sigil" not in str(Reg.rewardTextB(R, cW, 5, False)),
            "X1: the texts: '+1 Unique Sigil' on the tier row + the rank-up lines; other items their pretty name: %s | %s" % (str(Reg.rewardTextB(R, cW, 6, False)), [str(x) for x in Reg.rewardLines(R, cB, 6)]))
    # an admin's own item line: the first item token counts; amounts 1-64
    REW = Reg.REWARDS
    old_tok = REW.get("wheat.2")
    REW.put("wheat.2", JArray(JString)(["coins:5", "item:Ingredient_Bar_Iron:3", "item:Ingredient_Bar_Copper:2"]))
    a2 = Reg.itemAt(R, cW, 2)
    REW.put("wheat.2", JArray(JString)(["item:Ingredient_Bar_Iron:65", "item::2", "item:Ingredient_Bar_Iron:x"]))
    a3 = Reg.itemAt(R, cW, 2)
    REW.put("wheat.2", JArray(JString)(["item:Ingredient_Bar_Iron"]))
    a4 = Reg.itemAt(R, cW, 2)
    if old_tok is None:
        REW.remove("wheat.2")
    else:
        REW.put("wheat.2", old_tok)
    K.check(a2 is not None and str(a2[0]) == "Ingredient_Bar_Iron" and int(a2[1]) == 3 and a3 is None and a4 is not None and int(a4[1]) == 1,
            "X1: the first item token of a tier counts; 65 / no id / not a number are ignored; no amount = 1")
    # the Server Setup check
    rt = [Kit.rewardToken(t) for t in ("item:", "item:Skyy_Sigil_Unique:0", "item:Skyy_Sigil_Unique:65", "item:Skyy_Sigil_Unique:x", "item:a:b:c",
                                       "item:Skyy_Sigil_Unique:1", "item:Skyy_Sigil_Unique", "bogus:1")]
    rt = [None if x is None else str(x) for x in rt]
    K.check(all(x is not None and "item: needs" in x for x in rt[:5]) and rt[5].startswith("?") and rt[6].startswith("?") and "item:<id>:<n>" in rt[7],
            "X2: rewardToken: bad item forms are refused, a good one asks (items are not loaded in a bare JVM - the game checks the id), the "
            "unknown-token text names item:<id>:<n>: %s" % rt)
    two = Kit.checkReward("rewards[Wheat.6]", "recipe:Tool_Sickle_Iron_Recipe_Generated_0,item:Skyy_Sigil_Unique:1,item:Skyy_Sigil_Rare:1")
    K.check(two is not None and "One item reward per tier" in str(two), "X2: checkReward refuses a second item on one tier: %s" % two)
    # ---- THE GIVE on real containers. A bare JVM has no Item asset store (ItemStack's constructor looks its item up): an AssetStore stand-in
    # (a javassist subclass, allocated without a constructor - the SkyyArmory port fixture's way) holding a DefaultAssetMap with the two items
    from jpype import JDouble
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c_, n_):
        k_ = c_.class_ if hasattr(c_, "class_") else c_
        while k_ is not None:
            try:
                f_ = k_.getDeclaredField(n_)
                f_.setAccessible(True)
                return f_
            except Exception:
                k_ = k_.getSuperclass()
        raise KeyError(n_)
    AST, ITMc, DAM = JClass("com.hypixel.hytale.assetstore.AssetStore"), JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item"), JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jcp = JClass("javassist.ClassPool")(True)
    jct = jcp.makeClass("com.hypixel.hytale.assetstore.SkyyCollFakeStore", jcp.get("com.hypixel.hytale.assetstore.AssetStore"))
    jct.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyCollFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", jct))
    HAST = JClass(jct.toClass(AST.class_).getName())
    am_ = us.allocateInstance(DAM.class_)
    jf(DAM, "assetMapLock").set(am_, JClass("java.util.concurrent.locks.StampedLock")())
    mp_ = JClass("java.util.HashMap")()
    for iid_ in ("Skyy_Sigil_Unique", "Rock_Stone"):
        it_ = us.allocateInstance(ITMc.class_)
        jf(ITMc, "id").set(it_, iid_)
        jf(ITMc, "maxStack").setInt(it_, JInt(16 if "Sigil" in iid_ else 100))
        mp_.put(iid_, it_)
    jf(DAM, "assetMap").set(am_, mp_)
    st_ = us.allocateInstance(HAST.class_)
    jf(AST, "assetMap").set(st_, am_)
    jf(ITMc, "ASSET_STORE").set(None, st_)
    SIC, IS = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    ICON = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    INVS = {}

    @JImplements("java.util.function.Function")
    class SecsF(object):
        @JOverride
        def apply(self, u):
            v_ = INVS.get(str(u))
            if v_ is None:
                return None
            return JArray(ICON)(v_)
    LOADED = {"v": True}

    @JImplements("java.util.function.Predicate")
    class ItemOk(object):
        @JOverride
        def test(self, o):
            return bool(LOADED["v"])
    Rew.SECS = SecsF()
    Rew.ITEMOK = ItemOk()

    def secs(n_st=4, n_bp=2, n_hb=2):
        return [SIC(JShort(n_st)), SIC(JShort(n_bp)), SIC(JShort(n_hb))]

    def count(cs_, iid):
        n_ = 0
        for c_ in cs_:
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == iid:
                    n_ += int(s_.getQuantity())
        return n_

    def counts_file(key):
        f_ = os.path.join(base, "counts", key + ".properties")
        return open(f_, encoding="latin-1").read() if os.path.isfile(f_) else ""

    def ilog():
        f_ = os.path.join(base, "rewards-items.log")
        return open(f_, encoding="utf-8").read() if os.path.isfile(f_) else ""
    wheat = str(R.items[cW][0])
    need6 = int(Reg.threshold(R, cW, 6))
    u1 = UUID.fromString("00000000-0000-0000-0000-00000000c001")
    k1 = str(Util.pkey(u1))
    INVS[str(u1)] = secs()
    Cred.creditOne(None, u1, k1, wheat, JLong(need6 - 1), True)
    d1 = Store.dataK(k1)
    m5 = int(Store.meta(d1, "_paiditem.Wheat"))
    Cred.creditOne(None, u1, k1, wheat, JLong(1), True)
    m6 = int(Store.meta(d1, "_paiditem.Wheat"))
    n1 = count(INVS[str(u1)], "Skyy_Sigil_Unique")
    st0 = INVS[str(u1)][0].getItemStack(JShort(0))
    lg = ilog()
    cf = counts_file(k1)
    K.check(m5 == 0 and m6 == 6 and n1 == 1 and st0 is not None and str(st0.getItemId()) == "Skyy_Sigil_Unique" and "_paiditem.Wheat=6" in cf
            and lg.find("GIVE-BEGIN") >= 0 and lg.find("\tGIVE\t") > lg.find("GIVE-BEGIN") and "Wheat.6" in lg and int(Reg.tierOf(R, cW, need6)) == 6,
            "X3: gathering Wheat to tier VI (%d) pays ONE Unique Sigil into STORAGE first; tiers I-V wrote no marker; the marker _paiditem.Wheat=6 is in the "
            "counts file; rewards-items.log GIVE-BEGIN then GIVE: marker %s -> %s, sigils %s" % (need6, m5, m6, n1))
    r_again = list(Rew.settle(d1, R, cW, u1, k1))
    Cred.creditOne(None, u1, k1, wheat, JLong(int(Reg.threshold(R, cW, 7)) - need6), True)
    K.check(count(INVS[str(u1)], "Skyy_Sigil_Unique") == 1 and int(Store.meta(d1, "_paiditem.Wheat")) == 6 and not any(k_.startswith("_paiditem.") and k_ != "_paiditem.Wheat" for k_ in [str(x) for x in d1.meta.keySet()]),
            "X3: never twice (a 2nd settle, tier VII - no item - adds nothing, the marker stays 6); collections without an item reward write no marker")
    # owed: full inventory -> nothing given, marker untouched, owedAny; room -> the retry pays it
    u2 = UUID.fromString("00000000-0000-0000-0000-00000000c002")
    k2 = str(Util.pkey(u2))
    full = secs(1, 1, 1)
    for c_ in full:
        c_.setItemStackForSlot(JShort(0), IS("Rock_Stone", JInt(1)))
    INVS[str(u2)] = full
    Cred.creditOne(None, u2, k2, wheat, JLong(need6), True)
    d2 = Store.dataK(k2)
    o_full = (int(Store.meta(d2, "_paiditem.Wheat")), count(full, "Skyy_Sigil_Unique"), bool(Rew.owedAny(d2, R)), bool(Rew.itemOwed(d2, R, cW, 6)))
    full[1].removeItemStackFromSlot(JShort(0))
    Rew.settleAll(None, u2, k2)
    o_room = (int(Store.meta(d2, "_paiditem.Wheat")), count(full, "Skyy_Sigil_Unique"), str(full[1].getItemStack(JShort(0)).getItemId()), bool(Rew.itemOwed(d2, R, cW, 6)))
    K.check(o_full == (0, 0, True, True) and o_room == (6, 1, "Skyy_Sigil_Unique", False),
            "X4: a FULL inventory: nothing given, no marker, owed (the 30 s retry); a slot freed (the backpack) -> the retry pays it there: %s -> %s" % (o_full, o_room))
    u3 = UUID.fromString("00000000-0000-0000-0000-00000000c003")
    k3 = str(Util.pkey(u3))
    Cred.creditOne(None, u3, k3, wheat, JLong(need6), True)
    d3 = Store.dataK(k3)
    o_off = int(Store.meta(d3, "_paiditem.Wheat"))
    INVS[str(u3)] = secs()
    LOADED["v"] = False
    Rew.settleAll(None, u3, k3)
    o_nl = (int(Store.meta(d3, "_paiditem.Wheat")), count(INVS[str(u3)], "Skyy_Sigil_Unique"))
    LOADED["v"] = True
    Rew.settleAll(None, u3, k3)
    o_ok = (int(Store.meta(d3, "_paiditem.Wheat")), count(INVS[str(u3)], "Skyy_Sigil_Unique"))
    K.check(o_off == 0 and o_nl == (0, 0) and o_ok == (6, 1), "X4: offline = owed; the item not loaded (no SkyyGear 0.3.4) = owed; then paid: %s %s %s" % (o_off, o_nl, o_ok))
    # ---- fixer F1: profile:busy holds the give (owed), cleared -> paid; F2: an epoch change holds it 31 s, then paid
    BR = Util.bridge()
    u4 = UUID.fromString("00000000-0000-0000-0000-00000000c004")
    k4 = str(Util.pkey(u4))
    INVS[str(u4)] = secs()
    BR.put("profile:busy:" + str(u4), JClass("java.lang.Boolean").TRUE)
    Cred.creditOne(None, u4, k4, wheat, JLong(need6), True)
    d4 = Store.dataK(k4)
    b_on = (int(Store.meta(d4, "_paiditem.Wheat")), count(INVS[str(u4)], "Skyy_Sigil_Unique"), bool(Rew.itemOwed(d4, R, cW, 6)))
    BR.remove("profile:busy:" + str(u4))
    Rew.settleAll(None, u4, k4)
    b_off = (int(Store.meta(d4, "_paiditem.Wheat")), count(INVS[str(u4)], "Skyy_Sigil_Unique"))
    K.check(b_on == (0, 0, True) and b_off == (6, 1), "FIX F1: profile:busy set -> the Sigil is NOT put into the live inventory (owed, no marker); busy gone -> the retry pays it: %s -> %s" % (b_on, b_off))
    Unl = P("CollUnlocks")
    u5 = UUID.fromString("00000000-0000-0000-0000-00000000c005")
    k5 = str(Util.pkey(u5))
    INVS[str(u5)] = secs()
    BR.put("profile:epoch:" + str(u5), JClass("java.lang.Long")(3))
    Unl.publish(u5)          # the join (publishOnline's first sight): nothing owed, no give ever ran
    a_join = list(Rew.EPSEEN.get(u5))
    hold_join = bool(Rew.profileHold(u5))
    ea = Rew.EPSEEN.get(u5)
    ea[1] = ea[1] - 32000          # joined 32 s ago
    hold_old = bool(Rew.profileHold(u5))
    BR.put("profile:epoch:" + str(u5), JClass("java.lang.Long")(4))          # the profile switch
    Unl.checkEpochs()          # the 1 s saver sees it (syncEpoch -> publish) BEFORE anything is owed
    a_sw = list(Rew.EPSEEN.get(u5))
    import time as _t
    sw_recent = a_sw[0] == 4 and 0 <= int(_t.time() * 1000) - a_sw[1] < 5000
    Cred.creditOne(None, u5, k5, wheat, JLong(need6), True)          # tier VI on the new profile seconds after the switch
    d5 = Store.dataK(k5)
    e_new = (int(Store.meta(d5, "_paiditem.Wheat")), count(INVS[str(u5)], "Skyy_Sigil_Unique"), bool(Rew.itemOwed(d5, R, cW, 6)))
    ea = Rew.EPSEEN.get(u5)
    ea[1] = ea[1] - 32000          # the switch 32 s ago
    Rew.settleAll(None, u5, k5)
    e_late = (int(Store.meta(d5, "_paiditem.Wheat")), count(INVS[str(u5)], "Skyy_Sigil_Unique"))
    BR.remove("profile:epoch:" + str(u5))
    K.check(a_join[0] == 3 and a_join[1] > 0 and hold_join and not hold_old and sw_recent and e_new == (0, 0, True) and e_late == (6, 1),
            "FIX F2 (fixer 2): publish stamps the epoch - the JOIN holds 31 s (a join-time crash recovery keeps its 30 s window), then not; a profile "
            "switch with NOTHING owed is stamped by the 1 s saver (checkEpochs -> publish), so tier VI seconds later is held (owed, no marker); 32 s "
            "later the retry pays: %s %s %s %s %s %s" % (a_join, hold_join, hold_old, a_sw, e_new, e_late))
    # no SkyyProfiles (epoch -1): never holds, even at first sight; TOLD stamps older than 5 minutes are pruned
    u7 = UUID.fromString("00000000-0000-0000-0000-00000000c007")
    h7 = (bool(Rew.profileHold(u7)), list(Rew.EPSEEN.get(u7)))
    Rew.TOLD.put("old|x", JClass("java.lang.Long")(int(_t.time() * 1000) - 400000))
    Rew.TOLD.put("new|x", JClass("java.lang.Long")(int(_t.time() * 1000)))
    Rew.pruneTold(int(_t.time() * 1000))
    K.check(not h7[0] and h7[1] == [-1, 0] and not Rew.TOLD.containsKey("old|x") and Rew.TOLD.containsKey("new|x"),
            "FIX2 F5: no SkyyProfiles (epoch -1) never holds; 'waiting' line stamps older than 5 minutes are pruned (the 60 s saver): %s" % (h7,))
    # ---- fixer F3: the marker save FAILS (the counts file path is a non-empty folder) -> marker back, nothing given, the key stays DIRTY
    u6 = UUID.fromString("00000000-0000-0000-0000-00000000c006")
    k6 = str(Util.pkey(u6))
    INVS[str(u6)] = secs()
    Cred.creditOne(None, u6, k6, wheat, JLong(need6 - 1), True)
    Store.flushDirty()
    blk = os.path.join(base, "counts", k6 + ".properties")
    if os.path.isfile(blk):
        os.remove(blk)
    os.makedirs(os.path.join(blk, "x"), exist_ok=True)
    Cred.creditOne(None, u6, k6, wheat, JLong(1), True)
    d6 = Store.dataK(k6)
    f_fail = (int(Store.meta(d6, "_paiditem.Wheat")), count(INVS[str(u6)], "Skyy_Sigil_Unique"), bool(Store.DIRTY.containsKey(k6)))
    import shutil
    shutil.rmtree(blk)
    Store.flushDirty()
    f_saved = (os.path.isfile(blk), bool(Store.DIRTY.containsKey(k6)), "Wheat" in counts_file(k6) or str(wheat) in counts_file(k6))
    Rew.settleAll(None, u6, k6)
    f_paid = (int(Store.meta(d6, "_paiditem.Wheat")), count(INVS[str(u6)], "Skyy_Sigil_Unique"))
    K.check(f_fail == (0, 0, True) and f_saved[0] and not f_saved[1] and f_paid == (6, 1),
            "FIX F4: a failed marker save -> marker back, no Sigil, the counts key stays DIRTY; the next flush writes it; the retry then pays: %s %s %s" % (f_fail, f_saved, f_paid))
    Rew.SECS = None
    Rew.ITEMOK = None
    # ---- CollSigMig.update on the LIVE rewards.properties text (read only) + variants
    live_f = os.path.join(LIVE_DIR, "rewards.properties")
    live = open(live_f, "rb").read().decode("latin-1") if os.path.isfile(live_f) else str(Reg.rewardsText()).replace("," + TOK, "").replace("Bone.6=" + TOK + "\n", "").replace(str(Sig.MARK3) + "\n", "")
    K.notes.append("X5: live rewards.properties %s" % ("found (%d bytes)" % len(live) if os.path.isfile(live_f) else "missing - the 0.2.12 default used"))

    def upd(t_):
        r_ = Sig.update(t_)
        return None if r_ is None else (str(r_[0]), [str(x) for x in r_[1]], str(r_[2]), int(r_[3]), int(r_[4]), bool(r_[5]))

    def table(t_):
        return dict((str(k), [str(x) for x in v]) for k, v in Cob.table(JArray(JString)([l_.rstrip("\r") for l_ in t_.split("\n")])).items())
    u_ = upd(live)
    t_old, t_new = table(live), table(u_[0]) if u_ else {}
    want = dict(t_old)
    for k_ in ("wheat.6", "oaklog.6", "cobblestone.6", "bone.6"):
        want[k_] = list(want.get(k_, [])) + [TOK]
    nl_ = u_[0].split("\n") if u_ else []
    K.check(u_ is not None and u_[5] and u_[3] == 4 and u_[4] == 0 and t_new == want and str(Sig.MARK3) in nl_ and len(u_[1]) == 12
            and upd(u_[0]) is None and ("Bone.6=" + TOK) in [l_.rstrip("\r") for l_ in nl_],
            "X5: the LIVE file: 4 entries updated (Wheat / OakLog / Cobblestone appended, Bone.6 added in a new section), the loader reads exactly the old "
            "table + the tokens, 4 Undo rows, the marker; run again = nothing: %s" % (u_[2] if u_ else None))
    crlf = live.replace("\r\n", "\n").replace("\n", "\r\n")
    uc = upd(crlf)
    K.check(uc is not None and uc[5] and uc[0].count("\r\n") == uc[0].count("\n") and uc[3] == 4, "X5: CRLF kept on every line (old and new)")
    # fixer 2: a Notepad file without a final newline (CRLF and LF): one ending style, no lone CR / LF, still no final newline
    noeol = crlf.rstrip("\r\n")
    un_ = upd(noeol)
    lf_noeol = live.replace("\r\n", "\n").rstrip("\n")
    ul_ = upd(lf_noeol)
    onlyc = "# just a comment\r\n# and another"
    uo_ = upd(onlyc)
    K.check(un_ is not None and un_[5] and un_[3] == 4 and "\r" not in un_[0].replace("\r\n", "") and "\n" not in un_[0].replace("\r\n", "")
            and not un_[0].endswith("\n") and all(l_ in un_[0].split("\r\n") for l_ in noeol.split("\r\n") if not l_.startswith(("Wheat.6=", "OakLog.6=", "Cobblestone.6=")))
            and ul_ is not None and ul_[5] and "\r" not in ul_[0] and not ul_[0].endswith("\n")
            and uo_ is not None and "\r" not in uo_[0].replace("\r\n", "") and "\n" not in uo_[0].replace("\r\n", "") and str(Sig.MARK3) in uo_[0],
            "FIX2 X6: a file WITHOUT a final newline (CRLF / LF / comments only): every line keeps the file's one ending (no lone CR or LF), the "
            "new last line has none, as the old file: %s" % [repr(x_[0][-40:]) for x_ in (un_, ul_, uo_) if x_])
    hand = live.replace("Wheat.6=recipe:Tool_Sickle_Iron_Recipe_Generated_0", "Wheat.6=recipe:Tool_Sickle_Iron_Recipe_Generated_0,coins:5")
    uh = upd(hand)
    rem = "\n".join(l_ for l_ in live.split("\n") if not l_.startswith("OakLog.6="))
    ur = upd(rem)
    has = live.replace("Cobblestone.6=recipe:Tool_Pickaxe_Iron_Recipe_Generated_0", "Cobblestone.6=recipe:Tool_Pickaxe_Iron_Recipe_Generated_0,item:Skyy_Sigil_Rare:1")
    ua = upd(has)
    two_ = live.replace("Wheat.6=recipe:Tool_Sickle_Iron_Recipe_Generated_0", "Wheat.6=recipe:Tool_Sickle_Iron_Recipe_Generated_0\nWheat.6=coins:10")
    u2_ = upd(two_)
    ue = upd("")
    K.check(uh[5] and uh[3] == 3 and uh[4] == 1 and "kept hand-edited line" in uh[2] and table(uh[0]).get("wheat.6") == ["recipe:Tool_Sickle_Iron_Recipe_Generated_0", "coins:5"]
            and ur[5] and ur[3] == 3 and ur[4] == 1 and "an admin removed it" in ur[2] and "oaklog.6" not in table(ur[0])
            and ua[5] and ua[3] == 3 and "already has an item reward" in ua[2] and table(ua[0]).get("cobblestone.6") == ["recipe:Tool_Pickaxe_Iron_Recipe_Generated_0", "item:Skyy_Sigil_Rare:1"]
            and u2_[5] and u2_[3] == 3 and u2_[4] == 2 and ue[5] and ue[3] == 1 and ue[4] == 3 and str(Sig.MARK3) in ue[0],
            "X5: a hand-edited line is KEPT (logged), a removed default line is not re-added, a line that already has an item is left, two lines for one "
            "key are kept, an empty file gets only Bone.6 + the marker: %s | %s | %s" % (uh[2].strip()[:120], ur[2].strip()[:120], ua[2].strip()[:120]))
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Sig = P("CollReg"), P("CollStore"), P("CollSigMig")
    Paths = JClass("java.nio.file.Paths")
    b_ = Paths.get(home)
    rf = os.path.join(home, "rewards.properties")
    old = open(rf, "rb").read()

    def hist():
        d_ = os.path.join(home, "config-history")
        out_ = []
        for r_, _d, fs_ in os.walk(d_):
            for f_ in fs_:
                out_.append(open(os.path.join(r_, f_), "rb").read())
        return out_
    h0 = hist()
    msgs = []
    snaps = []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        Reg.loadAll()
        P("CollCobMig").run(b_)
        msgs.append(str(Sig.run(b_)))
        snaps.append(HK.tree_hash(home))
    new = open(rf, "rb").read()
    h1 = hist()
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else ""
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.13" in l_]
    R = Reg.D
    cW = int(R.byId.get("wheat"))
    K.check(msgs[0].startswith("Unique Sigils are collection rewards now") and msgs[1] == "" and snaps[0] == snaps[1],
            "D: the 1st start updates rewards.properties once, the 2nd start changes nothing: %s" % msgs)
    K.check(new != old and any(h_ == old for h_ in h1) and len(h1) >= len(h0) and len(rows) >= 1 and os.path.isfile(os.path.join(home, "migration-sigils.log"))
            and Reg.itemAt(R, cW, 6) is not None and str(Reg.itemAt(R, cW, 6)[0]) == "Skyy_Sigil_Unique",
            "D: the old file is kept in config-history (byte for byte), %d Undo row(s) in config-changes.log, migration-sigils.log, the loaded table "
            "has the Unique Sigil at Wheat VI" % len(rows))
    K.notes.append("D: %s" % msgs[0])
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
