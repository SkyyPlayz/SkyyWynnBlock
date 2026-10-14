"""SkyyClasses 0.1.21 - harness for ABILITY LINES -> FEED (tools/classes_0_1_21_patch.py; the shared tools/skyyroute.py MsgRoute).
Build first: python tools/classes_0_1_21_patch.py && python SkyyClasses/build_skyyclasses_0.1.21.py

    python SkyyClasses/test_skyyclasses_0.1.21.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. Live save data is only READ / copied.
  OLD  test_skyyclasses_0.1.20.py's own sections on the 0.1.21 jar: its OLD part (the 0.1.19 harness: loadout bridge + start twice on a
       scratch COPY of the live Skyy_SkyyClasses folder) and its R phase (MsgRoute + the heal routes, every check) as phase "route20"
  A    verify   every class loads + initialises with -Xverify:all (tools/harness_kit.py)
  C    compare  0.1.20 -> 0.1.21: exactly Abil.say changes + Abil.feedText is added (+ the version texts); no class added
  B    ability  EXECUTED with a stand-in SkyyHud on the skyy.bridge map, Abil.say on real cast / result lines of every ability + shape:
                chat = the 0.1.20 line word for word (0.1.20's own Abil.say on the same input, CONTROL); feed = one card (kind ability,
                no icon, feedText <= 48 characters, no chat line); feed refused = the chat line; off = nothing (OFF counted); no SkyyHud
                / a SkyyHud older than 0.3.22 (no "ability" kind: msgroute answers chat) / a SkyyHud without msgroute = the chat line;
                the admin switch abil.castChat OFF and the player's classes.abilChat OFF still hide it on every route; REFUSALS
                (Abil.refuse: not enough Mana, on cooldown) and Abil.send warnings stay in chat on the Feed route (CONTROL: 0.1.20 sends
                the same); feedText examples; SESSION: 10 casts + results with no SkyyHud vs the Feed route
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.21"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.20.jar")
BASE = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "msgtab", "cl")))
SCRATCH = BASE if "--phase" in sys.argv else os.path.join(BASE, "h")
os.environ["SKYYROUTE_SESSION"] = os.path.join(BASE, "session")      # T20's SESSION file lands in OUR scratch
_spec = importlib.util.spec_from_file_location("test_skyyclasses_0_1_20", os.path.join(HERE, "test_skyyclasses_0.1.20.py"))
T20 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T20)

EXPECT = {
    "Abil": ["+m feedText", "~m say"],
    # version texts only: the ready line / pack name, kits.properties "version", the config kit's export header
    "SkyyClassesPlugin": ["~m setup"],
    "KitMigrate": ["~m runOnce"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header"],
}
ADDED = []


def run_ability(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    # each jar in its own loader over the SYSTEM class path (the engine only): one PlayerRef class serves both
    def ldr(j):
        a_ = JClass("java.net.URL")[1]
        a_[0] = JClass("java.io.File")(j).toURI().toURL()
        return JClass("java.net.URLClassLoader")(a_, JClass("java.lang.ClassLoader").getSystemClassLoader())
    LN, L = ldr(jar), ldr(OLD_JAR)
    P = lambda n: JClass(PKG + n, loader=LN)
    MR, AB, Cfg, AC, AD = P("MsgRoute"), P("Abil"), P("ClassCfg"), P("AbilCfg"), P("AbilDefs")
    OAB, OMR = JClass(PKG + "Abil", loader=L), JClass(PKG + "MsgRoute", loader=L)
    UUID, Bool, AL = JClass("java.util.UUID"), JClass("java.lang.Boolean"), JClass("java.util.ArrayList")
    bridge = Cfg.bridge()
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    S = {"route": {}, "ok": True, "cards": [], "set": {}}

    def f_route(o):
        return S["route"].get(str(o[1]), "chat")

    def f_feed(o):
        S["cards"].append((str(o[1]), None if o[2] is None else str(o[2]), str(o[3]), None if o[4] is None else int(o[4])))
        return Bool.TRUE if S["ok"] else Bool.FALSE

    def f_set(o):
        v = S["set"].get(str(o[1]))
        return None if v is None else Bool.valueOf(v)
    FR, FF, FS = Fn(f_route), Fn(f_feed), Fn(f_set)

    def hud(on=True, route=None, msgroute=True):
        for k in ("msgroute:fn:get", "feed:fn:push"):
            bridge.remove(k)
        if on:
            if msgroute:
                bridge.put("msgroute:fn:get", FR)
            bridge.put("feed:fn:push", FF)
        S["route"], S["ok"], S["cards"] = dict(route or {}), True, []
        MR.CACHE.clear()
        OMR.CACHE.clear()
        AB.SAID, OAB.SAID = AL(), AL()
    bridge.put("settings:fn:get", FS)

    u = UUID.fromString("00000000-0000-4000-8000-000000000221")
    pr = U.allocateInstance(PR.class_)
    f_ = PR.class_.getDeclaredField("uuid")
    f_.setAccessible(True)
    f_.set(pr, u)

    def said(M):
        return [str(x) for x in M.SAID]

    # real lines: the cast line of every ability + shape (the 0.1.20 Abil.castNow text) and the result lines it sends
    fmt, secs = P("AbilMath").fmt, P("AbilMath").secs
    casts = []
    for ai in range(len(AD.IDS)):
        for sh in range(4):
            dn = str(AD.sname(ai, sh))
            if dn:
                casts.append(dn + "! -" + str(fmt(25.0)) + " Mana, -" + str(fmt(12.5)) + " Stamina. Ready again in " + str(secs(12500)) + " s.")
    results = [
        "Meteor hit 3 enemies (" + str(fmt(25.0)) + " damage each before armour).", "Meteor hit nothing.",
        "Sacred Heal: +45 HP to 3 players, healing over 5 s.",
        "Mana Barrier: a dome of 6 blocks for 10 s - damage to you inside costs Mana (2.5 per Mana) instead of Health.",
        "Shield Bubble: 120 HP for 12 s - it soaks attacks on you and your party inside and heals at 75 / 50 / 25 % and when it breaks.",
        "Mana Barrier ended - out of Mana (120 damage soaked for 40 Mana).",
        "Guardian Spirit saved you at 10 % Health (-20 Mana, -10 Stamina). Next save for you in 60 s.",
        "A Guardian Spirit (Skyy) saved you - 10 % Health.",
        "Arcane Beam stopped - out of Mana: 10 hits, 300 damage before armour.",
        "Running Blessing ended - it touched 4 players (+60 HP, healing over time follows).",
        "Frost Wake melted - it froze 2 enemies.",
    ]
    lines = casts + results
    K.check(len(casts) >= 20, "B: %d cast lines (every ability + shape)" % len(casts))

    # ---- chat (the server default): word for word = 0.1.20
    for label, kw in (("chat", dict(route={"ability": "chat"})), ("no SkyyHud", dict(on=False)),
                      ("SkyyHud older than 0.3.22 (no ability kind)", dict(route={"heal": "feed"})),
                      ("SkyyHud without msgroute", dict(msgroute=False))):
        hud(**kw)
        for t in lines:
            AB.say(pr, t)
            OAB.say(pr, t)
        K.check(said(AB) == said(OAB) == lines and S["cards"] == [], "B %s: every line in chat, word for word = 0.1.20 (%d lines)" % (label, len(said(AB))))
    # ---- feed
    hud(route={"ability": "feed"})
    for t in lines:
        AB.say(pr, t)
        OAB.say(pr, t)
    K.eq(said(AB), [], "B feed: no chat line")
    K.eq(said(OAB), lines, "B CONTROL 0.1.20: the same lines stay in chat on the Feed route")
    K.eq(len(S["cards"]), len(lines), "B feed: one card per line")
    K.check(all(c[0] == "ability" and c[1] is None and c[3] is None for c in S["cards"]), "B feed: kind ability, no icon, no count")
    K.check(all(0 < len(c[2]) <= 48 for c in S["cards"]), "B feed: every card text <= 48 characters: %s" % [c[2] for c in S["cards"] if len(c[2]) > 48])
    K.check(all(c[2] == str(AB.feedText(t)) for c, t in zip(S["cards"], lines)), "B feed: the card text = feedText(line)")
    short = [t for t in lines if len(t) <= 48]
    K.check(short and all(str(AB.feedText(t)) == t for t in short), "B feedText: a line that fits is the card word for word")
    cards = dict(zip(lines, [c[2] for c in S["cards"]]))
    for t, want in ((casts[0], None), (results[0], "Meteor hit 3 enemies (" + str(fmt(25.0)) + " damage each)."), (results[2], "Sacred Heal: +45 HP to 3 players"),
                    (results[3], "Mana Barrier: a dome of 6 blocks for 10 s"), (results[5], "Mana Barrier ended - out of Mana."),
                    (results[6], "Guardian Spirit saved you at 10 % Health."), (results[7], "A Guardian Spirit saved you - 10 % Health."),
                    (results[8], "Arcane Beam stopped - out of Mana: 10 hits")):
        if want is None:
            K.check(" Mana " in cards[t] + " " and "Stam" in cards[t] and "ready in" in cards[t], "B feedText cast: %r -> %r" % (t, cards[t]))
        else:
            K.eq(cards[t], want, "B feedText %r" % t)
    for c in sorted(set(cards[t] for t in casts), key=len)[-3:]:
        K.notes.append("longest cast cards: %s" % c)
    K.check(not [cards[t] for t in casts if cards[t].endswith("...")], "B feedText: no cast card is cut with '...'")
    # ---- feed refused -> chat
    hud(route={"ability": "feed"})
    S["ok"] = False
    AB.say(pr, results[0])
    K.eq(said(AB), [results[0]], "B feed refused (Feed widget hidden / SkyyHud said no) -> the chat line")
    # ---- off
    hud(route={"ability": "off"})
    o0 = int(MR.OFF.get())
    for t in lines[:5]:
        AB.say(pr, t)
    K.check(said(AB) == [] and S["cards"] == [] and int(MR.OFF.get()) == o0 + 5, "B off: nothing sent, OFF counted")
    # ---- the two switches still hide it first, on every route
    for r_ in ("chat", "feed"):
        hud(route={"ability": r_})
        S["set"]["classes.abilChat"] = False
        AB.say(pr, results[0])
        S["set"].pop("classes.abilChat")
        AC.CAST_CHAT = False
        AB.say(pr, results[0])
        AC.CAST_CHAT = True
        K.check(said(AB) == [] and S["cards"] == [], "B %s: classes.abilChat OFF / abil.castChat OFF still hide the line" % r_)
    # ---- refusals + warnings stay in chat on the Feed route
    hud(route={"ability": "feed"})
    refs = ["Not enough Mana - Meteor needs 25 Mana.", "Meteor is on cooldown - ready again in 4 s."]
    for i, t in enumerate(refs):
        P("AbilStore").TOLD.clear()
        JClass(PKG + "AbilStore", loader=L).TOLD.clear()
        AB.refuse(pr, t)
        OAB.refuse(pr, t)
    AB.send(pr, "Starfall Below broke - you moved. Your Mana, Stamina and cooldown were given back.", "#ffc800")
    OAB.send(pr, "Starfall Below broke - you moved. Your Mana, Stamina and cooldown were given back.", "#ffc800")
    K.check(said(AB) == said(OAB) and len(said(AB)) == 3 and S["cards"] == [],
            "B refusals + warnings stay in chat on the Feed route (= 0.1.20): %s" % said(AB))
    K.check(refs[0] in said(AB), "B the first refusal is in chat")
    # ---- SESSION: 10 casts, each with one result line
    def session(defaults):
        hud(defaults is not None, defaults)
        for i in range(10):
            MR.CACHE.clear()
            AB.say(pr, casts[i % len(casts)])
            AB.say(pr, results[i % len(results)])
        return len(said(AB)), len(S["cards"])
    before, after = session(None), session({"ability": "feed"})
    K.check(before == (20, 0) and after == (0, 20), "B SESSION: 20 ability lines in chat without SkyyHud, %d with Feed (%d cards)" % after)
    sd = os.environ.get("SKYYROUTE_SESSION")
    if sd:
        os.makedirs(sd, exist_ok=True)
        json.dump({"mod": "SkyyClasses " + VERSION, "before": before[0], "after": after[0], "cards": after[1], "what": "10 casts + 10 results"},
                  open(os.path.join(sd, "classes-ability.json"), "w"), indent=1)
    K.save()


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        assert os.path.realpath(BASE).startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep)
        T20.BASE = BASE
        T20.JAR = JAR
        T20.old_sections()
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("ability", run_ability), ("route20", T20.run_route)], script=__file__)
