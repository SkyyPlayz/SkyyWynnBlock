"""Derive SkyySacks/build_skyysacks_0.7.9.py from the SET pin 0.7.8 (edit THIS file, then regenerate: python tools/sacks_0_7_9_patch.py).
0.7.9 = THE CAMPFIRE TAB FOLLOWS SKYYCOOKING 0.1.3's HALVED XP SHARE. Skyy 2026-10-01 (verbatim): "ive been cooking meat using the campfire
in the /crafting. and im already cooking level 11. my highest level skill. id half the amount of cooking xp you get from the campfire." ->
SkyyCooking 0.1.3: campfire.xpFactor ("Campfire XP share") default 0.5 -> 0.25 (tools/cooking_0_1_3_patch.py; SkyyCooking pays the XP).
 - The /craft Campfire tab line ("Campfire accessory = emergency cook: N% Cooking XP, M% of your cooking bonus ...") shows SkyyCooking's
   LIVE share from (1) cook:fn:campfactors (SkyyCooking 0.1.1+: the running factors - unchanged from 0.7.4/0.7.8, now taken only when BOTH
   factors are numbers 0..1), else (2) NEW config:fn:SkyyCooking get campfire.xpFactor / campfire.buffFactor / enabled (SkyyCooking 0.1.2+
   config kit, tools/CONFIG-CONTRACT.md: canonical text, any thread, never throws), else (3) the fallback numbers CAMP_XP_PCT / CAMP_BUFF_PCT
   = SkyyCooking 0.1.3's defaults, 25 / 75 (were 50 / 75). Without SkyyCooking the tab keeps saying plain food and no Cooking XP.
 - The 0.7.4 build check no longer FAILS when the newest SkyyCooking script's defaults differ from the fallback numbers (it stopped the
   0.7.8 rebuild as soon as build_skyycooking_0.1.3.py existed): it now fails only when that script stops publishing what the live text
   reads (cook:fn:campfactors with its Object[]{Double buffFactor, Double xpFactor, Boolean enabled} shape, the config kit rows
   campfire.xpFactor / campfire.buffFactor / enabled of MOD SkyyCooking) or has no parsable CAMP_BUFF_DEF / CAMP_XP_DEF line; a differing
   default prints a NOTE (the fallback only shows for a SkyyCooking that answers neither bridge key).
Nothing else changes: the cooked-food rule, bags, tiers, the Omni, recipes, collection unlocks, /craft (every tab incl. what the Campfire tab
crafts and the cook:fn:campfire call), Furnace / Tannery, settings and config rows are 0.7.8 (class compare in the build report).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.8.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.9.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


# ================= docstring + version =================
rep('"""SkyySacks 0.7.8 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.8.py            -> SkyySacks/SkyySacks-0.7.8.jar' + LF,
    '"""SkyySacks 0.7.9 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.9.py            -> SkyySacks/SkyySacks-0.7.9.jar' + LF)
rep('the Cooking XP (x0.5) and grades the dish (x0.75 of the Cooking bonus); the tab does not report skill:fn:craftxp.',
    'the Cooking XP (x campfire.xpFactor: 0.5 then, 0.25 since SkyyCooking 0.1.3) and grades the dish (x0.75 of the Cooking bonus); the tab' + LF
    + 'does not report skill:fn:craftxp.')
rep('singular / plural; Deposit all on the Farming tab says cooked food stays in the inventory (SweepTask.cookedHeld).' + LF + '"""' + LF,
    'singular / plural; Deposit all on the Farming tab says cooked food stays in the inventory (SweepTask.cookedHeld).' + LF
    + '0.7.9 (derived from 0.7.8 by tools/sacks_0_7_9_patch.py - edit the patch, not this file; Skyy 2026-10-01 "id half the amount of cooking' + LF
    + 'xp you get from the campfire" -> SkyyCooking 0.1.3 campfire.xpFactor default 0.5 -> 0.25): the /craft Campfire tab line shows the LIVE' + LF
    + 'share from cook:fn:campfactors (both factors 0..1), else NEW config:fn:SkyyCooking get campfire.xpFactor / campfire.buffFactor / enabled,' + LF
    + 'else the fallback 25% / 75% (was 50% / 75%); no SkyyCooking = plain food, no XP (as before). The build check no longer fails on a' + LF
    + 'differing SkyyCooking default (NOTE only); it fails when SkyyCooking stops publishing what the live line reads. Nothing else changed.' + LF
    + '"""' + LF)
rep('VERSION = "0.7.8"', 'VERSION = "0.7.9"')

# ================= the fallback numbers + the build check =================
rep('''# 0.7.4: the Campfire tab text numbers = SkyyCooking's campfire.xpFactor / campfire.buffFactor defaults (cook:fn:campfire applies the real,
# configurable factors). Checked against the newest SkyyCooking build script when it is present (SkyyAccessories 0.4.3 pattern), so the
# text cannot drift from those defaults. CraftPage.campNote() shows SkyyCooking's LIVE factors from cook:fn:campfactors when that Function
# is on the bridge (an edited cooking.properties + /cookadmin reload shows at once); these numbers are only the fallback without it.
CAMP_XP_PCT, CAMP_BUFF_PCT = 50, 75
def _camp_defaults_check():
    import re, glob
    def _v(p):
        m = re.search(r"_(\\d+(?:\\.\\d+)*)\\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(glob.glob(os.path.join(HERE, "..", "SkyyCooking", "build_skyycooking_*.py")), key=_v)
    if not found:
        print("note: no SkyyCooking build script next to this mod - Campfire tab numbers not cross-checked")
        return
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    m = re.search(r"^CAMP_BUFF_DEF, CAMP_XP_DEF = ([0-9.]+), ([0-9.]+)", txt, re.M)
    if not m:
        raise SystemExit("0.7.4: %s has no CAMP_BUFF_DEF / CAMP_XP_DEF line - re-check the Campfire tab numbers (CAMP_*_PCT)" % os.path.basename(found[-1]))
    buff, xp = int(round(float(m.group(1)) * 100)), int(round(float(m.group(2)) * 100))
    if (buff, xp) != (CAMP_BUFF_PCT, CAMP_XP_PCT):
        raise SystemExit("0.7.4: %s defaults are buff %d%% / XP %d%% but the Campfire tab says %d%% / %d%% - update CAMP_*_PCT"
                         % (os.path.basename(found[-1]), buff, xp, CAMP_BUFF_PCT, CAMP_XP_PCT))
    print("campfire tab text matches %s defaults (XP %d%%, bonus %d%%)" % (os.path.basename(found[-1]), xp, buff))
_camp_defaults_check()
''', '''# 0.7.4: the Campfire tab text numbers = SkyyCooking's campfire.xpFactor / campfire.buffFactor (cook:fn:campfire applies the real,
# configurable factors). 0.7.9 (Skyy 2026-10-01 -> SkyyCooking 0.1.3 campfire.xpFactor default 0.5 -> 0.25): CraftPage.campNote() shows
# SkyyCooking's LIVE factors - cook:fn:campfactors (the running values), else config:fn:SkyyCooking get (its config kit) - so an edited
# value (Server Setup, cooking.properties + /cookadmin reload) shows at once; CAMP_*_PCT = SkyyCooking 0.1.3's defaults are only the text
# for a SkyyCooking that answers neither key.
CAMP_XP_PCT, CAMP_BUFF_PCT = 25, 75
# 0.7.9: 0.7.4's check FAILED the build whenever the newest SkyyCooking script's defaults differed from CAMP_*_PCT, which stopped every
# Sacks rebuild once SkyyCooking 0.1.3 halved the XP share. Now it fails only when that script stops publishing what the live line reads
# (cook:fn:campfactors and its shape; the campfire.xpFactor / campfire.buffFactor / enabled rows of the SkyyCooking config kit) or has no
# parsable defaults line; a differing default is a NOTE (the fallback numbers then trail SkyyCooking until the next Sacks version).
def _camp_defaults_check():
    import re, glob
    def _v(p):
        m = re.search(r"_(\\d+(?:\\.\\d+)*)\\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(glob.glob(os.path.join(HERE, "..", "SkyyCooking", "build_skyycooking_*.py")), key=_v)
    if not found:
        print("note: no SkyyCooking build script next to this mod - Campfire tab sources not cross-checked")
        return
    name = os.path.basename(found[-1])
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    m = re.search(r"^CAMP_BUFF_DEF, CAMP_XP_DEF = ([0-9.]+), ([0-9.]+)", txt, re.M)
    if not m:
        raise SystemExit("0.7.9: %s has no CAMP_BUFF_DEF / CAMP_XP_DEF line - re-check the Campfire tab numbers (CAMP_*_PCT)" % name)
    if 'b.put("cook:fn:campfactors"' not in txt or "Double buffFactor, Double xpFactor, Boolean enabled" not in txt:
        raise SystemExit("0.7.9: %s no longer publishes cook:fn:campfactors -> Object[]{Double buffFactor, Double xpFactor, Boolean enabled} "
                         "- update CraftPage.campFactors (tools/sacks_0_7_9_patch.py)" % name)
    if 'MOD="SkyyCooking"' not in txt:
        raise SystemExit("0.7.9: %s no longer publishes config:fn:SkyyCooking (CFG.emit MOD=\\"SkyyCooking\\") - update CraftPage.campCfg" % name)
    for key, typ in (("campfire.xpFactor", "dec"), ("campfire.buffFactor", "dec"), ("enabled", "bool")):
        if not re.search(r'\\("%s", "[^"]*", "[a-z]+", "%s"' % (re.escape(key), typ), txt):
            raise SystemExit("0.7.9: %s has no %s config row %s - update CraftPage.campCfg" % (name, typ, key))
    buff, xp = int(round(float(m.group(1)) * 100)), int(round(float(m.group(2)) * 100))
    if (buff, xp) != (CAMP_BUFF_PCT, CAMP_XP_PCT):
        print("NOTE: %s defaults are XP %d%% / bonus %d%%, the Campfire tab's fallback text says %d%% / %d%% - the tab shows SkyyCooking's "
              "live share; update CAMP_*_PCT in the next SkyySacks version" % (name, xp, buff, CAMP_XP_PCT, CAMP_BUFF_PCT))
    else:
        print("campfire tab: live share from cook:fn:campfactors / config:fn:SkyyCooking (%s publishes both); fallback text matches its "
              "defaults (XP %d%%, bonus %d%%)" % (name, xp, buff))
_camp_defaults_check()
''')

# ================= CraftPage: the live share =================
rep('''# the tab's emergency-cook line (Skyy: 50% XP, 75% of the buffs the Cooking skill adds); shown with set(), so commas and colons are safe.
# Review fix: the numbers are the LIVE factors from SkyyCooking's cook:fn:campfactors (apply(anything) -> Object[]{Double buffFactor,
# Double xpFactor, Boolean enabled}, any thread, no I/O - so an edited cooking.properties + /cookadmin reload shows at once); a SkyyCooking
# without that Function -> CAMP_XP_PCT / CAMP_BUFF_PCT, cross-checked against SkyyCooking's defaults at build time.
''', '''# the tab's emergency-cook line (Skyy 2026-09-24: 50% XP, 75% of the buffs the Cooking skill adds; Skyy 2026-10-01: XP halved -> 25%,
# SkyyCooking 0.1.3); shown with set(), so commas and colons are safe. The numbers are SkyyCooking's LIVE factors: (1) cook:fn:campfactors
# (apply(anything) -> Object[]{Double buffFactor, Double xpFactor, Boolean enabled}, any thread, no I/O - so an edited cooking.properties +
# /cookadmin reload or a Server Setup change shows at once), (2) 0.7.9: else config:fn:SkyyCooking get (the config kit's op), (3) else
# CAMP_XP_PCT / CAMP_BUFF_PCT (SkyyCooking 0.1.3's defaults).
''')
rep('''# {xp %, buff %, enabled 1/0}: cook:fn:campfactors when present and well formed, else the build-checked defaults (enabled)
cpg.addMethod(CtNewMethod.make("""
public static int[] campFactors() {
  int[] out = new int[] { CAMPXPPCT, CAMPBUFFPCT, 1 };
  try {
    Object f = {PKG}.SackPool.bridge().get("cook:fn:campfactors");
    if (!(f instanceof java.util.function.Function)) return out;
    Object r = ((java.util.function.Function) f).apply((Object) null);
    if (!(r instanceof Object[])) return out;
    Object[] a = (Object[]) r;
    if (a.length < 2) return out;
    out[1] = campPct(a[0], CAMPBUFFPCT);
    out[0] = campPct(a[1], CAMPXPPCT);
    if (a.length > 2 && Boolean.FALSE.equals(a[2])) out[2] = 0;
  } catch (Throwable t) { }
  return out;
}""".replace("{PKG}", PKG), cpg))
''', '''# 0.7.9: a factor (0..1) the way the config kit carries it - canonical text ("0.25") -> whole percent; anything else -> -1
cpg.addMethod(CtNewMethod.make("""
public static int campPctText(Object v) {
  if (!(v instanceof String)) return -1;
  double f = -1.0;
  try { f = Double.parseDouble(((String) v).trim()); } catch (Throwable t) { return -1; }
  if (!(f >= 0.0 && f <= 1.0)) return -1;
  return (int) Math.round(f * 100.0);
}""", cpg))
# 0.7.9: SkyyCooking's config kit (config:fn:SkyyCooking, SkyyCooking 0.1.2+; tools/CONFIG-CONTRACT.md op "get" -> the value as canonical
# text, null = unknown key; any thread, never throws, no I/O): {xp %, buff %, enabled 1/0}, or null when the function is missing or either
# factor does not read as a number 0..1. enabled = the "Graded cooking" part switch (only the text "false" counts as off)
cpg.addMethod(CtNewMethod.make("""
public static int[] campCfg() {
  try {
    Object f = {PKG}.SackPool.bridge().get("config:fn:SkyyCooking");
    if (!(f instanceof java.util.function.Function)) return null;
    java.util.function.Function fn = (java.util.function.Function) f;
    int xp = campPctText(fn.apply(new Object[] { "get", "campfire.xpFactor" }));
    int buff = campPctText(fn.apply(new Object[] { "get", "campfire.buffFactor" }));
    if (xp < 0 || buff < 0) return null;
    Object en = fn.apply(new Object[] { "get", "enabled" });
    return new int[] { xp, buff, "false".equals(en) ? 0 : 1 };
  } catch (Throwable t) { return null; }
}""".replace("{PKG}", PKG), cpg))
# {xp %, buff %, enabled 1/0}: (1) cook:fn:campfactors when present and well formed (an Object[] of >= 2 elements whose first two are numbers
# 0..1 - the running values; a third FALSE = graded cooking off), (2) 0.7.9: else campCfg() (config:fn:SkyyCooking), (3) else the
# defaults CAMPXPPCT / CAMPBUFFPCT (enabled)
cpg.addMethod(CtNewMethod.make("""
public static int[] campFactors() {
  try {
    Object f = {PKG}.SackPool.bridge().get("cook:fn:campfactors");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply((Object) null);
      if (r instanceof Object[]) {
        Object[] a = (Object[]) r;
        if (a.length >= 2 && campPct(a[0], -1) >= 0 && campPct(a[1], -1) >= 0) {
          int[] got = new int[] { campPct(a[1], CAMPXPPCT), campPct(a[0], CAMPBUFFPCT), 1 };
          if (a.length > 2 && Boolean.FALSE.equals(a[2])) got[2] = 0;
          return got;
        }
      }
    }
  } catch (Throwable t) { }
  int[] c = campCfg();
  if (c != null) return c;
  return new int[] { CAMPXPPCT, CAMPBUFFPCT, 1 };
}""".replace("{PKG}", PKG), cpg))
''')

# ================= self-checks =================
assert 'VERSION = "0.7.9"' in s and "CAMP_XP_PCT, CAMP_BUFF_PCT = 25, 75\n" in s and s.count("CAMP_XP_PCT, CAMP_BUFF_PCT = ") == 1
assert s.index("public static int campPct(Object v, int def) {") < s.index("public static int campPctText(Object v) {") \
    < s.index("public static int[] campCfg() {") < s.index("public static int[] campFactors() {") < s.index("public static String campNote() {")
assert s.count("campFactors()") == 2 and s.count('get("config:fn:SkyyCooking")') == 1 and s.count('get("cook:fn:campfactors")') == 1
assert "raise SystemExit(\"0.7.4: %s defaults are buff" not in s, "the 0.7.4 fail-on-default check is gone"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
