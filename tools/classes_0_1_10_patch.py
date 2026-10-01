"""Derive SkyyClasses/build_skyyclasses_0.1.10.py from the LIVE 0.1.9 (build_skyyclasses_0.1.9.py = the tools/deploy_set.py SET pin).
Run:  python tools/classes_0_1_10_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.10.py   (never --deploy: coordinated deploy)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> classes_0_1_8_patch.py ->
0.1.8 -> classes_0_1_9_patch.py -> the generated 0.1.9 read here; tools/classes_0_1_6_patch.py is NEVER re-run. Edit THIS file, never the
generated build script.

0.1.10 = two of Skyy's 2026-10-01 locks (OPEN-QUESTIONS):
  (1) "id give the warrior kit a wood shield": kit.Warrior default "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1". When a kit is handed
      out (automatic kit, the own class page, /classadmin kit) a SHIELD (Weapon_Shield_*, the first one in the kit) goes into the
      player's OFF-HAND when that is empty, else the normal 0.1.7 kit way (the 9 hotbar slots, the rest = the /class kit claim).
      Engine facts (HytaleServer.jar bytecode, read-only): the off-hand is the ACTIVE slot of the utility section (section id -5,
      InventoryComponent$Utility, DEFAULT_UTILITY_CAPACITY slots; Inventory.getUtilityItem() = Utility.getActiveItem() = the item in
      the active slot, none while the active slot is -1 = a fresh player's). The utility container only takes Utility.Usable items
      (its slot filter; every Weapon_Shield_* asset is usable - asserted from Assets.zip at build time). When an item is MOVED into a
      utility slot the vanilla server makes that slot the active one (InventoryPacketHandler, MoveItemStack: an
      InventoryActiveSlotRequestEvent other systems may cancel / redirect, InventoryUtils.setActiveSlot(ref, -5, slot) and the
      SetActiveSlot(-5, slot) packet). Kit.offhand mirrors exactly that: the active utility slot when it is set and empty, else (no
      active slot) the first empty utility slot made active the vanilla way (serverRequest true); an occupied active slot = the off-hand
      is taken -> the normal way. Counted before / after in the same container (a refused add can never be mistaken for a give).
      Shields stay free for every class (FREE_WEAPONS, no weapon lock). Claims of owed items (/class kit) stay the normal way.
  (2) "Priest heals self" default 50 -> 100 (Skyy: the Priest heals itself as much as each party member). The row label is
      "Priest self-heal (% of what members get)" - Skyy asked for "Priest self-heal (% of what one party member gets)" (50
      characters), the config kit refuses labels over 40 (tools/skyycfg.py emit: SkyyMenu's label column), so the full meaning is
      in the help with Skyy's example: "% of what one party member gets. 100 = the Priest heals as much as each party member. ...".
  ONE-TIME UPDATE of an existing config.properties (ClassCfg.migrate0110, setup() right after FILE is set and BEFORE ClassCfg.load,
  KitMigrate and the config kit; the SkyyGear 0.1.1 migrateStat011 machinery method for method): kit.Warrior is rewritten only when
  its effective line (the last one = what Properties reads, a one-line entry) still holds exactly the old default text
  "Weapon_Sword_Crude:1", priestHeal.selfPercent only when it still holds exactly "50"; any other value is kept and logged once
  ("kit.Warrior=... kept (custom)"; a value already on the new default is silent - Skyy set 100 by hand on the live server, that
  line simply stays); a missing line stays missing (the loader's new code default applies). Value text only (key, separator, CR
  kept), every other byte kept (ISO-8859-1 in and out). CfgHist.snapshot keeps the old file as a History version ("before the
  0.1.10 defaults update") and the rewrite only happens once config-history really holds those bytes (else WARN, untouched, the
  next start retries); CfgRows.atomicWrite; one config-changes.log line per changed key in the kit's scalar-row format (name
  "SkyyClasses 0.1.10", via update) so Server Setup -> Changes can Undo each. Runs once: the marker comment MG_MARK goes on its own
  line right above the first kit.Warrior / priestHeal.selfPercent entry (above its help comment when one sits directly on top),
  else at the top of the file; a file holding the marker is never touched again (a value an admin sets back later stays). The
  0.1.10 default file carries the marker, so a fresh file never updates.
Everything else (the /class page, the shared SKYY CARD block = CARD_SHA of SkyyProfiles 0.1.4, commands, permissions, bridge keys,
class rules, heal maths, arrows, kit states, claims) is 0.1.9's - asserted below. Harness: SkyyClasses/test_skyyclasses_0.1.10.py.
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.9.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.10.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
# the source must be the generated 0.1.9 of the EDITED lineage
assert 'VERSION = "0.1.9"' in s and "GENERATED by tools/classes_0_1_9_patch.py from the LIVE 0.1.8" in s, \
    "build_skyyclasses_0.1.9.py is not the live 0.1.9"
assert "DEF_HEAL_MSG_MS = 10000   # LOCKED Skyy 2026-09-25" in s, "0.1.9 is not the edited-lineage script"
REG0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


def block(a, b, text=None):
    """the text from anchor a (included) to anchor b (excluded) of `text` (default: the CURRENT source)"""
    t = s if text is None else text
    assert t.count(a) == 1 and t.count(b) == 1, (a[:60], b[:60])
    return t[t.index(a):t.index(b)]


# ================================================================================================ blocks that must stay 0.1.9's
CARD_START = "# =====================================================================================================================\n# SKYY CARD"
CARD_END = "# ======================================================================= (end of the shared SKYY CARD block)"
CARD_SHA = "bf659e0208b537a81ac8758d909f81976f03069816ea9dddb300f843a7eaa028"   # = tools/profiles_0_1_4_patch.py + classes_0_1_9_patch.py
_card = block(CARD_START, CARD_END) + CARD_END
assert hashlib.sha256(_card.encode("utf8")).hexdigest() == CARD_SHA, "the 0.1.9 SKYY CARD block is not SkyyProfiles 0.1.4's"
KEEP = [
    _card,                                                                                                    # the shared card component
    block("# ================= ClassPage: /class =================", "# ================= OpenTask:"),      # the whole /class page
    block("# ================= 0.1.6 HealTask:", "# ================= 0.1.6 PriestHealSys:"),              # the heal maths + the heal
    block("# ================= ClassRules:", "# ================= bridge functions ================="),     # the weapon lock
    block("# ================= 0.1.7 Arrows:", "# ================= 0.1.6 HealTask:"),                     # daily arrows
    block("# ================= 0.1.6 KitTask:", "# ================= 0.1.6 Kit, part 2:"),                 # KitTask (mode 0/1/2)
    block("public static void claim(", "# /class kit with nothing owed"),                                     # claims: the normal way
    block("# ================= 0.1.6 KitMigrate:", "# ================= ClassPage: /class ================="),
    block("# ================= 0.1.6 KitHooks", "# ================= 0.1.6 KitMigrate:"),
    block("# ================= ClassStore:", "# ================= ClassRules:"),
]

# ================================================================================================ docstring, Run line, version
rep('''"""SkyyClasses 0.1.9 - build script (javassist via jpype). GENERATED by tools/classes_0_1_9_patch.py from the LIVE 0.1.8 (the EDITED
lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> classes_0_1_8_patch.py -> 0.1.8) - edit the patch, not this file;
classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.10 - build script (javassist via jpype). GENERATED by tools/classes_0_1_10_patch.py from the LIVE 0.1.9 (the EDITED
lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> classes_0_1_8_patch.py -> 0.1.8 -> classes_0_1_9_patch.py -> 0.1.9) -
edit the patch, not this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
0.1.10 (2026-10-01, Skyy's locks - OPEN-QUESTIONS): the Warrior kit's Wood Shield + the Priest self-heal default.
  - kit.Warrior default "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" ("id give the warrior kit a wood shield"). Every kit hand-out
    (automatic, the own class page, /classadmin kit) puts the first SHIELD of the kit (Weapon_Shield_*) into the player's OFF-HAND
    when that is empty (Kit.offhand: the active utility slot when it is set and empty, else the first empty utility slot made the
    active one the vanilla way - the InventoryActiveSlotRequestEvent, InventoryUtils.setActiveSlot(ref, -5, slot), the
    SetActiveSlot packet, exactly what the server does when a player drags an item into a utility slot); a taken off-hand = the
    normal kit way (the 9 hotbar slots, the rest waits for /class kit). Counted before / after. Shields stay free for every class.
  - priestHeal.selfPercent default 50 -> 100 (Skyy: the Priest heals itself as much as each party member); row label "Priest
    self-heal (% of what members get)" (the kit's 40-character label limit), Skyy's example in the help.
  - One-time update of an existing config.properties (ClassCfg.migrate0110 before ClassCfg.load; the SkyyGear 0.1.1 pattern): an
    untouched kit.Warrior=Weapon_Sword_Crude:1 / priestHeal.selfPercent=50 line gets the new default, any other value is kept and
    logged, a missing line stays missing (the new code default applies); History version first (verified), one change-log line
    per changed key (Server Setup -> Changes can Undo it), runs once (marker comment MG_MARK).
  The /class page, the SKYY CARD block, commands, permissions, bridge keys, class rules, heal maths, arrows, kit states and claims
  are 0.1.9's (the patch asserts it).
''')
rep("Run:   python build_skyyclasses_0.1.9.py            -> SkyyClasses/SkyyClasses-0.1.9.jar",
    "Run:   python build_skyyclasses_0.1.10.py           -> SkyyClasses/SkyyClasses-0.1.10.jar")
rep('VERSION = "0.1.9"', 'VERSION = "0.1.10"')

# ================================================================================================ (1) the Warrior kit + the off-hand
WARRIOR_OLD = "Weapon_Sword_Crude:1"
WARRIOR_NEW = "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"
rep('''     "weapon_text": "Swords / Longswords / Spears", "kit": "Weapon_Sword_Crude:1"},''',
    '''     # 0.1.10 (LOCKED Skyy 2026-10-01): + a Wood Shield - it goes into the off-hand when that is empty (Kit.offhand)
     "weapon_text": "Swords / Longswords / Spears", "kit": "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"},''')

# ================================================================================================ (2) the self-heal default + the update's tables
rep("DEF_HEAL_SELF_PCT = 50\n",
    "DEF_HEAL_SELF_PCT = 100     # 0.1.10 (Skyy 2026-10-01): the Priest heals itself as much as each party member (was 50)\n")
rep("HEAL_MSG_MS_MIN, HEAL_MSG_MS_MAX = 1000, 60000\n", '''HEAL_MSG_MS_MIN, HEAL_MSG_MS_MAX = 1000, 60000
# 0.1.10 (LOCKED Skyy 2026-10-01): kit shields go into the OFF-HAND (the active utility slot) when it is empty - Kit.offhand. Only ids
# with this prefix (every one is Utility.Usable in Assets.zip - asserted below; torches / candles / Weapon_Kunai are usable too but
# stay the normal kit way), and only the first such entry of a kit.
OFFHAND_PREFIX = "Weapon_Shield_"
# 0.1.10 one-time update of an existing config.properties (ClassCfg.migrate0110; the SkyyGear 0.1.1 migrateStat011 machinery):
# (key, the 0.1.9 default text, the 0.1.10 default text, what the change means). Only a line still holding EXACTLY the old text changes.
MG_DEFAULTS = [("kit.Warrior", "Weapon_Sword_Crude:1", "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1", "the Warrior kit gets a Wood Shield"),
               ("priestHeal.selfPercent", "50", str(DEF_HEAL_SELF_PCT), "the Priest heals itself as much as each party member")]
# the marker comment (in the 0.1.10 default file and in every updated file): a doc comment with spaces and no "=", so the config kit
# never takes it for a "#key=value" template line; migrate0110 looks for MG_MARK_ID in comment lines only
MG_MARK_ID = "SkyyClasses 0.1.10 defaults"
MG_MARK = ("# %s (Skyy 2026-10-01): the Warrior kit has a Wood Shield (kit.Warrior Weapon_Sword_Crude:1,Weapon_Shield_Wood:1) and the "
           "Priest self-heal is 100 percent of what one party member gets (priestHeal.selfPercent 100)" % MG_MARK_ID)
# the name on the update's config-changes.log lines and its History version: a fixed literal (a later version keeps naming 0.1.10)
MG_WHO = "SkyyClasses 0.1.10"
assert all(32 <= ord(_c) < 127 for _c in MG_MARK + "".join("".join(_t) for _t in MG_DEFAULTS)), "the update texts must be plain ASCII"
assert "=" not in MG_MARK and MG_MARK.startswith("# ") and MG_MARK_ID in MG_MARK, "the marker must be a doc comment"
assert DEF_HEAL_SELF_PCT == HEAL_SELF_MAX == 100, "0.1.10: the self-heal default is 100 (the row maximum)"
''')
# build checks (after the default kit checks): the kit tables, the off-hand prefix vs Assets.zip and the weapon rules
rep('''    print("  %-10s %s" % (_c["name"], _c["kit"] or "(empty)"))
''', '''    print("  %-10s %s" % (_c["name"], _c["kit"] or "(empty)"))
# 0.1.10: the Warrior kit = the update's new default; the old default is the update's old text; shields are free for every class and
# every Weapon_Shield_ item is Utility.Usable (the utility container's slot filter takes it) - else the off-hand step could not work
_WAR = [c for c in CLASSES if c["name"] == "Warrior"][0]
assert _WAR["kit"] == MG_DEFAULTS[0][2] == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and MG_DEFAULTS[0][1] == "Weapon_Sword_Crude:1", \\
    "the Warrior kit default and the 0.1.10 update table disagree"
assert MG_DEFAULTS[1][1] == "50" and MG_DEFAULTS[1][2] == str(DEF_HEAL_SELF_PCT), "the self-heal update table"
assert (OFFHAND_PREFIX, "shields") in FREE_WEAPONS and classify("Weapon_Shield_Wood")[0] == FREE, "shields must stay free for every class"
def _usable(iid, depth=0):
    d = json.loads(_ASSETS.read(_ITEMS[iid]).decode("utf-8-sig"))
    u = d.get("Utility")
    if isinstance(u, dict) and "Usable" in u:
        return bool(u["Usable"])
    if depth > 8 or not d.get("Parent") or d.get("Parent") not in _ITEMS:
        return False
    return _usable(d["Parent"], depth + 1)
_SHIELDS = [i for i in _real if i.startswith(OFFHAND_PREFIX)]
assert _SHIELDS and all(_usable(i) for i in _SHIELDS), "a Weapon_Shield_ item is not Utility.Usable: %s" % [i for i in _SHIELDS if not _usable(i)]
assert not _usable("Weapon_Sword_Crude") and _usable("Weapon_Shield_Wood"), "Utility.Usable read from Assets.zip"
print("  off-hand (0.1.10): the first %s* of a kit goes into an empty off-hand - %d shields, all Utility.Usable" % (OFFHAND_PREFIX, len(_SHIELDS)))
''')

# ================================================================================================ engine types + probes for the off-hand step
rep('''    "DEPCFG": "com.hypixel.hytale.builtin.deployables.config.DeployableConfig",
}''', '''    "DEPCFG": "com.hypixel.hytale.builtin.deployables.config.DeployableConfig",
    # 0.1.10: the off-hand (the vanilla move-into-utility path: request event + active slot + packet)
    "ASRE": "com.hypixel.hytale.server.core.event.events.ecs.InventoryActiveSlotRequestEvent",
    "SAS":  "com.hypixel.hytale.protocol.packets.inventory.SetActiveSlot",
}''')
rep('''pool.get(T["DES"])

cfg  = pool.makeClass(PKG + ".ClassCfg")''', '''# 0.1.10: the off-hand step (Kit.offhand / Kit.select) and the one-time config update (ClassCfg.migrate0110)
for c, m in ((T["INV"], "getUtility"), (T["INV"], "getActiveUtilitySlot"), (T["INV"], "setActiveUtilitySlot"),
             (T["IC"], "addItemStackToSlot"), (T["INVC"], "UTILITY_SECTION_ID"), (T["ST"], "invoke"), (T["REF"], "getStore"),
             (T["ASRE"], "isCancelled"), (T["ASRE"], "getNewSlot"), ("com.hypixel.hytale.server.core.io.PacketHandler", "writeNoCache")):
    B.probe(pool, c, m)
assert int(pool.get(T["INVC"]).getField("UTILITY_SECTION_ID").getConstantValue()) == -5, "the utility section id is -5"
pool.get(T["SAS"])
pool.get(T["DES"])

cfg  = pool.makeClass(PKG + ".ClassCfg")''')

# ================================================================================================ the default file: comments + the marker
rep('''    "# kit.<Class> = item:amount,item:amount (at most %d stacks). In game: Server Setup -> Classes -> Class kits (also 'Use my hotbar')" % KIT_MAX_STACKS,
] + ["kit.%s=%s" % (_c["name"], _c["kit"]) for _c in CLASSES] + [''',
    '''    "# kit.<Class> = item:amount,item:amount (at most %d stacks). In game: Server Setup -> Classes -> Class kits (also 'Use my hotbar')" % KIT_MAX_STACKS,
    "# 0.1.10 (Skyy 2026-10-01): a shield (Weapon_Shield_...) in a kit goes into the off-hand when it is empty, else the hotbar like the rest",
] + [_l for _c in CLASSES for _l in (([MG_MARK] if _c["name"] == "Warrior" else []) + ["kit.%s=%s" % (_c["name"], _c["kit"])])] + [''')
rep('''    "# Numbers locked for now: sharePercent 25, selfPercent 50, radius 16, maxPerHit 10, maxPerSecond 10, party only.",''',
    '''    "# Numbers locked for now: sharePercent 25, selfPercent 100, radius 16, maxPerHit 10, maxPerSecond 10, party only.",
    "# selfPercent = Skyy 2026-10-01: 100 = the Priest heals itself as much as each party member (was 50).",''')

# ================================================================================================ the row: label + help (kit limits 40 / 100)
SELF_LABEL = "Priest self-heal (% of what members get)"
SELF_HELP = "% of what one party member gets. 100 = the Priest heals as much as each party member. 0 = never."
assert len(SELF_LABEL) <= 40 and len(SELF_HELP) <= 100, (len(SELF_LABEL), len(SELF_HELP))
assert not set('"\\') & set(SELF_LABEL + SELF_HELP), "label / help go into a double-quoted Python string"
rep('''    ("priestHeal.selfPercent", "Priest heals self", "priest", "int", str(DEF_HEAL_SELF_PCT), "0", str(HEAL_SELF_MAX), "", "%", "live",
     "The Priest heals this % of what one party member gets. 0 = never heals themself.",''',
    '''    # 0.1.10 (Skyy 2026-10-01): default 100, clearer label (Skyy's "Priest self-heal (%% of what one party member gets)" is 50 characters,
    # the kit allows 40 - the full meaning + Skyy's example are in the help)
    ("priestHeal.selfPercent", "%s", "priest", "int", str(DEF_HEAL_SELF_PCT), "0", str(HEAL_SELF_MAX), "", "%%", "live",
     "%s",''' % (SELF_LABEL, SELF_HELP))

# ================================================================================================ ClassCfg.migrate0110 (after the kit classes exist)
MIG_JAVA = r'''
# ================= 0.1.10 ClassCfg.migrate0110: the one-time update of an existing config.properties (Skyy 2026-10-01) =================
# The SkyyGear 0.1.1 migrateStat011 machinery method for method (reviewed + live): pure text step mgUpdate on the config kit's own parser
# (CfgFile.isComment / key / value / end / valStart), CfgHist.snapshot + mgSaved (no rewrite unless config-history really holds the old
# bytes), CfgRows.atomicWrite, one config-changes.log line per changed key, one INFO line (+ one per kept custom value).
F(cfg, "public static final String[] MG_KEY = %s;" % jarr([t[0] for t in MG_DEFAULTS]))
F(cfg, "public static final String[] MG_OLD = %s;" % jarr([t[1] for t in MG_DEFAULTS]))
F(cfg, "public static final String[] MG_NEW = %s;" % jarr([t[2] for t in MG_DEFAULTS]))
F(cfg, "public static final String[] MG_WHY = %s;" % jarr([t[3] for t in MG_DEFAULTS]))
F(cfg, "public static final String MG_MARK = %s;" % jstr(MG_MARK))
F(cfg, "public static final String MG_MARK_ID = %s;" % jstr(MG_MARK_ID))
F(cfg, "public static final String MG_WHO = %s;" % jstr(MG_WHO))
# a scalar key exactly as java.util.Properties / the loader read it (case-sensitive) -> the MG_KEY index, -1 = none
M(cfg, r"""
public static int mgIdx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < MG_KEY.length; i++) if (MG_KEY[i].equals(k)) return i;
  return -1;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = the marker is already in a comment line
# (nothing to do). Else { new text, "kit.Warrior Weapon_Sword_Crude:1 -> ... (...), ...", String[] kept notes, String[] { key, old, new }* }.
# A key whose LAST live line (the one Properties keeps) is a one-line entry holding exactly the old text is updated: every one-line entry
# of it holding the old text gets the new value (value text only: key, separator and CR stay). Anything else is kept: a custom value
# (noted unless it already is the new default), a continued entry (noted), a missing line (silent). Marker: on its own line right above
# the first kit.Warrior / priestHeal.selfPercent entry - above that entry's help comment when a comment line sits directly on top of it -
# else above line 0 (the start of a logical line by definition, so nothing can continue into the marker). Every line is scanned from
# the start of a logical line, so "a comment right above" is never the tail of a continued entry. Never throws for any text.
M(cfg, r"""
public static Object[] mgUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = MG_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int above = -1;
  int com = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MG_MARK_ID) >= 0) return null;
      if (s.trim().length() > 0) com = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int m = mgIdx(@PKG@.CfgFile.key(s));
    if (m >= 0) {
      if (first < 0) { first = k; above = (com >= 0 && com == k - 1) ? com : k; }
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && eff[i].equals(MG_OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(MG_KEY[i]).append(' ').append(MG_OLD[i]).append(" -> ").append(MG_NEW[i]).append(" (").append(MG_WHY[i]).append(')');
      rows.add(MG_KEY[i]);
      rows.add(MG_OLD[i]);
      rows.add(MG_NEW[i]);
    } else if (multi[i] || !eff[i].equals(MG_NEW[i])) {
      kept.add(MG_KEY[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (custom) - the 0.1.10 default is " + MG_NEW[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = mgIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(MG_OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + MG_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int at = first >= 0 ? above : 0;
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MG_MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MG_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyyClasses)
M(cfg, r"""
public static void mgKit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""")
# CfgHist.snapshot swallows its own errors, so after it the update checks that config-history really holds a copy with exactly these
# bytes (the new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log (SkyyGear 0.1.1
# review finding 3)
M(cfg, r"""
public static boolean mgSaved(byte[] old) {
  String[] have = @PKG@.CfgHist.list(0);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(0, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""")
# one config-changes.log line in the kit's scalar-row format (CfgLog.add without its per-line INFO; the key column = the row key, so
# Server Setup -> Changes undoes it with a plain set back to the old value)
M(cfg, r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + MG_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(), right after FILE is set and BEFORE ClassCfg.load + KitMigrate + CfgPub.start: the file before this update becomes a History
# version (KEEP 10, verified by mgSaved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one
# change-log line per updated key, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by \n ("" = nothing done:
# no file - load() writes the 0.1.10 default with the marker -, marker already there, or a failure - WARN, file untouched, retried at the
# next start)
M(cfg, r"""
public static synchronized String migrate0110() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = mgUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), MG_WHO, "before the 0.1.10 defaults update");
    if (!mgSaved(old)) {
      warn("config.properties NOT updated to the 0.1.10 defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.10 defaults: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no kit.Warrior / priestHeal.selfPercent line still had its 0.1.9 default - nothing changed (0.1.10 defaults marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append('\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    warn("could not update config.properties to the 0.1.10 defaults (the file is used as it is): " + t);
    return "";
  }
}""")
'''
rep('''print("config kit: %d rows, files %s" % (kit.info["rows"], ", ".join(kit.info["files"])))
''', '''print("config kit: %d rows, files %s" % (kit.info["rows"], ", ".join(kit.info["files"])))
''' + MIG_JAVA)

# ================================================================================================ Kit: the off-hand step in every hand-out
rep(r'''M(kit_, r"""
public static void tellGiven(@PR@ pr, String cls, String[] ids, int[] qs, int[] got) {
  int g = @PKG@.KitCfg.total(got);
  int left = @PKG@.KitCfg.total(qs) - g;
  if (g > 0) {
    String first = null;
    for (int i = 0; i < ids.length && first == null; i++) if (got[i] > 0) first = ids[i];
    popup(pr, "Class kit", cls + " kit - " + @PKG@.KitCfg.namesText(ids, got), first);
    tell(pr, "Your " + cls + " kit is in your hotbar: " + @PKG@.KitCfg.listText(ids, got) + ".", false);
    if ("Archer".equals(cls) && @PKG@.ClassCfg.ARROWS_ON) tell(pr, "Archers also get free arrows once a day - type /class arrows.", false);   // 0.1.7
  }
  if (left > 0) tell(pr, left + (left == 1 ? " item" : " items") + " of your " + cls + " kit did not fit your hotbar - make room, then type /class kit to collect " + (left == 1 ? "it." : "them."), true);
}""")''', r'''# 0.1.10: the chat line of a kit that landed (pure, bare-JVM tested): the 0.1.7 line while nothing went into the off-hand, else
# "Your Warrior kit is ready: Sword Crude x1 in your hotbar, Shield Wood x1 in your off-hand."
M(kit_, r"""
public static String givenLine(String cls, String[] ids, int[] got, int[] off) {
  int o = off == null ? 0 : @PKG@.KitCfg.total(off);
  if (o <= 0) return "Your " + cls + " kit is in your hotbar: " + @PKG@.KitCfg.listText(ids, got) + ".";
  int[] hb = new int[got.length];
  for (int i = 0; i < got.length; i++) hb[i] = got[i] - (i < off.length ? off[i] : 0);
  String h = @PKG@.KitCfg.listText(ids, hb);
  return "Your " + cls + " kit is ready: " + (h.length() > 0 ? h + " in your hotbar, " : "") + @PKG@.KitCfg.listText(ids, off) + " in your off-hand.";
}""")
M(kit_, r"""
public static void tellGiven(@PR@ pr, String cls, String[] ids, int[] qs, int[] got, int[] off) {
  int g = @PKG@.KitCfg.total(got);
  int left = @PKG@.KitCfg.total(qs) - g;
  if (g > 0) {
    String first = null;
    for (int i = 0; i < ids.length && first == null; i++) if (got[i] > 0) first = ids[i];
    popup(pr, "Class kit", cls + " kit - " + @PKG@.KitCfg.namesText(ids, got), first);
    tell(pr, givenLine(cls, ids, got, off), false);   // 0.1.10: says where the shield went
    if ("Archer".equals(cls) && @PKG@.ClassCfg.ARROWS_ON) tell(pr, "Archers also get free arrows once a day - type /class arrows.", false);   // 0.1.7
  }
  if (left > 0) tell(pr, left + (left == 1 ? " item" : " items") + " of your " + cls + " kit did not fit your hotbar - make room, then type /class kit to collect " + (left == 1 ? "it." : "them."), true);
}""")
# 0.1.10: the vanilla way an item moved INTO a utility slot becomes the active one (InventoryPacketHandler, MoveItemStack): an
# InventoryActiveSlotRequestEvent other systems may cancel or redirect (serverRequest = true, exactly what the vanilla move passes),
# InventoryUtils.setActiveSlot(ref, -5, slot) through the Inventory facade, then the SetActiveSlot packet tells the client. true = the
# slot is the active one now. Never throws.
M(kit_, r"""
public static boolean select(@PR@ pr, @INV@ inv, int slot) {
  try {
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) return false;
    @ST@ st = ref.getStore();
    if (st == null) return false;
    byte prev = inv.getActiveUtilitySlot();
    if (prev == (byte) slot) return true;
    @ASRE@ ev = new @ASRE@(@INVC@.UTILITY_SECTION_ID, (int) prev, (byte) slot, true);
    st.invoke(ref, ev);
    if (ev.isCancelled()) return false;
    byte ns = ev.getNewSlot();
    if (ns == prev) return false;
    inv.setActiveUtilitySlot(ref, ns, st);
    pr.getPacketHandler().writeNoCache(new @SAS@(@INVC@.UTILITY_SECTION_ID, (int) ns));
    return ns == (byte) slot;
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class kit: could not make utility slot " + slot + " the off-hand: " + t); return false; }
}""")
# 0.1.10 (LOCKED Skyy 2026-10-01): ONE shield into the player's OFF-HAND = the active utility slot (Inventory.getUtilityItem() reads
# exactly that) when it is empty: the active slot when it is set and empty, else (no active slot, -1) the first empty utility slot, made
# the active one (select). An occupied active slot = the off-hand is taken: 0, the shield goes the normal way. Only OFFHAND ids (the
# container's own filter takes only Utility.Usable items anyway). Counted in the same container before / after the add, so a refused add
# (filter, full) is never taken for a give; nothing that can fail sits between the add and the count. Returns 0 or 1 (world thread).
M(kit_, r"""
public static int offhand(@PR@ pr, @PLA@ p, String id) {
  @IC@ u = null;
  @INV@ inv = null;
  int slot = -1;
  boolean pick = false;
  try {
    if (pr == null || p == null || id == null || !id.startsWith(OFFHAND)) return 0;
    inv = p.getInventory();
    if (inv == null) return 0;
    u = inv.getUtility();
    if (u == null) return 0;
    int cap = u.getCapacity();
    int a = inv.getActiveUtilitySlot();
    if (a >= 0 && a < cap) {
      @IS@ cur = u.getItemStack((short) a);
      if (cur != null && !cur.isEmpty()) return 0;
      slot = a;
    } else {
      for (int sl = 0; sl < cap && slot < 0; sl++) {
        @IS@ c = u.getItemStack((short) sl);
        if (c == null || c.isEmpty()) slot = sl;
      }
      if (slot < 0) return 0;
      pick = true;
    }
  } catch (Throwable t0) { @PKG@.ClassCfg.warnLimited("class kit: off-hand check failed (" + id + " goes the normal way): " + t0); return 0; }
  int before = count(u, id);
  try { u.addItemStackToSlot((short) slot, new @IS@(id, 1)); } catch (Throwable t1) { @PKG@.ClassCfg.warnLimited("class kit: could not put " + id + " into the off-hand: " + t1); }
  int added = count(u, id) - before;
  if (added <= 0) return 0;
  if (added > 1) added = 1;
  if (pick) select(pr, inv, slot);
  try { p.markNeedsSave(); } catch (Throwable t2) { }
  return added;
}""")
# 0.1.10: one kit hand-out = the first OFFHAND entry into an empty off-hand (offhand), then everything else - and that shield when the
# off-hand is taken - the 0.1.7 way: the 9 hotbar slots only (put(p, 0, ...)); what does not fit is the /class kit claim (give).
# Returns { int[] got (everything that landed, per entry), int[] off (of that, in the off-hand) }.
M(kit_, r"""
public static Object[] putKit(@PR@ pr, @PLA@ p, String[] ids, int[] qs) {
  int[] off = new int[ids.length];
  int[] rest = new int[ids.length];
  boolean tried = false;
  for (int i = 0; i < ids.length && i < qs.length; i++) {
    rest[i] = qs[i];
    if (!tried && qs[i] > 0 && ids[i] != null && ids[i].startsWith(OFFHAND)) {
      tried = true;
      off[i] = offhand(pr, p, ids[i]);
      rest[i] = qs[i] - off[i];
    }
  }
  int[] hb = put(p, 0, ids, rest);
  int[] got = new int[ids.length];
  for (int i = 0; i < ids.length; i++) got[i] = off[i] + (i < hb.length ? hb[i] : 0);
  return new Object[] { got, off };
}""")''')
rep('''  int[] got = put(p, 0, ids, qs);   // 0.1.7: the hotbar only (LOCKED Skyy 2026-09-25); the rest = the /class kit claim
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  if (full) @PKG@.ClassStore.kitEnd(k, rem);
  else @PKG@.ClassStore.kitMerge(k, cls, rem);
  requeue(k);
  tellGiven(pr, cls, ids, qs, got);
  int g = @PKG@.KitCfg.total(got);
  int left = @PKG@.KitCfg.total(qs) - g;
  String who = pr.getUsername();
  if (admin && by != null && by.isValid()) {
    String what = g > 0 ? @PKG@.KitCfg.listText(ids, got) : "nothing fit";
    by.sendMessage(@MSG@.raw("[Classes] Gave " + who + " the " + cls + " kit: " + what + (left > 0 ? " - " + left + " items wait for them (/class kit)" : "") + ".").color("#8fe39a"));
  }
  @PKG@.ClassCfg.info("class kit: " + who + " (" + k + ") got the " + cls + " kit" + (admin ? " from " + (by == null ? "an admin" : by.getUsername()) : "")
    + " - given " + (g > 0 ? @PKG@.KitCfg.join(ids, got) : "nothing") + (left > 0 ? ", owed " + rem : ""));''',
    '''  Object[] pk = putKit(pr, p, ids, qs);   // 0.1.10: a shield into the empty off-hand, the rest the 0.1.7 way (the hotbar only); the rest = the /class kit claim
  int[] got = (int[]) pk[0];
  int[] off = (int[]) pk[1];
  String rem = @PKG@.KitCfg.rest(ids, qs, got);
  if (full) @PKG@.ClassStore.kitEnd(k, rem);
  else @PKG@.ClassStore.kitMerge(k, cls, rem);
  requeue(k);
  tellGiven(pr, cls, ids, qs, got, off);
  int g = @PKG@.KitCfg.total(got);
  int o = @PKG@.KitCfg.total(off);
  int left = @PKG@.KitCfg.total(qs) - g;
  String who = pr.getUsername();
  if (admin && by != null && by.isValid()) {
    String what = g > 0 ? @PKG@.KitCfg.listText(ids, got) + (o > 0 ? " (" + @PKG@.KitCfg.listText(ids, off) + " in the off-hand)" : "") : "nothing fit";
    by.sendMessage(@MSG@.raw("[Classes] Gave " + who + " the " + cls + " kit: " + what + (left > 0 ? " - " + left + " items wait for them (/class kit)" : "") + ".").color("#8fe39a"));
  }
  @PKG@.ClassCfg.info("class kit: " + who + " (" + k + ") got the " + cls + " kit" + (admin ? " from " + (by == null ? "an admin" : by.getUsername()) : "")
    + " - given " + (g > 0 ? @PKG@.KitCfg.join(ids, got) : "nothing") + (o > 0 ? " (off-hand " + @PKG@.KitCfg.join(ids, off) + ")" : "") + (left > 0 ? ", owed " + rem : ""));''')
rep('''F(kit_, "public static final long INFLIGHT_MS = %dL;" % KIT_INFLIGHT_MS)
''', '''F(kit_, "public static final long INFLIGHT_MS = %dL;" % KIT_INFLIGHT_MS)
F(kit_, "public static final String OFFHAND = %s;" % jstr(OFFHAND_PREFIX))   # 0.1.10: kit ids that go into an empty off-hand
''')

# ================================================================================================ setup(): the update before the loader
rep('''  @PKG@.ClassStore.DIR = base.resolve("players");
  String cfgText = @PKG@.ClassCfg.load();''', '''  @PKG@.ClassStore.DIR = base.resolve("players");
  @PKG@.ClassCfg.migrate0110();   // 0.1.10: an untouched kit.Warrior / priestHeal.selfPercent line -> the new default (once; History first)
  String cfgText = @PKG@.ClassCfg.load();''')

# ================================================================================================ the manifest text (where the shield goes)
rep("every class gets a kit with its basic weapon, straight into the hotbar;",
    "every class gets a kit with its basic weapon, straight into the hotbar (a Warrior's shield into the off-hand);")

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.1.9's changed: %s" % k[:80]
_card2 = block(CARD_START, CARD_END) + CARD_END
assert _card2 == _card and hashlib.sha256(_card2.encode("utf8")).hexdigest() == CARD_SHA, "the SKYY CARD block must stay SkyyProfiles 0.1.4's"
assert s.count("put(p, 0, ids, rest)") == 1 and "put(p, 0, ids, qs)" not in s, "give() hands out through putKit only"
assert s.count("tellGiven(") == 2 and s.count("putKit(") == 2 and s.count("offhand(") == 2 and s.count("select(pr, inv, slot)") == 1
assert s.index("public static Object[] putKit(") < s.index("public static String give("), "methods before callers (javassist)"
assert s.index("@PKG@.ClassCfg.migrate0110();") < s.index("String cfgText = @PKG@.ClassCfg.load();") < s.index("@PKG@.KitMigrate.runOnce();")
assert s.index("kit = CFG.emit(") < s.index("public static synchronized String migrate0110()"), "the update needs the kit classes"
assert "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" in s and 'DEF_HEAL_SELF_PCT = 100 ' in s
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.9 had %d)" % (s.count(LF), OLD.count(LF)))
