r"""Derive SkyyRolls/build_skyyrolls_0.1.4.py from the LIVE 0.1.3 (tools/deploy_set.py pins SkyyRolls 0.1.3).
0.1.4 (Skyy's beta backlog 2026-09-24 20:10, item 2 + the 19:50 note):

1. REFORGE ANVIL PAGE: /reforge (hytale:Adventurer - the first player command in SkyyRolls; /rolls stays admin-only).
   Hypixel SkyBlock reforge-anvil style, built as ONE inline CustomUIPage (HANDOFF section 2 rules: no .ui file, no underscores in
   element ids, root Group anchor Width/Height only, TextButton + EventData, rebuilt only after a click, never a periodic update):
   - Left "Anvil" panel: the picked item as a big ItemIcon, its name in rarity colour ("<Reforge> <item>"), rarity, where it sits
     (e.g. "Hotbar 3"), the current roll as SkyBlock-style stat lines (same text as the tooltip, see 2), the coin cost for its
     rarity, the player's purse, and a big Reforge button. After a reforge the lines show the NEW roll (green "New roll" header)
     and a "Before: ..." line with the previous roll. Empty anvil = the cost table per rarity (all six QIDS, Junk .. Legendary,
     plus "Other items" = cost.default). Clicking Select on the item already on the anvil (or Refresh) keeps the last reforge's
     "New roll" / "Before" lines; picking a different item clears them.
   - Right "Your gear" panel: every rollable item the player carries (hotbar, worn armor, tools, utility, inventory, backpack -
     the same Weapon_*/Armor_*/Tool_* rule as /rolls: no ammo, no Skyy items), 9 per page with Prev/Next, one Select button each.
     Opening /reforge with a rollable item in hand puts that item on the anvil right away.
   - "Put the item in" = PICK FROM THE INVENTORY LIST (one of the two options in the task). The item never leaves its slot: the
     reforge rewrites that slot in place, so nothing can be lost or duplicated on a crash, a disconnect, a closed page or a profile
     switch, and there is no custody code to get wrong. The single-slot ContainerWindow variant (openCustomPageWithWindows) is left
     out on purpose: the SkyySacks 0.3.0 page+ContainerWindow experiment was never confirmed in game, and custody would need
     return paths for close / disconnect / crash / profile:busy. Nothing is drawn on the vanilla inventory screen.
   - Reforge click, all on the player's world thread (page events run there): double-click guard 400 ms (no charge) ->
     profile:busy:<uuid> set -> refused (PROFILES-CONTRACT rule 5) -> profile:epoch changed since the item was picked -> refused,
     pick again -> the slot is re-read and must still hold the SAME item (item id + its SkyyRolls JSON = fingerprint), else refused
     -> Rolls.refuse() again -> stacks of more than 1 refused ("split the stack first": one roll per item) -> cost by the stack's
     quality id from Skyy_SkyyRolls/reforge.properties -> coins TAKEN FIRST through the SkyyCoins bridge coins:fn:take
     (apply(Object[]{UUID, Long}) -> Boolean; null/no function = coins unavailable, nothing taken) -> reroll (Rolls.applyRolls =
     fresh SkyyRolls + the ItemDisplay tooltip) -> setItemStackForSlot on the same container + slot -> if that throws or the
     transaction did not succeed: REFUND through coins:fn:add (apply(Object[]{UUID, Long}) -> Long) and a WARNING log line (a failed
     refund logs "REFUND FAILED, give back N coins by hand"). Success: page shows the new roll, chat-free (the info line says
     "Reforged! Your Mithril Shortbow is now Heroic (-2,500 coins)."), server log line "reforge: <player> <item> [old] -> [new] cost N".
     SkyyCoins' coins:fn:* act on the ACTIVE profile (coins 0.1.5), so the item and the coins always belong to the same profile.
   - Costs (coins, by the engine quality id of the stack; Server/Item/Qualities): Junk 100, Common 250, Uncommon 500, Rare 1000,
     Epic 2500, Legendary 5000 (Hypixel SkyBlock's reforge-anvil ladder), cost.default 1000 for every other quality (Tool,
     Technical, Developer, ...). File Skyy_SkyyRolls/reforge.properties (created with comments on first start, crash-safe: written
     as reforge.properties.tmp then moved into place with the SkyyCoins retry loop, never over an existing file; 0 = free; clamped
     0..1e12); re-read automatically when the file's modified time changes (checked on every /reforge), so no reload command.
   - /rolls reroll stays as the free ADMIN tool (unchanged).
2. TOOLTIP STYLE (Skyy 2026-09-24 19:50): every stat line shows the item's BASE value with the roll's bonus in brackets:
   "Damage: 11-48 (+24%)". Stats without a base show only the roll ("Strength: +12"). The base damage comes from the ENGINE'S OWN
   weapon damage data (read-only evidence, HytaleServer.jar bytecode 2026-09-24):
   - ItemModule.computeWeaponData(LoadedAssetsEvent) runs for every loaded Item with getWeapon() != null:
     WeaponDamageDataCollector.calculate(item, InteractionType.Primary) walks the item's Primary interaction chain with the item's
     own InteractionVars (InteractionManager.walkChain + a Collector over the DamageEntityInteraction / DamageCalculator /
     TargetedDamage nodes) and stores it with ItemWeapon.setBasicDamageBreakdown(); Ability1 (the signature) goes to
     setUltimateDamageBreakdown(); then Item.invalidatePacketCache() (the breakdown is sent to the client with the item).
     DamageBreakdown is a record: entries() -> List<DamageBreakdown$Entry(String labelKey, float min, float max)>, one entry per
     label ("" = the basic attack, "charged", ...).
   - Skyy's live server log (2026-09-24 19:51) has "Computed damage data for 221 of 265 weapon items" (vanilla) and "4 of 4"
     (a pack mod - More Crossbow Tiers), so modded weapons and future SkyyGear weapons are covered with no table in this jar.
   - Displayed base = min of the entries' min .. max of the entries' max of the BASIC breakdown (the ultimate breakdown only when
     the basic one is empty); a single value when min == max; entries with max <= 0 ignored (the engine never stores those:
     WeaponDamageDataCollector.outof only keeps a leaf with totalDmgMax > 0). An entry's min counts even when it is 0, and a
     min below 0 counts as 0: DamageCalculator.computeDamageRange has no clamp (min = sum x (1 - RandomPercentageModifier)), so a
     modifier of 1 or more gives a 0 / negative floor -> "0-48", never a lone "48" or another entry's higher floor. (Fix round
     2026-09-24: no vanilla weapon has a modifier >= 1 - Assets.zip only has 0 / 0.1 / 0.15 / 0.2 - and the only >= 1 value in
     the installed mods is an NPC attack, TheLostWorlds Sky_Guard_Combat 3.0, so this is a guard for future modded weapons.)
     Cross-check from Assets.zip JSON
     (build-time only, not shipped): Weapon_Shortbow_Mithril Primary vars = 11/17/23/31/37 damage per charge level + 48 headshot
     (TargetedDamage Head), and its damage interactions have no RandomPercentageModifier -> "11-48", exactly Skyy's example.
     Engine detail (WeaponDamageDataCollector.applyDamage): each hit adds DamageCalculator.computeDamageRange(runTime, out) =
     sum(BaseDamage) x (1 -/+ RandomPercentageModifier) to the leaf's totals, so weapons WITH a random spread show that spread
     (Weapon_Longsword_Copper: 11 and 33 with 0.15 -> about "9.4-38"), and a chain that hits several times in one attack shows the
     summed total. These are the engine's own numbers (the same breakdown the client receives with the item).
   - Items with no weapon damage data (tools, armor, the 44 vanilla weapons the engine computes nothing for) show roll-only lines.
   STAT SET UNCHANGED (placeholder until Skyy finishes the SkyyGear stat list): dmg %, str, crit, plus Reforge + Roll Quality lines.
   EASY TO EXTEND: the build script has ONE Python table STATS = [(key, label, max roll, unit, base source)]; it generates the Java
   arrays STAT_KEY / STAT_LABEL / STAT_MAX / STAT_UNIT / STAT_BASE, and roll(), the tooltip, the page lines, the chat line and the
   "Before" summary all loop over them. A new stat = one row (+ a branch in Rolls.baseText when it has a base value, e.g. armor
   defence later). A stat line is only shown when the item's SkyyRolls document has that key, so old items never show "+0" for a
   stat that did not exist when they were rolled. Metadata stays exactly {reforge, dmg, str, crit, quality, rolledAt}.
   VIEW_V 1 -> 2 and the tooltip signature now includes the base text, so every rolled item gets the new lines at the next join
   refresh (or /rolls read) - and again automatically if a game update changes a weapon's damage.
3. Not in 0.1.4 (Skyy is still deciding SkyyGear): unidentified drops, rarity-based roll ranges, smithing rarity, Smithing XP for
   reforging, reforge stones / powders, per-level costs, the rolls actually changing combat numbers (they stay display-only).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.3.py")
dst = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')

# ---------------- docstring ----------------
rep('''"""SkyyRolls 0.1.3 - build script (javassist via jpype). P0 spike #3: prove ItemStack metadata survives save/reload.
Run:   python build_skyyrolls_0.1.3.py            -> SkyyRolls/SkyyRolls-0.1.3.jar
       python build_skyyrolls_0.1.3.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
Commands (ADMIN ONLY, see Permissions below):''',
    '''"""SkyyRolls 0.1.4 - build script (javassist via jpype). Item rolls (reforge + stats) in ItemStack metadata, shown on the tooltip,
and the Reforge Anvil page.
Run:   python build_skyyrolls_0.1.4.py            -> SkyyRolls/SkyyRolls-0.1.4.jar
       python build_skyyrolls_0.1.4.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
Player command (hytale:Adventurer):
  /reforge               opens the Reforge Anvil page: pick a weapon, armor piece or tool from "Your gear" (or hold it when you
                         type /reforge), see its roll + the coin cost for its rarity, click Reforge to reroll it for coins
                         (SkyyCoins bridge: taken first, refunded if the reroll fails); the item stays in its own slot.
                         Costs: Skyy_SkyyRolls/reforge.properties (re-read when the file changes).
Commands (ADMIN ONLY, see Permissions below):''')
rep('''0.1.3: the rolls are SHOWN on the item: native ItemDisplay metadata''',
    '''0.1.4: /reforge Reforge Anvil page (pick from your gear, coins taken first + refunded on failure, cost by rarity from
  reforge.properties); tooltip stat lines show the BASE value with the roll in brackets, 'Damage: 11-48 (+24%)', base damage read
  from the engine's own weapon damage data (ItemWeapon.getBasicDamageBreakdown, computed by ItemModule at asset load - covers
  modded weapons); one STATS table drives rolls, tooltip, page and chat (easy to extend); VIEW_V 2 refreshes old tooltips.
  Design, evidence and what is left out: tools/rolls_0_1_4_patch.py.
0.1.3: the rolls are SHOWN on the item: native ItemDisplay metadata''')
rep('''Permissions: SkyyRolls is a test spike and /rolls give creates items, so it stays ADMIN-ONLY on purpose: there is NO''',
    '''Permissions (0.1.4): /reforge is a PLAYER command - its constructor calls setPermissionGroups(new String[] { "hytale:Adventurer" })
  (COMMAND RULES; vanilla /help pattern, same as SkyyAccessories /accessories). Everything below is about /rolls only.
Permissions: SkyyRolls is a test spike and /rolls give creates items, so it stays ADMIN-ONLY on purpose: there is NO''')
rep('''  skyy.0.1.3_skyyrolls.command.rolls, ...command.rolls.read''', '''  skyy.0.1.4_skyyrolls.command.rolls, ...command.rolls.read''')

# ---------------- engine names + probes ----------------
rep('''PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
''', '''PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
# 0.1.4: engine weapon damage data (tooltip base values) + the inline page API (same classes as SkyyAccessories / SkyyGuilds pages)
IWP = "com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon"
DBD = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown"
DBE = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown$Entry"
ILT = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
PAGE = "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE = "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
''')
rep('''    B.probe(pool, c, m)

PKG = "com.skyy.rolls"''', '''    B.probe(pool, c, m)
for c, m in ((ITM, "getWeapon"), (IWP, "getBasicDamageBreakdown"), (IWP, "getUltimateDamageBreakdown"), (DBD, "entries"),
             (DBE, "min"), (DBE, "max"), (IQ, "getLocalizationKey"), (IQ, "getId"), (ILT, "getIndex"), (ILT, "getAsset"),
             (PAGE, "rebuild"), (PAGE, "build"), (PAGE, "handleDataEvent"), (LIFE, "CanDismiss"), (PLA, "getPageManager"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (UCB, "appendInline"), (UCB, "set"), (UEB, "addEventBinding"), (EVD, "of"), (BT, "Activating"),
             (AC, "setPermissionGroups"), (IC, "setItemStackForSlot"), (INV, "getActiveToolsSlot"), (JP, "getDataDirectory"),
             (IS, "getQuantity")):
    B.probe(pool, c, m)

PKG = "com.skyy.rolls"''')

# ---------------- new classes + the @NAME@ source helpers ----------------
rep('''pl  = pool.makeClass(PKG + ".SkyyRollsPlugin", pool.get(JP))
''', '''pl  = pool.makeClass(PKG + ".SkyyRollsPlugin", pool.get(JP))
rfg = pool.makeClass(PKG + ".Reforge")                          # 0.1.4: costs config, coins bridge, gear scan (pure static)
rpg = pool.makeClass(PKG + ".ReforgePage", pool.get(PAGE))      # 0.1.4: /reforge inline page
rfc = pool.makeClass(PKG + ".ReforgeCmd", pool.get(APC))        # 0.1.4: /reforge (hytale:Adventurer)

# 0.1.4: new Java is written as raw strings with @NAME@ placeholders (SkyyGuilds style): no f-string brace doubling, and a Java \\"
# is written as-is. J() fails the build on any placeholder it cannot resolve.
import re as _re
T = {"PKG": PKG, "IS": IS, "BD": BD, "BV": BV, "MSG": MSG, "ITM": ITM, "IQ": IQ, "IWP": IWP, "DBD": DBD, "DBE": DBE, "INV": INV,
     "IC": IC, "PLA": PLA, "PR": PR, "REF": REF, "ST": ST, "WLD": WLD, "CTX": CTX, "TXN": TXN, "PAGE": PAGE, "LIFE": LIFE,
     "UCB": UCB, "UEB": UEB, "EVD": EVD, "BT": BT}


def J(src):
    for k, v in T.items():
        src = src.replace("@" + k + "@", v)
    left = _re.findall(r"@[A-Z]+@", src)
    assert not left, "unresolved placeholder(s): %s" % left
    return src


def M(c, src):
    c.addMethod(CtNewMethod.make(J(src), c))


def F(c, src):
    c.addField(CtField.make(J(src), c))


def C(c, src):
    c.addConstructor(CtNewConstructor.make(J(src), c))

''')

# ---------------- stat table ----------------
rep('''rl.addField(CtField.make('public static final int VIEW_V = 1;', rl))
''', '''rl.addField(CtField.make('public static final int VIEW_V = 2;', rl))   # 0.1.4: 2 = base value + (roll) lines -> old tooltips refresh
# ---------------- 0.1.4 STAT TABLE (Skyy is still designing the SkyyGear stats - this is the placeholder set) ----------------
# One row per rolled stat: (metadata key in "SkyyRolls", label on the tooltip / page, max roll (rolled 0..max), unit, base source).
# base source: "damage" = the weapon's base damage range from the engine's weapon damage data (Rolls.damageText);
#              ""       = the stat has no base value, its line shows only the roll ("Strength: +12").
# A new stat = one row here (+ a branch in Rolls.baseText when it has a base value). roll(), the tooltip, the /reforge page, the
# chat line and the "Before" summary all loop over these arrays. Items rolled before a row existed simply do not show that line.
# "reforge", "quality" and "rolledAt" are fixed keys (the reforge name, the 0-100 roll quality, the roll time), not stats.
STATS = [
    # key     label       max  unit  base
    ("dmg",  "Damage",    30,  "%",  "damage"),
    ("str",  "Strength",  25,  "",   ""),
    ("crit", "Crit",      15,  "",   ""),
]
assert len(set(r[0] for r in STATS)) == len(STATS), "duplicate stat key"
for _r in STATS:
    assert _re.match(r"^[a-z][a-zA-Z0-9]*$", _r[0]) and _r[0] not in ("reforge", "quality", "rolledAt"), _r
    assert _r[2] > 0 and _r[3] in ("", "%") and _r[4] in ("", "damage"), _r
    assert '"' not in _r[1] and "\\\\" not in _r[1], _r


def _jstr(vals):
    return "new String[] { " + ", ".join('"%s"' % v for v in vals) + " }"


F(rl, "public static final String[] STAT_KEY = " + _jstr([r[0] for r in STATS]) + ";")
F(rl, "public static final String[] STAT_LABEL = " + _jstr([r[1] for r in STATS]) + ";")
F(rl, "public static final int[] STAT_MAX = new int[] { " + ", ".join(str(r[2]) for r in STATS) + " };")
F(rl, "public static final String[] STAT_UNIT = " + _jstr([r[3] for r in STATS]) + ";")
F(rl, "public static final String[] STAT_BASE = " + _jstr([r[4] for r in STATS]) + ";")
''')

# ---------------- base values + stat text helpers, new tooltip description ----------------
OLD_DESC = '''# Description: the vanilla description (only when the item has one - otherwise the client would print the raw key), a blank line,
# then one line per roll. Same shape as SimpleEnchantments composeDescription (base + "\\n" + coloured raw lines).
rl.addMethod(CtNewMethod.make(f"""
public static {MSG} descMsg({IS} it, {BD} d, String col) {{
  {MSG} m = {MSG}.empty();
  try {{
    {ITM} item = it.getItem();
    if (item != null && tr(item.getDescriptionTranslationKey()) != null) {{
      m.insert(item.getDescriptionTranslationMessage());
      m.insert({MSG}.raw("\\\\n\\\\n"));
    }}
  }} catch (Throwable t) {{ }}
  int vd = num(d, "dmg");
  int vs = num(d, "str");
  int vc = num(d, "crit");
  int vq = num(d, "quality");
  m.insert(statLine("Reforge", str(d, "reforge"), col));
  m.insert({MSG}.raw("\\\\n"));
  m.insert(statLine("Damage", "+" + vd + "%", vd > 0 ? "#55FF55" : "#AAAAAA"));
  m.insert({MSG}.raw("\\\\n"));
  m.insert(statLine("Strength", "+" + vs, vs > 0 ? "#55FF55" : "#AAAAAA"));
  m.insert({MSG}.raw("\\\\n"));
  m.insert(statLine("Crit", "+" + vc, vc > 0 ? "#55FF55" : "#AAAAAA"));
  m.insert({MSG}.raw("\\\\n"));
  m.insert(statLine("Roll Quality", vq + "%", qualityColor(vq)));
  return m;
}}""", rl))
'''
NEW_DESC = r'''# ---- 0.1.4: base values. The engine computes every weapon's damage at asset load (ItemModule.computeWeaponData ->
# WeaponDamageDataCollector.calculate(item, Primary / Ability1) -> ItemWeapon.setBasicDamageBreakdown / setUltimateDamageBreakdown;
# DamageBreakdown.entries() = records (labelKey, min, max)). Base damage = lowest min .. highest max of the basic (Primary) breakdown;
# the ultimate (signature) breakdown only when the basic one is empty. A min of 0 counts, a min below 0 (a RandomPercentageModifier
# of 1 or more; computeDamageRange has no clamp) counts as 0. Evidence: tools/rolls_0_1_4_patch.py.
M(rl, """
public static String fnum(float f) {
  long r = Math.round((double) f);
  if (Math.abs(f - (float) r) < 0.05f) return String.valueOf(r);
  return String.valueOf(Math.round((double) f * 10.0) / 10.0);
}""")
M(rl, """
public static @BD@ rollsDoc(@IS@ it) {
  if (it == null || it.isEmpty()) return null;
  @BD@ md = it.getMetadata();
  if (md == null) return null;
  @BV@ v = md.get("SkyyRolls");
  if (v == null || !v.isDocument()) return null;
  return v.asDocument();
}""")
M(rl, """
public static float[] rangeOf(@DBD@ b) {
  if (b == null) return null;
  java.util.List es = b.entries();
  if (es == null || es.isEmpty()) return null;
  float lo = Float.MAX_VALUE;
  float hi = 0f;
  for (int i = 0; i < es.size(); i++) {
    Object o = es.get(i);
    if (!(o instanceof @DBE@)) continue;
    @DBE@ e = (@DBE@) o;
    float a = e.min();
    float z = e.max();
    if (z <= 0f) continue;
    if (a < 0f) a = 0f;
    if (a < lo) lo = a;
    if (z > hi) hi = z;
  }
  if (hi <= 0f) return null;
  if (lo == Float.MAX_VALUE || lo > hi) lo = hi;
  return new float[] { lo, hi };
}""")
M(rl, """
public static float[] damageRange(@IS@ it) {
  try {
    if (it == null || it.isEmpty()) return null;
    @ITM@ item = it.getItem();
    if (item == null) return null;
    @IWP@ w = item.getWeapon();
    if (w == null) return null;
    float[] r = rangeOf(w.getBasicDamageBreakdown());
    if (r == null) r = rangeOf(w.getUltimateDamageBreakdown());
    return r;
  } catch (Throwable t) { return null; }
}""")
M(rl, """
public static String damageText(@IS@ it) {
  float[] r = damageRange(it);
  if (r == null) return null;
  String a = fnum(r[0]);
  String z = fnum(r[1]);
  return a.equals(z) ? a : a + "-" + z;
}""")
# base value text of one stat, null = no base (the line shows only the roll). New base sources go here.
M(rl, """
public static String baseText(@IS@ it, String src) {
  if (src == null || src.length() == 0 || it == null) return null;
  if (src.equals("damage")) return damageText(it);
  return null;
}""")
M(rl, """
public static boolean hasStat(@BD@ d, int i) {
  return d != null && i >= 0 && i < STAT_KEY.length && d.containsKey(STAT_KEY[i]);
}""")
M(rl, """
public static String bonus(@BD@ d, int i) {
  int v = num(d, STAT_KEY[i]);
  return (v >= 0 ? "+" : "") + v + STAT_UNIT[i];
}""")
M(rl, """
public static @MSG@ baseLine(String label, String base, String bon, String bc) {
  @MSG@ m = @MSG@.empty();
  m.insert(@MSG@.raw(label + ": ").color("#AAAAAA"));
  m.insert(@MSG@.raw(base).color("#FFFFFF"));
  m.insert(@MSG@.raw(" (" + bon + ")").color(bc));
  return m;
}""")
# what the base values were when the tooltip was written (part of sig: a game update that changes a weapon's damage re-writes it)
M(rl, """
public static String baseSig(@IS@ it) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < STAT_KEY.length; i++) {
    String b = baseText(it, STAT_BASE[i]);
    if (b != null) sb.append(STAT_KEY[i]).append('=').append(b).append(';');
  }
  return sb.toString();
}""")
# plain-text stat lines (the /reforge page and the /rolls chat line); d == null = an item that was never rolled
M(rl, """
public static String[] statLines(@IS@ it, @BD@ d) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (d != null) {
    out.add("Reforge: " + str(d, "reforge"));
    for (int i = 0; i < STAT_KEY.length; i++) {
      if (!hasStat(d, i)) continue;
      String b = baseText(it, STAT_BASE[i]);
      out.add(STAT_LABEL[i] + ": " + (b != null ? b + " (" + bonus(d, i) + ")" : bonus(d, i)));
    }
    out.add("Roll Quality: " + num(d, "quality") + "%");
  } else {
    StringBuilder names = new StringBuilder();
    for (int i = 0; i < STAT_KEY.length; i++) {
      String b = baseText(it, STAT_BASE[i]);
      if (b != null) out.add(STAT_LABEL[i] + ": " + b);
      if (names.length() > 0) names.append(i == STAT_KEY.length - 1 ? " and " : ", ");
      names.append(STAT_LABEL[i]);
    }
    out.add("Not reforged yet - a reforge rolls " + names.toString() + " bonuses.");
  }
  String[] arr = new String[out.size()];
  for (int i = 0; i < arr.length; i++) arr[i] = (String) out.get(i);
  return arr;
}""")
# one-line roll summary (the page's "Before:" line and the reforge log line)
M(rl, """
public static String summary(@BD@ d) {
  if (d == null) return "not reforged";
  StringBuilder sb = new StringBuilder(str(d, "reforge"));
  for (int i = 0; i < STAT_KEY.length; i++) {
    if (!hasStat(d, i)) continue;
    sb.append("   ").append(STAT_LABEL[i]).append(' ').append(bonus(d, i));
  }
  sb.append("   Quality ").append(num(d, "quality")).append('%');
  return sb.toString();
}""")
# Description: the vanilla description (only when the item has one - otherwise the client would print the raw key), a blank line,
# then the Reforge line, one line per rolled stat from the STATS table - "Label: <base> (<roll>)" when the stat has a base value,
# "Label: <roll>" otherwise - and Roll Quality. Same shape as SimpleEnchantments composeDescription (base + "\n" + coloured raw lines).
M(rl, """
public static @MSG@ descMsg(@IS@ it, @BD@ d, String col) {
  @MSG@ m = @MSG@.empty();
  try {
    @ITM@ item = it.getItem();
    if (item != null && tr(item.getDescriptionTranslationKey()) != null) {
      m.insert(item.getDescriptionTranslationMessage());
      m.insert(@MSG@.raw("\\n\\n"));
    }
  } catch (Throwable t) { }
  m.insert(statLine("Reforge", str(d, "reforge"), col));
  for (int i = 0; i < STAT_KEY.length; i++) {
    if (!hasStat(d, i)) continue;
    int v = num(d, STAT_KEY[i]);
    String bc = v > 0 ? "#55FF55" : "#AAAAAA";
    String base = baseText(it, STAT_BASE[i]);
    m.insert(@MSG@.raw("\\n"));
    if (base != null) m.insert(baseLine(STAT_LABEL[i], base, bonus(d, i), bc));
    else m.insert(statLine(STAT_LABEL[i], bonus(d, i), bc));
  }
  int vq = num(d, "quality");
  m.insert(@MSG@.raw("\\n"));
  m.insert(statLine("Roll Quality", vq + "%", qualityColor(vq)));
  return m;
}""")
'''
rep(OLD_DESC, NEW_DESC)

rep('''public static String sig({IS} it, {BD} d) {{
  return VIEW_V + ":" + it.getItemId() + ":" + it.getQualityIndex() + ":" + Integer.toHexString(d.toJson().hashCode());
}}''', '''public static String sig({IS} it, {BD} d) {{
  return VIEW_V + ":" + it.getItemId() + ":" + it.getQualityIndex() + ":" + Integer.toHexString(d.toJson().hashCode())
    + ":" + Integer.toHexString(baseSig(it).hashCode());
}}''')

rep('''  d.append("reforge", new org.bson.BsonString(REFORGES[r.nextInt(REFORGES.length)]));
  d.append("dmg", new org.bson.BsonInt32(r.nextInt(31)));
  d.append("str", new org.bson.BsonInt32(r.nextInt(26)));
  d.append("crit", new org.bson.BsonInt32(r.nextInt(16)));
  d.append("quality", new org.bson.BsonInt32(r.nextInt(101)));''', '''  d.append("reforge", new org.bson.BsonString(REFORGES[r.nextInt(REFORGES.length)]));
  for (int i = 0; i < STAT_KEY.length; i++) d.append(STAT_KEY[i], new org.bson.BsonInt32(r.nextInt(STAT_MAX[i] + 1)));   // 0.1.4: STATS table
  d.append("quality", new org.bson.BsonInt32(r.nextInt(101)));''')

rep('''  {BD} d = v.asDocument();
  return str(d, "reforge") + " " + it.getItemId()
    + "  dmg +" + num(d, "dmg") + "%"
    + "  str " + num(d, "str")
    + "  crit " + num(d, "crit")
    + "  quality " + num(d, "quality")
    + (upToDate(it) ? "  [shown on the tooltip]" : "  [not on the tooltip]");''', '''  String[] ls = statLines(it, v.asDocument());   // 0.1.4: same lines as the tooltip / page (base value + (roll))
  StringBuilder sb = new StringBuilder(it.getItemId());
  for (int i = 0; i < ls.length; i++) sb.append("  ").append(ls[i]);
  sb.append(upToDate(it) ? "  [shown on the tooltip]" : "  [not on the tooltip]");
  return sb.toString();''')

# ---------------- Reforge helpers, page, /reforge (all Rolls methods exist by now) ----------------
REFORGE = r'''
# ================= 0.1.4 Reforge: costs config, coins bridge, gear scan (static; world thread except load at setup) =================
F(rfg, "public static volatile java.nio.file.Path FILE;")
F(rfg, "public static volatile java.util.HashMap COSTS = new java.util.HashMap();")
F(rfg, "public static volatile long MTIME = -1L;")
# Hypixel SkyBlock reforge-anvil ladder by rarity; every other quality id (Tool, Technical, Developer, ...) pays cost.default
F(rfg, 'public static final String[] QIDS = new String[] { "Junk", "Common", "Uncommon", "Rare", "Epic", "Legendary" };')
F(rfg, "public static final long[] QDEF = new long[] { 100L, 250L, 500L, 1000L, 2500L, 5000L };")
F(rfg, "public static final long DEF_OTHER = 1000L;")
# inventory sections: 0 hotbar, 1 storage, 2 backpack, 3 armor, 4 utility, 5 tools; listed hotbar, armor, tools, utility, storage, backpack
F(rfg, "public static final int[] SCAN = new int[] { 0, 3, 5, 4, 1, 2 };")
F(rfg, 'public static final String[] SEC_NAME = new String[] { "Hotbar", "Inventory", "Backpack", "Armor", "Utility", "Tools" };')
M(rfg, """
public static String defaultsText() {
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyRolls - Reforge Anvil (/reforge) cost in coins, by the item's quality (rarity) id.\\n");
  sb.append("# Coins are taken through SkyyCoins before the reroll and refunded if the reroll fails. 0 = free.\\n");
  sb.append("# Quality ids = Server/Item/Qualities (Junk, Common, Uncommon, Rare, Epic, Legendary; mods can add more).\\n");
  sb.append("# cost.default is used for every other quality (Tool, Technical, ...).\\n");
  sb.append("# This file is re-read automatically when it changes (checked every time someone opens /reforge).\\n");
  for (int i = 0; i < QIDS.length; i++) sb.append("cost." + QIDS[i] + "=" + QDEF[i] + "\\n");
  sb.append("cost.default=" + DEF_OTHER + "\\n");
  return sb.toString();
}""")
# First-run default file, crash-safe (SkyyCoins 0.1.5 saveK / SkyyProfiles pattern): write reforge.properties.tmp, then move it
# into place, retried 5 x 20 ms on a FileSystemException (Windows sharing violation from a scanner / indexer). A crash mid-write
# leaves only the .tmp, never a half-written reforge.properties (a truncated "cost.Legendary=50" would be a valid, wrong price);
# the next start simply writes it again. No REPLACE_EXISTING: a file that appeared meanwhile (an admin's own) is never overwritten.
M(rfg, """
public static void writeDefaults(java.nio.file.Path dst) throws Exception {
  java.nio.file.Files.createDirectories(dst.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dst.resolveSibling(dst.getFileName().toString() + ".tmp");
  java.nio.file.Files.write(tmp, defaultsText().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
  Throwable last = null;
  int i = 0;
  while (i < 5) {
    try {
      java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[0]);
      return;
    } catch (java.nio.file.FileAlreadyExistsException ae) {
      try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable d1) { }
      return;
    } catch (java.nio.file.FileSystemException fe) {
      last = fe;
      i++;
    } catch (Throwable t) {
      last = t;
      i = 5;
    }
    if (i < 5) { try { Thread.sleep(20L); } catch (Throwable ie) { } }
  }
  try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable d2) { }
  throw new java.io.IOException("could not create " + dst + ": " + last);
}""")
M(rfg, """
public static synchronized void load() {
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < QIDS.length; i++) m.put(QIDS[i].toLowerCase(), Long.valueOf(QDEF[i]));
  m.put("default", Long.valueOf(DEF_OTHER));
  try {
    if (FILE != null) {
      if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) writeDefaults(FILE);
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String k = (String) it.next();
        if (!k.startsWith("cost.")) continue;
        try {
          long v = Long.parseLong(p.getProperty(k).trim().replace(",", "").replace(" ", ""));
          if (v < 0L) v = 0L;
          if (v > 1000000000000L) v = 1000000000000L;
          m.put(k.substring(5).trim().toLowerCase(), Long.valueOf(v));
        } catch (Throwable e) { @PKG@.Rolls.warn("reforge.properties: " + k + " is not a whole number - the default is used"); }
      }
      MTIME = java.nio.file.Files.getLastModifiedTime(FILE, new java.nio.file.LinkOption[0]).toMillis();
    }
  } catch (Throwable t) { @PKG@.Rolls.warn("could not read reforge.properties - the default costs are used: " + t); }
  COSTS = m;
}""")
M(rfg, """
public static void maybeReload() {
  try {
    java.nio.file.Path f = FILE;
    if (f == null) return;
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { load(); return; }
    long t = java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis();
    if (t != MTIME) { load(); @PKG@.Rolls.info("reforge.properties changed - reforge costs re-read"); }
  } catch (Throwable e) { }
}""")
M(rfg, """
public static String qualityId(@IS@ it) {
  try {
    Object q = @IQ@.getAssetMap().getAsset(it.getQualityIndex());
    if (q instanceof @IQ@) { String id = ((@IQ@) q).getId(); if (id != null) return id; }
  } catch (Throwable t) { }
  return "";
}""")
M(rfg, """
public static String qualityName(@IS@ it) {
  try {
    Object q = @IQ@.getAssetMap().getAsset(it.getQualityIndex());
    if (q instanceof @IQ@) {
      String n = @PKG@.Rolls.tr(((@IQ@) q).getLocalizationKey());
      if (n != null) return n;
      String id = ((@IQ@) q).getId();
      if (id != null) return id;
    }
  } catch (Throwable t) { }
  return "Common";
}""")
M(rfg, """
public static String qcolor(String qid) {
  try {
    int ix = @IQ@.getAssetMap().getIndex(qid);
    Object q = @IQ@.getAssetMap().getAsset(ix);
    if (q instanceof @IQ@) { String h = @PKG@.Rolls.hex(((@IQ@) q).getTextColor()); if (h != null) return h; }
  } catch (Throwable t) { }
  return "#c9d2dd";
}""")
M(rfg, """
public static long costOf(String qid) {
  java.util.HashMap m = COSTS;
  Object v = qid == null ? null : m.get(qid.toLowerCase());
  if (v == null) v = m.get("default");
  return v instanceof Long ? ((Long) v).longValue() : DEF_OTHER;
}""")
M(rfg, """
public static long cost(@IS@ it) {
  return costOf(qualityId(it));
}""")
M(rfg, """
public static String fmt(long n) {
  String s = String.valueOf(n < 0L ? -n : n);
  StringBuilder sb = new StringBuilder();
  int c = 0;
  for (int i = s.length() - 1; i >= 0; i--) {
    sb.append(s.charAt(i));
    c++;
    if (c % 3 == 0 && i > 0) sb.append(',');
  }
  if (n < 0L) sb.append('-');
  return sb.reverse().toString();
}""")
M(rfg, """
public static Object bridgeGet(String k) {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (b instanceof java.util.Map) return ((java.util.Map) b).get(k);
  } catch (Throwable t) { }
  return null;
}""")
# SkyyCoins 0.1.5 bridge (build_skyycoins_0.1.5.py docstring): coins:fn:get apply(UUID) -> Long; coins:fn:take
# apply(Object[]{UUID, Long}) -> Boolean (false = not enough, nothing taken); coins:fn:add apply(Object[]{UUID, Long}) -> Long.
# All three act on the ACTIVE profile and return null while that profile's balance file cannot be read (frozen key).
M(rfg, """
public static long purse(java.util.UUID u) {
  try {
    Object f = bridgeGet("coins:fn:get");
    if (!(f instanceof java.util.function.Function)) return -1L;
    Object r = ((java.util.function.Function) f).apply(u);
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { @PKG@.Rolls.warn("coins:fn:get failed: " + t); }
  return -1L;
}""")
# 1 = taken, 0 = not enough coins (nothing taken), -1 = coins unavailable (no SkyyCoins, unreadable balance, error)
M(rfg, """
public static int take(java.util.UUID u, long amt) {
  try {
    Object f = bridgeGet("coins:fn:take");
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(amt) });
    if (r instanceof Boolean) return ((Boolean) r).booleanValue() ? 1 : 0;
  } catch (Throwable t) { @PKG@.Rolls.warn("coins:fn:take failed: " + t); }
  return -1;
}""")
M(rfg, """
public static boolean refund(java.util.UUID u, long amt) {
  try {
    Object f = bridgeGet("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(amt) });
    return r instanceof Number;
  } catch (Throwable t) { @PKG@.Rolls.warn("coins:fn:add (refund) failed: " + t); }
  return false;
}""")
M(rfg, """
public static String epoch(java.util.UUID u) {
  Object e = bridgeGet("profile:epoch:" + u);
  return e == null ? "" : String.valueOf(e);
}""")
M(rfg, """
public static @IC@ section(@INV@ inv, int s) {
  if (inv == null) return null;
  if (s == 0) return inv.getHotbar();
  if (s == 1) return inv.getStorage();
  if (s == 2) return inv.getBackpack();
  if (s == 3) return inv.getArmor();
  if (s == 4) return inv.getUtility();
  if (s == 5) return inv.getTools();
  return null;
}""")
M(rfg, """
public static @IS@ at(@INV@ inv, int s, int slot) {
  @IC@ c = section(inv, s);
  if (c == null || slot < 0 || slot >= c.getCapacity()) return null;
  return c.getItemStack((short) slot);
}""")
# what must still be in the slot for a reforge click to go through: the same item id AND the same rolls
M(rfg, """
public static String fp(@IS@ it) {
  if (it == null || it.isEmpty()) return "";
  return it.getItemId() + "|" + @PKG@.Rolls.rollsJson(it);
}""")
M(rfg, """
public static boolean same(@IS@ it, String id, String f) {
  if (it == null || it.isEmpty() || id == null || f == null) return false;
  return id.equals(it.getItemId()) && f.equals(fp(it));
}""")
M(rfg, """
public static java.util.ArrayList gear(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  for (int k = 0; k < SCAN.length; k++) {
    @IC@ c = section(inv, SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || @PKG@.Rolls.refuse(it) != null) continue;
      out.add(new int[] { SCAN[k], i });
    }
  }
  return out;
}""")
M(rfg, """
public static String where(int s, int slot) {
  if (s < 0 || s >= SEC_NAME.length) return "inventory";
  return SEC_NAME[s] + " " + (slot + 1);
}""")
M(rfg, """
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id;
  if (s.startsWith("Weapon_")) s = s.substring(7);
  else if (s.startsWith("Armor_")) s = s.substring(6);
  else if (s.startsWith("Tool_")) s = s.substring(5);
  return s.replace('_', ' ');
}""")
M(rfg, """
public static String itemName(@IS@ it) {
  String n = null;
  try { n = @PKG@.Rolls.tr(it.getItem().getTranslationKey()); } catch (Throwable t) { n = null; }
  if (n != null && n.indexOf(123) < 0) return n;
  return pretty(it == null ? null : it.getItemId());
}""")
M(rfg, """
public static String displayName(@IS@ it, @BD@ d) {
  return (d != null ? @PKG@.Rolls.str(d, "reforge") + " " : "") + itemName(it);
}""")

# ================= 0.1.4 ReforgePage (inline, rebuilt only after a click) =================
for f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int selSec;", "public int selSlot;", "public String selId;",
          "public String selFp;", "public String info;", "public String before;", "public boolean fresh;", "public String epoch;",
          "public long lastForge;"):
    F(rpg, f)
C(rpg, """
public ReforgePage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.rows = new java.util.ArrayList();
  this.pageNo = 0;
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null;
  this.info = ""; this.before = null; this.fresh = false; this.lastForge = 0L;
  this.epoch = @PKG@.Reforge.epoch(pr.getUuid());
}""")
M(rpg, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ');
}""")
M(rpg, """
public static String style(String bg, String hov, String press, String fg, int fs) {
  String ls = "LabelStyle: (FontSize: " + fs + ", TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + ls + "), Hovered: (Background: " + hov + ", " + ls + "), Pressed: (Background: " + press + ", " + ls + "));";
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr / SkyyGuilds 0.1 GuildPage.jsonStr)
M(rpg, """
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
# info line: "+" good (green), "-" refused / failed (orange), "=" neutral
M(rpg, """
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#8fe39a";
  if (c == '-') return "#ff9d6b";
  return "#cfe3ff";
}""")
M(rpg, """
public static String textOf(String res) {
  if (res == null) return "";
  if (res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-' || res.charAt(0) == '=')) return res.substring(1);
  return res;
}""")
M(rpg, """
public void clearSel() {
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null; this.before = null; this.fresh = false;
}""")
# Re-picking the item that is ALREADY on the anvil (its "On the anvil" button stays clickable) changes nothing: same slot, same
# fingerprint (item id + rolls, selFp is updated after every reforge) and same profile epoch -> keep before / fresh / info, so the
# last reforge's "New roll" + "Before:" lines do not vanish. Any other pick (other slot, changed item, other profile) resets them.
M(rpg, """
public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.Reforge.at(inv, s, slot);
  if (it == null || it.isEmpty() || @PKG@.Rolls.refuse(it) != null) return false;
  String ep = @PKG@.Reforge.epoch(this.playerRef.getUuid());
  String f = @PKG@.Reforge.fp(it);
  if (s == this.selSec && slot == this.selSlot && f.equals(this.selFp) && ep.equals(this.epoch)) return true;
  this.selSec = s; this.selSlot = slot; this.selId = it.getItemId(); this.selFp = f;
  this.before = null; this.fresh = false;
  this.epoch = ep;
  this.info = "=" + @PKG@.Reforge.itemName(it) + " is on the anvil. Click Reforge to reroll it.";
  return true;
}""")
# /reforge with a rollable item in hand puts it on the anvil (hand = tools section while usingToolsItem, else the active hotbar slot)
M(rpg, """
public void preselect(@INV@ inv) {
  try {
    if (inv == null) return;
    if (inv.usingToolsItem()) pick(inv, 5, (int) inv.getActiveToolsSlot());
    else pick(inv, 0, (int) inv.getActiveHotbarSlot());
  } catch (Throwable t) { }
}""")
M(rpg, """
public void anvil(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel) {
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 22);
  String rs = style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 22);
  b.appendInline("#SkyyRfMain", "Group #SkyyRfAnvil { Anchor: (Width: 580, Height: 620); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 10); Background: #142030(0.92); }");
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 34); Text: \\"Anvil\\"; Style: (FontSize: 21, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfAnvil", "Group #SkyyRfSel { Anchor: (Height: 122); LayoutMode: Left; }");
  b.appendInline("#SkyyRfSel", "Group #SkyyRfSlot { Anchor: (Width: 120, Height: 118); Background: #0b1524(0.95); }");
  if (sel != null) b.appendInline("#SkyyRfSlot", "ItemIcon { Anchor: (Width: 100, Height: 100, Left: 10, Top: 9); ItemId: \\"" + safe(sel.getItemId()) + "\\"; }");
  else b.appendInline("#SkyyRfSlot", "Label { Anchor: (Full: 0); Text: \\"?\\"; Style: (FontSize: 48, RenderBold: true, TextColor: #3a4a60, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfSel", "Label { Anchor: (Width: 16, Height: 118); Text: \\"\\"; }");
  b.appendInline("#SkyyRfSel", "Group #SkyyRfSelTxt { Anchor: (Width: 412, Height: 118); LayoutMode: Top; }");
  String col = sel == null ? "#9fb8d0" : @PKG@.Rolls.rarityColor(sel);
  b.appendInline("#SkyyRfSelTxt", "Label #SkyyRfName { Anchor: (Height: 46); Text: \\"\\"; Style: (FontSize: 22, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfSelTxt", "Label #SkyyRfRar { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfSelTxt", "Label #SkyyRfWhere { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }");
  if (sel == null) {
    b.set("#SkyyRfName.Text", "The anvil is empty");
    b.set("#SkyyRfRar.Text", "Pick an item from Your gear");
    b.set("#SkyyRfWhere.Text", "It stays in its own slot while you reforge it.");
    b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 16); Text: \\"\\"; }");
    b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 32); Text: \\"Reforge cost by rarity\\"; Style: (FontSize: 18, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
    int n = 0;
    for (int i = 0; i < @PKG@.Reforge.QIDS.length; i++) {
      String q = @PKG@.Reforge.QIDS[i];
      b.appendInline("#SkyyRfAnvil", "Label #SkyyRfCost" + n + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + @PKG@.Reforge.qcolor(q) + ", VerticalAlignment: Center); }");
      b.set("#SkyyRfCost" + n + ".Text", q + ": " + @PKG@.Reforge.fmt(@PKG@.Reforge.costOf(q)) + " coins");
      n++;
    }
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfCost" + n + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfCost" + n + ".Text", "Other items: " + @PKG@.Reforge.fmt(@PKG@.Reforge.costOf("default")) + " coins");
    b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 14); Text: \\"\\"; }");
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfHow1 { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfHow1.Text", "A reforge rerolls the reforge name and every stat of the item.");
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfHow2 { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfHow2.Text", "Tip: hold the item when you type /reforge to put it on the anvil.");
    return;
  }
  @BD@ d = @PKG@.Rolls.rollsDoc(sel);
  b.set("#SkyyRfName.Text", @PKG@.Reforge.displayName(sel, d));
  b.set("#SkyyRfRar.Text", @PKG@.Reforge.qualityName(sel).toUpperCase() + (sel.getQuantity() > 1 ? "   x" + sel.getQuantity() : ""));
  b.set("#SkyyRfWhere.Text", "In your " + @PKG@.Reforge.where(this.selSec, this.selSlot) + " - it stays there while you reforge it.");
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 10); Text: \\"\\"; }");
  b.appendInline("#SkyyRfAnvil", "Label #SkyyRfStHdr { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + (this.fresh ? "#8fe39a" : "#e6f2ff") + ", VerticalAlignment: Center); }");
  b.set("#SkyyRfStHdr.Text", this.fresh ? "New roll" : (d == null ? "Not reforged yet" : "Current roll"));
  String[] lines = @PKG@.Rolls.statLines(sel, d);
  for (int i = 0; i < lines.length && i < 8; i++) {
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfSt" + i + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 18, TextColor: " + (this.fresh ? "#c8ffd0" : "#dfe8f2") + ", VerticalAlignment: Center); }");
    b.set("#SkyyRfSt" + i + ".Text", lines[i]);
  }
  if (this.before != null) {
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfBefore { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 14, TextColor: #8a9bb0, VerticalAlignment: Center); }");
    b.set("#SkyyRfBefore.Text", "Before: " + this.before);
  }
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 12); Text: \\"\\"; }");
  long cost = @PKG@.Reforge.cost(sel);
  long have = @PKG@.Reforge.purse(u);
  b.appendInline("#SkyyRfAnvil", "Label #SkyyRfCostTxt { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 19, RenderBold: true, TextColor: #ffd070, VerticalAlignment: Center); }");
  b.set("#SkyyRfCostTxt.Text", cost > 0L ? "Cost: " + @PKG@.Reforge.fmt(cost) + " coins (" + @PKG@.Reforge.qualityName(sel) + ")" : "Cost: free");
  b.appendInline("#SkyyRfAnvil", "Label #SkyyRfPurse { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #cfe3ff, VerticalAlignment: Center); }");
  b.set("#SkyyRfPurse.Text", have >= 0L ? "Your purse: " + @PKG@.Reforge.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)");
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 8); Text: \\"\\"; }");
  boolean poor = cost > 0L && have >= 0L && have < cost;
  String bt = poor ? "Not enough coins" : (cost > 0L ? "Reforge (" + cost + " coins)" : "Reforge");
  b.appendInline("#SkyyRfAnvil", "Group #SkyyRfGo { Anchor: (Height: 60); LayoutMode: Left; }");
  b.appendInline("#SkyyRfGo", "Label { Anchor: (Width: 94, Height: 56); Text: \\"\\"; }");
  b.appendInline("#SkyyRfGo", "TextButton #SkyyRfForge { Anchor: (Width: 360, Height: 56); Text: \\"" + safe(bt) + "\\"; " + (poor ? rs : gs) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyRfForge", @EVD@.of("a", "reforge"));
}""")
M(rpg, """
public void gearList(@UCB@ b, @UEB@ ev, @INV@ inv) {
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 16);
  String ss = style("#6e5a1c", "#8a7224", "#4a3c10", "#fff0c8", 16);
  b.appendInline("#SkyyRfMain", "Group #SkyyRfList { Anchor: (Width: 596, Height: 620); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 10); Background: #142030(0.92); }");
  b.appendInline("#SkyyRfList", "Label #SkyyRfGearHdr { Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 21, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
  b.set("#SkyyRfGearHdr.Text", "Your gear (" + this.rows.size() + ")");
  int per = 9;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (this.rows.isEmpty()) {
    b.appendInline("#SkyyRfList", "Label #SkyyRfEmpty1 { Anchor: (Height: 40); Text: \\"\\"; Style: (FontSize: 17, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyRfEmpty1.Text", "No weapons, armor or tools on you.");
    b.appendInline("#SkyyRfList", "Label #SkyyRfEmpty2 { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyRfEmpty2.Text", "Carry one (hotbar, inventory, backpack or worn) and click Refresh.");
  }
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] r = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.Reforge.at(inv, r[0], r[1]);
    if (it == null || it.isEmpty()) continue;
    int idx = i - start;
    boolean on = r[0] == this.selSec && r[1] == this.selSlot;
    String rid = "#SkyyRfRow" + idx;
    @BD@ d = @PKG@.Rolls.rollsDoc(it);
    String col = @PKG@.Rolls.rarityColor(it);
    b.appendInline("#SkyyRfList", "Group #SkyyRfRow" + idx + " { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 4); Background: " + (on ? "#2c3a1e(0.95)" : "#0f1a2a(0.9)") + "; }");
    b.appendInline(rid, "Group { Anchor: (Width: 56, Height: 44); ItemIcon { Anchor: (Width: 40, Height: 40, Left: 8, Top: 2); ItemId: \\"" + safe(it.getItemId()) + "\\"; } }");
    b.appendInline(rid, "Group #SkyyRfRowTxt" + idx + " { Anchor: (Width: 334, Height: 44); LayoutMode: Top; }");
    b.appendInline("#SkyyRfRowTxt" + idx, "Label #SkyyRfRowName" + idx + " { Anchor: (Height: 24); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
    b.set("#SkyyRfRowName" + idx + ".Text", @PKG@.Reforge.displayName(it, d) + (it.getQuantity() > 1 ? "  x" + it.getQuantity() : ""));
    b.appendInline("#SkyyRfRowTxt" + idx, "Label #SkyyRfRowSub" + idx + " { Anchor: (Height: 20); Text: \\"\\"; Style: (FontSize: 13, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfRowSub" + idx + ".Text", @PKG@.Reforge.qualityName(it) + "  -  " + (d == null ? "not reforged" : "reforged: " + @PKG@.Rolls.str(d, "reforge")) + "  -  " + @PKG@.Reforge.where(r[0], r[1]));
    b.appendInline(rid, "Label { Anchor: (Width: 20, Height: 44); Text: \\"\\"; }");
    b.appendInline(rid, "TextButton #SkyyRfPick" + idx + " { Anchor: (Width: 150, Height: 42); Text: \\"" + (on ? "On the anvil" : "Select") + "\\"; " + (on ? ss : bs) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyRfPick" + idx, @EVD@.of("a", "sel:" + i));
    b.appendInline("#SkyyRfList", "Label { Anchor: (Height: 4); Text: \\"\\"; }");
  }
  if (pages > 1) {
    b.appendInline("#SkyyRfList", "Group #SkyyRfNav { Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyRfNav", "Label { Anchor: (Width: 92, Height: 34); Text: \\"\\"; }");
    b.appendInline("#SkyyRfNav", "TextButton #SkyyRfPrev { Anchor: (Width: 110, Height: 34); Text: \\"< Prev\\"; " + bs + " }");
    b.appendInline("#SkyyRfNav", "Label #SkyyRfPageTxt { Anchor: (Width: 150, Height: 34); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyRfPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyRfNav", "TextButton #SkyyRfNext { Anchor: (Width: 110, Height: 34); Text: \\"Next >\\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyRfPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyRfNext", @EVD@.of("a", "next"));
  }
}""")
M(rpg, """
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @INV@ inv = p == null ? null : p.getInventory();
  @IS@ sel = null;
  if (this.selSec >= 0) {
    sel = @PKG@.Reforge.at(inv, this.selSec, this.selSlot);
    if (!@PKG@.Reforge.same(sel, this.selId, this.selFp)) {
      sel = null;
      clearSel();
      if (this.info == null || this.info.length() == 0 || this.info.charAt(0) != '-') this.info = "-The item on the anvil moved or changed - pick it again.";
    }
  }
  this.rows = @PKG@.Reforge.gear(inv);
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 16);
  b.appendInline((String) null, "Group #SkyyRf { Anchor: (Width: 1240, Height: 860); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyRf", "Group { Anchor: (Height: 3); Background: #ffd070; }");
  b.appendInline("#SkyyRf", "Label { Anchor: (Height: 50); Text: \\"Reforge Anvil\\"; Style: (FontSize: 30, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyRf", "Label #SkyyRfSub { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyRfSub.Text", "Pick a weapon, armor piece or tool from Your gear. A reforge rerolls its reforge and stats for coins.");
  b.appendInline("#SkyyRf", "Label { Anchor: (Height: 8); Text: \\"\\"; }");
  b.appendInline("#SkyyRf", "Group #SkyyRfMain { Anchor: (Height: 620); LayoutMode: Left; }");
  anvil(b, ev, u, sel);
  b.appendInline("#SkyyRfMain", "Label { Anchor: (Width: 16, Height: 620); Text: \\"\\"; }");
  gearList(b, ev, inv);
  b.appendInline("#SkyyRf", "Label #SkyyRfInfo { Anchor: (Height: 36); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + colorOf(this.info) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyRfInfo.Text", textOf(this.info));
  b.appendInline("#SkyyRf", "Group #SkyyRfBottom { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyRfBottom", "Label { Anchor: (Width: 526, Height: 40); Text: \\"\\"; }");
  b.appendInline("#SkyyRfBottom", "TextButton #SkyyRfRefresh { Anchor: (Width: 140, Height: 40); Text: \\"Refresh\\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyRfRefresh", @EVD@.of("a", "refresh"));
}""")
# The reforge click. Order: guard -> profile:busy -> epoch -> same item still in the slot -> rollable -> one item -> cost -> coins
# TAKEN FIRST -> reroll + write the same slot -> on any failure REFUND. World thread (page events), same thread as SkyyCoins' callers.
M(rpg, """
public void forge(@INV@ inv) {
  long now = System.currentTimeMillis();
  if (now - this.lastForge < 400L) return;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Rolls.busy(u)) { this.info = "-Your profile is still loading - nothing was reforged. Try again in a moment."; return; }
  if (this.selSec < 0) { this.info = "-Pick an item from Your gear first."; return; }
  String ep = @PKG@.Reforge.epoch(u);
  if (!ep.equals(this.epoch)) { clearSel(); this.epoch = ep; this.info = "-Your profile changed - pick the item again."; return; }
  @IS@ it = @PKG@.Reforge.at(inv, this.selSec, this.selSlot);
  if (!@PKG@.Reforge.same(it, this.selId, this.selFp)) { clearSel(); this.info = "-That item moved or changed - pick it again."; return; }
  String why = @PKG@.Rolls.refuse(it);
  if (why != null) { this.info = "-" + why; return; }
  if (it.getQuantity() > 1) { this.info = "-A reforge works on one item at a time - split this stack of " + it.getQuantity() + " first."; return; }
  long cost = @PKG@.Reforge.cost(it);
  String name = @PKG@.Reforge.itemName(it);
  if (cost > 0L) {
    int t = @PKG@.Reforge.take(u, cost);
    if (t < 0) { this.info = "-Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken."; return; }
    if (t == 0) {
      long have = @PKG@.Reforge.purse(u);
      this.info = "-Not enough coins: this reforge costs " + @PKG@.Reforge.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Reforge.fmt(have) : "") + ".";
      return;
    }
  }
  @BD@ old = @PKG@.Rolls.rollsDoc(it);
  @IS@ nu = null;
  Object tx = null;
  Throwable err = null;
  try {
    nu = @PKG@.Rolls.applyRolls(it);
    tx = @PKG@.Reforge.section(inv, this.selSec).setItemStackForSlot((short) this.selSlot, nu);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && nu != null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || @PKG@.Reforge.refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Rolls.warn("REFORGE FAILED for " + this.playerRef.getUsername() + " (" + u + ") on " + this.selId + ": " + what
      + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    this.info = back ? "-The reforge failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Reforge.fmt(cost) + " coins were refunded." : ".")
      : "-The reforge failed and the refund did not go through - an admin can find it in the server log.";
    return;
  }
  this.lastForge = now;
  this.selFp = @PKG@.Reforge.fp(nu);
  this.before = @PKG@.Rolls.summary(old);
  this.fresh = true;
  @BD@ nd = @PKG@.Rolls.rollsDoc(nu);
  this.info = "+Reforged! Your " + name + " is now " + @PKG@.Rolls.str(nd, "reforge") + (cost > 0L ? " (-" + @PKG@.Reforge.fmt(cost) + " coins)." : ".");
  @PKG@.Rolls.info("reforge: " + this.playerRef.getUsername() + " " + this.selId + " [" + @PKG@.Rolls.summary(old) + "] -> [" + @PKG@.Rolls.summary(nd) + "] cost " + cost);
}""")
M(rpg, """
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("refresh")) { this.info = ""; rebuild(); return; }   // rescans Your gear; the anvil's last result stays (build() drops it if the item moved)
    if (a.equals("prev")) { this.pageNo--; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; rebuild(); return; }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = p == null ? null : p.getInventory();
    if (inv == null) return;
    if (a.startsWith("sel:")) {
      int i = -1;
      try { i = Integer.parseInt(a.substring(4)); } catch (Throwable t) { i = -1; }
      if (i < 0 || this.rows == null || i >= this.rows.size()) return;
      int[] r = (int[]) this.rows.get(i);
      if (!pick(inv, r[0], r[1])) this.info = "-That item is not there any more.";
      rebuild();
      return;
    }
    if (a.equals("reforge")) { forge(inv); rebuild(); return; }
  } catch (Throwable t) { @PKG@.Rolls.warn("reforge page click failed: " + t); }
}""")

# ================= 0.1.4 /reforge (player command) =================
C(rfc, """
public ReforgeCmd() {
  super("reforge", "Open the Reforge Anvil: reroll the reforge and stats of a weapon, armor piece or tool for coins");
  setPermissionGroups(new String[] { "hytale:Adventurer" });   // COMMAND RULES: ordinary players lack the auto node
}""")
M(rfc, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PKG@.Reforge.maybeReload();
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Reforge] no player found")); return; }
    @PKG@.ReforgePage page = new @PKG@.ReforgePage(pr);
    page.preselect(p.getInventory());
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Rolls.warn("/reforge failed: " + t);
    pr.sendMessage(@MSG@.raw("[Reforge] could not open the Reforge Anvil - the server log has the details"));
  }
}""")

'''
rep('''EXEC = f"protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{"
''', REFORGE + '''EXEC = f"protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{"
''')

# ---------------- plugin ----------------
rep('''  {PKG}.Rolls.LOG = getLogger();
  getCommandRegistry().registerCommand(new {PKG}.RollsCmd());
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.RollsReady());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /rolls [read] | /rolls reroll | /rolls give [itemId] | /rolls clear (admin only); rolls shown on the item tooltip");''',
    '''  {PKG}.Rolls.LOG = getLogger();
  // 0.1.4: stable data folder (HANDOFF: never the versioned default dir) + reforge costs
  {PKG}.Reforge.FILE = getDataDirectory().resolveSibling("Skyy_SkyyRolls").resolve("reforge.properties");
  {PKG}.Reforge.load();
  getCommandRegistry().registerCommand(new {PKG}.RollsCmd());
  getCommandRegistry().registerCommand(new {PKG}.ReforgeCmd());
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.RollsReady());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /reforge (players) opens the Reforge Anvil; /rolls [read] | reroll | give [itemId] | clear (admin only); tooltip = base value (+roll)");''')

rep('''for c in (rl, rdc, rrc, clc, gvc, gvr, cmd, rft, rdy, pl):''', '''for c in (rl, rfg, rpg, rfc, rdc, rrc, clc, gvc, gvr, cmd, rft, rdy, pl):''')
rep('''"SkyWynn item rolls spike: random stats stored in ItemStack metadata and shown on the item tooltip (/rolls give|read|reroll|clear). Zero dependencies."''',
    '''"SkyWynn item rolls: reforge + stats stored in ItemStack metadata, shown on the tooltip as base value (+roll); /reforge Reforge Anvil page (coins via SkyyCoins, optional); /rolls admin tools. Zero dependencies."''')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
