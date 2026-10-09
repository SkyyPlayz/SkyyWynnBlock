"""Derive SkyySacks/build_skyysacks_0.7.16.py from the SET pin 0.7.15 (edit THIS file, then regenerate: python tools/sacks_0_7_16_patch.py).
0.7.16 = THE BAG IS HELD HIGHER AND MORE IN FRONT (Skyy 2026-10-09: "i love the new bag! can we make the player hold it up a little
higher, more infront of him?").

Engine / asset facts (Assets.zip, read at build time):
 - an item JSON has NO held / first-person transform field (the 51 top-level keys of every vanilla item: only Scale, which scales the
   whole model). How high an item sits in the hand is decided only by the player animation set (PlayerAnimationsId).
 - every Magic Bag uses our set SkyySack = Parent Block (the vanilla two-hand "hold it in front" set) + SackLift. Block's first-person
   idle puts the R-Arm at (-41.8, -32.1, 61) - the bag hangs low at the bottom right of the screen.
 - vanilla items that sit higher / more central in first person do it with the R-Arm POSITION channel of their *_FPS animations:
   Rifle / Crossbow_Heavy (-28, -27, 46), Handgun (-33, -32, 54), Shield (L-Arm 40, -30, 52); x toward 0 = toward the screen centre
   (the Torch, held in the LEFT hand, uses +46), y less negative = higher.

1. OUR OWN HOLD POSES, generated at build time from the vanilla Block animations (vanilla-derived: never committed, never a vanilla path):
   for the 18 hold keys (Idle, Walk, WalkBackward, Run, RunBackward, Sprint, Crouch, CrouchWalk, CrouchWalkBackward, Jump, JumpWalk,
   JumpRun, Fall, FallFar, FluidIdle, FluidWalk, FluidWalkBackward, FluidRun) the SkyySack set now names its own files under
   Common/Characters/Animations/Items/SkyySacks/Hold/ (22 files: 9 first person, 13 third person; Jump_Far is shared by JumpWalk/JumpRun):
     FIRST PERSON: every R-Arm position key + HOLD_FPS_ARM_SHIFT = (+12 toward the screen centre, +10 up, 0 forward)
                   -> idle R-Arm (-41.8, -32.1, 61) -> (-29.8, -22.1, 61) (the vanilla Rifle sits at (-28, -27, 46)).
     THIRD PERSON: both upper arms (R-Arm, L-Arm) raised HOLD_3P_ARM_PITCH = 12 degrees on every orientation key (the same local-X
                   rotation the 0.7.14 lift uses for its 14 degree overshoot), so the two-hand hold sits at chest height, in front.
   Every other key (swim, climb, fly, build, swing, interact) still comes from Parent Block. Speed / Looping / BlendingDuration /
   KeepPreviousFirstPersonAnimation are Block's own values, copied per key.
2. THE LIFT ENDS ON THE NEW POSE. SackLift (SwapTo) is regenerated with tools/art/make_bags.py's own lift_anim + LIFT_PLAN_3P / _FPS, with
   the new hold idle as its end pose (its holdLastKeyframe = the set's Idle, so no jump when the idle takes over).
3. The open animation (SkyySacks_Bag_Open.blockyanim, the item-model swirl), models, textures, icons, sparkles: unchanged (byte-identical).
No Java change (every class is 0.7.15's or differs only in the version text); no saved data, command, system, event or setting.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.15.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.16.py")
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


assert 'VERSION = "0.7.15"' in s and "def bag_look(" in s and "HOLD_FPS_ARM_SHIFT" not in s, "the source must be the generated 0.7.15 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
GLB0 = s.count("registerGlobal(")
JAVA0 = s[:s.index("# ================= assets =================")]

# ================= docstring + version =================
rep('"""SkyySacks 0.7.15 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.15.py           -> SkyySacks/SkyySacks-0.7.15.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.15.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF,
    '"""SkyySacks 0.7.16 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.16.py           -> SkyySacks/SkyySacks-0.7.16.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.16.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF)
rep("current entity Ref (a page the client lost in a world move gets no update). Saved data unchanged." + LF + '"""' + LF,
    "current entity Ref (a page the client lost in a world move gets no update). Saved data unchanged." + LF
    + "0.7.16 (derived from 0.7.15 by tools/sacks_0_7_16_patch.py - edit the patch, not this file; Skyy 2026-10-09 \"can we make the player" + LF
    + "hold it up a little higher, more infront of him?\"): the SkyySack set gets its own hold poses for 18 keys (idle / walk / run / sprint /" + LF
    + "crouch / jump / fall / fluid), generated at build time from the vanilla Block animations: first person R-Arm + (12 toward the centre," + LF
    + "10 up, 0), third person both upper arms 12 degrees higher; SackLift ends on the new idle. Classes, ids, recipes, texts and saved data" + LF
    + "are 0.7.15's." + LF + '"""' + LF)
rep('VERSION = "0.7.15"', 'VERSION = "0.7.16"')

# ================= the hold poses (after the manifest is read, before BAG_FILES picks what ships) =================
rep('''BAG_SET_ID, BAG_LIFT_KEY = _A["player_set_id"], _A["lift_key"]
''', '''BAG_SET_ID, BAG_LIFT_KEY = _A["player_set_id"], _A["lift_key"]
# ================= 0.7.16 THE HOLD POSE (tools/sacks_0_7_16_patch.py docstring) =================
# Skyy 2026-10-09 "can we make the player hold it up a little higher, more infront of him?". An item JSON has no held transform, so the
# set does it: for HOLD_KEYS the SkyySack set names our own copies of the vanilla Block animations (read from Assets.zip at build time,
# written into BAG_GEN only - vanilla-derived, never committed) with these offsets. Ask for more / less here:
HOLD_FPS_ARM_SHIFT = (12.0, 10.0, 0.0)  # FIRST PERSON: added to every R-Arm position key (x: toward the screen centre, y: up, z: forward)
HOLD_3P_ARM_PITCH = -12.0               # THIRD PERSON: both upper arms rotated about their local X on every key (negative = up, the lift's sign)
HOLD_KEYS = ("Idle", "Walk", "WalkBackward", "Run", "RunBackward", "Sprint", "Crouch", "CrouchWalk", "CrouchWalkBackward",
             "Jump", "JumpWalk", "JumpRun", "Fall", "FallFar", "FluidIdle", "FluidWalk", "FluidWalkBackward", "FluidRun")
HOLD_DIR = "Characters/Animations/Items/SkyySacks/Hold"
HOLD_3P_NODES = ("R-Arm", "L-Arm")
def _hold_fps(a, src):
    """first person: every R-Arm position key + HOLD_FPS_ARM_SHIFT (the vanilla Rifle / Handgun approach)"""
    ch = a["nodeAnimations"].get("R-Arm") or {}
    keys = ch.get("position") or []
    if not keys:
        raise SystemExit("0.7.16 hold: %s has no R-Arm position key - cannot move the first-person hold" % src)
    for k in keys:
        d = k["delta"]
        for i, c in enumerate("xyz"):
            d[c] = BAG_MB.r6(d[c] + HOLD_FPS_ARM_SHIFT[i])
    return a
def _hold_3p(a, src):
    """third person: both upper arms HOLD_3P_ARM_PITCH degrees about their local X on every orientation key (q * rotX)"""
    rx = BAG_MB.axis_quat((1, 0, 0), HOLD_3P_ARM_PITCH)
    for node in HOLD_3P_NODES:
        keys = (a["nodeAnimations"].get(node) or {}).get("orientation") or []
        if not keys:
            raise SystemExit("0.7.16 hold: %s has no %s orientation key - cannot raise the third-person hold" % (src, node))
        for k in keys:
            k["delta"] = BAG_MB.qd(BAG_MB.qmul(BAG_MB._qn(k["delta"]), rx))
    return a
def _bag_hold():
    import types
    z = BAG_MB.SA.assets()
    try:
        blk = json.loads(z.read("Server/Item/Animations/Block.json").decode("utf-8-sig"))["Animations"]
        made, entries = {}, {}
        for hk in HOLD_KEYS:
            if hk not in blk:
                raise SystemExit("0.7.16 hold: the vanilla Block set has no %s key" % hk)
            e = json.loads(json.dumps(blk[hk]))
            for side in ("FirstPerson", "ThirdPerson"):
                sp = e.get(side)
                if not sp:
                    continue
                if sp not in made:
                    a = json.loads(z.read("Common/" + sp).decode("utf-8-sig"))
                    a = _hold_fps(a, sp) if side == "FirstPerson" else _hold_3p(a, sp)
                    out = HOLD_DIR + "/SkyySack_Hold_" + sp.split("/")[-1]
                    if out in made.values() or ("Common/" + out) in BAG_GEN:
                        raise SystemExit("0.7.16 hold: two hold files would share " + out)
                    BAG_GEN["Common/" + out] = BAG_MB.jbytes(a)
                    made[sp] = out
                e[side] = made[sp]
            entries[hk] = e
        # SackLift: make_bags' own lift_anim + plans, reading the NEW idle as its end pose (holdLastKeyframe = the set's Idle, no jump)
        idle3, idlef = "Common/" + blk["Idle"]["ThirdPerson"], "Common/" + blk["Idle"]["FirstPerson"]
        swap = {idle3: BAG_GEN["Common/" + made[blk["Idle"]["ThirdPerson"]]], idlef: BAG_GEN["Common/" + made[blk["Idle"]["FirstPerson"]]]}
        zw = types.SimpleNamespace(read=lambda n: swap[n] if n in swap else z.read(n))
        cur = types.SimpleNamespace(read=z.read)
        dur = _A["durations"]
        lifts = ((_A["player_lift_3p"], "Main_Handed/Item/Idle.blockyanim", idle3, dur["player_lift_3p"], BAG_MB.LIFT_PLAN_3P),
                 (_A["player_lift_fps"], "Main_Handed/Item/Idle_FPS.blockyanim", idlef, dur["player_lift_fps"], BAG_MB.LIFT_PLAN_FPS))
        for (lp, sa, sb, du, plan) in lifts:
            sbr = sb[len("Common/Characters/Animations/Items/"):]
            if BAG_MB.jbytes(BAG_MB.lift_anim(cur, sa, sbr, du, plan)) != BAG_GEN[lp]:
                raise SystemExit("0.7.16 hold: re-running make_bags.lift_anim does not give make_bags' own %s - the lift call changed" % lp)
            BAG_GEN[lp] = BAG_MB.jbytes(BAG_MB.lift_anim(zw, sa, sbr, du, plan))
    finally:
        z.close()
    st = json.loads(BAG_GEN[_A["player_set_draft"]].decode("utf-8"))
    if st.get("Parent") != "Block" or BAG_LIFT_KEY not in st["Animations"] or any(k in st["Animations"] for k in HOLD_KEYS):
        raise SystemExit("0.7.16 hold: the generated SkyySack set is not Parent Block + %s only" % BAG_LIFT_KEY)
    for hk in HOLD_KEYS:
        st["Animations"][hk] = entries[hk]
    st["$Comment"] = ("SkyWynn SkyySacks: the Magic Bag player animation set. Parent Block = the vanilla two-hand hold for every key not "
                      "listed; the hold keys (idle / walk / run / sprint / crouch / jump / fall / fluid) are SkyySacks/Hold copies of "
                      "Block's, held higher and more in front (0.7.16); SackLift = the one-shot lift played by the item's SwapTo.")
    BAG_GEN[_A["player_set_draft"]] = BAG_MB.jbytes(st)
    return made
BAG_HOLD = _bag_hold()   # vanilla path -> our hold file path (22 files)
''')
rep('''print("bag art: %d generated files in memory (tools/art/make_bags.py), %d ship in the jar; parts %s" % (
    len(BAG_GEN), len(BAG_FILES), ", ".join(k for k in ("anim", "set", "sparkle", "lift") if BAG_PARTS[k]) or "none"))''',
    '''print("bag art: %d generated files in memory (tools/art/make_bags.py), %d ship in the jar; parts %s" % (
    len(BAG_GEN), len(BAG_FILES), ", ".join(k for k in ("anim", "set", "sparkle", "lift") if BAG_PARTS[k]) or "none"))
if BAG_PARTS["set"] and not all(("Common/" + p) in BAG_FILES for p in BAG_HOLD.values()):
    raise SystemExit("0.7.16 hold: every hold file must ship with the set")
print("hold pose (0.7.16): %d keys -> %d SkyySacks/Hold files; first person R-Arm %+g / %+g / %+g (centre / up / forward), third person "
      "arms %g deg higher; SackLift ends on the new idle" % (len(HOLD_KEYS), len(BAG_HOLD), HOLD_FPS_ARM_SHIFT[0], HOLD_FPS_ARM_SHIFT[1],
                                                          HOLD_FPS_ARM_SHIFT[2], -HOLD_3P_ARM_PITCH))''')

# ================= self-checks =================
assert 'VERSION = "0.7.16"' in s and s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0 and s.count("registerGlobal(") == GLB0, \
    "no new command, ECS system or event"
_j1 = s[:s.index("# ================= assets =================")]
# the Java part may differ from 0.7.15 only in the docstring + VERSION
_body0 = JAVA0[JAVA0.index('VERSION = "0.7.15"'):].replace('VERSION = "0.7.15"', "")
_body1 = _j1[_j1.index('VERSION = "0.7.16"'):].replace('VERSION = "0.7.16"', "")
assert _body0 == _body1, "0.7.16 changes no Java / build code before the assets section"
assert s.index("BAG_HOLD = _bag_hold()") < s.index("BAG_FILES = {}"), "the hold files must exist before BAG_FILES picks what ships"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
