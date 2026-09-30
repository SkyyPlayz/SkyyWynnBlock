"""Derive SkyyAccessories/build_skyyaccessories_0.5.py from the LIVE 0.4.5 (build_skyyaccessories_0.4.5.py = the tools/deploy_set.py
SET pin; same style as acc_0_4_5_patch.py: rep(old, new) / cut(a, b, new) with asserted anchors; 0.4.5 stays untouched).
Run:  python tools/acc_0_5_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.py   (bare JVM -Xverify:all, table, fold, migration on a scratch copy, paging)

0.5 = BOOSTER ACCESSORIES, PART 1 (research/Booster-Accessories-Spec.md sections 1, 2.2, 5 and 6.1; Skyy's decisions in
OPEN-QUESTIONS.md, LOCKED 2026-09-30: no tier words - "they are all accessories. but they come in the same rarity tiers as weapons and
armor"; a line upgrades Normal -> Unique -> Rare -> Legendary and stops there; Fabled / Mythic are rare finds later; bag 18 up to 60;
fold the 25 talismans with the new numbers; "+stamina" = max Stamina AND Stamina Regen; admin give now; a stat that does nothing is
never on a booster). What changes (everything else is 0.4.5's, asserted by the KEEP blocks below):

  1. ONE BOOSTER TABLE (BOOSTERS in the generated script, between "# ---- BOOSTER TABLE START / END" so the harness execs it):
     family key (item ids), admin name (config, commands, acc:defs), line name (what players see), crystal colour, Legendary gem,
     stats [(entry, kind, four numbers Normal..Legendary)], source words per rarity, flavour line, the four Workbench recipes. The
     Java side is flat 1-D arrays (javassist cannot compile [][] or labeled break, spec 5.4): AccDefs.FAMILIES / LINE_ADMIN /
     LINE_NAME / LINE_IDS / LINE_SRC [line x 4 + tier - 1], E_KEYS / E_LINE / E_UNIT / E_WHOLE / E_CAP per config entry and the live
     numbers AccDefs.BOOST [entry x 5 + tier] (tier 0 = 0). STAT_KINDS is the allowlist (spec 1.4): a row with any other kind stops
     the build. Part 2 (0.5.1) adds rows + kinds and nothing else.
  2. THE FOLD: the 20 ids Skyy_Talisman_<Key>_<Common|Uncommon|Rare|Epic> = Normal..Legendary; the old fifth id _Legendary is a
     LEGACY id like _Talisman / _Ring / _Artifact (asset kept, no recipe, counts as Legendary, modernOf -> _Epic, ties with _Epic so
     the bag refuses the second one). Separate arrays: AccDefs.ID_WORD (ids only) and DISPLAY (everything players see). Names
     "<Rarity> <Line> Accessory" (legacy ids show the name of the rarity they count as); tooltips in the vanilla item-text markup
     (stat line first, what it does, the one-per-line rule with the next rarity, an italic flavour line). Numbers (spec 2.2):
     Health +6/+12/+18/+24 flat, Stamina +1.5/+3/+4.5/+6 flat + Stamina Regen +5/+10/+15/+20 %, Mana +6/+12/+18/+24 % with a floor
     of +1/+2/+3/+4, Regeneration 0.25/0.5/0.75/1.0 % every 2 s, Speed +2.5/+5/+7.5/+10 %.
  3. STAMINA REGEN (spec 5.4.1): AccEffects.staminaRegen tops Stamina up by pct x vanilla's CURRENT refill rate (the positive
     ADDITIVE regen entries of the Stamina value whose conditions pass Condition.allConditionsMet(cb, ref, now, rg) - exactly the
     check the engine's own regen makes, so never while sprinting, gliding or blocking, never during the empty-bar pause) x the
     seconds since the last 1 s tick; addStatValue like the engine, capped at max, skipped for a dead player. B.probe on every call.
  4. GEAR RARITIES: six quality assets Skyy_Acc_Normal .. Skyy_Acc_Mythic (QualityValue 1-6, the vanilla Common.json field set,
     SkyyGear's frame art, the kit's rarity colours, labels under general.qualities.* AND server.general.qualities.*; Fabled and
     Mythic ship unused so the quality index shift happens once). Bench accessories I Normal, II Unique, III Rare, IV+ Legendary; the
     Omni Legendary; the bag item Unique. AccDefs.rarityOf = 1..4 for every 0.5 item.
     RESTAMP: saved stacks keep their old quality index, so AccTick (every 5 s) hands each online player an AccRestampTask through
     world.execute (the SkyySacks 0.7.7 SweepTask pattern: the world thread, outside any system tick); it skips a player while
     AccStore.moveBlock says the profile is loading, fixes every Skyy_Talisman_* / Skyy_Accessory_* stack (the bag item included)
     in storage / hotbar / backpack whose index differs from its item's (withQuality: id and count unchanged, asserted), and counts
     the accessories before and after. (Spec 5.2 put it inside AccEffects.tick; a world task is the proven SkyySacks way - no
     inventory write while the store is ticking.)
  5. CONFIG MIGRATION (spec 5.1), AccCfg.migrate in AccCfg.load(true), BEFORE CfgPub.start: runs only when config.properties has a
     bonus. line and no boost. line (after it, never again - a later slots=9 stays 9); copies the file once to
     config.properties.pre-0.5.bak (never overwritten); slots=9 -> 18; untouched 0.4.x defaults give way; an edited Mana /
     Regeneration / Speed list is carried as its 1st, 2nd, 3rd and 5th numbers (capped at the entry's cap); an edited Health /
     Stamina list (unit % -> flat) or a list that is not 5 numbers is dropped and logged; the old bonus. lines and their 0.4.x
     default comments leave the file; the missing 0.5 keys (notice switch, 5 line switches, 7 boost. entries) are appended with
     comments. One atomic write (tmp + fsync + ATOMIC_MOVE), then one config-changes.log line per value in the kit's format (who
     migration-0.5, uuid -, via migrate) and one INFO line each. A file with neither kind of line only gets the missing keys.
  6. ONE-TIME NOTICE (spec 5.1, Server Setup switch notice.boosters, default on): AccNotice, checked from the effect tick (the
     player is ready, world thread) once per player per session: a player with a bag file from before (bags/<uuid>.properties or
     <uuid>-p<N>.properties) gets the spec's chat line once, ever; a player without one is recorded as new and never gets it.
     Seen players live in Skyy_SkyyAccessories/notices.properties, written by AccTick (never the world thread), atomically.
     (The spec suggested a PlayerReadyEvent listener; the effect tick already runs once a second for every ready player, so no
     listener is added.)
  7. THE BAG: AccStore.CAP 9 -> 60 storage slots; slot0..slot8 stay in bags/<key>.properties (same format - 0.4.5 reads and rewrites
     only that file), slot9..slot59 go into bags/<key>.more.properties (written only when it holds something or already exists;
     never deleted). A bag file that cannot be read at load is never overwritten afterwards (AccStore.BADFILE) and the page moves
     nothing into or out of that bag (AccStore.isBad: "your accessory bag file could not be read ..."). Config row slots:

     default 18, max 60 (new equips only, as in 0.4.4).
     THE PAGE (kit tools/skyyui.py 1.4, vanilla look kept): 1210 x 952 (fits 1080); the top well = the hint, the Bonuses summary
     (#SkyyAccBonus, 0.4.5's id) and two columns of 6 short lines (#SkyyAccBon0..11: "+24 max Health", "+20% Stamina Regen", ...,
     "<Line> Accessory - switched off"; live config numbers); the two list wells show PAGE_ROWS = 9 rows each (bag slots | the
     accessories in the inventory) in fixed row groups with the kit pager under each (#SkyyAccSp / #SkyyAccIp: small Secondary
     Prev / Next in the vanilla Disabled look at the ends, caption "Page 1 / 7"); the slot head shows "Bag slots - 3 of 18 used".
     The inventory list pages by 9 too (spec: 6) - the well is 9 rows high for the slots anyway, so both pagers line up.
     Bindings: un:<slot> (0..59) and eq:<index into invIds> as before (absolute indexes, so a click acts on what the player saw),
     plus sp:prev / sp:next / ip:prev / ip:next; the page numbers are clamped in build(). Texts no longer say talisman.
  8. SERVER SETUP (kit tools/skyycfg.py 1.1): slots (1-60, default 18), notice.boosters, regenEverySeconds, the 1-column table
     boost (entries <Admin>.<stat>, four numbers, check= AccCfg.checkBoost: 4 numbers, no minus, whole numbers where the entry
     needs them, caps 100 for a percent / 1000 flat), line.Health .. line.Speed (live kill switches, on by default: Skyy's
     decision 6). The old bonus row is gone (migrated).
  9. COMMANDS AND BRIDGES: /accessories lines (every player, hytale:Adventurer: each line, its four rarities with the live numbers,
     switched off or not; admins also see the item ids), /accessories give <player> <item id> [amount] and /accessories givetier
     <player> <line> <rarity> [amount] (requirePermission skyyaccessories.admin + setPermissionGroups(new String[0]); raw argument
     text like SkyyGear's /gear give; <line> = admin name or the old keys Vitality / Endurance / Intelligence; <rarity> = Normal ..
     Legendary or 1-4; amount 1-64). Delivery: AccGiveTask hops to the TARGET player's world (world.execute, the SkyyGear
     GearMigrateTask pattern), refuses while the profile loads, SimpleItemContainer.addOrDropItemStack one at a time (storage
     first, the rest at their feet), counts the items before and after, "Gave N" to the admin. acc:fn:give = Function(Object[] {
     UUID, String id, Integer amount}) -> Integer given (booster table ids only; on the player's world thread it delivers at once,
     from any other thread it hops, returns -1 = QUEUED and logs; 0 = nothing given and nothing queued - part 2 review finding 2:
     a caller must never retry on -1). acc:defs = "name:key:tier:itemId:rarity:ap:sources" records joined by ",".
 10. PART 2 (spec 6.2; built into this same 0.5 - part 1 was never deployed, the SET pin is still 0.4.5):
     - FIVE NEW LINES, 20 items, admin give only (no recipe - Skyy: acquisition later): Brawler (Strength +3/+6/+9/+12), Runic
       (Magical Power, same), Stonehide (Defense, same), Razorfang (Crit Chance +2/+4/+6/+8 % AND Crit Damage +4/+8/+12/+16 % on one
       line), Feather (-10/-20/-30/-40 % fall damage and +5/+10/+15/+20 % jump height). Ids Skyy_Talisman_<Key>_T1..T4 (id style
       "T" in the table; the folded lines keep "word"), per-rarity looks of spec 5.6 (crystal style or four named items), tooltips.
     - COMBAT STATS -> SkyyGear through the gear:extra:<uuid> bridge (SkyyGear 0.1 / 0.1.1 / 0.1.2 read ONE String per player -
       "str:40,cc:10" - and no other mod writes it, so SkyyAccessories owns the key): AccGear.textOf sums the best rarity of each
       line (whole numbers, keys only from the allowlist str mp def cc cd, sorted), AccGear.publish writes it only when it changes,
       own try + log-once flag in the tick. Foreign text: overwritten with one WARN per player; changed again within 5 s after our
       overwrite (a second writer) or not a String (another format) = writing stops for that player until they rejoin or switch
       profile (profile:epoch changes), one more WARN. Removed when empty, for every player who left (AccTick, every 5 s) and on
       shutdown - only while it still holds our text (Map.remove(key, value)). combatToGear (Server Setup, live) off = removed.
     - FEATHER through the movement protocol: the accessories.talismans post now carries jump (+0.20 = x1.20 jump height) and
       fallDamage (-0.40 = 40 % less) in the pct layer. Proven live on the READER side: MoveSync.sync (this jar's copy, the code that
       applies Speed today) writes jumpForce from every source, and SkyySkills 0.4.8 (live) applies the summed fallDamage of every
       source in its fall filter (stat:owner:fallDamage) - the harness runs SkyySkills 0.4.8's own MoveSync against our posts. The
       line ships ON (Skyy's decision 6: no line ships switched off); an accessory never sent jump / fall before (UNVERIFIED in game).
     - THE BAG PAGE: the Bonuses well is 12 key / value rows in the kit's property-row look (propKey 150 px + propValue, one line,
       fixed widths - skyyui.property_row itself writes WrapMaxLines / FlexWeight, which are not in skyyui.PROBED): one row per line
       ("Brawler" / "+12 Strength", "Stamina" / "+6 max Stamina, +20% Stamina Regen", "Mana" / "switched off"), then the notes:
       "Combat stats" - not sent (combatToGear off) / need SkyyGear, which is not running / SkyyGear's Gear stats in combat is off
       (config:fn:SkyyGear get part.stats) / paused (the back-off); "Fall damage" - needs SkyySkills (no stat:owner:fallDamage).
     - Server Setup: 5 more line switches (generated from the table), combatToGear, 7 more boost. entries (Strength.flat,
       MagicPower.flat, Defense.flat, Crit.chancePct, Crit.damagePct, Feather.fallPct, Feather.jumpPct). AccCfg.migrate also APPENDS
       every missing 0.5 key to a file that already has boost. lines (a server that ran part 1): no slots change, no removal, logged.
     - Part 1 review fixes: AccStore.deliver counts addOrDropItemStack's true returns as DROPPED (the engine returns true only when a
       remainder was dropped) - handed out = arrived + dropped, via the testable AccStore.giveCount; the harness M section falls back
       to a synthetic 0.4.5 folder when the live one is already migrated; AccNotice tests notice.boosters before remembering the
       player and forgets them on leave; the legacy tooltip line; canEquipK / equipK compare with the BEST slot of the line and swap
       the lowest (duplicates from stashK); one INFO line per player when the restamp changed stacks; boostIn names the decimals.
     - Part 2 review fixes: (1) max Health, max Stamina and max Mana each have their own log-once flag (F_HEALTH / F_STAMINA /
       F_MANA; one shared F_POOLS let a Health failure hide a later Stamina or Mana failure). (2) acc:fn:give off the target's world
       thread returns -1 (queued) instead of 0 once world.execute took the give (AccGiveTask.queued), so a loot-pass caller that
       retries on 0 cannot give twice; 0 now always means nothing was given and nothing is queued. Deploy notes (no code change):
       the skyyacc_health / skyyacc_stamina / skyyacc_mana MAX modifiers are saved with the character and never removed on leave or
       shutdown (as in 0.4.5 and SkyySkills: a relog keeps them, the next tick corrects them) - removing or disabling the mod leaves
       the last flat bonus on saved characters until a later admin cleanup command; the Stamina Regen top-up is a percent of the
       Stamina asset's own ADDITIVE regen entries only (RegeneratingModifier multipliers and armor regen entries are not in the
       rate), so quoted refill times hold for the vanilla numbers.

Build checks added (the build stops on each): a stat kind outside STAT_KINDS; a line without exactly 4 rarities Normal..Legendary /
4 numbers per stat / unique ids / unique icons; any item with a recipe above Legendary; the 20 modern, 15 old legacy and 5 _Legendary
ids fail to round-trip through the Python mirror of tierOf / familyOf / modernOf, or the equip swap order differs from 0.4.5 other than
_Legendary now tying with the tier-4 ids (_Epic, _Artifact); a name that is not "<Rarity> <Line> Accessory"; Vitality / Endurance /
Intelligence / Talisman in a lang value, a Server Setup label / help, or a Java string literal outside ids (AST scan of the script);
a missing look path; a quality asset whose field set differs from vanilla Common.json or with QualityValue >= 8; a missing engine
call of the Stamina Regen top-up (B.probe); the page not filling its 1210 x 952 body exactly (SUI.fit), SUI.check_page on sample states.
Part 2 adds: the 20 _T<n> ids round-trip through the id mirror, have no recipe and never start with Skyy_Accessory_ or end in a
legacy word; a stat kind that feeds gear:extra outside str / mp / def / cc / cd (never dmg, element damage, tdmg, spd, stam or a
"later" key); whole numbers for the gear:extra kinds; a line without its bag-page text or tooltip; more lines than the Bonuses well
holds (lines + 2 notes <= 12).
"""
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.5.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.5"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


def cut(a, b, new=""):
    """replace everything from anchor a (included) up to anchor b (kept) with new; returns the text that was cut"""
    global s
    assert s.count(a) == 1, "cut start count %d: %s" % (s.count(a), a[:120])
    assert s.count(b) == 1, "cut end count %d: %s" % (s.count(b), b[:120])
    i, j = s.index(a), s.index(b)
    assert i < j, "cut anchors out of order: %s / %s" % (a[:60], b[:60])
    old = s[i:j]
    s = s[:i] + new + s[j:]
    return old


def block(a, b):
    """the text from anchor a (included) to anchor b (excluded) of the CURRENT source (for unchanged-block asserts)"""
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


REG0 = s.count("registerCommand(")
# blocks that come out of this patch byte-identical (0.4.5's code the fold does not touch)
KEEP = [block('JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"', 'for c, m in ((ACM, "requirePermission"), (ACM, "addSubCommand")'),
        block("# (benchId, bench item id, display name, tiers, [upgrade materials to reach T2, T3, ...])", 'BAG = "Skyy_Accessory_Bag"'),
        block("dfs.addMethod(CtNewMethod.make(\"\"\"\npublic static boolean isAccessory(String id) {",
              "dfs.addMethod(CtNewMethod.make(\"\"\"\npublic static int tierOf(String id) {"),
        block("dfs.addMethod(CtNewMethod.make(\"\"\"\npublic static boolean hasOmni(String[] s) {",
              "# highest talisman tier per family (index = FAMILIES) among the bag slots"),
        block("# 0.4: bench accessory ids for the acc:has bridge value = EXACTLY ONE entry per bench id",
              "# ================= AccStore ================="),
        block("st_.addMethod(CtNewMethod.make(\"\"\"\npublic static void warn(String msg) {", "# 0.4.1: the bag of storage key k (bags/<k>.properties); lock stays per player"),
        block("# 0.4.1: the bag of the player's ACTIVE profile", "# 0.4.1: saves the bag of storage key k (the key the caller resolved once), then republishes the active profile"),
        block("st_.addMethod(CtNewMethod.make(\"\"\"\npublic static void save(java.util.UUID u) {",
              "# would equip(u, id) take the item? same rule as equip - asked BEFORE the item leaves the inventory"),
        # (canEquipK / equipK in between: part 1 review finding 5 - they now compare with the BEST slot of the line)
        block("st_.addMethod(CtNewMethod.make(\"\"\"\npublic static String equip(java.util.UUID u, String id) {",
              "# 0.4.3 review fix: SkyyCooking's LIVE Campfire accessory factors."),
        block("# 0.4.3 review fix: SkyyCooking's LIVE Campfire accessory factors.", "# ================= AccCfg (0.4.4)"),
        block("# ================= AccFn (bridge function acc:fn:has) =================", "# ================= AccPage ================="),
        block("page.addMethod(CtNewMethod.make(\"\"\"\npublic static String safe(String t) {", "# ================= AccPage look (0.4.5)"),
        block("# giveBack: 0 = back in the inventory", "page.addMethod(CtNewMethod.make(f\"\"\"\npublic void handleDataEvent("),
        block("fac.addInterface(pool.get(\"java.util.function.Function\"))", "# ================= /accessories reload (0.4.4, server admins only)"),
        block("# ================= MoveSync: the shared Skyy movement protocol", "# ================= AccEffects: talisman stats"),
        block("def item(iid, icon, quality, recipe_in, bench_req, page_id=None, visual=None):", "QUAL = [\"Common\", \"Common\", \"Uncommon\""),
        ]
# 0.4.5 methods the new AccCfg keeps word for word (spliced from the old source, asserted below)
_CFG_OLD = block("# ================= AccCfg (0.4.4)", "# ================= the admin config kit")


def _cfg_src(start):
    """one r\"\"\"...\"\"\" Java method of 0.4.5's AccCfg list, by the line that starts it"""
    i = _CFG_OLD.index('r"""\n' + start)
    j = _CFG_OLD.index('""",', i)
    return _CFG_OLD[i:j + 4]


CFG_KEEP = [_cfg_src(x) for x in ("public static void info(String msg) {", "public static void writeDefaults() {",
                                   "public static double num(String t) {", "public static boolean sameRow(double[] a, double[] b) {",
                                   "public static String dtext(double v) {", "public static String rowText(double[] r) {",
                                   "public static int intIn(String v, int def, int lo, int hi, String key) {",
                                   "public static String reload() {")]
_REL_OLD = block("# ================= /accessories reload (0.4.4, server admins only) =================",
                 "# ================= /accessories =================")
_CMD_ANCHOR = 'cmd.addMethod(CtNewMethod.make(f"""\nprotected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{\n  try {{\n    {PLA} player'
_CMD_EXEC = block(_CMD_ANCHOR, "tick.addInterface(pool.get(\"java.lang.Runnable\"))")
_EFF_KEEP = [block("eff.addConstructor(CtNewConstructor.make(\"public AccEffects() { super(); }\", eff))",
                   "# set (pct > 0) or remove (pct == 0) our MAX modifier on one stat")]
# 0.4.5's speed(): part 2 replaces it with move() (Speed + Feather's jump / fall in the same post); asserted to exist, then dropped
_EFF_SPEED_OLD = block("# Speed (0.3): the talisman bonus is POSTED as source \"accessories.talismans\"",
                       "eff.addMethod(CtNewMethod.make(f\"\"\"\npublic void tick(")
assert '{PKG}.MoveSync.post(u, "accessories.talismans", "pct", bonus, 0.0f, 0.0f);' in _EFF_SPEED_OLD

# ---------------------------------------------------------------- header / version
rep('''"""SkyyAccessories 0.4.5 - build script (derived from 0.4.4 by tools/acc_0_4_5_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.5.py            -> SkyyAccessories/SkyyAccessories-0.4.5.jar
       python build_skyyaccessories_0.4.5.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.5: THE VANILLA LOOK''', '''"""SkyyAccessories 0.5 - build script (derived from 0.4.5 by tools/acc_0_5_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.py            -> SkyyAccessories/SkyyAccessories-0.5.jar
       python build_skyyaccessories_0.5.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.py             (bare JVM -Xverify:all, table, fold, config migration on a scratch copy, paging)
0.5: BOOSTER ACCESSORIES, PARTS 1 AND 2 (Skyy's decisions, OPEN-QUESTIONS LOCKED 2026-09-30; research/Booster-Accessories-Spec.md 6.1
     and 6.2; full notes in tools/acc_0_5_patch.py):
     - ONE booster table (BOOSTERS -> flat 1-D arrays in AccDefs): line, stats, four numbers per stat (Normal..Legendary), item ids,
       looks, source words. Five folded lines: Health, Stamina, Mana, Regeneration, Speed. Part 2: five new lines (admin give only,
       ids Skyy_Talisman_<Key>_T1..T4): Brawler (Strength), Runic (Magical Power), Stonehide (Defense), Razorfang (Crit Chance and
       Crit Damage), Feather (less fall damage, higher jumps).
     - combat stats go to SkyyGear as ONE text per player in gear:extra:<uuid> (SkyyAccessories owns the key: whole numbers, keys
       str mp def cc cd, written only on change, a second writer = back off for that player, removed on leave / shutdown); Feather's
       jump and fall ride the accessories.talismans movement post (fall damage is applied by SkyySkills).
     - the 25 talismans FOLD into those lines: same ids, names "<Rarity> <Line> Accessory", new numbers (Health / Stamina flat, Mana %
       with a floor, Regeneration lower, Speed 2.5..10 %), _Epic = Legendary, the old _Legendary = a legacy id (no recipe, counts as
       Legendary, stored as _Epic); only the best rarity of a line counts; "+stamina" = max Stamina AND a Stamina Regen top-up that
       only flows while vanilla's own refill flows (never while sprinting, gliding or blocking).
     - GEAR RARITIES for every accessory: six Skyy_Acc_* qualities (Fabled / Mythic shipped unused), bench I Normal, II Unique,
       III Rare, IV+ Legendary, the Omni Legendary, the bag item Unique; a world-thread restamp fixes saved stacks.
     - config migration (one atomic write, config.properties.pre-0.5.bak, config-changes.log lines, slots 9 -> 18), a one-time chat
       notice per player (notices.properties), Server Setup rows for every number (boost table, 5 line switches, notice switch).
     - the bag: 60 storage slots (slot0..8 in bags/<key>.properties as before, slot9..59 in bags/<key>.more.properties, so a rollback
       to 0.4.5 hides them instead of deleting them), 18 by default; the page shows 9 rows per page with pagers.
     - /accessories lines (players), /accessories give | givetier (admins), bridges acc:defs + acc:fn:give; the bag page lists the
       active bonus of each line and says when SkyyGear / its combat stats / SkyySkills are missing for a line.
     DO NOT ROLL BACK BELOW 0.5: restamped stacks point at Skyy_Acc_* qualities that 0.4.5 does not ship (stale look, UNVERIFIED).
0.4.5 notes:
0.4.5: THE VANILLA LOOK''')
rep('VERSION = "0.4.5"\n', 'VERSION = "0.5"\n')

# ---------------------------------------------------------------- probes for the new engine calls
rep('''for c, m in ((ACM, "requirePermission"), (ACM, "addSubCommand"), (ACM, "setPermissionGroups"), (PR, "getUsername"), (PR, "getUuid"),
             (PR, "sendMessage")):
    B.probe(pool, c, m)
''', '''for c, m in ((ACM, "requirePermission"), (ACM, "addSubCommand"), (ACM, "setPermissionGroups"), (PR, "getUsername"), (PR, "getUuid"),
             (PR, "sendMessage")):
    B.probe(pool, c, m)
# 0.5: the Stamina Regen top-up (research/Booster-Accessories-Spec.md 5.4.1 - every call read in HytaleServer.jar bytecode), the quality
# restamp (the SkyySacks 0.7.7 calls), the admin give (addOrDropItemStack, the SkyyCooking / SkyyExploration call; the target's world
# thread: Store.isInThread + World.execute), /accessories lines (PlayerRef.hasPermission) and the raw command text (SkyyGear /gear give)
RGV = "com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue"
RGN = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating"
RGT = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating$RegenType"
CND = "com.hypixel.hytale.server.core.modules.entity.condition.Condition"
TMR = "com.hypixel.hytale.server.core.modules.time.TimeResource"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
for c, m in ((ESV, "getRegeneratingValues"), (RGV, "getRegenerating"), (RGN, "getRegenType"), (RGN, "getAmount"), (RGN, "getInterval"),
             (RGT, "ADDITIVE"), (CND, "allConditionsMet"), (TMR, "getResourceType"), (TMR, "getNow"), (ST, "getResource"),
             (ESV, "get"), (ESV, "getMax"), (ESM, "addStatValue"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItem"),
             (IS, "getQuantity"), (ITM, "getQualityIndex"), (IC, "setItemStackForSlot"), (SIC, "addOrDropItemStack"),
             (INV, "getCombinedStorageHotbarBackpack"), (ST, "isInThread"), (REF, "getStore"), (PR, "getReference"),
             (PR, "getWorldUuid"), (PR, "hasPermission"), (PR, "isValid"), (UNI, "getPlayer"), (UNI, "getWorld"), (WLD, "execute"),
             (ACM, "setAllowsExtraArguments"), (CTX, "getInputString"), (MSG, "raw"), (MSG, "color")):
    B.probe(pool, c, m)
''')

# ---------------------------------------------------------------- the new classes
rep('''rcmd = pool.makeClass(PKG + ".AccReloadCmd", pool.get(APC))    # 0.4.4: /accessories reload (server admins only)
''', '''rcmd = pool.makeClass(PKG + ".AccReloadCmd", pool.get(APC))    # 0.4.4: /accessories reload (server admins only)
lcmd = pool.makeClass(PKG + ".AccLinesCmd", pool.get(APC))     # 0.5: /accessories lines (every player)
gcmd = pool.makeClass(PKG + ".AccGiveCmd", pool.get(APC))      # 0.5: /accessories give (server admins only)
tcmd = pool.makeClass(PKG + ".AccGiveTierCmd", pool.get(APC))  # 0.5: /accessories givetier (server admins only)
adm  = pool.makeClass(PKG + ".AccAdmin")                         # 0.5: the give helpers (argument text, player lookup, acc:fn:give)
gtk  = pool.makeClass(PKG + ".AccGiveTask")                      # 0.5: one give, run on the TARGET player's world thread
gfn  = pool.makeClass(PKG + ".AccGiveFn")                        # 0.5: bridge acc:fn:give
rtk  = pool.makeClass(PKG + ".AccRestampTask")                   # 0.5: the quality restamp on a player's world thread
note = pool.makeClass(PKG + ".AccNotice")                        # 0.5: the one-time chat notice per player
gear = pool.makeClass(PKG + ".AccGear")                          # 0.5 part 2: gear:extra publisher, bag page notes, bridge clean-up
''')
assert "gear = " not in OLD and "AccGear" not in OLD

# ---------------------------------------------------------------- R1: constants, rarity, THE BOOSTER TABLE, config text
OLD_R1 = cut('BAG = "Skyy_Accessory_Bag"\n', "# ================= AccDefs =================", "@@R1@@")
# the recipes of the folded lines come from 0.4.5's TALISMANS rows (the Common..Epic steps; the old Epic -> Legendary step goes away)
_ns = {}
exec(compile(OLD_R1[OLD_R1.index("TALISMANS = ["):OLD_R1.index("assert all(len(t[4]) == 5")], "0.4.5 TALISMANS", "exec"), _ns)
OLD_TALISMANS = _ns["TALISMANS"]
assert [t[0] for t in OLD_TALISMANS] == ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed"]


def _recipes_py(recs, indent):
    out = []
    for r in recs:
        out.append(indent + "[" + ", ".join('("%s", %d)' % (m, q) for m, q in r) + "],")
    return "\n".join(out)


R1 = r'''BAG = "Skyy_Accessory_Bag"
OMNI = "Skyy_Accessory_Omni"   # 0.4: counts as every bench accessory at max tier (own group "Omni"); 0.5: Legendary (crafted, never Mythic)
CAP = 60          # 0.5: bag STORAGE slots (Skyy 2026-09-30: "bag 18 slots to start, up to 60"); AccStore.CAP, the page, un:<i>
MAIN_SLOTS = 9    # 0.5: slot0..slot8 stay in bags/<key>.properties - the file 0.4.x reads and rewrites whole - and slot9..slot59 go
                  # into bags/<key>.more.properties, which 0.4.x never opens: a rollback hides the extra slots, it cannot delete them
SLOTS_DEF = 18    # 0.5: config row slots default (1..CAP); it limits NEW equips only, as in 0.4.4
PAGE_ROWS = 9     # 0.5: bag page rows per page - the bag slots and the accessories in the inventory, each with the kit pager
BONUS_MAX = 12    # 0.5: the Bonuses well: two columns of 6 short lines
REGEN_EVERY = 2
REGEN_MAX = 30
assert MAIN_SLOTS == 9 and 1 <= SLOTS_DEF <= CAP == 60 and PAGE_ROWS == 9 and BONUS_MAX == 12

# ---- BOOSTER TABLE START (SkyyAccessories/test_skyyaccessories_0.5.py execs this block: plain Python - no kit, no JVM, no files)
# 0.5 rarity (Skyy 2026-09-30: "they are all accessories. but they come in the same rarity tiers as weapons and armor"; spec 1.2 / 5.2).
# ID words and display rarities are SEPARATE: the id word "Epic" means Legendary on screen, and "Legendary" ending an id is a legacy word.
ID_WORD = ["", "Common", "Uncommon", "Rare", "Epic"]            # tier 1..4: parse and build ids ONLY (the Workbench ladder)
LEGACY_WORDS = [("Talisman", 2), ("Ring", 3), ("Artifact", 4), ("Legendary", 4)]   # old id tails -> tier; modernOf -> the ID_WORD id
DISPLAY = ["", "Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic"]         # rarity 1..6 = everything players see
ACC_AP = [0, 10, 13, 16, 19, 22, 25]   # Accessory Power by rarity (spec 1.3): a build constant in acc:defs only - no setting, not shown
MAX_LINE_RARITY = 4                    # a line stops at Legendary; Fabled / Mythic are rare finds for later (spec 4.1)
SOURCE_WORDS = ("Craft", "Drop", "Chest", "Combine", "Boss")   # placeholder source words for the later loot pass (spec 2.3)
# THE BOOSTER TABLE (spec 2, 5.4): one row per line. Everything else - the AccDefs arrays, config entries, Server Setup rows, the
# effect tick, tooltips, item assets, /accessories lines, acc:defs and the harness - comes from it.
# (family key = item ids, admin name = config / commands / acc:defs, line name = what players see,
#  look: crystal colour + Legendary icon item (every rarity the colour's crystal fragment model; icons fragments / small cluster /
#        large cluster / that item) OR None + [4 items] (each rarity copies that vanilla item's model and icon, spec 5.6),
#  stats [(stat, kind, [Normal, Unique, Rare, Legendary])], source words per rarity, flavour line,
#  recipes [Normal inputs, Unique extra, Rare extra, Legendary extra] - each upgrade also takes the rarity below, at a Workbench -
#        or None (no recipe: admin give only until the loot pass, Skyy's decision 5),
#  id style "word" = Skyy_Talisman_<Key>_<Common|Uncommon|Rare|Epic> (the folded lines, their legacy ids kept) or "T" =
#        Skyy_Talisman_<Key>_T1..T4 (the new lines, spec 5.3))
SRC_FOLDED = ["Craft", "Craft+Drop", "Craft+Chest", "Craft+Boss"]
BOOSTERS = [
    ("Vitality", "Health", "Health", "Red", "Rock_Gem_Ruby",
     [("flat", "maxHealth", [6, 12, 18, 24])], SRC_FOLDED, "A warm pulse that steadies the heart.", [
@@REC0@@
     ], "word"),
    ("Endurance", "Stamina", "Stamina", "Yellow", "Rock_Gem_Topaz",
     [("flat", "maxStamina", [1.5, 3, 4.5, 6]), ("regenPct", "staminaRegen", [5, 10, 15, 20])], SRC_FOLDED,
     "It hums faster the harder you breathe.", [
@@REC1@@
     ], "word"),
    ("Intelligence", "Mana", "Mana", "Blue", "Rock_Gem_Sapphire",
     [("pct", "manaPct", [6, 12, 18, 24]), ("floor", "manaFloor", [1, 2, 3, 4])], SRC_FOLDED,
     "Cold to the touch, and full of quiet thoughts.", [
@@REC2@@
     ], "word"),
    ("Regeneration", "Regeneration", "Regeneration", "Green", "Rock_Gem_Emerald",
     [("pct", "healPct", [0.25, 0.5, 0.75, 1.0])], SRC_FOLDED, "Moss grows back on it overnight.", [
@@REC3@@
     ], "word"),
    ("Speed", "Speed", "Speed", "Cyan", "Rock_Gem_Zephyr",
     [("pct", "speedPct", [2.5, 5, 7.5, 10])], SRC_FOLDED, "The wind always seems to be at your back.", [
@@REC4@@
     ], "word"),
    # ---- part 2 (spec 2.3, 2.4): no recipes, ids _T1.._T4
    ("Strength", "Strength", "Brawler", None,
     ["Ingredient_Bone_Fragment", "Ingredient_Sinue_Cindersinue", "Ingredient_Fire_Essence", "Ingredient_Voidheart"],
     [("flat", "str", [3, 6, 9, 12])], ["Drop", "Combine", "Craft", "Boss"], "Scuffed wraps from a hundred fights.", None, "T"),
    ("MagicPower", "MagicPower", "Runic", "Purple", "Rock_Gem_Voidstone",
     [("flat", "mp", [3, 6, 9, 12])], ["Chest", "Combine", "Craft", "Boss"], "Faint runes crawl across it when you cast.", None, "T"),
    ("Defense", "Defense", "Stonehide", "White", "Rock_Crystal_Iridescent_Large",
     [("flat", "def", [3, 6, 9, 12])], ["Drop", "Combine", "Craft", "Boss"], "Heavy as a boulder, and just as stubborn.", None, "T"),
    ("Crit", "Crit", "Razorfang", "Pink", "Rock_Crystal_Iridescent_Medium",
     [("chancePct", "cc", [2, 4, 6, 8]), ("damagePct", "cd", [4, 8, 12, 16])], ["Chest", "Combine", "Craft", "Boss"],
     "Its edge always finds the gap in the armor.", None, "T"),
    ("Feather", "Feather", "Feather", None,
     ["Ingredient_Feathers_Light", "Ingredient_Feathers_Blue", "Ingredient_Ice_Essence", "Ingredient_Motes_Light"],
     [("fallPct", "fallPct", [10, 20, 30, 40]), ("jumpPct", "jumpPct", [5, 10, 15, 20])], ["Craft", "Craft", "Chest", "Chest"],
     "Lighter than it has any right to be.", None, "T"),
]
# THE STAT ALLOWLIST (spec 1.4; Skyy's decision 6: "stats that do nothing yet must NEVER be on a booster"): kind -> (config unit,
# whole numbers only, cap, what applies it in game). A row using any other kind stops the build. Never dmg, element damage, tdmg,
# spd or stam through gear:extra, or a key SkyyGear marks "later" (it accepts them and does nothing - a booster would lie).
STAT_KINDS = {
    "maxHealth":    ("flat", False, 1000, "stat map key skyyacc_health (StaticModifier MAX, ADDITIVE)"),
    "maxStamina":   ("flat", False, 1000, "stat map key skyyacc_stamina (StaticModifier MAX, ADDITIVE)"),
    "staminaRegen": ("pct",  False, 100,  "the Stamina Regen top-up: addStatValue(Stamina) while vanilla's own refill runs (AccEffects.staminaRegen)"),
    "manaPct":      ("pct",  False, 100,  "stat map key skyyacc_mana (MAX, ADDITIVE): percent of the flat Mana, never less than manaFloor"),
    "manaFloor":    ("flat", False, 1000, "the least the Mana line adds (with manaPct in the same line)"),
    "healPct":      ("pct",  False, 100,  "addStatValue(Health) every regenEverySeconds, percent of max Health"),
    "speedPct":     ("pct",  False, 100,  "movement protocol source accessories.talismans, layer pct, speed"),
    # part 2: SkyyGear 0.1 (live) reads gear:extra:<uuid> on every hit (VERIFIED: GearStats.totals(..., withExtra = true) in the
    # offence and Defense handlers); SkyyGear floors each part, so these take whole numbers only
    "str":          ("flat", True,  1000, "gear:extra key str - SkyyGear: +1% damage per point (melee, arrows, thrown weapons, staff melee)"),
    "mp":           ("flat", True,  1000, "gear:extra key mp - SkyyGear: +1% spell damage per point"),
    "def":          ("flat", True,  1000, "gear:extra key def - SkyyGear: mob and player hits x 100 / (100 + Defense)"),
    "cc":           ("pct",  True,  100,  "gear:extra key cc - SkyyGear: Crit Chance in percent (base 0)"),
    "cd":           ("pct",  True,  100,  "gear:extra key cd - SkyyGear: Crit Damage in percent (rides with cc on one line)"),
    "fallPct":      ("pct",  False, 100,  "movement protocol source accessories.talismans, fallDamage (pct layer, negated) - applied by SkyySkills"),
    "jumpPct":      ("pct",  False, 100,  "movement protocol source accessories.talismans, jump (pct layer) - applied by MoveSync.sync"),
}
# the gear:extra keys (spec 5.4): kind -> SkyyGear stat key; the ONLY keys SkyyAccessories may write (lsteal joins in wave 2)
GEAR_ALLOW = ("str", "mp", "def", "cc", "cd")
GEAR_KEYS = sorted(GEAR_ALLOW)                  # the text lists them in this order: "cc:8,cd:16,def:12,mp:12,str:12"
STAT_GEAR = {"str": "str", "mp": "mp", "def": "def", "cc": "cc", "cd": "cd"}
GEAR_NEVER = ("dmg", "tdmg", "spd", "stam", "fEarth", "fFire", "fWater", "fAir", "fThunder", "lsteal")
# kinds that only ride along with another kind of the same line (one tooltip template, one bag-page part with it)
RIDERS = {"manaFloor": "manaPct", "cd": "cc", "jumpPct": "fallPct", "staminaRegen": "maxStamina"}
ENTRIES = []      # config entries "<Admin>.<stat>" in table order: (key, line index, kind, [Normal, Unique, Rare, Legendary])
for _li, _b in enumerate(BOOSTERS):
    for _st, _kind, _vals in _b[5]:
        ENTRIES.append(("%s.%s" % (_b[1], _st), _li, _kind, list(_vals)))
E = dict((_e[0], _i) for _i, _e in enumerate(ENTRIES))
KIND_E = dict((_e[2], _i) for _i, _e in enumerate(ENTRIES))
LI = dict((_b[1], _i) for _i, _b in enumerate(BOOSTERS))


def booster_id(b, t):
    """the item id of rarity t (1..4) of table row b (its id style)"""
    return "Skyy_Talisman_%s_%s" % (b[0], ID_WORD[t]) if b[9] == "word" else "Skyy_Talisman_%s_T%d" % (b[0], t)


LINE_IDS = [booster_id(_b, _t) for _b in BOOSTERS for _t in range(1, 5)]   # [line * 4 + tier - 1]
LINE_SRC = [_b[6][_t - 1] for _b in BOOSTERS for _t in range(1, 5)]
BOOST_DEF = [",".join("%g" % _v for _v in _e[3]) for _e in ENTRIES]
FOLDED = [_b for _b in BOOSTERS if _b[9] == "word"]      # the 0.4.x lines: word ids, legacy ids, Workbench recipes
E_GEAR = [STAT_GEAR.get(_e[2], "") for _e in ENTRIES]    # per entry: its gear:extra key or ""
COMBAT_LINES = [_b[2] for _li, _b in enumerate(BOOSTERS) if any(E_GEAR[_i] for _i, _e in enumerate(ENTRIES) if _e[1] == _li)]


def _table_checks():
    """the table rules (spec 6.1 / 6.2 build checks); the harness runs them again"""
    import re as _re
    fams, admins, names, kinds = [b[0] for b in BOOSTERS], [b[1] for b in BOOSTERS], [b[2] for b in BOOSTERS], []
    for lst, what in ((fams, "family key"), (admins, "admin name"), (names, "line name")):
        assert len(set(lst)) == len(lst), "duplicate %s: %s" % (what, lst)
    words = [w for w in ID_WORD[1:]] + [w for w, _t in LEGACY_WORDS]
    for b in BOOSTERS:
        fam, adm, line, crystal, gem, stats, src, flavour, recipes, style = b
        assert _re.match(r"^[A-Z][A-Za-z]+$", fam) and not any(fam.endswith(w) for w in words), "family key %r: CamelCase, no _, " \
            "not ending in an id word or legacy word" % fam
        assert _re.match(r"^[A-Z][A-Za-z]+$", adm) and _re.match(r"^[A-Z][A-Za-z]+$", line), (adm, line)
        assert len(src) == MAX_LINE_RARITY and all(all(w in SOURCE_WORDS for w in x.split("+")) for x in src), (fam, src)
        assert style in ("word", "T"), (fam, style)
        if style == "word":
            assert recipes is not None and len(recipes) == MAX_LINE_RARITY, (fam, "a folded line keeps its 4 Workbench steps")
        else:
            assert recipes is None, (fam, "new lines have no recipe (Skyy: acquisition later - admin give only)")
        if crystal is None:
            assert isinstance(gem, list) and len(gem) == MAX_LINE_RARITY and len(set(gem)) == 4, (fam, "4 look items, one per rarity")
        else:
            assert _re.match(r"^[A-Z][a-z]+$", crystal) and isinstance(gem, str), (fam, crystal, gem)
        assert flavour and "." in flavour and all(ord(ch) < 128 for ch in flavour), flavour
        for st, kind, vals in stats:
            assert kind in STAT_KINDS, "%s uses the stat kind %r, which is not in the allowlist STAT_KINDS (spec 1.4)" % (fam, kind)
            unit, whole, cap, _how = STAT_KINDS[kind]
            assert _re.match(r"^[a-z][A-Za-z]*$", st), st
            assert len(vals) == MAX_LINE_RARITY, "%s.%s needs exactly 4 numbers (Normal..Legendary): %r" % (adm, st, vals)
            for v in vals:
                assert 0 <= v <= cap and round(v, 2) == v and (not whole or v == int(v)), (adm, st, v)
            assert list(vals) == sorted(vals) and vals[0] > 0, "%s.%s must grow with the rarity: %r" % (adm, st, vals)
            kinds.append(kind)
        ks = [k for _s, k, _v in stats]
        for rider, main in RIDERS.items():
            assert (rider in ks) <= (main in ks), "%s goes with %s in one line" % (rider, main)
        assert len([k for k in ks if k not in RIDERS]) == 1, "%s: exactly one main stat (the rest ride along): %s" % (adm, ks)
    assert len(set(kinds)) == len(kinds), "one line per stat kind (spec 1.1: one line per stat)"
    assert len(set(LINE_IDS)) == len(LINE_IDS) == 4 * len(BOOSTERS), "two rarities share an id"
    assert len(set(e[0] for e in ENTRIES)) == len(ENTRIES)
    assert ACC_AP[1:5] == [10, 13, 16, 19] and all(10 <= a <= 25 for a in ACC_AP[1:]), ACC_AP   # locked +10 to +25 (locks 111-113)
    assert DISPLAY[1:5] == ["Normal", "Unique", "Rare", "Legendary"] and MAX_LINE_RARITY == 4
    # part 2: gear:extra - only the allowlist, whole numbers, never a key SkyyGear keeps for weapons / armor or "later"
    for k, g in STAT_GEAR.items():
        assert g in GEAR_ALLOW and g not in GEAR_NEVER and STAT_KINDS[k][1], "gear:extra key %r is outside str mp def cc cd" % g
    assert set(GEAR_ALLOW) == set(STAT_GEAR.values()) and not set(GEAR_ALLOW) & set(GEAR_NEVER)
    assert all(g == "" or g in GEAR_ALLOW for g in E_GEAR)
    # part 2 ids: _T1.._T4, never the bench prefix, never ending in a legacy word (modernOf would rebuild them)
    for b in BOOSTERS:
        if b[9] != "T":
            continue
        for t in range(1, 5):
            i = booster_id(b, t)
            assert i.startswith("Skyy_Talisman_") and not i.startswith("Skyy_Accessory_") and i.endswith("_T%d" % t), i
            assert not any(i.endswith("_" + w) for w, _t in LEGACY_WORDS), i
    assert len(BOOSTERS) + 2 <= BONUS_MAX, "the Bonuses well holds one row per line + 2 notes (%d lines)" % len(BOOSTERS)


_table_checks()
# ---- BOOSTER TABLE END
assert [_b[0] for _b in BOOSTERS] == ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed", "Strength", "MagicPower",
                                     "Defense", "Crit", "Feather"], "the five folded lines + the five part 2 lines"
assert [_b[0] for _b in FOLDED] == ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed"]
assert BOOST_DEF == ["6,12,18,24", "1.5,3,4.5,6", "5,10,15,20", "6,12,18,24", "1,2,3,4", "0.25,0.5,0.75,1", "2.5,5,7.5,10",
                     "3,6,9,12", "3,6,9,12", "3,6,9,12", "2,4,6,8", "4,8,12,16", "10,20,30,40", "5,10,15,20"], BOOST_DEF
assert [_e[0] for _e in ENTRIES][7:] == ["Strength.flat", "MagicPower.flat", "Defense.flat", "Crit.chancePct", "Crit.damagePct",
                                         "Feather.fallPct", "Feather.jumpPct"], "the spec 5.8 part 2 entry names"
assert COMBAT_LINES == ["Brawler", "Runic", "Stonehide", "Razorfang"], COMBAT_LINES
# the numbers are exact float32 values (the loader computes (float) of the parsed text; the jar literals are "%.4ff")
import struct as _struct
def _f32(x):
    return _struct.unpack("<f", _struct.pack("<f", x))[0]
assert all(_f32(v) == v for _e in ENTRIES for v in _e[3]), "a booster default is not exact in float32"
# the rarity look: frame art = SkyyGear's Skyy_Gear_* table (tooltip + arrow texture quality, slot texture quality, drop particle);
# colours = the kit's rarity palette (the same hexes as SkyyGear / SkyySacks); the six quality assets Skyy_Acc_<Rarity>
QUAL_IDS = [""] + ["Skyy_Acc_" + _r for _r in DISPLAY[1:]]
QUAL_ART = {"Normal": ("Common", "Common", "Drop_Common"), "Unique": ("Legendary", "Legendary", "Drop_Legendary"),
            "Rare": ("Epic", "Epic", "Drop_Epic"), "Legendary": ("Rare", "Rare", "Drop_Rare"),
            "Fabled": ("Common", "Developer", "Drop_Legendary"), "Mythic": ("Epic", "Epic", "Drop_Epic")}
RARITY_COLORS = ["#ffffff"] + [SUI.RARITY[_r] for _r in DISPLAY[1:]]
BENCH_RARITY = [0, 1, 2, 3, 4, 4, 4, 4]   # bench tier I Normal, II Unique, III Rare, IV and up Legendary (crafted: stops at Legendary)


def _gear_art_check():
    """SkyyAccessories ships its own qualities (every Skyy mod works alone), but the look must match SkyyGear's ladder"""
    import re as _re, glob as _glob
    def _v(p):
        m = _re.search(r"_(\d+(?:\.\d+)*)\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(_glob.glob(os.path.join(HERE, "..", "SkyyGear", "build_skyygear_*.py")), key=_v)
    if not found:
        print("note: no SkyyGear build script next to this mod - the Skyy_Acc_* frame art is not cross-checked")
        return
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    rows = _re.findall(r'^\s*\("(\w+)", "(\w+)", "(#[0-9A-Fa-f]{6})", "#[0-9A-Fa-f]{6}", "(\w+)", "(\w+)", "(\w+)"\),', txt, _re.M)
    got = dict((nm, (col.lower(), (tt, sl, pt))) for _rid, nm, col, tt, sl, pt in rows)
    for r in DISPLAY[1:]:
        if r not in got:
            raise SystemExit("0.5: %s has no %s row in its RARITIES table - update _gear_art_check" % (os.path.basename(found[-1]), r))
        if got[r][1] != QUAL_ART[r] or got[r][0] != SUI.RARITY[r].lower():
            raise SystemExit("0.5: the %s look differs from %s (%r vs %r) - update QUAL_ART" % (r, os.path.basename(found[-1]), got[r], (SUI.RARITY[r], QUAL_ART[r])))
    print("rarity look matches %s (%s)" % (os.path.basename(found[-1]), ", ".join(DISPLAY[1:])))


_gear_art_check()

# ---- the Python mirror of the Java id rules (AccDefs.tailTier / tierOf / familyOf / isLegacy / modernOf / rarityOf) + the fold checks
def py_family(iid):
    tail = iid[len("Skyy_Talisman_"):]
    k = tail.rfind("_")
    return tail[:k] if k > 0 else tail
def py_tail_tier(iid):
    w = iid[iid.rfind("_") + 1:]
    return int(w[1:]) if len(w) >= 2 and w[0] == "T" and w[1:].isdigit() else -1
def py_tier(iid):
    if py_tail_tier(iid) > 0:
        return py_tail_tier(iid)
    for r in range(len(ID_WORD) - 1, 0, -1):
        if iid.endswith("_" + ID_WORD[r]):
            return r
    for w, t in LEGACY_WORDS:
        if iid.endswith("_" + w):
            return t
    return 1
def py_legacy(iid):
    return py_tail_tier(iid) <= 0 and any(iid.endswith("_" + w) for w, _t in LEGACY_WORDS)
def py_modern(iid):
    return "Skyy_Talisman_%s_%s" % (py_family(iid), ID_WORD[py_tier(iid)]) if py_legacy(iid) else iid
def old_tier(iid):   # SkyyAccessories 0.4.5 AccDefs.tierOf on talisman ids (Common 1 .. Legendary 5; Talisman 2, Ring 3, Artifact 4)
    for r, w in ((5, "Legendary"), (4, "Epic"), (3, "Rare"), (2, "Uncommon"), (1, "Common")):
        if iid.endswith("_" + w):
            return r
    return {"Artifact": 4, "Ring": 3, "Talisman": 2}.get(iid[iid.rfind("_") + 1:], 1)
OLD_IDS = ["Skyy_Talisman_%s_%s" % (_b[0], _w) for _b in FOLDED for _w in ("Common", "Uncommon", "Rare", "Epic", "Legendary")]
LEGACY_IDS = ["Skyy_Talisman_%s_%s" % (_b[0], _w) for _b in FOLDED for _w, _t in LEGACY_WORDS]
FOLDED_IDS = [booster_id(_b, _t) for _b in FOLDED for _t in range(1, 5)]
NEW_IDS = [booster_id(_b, _t) for _b in BOOSTERS if _b[9] == "T" for _t in range(1, 5)]
assert len(OLD_IDS) == 25 and len(LEGACY_IDS) == 20 and set(FOLDED_IDS) < set(OLD_IDS) and len(NEW_IDS) == 20
assert not set(NEW_IDS) & set(OLD_IDS + LEGACY_IDS) and sorted(FOLDED_IDS + NEW_IDS) == sorted(LINE_IDS)
for _li, _b in enumerate(BOOSTERS):
    for _t in range(1, 5):
        _i = LINE_IDS[_li * 4 + _t - 1]
        assert py_tier(_i) == _t and py_family(_i) == _b[0] and not py_legacy(_i) and py_modern(_i) == _i, _i
        assert (py_tail_tier(_i) == _t) == (_b[9] == "T"), _i       # part 2: the _T<n> tail parses first
    if _b[9] != "word":
        continue
    for _w, _t in LEGACY_WORDS:
        _i = "Skyy_Talisman_%s_%s" % (_b[0], _w)
        assert py_legacy(_i) and py_tier(_i) == _t and py_family(_i) == _b[0] and py_modern(_i) == LINE_IDS[_li * 4 + _t - 1], _i
assert py_modern("Skyy_Talisman_Vitality_Legendary") == "Skyy_Talisman_Vitality_Epic"
assert py_tier("Skyy_Talisman_Crit_T4") == 4 and py_family("Skyy_Talisman_MagicPower_T2") == "MagicPower"
# the equip swap order (AccStore.equipK: a higher tier of the same line swaps in, equal or lower is refused) is 0.4.5's for every pair
# of the 40 old ids of a line, except that the old fifth id (_Legendary) now TIES with the other tier-4 ids (_Epic and _Artifact)
_sgn = lambda x: (x > 0) - (x < 0)
for _b in FOLDED:
    _ids = sorted(set(i for i in OLD_IDS + LEGACY_IDS if py_family(i) == _b[0]))   # the 5 + 3 ids 0.4.5 knew (_Legendary is in both lists)

    assert len(_ids) == 8, _ids
    for _a in _ids:
        for _c in _ids:
            _o, _n = _sgn(old_tier(_a) - old_tier(_c)), _sgn(py_tier(_a) - py_tier(_c))
            if _o != _n:
                assert _n == 0 and "_Legendary" in (_a[-10:], _c[-10:]) and 4 in (old_tier(_a), old_tier(_c)), (_a, _c, _o, _n)

# ---- 0.5 CONFIG (the defaults file = the kit's DEFAULTS; AccCfg.migrate appends the lines from "notice.boosters" on to a 0.4.x file)
# groups of new keys: (comment lines, [(key, value), ...]) - the migration writes a group's comments before its first missing key
ADD_GROUPS = [
    (["# Tell players once, in chat, about the 0.5 accessory change (only players who had accessories before 0.5): true or false."],
     [("notice.boosters", "true")]),
    (["# Line switches: false = the line stays in the bag, counts for nothing and the Accessory Bag page says it is switched off."],
     [("line.%s" % _b[1], "true") for _b in BOOSTERS]),
    (["# Send the combat stats of the %s accessories to SkyyGear (true or false; false = they add nothing)." % ", ".join(COMBAT_LINES)],
     [("combatToGear", "true")]),
    (["# Booster numbers: four numbers for Normal,Unique,Rare,Legendary (no minus sign, up to 2 decimals). The entry name gives the",
      "# unit: flat = added to your maximum (Strength, MagicPower, Defense: whole points), pct = percent (Mana: of your Mana;",
      "# Regeneration: of max Health healed every regenEverySeconds; Speed: faster movement), chancePct / damagePct = whole percent",
      "# Crit Chance / Crit Damage, regenPct = percent faster Stamina refill, floor = the least the Mana line adds, fallPct = percent",
      "# less fall damage (written without a minus), jumpPct = percent higher jumps. The item tooltips print the built-in numbers;",
      "# the Accessory Bag page and /accessories lines show the ones below."],
     [("boost." + _e[0], BOOST_DEF[_i]) for _i, _e in enumerate(ENTRIES)]),
]
CONFIG_TEXT = "\n".join([
    "# SkyyAccessories settings. Change them in game: SkyWynn Menu -> Server Setup -> Accessories, or edit this file",
    "# and run /accessories reload (server admins: skyyaccessories.admin). Every change is logged in config-changes.log.",
    "#",
    "# Accessory bag slots every player can fill, 1-%d. Lowering it deletes nothing: accessories already in a higher slot stay," % CAP,
    "# keep counting and can still be unequipped - only a newly equipped accessory needs a free slot within the limit.",
    "slots=%d" % SLOTS_DEF,
    "# How often the Regeneration Accessory heals, in seconds (1-%d)." % REGEN_MAX,
    "regenEverySeconds=%d" % REGEN_EVERY,
] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + [""])
assert all(ord(ch) < 128 for ch in CONFIG_TEXT), "config text must stay ASCII"
# the 0.4.x lines the migration handles (spec 5.1): bonus.<family> with its untouched default and where an EDITED list goes ("" = its
# unit changed, it is dropped and logged); the 0.4.4 / 0.4.5 default comment lines it rewrites ("" = removed)
OLD_BONUS = [("Vitality", "2,4,6,8,10", "", "its unit changed from percent to flat - set boost.Health.flat by hand"),
             ("Endurance", "2,4,6,8,10", "", "its unit changed from percent to flat - set boost.Stamina.flat by hand"),
             ("Intelligence", "2,4,6,8,10", "Mana.pct", ""),
             ("Regeneration", "0.5,1,1.5,2,3", "Regeneration.pct", ""),
             ("Speed", "2,4,6,8,10", "Speed.pct", "")]
assert all(c == "" or c in E for _f, _d, c, _n in OLD_BONUS)
OLD_COMMENTS = [
    ("# Accessory bag slots every player can fill, 1-9. Lowering it deletes nothing: accessories already in a higher slot stay,",
     "# Accessory bag slots every player can fill, 1-%d. Lowering it deletes nothing: accessories already in a higher slot stay," % CAP),
    ("# How often the Regeneration talisman heals, in seconds (1-30).", "# How often the Regeneration Accessory heals, in seconds (1-%d)." % REGEN_MAX),
    ("# Talisman bonuses in percent for Common,Uncommon,Rare,Epic,Legendary (0-100 each, up to 2 decimals), one line per family.", ""),
    ("# Vitality / Endurance / Intelligence = percent of your flat max Health / Stamina / Mana, Regeneration = percent of max Health", ""),
    ("# healed every regenEverySeconds, Speed = percent movement speed. The item tooltips keep printing the built-in numbers", ""),
    ("# (2,4,6,8,10, Regeneration 0.5,1,1.5,2,3); the Accessory Bag page shows the ones below.", ""),
]
ADD_KEY = [k for _g, (_n, _ks) in enumerate(ADD_GROUPS) for k, _v in _ks]
ADD_VAL = [v for _g, (_n, _ks) in enumerate(ADD_GROUPS) for _k, v in _ks]
ADD_GROUP = [_g for _g, (_n, _ks) in enumerate(ADD_GROUPS) for _k, _v in _ks]
GROUP_NOTE = ["\n".join(_n) for _n, _ks in ADD_GROUPS]
MIG_NOTICE = ("[Accessories] Your talismans are now accessories: Health, Stamina, Mana, Regeneration and Speed Accessory, in the gear "
              "rarities Normal, Unique, Rare and Legendary, with new numbers. Stamina now also refills faster. /accessories lines "
              "shows every line.")   # spec 5.1 (the one place where the old word "talismans" reaches a player: it names what they had)


def jlit(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
def jstrs(xs):
    return ", ".join(jlit(x) for x in xs)
def JX(src):
    return src.replace("@PKG@", PKG)
def jfloats(vals, scale=1.0):
    return ", ".join("%.4ff" % (v * scale) for v in [0] + list(vals))
# 0.5: Java written with @TOKEN@ class names (no f-string brace doubling in the new code)
_TOK = {"PKG": PKG, "PR": PR, "REF": REF, "ST": ST, "UNI": UNI, "WLD": WLD, "MSG": MSG, "PLA": PLA, "INV": INV, "IC": IC, "IS": IS,
        "IST": IST, "ISS": ISS, "ESM": ESM, "ESV": ESV, "DST": DST, "MOD": MOD, "SMO": SMO, "MTG": MTG, "CAL": CAL, "CB": CB,
        "ACH": ACH, "QRY": QRY, "CTX": CTX, "EVD": EVD, "BT": BT, "UCB": UCB, "UEB": UEB, "RGV": RGV, "RGN": RGN, "RGT": RGT,
        "CND": CND, "TMR": TMR, "SIC": SIC, "ITM": ITM, "EST": EST}
def JT(src):
    out = src
    for _k, _v in _TOK.items():
        out = out.replace("@%s@" % _k, _v)
    assert "@" not in out, "unresolved @TOKEN@ in: " + out[:160]
    return out
def JM(cls, src):
    cls.addMethod(CtNewMethod.make(JT(src), cls))
def JF(cls, src):
    cls.addField(CtField.make(JT(src), cls))

'''
for _i, _t in enumerate(OLD_TALISMANS):
    R1 = R1.replace("@@REC%d@@" % _i, _recipes_py(_t[5][:4], "        "))
assert "@@REC" not in R1
rep("@@R1@@", R1)

# ---------------------------------------------------------------- AccDefs: fields, the id rules, rarity, the line helpers, names
rep('''dfs.addField(CtField.make('public static final String[] FAMILIES = new String[] { %s };' % ", ".join('"%s"' % t[0] for t in TALISMANS), dfs))
dfs.addField(CtField.make('public static final String[] TIER_NAMES = new String[] { "", "Talisman", "Ring", "Artifact" };', dfs))
dfs.addField(CtField.make('public static volatile float[] VIT = new float[] { %s };' % jfloats(TALISMANS[FAM["Vitality"]][4]), dfs))   # 0.4.4: AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile float[] END = new float[] { %s };' % jfloats(TALISMANS[FAM["Endurance"]][4]), dfs))   # 0.4.4: AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile float[] INT = new float[] { %s };' % jfloats(TALISMANS[FAM["Intelligence"]][4]), dfs))   # 0.4.4: AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile float[] REG = new float[] { %s };' % jfloats(TALISMANS[FAM["Regeneration"]][4]), dfs))   # 0.4.4: AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile float[] SPD = new float[] { %s };' % jfloats(TALISMANS[FAM["Speed"]][4], 0.01), dfs))   # 0.4.4: AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))   # 0.4.4: config row regenEverySeconds (kit field:)
# 0.4: rarity names (index = tier 1..5) and the vanilla quality TextColor of each (read from Assets.zip Server/Item/Qualities)
dfs.addField(CtField.make('public static final String[] RARITY = new String[] { %s };' % ", ".join('"%s"' % r for r in RARITIES), dfs))
dfs.addField(CtField.make('public static final String[] RARITY_COLOR = new String[] { %s };' % ", ".join('"%s"' % c for c in RARITY_COLORS), dfs))
''', r'''# 0.5: THE BOOSTER TABLE as flat 1-D arrays (javassist compiles no [][]): per line (FAMILIES order), per line x 4 + tier - 1, per entry
dfs.addField(CtField.make('public static final String[] FAMILIES = new String[] { %s };' % jstrs(b[0] for b in BOOSTERS), dfs))   # family keys (item ids only)
dfs.addField(CtField.make('public static final String[] LINE_ADMIN = new String[] { %s };' % jstrs(b[1] for b in BOOSTERS), dfs))   # config, commands, acc:defs
dfs.addField(CtField.make('public static final String[] LINE_NAME = new String[] { %s };' % jstrs(b[2] for b in BOOSTERS), dfs))    # "<Rarity> <Line> Accessory"
dfs.addField(CtField.make('public static final String[] LINE_IDS = new String[] { %s };' % jstrs(LINE_IDS), dfs))
dfs.addField(CtField.make('public static final String[] LINE_SRC = new String[] { %s };' % jstrs(LINE_SRC), dfs))
dfs.addField(CtField.make('public static final String[] ID_WORD = new String[] { %s };' % jstrs(ID_WORD), dfs))   # ids only (tier 1..4)
dfs.addField(CtField.make('public static final String[] LEGACY_WORD = new String[] { %s };' % jstrs(w for w, t in LEGACY_WORDS), dfs))
dfs.addField(CtField.make('public static final int[] LEGACY_TIER = new int[] { %s };' % ", ".join(str(t) for w, t in LEGACY_WORDS), dfs))
dfs.addField(CtField.make('public static final String[] DISPLAY = new String[] { %s };' % jstrs(DISPLAY), dfs))   # rarity 1..6
dfs.addField(CtField.make('public static final String[] RARITY_COLOR = new String[] { %s };' % jstrs(RARITY_COLORS), dfs))   # kit colours
dfs.addField(CtField.make('public static final int[] AP = new int[] { %s };' % ", ".join(str(a) for a in ACC_AP), dfs))
dfs.addField(CtField.make('public static final String[] E_KEYS = new String[] { %s };' % jstrs(e[0] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int[] E_LINE = new int[] { %s };' % ", ".join(str(e[1]) for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final String[] E_UNIT = new String[] { %s };' % jstrs(STAT_KINDS[e[2]][0] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int[] E_WHOLE = new int[] { %s };' % ", ".join("1" if STAT_KINDS[e[2]][1] else "0" for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final float[] E_CAP = new float[] { %s };' % ", ".join("%d.0f" % STAT_KINDS[e[2]][2] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int BONUS_MAX = %d;' % BONUS_MAX, dfs))
# the live numbers [entry * 5 + tier] (tier 0 = no accessory = 0), in the config unit (Speed / Regeneration in percent); AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile float[] BOOST = new float[] { %s };' % ", ".join(jfloats(e[3]) for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static volatile int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))   # 0.4.4: config row regenEverySeconds (kit field:)
for _b in BOOSTERS:   # 0.5: the line switches (kit field: rows line.<Admin>, live kill switches, on by default - Skyy's decision 6)
    dfs.addField(CtField.make('public static volatile boolean LINE_%s = true;' % _b[1].upper(), dfs))
dfs.addField(CtField.make('public static volatile boolean NOTICE = true;', dfs))   # 0.5: config row notice.boosters
# 0.5 part 2: the gear:extra key of each entry ("" = not a combat stat), the allowlist in text order, config row combatToGear, and the
# entries of the movement parts (-1 = no such entry)
dfs.addField(CtField.make('public static final String[] E_GEAR = new String[] { %s };' % jstrs(E_GEAR), dfs))
dfs.addField(CtField.make('public static final String[] GEAR_KEYS = new String[] { %s };' % jstrs(GEAR_KEYS), dfs))
dfs.addField(CtField.make('public static volatile boolean COMBAT_TO_GEAR = true;', dfs))
dfs.addField(CtField.make('public static final int E_SPEED = %d;' % KIND_E.get("speedPct", -1), dfs))
dfs.addField(CtField.make('public static final int E_JUMP = %d;' % KIND_E.get("jumpPct", -1), dfs))
dfs.addField(CtField.make('public static final int E_FALL = %d;' % KIND_E.get("fallPct", -1), dfs))
''')
assert "LINE_REGENERATION" not in OLD  # (the new field names are free)

rep('''dfs.addMethod(CtNewMethod.make("""
public static int tierOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isTalisman(id)) {
    for (int r = RARITY.length - 1; r >= 1; r--) if (id.endsWith("_" + RARITY[r])) return r;
    if (id.endsWith("_Artifact")) return 4;
    if (id.endsWith("_Ring")) return 3;
    if (id.endsWith("_Talisman")) return 2;
    return 1;
  }
  int t = id.lastIndexOf("_T");
  if (t < 0 || t + 2 >= id.length()) return 1;
  try { return Integer.parseInt(id.substring(t + 2)); } catch (Throwable e) { return 1; }
}""", dfs))
# 0.4: 0.2/0.3 talisman ids (Talisman/Ring/Artifact) - counted as Uncommon/Rare/Epic by tierOf
dfs.addMethod(CtNewMethod.make("""
public static boolean isLegacy(String id) {
  if (!isTalisman(id)) return false;
  return id.endsWith("_Talisman") || id.endsWith("_Ring") || id.endsWith("_Artifact");
}""", dfs))
# "Skyy_Talisman_Vitality_Ring" -> "Skyy_Talisman_Vitality_Rare"; every other id unchanged
dfs.addMethod(CtNewMethod.make("""
public static String modernOf(String id) {
  if (!isLegacy(id)) return id;
  String f = familyOf(id);
  int t = tierOf(id);
  if (f == null || t < 1 || t >= RARITY.length) return id;
  return "Skyy_Talisman_" + f + "_" + RARITY[t];
}""", dfs))
# rarity 1..5 (Common..Legendary) of any accessory: talismans by rarity, bench accessories T1..T5+ (plan), Omni Legendary; 0 = none
dfs.addMethod(CtNewMethod.make("""
public static int rarityOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isRetired(id)) return 0;   // 0.4.2: retired - never counts (future accessory power reads rarityOf)
  if (OMNI.equals(id)) return 5;
  int t = tierOf(id);
  if (t < 1) t = 1;
  if (t > 5) t = 5;
  return t;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String rarityName(String id) {
  if (isRetired(id)) return "Does nothing";   // 0.4.2: the page's rarity column for a retired accessory
  return RARITY[rarityOf(id)];
}""", dfs))
''', r'''# 0.5: the tier of a "_T<digits>" tail (the part 2 line ids Skyy_Talisman_<Key>_T1..T4), else -1
JM(dfs, r"""
public static int tailTier(String id) {
  if (!isTalisman(id)) return -1;
  int k = id.lastIndexOf('_');
  if (k < 0 || k + 2 >= id.length() + 1) return -1;
  String w = id.substring(k + 1);
  if (w.length() < 2 || w.charAt(0) != 'T') return -1;
  for (int i = 1; i < w.length(); i++) if (!Character.isDigit(w.charAt(i))) return -1;
  try { return Integer.parseInt(w.substring(1)); } catch (Throwable e) { return -1; }
}""")
# 0.5 tier 1..4 of a stat accessory: a _T<n> tail, then the id words Common..Epic, then the legacy words (Talisman 2, Ring 3, Artifact 4,
# Legendary 4 - the old fifth id folds into Legendary); bench accessories keep their _T<n>
JM(dfs, r"""
public static int tierOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isTalisman(id)) {
    int tt = tailTier(id);
    if (tt > 0) return tt;
    for (int r = ID_WORD.length - 1; r >= 1; r--) if (id.endsWith("_" + ID_WORD[r])) return r;
    for (int j = 0; j < LEGACY_WORD.length; j++) if (id.endsWith("_" + LEGACY_WORD[j])) return LEGACY_TIER[j];
    return 1;
  }
  int t = id.lastIndexOf("_T");
  if (t < 0 || t + 2 >= id.length()) return 1;
  try { return Integer.parseInt(id.substring(t + 2)); } catch (Throwable e) { return 1; }
}""")
# 0.4 / 0.5: an old stat accessory id (0.2/0.3 Talisman / Ring / Artifact, and 0.4's fifth id _Legendary): asset kept, no recipe
JM(dfs, r"""
public static boolean isLegacy(String id) {
  if (!isTalisman(id) || tailTier(id) > 0) return false;
  for (int j = 0; j < LEGACY_WORD.length; j++) if (id.endsWith("_" + LEGACY_WORD[j])) return true;
  return false;
}""")
# "Skyy_Talisman_Vitality_Ring" -> "..._Rare", "Skyy_Talisman_Vitality_Legendary" -> "..._Epic" (Legendary); every other id unchanged
JM(dfs, r"""
public static String modernOf(String id) {
  if (!isLegacy(id)) return id;
  String f = familyOf(id);
  int t = tierOf(id);
  if (f == null || t < 1 || t >= ID_WORD.length) return id;
  return "Skyy_Talisman_" + f + "_" + ID_WORD[t];
}""")
# 0.5 rarity 1..4 (Normal..Legendary, the gear ladder) of every accessory: stat accessories by tier, bench I Normal, II Unique,
# III Rare, IV and up Legendary, the Omni Legendary (crafted: never above Legendary); 5 / 6 (Fabled / Mythic) are for the rare finds
JM(dfs, r"""
public static int rarityOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isRetired(id)) return 0;   // 0.4.2: retired - never counts (future accessory power reads rarityOf)
  if (OMNI.equals(id)) return 4;
  int t = tierOf(id);
  if (t < 1) t = 1;
  if (t > 4) t = 4;
  return t;
}""")
JM(dfs, r"""
public static String rarityName(String id) {
  if (isRetired(id)) return "Does nothing";   // 0.4.2: the page's rarity column for a retired accessory
  return DISPLAY[rarityOf(id)];
}""")
''')

rep('''# highest talisman tier per family (index = FAMILIES) among the bag slots
dfs.addMethod(CtNewMethod.make("""
public static int[] bestTiers(String[] s) {
  int[] out = new int[FAMILIES.length];
  if (s == null) return out;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (!isTalisman(id)) continue;
    int f = familyIndex(familyOf(id));
    if (f < 0) continue;
    int t = tierOf(id);
    if (t > 5) t = 5;   // 0.4: Common..Legendary
    if (t > out[f]) out[f] = t;
  }
  return out;
}""", dfs))
''', '''# highest tier per line (index = FAMILIES) among the bag slots - ONLY THE HIGHEST RARITY OF A LINE COUNTS (a duplicate that slipped in
# through stashK changes nothing: the maximum is taken)
dfs.addMethod(CtNewMethod.make("""
public static int[] bestTiers(String[] s) {
  int[] out = new int[FAMILIES.length];
  if (s == null) return out;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (!isTalisman(id)) continue;
    int f = familyIndex(familyOf(id));
    if (f < 0) continue;
    int t = tierOf(id);
    if (t > 4) t = 4;   // 0.5: Normal..Legendary
    if (t > out[f]) out[f] = t;
  }
  return out;
}""", dfs))
''')


rep('''# 0.4: 2.0 -> "2", 1.5 -> "1.5" (one decimal, values are >= 0)
dfs.addMethod(CtNewMethod.make("""
public static String pctText(float v) {
  int i = Math.round(v * 10.0f);
  if (i % 10 == 0) return String.valueOf(i / 10);
  return String.valueOf(i / 10) + "." + String.valueOf(i % 10);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String bonusText(String[] s) {
  int[] b = bestTiers(s);
  StringBuilder sb = new StringBuilder();
  if (b[%(V)d] > 0) sb.append(" / +").append(pctText(VIT[b[%(V)d]])).append("%% Health");
  if (b[%(E)d] > 0) sb.append(" / +").append(pctText(END[b[%(E)d]])).append("%% Stamina");
  if (b[%(I)d] > 0) sb.append(" / +").append(pctText(INT[b[%(I)d]])).append("%% Mana");
  if (b[%(R)d] > 0) sb.append(" / Regen ").append(pctText(REG[b[%(R)d]])).append("%% HP per ").append(REGEN_EVERY).append("s");
  if (b[%(S)d] > 0) sb.append(" / +").append(pctText(SPD[b[%(S)d]] * 100.0f)).append("%% Speed");
  if (sb.length() == 0) return hasOmni(s) ? "Bonuses - no talismans yet - the Omni counts as every bench accessory" : "Bonuses - none yet - put talismans in this bag";
  return "Bonuses - " + sb.substring(3);
}""" % dict(V=FAM["Vitality"], E=FAM["Endurance"], I=FAM["Intelligence"], R=FAM["Regeneration"], S=FAM["Speed"]), dfs))
''', r'''# 0.5: the Java of AccDefs.statParts (per line, the short texts of its stats at one tier, live numbers) and AccDefs.lineOn, generated
# from the booster table when this script runs (a new stat kind needs its text here and a tooltip in TIPS)
def _stat_code():
    TXT = {   # kind -> Java expression of one part ((v) = the number); manaFloor rides along with manaPct
        "maxHealth": '"+" + numText(v) + " max Health"',
        "maxStamina": '"+" + numText(v) + " max Stamina"',
        "staminaRegen": '"+" + numText(v) + "% Stamina Regen"',
        "healPct": '"Heals " + numText(v) + "% max Health every " + REGEN_EVERY + " s"',
        "speedPct": '"+" + numText(v) + "% Speed"',
        "str": '"+" + numText(v) + " Strength"',                  # part 2
        "mp": '"+" + numText(v) + " Magical Power"',
        "def": '"+" + numText(v) + " Defense"',
    }
    PAIRS = {   # part 2: two stats of one line on ONE part (the rider is left out when its number is 0)
        "cc": ("cd", '"+" + numText(a) + "% Crit Chance"', '"+" + numText(r) + "% Crit Damage"'),
        "fallPct": ("jumpPct", '"-" + numText(a) + "% fall damage"', '"+" + numText(r) + "% jump height"'),
    }
    lines = []
    for li, bo in enumerate(BOOSTERS):
        body = []
        ks = dict((kd, E[bo[1] + "." + st]) for st, kd, _v in bo[5])
        for st, kd, _v in bo[5]:
            e = str(E[bo[1] + "." + st])
            if kd in ("manaFloor", "cd", "jumpPct"):
                continue
            if kd in PAIRS:
                rk, ta, tr = PAIRS[kd]
                rx = ("b[" + str(ks[rk]) + " * 5 + t]") if rk in ks else "0.0f"
                body.append("    float a" + e + " = b[" + e + " * 5 + t];\n    float r" + e + " = " + rx + ";\n    String p" + e + " = \"\";\n"
                            "    if (a" + e + " > 0.0f) p" + e + " = " + ta.replace("(a)", "(a" + e + ")") + ";\n"
                            "    if (r" + e + " > 0.0f) p" + e + " = p" + e + " + (p" + e + ".length() > 0 ? \", \" : \"\") + " +
                            tr.replace("(r)", "(r" + e + ")") + ";\n    if (p" + e + ".length() > 0) out.add(p" + e + ");")
                continue
            if kd == "manaPct":
                fl = ks.get("manaFloor")
                fx = ("b[" + str(fl) + " * 5 + t]") if fl is not None else "0.0f"
                body.append("    float v" + e + " = b[" + e + " * 5 + t];\n    float f" + e + " = " + fx + ";\n    if (v" + e + " > 0.0f || f" + e +
                            " > 0.0f) out.add(\"+\" + numText(v" + e + ") + \"% max Mana\" + (f" + e + " > 0.0f ? \" (at least +\" + numText(f" + e +
                            ") + \")\" : \"\"));")
                continue
            assert kd in TXT, "0.5: no text for the stat kind %s - add it to _stat_code (and to TIPS)" % kd
            body.append("    float v" + e + " = b[" + e + " * 5 + t];\n    if (v" + e + " > 0.0f) out.add(" + TXT[kd].replace("(v)", "(v" + e + ")") + ");")
        lines.append("  if (li == " + str(li) + ") {\n" + "\n".join(body) + "\n  }")
    return ("public static String[] statParts(int li, int t) {\n  java.util.ArrayList out = new java.util.ArrayList();\n"
            "  float[] b = BOOST;\n  if (t < 1 || t > 4) return new String[0];\n" + "\n".join(lines) +
            "\n  return (String[]) out.toArray(new String[0]);\n}")
STAT_JAVA = _stat_code()
LINEON_JAVA = ("public static boolean lineOn(int li) {\n  switch (li) {\n" +
               "".join("    case %d: return LINE_%s;\n" % (i, b[1].upper()) for i, b in enumerate(BOOSTERS)) +
               "    default: return false;\n  }\n}")
# 0.5: 24.0 -> "24", 1.5 -> "1.5", 0.25 -> "0.25" (up to 2 decimals, values are >= 0)
JM(dfs, r"""
public static String numText(float v) {
  long c = Math.round((double) v * 100.0);
  if (c % 100L == 0L) return String.valueOf(c / 100L);
  if (c % 10L == 0L) return String.valueOf(c / 100L) + "." + String.valueOf((c % 100L) / 10L);
  String f = String.valueOf(c % 100L);
  if (f.length() < 2) f = "0" + f;
  return String.valueOf(c / 100L) + "." + f;
}""")
# 0.5: is a line switched on (config rows line.<Admin>; generated from the table)
JM(dfs, LINEON_JAVA)
# 0.5: line index of an admin name, a family key (the old names Vitality / Endurance / Intelligence as aliases) or a line name; -1 = none
JM(dfs, r"""
public static int lineOf(String name) {
  if (name == null) return -1;
  String n = name.trim();
  for (int i = 0; i < FAMILIES.length; i++) {
    if (LINE_ADMIN[i].equalsIgnoreCase(n) || FAMILIES[i].equalsIgnoreCase(n) || LINE_NAME[i].equalsIgnoreCase(n)) return i;
  }
  return -1;
}""")
# 0.5: rarity word or number -> tier 1..4 (Normal, Unique, Rare, Legendary or 1-4); -1 = not a line rarity
JM(dfs, r"""
public static int rarityIndex(String w) {
  if (w == null) return -1;
  String x = w.trim();
  for (int t = 1; t <= 4; t++) if (DISPLAY[t].equalsIgnoreCase(x) || String.valueOf(t).equals(x)) return t;
  return -1;
}""")
JM(dfs, r"""
public static String idOf(int li, int t) {
  if (li < 0 || li >= FAMILIES.length || t < 1 || t > 4) return null;
  return LINE_IDS[li * 4 + t - 1];
}""")
JM(dfs, r"""
public static boolean isBoosterId(String id) {
  if (id == null) return false;
  for (int i = 0; i < LINE_IDS.length; i++) if (LINE_IDS[i].equals(id)) return true;
  return false;
}""")
# 0.5: the short texts of one line's stats at one tier, with the live numbers (generated from the booster table)
JM(dfs, STAT_JAVA)
# 0.5: the Bonuses well - one key / value row per line with its best accessory in the bag (key = the line name, value = its stats at
# that rarity with the live numbers, or "switched off"), up to BONUS_MAX rows: [key0, value0, key1, value1, ...], "" = an empty row.
# (AccGear.pageRows adds the SkyyGear / SkyySkills notes in the free rows.)
JM(dfs, r"""
public static String[] bonusRows(String[] s) {
  String[] out = new String[BONUS_MAX * 2];
  for (int i = 0; i < out.length; i++) out[i] = "";
  int[] best = bestTiers(s);
  int n = 0;
  for (int li = 0; li < FAMILIES.length; li++) {
    if (best[li] <= 0 || n >= BONUS_MAX) continue;
    out[n * 2] = LINE_NAME[li];
    if (!lineOn(li)) { out[n * 2 + 1] = "switched off"; n++; continue; }
    String[] p = statParts(li, best[li]);
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < p.length; k++) { if (k > 0) sb.append(", "); sb.append(p[k]); }
    out[n * 2 + 1] = sb.length() > 0 ? sb.toString() : "nothing (its numbers are 0 on this server)";
    n++;
  }
  return out;
}""")
JM(dfs, r"""
public static String bonusText(String[] s) {
  String[] l = bonusRows(s);
  if (l[0].length() > 0) return "Bonuses - your best accessory of each line counts";
  return hasOmni(s) ? "Bonuses - no stat accessories yet - the Omni counts as every bench accessory" : "Bonuses - none yet - put accessories in this bag";
}""")
# 0.5 part 2: the tiers that COUNT right now (bestTiers with the switched-off lines at 0) - the effect tick, the gear:extra text, the notes
JM(dfs, r"""
public static int[] activeTiers(String[] s) {
  int[] best = bestTiers(s);
  for (int li = 0; li < best.length; li++) if (!lineOn(li)) best[li] = 0;
  return best;
}""")
# 0.5 part 2: does line li at tier t send anything to SkyyGear (a gear:extra entry above 0) / have a fall-damage part above 0?
JM(dfs, r"""
public static boolean sendsGear(int li, int t) {
  if (t < 1 || t > 4) return false;
  for (int e = 0; e < E_GEAR.length; e++) if (E_LINE[e] == li && E_GEAR[e].length() > 0 && BOOST[e * 5 + t] >= 1.0f) return true;
  return false;
}""")
JM(dfs, r"""
public static boolean hasFall(int li, int t) {
  return E_FALL >= 0 && E_LINE[E_FALL] == li && t >= 1 && t <= 4 && BOOST[E_FALL * 5 + t] > 0.0f;
}""")
''')

rep('''public static String pretty(String id) {
  if (isTalisman(id)) {
    int tt = tierOf(id);
    String r = tt >= 0 && tt < RARITY.length ? RARITY[tt] : String.valueOf(tt);
    if (isLegacy(id)) return r + " " + familyOf(id) + " " + id.substring(id.lastIndexOf('_') + 1) + " - old";   // no parentheses in inline page text
    return r + " " + familyOf(id) + " Talisman";
  }
''', '''public static String pretty(String id) {
  if (isTalisman(id)) {   // 0.5: "<Rarity> <Line> Accessory" - never the family key or the old word (a legacy id shows its rarity's name)
    int r = rarityOf(id);
    int li = familyIndex(familyOf(id));
    String ln = li >= 0 ? LINE_NAME[li] + " Accessory" : "Accessory";
    return r >= 1 && r < DISPLAY.length ? DISPLAY[r] + " " + ln : ln;
  }
''')
# after pretty: the refusal word, acc:defs and /accessories lines
rep('''# 0.4: bench accessory ids for the acc:has bridge value = EXACTLY ONE entry per bench id''', r'''# 0.5: what the bag's "same or better ... already equipped" refusal names
JM(dfs, r"""
public static String lineLabel(String id) {
  if (isTalisman(id)) {
    int li = familyIndex(familyOf(id));
    return li >= 0 ? LINE_NAME[li] + " Accessory" : "accessory of that line";
  }
  return OMNI.equals(id) ? "Omni accessory" : "bench accessory";
}""")
# 0.5 bridge acc:defs (spec 5.9): every rarity of every line as name:key:tier:itemId:rarity:ap:sources, records joined by ","
JM(dfs, r"""
public static String defsText() {
  StringBuilder sb = new StringBuilder();
  for (int li = 0; li < FAMILIES.length; li++) {
    for (int t = 1; t <= 4; t++) {
      if (sb.length() > 0) sb.append(',');
      sb.append(LINE_ADMIN[li]).append(':').append(FAMILIES[li]).append(':').append(t).append(':').append(LINE_IDS[li * 4 + t - 1]);
      sb.append(':').append(DISPLAY[t]).append(':').append(AP[t]).append(':').append(LINE_SRC[li * 4 + t - 1]);
    }
  }
  return sb.toString();
}""")
# 0.5 /accessories lines: one chat line per line (its four rarities with the live numbers); ids = the admin's extra id line
JM(dfs, r"""
public static String[] linesText(boolean ids) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int li = 0; li < FAMILIES.length; li++) {
    StringBuilder sb = new StringBuilder();
    sb.append(LINE_NAME[li]).append(" Accessory (").append(LINE_ADMIN[li]).append(")");
    if (!lineOn(li)) sb.append(" - SWITCHED OFF on this server");
    sb.append(": ");
    for (int t = 1; t <= 4; t++) {
      if (t > 1) sb.append(" | ");
      sb.append(DISPLAY[t]).append(' ');
      String[] p = statParts(li, t);
      if (p.length == 0) sb.append("nothing");
      for (int k = 0; k < p.length; k++) { if (k > 0) sb.append(" and "); sb.append(p[k]); }
    }
    out.add(sb.toString());
    if (ids) {
      StringBuilder ib = new StringBuilder("    ids: ");
      for (int t = 1; t <= 4; t++) { if (t > 1) ib.append(" / "); ib.append(LINE_IDS[li * 4 + t - 1]); }
      out.add(ib.toString());
    }
  }
  return (String[]) out.toArray(new String[0]);
}""")
# 0.4: bench accessory ids for the acc:has bridge value = EXACTLY ONE entry per bench id''')

# ---------------------------------------------------------------- AccStore: 60 slots in two files, restamp, count, deliver
rep('''st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
# 0.4.4: CAP stays the STORAGE size (bag files slot0..slot8, the page loop, the un:<i> buttons); SLOTS = this server's limit for NEW
# equips (config row slots, kit field:). Accessories already in a slot >= SLOTS stay, keep counting and can be unequipped.
st_.addField(CtField.make("public static volatile int SLOTS = %d;" % CAP, st_))
''', '''st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
st_.addField(CtField.make("public static final int MAIN = %d;" % MAIN_SLOTS, st_))   # 0.5: slot0..MAIN-1 in <key>.properties, the rest in <key>.more.properties
# 0.4.4: CAP stays the STORAGE size (0.5: 60 - the page, the un:<i> buttons); SLOTS = this server's limit for NEW equips (config row
# slots, kit field:, default 18). Accessories already in a slot >= SLOTS stay, keep counting and can be unequipped.
st_.addField(CtField.make("public static volatile int SLOTS = %d;" % SLOTS_DEF, st_))
# 0.5: bag files that could not be READ at load (path text -> reason): never overwritten afterwards, so a read error cannot wipe a bag
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADFILE = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static boolean RESTAMP_WARNED = false;", st_))
''')
rep('''# 0.4.1: the bag of storage key k (bags/<k>.properties); lock stays per player
st_.addMethod(CtNewMethod.make("""
public static String[] slotsK(java.util.UUID u, String k) {
  String[] s = (String[]) BAGS.get(k);
  if (s != null) return s;
  synchronized (lock(u)) {
    s = (String[]) BAGS.get(k);
    if (s != null) return s;
    s = new String[CAP];
    try {
      java.nio.file.Path f = DIR.resolve(k + ".properties");
      if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
        java.util.Properties p = new java.util.Properties();
        java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
        try { p.load(in); } finally { in.close(); }
        for (int i = 0; i < CAP; i++) {
          String v = p.getProperty("slot" + i);
          if (v != null && v.trim().length() > 0) s[i] = v.trim();
        }
      }
    } catch (Throwable t) { warn("could not load bag " + k + " for " + u + ": " + t); }
    BAGS.put(k, s);
    return s;
  }
}""", st_))
''', r'''# 0.5: slots from..to-1 of one bag file (a missing file = empty slots); a file that cannot be read is remembered in BADFILE
JM(st_, r"""
public static void readInto(String[] s, java.nio.file.Path f, int from, int to) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    for (int i = from; i < to && i < s.length; i++) {
      String v = p.getProperty("slot" + i);
      if (v != null && v.trim().length() > 0) s[i] = v.trim();
    }
  } catch (Throwable t) {
    BADFILE.put(f.toString(), String.valueOf(t));
    warn("could not load bag file " + f + " - it is left as it is and not overwritten until the server restarts: " + t);
  }
}""")
# 0.4.1: the bag of storage key k; 0.5: slot0..8 from bags/<k>.properties (0.4.x's file, same format), slot9..59 from bags/<k>.more.properties
JM(st_, r"""
public static String[] slotsK(java.util.UUID u, String k) {
  String[] s = (String[]) BAGS.get(k);
  if (s != null) return s;
  synchronized (lock(u)) {
    s = (String[]) BAGS.get(k);
    if (s != null) return s;
    s = new String[CAP];
    readInto(s, DIR.resolve(k + ".properties"), 0, MAIN);
    readInto(s, DIR.resolve(k + ".more.properties"), MAIN, CAP);
    BAGS.put(k, s);
    return s;
  }
}""")
# 0.5: true when a file of bag k could not be read at load: the page then moves nothing into or out of that bag (a move could not be
# saved, and an item put in would be lost at the next restart)
JM(st_, r"""
public static boolean isBad(String k) {
  if (DIR == null || k == null) return false;
  return BADFILE.containsKey(DIR.resolve(k + ".properties").toString()) || BADFILE.containsKey(DIR.resolve(k + ".more.properties").toString());
}""")
# 0.5: writes slots from..to-1 into one bag file (tmp + move). The main file is always written (0.4.5's format and comment); the second
# file only when it holds something or already exists (then it may become empty - it is never deleted). A BADFILE is never written.
JM(st_, r"""
public static void writeSlots(String[] s, String name, int from, int to, boolean always) throws java.io.IOException {
  java.nio.file.Path f = DIR.resolve(name);
  if (BADFILE.containsKey(f.toString())) { warn("bag file " + f + " could not be read at load, so it is not overwritten (restart after fixing or removing it)"); return; }
  java.util.Properties p = new java.util.Properties();
  boolean any = false;
  for (int i = from; i < to && i < s.length; i++) if (s[i] != null) { p.setProperty("slot" + i, s[i]); any = true; }
  if (!any && !always && !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  java.nio.file.Path tmp = DIR.resolve(name + ".tmp");
  java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
  try { p.store(out, from == 0 ? "SkyyAccessories bag" : "SkyyAccessories bag - slots 10 to 60 (0.5 and later)"); } finally { out.close(); }
  java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
}""")
''')
rep('''# 0.4.1: saves the bag of storage key k (the key the caller resolved once), then republishes the active profile
st_.addMethod(CtNewMethod.make("""
public static void saveK(java.util.UUID u, String k) {
  synchronized (lock(u)) {
    try {
      String[] s = slotsK(u, k);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.util.Properties p = new java.util.Properties();
      for (int i = 0; i < s.length; i++) if (s[i] != null) p.setProperty("slot" + i, s[i]);
      java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
      java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
      try { p.store(out, "SkyyAccessories bag"); } finally { out.close(); }
      java.nio.file.Files.move(tmp, DIR.resolve(k + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable t) { warn("could not save bag " + k + " for " + u + ": " + t); }
    publish(u);
  }
}""", st_))
''', '''# 0.4.1: saves the bag of storage key k (the key the caller resolved once), then republishes the active profile; 0.5: two files
st_.addMethod(CtNewMethod.make("""
public static void saveK(java.util.UUID u, String k) {
  synchronized (lock(u)) {
    try {
      String[] s = slotsK(u, k);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      writeSlots(s, k + ".properties", 0, MAIN, true);
      writeSlots(s, k + ".more.properties", MAIN, CAP, false);
    } catch (Throwable t) { warn("could not save bag " + k + " for " + u + ": " + t); }
    publish(u);
  }
}""", st_))
''')
rep('''# 0.4.3 review fix: SkyyCooking's LIVE Campfire accessory factors.''', r'''# 0.5: the accessories (Skyy_Talisman_* / Skyy_Accessory_*, the bag item too) in storage + hotbar + backpack, by count
JM(st_, r"""
public static int accCount(@IC@[] conts) {
  int n = 0;
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id != null && (id.startsWith("Skyy_Talisman_") || id.startsWith("Skyy_Accessory_"))) n = n + it.getQuantity();
    }
  }
  return n;
}""")
# 0.5 RESTAMP (spec 5.2, the SkyySacks 0.7.7 pattern): a saved stack keeps the quality index it was saved with, so every accessory stack
# (and the bag item) whose index differs from its item's gets withQuality(item index) - id and count unchanged (asserted per stack, and
# the accessory count before and after is compared). World thread only (AccRestampTask); returns the stacks changed.
JM(st_, r"""
public static int restamp(@INV@ inv) {
  if (inv == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  int before = accCount(conts);
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id == null || !(id.startsWith("Skyy_Talisman_") || id.startsWith("Skyy_Accessory_"))) continue;
      @ITM@ item = it.getItem();
      if (item == null) continue;
      int want = item.getQualityIndex();
      if (it.getQualityIndex() == want) continue;
      @IS@ nw = it.withQuality(want);
      if (nw == null || !id.equals(nw.getItemId()) || nw.getQuantity() != it.getQuantity()) {
        if (!RESTAMP_WARNED) { RESTAMP_WARNED = true; warn("restamp skipped " + id + ": withQuality changed the id or the count (logged once)"); }
        continue;
      }
      cont.setItemStackForSlot(s, nw);
      n++;
    }
  }
  int after = accCount(conts);
  if (after != before && !RESTAMP_WARNED) { RESTAMP_WARNED = true; warn("restamp: the accessory count changed from " + before + " to " + after + " (logged once)"); }
  return n;
}""")
# 0.5: how many of item id are in storage + hotbar + backpack (the give counts before and after)
JM(st_, r"""
public static int countOf(@INV@ inv, String id) {
  if (inv == null || id == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n = n + it.getQuantity();
    }
  }
  return n;
}""")
# 0.5 give (spec 5.9): n copies of id, one at a time (MaxStack 1), storage first and the rest dropped at the player's feet
# (addOrDropItemStack, vanilla's giveOutput call), counted before and after. ONLY on that player's world thread (Store.isInThread);
# returns { handed out, now in the inventory, dropped } or null when the player / store / thread is not right.
JM(st_, r"""
public static int[] deliver(@PR@ pr, String id, int n) {
  if (pr == null || id == null || n < 1) return null;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  @ST@ st = r.getStore();
  if (st == null || !st.isInThread()) return null;
  @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  if (p == null || p.getInventory() == null) return null;
  @INV@ inv = p.getInventory();
  int before = countOf(inv, id);
  int ok = 0;
  for (int i = 0; i < n; i++) {
    if (@SIC@.addOrDropItemStack(st, r, inv.getCombinedStorageHotbarBackpack(), new @IS@(id, 1))) ok++;
  }
  int[] c = giveCount(before, countOf(inv, id), dropped, n);
  if (c[3] != 0) warn("give of " + n + " x " + id + " to " + pr.getUsername() + ": " + c[1] + " arrived in the inventory and " + c[2] + " were dropped at their feet (" + c[0] + " handed out)");
  return new int[] { c[0], c[1], c[2] };
}""")
# 0.4.3 review fix: SkyyCooking's LIVE Campfire accessory factors.''')
# part 1 review finding 1: SimpleItemContainer.addOrDropItemStack returns TRUE ONLY WHEN A REMAINDER WAS DROPPED at the player's feet
# (HytaleServer.jar bytecode: addItemStack, then dropItem + iconst_1 when getRemainder() is not empty, else iconst_0). So the loop
# counts the true returns as dropped, and handed out = arrived in the inventory + dropped. The arithmetic is its own method so the
# harness can test it without the engine: { handed out, arrived, dropped, 1 = not all n accounted for (warn) }.
rep('''  int before = countOf(inv, id);
  int ok = 0;
  for (int i = 0; i < n; i++) {
    if (@SIC@.addOrDropItemStack(st, r, inv.getCombinedStorageHotbarBackpack(), new @IS@(id, 1))) ok++;
  }
''', '''  int before = countOf(inv, id);
  int dropped = 0;
  for (int i = 0; i < n; i++) {
    if (@SIC@.addOrDropItemStack(st, r, inv.getCombinedStorageHotbarBackpack(), new @IS@(id, 1))) dropped++;   // true = dropped
  }
''')
rep('''# 0.5 give (spec 5.9): n copies of id, one at a time (MaxStack 1), storage first and the rest dropped at the player's feet''',
    '''# 0.5 (part 1 review finding 1): the give arithmetic - got = the count after minus before (never below 0), handed out = got + dropped;
# c[3] = 1 when that is not the n asked for (a stack merged elsewhere, a full inventory that could not drop, ...)
JM(st_, r"""
public static int[] giveCount(int before, int after, int dropped, int n) {
  int got = after - before;
  if (got < 0) got = 0;
  int d = dropped < 0 ? 0 : dropped;
  int ok = got + d;
  return new int[] { ok, got, d, ok != n ? 1 : 0 };
}""")
# 0.5 give (spec 5.9): n copies of id, one at a time (MaxStack 1), storage first and the rest dropped at the player's feet''')
# part 1 review finding 5: canEquipK / equipK compared with the FIRST slot of the line; a line with duplicates (the stashK last resort)
# could let a Unique replace a Normal while a Legendary sat in another slot. Now: refused when ANY slot of the line is equal or better;
# otherwise the LOWEST slot of the line is swapped out (the others stay; bestTiers takes the maximum).
rep('''    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (g != null && g.equals({PKG}.AccDefs.groupOf(s[i]))) return {PKG}.AccDefs.tierOf(s[i]) < tier;
    }}
    int cap = capOf(s);   // 0.4.4: a free slot below this server's limit (an in-place upgrade above is still fine)''',
    '''    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    boolean same = false;
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || g == null || !g.equals({PKG}.AccDefs.groupOf(s[i]))) continue;
      if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return false;   // 0.5: an equal or better one anywhere in the line = refused
      same = true;
    }}
    if (same) return true;   // 0.5: every slot of the line is lower - the lowest is swapped out
    int cap = capOf(s);   // 0.4.4: a free slot below this server's limit (an in-place upgrade above is still fine)''')
rep('''    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (g != null && g.equals({PKG}.AccDefs.groupOf(s[i]))) {{
        if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return null;
        String old = s[i]; s[i] = id; saveK(u, k); return old;
      }}
    }}''', '''    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    int low = -1;
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || g == null || !g.equals({PKG}.AccDefs.groupOf(s[i]))) continue;
      if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return null;   // 0.5: an equal or better one anywhere in the line = refused
      if (low < 0 || {PKG}.AccDefs.tierOf(s[i]) < {PKG}.AccDefs.tierOf(s[low])) low = i;
    }}
    if (low >= 0) {{ String old = s[low]; s[low] = id; saveK(u, k); return old; }}   // 0.5: the lowest slot of the line''')

# ---------------------------------------------------------------- AccCfg: loader, boost entries, the 0.5 migration, the check hook
_CFG_NEW = r'''# ================= AccCfg (0.4.4; 0.5: booster entries, line switches, notice switch, the one-time 0.5 migration) =================
cfg_.addField(CtField.make("public static java.nio.file.Path FILE;", cfg_))
cfg_.addField(CtField.make("public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT), cfg_))
cfg_.addField(CtField.make("public static final String[] BOOST_DEF = new String[] { %s };" % jstrs(BOOST_DEF), cfg_))   # index = AccDefs.E_KEYS
cfg_.addField(CtField.make('public static volatile String TIP_SEEN = "";', cfg_))   # the last "differs from the tooltips" text logged
# 0.5 migration data (spec 5.1)
cfg_.addField(CtField.make("public static final String[] OLD_FAM = new String[] { %s };" % jstrs(o[0] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_DEF = new String[] { %s };" % jstrs(o[1] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_CARRY = new String[] { %s };" % jstrs(o[2] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_WHY = new String[] { %s };" % jstrs(o[3] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] ADD_KEY = new String[] { %s };" % jstrs(ADD_KEY), cfg_))
cfg_.addField(CtField.make("public static final String[] ADD_VAL = new String[] { %s };" % jstrs(ADD_VAL), cfg_))
cfg_.addField(CtField.make("public static final int[] ADD_GROUP = new int[] { %s };" % ", ".join(str(g) for g in ADD_GROUP), cfg_))
cfg_.addField(CtField.make("public static final String[] GROUP_NOTE = new String[] { %s };" % jstrs(GROUP_NOTE), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_COMMENT = new String[] { %s };" % jstrs(o for o, n in OLD_COMMENTS), cfg_))
cfg_.addField(CtField.make("public static final String[] NEW_COMMENT = new String[] { %s };" % jstrs(n for o, n in OLD_COMMENTS), cfg_))
for _src in [
@@CFG_INFO@@
@@CFG_WRITEDEFAULTS@@
@@CFG_NUM@@
# "6,12,18,24" -> n numbers (n = 4 for a booster entry, 5 for a 0.4.x bonus list), or null when it is not exactly n numbers >= 0
r"""
public static double[] parseN(String v, int n) {
  if (v == null) return null;
  String[] p = v.split(",", -1);
  if (p.length != n) return null;
  double[] out = new double[n];
  for (int i = 0; i < n; i++) {
    double x = num(p[i]);
    if (x < 0.0) return null;
    out[i] = x;
  }
  return out;
}""",
@@CFG_SAMEROW@@
@@CFG_DTEXT@@
@@CFG_ROWTEXT@@
@@CFG_INTIN@@
r"""
public static boolean boolIn(String v, boolean def, String key) {
  if (v == null) return def;
  String x = v.trim().toLowerCase();
  if (x.equals("true") || x.equals("on") || x.equals("yes") || x.equals("1")) return true;
  if (x.equals("false") || x.equals("off") || x.equals("no") || x.equals("0")) return false;
  @PKG@.AccStore.warn("config.properties: " + key + "=" + v.trim() + " is not true or false - " + (def ? "true" : "false") + " is used");
  return def;
}""",
r"""
public static int entryIndex(String en) {
  if (en == null) return -1;
  for (int i = 0; i < @PKG@.AccDefs.E_KEYS.length; i++) if (@PKG@.AccDefs.E_KEYS[i].equals(en)) return i;
  return -1;
}""",
# one booster entry from the file: 4 numbers, capped at the entry's cap, whole numbers where the entry needs them (the loader clamps like
# the kit validates; a line that is not 4 numbers falls back to the built-in numbers)
r"""
public static double[] boostIn(String v, int e) {
  double[] d = parseN(BOOST_DEF[e], 4);
  if (v == null) return d;
  String k = "boost." + @PKG@.AccDefs.E_KEYS[e];
  double[] r = parseN(v, 4);
  if (r == null) {
    @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " is not 4 numbers like " + BOOST_DEF[e] + " (Normal,Unique,Rare,Legendary; 0 or more, at most 2 decimals, no minus sign) - the built-in numbers are used");
    return d;
  }
  double cap = (double) @PKG@.AccDefs.E_CAP[e];
  boolean cl = false;
  boolean wh = false;
  for (int t = 0; t < 4; t++) {
    if (r[t] > cap) { r[t] = cap; cl = true; }
    if (@PKG@.AccDefs.E_WHOLE[e] == 1 && r[t] != Math.floor(r[t])) { r[t] = Math.floor(r[t]); wh = true; }
  }
  if (cl) @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " has a number above " + dtext(cap) + " - " + dtext(cap) + " is used there");
  if (wh) @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " takes whole numbers only - the decimals are dropped");
  return r;
}""",
r"""
public static String oneLine(String t) {
  if (t == null) return "";
  return t.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ');
}""",
# the key of one physical .properties line (null for a comment or a blank line)
r"""
public static String keyOf(String ln) {
  if (ln == null) return null;
  int i = 0;
  while (i < ln.length() && (ln.charAt(i) == ' ' || ln.charAt(i) == '\t' || ln.charAt(i) == '\f')) i++;
  if (i >= ln.length()) return null;
  char c0 = ln.charAt(i);
  if (c0 == '#' || c0 == '!') return null;
  int j = i;
  while (j < ln.length()) {
    char c = ln.charAt(j);
    if (c == '=' || c == ':' || c == ' ' || c == '\t' || c == '\f') break;
    j++;
  }
  return ln.substring(i, j);
}""",
# a value line that continues on the next physical line (an odd number of backslashes at the end)
r"""
public static boolean contLine(String ln) {
  int n = 0;
  for (int i = ln.length() - 1; i >= 0 && ln.charAt(i) == '\\'; i--) n++;
  return n % 2 == 1;
}""",
# the migration's change-log lines, in the kit's config-changes.log format (who migration-0.5, uuid -, via migrate) + one INFO line each
r"""
public static void logMig(java.util.ArrayList logs) {
  StringBuilder sb = new StringBuilder();
  String now = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss").format(java.time.LocalDateTime.now());
  for (int i = 0; i < logs.size(); i++) {
    String[] e = (String[]) logs.get(i);
    sb.append(now).append('\t').append("migration-0.5").append('\t').append('-').append('\t').append("migrate").append('\t');
    sb.append(oneLine(e[0])).append('\t').append(oneLine(e[1])).append('\t').append(oneLine(e[2])).append('\t').append(oneLine(e[3])).append('\n');
    info("config " + oneLine(e[0]) + " " + oneLine(e[1]) + " -> " + oneLine(e[2]) + " by migration-0.5 (migrate)" + ("ok".equals(e[3]) ? "" : " [" + e[3] + "]"));
  }
  try {
    java.nio.file.Path lf = FILE.resolveSibling("config-changes.log");
    java.nio.file.Files.write(lf, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { @PKG@.AccStore.warn("could not write config-changes.log for the 0.5 update: " + t); }
}""",
# THE ONE-TIME 0.5 MIGRATION (spec 5.1). setup() -> load(true) -> here, BEFORE CfgPub.start. Runs only when the file has a bonus. line
# and no boost. line (a file with neither just gets the missing 0.5 keys); afterwards there is no bonus. line, so it never runs again.
# One atomic write; the old file is copied once to config.properties.pre-0.5.bak; every changed / carried / dropped / added value is
# logged. Returns "" when nothing was done, else the summary for the ready log line.
r"""
public static String migrate() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return "";
    byte[] raw = java.nio.file.Files.readAllBytes(FILE);
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.ByteArrayInputStream(raw));
    boolean hasBonus = false;
    boolean hasBoost = false;
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String pk = (String) it.next();
      if (pk.startsWith("bonus.")) hasBonus = true;
      if (pk.startsWith("boost.")) hasBoost = true;
    }
    // 0.5 part 2: mig = the 0.4.x -> 0.5 update (bonus. lines and no boost. line). A file that already has boost. lines (a server
    // that ran part 1) only gets the 0.5 keys it misses appended: no slots change, no removal, no .bak (nothing is lost).
    boolean mig = hasBonus && !hasBoost;
    String text = new String(raw, "ISO-8859-1");
    String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    String body = text;
    if (body.endsWith("\r\n")) body = body.substring(0, body.length() - 2);
    else if (body.endsWith("\n")) body = body.substring(0, body.length() - 1);
    String[] lines = body.length() == 0 ? new String[0] : body.split("\r?\n", -1);
    java.util.ArrayList logs = new java.util.ArrayList();
    java.util.HashMap carried = new java.util.HashMap();
    for (int f = 0; mig && f < OLD_FAM.length; f++) {
      String key = "bonus." + OLD_FAM[f];
      String ov = p.getProperty(key);
      if (ov == null) continue;
      String o = ov.trim();
      double[] r = parseN(o, 5);
      if (r != null && sameRow(r, parseN(OLD_DEF[f], 5))) { logs.add(new String[] { key, o, "(removed - the 0.5 default applies)", "done" }); continue; }
      if (OLD_CARRY[f].length() == 0) { logs.add(new String[] { key, o, "(dropped - " + OLD_WHY[f] + ")", "invalid" }); continue; }
      if (r == null) { logs.add(new String[] { key, o, "(dropped - not 5 numbers, so the 0.5 default applies)", "invalid" }); continue; }
      int e = entryIndex(OLD_CARRY[f]);
      double[] c = new double[] { r[0], r[1], r[2], r[4] };
      String note = "";
      for (int t = 0; t < 4; t++) {
        if (e >= 0 && c[t] > (double) @PKG@.AccDefs.E_CAP[e]) { c[t] = (double) @PKG@.AccDefs.E_CAP[e]; note = ", capped at " + dtext(c[t]); }
      }
      String cv = rowText(c);
      carried.put(OLD_CARRY[f], cv);
      logs.add(new String[] { key, o, "boost." + OLD_CARRY[f] + "=" + cv + " (the 1st, 2nd, 3rd and 5th number - the 4th, " + dtext(r[3]) + ", is dropped" + note + ")", "done" });
    }
    String sv = p.getProperty("slots");
    boolean bump = mig && sv != null && sv.trim().equals("9");
    boolean bumped = false;
    StringBuilder out = new StringBuilder();
    boolean contDrop = false;
    boolean contKeep = false;
    for (int i = 0; i < lines.length; i++) {
      String ln = lines[i];
      if (contDrop) { contDrop = contLine(ln); continue; }
      if (contKeep) { contKeep = contLine(ln); out.append(ln).append(nl); continue; }
      String k = keyOf(ln);
      if (mig && k != null && k.startsWith("bonus.")) { contDrop = contLine(ln); continue; }
      if (bump && "slots".equals(k) && !contLine(ln)) { out.append("slots=@SLOTS@").append(nl); bumped = true; continue; }
      if (mig && k == null) {
        int oc = -1;
        for (int j = 0; j < OLD_COMMENT.length; j++) if (OLD_COMMENT[j].equals(ln)) oc = j;
        if (oc >= 0) { if (NEW_COMMENT[oc].length() > 0) out.append(NEW_COMMENT[oc]).append(nl); continue; }
      }
      if (k != null) contKeep = contLine(ln);
      out.append(ln).append(nl);
    }
    if (bumped) logs.add(0, new String[] { "slots", "9", "@SLOTS@", "ok" });
    StringBuilder add = new StringBuilder();
    int lastGroup = -1;
    for (int a = 0; a < ADD_KEY.length; a++) {
      if (p.getProperty(ADD_KEY[a]) != null) continue;
      String v = ADD_VAL[a];
      if (ADD_KEY[a].startsWith("boost.")) {
        String cv2 = (String) carried.get(ADD_KEY[a].substring(6));
        if (cv2 != null) v = cv2;
        logs.add(new String[] { "boost[" + ADD_KEY[a].substring(6) + "]", "(none)", v, "done" });
      } else logs.add(new String[] { ADD_KEY[a], "(none)", v, "done" });
      if (ADD_GROUP[a] != lastGroup) {
        lastGroup = ADD_GROUP[a];
        String[] nt = GROUP_NOTE[lastGroup].split("\n");
        for (int j = 0; j < nt.length; j++) add.append(nt[j]).append(nl);
      }
      add.append(ADD_KEY[a]).append('=').append(v).append(nl);
    }
    if (logs.size() == 0) return "";
    String result = out.toString();
    if (add.length() > 0) result = result + "# ---- added by SkyyAccessories 0.5 (booster accessories) ----" + nl + add.toString();
    java.nio.file.Path bak = FILE.resolveSibling(FILE.getFileName().toString() + ".pre-0.5.bak");
    if (!hasBoost && !java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0])) java.nio.file.Files.copy(FILE, bak, new java.nio.file.CopyOption[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp-0.5");
    java.io.FileOutputStream fo = new java.io.FileOutputStream(tmp.toFile());
    try { fo.write(result.getBytes("ISO-8859-1")); fo.flush(); fo.getFD().sync(); } finally { fo.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    logMig(logs);
    if (hasBoost) return "config.properties: " + logs.size() + " missing 0.5 settings added (config-changes.log)";
    return "config.properties updated to 0.5 (" + logs.size() + " changes in config-changes.log, the old file kept as config.properties.pre-0.5.bak)";
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to 0.5 - it stays as it is, and the built-in 0.5 numbers apply where it has none: " + t);
    return "config.properties could not be updated to 0.5 (see the warning)";
  }
}""",
# the mod's loader: setup() (first = true: writes the 0.5 default file or migrates a 0.4.x one, first) and the kit's RELOAD after every
# save / hand edit
r"""
public static String load(boolean first) {
  String mig = "";
  if (first) { writeDefaults(); mig = migrate(); }
  java.util.Properties p = new java.util.Properties();
  try {
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) {
    if (!first) {
      @PKG@.AccStore.warn("config.properties could not be read - the current settings stay: " + t);
      return "config.properties could not be read - the current settings stay";
    }
    @PKG@.AccStore.warn("config.properties could not be read - the built-in settings are used: " + t);
    p = new java.util.Properties();
  }
  int sl = intIn(p.getProperty("slots"), @SLOTS@, 1, @CAP@, "slots");
  int rg = intIn(p.getProperty("regenEverySeconds"), @REGEN@, 1, @RMAX@, "regenEverySeconds");
  float[] bo = new float[@NE@ * 5];
  StringBuilder bt = new StringBuilder();
  for (int e = 0; e < @NE@; e++) {
    double[] r = boostIn(p.getProperty("boost." + @PKG@.AccDefs.E_KEYS[e]), e);
    bo[e * 5] = 0.0f;
    for (int t = 0; t < 4; t++) bo[e * 5 + t + 1] = (float) r[t];
    if (!sameRow(r, parseN(BOOST_DEF[e], 4))) bt.append(", ").append(@PKG@.AccDefs.E_KEYS[e]).append(' ').append(rowText(r));
  }
  boolean[] on = new boolean[@NL@];
  StringBuilder off = new StringBuilder();
  for (int li = 0; li < @NL@; li++) {
    on[li] = boolIn(p.getProperty("line." + @PKG@.AccDefs.LINE_ADMIN[li]), true, "line." + @PKG@.AccDefs.LINE_ADMIN[li]);
    if (!on[li]) off.append(", ").append(@PKG@.AccDefs.LINE_ADMIN[li]);
  }
  boolean nt = boolIn(p.getProperty("notice.boosters"), true, "notice.boosters");
  boolean cg = boolIn(p.getProperty("combatToGear"), true, "combatToGear");   // 0.5 part 2
  @PKG@.AccStore.SLOTS = sl;
  @PKG@.AccDefs.REGEN_EVERY = rg;
  @PKG@.AccDefs.BOOST = bo;
@SETLINES@
  @PKG@.AccDefs.NOTICE = nt;
  @PKG@.AccDefs.COMBAT_TO_GEAR = cg;
  StringBuilder tip = new StringBuilder();
  if (rg != @REGEN@) tip.append(", Regeneration every ").append(rg).append(" s");
  tip.append(bt.toString());
  String ts = "";
  if (tip.length() > 0) ts = tip.substring(2);
  if (!ts.equals(TIP_SEEN)) {
    TIP_SEEN = ts;
    if (ts.length() > 0) info("this server's booster numbers differ from what the item tooltips print (built-in numbers - the Accessory Bag page and /accessories lines show the live ones): " + ts);
  }
  String bs = "built-in";
  if (bt.length() > 0) bs = "custom (" + bt.substring(2) + ")";
  String res = "config " + sl + " bag slots, Regeneration every " + rg + " s, booster numbers " + bs;
  if (off.length() > 0) res = res + ", lines switched off: " + off.substring(2);
  if (!nt) res = res + ", the 0.5 notice is off";
  if (!cg) res = res + ", combat stats are not sent to SkyyGear (combatToGear=false)";
  if (mig.length() > 0) res = res + "; " + mig;
  return res;
}""",
@@CFG_RELOAD@@
# check= hook of the boost table: key = boost[<entry>], value = the canonical text, null = a removal
r"""
public static String checkBoost(String key, String value) {
  String en = key == null ? "" : key;
  int a = en.indexOf('[');
  int b = en.lastIndexOf(']');
  if (a >= 0 && b > a) en = en.substring(a + 1, b);
  int e = entryIndex(en);
  if (e < 0) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < @PKG@.AccDefs.E_KEYS.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.E_KEYS[i]); }
    return "Unknown entry. The booster entries are: " + sb.toString() + ".";
  }
  if (value == null) return "The " + en + " line stays - set it to " + BOOST_DEF[e] + " to go back to the built-in numbers.";
  double[] r = parseN(value, 4);
  if (r == null) return "Needs 4 numbers for Normal,Unique,Rare,Legendary like " + BOOST_DEF[e] + " (no minus sign, up to 2 decimals).";
  double cap = (double) @PKG@.AccDefs.E_CAP[e];
  for (int t = 0; t < 4; t++) if (r[t] > cap) return "Each number must be from 0 to " + dtext(cap) + " - " + @PKG@.AccDefs.DISPLAY[t + 1] + " is " + dtext(r[t]) + ".";
  if (@PKG@.AccDefs.E_WHOLE[e] == 1) {
    for (int t = 0; t < 4; t++) if (r[t] != Math.floor(r[t])) return "Whole numbers only for " + en + " - " + @PKG@.AccDefs.DISPLAY[t + 1] + " is " + dtext(r[t]) + ".";
  }
  return null;
}""",
]:
    _src = JX(_src).replace("@CAP@", str(CAP)).replace("@SLOTS@", str(SLOTS_DEF)).replace("@REGEN@", str(REGEN_EVERY)) \
        .replace("@RMAX@", str(REGEN_MAX)).replace("@NE@", str(len(ENTRIES))).replace("@NL@", str(len(BOOSTERS))) \
        .replace("@SETLINES@", "\n".join("  %s.AccDefs.LINE_%s = on[%d];" % (PKG, b[1].upper(), i) for i, b in enumerate(BOOSTERS)))
    assert "@" not in _src.replace("@PKG@", ""), _src[:80]
    cfg_.addMethod(CtNewMethod.make(_src, cfg_))

'''
for _tok, _k in (("@@CFG_INFO@@", 0), ("@@CFG_WRITEDEFAULTS@@", 1), ("@@CFG_NUM@@", 2), ("@@CFG_SAMEROW@@", 3), ("@@CFG_DTEXT@@", 4),
                 ("@@CFG_ROWTEXT@@", 5), ("@@CFG_INTIN@@", 6), ("@@CFG_RELOAD@@", 7)):
    _CFG_NEW = _CFG_NEW.replace(_tok, CFG_KEEP[_k])
assert "@@" not in _CFG_NEW
cut("# ================= AccCfg (0.4.4)", "# ================= the admin config kit", _CFG_NEW)

# ---------------------------------------------------------------- Server Setup rows (kit tools/skyycfg.py)
cut("# ================= the admin config kit (0.4.4;", "# ================= AccFn (bridge function acc:fn:has) =================", r'''# ================= the admin config kit (0.4.4; research/Server-Setup-Spec.md 4.14, tools/CONFIG-CONTRACT.md; 0.5 rows: spec 5.8) =================
# (key, label, cat, type, default, min, max, opts, unit, flags, help, bind) - row key = file key (spec 7: the file key never changes)
CFG_CATS = [("bag", "Accessory Bag"), ("boosters", "Boosters")]
CFG_ROWS = [
    ("slots", "Accessory slots", "bag", "int", str(SLOTS_DEF), "1", str(CAP), "step=1", "", "new,danger",
     "Lowering it deletes nothing: accessories already in higher slots stay and count until taken out.",
     "field:AccStore.SLOTS@config.properties:slots;confirm=down"),
    ("notice.boosters", "Tell players about the accessory change", "bag", "bool", "true", "", "", "", "", "live",
     "One chat line, once, for each player who had accessories before 0.5.",
     "field:AccDefs.NOTICE@config.properties:notice.boosters"),
    ("regenEverySeconds", "Regeneration heals every", "boosters", "int", str(REGEN_EVERY), "1", str(REGEN_MAX), "step=1", "s", "live,adv",
     "How often the Regeneration Accessory heals. Its item tooltip keeps saying %d seconds." % REGEN_EVERY,
     "field:AccDefs.REGEN_EVERY@config.properties:regenEverySeconds"),
    ("boost", "Booster numbers", "boosters", "table", "", "", "60", "text;type;Normal..Legendary", "", "live,danger",
     "Four numbers, Normal to Legendary. The entry name gives the unit. Fall is written without a minus.",
     "reload@config.properties:boost.;check=AccCfg.checkBoost"),
    ("combatToGear", "Send combat stats to SkyyGear", "boosters", "bool", "true", "", "", "", "", "live",
     "Off = %s add nothing (SkyyGear applies their stats)." % " and ".join(
         [", ".join(COMBAT_LINES[:-1]), COMBAT_LINES[-1]] if len(COMBAT_LINES) > 1 else COMBAT_LINES),
     "field:AccDefs.COMBAT_TO_GEAR@config.properties:combatToGear"),
] + [("line.%s" % _b[1], "%s line" % _b[2], "boosters", "bool", "true", "", "", "", "", "live",
      "Off = the line stays in the bag, counts for nothing and the bag page says switched off.",
      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS]
assert all(len(_r[10]) <= 100 for _r in CFG_ROWS), [_r[0] for _r in CFG_ROWS if len(_r[10]) > 100]
CFG_NOTE = "Item tooltips show the built-in numbers - the Accessory Bag page shows this server's."
kit = CFG.emit(pool, PKG, MOD="SkyyAccessories", TITLE="Accessories", VERSION=VERSION, NODE="skyyaccessories.admin", CATS=CFG_CATS,
               ROWS=CFG_ROWS, FILES=["Skyy_SkyyAccessories/config.properties"], NOTE=CFG_NOTE, RELOAD="AccCfg.reload", KEEP=20,
               DEFAULTS={"config.properties": CONFIG_TEXT})

# ================= 0.5 part 2: AccGear - combat stats to SkyyGear (gear:extra:<uuid>), the bag page notes, bridge clean-up =================
# SkyyGear 0.1 (live) / 0.1.1 / 0.1.2 read gear:extra:<uuid> as ONE String ("str:40,cc:10": GearStats.extra -> parseExtra, whole numbers,
# unknown keys skipped) and add it to the totals of every hit (GearStats.totals(..., withExtra = true) in the offence and Defense
# handlers). No other mod writes the key (every build script in this repo checked), so SkyyAccessories OWNS it (spec 5.4, "one
# gear:extra writer" in 4.2): the text is written only when it changes; removed when it becomes empty, for every player who left
# (AccTick, every 5 s) and on shutdown - always with Map.remove(key, ourText), so a text another mod wrote is never removed. A text we
# did not write is overwritten with one WARN per player; when it changes again within 5 s after that overwrite (a second writer) or
# is not a String at all (another format), writing stops for that player until they rejoin or switch profile (profile:epoch changes),
# with one more WARN - two writers never fight every second. Bridge values are java.lang types only.
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> our text in the bridge
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap AT = new java.util.concurrent.ConcurrentHashMap();")      # uuid -> Long ms of our overwrite of a foreign text
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap STOP = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> the profile epoch we stopped at
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> the overwrite WARN was logged
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap MOVED = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> we have a movement entry
JF(gear, 'public static final String SOURCE = "accessories.talismans";')   # our movement protocol source (tools/skyymove.py)
JF(gear, 'public static final String OWNER_FALL = "stat:owner:fallDamage";')   # SkyySkills claims it: it applies every source's fall damage
JM(gear, r"""
public static String keyOf(java.util.UUID u) {
  return "gear:extra:" + u.toString();
}""")
JM(gear, r"""
public static String clip(Object o) {
  String t = String.valueOf(o);
  return t.length() > 80 ? t.substring(0, 80) + "..." : t;
}""")
JM(gear, r"""
public static Object epochMark(java.util.UUID u) {
  Object ep = @PKG@.AccStore.epochOf(u);
  if (ep == null) return "-";
  return ep;
}""")
# the text for one bag: best = AccDefs.activeTiers (switched-off lines 0); every gear:extra entry of the line's best rarity, floored to a
# whole number (SkyyGear floors each part anyway), summed per key, keys in GEAR_KEYS order, zero parts left out; "" = nothing to send
JM(gear, r"""
public static String textOf(int[] best) {
  if (!@PKG@.AccDefs.COMBAT_TO_GEAR || best == null) return "";
  String[] gk = @PKG@.AccDefs.GEAR_KEYS;
  long[] sum = new long[gk.length];
  float[] bo = @PKG@.AccDefs.BOOST;
  for (int e = 0; e < @PKG@.AccDefs.E_GEAR.length; e++) {
    String g = @PKG@.AccDefs.E_GEAR[e];
    if (g.length() == 0) continue;
    int li = @PKG@.AccDefs.E_LINE[e];
    int t = li >= 0 && li < best.length ? best[li] : 0;
    if (t < 1 || t > 4) continue;
    int gi = -1;
    for (int k = 0; k < gk.length; k++) if (gk[k].equals(g)) gi = k;
    if (gi < 0) continue;
    double v = Math.floor((double) bo[e * 5 + t]);
    if (v > 0.0) sum[gi] = sum[gi] + (long) v;
  }
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < gk.length; k++) {
    if (sum[k] <= 0L) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(gk[k]).append(':').append(sum[k]);
  }
  return sb.toString();
}""")
# publish one player's text (any thread: the bridge is a ConcurrentHashMap; the tick calls it on the world thread once a second).
# Returns 0 nothing written, 1 written, 2 removed, 3 a foreign text overwritten, 4 writing stopped for this player.
JM(gear, r"""
public static int publish(java.util.UUID u, String name, String text, long now) {
  if (u == null) return 0;
  String key = keyOf(u);
  java.util.Map b = @PKG@.AccStore.bridge();
  Object st = STOP.get(u);
  if (st != null) {
    if (st.equals(epochMark(u))) return 0;
    STOP.remove(u);
    AT.remove(u);
    WARNED.remove(u);
    @PKG@.AccCfg.info("gear:extra for " + name + ": the profile switched - SkyyAccessories writes it again");
  }
  String tx = text == null ? "" : text;
  Object cur = b.get(key);
  String last = (String) LAST.get(u);
  if (cur != null && !(cur instanceof String)) {
    STOP.put(u, epochMark(u));
    LAST.remove(u);
    @PKG@.AccStore.warn(key + " (" + name + ") holds a " + cur.getClass().getName() + ", not a text - another mod's format, so SkyyAccessories leaves it alone and sends no accessory combat stats for this player until they rejoin or switch profile");
    return 4;
  }
  boolean foreign = cur != null && (last == null || !last.equals(cur));
  if (foreign) {
    Long at = (Long) AT.get(u);
    if (at != null && now - at.longValue() < 5000L) {
      STOP.put(u, epochMark(u));
      LAST.remove(u);
      AT.remove(u);
      @PKG@.AccStore.warn(key + " (" + name + ") changed again within 5 s after SkyyAccessories wrote it (now: " + clip(cur) + ") - a second writer; SkyyAccessories stops writing it for this player until they rejoin or switch profile");
      return 4;
    }
    if (tx.length() == 0) { LAST.remove(u); return 0; }   // nothing of ours to send: the other text stays
    if (!WARNED.containsKey(u)) {
      WARNED.put(u, Boolean.TRUE);
      @PKG@.AccStore.warn(key + " (" + name + ") held a text SkyyAccessories did not write (" + clip(cur) + ") - SkyyAccessories is the only writer of this key and replaces it");
    }
    b.put(key, tx);
    LAST.put(u, tx);
    AT.put(u, Long.valueOf(now));
    return 3;
  }
  if (tx.length() == 0) {
    LAST.remove(u);
    if (cur != null) { b.remove(key, cur); return 2; }
    return 0;
  }
  if (tx.equals(cur)) { LAST.put(u, tx); return 0; }
  b.put(key, tx);
  LAST.put(u, tx);
  return 1;
}""")
# our movement entry for one player (the protocol's own remove: MoveSync.post with all zeros does exactly this)
JM(gear, r"""
public static void dropMove(java.util.UUID u) {
  try {
    Object o = @PKG@.AccStore.bridge().get("move:" + u.toString());
    if (o instanceof java.util.Map) ((java.util.Map) o).remove(SOURCE);
  } catch (Throwable t) { }
}""")
# every player who left (AccTick, every 5 s, any thread): our gear:extra text and movement entry go, the per-player state is forgotten
JM(gear, r"""
public static void prune(java.util.Set online) {
  java.util.Map b = @PKG@.AccStore.bridge();
  java.util.Iterator it = LAST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (online.contains(e.getKey())) continue;
    b.remove(keyOf((java.util.UUID) e.getKey()), e.getValue());
    it.remove();
  }
  java.util.Iterator mi = MOVED.keySet().iterator();
  while (mi.hasNext()) {
    java.util.UUID mu = (java.util.UUID) mi.next();
    if (online.contains(mu)) continue;
    dropMove(mu);
    mi.remove();
  }
  AT.keySet().retainAll(online);
  STOP.keySet().retainAll(online);
  WARNED.keySet().retainAll(online);
}""")
# plugin shutdown: every text we wrote and every movement entry of ours leaves the bridge (the bridge outlives a plugin reload)
JM(gear, r"""
public static void shutdownAll() {
  java.util.Map b = @PKG@.AccStore.bridge();
  java.util.Iterator it = LAST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    b.remove(keyOf((java.util.UUID) e.getKey()), e.getValue());
  }
  java.util.Iterator mi = MOVED.keySet().iterator();
  while (mi.hasNext()) dropMove((java.util.UUID) mi.next());
  LAST.clear();
  MOVED.clear();
  AT.clear();
  STOP.clear();
  WARNED.clear();
}""")
# SkyyGear running = its bridge functions are there (gear:fn:stats, gear:gates - SkyyGear 0.1 setup); its combat stats switch = the
# kit's config:fn:SkyyGear "get" of part.stats (a java.lang call; tools/CONFIG-CONTRACT.md: never throws, never touches the world).
# Unknown (no config function, an odd answer) counts as on.
JM(gear, r"""
public static boolean gearRunning() {
  java.util.Map b = @PKG@.AccStore.bridge();
  return b.get("gear:fn:stats") instanceof java.util.function.Function || b.get("gear:gates") != null;
}""")
JM(gear, r"""
public static boolean gearStatsOn() {
  try {
    Object f = @PKG@.AccStore.bridge().get("config:fn:SkyyGear");
    if (!(f instanceof java.util.function.Function)) return true;
    Object r = ((java.util.function.Function) f).apply(new Object[] { "get", "part.stats" });
    if (!(r instanceof String)) return true;
    String x = ((String) r).trim().toLowerCase();
    return !(x.equals("false") || x.equals("off") || x.equals("no") || x.equals("0"));
  } catch (Throwable t) { return true; }
}""")
JM(gear, r"""
public static boolean fallOwned() {
  return @PKG@.AccStore.bridge().get(OWNER_FALL) != null;
}""")
# why the combat lines do nothing for this player right now ("" = they work): the bag page's "Combat stats" note
JM(gear, r"""
public static String combatNote(java.util.UUID u) {
  if (!@PKG@.AccDefs.COMBAT_TO_GEAR) return "not sent - switched off in Server Setup";
  if (!gearRunning()) return "need SkyyGear, which is not running";
  if (!gearStatsOn()) return "off in SkyyGear (Gear stats in combat)";
  if (u != null && STOP.containsKey(u)) return "paused - another mod writes them (server log)";
  return "";
}""")
# the Bonuses well of the bag page: AccDefs.bonusRows + the notes in the free rows (a combat line that sends nothing, Feather's fall part
# without a fall-damage owner) - [key0, value0, ...], BONUS_MAX rows
JM(gear, r"""
public static String[] pageRows(String[] s, java.util.UUID u) {
  String[] r = @PKG@.AccDefs.bonusRows(s);
  int max = @PKG@.AccDefs.BONUS_MAX;
  int n = 0;
  while (n < max && r[n * 2].length() > 0) n++;
  int[] best = @PKG@.AccDefs.activeTiers(s);
  boolean gear = false;
  boolean fall = false;
  for (int li = 0; li < best.length; li++) {
    if (best[li] <= 0) continue;
    if (@PKG@.AccDefs.sendsGear(li, best[li])) gear = true;
    if (@PKG@.AccDefs.hasFall(li, best[li])) fall = true;
  }
  if (gear && n < max) {
    String cn = combatNote(u);
    if (cn.length() > 0) { r[n * 2] = "Combat stats"; r[n * 2 + 1] = cn; n++; }
  }
  if (fall && n < max && !fallOwned()) { r[n * 2] = "Fall damage"; r[n * 2 + 1] = "needs SkyySkills, which is not running"; n++; }
  return r;
}""")

''')

# ---------------------------------------------------------------- AccPage: page state fields, the look block, build()
rep('''page.addField(CtField.make("public String key;", page))   # 0.4.1: profile storage key the page was built for
''', '''page.addField(CtField.make("public String key;", page))   # 0.4.1: profile storage key the page was built for
page.addField(CtField.make("public int slotPage;", page))   # 0.5: the bag slot pager (clamped in build())
page.addField(CtField.make("public int invPage;", page))    # 0.5: the inventory list pager (clamped in build())
''')
_PAGE_OLD = cut("# ================= AccPage look (0.4.5)", "# giveBack: 0 = back in the inventory", r'''# ================= AccPage look (0.4.5; 0.5: bonus columns + pagers): the vanilla UI kit tools/skyyui.py, called when THIS script runs =================
# research/Vanilla-UI-Style-Guide.md sections 3, 7, 8c. acc_page_*() build the markup from kit calls (every value proven by SUI.verify() at
# the top of this script). The Java the kit emits gets a name here (ACC_*_JAVA) and is interpolated into the build() f-string below as
# {ACC_..._JAVA}: interpolated text is never re-parsed by Python, so the kit's Java string literals reach javassist exactly as written.
# ---- ACC PAGE BLOCK START (SkyyAccessories/test_skyyaccessories_0.5.py execs this block and ACC_BUILD_SRC below, with SUI verified,
# PKG, CAP, PAGE_ROWS, BONUS_MAX and the class-name constants defined, and compares the compiled build() with acc_page_state())
ACC_PREFIX = "SkyyAcc"                 # every element id starts with it; 0.4.4's root #SkyyAcc = the body
ACC_COL_W, ACC_COL_GAP = 580, 16       # two list wells: the bag slots | the accessories in the inventory
ACC_LIST_PAD = SUI.WELL_LIST_PAD       # 4: the vanilla list well's padding (WorldEventPanelPage #ListContainer)
ACC_COL_IN = ACC_COL_W - 2 * ACC_LIST_PAD                                       # 572: the width of a row inside a well
ACC_W = 2 * ACC_COL_W + ACC_COL_GAP + 2 * SUI.CONTENT_PAD                     # 1210
ACC_ROW_H, ACC_ROW_GAP = SUI.ROW_H_READABLE, SUI.ROW_GAP                       # 56 + 3: two readable lines (18 px name, 15 px rarity)
ACC_ACT_W = 112                        # UNEQUIP / EQUIP: a small Secondary row action (vanilla 92; 112 keeps UNEQUIP at 14 px)
ACC_PANEL_W = ACC_COL_IN - 4 - ACC_ACT_W                                       # the row panel; the action sits 4 px right of it
ACC_BAR = 4 + 8                        # the status bar (4 px + 8 px gap, WorldEventListRow)
ACC_ICON, ACC_ICON_BOX = 40, 52        # 40 px item icon in a 52 px box (12 px to the text)
ACC_ROW_PAD = 8                        # row panel padding left / right (WorldEventListRow)
ACC_TEXT_W = ACC_PANEL_W - 2 * ACC_ROW_PAD - ACC_BAR - ACC_ICON_BOX            # 376
ACC_NAME_H, ACC_SUB_H = SUI.fs(14) + 6, SUI.fs(12) + 5                          # 24 + 20 (the kit's row_text heights)
ACC_TEXT_TOP = (ACC_ROW_H - ACC_NAME_H - ACC_SUB_H) // 2                       # 6
ACC_LINE_H = 26                        # hint / bonus summary lines
ACC_TOP_PAD = 8
ACC_BON_ROWS, ACC_BON_H = BONUS_MAX // 2, 22                                    # 0.5: two columns of 6 bonus rows (16 px, one line)
ACC_BON_W = (ACC_W - 2 * SUI.CONTENT_PAD - 2 * 8) // 2                          # 580: half the top well's inner width
ACC_BON_KEY_W = SUI.PROP_KEY_W                                                  # 0.5 part 2: 150, the WorldEventPropertyRow key column
ACC_BON_VAL_W = ACC_BON_W - ACC_BON_KEY_W - 8                                   # 422: the value (the key's right margin is 8)
ACC_TOP_H = 2 * ACC_TOP_PAD + 2 * ACC_LINE_H + ACC_BON_ROWS * ACC_BON_H         # 200: the well on top
ACC_SEC_H = SUI.fs(13) + 10 + 10 + 4   # section head 26 + its margins 10 / 4 (WorldEventSectionLabel)
ACC_ROWS_H = PAGE_ROWS * (ACC_ROW_H + ACC_ROW_GAP)                              # 531: one page of rows (a fixed group)
ACC_PG_BTN_W, ACC_PG_CAP_W, ACC_PG_GAP = 120, 260, 12                           # 0.5: the kit pager in a 572 px well (524 px wide)
ACC_PG_H = SUI.BTN_SMALL_H + 8                                                  # 40: the pager's .h (32 + its top margin 8)
ACC_COLS_H = 2 * ACC_LIST_PAD + ACC_SEC_H + ACC_ROWS_H + ACC_PG_H              # 619: a list well = head + one page of rows + pager
ACC_SEP_H = 1 + 2 * SUI.SEP_MARGIN     # content separator 1 px, 8 px above and below
ACC_INFO_H = 44                        # the result line: 16 px bold, wraps to two lines
ACC_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + ACC_TOP_H + ACC_COLS_H + ACC_SEP_H + ACC_INFO_H     # 952 (fits 1080)
ACC_HINT = "Bench accessories unlock /craft recipes. Stat accessories add their bonus while they sit here - only your best of each line counts."
ACC_EMPTY = "Empty slot"
ACC_NONE = "None - craft accessories at a Workbench"
ACC_INFO_COLOR = "infoColor(this.info)"   # the Java colour expression of the result line (AccPage.infoColor below)
UI_DATA_COLORS = ["#8a97a3"]           # AccDefs.RETIRED_COLOR (0.4.2): a retired accessory's name + rarity word - data, like the rarity colours
assert (ACC_W, ACC_H) == (1210, 952) and ACC_COL_IN == 572 and ACC_TEXT_W == 376 and ACC_TEXT_TOP == 6, (ACC_W, ACC_H, ACC_TEXT_W)
assert ACC_ACT_W - 2 * SUI.BTN_SMALL_PAD >= 64 + 8, "UNEQUIP (64 px at 14 px bold) fits the small button without shrinking"
assert 2 * ACC_PG_BTN_W + 2 * ACC_PG_GAP + ACC_PG_CAP_W <= ACC_COL_IN, "the pager fits a list well"
SUI.assert_page_size(ACC_W, ACC_H)
# AccPage.infoColor: the result line's colour from the result text (no +/-/= marks in the texts): vanilla success green = done, error
# red = refused (nothing moved, or an item could not be given back), info blue = a note (the profile switched) and the Campfire line
# shown while no result is set. The patch (tools/acc_0_5_patch.py) asserts the full list of texts handleDataEvent sets; the harness
# runs this method on the real texts.
ACC_INFO_COLOR_SRC = """
public static String infoColor(String t) {
  if (t == null || t.length() == 0) return "%(eq)s";
  if (t.startsWith("upgraded to ")) return t.indexOf(" could not be returned") >= 0 ? "%(no)s" : "%(ok)s";
  if (t.startsWith("equipped ") || t.startsWith("unequipped ")) return "%(ok)s";
  if (t.startsWith("your profile changed")) return "%(eq)s";
  return "%(no)s";
}""" % {"ok": SUI.STATUS["+"], "no": SUI.STATUS["-"], "eq": SUI.STATUS["="]}


def acc_pager(parent, prefix, st):
    """The kit pager (Prev / caption / Next, small Secondary buttons, the Disabled look at the ends) under a list well's rows:
    st = (caption, prev_on, next_on) - J() values in the build, plain values in checks. Ids #<prefix>Prev / Page / Next."""
    cap, prev_on, next_on = st
    p = SUI.pager(parent, prefix, ACC_COL_IN, text=cap, prev_on=prev_on, next_on=next_on, btn_w=ACC_PG_BTN_W, caption_w=ACC_PG_CAP_W,
                  gap=ACC_PG_GAP)
    assert p.h == ACC_PG_H and (p.prev, p.page, p.next) == (prefix + "Prev", prefix + "Page", prefix + "Next"), (p.h, p.prev)
    return p


def acc_page_shell(bonus, bon, info, head, sp, ip):
    """The window + everything that is not a row: the top well (hint, #SkyyAccBonus, the bonus rows #SkyyAccBr0..11 in two columns:
    key #SkyyAccBk<k> + value #SkyyAccBon<k>), the two list wells with their section heads, their fixed row groups #SkyyAccSlotRows /
    #SkyyAccInvRows and pagers #SkyyAccSp / #SkyyAccIp, the separator and #SkyyAccInfo (colour = ACC_INFO_COLOR, a J() in the markup).
    bonus / bon (12 (key, value) pairs) / info / head (the slot head) = the b.set values; sp / ip = the pager states (see acc_pager).
    The bonus rows are the kit's property-row look (Pages/WorldEvent/WorldEventPropertyRow: the propKey label 150 px + 8, the
    propValue label, LayoutMode Left) with fixed widths and one line each: skyyui.property_row itself writes FlexWeight and
    WrapMaxLines, which skyyui.PROBED does not list yet (assert_proven). Returns the Shell."""
    sh = SUI.page_shell(ACC_PREFIX + "F", ACC_W, ACC_H, "Accessory Bag", body_id=ACC_PREFIX)
    ap, body = sh.appends, sh.body
    ap.append((body, SUI.panel("SkyyAccTop", "well", h=ACC_TOP_H, pad={"horizontal": 8, "vertical": ACC_TOP_PAD})))
    sh.text("SkyyAccTop", "SkyyAccHint", ACC_HINT, "default", h=ACC_LINE_H)             # left-aligned like the vanilla #Summary text
    ap.append(("SkyyAccTop", SUI.label("SkyyAccBonus", "", "propValue", h=ACC_LINE_H, wrap=False)))   # a value, not a result line
    ap.append(("SkyyAccTop", SUI.group("SkyyAccBonCols", "Left", h=ACC_BON_ROWS * ACC_BON_H)))
    for c in range(2):
        col = "SkyyAccBonC%d" % c
        ap.append(("SkyyAccBonCols", SUI.group(col, "Top", w=ACC_BON_W, h=ACC_BON_ROWS * ACC_BON_H)))
        for r in range(ACC_BON_ROWS):
            k = c * ACC_BON_ROWS + r
            ap.append((col, SUI.group("SkyyAccBr%d" % k, "Left", w=ACC_BON_W, h=ACC_BON_H)))
            ap.append(("SkyyAccBr%d" % k, SUI.label("SkyyAccBk%d" % k, "", "propKey", w=ACC_BON_KEY_W, h=ACC_BON_H, wrap=False,
                                                    anchor={"right": 8})))
            ap.append(("SkyyAccBr%d" % k, SUI.label("SkyyAccBon%d" % k, "", "propValue", w=ACC_BON_VAL_W, h=ACC_BON_H, wrap=False)))
    ap.append((body, SUI.group("SkyyAccCols", "Left", h=ACC_COLS_H)))
    ap.append(("SkyyAccCols", SUI.panel("SkyyAccLeft", "well", w=ACC_COL_W, h=ACC_COLS_H, pad=ACC_LIST_PAD)))
    ap.append(("SkyyAccCols", SUI.panel("SkyyAccRight", "well", w=ACC_COL_W, h=ACC_COLS_H, pad=ACC_LIST_PAD, anchor={"left": ACC_COL_GAP})))
    ap.append(("SkyyAccLeft", SUI.section("SkyyAccSlotsH", "")))                      # "Bag slots - 3 of 18 used" (b.set)
    ap.append(("SkyyAccLeft", SUI.group("SkyyAccSlotRows", "Top", h=ACC_ROWS_H)))
    ap.extend(acc_pager("SkyyAccLeft", "SkyyAccSp", sp))
    ap.append(("SkyyAccRight", SUI.section("SkyyAccInvH", "Accessories in your inventory")))
    ap.append(("SkyyAccRight", SUI.group("SkyyAccInvRows", "Top", h=ACC_ROWS_H)))
    ap.extend(acc_pager("SkyyAccRight", "SkyyAccIp", ip))
    ap.append((body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})))
    ap.append((body, SUI.status_line("SkyyAccInfo", ACC_INFO_COLOR, h=ACC_INFO_H, wrap=True)))
    ap.sets.append(("SkyyAccSlotsH", "Text", head))
    ap.sets.append(("SkyyAccBonus", "Text", bonus))
    assert len(bon) == BONUS_MAX and all(len(kv) == 2 for kv in bon), "bon = %d (key, value) pairs" % BONUS_MAX
    for k in range(BONUS_MAX):
        ap.sets.append(("SkyyAccBk%d" % k, "Text", bon[k][0]))
        ap.sets.append(("SkyyAccBon%d" % k, "Text", bon[k][1]))
    ap.sets.append(("SkyyAccInfo", "Text", info))
    SUI.fit([ACC_LINE_H, ACC_LINE_H, ACC_BON_ROWS * ACC_BON_H], ACC_TOP_H - 2 * ACC_TOP_PAD, "top well")
    SUI.fit([ACC_BON_W, ACC_BON_W], sh.inner_w - 2 * 8, "bonus columns")
    SUI.fit([ACC_BON_KEY_W, 8, ACC_BON_VAL_W], ACC_BON_W, "bonus row")
    SUI.fit([ACC_COL_W, ACC_COL_GAP, ACC_COL_W], sh.inner_w, "columns")
    SUI.fit([ACC_SEC_H, ACC_ROWS_H, ACC_PG_H], ACC_COLS_H - 2 * ACC_LIST_PAD, "list well")
    SUI.fit([ACC_ROW_H + ACC_ROW_GAP] * PAGE_ROWS, ACC_ROWS_H, "one page of rows")
    SUI.fit([ACC_PANEL_W, 4, ACC_ACT_W], ACC_COL_IN, "row in the well")
    SUI.fit([ACC_ROW_PAD, ACC_BAR, ACC_ICON_BOX, ACC_TEXT_W, ACC_ROW_PAD], ACC_PANEL_W, "row panel")
    left = sh.fit([ACC_TOP_H, ACC_COLS_H, ACC_SEP_H, ACC_INFO_H], "accessory page body")
    assert left == 0 and sh.inner_w == 2 * ACC_COL_W + ACC_COL_GAP, "the body must be filled exactly (no FlexWeight filler): %d px left" % left
    return sh


def acc_page_row_box(ap, col, rid):
    """The row container #<rid> (a bag slot or an inventory row: LayoutMode Left, 56 + 3) in the row group col."""
    ap.append((col, SUI.group(rid, "Left", h=ACC_ROW_H, anchor={"bottom": ACC_ROW_GAP})))


def acc_page_row_full(ap, rid, act_id, act_text, item, name, rarity, colr):
    """A filled row inside #<rid>: the WorldEventListRow look with fixed widths - the row panel #<rid>P (#101925(0.55), padding 8) with
    the status bar, the item icon #<rid>Ic (ItemIcon: the item id only, metadata-free), the name #<rid>Nm (18 px bold) + the rarity
    word #<rid>Rr (15 px), both in the rarity colour colr and b.set - then the small Secondary action button act_id."""
    ap.append((rid, SUI.panel(rid + "P", "row", w=ACC_PANEL_W, h=ACC_ROW_H, layout="Left", pad={"left": ACC_ROW_PAD, "right": ACC_ROW_PAD})))
    ap.append((rid + "P", SUI.group(rid + "Bar", None, w=4, anchor={"right": 8}, extra="Background: " + SUI.COLOR["selected"])))
    ap.append((rid + "P", SUI.group(rid + "Ib", None, w=ACC_ICON_BOX, h=ACC_ROW_H)))
    ap.append((rid + "Ib", SUI.item_icon(rid + "Ic", item, ACC_ICON, anchor={"left": 0, "top": (ACC_ROW_H - ACC_ICON) // 2})))
    ap.append((rid + "P", SUI.group(rid + "T", "Top", w=ACC_TEXT_W, h=ACC_ROW_H, pad={"top": ACC_TEXT_TOP})))
    ap.text(rid + "T", rid + "Nm", name, "rowName", h=ACC_NAME_H, col=colr)
    ap.text(rid + "T", rid + "Rr", rarity, "rowSub", h=ACC_SUB_H, col=colr)
    ap.append((rid, SUI.row_action(act_id, act_text, w=ACC_ACT_W)))


def acc_page_row_empty(ap, rid):
    """An empty bag slot inside #<rid>: a static row panel across the well with the grey caption "Empty slot" at the name position."""
    ap.append((rid, SUI.panel(rid + "P", "row", w=ACC_COL_IN, h=ACC_ROW_H, layout="Left", pad={"left": ACC_ROW_PAD, "right": ACC_ROW_PAD})))
    ap.append((rid + "P", SUI.spacer(w=ACC_BAR + ACC_ICON_BOX)))
    ap.append((rid + "P", SUI.label(None, ACC_EMPTY, "caption", w=ACC_COL_IN - 2 * ACC_ROW_PAD - ACC_BAR - ACC_ICON_BOX, h=ACC_ROW_H)))


def acc_page_none():
    """The line in the inventory list when no accessory is carried."""
    return SUI.label(None, ACC_NONE, "caption", h=30, anchor={"left": 2})


def acc_page_state(bonus, bon, info, head, sp, ip, slots, inv, inv_total):
    """The whole page for ONE state, as the chunks build() emits in order (each an Appends: its appends, then its b.set lines):
    slots = the rows of the CURRENT slot page [(slot index, None for an empty slot | (item, name, rarity, colour))], inv = the rows of
    the current inventory page [(index into invIds, (item, name, rarity, colour))], inv_total = how many accessories are carried (0 =
    the "none" line). Values are plain strings or J(expr, sample); the result line's colour stays the J(ACC_INFO_COLOR). Used by the
    build-time check of sample states below and by the harness, which compares these chunks with what the compiled build() sends."""
    sh = acc_page_shell(bonus, bon, info, head, sp, ip)
    chunks = [sh.appends]
    for i, v in slots:
        rid = "SkyyAccSlot" + str(i)
        box = SUI.Appends()
        acc_page_row_box(box, "SkyyAccSlotRows", rid)
        chunks.append(box)
        ap = SUI.Appends()
        if v is None:
            acc_page_row_empty(ap, rid)
        else:
            acc_page_row_full(ap, rid, "SkyyAccUn" + str(i), "Unequip", v[0], v[1], v[2], v[3])
        chunks.append(ap)
    if inv_total == 0:
        chunks.append(SUI.Appends([("SkyyAccInvRows", acc_page_none())]))
    for i, v in inv:
        ap = SUI.Appends()
        acc_page_row_box(ap, "SkyyAccInvRows", "SkyyAccInv" + str(i))
        acc_page_row_full(ap, "SkyyAccInv" + str(i), "SkyyAccEq" + str(i), "Equip", v[0], v[1], v[2], v[3])
        chunks.append(ap)
    return chunks


def acc_page_check(chunks):
    """check_page on a whole state (ids, prefix, no duplicates, every parent created first, every b.set target exists) and the proven
    property table (kit 1.4 assert_proven: only what deployed pages use)"""
    whole = SUI.Appends()
    for c in chunks:
        whole += c
    SUI.assert_proven(whole, what="accessory page")
    return SUI.check_page(whole, ACC_PREFIX)


def _acc_java(ap, indent, known=()):
    """The Java statements of one Appends (appends, then b.set lines), checked first, indented for the build() source."""
    SUI.check_page(ap, ACC_PREFIX, known_parents=[SUI.render(k) for k in known])
    return LF.join(indent + ln for ln in ap.java("b").split(LF))


LF = chr(10)
_I = SUI.J("i", "0")                   # the row's index in build() (slot index / index into invIds); ids like "SkyyAccSlot" + (i) + "Nm"
_SLOT, _INV = "SkyyAccSlot" + _I, "SkyyAccInv" + _I
_Q = SUI.RARITY["Legendary"]           # colour sample of the runtime rarity colour (AccDefs.rarityColor)
# the texts: the Java expressions of build() (b.set never parses markup); safe() stays on the ItemIds (inline markup)
ACC_SH = acc_page_shell(SUI.J(PKG + ".AccDefs.bonusText(s)", "Bonuses - none yet - put accessories in this bag"),
                        [(SUI.J("bl[%d]" % (2 * k), "Stamina"), SUI.J("bl[%d]" % (2 * k + 1), "+6 max Stamina, +20% Stamina Regen"))
                         for k in range(BONUS_MAX)],
                        SUI.J("this.info != null && this.info.length() > 0 ? this.info : " + PKG + ".AccStore.campLine(s)",
                              "equipped Legendary Health Accessory"),
                        SUI.J("slotsHead", "Bag slots - 3 of 18 used"),
                        (SUI.J("slotCaption", "Page 1 / 2"), SUI.J("this.slotPage > 0", "true"), SUI.J("this.slotPage < slotPages - 1", "true")),
                        (SUI.J("invCaption", "Page 1 / 1"), SUI.J("this.invPage > 0", "true"), SUI.J("this.invPage < invPages - 1", "true")))
SUI.check_page(ACC_SH.appends, ACC_PREFIX)
SUI.assert_proven(ACC_SH.appends, what="accessory page shell")
ACC_TOP_JAVA = LF.join("  " + ln for ln in ACC_SH.java("b").split(LF))
_ap = SUI.Appends()
acc_page_row_box(_ap, "SkyyAccSlotRows", _SLOT)
ACC_SLOT_JAVA = _acc_java(_ap, "    ", known=["SkyyAccSlotRows"])
_ap = SUI.Appends()
acc_page_row_full(_ap, _SLOT, "SkyyAccUn" + _I, "Unequip", SUI.J("safe(s[i])", "Skyy_Talisman_Vitality_Epic"),
                  SUI.J(PKG + ".AccDefs.pretty(s[i])", "Legendary Health Accessory"),
                  SUI.J(PKG + ".AccDefs.rarityName(s[i]).toUpperCase()", "LEGENDARY"),
                  SUI.J(PKG + ".AccDefs.rarityColor(s[i])", _Q))
ACC_FULL_JAVA = _acc_java(_ap, "      ", known=[_SLOT])
_ap = SUI.Appends()
acc_page_row_empty(_ap, _SLOT)
ACC_EMPTY_JAVA = _acc_java(_ap, "      ", known=[_SLOT])
ACC_NONE_JAVA = SUI.java_append("SkyyAccInvRows", acc_page_none())
_ap = SUI.Appends()
acc_page_row_box(_ap, "SkyyAccInvRows", _INV)
acc_page_row_full(_ap, _INV, "SkyyAccEq" + _I, "Equip", SUI.J("safe(id)", "Skyy_Accessory_Workbench_T2"),
                  SUI.J(PKG + ".AccDefs.pretty(id)", "Workbench II"),
                  SUI.J(PKG + ".AccDefs.rarityName(id).toUpperCase()", "UNIQUE"),
                  SUI.J(PKG + ".AccDefs.rarityColor(id)", SUI.RARITY["Unique"]))
ACC_INV_JAVA = _acc_java(_ap, "    ", known=["SkyyAccInvRows"])
# build-time check of whole sample states: a full page of slots + 9 inventory rows, an empty bag with nothing carried, a middle page
_full = ("Skyy_Talisman_Speed_Epic", "Legendary Speed Accessory", "LEGENDARY", SUI.RARITY["Legendary"])
_invr = ("Skyy_Accessory_Furnace_T1", "Furnace", "NORMAL", SUI.RARITY["Normal"])
_bon = [("Health", "+24 max Health"), ("Stamina", "+6 max Stamina, +20% Stamina Regen"), ("Mana", "+24% max Mana (at least +4)"),
        ("Regeneration", "Heals 1% max Health every 2 s"), ("Speed", "+10% Speed"), ("Brawler", "+12 Strength"),
        ("Runic", "+12 Magical Power"), ("Stonehide", "switched off"), ("Razorfang", "+8% Crit Chance, +16% Crit Damage"),
        ("Feather", "-40% fall damage, +20% jump height"), ("Combat stats", "need SkyyGear, which is not running"),
        ("Fall damage", "needs SkyySkills, which is not running")]
_nobon = [("", "")] * BONUS_MAX
assert len(_bon) == BONUS_MAX
for _acc_st in (acc_page_state("Bonuses - your best accessory of each line counts", _bon, "", "Bag slots - 9 of 18 used",
                               ("Page 1 / 2", False, True), ("Page 1 / 2", False, True),
                               [(i, _full) for i in range(PAGE_ROWS)], [(i, _invr) for i in range(PAGE_ROWS)], 12),
                acc_page_state("Bonuses - none yet - put accessories in this bag", _nobon, "", "Bag slots - 0 of 18 used",
                               ("Page 1 / 2", False, True), ("Page 1 / 1", False, False), [(i, None) for i in range(PAGE_ROWS)], [], 0),
                acc_page_state("Bonuses - none yet", _nobon, "bag is full, or the same or a better Speed Accessory is already equipped",
                               "Bag slots - 3 of 60 used", ("Page 4 / 7", True, True), ("Page 2 / 2", True, False),
                               [(27, _full), (28, None), (35, _full)], [(9, _invr)], 10)):
    acc_page_check(_acc_st)
print("accessory page: %d x %d on %s, %d static appends + row templates checked (%d rows a page, pagers under both lists)" % (
    ACC_W, ACC_H, KIT_ID, len(ACC_SH.appends), PAGE_ROWS))
# ---- ACC PAGE BLOCK END
ACC_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  this.key = {PKG}.AccStore.pkey(u);   // 0.4.1
  String[] s = {PKG}.AccStore.snapshot(u);
  int cap = {PKG}.AccStore.capOf(s);   // 0.4.4
  // 0.5: the slots this page lists (a slot above this server's limit only while something is still in it), {PAGE_ROWS} a page
  int[] shown = new int[s.length];
  int ns = 0;
  int used = 0;
  for (int i = 0; i < s.length; i++) {{
    if (s[i] != null) used++;
    if (i >= cap && s[i] == null) continue;
    shown[ns] = i;
    ns++;
  }}
  int slotPages = (ns + {PAGE_ROWS} - 1) / {PAGE_ROWS};
  if (slotPages < 1) slotPages = 1;
  if (this.slotPage >= slotPages) this.slotPage = slotPages - 1;
  if (this.slotPage < 0) this.slotPage = 0;
  String slotsHead = "Bag slots - " + used + " of " + cap + " used";
  String slotCaption = "Page " + (this.slotPage + 1) + " / " + slotPages;
  java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);
  this.invIds = new String[inv.size()];
  for (int i = 0; i < inv.size(); i++) this.invIds[i] = (String) inv.get(i);
  int invPages = (inv.size() + {PAGE_ROWS} - 1) / {PAGE_ROWS};
  if (invPages < 1) invPages = 1;
  if (this.invPage >= invPages) this.invPage = invPages - 1;
  if (this.invPage < 0) this.invPage = 0;
  String invCaption = "Page " + (this.invPage + 1) + " / " + invPages;
  String[] bl = {PKG}.AccGear.pageRows(s, u);   // 0.5 part 2: one key / value row per line + the SkyyGear / SkyySkills notes
  // the window, the top well (hint, bonuses), the two list wells (heads, row groups, pagers), the separator and the result line
{ACC_TOP_JAVA}
  for (int q = 0; q < {PAGE_ROWS}; q++) {{
    int k = this.slotPage * {PAGE_ROWS} + q;
    if (k >= ns) break;
    int i = shown[k];
{ACC_SLOT_JAVA}
    if (s[i] != null) {{
{ACC_FULL_JAVA}
      ev.addEventBinding({BT}.Activating, "#SkyyAccUn" + i, {EVD}.of("a", "un:" + i));
    }} else {{
{ACC_EMPTY_JAVA}
    }}
  }}
  if (inv.isEmpty()) {ACC_NONE_JAVA}
  for (int q = 0; q < {PAGE_ROWS}; q++) {{
    int i = this.invPage * {PAGE_ROWS} + q;
    if (i >= inv.size()) break;
    String id = (String) inv.get(i);
{ACC_INV_JAVA}
    ev.addEventBinding({BT}.Activating, "#SkyyAccEq" + i, {EVD}.of("a", "eq:" + i));
  }}
  ev.addEventBinding({BT}.Activating, "#SkyyAccSpPrev", {EVD}.of("a", "sp:prev"));
  ev.addEventBinding({BT}.Activating, "#SkyyAccSpNext", {EVD}.of("a", "sp:next"));
  ev.addEventBinding({BT}.Activating, "#SkyyAccIpPrev", {EVD}.of("a", "ip:prev"));
  ev.addEventBinding({BT}.Activating, "#SkyyAccIpNext", {EVD}.of("a", "ip:next"));
}}"""
for _piece in (ACC_TOP_JAVA, ACC_SLOT_JAVA, ACC_FULL_JAVA, ACC_EMPTY_JAVA, ACC_NONE_JAVA, ACC_INV_JAVA):
    assert _piece in ACC_BUILD_SRC, "kit Java changed on its way into the build() source"   # the f-string pilot: verbatim
assert ACC_BUILD_SRC.count("infoColor(this.info)") == 1 and ACC_BUILD_SRC.count("safe(") == 2, "infoColor once; safe() on the 2 ItemIds only"
page.addMethod(CtNewMethod.make(ACC_INFO_COLOR_SRC, page))   # before build() (javassist: methods before their callers)
page.addMethod(CtNewMethod.make(ACC_BUILD_SRC, page))
''')

# ---------------------------------------------------------------- handleDataEvent: the pagers, 60 slots, invIds of any length, new texts
_HDE_OLD = cut('page.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent(', 'fac.addInterface(pool.get("java.util.function.Function"))', r'''page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    // 0.5: the two pagers move nothing (build() clamps the page numbers)
    if (data.indexOf("sp:prev\\"") >= 0) {{ if (this.slotPage > 0) this.slotPage = this.slotPage - 1; rebuild(); return; }}
    if (data.indexOf("sp:next\\"") >= 0) {{ this.slotPage = this.slotPage + 1; rebuild(); return; }}
    if (data.indexOf("ip:prev\\"") >= 0) {{ if (this.invPage > 0) this.invPage = this.invPage - 1; rebuild(); return; }}
    if (data.indexOf("ip:next\\"") >= 0) {{ this.invPage = this.invPage + 1; rebuild(); return; }}
    String k = {PKG}.AccStore.pkey(u);   // integration pass: ONE storage key for everything this click does (semantics rule 1)
    if (this.key != null && !this.key.equals(k)) {{   // 0.4.1: profile switched since this page was drawn
      this.info = "your profile changed - this is the bag of your current profile now";
      this.slotPage = 0;
      this.invPage = 0;
      rebuild(); return;
    }}
    String blk = {PKG}.AccStore.moveBlock(u);   // integration pass: profile:busy / unknown profile state -> move nothing
    if (blk != null) {{ this.info = blk; rebuild(); return; }}
    {PKG}.AccStore.slotsK(u, k);   // 0.5: load the bag first, so a file that cannot be read is known before anything moves
    if ({PKG}.AccStore.isBad(k)) {{ this.info = "your accessory bag file could not be read - nothing was moved, tell an admin (server log)"; rebuild(); return; }}
    for (int i = 0; i < {PKG}.AccStore.CAP; i++) {{
      if (data.indexOf("un:" + i + "\\"") < 0) continue;
      String id = {PKG}.AccStore.unequipK(u, k, i);
      if (id == null) return;
      String give = {PKG}.AccDefs.modernOf(id);   // 0.4 / 0.5: an old id comes back as the current (upgradable) item
      if (!giveOne(player, give)) {{ {PKG}.AccStore.putK(u, k, i, id); this.info = "your inventory is full"; }}
      else this.info = "unequipped " + {PKG}.AccDefs.pretty(give) + (give.equals(id) ? "" : " - your older copy came back as the current item");
      rebuild(); return;
    }}
    int ni = this.invIds == null ? 0 : this.invIds.length;
    for (int i = 0; i < ni; i++) {{
      if (data.indexOf("eq:" + i + "\\"") < 0) continue;
      if (this.invIds[i] == null) return;
      String id = this.invIds[i];
      if ({PKG}.AccDefs.isRetired(id)) {{   // 0.4.2: retired - refused with the reason, nothing is moved
        this.info = {PKG}.AccDefs.retiredWhy(id);
        try {{ this.playerRef.sendMessage({MSG}.raw("[Accessories] " + {PKG}.AccDefs.retiredChat(id))); }} catch (Throwable t2) {{ }}
        rebuild(); return;
      }}
      String put = {PKG}.AccDefs.modernOf(id);   // 0.4 / 0.5: an old id is stored as its current id
      String why = "bag is full, or the same or a better " + {PKG}.AccDefs.lineLabel(id) + " is already equipped";
      if (!{PKG}.AccStore.canEquipK(u, k, put)) {{ this.info = why; rebuild(); return; }}
      if (!takeOne(player, id)) {{ this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }}
      String res = {PKG}.AccStore.equipK(u, k, put);
      if (res == null) {{
        int g = giveBack(player, u, k, id);
        this.info = g == 0 ? why : (g == 1 ? why + " - it was kept in a free bag slot" : "could not give " + {PKG}.AccDefs.pretty(id) + " back - inventory and bag full, reported to the server log");
        rebuild(); return;
      }}
      if (res.length() > 0) {{
        res = {PKG}.AccDefs.modernOf(res);
        int g = giveBack(player, u, k, res);
        String old = {PKG}.AccDefs.pretty(res);
        this.info = "upgraded to " + {PKG}.AccDefs.pretty(id) + " - " + (g == 0 ? old + " returned" : (g == 1 ? old + " kept in the bag - inventory full" : old + " could not be returned - reported to the server log"));
      }}
      else this.info = "equipped " + {PKG}.AccDefs.pretty(put) + (put.equals(id) ? "" : " - converted from an older copy");
      rebuild(); return;
    }}
  }} catch (Throwable t) {{ {PKG}.AccStore.warn("bag page event failed: " + t); }}
}}""", page))

''')

# ---------------------------------------------------------------- commands, give, restamp task, notice
_CMDS = r'''# ================= 0.5 admin give helpers (AccAdmin), the delivery task (AccGiveTask), acc:fn:give (AccGiveFn) =================
JM(adm, r"""
public static void msg(@PR@ pr, String t) {
  if (pr == null) return;
  try { pr.sendMessage(@MSG@.raw("[Accessories] " + t)); } catch (Throwable e) { }
}""")
# the words after the sub-command word ("accessories give Skyy Skyy_Talisman_Speed_Epic 2" -> "Skyy Skyy_Talisman_Speed_Epic 2"; SkyyGear's rest)
JM(adm, r"""
public static String rest(@CTX@ ctx, String word) {
  String line = "";
  try { line = ctx.getInputString(); } catch (Throwable t) { line = ""; }
  if (line == null) return "";
  String[] tk = line.trim().split("\\s+");
  StringBuilder sb = new StringBuilder();
  boolean seen = false;
  for (int i = 0; i < tk.length; i++) {
    if (!seen) { if (tk[i].equalsIgnoreCase(word) || tk[i].equalsIgnoreCase("/" + word)) seen = true; continue; }
    if (sb.length() > 0) sb.append(' ');
    sb.append(tk[i]);
  }
  return sb.toString().trim();
}""")
JM(adm, r"""
public static @PR@ findPlayer(String name) {
  if (name == null) return null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(name.trim())) return (@PR@) o;
    }
  } catch (Throwable t) { }
  return null;
}""")
JM(adm, r"""
public static int amountOf(String t) {
  try {
    int n = Integer.parseInt(t.trim());
    return n >= 1 && n <= 64 ? n : -1;
  } catch (Throwable e) { return -1; }
}""")
# which ids /accessories give takes: the booster table ids, the active bench accessories (up to their top tier), the Omni and the bag
# item; never an old (legacy) id or a retired accessory. null = fine, else the reason (no ids in it: admins see ids via /accessories lines)
JM(adm, r"""
public static String giveable(String id) {
  if (id == null || id.length() == 0) return "no item id given";
  if (@PKG@.AccDefs.isBoosterId(id)) return null;
  if (@PKG@.AccDefs.BAG.equals(id) || @PKG@.AccDefs.OMNI.equals(id)) return null;
  if (@PKG@.AccDefs.isLegacy(id)) return "that is an old id - give its current id instead (/accessories lines shows them)";
  if (@PKG@.AccDefs.isRetired(id)) return "that accessory is retired and does nothing";
  String bn = @PKG@.AccDefs.benchOf(id);
  if (bn != null && !@PKG@.AccDefs.isTalisman(id)) {
    int t = @PKG@.AccDefs.tierOf(id);
    for (int i = 0; i < @PKG@.AccDefs.BENCH_IDS.length; i++) {
      if (@PKG@.AccDefs.BENCH_IDS[i].equals(bn) && t >= 1 && t <= @PKG@.AccDefs.BENCH_MAX[i] && id.equals("Skyy_Accessory_" + bn + "_T" + t)) return null;
    }
  }
  return "not an accessory of this mod - /accessories lines lists the stat accessory ids";
}""")
gtk.addInterface(pool.get("java.lang.Runnable"))
JF(gtk, "public @PR@ admin;")
JF(gtk, "public @PR@ target;")
JF(gtk, "public String id;")
JF(gtk, "public int n;")
JF(gtk, "public boolean onWorld;")
JF(gtk, "public boolean queued;")
gtk.addConstructor(CtNewConstructor.make(JT("public AccGiveTask(@PR@ admin, @PR@ target, String id, int n) { this.admin = admin; this.target = target; this.id = id; this.n = n; this.onWorld = false; this.queued = false; }"), gtk))
# first run: hop to the TARGET player's world (any thread); second run, on that world thread: refuse while the profile loads, deliver,
# tell the admin (and the player), log one INFO line. admin == null = acc:fn:give called off the world thread. queued = true once
# world.execute accepted the second run (acc:fn:give then returns -1, part 2 review finding 2).
JM(gtk, r"""
public void run() {
  try {
    if (this.target == null || !this.target.isValid()) { @PKG@.AccAdmin.msg(this.admin, "that player left"); return; }
    if (!this.onWorld) {
      java.util.UUID wu = this.target.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.AccAdmin.msg(this.admin, "that player's world is not loaded - try again"); return; }
      this.onWorld = true;
      w.execute(this);
      this.queued = true;
      return;
    }
    String nm = this.target.getUsername();
    if (@PKG@.AccStore.moveBlock(this.target.getUuid()) != null) { @PKG@.AccAdmin.msg(this.admin, nm + "'s profile is loading - nothing was given, try again in a moment"); return; }
    int[] g = @PKG@.AccStore.deliver(this.target, this.id, this.n);
    if (g == null) { @PKG@.AccAdmin.msg(this.admin, "could not reach " + nm + "'s inventory - nothing was given, try again"); return; }
    String item = @PKG@.AccDefs.pretty(this.id);
    @PKG@.AccAdmin.msg(this.admin, "Gave " + g[0] + " x " + item + " to " + nm + (g[2] > 0 ? " (" + g[2] + " dropped at their feet - inventory full)" : ""));
    if (this.admin == null || !this.admin.getUuid().equals(this.target.getUuid())) @PKG@.AccAdmin.msg(this.target, "You got " + g[0] + " x " + item + (g[2] > 0 ? " (" + g[2] + " dropped at your feet - inventory full)" : ""));
    @PKG@.AccCfg.info("give: " + (this.admin == null ? "acc:fn:give" : this.admin.getUsername()) + " gave " + g[0] + " x " + this.id + " to " + nm + " (" + g[1] + " in the inventory, " + g[2] + " dropped)");
  } catch (Throwable t) {
    @PKG@.AccStore.warn("give failed: " + t);
    @PKG@.AccAdmin.msg(this.admin, "give failed - see the server log");
  }
}""")
JM(adm, r"""
public static void giveCmd(@PR@ pr, String rest, boolean byTier) {
  String[] tk = rest == null || rest.trim().length() == 0 ? new String[0] : rest.trim().split("\\s+");
  String id = null;
  int n = 1;
  if (!byTier) {
    if (tk.length < 2 || tk.length > 3) { msg(pr, "usage: /accessories give <player> <item id> [amount 1-64]"); return; }
    id = tk[1];
    if (tk.length == 3) n = amountOf(tk[2]);
  } else {
    if (tk.length < 3 || tk.length > 4) { msg(pr, "usage: /accessories givetier <player> <line> <rarity> [amount 1-64]"); return; }
    int li = @PKG@.AccDefs.lineOf(tk[1]);
    if (li < 0) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < @PKG@.AccDefs.LINE_ADMIN.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.LINE_ADMIN[i]); }
      msg(pr, "unknown line - use one of: " + sb.toString());
      return;
    }
    int t = @PKG@.AccDefs.rarityIndex(tk[2]);
    if (t < 1) { msg(pr, "unknown rarity - use Normal, Unique, Rare, Legendary or 1 to 4"); return; }
    id = @PKG@.AccDefs.idOf(li, t);
    if (tk.length == 4) n = amountOf(tk[3]);
  }
  if (n < 1) { msg(pr, "the amount must be a whole number from 1 to 64"); return; }
  String why = giveable(id);
  if (why != null) { msg(pr, why); return; }
  @PR@ target = findPlayer(tk[0]);
  if (target == null) { msg(pr, "no online player called " + tk[0]); return; }
  new @PKG@.AccGiveTask(pr, target, id, n).run();
}""")
# acc:fn:give (spec 5.9) for the later loot pass: booster table ids only; on the player's world thread it delivers at once and returns how
# many were handed out (counted before and after); from any other thread it hops to that world and logs one line.
# THE RESULT (part 2 review finding 2 - the spec's "returns 0" off the thread made a retry-on-0 caller give twice):
#   n > 0 = given now (counted), 0 = NOTHING given and nothing queued (bad id / amount, player offline, profile loading, inventory not
#   reachable, the player's world not loaded), -1 = QUEUED: the give runs later on the player's world thread and its outcome is only
#   logged (it can still give nothing if the player leaves first). A caller must never retry on -1.
JM(adm, r"""
public static int giveFn(java.util.UUID u, String id, int n) {
  if (u == null || !@PKG@.AccDefs.isBoosterId(id) || n < 1 || n > 64) return 0;
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t) { pr = null; }
  if (pr == null || !pr.isValid()) return 0;
  @REF@ r = pr.getReference();
  @ST@ st = r == null ? null : r.getStore();
  if (st != null && st.isInThread()) {
    if (@PKG@.AccStore.moveBlock(u) != null) return 0;
    int[] g = @PKG@.AccStore.deliver(pr, id, n);
    if (g == null) return 0;
    @PKG@.AccCfg.info("give: acc:fn:give gave " + g[0] + " x " + id + " to " + pr.getUsername() + " (" + g[1] + " in the inventory, " + g[2] + " dropped)");
    return g[0];
  }
  @PKG@.AccGiveTask gt = new @PKG@.AccGiveTask(null, pr, id, n);
  gt.run();
  if (!gt.queued) { @PKG@.AccStore.warn("acc:fn:give was called off " + pr.getUsername() + "'s world thread and could not reach that world - nothing was given, the call returns 0"); return 0; }
  @PKG@.AccStore.warn("acc:fn:give was called off " + pr.getUsername() + "'s world thread - the give runs later on that thread and the call returns -1 (queued: do not retry)");
  return -1;
}""")
gfn.addInterface(pool.get("java.util.function.Function"))
gfn.addConstructor(CtNewConstructor.make("public AccGiveFn() { }", gfn))
JM(gfn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return Integer.valueOf(0);
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String) || !(a[2] instanceof Number)) return Integer.valueOf(0);
    return Integer.valueOf(@PKG@.AccAdmin.giveFn((java.util.UUID) a[0], (String) a[1], ((Number) a[2]).intValue()));
  } catch (Throwable t) { @PKG@.AccStore.warn("acc:fn:give failed: " + t); return Integer.valueOf(0); }
}""")

# ================= 0.5 AccNotice: the one-time chat line (spec 5.1) =================
# Checked by the effect tick (world thread, the player is ready) once per player per session (ASKED, forgotten when they leave): a
# player with a bag file from before (bags/<uuid>.properties or bags/<uuid>-p<N>.properties) gets MIG_NOTICE once, ever (unless
# notice.boosters is off: then nothing is looked at or recorded - no directory scan - so switching it on later still tells them); a
# player without one is recorded as new and never gets it. Seen players live in
# Skyy_SkyyAccessories/notices.properties, saved by AccTick (never the world thread), tmp + fsync + move. An unreadable file is left
# alone and the notice is remembered for this session only.
JF(note, "public static java.nio.file.Path FILE;")
JF(note, "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();")
JF(note, "public static final java.util.concurrent.ConcurrentHashMap ASKED = new java.util.concurrent.ConcurrentHashMap();")
JF(note, "public static volatile boolean DIRTY = false;")
JF(note, "public static boolean BROKEN = false;")
JF(note, "public static boolean SAVEWARNED = false;")
note.addField(CtField.make("public static final String TEXT = %s;" % jlit(MIG_NOTICE), note))
JM(note, r"""
public static void load() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); SEEN.put(k, p.getProperty(k)); }
  } catch (Throwable t) {
    BROKEN = true;
    @PKG@.AccStore.warn("could not read " + FILE + " - the 0.5 notice is remembered for this session only (the file is left untouched): " + t);
  }
}""")
JM(note, r"""
public static boolean hasOldBag(java.util.UUID u) {
  try {
    java.nio.file.Path d = @PKG@.AccStore.DIR;
    if (d == null || !java.nio.file.Files.exists(d, new java.nio.file.LinkOption[0])) return false;
    if (java.nio.file.Files.exists(d.resolve(u.toString() + ".properties"), new java.nio.file.LinkOption[0])) return true;
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(d, u.toString() + "-p*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        String nm = String.valueOf(((java.nio.file.Path) it.next()).getFileName());
        if (!nm.endsWith(".more.properties")) return true;
      }
    } finally { ds.close(); }
  } catch (Throwable t) { }
  return false;
}""")
JM(note, r"""
public static void check(@PR@ pr, java.util.UUID u) {
  if (u == null || pr == null) return;
  String us = u.toString();
  if (SEEN.containsKey(us) || ASKED.containsKey(u)) return;
  if (!@PKG@.AccDefs.NOTICE) return;   // part 1 review finding 3: switched off = nothing looked at or remembered, so switching it on still tells them
  ASKED.put(u, Boolean.TRUE);          // (forgotten when the player leaves: AccTick)
  if (!hasOldBag(u)) { SEEN.put(us, "new"); if (!BROKEN) DIRTY = true; return; }
  SEEN.put(us, "boosters-0.5");
  if (!BROKEN) DIRTY = true;
  pr.sendMessage(@MSG@.raw(TEXT).color("@INFOCOL@"));
}""".replace("@INFOCOL@", SUI.STATUS["="]))
JM(note, r"""
public static synchronized void save() {
  if (!DIRTY || BROKEN || FILE == null) return;
  DIRTY = false;
  try {
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = SEEN.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty((String) e.getKey(), String.valueOf(e.getValue())); }
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyyAccessories one-time notices per player (uuid=boosters-0.5 told / new = joined without accessories)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  } catch (Throwable t) {
    DIRTY = true;
    if (!SAVEWARNED) { SAVEWARNED = true; @PKG@.AccStore.warn("could not save " + FILE + " (retried by the next save): " + t); }
  }
}""")

# ================= 0.5 AccRestampTask: the quality restamp on one player's world thread (dispatched by AccTick every 5 s) =================
rtk.addInterface(pool.get("java.lang.Runnable"))
JF(rtk, "public @PR@ pr;")
JF(rtk, "public java.util.UUID expectedWorld;")
JF(rtk, "public static boolean FAILED = false;")
JF(rtk, "public static volatile long STAMPED = 0L;")
rtk.addConstructor(CtNewConstructor.make(JT("public AccRestampTask(@PR@ pr, java.util.UUID w) { this.pr = pr; this.expectedWorld = w; }"), rtk))
JM(rtk, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID nowWorld = this.pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    if (@PKG@.AccStore.moveBlock(this.pr.getUuid()) != null) return;   // the live inventory may not be the active profile's yet
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    int n = @PKG@.AccStore.restamp(p.getInventory());
    if (n > 0) {   // part 1 review note: admins can see that the restamp ran (one line per player per restamp that changed stacks)
      STAMPED = STAMPED + (long) n;
      @PKG@.AccCfg.info("restamp: " + n + " accessory stack(s) of " + this.pr.getUsername() + " moved to the 0.5 rarity look (" + STAMPED + " since the start)");
    }
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("accessory rarity restamp failed (logged once): " + t); }
  }
}""")

'''
_REL_NEW = r'''# ================= /accessories lines (0.5, every player) =================
lcmd.addConstructor(CtNewConstructor.make("""
public AccLinesCmd() {
  super("lines", "Show every accessory line, its rarities and this server's numbers");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""", lcmd))
JM(lcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    boolean admin = false;
    try { admin = pr.hasPermission("skyyaccessories.admin"); } catch (Throwable t0) { admin = false; }
    pr.sendMessage(@MSG@.raw("[Accessories] Accessory lines on this server - only your best accessory of each line counts, and every line stops at Legendary:"));
    String[] ls = @PKG@.AccDefs.linesText(admin);
    for (int i = 0; i < ls.length; i++) pr.sendMessage(@MSG@.raw("  " + ls[i]));
  } catch (Throwable t) {
    @PKG@.AccStore.warn("/accessories lines failed: " + t);
    pr.sendMessage(@MSG@.raw("[Accessories] could not list the lines - see the server log"));
  }
}""")
# ================= /accessories give | givetier (0.5, server admins only) =================
# COMMAND RULES: an admin sub-command under a player command needs requirePermission AND setPermissionGroups(new String[0]) (lint
# perm_group_leaks). The arguments are read from the raw command text (setAllowsExtraArguments, SkyyGear's /gear give way), so there is
# no usage variant and [amount] is simply an optional last word.
gcmd.addConstructor(CtNewConstructor.make("""
public AccGiveCmd() {
  super("give", "(admin) Give an accessory: /accessories give <player> <item id> [amount]");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""", gcmd))
JM(gcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.AccAdmin.giveCmd(pr, @PKG@.AccAdmin.rest(ctx, "give"), false); }
  catch (Throwable t) { @PKG@.AccStore.warn("/accessories give failed: " + t); @PKG@.AccAdmin.msg(pr, "give failed - see the server log"); }
}""")
tcmd.addConstructor(CtNewConstructor.make("""
public AccGiveTierCmd() {
  super("givetier", "(admin) Give by line and rarity: /accessories givetier <player> <line> <rarity> [amount]");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""", tcmd))
JM(tcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.AccAdmin.giveCmd(pr, @PKG@.AccAdmin.rest(ctx, "givetier"), true); }
  catch (Throwable t) { @PKG@.AccStore.warn("/accessories givetier failed: " + t); @PKG@.AccAdmin.msg(pr, "give failed - see the server log"); }
}""")

# ================= /accessories =================
cmd.addConstructor(CtNewConstructor.make("""
public AccCmd() {
  super("accessories", "Open your accessory bag");
  addAliases(new String[] { "acc", "accbag" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });   // 0.4: COMMAND RULES - ordinary players lack the auto node
  addSubCommand(new com.skyy.accessories.AccReloadCmd());   // 0.4.4: server admins only (its own groups are cleared)
  addSubCommand(new com.skyy.accessories.AccLinesCmd());    // 0.5: every player (its own hytale:Adventurer group)
  addSubCommand(new com.skyy.accessories.AccGiveCmd());     // 0.5: server admins only (its own groups are cleared)
  addSubCommand(new com.skyy.accessories.AccGiveTierCmd()); // 0.5: server admins only (its own groups are cleared)
}""", cmd))
'''
cut("# ================= /accessories reload (0.4.4, server admins only) =================", _CMD_ANCHOR,

    _CMDS + _REL_OLD + _REL_NEW)

# ---------------------------------------------------------------- AccTick: + the notice save and the restamp dispatch
rep('''tick.addMethod(CtNewMethod.make(f"public void run() {{ {PKG}.AccStore.publishOnline(); {PKG}.AccStore.campCheck(); }}", tick))   # 0.4.3 review fix
''', r'''# 0.4.3 review fix: campCheck; 0.5: the notices file (never saved on a world thread) and one AccRestampTask per online player on its world;
# 0.5 part 2: every player who left loses our gear:extra text and movement entry (AccGear.prune) and the notice's once-a-session mark
JF(tick, "public static boolean PRUNE_WARNED = false;")
JM(tick, r"""
public void run() {
  @PKG@.AccStore.publishOnline();
  @PKG@.AccStore.campCheck();
  try { @PKG@.AccNotice.save(); } catch (Throwable t) { }
  java.util.HashSet online = new java.util.HashSet();
  boolean listed = false;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      online.add(pr.getUuid());
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new @PKG@.AccRestampTask(pr, wu));
    }
    listed = true;
  } catch (Throwable t) { }
  if (!listed) return;   // never prune from a player list that could not be read
  try {
    @PKG@.AccGear.prune(online);
    @PKG@.AccNotice.ASKED.keySet().retainAll(online);
  } catch (Throwable t) {
    if (!PRUNE_WARNED) { PRUNE_WARNED = true; @PKG@.AccStore.warn("removing the bridge keys of players who left failed (logged once): " + t); }
  }
}""")
''')

# ---------------------------------------------------------------- AccEffects: the booster table, one try per publisher, Stamina Regen
cut("# ================= AccEffects: talisman stats", "# ================= plugin =================", r'''# ================= AccEffects: accessory stats (EntityTickingSystem on Player entities, runs on each world's thread) =================
# Pattern copied from TerrariaAddons 1.7.4 (DivingHelmetSystem: putModifier/removeModifier with a StaticModifier under a fixed key;
# BandOfRegenerationSystem: addStatValue(DefaultEntityStatTypes.getHealth(), n); speed through the Skyy movement protocol). Work is
# throttled to once per second per player. 0.5: the numbers come from the booster table (AccDefs.BOOST, live config), a switched-off
# line counts for nothing, and every publisher has its own try + log-once flag (spec 5.4), so one failing part never stops the others.
''' + _EFF_KEEP[0] + r'''# 0.5: set (amt > 0) or remove (amt <= 0) our MAX modifier on one stat, ADDITIVE (never MULTIPLICATIVE: the engine sums every
# multiplicative amount into one factor); only writes when something changes. Throws to the caller's publisher try.
# Never removed on leave or shutdown (as in 0.4.5 and SkyySkills): the modifier is saved with the character, a relog keeps it and the
# next tick corrects it. DEPLOY NOTE (part 2 review finding 3): removing or disabling the mod leaves the last flat bonus on saved
# characters until a later admin cleanup command removes skyyacc_health / skyyacc_stamina / skyyacc_mana.
JM(eff, r"""
public static void modAmt(@ESM@ m, int idx, String key, float amt) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;   // getModifier/putModifier would log "No EntityStatValue found" every second
  @MOD@ cur = m.getModifier(idx, key);
  if (amt <= 0.0f) { if (cur != null) m.removeModifier(idx, key); return; }
  @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, amt);
  if (cur != null && cur.equals(want)) return;
  m.putModifier(idx, key, want);
}""")
# 0.5 Mana: pct of the FLAT max Mana (flatMax: the type max + every other ADDITIVE MAX modifier, ours left out), never less than floor
JM(eff, r"""
public static void manaMod(@ESM@ m, int idx, String key, float pct, float floor) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;
  float amt = 0.0f;
  if (pct > 0.0f) amt = Math.round(flatMax(v, idx, key) * pct) / 100.0f;
  if (floor > amt) amt = floor;
  modAmt(m, idx, key, amt);
}""")
# 0.5 STAMINA REGEN (spec 5.4.1; every call read in HytaleServer.jar bytecode and B.probe'd): the rate vanilla is refilling at RIGHT NOW
# = the sum of amount / interval over the Stamina value's positive ADDITIVE regen entries whose conditions pass
# Condition.allConditionsMet(cb, ref, now, rg) - exactly the check RegeneratingValue.shouldRegenerate makes after its timer step (we
# never call shouldRegenerate / regenerate: they advance the engine's own regen timer); the clock is the store's TimeResource, like
# EntityStatsSystems$Regenerate. The top-up = rate x pct / 100 x the seconds since the last 1 s tick (clamped 0..2), capped at max,
# skipped for a dead player or a full bar, added with addStatValue like the engine. Sprinting / gliding / blocking / the empty-bar pause
# fail those conditions, so the bonus never flows then (sampled once a second: at most one second's bonus either way).
# The rate is the Stamina asset's own ADDITIVE regen entries only (part 2 review finding 4): RegeneratingModifier multipliers and
# armor regen entries are not in it, so "X% faster" and any quoted refill time hold for the vanilla numbers.
JM(eff, r"""
public static void staminaRegen(@ST@ store, @CB@ cb, @REF@ ref, @ESM@ m, float pct, float secs) {
  if (pct <= 0.0f) return;
  int si = @DST@.getStamina();
  if (si < 0) return;
  @ESV@ v = m.get(si);
  if (v == null) return;
  int hi = @DST@.getHealth();
  @ESV@ hv = hi < 0 ? null : m.get(hi);
  if (hv != null && hv.get() <= 0.0f) return;
  float cur = v.get();
  float max = v.getMax();
  if (cur >= max) return;
  @RGV@[] rv = v.getRegeneratingValues();
  if (rv == null || rv.length == 0) return;
  java.time.Instant now = ((@TMR@) store.getResource(@TMR@.getResourceType())).getNow();
  float rate = 0.0f;
  for (int i = 0; i < rv.length; i++) {
    if (rv[i] == null) continue;
    @RGN@ rg = rv[i].getRegenerating();
    if (rg == null || rg.getRegenType() != @RGT@.ADDITIVE) continue;
    float a = rg.getAmount();
    float iv = rg.getInterval();
    if (a <= 0.0f || iv <= 0.0f) continue;
    if (@CND@.allConditionsMet(cb, ref, now, rg)) rate = rate + a / iv;
  }
  if (rate <= 0.0f) return;
  float sec = secs;
  if (sec < 0.0f) sec = 0.0f;
  if (sec > 2.0f) sec = 2.0f;
  float amt = rate * pct / 100.0f * sec;
  if (cur + amt > max) amt = max - cur;
  if (amt > 0.0f) m.addStatValue(si, amt);
}""")
# Movement (0.3 Speed; 0.5 part 2 + Feather): the whole bag is ONE source "accessories.talismans" (layer pct) in the shared movement
# protocol (tools/skyymove.py) - speed 0.10 = +10 %, jump 0.20 = jump HEIGHT x 1.20, fallDamage -0.40 = 40 % less fall damage (the
# config stores the magnitude, the tick adds the minus); all zero removes the entry. MoveSync.sync applies the total of every source:
# baseSpeed = default x clamp((1 + sum flat) x (1 + sum pct), 0.3, 5), jumpForce from the summed jump height (clamped to h0 + 20
# blocks); fall damage is applied ONCE, by the mod holding stat:owner:fallDamage (SkyySkills 0.4.8: its fall filter multiplies by
# MoveSync.fallMultiplier(sums of every source)). Still baseSpeed only for speed (the direction multipliers are factors ON baseSpeed).
# The 0.2 back-off lives on in MoveSync; an unequip restores defaults only for a field still holding the value written. AccGear.MOVED
# remembers who has an entry, so AccTick removes it when they leave (AccGear.prune) and shutdown removes every one.
JM(eff, r"""
public static void move(java.util.UUID u, @PR@ pr, @CB@ cb, @REF@ ref, float speed, float jump, float fall) {
  @PKG@.MoveSync.post(u, @PKG@.AccGear.SOURCE, "pct", speed, jump, fall);
  if (speed != 0.0f || jump != 0.0f || fall != 0.0f) @PKG@.AccGear.MOVED.put(u, Boolean.TRUE);
  else @PKG@.AccGear.MOVED.remove(u);
  @PKG@.MoveSync.sync(u, pr, cb, ref, @PKG@.AccStore.SPEED, "SkyyAccessories");
}""")
# one log-once flag per publisher (spec 5.4; part 2 review finding 1: Health, Stamina and Mana had shared one pools flag, so a
# Health failure hid a later Stamina or Mana failure). F_STAM = the Stamina Regen top-up, F_STAMINA = the max Stamina modifier.
JF(eff, "public static boolean F_HEALTH = false;")
JF(eff, "public static boolean F_STAMINA = false;")
JF(eff, "public static boolean F_MANA = false;")
JF(eff, "public static boolean F_STAM = false;")
JF(eff, "public static boolean F_HEAL = false;")
JF(eff, "public static boolean F_MOVE = false;")
JF(eff, "public static boolean F_GEAR = false;")
JF(eff, "public static boolean F_NOTE = false;")
JM(eff, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  @REF@ ref = null;
  @PR@ pr = null;
  java.util.UUID u = null;
  float[] c = null;
  float secs = 0.0f;
  int[] best = null;
  @ESM@ m = null;
  try {
    ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    u = pr.getUuid();
    c = (float[]) @PKG@.AccStore.CLOCK.get(u);
    if (c == null) { c = new float[] { 1.0f, 0.0f }; @PKG@.AccStore.CLOCK.put(u, c); }
    c[0] = c[0] + dt;
    if (c[0] < 1.0f) return;
    secs = c[0];
    c[0] = 0.0f;
    @PKG@.AccStore.checkEpoch(u);   // 0.4.1: republish acc:has / acc:tal within a second of a profile switch
    best = @PKG@.AccDefs.bestTiers(@PKG@.AccStore.snapshot(u));   // 0.4.1: the ACTIVE profile's bag; only the best rarity of a line
    for (int li = 0; li < best.length; li++) if (!@PKG@.AccDefs.lineOn(li)) best[li] = 0;   // 0.5: a switched-off line counts for nothing
    m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AccStore.warn("accessory effects failed (logged once): " + t); }
    return;
  }
  float[] bo = @PKG@.AccDefs.BOOST;
  // 1. stat pools: max Health and max Stamina flat, max Mana a percent of the flat Mana with a floor (removed at 0)
  if (m != null) {
    try { modAmt(m, @DST@.getHealth(), "skyyacc_health", bo[@E_HF@ * 5 + best[@L_H@]]); }
    catch (Throwable t) { if (!F_HEALTH) { F_HEALTH = true; @PKG@.AccStore.warn("max Health from accessories failed (logged once): " + t); } }
    try { modAmt(m, @DST@.getStamina(), "skyyacc_stamina", bo[@E_SF@ * 5 + best[@L_S@]]); }
    catch (Throwable t) { if (!F_STAMINA) { F_STAMINA = true; @PKG@.AccStore.warn("max Stamina from accessories failed (logged once): " + t); } }
    try { manaMod(m, @DST@.getMana(), "skyyacc_mana", bo[@E_MP@ * 5 + best[@L_M@]], bo[@E_MF@ * 5 + best[@L_M@]]); }
    catch (Throwable t) { if (!F_MANA) { F_MANA = true; @PKG@.AccStore.warn("max Mana from accessories failed (logged once): " + t); } }
  }
  // 2. Stamina Regen top-up (only while vanilla's own refill flows)
  try { if (m != null && best[@L_S@] > 0) staminaRegen(store, cb, ref, m, bo[@E_SR@ * 5 + best[@L_S@]], secs); }
  catch (Throwable t) { if (!F_STAM) { F_STAM = true; @PKG@.AccStore.warn("Stamina Regen from accessories failed (logged once): " + t); } }
  // 3. Regeneration: a percent of the FULL current max Health every regenEverySeconds (the Health bar the item text names)
  try {
    int rt = best[@L_R@];
    if (m != null && rt > 0) {
      c[1] = c[1] + 1.0f;
      if (c[1] >= (float) @PKG@.AccDefs.REGEN_EVERY) {
        c[1] = 0.0f;
        int hi = @DST@.getHealth();
        @ESV@ hv = hi < 0 ? null : m.get(hi);
        if (hv != null) {
          float hnow = hv.get();
          float hmax = hv.getMax();
          float amt = hmax * bo[@E_RP@ * 5 + rt] / 100.0f;
          if (hnow > 0.0f && hnow < hmax) {
            if (hnow + amt > hmax) amt = hmax - hnow;
            m.addStatValue(hi, amt);
          }
        }
      }
    } else c[1] = 0.0f;
  } catch (Throwable t) { if (!F_HEAL) { F_HEAL = true; @PKG@.AccStore.warn("Regeneration from accessories failed (logged once): " + t); } }
  // 4. movement: Speed + Feather (jump height, less fall damage) through the shared protocol (source accessories.talismans, layer
  //    pct, fractions: 0.10 = +10%, fall -0.40 = 40% less)
  try { move(u, pr, cb, ref, bo[@E_SP@ * 5 + best[@L_SP@]] / 100.0f, bo[@E_JU@ * 5 + best[@L_FE@]] / 100.0f, 0.0f - bo[@E_FA@ * 5 + best[@L_FE@]] / 100.0f); }
  catch (Throwable t) { if (!F_MOVE) { F_MOVE = true; @PKG@.AccStore.warn("accessory Speed / Feather failed (logged once): " + t); } }
  // 5. combat stats to SkyyGear: ONE text per player in gear:extra:<uuid> (written only when it changes; AccGear's back-off rules)
  try { @PKG@.AccGear.publish(u, pr.getUsername(), @PKG@.AccGear.textOf(best), System.currentTimeMillis()); }
  catch (Throwable t) { if (!F_GEAR) { F_GEAR = true; @PKG@.AccStore.warn("accessory combat stats for SkyyGear failed (logged once): " + t); } }
  // 6. the one-time 0.5 notice
  try { @PKG@.AccNotice.check(pr, u); }
  catch (Throwable t) { if (!F_NOTE) { F_NOTE = true; @PKG@.AccStore.warn("the 0.5 notice failed (logged once): " + t); } }
}""".replace("@E_HF@", str(KIND_E["maxHealth"])).replace("@E_SF@", str(KIND_E["maxStamina"])).replace("@E_SR@", str(KIND_E["staminaRegen"]))
     .replace("@E_MP@", str(KIND_E["manaPct"])).replace("@E_MF@", str(KIND_E["manaFloor"])).replace("@E_RP@", str(KIND_E["healPct"]))
     .replace("@E_SP@", str(KIND_E["speedPct"])).replace("@L_H@", str(ENTRIES[KIND_E["maxHealth"]][1]))
     .replace("@L_S@", str(ENTRIES[KIND_E["maxStamina"]][1])).replace("@L_M@", str(ENTRIES[KIND_E["manaPct"]][1]))
     .replace("@L_R@", str(ENTRIES[KIND_E["healPct"]][1])).replace("@L_SP@", str(ENTRIES[KIND_E["speedPct"]][1]))
     .replace("@E_JU@", str(KIND_E["jumpPct"])).replace("@E_FA@", str(KIND_E["fallPct"])).replace("@L_FE@", str(ENTRIES[KIND_E["fallPct"]][1])))
assert ENTRIES[KIND_E["staminaRegen"]][1] == ENTRIES[KIND_E["maxStamina"]][1] and ENTRIES[KIND_E["manaFloor"]][1] == ENTRIES[KIND_E["manaPct"]][1]
assert ENTRIES[KIND_E["jumpPct"]][1] == ENTRIES[KIND_E["fallPct"]][1], "Feather's jump and fall are one line"

''')

# ---------------------------------------------------------------- plugin
cut("# ================= plugin =================", "for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_):", r'''# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyAccessoriesPlugin({JPI} init) {{ super(init); }}", pl))
_READY = ("[SkyyAccessories] %s ready (%s) - /accessories (lines; admins: give, givetier, reload), right-click the Accessory Bag; %d bench "
          "accessories + Omni (%d retired kept as items that do nothing - Alchemy Bench, Cooking Bench), Campfire accessory for quick "
          "inventory cooking, %d booster lines in the gear rarities Normal to Legendary (%d items + %d old ids; combat stats to SkyyGear "
          "through gear:extra, Feather's jump and fall through the movement protocol), bag up to %d slots, one "
          "bag per profile when SkyyProfiles runs; ") % (VERSION, KIT_ID, sum(b[3] for b in ACTIVE),
                                                       sum(b[3] for b in BENCHES if b[0] in RETIRED), len(BOOSTERS), len(LINE_IDS),
                                                       len(FOLDED) * len(LEGACY_WORDS), CAP)
JM(pl, r"""
public void setup() {
  @PKG@.AccStore.LOG = getLogger();
  @PKG@.AccStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("bags");
  @PKG@.AccCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("config.properties");   // 0.4.4
  String cs = @PKG@.AccCfg.load(true);   // 0.5: a first start writes the 0.5 file; an existing 0.4.x file is updated ONCE (before CfgPub.start)
  @PKG@.AccNotice.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("notices.properties");   // 0.5
  @PKG@.AccNotice.load();
  com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction.registerSimple(this, @PKG@.SkyyAccessoriesPlugin.class, "SkyyAccBag", new @PKG@.AccPageFactory());
  getCommandRegistry().registerCommand(new @PKG@.AccCmd());
  @PKG@.AccStore.bridge().put("acc:fn:has", new @PKG@.AccFn());
  @PKG@.AccStore.bridge().put("acc:defs", @PKG@.AccDefs.defsText());     // 0.5: every rarity of every line (the later loot pass)
  @PKG@.AccStore.bridge().put("acc:fn:give", new @PKG@.AccGiveFn());     // 0.5: give a booster to an online player (n given now, 0 none, -1 queued: never retry)
  getEntityStoreRegistry().registerSystem(new @PKG@.AccEffects());
  @PKG@.MoveSync.checkProto("SkyyAccessories");
  this.ticker = com.hypixel.hytale.server.core.HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.AccTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log(@READY@ + cs + "; admin settings: SkyWynn Menu -> Server Setup -> Accessories or /accessories reload");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());   // 0.4.4: config:def / config:fn:SkyyAccessories - LAST, after the config load
}""".replace("@READY@", jlit(_READY)))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:has"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:give"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:defs"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccGear.shutdownAll(); } catch (Throwable t) { }   // 0.5 part 2: our gear:extra texts + movement entries
  try { com.skyy.accessories.AccNotice.save(); } catch (Throwable t) { }
  try { com.skyy.accessories.CfgPub.shutdown(); } catch (Throwable t) { }   // 0.4.4: pending config saves + change-log lines now
  super.shutdown();
}""", pl))

''')
rep('''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_):
    c.writeFile(OUT)''', '''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear):
    c.writeFile(OUT)''')

# ---------------------------------------------------------------- assets: qualities, looks, names, tooltips, legacy ids, build checks
_ASSET_OLD = cut('QUAL = ["Common", "Common", "Uncommon"', 'jar = os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)', r'''QUAL = [QUAL_IDS[BENCH_RARITY[min(_t, 7)]] for _t in range(8)]   # 0.5: bench tier -> Skyy_Acc_* (I Normal .. IV+ Legendary; = AccDefs.rarityOf)
files = {}
lang = []
# ---- 0.5 the six quality assets (spec 5.2): the vanilla Common.json field set, SkyyGear's frame art, the kit's rarity colours, the
# label under general.qualities.<id> AND server.general.qualities.<id> (the SkyySacks pattern). Fabled and Mythic ship unused (spec 4.1).
_VQF = set(json.loads(_ASSETS.read("Server/Item/Qualities/Common.json").decode("utf-8-sig")).keys())
_PARTS = set(os.path.basename(n)[:-len(".particlesystem")] for n in _ASSETS.namelist() if n.endswith(".particlesystem"))
def _tex(p):
    q = "Common/" + p
    return q in _COMMON or (q.endswith(".png") and q[:-4] + "@2x.png" in _COMMON)
for _r in range(1, len(DISPLAY)):
    _nm = DISPLAY[_r]
    _tt, _slot, _part = QUAL_ART[_nm]
    _q = {"QualityValue": _r,
          "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % _tt,
          "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltip%sArrow.png" % _tt,
          "SlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "BlockSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "SpecialSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "TextColor": SUI.RARITY[_nm].lower(),
          "LocalizationKey": "server.general.qualities." + QUAL_IDS[_r],
          "VisibleQualityLabel": True,
          "RenderSpecialSlot": True,
          "ItemEntityConfig": {"ParticleSystemId": _part}}
    assert set(_q) == _VQF, "0.5: quality field set differs from vanilla Common.json: %s" % (set(_q) ^ _VQF)
    assert _q["QualityValue"] < 8, "0.5: a quality at 8 or more is 'technical' for SkyyAuctions"
    for _k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        assert _tex(_q[_k]), "0.5: quality texture missing in Assets.zip: " + _q[_k]
    assert _part in _PARTS, "0.5: drop particle missing in Assets.zip: " + _part
    files["Server/Item/Qualities/%s.json" % QUAL_IDS[_r]] = json.dumps(_q, indent=2)
    lang.append("general.qualities.%s=%s" % (QUAL_IDS[_r], _nm))
    lang.append("server.general.qualities.%s=%s" % (QUAL_IDS[_r], _nm))
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, "Icons/ItemsGenerated/Utility_Bag_Seed.png", QUAL_IDS[2],
    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], FIELD_REQ, "SkyyAccBag"), indent=2)
lang.append("items.%s.name=Accessory Bag" % BAG); lang.append("server.items.%s.name=Accessory Bag" % BAG)
d = ("Right-click to open. Holds your accessories. Bench accessories in it let /craft make that bench's recipes straight from your "
     "inventory; stat accessories in it add their bonus (only your best of each line counts); the Omni accessory counts as every bench "
     "accessory.")
lang.append("items.%s.description=%s" % (BAG, d)); lang.append("server.items.%s.description=%s" % (BAG, d))
count = 0
retired_count = 0
# 0.4.2: descriptions of the retired bench accessories (asset kept, no recipe)
RETIRED_TAIL = " This accessory does nothing and cannot be equipped; if one is still in your Accessory Bag, Unequip takes it out."
RETIRED_DESC = {
    "Alchemybench": "Retired. Alchemy is a skill now: brew at a real Alchemy Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
    "Cookingbench": "Retired. Cooking is a skill now: cook at a real Cooking Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
}
assert sorted(RETIRED_DESC) == sorted(RETIRED)
for bench_id, bench_item, name, tiers, ups in BENCHES:
    for t in range(1, tiers + 1):
        iid = "Skyy_Accessory_%s_T%d" % (bench_id, t)
        if t == 1:
            need_item(bench_item)
            rin = [{"ItemId": bench_item, "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}]
        else:
            rin = [{"ItemId": "Skyy_Accessory_%s_T%d" % (bench_id, t - 1), "Quantity": 1}] + [mat(m, q) for m, q in ups[t - 2]]   # 0.2: mat() fixes resource types
        icon = "Icons/ItemsGenerated/%s.png" % ("Bench_Architects" if bench_item == "Bench_Builders" else bench_item)
        node = item(iid, icon, QUAL[min(t, 7)], rin, WB_REQ)
        disp = "%s Accessory %s" % (name, ROMAN[t]) if tiers > 1 else "%s Accessory" % name
        d = "Put it in your Accessory Bag to craft %s recipes%s from your inventory with /craft.%s" % (
            name, (" up to tier %s" % ROMAN[t]) if tiers > 1 else "",
            (" Upgrade it with the same materials the bench needs for tier %s." % ROMAN[t + 1]) if t < tiers else "")
        if bench_id == "Campfire":   # 0.4.3: back as quick inventory cooking (SkyyCooking cook:fn:campfire through SkyySacks /craft)
            d = CAMPFIRE_DESC
        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)
            del node["Recipe"]
            disp += " (retired)"
            d = RETIRED_DESC[bench_id]
            retired_count += 1
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        count += 1
need_item("Ingredient_Bar_Copper"); need_item("Ingredient_Fabric_Scrap_Cotton"); assert "Wood_Trunk" in _RTYPES

# ---- 0.5 THE BOOSTER ITEMS (spec 2.2, 5.6, 5.7): one item per rarity of every line, generated from the booster table.
# Look: the line's crystal fragment MODEL for every rarity; icons Normal crystal fragments, Unique small cluster, Rare large cluster,
# Legendary the gem (each rarity its own icon). Names "<Rarity> <Line> Accessory". Tooltip = vanilla item-text markup: the stat line
# first (<color is="#ffffff">), what it does, the one-per-line rule with the next rarity, an italic flavour line; a line break is the
# two characters \n inside one lang line (a real newline would break the file).
TIP_NL = "\\n"
def _w(t):
    return '<color is="#ffffff">%s</color>' % t
def _n(v):
    return "%g" % v
TIPS = {   # kind -> (stat line, what it does) at one rarity; vals = {kind: number}; kinds without an entry ride along (manaFloor)
    "maxHealth": lambda v: (_w("+%s max Health" % _n(v["maxHealth"])) + " while in your Accessory Bag.",
                            "Raises your maximum Health; the bar fills up by normal means."),
    "maxStamina": lambda v: (_w("+%s max Stamina" % _n(v["maxStamina"])) + " and " + _w("+%s%% Stamina Regen" % _n(v["staminaRegen"])) +
                             " while in your Accessory Bag.",
                             "Your Stamina refills %s%% faster whenever it refills (not while you sprint, glide or block)." % _n(v["staminaRegen"])),
    "manaPct": lambda v: (_w("+%s%% max Mana" % _n(v["manaPct"])) + " (at least +%s) while in your Accessory Bag." % _n(v["manaFloor"]),
                          "A percent of the Mana your level, skills and gear give."),
    "healPct": lambda v: (_w("Heals %s%% of your max Health" % _n(v["healPct"])) + " every %d seconds while in your Accessory Bag." % REGEN_EVERY,
                          "Works in combat too."),
    "speedPct": lambda v: (_w("+%s%% movement speed" % _n(v["speedPct"])) + " while in your Accessory Bag.", "Adds on top of Acrobatics."),
    # part 2 (spec 5.7): the stat line first, what it affects, the requirement (no mod names - players do not know "SkyyGear")
    "str": lambda v: (_w("+%s Strength" % _n(v["str"])) + " while in your Accessory Bag.",
                      "More damage with melee, arrows, thrown weapons and staff melee." + TIP_NL + "Works with gear weapons or bare hands."),
    "mp": lambda v: (_w("+%s Magical Power" % _n(v["mp"])) + " while in your Accessory Bag.",
                     "More damage with spells." + TIP_NL + "Spell shots only (wand, staff, spellbook)."),
    "def": lambda v: (_w("+%s Defense" % _n(v["def"])) + " while in your Accessory Bag.",
                      "Takes a little off every hit." + TIP_NL + "Against hits from mobs and players."),
    "cc": lambda v: (_w("+%s%% Crit Chance" % _n(v["cc"])) + " and " + _w("+%s%% Crit Damage" % _n(v["cd"])) + " while in your Accessory Bag.",
                     "A critical hit does double damage, and Crit Damage makes it hit even harder." + TIP_NL +
                     "Works with gear weapons or bare hands."),
    "fallPct": lambda v: (_w("-%s%% fall damage" % _n(v["fallPct"])) + " and " + _w("+%s%% jump height" % _n(v["jumpPct"])) +
                          " while in your Accessory Bag.", "Softer landings and higher jumps, on top of Acrobatics."),
}
def booster_name(li, t):
    return "%s %s Accessory" % (DISPLAY[t], BOOSTERS[li][2])
def booster_desc(li, t, legacy=False):
    b = BOOSTERS[li]
    vals = dict((kind, v[t - 1]) for _st, kind, v in b[5])
    main = [k for k in vals if k in TIPS]
    assert len(main) == 1, "0.5: line %s needs exactly one tooltip template among %s" % (b[1], list(vals))
    first, what = TIPS[main[0]](vals)
    nxt = ("Next: %s (upgrade it at a Workbench)." if b[8] is not None else "Next: %s.") % booster_name(li, t + 1) if t < 4 else ""
    rule = "Only your best %s Accessory counts. " % b[2] + (nxt if t < 4 else "Legendary is the top rarity.")
    # part 1 review finding 4: an old copy can be refused as a tie (an equal or better one already equipped) and never converted
    old = ""
    if legacy:
        old = TIP_NL + "An older copy: put it in your Accessory Bag once and it becomes the current one" + (
            " (only that one can be upgraded)" if t < 4 else "") + ". If it is refused, an equal or better one is already equipped."
    return first + TIP_NL + what + TIP_NL + rule + old + TIP_NL + TIP_NL + "<i>%s</i>" % b[7]
tal_count = 0
legacy_count = 0
ICONS = {}
for li, b in enumerate(BOOSTERS):
    fam, adm, line, crystal, gem, stats, src, flavour, recipes, style = b
    if crystal is not None:   # crystal style: the crystal fragment model in the line's colour for every rarity (clusters / gems are blocks)
        _v = visual_of("Ingredient_Crystal_" + crystal)
        visuals = [None, _v, _v, _v, _v]
        icons = [None, icon_of("Ingredient_Crystal_" + crystal), icon_of("Rock_Crystal_%s_Small" % crystal),
                 icon_of("Rock_Crystal_%s_Large" % crystal), icon_of(gem)]
    else:                     # part 2 item style (spec 5.6): each rarity copies the model and icon of its own vanilla item
        visuals = [None] + [visual_of(x) for x in gem]
        icons = [None] + [icon_of(x) for x in gem]
    assert len(set(icons[1:])) == 4, "0.5: two rarities of the %s line share an icon: %s" % (adm, icons)
    ICONS[adm] = icons
    for t in range(1, 5):
        iid = LINE_IDS[li * 4 + t - 1]
        if recipes is None:
            rin = []                  # part 2: no recipe (admin give only until the loot pass)
        elif t == 1:
            rin = [mat(m, q) for m, q in recipes[0]]
        else:
            rin = [{"ItemId": LINE_IDS[li * 4 + t - 2], "Quantity": 1}] + [mat(m, q) for m, q in recipes[t - 1]]
        node = item(iid, icons[t], QUAL_IDS[t], rin, WB_REQ, visual=visuals[t])
        if recipes is None:
            del node["Recipe"]
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, booster_name(li, t))); lang.append("server.items.%s.name=%s" % (iid, booster_name(li, t)))
        lang.append("items.%s.description=%s" % (iid, booster_desc(li, t))); lang.append("server.items.%s.description=%s" % (iid, booster_desc(li, t)))
        tal_count += 1
    if style != "word":
        continue              # the new lines have no old ids
    # the old ids (0.2/0.3 Talisman / Ring / Artifact and 0.4's fifth id Legendary): asset kept so owned copies still load and render,
    # NO recipe; the look, name and text of the rarity they count as (players never see ids); equip / unequip turns them into that id
    vis = visuals[1]
    for word, lt in LEGACY_WORDS:
        iid = "Skyy_Talisman_%s_%s" % (fam, word)
        node = item(iid, icons[lt], QUAL_IDS[lt], [], WB_REQ, visual=vis)
        del node["Recipe"]
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, booster_name(li, lt))); lang.append("server.items.%s.name=%s" % (iid, booster_name(li, lt)))
        lang.append("items.%s.description=%s" % (iid, booster_desc(li, lt, True))); lang.append("server.items.%s.description=%s" % (iid, booster_desc(li, lt, True)))

        legacy_count += 1
print("booster items:", tal_count, "old ids kept (no recipe):", legacy_count)

# 0.4 OMNI accessory: Workbench recipe = the max-tier accessory of every bench; counts as all of them (AccDefs.benchList); 0.5 Legendary
omni_in = []
for bench_id, bench_item, name, tiers, ups in ACTIVE:   # 0.4.2: retired benches are no inputs (13 -> 10); 0.4.3: the Campfire is again (11)
    top = "Skyy_Accessory_%s_T%d" % (bench_id, tiers)
    assert "Server/Item/Items/Utility/%s.json" % top in files, top
    omni_in.append({"ItemId": top, "Quantity": 1})
assert len(omni_in) == len(ACTIVE) == 11
assert {"ItemId": "Skyy_Accessory_Campfire_T1", "Quantity": 1} in omni_in   # 0.4.3
files["Server/Item/Items/Utility/%s.json" % OMNI] = json.dumps(item(OMNI, icon_of("Rock_Gem_Diamond"), QUAL_IDS[4], omni_in, WB_REQ), indent=2)
lang.append("items.%s.name=Omni Accessory" % OMNI); lang.append("server.items.%s.name=Omni Accessory" % OMNI)
d = ("Legendary accessory. Keep it in your Accessory Bag and it counts as EVERY bench accessory at its highest tier (%s), so /craft shows "
     "all of their recipes. It has its own slot rule, so it can sit next to other bench accessories. Crafted at a Workbench from all %d "
     "top-tier bench accessories. Campfire dishes made through it are quick inventory cooking, like the Campfire accessory. Alchemy "
     "and Cooking are table-only, so the retired Alchemy Bench and Cooking Bench accessories are not part of it and are not covered.") % (", ".join(("%s %s" % (b[2], ROMAN[b[3]])) if b[3] > 1 else b[2] for b in ACTIVE), len(ACTIVE))
lang.append("items.%s.description=%s" % (OMNI, d)); lang.append("server.items.%s.description=%s" % (OMNI, d))
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
print("accessory items:", count, "retired (no recipe):", retired_count)
# 0.4.2 build check: no generated recipe takes a retired bench accessory, and no retired accessory has a recipe
_RET_IDS = set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in BENCHES if b[0] in RETIRED for t in range(1, b[3] + 1))
assert retired_count == len(_RET_IDS) == 5, (retired_count, sorted(_RET_IDS))   # 0.4.3: Alchemy Bench T1-T4 + Cooking Bench
for _fn, _body in files.items():
    if not _fn.endswith(".json") or not _fn.startswith("Server/Item/Items/"):
        continue
    _node = json.loads(_body)
    _iid = os.path.basename(_fn)[:-5]
    if _iid in _RET_IDS:
        assert "Recipe" not in _node, "retired accessory still has a recipe: " + _iid
    for _inp in (_node.get("Recipe") or {}).get("Input", []):
        assert _inp.get("ItemId") not in _RET_IDS, "%s still takes the retired %s" % (_iid, _inp.get("ItemId"))
# 0.4.3 build check: the Campfire accessory is back - the 0.4.1 Workbench recipe, its own name + description, an Omni input; 0.5 Normal
_CF = "Skyy_Accessory_Campfire_T1"
assert _CF not in _RET_IDS
_cfn = json.loads(files["Server/Item/Items/Utility/%s.json" % _CF])
assert (_cfn.get("Recipe") or {}).get("Input") == [{"ItemId": "Bench_Campfire", "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}], _cfn.get("Recipe")
assert _cfn["Recipe"]["BenchRequirement"] == WB_REQ and _cfn["Quality"] == QUAL_IDS[1], _cfn
for _pre in ("items.", "server.items."):
    assert (_pre + _CF + ".name=Campfire Accessory") in lang, _pre
    assert (_pre + _CF + ".description=" + CAMPFIRE_DESC) in lang, _pre
assert not any(l.startswith(("items." + _CF + ".", "server.items." + _CF + ".")) and "etired" in l for l in lang), "Campfire text still says retired"
_omn = json.loads(files["Server/Item/Items/Utility/%s.json" % OMNI])["Recipe"]["Input"]
assert sorted(i["ItemId"] for i in _omn) == sorted("Skyy_Accessory_%s_T%d" % (b[0], b[3]) for b in ACTIVE) and len(_omn) == 11, _omn
print("campfire accessory: recipe back, Omni input %d of %d, retired ids: %s" % (_omn.index({"ItemId": _CF, "Quantity": 1}) + 1, len(_omn), ", ".join(sorted(_RET_IDS))))


def _booster_asset_checks():
    """0.5 part 1 build checks on the generated assets (research/Booster-Accessories-Spec.md 6.1)"""
    import re as _re
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    assert sorted(quals) == sorted(QUAL_IDS[1:]) and len(quals) == 6, sorted(quals)
    lt = files["Server/Languages/en-US/server.lang"]
    lmap = dict(l.split("=", 1) for l in lt.split("\n") if "=" in l)
    for qid in quals:
        assert lmap.get("general.qualities." + qid) == lmap.get("server.general.qualities." + qid) == qid[len("Skyy_Acc_"):], qid
    # every item's quality is shipped here; an item with a recipe (booster, bench, Omni, bag) is never above Legendary
    for iid, node in items.items():
        assert node["Quality"] in quals, "%s uses quality %s that is not shipped" % (iid, node["Quality"])
        if "Recipe" in node:
            assert QUAL_IDS.index(node["Quality"]) <= MAX_LINE_RARITY, "crafted %s is above Legendary (%s)" % (iid, node["Quality"])
    assert items[OMNI]["Quality"] == QUAL_IDS[4] and items[BAG]["Quality"] == QUAL_IDS[2]
    for b in BENCHES:
        for t in range(1, b[3] + 1):
            assert items["Skyy_Accessory_%s_T%d" % (b[0], t)]["Quality"] == QUAL_IDS[BENCH_RARITY[min(t, 7)]], (b[0], t)
    # the booster ids: exactly 4 rarities Normal..Legendary per line, the Workbench ladder (folded lines), no recipe (part 2 lines),
    # the old ids without a recipe
    for li, b in enumerate(BOOSTERS):
        ids = LINE_IDS[li * 4:li * 4 + 4]
        assert [items[i]["Quality"] for i in ids] == QUAL_IDS[1:5], (b[1], [items[i]["Quality"] for i in ids])
        assert len(set(items[i]["Icon"] for i in ids)) == 4, "%s: two rarities share an icon" % b[1]
        if b[9] != "word":
            assert all("Recipe" not in items[i] for i in ids), "%s: a part 2 line has a recipe (admin give only)" % b[1]
            assert all(i.endswith("_T%d" % (t + 1)) and not i.startswith("Skyy_Accessory_") for t, i in enumerate(ids)), ids
            assert not any(("Skyy_Talisman_%s_%s" % (b[0], w)) in items for w, _t in LEGACY_WORDS), "%s: no old ids" % b[1]
            continue
        for t in range(2, 5):
            assert {"ItemId": ids[t - 2], "Quantity": 1} in items[ids[t - 1]]["Recipe"]["Input"], "%s: the ladder is broken at %s" % (b[1], ids[t - 1])
        for w, t in LEGACY_WORDS:
            lid = "Skyy_Talisman_%s_%s" % (b[0], w)
            assert "Recipe" not in items[lid] and items[lid]["Quality"] == QUAL_IDS[t] and items[lid]["Icon"] == items[ids[t - 1]]["Icon"], lid
            assert lmap["server.items.%s.name" % lid] == lmap["server.items.%s.name" % ids[t - 1]], lid
    assert not any(i.endswith("_Legendary") and i.startswith("Skyy_Talisman_") and "Recipe" in n for i, n in items.items())
    assert not any(inp.get("ItemId", "").startswith("Skyy_Talisman_") and inp.get("ItemId", "").endswith("_Legendary")
                   for n in items.values() for inp in (n.get("Recipe") or {}).get("Input", [])), "a recipe still takes an old _Legendary id"
    # names: exactly "<Rarity> <Line> Accessory" for all 60 stat accessory ids (40 modern + 20 old); lang lines are one line each
    for li, b in enumerate(BOOSTERS):
        for t in range(1, 5):
            assert lmap["items.%s.name" % LINE_IDS[li * 4 + t - 1]] == "%s %s Accessory" % (DISPLAY[t], b[2])
            d = lmap["items.%s.description" % LINE_IDS[li * 4 + t - 1]]
            assert d.startswith('<color is="#ffffff">') and "while in your Accessory Bag." in d.split("\\n")[0], "stat line first: " + d[:80]
            if b[8] is None:
                assert "Workbench" not in d, "a part 2 tooltip promises a Workbench upgrade: " + d
    assert all("\r" not in l for l in lang) and len(lt.split("\n")) == len(lang) + 1, "a lang value holds a real line break"
    # no scrapped name or the old item word in anything a player reads: lang values, Server Setup labels + help (admins), config text
    bad = ("Vitality", "Endurance", "Intelligence", "Talisman")
    for k, v in lmap.items():
        assert not any(w in v for w in bad) and "talisman" not in v.lower(), "a player text says %r: %s=%s" % ([w for w in bad if w in v], k, v)
    for r in CFG_ROWS:
        assert not any(w in r[1] + r[10] for w in bad) and "talisman" not in (r[1] + r[10]).lower(), r[0]
    assert not any(w in CONFIG_TEXT for w in bad) and "talisman" not in CONFIG_TEXT.lower()
    print("booster assets: %d lines x 4 rarities (%d with a Workbench ladder, %d admin give only), %d old ids, 6 qualities (%s), "
          "names and texts checked" % (len(BOOSTERS), len(FOLDED), len(BOOSTERS) - len(FOLDED), len(LEGACY_IDS), ", ".join(DISPLAY[1:])))


_booster_asset_checks()


def _player_literals_check():
    """0.5 build check: no Java string literal of this script says Vitality / Endurance / Intelligence / Talisman / talisman, except
    item ids and id words (the id rules need them), the movement source name and the one notice text (MIG_NOTICE, spec 5.1). Scans every
    string constant / f-string of this script that holds Java (a "public " member) - chat, page, refusal and command texts included."""
    import ast as _ast, re
    tree = _ast.parse(
open(os.path.abspath(__file__), encoding="utf8").read())
    ok_exact = set(["Vitality", "Endurance", "Intelligence", "Talisman", "Ring", "Artifact", "Legendary", "accessories.talismans",
                    "_Talisman", "_Ring", "_Artifact", "Skyy_Talisman_", "T:"])
    id_re = re.compile(r"^Skyy_[A-Za-z0-9_]*$")
    lit_re = re.compile(r'"((?:[^"\\\n]|\\.)*)"')
    n = 0
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Constant) and isinstance(node.value, str):
            txt = node.value
        elif isinstance(node, _ast.JoinedStr):
            txt = "".join(v.value for v in node.values if isinstance(v, _ast.Constant) and isinstance(v.value, str))
        else:
            continue
        if not re.search(r"(^|\n)\s*(public|protected)\s", txt):
            continue
        txt = re.sub(r"//[^\n]*", "", txt)
        for m in lit_re.finditer(txt):
            lit = m.group(1)
            n += 1
            if lit in ok_exact or id_re.match(lit) or lit == jlit(MIG_NOTICE)[1:-1]:
                continue
            if any(w in lit for w in ("Vitality", "Endurance", "Intelligence", "Talisman")) or "talisman" in lit.lower():
                raise SystemExit("0.5: a Java string literal says an old name (players must only see line names): %r" % lit)
    page = [ACC_HINT, ACC_NONE, ACC_EMPTY] + [SUI.render(v) for _p, mk in ACC_SH.appends for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,))] + \
        [SUI.render(v) for _i, _p, v in ACC_SH.all_sets()]

    for t in page:
        if any(w in t for w in ("Vitality", "Endurance", "Intelligence", "Talisman")) or "talisman" in t.lower():
            raise SystemExit("0.5: a page text says an old name: %r" % t[:200])
    print("player texts: %d Java string literals and %d page texts scanned, no old names" % (n, len(page)))


_player_literals_check()

''')
assert "Skyy_Talisman_%s_%s" in _ASSET_OLD and "RARITIES[t]" in _ASSET_OLD
# manifest
rep('''B.manifest("SkyyAccessories", VERSION, "SkyWynn accessory bag: bench accessories unlock /craft (SkyySacks) recipes, stat talismans (Vitality, Endurance, Intelligence, Regeneration, Speed) in rarities Common to Legendary add a percent on top of your flat stats while they sit in the bag; the Omni accessory counts as every bench accessory; speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol; one bag per SkyyProfiles profile when that mod is installed; the Campfire accessory is quick inventory cooking (campfire dishes in /craft at reduced Cooking XP and bonus with SkyyCooking); the Alchemy Bench and Cooking Bench accessories are retired (Alchemy and Cooking are table-only); bag slots, the regeneration interval and the talisman bonuses are server settings (config.properties, editable in game through SkyWynn Menu -> Server Setup). Zero dependencies."''',
    '''B.manifest("SkyyAccessories", VERSION, "SkyWynn accessory bag: bench accessories unlock /craft (SkyySacks) recipes; stat accessories in ten lines (Health, Stamina with Stamina Regen, Mana, Regeneration, Speed, and admin-given Brawler, Runic, Stonehide, Razorfang and Feather - combat stats through SkyyGear, fall damage through SkyySkills) in the gear rarities Normal to Legendary add their bonus while they sit in the bag, only the best of each line counts; the Omni accessory counts as every bench accessory; speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol; up to 60 bag slots (18 by default); one bag per SkyyProfiles profile when that mod is installed; the Campfire accessory is quick inventory cooking (campfire dishes in /craft at reduced Cooking XP and bonus with SkyyCooking); the Alchemy Bench and Cooking Bench accessories are retired; bag slots, every booster number and the line switches are server settings (config.properties, editable in game through SkyWynn Menu -> Server Setup); /accessories lines lists every line. Zero dependencies."''')

# ---------------------------------------------------------------- self-checks on the generated script
for k in KEEP:
    assert k in s, "a block that must stay 0.4.5's changed: %s" % k[:80]
for k in CFG_KEEP + _EFF_KEEP + [_REL_OLD, _CMD_EXEC]:
    assert s.count(k) == 1, "a kept 0.4.5 method is missing or doubled: %s" % k[:80]
assert _EFF_SPEED_OLD not in s and "public static void speed(" not in s, "0.4.5's speed() is replaced by move()"
rep("kit.write(OUT)   # 0.4.4: deferred kit checks (AccCfg.reload / checkBonus exist with the right signatures), then the 7 kit classes",
    "kit.write(OUT)   # 0.4.4: deferred kit checks (0.5: AccCfg.reload / checkBoost exist with the right signatures), then the 7 kit classes")
for gone in ("TALISMANS", "RARITIES[", "in RARITIES", "TIER_NAMES", "TIER_QUAL", "BONUS_DEF", 'FAM["', "AccDefs.VIT", "AccDefs.SPD", "checkBonus",

             "return RARITY[", "RARITY.length", "AccDefs.RARITY[", "pctText(", "_QZ", "talisman effects failed", "bonusLines(",
             "if (@SIC@.addOrDropItemStack(st, r, inv.getCombinedStorageHotbarBackpack(), new @IS@(id, 1))) ok++;"):
    assert gone not in s[s.index("import sys, os, json"):], "0.4.5 name left in the 0.5 code: " + gone

HDE = block("public void handleDataEvent(", "fac.addInterface(")
INFO_SETS = [   # (the assignment as the source spells it, the colour infoColor picks: + green / - red / = info blue)
    ('this.info = "your profile changed - this is the bag of your current profile now";', "="),
    ("this.info = blk;", "-"),
    ('this.info = "your accessory bag file could not be read - nothing was moved, tell an admin (server log)";', "-"),

    ('this.info = "your inventory is full";', "-"),
    ('this.info = "unequipped " + {PKG}.AccDefs.pretty(give) + ', "+"),
    ("this.info = {PKG}.AccDefs.retiredWhy(id);", "-"),
    ("this.info = why;", "-"),
    ('this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory";', "-"),
    ('this.info = g == 0 ? why : (g == 1 ? why + " - it was kept in a free bag slot" : "could not give " + ', "-"),
    ('this.info = "upgraded to " + {PKG}.AccDefs.pretty(id) + " - " + (g == 0 ? old + " returned" : (g == 1 ? old + " kept in the bag '
     '- inventory full" : old + " could not be returned - reported to the server log"));', "+ (- when the old one could not be returned)"),
    ('this.info = "equipped " + {PKG}.AccDefs.pretty(put) + ', "+"),
]
assert HDE.count("this.info = ") == len(INFO_SETS), "handleDataEvent sets %d result texts, INFO_SETS lists %d" % (HDE.count("this.info = "), len(INFO_SETS))
for _a, _c in INFO_SETS:
    assert HDE.count(_a) == 1, "result text changed - decide its colour in AccPage.infoColor: " + _a
assert HDE.count('String why = "bag is full, or the same or a better "') == 1
assert [ln.strip() for ln in s.split(LF) if "ev.addEventBinding(" in ln] == [
    'ev.addEventBinding({BT}.Activating, "#SkyyAccUn" + i, {EVD}.of("a", "un:" + i));',
    'ev.addEventBinding({BT}.Activating, "#SkyyAccEq" + i, {EVD}.of("a", "eq:" + i));',
    'ev.addEventBinding({BT}.Activating, "#SkyyAccSpPrev", {EVD}.of("a", "sp:prev"));',
    'ev.addEventBinding({BT}.Activating, "#SkyyAccSpNext", {EVD}.of("a", "sp:next"));',
    'ev.addEventBinding({BT}.Activating, "#SkyyAccIpPrev", {EVD}.of("a", "ip:prev"));',
    'ev.addEventBinding({BT}.Activating, "#SkyyAccIpNext", {EVD}.of("a", "ip:next"));'], "event bindings"
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert s.count("registerSystem(") == 1, "one registerSystem per class (AccEffects only)"
assert s.index("# ---- ACC PAGE BLOCK START") < s.index("# ---- ACC PAGE BLOCK END") < s.index("page.addMethod(CtNewMethod.make(ACC_BUILD_SRC, page))")
assert s.index("# ---- BOOSTER TABLE START") < s.index("# ---- BOOSTER TABLE END") < s.index("# ================= AccDefs =================")
assert s.index("public static String safe(String t)") < s.index("ACC_BUILD_SRC = f") < s.index("public static int giveBack("), \
    "javassist: build() keeps its place (after safe / carried, before giveBack / handleDataEvent)"
# javassist: methods before their callers across the new classes
for _a, _b in (("public static void msg(@PR@ pr, String t)", "public AccGiveTask(@PR@ admin"), ("public AccGiveTask(@PR@ admin", "public static void giveCmd("),
               ("public static int giveFn(", "public Object apply(Object arg) {\n  try {\n    if (!(arg instanceof Object[]))"),
               ("public static void check(@PR@ pr, java.util.UUID u)", "public void tick(float dt, int idx, @ACH@ chunk"),
               ("public AccRestampTask(@PR@ pr", "public void run() {\n  @PKG@.AccStore.publishOnline();"),
               ("public static String[] statParts(", "public static String[] bonusRows("),
               ("public static int[] deliver(", "public static int giveFn("),
               ("public static int[] giveCount(", "public static int[] deliver("),
               ("public static String[] bonusRows(", "public static String[] pageRows("),
               ("public static boolean sendsGear(", "public static String[] pageRows("),
               ("public static boolean hasFall(", "public static String[] pageRows("),
               ("public static int[] activeTiers(", "public static String[] pageRows("),
               ("public static String[] pageRows(", "public void build("),
               ("public static String textOf(int[] best)", "public void tick(float dt, int idx, @ACH@ chunk"),
               ("public static int publish(java.util.UUID u, String name", "public void tick(float dt, int idx, @ACH@ chunk"),
               ("public static void move(java.util.UUID u", "public void tick(float dt, int idx, @ACH@ chunk"),
               ("public static void prune(java.util.Set online)", "public void run() {\n  @PKG@.AccStore.publishOnline();"),
               ("public static void dropMove(", "public static void prune(java.util.Set online)"),
               ("public static void shutdownAll()", "protected void shutdown()"),
               ("public static Object epochOf(", "public static Object epochMark("),
               ("public static void staminaRegen(", "public void tick(float dt, int idx, @ACH@ chunk"),
               ("public static String migrate()", "public static String load(boolean first)"),
               ("public static String lineLabel(String id)", "public void handleDataEvent(")):
    _ia, _ib = s.find(_a), s.find(_b)
    assert 0 <= _ia < _ib, "javassist order: %s must come before %s" % (_a[:50], _b[:50])
# part 2 review: one log-once flag per publisher; acc:fn:give's -1 = queued
for _f in ("F_HEALTH", "F_STAMINA", "F_MANA", "F_STAM", "F_HEAL", "F_MOVE", "F_GEAR", "F_NOTE"):
    assert s.count("if (!%s) { %s = true;" % (_f, _f)) == 1, "one log-once flag per publisher: " + _f
assert "F_POOLS" not in s
_gf = s[s.index("public static int giveFn("):s.index("gfn.addInterface(")]
assert _gf.count("return -1;") == 1 and _gf.index("if (!gt.queued) {") < _gf.index("return -1;"), "acc:fn:give: -1 only once queued"
assert 'VERSION = "0.5"' in s and "@@" not in s
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.5
print("wrote", dst, "(%d lines; 0.4.5 had %d)" % (s.count(LF), OLD.count(LF)))
