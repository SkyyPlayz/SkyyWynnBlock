"""Derive SkyyGear/build_skyygear_0.2.10.py from the LIVE 0.2.9 (build_skyygear_0.2.9.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_9_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_10_patch.py      then      python SkyyGear/build_skyygear_0.2.10.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.10.py (the 0.2.9 harness on the new jar + section AK).

0.2.10 = THE SIGNATURE CHARGE IS KEPT PER WEAPON ON A SWAP (Skyy LOCKED docs/answered/gear.md 2026-10-08: "1 tweak , make it stay when you
change weapon and change back instead of resetting."). Vanilla signatures (Ability 1: daggers Razorstrike, crossbow BigArrow, ...) charge the
player stat SignatureEnergy (Assets.zip Server/Entity/Stats/SignatureEnergy.json Min 0 / Max 0 / Shared: the held weapon's Weapon.StatModifiers
set its max) and, for the bows, SignatureCharges (the loaded big shot).
  - WHY IT RESETS (HytaleServer.jar bytecode, checked by this build): Hotbar.setActiveSlot sets the new slot FIRST, then dispatches
    InventorySetActiveSlotEvent synchronously (CommandBuffer.invoke -> Store.internal_invoke). The engine's
    InventorySystems$ActiveSlotChangedEntityEventSystem then queues the NEW item's Weapon.EntityStatsToClear (every vanilla weapon template:
    "SignatureEnergy", bows + crossbows also "SignatureCharges", "Ammo") into StatModifiersManager.queueEntityStatsToClear and
    scheduleRecalculate(); the next EntityStatsSystems$Recalculate tick (StatModifiersManager.recalculateEntityStatModifiers) runs
    EntityStatMap.minimizeStatValue on each queued stat (= 0) and re-applies the held item's stat modifiers (the new max; a non-weapon gives
    max 0, which clamps the value to 0). So the meter is still intact while the event is dispatched, and settled after the next recalc.
  - WORKING WITH IT: GearSigSlotSys (an EntityEventSystem on the same event) reads the meter of the weapon being LEFT before anything is
    cleared and keeps it (memory only) keyed by player + hotbar slot, with the item id + durability. GearSigTick (only does work for a
    player with a pending swap) first calls the engine's own public recalculateEntityStatModifiers (a no-op when Recalculate already ran -
    it returns at once when its flag is clear), so the engine's clear + the new max are applied exactly as vanilla does them, and then
    puts back the kept value of the slot now held (clamped to the new max; never below what the meter already shows). No per-tick fighting:
    one restore per swap, and nothing touches the meter while a weapon is held.
  - NO DUPE: a kept value is exactly the meter at the moment that weapon was left; a restore consumes it. Several swaps inside one tick
    (the meter not yet settled) keep nothing new. If the engine CARRIES the meter to the next item (a pack weapon with a signature max but
    no EntityStatsToClear), what was carried is taken off the kept value. A kept slot whose item leaves (drop, trade, move, another item put
    there: InventoryChangeEvent on the hotbar, GearSigInvSys) loses its kept charge; the restore also needs the same item id + durability
    in that slot. Cleared on logout, death (DeathComponent), world switch / join (PlayerReadyEvent), profile switch (profile:epoch moved,
    profile:busy - tools/PROFILES-CONTRACT.md) and when the row is switched off.
  - Every weapon whose item stat modifiers include SignatureEnergy (vanilla and pack-mod weapons alike - it is the player's stat).
  - Server Setup -> Gear -> Combat: gear.signatureKeep (switch, live, default ON; off = the vanilla reset). New key, no one-time update
    (a missing line means its default - the 0.1.2 rule); the fresh file lists it under its own heading.
  - REVIEW FIXES (2026-10-08): (1) SkyySkills' Archer perk "Crossbows stay loaded" already keeps the crossbow's bolts + big-arrow meter
    (Xbow.onSlot / keepOneMeter: ONE banked meter, LOCKED docs/answered/classes.md) - while SkyySkills is loaded, a weapon whose id starts
    with one of its perk.archery.keepLoaded.items prefixes (read through config:fn:SkyySkills "get", 5 s cache; default Weapon_Crossbow_)
    is left to SkyySkills: Gear neither keeps nor restores it (leave code 5). Without SkyySkills Gear keeps crossbows too. (2) GearSigTick is
    registered ordered AFTER EntityStatsSystems$Recalculate (so the engine's pass - and GearLockSys, ordered before it - always runs first;
    the in-tick recalc stays as a safety net), GearSigTickU = the unordered fallback. (3) a slot event that lands after the logout clean-up
    could leave a kept entry behind: GearSigBye also sweeps entries of players no longer in Universe.getPlayers() on every logout / ready.
No asset, no saved data, no migration, no command. 6 classes added (GearSig + 3 systems + the unordered tick fallback + the GearSigBye
listener). Rolling back to 0.2.9 is safe (the vanilla reset again).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.9.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.10.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.9"' in s and s.startswith('"""SkyyGear 0.2.9 - build script'), "build_skyygear_0.2.9.py is not the live 0.2.9"
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.9 - build script (javassist via jpype). GENERATED by tools/gear_0_2_9_patch.py from the LIVE 0.2.8 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.9.py -> SkyyGear/SkyyGear-0.2.9.jar (never --deploy).

0.2.9 = ''', '''"""SkyyGear 0.2.10 - build script (javassist via jpype). GENERATED by tools/gear_0_2_10_patch.py from the LIVE 0.2.9 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.10.py -> SkyyGear/SkyyGear-0.2.10.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.10 = "):].strip() + '''

0.2.9 (the base, everything below is still true unless 0.2.10 above says otherwise):
0.2.9 = ''')
rep('VERSION = "0.2.9"', 'VERSION = "0.2.10"')

# ================================================================================================================ Server Setup row
rep('''     "Weights Slow,Medium,Fast,Super Fast of a weapon's tier." + PH, "field:GearCfg.SWING_ODDS;check=GearCfg.checkSwingOdds"),
''', '''     "Weights Slow,Medium,Fast,Super Fast of a weapon's tier." + PH, "field:GearCfg.SWING_ODDS;check=GearCfg.checkSwingOdds"),
    # 0.2.10 SIGNATURE CHARGE KEPT ON SWAP (Skyy LOCKED 2026-10-08). New key: a missing line means its default (no one-time update)
    ("gear.signatureKeep", "Keep signature charge on weapon swap", "combat", "bool", "true", "", "", "", "", "live",
     "A weapon keeps its signature (Ability 1) charge when you switch away and back. Off = vanilla reset.", "field:GearCfg.SIG_KEEP"),
''')
rep('''SW_ROWK = ["swing.tiers", "swing.odds"]
''', '''SW_ROWK = ["swing.tiers", "swing.odds"]
# 0.2.10: the signature-charge row of a fresh file (an existing file gets it the first time it is changed in Server Setup)
SG_HEAD = "# ---- signature charge kept on a weapon swap (SkyyGear 0.2.10) ----"
SG_ROWK = ["gear.signatureKeep"]
assert all(32 <= ord(_c) < 127 for _c in SG_HEAD) and "=" not in SG_HEAD
''')
rep('''    for k in SW_ROWK:
        scal(k)
''', '''    for k in SW_ROWK:
        scal(k)
    L += ["", SG_HEAD]         # 0.2.10: the signature-charge row at the very end of a fresh file (no one-time update adds it)
    for k in SG_ROWK:
        scal(k)
''')
rep('''              ("SWING_ON", "boolean", "true"), ("SWING_ODDS", "String", jstr(SPEED_ODDS_DEF))]''',
    '''              ("SWING_ON", "boolean", "true"), ("SWING_ODDS", "String", jstr(SPEED_ODDS_DEF)),
              # 0.2.10 the signature charge kept on a weapon swap
              ("SIG_KEEP", "boolean", "true")]''')
rep('''  SWING_W = swingOdds(swo);
''', '''  SWING_W = swingOdds(swo);
  // 0.2.10 the signature charge kept on a weapon swap (off: GearSigTick drops every kept charge on its next pass)
  SIG_KEEP = pbool(p, "gear.signatureKeep", true);
''')

# ================================================================================================================ engine facts + the new classes
SIG_PY = r'''
# ================================================================= 0.2.10 SIGNATURE CHARGE KEPT ON A SWAP (Skyy LOCKED 2026-10-08; see the header)
SG = {
    "ISAE": "com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent",
    "HOTB": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "SMMG": "com.hypixel.hytale.server.core.entity.StatModifiersManager",
    "IOMAP": "it.unimi.dsi.fastutil.ints.Int2ObjectMap",
    "RECC": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Recalculate",
}
for _k in SG:
    assert _k not in T, "0.2.10 token clashes: " + _k
T.update(SG)
for c, m in ((SG["ISAE"], "getInventorySectionId"), (SG["ISAE"], "getPreviousSlot"), (SG["ISAE"], "getNewSlot"),
             (SG["HOTB"], "getComponentType"), (SG["HOTB"], "getSectionId"), (SG["HOTB"], "getActiveSlot"), (SG["HOTB"], "getInventory"),
             (SG["SMMG"], "recalculateEntityStatModifiers"), (SG["SMMG"], "queueEntityStatsToClear"), (SG["SMMG"], "scheduleRecalculate"),
             (PB["ESM"], "getStatModifiersManager"), (PB["ESM"], "setStatValue"), (PB["ESM"], "get"), (PB["ESV"], "getMax"), (PB["ESV"], "get"),
             (PB["ESV"], "getIndex"), (PB["DST"], "getSignatureEnergy"), (PB["DTHC"], "getComponentType"), (ITM, "getWeapon"),
             (IWP, "getStatModifiers"), (IWP, "getEntityStatsToClear"), (ICE, "getComponentType"), (ICE, "getItemContainer"),
             (ICE, "getTransaction"), (TXN, "wasSlotModified"), (IS, "getDurability"), (IS, "getItemId"), (IC, "getItemStack"),
             (IC, "getCapacity"), (PB["PDEV"], "getPlayerRef"), (PRE, "getPlayerRef"), (UNI, "get"), (UNI, "getPlayers"), (PR, "getUuid")):
    B.probe(pool, c, m)
_rcm = pool.get(SG["SMMG"]).getDeclaredMethod("recalculateEntityStatModifiers")
assert J0["Modifier"].isPublic(_rcm.getModifiers()) and str(_rcm.getSignature()) == ("(Lcom/hypixel/hytale/component/Ref;L%s;Lcom/hypixel/hytale/component/ComponentAccessor;)V"
                                                                                     % PB["ESM"].replace(".", "/")), "recalculateEntityStatModifiers changed"
import jpype
_JIP = jpype.JClass("javassist.bytecode.InstructionPrinter")
_JPS, _JBOS = jpype.JClass("java.io.PrintStream"), jpype.JClass("java.io.ByteArrayOutputStream")


def sg_code(cls, meth, sig=None):
    out = []
    for _mm in pool.get(cls).getDeclaredMethods():
        if str(_mm.getName()) == meth and (sig is None or str(_mm.getSignature()) == sig):
            _b = _JBOS()
            _JIP(_JPS(_b)).print_(_mm)
            out.append(str(_b.toString()))
    assert out, "no %s.%s%s" % (cls, meth, sig or "")
    return "\n".join(out)


# the WHY (re-checked on every build: a new engine that changes it stops the build instead of fighting a different reset)
_set = sg_code("com.hypixel.hytale.server.core.inventory.ActiveSlotInventoryComponent", "setActiveSlot",
               "(BLcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/ComponentAccessor;)V")
assert _set.index("putfield") < _set.index("InventorySetActiveSlotEvent.<init>") < _set.index("ComponentAccessor.invoke"), \
    "Hotbar.setActiveSlot no longer sets the slot before it dispatches InventorySetActiveSlotEvent"
_inv = sg_code("com.hypixel.hytale.component.CommandBuffer", "invoke", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/system/EcsEvent;)V")
assert "Store.internal_invoke" in _inv, "CommandBuffer.invoke(Ref, EcsEvent) no longer dispatches at once"
_ase = sg_code("com.hypixel.hytale.server.core.inventory.InventorySystems$ActiveSlotChangedEntityEventSystem", "handle",
               "(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;L%s;)V"
               % SG["ISAE"].replace(".", "/"))
for _n in ("StatModifiersManager.scheduleRecalculate", "InventoryComponent.getItemInHand", "ItemWeapon.getEntityStatsToClear",
           "StatModifiersManager.queueEntityStatsToClear"):
    assert _n in _ase, "ActiveSlotChangedEntityEventSystem no longer calls " + _n
assert "minimizeStatValue" not in _ase and "setStatValue" not in _ase, "the slot-change system now writes the stat itself"
_rec = sg_code(SG["SMMG"], "recalculateEntityStatModifiers")
assert _rec.index("StatModifiersManager.recalculate(Z)") < _rec.index("EntityStatMap.minimizeStatValue") < _rec.index("IntSet.clear") \
    < _rec.index("StatModifiersManager.addItemStatModifiers"), "recalculateEntityStatModifiers: flag -> clear the queued stats -> item modifiers changed"
_rec5 = "\n".join(_rec.split("\n")[:5])
assert "StatModifiersManager.recalculate(Z)" in _rec5 and "ifne" in _rec5 and "return" in _rec5, \
    "recalculateEntityStatModifiers no longer returns at once when its flag is clear (GearSigTick calls it as a flush)"
_rsys = sg_code("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Recalculate", "tick")
assert "StatModifiersManager.recalculateEntityStatModifiers" in _rsys, "EntityStatsSystems$Recalculate no longer calls recalculateEntityStatModifiers"
_hot = sg_code("com.hypixel.hytale.server.core.inventory.InventorySystems$LegacyHotbarChangeStatSystem", "tick")
assert "Transaction.wasSlotModified" in _hot and "getActiveSlot" in _hot, "LegacyHotbarChangeStatSystem: only an ACTIVE-slot content change clears"
# the stat assets the meter lives in (read-only Assets.zip): Min 0 / Max 0 (the weapon sets the max) / Shared; the bows' charge stat
_sge = json.loads(AZ.read("Server/Entity/Stats/SignatureEnergy.json").decode("utf-8"))
_sgc = json.loads(AZ.read("Server/Entity/Stats/SignatureCharges.json").decode("utf-8"))
assert _sge.get("Max") == 0 and _sge.get("Min") == 0 and _sge.get("Shared") is True, "SignatureEnergy.json changed: %s" % _sge
assert _sgc.get("Min") == 0 and _sgc.get("Shared") is True, "SignatureCharges.json changed: %s" % _sgc
SG_CLEAR = {}
for _n in AZ_NAMES:
    if _n.startswith("Server/Item/Items/Weapon/") and _n.endswith(".json"):
        try:
            _w = json.loads(AZ.read(_n).decode("utf-8")).get("Weapon") or {}
        except Exception:
            continue
        for _st in _w.get("EntityStatsToClear") or []:
            SG_CLEAR[_st] = SG_CLEAR.get(_st, 0) + 1
assert SG_CLEAR.get("SignatureEnergy", 0) >= 8, "the vanilla weapon templates no longer clear SignatureEnergy on equip: %s" % SG_CLEAR
print("0.2.10 signature keep: engine reset path checked (setActiveSlot -> event -> queueEntityStatsToClear -> Recalculate minimize); "
      "vanilla EntityStatsToClear files %s" % sorted(SG_CLEAR.items()))

gsg = mk("GearSig")                     # the kept charges (memory only) + the leave / settle / invalidate rules
gsgs = mk("GearSigSlotSys", EES)        # InventorySetActiveSlotEvent -> keep the meter of the weapon being left
gsgi = mk("GearSigInvSys", EES)         # InventoryChangeEvent (hotbar) -> a kept slot whose item left loses its charge
gsgt = mk("GearSigTick", ETS)           # a pending swap: the engine's own recalc first, then the restore (clamped to the new max)
gsgtU = mk("GearSigTickU", PKG + ".GearSigTick")   # review fix 2: the unordered fallback (one registerSystem per class)
gsgb = mk("GearSigBye")                 # PlayerDisconnectEvent + PlayerReadyEvent -> forget (+ review fix 3: sweep players who are gone)
SIG_CLASSES = [gsg, gsgs, gsgi, gsgt, gsgtU, gsgb]
# STATE: UUID -> Object[] { String profileEpoch, int[] { pending 0/1, origin slot }, HashMap slot(Integer) -> Object[] { String itemId,
# Double durability, Float energy, Float charges }, float[] { floating energy, floating charges } }. "Floating" = the part of the meter that
# is still the SAME charge as the kept value of the origin slot (the engine did not clear it: a non-weapon keeps SignatureCharges under its
# base max 100, a pack weapon without EntityStatsToClear keeps both). Only players with a kept charge or a pending swap are in it.
F(gsg, "public static final java.util.concurrent.ConcurrentHashMap STATE = new java.util.concurrent.ConcurrentHashMap();")
# counters: 0 kept, 1 restored, 2 dropped (the item left / changed), 3 forgotten (logout / death / world / profile / off), 4 not kept (meter
# not settled yet), 5 carried by the engine (taken off a kept value)
F(gsg, "public static final int[] N = new int[6];")
M(gsg, r"""
public static int sigIdx() {
  return @DST@.getSignatureEnergy();
}""")
M(gsg, r"""
public static int chgIdx(@ESM@ m) {
  if (m == null) return -1;
  try {
    @ESV@ v = m.get("SignatureCharges");
    return v == null ? -1 : v.getIndex();
  } catch (Throwable t) { return -1; }
}""")
M(gsg, r"""
public static float val(@ESM@ m, int i) {
  if (m == null || i < 0) return 0.0f;
  @ESV@ v = m.get(i);
  return v == null ? 0.0f : v.get();
}""")
M(gsg, r"""
public static float maxOf(@ESM@ m, int i) {
  if (m == null || i < 0) return 0.0f;
  @ESV@ v = m.get(i);
  return v == null ? 0.0f : v.getMax();
}""")
# a weapon with a signature = its item stat modifiers set the SignatureEnergy max (vanilla templates and pack weapons alike)
M(gsg, r"""
public static boolean hasSig(@IS@ s, int e) {
  if (s == null || s.isEmpty() || e < 0) return false;
  @ITM@ it = s.getItem();
  if (it == null) return false;
  @IWP@ w = it.getWeapon();
  if (w == null) return false;
  @IOMAP@ mm = w.getStatModifiers();
  return mm != null && mm.get(e) != null;
}""")
M(gsg, r"""
public static boolean same(@IS@ a, String id, double dur) {
  return a != null && !a.isEmpty() && id != null && id.equals(a.getItemId()) && a.getDurability() == dur;
}""")
M(gsg, r"""
public static @IS@ at(@IC@ c, int slot) {
  if (c == null || slot < 0 || slot >= c.getCapacity()) return null;
  return c.getItemStack((short) slot);
}""")
M(gsg, r"""
public static void forget(java.util.UUID u) {
  if (u != null && STATE.remove(u) != null) N[3] = N[3] + 1;
}""")
# the player's state; a moved profile epoch (profile switch) forgets everything first (PROFILES-CONTRACT)
M(gsg, r"""
public static Object[] state(java.util.UUID u, boolean make) {
  if (u == null) return null;
  String ep = @PKG@.Gear.epoch(u);
  Object[] s = (Object[]) STATE.get(u);
  if (s != null && !ep.equals(s[0])) { forget(u); s = null; }
  if (s == null && make) {
    s = new Object[] { ep, new int[] { 0, -1 }, new java.util.HashMap(), new float[] { 0.0f, 0.0f } };
    STATE.put(u, s);
  }
  return s;
}""")
M(gsg, r"""
public static boolean pending(java.util.UUID u) {
  if (u == null) return false;
  Object[] s = (Object[]) STATE.get(u);
  return s != null && ((int[]) s[1])[0] != 0;
}""")
M(gsg, r"""
public static int kept(java.util.UUID u) {
  if (u == null) return 0;
  Object[] s = (Object[]) STATE.get(u);
  return s == null ? 0 : ((java.util.HashMap) s[2]).size();
}""")
# review fix 1: SkyySkills' Archer perk keeps the crossbow meter itself (ONE banked meter, LOCKED) - its crossbow ids are left to it.
# XBC = { Long readAt, String[] prefixes } (5 s cache; one atomic swap, any world thread); the prefixes are SkyySkills' own row
# perk.archery.keepLoaded.items through its config kit op "get" (an empty / unreadable answer = its own default Weapon_Crossbow_).
F(gsg, "public static volatile Object[] XBC = null;")
M(gsg, r"""
public static String[] xbowPrefixes() {
  long now = System.currentTimeMillis();
  Object[] c = XBC;
  if (c != null && now - ((Long) c[0]).longValue() >= 0L && now - ((Long) c[0]).longValue() < 5000L) return (String[]) c[1];
  java.util.ArrayList l = new java.util.ArrayList();
  if (@PKG@.Gear.bget("config:def:SkyySkills") != null) {
    String raw = null;
    try {
      java.util.function.Function f = @PKG@.Gear.fn("config:fn:SkyySkills");
      if (f != null) {
        Object r = f.apply(new Object[] { "get", "perk.archery.keepLoaded.items" });
        if (r instanceof String) raw = (String) r;
      }
    } catch (Throwable t) { raw = null; }
    String[] ps = raw == null ? new String[0] : raw.split(",");
    for (int i = 0; i < ps.length; i++) {
      String t2 = ps[i].trim();
      if (t2.length() > 0) l.add(t2);
    }
    if (l.isEmpty()) l.add("Weapon_Crossbow_");
  }
  String[] a = new String[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
  XBC = new Object[] { Long.valueOf(now), a };
  return a;
}""")
M(gsg, r"""
public static boolean skillsKeeps(@IS@ s) {
  if (s == null || s.isEmpty()) return false;
  String id = s.getItemId();
  if (id == null) return false;
  String[] a = xbowPrefixes();
  for (int i = 0; i < a.length; i++) if (a[i] != null && a[i].length() > 0 && id.startsWith(a[i])) return true;
  return false;
}""")
# review fix 3: drop the entries of players who are no longer on the server (a slot event after the logout clean-up re-made one)
M(gsg, r"""
public static int sweepWith(java.util.Set online) {
  if (online == null || STATE.isEmpty()) return 0;
  Object[] ks = STATE.keySet().toArray();
  int n = 0;
  for (int i = 0; i < ks.length; i++) {
    if (online.contains(ks[i])) continue;
    if (STATE.remove(ks[i]) != null) { N[3] = N[3] + 1; n++; }
  }
  return n;
}""")
M(gsg, r"""
public static int sweep() {
  if (STATE.isEmpty()) return 0;
  try {
    @UNI@ un = @UNI@.get();
    if (un == null) return 0;
    java.util.Collection ps = un.getPlayers();
    if (ps == null) return 0;
    java.util.HashSet on = new java.util.HashSet();
    java.util.Iterator it = ps.iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@) on.add(((@PR@) o).getUuid());
    }
    return sweepWith(on);
  } catch (Throwable t) { return 0; }
}""")
# the event (the meter still shows the weapon being LEFT: nothing is cleared before the next recalc). Returns 0 off, 1 kept, 2 nothing to
# keep (no signature weapon / an empty meter), 3 not kept (an earlier swap of this tick is not settled - the meter is not this weapon's), 4 busy,
# 5 left to SkyySkills (its crossbow perk keeps that meter - review fix 1)
M(gsg, r"""
public static int leave(java.util.UUID u, @IC@ hot, @ESM@ m, int prev, int now) {
  if (u == null) return 0;
  if (!@PKG@.GearCfg.SIG_KEEP) { forget(u); return 0; }
  if (@PKG@.Gear.busy(u)) { forget(u); return 4; }
  Object[] s = state(u, true);
  int[] f = (int[]) s[1];
  java.util.HashMap k = (java.util.HashMap) s[2];
  int code = 2;
  if (f[0] != 0) {
    N[4] = N[4] + 1;
    code = 3;
  } else {
    @IS@ l = at(hot, prev);
    int e = sigIdx();
    int c = chgIdx(m);
    float ev = val(m, e);
    float cv = val(m, c);
    boolean sk = hasSig(l, e) && skillsKeeps(l);
    if (!sk && hasSig(l, e) && (ev > 0.0f || cv > 0.0f)) {
      k.put(Integer.valueOf(prev), new Object[] { l.getItemId(), Double.valueOf(l.getDurability()), Float.valueOf(ev), Float.valueOf(cv) });
      f[1] = prev;
      float[] fl = (float[]) s[3];
      fl[0] = ev;
      fl[1] = cv;
      N[0] = N[0] + 1;
      code = 1;
    } else {
      k.remove(Integer.valueOf(prev));
      if (f[1] == prev) f[1] = -1;
      if (sk) code = 5;
    }
  }
  f[0] = 1;
  return code;
}""")
# after the engine's recalc (clear + the new max): the floating part is what the meter still holds of the origin's kept value; it comes OFF
# that kept value the moment the held item can use it (its own stat modifiers have that stat: a signature weapon / a bow) - a stone or a
# weapon without a signature cannot, so it only floats on (and dies when the engine clears it). Then the kept value of the slot now held
# comes back (same item id + durability, clamped to the new max, never lower than the meter shows). Returns 0 no state, 1 restored,
# 2 refused (the item changed), 3 nothing kept for this slot
M(gsg, r"""
public static int settle(java.util.UUID u, @IC@ hot, @ESM@ m, int active) {
  Object[] s = state(u, false);
  if (s == null) return 0;
  int[] f = (int[]) s[1];
  java.util.HashMap k = (java.util.HashMap) s[2];
  f[0] = 0;
  int e = sigIdx();
  int c = chgIdx(m);
  float ce = val(m, e);
  float cc = val(m, c);
  float[] fl = (float[]) s[3];
  if (f[1] >= 0) {
    Integer lk = Integer.valueOf(f[1]);
    Object[] x = (Object[]) k.get(lk);
    float fe = Math.min(fl[0], ce);
    float fc = Math.min(fl[1], cc);
    if (x == null || f[1] == active) { fe = 0.0f; fc = 0.0f; }
    else {
      @IS@ held = at(hot, active);
      boolean took = false;
      if (fe > 0.0f && hasSig(held, e)) { x[2] = Float.valueOf(Math.max(0.0f, ((Float) x[2]).floatValue() - fe)); fe = 0.0f; took = true; }
      if (fc > 0.0f && hasSig(held, c)) { x[3] = Float.valueOf(Math.max(0.0f, ((Float) x[3]).floatValue() - fc)); fc = 0.0f; took = true; }
      if (took) N[5] = N[5] + 1;
      if (((Float) x[2]).floatValue() <= 0.0f && ((Float) x[3]).floatValue() <= 0.0f) k.remove(lk);
    }
    fl[0] = fe;
    fl[1] = fc;
    if (fe <= 0.0f && fc <= 0.0f) f[1] = -1;
  }
  int code = 3;
  Object[] r = (Object[]) k.remove(Integer.valueOf(active));
  if (r != null) {
    @IS@ cur = at(hot, active);
    if (same(cur, (String) r[0], ((Double) r[1]).doubleValue()) && hasSig(cur, e) && !skillsKeeps(cur)) {
      float te = Math.min(maxOf(m, e), Math.max(ce, ((Float) r[2]).floatValue()));
      if (te > ce) m.setStatValue(e, te);
      if (c >= 0) {
        float tc = Math.min(maxOf(m, c), Math.max(cc, ((Float) r[3]).floatValue()));
        if (tc > cc) m.setStatValue(c, tc);
      }
      N[1] = N[1] + 1;
      code = 1;
    } else {
      N[2] = N[2] + 1;
      code = 2;
    }
  }
  if (k.isEmpty()) STATE.remove(u);
  return code;
}""")
# a hotbar change touching a kept slot: the charge stays only while the same item (id + durability) is still there. Returns the drops.
M(gsg, r"""
public static int changed(java.util.UUID u, @IC@ c, @TXN@ t) {
  if (u == null || t == null || STATE.isEmpty()) return 0;
  Object[] s = (Object[]) STATE.get(u);
  if (s == null) return 0;
  java.util.HashMap k = (java.util.HashMap) s[2];
  Object[] ks = k.keySet().toArray();
  int n = 0;
  for (int i = 0; i < ks.length; i++) {
    int slot = ((Integer) ks[i]).intValue();
    if (!t.wasSlotModified((short) slot)) continue;
    Object[] x = (Object[]) k.get(ks[i]);
    if (x != null && same(at(c, slot), (String) x[0], ((Double) x[1]).doubleValue())) continue;
    k.remove(ks[i]);
    N[2] = N[2] + 1;
    n++;
  }
  if (k.isEmpty() && ((int[]) s[1])[0] == 0) STATE.remove(u);
  return n;
}""")
M(gsg, r"""
public static String statusText() {
  return "signature charge kept on a weapon swap " + (@PKG@.GearCfg.SIG_KEEP ? "on" : "OFF (gear.signatureKeep)");
}""")
M(gsg, r"""
public static String counters() {
  return "kept " + N[0] + ", restored " + N[1] + ", dropped " + N[2] + ", forgotten " + N[3] + ", not settled " + N[4] + ", carried " + N[5]
      + "; players holding a kept charge " + STATE.size();
}""")
# the systems (thin: every rule above is a static the bare-JVM harness runs on a real EntityStatMap / container)
event_system(gsgs, "GearSigSlotSys", SG["ISAE"], PLAYER_Q, r"""
    if (!(ev instanceof @ISAE@)) return;
    @ISAE@ e = (@ISAE@) ev;
    @HOTB@ hc = (@HOTB@) chunk.getComponent(idx, @HOTB@.getComponentType());
    if (hc == null || e.getInventorySectionId() != hc.getSectionId()) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    @ESM@ m = (@ESM@) chunk.getComponent(idx, @ESM@.getComponentType());
    if (m == null) return;
    @PKG@.GearSig.leave(pr.getUuid(), hc.getInventory(), m, e.getPreviousSlot(), e.getNewSlot());""")
event_system(gsgi, "GearSigInvSys", ICE, PLAYER_Q, r"""
    if (@PKG@.GearSig.STATE.isEmpty() || !(ev instanceof @ICE@)) return;
    @ICE@ e = (@ICE@) ev;
    if (e.getComponentType() != @HOTB@.getComponentType()) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.GearSig.changed(pr.getUuid(), e.getItemContainer(), e.getTransaction());""")
F(gsgt, "public static boolean FAILED_ONCE = false;")
# review fix 2: ordered AFTER EntityStatsSystems$Recalculate (the GearLockSys pattern; RECALC set by setup, null = unordered)
F(gsgt, "public static Class RECALC;")
F(gsgt, "public java.util.Set deps;")
C(gsgt, r"""
public GearSigTick(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  if (ordered && RECALC != null) this.deps.add(new @SDEP@(@ORD@.AFTER, RECALC));
}""")
M(gsgt, "public java.util.Set getDependencies() { return this.deps; }")
M(gsgt, "public boolean isParallel(int a, int b) { return false; }")
M(gsgt, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(gsgt, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  if (@PKG@.GearSig.STATE.isEmpty()) return;
  try {
    if (!@PKG@.GearCfg.SIG_KEEP) { @PKG@.GearSig.STATE.clear(); return; }
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if (!@PKG@.GearSig.STATE.containsKey(u)) return;
    if (chunk.getComponent(idx, @DTHC@.getComponentType()) != null || @PKG@.Gear.busy(u)) { @PKG@.GearSig.forget(u); return; }
    if (@PKG@.GearSig.state(u, false) == null || !@PKG@.GearSig.pending(u)) return;
    @REF@ ref = chunk.getReferenceTo(idx);
    @ESM@ m = (@ESM@) chunk.getComponent(idx, @ESM@.getComponentType());
    @HOTB@ hc = (@HOTB@) chunk.getComponent(idx, @HOTB@.getComponentType());
    if (ref == null || m == null || hc == null) { @PKG@.GearSig.forget(u); return; }
    // the engine's own recalc (its queued clear + the held item's max) - a no-op when EntityStatsSystems$Recalculate already ran it
    m.getStatModifiersManager().recalculateEntityStatModifiers(ref, m, cb);
    @PKG@.GearSig.settle(u, hc.getInventory(), m, hc.getActiveSlot());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.Gear.warn("signature keep tick failed (logged once): " + t); }
  }
}""")
C(gsgtU, "public GearSigTickU() { super(false); }")
gsgb.addInterface(pool.get("java.util.function.Consumer"))
C(gsgb, "public GearSigBye() { }")
M(gsgb, r"""
public void accept(Object ev) {
  try {
    if (ev instanceof @PDEV@) {
      @PR@ pr = ((@PDEV@) ev).getPlayerRef();
      if (pr != null) @PKG@.GearSig.forget(pr.getUuid());
      @PKG@.GearSig.sweep();
      return;
    }
    if (ev instanceof @PRE@) {
      @REF@ r = ((@PRE@) ev).getPlayerRef();
      if (r == null) return;
      @ST@ st = r.getStore();
      if (st == null) return;
      @PR@ pr2 = (@PR@) st.getComponent(r, @PR@.getComponentType());
      if (pr2 != null) @PKG@.GearSig.forget(pr2.getUuid());
      @PKG@.GearSig.sweep();
    }
  } catch (Throwable t) { }
}""")

'''
rep('''# ================================================================= plugin (spec Appendix A setup() order)
''', SIG_PY + '''# ================================================================= plugin (spec Appendix A setup() order)
''')
rep('''                                                        "GearChestBreakSys", "GearCraftPreSys")))''',
    '''                                                        "GearChestBreakSys", "GearCraftPreSys",
                                                        # 0.2.10 the signature charge kept on a weapon swap
                                                        "GearSigSlotSys", "GearSigInvSys")))''')
rep('''  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.GearBye());
''', '''  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.GearBye());
  // 0.2.10: the kept signature charges are memory only - forgotten on logout and on every PlayerReadyEvent (join / world switch)
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.GearSigBye());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.GearSigBye());
  // 0.2.10 review fix 2: the restore tick runs AFTER the engine's EntityStatsSystems$Recalculate (unordered fallback + one WARN)
  @PKG@.GearSigTick.RECALC = @PKG@.GearFx.cls("@RECC@");
  if (@PKG@.GearSigTick.RECALC == null) @PKG@.Gear.warn("EntityStatsSystems$Recalculate not found - the signature keep tick runs unordered (it runs the engine's recalc itself first)");
  try { getEntityStoreRegistry().registerSystem(new @PKG@.GearSigTick(true)); }
  catch (Throwable tsg) {
    @PKG@.Gear.warn("could not order the signature keep tick after EntityStatsSystems$Recalculate (" + tsg + ") - unordered fallback");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.GearSigTickU()); } catch (Throwable tsgb) { @PKG@.Gear.warn("GearSigTickU could not be registered: " + tsgb); }
  }
''')
rep('''+ @PKG@.GearSpeed.readyText() + "; Reforge level up "''', '''+ @PKG@.GearSpeed.readyText() + "; " + @PKG@.GearSig.statusText() + "; Reforge level up "''')
rep('''CRIT_CLASSES + [gspd]
''', '''CRIT_CLASSES + [gspd] + SIG_CLASSES
''')
# the build line names the new part
rep('''print("classes written: %d + %d config kit classes; %d config rows; %d stats; %d quality assets" % (len(ALL), len(kit.classes), len(CFG_ROWS), NS, NR))''',
    '''print("classes written: %d + %d config kit classes; %d config rows; %d stats; %d quality assets" % (len(ALL), len(kit.classes), len(CFG_ROWS), NS, NR))
print("0.2.10: signature charge kept on a weapon swap - %s (row gear.signatureKeep, default on)" % ", ".join(str(c.getName()).rsplit(".", 1)[1] for c in SIG_CLASSES))''')

# ================================================================================================================ write
assert s.count("registerSystem(") == SYS0 + 2 and s.count("registerCommand(") == CMD0, \
    "0.2.10 registers its slot / inventory systems through the _reg list; only GearSigTick (ordered) + GearSigTickU (its fallback) are new registerSystem text"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))
