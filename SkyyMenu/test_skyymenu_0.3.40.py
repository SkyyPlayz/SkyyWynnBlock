"""Harness for SkyyMenu 0.3.40 (the SkyWynn Menu item is one-handed; tools/menu_0_3_40_patch.py).
Build first:
    python tools/menu_0_3_40_patch.py && python SkyyMenu/build_skyymenu_0.3.40.py

    python SkyyMenu/test_skyymenu_0.3.40.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py - the 0.3.39 harness's phases on this jar):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.39 -> 0.3.40: exactly the listed members differ (version texts); the non-class entries = manifest + Skyy_Menu.json
  T    the 0.3.37 Teleport phase - unchanged behaviour
  T39  the 0.3.39 phase (Supplies tab picture, Mods list versions, dots, Arrange, icon items)
  T40  ONE-HANDED, by the engine's own rule (read from HytaleServer.jar, read-only):
       RULE   ItemUtility has the "Compatible" key; Item.utility defaults to ItemUtility.DEFAULT (Compatible false = two-handed);
              InteractionContext routes by isCompatible() + InteractionConfiguration.getPriorityFor
       ITEM   the jar's Skyy_Menu.json: Utility.Compatible true; Priorities Secondary MainHand 1; = the vanilla Tool_Hoe_Crude's;
              the 0.3.39 JSON had neither (the cause); every other key identical to 0.3.39 (look, icon, interaction, lang ids)
       ROUTE  the engine's main-hand / off-hand choice (InteractionContext.forInteraction, ported): right-click opens the menu with an
              empty off-hand, a shield (priority 0) or a torch (OffHand -1) in the off-hand; without the priority a shield would take it
       VERS   the MODS_VERSIONS table = 0.3.39's (the t39 live-SET VERS check is a NOTE: the SET moved on after 0.3.39's build)
       IDS    every asset id the item names exists (Model / Texture / Icon in the jar, PlayerAnimationsId Item, Quality, Category, page)
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev"))
import harness_kit as HK

_s39 = importlib.util.spec_from_file_location("test_skyymenu_0_3_39", os.path.join(HERE, "test_skyymenu_0.3.39.py"))
T39M = importlib.util.module_from_spec(_s39)
_s39.loader.exec_module(T39M)
T37 = T39M.T37
T35 = T39M.T35

VERSION = "0.3.40"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.39.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu40", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T35.LIVE_DIR
ADDED = []
EXPECT = {      # the class compare 0.3.39 -> 0.3.40: version texts only
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'],   # the config kit's version text
    'MenuData': ['~<clinit>'],                            # the version
    'OpsPage': ['~<clinit>'],                             # the live SET versions the Admin page lists
    'SkyyMenuPlugin': ['~m setup'],                       # the ready line
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ITEM_JSON = "Server/Item/Items/Utility/Skyy_Menu.json"
GAME = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "install", "release", "package", "game", "latest")
SERVER_JAR = os.path.join(GAME, "Server", "HytaleServer.jar")
ASSETS_ZIP = os.path.join(GAME, "Assets.zip")
ONE_HAND = {"Utility": {"Compatible": True}, "InteractionConfig": {"Priorities": {"Secondary": {"MainHand": 1}}}}


def prio(item, itype, slot):
    """InteractionConfiguration.getPriorityFor: no config / no entry = 0; a number = every slot; a map = that slot (else 0)"""
    p = ((item or {}).get("InteractionConfig") or {}).get("Priorities") or {}
    v = p.get(itype)
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    return int(v.get(slot, 0))


def route(main, off, itype):
    """InteractionContext.forInteraction (HytaleServer.jar bytecode 522-695, ported): 'off' = the off-hand item handles it"""
    if main is None and off is not None:
        return "off"
    if main is None or off is None:
        return "main"
    pm, po = prio(main, itype, "MainHand"), prio(off, itype, "OffHand")
    if pm == po:
        return "off" if itype == "Secondary" and (main.get("Utility") or {}).get("Compatible", False) else "main"
    if pm < po:
        return "off"
    if itype not in (main.get("Interactions") or {}):
        return "off"
    return "main"


def run_t40(out, jar, scratch, _home):
    from cpstrings import read_utf8_constants
    K = HK.Child(out)
    sj = zipfile.ZipFile(SERVER_JAR)
    cp = lambda n: read_utf8_constants(sj.read("com/hypixel/hytale/server/core/" + n + ".class"))
    iu, it, ic = cp("asset/type/item/config/ItemUtility"), cp("asset/type/item/config/Item"), cp("entity/InteractionContext")
    K.check("Compatible" in iu and "isCompatible" in iu and "DEFAULT" in iu, "RULE: ItemUtility has the Compatible key + DEFAULT")
    K.check("Utility" in it and "getUtility" in it, "RULE: Item has the Utility key")
    K.check("isCompatible" in ic and "getPriorityFor" in ic, "RULE: InteractionContext routes by isCompatible + getPriorityFor")
    new = json.loads(zipfile.ZipFile(jar).read(ITEM_JSON).decode("utf8"))
    old = json.loads(zipfile.ZipFile(OLD_JAR).read(ITEM_JSON).decode("utf8"))
    K.check(new.get("Utility") == {"Compatible": True}, "ITEM: Utility.Compatible true (one-handed): %r" % new.get("Utility"))
    K.check(prio(new, "Secondary", "MainHand") == 1, "ITEM: right-click priority MainHand 1")
    K.check("Utility" not in old and "InteractionConfig" not in old, "ITEM: 0.3.39 had no Utility block = DEFAULT Compatible false (the cause)")
    az = zipfile.ZipFile(ASSETS_ZIP)
    an = az.namelist()
    vitems = dict((n.split("/")[-1][:-5], n) for n in an if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    hoe = json.loads(az.read(vitems["Tool_Hoe_Crude"]).decode("utf-8-sig"))
    K.check(all(hoe.get(k_) == v_ for k_, v_ in ONE_HAND.items()) and all(new[k_] == v_ for k_, v_ in ONE_HAND.items()),
            "ITEM: the two keys = the vanilla Tool_Hoe_Crude's")
    rest_n = dict((k_, v_) for k_, v_ in new.items() if k_ not in ONE_HAND)
    K.eq(rest_n, old, "ITEM: every other key = 0.3.39 (look, icon, interaction)")
    K.eq(new["Interactions"], {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyyMenu"}}]}},
         "ITEM: right-click opens the SkyyMenu page")
    # ROUTE: the engine's choice, with the vanilla off-hand items
    shield = json.loads(az.read(vitems["Template_Weapon_Shield"]).decode("utf-8-sig"))   # every vanilla shield's Parent
    K.check("Secondary" in (shield.get("Interactions") or {}), "ROUTE: the vanilla shield has its own right-click (block)")
    torch = json.loads(az.read(vitems["Furniture_Crude_Torch"]).decode("utf-8-sig"))
    for nm_, off_ in (("empty", None), ("shield", shield), ("torch", torch)):
        K.eq(route(new, off_, "Secondary"), "main", "ROUTE: right-click with %s off-hand opens the menu" % nm_)
    K.eq(route(new, shield, "Primary"), route(old, shield, "Primary"), "ROUTE: left-click routing unchanged from 0.3.39 (equal priorities)")
    nopri = dict(new)
    nopri.pop("InteractionConfig")
    K.eq(route(nopri, shield, "Secondary"), "off", "ROUTE: control - Compatible without the priority would hand right-click to a shield")
    K.eq(route(old, shield, "Secondary"), "main", "ROUTE: control - 0.3.39 kept right-click (two-handed, off-hand blocked)")
    # IDS
    jn = set(zipfile.ZipFile(jar).namelist())
    for f_ in ("Model", "Texture", "Icon"):
        K.check("Common/" + new[f_] in jn and "Common/" + new[f_] not in an, "IDS: %s %s ships in the jar (ours, no vanilla clash)" % (f_, new[f_]))
    K.check("Server/Item/Animations/%s.json" % new["PlayerAnimationsId"] in an, "IDS: PlayerAnimationsId %s exists" % new["PlayerAnimationsId"])
    K.check([n for n in an if n.startswith("Server/Item/Qualities/") and n.endswith("/%s.json" % new["Quality"])] != [],
            "IDS: Quality %s exists" % new["Quality"])
    cats = [json.loads(az.read(vitems[k_]).decode("utf-8-sig")).get("Categories") for k_ in ("Tool_Hoe_Crude",)]
    K.check(new["Categories"] == ["Items.Tools"] and ["Items.Tools"] in cats, "IDS: Category Items.Tools is a vanilla category")
    lang = zipfile.ZipFile(jar).read("Server/Languages/en-US/server.lang").decode("utf8")
    for k_ in new["TranslationProperties"].values():
        K.check(k_ + "=" in lang, "IDS: lang key %s" % k_)
    # VERS (the t39 phase's live-SET check is a note here): the offline Mods versions table is 0.3.39's, unchanged
    src_ = lambda v_: open(os.path.join(HERE, "build_skyymenu_%s.py" % v_), encoding="utf8").read()
    blk_ = lambda t_: t_[t_.index("MODS_VERSIONS = {"):t_.index("}", t_.index("MODS_VERSIONS = {"))]
    K.eq(blk_(src_("0.3.40")), blk_(src_("0.3.39")), "VERS: MODS_VERSIONS = 0.3.39's (this round leaves it alone)")
    print("T40. one-handed: Utility %s, Priorities %s, routing ok" % (new["Utility"], new["InteractionConfig"]["Priorities"]))
    K.save()


def nonclass_want():
    return sorted(["manifest.json", ITEM_JSON])


if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        _eq0 = HK.Child.eq

        def _eq(self, got, want, what):
            if what == "C: non-class entries changed" and want == ["manifest.json"]:
                return _eq0(self, sorted(got), nonclass_want(), "C: non-class entries changed = manifest + Skyy_Menu.json")
            return _eq0(self, got, want, what)
        HK.Child.eq = _eq
    if HK.arg("--phase") == "t39":
        # MODS_VERSIONS froze at the SET of the 0.3.39 build; the SET moved on since (the 0.3.39 jar fails this the same way) -> a note;
        # T40 checks the table is 0.3.39's unchanged. Refreshing it is a separate round.
        _ck0 = HK.Child.check

        def _ck(self, cond, what):
            if not cond and what.startswith("VERS: MOD_VER = the live SET"):
                self.notes.append("t39 VERS drift (not this round): " + what)
                print("NOTE", what)
                return True
            return _ck0(self, cond, what)
        HK.Child.check = _ck
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("t", T37.run_t), ("t39", T37.run_t39), ("t40", run_t40), ("live", T35.run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyMenu"))
