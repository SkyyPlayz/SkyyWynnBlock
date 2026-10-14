"""Derive SkyyGear/build_skyygear_0.3.5.py from the LIVE 0.3.4 (build_skyygear_0.3.4.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_4_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_5_patch.py      then      python SkyyGear/build_skyygear_0.3.5.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.5.py

0.3.5 (2026-10-14) = VAULT SUMMON + HANDS COUNT AS CRUDE + THE IDENTIFY ANIMATION + THE LIFELONG FISHING POLE + REBIRTH R7. Skyy's words:
  2026-10-14 "Run everything you can in parallel. I want everything on your list done by 5 pm when i get off work."
  2026-10-14 popup ("an EMPTY HAND or a non-hoe item still harvests crops 2+ tiers up. Close that gap?") "Hands count as Crude (Recommended)"
  2026-10-13 LOST TOOL "if you can, make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"
  2026-10-11 LOST LOOT "we could maybe do an animation for the identifying."
  gear.md 2026-10-12 "the pole will level with you once you get it"; Rebirth-Spec D8-D10 / G6 "reset to crude level 1. all upgrade points are
  gone/ removed. BUT you get a REBIRTH modifier" + D9 gathering armor "reset to T1 on rebirth keeping rarity" + D7 / D8 Multitool after rebirth 1.
Built on the LIVE 0.3.4 (Sigils, armor levels, the till area and every older system are untouched apart from the hooks listed here).

1. VAULT SUMMON (SkyyVault 0.1.6 vault:fn:findLL / takeLL / doneLL / putBack, contract in tools/vault_0_1_6_patch.py): /pickaxe /hatchet /hoe
   /sickle /pole now bring your EXACT tool out of a CLOSED Vault. Order: inventory -> Requip -> an open window -> THE VAULT -> its loaded
   chest -> an exact copy. GearLife.fromVault, all in the same world-thread call: findLL ("p:s" = there; null = not there -> the old path;
   "!pending" = a take is still open -> "try again in a few seconds", NEVER a copy; "!unreadable" -> try again, never a copy) -> takeLL
   (refused "-why" -> "try again", never a copy) -> the stack goes into a free slot and is read back (uid) -> doneLL; could not be placed ->
   putBack ("+" back in the Vault / "=" Vault full: kept in the vault file, placed at the next start / "-" the Vault resolves it by itself).
   A doneLL that answers FALSE is logged (the tool IS in the inventory; the Vault's own 5 s auto-resolve closes the take).
   FIX ROUND 2: findLL THROWING = "the Vault could not be checked - try again" (critic A4: never the chest / copy path - only a real null is
   "not there"); a stack the slot TOOK but that did not read back is taken out of the slot again BEFORE putBack (critic A5: never one in the
   inventory + one back in the Vault); if it cannot be taken out it stays (doneLL, LL-VAULT-KEPT) and putBack is never called. Crash points
   10 (after the take), 11 (after the place), 12 (after doneLL) are in the harness: the Vault's saved pending record + its auto-resolve
   keep exactly one tool (SkyyVault's own proof), and gear never makes a copy while the Vault answers anything but null.
2. HANDS COUNT AS CRUDE ON CROPS (Skyy's popup answer): an empty hand or any item that is not a hoe / sickle counts as the lowest tier
   (a Crude hoe = tier 1, capped at the hoe family's top like a hoe): a crop one tier up = slow + half Farming XP (gear:fn:farmTier answers 1),
   two or more up = REFUSED - the left-click (GearToolHitSys, DamageBlockEvent) AND the F-harvest (GearChestOpenSys, UseBlockEvent$Pre) -
   with the same "Too tough" popup ("Too tough for your bare hands"). Ore / logs keep gate.bareHands (unchanged).
3. THE IDENTIFY ANIMATION: after a successful identify / re-identify (the Anvil and the Identify page, one item or Identify all) SkyyGear
   asks SkyyExploration 0.2.8's explore:fn:reveal (contract in tools/exploration_0_2_8_patch.py): one card per item "id|name|Lv N - Rarity|
   #hex|rank|cover id|cover name" (rank 0 plain, 1 Rare / Set, 2 Legendary / Fabled / Mythic / Untiered; the cover = the mystery bag or the
   unidentified item itself), at most 10 (Identify all: the best last; fewer shown = the rest stay in the page's own result line),
   back command: the Anvil /reforge, the Identify page /identify while identify.command is on (fix round); more than 10 = "Showing your 10
   best of N" and the Identify all result line also goes to chat (the reveal page replaces the page). Called AFTER the identify swap has finished (the item is in its slot); FALSE (no SkyyExploration, switched
   off, offline) = nothing else changes (the page's own result line stays as before).
4. THE LIFELONG FISHING POLE (research/Gathering-Shards-Spec.md 5.1 / 5.4): the 5th lifelong kind "pole" = SkyyFishing's rods
   (SkyyFishing_Rod_<Tier>; Crude = the Wooden rod SkyyFishing_Rod_Bamboo). /pole brings it back like /pickaxe (Requip, an open window,
   the Vault, its chest, an exact copy). It levels with Fishing (capped by its tier; Lv 1 until SkyySkills publishes a Fishing level - so no text promises it yet, fix round),
   can't be dropped / sold (the 0.3.0 rules), resets on a rebirth. It has NO perks yet (Steady Line / Fishing Fortune later) and is not on
   the Tools tab (the four-row page is unchanged). SkyyGear never draws a rod's tooltip (SkyyFishing owns it; GearData.put writes only the
   document on a rod). HOW YOU GET IT, ONCE: (a) Marlow's quest pole - SkyyFishing 0.1.5's maker asks gear:fn:pole (Object[] { UUID,
   ItemStack, String grant } -> ItemStack): the rod comes back stamped lifelong for the claim's profile with a uid made from profile key
   + grant (the same stack on every SkyyQuests retry); the registry is NOT written there (any thread) - the sweep adopts it when it
   arrives (LL-POLE-ADOPT). A profile that already has a pole gets a plain rod (LL-POLE-PLAIN). (b) no pole yet: hold MARLOW'S rod (one
   with his quest's grant - fishing:fn:grantOf - e.g. claimed before 0.3.5, upgraded or not) and type /lifelong (once). FIX ROUND 2 (critic
   C2): a crafted / bought plain rod is refused (Skyy gear.md "it just initially comes from a quest"). The migration never gives a pole
   (Skyy: "well do a quest at hub to get into fishing").
   SkyyFishing 0.1.5 keeps the pole's SkyyGear document through its bench upgrade (Wooden -> Copper -> Iron), so the bench is the pole's
   tier-up (the sweep records the new tier).
5. REBIRTH R7 (research/cloud/Rebirth-Spec.md 1, 4.2, 5, section 6 R7): SkyyGear is the participant rebirth:part:gear (GearRb), the same
   two-phase protocol as Skills / Coins / Bank (apply(Object[] { op, pkey, txid, Integer newN, rewards }) -> String, never throws, never
   calls another mod during an op): measure / prepare (a backup of lifelong/<pkey>.properties in Skyy_SkyyGear/rebirth-backup/<pkey>/<txid>/,
   the last 3 kept, + the STAGED file rebirth/<pkey>.rb-<txid>.properties; nothing live changes) / commit (ONE atomic write of the rebirth
   RECORD rebirth/<pkey>.record.properties with rb.lastTx = txid, rb.n, hist.<n>; a repeated commit = "done") / abort / status. The
   record is applied ON THE WORLD THREAD (the sweep - the registry is only ever changed there): every lifelong kind -> tier Crude, all
   Upgrade Points removed (<kind>.up.* gone), <kind>.rbTx = txid; then each lifelong tool is converted IN PLACE when the sweep sees it
   (inventory: at once; a chest / the Vault / Requip: when it comes back; an exact copy too): item id -> the Crude one, rarity + lines +
   reforge name kept, level = your (reset) skill level, document rbx = txid (idempotent, a crash before the engine saved the inventory
   converts it again). Gathering armor (the Mining pieces) BORN before the rebirth (document b0, new in this build; none = from before
   0.3.5) -> Copper (T1) the first time it is on you after it, rarity + lines kept, set field moved (fix round 2, critics C1 / A3: no 30 s
   window - a piece stashed in a chest / the Vault / Requip / with a friend, or identified later, resets too; a piece made after the rebirth
   keeps its tier; an OLD piece bought from someone after your rebirth resets as well - question). THE REBIRTH MODIFIER: rebirth:fn:node(UUID, "<Arm>.tool") + "<Arm>.tool2" (Mining /
   Foraging / Farming / Fishing; the two Void-Forged nodes) x lifelong.rebirthPct (5 %) per level on the tool's Power, Fortune and Wisdom (read live; 0 until the R8
   tree sells the node). MULTITOOL GATE: with SkyyRebirth loaded and the row multi.rebirthGate ON the /multitool merge needs rebirth n >= 1
   (rebirth:n:<uuid>). FIX ROUND 2 (critic B1): the row ships OFF - SkyyRebirth publishes no "rebirth.on" flag and keeps rebirth:fn:count
   (n = 0 for everyone) while switched off, so an ON default locked the plain-tool merge that works in 0.3.4; turn it on with rebirth.on. While SkyyRebirth's rebirth:fn:busy says the profile is inside a rebirth (or a committed record is not applied
   yet) perk buys, point resets and lifelong tier-ups wait. NOTE: SkyyRebirth 0.2 calls only skills / coins / bank - "gear" must be added
   to its PARTS by the SkyyRebirth round (not this file); until then nothing calls rebirth:part:gear.
ROWS (Server Setup -> Gear, both danger): lifelong.rebirthPct (5 %), multi.rebirthGate (OFF - fix round 2). Absent = the default; a fresh file gets a 0.3.5
block. No one-time update. SAVED DATA: registry keys pole.* (the 5th kind), <kind>.rbTx / .rbN, rb.applied, rb.n, garmor.rbTx /
rbCut (fix round 2: rbAt / rbDone of the first build are removed at the next apply); tool documents rbx / rb / lgr (Marlow's grant); every
NEW document b0 (its birth); new files rebirth/<pkey>.record.properties, rebirth/<pkey>.rb-<txid>.properties,
rebirth-backup/<pkey>/<txid>/.
ROLLBACK 0.3.5 -> 0.3.4 is safe for items: a lifelong pole becomes a plain rod with an unused document (0.3.4 has no pole kind), the new
keys / files are ignored, tools already reset by a rebirth stay Crude (nobody can rebirth while rebirth.on is off). The multitool gate goes.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.4.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.5.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.4"' in s and "GENERATED by tools/gear_0_3_4_patch.py" in s and "0.3.5" not in s[:400], "not the generated 0.3.4 script"
assert "GearRb" not in s and "fromVault" not in s and "rebirthPct" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.4":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.4" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.4 - build script (javassist via jpype). GENERATED by tools/gear_0_3_4_patch.py from the LIVE 0.3.3 (itself GENERATED by
tools/gear_0_3_3_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.4.py -> SkyyGear/SkyyGear-0.3.4.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.4.py
''', '''"""SkyyGear 0.3.5 - build script (javassist via jpype). GENERATED by tools/gear_0_3_5_patch.py from the LIVE 0.3.4 (itself GENERATED by
tools/gear_0_3_4_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.5.py -> SkyyGear/SkyyGear-0.3.5.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.5.py

0.3.5 = VAULT SUMMON + HANDS COUNT AS CRUDE + THE IDENTIFY ANIMATION + THE LIFELONG FISHING POLE + REBIRTH R7 (notes: tools/gear_0_3_5_patch.py):
/pickaxe & co. bring your exact tool out of a closed Vault (SkyyVault 0.1.6); an empty hand or a non-farming item counts as a Crude hoe
on crops (two tiers up refused, one up half XP); identifying flips cards on SkyyExploration's reveal page; the fishing pole is the 5th
lifelong tool (/pole, Marlow's quest pole, once); SkyyGear joins the rebirth as rebirth:part:gear (tools back to Crude, points removed,
Mining armor back to Copper, the rebirth tool modifier, multitools after rebirth 1).

--- 0.3.4 notes ---
''')
rep('VERSION = "0.3.4"\n', 'VERSION = "0.3.5"\n')

# ================================================================================================================ rows
after('''    ("hoe.areaElsewhere", "Area tilling outside islands", "lifelong", "bool", "false", "", "", "", "", "live,danger",
     "Off = the extra blocks are tilled only on island worlds where you may build.", "field:GearCfg.HOE_ELSE"),
''', '''    # 0.3.5 REBIRTH R7 (research/cloud/Rebirth-Spec.md D7 / D10): the rebirth tool modifier and the multitool gate
    ("lifelong.rebirthPct", "Rebirth tool bonus per node level", "lifelong", "int", "5", "0", "100", "", "%", "live,danger",
     "Each level of the rebirth tool node adds this % to a lifelong tool's Power, Fortune and Wisdom.", "field:GearCfg.LL_RBPCT"),
    ("multi.rebirthGate", "Multitools after rebirth 1", "tools", "bool", "false", "", "", "", "", "live,danger",
     "On = multitools open after your first rebirth. Switch on with rebirth.on. Off = always.", "field:GearCfg.MULTI_RBGATE"),
''')
rep('''           "part.sigils", "garmor.levels", "garmor.ladders", "hoe.areaElsewhere", "sigil.mythicUse"}''',
    '''           "part.sigils", "garmor.levels", "garmor.ladders", "hoe.areaElsewhere", "sigil.mythicUse",
           # 0.3.5: the rebirth tool modifier (gathering power = economy) + the multitool gate (Skyy's rebirth lock)
           "lifelong.rebirthPct", "multi.rebirthGate"}''')
after('''G34_HEAD = "# ---- sigils, gathering armor levels, the hoe till area (SkyyGear 0.3.4) ----"
G34_ROWK = ["part.sigils", "sigil.mythicUse", "garmor.levels", "garmor.ladders", "hoe.areaOn", "hoe.area", "hoe.areaElsewhere"]
assert all(32 <= ord(_c) < 127 for _c in G34_HEAD) and "=" not in G34_HEAD
''', '''G35_HEAD = "# ---- the fishing pole, rebirth (SkyyGear 0.3.5) ----"
G35_ROWK = ["lifelong.rebirthPct", "multi.rebirthGate"]
assert all(32 <= ord(_c) < 127 for _c in G35_HEAD) and "=" not in G35_HEAD
''')
rep('''    L += ["", G34_HEAD]         # 0.3.4: the new rows (no one-time update adds them; absent = the default)
    for k in G34_ROWK:
        scal(k)
''', '''    L += ["", G34_HEAD]         # 0.3.4: the new rows (no one-time update adds them; absent = the default)
    for k in G34_ROWK:
        scal(k)
    L += ["", G35_HEAD]         # 0.3.5: the new rows (no one-time update adds them; absent = the default)
    for k in G35_ROWK:
        scal(k)
''')
rep('''              ("HOE_ON", "boolean", "true"), ("HOE_AREA", "String", jstr(HOE_AREA_DEF)), ("HOE_ELSE", "boolean", "false")]''',
    '''              ("HOE_ON", "boolean", "true"), ("HOE_AREA", "String", jstr(HOE_AREA_DEF)), ("HOE_ELSE", "boolean", "false"),
              # 0.3.5 the rebirth tool modifier + the multitool gate
              ("LL_RBPCT", "int", "5"), ("MULTI_RBGATE", "boolean", "false")]''')
after('''  HOE_ELSE = pbool(p, "hoe.areaElsewhere", false);
''', '''  // 0.3.5 the rebirth tool modifier (% per level of the rebirth tree's tool node) + the multitool gate (rebirth n >= 1)
  LL_RBPCT = (int) plong(p, "lifelong.rebirthPct", 5L, 0L, 100L);
  MULTI_RBGATE = pbool(p, "multi.rebirthGate", false);          // fix round 2 (critic B1): OFF until rebirth is switched on
''')

# ================================================================================================================ the pole: build-time kinds
rep('''LL_KIND = ["pickaxe", "hatchet", "hoe", "sickle"]
LL_KNAME = ["Pickaxe", "Hatchet", "Hoe", "Sickle"]
LL_KFAM = [1, 3, 4, 5]                              # GearTool.fam: 1 pickaxe, 3 hatchet, 4 hoe, 5 sickle (2 = the shovel stays plain)
LL_KSKILL = ["Mining", "Foraging", "Farming", "Farming"]
LL_KCRUDE = ["Tool_%s_Crude" % _n for _n in LL_KNAME]
assert all(_i in AZ_ITEMS for _i in LL_KCRUDE)
''', '''LL_KIND = ["pickaxe", "hatchet", "hoe", "sickle"]
LL_KNAME = ["Pickaxe", "Hatchet", "Hoe", "Sickle"]
LL_KFAM = [1, 3, 4, 5]                              # GearTool.fam: 1 pickaxe, 3 hatchet, 4 hoe, 5 sickle (2 = the shovel stays plain)
LL_KSKILL = ["Mining", "Foraging", "Farming", "Farming"]
LL_KCRUDE = ["Tool_%s_Crude" % _n for _n in LL_KNAME]
assert all(_i in AZ_ITEMS for _i in LL_KCRUDE)
# 0.3.5 THE FISHING POLE = the 5th lifelong kind (research/Gathering-Shards-Spec.md 5.1 / 5.4): SkyyFishing's rods SkyyFishing_Rod_<Tier>
# (Wooden = SkyyFishing_Rod_Bamboo = Crude). Family 9 is no GearTool family (kOf answers POLE by the id prefix; a rod never hits with tool power)
LL_POLE = 4
LL_POLE_PRE = "SkyyFishing_Rod_"
LL_POLE_LAD = ",".join(LL_POLE_PRE + _t for _t in ("Bamboo", "Copper", "Iron"))          # the SkyyFishing bench's rod recipes (0.1.4)
LL_KIND.append("pole")
LL_KNAME.append("Fishing Pole")
LL_KFAM.append(9)
LL_KSKILL.append("Fishing")
LL_KCRUDE.append(LL_POLE_PRE + "Bamboo")
assert len(LL_KIND) == len(LL_KNAME) == len(LL_KFAM) == len(LL_KSKILL) == len(LL_KCRUDE) == 5 and 9 not in LL_KFAM[:4]
# 0.3.5 REBIRTH R7: the rebirth tree ARM whose tool nodes set a kind's rebirth modifier (Rebirth-Spec 2.3; SkyyRebirth 0.3 sells TWO per arm:
# "<Arm>.tool" Void-Forged ... and "<Arm>.tool2" Void-Forged ... II, max 5 each, "+{v} rebirth modifier levels") - both read live through
# rebirth:fn:node and added (0 until the R8 tree sells them). FIX (critic 2.1): 0.3.5's first build read only "<Arm>.tool"
LL_RBNODE = ["Mining", "Foraging", "Farming", "Farming", "Fishing"]
LL_RBSFX = [".tool", ".tool2"]
''')
rep('''LL_KLAD = []
for _n in LL_KNAME:
''', '''LL_KLAD = []
for _n in LL_KNAME[:4]:          # 0.3.5: the pole's ladder is the SkyyFishing bench's (added below)
''')
rep('''assert LL_KLAD[0].endswith("Tool_Pickaxe_Adamantite") and LL_KLAD[2].endswith("Tool_Hoe_Thorium") and LL_KLAD[3].endswith("Tool_Sickle_Iron")
''', '''assert LL_KLAD[0].endswith("Tool_Pickaxe_Adamantite") and LL_KLAD[2].endswith("Tool_Hoe_Thorium") and LL_KLAD[3].endswith("Tool_Sickle_Iron")
LL_KLAD.append(LL_POLE_LAD)          # 0.3.5
F(gll, "public static final int POLE = %d;" % LL_POLE)          # 0.3.5
F(gll, "public static final String[] RBNODE = %s;" % jarr(LL_RBNODE))          # 0.3.5: the arm
F(gll, "public static final String[] RBSFX = %s;" % jarr(LL_RBSFX))          # 0.3.5 fix: its tool nodes (I + II)
''')

# ================================================================================================================ GearData: a rod is no gear item
after('''M(gdt, "public static boolean isTool(String id) { return id != null && id.startsWith(\\"Tool_\\") && !skyyItem(id); }")
''', '''# 0.3.5: a SkyyFishing rod (the lifelong pole) - SkyyGear keeps only its document on it (SkyyFishing owns the rod's tooltip and quality)
M(gdt, "public static boolean pole(String id) { return id != null && id.startsWith(\\"SkyyFishing_Rod_\\"); }")
''')
rep('''public static @IS@ put(@IS@ s, @BD@ doc, java.util.UUID owner) {
  if (s == null || s.isEmpty() || doc == null) return s;
''', '''public static @IS@ put(@IS@ s, @BD@ doc, java.util.UUID owner) {
  if (s == null || s.isEmpty() || doc == null) return s;
  if (pole(s.getItemId())) return s.withMetadata(@PKG@.GearDefs.DOC_KEY, (@BV@) doc);          // 0.3.5: the pole = the document only
''')

# 0.3.5 fix round 2 (critics C1 / A3): every NEW document carries b0 = its birth (ms) - "at" moves with every reforge / level up / identify,
# b0 never does (clones keep it). The rebirth's armor reset asks it: a piece born before the rebirth goes back to Copper wherever it was
rep('''  d.append("at", new org.bson.BsonInt64(System.currentTimeMillis()));
  d.append("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kind)));
  return d;''', '''  d.append("at", new org.bson.BsonInt64(System.currentTimeMillis()));
  d.append("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kind)));
  d.append("b0", new org.bson.BsonInt64(System.currentTimeMillis()));          // 0.3.5 fix round 2: the birth (the rebirth armor reset)
  return d;''')

# ================================================================================================================ GearLL: kinds, hands, rebirth
rep('''M(gll, "public static int kOf(String id) { return id == null ? -1 : kOfFam(@PKG@.GearData.toolFam(id)); }")''',
    '''M(gll, "public static int kOf(String id) { return id == null ? -1 : (@PKG@.GearData.pole(id) ? POLE : kOfFam(@PKG@.GearData.toolFam(id))); }")          # 0.3.5: + the pole
M(gll, "public static boolean isPole(String id) { return @PKG@.GearData.pole(id); }")''')
# hands = Crude on crops (Skyy 2026-10-14 popup "Hands count as Crude (Recommended)")
rep('''  if (!fits) {
    if (c == 4 || !@PKG@.GearCfg.GATE_BARE) return new int[] { -1, c, m, -1, f, 0 };
    return new int[] { 2, c, m, -1, f, 0 };
  }''', '''  if (!fits) {
    // 0.3.5 (Skyy 2026-10-14 "Hands count as Crude"): an empty hand or any item that is no hoe / sickle counts as a Crude hoe on crops (tier 1,
    // capped by the hoe family's top like a hoe): one tier up = 1 (slow, half XP, no Fortune), two or more up = 2 (refused). [4] = the hoe family
    if (c == 4) {
      int hm = m > FAMMAX[4] ? FAMMAX[4] : m;
      int hd = hm - 1;
      return new int[] { hd <= 0 ? 0 : (hd <= 1 ? 1 : 2), c, m, 0, 4, hd < 0 ? 0 : hd };
    }
    if (!@PKG@.GearCfg.GATE_BARE) return new int[] { -1, c, m, -1, f, 0 };
    return new int[] { 2, c, m, -1, f, 0 };
  }''')
rep('''    int[] d = decide(s, bt);
    if (d[0] < 1) return 0;
    String tn = (s == null || s.isEmpty()) ? null : @PKG@.Gear.itemName(s.getItemId());''', '''    int[] d = decide(s, bt);
    if (d[0] < 1) return 0;
    String tn = (s == null || s.isEmpty()) ? "bare hands" : @PKG@.Gear.itemName(s.getItemId());          // 0.3.5: hands count as Crude on crops''')
rep('''public static boolean useNo(@PR@ pr, @IS@ s, @TBTY@ bt) {
  try {
    if (s == null || s.isEmpty() || !@PKG@.GearCfg.GATE_ON) return false;
    int[] cm = cat(bt);
    if (cm[0] != 4) return false;
    int[] d = decideC(s, cm[0], cm[1]);
    if (d[0] != 2) return false;
    N[0] = N[0] + 1L;
    if (pr != null) cropNo(pr, pr.getUuid(), s.getItemId(), @PKG@.Gear.itemName(s.getItemId()), d);
    return true;''', '''public static boolean useNo(@PR@ pr, @IS@ s, @TBTY@ bt) {
  try {
    if (!@PKG@.GearCfg.GATE_ON) return false;          // 0.3.5: an empty hand too (hands count as Crude on crops)
    int[] cm = cat(bt);
    if (cm[0] != 4) return false;
    int[] d = decideC(s, cm[0], cm[1]);
    if (d[0] != 2) return false;
    N[0] = N[0] + 1L;
    boolean hand = s == null || s.isEmpty();
    if (pr != null) cropNo(pr, pr.getUuid(), hand ? null : s.getItemId(), hand ? "bare hands" : @PKG@.Gear.itemName(s.getItemId()), d);
    return true;''')
# rebirth (read side) + the record cache; the modifier in perkFx
before('''# the scheduler-side read at join (GearRefreshTask's first hop): the world thread later finds the registry in memory
''', r'''# ---- 0.3.5 REBIRTH R7, read side (tools/gear_0_3_5_patch.py item 5). RBREC = profile key -> the rebirth RECORD (rebirth/<pkey>.record.properties:
# rb.lastTx / rb.n / rb.at / hist.<n>) or "none"; written only by the participant GearRb (its commit), applied on the world thread (GearLife)
F(gll, "public static final java.util.concurrent.ConcurrentHashMap RBREC = new java.util.concurrent.ConcurrentHashMap();")
# fix round 2 (critic B2): profile key -> Long ms of the last failed read (an unreadable record is read again at most every 30 s, like reg())
F(gll, "public static final java.util.concurrent.ConcurrentHashMap RBBAD = new java.util.concurrent.ConcurrentHashMap();")
M(gll, r"""
public static String safeKey(String pk) {
  return pk == null ? "" : pk.replace('/', '_').replace('\\', '_').replace(':', '_').replace('.', '_');
}""")
M(gll, r"""
public static java.nio.file.Path rbFile(String pk) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pk == null || pk.length() == 0) return null;
  return d.resolve("rebirth").resolve(safeKey(pk) + ".record.properties");
}""")
# the record of profile pk (null = none / unreadable - an unreadable record is never cached; fix round 2: read again at most every 30 s)
M(gll, r"""
public static java.util.Properties rbRec(String pk) {
  if (pk == null || pk.length() == 0) return null;
  Object o = RBREC.get(pk);
  if (o instanceof java.util.Properties) return (java.util.Properties) o;
  if ("none".equals(o)) return null;
  long now = System.currentTimeMillis();
  Object bad = RBBAD.get(pk);
  if (bad instanceof Long && now >= ((Long) bad).longValue() && now - ((Long) bad).longValue() < 30000L) return null;          // fix round 2 (critic B2)
  java.nio.file.Path f = rbFile(pk);
  if (f == null) return null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { RBREC.putIfAbsent(pk, "none"); RBBAD.remove(pk); return null; }
    java.util.Properties p = @PKG@.GearCfg.read(f);
    RBBAD.remove(pk);
    Object prev = RBREC.putIfAbsent(pk, p);
    if (prev instanceof java.util.Properties) return (java.util.Properties) prev;
    return p;
  } catch (Throwable t) {
    RBBAD.put(pk, Long.valueOf(now));
    @PKG@.Gear.warnOnce("rbrec:" + pk, "the rebirth record of " + pk + " could not be read (" + t + ") - read again in 30 s");
    return null;
  }
}""")
# a committed rebirth this registry has not applied yet
M(gll, r"""
public static boolean rbPending(String pk, java.util.Properties P) {
  java.util.Properties r = rbRec(pk);
  if (r == null || P == null) return false;
  String tx = r.getProperty("rb.lastTx");
  return tx != null && !tx.equals(P.getProperty("rb.applied"));
}""")
# SkyyRebirth's rebirth:fn:busy (the profile is inside a rebirth); no SkyyRebirth / any error = false
M(gll, r"""
public static boolean rbBusy(String pk) {
  java.util.function.Function f = @PKG@.Gear.fn("rebirth:fn:busy");
  if (f == null || pk == null) return false;
  try { return Boolean.TRUE.equals(f.apply(pk)); } catch (Throwable t) { return false; }
}""")
# perk buys, point resets and lifelong tier-ups wait while a rebirth runs or is not applied yet
M(gll, r"""
public static boolean rbWait(java.util.UUID u) {
  if (u == null) return false;
  String pk = @PKG@.Gear.pkey(u);
  if (rbBusy(pk)) return true;
  Object o = REG.get(pk);
  return o instanceof java.util.Properties && rbPending(pk, (java.util.Properties) o);
}""")
# THE REBIRTH MODIFIER (Skyy G6 "you get a REBIRTH modifier", D7 "upgraded in the mining rebirth tree"): the level of the kind's tree node
# (rebirth:fn:node, live) x lifelong.rebirthPct % on Power, Fortune and Wisdom; 1.0 = none
M(gll, r"""
public static int rbNode(java.util.UUID u, int k) {
  java.util.function.Function f = @PKG@.Gear.fn("rebirth:fn:node");
  if (f == null || u == null || k < 0 || k >= RBNODE.length) return 0;
  int lv = 0;
  for (int i = 0; i < RBSFX.length; i++) {          // fix (critic 2.1): "<Arm>.tool" + "<Arm>.tool2"
    try {
      Object r = f.apply(new Object[] { u, RBNODE[k] + RBSFX[i] });
      if (r instanceof Integer && ((Integer) r).intValue() > 0) lv = lv + ((Integer) r).intValue();
    } catch (Throwable t) { }
  }
  return lv;
}""")
M(gll, r"""
public static double rbMult(java.util.UUID u, int k) {
  int lv = rbNode(u, k);
  if (lv <= 0 || @PKG@.GearCfg.LL_RBPCT <= 0) return 1.0;
  return 1.0 + (double) lv * (double) @PKG@.GearCfg.LL_RBPCT / 100.0;
}""")
# THE MULTITOOL GATE (D7 / D8 "unlock the multi tool after the first rebirth"): null = may merge; with SkyyRebirth loaded the ACTIVE profile needs
# rebirth n >= 1 (rebirth:n:<uuid>; absent = still loading); no SkyyRebirth or multi.rebirthGate off (the default since fix round 2) = unchanged
M(gll, r"""
public static String rbGate(java.util.UUID u) {
  if (!@PKG@.GearCfg.MULTI_RBGATE || u == null || @PKG@.Gear.fn("rebirth:fn:count") == null) return null;
  Object n = @PKG@.Gear.bget("rebirth:n:" + u);
  if (!(n instanceof Integer)) return "Your rebirths are still loading - try again in a moment.";
  if (((Integer) n).intValue() >= 1) return null;
  return "Multitools come after your first rebirth.";
}""")
''')
rep('''public static double[] perkFx(java.util.UUID u, int f, @BD@ d) {
  if (!mine(u, d)) return new double[] { 1.0, 0.0, 0.0 };
  int k = kOfFam(f);
  if (k < 0) return new double[] { 1.0, 0.0, 0.0 };
  java.util.Properties P = reg(@PKG@.Gear.pkey(u));
  double pw = 1.0 + (double) perkOf(P, k, 0) * @PKG@.GearCfg.LL_PSPD / 100.0;
  double fo = (double) perkOf(P, k, 1) * @PKG@.GearCfg.LL_PFORT;
  double wi = (double) perkOf(P, k, 2) * @PKG@.GearCfg.LL_PWIS;
  return new double[] { pw, fo, wi };
}''', '''public static double[] perkFx(java.util.UUID u, int f, @BD@ d) {
  if (!mine(u, d)) return new double[] { 1.0, 0.0, 0.0 };
  int k = kOfFam(f);
  if (k < 0) return new double[] { 1.0, 0.0, 0.0 };
  java.util.Properties P = reg(@PKG@.Gear.pkey(u));
  double pw = 1.0 + (double) perkOf(P, k, 0) * @PKG@.GearCfg.LL_PSPD / 100.0;
  double fo = (double) perkOf(P, k, 1) * @PKG@.GearCfg.LL_PFORT;
  double wi = (double) perkOf(P, k, 2) * @PKG@.GearCfg.LL_PWIS;
  return new double[] { pw, fo, wi, rbMult(u, k) };          // 0.3.5: [3] = the rebirth modifier (x on the totals, GearTool.stats)
}''')
rep('''public static void prefetch(java.util.UUID u) {
  try { if (@PKG@.GearCfg.LL_ON && u != null) reg(@PKG@.Gear.pkey(u)); } catch (Throwable t) { }
}''', '''public static void prefetch(java.util.UUID u) {
  try { if (@PKG@.GearCfg.LL_ON && u != null) { reg(@PKG@.Gear.pkey(u)); rbRec(@PKG@.Gear.pkey(u)); } } catch (Throwable t) { }          // 0.3.5: + the rebirth record
}''')
rep('''  return "lifelong tools on (one pickaxe / hatchet / hoe / sickle per profile, level = skill level capped by tier, 1 Upgrade Point per level, crafting "''',
    '''  return "lifelong tools on (one pickaxe / hatchet / hoe / sickle per profile + the fishing pole from Marlow or /lifelong, level = skill level capped by tier, 1 Upgrade Point per level, crafting "''')
rep('''/pickaxe /hatchet /hoe /sickle fetch yours from Requip / an open window / its loaded chest, else an exact copy every " + @PKG@.GearCfg.LL_RECLAIM + " s); tool tier gate " + (@PKG@.GearCfg.GATE_ON ? "on (Crude counts as Copper, one tier up x" + @PKG@.Gear.fnum10(@PKG@.GearCfg.GATE_NEXT) + ", two up x" + @PKG@.Gear.fnum10(@PKG@.GearCfg.GATE_TWO) + ", three up refused, crops two up refused, bare hands "''',
    '''/pickaxe /hatchet /hoe /sickle /pole fetch yours from Requip / an open window / the Vault / its loaded chest, else an exact copy every " + @PKG@.GearCfg.LL_RECLAIM + " s; rebirth part " + (@PKG@.GearCfg.LL_RBPCT > 0 ? "+" + @PKG@.GearCfg.LL_RBPCT + " % per tool node level" : "no tool modifier") + ", multitools " + (@PKG@.GearCfg.MULTI_RBGATE ? "after rebirth 1" : "always") + "); tool tier gate " + (@PKG@.GearCfg.GATE_ON ? "on (Crude counts as Copper, one tier up x" + @PKG@.Gear.fnum10(@PKG@.GearCfg.GATE_NEXT) + ", two up x" + @PKG@.Gear.fnum10(@PKG@.GearCfg.GATE_TWO) + ", three up refused, crops two up refused, hands count as Crude on crops, bare hands "''')

# ================================================================================================================ GearTool.stats: the rebirth modifier
rep('''    if (px[2] > 0.0) { wi = wi + px[2]; if (wi > @PKG@.GearCfg.TOOL_WCAP) wi = @PKG@.GearCfg.TOOL_WCAP; }
  }''', '''    if (px[2] > 0.0) { wi = wi + px[2]; if (wi > @PKG@.GearCfg.TOOL_WCAP) wi = @PKG@.GearCfg.TOOL_WCAP; }
    if (px.length > 3 && px[3] > 1.0) {          // 0.3.5: the rebirth modifier (Power / Fortune / Wisdom x, the caps still hold)
      if (f <= 3) { pw = pw * px[3]; if (pw > 100.0) pw = 100.0; }
      fo = fo * px[3]; if (fo > @PKG@.GearCfg.TOOL_FCAP) fo = @PKG@.GearCfg.TOOL_FCAP; fo = (double) Math.round(fo * 10.0) / 10.0;
      wi = wi * px[3]; if (wi > @PKG@.GearCfg.TOOL_WCAP) wi = @PKG@.GearCfg.TOOL_WCAP;
    }
  }''')

# FIX (critic 2.2): GearTool.mstats (family 6) returned before the modifier - a lifelong Multitool (mine) takes the Mining node's modifier
# ("Void-Forged Pick: pickaxe and Multitool") on both sides, the same caps. A plain Multitool stays plain (as a plain pickaxe does)
rep('''    wm = a[2];
    wc = b[2];
  }
  return new double[] { 6.0,''', '''    wm = a[2];
    wc = b[2];
    double xm = @PKG@.GearLL.mine(u, d) ? @PKG@.GearLL.rbMult(u, 0) : 1.0;          // 0.3.5 fix: the rebirth modifier (lifelong only)
    if (xm > 1.0) {
      pm = pm * xm; if (pm > 100.0) pm = 100.0;
      pc = pc * xm; if (pc > 100.0) pc = 100.0;
      fm = fm * xm; if (fm > @PKG@.GearCfg.TOOL_FCAP) fm = @PKG@.GearCfg.TOOL_FCAP; fm = r1(fm);
      fc = fc * xm; if (fc > @PKG@.GearCfg.TOOL_FCAP) fc = @PKG@.GearCfg.TOOL_FCAP; fc = r1(fc);
      wm = wm * xm; if (wm > @PKG@.GearCfg.TOOL_WCAP) wm = @PKG@.GearCfg.TOOL_WCAP;
      wc = wc * xm; if (wc > @PKG@.GearCfg.TOOL_WCAP) wc = @PKG@.GearCfg.TOOL_WCAP;
    }
  }
  return new double[] { 6.0,''')

# ================================================================================================================ GearMerge / GearUp gates
# FIX (critic 3.1): the 0.3.0 text promised the lifelong merge "after your first rebirth" - it is not built yet (the Multitool merge of the
# lifelong pickaxe + hatchet = a later round; question). The rebirth gate stays for plain tools.
rep('''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return "Your lifelong " + w + " cannot be merged (multitools come after your first rebirth).";     // 0.3.0''',
    '''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return "Your lifelong " + w + " cannot be merged yet - merging lifelong tools into a multitool comes in a later update.";     // 0.3.0 (0.3.5 fix: the text)''')
rep('''public static Object[] check(@IS@ p, @IS@ h, java.util.UUID u) {
  String w = why(p, 1);
  if (w == null) w = why(h, 3);''', '''public static Object[] check(@IS@ p, @IS@ h, java.util.UUID u) {
  String w = @PKG@.GearLL.rbGate(u);          // 0.3.5 R7: multitools after rebirth 1 (with SkyyRebirth; multi.rebirthGate)
  if (w == null) w = why(p, 1);
  if (w == null) w = why(h, 3);''')
rep('''    if (!@PKG@.GearLL.mine(u, d)) return new Object[] { "Only your lifelong " + @PKG@.GearLL.KIND[lk] + " can be tiered up - this one is a plain tool.", to, null };
    String lw = @PKG@.GearLL.tierWhy(u, to);''', '''    if (!@PKG@.GearLL.mine(u, d)) return new Object[] { "Only your lifelong " + @PKG@.GearLL.KIND[lk] + " can be tiered up - this one is a plain tool.", to, null };
    if (@PKG@.GearLL.rbWait(u)) return new Object[] { "A rebirth is finishing on this profile - try again in a few seconds.", to, null };          // 0.3.5
    String lw = @PKG@.GearLL.tierWhy(u, to);''')

# ================================================================================================================ GearIdent: the reveal cards
before('''# ---- 0.2.11: bags + re-identify in the identify core (see the header).''', r'''# ---- 0.3.5 THE IDENTIFY ANIMATION (Skyy 2026-10-11 "we could maybe do an animation for the identifying."): SkyyExploration 0.2.8's
# explore:fn:reveal (tools/exploration_0_2_8_patch.py item 4): Object[] { UUID, title, subtitle, String[] cards, "identify" } -> Boolean. A card
# = "icon|name|sub|#rrggbb|rank|coverIcon|coverName" (rank 0 plain, 1 Rare / Set, 2 Legendary / Fabled / Mythic / Untiered), at most 10.
# Called only AFTER the identify swap has finished (the new item is in its slot); FALSE = nothing else changes (the page's own line stays)
F(gidn, "public static final long[] RV = new long[3];")          # 0.3.5: reveals asked, shown (TRUE), not shown (FALSE / none)
# fix (critic 3.4): the reveal's "< Back" - the Anvil (ReforgePage) = /reforge (it opens the Anvil), the Identify page = /identify only while
# identify.command is on (else no Back, only Close: /identify would answer "switched off")
M(gidn, r"""
public static String backFor(Object page) {
  if (page != null && page.getClass().getName().endsWith("ReforgePage")) return "reforge";
  return @PKG@.GearCfg.IDENTIFY_CMD ? "identify" : null;
}""")
# Identify all: the page's result line goes to chat when the reveal page replaced the page (fix critic 3.4)
M(gidn, r"""
public static void revTell(@PR@ pr, String info) {
  if (pr == null || info == null || info.length() < 2) return;
  try { pr.sendMessage(@MSG@.raw("[Identify] " + info.substring(1)).color(@PKG@.GearDefs.C_GOLD)); } catch (Throwable t) { }
}""")
M(gidn, r"""
public static int revRank(int r) {
  String id = r >= 0 && r < @PKG@.GearDefs.R_ID.length ? @PKG@.GearDefs.R_ID[r] : "normal";
  if ("legendary".equals(id) || "fabled".equals(id) || "mythic".equals(id) || "untiered".equals(id)) return 2;
  if ("rare".equals(id) || "set".equals(id)) return 1;
  return 0;
}""")
M(gidn, r"""
public static String revSafe(String t) {
  if (t == null) return "";
  return t.replace('|', '/').replace('\n', ' ').replace('\r', ' ');
}""")
# the face-down side: a mystery bag shows itself, an unidentified item "Unidentified <name>", a re-identified one its old name
M(gidn, r"""
public static String coverName(String id, boolean reid) {
  if (id == null) return "?";
  if (@PKG@.GearUnid.isBox(id) || reid) return @PKG@.Gear.itemName(id);
  return "Unidentified " + @PKG@.Gear.itemName(id);
}""")
M(gidn, r"""
public static String revCard(@IS@ got, @BD@ nd, String coverId, String coverName) {
  if (got == null || got.isEmpty() || nd == null) return null;
  String id = got.getItemId();
  int r = @PKG@.GearData.rarity(nd);
  String hex = r >= 0 && r < @PKG@.GearDefs.R_HEX.length ? @PKG@.GearDefs.R_HEX[r] : "#FFFFFF";
  String sub = "Lv " + @PKG@.GearLevel.level(id, nd) + " - " + (r >= 0 && r < @PKG@.GearDefs.R_NAME.length ? @PKG@.GearDefs.R_NAME[r] : "?");
  return revSafe(id) + "|" + revSafe(@PKG@.GearView.nameText(id, nd)) + "|" + revSafe(sub) + "|" + hex + "|" + revRank(r) + "|" + revSafe(coverId == null ? id : coverId) + "|" + revSafe(coverName);
}""")
# cards = Object[] { Integer rank, String card }: sorted rank ascending (the best flips LAST), at most the 10 best; TRUE = the page opens
M(gidn, r"""
public static boolean reveal(java.util.UUID u, java.util.ArrayList cards, String title, String sub, String back) {
  RV[0] = RV[0] + 1L;
  java.util.function.Function f = @PKG@.Gear.fn("explore:fn:reveal");
  if (u == null || cards == null || cards.isEmpty() || f == null) { RV[2] = RV[2] + 1L; return false; }
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < cards.size(); i++) {
    Object[] c = (Object[]) cards.get(i);
    int rk = ((Integer) c[0]).intValue();
    int at = l.size();
    while (at > 0 && ((Integer) ((Object[]) l.get(at - 1))[0]).intValue() > rk) at--;
    l.add(at, c);
  }
  if (l.size() > 10) sub = "Showing your 10 best of " + l.size() + " - click the cards to see what you got.";          // fix (critic 3.4)
  while (l.size() > 10) l.remove(0);
  String[] a = new String[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) ((Object[]) l.get(i))[1];
  Object r = null;
  try { r = f.apply(new Object[] { u, title, sub, a, back }); } catch (Throwable t) { r = null; @PKG@.Gear.warnOnce("reveal", "explore:fn:reveal failed (logged once): " + t); }
  boolean ok = Boolean.TRUE.equals(r);
  if (ok) RV[1] = RV[1] + 1L; else RV[2] = RV[2] + 1L;
  return ok;
}""")
# one identify / re-identify result (identify()'s / reroll()'s Object[]: [2] the new stack, [4] its document); coverId = the stack before
M(gidn, r"""
public static boolean revealOne(java.util.UUID u, Object[] res, String coverId, boolean reid, String back) {
  if (res == null || res.length < 5 || !(res[2] instanceof @IS@) || !(res[4] instanceof @BD@)) return false;
  String cd = revCard((@IS@) res[2], (@BD@) res[4], coverId, coverName(coverId, reid));
  if (cd == null) return false;
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(new Object[] { Integer.valueOf(revRank(@PKG@.GearData.rarity((@BD@) res[4]))), cd });
  return reveal(u, l, reid ? "Re-identified!" : "Identified!", "Click the card to see what you got.", back);
}""")
''')
rep('''M(gidn, r"""
public static Object[] allIn(@IC@[] bySec, java.util.ArrayList rs, java.util.UUID u, String who, java.util.ArrayList recent) {''',
    '''M(gidn, r"""
public static Object[] allInC(@IC@[] bySec, java.util.ArrayList rs, java.util.UUID u, String who, java.util.ArrayList recent, java.util.ArrayList cards) {''')
rep('''    done++;
    spent = spent + ((Long) res[5]).longValue();
    if (res.length > 6 && res[6] instanceof Object[]) work.add(res[6]);''', '''    done++;
    spent = spent + ((Long) res[5]).longValue();
    if (res.length > 6 && res[6] instanceof Object[]) work.add(res[6]);
    if (cards != null && res[2] instanceof @IS@ && res[4] instanceof @BD@) {          // 0.3.5: one reveal card per item
      String cd = revCard((@IS@) res[2], (@BD@) res[4], it.getItemId(), coverName(it.getItemId(), false));
      if (cd != null) cards.add(new Object[] { Integer.valueOf(revRank(@PKG@.GearData.rarity((@BD@) res[4]))), cd });
    }''')
after('''    if (recent != null) recent.add(name + ": " + (sum.length() > 0 ? sum : "no modifiers"));
  }
  return new Object[] { Integer.valueOf(done), Long.valueOf(spent), Integer.valueOf(skipped), firstSkip, stop };
}""")
''', '''M(gidn, r"""
public static Object[] allIn(@IC@[] bySec, java.util.ArrayList rs, java.util.UUID u, String who, java.util.ArrayList recent) {
  return allInC(bySec, rs, u, who, recent, null);
}""")
''')
# the pages (the Identify page + the Anvil): one item, re-identify, Identify all
rep('''  Object[] res = @PKG@.GearIdent.identify(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), false, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
  int code = ((Integer) res[0]).intValue();''', '''  String rvC = this.selId;          // 0.3.5: the reveal card's cover (the bag / the unidentified item)
  Object[] res = @PKG@.GearIdent.identify(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), false, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
  int code = ((Integer) res[0]).intValue();
  if (code == 1) @PKG@.GearIdent.revealOne(u, res, rvC, false, @PKG@.GearIdent.backFor(this));          // 0.3.5: the identify animation (SkyyExploration's reveal page)''', count=2)
rep('''  Object[] res = @PKG@.GearIdent.reroll(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername());
  int code = ((Integer) res[0]).intValue();''', '''  String rvC = this.selId;          // 0.3.5: the reveal card's cover (the item before)
  Object[] res = @PKG@.GearIdent.reroll(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername());
  int code = ((Integer) res[0]).intValue();
  if (code == 1) @PKG@.GearIdent.revealOne(u, res, rvC, true, @PKG@.GearIdent.backFor(this));          // 0.3.5''', count=2)
rep('''  Object[] r = @PKG@.GearIdent.allIn(by, rs, u, this.playerRef.getUsername(), this.recent);
  int done = ((Integer) r[0]).intValue();''', '''  java.util.ArrayList rvL = new java.util.ArrayList();          // 0.3.5: one reveal card per identified item
  Object[] r = @PKG@.GearIdent.allInC(by, rs, u, this.playerRef.getUsername(), this.recent, rvL);
  int done = ((Integer) r[0]).intValue();''')
rep('''  Object[] r = @PKG@.GearIdent.allIn(by, rs, u, this.playerRef.getUsername(), rec);
  int done = ((Integer) r[0]).intValue();''', '''  java.util.ArrayList rvL = new java.util.ArrayList();          // 0.3.5: one reveal card per identified item
  Object[] r = @PKG@.GearIdent.allInC(by, rs, u, this.playerRef.getUsername(), rec, rvL);
  int done = ((Integer) r[0]).intValue();''')

# fix (critic 3.4): the reveal AFTER the result line is known (both pages end alike): the cards open, the line goes to chat (the page is replaced)
rep('''  else this.info = "+Identified " + done + (done == 1 ? " item" : " items") + " for " + @PKG@.Gear.fmt(spent) + " coins.";
}""")''', '''  else this.info = "+Identified " + done + (done == 1 ? " item" : " items") + " for " + @PKG@.Gear.fmt(spent) + " coins.";
  if (done > 0 && @PKG@.GearIdent.reveal(u, rvL, "Identified " + done + (done == 1 ? " item!" : " items!"), "Click the cards to see what you got.", @PKG@.GearIdent.backFor(this))) @PKG@.GearIdent.revTell(this.playerRef, this.info);          // 0.3.5
}""")''', count=2)

# ================================================================================================================ GearLife (write side)
rep('''LL_CMDS = [("PickaxeCmd", "pickaxe", 0), ("HatchetCmd", "hatchet", 1), ("HoeCmd", "hoe", 2), ("SickleCmd", "sickle", 3)]''',
    '''LL_CMDS = [("PickaxeCmd", "pickaxe", 0), ("HatchetCmd", "hatchet", 1), ("HoeCmd", "hoe", 2), ("SickleCmd", "sickle", 3),
           ("PoleCmd", "pole", 4)]          # 0.3.5: the fishing pole''')
rep('''gtrk = mk("GearTrackTask")          # 0.3.2: where a lifelong tool went (one world task after an inventory change in an open window)
LIFE_CLASSES += [glf, lpg] + llcmds + [tpc, llc, gdrop, gllfn, gtrk]''', '''gtrk = mk("GearTrackTask")          # 0.3.2: where a lifelong tool went (one world task after an inventory change in an open window)
grb = mk("GearRb")                  # 0.3.5: the rebirth participant rebirth:part:gear (research/cloud/Rebirth-Spec.md 5)
LIFE_CLASSES += [glf, lpg] + llcmds + [tpc, llc, gdrop, gllfn, gtrk, grb]''')
rep('''# 0.3.2: 14 fetched from Requip, 15 fetched from an open window, 16 fetched from its chest, 17 exact copies
F(glf, "public static final long[] N = new long[18];")''', '''# 0.3.2: 14 fetched from Requip, 15 fetched from an open window, 16 fetched from its chest, 17 exact copies
# 0.3.5: 18 fetched from the Vault, 19 Vault waits / refusals, 20 tools reset by a rebirth, 21 armor pieces reset by a rebirth, 22 rebirths
# applied, 23 poles stamped (Marlow), 24 poles adopted, 25 Marlow poles left plain (the profile had one)
F(glf, "public static final long[] N = new long[26];")''')
rep('''public static void recover(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  for (int k = 0; k < 4; k++) {''', '''public static void recover(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) {          // 0.3.5: + the pole''')
rep('''  boolean[] has = new boolean[4];
  java.util.ArrayList l = @PKG@.GearSmith.rqList(u, "items");''', '''  boolean[] has = new boolean[@PKG@.GearLL.KIND.length];          // 0.3.5: kOf may answer the pole (only the four are named below)
  java.util.ArrayList l = @PKG@.GearSmith.rqList(u, "items");''')
rep('''M(glf, r"""
public static @BD@ llDoc(@BD@ d0, String id, java.util.UUID u, String pk, String lu, boolean rp) {
  @BD@ nd = d0 == null ? @PKG@.GearData.base(@PKG@.GearData.kindFor(id), 0, true, "lifelong") : d0.clone();''',
    '''M(glf, r"""
public static @BD@ llDoc(@BD@ d0, String id, java.util.UUID u, String pk, String lu, boolean rp) {
  @BD@ nd = d0 == null ? @PKG@.GearData.base(@PKG@.GearLL.isPole(id) ? "tool" : @PKG@.GearData.kindFor(id), 0, true, "lifelong") : d0.clone();          // 0.3.5: a pole = kind tool''')
# the rebirth + pole helpers of the sweep (before pass: methods before callers)
before('''# one look over the inventory: level sync, the registry's item id, returned originals, stale copies, others' stale replacements
M(glf, r"""
public static void pass(''', r'''# ---- 0.3.5 THE POLE: Marlow's quest pole arrives stamped (gear:fn:pole); the first look that finds it while the profile has no pole makes it the
# lifelong one (ONE registry write) - the registry is never written by the bridge call (any thread)
M(glf, r"""
public static boolean adoptPole(@PR@ pr, String pk, java.util.Properties P, String lu, String id) {
  String K = @PKG@.GearLL.KIND[@PKG@.GearLL.POLE];
  if (!commit(pk, P, @PKG@.GearLL.POLE, lu, id, false, null, null, true)) {
    P.remove(K + ".uid");
    P.remove(K + ".id");
    P.remove(K + ".rp");
    return false;
  }
  N[24] = N[24] + 1L;
  @PKG@.GearLog.line("LL-POLE-ADOPT " + pr.getUuid() + " " + pk + " " + lu + " " + id);
  tellOnce(pr, "pole", "This fishing pole is your lifelong pole now - it can't be dropped, and /pole brings it back if you lose it.", 5000L);
  return true;
}""")
# ---- 0.3.5 REBIRTH R7, write side (world thread). rbApply: the committed record -> the registry (every kind: tier Crude, Upgrade Points removed,
# <kind>.rbTx = the rebirth; the armor step opens) in ONE registry write; a failed write changes nothing (the next look tries again)
M(glf, r"""
public static boolean rbApply(@PR@ pr, String pk, java.util.Properties P) {
  java.util.Properties R = @PKG@.GearLL.rbRec(pk);
  if (R == null) return false;
  String tx = R.getProperty("rb.lastTx");
  if (tx == null || tx.equals(P.getProperty("rb.applied"))) return false;
  String n = String.valueOf(@PKG@.GearLL.getl(R, "rb.n", 0L));
  java.util.Properties old = (java.util.Properties) P.clone();
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) {
    String K = @PKG@.GearLL.KIND[k];
    int sp = @PKG@.GearLL.spent(P, k);
    for (int p = 0; p < @PKG@.GearLL.PK.length; p++) P.remove(K + ".up." + @PKG@.GearLL.PK[p]);
    if (P.getProperty(K + ".uid") == null) continue;
    P.setProperty(K + ".rbTx", tx);
    P.setProperty(K + ".rbN", n);
    String cr = @PKG@.GearLL.KCRUDE[k];
    if (@PKG@.Gear.item(cr) != null) P.setProperty(K + ".id", cr);
    sb.append(' ').append(K).append(" (").append(sp).append(" points)");
  }
  P.setProperty("garmor.rbTx", tx);
  P.setProperty("garmor.rbCut", String.valueOf(@PKG@.GearLL.getl(R, "rb.at", System.currentTimeMillis())));          // fix round 2: pieces born before it reset
  P.remove("garmor.rbAt");          // (the 30 s window of the first 0.3.5 build - gone)
  P.remove("garmor.rbDone");
  P.setProperty("rb.applied", tx);
  P.setProperty("rb.n", n);
  if (!@PKG@.GearLL.save(pk, P)) {
    P.clear();
    P.putAll(old);
    return false;
  }
  N[22] = N[22] + 1L;
  java.util.UUID u = pr.getUuid();
  @PKG@.GearTool.LAST.remove(u);
  @PKG@.GearGate.bump(u);
  @PKG@.GearLog.line("LL-REBIRTH-APPLY " + u + " " + pk + " " + tx + " rebirth " + n + ":" + sb);
  tellOnce(pr, "rebirth" + tx, "Rebirth: your lifelong tools go back to Crude and Lv 1 and their Upgrade Points are gone - their rarity and rolls stay. Your Mining armor goes back to Copper.", 5000L);
  return true;
}""")
# fix (critic 3.2): the pole lost its whole tooltip in rbTool (the old tier's look is dropped) - SkyyFishing 0.1.5 redraws it (fishing:fn:restamp,
# ItemStack -> ItemStack: its rig lines + the lifelong line); kept only when the answer is the same rod with our rbx. No SkyyFishing = as before
M(glf, r"""
public static @IS@ poleLook(@IS@ ns, String to, String tx) {
  java.util.function.Function f = @PKG@.Gear.fn("fishing:fn:restamp");
  if (f == null || ns == null) return ns;
  try {
    Object r = f.apply(ns);
    if (r instanceof @IS@) {
      @IS@ s2 = (@IS@) r;
      @BD@ d2 = docOf(s2);
      if (to.equals(s2.getItemId()) && s2.getQuantity() == 1 && d2 != null && tx.equals(@PKG@.GearData.str(d2, "rbx", ""))) return s2;
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("polelook", "fishing:fn:restamp failed - the pole shows its plain name (logged once): " + t); }
  return ns;
}""")
M(glf, r"""
public static boolean rbNeed(java.util.Properties P, String K, @BD@ d) {
  String t = P.getProperty(K + ".rbTx");
  return t != null && d != null && !t.equals(@PKG@.GearData.str(d, "rbx", ""));
}""")
# one lifelong stack -> its Crude item IN PLACE (rarity, lines, reforge name kept; level = the skill rule; rbx = the rebirth). Read back; a crash
# before the engine saved the inventory leaves the old stack, which the next look converts again (rbx). The pole keeps SkyyFishing's rig data.
M(glf, r"""
public static boolean rbTool(@PR@ pr, @IC@ c, int i, @IS@ x, @BD@ d, int k, String pk, java.util.Properties P) {
  java.util.UUID u = pr.getUuid();
  String K = @PKG@.GearLL.KIND[k];
  String tx = P.getProperty(K + ".rbTx");
  String id = x.getItemId();
  String to = @PKG@.GearLL.KCRUDE[k];
  if (@PKG@.Gear.item(to) == null) to = id;          // the Crude item is not on this server (the pole without SkyyFishing): only the stamp
  @BD@ nd = d.clone();
  nd.put("rbx", new org.bson.BsonString(tx));
  nd.put("rb", new org.bson.BsonInt32((int) @PKG@.GearLL.getl(P, K + ".rbN", 0L)));
  nd.remove("lvU");
  if (!to.equals(id) && !@PKG@.GearLL.isPole(to)) {
    String kd = @PKG@.GearData.kindFor(to);
    nd.put("kind", new org.bson.BsonString(kd));
    if (nd.containsKey("gate")) nd.put("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kd)));
  }
  int lv = @PKG@.GearLL.levelFor(u, to);
  if (lv >= 1) nd.put("lvl", new org.bson.BsonInt32(lv));
  @IS@ base = x;
  if (!to.equals(id)) {
    if (@PKG@.GearLL.isPole(to)) {
      @BD@ md = x.getMetadata();
      @BD@ cm = md == null ? null : (@BD@) md.clone();
      if (cm != null) cm.remove(@IDM@.KEY);
      base = cm == null || cm.isEmpty() ? new @IS@(to, 1) : new @IS@(to, 1).withMetadata(cm);
    } else base = @PKG@.GearData.carry(new @IS@(to, 1), x);
  }
  @IS@ ns = @PKG@.GearData.put(base, nd, u);
  if (!to.equals(id) && @PKG@.GearLL.isPole(to)) ns = poleLook(ns, to, tx);          // fix (critic 3.2): SkyyFishing redraws the pole's tooltip
  @PKG@.GearLog.line("LL-REBIRTH-TOOL-BEGIN " + u + " " + pk + " " + K + " " + @PKG@.GearLL.uid(d) + " " + id + " -> " + to + " undo: " + @PKG@.GearMerge.json(x));
  crash(13);
  Object t2 = null;
  try { t2 = c.setItemStackForSlot((short) i, ns); } catch (Throwable t) { t2 = null; @PKG@.Gear.warn("rebirth: a lifelong tool could not be reset: " + t); }
  @IS@ back = c.getItemStack((short) i);
  @BD@ bd = docOf(back);
  boolean ok = t2 != null && !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) && back != null && to.equals(back.getItemId()) && bd != null && tx.equals(@PKG@.GearData.str(bd, "rbx", ""));
  if (!ok) return false;
  @PKG@.GearStamp.selfNote(u, t2);
  N[20] = N[20] + 1L;
  @PKG@.GearLog.line("LL-REBIRTH-TOOL " + u + " " + pk + " " + K + " " + @PKG@.GearLL.uid(d) + " " + id + " -> " + to + " lv" + lv + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(nd)]);
  return true;
}""")
# the Copper (T1) piece of a Mining armor piece's slot; null = none / not a piece
M(glf, r"""
public static String rbArmorTo(String id) {
  if (id == null || !id.startsWith("Armor_") || !@PKG@.GearMine.isPiece(id)) return null;
  String to = "Armor_Copper_" + id.substring(id.lastIndexOf('_') + 1);
  return @PKG@.GearMine.isPiece(to) && @PKG@.Gear.item(to) != null ? to : null;
}""")
# GATHERING ARMOR back to T1 (Rebirth-Spec D9 / gear.md "reset to T1 on rebirth keeping rarity"): every identified Mining piece ON the player
# (all six sections, armor included) that was BORN before the latest rebirth (document b0 < garmor.rbCut; no b0 = from before 0.3.5) and is
# not converted for it yet (rbx) -> Copper, rarity + lines kept, set field moved, level = the skill rule, rbx = the rebirth. FIX ROUND 2
# (critics C1 / A3): no 30 s window any more - a piece kept in a chest / the Vault / Requip / with a friend during the rebirth, or identified
# later, resets the first time it is on you; a piece made after the rebirth keeps its tier
M(glf, r"""
public static int rbArmor(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  String tx = P.getProperty("garmor.rbTx");
  if (tx == null || inv == null) return 0;
  long cut = @PKG@.GearLL.getl(P, "garmor.rbCut", 0L);
  java.util.UUID u = pr.getUuid();
  int n = 0;
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty() || x.getQuantity() != 1) continue;
      String id = x.getItemId();
      String to = rbArmorTo(id);
      if (to == null || to.equals(id)) continue;
      @BD@ d = docOf(x);
      if (d == null || !@PKG@.GearData.identified(d) || tx.equals(@PKG@.GearData.str(d, "rbx", ""))) continue;
      long b0 = @PKG@.GearData.lnum(d, "b0", 0L);
      if (b0 > 0L && (cut <= 0L || b0 >= cut)) continue;          // fix round 2: born after the rebirth = keeps its tier
      @BD@ nd = d.clone();
      nd.put("rbx", new org.bson.BsonString(tx));
      nd.remove("lvU");
      String os = @PKG@.GearSet.of(nd);
      String ns2 = @PKG@.GearMine.setFor(to);
      if (os != null && ns2 != null && @PKG@.GearUtFx.gathering(os)) nd.put("set", new org.bson.BsonString(ns2));
      int al = @PKG@.GearArmLv.levelFor(u, to);
      if (al >= 1) nd.put("lvl", new org.bson.BsonInt32(al));
      @IS@ ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(to, 1), x), nd, u);
      @PKG@.GearLog.line("LL-REBIRTH-ARMOR-BEGIN " + u + " " + pk + " " + id + " -> " + to + " undo: " + @PKG@.GearMerge.json(x));
      Object t2 = null;
      try { t2 = c.setItemStackForSlot((short) i, ns); } catch (Throwable t) { t2 = null; }
      @IS@ back = c.getItemStack((short) i);
      if (t2 == null || (t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) || back == null || !to.equals(back.getItemId())) continue;
      @PKG@.GearStamp.selfNote(u, t2);
      N[21] = N[21] + 1L;
      n++;
      @PKG@.GearLog.line("LL-REBIRTH-ARMOR " + u + " " + pk + " " + id + " -> " + to + " lv" + al);
    }
  }
  return n;
}""")
''')
rep('''        String cur = P.getProperty(K + ".uid");
        if (lu.equals(cur)) {
          if (!one.add(lu)) { remove(c, i, x, u, "a second stack of your lifelong " + K + " (" + lu + ") - only one exists"); continue; }
          here = here | (1 << k);''', '''        String cur = P.getProperty(K + ".uid");
        if (lu.equals(cur)) {
          if (!one.add(lu)) { remove(c, i, x, u, "a second stack of your lifelong " + K + " (" + lu + ") - only one exists"); continue; }
          // 0.3.5 REBIRTH R7: the current tool of a rebirthed profile goes back to Crude here (once per rebirth: rbx)
          if (rbNeed(P, K, d) && rbTool(pr, c, i, x, d, k, pk, P)) {
            x = c.getItemStack((short) i);
            d = docOf(x);
            if (x == null || x.isEmpty() || d == null) continue;
            id = x.getItemId();
          }
          here = here | (1 << k);''')
rep('''        if (lu.equals(P.getProperty(K + ".pend"))) continue;
        if (@PKG@.GearLL.isRt(d)) continue;          // fix round 2: a retired one stays as it is until /lifelong swaps it back''',
    '''        if (lu.equals(P.getProperty(K + ".pend"))) continue;
        if (cur == null && k == @PKG@.GearLL.POLE && !@PKG@.GearLL.isRt(d)) { if (adoptPole(pr, pk, P, lu, id)) again = true; continue; }          // 0.3.5: Marlow's pole
        if (@PKG@.GearLL.isRt(d)) continue;          // fix round 2: a retired one stays as it is until /lifelong swaps it back''')
rep('''  recover(pr, inv, pk, P);
  boolean mg = false;
  if (!"1".equals(P.getProperty("migrated"))) mg = migrate(pr, inv, pk, P);
  pass(pr, inv, pk, P, mg);          // fix round: one save carries the migration's deferred commits + migrated=1
  N[0] = N[0] + 1L;''', '''  recover(pr, inv, pk, P);
  rbApply(pr, pk, P);          // 0.3.5 REBIRTH R7: a committed rebirth record -> the registry (once)
  boolean mg = false;
  if (!"1".equals(P.getProperty("migrated"))) mg = migrate(pr, inv, pk, P);
  pass(pr, inv, pk, P, mg);          // fix round: one save carries the migration's deferred commits + migrated=1
  rbArmor(pr, inv, pk, P);          // 0.3.5 REBIRTH R7: Mining armor born before the rebirth -> Copper when it is on you (fix round 2: no window)
  N[0] = N[0] + 1L;''')
rep('''  for (int k = 0; k < 4; k++) {
    if ((mask & (1 << k)) == 0) continue;
    String K = @PKG@.GearLL.KIND[k];
    String cur = P.getProperty(K + ".uid");
    if (cur == null || have.contains(cur)) continue;''', '''  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) {          // 0.3.5: + the pole
    if ((mask & (1 << k)) == 0) continue;
    String K = @PKG@.GearLL.KIND[k];
    String cur = P.getProperty(K + ".uid");
    if (cur == null || have.contains(cur)) continue;''')
# THE VAULT (closed) - before reclaimW
before('''# /pickaxe /hatchet /hoe /sickle (world thread; w = the command's world, null = no chest lookup): "+" done, "-" refused (why).''', r'''# ---- 0.3.5 VAULT SUMMON (Skyy 2026-10-13 LOST TOOL; SkyyVault 0.1.6, contract in tools/vault_0_1_6_patch.py). The tool in a CLOSED Vault comes
# back EXACTLY, all in this one world-thread call: findLL -> takeLL -> place + read back -> doneLL (or putBack). null = not in the Vault / no
# SkyyVault 0.1.6 (the old path goes on); "-..." = it IS in the Vault but not now / the Vault could not be asked (never an exact copy then); "+..." = fetched
F(glf, "public static volatile boolean TEST_NOREAD = false;")          # fix round 2, harness only: the read-back after the Vault place fails
M(glf, "public static String vaultAt(String at) { int c = at == null ? -1 : at.indexOf(':'); return c > 0 ? \"page \" + at.substring(0, c) + \", slot \" + at.substring(c + 1) : \"your Vault\"; }")
M(glf, r"""
public static String fromVault(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String cur) {
  java.util.function.Function ff = @PKG@.Gear.fn("vault:fn:findLL");
  if (ff == null) return null;
  java.util.UUID u = pr.getUuid();
  String K = @PKG@.GearLL.KIND[k];
  Object fr = null;
  try { fr = ff.apply(new Object[] { u, pk, cur }); }
  catch (Throwable t) {          // fix round 2 (critic A4): only a real null means "not in the Vault" - an error never leads to an exact copy
    N[19] = N[19] + 1L;
    @PKG@.Gear.warnOnce("vaultfind", "vault:fn:findLL failed (logged once; /" + K + " answers 'try again', never a copy): " + t);
    return "-The Vault could not be checked right now - type /" + K + " again in a moment.";
  }
  if (!(fr instanceof String)) return null;
  String at = (String) fr;
  if ("!pending".equals(at)) { N[19] = N[19] + 1L; return "-Your " + K + " is on its way between your Vault and your inventory - type /" + K + " again in a few seconds."; }
  if (at.startsWith("!")) { N[19] = N[19] + 1L; return "-Your " + K + " is in your Vault, but the Vault cannot be read right now - try again in a moment."; }
  java.util.function.Function ft = @PKG@.Gear.fn("vault:fn:takeLL");
  java.util.function.Function fd = @PKG@.Gear.fn("vault:fn:doneLL");
  java.util.function.Function fb = @PKG@.Gear.fn("vault:fn:putBack");
  if (ft == null || fd == null || fb == null) return "-Your " + K + " is in your Vault (" + vaultAt(at) + ") - open /vault and take it out.";
  if (@PKG@.Gear.busy(u) || !pk.equals(@PKG@.Gear.pkey(u))) return "-Your profile is changing - try again in a moment.";
  Object[] fe = @PKG@.GearStamp.firstEmpty(new @IC@[] { inv.getStorage(), inv.getBackpack(), inv.getHotbar() }, null, -1);
  if (fe == null) return "-No room - free one inventory slot and try again.";
  @IC@ dc = (@IC@) fe[0];
  int ds = ((Integer) fe[1]).intValue();
  @PKG@.GearLog.line("LL-SUMMON-BEGIN " + u + " " + pk + " " + K + " " + cur + " from the Vault " + at);
  Object tr = null;
  try { tr = ft.apply(new Object[] { u, pk, cur }); } catch (Throwable t) { tr = "-" + t; }
  if (!(tr instanceof Object[])) {
    String why = tr instanceof String ? (String) tr : "no answer";
    if (why.startsWith("-")) why = why.substring(1);
    N[19] = N[19] + 1L;
    @PKG@.GearLog.line("LL-VAULT-REFUSED " + u + " " + pk + " " + K + " " + cur + " (" + why + ")");
    return "-Your " + K + " is in your Vault (" + vaultAt(at) + ") but could not come out right now (" + why + ") - try again.";
  }
  Object[] ta = (Object[]) tr;
  String tok = ta.length > 0 && ta[0] instanceof String ? (String) ta[0] : null;
  @IS@ x = ta.length > 1 && ta[1] instanceof @IS@ ? (@IS@) ta[1] : null;
  crash(10);
  @BD@ d = docOf(x);
  boolean ours = tok != null && x != null && !x.isEmpty() && x.getQuantity() == 1 && @PKG@.GearLL.isLL(d) && cur.equals(@PKG@.GearLL.uid(d)) && pk.equals(@PKG@.GearLL.owner(d));
  boolean ok = false;
  boolean placed = false;
  if (ours) {
    try {
      Object t2 = dc.setItemStackForSlot((short) ds, x);
      ok = !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded());
      placed = ok;
      if (ok) @PKG@.GearStamp.selfNote(u, t2);
    } catch (Throwable t) { ok = false; @PKG@.Gear.warn("lifelong: a tool from the Vault could not be put into the inventory: " + t); }
    if (ok) {
      @BD@ nd = TEST_NOREAD ? null : docOf(dc.getItemStack((short) ds));
      ok = nd != null && cur.equals(@PKG@.GearLL.uid(nd));
    }
  }
  crash(11);
  if (!ok && placed) {          // fix round 2 (critic A5): the slot took it but it did not read back - take it out again BEFORE putBack (never two)
    boolean gone = false;
    try {
      Object rt = dc.removeItemStackFromSlot((short) ds);
      if (!(rt instanceof @TXN@ && !((@TXN@) rt).succeeded())) @PKG@.GearStamp.selfNote(u, rt);
      @IS@ left = dc.getItemStack((short) ds);
      gone = left == null || left.isEmpty();
    } catch (Throwable t) { gone = false; }
    if (!gone) {          // it stays in the inventory: the take is closed (doneLL), the sweep keeps one stack - never putBack then
      Object dk = null;
      try { dk = fd.apply(new Object[] { u, tok }); } catch (Throwable t) { dk = null; }
      @PKG@.Gear.warn("lifelong: " + K + " " + cur + " came out of the Vault but did not read back and could not be taken out of the slot - it stays in the inventory (doneLL " + dk + ")");
      @PKG@.GearLog.line("LL-VAULT-KEPT " + u + " " + pk + " " + K + " " + cur + " token " + tok + " doneLL " + dk);
      return "-Your " + K + " came out of your Vault but could not be checked - look in your inventory (an admin has the record).";
    }
  }
  if (!ok) {
    if (tok == null) {
      @PKG@.Gear.warn("LIFELONG TOOL OUT OF PLACE: the Vault handed out " + K + " " + cur + " of profile " + pk + " without a token - gear.log has it (LL-VAULT-NOTOKEN)");
      @PKG@.GearLog.line("LL-VAULT-NOTOKEN " + u + " " + pk + " " + K + " " + cur + " " + (x == null ? "no stack" : @PKG@.GearMerge.json(x)));
      return "-Moving your " + K + " out of the Vault went wrong - an admin has the record (gear.log).";
    }
    Object pb = null;
    try { pb = fb.apply(new Object[] { u, tok }); } catch (Throwable t) { pb = "-" + t; }
    String ps = pb instanceof String ? (String) pb : "-no answer";
    @PKG@.GearLog.line("LL-VAULT-BACK " + u + " " + pk + " " + K + " " + cur + " token " + tok + " " + ps);
    if (ps.startsWith("+")) return "-Your " + K + " could not be put into your inventory - it stayed in your Vault.";
    if (ps.startsWith("=")) return "-Your " + K + " could not be put into your inventory and your Vault is full - it is kept safe and goes back into your Vault at the next restart.";
    return "-Your " + K + " could not be put into your inventory - it goes back into your Vault by itself in a few seconds.";
  }
  Object dn = null;
  try { dn = fd.apply(new Object[] { u, tok }); } catch (Throwable t) { dn = null; }
  crash(12);
  if (!Boolean.TRUE.equals(dn)) {
    @PKG@.Gear.warnOnce("vaultdone", "vault:fn:doneLL did not confirm a fetched lifelong tool (logged once; the Vault closes it by itself - the tool is in the inventory)");
    @PKG@.GearLog.line("LL-VAULT-DONE-UNCONFIRMED " + u + " " + pk + " " + K + " " + cur + " token " + tok);
  }
  if (clearLoc(P, K)) @PKG@.GearLL.save(pk, P);
  hereAdd(u, pk, k);
  N[18] = N[18] + 1L;
  int[] f2 = find(inv, pk, cur);
  String wh = f2 == null ? "inventory" : @PKG@.GearForge.where(f2[0], f2[1]);
  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from the Vault " + at + " -> " + wh);
  return "+Your " + @PKG@.Gear.itemName(x.getItemId()) + " came back from your Vault into your " + wh + ".";
}""")
''')
rep('''  if (pr == null || p == null || k < 0 || k > 3) return "-No player.";''',
    '''  if (pr == null || p == null || k < 0 || k >= @PKG@.GearLL.KIND.length) return "-No player.";          // 0.3.5: + the pole''')
rep('''  String cur = P.getProperty(K + ".uid");
  if (cur == null) return "-Your lifelong " + K + " is still waiting for a free inventory slot - make room and it arrives.";''',
    '''  String cur = P.getProperty(K + ".uid");
  if (cur == null && k == @PKG@.GearLL.POLE) return "-You have no fishing pole yet - Marlow at the hub pier gives you one (got his pole before? hold it and type /lifelong).";          // 0.3.5 (fix round 2: Marlow's rod only)
  if (cur == null) return "-Your lifelong " + K + " is still waiting for a free inventory slot - make room and it arrives.";''')
rep('''  String r = fromWindows(pr, p, inv, pk, P, k, cur);
  if (r != null) return r;
  String[] why = new String[] { null };''', '''  String r = fromWindows(pr, p, inv, pk, P, k, cur);
  if (r != null) return r;
  r = fromVault(pr, inv, pk, P, k, cur);          // 0.3.5: a CLOSED Vault (SkyyVault 0.1.6) - never an exact copy while it has the tool
  if (r != null) return r;
  String[] why = new String[] { null };''')
# /lifelong on a rod while the profile has no pole: adopt it (any time, once)
rep('''  int k = @PKG@.GearLL.kOf(id);
  if (k < 0) return "-Only a pickaxe, hatchet, hoe or sickle can be a lifelong tool.";
  String K = @PKG@.GearLL.KIND[k];
  if (x.getQuantity() != 1) return "-That is a stack - hold a single tool.";''', '''  int k = @PKG@.GearLL.kOf(id);
  if (k < 0) return "-Only a pickaxe, hatchet, hoe, sickle or fishing rod can be a lifelong tool.";
  String K = @PKG@.GearLL.KIND[k];
  if (x.getQuantity() != 1) return "-That is a stack - hold a single tool.";
  // 0.3.5: no pole yet -> the rod in your hand becomes it (any time, once; Marlow's pole after that stays a plain rod)
  if (k == @PKG@.GearLL.POLE && P.getProperty(K + ".uid") == null) {
    @BD@ pd = null;
    try { pd = @PKG@.GearData.gearDoc(x.getMetadata()); } catch (Throwable t0) { pd = null; }
    if (@PKG@.GearLL.isLL(pd) && !pk.equals(@PKG@.GearLL.owner(pd))) return "-That is another player's lifelong pole.";
    // fix round 2 (critic C2, Skyy gear.md "it just initially comes from a quest"): only MARLOW'S rod - one carrying his quest's grant
    // (SkyyFishing's fishing:fn:grantOf; the bench upgrade keeps it) or already stamped lifelong for this profile - becomes the pole. This is
    // for poles claimed before 0.3.5; a crafted / bought plain rod is refused
    String gr = null;
    java.util.function.Function gf = @PKG@.Gear.fn("fishing:fn:grantOf");
    try { Object go = gf == null ? null : gf.apply(x); if (go instanceof String) gr = (String) go; } catch (Throwable t1) { gr = null; }
    if ((gr == null || gr.length() == 0) && !@PKG@.GearLL.isLL(pd)) return "-Only the fishing pole from Marlow's quest at the hub pier can become your lifelong pole - this rod is a plain one.";
    if (!mark(pr, inv, pk, P, k, h[0], h[1], "repick")) return "-That did not work - nothing changed. Try again in a moment.";
    sweep0(pr, inv, true);
    return "+" + @PKG@.Gear.itemName(id) + " is your lifelong fishing pole now - it can't be dropped and /pole brings it back.";
  }''')
# fix round 2 (critic A2, the part that holds): a /pole exact copy is made from the SkyyGear document only - SkyyFishing's rig (reel + parts)
# stays on the original (the copy has its OWN uid + lcu, so the original is restored or retired when it turns up - never removed); the line says so
rep('''  return "+Your " + K + " cannot be reached (" + where + "), so here is an exact copy: " + nm + " - same tier, rarity, rolls, perks and points. If the old one turns up, it is your " + K + " again and this copy disappears.";''',
    '''  return "+Your " + K + " cannot be reached (" + where + "), so here is an exact copy: " + nm + " - same tier, rarity, rolls, perks and points. If the old one turns up, it is your " + K + " again and this copy disappears." + (k == @PKG@.GearLL.POLE ? " Its reel and parts stay on the old pole until then." : "");''')
# perk buys / resets wait during a rebirth
rep('''  if (u == null || k < 0 || k > 3 || p < 0 || p >= @PKG@.GearLL.PK.length) return "-Pick a tool first.";
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";''', '''  if (u == null || k < 0 || k > 3 || p < 0 || p >= @PKG@.GearLL.PK.length) return "-Pick a tool first.";
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  if (@PKG@.GearLL.rbWait(u)) return "-A rebirth is finishing on this profile - try again in a few seconds.";          // 0.3.5''')
rep('''  if (u == null || k < 0 || k > 3) return "-Pick a tool first.";
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "-Your lifelong tool list cannot be read right now.";
  String K = @PKG@.GearLL.KIND[k];
  int sp = @PKG@.GearLL.spent(P, k);''', '''  if (u == null || k < 0 || k > 3) return "-Pick a tool first.";
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  if (@PKG@.GearLL.rbWait(u)) return "-A rebirth is finishing on this profile - try again in a few seconds.";          // 0.3.5
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "-Your lifelong tool list cannot be read right now.";
  String K = @PKG@.GearLL.KIND[k];
  int sp = @PKG@.GearLL.spent(P, k);''')
rep('''", fetched from Requip " + N[14] + " / a window " + N[15] + " / a chest " + N[16] + ", exact copies " + N[17];''',
    '''", fetched from Requip " + N[14] + " / a window " + N[15] + " / a chest " + N[16] + " / the Vault " + N[18] + " (waits " + N[19] + "), exact copies " + N[17] + ", rebirths applied " + N[22] + " (tools reset " + N[20] + ", armor " + N[21] + "), poles stamped " + N[23] + " / adopted " + N[24] + " / plain " + N[25];''')
# Marlow's pole (gear:fn:pole): the stack stamped lifelong for the claim's profile (no registry write here - any thread)
before('''# ---- LifePage: the Tools tab of /smithing (/toolpoints)''', r'''# 0.3.5 THE POLE FROM MARLOW (gear:fn:pole, SkyyFishing 0.1.5's maker; any thread): the rod comes back with a lifelong document for the active
# profile - uid = a hash of profile key + the claim's grant id (every SkyyQuests retry stamps the SAME uid), lgr = the grant. The registry is
# only READ here (the sweep adopts it on arrival). A profile that already has a pole (any uid - fix: also this grant's own, once adopted) gets
# the plain rod back; the same uid is stamped again only while nothing is adopted yet (a SkyyQuests retry before the rod arrived).
M(glf, r"""
public static String poleUid(String pk, String grant) {
  try {
    java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-256");
    byte[] h = md.digest((pk + "|" + grant).getBytes("UTF-8"));
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < 8; i++) { int b = h[i] & 255; if (b < 16) sb.append('0'); sb.append(Integer.toHexString(b)); }
    return sb.toString();
  } catch (Throwable t) { return null; }
}""")
M(glf, r"""
public static @IS@ poleStamp(java.util.UUID u, @IS@ st, String grant) {
  try {
    if (!@PKG@.GearCfg.LL_ON || u == null || st == null || st.isEmpty() || !@PKG@.GearLL.isPole(st.getItemId()) || st.getQuantity() != 1 || grant == null || grant.length() == 0) return st;
    if (@PKG@.GearLL.isLL(docOf(st))) return st;
    String pk = @PKG@.Gear.pkey(u);
    java.util.Properties P = @PKG@.GearLL.reg(pk);
    if (@PKG@.GearLL.bad(P)) { @PKG@.Gear.warnOnce("polebad:" + pk, "Marlow's pole for " + pk + " stays a plain rod: the lifelong list cannot be read right now"); return st; }
    String lu = poleUid(pk, grant);
    if (lu == null) return st;
    String cur = P.getProperty(@PKG@.GearLL.KIND[@PKG@.GearLL.POLE] + ".uid");
    if (cur != null) {          // fix (critic 1.1): the pole exists (adopted) - even the same grant's repeat is a plain rod (a 2nd same-uid stack could replace an upgraded pole)
      N[25] = N[25] + 1L;
      @PKG@.GearLog.line("LL-POLE-PLAIN " + u + " " + pk + " grant " + grant + " (the profile already has the pole " + cur + ")");
      return st;
    }
    @BD@ nd = llDoc(null, st.getItemId(), u, pk, lu, false);
    nd.put("lgr", new org.bson.BsonString(grant));
    N[23] = N[23] + 1L;
    @PKG@.GearLog.line("LL-POLE-STAMP " + u + " " + pk + " " + lu + " grant " + grant);
    return @PKG@.GearData.put(st, nd, u);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("polestamp", "gear:fn:pole failed (the rod stays plain; logged once): " + t); return st; }
}""")
''')
# the pole command + the Tools page selection
rep('''C(llcmds[3], r"""
public SickleCmd() {
  super("sickle", "Lost your lifelong sickle? Brings it back from a chest or Requip, or makes an exact copy (only when you have none)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")''', '''C(llcmds[3], r"""
public SickleCmd() {
  super("sickle", "Lost your lifelong sickle? Brings it back from a chest or Requip, or makes an exact copy (only when you have none)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
C(llcmds[4], r"""
public PoleCmd() {
  super("pole", "Lost your lifelong fishing pole? Brings it back from a chest, the Vault or Requip, or makes an exact copy");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")''')
rep('''    int k = x == null || x.isEmpty() ? -1 : @PKG@.GearLL.kOf(x.getItemId());
    if (k >= 0) page.sel = k;''', '''    int k = x == null || x.isEmpty() ? -1 : @PKG@.GearLL.kOf(x.getItemId());
    if (k >= 0 && k < 4) page.sel = k;          // 0.3.5: the pole is not on the four-row Tools tab''')
# gear:fn:pole (mode 3)
rep('''    java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
    if (this.mode == 2) {''', '''    java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
    if (this.mode == 3) return a[1] instanceof @IS@ ? @PKG@.GearLife.poleStamp(u, (@IS@) a[1], a.length > 2 && a[2] instanceof String ? (String) a[2] : null) : a[1];          // 0.3.5 gear:fn:pole
    if (this.mode == 2) {''')
# THE PARTICIPANT (after GearLLFn)
before('''# ---- the hooks: the join + scan hooks get their bodies now (GearLife exists); the Tools tab click on the other Smithing pages''', r'''# ---- 0.3.5 GearRb = rebirth:part:gear (research/cloud/Rebirth-Spec.md 4.3 / 5.2 / 5.3; the SkyyBank 0.1.11 BankRb shape). apply(Object[] { String op,
# String pkey, String txid, Integer newN, String rewards }) -> String, never throws, never calls another mod (SkyyRebirth's decision only to
# clean an OLDER staged file in prepare, like BankRb):
#   measure  "ok:kinds=<n>;points=<spent>;tiers=<kind:id,...>" (nothing written)
#   prepare  measure + a BACKUP of lifelong/<pkey>.properties in rebirth-backup/<pkey>/<txid>/ (last 3 kept) + the STAGED file rebirth/<pkey>.rb-<txid>
#   commit   ONE atomic write of the RECORD rebirth/<pkey>.record.properties (rb.lastTx = txid, rb.n, rb.at, hist.<n>) - the world thread applies
#            it (GearLife.rbApply / rbTool / rbArmor); already committed = "done"
#   abort    deletes the staged file (refused once committed); status = committed / staged / none
grb.addInterface(pool.get("java.util.function.Function"))
F(grb, "public static volatile int CRASH = 0;")           # harness only: 1 after the backup, 2 after the staged write, 3 after the record write
F(grb, "public static volatile int FAIL_WRITE = 0;")      # harness only: the next N record writes fail
F(grb, "public static final long[] N = new long[5];")    # 0 prepared, 1 committed, 2 done (repeat), 3 aborted, 4 errors
C(grb, "public GearRb() { }")
M(grb, r"""
public static void crash(int n) {
  if (CRASH == n) throw new IllegalStateException("harness: a crash at rebirth step " + n);
}""")
M(grb, "public static boolean validKey(String k) { return k != null && k.length() > 0 && k.length() <= 80 && k.matches(\"[A-Za-z0-9_-]+\"); }")
M(grb, "public static boolean validTx(String tx) { return tx != null && tx.matches(\"tx[0-9]{13}-[0-9a-f]{6}\"); }")
M(grb, r"""
public static java.nio.file.Path staged(String k, String tx) {
  return @PKG@.GearCfg.DIR.resolve("rebirth").resolve(@PKG@.GearLL.safeKey(k) + ".rb-" + tx + ".properties");
}""")
M(grb, r"""
public static void write(java.nio.file.Path f, java.util.Properties p, String comment) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try { p.store(out, comment); out.flush(); out.getFD().sync(); } finally { out.close(); }
  try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  catch (java.nio.file.AtomicMoveNotSupportedException am) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
}""")
M(grb, r"""
public static java.util.Properties read(java.nio.file.Path f) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    return @PKG@.GearCfg.read(f);
  } catch (Throwable t) { return null; }
}""")
M(grb, r"""
public static void deleteTree(java.io.File f) {
  if (f == null) return;
  java.io.File[] c = f.listFiles();
  if (c != null) for (int i = 0; i < c.length; i++) deleteTree(c[i]);
  f.delete();
}""")
M(grb, r"""
public static void backup(String k, String tx) throws java.io.IOException {
  java.nio.file.Path dir = @PKG@.GearCfg.DIR.resolve("rebirth-backup").resolve(@PKG@.GearLL.safeKey(k));
  java.nio.file.Path to = dir.resolve(tx);
  java.nio.file.Files.createDirectories(to, new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path src = @PKG@.GearLL.file(k);
  java.util.Properties p = src == null ? null : read(src);
  if (p == null) { p = new java.util.Properties(); p.setProperty("none", "1"); }
  write(to.resolve(@PKG@.GearLL.safeKey(k) + ".properties"), p, "SkyyGear rebirth backup of lifelong/" + k + ".properties before " + tx + " - restore by hand while the server is stopped");
  java.io.File[] all = dir.toFile().listFiles();
  if (all == null || all.length <= 3) return;
  java.util.Arrays.sort(all);
  for (int i = 0; i < all.length - 3; i++) deleteTree(all[i]);
}""")
M(grb, r"""
public static String decision(String tx) {
  try {
    java.util.function.Function f = @PKG@.Gear.fn("rebirth:fn:decision");
    if (f != null) { Object r = f.apply(tx); if (r instanceof String) return (String) r; }
  } catch (Throwable t) { }
  return "unknown";
}""")
M(grb, r"""
public static String cleanStale(String k, String tx) {
  java.io.File[] fs = @PKG@.GearCfg.DIR.resolve("rebirth").toFile().listFiles();
  if (fs == null) return null;
  String pre = @PKG@.GearLL.safeKey(k) + ".rb-";
  for (int i = 0; i < fs.length; i++) {
    String nm = fs[i].getName();
    if (!nm.startsWith(pre)) continue;
    String old;
    if (nm.endsWith(".properties")) old = nm.substring(pre.length(), nm.length() - 11);
    else if (nm.endsWith(".properties.tmp")) old = nm.substring(pre.length(), nm.length() - 15);
    else continue;
    if (old.equals(tx)) continue;
    if ("commit".equals(decision(old))) return "err:an older rebirth of this profile is still finishing (" + old + ")";
    fs[i].delete();
  }
  return null;
}""")
M(grb, r"""
public static String lastTx(String k) {
  java.util.Properties r = @PKG@.GearLL.rbRec(k);
  return r == null ? null : r.getProperty("rb.lastTx");
}""")
M(grb, r"""
public static String facts(java.util.Properties P) {
  int kinds = 0;
  int pts = 0;
  StringBuilder t = new StringBuilder();
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) {
    String K = @PKG@.GearLL.KIND[k];
    pts = pts + @PKG@.GearLL.spent(P, k);
    if (P.getProperty(K + ".uid") == null) continue;
    kinds++;
    if (t.length() > 0) t.append(',');
    t.append(K).append(':').append(P.getProperty(K + ".id", "?"));
  }
  return "kinds=" + kinds + ";points=" + pts + ";tiers=" + t;
}""")
M(grb, r"""
public static String prepare(String k, String tx, boolean wr) {
  java.util.Properties P = @PKG@.GearLL.reg(k);
  if (@PKG@.GearLL.bad(P)) return "err:the lifelong list of " + k + " cannot be read";
  if (tx.equals(lastTx(k))) return "err:already committed";
  String f = facts(P);
  if (!wr) return "ok:" + f;
  String st = cleanStale(k, tx);
  if (st != null) return st;
  try {
    backup(k, tx);
    crash(1);
    java.util.Properties sp = new java.util.Properties();
    sp.setProperty("tx", tx);
    sp.setProperty("pkey", k);
    sp.setProperty("facts", f);
    write(staged(k, tx), sp, "SkyyGear rebirth " + tx + " - staged (nothing live changes until the commit)");
    crash(2);
  } catch (IllegalStateException ce) { throw ce; }
  catch (Throwable t) { N[4] = N[4] + 1L; return "err:could not write the staged file: " + t; }
  N[0] = N[0] + 1L;
  @PKG@.GearLog.line("LL-REBIRTH-PREPARE " + k + " " + tx + " " + f);
  return "ok:" + f;
}""")
M(grb, r"""
public static String commit(String k, String tx, int n) {
  java.nio.file.Path sp = staged(k, tx);
  if (tx.equals(lastTx(k))) {
    try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t) { }
    N[2] = N[2] + 1L;
    return "done";
  }
  java.util.Properties p = read(sp);
  if (p == null || !tx.equals(p.getProperty("tx"))) return "err:no staged file for " + tx;
  java.util.Properties R = new java.util.Properties();
  java.util.Properties old = @PKG@.GearLL.rbRec(k);
  if (old != null) R.putAll(old);
  R.setProperty("rb.lastTx", tx);
  R.setProperty("rb.n", String.valueOf(n));
  R.setProperty("rb.at", String.valueOf(System.currentTimeMillis()));
  R.setProperty("hist." + n, tx);
  if (FAIL_WRITE > 0) { FAIL_WRITE = FAIL_WRITE - 1; N[4] = N[4] + 1L; return "err:could not write the rebirth record of " + k + " (test)"; }
  try { write(@PKG@.GearLL.rbFile(k), R, "SkyyGear rebirth record of profile " + k + " (written by the server - do not edit while it runs)"); }
  catch (Throwable t) { N[4] = N[4] + 1L; return "err:could not write the rebirth record of " + k + ": " + t; }
  crash(3);
  @PKG@.GearLL.RBREC.put(k, R);
  @PKG@.GearLL.RBBAD.remove(k);          // fix round 2
  try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t2) { }
  try { if (k.length() >= 36) @PKG@.GearLL.RESYNC.put(java.util.UUID.fromString(k.substring(0, 36)), Boolean.TRUE); } catch (Throwable t3) { }
  N[1] = N[1] + 1L;
  @PKG@.GearLog.line("LL-REBIRTH-COMMIT " + k + " " + tx + " rebirth " + n + " (the tools reset at the next look)");
  return "ok";
}""")
M(grb, r"""
public static String abort(String k, String tx) {
  if (tx.equals(lastTx(k))) return "err:already committed";
  try {
    java.nio.file.Path sp = staged(k, tx);
    java.nio.file.Files.deleteIfExists(sp);
    java.nio.file.Files.deleteIfExists(sp.resolveSibling(sp.getFileName().toString() + ".tmp"));
  } catch (Throwable t) { return "err:" + t; }
  N[3] = N[3] + 1L;
  return "done";
}""")
M(grb, r"""
public static String status(String k, String tx) {
  if (tx.equals(lastTx(k))) return "committed";
  return java.nio.file.Files.exists(staged(k, tx), new java.nio.file.LinkOption[0]) ? "staged" : "none";
}""")
M(grb, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "err:bad arguments";
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof String) || !(a[1] instanceof String) || !(a[2] instanceof String)) return "err:bad arguments";
    String op = (String) a[0];
    String k = ((String) a[1]).trim();
    String tx = (String) a[2];
    if (!validKey(k)) return "err:bad profile key";
    if (!validTx(tx)) return "err:bad txid";
    if (@PKG@.GearCfg.DIR == null) return "err:SkyyGear is not started";
    if ("measure".equals(op)) return prepare(k, tx, false);
    if ("prepare".equals(op)) return prepare(k, tx, true);
    if ("commit".equals(op)) {
      int n = a.length > 3 && a[3] instanceof Number ? ((Number) a[3]).intValue() : -1;
      if (n < 1) return "err:no rebirth number";
      return commit(k, tx, n);
    }
    if ("abort".equals(op)) return abort(k, tx);
    if ("status".equals(op)) return status(k, tx);
    return "err:unknown op " + op;
  } catch (IllegalStateException ce) {
    if (CRASH > 0) throw ce;          // harness only: the crash goes up like a JVM stop
    return "err:" + ce;
  } catch (Throwable t) { return "err:" + t; }
}""")
M(grb, r"""
public static String statusText() {
  return "rebirth part rebirth:part:gear (prepared " + N[0] + ", committed " + N[1] + ", repeated " + N[2] + ", aborted " + N[3] + ", errors " + N[4] + ")";
}""")
''')

# ================================================================================================================ the plugin
rep('''  getCommandRegistry().registerCommand(new @PKG@.SickleCmd());
  getCommandRegistry().registerCommand(new @PKG@.LifelongCmd());''', '''  getCommandRegistry().registerCommand(new @PKG@.SickleCmd());
  getCommandRegistry().registerCommand(new @PKG@.PoleCmd());          // 0.3.5: the fishing pole
  getCommandRegistry().registerCommand(new @PKG@.LifelongCmd());''')
rep('''  br.put("quest:caller:gearlife", Boolean.TRUE);            // 0.3.0 fix round 2: SkyyQuests' "lifelong 4/4" tutorial part may count now''',
    '''  br.put("quest:caller:gearlife", Boolean.TRUE);            // 0.3.0 fix round 2: SkyyQuests' "lifelong 4/4" tutorial part may count now
  br.put("gear:fn:pole", new @PKG@.GearLLFn(3));           // 0.3.5: SkyyFishing 0.1.5 stamps Marlow's quest pole lifelong
  br.put("rebirth:part:gear", new @PKG@.GearRb());         // 0.3.5 REBIRTH R7: the participant (SkyyRebirth calls it once "gear" is in its PARTS)''')
rep('''bq.remove("gear:fn:lifelong"); bq.remove("gear:fn:perk"); bq.remove("gear:fn:farmTier"); bq.remove("quest:caller:gearlife");''',
    '''bq.remove("gear:fn:lifelong"); bq.remove("gear:fn:perk"); bq.remove("gear:fn:farmTier"); bq.remove("quest:caller:gearlife"); bq.remove("gear:fn:pole"); bq.remove("rebirth:part:gear");''')
rep('''/toolpoints, /pickaxe, /hatchet, /hoe, /sickle, /lifelong, /gear (admin:''', '''/toolpoints, /pickaxe, /hatchet, /hoe, /sickle, /pole, /lifelong, /gear (admin:''')
rep('''@PKG@.GearTill.statusText() + "; gear:fn:curve''', '''@PKG@.GearTill.statusText() + "; " + @PKG@.GearRb.statusText() + "; identify reveal " + (@PKG@.Gear.fn("explore:fn:reveal") != null ? "on (SkyyExploration)" : "waits for SkyyExploration 0.2.8") + "; gear:fn:curve''')
rep('''gear:fn:lifelong, gear:fn:perk, gear:fn:farmTier; wand / staff tooltips''', '''gear:fn:lifelong, gear:fn:perk, gear:fn:farmTier, gear:fn:pole, rebirth:part:gear; wand / staff tooltips''')
rep('''your lifelong hoe tills a bigger square the higher its tier; Server Setup -> Gear.''',
    '''your lifelong hoe tills a bigger square the higher its tier; /pickaxe and co. bring your exact tool out of a closed Vault; bare hands count as a Crude hoe on crops; identifying flips cards on SkyyExploration's reveal page; the fishing pole is the fifth lifelong tool (/pole, from Marlow's quest); rebirths reset lifelong tools to Crude and Mining armor to Copper (rebirth:part:gear) and open multitools; Server Setup -> Gear.''')

# ================================================================================================================ checks on the result
assert s.count("GearLife.fromVault(") == 0 and s.count("fromVault(pr, inv, pk, P, k, cur)") == 1 and s.count("revealOne(u, res, rvC") == 4
assert s.count("allInC(by, rs, u") == 2 and s.count("rbTool(pr, c, i, x, d, k, pk, P)") == 1 and s.count("new @PKG@.GearRb()") == 1
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.4 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.4 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
