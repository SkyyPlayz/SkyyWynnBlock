"""SkyySkills 0.4.44 - harness for tools/skills_0_4_44_patch.py: (A) THE ROLL GOES EVERY WAY (the client's own dodge input through the
player's Interactions slot InteractionType.Dodge; the 0.4.43 server sprint press off in that mode; row acro.rollKey), (B) DODGE STYLES BY
CLASS (roll / lunge / flip roots, acro.dodgeStyle.<class>), (C) PERFECT DODGE TUNING (100 ms, caps 1000000, any attacker, stacks with
Perfect Parries, HUD flash, Pd44Mig).
Build first: python tools/skills_0_4_44_patch.py && python SkyySkills/build_skyyskills_0.4.44.py

    python SkyySkills/test_skyyskills_0.4.44.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.43 -> 0.4.44: + Pd44Mig; only the planned members of Acro / AcroCfg / AcroSys / PDodge / PDodgeSys / PCounterSys / Ranch
               + the config texts differ; non-class entries: manifest.json + the 67 new dodge-style asset files
  DIR THE DIRECTION PICK EXECUTED BY THE ENGINE, per style (roll = Dodge.json's MovementCondition, lunge / flip = their named Pick): the
      engine's own codec decodes it, then the REAL MovementConditionInteraction.tick0 for every MovementDirection (None + the 8) on a
      real InteractionContext / InteractionEntry / InteractionChain -> the label it jumps to -> the branch (the engine's *_LABEL_INDEX
      table) -> the body; each body's cost, i-frames, look effect -> animation (flip: the Shortbow item animation step), push X / Y / Z +
      force read the way the engine follows the names; the anim step + a push decoded by the engine codecs; the style roots -> Main ->
      Pick, Cooldown 0
  KEY the dodge-input slot on the REAL Acro + the REAL engine Interactions component (stand-in Store / CommandBuffer; a real
      InteractionModule instance): bindPlan for every case (our 3 roots, another mod's root, off); keyBind (no component -> one put,
      empty -> in place, already right -> nothing, another of ours -> replaced, another mod's -> left + WARN, off -> out, a broken store
      -> 9); the style per class (AcroCfg.readStyles defaults / custom / bad values, styleFor, styleRoot); keyTick once a second with
      class:<uuid> (Warrior = lunge, Priest = flip, none = roll, a class switch rebinds), acro.rollKey / acro.dodgeTap off -> out
  TAP the 0.4.43 server press: key mode = no server roll; acro.rollKey=false = 0.4.43's press; WIRE (AcroSys.tick -> keyTick; keyTick ->
      wantRoot -> SkillClass.className; keyBind -> Interactions set / remove + putComponent; Acro.dodge / rollFx / PDodge.rollAge count the
      style effects); the fresh xp.properties block; the 10 Server Setup rows right after acro.dodgeTapMs
  PD  perfect dodge: PDodge.read defaults (100 ms, 1000000 / min), Ranch.read (1000000 / min); flashText (<= 48) + flash through a
      feed:fn:push stand-in (args, TRUE / FALSE / none / throws); bytecode: PDodgeSys passes "any attacker" (true), PCounterSys has no
      return between the Perfect Parries check and setAmount (stacks), perfect() sends chat only when flash() says no; Pd44Mig.plan on
      untouched / admin / missing / marked / CRLF / continued files + sameAfter (and a tampered control)
  0.4.43's phases on the 0.4.44 jar (SB / HP / EV + every inherited phase, START TWICE on a scratch COPY of the live data included) - the
      checks pinning 0.4.43's numbers / behaviour that 0.4.44 changes on purpose are expected (EXPECTED44 below, each with its reason).
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.4.44"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.43.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "roll01", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")   # read only
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))
EXPECT = {
    'Acro': ['~<clinit>', '+f FLIP_ROOT', '+f KEY_FAILED', '+f KEY_FOREIGN', '+f KEY_ROOT', '+f LUNGE_ROOT', '+f STYLE_FX', '+m bindPlan', '+m isStyleFx',
             '+m keyBind', '+m keyTick', '+m ours', '+m styleFor', '+m styleFx', '+m styleRoot', '+m wantRoot', '~m dodge', '~m rollFx',
             '~m state', '~m tap'],
    'AcroCfg': ['+f ROLL_KEY', '+f STYLE', '+f STYLE_CLASSES', '+f STYLE_DEFS', '+m readStyles', '~<clinit>', '~m read'],
    'AcroSys': ['~m tick'],
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'PCounterSys': ['~m handle'],
    'PDodge': ['+m flash', '+m flashText', '~<clinit>', '~m perfect', '~m read', '~m rollAge', '~m text'],
    'PDodgeSys': ['~m handle'],
    'Ranch': ['~<clinit>', '~m read'],
    'SkillCfg': ['~m load'],
    'SkyySkillsPlugin': ['~m setup'],
}
ADDED = ["Pd44Mig"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_EQ0 = HK.Child.eq
T43 = tmod("test_skyyskills_0.4.43.py", "t0443")
HK.Child.eq = _EQ0


def _unsafe():
    from jpype import JClass
    U_ = JClass("sun.misc.Unsafe")
    uf = U_.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    return uf.get(None)


def _jf(c, name):
    while c is not None:
        try:
            f = c.getDeclaredField(name)
            f.setAccessible(True)
            return f
        except Exception:
            c = c.getSuperclass()
    raise KeyError(name)


def getany(o, name):
    return _jf(o.getClass(), name).get(o)


def setany(o, name, v):
    _jf(o.getClass(), name).set(o, v)


def _bridge():
    from jpype import JClass
    Sys = JClass("java.lang.System")
    br = Sys.getProperties().get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        Sys.getProperties().put("skyy.bridge", br)
    return br


def _fn(f):
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, o):
            return f(o)
    return Fn()


def _code(cls_name, meth, jar):
    """javassist instruction lines of one method of the jar (in the child JVM: javassist on the class path)"""
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    c = cp.get(cls_name)
    out = []
    for m in c.getDeclaredMethods():
        if str(m.getName()) != meth:
            continue
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        it = ca.iterator()
        while it.hasNext():
            pos = it.next()
            out.append(str(IP.instructionString(it, pos, mi.getConstPool())))
    return out


# ============================================================================================ DIR: the engine picks the dodge
D7 = 0.7071
DIRS = {"Forward": (0, -1), "ForwardLeft": (-D7, -D7), "ForwardRight": (D7, -D7), "Back": (0, 1), "BackLeft": (-D7, D7), "BackRight": (D7, D7),
        "Left": (-1, 0), "Right": (1, 0)}
FIELD = {"None": "failed", "Forward": "forward", "Back": "back", "Left": "left", "Right": "right", "ForwardLeft": "forwardLeft",
         "ForwardRight": "forwardRight", "BackLeft": "backLeft", "BackRight": "backRight"}
ROLL_ID = {"Forward": "SkyySkills_Roll_Forward", "ForwardLeft": "SkyySkills_Roll_ForwardLeft", "ForwardRight": "SkyySkills_Roll_ForwardRight",
           "Back": "SkyySkills_Roll_Back", "BackLeft": "SkyySkills_Roll_BackLeft", "BackRight": "SkyySkills_Roll_BackRight", "Left": "Dodge_Left",
           "Right": "Dodge_Right"}
ROLL_ANIM = {"Forward": "Roll", "Back": "RollBackward", "Left": "RollLeft", "Right": "RollRight"}
LUNGE_ANIM = {"Forward": "DashForward", "Back": "DashBackward", "Left": "DashLeft", "Right": "DashRight"}
FLIP_ANIM = {"Back": "Backflip", "Left": "SideflipLeft", "Right": "SideflipRight"}


def group(k):
    return "Forward" if k.startswith("Forward") else ("Back" if k.startswith("Back") else k)


def want(style, md):
    """(body id, X, Y, Z, force, look effect, entity animation or None, item animation or None) for a MovementDirection name"""
    k = "Back" if md == "None" else md
    x, z = DIRS[k]
    g = group(k)
    if style == "roll":
        fx = {"Forward": "Dodge_Forward", "Back": "Dodge_Back", "Left": "Dodge_Left", "Right": "Dodge_Right"}[g]
        return ROLL_ID[k], x, 0, z, 13, fx, ROLL_ANIM[g], None
    if style == "lunge":
        return "SkyySkills_Lunge_" + k, x, 0, z, 10, "Dodge_Lunge_" + g, LUNGE_ANIM[g], None
    if g == "Forward":
        return "SkyySkills_Flip_" + k, x, 0.5, z, 13, "Dodge_Forward", "Roll", None
    return "SkyySkills_Flip_" + k, x, 0.5, z, 13, "Dodge_Flip", None, FLIP_ANIM[g]


def body_parts(jz, az, rid):
    """follow the names like the engine: body -> its Serial -> the steps; (cost, failed, safe, spend, looks, anims, push)"""
    jn = set(jz.namelist())

    def rd(name):
        p = "Server/Item/Interactions/Dodge/%s.json" % name
        if p in jn:
            return json.loads(jz.read(p).decode("utf-8"))
        return json.loads(az.read(p).decode("utf-8-sig"))
    b = rd(rid)
    if rid in ("Dodge_Left", "Dodge_Right"):            # vanilla's own bodies (inline steps)
        st = b["Next"]["Interactions"]
        return b["Costs"], b.get("Failed"), st[0]["EffectId"] == "Dodge_Invulnerability", st[3].get("RequiredGameMode") == "Adventure", [st[1]["EffectId"]], [], st[2]
    steps = rd(b["Next"])["Interactions"]
    looks, anims = [], []
    for nm in steps[1:-2]:
        o = rd(nm)
        if o["Type"] == "ApplyEffect":
            looks.append(o["EffectId"])
        else:
            anims.append(o)
    safe = rd(steps[0])["EffectId"] == "Dodge_Invulnerability"
    spend = rd(steps[-1]).get("RequiredGameMode") == "Adventure"
    return b["Costs"], b.get("Failed"), safe, spend, looks, anims, rd(steps[-2])


def run_dir(out, jar, scratch, _home):
    from jpype import JClass, JArray, JBoolean
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    U = _unsafe()
    alloc = lambda c: U.allocateInstance(c.class_)
    AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
    ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    MCI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.MovementConditionInteraction")
    SIM = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.SimpleInteraction")
    AFI = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.ApplyForceInteraction")
    ICL = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
    LBL = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.operation.Label")
    ICTX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    IENT = JClass("com.hypixel.hytale.server.core.entity.InteractionEntry")
    ICH = JClass("com.hypixel.hytale.server.core.entity.InteractionChain")
    ISD = JClass("com.hypixel.hytale.protocol.InteractionSyncData")
    MD = JClass("com.hypixel.hytale.protocol.MovementDirection")
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    CDH = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler")
    Paths, JStr, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")
    jz, az = zipfile.ZipFile(jar), zipfile.ZipFile(ASSETS)
    jn = set(jz.namelist())

    def jread(p):
        return json.loads(jz.read(p).decode("utf-8"))

    def dec(codec, obj, key):
        o = dict(obj)
        o.pop("Type", None)
        ei = AEI(Paths.get(os.path.join(scratch, key + ".json"), Arr.newInstance(JStr.class_, 0)), ADT(ICL.class_, key, None))
        r = codec.decodeJson(RJR.fromJsonString(json.dumps(o, indent=2)), ei)
        return r, [str(k) for k in ei.getUnknownKeys()]
    # the roots -> Main -> the MovementCondition
    picks = {}
    root = jread("Server/Item/RootInteractions/Dodge.json")
    K.eq(root, {"Interactions": ["Dodge"], "RequireNewClick": True, "Cooldown": {"Cooldown": 0}}, "DIR roll root Dodge = vanilla + Cooldown 0")
    main = jread("Server/Item/Interactions/Dodge.json")
    K.check(main["Type"] == "Condition" and main["Flying"] is False and main["Next"]["Type"] == "MovementCondition", "DIR roll: Dodge.json = Condition Flying false -> MovementCondition")
    picks["roll"] = main["Next"]
    for sty, rid in (("lunge", "SkyySkills_Dodge_Lunge"), ("flip", "SkyySkills_Dodge_Flip")):
        r = jread("Server/Item/RootInteractions/%s.json" % rid)
        cap = sty.capitalize()
        K.eq(r, {"Interactions": ["SkyySkills_Dodge_%s_Main" % cap], "RequireNewClick": True, "Cooldown": {"Cooldown": 0}}, "DIR %s root -> Main, Cooldown 0" % sty)
        m = jread("Server/Item/Interactions/Dodge/SkyySkills_Dodge_%s_Main.json" % cap)
        K.eq(m, {"Type": "Condition", "Flying": False, "Next": "SkyySkills_Dodge_%s_Pick" % cap}, "DIR %s Main = Condition Flying false -> the named Pick" % sty)
        picks[sty] = jread("Server/Item/Interactions/Dodge/SkyySkills_Dodge_%s_Pick.json" % cap)
    # the engine's own label table
    idx = {}
    for fname, field in (("FAILED", "failed"), ("FORWARD", "forward"), ("BACK", "back"), ("LEFT", "left"), ("RIGHT", "right"),
                         ("FORWARD_LEFT", "forwardLeft"), ("FORWARD_RIGHT", "forwardRight"), ("BACK_LEFT", "backLeft"), ("BACK_RIGHT", "backRight")):
        f = MCI.class_.getDeclaredField(fname + "_LABEL_INDEX")
        f.setAccessible(True)
        idx[int(f.getInt(None))] = field
    K.check(sorted(idx) == list(range(9)), "DIR the engine has 9 labels 0-8: %s" % idx)
    t0m = MCI.class_.getDeclaredMethod("tick0", JClass("java.lang.Boolean").TYPE, JClass("java.lang.Float").TYPE, IT.class_, ICTX.class_, CDH.class_)
    t0m.setAccessible(True)
    labels = JArray(LBL)(9)
    for i in range(9):
        lb = alloc(LBL)
        setany(lb, "index", JClass("java.lang.Integer").valueOf(1000 + i))
        labels[i] = lb
    pj = json.loads(az.read("Server/Models/Human/Player.json").decode("utf-8-sig"))
    sets = pj.get("AnimationSets") or {}
    sb = json.loads(az.read("Server/Item/Animations/Shortbow.json").decode("utf-8-sig")).get("Animations") or {}
    for sty in ("roll", "lunge", "flip"):
        mci, unk = dec(MCI.CODEC, picks[sty], "Pick_" + sty)
        K.check(mci is not None and not unk, "DIR %s: the engine's MovementCondition codec decodes it, no unknown key %s" % (sty, unk))
        fields = dict((k, None if getany(mci, k) is None else str(getany(mci, k))) for k in FIELD.values())
        seen = {}
        for md in MD.values():
            ctx, ent, ch = alloc(ICTX), alloc(IENT), alloc(ICH)
            setany(ent, "useSimulationState", JBoolean(False))
            setany(ent, "serverState", ISD())
            cs = ISD()
            setany(cs, "movementDirection", md)
            setany(ent, "clientState", cs)
            setany(ctx, "entry", ent)
            setany(ctx, "chain", ch)
            setany(ctx, "labels", labels)
            t0m.invoke(mci, JArray(JClass("java.lang.Object"))([JClass("java.lang.Boolean").valueOf(True), JClass("java.lang.Float").valueOf(0.0), IT.Dodge, ctx, None]))
            li = int(getany(ch, "operationCounter")) - 1000
            name = str(md)
            branch = idx.get(li)
            rid = fields.get(branch) if branch else None
            seen[name] = rid
            if name not in FIELD:
                K.check(False, "DIR an unknown MovementDirection %s" % name)
                continue
            wid, wx, wy, wz, wf, wfx, wan, wia = want(sty, name)
            K.check(branch == FIELD[name] and rid == wid and str(getany(ent, "serverState").state) == "Finished",
                    "DIR %-5s %-12s -> label %d = %s -> %s (want %s)" % (sty, name, li, branch, rid, wid))
            if rid is None or ("Server/Item/Interactions/Dodge/%s.json" % rid not in jn and rid not in ("Dodge_Left", "Dodge_Right")):
                K.check(False, "DIR %s %s: body %s missing" % (sty, name, rid))
                continue
            cost, failed, safe, spend, looks, anims, push = body_parts(jz, az, rid)
            d = push["Direction"]
            ok_push = abs(float(d["X"]) - wx) < 1e-3 and abs(float(d.get("Y", 0)) - wy) < 1e-3 and abs(float(d["Z"]) - wz) < 1e-3 and push["Force"] == wf
            fxa = None
            if looks:
                fxj = json.loads(jz.read("Server/Entity/Effects/Movement/%s.json" % looks[0]).decode("utf-8"))
                fxa = (fxj.get("ApplicationEffects") or {}).get("EntityAnimationId")
            ia = anims[0]["Effects"]["ItemAnimationId"] if anims else None
            K.check(cost == {"Stamina": 2} and failed == "Stamina_Bar_Flash" and safe and spend and ok_push and looks == [wfx] and fxa == wan and ia == wia,
                    "DIR %-5s %-12s: Stamina 2, i-frames, Adventure spend, push %s force %s, look %s = %s, item anim %s (want %.3f/%.1f/%.3f f%d, %s, %s, %s)"
                    % (sty, name, d, push["Force"], looks, fxa, ia, wx, wy, wz, wf, wfx, wan, wia))
            if wan:
                K.check(bool((sets.get(wan) or {}).get("Animations")), "DIR %s: %s is a vanilla Player.json animation set" % (sty, wan))
            if anims:
                a0 = anims[0]
                K.check(a0["Effects"].get("ItemPlayerAnimationsId") == "Shortbow" and isinstance(sb.get(ia), dict), "DIR flip: %s is a vanilla Shortbow animation" % ia)
                # ItemPlayerAnimationsId is an asset reference: the codec hands it to the ItemPlayerAnimations store's validator (none in a
                # bare JVM) - reaching that validator proves the key is the engine's; the rest decodes with no unknown key
                why = ""
                try:
                    dec(SIM.CODEC, a0, "Anim_" + name)
                except Exception as e_:
                    t_ = e_
                    while t_ is not None:
                        why += " | " + str(t_)
                        t_ = t_.getCause() if hasattr(t_, "getCause") else None
                K.check("Effects.ItemPlayerAnimationsId" in why and "AssetStore.validate" in why,
                        "DIR flip: ItemPlayerAnimationsId reaches the engine's asset-reference validator (a real Effects field)")
                a1 = {"Type": "Simple", "Effects": {"ItemAnimationId": a0["Effects"]["ItemAnimationId"]}}
                so, sunk = dec(SIM.CODEC, a1, "Anim1_" + name)
                K.check(so is not None and not sunk and str(getany(getany(so, "effects"), "itemAnimationId")) == ia,
                        "DIR flip: ItemAnimationId %s decodes as an engine Simple interaction's effect, no unknown key %s" % (ia, sunk))
        K.check(sorted(seen) == sorted(FIELD), "DIR %s: every MovementDirection (None + 8) executed" % sty)
        K.check(seen.get("None") == seen.get("Back") == want(sty, "Back")[0], "DIR %s: S + sprint and no key both dodge BACK (%s)" % (sty, seen.get("Back")))
    # one flip push through the engine's ApplyForce codec (the Y hop is a real field)
    fp = jread("Server/Item/Interactions/Dodge/SkyySkills_Flip_Back_Push.json")
    ao, aunk = dec(AFI.CODEC, fp, "FlipPush")
    K.check(ao is not None and not aunk, "DIR the flip push decodes as an engine ApplyForce, no unknown key %s" % aunk)
    fx = jread("Server/Entity/Effects/Movement/Dodge_Flip.json")
    K.eq(fx, {"Duration": 0.25, "OverlapBehavior": "Extend"}, "DIR Dodge_Flip = a 0.25 s marker (the roll effects' duration, no animation)")
    new_files = sorted(n for n in jn if ("SkyySkills_Lunge" in n or "SkyySkills_Flip" in n or "SkyySkills_Dodge_" in n or "Dodge_Lunge" in n or n.endswith("/Dodge_Flip.json")))
    K.eq(len(new_files), 67, "DIR the jar ships the 67 style files (60 interactions, 2 roots, 5 effects)")
    K.save()


# ============================================================================================ KEY: the dodge-input slot + styles
def _fakes(out_dir):
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    st_ = cp.makeClass("skyytest44.KStore")
    st_.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    st_.addField(CtField.make("public com.hypixel.hytale.component.Component its;", st_))
    st_.addField(CtField.make("public com.hypixel.hytale.component.ComponentType itsType;", st_))
    st_.addField(CtField.make("public int gets;", st_))
    st_.addField(CtField.make("public boolean boom;", st_))
    st_.addConstructor(CtNewConstructor.make("public KStore() { super(null, 0, null, null); }", st_))
    st_.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  this.gets = this.gets + 1;
  if (this.boom) throw new java.lang.IllegalStateException("boom");
  if (t == this.itsType) return this.its;
  return null;
}""", st_))
    st_.writeFile(out_dir)
    cb_ = cp.makeClass("skyytest44.KCB")
    cb_.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    cb_.addField(CtField.make("public int puts;", cb_))
    cb_.addField(CtField.make("public com.hypixel.hytale.component.Component put;", cb_))
    cb_.addField(CtField.make("public com.hypixel.hytale.component.ComponentType putType;", cb_))
    cb_.addConstructor(CtNewConstructor.make("public KCB() { super(null); }", cb_))
    cb_.addMethod(CtNewMethod.make("""public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  this.puts = this.puts + 1;
  this.put = c;
  this.putType = t;
}""", cb_))
    cb_.writeFile(out_dir)


def run_key(out, jar, scratch, _home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    fake = os.path.join(scratch, "keyfake")
    os.makedirs(fake, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, fake, jar], verify=True)
    _fakes(fake)
    U = _unsafe()
    A, AC, Cfg = JClass(PKG + "Acro"), JClass(PKG + "AcroCfg"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    ITS = JClass("com.hypixel.hytale.server.core.modules.interaction.Interactions")
    IMM = JClass("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    Props, UUID = JClass("java.util.Properties"), JClass("java.util.UUID")
    KStore, KCB = JClass("skyytest44.KStore"), JClass("skyytest44.KCB")
    R, L, F = "Dodge", "SkyySkills_Dodge_Lunge", "SkyySkills_Dodge_Flip"
    K.check(str(A.KEY_ROOT) == R and str(A.LUNGE_ROOT) == L and str(A.FLIP_ROOT) == F, "KEY the three roots")
    # ---------------------------------------------------------------- bindPlan (pure)
    for cur, w, exp, what in ((None, R, 1, "empty slot -> put the style root in"), (R, R, 0, "already right"), (R, L, 1, "our roll -> the lunge (class change)"),
                              (F, R, 1, "our flip -> the roll"), ("PerfectDodge", R, 3, "another mod's root -> left alone"), (None, None, 0, "empty, not wanted"),
                              (R, None, 2, "not wanted -> our roll out"), (L, None, 2, "not wanted -> our lunge out"), ("PerfectDodge", None, 0, "not wanted, another root kept"),
                              ("dodge", R, 3, "case matters (an id is exact)")):
        K.eq(int(A.bindPlan(cur, w)), exp, "KEY bindPlan(%r, %r): %s" % (cur, w, what))
    # ---------------------------------------------------------------- styles
    AC.read(Props())
    K.eq([str(x) for x in AC.STYLE_CLASSES], ["none", "archer", "warrior", "assassin", "monk", "mage", "berserker", "priest", "spellblade"], "STY the classes")
    K.eq([str(x) for x in AC.STYLE], ["roll", "roll", "lunge", "flip", "flip", "roll", "lunge", "flip", "lunge"], "STY defaults (heavy lunge, most roll, light flip)")
    for c, w in (("Warrior", L), ("Berserker", L), ("Spellblade", L), ("Archer", R), ("Mage", R), ("Assassin", F), ("Monk", F), ("Priest", F),
                 (None, R), ("Shaman", R), ("  priest ", F)):
        K.eq(str(A.styleRoot(A.styleFor(c))), w, "STY class %r -> %s" % (c, w))
    p = Props()
    p.setProperty("acro.dodgeStyle.warrior", "Flip")
    p.setProperty("acro.dodgeStyle.none", "lunge")
    p.setProperty("acro.dodgeStyle.mage", "cartwheel")
    AC.read(p)
    K.check(str(A.styleFor("Warrior")) == "flip" and str(A.styleFor(None)) == "lunge" and str(A.styleFor("Mage")) == "roll", "STY custom values read (any case); a bad value = the default")
    AC.read(Props())
    # ---------------------------------------------------------------- the real Interactions component + a real InteractionModule
    mod = U.allocateInstance(IMM.class_)
    ct = U.allocateInstance(CT.class_)
    f = IMM.class_.getDeclaredField("interactionsComponentType")
    f.setAccessible(True)
    f.set(mod, ct)
    fi = IMM.class_.getDeclaredField("instance")
    fi.setAccessible(True)
    fi.set(None, mod)
    K.check(ITS.getComponentType() == ct, "KEY Interactions.getComponentType() answers (a real InteractionModule)")

    def fresh(comp):
        st, cb = U.allocateInstance(KStore.class_), U.allocateInstance(KCB.class_)   # the engine constructors are package-private
        st.itsType = ct
        st.its = comp
        return st, cb
    st, cb = fresh(None)
    r = int(A.keyBind(st, cb, None, L))
    K.check(r == 1 and int(cb.puts) == 1 and cb.putType == ct and str(cb.put.getInteractionId(IT.Dodge)) == L and cb.put.getInteractions().size() == 1,
            "KEY no Interactions component -> a new one put with only Dodge = the lunge root")
    c = ITS()
    c.consumeNetworkOutdated()
    st, cb = fresh(c)
    r = int(A.keyBind(st, cb, None, R))
    K.check(r == 1 and int(cb.puts) == 0 and str(c.getInteractionId(IT.Dodge)) == R and bool(c.consumeNetworkOutdated()), "KEY an empty component -> set in place, network update raised")
    r = int(A.keyBind(st, cb, None, R))
    K.check(r == 0 and not bool(c.consumeNetworkOutdated()), "KEY already right -> nothing (no network update)")
    c.setInteractionId(IT.Use, "SomeUse")
    r = int(A.keyBind(st, cb, None, F))
    K.check(r == 1 and str(c.getInteractionId(IT.Dodge)) == F and str(c.getInteractionId(IT.Use)) == "SomeUse", "KEY our roll -> the flip (class change), Use untouched")
    c2 = ITS()
    c2.setInteractionId(IT.Dodge, "PerfectDodge")
    st2, cb2 = fresh(c2)
    A.KEY_FOREIGN = False
    r = int(A.keyBind(st2, cb2, None, R))
    K.check(r == 3 and str(c2.getInteractionId(IT.Dodge)) == "PerfectDodge" and bool(A.KEY_FOREIGN), "KEY another mod's dodge root -> left alone, WARN once")
    r = int(A.keyBind(st, cb, None, None))
    K.check(r == 2 and c.getInteractionId(IT.Dodge) is None and str(c.getInteractionId(IT.Use)) == "SomeUse", "KEY off -> our root taken out (Use kept)")
    r = int(A.keyBind(st2, cb2, None, None))
    K.check(r == 0 and str(c2.getInteractionId(IT.Dodge)) == "PerfectDodge", "KEY off -> another mod's root kept")
    st3, cb3 = fresh(None)
    K.check(int(A.keyBind(st3, cb3, None, None)) == 0 and int(cb3.puts) == 0, "KEY off + no component -> nothing created")
    stb, cbb = fresh(None)
    stb.boom = True
    A.KEY_FAILED = False
    K.check(int(A.keyBind(stb, cbb, None, R)) == 9 and bool(A.KEY_FAILED), "KEY a throwing store -> 9 + one WARN (never throws)")
    # ---------------------------------------------------------------- keyTick: once a second, the class's style
    br = _bridge()
    u = UUID.fromString("00000000-0000-4000-8000-0000000044aa")
    s = A.state(u)
    K.check(len(s) == 308, "KEY the Acro state has 308 slots (304 / 305 = the slot check)")
    c = ITS()
    st, cb = fresh(c)
    AC.TAP_ON, AC.ROLL_KEY = True, True
    br.put("class:" + str(u), "Warrior")
    t0 = 1_800_000_000_000
    A.keyTick(s, st, cb, None, u, JLong(t0))
    K.check(str(c.getInteractionId(IT.Dodge)) == L and float(s[305]) == 1.0 and float(s[304]) == float(t0), "KEY keyTick: a Warrior gets the lunge")
    g0 = int(st.gets)
    br.put("class:" + str(u), "Priest")
    A.keyTick(s, st, cb, None, u, JLong(t0 + 999))
    K.check(int(st.gets) == g0 and str(c.getInteractionId(IT.Dodge)) == L, "KEY keyTick: nothing again within 1 s")
    A.keyTick(s, st, cb, None, u, JLong(t0 + 1000))
    K.check(str(c.getInteractionId(IT.Dodge)) == F, "KEY keyTick: class switch to Priest -> the flip after 1 s")
    br.remove("class:" + str(u))
    A.keyTick(s, st, cb, None, u, JLong(t0 + 2000))
    K.check(str(c.getInteractionId(IT.Dodge)) == R, "KEY keyTick: no class -> the roll")
    AC.ROLL_KEY = False
    A.keyTick(s, st, cb, None, u, JLong(t0 + 3000))
    K.check(c.getInteractionId(IT.Dodge) is None and float(s[305]) == 2.0, "KEY keyTick: acro.rollKey off -> the slot taken out")
    AC.ROLL_KEY, AC.TAP_ON = True, False
    c.setInteractionId(IT.Dodge, R)
    A.keyTick(s, st, cb, None, u, JLong(t0 + 4000))
    K.check(c.getInteractionId(IT.Dodge) is None, "KEY keyTick: acro.dodgeTap off -> no sprint dodge at all (slot out)")
    AC.TAP_ON = True
    A.keyTick(s, st, cb, None, u, JLong(t0 + 5000))
    K.check(str(c.getInteractionId(IT.Dodge)) == R, "KEY keyTick: both on again -> slot back")
    K.save()


# ============================================================================================ TAP: the server press in both modes + wiring
def run_tap(out, jar, scratch, _home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    A, AC, Cfg = JClass(PKG + "Acro"), JClass(PKG + "AcroCfg"), JClass(PKG + "SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    MST, Props, UUID = JClass("com.hypixel.hytale.protocol.MovementStates"), JClass("java.util.Properties"), JClass("java.util.UUID")
    AC.read(Props())
    K.check(bool(AC.ROLL_KEY) and bool(AC.TAP_ON), "TAP CFG a file without acro.rollKey = key mode on (the default)")
    p = Props()
    p.setProperty("acro.rollKey", "false")
    AC.read(p)
    K.check(not bool(AC.ROLL_KEY) and bool(AC.TAP_ON), "TAP CFG acro.rollKey=false is read")
    AC.read(Props())

    def ms(sprint):
        m = MST()
        m.onGround, m.sprinting, m.running, m.horizontalIdle = True, sprint, not sprint, False
        return m

    def press(key_mode, uid):
        AC.ROLL_KEY = key_mode
        s = A.state(UUID.fromString(uid))
        t = 1_800_000_000_000
        r1 = bool(A.tap(s, ms(False), JLong(t), False, -1.0))
        r2 = bool(A.tap(s, ms(True), JLong(t + 33), False, 10.0))
        return r1, r2, float(s[296])
    r = press(True, "00000000-0000-4000-8000-0000000044b1")
    K.check(r == (False, False, 0.0), "TAP key mode: a sprint press starts NO server roll (the client's dodge input dodges): %s" % (r,))
    r = press(False, "00000000-0000-4000-8000-0000000044b2")
    K.check(r[0] is False and r[1] is True, "TAP acro.rollKey=false: the press rolls on that tick (0.4.43 exactly): %s" % (r,))
    AC.ROLL_KEY = True
    g = PW.calls(jar)
    has = lambda m, c: PKG + c in g.get(m, set())
    K.check(has("AcroSys.tick", "Acro.keyTick") and has("Acro.keyTick", "Acro.keyBind") and has("Acro.keyTick", "Acro.wantRoot")
            and has("Acro.wantRoot", "SkillClass.className") and has("Acro.keyBind", "Acro.bindPlan"), "WIRE AcroSys.tick -> keyTick -> wantRoot (class:<uuid>) + keyBind -> bindPlan")
    kb = g.get("Acro.keyBind", set())
    K.check("com.hypixel.hytale.server.core.modules.interaction.Interactions.setInteractionId" in kb
            and "com.hypixel.hytale.server.core.modules.interaction.Interactions.removeInteractionId" in kb
            and "com.hypixel.hytale.component.CommandBuffer.putComponent" in kb, "WIRE keyBind: Interactions set / remove + CommandBuffer.putComponent")
    K.check(has("Acro.dodge", "Acro.styleFx") and has("Acro.rollFx", "Acro.styleFx") and has("PDodge.rollAge", "Acro.isStyleFx"),
            "WIRE the lunge / flip effects count in Acro.dodge (XP + push), Acro.rollFx and PDodge.rollAge (perfect dodge)")
    K.eq([str(x) for x in A.STYLE_FX], ["Dodge_Lunge_Forward", "Dodge_Lunge_Back", "Dodge_Lunge_Left", "Dodge_Lunge_Right", "Dodge_Flip"], "WIRE the style effect ids")
    K.check(has("SkyySkillsPlugin.setup", "Pd44Mig.run") and has("SkyySkillsPlugin.setup", "RbCoinMig.run"), "WIRE setup -> RbCoinMig.run + Pd44Mig.run")
    z = zipfile.ZipFile(jar)
    K.check(b"ROLL_KEY" in z.read("com/skyy/skills/Acro.class"), "WIRE Acro.tap reads AcroCfg.ROLL_KEY")
    asy = z.read("com/skyy/skills/AcroSys.class")
    K.check(b"keyTick" in asy and b"startRoll" in asy, "WIRE AcroSys keeps the 0.4.43 press block (acro.rollKey=false) next to keyTick")
    cfgc = b"".join(z.read(n) for n in z.namelist() if n.startswith("com/skyy/skills/SkillCfg") and n.endswith(".class"))
    K.check(b"acro.rollKey=true" in cfgc and b"acro.dodgeStyle.warrior=lunge" in cfgc and b"acro.dodgeStyle.priest=flip" in cfgc
            and b"acro.perfectDodge.windowMs=100" in cfgc and b"ranching.maxXpPerMinute=1000000" in cfgc and b"SkyySkills 0.4.44 perfect dodge 100 ms" in cfgc,
            "WIRE the fresh xp.properties: acro.rollKey, the 9 styles, 100 ms, 1000000, the Pd44Mig marker")
    Rows = JClass(PKG + "CfgRows")
    keys = [str(x) for x in Rows.KEYS]
    i = keys.index("acro.dodgeTapMs") + 1
    want_k = ["acro.rollKey"] + ["acro.dodgeStyle." + c for c in ("none", "archer", "warrior", "assassin", "monk", "mage", "berserker", "priest", "spellblade")]
    K.eq(keys[i:i + 10], want_k, "WIRE the 10 Server Setup rows right after acro.dodgeTapMs")
    for k in want_k:
        j = keys.index(k)
        K.check(str(Rows.CATS[j]) == "acrobatics" and len(str(Rows.HELPS[j])) <= 100 and len(str(Rows.LABELS[j])) <= 40, "WIRE row %s: acrobatics, help / label length" % k)
    j = keys.index("acro.dodgeStyle.warrior")
    K.check(str(Rows.TYPES[j]) == "choice" and str(Rows.DEFS[j]) == "lunge" and str(Rows.OPTS[j]) == "roll|Roll,lunge|Lunge,flip|Flip", "WIRE a style row = choice roll / lunge / flip")
    K.notes.append("rows: %s" % [(str(Rows.LABELS[keys.index(k)]), str(Rows.DEFS[keys.index(k)])) for k in want_k])
    j = keys.index("acro.perfectDodge.windowMs")
    K.check(str(Rows.DEFS[j]) == "100" and str(Rows.DEFS[keys.index("acro.perfectDodge.maxXpPerMinute")]) == "1000000"
            and str(Rows.DEFS[keys.index("ranching.maxXpPerMinute")]) == "1000000", "WIRE row defaults 100 ms / 1000000 / 1000000")
    K.save()


# ============================================================================================ PD: perfect dodge tuning + Pd44Mig
def run_pd(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P, RC, Cfg, M = JClass(PKG + "PDodge"), JClass(PKG + "Ranch"), JClass(PKG + "SkillCfg"), JClass(PKG + "Pd44Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Props, UUID = JClass("java.util.Properties"), JClass("java.util.UUID")
    P.read(Props())
    K.check(int(P.WINDOW_MS) == 100 and int(P.MAX_PM) == 1000000 and int(P.XP) == 5 and int(P.COUNTER_MS) == 750 and abs(float(P.MULT) - 1.25) < 1e-9,
            "PD defaults: 100 ms, 1000000 XP / min, 5 XP, 750 ms, x1.25")
    p = Props()
    p.setProperty("acro.perfectDodge.windowMs", "50")
    P.read(p)
    K.check(int(P.WINDOW_MS) == 50, "PD an admin's 50 is read")
    P.read(Props())
    RC.read(Props())
    K.check(int(RC.PER_MIN) == 1000000, "PD Ranching cap default 1000000 / min")
    # the HUD flash
    for xp, w in ((5, "Perfect dodge! Next hit x1.25 +5 XP"), (0, "Perfect dodge! Next hit x1.25")):
        K.eq(str(P.flashText(xp)), w, "PD flashText(%d)" % xp)
    K.check(len(str(P.flashText(999999999))) <= 48, "PD flashText <= 48 (SkyyHud's feed limit)")
    br = _bridge()
    u = UUID.fromString("00000000-0000-4000-8000-0000000044c1")
    got = []
    br.put("feed:fn:push", _fn(lambda o: (got.append([str(x) if x is not None else None for x in o]), JClass("java.lang.Boolean").TRUE)[1]))
    K.check(bool(P.flash(u, 5)) and got and got[-1] == [str(u), "dodge", None, "Perfect dodge! Next hit x1.25 +5 XP"], "PD flash -> feed:fn:push {uuid, dodge, null, text} = TRUE: %s" % got)
    br.put("feed:fn:push", _fn(lambda o: JClass("java.lang.Boolean").FALSE))
    K.check(not bool(P.flash(u, 5)), "PD the HUD says no -> FALSE (the chat line goes out)")
    br.remove("feed:fn:push")
    K.check(not bool(P.flash(u, 5)), "PD no SkyyHud -> FALSE")

    def boom(o):
        raise RuntimeError("x")
    br.put("feed:fn:push", _fn(boom))
    K.check(not bool(P.flash(u, 5)), "PD a throwing feed -> FALSE (never throws)")
    br.remove("feed:fn:push")
    # bytecode: any attacker pays; the counter stacks; chat only when the flash says no
    hd = _code(PKG + "PDodgeSys", "handle", jar)
    k = [i for i, l in enumerate(hd) if "PDodge.perfect" in l]
    K.check(len(k) == 1 and hd[k[0] - 1].strip().startswith("iconst_1"), "PD PDodgeSys passes mob = true (any attacker pays the XP): %s" % (hd[k[0] - 1] if k else None))
    K.check(not any("isPlayer" in l for l in hd[k[0] - 3:k[0]]) if k else False, "PD the attacker kind no longer decides the XP")
    pc = _code(PKG + "PCounterSys", "handle", jar)
    hf = [i for i, l in enumerate(pc) if "PDodge.hasFx" in l]
    sa = [i for i, l in enumerate(pc) if "setAmount" in l]
    K.check(len(hf) == 1 and sa and sa[-1] > hf[0] and not any(l.strip() == "return" for l in pc[hf[0]:sa[-1]]),
            "PD PCounterSys: no return between the Perfect Parries check and setAmount (the two counters stack)")
    pf = _code(PKG + "PDodge", "perfect", jar)
    fl = [i for i, l in enumerate(pf) if "PDodge.flash" in l]
    sm = [i for i, l in enumerate(pf) if "sendMessage" in l]
    K.check(len(fl) == 1 and len(sm) == 1 and fl[0] < sm[0] and pf[fl[0] + 1].strip().startswith("ifne"), "PD perfect(): flash first, the chat line only when it says no")
    # Pd44Mig.plan
    S = lambda x: JString(x)
    t1 = "a=1\nacro.perfectDodge.windowMs=50\nacro.perfectDodge.maxXpPerMinute=50\nranching.maxXpPerMinute=200\n"
    r = M.plan(S(t1))
    body = str(r[0])
    K.check(r is not None and "acro.perfectDodge.windowMs=100\n" in body and "acro.perfectDodge.maxXpPerMinute=1000000\n" in body
            and "ranching.maxXpPerMinute=1000000\n" in body and body.endswith(str(M.MARK) + "\n") and body.startswith("a=1\n"),
            "MIG untouched defaults -> 100 / 1000000 / 1000000, marker at the end")
    K.eq([str(x) for x in r[1]], ["acro.perfectDodge.windowMs", "50", "100", "acro.perfectDodge.maxXpPerMinute", "50", "1000000", "ranching.maxXpPerMinute", "200", "1000000"], "MIG the change-log rows")
    K.check(bool(M.sameAfter(JString(t1).getBytes("ISO-8859-1"), JString(body).getBytes("ISO-8859-1"), r[2])), "MIG sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(JString(t1).getBytes("ISO-8859-1"), JString(body.replace("a=1", "a=2")).getBytes("ISO-8859-1"), r[2])), "MIG sameAfter refuses another changed key (control)")
    t2 = "acro.perfectDodge.windowMs=80\nranching.maxXpPerMinute=200\n"
    r = M.plan(S(t2))
    body = str(r[0])
    K.check("acro.perfectDodge.windowMs=80\n" in body and "ranching.maxXpPerMinute=1000000\n" in body and "windowMs=80 kept" in str(r[3]), "MIG an admin's 80 kept (INFO), the untouched 200 moved")
    r = M.plan(S("a=1\n"))
    K.check(str(r[0]) == "a=1\n" + str(M.MARK) + "\n" and len(r[1]) == 0, "MIG no lines (Skyy's live file) -> only the marker (the new code defaults apply)")
    K.check(M.plan(S("a=1\n" + str(M.MARK) + "\nacro.perfectDodge.windowMs=50\n")) is None, "MIG the marker -> nothing again (run once)")
    r = M.plan(S("x=1\r\nacro.perfectDodge.windowMs=50\r\n"))
    K.check(str(r[0]) == "x=1\r\nacro.perfectDodge.windowMs=100\r\n" + str(M.MARK) + "\r\n", "MIG CRLF file keeps CRLF")
    r = M.plan(S("acro.perfectDodge.windowMs=5\\\n0\n"))
    K.check(len(r[1]) == 0 and "acro.perfectDodge.windowMs=5\\\n0\n" in str(r[0]), "MIG a continued entry is never rewritten")
    r = M.plan(S("acro.perfectDodge.windowMs=50\nacro.perfectDodge.windowMs=70\n"))
    K.check(len(r[1]) == 0, "MIG the LAST entry decides (50 then 70 = the admin's 70)")
    K.save()


# ============================================================================================ LIVE44: start twice on a scratch COPY of the live data
def run_live44(out, jar, scratch, home):
    """every one-time update in setup() order + SkillCfg.load, twice, 0.4.43 vs 0.4.44, each on its own copy of the live folder"""
    import shutil
    from jpype import JClass
    T38 = T43.T42.T41.T38
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    migs = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig", "PerkMig", "PollMig", "RbCoinMig"]
    res = {}
    lc_root = os.path.dirname(home)

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)
    for tag, jr, mg in (("old", OLD_JAR, migs), ("new", jar, migs + ["Pd44Mig"])):
        lc = os.path.join(lc_root, "copy44-" + tag)
        shutil.copytree(home, lc)
        L = T38.loader_for(jr)
        J = lambda n: JClass(PKG + n, loader=L)
        Cfg, Sto, Hist, CLog, Rows = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")

        def start():
            Cfg.FILE = T38.path(os.path.join(lc, "xp.properties"))
            Sto.DATA.clear()
            Sto.DIRTY.clear()
            Sto.DIR = T38.path(os.path.join(lc, "players"))
            Hist.DIR = None
            Rows.HOME = None
            CLog.FILE = None
            CLog.Q.clear()
            r = {}
            for nm in mg:
                r[nm] = str(J(nm).run())
            r["load"] = str(Cfg.load())
            return r
        s0 = snap(lc)
        r1 = start()
        s1 = snap(lc)
        r2 = start()
        s2 = snap(lc)
        PD, RC, AC = J("PDodge"), J("Ranch"), J("AcroCfg")
        res[tag] = {"r1": r1, "r2": r2, "s0": s0, "s1": s1, "s2": s2, "win": int(PD.WINDOW_MS), "pm": int(PD.MAX_PM), "rpm": int(RC.PER_MIN),
                    "mark": str(J("Pd44Mig").MARK) if tag == "new" else None, "rk": bool(AC.ROLL_KEY) if tag == "new" else None}
    o, n = res["old"], res["new"]
    ch_o = sorted(k for k in set(o["s0"]) | set(o["s1"]) if o["s0"].get(k) != o["s1"].get(k))
    ch_n = sorted(k for k in set(n["s0"]) | set(n["s1"]) if n["s0"].get(k) != n["s1"].get(k))
    extra = sorted(set(ch_n) - set(ch_o))
    K.notes.append("LIVE44: 0.4.43 start 1 changed %s; 0.4.44 changed %s; Pd44Mig: %s" % (ch_o, ch_n, n["r1"].get("Pd44Mig", "")[:300]))
    K.check(set(extra) <= {"xp.properties", "config-changes.log"} | set(k for k in extra if k.startswith("config-history/")),
            "LIVE44: 0.4.44 start 1 changes what 0.4.43 changes + only xp.properties / its History copy / the change log: %s" % extra)
    xp0 = n["s0"].get("xp.properties", b"").decode("latin-1")
    xp1 = n["s1"].get("xp.properties", b"").decode("latin-1")
    nl = "\r\n" if "\r\n" in xp0 else "\n"
    keys = ("acro.perfectDodge.windowMs", "acro.perfectDodge.maxXpPerMinute", "ranching.maxXpPerMinute")
    if not any(("\n" + k) in ("\n" + xp0) for k in keys):
        pre = "" if xp0.endswith("\n") else nl
        K.check(xp1 == xp0 + pre + n["mark"] + nl, "LIVE44: the live xp.properties (none of the 3 keys): only the marker appended, every other byte kept")
        K.check(n["win"] == 100 and n["pm"] == 1000000 and n["rpm"] == 1000000, "LIVE44: the live copy reads the new code defaults 100 ms / 1000000 / 1000000 (0.4.43 read %d / %d / %d)" % (o["win"], o["pm"], o["rpm"]))
    else:
        K.notes.append("LIVE44: the live xp.properties has some of the 3 keys - plan() decides (checked in PD)")
    if xp0 != xp1:
        K.check(any(k.startswith("config-history/") and v == n["s0"]["xp.properties"] for k, v in n["s1"].items() if k not in n["s0"]),
                "LIVE44: the live xp.properties before the update is in config-history")
    K.check(all(n["s1"].get(k) == n["s2"].get(k) for k in set(n["s1"]) | set(n["s2"])) and n["r2"].get("Pd44Mig") == "", "LIVE44: 0.4.44 start 2 changes nothing")
    K.check(all(n["s0"].get(k) == n["s1"].get(k) for k in n["s0"] if k.startswith("players/")), "LIVE44: player files untouched")
    K.check(n["rk"] is True, "LIVE44: the live copy runs key mode (acro.rollKey default true)")
    K.save()


# 0.4.43's phases on this jar: the checks pinning the older numbers / behaviour - with why
EXPECTED44 = [
    ("G ROWS: the Sounds category, 249 rows (241 + 8)", "0.4.44: 271 rows (+ acro.rollKey + 9 acro.dodgeStyle.*)"),
    ("G5 defaults: on, 200 a minute", "0.4.44: the Ranching cap default is 1000000 (Skyy: caps absurdly high); PD checks Ranch.read"),
    ("G5 the minute cap 200:", "0.4.44: the same cap logic, default 1000000 (the 200 call pins the old default)"),
    ("G6 defaults on / 50 ms / 750 ms / x1.25 / 5 XP", "0.4.44: window 100 ms (Skyy); PD checks PDodge.read"),
    ("G6 67 ms = NOT perfect", "0.4.44: the window is 100 ms, so 67 ms IS perfect now"),
    ("FIX2 C4 REAL PCounterSys: a parry counterattack is not multiplied again", "0.4.44: Skyy 'Stack them' - the parry counter gets our x1.25 too (PD checks the bytecode)"),
    ("FIX A1 defaults: XP cap 50 a minute", "0.4.44: cap 1000000 and 'any attacker' in the text"),
    ("FIX A1/C3 a PLAYER's hit (PvP on): blocked + the counter-hit window, NO Acrobatics XP", "0.4.44: Skyy 'doesn't have to hit a mob' - a player's hit pays the XP too"),
    ("G7 the fresh default xp.properties carries the 0.4.37 block", "0.4.44: the block now holds 100 ms / 1000000 / 1000000 + the any-attacker comment (TAP checks the new lines)"),
    ("G7 /skills reload reads the edited lines", "0.4.44: the test replaces the OLD default text windowMs=50 (now 100) - nothing to replace"),
    ("G7 a file without the 0.4.37 keys = the code defaults", "0.4.44: the code default window is 100 ms (pinned 50)"),
]
for _e in EXPECTED44:
    if _e not in T43.EXPECTED43:
        T43.EXPECTED43.append(_e)


def wrap44(fn):
    def run(out, jar, scratch, home):
        tmp = out + ".i44.json"
        fn(tmp, jar, scratch, home)
        d = json.load(open(tmp))
        K = HK.Child(out)
        K.ok, K.notes = d["ok"], d["notes"]
        for f in d["fails"]:
            hit = [e for e in EXPECTED44 if f.startswith(e[0])]
            if hit:
                K.ok += 1
                K.notes.append("expected in 0.4.44 (%s): %s" % (hit[0][1], f[:160]))
            else:
                K.fails.append(f)
        K.save()
    return run


_CMP0 = HK.run_compare


def _compare44(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit's class compare; its 'non-class entries: only manifest.json' check is replaced by: manifest.json + exactly the 67 new
    dodge-style files (60 interactions, 2 roots, 5 effects), every other non-class entry byte-identical"""
    _CMP0(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    new = sorted(n for n in ed if n != "manifest.json")
    style = lambda n: (n.startswith("Server/Item/Interactions/Dodge/SkyySkills_") and ("_Lunge" in n or "_Flip" in n or "_Dodge_" in n)) \
        or n.startswith("Server/Item/RootInteractions/SkyySkills_Dodge_") or n.startswith("Server/Entity/Effects/Movement/Dodge_Lunge_") \
        or n == "Server/Entity/Effects/Movement/Dodge_Flip.json"
    fails = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    ok = "manifest.json" in ed and len(new) == 67 and all(style(n) and n not in ea for n in new)
    if ok:
        d["ok"] += 1
        d["notes"].append("C: non-class entries: manifest.json + the 67 new dodge-style files (nothing else changed)")
    else:
        fails.append("C: non-class entries beyond manifest.json + the 67 style files: %s" % [n for n in new if not style(n) or n in ea][:8])
    d["fails"] = fails
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = _compare44

if __name__ == "__main__":
    phases = [("dir", run_dir), ("key", run_key), ("tap", run_tap), ("pd", run_pd), ("live44", run_live44)]
    if "--no-old" not in sys.argv:
        phases += [("sb", wrap44(T43.run_sb)), ("hp", wrap44(T43.run_hp)), ("ev", wrap44(T43.run_ev)),
                   ("fort", wrap44(T43.wrap43(T43.T42.run_fort))), ("hub", wrap44(T43.wrap43(T43.T42.T41.run_hub)))]
        phases += [(k, wrap44(T43.wrap43(T43.T42.T41.wrap41(f)))) for k, f in T43.T42.T41.OLD_PHASES]
    try:
        HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
               phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
    finally:
        if "--phase" not in sys.argv and os.path.isdir(T43.T42.OLD_DIR):
            import shutil
            shutil.rmtree(T43.T42.OLD_DIR, ignore_errors=True)
