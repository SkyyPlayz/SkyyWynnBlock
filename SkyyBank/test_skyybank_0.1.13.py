"""Harness for SkyyBank 0.1.13 (HUBS H3d: the Storage > Bank tab; tools/bank_0_1_13_patch.py). Build first:
python tools/bank_0_1_13_patch.py && python SkyyBank/build_skyybank_0.1.13.py

    python SkyyBank/test_skyybank_0.1.13.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.12 -> 0.1.13 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyBank, AA engine-access audit), plus here:
  VIS   BankHubVis: no bank:fn:unlocked Function = shown; one that answers TRUE = shown, FALSE / throws = hidden (HubBar.tabs too)
  CLICK Refresh (a non-hub click) still answers on the page; the page id is the one the patch pins (BANK_PAGE_CHECKED)
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.13"
PKG = "com.skyy.bank."


def prep(E, J, home):
    from jpype import JClass
    J("BankStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
    J("BankStore").DIR = E.Paths.get(os.path.join(home, "accounts"))
    J("BankConfig").FILE = E.Paths.get(os.path.join(home, "config.properties"))
    J("BankConfig").STATE = E.Paths.get(os.path.join(home, "state.properties"))
    J("BankWatch").STOP = False
    J("BankWatch").EXEC = E.U.allocateInstance(E.RecEx.class_)     # a recording scheduler: the page check is queued, never run


def vis_cases(K, E, J, vis, u):
    import jpype
    from jpype import JClass, JImplements, JOverride
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    @JImplements("java.util.function.Function")
    class Unl:
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            if self.ans == "throw":
                raise RuntimeError("boom")
            return self.ans
    HB = J("HubBar")
    for ans, want, what in ((TRUE, TRUE, "TRUE"), (FALSE, FALSE, "FALSE"), ("throw", FALSE, "throws")):
        E.br.put("bank:fn:unlocked", Unl(ans))
        K.check(vis.apply(u) == want, "VIS: bank:fn:unlocked answers %s -> the tab %s" % (what, "shown" if want == TRUE else "hidden"))
    E.br.put("bank:fn:unlocked", Unl(FALSE))
    K.check(len(list(HB.tabs("storage", u))) == 0, "VIS: a locked bank -> HubBar.tabs(storage) has no Bank tab")
    K.eq(str(HB.open(None, u, "storage", "bank")), "hidden", "VIS: a locked bank -> HubBar.open answers hidden (no page, no command)")
    E.br.remove("bank:fn:unlocked")
    K.check(vis.apply(u) == TRUE, "VIS: the key gone again -> shown")


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "BankPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) still answers on the bank page")


def extra_hub(K, W, J):
    src = open(os.path.join(HERE, "build_skyybank_%s.py" % VERSION), encoding="utf8").read()
    import re
    m = re.search(r'BANK_PAGE_CHECKED = "([0-9a-f]{12})"', src)
    import zipfile
    data = zipfile.ZipFile(S.jar).read("com/skyy/bank/SkyyBankPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data,
            "PAGE: the built page id = BANK_PAGE_CHECKED %s (the ready line; the 0.1.7 page-check rule)" % (m and m.group(1)))


S = H.Spec(name="SkyyBank", version=VERSION, pkg=PKG, hub="storage", tab="bank", mod="SkyyBank", open_cls="BankHubOpen", vis_cls="BankHubVis",
           page_cls="BankPage", prefix="SkyyBankF", idp="SkyyB", plugin_cls="SkyyBankPlugin", register_call="BankHubOpen.register",
           register=lambda J: J("BankHubOpen").register(), prep=prep, vis_cases=vis_cases, clicks=[('{"a":"refresh","@BAmount":""}', chk_refresh)],
           extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyBank-0.1.12.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "bank"))), script=__file__,
           added=["HubBar", "BankHubVis", "BankHubOpen"],
           expect={"BankPage": ["+m hubAck", "+m hubClick", "~m build", "~m handleDataEvent"], "SkyyBankPlugin": ["~m setup", "~m shutdown"],
                   "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]})      # CfgFn / CfgRows: the config kit's version texts

if __name__ == "__main__":
    H.run(S)
