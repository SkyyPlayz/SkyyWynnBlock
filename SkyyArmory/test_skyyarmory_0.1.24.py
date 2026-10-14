"""Harness for SkyyArmory 0.1.24 (BOSS SIGIL DROPS; tools/armory_0_1_24_patch.py). Build first:
    python tools/armory_0_1_24_patch.py && python SkyyArmory/build_skyyarmory_0.1.24.py

    python SkyyArmory/test_skyyarmory_0.1.24.py [--jar <SkyyArmory-0.1.24.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.23 -> 0.1.24: exactly the listed members differ (+ the version texts), no class added; non-class entries: manifest only
  X   exec     EVERY NEW CODE PATH: the config (fresh file lines, the loader with defaults / hand edits / bad values, the Server Setup check),
               SoulDrop.sigil for every boss / zone / roll / row / item-loaded case (ROLL + ITEMOK seams), the volcanic / no-zone rule,
               Monk.bossWord's whole-part rule on the real stun.bossWords
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): the 2nd start changes nothing, the new rows
               read their defaults, the file's bytes stay as the 0.1.23 start leaves them
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the 3 lines in SoulDrop.roll that read the dying NPC's role and add the Sigil stack to the essence
drop list (the essence path itself = 0.1.23, unchanged; a boss kill in game is the test). Exit code 1 on any failure.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.24", "0.1.23"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear4fix", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyArmory")
# the members 0.1.24 changes (version-text-only members checked by hand 2026-10-14: ArmoryCheck packCheck / packOf = the "Skyy:0.1.24 SkyyArmory" pack
# name, ArmoryCfg load / reloadAll / useDefaults + CfgFile / CfgRows <clinit> = the default file's first line, CfgFn opExport / CfgRows header
# = the version, SkyyArmoryPlugin setup = the "0.1.24 ready" lines)
EXPECT = {"ArmoryCfg": ["+f SGL_BOSS", "+f SGL_ON", "+f SGL_PCT", "+f SGL_PCT_DEF", "+f SGL_ZONE", "+f SGL_ZONE_DEF", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
          "ArmoryCheck": ["~m packCheck", "~m packOf"], "ArmoryDefs": ["+f SGL_IDS", "+f SGL_NAMES", "~<clinit>"], "ArmoryHooks": ["+m checkSigil"],
          "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyArmoryPlugin": ["~m setup"],
          "SoulDrop": ["+f BOSSES", "+f ITEMOK", "+f SIGILS", "+m itemOk", "+m sigil", "~<clinit>", "~m roll"]}
ADDED = []


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JObject, JBoolean, JString, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Cfg, Defs, Sd, Hooks, Monk = P("ArmoryCfg"), P("ArmoryDefs"), P("SoulDrop"), P("ArmoryHooks"), P("Monk")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    DEF = str(Cfg.DEF_CFG)
    K.check([str(x) for x in Defs.SGL_NAMES] == ["Unique", "Rare", "Legendary", "Fabled", "Mythic"]
            and [str(x) for x in Defs.SGL_IDS] == ["Skyy_Sigil_" + n for n in ("Unique", "Rare", "Legendary", "Fabled", "Mythic")],
            "X1: the five Sigil ids (SkyyGear 0.3.4's items) in rarity order")
    want = ["sigil.drops=true", "sigil.chance.Unique=0", "sigil.chance.Rare=4", "sigil.chance.Legendary=3", "sigil.chance.Fabled=1.5",
            "sigil.chance.Mythic=0", "sigil.zone.Unique=0", "sigil.zone.Rare=2", "sigil.zone.Legendary=3", "sigil.zone.Fabled=4", "sigil.zone.Mythic=0",
            "sigil.bossWords=Boss,Guardian,Duke,Dragon,Chieftain,Hedera"]          # fixer: Mythic no drop source; the narrower Sigil boss words
    K.check(all(("\n" + w + "\n") in DEF for w in want), "X1: a fresh config.properties carries the sigil rows at their defaults: %s" % [w for w in want if ("\n" + w + "\n") not in DEF])

    def apply(**kv):
        p = Props()
        p.load(SR(DEF))
        for k, v in kv.items():
            if v is None:
                p.remove(k.replace("__", "."))
            else:
                p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p)
    apply()
    K.check(bool(Cfg.SGL_ON) and list(Cfg.SGL_PCT) == [0.0, 4.0, 3.0, 1.5, 0.0] and list(Cfg.SGL_ZONE) == [0.0, 2.0, 3.0, 4.0, 0.0] and str(Cfg.SGL_BOSS) == "Boss,Guardian,Duke,Dragon,Chieftain,Hedera",
            "X1: the loader reads the defaults: %s %s" % (list(Cfg.SGL_PCT), list(Cfg.SGL_ZONE)))
    p = Props()
    p.load(SR(DEF))
    for k in [w.split("=")[0] for w in want]:
        p.remove(k)
    Cfg.apply(p)
    K.check(bool(Cfg.SGL_ON) and list(Cfg.SGL_PCT) == [0.0, 4.0, 3.0, 1.5, 0.0] and list(Cfg.SGL_ZONE) == [0.0, 2.0, 3.0, 4.0, 0.0] and str(Cfg.SGL_BOSS) == "Boss,Guardian,Duke,Dragon,Chieftain,Hedera",
            "X1: a live file WITHOUT the sigil lines (every server today) = the defaults (no one-time update needed)")
    apply(sigil__chance__Rare="250", sigil__zone__Mythic="-3", sigil__drops="false")
    K.check(not bool(Cfg.SGL_ON) and float(Cfg.SGL_PCT[1]) == 100.0 and float(Cfg.SGL_ZONE[4]) == 0.0, "X1: hand edits are clamped (250 %% -> 100, zone -3 -> 0), sigil.drops false read: %s %s" % (list(Cfg.SGL_PCT), list(Cfg.SGL_ZONE)))
    apply()
    K.check(Hooks.checkSigil("sigil.chance[Rare]", "5") is None and Hooks.checkSigil("sigil.zone[Mythic]", "4") is None
            and Hooks.checkSigil("sigil.chance[Normal]", "5") is not None and "Unique, Rare, Legendary, Fabled or Mythic" in str(Hooks.checkSigil("sigil.chance[Normal]", "5")),
            "X1: Server Setup's check names the five rarities (a Normal entry refused)")
    # SoulDrop.sigil: ROLL seam (0..100) + ITEMOK seam (which Sigil items are loaded)
    LOADED = {"v": True}

    @JImplements("java.util.function.Predicate")
    class ItemOk(object):
        @JOverride
        def test(self, o):
            return bool(LOADED["v"])
    Sd.ITEMOK = ItemOk()

    def sg(role, zone, roll, volc=False):
        Sd.ROLL = float(roll)
        r = Sd.sigil(role, JInt(zone), volc)
        return None if r is None else str(r)
    # FIX C1: by default the Mythic Sigil has NO drop source (G3 "No Mythic Sigil"): a Zone 4 boss's lowest roll gives Fabled, never Mythic
    c1 = [sg("Dragon_Frost", 4, 0.0), sg("Dragon_Frost", 4, 0.1), sg("Dungeon_Feastmaster_Boss", 9, 0.0)]
    K.check(c1 == ["Skyy_Sigil_Fabled"] * 3, "FIX C1: defaults: no Mythic Sigil from any boss (roll 0 in Zone 4 / 9 = Fabled): %s" % c1)
    # FIX C3: the Sigil boss words skip the stunlock's mini-bosses (ordinary Zone 2+ mobs), even at roll 0 in Zone 4; the real bosses still roll
    c3n = [sg(x, 4, 0.0) for x in ("Skeleton_Elite", "Yeti", "Golem_Crystal_Earth", "Golem_Firesteel", "Rex_Cave")]
    c3y = [sg(x, 4, 0.0) for x in ("Golem_Guardian_Void", "Trork_Chieftain", "Hedera", "Goblin_Duke")]
    K.check(c3n == [None] * 5 and c3y == ["Skyy_Sigil_Fabled"] * 4 and bool(Monk.bossWord("Yeti", Cfg.STUN_BOSS)),
            "FIX C3: Elite / Yeti / Golem / Rex mini-bosses never drop Sigils (the stunlock still counts Yeti a boss); Guardian / Chieftain / Hedera / Duke bosses do: %s %s" % (c3n, c3y))
    apply(sigil__chance__Mythic="0.25", sigil__zone__Mythic="4")          # an admin switches the Mythic Sigil on: the full ladder below
    b0 = int(Sd.BOSSES)
    got = [sg("Goblin_Duke", 1, 0.0), sg("Goblin_Duke", 2, 0.0), sg("Goblin_Duke", 2, 3.99), sg("Goblin_Duke", 2, 4.0),
           sg("Goblin_Duke", 3, 0.1), sg("Goblin_Duke", 3, 2.99), sg("Goblin_Duke", 3, 3.5), sg("Dragon_Frost", 4, 0.1),
           sg("Dragon_Frost", 4, 0.24), sg("Dragon_Frost", 4, 1.2), sg("Dragon_Frost", 4, 2.9), sg("Dragon_Frost", 4, 3.9), sg("Dragon_Frost", 4, 50.0)]
    K.check(got == [None, "Skyy_Sigil_Rare", "Skyy_Sigil_Rare", None, "Skyy_Sigil_Legendary", "Skyy_Sigil_Legendary", "Skyy_Sigil_Rare",
                    "Skyy_Sigil_Mythic", "Skyy_Sigil_Mythic", "Skyy_Sigil_Fabled", "Skyy_Sigil_Legendary", "Skyy_Sigil_Rare", None],
            "X2: one roll from Mythic down, the first hit drops: Zone 1 boss nothing (Unique never from bosses), Zone 2 Rare < 4 %%, Zone 3 Legendary < "
            "3 %% else Rare, Zone 4 (Mythic switched on) Mythic < 0.25 %%, Fabled < 1.5 %%, Legendary < 3 %%, Rare < 4 %%: %s" % got)
    K.check(int(Sd.BOSSES) == b0 + len(got), "X2: every boss call counted (BOSSES)")
    b1 = int(Sd.BOSSES)
    no = [sg("Trork_Grunt", 4, 0.0), sg("Snapdragon", 4, 0.0), sg(None, 4, 0.0), sg("Goblin_Duke", -1, 0.0), sg("Goblin_Duke", 0, 0.0)]
    K.check(no == [None] * 5 and int(Sd.BOSSES) == b1, "X2: never: a plain mob, Snapdragon (whole-part rule: not 'Dragon'), no role, no zone (-1 / volcanic passes -1), zone 0 - not even counted: %s" % no)
    LOADED["v"] = False
    nl = sg("Dragon_Frost", 4, 0.0)
    LOADED["v"] = True
    apply(sigil__drops="false")
    off = sg("Dragon_Frost", 4, 0.0)
    apply(sigil__chance__Mythic="0", sigil__chance__Fabled="0")
    z0 = sg("Dragon_Frost", 4, 0.0)
    apply(sigil__zone__Rare="0", sigil__zone__Legendary="0", sigil__zone__Fabled="0", sigil__zone__Mythic="0")
    zz = sg("Dragon_Frost", 4, 0.0)
    apply(sigil__zone__Unique="1", sigil__chance__Unique="100")
    un = sg("Goblin_Duke", 1, 99.0)
    apply(sigil__bossWords="Gorilla")
    words = [sg("Goblin_Duke", 4, 0.0), sg("Jungle_Gorilla", 4, 0.0)]
    apply(stun__bossWords="Gorilla")
    words2 = [sg("Goblin_Duke", 4, 0.0), sg("Jungle_Gorilla", 4, 0.0)]
    apply()
    K.check(nl is None and off is None and z0 == "Skyy_Sigil_Legendary" and zz is None and un == "Skyy_Sigil_Unique" and words == [None, "Skyy_Sigil_Fabled"]
            and words2 == ["Skyy_Sigil_Fabled", None],
            "X3: no Sigil item loaded (no SkyyGear 0.3.4) = nothing (never an unknown item); sigil.drops off = nothing; a 0 %% chance skips that rarity; "
            "zone 0 = never; an admin may turn Unique on (zone 1, 100 %%); the boss words are the live sigil.bossWords row (stun.bossWords no longer counts): %s" % [nl, off, z0, zz, un, words, words2])
    Sd.ROLL = -1.0
    Sd.ITEMOK = None
    real = [bool(Sd.itemOk("Skyy_Sigil_Rare"))]
    K.check(real == [False], "X3: itemOk without the seam reads the item asset map (a bare JVM has no Sigil item = false, as on a server without SkyyGear 0.3.4)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.24 (new rows absent = defaults): %s" % (before is not None))
    K.check(bool(Cfg.SGL_ON) and list(Cfg.SGL_PCT) == [0.0, 4.0, 3.0, 1.5, 0.0] and list(Cfg.SGL_ZONE) == [0.0, 2.0, 3.0, 4.0, 0.0] and str(Cfg.SGL_BOSS) == "Boss,Guardian,Duke,Dragon,Chieftain,Hedera",
            "D: the live copy reads the sigil defaults")
    K.notes.append("D: live config.properties %s bytes" % (len(before) if before else 0))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyArmory", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
