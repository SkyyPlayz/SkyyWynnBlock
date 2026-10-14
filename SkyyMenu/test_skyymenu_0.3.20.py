"""Harness for SkyyMenu 0.3.20 (the profile name follow-up; tools/menu_0_3_20_patch.py).
Build first: python tools/menu_0_3_20_patch.py && python SkyyMenu/build_skyymenu_0.3.20.py

    python SkyyMenu/test_skyymenu_0.3.20.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.19 -> 0.3.20: exactly PetTile.body + StatsCalc.profileName differ (+ the version texts); no class added
  N  name     on both SkyyProfiles bridge shapes (0.1.12+: profile:name "<Class> <name>" + profile:pname; older: profile:name = the bare
              name, no pname): PetTile.body's first line shows the whole "<Class> <name>" up to 27 characters (CONTROL 0.3.19 cuts
              "Spellblade <16 letters>" at 24), a longer text = 24 + "...", the line stays <= LINE_MAX (79) and is never clipped by
              MenuUtil.clip; StatsCalc.profileName = the bare name on both shapes (pname first, else name); the Stats header shows the
              class once; the Profile tab's Profile row value = the bare name and fits its 192 px column for a 16-letter name
  X, D        every 0.3.19 exec + live check carried forward (SkyyMenu/test_skyymenu_0.3.19.py's run_exec / run_live, run on the 0.3.20
              jar against 0.3.18 exactly as they ran on 0.3.19)
  AA engine-access audit
Scratch: tools/dev/scratch/namefix/menu (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(HERE, "test_skyymenu_0.3.19.py"))
T19 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T19)

VERSION = "0.3.20"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.19.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "namefix", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T19.LIVE_DIR
EXPECT = {
    "PetTile": ["~m body"],
    "StatsCalc": ["~m profileName"],
    "MenuData": ["~<clinit>"],                    # the Mods list's own SkyyMenu entry carries VERSION
    "CfgRows": ["~m header"],                     # the version text
    "CfgFn": ["~m opExport"],                     # the version text
    "SkyyMenuPlugin": ["~m setup"],               # the ready line's version
}
ADDED = []


def run_name(out, jar, scratch, _home):
    from jpype import JClass
    import skyyui as SUI
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", BR)
    Ln, Lo = T19.loader_for(jar), T19.loader_for(OLD_JAR)
    PT, PTo = JClass(PKG + "PetTile", loader=Ln), JClass(PKG + "PetTile", loader=Lo)
    SC, SCo = JClass(PKG + "StatsCalc", loader=Ln), JClass(PKG + "StatsCalc", loader=Lo)
    LM = int(SC.LINE_MAX)
    K.eq(LM, 79, "N: LINE_MAX")
    u = JClass("java.util.UUID")(0x0B0A0000000000CD, 0x20)
    us = str(u)

    def shape(name=None, pname=None, cls=None):
        for k, v in (("profile:name:", name), ("profile:pname:", pname), ("profile:class:", cls)):
            if v is None:
                BR.remove(k + us)
            else:
                BR.put(k + us, v)

    def first(T):
        return str(T.body(u, None)).split("\n")[0]

    def pets(n):
        return "Your pets on this profile (%s). Click to see them all." % n
    LONG = "Spellblade Abcdefghijklmnop"
    cases = [
        # (label, name, pname, class, want pets first line, want profileName)
        ("0.1.12 shape", "Priest Banana", "Banana", "Priest", pets("Priest Banana"), "Banana"),
        ("0.1.12 shape, longest class + 16 letters (27)", LONG, "Abcdefghijklmnop", "Spellblade", pets(LONG), "Abcdefghijklmnop"),
        ("0.1.12 shape, 16 W", "Spellblade " + "W" * 16, "W" * 16, "Spellblade", pets("Spellblade " + "W" * 16), "W" * 16),
        ("0.1.12 shape, no class", "Banana", "Banana", None, pets("Banana"), "Banana"),
        ("older SkyyProfiles (bare name)", "Banana", None, "Priest", pets("Banana"), "Banana"),
        ("older SkyyProfiles, 16 letters", "Abcdefghijklmnop", None, "Priest", pets("Abcdefghijklmnop"), "Abcdefghijklmnop"),
        ("28 characters (beyond any SkyyProfiles text)", "Spellblade Abcdefghijklmnopq", "Abcdefghijklmnopq", "Spellblade",
         pets("Spellblade Abcdefghijklm..."), "Abcdefghijklmnopq"),
        ("40 characters with a space at the cut", "Spellblade Abcdefghijkl  mnopqrstuvwxyz12", None, None,
         pets("Spellblade Abcdefghijkl..."), "Spellblade Abcdefghijkl  mnopqrstuvwxyz12"),
        ("no profile", None, None, None, "Your pets on this profile. Click to see them all.", None),
    ]
    for label, n, pn, c, want_pet, want_pn in cases:
        shape(n, pn, c)
        got = first(PT)
        K.eq(got, want_pet, "N pets: %s" % label)
        K.check(len(got) <= LM, "N pets: %s - <= LINE_MAX (%d)" % (label, len(got)))
        p = SC.profileName(u)
        K.eq(None if p is None else str(p), want_pn, "N stats: profileName - %s" % label)
        if pn is None:
            po = SCo.profileName(u)
            K.eq(None if p is None else str(p), None if po is None else str(po), "N stats: %s - the same name as 0.3.19" % label)
    # CONTROL 0.3.19: the 27-character display text was cut at 24
    shape(LONG, "Abcdefghijklmnop", "Spellblade")
    K.eq(first(PTo), pets(LONG[:24].strip()), "N CONTROL 0.3.19: the pets tile cut 'Spellblade <16 letters>' at 24")
    K.eq(str(SCo.profileName(u)), LONG, "N CONTROL 0.3.19: the Stats page showed the class twice (profile:name)")
    # the Stats header: the class once
    shape("Priest Banana", "Banana", "Priest")
    h = str(SC.header(u, "Skyy"))
    K.check(h.startswith("Skyy  -  Priest  -  profile Banana"), "N stats header: the class once (%s)" % h)
    K.check(h.count("Priest") == 1, "N stats header: 'Priest' appears once")
    ho = str(SCo.header(u, "Skyy"))
    K.check(ho.count("Priest") == 2, "N CONTROL 0.3.19: the header showed the class twice (%s)" % ho)
    # the Profile tab's row value
    rows = JClass("java.util.ArrayList")()
    SC.profileTab(rows, u)
    r0 = [str(x) for x in rows.get(0)] if rows.size() > 0 else []
    K.check(len(r0) >= 2 and r0[0] == "Profile" and r0[1] == "Banana", "N stats Profile row: Profile | Banana (%s)" % r0[:3])
    # the value column: a 16-letter bare name fits (192 px at 18 px bold); the old display text would not
    K.check(SUI.text_width("Abcdefghijklmnop", 18, bold=True) <= 192, "N: a 16-letter name fits the Profile row's 192 px column")
    K.check(SUI.text_width(LONG, 18, bold=True) > 192, "N CONTROL: 'Spellblade <16 letters>' would overflow that column")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("name", run_name), ("exec", T19.run_exec), ("live", T19.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
