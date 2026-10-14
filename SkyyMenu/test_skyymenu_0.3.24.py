"""Harness for SkyyMenu 0.3.24 (/soundtest + the rebirth / sound buttons on the Admin page; tools/menu_0_3_24_patch.py).
Build first: python tools/menu_0_3_24_patch.py && python SkyyMenu/build_skyymenu_0.3.24.py

    python SkyyMenu/test_skyymenu_0.3.24.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.23 -> 0.3.24: + SoundTest, SoundTestArgCmd, SoundTestCmd; OpsPage's tables (the 7 rows), MenuData (the help line), the
              plugin's setup (registers /soundtest), the version texts
  SND /soundtest EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py: every Assets.zip sound id in the engine's SoundEvent
      store, a stand-in player on a REAL GamePacketHandler): help / list (the 14 ids this round's mods use, each with where) / more (the
      plan's candidates) / a number = ONE PlaySoundEvent2D of that id (UI) to the admin only / next + prev (per admin, wrapping) / any id /
      a missing id, a bad id, a number out of range = an answer and NO packet; every list id is in Assets.zip, unique, and every mod's
      default sound id of this round is listed; the commands: /soundtest + its usage variant need skyymenu.modconfig (requirePermission)
      and the ENGINE's own parser takes "/soundtest", "/soundtest list", "/soundtest 3", "/soundtest SFX_Coins_Land" to the player-only
      execute (and refuses two words); the real SoundTestArgCmd.execute path sends the chat lines + the sound
  O   the 0.3.23 Admin-page phase on the 0.3.24 jar (test_skyymenu_0.3.23.py's run_ops; its one Text value per button, "Oak_Log.2", is
      replaced by a per-line value where the command needs a number / arm: crashtest 3, points / refund Mining or all, soundtest
      SFX_Coins_Land): every row against the REAL command objects of the SET jars (SkyyRebirth 0.3.1: crashtest / points / refund are
      sub-commands, O_DEPTH 1), every dispatch line through the ENGINE's parser, permission hiding = the engine's verdict, confirm timing,
      paging (Players now 45 buttons = 2 pages), the page itself
  S D   the 0.3.22 shards phase and the 0.3.19 live phase carried forward (D = start twice on a scratch COPY of the live Skyy_SkyyMenu);
        T / N (0.3.21 tabs, 0.3.20 names) are not re-run: their old-side jars (0.3.20 / 0.3.19) are no longer kept and 0.3.24 does not
        touch those classes (phase C)
  FIX the critic fix: Rebirth crash test is a danger row (page confirm + the command's own), EXECUTED on a real OpsPage + RbAdminCmd
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SK

# the 0.3.23 harness, its Text value per button made per-line (a crash test needs a number, points / refund an arm)
TEXTS = {"rebirthadmin crashtest {t}": "3", "rebirthadmin points {t} 100": "Mining", "rebirthadmin points {t} reset": "all",
         "rebirthadmin refund {t}": "Mining", "soundtest {t}": "SFX_Coins_Land"}
_p23 = os.path.join(HERE, "test_skyymenu_0.3.23.py")
_src = open(_p23, encoding="utf-8").read()
for _a, _b, _n in (('.replace("{t}", TEXT)', '.replace("{t}", TEXTS.get(LINES[i], TEXT))', 1),
                   ("        p.arg = TEXT\n", "        p.arg = TEXTS.get(LINES[i], TEXT)\n", 1),
                   ("""'{"a":"op%d","@OpsArg":"%s"}' % (i, TEXT))""", """'{"a":"op%d","@OpsArg":"%s"}' % (i, TEXTS.get(LINES[i], TEXT)))""", 2)):
    assert _src.count(_a) == _n, (_a, _src.count(_a))
    _src = _src.replace(_a, _b)
_src = _src.replace('if __name__ == "__main__":', 'if False:', 1)
T23 = types.ModuleType("test_skyymenu_0_3_23x")
T23.__file__ = _p23
T23.TEXTS = TEXTS
exec(compile(_src, _p23, "exec"), T23.__dict__)
T22, T21, T20, T19 = T23.T22, T23.T21, T23.T20, T23.T19

VERSION = "0.3.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.23.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound1fix", "menu")))
PKG = "com.skyy.menu."
EXPECT = {
    "MenuData": ["~<clinit>"],                       # the Mods text line /soundtest + the version
    "CfgRows": ["~m header"],                        # the version text
    "CfgFn": ["~m opExport"],                        # the version text
    "SkyyMenuPlugin": ["~m setup"],                  # registers /soundtest + the ready line
    "OpsPage": ["~<clinit>"],                        # the OPS tables: 4 rebirth + 3 sound rows
}
ADDED = ["SoundTest", "SoundTestArgCmd", "SoundTestCmd"]
ROUND_DEFAULTS = ["SFX_Dungeon_Checkpoint_Activate", "SFX_Event_Chapter_1_Complete_Sting", "SFX_Coins_Land", "SFX_Drag_Items_Paper",
                  "SFX_Chest_Wooden_Open_Player", "SFX_Wood_Land", "SFX_Coffer_Goblin_Reward", "SFX_Memories_Unlock_Local",
                  "SFX_Portal_Neutral_Teleport_Local", "SFX_Deployable_Totem_Heal_Spawn", "SFX_Deployable_Totem_Heal_Despawn"]


def run_snd(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    st = SK.Stage()
    ST, Arg, Cmd = JClass(PKG + "SoundTest"), JClass(PKG + "SoundTestArgCmd"), JClass(PKG + "SoundTestCmd")
    pa = st.player("Skyy", "00000000-0000-0000-0000-0000000000a4")
    pb = st.player("Bob", "00000000-0000-0000-0000-0000000000b4")
    st.universe()
    IDS, USES, IN_USE = [str(x) for x in ST.IDS], [str(x) for x in ST.USES], int(ST.IN_USE)
    K.check(all(i in st.ids for i in IDS) and len(set(IDS)) == len(IDS) and IN_USE == 14 and len(IDS) > IN_USE, "LIST %d ids (%d in use), unique, every one in Assets.zip" % (len(IDS), IN_USE))
    K.check(all(d in IDS[:IN_USE] for d in ROUND_DEFAULTS), "LIST every default sound id of this round's mods is in the 'list' part")

    def run(arg, who=None):
        st.clear()
        return [str(x) for x in ST.run(who or pa, arg)]
    h = run(None)
    K.check(len(h) == 3 and "/soundtest list" in h[0] and st.sounds() == [], "CMD help (no argument): 3 lines, no sound")
    K.eq(run("help"), h, "CMD /soundtest help = the help")
    L = run("list")
    K.check(len(L) == IN_USE + 2 and L[1] == " #1 %s - %s" % (IDS[0], USES[0]) and st.sounds() == [], "CMD list: the %d in-use ids numbered with their use" % IN_USE)
    M_ = run("more")
    K.check(len(M_) == len(IDS) - IN_USE + 2 and M_[1].startswith(" #%d " % (IN_USE + 1)) and st.sounds() == [], "CMD more: the plan's candidates, numbered after the list")
    K.eq(len(run("all")), len(IDS) + 2, "CMD all: every id")
    r = run("3")
    K.check(r[0].startswith("+Playing #3 SFX_Coins_Land") and st.sounds() == [("Skyy", "SFX_Coins_Land", "UI", "2d")], "CMD /soundtest 3 = ONE PlaySoundEvent2D to the admin only: %s" % r)
    r = run("next")
    K.check(r[0].startswith("+Playing #4 ") and st.sounds() == [("Skyy", IDS[3], "UI", "2d")], "CMD next after #3 = #4")
    run("prev")
    run("prev")
    K.eq(st.sounds(), [("Skyy", IDS[1], "UI", "2d")], "CMD prev twice = #2")
    r = run("next", pb)
    K.check(r[0].startswith("+Playing #1 ") and st.sounds() == [("Bob", IDS[0], "UI", "2d")], "CMD next: a cursor per admin (Bob starts at #1)")
    run(str(len(IDS)))
    r = run("next")
    K.check(r[0].startswith("+Playing #1 "), "CMD next wraps after the last")
    run("1")
    r = run("prev")
    K.check(r[0].startswith("+Playing #%d " % len(IDS)), "CMD prev wraps before the first")
    r = run("SFX_Tornado")
    K.check(r[0].startswith("+Playing #") and st.sounds() == [("Skyy", "SFX_Tornado", "UI", "2d")], "CMD a listed id by name (its number shown)")
    r = run("SFX_Ice_Ball_Death")
    unl = "SFX_Ice_Ball_Death" in st.ids
    r2 = run("SFX_Coins_Walk")
    K.check(r2[0].startswith("+Playing SFX_Coins_Walk") and st.sounds() == [("Skyy", "SFX_Coins_Walk", "UI", "2d")], "CMD any vanilla id not in the list plays")
    for bad, what in ((SK.BAD_ID, "a missing id"), ("SFX Coins", "a space"), ("0", "number 0"), (str(len(IDS) + 1), "a number past the list"), ("x" * 121, "121 characters")):
        r = run(bad)
        K.check(len(r) == 1 and r[0].startswith("-") and st.sounds() == [], "CMD %s = an answer, no packet: %s" % (what, r[0][:80]))
    K.check(not str(ST.play(None, "SFX_Coins_Land", "x")).startswith("+"), "CMD play without a player = refused, no throw")
    # the real execute paths: the chat lines + the sound
    st.clear()
    ST.send(pa, ST.run(pa, "5"))
    ch = st.chats("Skyy")
    K.check(ch and ch[0][1].startswith("[Sound test] Playing #5 ") and st.sounds() == [("Skyy", IDS[4], "UI", "2d")], "CMD send: the chat line [Sound test] ... + the sound: %s" % ch)
    # the commands: node + the engine's parser
    root, var = Cmd(), Arg()
    K.check(str(root.getName()) == "soundtest" and str(root.getPermission()) == "skyymenu.modconfig" and str(var.getPermission()) == "skyymenu.modconfig",
            "PERM /soundtest + its usage variant require skyymenu.modconfig")
    PM, HS = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule"), JClass("java.util.HashSet")
    MSGS = []

    def sender(nodes):
        ns = HS()
        for n_ in nodes:
            ns.add(n_)

        @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
        class Snd(object):
            @JOverride
            def getUsername(self):
                return "Tester"

            @JOverride
            def getUuid(self):
                return JClass("java.util.UUID")(1, 2)

            @JOverride
            def sendMessage(self, m):
                MSGS.append(str(m.getMessageId() or m.getRawText()))

            @JOverride
            def hasPermission(self, q, *rest):
                rr = PM.hasPermission(ns, str(q)) if str(q.getClass().getName()) == "java.lang.String" else PM.hasPermission(ns, q)
                return bool(rr) if rr is not None else False
        return Snd()

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    root.setOwner(Owner())
    try:
        root.completeRegistration()
    except Exception as e:
        K.notes.append("completeRegistration: %s" % str(e)[:80])
    Tok, PCx, PRs = (JClass("com.hypixel.hytale.server.core.command.system.Tokenizer"), JClass("com.hypixel.hytale.server.core.command.system.ParserContext"),
                     JClass("com.hypixel.hytale.server.core.command.system.ParseResult"))

    def parse(line, snd):
        del MSGS[:]
        res = PRs()
        toks = Tok.parseArguments(line, res)
        ctx = PCx.of(toks, line, res)
        try:
            root.acceptCall(snd, ctx, res)
        except Exception as e:
            MSGS.append("EXC " + str(e)[:200])
        if res.failed():
            res.sendMessages(snd)
            return False, list(MSGS)
        return True, list(MSGS)
    adm, nobody = sender(["skyymenu.modconfig"]), sender([])
    for line in ("soundtest", "soundtest list", "soundtest 3", "soundtest SFX_Coins_Land", "soundtest next"):
        ok, ms = parse(line, adm)
        K.check(ok and "server.commands.errors.playerOrArg" in ms, "PARSE /%s reaches the player-only execute (%s)" % (line, ms[:1]))
    ok, ms = parse("soundtest list now", adm)
    K.check(not ok, "PARSE /soundtest with two words is refused (%s)" % ms[:1])
    ok, ms = parse("soundtest list", nobody)
    K.check(not ok or "server.commands.errors.playerOrArg" not in ms, "PARSE a sender without skyymenu.modconfig never reaches it (%s)" % ms[:1])
    K.save()


def run_fix(out, jar, scratch, _home):
    """FIX (critic 2026-10-14): Rebirth crash test is a danger row - the page asks for a 2nd press before /rebirthadmin crashtest is sent,
    and the command's own type-it-twice confirm stays: EXECUTED on a real OpsPage + the REAL SkyyRebirth 0.3.1 command tree."""
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    rb = os.path.join(ROOT, "SkyyRebirth", "SkyyRebirth-0.3.1.jar")
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, rb], verify=True)
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    OP = JClass(PKG + "OpsPage")
    LINES, LABELS, CONF = [str(x) for x in OP.O_LINE], [str(x) for x in OP.O_LABEL], [bool(x) for x in OP.O_CONF]
    ci, pi = LINES.index("rebirthadmin crashtest {t}"), LINES.index("rebirthadmin points {t} 100")
    K.check(LABELS[ci] == "Rebirth crash test" and CONF[ci], "FIX the Rebirth crash test row is a danger row (O_CONF true)")
    K.check(all(CONF[LINES.index(x)] for x in ("rebirthadmin points {t} reset", "rebirthadmin refund {t}", "rebirthadmin recover")),
            "FIX wipe / refund / recover stay danger rows")
    K.check(not CONF[pi], "FIX Rebirth test points stays a one-press button (additive test points; rejected finding)")
    PM, HS = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule"), JClass("java.util.HashSet")

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
    class Snd(object):
        @JOverride
        def getUsername(self):
            return "Skyy"

        @JOverride
        def getUuid(self):
            return JClass("java.util.UUID")(1, 2)

        @JOverride
        def sendMessage(self, m):
            pass

        @JOverride
        def hasPermission(self, q, *rest):
            ns = HS()
            ns.add("*")
            r = PM.hasPermission(ns, str(q)) if str(q.getClass().getName()) == "java.lang.String" else PM.hasPermission(ns, q)
            return bool(r) if r is not None else False

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    root = JClass("com.skyy.rebirth.RbAdminCmd")()
    root.setOwner(Owner())
    try:
        root.completeRegistration()
    except Exception as e:
        K.notes.append("completeRegistration: %s" % str(e)[:80])
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PR.class_)
    c_ = PR.class_
    while c_ is not None:
        try:
            f = c_.getDeclaredField("uuid")
            f.setAccessible(True)
            f.set(pr, JClass("java.util.UUID").fromString("00000000-0000-4000-8000-000000000324"))
            break
        except Exception:
            c_ = c_.getSuperclass()
    HM, AL, Long, Bool = JClass("java.util.HashMap"), JClass("java.util.ArrayList"), JClass("java.lang.Long"), JClass("java.lang.Boolean")

    def page():
        p = OP(pr, 2)
        t = HM()
        t.put("cmd:rebirthadmin", root)
        t.put("sender", Snd())
        t.put("online", JArray(JString)(["Skyy"]))
        t.put("page", Bool.TRUE)
        t.put("ran", AL())
        t.put("now", Long(1000000))
        p.test = t
        return p

    def press(p, ms, i=ci, txt="3"):
        p.test.put("now", Long(ms))
        p.handleDataEvent(None, None, '{"a":"op%d","@OpsArg":"%s"}' % (i, txt))
        return [str(x) for x in p.test.get("ran")]
    p = page()
    K.check(bool(p.visible(ci)), "FIX the crash test button shows for an admin (real /rebirthadmin crashtest leaf)")
    K.eq(press(p, 1000000), [], "FIX crash test: ONE press sends nothing (a /rebirthadmin crashtest 3 typed earlier can no longer be completed by one press)")
    K.check(str(p.info).startswith("=Press Rebirth crash test again within 10 s") and p.armedNow(ci), "FIX crash test: the page asks for a 2nd press (%s)" % p.info)
    K.eq(press(p, 1000200), [], "FIX crash test: a 2nd press within 400 ms is one double-click, nothing sent")
    K.eq(press(p, 1003000), ["rebirthadmin crashtest 3"], "FIX crash test: the 2nd press within 10 s sends /rebirthadmin crashtest 3 (the command then asks again)")
    K.eq(press(p, 1005000), ["rebirthadmin crashtest 3"], "FIX crash test: press 3 only re-arms the page, nothing sent")
    K.check(p.armedNow(ci), "FIX crash test: press 3 armed again")
    K.eq(press(p, 1007000), ["rebirthadmin crashtest 3", "rebirthadmin crashtest 3"], "FIX crash test: press 4 sends it again (= the command's confirm, 4 s after its ask)")
    q = page()
    K.eq(press(q, 1000000), [], "FIX crash test: armed on a fresh page")
    K.eq(press(q, 1000000 + 10001), [], "FIX crash test: a 2nd press after 10 s re-arms instead of running")
    K.check(str(q.info).startswith("=The 10 s ran out"), "FIX crash test: says the 10 s ran out (%s)" % q.info)
    r = page()
    K.eq(press(r, 1000000, pi, "Mining"), ["rebirthadmin points Mining 100"], "FIX test points still one press")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           # T / N (0.3.21 run_tabs, 0.3.20 run_name) need the 0.3.20 / 0.3.19 jars as their "old" side - those jars are no longer kept here;
           # the classes they test (SettingsPage, PetTile, StatsCalc, MenuData's tables) are unchanged by 0.3.24 (phase C: MenuData differs
           # only in <clinit> = the one help line + the version), so they are not re-run
           phases=[("snd", run_snd), ("fix", run_fix), ("ops", T23.run_ops), ("shards", T22.run_shards), ("live", T19.run_live)],
           script=__file__, live=(T23.LIVE_DIR, "Skyy_SkyyMenu"))
