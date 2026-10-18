"""Derive SkyySacks/build_skyysacks_0.8.20.py from the SET pin 0.8.19 (the GENERATED build_skyysacks_0.8.19.py; edit THIS file, then
regenerate: python tools/sacks_0_8_20_patch.py; never re-run sacks_0_8_19_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.19 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_20_patch.py   then   python SkyySacks/build_skyysacks_0.8.20.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.20.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.20 (2026-10-17) = ZONE ALLOYS + FURNACE CHARM in the /craft Furnace (round ores01, research/Zone-Ores-Alloys-Spec.md 3 / 4 / 5 / 7 B3).
Skyy 2026-10-17: "Yes - start the zone ores + alloys + Furnace Charm round right after the current set deploys." + "Yes, build with defaults
(Recommended)" (the spec's questions: the charm works in the /craft Furnace only, 1 + 1 -> 1 alloys, the charm must be equipped).
gear.md 2026-10-17: "T1-T5 upgrades cost each zone's two metals and unlock that zone's alloy ... Keep your speed/fuel numbers and Eternal
Flame at Charcoal tier 7. Collections for base metals only, no alloy collections."
  1. ALLOY ROWS: the Furnace tab also lists every CraftingRecipe whose bench requirement id is "SkyyAlloy" (B1's standalone recipe files
     Server/Item/Recipes/SkyWynn/Alloy_<Name>.json in SkyyWorldGen - a bench id no block has, so a placed vanilla furnace never makes them;
     CraftingPlugin.onRecipeLoad files an unknown bench id under its own BenchRecipeRegistry (computeIfAbsent), no validation, and the
     recipe is in CraftingRecipe's asset map like the vanilla Salvage files). They queue in the player's own Furnace ProcBench (its fuel,
     tier speed, output slot), sorted with the other rows by tier then name (RecipeCmp, tools/tier_tags.py at build time).
     LOCK: the alloy's tier (ProcBench.ALLOY_IDS: Bronze T1, Dusk T2, Azurvane T3, Cinder T4, Lumen T5, Electrum T1 - Skyy: "Electrum
     (Gold + Silver, unlocked at the Bronze furnace tier)"; by id, else by the metal word of the recipe's output id Ingredient_Bar_<Word>;
     an unknown SkyyAlloy output = its RequiredTierLevel, else T5) must be <= the equipped Furnace Charm tier (Eternal Flame = T5). A locked row is drawn greyed, no buttons,
     "<name> - Furnace Charm T<n> unlocks this"; procQueue checks it again on the click (nothing is taken when locked) and refuses an alloy
     on any bench but the Furnace. Charm removed later: queued alloy units finish (paid already); new ones refuse.
     Instant crafting never makes them: tableOnly() is true for a Processing bench other than Salvagebench (instant tabs, search,
     Collections tab, sacks:fn craft all refuse), as before.
  2. FURNACE CHARM (bridge acc:smelt:<uuid> = "<tier 0-5>|<timePct>|<fuelPct>|<eternal 0/1>|<pkey>", SkyyAccessories 0.5.25). Read by
     ProcBench.smelt(key) on every advance (outside the bench lock) - only for the Furnace and only while <key> is that player's ACTIVE
     profile key (field 5 + SackPool.pkey); absent / malformed / tier 0 = no bonus = 0.8.19 exactly. Clamps: tier 0-5, time 0-90, fuel 0-1000.
     - time: unit time = vanilla time x (1 - bench tier reduction) x (1 - timePct). ProcJob.unitMs keeps the BASE time (bench tier only,
       fixed at queue time as before); the charm's cut is applied LIVE in advanceC (critic fix: removing the charm slows the running job,
       exactly like the fuel rate - no lending one charm for a big batch); describe / queueMs show the live time; the row's "each" too.
     - acc:smelt has a 5th field = the profile key it describes (critic fix, SkyyAccessories 0.5.25): smelt(k) needs field 5 == k (the
       bench's key) - 4 fields or another key = no bonus, so a profile switch never carries the old profile's charm (alloy lock).
       procQueue and buildProc read smelt(k) themselves for the lock.
     - join / restart (critic fix): while the player is online and acc:smelt:<uuid> is absent, the Furnace does not replay (clock kept)
       until it appears or 10 s pass (ProcBench.waitFrom / holdFor) - an Eternal Flame owner's offline span never burns fuel before the
       value is published.
     - fuel: advanceC drains step x (1 + fuelPct/100) fuel ms per processed ms (ceil); when the loaded fuel ms cannot pay a whole step the
       step shrinks to what it pays (at least 1 ms, the bench never stalls) and fuelMs ends at 0. Read live on every advance, so equipping
       / removing the charm mid-job only changes the fuel rate from then on (the replayed span since the last advance uses the state at
       that advance). No item is created or removed by it: fuel items are only burned by burnOne as before.
     - Eternal Flame (eternal 1): the Furnace burns nothing (no burnOne, fuelMs untouched, loaded fuel stays and can be unloaded), so no
       Charcoal byproduct; never "OUT OF FUEL", no fuel warning; the status line says "Eternal Flame ... needs no fuel".
     The Tannery is untouched. The status line names the charm ("Furnace Charm T3 30 percent faster", fuel time at the charm's rate).
  3. CHARCOAL COLLECTION (spec 5, SkyyCollections 0.2.25 B4): every Ingredient_Charcoal the Furnace's ExtraOutput puts into the output
     slot (burnOne) is also counted in the new ledger <bench>.collDone (saved in the processing file next to xpDone, cap 1,000,000).
     ProcTask.drainColl pays it once the profile is settled: coll:fn:add {UUID, "Ingredient_Charcoal", Long qty <= 256, "sacks:furnace",
     pkey}; TRUE drains exactly that count (crafts.log COLLECTION line); FALSE / null / no function / an error keeps the ledger and waits
     30 s per key (no Charcoal collection yet, source not accepted, player offline). Never for the no-output fallback, cancel or unload.
  Saved data: + <bench>.collDone in Skyy_SkyySacks/processing/<pkey>.properties (written only when not empty); nothing else changes.
  No command / system / config key / permission added. ROLLBACK to 0.8.19: safe - alloy jobs already queued still finish (finishUnit reads
  the recipe asset by id; with SkyyWorldGen rolled back too their inputs go to the output slot, the 0.7.0 fallback), the charm simply stops
  applying, an unpaid collDone ledger is dropped at the next save (only uncredited Charcoal collection counts are lost, never items).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.19.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.20.py"))
assert P.has('VERSION = "0.8.19"\n') and P.has("supply:fn:claims") and P.has('"Materials come from your inventory, the Void and your Void Charms - sorted by tier."'), "not the live generated SkyySacks 0.8.19"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.20 (2026-10-17)"):].rstrip() + "\n"

# the alloy ladder (spec 3, ids FINAL): output item id -> the Furnace Charm tier that unlocks it
ALLOYS = [("Ingredient_Bar_Bronze", 1), ("Ingredient_Bar_Dusk_SkyWynn", 2), ("Ingredient_Bar_Azurvane_SkyWynn", 3),
          ("Ingredient_Bar_Cinder_SkyWynn", 4), ("Ingredient_Bar_Lumen_SkyWynn", 5),
          ("Ingredient_Bar_Electrum_SkyWynn", 1)]   # Skyy: "Electrum (Gold + Silver, unlocked at the Bronze furnace tier)"
ALLOY_WORDS = [a.split("_")[2] for a, _t in ALLOYS]   # the metal word: an output id with another suffix still finds its tier

# ---- header, version
P.rep('''  ROLLBACK to 0.8.18: safe (same files, same keys).
"""
''', '''  ROLLBACK to 0.8.18: safe (same files, same keys).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.19"\n', 'VERSION = "0.8.20"\n')

# ---- 2. ProcBench fields: owner key, the charm state of the last advance, the Charcoal ledger, the alloy ladder
P.rep('''pben.addField(CtField.make("public static final int XP_CAP = 10000;", pben))
''', '''pben.addField(CtField.make("public static final int XP_CAP = 10000;", pben))
# 0.8.20 (tools/sacks_0_8_20_patch.py docstring): key = the profile key this bench belongs to (set by ProcStore; memory only); cTier / cTime /
# cFuel / cEternal = the Furnace Charm (acc:smelt) as the last advance read it; collDone = Charcoal not yet credited through coll:fn:add
pben.addField(CtField.make("public String key;", pben))
pben.addField(CtField.make("public int cTier;", pben))
pben.addField(CtField.make("public int cTime;", pben))
pben.addField(CtField.make("public int cFuel;", pben))
pben.addField(CtField.make("public boolean cEternal;", pben))
pben.addField(CtField.make("public long waitFrom;", pben))   # critic fix: when this bench first found acc:smelt absent (0 = not waiting)
pben.addField(CtField.make("public java.util.LinkedHashMap collDone;", pben))
pben.addField(CtField.make("public static final int COLL_CAP = 1000000;", pben))
pben.addField(CtField.make('public static final String ALLOY_BENCH = "SkyyAlloy";', pben))
pben.addField(CtField.make('public static final String[] ALLOY_IDS = new String[] { %s };', pben))
pben.addField(CtField.make("public static final int[] ALLOY_TIER = new int[] { %s };", pben))
pben.addField(CtField.make('public static final String[] ALLOY_WORD = new String[] { %s };', pben))
''' % (", ".join('"%s"' % a for a, _t in ALLOYS), ", ".join(str(t) for _a, t in ALLOYS), ", ".join('"%s"' % w for w in ALLOY_WORDS)))

# ---- 2. the charm + alloy helpers (after unitMs)
P.rep('''  long v = Math.round((t - t * red) * 1000.0);
  return v < 0L ? 0L : v;
}}""", pben))
''', '''  long v = Math.round((t - t * red) * 1000.0);
  return v < 0L ? 0L : v;
}}""", pben))
# 0.8.20: the Furnace Charm of the player whose ACTIVE profile key is k: {tier 0-5, time %, fuel %, eternal 0/1}; all 0 = none (= 0.8.19)
pben.addMethod(CtNewMethod.make(f"""
public static int[] smelt(String k) {{
  int[] z = new int[4];
  if (k == null || k.length() < 36) return z;
  try {{
    java.util.UUID u = java.util.UUID.fromString(k.substring(0, 36));
    Object v = {PKG}.SackPool.bridge().get("acc:smelt:" + u.toString());
    if (v == null) return z;
    String[] p = String.valueOf(v).trim().split("[|]");
    if (p.length < 5 || !k.equals(p[4].trim())) return z;   // critic fix: field 5 = the profile key it describes
    int t = Integer.parseInt(p[0].trim());
    int tm = Integer.parseInt(p[1].trim());
    int fu = Integer.parseInt(p[2].trim());
    int et = Integer.parseInt(p[3].trim());
    if (t <= 0 && et != 1) return z;
    if (!k.equals({PKG}.SackPool.pkey(u))) return z;
    if (t < 0) t = 0;
    if (t > 5) t = 5;
    if (tm < 0) tm = 0;
    if (tm > 90) tm = 90;
    if (fu < 0) fu = 0;
    if (fu > 1000) fu = 1000;
    z[0] = t; z[1] = tm; z[2] = fu; z[3] = et == 1 ? 1 : 0;
    if (z[3] == 1) {{ z[2] = 0; if (z[0] < 5) z[0] = 5; }}
    return z;
  }} catch (Throwable x) {{ return new int[4]; }}
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public static long charmMs(long ms, int pct) {
  if (ms <= 0L || pct <= 0) return ms;
  if (pct > 90) pct = 90;
  long v = Math.round((double) ms * (double) (100 - pct) / 100.0);
  return v < 0L ? 0L : v;
}""", pben))
# critic fix: true = hold the replay (the player is online, acc:smelt not published yet, < 10 s since this bench first saw that)
pben.addMethod(CtNewMethod.make("""
public synchronized boolean holdFor(boolean absent, boolean online, long now) {
  if (!absent || !online) { this.waitFrom = 0L; return false; }
  if (this.waitFrom <= 0L || this.waitFrom > now) this.waitFrom = now;
  return now - this.waitFrom < 10000L;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public static int alloyTierOf(String id) {
  if (id == null) return 0;
  for (int i = 0; i < ALLOY_IDS.length; i++) if (ALLOY_IDS[i].equals(id)) return ALLOY_TIER[i];
  // the metal word read from the recipe's output id (Ingredient_Bar_<Word>...): the final id of a new alloy may differ in its suffix
  if (!id.startsWith("Ingredient_Bar_")) return 0;
  String[] w = id.split("_");
  if (w.length < 3) return 0;
  for (int i = 0; i < ALLOY_WORD.length; i++) if (ALLOY_WORD[i].equals(w[2])) return ALLOY_TIER[i];
  return 0;
}""", pben))
# 0.8.20: 0 = not an alloy (no SkyyAlloy bench requirement); else the Furnace Charm tier it needs (the ladder, else RequiredTierLevel, else 5)
pben.addMethod(CtNewMethod.make(f"""
public static int alloyNeed({CRR} r) {{
  if (r == null) return 0;
  {BRQ}[] br = r.getBenchRequirement();
  boolean al = false;
  int req = 0;
  for (int i = 0; br != null && i < br.length; i++) {{
    if (br[i] == null || br[i].id == null || !br[i].id.equalsIgnoreCase(ALLOY_BENCH)) continue;
    al = true;
    if (br[i].requiredTierLevel > req) req = br[i].requiredTierLevel;
  }}
  if (!al) return 0;
  {MQ} po = r.getPrimaryOutput();
  int t = alloyTierOf(po == null ? null : po.getItemId());
  if (t > 0) return t;
  if (req <= 0 || req > 5) return 5;
  return req;
}}""", pben))
''')

# ---- constructor: the ledger
P.rep('''  this.xpDone = new java.util.LinkedHashMap();
  this.needsFuel = benchNeedsFuel(bench);''', '''  this.xpDone = new java.util.LinkedHashMap();
  this.collDone = new java.util.LinkedHashMap();
  this.needsFuel = benchNeedsFuel(bench);''')

# ---- Eternal Flame: never a fuel warning
P.rep('''  if (!this.needsFuel || this.queue.isEmpty() || this.fuelMs > 0L || !this.fuel.isEmpty() || this.warnedFuel) return false;''',
      '''  if (!this.needsFuel || this.cEternal || this.queue.isEmpty() || this.fuelMs > 0L || !this.fuel.isEmpty() || this.warnedFuel) return false;''')

# ---- 3. burnOne: Furnace charcoal into the collection ledger as it lands in the output slot
P.rep('''            addTo(this.out, outs[i].getItemId(), n);
''', '''            addTo(this.out, outs[i].getItemId(), n);
            if ("Furnace".equalsIgnoreCase(this.bench) && "Ingredient_Charcoal".equals(outs[i].getItemId())) {{
              Integer cc = (Integer) this.collDone.get(outs[i].getItemId());
              if (cc == null || cc.intValue() < COLL_CAP) addTo(this.collDone, outs[i].getItemId(), n);
            }}
''')

# ---- 2. advance: the charm's fuel rate / Eternal Flame (advanceC holds the lock; advance reads the bridge first, outside it)
P.rep('''public synchronized int advance(long now) {{
  if (!this.needsFuel) this.needsFuel = benchNeedsFuel(this.bench);
''', '''public synchronized int advanceC(long now, int[] c) {{
  if (!this.needsFuel) this.needsFuel = benchNeedsFuel(this.bench);
  this.cTier = c[0]; this.cTime = c[1]; this.cFuel = c[2]; this.cEternal = c[3] == 1;
  boolean burns = this.needsFuel && !this.cEternal;
  long fp = (long) this.cFuel;
''')
P.rep('''    long need = j.unitMs - this.progress;
''', '''    long eff = charmMs(j.unitMs, this.cTime);   // critic fix: the charm's time cut is live (ProcJob.unitMs = the base time)
    long need = eff - this.progress;
''')
P.rep('''    if (need <= 0L && j.unitMs > 0L) {{ finishUnit(j); done++; continue; }}''', '''    if (need <= 0L && eff > 0L) {{ finishUnit(j); done++; continue; }}''')
P.rep('''    t += j.unitMs * (long) j.count;''', '''    t += charmMs(j.unitMs, this.cTime) * (long) j.count;''')
P.rep('''    long left = h.unitMs - this.progress; if (left < 0L) left = 0L;
    if (h.unitMs > 0L) pct = (int) ((this.progress * 100L) / h.unitMs);''', '''    long hu = charmMs(h.unitMs, this.cTime);   // critic fix: the live unit time
    long left = hu - this.progress; if (left < 0L) left = 0L;
    if (hu > 0L) pct = (int) ((this.progress * 100L) / hu);''')
P.rep('''    if (this.needsFuel && this.fuelMs <= 0L && !burnOne()) break;''', '''    if (burns && this.fuelMs <= 0L && !burnOne()) break;''')
P.rep('''    if (this.needsFuel) {{
      if (step > this.fuelMs) step = this.fuelMs;
      this.fuelMs = this.fuelMs - step;
    }}
''', '''    if (burns && fp <= 0L) {{
      if (step > this.fuelMs) step = this.fuelMs;
      this.fuelMs = this.fuelMs - step;
    }} else if (burns) {{
      // 0.8.20 Furnace Charm: step x (1 + fuel %) fuel ms (ceil); what is loaded pays a shorter step (at least 1 ms - never stalls)
      long cost = step + (step * fp + 99L) / 100L;
      if (cost > this.fuelMs) {{
        step = (this.fuelMs * 100L) / (100L + fp);
        if (step <= 0L) step = 1L;
        this.fuelMs = 0L;
      }} else this.fuelMs = this.fuelMs - cost;
    }}
''')
P.rep('''  if (this.queue.isEmpty()) this.progress = 0L;
  return done;
}}""", pben))
''', '''  if (this.queue.isEmpty()) this.progress = 0L;
  return done;
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public int advance(long now) {
  if (!"Furnace".equalsIgnoreCase(this.bench)) return advanceC(now, new int[4]);
  boolean absent = false;
  boolean online = false;
  if (this.key != null && this.key.length() >= 36) {
    try {
      java.util.UUID u = java.util.UUID.fromString(this.key.substring(0, 36));
      absent = com.skyy.sacks.SackPool.bridge().get("acc:smelt:" + u.toString()) == null;
      if (absent) {
        com.hypixel.hytale.server.core.universe.Universe uni = com.hypixel.hytale.server.core.universe.Universe.get();
        online = uni != null && uni.getPlayer(u) != null;
      }
    } catch (Throwable t) { absent = false; }
  }
  if (holdFor(absent, online, now)) return 0;   // critic fix: the replay waits for acc:smelt (at most 10 s) - clock kept
  return advanceC(now, smelt(this.key));
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized java.util.ArrayList collList() {
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.Iterator it = this.collDone.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    l.add(new Object[] { e.getKey(), e.getValue() });
  }
  return l;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized void takeColl(String id, int n) {
  if (id == null || n <= 0) return;
  Integer cur = (Integer) this.collDone.get(id);
  if (cur == null) return;
  int v = cur.intValue() - n;
  if (v <= 0) this.collDone.remove(id); else this.collDone.put(id, Integer.valueOf(v));
}""", pben))
''')

# ---- describe: the charm on the status line, Eternal Flame needs no fuel, fuel time at the charm's rate
P.rep('''  if (!equipped) s0.append(" - accessory not equipped (queued items still finish)");
  if (this.needsFuel) s0.append(" - fuel ").append(dur(fuelTotalMs())).append(" (").append(total(this.fuel)).append(" items loaded)");
  else s0.append(" - needs no fuel");''', '''  if (this.cEternal) s0.append(" - Eternal Flame");
  else if (this.cTier > 0) s0.append(" - Furnace Charm T").append(this.cTier);
  if ((this.cEternal || this.cTier > 0) && this.cTime > 0) s0.append(" ").append(this.cTime).append(" percent faster");
  if (!equipped) s0.append(" - accessory not equipped (queued items still finish)");
  if (this.needsFuel && !this.cEternal) {{
    long fms = fuelTotalMs();
    if (this.cFuel > 0) fms = (fms * 100L) / (100L + (long) this.cFuel);
    s0.append(" - fuel ").append(dur(fms)).append(" (").append(total(this.fuel)).append(" items loaded");
    if (this.cFuel > 0) s0.append(" - burns ").append(this.cFuel).append(" percent faster");
    s0.append(")");
  }}
  else s0.append(" - needs no fuel");''')
P.rep('''    else if (this.needsFuel && this.fuelMs <= 0L && this.fuel.isEmpty()) state = "OUT OF FUEL - load fuel to continue";''',
      '''    else if (this.needsFuel && !this.cEternal && this.fuelMs <= 0L && this.fuel.isEmpty()) state = "OUT OF FUEL - load fuel to continue";''')

# ---- saved: <bench>.collDone (only when not empty)
P.rep('''  p.setProperty(b + "xpDone", ser(this.xpDone));
''', '''  p.setProperty(b + "xpDone", ser(this.xpDone));
  if (!this.collDone.isEmpty()) p.setProperty(b + "collDone", ser(this.collDone));
''')
P.rep('''  this.xpDone.clear(); parseInto(this.xpDone, p.getProperty(b + "xpDone"), 1);
''', '''  this.xpDone.clear(); parseInto(this.xpDone, p.getProperty(b + "xpDone"), 1);
  this.collDone.clear(); parseInto(this.collDone, p.getProperty(b + "collDone"), 1);
''')

# ---- ProcStore: every bench knows its profile key
P.rep('''        pb.fromProps(p);
''', '''        pb.fromProps(p);
        pb.key = k;
''')
P.rep('''  pb.clock = System.currentTimeMillis();
  Object prev = m.putIfAbsent(bench, pb);''', '''  pb.clock = System.currentTimeMillis();
  pb.key = k;
  Object prev = m.putIfAbsent(bench, pb);''')

# ---- 1. CraftPage: the alloy recipes, listed in the Furnace tab
P.rep('''# 0.7.3: tab ids are A:craft / A:smith / A:farm / P:<bench> / C: only''', '''# 0.8.20: every recipe whose bench requirement id is SkyyAlloy (B1's standalone Alloy_<Name> files) - the Furnace tab lists them (locked rows
# included; buildProc greys them, procQueue refuses them until the Furnace Charm tier is reached)
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet alloyRecipes() {{
  java.util.TreeSet ids = new java.util.TreeSet();
  try {{
    java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (o instanceof {CRR} && {PKG}.ProcBench.alloyNeed(({CRR}) o) > 0) ids.add((({CRR}) o).getId());
    }}
  }} catch (Throwable t) {{ }}
  return ids;
}}""", cpg))
# 0.7.3: tab ids are A:craft / A:smith / A:farm / P:<bench> / C: only''')
P.rep('''    ids.addAll(benchRecipes(u, tabId.substring(2)));
''', '''    ids.addAll(benchRecipes(u, tabId.substring(2)));
    if (tabId.equalsIgnoreCase("P:Furnace")) ids.addAll(alloyRecipes());   // 0.8.20
''')

# ---- 1. procQueue: the lock (checked on the click with a fresh smelt(k), nothing taken); the job keeps the BASE unit time (critic fix)
P.rep('''  {PKG}.ProcBench pb = {PKG}.ProcStore.of(k, bench);
  long now = System.currentTimeMillis();
  pb.advance(now);
''', '''  {PKG}.ProcBench pb = {PKG}.ProcStore.of(k, bench);
  long now = System.currentTimeMillis();
  pb.advance(now);
  int aneed = {PKG}.ProcBench.alloyNeed(r);   // 0.8.20
  if (aneed > 0 && !"Furnace".equalsIgnoreCase(bench)) return "alloys smelt in the Furnace only - nothing was taken";
  if (aneed > {PKG}.ProcBench.smelt(k)[0]) return "Furnace Charm T" + aneed + " unlocks this - equip it in your Void Charms (nothing was taken)";
''')
P.rep('''" unitMs=" + unit + " tier=" + tier + " fromBags=" + consumed + audit);''',
      '''" unitMs=" + unit + " tier=" + tier + " charm=" + pb.cTier + "/" + pb.cTime + "/" + pb.cFuel + (pb.cEternal ? "/eternal" : "") + " fromBags=" + consumed + audit);''')

# ---- 1. + 2. buildProc: greyed locked rows, the charm's time in "each"
P.rep('''  @PKG@.ProcBench view = pb != null ? pb : new @PKG@.ProcBench(bench);
''', '''  @PKG@.ProcBench view = pb != null ? pb : new @PKG@.ProcBench(bench);
  if (pb == null) { view.key = k; view.advance(System.currentTimeMillis()); }   // 0.8.20: the charm on the status line (an empty bench)
  int ctier = "Furnace".equalsIgnoreCase(bench) ? @PKG@.ProcBench.smelt(k)[0] : 0;   // critic fix: the lock from a fresh read
''')
P.rep('''  this.fuelPick = false;
  boolean only = Boolean.TRUE.equals(ONLY.get(u));
  java.util.ArrayList ent = new java.util.ArrayList();
  for (int i = 0; i < raw.size(); i++) {
    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (only && l0 <= 0) continue;
    @MQ@ o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
    ent.add(new Object[] { r0, Integer.valueOf(l0), Integer.valueOf(@PKG@.RecipeCmp.sortKey(id0)), @PKG@.RecipeCmp.sortName(id0) });   // 0.8.11: tier, then name''',
      '''  this.fuelPick = false;
  boolean only = Boolean.TRUE.equals(ONLY.get(u));
  java.util.ArrayList ent = new java.util.ArrayList();
  for (int i = 0; i < raw.size(); i++) {
    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (@PKG@.ProcBench.alloyNeed(r0) > ctier) l0 = 0;   // 0.8.20: a locked alloy is never "can make"
    if (only && l0 <= 0) continue;
    @MQ@ o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
    ent.add(new Object[] { r0, Integer.valueOf(l0), Integer.valueOf(@PKG@.RecipeCmp.sortKey(id0)), @PKG@.RecipeCmp.sortName(id0) });   // 0.8.11: tier, then name''')
P.rep('''    int lim = limit(r, mats);
    int allN = lim < room ? lim : room;
    drawRow(b, ev, i, r, mats, lim, "", allN, true, @PKG@.ProcBench.dur(@PKG@.ProcBench.unitMs(r, bench, tier)) + " each");''',
      '''    int lim = limit(r, mats);
    int aneed = @PKG@.ProcBench.alloyNeed(r);
    String lockNote = "";
    if (aneed > ctier) { lim = 0; lockNote = " - Furnace Charm T" + aneed + " unlocks this"; }   // 0.8.20: greyed, no buttons
    int allN = lim < room ? lim : room;
    drawRow(b, ev, i, r, mats, lim, lockNote, allN, true, @PKG@.ProcBench.dur(@PKG@.ProcBench.charmMs(@PKG@.ProcBench.unitMs(r, bench, tier), view.cTime)) + " each");''')

# ---- 3. ProcTask: pay the Charcoal ledger through coll:fn:add
P.rep('''ptk.addField(CtField.make("public static final int XP_CALL = 1000;", ptk))
''', '''ptk.addField(CtField.make("public static final int XP_CALL = 1000;", ptk))
# 0.8.20: Charcoal collection credit (coll:fn:add, source sacks:furnace): at most COLL_CALL per call; a refused key waits COLLNEXT (30 s)
ptk.addField(CtField.make("public static final int COLL_CALL = 256;", ptk))
ptk.addField(CtField.make("public static long COLLWARN;", ptk))
ptk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap COLLNEXT = new java.util.concurrent.ConcurrentHashMap();", ptk))
''')
P.rep('''      {PKG}.CraftLog.later(k, "SMITHING " + recipe + " x" + n + " -> " + ((Number) got).longValue() + " xp");
    }}
  }}
}}""", ptk))
''', '''      {PKG}.CraftLog.later(k, "SMITHING " + recipe + " x" + n + " -> " + ((Number) got).longValue() + " xp");
    }}
  }}
}}""", ptk))
# 0.8.20: one pass over the ledger with coll:fn:add `f` (no lock of ours held during the call); returns the count credited, -1 = refused /
# failed (the ledger is kept as it is)
ptk.addMethod(CtNewMethod.make(f"""
public static int drainColl0(Object f, java.util.UUID u, String k, {PKG}.ProcBench pb) {{
  if (!(f instanceof java.util.function.Function)) return -1;
  java.util.ArrayList l = pb.collList();
  int sent = 0;
  for (int i = 0; i < l.size(); i++) {{
    Object[] e = (Object[]) l.get(i);
    String id = (String) e[0];
    int n = ((Integer) e[1]).intValue();
    if (n <= 0) continue;
    if (n > COLL_CALL) n = COLL_CALL;
    Object got = null;
    try {{
      got = ((java.util.function.Function) f).apply(new Object[] {{ u, id, Long.valueOf((long) n), "sacks:furnace", k }});
    }} catch (Throwable t) {{
      long now = System.currentTimeMillis();
      if (now - COLLWARN > 60000L) {{ COLLWARN = now; {PKG}.SackPool.warn("charcoal collection: coll:fn:add failed (ledger kept, retried): " + t); }}
      return -1;
    }}
    if (!Boolean.TRUE.equals(got)) return -1;
    pb.takeColl(id, n);
    {PKG}.ProcStore.markDirty(k);
    {PKG}.CraftLog.later(k, "COLLECTION " + id + " x" + n + " credited (sacks:furnace)");
    sent += n;
  }}
  return sent;
}}""", ptk))
ptk.addMethod(CtNewMethod.make(f"""
public static void drainColl(java.util.UUID u, String k, {PKG}.ProcBench pb) {{
  if (pb.collDone.isEmpty()) return;
  long now = System.currentTimeMillis();
  Object nx = COLLNEXT.get(k);
  if (nx instanceof Long && now < ((Long) nx).longValue()) return;
  if (!k.equals({PKG}.SackPool.settledKey(u))) return;
  int r = drainColl0({PKG}.SackPool.bridge().get("coll:fn:add"), u, k, pb);
  if (r < 0) COLLNEXT.put(k, Long.valueOf(now + 30000L)); else COLLNEXT.remove(k);
}}""", ptk))
''')
P.rep('''      if (fo instanceof {PKG}.ProcBench) drainXp(u, k, ({PKG}.ProcBench) fo);''',
      '''      if (fo instanceof {PKG}.ProcBench) {{ drainXp(u, k, ({PKG}.ProcBench) fo); drainColl(u, k, ({PKG}.ProcBench) fo); }}''')

# ---- the 5 Enchanted rows of this round (tools/skyyench.py, B4: Enchanted Lead / Chromium / Slag / Titanium Ingot + Enchanted Charcoal) home by
# skyyench at build time like every row; the 0.8.14 row-count guard accepts them (and still 102 while skyyench lacks them)
P.rep('''assert len(EN.IDS) == 102 and "Skyy_Ench_LifeEssence" not in EN.IDS''',
      '''ORES_ENCH = ("Skyy_Ench_Lead", "Skyy_Ench_Chromium", "Skyy_Ench_Slag", "Skyy_Ench_Titanium", "Skyy_Ench_Charcoal")   # 0.8.20: round ores01 rows
assert len(EN.IDS) == 102 + len([_i for _i in ORES_ENCH if _i in EN.IDS]) and "Skyy_Ench_LifeEssence" not in EN.IDS''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.20 adds no system / command"
P.finish()
