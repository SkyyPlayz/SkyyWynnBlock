"""Harness for SkyySacks 0.8.18 (round FP1: the Potion Flask / Food Pouch go first - supply:fn:claims - and their two lifelong ids never
enter the Void; tools/sacks_0_8_18_patch.py). Build first:
    python tools/sacks_0_8_18_patch.py && python SkyySacks/build_skyysacks_0.8.18.py

    python SkyySacks/test_skyysacks_0.8.18.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.17 -> 0.8.18: exactly the planned members; non-class entries: manifest.json only
  SUP  EXECUTED on the 0.8.0 harness's Void stand-ins (real SimpleItemContainers, a stand-in Item store, a scratch pool folder) with a
       stand-in supply:fn:claims (counts its calls):
       HOME   Skyy_Flask_* / Skyy_Food_Pouch_* -> supplyItem, homeOf / catOf / intake null (even with cooked food ON), voidRoom 0, the
              sweep (Deposit all, every container) leaves them, sacks:fn:deposit refuses them; look-alike ids unaffected
       ASK    no key / FALSE / null / a non-Boolean = not claimed; a throwing Function = not claimed + warned ONCE; another player's claim
              never touches this player
       SWEEP  claimed cooked food stays in the inventory (Deposit all + the 2 s sweep form), unclaimed items go in, ONE ask per distinct
              id per pass (two stacks = one call), SUPSEEN + sigOf's 10 s bucket while claimed items are held, cleared once not claimed;
              claims FALSE again = the Void takes them; conserved every time
       SPLIT  auto-pickup (PickGive.split 5-arg): claimed -> the storage first (Void 0); a full storage -> the Void as before; the Void
              too small -> the rest into the pickup container, then the feet; unclaimed = Void first (0.8.17); the 4-arg form = no
              storage (claimed -> the pickup container first); harness faults 1 / 2 roll every part back (storage, Void, container)
       HARV   PickHarv.move leaves a claimed harvest in the inventory, moves an unclaimed one
       DEP    sacks:fn:deposit (Requip) refuses a claimed id (0, the slot untouched), takes an unclaimed one
  TG   the 0.8.16 harness's TG phase on this jar (seeds / saplings switches, popup, feed) - unchanged behaviour
  KEYS the 0.8.17 harness's KEYS phase on this jar (the fish keys) - unchanged behaviour
  D    START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the real SkyyCooking 0.1.11 supply:fn:claims answers, the real drop entities (deliver's
storage lookup through the real Store), the Flask / Pouch auto-fill taking what we leave behind. Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_17", os.path.join(HERE, "test_skyysacks_0.8.17.py"))
T17 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T17)
sys.argv = _argv
HK.run_compare = _orig_compare
T16, T0810 = T17.T16, T17.T0810
T089 = T16.T089

VERSION = "0.8.18"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.17.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fp1", "sackswd", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the version text
    "SackDefs": ["+m supplyItem", "~m homeOf"],
    "SackPool": ["+f CLAIMWARN", "+m claimed", "~<clinit>"],
    "SweepTask": ["+f SUPSEEN", "~<clinit>", "~m sweep", "~m sigOf"],
    "PickGive": ["+m split", "~m split", "~m deliver"],   # + the 5-argument split; the 4-argument one now delegates
    "PickHarv": ["~m move"],
    "SackBridge": ["~m deposit"],
    "SkyySacksPlugin": ["~m setup"],   # the ready line's version
}
ADDED = []


def run_sup(out, jar, scratch, home):
    """the 0.8.16 run_tg pattern (the 0.8.0 stand-in slice), with this round's cases"""
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    src = open(T089.T080, encoding="utf8").read()
    a = src.index("    # ---------------- stand-ins (the 0.7.12+ harness pattern)\n")
    b = src.index("    # ---------------- D. categories\n", a)
    head = ("def run_void_fixture():\n    import jpype\n    import skyybuild as B\n"
            "    from jpype import JClass, JArray, JShort, JString, JInt, JLong, JImplements, JOverride\n"
            "    jp = JClass(\"javassist.ClassPool\")(True)\n    jp.appendClassPath(B.SERVER_JAR)\n    jp.appendClassPath(JAR)\n")
    body = head + src[a:b] + "    _VOID(locals())\n"
    ns = {"__file__": T089.T080, "__name__": "t080"}
    exec(compile(src[:src.index("def run():")], T089.T080, "exec"), ns)
    ns.update(JAR=jar, SCRATCH=os.path.join(scratch, "sup"), _VOID=lambda L: sup_cases(K, L, scratch))
    exec(compile(body, T089.T080 + " (stand-in slice)", "exec"), ns)
    try:
        ns["run_void_fixture"]()
    finally:
        for f in ns["FAILS"]:
            K.check(False, "SUP fixture: " + f)
        K.save()
        try:
            __import__("jpype").JClass(PKG + "SackPool").WRITER.shutdownNow()
        except Exception:
            pass


def sup_cases(K, L, scratch):
    from jpype import JClass, JString, JImplements, JOverride, JLong, JShort, JInt
    Defs, Pool = L["Defs"], L["Pool"]
    fresh, player, inv_counts, custom_item, drain, pc = (L[n] for n in ("fresh", "player", "inv_counts", "custom_item", "drain", "pc"))
    UUID, jfield, pref, bridge, TPlayers = (L[n] for n in ("UUID", "jfield", "pref", "bridge", "TPlayers"))
    J = lambda n: JClass(PKG + n)
    Swp, PG, PH, Br = J("SweepTask"), J("PickGive"), J("PickHarv"), J("SackBridge")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    pr_field = jfield(PLA.class_, "playerRef")
    U1, U2 = UUID.fromString("00000000-0000-0000-0000-00000000f101"), UUID.fromString("00000000-0000-0000-0000-00000000f102")
    k1 = str(U1)
    CK, CK2, WHEAT, ORE = "Food_Bread", "Food_Fish_Grilled", "Plant_Crop_Wheat_Item", "Ore_Copper"
    FL = ["Skyy_Flask_Empty", "Skyy_Flask_V_Potion_Health", "Skyy_Food_Pouch_Empty", "Skyy_Food_Pouch_V_Food_Bread"]
    for i_ in [CK, CK2, WHEAT, ORE]:
        custom_item(i_, 100)
    for i_ in FL:
        custom_item(i_, 1)
    Defs.COOKED_FARM = True   # cooked food may enter the Void (bags.cookedFood ON) - the case where the order matters

    CLAIM = {}      # (uuid, id) -> answer object
    CALLS = []

    @JImplements("java.util.function.Function")
    class Claims(object):
        @JOverride
        def apply(self, o):
            CALLS.append((str(o[0]), str(o[1])))
            v = CLAIM.get((str(o[0]), str(o[1])))
            if v == "boom":
                raise RuntimeError("stand-in claims failure")
            if v is None:
                return None
            if isinstance(v, bool):
                return JClass("java.lang.Boolean").valueOf(v)
            return JString(v)

    def mkp(u_, storage=(), hotbar=(), cap=36):
        p_ = player(storage=storage, hotbar=hotbar, cap=cap)
        pr_field.set(p_, pref(u_))
        return p_

    def claimed(u_, iid, memo=None):
        return bool(Pool.claimed(u_, JString(iid), memo))

    # ============================================================== HOME (the two lifelong items never pool)
    K.check(all(bool(Defs.supplyItem(JString(i_))) for i_ in FL) and not any(bool(Defs.supplyItem(JString(i_))) for i_ in ("Skyy_FlaskX", "Skyy_Food_Pouch", "Skyy_Cook_Stew_G3", CK)),
            "HOME: supplyItem = exactly the Skyy_Flask_ / Skyy_Food_Pouch_ prefixes")
    K.check(all(Defs.homeOf(JString(i_)) is None and Defs.catOf(JString(i_)) is None and Defs.intake(U1, JString(i_)) is None for i_ in FL),
            "HOME: homeOf / catOf / intake = null for the Flask / Pouch ids (cooked food ON)")
    bridge.put("cook:prefix", JString("Skyy_Cook"))
    K.check(str(Defs.homeOf(JString(CK))) == "Farming" and str(Defs.catOf(JString(CK))) == "Farming", "HOME: cooked food still Farming (cooked food ON)")
    fresh(os.path.join(scratch, "sup", "home"))
    K.check(all(int(PG.voidRoom(U1, JString(k1), IS(i_, 1))) == 0 for i_ in FL), "HOME: auto-pickup voidRoom = 0 for the Flask / Pouch")
    p_ = mkp(U1, storage=[(i_, 1) for i_ in FL] + [(ORE, 10)], hotbar=[(FL[1], 1)])
    before = inv_counts(p_)
    int(Swp.sweep(p_, JString(k1), None, True))
    drain()
    K.check(all(inv_counts(p_).get(i_, 0) == before[i_] for i_ in FL) and not any(i_ in pc(k1) for i_ in FL) and pc(k1).get(ORE, 0) == 10,
            "HOME: Deposit all (every container) leaves the Flask / Pouch, stores the ore (%s)" % pc(k1))

    # ============================================================== ASK (one call, every failure = not claimed)
    bridge.remove("supply:fn:claims")
    K.check(not claimed(U1, CK), "ASK: no supply:fn:claims (SkyyCooking older / missing) = not claimed")
    bridge.put("supply:fn:claims", Claims())
    CLAIM[(k1, CK)] = True
    CLAIM[(k1, WHEAT)] = False
    CLAIM[(k1, ORE)] = "yes"
    K.eq([claimed(U1, CK), claimed(U1, WHEAT), claimed(U1, ORE), claimed(U1, CK2), claimed(U2, CK), claimed(None, CK)],
         [True, False, False, False, False, False], "ASK: TRUE = claimed; FALSE / a String / null (unknown id) / another player / no player = not")
    CLAIM[(k1, CK2)] = "boom"
    Pool.CLAIMWARN = False
    r1, r2 = claimed(U1, CK2), claimed(U1, CK2)
    K.check(not r1 and not r2 and bool(Pool.CLAIMWARN), "ASK: a throwing claims = not claimed (both calls), warned once (CLAIMWARN set)")
    del CLAIM[(k1, CK2)]
    memo = JClass("java.util.HashMap")()
    del CALLS[:]
    claimed(U1, CK, memo), claimed(U1, CK, memo), claimed(U1, WHEAT, memo), claimed(U1, WHEAT, memo)
    K.eq(len(CALLS), 2, "ASK: with the pass memo each distinct id is asked once (%s)" % CALLS)

    # ============================================================== SWEEP (2 s sweep + Deposit all)
    def sweep_case(tag, all_c):
        fresh(os.path.join(scratch, "sup", "sw-" + tag))
        p_ = mkp(U1, storage=[(CK, 5), (CK, 3), (WHEAT, 20), (CK2, 4)])
        b0 = inv_counts(p_)
        del CALLS[:]
        moved = int(Swp.sweep(p_, JString(k1), None, all_c))
        drain()
        a0, pool = inv_counts(p_), pc(k1)
        cons = all(a0.get(i_, 0) + pool.get(i_, 0) == b0[i_] for i_ in b0)
        return a0, pool, moved, cons, list(CALLS)
    CLAIM[(k1, CK2)] = False
    for tag, all_c in (("dep", True), ("auto", False)):
        a0, pool, moved, cons, calls = sweep_case(tag, all_c)
        K.check(a0.get(CK, 0) == 8 and pool.get(CK, 0) == 0 and pool.get(WHEAT, 0) == 20 and pool.get(CK2, 0) == 4 and cons,
                "SWEEP (%s): the claimed bread stays in the inventory (8), wheat + unclaimed grilled fish go into the Void, conserved (inv %s pool %s)" % (tag, a0, pool))
        K.eq(calls.count((k1, CK)), 1, "SWEEP (%s): two bread stacks = ONE claims call in the pass (%s)" % (tag, calls))
        K.check(Swp.SUPSEEN.containsKey(k1), "SWEEP (%s): SUPSEEN marks the player (claimed items held)" % tag)
    sig1 = str(Swp.sigOf(U1))
    K.check(("|%d|" % (int(JClass("java.lang.System").currentTimeMillis()) // 10000)) in sig1 or ("|%d|" % (int(JClass("java.lang.System").currentTimeMillis()) // 10000 - 1)) in sig1,
            "SWEEP: sigOf carries the 10 s bucket while claimed items are held (re-sweep) [%s]" % sig1[:80])
    CLAIM[(k1, CK)] = False
    a0, pool, moved, cons, calls = sweep_case("unclaimed", False)
    K.check(a0.get(CK, 0) == 0 and pool.get(CK, 0) == 8 and cons and not Swp.SUPSEEN.containsKey(k1),
            "SWEEP: claims FALSE (Pouch full / auto-fill off) = the bread goes into the Void as in 0.8.17, SUPSEEN cleared (pool %s)" % pool)
    K.check("|0|" in str(Swp.sigOf(U1)), "SWEEP: sigOf's bucket is 0 again once nothing claimed is held")
    bridge.remove("supply:fn:claims")
    a0, pool, moved, cons, calls = sweep_case("nokey", False)
    K.check(pool.get(CK, 0) == 8 and cons, "SWEEP: no claims key = 0.8.17 behaviour (bread into the Void)")
    bridge.put("supply:fn:claims", Claims())
    CLAIM[(k1, CK)] = True

    # ============================================================== SPLIT (auto-pickup straight to the Void)
    def split_case(tag, q, stor_items=(), stor_cap=36, inv_items=(), inv_cap=9, five=True, fault=0, prefill=None):
        fresh(os.path.join(scratch, "sup", "sp-" + tag))
        if prefill:
            for i_, n_ in prefill.items():
                Pool.add(JString(k1), JString(i_), JLong(n_))
        stor, inv = SIC(JShort(stor_cap)), SIC(JShort(inv_cap))
        for cont, its in ((stor, stor_items), (inv, inv_items)):
            for (iid, n_) in its:
                assert cont.addItemStack(IS(iid, n_)).succeeded()
        cnt = lambda c, i_: int(PG.countId(c, JString(i_)))
        b = (cnt(stor, CK), cnt(inv, CK), int(Pool.get(JString(k1), JString(CK))))
        PG.FAULT = fault
        try:
            r = PG.split(U1, JString(k1), IS(CK, q), inv, stor) if five else PG.split(U1, JString(k1), IS(CK, q), inv)
        finally:
            PG.FAULT = 0
        a = (cnt(stor, CK), cnt(inv, CK), int(Pool.get(JString(k1), JString(CK))))
        return (None if r is None else [int(x) for x in r]), b, a

    r, b, a = split_case("claimed", 10)
    K.check(r == [0, 10, 0] and a == (10, 0, 0), "SPLIT: claimed bread -> the storage first, nothing into the Void (%s %s)" % (r, a))
    r, b, a = split_case("storfull", 10, stor_items=[(ORE, 100)], stor_cap=1)
    K.check(r == [10, 0, 0] and a == (0, 0, 10), "SPLIT: claimed but the storage is full -> the Void as before (%s %s)" % (r, a))
    r, b, a = split_case("part", 30, stor_items=[(ORE, 100), (CK, 90)], stor_cap=2)
    K.check(r == [20, 10, 0] and a == (100, 0, 20), "SPLIT: claimed, the storage takes 10 of 30 -> the rest into the Void, every item counted (%s %s)" % (r, a))
    cap0 = int(J("VoidStore").capsK(U1, JString(k1)).get(JString("Farming")))
    r, b, a = split_case("voidsmall", 30, stor_items=[(ORE, 100)], stor_cap=1, prefill={WHEAT: cap0 - 5})
    K.check(r == [5, 25, 0] and a == (0, 25, 5), "SPLIT: claimed, the storage full, the Void has room for 5 -> 5 in, 25 into the pickup container (%s %s)" % (r, a))
    r, b, a = split_case("feet", 30, stor_items=[(ORE, 100)], stor_cap=1, inv_items=[(ORE, 100)], inv_cap=1, prefill={WHEAT: cap0 - 5})
    K.check(r == [5, 0, 25], "SPLIT: storage + container full, the Void 5 -> 25 left for the feet (%s)" % (r,))
    CLAIM[(k1, CK)] = False
    r, b, a = split_case("unclaimed", 10)
    K.check(r == [10, 0, 0] and a == (0, 0, 10), "SPLIT: unclaimed = the Void first (0.8.17) (%s %s)" % (r, a))
    CLAIM[(k1, CK)] = True
    r, b, a = split_case("four", 10, five=False)
    K.check(r == [0, 10, 0] and a == (0, 10, 0), "SPLIT: the 4-argument form (no storage) -> claimed goes into the pickup container (%s %s)" % (r, a))
    for f_ in (1, 2):
        r, b, a = split_case("fault%d" % f_, 30, stor_items=[(ORE, 100), (CK, 90)], stor_cap=2, prefill={WHEAT: cap0 - 5}, fault=f_)
        K.check(r is None and a == b, "SPLIT: harness fault %d -> everything rolled back (storage, Void, container) %s == %s" % (f_, a, b))
    # review fixes (FP1 critic): a stack with metadata is never claimed (the Flask / Pouch take plain stacks only); no container at all = the Void
    fresh(os.path.join(scratch, "sup", "sp-meta"))
    stor_m, inv_m = SIC(JShort(36)), SIC(JShort(9))
    del CALLS[:]
    r = PG.split(U1, JString(k1), IS(CK, 10).withMetadata(JString("SkyyRolls"), JClass("org.bson.BsonString")("x")), inv_m, stor_m)
    K.check(int(PG.countId(stor_m, JString(CK))) == 0 and not CALLS, "SPLIT (review 4): a claimed id WITH metadata is not asked / not put into the storage first (%s, calls %s)" % (None if r is None else [int(x) for x in r], CALLS))
    fresh(os.path.join(scratch, "sup", "sp-none"))
    r = PG.split(U1, JString(k1), IS(CK, 10), None, None)
    K.check(r is not None and [int(x) for x in r] == [10, 0, 0], "SPLIT (review LOW 7): claimed but no storage and no container -> the Void takes it (%s)" % (None if r is None else [int(x) for x in r]))
    fresh(os.path.join(scratch, "sup", "sw-hot"))
    p_ = mkp(U1, hotbar=[(CK, 5)])
    del CALLS[:]
    int(Swp.sweep(p_, JString(k1), None, True))
    drain()
    K.check(pc(k1).get(CK, 0) == 5 and inv_counts(p_).get(CK, 0) == 0 and (k1, CK) not in CALLS,
            "SWEEP (review 3): claimed bread in the HOTBAR is not asked - Deposit all puts it into the Void (the Pouch never fills from the hotbar) (pool %s, calls %s)" % (pc(k1), CALLS))

    # ============================================================== HARV (PickHarv.move)
    fresh(os.path.join(scratch, "sup", "harv"))
    cont = SIC(JShort(9))
    cont.addItemStack(IS(CK, 6))
    cont.addItemStack(IS(WHEAT, 6))
    m1 = int(PH.move(U1, JString(k1), IS(CK, 6), cont, JLong(6)))
    m2 = int(PH.move(U1, JString(k1), IS(WHEAT, 6), cont, JLong(6)))
    K.check(m1 == 0 and int(PG.countId(cont, JString(CK))) == 6 and m2 == 6 and int(PG.countId(cont, JString(WHEAT))) == 0 and pc(k1).get(WHEAT, 0) == 6,
            "HARV: a claimed harvest stays in the inventory, an unclaimed one goes into the Void (%d %d)" % (m1, m2))

    # ============================================================== DEP (sacks:fn:deposit, Requip)
    fresh(os.path.join(scratch, "sup", "dep"))
    p_ = mkp(U1, hotbar=[(CK, 7), (WHEAT, 9), (FL[2], 1)])
    Br.PLAYERS = TPlayers()
    TPlayers.P = p_
    hb = p_.getInventory().getHotbar()
    slot = lambda iid: [s_ for s_ in range(9) if hb.getItemStack(JShort(s_)) is not None and str(hb.getItemStack(JShort(s_)).getItemId()) == iid][0]
    d1 = int(Br.deposit(U1, JString(CK), JLong(7), JInt(slot(CK))))
    d2 = int(Br.deposit(U1, JString(WHEAT), JLong(9), JInt(slot(WHEAT))))
    d3 = int(Br.deposit(U1, JString(FL[2]), JLong(1), JInt(slot(FL[2]))))
    drain()
    ic = inv_counts(p_)
    K.check(d1 == 0 and ic.get(CK, 0) == 7 and d2 == 9 and ic.get(WHEAT, 0) == 0 and pc(k1).get(WHEAT, 0) == 9 and d3 == 0 and ic.get(FL[2], 0) == 1,
            "DEP: sacks:fn:deposit refuses claimed bread + the Food Pouch (they stay in the slot), takes the wheat (%d %d %d %s)" % (d1, d2, d3, ic))
    Br.PLAYERS = None
    bridge.remove("supply:fn:claims")
    bridge.remove("cook:prefix")
    Defs.COOKED_FARM = False
    Swp.SUPSEEN.clear()
    drain()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("sup", run_sup), ("tg", T16.run_tg), ("keys", T17.run_keys), ("live", T0810.run_live10)],
           __file__, live=(T16.T15.BETA, "Skyy_SkyySacks"))
