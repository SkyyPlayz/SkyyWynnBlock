"""Derive SkyyAccessories/build_skyyaccessories_0.5.10.py from the GENERATED 0.5.9 script (build_skyyaccessories_0.5.9.py = the
tools/deploy_set.py SET pin, written by tools/accessories_0_5_9_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.9 script
stays untouched - never re-run accessories_0_5_9_patch.py on top of this).
Run:  python tools/accessories_0_5_10_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.10.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.10.py   (bare JVM -Xverify:all: class compare 0.5.9 -> 0.5.10, the helmet light run
      on a REAL engine ECS store through AccLanternSys, Lantern-only traces identical to 0.5.9, config, start twice on a live copy)

0.5.10 = THE MINING HELMET LIGHT. Skyy: "make sure that if those mining helmets show a light, it works. there is already a mod that adds
working lantern helmets" (docs/answered/gear.md:72; research/cloud/Mining-Armor-Spec.md section 6).
  - SkyyGear 0.2.15 posts gear:lamp:<uuid> = Integer 1-4 (Normal / Unique / Rare / Legendary Lantern strength) on the skyy.bridge map while
    an ACTIVE (level-ok) Mining Set helmet is worn, and removes it when none / under-level / profile:busy / leave.
  - AccLantern.step (AccLanternSys, the player's world thread, decides at least once a second) now lights the player with
    t = max(best Lantern in the bag (only while line.Lantern is on), AccLantern.helmetTier(u)) - the SAME glow + hidden reach lights as a
    Lantern of that rarity (one light per player: the stronger wins, never stacked). No key = exactly 0.5.9 (the harness compares the
    traces of both jars). Key gone / lower -> the next decision (<= 1 s) drops / lowers the light.
  - helmetTier(u): 0 unless lantern.helmet is on, the bridge value is a Number or a digit String 1-4 (clamped to 4), and
    profile:busy:<uuid> is NOT set (the live inventory may belong to the other profile during a switch). Nothing saved: the bridge key is
    SkyyGear's, our light state is the 0.5.4 in-memory state (pruned on leave, cleared on shutdown).
  - New Server Setup row lantern.helmet ("Mining helmet light", bool, on, live; category lantern): off = mining helmets light nothing
    (Lanterns unchanged). It is independent of line.Lantern (that row says "Lanterns light nothing"; a helmet is not a Lantern).
    The fresh-install default file gets a comment + lantern.helmet=true; an existing file is never rewritten (a missing key = on).
  - Bridge acc:lamp = "on" while lantern.helmet is on, else "off" (setup + every 5 s AccTick; removed on shutdown): SkyyGear 0.2.15 shows
    its tooltip line "Lamp: ..." only while it is "on" (spec 6: no text claiming a light that does not work).
UNVERIFIED (in game only): the light with a real SkyyGear 0.2.15 helmet (the harness posts the bridge key itself, exactly as
SkyyGear's postLamp does: Integer.valueOf(1..4)).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.9.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.10.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.9"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.9"\n' in s and "_gem_order_check()" in s and "helmetTier" not in s, "the source must be the generated 0.5.9 script"
REG0, SYS0 = s.count("registerCommand("), s.count("registerSystem(")

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.9 - build script (derived from the generated build_skyyaccessories_0.5.8.py by tools/accessories_0_5_9_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.9.py            -> SkyyAccessories/SkyyAccessories-0.5.9.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.9.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.9.py             (bare JVM -Xverify:all: every 0.5.8 check + the tab icon + the gem order + the engine
       asset validators)
''', '''"""SkyyAccessories 0.5.10 - build script (derived from the generated build_skyyaccessories_0.5.9.py by tools/accessories_0_5_10_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.10.py            -> SkyyAccessories/SkyyAccessories-0.5.10.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.10.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.10.py             (bare JVM -Xverify:all: class compare 0.5.9 -> 0.5.10, the helmet light on a real ECS
       store, Lantern-only traces = 0.5.9, config, start twice on a live copy)
0.5.10: THE MINING HELMET LIGHT (Skyy: "make sure that if those mining helmets show a light, it works"; full notes in
     tools/accessories_0_5_10_patch.py): while SkyyGear 0.2.15 posts gear:lamp:<uuid> (1-4 = Lantern Normal..Legendary) the player glows
     exactly like a Lantern of that rarity; with a Lantern in the bag too the stronger wins (never stacked); gone within ~1 s after the
     key goes; ignored while profile:busy. Server Setup -> Accessories -> Lantern: "Mining helmet light" (lantern.helmet, on). Bridge
     acc:lamp = "on" / "off" (SkyyGear's tooltip Lamp line). Nothing saved.
''')
rep('VERSION = "0.5.9"\n', 'VERSION = "0.5.10"\n')

# ---------------------------------------------------------------------------------------------------------------- config: the new row
HELM_PY = '''
# 0.5.10: THE MINING HELMET LIGHT (tools/accessories_0_5_10_patch.py) - lantern.helmet: SkyyGear's gear:lamp:<uuid> (1-4) lights the wearer
# like a Lantern of that rarity (the stronger of helmet / bag Lantern wins). Independent of line.Lantern. A missing key = on.
LAN_HELMET_KEY = "lantern.helmet"
LAN_HELMET_LINES = [
    "# Mining helmet light (0.5.10): while a player wears an active SkyyGear mining helmet, they glow like a Lantern of the helmet's",
    "# strength (Copper Normal, Iron and Thorium Unique, Cobalt and Adamantite Rare, Mithril and Onyxium Legendary); with a Lantern in",
    "# the Accessory Bag too, the stronger one lights them (never both). Set lantern.helmet to false to switch helmet lights off.",
    "%s=true" % LAN_HELMET_KEY]
LAN_HELMET_ROW = (LAN_HELMET_KEY, "Mining helmet light", "lantern", "bool", "true", "", "", "", "", "live",
                  "Off = SkyyGear mining helmets light nothing (Lanterns unchanged). Gone within a second.",
                  "field:AccDefs.LAN_HELMET@config.properties:%s" % LAN_HELMET_KEY)
assert all(ord(_c) < 128 for _t in LAN_HELMET_LINES for _c in _t)
assert not any("=" in _l for _l in LAN_HELMET_LINES if _l.startswith("#"))
assert len(LAN_HELMET_ROW[1]) <= 40 and len(LAN_HELMET_ROW[10]) <= 100
'''
rep('''assert len(LAN_ROWS) == 13 and LAN_CONFIG_LINES[-1] == "lantern.shareReach=false" and M55_MARK in LAN_CONFIG_LINES
''', '''assert len(LAN_ROWS) == 13 and LAN_CONFIG_LINES[-1] == "lantern.shareReach=false" and M55_MARK in LAN_CONFIG_LINES
''' + HELM_PY)
rep('''] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + LAN_CONFIG_LINES + [""])''',
    '''] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + LAN_CONFIG_LINES + LAN_HELMET_LINES + [""])''')
rep('''for _b in BOOSTERS] + LAN_ROWS   # 0.5.4: + the Lantern''', '''for _b in BOOSTERS] + LAN_ROWS + [LAN_HELMET_ROW]   # 0.5.4: + the Lantern; 0.5.10: + the mining helmet light''')

# AccDefs field (the kit's field: row target)
rep('''dfs.addField(CtField.make('public static volatile boolean LAN_SHARE = false;', dfs))     # config row lantern.shareReach (fix round)
''', '''dfs.addField(CtField.make('public static volatile boolean LAN_SHARE = false;', dfs))     # config row lantern.shareReach (fix round)
dfs.addField(CtField.make('public static volatile boolean LAN_HELMET = true;', dfs))     # 0.5.10: config row lantern.helmet (mining helmet light)
''')
# AccCfg: the key, the loader
rep('''cfg_.addField(CtField.make('public static final String LAN_SHARE_KEY = "%s";' % LAN_SHARE_KEY, cfg_))   # fix round
''', '''cfg_.addField(CtField.make('public static final String LAN_SHARE_KEY = "%s";' % LAN_SHARE_KEY, cfg_))   # fix round
cfg_.addField(CtField.make('public static final String LAN_HELMET_KEY = "%s";' % LAN_HELMET_KEY, cfg_))   # 0.5.10
''')
rep('''  boolean lanShare = boolIn(p.getProperty(LAN_SHARE_KEY), false, LAN_SHARE_KEY);   // the fix round: the reach light shown to everyone (off)
''', '''  boolean lanShare = boolIn(p.getProperty(LAN_SHARE_KEY), false, LAN_SHARE_KEY);   // the fix round: the reach light shown to everyone (off)
  boolean lanHelmet = boolIn(p.getProperty(LAN_HELMET_KEY), true, LAN_HELMET_KEY);   // 0.5.10: the mining helmet light (on)
''')
rep('''  @PKG@.AccDefs.LAN_SHARE = lanShare;
''', '''  @PKG@.AccDefs.LAN_SHARE = lanShare;
  @PKG@.AccDefs.LAN_HELMET = lanHelmet;   // 0.5.10
''')
rep('''  if (lanShare) res = res + ", Lantern reach light shown to everyone";
''', '''  if (lanShare) res = res + ", Lantern reach light shown to everyone";
  if (!lanHelmet) res = res + ", mining helmet light switched off";   // 0.5.10
''')

# ---------------------------------------------------------------------------------------------------------------- AccLantern
HELM_JAVA = '''# 0.5.10 THE MINING HELMET LIGHT: SkyyGear 0.2.15's gear:lamp:<uuid> (Integer 1-4 = the Lantern rarity of the worn active mining helmet)
# -> the tier this player's helmet asks for (0 = none): only while lantern.helmet is on and the profile is not switching (profile:busy).
# A Number or a digit String is read (clamped to 1..4); anything else = 0. Bridge reads only (ConcurrentHashMap: any thread).
JM(lan, r"""
public static int helmetTier(java.util.UUID u) {
  if (u == null || !@PKG@.AccDefs.LAN_HELMET) return 0;
  try {
    java.util.Map b = @PKG@.AccStore.bridge();
    String us = u.toString();
    if (b.get("profile:busy:" + us) != null) return 0;
    Object o = b.get("gear:lamp:" + us);
    if (o == null) return 0;
    int v = 0;
    if (o instanceof java.lang.Number) v = ((java.lang.Number) o).intValue();
    else if (o instanceof String) {
      String x = ((String) o).trim();
      if (x.length() == 1 && Character.isDigit(x.charAt(0))) v = x.charAt(0) - '0';
    }
    if (v <= 0) return 0;
    if (v > 4) v = 4;
    return v;
  } catch (Throwable t) { return 0; }
}""")
# 0.5.10: acc:lamp = "on" while lantern.helmet is on (SkyyGear 0.2.15 shows its tooltip "Lamp:" line only then), "off" otherwise; setup + every
# AccTick (5 s: a live Server Setup change reaches it); removed on shutdown
JM(lan, r"""
public static void pubLamp() {
  try {
    String v = @PKG@.AccDefs.LAN_HELMET ? "on" : "off";
    java.util.Map b = @PKG@.AccStore.bridge();
    if (!v.equals(b.get("acc:lamp"))) b.put("acc:lamp", v);
  } catch (Throwable t) { }
}""")
'''
rep('''# ONE TICK for one player (AccLanternSys: u, their entity, its store and CommandBuffer, dt).''',
    HELM_JAVA + '''# ONE TICK for one player (AccLanternSys: u, their entity, its store and CommandBuffer, dt).''')
rep('''    if (@PKG@.AccDefs.LINE_LANTERN && !dead) t = @PKG@.AccDefs.lanBest(@PKG@.AccStore.snapshot(u));
''', '''    if (@PKG@.AccDefs.LINE_LANTERN && !dead) t = @PKG@.AccDefs.lanBest(@PKG@.AccStore.snapshot(u));
    if (!dead) {   // 0.5.10: a worn mining helmet (SkyyGear gear:lamp) lights like a Lantern of its rarity - the stronger wins, never both
      int hl = helmetTier(u);
      if (hl > t) t = hl;
    }
''')
rep('''  try { @PKG@.AccLantern.prune(online); } catch (Throwable t) { }   // 0.5.4: the Lantern state of players who left (their helpers go by themselves)
''', '''  try { @PKG@.AccLantern.prune(online); } catch (Throwable t) { }   // 0.5.4: the Lantern state of players who left (their helpers go by themselves)
  @PKG@.AccLantern.pubLamp();   // 0.5.10: acc:lamp follows lantern.helmet
''')
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternHide());   // the fix round: the reach light is the wearer's own
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternHide());   // the fix round: the reach light is the wearer's own
  @PKG@.AccLantern.pubLamp();   // 0.5.10: acc:lamp = "on" (the mining helmet light reader is here)
''')
rep('''  try { com.skyy.accessories.AccLantern.clearAll(); } catch (Throwable t) { }   // 0.5.4: the Lantern state (helpers: NonSerialized + a 5 s despawn)
''', '''  try { com.skyy.accessories.AccLantern.clearAll(); } catch (Throwable t) { }   // 0.5.4: the Lantern state (helpers: NonSerialized + a 5 s despawn)
  try { com.skyy.accessories.AccStore.bridge().remove("acc:lamp"); } catch (Throwable t) { }   // 0.5.10
''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s.index("public static int helmetTier") < s.index("public static int step(") < s.index("AccLantern.pubLamp();   // 0.5.10: acc:lamp follows")
assert s.index("LAN_HELMET_ROW = (") < s.index("CFG_ROWS = [") and s.index("LAN_HELMET_LINES = [") < s.index("CONFIG_TEXT = ")
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.9 - build script (derived from the generated build_skyyaccessories_0.5.8.py by tools/accessories_0_5_9_patch.py -',
    "Run:   python build_skyyaccessories_0.5.9.py            -> SkyyAccessories/SkyyAccessories-0.5.9.jar   (deploys go through tools/deploy_set.py --yes)",
    "       python build_skyyaccessories_0.5.9.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)",
    "Test:  python test_skyyaccessories_0.5.9.py             (bare JVM -Xverify:all: every 0.5.8 check + the tab icon + the gem order + the engine",
    "       asset validators)",
    'VERSION = "0.5.9"',
    '] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + LAN_CONFIG_LINES + [""])   # 0.5.4: + the Lantern (0.5.3\'s Night Vision part is gone)',
    '      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS] + LAN_ROWS   # 0.5.4: + the Lantern',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED]
assert not _bad, "0.5.9 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.9 had %d)" % (s.count(LF), OLD.count(LF)))
