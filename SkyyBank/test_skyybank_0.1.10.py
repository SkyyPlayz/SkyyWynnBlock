"""Harness for SkyyBank 0.1.10 (the profile name line; tools/bank_0_1_10_patch.py).
Build first: python tools/bank_0_1_10_patch.py && python SkyyBank/build_skyybank_0.1.10.py

    python SkyyBank/test_skyybank_0.1.10.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.9 -> 0.1.10: exactly BankPage.subText differs (+ the version texts); no class added
  N  name     BankPage.subText on the bridge shapes: SkyyProfiles 0.1.12+ (profile:name "<Class> <name>" + profile:pname) -> shown as it
              is, never the class twice; an older SkyyProfiles (no pname, name = the bare name) -> the old "(Class)" suffix; the
              0.1.12 publish gap (name written, pname not yet) -> no double class; no class / no name / no bridge values; CONTROL
              0.1.9 shows the class twice with 0.1.12's shape
  X, D        every 0.1.9 exec + live check carried forward (SkyyBank/test_skyybank_0.1.9.py's run_exec / run_live, run on the 0.1.10
              jar against 0.1.8 exactly as they ran on 0.1.9)
  AA engine-access audit
Scratch: tools/dev/scratch/namefix/bank (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("test_skyybank_0_1_9", os.path.join(HERE, "test_skyybank_0.1.9.py"))
T9 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T9)

VERSION = "0.1.10"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBank-0.1.9.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "namefix", "bank")))
PKG = "com.skyy.bank."
LIVE_DIR = T9.LIVE_DIR
EXPECT = {
    "BankPage": ["~m subText"],
    "CfgRows": ["~m header"],                     # the version text
    "CfgFn": ["~m opExport"],                     # the version text
    "SkyyBankPlugin": ["~m setup"],               # the ready line's version
}
ADDED = []


def run_name(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", BR)
    new = JClass(PKG + "BankPage", loader=T9.loader_for(jar))
    old = JClass(PKG + "BankPage", loader=T9.loader_for(OLD_JAR))
    u = JClass("java.util.UUID")(0x0B0A0000000000AB, 0x10)
    us = str(u)
    TAIL = "  -  every profile has its own bank. Coins in the bank earn interest and are never lost when you die."
    PLAIN = "Coins in the bank earn interest and are never lost when you die."

    def shape(name=None, pname=None, cls=None):
        for k, v in (("profile:name:", name), ("profile:pname:", pname), ("profile:class:", cls)):
            if v is None:
                BR.remove(k + us)
            else:
                BR.put(k + us, v)
    cases = [
        # (label, name, pname, class, want 0.1.10)
        ("0.1.12 shape with a class", "Priest Banana", "Banana", "Priest", "Profile Priest Banana" + TAIL),
        ("0.1.12 shape, longest class + 16-letter name", "Spellblade Abcdefghijklmnop", "Abcdefghijklmnop", "Spellblade",
         "Profile Spellblade Abcdefghijklmnop" + TAIL),
        ("0.1.12 shape, no class yet", "Banana", "Banana", None, "Profile Banana" + TAIL),
        ("0.1.12 publish gap (name written, pname not yet)", "Priest Banana", None, "Priest", "Profile Priest Banana" + TAIL),
        ("older SkyyProfiles (bare name + class)", "Banana", None, "Priest", "Profile Banana (Priest)" + TAIL),
        ("older SkyyProfiles, name happens to equal the class", "Priest", None, "Priest", "Profile Priest (Priest)" + TAIL),
        ("older SkyyProfiles, no class", "Banana", None, None, "Profile Banana" + TAIL),
        ("older SkyyProfiles, empty class", "Banana", None, "", "Profile Banana" + TAIL),
        ("no profile name", None, None, "Priest", PLAIN),
        ("empty profile name", "", "", "Priest", PLAIN),
        ("nothing on the bridge", None, None, None, PLAIN),
    ]
    for label, n, pn, c, want in cases:
        shape(n, pn, c)
        K.eq(str(new.subText(u)), want, "N: %s" % label)
        if pn is None:
            if n == "Priest Banana":
                K.eq(str(old.subText(u)), "Profile Priest Banana (Priest)" + TAIL, "N CONTROL 0.1.9: the gap shows the class twice")
            else:
                K.eq(str(new.subText(u)), str(old.subText(u)), "N: %s - the same line as 0.1.9" % label)
    shape("Priest Banana", "Banana", "Priest")
    K.eq(str(old.subText(u)), "Profile Priest Banana (Priest)" + TAIL, "N CONTROL 0.1.9: SkyyProfiles 0.1.12 makes it show the class twice")
    K.check("(Priest)" not in str(new.subText(u)), "N: 0.1.10 never shows the class twice with SkyyProfiles 0.1.12")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBank", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("name", run_name), ("exec", T9.run_exec), ("live", T9.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBank"))
