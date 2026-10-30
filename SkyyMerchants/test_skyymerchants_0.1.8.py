"""Harness for SkyyMerchants 0.1.8 (RARITY PASS: the rarity square behind every shop row icon; tools/merchants_0_1_8_patch.py + the kit's
static_row(icon_bg=), = SkyyPets 0.4.18). Build first: python tools/merchants_0_1_8_patch.py && python SkyyMerchants/build_skyymerchants_0.1.8.py

    python SkyyMerchants/test_skyymerchants_0.1.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  A   verify   every class loads + initialises
  C   compare  0.1.7 -> 0.1.8: only MerchPage (+ rbg, ~ build) and the version text (plugin, CfgFn / CfgRows / MerchCfg headers)
  K   kit      the jar's kit art = 59 files (SUI.check_jar_kit); the generated rows markup: the #SkyyMcR<i>If square in BOTH row looks (Buy +
               sold out), the same b.set lines, the text column >= 40 px, kit-proven
  X   exec     EXECUTES MerchPage.rbg: SkyyGear's gear:fn:rarity words (a stand-in bridge Function) -> the item rarity hex + "(0.4)",
               mythic / junk / null / no bridge / a throwing bridge -> the faint grey; the 30 pet eggs -> their quality colour, our dragon eggs
               Legendary, an unknown egg suffix grey; then MerchPage.build on a real UICommandBuilder with a stand-in site: every row's
               square = its item's colour, a sold-out row = the faint grey, names stay soft white (no row text colour changed)
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyMerchants: MerchMig + MerchMigP7 + MerchCfg.load + the kit TWICE: 0.1.8
               writes nothing new (no saved data, no migration); the second start changes nothing; the merchants registry untouched
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.8"
PKG = "com.skyy.merchants."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMerchants-0.1.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_merchants", "me")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMerchants")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "MerchCfg": ["~m applyAll", "~m seed"],   # the version text they inline
          "MerchPage": ["+m rbg", "~m build"], "SkyyMerchantsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []


def sui():
    import skyyui as SUI
    SUI.verify()
    return SUI


def colours():
    SUI = sui()
    gear = dict((w.lower(), SUI.RARITY[w] + "(0.4)") for w in ("Normal", "Unique", "Rare", "Legendary", "Fabled"))
    egg = dict((r, (SUI.QUALITY[r] if r != "Mythic" else SUI.RARITY["Mythic"]) + "(0.4)") for r in ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"))
    return SUI, gear, egg, SUI.COLOR["disabled"] + "(0.15)"


def loader(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def gen_module():
    """the generated build script's page_java() rows (no build: the module is read up to PJ = page_java())"""
    src = open(os.path.join(HERE, "build_skyymerchants_%s.py" % VERSION), encoding="utf8").read()
    return src


# ======================================================================================================== K: the kit art + the rows markup
def run_kit(out, jar, scratch, _home):
    K = HK.Child(out)
    SUI, gear, egg, NONE = colours()
    need = ("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", SUI.HUB_FRAME["market"], "Tertiary")
    K.eq(SUI.check_jar_kit(jar, need=need), 59, "K the jar's kit art = 59 kit files (byte for byte)")
    J_ = SUI.J
    COL = SUI.COLOR
    sh = SUI.page_shell("SkyyMc", 900, 720, "Traveling Merchant", body_id="SkyyMcBody")
    LIST_IN = sh.inner_w - 2 * SUI.WELL_LIST_PAD - 12
    src = gen_module()
    m = re.search(r"    rkw = dict\((.*?)\n    r_on = ", src, re.S)
    K.check(m is not None and 'icon_bg=J_("ibg", SUI.RARITY["Normal"] + "(" + RBG_ALPHA + ")")' in m.group(1), "K the generated script gives rkw the icon_bg square")
    rkw = dict(icon=J_("ic", "Weapon_Sword_Frost"), name=J_("nm", "Frost Sword"), sub=J_("sb", "1 left this visit"),
               tag=J_("tg", "7,500 coins"), tag_col=J_("tc", COL["gold"]), tag_w=200, action="Buy", icon_bg=J_("ibg", SUI.RARITY["Normal"] + "(0.4)"))
    r_on = SUI.static_row("SkyyMcR" + J_("i", "0"), LIST_IN, action_on=True, **rkw)
    r_off = SUI.static_row("SkyyMcR" + J_("i", "0"), LIST_IN, action_on=False, **rkw)
    old = dict(rkw)
    old.pop("icon_bg")
    o_on = SUI.static_row("SkyyMcR" + J_("i", "0"), LIST_IN, action_on=True, **old)
    for nm, r in (("Buy", r_on), ("sold out", r_off)):
        t = SUI.render(r)
        K.check(re.search(r"Group #SkyyMcR0If \{ Anchor: \(Width: 44, Height: 44, Left: 0, Top: \d+\); Background: #FFFFFF\(0\.4\); \}", t) is not None,
                "K the %s row look holds the 44 px #SkyyMcR<i>If square" % nm)
        SUI.check_markup(str(r), prefix="SkyyMc")
    K.eq([s[0] for s in r_on.sets], [s[0] for s in r_off.sets], "K r_on / r_off set the same elements")
    K.eq([s[0] for s in r_on.sets], [s[0] for s in o_on.sets], "K the b.set lines are the 0.1.7 ones (the square is markup only)")
    K.check(r_on.text_w >= 40 and r_on.text_w == o_on.text_w, "K the text column keeps its width (%d px, 0.1.7 %d)" % (r_on.text_w, o_on.text_w))
    SUI.assert_proven([r_on, r_off], what="shop rows")
    K.check(True, "K the rows are kit-proven (assert_proven)")
    K.check("String ibg = left > 0 ? rbg(ic) : \"@RBGNONE@\";" in src and '"@RBGNONE@": RBG_NONE' in src, "K the row loop fills ibg (sold out = RBG_NONE)")
    K.save()


# ======================================================================================================== X: rbg + the page build, EXECUTED
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JImplements, JOverride
    K = HK.Child(out)
    SUI, gear, egg, NONE = colours()
    import skyyeggs as EGG
    HK.jvm([B.SERVER_JAR], verify=True)
    L = loader(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Page, Cfg, Reg, Eng, Shop, Wall = J("MerchPage"), J("MerchCfg"), J("MerchReg"), J("MerchEng"), J("MerchShop"), J("MerchWall")
    br = JClass("java.lang.System").getProperties()
    if br.get("skyy.bridge") is None:
        br.put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    m = br.get("skyy.bridge")
    ANS = {"Weapon_Sword_Frost": "normal", "Weapon_Axe_Bone": "unique", "Sword_Iron_Green": "rare", "Weapon_Bo_Iron": " Legendary ",
           "Weapon_Wand_Iron": "fabled", "Weapon_Sword_Mythic": "mythic", "Weapon_Junk": "shiny", "Weapon_Set_Piece": "set"}

    @JImplements("java.util.function.Function")
    class GearFn(object):
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, a):
            i = str(a[0])
            self.calls.append(i)
            if i == "Weapon_Boom":
                raise RuntimeError("boom")
            return JString(ANS[i]) if i in ANS else None

    @JImplements("java.util.function.Function")
    class Boom(object):
        @JOverride
        def apply(self, a):
            raise RuntimeError("boom")
    m.remove("gear:fn:rarity")
    K.eq(str(Page.rbg("Weapon_Sword_Frost")), NONE, "X no SkyyGear on the bridge -> the faint grey")
    gf = GearFn()
    m.put("gear:fn:rarity", gf)
    got = dict((i, str(Page.rbg(i))) for i in ANS)
    want = {"Weapon_Sword_Frost": gear["normal"], "Weapon_Axe_Bone": gear["unique"], "Sword_Iron_Green": gear["rare"], "Weapon_Bo_Iron": gear["legendary"],
            "Weapon_Wand_Iron": gear["fabled"], "Weapon_Sword_Mythic": NONE, "Weapon_Junk": NONE, "Weapon_Set_Piece": NONE}
    K.eq(got, want, "X gear:fn:rarity normal / unique / rare / legendary (trimmed, any case) / fabled -> the item rarity hex + (0.4); mythic / set / junk -> grey")
    K.check(gear["normal"] == "#FFFFFF(0.4)" and gear["unique"] == "#FFFF55(0.4)" and gear["rare"] == "#FF55FF(0.4)" and gear["legendary"] == "#55FFFF(0.4)"
            and gear["fabled"] == "#FF5555(0.4)", "X the item rarity colours = skyyui RARITY (%s)" % gear)
    K.eq((str(Page.rbg("Mount_Horse_Pack")), str(Page.rbg("Weapon_Boom")), str(Page.rbg(None)), str(Page.rbg(""))), (NONE, NONE, NONE, NONE),
         "X a mount / vanilla id (no answer), a throwing bridge, null, empty -> the faint grey (never throws)")
    m.put("gear:fn:rarity", Boom())
    K.eq(str(Page.rbg("Weapon_Sword_Frost")), NONE, "X a bridge that always throws -> the faint grey")
    m.put("gear:fn:rarity", gf)
    n0 = len(gf.calls)
    eg = dict((i, str(Page.rbg(i))) for i in EGG.IDS)
    K.check(len(eg) == 30 and all(v == egg[i.rsplit("_", 1)[1]] for i, v in eg.items()), "X the 30 pet eggs -> their rarity's quality colour (%s)" % list(eg.items())[:2])
    K.check(len(gf.calls) == n0, "X eggs never ask SkyyGear")
    K.eq((str(Page.rbg("Skyy_PetEgg_Dragon_Air")), str(Page.rbg("Skyy_PetEgg_Dragon_Void")), str(Page.rbg("Skyy_PetEgg_Mining_Shiny"))),
         (egg["Legendary"], egg["Legendary"], NONE), "X our dragon eggs = Legendary, an unknown egg suffix = grey")
    K.check(egg["Mythic"] == SUI.RARITY["Mythic"] + "(0.4)" and egg["Epic"] == SUI.QUALITY["Epic"] + "(0.4)", "X egg colours = SkyyPets RARITY_COLORS")
    # ---- the page build on a real UICommandBuilder: a stand-in site in zone 1 with weapons / a mount / an egg
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.join(scratch, "x1", "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyMerchants"), exist_ok=True)
    Cfg.load(P(mods))
    K.check(bool(Cfg.ON), "X merchants on (default file)")
    ids = ["Weapon_Sword_Frost", "Weapon_Axe_Bone", "Sword_Iron_Green", "Weapon_Bo_Iron", "Weapon_Wand_Iron", "Mount_Horse_Pack", "Skyy_PetEgg_Mining_Legendary",
           "Skyy_PetEgg_Farming_Epic"]
    ex = JClass("java.util.HashSet")()
    for i in ids:
        ex.add(i)
        Shop.NAMES.put(i, "Name " + i)
    Eng.EXTRA = ex
    site = J("MerchSite")()
    site.zone = "zone1"
    site.uuid = "npc-0108"
    site.placedAt = int(JClass("java.lang.System").currentTimeMillis())
    site.stock = ("0:Weapon_Sword_Frost:1000:1,0:Weapon_Axe_Bone:900:1,0:Sword_Iron_Green:800:0,0:Weapon_Bo_Iron:700:2,0:Weapon_Wand_Iron:600:1,"
                  "1:Mount_Horse_Pack:500:1,2:Skyy_PetEgg_Mining_Legendary:600000:1,2:Skyy_PetEgg_Farming_Epic:5000:0")
    lst = JClass("java.util.ArrayList")()
    lst.add(site)
    Reg.W.put(Reg.wf("default"), lst)
    K.check(J("MerchCore").siteOf("default", "zone1") is not None, "X the stand-in site is found")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PR.class_)
    for f in PR.class_.getDeclaredFields():
        if str(f.getType().getName()) == "java.util.UUID":
            f.setAccessible(True)
            f.set(pr, JClass("java.util.UUID").randomUUID())
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    page = Page(pr, "default", "zone1", "npc-0108")

    def build(tab):
        page.tab = tab
        b_, e_ = UCB(), UEB()
        page.build(None, b_, e_, None)
        return " | ".join("%s=%s/%s" % (x.selector, x.data, x.text) for x in b_.getCommands()), len(e_.getEvents())

    def squares(txt):
        return dict((int(a), b) for a, b in re.findall(r"Group #SkyyMcR(\d+)If \{ Anchor: \(Width: 44, Height: 44, Left: 0, Top: \d+\); Background: ([^;]+); \}", txt))
    t0, n0 = build(0)
    K.eq(squares(t0), {0: gear["normal"], 1: gear["unique"], 2: NONE, 3: gear["legendary"], 4: gear["fabled"]},
         "X Weapons tab: each row's square = its rarity; the sold-out Rare row = the faint grey")
    K.eq(n0, 4 + 4, "X Weapons tab: 4 Buy bindings (the sold-out row has none) + 4 base bindings (unchanged behaviour)")
    K.check(t0.count("Name Weapon_") + t0.count("Name Sword_") >= 5 and "Sold out - restocks when it moves" in t0, "X Weapons tab: names + sold-out text as before")
    K.check(not re.search(r"#SkyyMcR\d+Nm[^|]*TextColor: #(FFFF55|FF55FF|55FFFF|FF5555)", t0), "X the row names keep their soft-white kit colour (not rarity coloured)")
    t1, _ = build(1)
    K.eq(squares(t1), {0: NONE}, "X Mounts tab: a mount (no rarity answer) = the faint grey")
    t2, _ = build(2)
    K.eq(squares(t2), {0: egg["Legendary"], 1: NONE}, "X Pet eggs tab: a Legendary egg = Legendary gold; a sold-out Epic egg = grey")
    site.uuid = "someone-else"
    t3, n3 = build(0)
    K.check(squares(t3) == {} and n3 == 4, "X a merchant that moved on: no rows (as before)")
    K.save()


# ======================================================================================================== D: the live copy, twice
def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    reg0 = HK.tree_hash(os.path.join(home, "merchants")) if os.path.isdir(os.path.join(home, "merchants")) else {}
    snaps, msgs = [], []
    for start in (1, 2):
        L = loader(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        J("MerchLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyMerchants")
        J("MerchMig").run(P(mods))
        msgs.append(str(J("MerchMigP7").run(P(mods))))
        J("MerchCfg").load(P(mods))
        J("CfgPub").start(P(mods), J("MerchLog").LOG)
        K.check(bool(J("MerchCfg").ON) and len(J("MerchCfg").ZONES) >= 4, "D%d the live copy loads (%d zones)" % (start, len(J("MerchCfg").ZONES)))
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    new = sorted(set(snaps[0]) - set(h0))
    K.check(changed == [] and msgs[0] == "", "D the first start changes no file (0.1.7's updates already ran; 0.1.8 adds none): changed %s msg %r" % (changed, msgs[0][:120]))
    K.check(all(n.startswith(("config-history", "config-changes")) for n in new), "D only kit files may be new: %s" % new)
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "D the second start changes nothing")
    reg1 = HK.tree_hash(os.path.join(home, "merchants")) if os.path.isdir(os.path.join(home, "merchants")) else {}
    K.check(reg0 == reg1, "D the merchants registry is untouched")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMerchants", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("kit", run_kit), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMerchants"))
